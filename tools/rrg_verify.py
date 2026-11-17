#!/usr/bin/env python3
"""RV1 A — independent re-implementation of Flow › RRG (written from the formula in docs/briefs/RV1-brief.md, NOT from the JS).

  rs     = ETF / SPY on dates present in both
  raw    = 100 * (EMA12(rs) - EMA26(rs)) / EMA26(rs)            pandas ewm(span=n, adjust=False)
  momRaw = raw - raw[lag]      (D lag 5 · W lag 4)
  ratio  = 100 + z(raw, win)   mom = 100 + z(momRaw, win)       (D win 252 · W 52 · population SD)
  eps = 0.10*SD(raw, win)  delta = 0.10*SD(momRaw, win)         (SD of the last window, applied to the whole history)
  state  : sign of raw (|raw|<=eps -> neutral) x sign of momRaw (> delta -> up) with 'zero' hysteresis
           (leave pos/neg only when raw crosses 0; leave up/down only when momRaw crosses 0)
  Weekly : last close of each Mon-Sun week; an unfinished week (last session not Friday AND ref date before that Saturday) is dropped
           from the state and only previewed.

  python3 tools/rrg_verify.py gen  cases.json            # deterministic synthetic price set (23 symbols + edge cases)
  python3 tools/rrg_verify.py run  cases.json out.json   # this implementation
  python3 tools/rrg_verify.py diff app.json py.json      # compare (exit 1 on any mismatch)
"""
import datetime as dt, json, math, sys
import numpy as np, pandas as pd

K = 0.10
FAST, SLOW = 12, 26
TF = {'D': dict(win=252, lag=5), 'W': dict(win=52, lag=4)}
SYMS = ['XLU','PAVE','XHB','XLB','XLC','XBI','JETS','IGV','XRT','HACK','XLF','KRE','XLE','XLV','ITA','SMH','ARKX','IRBO','XLK','XLI','XLY','XLP','XLRE']


def ema(x, n): return pd.Series(x, dtype=float).ewm(span=n, adjust=False).mean().to_numpy()


def popsd(a): return float(np.sqrt(np.mean((a - np.mean(a)) ** 2)))


def states(raw, mom, start, eps, delta):
    """own state machine · returns list of 'lead|weak|imp|lag|flat'|None"""
    out, rel, up = [None] * len(raw), None, False
    for i in range(start, len(raw)):
        r, c = raw[i], mom[i]
        fresh = 'pos' if r > eps else 'neg' if r < -eps else 'neu'
        if rel is None:
            rel, up = fresh, c > delta
        else:
            if rel == 'neu': rel = fresh
            elif rel == 'pos' and r < 0: rel = fresh
            elif rel == 'neg' and r > 0: rel = fresh
            if up and c < 0: up = False
            elif (not up) and c > delta: up = True
        out[i] = 'flat' if rel == 'neu' else ('lead' if up else 'weak') if rel == 'pos' else ('imp' if up else 'lag')
    return out


def compute(close, bench, tf):
    p = TF[tf]; n = len(close); need = SLOW + p['win'] + p['lag']
    if n < need: return {'err': 'short'}
    rs = np.asarray(close, float) / np.asarray(bench, float)
    f, s = ema(rs, FAST), ema(rs, SLOW)
    raw = 100 * (f - s) / s
    mom = np.zeros(n); mom[p['lag']:] = raw[p['lag']:] - raw[:-p['lag']]
    w = p['win']
    rw, mw = raw[-w:], mom[-w:]
    sr, sm = popsd(rw), popsd(mw)
    if not (sr > 0 and sm > 0): return {'err': 'flat'}
    ratio = 100 + (raw[-1] - rw.mean()) / sr
    momz = 100 + (mom[-1] - mw.mean()) / sm
    eps, delta = K * sr, K * sm
    st = states(raw, mom, max(SLOW, p['lag']), eps, delta)
    cur = st[-1]
    runs = []                          # run-length encode the valid part
    for x in st:
        if x is None: continue
        if runs and runs[-1][0] == x: runs[-1][1] += 1
        else: runs.append([x, 1])
    days = runs[-1][1]; prev = runs[-2][1] if len(runs) > 1 else None
    return {'rsTrend': float(raw[-1]), 'rawChg': float(mom[-1]), 'ratio': float(ratio), 'mom': float(momz), 'eps': eps, 'delta': delta,
            'quad': cur, 'days': days, 'prevDays': prev}


def weekly(dates, close, bench, ref):
    d = pd.to_datetime(pd.Series(dates))
    wk = d - pd.to_timedelta(d.dt.day_of_week, unit='D')
    df = pd.DataFrame({'wk': wk.dt.strftime('%Y-%m-%d'), 'obs': dates, 'c': close, 'b': bench})
    g = df.groupby('wk', sort=True).agg(c=('c', 'last'), b=('b', 'last'), obs=('obs', 'last'))
    lastobs = g['obs'].iloc[-1]
    sat = (pd.Timestamp(g.index[-1]) + pd.Timedelta(days=5)).strftime('%Y-%m-%d')
    partial = dt.date.fromisoformat(lastobs).weekday() != 4 and (ref or lastobs) < sat
    return g, partial


def row(case):
    etf = {x['datetime']: float(x['close']) for x in case['etf'] if float(x['close']) > 0}
    ben = {x['datetime']: float(x['close']) for x in case['bench'] if float(x['close']) > 0}
    if not etf: return {'d': {'err': 'nodata'}, 'w': {'err': 'nodata'}}
    la, lb = max(etf), max(ben)
    if la != lb: return {'d': {'err': 'mismatch'}, 'w': {'err': 'mismatch'}}
    dates = sorted(set(etf) & set(ben))
    c = [etf[x] for x in dates]; b = [ben[x] for x in dates]
    d = compute(c, b, 'D'); d['date'] = dates[-1]
    g, partial = weekly(dates, c, b, case['ref'])
    m = len(g) - 1 if partial else len(g)
    w = compute(g['c'].to_numpy()[:m], g['b'].to_numpy()[:m], 'W'); w['date'] = g['obs'].iloc[m - 1]
    if partial and 'err' not in w:
        pv = compute(g['c'].to_numpy(), g['b'].to_numpy(), 'W')
        if 'err' not in pv: w['preview'] = {'asOf': g['obs'].iloc[-1], 'quad': pv['quad'], 'rsTrend': pv['rsTrend'], 'rawChg': pv['rawChg']}
    return {'d': d, 'w': w}


# ------------------------------------------------------------------ synthetic price set (deterministic)
HOL = {'2022-11-24','2022-12-26','2023-01-02','2023-01-16','2023-02-20','2023-04-07','2023-05-29','2023-06-19','2023-07-04','2023-09-04','2023-11-23','2023-12-25',
       '2024-01-01','2024-01-15','2024-02-19','2024-03-29','2024-05-27','2024-06-19','2024-07-04','2024-09-02','2024-11-28','2024-12-25',
       '2025-01-01','2025-01-20','2025-02-17','2025-04-18','2025-05-26','2025-06-19','2025-07-04','2025-09-01','2025-11-27','2025-12-25',
       '2026-01-01','2026-01-19','2026-02-16','2026-04-03','2026-05-25','2026-06-19','2026-07-03','2026-09-07','2026-11-26'}


def sessions(end, n):
    out, d = [], dt.date.fromisoformat(end)
    while len(out) < n:
        s = d.isoformat()
        if d.weekday() < 5 and s not in HOL: out.append(s)
        d -= dt.timedelta(days=1)
    return out[::-1]


def walk(rng, n, vol, drift=0.0, start=100.0):
    return start * np.exp(np.cumsum(rng.normal(drift, vol, n)))


def td(dates, closes):   # Twelve Data shape, newest first
    return [{'datetime': d, 'close': '%.6f' % c, 'high': '%.6f' % (c * 1.004)} for d, c in zip(dates[::-1], closes[::-1])]


def gen():
    rng = np.random.default_rng(20261117)
    cases = []
    def add(i, sym, ref, dates_e, ce, dates_b, cb): cases.append({'id': i, 'sym': sym, 'ref': ref, 'etf': td(dates_e, ce), 'bench': td(dates_b, cb)})
    N = 1200
    for end, ref, tag in (('2026-11-18', '2026-11-18', 'midweek'), ('2026-11-13', '2026-11-18', 'friday')):
        ds = sessions(end, N); spy = walk(rng, N, 0.0095, 0.0003, 400)
        for j, s in enumerate(SYMS):
            beta = 0.6 + 0.04 * j; e = walk(rng, N, 0.011 + 0.0004 * j, 0.0001 * ((j % 5) - 2), 50)
            c = e * (spy / spy[0]) ** beta                  # correlated with SPY, own trend
            add(f'{tag}:{s}', s, ref, ds, c, ds, spy)
        base = (ds, spy)
        if tag == 'midweek':
            # ---- edge cases on the same SPY path
            e0 = walk(rng, N, 0.012, 0.0, 80) * (spy / spy[0]) ** 0.9
            add('edge:spy_vs_itself', 'SPY', ref, ds, spy, ds, spy)
            add('edge:synthetic_up_1.01^n', 'SYN', ref, ds, spy * 1.01 ** np.arange(N), ds, spy)
            add('edge:flat_series', 'FLAT', ref, ds, spy * 2.0, ds, spy)
            i = N - 400; add('edge:missing_spy_day', 'X', ref, ds, e0, ds[:i] + ds[i + 1:], np.delete(spy, i))
            add('edge:missing_etf_day', 'X', ref, ds[:i] + ds[i + 1:], np.delete(e0, i), ds, spy)
            add('edge:mismatch_last_date', 'X', ref, ds[:-1], e0[:-1], ds, spy)
            add('edge:mismatch_last_date_bench_behind', 'X', ref, ds, e0, ds[:-1], spy[:-1])
            for n, nm in ((282, 'need_minus_1'), (283, 'need_exact'), (284, 'need_plus_1')):
                add(f'edge:D_{nm}', 'X', ref, ds[-n:], e0[-n:], ds[-n:], spy[-n:])
            add('edge:no_data', 'X', ref, [], [], ds, spy)
            # weekly exactly 82 complete Mon–Fri weeks (no holidays) ending Fri → W need exact; and 81
            wd = []; d = dt.date(2026, 11, 13)
            while len(wd) < 82 * 5:
                if d.weekday() < 5: wd.append(d.isoformat())
                d -= dt.timedelta(days=1)
            wd = wd[::-1]; sp2 = walk(rng, len(wd), 0.0095, 0.0003, 400); e2 = walk(rng, len(wd), 0.012, 0, 70) * (sp2 / sp2[0])
            add('edge:W_need_exact_82w', 'X', '2026-11-18', wd, e2, wd, sp2)
            add('edge:W_need_minus_1_81w', 'X', '2026-11-18', wd[5:], e2[5:], wd[5:], sp2[5:])
            # last week of 1,2,3,4 sessions (ref inside that week → partial)
            for k in (1, 2, 3, 4):
                full = sessions('2026-11-13', N); extra = ['2026-11-16', '2026-11-17', '2026-11-18', '2026-11-19'][:k]
                dd = full + extra; sp3 = walk(rng, len(dd), 0.0095, 0.0003, 400); e3 = walk(rng, len(dd), 0.012, 0, 70) * (sp3 / sp3[0]) ** 0.8
                add(f'edge:last_week_{k}_sessions_partial', 'X', extra[-1], dd, e3, dd, sp3)
            # holiday week ends Thursday (Thanksgiving week: Mon–Wed + Fri half-day is normal; test a week whose last session is Thursday and ref is after the week)
            dd = sessions('2026-11-25', N); sp4 = walk(rng, N, 0.0095, 0.0003, 400); e4 = walk(rng, N, 0.012, 0, 70) * (sp4 / sp4[0]) ** 0.8
            add('edge:holiday_week_ends_wed_ref_next_week', 'X', '2026-11-30', dd, e4, dd, sp4)
            add('edge:holiday_week_ends_wed_ref_same_week', 'X', '2026-11-25', dd, e4, dd, sp4)
            # hysteresis: rs oscillating around 1 with tiny amplitude (crosses ±eps repeatedly) and a noisy zero-drift rs
            osc = spy * (1 + 0.002 * np.sin(np.arange(N) / 3.0) + 0.0005 * rng.normal(size=N))
            add('edge:hysteresis_oscillating', 'X', ref, ds, osc, ds, spy)
            add('edge:hysteresis_noise_zero_drift', 'X', ref, ds, spy * np.exp(np.cumsum(rng.normal(0, 0.0015, N))), ds, spy)
            # quadrant reachability: sinusoidal rs (period 120 bars) — the phase is searched with THIS implementation, then the app is asked
            t = np.arange(N); want = {'lead', 'weak', 'imp', 'lag', 'flat'}
            for ph in np.linspace(0, 2 * math.pi, 720, endpoint=False):
                m = 1 + 0.05 * np.sin(2 * math.pi * t / 120 + ph)
                q = compute(spy * m, spy, 'D').get('quad')
                if q in want: want.discard(q); add(f'edge:quadrant_{q}', 'X', ref, ds, spy * m, ds, spy)
            # truly constant relative strength (rs = 1 exactly) and constant prices
            add('edge:rs_exactly_1', 'X', ref, ds, spy.copy(), ds, spy)
            add('edge:both_constant_100', 'X', ref, ds, np.full(N, 100.0), ds, np.full(N, 100.0))
    return cases


def run(cases): return {'meta': {'K': K}, 'rows': {c['id']: row(c) for c in cases}}


NUM = ('rsTrend', 'rawChg', 'ratio', 'mom', 'eps', 'delta')
ILL = ('edge:synthetic_up', 'edge:flat_series')   # raw is (almost) constant → SD ~1e-8: z-scores are ill-conditioned, float noise is amplified; state/days still must match, numbers to 1e-5
def cmp(app, py, tol0=1e-9):
    bad = []
    for cid, a in app['rows'].items():
        tol = 1e-5 if cid.startswith(ILL) else tol0
        for tf in ('d', 'w'):
            x, y = a[tf], py['rows'][cid][tf]
            if ('err' in x) != ('err' in y): bad.append((cid, tf, 'err', x.get('err'), y.get('err'))); continue
            if 'err' in x: continue
            if x['quad'] != y['quad']: bad.append((cid, tf, 'state', x['quad'], y['quad']))
            if x['days'] != y['days']: bad.append((cid, tf, 'days', x['days'], y['days']))
            if x.get('prevDays') != y.get('prevDays'): bad.append((cid, tf, 'prevDays', x.get('prevDays'), y.get('prevDays')))
            if x['date'] != y['date']: bad.append((cid, tf, 'date', x['date'], y['date']))
            for k in NUM:
                if abs(x[k] - y[k]) > tol * max(1, abs(y[k])): bad.append((cid, tf, k, x[k], y[k]))
            pa, pb = x.get('preview'), y.get('preview')
            if (pa is None) != (pb is None) or (pa and (pa['quad'] != pb['quad'] or pa['asOf'] != pb['asOf'] or abs(pa['rsTrend'] - pb['rsTrend']) > tol)): bad.append((cid, tf, 'preview', pa, pb))
    return bad


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == 'gen': json.dump(gen(), open(a[1], 'w'), separators=(',', ':')); print('cases:', len(gen()))
    elif a[0] == 'run': json.dump(run(json.load(open(a[1]))), open(a[2], 'w'), separators=(',', ':'))
    elif a[0] == 'diff':
        bad = cmp(json.load(open(a[1])), json.load(open(a[2])))
        for b in bad: print('MISMATCH', *b)
        print('compared; mismatches:', len(bad)); sys.exit(1 if bad else 0)
