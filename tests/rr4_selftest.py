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
U = rb.unpack(doc)
t('doc: asOf = last SPY session · bars = BARS · every symbol present', doc['asOf'] == '2026-11-23' and doc['bars'] == rb.BARS and len(U['dates']) == rb.BARS and set(U['syms']) == {rb.RRG_BENCH, *rb.RRG_SYMS} and doc['missing'] == [])
t('doc: arrays aligned to dates (len c == len h == bars) · dates ascending', all(len(v['c']) == len(v['h']) == doc['bars'] for v in U['syms'].values()) and U['dates'] == sorted(U['dates']))
t('doc: size well under Firestore 1 MB (< 500 KB for 24 symbols × close+high)', rb.doc_bytes(doc) < 500_000, rb.doc_bytes(doc))
# HF3 C — the REAL size: every symbol, the real bar count. The old array shape needed ~41k index entries (> 40,000 → the write failed every run, never selftested)
t('HF3 C: real bar count (800) × every symbol', rb.BARS == 800 and doc['bars'] == 800 and len(U['syms']) == len(rb.RRG_SYMS) + 1 and all(len(v['c']) == 800 for v in U['syms'].values()))
t('HF3 C: the bulk is two JSON strings (datesJ · symsJ), no array / map field', isinstance(doc['datesJ'], str) and isinstance(doc['symsJ'], str) and not any(isinstance(v, (list, dict)) and k != 'missing' for k, v in doc.items()), list(doc))
t('HF3 C: estimated index entries < 2,000 (limit 40,000)', rb.index_entries(doc) < 2000, rb.index_entries(doc))
old_shape = {'v': 1, 'asOf': doc['asOf'], 'bench': 'SPY', 'bars': 800, 'dates': U['dates'], 'syms': U['syms'], 'missing': []}
t('HF3 C: guard — the OLD array shape is the same order as the 40,000 limit (the estimator sees it: ~39k by our count, Firestore rejected it)', rb.index_entries(old_shape) > 30_000, rb.index_entries(old_shape))
t('HF3 C: JSON size < 900 KB', rb.doc_bytes(doc) < 900_000, rb.doc_bytes(doc))
t('HF3 C: round trip unpack == what went in (dates · closes · highs · nulls)', U['dates'] == [str(d) for d in sessions(900)[-800:]] and all(len(v['h']) == 800 for v in U['syms'].values()))
d2 = dict(data); d2['XLU'] = [r for r in data['XLU'] if str(r[0]) != '2026-11-12']
doc2 = rb.build_doc(d2, NOW); U2 = rb.unpack(doc2); i = U2['dates'].index('2026-11-12')
t('a symbol missing one day → null at that index (other symbols keep the day)', U2['syms']['XLU']['c'][i] is None and U2['syms']['XLE']['c'][i] is not None)
d3 = dict(data); d3.pop('XLF'); d3['XLE'] = None
doc3 = rb.build_doc(d3, NOW)
t('symbols that failed to download are listed in `missing` and left out', doc3['missing'] == ['XLF', 'XLE'] and 'XLF' not in rb.unpack(doc3)['syms'])
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

# 4 · CR1 — "already fresh" rule of build_prices.py
import build_prices as bp
N = utc('2026-11-24T05:30:00Z')      # Tue 00:30 ET → latest completed session = Mon 23 Nov
t('fresh: rs2 + rrg both on the latest completed session', bp.is_fresh('2026-11-23', '2026-11-23', N))
t('not fresh: rrg/bars one session behind', not bp.is_fresh('2026-11-23', '2026-11-20', N))
t('not fresh: rs2 behind', not bp.is_fresh('2026-11-20', '2026-11-23', N))
t('not fresh: a missing doc (empty asOf) → run normally', not bp.is_fresh('', '2026-11-23', N) and not bp.is_fresh('2026-11-23', None, N))
t('weekend: Friday data is fresh on Sat/Sun', bp.is_fresh('2026-11-20', '2026-11-20', utc('2026-11-22T06:00:00Z')))
t('holiday: Wed data is fresh over Thanksgiving Thursday', bp.is_fresh('2026-11-25', '2026-11-25', utc('2026-11-26T23:00:00Z')))
t('before the 16:15 ET cut the previous session is the target', bp.is_fresh('2026-11-20', '2026-11-20', utc('2026-11-23T20:00:00Z')) and not bp.is_fresh('2026-11-20', '2026-11-20', utc('2026-11-23T21:30:00Z')))


class _Doc:
    def __init__(self, d): self.exists, self._d = d is not None, d
    def to_dict(self): return self._d


class _Base:
    def __init__(self, docs, boom=False): self.docs, self.boom = docs, boom
    def collection(self, c): self.c = c; return self
    def document(self, d):
        self.k = self.c + '/' + d; return self
    def get(self):
        if self.boom: raise RuntimeError('offline')
        return _Doc(self.docs.get(self.k))


t('read_asofs reads rs2/_meta.asOf and rrg/bars.asOf', bp.read_asofs(_Base({'rs2/_meta': {'asOf': '2026-11-23'}, 'rrg/bars': {'asOf': '2026-11-23'}})) == ('2026-11-23', '2026-11-23'))
t('read_asofs: missing docs → empty strings (not fresh)', bp.read_asofs(_Base({})) == ('', ''))
t('read_asofs: read error → empty strings (run normally)', bp.read_asofs(_Base({}, boom=True)) == ('', ''))
# the workflow
wf = open(os.path.join(HERE, '..', '.github', 'workflows', 'prices.yml'), encoding='utf-8').read()
crons = re.findall(r"- cron: '([^']+)'", wf)
t('workflow: no cron on minute :00 or :30', crons and all(c.split()[0] not in ('0', '30') for c in crons), crons)
t('workflow: a backup run every day about an hour after the main run (00:13 UTC)', '13 0 * * *' in crons)
t('workflow: main runs 22:17 UTC Mon–Thu · 23:17 UTC Fri / Sat', '17 22 * * 1-4' in crons and '17 23 * * 5' in crons and '17 23 * * 6' in crons)
t('workflow: manual run is forced (never skipped as fresh) · rr4 selftest runs in the workflow', "PRICES_FORCE: ${{ github.event_name == 'workflow_dispatch'" in wf and 'tests/rr4_selftest.py' in wf)
print('PASS %d checks' % ok)
