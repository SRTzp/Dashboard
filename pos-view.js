/* pos-view.js — PV1 honest position numbers (pure functions · no DOM / clock / storage)
   One formula for every surface (Today row · Plan card · drawer). Used two ways: Node (module.exports) for tests · browser (globalThis.PosView).
   index.html carries a byte-for-byte copy between BEGIN/END markers (python3 tools/sync_pv1.py).
   calc(inp) — inp:
     dir 'long'|'short' · mult (contract multiplier, default 1) · fx (account-currency per 1 unit of price currency; 1 for same currency; null = missing) · fxSrc (text)
     fills [{qty,px}]   filled lots only (held)           planned [{qty,px}]  every plan row, filled or not (null = not sized)
     stop (current stop) · initialStop (first stop, for R) · price · priceAt · priceSrc · equity (account) · pool (strategy pool)
     openRiskMoney  engine exposure for the held quantity (optional; when absent the loss at the current stop is computed here)
     plannedRiskMoney / plannedRiskPct  stored whole-plan risk (optional; when absent it is computed from `planned` + `stop`)
     targets [{qty,px}] planned exits · exits [{qty,px}] exits already taken (display only: reward / banked)
     plannedValueMoney  whole-plan position value at the planned prices (optional; when absent computed from `planned`)
   Returns a flat object. Every figure that cannot be worked out is null and has a reason in why[<field>] — never 0, never an assumed value.
   Money is in account currency (price × qty × mult × fx). Percentages are plain numbers (1.2 = 1.2%). Planned rows never touch heldQty / cost / value. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.PosView = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  var num = function (v) { return typeof v === 'number' && isFinite(v); };
  var pos = function (v) { return num(v) && v > 0; };
  function sum(rows, f) { return (rows || []).reduce(function (s, r) { return s + f(r); }, 0); }
  function clean(rows) { return (rows || []).filter(function (r) { return r && pos(+r.qty) && pos(+r.px); }).map(function (r) { return { qty: +r.qty, px: +r.px }; }); }

  function calc(inp) {
    inp = inp || {};
    var why = {}, o = { why: why };
    var dir = String(inp.dir).toLowerCase() === 'short' ? -1 : 1, mult = pos(+inp.mult) ? +inp.mult : 1;
    var fx = pos(+inp.fx) ? +inp.fx : null, uv = fx === null ? null : mult * fx;
    var fills = clean(inp.fills), plannedRaw = inp.planned, planned = plannedRaw == null ? null : clean(plannedRaw);
    var stop = pos(+inp.stop) ? +inp.stop : null, price = pos(+inp.price) ? +inp.price : null;
    var equity = pos(+inp.equity) ? +inp.equity : null, pool = pos(+inp.pool) ? +inp.pool : null;
    o.dir = dir === -1 ? 'short' : 'long'; o.mult = mult; o.fx = fx; o.fxSrc = inp.fxSrc || null; if (fx === null) why.fx = 'no FX';
    o.stop = stop;

    o.heldQty = sum(fills, function (r) { return r.qty; });
    o.plannedQty = planned && planned.length ? sum(planned, function (r) { return r.qty; }) : null; if (o.plannedQty === null) why.plannedQty = 'not sized';
    o.entriesDone = fills.length; o.entriesTotal = planned && planned.length ? Math.max(planned.length, fills.length) : (fills.length || null);
    o.avgEntry = o.heldQty > 0 ? sum(fills, function (r) { return r.qty * r.px; }) / o.heldQty : null; if (o.avgEntry === null) why.avgEntry = 'no filled shares';

    o.price = price; o.priceAt = inp.priceAt || null; o.priceSrc = inp.priceSrc || null; if (price === null) why.price = 'no live price';

    o.cost = null; o.value = null; o.uPnl = null; o.uPnlPct = null; o.weightAcct = null; o.weightPool = null; o.toStop = null; o.openRisk = null; o.openRiskPct = null; o.stopPnl = null; o.stopPnlPct = null; o.openRiskNone = false;
    if (o.heldQty > 0) {
      if (uv === null) { ['cost', 'value', 'uPnl', 'uPnlPct', 'weightAcct', 'weightPool', 'toStop', 'openRisk', 'openRiskPct'].forEach(function (k) { why[k] = 'no FX'; }); }
      else {
        o.cost = sum(fills, function (r) { return r.qty * r.px; }) * uv;
        if (price !== null) {
          o.value = o.heldQty * price * uv;
          o.uPnl = dir * (price - o.avgEntry) * o.heldQty * uv; o.uPnlPct = o.cost > 0 ? o.uPnl / o.cost * 100 : null;
          o.weightAcct = equity !== null ? o.value / equity * 100 : null; if (equity === null) why.weightAcct = 'no account value';
          o.weightPool = pool !== null ? o.value / pool * 100 : null; if (pool === null) why.weightPool = 'no strategy pool';
          if (stop !== null) o.toStop = o.heldQty * Math.abs(price - stop) * uv; else why.toStop = 'no stop';
        } else { ['value', 'uPnl', 'uPnlPct', 'weightAcct', 'weightPool', 'toStop'].forEach(function (k) { why[k] = 'no live price'; }); }
        if (stop !== null) {
          o.stopPnl = dir * (stop - o.avgEntry) * o.heldQty * uv; o.stopPnlPct = equity !== null ? o.stopPnl / equity * 100 : null;
          var r = num(inp.openRiskMoney) ? inp.openRiskMoney : Math.max(0, -o.stopPnl);
          if (r > 1e-9) { o.openRisk = r; o.openRiskPct = equity !== null ? r / equity * 100 : null; if (equity === null) why.openRiskPct = 'no account value'; }
          else { o.openRiskNone = true; why.openRisk = 'none · stop at or beyond entry'; }
        } else { why.openRisk = 'no stop'; why.stopPnl = 'no stop'; }
      }
    } else { ['cost', 'value', 'uPnl', 'uPnlPct', 'weightAcct', 'weightPool', 'toStop', 'openRisk', 'openRiskPct'].forEach(function (k) { why[k] = 'nothing filled yet'; }); }

    /* whole-plan risk (stored figure wins; else computed from every planned row at the stop) */
    o.plannedRisk = null; o.plannedRiskPct = null;
    if (pos(+inp.plannedRiskMoney)) { o.plannedRisk = +inp.plannedRiskMoney; o.plannedRiskPct = num(+inp.plannedRiskPct) && inp.plannedRiskPct != null ? +inp.plannedRiskPct : (equity !== null ? o.plannedRisk / equity * 100 : null); }
    else if (planned && planned.length && stop !== null && uv !== null) {
      o.plannedRisk = sum(planned, function (r) { return r.qty * Math.max(0, dir * (r.px - stop)); }) * uv; o.plannedRiskPct = equity !== null ? o.plannedRisk / equity * 100 : null;
      if (!(o.plannedRisk > 1e-9)) { o.plannedRisk = null; o.plannedRiskPct = null; why.plannedRisk = 'none · stop at or beyond entry'; }
    } else why.plannedRisk = !planned || !planned.length ? 'not sized' : stop === null ? 'no stop' : 'no FX';

    o.plannedValue = null;
    if (pos(+inp.plannedValueMoney)) o.plannedValue = +inp.plannedValueMoney;
    else if (planned && planned.length && uv !== null) o.plannedValue = sum(planned, function (r) { return r.qty * r.px; }) * uv;
    else if (planned && planned.length) why.plannedValue = 'no FX'; else why.plannedValue = 'not sized';

    /* R = one unit of initial risk per share = |first entry − first stop| */
    var e0 = fills.length ? fills[0].px : (planned && planned.length ? planned[0].px : null), s0 = pos(+inp.initialStop) ? +inp.initialStop : stop;
    o.rUnit = (e0 !== null && s0 !== null && dir * (e0 - s0) > 0) ? dir * (e0 - s0) : null; if (o.rUnit === null) why.rUnit = 'no initial stop';
    o.R = (o.rUnit !== null && price !== null && o.avgEntry !== null) ? dir * (price - o.avgEntry) / o.rUnit : null; if (o.R === null) why.R = o.rUnit === null ? why.rUnit : price === null ? 'no live price' : 'nothing filled yet';
    /* PV1b — display-only extras: initial stop · reward at the planned targets · banked on exits already taken (never feed sizing / risk / gates) */
    o.initialStop = pos(+inp.initialStop) ? +inp.initialStop : null;
    o.reward = null; o.rewardR = null; o.banked = null;
    var tg = clean(inp.targets);
    if (planned && planned.length && tg.length && uv !== null) {
      var pq = sum(planned, function (r) { return r.qty; }), pa = sum(planned, function (r) { return r.qty * r.px; }) / pq;
      o.reward = sum(tg, function (t) { return dir * (t.px - pa) * t.qty; }) * uv;
      if (o.plannedRisk > 0) o.rewardR = o.reward / o.plannedRisk;
    } else why.reward = !planned || !planned.length ? 'not sized' : !tg.length ? 'no target' : 'no FX';
    var ex = clean(inp.exits);
    if (ex.length && o.avgEntry !== null && uv !== null) o.banked = sum(ex, function (x) { return dir * (x.px - o.avgEntry) * x.qty; }) * uv;
    return o;
  }
  return { calc: calc };
});
