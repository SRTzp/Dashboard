#!/usr/bin/env python3
"""PX1 · ราคาปิดสัปดาห์ + EMA10 (รายสัปดาห์) ของหุ้น Core → Firestore users/{uid}/prices/{ySym} + _meta

อ่านการ์ด users/{uid}/coreCards (status plan/open) → ดึง yfinance รายวัน 2 ปี → แท่งสัปดาห์ (จบศุกร์) → เขียนกลับ
env: FIREBASE_SA (JSON service account ทั้งก้อน) · FIREBASE_UID
ห้ามพิมพ์ค่า secret / ห้ามพิมพ์ JSON กุญแจ ใน log (สคริปต์นี้ไม่พิมพ์ env เลย)
ฟังก์ชันล้วน (ไม่แตะเน็ต · ไม่ต้องมี pandas): to_ysym · weekly_closes · ema10 · check · run
"""
import bisect
import datetime as dt
import json
import math
import os
import sys

VER = 2
SPAN = 10

# ── RS1 · RS line + RS Rating 1–99 (แสดงผล/จัดอันดับเท่านั้น — ไม่ใช่ gate) ──
RS_WEIGHTS = ((63, 0.4), (126, 0.2), (189, 0.2), (252, 0.2))   # (sessions, weight): 3m 6m 9m 12m
RS_MIN_BARS = 253            # r12m = close_t / close_{t-252} - 1 ต้องมี 253 แท่ง
RS_AGO = 20                  # 4 สัปดาห์ = 20 sessions
RS_LINE_WIN = 20             # ความชัน RS line
RS_LINE_BAND = 0.02          # ±2%
RS_HI_WIN = 252
RS_BENCH = {'us': 'SPY', 'th': '^SET.BK'}
RS_BENCH_FALLBACK = {'th': 'TDEX.BK'}   # SET50 ETF · ใช้เมื่อ ^SET.BK มี < 252 แถว (Yahoo ส่ง index มาไม่ครบ)
RS_MIN_UNIVERSE = 30         # universe ที่ดึงได้น้อยกว่านี้ → ไม่ให้ rating (reason universe<30)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def to_ysym(ticker, market=None):
    """TH (market=='TH' หรือลงท้าย .BK) → XXX.BK · US → ตัวใหญ่"""
    t = ''.join(str(ticker or '').split()).upper()
    if not t:
        return ''
    if str(market or '').upper() == 'TH' or t.endswith('.BK'):
        return (t[:-3] if t.endswith('.BK') else t) + '.BK'
    return t


def _rows(daily):
    """รับ list[(date, close)] หรือ pandas Series (index=วันที่) → [(date, float)] เรียงวัน · ตัดค่าว่าง"""
    items = daily.items() if hasattr(daily, 'items') else daily
    out = []
    for d, v in items:
        if isinstance(d, dt.datetime):        # รวม pandas.Timestamp
            d = d.date()
        elif isinstance(d, str):
            d = dt.date.fromisoformat(d[:10])
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        out.append((d, f))
    out.sort(key=lambda x: x[0])
    return out


def _friday_of(d):
    return d + dt.timedelta(days=(4 - d.weekday()) % 7)


def weekly_closes(daily, now_utc):
    """รวมรายวัน → แท่งสัปดาห์จบศุกร์ (เก่า→ใหม่) · ตัดสัปดาห์ที่ยังไม่จบ
    สัปดาห์จบเมื่อ วันนี้(UTC) > ศุกร์ของสัปดาห์นั้น หรือ เป็นวันศุกร์และเลย 22:00 UTC (หลังปิดทั้ง US/TH)
    คืน [{'closeDate':'YYYY-MM-DD' (วันซื้อขายสุดท้ายจริงของสัปดาห์), 'close':float}]"""
    weeks = {}
    for d, c in _rows(daily):
        weeks[_friday_of(d)] = (d, c)          # วันสุดท้ายของสัปดาห์ทับตัวก่อนหน้า
    today = now_utc.date()
    out = []
    for fri in sorted(weeks):
        done = today > fri or (today == fri and now_utc.hour >= 22)
        if done:
            d, c = weeks[fri]
            out.append({'closeDate': d.isoformat(), 'close': c})
    return out


def ema10(closes):
    """EMA span=10 แบบ ewm(adjust=False) (ตรง TradingView) · ข้อมูล < 10 ค่า → None"""
    xs = [float(x) for x in closes]
    if len(xs) < SPAN:
        return None
    a = 2.0 / (SPAN + 1)
    e = xs[0]
    for x in xs[1:]:
        e = a * x + (1 - a) * e
    return e


def check(close, prev=None):
    """(ok, suspect) · close ≤ 0 / NaN → ไม่ผ่าน · เปลี่ยนจากสัปดาห์ก่อน > 40% → suspect"""
    try:
        c = float(close)
    except (TypeError, ValueError):
        return False, False
    if math.isnan(c) or c <= 0:
        return False, False
    suspect = False
    if prev is not None:
        try:
            p = float(prev)
            if p > 0 and abs(c / p - 1) > 0.40:
                suspect = True
        except (TypeError, ValueError):
            pass
    return True, suspect


def pick_tickers(cards):
    """การ์ด plan/open → {ySym: ticker} ตัดซ้ำ (หลายบัญชี = 1 ตัว)"""
    seen = {}
    for c in cards:
        if str(c.get('status')) not in ('plan', 'open'):
            continue
        y = to_ysym(c.get('ticker'), c.get('market'))
        if y and y not in seen:
            seen[y] = str(c.get('ticker') or '').strip().upper()
    return seen


def run(cards, fetch, write, now):
    """fetch(ySym)->daily (list/Series) หรือ raise · write(docId, dict) · now = datetime UTC
    คืน exit code: 1 ถ้าล้มทุกตัว (มีอย่างน้อย 1 ตัวให้ดึง) ไม่งั้น 0"""
    syms = pick_tickers(cards)
    ok, failed = [], []
    for y, tk in syms.items():
        try:
            wk = weekly_closes(fetch(y), now)
            if not wk:
                raise ValueError('no completed week')
            last = wk[-1]
            prev = wk[-2]['close'] if len(wk) > 1 else None
            good, suspect = check(last['close'], prev)
            if not good:
                raise ValueError('bad close')
            e = ema10([w['close'] for w in wk])
            write(y, {'sym': tk, 'ySym': y, 'close': round(last['close'], 4), 'closeDate': last['closeDate'],
                      'ema10w': None if e is None else round(e, 4), 'weeks': len(wk), 'suspect': suspect, 'src': 'yfinance'})
            ok.append(y)
        except Exception as ex:           # ตัวที่ดึงไม่ได้ → ไม่เขียนทับ doc เดิม · ทำตัวอื่นต่อ
            failed.append({'ySym': y, 'why': str(ex)[:120]})
    write('_meta', {'runAt': now.isoformat(), 'ok': ok, 'failed': failed, 'n': len(syms), 'ver': VER})
    print(f'prices: ok {len(ok)}/{len(syms)}' + (' · failed ' + ','.join(f['ySym'] for f in failed) if failed else ''))
    return 1 if (syms and not ok) else 0


# ───────────────────────── RS1 (ฟังก์ชันล้วน ไม่แตะเน็ต) ─────────────────────────
def rs_market(ysym):
    """ySym → 'th' (ลงท้าย .BK) | 'us'"""
    return 'th' if str(ysym).upper().endswith('.BK') else 'us'


def rs_score(closes, offset=0):
    """score = 0.4·r3m + 0.2·r6m + 0.2·r9m + 0.2·r12m (return ราคาปรับแล้ว, 63/126/189/252 sessions)
    offset = ย้อนไปกี่ session (4 สัปดาห์ก่อน = 20) · แท่งไม่พอ → None"""
    xs = [float(x) for x in closes]
    if offset:
        xs = xs[:len(xs) - offset]
    if len(xs) < RS_MIN_BARS:
        return None
    t = xs[-1]
    total = 0.0
    for n, w in RS_WEIGHTS:
        base = xs[-1 - n]
        if not (base > 0 and t > 0):
            return None
        total += w * (t / base - 1)
    return total


def pct_cuts(scores):
    """cut-off 99 ค่า = เปอร์เซนไทล์ที่ 1..99 (linear interpolation เหมือน numpy) · ว่าง → []"""
    xs = sorted(scores)
    n = len(xs)
    if n == 0:
        return []
    out = []
    for k in range(1, 100):
        pos = (n - 1) * k / 100.0
        lo = int(math.floor(pos))
        hi = min(lo + 1, n - 1)
        out.append(xs[lo] + (xs[hi] - xs[lo]) * (pos - lo))
    return out


def rs_rating(score, cuts):
    """rating 1–99 = 1 + จำนวน cut-off ที่ต่ำกว่า score (คะแนนเท่ากัน = rating เท่ากัน) · clamp 1..99"""
    if score is None or not cuts:
        return None
    return max(1, min(99, bisect.bisect_left(cuts, score) + 1))


def align(stock, bench):
    """[(date, close)] 2 ชุด → [(date, stock, bench)] เฉพาะวันที่มีทั้งคู่"""
    b = dict(bench)
    return [(d, c, b[d]) for d, c in stock if d in b and b[d] > 0]


def rs_line_info(aligned):
    """RS line = stock ÷ bench · คืน (line 'up'|'flat'|'down'|None, newHigh, newHigh5d) (None ถ้าแท่งไม่พอ)
    newHigh = วันนี้ ≥ max 252 sessions (รวมวันนี้) · newHigh5d = เป็นจริงในวันใดวันหนึ่งของ 5 session ล่าสุด"""
    L = [c / b for _, c, b in aligned]
    if len(L) < RS_HI_WIN:
        return None, None, None
    chg = round(L[-1] / L[-1 - RS_LINE_WIN] - 1, 9)   # กัน float ที่ขอบ ±2%
    line = 'up' if chg > RS_LINE_BAND else 'down' if chg < -RS_LINE_BAND else 'flat'

    def hi_at(i):
        lo = max(0, i - RS_HI_WIN + 1)
        return L[i] >= max(L[lo:i + 1])
    new_high = hi_at(len(L) - 1)
    new_high5d = any(hi_at(i) for i in range(len(L) - 5, len(L)))
    return line, new_high, new_high5d


def rs_table(universe_closes, ysym_market):
    """universe_closes {ySym: [(date,close)]} → {mkt: {'asOf','n','cuts','cuts4w'}} (ตลาดที่ n < RS_MIN_UNIVERSE ไม่ใส่)"""
    sc, ago, asof = {'us': [], 'th': []}, {'us': [], 'th': []}, {'us': '', 'th': ''}
    for y, rows in universe_closes.items():
        m = ysym_market(y)
        cl = [c for _, c in rows]
        s = rs_score(cl)
        if s is None:
            continue
        sc[m].append(s)
        s4 = rs_score(cl, RS_AGO)
        if s4 is not None:
            ago[m].append(s4)
        asof[m] = max(asof[m], rows[-1][0].isoformat())
    out = {}
    for m in ('us', 'th'):
        if len(sc[m]) >= RS_MIN_UNIVERSE:
            out[m] = {'asOf': asof[m], 'n': len(sc[m]), 'cuts': [round(c, 6) for c in pct_cuts(sc[m])],
                      'cuts4w': [round(c, 6) for c in pct_cuts(ago[m])]}
    return out


def pick_bench(m, clean):
    """benchmark ของตลาด m → (symbol, rows) · หลัก ถ้า ≥ 252 แถว ไม่งั้นลอง fallback ที่ ≥ 252 แถว ไม่งั้นคืนหลัก (rows อาจสั้น/None)"""
    main = RS_BENCH[m]
    if len(clean.get(main) or []) >= RS_HI_WIN:
        return main, clean[main]
    fb = RS_BENCH_FALLBACK.get(m)
    if fb and len(clean.get(fb) or []) >= RS_HI_WIN:
        return fb, clean[fb]
    return main, clean.get(main)


def rs_hi_ret(rows):
    """WL2 — {hi52, hi52Date, offHigh, r3m, r6m, r9m, r12m} จาก adj close (ใช้ 252 แท่งล่าสุดรวมวันนี้ · offHigh = close/hi52 − 1 · rNm = return 63/126/189/252 sessions)
    ฟิลด์ที่แท่งไม่พอ = None · เพิ่มอย่างเดียว ไม่แตะสูตร rating"""
    out = {'hi52': None, 'hi52Date': None, 'offHigh': None, 'r3m': None, 'r6m': None, 'r9m': None, 'r12m': None}
    if not rows:
        return out
    cl = [float(c) for _, c in rows]
    t = cl[-1]
    win = rows[-RS_HI_WIN:]
    if len(rows) >= RS_HI_WIN and t > 0:
        d, h = max(win, key=lambda x: (float(x[1]), x[0]))      # เสมอกัน → วันล่าสุด
        h = float(h)
        out['hi52'], out['hi52Date'], out['offHigh'] = round(h, 4), d.isoformat(), round(t / h - 1, 4)
    for key, (n, _w) in zip(('r3m', 'r6m', 'r9m', 'r12m'), RS_WEIGHTS):
        if len(cl) > n and cl[-1 - n] > 0 and t > 0:
            out[key] = round(t / cl[-1 - n] - 1, 4)
    return out


def rs_for(ysym, rows, bench_rows, table, bench_sym=None):
    """สร้าง dict rs ของ 1 ตัว · rows/bench_rows = [(date, adj close)] (None = ดึงไม่ได้) · table = rsTable[mkt] หรือ None
    bench_sym = ชื่อ benchmark ที่ใช้จริง (บันทึกใน 'bench')"""
    m = rs_market(ysym)
    rs = {'rating': None, 'rating4wAgo': None, 'line': None, 'newHigh': None, 'newHigh5d': None,
          'bench': bench_sym or RS_BENCH[m], 'asOf': rows[-1][0].isoformat() if rows else None}
    if not rows:
        rs['reason'] = 'no-data'
        return rs
    rs.update(rs_hi_ret(rows))      # WL2 — เพิ่มอย่างเดียว
    if len(rows) < RS_MIN_BARS:
        rs['reason'] = 'history<252'
    elif not table or not table.get('cuts'):
        rs['reason'] = 'universe<%d' % RS_MIN_UNIVERSE
    else:
        cl = [c for _, c in rows]
        rs['rating'] = rs_rating(rs_score(cl), table['cuts'])
        rs['rating4wAgo'] = rs_rating(rs_score(cl, RS_AGO), table.get('cuts4w') or [])
    if bench_rows:
        rs['line'], rs['newHigh'], rs['newHigh5d'] = rs_line_info(align(rows, bench_rows))
        if rs['line'] is None and 'reason' not in rs:
            rs['reason'] = 'bench<252'      # หุ้นมี ≥252 แท่งแต่ benchmark ซ้อนวันไม่ถึง (เช่น Yahoo ส่ง ^SET.BK มาแค่ 1 แท่ง)
    elif 'reason' not in rs:
        rs['reason'] = 'no-bench'
    return rs


def load_universe(path):
    """ไฟล์ข้อความ 1 ticker/บรรทัด · ข้าม # และบรรทัดว่าง · ตัดซ้ำ คงลำดับ"""
    out, seen = [], set()
    try:
        with open(path, encoding='utf-8') as f:
            for ln in f:
                t = ln.split('#')[0].strip().upper()
                if t and t not in seen:
                    seen.add(t)
                    out.append(t)
    except OSError:
        pass
    return out


def pick_rs_tickers(cards, watch):
    """Watchlist (รวม Candidates; ไม่รวม archived) + การ์ด Core plan/open → {ySym: ticker} (ตัดซ้ำ)"""
    seen = dict(pick_tickers(cards))
    for w in watch:
        if w.get('archived') is True:
            continue
        t = w.get('ticker')
        mk = w.get('market') or ('TH' if str(t or '').upper().endswith('.BK') else 'US')
        y = to_ysym(t, mk)
        if y and y not in seen:
            seen[y] = str(t or '').strip().upper()
    return seen


def run_rs(syms, universe, fetch_many, write, now, sector_fetch=None, have_sector=()):
    """syms {ySym: ticker} · universe [ySym] · fetch_many(list)->{ySym: [(date, adj close)]} (ตัวที่ดึงไม่ได้ = ไม่มี key)
    เขียน prices/{ySym} {'rs':…} + prices/_meta {'rsTable':…} · คืน (n_rated, failed list)"""
    benches = list(RS_BENCH.values())
    need = list(dict.fromkeys(list(universe) + list(syms) + benches + list(RS_BENCH_FALLBACK.values())))
    data = fetch_many(need)
    clean = {y: _rows(r) for y, r in data.items() if r is not None and len(r)}
    table = rs_table({y: clean[y] for y in universe if y in clean}, rs_market)
    failed, n = [], 0
    for y, tk in syms.items():
        rows = clean.get(y)
        m = rs_market(y)
        bsym, brows = pick_bench(m, clean)
        rs = rs_for(y, rows, brows, table.get(m), bsym)
        if not rows:
            failed.append({'ySym': y, 'why': 'no-data'})
        doc = {'sym': tk, 'ySym': y, 'rs': rs}
        if sector_fetch and y not in have_sector:      # WL2 — sector/industry ครั้งเดียวต่อ ticker (cache = ฟิลด์ใน prices/{ySym})
            try:
                si = sector_fetch(y) or {}
                if si.get('sector') or si.get('industry'):
                    doc['sector'], doc['industry'] = si.get('sector') or '', si.get('industry') or ''
            except Exception as ex:
                print('sector fetch failed', y, str(ex)[:60])
        write(y, doc)
        n += rs['rating'] is not None
    write('_meta', {'rsTable': table, 'rsRunAt': now.isoformat()})
    print(f'rs: rated {n}/{len(syms)} · universe us {table.get("us", {}).get("n", 0)} th {table.get("th", {}).get("n", 0)}'
          + (' · no-data ' + ','.join(f['ySym'] for f in failed) if failed else ''))
    return n, failed


def _yf_fetch(ysym):
    import yfinance as yf
    df = yf.download(ysym, interval='1d', period='2y', auto_adjust=False, progress=False)
    if df is None or len(df) == 0:
        raise ValueError('no data')
    s = df['Close']
    if hasattr(s, 'columns'):           # yfinance รุ่นใหม่คืน DataFrame หลายระดับ
        s = s.iloc[:, 0]
    return s.dropna()


def _yf_fetch_many(syms, chunk=80):
    """ดึง adjusted close รายวัน 2 ปี ทีละกลุ่ม → {ySym: [(date, close)]} (ตัวที่ล้ม = ไม่มี key)"""
    import yfinance as yf
    out = {}
    syms = list(syms)
    for i in range(0, len(syms), chunk):
        part = syms[i:i + chunk]
        try:
            df = yf.download(part, interval='1d', period='2y', auto_adjust=True, progress=False,
                             group_by='column', threads=True)
            cl = df['Close']
        except Exception as ex:
            print('rs fetch chunk failed:', str(ex)[:100])
            continue
        if not hasattr(cl, 'columns'):          # ตัวเดียว → Series
            cl = cl.to_frame(part[0])
        for y in part:
            if y in cl.columns:
                s = cl[y].dropna()
                if len(s):
                    out[y] = list(s.items())
    return out


def _yf_sector(ysym):
    """WL2 — {'sector','industry'} จาก yfinance (ETF/ดัชนีไม่มี → {})"""
    import yfinance as yf
    info = yf.Ticker(ysym).info or {}
    return {'sector': str(info.get('sector') or ''), 'industry': str(info.get('industry') or '')}


def main():
    import firebase_admin
    from firebase_admin import credentials, firestore
    uid = os.environ.get('FIREBASE_UID', '').strip()
    sa = os.environ.get('FIREBASE_SA', '').strip()
    if not uid or not sa:
        print('ไม่พบ FIREBASE_UID / FIREBASE_SA (ตรวจ Secrets)')
        return 1
    firebase_admin.initialize_app(credentials.Certificate(json.loads(sa)))
    db = firestore.client()
    base = db.collection('users').document(uid)
    cards = [d.to_dict() or {} for d in base.collection('coreCards').stream()]

    def write(doc_id, data):
        data = dict(data)
        if doc_id == '_meta':
            data['runAt'] = firestore.SERVER_TIMESTAMP
        else:
            data['at'] = firestore.SERVER_TIMESTAMP
        base.collection('prices').document(doc_id).set(data, merge=True)   # RS1 — merge: คงฟิลด์เดิม (rs ↔ ราคารายสัปดาห์)

    now = dt.datetime.now(dt.timezone.utc)
    code = run(cards, _yf_fetch, write, now)
    try:        # RS1 — ล้มแล้วไม่ทำให้งานราคารายสัปดาห์เดิมล้ม
        watch = [d.to_dict() or {} for d in base.collection('watchlist').stream()]
        uni = [to_ysym(t) for t in load_universe(os.path.join(ROOT, 'data', 'universe_us.txt'))] + \
              [to_ysym(t, 'TH') for t in load_universe(os.path.join(ROOT, 'data', 'universe_th.txt'))]
        have = {d.id for d in base.collection('prices').stream() if (d.to_dict() or {}).get('sector') or (d.to_dict() or {}).get('industry')}
        run_rs(pick_rs_tickers(cards, watch), uni, _yf_fetch_many, write, now, _yf_sector, have)
    except Exception as ex:
        print('rs failed:', str(ex)[:200])
    return code


if __name__ == '__main__':
    sys.exit(main())
