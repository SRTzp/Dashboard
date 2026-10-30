/* core-size.js — เครื่องคิดขนาดไม้ Core (ฟังก์ชันบริสุทธิ์ · ไม่อ่าน DOM/เวลา/ที่เก็บข้อมูล)
   กติกา = claude/core-risk-framework.md · สเปกการ์ด = claude/7E-card-spec.md
   ใช้ 2 ทาง: Node (module.exports) สำหรับเทส · เบราว์เซอร์ (globalThis.CoreSize) → 7E-1 ผูกเป็น Calc.coreSize
   ทุกฟังก์ชัน: รับ object เดียว → คืน object · ข้อมูลผิด/ขาด → คืน {ok:false, err:'รหัส'} ไม่ throw
   ตัวเลขเงินคืนค่าดิบ (ไม่ปัดเศษ) — ปัดที่การแสดงผล ยกเว้น "จำนวนหุ้น" ที่ปัดลงตามล็อตเสมอ
   v2 (30 ก.ย. ค่ำ): +เงินสดคุมไม้ W · L เฉพาะ Tier A · สถานะบันได bought/wait/cancelled · ยกเลิกระดับอัตโนมัติเมื่อ Stop เลย
                      · ชั้น 2 รวมบันไดที่จอง · ประตูเปิดบันไดใหม่ (f) · งบ W/L · จัด Tier */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.CoreSize = factory();
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  var EPS = 1e-9;
  var DEFAULTS = {
    riskPct: 0.01,        // งบเสี่ยงต่อตัว (W) % ของ "ทั้งถัง" (× f)
    tierCap: { A: 0.15, B: 0.10 },  // เพดานไม้แรก % ของถัง (CZ1: A 15 · B 10)
    tierRisk: { A: 0.0125, B: 0.0125 },  // CZ1: Risk/ไม้ % ของถัง แยก Tier (ค่าเริ่ม · ผู้เรียกส่ง riskPct ตาม Tier)
    stockCap: { A: 0.25, B: 0.25 },      // CZ1: เพดานรวม/หุ้น % ของถัง (ทุน cost basis)
    addRatio: 0.5,        // ไม้เติม = 50% ของไม้ก่อนหน้า
    ladderBudget: 0.10,   // L: งบเงินต่อตัว % ของถัง
    ladderRiskCap: 0.025, // L: ความเสี่ยงเต็มบันได % ของถัง
    ladderShareCap: 0.30, // L: งบรวมทุกตัว (ถือ + จอง) % ของถัง — ตายตัว
    layer2Cap: 0.20, layer2Warn: 0.15,
    emergencyPct: 0.07,   // Stop ฉุกเฉิน = Stop × (1 − 7%)
    staleDays: 7,
    gateStreak: 2,        // เปิดบันไดใหม่: f < 100% ติดกัน 2 สัปดาห์
    /* เกณฑ์ Tier · คีย์ระดับบน = A-Fortress (Mature) · growth = A-Growth (High Growth) — TIER2 */
    tier: { roicMin: 0.12, ndEbitdaMax: 2, fcfConvMin: 0.8, growth: { revGrowthMin: 0.20, revCagr3Min: 0.15, ndEbitdaMax: 3 } }
  };
  var SPLIT = { 2: [0.5, 0.5], 3: [0.4, 0.3, 0.3] };

  function num(x) { return typeof x === 'number' && isFinite(x); }
  function fail(err) { return { ok: false, err: err }; }
  function lotOf(market, lot) { return num(lot) && lot > 0 ? lot : (market === 'TH' ? 100 : 1); }
  /* ปัดลงตามล็อต (ไม่ปัดขึ้นเด็ดขาด) · EPS กัน 699.9999999 จากทศนิยม */
  function floorLot(q, lot) {
    if (!num(q) || q <= 0) return 0;
    lot = lot > 0 ? lot : 1;
    return Math.floor(q / lot + EPS) * lot;
  }

  /* ── ชั้น 1 · W ไม้แรก ──
     qty = ปัดล็อต( min( ถัง × งบเสี่ยง × f ÷ (Entry − Stop) , ถัง × เพดานTier ÷ Entry , ถัง × เพดานรวม/หุ้น ÷ Entry , เงินสดว่าง ÷ Entry ) )
     cash = เงินสดว่างของถัง (ดู portfolioSplit) · ไม่ส่ง = ไม่คุมด้วยเงินสด · cashLimited = เงินสดเป็นตัวคุม */
  function firstLot(o) {
    o = o || {};
    var tank = o.tank, e = o.entry, s = o.stop;
    if (!(num(tank) && tank > 0)) return fail('NO_TANK');
    if (!(num(e) && num(s) && s > 0 && e > s)) return fail('BAD_PRICES');
    var f = num(o.f) ? o.f : 1;
    var riskPct = num(o.riskPct) ? o.riskPct : DEFAULTS.riskPct;
    var capPct = num(o.tierCapPct) ? o.tierCapPct : DEFAULTS.tierCap[o.tier || 'A'];
    var stockPct = num(o.stockCapPct) ? o.stockCapPct : DEFAULTS.stockCap[o.tier || 'A'];
    var lot = lotOf(o.market, o.lot);
    var budgetFull = tank * riskPct, budget = budgetFull * f;
    /* LN3fix2 — lotRisk (เศษส่วนของถัง) = Risk % ที่ผู้ใช้ใส่ให้ไม้แรก: ขนาด = lotRisk × ถัง ÷ (Entry − Stop) · ไม่ส่ง = สูตรเดิม (งบ × f) · overBudget = ใส่เกินงบ (ผู้เรียกบล็อก) */
    var hasLotRisk = num(o.lotRisk) && o.lotRisk > 0;
    var byRisk = (hasLotRisk ? tank * o.lotRisk : budget) / (e - s), byCap = tank * capPct / e, byStock = tank * stockPct / e;
    var hasCash = num(o.cash);
    var byCash = hasCash ? Math.max(0, o.cash) / e : Infinity;
    var base = Math.min(byRisk, byCap, byStock);
    var cashLimited = hasCash && byCash < base - EPS;
    var stockCapped = byStock < Math.min(byRisk, byCap) - EPS;   // เพดานรวม/หุ้นเป็นตัวคุม (CZ1)
    var qty = floorLot(Math.min(base, byCash), lot);
    return {
      ok: true, qty: qty, lot: lot, budgetFull: budgetFull, budget: budget,
      byRisk: byRisk, byCap: byCap, byStock: byStock, byCash: hasCash ? byCash : null,
      capped: byCap < byRisk && !stockCapped, stockCapped: stockCapped, cashLimited: cashLimited,
      cost: qty * e, risk: qty * (e - s),
      costPct: qty * e / tank, riskPctTank: qty * (e - s) / tank,
      zeroLot: qty === 0,   // ปัดแล้วเหลือ 0 → การ์ดห้ามบันทึกซื้อ
      maxRisk: budget / tank, overBudget: hasLotRisk && o.lotRisk > budget / tank + EPS
    };
  }

  /* ── ชั้น 1 · W ไม้เติม ──
     เป้า = ไม้ก่อนหน้า × 50% · ค้าง = ถือ × max(0, ทุนเฉลี่ย − Stop) · เติมได้เมื่อ ค้าง + ไม้ใหม่ ≤ งบเสี่ยง × f · และไม่เกินเงินสดว่าง
     tag: normal | risk_limited | cash_limited (เงินสดคุม) | move_stop (ความเสี่ยงไม่พอ → เลื่อน Stop ขึ้นก่อน) | too_small (เป้า 50% ต่ำกว่า 1 ล็อต)
          | stock_capped (เพดานรวม/หุ้นคุม · ซื้อได้ > 0) | stock_full (เพดานรวม/หุ้นเต็ม · ซื้อไม่ได้) — CZ1 · ส่ง o.stockCapPct (เศษส่วนของถัง) · ไม่ส่ง = ไม่จำกัด
     เพดานรวม/หุ้นคิดจากทุน (cost basis): ถือ × ทุนเฉลี่ย + ไม้ใหม่ × ราคา ≤ ถัง × เพดานรวม */
  function addLot(o) {
    o = o || {};
    var tank = o.tank, px = o.price, s = o.stop;
    if (!(num(tank) && tank > 0)) return fail('NO_TANK');
    if (!(num(px) && num(s) && s > 0 && px > s)) return fail('BAD_PRICES');
    /* LN3fix2 — layer 'acc' = ไม้เร่ง: ชั้นเร่งยังว่างได้ (heldQty 0) · base/ไม่ส่ง = กติกาเดิม */
    var layer = o.layer === 'acc' ? 'acc' : 'base';
    var held = o.heldQty, avg = o.avgCost;
    if (layer === 'acc' && !(num(held) && held > 0)) { held = 0; avg = 0; }
    else if (!(num(held) && held > 0 && num(avg) && avg > 0)) return fail('NO_POSITION');
    var hasLotRisk = num(o.lotRisk) && o.lotRisk > 0;   // ผู้ใช้ใส่ Risk % ต่อไม้ (เศษส่วนของถัง) → โหมดใหม่
    var prev = num(o.prevLotQty) && o.prevLotQty > 0 ? o.prevLotQty : held;
    var f = num(o.f) ? o.f : 1;
    var riskPct = num(o.riskPct) ? o.riskPct : DEFAULTS.riskPct;
    var ratio = num(o.ratio) ? o.ratio : DEFAULTS.addRatio;
    var lot = lotOf(o.market, o.lot);
    var budget = tank * riskPct * f;
    var carry = held * Math.max(0, avg - s);       // ความเสี่ยงค้าง (Stop เลยทุน = 0) · ของชั้นนี้
    var room = budget - carry;
    var per = px - s;
    var target = (layer === 'acc' && hasLotRisk) ? Infinity : prev * ratio;   // ไม้เร่งไม่ใช้เป้า 50%
    var byRisk = room > 0 ? room / per : 0;
    var wantQty = hasLotRisk ? tank * o.lotRisk / per : target;
    var hasCash = num(o.cash);
    var byCash = hasCash ? Math.max(0, o.cash) / px : Infinity;
    var hasStock = num(o.stockCapPct) && o.stockCapPct > 0;
    var heldCost = num(o.heldCostTotal) ? o.heldCostTotal : held * avg;   // เพดานรวม/หุ้นนับทุนทุกชั้น (ผู้เรียกส่ง heldCostTotal)
    var byStock = hasStock ? Math.max(0, tank * o.stockCapPct - heldCost) / px : Infinity;
    var m = Math.min(hasLotRisk ? wantQty : target, byRisk);
    var stockBinds = hasStock && byStock < m - EPS;
    var cashBinds = hasCash && byCash < Math.min(m, byStock) - EPS;
    var qty = floorLot(Math.min(m, byStock, byCash), lot);
    var tag, lim = hasLotRisk ? wantQty : target;
    if (cashBinds) tag = 'cash_limited';
    else if (stockBinds) tag = qty > 0 ? 'stock_capped' : 'stock_full';
    else if (qty === 0) tag = byRisk < lim ? 'move_stop' : 'too_small';
    else tag = byRisk < lim ? 'risk_limited' : 'normal';
    var newRisk = qty * per;
    var newHeld = held + qty;
    var out = {
      ok: true, qty: qty, lot: lot, tag: tag, budget: budget,
      target: target, byRisk: byRisk, byStock: hasStock ? byStock : null, byCash: hasCash ? byCash : null, carry: carry, newRisk: newRisk, total: carry + newRisk,
      cost: qty * px, newHeld: newHeld, newAvgCost: qty > 0 ? (held * avg + qty * px) / newHeld : avg
    };
    /* LN3fix2 — ฟิลด์ใหม่ (เพิ่มท้าย · ไม่กระทบผู้เรียกเดิม): layer · maxRisk = Risk สูงสุดที่ใส่ได้ (เศษส่วนของถัง) · overRoom · overRatio (เฉพาะ base · เตือน ไม่ตัด qty) */
    out.layer = layer; out.room = room; out.maxRisk = Math.max(0, room) / tank;
    out.overRoom = hasLotRisk && o.lotRisk > out.maxRisk + EPS;
    out.overRatio = layer === 'base' && prev > 0 && qty > prev * ratio + EPS;
    out.riskPctTank = newRisk / tank;
    return out;
  }

  /* ── L · บันไดถัวตามแนวรับ (เฉพาะ Tier A) ──
     levels = [{px, status}] เรียงราคาลง · status: 'wait' (จอง · ค่าเริ่มต้น) | 'bought' | 'cancelled' (ตัดออกจากยอด/สัดส่วน/ความเสี่ยง · ไม่กระจายเงินไประดับอื่น)
     แบ่งเงิน: 3 ระดับ 40/30/30 · 2 ระดับ 50/50 (หรือส่ง split เอง) · ขนาด = ตามงบเงิน ไม่ดูระยะ SL · ไม่ใช้ f
     Tier ไม่ใช่ 'A' (รวมไม่ส่ง = B) → TIER_B_NO_LADDER */
  function ladder(o) {
    o = o || {};
    var tank = o.tank, sl = o.sl, lv = o.levels;
    if (!(num(tank) && tank > 0)) return fail('NO_TANK');
    if (o.tier !== 'A') return fail('TIER_B_NO_LADDER');
    if (!lv || lv.length < 2 || lv.length > 3) return fail('LEVELS_2_3');
    if (!(num(sl) && sl > 0)) return fail('BAD_SL');
    var i;
    for (i = 0; i < lv.length; i++) {
      if (!num(lv[i].px)) return fail('BAD_LEVEL');
      if (i > 0 && !(lv[i].px < lv[i - 1].px)) return fail('LEVELS_NOT_DESC');
      // ตรวจ "ต้องสูงกว่า SL" เฉพาะระดับที่ยังจอง (ระดับที่ซื้อแล้ว/ยกเลิกแล้วอยู่ใต้ Stop ได้ — Stop เลื่อนตาม Higher Low)
      if ((lv[i].status || 'wait') === 'wait' && !(lv[i].px > sl)) return fail('LEVEL_BELOW_SL');
    }
    var split = o.split || SPLIT[lv.length];
    if (split.length !== lv.length) return fail('BAD_SPLIT');
    var sum = 0; for (i = 0; i < split.length; i++) sum += split[i];
    if (Math.abs(sum - 1) > 1e-6) return fail('SPLIT_NOT_100');
    var budgetPct = num(o.budgetPct) ? o.budgetPct : DEFAULTS.ladderBudget;
    var riskCap = num(o.riskCapPct) ? o.riskCapPct : DEFAULTS.ladderRiskCap;
    var lot = lotOf(o.market, o.lot);
    var budget = tank * budgetPct;
    var rows = [], qty = 0, cost = 0, risk = 0, firstRisk = 0, firstIdx = -1;
    var heldQty = 0, heldCost = 0, reservedCost = 0, reservedRisk = 0;
    for (i = 0; i < lv.length; i++) {
      var st = lv[i].status === 'bought' ? 'bought' : (lv[i].status === 'cancelled' ? 'cancelled' : 'wait');
      var cancelled = st === 'cancelled';
      var alloc = budget * split[i];
      var q = cancelled ? 0 : floorLot(alloc / lv[i].px, lot);
      var c = q * lv[i].px, r = q * Math.max(0, lv[i].px - sl);
      rows.push({ px: lv[i].px, alloc: alloc, qty: q, cost: c, risk: r, cancelled: cancelled, status: st });
      qty += q; cost += c; risk += r;
      if (st === 'bought') { heldQty += q; heldCost += c; }
      if (st === 'wait') { reservedCost += c; reservedRisk += r; }
      if (!cancelled && firstIdx < 0) { firstIdx = i; firstRisk = r; }
    }
    var warns = [];
    if (risk / tank > riskCap + EPS) warns.push('RISK_OVER');       // เตือน ไม่บล็อก
    for (i = 0; i < rows.length; i++) if (rows[i].status === 'wait' && rows[i].qty === 0) warns.push('ZERO_LOT_L' + (i + 1));
    var live = 0; for (i = 0; i < rows.length; i++) if (!rows[i].cancelled) live++;
    return {
      ok: true, lot: lot, budget: budget, rows: rows, sl: sl,
      qty: qty, cost: cost, avgCost: qty > 0 ? cost / qty : null,
      fullRisk: risk, fullRiskPct: risk / tank,               // เสี่ยงเต็มบันได (ถือ + จอง) จากราคาระดับถึง SL
      firstRisk: firstRisk, firstRiskPct: firstRisk / tank,   // ซื้อแค่ระดับแรกที่ยังไม่ยกเลิก
      sharePct: cost / tank,                                  // สัดส่วนของตัวนี้ (แผนเต็ม = ถือ + จอง)
      heldQty: heldQty, heldCost: heldCost, reservedCost: reservedCost, reservedRisk: reservedRisk,
      liveLevels: live, warns: warns
    };
  }

  /* เลื่อน Stop ของบันได — เลื่อนขึ้นอย่างเดียว · ระดับที่ยังไม่ซื้อ (wait) ที่ราคา ≤ Stop ใหม่ → ยกเลิกอัตโนมัติ (คืนเงินจอง)
     คืน levels ชุดใหม่ (ไม่แก้ของเดิม) · ended = ไม่เหลือระดับที่ยังไม่ยกเลิก */
  function applyStopMove(o) {
    o = o || {};
    if (!(num(o.sl) && o.sl > 0 && num(o.newSl) && o.newSl > 0)) return fail('BAD_SL');
    if (o.newSl < o.sl) return fail('STOP_DOWN');
    var lv = o.levels || [], out = [], cancelled = [], live = 0, i;
    for (i = 0; i < lv.length; i++) {
      var st = lv[i].status || 'wait';
      var n = { px: lv[i].px, status: st };
      if (st === 'wait' && lv[i].px <= o.newSl + EPS) { n.status = 'cancelled'; cancelled.push(i); }
      if (n.status !== 'cancelled') live++;
      out.push(n);
    }
    return { ok: true, sl: o.newSl, levels: out, cancelled: cancelled, ended: live === 0 };
  }

  /* งบ W / L / เงินว่างของถัง Core (บัญชีเดียว)
     ladders = ผลของ ladder() ทุกตัวที่ยังเปิดอยู่ (จบรอบ = ไม่มีใน list → เงินคืน W) · wCost = ทุนของตำแหน่ง W ที่ถืออยู่ */
  function portfolioSplit(o) {
    o = o || {};
    if (!(num(o.tank) && o.tank > 0)) return fail('NO_TANK');
    var cap = num(o.capPct) ? o.capPct : DEFAULTS.ladderShareCap;
    var lHeld = 0, lRes = 0, i, ls = o.ladders || [];
    for (i = 0; i < ls.length; i++) { lHeld += ls[i].heldCost || 0; lRes += ls[i].reservedCost || 0; }
    var w = num(o.wCost) ? o.wCost : 0;
    var lUsed = lHeld + lRes, raw = o.tank - w - lUsed;
    return {
      ok: true, w: w, lHeld: lHeld, lReserved: lRes, lUsed: lUsed,
      lPct: lUsed / o.tank, lCap: cap, lOver: lUsed / o.tank > cap + EPS,
      cashFree: Math.max(0, raw), overCommitted: raw < -EPS
    };
  }

  /* สัดส่วน L รวมทุกตัว (ถือ + จอง · ตัดระดับที่ cancelled) ≤ 30% ของถัง */
  function ladderShare(o) {
    o = o || {};
    if (!(num(o.tank) && o.tank > 0)) return fail('NO_TANK');
    var cap = num(o.capPct) ? o.capPct : DEFAULTS.ladderShareCap;
    var cost = 0, i, ls = o.ladders || [];
    for (i = 0; i < ls.length; i++) cost += ls[i].cost || 0;
    var pct = cost / o.tank;
    return { ok: true, cost: cost, pct: pct, cap: cap, over: pct > cap + EPS };
  }

  /* ── ชั้น 2 · ความเสี่ยงถึง Stop (รวม W + L) ──
     positions = ที่ถืออยู่ [{qty, px, stop}] → คิดจากราคาปัจจุบัน · px ว่าง = ไม่นับ + missing · px ≤ stop = 0
     reserved  = ระดับบันไดที่จอง (ยังไม่ซื้อ · ไม่ยกเลิก) [{qty, px = ราคาระดับ, stop}] → คิดจากราคาระดับถึง Stop
     risk/pct = ตอนนี้ · riskFull/pctFull = ถ้าบันไดเต็ม · level คิดจาก "เต็ม" (ชั้น 2 นับที่จองด้วย) · levelNow = ตอนนี้ */
  function level2(pct, cap, warn) { return pct > cap + EPS ? 'over' : (pct >= warn - EPS ? 'warn' : 'ok'); }
  function layer2(o) {
    o = o || {};
    if (!(num(o.tank) && o.tank > 0)) return fail('NO_TANK');
    var cap = num(o.cap) ? o.cap : DEFAULTS.layer2Cap, warn = num(o.warn) ? o.warn : DEFAULTS.layer2Warn;
    var ps = o.positions || [], rs = o.reserved || [], risk = 0, missing = 0, value = 0, resRisk = 0, riskAcc = 0, i;
    for (i = 0; i < ps.length; i++) {
      var p = ps[i];
      if (!(num(p.px) && p.px > 0)) { missing++; continue; }
      var pr = p.qty * Math.max(0, p.px - p.stop);   // LN3fix2 — position.layer = 'acc' (ไม้เร่ง · SL ของชั้นเร่ง) แยกยอดไว้ใน riskAcc · รวมใน risk ตามเดิม
      risk += pr; if (p.layer === 'acc') riskAcc += pr;
      value += p.qty * p.px;
    }
    for (i = 0; i < rs.length; i++) resRisk += rs[i].qty * Math.max(0, rs[i].px - rs[i].stop);
    var pct = risk / o.tank, full = risk + resRisk, pctFull = full / o.tank;
    return {
      ok: true, risk: risk, pct: pct, value: value, missing: missing, cap: cap, warn: warn,
      riskReserved: resRisk, riskFull: full, pctFull: pctFull, riskAcc: riskAcc, riskBase: risk - riskAcc,
      levelNow: level2(pct, cap, warn), level: level2(pctFull, cap, warn)
    };
  }

  /* "ถ้าทุกไม้โดน Stop บัญชีลด ≈ x%" = ความเสี่ยงชั้น 2 (จากราคาปัจจุบัน) รวมทุก port ในบัญชี ÷ ทุนบัญชี */
  function accountDrop(o) {
    o = o || {};
    if (!(num(o.accountCap) && o.accountCap > 0)) return fail('NO_ACCOUNT_CAP');
    var r = 0, i, rs = o.risks || [];
    for (i = 0; i < rs.length; i++) r += rs[i] || 0;
    return { ok: true, risk: r, pct: r / o.accountCap };
  }

  /* ตัวเล็กเทียบทุน: กำไร/ขาดทุนถ้าขายที่ Stop เทียบทุนเฉลี่ย (ค่าบวก = ยังกำไร) */
  function vsCost(o) {
    o = o || {};
    if (!(num(o.qty) && num(o.avgCost) && num(o.stop))) return fail('BAD_INPUT');
    return { ok: true, pnl: o.qty * (o.stop - o.avgCost) };
  }

  function emergencyStop(o) {
    o = o || {};
    if (!(num(o.stop) && o.stop > 0)) return fail('BAD_STOP');
    var pct = num(o.pct) ? o.pct : DEFAULTS.emergencyPct;
    return { ok: true, price: o.stop * (1 - pct) };
  }

  /* ป้ายสถานะ: na(⚪) > red(🔴) > yellow(🟡) > green(🟢) · today/pxDate = 'YYYY-MM-DD' (ส่งเข้ามา ไม่อ่านนาฬิกา) */
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

  /* ── ประตูเปิดบันไดใหม่ (Fund-flow) ──
     fHistory = f รายสัปดาห์ เรียง "ใหม่ → เก่า" · แต่ละค่า = 1 / 0.75 / 0.5 หรือ null (ไม่ทราบ = ไฟล์เก่า/ขาดข้อมูล — ไม่ใช่ 100%)
     เปิดได้เมื่อ f < 100% ติดกันครบ need สัปดาห์ (ค่าเริ่มต้น 2) นับจากสัปดาห์ล่าสุด · null ขาดกลาง = ตัดสาย
     status: unknown (ล่าสุดไม่ทราบ) | green (ล่าสุด 100% → งดเปิดใหม่) | red
     ใช้กับ "เปิดบันไดใหม่" เท่านั้น — บันไดที่มีอยู่ทำงานต่อจนออกเอง */
  function openGate(o) {
    o = o || {};
    var h = o.fHistory || [], need = num(o.need) && o.need > 0 ? o.need : DEFAULTS.gateStreak;
    var newest = h.length ? h[0] : null;
    if (!num(newest)) return { ok: true, open: false, reason: 'unknown', status: 'unknown', streak: 0, need: need };
    if (newest >= 1 - EPS) return { ok: true, open: false, reason: 'green', status: 'green', streak: 0, need: need, f: newest };
    var streak = 0, i;
    for (i = 0; i < h.length; i++) { if (num(h[i]) && h[i] < 1 - EPS) streak++; else break; }
    var open = streak >= need;
    return { ok: true, open: open, reason: open ? 'ok' : 'short_streak', status: 'red', streak: streak, need: need, f: newest };
  }

  /* ── วางบันไดใหม่ได้ไหม (รวมทุกเงื่อนไข · คืนเหตุผลทั้งหมดที่ไม่ผ่าน) ──
     TIER_B · NOT_FORTRESS (o.fortress === false) · GATE_<reason> · BAD_LADDER · L_SHARE_OVER (ถือ+จองรวมใหม่ > 30%) · LAYER2_OVER (ชั้น 2 รวมบันไดใหม่ > 20%) · NO_CASH (ทุนบันไดใหม่ > เงินว่าง) */
  function canPlaceLadder(o) {
    o = o || {};
    var reasons = [];
    if (!(num(o.tank) && o.tank > 0)) return fail('NO_TANK');
    if (o.tier !== 'A') reasons.push('TIER_B');
    if (o.fortress === false) reasons.push('NOT_FORTRESS');   /* TIER2: L ใช้ได้เฉพาะ A-Fortress · ไม่ส่ง = true */
    var g = o.gate || { open: false, reason: 'unknown' };
    if (!g.open) reasons.push('GATE_' + g.reason);
    var nl = o.ladder;
    if (!nl || !nl.ok) { reasons.push('BAD_LADDER'); return { ok: true, allowed: false, reasons: reasons }; }
    var ex = o.existingLadders || [];
    var shareCap = num(o.shareCap) ? o.shareCap : DEFAULTS.ladderShareCap;
    var l2Cap = num(o.l2Cap) ? o.l2Cap : DEFAULTS.layer2Cap;
    var sp = portfolioSplit({ tank: o.tank, wCost: o.wCost, ladders: ex, capPct: shareCap });
    if ((sp.lUsed + nl.cost) / o.tank > shareCap + EPS) reasons.push('L_SHARE_OVER');
    var res = (o.reserved || []).slice(), i;
    for (i = 0; i < nl.rows.length; i++) if (nl.rows[i].status === 'wait') res.push({ qty: nl.rows[i].qty, px: nl.rows[i].px, stop: nl.sl });
    var l2 = layer2({ tank: o.tank, positions: o.positions || [], reserved: res });
    if (l2.pctFull > l2Cap + EPS) reasons.push('LAYER2_OVER');
    if (nl.cost > sp.cashFree + EPS) reasons.push('NO_CASH');
    return { ok: true, allowed: reasons.length === 0, reasons: reasons, pctFull: l2.pctFull, cashFree: sp.cashFree, sharePct: (sp.lUsed + nl.cost) / o.tank };
  }

  /* ── จัด Tier (2 มุม · Damodaran Corporate Life Cycle) ──
     A = ผ่านอย่างน้อย 1 มุม · B = ไม่ผ่านทั้งคู่ · ขาดข้อมูลข้อไหน = ข้อนั้นไม่ผ่าน
     A-Fortress: ROIC > roicMin · ND/EBITDA < ndEbitdaMax · FCF conv > fcfConvMin · fcfPositive3y · capitalReturn · Gate 5 "ไม่" ทั้ง 3
     A-Growth:   revGrowth ≥ growth.revGrowthMin · revCagr3 ≥ growth.revCagr3Min · opMargin > 0 และ ≥ opMarginPrev · ocf > 0
                 · (ndEbitda < growth.ndEbitdaMax หรือ netDebt ≤ 0 / netCash true) · Gate 5 "ไม่" ทั้ง 3
       gate5 = {substitute, customerMigrating, singleProduct} true = ใช่ (ความเสี่ยง) · false = ไม่ · ไม่ตอบ/ขาดข้อมูล = ไม่ผ่าน
     passed/failedNumbers/gate5Yes/gate5Unanswered = ความหมายเดิม (ตัวเลข 3 ข้อฝั่ง Fortress) · lenses = ผลละเอียดแต่ละมุม (failed รหัส:
       roic nd fcf fcf3y capret gate5 | rev cagr opm opm_trend ocf nd_g) · lens = 'fortress'|'growth'|'both'|null ตามผลจริงหลัง override
     ไม่นับ Gate 4 (ราคา) · override {tier, lens, reason}: ยกเป็น A / เลือกมุมที่คำนวณไม่ผ่าน ต้องมีเหตุผล (ไม่ว่าง) ไม่งั้น REASON_REQUIRED · ลดลงไม่ต้องมีเหตุผล */
  function classifyTier(o) {
    o = o || {};
    var T = DEFAULTS.tier, G = T.growth, og = o.growth || {};
    var roicMin = num(o.roicMin) ? o.roicMin : T.roicMin;
    var ndMax = num(o.ndEbitdaMax) ? o.ndEbitdaMax : T.ndEbitdaMax;
    var fcfMin = num(o.fcfConvMin) ? o.fcfConvMin : T.fcfConvMin;
    var revMin = num(og.revGrowthMin) ? og.revGrowthMin : G.revGrowthMin;
    var cagrMin = num(og.revCagr3Min) ? og.revCagr3Min : G.revCagr3Min;
    var ndMaxG = num(og.ndEbitdaMax) ? og.ndEbitdaMax : G.ndEbitdaMax;
    var passed = {
      roic: num(o.roic) && o.roic > roicMin,
      nd: num(o.ndEbitda) && o.ndEbitda < ndMax,
      fcf: num(o.fcfConv) && o.fcfConv > fcfMin
    };
    var failedNumbers = [];
    if (!passed.roic) failedNumbers.push('roic');
    if (!passed.nd) failedNumbers.push('nd');
    if (!passed.fcf) failedNumbers.push('fcf');
    var g5 = o.gate5 || {}, keys = ['substitute', 'customerMigrating', 'singleProduct'], yes = [], unans = [], i;
    for (i = 0; i < keys.length; i++) {
      if (g5[keys[i]] === true) yes.push(keys[i]);
      else if (g5[keys[i]] !== false) unans.push(keys[i]);
    }
    var g5ok = yes.length === 0 && unans.length === 0;
    var fFailed = failedNumbers.slice();
    if (o.fcfPositive3y !== true) fFailed.push('fcf3y');
    if (o.capitalReturn !== true) fFailed.push('capret');
    if (!g5ok) fFailed.push('gate5');
    var gFailed = [];
    if (!(num(o.revGrowth) && o.revGrowth >= revMin - EPS)) gFailed.push('rev');
    if (!(num(o.revCagr3) && o.revCagr3 >= cagrMin - EPS)) gFailed.push('cagr');
    if (!(num(o.opMargin) && o.opMargin > 0)) gFailed.push('opm');
    if (!(num(o.opMargin) && num(o.opMarginPrev) && o.opMargin >= o.opMarginPrev - EPS)) gFailed.push('opm_trend');
    if (!(o.ocf === true || (num(o.ocf) && o.ocf > 0))) gFailed.push('ocf');
    if (!((num(o.ndEbitda) && o.ndEbitda < ndMaxG) || (num(o.netDebt) && o.netDebt <= 0) || o.netCash === true)) gFailed.push('nd_g');
    if (!g5ok) gFailed.push('gate5');
    var lenses = { fortress: { pass: fFailed.length === 0, failed: fFailed }, growth: { pass: gFailed.length === 0, failed: gFailed } };
    var lensOf = function (f, g) { return f && g ? 'both' : f ? 'fortress' : g ? 'growth' : null; };
    var computedLens = lensOf(lenses.fortress.pass, lenses.growth.pass);
    var computed = computedLens ? 'A' : 'B';
    var tier = computed, lens = computedLens, overridden = false, reason = '';
    var ov = o.override;
    if (ov && (ov.tier === 'A' || ov.tier === 'B')) {
      if (ov.tier === 'B') {
        if (computed !== 'B') { tier = 'B'; lens = null; overridden = true; reason = typeof ov.reason === 'string' ? ov.reason.trim() : ''; }
      } else {
        var want = (ov.lens === 'fortress' || ov.lens === 'growth' || ov.lens === 'both') ? ov.lens : (computed === 'A' ? computedLens : 'fortress');
        var needF = want !== 'growth', needG = want !== 'fortress';
        var unsupported = (needF && !lenses.fortress.pass) || (needG && !lenses.growth.pass);
        if (unsupported) {
          reason = typeof ov.reason === 'string' ? ov.reason.trim() : '';
          if (!reason) return { ok: false, err: 'REASON_REQUIRED', tier: computed, computed: computed };
        }
        if (computed !== 'A' || want !== computedLens) { tier = 'A'; lens = want; overridden = true; }
        if (!overridden) reason = '';
      }
    }
    return { ok: true, tier: tier, computed: computed, passed: passed, failedNumbers: failedNumbers, gate5Yes: yes, gate5Unanswered: unans,
      overridden: overridden, reason: reason, lenses: lenses, lens: lens, computedLens: computedLens };
  }


  /* ── ป้าย Tier เทียบ Watchlist (เตือนอย่างเดียว · ไม่ล็อก · ไม่เปลี่ยน Tier เอง) ──
     cardTier = 'A'|'B' ของการ์ด · watch = {loaded, found, tier ('A'|'B'|null), setAt ('YYYY-MM-DD'|null)} · today = 'YYYY-MM-DD'
     คืน badges[{code, level:'warn'|'muted', text}] — ว่าง = ไม่มีอะไรต้องแสดง
     โหลด Watchlist ไม่ได้ (loaded ≠ true) = ไม่เตือนเรื่อง Tier เลย
     การ์ด A: ไม่อยู่ WL → warn · WL ไม่มี Tier → warn · WL = B → warn · WL = A และ setAt เกิน 12 เดือน → muted ทบทวน
     การ์ด B: ไม่เตือน · muted "Watchlist = A" / "ไม่อยู่ใน Watchlist" */
  function tierBadge(o) {
    o = o || {};
    var w = o.watch || {}, out = [];
    if (w.loaded !== true) return { ok: true, badges: out };
    if (o.cardTier === 'A') {
      if (!w.found) out.push({ code: 'NOT_IN_WATCHLIST', level: 'warn', text: 'ไม่อยู่ใน Watchlist · ยังไม่ได้ทำการบ้าน' });
      else if (w.tier !== 'A' && w.tier !== 'B') out.push({ code: 'NO_WL_TIER', level: 'warn', text: 'ยังไม่ได้ตั้ง Tier ใน Watchlist' });
      else if (w.tier === 'B') out.push({ code: 'WL_B', level: 'warn', text: 'Watchlist = B · การ์ดยังเป็น A' });
      else if (isOlderThanMonths(w.setAt, o.today, 12)) out.push({ code: 'REVIEW', level: 'muted', text: 'ทบทวน Tier (ตั้งเมื่อ ' + w.setAt + ')' });
    } else {
      if (!w.found) out.push({ code: 'NOT_IN_WATCHLIST', level: 'muted', text: 'ไม่อยู่ใน Watchlist' });
      else if (w.tier === 'A') out.push({ code: 'WL_A', level: 'muted', text: 'Watchlist = A' });
    }
    return { ok: true, badges: out };
  }
  /* เกินกี่เดือน = วันนี้เลยวันครบรอบ (setAt + n เดือน) ไปแล้ว · วันที่ผิดรูปแบบ/ขาด = false (ไม่เตือน) */
  function isOlderThanMonths(setAt, today, n) {
    var a = /^(\d{4})-(\d{2})-(\d{2})$/.exec(setAt || ''), b = /^(\d{4})-(\d{2})-(\d{2})$/.exec(today || '');
    if (!a || !b) return false;
    var due = Date.UTC(+a[1], +a[2] - 1 + n, +a[3]), now = Date.UTC(+b[1], +b[2] - 1, +b[3]);
    return isFinite(due) && isFinite(now) && now > due;
  }

  /* ── DD1 · เบรกชั้น 3 (DD ของถัง) — ปกติ → ลดขนาด → พัก → ฟื้นตัว ──
     ฟังก์ชันบริสุทธิ์: ไม่อ่านนาฬิกา (รับ weekKey = วันอาทิตย์ต้นสัปดาห์ปัจจุบัน · today = YYYY-MM-DD จากข้างนอก) · ไม่แตะ DOM/ที่เก็บข้อมูล
     รับ {equity, peak, stage, stageSince, pauseUntil, reviewDone, recoverDd0, weekly:{weekKey:ddPct}, recoverPnl, oneR, cfg:{ddReduce,ddPause,ddPauseWeeks,ddRecoverR}, weekKey, today}
       recoverPnl = กำไรสุทธิจากไม้ที่ปิดตั้งแต่เข้า recover (เงินเดียวกับ oneR) · oneR = 1R = RPT ปกติ × ถัง
       belowWeeks/pauseWeeks ในเอกสาร brief: คำนวณจาก weekly + cfg.ddPauseWeeks ในฟังก์ชันนี้ (ไม่ให้ผู้เรียกนับเอง)
     คืน state ใหม่ (peak, stage, stageSince, pauseUntil, reviewDone, recoverDd0, weekly) + {ddPct, sizeFactor, allowNew, allowLadder, reasons[], entered, info{}}
     ตีความ (จดในรายงาน DD1):
       · "ติดกัน 2 สัปดาห์" = สัปดาห์ที่จบแล้ว 2 สัปดาห์ล่าสุดติดกันตามปฏิทิน (weekKey−7, weekKey−14) ที่ DD < ddReduce และต้องเป็นสัปดาห์หลังสัปดาห์ที่เข้าสถานะนั้น · DD ตอนนี้ต้อง < ddReduce ด้วย (กันเด้งกลับ)
       · พักซ้ำ (stage recover หรือ reduce ที่ต่อมาจาก recover = มี recoverDd0): DD ≥ ddPause และ DD ≥ recoverDd0 + repauseGapPct (1R เป็น % ของ RPT ปกติ · ไม่ส่ง = 0 → "ลึกกว่า recoverDd0")
         recoverDd0 = DD ตอนออกจากพัก · เก็บตลอด recover และ reduce ที่ต่อมา · ล้างเมื่อ normal/pause — กัน deadlock ถ้าออกจากพักตอน DD ยัง ≥ 20 และกันพักซ้ำเพราะลึกขึ้นนิดเดียว
       · ออกจาก recover (+2R หรือ 2 สัปดาห์ติดกัน): DD ≥ ddReduce → reduce ทันทีในรอบเดียวกัน (stageSince = วันนี้) · ต่ำกว่า → normal */
  var DD_STAGES = ['normal', 'reduce', 'pause', 'recover'];
  function ddIsDate(s) { return typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s); }
  function ddUtc(s) { return Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10)); }
  function ddAddDays(s, n) {
    var d = new Date(ddUtc(s) + n * 86400000), p = function (x) { return (x < 10 ? '0' : '') + x; };
    return d.getUTCFullYear() + '-' + p(d.getUTCMonth() + 1) + '-' + p(d.getUTCDate());
  }
  function ddDaysBetween(a, b) { return Math.round((ddUtc(b) - ddUtc(a)) / 86400000); }
  function ddWeekOf(s) { return ddAddDays(s, -new Date(ddUtc(s)).getUTCDay()); }   // อาทิตย์ต้นสัปดาห์ (ตรง wpWeekKey)
  function ddStep(o) {
    o = o || {};
    if (!num(o.equity)) return fail('NO_EQUITY');
    if (!ddIsDate(o.weekKey)) return fail('BAD_WEEK');
    var cfg = o.cfg || {};
    var reduceAt = num(cfg.ddReduce) ? cfg.ddReduce : 12.5, pauseAt = num(cfg.ddPause) ? cfg.ddPause : 20;
    var pauseWeeks = num(cfg.ddPauseWeeks) ? cfg.ddPauseWeeks : 2, recoverR = num(cfg.ddRecoverR) ? cfg.ddRecoverR : 2;
    if (!(reduceAt > 0 && reduceAt < pauseAt)) return fail('BAD_CFG');
    var today = ddIsDate(o.today) ? o.today : o.weekKey;
    var peak = (num(o.peak) && o.peak > 0) ? o.peak : o.equity;
    if (o.equity > peak) peak = o.equity;
    var ddPct = peak > 0 ? Math.max(0, (peak - o.equity) / peak * 100) : 0;
    var HI = pauseAt - EPS, LO = reduceAt - EPS;
    // snapshot รายสัปดาห์ (ค่าล่าสุดของสัปดาห์ชนะ · เก็บ 12 สัปดาห์ล่าสุด)
    var weekly = {}, k, src = o.weekly || {};
    for (k in src) if (ddIsDate(k) && num(src[k])) weekly[k] = src[k];
    var prev1 = ddAddDays(o.weekKey, -7), prev2 = ddAddDays(o.weekKey, -14);   // อ่านก่อนเขียนสัปดาห์ปัจจุบัน
    weekly[o.weekKey] = Math.round(ddPct * 100) / 100;
    var keys = Object.keys(weekly).sort().reverse().slice(0, 12), w2 = {};
    keys.forEach(function (x) { w2[x] = weekly[x]; });
    weekly = w2;

    var stage = DD_STAGES.indexOf(o.stage) >= 0 ? o.stage : 'normal';
    var since = ddIsDate(o.stageSince) ? o.stageSince : today;
    var pauseUntil = ddIsDate(o.pauseUntil) ? o.pauseUntil : null;
    var reviewDone = !!o.reviewDone, dd0 = num(o.recoverDd0) ? o.recoverDd0 : null, entered = null;
    var after = ddWeekOf(since);
    var below2 = ddIsDate(prev1) && prev2 > after && num(src[prev1]) && num(src[prev2]) && src[prev1] < reduceAt - EPS && src[prev2] < reduceAt - EPS && ddPct < LO;
    var gap = (num(o.repauseGapPct) && o.repauseGapPct > 0) ? o.repauseGapPct : 0;
    var oneR = num(o.oneR) ? o.oneR : 0, rPnl = num(o.recoverPnl) ? o.recoverPnl : 0;
    function toPause() { stage = 'pause'; since = today; pauseUntil = ddAddDays(today, 7 * pauseWeeks); reviewDone = false; dd0 = null; entered = 'pause'; }
    function deeper() { return dd0 == null || (gap > 0 ? ddPct >= dd0 + gap - EPS : ddPct > dd0 + EPS); }
    function to(st) { stage = st; since = today; entered = st; }
    if (stage === 'normal') {
      if (ddPct >= HI) toPause(); else if (ddPct >= LO) to('reduce');
    } else if (stage === 'reduce') {
      if (ddPct >= HI && deeper()) toPause(); else if (below2) to('normal');
    } else if (stage === 'pause') {
      if (!pauseUntil) pauseUntil = ddAddDays(since, 7 * pauseWeeks);
      if (today >= pauseUntil && reviewDone) { to('recover'); dd0 = ddPct; }
    } else {   // recover
      if (ddPct >= HI && deeper()) toPause();
      else if ((oneR > 0 && rPnl >= recoverR * oneR - EPS) || below2) to(ddPct >= LO ? 'reduce' : 'normal');
    }
    if (stage !== 'pause') pauseUntil = null;
    if (stage !== 'recover' && stage !== 'reduce') dd0 = null;
    var reasons = [];
    if (stage === 'reduce') reasons.push('DD_REDUCE');
    if (stage === 'pause') reasons.push('DD_PAUSE');
    if (stage === 'recover') reasons.push('DD_RECOVER');
    return {
      ok: true, peak: peak, stage: stage, stageSince: since, pauseUntil: pauseUntil, reviewDone: stage === 'pause' ? reviewDone : false,
      recoverDd0: dd0, weekly: weekly, ddPct: ddPct,
      sizeFactor: stage === 'normal' ? 1 : (stage === 'pause' ? 0 : 0.5), allowNew: stage !== 'pause', allowLadder: stage === 'normal',
      reasons: reasons, entered: entered,
      info: { pauseLeftDays: (stage === 'pause' && pauseUntil) ? Math.max(0, ddDaysBetween(today, pauseUntil)) : null, timeDone: stage === 'pause' && !!pauseUntil && today >= pauseUntil,
              recoverNeed: recoverR * oneR, recoverPnl: rPnl, reduceAt: reduceAt, pauseAt: pauseAt, belowWeeks: below2 }
    };
  }

  return {
    DEFAULTS: DEFAULTS, floorLot: floorLot,
    firstLot: firstLot, addLot: addLot, ladder: ladder, applyStopMove: applyStopMove,
    portfolioSplit: portfolioSplit, ladderShare: ladderShare, layer2: layer2,
    accountDrop: accountDrop, vsCost: vsCost, emergencyStop: emergencyStop, status: status,
    openGate: openGate, canPlaceLadder: canPlaceLadder, classifyTier: classifyTier, tierBadge: tierBadge,
    ddStep: ddStep, ddWeekOf: ddWeekOf, ddAddDays: ddAddDays, ddDaysBetween: ddDaysBetween
  };
});
