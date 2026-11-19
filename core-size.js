/* core-size.js — allocation + position-state helpers for Core (pure functions · no DOM / clock / storage)
   AU1: this module no longer SIZES anything. Every size, risk, lot, heat and drawdown number comes from the risk engine (RE1: risk-engine.js + re1-adapter.js + pos-view.js).
   What stays (read-only, no sizing use):
     poolSplit  — capital allocation: total + % {winner, ladder, sat} → ฿ per pool (Port pool lines, Settings hint)
     poolFree   — free cash of ONE pool = pool − held − reserved (Port "free cash")
     status     — position-health dot: na / red / yellow / green from price vs stop vs EMA (Today sell / stale-price / green signals)
   Used two ways: Node (module.exports) for tests · browser (globalThis.CoreSize → Calc.coreSize). Every function takes one object and returns one object;
   bad / missing input → {ok:false, err:'CODE'} (never throws). */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.CoreSize = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var EPS = 1e-9;
  var DEFAULTS = {
    poolSplit: { winner: 50, ladder: 30, sat: 20 },   // % of the account (sums to 100)
    staleDays: 7
  };

  function num(x) { return typeof x === 'number' && isFinite(x); }
  function fail(err) { return { ok: false, err: err }; }

  /* status badge: na(⚪) > red(🔴) > yellow(🟡) > green(🟢) · today/pxDate = 'YYYY-MM-DD' (passed in, no clock) */
  function status(o) {
    o = o || {};
    var age = null;
    if (o.today && o.pxDate) {
      var a = Date.parse(o.today + 'T00:00:00Z'), b = Date.parse(o.pxDate + 'T00:00:00Z');
      if (isFinite(a) && isFinite(b)) age = Math.round((a - b) / 86400000);
    }
    var stale = num(o.staleDays) ? o.staleDays : DEFAULTS.staleDays;
    if (!(num(o.px) && o.px > 0) || age === null || age > stale) return { ok: true, status: 'na', age: age };
    if (num(o.stop) && o.px < o.stop) return { ok: true, status: 'red', age: age };
    if (num(o.ema10) && o.px < o.ema10) return { ok: true, status: 'yellow', age: age };
    return { ok: true, status: 'green', age: age };
  }

  /* poolSplit: total (฿) + pct {winner, ladder, sat} (numbers, % summing to 100, each 0–100) → {ok, winner, ladder, sat (฿), pct}
       errors → {ok:false, err:'NO_TOTAL' | 'BAD_PCT' | 'SUM_NOT_100'} · no pct = 50/30/20 */
  function poolSplit(o) {
    o = o || {};
    if (!(num(o.total) && o.total > 0)) return fail('NO_TOTAL');
    var p = o.pct || DEFAULTS.poolSplit, k = ['winner', 'ladder', 'sat'], i, sum = 0;
    for (i = 0; i < 3; i++) { if (!(num(p[k[i]]) && p[k[i]] >= 0 && p[k[i]] <= 100)) return fail('BAD_PCT'); sum += p[k[i]]; }
    if (Math.abs(sum - 100) > 1e-6) return fail('SUM_NOT_100');
    return { ok: true, total: o.total, winner: o.total * p.winner / 100, ladder: o.total * p.ladder / 100, sat: o.total * p.sat / 100,
      pct: { winner: p.winner, ladder: p.ladder, sat: p.sat } };
  }

  /* free cash of one pool = pool − held − reserved (other pools untouched) · over = used more than the pool (warn only) */
  function poolFree(o) {
    o = o || {};
    if (!(num(o.pool) && o.pool >= 0)) return fail('NO_POOL');
    var held = num(o.held) ? o.held : 0, res = num(o.reserved) ? o.reserved : 0, raw = o.pool - held - res;
    return { ok: true, pool: o.pool, held: held, reserved: res, used: held + res, free: Math.max(0, raw), over: raw < -EPS,
      usedPct: o.pool > 0 ? (held + res) / o.pool : 0 };
  }

  return { DEFAULTS: DEFAULTS, poolSplit: poolSplit, poolFree: poolFree, status: status };
});
