// PS1 — pure-function tests for ps1-size.js. Run: node tests/ps1_size_test.js
const P = require('../ps1-size.js'); let f = 0, n = 0;
const ok = (c, m) => { n++; if (!c) { f++; console.log('FAIL', m); } };
const near = (a, b, m, e = 1e-6) => ok(Math.abs(a - b) < e, m + ' got ' + a + ' want ' + b);

// AAA example (lot 1): E 1,000,000 · entry 10 risk .5% · SL 8 · entry 10.5 risk .3%
let r = P.planSize({ E: 1e6, lot: 1, ideaRiskPct: 0.8, entries: [{ px: 10, riskPct: 0.5 }, { px: 10.5, riskPct: 0.3 }], stops: [{ px: 8 }] });
ok(r.ok, 'aaa ok'); ok(r.rows[0].qty === 2500, 'aaa row1 ' + r.rows[0].qty); ok(r.rows[1].qty === 1200, 'aaa row2 ' + r.rows[1].qty);
near(r.riskPct, 0.80, 'aaa total risk'); near(r.leftPct, 0, 'aaa left 0 (0.8 idea)'); near(r.avgEntry, 10.16, 'aaa avg', 0.005);
r = P.planSize({ E: 1e6, lot: 1, ideaRiskPct: 1.0, entries: [{ px: 10, riskPct: 0.5 }, { px: 10.5, riskPct: 0.3 }], stops: [{ px: 8 }] });
near(r.leftPct, 0.20, 'aaa left .20 of 1.0');
// rows over the idea budget
r = P.planSize({ E: 1e6, lot: 1, ideaRiskPct: 0.7, entries: [{ px: 10, riskPct: 0.5 }, { px: 10.5, riskPct: 0.3 }], stops: [{ px: 8 }] });
ok(r.errs.includes('ROWS_OVER_BUDGET'), 'rows over budget');
// single row, rounding down, TH lot 100
r = P.planSize({ E: 1e6, market: 'TH', ideaRiskPct: 0.4, entries: [{ px: 100 }], stops: [{ px: 95 }] });
ok(r.rows[0].qty === 800, 'TH lot 100 floor ' + r.rows[0].qty);
// blended stop 50/50
let b = P.blendStop([{ px: 90, pct: 50 }, { px: 80, pct: 50 }]); near(b.px, 85, 'blend 85');
r = P.planSize({ E: 1e6, lot: 1, ideaRiskPct: 0.5, entries: [{ px: 100 }], stops: [{ px: 90, pct: 50 }, { px: 80, pct: 50 }] });
ok(r.rows[0].qty === 333, 'blend qty ' + r.rows[0].qty); near(r.avgStop, 85, 'avg SL'); ok(r.riskPct <= 0.5 + 1e-9, 'risk within');
ok(!P.blendStop([{ px: 90, pct: 60 }, { px: 80, pct: 50 }]).ok && P.blendStop([{ px: 90, pct: 60 }, { px: 80, pct: 50 }]).err === 'STOP_PCT_100', '% != 100 blocks');
ok(P.blendStop([{ px: 90 }, { px: 80 }, { px: 70 }, { px: 60 }, { px: 50 }]).err === 'TOO_MANY_STOPS', 'max 4 stops');
// size cap trims shares
r = P.planSize({ E: 1e6, lot: 1, ideaRiskPct: 1.0, maxSizePct: 7.5, entries: [{ px: 100 }], stops: [{ px: 99 }] });
ok(r.trimmed && r.qty === 750, 'trim qty ' + r.qty); near(r.sizePct, 7.5, 'size 7.5');
r = P.planSize({ E: 1e6, lot: 1, ideaRiskPct: 0.5, maxSizePct: 7.5, entries: [{ px: 100 }], stops: [{ px: 90 }] });
ok(!r.trimmed && r.qty === 500, 'no trim');
ok(P.planSize({ E: 1e6, ideaRiskPct: 0.5, entries: [{ px: 80 }], stops: [{ px: 90 }] }).err === 'ENTRY_NOT_ABOVE_STOP', 'entry <= stop');
// cap check blocks
const c = P.cfg({}); let k = P.capCheck({ E: 1e6, cfg: c, bucket: 'winner', newRisk: 5000, usedBucket: 11000, usedTotal: 20000 });
ok(!k.ok && k.reasons.includes('BUCKET_CAP'), 'bucket cap blocks'); // 16000 = 1.6% > 1.5
k = P.capCheck({ E: 1e6, cfg: c, bucket: 'ladder', newRisk: 12000, usedBucket: 10000, usedTotal: 40000 });
ok(!k.ok && k.reasons.includes('TOTAL_CAP') && !k.reasons.includes('BUCKET_CAP'), 'total cap blocks ' + JSON.stringify(k.reasons));
k = P.capCheck({ E: 1e6, cfg: c, bucket: 'ladder', newRisk: 5000, usedBucket: 0, usedTotal: 0 }); ok(k.ok, 'under caps ok');
// add-on gate
let a = P.addOnBudget({ ideaBudget: 5000, tranches: [{ qty: 100, avg: 50, stop: 50 }, { qty: 50, avg: 55, stop: 56 }] }); ok(a.newBudget && a.budget === 5000, 'new budget when stops>=avg');
a = P.addOnBudget({ ideaBudget: 5000, tranches: [{ qty: 100, avg: 50, stop: 48 }] }); ok(!a.newBudget && a.budget === 4800, 'remaining only ' + a.budget);
a = P.addOnBudget({ ideaBudget: 5000, tranches: [{ qty: 100, avg: 50, stop: 51 }, { qty: 10, avg: 60, stop: 59 }] }); ok(!a.newBudget, 'one tranche below avg -> no new budget');
// Sat lots
let s = P.satLots({ E: 1e6, riskPct: 0.2, entry: 2000, stop: 1990, multiplier: 100, lotStep: 0.01 }); near(s.lots, 2, 'sat lots 2', 1e-9);
s = P.satLots({ E: 1e6, riskPct: 0.2, entry: 2000, stop: 1993, multiplier: 100, lotStep: 0.01 }); near(s.lots, 2.85, 'sat floor to step', 1e-9); ok(s.risk <= 2000 + 1e-6, 'sat risk <= budget');
s = P.satLots({ E: 1e6, riskPct: 0.1, entry: 1000, stop: 970, multiplier: 200, lotStep: 1 }); ok(s.lots === 0 && s.belowMin, 'sat lot step 1 rounds down to 0');
// panel
const pos = [
  { id: 1, ticker: 'A', bucket: 'winner', qty: 100, avg: 50, stop: 50, px: 60, fx: 1 },     // breakeven stop: principal 0, giveback 1000
  { id: 2, ticker: 'B', bucket: 'winner', qty: 100, avg: 50, stop: 45, px: 52, fx: 1 },     // principal 500, gb 700
  { id: 3, ticker: 'C', bucket: 'ladder', qty: 10, avg: 10, px: 11, fx: 1 },                // no stop -> unknown
  { id: 4, ticker: 'D', bucket: 'ladder', qty: 10, avg: 10, stop: 8, fx: 1 }];              // no px -> giveback unknown
let pn = P.panel({ E: 100000, cfg: c, positions: pos });
near(pn.ideas[0].principal, 0, 'breakeven principal 0'); near(pn.principal, 500 + 20, 'sum excludes unknown');
ok(pn.missing.length === 2 && pn.unknownPrincipal === 1 && pn.unknownGiveBack === 2 && pn.partial, 'missing flagged, not 0');
ok(pn.ideas[2].principal === null && pn.ideas[3].giveBack === null, 'null not 0');
ok(P.gbLevel(7.99, c) === 'ok' && P.gbLevel(8, c) === 'amber' && P.gbLevel(9.99, c) === 'amber' && P.gbLevel(10, c) === 'red', 'give-back bands');
pn = P.panel({ E: 10000, cfg: c, positions: [{ id: 1, ticker: 'X', bucket: 'winner', qty: 100, avg: 50, stop: 40, px: 50, fx: 1 }] });
ok(pn.buckets.winner.status === 'stop' && pn.buckets.ladder.status === 'stop', 'total cap reached -> every bucket Stop opening');
pn = P.panel({ E: 100000, cfg: c, positions: [{ id: 1, ticker: 'X', bucket: 'winner', qty: 100, avg: 50, stop: 35, px: 50, fx: 1 }] });
ok(pn.buckets.winner.status === 'stop' && pn.buckets.ladder.status === 'normal', 'winner at 1.5% cap -> stop, ladder normal');
// settings: no hardcoded default
ok(c.def.ladder === null && c.def.winner === null && c.def.satMain === null && c.def.satTac === null, 'default risk starts empty');
ok(P.cfg({ def: { winner: 0.4, satMain: 0.2, satTac: 0.9 } }).def.winner === 0.4, 'default inside range kept');
ok(P.cfg({ def: { satTac: 0.9 } }).def.satTac === null, 'out of range -> empty');
ok(P.cfgErrors({ def: { winner: 0.9 } })['def.winner'], 'range error');
ok(P.cfgErrors({ weights: { ladder: 50, winner: 30, sat: 10 } }).weights, 'weights total');
console.log(f ? `${f}/${n} FAILED` : `ps1-size: ${n} checks PASS`); process.exit(f ? 1 : 0);
