#!/usr/bin/env python3
"""RV1 B — does the DATA SOURCE change the Flow › RRG state?   (research only · no app change · no API key · nothing written but the two report files)

 1  raw (split-adjusted, what Twelve Data sends) vs dividend-adjusted closes (Yahoo 'Adj Close'): state / days / ratio / mom per symbol, D and W,
    today and across the last 5 years (% of days the state differs)
 2  unfinished daily bar: the app has no filter for a bar that is still trading — simulate it with Yahoo 1h bars (3 snapshots of the US session)
    and count how often the state on the partial bar differs from the state on the closed bar
 3  Twelve Data vs Yahoo last closes: only if --td-export FILE is given (a user export of the app's rrg rows); otherwise reported as "not run"
 4  benchmark sanity on real SPY: SPY vs itself, SPY × 1.01^n, quadrants reachable
 Also builds the per-symbol table (app rrgCompute on Yahoo raw closes vs tools/rrg_verify.py) → RV1-data.json, consumed by tools/rrg_report.py

  python3 scripts/rrg_data_check.py --out docs/reports/RV1-data      # needs: pip install yfinance pandas numpy · node
  python3 scripts/rrg_data_check.py --selftest                       # offline: synthetic prices, same pipeline
Run by .github/workflows/rrg-data-check.yml (workflow_dispatch) because Yahoo rate-limits the Mac."""
import argparse, datetime as dt, json, math, os, subprocess, sys, tempfile
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import rrg_verify as V

SYMS, BENCH = V.SYMS, 'SPY'
EXTRA = ['ARTY']   # not in RRG_SYMS: candidate replacement for IRBO (finding 6) — checked, never used by the app
HIGH_YIELD = ['XLU', 'XLRE', 'XLP', 'XLE', 'KRE', 'XLF']
SNAPS = [('10:30', '≈ 11:30 ET · 23:30 ICT'), ('12:30', '≈ 13:30 ET · 01:30 ICT'), ('14:30', '≈ 15:30 ET · 03:30 ICT')]
EVAL_YEARS = 5


# ------------------------------------------------------------------ providers
def yahoo_daily(years=EVAL_YEARS + 2):
    import yfinance as yf
    raw = yf.download(SYMS + EXTRA + [BENCH], period=f'{years}y', interval='1d', auto_adjust=False, group_by='ticker', progress=False, threads=False)
    out = {}
    for s in SYMS + EXTRA + [BENCH]:
        try:
            d = raw[s][['Close', 'Adj Close']].dropna()
            if d.empty: print('no data', s, '(empty)'); continue
            d.index = [x.strftime('%Y-%m-%d') for x in d.index]
            out[s] = d
        except Exception as e: print('no data', s, e)
    return out


def yahoo_hourly():
    import yfinance as yf
    raw = yf.download(SYMS + EXTRA + [BENCH], period='730d', interval='1h', auto_adjust=False, group_by='ticker', progress=False, threads=False)
    out = {}
    for s in SYMS + EXTRA + [BENCH]:
        try:
            d = raw[s][['Close']].dropna()
            if d.empty: continue
            idx = d.index.tz_convert('America/New_York') if d.index.tz else d.index
            d = d.copy(); d['date'] = [x.strftime('%Y-%m-%d') for x in idx]; d['hm'] = [x.strftime('%H:%M') for x in idx]; out[s] = d
        except Exception as e: print('no hourly', s, e)
    return out


def synth(years, syms):
    """offline stand-in: raw closes + dividend-adjusted closes (a dividend every ~63 sessions, yield by symbol) + hourly snapshots"""
    rng = np.random.default_rng(7); n = int(252 * years); ds = V.sessions('2026-11-13', n)
    spy = V.walk(rng, n, 0.0095, 0.0003, 400); daily, hourly = {}, {}
    def mk(c, y):
        adj = c.copy(); f = 1.0
        for i in range(n - 1, -1, -1):
            adj[i] = c[i] * f
            if i % 63 == 0 and i: f *= (1 - y / 4)
        return pd.DataFrame({'Close': c, 'Adj Close': adj}, index=ds)
    daily[BENCH] = mk(spy, 0.013)
    for j, s in enumerate(syms): daily[s] = mk(V.walk(rng, n, 0.011, 0.0, 60) * (spy / spy[0]) ** 0.8, 0.01 + 0.004 * (j % 4))
    for s, d in daily.items():
        rows = []
        for i, day in enumerate(ds[-300:]):
            c = d['Close'].iloc[-300 + i]
            for hm in ('10:30', '12:30', '14:30'): rows.append((day, hm, c * (1 + rng.normal(0, 0.004))))
        hourly[s] = pd.DataFrame({'date': [r[0] for r in rows], 'hm': [r[1] for r in rows], 'Close': [r[2] for r in rows]})
    return daily, hourly


# ------------------------------------------------------------------ rolling state (same maths as rrg_verify.compute, prefix-invariant parts hoisted)
def prep(close, bench, tf):
    p = V.TF[tf]; rs = np.asarray(close, float) / np.asarray(bench, float)
    f, s = V.ema(rs, V.FAST), V.ema(rs, V.SLOW); raw = 100 * (f - s) / s
    mom = np.zeros(len(raw)); mom[p['lag']:] = raw[p['lag']:] - raw[:-p['lag']]
    return raw, mom


def state_at(raw, mom, i, tf):
    p = V.TF[tf]; w = p['win']
    if i + 1 < V.SLOW + w + p['lag']: return None
    rw, mw = raw[i - w + 1:i + 1], mom[i - w + 1:i + 1]; sr, sm = V.popsd(rw), V.popsd(mw)
    if not (sr > 0 and sm > 0): return None
    st = V.states(raw[:i + 1].tolist(), mom[:i + 1].tolist(), max(V.SLOW, p['lag']), V.K * sr, V.K * sm)
    q = st[-1]; days = 1
    for k in range(len(st) - 2, -1, -1):
        if st[k] != q: break
        days += 1
    return {'quad': q, 'days': days, 'ratio': 100 + (raw[i] - rw.mean()) / sr, 'mom': 100 + (mom[i] - mw.mean()) / sm}


def weekly_arrays(dates, close, bench):
    d = pd.to_datetime(pd.Series(dates)); wk = (d - pd.to_timedelta(d.dt.day_of_week, unit='D')).dt.strftime('%Y-%m-%d')
    g = pd.DataFrame({'wk': wk, 'obs': dates, 'c': close, 'b': bench}).groupby('wk', sort=True).agg(c=('c', 'last'), b=('b', 'last'), obs=('obs', 'last'))
    return g['obs'].tolist(), g['c'].to_numpy(), g['b'].to_numpy()


REL = {'lead': 'out', 'weak': 'out', 'imp': 'under', 'lag': 'under', 'flat': 'neutral'}


def history(dates, c_raw, c_adj, bench_raw, bench_adj, tf, window_days):
    """per eval bar: state on raw vs adjusted. Returns dict of rates"""
    if len(dates) == 0: return {'n': 0, 'diff_pct': None, 'rel_diff_pct': None, 'mean_abs_dratio': None, 'mean_abs_dmom': None, 'raw_flip_pct': 0.0}
    if tf == 'W':
        wd, cr, br = weekly_arrays(dates, c_raw, bench_raw); _, ca, ba = weekly_arrays(dates, c_adj, bench_adj); idx = [i for i, x in enumerate(wd) if x >= window_days]
        # the last week may be unfinished — keep only closed weeks
        if dt.date.fromisoformat(dates[-1]).weekday() != 4 and idx and idx[-1] == len(wd) - 1: idx = idx[:-1]
    else: cr, br, ca, ba = np.asarray(c_raw), np.asarray(bench_raw), np.asarray(c_adj), np.asarray(bench_adj); idx = [i for i, x in enumerate(dates) if x >= window_days]
    Rr, Mr = prep(cr, br, tf); Ra, Ma = prep(ca, ba, tf)
    n = diff = rdiff = 0; dr = []; dm = []; prev = None; flips = 0
    for i in idx:
        a, b = state_at(Rr, Mr, i, tf), state_at(Ra, Ma, i, tf)
        if not a or not b: continue
        n += 1; diff += a['quad'] != b['quad']; rdiff += REL[a['quad']] != REL[b['quad']]; dr.append(abs(a['ratio'] - b['ratio'])); dm.append(abs(a['mom'] - b['mom']))
        if prev is not None and prev != a['quad']: flips += 1
        prev = a['quad']
    return {'n': n, 'diff_pct': 100 * diff / n if n else None, 'rel_diff_pct': 100 * rdiff / n if n else None, 'mean_abs_dratio': float(np.mean(dr)) if dr else None, 'mean_abs_dmom': float(np.mean(dm)) if dm else None, 'raw_flip_pct': 100 * flips / max(n - 1, 1)}


def partial_sim(daily, hourly, sym, last_n):
    """state on a partial bar (last close replaced by an intraday snapshot) vs the closed bar, D every session, W on Fridays"""
    if sym not in hourly or BENCH not in hourly: return None
    e, b = daily[sym]['Close'], daily[BENCH]['Close']; dates = sorted(set(e.index) & set(b.index)); ce = e.loc[dates].to_numpy(); cb = b.loc[dates].to_numpy()
    he = hourly[sym]; hb = hourly[BENCH]; out = {hm: {'n': 0, 'D_diff': 0, 'D_rel': 0, 'nW': 0, 'W_diff': 0, 'W_rel': 0} for hm, _ in SNAPS}
    Rd, Md = prep(ce, cb, 'D'); wd, cw, bw = weekly_arrays(dates, ce, cb)
    Rw, Mw = prep(cw, bw, 'W'); wlast = {x: k for k, x in enumerate(wd)}
    pos = {d: i for i, d in enumerate(dates)}
    days = [d for d in dates if d in set(he['date']) and d in set(hb['date'])][-last_n:]
    for day in days:
        i = pos[day]; closed = state_at(Rd, Md, i, 'D')
        if not closed: continue
        for hm, _ in SNAPS:
            pe = he[(he['date'] == day) & (he['hm'] == hm)]['Close']; pb = hb[(hb['date'] == day) & (hb['hm'] == hm)]['Close']
            if pe.empty or pb.empty: continue
            ce2, cb2 = ce[:i + 1].copy(), cb[:i + 1].copy(); ce2[-1], cb2[-1] = pe.iloc[-1], pb.iloc[-1]
            R2, M2 = prep(ce2, cb2, 'D'); part = state_at(R2, M2, i, 'D')
            if not part: continue
            o = out[hm]; o['n'] += 1; o['D_diff'] += part['quad'] != closed['quad']; o['D_rel'] += REL[part['quad']] != REL[closed['quad']]
            if dt.date.fromisoformat(day).weekday() == 4:    # Friday: the app treats the weekly bar as complete (dow == 5) → classifies on the partial bar
                j = [k for k, x in enumerate(wd) if x == day][0]
                wc = state_at(Rw[:j + 1], Mw[:j + 1], j, 'W')
                cw2, bw2 = cw[:j + 1].copy(), bw[:j + 1].copy(); cw2[-1], bw2[-1] = pe.iloc[-1], pb.iloc[-1]
                R3, M3 = prep(cw2, bw2, 'W'); wp = state_at(R3, M3, j, 'W')
                if wc and wp: o['nW'] += 1; o['W_diff'] += wp['quad'] != wc['quad']; o['W_rel'] += REL[wp['quad']] != REL[wc['quad']]
    return out


# ------------------------------------------------------------------ pipeline
def td_cases(daily, ref, use='Close'):
    cases, bench = [], [{'datetime': d, 'close': '%.6f' % v, 'high': '%.6f' % v} for d, v in zip(daily[BENCH].index[::-1], daily[BENCH][use].to_numpy()[::-1])]
    for s in [k for k in daily if k != BENCH]:
        e = [{'datetime': d, 'close': '%.6f' % v, 'high': '%.6f' % v} for d, v in zip(daily[s].index[::-1], daily[s][use].to_numpy()[::-1])]
        cases.append({'id': s, 'sym': s, 'ref': ref, 'etf': e, 'bench': bench})
    return cases


def app_rows(cases):
    with tempfile.TemporaryDirectory() as d:
        cf = os.path.join(d, 'c.json'); json.dump(cases, open(cf, 'w'))
        return json.loads(subprocess.run(['node', os.path.join(ROOT, 'tools', 'rrg_app_run.js'), cf], capture_output=True, text=True, check=True).stdout)


def run(daily, hourly, ref, syms, partial_n, td_export=None):
    nodata = [s for s in syms if s not in daily or len(daily[s]) == 0]
    for s in nodata: print('no data', s, '— skipped')
    syms = [s for s in syms if s not in nodata]
    res = {'asof': ref, 'syms': syms, 'nodata': nodata, 'rows': {}, 'hist': {}, 'partial': {}, 'bench': {}, 'td': None}
    cases = td_cases({k: v for k, v in daily.items() if k in syms + [BENCH]}, ref)
    app = app_rows(cases); py = V.run(cases); bad = V.cmp(app, py); res['mismatches'] = [list(map(str, b)) for b in bad]
    adj_app = app_rows(td_cases({k: v for k, v in daily.items() if k in syms + [BENCH]}, ref, 'Adj Close'))
    for s in syms:
        res['rows'][s] = {'app': app['rows'][s], 'py': py['rows'][s], 'adj': adj_app['rows'][s]}
    start = (dt.date.fromisoformat(ref) - dt.timedelta(days=int(365.25 * EVAL_YEARS))).isoformat()
    for s in list(syms):
        e, b = daily[s], daily[BENCH]; dates = sorted(set(e.index) & set(b.index))
        if not dates: res['nodata'].append(s); res['syms'].remove(s); res['rows'].pop(s, None); print('no overlapping dates', s, '— skipped'); continue
        a = lambda df, c: df.loc[dates, c].to_numpy()
        res['hist'][s] = {tf: history(dates, a(e, 'Close'), a(e, 'Adj Close'), a(b, 'Close'), a(b, 'Adj Close'), tf, start) for tf in ('D', 'W')}
        p = partial_sim(daily, hourly, s, partial_n) if hourly else None
        if p: res['partial'][s] = p
        print('done', s, flush=True)
    # 4 · benchmark sanity on real SPY
    sp = daily[BENCH]['Close']; ds = list(sp.index); n = len(ds); mk = lambda arr: [{'datetime': d, 'close': '%.6f' % v, 'high': '%.6f' % v} for d, v in zip(ds[::-1], np.asarray(arr)[::-1])]
    sanity = [{'id': 'spy_vs_spy', 'sym': 'SPY', 'ref': ref, 'etf': mk(sp.to_numpy()), 'bench': mk(sp.to_numpy())},
              {'id': 'spy_x_1.01^n', 'sym': 'SYN', 'ref': ref, 'etf': mk(sp.to_numpy() * 1.01 ** np.arange(n)), 'bench': mk(sp.to_numpy())},
              {'id': 'spy_x_0.99^n', 'sym': 'SYN', 'ref': ref, 'etf': mk(sp.to_numpy() * 0.99 ** np.arange(n)), 'bench': mk(sp.to_numpy())}]
    sa = app_rows(sanity)['rows']; res['bench'] = {k: {'D': v['d'].get('err') or v['d']['quad'], 'W': v['w'].get('err') or v['w']['quad']} for k, v in sa.items()}
    if td_export and os.path.exists(td_export):
        rows = json.load(open(td_export)); rows = rows.get('rowsD', rows) if isinstance(rows, dict) else rows
        t = {}
        for r in rows:
            s, d, c = r.get('sym'), r.get('date'), r.get('close')
            if s in daily and d in daily[s].index and c: t[s] = {'date': d, 'td': c, 'yahoo_raw': float(daily[s].loc[d, 'Close']), 'diff_pct': 100 * (c / float(daily[s].loc[d, 'Close']) - 1)}
        res['td'] = t
    return res


def fmt(x, d=1): return '—' if x is None else f'{x:.{d}f}'


def md(res, out_md):
    L = [f"# RV1 B — data checks (generated {dt.date.today()} · as of {res['asof']})", '',
         'Closes: **raw** = Yahoo `Close` (split-adjusted only — same convention as Twelve Data) · **adj** = Yahoo `Adj Close` (dividend-adjusted). Window: last 5 years, state recomputed at every bar with only the data available at that bar.', '',
         '## B1 · Raw vs dividend-adjusted', '', '| Symbol | TF | state today raw | adj | days raw/adj | ratio raw/adj | mom raw/adj | % bars state differs (5y) | % bars Out/Under side differs | mean |Δratio| | flips/100 bars (raw) |', '|---|---|---|---|---|---|---|---|---|---|---|']
    for s in res['syms']:
        for tf, k in (('D', 'd'), ('W', 'w')):
            a, j, h = res['rows'][s]['app'][k], res['rows'][s]['adj'][k], res['hist'][s][tf]
            if 'err' in a or 'err' in j: L.append(f'| {s} | {tf} | {a.get("err", a.get("quad"))} | {j.get("err", j.get("quad"))} | | | | | | | |'); continue
            L.append(f"| {s}{' ★' if s in HIGH_YIELD else ''}{' (extra)' if s in EXTRA else ''} | {tf} | {a['quad']} | {j['quad']}{'' if a['quad'] == j['quad'] else ' ✗'} | {a['days']}/{j['days']} | {a['ratio']:.2f}/{j['ratio']:.2f} | {a['mom']:.2f}/{j['mom']:.2f} | {fmt(h['diff_pct'])} | {fmt(h['rel_diff_pct'])} | {fmt(h['mean_abs_dratio'], 2)} | {fmt(h['raw_flip_pct'])} |")
    if res.get('nodata'): L += ['', '**No data (skipped):** ' + ', '.join(res['nodata']) + ' — no rows from the provider (delisted / renamed ticker).']
    L += ['', '★ = high-yield ETFs expected to be most affected (XLU, XLRE, XLP, XLE, KRE, XLF).', '']
    for tf in ('D', 'W'):
        hy = [res['hist'][s][tf]['diff_pct'] for s in res['syms'] if s in HIGH_YIELD and res['hist'][s][tf]['diff_pct'] is not None]
        ot = [res['hist'][s][tf]['diff_pct'] for s in res['syms'] if s not in HIGH_YIELD and res['hist'][s][tf]['diff_pct'] is not None]
        if hy and ot: L.append(f'- {tf}: mean % of bars with a different state — high-yield group **{np.mean(hy):.1f} %** · other symbols **{np.mean(ot):.1f} %** · worst {max(hy + ot):.1f} %')
    L += ['', '## B2 · Unfinished daily bar', '',
          'Code path (index.html): `rrgFetchBatch` → Twelve Data `time_series?interval=1day` (no `end_date`/closed-bar filter) → `rrgSeries` keeps every row → `rrgBuildRows` → `rrgCompute(...)` classifies on the LAST row, whatever it is. `rrgBarsFresh` only checks the bar is ≤ 4 calendar days old (and ≥ −1), and `rrgCacheFresh` keeps a fetch for the rest of the ICT calendar day. The weekly path treats a Friday as a finished week (`dow === 5`), so a Friday partial bar is classified too.', '',
          'Simulation: the last daily close (ETF and SPY) is replaced by the Yahoo 1h price at three points of the US session; the state is compared with the state on the closed bar.', '',
          '| Snapshot (US session) | sessions | D: % state differs | D: % Out/Under side differs | Fridays | W: % state differs | W: % side differs |', '|---|---|---|---|---|---|---|']
    for hm, lab in SNAPS:
        n = dd = dr = nw = wd = wr = 0
        for s, p in res['partial'].items(): o = p[hm]; n += o['n']; dd += o['D_diff']; dr += o['D_rel']; nw += o['nW']; wd += o['W_diff']; wr += o['W_rel']
        L.append(f"| {hm} bar close · {lab} | {n} | {fmt(100 * dd / n) if n else '—'} | {fmt(100 * dr / n) if n else '—'} | {nw} | {fmt(100 * wd / nw) if nw else '—'} | {fmt(100 * wr / nw) if nw else '—'} |")
    L += ['', '(Counts pool all symbols. 03:30 ICT is ~30 min before the close, so it is the best case for the partial bar.)', '', '## B3 · Twelve Data vs Yahoo (last close)', '']
    if res['td']:
        L += ['| Symbol | date | Twelve Data | Yahoo raw | diff % |', '|---|---|---|---|---|'] + [f"| {s} | {v['date']} | {v['td']} | {v['yahoo_raw']:.4f} | {v['diff_pct']:+.3f} |" for s, v in res['td'].items()]
    else: L.append('Not run — needs a user export of the app’s stored RRG rows (`--td-export file.json`, rows with `sym`, `date`, `close`). Console snippet for the browser: `copy(JSON.stringify(ffState().rrg.rowsD.map(r=>({sym:r.sym,date:r.date,close:r.close}))))`. No key is involved.')
    L += ['', '## B4 · Benchmark sanity (real SPY, app code)', '', '| Case | D | W |', '|---|---|---|'] + [f'| {k} | {v["D"]} | {v["W"]} |' for k, v in res['bench'].items()]
    L += ['', f"## App vs independent on real closes: **{len(res['mismatches'])} mismatches**"] + [f'- {" ".join(m)}' for m in res['mismatches'][:20]]
    open(out_md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='docs/reports/RV1-data'); ap.add_argument('--selftest', action='store_true'); ap.add_argument('--td-export'); a = ap.parse_args()
    if a.selftest:
        syms = ['XLU', 'XLK', 'KRE']; daily, hourly = synth(3.2, syms); ref = daily[BENCH].index[-1]
        daily['DEAD'] = pd.DataFrame({'Close': [], 'Adj Close': []}, dtype=float)   # delisted ticker: empty frame, must be reported + skipped, not crash
        res = run(daily, hourly, ref, syms + ['DEAD', 'GONE'], 40)
        ok = res['nodata'] == ['DEAD', 'GONE'] and res['syms'] == syms and history([], [], [], [], [], 'W', '2020-01-01')['n'] == 0
        ok = ok and (not res['mismatches']) and all(res['hist'][s]['D']['n'] > 300 for s in syms) and res['partial'] and res['bench']['spy_vs_spy']['D'].startswith('คำนวณไม่ได้')
        md(res, os.path.join(tempfile.gettempdir(), 'rrg_selftest.md')); print('PASS rrg_data_check selftest' if ok else 'FAIL rrg_data_check selftest', res['mismatches'][:3], res['bench']); sys.exit(0 if ok else 1)
    daily = yahoo_daily(); hourly = yahoo_hourly(); ref = dt.date.today().isoformat()
    res = run(daily, hourly, ref, SYMS + EXTRA, 250, a.td_export)
    res['asof'] = daily[BENCH].index[-1]
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    json.dump(res, open(a.out + '.json', 'w'), separators=(',', ':')); md(res, a.out + '.md'); print('wrote', a.out + '.json/.md')
