// PV1 A3 — node tests for pos-view.js (run: node tests/pv1_posview_test.js)
const P = require('../pos-view.js'); let pass = 0, fail = 0;
const t = (n, c, x) => { if (c) pass++; else { fail++; console.log('FAIL', n, x === undefined ? '' : JSON.stringify(x)); } };
const near = (a, b, e = 0.01) => a != null && Math.abs(a - b) <= e;
const E = 5019200;
// NVDA stored card (A0): 11 filled @158, plan rows 11@158 + 18@140, stop 110, FX 33.76, price 162.85
const nv = { dir: 'long', mult: 1, fx: 33.76, fxSrc: 'Settings rate', fills: [{ qty: 11, px: 158 }], planned: [{ qty: 11, px: 158 }, { qty: 18, px: 140 }], stop: 110, initialStop: 110, price: 162.85, priceAt: '2026-11-13', equity: E, pool: E * 0.5 };
let r = P.calc(nv);
t('nvda held', r.heldQty === 11); t('nvda planned', r.plannedQty === 29); t('nvda avg', r.avgEntry === 158);
t('nvda cost', near(r.cost, 58674.88)); t('nvda value', near(r.value, 60475.98)); t('nvda weight', near(r.weightAcct, 1.2049, 0.001), r.weightAcct);
t('nvda pool weight', near(r.weightPool, 2.4098, 0.001));
t('nvda upnl', near(r.uPnl, 1801.1, 0.5) || near(r.uPnl, 11 * 4.85 * 33.76), r.uPnl); t('nvda upnl%', near(r.uPnlPct, 3.07, 0.01), r.uPnlPct);
t('nvda openRisk', near(r.openRisk, 17825.28)); t('nvda openRisk%', near(r.openRiskPct, 0.3551, 0.001));
t('nvda toStop', near(r.toStop, 19626.38)); t('nvda planned risk (computed) 36,055.68', near(r.plannedRisk, 36055.68), r.plannedRisk); t('nvda planned risk %', near(r.plannedRiskPct, 0.7184, 0.001));
t('nvda R unit 48', r.rUnit === 48); t('nvda R 0.10', near(r.R, 4.85 / 48, 0.001));
r = P.calc(Object.assign({}, nv, { plannedRiskMoney: 36055.68, plannedRiskPct: 0.7183551163532036 })); t('stored plan risk wins', r.plannedRisk === 36055.68 && r.plannedRiskPct === 0.7183551163532036);
// the two illustrative cases from the brief
r = P.calc({ dir: 'long', fx: 33.5, fills: [{ qty: 29, px: 158 }], price: 158, equity: E }); t('29×158×33.5 = 153,497', Math.round(r.cost) === 153497, r.cost);
r = P.calc({ dir: 'long', fx: 33.5, fills: [{ qty: 11, px: 158 }], price: 158, equity: E }); t('11×158×33.5 = 58,223', Math.round(r.cost) === 58223, r.cost);
// planned rows never change held / cost / value
const a = P.calc({ dir: 'long', fx: 33.76, fills: [{ qty: 11, px: 158 }], price: 160, stop: 110, equity: E }), b = P.calc({ dir: 'long', fx: 33.76, fills: [{ qty: 11, px: 158 }], planned: [{ qty: 11, px: 158 }, { qty: 18, px: 140 }, { qty: 50, px: 120 }], price: 160, stop: 110, equity: E });
t('planned rows do not change held/cost/value', a.heldQty === b.heldQty && a.cost === b.cost && a.value === b.value && a.avgEntry === b.avgEntry);
// nothing filled: plan only
r = P.calc({ dir: 'long', fx: 1, planned: [{ qty: 100, px: 50 }], stop: 45, price: 50, equity: 1e6 }); t('plan only: held 0, value null with reason', r.heldQty === 0 && r.value === null && /nothing filled/.test(r.why.value) && r.plannedRisk === 500, r);
// short
r = P.calc({ dir: 'short', fx: 1, fills: [{ qty: 2, px: 100 }], stop: 110, price: 95, equity: 10000 }); t('short upnl +10', r.uPnl === 10 && r.uPnlPct === 5, r); t('short open risk 20', r.openRisk === 20 && near(r.openRiskPct, 0.2)); t('short toStop 30', r.toStop === 30); t('short R = +0.5', near(r.R, 0.5) && r.rUnit === 10);
r = P.calc({ dir: 'short', fx: 1, fills: [{ qty: 2, px: 100 }], stop: 90, price: 95, equity: 10000 }); t('short stop below entry → none', r.openRisk === null && r.openRiskNone && /stop at or beyond entry/.test(r.why.openRisk), r);
// long stop above entry-protected
r = P.calc({ dir: 'long', fx: 1, fills: [{ qty: 10, px: 100 }], stop: 100, price: 105, equity: 1e5 }); t('long stop = entry → none', r.openRiskNone && r.openRisk === null);
r = P.calc({ dir: 'long', fx: 1, fills: [{ qty: 10, px: 100 }], stop: 105, price: 110, equity: 1e5 }); t('long stop beyond entry → none, locked profit in stopPnl', r.openRiskNone && r.stopPnl === 50);
// partial fill 1/2 (Sat lots) + multiplier
r = P.calc({ dir: 'long', mult: 100, fx: 33, fills: [{ qty: 0.02, px: 2000 }], planned: [{ qty: 0.02, px: 2000 }, { qty: 0.03, px: 1990 }], stop: 1980, price: 2010, equity: 1e6 });
t('mult: value 0.02×2010×100×33', near(r.value, 0.02 * 2010 * 100 * 33), r.value); t('mult: open risk', near(r.openRisk, 0.02 * 20 * 100 * 33), r.openRisk); t('1/2 entries', r.entriesDone === 1 && r.entriesTotal === 2); t('plannedQty 0.05', near(r.plannedQty, 0.05, 1e-9));
// missing price
r = P.calc({ dir: 'long', fx: 1, fills: [{ qty: 10, px: 100 }], stop: 90, equity: 1e5 }); t('no price: value/uPnl null + reason', r.value === null && r.uPnl === null && r.why.value === 'no live price' && r.why.price === 'no live price', r.why); t('no price: openRisk kept', r.openRisk === 100);
// missing FX
r = P.calc({ dir: 'long', fx: null, fills: [{ qty: 10, px: 100 }], stop: 90, price: 101, equity: 1e5 }); t('no FX: money null + reason, no assumed rate', r.cost === null && r.value === null && r.openRisk === null && r.why.value === 'no FX' && r.why.openRisk === 'no FX' && r.fx === null, r);
// missing equity
r = P.calc({ dir: 'long', fx: 1, fills: [{ qty: 10, px: 100 }], stop: 90, price: 101 }); t('no equity: weight null + reason', r.weightAcct === null && r.why.weightAcct === 'no account value' && r.value === 1010);
// engine exposure wins over computed loss
r = P.calc({ dir: 'long', fx: 1, fills: [{ qty: 10, px: 100 }], stop: 90, price: 101, equity: 1e4, openRiskMoney: 112 }); t('engine exposure used', r.openRisk === 112 && near(r.openRiskPct, 1.12));
// no stop
r = P.calc({ dir: 'long', fx: 1, fills: [{ qty: 10, px: 100 }], price: 101, equity: 1e4 }); t('no stop: reasons', r.openRisk === null && r.why.openRisk === 'no stop' && r.why.toStop === 'no stop');
console.log(pass + ' passed, ' + fail + ' failed'); process.exit(fail ? 1 : 0);
