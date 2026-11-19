#!/usr/bin/env python3
"""RS1 data selftest (ไม่แตะเน็ต) · python3 tests/rs1_selftest.py"""
import datetime as dt
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import build_prices as bp

D0 = dt.date(2025, 1, 1)
def rows(vals):
    return [(D0 + dt.timedelta(days=i), v) for i, v in enumerate(vals)]
ok = 0
def t(name, cond):
    global ok
    if not cond:
        print('FAIL', name); sys.exit(1)
    ok += 1

# 1 · weighted score: closes[-1]=t, offsets 63/126/189/252 — ตั้งค่าให้ r แต่ละช่วงรู้ค่า
c = [100.0] * 300
c[-1 - 252] = 50.0    # r12m = +100%
c[-1 - 189] = 80.0    # r9m  = +25%
c[-1 - 126] = 100.0   # r6m  = 0
c[-1 - 63] = 125.0    # r3m  = -20%
t('score', abs(bp.rs_score(c) - (0.4 * -0.2 + 0.2 * 0 + 0.2 * 0.25 + 0.2 * 1.0)) < 1e-12)
t('score<253', bp.rs_score([100.0] * 252) is None and bp.rs_score([100.0] * 253) is not None)
t('score offset', bp.rs_score([100.0] * 273, 20) is not None and bp.rs_score([100.0] * 273, 21) is None)

# 2 · percentile cuts + rating (ties, clamp, monotonic)
sc = [i / 100 for i in range(100)]          # 100 คะแนนไม่ซ้ำ
cuts = bp.pct_cuts(sc)
t('cuts99', len(cuts) == 99 and all(a <= b for a, b in zip(cuts, cuts[1:])))
t('min=1', bp.rs_rating(min(sc), cuts) == 1)
t('max=99', bp.rs_rating(max(sc), cuts) == 99)
t('clamp', bp.rs_rating(-9, cuts) == 1 and bp.rs_rating(9, cuts) == 99)
t('median~50', 49 <= bp.rs_rating(0.495, cuts) <= 51)
r = [bp.rs_rating(s, cuts) for s in sc]
t('monotonic', all(a <= b for a, b in zip(r, r[1:])))
tie = bp.pct_cuts([0.1, 0.5, 0.5, 0.5, 0.9] * 20)
t('ties same', bp.rs_rating(0.5, tie) == bp.rs_rating(0.5, tie) and bp.rs_rating(0.5, tie) not in (1, 99))
t('empty', bp.rs_rating(0.3, []) is None and bp.rs_rating(None, cuts) is None)

# 3 · rs_for: <252 bars → rating None + reason
short = rows([100.0 + i for i in range(200)])
x = bp.rs_for('AAPL', short, short, {'cuts': cuts, 'cuts4w': cuts})
t('hist<252', x['rating'] is None and x['reason'] == 'history<252' and x['bench'] == 'SPY' and x['line'] is None)
t('no-data', bp.rs_for('AAPL', [], None, None)['reason'] == 'no-data')
long_ = rows([100.0 + i * 0.5 for i in range(300)])
t('no table', bp.rs_for('AAPL', long_, long_, None)['reason'].startswith('universe<'))
full = bp.rs_for('AAPL', long_, long_, {'cuts': cuts, 'cuts4w': cuts})
t('rated', isinstance(full['rating'], int) and 1 <= full['rating'] <= 99 and full['asOf'] == long_[-1][0].isoformat())
t('keys', set(full) >= {'rating', 'rating4wAgo', 'line', 'newHigh', 'newHigh5d', 'bench', 'asOf'})

t('bench<252', bp.rs_for('PTT.BK', long_, rows([100.0]), {'cuts': cuts, 'cuts4w': cuts})['reason'] == 'bench<252')
t('no-bench', bp.rs_for('PTT.BK', long_, None, {'cuts': cuts, 'cuts4w': cuts})['reason'] == 'no-bench')

# bench fallback: ^SET.BK ≥252 → ใช้ ^SET.BK · ไม่ถึง → TDEX.BK · ไม่มีทั้งคู่ → ^SET.BK (reason bench<252)
tdex, setix = rows([100.0 + i * 0.1 for i in range(300)]), rows([100.0 + i * 0.2 for i in range(300)])
t('bench main', bp.pick_bench('th', {'^SET.BK': setix, 'TDEX.BK': tdex})[0] == '^SET.BK')
t('bench 252', bp.pick_bench('th', {'^SET.BK': setix[:252], 'TDEX.BK': tdex})[0] == '^SET.BK' and bp.pick_bench('th', {'^SET.BK': setix[:251], 'TDEX.BK': tdex})[0] == 'TDEX.BK')
t('bench fb', bp.pick_bench('th', {'^SET.BK': rows([100.0]), 'TDEX.BK': tdex}) == ('TDEX.BK', tdex))
t('bench none', bp.pick_bench('th', {'^SET.BK': rows([100.0])})[0] == '^SET.BK' and bp.pick_bench('us', {'SPY': setix})[0] == 'SPY')
sh = {}
bp.run_rs({'T1.BK': 'T1'}, [f'T{i}.BK' for i in range(40)], lambda ys: {**{f'T{i}.BK': tdex for i in range(40)}, '^SET.BK': rows([100.0]), 'TDEX.BK': tdex},
          lambda k, d: sh.setdefault(k, {}).update(d), dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc))
t('run_rs bench', sh['T1.BK']['rs']['bench'] == 'TDEX.BK' and sh['T1.BK']['rs']['line'] is not None)

# 4 · TH ticker mapping + market/bench
t('map PTT', bp.to_ysym('ptt', 'TH') == 'PTT.BK' and bp.to_ysym('PTT.BK') == 'PTT.BK' and bp.to_ysym(' aapl ') == 'AAPL')
t('bench th', bp.rs_for('PTT.BK', short, None, None)['bench'] == '^SET.BK' and bp.rs_market('PTT.BK') == 'th')
t('pick', bp.pick_rs_tickers([{'status': 'open', 'ticker': 'aapl', 'market': 'US'}, {'status': 'closed', 'ticker': 'zzz'}],
    [{'ticker': 'AAPL'}, {'ticker': 'PTT', 'market': 'TH'}, {'ticker': 'OLD', 'archived': True}, {'ticker': 'ADVANC.BK'}])
    == {'AAPL': 'AAPL', 'PTT.BK': 'PTT', 'ADVANC.BK': 'ADVANC.BK'})

# 5 · RS line + new-high logic (bench คงที่ 100 → line = stock/100)
def mk(vals): return bp.align(rows(vals), rows([100.0] * len(vals)))
up = [100.0] * 260 + [100 * (1 + 0.03 * i / 20) for i in range(1, 21)]      # +3% ใน 20 วัน
t('line up', bp.rs_line_info(mk(up))[0] == 'up')
t('line flat', bp.rs_line_info(mk([100.0] * 280))[0] == 'flat')
t('line flat 2%', bp.rs_line_info(mk([100.0] * 260 + [100 + 2 * i / 20 for i in range(1, 21)]))[0] == 'flat')   # = +2.0% ไม่เกิน band
t('line down', bp.rs_line_info(mk([100.0] * 260 + [100 - 3 * i / 20 for i in range(1, 21)]))[0] == 'down')
l, nh, nh5 = bp.rs_line_info(mk([100.0 + i * 0.1 for i in range(280)]))
t('new high', nh is True and nh5 is True)
v = [100.0 + i * 0.1 for i in range(270)] + [120.0, 90, 90, 90, 90, 90, 90, 90, 90, 90]   # ทำ high เมื่อ 9 วันก่อน
l, nh, nh5 = bp.rs_line_info(mk(v))
t('not new high', nh is False and nh5 is False)
v = [100.0 + i * 0.1 for i in range(274)] + [200.0, 150, 140, 130, 120, 110][:6]            # high 5 วันก่อน (อยู่ใน 5 session)
v = v[:276] + [200.0, 150, 140, 130]                                                         # high ที่ index -4
l, nh, nh5 = bp.rs_line_info(mk(v))
t('5d only', nh is False and nh5 is True)
t('line short', bp.rs_line_info(mk([100.0] * 200)) == (None, None, None))
t('align gaps', len(bp.align(rows([1, 2, 3]), [(D0, 1.0), (D0 + dt.timedelta(days=2), 1.0)])) == 2)

# 6 · rs_table + run_rs (ปลอม fetch/write)
import random
random.seed(1)
def walk(drift): 
    v, out = 100.0, []
    for _ in range(300):
        v *= 1 + drift + random.uniform(-0.01, 0.01); out.append(v)
    return rows(out)
uni = {f'U{i}': walk(i / 20000) for i in range(60)}
uni.update({f'T{i}.BK': walk(i / 20000) for i in range(40)})
tb = bp.rs_table(uni, bp.rs_market)
t('table', tb['us']['n'] == 60 and tb['th']['n'] == 40 and len(tb['us']['cuts']) == 99 and len(tb['us']['cuts4w']) == 99)
small = bp.rs_table({f'U{i}': walk(0) for i in range(5)}, bp.rs_market)
t('table small', 'us' not in small)
store = {}
data = dict(uni); data['SPY'] = walk(0.0003); data['^SET.BK'] = walk(0.0001); data['NEW'] = walk(0.01)
n, failed = bp.run_rs({'NEW': 'NEW', 'MISSING': 'MISSING', 'T39.BK': 'T39'}, list(uni), lambda ys: {y: data[y] for y in ys if y in data},
                      lambda k, d: store.setdefault(k, {}).update(d), dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc))
t('run_rs', n == 2 and [f['ySym'] for f in failed] == ['MISSING'] and store['NEW']['rs']['rating'] >= 90
  and store['MISSING']['rs']['reason'] == 'no-data' and store['_meta']['rsTable']['us']['n'] == 60)
# 7 · WL2 — hi52 / offHigh / r3m..r12m (additive) + sector cache
h = bp.rs_hi_ret(rows([100.0] * 100 + [200.0] + [150.0] * 199 + [100.0]))
t('wl2 hi', h['hi52'] == 200.0 and h['hi52Date'] == (D0 + dt.timedelta(days=100)).isoformat() and h['offHigh'] == -0.5)
t('wl2 ret', h['r3m'] == round(100 / 150 - 1, 4) and h['r12m'] is not None)
sh = bp.rs_hi_ret(rows([100.0 + i for i in range(100)]))
t('wl2 short', sh['hi52'] is None and sh['offHigh'] is None and sh['r3m'] is not None and sh['r6m'] is None)
t('wl2 empty', bp.rs_hi_ret([])['offHigh'] is None and 'hi52' in bp.rs_for('AAPL', long_, long_, {'cuts': cuts, 'cuts4w': cuts}))
fz = bp.rs_for('AAPL', long_, long_, {'cuts': cuts, 'cuts4w': cuts})
t('wl2 at high', fz['offHigh'] == 0.0 and fz['hi52Date'] == long_[-1][0].isoformat() and fz['rating'] == full['rating'])
st2, calls = {}, []
def sf(y): calls.append(y); return {'sector': 'Technology', 'industry': 'Semiconductors'}
bp.run_rs({'NEW': 'NEW', 'T39.BK': 'T39'}, list(uni), lambda ys: {y: data[y] for y in ys if y in data}, lambda k, d: st2.setdefault(k, {}).update(d),
          dt.datetime(2026, 11, 18, tzinfo=dt.timezone.utc), sf, {'T39.BK'})
t('wl2 sector once', calls == ['NEW'] and st2['NEW']['sector'] == 'Technology' and st2['NEW']['industry'] == 'Semiconductors' and 'sector' not in st2['T39.BK'])
t('wl2 rs keys', 'offHigh' in st2['NEW']['rs'] and st2['NEW']['rs']['rating'] >= 90)
t('universe file', len(bp.load_universe(os.path.join(bp.ROOT, 'data', 'universe_th.txt'))) == 100)
print(f'RS1 selftest OK · {ok} checks')
