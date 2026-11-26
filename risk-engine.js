/* risk-engine.js — RE1 risk engine (pure functions · no DOM / clock / storage / network)
   Spec: docs/briefs/RE1-decisions.md (rev 2) + docs/briefs/RE1-tech-spec.md. RE-A: NOT wired into index.html.
   Used two ways: Node (module.exports) for tests · browser (globalThis.RiskEngine).
   Conventions
   - Every function takes plain data (time `now` = epoch ms and all state are passed in) and returns plain data. Never throws on bad input:
     missing / invalid data -> reasons[] with an UNKNOWN-style code, never a silent 0.
   - Percentages are plain numbers (0.40 = 0.40 %). Money is one account base currency; FX is fixed per snapshot and passed per tranche.
   - Strategy keys = the dashboard's keys: winner = Momentum · sat = Satellite · ladder = Compounder.
   - Result shape of every check: {allowed, reasons:[code], flags:[code], ...detail}. reasons = block a NEW risk-increasing order;
     flags = information / breach markers. Fills, reductions, exits and stop updates are never blocked (see actionPolicy / asFill).
   - Time zone is fixed Asia/Bangkok (UTC+7, no DST): day 00:00 · week Monday 00:00 · month day 1 00:00. Machine time zone is never read. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.RiskEngine = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var EPS = 1e-9, MEPS = 1e-7;                /* ratio tolerance · money tolerance */
  var HR = 3600000, DAY = 86400000, BKK = 7 * HR;

  /* ── Policy constants (RE1-decisions.md §1-§5). Overridable per call via cfg. ── */
  var POLICY = {
    mom: { rptPct: 0.40, weeklyPct: 1.60, monthlyPct: 6.40, ammo: 4, homeworkCap: 0.7, starter: 0.25, releaseR: 1.5 },
    sat: { stepRpt: [0.20, 0.20, 0.20, 0.20], weeklyPct: 0.80, monthlyPct: 3.20, condReduced: 0.65, minRR: 1.5, staleOrderMs: DAY, maxActive: 3, newSetupRiskCut: 0.50 },   /* HF5 — queue: max live Sat setups per account · a new one needs every live setup's risk cut >= this share */
    comp: { pilotPct: 0.50, addonPct: 0.50, totalCapPct: 1.00, valueCapPct: 12.5, heatCapPct: 6.0, starter: 0.25, lockLosses: 6, unlockDays: 7, homeworkCap: 1.0 },
    /* PC2 2e — homework factor per strategy track when homework is NOT done (done = 100 %). Compounder: full size (homework unlocks adds + risk above 1 %). Momentum: 70 %. */
    hwFactor: { comp: 1.00, mom: 0.70 },
    /* PC2 — constants (not Settings) */
    compRiskMax: 2.0, compHighMaxOpen: 2, momTopupDays: 5,
    /* RM1 — shared new-entry budget modifier ("initial settings to test"). One signal result feeds sizing AND every view.
       table[equity][credit]: green/red of ACWI/BIL (SMA 20/50) x HYG/IEI (SMA 20/50). Neutral / unavailable / stale -> fallback (never 100 %). All values + SMA periods are settings (rev 4: 100/80/80/60, fallback 80). */
    regime: { table: { green: { green: 1.0, red: 0.80 }, red: { green: 0.80, red: 0.60 } }, fallback: 0.80, freshDays: 4, smaFast: 20, smaSlow: 50 },
    active: { weeklyPct: 3.0, monthlyPct: 12.0 },
    emergency: { triggerPct: 10, recoverPct: 5, factor: 0.5, stopPct: 20, stopRecoverPct: 15 },   /* AU2: DD_STOP vs the confirmed-equity PEAK (ddStopStep) — stops at 20 %, lifts within 15 %; the 10 % half-size rule keeps its month-start basis */
    snapshot: { blockAfterDays: 14 }
  };
  /* RK1 — risk per idea (Settings). One set for both accounts. New plans only: saved plans / holdings keep their stored risk and qty.
     weekly = 4 x per-idea · monthly = 4 x weekly (so the money check and the 4-loss count stop at the same point). Sat: every step = the fixed value (the step machine + lock after the 4th loss stay). */
  /* CP1 — Compounder buys when the market rests. ONE place for both constants.
     MARKET_PULLBACK_PCT: SPY (US stocks) or SET (Thai stocks) this far below its 52-week high = a pullback (an opportunity, not a reason to fear).
     COMP_REGIME_FACTOR: Compounder-only size modifier from the two regime signals (green = both green · oneRed · bothRed · fallback = stale / unknown data, never 100 %).
     CP1: Momentum and Sat keep POLICY.regime (100 / 80 / 60). */
  var MARKET_PULLBACK_PCT = 7;
  var COMP_REGIME_FACTOR = { green: 1.00, oneRed: 1.00, bothRed: 0.75, fallback: 0.75 };
  var RISK_DEFAULTS = { compTotal: 1.00, compFirst: 0.50, mom: 0.40, sat: 0.20 };
  var RISK_BOUNDS = { compTotal: [0.50, 1.50], mom: [0.20, 0.60], sat: [0.10, 0.40] };
  function r6(x) { return Math.round(x * 1e6) / 1e6; }
  function riskValidate(c) {
    c = c || {}; var e = [], D = RISK_DEFAULTS;
    var v = { compTotal: c.compTotal == null ? D.compTotal : Number(c.compTotal), compFirst: c.compFirst == null ? D.compFirst : Number(c.compFirst),
      mom: c.mom == null ? D.mom : Number(c.mom), sat: c.sat == null ? D.sat : Number(c.sat) };
    ['compTotal', 'mom', 'sat'].forEach(function (k) { var b = RISK_BOUNDS[k]; if (!num(v[k]) || v[k] < b[0] - EPS || v[k] > b[1] + EPS) e.push({ key: k, code: 'OUT_OF_BOUNDS', min: b[0], max: b[1] }); });
    if (!num(v.compFirst) || v.compFirst <= 0) e.push({ key: 'compFirst', code: 'OUT_OF_BOUNDS', min: 0.01, max: v.compTotal });
    else if (num(v.compTotal) && v.compFirst > v.compTotal + EPS) e.push({ key: 'compFirst', code: 'FIRST_ABOVE_TOTAL', min: 0.01, max: v.compTotal });
    return { ok: e.length === 0, errors: e, values: v };
  }
  /* applyRisk(cfg) — sets POLICY from the settings values (invalid -> nothing changes, errors returned). applyRisk() / applyRisk(null) = defaults. */
  function applyRisk(c) {
    var v = riskValidate(c); if (!v.ok) return v; var x = v.values;
    POLICY.comp.totalCapPct = r6(x.compTotal); POLICY.comp.pilotPct = r6(x.compFirst); POLICY.comp.addonPct = r6(x.compFirst);
    POLICY.mom.rptPct = r6(x.mom); POLICY.mom.weeklyPct = r6(4 * x.mom); POLICY.mom.monthlyPct = r6(16 * x.mom);
    POLICY.sat.stepRpt = [r6(x.sat), r6(x.sat), r6(x.sat), r6(x.sat)]; POLICY.sat.weeklyPct = r6(4 * x.sat); POLICY.sat.monthlyPct = r6(16 * x.sat);
    return v;
  }
  function riskDerived() { return { momWeekly: POLICY.mom.weeklyPct, momMonthly: POLICY.mom.monthlyPct, satWeekly: POLICY.sat.weeklyPct, satMonthly: POLICY.sat.monthlyPct }; }
  var STRATS = { winner: 'winner', mom: 'winner', momentum: 'winner', sat: 'sat', satellite: 'sat', ladder: 'ladder', comp: 'ladder', compounder: 'ladder' };

  /* ── Reason codes (every block / flag the engine can emit). kind: block = refuses a NEW risk-increasing order · flag = marker / warning. ── */
  var REASONS = {
    NO_SNAPSHOT:        { kind: 'block', text: 'No confirmed equity snapshot for this account' },
    SNAPSHOT_STALE:     { kind: 'block', text: 'Last confirmed snapshot is older than 14 days' },
    SNAPSHOT_OLD:       { kind: 'flag',  text: 'No snapshot for the current period — using the last confirmed one' },
    EQUITY_MISSING:     { kind: 'block', text: 'Equity basis missing or not positive' },
    FX_MISSING:         { kind: 'block', text: 'FX rate missing for a non-base currency' },
    SPEC_MISSING:       { kind: 'block', text: 'Contract multiplier / lot step / minimum lot missing' },
    PRICE_MISSING:      { kind: 'block', text: 'Entry or stop missing' },
    STOP_EQUALS_ENTRY:  { kind: 'block', text: 'Stop equals entry' },
    STOP_WRONG_SIDE:    { kind: 'block', text: 'Stop is on the wrong side of entry for this direction' },
    LOT_BELOW_MIN:      { kind: 'block', text: 'Budget does not cover the minimum lot' },
    COST_UNKNOWN:       { kind: 'flag',  text: 'Cost settings missing — costs not estimated (never treated as 0)' },
    CAP_HOMEWORK:       { kind: 'flag',  text: 'Homework not done — size limited to 70% of full' },
    MONEY_WEEK:         { kind: 'block', text: 'Weekly loss budget would be exceeded' },
    MONEY_MONTH:        { kind: 'block', text: 'Monthly loss budget would be exceeded' },
    AMMO_EXHAUSTED:     { kind: 'block', text: 'Weekly Momentum ammunition (4) used or reserved' },
    AMMO_OVERSHOOT:     { kind: 'flag',  text: 'Weekly losing-idea count is above 4 (accepted, new risk restricted)' },
    ACTIVE_WEEK:        { kind: 'block', text: 'Active (Momentum + Satellite) weekly 3% summary check exceeded' },
    ACTIVE_MONTH:       { kind: 'block', text: 'Active (Momentum + Satellite) monthly 12% summary check exceeded' },
    COMP_VALUE_CAP:     { kind: 'block', text: 'Position value would exceed the 12.5% of account value cap' },
    SAT_LOCKED:         { kind: 'block', text: 'Satellite locked after a loss at Step 4 until the weekly reset' },
    SAT_QUEUE_BUSY:     { kind: 'block', text: 'Another Satellite setup still has most of its risk in this account' },
    SAT_QUEUE_MAX:      { kind: 'block', text: 'Maximum Satellite setups are open in this account' },
    SAT_DAILY_LIMIT:    { kind: 'block', text: 'One setup per product per day already used' },
    SAT_REENTRY_USED:   { kind: 'block', text: 'Re-entry already used today for this product' },
    SAT_REENTRY_COND:   { kind: 'block', text: 'Re-entry conditions not met' },
    SAT_COND_INCOMPLETE:{ kind: 'block', text: 'EMA50 / Structure not both selected' },
    SAT_COND_BLOCKED:   { kind: 'block', text: 'Trend/MSS: no MSS — setup not allowed' },
    SAT_REENTRY_TAG:    { kind: 'flag',  text: 'Re-entry (one extra confirm applied)' },
    SAT_NEAREST_TARGET: { kind: 'flag',  text: 'Reduced condition: exit at the nearest key target' },
    SAT_STALE_ORDER:    { kind: 'flag',  text: 'Working order older than one day — still valid?' },
    SAT_BAD_ORDER:      { kind: 'block', text: 'Entry / SL / TP order invalid for the direction' },
    SAT_RR:             { kind: 'block', text: 'R:R below 1.5 or TP missing' },
    COMP_LOCKED:        { kind: 'block', text: 'Compounder locked after six consecutive losing ticker-cycles' },
    COMP_HEAT:          { kind: 'block', text: 'Compounder heat cap 6% would be exceeded' },
    PLAN_TOTAL_RISK:    { kind: 'block', text: 'Total risk is over today\'s limit' },
    ADDON_THESIS:       { kind: 'block', text: 'Thesis not complete — Add-on / further buys need it' },
    ADDON_TOTAL_RISK:   { kind: 'block', text: 'Ticker total risk (existing tranches at current stop + this order) would exceed the plan limit' },
    ADDON_BELOW_ENTRY_WARN: { kind: 'flag', text: 'Adding below entry — re-check ④ Wrong if' },
    COMP_PHASE_CAP:     { kind: 'block', text: 'Above the allowed risk for the current phase' },
    COMP_REGIME_STALE:  { kind: 'flag',  text: 'Regime data stale — size capped at 75%' },
    COMP_UNLOCK_WAIT:   { kind: 'block', text: 'Unlock needs at least 7 days after the sixth loss closed' },
    COMP_UNLOCK_SIGNALS:{ kind: 'block', text: 'Unlock needs both regime signals green' },
    COMP_UNLOCK_STALE:  { kind: 'block', text: 'Unlock blocked: regime data not fresh' },
    COMP_UNLOCK_NOTE:   { kind: 'block', text: 'Unlock needs a written review note' },
    COMP_UNLOCK_CONFIRM:{ kind: 'block', text: 'Unlock needs an explicit confirm' },
    DD_STOP:            { kind: 'block', text: 'Account is 20% below its peak · new entries stopped' },
    EMERGENCY_ON:       { kind: 'flag',  text: 'Emergency: risk factor 0.5' },
    FILL_OVER_LIMIT:    { kind: 'flag',  text: 'Actual fill exceeds a limit — accepted, new risk restricted' },
    UNKNOWN_DATA:       { kind: 'block', text: 'Required data missing' }
  };

  /* ── helpers ── */
  function num(x) { return typeof x === 'number' && isFinite(x); }
  function pos(x) { return num(x) && x > 0; }
  function str(x) { return typeof x === 'string' && x.trim().length > 0; }
  function strat(k) { return STRATS[String(k || '').toLowerCase()] || null; }
  function res(reasons, flags, extra) {
    var o = extra || {}; o.reasons = uniq(reasons); o.flags = uniq(flags || []); o.allowed = o.reasons.length === 0; return o;
  }
  function uniq(a) { var s = {}, o = []; a.forEach(function (x) { if (!s[x]) { s[x] = 1; o.push(x); } }); return o; }
  function merge(a, b) { var o = {}, k; a = a || {}; b = b || {}; for (k in a) o[k] = a[k]; for (k in b) o[k] = b[k]; return o; }
  function pol(cfg) { return merge(POLICY, cfg); }
  function floorLot(q, lot) {
    if (!num(q) || q <= 0) return 0; lot = lot > 0 ? lot : 1;
    var v = Math.floor(q / lot + EPS) * lot; return Math.round(v * 1e8) / 1e8;
  }
  function dirOf(side) { return String(side).toLowerCase() === 'short' || side === 'Sell' || side === 'sell' ? -1 : 1; }
  function leq(a, b) { return a <= b + MEPS; }

  /* ═══ 1. Time — Asia/Bangkok, pure arithmetic ═══ */
  function dayStart(ms) { return Math.floor((ms + BKK) / DAY) * DAY - BKK; }
  function weekStart(ms) { var i = Math.floor((ms + BKK) / DAY), dow = ((i + 3) % 7 + 7) % 7; return (i - dow) * DAY - BKK; }   /* Monday 00:00 */
  function monthStart(ms) { var d = new Date(ms + BKK); return Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1) - BKK; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function dayKey(ms) { var d = new Date(ms + BKK); return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()); }
  function weekKey(ms) { return dayKey(weekStart(ms)); }
  function monthKey(ms) { return dayKey(monthStart(ms)).slice(0, 7); }
  /* date-only exit (history) = 12:00 Asia/Bangkok of that date (RE1-answers-A #9) */
  function noonOf(dateStr) { return /^\d{4}-\d{2}-\d{2}/.test(String(dateStr)) ? Date.parse(String(dateStr).slice(0, 10) + 'T12:00:00+07:00') : null; }
  var bkk = { noonOf: noonOf, dayStart: dayStart, weekStart: weekStart, monthStart: monthStart, dayKey: dayKey, weekKey: weekKey, monthKey: monthKey,
    nextWeekStart: function (ms) { return weekStart(ms) + 7 * DAY; } };

  /* ═══ 2. Strict sign rule ═══ net after fees and swap: <0 loss · >0 win · =0 breakeven. No tolerance band. ═══ */
  function outcome(net) { return num(net) ? (net < 0 ? 'loss' : net > 0 ? 'win' : 'be') : null; }

  /* ═══ 3. Costs. cost settings = {perSidePct, perUnit, min, flat} (money, account currency) — resolved per account + strategy, per-trade override wins.
        Missing settings => known:false (amount null). NEVER 0. ═══ */
  function resolveCosts(settings, account, strategy, override) {
    var src = null, k = strat(strategy);
    if (override && typeof override === 'object') src = override;
    else if (settings && settings[account] && k && settings[account][k]) src = settings[account][k];
    if (!src) return { known: false };
    if (!(num(src.perSidePct) || num(src.perUnit) || num(src.min) || num(src.flat))) return { known: false };
    return { known: true, perSidePct: num(src.perSidePct) ? src.perSidePct : 0, perUnit: num(src.perUnit) ? src.perUnit : 0,
      min: num(src.min) ? src.min : 0, flat: num(src.flat) ? src.flat : 0, source: override ? 'trade' : 'account' };
  }
  function exitCost(costs, qty, price, mult, fx) {
    if (!costs || costs.known !== true) return null;
    if (!(qty > 0)) return 0;
    var c = qty * price * (mult || 1) * (fx || 1) * costs.perSidePct / 100 + qty * costs.perUnit;
    return Math.max(c, costs.min) + costs.flat;
  }

  /* ═══ 4. Idea-level math ═══
     idea = {id, account, strategy, side, status, tranches:[{id, entry, qty, stop, initialStop, mult, fx, stopConfirmed}],
             exits:[{id, time, qty, price, fees, swap, trancheId}], entryFees (money, default 0), workingOrders:[{id, qty, entry, stop, mult, fx, at}]}
     fees / swap are COSTS (positive = money paid; negative swap = credit). */
  function trancheUV(t) { return (num(t.mult) && t.mult > 0 ? t.mult : 1) * (num(t.fx) && t.fx > 0 ? t.fx : 1); }
  function exitedQty(idea, trId) {
    var q = 0; (idea.exits || []).forEach(function (e) { if (trId == null || e.trancheId == null || e.trancheId === trId) q += e.qty || 0; }); return q;
  }
  function remainingQtyOf(idea, tr) {
    var q = tr.qty, ex = 0, multi = (idea.tranches || []).length > 1;
    (idea.exits || []).forEach(function (e) { if (e.trancheId === tr.id || (e.trancheId == null && !multi)) ex += e.qty || 0; });
    return Math.max(0, q - ex);
  }
  function exitGross(idea, e) {
    var tr = null, multi = (idea.tranches || []).length > 1;
    (idea.tranches || []).forEach(function (t) { if (t.id === e.trancheId || (e.trancheId == null && !multi)) tr = t; });
    if (!tr) { tr = (idea.tranches || [])[0]; }
    if (!tr) return 0;
    return (e.price - tr.entry) * dirOf(idea.side) * e.qty * trancheUV(tr);
  }
  /* net of one exit event (entry fees are NOT in here — they are attributed in realizedEvents) */
  function exitNet(idea, e) { return exitGross(idea, e) - (e.fees || 0) - (e.swap || 0); }
  /* realized events for period attribution: every exit event with its net; entry fees charged to the FIRST exit event (by time, id). */
  function realizedEvents(idea) {
    var ex = (idea.exits || []).slice().sort(function (a, b) { return a.time - b.time || String(a.id) < String(b.id) ? -1 : 1; });
    return ex.map(function (e, i) { return { id: e.id, time: e.time, net: exitNet(idea, e) - (i === 0 ? (idea.entryFees || 0) : 0) }; });
  }
  function ideaRealizedNet(idea) {
    var s = 0, ev = realizedEvents(idea); ev.forEach(function (e) { s += e.net; });
    if (!ev.length) s -= (idea.entryFees || 0);
    return s;
  }
  function ideaStatusOf(idea) { return idea.status; }
  function liveTranches(idea) {
    return (idea.tranches || []).map(function (t) { return { t: t, q: remainingQtyOf(idea, t) }; }).filter(function (x) { return x.q > 0; });
  }
  /* projected result of the idea if every remaining tranche exits at its current stop.
     = realized (partial exits + incurred fees/swap) + stop-P&L of remaining + estimated remaining exit costs. Unknown costs => projectedNet null. */
  function ideaResult(idea, costs) {
    var dir = dirOf(idea.side), realized = ideaRealizedNet(idea), live = liveTranches(idea), stopPnl = 0, principal = 0, estCost = 0, unknown = false, missingStop = false;
    live.forEach(function (x) {
      var t = x.t, uv = trancheUV(t);
      if (!pos(t.stop)) { missingStop = true; return; }
      var p = (t.stop - t.entry) * dir * x.q * uv;
      stopPnl += p; principal += Math.max(0, -p);
      var c = exitCost(costs, x.q, t.stop, t.mult, t.fx);
      if (c === null) unknown = true; else estCost += c;
    });
    var out = { realizedNet: realized, stopPnl: stopPnl, principalRisk: principal, remainingQty: live.reduce(function (s, x) { return s + x.q; }, 0),
      costUnknown: unknown, unknownStop: missingStop, estExitCost: unknown ? null : estCost };
    out.projectedNet = (unknown || missingStop) ? null : realized + stopPnl - estCost;
    /* money exposure still to come. Per tranche: loss at its stop after its own exit cost and its share of not-yet-attributed entry fees, floored at 0
       (no cross-tranche offset). Reduced only by realized profit of the same idea. Realized losses are NOT here (they are in the realized term).
       Unknown cost => exposure falls back to principal only (flagged by costUnknown) · unknown stop => null. */
    if (missingStop) out.exposure = null;
    else {
      var pend = (idea.exits || []).length ? 0 : (idea.entryFees || 0), totQ = live.reduce(function (s, x) { return s + x.q; }, 0), ex = 0;
      live.forEach(function (x) {
        var t = x.t, uv = trancheUV(t), p = (t.stop - t.entry) * dir * x.q * uv, c = exitCost(costs, x.q, t.stop, t.mult, t.fx);
        ex += Math.max(0, -(p - (c === null ? 0 : c) - (totQ > 0 ? pend * x.q / totQ : 0)));
      });
      var realizedExits = 0; realizedEvents(idea).forEach(function (e) { realizedExits += e.net; });
      out.exposure = Math.max(0, ex - Math.max(0, realizedExits));
    }
    return out;
  }
  /* estimated net-breakeven stop for the remaining quantity (single stop for all live tranches) — null if nothing live / unknown costs */
  function netBreakevenStop(idea, costs) {
    var dir = dirOf(idea.side), live = liveTranches(idea); if (!live.length) return null;
    if (!costs || costs.known !== true) return null;
    var W = 0, WE = 0, qty = 0, mv = 0;
    live.forEach(function (x) { var uv = trancheUV(x.t); W += x.q * uv; WE += x.q * uv * x.t.entry; qty += x.q; mv += uv; });
    var Ew = WE / W, realized = ideaRealizedNet(idea), s = Ew;
    for (var i = 0; i < 40; i++) {
      var c = exitCost(costs, qty, s, mv / live.length, 1) || 0;   /* uv already holds mult*fx: use price*uv via mult=uv/qty-weighted */
      c = exitCostUV(costs, qty, s, W / qty);
      var ns = Ew + (c - realized) / (dir * W);
      if (Math.abs(ns - s) < 1e-10) { s = ns; break; } s = ns;
    }
    return s;
  }
  function exitCostUV(costs, qty, price, uvAvg) {
    return Math.max(qty * price * uvAvg * costs.perSidePct / 100 + qty * costs.perUnit, costs.min) + costs.flat;
  }
  /* Option C: the ammunition reservation is released only when the CONFIRMED stop projects net >= 0 (strict, costs included).
     Re-evaluated whenever the caller recomputes (events: confirmed stop change, qty change, partial exit, addition, cost edit). */
  function ammoReleased(idea, costs) {
    var live = liveTranches(idea); if (!live.length) return false;
    if (!live.every(function (x) { return x.t.stopConfirmed === true; })) return false;
    var r = ideaResult(idea, costs);
    return r.projectedNet !== null && r.projectedNet >= -MEPS;
  }
  /* R multiple of the first tranche at a price, from the initial stop frozen at fill */
  function rMultiple(tr, price, side) {
    var d = Math.abs(tr.entry - (pos(tr.initialStop) ? tr.initialStop : tr.stop)); if (!(d > 0) || !pos(price)) return null;
    return (price - tr.entry) * dirOf(side) / d;
  }

  /* ═══ 5. Snapshots & basis ═══
     snapshots = [{at, equity, fx?, confirmed}] per account (caller filters the account — accounts never mix). */
  function snapshotBasis(snapshots, now, cfg) {
    var P = pol(cfg), list = (snapshots || []).filter(function (s) { return s && s.confirmed === true && pos(s.equity) && num(s.at) && s.at <= now; })
      .sort(function (a, b) { return a.at - b.at; });
    if (!list.length) return { ok: false, state: 'none', reasons: ['NO_SNAPSHOT'], flags: [] };
    var last = list[list.length - 1], ageDays = (now - last.at) / DAY;
    if (ageDays > P.snapshot.blockAfterDays + EPS) return { ok: false, state: 'stale', ageDays: ageDays, snapshot: last, reasons: ['SNAPSHOT_STALE'], flags: [] };
    var ws = weekStart(now), ms = monthStart(now);
    /* RE-C1 (brief wins): week-start / month-start basis = the LATEST confirmed snapshot at or before the period start (a snapshot's `at` is its as-of date, 00:00 Bangkok).
       None at or before the start (first run) → the earliest confirmed one, flagged BASIS_FIRST. A mid-week snapshot never replaces the week-start basis. */
    function pick(from) { var c = null; list.forEach(function (s) { if (s.at <= from) c = s; }); return c || list[0]; }
    var wk = pick(ws), mo = pick(ms), flags = [];
    if (last.at < ws) flags.push('SNAPSHOT_OLD');
    if (wk.at > ws || mo.at > ms) flags.push('BASIS_FIRST');
    return { ok: true, state: last.at < ws ? 'carried' : 'current', ageDays: ageDays, snapshot: last,
      weekEquity: wk.equity, weekAt: wk.at, monthEquity: mo.equity, monthAt: mo.at,
      currentEquity: last.equity, reasons: [], flags: flags };
  }

  /* ═══ 6. Emergency ═══
     state = {active, refEquity, refStartMs} · flows = [{at, amount}] (+deposit / −withdrawal) · snapshot = {at, equity, confirmed}
     monthStartEquity = month-start basis = the latest confirmed snapshot at or before day 1 00:00 Bangkok (caller: snapshotBasis().monthEquity / monthAt; brief RE-C1 §1).
     Trigger: cash-flow-adjusted decline >= 10 % from the reference. Keeps its reference across month change until adjusted decline is above −5 %. */
  function flowsSince(flows, fromMs, toMs) { var s = 0; (flows || []).forEach(function (f) { if (f && num(f.amount) && f.at > fromMs && f.at <= toMs) s += f.amount; }); return s; }
  function emergencyStep(state, snap, monthRef, flows, cfg) {
    var E = pol(cfg).emergency, st = { active: !!(state && state.active), refEquity: state && state.refEquity, refStartMs: state && state.refStartMs };
    if (!snap || !snap.confirmed || !pos(snap.equity)) return merge(st, { factor: st.active ? E.factor : 1, changed: false, declinePct: null });
    var ref = st.active ? { equity: st.refEquity, at: st.refStartMs } : (monthRef && pos(monthRef.equity) ? { equity: monthRef.equity, at: monthRef.at } : null);
    if (!ref) return merge(st, { factor: st.active ? E.factor : 1, changed: false, declinePct: null });
    var adj = snap.equity - flowsSince(flows, ref.at, snap.at), dec = (ref.equity - adj) / ref.equity * 100, was = st.active, changed = false;
    if (!st.active && dec >= E.triggerPct - EPS) { st.active = true; st.refEquity = ref.equity; st.refStartMs = ref.at; changed = true; }
    else if (st.active && dec < E.recoverPct - EPS) { st.active = false; st.refEquity = null; st.refStartMs = null; changed = true; }
    return merge(st, { factor: st.active ? E.factor : 1, changed: changed, declinePct: dec, was: was });
  }
  /* AU2 — DD_STOP: drawdown from the PEAK (high-water mark) of confirmed equity snapshots, cash-flow adjusted (deposits / withdrawals never move it).
     Flows after the first snapshot only. Performance equity P(t) = equity(t) − Σflows(first, t]. peakP = max P (floored by the stored state.peakP).
     Drawdown now = (peakP − P_now) / (peakP + F_now) — the peak expressed in today's capital. Stops at >= stopPct; lifts when back within stopRecoverPct of the peak.
     snaps = [{at, equity, confirmed}] (any order) · flows = [{at, amount}] · state = {peakP, peakAt, stopped} (stored per account, optional). */
  function ddStopStep(state, snaps, flows, cfg) {
    var E = pol(cfg).emergency, list = (snaps || []).filter(function (x) { return x && x.confirmed !== false && !x.provisional && num(x.at) && pos(x.equity); }).sort(function (a, b) { return a.at - b.at; });
    var peakP = state && num(state.peakP) ? state.peakP : null, peakAt = state && num(state.peakAt) ? state.peakAt : null, stopped = false, dd = null, F = 0;
    if (!list.length) return { stopped: false, ddPct: null, peakP: peakP, peakAt: peakAt, peakEquity: null, flowAdj: 0 };
    var t0 = list[0].at;
    list.forEach(function (sn) {
      F = flowsSince(flows, t0, sn.at); var P = sn.equity - F;
      if (peakP === null || P > peakP + EPS) { peakP = P; peakAt = sn.at; }
      var den = peakP + F; dd = den > 0 ? (peakP - P) / den * 100 : null;
      if (dd !== null) { if (!stopped && dd >= E.stopPct - EPS) stopped = true; else if (stopped && dd <= E.stopRecoverPct + EPS) stopped = false; }
    });
    return { stopped: stopped, ddPct: dd, peakP: peakP, peakAt: peakAt, peakEquity: peakP + F, flowAdj: F };
  }

  /* ═══ 7. Sizing (all strategies) ═══
     o = {equity (basis: week-start snapshot), rptPct, factor (cond × emergency or min(regime, emergency)), fraction (homework / starter, 0..1, default 1),
          entry, stop, side, minStopDist (optional, price units), mult, fx, lotStep, minLot}
     sizing distance = max(actual |entry−stop|, minStopDist); risk and results use the ACTUAL stop; the user's stop is never moved. */
  function sizeOrder(o) {
    o = o || {}; var blocks = [], flags = [];
    if (!pos(o.equity)) blocks.push('EQUITY_MISSING');
    if (!(pos(o.entry) && pos(o.stop))) blocks.push('PRICE_MISSING');
    else if (o.entry === o.stop) blocks.push('STOP_EQUALS_ENTRY');
    else if (o.side && ((dirOf(o.side) === 1 && o.stop > o.entry) || (dirOf(o.side) === -1 && o.stop < o.entry))) blocks.push('STOP_WRONG_SIDE');
    if (!(pos(o.mult) && pos(o.lotStep) && num(o.minLot) && o.minLot >= 0)) blocks.push('SPEC_MISSING');
    if (!(pos(o.fx))) blocks.push('FX_MISSING');
    if (!pos(o.rptPct)) blocks.push('UNKNOWN_DATA');
    if (blocks.length) return { allowed: false, reasons: uniq(blocks), flags: [], qty: 0 };
    var factor = num(o.factor) && o.factor >= 0 ? o.factor : 1, frac = num(o.fraction) ? Math.max(0, Math.min(1, o.fraction)) : 1;
    var actual = Math.abs(o.entry - o.stop), sd = Math.max(actual, pos(o.minStopDist) ? o.minStopDist : 0), uv = o.mult * o.fx;
    var eff = o.rptPct * factor, budget = o.equity * eff / 100;
    var q0 = floorLot(budget / (sd * uv), o.lotStep), q = floorLot(q0 * frac, o.lotStep);
    var below = q < (o.minLot || 0) - 1e-12 || q <= 0;
    if (frac < 1) flags.push('CAP_HOMEWORK');
    return res(below ? ['LOT_BELOW_MIN'] : [], flags, { qty: below ? 0 : q, qtyFull: q0, effectiveRptPct: eff, budget: budget, sizingDistance: sd, actualDistance: actual,
      actualRisk: below ? 0 : q * actual * uv, actualRiskPct: below ? 0 : q * actual * uv / o.equity * 100, minStopApplied: sd > actual + EPS, notional: below ? 0 : q * o.entry * uv });
  }
  /* One attempt with several entry levels (PB1 multi-entry): ONE effective RPT for the whole attempt, shared by the levels by the user's split.
     o = sizeOrder inputs without entry + {levels:[{price, splitPct}]} (splitPct sum must be 100). Each level is floored to the lot separately; total risk <= one budget. */
  function sizeAttempt(o) {
    o = o || {}; var L = o.levels || [], sum = 0, out = [], flags = [], reasons = [];
    L.forEach(function (l) { sum += num(l.splitPct) ? l.splitPct : 0; });
    if (!L.length || Math.abs(sum - 100) > 1e-6) return { allowed: false, reasons: ['UNKNOWN_DATA'], flags: [], levels: [] };
    var tot = 0, qtyTot = 0;
    L.forEach(function (l) {
      var r = sizeOrder(merge(o, { entry: l.price, rptPct: o.rptPct * l.splitPct / 100 }));
      out.push({ price: l.price, splitPct: l.splitPct, qty: r.qty, actualRisk: r.actualRisk, reasons: r.reasons });
      reasons = reasons.concat(r.reasons); tot += r.actualRisk || 0; qtyTot += r.qty || 0; flags = flags.concat(r.flags);
    });
    return res(reasons, flags, { levels: out, actualRisk: tot, actualRiskPct: pos(o.equity) ? tot / o.equity * 100 : null, qty: qtyTot, effectiveRptPct: o.rptPct * (num(o.factor) ? o.factor : 1) });
  }
  /* Momentum / Compounder entry fraction of full size: homework cap (thesis done?) × starter (first entry only, when ON). usedFraction = already held + working. */
  function entryFraction(o) {
    o = o || {}; var cap = o.homeworkDone === true ? 1 : POLICY.hwFactor.mom;
    var first = o.starterOn === true && o.isFirstEntry === true ? POLICY.mom.starter : 1;
    var allow = Math.min(cap, first), used = num(o.usedFraction) ? o.usedFraction : 0;
    return { fraction: Math.max(0, Math.min(1, allow - used)), cap: cap, capped: o.homeworkDone !== true, firstEntry: first };
  }
  function emergencyFactor(active, cfg) { return active ? pol(cfg).emergency.factor : 1; }

  /* ═══ 8. Aggregation helpers ═══ */
  function inPeriod(ms, from, to) { return ms >= from && ms < to; }
  function ideaPeriodNet(idea, from, to) {
    var s = 0; realizedEvents(idea).forEach(function (e) { if (inPeriod(e.time, from, to)) s += e.net; }); return s;
  }
  function ideasOf(ideas, account, strategyKey) {
    return (ideas || []).filter(function (i) { return i && (account == null || i.account === account) && (!strategyKey || strat(i.strategy) === strategyKey); });
  }
  function isLive(i) { return i.status === 'ordered' || i.status === 'holding'; }
  function reservedRisk(idea) {   /* working orders reserve their real quantity; draft/planned reserve nothing */
    var dir = dirOf(idea.side), s = 0; (idea.workingOrders || []).forEach(function (w) {
      if (pos(w.entry) && pos(w.stop) && pos(w.qty)) s += w.qty * Math.abs(w.entry - w.stop) * (w.mult > 0 ? w.mult : 1) * (w.fx > 0 ? w.fx : 1);
    }); return s;
  }
  /* Realized money per strategy/account for a period. gross = Σ over ideas of max(0, −idea period net) (wins never offset) · net = Σ idea period net. */
  function realizedPeriod(ideas, from, to) {
    var gross = 0, net = 0; ideas.forEach(function (i) { var n = ideaPeriodNet(i, from, to); net += n; gross += Math.max(0, -n); }); return { gross: gross, net: net };
  }
  /* exposures: open (holding ideas) and reserved (working orders), costs resolved by caller via costsFor(idea) */
  function exposures(ideas, costsFor) {
    var open = 0, reserved = 0, unknown = [];
    ideas.forEach(function (i) {
      if (i.status === 'holding') { var r = ideaResult(i, costsFor ? costsFor(i) : null); if (r.exposure === null) unknown.push(i.id); else open += r.exposure; if (r.costUnknown) unknown.push(i.id); }
      reserved += reservedRisk(i);
    });
    return { open: open, reserved: reserved, unknown: uniq(unknown) };
  }

  /* ═══ 9. Momentum ═══
     in = {account, now, basis (snapshotBasis result), ideas (this account only), candidate:{ideaId, riskMoney, isAddition}, costsFor(idea), emergency?, cfg} */
  function momentumState(i) {
    var P = pol(i.cfg).mom, now = i.now, ws = weekStart(now), we = ws + 7 * DAY, ms = monthStart(now), me = nextMonth(ms);
    var all = ideasOf(i.ideas, i.account, 'winner'), costsFor = i.costsFor;
    var weekLosses = 0, completedLoss = 0;
    all.forEach(function (idea) {
      if (idea.status === 'closed') {
        var close = closeTimeOf(idea);
        if (close !== null && inPeriod(close, ws, we) && ideaRealizedNet(idea) < 0) completedLoss++;
      }
    });
    var live = all.filter(isLive), reservedIdeas = live.filter(function (idea) { return !(idea.status === 'holding' && ammoReleased(idea, costsFor ? costsFor(idea) : null)); });
    var wk = realizedPeriod(all, ws, we), mo = realizedPeriod(all, ms, me), ex = exposures(live, costsFor);
    return { completedLosses: completedLoss, reservedIdeas: reservedIdeas.map(function (x) { return x.id; }), ammoUsed: completedLoss + reservedIdeas.length,
      weekGross: wk.gross, monthGross: mo.gross, open: ex.open, reserved: ex.reserved, unknown: ex.unknown, P: P, ws: ws, ms: ms };
  }
  function nextMonth(ms) { var d = new Date(ms + BKK); return Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 1) - BKK; }
  function closeTimeOf(idea) { if (num(idea.closedAt)) return idea.closedAt; var t = null; (idea.exits || []).forEach(function (e) { if (t === null || e.time > t) t = e.time; }); return t; }

  function momentumCheck(i) {
    var b = i.basis; if (!b || !b.ok) return res(b ? b.reasons : ['NO_SNAPSHOT'], [], {});
    var S = momentumState(i), P = S.P, cand = i.candidate || {}, reasons = [], flags = (b.flags || []).slice();
    if (i.ddStop === true) reasons.push('DD_STOP');
    var risk = num(cand.riskMoney) && cand.riskMoney >= 0 ? cand.riskMoney : null;
    if (risk === null) reasons.push('UNKNOWN_DATA');
    var wCap = b.weekEquity * P.weeklyPct / 100, mCap = b.monthEquity * P.monthlyPct / 100;
    var wUse = S.weekGross + S.open + S.reserved + (risk || 0), mUse = S.monthGross + S.open + S.reserved + (risk || 0);
    if (!leq(wUse, wCap)) reasons.push('MONEY_WEEK');
    if (!leq(mUse, mCap)) reasons.push('MONEY_MONTH');
    var candIdeas = cand.isAddition === true || (S.reservedIdeas.indexOf(cand.ideaId) >= 0) ? 0 : 1;
    var ammoAfter = S.ammoUsed + candIdeas;
    if (ammoAfter > P.ammo) reasons.push('AMMO_EXHAUSTED');
    if (S.completedLosses > P.ammo) flags.push('AMMO_OVERSHOOT');
    if (S.unknown.length) flags.push('COST_UNKNOWN');
    return res(reasons, flags, { money: { weekUsed: wUse, weekCap: wCap, monthUsed: mUse, monthCap: mCap, weekGross: S.weekGross, open: S.open, reserved: S.reserved },
      ammo: { completedLosses: S.completedLosses, reserved: S.reservedIdeas.length, candidate: candIdeas, total: ammoAfter, max: P.ammo },
      usageWeek: S.weekGross + S.open + S.reserved, usageMonth: S.monthGross + S.open + S.reserved });
  }

  /* ═══ 10. Satellite ═══ */
  function satCondition(c) {
    c = c || {}; var R = POLICY.sat.condReduced;
    if (typeof c.ema50 !== 'boolean' || typeof c.structure !== 'boolean') return { status: 'incomplete', factor: null, allowed: false, reasons: ['SAT_COND_INCOMPLETE'], flags: [], label: 'Incomplete' };
    var mss = c.mss === 'yes' || c.mss === true ? 'yes' : (c.mss === 'no' || c.mss === false ? 'no' : null);
    if (c.structure) {
      if (c.ema50) return { status: 'full', factor: 1, allowed: true, reasons: [], flags: [], label: 'Full', isFull: true };
      return { status: 'reduced', factor: R, allowed: true, reasons: [], flags: ['SAT_NEAREST_TARGET'], label: 'Reduced', isFull: false };
    }
    if (mss === 'yes') return c.ema50 ? { status: 'counter', factor: R, allowed: true, reasons: [], flags: [], label: 'Counter trend @ MSS', isFull: false, tag: 'counter-trend' }
      : { status: 'reversal', factor: R, allowed: true, reasons: [], flags: ['SAT_NEAREST_TARGET'], label: 'Reversal @ MSS', isFull: false, tag: 'reversal' };
    return { status: 'blocked', factor: null, allowed: false, reasons: ['SAT_COND_BLOCKED'], flags: [], label: 'Blocked' };
  }
  function satEntryOrder(o) {   /* Entry/SL/TP order + R:R >= 1.5, TP mandatory */
    o = o || {}; var d = dirOf(o.side);
    if (!(pos(o.entry) && pos(o.stop))) return { allowed: false, reasons: ['PRICE_MISSING'], flags: [] };
    if (!pos(o.tp)) return { allowed: false, reasons: ['SAT_RR'], flags: [] };
    var ok = d === 1 ? (o.stop < o.entry && o.entry < o.tp) : (o.stop > o.entry && o.entry > o.tp);
    if (!ok) return { allowed: false, reasons: ['SAT_BAD_ORDER'], flags: [] };
    var rr = Math.abs(o.tp - o.entry) / Math.abs(o.entry - o.stop);
    return rr + EPS >= POLICY.sat.minRR ? { allowed: true, reasons: [], flags: [], rr: rr } : { allowed: false, reasons: ['SAT_RR'], flags: [], rr: rr };
  }
  /* Step machine. attempts = [{id, closeAt, net}] completed attempts (a stopped-out attempt and its re-entry are two results).
     Only results of the CURRENT week (Bangkok, by close time) count; weekly reset → Step 1 and unlock. Order: closeAt then id (deterministic). */
  function satStepState(attempts, now, cfg) {
    var P = pol(cfg).sat, ws = weekStart(now), we = ws + 7 * DAY, idx = 0, locked = false, net = 0, seen = {}, trace = [];
    (attempts || []).filter(function (a) { return a && num(a.net) && num(a.closeAt) && inPeriod(a.closeAt, ws, we); })
      .sort(function (a, b) { return a.closeAt - b.closeAt || (String(a.id) < String(b.id) ? -1 : String(a.id) > String(b.id) ? 1 : 0); })
      .forEach(function (a) {
        if (a.id != null) { if (seen[a.id]) return; seen[a.id] = 1; }   /* event ids prevent double counting */
        if (locked) { net += a.net; return; }                           /* results while locked (e.g. an older order finishing) still count in net, step stays */
        net += a.net; var o = outcome(a.net);
        if (o === 'loss') { if (idx >= P.stepRpt.length - 1) locked = true; else idx++; }
        else if (o === 'win' && net >= 0) idx = 0;                      /* win and weekly net >= 0 → Step 1 · win and net < 0 → stay */
        trace.push({ id: a.id, outcome: o, stepIndex: idx, locked: locked, weeklyNet: net });
      });
    return { stepIndex: idx, step: idx + 1, locked: locked, weeklyNet: net, baseRptPct: P.stepRpt[idx], trace: trace, weekStart: ws, resetAt: we };
  }
  function satEffectiveRpt(step, condFactor, emergencyF, cfg) {
    var P = pol(cfg).sat; if (!(num(condFactor) && condFactor > 0)) return null;
    return P.stepRpt[step.stepIndex] * condFactor * (num(emergencyF) ? emergencyF : 1);   /* Condition applied once */
  }
  /* HF5 — risk cut of ONE live Sat setup: 1 − (risk at the current stop ÷ risk at the initial stop), 0..1. A working (unfilled) order = full risk = 0.
     Risk = Σ live tranches max(0, (entry − stop) × dir × qty × mult × fx). Initial stop unknown → 0 (never assume a cut). stopOverride = what-if current stop (Move stop preview). */
  function satRiskNow(idea, stopOverride) {
    var dir = dirOf(idea.side), ini = 0, cur = 0, unknown = false, live = idea.status === 'holding' ? liveTranches(idea) : [];
    if (!live.length) return { initial: 0, current: 0, cut: 0, full: true };
    live.forEach(function (x) {
      var t = x.t, uv = trancheUV(t), st = num(stopOverride) && stopOverride > 0 ? stopOverride : t.stop, is = pos(t.initialStop) ? t.initialStop : null;
      if (!pos(st)) { unknown = true; return; }
      cur += Math.max(0, (t.entry - st) * dir * x.q * uv);
      if (is === null) unknown = true; else ini += Math.max(0, (t.entry - is) * dir * x.q * uv);
    });
    var cut = unknown ? 0 : (ini > EPS ? Math.min(1, Math.max(0, 1 - cur / ini)) : (cur <= EPS ? 1 : 0));
    return { initial: ini, current: cur, cut: cut, full: false };
  }
  function satRiskCutPct(idea) { return satRiskNow(idea).cut; }
  /* queue (HF5, replaces "one active setup"): a new Sat setup needs (1) fewer than POLICY.sat.maxActive live Sat setups (working orders + holdings) in the account AND
     (2) every live setup's risk cut >= POLICY.sat.newSetupRiskCut. detail: open = [{id, cut}] of every live setup · blockers = those under the cut. */
  function satQueueCheck(ideas, account, candidateId, cfg) {
    var P = pol(cfg).sat, live = ideasOf(ideas, account, 'sat').filter(function (i) { return isLive(i) && i.id !== candidateId; });
    var open = live.map(function (i) { return { id: i.id, cut: satRiskCutPct(i), working: i.status !== 'holding' }; });
    if (live.length >= P.maxActive) return res(['SAT_QUEUE_MAX'], [], { busyWith: live.map(function (x) { return x.id; }), open: open, max: P.maxActive });
    var blockers = open.filter(function (o) { return o.cut + EPS < P.newSetupRiskCut; });
    return blockers.length ? res(['SAT_QUEUE_BUSY'], [], { busyWith: blockers.map(function (x) { return x.id; }), open: open, blockers: blockers, need: P.newSetupRiskCut }) : res([], [], { open: open });
  }
  function satStaleOrders(ideas, now, cfg) {   /* Today reminder only — never an auto-cancel */
    var lim = pol(cfg).sat.staleOrderMs, out = [];
    (ideas || []).forEach(function (i) { if (strat(i.strategy) === 'sat' && i.status === 'ordered') (i.workingOrders || []).forEach(function (w) { if (num(w.at) && now - w.at > lim) out.push({ ideaId: i.id, orderId: w.id }); }); });
    return out;
  }
  /* Daily: one setup per product per Bangkok day + ONE re-entry after a whipsaw stop-out while the setup is still valid.
     o = {now, product, attempts:[{id, product, startAt, status:'working|open|closed|cancelled', net, exitReason:'stop'|'target'|'manual'|..., reentry:bool}],
          reentry:{ confirmed, setupValid, sameDirectionZone, trendUnchanged, candleClosedSince } (one-tap confirm at Place order)} */
  function satDailyCheck(o) {
    var ds = dayStart(o.now), de = ds + DAY;
    var today = (o.attempts || []).filter(function (a) { return a.product === o.product && a.status !== 'cancelled' && inPeriod(a.startAt, ds, de); });
    if (!today.length) return res([], [], { reentry: false });
    var used = today.filter(function (a) { return a.reentry === true; }).length;
    if (today.length >= 2 || used > 0) return res(['SAT_REENTRY_USED'], [], {});
    var first = today[0];
    if (!(first.status === 'closed' && first.exitReason === 'stop' && outcome(first.net) === 'loss')) return res(['SAT_DAILY_LIMIT'], [], {});
    var r = o.reentry || {};
    var ok = r.confirmed === true && r.setupValid === true && r.sameDirectionZone === true && r.trendUnchanged === true && r.candleClosedSince === true;
    if (!ok) return res(['SAT_REENTRY_COND'], [], { reentry: true });
    return res([], ['SAT_REENTRY_TAG'], { reentry: true, originalAttemptId: first.id });
  }
  /* Budget: max(0, −weekly net realized) + open + reserved + candidate <= 1.20 % of week-start equity (monthly 4.80 % of month-start equity) */
  function satBudgetCheck(i) {
    var b = i.basis; if (!b || !b.ok) return res(b ? b.reasons : ['NO_SNAPSHOT'], [], {});
    var P = pol(i.cfg).sat, ws = weekStart(i.now), we = ws + 7 * DAY, ms = monthStart(i.now), me = nextMonth(ms), all = ideasOf(i.ideas, i.account, 'sat');
    var wk = realizedPeriod(all, ws, we), mo = realizedPeriod(all, ms, me), ex = exposures(all.filter(isLive), i.costsFor);
    var risk = num(i.candidateRisk) && i.candidateRisk >= 0 ? i.candidateRisk : null, reasons = [], flags = (b.flags || []).slice();
    if (risk === null) reasons.push('UNKNOWN_DATA');
    var wUse = Math.max(0, -wk.net) + ex.open + ex.reserved + (risk || 0), mUse = Math.max(0, -mo.net) + ex.open + ex.reserved + (risk || 0);
    var wCap = b.weekEquity * P.weeklyPct / 100, mCap = b.monthEquity * P.monthlyPct / 100;
    if (!leq(wUse, wCap)) reasons.push('MONEY_WEEK'); if (!leq(mUse, mCap)) reasons.push('MONEY_MONTH');
    if (ex.unknown.length) flags.push('COST_UNKNOWN');
    return res(reasons, flags, { weekUsed: wUse, weekCap: wCap, monthUsed: mUse, monthCap: mCap, weeklyNet: wk.net, monthlyNet: mo.net,
      usageWeek: Math.max(0, -wk.net) + ex.open + ex.reserved, usageMonth: Math.max(0, -mo.net) + ex.open + ex.reserved });
  }
  /* Full Satellite gate for a NEW order (not a fill). */
  function satCheck(i) {
    var reasons = [], flags = [], st = satStepState(i.attempts, i.now, i.cfg);
    if (i.ddStop === true) reasons.push('DD_STOP');
    if (st.locked) reasons.push('SAT_LOCKED');
    var cond = satCondition(i.condition); reasons = reasons.concat(cond.reasons); flags = flags.concat(cond.flags);
    var ord = satEntryOrder(i.order); reasons = reasons.concat(ord.reasons);
    var q = satQueueCheck(i.ideas, i.account, i.candidateId); reasons = reasons.concat(q.reasons);
    var d = satDailyCheck({ now: i.now, product: i.product, attempts: i.dayAttempts, reentry: i.reentry }); reasons = reasons.concat(d.reasons); flags = flags.concat(d.flags);
    var rpt = satEffectiveRpt(st, cond.factor, i.emergencyFactor, i.cfg);
    var bud = satBudgetCheck({ basis: i.basis, now: i.now, account: i.account, ideas: i.ideas, costsFor: i.costsFor, candidateRisk: i.candidateRisk, cfg: i.cfg });
    reasons = reasons.concat(bud.reasons); flags = flags.concat(bud.flags);
    return res(reasons, flags, { step: st, condition: cond, effectiveRptPct: rpt, budget: bud, usageWeek: bud.usageWeek, usageMonth: bud.usageMonth });
  }

  /* ═══ 11. Compounder ═══ */
  /* RM1 — ONE shared regime result (sizing + every view).
     signals: {acwi, hyg, asOf}  acwi / hyg = 'green' | 'red' | 'neutral' | 'unavailable' (legacy true / false / null still accepted: true = green, false = red, null = unavailable)
     asOf = the OLDEST of the four input dates (fundflow.json inputs_asof — never the file's own as_of / run date). Fresh = age (today Asia/Bangkok - asOf) in 0..4 calendar days.
     Modifier: both signals known -> table[equity][credit]; either neutral / unavailable, or no usable date -> fallback 75 %. Stale (age > 4) -> min(table value, fallback 75 %). Missing data never gives 100 %. */
  function asOfMs(v) { if (num(v)) return v; if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}/.test(v)) return Date.parse(v.slice(0, 10) + 'T00:00:00+07:00'); return null; }
  function calDaysBetween(aMs, bMs) { return Math.round((dayStart(bMs) - dayStart(aMs)) / DAY); }
  function sigState(v) { return v === true ? 'green' : v === false ? 'red' : (v === 'green' || v === 'red' || v === 'neutral') ? v : 'unavailable'; }
  function regimeModifier(eq, cr, cfg) {
    var T = pol(cfg).regime, e = sigState(eq), c = sigState(cr);
    return (e === 'green' || e === 'red') && (c === 'green' || c === 'red') ? T.table[e][c] : null;
  }
  function regimeState(sig, now, cfg) {
    var T = pol(cfg).regime, s = sig || {}, eq = sigState(s.acwi), cr = sigState(s.hyg);
    var known = (eq === 'green' || eq === 'red') && (cr === 'green' || cr === 'red');
    var a = asOfMs(s.asOf), age = a === null ? null : calDaysBetween(a, now);
    var dateFresh = age !== null && age >= 0 && age <= T.freshDays, fresh = dateFresh && known;   /* fresh = recent date AND both signals usable */
    var base = known ? T.table[eq][cr] : T.fallback;
    var factor = (known && dateFresh) ? base : Math.min(base, T.fallback);
    var reds = (eq === 'red' ? 1 : 0) + (cr === 'red' ? 1 : 0), missing = (known ? 0 : (eq === 'green' || eq === 'red' ? 0 : 1) + (cr === 'green' || cr === 'red' ? 0 : 1));
    var fallback = !known || !dateFresh;
    var cT = COMP_REGIME_FACTOR, cBase = known ? (reds === 0 ? cT.green : reds === 1 ? cT.oneRed : cT.bothRed) : cT.fallback;
    var compF = (known && dateFresh) ? cBase : Math.min(cBase, cT.fallback);   /* CP1 — Compounder's own modifier (Momentum keeps `factor`) */
    return { reasons: [], factor: factor, compFactor: compF, modifier: factor, base: base, equity: eq, credit: cr, reds: reds, missing: missing, known: known, fresh: !!fresh, ageDays: age, asOf: typeof s.asOf === 'string' ? s.asOf.slice(0, 10) : null,
      bothGreen: eq === 'green' && cr === 'green', dateFresh: dateFresh, stale: !fresh, fallback: fallback, flags: fallback ? ['COMP_REGIME_STALE'] : [] };
  }
  /* The one reader of fundflow.json: ratios.ACWI_BIL / HYG_IEI {state, inputs_asof:{..}} -> signals -> regimeState. demo / missing file -> both unavailable. */
  function oldestInput(r) {
    var m = null; if (!r || !r.inputs_asof) return null;
    Object.keys(r.inputs_asof).forEach(function (k) { var v = r.inputs_asof[k]; if (typeof v === 'string' && /^\d{4}-\d{2}-\d{2}/.test(v) && (m === null || v < m)) m = v.slice(0, 10); });
    return m;
  }
  function fundflowSignals(ff, cfg) {
    var rat = (ff && !ff.demo && ff.ratios) || {}, A = rat.ACWI_BIL, H = rat.HYG_IEI, dates = [];
    var P = pol(cfg).regime, st = function (r) {
      if (!r || !(r.state === 'green' || r.state === 'red' || r.state === 'neutral')) return 'unavailable';
      if (r.adj !== true || !r.sma || r.sma[0] !== P.smaFast || r.sma[1] !== P.smaSlow) return 'unavailable';   /* file built with other periods / unadjusted data -> never trusted */
      return r.state;
    };
    [A, H].forEach(function (r) { if (r && r.inputs_asof) { var o = oldestInput(r); if (o) dates.push(o); else dates.push(null); } else dates.push(null); });
    var asOf = dates.indexOf(null) >= 0 ? null : (dates[0] < dates[1] ? dates[0] : dates[1]);
    return { acwi: st(A), hyg: st(H), asOf: asOf, acwiDays: A && A.days_in_state != null ? A.days_in_state : null, hygDays: H && H.days_in_state != null ? H.days_in_state : null,
      acwiSma: A && A.sma20 != null ? [A.sma20, A.sma50] : null, hygSma: H && H.sma20 != null ? [H.sma20, H.sma50] : null, demo: !!(ff && ff.demo) || !ff };
  }
  function regimeFromFundflow(ff, now, cfg) {
    var sg = fundflowSignals(ff, cfg), r = regimeState(sg, now, cfg);
    r.signals = sg; r.acwiDays = sg.acwiDays; r.hygDays = sg.hygDays; r.acwiSma = sg.acwiSma; r.hygSma = sg.hygSma; r.demo = sg.demo;
    return r;
  }
  /* one display line for every view: "75% of normal · equity red, credit green" */
  function smaLabel(cfg) { var T = pol(cfg).regime; return 'SMA ' + T.smaFast + '/' + T.smaSlow; }
  function regimeText(r) {
    var pc = Math.round(r.factor * 100);
    if (r.fallback) return { head: 'Modifier unavailable · fallback cap ' + pc + '%', short: pc + '% fallback', reason: !r.known ? 'a signal is missing' : 'data is stale' };
    return { head: pc + '% of normal', short: pc + '%', reason: 'equity ' + r.equity + ', credit ' + r.credit };
  }
  function compFactor(regime, emergencyF) { return Math.min(num(regime.compFactor) ? regime.compFactor : regime.factor, num(emergencyF) ? emergencyF : 1); }   /* CP1 — Compounder: min(Compounder regime modifier, Emergency), never multiplied */
  function momFactor(regime, emergencyF) { return Math.min(regime.factor, num(emergencyF) ? emergencyF : 1); }   /* Momentum (RM1): min(Regime 100/80/60, Emergency) — unchanged by CP1 */
  /* CP1 — market state. m = {spy: offHi, set: offHi} (fractions, −0.09 = 9 % below the 52-week high; null / missing = unknown) · reds = how many regime signals are red (0..2).
     Pullback = the stock's index >= MARKET_PULLBACK_PCT below its high, OR exactly one regime signal red. US stocks use SPY, Thai stocks use SET. */
  function pullback(m, reds) { /* CP1 */
    var pct = function (v) { return num(v) ? Math.round(-v * 10000) / 100 : null; }; /* CP1 */
    var spy = pct(m && m.spy), set = pct(m && m.set), one = reds === 1, thr = MARKET_PULLBACK_PCT; /* CP1 */
    var us = (spy !== null && spy >= thr) || one, th = (set !== null && set >= thr) || one; /* CP1 */
    return { on: us || th, US: us, TH: th, spyPct: spy, setPct: set, oneRed: one, reds: reds, threshold: thr }; /* CP1 */
  } /* CP1 */

  /* heat = current open principal risk of live Compounder ideas (same idea-level calculation), cap 6 % */
  function compHeat(ideas, account, costsFor, equity, currentEquity) {
    var live = ideasOf(ideas, account, 'ladder').filter(function (i) { return i.status === 'holding'; }), money = 0, unknown = [];
    live.forEach(function (i) { var r = ideaResult(i, costsFor ? costsFor(i) : null); if (r.exposure === null) unknown.push(i.id); else money += r.exposure; });
    return { money: money, pct: pos(equity) ? money / equity * 100 : null, pctCurrent: pos(currentEquity) ? money / currentEquity * 100 : null, unknown: unknown, count: live.length };
  }
  /* Lock: six consecutive losing ticker-cycles (first fill → flat). A win resets; exact breakeven neither counts nor resets.
     cycles = [{id, flatAt, net}] · unlocks = [{at}] (a recorded unlock resets the streak to 0 from that time) */
  function compStreak(cycles, unlocks, cfg) {
    var P = pol(cfg).comp, lastUnlock = -Infinity, seen = {};
    (unlocks || []).forEach(function (u) { if (u && num(u.at) && u.at > lastUnlock) lastUnlock = u.at; });
    var streak = 0, sixthAt = null;
    (cycles || []).filter(function (c) { return c && num(c.net) && num(c.flatAt) && c.flatAt > lastUnlock; })
      .sort(function (a, b) { return a.flatAt - b.flatAt || (String(a.id) < String(b.id) ? -1 : 1); })
      .forEach(function (c) {
        if (c.id != null) { if (seen[c.id]) return; seen[c.id] = 1; }
        var o = outcome(c.net);
        if (o === 'loss') { streak++; if (streak === P.lockLosses && sixthAt === null) sixthAt = c.flatAt; } else if (o === 'win') { streak = 0; sixthAt = null; }
      });
    return { streak: streak, locked: streak >= P.lockLosses, sixthLossAt: streak >= P.lockLosses ? sixthAt : null };
  }
  function compUnlockCheck(o) {
    var P = pol(o.cfg).comp, st = o.streakState, reasons = [];
    if (!st || !st.locked) return res([], [], { unlocked: false, nothingToUnlock: true });
    if (!(num(st.sixthLossAt) && o.now - st.sixthLossAt >= P.unlockDays * DAY - EPS)) reasons.push('COMP_UNLOCK_WAIT');
    var rg = o.regime || {};
    if (!rg.fresh) reasons.push('COMP_UNLOCK_STALE');
    if (!rg.bothGreen) reasons.push('COMP_UNLOCK_SIGNALS');
    if (!str(o.note)) reasons.push('COMP_UNLOCK_NOTE');
    if (o.confirm !== true) reasons.push('COMP_UNLOCK_CONFIRM');
    return res(reasons, [], { unlocked: reasons.length === 0, streakAfter: reasons.length ? st.streak : 0 });
  }
  /* kind: 'pilot' | 'topup' | 'addon' · o = {kind, starterOn, thesisDone, side, entryPx?, avgEntry?, factor? (= min(Regime, Emergency)), requestedPct (new order, % of week-start equity), usedPct (the ticker's existing tranches at their CURRENT stop + working orders, same basis)}
     Pilot: first 0.50 % (Starter ON: 0.25 %). Add-on / further buys (answers-A #16 · owner amendment): TOTAL-RISK rule only —
       thesis done AND used + new <= total (Settings, default 1.00 %) x factor (0.50 % without thesis; a Starter top-up may use that 0.50 % without thesis) AND new order alone <= 0.50 % x factor.
       Entry may be above OR below the average entry; below only raises the warning ADDON_BELOW_ENTRY_WARN (never a block). No +1.5R, no breakeven-stop condition. */
  function compEntryCheck(o) {
    var P = pol(o.cfg).comp, reasons = [], flags = [], used = num(o.usedPct) ? o.usedPct : 0, req = num(o.requestedPct) ? o.requestedPct : 0, cap;
    if (o.legacy === true && o.kind !== 'addon') o = merge(o, { kind: 'addon' });   /* legacy-shape card: any NEW buy follows the Add-on rule; usedPct = ticker's total principal risk (RE1-answers-A #4) */
    if (o.kind === 'pilot') {
      cap = o.starterOn === true ? P.pilotPct * P.starter * 2 : P.pilotPct;      /* starter = 0.25 of the WHOLE plan (1 %) = half of Pilot */
      if (used + req > cap + EPS) reasons.push('COMP_PHASE_CAP');
    } else if (o.kind === 'plan') {
      /* PC2 §1 — a row that was in the plan BEFORE the first fill is part of the first build: no thesis needed; total (plan %) x homework factor (Compounder 100 %) x regime. */
      var fzp = num(o.factor) ? o.factor : 1, pp = pos(o.planPct) ? o.planPct : P.totalCapPct;
      cap = pp * POLICY.hwFactor.comp * fzp * (o.starterOn === true ? P.starter : 1);
      if (used + req > cap + EPS) reasons.push('PLAN_TOTAL_RISK');
    } else if (o.kind === 'topup' || o.kind === 'addon') {
      if (o.kind === 'addon' && o.thesisDone !== true) reasons.push('ADDON_THESIS');
      var fz = num(o.factor) ? o.factor : 1, pa = pos(o.planPct) ? o.planPct : P.totalCapPct;
      cap = o.thesisDone === true ? pa * fz : P.pilotPct;   /* RM1: total-risk cap (plan %, default Settings 1.00 %) x effective modifier with thesis · 0.50 % without */
      var alone = o.noAlone === true ? Infinity : P.addonPct * fz;   /* PC2 2e: the add-on rule is the TOTAL-risk rule only (plan budget) */
      if (used + req > cap + EPS || req > alone + EPS) reasons.push('ADDON_TOTAL_RISK');
      if (pos(o.entryPx) && pos(o.avgEntry) && (dirOf(o.side) === 1 ? o.entryPx < o.avgEntry - EPS : o.entryPx > o.avgEntry + EPS)) flags.push('ADDON_BELOW_ENTRY_WARN');
    } else return res(['UNKNOWN_DATA'], [], {});
    return res(reasons, flags, { capPct: cap, roomPct: Math.max(0, cap - used) });
  }
  /* legacy shape (answers-A #4): more than two tranches, or accelerator lots. Never resized / re-split; existing lots count to heat at actual remaining risk. */
  function compLegacyShape(o) {
    o = o || {}; var n = num(o.tranches) ? o.tranches : 0, acc = num(o.accelLots) ? o.accelLots : 0, why = [];
    if (n > 2) why.push('TRANCHES_GT_2'); if (acc > 0) why.push('ACCELERATOR_LOTS');
    return { legacy: why.length > 0, why: why };
  }
  function compCheck(i) {
    var reasons = [], flags = [], b = i.basis;
    if (!b || !b.ok) return res(b ? b.reasons : ['NO_SNAPSHOT'], [], {});
    flags = flags.concat(b.flags || []);
    var ck = compStreak(i.cycles, i.unlocks, i.cfg); if (ck.locked) reasons.push('COMP_LOCKED');
    if (i.ddStop === true) reasons.push('DD_STOP');
    var rg = i.regime || regimeState(i.signals, i.now, i.cfg), f = compFactor(rg, i.emergencyFactor); flags = flags.concat(rg.flags);
    var e = compEntryCheck(merge(i.entry || {}, { factor: f })); reasons = reasons.concat(e.reasons); flags = flags.concat(e.flags);
    var heat = compHeat(i.ideas, i.account, i.costsFor, b.weekEquity, b.currentEquity), cand = num(i.candidateRisk) ? i.candidateRisk : 0, P = pol(i.cfg).comp;
    if (heat.unknown.length) flags.push('COST_UNKNOWN');
    if (!leq(heat.money + cand, b.weekEquity * P.heatCapPct / 100)) reasons.push('COMP_HEAT');
    return res(reasons, flags, { lock: ck, regime: rg, factor: f, heat: heat, entry: e, riskPctOfEquity: heat.pct });
  }

  /* ═══ 12. Active summary (Momentum + Satellite): Σ of each strategy's projected usage, each floored at 0 separately ═══ */
  function activeSummary(i) {
    var P = pol(i.cfg).active, b = i.basis; if (!b || !b.ok) return res(b ? b.reasons : ['NO_SNAPSHOT'], [], {});
    var wk = Math.max(0, i.mom.usageWeek || 0) + Math.max(0, i.sat.usageWeek || 0), mo = Math.max(0, i.mom.usageMonth || 0) + Math.max(0, i.sat.usageMonth || 0);
    var cand = num(i.candidateRisk) ? i.candidateRisk : 0, r = [];
    if (!leq(wk + cand, b.weekEquity * P.weeklyPct / 100)) r.push('ACTIVE_WEEK');
    if (!leq(mo + cand, b.monthEquity * P.monthlyPct / 100)) r.push('ACTIVE_MONTH');
    return res(r, [], { weekUsed: wk + cand, monthUsed: mo + cand, weekCap: b.weekEquity * P.weeklyPct / 100, monthCap: b.monthEquity * P.monthlyPct / 100 });
  }

  /* ═══ 13. Action policy: reductions / exits / stop updates are always allowed; an actual fill is always accepted (breach flagged);
         only NEW proposed risk-increasing orders are blocked. ═══ */
  var RISK_INCREASING = { order: 1, addon: 1, topup: 1, edit_increase: 1 };
  function actionPolicy(action, checkResult) {
    var r = checkResult || { reasons: [], flags: [] };
    if (action === 'fill') return asFill(r);
    if (RISK_INCREASING[action]) return { accepted: r.reasons.length === 0, reasons: r.reasons.slice(), flags: r.flags.slice() };
    return { accepted: true, reasons: [], flags: r.flags.slice() };   /* cancel, reduce, close, stop_update, snapshot, cost_edit … */
  }
  function asFill(r) {
    var breach = r.reasons && r.reasons.length; return { accepted: true, reasons: [], flags: uniq((r.flags || []).concat(breach ? ['FILL_OVER_LIMIT'] : [])), breached: breach ? r.reasons.slice() : [] };
  }

  /* ═══ 14. Event log fold (append-only log → ideas). Event ids make replay idempotent; order = (at, id). Backdated events simply change the derived state
         (current state recomputed; past orders are never retro-blocked — checks only run on new orders). ═══
     event = {id, type, at, account, ideaId, ...}. Types: order · cancel · fill · partial_close · close · stop_confirm. (snapshot/cost_edit/cashflow/lock/unlock/emergency
     are consumed by the dedicated functions above.) */
  function foldEvents(events) {
    var seen = {}, ideas = {}, list = [];
    (events || []).filter(function (e) { return e && e.id != null && num(e.at); }).sort(function (a, b) { return a.at - b.at || (String(a.id) < String(b.id) ? -1 : String(a.id) > String(b.id) ? 1 : 0); })
      .forEach(function (e) {
        if (seen[e.id]) return; seen[e.id] = 1;
        var I = e.ideaId != null ? ideas[e.ideaId] : null;
        if (e.type === 'order') {
          if (!I) { I = ideas[e.ideaId] = { id: e.ideaId, account: e.account, strategy: e.strategy, product: e.product, side: e.side, status: 'ordered', tranches: [], exits: [], workingOrders: [], entryFees: 0, orderedAt: e.at, reentry: !!e.reentry, attemptId: e.attemptId }; list.push(I); }
          I.workingOrders.push({ id: e.orderId || e.id, qty: e.qty, entry: e.entry, stop: e.stop, mult: e.mult, fx: e.fx, at: e.at });
          if (I.status !== 'holding') I.status = 'ordered';
        } else if (I) {
          if (e.type === 'cancel') {
            var rem = e.orderId ? I.workingOrders.filter(function (w) { return w.id !== e.orderId; }) : [];
            I.workingOrders = rem; if (!I.tranches.length && !rem.length) { I.status = 'cancelled'; I.cancelledAt = e.at; }
          } else if (e.type === 'fill') {
            var ft = I.tranches.filter(function (t) { return t.id === e.trancheId; })[0];
            if (!ft) { ft = { id: e.trancheId || e.id, entry: e.price, qty: 0, stop: e.stop, initialStop: e.stop, mult: e.mult, fx: e.fx, stopConfirmed: false, filledAt: e.at }; I.tranches.push(ft); }
            var nq = ft.qty + e.qty; ft.entry = (ft.entry * ft.qty + e.price * e.qty) / nq; ft.qty = nq; if (pos(e.stop)) ft.stop = e.stop;
            I.entryFees += e.fees || 0;
            I.workingOrders = I.workingOrders.filter(function (w) { return !(e.orderId && w.id === e.orderId); }); I.status = 'holding';
          } else if (e.type === 'partial_close' || e.type === 'close') {
            I.exits.push({ id: e.id, time: e.at, qty: e.qty, price: e.price, fees: e.fees || 0, swap: e.swap || 0, trancheId: e.trancheId, reason: e.reason });
            var left = 0; I.tranches.forEach(function (t) { left += remainingQtyOf(I, t); });
            if (e.type === 'close' || left <= 1e-12) { I.status = 'closed'; I.closedAt = e.at; I.exitReason = e.reason; I.workingOrders = []; }
          } else if (e.type === 'stop_confirm') {
            I.tranches.forEach(function (t) { if (e.trancheId == null || t.id === e.trancheId) { t.stop = e.stop; t.stopConfirmed = e.confirmed !== false; } });
          }
        }
      });
    return list;
  }

  return {
    POLICY: POLICY, RISK_DEFAULTS: RISK_DEFAULTS, RISK_BOUNDS: RISK_BOUNDS, riskValidate: riskValidate, applyRisk: applyRisk, riskDerived: riskDerived, REASONS: REASONS, EPS: EPS,
    bkk: bkk, outcome: outcome,
    resolveCosts: resolveCosts, exitCost: exitCost,
    ideaResult: ideaResult, ideaRealizedNet: ideaRealizedNet, realizedEvents: realizedEvents, netBreakevenStop: netBreakevenStop, ammoReleased: ammoReleased, rMultiple: rMultiple,
    snapshotBasis: snapshotBasis, emergencyStep: emergencyStep, ddStopStep: ddStopStep, emergencyFactor: emergencyFactor,
    sizeOrder: sizeOrder, entryFraction: entryFraction, floorLot: floorLot,
    realizedPeriod: realizedPeriod, exposures: exposures,
    momentumState: momentumState, momentumCheck: momentumCheck,
    satCondition: satCondition, satEntryOrder: satEntryOrder, satStepState: satStepState, satEffectiveRpt: satEffectiveRpt, satQueueCheck: satQueueCheck, satRiskCutPct: satRiskCutPct, satRiskNow: satRiskNow,
    satStaleOrders: satStaleOrders, satDailyCheck: satDailyCheck, satBudgetCheck: satBudgetCheck, satCheck: satCheck,
    regimeState: regimeState, regimeModifier: regimeModifier, regimeFromFundflow: regimeFromFundflow, regimeText: regimeText, smaLabel: smaLabel, fundflowSignals: fundflowSignals, asOfMs: asOfMs, compLegacyShape: compLegacyShape, sizeAttempt: sizeAttempt, compFactor: compFactor, momFactor: momFactor, pullback: pullback, MARKET_PULLBACK_PCT: MARKET_PULLBACK_PCT, COMP_REGIME_FACTOR: COMP_REGIME_FACTOR, compHeat: compHeat, compStreak: compStreak, compUnlockCheck: compUnlockCheck, compEntryCheck: compEntryCheck, compCheck: compCheck,
    activeSummary: activeSummary, actionPolicy: actionPolicy, asFill: asFill, foldEvents: foldEvents
  };
});
