/* RM1 — shared new-entry budget modifier: table · fallback · freshness (oldest input) · min() with emergency · no compounding ·
   saved plans / holdings untouched · Compounder limited by risk / total-risk room / value-cap room · Momentum with multiplier + FX · round-down.
   Run: node tests/rm1_engine_test.js */
const R = require('../risk-engine.js'), A = require('../re1-adapter.js');
let pass = 0, fail = 0;
function ok(name, cond, d) { if (cond) pass++; else { fail++; console.log('FAIL - ' + name + (d !== undefined ? ' :: ' + JSON.stringify(d).slice(0, 400) : '')); } }
const near = (a, b, e) => Math.abs(a - b) <= (e || 1e-6);
const NOW = Date.parse('2026-11-16T10:00:00+07:00');   // Monday, Bangkok
const it = (st, a, b, asof, asof2) => ({ tf: 'D', sma: [20, 50], adj: true, state: st, up: st === 'green' ? true : st === 'red' ? false : null, days_in_state: 5, bar: asof, inputs_asof: { [a]: asof, [b]: asof2 || asof }, sma20: 1, sma50: 1, ratio: 1 });
const FFR = (eq, cr, asof, asof2) => ({ ACWI_BIL: it(eq, 'ACWI', 'BIL', asof, asof2), HYG_IEI: it(cr, 'HYG', 'IEI', asof, asof2) });
const FFX = (eq, cr, asof, asof2) => ({ as_of: '2026-11-17', ratios: FFR(eq, cr, asof, asof2) });   // as_of = run date (NOT used for freshness)
const mod = (eq, cr, asof, asof2) => R.regimeFromFundflow(FFX(eq, cr, asof, asof2), NOW);

/* 1 — four combinations (rev 4: 100 / 80 / 80 / 60) */
ok('green/green = 100%', near(mod('green', 'green', '2026-11-16').factor, 1));
ok('green/red = 80%', near(mod('green', 'red', '2026-11-16').factor, 0.8));
ok('red/green = 80%', near(mod('red', 'green', '2026-11-16').factor, 0.8));
ok('red/red = 60%', near(mod('red', 'red', '2026-11-16').factor, 0.6));
ok('fresh known signals are not a fallback', mod('green', 'green', '2026-11-16').fallback === false);
ok('table + fallback are policy settings (override via cfg)', near(R.regimeFromFundflow(FFX('red', 'red', '2026-11-16'), NOW, { regime: { table: { green: { green: 1, red: 0.8 }, red: { green: 0.8, red: 0.4 } }, fallback: 0.7, freshDays: 4, smaFast: 20, smaSlow: 50 } }).factor, 0.4));
ok('SMA periods are policy settings', R.POLICY.regime.smaFast === 20 && R.POLICY.regime.smaSlow === 50 && R.smaLabel() === 'SMA 20/50' && R.smaLabel({ regime: { smaFast: 10, smaSlow: 20 } }) === 'SMA 10/20');

/* 2 — neutral / unavailable / stale → fallback 80%, never 100% */
ok('neutral equity → fallback 80%', near(mod('neutral', 'green', '2026-11-16').factor, 0.8) && mod('neutral', 'green', '2026-11-16').fallback);
ok('unavailable credit → fallback 80%', near(mod('green', 'unavailable', '2026-11-16').factor, 0.8));
ok('both neutral, all green history → still 80% (never 100%)', near(mod('neutral', 'neutral', '2026-11-16').factor, 0.8));
ok('no file / demo → 80% fallback, flagged', near(R.regimeFromFundflow(null, NOW).factor, 0.8) && R.regimeFromFundflow({ demo: true, ratios: FFR('green', 'green', '2026-11-16') }, NOW).fallback);
ok('4 calendar days old (Thu 12 Nov) = fresh → 100%', near(mod('green', 'green', '2026-11-12').factor, 1) && mod('green', 'green', '2026-11-12').fresh);
ok('5 calendar days old (Wed 11 Nov) = stale → 80%', near(mod('green', 'green', '2026-11-11').factor, 0.8) && mod('green', 'green', '2026-11-11').stale);
ok('stale red/red stays 60% (cap only lowers)', near(mod('red', 'red', '2026-11-10').factor, 0.6));
ok('oldest of the four inputs decides (BIL 5 days old, others today → stale)', mod('green', 'green', '2026-11-16', '2026-11-11').stale && mod('green', 'green', '2026-11-16', '2026-11-11').asOf === '2026-11-11');
ok('the file as_of / run date is NOT used', mod('green', 'green', '2026-11-11').asOf === '2026-11-11' && R.regimeFromFundflow({ as_of: '2026-11-16', ratios: FFR('green', 'green', '2026-11-11') }, NOW).stale);
ok('a ratio built with other SMA periods or unadjusted data is never trusted', (() => { const f = FFX('green', 'green', '2026-11-16'); f.ratios.ACWI_BIL.sma = [10, 20]; return near(R.regimeFromFundflow(f, NOW).factor, 0.8) && R.regimeFromFundflow(f, NOW).equity === 'unavailable'; })());
ok('text: modifier + reason', R.regimeText(mod('green', 'red', '2026-11-16')).head === '80% of normal' && R.regimeText(mod('green', 'red', '2026-11-16')).reason === 'equity green, credit red');
ok('text: fallback', R.regimeText(mod('neutral', 'red', '2026-11-16')).head === 'Modifier unavailable · fallback cap 80%');

/* 3 — min() with emergency, never multiplied */
ok('emergency 50% + red/red 60% → 50% (not 30%)', near(R.compFactor(mod('red', 'red', '2026-11-16'), 0.5), 0.5));
ok('emergency 50% + green/green → 50%', near(R.compFactor(mod('green', 'green', '2026-11-16'), 0.5), 0.5));
ok('emergency 0% → 0', R.compFactor(mod('green', 'green', '2026-11-16'), 0) === 0);

/* fixture */
function tr(o) { return Object.assign({ port: 'core', bias: 'Long', mult: 1, cur: 'USD', status: 'open', date: '2026-11-10', qty: 10, entry: 100, sl: 95 }, o); }
function src(ff, over) {
  const snap = { id: 's1', bkkDate: '2026-11-16', equity: 5000000, confirmed: true, kind: 'weekly' };
  const S = { fx: 35, equitySnapshots: [snap], costSettings: { winner: { perUnit: 0.005, min: 1 }, ladder: { perUnit: 0.005, min: 1 }, sat: { perUnit: 7, swapDay: 3 } }, capital: { core: 5000000, satB: 0 } };
  return Object.assign({ costsOn: false, now: NOW, accounts: [{ id: 'main', name: 'Main', ports: ['core', 'satB'] }], books: { main: { settings: S, trades: [] } }, cards: [], ideas: [], ff, specs: {}, portCur: { core: 'THB', satB: 'USD' }, homework: {}, starterOn: false }, over || {});
}
const spec = { mult: 1, fx: 35, lotStep: 1, minLot: 1 };
const EQ = 5000000, DIST = 10 * 35;
const green = FFX('green', 'green', '2026-11-16'), rr = FFX('red', 'red', '2026-11-16'), gr = FFX('green', 'red', '2026-11-16');
const pilot = (L, o) => A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: false, side: 'long', entry: 180, stop: 170 }, spec, o || {}));

/* 4 — sizing: the modifier is applied once to the base budget */
{
  const q = ff => pilot(A.live(src(ff), 'main')).qty;
  const q100 = q(green), q80 = q(gr), q60 = q(rr);
  ok('Compounder pilot qty = floor(equity × 0.50% × modifier ÷ loss/share)', q100 === Math.floor(EQ * 0.005 / DIST) && q80 === Math.floor(EQ * 0.005 * 0.8 / DIST) && q60 === Math.floor(EQ * 0.005 * 0.6 / DIST), [q100, q80, q60]);
  const m60 = pilot(A.live(src(rr), 'main'));
  ok('size line text names the one limiting rule: regime 60%', m60.limit && m60.limit.code === 'regime' && m60.limit.text === 'limited by regime 60%', m60.limit);
  ok('no limiting text at 100%', pilot(A.live(src(green), 'main')).limit === null);
  const Lem = A.live(src(rr), 'main'); Lem.eF = 0.5;
  const mem = pilot(Lem);
  ok('emergency 50% + red/red: effective 50% (min), text names emergency brake', near(mem.effPct, 0.25) && mem.limit.text === 'limited by emergency brake 50%' && mem.qty === Math.floor(EQ * 0.0025 / DIST), [mem.effPct, mem.limit]);
  const L0 = A.live(src(green), 'main'); L0.eF = 0;
  const m0 = pilot(L0);
  ok('emergency 0% → no new risk (qty 0, nothing sold)', m0.qty === 0 && m0.blocked, [m0.qty, m0.reasons]);
  const La = A.live(src(rr), 'main'), r1 = pilot(La), r2 = pilot(La), r3 = pilot(A.live(src(rr), 'main'));
  ok('repeated recalculation of the same plan gives identical qty (no compounding)', r1.qty === r2.qty && r2.qty === r3.qty && near(r1.effPct, r3.effPct), [r1.qty, r2.qty, r3.qty]);
  const rs = 0; void rs;
}

/* 5 — saved plan / holding untouched after a signal change */
{
  const s = src(green); s.books.main.trades = [tr({ id: 'h1', sym: 'NVDA', qty: 40, entry: 100, sl: 95, posGroup: 'h1', sl0: 95 })];
  s.cards = [{ id: 'cH', acct: 'main', ticker: 'NVDA', market: 'US', strategy: 'L', status: 'open', trade_id: 'h1', lots: [{ n: 1, px: 100, qty: 40 }] }];
  const before = JSON.stringify(s.books.main.trades) + JSON.stringify(s.cards);
  const L1 = A.live(s, 'main'); const q1 = L1.ideas[0].tranches.map(t => [t.qty, t.entry, t.stop]);
  s.ff = rr; const L2 = A.live(s, 'main'); const q2 = L2.ideas[0].tranches.map(t => [t.qty, t.entry, t.stop]);
  ok('holding quantities / entries / stops identical after red/red', JSON.stringify(q1) === JSON.stringify(q2));
  ok('stored trades + cards are not written by sizing or a signal change', before === JSON.stringify(s.books.main.trades) + JSON.stringify(s.cards));
  ok('existing position risk is read, not resized (same exposure under both signals)', A.sizeComp(L1, Object.assign({ kind: 'addon', ideaId: L1.ideas[0].id, thesisDone: true, side: 'long', entry: 110, stop: 104 }, spec)).usedPct === A.sizeComp(L2, Object.assign({ kind: 'addon', ideaId: L2.ideas[0].id, thesisDone: true, side: 'long', entry: 110, stop: 104 }, spec)).usedPct);
}

/* 6 — Compounder: limited by risk / total-risk room / value-cap room in turn (add-on, thesis done) */
{
  const hold = (qty, entry, stop) => { const s = src(gr); s.books.main.trades = [tr({ id: 'b1', sym: 'BIGC', qty, entry, sl: stop, posGroup: 'b1', sl0: stop })]; s.cards = [{ id: 'cB', acct: 'main', ticker: 'BIGC', market: 'US', strategy: 'L', status: 'open', trade_id: 'b1', lots: [{ n: 1, px: entry, qty }] }]; return A.live(s, 'main'); };
  const add = (L, o) => A.sizeComp(L, Object.assign({ kind: 'addon', ideaId: L.ideas[0].id, thesisDone: true, side: 'long', entry: 100, stop: 90 }, spec, o || {}));
  // (a) risk-limited: small holding, wide room → qty = risk budget (0.50% × 80%), no room limit text except regime
  const La = hold(10, 100, 95), a = add(La);
  ok('(a) risk qty is the smallest → regime text', a.limits.finalQty === a.limits.riskQty && a.limit && a.limit.code === 'regime' && a.qty === a.limits.riskQty, a.limits);
  // (b) total-risk room: existing ≈0.5% risk → room = 1.00% × 80% − used
  const Lb = hold(70, 100, 90), b = add(Lb);
  ok('(b) total-risk room is the smallest → "limited by total risk" (1.00% × 80% = 0.80%)', b.limit && b.limit.code === 'total_risk' && b.limit.text === 'limited by total risk 0.8%' && b.qty > 0 && b.qty < b.limits.riskQty && b.qty === b.limits.totalRoomQty, [b.limit, b.limits]);
  ok('(b) the cut order is allowed (not blocked)', !b.blocked && b.reasons.length === 0, b.reasons);
  // (c) value-cap room: tight stop → risk qty huge, value room smaller. 12.5% of 5,000,000 = 625,000 THB; existing value 10×100×35 = 35,000
  const Lc = hold(10, 100, 95), c = add(Lc, { entry: 100, stop: 99.5 });
  ok('(c) value-cap room is the smallest → "limited by 12.5% value cap"', c.limit && c.limit.code === 'value_cap' && c.limit.text === 'limited by 12.5% value cap' && c.qty === c.limits.valueRoomQty, [c.limit, c.limits]);
  ok('(c) held value + new value ≤ 12.5% of account, cap NOT scaled by the modifier', (10 * 100 + c.qty * 100) * 35 <= EQ * 0.125 + 1e-6 && near(c.limits.valueCapPct, 12.5));
  const Cg = A.live(src(green), 'main'), Cr = A.live(src(rr), 'main'), tight = { entry: 100, stop: 99.5 };
  ok('(c) value cap identical under 100% and 60% (counts holdings, not × modifier)', pilot(Cg, tight).limits.valueRoomQty === pilot(Cr, tight).limits.valueRoomQty);
  // (d) value cap already full → blocked with its own code
  const Ld = hold(178, 100, 99), d = add(Ld, { stop: 99 });
  ok('(d) value room below one share → COMP_VALUE_CAP blocks', d.reasons.indexOf('COMP_VALUE_CAP') >= 0 && d.blocked, d.reasons);
  // total cap with thesis = 1.00% (RK1; was 1.25%): pilot+addon allowed up to it at 100%
  const L100 = (() => { const s = src(green); s.books.main.trades = [tr({ id: 'k1', sym: 'KKK', qty: 100, entry: 100, sl: 90, posGroup: 'k1', sl0: 90 })]; s.cards = [{ id: 'cK', acct: 'main', ticker: 'KKK', market: 'US', strategy: 'L', status: 'open', trade_id: 'k1', lots: [{ n: 1, px: 100, qty: 100 }] }]; return A.live(s, 'main'); })();
  const k = add(L100); ok('policy: totalCapPct 1.00 · valueCapPct 12.5 · pilot/add-on 0.50', R.POLICY.comp.totalCapPct === 1.00 && R.POLICY.comp.valueCapPct === 12.5 && R.POLICY.comp.pilotPct === 0.5 && k.limits.totalCapPct === 1.00, k.limits);
}

/* 7 — Momentum: budget × modifier, multiplier ≠ 1 and FX, round down */
{
  const mom = (ff, o) => { const L = A.live(src(ff), 'main'); return A.sizeMomentum(L, Object.assign({ entry: 2600, stop: 2590, side: 'long', homeworkDone: true, isFirstEntry: true, mult: 100, fx: 35, lotStep: 0.01, minLot: 0.01 }, o || {})); };
  const m1 = mom(green), m2 = mom(rr);
  const exp = (mod_) => Math.floor(EQ * 0.0040 * mod_ / (10 * 100 * 35) / 0.01 + 1e-9) * 0.01;
  ok('Momentum qty = budget × modifier ÷ (|entry−stop| × multiplier × FX), rounded down to the lot step', near(m1.qty, exp(1), 1e-9) && near(m2.qty, exp(0.6), 1e-9) && m2.qty < m1.qty, [m1.qty, m2.qty, exp(1), exp(0.6)]);
  ok('Momentum text: limited by regime 60%', m2.limit && m2.limit.text === 'limited by regime 60%', m2.limit);
  ok('Momentum never rounds up: risk ≤ budget', m2.money <= EQ * 0.0040 * 0.6 + 1e-6, m2.money);
  const m3 = mom(green, { stop: 2597, lotStep: 1, minLot: 1, mult: 7, fx: 33 });
  ok('Momentum with an odd multiplier + FX, integer lots', m3.qty === Math.floor(EQ * 0.0040 / (3 * 7 * 33)), m3.qty);
}

console.log((fail ? 'FAIL ' : 'PASS ') + pass + '/' + (pass + fail) + ' RM1 engine assertions');
process.exit(fail ? 1 : 0);
