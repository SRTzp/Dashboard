#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_fundflow.py — คำนวณ 6 ratio ของแถบ Regime แล้วเขียน fundflow.json (เฟส 4 · งาน P1)

หน้า index.html อ่านไฟล์นี้แบบ relative ('fundflow.json') จึงต้องวางไว้ที่ราก repo เดียวกับ index.html
รันโดย GitHub Actions หลังตลาด US ปิด (.github/workflows/fundflow.yml) — ไม่ใช้ LLM ไม่ใช้ secret

ver 3 (RM1): ACWI_BIL และ HYG_IEI = สัญญาณ SMA 20/50 ของ ratio (ไม่ใช่ SMA ของแต่ละ ETF)
  ใช้ราคาปิดแบบ total-return-adjusted เท่านั้น (yfinance auto_adjust=True) — ไม่ fall back เป็นราคาดิบ · ขาดขา = unavailable
  เฉพาะแท่งที่ตลาด US ปิดแล้ว (ตัดแท่งของวันที่ US ปัจจุบันทิ้ง ถ้ารันก่อน 16:15 America/New_York)
  state: SMA20 > SMA50 → green · < → red · เท่ากัน → state ก่อนหน้า (ไม่มี → neutral) · < 50 แท่งที่ align ได้ → unavailable
ratio อื่น (HYG_IEF, HG_GC, SPHB_SPLV, RSP_SPY): ราคาปิดดิบ (auto_adjust=False) · EMA เร็ว vs ช้า · ver 2 เดิม
  up         = EMA เร็ว > EMA ช้า ที่แท่งล่าสุด (SMA keys: green→true · red→false · อื่น→null)
  flip_days  = จำนวนแท่งที่อยู่ฝั่งเดิมติดกัน นับแท่งล่าสุดด้วย (weekly = สัปดาห์ · daily = วัน)
  prev_week  = {'up', 'bar'} สถานะ ณ แท่งสุดท้ายที่อยู่ในสัปดาห์ ISO ก่อนสัปดาห์ของแท่งล่าสุด
               (TF W = แท่งสัปดาห์ก่อนหน้า 1 แท่ง · TF D = แท่งรายวันสุดท้ายของสัปดาห์ก่อนหน้า)
               อ่านจาก EMA ชุดเดียวกับค่าปัจจุบันที่ index ย้อนหลัง (EMA ไม่มองอนาคต)
               หาแท่งไม่ได้ หรือแท่งนั้นมีข้อมูลน้อยกว่า MIN_BARS → None
weekly ใช้แท่งสัปดาห์ (สิ้นสุดวันศุกร์) รวมสัปดาห์ปัจจุบันที่ยังไม่ปิด — ตรงกับที่ TradingView แสดงแบบ realtime

ทดสอบเครื่องตัวเอง:  python3 scripts/build_fundflow.py --out /tmp/fundflow.json
ทดสอบสูตรไม่ต่อเน็ต:  python3 scripts/build_fundflow.py --selftest
"""
import argparse, datetime, json, math, os, sys

RATIOS = {
    # key          ตัวตั้ง   ตัวหาร   TF   EMA(fast,slow)
    'ACWI_BIL':  ('ACWI',  'BIL',  'D', None),                   # RM1: SMA 20/50 ของ ratio · adjusted
    'HYG_IEF':   ('HYG',   'IEF',  'W', (10, 20)),
    'HYG_IEI':   ('HYG',   'IEI',  'D', None),                   # RM1: SMA 20/50 ของ ratio · adjusted
    'HG_GC':     ('HG=F',  'GC=F', 'W', (10, 20)),               # front-month continuous — ต่างจาก HG1!/GC1! ของ TV เล็กน้อยช่วง roll (ยอมรับแล้ว)
    'SPHB_SPLV': ('SPHB',  'SPLV', 'D', (10, 20)),
    'RSP_SPY':   ('RSP',   'SPY',  'D', (10, 20)),
}
SMA_KEYS = ('ACWI_BIL', 'HYG_IEI')   # RM1: ใช้ราคา adjusted + SMA 20/50
def _policy_sma():
    """SMA periods are a policy setting: read POLICY.regime.smaFast / smaSlow from risk-engine.js (the app refuses a file built with other periods) · default 20/50"""
    try:
        src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'risk-engine.js'), encoding='utf-8').read()
        import re
        f, sl = re.search(r'smaFast:\s*(\d+)', src), re.search(r'smaSlow:\s*(\d+)', src)
        if f and sl and 0 < int(f.group(1)) < int(sl.group(1)): return (int(f.group(1)), int(sl.group(1)))
    except Exception: pass
    return (20, 50)
SMA_PAIR = _policy_sma()
ADJ_SYMS = sorted({s for k in SMA_KEYS for s in RATIOS[k][:2]})            # ACWI BIL HYG IEI
RAW_SYMS = sorted({s for k, v in RATIOS.items() if k not in SMA_KEYS for s in v[:2]})
VER = 3
MIN_BARS = 60          # น้อยกว่านี้ EMA ยังไม่นิ่ง → ไม่เขียนค่า ratio นั้น
MIN_OBS_SMA = SMA_PAIR[1]   # RM1: the slow period = minimum aligned observations, otherwise unavailable
NY_CLOSE = (16, 15)    # ตลาด US ปิด 16:00 + 15 นาที (America/New_York)


def ema(vals, span):
    k = 2.0 / (span + 1.0)
    out, e = [], None
    for v in vals:
        e = v if e is None else (v - e) * k + e
        out.append(e)
    return out


def state_of(vals, fast, slow):
    """คืน (up, flip_days, sides) จากลำดับค่า ratio (เก่า→ใหม่) — sides = up ของทุกแท่ง"""
    f, s = ema(vals, fast), ema(vals, slow)
    sides = [a > b for a, b in zip(f, s)]
    up = sides[-1]
    n = 0
    for x in reversed(sides):
        if x != up: break
        n += 1
    return up, n, sides


def prev_week_of(ds, sides, min_bars=MIN_BARS):
    """แท่งสุดท้ายในสัปดาห์ ISO ก่อนสัปดาห์ของแท่งล่าสุด → {'up','bar'} หรือ None"""
    last = ds[-1].isocalendar()[:2]
    for i in range(len(ds) - 2, -1, -1):
        if ds[i].isocalendar()[:2] < last:
            if i + 1 < min_bars: return None
            return {'up': bool(sides[i]), 'bar': ds[i].isoformat()}
    return None


def weekly_last(dates, closes):
    """รวมเป็นแท่งสัปดาห์ (จ–ศ) ใช้ราคาปิดวันสุดท้ายของสัปดาห์"""
    out = {}
    for d, c in zip(dates, closes):
        y, w, _ = d.isocalendar()
        out[(y, w)] = (d, c)          # วันหลังทับวันก่อน = ปิดล่าสุดของสัปดาห์
    return [v for _, v in sorted(out.items())]


def ratio_series(a, b):
    """a, b = dict{date: close} → (dates, ratio) เฉพาะวันที่มีทั้งคู่"""
    ds = sorted(set(a) & set(b))
    ds = [d for d in ds if a[d] and b[d] and math.isfinite(a[d]) and math.isfinite(b[d]) and b[d] != 0]
    return ds, [a[d] / b[d] for d in ds]


def drop_partial(series, now=None):
    """RM1: ตัดแท่งของวันที่ US ปัจจุบันทิ้ง ถ้ายังไม่ถึง 16:15 America/New_York (แท่งยังไม่ปิด)"""
    from zoneinfo import ZoneInfo
    now = now or datetime.datetime.now(datetime.timezone.utc)
    ny = now.astimezone(ZoneInfo('America/New_York'))
    if (ny.hour, ny.minute) >= NY_CLOSE: return series
    return {d: v for d, v in series.items() if d < ny.date()}


def sma(vals, n):
    return sum(vals[-n:]) / n


def sma_states(r):
    """RM1: state ของทุกแท่ง (None ก่อนมี 50 แท่ง) · SMA20>SMA50 green · < red · เท่ากัน → ก่อนหน้า (ไม่มี → neutral)"""
    out, prev = [None] * len(r), None
    for i in range(MIN_OBS_SMA - 1, len(r)):
        a, b = round(sma(r[:i + 1], SMA_PAIR[0]), 12), round(sma(r[:i + 1], SMA_PAIR[1]), 12)
        cur = 'green' if a > b else 'red' if a < b else (prev or 'neutral')
        out[i] = cur
        if a != b: prev = cur
    return out


def _unavailable(a_leg=None, b_leg=None):
    asof = {k: v for k, v in (a_leg or {}).items()}
    return {'tf': 'D', 'sma': list(SMA_PAIR), 'adj': True, 'up': None, 'state': 'unavailable', 'days_in_state': 0,
            'flip_days': 0, 'bar': None, 'inputs_asof': asof or None, 'sma20': None, 'sma50': None, 'ratio': None,
            'prev_week': None}


def sma_item(num, den, a, b):
    """a, b = {date: adjusted close} ของตัวตั้ง/ตัวหาร (ผ่าน drop_partial แล้ว) → item ของ ratio หรือ unavailable"""
    legs = {num: max(a).isoformat() if a else None, den: max(b).isoformat() if b else None}
    if not a or not b: return _unavailable(legs), f'ไม่มีราคา adjusted {num if not a else den}'
    ds, r = ratio_series(a, b)
    if len(r) < MIN_OBS_SMA: return _unavailable(legs), f'ข้อมูลไม่พอ ({len(r)} แท่ง · ต้อง {MIN_OBS_SMA})'
    st = sma_states(r)
    cur = st[-1]
    n = 0
    for x in reversed(st):
        if x != cur: break
        n += 1
    pw = None
    last = ds[-1].isocalendar()[:2]
    for i in range(len(ds) - 2, -1, -1):
        if ds[i].isocalendar()[:2] < last:
            if st[i] in ('green', 'red'): pw = {'up': st[i] == 'green', 'bar': ds[i].isoformat()}
            break
    return {'tf': 'D', 'sma': list(SMA_PAIR), 'adj': True,
            'up': True if cur == 'green' else False if cur == 'red' else None,
            'state': cur, 'days_in_state': int(n), 'flip_days': int(n), 'bar': ds[-1].isoformat(),
            'inputs_asof': legs, 'sma20': round(sma(r, SMA_PAIR[0]), 6), 'sma50': round(sma(r, SMA_PAIR[1]), 6),
            'ratio': round(r[-1], 6), 'prev_week': pw}, None


def compute(prices, adj=None, now=None):
    """prices = {symbol: {date: raw close}} · adj = {symbol: {date: adjusted close}} → (ratios, errs)
    SMA_KEYS ใช้ adj เท่านั้น (ไม่ fall back เป็น raw) · ขาดขา/ข้อมูลไม่พอ → state 'unavailable'"""
    res, errs = {}, []
    adj = adj or {}
    for key, (num, den, tf, pair) in RATIOS.items():
        if key in SMA_KEYS:
            a = drop_partial(adj.get(num) or {}, now)
            b = drop_partial(adj.get(den) or {}, now)
            item, err = sma_item(num, den, a, b)
            if err: errs.append(f'{key}: {err} → unavailable')
            res[key] = item
            continue
        fa, sl = pair
        if num not in prices or den not in prices:
            errs.append(f'{key}: ไม่มีราคา {num if num not in prices else den}'); continue
        ds, r = ratio_series(prices[num], prices[den])
        if tf == 'W':
            wk = weekly_last(ds, r)
            ds, r = [x[0] for x in wk], [x[1] for x in wk]
        if len(r) < MIN_BARS:
            errs.append(f'{key}: ข้อมูลไม่พอ ({len(r)} แท่ง · ต้อง {MIN_BARS})'); continue
        up, n, sides = state_of(r, fa, sl)
        res[key] = {'up': bool(up), 'flip_days': int(n), 'tf': tf, 'bar': ds[-1].isoformat(),
                    'ratio': round(r[-1], 6), 'ema': [fa, sl], 'prev_week': prev_week_of(ds, sides, MIN_BARS)}
    return res, errs


def _download(symbols, adjust=False):
    import yfinance as yf
    # adjust=False = ราคาปิดดิบ (เหมือน TradingView) · adjust=True = total-return-adjusted (RM1 · ACWI/BIL/HYG/IEI)
    df = yf.download(symbols, period='6y', interval='1d', auto_adjust=bool(adjust),
                     progress=False, group_by='column', threads=False)
    close = df['Close']
    out = {}
    for s in symbols:
        if s not in close: continue
        ser = close[s].dropna()
        if len(ser): out[s] = {ix.date(): float(v) for ix, v in ser.items()}
    return out


def fetch(symbols, dl=None, sleep=None, wait=20):
    """ดึงราคา · ถ้ามี symbol ขาด → รอ wait วินาที แล้วลองใหม่ 1 ครั้งเฉพาะตัวที่ขาด"""
    import time
    dl = dl or _download
    sleep = sleep or time.sleep
    out = dl(symbols)
    miss = [s for s in symbols if s not in out]
    if miss:
        print('⚠ ขาด', ','.join(miss), f'— รอ {wait}s แล้วลองใหม่ 1 ครั้ง')
        sleep(wait)
        out.update(dl(miss))
    return out


FAR = datetime.datetime(2035, 1, 1, tzinfo=datetime.timezone.utc)   # selftest: ไม่ตัดแท่งไหนทิ้ง


def selftest():
    D = datetime.date
    base = D(2020, 1, 1)
    ds = [base + datetime.timedelta(days=i) for i in range(1500) if (base + datetime.timedelta(days=i)).weekday() < 5]
    up = {d: 100 + i * 0.1 for i, d in enumerate(ds)}             # ขึ้นตลอด
    dn = {d: 100 - i * 0.01 for i, d in enumerate(ds)}            # ลงตลอด
    one = {d: 1.0 for d in ds}
    # ขึ้นแล้วกลับลง 3 วันท้าย (ไม่คร่อมสัปดาห์)
    turn = {d: (100 + i * 0.1 if i < len(ds) - 3 else 100 + (len(ds) - 3) * 0.1 - (i - len(ds) + 4) * 20) for i, d in enumerate(ds)}
    p = {'HYG': dn, 'IEF': one, 'HG=F': up, 'GC=F': one, 'SPHB': turn, 'SPLV': one, 'RSP': up, 'SPY': one}
    # adjusted legs: ราคาต่างจากดิบโดยตั้งใจ (x2) เพื่อพิสูจน์ว่าไม่ได้อ่านดิบ
    ad = {'ACWI': {d: v * 2 for d, v in up.items()}, 'BIL': {d: 2.0 for d in ds},
          'HYG': {d: v * 2 for d, v in dn.items()}, 'IEI': {d: 2.0 for d in ds}}
    r, e = compute(p, ad, FAR)
    assert not e, e
    assert len(r) == len(RATIOS)

    # --- สูตร SMA: คำนวณมือ ---
    asc = [float(i) for i in range(1, 51)]                         # 1..50 → SMA20 = mean(31..50) = 40.5 · SMA50 = 25.5
    assert sma(asc, 20) == 40.5 and sma(asc, 50) == 25.5
    assert sma_states(asc)[-1] == 'green'
    des = asc[::-1]                                                # 50..1 → SMA20 = 10.5 · SMA50 = 25.5
    assert sma(des, 20) == 10.5 and sma_states(des)[-1] == 'red'
    # เท่ากัน → state ก่อนหน้า: 1..50 แล้ว x=-449 → SMA20 = 330/20 = 16.5 = SMA50 = 825/50
    eq = asc + [-449.0]
    assert sma(eq, 20) == 16.5 and sma(eq, 50) == 16.5
    assert sma_states(eq)[-2:] == ['green', 'green']
    # เท่ากันและไม่มี state ก่อนหน้า → neutral (ratio คงที่ 50 แท่ง)
    assert sma_states([1.0] * 50)[-1] == 'neutral'
    # days_in_state ผ่าน sma_item: 1..50 แล้ว -449 → green 2 วัน
    d50 = [D(2025, 1, 6) + datetime.timedelta(days=i) for i in range(51)]
    it, _ = sma_item('X', 'Y', dict(zip(d50, eq)), dict.fromkeys(d50, 1.0))
    assert it['state'] == 'green' and it['days_in_state'] == 2 and it['sma20'] == 16.5 and it['sma50'] == 16.5, it
    it, _ = sma_item('X', 'Y', dict(zip(d50[:50], asc)), dict.fromkeys(d50, 1.0))
    assert it['state'] == 'green' and it['days_in_state'] == 1 and it['sma20'] == 40.5 and it['sma50'] == 25.5, it
    it, _ = sma_item('X', 'Y', dict(zip(d50[:50], des)), dict.fromkeys(d50, 1.0))
    assert it['state'] == 'red' and it['up'] is False
    it, _ = sma_item('X', 'Y', dict.fromkeys(d50[:50], 3.0), dict.fromkeys(d50, 1.0))
    assert it['state'] == 'neutral' and it['up'] is None and it['days_in_state'] == 1

    # --- 49 vs 50 แท่ง ---
    it49, er = sma_item('X', 'Y', dict(zip(d50[:49], asc[:49])), dict.fromkeys(d50, 1.0))
    assert it49['state'] == 'unavailable' and it49['up'] is None and it49['sma20'] is None and 'ข้อมูลไม่พอ' in er
    it50, er = sma_item('X', 'Y', dict(zip(d50[:50], asc)), dict.fromkeys(d50, 1.0))
    assert it50['state'] == 'green' and er is None

    # --- item ของ ratio ทั้งสอง (ราคา adjusted x2 ต้องเท่ากับ ratio ของ raw เพราะหารกัน) ---
    for k in SMA_KEYS:
        v = r[k]
        assert v['sma'] == [20, 50] and v['adj'] is True and v['tf'] == 'D', v
        assert 'slow' not in v and 'ema' not in v, v
        assert set(v['inputs_asof']) == set(RATIOS[k][:2]) and v['bar'] == ds[-1].isoformat()
        assert v['prev_week'] is not None and v['prev_week']['bar'] < v['bar']
    a = r['ACWI_BIL']
    assert a['state'] == 'green' and a['up'] is True and a['days_in_state'] > 50 and a['prev_week']['up'] is True
    assert abs(a['ratio'] - round(up[ds[-1]] * 2 / 2.0, 6)) < 1e-6          # adjusted ÷ adjusted
    assert r['HYG_IEI']['state'] == 'red' and r['HYG_IEI']['up'] is False
    assert a['inputs_asof'] == {'ACWI': ds[-1].isoformat(), 'BIL': ds[-1].isoformat()}
    for k in ('HYG_IEF', 'HG_GC', 'SPHB_SPLV', 'RSP_SPY'): assert 'slow' not in r[k] and 'sma' not in r[k] and r[k]['ema']
    assert r['HYG_IEF']['up'] is False and r['HYG_IEF']['tf'] == 'W' and r['HYG_IEF']['ema'] == [10, 20]

    # --- ขาดขา → unavailable (ratio อื่นไม่กระทบ) ---
    r2, e2 = compute(p, {k: v for k, v in ad.items() if k != 'BIL'}, FAR)
    assert r2['ACWI_BIL']['state'] == 'unavailable' and r2['ACWI_BIL']['up'] is None and r2['HYG_IEI']['state'] == 'red'
    assert any('ACWI_BIL' in x for x in e2), e2
    # --- adjusted เท่านั้น: มีราคาดิบครบแต่ไม่มี adjusted → unavailable (ห้าม fall back) ---
    raw_all = dict(p, ACWI=up, BIL=one, IEI=one)
    r3, e3 = compute(raw_all, {}, FAR)
    assert r3['ACWI_BIL']['state'] == 'unavailable' and r3['HYG_IEI']['state'] == 'unavailable', r3
    # --- ขาข้างหนึ่งหยุดก่อน (คนละวันล่าสุด) → bar = วันร่วมล่าสุด · inputs_asof แยกต่อขา ---
    shorter = {d: v for d, v in ad['BIL'].items() if d != ds[-1]}
    r4, _ = compute(p, dict(ad, BIL=shorter), FAR)
    assert r4['ACWI_BIL']['bar'] == ds[-2].isoformat() and r4['ACWI_BIL']['inputs_asof'] == {'ACWI': ds[-1].isoformat(), 'BIL': ds[-2].isoformat()}

    # --- แท่งยังไม่ปิด: ก่อน 16:15 NY ตัดแท่งวันนั้น · หลัง 16:15 เก็บ ---
    from zoneinfo import ZoneInfo
    NY = ZoneInfo('America/New_York')
    day = ds[-1]
    at = lambda h, m: datetime.datetime(day.year, day.month, day.day, h, m, tzinfo=NY).astimezone(datetime.timezone.utc)
    assert max(drop_partial(up, at(15, 0))) == ds[-2]
    assert max(drop_partial(up, at(16, 14))) == ds[-2]
    assert max(drop_partial(up, at(16, 15))) == ds[-1]
    assert max(drop_partial(up, at(23, 0))) == ds[-1]
    nxt = datetime.datetime.combine(day + datetime.timedelta(days=1), datetime.time(3, 0), tzinfo=NY).astimezone(datetime.timezone.utc)
    assert max(drop_partial(up, nxt)) == ds[-1]                      # วันรุ่งขึ้น: แท่งเดิมปิดแล้ว
    r5, _ = compute(p, ad, at(10, 0))
    assert r5['ACWI_BIL']['bar'] == ds[-2].isoformat() and r5['ACWI_BIL']['inputs_asof']['ACWI'] == ds[-2].isoformat()
    # ratio ที่ไม่ใช่ SMA ไม่ถูกตัดแท่ง
    assert r5['HYG_IEF']['bar'] == r['HYG_IEF']['bar']

    # --- ratio อื่นเดิม (EMA) ---
    assert r['SPHB_SPLV']['up'] is False and 1 <= r['SPHB_SPLV']['flip_days'] <= 5, r['SPHB_SPLV']
    wk = weekly_last(ds[:10], list(range(10)))
    assert [x[1] for x in wk] == [2, 7, 9], wk          # 2020-01-01 = พุธ → สัปดาห์แรกมี 3 วัน (พ-ศ)
    for k, v in r.items():
        pw = v['prev_week']
        assert pw is not None and pw['bar'] < v['bar'], (k, v)
    sp = r['SPHB_SPLV']
    assert sp['up'] is False and sp['prev_week']['up'] is True, sp
    wds, _ = ratio_series(up, one)
    wkd = [x[0] for x in weekly_last(wds, [0] * len(wds))]
    assert r['ACWI_BIL']['prev_week']['bar'] == wkd[-2].isoformat(), (r['ACWI_BIL'], wkd[-2:])
    assert datetime.date.fromisoformat(sp['prev_week']['bar']).isocalendar()[:2] < datetime.date.fromisoformat(sp['bar']).isocalendar()[:2]
    # ข้อมูลสั้น: prev ไม่ถึง MIN_BARS → None แต่ค่าปัจจุบันยังออก (W: 60 แท่งพอดี → prev มี 59)
    short = [ds[0] + datetime.timedelta(days=7 * i) for i in range(MIN_BARS)]
    rs, es = compute({'HYG': dict(zip(short, [100 + i for i in range(MIN_BARS)])), 'IEF': dict.fromkeys(short, 1.0)}, {}, FAR)
    assert 'HYG_IEF' in rs and rs['HYG_IEF']['prev_week'] is None and rs['HYG_IEF']['up'] is True, rs
    # retry: symbol ขาดรอบแรก → รอ 20s แล้วดึงซ้ำเฉพาะตัวที่ขาด 1 ครั้ง
    calls, slept = [], []
    def fake(syms):
        calls.append(list(syms))
        return {x: {} for x in syms if not (len(calls) == 1 and x == 'BIL')}
    got = fetch(['ACWI', 'BIL', 'HYG'], dl=fake, sleep=slept.append)
    assert calls == [['ACWI', 'BIL', 'HYG'], ['BIL']] and slept == [20] and set(got) == {'ACWI', 'BIL', 'HYG'}, (calls, slept)
    calls.clear(); slept.clear()
    fetch(['ACWI'], dl=fake, sleep=slept.append)
    assert calls == [['ACWI']] and slept == [], 'ไม่ขาด → ไม่ retry'
    assert ADJ_SYMS == ['ACWI', 'BIL', 'HYG', 'IEI'] and 'ACWI' not in RAW_SYMS and 'IEI' not in RAW_SYMS
    print('selftest OK', json.dumps(r, default=str)[:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fundflow.json'))
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: return selftest()

    prices = fetch(RAW_SYMS)                                           # ราคาดิบ: ratio อื่น
    adj = fetch(ADJ_SYMS, dl=lambda s: _download(s, adjust=True))      # adjusted: ACWI_BIL / HYG_IEI เท่านั้น
    ratios, errs = compute(prices, adj)
    for x in errs: print('⚠', x)
    if len(ratios) < len(RATIOS):
        # ratio ปกติขาด = ไม่เขียนทับไฟล์เดิม — หน้าจอจะขึ้น "ข้อมูลเก่า" เอง
        print(f'✗ ได้ไม่ครบ {len(RATIOS)} ratio — ไม่เขียนไฟล์'); sys.exit(1)
    if all(ratios[k]['state'] == 'unavailable' for k in SMA_KEYS) and not any(adj.values()):
        # ดึง adjusted ไม่ได้เลย (ถูกบล็อก/rate limit) = ไม่เขียนทับไฟล์เดิมด้วย unavailable ทั้งคู่
        print('✗ ไม่ได้ราคา adjusted สักตัว — ไม่เขียนไฟล์'); sys.exit(1)
    as_of = max(v['bar'] for v in ratios.values() if v.get('bar'))
    doc = {'as_of': as_of,
           'generated_at': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
           'ver': VER,
           'method': 'ACWI_BIL & HYG_IEI = SMA 20/50 of the ratio (adjusted closes, yfinance auto_adjust=True, completed US sessions only) · others raw closes EMA10/20 · W = ISO week (current week incl.) · prev_week = last bar of previous ISO week · source yfinance',
           'ratios': ratios}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print('✓ เขียน', a.out, json.dumps(doc, ensure_ascii=False)[:400])


if __name__ == '__main__':
    main()
