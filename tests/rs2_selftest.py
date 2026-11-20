#!/usr/bin/env python3
"""RS2a data selftest (no network, no pandas) · python3 tests/rs2_selftest.py
symbol-file filtering · liquidity filter · chunked download retry · doc size limit/split · rating parity with RS1 · universe refresh rule"""
import datetime as dt
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import build_prices as bp
import build_rs2 as b

ok = 0


def t(name, cond):
    global ok
    if not cond:
        print('FAIL', name)
        sys.exit(1)
    ok += 1


# 1 · symbol files
NAS = """Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares
AAPL|Apple Inc. - Common Stock|Q|N|N|100|N|N
QQQ|Invesco QQQ Trust, Series 1|G|N|N|100|Y|N
ZZZT|NASDAQ TEST STOCK|G|Y|N|100|N|N
ABCDW|Acme Acquisition Corp. - Warrants|S|N|N|100|N|N
ABCDU|Acme Acquisition Corp. - Units|S|N|N|100|N|N
ABCDR|Acme Corp. - Rights|S|N|N|100|N|N
PFEDP|Foo Inc. - 7.5% Series A Cumulative Preferred Stock|Q|N|N|100|N|N
BADCO|Bad Co. - Common Stock|Q|N|D|100|N|N
NVDA|NVIDIA Corporation - Common Stock|Q|N|N|100|N|N
GOOGL|Alphabet Inc. - Class A Common Stock|Q|N|N|100|N|N
File Creation Time: 1120202622:00||||||
"""
OTH = """ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol
A|Agilent Technologies, Inc. Common Stock|N|A|N|100|N|A
BRK.B|Berkshire Hathaway Inc. Class B Common Stock|N|BRK.B|N|100|N|BRK.B
SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY
GLD|SPDR Gold Shares|P|GLD|Y|100|N|GLD
XYZ$A|Xyz Corp. Preferred Shares|N|XYZ$A|N|100|N|XYZ-A
AMEXCO|Amex Co. Common Stock|A|AMEXCO|N|100|N|AMEXCO
BATSCO|Bats Co. Common Stock|Z|BATSCO|N|100|N|BATSCO
TSTX|Test Co. Common Stock|N|TSTX|N|100|Y|TSTX
CEF|Some Income Fund Common Shares|N|CEF|N|100|N|CEF
File Creation Time: 1120202622:00||||||
"""
info = b.parse_symbol_files(NAS, OTH)
syms = {x['t']: x for x in info}
t('keeps common stocks', set(syms) == {'AAPL', 'NVDA', 'GOOGL', 'A', 'BRK-B', 'AMEXCO'})
t('drops ETF / test / warrants / units / rights / preferred / non-normal / Arca / BATS / funds',
  not ({'QQQ', 'ZZZT', 'ABCDW', 'ABCDU', 'ABCDR', 'PFEDP', 'BADCO', 'SPY', 'GLD', 'BATSCO', 'TSTX', 'CEF'} & set(syms)) and 'XYZ$A' not in syms)
t('exchange labels', syms['AAPL']['e'] == 'NASDAQ' and syms['A']['e'] == 'NYSE' and syms['AMEXCO']['e'] == 'AMEX')
t('yahoo symbol BRK.B → BRK-B', 'BRK-B' in syms)
t('names trimmed', syms['AAPL']['n'] == 'Apple' and syms['A']['n'].startswith('Agilent Technologies') and not syms['GOOGL']['n'].endswith('Stock'))
t('long names ellipsized ≤ 28', len(b.clean_name('A Very Long Company Name Incorporated International Common Stock')) <= 28)

# 2 · liquidity
D0 = dt.date(2025, 1, 1)


def series(price, n, vol):
    return {'close': [(D0 + dt.timedelta(days=i), price) for i in range(n)], 'vol': [vol] * n}


t('adv50', abs(b.adv50([10.0] * 60, [1_000_000] * 60) - 10_000_000) < 1e-6)
t('adv50 needs 50 bars', b.adv50([10.0] * 49, [1e6] * 49) is None)
t('liquid: $10 and $10M both inclusive', b.is_liquid(10.0, 10_000_000.0) and not b.is_liquid(9.99, 5e7) and not b.is_liquid(50.0, 9_999_999.0) and not b.is_liquid(None, 1e8) and not b.is_liquid(20.0, None))


def climb(start, step, n, vol, base_n=0):
    px = [start + step * i for i in range(n)]
    return {'close': [(D0 + dt.timedelta(days=i), p) for i, p in enumerate(px)], 'vol': [vol] * n}


# universe: 40 liquid risers of different slope · one cheap · one illiquid · one short history
N = 300
info = [{'t': 'L%02d' % i, 'n': 'L%02d' % i, 'e': 'NYSE'} for i in range(40)]
data = {x['t']: climb(50, 0.02 + 0.01 * i, N, 400_000) for i, x in enumerate(info)}   # 400k sh × ≥$50 = ≥$20M
info += [{'t': 'CHEAP', 'n': 'Cheap', 'e': 'NYSE'}, {'t': 'THIN', 'n': 'Thin', 'e': 'NYSE'}, {'t': 'NEW', 'n': 'New', 'e': 'NYSE'}, {'t': 'NODATA', 'n': 'X', 'e': 'NYSE'}]
data['CHEAP'] = series(5.0, N, 50_000_000)
data['THIN'] = series(50.0, N, 1_000)
data['NEW'] = series(50.0, 100, 5_000_000)
bench = bp._rows([(D0 + dt.timedelta(days=i), 100 + 0.01 * i) for i in range(N)])
rows, table, liq, nrated = b.rs2_rows(info, data, bench)
tk = {r['t'] for r in rows}
t('liquidity filter applied (cheap / thin / no data out)', 'CHEAP' not in tk and 'THIN' not in tk and 'NODATA' not in tk)
t('liquid list = 41 (40 risers + NEW) · rated = 40 (NEW has < 253 bars)', len(liq) == 41 and nrated == 40 and 'NEW' not in tk)
t('table is the liquid-universe table', table and table['n'] == 40 and len(table['cuts']) == 99)
t('sorted by rating desc', [r['r'] for r in rows] == sorted((r['r'] for r in rows), reverse=True) and rows[0]['t'] == 'L39')
r0 = rows[0]
t('row has every short key', all(k in r0 for k in ('t', 'n', 'e', 'r', 'p', 'l', 'h', 'o', 'x', 'xd', 'c', 'v', 'a3', 'a6', 'a9', 'a12')))
t('same rating as RS1 formula (rs_for on the same table)', all(r['r'] == bp.rs_for(r['t'], bp._rows(data[r['t']]['close']), bench, table, 'SPY')['rating'] for r in rows))
t('adv in $ (rounded int)', isinstance(r0['v'], int) and r0['v'] > b.MIN_ADV)

# 3 · chunked download + retry
calls = []


def flaky(part):
    calls.append(list(part))
    if part[0] == 's200' and calls.count(part) == 1:
        raise RuntimeError('rate limited')
    if part[0] == 's400':
        raise RuntimeError('always fails')
    return {s: {'close': [], 'vol': []} for s in part}


names = ['s%d' % i for i in range(0, 600, 1)]
sl = []
got, failed = b.fetch_chunked(names, flaky, chunk=200, sleep=0, retries=1, sleeper=lambda x: sl.append(x))
t('chunks of ≤ 200', all(len(c) <= 200 for c in calls))
t('retry once then continue', calls.count(names[200:400]) == 2 and calls.count(names[400:600]) == 2)
t('chunk that fails twice is skipped and counted', failed == 1 and len(got) == 400)
t('sleeps between chunks', len(sl) >= 3)
t('chunks helper', [len(c) for c in b.chunks(range(450), 200)] == [200, 200, 50])

# 4 · doc size / split
def fake_rows(n):
    return [{'t': 'T%04d' % i, 'n': 'Company %04d' % i, 'e': 'NYSE', 's': 'Technology', 'i': 'Software - Application', 'r': 99 - i % 99, 'p': 80, 'l': 'u', 'h': 0, 'o': -0.123,
             'x': 123.45, 'xd': '2026-11-03', 'c': 111.11, 'v': 123456789, 'a3': 0.123, 'a6': 0.234, 'a9': 0.345, 'a12': 0.456} for i in range(n)]


r2000 = fake_rows(2200)
d = b.split_docs('2026-11-18', r2000)
t('2,200 realistic rows fit one doc < 900 KB', list(d) == ['latest'] and b.doc_bytes(d['latest']) < b.DOC_LIMIT)
d = b.split_docs('2026-11-18', r2000, limit=100_000)
t('over the limit → header + latest_0..k, ≤ 500 rows each, every row once',
  d['latest']['parts'] == len(d) - 1 and 'rows' not in d['latest'] and all(len(v['rows']) <= 500 for k, v in d.items() if k != 'latest')
  and sum(len(v['rows']) for k, v in d.items() if k != 'latest') == 2200 and d['latest']['n'] == 2200)
t('every split doc < limit', all(b.doc_bytes(v) < b.DOC_LIMIT for v in d.values()))

# 5 · sectors cache + refresh rule
cache = {'L39': 'Technology|Software'}
looked = []
n = b.fill_sectors(rows, cache, budget_s=100, getter=lambda y: (looked.append(y), ('Energy', 'Oil'))[1])
t('sector lookups only for cache misses', 'L39' not in looked and n == len(rows) - 1)
tick = iter(range(0, 1000, 10))
cache2 = {}
n2 = b.fill_sectors(rows, cache2, budget_s=25, getter=lambda y: ('S', 'I'), clock=lambda: next(tick))
t('sector lookups stop at the time budget (best-rated first)', 0 < n2 < len(rows) and list(cache2)[0] == rows[0]['t'])
b.with_sectors(rows, {'L39': 'Technology|Software'})
t('with_sectors splits sector|industry', rows[0]['s'] == 'Technology' and rows[0]['i'] == 'Software')
now = dt.datetime(2026, 11, 20, 22, 30, tzinfo=dt.timezone.utc)
t('universe refresh: none → stale · 7 days → stale · 2 days → fresh',
  b.universe_stale({}, now) and b.universe_stale({'universeAt': (now - dt.timedelta(days=7)).isoformat(), 'liquid': [1]}, now)
  and not b.universe_stale({'universeAt': (now - dt.timedelta(days=2)).isoformat(), 'liquid': [1]}, now))

# 6 · build_prices.run_rs accepts the liquid table for US
tab = {'asOf': '2026-11-18', 'n': 40, 'cuts': table['cuts'], 'cuts4w': table['cuts4w']}
wr = {}
bp.run_rs({'L10': 'L10'}, [], lambda need: {y: data[y]['close'] if y in data else bench for y in need if y in data or y in ('SPY',)} | {'SPY': bench}, lambda k, v: wr.__setitem__(k, v), now, us_table=tab)
t('Watch rating for a US stock comes from the liquid table', wr['L10']['rs']['rating'] == [r for r in rows if r['t'] == 'L10'][0]['r'] and wr['_meta']['rsTable']['us']['n'] == 40)
print('PASS %d checks' % ok)
