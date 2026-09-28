#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_fundflow.py — คำนวณ 6 ratio ของแถบ Regime แล้วเขียน fundflow.json (เฟส 4 · งาน P1)

หน้า index.html อ่านไฟล์นี้แบบ relative ('fundflow.json') จึงต้องวางไว้ที่ราก repo เดียวกับ index.html
รันโดย GitHub Actions หลังตลาด US ปิด (.github/workflows/fundflow.yml) — ไม่ใช้ LLM ไม่ใช้ secret

ต่อ ratio: EMA10 vs EMA20 ของ (ตัวตั้ง / ตัวหาร)
  up         = EMA10 > EMA20 ที่แท่งล่าสุด
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
    # key          ตัวตั้ง   ตัวหาร   TF
    'ACWI_BIL':  ('ACWI',  'BIL',  'W'),
    'HYG_IEF':   ('HYG',   'IEF',  'W'),
    'HYG_IEI':   ('HYG',   'IEI',  'W'),   # เพิ่มใหม่ — คู่กับ HYG_IEF (แอปยังอ่าน key เดิม)
    'HG_GC':     ('HG=F',  'GC=F', 'W'),   # front-month continuous — ต่างจาก HG1!/GC1! ของ TV เล็กน้อยช่วง roll (ยอมรับแล้ว)
    'SPHB_SPLV': ('SPHB',  'SPLV', 'D'),
    'RSP_SPY':   ('RSP',   'SPY',  'D'),
}
FAST, SLOW = 10, 20
MIN_BARS = 60          # น้อยกว่านี้ EMA ยังไม่นิ่ง → ไม่เขียนค่า ratio นั้น


def ema(vals, span):
    k = 2.0 / (span + 1.0)
    out, e = [], None
    for v in vals:
        e = v if e is None else (v - e) * k + e
        out.append(e)
    return out


def state_of(vals):
    """คืน (up, flip_days, sides) จากลำดับค่า ratio (เก่า→ใหม่) — sides = up ของทุกแท่ง"""
    f, s = ema(vals, FAST), ema(vals, SLOW)
    sides = [a > b for a, b in zip(f, s)]
    up = sides[-1]
    n = 0
    for x in reversed(sides):
        if x != up: break
        n += 1
    return up, n, sides


def prev_week_of(ds, sides):
    """แท่งสุดท้ายในสัปดาห์ ISO ก่อนสัปดาห์ของแท่งล่าสุด → {'up','bar'} หรือ None"""
    last = ds[-1].isocalendar()[:2]
    for i in range(len(ds) - 2, -1, -1):
        if ds[i].isocalendar()[:2] < last:
            if i + 1 < MIN_BARS: return None
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


def compute(prices):
    """prices = {symbol: {date: close}} → dict ratios สำหรับ JSON"""
    res, errs = {}, []
    for key, (num, den, tf) in RATIOS.items():
        if num not in prices or den not in prices:
            errs.append(f'{key}: ไม่มีราคา {num if num not in prices else den}'); continue
        ds, r = ratio_series(prices[num], prices[den])
        if tf == 'W':
            wk = weekly_last(ds, r)
            ds, r = [x[0] for x in wk], [x[1] for x in wk]
        if len(r) < MIN_BARS:
            errs.append(f'{key}: ข้อมูลไม่พอ ({len(r)} แท่ง)'); continue
        up, n, sides = state_of(r)
        res[key] = {'up': bool(up), 'flip_days': int(n), 'tf': tf, 'bar': ds[-1].isoformat(),
                    'ratio': round(r[-1], 6), 'prev_week': prev_week_of(ds, sides)}
    return res, errs


def fetch(symbols):
    import yfinance as yf
    df = yf.download(symbols, period='6y', interval='1d', auto_adjust=True,
                     progress=False, group_by='column', threads=True)
    close = df['Close']
    out = {}
    for s in symbols:
        if s not in close: continue
        ser = close[s].dropna()
        if len(ser): out[s] = {ix.date(): float(v) for ix, v in ser.items()}
    return out


def selftest():
    base = datetime.date(2020, 1, 1)
    ds = [base + datetime.timedelta(days=i) for i in range(1500) if (base + datetime.timedelta(days=i)).weekday() < 5]
    up = {d: 100 + i * 0.1 for i, d in enumerate(ds)}             # ขึ้นตลอด
    dn = {d: 100 - i * 0.01 for i, d in enumerate(ds)}            # ลงตลอด
    one = {d: 1.0 for d in ds}
    # ขึ้นแล้วกลับลง 3 วันท้าย (แท่งล่าสุดคือพฤหัส → 3 วันท้ายอยู่ในสัปดาห์ล่าสุดทั้งหมด ไม่คร่อมสัปดาห์)
    turn = {d: (100 + i * 0.1 if i < len(ds) - 3 else 100 + (len(ds) - 3) * 0.1 - (i - len(ds) + 4) * 20) for i, d in enumerate(ds)}
    p = {'ACWI': up, 'BIL': one, 'HYG': dn, 'IEF': one, 'IEI': one, 'HG=F': up, 'GC=F': one,
         'SPHB': turn, 'SPLV': one, 'RSP': up, 'SPY': one}
    r, e = compute(p)
    assert not e, e
    assert r['ACWI_BIL']['up'] and r['ACWI_BIL']['tf'] == 'W'
    assert r['HYG_IEF']['up'] is False
    assert 'HYG_IEI' in r and r['HYG_IEI']['up'] is False and r['HYG_IEI']['tf'] == 'W', r.get('HYG_IEI')
    assert len(r) == len(RATIOS)
    assert r['SPHB_SPLV']['up'] is False and 1 <= r['SPHB_SPLV']['flip_days'] <= 5, r['SPHB_SPLV']
    assert r['ACWI_BIL']['flip_days'] > 50
    wk = weekly_last(ds[:10], list(range(10)))
    assert [x[1] for x in wk] == [2, 7, 9], wk          # 2020-01-01 = พุธ → สัปดาห์แรกมี 3 วัน (พ-ศ)
    for k, v in r.items():
        pw = v['prev_week']
        assert pw is not None and pw['bar'] < v['bar'], (k, v)
    assert r['ACWI_BIL']['prev_week']['up'] is True
    sp = r['SPHB_SPLV']
    assert sp['up'] is False and sp['prev_week']['up'] is True, sp
    # weekly: prev_week.bar = แท่งก่อนแท่งล่าสุด 1 แท่งพอดี
    wds, _ = ratio_series(p['ACWI'], p['BIL'])
    wkd = [x[0] for x in weekly_last(wds, [0] * len(wds))]
    assert r['ACWI_BIL']['prev_week']['bar'] == wkd[-2].isoformat(), (r['ACWI_BIL'], wkd[-2:])
    # daily: prev_week.bar = วันสุดท้ายของสัปดาห์ ISO ก่อนหน้า
    assert datetime.date.fromisoformat(sp['prev_week']['bar']).isocalendar()[:2] < datetime.date.fromisoformat(sp['bar']).isocalendar()[:2]
    # ข้อมูลสั้น: prev ไม่ถึง MIN_BARS → None แต่ค่าปัจจุบันยังออก (W: 60 แท่งพอดี → prev มี 59)
    short = [ds[0] + datetime.timedelta(days=7 * i) for i in range(MIN_BARS)]
    rs, es = compute({'ACWI': dict(zip(short, [100 + i for i in range(MIN_BARS)])), 'BIL': dict.fromkeys(short, 1.0)})
    assert 'ACWI_BIL' in rs and rs['ACWI_BIL']['prev_week'] is None and rs['ACWI_BIL']['up'] is True, rs
    print('selftest OK', json.dumps(r, default=str)[:300])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fundflow.json'))
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest: return selftest()

    syms = sorted({s for n, d, _ in RATIOS.values() for s in (n, d)})
    prices = fetch(syms)
    ratios, errs = compute(prices)
    for x in errs: print('⚠', x)
    if len(ratios) < len(RATIOS):
        # ไม่ครบ = ไม่เขียนทับไฟล์เดิม — หน้าจอจะขึ้น "ข้อมูลเก่า" เองเมื่อ as_of เกิน 2 วันทำการ
        # (ดีกว่าเขียนไฟล์ขาด ratio แล้วเพดาน % คำนวณผิดเงียบ ๆ)
        print(f'✗ ได้ไม่ครบ {len(RATIOS)} ratio — ไม่เขียนไฟล์'); sys.exit(1)
    as_of = max(v['bar'] for v in ratios.values())
    doc = {'as_of': as_of,
           'generated_at': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
           'method': f'EMA{FAST}/EMA{SLOW} of ratio · W = ISO week (current week incl.) · prev_week = last bar of previous ISO week · source yfinance',
           'ratios': ratios}
    with open(a.out, 'w', encoding='utf-8') as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print('✓ เขียน', a.out, json.dumps(doc, ensure_ascii=False)[:400])


if __name__ == '__main__':
    main()
