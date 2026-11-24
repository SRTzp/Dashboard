#!/usr/bin/env python3
"""RR4 · daily bars (close + high) of the RRG ETFs + SPY → Firestore users/{uid}/rrg/bars
The app builds the Flow RRG tails from this doc (existing rrgCompute) when it is ≤ 1 trading day old — no Twelve Data call.
One doc: {v, asOf, bench, bars, dates:[…], syms:{XLU:{c:[…], h:[…]}, …}} · arrays are aligned to `dates` (null = no bar that day).
RRG_SYMS mirrors RRG_SYMS / RRG_BENCH in index.html — tests/rr4_selftest.py fails if they differ.
Pure functions (no network) + _yf_bars()."""
import datetime as dt

import us_sessions

RRG_BENCH = 'SPY'
RRG_SYMS = ['XLU', 'PAVE', 'XHB', 'XLB', 'XLC', 'XBI', 'JETS', 'IGV', 'XRT', 'HACK', 'XLF', 'KRE', 'XLE', 'XLV', 'ITA',
            'SMH', 'ARKX', 'ROBO', 'XLK', 'XLI', 'XLY', 'XLP', 'XLRE']
BARS = 800                  # sessions kept · weekly needs ~82 weeks (≈ 410 sessions) + EMA warm-up · ~330 KB, well under Firestore's 1 MB doc limit
DOC_LIMIT = 700_000         # bytes (JSON estimate) · over this → fewer bars
VER = 1


def clean(rows):
    """[(date, close, high)] → sorted [(iso, close, high)] · drops non-positive / NaN closes · a bad high falls back to the close"""
    out = {}
    for d, c, h in rows:
        if isinstance(d, dt.datetime):
            d = d.date()
        d = str(d)[:10]
        try:
            c = float(c)
        except (TypeError, ValueError):
            continue
        if not (c > 0) or c != c:
            continue
        try:
            h = float(h)
        except (TypeError, ValueError):
            h = c
        if not (h > 0) or h != h:
            h = c
        out[d] = (round(c, 4), round(h, 4))
    return [(d, v[0], v[1]) for d, v in sorted(out.items())]


def drop_partial(rows, now_utc):
    """a bar dated today (ET) before 16:15 ET is an intraday bar — never keep it"""
    et = now_utc.astimezone(us_sessions.ET)
    today = et.date().isoformat()
    if et.hour * 60 + et.minute < us_sessions.CLOSE_MIN:
        return [r for r in rows if r[0] < today]
    return rows


def build_doc(data, now_utc, bars=BARS):
    """data {sym: [(date, close, high)]} (SPY included) → doc dict, or None when SPY is missing / too short · symbols that failed are left out"""
    ser = {s: drop_partial(clean(r), now_utc) for s, r in data.items() if r is not None and len(r)}
    bench = ser.get(RRG_BENCH)
    if not bench or len(bench) < 60:
        return None
    dates = sorted({d for r in ser.values() for d, _c, _h in r})[-bars:]
    ix = {d: i for i, d in enumerate(dates)}
    syms = {}
    for s in [RRG_BENCH] + RRG_SYMS:
        r = ser.get(s)
        if not r:
            continue
        c, h = [None] * len(dates), [None] * len(dates)
        for d, cc, hh in r:
            i = ix.get(d)
            if i is not None:
                c[i], h[i] = cc, hh
        syms[s] = {'c': c, 'h': h}
    return {'v': VER, 'asOf': bench[-1][0], 'bench': RRG_BENCH, 'bars': len(dates), 'dates': dates, 'syms': syms,
            'missing': [s for s in RRG_SYMS if s not in syms]}


def doc_bytes(doc):
    import json
    return len(json.dumps(doc, separators=(',', ':')).encode('utf-8'))


def _yf_bars(syms, chunk=30):
    """yfinance daily OHLC (split-adjusted close, like Twelve Data's default) → {sym: [(date, close, high)]} · failed symbols have no key"""
    import yfinance as yf
    out = {}
    syms = list(syms)
    for i in range(0, len(syms), chunk):
        part = syms[i:i + chunk]
        try:
            df = yf.download(part, interval='1d', period='5y', auto_adjust=False, progress=False, group_by='column', threads=True)
            cl, hi = df['Close'], df['High']
        except Exception as ex:
            print('rrg bars chunk failed:', str(ex)[:100])
            continue
        if not hasattr(cl, 'columns'):
            cl, hi = cl.to_frame(part[0]), hi.to_frame(part[0])
        for y in part:
            if y in cl.columns:
                c = cl[y].dropna()
                if len(c):
                    out[y] = [(d, v, hi[y].get(d)) for d, v in c.items()]
    return out


def run(fetch, write, now_utc, bars=BARS):
    """fetch(syms) → {sym: [(date, close, high)]} · write(doc_id, data) · → doc or None (nothing written when SPY is missing)"""
    data = fetch([RRG_BENCH] + RRG_SYMS)
    doc = build_doc(data, now_utc, bars)
    if doc is None:
        print('rrg bars: SPY missing or too short — not written')
        return None
    while doc_bytes(doc) > DOC_LIMIT and doc['bars'] > 300:
        doc = build_doc(data, now_utc, doc['bars'] - 100)
    write('bars', doc)
    print('rrg bars: %d symbols · %d bars · asOf %s · %d KB%s' % (len(doc['syms']), doc['bars'], doc['asOf'], doc_bytes(doc) // 1024,
                                                                  ' · missing ' + ','.join(doc['missing']) if doc['missing'] else ''))
    return doc
