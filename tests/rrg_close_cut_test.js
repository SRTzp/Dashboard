// RV1b — fake-clock test: today's (America/New_York) bar is dropped before 16:15 ET, kept after; weekly Friday preview; cache replaced after the close.
//   node tests/rrg_close_cut_test.js
const A = require('../tools/rrg_app_run.js'), fs = require('fs'), vm = require('vm'), path = require('path');
let ok = 0, fail = 0;
const t = (n, c, x) => { if (c) ok++; else { fail++; console.log('FAIL', n, x === undefined ? '' : JSON.stringify(x)); } };
const utc = (y, m, d, h, mi) => Date.UTC(y, m - 1, d, h, mi);
function bars(endISO, n) {   // weekday bars newest-first
  const out = []; let d = new Date(endISO + 'T00:00:00Z');
  while (out.length < n) { const w = d.getUTCDay(); if (w && w < 6) { const i = out.length; out.push({ datetime: d.toISOString().slice(0, 10), close: String(100 + (n - i) * 0.1 + Math.sin(i) ), high: String(101 + (n - i) * 0.1) }); } d.setUTCDate(d.getUTCDate() - 1); }
  return out;
}
const last = (m) => [...m.keys()].sort().pop();
// ET = UTC-5 in November (EST): 16:14 ET = 21:14 UTC · 16:15 ET = 21:15 UTC
const Wed = '2026-11-18', Fri = '2026-11-20';
A.setNow(utc(2026, 11, 18, 20, 0));   // Wed 15:00 ET
t('15:00 ET: today bar dropped', last(A.rrgSeries(bars(Wed, 30))) === '2026-11-17');
A.setNow(utc(2026, 11, 18, 21, 14));  // 16:14 ET
t('16:14 ET: still dropped', last(A.rrgSeries(bars(Wed, 30))) === '2026-11-17' && A.getTrim() === Wed);
A.setNow(utc(2026, 11, 18, 21, 15));  // 16:15 ET
t('16:15 ET: kept', last(A.rrgSeries(bars(Wed, 30))) === Wed);
A.setNow(utc(2026, 11, 19, 3, 0));    // Wed 22:00 ET (Thu 03:00 UTC): ET date is still Wed → kept
t('after midnight UTC but still Wed ET: kept', last(A.rrgSeries(bars(Wed, 30))) === Wed);
A.setNow(utc(2026, 11, 18, 14, 29));  // 09:29 ET
t('pre-market: today bar dropped, yesterday kept', last(A.rrgSeries(bars(Wed, 30))) === '2026-11-17');
// DST: July = EDT (UTC-4): 16:14 ET = 20:14 UTC
A.setNow(utc(2026, 7, 15, 20, 14)); t('EDT 16:14 ET: dropped', last(A.rrgSeries(bars('2026-07-15', 30))) === '2026-07-14');
A.setNow(utc(2026, 7, 15, 20, 15)); t('EDT 16:15 ET: kept', last(A.rrgSeries(bars('2026-07-15', 30))) === '2026-07-15');
// SPY and ETF trimmed identically → no "Mismatched end dates", rows built on the previous close
const mk = (end) => { const e = bars(end, 600), b = bars(end, 600).map((x, i) => Object.assign(x, { close: String(200 + (600 - i) * 0.05) })); return { e, b }; };
A.setNow(utc(2026, 11, 20, 15, 0)); A.setRef('2026-11-20');   // Fri 10:00 ET
{ const { e, b } = mk(Fri), r = A.rrgBuildRows({ s: 'XLK', n: 'x' }, { XLK: e }, A.rrgSeries(b));
  t('Fri mid-session D: last bar = Thu', r.d.date === '2026-11-19' && !r.d.err, r.d.err || r.d.date);
  t('Fri mid-session W: week partial → preview as of Thu, state from closed weeks', r.w.preview && r.w.preview.asOf === '2026-11-19' && r.w.date === '2026-11-13', r.w); }
A.setNow(utc(2026, 11, 20, 21, 15)); A.setRef('2026-11-20');   // Fri 16:15 ET
{ const { e, b } = mk(Fri), r = A.rrgBuildRows({ s: 'XLK', n: 'x' }, { XLK: e }, A.rrgSeries(b));
  t('Fri after close D: last bar = Fri', r.d.date === Fri, r.d.date);
  t('Fri after close W: week complete, no preview', !r.w.preview && r.w.date === Fri, r.w); }
// cache replaced after the close — the app's own rrgCacheFresh/rrgBarsFresh/rrgFreshTxt
const src = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
function fn(name) { const a = src.indexOf('\nfunction ' + name + '(') + 1; if (a < 1) throw new Error('no ' + name); let i = src.indexOf('{', a), d = 0; for (; i < src.length; i++) { if (src[i] === '{') d++; else if (src[i] === '}' && --d === 0) break; } return src.slice(a, i + 1); }
let F = null, NOW2 = 0;
class FD extends Date { constructor(...a) { a.length ? super(...a) : super(NOW2); } static now() { return NOW2; } }
const ctx = vm.createContext({ Date: FD, Intl, Math, parseInt, Map, Array, Object, String, console, ffState: () => F });
vm.runInContext(['const RRG_MODEL=2,RRG_MAXAGE=4;', 'let rrgTrimDate="";', 'function rrgToday(){ return new Date(Date.now()).toISOString().slice(0,10); }', fn('rrgDayDiff'), fn('rrgBarsFresh'), fn('rrgEtNow'), fn('rrgProvCut'), fn('rrgCacheFresh'), fn('rrgOutdated'), fn('rrgFreshTxt'),
  'this.api={rrgCacheFresh,rrgFreshTxt};'].join('\n'), ctx);
const rrg = (prov) => ({ rrg: { day: '2026-11-18', rowsD: [{ sym: 'X', tailF: [1, 2, 3, 4] }], model: 2, lastBar: '2026-11-17', prov } });
NOW2 = utc(2026, 11, 18, 20, 0); F = rrg('2026-11-18');   // Wed 15:00 ET, fetched mid-session
t('mid-session cache is fresh while still open', ctx.api.rrgCacheFresh(F) === true);
t('header says "as of <date> close"', /as of 2026-11-17 close/.test(ctx.api.rrgFreshTxt(F.rrg)), ctx.api.rrgFreshTxt(F.rrg));
NOW2 = utc(2026, 11, 18, 21, 15);                          // 16:15 ET
t('after the close the mid-session cache is stale → refetch', ctx.api.rrgCacheFresh(F) === false);
F = rrg(''); t('cache fetched after close (no prov) stays fresh', ctx.api.rrgCacheFresh(F) === true);
// the app itself: IRBO gone, ROBO "Robotics", build bumped
t('RRG_SYMS has ROBO/Robotics, no IRBO', A.RRG_SYMS.some(x => x.s === 'ROBO' && x.n === 'Robotics') && !A.RRG_SYMS.some(x => x.s === 'IRBO') && A.RRG_SYMS.length === 23);
console.log(fail ? `FAIL ${fail}/${ok + fail}` : `PASS ${ok}/${ok + fail}`); process.exit(fail ? 1 : 0);
