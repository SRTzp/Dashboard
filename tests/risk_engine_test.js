// RE-A — pure-function tests for risk-engine.js. Run: node tests/risk_engine_test.js
// Groups 1-9 = RE1-decisions.md §7 · B = boundary cases (exactly at limit, Monday/month reset with carried risk, two accounts) · X = extra rules.
const R = require('../risk-engine.js'); let f = 0, n = 0;
const ok = (c, m) => { n++; if (!c) { f++; console.log('FAIL', m); } };
const eq = (a, b, m) => ok(a === b, m + ' got ' + JSON.stringify(a) + ' want ' + JSON.stringify(b));
const near = (a, b, m, e = 1e-6) => ok(typeof a === 'number' && Math.abs(a - b) < e, m + ' got ' + a + ' want ' + b);
const has = (r, code, m) => ok(r.reasons.includes(code) || r.flags.includes(code), m + ' has ' + code + ' (reasons ' + r.reasons + ' flags ' + r.flags + ')');
const no = (r, code, m) => ok(!r.reasons.includes(code) && !r.flags.includes(code), m + ' lacks ' + code + ' (reasons ' + r.reasons + ')');
const T = s => Date.parse(s + '+07:00');                 // Bangkok wall time -> ms (explicit offset: machine time zone never matters)
const D = 86400000;

// ── fixtures ─────────────────────────────────────────────────────────────
// 2026-11-16 is a Monday. Week W = Mon 16 Nov .. Sun 22 Nov. Month Nov.
const MON = T('2026-11-16T00:00:00'), WED = T('2026-11-18T10:00:00'), NOW = WED;
const E = 1000000;
const snaps = (eq0 = E, at = T('2026-11-16T08:00:00')) => [{ at, equity: eq0, confirmed: true }];
const basis = (eq0 = E, now = NOW, at) => R.snapshotBasis(snaps(eq0, at || T('2026-11-16T08:00:00')), now);
let nid = 0;
// closed (or live) idea. mult/fx = 1 so money = price units. exitAt null => holding.
function idea(o) {
  const id = o.id || ('i' + (++nid)), side = o.side || 'long';
  const I = { id, account: o.account || 'main', strategy: o.strategy || 'winner', side, status: o.exitAt ? 'closed' : (o.status || 'holding'), product: o.product || 'AAA',
    tranches: [{ id: id + 't1', entry: o.entry, qty: o.qty, stop: o.stop, initialStop: o.initialStop != null ? o.initialStop : o.stop, mult: 1, fx: 1, stopConfirmed: !!o.confirmed }],
    exits: [], entryFees: o.entryFees || 0, workingOrders: o.working || [] };
  if (o.exitAt) { I.exits.push({ id: id + 'x', time: o.exitAt, qty: o.qty, price: o.exitPrice, fees: o.fees || 0, swap: 0, trancheId: id + 't1', reason: o.reason || 'stop' }); I.closedAt = o.exitAt; }
  return I;
}
// a closed LOSING idea with money loss L (entry 100, qty chosen so (100-95)*qty = L)
const loser = (L, o = {}) => idea(Object.assign({ entry: 100, stop: 95, qty: L / 5, exitPrice: 95, exitAt: T('2026-11-17T11:00:00') }, o));
const costsNone = () => null;
const C = R.resolveCosts({ main: { winner: { perSidePct: 0.1 } } }, 'main', 'winner');
const costsOf = () => C;

// ═══ G1 · Satellite: −0.130 −0.300 −0.195 +0.600 = −0.025 → stays Step 4; one more loss → locked; Monday → Step 1 ═══
{
  const at = i => T('2026-11-16T' + String(9 + i).padStart(2, '0') + ':00:00'), A = (nets) => nets.map((v, i) => ({ id: 'a' + i, closeAt: at(i), net: v }));
  let s = R.satStepState(A([-0.130, -0.300, -0.195, +0.600]), T('2026-11-17T20:00:00'));
  eq(s.step, 4, 'G1 step 4 after loss/loss/loss/win(net −0.025)'); near(s.weeklyNet, -0.025, 'G1 weekly net −0.025'); ok(!s.locked, 'G1 not locked');
  eq(s.trace[0].stepIndex, 1, 'G1 after 1st loss → Step 2'); eq(s.trace[1].stepIndex, 2, 'G1 → Step 3'); eq(s.trace[2].stepIndex, 3, 'G1 → Step 4');
  eq(s.trace[3].stepIndex, 3, 'G1 win with net<0 stays');
  s = R.satStepState(A([-0.130, -0.300, -0.195, +0.600, -0.130]), T('2026-11-17T20:00:00'));
  ok(s.locked, 'G1 one more loss at Step 4 → locked');
  const nxt = R.satStepState(A([-0.130, -0.300, -0.195, +0.600, -0.130]), MON + 7 * D);
  eq(nxt.step, 1, 'G1 Monday → Step 1'); ok(!nxt.locked, 'G1 Monday unlocks');
  eq(R.satStepState(A([-0.130, -0.300, -0.195, +0.600, -0.130]), T('2026-11-22T23:59:59')).locked, true, 'G1 Sunday 23:59:59 still locked');
  eq(R.satStepState(A([-0.130, -0.300, -0.195, +0.600, -0.130]), T('2026-11-23T00:00:00')).locked, false, 'G1 Monday 00:00 Bangkok reset');
  // win that brings weekly net to exactly 0 or above resets
  s = R.satStepState(A([-0.2, +0.2]), NOW); eq(s.step, 1, 'G1 win and net = 0 → Step 1');
  s = R.satStepState(A([-0.2, 0]), NOW); eq(s.step, 2, 'G1 breakeven → stay');
  s = R.satStepState(A([-0.2, -0.3, +0.1]), NOW); eq(s.step, 3, 'G1 win with net<0 → stay at current');
}

// ═══ G2 · Satellite full path 0.20+0.30+0.30+0.40 = 1.20 % → budget and lock agree; cancel → no step change; re-entry after Step 1 loss sizes at Step 2 ═══
{
  const losses = [2000, 3000, 3000, 4000].map((L, i) => loser(L, { id: 's' + i, strategy: 'sat', exitAt: T('2026-11-16T' + String(9 + i).padStart(2, '0') + ':00:00'), reason: 'stop' }));
  const attempts = losses.map(i => ({ id: i.id, closeAt: i.closedAt, net: R.ideaRealizedNet(i) }));
  const st = R.satStepState(attempts, NOW);
  ok(st.locked, 'G2 locked after 4th loss'); near(st.weeklyNet, -12000, 'G2 net −12,000 = 1.20% of 1,000,000');
  const b = basis();
  const bc0 = R.satBudgetCheck({ basis: b, now: NOW, account: 'main', ideas: losses, candidateRisk: 0 });
  ok(bc0.allowed, 'G2 budget exactly 1.20% used still "allowed" with nothing new'); near(bc0.weekUsed, 12000, 'G2 used 12,000'); near(bc0.weekCap, 12000, 'G2 cap 12,000');
  const bc1 = R.satBudgetCheck({ basis: b, now: NOW, account: 'main', ideas: losses, candidateRisk: 1 });
  has(bc1, 'MONEY_WEEK', 'G2 any new risk blocked at the limit');
  const gate = R.satCheck({ now: NOW, account: 'main', ideas: losses, attempts, basis: b, condition: { ema50: true, structure: true }, order: { side: 'long', entry: 100, stop: 99, tp: 102 }, product: 'XAU', dayAttempts: [], candidateRisk: 1 });
  has(gate, 'SAT_LOCKED', 'G2 lock and budget agree: locked'); has(gate, 'MONEY_WEEK', 'G2 ... and budget blocked');
  // cancel before any fill = no step change, no result
  const ev = R.foldEvents([{ id: 'e1', type: 'order', at: T('2026-11-16T09:00:00'), account: 'main', ideaId: 'c1', strategy: 'sat', product: 'XAU', side: 'long', qty: 1, entry: 100, stop: 99, mult: 1, fx: 1, orderId: 'o1' },
    { id: 'e2', type: 'cancel', at: T('2026-11-16T10:00:00'), account: 'main', ideaId: 'c1', orderId: 'o1' }]);
  eq(ev[0].status, 'cancelled', 'G2 cancel before fill → cancelled'); eq(R.satStepState([], NOW).step, 1, 'G2 no result → Step 1'); eq(R.satQueueCheck(ev, 'main', 'zz').allowed, true, 'G2 cancel releases the queue');
  // re-entry after a Step 1 loss sizes at Step 2 (not capped at the first attempt)
  const a1 = [{ id: 'r1', closeAt: T('2026-11-17T09:00:00'), net: -2000 }], s2 = R.satStepState(a1, NOW);
  eq(s2.step, 2, 'G2 Step 1 loss → Step 2'); near(R.satEffectiveRpt(s2, 1, 1), 0.30, 'G2 re-entry full condition = 0.30%'); near(R.satEffectiveRpt(s2, 0.65, 1), 0.195, 'G2 re-entry reduced = 0.195%');
  const day = [{ id: 'r1', product: 'XAU', startAt: T('2026-11-18T01:00:00'), status: 'closed', net: -2000, exitReason: 'stop' }];
  const good = { confirmed: true, setupValid: true, sameDirectionZone: true, trendUnchanged: true, candleClosedSince: true };
  const re = R.satDailyCheck({ now: NOW, product: 'XAU', attempts: day, reentry: good });
  ok(re.allowed, 'G2 re-entry allowed'); has(re, 'SAT_REENTRY_TAG', 'G2 re-entry tagged'); eq(re.originalAttemptId, 'r1', 'G2 original attempt linked');
  const sz = R.sizeOrder({ equity: E, rptPct: R.satEffectiveRpt(s2, 1, 1), entry: 100, stop: 99, side: 'long', mult: 1, fx: 1, lotStep: 1, minLot: 1 }); eq(sz.qty, 3000, 'G2 re-entry qty at 0.30% (3,000)');
  for (const k of Object.keys(good)) { const bad = Object.assign({}, good, { [k]: false }); has(R.satDailyCheck({ now: NOW, product: 'XAU', attempts: day, reentry: bad }), 'SAT_REENTRY_COND', 'G2 re-entry needs ' + k); }
  has(R.satDailyCheck({ now: NOW, product: 'XAU', attempts: [day[0], { id: 'r2', product: 'XAU', startAt: NOW, status: 'closed', net: -1, exitReason: 'stop', reentry: true }], reentry: good }), 'SAT_REENTRY_USED', 'G2 third attempt refused');
  has(R.satDailyCheck({ now: NOW, product: 'XAU', attempts: [Object.assign({}, day[0], { exitReason: 'target', net: 5 })], reentry: good }), 'SAT_DAILY_LIMIT', 'G2 no re-entry after a win / non-stop exit');
  eq(R.satDailyCheck({ now: NOW, product: 'BTC', attempts: day, reentry: good }).allowed, true, 'G2 other product has its own daily slot');
  eq(R.satDailyCheck({ now: T('2026-11-19T00:00:00'), product: 'XAU', attempts: day, reentry: good }).reasons.length, 0, 'G2 next Bangkok day resets');
}

// ═══ G3 · Momentum ═══
{
  const b = basis(), ask = (ideas, risk, extra) => R.momentumCheck(Object.assign({ now: NOW, account: 'main', basis: b, ideas, costsFor: costsNone, candidate: { ideaId: 'new', riskMoney: risk } }, extra || {}));
  // realized 1.35 % (3 losses x 0.45 %) → at most 0.45 % combined open + pending + new
  const three = [loser(4500), loser(4500), loser(4500)];
  ok(ask(three, 4500).allowed, 'G3 0.45% new allowed with 1.35% realized');
  has(ask(three, 4501), 'MONEY_WEEK', 'G3 0.45%+1 blocked'); near(ask(three, 4500).money.weekCap, 18000, 'G3 weekly cap 1.80% = 18,000');
  const open = idea({ id: 'open1', entry: 100, stop: 95, qty: 400, status: 'holding' });   // open principal risk 2,000
  no(ask(three.concat([open]), 2500), 'MONEY_WEEK', 'G3 open 2,000 + new 2,500 = 0.45% fits the money check'); has(ask(three.concat([open]), 2501), 'MONEY_WEEK', 'G3 combined over 0.45% blocked');
  const wk = idea({ id: 'wk1', entry: 100, stop: 95, qty: 500, status: 'ordered', working: [{ id: 'w', qty: 500, entry: 100, stop: 95, mult: 1, fx: 1, at: NOW }] });  // working order reserves 2,500
  has(ask(three.concat([wk]), 2500), 'MONEY_WEEK', 'G3 pending order reservation counts');
  // wins never offset
  const win = idea({ entry: 100, stop: 95, qty: 2000, exitPrice: 110, exitAt: T('2026-11-17T09:00:00'), reason: 'target' });   // +20,000
  has(ask(three.concat([win]), 4501), 'MONEY_WEEK', 'G3 a win does not offset realized losses');
  // four half-size losses (≈0.90 %) → locked by ammunition (count), not money
  const half = [1, 2, 3, 4].map(() => loser(2250)), r4 = ask(half, 2250);
  has(r4, 'AMMO_EXHAUSTED', 'G3 four half-size losses lock'); no(r4, 'MONEY_WEEK', 'G3 ... although money is fine'); near(r4.money.weekGross, 9000, 'G3 gross 0.90%');
  eq(r4.ammo.completedLosses, 4, 'G3 ammo 4 used');
  // one idea with half + addition counts once
  const hAdd = idea({ id: 'ha', entry: 100, stop: 95, qty: 200, status: 'holding' }); hAdd.tranches.push({ id: 'ha2', entry: 102, qty: 200, stop: 95, initialStop: 95, mult: 1, fx: 1 });
  eq(R.momentumCheck({ now: NOW, account: 'main', basis: b, ideas: three.concat([hAdd]), costsFor: costsNone, candidate: { ideaId: 'ha', isAddition: true, riskMoney: 100 } }).ammo.total, 4, 'G3 addition to an existing idea adds no ammunition');
  // cancelling a fully unfilled idea releases it
  const unf = idea({ id: 'un', entry: 100, stop: 95, qty: 100, status: 'ordered', working: [{ id: 'w2', qty: 100, entry: 100, stop: 95, mult: 1, fx: 1, at: NOW }] }); unf.tranches = [];
  eq(ask(three.concat([unf]), 100).ammo.reserved, 1, 'G3 ordered idea reserves one allowance'); unf.status = 'cancelled'; unf.workingOrders = []; eq(ask(three.concat([unf]), 100).ammo.reserved, 0, 'G3 cancelled idea released');
  // wins do not reset the weekly count
  eq(ask(three.concat([win]), 100).ammo.completedLosses, 3, 'G3 win does not reset the count');
  // Monday with four carried full-risk positions → no new entry until one stop is confirmed at net breakeven
  const carried = [1, 2, 3, 4].map(k => idea({ id: 'c' + k, entry: 100, stop: 95, qty: 880, status: 'holding' }));   // ≈4,484 each incl. est. exit cost ≈ 1.80 % open
  const mon = (ideas, risk) => R.momentumCheck({ now: MON + 3600000, account: 'main', basis: R.snapshotBasis(snaps(E, T('2026-11-16T00:30:00')), MON + 3600000), ideas, costsFor: costsOf, candidate: { ideaId: 'new', riskMoney: risk } });
  let rm = mon(carried, 4500); has(rm, 'AMMO_EXHAUSTED', 'G3 Monday: 4 carried ideas reserve 4 allowances'); has(rm, 'MONEY_WEEK', 'G3 Monday: carried open risk fills the cap');
  carried.forEach(c => { c.entryFees = 0; });
  const be = R.netBreakevenStop(carried[0], C); ok(be > 100, 'G3 net-breakeven stop is above entry (costs) ' + be);
  carried[0].tranches[0].stop = be; carried[0].tranches[0].stopConfirmed = true;
  rm = mon(carried, 4500); no(rm, 'AMMO_EXHAUSTED', 'G3 confirmed net-breakeven stop releases one allowance'); no(rm, 'MONEY_WEEK', 'G3 ... and its money'); ok(rm.allowed, 'G3 entry allowed after release ' + rm.reasons);
}

// ═══ G4 · Momentum Option C ═══
{
  const b = basis();
  const mk = () => idea({ id: 'oc', entry: 100, stop: 95, qty: 1000, status: 'holding', entryFees: 100 });
  const I = mk(), c1 = R.resolveCosts({ main: { winner: { perSidePct: 0.1 } } }, 'main', 'winner'), c2 = R.resolveCosts({ main: { winner: { perSidePct: 0.5 } } }, 'main', 'winner');
  // before any stop move: reserved, exposure = principal + costs
  ok(!R.ammoReleased(I, c1), 'G4 not released before stop confirmed');
  I.tranches[0].stop = 100; I.tranches[0].stopConfirmed = true;            // stop at ENTRY, not net breakeven
  let rs = R.ideaResult(I, c1); ok(rs.projectedNet < 0, 'G4 stop at entry projects a net loss (fees) ' + rs.projectedNet); ok(!R.ammoReleased(I, c1), 'G4 stop at entry keeps the reservation');
  ok(rs.exposure > 0 && rs.exposure < 400, 'G4 money exposure fell to costs only: ' + rs.exposure);
  const be = R.netBreakevenStop(I, c1); I.tranches[0].stop = be;
  rs = R.ideaResult(I, c1); near(rs.projectedNet, 0, 'G4 projected net at net-breakeven stop = 0', 1e-6); ok(R.ammoReleased(I, c1), 'G4 net-breakeven stop releases the reservation');
  near(rs.exposure, 0, 'G4 money exposure 0 at net breakeven', 1e-6);
  // later cost edit brings it back without touching the position
  const before = JSON.stringify(I.tranches); ok(!R.ammoReleased(I, c2), 'G4 cost edit (higher costs) brings the reservation back'); eq(JSON.stringify(I.tranches), before, 'G4 position untouched by the cost edit');
  eq(R.ammoReleased(I, null), false, 'G4 unknown costs never release');
  ok(R.ideaResult(I, null).projectedNet === null && R.ideaResult(I, null).costUnknown === true, 'G4 unknown costs → Unknown (null), not 0');
  // unconfirmed stop never releases even if it would project ≥ 0
  I.tranches[0].stopConfirmed = false; I.tranches[0].stop = be + 1; ok(!R.ammoReleased(I, c1), 'G4 +1.5R prompt alone releases nothing: stop must be confirmed');
  // fifth loss accepted and flagged
  const five = [1, 2, 3, 4, 5].map(() => loser(2250)), r5 = R.momentumCheck({ now: NOW, account: 'main', basis: b, ideas: five, costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 100 } });
  has(r5, 'AMMO_OVERSHOOT', 'G4 fifth loss flagged'); has(r5, 'AMMO_EXHAUSTED', 'G4 new risk restricted'); eq(R.actionPolicy('fill', r5).accepted, true, 'G4 the actual fill/close is accepted');
  has(R.actionPolicy('fill', r5), 'FILL_OVER_LIMIT', 'G4 fill over limit flagged');
  eq(R.actionPolicy('order', r5).accepted, false, 'G4 new order blocked');
  for (const a of ['close', 'reduce', 'stop_update', 'cancel']) eq(R.actionPolicy(a, r5).accepted, true, 'G4 ' + a + ' always allowed');
  // partial exit realises into the idea; ammo still reserved until the stop projects ≥ 0
  const P = idea({ id: 'pp', entry: 100, stop: 95, qty: 1000, status: 'holding' }); P.exits.push({ id: 'p1', time: NOW, qty: 500, price: 110, fees: 0, swap: 0, trancheId: P.tranches[0].id });
  eq(R.ideaResult(P, null).remainingQty, 500, 'G4 partial exit leaves 500'); near(R.ideaResult(P, null).realizedNet, 5000, 'G4 partial exit realised +5,000');
}

// ═══ G5 · Strict sign rule ═══
{
  eq(R.outcome(-0.0001), 'loss', 'G5 −0.0001 is a loss'); eq(R.outcome(0.0001), 'win', 'G5 +0.0001 is a win'); eq(R.outcome(0), 'be', 'G5 0 is breakeven'); eq(R.outcome(NaN), null, 'G5 NaN → null');
  // stop at entry exit netting negative after fees = loss everywhere
  const so = idea({ id: 'se', strategy: 'sat', entry: 100, stop: 100, qty: 100, exitPrice: 100, exitAt: T('2026-11-17T10:00:00'), fees: 5 });
  near(R.ideaRealizedNet(so), -5, 'G5 net −5 after fees'); eq(R.outcome(R.ideaRealizedNet(so)), 'loss', 'G5 stop-at-entry with fees = loss');
  const st = R.satStepState([{ id: 'x', closeAt: so.closedAt, net: R.ideaRealizedNet(so) }], NOW); eq(st.step, 2, 'G5 Satellite step +1');
  const mo = idea({ id: 'me', entry: 100, stop: 100, qty: 100, exitPrice: 100, exitAt: T('2026-11-17T10:00:00'), fees: 5 });
  eq(R.momentumState({ now: NOW, account: 'main', ideas: [mo], costsFor: costsNone }).completedLosses, 1, 'G5 Momentum allowance used');
  const ex = idea({ id: 'ez', entry: 100, stop: 100, qty: 100, exitPrice: 100, exitAt: T('2026-11-17T10:00:00'), fees: 0 });
  eq(R.momentumState({ now: NOW, account: 'main', ideas: [ex], costsFor: costsNone }).completedLosses, 0, 'G5 exact breakeven is not a loss');
  eq(R.satStepState([{ id: 'x', closeAt: so.closedAt, net: 0 }], NOW).step, 1, 'G5 exact breakeven keeps Step 1');
  // swap counts too
  const sw = idea({ id: 'sw', entry: 100, stop: 100, qty: 1, exitPrice: 100.5, exitAt: T('2026-11-17T10:00:00') }); sw.exits[0].swap = 0.6; near(R.ideaRealizedNet(sw), -0.1, 'G5 swap included'); eq(R.outcome(R.ideaRealizedNet(sw)), 'loss', 'G5 gross win, net loss after swap');
}

// ═══ G6 · Compounder ═══
{
  const pilot = { id: 'p', entry: 100, qty: 100, stop: 95, initialStop: 95, mult: 1, fx: 1 };
  // Starter top-up (no thesis) allowed within 0.50 %; Add-on without thesis blocked. Add-on = TOTAL-RISK rule only (answers-A #16 amended).
  const tu = R.compEntryCheck({ kind: 'topup', starterOn: true, thesisDone: false, side: 'long', usedPct: 0.25, requestedPct: 0.25 });
  ok(tu.allowed, 'G6 Starter top-up without thesis allowed (no stop / breakeven condition)'); near(tu.capPct, 0.5, 'G6 top-up capped at 0.50% without thesis');
  has(R.compEntryCheck({ kind: 'topup', starterOn: true, thesisDone: false, side: 'long', usedPct: 0.25, requestedPct: 0.3 }), 'ADDON_TOTAL_RISK', 'G6 top-up above 0.50% total blocked without thesis');
  const addonArgs = { kind: 'addon', side: 'long', usedPct: 0.5, requestedPct: 0.5 };
  const noT = R.compEntryCheck({ kind: 'addon', thesisDone: false, side: 'long', usedPct: 0.5, requestedPct: 0.5 }); has(noT, 'ADDON_THESIS', 'G6 Add-on without thesis blocked'); ok(!noT.allowed, 'G6 ... not allowed');
  ok(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.5, requestedPct: 0.5 }).allowed, 'G6 Add-on with thesis: 0.50 + 0.50 = 1.00 allowed (no +1.5R / breakeven needed; RM1 cap 1.25%)');
  has(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.5, requestedPct: 0.51 }), 'ADDON_TOTAL_RISK', 'G6 total above 1.25% blocked (new order also above its own 0.50%)');
  has(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.25, requestedPct: 0.8 }), 'ADDON_TOTAL_RISK', 'G6 beyond whole plan 1% blocked');
  has(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0, requestedPct: 0.4, factor: 0.5 }), 'ADDON_TOTAL_RISK', 'G6 new order alone > 0.50% x min(Regime, Emergency) blocked');
  ok(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.2, requestedPct: 0.25, factor: 0.5 }).allowed, 'G6 new order = 0.50% x 50% allowed');
  const below = R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.5, requestedPct: 0.3, entryPx: 98, avgEntry: 100 });
  ok(below.allowed && below.flags.indexOf('ADDON_BELOW_ENTRY_WARN') >= 0, 'G6 adding below the average entry: allowed + warning only');
  ok(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.5, requestedPct: 0.3, entryPx: 103, avgEntry: 100 }).flags.indexOf('ADDON_BELOW_ENTRY_WARN') < 0, 'G6 above entry: no warning');
  ok(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'short', usedPct: 0.5, requestedPct: 0.3, entryPx: 102, avgEntry: 100 }).flags.indexOf('ADDON_BELOW_ENTRY_WARN') >= 0, 'G6 short: adverse side warns');
  ok(R.compEntryCheck({ kind: 'addon', thesisDone: true, side: 'long', usedPct: 0.25, requestedPct: 0.75 }).capPct === 1.25, 'G6 whole plan = 1.25% (RM1: was 1.00%)');
  eq(R.compEntryCheck({ kind: 'pilot', starterOn: true, thesisDone: false, requestedPct: 0.25 }).allowed, true, 'G6 Starter first entry 0.25%');
  has(R.compEntryCheck({ kind: 'pilot', starterOn: true, thesisDone: false, requestedPct: 0.3 }), 'COMP_PHASE_CAP', 'G6 Starter first entry above 0.25 blocked');
  has(R.compEntryCheck({ kind: 'pilot', thesisDone: false, requestedPct: 0.6 }), 'COMP_PHASE_CAP', 'G6 thesis incomplete → Pilot only (0.50%)');
  // min(Regime 75 %, Emergency 50 %) = 50 %
  const now = NOW, fresh = { acwi: true, hyg: false, asOf: now - 1 * D }, rg = R.regimeState(fresh, now);
  near(rg.factor, 0.8, 'G6 one red = 80% (RM1)'); near(R.compFactor(rg, 0.5), 0.5, 'G6 min(80%, 50%) = 50% (not 40%)');
  near(R.regimeState({ acwi: true, hyg: true, asOf: now }, now).factor, 1, 'G6 both green 100%'); near(R.regimeState({ acwi: false, hyg: false, asOf: now }, now).factor, 0.6, 'G6 both red 60% (RM1)');
  const stale = R.regimeState({ acwi: true, hyg: true, asOf: now - 5 * D }, now); near(stale.factor, 0.8, 'G6 stale caps at 80% (RM1 fallback)'); has(stale, 'COMP_REGIME_STALE', 'G6 stale flagged');
  near(R.regimeState({ acwi: true, hyg: true, asOf: now - 4 * D }, now).factor, 1, 'G6 exactly 4 days is still fresh');
  // six-loss lock
  const cyc = (nets, t0 = T('2026-11-01T10:00:00')) => nets.map((v, i) => ({ id: 'cy' + i, flatAt: t0 + i * D, net: v }));
  eq(R.compStreak(cyc([-1, -1, -1, -1, -1]), []).locked, false, 'G6 five losses: not locked');
  let k = R.compStreak(cyc([-1, -1, -1, -1, -1, -1]), []); ok(k.locked, 'G6 six consecutive losses → lock'); eq(k.streak, 6, 'G6 streak 6');
  eq(R.compStreak(cyc([-1, -1, -1, +1, -1, -1, -1]), []).locked, false, 'G6 a win resets');
  eq(R.compStreak(cyc([-1, -1, -1, 0, -1, -1, -1]), []).locked, true, 'G6 exact breakeven neither counts nor resets');
  eq(R.compStreak(cyc([-0.2, -0.2, -0.2, -0.2, -0.2, -0.2]), []).locked, true, 'G6 six small losses still lock (not 6% total)');
  // unlock gate
  const sixth = k.sixthLossAt, green = R.regimeState({ acwi: true, hyg: true, asOf: sixth + 7 * D - 1 }, sixth + 7 * D), U = (o) => R.compUnlockCheck(Object.assign({ streakState: k, now: sixth + 7 * D, regime: green, note: 'reviewed the six exits', confirm: true }, o));
  ok(U({}).allowed && U({}).unlocked, 'G6 unlock OK on day 7 with everything in place'); eq(U({}).streakAfter, 0, 'G6 streak returns to 0');
  has(U({ now: sixth + 7 * D - 1 }), 'COMP_UNLOCK_WAIT', 'G6 refused before day 7');
  has(U({ regime: R.regimeState({ acwi: true, hyg: true, asOf: sixth - 3 * D }, sixth + 7 * D) }), 'COMP_UNLOCK_STALE', 'G6 refused with stale data');
  has(U({ regime: R.regimeState({ acwi: true, hyg: false, asOf: sixth + 7 * D }, sixth + 7 * D) }), 'COMP_UNLOCK_SIGNALS', 'G6 refused when a signal is red');
  has(U({ note: '   ' }), 'COMP_UNLOCK_NOTE', 'G6 refused without a note'); has(U({ note: '' }), 'COMP_UNLOCK_NOTE', 'G6 refused with empty note'); has(U({ confirm: false }), 'COMP_UNLOCK_CONFIRM', 'G6 refused without confirm');
  eq(R.compStreak(cyc([-1, -1, -1, -1, -1, -1]), [{ at: sixth + 8 * D }]).streak, 0, 'G6 recorded unlock → streak 0'); eq(R.compStreak(cyc([-1, -1, -1, -1, -1, -1, -1], T('2026-11-01T10:00:00')), [{ at: sixth + 8 * D }]).locked, false, 'G6 losses before the unlock do not re-lock');
  // locked blocks pilot AND add-on; heat cap
  const b = basis(), sig = { acwi: true, hyg: true, asOf: NOW };
  const lockedCk = R.compCheck({ now: NOW, account: 'main', basis: b, ideas: [], cycles: cyc([-1, -1, -1, -1, -1, -1]), unlocks: [], signals: sig, entry: { kind: 'pilot', requestedPct: 0.5, thesisDone: true }, emergencyFactor: 1 });
  has(lockedCk, 'COMP_LOCKED', 'G6 lock blocks Pilot');
  has(R.compCheck({ now: NOW, account: 'main', basis: b, ideas: [], cycles: cyc([-1, -1, -1, -1, -1, -1]), unlocks: [], signals: sig, entry: Object.assign({ thesisDone: true }, addonArgs), emergencyFactor: 1 }), 'COMP_LOCKED', 'G6 lock blocks Add-on');
  const heatIdeas = [1, 2, 3, 4, 5, 6].map(i => idea({ id: 'h' + i, strategy: 'ladder', entry: 100, stop: 95, qty: 2000, status: 'holding' }));   // 10,000 each = 6%
  const hk = R.compCheck({ now: NOW, account: 'main', basis: b, ideas: heatIdeas, cycles: [], unlocks: [], signals: sig, entry: { kind: 'pilot', requestedPct: 0.5, thesisDone: true }, candidateRisk: 5000, emergencyFactor: 1 });
  has(hk, 'COMP_HEAT', 'G6 heat cap 6% blocks'); near(hk.heat.pct, 6, 'G6 heat 6.00%'); eq(R.compCheck({ now: NOW, account: 'main', basis: b, ideas: heatIdeas, cycles: [], unlocks: [], signals: sig, entry: { kind: 'pilot', requestedPct: 0.5, thesisDone: true }, candidateRisk: 0, emergencyFactor: 1 }).allowed, true, 'G6 exactly 6% heat with nothing new is fine');
  // Compounder money checks are separate from Active
  eq(R.compCheck({ now: NOW, account: 'main', basis: b, ideas: [], cycles: [], unlocks: [], signals: sig, entry: { kind: 'pilot', requestedPct: 0.5, thesisDone: true }, candidateRisk: 5000, emergencyFactor: 1 }).allowed, true, 'G6 Pilot within heat allowed');
}

// ═══ G7 · Emergency ═══
{
  const nov = T('2026-11-01T09:00:00'), mref = { equity: 1000000, at: nov };
  let s = R.emergencyStep(null, { at: T('2026-11-12T20:00:00'), equity: 900000, confirmed: true }, mref, []);
  ok(s.active && s.factor === 0.5, 'G7 −10% at a mid-month snapshot → half size immediately'); near(s.declinePct, 10, 'G7 decline 10.0');
  s = R.emergencyStep(null, { at: T('2026-11-12T20:00:00'), equity: 900001, confirmed: true }, mref, []); ok(!s.active, 'G7 −9.9999% does not trigger');
  s = R.emergencyStep(null, { at: T('2026-11-12T20:00:00'), equity: 900000, confirmed: false }, mref, []); ok(!s.active, 'G7 unconfirmed snapshot ignored');
  const on = { active: true, refEquity: 1000000, refStartMs: nov };
  // survives a month change: new month reference (Dec 1: 920,000) is NOT used while Emergency is on
  s = R.emergencyStep(on, { at: T('2026-12-01T09:00:00'), equity: 920000, confirmed: true }, { equity: 920000, at: T('2026-12-01T09:00:00') }, []);
  ok(s.active, 'G7 stays through the month change (decline 8% from the retained reference)'); eq(s.refEquity, 1000000, 'G7 reference retained');
  s = R.emergencyStep(on, { at: T('2026-12-08T09:00:00'), equity: 950000, confirmed: true }, { equity: 920000, at: T('2026-12-01T09:00:00') }, []); ok(s.active, 'G7 exactly −5.0% is not above −5% → stays');
  s = R.emergencyStep(on, { at: T('2026-12-08T09:00:00'), equity: 950001, confirmed: true }, { equity: 920000, at: T('2026-12-01T09:00:00') }, []); ok(!s.active && s.factor === 1, 'G7 above −5% of the retained reference → off');
  // cash flows excluded
  s = R.emergencyStep(null, { at: T('2026-11-12T20:00:00'), equity: 1000000, confirmed: true }, mref, [{ at: T('2026-11-10T09:00:00'), amount: 100000 }]);
  ok(s.active, 'G7 a deposit does not hide a −10% performance drop');
  s = R.emergencyStep(null, { at: T('2026-11-12T20:00:00'), equity: 900000, confirmed: true }, mref, [{ at: T('2026-11-10T09:00:00'), amount: -100000 }]);
  ok(!s.active, 'G7 a withdrawal is not a loss'); near(s.declinePct, 0, 'G7 adjusted decline 0');
  // factor feeds sizing: Satellite Step 3 × 65% × 0.5 = 0.0975%
  near(R.satEffectiveRpt({ stepIndex: 2 }, 0.65, 0.5), 0.0975, 'G7 Step 3 × 65% × Emergency 0.5 = 0.0975% (no old 0.6 multiplier)');
  near(R.emergencyFactor(true), 0.5, 'G7 factor 0.5'); near(R.emergencyFactor(false), 1, 'G7 factor 1');
  eq(R.emergencyStep(null, null, mref, []).active, false, 'G7 no snapshot → unchanged');
}

// ═══ G8 · Min-stop ═══
{
  const base = { equity: E, rptPct: 0.45, entry: 100, side: 'long', mult: 1, fx: 1, lotStep: 1, minLot: 1 };
  const r = R.sizeOrder(Object.assign({}, base, { stop: 98, minStopDist: 4 }));
  eq(r.qty, 1125, 'G8 sized on 4% distance (4,500/4 = 1,125)'); near(r.sizingDistance, 4, 'G8 sizing distance 4'); near(r.actualDistance, 2, 'G8 actual distance 2');
  near(r.actualRisk, 2250, 'G8 risk reported on the actual 2% stop'); ok(r.minStopApplied, 'G8 flagged min-stop applied');
  const s = R.sizeOrder(Object.assign({}, base, { stop: 95, minStopDist: 4 })); eq(s.qty, 900, 'G8 actual distance above the minimum: size on actual'); near(s.actualRisk, 4500, 'G8 full 0.45% risk');
  eq(R.sizeOrder(Object.assign({}, base, { stop: 95 })).qty, 900, 'G8 plan example: 1,000,000 · 0.45% · 100/95 → 900'); eq(R.sizeOrder(Object.assign({}, base, { stop: 95, factor: 0.5 })).qty, 450, 'G8 half → 450');
  // fraction (homework) and Starter
  const hw = R.entryFraction({ homeworkDone: false }); near(hw.fraction, 0.5, 'G8 thesis not done → 50%'); eq(R.sizeOrder(Object.assign({}, base, { stop: 95, fraction: hw.fraction })).qty, 450, 'G8 homework cap halves qty');
  near(R.entryFraction({ homeworkDone: true, starterOn: true, isFirstEntry: true }).fraction, 0.25, 'G8 Starter ¼ first entry'); near(R.entryFraction({ homeworkDone: true, starterOn: true, isFirstEntry: false, usedFraction: 0.25 }).fraction, 0.75, 'G8 topup remainder 75%');
  near(R.entryFraction({ homeworkDone: false, usedFraction: 0.5 }).fraction, 0, 'G8 addition blocked while thesis undone (nothing left under 50%)');
  // the user's stop is never moved
  ok(!('stop' in r), 'G8 engine returns no moved stop');
  // short side
  const sh = R.sizeOrder({ equity: E, rptPct: 0.45, entry: 100, stop: 105, side: 'short', mult: 1, fx: 1, lotStep: 1, minLot: 1 }); eq(sh.qty, 900, 'G8 short sizing'); has(R.sizeOrder({ equity: E, rptPct: 0.45, entry: 100, stop: 95, side: 'short', mult: 1, fx: 1, lotStep: 1, minLot: 1 }), 'STOP_WRONG_SIDE', 'G8 wrong side blocked');
  has(R.sizeOrder(Object.assign({}, base, { stop: 100 })), 'STOP_EQUALS_ENTRY', 'G8 entry = stop blocked');
  // FX and contract
  const g = R.sizeOrder({ equity: E, rptPct: 0.30, entry: 2000, stop: 1990, side: 'long', mult: 100, fx: 35, lotStep: 0.01, minLot: 0.01 }); near(g.qty, 0.08, 'G8 FX + contract multiplier + lot step: 3,000 / (10·100·35) = 0.0857 → floor 0.08', 1e-9); ok(g.qty > 0, 'G8 FX sizing returns a lot');
}

// ═══ G9 · accounts never mix · fills over a cap accepted · stale snapshot · lot below minimum ═══
{
  const b = basis(), main = [loser(18000, { account: 'main' })], fam = [loser(18000, { account: 'fam' })];
  const mA = (ideas, acct) => R.momentumCheck({ now: NOW, account: acct, basis: b, ideas, costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 4500 } });
  has(mA(main.concat(fam), 'main'), 'MONEY_WEEK', 'G9 Main over its cap'); ok(mA(main, 'fam').allowed, 'G9 Family is untouched by Main losses (ideas filtered by account)');
  ok(mA(main.concat(fam), 'fam').reasons.includes('MONEY_WEEK'), 'G9 Family sees only its own ideas');
  ok(R.momentumCheck({ now: NOW, account: 'fam', basis: b, ideas: main, costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 4500 } }).allowed, 'G9 Main ideas passed for Family are ignored');
  // separate snapshots per account → separate basis
  const bm = R.snapshotBasis([{ at: T('2026-11-16T08:00:00'), equity: 1000000, confirmed: true }], NOW), bf = R.snapshotBasis([{ at: T('2026-11-16T08:00:00'), equity: 200000, confirmed: true }], NOW);
  near(R.sizeOrder({ equity: bm.weekEquity, rptPct: 0.45, entry: 100, stop: 95, mult: 1, fx: 1, lotStep: 1, minLot: 1 }).qty, 900, 'G9 Main size from Main equity'); near(R.sizeOrder({ equity: bf.weekEquity, rptPct: 0.45, entry: 100, stop: 95, mult: 1, fx: 1, lotStep: 1, minLot: 1 }).qty, 180, 'G9 Family size from Family equity');
  // fill over a cap accepted and flagged
  const over = mA(main, 'main'); eq(R.actionPolicy('fill', over).accepted, true, 'G9 actual fill over a cap accepted'); has(R.actionPolicy('fill', over), 'FILL_OVER_LIMIT', 'G9 breach flagged'); eq(R.actionPolicy('order', over).accepted, false, 'G9 the proposed order is blocked');
  // snapshot older than 14 days blocks new risk
  const s0 = T('2026-11-01T09:00:00'), mk = now => R.snapshotBasis([{ at: s0, equity: E, confirmed: true }], now);
  ok(mk(s0 + 14 * D).ok, 'G9 exactly 14 days old: still usable (with warning)'); has(mk(s0 + 14 * D), 'SNAPSHOT_OLD', 'G9 carried snapshot warns');
  const st = mk(s0 + 14 * D + 1); ok(!st.ok, 'G9 older than 14 days: blocked'); has(st, 'SNAPSHOT_STALE', 'G9 SNAPSHOT_STALE');
  has(R.momentumCheck({ now: s0 + 15 * D, account: 'main', basis: st, ideas: [], costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 1 } }), 'SNAPSHOT_STALE', 'G9 momentum gate blocks on a stale snapshot');
  has(R.satBudgetCheck({ basis: st, now: s0 + 15 * D, account: 'main', ideas: [], candidateRisk: 1 }), 'SNAPSHOT_STALE', 'G9 satellite gate blocks on a stale snapshot');
  has(R.snapshotBasis([], NOW), 'NO_SNAPSHOT', 'G9 no snapshot at all blocks'); has(R.snapshotBasis([{ at: s0, equity: E, confirmed: false }], NOW), 'NO_SNAPSHOT', 'G9 unconfirmed snapshot does not count');
  eq(basis().state, 'current', 'G9 snapshot of this week = current'); eq(R.snapshotBasis(snaps(E, T('2026-11-09T09:00:00')), NOW).state, 'carried', 'G9 last-week snapshot is carried (warning)');
  // lot below minimum blocks
  const lb = R.sizeOrder({ equity: 10000, rptPct: 0.05, entry: 2000, stop: 1990, side: 'long', mult: 100, fx: 1, lotStep: 0.01, minLot: 0.01 });
  ok(!lb.allowed, 'G9 lot below minimum blocked'); has(lb, 'LOT_BELOW_MIN', 'G9 LOT_BELOW_MIN'); eq(lb.qty, 0, 'G9 qty 0, not rounded up');
  // missing data → blocked with a reason (never silently 0)
  has(R.sizeOrder({ equity: 0, rptPct: 0.2, entry: 100, stop: 95, mult: 1, fx: 1, lotStep: 1, minLot: 1 }), 'EQUITY_MISSING', 'G9 equity missing'); has(R.sizeOrder({ equity: E, rptPct: 0.2, entry: 100, stop: 95, mult: 1, lotStep: 1, minLot: 1 }), 'FX_MISSING', 'G9 FX missing');
  has(R.sizeOrder({ equity: E, rptPct: 0.2, entry: 100, stop: 95, fx: 1, lotStep: 1, minLot: 1 }), 'SPEC_MISSING', 'G9 contract multiplier missing');
}

// ═══ B · boundary cases ═══
{
  const b = basis(), ask = (ideas, risk, now = NOW, bs = b) => R.momentumCheck({ now, account: 'main', basis: bs, ideas, costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: risk } });
  ok(ask([], 18000).allowed, 'B exactly at the weekly limit allowed'); has(ask([], 18000.01), 'MONEY_WEEK', 'B one cent over blocked');
  ok(ask([loser(9000), loser(9000)], 0).allowed, 'B exactly 1.80% realized, nothing new → allowed'); eq(R.satBudgetCheck({ basis: b, now: NOW, account: 'main', ideas: [], candidateRisk: 12000 }).allowed, true, 'B Satellite exactly 1.20% allowed');
  has(R.satBudgetCheck({ basis: b, now: NOW, account: 'main', ideas: [], candidateRisk: 12000.01 }), 'MONEY_WEEK', 'B Satellite over 1.20% blocked');
  // Monday reset with carried risk: last week's losses fall out, carried open risk stays
  const lastWeek = loser(18000, { exitAt: T('2026-11-13T15:00:00') }), carriedOpen = idea({ id: 'co', entry: 100, stop: 95, qty: 900, status: 'holding' });
  const monNow = MON + 3600000, bm = R.snapshotBasis(snaps(E, T('2026-11-16T00:30:00')), monNow);
  const r = ask([lastWeek, carriedOpen], 4500, monNow, bm); ok(r.allowed, 'B Monday: last week’s 1.80% losses no longer count, 0.45% carried + 0.45% new fits'); near(r.money.weekGross, 0, 'B Monday gross 0'); near(r.money.open, 4500, 'B carried open risk still counts');
  has(ask([lastWeek, carriedOpen], 13501.01, monNow, bm), 'MONEY_WEEK', 'B carried risk is never erased by a reset');
  eq(r.ammo.completedLosses, 0, 'B Monday: weekly count reset');
  // Sunday 23:59:59 vs Monday 00:00:00 (Bangkok)
  const sun = T('2026-11-15T23:59:59'), mon0 = T('2026-11-16T00:00:00');
  ok(R.bkk.weekStart(sun) < mon0 && R.bkk.weekStart(mon0) === mon0, 'B week boundary Monday 00:00 Bangkok'); eq(R.bkk.weekKey(mon0), '2026-11-16', 'B week key'); eq(R.bkk.dayKey(T('2026-11-16T00:00:00')), '2026-11-16', 'B day key');
  eq(R.bkk.monthStart(T('2026-11-30T23:59:59')), T('2026-11-01T00:00:00'), 'B month start'); eq(R.bkk.monthKey(T('2026-12-01T00:00:00')), '2026-12', 'B month 1st 00:00 Bangkok');
  // UTC evening of the 15th is already Monday 16th in Bangkok (17:00 UTC = 00:00 +07)
  eq(R.bkk.weekKey(Date.parse('2026-11-15T17:00:00Z')), '2026-11-16', 'B UTC 17:00 Sunday = Monday in Bangkok');
  // Month reset: monthly counters reset, exposure stays; weekly window continues across the month boundary
  const dec = T('2026-12-01T09:00:00'), novLoss = loser(72000, { exitAt: T('2026-11-30T10:00:00') }), decLoss = loser(100, { exitAt: T('2026-12-01T08:00:00') });
  const decBasis = R.snapshotBasis([{ at: T('2026-12-01T08:30:00'), equity: E, confirmed: true }], dec);
  const mm = ask([novLoss, decLoss], 0, dec, decBasis); near(mm.money.monthUsed, 100, 'B new month: November losses no longer in the monthly total');
  const mm2 = R.momentumCheck({ now: T('2026-11-30T12:00:00'), account: 'main', basis: R.snapshotBasis(snaps(E, T('2026-11-23T08:00:00')), T('2026-11-30T12:00:00')), ideas: [novLoss], costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 1 } });
  has(mm2, 'MONEY_MONTH', 'B monthly 7.20% (72,000) reached → blocked even though the week is fresh');
  eq(R.momentumState({ now: T('2026-11-30T12:00:00'), account: 'main', ideas: [loser(72000, { exitAt: T('2026-11-30T10:00:00') })], costsFor: costsNone }).completedLosses, 1, 'B a single huge loss uses one allowance only (count ≠ money)');
  // month-start basis for monthly cap, week-start basis for weekly
  const twoBasis = { ok: true, flags: [], weekEquity: 1000000, monthEquity: 500000 }; near(ask([], 0, NOW, twoBasis).money.monthCap, 36000, 'B monthly cap from month-start equity'); near(ask([], 0, NOW, twoBasis).money.weekCap, 18000, 'B weekly cap from week-start equity');
  // results belong to the week of the close time; ideas opened last week, closed this week count this week
  const crossing = loser(4500, { exitAt: T('2026-11-17T09:00:00') }); crossing.openedAt = T('2026-11-10T09:00:00'); near(ask([crossing], 0).money.weekGross, 4500, 'B result belongs to the close week');
  // partial exits count immediately toward the budget, but ammunition only at completion
  const part = idea({ id: 'pt', entry: 100, stop: 95, qty: 1000, status: 'holding' }); part.exits.push({ id: 'px', time: T('2026-11-17T09:00:00'), qty: 500, price: 95, fees: 0, swap: 0, trancheId: part.tranches[0].id });
  const pr = ask([part], 0); near(pr.money.weekGross, 2500, 'B partial exit loss counts immediately'); eq(pr.ammo.completedLosses, 0, 'B ... but the idea is not a completed loss yet'); eq(pr.ammo.reserved, 1, 'B ... and still reserves its allowance');
  // two accounts: same instant, independent step / lock state
  const atts = { main: [{ id: 'm', closeAt: T('2026-11-17T09:00:00'), net: -1 }], fam: [] }; eq(R.satStepState(atts.main, NOW).step, 2, 'B Main at Step 2'); eq(R.satStepState(atts.fam, NOW).step, 1, 'B Family still Step 1');
  // duplicate event ids never double count
  const dup = [{ id: 'a', closeAt: T('2026-11-16T09:00:00'), net: -1 }, { id: 'a', closeAt: T('2026-11-16T09:00:00'), net: -1 }]; eq(R.satStepState(dup, NOW).step, 2, 'B duplicate attempt id counted once');
  const evs = [{ id: 'o1', type: 'order', at: 1, account: 'main', ideaId: 'x', strategy: 'winner', product: 'A', side: 'long', qty: 10, entry: 10, stop: 9, mult: 1, fx: 1, orderId: 'w1' }, { id: 'f1', type: 'fill', at: 2, account: 'main', ideaId: 'x', trancheId: 't', qty: 10, price: 10, stop: 9, mult: 1, fx: 1, orderId: 'w1' }, { id: 'c1', type: 'close', at: 3, account: 'main', ideaId: 'x', trancheId: 't', qty: 10, price: 9 }];
  const once = R.foldEvents(evs), twice = R.foldEvents(evs.concat(evs, [evs[0]])); eq(JSON.stringify(once), JSON.stringify(twice), 'B replay with duplicate events is idempotent'); eq(R.foldEvents(evs.slice().reverse())[0].status, 'closed', 'B replay order independent (sorted by time, id)');
  near(R.ideaRealizedNet(once[0]), -10, 'B folded idea net −10');
}

// ═══ X · extra rules ═══
{
  // Satellite condition table
  const c = (e, s, m) => R.satCondition({ ema50: e, structure: s, mss: m });
  eq(c(true, true).factor, 1, 'X ✓✓ → 100%'); eq(c(false, true).factor, 0.65, 'X ✗✓ → 65%'); has(c(false, true), 'SAT_NEAREST_TARGET', 'X ✗✓ nearest-target warning');
  eq(c(true, false, 'yes').label, 'Counter trend @ MSS', 'X ✓✗ + MSS Yes'); eq(c(true, false, 'yes').factor, 0.65, 'X counter 65%'); eq(c(false, false, 'yes').label, 'Reversal @ MSS', 'X ✗✗ + MSS Yes'); has(c(false, false, 'yes'), 'SAT_NEAREST_TARGET', 'X reversal warning');
  has(c(true, false, 'no'), 'SAT_COND_BLOCKED', 'X ✓✗ MSS No blocked'); has(c(false, false, null), 'SAT_COND_BLOCKED', 'X ✗✗ MSS blank blocked'); has(c(false, false, 'no'), 'SAT_COND_BLOCKED', 'X ✗✗ MSS No blocked');
  has(R.satCondition({ ema50: null, structure: true }), 'SAT_COND_INCOMPLETE', 'X EMA50 unselected incomplete'); has(R.satCondition({ ema50: true }), 'SAT_COND_INCOMPLETE', 'X Structure unselected incomplete');
  eq(c(true, true).isFull, true, 'X is_full_condition derived true'); eq(c(false, true).isFull, false, 'X is_full_condition derived false');
  // entry/SL/TP order and R:R
  ok(R.satEntryOrder({ side: 'long', entry: 100, stop: 99, tp: 101.5 }).allowed, 'X R:R exactly 1.5 allowed'); has(R.satEntryOrder({ side: 'long', entry: 100, stop: 99, tp: 101.4 }), 'SAT_RR', 'X R:R 1.4 blocked'); has(R.satEntryOrder({ side: 'long', entry: 100, stop: 99 }), 'SAT_RR', 'X TP mandatory');
  has(R.satEntryOrder({ side: 'long', entry: 100, stop: 101, tp: 103 }), 'SAT_BAD_ORDER', 'X buy needs SL < Entry < TP'); ok(R.satEntryOrder({ side: 'short', entry: 100, stop: 101, tp: 98.5 }).allowed, 'X sell SL > Entry > TP');
  // queue across products
  const xau = idea({ id: 'xau', strategy: 'sat', entry: 100, stop: 99, qty: 1, status: 'ordered', product: 'XAU', working: [{ id: 'w', qty: 1, entry: 100, stop: 99, mult: 1, fx: 1, at: NOW }] });
  has(R.satQueueCheck([xau], 'main', 'btc'), 'SAT_QUEUE_BUSY', 'X XAU ordered blocks BTC'); eq(R.satQueueCheck([xau], 'main', 'xau').allowed, true, 'X same idea is not blocked by itself'); eq(R.satQueueCheck([xau], 'fam', 'btc').allowed, true, 'X queue is per account');
  xau.status = 'holding'; has(R.satQueueCheck([xau], 'main', 'btc'), 'SAT_QUEUE_BUSY', 'X holding (BE stop / partial exit) keeps the queue'); xau.status = 'closed'; eq(R.satQueueCheck([xau], 'main', 'btc').allowed, true, 'X closed releases the queue');
  const old = idea({ id: 'old', strategy: 'sat', entry: 1, stop: 0.5, qty: 1, status: 'ordered', working: [{ id: 'w9', qty: 1, entry: 1, stop: 0.5, mult: 1, fx: 1, at: NOW - D - 1 }] }); eq(R.satStaleOrders([old], NOW).length, 1, 'X order older than a day → reminder'); eq(R.satStaleOrders([Object.assign({}, old, { workingOrders: [{ id: 'w', at: NOW - D }] })], NOW).length, 0, 'X exactly one day → no reminder yet');
  // Active summary: each strategy floored at 0 separately
  const b = basis(), a = R.activeSummary({ basis: b, mom: { usageWeek: 18000, usageMonth: 18000 }, sat: { usageWeek: 12000, usageMonth: 12000 }, candidateRisk: 0 }); ok(a.allowed, 'X Active weekly: 1.80 + 1.20 = 3.00% exactly allowed'); has(R.activeSummary({ basis: b, mom: { usageWeek: 18000, usageMonth: 18000 }, sat: { usageWeek: 12000, usageMonth: 12000 }, candidateRisk: 1 }), 'ACTIVE_WEEK', 'X one more blocked');
  const neg = R.activeSummary({ basis: b, mom: { usageWeek: -5000, usageMonth: -5000 }, sat: { usageWeek: 30000, usageMonth: 30000 }, candidateRisk: 0 }); near(neg.weekUsed, 30000, 'X a profitable strategy never offsets the other'); ok(neg.allowed, 'X 30,000 = 3.00% exactly');
  has(R.activeSummary({ basis: b, mom: { usageWeek: -5000, usageMonth: -5000 }, sat: { usageWeek: 30000.01, usageMonth: 0 }, candidateRisk: 0 }), 'ACTIVE_WEEK', 'X no offset: 30,000.01 blocked');
  has(R.activeSummary({ basis: b, mom: { usageWeek: 0, usageMonth: 72000 }, sat: { usageWeek: 0, usageMonth: 48000.01 }, candidateRisk: 0 }), 'ACTIVE_MONTH', 'X Active monthly 12%');
  // Satellite open risk vs net: wins offset within Satellite
  const sw = idea({ id: 'sw1', strategy: 'sat', entry: 100, stop: 99, qty: 5000, exitPrice: 101.5, exitAt: T('2026-11-17T09:00:00'), reason: 'target' }), sl = loser(2000, { strategy: 'sat' });
  near(R.satBudgetCheck({ basis: b, now: NOW, account: 'main', ideas: [sw, sl], candidateRisk: 0 }).usageWeek, 0, 'X Satellite weekly net positive → usage 0 (floor)');
  near(R.satBudgetCheck({ basis: b, now: NOW, account: 'main', ideas: [sl], candidateRisk: 0 }).usageWeek, 2000, 'X Satellite usage = max(0, −net)');
  // costs never silently 0
  eq(R.resolveCosts({}, 'main', 'winner').known, false, 'X no cost settings → known:false'); eq(R.resolveCosts({ main: { winner: {} } }, 'main', 'winner').known, false, 'X empty cost settings → known:false'); eq(R.resolveCosts({ main: { winner: { perSidePct: 0.1 } } }, 'main', 'winner', { perUnit: 0.01 }).source, 'trade', 'X per-trade override wins');
  eq(R.exitCost(null, 1, 1, 1, 1), null, 'X unknown exit cost is null, not 0');
  const flagged = R.momentumCheck({ now: NOW, account: 'main', basis: b, ideas: [idea({ id: 'u', entry: 100, stop: 95, qty: 100, status: 'holding' })], costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 1 } }); has(flagged, 'COST_UNKNOWN', 'X missing costs flagged');
  // short-side idea result
  const shortI = idea({ id: 'sh', side: 'short', entry: 100, stop: 105, qty: 100, status: 'holding' }); near(R.ideaResult(shortI, C).principalRisk, 500, 'X short principal risk'); const be = R.netBreakevenStop(shortI, C); ok(be < 100, 'X short net-breakeven stop is below entry ' + be);
  // principal risk floored per tranche: profit-locked tranche never reduces another tranche's risk
  const two = idea({ id: 'two', entry: 100, stop: 95, qty: 100, status: 'holding' }); two.tranches.push({ id: 'tb', entry: 90, qty: 100, stop: 95, initialStop: 85, mult: 1, fx: 1, stopConfirmed: true });
  near(R.ideaResult(two, null).principalRisk, 500, 'X locked profit of tranche B does not reduce tranche A risk');
  // R multiples use the initial stop frozen at fill
  near(R.rMultiple({ entry: 100, stop: 100, initialStop: 95 }, 107.5, 'long'), 1.5, 'X 1.5R from the initial stop even after the stop moved');
  // regime unknown → treated stale
  eq(R.regimeState({ acwi: null, hyg: true, asOf: NOW }, NOW).fresh, false, 'X missing signal = not fresh');
}


// ═══ A · RE1-answers-A behaviour changes ═══
{
  const today = T('2026-11-18T10:00:00');
  const rs = d => R.regimeState({ acwi: true, hyg: true, asOf: d }, today);
  eq(rs('2026-11-18').fresh, true, 'A freshness: as-of today is fresh'); eq(rs('2026-11-14').fresh, true, 'A as-of 4 calendar days ago is fresh (Fri → Wed)'); eq(rs('2026-11-13').fresh, false, 'A 5 calendar days is stale');
  eq(rs('2026-11-14').ageDays, 4, 'A age in calendar days'); eq(rs(undefined).fresh, false, 'A missing as-of = not fresh'); eq(rs('garbage').fresh, false, 'A unparsable as-of = not fresh'); eq(rs('2026-11-19').fresh, false, 'A future as-of = not fresh');
  near(rs('2026-11-10').factor, 0.8, 'A stale caps at 80% (RM1 fallback)'); near(R.regimeState({ acwi: false, hyg: false, asOf: '2026-11-10' }, today).factor, 0.6, 'A stale both red stays 60% (cap only lowers)');
  // Bangkok calendar: 00:30 Bangkok on the 19th is 17:30 UTC on the 18th — still counts as the 19th
  eq(R.regimeState({ acwi: true, hyg: true, asOf: '2026-11-15' }, T('2026-11-19T00:30:00')).fresh, true, 'A Bangkok date used, not UTC');
  // heat: week-start equity for the cap, current equity shown too
  const hi = [idea({ id: 'ha1', strategy: 'ladder', entry: 100, stop: 95, qty: 2000, status: 'holding' })], h = R.compHeat(hi, 'main', null, 1000000, 800000);
  near(h.pct, 1, 'A heat vs week-start equity'); near(h.pctCurrent, 1.25, 'A heat also shown vs current equity'); eq(h.count, 1, 'A heat count');
  const b = R.snapshotBasis([{ at: T('2026-11-16T08:00:00'), equity: 1000000, confirmed: true }, { at: T('2026-11-18T08:00:00'), equity: 900000, confirmed: true }], today);
  near(R.compCheck({ now: today, account: 'main', basis: b, ideas: hi, cycles: [], unlocks: [], signals: { acwi: true, hyg: true, asOf: '2026-11-18' }, entry: { kind: 'pilot', requestedPct: 0.5, thesisDone: true }, candidateRisk: 0, emergencyFactor: 1 }).heat.pct, 1, 'A compCheck heat on week-start equity (not the later 900k snapshot)');
  // legacy-shape compounder cards
  ok(R.compLegacyShape({ tranches: 3 }).legacy, 'A >2 tranches = legacy shape'); ok(R.compLegacyShape({ tranches: 2, accelLots: 1 }).legacy, 'A accelerator lot = legacy shape'); ok(!R.compLegacyShape({ tranches: 2 }).legacy, 'A two tranches = normal');
  const pl = { id: 'p', entry: 100, qty: 100, stop: 95, initialStop: 95, mult: 1, fx: 1 }, okPilot = { tranche: pl, price: 107.5, stopConfirmed: true, projectedNetOk: true };
  has(R.compEntryCheck({ kind: 'pilot', legacy: true, thesisDone: false, side: 'long', usedPct: 0.5, requestedPct: 0.2, pilot: okPilot }), 'ADDON_THESIS', 'A new buy on a legacy card must pass Add-on rules (thesis)');
  has(R.compEntryCheck({ kind: 'pilot', legacy: true, thesisDone: true, side: 'long', usedPct: 1.1, requestedPct: 0.2, pilot: okPilot }), 'ADDON_TOTAL_RISK', 'A legacy card: ticker total principal risk stays within 1.25% (RM1: was 1%)');
  ok(R.compEntryCheck({ kind: 'pilot', legacy: true, thesisDone: true, side: 'long', usedPct: 0.8, requestedPct: 0.2, pilot: okPilot }).allowed, 'A legacy card: exactly 1% allowed');
  // multi-entry inside one attempt shares ONE rpt
  const at = R.sizeAttempt({ equity: E, rptPct: 0.30, factor: 1, stop: 95, side: 'long', mult: 1, fx: 1, lotStep: 1, minLot: 1, levels: [{ price: 100, splitPct: 50 }, { price: 98, splitPct: 50 }] });
  ok(at.allowed, 'A multi-entry allowed'); ok(at.actualRisk <= 3000 + 1e-6 && at.actualRisk > 2900, 'A both levels together ≈ one 0.30% budget: ' + at.actualRisk); eq(at.levels.length, 2, 'A two levels'); near(at.effectiveRptPct, 0.30, 'A one effective RPT');
  eq(R.sizeAttempt({ equity: E, rptPct: 0.30, stop: 95, side: 'long', mult: 1, fx: 1, lotStep: 1, minLot: 1, levels: [{ price: 100, splitPct: 60 }, { price: 98, splitPct: 50 }] }).allowed, false, 'A split must total 100');
  eq(R.satStepState([{ id: 'att', closeAt: NOW - 1, net: -1 }, { id: 'att', closeAt: NOW - 1, net: -2 }], NOW).step, 2, 'A a multi-entry attempt is one result for step logic');
  // history rule
  eq(R.bkk.noonOf('2026-11-13'), T('2026-11-13T12:00:00'), 'A date-only exit = 12:00 Bangkok'); eq(R.bkk.noonOf('x'), null, 'A bad date → null');
  eq(R.bkk.weekKey(R.bkk.noonOf('2026-11-15')), '2026-11-09', 'A Sunday noon belongs to the previous Bangkok week');
}

// ═══ RE-C1 · snapshot basis = latest confirmed snapshot AT OR BEFORE the period start (brief wins; a mid-week manual snapshot never replaces it) ═══
{
  const D0 = t => Date.parse(t + 'T00:00:00+07:00'), snaps = [{ at: D0('2026-11-09'), equity: 5000000, confirmed: true }, { at: D0('2026-11-18'), equity: 5300000, confirmed: true }];
  const b = R.snapshotBasis(snaps, Date.parse('2026-11-19T10:00:00+07:00'));
  eq(b.weekEquity, 5000000, 'RE-C1 mid-week manual snapshot (Wed) does NOT replace the week-start basis (Mon 16 Nov → latest at/before = 9 Nov)');
  eq(b.currentEquity, 5300000, 'RE-C1 …but it is the current equity');
  eq(b.monthEquity, 5000000, 'RE-C1 month basis = latest at/before 1 Nov → earliest available (first run), flagged');
  ok(b.flags.indexOf('BASIS_FIRST') >= 0, 'RE-C1 no snapshot before the month start → BASIS_FIRST');
  const b2 = R.snapshotBasis(snaps.concat([{ at: D0('2026-11-16'), equity: 5100000, confirmed: true }]), Date.parse('2026-11-19T10:00:00+07:00'));
  eq(b2.weekEquity, 5100000, 'RE-C1 a snapshot dated Monday (as-of Monday 00:00) IS the week-start basis');
}

// ═══ AU2 · DD_STOP — 20% below the reference stops NEW entries (all strategies); recovery steps stop → half size → full ═══
{
  const nov = T('2026-11-01T09:00:00'), mref = { equity: 1000000, at: nov }, at = T('2026-11-12T20:00:00'), step = (st, eqv, ref) => R.emergencyStep(st, { at, equity: eqv, confirmed: true }, ref || mref, []);
  eq(R.POLICY.emergency.stopPct, 20, 'AU2 stopPct 20');
  let s = step(null, 810000); ok(s.active && !s.stopped && s.factor === 0.5, 'AU2 −19% → half size only, no stop');
  s = step(null, 800000); ok(s.stopped && s.active && s.factor === 0.5, 'AU2 exactly −20% → stopped (and half size state kept)'); near(s.declinePct, 20, 'AU2 decline 20');
  s = step(null, 799999); ok(s.stopped, 'AU2 below −20% → stopped');
  s = step(null, 800001); ok(!s.stopped, 'AU2 −19.9999% does not stop');
  let st = step(null, 780000);
  s = step(st, 840000); ok(s.stopped && s.active, 'AU2 −16% still stopped (recovers only above −15%)');
  s = step(s, 850000); ok(s.stopped, 'AU2 exactly −15% still stopped');
  s = step(s, 850001); ok(!s.stopped && s.active && s.factor === 0.5, 'AU2 above −15% → stop lifted, half size remains');
  s = step(s, 950001); ok(!s.stopped && !s.active && s.factor === 1, 'AU2 above −5% → full size');
  s = R.emergencyStep(null, { at, equity: 700000, confirmed: false }, mref, []); ok(!s.stopped, 'AU2 unconfirmed snapshot ignored');
  // the three checks refuse new orders; fills / reductions / stop moves stay allowed
  const b = basis(), mom = R.momentumCheck({ now: NOW, account: 'main', basis: b, ideas: [], costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 10 }, ddStop: true });
  has(mom, 'DD_STOP', 'AU2 Momentum blocked'); ok(!mom.allowed, 'AU2 Momentum not allowed');
  no(R.momentumCheck({ now: NOW, account: 'main', basis: b, ideas: [], costsFor: costsNone, candidate: { ideaId: 'n', riskMoney: 10 }, ddStop: false }), 'DD_STOP', 'AU2 off → no DD_STOP');
  has(R.satCheck({ now: NOW, account: 'main', basis: b, ideas: [], attempts: [], condition: { trend: 'ok' }, order: {}, candidateRisk: 1, ddStop: true }), 'DD_STOP', 'AU2 Satellite blocked');
  has(R.compCheck({ now: NOW, account: 'main', basis: b, ideas: [], cycles: [], unlocks: [], signals: { acwi: true, hyg: true, asOf: '2026-11-18' }, entry: { kind: 'pilot', requestedPct: 0.5, thesisDone: true }, emergencyFactor: 1, ddStop: true }), 'DD_STOP', 'AU2 Compounder blocked');
  ok(R.REASONS.DD_STOP && R.REASONS.DD_STOP.kind === 'block' && /20% below its peak/.test(R.REASONS.DD_STOP.text), 'AU2 reason text');
  const blk = { reasons: ['DD_STOP'], flags: [] };
  ['order', 'addon', 'topup', 'edit_increase'].forEach(a => ok(R.actionPolicy(a, blk).accepted === false, 'AU2 ' + a + ' refused'));
  ['fill', 'close', 'reduce', 'partial_close', 'stop_update', 'cancel'].forEach(a => ok(R.actionPolicy(a, blk).accepted === true, 'AU2 ' + a + ' always allowed'));
}

console.log((f ? 'FAIL ' : 'PASS ') + (n - f) + '/' + n + ' risk-engine assertions');
process.exit(f ? 1 : 0);
