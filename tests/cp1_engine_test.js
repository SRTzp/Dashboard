/* CP1 B — market state (pullback) + Compounder size rule 100 / 100 / 75. Run: node tests/cp1_engine_test.js */
const R = require('../risk-engine.js'), A = require('../re1-adapter.js');
let pass = 0, fail = 0;
function ok(name, cond, d) { if (cond) pass++; else { fail++; console.log('FAIL - ' + name + (d !== undefined ? ' :: ' + JSON.stringify(d).slice(0, 400) : '')); } }
const near = (a, b, e) => Math.abs(a - b) <= (e || 1e-6);
const NOW = Date.parse('2026-11-16T10:00:00+07:00');   // Monday
const bk = d => Date.parse(d + 'T00:00:00+07:00');
// RM1 fixture: fundflow ratios in the SMA 20/50 shape (state + inputs_asof, adjusted)
const FFR = (eq, cr, asof) => { const it = (st, a, b) => ({ tf: 'D', sma: [20, 50], adj: true, state: st, up: st === 'green' ? true : st === 'red' ? false : null, days_in_state: 5, bar: asof, inputs_asof: { [a]: asof, [b]: asof }, sma20: 1, sma50: 1, ratio: 1 }); return { ACWI_BIL: it(eq, 'ACWI', 'BIL'), HYG_IEI: it(cr, 'HYG', 'IEI') }; };
const FF = { as_of: '2026-11-17', ratios: FFR('green', 'red', '2026-11-13') };   // one red → 80% (RM1)
function tr(o) { return Object.assign({ port: 'core', bias: 'Long', mult: 1, cur: 'USD', status: 'open', date: '2026-11-10', qty: 10, entry: 100, sl: 95 }, o); }
function src(over) {
  const snap = { id: 's1', bkkDate: '2026-11-16', equity: 5000000, confirmed: true, kind: 'weekly' };
  const S = (e) => Object.assign({ fx: 35, equitySnapshots: [snap], costSettings: { winner: { perUnit: 0.005, min: 1 }, ladder: { perUnit: 0.005, min: 1 }, sat: { perUnit: 7, swapDay: 3 } }, capital: { core: 5000000, satB: 0 } }, e || {});
  const o = { costsOn: true, now: NOW, accounts: [{ id: 'main', name: 'Main', ports: ['core', 'satB'] }, { id: 'fam', name: 'Family', ports: ['core', 'satB'] }],
    books: { main: { settings: S(), trades: [] }, fam: { settings: S({ equitySnapshots: [{ id: 'f1', bkkDate: '2026-11-09', equity: 10000000, confirmed: true }] }), trades: [] } },
    cards: [], ideas: [], ff: FF, specs: {}, portCur: { core: 'THB', satB: 'USD' }, homework: {}, starterOn: false };
  return Object.assign(o, over || {});
}
const spec = { mult: 1, fx: 35, lotStep: 1, minLot: 1 };

/* §0 — NVDA Compounder: Pilot 0.50% × regime 75% = 0.375% (NOT 0.50% × homework 50% = 0.25%) */

const withFF = ff => A.live(src({ ff: { as_of: '2026-11-17', ratios: ff } }), 'main');
const STATES = { 'both green': FFR('green', 'green', '2026-11-13'), 'one red': FFR('green', 'red', '2026-11-13'), 'both red': FFR('red', 'red', '2026-11-13') };
ok('constants live in one place: MARKET_PULLBACK_PCT = 7 · COMP_REGIME_FACTOR 100/100/75', R.MARKET_PULLBACK_PCT === 7 && R.COMP_REGIME_FACTOR.green === 1 && R.COMP_REGIME_FACTOR.oneRed === 1 && R.COMP_REGIME_FACTOR.bothRed === 0.75);
const pil = L => A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: false, side: 'long', entry: 180, stop: 170 }, spec));
const mom = L => A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 180, stop: 170 }, spec));
const eff = {};
for (const k in STATES) { const L = withFF(STATES[k]); eff[k] = { comp: pil(L).effPct, mom: mom(L).effPct, cf: L.regime.compFactor, mf: L.regime.factor }; }
ok('Compounder Pilot: both green full 0.50%', near(eff['both green'].comp, 0.5), eff);
ok('Compounder Pilot: ONE red = full 0.50% (was 75/80%)', near(eff['one red'].comp, 0.5), eff);
ok('Compounder Pilot: both red = 0.375%', near(eff['both red'].comp, 0.375), eff);
ok('Momentum unchanged in all three states (0.40 × 100/80/60%)', near(eff['both green'].mom, 0.4) && near(eff['one red'].mom, 0.32) && near(eff['both red'].mom, 0.24), eff);
const Le = withFF(STATES['both green']); Le.eF = 0.5;
ok('factor = min(regime, emergency): emergency 50% + both green → 0.25%', near(pil(Le).effPct, 0.25));
const Lr = withFF(STATES['both red']); Lr.eF = 0.5;
ok('emergency 50% + both red (75%) → 50% (not 37.5%)', near(pil(Lr).effPct, 0.25));
ok('stale / unknown data keeps a cap (never 100%)', R.regimeFromFundflow(null, NOW).compFactor === 0.75);
/* pullback(): SPY / SET >= 7% below the 52-week high, or exactly one red */
const pb = (spy, set, reds) => R.pullback({ spy: spy, set: set }, reds);
ok('SPY −6.9% → no pullback', pb(-0.069, -0.01, 0).on === false);
ok('SPY −7.0% → pullback (US)', pb(-0.07, -0.01, 0).on === true && pb(-0.07, -0.01, 0).US === true && pb(-0.07, -0.01, 0).TH === false);
ok('SET only −8% → Thai stocks only', pb(-0.01, -0.08, 0).TH === true && pb(-0.01, -0.08, 0).US === false && pb(-0.01, -0.08, 0).on === true);
ok('exactly one red signal → pullback for both', pb(-0.01, -0.01, 1).US && pb(-0.01, -0.01, 1).TH);
ok('both red is NOT the "one red" trigger on its own (index test decides)', pb(-0.01, -0.01, 2).on === false && pb(-0.09, -0.01, 2).US === true);
ok('missing index numbers → unknown, not a pullback', pb(null, undefined, 0).on === false && pb(null, undefined, 0).spyPct === null);
ok('percent values are returned positive for the line', pb(-0.0912, -0.0555, 0).spyPct === 9.12 && pb(-0.0912, -0.0555, 0).setPct === 5.55);
console.log((fail ? 'FAIL ' : 'PASS ') + pass + '/' + (pass + fail) + ' CP1 engine assertions');
process.exit(fail ? 1 : 0);
