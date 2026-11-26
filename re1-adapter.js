/* re1-adapter.js — RE-B read-only adapter: dashboard data → risk-engine inputs → dry-run report.
   Pure (no DOM / clock / storage / network): the caller passes a plain `src` object and the time. It never writes anything and never mutates `src`.
   Used two ways: Node (module.exports, needs ./risk-engine.js) · browser (globalThis.Re1Adapter, needs globalThis.RiskEngine).
   Missing data is Unknown (null + an entry in report.missing) — never 0.
   src = { now (ms), accounts:[{id,name,ports}], books:{id:{settings, trades}}, cards:[coreCards docs], ideas:[satIdeas docs],
           ff:{as_of, ratios:{ACWI_BIL:{up,slow:{up}}, HYG_IEI:{up,slow:{up}}}, demo?}, specs:{SYM: {contract,lotStep,minLot,cur,sys}|null},
           portCur:{core:'THB', satB:'USD'}, homework:{SYM:true|false}, starterOn:bool } */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory(require('./risk-engine.js'));
  else root.Re1Adapter = factory(root.RiskEngine);
})(typeof self !== 'undefined' ? self : this, function (R) {
  'use strict';

  var DAY = 86400000;
  function num(x) { return typeof x === 'number' && isFinite(x); }
  function pos(x) { return num(x) && x > 0; }
  function n(x) { var v = typeof x === 'string' ? parseFloat(x.replace(/,/g, '')) : x; return num(v) ? v : null; }
  function isoMs(s) { var t = typeof s === 'string' ? Date.parse(s) : NaN; return isFinite(t) ? t : null; }
  function symKey(s) { return String(s == null ? '' : s).replace(/\s+/g, '').toUpperCase(); }
  function clone(o) { return JSON.parse(JSON.stringify(o === undefined ? null : o)); }
  function sumBy(a, f) { var s = 0; a.forEach(function (x) { s += f(x); }); return s; }

  /* ── missing-field collector ── */
  function Missing() { this.m = {}; }
  Missing.prototype.add = function (code, id, note) { var e = this.m[code] || (this.m[code] = { code: code, count: 0, ids: [], note: note || '' }); e.count++; if (e.ids.length < 25 && id != null && e.ids.indexOf(id) < 0) e.ids.push(id); };
  Missing.prototype.list = function () { var m = this.m; return Object.keys(m).sort().map(function (k) { return m[k]; }); };

  var MISSING_NOTES = {
    COSTS: 'No cost settings (fees / swap) exist in the app yet — projected nets are Unknown and no Option-C release can be granted',
    INITIAL_STOP: 'No sl0 / stop history — initial stop (for R and sizing) unknown; current stop shown instead',
    CONFIRMED_STOP: 'The app does not record "stop confirmed" — treated as not confirmed (reservation kept)',
    CLOSE_TIME: 'Closed trade has no close time and no exit date — excluded from week/month attribution',
    CLOSE_TIME_DATE_ONLY: 'Closed trade has an exit date only — attributed to 12:00 Asia/Bangkok of that date',
    EXCHANGE: 'Trade has no card / exchange field — exchange inferred from the .BK suffix only',
    LOT_SPEC: 'No product / lot spec resolved for the symbol — engine size is Unknown',
    FX: 'USD position but no FX rate in the account settings — excluded from engine sums',
    STRATEGY: 'Core-port trade without a card — strategy assumed Momentum (winner)',
    PORT: 'Trade on a port the risk engine does not cover (e.g. satA / option)',
    EQUITY_SNAPSHOT: 'No confirmed equity snapshot — entered-capital PROXY used for the dry run',
    EXIT_REASON: 'Exit reason (stop / target / manual) is not recorded — whipsaw re-entry cannot be derived from history',
    ORDER_TIME: 'Working order has no placed-at time — 1-day stale-order reminder cannot be derived',
    ORDER_QTY: 'Working order has no quantity — reservation Unknown',
    CARD_NO_TRADE: 'Open card has no matching open trade row'
  };

  /* ── idea building ── */
  function coreTrack(c) { return (c && (c.strategy === 'L' || c.track === 'ladder')) ? 'ladder' : 'winner'; }
  function marketOf(sym, card) { return card && (card.market === 'TH' || card.market === 'US') ? card.market : (/\.BK$/i.test(String(sym || '')) ? 'TH' : null); }
  function tradeTime(t, miss) {
    var c = isoMs(t.closedAt);
    if (c !== null) return { ms: c, dateOnly: false };
    var d = R.bkk.noonOf(t.exitDate);
    if (d !== null) { miss.add('CLOSE_TIME_DATE_ONLY', t.id); return { ms: d, dateOnly: true }; }
    miss.add('CLOSE_TIME', t.id); return { ms: 0, dateOnly: false };
  }

  /* exit reason for whipsaw / re-entry: explicit 'stop'|'target'|'manual' else derived from price vs the row's stop / target (the app's own exitReason is a free tag) */
  function exitReasonOf(t, side) {
    if (t.exitReason === 'stop' || t.exitReason === 'target' || t.exitReason === 'manual') return t.exitReason;
    var x = n(t.exitPrice), sl = n(t.sl), tp = n(t.tp), long = side !== 'short';
    if (pos(x) && pos(sl) && (long ? x <= sl + 1e-9 : x >= sl - 1e-9)) return 'stop';
    if (pos(x) && pos(tp) && (long ? x >= tp - 1e-9 : x <= tp + 1e-9)) return 'target';
    return pos(x) ? 'manual' : null;
  }
  /* Build engine ideas for ONE account. Returns {ideas, info:{id→meta}, excluded:[...]} */
  function buildAccount(src, acc, miss) {
    var B = (src.books && src.books[acc.id]) || {}, S = B.settings || {}, trades = Array.isArray(B.trades) ? B.trades : [];
    var fx = pos(n(S.fx)) ? n(S.fx) : null, portCur = src.portCur || { core: 'THB', satB: 'USD' };
    var cards = (src.cards || []).filter(function (c) { return c && c.acct === acc.id; });
    var ideasDocs = (src.ideas || []);
    var cardByTrade = {}; cards.forEach(function (c) { if (c.trade_id) cardByTrade[c.trade_id] = c; if (c.acc_trade_id) cardByTrade[c.acc_trade_id] = c; });
    var slotByTrade = {}, slotIdea = {};
    ideasDocs.forEach(function (i) { var sl = i && i.accts && i.accts[acc.id]; if (sl && sl.trade_id) { slotByTrade[sl.trade_id] = i; } });
    // group trade rows by posGroup first, then by owner (card / sat idea / loose)
    var byPg = {}; trades.forEach(function (t) { if (!t) return; var g = t.posGroup || t.id; (byPg[g] = byPg[g] || []).push(t); });
    var groups = {};   // ownerKey -> {rows, card, idea}
    Object.keys(byPg).forEach(function (g) {
      var rows = byPg[g], card = null, idea = null;
      rows.forEach(function (t) { card = card || cardByTrade[t.id] || null; idea = idea || slotByTrade[t.id] || null; });
      var key = card ? 'c:' + card.id : idea ? 's:' + idea.id : 'g:' + g;
      var G = groups[key] || (groups[key] = { key: key, rows: [], card: card, idea: idea }); G.rows = G.rows.concat(rows);
    });
    var out = [], info = {}, excluded = [];

    Object.keys(groups).forEach(function (key) {
      var G = groups[key], rows = G.rows.filter(function (t) { return t.status !== 'cancelled'; });
      if (!rows.length) return;
      var t0 = rows[0], port = t0.port, strategy, assumed = false;
      if (G.card) strategy = coreTrack(G.card);
      else if (port === 'satB' || G.idea) strategy = 'sat';
      else if (port === 'core') { strategy = 'winner'; assumed = true; miss.add('STRATEGY', t0.id); }
      else { miss.add('PORT', t0.id); excluded.push({ id: t0.id, sym: t0.sym, why: 'PORT' }); return; }
      var cur = t0.cur || portCur[port] || null, usd = cur === 'USD';
      if (usd && fx === null) { miss.add('FX', t0.id); excluded.push({ id: key, sym: t0.sym, why: 'FX' }); return; }
      var efx = usd ? fx : 1, mult = pos(n(t0.mult)) ? n(t0.mult) : 1, side = t0.bias === 'Short' ? 'short' : 'long';
      // tranches: key = accelerator flag + entry price
      var trs = {}, exits = [], hist = G.card && Array.isArray(G.card.stopHistory) && G.card.stopHistory.length ? G.card.stopHistory : null;
      var anyOpen = false, anyPlan = false, lastExit = null, sl0Missing = false;
      rows.forEach(function (t) {
        if (t.status === 'plan') { anyPlan = true; return; }
        var tk = (t.acc ? 'a' : 'b') + '|' + t.entry, T = trs[tk];
        var init = pos(n(t.sl0)) ? n(t.sl0) : (hist && pos(n(hist[0].from)) && !t.acc ? n(hist[0].from) : null);
        if (!T) T = trs[tk] = { id: key + '#' + tk, entry: n(t.entry), qty: 0, stop: null, initialStop: init, mult: n(t.mult) > 0 ? n(t.mult) : 1, fx: efx, stopConfirmed: false, acc: !!t.acc, openedAt: t.openedAt || t.date || null };
        T.qty += n(t.qty) || 0;
        if (t.status === 'open') { anyOpen = true; T.stop = n(t.sl); }
        else if (t.status === 'closed') {
          if (T.stop === null) T.stop = n(t.sl);
          var tm = tradeTime(t, miss); if (lastExit === null || tm.ms > lastExit) lastExit = tm.ms;
          exits.push({ id: 'x:' + t.id, time: tm.ms, qty: n(t.qty) || 0, price: n(t.exitPrice), fees: 0, swap: 0, trancheId: T.id, reason: exitReasonOf(t, side), dateOnly: tm.dateOnly });
          if (!t.exitReason) miss.add('EXIT_REASON', t.id);
        }
        if (init === null) sl0Missing = true;
      });
      var tranches = Object.keys(trs).map(function (k) { return trs[k]; });
      tranches.forEach(function (T) {
        if (T.initialStop === null) { T.initialStop = T.stop; T.initialStopUnknown = true; miss.add('INITIAL_STOP', key); }
        // stop confirmed = a recorded stop move on the card's history that ends at the current stop (inferred; the app has no explicit marker)
        if (hist && !T.acc && pos(T.stop) && pos(n(hist[hist.length - 1].to)) && Math.abs(n(hist[hist.length - 1].to) - T.stop) < 1e-9) T.stopConfirmedInferred = true;
        miss.add('CONFIRMED_STOP', key);
      });
      miss.add('COSTS', key);
      // working orders
      var wo = [], placedAt = null;
      if (G.idea) {   // Sat: idea.ln4.placedAt = Ordered
        var pl = G.idea.ln4 && G.idea.ln4.placedAt; if (pl) placedAt = pl;
      }
      var status = anyOpen ? 'holding' : (tranches.length && !anyPlan ? 'closed' : (anyPlan ? (placedAt ? 'ordered' : 'planned') : 'planned'));
      if (G.idea && anyPlan && placedAt) rows.forEach(function (t) {
        if (t.status !== 'plan') return;
        if (!pos(n(t.qty))) miss.add('ORDER_QTY', t.id);
        if (isoMs(placedAt) === null) miss.add('ORDER_TIME', t.id);
        wo.push({ id: 'w:' + t.id, qty: n(t.qty), entry: n(t.entry), stop: n(t.sl), mult: mult, fx: efx, at: isoMs(placedAt) });
      });
      var idea = { id: key, account: acc.id, strategy: strategy, side: side, status: status, product: symKey(t0.sym), sym: t0.sym, tranches: tranches, exits: exits, entryFees: 0, workingOrders: wo, rowIds: rows.map(function (t) { return t.id; }) };
      if (status === 'closed') idea.closedAt = lastExit;
      if (G.card) { idea.cardId = G.card.id; idea.market = marketOf(t0.sym, G.card); }
      else idea.market = marketOf(t0.sym, null);
      if (!G.card && port === 'core' && idea.market === null) miss.add('EXCHANGE', t0.id);
      out.push(idea);
      info[key] = { strategy: strategy, assumedStrategy: assumed, sym: t0.sym, card: G.card ? G.card.id : null, satIdea: G.idea ? G.idea.id : null, cur: cur, hasAcc: tranches.some(function (T) { return T.acc; }), nTranches: tranches.length };
    });

    // cards without any trade row: Core working orders (plan.ps1.rows with placed flags) / drafts
    cards.forEach(function (c) {
      if (c.status === 'closed' || c.archived === true) return;
      var has = Object.keys(info).some(function (k) { return info[k].card === c.id; });
      if (c.status === 'open' && !has) { miss.add('CARD_NO_TRADE', c.id); return; }
      var track = coreTrack(c), pl = c.plan || {}, rowsP = pl.ps1 && Array.isArray(pl.ps1.rows) ? pl.ps1.rows : null;
      var market = marketOf(c.ticker, c), cur = market === 'TH' ? 'THB' : 'USD';
      if (cur === 'USD' && fx === null) { miss.add('FX', c.id); return; }
      var efx = cur === 'USD' ? fx : 1, k = (c.lots || []).length, plv = (c.ln4 && c.ln4.placedLv && typeof c.ln4.placedLv === 'object') ? c.ln4.placedLv : {}, wo = [];
      var levels = rowsP && rowsP.length ? rowsP : (pos(n(pl.entry)) ? [{ px: pl.entry, qty: null }] : []);
      levels.forEach(function (lv, j) {
        var placed = (plv[j] && j >= k) || (c.ln4 && c.ln4.placedAt && j === k);
        if (!placed) return;
        if (!pos(n(lv.qty))) miss.add('ORDER_QTY', c.id);
        wo.push({ id: 'w:' + c.id + ':' + j, qty: n(lv.qty), entry: n(lv.px), stop: n(pl.stop), mult: 1, fx: efx, at: isoMs(plv[j]) !== null ? isoMs(plv[j]) : isoMs(c.ln4 && c.ln4.placedAt) });
        if (isoMs(plv[j]) === null && isoMs(c.ln4 && c.ln4.placedAt) === null) miss.add('ORDER_TIME', c.id);
      });
      if (has) {   // holding card with extra placed levels → attach reservation to the existing idea
        var ex = out.filter(function (i) { return info[i.id] && info[i.id].card === c.id; })[0];
        if (ex && wo.length) ex.workingOrders = ex.workingOrders.concat(wo);
        return;
      }
      var id = 'c:' + c.id, idea = { id: id, account: acc.id, strategy: track, side: 'long', status: wo.length ? 'ordered' : 'planned', product: symKey(c.ticker), sym: c.ticker, tranches: [], exits: [], entryFees: 0, workingOrders: wo,
        cardId: c.id, market: market, plan: { entry: n(pl.entry), stop: n(pl.stop), tp: n(pl.tp || pl.target), levels: levels.map(function (l) { return { px: n(l.px), qty: n(l.qty) }; }), starter: !!pl.starter } };
      out.push(idea); info[id] = { strategy: track, sym: c.ticker, card: c.id, cur: cur, nTranches: 0, plannedOnly: true };
    });
    // Sat ideas of this account with no trade yet (drafts / planned)
    ideasDocs.forEach(function (i) {
      var sl = i && ((i.accts && i.accts[acc.id]) || (i.pb_acct === acc.id && i.ln4 && i.ln4.placedAt ? {} : null)); if (!i || !sl || sl.skip) return;   /* HF5 — a Place-order plan (pb_acct, no account slot until Filled) is a live working order */
      var has = Object.keys(info).some(function (k) { return info[k].satIdea === i.id; });
      if (has || i.status === 'closed' || i.status === 'cancelled') return;
      var placed = i.ln4 && i.ln4.placedAt, id = 's:' + i.id;
      var cur = (src.specs && src.specs[symKey(i.asset)] && src.specs[symKey(i.asset)].cur) || 'USD';
      var efx = cur === 'USD' ? fx : 1; if (efx === null) { miss.add('FX', i.id); return; }
      var mult = (src.specs && src.specs[symKey(i.asset)] && pos(n(src.specs[symKey(i.asset)].contract))) ? n(src.specs[symKey(i.asset)].contract) : null;
      var snap0 = i.ln4 && i.ln4.snap && i.ln4.snap['0'], qty = pos(n(sl.lot)) ? n(sl.lot) : (snap0 && pos(n(snap0.lot)) ? n(snap0.lot) : null), wo = [];   /* HF5 — no slot lot yet: the lot stored with the order snapshot */
      if (placed && qty !== null && mult !== null) wo.push({ id: 'w:' + i.id, qty: qty, entry: n(i.entry), stop: n(i.sl), mult: mult, fx: efx, at: isoMs(placed) });
      if (placed && (qty === null || mult === null)) miss.add('ORDER_QTY', i.id);
      out.push({ id: id, account: acc.id, strategy: 'sat', side: i.bias === 'Short' ? 'short' : 'long', status: placed ? 'ordered' : 'planned', product: symKey(i.asset), sym: i.asset, tranches: [], exits: [], entryFees: 0, workingOrders: wo,
        plan: { entry: n(i.entry), stop: n(i.sl), tp: n(i.tp), lot: qty } });
      info[id] = { strategy: 'sat', sym: i.asset, satIdea: i.id, cur: cur, nTranches: 0, plannedOnly: true };
    });
    return { ideas: out, info: info, excluded: excluded, fx: fx, S: S };
  }

  /* ── helpers on engine results ── */
  function totQty(i) { return sumBy(i.tranches, function (t) { return t.qty; }); }
  function uvOf(t) { return (t.mult > 0 ? t.mult : 1) * (t.fx > 0 ? t.fx : 1); }
  function ideaAvg(i) { var q = totQty(i); return q > 0 ? sumBy(i.tranches, function (t) { return t.entry * t.qty; }) / q : null; }
  function riskAt(i, which) {   // money risk of the WHOLE idea (all tranche qty) at current or initial stop, floor 0 per tranche
    var s = 0, dir = i.side === 'short' ? -1 : 1, unknown = false;
    i.tranches.forEach(function (t) { var st = which === 'initial' ? t.initialStop : t.stop; if (!pos(st)) { unknown = true; return; } s += Math.max(0, (t.entry - st) * dir * t.qty * uvOf(t)); });
    return unknown ? null : s;
  }
  function pct(x, eq) { return num(x) && pos(eq) ? x / eq * 100 : null; }

  /* Engine "would size today" for one idea (full size as entered) */
  function engineSize(i, meta, ctx) {
    var out = { rptPct: null, qty: null, risk: null, riskPct: null, reasons: [], notes: [] }, eq = ctx.weekEquity;
    var avg = ideaAvg(i) !== null ? ideaAvg(i) : (i.plan ? i.plan.entry : null), t0 = i.tranches[0];
    var stop = t0 ? t0.initialStop : (i.plan ? i.plan.stop : (i.workingOrders[0] ? i.workingOrders[0].stop : null));
    var spec = ctx.spec(i), mult = t0 ? t0.mult : (i.workingOrders[0] ? i.workingOrders[0].mult : (spec && spec.contract) || (i.market ? 1 : null));
    var efx = t0 ? t0.fx : (i.workingOrders[0] ? i.workingOrders[0].fx : (meta.cur === 'USD' ? ctx.fx : 1));
    var lotStep = spec ? spec.lotStep : null, minLot = spec ? spec.minLot : null;
    if (i.strategy !== 'sat') { var mk = i.market; if (mk === 'TH') { lotStep = 100; minLot = 100; } else if (mk === 'US') { lotStep = 1; minLot = 1; } else { lotStep = null; } }
    var base = i.strategy === 'winner' ? R.POLICY.mom.rptPct : i.strategy === 'ladder' ? R.POLICY.comp.pilotPct : null;
    var hw = ctx.homework[symKey(i.sym)], frac = 1, notes = out.notes, factor = 1, factors = out.factors = [];
    if (i.strategy === 'winner') {
      factors.push('BASE_' + R.POLICY.mom.rptPct);
      if (hw === undefined) notes.push('homework state unknown — shown at 100%'); else if (hw === false) { frac = R.POLICY.hwFactor.mom; notes.push('homework not done → ' + Math.round(frac * 100) + '%'); factors.push('HOMEWORK_' + Math.round(frac * 100)); }
      if (ctx.regime) { factor = R.compFactor(ctx.regime, ctx.emergencyFactor); var mp = Math.round(factor * 100); if (mp < 100) factors.push((ctx.emergencyFactor && ctx.emergencyFactor < ctx.regime.factor ? 'EMERGENCY_' : 'REGIME_') + mp); }   /* RM1: Momentum also takes min(Regime, Emergency) */
      else if (ctx.emergencyFactor && ctx.emergencyFactor < 1) { factor *= ctx.emergencyFactor; factors.push('EMERGENCY_50'); }
    } else if (i.strategy === 'ladder') {
      /* Compounder: the Pilot (0.50% of the 1% plan) IS the 50% homework phase — the homework cap is a phase cap, never a second multiplier (RE-C1 §0).
         Regime factor applies to NEW entries: min(Regime, Emergency). Starter ¼ (Training ON) = half of the Pilot. */
      factors.push('PILOT_' + R.POLICY.comp.pilotPct);
      if (hw === false) notes.push('thesis not done → Pilot only (no further cut)');
      if (ctx.regime) { factor = R.compFactor(ctx.regime, ctx.emergencyFactor); var pc = Math.round(factor * 100); if (pc < 100) factors.push((ctx.emergencyFactor && ctx.emergencyFactor < ctx.regime.factor ? 'EMERGENCY_' : 'REGIME_') + pc); if (ctx.regime.stale) factors.push('REGIME_STALE'); }
      if (ctx.starterOn === true) { frac = R.POLICY.comp.starter * 2; factors.push('STARTER_25'); }
    }
    var rpts = base !== null ? [base] : [R.POLICY.sat.stepRpt[ctx.satStepIndex], R.POLICY.sat.stepRpt[ctx.satStepIndex] * R.POLICY.sat.condReduced];
    if (i.strategy === 'sat') notes.push('Satellite: Condition unknown in history → shown at 100% and 65% of the current step (' + (ctx.satStepIndex + 1) + ')');
    var msPct = ctx.minStopPct(i);
    var minDist = pos(msPct) && pos(avg) ? avg * msPct / 100 : null;
    var variants = rpts.map(function (r) {
      var z = R.sizeOrder({ equity: eq, rptPct: r, factor: factor, fraction: frac, entry: avg, stop: stop, side: i.side, minStopDist: minDist, mult: mult, fx: efx, lotStep: lotStep, minLot: minLot });
      return { rptPct: r, effectiveRptPct: z.effectiveRptPct, qty: z.qty, risk: z.actualRisk, riskPct: z.actualRiskPct, reasons: z.reasons, minStopApplied: !!z.minStopApplied };
    });
    out.variants = variants; var v0 = variants[0]; out.rptPct = v0.rptPct; out.qty = v0.reasons.length ? null : v0.qty; out.risk = v0.reasons.length ? null : v0.risk; out.riskPct = v0.reasons.length ? null : v0.riskPct; out.reasons = v0.reasons.slice();
    out.minStopApplied = v0.minStopApplied; out.stopUsed = stop; out.entryUsed = avg;
    return out;
  }

  /* ── Journal outcome badges (old rounded rule vs strict) ── */
  function oldOutcome(p) { var r = Math.round(Number(p) || 0) || 0; return r > 0 ? 'win' : r < 0 ? 'loss' : 'be'; }
  function badges(trades, acct) {
    var tot = 0, changed = [], pnlRows = 0;
    trades.forEach(function (t) {
      if (!t || t.status !== 'closed' || !(n(t.exitPrice) > 0) || !(n(t.entry) > 0) || !(n(t.qty) > 0)) return;
      tot++; var dir = t.bias === 'Short' ? -1 : 1, p = (n(t.exitPrice) - n(t.entry)) * n(t.qty) * (n(t.mult) > 0 ? n(t.mult) : 1) * dir, o = oldOutcome(p), s = R.outcome(p);
      pnlRows++; if (o !== s) changed.push({ id: t.id, sym: t.sym, date: t.exitDate || t.date || null, pnl: p, old: o, strict: s });
    });
    return { closedRows: tot, changed: changed.length, list: changed.slice(0, 30) };
  }

  /* ── report ── */
  function build(src) {
    var now = src.now, miss = new Missing(), report = { generatedAt: now, generatedAtBkk: R.bkk.dayKey(now), policy: 'RE1-decisions rev 2 + answers-A', baseCurrency: 'THB', readOnly: true, accounts: [], notes: [] };
    var ff = src.ff || {};
    var regime = R.regimeFromFundflow(ff.demo ? null : ff, now), signals = regime.signals;   /* RM1: the one shared reader */
    report.regime = { signals: signals, factor: regime.factor, base: regime.base, fresh: regime.fresh, ageDays: regime.ageDays, asOf: regime.asOf, equity: regime.equity, credit: regime.credit, fallback: regime.fallback, demo: !!ff.demo, flags: regime.flags };
    if (ff.demo) report.notes.push('fundflow.json not loaded (demo data) — regime result is not usable');

    (src.accounts || []).forEach(function (acc) {
      var M = new Missing(), A = buildAccount(src, acc, M), S = A.S || {};
      var out = { id: acc.id, name: acc.name, ports: acc.ports || null };
      // equity basis: engine needs confirmed snapshots; none exist → entered-capital PROXY (flagged everywhere)
      var cap = S.capital || {}, pc = src.portCur || { core: 'THB', satB: 'USD' }, ports = acc.ports || ['core', 'satB'];
      var coreV = ports.indexOf('core') >= 0 && n(cap.core) !== null ? n(cap.core) * (pc.core === 'USD' ? (A.fx || 0) : 1) : 0;
      var satV = ports.indexOf('satB') >= 0 && n(cap.satB) !== null ? n(cap.satB) * (pc.satB === 'USD' ? (A.fx || 0) : 1) : 0;
      var proxy = coreV + satV, realSnaps = Array.isArray(S.equitySnapshots) ? S.equitySnapshots : null;
      var basisKind = (realSnaps && realSnaps.length) ? 'confirmed snapshots' : 'PROXY (entered capital, not a snapshot)';
      if (!(realSnaps && realSnaps.length)) M.add('EQUITY_SNAPSHOT', acc.id);
      var basis = liveBasis(S, now, proxy);
      out.equity = { basisKind: basisKind, proxyEquity: pos(proxy) ? proxy : null, weekEquity: basis.ok ? basis.weekEquity : null, monthEquity: basis.ok ? basis.monthEquity : null, currentEquity: basis.ok ? basis.currentEquity : null,
        snapshotState: basis.state, snapshotAgeDays: basis.ageDays != null ? basis.ageDays : null, reasons: basis.reasons.slice(), fx: A.fx, snapshotsAvailable: realSnaps ? realSnaps.length : 0 };
      var costsFor = function () { return null; };   // no cost settings in the app yet
      var ideas = A.ideas, wk0 = R.bkk.weekStart(now), mo0 = R.bkk.monthStart(now);
      var live = ideas.filter(function (i) { return i.status === 'holding' || i.status === 'ordered'; });

      // Satellite state from history
      var satI = ideas.filter(function (i) { return i.strategy === 'sat'; });
      var attempts = satI.filter(function (i) { return i.status === 'closed' && num(i.closedAt) && i.closedAt > 0; }).map(function (i) { return { id: i.id, closeAt: i.closedAt, net: R.ideaRealizedNet(i) }; });
      var step = R.satStepState(attempts, now);
      var dayAtt = satI.filter(function (i) { return i.tranches.length || i.status === 'ordered'; }).map(function (i) {
        var t0 = i.tranches[0]; var start = t0 && isoMs(t0.openedAt) !== null ? isoMs(t0.openedAt) : (t0 && R.bkk.noonOf(t0.openedAt)); if (start == null) start = i.workingOrders[0] && i.workingOrders[0].at || null;
        return { id: i.id, product: i.product, startAt: start, status: i.status === 'closed' ? 'closed' : i.status === 'ordered' ? 'working' : 'open', net: i.status === 'closed' ? R.ideaRealizedNet(i) : null, exitReason: i.exits[0] && i.exits[0].reason || null };
      }).filter(function (a) { return num(a.startAt); });
      var queue = satI.filter(function (i) { return i.status === 'ordered' || i.status === 'holding'; });
      var satBud = R.satBudgetCheck({ basis: basis, now: now, account: acc.id, ideas: ideas, costsFor: costsFor, candidateRisk: 0 });
      out.satellite = { step: step.step, locked: step.locked, weeklyNet: step.weeklyNet, baseRptPct: step.baseRptPct, resetAt: step.resetAt, attemptsThisWeek: step.trace.length, trace: step.trace,
        queue: queue.map(function (i) { return { id: i.id, sym: i.sym, status: i.status }; }), activeSetups: queue.length, queueNote: queue.length > 1 ? 'more than one active setup (legacy) — nothing is cancelled' : '',
        todayAttempts: dayAtt.filter(function (a) { return R.bkk.dayKey(a.startAt) === R.bkk.dayKey(now); }).map(function (a) { return { id: a.id, product: a.product, status: a.status, net: a.net }; }),
        budget: pickBudget(satBud, 'sat'), staleOrders: R.satStaleOrders(ideas, now) };

      // Momentum
      var mom = R.momentumState({ now: now, account: acc.id, ideas: ideas, costsFor: costsFor, cfg: null });
      var momChk = R.momentumCheck({ now: now, account: acc.id, basis: basis, ideas: ideas, costsFor: costsFor, candidate: { ideaId: '__none__', isAddition: true, riskMoney: 0 } });
      out.momentum = { completedLossesThisWeek: mom.completedLosses, reservedIdeas: mom.reservedIdeas.length, reservedIds: mom.reservedIdeas, ammoUsed: mom.ammoUsed, ammoMax: R.POLICY.mom.ammo,
        weekGrossLoss: mom.weekGross, monthGrossLoss: mom.monthGross, openExposure: mom.open, reservedOrderRisk: mom.reserved, money: momChk.money || null, unknownCostIdeas: mom.unknown.length, reasonsIfNewOrder: momChk.reasons, flags: momChk.flags,
        note: 'costs not recorded: no reservation can be released (Option C needs a known net-breakeven)' };

      // Compounder
      var comp = ideas.filter(function (i) { return i.strategy === 'ladder'; });
      var cycles = comp.filter(function (i) { return i.status === 'closed' && num(i.closedAt) && i.closedAt > 0; }).map(function (i) { return { id: i.id, flatAt: i.closedAt, net: R.ideaRealizedNet(i) }; });
      var streak = R.compStreak(cycles, []);
      var heat = R.compHeat(basis.ok ? fxIdeas(ideas, A.fx, basis.weekFx) : ideas, acc.id, costsFor, basis.ok ? basis.weekEquity : null, basis.ok ? basis.currentEquity : null);   /* TS1 — heat uses the week-snapshot FX like the other limits */
      var legacy = [];
      comp.forEach(function (i) {
        var m = A.info[i.id] || {}, ls = R.compLegacyShape({ tranches: i.tranches.length, accelLots: i.tranches.filter(function (t) { return t.acc; }).length });
        var card = (src.cards || []).filter(function (c) { return c.id === m.card; })[0], lots = card && Array.isArray(card.lots) ? card.lots : [];
        var accLots = lots.filter(function (l) { return l && (l.layer === 'acc' || l.acc === true); }).length, ls2 = R.compLegacyShape({ tranches: Math.max(i.tranches.length, lots.length), accelLots: Math.max(accLots, i.tranches.filter(function (t) { return t.acc; }).length) });
        if (ls2.legacy && i.status !== 'closed') legacy.push({ id: i.id, sym: i.sym, status: i.status, tranches: Math.max(i.tranches.length, lots.length), accelerator: Math.max(accLots, 0) || undefined, why: ls2.why, strategyKey: card ? card.strategy : null });
      });
      out.compounder = { streak: streak.streak, locked: streak.locked, cyclesClosed: cycles.length, heatMoney: heat.money, heatPctWeekStart: heat.pct, heatPctCurrent: heat.pctCurrent, heatCapPct: R.POLICY.comp.heatCapPct, heatCount: heat.count,
        regimeFactor: regime.factor, regimeFresh: regime.fresh, regimeAgeDays: regime.ageDays, regimeFallback: regime.fallback, legacyShapeCards: legacy };

      // Emergency: needs confirmed snapshots
      out.emergency = realSnaps && realSnaps.length ? (function () { var last = realSnaps[realSnaps.length - 1]; var e = R.emergencyStep(null, last, basis.ok ? { equity: basis.monthEquity, at: basis.monthAt } : null, S.cashFlows || []); return { state: e.active ? 'ACTIVE' : 'off', declinePct: e.declinePct, factor: e.factor }; })() : { state: 'n/a', reason: 'no confirmed equity snapshots — Emergency cannot be evaluated; shown as off (factor 1)', factor: 1 };

      // Positions & working orders: old vs engine
      var ctx = { weekEquity: basis.ok ? basis.weekEquity : null, fx: A.fx, homework: src.homework || {}, satStepIndex: step.stepIndex, regime: regime, emergencyFactor: 1, starterOn: false,
        spec: function (i) { return (src.specs && src.specs[symKey(i.sym)]) || null; },
        minStopPct: function (i) { var ms = S.psRisk && S.psRisk.minStop; var v = ms && (ms[i.sym] != null ? ms[i.sym] : ms[symKey(i.sym)]); return pos(n(v)) ? n(v) : null; } };
      var rowsOut = [];
      live.forEach(function (i) {
        var meta = A.info[i.id] || {}, es = ctx.weekEquity ? engineSize(i, meta, ctx) : { reasons: ['EQUITY_MISSING'], variants: [] };
        var spec = ctx.spec(i);
        if (i.strategy === 'sat' && !spec) M.add('LOT_SPEC', i.sym);
        var res0 = R.ideaResult(i, null), resv = R.exposures([i], costsFor);
        var oldQty = i.status === 'holding' ? totQty(i) : (i.workingOrders[0] ? sumBy(i.workingOrders, function (w) { return w.qty || 0; }) : null);
        var heldQty = i.status === 'holding' ? res0.remainingQty : null;
        var oldRiskCur = i.status === 'holding' ? res0.principalRisk : null;
        var oldRiskInit = i.tranches.length ? riskAt(i, 'initial') : null;
        var woRisk = i.workingOrders.length ? sumBy(i.workingOrders, function (w) { return pos(w.qty) && pos(w.entry) && pos(w.stop) ? w.qty * Math.abs(w.entry - w.stop) * (w.mult > 0 ? w.mult : 1) * (w.fx > 0 ? w.fx : 1) : 0; }) : null;
        var why = [];
        var oldInitPct = pct(i.status === 'holding' ? oldRiskInit : woRisk, ctx.weekEquity);
        if (es.rptPct != null && oldInitPct != null) { if (oldInitPct > es.rptPct * 1.05) why.push('OLD_RISK_ABOVE_ENGINE_RPT'); else if (oldInitPct < es.rptPct * 0.7) why.push('OLD_RISK_BELOW_ENGINE_RPT'); }
        if (es.minStopApplied) why.push('MIN_STOP_SIZING');
        (es.factors || []).forEach(function (f) { if (/^(HOMEWORK|REGIME|EMERGENCY|STARTER)_/.test(f)) why.push(f); });
        if (es.reasons.length) why = why.concat(es.reasons);
        if (i.tranches.some(function (t) { return t.initialStopUnknown; })) why.push('INITIAL_STOP_UNKNOWN');
        if (basisKind !== 'confirmed snapshots') why.push('EQUITY_PROXY');
        var meta2 = A.info[i.id] || {};
        rowsOut.push({ id: i.id, sym: i.sym, strategy: i.strategy, status: i.status, side: i.side, legacyShape: comp.indexOf(i) >= 0 && legacy.some(function (l) { return l.id === i.id; }),
          old: { qtyAsEntered: oldQty, qtyHeldNow: heldQty, avgEntry: ideaAvg(i), currentStop: i.tranches[0] ? i.tranches[0].stop : (i.workingOrders[0] ? i.workingOrders[0].stop : null), initialStop: i.tranches[0] ? i.tranches[0].initialStop : null,
            principalRiskAtCurrentStop: oldRiskCur, riskAtInitialStop: oldRiskInit, workingOrderRisk: woRisk, riskPctOfEquityAtInitial: oldInitPct },
          engine: { rptPct: es.rptPct, effectiveRptPct: es.variants && es.variants[0] ? es.variants[0].effectiveRptPct : null, factors: es.factors || [], qty: es.qty, riskMoney: es.risk, riskPct: es.riskPct, variants: es.variants, reasons: es.reasons, notes: es.notes },
          whyDifferent: Array.from(new Set(why)), exposure: res0.exposure, projectedNet: res0.projectedNet, costUnknown: res0.costUnknown, tranches: i.tranches.length, accelerator: meta2.hasAcc || false });
      });
      out.positions = rowsOut;

      // Orders that would be blocked today (Ordered + complete Planned), evaluated as a NEW order against everything else
      var blocked = [], ddStopNow = basis.ok && liveEmergency(basis.snaps || [], S.cashFlows || [], S.re1 && S.re1.peak).stopped === true;
      ideas.filter(function (i) { return i.status === 'ordered' || i.status === 'planned'; }).forEach(function (i) {
        var others = ideas.filter(function (x) { return x !== i; }), plan = i.plan || {}, w = i.workingOrders, e0 = w[0] ? w[0].entry : plan.entry, s0 = w[0] ? w[0].stop : plan.stop;
        var risk = w.length ? sumBy(w, function (x) { return pos(x.qty) && pos(x.entry) && pos(x.stop) ? x.qty * Math.abs(x.entry - x.stop) * (x.mult > 0 ? x.mult : 1) * (x.fx > 0 ? x.fx : 1) : 0; }) : (plan.levels && pos(s0) ? sumBy(plan.levels, function (l) { return pos(l.qty) && pos(l.px) ? l.qty * Math.abs(l.px - s0) : 0; }) : null);
        var r = [], f = [];
        if (!basis.ok) r = r.concat(basis.reasons);
        else if (i.strategy === 'winner') { var c = R.momentumCheck({ now: now, account: acc.id, basis: basis, ideas: others, costsFor: costsFor, candidate: { ideaId: i.id, isAddition: false, riskMoney: risk === null ? null : risk } }); r = c.reasons; f = c.flags; }
        else if (i.strategy === 'sat') {
          if (step.locked) r.push('SAT_LOCKED');
          r = r.concat(R.satQueueCheck(others, acc.id, i.id).reasons);
          if (plan.tp != null || w.length) { var ord = R.satEntryOrder({ side: i.side, entry: e0, stop: s0, tp: plan.tp }); if (plan.tp != null) r = r.concat(ord.reasons); }
          r = r.concat(R.satDailyCheck({ now: now, product: i.product, attempts: dayAtt.filter(function (a) { return a.id !== i.id; }), reentry: {} }).reasons);
          var sb = R.satBudgetCheck({ basis: basis, now: now, account: acc.id, ideas: others, costsFor: costsFor, candidateRisk: risk }); r = r.concat(sb.reasons); f = f.concat(sb.flags);
        } else {
          if (streak.locked) r.push('COMP_LOCKED');
          var h2 = R.compHeat(fxIdeas(others, A.fx, basis.weekFx), acc.id, costsFor, basis.weekEquity, basis.currentEquity); if (risk !== null && h2.money + risk > basis.weekEquity * R.POLICY.comp.heatCapPct / 100 + 1e-7) r.push('COMP_HEAT');
          f = f.concat(regime.flags);
        }
        if (basis.ok && ddStopNow) r.unshift('DD_STOP');
        if (r.length) blocked.push({ id: i.id, sym: i.sym, strategy: i.strategy, status: i.status, reasons: Array.from(new Set(r)), flags: Array.from(new Set(f)), candidateRisk: risk });
      });
      out.wouldBeBlocked = blocked;

      out.legacyShapeCards = legacy;
      out.excluded = A.excluded;
      out.journalBadges = badges(Array.isArray((src.books[acc.id] || {}).trades) ? src.books[acc.id].trades : [], acc.id);
      var ml = M.list(); ml.forEach(function (e) { e.note = MISSING_NOTES[e.code] || ''; }); out.missing = ml;
      out.counts = { tradeRows: ((src.books[acc.id] || {}).trades || []).length, ideas: ideas.length, holding: ideas.filter(function (i) { return i.status === 'holding'; }).length, ordered: ideas.filter(function (i) { return i.status === 'ordered'; }).length, planned: ideas.filter(function (i) { return i.status === 'planned'; }).length, closed: ideas.filter(function (i) { return i.status === 'closed'; }).length };
      report.accounts.push(out);
    });
    report.missingGlobal = miss.list();
    return report;
  }
  function pickBudget(b, k) { return { allowedNow: b.allowed, weekUsed: b.weekUsed, weekCap: b.weekCap, monthUsed: b.monthUsed, monthCap: b.monthCap, weeklyNet: b.weeklyNet, monthlyNet: b.monthlyNet, reasons: b.reasons, flags: b.flags }; }

  /* ── markdown ── */
  function f2(x, d) { return num(x) ? (Math.round(x * Math.pow(10, d == null ? 2 : d)) / Math.pow(10, d == null ? 2 : d)).toString() : 'Unknown'; }
  function money(x) { return num(x) ? Math.round(x).toLocaleString('en-US') : 'Unknown'; }
  function esc(s) { return String(s == null ? '' : s).replace(/\|/g, '\\|').replace(/\n/g, ' '); }
  function toMarkdown(rp) {
    var L = [], P = function (s) { L.push(s == null ? '' : s); };
    P('# RE1 dry run — ' + rp.generatedAtBkk + ' (Asia/Bangkok)'); P('');
    P('**Read-only.** Nothing was written to Firestore or localStorage. Missing data is shown as `Unknown`, never 0. Accounts are never mixed. Policy: ' + rp.policy + '. Base currency ' + rp.baseCurrency + '.'); P('');
    rp.notes.forEach(function (t) { P('> ' + t); });
    P('## Regime (new-entry budget modifier · Momentum + Compounder)'); P('');
    P('- ACWI/BIL (SMA 20/50): ' + rp.regime.signals.acwi + ' · HYG/IEI (SMA 20/50): ' + rp.regime.signals.hyg + ' · oldest input date ' + (rp.regime.signals.asOf || 'Unknown'));
    P('- Modifier **' + Math.round(rp.regime.factor * 100) + '%**' + (rp.regime.fallback ? ' (fallback)' : '') + ' · fresh: ' + (rp.regime.fresh ? 'yes' : 'NO') + (rp.regime.ageDays != null ? ' (' + rp.regime.ageDays + ' calendar days old)' : '')); P('');
    rp.accounts.forEach(function (a) {
      P('---'); P('## Account: ' + esc(a.name || a.id) + ' (`' + a.id + '`)'); P('');
      P('Rows: ' + a.counts.tradeRows + ' trade rows → ' + a.counts.ideas + ' ideas (holding ' + a.counts.holding + ' · ordered ' + a.counts.ordered + ' · planned ' + a.counts.planned + ' · closed ' + a.counts.closed + ')'); P('');
      P('### Equity basis');
      P('- Basis: **' + a.equity.basisKind + '** · week-start ' + money(a.equity.weekEquity) + ' · month-start ' + money(a.equity.monthEquity) + ' · FX ' + (a.equity.fx == null ? 'Unknown' : a.equity.fx) + ' · confirmed snapshots found: ' + a.equity.snapshotsAvailable);
      if (a.equity.reasons.length) P('- Gate reasons: ' + a.equity.reasons.join(', '));
      P('- Emergency: **' + a.emergency.state + '**' + (a.emergency.reason ? ' — ' + a.emergency.reason : '')); P('');
      P('### Exposure and budget usage (this week / month)');
      var m = a.momentum, sb = a.satellite.budget, c = a.compounder;
      P('| Strategy | Week | Month | Notes |'); P('|---|---|---|---|');
      P('| Momentum | gross losses ' + money(m.weekGrossLoss) + ' + open ' + money(m.openExposure) + ' + working orders ' + money(m.reservedOrderRisk) + (m.money ? ' = ' + money(m.money.weekUsed) + ' / cap ' + money(m.money.weekCap) : '') + ' | ' + (m.money ? money(m.money.monthUsed) + ' / ' + money(m.money.monthCap) : 'Unknown') + ' | ammunition ' + m.ammoUsed + '/' + m.ammoMax + ' (lost ' + m.completedLossesThisWeek + ' + reserved ' + m.reservedIdeas + ') |');
      P('| Satellite | ' + money(sb.weekUsed) + ' / ' + money(sb.weekCap) + ' (week net ' + money(sb.weeklyNet) + ') | ' + money(sb.monthUsed) + ' / ' + money(sb.monthCap) + ' | Step ' + a.satellite.step + (a.satellite.locked ? ' **LOCKED**' : '') + ' · base ' + a.satellite.baseRptPct + '% |');
      P('| Compounder | heat ' + money(c.heatMoney) + ' = ' + f2(c.heatPctWeekStart) + '% of week-start equity (' + f2(c.heatPctCurrent) + '% of current) / cap ' + c.heatCapPct + '% | — | streak ' + c.streak + '/6' + (c.locked ? ' **LOCKED**' : '') + ' · regime ' + Math.round(c.regimeFactor * 100) + '%' + (c.regimeFresh ? '' : ' (stale)') + ' |'); P('');
      P('### Satellite — rebuilt from history');
      P('- Step ' + a.satellite.step + ' · locked: ' + a.satellite.locked + ' · weekly net ' + money(a.satellite.weeklyNet) + ' · attempts this week: ' + a.satellite.attemptsThisWeek + ' · weekly reset ' + new Date(a.satellite.resetAt + 7 * 3600000).toISOString().slice(0, 16).replace('T', ' ') + ' Bangkok');
      P('- Queue (active setups): ' + (a.satellite.queue.length ? a.satellite.queue.map(function (q) { return esc(q.sym) + ' [' + q.status + ']'; }).join(', ') : 'none') + (a.satellite.queueNote ? ' — ' + a.satellite.queueNote : ''));
      P('- Stale working orders (> 1 day): ' + a.satellite.staleOrders.length); P('');
      P('### Momentum');
      P('- Losing ideas this week: **' + m.completedLossesThisWeek + '** · reserved ideas: **' + m.reservedIdeas + '** · ' + (m.reasonsIfNewOrder.length ? 'a new order today would be blocked: ' + m.reasonsIfNewOrder.join(', ') : 'a new order would not be blocked by Momentum limits'));
      P('- ' + m.note); P('');
      P('### Compounder');
      P('- Heat ' + f2(c.heatPctWeekStart) + '% · closed cycles ' + c.cyclesClosed + ' · losing streak ' + c.streak + ' · legacy-shape cards: ' + c.legacyShapeCards.length);
      c.legacyShapeCards.forEach(function (l) { P('  - **legacy shape** ' + esc(l.sym) + ' (`' + l.id + '`): ' + l.tranches + ' tranche(s)' + (l.accelerator ? ', ' + l.accelerator + ' accelerator lot(s)' : '') + ' — ' + l.why.join(', ') + ' · left as is'); });
      P('');
      P('### Open positions and working orders — old vs engine');
      if (!a.positions.length) P('_none_'); else {
        P('| Symbol | Strat | Status | Old qty | Old risk @initial stop | Engine qty | Engine risk | Difference reasons |'); P('|---|---|---|---:|---:|---:|---:|---|');
        a.positions.forEach(function (p) {
          var ev = p.engine.variants && p.engine.variants.length > 1 ? p.engine.variants.map(function (v) { return (v.qty == null ? 'Unknown' : v.qty) + ' @' + f2(v.rptPct, 3) + '%'; }).join(' / ') : (p.engine.qty == null ? 'Unknown' : p.engine.qty);
          P('| ' + esc(p.sym) + (p.legacyShape ? ' ⚑' : '') + ' | ' + p.strategy + ' | ' + p.status + ' | ' + (p.old.qtyAsEntered == null ? 'Unknown' : p.old.qtyAsEntered) + ' | ' + money(p.status === 'holding' ? p.old.riskAtInitialStop : p.old.workingOrderRisk) + ' (' + f2(p.old.riskPctOfEquityAtInitial) + '%) | ' + ev + ' | ' + (p.engine.riskMoney == null ? 'Unknown' : money(p.engine.riskMoney)) + ' | ' + esc(p.whyDifferent.join(', ') || '—') + ' |');
        });
      }
      P('');
      P('### Orders that would be blocked today');
      if (!a.wouldBeBlocked.length) P('_none_'); else a.wouldBeBlocked.forEach(function (b) { P('- ' + esc(b.sym) + ' (' + b.strategy + ', ' + b.status + '): **' + b.reasons.join(', ') + '**'); });
      P('');
      P('### Journal outcome badges under the strict sign rule');
      P('- Closed trade rows: ' + a.journalBadges.closedRows + ' · badges that change: **' + a.journalBadges.changed + '** (old rule rounds P&L to whole currency units; gross P&L, costs not recorded)');
      a.journalBadges.list.slice(0, 15).forEach(function (b) { P('  - ' + esc(b.sym) + ' ' + esc(b.date) + ': ' + b.old + ' → ' + b.strict + ' (P&L ' + f2(b.pnl, 4) + ')'); });
      P('');
      P('### Missing fields'); P('');
      if (!a.missing.length) P('_none_'); else { P('| Field | Count | Meaning | Examples |'); P('|---|---:|---|---|'); a.missing.forEach(function (e) { P('| ' + e.code + ' | ' + e.count + ' | ' + esc(e.note) + ' | ' + esc(e.ids.slice(0, 5).join(', ')) + ' |'); }); }
      if (a.excluded.length) { P(''); P('Excluded from engine sums: ' + a.excluded.map(function (x) { return esc(x.sym || x.id) + ' (' + x.why + ')'; }).join(', ')); }
      P('');
    });
    if (rp.missingGlobal.length) { P('---'); P('## Missing (global)'); rp.missingGlobal.forEach(function (e) { P('- ' + e.code + ': ' + e.count); }); }
    return L.join('\n');
  }
  function toJson(rp) { return JSON.stringify(rp, function (k, v) { return (typeof v === 'number' && !isFinite(v)) ? null : v; }, 2); }

  /* ═════════════════════════════════════════════════════════════════════════════════════════════════
     RE-C1 — LIVE layer: the same pure inputs, used by the forms (no longer a dry run). Still pure: no DOM / clock / storage.
     Per-account book settings S:  equitySnapshots[{id,at,bkkDate,equity,fx,kind,confirmed}] · cashFlows[{id,at,bkkDate,amount}]
       costSettings{winner|sat|ladder:{perSidePct,perUnit,min,flat,swapDay}} · re1:{cutoverAt (ms), unlocks:[{at,note}]}
     trade rows: fees, swap, entryFee, costOverride, stopConfirmed, stopConfirmedAt, exitReason, reentry
     ═════════════════════════════════════════════════════════════════════════════════════════════════ */
  var RP = R.POLICY;
  function asOfAt(x) { var d = x && x.bkkDate ? R.bkk.noonOf(x.bkkDate) : null; return d !== null ? d - 12 * 3600000 : (x && num(x.at) ? x.at : null); }   /* as-of date → Bangkok 00:00 of that date */
  function flowAt(f) { var a = asOfAt(f); return a === null ? null : a + 12 * 3600000; }   /* a flow dated D happens at noon of D: after a snapshot dated D, before one dated D+1 */
  /* Basis (brief §1): week/month-start equity = latest CONFIRMED snapshot at or before the period start (as-of date) · none before → the earliest confirmed one (flag).
     Provisional (first run, no snapshot): entered capital, at most 14 days after cut-over (then the engine's 14-day block applies). Withdrawals reduce the basis at once; deposits count from the next snapshot. */
  function liveBasis(S, now, proxy) {
    var snaps = (Array.isArray(S.equitySnapshots) ? S.equitySnapshots : []).filter(function (x) { return x && x.confirmed === true && pos(n(x.equity)); })
      .map(function (x) { return { id: x.id, at: asOfAt(x), equity: n(x.equity), confirmed: true, fx: n(x.fx), kind: x.kind, bkkDate: x.bkkDate }; }).filter(function (x) { return x.at !== null && x.at <= now; })
      .sort(function (a, b) { return a.at - b.at; });
    var prov = false, cut = S.re1 && num(S.re1.cutoverAt) ? S.re1.cutoverAt : now;
    if (!snaps.length && pos(proxy)) { snaps = [{ id: 'provisional', at: cut, equity: proxy, confirmed: true, provisional: true }]; prov = true; }
    var b = R.snapshotBasis(snaps, now);
    if (!b.ok) return { ok: false, state: b.state, reasons: b.reasons, flags: [], snaps: snaps, provisional: prov, ageDays: b.ageDays == null ? null : b.ageDays, snapshot: b.snapshot || null };
    var ws = R.bkk.weekStart(now), ms = R.bkk.monthStart(now);
    function pickAt(t) { var c = null; snaps.forEach(function (x) { if (x.at <= t) c = x; }); return c || snaps[0]; }
    var wk = pickAt(ws), mo = pickAt(ms), last = b.snapshot, flags = (b.flags || []).filter(function (f) { return f !== 'SNAPSHOT_OLD'; });
    var flows = Array.isArray(S.cashFlows) ? S.cashFlows.filter(function (f) { return f && num(n(f.amount)); }) : [];
    function wd(from) { var s = 0; flows.forEach(function (f) { var a = n(f.amount), at = flowAt(f); if (a < 0 && at !== null && at > from) s += -a; }); return s; }
    var wkEq = wk.equity - wd(wk.at), moEq = mo.equity - wd(mo.at), curEq = last.equity - wd(last.at);
    if (wk.at > ws) flags.push('BASIS_FIRST');
    if (prov) flags.push('PROVISIONAL');
    /* RE-D §2 — each snapshot freezes its FX: the week / month usage is converted at the rate of the snapshot that gives that basis (null = older snapshot without a rate → the current rate, labelled) */
    return { ok: true, state: prov ? 'provisional' : (last.at >= ws ? 'current' : 'carried'), ageDays: b.ageDays, snapshot: last, weekEquity: wkEq, weekAt: wk.at, monthEquity: moEq, monthAt: mo.at, currentEquity: curEq,
      weekFx: pos(wk.fx) ? wk.fx : null, monthFx: pos(mo.fx) ? mo.fx : null,
      reasons: [], flags: flags, snaps: snaps, provisional: prov, provisionalUntil: prov ? cut + RP.snapshot.blockAfterDays * DAY : null, weekSnapDate: wk.bkkDate || null, lastDate: last.bkkDate || null, confirmedThisWeek: !prov && last.at >= ws };
  }
  /* Emergency: replay every confirmed snapshot in order (evaluated AT a snapshot). Reference = month-start basis of that snapshot. */
  function liveEmergency(snaps, flows, peakState) {
    var st = null, out = { active: false, stopped: false, factor: 1, declinePct: null, refEquity: null };
    var fl = (flows || []).map(function (f) { return { at: flowAt(f), amount: n(f.amount) }; }).filter(function (f) { return f.at !== null && f.amount !== null; });
    var real = snaps.filter(function (x) { return !x.provisional; });
    real.forEach(function (sn, i, arr) {
      var upto = arr.slice(0, i + 1), ms = R.bkk.monthStart(sn.at), ref = null; upto.forEach(function (x) { if (x.at <= ms) ref = x; }); if (!ref) ref = upto[0];
      var e = R.emergencyStep(st, sn, { equity: ref.equity, at: ref.at }, fl);
      st = { active: e.active, refEquity: e.refEquity, refStartMs: e.refStartMs };
      out = { active: e.active, stopped: false, factor: e.factor, declinePct: e.declinePct, refEquity: e.refEquity, refStartMs: e.refStartMs, evaluatedAt: sn.at };
    });
    /* AU2 — DD_STOP is measured from the confirmed-equity PEAK, not the month start */
    var d = R.ddStopStep(peakState || null, real, fl);
    out.stopped = d.stopped === true; out.ddPct = d.ddPct; out.peakP = d.peakP; out.peakAt = d.peakAt; out.peakEquity = d.peakEquity;
    return out;
  }
  /* RE-C2 §6 — Costs switch: OFF (default) = the whole cost feature is dormant: costs count as 0 (known, all zero) → net = gross, net-breakeven = entry, never Unknown. ONE flag, read here (src.costsOn === true = ON = RE-C1 behaviour). */
  var NO_COSTS = { known: true, perSidePct: 0, perUnit: 0, min: 0, flat: 0, swapDay: 0, source: 'off' };
  function unitCosts(S, acct, strategy, override, on) {
    if (on !== true) return { known: true, perSidePct: 0, perUnit: 0, min: 0, flat: 0, swapDay: 0, source: 'off' };
    var key = strategy === 'winner' ? 'winner' : strategy === 'ladder' ? 'ladder' : 'sat', cs = S.costSettings && typeof S.costSettings === 'object' ? S.costSettings : {};
    var one = {}; one[acct] = cs;
    var c = R.resolveCosts(one, acct, key, override || null);
    if (c.known && !override && cs[key] && num(cs[key].swapDay)) c.swapDay = cs[key].swapDay;
    if (c.known && override && num(override.swapDay)) c.swapDay = override.swapDay;
    return c;
  }
  /* The whole live state of ONE account (accounts never mix: only this account's book, trades, cards and ideas are read). */
  function live(src, acctId) {
    var now = src.now, acc = ((src.accounts || []).filter(function (a) { return a.id === acctId; })[0]) || { id: acctId }, miss = new Missing();
    var A = buildAccount(src, acc, miss), S = A.S || {}, ideas = A.ideas, fx = A.fx;
    var cap = S.capital || {}, pc = src.portCur || { core: 'THB', satB: 'USD' }, ports = acc.ports || ['core', 'satB'];
    var coreV = ports.indexOf('core') >= 0 && n(cap.core) !== null ? n(cap.core) * (pc.core === 'USD' ? (fx || 0) : 1) : 0, satV = ports.indexOf('satB') >= 0 && n(cap.satB) !== null ? n(cap.satB) * (pc.satB === 'USD' ? (fx || 0) : 1) : 0;
    var basis = liveBasis(S, now, coreV + satV), flows = Array.isArray(S.cashFlows) ? S.cashFlows : [];
    var emergency = liveEmergency(basis.snaps || [], flows, S.re1 && S.re1.peak), eF = emergency.factor;
    var rowsById = {}; ((src.books && src.books[acctId] && src.books[acctId].trades) || []).forEach(function (t) { if (t) rowsById[t.id] = t; });
    var rowsOf = function (idea) { return (idea.rowIds || []).map(function (id) { return rowsById[id]; }).filter(Boolean); };
    var costOverrideOf = function (idea) { var o = null; rowsOf(idea).forEach(function (t) { if (t.costOverride && typeof t.costOverride === 'object') o = t.costOverride; }); return o; };
    var costsOn = src.costsOn === true, costsFor = function (idea) { return unitCosts(S, acctId, idea.strategy, costOverrideOf(idea), costsOn); };
    var offRow = function (idea) { return !costsOn || rowsOf(idea).some(function (t) { return t.costsOff === true; }); };   /* a trade closed while OFF is never re-costed when ON later */
    ideas.forEach(function (i) {
      if (!i.tranches.length) return;
      var c = costsFor(i), fees = 0, anyRec = false, swap = 0, zero = offRow(i);
      rowsOf(i).forEach(function (t) { if (!zero && t.status !== 'plan' && num(n(t.entryFee))) { fees += n(t.entryFee); anyRec = true; } });
      if (zero) anyRec = true;
      if (!anyRec && c.known) i.tranches.forEach(function (t) { fees += R.exitCost(c, t.qty, t.entry, t.mult, t.fx) || 0; });
      if (!zero && c.known && num(c.swapDay) && c.swapDay > 0 && i.strategy === 'sat') i.tranches.forEach(function (t) { var o = isoMs(t.openedAt) !== null ? isoMs(t.openedAt) : R.bkk.noonOf(t.openedAt); if (o !== null && now > o) { var d = Math.floor((now - o) / DAY); swap += d * c.swapDay * t.qty * (t.fx > 0 ? t.fx : 1); } });
      i.entryFees = fees + swap;
      (i.exits || []).forEach(function (e) {
        var t = rowsById[String(e.id).replace(/^x:/, '')]; if (!t) return;
        if (zero || t.costsOff === true) { e.fees = 0; e.swap = 0; return; }
        e.fees = num(n(t.fees)) ? n(t.fees) : (c.known ? (R.exitCost(c, e.qty, e.price, i.tranches[0].mult, i.tranches[0].fx) || 0) : 0); e.swap = num(n(t.swap)) ? n(t.swap) : 0;
      });
      i.reentry = rowsOf(i).some(function (t) { return t.reentry === true; });
      i.tranches.forEach(function (t) { t.stopConfirmed = rowsOf(i).some(function (r) { return r.status === 'open' && r.stopConfirmed === true && n(r.entry) === t.entry && Math.abs(n(r.sl) - t.stop) < 1e-9; }); });
    });
    var ff = src.ff || {};
    var regime = R.regimeFromFundflow(ff.demo ? null : ff, now), signals = regime.signals;   /* RM1: same shared reader as build() and every view */
    var momState = basis.ok ? R.momentumState({ now: now, account: acctId, ideas: ideas, costsFor: costsFor }) : null;
    var satI = ideas.filter(function (i) { return i.strategy === 'sat'; });
    var attempts = satI.filter(function (i) { return i.status === 'closed' && num(i.closedAt) && i.closedAt > 0; }).map(function (i) { return { id: i.id, closeAt: i.closedAt, net: R.ideaRealizedNet(i) }; });
    var step = R.satStepState(attempts, now);
    var dayAtt = satI.filter(function (i) { return i.tranches.length || i.status === 'ordered'; }).map(function (i) {
      var t0 = i.tranches[0], start = t0 ? (isoMs(t0.openedAt) !== null ? isoMs(t0.openedAt) : R.bkk.noonOf(t0.openedAt)) : null; if (start == null && i.workingOrders[0]) start = i.workingOrders[0].at || null;
      var ex = i.exits[i.exits.length - 1] || null;
      return { id: i.id, product: i.product, startAt: start, status: i.status === 'closed' ? 'closed' : i.status === 'ordered' ? 'working' : 'open', net: i.status === 'closed' ? R.ideaRealizedNet(i) : null, exitReason: ex && ex.reason || null, reentry: !!i.reentry, closeAt: i.closedAt || null, side: i.side, entry: t0 ? t0.entry : null };
    }).filter(function (a) { return num(a.startAt); });
    var comp = ideas.filter(function (i) { return i.strategy === 'ladder'; });
    var cycles = comp.filter(function (i) { return i.status === 'closed' && num(i.closedAt) && i.closedAt > 0; }).map(function (i) { return { id: i.id, flatAt: i.closedAt, net: R.ideaRealizedNet(i) }; });
    var unlocks = (S.re1 && Array.isArray(S.re1.unlocks) ? S.re1.unlocks : []).filter(function (u) { return u && num(u.at); });
    var streak = R.compStreak(cycles, unlocks);
    var ideasW = basis.ok ? fxIdeas(ideas, fx, basis.weekFx) : ideas;
    var heat = basis.ok ? R.compHeat(ideasW, acctId, costsFor, basis.weekEquity, basis.currentEquity) : null;   /* TS1 — week-snapshot FX */
    var ideasM = basis.ok ? fxIdeas(ideas, fx, basis.monthFx) : ideas, Lx = { now: now, acct: acctId, basis: basis, costsFor: costsFor, ideasW: ideasW, ideasM: ideasM };
    var satBud = basis.ok ? satBudL(Lx, 0) : null;
    var momChk = basis.ok ? momCheckL(Lx, { ideaId: '__none__', isAddition: true, riskMoney: 0 }) : null;
    var active = basis.ok ? R.activeSummary({ basis: basis, mom: { usageWeek: momChk.usageWeek, usageMonth: momChk.usageMonth }, sat: { usageWeek: satBud.usageWeek, usageMonth: satBud.usageMonth }, candidateRisk: 0 }) : null;
    return { acct: acctId, costsOn: costsOn, name: acc.name || acctId, now: now, fx: fx, S: S, ideas: ideas, info: A.info, basis: basis, emergency: emergency, eF: eF, costsFor: costsFor, regime: regime, signals: signals,
      mom: { state: momState, chk: momChk }, sat: { step: step, attempts: attempts, dayAtt: dayAtt, budget: satBud, stale: R.satStaleOrders(ideas, now) }, comp: { streak: streak, cycles: cycles, unlocks: unlocks, heat: heat }, active: active, rowsById: rowsById, ideasW: ideasW, ideasM: ideasM };
  }
  /* ── reason text (engine text + the concrete numbers) ── */
  /* HF5 — the Sat queue names the OPEN setup (not the candidate): queue = {kind:'max'|'busy', open:[{id, satId, sym, cut, working}], blocker:{...}} */
  function queueInfo(L, q) {
    if (!q.reasons.length) return null;
    var rows = (q.open || []).map(function (o) { var inf = L.info[o.id] || {}; return { id: o.id, satId: inf.satIdea || null, sym: String(inf.sym || o.id).replace(/USDT$|USD$/, '') || inf.sym, cut: o.cut, working: o.working }; });
    if (q.reasons[0] === 'SAT_QUEUE_MAX') return { kind: 'max', max: q.max, open: rows };
    var ids = q.busyWith || [], bl = rows.filter(function (r) { return ids.indexOf(r.id) >= 0; }).sort(function (a, b) { return a.cut - b.cut; })[0];
    return { kind: 'busy', open: rows, blocker: bl, need: q.need };
  }
  function queueText(code, q) {
    if (q.kind === 'max') return q.open.length + ' Sat setups open (' + q.open.map(function (r) { return r.sym; }).join(', ') + ') · max ' + q.max;
    var b = q.blocker, now = Math.round(b.cut * 100), need = Math.round(q.need * 100);
    if (b.working) return b.sym + ' order is working with full risk · fill it and cut its risk ≥ ' + need + '% (or cancel it) to open another Sat';
    return b.sym + ' is open with ' + (now === 0 ? 'full risk' : (100 - now) + '% of its risk left') + ' · move its stop to cut risk ≥ ' + need + '% (now ' + now + '%) to open another Sat';
  }
  function rtext(code, d) {
    var T = R.REASONS[code] ? R.REASONS[code].text : code; d = d || {};
    if ((code === 'MONEY_WEEK') && d.roomPct != null) return T + ' — room ' + f2(d.roomPct, 2) + '%';
    if ((code === 'SAT_QUEUE_BUSY' || code === 'SAT_QUEUE_MAX') && d.queue) return queueText(code, d.queue);
    if (code === 'COMP_HEAT' && d.heat && d.heat.pct != null) return 'Heat cap: ' + f2(d.heat.pct, 1) + '% of 6% — room ' + f2(Math.max(0, 6 - d.heat.pct), 1) + '%';
    return T;
  }
  function f2(x, d) { d = d == null ? 2 : d; var v = Math.round(x * Math.pow(10, d)) / Math.pow(10, d); return String(v); }
  function pctTxt(x) { return f2(x, 3) + '%'; }
  function ideaOthers(L, ideaId) { return L.ideas.filter(function (i) { return i.id !== ideaId; }); }
  /* largest qty (lot multiple) whose risk fits the room, never above the sized qty */
  function allowedQty(room, perUnit, lotStep, minLot, maxQty) { if (!(room > 0) || !(perUnit > 0)) return 0; var q = R.floorLot(Math.min(maxQty, room / perUnit), lotStep); return q >= (minLot || 0) - 1e-12 && q > 0 ? q : 0; }
  /* RE-D §2 — ideas re-priced at a snapshot's FX (USD tranches / working orders only). Used for the week / month USAGE; the candidate order stays at the current rate. */
  function fxIdeas(ideas, cur, to) {
    if (!pos(to) || !pos(cur) || Math.abs(to - cur) < 1e-12) return ideas;
    return ideas.map(function (i) { var c = Object.assign({}, i); c.tranches = (i.tranches || []).map(function (t) { return t.fx === cur ? Object.assign({}, t, { fx: to }) : t; }); c.workingOrders = (i.workingOrders || []).map(function (w) { return w.fx === cur ? Object.assign({}, w, { fx: to }) : w; }); return c; });
  }
  function otherIds(ideas, id) { return ideas.filter(function (i) { return i.id !== id; }); }
  function mergeDual(w, m, kind) {   /* week fields from the week-basis run, month fields from the month-basis run */
    if (w === m) return w;
    var o = Object.assign({}, w), r = w.reasons.filter(function (c) { return c !== 'MONEY_MONTH'; });
    if (m.reasons.indexOf('MONEY_MONTH') >= 0) { var at = Math.max(r.indexOf('MONEY_WEEK'), r.indexOf('UNKNOWN_DATA')); r.splice(at + 1, 0, 'MONEY_MONTH'); }
    o.reasons = r; o.allowed = r.length === 0;
    if (kind === 'mom') { o.money = Object.assign({}, w.money, { monthUsed: m.money.monthUsed, monthCap: m.money.monthCap }); o.usageMonth = m.usageMonth; }
    else { o.monthUsed = m.monthUsed; o.monthCap = m.monthCap; o.monthlyNet = m.monthlyNet; o.usageMonth = m.usageMonth; }
    return o;
  }
  /* Momentum / Satellite budget check with week usage at the week-snapshot FX and month usage at the month-snapshot FX (identical to a single run when both equal the current rate) */
  function momCheckL(L, cand, exceptId) {
    var f = function (ideas) { return R.momentumCheck({ now: L.now, account: L.acct, basis: L.basis, ideas: exceptId === undefined ? ideas : otherIds(ideas, exceptId), costsFor: L.costsFor, candidate: cand }); };
    return mergeDual(f(L.ideasW), f(L.ideasM), 'mom');
  }
  function satBudL(L, candRisk, exceptId) {
    var f = function (ideas) { return R.satBudgetCheck({ basis: L.basis, now: L.now, account: L.acct, ideas: exceptId === undefined ? ideas : otherIds(ideas, exceptId), costsFor: L.costsFor, candidateRisk: candRisk }); };
    return mergeDual(f(L.ideasW), f(L.ideasM), 'sat');
  }
  function baseModel(L, strat) { return { ddStop: !!(L.emergency && L.emergency.stopped), strategy: strat, acct: L.acct, ok: false, blocked: true, reasons: [], reasonTexts: [], flags: [], formula: '', effPct: null, qty: 0, money: null, roomLine: '', allowedQty: 0, chip: null, factors: [] }; }
  /* PC2 §1 — total-risk blocks say the real rule with numbers: "Risk 0.36% is over the limit for this plan 0.24% (0.40% × homework 100% × risk-off 60%)" */
  function numTexts(m) {
    if (!m.fit || !m.budget) return m;
    m.reasons.forEach(function (c, i) { if (c === 'PLAN_TOTAL_RISK' || c === 'ADDON_TOTAL_RISK') m.reasonTexts[i] = (c === 'ADDON_TOTAL_RISK' ? 'Risk ' + f2(m.fit.totalPct, 2) + '% is over the ' + f2(m.fit.capPct, 2) + '% limit for this stock (all lots at their current stop)' : 'Risk ' + f2(m.fit.totalPct, 2) + '% is over the limit for this plan ' + f2(m.fit.capPct, 2) + '% (' + m.budget.text + ')'); });
    return m;
  }
  function finish(m, d) {
    if (m.ddStop && m.reasons.indexOf('DD_STOP') < 0) m.reasons.unshift('DD_STOP'); if (m.ddStop) m.allowedQty = 0;
    var seen = {}; m.reasons = m.reasons.filter(function (c) { if (seen[c]) return false; seen[c] = 1; return true; });
    m.reasonTexts = m.reasons.map(function (c) { return rtext(c, d); }); m.blocked = m.reasons.length > 0; m.ok = !m.blocked && m.qty > 0; return m;
  }
  function sizeCommon(L, f, rptPct, factor, fraction) {
    var o = { equity: L.basis.weekEquity, rptPct: rptPct, factor: factor, fraction: fraction, stop: f.stop, side: f.side, minStopDist: f.minStopDist, mult: f.mult, fx: f.fx, lotStep: f.lotStep, minLot: f.minLot };
    if (f.levels && f.levels.length > 1) {   /* several entry levels inside ONE attempt: one shared effective RPT, user split (answers-A #5) */
      var z = R.sizeAttempt(Object.assign(o, { levels: f.levels })), q = 0, w = 0;
      z.levels.forEach(function (l) { q += l.qty || 0; w += (l.qty || 0) * l.price; });
      z.avgEntry = q > 0 ? w / q : f.entry; z.actualDistance = Math.abs(z.avgEntry - f.stop); z.sizingDistance = z.actualDistance;
      var below = z.levels.some(function (l) { return l.reasons.indexOf('LOT_BELOW_MIN') >= 0; });
      if (below && z.reasons.indexOf('LOT_BELOW_MIN') < 0) z.reasons = z.reasons.concat(['LOT_BELOW_MIN']);
      return z;
    }
    return R.sizeOrder(Object.assign(o, { entry: f.entry }));
  }
  /* ── Momentum (new order · addition · edit) ──
     f = {entry, stop, side, homeworkDone, starterOn, isFirstEntry, usedFraction, ideaId, isAddition, mult, fx, lotStep, minLot, minStopDist} */
  function sizeMomentum(L, f) {
    var m = baseModel(L, 'winner'); m.chip = L.emergency.active ? { t: 'Emergency 50%', c: 'r' } : null;   /* the 'Homework not done' state is shown once, by the WL1 cap box under the result */
    if (!L.basis.ok) { m.reasons = L.basis.reasons.slice(); return finish(m); }
    var fr = R.entryFraction({ homeworkDone: f.homeworkDone === true || f.topUp === true, starterOn: f.starterOn === true, isFirstEntry: f.isFirstEntry !== false, usedFraction: f.usedFraction || 0 });   /* PC2 2f: a top-up is sized against the FULL budget */
    var base = RP.mom.rptPct, rg = L.regime, ef = R.compFactor(rg, L.eF), emOnly = L.eF < rg.factor, z = sizeCommon(L, f, base, ef, fr.fraction); m.sizing = z; if (z.levels) m.levels = z.levels; m.factors = ['BASE_' + base];   /* RM1: effective modifier = min(regime, emergency), applied once to the base budget */
    var parts = [f2(base, 2) + '%'], eff = base * ef * fr.fraction;
    if (f.homeworkDone !== true) { var hwp = Math.round(RP.hwFactor.mom * 100); parts.push('homework ' + hwp + '%'); m.factors.push('HOMEWORK_' + hwp); }
    if (f.starterOn === true && f.isFirstEntry !== false) { parts.push('starter 25%'); m.factors.push('STARTER_25'); }
    if (ef < 1) { var mpc = Math.round(ef * 100); parts.push((emOnly ? 'emergency ' : 'regime ') + mpc + '%'); m.factors.push((emOnly ? 'EMERGENCY_' : 'REGIME_') + mpc); m.limit = { code: emOnly ? 'emergency' : 'regime', text: 'limited by ' + (emOnly ? 'emergency brake ' : 'regime ') + mpc + '%' }; }
    m.regime = { factor: ef, base: rg.factor, emergency: L.eF, fallback: rg.fallback, equity: rg.equity, credit: rg.credit };
    m.effPct = eff; m.formula = parts.join(' × ') + ' = ';
    if (z.reasons.length) { m.reasons = z.reasons.slice(); return finish(m); }
    m.qty = z.qty; m.money = z.actualRisk; m.moneyPct = z.actualRiskPct; m.sizingDistance = z.sizingDistance; m.minStopApplied = z.minStopApplied; m.avgEntry = z.avgEntry || f.entry;
    /* PC2 §1 / 2e / 2f — rows that follow a fill. planned = in the plan before the first fill (first build) · topUp = Momentum 70 % → full within 5 days (first build) · isAddition = add-on (homework + total-risk rule). */
    var extra = [], meM = L.ideas.filter(function (i) { return i.id === f.ideaId; })[0] || null, heldQ = meM ? totQty(meM) : 0, uvM = (f.mult > 0 ? f.mult : 1) * (f.fx > 0 ? f.fx : 1);
    m.fit = null;
    if (heldQ > 0 && (f.isAddition === true || f.planned === true || f.topUp === true) && z.actualDistance > 0) {
      var prM = R.ideaResult(meM, L.costsFor(meM)), existM = prM.exposure === null ? prM.principalRisk : prM.exposure, eqM = L.basis.weekEquity;
      var budPct = base * ef * (f.topUp === true || f.homeworkDone === true ? 1 : RP.hwFactor.mom), budMoney = eqM * budPct / 100, newRisk = z.actualRisk || 0;
      if (f.isAddition === true && f.topUp !== true && f.homeworkDone !== true) extra.push('ADDON_THESIS');
      var roomQ = R.floorLot(Math.max(0, budMoney - existM) / (z.actualDistance * uvM), f.lotStep);
      if (roomQ < (z.qty || 0)) {
        if (roomQ >= (f.minLot || 0) - 1e-12 && roomQ > 0) { var rk = roomQ * z.actualDistance * uvM; z = Object.assign({}, z, { qty: roomQ, actualRisk: rk, actualRiskPct: rk / eqM * 100 }); m.sizing = z; m.qty = roomQ; m.money = rk; m.moneyPct = z.actualRiskPct; newRisk = rk; }
        else extra.push(f.isAddition === true && f.topUp !== true ? 'ADDON_TOTAL_RISK' : 'PLAN_TOTAL_RISK');
        m.limit = { code: 'total_risk', text: 'limited by total risk ' + f2(budPct, 2) + '%' };
      }
      m.fit = { totalPct: (existM + newRisk) / eqM * 100, capPct: budPct, usedPct: existM / eqM * 100, held: heldQ, existing: existM, budgetMoney: budMoney, newRisk: newRisk, avg: ideaAvg(meM), uv: uvM };
      var regL = rg.fallback ? 'fallback ' + Math.round(ef * 100) + '%' : (ef < 1 ? (emOnly ? 'emergency ' : 'risk-off ') + Math.round(ef * 100) + '%' : 'risk-on 100%'), hwM = f.topUp === true || f.homeworkDone === true ? 1 : RP.hwFactor.mom;
      m.budget = { planPct: base, hw: hwM, reg: ef, regLabel: regL, capPct: budPct, text: f2(base, 2) + '% × homework ' + Math.round(hwM * 100) + '% × ' + regL };
    }
    var chk = momCheckL(L, { ideaId: f.ideaId || '__new__', isAddition: f.isAddition === true, riskMoney: z.actualRisk }, f.ideaId);
    m.reasons = extra.concat(chk.reasons.filter(function (c) { return extra.indexOf(c) < 0; })); m.flags = chk.flags.slice();
    var Mo = chk.money, uv = f.mult * f.fx, wRoom = Mo.weekCap - (Mo.weekUsed - z.actualRisk), mRoom = Mo.monthCap - (Mo.monthUsed - z.actualRisk), room = Math.min(wRoom, mRoom);
    m.room = { weekPct: Math.max(0, wRoom) / L.basis.weekEquity * 100, monthPct: Math.max(0, mRoom) / L.basis.monthEquity * 100, ideasUsed: chk.ammo.total, ideasMax: chk.ammo.max, completedLosses: chk.ammo.completedLosses }; m.roomPct = m.room.weekPct;
    var held = chk.ammo.completedLosses + chk.ammo.reserved, needPct = z.actualRisk / L.basis.weekEquity * 100;
    if (m.reasons.indexOf('AMMO_EXHAUSTED') >= 0) m.roomLine = 'Ideas ' + Math.min(held, chk.ammo.max) + ' of ' + chk.ammo.max + ' used or reserved · week room ' + pctTxt(m.room.weekPct);   /* blocked: say what is used, never a count above the limit */
    else if (m.reasons.indexOf('MONEY_WEEK') >= 0 || m.reasons.indexOf('MONEY_MONTH') >= 0) m.roomLine = 'Week room ' + pctTxt(m.room.weekPct) + ' · this order needs ' + pctTxt(needPct) + ' · ideas ' + Math.min(held, chk.ammo.max) + ' of ' + chk.ammo.max + ' used or reserved';
    else m.roomLine = 'Week room ' + pctTxt(m.room.weekPct) + ' · idea ' + chk.ammo.total + ' of ' + chk.ammo.max + (f.homeworkDone === true ? '' : ' · full size after homework');
    m.allowedQty = m.reasons.indexOf('AMMO_EXHAUSTED') >= 0 || m.reasons.indexOf('ADDON_THESIS') >= 0 ? 0 : allowedQty(room, z.actualDistance * uv, f.lotStep, f.minLot, m.qty);
    if (m.fit && m.reasons.some(function (c) { return c === 'ADDON_TOTAL_RISK' || c === 'PLAN_TOTAL_RISK'; })) m.allowedQty = 0;
    return numTexts(finish(m, { roomPct: m.room.weekPct }));
  }
  /* ── Satellite ──
     f = {entry, stop, tp, side, cond:{ema50,structure,mss}, product, ideaId, reentry:{…}, mult, fx, lotStep, minLot, minStopDist, levels?:[{price,splitPct}]} */
  function sizeSat(L, f) {
    var m = baseModel(L, 'sat'), cond = R.satCondition(f.cond || {}), st = L.sat.step;
    m.chip = cond.status === 'full' ? { t: 'Full', c: 'g' } : cond.status === 'reduced' ? { t: 'Reduced 65%', c: 'a' } : cond.status === 'blocked' ? { t: 'Blocked', c: 'r' } : { t: 'Choose Trend', c: 'f' };
    m.condition = cond; m.step = st.step; m.reentry = false;
    if (!L.basis.ok) { m.reasons = L.basis.reasons.slice(); return finish(m); }
    var rs = cond.reasons.slice(), ord = R.satEntryOrder({ side: f.side, entry: f.entry, stop: f.stop, tp: f.tp });
    rs = rs.concat(ord.reasons); m.rr = ord.rr == null ? null : ord.rr;
    if (st.locked) rs.push('SAT_LOCKED');
    var q0 = R.satQueueCheck(L.ideas, L.acct, f.ideaId); rs = rs.concat(q0.reasons); m.queue = queueInfo(L, q0);
    var others = L.sat.dayAtt.filter(function (a) { return a.id !== f.ideaId; }), dc = R.satDailyCheck({ now: L.now, product: f.product, attempts: others, reentry: f.reentry || {} });
    rs = rs.concat(dc.reasons); m.flags = m.flags.concat(dc.flags, cond.flags); m.reentry = dc.reentry === true; m.reentryNeedsConfirm = dc.reasons.indexOf('SAT_REENTRY_COND') >= 0;
    var todayN = others.filter(function (a) { return a.product === f.product && R.bkk.dayKey(a.startAt) === R.bkk.dayKey(L.now) && a.status !== 'cancelled'; }).length;
    var cf = cond.factor == null ? 0 : cond.factor, base = RP.sat.stepRpt[st.stepIndex], ef = L.eF;
    /* EF1 — news window: size cut = min(condition factor, news factor), never multiplied */
    var nf = (f.newsPct > 0 && f.newsPct < 100) ? f.newsPct / 100 : null, newsCut = false;
    if (nf != null && cf > 0 && nf < cf) { cf = nf; newsCut = true; } else if (nf != null && cf > 0 && nf === cf) { newsCut = true; }
    m.newsCut = newsCut; if (newsCut) m.chip = { t: 'News ' + Math.round(cf * 100) + '%', c: 'a' };
    m.factors = ['STEP_' + st.step]; var parts = [f2(base, 2) + '%'];
    if (newsCut) { parts.push('news ' + Math.round(cf * 100) + '%'); m.factors.push('NEWS_' + Math.round(cf * 100)); }
    else if (cond.status === 'reduced') { parts.push('65%'); m.factors.push('CONDITION_65'); }
    if (ef < 1) { parts.push('emergency 50%'); m.factors.push('EMERGENCY_50'); }
    m.effPct = cond.factor == null ? null : base * cf * ef; m.formula = parts.join(' × ') + ' = ';
    var z = { reasons: [], qty: 0, actualRisk: 0, actualDistance: 0 };
    if (cf > 0) {
      z = sizeCommon(L, f, base, cf * ef, 1); if (z.levels) m.levels = z.levels;
      if (z.reasons.length) rs = rs.concat(z.reasons);
    }
    m.sizing = z; m.qty = z.qty || 0; m.money = z.actualRisk || 0; m.moneyPct = z.actualRiskPct != null ? z.actualRiskPct : (m.money / L.basis.weekEquity * 100);
    var bud = satBudL(L, m.money || 0, f.ideaId);
    rs = rs.concat(bud.reasons); m.flags = m.flags.concat(bud.flags);
    var act = R.activeSummary({ basis: L.basis, mom: { usageWeek: L.mom.chk.usageWeek, usageMonth: L.mom.chk.usageMonth }, sat: { usageWeek: bud.usageWeek, usageMonth: bud.usageMonth }, candidateRisk: m.money || 0 });
    rs = rs.concat(act.reasons); m.reasons = rs;
    var wRoom = bud.weekCap - (bud.weekUsed - m.money), room = Math.min(wRoom, bud.monthCap - (bud.monthUsed - m.money));
    m.room = { weekPct: Math.max(0, wRoom) / L.basis.weekEquity * 100 }; m.roomPct = m.room.weekPct;
    var uv = f.mult * f.fx; m.allowedQty = (z.actualDistance > 0 && uv > 0 && m.qty > 0) ? allowedQty(room, z.actualDistance * uv, f.lotStep, f.minLot, m.qty) : 0;
    var q = q0;
    m.roomLine = (m.rr != null ? 'R:R ' + f2(m.rr, 1) + ' · ' : '') + (q.reasons.length ? 'queue busy' : 'queue free') + ' · ' + (m.reentry ? 're-entry' : todayN === 0 ? '1st setup today' : 'setup ' + (todayN + 1) + ' today') + ' · week room ' + pctTxt(m.room.weekPct);
    return finish(m, { roomPct: m.room.weekPct, queue: m.queue });
  }
  /* ── Compounder ──
     f = {kind:'pilot'|'topup'|'addon', ideaId (existing idea of this ticker), thesisDone, starterOn, entry, stop, side, mult, fx, lotStep, minLot, minStopDist, legacy, levels?}
     Add-on / further buys = TOTAL-RISK rule (answers-A #16 amended): thesis + (existing tranches at current stop + working orders + new order) <= 1.00 % (0.50 % without thesis)
     of week-start equity + new order alone <= 0.50 % x min(Regime, Emergency). Entry above OR below the average entry (below = warning only). */
  function sizeComp(L, f) {
    var m = baseModel(L, 'ladder'), kind = f.kind || 'pilot'; m.kind = kind;
    m.chip = null;   /* RM1: the modifier is shown once, in the size line ("limited by regime 50%") and the Flow line — no second chip */
    if (!L.basis.ok) { m.reasons = L.basis.reasons.slice(); return finish(m); }
    var me = L.ideas.filter(function (i) { return i.id === f.ideaId; })[0] || null, rg = L.regime, fac = R.compFactor(rg, L.eF), thesis = f.thesisDone === true, emOnly = L.eF < rg.factor;
    /* PC2 — new path (f.riskPct given): 'plan' = first build (rows in the plan before the first fill; no thesis) · 'addon' = rows added after it (thesis + total-risk rule). Budget = the plan's risk % (default Settings Compounder total) x homework factor (Compounder 100 %) x regime. */
    var np = f.riskPct > 0, planPct = np ? f.riskPct : RP.comp.totalCapPct, isPlan = kind === 'plan';
    var multi = !!(f.levels && f.levels.length > 1), planCap = (thesis || isPlan) ? planPct : RP.comp.pilotPct;   /* RM1: whole-plan budget = Settings total (RK1 default 1.00 %) with thesis */
    var base = multi ? planCap : (isPlan || (np && kind === 'addon') ? planPct : (kind === 'pilot' ? RP.comp.pilotPct : RP.comp.addonPct));
    var fraction = (kind === 'pilot' && f.starterOn === true && !multi) ? RP.comp.starter * 2 : (isPlan && f.starterOn === true && !multi ? RP.comp.starter : 1);
    var label = multi || isPlan ? 'Plan ' : kind === 'pilot' ? 'Pilot ' : 'Add-on ';
    m.factors = [(multi || isPlan ? 'PLAN_' : kind === 'pilot' ? 'PILOT_' : 'ADDON_') + base]; var parts = [label + f2(base, 2) + '%'];
    var hwC = RP.hwFactor.comp; if (isPlan && hwC < 1) { parts.push('homework ' + Math.round(hwC * 100) + '%'); }
    var regLimit = null;
    if (fac < 1) { var pc = Math.round(fac * 100); parts.push((emOnly ? 'emergency ' : 'regime ') + pc + '%'); m.factors.push((emOnly ? 'EMERGENCY_' : 'REGIME_') + pc); regLimit = { code: emOnly ? 'emergency' : 'regime', text: 'limited by ' + (emOnly ? 'emergency brake ' : 'regime ') + pc + '%' }; }
    if (fraction < 1) { parts.push('starter 25%'); m.factors.push('STARTER_25'); }
    m.regime = { factor: fac, base: rg.factor, emergency: L.eF, fallback: rg.fallback, equity: rg.equity, credit: rg.credit };
    m.effPct = base * fac * fraction; m.formula = parts.join(' × ') + ' = ';
    var z = sizeCommon(L, f, base, fac, fraction); m.sizing = z; if (z.levels) m.levels = z.levels;
    if (z.reasons.length) { m.reasons = z.reasons.slice(); return finish(m); }
    var eq = L.basis.weekEquity, existing = 0, working = 0, avg = null, heldValue = 0, uvv = (f.mult > 0 ? f.mult : 1) * (f.fx > 0 ? f.fx : 1);
    if (me) {
      var pr = R.ideaResult(me, L.costsFor(me)); existing = pr.exposure === null ? pr.principalRisk : pr.exposure; avg = ideaAvg(me);
      (me.tranches || []).forEach(function (t) { if (pos(t.qty) && pos(t.entry)) heldValue += t.qty * t.entry * (t.mult > 0 ? t.mult : 1) * (t.fx > 0 ? t.fx : 1); });
      (me.workingOrders || []).forEach(function (w) { if (pos(w.qty) && pos(w.entry) && pos(w.stop)) { working += w.qty * Math.abs(w.entry - w.stop) * (w.mult > 0 ? w.mult : 1) * (w.fx > 0 ? w.fx : 1); heldValue += w.qty * w.entry * (w.mult > 0 ? w.mult : 1) * (w.fx > 0 ? w.fx : 1); } });
    }
    /* RM1 — final qty = the smallest of: risk qty (budget x modifier) · total-risk room qty · value-cap room qty. Always from the base budget (never a reduced number again). */
    var riskQty = z.qty, avgPx = z.avgEntry || f.entry, dist = z.actualDistance, lotStep = f.lotStep, usedMoney = existing + working;
    var capTotalPct = (kind === 'pilot' && !multi) ? (f.starterOn === true ? RP.comp.pilotPct * RP.comp.starter * 2 : RP.comp.pilotPct) : (thesis ? planPct * fac : RP.comp.pilotPct);
    if (multi) capTotalPct = thesis ? planPct * fac : RP.comp.pilotPct * fac;
    if (isPlan) capTotalPct = planPct * hwC * fac * (f.starterOn === true ? RP.comp.starter : 1);
    if (np && kind === 'addon') capTotalPct = thesis ? planPct * fac : RP.comp.pilotPct;
    var totalRoomMoney = eq * capTotalPct / 100 - usedMoney, valueCapPct = pos(f.valueCapPct) ? f.valueCapPct : RP.comp.valueCapPct, valueRoomMoney = eq * valueCapPct / 100 - heldValue;
    var totalQty = (dist > 0 && uvv > 0) ? R.floorLot(Math.max(0, totalRoomMoney) / (dist * uvv), lotStep) : 0, valueQty = (avgPx > 0 && uvv > 0) ? R.floorLot(Math.max(0, valueRoomMoney) / (avgPx * uvv), lotStep) : 0;
    var finalQty = Math.min(riskQty, totalQty, valueQty), minLot = f.minLot || 0, limit = regLimit, valueBlocked = false;
    if (finalQty < riskQty) {
      var byValue = valueQty < totalQty;
      limit = byValue ? { code: 'value_cap', text: 'limited by ' + f2(valueCapPct, 1) + '% value cap' } : { code: 'total_risk', text: 'limited by total risk ' + f2(capTotalPct, 2) + '%' };
      if (finalQty >= minLot - 1e-12 && finalQty > 0) {
        var k = finalQty / riskQty;
        if (z.levels && z.levels.length > 1) {
          var lv = z.levels.map(function (l) { var q = R.floorLot((l.qty || 0) * k, lotStep); return Object.assign({}, l, { qty: q, actualRisk: q * Math.abs(l.price - f.stop) * uvv }); });
          var risk = 0, qt = 0; lv.forEach(function (l) { risk += l.actualRisk; qt += l.qty; });
          z = Object.assign({}, z, { levels: lv, qty: qt, actualRisk: risk, actualRiskPct: risk / eq * 100 }); m.levels = lv;
        } else { var rk = finalQty * z.actualDistance * uvv; z = Object.assign({}, z, { qty: finalQty, actualRisk: rk, actualRiskPct: rk / eq * 100 }); }
        m.sizing = z;
      } else if (byValue) valueBlocked = true;   /* nothing fits: keep the risk size so the block shows what was needed */
    }
    m.limit = limit; m.limits = { riskQty: riskQty, totalRoomQty: totalQty, valueRoomQty: valueQty, finalQty: finalQty, valueCapPct: valueCapPct, totalCapPct: capTotalPct };
    m.qty = z.qty; m.money = z.actualRisk; m.moneyPct = z.actualRiskPct; m.avgEntry = z.avgEntry || f.entry;
    var usedPct = (existing + working) / eq * 100, firstPct = multi ? m.effPct * ((f.levels[0].splitPct || 0) / 100) : (m.money / eq * 100);
    var chkKind = multi ? 'pilot' : kind, reqPct = multi ? firstPct : (m.money / eq * 100);
    var entry = { kind: chkKind, starterOn: f.starterOn === true, thesisDone: thesis, legacy: f.legacy === true, side: f.side, entryPx: f.entry, avgEntry: avg, requestedPct: reqPct, usedPct: multi ? 0 : usedPct, factor: fac, planPct: np ? planPct : undefined, noAlone: np };
    var cc = R.compCheck({ basis: L.basis, now: L.now, account: L.acct, ideas: ideaOthers({ ideas: L.ideasW || L.ideas }, f.ideaId), costsFor: L.costsFor, cycles: L.comp.cycles, unlocks: L.comp.unlocks, regime: L.regime, signals: L.signals, emergencyFactor: L.eF, entry: entry, candidateRisk: m.money });
    m.reasons = cc.reasons.slice(); m.flags = cc.flags.slice(); m.lock = cc.lock; m.heat = cc.heat; m.entry = cc.entry; m.usedPct = usedPct;
    if (valueBlocked) m.reasons.push('COMP_VALUE_CAP');
    var hRoom = Math.max(0, eq * RP.comp.heatCapPct / 100 - cc.heat.money), totRoom = Math.max(0, totalRoomMoney), room = Math.min(hRoom, totRoom);
    m.room = { heatPct: cc.heat.pct, heatCapPct: RP.comp.heatCapPct, roomPct: hRoom / eq * 100, tickerUsedPct: usedPct, tickerCapPct: capTotalPct };
    var uv = f.mult * f.fx, hard = m.reasons.some(function (c) { return /^(COMP_LOCKED|ADDON_THESIS|COMP_VALUE_CAP)$/.test(c); });
    m.allowedQty = hard ? 0 : allowedQty(multi ? hRoom : room, z.actualDistance * uv, f.lotStep, f.minLot, m.qty);
    m.roomLine = 'Heat ' + f2(cc.heat.pct, 1) + '% of ' + RP.comp.heatCapPct + '% · room ' + f2(m.room.roomPct, 1) + '%' + (me ? ' · ticker ' + f2(usedPct, 2) + '% of ' + f2(capTotalPct, 2) + '%' : '');
    var miss = []; if (!thesis) miss.push('thesis done');
    m.addon = { locked: miss.length > 0, missing: miss, totalRoomPct: Math.max(0, capTotalPct - usedPct) };
    /* PC2 §1 — the limit in plain numbers: total risk (held at their current stop + this row) vs today's budget, and the formula behind it */
    var regPc = Math.round(fac * 100), regLab = rg.fallback ? 'fallback ' + regPc + '%' : (fac < 1 ? (emOnly ? 'emergency ' : 'risk-off ') + regPc + '%' : 'risk-on 100%');
    var newPct = m.money != null ? m.money / eq * 100 : 0, totPct = usedPct + newPct;
    m.budget = { planPct: planPct, hw: isPlan ? hwC : 1, reg: fac, regLabel: regLab, capPct: capTotalPct, text: f2(planPct, 2) + '% × homework ' + Math.round((isPlan ? hwC : 1) * 100) + '% × ' + regLab };
    m.fit = { totalPct: totPct, capPct: capTotalPct, usedPct: usedPct, newPct: newPct, held: me ? totQty(me) : 0, existing: existing, budgetMoney: eq * capTotalPct / 100, newRisk: m.money || 0, avg: avg, uv: uvv, valueLimited: !!(m.limit && m.limit.code === 'value_cap') };
    return numTexts(finish(m, { heat: cc.heat }));
  }
  /* idea-level helper for the stop form: estimated net-breakeven price, effect of confirming a new stop */
  function stopInfo(L, ideaId, newStop) {
    var i = L.ideas.filter(function (x) { return x.id === ideaId; })[0]; if (!i) return null;
    var c = L.costsFor(i), nb = R.netBreakevenStop(i, c), avg = ideaAvg(i), trial = JSON.parse(JSON.stringify(i));
    trial.tranches.forEach(function (t) { t.stop = newStop; t.stopConfirmed = true; });
    var after = R.ideaResult(trial, c);
    return { costsKnown: c.known, netBreakeven: nb, avgEntry: avg, costPerShare: nb !== null && avg !== null ? Math.abs(nb - avg) : null, projectedNetAfter: after.projectedNet, exposureAfter: after.exposure,
      atBreakeven: c.known && after.projectedNet !== null && after.projectedNet >= -1e-7, frees: i.strategy === 'winner' && R.ammoReleased(trial, c), strategy: i.strategy,
      rNow: null, firstTranche: i.tranches[0] || null };
  }

  return { live: live, liveBasis: liveBasis, liveEmergency: liveEmergency, sizeMomentum: sizeMomentum, sizeSat: sizeSat, sizeComp: sizeComp, stopInfo: stopInfo, unitCosts: unitCosts, asOfAt: asOfAt, rtext: rtext, f2: f2, pctTxt: pctTxt,
    build: build, buildAccount: buildAccount, toMarkdown: toMarkdown, toJson: toJson, badges: badges, MISSING_NOTES: MISSING_NOTES };
});
