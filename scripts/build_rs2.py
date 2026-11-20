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


SAMPLE_N = 1500               # random non-liquid common stocks added to the weekly whole-market table
MIN_DL_RATIO = 0.80           # fewer than 80% of the requested symbols downloaded → keep last week's table (cutsStale)
R1_WIN, R3_WIN = 21, 63       # 1-month / 3-month return windows (sessions)
EARN_CAP = 300                # weekly earnings lookups: names matching a preset, best RS first
EARN_BUDGET_S = 240
# Preset thresholds — keep in sync with RS2_PRESETS in index.html (the Screen tab) · used here only to choose whose earnings date to look up
PRESETS = {
    'leaders': lambda r: r['r'] >= 80 and r['o'] is not None and r['o'] >= -0.15,
    'emerging': lambda r: r.get('m3') is not None and r.get('m1') is not None and r['m3'] >= 90 and r['m1'] >= 90 and r['r'] < 85,
    'pullback': lambda r: r.get('m3') is not None and r.get('m1') is not None and r['r'] >= 85 and r['m3'] >= 80 and r['m1'] < 60 and r['o'] is not None and r['o'] >= -0.15,
}


def week_seed(now):
    """new random seed every ISO week → 'YYYY-Www'"""
    y, w, _ = now.isocalendar()
    return '%d-W%02d' % (y, w)


def pick_sample(syms, k=SAMPLE_N, seed='0'):
    """random sample of k symbols (all of them if fewer) · deterministic for a seed · sorted"""
    import random
    syms = sorted(syms)
    if len(syms) <= k:
        return syms
    return sorted(random.Random(str(seed)).sample(syms, k))


def ret(closes, n):
    """close_t / close_{t-n} − 1 · None when too short / non-positive"""
    if len(closes) <= n or not (closes[-1 - n] > 0 and closes[-1] > 0):
        return None
    return closes[-1] / closes[-1 - n] - 1


def score_pack(closes):
    """the four scores a table is built from: s12 = RS1 weighted score · s4 = same 20 sessions ago · s3 = 3-month return · s1 = 1-month return (None when too short)"""
    return {'s12': bp.rs_score(closes), 's4': bp.rs_score(closes, bp.RS_AGO), 's3': ret(closes, R3_WIN), 's1': ret(closes, R1_WIN)}


def build_table(packs, as_of, extra=None):
    """packs [score_pack dict] (liquid + sample) → {'asOf','n','cuts','cuts4w','cuts3m','cuts1m', ...extra} · None when fewer than RS_MIN_UNIVERSE scored"""
    def cuts(k):
        return [round(c, 6) for c in bp.pct_cuts([p[k] for p in packs if p.get(k) is not None])]
    n = sum(1 for p in packs if p.get('s12') is not None)
    if n < bp.RS_MIN_UNIVERSE:
        return None
    t = {'asOf': as_of, 'n': n, 'cuts': cuts('s12'), 'cuts4w': cuts('s4'), 'cuts3m': cuts('s3'), 'cuts1m': cuts('s1')}
    t.update(extra or {})
    return t


def choose_table(new, dl_ratio, last):
    """new table (or None) · share of requested symbols downloaded · last stored table (or None) → (table, stale)
    < 80% downloaded or no new table: keep last week's table (stale) · nothing stored yet: use the new one, still flagged stale"""
    if new is not None and dl_ratio >= MIN_DL_RATIO:
        return new, False
    if last and last.get('cuts'):
        return last, True
    return new, True


def classify(info, data):
    """→ (liquid [(x, rows, adv)], other [(x, rows)]) · other = not liquid but has ≥ 253 bars (eligible for the sample)"""
    liquid, other = [], []
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
        elif len(cl) >= bp.RS_MIN_BARS:
            other.append((x, rows))
    return liquid, other


def table_for(liquid, other, bench_asof=None, seed='0', sample_n=SAMPLE_N):
    """whole-market table = liquid names + a random non-liquid sample (≥ 252 bars) → (table, sample_size)"""
    keep = set(pick_sample([x['t'] for x, _ in other], sample_n, seed))
    packs = [score_pack([c for _, c in r]) for _, r, _ in liquid] + [score_pack([c for _, c in r]) for x, r in other if x['t'] in keep]
    asof = max((r[-1][0].isoformat() for _, r, _ in liquid), default='')
    return build_table(packs, asof, {'sample': len(keep), 'seed': str(seed)}), len(keep)


def rs2_rows(info, data, bench_rows, table=None, seed='0'):
    """info [{'t','n','e'}] · data {sym: {'close':[(date,c)], 'vol':[v]}} · bench_rows [(date,c)] (SPY) · table = stored whole-market table (None → build one from liquid + sample)
    → (rows, table, liquid_info, n_rated) · rows only for liquid + rated stocks, best RS first"""
    liquid, other = classify(info, data)
    if table is None:
        table, _ = table_for(liquid, other, seed=seed)
    out = []
    if table:
        for x, rows, a in liquid:
            rs = bp.rs_for(x['t'], rows, bench_rows, table, 'SPY')
            if rs.get('rating') is None:
                continue
            cl = [c for _, c in rows]
            out.append(compact(x, rows, a, rs, rate_ret(ret(cl, R3_WIN), table.get('cuts3m')), rate_ret(ret(cl, R1_WIN), table.get('cuts1m'))))
    out.sort(key=lambda r: (-r['r'], r['t']))
    return out, table, [x for x, _, _ in liquid], len(out)


def rate_ret(v, cuts):
    return bp.rs_rating(v, cuts) if (v is not None and cuts) else None


def _r(v, k):
    return None if v is None else round(float(v), k)


def compact(x, rows, a, rs, m3=None, m1=None):
    """short-key row: t n e s i | r (12M rating) p (4w ago) m3 m1 (3M / 1M ratings) l h o x xd c v | a3 a6 a9 a12 (returns) | nx (next earnings)"""
    row = {'t': x['t'], 'n': x['n'], 'e': x['e'], 'r': rs['rating'], 'p': rs.get('rating4wAgo'), 'm3': m3, 'm1': m1,
           'l': {'up': 'u', 'down': 'd', 'flat': 'f'}.get(rs.get('line'), ''),
           'h': 2 if rs.get('newHigh') else 1 if rs.get('newHigh5d') else 0,
           'o': _r(rs.get('offHigh'), 3), 'x': _r(rs.get('hi52'), 2), 'xd': rs.get('hi52Date') or '', 'c': round(rows[-1][1], 2), 'v': int(round(a)),
           'a3': _r(rs.get('r3m'), 3), 'a6': _r(rs.get('r6m'), 3), 'a9': _r(rs.get('r9m'), 3), 'a12': _r(rs.get('r12m'), 3)}
    return row


def earn_candidates(rows, cap=EARN_CAP):
    """tickers matching any preset, best RS first, at most `cap`"""
    out = []
    for r in rows:
        if any(f(r) for f in PRESETS.values()):
            out.append(r['t'])
            if len(out) >= cap:
                break
    return out


def parse_earn(v):
    """yfinance calendar value (date / datetime / list of them / 'YYYY-MM-DD…') → 'YYYY-MM-DD' of the earliest, or ''"""
    if isinstance(v, (list, tuple)):
        ds = [parse_earn(x) for x in v]
        ds = [d for d in ds if d]
        return min(ds) if ds else ''
    if hasattr(v, 'isoformat'):
        return v.isoformat()[:10]
    s = str(v or '')[:10]
    return s if re.match(r'^\d{4}-\d{2}-\d{2}$', s) else ''


MAX_MISS = 30     # consecutive failed / empty lookups → assume Yahoo is rate-limiting us and stop (nothing is cached for a miss)


def fill_earnings(tickers, cache, today, budget_s=EARN_BUDGET_S, getter=None, clock=time.time):
    """weekly lookup: refresh a ticker when it has no cached date or the cached date has passed · stops at the time budget or after MAX_MISS misses in a row
    · a miss (error / no date) is NOT cached · returns lookups made"""
    getter = getter or _yf_earn
    t0, n, miss = clock(), 0, 0
    for y in tickers:
        c = cache.get(y)
        if c and c >= today:
            continue
        if clock() - t0 > budget_s or miss >= MAX_MISS:
            break
        n += 1
        try:
            d = parse_earn(getter(y))
        except Exception:
            d = ''
        if d:
            cache[y], miss = d, 0
        else:
            miss += 1
    return n


def with_earnings(rows, cache, today):
    for r in rows:
        d = cache.get(r['t'])
        if d and d >= today:
            r['nx'] = d
    return rows


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


def _yf_earn(y):
    """next earnings date from the yfinance calendar (None when unknown)"""
    import yfinance as yf
    cal = yf.Ticker(y).calendar
    if isinstance(cal, dict):
        return cal.get('Earnings Date')
    return None


def stooq_symbol(y):
    """Yahoo symbol → Stooq: BRK-B → brk-b.us"""
    return str(y).strip().lower() + '.us'


def parse_stooq_csv(txt, days=HISTORY_DAYS):
    """Stooq daily CSV (Date,Open,High,Low,Close,Volume — prices are NOT split/dividend adjusted) → {'close': [(date, c)], 'vol': [v]} for the last `days` calendar days · {} when empty"""
    ls = [l for l in str(txt or '').strip().split('\n') if l.strip()]
    if len(ls) < 2 or not ls[0].lower().startswith('date'):
        return {}
    cut = (dt.date.today() - dt.timedelta(days=days)).isoformat()
    close, vol = [], []
    for ln in ls[1:]:
        f = ln.strip().split(',')
        if len(f) < 6 or f[0] < cut:
            continue
        try:
            close.append((dt.date.fromisoformat(f[0]), float(f[4])))
            vol.append(float(f[5] or 0))
        except ValueError:
            continue
    return {'close': close, 'vol': vol} if close else {}


def _stooq_fetch_chunk(part):
    """fallback reader behind RS2_SOURCE=stooq (off by default · untested against the live service) — one CSV per symbol"""
    out = {}
    for y in part:
        try:
            d = parse_stooq_csv(_http('https://stooq.com/q/d/l/?s=%s&i=d' % stooq_symbol(y)))
        except Exception:
            continue
        if d:
            out[y] = d
    return out


def fetch_fn():
    return _stooq_fetch_chunk if os.environ.get('RS2_SOURCE', '').lower() == 'stooq' else _yf_fetch_chunk


def _yf_sector(y):
    import yfinance as yf
    info = yf.Ticker(y).info or {}
    return str(info.get('sector') or ''), str(info.get('industry') or '')


def fill_sectors(rows, cache, budget_s=SECTOR_BUDGET_S, getter=None, clock=time.time):
    """look up sector|industry for rows missing from the cache, best-rated first, until the time budget runs out or MAX_MISS lookups in a row come back empty
    (Yahoo rate-limiting) · an empty answer is not cached"""
    getter = getter or _yf_sector
    t0, n, miss = clock(), 0, 0
    for r in rows:
        if r['t'] in cache:
            continue
        if clock() - t0 > budget_s or miss >= MAX_MISS:
            break
        n += 1
        try:
            s, i = getter(r['t'])
        except Exception:
            s = i = ''
        if s or i:
            cache[r['t']], miss = s + '|' + i, 0
        else:
            miss += 1
    return n


def build(base, now, seed_sectors=None):
    """run the whole job against Firestore `base` (users/{uid}) → the whole-market table used (dict) or None on failure. Keeps yesterday's doc on failure.
    weekly (universe stale / RS2_FULL=1): all symbols → liquid list + random non-liquid sample → new table (kept in rs2/_meta.cuts…) + earnings lookups
    daily: stored liquid list → scores mapped with the stored table"""
    col = base.collection('rs2')
    meta_ref = col.document('_meta')
    snap0 = meta_ref.get()
    meta = (snap0.to_dict() or {}) if snap0.exists else {}
    uni_ref = col.document('_universe')
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
        data, bad = fetch_chunked(syms + ['SPY'], fetch_fn())
        spy = bp._rows(data.pop('SPY', {}).get('close') or [])
        if len(spy) < bp.RS_HI_WIN:
            raise RuntimeError('SPY benchmark too short (%d rows)' % len(spy))
        dl_ratio = len(data) / float(len(syms) or 1)
        if dl_ratio < 0.5:
            raise RuntimeError('only %d of %d symbols downloaded' % (len(data), len(syms)))
        last = {k: meta[k] for k in ('asOf', 'n', 'cuts', 'cuts4w', 'cuts3m', 'cuts1m', 'sample', 'seed') if k in meta} if meta.get('cuts') else None
        liquid, other = classify(info, data)
        if full:
            new, _ = table_for(liquid, other, seed=week_seed(now))
            table, stale = choose_table(new, dl_ratio, last)
        elif last:
            table, stale = last, bool(meta.get('cutsStale'))
        else:       # first ever run is a daily one: liquid-only table, flagged stale until the next weekly run
            table, stale = table_for(liquid, [], seed='0')[0], True
        rows, table, liq, n_rated = rs2_rows(info, data, spy, table)
        n_liq = len(liq)
        if n_liq < bp.RS_MIN_UNIVERSE or not table:
            raise RuntimeError('liquid universe too small (%d)' % n_liq)
        today = dt.date.today().isoformat()
        sec_ref, earn_ref = col.document('_sectors'), col.document('_earn')
        snap = sec_ref.get()
        cache = dict((snap.to_dict() or {}).get('m') or {}) if snap.exists else {}
        for k, v in (seed_sectors or {}).items():
            cache.setdefault(k, v)
        got = fill_sectors(rows, cache)
        if got:
            sec_ref.set({'m': cache, 'at': now.isoformat()})
        with_sectors(rows, cache)
        es = earn_ref.get()
        ecache = dict((es.to_dict() or {}).get('m') or {}) if es.exists else {}
        if full and fill_earnings(earn_candidates(rows), ecache, today):
            earn_ref.set({'m': ecache, 'at': now.isoformat()})
        with_earnings(rows, ecache, today)
        as_of = table['asOf']
        docs = split_docs(as_of, rows)
        for k, v in docs.items():
            col.document(k).set(v)
        if full:
            uni_ref.set({'liquid': liq, 'at': now.isoformat()})
        m = {'asOf': as_of, 'n': n_liq, 'nRated': n_rated, 'runAt': now.isoformat(), 'runSecs': round(time.time() - t0),
             'universeAt': now.isoformat() if full else meta.get('universeAt'), 'failedChunks': bad, 'dlRatio': round(dl_ratio, 3),
             'parts': len(docs) - 1 if 'parts' in docs['latest'] else 0, 'bytes': {k: doc_bytes(v) for k, v in docs.items()},
             'cuts': table['cuts'], 'cuts4w': table['cuts4w'], 'cuts3m': table.get('cuts3m'), 'cuts1m': table.get('cuts1m'),
             'cutsN': table['n'], 'sample': table.get('sample'), 'seed': table.get('seed'), 'cutsStale': stale, 'earnN': len(ecache),
             'source': os.environ.get('RS2_SOURCE', 'yahoo') or 'yahoo', 'error': None, 'rule': 'close>=10 and adv50>=10M'}
        col.document('_meta').set(m)
        print('rs2: liquid %d · rated %d · table n %s (sample %s%s) · docs %s · %ds' % (n_liq, n_rated, table['n'], table.get('sample'), ' STALE' if stale else '', {k: doc_bytes(v) for k, v in docs.items()}, time.time() - t0))
        return table
    except Exception as ex:
        print('rs2 failed:', str(ex)[:200])
        meta_ref.set({'error': str(ex)[:300], 'errorAt': now.isoformat()}, merge=True)   # yesterday's rs2/latest stays
        return None


if __name__ == '__main__':
    print('library module — run via build_prices.py')
