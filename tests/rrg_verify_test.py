#!/usr/bin/env python3
"""RV1 A — the app's own rrgCompute/rrgToWeekly (node, extracted from index.html) must equal tools/rrg_verify.py (pandas) on a fixed synthetic price set:
23 symbols × D/W × 2 end dates + edge cases. Pass = equal state/days/prevDays/date and numbers within 1e-9 (1e-5 for ill-conditioned flat series).
    python3 tests/rrg_verify_test.py"""
import json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, 'tools'))
import rrg_verify as V
ok = fail = 0
def t(name, cond, extra=''):
    global ok, fail
    if cond: ok += 1
    else: fail += 1; print('FAIL', name, extra)
cases = V.gen()
with tempfile.TemporaryDirectory() as d:
    cf = os.path.join(d, 'c.json'); json.dump(cases, open(cf, 'w'))
    app = json.loads(subprocess.run(['node', os.path.join(ROOT, 'tools', 'rrg_app_run.js'), cf], capture_output=True, text=True, check=True).stdout)
py = V.run(cases)
bad = V.cmp(app, py)
t('app == independent (all cases, D and W)', not bad, bad[:5])
R = app['rows']
t('app constants K=0.10 zero-hysteresis fast12 slow26', app['meta']['K'] == 0.10 and app['meta']['hyst'] == 'zero' and app['meta']['fast'] == 12 and app['meta']['slow'] == 26)
t('23 symbols covered ×2 end dates', len([k for k in R if k.startswith(('midweek:', 'friday:'))]) == 46)
t('SPY vs itself → not classified (flat)', 'err' in R['edge:spy_vs_itself']['d'] and 'err' in R['edge:spy_vs_itself']['w'])
for k in ('edge:mismatch_last_date', 'edge:mismatch_last_date_bench_behind'): t(k + ' → "Mismatched end dates"', R[k]['d'].get('err', '').startswith('Mismatched end dates'))
t('missing SPY day == missing ETF day (intersection)', R['edge:missing_spy_day']['d']['ratio'] == R['edge:missing_etf_day']['d']['ratio'])
t('D need-1 → error · need → ok', 'err' in R['edge:D_need_minus_1']['d'] and 'err' not in R['edge:D_need_exact']['d'])
t('W need 82 weeks → ok · 81 → error', 'err' not in R['edge:W_need_exact_82w']['w'] and 'err' in R['edge:W_need_minus_1_81w']['w'])
for k in (1, 2, 3, 4): t(f'last week with {k} session(s) is partial → preview only', 'preview' in R[f'edge:last_week_{k}_sessions_partial']['w'])
t('holiday week (ends Wed) closed once the next week starts', 'preview' not in R['edge:holiday_week_ends_wed_ref_next_week']['w'] and 'preview' in R['edge:holiday_week_ends_wed_ref_same_week']['w'])
t('friday end date: no preview', all('preview' not in R[f'friday:{s}']['w'] for s in V.SYMS))
t('synthetic SPY×1.01^n is Outperforming (rel pos)', R['edge:synthetic_up_1.01^n']['d']['rel'] == 'pos' and R['edge:synthetic_up_1.01^n']['w']['rel'] == 'pos')
t('every quadrant reachable (D)', {q for q in ('lead', 'weak', 'imp', 'lag', 'flat') if R.get('edge:quadrant_' + q, {}).get('d', {}).get('quad') == q} == {'lead', 'weak', 'imp', 'lag', 'flat'})
print(f'PASS {ok}/{ok + fail}' if not fail else f'FAIL {fail}/{ok + fail}'); sys.exit(1 if fail else 0)
