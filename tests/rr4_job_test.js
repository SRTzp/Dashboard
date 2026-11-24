#!/usr/bin/env node
// RR4 / CR1 — the app's own code (extracted from index.html): (1) the job's bars → rows == Twelve Data bars → rows (quadrant + tail + every field)
// (2) the JS trading-calendar twin == tests/fixtures/us_calendar.json (same fixture as the python selftest)
//   node tests/rr4_job_test.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const src = fs.readFileSync(path.join(__dirname, '..', 'index.html'), 'utf8');
function block(from, to) { const a = src.indexOf(from), b = src.indexOf(to, a); if (a < 0 || b < 0) throw new Error('marker not found: ' + from); return src.slice(a, b); }
function fn(name) { const a = src.indexOf('\nfunction ' + name + '(') + 1; if (a < 1) throw new Error('no function ' + name); let i = src.indexOf('{', a), d = 0; for (; i < src.length; i++) { if (src[i] === '{') d++; else if (src[i] === '}' && --d === 0) break; } return src.slice(a, i + 1); }
const code = block('const RRG_BUILD', '/* ---------- ดึงราคาจาก Twelve Data') + '\n' + fn('rrgSeries') + '\n' + fn('rrgBuildRows') + '\n' + fn('rrgMergeRow') + '\nlet rrgTrimDate = "";\n' + fn('rrgEtNow') + '\n' + fn('rrgProvCut')
  + '\nlet REF = null; function rrgToday(){ return REF; }\n'
  + block('/* ── UX3 · US trading calendar', 'async function ux3RrgJob');
let NOW = Date.UTC(2030, 0, 15, 12, 0);
class FakeDate extends Date { constructor(...a) { a.length ? super(...a) : super(NOW); } static now() { return NOW; } }
const ctx = vm.createContext({ Math, Date: FakeDate, Intl, Map, Set, Array, Object, JSON, String, Number, console, parseInt });
vm.runInContext(code + '\nthis.__api = {RRG_SYMS, RRG_BENCH, rrgSeries, rrgBuildRows, rrgJobGot, rrgJobOk, rrgJobRows, setRef:(r)=>{REF=r;}, ux3Holidays, ux3LastDone, ux3Behind, ux3IsSession, ux3PrevSession};', ctx);
const A = ctx.__api;
let ok = 0, fail = 0;
const t = (name, cond, extra) => { if (cond) ok++; else { fail++; console.log('FAIL', name, extra === undefined ? '' : JSON.stringify(extra).slice(0, 400)); } };

// ---- calendar fixture
const fx = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures', 'us_calendar.json'), 'utf8'));
for (const y of Object.keys(fx.holidays)) t('holidays ' + y, JSON.stringify([...A.ux3Holidays(+y)].sort()) === JSON.stringify(fx.holidays[y]), [...A.ux3Holidays(+y)].sort());
for (const c of fx.last_done) t('last completed session · ' + c.now + ' · ' + c.why, A.ux3LastDone(Date.parse(c.now)) === c.last, A.ux3LastDone(Date.parse(c.now)));
for (const c of fx.behind) t('sessions behind · ' + c.now + ' as-of ' + c.asof, A.ux3Behind(c.asof, Date.parse(c.now)) === c.n, A.ux3Behind(c.asof, Date.parse(c.now)));

// ---- same bars through both paths
function rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
function sessions(n, endIso) { const out = []; let d = endIso; while (out.length < n) { if (A.ux3IsSession(d)) out.push(d); d = A.ux3PrevSession(d); } return out.reverse(); }
const END = '2030-01-14', ds = sessions(900, END);     // NOW = 15 Jan 2030 12:00 UTC (after the close) → END is a completed session
const syms = [A.RRG_BENCH].concat(A.RRG_SYMS.map(x => x.s)), bars = {};
syms.forEach((s, k) => { const r = rng(7 + k); let p = 100, drift = (k - 12) / 6000; bars[s] = ds.map(d => { p *= 1 + drift + (r() - 0.5) * 0.02; const c = Math.round(p * 1e4) / 1e4; return {d, c, h: Math.round(c * (1 + r() * 0.01) * 1e4) / 1e4}; }); });
const skipDay = ds[ds.length - 40];
bars.XLE = bars.XLE.map(b => b.d === skipDay ? null : b);      // one ETF missing a day
// Twelve Data shape: {values:[{datetime, close, high}]} newest first
const D = ds.slice(-800), inD = new Set(D);   // identical bars: the job keeps the last 800 sessions, so does the Twelve Data side of this test
const td = {}; syms.forEach(s => { td[s] = bars[s].filter(b => b && inD.has(b.d)).slice().reverse().map(b => ({ datetime: b.d, close: String(b.c), high: String(b.h) })); });
// job doc shape (scripts/rrg_bars.py): dates (last 800) + aligned arrays, null = no bar
const doc = { v: 1, asOf: END, bench: 'SPY', bars: D.length, dates: D, syms: {} };
syms.forEach(s => { const m = new Map(bars[s].filter(Boolean).map(b => [b.d, b])); doc.syms[s] = { c: D.map(d => m.has(d) ? m.get(d).c : null), h: D.map(d => m.has(d) ? m.get(d).h : null) }; });
A.setRef(END);
const bench = A.rrgSeries(td.SPY), tdD = [], tdW = [];
A.RRG_SYMS.forEach(def => { const r = A.rrgBuildRows(def, td, bench); tdD.push(r.d); tdW.push(r.w); });
const job = A.rrgJobRows(JSON.parse(JSON.stringify(doc)));
t('job rows built', !!job && job.rowsD.length === 23 && job.rowsW.length === 23);
t('no row is an error (both paths)', tdD.every(r => !r.err) && job.rowsD.every(r => !r.err), job.rowsD.filter(r => r.err));
const J = x => JSON.stringify(x);
let same = 0; A.RRG_SYMS.forEach((def, i) => { if (J(tdD[i]) === J(job.rowsD[i]) && J(tdW[i]) === J(job.rowsW[i])) same++; else console.log('differs', def.s); });
t('every symbol: Daily + Weekly row identical (quadrant · tail · numbers)', same === 23, same);
t('quadrants + tails match explicitly (Daily)', tdD.every((r, i) => r.quad === job.rowsD[i].quad && J(r.tail) === J(job.rowsD[i].tail)) && tdD.every(r => Array.isArray(r.tail) && r.tail.length === 5));
t('more than one quadrant in the data (the test is not trivially equal)', new Set(tdD.map(r => r.quad)).size >= 2, tdD.map(r => r.quad));
t('lastBar = END', job.lastBar === END);

// ---- validity rule: ≤ 1 trading day old
const at = (iso) => Date.parse(iso);
t('fresh: asOf == last completed session', A.rrgJobOk(Object.assign({}, doc), at('2030-01-15T12:00:00Z')));
t('fresh: 1 session old (job missed one night)', A.rrgJobOk(Object.assign({}, doc), at('2030-01-16T12:00:00Z')));
t('stale: 2 sessions old → Twelve Data', !A.rrgJobOk(Object.assign({}, doc), at('2030-01-17T12:00:00Z')));
t('weekend is not stale (Fri bars on Saturday)', A.rrgJobOk(Object.assign({}, doc, { asOf: '2030-01-11' }), at('2030-01-12T12:00:00Z')));
t('missing symbol → not usable', !A.rrgJobOk(Object.assign({}, doc, { syms: Object.assign({}, doc.syms, { XLE: undefined }) }), at('2030-01-15T12:00:00Z')));
t('no doc / no SPY → not usable', !A.rrgJobOk(null, at('2030-01-15T12:00:00Z')) && !A.rrgJobOk(Object.assign({}, doc, { syms: {} }), at('2030-01-15T12:00:00Z')));
console.log(fail ? `FAIL ${fail}/${ok + fail}` : `PASS ${ok}/${ok}`); process.exit(fail ? 1 : 0);
