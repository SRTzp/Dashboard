#!/usr/bin/env python3
"""RS2a · ranked RS list of liquid US stocks → Firestore users/{uid}/rs2/latest (+ latest_0..k) and rs2/_meta, rs2/_sectors

Universe: NYSE + Nasdaq + NYSE American common stocks (Nasdaq Trader symbol files) · liquid = last close ≥ $10 and
50-day average dollar volume ≥ $10M. The RS1 formula is reused unchanged (build_prices.rs_for / rs_table) so a stock has the
same rating on Watch and in this list. Display + ranking only — never a gate.
Pure functions (no network, no pandas) are unit-tested by tests/rs2_selftest.py.
"""
import datetime as dt
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_prices as bp   # noqa: E402

NASDAQ_URL = 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt'
OTHER_URL = 'https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt'
MIN_CLOSE = 10.0
MIN_ADV = 10_000_000.0
ADV_WIN = 50
HISTORY_DAYS = 410            # calendar days ≈ 13.5 months ≈ 280 sessions (RS needs 253 + 20 for rating4wAgo)
CHUNK = 200
DOC_LIMIT = 900 * 1024        # bytes per Firestore doc (hard limit 1 MiB)
PART_ROWS = 500
UNIVERSE_REFRESH_DAYS = 6     # full symbol scan weekly; other days re-use the stored liquid list
SECTOR_BUDGET_S = 300         # yfinance .info lookups per run (cached in rs2/_sectors; converges over a few runs)
EXCH = {'Q': 'NASDAQ', 'G': 'NASDAQ', 'S': 'NASDAQ', 'N': 'NYSE', 'A': 'AMEX'}   # nasdaqlisted market category / otherlisted exchange

_BAD_NAME = re.compile(
    r'\bwarrants?\b|\brights?\b|\bunits?\b|\bpreferred\b|\bpref\b|\bnotes?\b|\bdebentures?\b|\bsubordinated\b|\bdepositary shares?\b.*\bpreferred|'
    r'\bfund\b|\betf\b|\betn\b|\bpartnership units?\b|\bcontingent\b|\bacquisition corp|\bblank check|\bwhen issued\b|\bdue \d{4}|\d+(\.\d+)?%|'
    r'\bcertificates?\b|\bbeneficial interest\b.*\btrust\b.*\bunits?\b|\bcapital securities\b|\btrust preferred\b|\bliquidating\b', re.I)


def _lines(txt):
    ls = [l.rstrip('\r') for l in str(txt or '').split('\n') if l.strip()]
    return ls


def clean_name(n):
    """'Agilent Technologies, Inc. Common Stock' → 'Agilent Technologies, Inc.' (≤ 28 chars)"""
    n = str(n or '').strip()
    n = re.sub(r'\s*-\s*(Class [A-Z]\s+)?(Common Stock|Ordinary Shares?|Common Shares?|American Depositary Shares?|Class [A-Z].*)$', '', n, flags=re.I)
    n = re.sub(r'\s+(Common Stock|Ordinary Shares?|Common Shares?|Class [A-Z] Common Stock|Class [A-Z] Ordinary Shares?|American Depositary Shares?).*$', '', n, flags=re.I)
    n = re.sub(r',?\s*(Inc|Corp|Corporation|Ltd|Limited|Co|Company|PLC|N\.V|S\.A|Holdings?|Group)\.?$', '', n, flags=re.I).strip(' ,.')
    return (n[:27] + '…') if len(n) > 28 else n


def ysym_of(t):
    """symbol-file ticker → Yahoo symbol (BRK.B → BRK-B)"""
    return str(t or '').strip().upper().replace('.', '-')


def _common(name, sym):
    if not name or _BAD_NAME.search(name):
        return False
    if re.search(r'[$^]|\.(WS|U|RT|W)\b|[-.]W[SA]?$|\.PR', sym):
        return False
    return True


def parse_symbol_files(nasdaq_txt, other_txt):
    """→ [{'t':ySym,'n':name,'e':exchange}] common stocks only · drops ETFs, test issues, non-normal status, warrants, units,
    preferreds, rights, notes, funds · otherlisted: only NYSE (N) + NYSE American (A) · deduped, sorted"""
    out, seen = [], set()

    def add(sym, name, exch):
        y = ysym_of(sym)
        if not y or y in seen or not _common(name, sym):
            return
        seen.add(y)
        out.append({'t': y, 'n': clean_name(name), 'e': exch})
    for ln in _lines(nasdaq_txt)[1:]:
        f = ln.split('|')
        if len(f) < 8 or f[0].startswith('File Creation'):
            continue
        sym, name, mcat, test, status, etf = f[0], f[1], f[2], f[3], f[4], f[6]
        if test.strip() == 'Y' or etf.strip() == 'Y' or status.strip() not in ('N', ''):
            continue
        add(sym, name, 'NASDAQ')
    for ln in _lines(other_txt)[1:]:
        f = ln.split('|')
        if len(f) < 8 or f[0].startswith('File Creation'):
            continue
        sym, name, ex, etf, test = f[0], f[1], f[2], f[4], f[6]
        if test.strip() == 'Y' or etf.strip() == 'Y' or ex.strip() not in ('N', 'A'):
            continue
        add(sym, name, EXCH[ex.strip()])
    out.sort(key=lambda x: x['t'])
    return out


def adv50(closes, vols):
    """mean(close × volume) over the last 50 sessions · needs ≥ 50 pairs else None"""
    n = min(len(closes), len(vols))
    if n < ADV_WIN:
        return None
    s = 0.0
    for c, v in zip(closes[-ADV_WIN:], vols[-ADV_WIN:]):
        s += float(c) * float(v)
    return s / ADV_WIN


def is_liquid(close, adv):
    return close is not None and adv is not None and close >= MIN_CLOSE and adv >= MIN_ADV


def chunks(seq, n=CHUNK):
    seq = list(seq)
    return [seq[i:i + n] for i in range(0, len(seq), n)]


def fetch_chunked(syms, fetch_chunk, chunk=CHUNK, sleep=0.5, retries=1, sleeper=time.sleep):
    """fetch_chunk(list)->{sym: {'close':[(date,c)], 'vol':[v]}} · retry a failed chunk once · a chunk that fails twice is skipped
    → ({sym: data}, failed_chunks)"""
    out, failed = {}, 0
    for part in chunks(syms, chunk):
        got = None
        for attempt in range(retries + 1):
            try:
                got = fetch_chunk(part)
                break
            except Exception as ex:
                print('rs2 chunk failed (attempt %d): %s' % (attempt + 1, str(ex)[:100]))
                sleeper(2)
        if got is None:
            failed += 1
        else:
            out.update(got)
        sleeper(sleep)
    return out, failed


def rs2_rows(info, data, bench_rows, now_date=None):
    """info [{'t','n','e'}] · data {sym: {'close':[(date,c)], 'vol':[v]}} · bench_rows [(date,c)] (SPY)
    → (rows, table, liquid_info, n_rated) · rows only for liquid + rated stocks · liquid_info = every liquid name (rated or not)
    · table = {'asOf','n','cuts','cuts4w'} (the liquid-universe table — also used for the Watch ratings)"""
    liquid = []
    for x in info:
        d = data.get(x['t'])
        if not d or not d.get('close'):
            continue
        rows = bp._rows(d['close'])
        cl = [c for _, c in rows]
        vol = [float(v) for v in d['vol']][-len(cl):] if d.get('vol') else []
        a = adv50(cl, vol)
        if is_liquid(cl[-1] if cl else None, a):
            liquid.append((x, rows, a))
    table = bp.rs_table({x['t']: r for x, r, _ in liquid}, lambda y: 'us').get('us')
    out = []
    for x, rows, a in liquid:
        rs = bp.rs_for(x['t'], rows, bench_rows, table, 'SPY')
        if rs.get('rating') is None:
            continue
        out.append(compact(x, rows, a, rs))
    out.sort(key=lambda r: (-r['r'], r['t']))
    return out, table, [x for x, _, _ in liquid], len(out)


def _r(v, k):
    return None if v is None else round(float(v), k)


def compact(x, rows, a, rs):
    """short-key row: t n e s i | r p l h o x xd c v | a3 a6 a9 a12"""
    row = {'t': x['t'], 'n': x['n'], 'e': x['e'], 'r': rs['rating'], 'p': rs.get('rating4wAgo'),
           'l': {'up': 'u', 'down': 'd', 'flat': 'f'}.get(rs.get('line'), ''),
           'h': 2 if rs.get('newHigh') else 1 if rs.get('newHigh5d') else 0,
           'o': _r(rs.get('offHigh'), 3), 'x': _r(rs.get('hi52'), 2), 'xd': rs.get('hi52Date') or '', 'c': round(rows[-1][1], 2), 'v': int(round(a)),
           'a3': _r(rs.get('r3m'), 3), 'a6': _r(rs.get('r6m'), 3), 'a9': _r(rs.get('r9m'), 3), 'a12': _r(rs.get('r12m'), 3)}
    return row


def with_sectors(rows, sectors):
    """sectors {sym: 'Sector|Industry'} → rows get s / i"""
    for r in rows:
        v = sectors.get(r['t'])
        if v:
            s, _, i = v.partition('|')
            r['s'], r['i'] = s, i
    return rows


def split_docs(as_of, rows, limit=DOC_LIMIT, part_rows=PART_ROWS):
    """→ {docId: dict} · one doc 'latest' when it fits `limit` bytes, else latest (header with parts) + latest_0..k (≤ part_rows rows each)"""
    one = {'asOf': as_of, 'n': len(rows), 'rows': rows}
    if len(json.dumps(one, separators=(',', ':'), ensure_ascii=False).encode('utf-8')) <= limit:
        return {'latest': one}
    parts = chunks(rows, part_rows)
    docs = {'latest': {'asOf': as_of, 'n': len(rows), 'parts': len(parts)}}
    for i, p in enumerate(parts):
        docs['latest_%d' % i] = {'asOf': as_of, 'i': i, 'rows': p}
    return docs


def doc_bytes(doc):
    return len(json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode('utf-8'))


def universe_stale(meta, now, days=UNIVERSE_REFRESH_DAYS):
    at = (meta or {}).get('universeAt')
    if not at or not (meta or {}).get('liquid'):
        return True
    try:
        return (now - dt.datetime.fromisoformat(at)).days >= days
    except ValueError:
        return True


# ───────────────────────── network side ─────────────────────────
def _http(url):
    import urllib.request
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'rs2-universe/1'}), timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


def _yf_fetch_chunk(part, days=HISTORY_DAYS):
    """adjusted close + volume, daily · {sym: {'close': [(date, c)], 'vol': [v]}} (a symbol with no data = absent)"""
    import yfinance as yf
    start = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    df = yf.download(part, start=start, interval='1d', auto_adjust=True, progress=False, group_by='column', threads=True)
    cl, vo = df['Close'], df['Volume']
    if not hasattr(cl, 'columns'):
        cl, vo = cl.to_frame(part[0]), vo.to_frame(part[0])
    out = {}
    for y in part:
        if y in cl.columns:
            c = cl[y]
            m = c.notna()
            c = c[m]
            if len(c):
                out[y] = {'close': list(c.items()), 'vol': [float(v) if v == v else 0.0 for v in vo[y][m]]}
    return out


def _yf_sector(y):
    import yfinance as yf
    info = yf.Ticker(y).info or {}
    return str(info.get('sector') or ''), str(info.get('industry') or '')


def fill_sectors(rows, cache, budget_s=SECTOR_BUDGET_S, getter=None, clock=time.time):
    """look up sector|industry for rows missing from the cache, best-rated first, until the time budget runs out"""
    getter = getter or _yf_sector
    t0, n = clock(), 0
    for r in rows:
        if r['t'] in cache:
            continue
        if clock() - t0 > budget_s:
            break
        try:
            s, i = getter(r['t'])
            cache[r['t']] = (s + '|' + i) if (s or i) else '|'
        except Exception:
            pass
        n += 1
    return n


def build(base, now, seed_sectors=None):
    """run the whole job against Firestore `base` (users/{uid}) → dict(us table, stats) or raises. Keeps yesterday's doc on failure."""
    meta_ref = base.collection('rs2').document('_meta')
    snap0 = meta_ref.get()
    meta = (snap0.to_dict() or {}) if snap0.exists else {}
    uni_ref = base.collection('rs2').document('_universe')
    usnap = uni_ref.get()
    meta['liquid'] = ((usnap.to_dict() or {}).get('liquid') or []) if usnap.exists else []
    t0 = time.time()
    try:
        full = universe_stale(meta, now) or os.environ.get('RS2_FULL') == '1'
        if full:
            info = parse_symbol_files(_http(NASDAQ_URL), _http(OTHER_URL))
            print('rs2: symbol files → %d common stocks' % len(info))
        else:
            info = meta['liquid']
        syms = [x['t'] for x in info]
        data, bad = fetch_chunked(syms + ['SPY'], _yf_fetch_chunk)
        spy = bp._rows(data.pop('SPY', {}).get('close') or [])
        if len(spy) < bp.RS_HI_WIN:
            raise RuntimeError('SPY benchmark too short (%d rows)' % len(spy))
        if len(data) < 0.5 * len(syms):
            raise RuntimeError('only %d of %d symbols downloaded' % (len(data), len(syms)))
        rows, table, liq, n_rated = rs2_rows(info, data, spy)
        n_liq = len(liq)
        if n_liq < bp.RS_MIN_UNIVERSE or not table:
            raise RuntimeError('liquid universe too small (%d)' % n_liq)
        sec_ref = base.collection('rs2').document('_sectors')
        snap = sec_ref.get()
        cache = dict((snap.to_dict() or {}).get('m') or {}) if snap.exists else {}
        for k, v in (seed_sectors or {}).items():
            cache.setdefault(k, v)
        got = fill_sectors(rows, cache)
        if got:
            sec_ref.set({'m': cache, 'at': now.isoformat()})
        with_sectors(rows, cache)
        as_of = table['asOf']
        docs = split_docs(as_of, rows)
        for k, v in docs.items():
            base.collection('rs2').document(k).set(v)
        liquid = liq if full else info
        m = {'asOf': as_of, 'n': n_liq, 'nRated': n_rated, 'runAt': now.isoformat(), 'runSecs': round(time.time() - t0),
             'universeAt': now.isoformat() if full else meta.get('universeAt'), 'liquid': liquid, 'failedChunks': bad,
             'parts': len(docs) - 1 if 'parts' in docs['latest'] else 0, 'bytes': {k: doc_bytes(v) for k, v in docs.items()},
             'error': None, 'rule': 'close>=10 and adv50>=10M'}
        if full:
            uni_ref.set({'liquid': liquid, 'at': now.isoformat()})
        m.pop('liquid')
        base.collection('rs2').document('_meta').set(m)
        print('rs2: liquid %d · rated %d · docs %s · %ds' % (n_liq, n_rated, {k: doc_bytes(v) for k, v in docs.items()}, time.time() - t0))
        return table
    except Exception as ex:
        print('rs2 failed:', str(ex)[:200])
        meta_ref.set({'error': str(ex)[:300], 'errorAt': now.isoformat()}, merge=True)   # yesterday's rs2/latest stays
        return None


if __name__ == '__main__':
    print('library module — run via build_prices.py')
