#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compare_regime.py — RM1 research add-on (display only · no effect on the app).
Last 5 years of adjusted closes (yfinance auto_adjust=True) for ACWI/BIL and HYG/IEI.
Compares SMA 10/20 vs SMA 20/50 of the ratio:
  - flips per year per ratio
  - % of days the modifier table gives 100 / 80 / 60
  - sessions from the 2020 low and the 2022 low back to a 100 % modifier
The table + fallback are read from risk-engine.js (POLICY.regime), so the report follows the policy settings.
Run by .github/workflows/regime-compare.yml (workflow_dispatch) because Yahoo rate-limits the Mac.
  python3 scripts/compare_regime.py --out docs/reports/RM1-compare.md
  python3 scripts/compare_regime.py --selftest
"""
import argparse, datetime, json, math, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAIRS = {'ACWI_BIL': ('ACWI', 'BIL'), 'HYG_IEI': ('HYG', 'IEI')}
PERIODS = [(10, 20), (20, 50)]
LOWS = {'2020 low (23 Mar 2020)': datetime.date(2020, 3, 23), '2022 low (12 Oct 2022)': datetime.date(2022, 10, 12)}


def policy():
    """table + fallback from risk-engine.js POLICY.regime (so the report follows the settings)"""
    src = open(os.path.join(ROOT, 'risk-engine.js'), encoding='utf-8').read()
    m = re.search(r"regime:\s*\{\s*table:\s*\{\s*green:\s*\{\s*green:\s*([\d.]+),\s*red:\s*([\d.]+)\s*\},\s*red:\s*\{\s*green:\s*([\d.]+),\s*red:\s*([\d.]+)\s*\}\s*\},\s*fallback:\s*([\d.]+)", src)
    if not m: return {'gg': 1.0, 'gr': .8, 'rg': .8, 'rr': .6, 'fb': .8}
    a, b, c, d, f = map(float, m.groups()); return {'gg': a, 'gr': b, 'rg': c, 'rr': d, 'fb': f}


def sma(vals, n, i): return sum(vals[i - n + 1:i + 1]) / n


def states(r, fast, slow):
    """per-bar state (None until `slow` bars) · equal -> previous valid · none -> neutral"""
    out, prev = [None] * len(r), None
    for i in range(slow - 1, len(r)):
        a, b = round(sma(r, fast, i), 12), round(sma(r, slow, i), 12)
        cur = 'green' if a > b else 'red' if a < b else (prev or 'neutral')
        out[i] = cur
        if a != b: prev = cur
    return out


def ratio(a, b):
    ds = sorted(set(a) & set(b)); ds = [d for d in ds if a[d] and b[d] and b[d] != 0 and math.isfinite(a[d]) and math.isfinite(b[d])]
    return ds, [a[d] / b[d] for d in ds]


def modifier(eq, cr, P):
    if eq in ('green', 'red') and cr in ('green', 'red'): return {('green', 'green'): P['gg'], ('green', 'red'): P['gr'], ('red', 'green'): P['rg'], ('red', 'red'): P['rr']}[(eq, cr)]
    return P['fb']


def analyse(ds_all, series, P, years=5):
    """series = {key: (dates, ratio)} -> per period: flips/yr per ratio, % days at each modifier, days from lows back to 100 %"""
    res = {}
    for fast, slow in PERIODS:
        st = {k: dict(zip(d, states(r, fast, slow))) for k, (d, r) in series.items()}
        common = [d for d in ds_all if all(st[k].get(d) for k in st)]
        flips = {}
        for k in st:
            seq = [st[k][d] for d in common]; n = sum(1 for i in range(1, len(seq)) if seq[i] != seq[i - 1])
            flips[k] = n / (len(common) / 252.0) if common else None
        mods = [modifier(st['ACWI_BIL'][d], st['HYG_IEI'][d], P) for d in common]
        share = {v: 100.0 * sum(1 for m in mods if abs(m - v) < 1e-9) / len(mods) for v in sorted(set([P['gg'], P['gr'], P['rg'], P['rr'], P['fb']]), reverse=True)} if mods else {}
        back = {}
        for nm, low in LOWS.items():
            idx = next((i for i, d in enumerate(common) if d >= low), None)
            if idx is None: back[nm] = None; continue
            j = next((k for k in range(idx, len(common)) if abs(mods[k] - P['gg']) < 1e-9), None)
            back[nm] = (j - idx) if j is not None else None
        res[(fast, slow)] = {'days': len(common), 'from': common[0].isoformat() if common else None, 'to': common[-1].isoformat() if common else None, 'flips': flips, 'share': share, 'back': back}
    return res


def render(res, P):
    L = ['# RM1 — regime signal comparison (research only)', '',
         'Adjusted closes (yfinance `auto_adjust=True`), ratio = numerator ÷ denominator, SMA of the **ratio**. Modifier table from `risk-engine.js`: green/green %d%% · green/red %d%% · red/green %d%% · red/red %d%% · fallback %d%%. Display only — no effect on the app.' % tuple(round(P[k] * 100) for k in ('gg', 'gr', 'rg', 'rr', 'fb')), '']
    first = next(iter(res.values()))
    L += ['Window: %s → %s (%d aligned sessions).' % (first['from'], first['to'], first['days']), '']
    L += ['## Flips per year', '', '| SMA | ACWI/BIL | HYG/IEI |', '|---|---:|---:|']
    for (f, s), r in res.items(): L.append('| %d/%d | %s | %s |' % (f, s, *(('%.1f' % r['flips'][k]) if r['flips'].get(k) is not None else '—' for k in ('ACWI_BIL', 'HYG_IEI'))))
    L += ['', '## Share of days at each modifier', '']
    vals = sorted({v for r in res.values() for v in r['share']}, reverse=True)
    L += ['| SMA | ' + ' | '.join('%d%%' % round(v * 100) for v in vals) + ' |', '|---|' + '---:|' * len(vals)]
    for (f, s), r in res.items(): L.append('| %d/%d | ' % (f, s) + ' | '.join('%.1f%%' % r['share'].get(v, 0.0) for v in vals) + ' |')
    L += ['', '## Sessions from the low back to a 100% modifier', '', '| SMA | ' + ' | '.join(LOWS) + ' |', '|---|' + '---:|' * len(LOWS)]
    for (f, s), r in res.items(): L.append('| %d/%d | ' % (f, s) + ' | '.join(('%d' % r['back'][n]) if r['back'].get(n) is not None else 'not reached' for n in LOWS) + ' |')
    L += ['', '_Generated %s UTC · source yfinance_' % datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')]
    return '\n'.join(L) + '\n'


def download(symbols):
    import yfinance as yf
    df = yf.download(symbols, period='6y', interval='1d', auto_adjust=True, progress=False, group_by='column', threads=False)
    close = df['Close']; out = {}
    for s in symbols:
        if s in close:
            ser = close[s].dropna()
            if len(ser): out[s] = {ix.date(): float(v) for ix, v in ser.items()}
    return out


def selftest():
    P = {'gg': 1.0, 'gr': .8, 'rg': .8, 'rr': .6, 'fb': .8}
    assert modifier('green', 'green', P) == 1.0 and modifier('red', 'red', P) == .6 and modifier('green', 'neutral', P) == .8
    asc = [float(i) for i in range(1, 51)]
    assert states(asc, 20, 50)[-1] == 'green' and states(asc[::-1], 20, 50)[-1] == 'red' and states(asc, 20, 50)[48] is None
    eq = asc + [-449.0]; assert states(eq, 20, 50)[-1] == 'green'                       # equal -> previous
    assert states([1.0] * 50, 20, 50)[-1] == 'neutral'
    base = datetime.date(2020, 1, 1); ds = [base + datetime.timedelta(days=i) for i in range(2200) if (base + datetime.timedelta(days=i)).weekday() < 5]
    up = {d: 100 + i * 0.1 for i, d in enumerate(ds)}; one = dict.fromkeys(ds, 1.0)
    wave = {d: 100 + 10 * math.sin(i / 25.0) for i, d in enumerate(ds)}
    series = {'ACWI_BIL': ratio(up, one), 'HYG_IEI': ratio(wave, one)}
    r = analyse(ds, series, P)
    assert set(r) == set(PERIODS) and r[(10, 20)]['flips']['HYG_IEI'] > 0 and r[(20, 50)]['flips']['HYG_IEI'] > 0 and r[(10, 20)]['flips']['ACWI_BIL'] == 0, r
    assert r[(10, 20)]['days'] > r[(20, 50)]['days']                                  # shorter warm-up -> more aligned sessions
    assert abs(sum(r[(20, 50)]['share'].values()) - 100) < 1e-6
    md = render(r, P); assert '| 10/20 |' in md and '| 20/50 |' in md and 'Flips per year' in md
    print('selftest OK')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default=os.path.join(ROOT, 'docs', 'reports', 'RM1-compare.md')); ap.add_argument('--selftest', action='store_true'); a = ap.parse_args()
    if a.selftest: return selftest()
    syms = sorted({s for p in PAIRS.values() for s in p}); px = download(syms)
    miss = [s for s in syms if s not in px]
    if miss: print('✗ no adjusted data for', ','.join(miss), '— report not written'); sys.exit(1)
    series = {k: ratio(px[n], px[d]) for k, (n, d) in PAIRS.items()}
    cutoff = datetime.date.today() - datetime.timedelta(days=365 * 5 + 2)
    series = {k: ([d for d in ds if d >= cutoff - datetime.timedelta(days=120)], [r for d, r in zip(ds, rs) if d >= cutoff - datetime.timedelta(days=120)]) for k, (ds, rs) in series.items()}   # warm-up for the SMAs
    ds_all = sorted(set(series['ACWI_BIL'][0]) & set(series['HYG_IEI'][0])); ds_all = [d for d in ds_all if d >= cutoff]
    P = policy(); md = render(analyse(ds_all, series, P), P)
    os.makedirs(os.path.dirname(a.out), exist_ok=True); open(a.out, 'w', encoding='utf-8').write(md); print('✓ wrote', a.out); print(md)


if __name__ == '__main__':
    main()
