/* ps1-size.js — PS1 Portfolio & Risk (pure functions · no DOM / clock / storage)
   Rules: docs/briefs/PS1-brief.md. Used two ways: Node (module.exports) for tests · browser (globalThis.Ps1).
   index.html carries a byte-for-byte copy between BEGIN/END markers (python3 tools/sync_ps1.py).
   Every function takes one object and returns an object. Bad input -> {ok:false, err:'CODE'} (never throws).
   Money is whatever single currency the caller passes (E and prices in the same currency).
   Percentages are plain numbers (0.5 = 0.5%). Shares are always rounded DOWN to the lot. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.Ps1 = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var EPS = 1e-9;
  /* bucket keys = the dashboard's own keys: ladder = Compounder · winner = Momentum · sat = Satellite */
  var BUCKETS = {
    ladder: { label: 'Compounder', weight: 50, riskMin: 0.80, riskMax: 1.25, sizeMin: 10, sizeMax: 12.5, cap: 3.0 },
    winner: { label: 'Momentum',   weight: 30, riskMin: 0.35, riskMax: 0.50, sizeMin: 6,  sizeMax: 7.5,  cap: 1.5 },
    sat:    { label: 'Satellite',  weight: 20, riskMin: 0.10, riskMax: 0.25, sizeMin: null, sizeMax: null, cap: 0.5 }
  };
  var TOTAL_CAP = 5.0, GB_AMBER = 8, GB_RED = 10, MAX_ROWS = 4;

  function num(x) { return typeof x === 'number' && isFinite(x); }
  function fail(err) { return { ok: false, err: err }; }
  function floorLot(q, lot) {
    if (!num(q) || q <= 0) return 0;
    lot = lot > 0 ? lot : 1;
    return Math.floor(q / lot + EPS) * lot;
  }
  function round(x, d) { var m = Math.pow(10, d); return Math.round(x * m) / m; }
  function lotOf(market, lot) { return num(lot) && lot > 0 ? lot : (market === 'TH' ? 100 : 1); }

  /* Settings (settings.psRisk, stored as plain numbers, % units). Missing / out-of-range default risk -> null (= "not set").
     raw = {max:{ladder,winner}, cap:{ladder,winner,sat}, total, gb:{amber,red}, weights:{...}, def:{ladder,winner,satMain,satTac}} */
  function inRange(v, lo, hi) { return num(v) && v >= lo - EPS && v <= hi + EPS; }
  function cfg(raw) {
    raw = raw || {};
    var out = { buckets: {}, total: num(raw.total) && raw.total > 0 ? raw.total : TOTAL_CAP,
      gbAmber: raw.gb && num(raw.gb.amber) && raw.gb.amber > 0 ? raw.gb.amber : GB_AMBER,
      gbRed: raw.gb && num(raw.gb.red) && raw.gb.red > 0 ? raw.gb.red : GB_RED, def: {} };
    if (out.gbRed < out.gbAmber) out.gbRed = out.gbAmber;
    Object.keys(BUCKETS).forEach(function (k) {
      var d = BUCKETS[k], w = raw.weights && num(raw.weights[k]) && raw.weights[k] >= 0 ? raw.weights[k] : d.weight;
      var cap = raw.cap && num(raw.cap[k]) && raw.cap[k] > 0 ? raw.cap[k] : d.cap;
      var mx = raw.max && num(raw.max[k]) && raw.max[k] > 0 ? raw.max[k] : d.sizeMax;
      out.buckets[k] = { label: d.label, weight: w, riskMin: d.riskMin, riskMax: d.riskMax, sizeMax: mx, cap: cap };
    });
    var dd = raw.def || {};
    ['ladder', 'winner'].forEach(function (k) {
      var b = BUCKETS[k]; out.def[k] = inRange(dd[k], b.riskMin, b.riskMax) ? dd[k] : null;
    });
    ['satMain', 'satTac'].forEach(function (k) { out.def[k] = inRange(dd[k], BUCKETS.sat.riskMin, BUCKETS.sat.riskMax) ? dd[k] : null; });
    var sum = 0; Object.keys(out.buckets).forEach(function (k) { sum += out.buckets[k].weight; });
    out.weightsOk = Math.abs(sum - 100) < 1e-6;
    return out;
  }
  /* validation of the settings form -> {field: message} */
  function cfgErrors(raw) {
    raw = raw || {}; var e = {}, dd = raw.def || {};
    [['ladder', 'ladder'], ['winner', 'winner'], ['satMain', 'sat'], ['satTac', 'sat']].forEach(function (p) {
      var v = dd[p[0]], b = BUCKETS[p[1]];
      if (v === null || v === undefined || v === '' || (num(v) && isNaN(v))) return;   /* empty = allowed (shows "Set default risk") */
      if (!inRange(v, b.riskMin, b.riskMax)) e['def.' + p[0]] = 'Use ' + b.riskMin + '–' + b.riskMax + '%';
    });
    if (raw.weights) {
      var s = 0, bad = false; Object.keys(BUCKETS).forEach(function (k) { var w = raw.weights[k]; if (!num(w) || w < 0) bad = true; else s += w; });
      if (bad || Math.abs(s - 100) > 1e-6) e.weights = 'Weights must total 100';
    }
    if (raw.total !== undefined && !(num(raw.total) && raw.total > 0 && raw.total <= 100)) e.total = '> 0';
    if (raw.gb && num(raw.gb.amber) && num(raw.gb.red) && raw.gb.red < raw.gb.amber) e.gb = 'Red must be ≥ amber';
    return e;
  }

  /* ── Plan sizing (Momentum + Compounder) ──
     E · lot · maxSizePct (% of E)
     entries = [{px, riskPct}]   (1 row: riskPct omitted -> uses ideaRiskPct) · ideaRiskPct = this idea's budget (% of E) × multiplier already applied by caller
     stops   = [{px, pct}]       (1 row: full exit · 2+ rows: pct = % of shares exited, must total 100)
     Shares per entry row = floor(rowRisk% × E / (entry − blendedStop)). Size cap trims all rows proportionally (floor to lot).
     Risk used = Σ shares × (entry − blendedStop) / E. */
  function blendStop(stops) {
    if (!stops || !stops.length) return fail('NO_STOP');
    if (stops.length > MAX_ROWS) return fail('TOO_MANY_STOPS');
    var i, s = 0, t = 0;
    for (i = 0; i < stops.length; i++) if (!(num(stops[i].px) && stops[i].px > 0)) return fail('BAD_STOP');
    if (stops.length === 1) return { ok: true, px: stops[0].px, multi: false };
    for (i = 0; i < stops.length; i++) {
      if (!(num(stops[i].pct) && stops[i].pct > 0)) return fail('STOP_PCT');
      s += stops[i].px * stops[i].pct; t += stops[i].pct;
    }
    if (Math.abs(t - 100) > 1e-6) return fail('STOP_PCT_100');
    return { ok: true, px: s / t, multi: true };
  }
  function planSize(o) {
    o = o || {};
    var E = o.E, en = o.entries, lot = lotOf(o.market, o.lot);
    if (!(num(E) && E > 0)) return fail('NO_E');
    if (!en || !en.length) return fail('NO_ENTRY');
    if (en.length > MAX_ROWS) return fail('TOO_MANY_ENTRIES');
    var bs = blendStop(o.stops); if (!bs.ok) return bs;
    var stop = bs.px, multi = en.length > 1, i;
    var idea = o.ideaRiskPct;
    if (!(num(idea) && idea > 0)) return fail('NO_RISK');
    var rows = [], sumRow = 0;
    for (i = 0; i < en.length; i++) {
      var px = en[i].px;
      if (!(num(px) && px > 0)) return fail('BAD_ENTRY');
      if (!(px > stop + EPS)) return fail('ENTRY_NOT_ABOVE_STOP');
      var rr = multi ? en[i].riskPct : idea;
      if (!(num(rr) && rr > 0)) return fail('ROW_RISK');
      sumRow += rr;
      rows.push({ px: px, riskPct: rr, qty: floorLot(rr / 100 * E / (px - stop), lot) });
    }
    var res = { ok: true, E: E, lot: lot, stop: stop, multi: multi, stopMulti: bs.multi, rows: rows, idea: idea, errs: [] };
    if (multi && sumRow > idea + EPS) res.errs.push('ROWS_OVER_BUDGET');
    /* size cap -> trim all rows proportionally */
    var cost = 0, q = 0; rows.forEach(function (r) { cost += r.qty * r.px; q += r.qty; });
    res.trimmed = false;
    var capCost = Infinity, sizeCost = Infinity, hasCash = num(o.cash) && o.cash >= 0;
    if (num(o.maxSizePct) && o.maxSizePct > 0) sizeCost = o.maxSizePct / 100 * E;
    capCost = sizeCost; if (hasCash && o.cash < capCost) capCost = o.cash;   /* existing free-cash check applies on top of the size cap */
    res.cashLimited = false;
    if (capCost < Infinity) {
      if (cost > capCost + EPS) {
        res.cashLimited = hasCash && o.cash <= sizeCost + EPS;
        var k = capCost / cost; res.trimmed = true; res.untrimmedQty = q;
        cost = 0; q = 0;
        rows.forEach(function (r) { r.qty = floorLot(r.qty * k, lot); cost += r.qty * r.px; q += r.qty; });
        /* proportional floor can still leave cost marginally over because of lot rounding of different prices -> step down */
        var guard = 0;
        while (cost > capCost + EPS && guard++ < 1000) {
          var j = -1, best = -1; rows.forEach(function (r, ix) { if (r.qty >= lot && r.px > best) { best = r.px; j = ix; } });
          if (j < 0) break; rows[j].qty -= lot; cost -= lot * rows[j].px;
        }
        q = 0; rows.forEach(function (r) { q += r.qty; });
      }
    }
    var risk = 0; rows.forEach(function (r) { r.risk = r.qty * (r.px - stop); risk += r.risk; r.cost = r.qty * r.px; });
    res.qty = q; res.cost = cost; res.avgEntry = q > 0 ? cost / q : null; res.avgStop = stop;
    res.risk = risk; res.riskPct = risk / E * 100; res.leftPct = Math.max(0, idea - res.riskPct);
    res.sizePct = cost / E * 100;
    res.zero = q === 0;
    return res;
  }

  /* ── Cap checks (before Save) ──
     E · bucket · newRisk (money) · usedBucket / usedTotal = principal risk already open (money) · unknownCount = positions with unknown risk
     -> {ok, reasons:[CODE], bucketPct, totalPct, bucketLeftPct, totalLeftPct} */
  function capCheck(o) {
    o = o || {}; var c = o.cfg || cfg(null), E = o.E;
    if (!(num(E) && E > 0)) return fail('NO_E');
    var b = c.buckets[o.bucket]; if (!b) return fail('BAD_BUCKET');
    var nr = num(o.newRisk) && o.newRisk > 0 ? o.newRisk : 0;
    var ub = num(o.usedBucket) ? o.usedBucket : 0, ut = num(o.usedTotal) ? o.usedTotal : 0;
    var bp = (ub + nr) / E * 100, tp = (ut + nr) / E * 100, reasons = [];
    if (bp > b.cap + EPS) reasons.push('BUCKET_CAP');
    if (tp > c.total + EPS) reasons.push('TOTAL_CAP');
    return { ok: reasons.length === 0, reasons: reasons, bucketPct: bp, totalPct: tp, bucketCap: b.cap, totalCap: c.total,
      bucketLeftPct: Math.max(0, b.cap - ub / E * 100), totalLeftPct: Math.max(0, c.total - ut / E * 100) };
  }

  /* ── Add-on (pyramid) ──
     tranches = [{qty, avg, stop}] (long) · ideaBudgetMoney = full idea budget · currentRisk = principal risk of the idea now (money)
     New full budget allowed only when EVERY tranche stop >= its average entry (principal risk 0). Otherwise only what's left. */
  function addOnBudget(o) {
    o = o || {}; var tr = o.tranches || [];
    if (!tr.length) return fail('NO_POSITION');
    if (!(num(o.ideaBudget) && o.ideaBudget > 0)) return fail('NO_BUDGET');
    var allSafe = true, risk = 0, i;
    for (i = 0; i < tr.length; i++) {
      var t = tr[i];
      if (!(num(t.qty) && t.qty > 0 && num(t.avg) && t.avg > 0 && num(t.stop) && t.stop > 0)) return fail('BAD_TRANCHE');
      if (t.stop < t.avg - EPS) allSafe = false;
      risk += t.qty * Math.max(0, t.avg - t.stop);
    }
    return { ok: true, newBudget: allSafe, risk: risk, budget: allSafe ? o.ideaBudget : Math.max(0, o.ideaBudget - risk),
      left: allSafe ? o.ideaBudget : Math.max(0, o.ideaBudget - risk) };
  }
  /* shares for an add-on at (px, stop) given the budget money */
  function addOnQty(o) {
    o = o || {};
    if (!(num(o.budget) && o.budget > 0)) return { ok: true, qty: 0 };
    if (!(num(o.px) && num(o.stop) && o.px > o.stop)) return fail('BAD_PRICES');
    return { ok: true, qty: floorLot(o.budget / (o.px - o.stop), lotOf(o.market, o.lot)) };
  }

  /* ── Satellite contracts / lots ──
     lots = floor( E × risk% ÷ (|entry − stop| × multiplier) , lotStep ) · single stop, full exit */
  function satLots(o) {
    o = o || {};
    if (!(num(o.E) && o.E > 0)) return fail('NO_E');
    if (!(num(o.riskPct) && o.riskPct > 0)) return fail('NO_RISK');
    if (!(num(o.entry) && o.entry > 0 && num(o.stop) && o.stop > 0 && Math.abs(o.entry - o.stop) > EPS)) return fail('BAD_PRICES');
    if (!(num(o.multiplier) && o.multiplier > 0 && num(o.lotStep) && o.lotStep > 0)) return fail('BAD_SPEC');
    var perLot = Math.abs(o.entry - o.stop) * o.multiplier, raw = o.E * o.riskPct / 100 / perLot;
    var lots = round(Math.floor(raw / o.lotStep + EPS) * o.lotStep, 8);
    var min = num(o.minLot) && o.minLot > 0 ? o.minLot : o.lotStep;
    return { ok: true, raw: raw, lots: lots, perLot: perLot, risk: lots * perLot, riskPct: lots * perLot / o.E * 100, belowMin: lots < min - 1e-12 };
  }

  /* ── Portfolio Risk panel ──
     positions = [{id, ticker, bucket, side:'Long'|'Short', qty, mult, avg, stop, px, fx}]  (money converted by caller via fx; all -> E currency)
     principal = qty×mult×max(0, avg−stop) for Long (0 when stop ≥ avg) · Short mirrored  -> needs avg & stop, else unknown
     giveBack  = qty×mult×max(0, px−stop) (incl. open profit)                               -> needs px & stop, else unknown
     Unknown is NEVER counted as 0: it is listed in .missing and excluded from sums (sums are labelled partial). */
  function positionRisk(p) {
    var q = (num(p.qty) ? p.qty : 0) * (num(p.mult) && p.mult > 0 ? p.mult : 1) * (num(p.fx) && p.fx > 0 ? p.fx : 1), short = p.side === 'Short';
    var hasStop = num(p.stop) && p.stop > 0, hasAvg = num(p.avg) && p.avg > 0, hasPx = num(p.px) && p.px > 0;
    var principal = null, giveBack = null;
    if (hasStop && hasAvg) principal = q * Math.max(0, short ? p.stop - p.avg : p.avg - p.stop);
    if (hasStop && hasPx) giveBack = q * Math.max(0, short ? p.stop - p.px : p.px - p.stop);
    return { principal: principal, giveBack: giveBack, missingStop: !hasStop, missingPx: !hasPx, missing: !hasStop || !hasPx };
  }
  function gbLevel(pct, c) { c = c || cfg(null); return pct >= c.gbRed - EPS ? 'red' : (pct >= c.gbAmber - EPS ? 'amber' : 'ok'); }
  function panel(o) {
    o = o || {}; var c = o.cfg || cfg(null), E = o.E;
    if (!(num(E) && E > 0)) return fail('NO_E');
    var ps = o.positions || [], out = { ok: true, E: E, buckets: {}, ideas: [], missing: [], unknownPrincipal: 0, unknownGiveBack: 0 }, i, tot = 0, gb = 0;
    Object.keys(c.buckets).forEach(function (k) { out.buckets[k] = { principal: 0, value: 0, cap: c.buckets[k].cap, weight: c.buckets[k].weight }; });
    for (i = 0; i < ps.length; i++) {
      var p = ps[i], r = positionRisk(p), b = out.buckets[p.bucket];
      var val = (num(p.qty) ? p.qty : 0) * (num(p.mult) && p.mult > 0 ? p.mult : 1) * (num(p.fx) && p.fx > 0 ? p.fx : 1) * (num(p.px) && p.px > 0 ? p.px : (num(p.avg) ? p.avg : 0));
      if (b) b.value += val;
      if (r.principal === null) out.unknownPrincipal++; else { tot += r.principal; if (b) b.principal += r.principal; }
      if (r.giveBack === null) out.unknownGiveBack++; else gb += r.giveBack;
      if (r.missing) out.missing.push({ id: p.id, ticker: p.ticker, bucket: p.bucket, missingStop: r.missingStop, missingPx: r.missingPx });
      out.ideas.push({ id: p.id, ticker: p.ticker, bucket: p.bucket, principal: r.principal, principalPct: r.principal === null ? null : r.principal / E * 100,
        giveBack: r.giveBack, giveBackPct: r.giveBack === null ? null : r.giveBack / E * 100, missing: r.missing });
    }
    out.principal = tot; out.principalPct = tot / E * 100; out.totalCap = c.total;
    out.totalLeftPct = Math.max(0, c.total - out.principalPct);
    out.giveBack = gb; out.giveBackPct = gb / E * 100; out.giveBackLevel = gbLevel(out.giveBackPct, c);
    out.partial = out.unknownPrincipal > 0 || out.unknownGiveBack > 0;
    Object.keys(out.buckets).forEach(function (k) {
      var b = out.buckets[k]; b.principalPct = b.principal / E * 100; b.leftPct = Math.max(0, b.cap - b.principalPct);
      b.capUsedPct = b.cap > 0 ? b.principalPct / b.cap * 100 : 0; b.actualPct = b.value / E * 100;
      b.stopOpening = b.principalPct >= b.cap - EPS || out.principalPct >= c.total - EPS;
      b.status = b.stopOpening ? 'stop' : 'normal';
    });
    return out;
  }

  /* ══ PS1b ══ */
  /* ── Sat minimum stop distance (% of entry price) ──
     minPct = per-asset setting (null/0 = not set -> blocked) · pointSize = price units per "point" (display only, default 1) */
  function minStopCheck(o) {
    o = o || {};
    if (!(num(o.minPct) && o.minPct > 0)) return { ok: false, err: 'MIN_NOT_SET' };
    if (!(num(o.entry) && o.entry > 0)) return { ok: true, err: null, minDist: null, minPts: null };   /* nothing to compare yet */
    var ps = num(o.pointSize) && o.pointSize > 0 ? o.pointSize : 1, minDist = o.entry * o.minPct / 100, minPts = minDist / ps;
    if (!(num(o.stop) && o.stop > 0)) return { ok: true, err: null, minDist: minDist, minPts: minPts, pts: null };
    var d = Math.abs(o.entry - o.stop);
    return { ok: d >= minDist - 1e-9 * o.entry, err: d >= minDist - 1e-9 * o.entry ? null : 'TOO_TIGHT', minDist: minDist, minPts: minPts, pts: d / ps };
  }
  /* risk as % of the port's own value (Details only) */
  function portPct(riskMoney, portValue) { return num(riskMoney) && num(portValue) && portValue > 0 ? riskMoney / portValue * 100 : null; }

  /* ── Loss limits (per port) ──  Thai time = UTC+7 · day resets 06:00 · week resets Monday 06:00 */
  var HR = 3600000, DAY = 86400000, LOSS_DEF = { ddMax: 20, ddHalf: 10, dayR: 2, weekR: 5 };
  function lossCfg(raw) {
    raw = raw || {}; var o = {};
    Object.keys(LOSS_DEF).forEach(function (k) { o[k] = num(raw[k]) && raw[k] > 0 ? raw[k] : LOSS_DEF[k]; });
    if (o.ddHalf >= o.ddMax) o.ddHalf = o.ddMax;
    return o;
  }
  function lossCfgErrors(raw) {
    raw = raw || {}; var e = {};
    ['ddMax', 'ddHalf', 'dayR', 'weekR'].forEach(function (k) { if (raw[k] !== undefined && raw[k] !== null && raw[k] !== '' && !(num(raw[k]) && raw[k] > 0)) e[k] = '> 0'; });
    if (!e.ddMax && !e.ddHalf && num(raw.ddMax) && num(raw.ddHalf) && raw.ddHalf >= raw.ddMax) e.ddHalf = 'Must be below max drawdown';
    if (!e.ddMax && num(raw.ddMax) && raw.ddMax > 100) e.ddMax = '≤ 100';
    if (!e.dayR && !e.weekR && num(raw.dayR) && num(raw.weekR) && raw.weekR < raw.dayR) e.weekR = 'Week limit must be ≥ day limit';
    return e;
  }
  function dayStart(now) { var i = Math.floor((now + HR) / DAY); return i * DAY - HR; }                    /* last 06:00 Thai */
  function weekStart(now) { var i = Math.floor((now + HR) / DAY), dow = ((i + 3) % 7 + 7) % 7; return (i - dow) * DAY - HR; }   /* Monday 06:00 Thai */
  /* drawdown state machine · st = {peak, half, low, stopped} · returns new state (pure) */
  function lossStep(st, value, c) {
    c = lossCfg(c); st = st || {};
    var n = { peak: num(st.peak) ? st.peak : null, half: !!st.half, low: num(st.low) ? st.low : null, stopped: !!st.stopped };
    if (!(num(value) && value > 0)) return n;
    if (n.stopped) return n;                                  /* frozen until resume() */
    if (n.peak === null || value > n.peak) { n.peak = value; }
    if (n.half) {
      n.low = n.low === null ? value : Math.min(n.low, value);
      if (value >= n.peak - (n.peak - n.low) / 2 - 1e-9) { n.half = false; n.low = null; }   /* half of the deepest drop recovered */
    }
    var dd = (n.peak - value) / n.peak * 100;
    if (dd >= c.ddMax - 1e-9) { n.stopped = true; n.half = false; n.low = null; }
    else if (!n.half && dd >= c.ddHalf - 1e-9) { n.half = true; n.low = value; }
    return n;
  }
  function lossResume(st, value, note) {
    if (!(typeof note === 'string' && note.trim().length > 0)) return fail('NOTE_REQUIRED');
    if (!(num(value) && value > 0)) return fail('NO_VALUE');
    return { ok: true, state: { peak: value, half: false, low: null, stopped: false } };
  }
  /* closed ideas -> loss units.
     items = [{gid, idea, t(ms), pnl (money, negative = loss), risk (planned money), rMoney}]
     one idea group (gid = position group incl. partial exits) counts when net pnl < 0 and loss > ¼ planned risk (scratch/breakeven ignored)
     the same idea across accounts (idea key) counts once (largest loss in R units). Only items with t >= startMs. */
  function lossUnits(o) {
    o = o || {}; var items = o.items || [], now = o.now, startMs = num(o.startMs) ? o.startMs : 0, g = {}, order = [];
    items.forEach(function (it) {
      if (!num(it.t) || it.t < startMs || !num(it.pnl) || !(num(it.rMoney) && it.rMoney > 0)) return;
      var k = String(it.gid); if (!g[k]) { g[k] = { idea: it.idea || k, pnl: 0, risk: 0, t: 0, r: it.rMoney }; order.push(k); }
      g[k].pnl += it.pnl; g[k].risk += num(it.risk) ? it.risk : 0; g[k].t = Math.max(g[k].t, it.t);
    });
    var byIdea = {};
    order.forEach(function (k) {
      var x = g[k]; if (!(x.pnl < 0) || !(-x.pnl > x.risk / 4 + 1e-9)) return;
      var u = -x.pnl / x.r, cur = byIdea[x.idea];
      if (!cur) byIdea[x.idea] = { units: u, t: x.t }; else { if (u > cur.units) cur.units = u; if (x.t > cur.t) cur.t = x.t; }
    });
    var ds = dayStart(now), ws = weekStart(now), day = 0, week = 0, nDay = 0, nWeek = 0;
    Object.keys(byIdea).forEach(function (k) {
      var b = byIdea[k]; if (b.t >= ws) { week += b.units; nWeek++; } if (b.t >= ds) { day += b.units; nDay++; }
    });
    return { day: day, week: week, nDay: nDay, nWeek: nWeek, dayEnd: ds + DAY, weekEnd: ws + 7 * DAY };
  }
  /* status of one port. port = 'ladder'|'winner'|'sat' · st = lossStep result · units = lossUnits result (null for ladder) */
  function lossStatus(o) {
    o = o || {}; var c = lossCfg(o.cfg), st = o.state || {}, u = o.units, port = o.port;
    var dd = (num(st.peak) && st.peak > 0 && num(o.value)) ? Math.max(0, (st.peak - o.value) / st.peak * 100) : 0;
    var r = { port: port, ddPct: dd, mult: 1, blocked: false, status: 'normal', label: 'Normal', until: null, reason: '', dayR: u ? u.day : 0, weekR: u ? u.week : 0, cfg: c };
    var hasRW = port === 'winner' || port === 'sat';
    if (st.stopped) { r.status = 'review'; r.label = 'Stop & review'; r.blocked = true; r.reason = 'Down ' + dd.toFixed(1) + '% from peak (limit ' + c.ddMax + '%) — press "Reviewed — resume"'; return r; }
    if (hasRW && u && u.week >= c.weekR - 1e-9) { r.status = 'week'; r.label = 'Stop week'; r.blocked = true; r.until = u.weekEnd; r.reason = 'Week loss ' + u.week.toFixed(1) + 'R ≥ ' + c.weekR + 'R'; return r; }
    if (hasRW && u && u.day >= c.dayR - 1e-9) { r.status = 'day'; r.label = 'Stop today'; r.blocked = true; r.until = u.dayEnd; r.reason = 'Day loss ' + u.day.toFixed(1) + 'R ≥ ' + c.dayR + 'R'; return r; }
    if (st.half) { r.status = 'half'; r.label = 'Half size'; r.mult = 0.5; r.reason = 'Down ' + dd.toFixed(1) + '% from peak — risk × 0.5'; }
    return r;
  }

  return { minStopCheck: minStopCheck, portPct: portPct, lossCfg: lossCfg, lossCfgErrors: lossCfgErrors, lossStep: lossStep, lossResume: lossResume, lossUnits: lossUnits, lossStatus: lossStatus, dayStart: dayStart, weekStart: weekStart, LOSS_DEF: LOSS_DEF,
    BUCKETS: BUCKETS, TOTAL_CAP: TOTAL_CAP, MAX_ROWS: MAX_ROWS, cfg: cfg, cfgErrors: cfgErrors, blendStop: blendStop, planSize: planSize,
    capCheck: capCheck, addOnBudget: addOnBudget, addOnQty: addOnQty, satLots: satLots, positionRisk: positionRisk, gbLevel: gbLevel, panel: panel, floorLot: floorLot };
});
