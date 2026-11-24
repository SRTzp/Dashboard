#!/usr/bin/env python3
"""RR4 / CR1 data selftest (no network, no pandas) · python3 tests/rr4_selftest.py
RRG symbol list == index.html · bars doc (alignment · size · partial bar · missing symbol) · US calendar vs tests/fixtures/us_calendar.json"""
import datetime as dt
import json
import os
import re
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))
import rrg_bars as rb
import us_sessions as us

ok = 0


def t(name, cond, extra=''):
    global ok
    if not cond:
        print('FAIL', name, extra)
        sys.exit(1)
    ok += 1


def utc(s):
    return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))


# 1 · the job's symbol list is the app's
src = open(os.path.join(HERE, '..', 'index.html'), encoding='utf-8').read()
m = re.search(r"const RRG_SYMS = \[(.*?)\];", src, re.S)
app_syms = re.findall(r"\{s:'([A-Z0-9]+)'", m.group(1))
t('RRG_SYMS (job) == RRG_SYMS (index.html), same order', rb.RRG_SYMS == app_syms, (rb.RRG_SYMS, app_syms))
t("RRG_BENCH (job) == RRG_BENCH (index.html)", re.search(r"const RRG_BENCH = '(\w+)'", src).group(1) == rb.RRG_BENCH)
t('bars kept ≥ what the weekly view needs (82 weeks ≈ 410 sessions)', rb.BARS >= 410)

# 2 · bars doc
NOW = utc('2026-11-24T05:30:00Z')          # Tue 00:30 ET


def sessions(n, end='2026-11-23'):
    d, out = dt.date.fromisoformat(end), []
    while len(out) < n:
        if us.is_session(d):
            out.append(d)
        d -= dt.timedelta(days=1)
    return sorted(out)


ds = sessions(900)
data = {s: [(d, 100 + i * 0.01 + k, 101 + i * 0.01 + k) for i, d in enumerate(ds)] for k, s in enumerate([rb.RRG_BENCH] + rb.RRG_SYMS)}
doc = rb.build_doc(data, NOW)
t('doc: asOf = last SPY session · bars = BARS · every symbol present', doc['asOf'] == '2026-11-23' and doc['bars'] == rb.BARS and len(doc['dates']) == rb.BARS and set(doc['syms']) == {rb.RRG_BENCH, *rb.RRG_SYMS} and doc['missing'] == [])
t('doc: arrays aligned to dates (len c == len h == bars) · dates ascending', all(len(v['c']) == len(v['h']) == doc['bars'] for v in doc['syms'].values()) and doc['dates'] == sorted(doc['dates']))
t('doc: size well under Firestore 1 MB (< 500 KB for 24 symbols × close+high)', rb.doc_bytes(doc) < 500_000, rb.doc_bytes(doc))
d2 = dict(data); d2['XLU'] = [r for r in data['XLU'] if str(r[0]) != '2026-11-12']
doc2 = rb.build_doc(d2, NOW); i = doc2['dates'].index('2026-11-12')
t('a symbol missing one day → null at that index (other symbols keep the day)', doc2['syms']['XLU']['c'][i] is None and doc2['syms']['XLE']['c'][i] is not None)
d3 = dict(data); d3.pop('XLF'); d3['XLE'] = None
doc3 = rb.build_doc(d3, NOW)
t('symbols that failed to download are listed in `missing` and left out', doc3['missing'] == ['XLF', 'XLE'] and 'XLF' not in doc3['syms'])
d4 = dict(data); d4.pop(rb.RRG_BENCH)
t('no SPY → no doc (nothing is written)', rb.build_doc(d4, NOW) is None)
wrote = {}
t('run(): no SPY → write() never called', rb.run(lambda s: d4, lambda k, v: wrote.update({k: v}), NOW) is None and not wrote)
# a bar dated "today" (ET) before 16:15 ET is intraday
today_rows = {s: r + [(dt.date(2026, 11, 24), 150, 151)] for s, r in data.items()}
t('intraday bar of today (before 16:15 ET) is dropped', rb.build_doc(today_rows, utc('2026-11-24T15:00:00Z'))['asOf'] == '2026-11-23')
t('the same bar is kept after 16:15 ET', rb.build_doc(today_rows, utc('2026-11-24T21:30:00Z'))['asOf'] == '2026-11-24')
bad = {s: r[:-1] + [(r[-1][0], float('nan'), 1)] for s, r in data.items()}
t('NaN / non-positive closes are dropped', rb.build_doc(bad, NOW)['asOf'] == str(ds[-2]))
t('numbers rounded to 4 dp', rb.clean([('2026-01-02', 1.23456789, 1.3333333)]) == [('2026-01-02', 1.2346, 1.3333)])
big = rb.build_doc(data, NOW, 800); rb.DOC_LIMIT, old = 200_000, rb.DOC_LIMIT
w2 = {}; rb.run(lambda s: data, lambda k, v: w2.update({k: v}), NOW); rb.DOC_LIMIT = old
t('size guard: over the limit → fewer bars (never over)', w2['bars']['bars'] < 800)

# 3 · calendar (same fixture the app twin is tested with)
fx = json.load(open(os.path.join(HERE, 'fixtures', 'us_calendar.json')))
for y, hs in fx['holidays'].items():
    t('holidays %s' % y, sorted(str(d) for d in us.holidays(int(y))) == hs, (y, sorted(str(d) for d in us.holidays(int(y)))))
for c in fx['last_done']:
    t('last completed session · %s · %s' % (c['now'], c['why']), str(us.last_completed_session(utc(c['now']))) == c['last'], str(us.last_completed_session(utc(c['now']))))
for c in fx['behind']:
    t('sessions behind · now %s as-of %s' % (c['now'], c['asof']), us.sessions_behind(c['asof'], utc(c['now'])) == c['n'], us.sessions_behind(c['asof'], utc(c['now'])))
print('PASS %d checks' % ok)
