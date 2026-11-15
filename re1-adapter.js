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
          exits.push({ id: 'x:' + t.id, time: tm.ms, qty: n(t.qty) || 0, price: n(t.exitPrice), fees: 0, swap: 0, trancheId: T.id, reason: t.exitReason || null, dateOnly: tm.dateOnly });
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
      var idea = { id: key, account: acc.id, strategy: strategy, side: side, status: status, product: symKey(t0.sym), sym: t0.sym, tranches: tranches, exits: exits, entryFees: 0, workingOrders: wo };
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
      var sl = i && i.accts && i.accts[acc.id]; if (!i || !sl || sl.skip) return;
      var has = Object.keys(info).some(function (k) { return info[k].satIdea === i.id; });
      if (has || i.status === 'closed' || i.status === 'cancelled') return;
      var placed = i.ln4 && i.ln4.placedAt, id = 's:' + i.id;
      var cur = (src.specs && src.specs[symKey(i.asset)] && src.specs[symKey(i.asset)].cur) || 'USD';
      var efx = cur === 'USD' ? fx : 1; if (efx === null) { miss.add('FX', i.id); return; }
      var mult = (src.specs && src.specs[symKey(i.asset)] && pos(n(src.specs[symKey(i.asset)].contract))) ? n(src.specs[symKey(i.asset)].contract) : null;
      var qty = pos(n(sl.lot)) ? n(sl.lot) : null, wo = [];
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
    var hw = ctx.homework[symKey(i.sym)], frac = 1, notes = out.notes;
    if (i.strategy === 'winner' || i.strategy === 'ladder') {
      if (hw === undefined) notes.push('homework state unknown — shown at 100%'); else if (hw === false) { frac = R.POLICY.mom.homeworkCap; notes.push('thesis not done → 50%'); }
    }
    var rpts = base !== null ? [base] : [R.POLICY.sat.stepRpt[ctx.satStepIndex], R.POLICY.sat.stepRpt[ctx.satStepIndex] * R.POLICY.sat.condReduced];
    if (i.strategy === 'sat') notes.push('Satellite: Condition unknown in history → shown at 100% and 65% of the current step (' + (ctx.satStepIndex + 1) + ')');
    var msPct = ctx.minStopPct(i);
    var minDist = pos(msPct) && pos(avg) ? avg * msPct / 100 : null;
    var variants = rpts.map(function (r) {
      var z = R.sizeOrder({ equity: eq, rptPct: r, factor: 1, fraction: frac, entry: avg, stop: stop, side: i.side, minStopDist: minDist, mult: mult, fx: efx, lotStep: lotStep, minLot: minLot });
      return { rptPct: r, qty: z.qty, risk: z.actualRisk, riskPct: z.actualRiskPct, reasons: z.reasons, minStopApplied: !!z.minStopApplied };
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
    var ff = src.ff || {}, rat = ff.ratios || {}, g = function (k) { var r = rat[k]; if (!r) return null; var up = r.slow && typeof r.slow.up === 'boolean' ? r.slow.up : (typeof r.up === 'boolean' ? r.up : null); return up; };
    var slowMissing = ['ACWI_BIL', 'HYG_IEI'].filter(function (k) { return rat[k] && !(rat[k].slow && typeof rat[k].slow.up === 'boolean'); });
    var signals = { acwi: g('ACWI_BIL'), hyg: g('HYG_IEI'), asOf: ff.as_of || null };
    var regime = R.regimeState(signals, now);
    report.regime = { signals: signals, factor: regime.factor, base: regime.base, fresh: regime.fresh, ageDays: regime.ageDays, demo: !!ff.demo, slowSeriesMissing: slowMissing, flags: regime.flags };
    if (ff.demo) report.notes.push('fundflow.json not loaded (demo data) — regime result is not usable');

    (src.accounts || []).forEach(function (acc) {
      var M = new Missing(), A = buildAccount(src, acc, M), S = A.S || {};
      var out = { id: acc.id, name: acc.name, ports: acc.ports || null };
      // equity basis: engine needs confirmed snapshots; none exist → entered-capital PROXY (flagged everywhere)
      var cap = S.capital || {}, pc = src.portCur || { core: 'THB', satB: 'USD' }, ports = acc.ports || ['core', 'satB'];
      var coreV = ports.indexOf('core') >= 0 && n(cap.core) !== null ? n(cap.core) * (pc.core === 'USD' ? (A.fx || 0) : 1) : 0;
      var satV = ports.indexOf('satB') >= 0 && n(cap.satB) !== null ? n(cap.satB) * (pc.satB === 'USD' ? (A.fx || 0) : 1) : 0;
      var proxy = coreV + satV, realSnaps = Array.isArray(S.equitySnapshots) ? S.equitySnapshots : null;
      var snaps, basisKind;
      if (realSnaps && realSnaps.length) { snaps = realSnaps; basisKind = 'confirmed snapshots'; }
      else { snaps = pos(proxy) ? [{ at: R.bkk.weekStart(now) + 1, equity: proxy, confirmed: true }] : []; basisKind = 'PROXY (entered capital, not a snapshot)'; M.add('EQUITY_SNAPSHOT', acc.id); }
      var basis = R.snapshotBasis(snaps, now);
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
      var heat = R.compHeat(ideas, acc.id, costsFor, basis.ok ? basis.weekEquity : null, basis.ok ? basis.currentEquity : null);
      var legacy = [];
      comp.forEach(function (i) {
        var m = A.info[i.id] || {}, ls = R.compLegacyShape({ tranches: i.tranches.length, accelLots: i.tranches.filter(function (t) { return t.acc; }).length });
        var card = (src.cards || []).filter(function (c) { return c.id === m.card; })[0], lots = card && Array.isArray(card.lots) ? card.lots : [];
        var accLots = lots.filter(function (l) { return l && (l.layer === 'acc' || l.acc === true); }).length, ls2 = R.compLegacyShape({ tranches: Math.max(i.tranches.length, lots.length), accelLots: Math.max(accLots, i.tranches.filter(function (t) { return t.acc; }).length) });
        if (ls2.legacy && i.status !== 'closed') legacy.push({ id: i.id, sym: i.sym, status: i.status, tranches: Math.max(i.tranches.length, lots.length), accelerator: Math.max(accLots, 0) || undefined, why: ls2.why, strategyKey: card ? card.strategy : null });
      });
      out.compounder = { streak: streak.streak, locked: streak.locked, cyclesClosed: cycles.length, heatMoney: heat.money, heatPctWeekStart: heat.pct, heatPctCurrent: heat.pctCurrent, heatCapPct: R.POLICY.comp.heatCapPct, heatCount: heat.count,
        regimeFactor: regime.factor, regimeFresh: regime.fresh, regimeAgeDays: regime.ageDays, legacyShapeCards: legacy };

      // Emergency: needs confirmed snapshots
      out.emergency = realSnaps && realSnaps.length ? (function () { var last = realSnaps[realSnaps.length - 1]; var e = R.emergencyStep(null, last, basis.ok ? { equity: basis.monthEquity, at: basis.monthAt } : null, S.cashFlows || []); return { state: e.active ? 'ACTIVE' : 'off', declinePct: e.declinePct, factor: e.factor }; })() : { state: 'n/a', reason: 'no confirmed equity snapshots — Emergency cannot be evaluated; shown as off (factor 1)', factor: 1 };

      // Positions & working orders: old vs engine
      var ctx = { weekEquity: basis.ok ? basis.weekEquity : null, fx: A.fx, homework: src.homework || {}, satStepIndex: step.stepIndex,
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
        (es.notes || []).forEach(function (t) { if (/50%/.test(t)) why.push('HOMEWORK_50'); });
        if (es.reasons.length) why = why.concat(es.reasons);
        if (i.tranches.some(function (t) { return t.initialStopUnknown; })) why.push('INITIAL_STOP_UNKNOWN');
        if (basisKind !== 'confirmed snapshots') why.push('EQUITY_PROXY');
        var meta2 = A.info[i.id] || {};
        rowsOut.push({ id: i.id, sym: i.sym, strategy: i.strategy, status: i.status, side: i.side, legacyShape: comp.indexOf(i) >= 0 && legacy.some(function (l) { return l.id === i.id; }),
          old: { qtyAsEntered: oldQty, qtyHeldNow: heldQty, avgEntry: ideaAvg(i), currentStop: i.tranches[0] ? i.tranches[0].stop : (i.workingOrders[0] ? i.workingOrders[0].stop : null), initialStop: i.tranches[0] ? i.tranches[0].initialStop : null,
            principalRiskAtCurrentStop: oldRiskCur, riskAtInitialStop: oldRiskInit, workingOrderRisk: woRisk, riskPctOfEquityAtInitial: oldInitPct },
          engine: { rptPct: es.rptPct, qty: es.qty, riskMoney: es.risk, riskPct: es.riskPct, variants: es.variants, reasons: es.reasons, notes: es.notes },
          whyDifferent: Array.from(new Set(why)), exposure: res0.exposure, projectedNet: res0.projectedNet, costUnknown: res0.costUnknown, tranches: i.tranches.length, accelerator: meta2.hasAcc || false });
      });
      out.positions = rowsOut;

      // Orders that would be blocked today (Ordered + complete Planned), evaluated as a NEW order against everything else
      var blocked = [];
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
          var h2 = R.compHeat(others, acc.id, costsFor, basis.weekEquity, basis.currentEquity); if (risk !== null && h2.money + risk > basis.weekEquity * R.POLICY.comp.heatCapPct / 100 + 1e-7) r.push('COMP_HEAT');
          f = f.concat(regime.flags);
        }
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
    P('## Regime (Compounder)'); P('');
    P('- ACWI/BIL (slow): ' + (rp.regime.signals.acwi === null ? 'Unknown' : rp.regime.signals.acwi ? 'green' : 'red') + ' · HYG/IEI (slow): ' + (rp.regime.signals.hyg === null ? 'Unknown' : rp.regime.signals.hyg ? 'green' : 'red') + ' · as-of ' + (rp.regime.signals.asOf || 'Unknown'));
    P('- Factor **' + Math.round(rp.regime.factor * 100) + '%** · fresh: ' + (rp.regime.fresh ? 'yes' : 'NO') + (rp.regime.ageDays != null ? ' (' + rp.regime.ageDays + ' calendar days old)' : '') + (rp.regime.slowSeriesMissing.length ? ' · slow series missing for ' + rp.regime.slowSeriesMissing.join(', ') : '')); P('');
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

  return { build: build, buildAccount: buildAccount, toMarkdown: toMarkdown, toJson: toJson, badges: badges, MISSING_NOTES: MISSING_NOTES };
});
