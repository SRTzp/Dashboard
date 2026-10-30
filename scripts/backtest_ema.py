#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backtest_ema.py — compare weekly EMA pairs for the Regime signal (ACWI/BIL · HYG/IEI)

Same method as build_fundflow.py (weekly bar = last close of each ISO week · up = EMA fast > EMA slow),
reusing its ema / weekly_last / ratio_series. Read-only: prints tables, writes nothing to the repo.

Variants: EMA10/20 (current) · EMA5/10 · EMA5/10 confirmed (new side must hold 2 weekly closes)
Per ratio:   flips per year · whipsaws (flip that reverses within 4 weeks) · % of weeks red
Drawdowns:   for every ACWI fall >= 15% (weekly closes): how far ACWI had already fallen when the
             signal first turned red, and how far ACWI had risen off the low when it turned green again
Sizing:      the app's Core factor (both green 100% · one red 75% · both red 50%) applied to ACWI,
             rest in BIL, signal from last week's close (no look-ahead) → CAGR · max drawdown · changes/yr

Run:       pip install yfinance && python3 scripts/backtest_ema.py
Offline:   python3 scripts/backtest_ema.py --selftest
"""
import argparse, datetime, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_fundflow import ema, weekly_last, ratio_series   # noqa: E402

# (label, fast, slow, confirm, timeframe, raw prices) — D = daily bars, state read at each weekly close
VARIANTS = [('EMA10/20 (now)', 10, 20, 1, 'W', False), ('EMA5/10', 5, 10, 1, 'W', False),
            ('EMA5/10 + 2wk confirm', 5, 10, 2, 'W', False), ('Daily EMA20/50 raw (Winner)', 20, 50, 1, 'D', True),
            ('Daily EMA50/100 raw (Ladder)', 50, 100, 1, 'D', True)]
PAIRS = [('ACWI/BIL', 'ACWI', 'BIL'), ('HYG/IEI', 'HYG', 'IEI')]
WARMUP = 30          # weekly bars skipped before scoring (EMA settling)
WHIPSAW = 4          # a flip that reverses within this many weeks counts as a whipsaw
DD_MIN = 0.15        # ACWI fall that counts as a major drawdown


def sides_of(vals, fast, slow, confirm):
    """True = green. With confirm=n the side only changes after n weekly closes on the new side."""
    f, s = ema(vals, fast), ema(vals, slow)
    raw = [a > b for a, b in zip(f, s)]
    out, cur, run = [], raw[0], 0
    for x in raw:
        if x == cur: run = 0
        else:
            run += 1
            if run >= confirm: cur, run = x, 0
        out.append(cur)
    return out


def flip_stats(sides, years, whip_bars=WHIPSAW):
    idx = [i for i in range(1, len(sides)) if sides[i] != sides[i - 1]]
    whip = sum(1 for a, b in zip(idx, idx[1:]) if b - a <= whip_bars)
    return {'flips_yr': len(idx) / years, 'whipsaws': whip, 'red_pct': 100.0 * sides.count(False) / len(sides)}


def drawdowns(px):
    """Episodes where px falls >= DD_MIN from a running peak → [(peak_i, trough_i, recover_i|None)]"""
    eps, peak_i, i, n = [], 0, 1, len(px)
    while i < n:
        if px[i] >= px[peak_i]: peak_i = i; i += 1; continue
        if px[i] <= px[peak_i] * (1 - DD_MIN):
            trough_i, j = i, i
            while j < n and px[j] < px[peak_i]:
                if px[j] < px[trough_i]: trough_i = j
                j += 1
            eps.append((peak_i, trough_i, j if j < n else None))
            peak_i, i = (j, j + 1) if j < n else (n - 1, n)
            continue
        i += 1
    return eps


def dd_rows(px, ds, sides):
    rows = []
    for p, t, r in drawdowns(px):
        red = next((k for k in range(p, t + 1) if not sides[k]), None)
        fell = (px[red] / px[p] - 1) * 100 if red is not None else None
        end = r if r is not None else len(px) - 1
        grn = next((k for k in range(t, end + 1) if sides[k]), None) if red is not None else None
        rose = (px[grn] / px[t] - 1) * 100 if grn is not None else None
        rows.append({'peak': ds[p], 'depth': (px[t] / px[p] - 1) * 100, 'fell_at_red': fell, 'rose_at_green': rose})
    return rows


def sizing(acwi, bil, s_acwi, s_hyg):
    """Weekly equity of the Core factor on ACWI (rest BIL); factor decided at the previous close."""
    eq, peak, mdd, chg, last = 1.0, 1.0, 0.0, 0, None
    for i in range(1, len(acwi)):
        reds = (not s_acwi[i - 1]) + (not s_hyg[i - 1])
        f = 1.0 if reds == 0 else (0.75 if reds == 1 else 0.5)
        if last is not None and f != last: chg += 1
        last = f
        eq *= 1 + f * (acwi[i] / acwi[i - 1] - 1) + (1 - f) * (bil[i] / bil[i - 1] - 1)
        peak = max(peak, eq); mdd = min(mdd, eq / peak - 1)
    return eq, mdd * 100, chg


def run(prices, raw=None):
    """prices = {symbol: {date: close}} (adjusted) · raw = same with raw closes (for raw variants) → markdown report"""
    raw = raw or prices
    series = {}
    for name, a, b in PAIRS:
        ds, r = ratio_series(prices[a], prices[b])
        wk = weekly_last(ds, r)
        series[name] = {x[0]: x[1] for x in wk}
    acwi_w = {x[0]: x[1] for x in weekly_last(*zip(*sorted(prices['ACWI'].items())))}
    bil_w = {x[0]: x[1] for x in weekly_last(*zip(*sorted(prices['BIL'].items())))}
    ds = sorted(set(acwi_w) & set(bil_w) & set(series['ACWI/BIL']) & set(series['HYG/IEI']))
    if len(ds) <= WARMUP + 52: raise SystemExit(f'not enough weekly bars ({len(ds)})')
    acwi, bil = [acwi_w[d] for d in ds], [bil_w[d] for d in ds]
    sc = slice(WARMUP, None)
    dsc, pxc, bilc = ds[sc], acwi[sc], bil[sc]
    years = (dsc[-1] - dsc[0]).days / 365.25
    out = [f'# Regime EMA backtest\n\nWeekly bars {dsc[0]} → {dsc[-1]} ({len(dsc)} weeks · {years:.1f} yrs) · '
           f'{WARMUP} warm-up weeks skipped · whipsaw = flip reversed within {WHIPSAW} weeks\n']
    sides, noise = {}, {}
    for v, fast, slow, conf, tf, use_raw in VARIANTS:
        for name, a, b in PAIRS:
            src = raw if use_raw else prices
            if tf == 'W':
                wk = {x[0]: x[1] for x in weekly_last(*ratio_series(src[a], src[b]))}
                sides[(v, name)] = sides_of([wk[d] for d in ds], fast, slow, conf)[sc]
                noise[(v, name)] = flip_stats(sides[(v, name)], years)
                continue
            dd, dr = ratio_series(src[a], src[b])
            dside = sides_of(dr, fast, slow, conf)
            j, wside = 0, []
            for d in ds:                                  # daily state at each weekly close
                while j + 1 < len(dd) and dd[j + 1] <= d: j += 1
                wside.append(dside[j])
            sides[(v, name)] = wside[sc]
            k0 = next(i for i, d in enumerate(dd) if d >= dsc[0])
            noise[(v, name)] = flip_stats(dside[k0:], years, WHIPSAW * 5)   # counted on daily bars · whipsaw = 20 days

    out.append('## 1. Signal noise\n\n| Variant | Ratio | Flips / yr | Whipsaws | % time red |\n|---|---|---|---|---|')
    for v, *_ in VARIANTS:
        for name, _, _ in PAIRS:
            s = noise[(v, name)]
            out.append(f"| {v} | {name} | {s['flips_yr']:.2f} | {s['whipsaws']} | {s['red_pct']:.0f}% |")

    fmt = lambda x: '—' if x is None else f'{x:+.1f}%'
    for name, _, _ in PAIRS:
        out.append(f'\n## 2. ACWI falls ≥ {DD_MIN*100:.0f}% · signal {name}\n\n'
                   '"Fell at red" = ACWI drop from its peak when the signal first turned red (closer to 0 = earlier). '
                   '"Rose at green" = ACWI gain off the low when it turned green again (smaller = earlier re-entry). — = never turned.\n')
        out.append('| Peak week | Depth | ' + ' | '.join(f'{v} fell at red · rose at green' for v, *_ in VARIANTS) + ' |')
        out.append('|---|---|' + '---|' * len(VARIANTS))
        per = [dd_rows(pxc, dsc, sides[(v, name)]) for v, *_ in VARIANTS]
        for k, row in enumerate(per[0]):
            cells = ' | '.join(f"{fmt(p[k]['fell_at_red'])} · {fmt(p[k]['rose_at_green'])}" for p in per)
            out.append(f"| {row['peak']} | {row['depth']:.1f}% | {cells} |")

    out.append('\n## 3. Core sizing factor (100 / 75 / 50) on ACWI, rest in BIL\n\n'
               '| Variant | CAGR | Max drawdown | Factor changes / yr |\n|---|---|---|---|')
    bh_eq, bh_mdd, _ = sizing(pxc, bilc, [True] * len(pxc), [True] * len(pxc))
    for v, *_ in VARIANTS:
        eq, mdd, chg = sizing(pxc, bilc, sides[(v, 'ACWI/BIL')], sides[(v, 'HYG/IEI')])
        out.append(f'| {v} | {(eq ** (1 / years) - 1) * 100:.2f}% | {mdd:.1f}% | {chg / years:.2f} |')
    out.append(f'| Buy & hold ACWI (always 100%) | {(bh_eq ** (1 / years) - 1) * 100:.2f}% | {bh_mdd:.1f}% | 0 |')
    out.append('\nNotes: ACWI/BIL returns use total-return prices · signals use adjusted prices except "raw" variants · '
               'daily variants are read at each weekly close (mid-week flips not traded) · no costs or taxes.')
    return '\n'.join(out)


def fetch(symbols, adjust=True):
    import yfinance as yf
    df = yf.download(symbols, start='2007-01-01', interval='1d', auto_adjust=adjust,
                     progress=False, group_by='column', threads=False)
    close, out = df['Close'], {}
    for s in symbols:
        ser = close[s].dropna() if s in close else []
        if not len(ser): raise SystemExit(f'no prices for {s}')
        out[s] = {ix.date(): float(v) for ix, v in ser.items()}
    return out


def selftest():
    base = datetime.date(2010, 1, 4)
    ds = [base + datetime.timedelta(days=i) for i in range(365 * 8) if (base + datetime.timedelta(days=i)).weekday() < 5]
    n = len(ds)
    # rise → 30% crash → recovery → rise (one clear drawdown episode)
    def path(i):
        a, b, c = int(n * .45), int(n * .55), int(n * .70)
        if i < a: return 100 * (1.0004 ** i)
        top = 100 * (1.0004 ** a)
        if i < b: return top * (1 - 0.30 * (i - a) / (b - a))
        if i < c: return top * 0.70 * (1 + 0.45 * (i - b) / (c - b))
        return top * 0.70 * 1.45 * (1.0003 ** (i - c))
    acwi = {d: path(i) for i, d in enumerate(ds)}
    bil = {d: 100 * (1.00008 ** i) for i, d in enumerate(ds)}
    hyg = {d: path(i) ** 0.5 * 10 for i, d in enumerate(ds)}
    iei = {d: 100.0 for d in ds}
    rep = run({'ACWI': acwi, 'BIL': bil, 'HYG': hyg, 'IEI': iei})
    assert '| Daily EMA50/100 raw (Ladder) | ACWI/BIL |' in rep, rep
    assert '## 1. Signal noise' in rep and '## 3. Core sizing' in rep, rep
    assert rep.count('| EMA') >= 3 * len(PAIRS) + 3, rep
    # a smooth single crash: every variant turns red during the fall and green again after
    assert not any('—' in ln for ln in rep.splitlines() if ln.startswith('| 20')), rep
    # confirm=2 never flips more than confirm=1
    v = [100 + math.sin(i / 3) * 5 for i in range(300)]
    assert sum(1 for a, b in zip(sides_of(v, 5, 10, 2), sides_of(v, 5, 10, 2)[1:]) if a != b) <= \
           sum(1 for a, b in zip(sides_of(v, 5, 10, 1), sides_of(v, 5, 10, 1)[1:]) if a != b)
    assert drawdowns([100, 90, 80, 95, 101, 102]) == [(0, 2, 4)]
    print('selftest OK\n'); print(rep)


def now_check():
    """Last 6 weekly bars of each ratio with EMA10/EMA20 — dividend-adjusted (app) vs raw close (TradingView default)"""
    import yfinance as yf
    out = ['# Current state check (EMA10/20 · weekly · current week incl.)\n']
    for adj in (True, False):
        df = yf.download(['ACWI', 'BIL', 'HYG', 'IEI'], period='3y', interval='1d', auto_adjust=adj,
                         progress=False, group_by='column', threads=False)['Close']
        px = {s: {ix.date(): float(v) for ix, v in df[s].dropna().items()} for s in ('ACWI', 'BIL', 'HYG', 'IEI')}
        out.append(f"## {'Adjusted (app)' if adj else 'Raw close (TradingView default)'}\n")
        for name, a, b in PAIRS:
            ds, r = ratio_series(px[a], px[b])
            wk = weekly_last(ds, r)
            vals = [x[1] for x in wk]
            f, s = ema(vals, 10), ema(vals, 20)
            out.append(f'**{name}** | week ending | ratio | EMA10 | EMA20 | side |\n|---|---|---|---|---|---|')
            for i in range(len(wk) - 6, len(wk)):
                out.append(f"| | {wk[i][0]} | {vals[i]:.5f} | {f[i]:.5f} | {s[i]:.5f} | {'🟢 up' if f[i] > s[i] else '🔴 down'} |")
            out.append('')
        if not adj:                                   # requested rule: daily EMA20/50 on raw closes
            for name, a, b in PAIRS:
                ds, r = ratio_series(px[a], px[b])
                f, s = ema(r, 20), ema(r, 50)
                out.append(f'**{name} · DAILY EMA20/50 raw** | day | ratio | EMA20 | EMA50 | side |\n|---|---|---|---|---|---|')
                for i in range(len(r) - 6, len(r)):
                    out.append(f"| | {ds[i]} | {r[i]:.5f} | {f[i]:.5f} | {s[i]:.5f} | {'🟢 up' if f[i] > s[i] else '🔴 down'} |")
                out.append('')
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--now', action='store_true')
    a = ap.parse_args()
    if a.selftest: return selftest()
    if a.now:
        rep = now_check(); print(rep)
        summ = os.environ.get('GITHUB_STEP_SUMMARY')
        if summ:
            with open(summ, 'a', encoding='utf-8') as f: f.write(rep + '\n')
        return
    syms = ['ACWI', 'BIL', 'HYG', 'IEI']
    rep = run(fetch(syms), fetch(syms, adjust=False))
    print(rep)
    summ = os.environ.get('GITHUB_STEP_SUMMARY')
    if summ:
        with open(summ, 'a', encoding='utf-8') as f: f.write(rep + '\n')


if __name__ == '__main__':
    main()
