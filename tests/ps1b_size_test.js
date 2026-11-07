// PS1b — pure-function tests (min stop · loss limits · fake clock). Run: node tests/ps1b_size_test.js
const P = require('../ps1-size.js'); let f = 0, n = 0;
const ok = (c, m) => { n++; if (!c) { f++; console.log('FAIL', m); } };
const T = s => Date.parse(s + '+07:00');   // Thai local time
// ── min stop
let r = P.minStopCheck({ minPct: 0.5, entry: 4000, stop: 3985 });
ok(!r.ok && r.err === 'TOO_TIGHT' && Math.abs(r.minPts - 20) < 1e-9, 'tighter than 0.5% blocks (min 20 pts)');
ok(P.minStopCheck({ minPct: 0.5, entry: 4000, stop: 3980 }).ok, 'equal to min OK');
ok(P.minStopCheck({ minPct: 0.5, entry: 4000, stop: 4020 }).ok, 'short side equal OK');
ok(P.minStopCheck({ minPct: 0.5, entry: 4000, stop: 3900 }).ok, 'wider OK');
ok(P.minStopCheck({ minPct: null, entry: 4000, stop: 3900 }).err === 'MIN_NOT_SET', 'not set blocks');
ok(P.minStopCheck({ minPct: 0, entry: 4000, stop: 3900 }).err === 'MIN_NOT_SET', '0 = not set');
ok(P.minStopCheck({ minPct: 1.5, entry: 100000, pointSize: 10 }).minPts === 150, 'point size display');
// lots: no value cap — lots = E×risk% ÷ (stop pts × mult), floor to step
let L = P.satLots({ E: 150000, riskPct: 0.2, entry: 4000, stop: 3980, multiplier: 100, lotStep: 0.01 });
ok(Math.abs(L.lots - 0.15) < 1e-9, 'sat lots ' + L.lots);
ok(P.portPct(300, 20000) === 1.5, 'port pct');
// ── clock
ok(P.dayStart(T('2026-11-09T05:59:00')) === T('2026-11-08T06:00:00'), 'before 06:00 belongs to previous day');
ok(P.dayStart(T('2026-11-09T06:00:00')) === T('2026-11-09T06:00:00'), 'day starts 06:00');
ok(new Date(P.weekStart(T('2026-11-11T12:00:00'))).toISOString() === new Date(T('2026-11-09T06:00:00')).toISOString(), 'week starts Monday 06:00 (Wed -> Mon 9 Nov)');
ok(P.weekStart(T('2026-11-09T05:00:00')) === T('2026-11-02T06:00:00'), 'Monday 05:00 still last week');
// ── drawdown machine
const cfg = { ddMax: 20, ddHalf: 10 };
let s = P.lossStep(null, 100, cfg); ok(s.peak === 100 && !s.half, 'peak set');
s = P.lossStep(s, 92, cfg); ok(!s.half, '8% normal');
s = P.lossStep(s, 90, cfg); ok(s.half, '10% half size');
s = P.lossStep(s, 86, cfg); ok(s.half && s.low === 86, 'deeper drop tracked (14%)');
s = P.lossStep(s, 92, cfg); ok(s.half, '−8% not yet recovered half of 14 (needs ≤ −7%)');
s = P.lossStep(s, 93, cfg); ok(!s.half, 'back to −7% = half of 14% recovered -> full size');
s = P.lossStep(s, 101, cfg); ok(s.peak === 101, 'new peak');
s = { peak: 100, half: true, low: 85, stopped: false }; s = P.lossStep(s, 80, cfg); ok(s.stopped && !s.half, '20% stop & review');
s = P.lossStep(s, 120, cfg); ok(s.stopped && s.peak === 100, 'recovery alone does not resume');
ok(P.lossResume(s, 95, '').err === 'NOTE_REQUIRED' && P.lossResume(s, 95, '   ').err === 'NOTE_REQUIRED', 'resume needs a note');
let rs = P.lossResume(s, 95, 'reviewed plan'); ok(rs.ok && rs.state.peak === 95 && !rs.state.stopped, 'resume resets peak to current value');
// ── day / week units  (R money 300)
const NOW = T('2026-11-11T10:00:00');
const it = (gid, ts, pnl, risk, extra) => Object.assign({ gid, idea: gid, t: T(ts), pnl, risk: risk == null ? 300 : risk, rMoney: 300 }, extra);
let u = P.lossUnits({ now: NOW, items: [it('a', '2026-11-11T08:00:00', -300), it('b', '2026-11-11T09:00:00', -300)] });
ok(Math.abs(u.day - 2) < 1e-9 && u.nDay === 2, 'two normal losses = 2R');
let st = P.lossStatus({ port: 'sat', value: 100, state: { peak: 100 }, units: u }); ok(st.status === 'day' && st.blocked && st.until === T('2026-11-12T06:00:00'), 'stop today until 06:00 next day');
u = P.lossUnits({ now: NOW, items: [it('a', '2026-11-11T08:00:00', -700)] });
ok(Math.abs(u.day - 700 / 300) < 1e-9, 'one big gap loss counted by size (2.33R)');
ok(P.lossStatus({ port: 'winner', value: 100, state: { peak: 100 }, units: u }).status === 'day', 'one big loss alone stops the day');
u = P.lossUnits({ now: NOW, items: [it('a', '2026-11-11T08:00:00', -250)] });
ok(Math.abs(u.day - 250 / 300) < 1e-9 && P.lossStatus({ port: 'sat', value: 100, state: {}, units: u }).status === 'normal', 'under 2R = normal');
u = P.lossUnits({ now: NOW, items: [it('a', '2026-11-11T08:00:00', -50), it('b', '2026-11-11T08:30:00', 0), it('c', '2026-11-11T08:40:00', 40)] });
ok(u.day === 0, 'scratch (<¼ risk loss), breakeven, win not counted');
u = P.lossUnits({ now: NOW, items: [it('a', '2026-11-11T08:00:00', -100, 400)] });
ok(u.day === 0, 'loss exactly ¼ of planned risk not counted');
u = P.lossUnits({ now: NOW, items: [it('a', '2026-11-11T08:00:00', -101, 400)] }); ok(u.day > 0, 'loss above ¼ counted');
// partial exits of the same idea counted once (net)
u = P.lossUnits({ now: NOW, items: [it('g1', '2026-11-11T07:00:00', -150, 150), it('g1', '2026-11-11T08:00:00', -150, 150)] });
ok(Math.abs(u.day - 1) < 1e-9 && u.nDay === 1, 'partial exits = one loss of 1R');
// same idea in two accounts = one loss (largest)
u = P.lossUnits({ now: NOW, items: [it('m1', '2026-11-11T07:00:00', -300, 300, { idea: 'XAU|Long|2026-11-11' }), it('f1', '2026-11-11T07:00:00', -150, 150, { idea: 'XAU|Long|2026-11-11', rMoney: 150 })] });
ok(u.nDay === 1 && Math.abs(u.day - 1) < 1e-9, 'same idea across accounts = 1 loss');
// reset times
u = P.lossUnits({ now: T('2026-11-12T05:59:00'), items: [it('a', '2026-11-11T08:00:00', -700)] }); ok(u.day > 2, 'still blocked at 05:59');
u = P.lossUnits({ now: T('2026-11-12T06:00:00'), items: [it('a', '2026-11-11T08:00:00', -700)] }); ok(u.day === 0 && u.week > 2, 'day resets at 06:00, week keeps it');
// week 5R
const wk = [0, 1, 2, 3, 4].map(i => it('w' + i, '2026-11-1' + (0 + i > 1 ? 1 : 0) + 'T0' + (6 + i) + ':30:00', -300));
u = P.lossUnits({ now: T('2026-11-11T12:00:00'), items: [it('a', '2026-11-09T07:00:00', -300), it('b', '2026-11-09T09:00:00', -300), it('c', '2026-11-10T09:00:00', -300), it('d', '2026-11-10T11:00:00', -300), it('e', '2026-11-10T13:00:00', -300)] });
st = P.lossStatus({ port: 'sat', value: 100, state: {}, units: u }); ok(Math.abs(u.week - 5) < 1e-9 && st.status === 'week' && st.until === T('2026-11-16T06:00:00'), 'week 5R -> stop until Monday 06:00');
u = P.lossUnits({ now: T('2026-11-16T06:00:00'), items: [it('a', '2026-11-13T07:00:00', -3000)] }); ok(u.week === 0, 'week resets Monday 06:00');
// startMs: older trades don't count
u = P.lossUnits({ now: NOW, startMs: T('2026-11-11T09:30:00'), items: [it('a', '2026-11-11T08:00:00', -700)] }); ok(u.day === 0, 'trades before first run do not count');
// compounder: dd only
st = P.lossStatus({ port: 'ladder', value: 100, state: { peak: 100 }, units: { day: 9, week: 9, dayEnd: 1, weekEnd: 1 } }); ok(st.status === 'normal', 'compounder ignores day/week');
// precedence + half size
st = P.lossStatus({ port: 'sat', value: 88, state: { peak: 100, half: true, low: 88 }, units: { day: 0, week: 0 } }); ok(st.status === 'half' && st.mult === 0.5 && !st.blocked, 'half size mult 0.5, not blocked');
st = P.lossStatus({ port: 'sat', value: 70, state: { peak: 100, stopped: true }, units: { day: 3, week: 6, dayEnd: 1, weekEnd: 2 } }); ok(st.status === 'review' && st.blocked && st.until === null, 'review beats day/week');
ok(P.lossCfgErrors({ ddMax: 20, ddHalf: 25 }).ddHalf && P.lossCfgErrors({ dayR: 3, weekR: 2 }).weekR && P.lossCfgErrors({ ddMax: -1 }).ddMax, 'cfg errors');
ok(P.lossCfg(null).dayR === 2 && P.lossCfg({}).weekR === 5 && P.lossCfg({}).ddMax === 20 && P.lossCfg({}).ddHalf === 10, 'defaults 20/10/2R/5R');
console.log(f ? `${f}/${n} FAILED` : `ps1b-size: ${n} checks PASS`); process.exit(f ? 1 : 0);
