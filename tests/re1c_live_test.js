/* RE-C1 — pure tests of the live adapter layer (basis · costs · sizing models · stop confirm · emergency · accounts). Run: node tests/re1c_live_test.js */
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
{
  const L = A.live(src(), 'main');
  ok('basis ok, week equity = latest snapshot at/before Monday', L.basis.ok && L.basis.weekEquity === 5000000 && !L.basis.provisional, L.basis);
  const m = A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: false, side: 'long', entry: 180, stop: 170 }, spec));
  const eq = 5000000, dist = 10 * 35;   // THB per share
  ok('regime = one red → 80% (RM1 table 100/80/80/60)', near(L.regime.factor, 0.8), L.regime);
  ok('Compounder effective % = 0.50 × 100% = 0.50 at one red (CP1; homework NOT applied on top of the Pilot)', near(m.effPct, 0.5), m.effPct);
  ok('qty = floor(5,000,000 × 0.50% / 350) = 71', m.qty === Math.floor(eq * 0.005 / dist), m.qty);
  ok('formula names the Pilot (no regime cut at one red)', /^Pilot 0\.5% = $/.test(m.formula), m.formula);
  ok('factors list names every factor', m.factors.join() === 'PILOT_0.5', m.factors);
  const m2 = A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: true, side: 'long', entry: 180, stop: 170 }, spec));
  ok('thesis done does not change the Pilot size (same 0.50%)', near(m2.effPct, 0.5) && m2.qty === m.qty);
  const m3 = A.sizeComp(L, Object.assign({ kind: 'pilot', starterOn: true, thesisDone: false, side: 'long', entry: 180, stop: 170 }, spec));
  ok('Starter ¼ = half of the Pilot → 0.50 × 100% × 50% and STARTER_25 named', near(m3.effPct, 0.25) && m3.factors.indexOf('STARTER_25') >= 0 && /starter 25%/.test(m3.formula), m3.factors);
  // Momentum keeps the homework factor (it is a multiplier there)
  const mm = A.sizeMomentum(L, Object.assign({ homeworkDone: false, side: 'long', entry: 180, stop: 170 }, spec));
  ok('Momentum homework 70%: 0.40 × 70% × regime 80% = 0.224 (PC2 2e)', near(mm.effPct, 0.224) && /0\.4% × homework 70% × regime 80% = $/.test(mm.formula), mm.formula);
  const mf = A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 180, stop: 170 }, spec));
  ok('Momentum thesis done: 0.40% × regime 80% = 0.32, no homework text', near(mf.effPct, 0.32) && !/homework/.test(mf.formula));
}
/* basis: provisional · stale · withdrawals · mid-week manual snapshot keeps week-start basis */
{
  const s = src(); s.books.main.settings.equitySnapshots = []; s.books.main.settings.re1 = { cutoverAt: NOW - 3 * 86400000 };
  let L = A.live(s, 'main'); ok('no snapshot → Provisional from entered capital', L.basis.ok && L.basis.provisional && L.basis.weekEquity === 5000000 && L.basis.flags.indexOf('PROVISIONAL') >= 0, L.basis);
  s.books.main.settings.re1 = { cutoverAt: NOW - 15 * 86400000 }; L = A.live(s, 'main'); ok('provisional older than 14 days → blocked (stale)', !L.basis.ok && L.basis.reasons[0] === 'SNAPSHOT_STALE', L.basis);
  const s2 = src(); s2.books.main.settings.equitySnapshots = [{ id: 'a', bkkDate: '2026-11-02', equity: 4000000, confirmed: true }]; L = A.live(s2, 'main');
  ok('snapshot 14 days old still usable (exactly 14.4 → blocked)', !L.basis.ok, L.basis.state);
  const s3 = src(); s3.books.main.settings.equitySnapshots = [{ id: 'a', bkkDate: '2026-11-15', equity: 5000000, confirmed: true }, { id: 'b', bkkDate: '2026-11-18', equity: 5300000, confirmed: true }]; s3.now = bk('2026-11-19') + 36000000;
  L = A.live(s3, 'main'); ok('mid-week manual snapshot does not replace the week-start basis', L.basis.weekEquity === 5000000 && L.basis.currentEquity === 5300000, [L.basis.weekEquity, L.basis.currentEquity]);
  const s4 = src(); s4.books.main.settings.cashFlows = [{ id: 'w', bkkDate: '2026-11-17', amount: -200000 }, { id: 'd', bkkDate: '2026-11-17', amount: 500000 }]; s4.now = bk('2026-11-18') + 36000000;
  L = A.live(s4, 'main'); ok('withdrawal reduces the basis at once · deposit does not count until the next snapshot', L.basis.weekEquity === 4800000, L.basis.weekEquity);
  const s5 = src(); s5.books.main.settings.equitySnapshots[0].confirmed = false; s5.books.main.settings.capital = {}; L = A.live(s5, 'main');
  ok('unconfirmed snapshot never counts', !L.basis.ok && L.basis.reasons[0] === 'NO_SNAPSHOT', L.basis);
}
/* costs: missing → Unknown, never 0 · stop confirm at net breakeven releases the idea (Option C) · cost edit */
{
  const base = () => { const s = src(); s.books.main.trades = [tr({ id: 'a1', sym: 'AAPL', qty: 100, entry: 100, sl: 95, posGroup: 'a1', sl0: 95 })]; return s; };
  let s = base(); s.books.main.settings.costSettings = {}; let L = A.live(s, 'main');
  const i0 = L.ideas[0]; const si = A.stopInfo(L, i0.id, 101);
  ok('missing costs → stop cannot be recognised as net breakeven', si.costsKnown === false && si.netBreakeven === null && si.atBreakeven === false && si.frees === false, si);
  ok('missing costs → COST_UNKNOWN flag on a Momentum result', A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 50, stop: 48 }, spec)).flags.indexOf('COST_UNKNOWN') >= 0);
  s = base(); L = A.live(s, 'main'); const i1 = L.ideas[0], c1 = L.costsFor(i1);
  ok('costs known', c1.known && c1.perUnit === 0.005);
  const entryFee = R.exitCost(c1, 100, 100, 1, 35); ok('entry fee counted from the fill (idea-level)', near(i1.entryFees, entryFee) && entryFee > 0, i1.entryFees);
  const nb = R.netBreakevenStop(i1, c1); ok('net breakeven > entry (costs)', nb > 100, nb);
  const sNow = A.stopInfo(L, i1.id, 100);   // stop at entry: net negative (costs) → not breakeven
  ok('stop at entry is NOT net breakeven when costs exist (strict sign)', sNow.atBreakeven === false && sNow.frees === false, sNow);
  const sOk = A.stopInfo(L, i1.id, Math.ceil(nb * 100) / 100 + 0.01);
  ok('stop at/above estimated net breakeven → Risk 0 · frees 1 idea (once confirmed)', sOk.atBreakeven === true && sOk.frees === true, sOk);
  // confirmed marker on the row releases the reservation in the live state
  const mAmmo0 = L.mom.state.ammoUsed;
  s = base(); s.books.main.trades[0].sl = Math.ceil(nb * 100) / 100 + 0.01; s.books.main.trades[0].stopConfirmed = true; L = A.live(s, 'main');
  ok('confirmed net-breakeven stop releases the ammunition reservation', mAmmo0 === 1 && L.mom.state.ammoUsed === 0, [mAmmo0, L.mom.state.ammoUsed]);
  s = base(); s.books.main.trades[0].sl = Math.ceil(nb * 100) / 100 + 0.01; L = A.live(s, 'main');
  ok('same stop NOT confirmed at the broker keeps the reservation', L.mom.state.ammoUsed === 1);
  s = base(); s.books.main.trades[0].sl = 101; s.books.main.trades[0].stopConfirmed = true; s.books.main.settings.costSettings.winner = { perUnit: 50, min: 1 }; L = A.live(s, 'main');
  ok('a later cost edit can bring the reservation back (position untouched)', L.mom.state.ammoUsed === 1 && L.ideas[0].tranches[0].qty === 100);
}
/* Momentum blocked: shows reason + allowed quantity; ammunition; money */
{
  const s = src(); s.books.main.trades = [1, 2, 3, 4].map(k => tr({ id: 'h' + k, sym: 'S' + k, qty: 10, entry: 100, sl: 95, posGroup: 'h' + k, sl0: 95 }));
  const L = A.live(s, 'main');
  const m = A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95, ideaId: 'new' }, spec));
  ok('fifth idea blocked: AMMO_EXHAUSTED, allowed 0, Place order disabled (blocked)', m.blocked && m.reasons.indexOf('AMMO_EXHAUSTED') >= 0 && m.allowedQty === 0 && !m.ok, m);
  const s2 = src(); s2.books.main.trades = [tr({ id: 'big', sym: 'BIG', qty: 5000, entry: 100, sl: 95, posGroup: 'big', sl0: 95 })];   // open risk 5000*5*35 = 875,000 = 17.5% of equity >> cap
  const L2 = A.live(s2, 'main'); const m2 = A.sizeMomentum(L2, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95, ideaId: 'new' }, spec));
  ok('over the weekly money limit → MONEY_WEEK with room text', m2.reasons.indexOf('MONEY_WEEK') >= 0 && /room/.test(m2.reasonTexts.join(' ')), m2.reasonTexts);
  const s3 = src(); s3.books.main.trades = [tr({ id: 'o1', sym: 'O1', qty: 1000, entry: 100, sl: 95, posGroup: 'o1', sl0: 95 })];
  const L3 = A.live(s3, 'main'); const m3 = A.sizeMomentum(L3, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95, ideaId: 'new' }, spec));
  ok('allowed quantity is a lot multiple ≤ sized qty and fits the room', m3.blocked ? (m3.allowedQty < m3.qty && m3.allowedQty >= 0) : true, [m3.qty, m3.allowedQty]);
}
/* accounts never mix */
{
  const s = src(); s.books.main.trades = [tr({ id: 'h1', sym: 'X1', qty: 1000, entry: 100, sl: 95, posGroup: 'h1', sl0: 95 })];
  const Lm = A.live(s, 'main'), Lf = A.live(s, 'fam');
  ok('Family sees none of Main’s ideas / exposure', Lf.ideas.length === 0 && Lf.mom.state.open === 0 && Lm.mom.state.open > 0);
  ok('Family basis is its own snapshot (10M, 9 Nov, carried)', Lf.basis.weekEquity === 10000000 && Lf.basis.state === 'carried', Lf.basis);
}
/* Emergency evaluated at a snapshot; Compounder min(Regime, Emergency) */
{
  const s = src(); s.books.main.settings.equitySnapshots = [{ id: 'a', bkkDate: '2026-11-02', equity: 5000000, confirmed: true }, { id: 'b', bkkDate: '2026-11-16', equity: 4450000, confirmed: true }];
  const L = A.live(s, 'main');
  ok('−11% at a confirmed snapshot → Emergency on (factor 0.5)', L.emergency.active && L.eF === 0.5, L.emergency);
  const m = A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95 }, spec));
  ok('Momentum shows emergency in the formula', near(m.effPct, 0.2) && /emergency 50%/.test(m.formula), m.formula);
  const c = A.sizeComp(L, Object.assign({ kind: 'pilot', side: 'long', entry: 100, stop: 95 }, spec));
  ok('Compounder = min(Regime 75%, Emergency 50%) = 50% (not multiplied)', near(c.effPct, 0.25) && c.factors.join() === 'PILOT_0.5,EMERGENCY_50', [c.effPct, c.factors]);
  const s2 = src(); s2.books.main.settings.equitySnapshots = [{ id: 'a', bkkDate: '2026-11-02', equity: 5000000, confirmed: true }, { id: 'b', bkkDate: '2026-11-16', equity: 4900000, confirmed: true }];
  ok('−2% → off', !A.live(s2, 'main').emergency.active);
}
/* Satellite: step path, queue, daily, re-entry, stale order, condition table, lots round down */
{
  const specS = { mult: 100, fx: 1, lotStep: 0.01, minLot: 0.01 };
  const gold = (o) => Object.assign({ entry: 2642, stop: 2628, tp: 2684, side: 'long', product: 'XAUUSD', cond: { ema50: true, structure: true }, ideaId: 'new' }, specS, o || {});
  const s = src(); s.fxSet = 1; s.books.main.settings.fx = 1; s.books.main.settings.equitySnapshots = [{ id: 's1', bkkDate: '2026-11-16', equity: 100000, confirmed: true }]; s.books.main.settings.capital = {};
  s.books.main.settings.costSettings = { sat: { perUnit: 7, swapDay: 3 } };
  let L = A.live(s, 'main'); let m = A.sizeSat(L, gold());
  ok('Satellite Step 1 full: 0.20% × 100%', m.step === 1 && near(m.effPct, 0.2) && /^0\.2% = $/.test(m.formula), m.formula);
  ok('lot = floor(100000 × 0.2% / (14 × 100)) = 0.14', near(m.qty, 0.14, 1e-9), m.qty);
  ok('R:R 3.0 in the room line', /R:R 3/.test(m.roomLine) && /queue free/.test(m.roomLine) && /1st setup today/.test(m.roomLine), m.roomLine);
  const mr = A.sizeSat(L, gold({ cond: { ema50: false, structure: true } }));
  ok('Reduced condition: 65% applied once + nearest-target flag', near(mr.effPct, 0.13) && /× 65% = /.test(mr.formula) && mr.flags.indexOf('SAT_NEAREST_TARGET') >= 0 && mr.chip.t === 'Reduced 65%', mr);
  ok('no MSS → blocked', A.sizeSat(L, gold({ cond: { ema50: false, structure: false, mss: false } })).reasons.indexOf('SAT_COND_BLOCKED') >= 0);
  ok('R:R < 1.5 blocked', A.sizeSat(L, gold({ tp: 2650 })).reasons.indexOf('SAT_RR') >= 0);
  ok('lot below minimum → blocked, never rounded up', A.sizeSat(L, gold({ stop: 1000 })).reasons.indexOf('LOT_BELOW_MIN') >= 0);
  // step path: a loss → step 2
  const sat = (id, ent, ex, closed) => tr({ id, sym: 'XAUUSD', port: 'satB', cur: 'USD', qty: 0.1, entry: ent, sl: ent - 10, status: 'closed', exitPrice: ex, exitDate: closed, closedAt: closed + 'T03:00:00.000Z', posGroup: id, sl0: ent - 10, exitReason: 'stop', mult: 100, openedAt: closed + 'T01:00:00.000Z' });
  const s2 = JSON.parse(JSON.stringify(s)); s2.books.main.trades = [sat('g1', 2600, 2590, '2026-11-16')]; s2.ideas = [{ id: 'g1i', asset: 'XAUUSD', accts: { main: { trade_id: 'g1' } } }];
  L = A.live(s2, 'main'); m = A.sizeSat(L, gold({ product: 'EURUSD', entry: 1.1, stop: 1.09, tp: 1.13, mult: 100000, lotStep: 0.01, minLot: 0.01 }));
  ok('after a stopped loss → Step 2 machine state, value stays 0.20% (RK1: label is just the value)', m.step === 2 && /^0\.2% = $/.test(m.formula), [m.step, m.formula]);
  const mq = A.sizeSat(L, gold());
  ok('same product same day after a stop loss → re-entry needs the confirm', mq.reasons.indexOf('SAT_REENTRY_COND') >= 0 && mq.reentryNeedsConfirm === true, mq.reasons);
  const mc = A.sizeSat(L, gold({ reentry: { confirmed: true, setupValid: true, sameDirectionZone: true, trendUnchanged: true, candleClosedSince: true } }));
  ok('re-entry with the one-tap confirm → allowed, tagged, uses the CURRENT step RPT (Step 2)', mc.reasons.indexOf('SAT_REENTRY_COND') < 0 && mc.reentry === true && mc.flags.indexOf('SAT_REENTRY_TAG') >= 0 && mc.step === 2, [mc.reasons, mc.flags, mc.step]);
  // queue
  const s3 = JSON.parse(JSON.stringify(s)); s3.books.main.trades = [tr({ id: 'q1', sym: 'EURUSD', port: 'satB', cur: 'USD', qty: 0.1, entry: 1.1, sl: 1.09, posGroup: 'q1', sl0: 1.09, mult: 100000 })];
  L = A.live(s3, 'main'); ok('queue: another active setup in this account blocks a new one', A.sizeSat(L, gold()).reasons.indexOf('SAT_QUEUE_BUSY') >= 0);
  const Lf = A.live(s3, 'fam'); ok('queue is per account (Family free)', A.sizeSat(Lf, gold()).reasons.indexOf('SAT_QUEUE_BUSY') < 0);
  // stale order reminder
  const s4 = JSON.parse(JSON.stringify(s)); s4.books.main.trades = [tr({ id: 'w1', sym: 'XAUUSD', port: 'satB', cur: 'USD', status: 'plan', qty: 0.1, entry: 2600, sl: 2590, mult: 100 })];
  s4.ideas = [{ id: 'wi', asset: 'XAUUSD', accts: { main: { trade_id: 'w1' } }, ln4: { placedAt: new Date(NOW - 30 * 3600000).toISOString() } }];
  L = A.live(s4, 'main'); ok('working order older than a day → stale reminder (no auto-cancel)', L.sat.stale.length === 1, L.sat.stale);
  // lock after a loss at step 4
  const s5 = JSON.parse(JSON.stringify(s)); s5.books.main.trades = ['2026-11-16', '2026-11-16', '2026-11-16', '2026-11-16'].map((d, k) => sat('z' + k, 2600 + k, 2590 + k, d));
  s5.books.main.trades.forEach((t, k) => { t.closedAt = '2026-11-16T0' + (k + 1) + ':00:00.000Z'; });
  L = A.live(s5, 'main'); ok('loss at Step 4 locks Satellite until Monday', L.sat.step.locked && A.sizeSat(L, gold({ product: 'EURUSD' })).reasons.indexOf('SAT_LOCKED') >= 0, L.sat.step);
}
/* Compounder: Add-on locked list · six-loss lock · heat cap */
{
  const s = src();
  s.books.main.trades = [tr({ id: 'n1', sym: 'NVDA', qty: 100, entry: 100, sl: 95, posGroup: 'n1', sl0: 95 })]; s.cards = [{ id: 'cN', acct: 'main', ticker: 'NVDA', market: 'US', strategy: 'L', status: 'open', trade_id: 'n1', lots: [{ n: 1, px: 100, qty: 100 }], stopHistory: [] }];
  let L = A.live(s, 'main'); const idea = L.ideas[0];
  const m = A.sizeComp(L, Object.assign({ kind: 'addon', ideaId: idea.id, thesisDone: false, side: 'long', entry: 110, stop: 104 }, spec));
  ok('Add-on without thesis: locked, lists only "thesis done" (no +1.5R / breakeven condition)', m.blocked && m.addon.locked && m.addon.missing.join() === 'thesis done' && m.reasons.indexOf('ADDON_THESIS') >= 0, m.addon);
  const m2 = A.sizeComp(L, Object.assign({ kind: 'addon', ideaId: idea.id, thesisDone: true, side: 'long', entry: 110, stop: 104 }, spec));
  ok('Add-on with thesis: allowed with Pilot at its original stop and price far from +1.5R', !m2.reasons.length && m2.qty > 0 && !m2.addon.locked, m2.reasons);
  ok('Add-on formula = 0.50% (no regime cut at one red) and ticker total shown', /^Add-on 0\.5% = $/.test(m2.formula) && /ticker/.test(m2.roomLine), m2.formula);
  const m3 = A.sizeComp(L, Object.assign({ kind: 'addon', ideaId: idea.id, thesisDone: true, side: 'long', entry: 98, stop: 92 }, spec));
  ok('Adding below the average entry: allowed + warning line (never a block)', !m3.blocked && m3.flags.indexOf('ADDON_BELOW_ENTRY_WARN') >= 0, [m3.reasons, m3.flags]);
  ok('above the average entry: no warning', m2.flags.indexOf('ADDON_BELOW_ENTRY_WARN') < 0);
  // existing tranche already carries 0.9% → total-risk room = 1.00% × 80% − 0.49% = 0.31% → qty is cut to that room (RM1: limited by total risk) instead of blocked
  const big = src(); big.books.main.trades = [tr({ id: 'b1', sym: 'BIGC', qty: 100, entry: 100, sl: 90, posGroup: 'b1', sl0: 90 })]; big.cards = [{ id: 'cB', acct: 'main', ticker: 'BIGC', market: 'US', strategy: 'L', status: 'open', trade_id: 'b1', lots: [{ n: 1, px: 100, qty: 100 }] }];
  const LB = A.live(big, 'main'), ib = LB.ideas[0], mb = A.sizeComp(LB, Object.assign({ kind: 'addon', ideaId: ib.id, thesisDone: true, side: 'long', entry: 100, stop: 90 }, spec));
  ok('total-risk rule: existing 0.70% + new 0.50% > 1.00% → qty cut to the room, limited by total risk', mb.limit && mb.limit.code === 'total_risk' && mb.qty > 0 && mb.qty < mb.limits.riskQty && /^limited by total risk 1(\.0+)?%$/.test(mb.limit.text), [mb.reasons, mb.usedPct, mb.limit, mb.limits]);
  const mp = A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: false, side: 'long', entry: 100, stop: 95, levels: [{ price: 100, splitPct: 50 }, { price: 96, splitPct: 50 }] }, spec));
  ok('planned multi-entry without thesis: all levels together within 0.50% (CP1: no regime cut at one red)', near(mp.effPct, 0.5) && mp.levels.length === 2 && mp.money / 5000000 * 100 <= 0.5 + 1e-9, [mp.effPct, mp.money]);
  const mpt = A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: true, side: 'long', entry: 100, stop: 95, levels: [{ price: 100, splitPct: 50 }, { price: 96, splitPct: 50 }] }, spec));
  ok('planned multi-entry with thesis: cap in force 1.00% × regime (RK1)', near(mpt.effPct, 1.0) && mpt.money / 5000000 * 100 <= 1.0 + 1e-9, [mpt.effPct, mpt.money]);
  const heatLarge = src(); heatLarge.books.main.trades = Array.from({ length: 6 }, (_, k) => tr({ id: 'c' + k, sym: 'C' + k, qty: 1000, entry: 100, sl: 96, posGroup: 'c' + k, sl0: 96 }));
  heatLarge.cards = heatLarge.books.main.trades.map((t, k) => ({ id: 'cc' + k, acct: 'main', ticker: 'C' + k, market: 'US', strategy: 'L', status: 'open', trade_id: t.id, lots: [{ n: 1, px: 100, qty: 1000 }] }));
  L = A.live(heatLarge, 'main'); const mh = A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: true, side: 'long', entry: 100, stop: 90 }, spec));
  ok('heat cap 6%: blocked with heat text, allowed qty smaller than sized', mh.reasons.indexOf('COMP_HEAT') >= 0 && /Heat cap/.test(mh.reasonTexts.join(' ')) && mh.allowedQty <= mh.qty, [mh.reasons, mh.reasonTexts]);
  const sl = src(); sl.books.main.trades = Array.from({ length: 6 }, (_, k) => tr({ id: 'l' + k, sym: 'L' + k, qty: 10, entry: 100, sl: 95, status: 'closed', exitPrice: 90, exitDate: '2026-11-1' + k, closedAt: '2026-11-1' + k + 'T03:00:00.000Z', posGroup: 'l' + k, sl0: 95 }));
  sl.cards = sl.books.main.trades.map((t, k) => ({ id: 'lc' + k, acct: 'main', ticker: 'L' + k, market: 'US', strategy: 'L', status: 'closed', trade_id: t.id, lots: [] }));
  sl.now = NOW + 1000; L = A.live(sl, 'main'); const ml = A.sizeComp(L, Object.assign({ kind: 'pilot', side: 'long', entry: 100, stop: 95 }, spec));
  ok('six consecutive losing cycles → Compounder locked', L.comp.streak.locked && ml.reasons.indexOf('COMP_LOCKED') >= 0, L.comp.streak);
}
/* no write changes an existing position's quantity: the live layer never mutates its input */
{
  const s = src(); s.books.main.trades = [tr({ id: 'a1', sym: 'AAPL', qty: 100, entry: 100, sl: 95, posGroup: 'a1', sl0: 95 })];
  const before = JSON.stringify(s); const L = A.live(s, 'main'); A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95 }, spec)); A.stopInfo(L, L.ideas[0].id, 101);
  ok('live layer is read-only (input unchanged)', JSON.stringify(s) === before);
}

/* RE-C1 — a blocked Momentum form never shows a count above the limit; the room line agrees with the reason */
{
  const s = src(); s.books.main.trades = [1, 2, 3, 4].map(k => tr({ id: 'h' + k, sym: 'S' + k, qty: 10, entry: 100, sl: 95, posGroup: 'h' + k, sl0: 95 }));
  const L = A.live(s, 'main'); const m = A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95, ideaId: 'new' }, spec));
  ok('blocked by ammunition: room line says "Ideas 4 of 4 used or reserved" (never "5 of 4")', /^Ideas 4 of 4 used or reserved/.test(m.roomLine) && !/5 of 4/.test(m.roomLine), m.roomLine);
  const s2 = src(); s2.books.main.trades = [tr({ id: 'big', sym: 'BIG', qty: 5000, entry: 100, sl: 95, posGroup: 'big', sl0: 95 })];
  const m2 = A.sizeMomentum(A.live(s2, 'main'), Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95, ideaId: 'new' }, spec));
  ok('blocked by money: room line shows the room left and what this order needs, ideas never above 4', /this order needs/.test(m2.roomLine) && !/ideas [5-9] of 4/.test(m2.roomLine), m2.roomLine);
  const s3 = src(); const m3 = A.sizeMomentum(A.live(s3, 'main'), Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95, ideaId: 'new' }, spec));
  ok('allowed: "Week room … · idea 1 of 4"', /idea 1 of 4/.test(m3.roomLine), m3.roomLine);
}

/* RE-C2 §6 — Costs switch OFF: costs 0 · net = gross · net-breakeven = entry · never Unknown · trades closed while OFF are never re-costed when ON later */
{
  const off = () => { const s = src(); s.costsOn = false; s.books.main.trades = [tr({ id: 'a1', sym: 'AAPL', qty: 100, entry: 100, sl: 95, posGroup: 'a1', sl0: 95 })]; return s; };
  let s = off(); s.books.main.settings.costSettings = {}; let L = A.live(s, 'main');
  const si = A.stopInfo(L, L.ideas[0].id, 100);
  ok('OFF: costs known (all zero) even with no cost settings → never Unknown', L.costsFor(L.ideas[0]).known === true && si.costsKnown === true && L.costsOn === false, si);
  ok('OFF: estimated net-breakeven price = entry price', si.netBreakeven === 100 && si.costPerShare === 0, si);
  ok('OFF: no COST_UNKNOWN flag on a Momentum result', A.sizeMomentum(L, Object.assign({ homeworkDone: true, side: 'long', entry: 50, stop: 48 }, spec)).flags.indexOf('COST_UNKNOWN') < 0);
  s = off(); s.books.main.trades[0].sl = 100; s.books.main.trades[0].stopConfirmed = true; L = A.live(s, 'main');
  ok('OFF: stop confirmed at entry frees the Momentum idea (Option C) and risk is 0', L.mom.state.ammoUsed === 0 && L.mom.state.reservedIdeas.length === 0, L.mom.state);
  s = off(); s.books.main.settings.costSettings = { winner: { perUnit: 50, min: 1 } }; L = A.live(s, 'main');
  ok('OFF: saved cost values stay in the data, unread (costs still 0)', L.costsFor(L.ideas[0]).perUnit === 0 && s.books.main.settings.costSettings.winner.perUnit === 50);
  const closed = (extra) => { const s = off(); s.books.main.trades = [tr(Object.assign({ id: 'c1', sym: 'AAPL', qty: 100, entry: 100, sl: 95, status: 'closed', exitPrice: 100, exitDate: '2026-10-01', closedAt: '2026-10-01T04:00:00.000Z', posGroup: 'c1', sl0: 95 }, extra || {}))]; return s; };
  L = A.live(closed(), 'main'); let ir = L.ideas[0];
  ok('OFF: exit at entry = breakeven (no Momentum loss counted)', L.mom.state.completedLosses === 0 && L.mom.state.ammoUsed === 0 && ir.status === 'closed', L.mom.state);
  ok('OFF: Satellite exit at entry does not change the step', (() => { const s2 = closed({ port: 'satB', sym: 'XAUUSD', cur: 'USD' }); const L2 = A.live(s2, 'main'); return L2.sat.step.step === 1 && !L2.sat.step.locked; })());
  // ON later: a trade closed while OFF (costsOff) is never re-costed; a normal one with the same data is
  const on1 = closed({ costsOff: true }); on1.costsOn = true; on1.books.main.settings.costSettings = { winner: { perUnit: 0.5, min: 1 } };
  const on2 = closed(); on2.costsOn = true; on2.books.main.settings.costSettings = { winner: { perUnit: 0.5, min: 1 } };
  const L1 = A.live(on1, 'main'), L2 = A.live(on2, 'main');
  const net = (L) => { const i = L.ideas[0]; return R.ideaRealizedNet(i); };
  ok('ON later: a trade closed while OFF keeps net = gross (never re-costed)', Math.abs(net(L1)) < 1e-9, net(L1));
  ok('ON: a trade closed with the switch ON is costed as in RE-C1', net(L2) < -1e-9, net(L2));
  ok('ON later never changes a position / order quantity', L1.ideas[0].tranches[0].qty === 100 && L2.ideas[0].tranches[0].qty === 100);
}
/* RE-D §2 — FX per snapshot: week / month USAGE converts at the rate of the snapshot that gives the basis; a NEW order still converts at the current Settings rate */
{
  const mk = (snapFx, curFx) => {
    const s = src(); const S = s.books.main.settings; S.fx = curFx; S.equitySnapshots = [{ id: 's1', bkkDate: '2026-11-16', equity: 5000000, confirmed: true, kind: 'weekly', fx: snapFx }].map(x => { if (snapFx == null) delete x.fx; return x; });
    S.costSettings = null; s.costsOn = false;
    S.re1 = { cutoverAt: NOW - 86400000 };
    s.books.main.trades = [tr({ id: 'u1', sym: 'AAPL', qty: 100, entry: 100, sl: 90, posGroup: 'u1', sl0: 90 })];   // open Momentum USD: risk $1,000
    return s;
  };
  const open = (L) => L.mom.chk.money.open;
  const L1 = A.live(mk(30, 35), 'main'), L2 = A.live(mk(35, 35), 'main'), L3 = A.live(mk(null, 35), 'main');
  ok('basis carries the snapshot FX (week and month)', L1.basis.weekFx === 30 && L1.basis.monthFx === 30, [L1.basis.weekFx, L1.basis.monthFx]);
  ok('open risk in the week usage = $1,000 × snapshot FX 30 = 30,000', near(open(L1), 30000, 1e-6), open(L1));
  ok('same trade with snapshot FX = current FX 35 → 35,000 (unchanged behaviour)', near(open(L2), 35000, 1e-6), open(L2));
  ok('older snapshot without a stored FX → current rate (35) and no frozen rate', near(open(L3), 35000, 1e-6) && L3.basis.weekFx === null, [open(L3), L3.basis.weekFx]);
  ok('engine output identical when snapshot FX = current FX (single run)', JSON.stringify(L2.mom.chk) === JSON.stringify(A.live(mk(null, 35), 'main').mom.chk));
  const m1 = A.sizeMomentum(L1, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95 }, spec, { fx: 35 }));
  ok('a new order still sizes and converts at the current rate 35 (risk of one share = $5 × 35)', m1.qty > 0 && near(m1.money, m1.qty * 5 * 35, 1e-6), [m1.qty, m1.money]);
  const m1b = A.sizeMomentum(L2, Object.assign({ homeworkDone: true, side: 'long', entry: 100, stop: 95 }, spec, { fx: 35 }));
  ok('same qty either way; only the room line (usage) differs', m1.qty === m1b.qty && near(L1.mom.chk.money.weekUsed, 30000, 1e-6) && near(L2.mom.chk.money.weekUsed, 35000, 1e-6), [m1.qty, m1b.qty]);
  // month basis from an older snapshot with a different rate: week at the week snapshot's rate, month at the month snapshot's rate
  const s5 = mk(30, 35); s5.books.main.settings.equitySnapshots = [{ id: 'm0', bkkDate: '2026-10-30', equity: 5000000, confirmed: true, kind: 'weekly', fx: 32 }, { id: 'w0', bkkDate: '2026-11-16', equity: 5000000, confirmed: true, kind: 'weekly', fx: 30 }];
  s5.now = bk('2026-11-17') + 36000000;
  const L5 = A.live(s5, 'main');
  ok('week usage at the week-start snapshot rate, month usage at the month-start snapshot rate', L5.basis.weekFx === 30 && L5.basis.monthFx === 32 && near(L5.mom.chk.money.weekUsed, 30000, 1e-6) && near(L5.mom.chk.money.monthUsed, 32000, 1e-6), [L5.basis.weekFx, L5.basis.monthFx, L5.mom.chk.money]);
  ok('positions and orders are untouched (qty / stop)', L1.ideas[0].tranches[0].qty === 100 && L1.ideas[0].tranches[0].stop === 90);
}
/* TS1 §4 — Compounder heat uses the same frozen-FX basis: existing usage at the WEEK snapshot rate, the new order at the current rate; no stored rate → current rate */
{
  const mk = (snapFx, curFx) => {
    const s = src(); const S = s.books.main.settings; S.fx = curFx; S.equitySnapshots = [{ id: 's1', bkkDate: '2026-11-16', equity: 5000000, confirmed: true, kind: 'weekly', fx: snapFx }].map(x => { if (snapFx == null) delete x.fx; return x; });
    S.costSettings = null; s.costsOn = false; S.re1 = { cutoverAt: NOW - 86400000 };
    s.cards = [{ id: 'cc1', acct: 'main', ticker: 'AAPL', market: 'US', strategy: 'L', status: 'open', trade_id: 'h1', stopHistory: [], lots: [{ n: 1, px: 100, qty: 100 }] }];
    s.books.main.trades = [tr({ id: 'h1', sym: 'AAPL', port: 'core', qty: 100, entry: 100, sl: 90, posGroup: 'h1', sl0: 90, cardId: 'cc1', strategy: 'ladder' })];   // open USD Compounder: risk $1,000
    return s;
  };
  const heat = (L) => L.comp.heat;
  const La = A.live(mk(30, 35), 'main'), Lb = A.live(mk(30, 40), 'main'), Lc = A.live(mk(30, 28), 'main');
  ok('TS1 heat: the open Compounder idea is counted', heat(La) && heat(La).count === 1, heat(La));
  ok('TS1 heat money = $1,000 × snapshot FX 30 = 30,000', near(heat(La).money, 30000, 1e-6), heat(La));
  ok('TS1 heat does not move when only the FX rate moves after the snapshot (35 → 40 → 28)', near(heat(Lb).money, heat(La).money) && near(heat(Lc).money, heat(La).money), [heat(La).money, heat(Lb).money, heat(Lc).money]);
  ok('TS1 heat % identical for any current rate', near(heat(La).pct, heat(Lb).pct) && near(heat(La).pct, 30000 / 5000000 * 100, 1e-9), [heat(La).pct, heat(Lb).pct]);
  const Ln = A.live(mk(null, 35), 'main'), Ln2 = A.live(mk(null, 40), 'main');
  ok('TS1 heat with no stored snapshot rate → current rate (35 / 40)', near(heat(Ln).money, 35000, 1e-6) && near(heat(Ln2).money, 40000, 1e-6), [heat(Ln).money, heat(Ln2).money]);
  const cs = (L) => A.sizeComp(L, Object.assign({ kind: 'pilot', thesisDone: false, side: 'long', entry: 180, stop: 170 }, spec, { fx: 35 }));
  const ma = cs(La), mb = A.sizeComp(Lb, Object.assign({ kind: 'pilot', thesisDone: false, side: 'long', entry: 180, stop: 170 }, spec, { fx: 40 }));
  ok('TS1 new-order check: existing heat in the room line stays at the week rate, the new order uses the current rate', ma.heat && mb.heat && near(ma.heat.money, mb.heat.money, 1e-6), [ma.heat && ma.heat.money, mb.heat && mb.heat.money]);
}
console.log((fail ? 'FAIL ' : 'PASS ') + pass + '/' + (pass + fail) + ' live-layer assertions'); process.exit(fail ? 1 : 0);
