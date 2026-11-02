/* tests/core_size_test.js — เทส core-size.js ด้วยตัวเลขจาก claude/core-risk-framework.md
   รัน: node tests/core_size_test.js   (ไม่ต้องติดตั้งอะไร · ไม่แตะ index.html) */
'use strict';
var path = require('path');
var C = require(path.join(__dirname, '..', 'core-size.js'));

var pass = 0, fail = 0;
function eq(name, got, want) {
  var ok = got === want;
  if (ok) pass++; else { fail++; console.log('FAIL  ' + name + '  got=' + got + '  want=' + want); }
}
function near(name, got, want, tol) {
  var ok = typeof got === 'number' && Math.abs(got - want) <= (tol == null ? 1e-6 : tol);
  if (ok) pass++; else { fail++; console.log('FAIL  ' + name + '  got=' + got + '  want=' + want); }
}
function section(s) { console.log('— ' + s); }

/* ───────── W ไม้แรก · ถัง 700,000 · Entry 100 · Stop 90 · Tier A 10% ───────── */
section('W ไม้แรก');
function first(f, market) { return C.firstLot({ tank: 700000, entry: 100, stop: 90, f: f, tier: 'A', market: market }); }
eq('US f100 = 700', first(1, 'US').qty, 700);
eq('US f75 = 525', first(0.75, 'US').qty, 525);
eq('US f50 = 350', first(0.5, 'US').qty, 350);
eq('TH f100 = 700', first(1, 'TH').qty, 700);
eq('TH f75 = 500 (ปัดลง)', first(0.75, 'TH').qty, 500);
eq('TH f50 = 300 (ปัดลง)', first(0.5, 'TH').qty, 300);
near('งบเสี่ยงเต็ม 7,000', first(1, 'US').budgetFull, 7000);
near('f75 งบ 5,250', first(0.75, 'US').budgetFull * 0.75, 5250);
near('ไม้แรก f100 เสี่ยง 7,000', first(1, 'US').risk, 7000);
near('ไม้แรก f100 = 1% ของถัง', first(1, 'US').riskPctTank, 0.01);
eq('f100 ไม่ชนเพดาน (เท่ากันพอดี)', first(1, 'US').capped, false);
// ชนเพดาน Tier: Stop 95 → byRisk 1400 > cap 700
var capd = C.firstLot({ tank: 700000, entry: 100, stop: 95, f: 1, tier: 'A', tierCapPct: 0.10 });   // CZ1: DEFAULTS.tierCap เปลี่ยนเป็น A15/B10 → ส่งค่าเดิม (10%) ตรง
eq('Stop ใกล้ → ชนเพดาน Tier A = 700', capd.qty, 700);
eq('ชนเพดาน flag', capd.capped, true);
eq('Tier B (5%) ชนเพดาน = 350', C.firstLot({ tank: 700000, entry: 100, stop: 95, f: 1, tier: 'B', tierCapPct: 0.05 }).qty, 350);   // CZ1: ส่ง 5% ตรง
eq('tierCapPct ส่งเอง 8% = 560', C.firstLot({ tank: 700000, entry: 100, stop: 95, f: 1, tierCapPct: 0.08 }).qty, 560);
eq('งบเสี่ยงปรับ 2% = 1400 → ชนเพดาน 700', C.firstLot({ tank: 700000, entry: 100, stop: 90, riskPct: 0.02, tier: 'A', tierCapPct: 0.10 }).qty, 700);   // CZ1: ส่ง 10% ตรง
// ── CZ1 · เพดานรวม/หุ้น + DEFAULTS ใหม่ ──
section('CZ1 firstLot · เพดานรวม/หุ้น');
var sc = C.firstLot({ tank: 100000, entry: 100, stop: 99, f: 1, tier: 'A', tierCapPct: 0.30, stockCapPct: 0.25 });
eq('เพดานรวม 25% (เพดานไม้แรก 30%, Stop แคบ) = 250', sc.qty, 250);
eq('stockCapped true', sc.stockCapped, true);
eq('capped false (เพดานรวมคุมก่อน)', sc.capped, false);
eq('byStock = 250', Math.round(sc.byStock), 250);
eq('ไม่ชนเพดานรวม → stockCapped false', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A' }).stockCapped, false);
eq('DEFAULTS tier B ไม่ส่ง tierCapPct → ใช้ 10%', C.firstLot({ tank: 700000, entry: 100, stop: 99, f: 1, tier: 'B', stockCapPct: 1 }).qty, 700);
eq('DEFAULTS tier A ไม่ส่ง tierCapPct → ใช้ 15%', C.firstLot({ tank: 700000, entry: 100, stop: 99, f: 1, tier: 'A', stockCapPct: 1 }).qty, 1050);
eq('DEFAULTS.tierCap = A15/B10', C.DEFAULTS.tierCap.A + '/' + C.DEFAULTS.tierCap.B, '0.15/0.1');
eq('DEFAULTS.tierRisk = 1.25% ทั้งสอง', C.DEFAULTS.tierRisk.A + '/' + C.DEFAULTS.tierRisk.B, '0.0125/0.0125');
eq('DEFAULTS.stockCap = 25% ทั้งสอง', C.DEFAULTS.stockCap.A + '/' + C.DEFAULTS.stockCap.B, '0.25/0.25');
eq('ไม่ส่ง stockCapPct ใช้ DEFAULTS 25% (tier B · เพดานไม้แรก 100%)', C.firstLot({ tank: 100000, entry: 100, stop: 99, f: 1, tier: 'B', tierCapPct: 1 }).qty, 250);
eq('เพดานรวมคุมไม้แรกพร้อมเงินสด: เงินสดน้อยกว่า → cashLimited', C.firstLot({ tank: 100000, entry: 100, stop: 99, f: 1, tier: 'A', tierCapPct: 0.30, stockCapPct: 0.25, cash: 10000 }).cashLimited, true);
eq('เพดานรวมไม่เป็นตัวคุมเมื่อเงินสดน้อยกว่า → qty ตามเงินสด 100', C.firstLot({ tank: 100000, entry: 100, stop: 99, f: 1, tier: 'A', tierCapPct: 0.30, stockCapPct: 0.25, cash: 10000 }).qty, 100);
// ปัดเหลือ 0 (TH)
var z = C.firstLot({ tank: 50000, entry: 500, stop: 450, f: 1, market: 'TH' });
eq('TH ถังเล็ก ปัดเหลือ 0', z.qty, 0);
eq('zeroLot flag', z.zeroLot, true);
// ข้อมูลผิด
eq('Entry ≤ Stop → BAD_PRICES', C.firstLot({ tank: 700000, entry: 90, stop: 100 }).err, 'BAD_PRICES');
eq('Entry = Stop → BAD_PRICES', C.firstLot({ tank: 700000, entry: 90, stop: 90 }).err, 'BAD_PRICES');
eq('Stop 0 → BAD_PRICES', C.firstLot({ tank: 700000, entry: 90, stop: 0 }).err, 'BAD_PRICES');
eq('ไม่มีถัง → NO_TANK', C.firstLot({ entry: 100, stop: 90 }).err, 'NO_TANK');
eq('ไม่ส่งอะไร ไม่ throw', C.firstLot().ok, false);

/* ───────── W ไม้เติม · pyramid 700 → 350 → 175 ───────── */
section('W ไม้เติม / pyramid');
var a2 = C.addLot({ tank: 700000, f: 1, price: 115, stop: 100, heldQty: 700, avgCost: 100, prevLotQty: 700 });
eq('ไม้ 2 = 350', a2.qty, 350);
near('ไม้ 2 ค้าง 0 (Stop เท่าทุน)', a2.carry, 0);
near('ไม้ 2 เสี่ยงใหม่ 5,250', a2.newRisk, 5250);
eq('ไม้ 2 tag normal', a2.tag, 'normal');
near('ทุนเฉลี่ยใหม่ 105', a2.newAvgCost, 105);
var a3 = C.addLot({ tank: 700000, f: 1, price: 130, stop: 112, heldQty: 1050, avgCost: 105, prevLotQty: 350 });
eq('ไม้ 3 = 175', a3.qty, 175);
near('ไม้ 3 ค้าง 0 (Stop 112 เลยทุน 105)', a3.carry, 0);
near('ไม้ 3 เสี่ยงใหม่ 3,150', a3.newRisk, 3150);
// รวมหลัง 3 ไม้ + ชั้น 2 ที่ราคา 130 (framework: ≈22,000 / ≈3.2%)
var q3 = 700 + 350 + 175;
eq('รวม 1,225 หุ้น', q3, 1225);
var l2 = C.layer2({ tank: 700000, positions: [{ qty: q3, px: 130, stop: 112 }] });
near('ชั้น 2 = 22,050', l2.risk, 22050);
near('ชั้น 2 ≈ 3.15%', l2.pct, 0.0315, 1e-4);
near('มูลค่า @130 ≈ 159,250 (≈23% ของถัง)', l2.value, 159250);
near('มูลค่า/ถัง ≈ 22.75%', l2.value / 700000, 0.2275, 1e-4);
// ขาดทุนสูงสุดต่อตัวไม่เกินงบ: ไม้ 1+2+3 ถ้าโดน Stop ปัจจุบัน 112 เทียบทุนเฉลี่ย
var avg3 = (700 * 100 + 350 * 115 + 175 * 130) / 1225;
near('ทุนเฉลี่ย 3 ไม้ ≈ 108.57', avg3, 108.5714, 1e-3);
near('Stop 112 เหนือทุนเฉลี่ย → ยังกำไร (เทียบทุน +)', C.vsCost({ qty: 1225, avgCost: avg3, stop: 112 }).pnl, 1225 * (112 - avg3), 1e-6);

// Stop ยังไม่เลื่อน → ความเสี่ยงค้างกินงบหมด
var m0 = C.addLot({ tank: 700000, f: 1, price: 115, stop: 90, heldQty: 700, avgCost: 100, prevLotQty: 700 });
eq('Stop 90 ไม่เลื่อน: ค้าง 7,000 = งบ → เติม 0', m0.qty, 0);
eq('tag move_stop', m0.tag, 'move_stop');
// Stop 95 → ค้าง 3,500 · เหลือ 3,500 · ต่อหุ้น 20 → 175 < เป้า 350 → ลดให้พอดี
var m1 = C.addLot({ tank: 700000, f: 1, price: 115, stop: 95, heldQty: 700, avgCost: 100, prevLotQty: 700 });
eq('Stop 95: ลดเหลือ 175', m1.qty, 175);
eq('tag risk_limited', m1.tag, 'risk_limited');
near('ค้าง + ใหม่ = 7,000 พอดีงบ', m1.total, 7000);
// f 75% กับไม้เติม
var f75 = C.addLot({ tank: 700000, f: 0.75, price: 115, stop: 100, heldQty: 500, avgCost: 100, prevLotQty: 500, market: 'TH' });
eq('TH f75 ไม้ 2: เป้า 250 → ปัด 200', f75.qty, 200);
eq('tag normal (ปัดล็อตอย่างเดียวไม่ใช่ความเสี่ยงคุม)', f75.tag, 'normal');
var f75b = C.addLot({ tank: 700000, f: 0.75, price: 115, stop: 90, heldQty: 500, avgCost: 100, prevLotQty: 500, market: 'TH' });
eq('TH f75 Stop 90: ค้าง 5,000 เหลือ 250 → 10 หุ้น → ปัด 0', f75b.qty, 0);
eq('tag move_stop', f75b.tag, 'move_stop');
// เป้า 50% ต่ำกว่า 1 ล็อต (TH ไม้ก่อน 100 → 50)
var ts = C.addLot({ tank: 700000, f: 1, price: 130, stop: 120, heldQty: 100, avgCost: 100, prevLotQty: 100, market: 'TH' });
eq('TH เป้า 50 < ล็อต → 0', ts.qty, 0);
eq('tag too_small (ไม่ใช่ move_stop)', ts.tag, 'too_small');
eq('ราคาเติม ≤ Stop → BAD_PRICES', C.addLot({ tank: 700000, price: 95, stop: 100, heldQty: 100, avgCost: 100 }).err, 'BAD_PRICES');
eq('ไม่มีตำแหน่ง → NO_POSITION', C.addLot({ tank: 700000, price: 115, stop: 100 }).err, 'NO_POSITION');
// Stop เลยทุน → ค้าง 0 ไม่ติดลบ
near('Stop เหนือทุน ค้าง = 0 ไม่ติดลบ', C.addLot({ tank: 700000, f: 1, price: 140, stop: 120, heldQty: 700, avgCost: 100, prevLotQty: 700 }).carry, 0);

/* ───────── L · บันได ───────── */
section('CZ1 addLot · เพดานรวม/หุ้น (ทุน)');
var ac1 = C.addLot({ tank: 100000, heldQty: 200, avgCost: 100, price: 110, stop: 105, f: 1, riskPct: 0.05, prevLotQty: 200, stockCapPct: 0.25 });
eq('ถือ 200@100 · เพดาน 25% · px110 → byStock 45.45 → qty 45', ac1.qty, 45);
eq('tag stock_capped', ac1.tag, 'stock_capped');
near('byStock = (25,000−20,000)/110', ac1.byStock, 5000 / 110, 1e-9);
var ac2 = C.addLot({ tank: 100000, heldQty: 250, avgCost: 100, price: 110, stop: 105, f: 1, riskPct: 0.05, prevLotQty: 250, stockCapPct: 0.25 });
eq('ถือ 250@100 · เพดาน 25% → qty 0', ac2.qty, 0);
eq('tag stock_full', ac2.tag, 'stock_full');
var ac3a = C.addLot({ tank: 100000, heldQty: 200, avgCost: 100, price: 110, stop: 105, f: 1, riskPct: 0.05, prevLotQty: 200 });
var ac3b = C.addLot({ tank: 100000, heldQty: 200, avgCost: 100, price: 110, stop: 105, f: 1, riskPct: 0.05, prevLotQty: 200, stockCapPct: undefined });
eq('ไม่ส่ง stockCapPct → ผลเท่าเดิม (ไม่จำกัด · byStock null)', ac3a.byStock === null && ac3a.tag !== 'stock_capped' && ac3a.tag !== 'stock_full', true);
eq('ไม่ส่ง stockCapPct = ส่ง undefined ผลเท่ากันทุก field', JSON.stringify(ac3a), JSON.stringify(ac3b));
eq('เพดานรวมหลวมกว่าเป้า → tag เดิม (normal)', C.addLot({ tank: 100000, heldQty: 200, avgCost: 100, price: 110, stop: 105, f: 1, riskPct: 0.05, prevLotQty: 20, stockCapPct: 0.9 }).tag, 'normal');
eq('ใช้ทุน (cost) ไม่ใช่ราคาตลาด: ถือ 200@100 px 300 → byStock ยังคิดจาก 20,000', Math.round(C.addLot({ tank: 100000, heldQty: 200, avgCost: 100, price: 300, stop: 250, f: 1, riskPct: 0.5, prevLotQty: 200, stockCapPct: 0.25 }).byStock * 300), 5000);

section('L บันได');
var L = C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] });
eq('L1 = 280', L.rows[0].qty, 280);
eq('L2 = 233', L.rows[1].qty, 233);
eq('L3 = 262', L.rows[2].qty, 262);
eq('รวม 775', L.qty, 775);
near('งบ 70,000', L.budget, 70000);
near('เงินแบ่ง L1 = 28,000', L.rows[0].alloc, 28000);
near('เงินแบ่ง L2 = 21,000', L.rows[1].alloc, 21000);
near('เงินแบ่ง L3 = 21,000', L.rows[2].alloc, 21000);
near('ทุนรวม 69,930', L.cost, 69930);
near('ทุนเฉลี่ย = 69,930 / 775', L.avgCost, 69930 / 775, 1e-9);
eq('ทุนเฉลี่ยปัด 2 ตำแหน่ง = 90.23', Math.round(L.avgCost * 100) / 100, 90.23);
near('เสี่ยงเต็มบันได 15,680', L.fullRisk, 15680);
near('≈ 2.24%', L.fullRiskPct, 0.0224, 1e-4);
near('ซื้อแค่ L1 เสี่ยง 8,400', L.firstRisk, 8400);
near('≈ 1.2%', L.firstRiskPct, 0.012, 1e-9);
near('สัดส่วนตัวนี้ ≈ 9.99%', L.sharePct, 0.0999, 1e-4);
eq('เสี่ยงเต็ม 2.24% ≤ 2.5% ไม่เตือน', L.warns.length, 0);
// ไม่ใช้ f: ส่ง f มาก็ไม่เปลี่ยนผล
eq('L ไม่ใช้ f', C.ladder({ tier: 'A', tank: 700000, sl: 70, f: 0.5, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] }).qty, 775);
// SL ยก/เงินเพิ่ม → เกิน 2.5% → เตือน
var Lb = C.ladder({ tier: 'A', tank: 700000, sl: 60, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] });
eq('SL 60 เสี่ยงเกิน 2.5% → RISK_OVER', Lb.warns.indexOf('RISK_OVER') >= 0, true);
eq('ยังคิดผลให้ (เตือน ไม่บล็อก)', Lb.ok, true);
// TH ปัดหลัก 100 ทุกระดับ
var Lt = C.ladder({ tier: 'A', tank: 700000, sl: 70, market: 'TH', levels: [{ px: 100 }, { px: 90 }, { px: 80 }] });
eq('TH L1 = 200', Lt.rows[0].qty, 200);
eq('TH L2 = 200', Lt.rows[1].qty, 200);
eq('TH L3 = 200', Lt.rows[2].qty, 200);
eq('TH รวม 600', Lt.qty, 600);
near('TH ทุน 54,000', Lt.cost, 54000);
near('TH เสี่ยงเต็ม 12,000', Lt.fullRisk, 12000);
// 2 ระดับ = 50/50
var L2 = C.ladder({ tier: 'A', tank: 700000, sl: 80, levels: [{ px: 100 }, { px: 90 }] });
near('2 ระดับ แบ่ง 50%', L2.rows[0].alloc, 35000);
eq('2 ระดับ L1 = 350', L2.rows[0].qty, 350);
eq('2 ระดับ L2 = 388', L2.rows[1].qty, 388);
// ยกเลิกระดับที่ยังไม่ซื้อ = คืนสัดส่วน
var Lc = C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80, status: 'cancelled' }] });
eq('ยกเลิก L3 → รวม 513', Lc.qty, 513);
near('ยกเลิก L3 → ทุน 48,970', Lc.cost, 28000 + 233 * 90);
near('ยกเลิก L3 → เสี่ยงเต็ม 13,060', Lc.fullRisk, 8400 + 4660);
eq('แถว L3 ตั้ง cancelled', Lc.rows[2].cancelled, true);
// กรอกผิด
eq('ระดับเดียว → LEVELS_2_3', C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }] }).err, 'LEVELS_2_3');
eq('ระดับไม่ไล่ลง → LEVELS_NOT_DESC', C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 90 }, { px: 100 }] }).err, 'LEVELS_NOT_DESC');
eq('ระดับต่ำกว่า SL → LEVEL_BELOW_SL', C.ladder({ tier: 'A', tank: 700000, sl: 85, levels: [{ px: 100 }, { px: 80 }] }).err, 'LEVEL_BELOW_SL');
eq('split ไม่ครบ 100% → SPLIT_NOT_100', C.ladder({ tier: 'A', tank: 700000, sl: 70, split: [0.5, 0.3, 0.3], levels: [{ px: 100 }, { px: 90 }, { px: 80 }] }).err, 'SPLIT_NOT_100');
// สัดส่วน L รวม ≤ 30%
var S = C.ladderShare({ tank: 700000, ladders: [L, L, L] });
near('L 3 ตัว ≈ 29.97%', S.pct, 3 * 69930 / 700000, 1e-9);
eq('ยังไม่เกิน 30%', S.over, false);
eq('L 4 ตัว = เกิน 30%', C.ladderShare({ tank: 700000, ladders: [L, L, L, L] }).over, true);
eq('L 3 ตัวเต็ม + 1 ตัวที่ยกเลิก L3 (ทุน 48,970) = 36.96% เกิน', C.ladderShare({ tank: 700000, ladders: [L, L, L, Lc] }).over, true);
eq('4 ตัวที่ยกเลิก L3 ทุกตัว = 27.98% → คืนสัดส่วนแล้วไม่เกิน', C.ladderShare({ tank: 700000, ladders: [Lc, Lc, Lc, Lc] }).over, false);

/* ───────── ชั้น 2 ───────── */
section('ชั้น 2');
var t2a = C.layer2({ tank: 700000, positions: [{ qty: 500, px: 108, stop: 90 }] });
near('Family ตัวอย่าง 500×18 = 9,000', t2a.risk, 9000);
eq('level ok', t2a.level, 'ok');
var t2b = C.layer2({ tank: 100000, positions: [{ qty: 1000, px: 100, stop: 85 }] });
near('15,000 = 15% → warn', t2b.pct, 0.15, 1e-12);
eq('ขอบ 15% = warn', t2b.level, 'warn');
eq('20% ตรง ๆ ยัง warn (ไม่ over)', C.layer2({ tank: 100000, positions: [{ qty: 1000, px: 100, stop: 80 }] }).level, 'warn');
eq('เกิน 20% = over', C.layer2({ tank: 100000, positions: [{ qty: 1000, px: 100, stop: 79 }] }).level, 'over');
var t2m = C.layer2({ tank: 700000, positions: [{ qty: 500, px: 108, stop: 90 }, { qty: 300, px: null, stop: 50 }, { qty: 100, stop: 10 }] });
eq('ขาดราคา 2 ตัว', t2m.missing, 2);
near('ตัวไม่มีราคาไม่นับความเสี่ยง', t2m.risk, 9000);
near('ราคา ≤ Stop → 0 ไม่ติดลบ', C.layer2({ tank: 700000, positions: [{ qty: 100, px: 80, stop: 90 }] }).risk, 0);
near('W+L รวมชั้น 2', C.layer2({ tank: 700000, positions: [{ qty: 500, px: 108, stop: 90 }, { qty: 280, px: 96.5, stop: 70 }] }).risk, 9000 + 280 * 26.5);
near('L1 ที่ 96.50 = 7,420', C.layer2({ tank: 700000, positions: [{ qty: 280, px: 96.5, stop: 70 }] }).risk, 7420);
eq('ไม่มีตำแหน่ง → 0', C.layer2({ tank: 700000, positions: [] }).risk, 0);
// บัญชีลด (ตัวอย่างบัญชี 1,000,000)
near('บัญชี 1,000,000 · Family 9,000 → 0.9%', C.accountDrop({ accountCap: 1000000, risks: [9000] }).pct, 0.009, 1e-12);
near('รวมหลาย port', C.accountDrop({ accountCap: 1000000, risks: [9000, 2500] }).pct, 0.0115, 1e-12);
eq('ไม่มีทุนบัญชี → NO_ACCOUNT_CAP', C.accountDrop({ risks: [1] }).err, 'NO_ACCOUNT_CAP');

/* ───────── Stop ฉุกเฉิน · สถานะ · ล็อต ───────── */
section('Stop ฉุกเฉิน / สถานะ');
near('Stop 90 → 83.70', C.emergencyStop({ stop: 90 }).price, 83.7, 1e-9);
near('Stop 70 → 65.10', C.emergencyStop({ stop: 70 }).price, 65.1, 1e-9);
near('ปรับ −10%', C.emergencyStop({ stop: 100, pct: 0.10 }).price, 90, 1e-9);
eq('Stop ผิด', C.emergencyStop({ stop: 0 }).err, 'BAD_STOP');
var T = '2026-09-30';
eq('เขียว', C.status({ px: 108, pxDate: '2026-09-27', today: T, stop: 90, ema10: 104.2 }).status, 'green');
eq('เหลือง (ใต้ EMA10)', C.status({ px: 96.5, pxDate: '2026-09-27', today: T, stop: 70, ema10: 99.1 }).status, 'yellow');
eq('แดง (ใต้ Stop)', C.status({ px: 89, pxDate: '2026-09-27', today: T, stop: 90, ema10: 104 }).status, 'red');
eq('แดงก่อนเหลือง', C.status({ px: 60, pxDate: '2026-09-27', today: T, stop: 70, ema10: 99 }).status, 'red');
eq('ปิดเท่า Stop ไม่ใช่แดง', C.status({ px: 90, pxDate: '2026-09-27', today: T, stop: 90 }).status, 'green');
eq('เก่า 7 วัน ยังใช้ได้', C.status({ px: 108, pxDate: '2026-09-23', today: T, stop: 90 }).status, 'green');
eq('เก่า 8 วัน → ⚪', C.status({ px: 108, pxDate: '2026-09-22', today: T, stop: 90 }).status, 'na');
eq('ไม่มีราคา → ⚪', C.status({ pxDate: '2026-09-27', today: T, stop: 90 }).status, 'na');
eq('ไม่มีวันที่ → ⚪', C.status({ px: 108, today: T, stop: 90 }).status, 'na');
eq('ไม่มี EMA10 ข้ามข้อเหลือง', C.status({ px: 50, pxDate: '2026-09-27', today: T, stop: 40 }).status, 'green');
eq('อายุ 3 วัน', C.status({ px: 108, pxDate: '2026-09-27', today: T, stop: 90 }).age, 3);
section('floorLot');
eq('699.9999999999 → 700', C.floorLot(700 - 1e-12, 1), 700);
eq('525 / 100 → 500', C.floorLot(525, 100), 500);
eq('99.9 / 100 → 0', C.floorLot(99.9, 100), 0);
eq('ติดลบ → 0', C.floorLot(-5, 100), 0);
eq('NaN → 0', C.floorLot(NaN, 100), 0);


/* ═════════ v2 (30 ก.ย. ค่ำ): เงินสดคุม · Tier A · ยกเลิกอัตโนมัติ · ชั้น 2 รวมจอง · ประตู f · งบ W/L · จัด Tier ═════════ */
section('L เฉพาะ Tier A');
eq('Tier B วางบันไดไม่ได้', C.ladder({ tier: 'B', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] }).err, 'TIER_B_NO_LADDER');
eq('ไม่ส่ง tier = B', C.ladder({ tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] }).err, 'TIER_B_NO_LADDER');

section('สถานะบันได · ถือ/จอง');
var Lh = C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100, status: 'bought' }, { px: 90 }, { px: 80 }] });
eq('ถือ L1 = 280', Lh.heldQty, 280);
near('ถือ 28,000', Lh.heldCost, 28000);
near('จอง L2+L3 = 41,930', Lh.reservedCost, 233 * 90 + 262 * 80);
near('เสี่ยงที่จอง = 233×20 + 262×10 = 7,280', Lh.reservedRisk, 7280);
near('ถือ + จอง = ทุนทั้งบันได', Lh.heldCost + Lh.reservedCost, Lh.cost);
eq('ระดับที่ยังไม่ยกเลิก 3', Lh.liveLevels, 3);

section('เลื่อน Stop → ยกเลิกระดับอัตโนมัติ');
var lv0 = [{ px: 100, status: 'bought' }, { px: 90 }, { px: 80 }];
var m85 = C.applyStopMove({ levels: lv0, sl: 70, newSl: 85 });
eq('Stop 85: ยกเลิก L3 (80)', m85.cancelled.join(','), '2');
eq('L3 cancelled', m85.levels[2].status, 'cancelled');
eq('L2 (90) ยังจอง', m85.levels[1].status, 'wait');
eq('ไม่แก้ของเดิม', lv0[2].status === undefined, true);
var m90 = C.applyStopMove({ levels: lv0, sl: 70, newSl: 90 });
eq('Stop = 90 พอดี: L2 ก็ยกเลิก', m90.cancelled.join(','), '1,2');
var m105 = C.applyStopMove({ levels: lv0, sl: 70, newSl: 105 });
eq('Stop 105 เหนือ L1 ที่ซื้อแล้ว: L1 ไม่ถูกแตะ', m105.levels[0].status, 'bought');
eq('ยกเลิกหมดที่ยังจอง', m105.cancelled.join(','), '1,2');
eq('ยังไม่จบ (ยังถือ L1)', m105.ended, false);
eq('Stop ลง → STOP_DOWN', C.applyStopMove({ levels: lv0, sl: 70, newSl: 65 }).err, 'STOP_DOWN');
eq('Stop เท่าเดิม ไม่ยกเลิกอะไร', C.applyStopMove({ levels: lv0, sl: 70, newSl: 70 }).cancelled.length, 0);
eq('ไม่มีที่ซื้อ + Stop ทะลุทุกระดับ = จบ', C.applyStopMove({ levels: [{ px: 100, status: 'cancelled' }, { px: 90 }], sl: 70, newSl: 95 }).ended, true);
// คืนสัดส่วนจริง: คำนวณบันไดใหม่หลังยกเลิก
var Lafter = C.ladder({ tier: 'A', tank: 700000, sl: 85, levels: m85.levels });
near('หลัง Stop 85: จอง = L2 เท่านั้น 20,970', Lafter.reservedCost, 233 * 90);
near('ถือ L1 เท่าเดิม', Lafter.heldCost, 28000);
near('ทุนบันไดเหลือ 48,970 (คืน L3 = 20,960)', Lafter.cost, 28000 + 233 * 90);
near('เสี่ยงเต็มบันได = L1: 280×15 + L2: 233×5 = 5,365', Lafter.fullRisk, 280 * 15 + 233 * 5);
// Stop เหนือระดับที่ซื้อแล้ว: ไม่ error และเสี่ยง 0 (ไม่ติดลบ)
var Lup = C.ladder({ tier: 'A', tank: 700000, sl: 105, levels: m105.levels });
eq('ok แม้ Stop เหนือ L1', Lup.ok, true);
near('เสี่ยงเต็ม = 0', Lup.fullRisk, 0);
eq('ยังมีระดับ wait ใต้ Stop → LEVEL_BELOW_SL (ต้องผ่าน applyStopMove ก่อน)', C.ladder({ tier: 'A', tank: 700000, sl: 105, levels: [{ px: 100, status: 'bought' }, { px: 90 }] }).err, 'LEVEL_BELOW_SL');

section('งบ W / L / เงินว่าง');
var LA = C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] });
var sp0 = C.portfolioSplit({ tank: 700000, wCost: 100000, ladders: [LA] });
near('จองเต็มบันได 69,930', sp0.lReserved, 69930);
near('เงินว่าง 530,070', sp0.cashFree, 700000 - 100000 - 69930);
near('L ≈ 9.99%', sp0.lPct, 0.0999, 1e-4);
eq('ไม่เกิน 30%', sp0.lOver, false);
var sp1 = C.portfolioSplit({ tank: 700000, wCost: 100000, ladders: [Lh] });
near('ถือ 28,000', sp1.lHeld, 28000);
near('จอง 41,930', sp1.lReserved, 41930);
near('ซื้อ L1 แล้ว เงินว่างเท่าเดิม (จองอยู่แล้ว)', sp1.cashFree, sp0.cashFree);
var sp2 = C.portfolioSplit({ tank: 700000, wCost: 100000, ladders: [] });
near('จบรอบ (L ออกหมด) เงินคืน W', sp2.cashFree, 600000);
near('ยกเลิก L3 คืนเงินจอง 20,960', C.portfolioSplit({ tank: 700000, wCost: 100000, ladders: [Lafter] }).cashFree - sp0.cashFree, 262 * 80);
eq('L 4 ตัว > 30% → lOver', C.portfolioSplit({ tank: 700000, wCost: 0, ladders: [LA, LA, LA, LA] }).lOver, true);
eq('เงินเกินถัง → overCommitted', C.portfolioSplit({ tank: 700000, wCost: 650000, ladders: [LA] }).overCommitted, true);
near('overCommitted เงินว่าง = 0', C.portfolioSplit({ tank: 700000, wCost: 650000, ladders: [LA] }).cashFree, 0);

section('เงินสดคุมไม้ W');
var c1 = C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A', cash: 30000 });
eq('เงินสด 30,000 → 300 หุ้น', c1.qty, 300);
eq('cashLimited', c1.cashLimited, true);
eq('เงินสดเหลือเฟือ ไม่คุม', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A', cash: 500000 }).cashLimited, false);
eq('เงินสดเท่ากับที่ต้องใช้พอดี ไม่ถือว่าคุม', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A', cash: 70000 }).cashLimited, false);
eq('ไม่ส่ง cash = ไม่คุม', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A' }).cashLimited, false);
eq('TH เงินสด 25,000 → 250 → ปัด 200', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A', cash: 25000, market: 'TH' }).qty, 200);
var c0 = C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, tier: 'A', cash: 0 });
eq('เงินสด 0 → 0 หุ้น', c0.qty, 0);
eq('เงินสด 0 → zeroLot', c0.zeroLot, true);
eq('เงินสด 0 → cashLimited', c0.cashLimited, true);
eq('เงินสดติดลบ = 0', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 1, cash: -5000 }).qty, 0);
var ca = C.addLot({ tank: 700000, f: 1, price: 115, stop: 100, heldQty: 700, avgCost: 100, prevLotQty: 700, cash: 20000 });
eq('ไม้เติมเงินสด 20,000 @115 → 173', ca.qty, 173);
eq('tag cash_limited', ca.tag, 'cash_limited');
var ca0 = C.addLot({ tank: 700000, f: 1, price: 115, stop: 100, heldQty: 700, avgCost: 100, prevLotQty: 700, cash: 0 });
eq('ไม้เติมเงินสด 0 → 0', ca0.qty, 0);
eq('tag cash_limited (ไม่ใช่ move_stop)', ca0.tag, 'cash_limited');
eq('เงินสดพอ → ความเสี่ยงคุมตามเดิม', C.addLot({ tank: 700000, f: 1, price: 115, stop: 95, heldQty: 700, avgCost: 100, prevLotQty: 700, cash: 900000 }).tag, 'risk_limited');
eq('เงินสดคุมก่อนความเสี่ยงคุม', C.addLot({ tank: 700000, f: 1, price: 115, stop: 95, heldQty: 700, avgCost: 100, prevLotQty: 700, cash: 10000 }).tag, 'cash_limited');
near('ไม้เติมมี cost', ca.cost, 173 * 115);
eq('งบเสี่ยง W ยัง = 1% ของทั้งถัง × f (ไม่ลดตามเงินสด)', C.firstLot({ tank: 700000, entry: 100, stop: 90, f: 0.75, tier: 'A', cash: 20000 }).budget, 5250);

section('ชั้น 2 รวมบันไดที่จอง');
var pos1 = [{ qty: 280, px: 96.5, stop: 70 }];
var res1 = [{ qty: 233, px: 90, stop: 70 }, { qty: 262, px: 80, stop: 70 }];
var l2r = C.layer2({ tank: 700000, positions: pos1, reserved: res1 });
near('ตอนนี้ 7,420', l2r.risk, 7420);
near('ที่จอง 4,660 + 2,620 = 7,280', l2r.riskReserved, 7280);
near('ถ้าบันไดเต็ม 14,700', l2r.riskFull, 14700);
near('ตอนนี้ ≈ 1.06%', l2r.pct, 0.0106, 1e-4);
near('เต็ม 2.1%', l2r.pctFull, 0.021, 1e-9);
eq('ไม่ส่ง reserved เหมือนเดิม', C.layer2({ tank: 700000, positions: pos1 }).riskFull, 7420);
var l2o = C.layer2({ tank: 100000, positions: [{ qty: 500, px: 100, stop: 90 }], reserved: [{ qty: 500, px: 100, stop: 60 }] });
eq('ตอนนี้ 5% = ok', l2o.levelNow, 'ok');
eq('เต็ม 25% = over (level คิดจากเต็ม)', l2o.level, 'over');
near('เต็ม 25%', l2o.pctFull, 0.25, 1e-12);
eq('ราคา ≤ Stop ของ reserved = 0', C.layer2({ tank: 700000, positions: [], reserved: [{ qty: 100, px: 60, stop: 70 }] }).riskReserved, 0);

section('ประตูเปิดบันไดใหม่ (f)');
var g = function (h, need) { return C.openGate({ fHistory: h, need: need }); };
eq('75%,75% → เปิด', g([0.75, 0.75]).open, true);
eq('streak 2', g([0.75, 0.75]).streak, 2);
eq('50%,75% → เปิด', g([0.5, 0.75]).open, true);
eq('75% สัปดาห์เดียว → ยังไม่เปิด', g([0.75]).open, false);
eq('reason short_streak', g([0.75]).reason, 'short_streak');
eq('100% ล่าสุด → งดเปิด (green)', g([1, 0.75, 0.75]).reason, 'green');
eq('green ปิด', g([1, 0.75, 0.75]).open, false);
eq('ล่าสุด null → unknown', g([null, 0.75, 0.75]).reason, 'unknown');
eq('unknown ปิด', g([null, 0.75, 0.75]).open, false);
eq('unknown status', g([null]).status, 'unknown');
eq('list ว่าง → unknown', g([]).reason, 'unknown');
eq('ไม่ส่งอะไร ไม่ throw', C.openGate().open, false);
eq('75,50,75 = streak 3 เปิด', g([0.75, 0.5, 0.75]).streak, 3);
eq('75, null, 50 → ตัดสายที่ null (streak 1)', g([0.75, null, 0.5]).streak, 1);
eq('75, null, 50 → ไม่เปิด', g([0.75, null, 0.5]).open, false);
eq('75, 100, 75 → streak 1 ไม่เปิด', g([0.75, 1, 0.75]).open, false);
eq('need = 3 ปรับได้ · 2 สัปดาห์ไม่พอ', g([0.75, 0.75], 3).open, false);
eq('need = 3 ครบ', g([0.75, 0.75, 0.5], 3).open, true);
eq('red status', g([0.75, 0.75]).status, 'red');
eq('green status', g([1]).status, 'green');

section('วางบันไดใหม่ได้ไหม');
var okGate = { open: true, reason: 'ok' };
var NL = C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }] });
var ok1 = C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 100000, positions: [], reserved: [] });
eq('ผ่านทุกข้อ', ok1.allowed, true);
near('RG2b: ไม่มี pctFull (Layer 2 ถูกถอด) · sharePct = ทุนบันไดใหม่ ÷ ถัง Ladder', ok1.sharePct, NL.cost / 700000, 1e-9);
eq('Tier B ไม่ผ่าน', C.canPlaceLadder({ tank: 700000, tier: 'B', gate: okGate, ladder: NL }).reasons.indexOf('TIER_B') >= 0, true);
eq('ประตูปิด (green)', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: { open: false, reason: 'green' }, ladder: NL }).reasons.indexOf('GATE_green') >= 0, false);   /* RG2b: ไม่มีประตู f */
eq('ประตูปิด (unknown)', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: { open: false, reason: 'unknown' }, ladder: NL }).reasons.indexOf('GATE_unknown') >= 0, false);   /* RG2b */
eq('ไม่ส่ง gate = งด', C.canPlaceLadder({ tank: 700000, tier: 'A', ladder: NL }).allowed, true);   /* RG2b: ไม่มีประตู f */
// ชั้น 2 เกิน 20%: ถือเสี่ยง 130,000 (18.57%) + บันไดใหม่ 15,680 (2.24%) = 20.8%
var big = C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, positions: [{ qty: 1000, px: 200, stop: 70 }] });
eq('ชั้น 2 รวมบันไดใหม่เกิน 20%', big.reasons.indexOf('LAYER2_OVER') >= 0, false);   /* RG2b: ไม่มีเช็กชั้น 2 */
eq('เกิน → ไม่อนุญาต', big.allowed, true);   /* RG2b */
var mid = C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, positions: [{ qty: 1000, px: 170, stop: 70 }] });
eq('เสี่ยง 100,000 (14.3%) + 2.24% = 16.5% ผ่าน', mid.allowed, true);
eq('ชั้น 2 นับที่จองของบันไดเดิมด้วย', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, positions: [{ qty: 1000, px: 170, stop: 70 }], reserved: [{ qty: 1000, px: 150, stop: 70 }] }).reasons.indexOf('LAYER2_OVER') >= 0, false);   /* RG2b */
eq('เงินสดไม่พอจอง', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 650000 }).reasons.indexOf('NO_CASH') >= 0, false);   /* RG2b: ไม้ W ไม่กินถัง Ladder */
eq('L รวมเกิน 30%', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL, NL] }).reasons.indexOf('L_SHARE_OVER') >= 0, false);   /* RG2b */
eq('L 2 ตัวเดิม + 1 ใหม่ = 29.97% ผ่านข้อ 30%', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL] }).reasons.indexOf('L_SHARE_OVER'), -1);
eq('7E-2b-1: ส่ง l2Cap 0.25 → เคส 20.8% ผ่านชั้น 2', big.reasons.indexOf('LAYER2_OVER') >= 0 && C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, positions: [{ qty: 1000, px: 200, stop: 70 }], l2Cap: 0.25 }).reasons.indexOf('LAYER2_OVER') < 0, false);   /* RG2b */
eq('7E-2b-1: shareCap 0.20 → 3 ตัวเดิม+1 ใหม่ เกิน', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL], shareCap: 0.20 }).reasons.indexOf('L_SHARE_OVER') >= 0, false);   /* RG2b */
eq('7E-2b-1: shareCap 0.40 → 3 ตัวเดิม+1 ใหม่ ผ่าน', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL, NL], shareCap: 0.40 }).reasons.indexOf('L_SHARE_OVER'), -1);
eq('บันไดเสีย → BAD_LADDER', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: { ok: false } }).reasons.indexOf('BAD_LADDER') >= 0, true);
eq('รวมเหตุผลหลายข้อ', C.canPlaceLadder({ tank: 700000, tier: 'B', gate: { open: false, reason: 'green' }, ladder: NL, wCost: 650000 }).reasons.length === 1, true);   /* RG2b: เหลือ TIER_B ข้อเดียว */

section('จัด Tier');
var good = { roic: 0.18, ndEbitda: 1.2, fcfConv: 0.9, fcfPositive3y: true, capitalReturn: true, gate5: { substitute: false, customerMigrating: false, singleProduct: false } };
var tc = function (patch, ov) { var o = JSON.parse(JSON.stringify(good)); for (var k in patch) { if (k === 'gate5') for (var j in patch.gate5) o.gate5[j] = patch.gate5[j]; else o[k] = patch[k]; } if (ov) o.override = ov; return C.classifyTier(o); };
eq('ผ่านครบ → A', tc({}).tier, 'A');
eq('ROIC ต่ำ → B', tc({ roic: 0.10 }).tier, 'B');
eq('บอกข้อที่ไม่ผ่าน = roic', tc({ roic: 0.10 }).failedNumbers.join(','), 'roic');
eq('ROIC เท่ากับเกณฑ์ (ต้อง >) → B', tc({ roic: 0.12 }).tier, 'B');
eq('7E-2b-1: ROIC 12.5% ND 1.5 FCF 85% Gate 5 ไม่ทั้ง 3 → A', tc({ roic: 0.125, ndEbitda: 1.5, fcfConv: 0.85 }).tier, 'A');
eq('7E-2b-1: ROIC 11.9% → B', tc({ roic: 0.119 }).tier, 'B');
eq('7E-2b-1: ขาด fcfConv → B', tc({ fcfConv: null }).tier, 'B');
eq('7E-2b-1: Gate 5 ใช่ 1 ข้อ → B', tc({ roic: 0.125, gate5: { substitute: true } }).tier, 'B');
eq('roicMin 12% ปรับได้ · ROIC 13% ผ่าน', C.classifyTier({ roic: 0.13, roicMin: 0.12, ndEbitda: 1, fcfConv: 0.9, fcfPositive3y: true, capitalReturn: true, gate5: good.gate5 }).tier, 'A');
eq('ND/EBITDA = 2 (ต้อง <) → B', tc({ ndEbitda: 2 }).tier, 'B');
eq('ND/EBITDA ติดลบ (เงินสดสุทธิ) ผ่าน', tc({ ndEbitda: -0.5 }).tier, 'A');
eq('FCF = 80% (ต้อง >) → B', tc({ fcfConv: 0.8 }).tier, 'B');
eq('FCF 81% ผ่าน', tc({ fcfConv: 0.81 }).tier, 'A');
eq('ไม่มีตัวเลข → B', tc({ ndEbitda: null }).tier, 'B');
eq('ตัวเลขไม่ผ่าน 3 ข้อ บอกครบ', tc({ roic: 0.05, ndEbitda: 3, fcfConv: 0.5 }).failedNumbers.length, 3);
eq('Gate 5 ใช่ข้อเดียว (แทนที่) → B', tc({ gate5: { substitute: true } }).tier, 'B');
eq('Gate 5 ใช่ข้อเดียว (ลูกค้าย้าย) → B', tc({ gate5: { customerMigrating: true } }).tier, 'B');
eq('Gate 5 ใช่ข้อเดียว (สินค้าเดียว >50%) → B', tc({ gate5: { singleProduct: true } }).tier, 'B');
eq('บอก Gate 5 ที่ตอบใช่', tc({ gate5: { substitute: true, singleProduct: true } }).gate5Yes.join(','), 'substitute,singleProduct');
eq('Gate 5 ยังไม่ตอบ → B (ค่าเริ่มต้น B)', C.classifyTier({ roic: 0.18, ndEbitda: 1, fcfConv: 0.9 }).tier, 'B');
eq('บอกข้อที่ยังไม่ตอบ', C.classifyTier({ roic: 0.18, ndEbitda: 1, fcfConv: 0.9, gate5: { substitute: false } }).gate5Unanswered.length, 2);
eq('ไม่ส่งอะไรเลย → B ไม่ throw', C.classifyTier().tier, 'B');
eq('override A ไม่มีเหตุผล → REASON_REQUIRED', tc({ roic: 0.10 }, { tier: 'A' }).err, 'REASON_REQUIRED');
eq('override A เหตุผลว่างเว้นวรรค → REASON_REQUIRED', tc({ roic: 0.10 }, { tier: 'A', reason: '   ' }).err, 'REASON_REQUIRED');
eq('REASON_REQUIRED ยังคืน tier ที่คำนวณ = B', tc({ roic: 0.10 }, { tier: 'A' }).tier, 'B');
var ovA = tc({ roic: 0.10 }, { tier: 'A', reason: 'ROIC ต่ำเพราะลงทุนขยายกำลังผลิต ไม่ใช่ธุรกิจแย่' });
eq('override A มีเหตุผล → A', ovA.tier, 'A');
eq('overridden flag', ovA.overridden, true);
eq('เก็บเหตุผล (trim แล้ว)', ovA.reason, 'ROIC ต่ำเพราะลงทุนขยายกำลังผลิต ไม่ใช่ธุรกิจแย่');
eq('ค่าที่คำนวณเดิมยังอยู่ = B', ovA.computed, 'B');
var ovB = tc({}, { tier: 'B' });
eq('override ลงเป็น B ไม่ต้องมีเหตุผล', ovB.tier, 'B');
eq('override ลง = overridden', ovB.overridden, true);
eq('override A ตอนคำนวณได้ A อยู่แล้ว ไม่ต้องเหตุผล', tc({}, { tier: 'A' }).overridden, false);
eq('Tier A ที่จัดได้ → วางบันไดได้', C.ladder({ tier: tc({}).tier, tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }] }).ok, true);
eq('Tier B ที่จัดได้ → วางบันไดไม่ได้', C.ladder({ tier: tc({ roic: 0.05 }).tier, tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }] }).err, 'TIER_B_NO_LADDER');


section('TIER2 · Tier 2 มุมมอง (A-Fortress / A-Growth)');
var FO = { roic: 0.15, ndEbitda: 1.5, fcfConv: 0.9, fcfPositive3y: true, capitalReturn: true };
var GR = { revGrowth: 0.25, revCagr3: 0.18, opMargin: 0.12, opMarginPrev: 0.10, ocf: true, ndEbitda: 2.5 };
var G5N = { gate5: { substitute: false, customerMigrating: false, singleProduct: false } };
var mk = function () { var o = {}; for (var i = 0; i < arguments.length; i++) for (var k in arguments[i]) o[k] = arguments[i][k]; return o; };
// 1
var t1 = C.classifyTier(mk(FO, G5N));
eq('T2-1 Fortress ผ่าน → lens fortress', t1.lens, 'fortress');
eq('T2-1 tier A', t1.tier, 'A');
eq('T2-1 growth ไม่ผ่านเพราะไม่มีข้อมูล', t1.lenses.growth.pass, false);
// 2
var t2 = C.classifyTier(mk(FO, G5N, { capitalReturn: undefined }));
eq('T2-2 capret ไม่มีข้อมูล → fortress ไม่ผ่าน', t2.lenses.fortress.failed.join(','), 'capret');
eq('T2-2 growth ไม่มีข้อมูลด้วย → B', t2.tier, 'B');
eq('T2-2 fcf3y ไม่มีข้อมูล → fcf3y', C.classifyTier(mk(FO, G5N, { fcfPositive3y: undefined })).lenses.fortress.failed.join(','), 'fcf3y');
eq('T2-2 ค่าเดิม passed ยังเป็นตัวเลข 3 ข้อ', JSON.stringify(t2.passed), '{"roic":true,"nd":true,"fcf":true}');
// 3
var t3 = C.classifyTier(mk(GR, G5N));
eq('T2-3 Growth ผ่าน → lens growth', t3.lens, 'growth');
eq('T2-3 tier A · computed A', t3.tier + t3.computed, 'AA');
eq('T2-3 fortress ไม่ผ่านไม่ทำให้ failedNumbers ผิด', t3.failedNumbers.join(','), 'roic,nd,fcf');
// 4
var gf = function (p) { return C.classifyTier(mk(GR, G5N, p)).lenses.growth.failed.join(','); };
eq('T2-4 rev 19.9% → rev', gf({ revGrowth: 0.199 }), 'rev');
eq('T2-4 rev 20% พอดีผ่าน (≥)', gf({ revGrowth: 0.20 }), '');
eq('T2-4 CAGR 14.9% → cagr', gf({ revCagr3: 0.149 }), 'cagr');
eq('T2-4 opm 9% vs 10% → opm_trend', gf({ opMargin: 0.09 }), 'opm_trend');
eq('T2-4 opm เท่าปีก่อนผ่าน', gf({ opMargin: 0.10 }), '');
eq('T2-4 opm −1% → opm', gf({ opMargin: -0.01 }).split(',').indexOf('opm') >= 0, true);
eq('T2-4 ไม่มี opm ปีก่อน → opm_trend', gf({ opMarginPrev: null }), 'opm_trend');
eq('T2-4 OCF ไม่มีข้อมูล → ocf', gf({ ocf: undefined }), 'ocf');
eq('T2-4 OCF เป็นตัวเลข > 0 ผ่าน', gf({ ocf: 500 }), '');
eq('T2-4 ND 3.5 → nd_g', gf({ ndEbitda: 3.5 }), 'nd_g');
eq('T2-4 ND = 3 (ต้อง <) → nd_g', gf({ ndEbitda: 3 }), 'nd_g');
eq('T2-4 ND 3.5 แต่ netDebt −100 → ผ่าน', gf({ ndEbitda: 3.5, netDebt: -100 }), '');
eq('T2-4 ND 3.5 แต่ netCash ✓ → ผ่าน', gf({ ndEbitda: 3.5, netCash: true }), '');
eq('T2-4 ND 3.5 netDebt +100 → nd_g', gf({ ndEbitda: 3.5, netDebt: 100 }), 'nd_g');
// 5
var t5 = C.classifyTier(mk(FO, GR, { ndEbitda: 1.5 }, G5N));
eq('T2-5 ผ่านทั้งคู่ → both', t5.lens, 'both');
eq('T2-5 tier A', t5.tier, 'A');
// 6
var t6 = C.classifyTier(mk(FO, GR, { ndEbitda: 1.5 }, { gate5: { substitute: true, customerMigrating: false, singleProduct: false } }));
eq('T2-6 Gate 5 ใช่ 1 ข้อ → B', t6.tier, 'B');
eq('T2-6 lens null', t6.lens, null);
eq('T2-6 fortress failed gate5', t6.lenses.fortress.failed.join(','), 'gate5');
eq('T2-6 growth failed gate5', t6.lenses.growth.failed.join(','), 'gate5');
eq('T2-6 Gate 5 ไม่ตอบ → gate5 ทั้งคู่', C.classifyTier(mk(FO, GR, { ndEbitda: 1.5 })).lenses.growth.failed.join(','), 'gate5');
// 7
var o7 = C.classifyTier(mk(FO, { capitalReturn: false }, G5N, { override: { tier: 'A', lens: 'growth', reason: '' } }));
eq('T2-7 override A·growth ที่คำนวณไม่ผ่าน ไม่มีเหตุผล → REASON_REQUIRED', o7.err, 'REASON_REQUIRED');
var o7b = C.classifyTier(mk(FO, { capitalReturn: false }, G5N, { override: { tier: 'A', lens: 'growth', reason: 'รายได้โตเร็วกว่าตัวเลขที่กรอก' } }));
eq('T2-7 มีเหตุผล → tier A', o7b.tier, 'A');
eq('T2-7 lens growth', o7b.lens, 'growth');
eq('T2-7 overridden', o7b.overridden, true);
eq('T2-7 computed ยัง B', o7b.computed, 'B');
eq('T2-7 override A ไม่ระบุ lens ตอนคำนวณ B → fortress (ความหมายเดิม)', C.classifyTier(mk(FO, { roic: 0.05 }, G5N, { override: { tier: 'A', reason: 'x' } })).lens, 'fortress');
eq('T2-7 คำนวณ fortress เลือก both → ต้องมีเหตุผล', C.classifyTier(mk(FO, G5N, { override: { tier: 'A', lens: 'both' } })).err, 'REASON_REQUIRED');
var o7d = C.classifyTier(mk(FO, GR, { ndEbitda: 1.5 }, G5N, { override: { tier: 'A', lens: 'fortress' } }));
eq('T2-7 คำนวณ both ลดเป็น fortress ไม่ต้องเหตุผล', o7d.err === undefined && o7d.lens === 'fortress' && o7d.overridden === true, true);
eq('T2-7 เลือก lens เท่าที่คำนวณได้ → ไม่ overridden', C.classifyTier(mk(FO, G5N, { override: { tier: 'A', lens: 'fortress' } })).overridden, false);
eq('T2-7 ลดเป็น B ไม่ต้องเหตุผล · lens null', (function (r) { return r.tier + String(r.lens) + r.overridden; })(C.classifyTier(mk(FO, G5N, { override: { tier: 'B' } }))), 'Bnulltrue');
// 8
eq('T2-8 fortress:false → NOT_FORTRESS', C.canPlaceLadder({ tank: 700000, tier: 'A', fortress: false, gate: okGate, ladder: NL, wCost: 0 }).reasons.indexOf('NOT_FORTRESS') >= 0, true);
eq('T2-8 fortress:false → ไม่อนุญาต', C.canPlaceLadder({ tank: 700000, tier: 'A', fortress: false, gate: okGate, ladder: NL, wCost: 0 }).allowed, false);
eq('T2-8 ไม่ส่ง fortress → เหมือนเดิม (วางได้)', ok1.allowed && ok1.reasons.indexOf('NOT_FORTRESS') < 0, true);
eq('T2-8 fortress:true → ไม่มี NOT_FORTRESS', C.canPlaceLadder({ tank: 700000, tier: 'A', fortress: true, gate: okGate, ladder: NL, wCost: 0 }).reasons.indexOf('NOT_FORTRESS'), -1);
eq('T2-8 ladder() ไม่แตะ — tier A ยังวางได้', C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }] }).ok, true);
// 9
eq('T2-9 ค่าเริ่มต้น growth', JSON.stringify(C.DEFAULTS.tier.growth), '{"revGrowthMin":0.2,"revCagr3Min":0.15,"ndEbitdaMax":3}');
eq('T2-9 ส่งทับ revGrowthMin 0.15 → rev 19.9% ผ่าน', C.classifyTier(mk(GR, G5N, { revGrowth: 0.199, growth: { revGrowthMin: 0.15 } })).lens, 'growth');
eq('T2-9 ส่งทับ revCagr3Min 0.20 → CAGR 18% ไม่ผ่าน', C.classifyTier(mk(GR, G5N, { growth: { revCagr3Min: 0.20 } })).lenses.growth.failed.join(','), 'cagr');
eq('T2-9 ส่งทับ growth.ndEbitdaMax 4 → ND 3.5 ผ่าน', C.classifyTier(mk(GR, G5N, { ndEbitda: 3.5, growth: { ndEbitdaMax: 4 } })).lens, 'growth');
eq('T2-9 ส่ง growth บางคีย์ → คีย์อื่นใช้ค่าเริ่มต้น', C.classifyTier(mk(GR, G5N, { revGrowth: 0.199, growth: { revCagr3Min: 0.10 } })).lenses.growth.failed.join(','), 'rev');
eq('T2-9 roicMin ส่งทับยังทำงาน (Fortress)', C.classifyTier(mk(FO, G5N, { roicMin: 0.20 })).lenses.fortress.failed.join(','), 'roic');


section('ป้าย Tier เทียบ Watchlist');
var TD = '2026-09-30';
var tb = function (card, watch) { return C.tierBadge({ cardTier: card, watch: watch, today: TD }).badges; };
var one = function (b) { return b.length === 1 ? b[0].code + ':' + b[0].level : 'n=' + b.length; };
// การ์ด A
eq('A · WL = B → เตือน', one(tb('A', { loaded: true, found: true, tier: 'B', setAt: '2026-01-01' })), 'WL_B:warn');
eq('A · WL = B ข้อความ', tb('A', { loaded: true, found: true, tier: 'B' })[0].text, 'Watchlist = B · การ์ดยังเป็น A');
eq('A · ยังไม่ตั้ง Tier → เตือน', one(tb('A', { loaded: true, found: true, tier: null })), 'NO_WL_TIER:warn');
eq('A · ยังไม่ตั้ง Tier ข้อความ', tb('A', { loaded: true, found: true })[0].text, 'ยังไม่ได้ตั้ง Tier ใน Watchlist');
eq('A · ไม่อยู่ใน Watchlist → เตือน', one(tb('A', { loaded: true, found: false })), 'NOT_IN_WATCHLIST:warn');
eq('A · ไม่อยู่ ข้อความ', tb('A', { loaded: true, found: false })[0].text, 'ไม่อยู่ใน Watchlist · ยังไม่ได้ทำการบ้าน');
eq('A · WL = A สดใหม่ → ไม่มีป้าย', tb('A', { loaded: true, found: true, tier: 'A', setAt: '2026-06-01' }).length, 0);
eq('A · WL = A ตั้งเกิน 12 เดือน → เทา ทบทวน', one(tb('A', { loaded: true, found: true, tier: 'A', setAt: '2025-09-29' })), 'REVIEW:muted');
eq('A · ทบทวน แสดงวันที่ตั้ง', tb('A', { loaded: true, found: true, tier: 'A', setAt: '2025-09-29' })[0].text, 'ทบทวน Tier (ตั้งเมื่อ 2025-09-29)');
eq('A · ครบ 12 เดือนพอดี (30 ก.ย. 68→69) ยังไม่เกิน', tb('A', { loaded: true, found: true, tier: 'A', setAt: '2025-09-30' }).length, 0);
eq('A · เกินไป 1 วัน → ทบทวน', tb('A', { loaded: true, found: true, tier: 'A', setAt: '2025-09-29' }).length, 1);
eq('A · WL = A ไม่มีวันที่ตั้ง → ไม่เตือน', tb('A', { loaded: true, found: true, tier: 'A' }).length, 0);
eq('A · วันที่ผิดรูปแบบ → ไม่เตือน', tb('A', { loaded: true, found: true, tier: 'A', setAt: 'ไม่ทราบ' }).length, 0);
eq('A · WL = B ไม่ขึ้น "ทบทวน" ซ้อน', tb('A', { loaded: true, found: true, tier: 'B', setAt: '2020-01-01' }).length, 1);
// การ์ด B
eq('B · WL = B ไม่เตือน', tb('B', { loaded: true, found: true, tier: 'B' }).length, 0);
eq('B · WL ไม่มี Tier ไม่เตือน', tb('B', { loaded: true, found: true, tier: null }).length, 0);
eq('B · WL = A → เทา', one(tb('B', { loaded: true, found: true, tier: 'A', setAt: '2020-01-01' })), 'WL_A:muted');
eq('B · WL = A ข้อความ', tb('B', { loaded: true, found: true, tier: 'A' })[0].text, 'Watchlist = A');
eq('B · ไม่อยู่ใน Watchlist → เทา', one(tb('B', { loaded: true, found: false })), 'NOT_IN_WATCHLIST:muted');
eq('B · ไม่อยู่ ข้อความ', tb('B', { loaded: true, found: false })[0].text, 'ไม่อยู่ใน Watchlist');
eq('B · ไม่ขึ้น "ทบทวน" (ไม่ใช่การ์ด A)', tb('B', { loaded: true, found: true, tier: 'A', setAt: '2020-01-01' })[0].code, 'WL_A');
// โหลดไม่ได้
eq('โหลด Watchlist ไม่ได้ (การ์ด A) = เงียบ', tb('A', { loaded: false, found: false }).length, 0);
eq('โหลดไม่ได้ (การ์ด B) = เงียบ', tb('B', { loaded: false }).length, 0);
eq('ไม่ส่ง watch = เงียบ', C.tierBadge({ cardTier: 'A' }).badges.length, 0);
eq('ไม่ส่งอะไร ไม่ throw', C.tierBadge().ok, true);
eq('ไม่ล็อก: ไม่เปลี่ยน Tier ในผล', C.tierBadge({ cardTier: 'A', watch: { loaded: true, found: true, tier: 'B' }, today: TD }).tier, undefined);
eq('ป้ายเตือนไม่ขวางการวางบันไดของการ์ด A', C.ladder({ tier: 'A', tank: 700000, sl: 70, levels: [{ px: 100 }, { px: 90 }] }).ok, true);

/* ───────── DD1 · ddStep — เบรกชั้น 3 ───────── */
section('DD1 ddStep');
var CFGC = { ddReduce: 12.5, ddPause: 20, ddPauseWeeks: 2, ddRecoverR: 2 };   // Core
var CFGS = { ddReduce: 12.5, ddPause: 20, ddPauseWeeks: 1, ddRecoverR: 2 };   // Sat
// สัปดาห์ (อาทิตย์): 2026-09-06 · 09-13 · 09-20 · 09-27 · 10-04 · 10-11
function dd(o, cfg) {
  var b = { equity: 100, peak: 100, stage: 'normal', stageSince: '2026-08-02', weekly: {}, weekKey: '2026-10-04', today: '2026-10-06', oneR: 10, recoverPnl: 0, cfg: cfg || CFGC };
  for (var k in o) b[k] = o[k];
  return C.ddStep(b);
}
var r;
r = dd({}); eq('dd0 normal ×1', r.stage + '|' + r.sizeFactor + '|' + r.allowNew + '|' + r.allowLadder, 'normal|1|true|true');
r = dd({ equity: 90 }); eq('DD 10% ยัง normal', r.stage, 'normal'); near('ddPct 10', r.ddPct, 10);
r = dd({ equity: 87.5 }); eq('DD 12.5 (เท่าเกณฑ์) → reduce', r.stage, 'reduce');
eq('reduce ×0.5 · ใหม่ได้ · ไม่มีบันไดใหม่', r.sizeFactor + '|' + r.allowNew + '|' + r.allowLadder, '0.5|true|false');
eq('reduce entered', r.entered, 'reduce');
r = dd({ equity: 80 }); eq('DD 20 (เท่าเกณฑ์) → pause', r.stage, 'pause');
eq('pause ห้ามเปิดใหม่', r.sizeFactor + '|' + r.allowNew + '|' + r.allowLadder, '0|false|false');
eq('Core พัก 14 วัน', r.pauseUntil, '2026-10-20'); eq('Sat พัก 7 วัน', dd({ equity: 80 }, CFGS).pauseUntil, '2026-10-13');
eq('pause ยังไม่ครบ left 14', r.info.pauseLeftDays, 14);
r = dd({ equity: 70, stage: 'reduce' }); eq('reduce → pause เมื่อ DD ≥ 20', r.stage, 'pause');
eq('DD 19.99 ยัง reduce', dd({ equity: 80.01, stage: 'reduce' }).stage, 'reduce');
// peak ขยับ
r = dd({ equity: 110 }); eq('equity > peak → peak ขยับ', r.peak, 110); near('ddPct 0', r.ddPct, 0);
r = dd({ equity: 100, peak: 125 }); near('peak 125 equity 100 → DD 20', r.ddPct, 20); eq('→ pause', r.stage, 'pause');
r = dd({ peak: null, equity: 50 }); eq('ไม่มี peak → peak = equity', r.peak, 50);
// reduce → normal: 2 สัปดาห์ที่จบแล้ว ต่ำกว่าเกณฑ์
var RS = { stage: 'reduce', stageSince: '2026-09-01', equity: 95 };   // เข้า reduce สัปดาห์ 08-30
r = dd(Object.assign({ weekly: { '2026-09-27': 10, '2026-09-20': 11 } }, RS)); eq('2 สัปดาห์ติด < 12.5 → normal', r.stage, 'normal');
r = dd(Object.assign({ weekly: { '2026-09-27': 10 } }, RS)); eq('สัปดาห์เดียว → ยัง reduce', r.stage, 'reduce');
r = dd(Object.assign({ weekly: { '2026-09-27': 10, '2026-09-20': 12.5 } }, RS)); eq('สัปดาห์หนึ่ง = 12.5 ไม่ใช่ต่ำกว่า → ยัง reduce', r.stage, 'reduce');
r = dd(Object.assign({ weekly: { '2026-09-27': 10, '2026-09-13': 5 } }, RS)); eq('ไม่ติดกัน (ขาดสัปดาห์กลาง) → ยัง reduce', r.stage, 'reduce');
r = dd(Object.assign({ weekly: { '2026-10-04': 5, '2026-09-27': 10 } }, RS)); eq('ไม่นับสัปดาห์ปัจจุบัน (ปัจจุบัน + 1 สัปดาห์) → ยัง reduce', r.stage, 'reduce');
r = dd(Object.assign({}, RS, { equity: 85, weekly: { '2026-09-27': 10, '2026-09-20': 11 } })); eq('DD ตอนนี้ยัง ≥ 12.5 → ไม่ออก reduce', r.stage, 'reduce');
r = dd(Object.assign({}, RS, { stageSince: '2026-09-22', weekly: { '2026-09-27': 10, '2026-09-20': 11 } })); eq('สัปดาห์ที่เข้า reduce ไม่นับ → ยัง reduce', r.stage, 'reduce');
r = dd(Object.assign({ weekly: {} }, RS, { equity: 95 })); eq('weekly ของสัปดาห์ปัจจุบันถูกเขียน', r.weekly['2026-10-04'], 5);
// weekly: ค่าล่าสุดชนะ + เก็บ 12 สัปดาห์
var wk = {}; for (var i = 0; i < 15; i++) wk[C.ddAddDays('2026-04-05', 7 * i)] = i;
r = dd({ weekly: wk, weekKey: '2026-10-04', today: '2026-10-04' }); eq('weekly เก็บ 12 สัปดาห์', Object.keys(r.weekly).length, 12);
r = dd({ weekly: { '2026-10-04': 50 }, equity: 97 }); near('ค่าล่าสุดของสัปดาห์ชนะ', r.weekly['2026-10-04'], 3);
// pause: ต้องครบเวลา + รีวิว
var PS = { stage: 'pause', stageSince: '2026-10-06', pauseUntil: '2026-10-20', equity: 78 };
r = dd(Object.assign({ today: '2026-10-20', reviewDone: false }, PS)); eq('ครบเวลาแต่ไม่มีรีวิว → ยัง pause', r.stage, 'pause'); eq('timeDone', r.info.timeDone, true);
r = dd(Object.assign({ today: '2026-10-19', reviewDone: true }, PS)); eq('มีรีวิวแต่ยังไม่ครบเวลา → ยัง pause', r.stage, 'pause'); eq('left 1 วัน', r.info.pauseLeftDays, 1);
r = dd(Object.assign({ today: '2026-10-20', reviewDone: true }, PS)); eq('ครบเวลา + รีวิว → recover', r.stage, 'recover');
eq('recover ×0.5 · ใหม่ได้ · ไม่มีบันไดใหม่', r.sizeFactor + '|' + r.allowNew + '|' + r.allowLadder, '0.5|true|false');
eq('recover เก็บ DD ตอนเข้า', Math.round(r.recoverDd0 * 100) / 100, 22);
eq('recover ล้าง pauseUntil', r.pauseUntil, null);
r = dd({ stage: 'pause', stageSince: '2026-10-06', pauseUntil: '2026-10-13', reviewDone: true, today: '2026-10-13', equity: 78 }, CFGS); eq('Sat 1 สัปดาห์ → recover', r.stage, 'recover');
// recover
var RV = { stage: 'recover', stageSince: '2026-10-20', recoverDd0: 22, equity: 78, today: '2026-10-21', weekKey: '2026-10-18' };
r = dd(Object.assign({}, RV)); eq('recover ยังอยู่ (DD เท่าตอนเข้า ไม่ re-pause)', r.stage, 'recover');
r = dd(Object.assign({}, RV, { equity: 76 })); eq('recover + DD ลึกกว่าตอนเข้า ≥ 20 → pause ซ้ำ', r.stage, 'pause'); eq('นับพักใหม่ 14 วัน', r.pauseUntil, '2026-11-04');
eq('pause ซ้ำล้างรีวิว', r.reviewDone, false);
r = dd(Object.assign({}, RV, { recoverDd0: 15, equity: 79 })); eq('recover เข้าตอน DD 15 แล้วกลับ ≥ 20 → pause ซ้ำ', r.stage, 'pause');
r = dd(Object.assign({}, RV, { recoverPnl: 20 })); eq('กำไรปิด = 2R (20 จาก 1R=10) · DD 22 ยัง ≥ 12.5 → reduce ทันที (DD1fix)', r.stage, 'reduce');
r = dd(Object.assign({}, RV, { recoverPnl: 20, equity: 95 })); eq('กำไรปิด = 2R · DD 5 → normal', r.stage, 'normal');
r = dd(Object.assign({}, RV, { recoverPnl: 19.99 })); eq('กำไรปิด 1.999R → ยัง recover', r.stage, 'recover');
r = dd(Object.assign({}, RV, { recoverPnl: -50 })); eq('ขาดทุนไม่ช่วย → ยัง recover', r.stage, 'recover');
r = dd(Object.assign({}, RV, { recoverPnl: 5 }, { recoverR: 0 })); eq('ไม่ส่ง oneR = ไม่เช็ก R', dd(Object.assign({}, RV, { oneR: 0, recoverPnl: 999 })).stage, 'recover');
r = dd(Object.assign({}, RV, { equity: 95, weekKey: '2026-11-08', today: '2026-11-10', weekly: { '2026-11-01': 8, '2026-10-25': 9 } })); eq('recover → normal ด้วย DD < เกณฑ์ 2 สัปดาห์', r.stage, 'normal');
r = dd(Object.assign({}, RV, { equity: 95, weekKey: '2026-11-08', today: '2026-11-10', weekly: { '2026-11-01': 8 } })); eq('recover สัปดาห์เดียว → ยัง recover', r.stage, 'recover');
r = dd({ stage: 'recover', stageSince: '2026-10-20', recoverDd0: 22, equity: 78, today: '2026-10-21', weekKey: '2026-10-18', cfg: { ddReduce: 12.5, ddPause: 20, ddPauseWeeks: 2, ddRecoverR: 3 }, recoverPnl: 20 }); eq('ddRecoverR 3 → 2R ไม่พอ', r.stage, 'recover');
// ค่าผิด/ไม่ throw
eq('equity ไม่ใช่ตัวเลข → fail', C.ddStep({ equity: 'x', weekKey: '2026-10-04' }).ok, false);
eq('weekKey ผิด → fail', C.ddStep({ equity: 1, weekKey: 'x' }).err, 'BAD_WEEK');
eq('reduce ≥ pause → fail', dd({}, { ddReduce: 20, ddPause: 20, ddPauseWeeks: 2, ddRecoverR: 2 }).err, 'BAD_CFG');
eq('ไม่ส่งอะไร ไม่ throw', C.ddStep().ok, false);
eq('stage แปลก → normal', dd({ stage: 'zzz' }).stage, 'normal');
eq('ddWeekOf วันพุธ → อาทิตย์ก่อนหน้า', C.ddWeekOf('2026-10-07'), '2026-10-04');
eq('ddWeekOf วันอาทิตย์ = ตัวมันเอง', C.ddWeekOf('2026-10-04'), '2026-10-04');
eq('ddAddDays ข้ามเดือน', C.ddAddDays('2026-10-25', 14), '2026-11-08');

/* ───────── DD1fix · ออกจาก recover ตอน DD ลึก + ระยะกันพักซ้ำ 1R ───────── */
section('DD1fix');
var G = 1.25;   // gap = RPT ปกติ 1.25%
function fx2(o, cfg) { return dd(Object.assign({ repauseGapPct: G }, o), cfg); }
var RC = { stage: 'recover', stageSince: '2026-09-28', recoverDd0: 25, today: '2026-10-06', weekKey: '2026-10-04' };
r = fx2(Object.assign({}, RC, { equity: 77, recoverPnl: 20 }));   // DD 23 + 2R
eq('1 recover dd0 25 · +2R · DD 23 → reduce รอบเดียว', r.stage + '|' + r.entered, 'reduce|reduce');
eq('1 recoverDd0 ยัง 25 · ×0.5 · ไม่มีบันไดใหม่', r.recoverDd0 + '|' + r.sizeFactor + '|' + r.allowLadder, '25|0.5|false');
eq('1 reduce ที่เข้าจาก recover: stageSince = วันนี้', r.stageSince, '2026-10-06');
var r2 = fx2({ stage: 'reduce', stageSince: r.stageSince, recoverDd0: r.recoverDd0, equity: 77 });
eq('2 รอบถัดไป DD 23 → ยัง reduce (ไม่ pause)', r2.stage, 'reduce');
var RD = { stage: 'reduce', stageSince: '2026-10-06', recoverDd0: 25 };
eq('3 reduce dd0 25 · DD 26.24 → reduce', fx2(Object.assign({}, RD, { equity: 73.76 })).stage, 'reduce');
r = fx2(Object.assign({}, RD, { equity: 73.75 }));
eq('3 DD 26.25 → pause', r.stage, 'pause'); eq('3 recoverDd0 ล้าง · pauseUntil = วันนี้ + 14', r.recoverDd0 + '|' + r.pauseUntil, 'null|2026-10-20');
var R22 = { stage: 'recover', stageSince: '2026-09-28', recoverDd0: 22 };
eq('4 recover dd0 22 · DD 22.1 → recover', fx2(Object.assign({}, R22, { equity: 77.9 })).stage, 'recover');
eq('4 DD 23.24 → recover', fx2(Object.assign({}, R22, { equity: 76.76 })).stage, 'recover');
eq('4 DD 23.25 → pause', fx2(Object.assign({}, R22, { equity: 76.75 })).stage, 'pause');
eq('5 recover dd0 15 · DD 20 → pause (20 ≥ 16.25)', fx2({ stage: 'recover', stageSince: '2026-09-28', recoverDd0: 15, equity: 80 }).stage, 'pause');
eq('6 recover · +2R · DD 14 → reduce', fx2(Object.assign({}, RC, { recoverDd0: 15, equity: 86, recoverPnl: 20 })).stage, 'reduce');
r = fx2(Object.assign({}, RC, { recoverDd0: 15, equity: 90, recoverPnl: 20 }));
eq('6 DD 10 → normal · recoverDd0 null', r.stage + '|' + r.recoverDd0, 'normal|null');
r = fx2({ stage: 'reduce', stageSince: '2026-09-01', recoverDd0: 25, equity: 95, weekly: { '2026-09-27': 10, '2026-09-20': 11 } });
eq('7 reduce dd0 25 · below2 → normal · recoverDd0 null', r.stage + '|' + r.recoverDd0, 'normal|null');
eq('8 ไม่ส่ง repauseGapPct → พฤติกรรมเดิม (dd0 22 · DD 22.1 → pause)', dd({ stage: 'recover', stageSince: '2026-09-28', recoverDd0: 22, equity: 77.9 }).stage, 'pause');
eq('9 reduce ปกติ (ไม่มี dd0) DD 20 → pause', fx2({ stage: 'reduce', stageSince: '2026-09-01', equity: 80 }).stage, 'pause');

/* ───────── LN3fix2 · ไม้เร่ง (layer acc) · Risk % ต่อไม้ · over_ratio · layer2 แยกชั้น ───────── */
section('LN3fix2');
var T2 = 127000;
// ตัวอย่างในม็อกอัป: Base 80 @131 SL 115 · เร่ง @145 SL 140 · งบเร่ง 0.35% → ติดเพดานต่อหุ้น 15% = 59 หุ้น
var ac = C.addLot({ tank: T2, f: 1, price: 145, stop: 140, heldQty: 0, avgCost: 0, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035, stockCapPct: 0.15, heldCostTotal: 80 * 131 });
eq('acc ชั้นว่างเริ่มได้ (ไม่ NO_POSITION)', ac.ok, true);
eq('acc ตัวอย่างม็อกอัป: 59 หุ้น · ชนเพดานต่อหุ้น 15%', ac.qty + '|' + ac.tag, '59|stock_capped');
near('acc เสี่ยง = 59 × 5 = 295', ac.newRisk, 295);
eq('acc layer ในผล', ac.layer, 'acc');
eq('acc ไม่ใช้เป้า 50%: prevLotQty 10 ไม่ตัด qty', C.addLot({ tank: T2, f: 1, price: 145, stop: 140, heldQty: 0, avgCost: 0, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035, stockCapPct: 0.15, heldCostTotal: 80 * 131, prevLotQty: 10 }).qty, 59);
var acN = C.addLot({ tank: T2, f: 1, price: 145, stop: 140, heldQty: 0, avgCost: 0, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035 });
eq('acc ไม่ส่งเพดานต่อหุ้น: qty = งบเร่ง ÷ ระยะ SL = 88', acN.qty, 88);   // 127000×0.0035/5 = 88.9
eq('acc maxRisk = งบเร่งที่เหลือ', Math.round(acN.maxRisk * 1e6) / 1e6, 0.0035);
var ac2 = C.addLot({ tank: T2, f: 1, price: 146, stop: 140, heldQty: 59, avgCost: 145, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035 });
eq('acc ชั้นมีของแล้ว: ความเสี่ยงค้าง = 59×5 → เหลือ = งบ − ค้าง', Math.round(ac2.room), Math.round(T2 * 0.0035 - 59 * 5));
eq('acc ใส่เกินงบที่เหลือ → overRoom', C.addLot({ tank: T2, f: 1, price: 146, stop: 140, heldQty: 59, avgCost: 145, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035 }).overRoom, true);
eq('acc ใส่น้อยกว่างบเหลือ → ไม่ overRoom', C.addLot({ tank: T2, f: 1, price: 146, stop: 140, heldQty: 59, avgCost: 145, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0005 }).overRoom, false);
eq('acc เงินสดคุม', C.addLot({ tank: T2, f: 1, price: 145, stop: 140, heldQty: 0, avgCost: 0, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035, cash: 1450 }).tag, 'cash_limited');
eq('acc FF 0.5 ลดงบเร่ง (maxRisk 0.00175)', Math.round(C.addLot({ tank: T2, f: 0.5, price: 145, stop: 140, heldQty: 0, avgCost: 0, layer: 'acc', riskPct: 0.0035, lotRisk: 0.001 }).maxRisk * 1e6) / 1e6, 0.00175);
// base: เกิน 50% ของไม้ก่อน = ป้าย overRatio แต่ qty ไม่ถูกตัด
var bo = C.addLot({ tank: T2, f: 1, price: 140, stop: 115, heldQty: 40, avgCost: 131, prevLotQty: 40, riskPct: 0.01, lotRisk: 0.0049, ratio: 0.5 });
eq('base เกิน 50%: overRatio = true · qty 24 ไม่ถูกตัดเหลือ 20', bo.overRatio + '|' + bo.qty, 'true|24');
eq('base ไม่เกิน 50% → overRatio false', C.addLot({ tank: T2, f: 1, price: 140, stop: 115, heldQty: 40, avgCost: 131, prevLotQty: 40, riskPct: 0.01, lotRisk: 0.0030, ratio: 0.5 }).overRatio, false);
eq('base ใส่เกินงบเหลือ → overRoom (room = 1270 − 640 = 630)', C.addLot({ tank: T2, f: 1, price: 140, stop: 115, heldQty: 40, avgCost: 131, prevLotQty: 40, riskPct: 0.01, lotRisk: 0.0060 }).overRoom, true);
eq('base งบเต็ม (ค้าง ≥ งบ) → room ≤ 0 · qty 0', (function () { var r = C.addLot({ tank: T2, f: 1, price: 140, stop: 115, heldQty: 80, avgCost: 131, prevLotQty: 80, riskPct: 0.01, lotRisk: 0.001 }); return r.qty + '|' + (r.room <= 0) + '|' + r.maxRisk; })(), '0|true|0');
// เพดานรวม/หุ้นนับทุนทุกชั้น
eq('heldCostTotal รวมทุกชั้น: ทุนรวมเต็มเพดาน → stock_full', C.addLot({ tank: T2, f: 1, price: 145, stop: 140, heldQty: 0, avgCost: 0, layer: 'acc', riskPct: 0.0035, lotRisk: 0.0035, stockCapPct: 0.15, heldCostTotal: 19050 }).tag, 'stock_full');
// เรียกแบบเดิม (ไม่ส่ง lotRisk/layer) ได้ผลเดิม: ตัวอย่างบรรทัด 68
var old1 = C.addLot({ tank: 700000, f: 1, price: 115, stop: 100, heldQty: 700, avgCost: 100, prevLotQty: 700 });
eq('เรียกแบบเดิม: target = 50% และไม่ติด field ใหม่ที่เปลี่ยนผล', old1.qty + '|' + old1.target, a2.qty + '|' + a2.target);
eq('เรียกแบบเดิม ไม่มี position → ยัง NO_POSITION', C.addLot({ tank: 700000, price: 115, stop: 100, heldQty: 0, avgCost: 0 }).err, 'NO_POSITION');
// firstLot + Risk % ต่อไม้
var fl = C.firstLot({ tank: T2, f: 1, entry: 131, stop: 115, tier: 'A', riskPct: 0.01, tierCapPct: 0.15, stockCapPct: 0.15, lotRisk: 0.006 });
eq('firstLot Risk 0.6% → 47 หุ้น (762 ÷ 16)', fl.qty, 47);
eq('firstLot ไม่เกินงบ (maxRisk 1.0%) → overBudget false', fl.overBudget, false);
eq('firstLot Risk 2% เกินงบ → overBudget true', C.firstLot({ tank: T2, f: 1, entry: 131, stop: 115, tier: 'A', riskPct: 0.01, lotRisk: 0.02 }).overBudget, true);
eq('firstLot FF 0.75 ลดงบ → maxRisk 0.0075', C.firstLot({ tank: T2, f: 0.75, entry: 131, stop: 115, tier: 'A', riskPct: 0.01, lotRisk: 0.006 }).maxRisk, 0.0075);
eq('firstLot Risk ใหญ่แต่ติดเพดานไม้แรกของ Tier', C.firstLot({ tank: T2, f: 1, entry: 131, stop: 115, tier: 'A', riskPct: 0.05, tierCapPct: 0.1, stockCapPct: 0.25, lotRisk: 0.05 }).qty, Math.floor(T2 * 0.1 / 131));
eq('firstLot ไม่ส่ง lotRisk = สูตรเดิม (งบ×f)', C.firstLot({ tank: 700000, f: 1, entry: 100, stop: 90, tier: 'A' }).qty, 700);
// layer2 แยกชั้น
var l2L = C.layer2({ tank: T2, positions: [{ qty: 80, px: 147, stop: 115 }, { qty: 59, px: 147, stop: 140, layer: 'acc' }] });
near('layer2 รวมทุกชั้นตาม SL ของชั้น: 80×32 + 59×7', l2L.risk, 80 * 32 + 59 * 7);
near('layer2 riskAcc = 59×7', l2L.riskAcc, 59 * 7);
near('layer2 riskBase = 80×32', l2L.riskBase, 80 * 32);
var l2O = C.layer2({ tank: 700000, positions: [{ qty: 700, px: 110, stop: 100 }] });
eq('layer2 เดิม (ไม่มี layer) riskAcc = 0 · ผลรวมเดิม', l2O.riskAcc + '|' + l2O.risk, '0|7000');

/* ───────── RG2b · ถังแยก Winner / Ladder / Sat ───────── */
section('RG2b poolSplit');
var ps = C.poolSplit({ total: 1000000 });
eq('poolSplit ค่าเริ่ม 50/30/20 ok', ps.ok, true);
near('poolSplit Winner 500,000', ps.winner, 500000);
near('poolSplit Ladder 300,000', ps.ladder, 300000);
near('poolSplit Sat 200,000', ps.sat, 200000);
eq('poolSplit รวม 99 → SUM_NOT_100', C.poolSplit({ total: 1e6, pct: { winner: 50, ladder: 30, sat: 19 } }).err, 'SUM_NOT_100');
eq('poolSplit ติดลบ → BAD_PCT', C.poolSplit({ total: 1e6, pct: { winner: -10, ladder: 60, sat: 50 } }).err, 'BAD_PCT');
eq('poolSplit เกิน 100 → BAD_PCT', C.poolSplit({ total: 1e6, pct: { winner: 101, ladder: 0, sat: -1 } }).err, 'BAD_PCT');
eq('poolSplit 0/100/0 ผ่าน', C.poolSplit({ total: 1e6, pct: { winner: 0, ladder: 100, sat: 0 } }).ladder, 1e6);
eq('poolSplit ไม่มียอดรวม → NO_TOTAL', C.poolSplit({ total: 0 }).err, 'NO_TOTAL');
eq('poolSplit ค่าเริ่ม DEFAULTS.poolSplit', JSON.stringify(C.DEFAULTS.poolSplit), '{"winner":50,"ladder":30,"sat":20}');

section('RG2b poolFree · ถังอิสระ');
var pfW = C.poolFree({ pool: 500000, held: 200000 });
near('Winner ว่าง = ถัง − ถือ', pfW.free, 300000);
var LB = C.ladder({ tier: 'A', tank: 300000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }], budgetPct: 0.1667 });
var pfL0 = C.poolFree({ pool: 300000, held: 0, reserved: 0 });
var pfL1 = C.poolFree({ pool: 300000, held: LB.heldCost, reserved: LB.reservedCost });
near('วางบันไดแล้ว Ladder ว่างลด', pfL0.free - pfL1.free, LB.cost);
near('วางบันไดแล้ว Winner ว่างเท่าเดิม', C.poolFree({ pool: 500000, held: 200000 }).free, pfW.free);
eq('ใช้เกินถัง = over (เตือน ไม่ปิด)', C.poolFree({ pool: 100000, held: 150000 }).over, true);
eq('ใช้เกินถัง ว่าง = 0', C.poolFree({ pool: 100000, held: 150000 }).free, 0);
eq('ไม่มีถัง → NO_POOL', C.poolFree({}).err, 'NO_POOL');

section('RG2b ladderBudget · 5% ของบัญชี × f');
var lb = C.ladderBudget({ acct: 1000000, pool: 300000, f: 1 });
near('งบเต็ม 5% ของบัญชี = 50,000', lb.full, 50000);
near('f 100% → 50,000', lb.budget, 50000);
near('≈ 16.67% ของถัง Ladder 30%', lb.budgetPctPool, 50000 / 300000, 1e-9);
near('f 75% → 37,500', C.ladderBudget({ acct: 1000000, pool: 300000, f: 0.75 }).budget, 37500);
near('f 50% → 25,000', C.ladderBudget({ acct: 1000000, pool: 300000, f: 0.5 }).budget, 25000);
near('ตั้ง maxAcctPct 4 → 40,000', C.ladderBudget({ acct: 1000000, pool: 300000, maxAcctPct: 4 }).budget, 40000);
eq('ไม่มีบัญชี → NO_ACCT', C.ladderBudget({ pool: 1 }).err, 'NO_ACCT');

section('RG2b canPlaceLadder · ถัง Ladder อิสระ ไม่มีประตู');
var NL2 = C.ladder({ tier: 'A', tank: 300000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }], budgetPct: 50000 / 300000 });
var cp0 = C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, wCost: 9e9 });
eq('ผ่านแม้ Winner ใช้เงินเต็ม (wCost ไม่เกี่ยว)', cp0.allowed, true);
eq('ไม่มีเหตุผล GATE_*', cp0.reasons.filter(function (r) { return /^GATE_/.test(r); }).length, 0);
var cp1 = C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, existingLadders: [NL2, NL2, NL2, NL2, NL2, NL2] });
eq('ถัง Ladder เต็ม → NO_CASH', cp1.reasons.indexOf('NO_CASH') >= 0, true);
eq('ไม่มี L_SHARE_OVER / LAYER2_OVER', cp1.reasons.indexOf('L_SHARE_OVER') + cp1.reasons.indexOf('LAYER2_OVER'), -2);
eq('maxCost 40,000 < ทุนบันได → STOCK_OVER', C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, maxCost: 40000 }).reasons.indexOf('STOCK_OVER') >= 0, true);
eq('maxCost 60,000 ผ่าน', C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, maxCost: 60000 }).allowed, true);
eq('Winner cap 25% ของถัง Winner: 500,000 × 25% ÷ 100 = 1,250 หุ้น', C.firstLot({ tank: 500000, entry: 100, stop: 99, f: 1, tier: 'A', tierCapPct: 1, stockCapPct: 0.25, riskPct: 0.5 }).qty, 1250);
eq('firstLot ของ Winner ไม่กระทบถัง Ladder (ถังแยก ใส่ tank Winner)', C.firstLot({ tank: 500000, entry: 100, stop: 90, f: 1, tier: 'A', tierCapPct: 1, stockCapPct: 0.25 }).qty, 500);

console.log('\n' + (fail === 0 ? 'PASS' : 'FAIL') + '  ' + pass + ' ผ่าน · ' + fail + ' ไม่ผ่าน');
process.exit(fail === 0 ? 0 : 1);
