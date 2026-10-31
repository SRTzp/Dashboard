# RG2b — retired / changed old-test expectations (Run 2)

Rule applied: only expected values / fixture inputs changed in old suites; no test deleted unless the feature was removed by the brief (marked **inverted/removed**).
Causes (all intended by the brief):
- **Pool split**: Winner/Ladder/Sat sizes now come from the 50/30/20 pools. Where a test's intent was orthogonal to pool size, the fixture is *pinned* (`settings.pools` seeded so Winner/Sat pool = the old capital: helpers `pin_winner_pool` (p24), `pin_sat_pool` (p54), `pin_winner`/`pin_sat` params, `ln3fix_common.launch2(winnerCap=15)`); otherwise the expected number was recomputed.
- **Removed features (inverted/removed)**: Macro size ×0.6/×0.4, f-gate / `coreGate`, tier A/B table → single `winnerCap`, Layer-2 cap/levels, total cap / L-share, W/L strategy selector and W→L convert, Core/Main/Tactical Port bars → Winner·Ladder·Sat pool line, Sat Main%/Tactical% split → whole-pool sizing, scope labels Winner|Ladder|Sat.
- **Sat v2 base**: RPT lists Main [0.5..2]/Tactical [0.25..1], default RPT 1.5/0.75, caps 1.4×/1.2×, brake DD 3%, new-trades quota 4 (Main+Tactical combined).
- **§4.7 DD per pool** (Winner / Ladder / Sat), table columns `DD W / DD L / DD S`.
- **core_size_test.js**: 12 `canPlaceLadder` cases (gate/L_SHARE/LAYER2 removed): ชั้น 2 รวมบันไดใหม่ = 2.24% · ประตูปิด (green) · ประตูปิด (unknown) · ไม่ส่ง gate = งด · ชั้น 2 รวมบันไดใหม่เกิน 20% · เกิน → ไม่อนุญาต · ชั้น 2 นับที่จองของบันไดเดิมด้วย · เงินสดไม่พอจอง · L รวมเกิน 30% · 7E-2b-1 l2Cap 0.25 · 7E-2b-1 shareCap 0.20 · รวมเหตุผลหลายข้อ. Count 471 old + 31 new = 502.
- **Source fixes made while retiring** (not test edits): Plan-form size row no longer shows Macro "ลด 40%" for non-MR plans; `satV2Cfg` output stamped `poolMig:'RG2b'` (re-saving a read cfg no longer re-migrates caps/brake); ≤340px plan status-line font.
- **Also**: `satMacroFactors()` now returns `{neutral, against, mr}` (against = 1; MR keeps 0.6 via `mr`); Watchlist row shows a track badge only for Ladder (Winner = default, avoids row wrap at 355px).

Per-file changes (`-` old → `+` new, shortened to 170 chars):


## tests/core_size_test.js

    -near('ชั้น 2 รวมบันไดใหม่ = 2.24%', ok1.pctFull, 15680 / 700000, 1e-9);
    +near('RG2b: ไม่มี pctFull (Layer 2 ถูกถอด) · sharePct = ทุนบันไดใหม่ ÷ ถัง Ladder', ok1.sharePct, NL.cost / 700000, 1e-9);
    -eq('ประตูปิด (green)', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: { open: false, reason: 'green' }, ladder: NL }).reasons.indexOf('GATE_green') >= 0, true);
    -eq('ประตูปิด (unknown)', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: { open: false, reason: 'unknown' }, ladder: NL }).reasons.indexOf('GATE_unknown') >= 0, true);
    -eq('ไม่ส่ง gate = งด', C.canPlaceLadder({ tank: 700000, tier: 'A', ladder: NL }).allowed, false);
    +eq('ประตูปิด (green)', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: { open: false, reason: 'green' }, ladder: NL }).reasons.indexOf('GATE_green') >= 0, false);   /*
    +eq('ประตูปิด (unknown)', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: { open: false, reason: 'unknown' }, ladder: NL }).reasons.indexOf('GATE_unknown') >= 0, false)
    +eq('ไม่ส่ง gate = งด', C.canPlaceLadder({ tank: 700000, tier: 'A', ladder: NL }).allowed, true);   /* RG2b: ไม่มีประตู f */
    -eq('ชั้น 2 รวมบันไดใหม่เกิน 20%', big.reasons.indexOf('LAYER2_OVER') >= 0, true);
    -eq('เกิน → ไม่อนุญาต', big.allowed, false);
    +eq('ชั้น 2 รวมบันไดใหม่เกิน 20%', big.reasons.indexOf('LAYER2_OVER') >= 0, false);   /* RG2b: ไม่มีเช็กชั้น 2 */
    +eq('เกิน → ไม่อนุญาต', big.allowed, true);   /* RG2b */
    -eq('ชั้น 2 นับที่จองของบันไดเดิมด้วย', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, positions: [{ qty: 1000, px: 170, stop: 70 }], res
    -eq('เงินสดไม่พอจอง', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 650000 }).reasons.indexOf('NO_CASH') >= 0, true);
    -eq('L รวมเกิน 30%', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL, NL] }).reasons.indexOf('L_SHARE_OVER') >= 0
    +eq('ชั้น 2 นับที่จองของบันไดเดิมด้วย', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, positions: [{ qty: 1000, px: 170, stop: 70 }], res
    +eq('เงินสดไม่พอจอง', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 650000 }).reasons.indexOf('NO_CASH') >= 0, false);   /* RG2b: ไม้ W ไม่
    +eq('L รวมเกิน 30%', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL, NL] }).reasons.indexOf('L_SHARE_OVER') >= 0
    -eq('7E-2b-1: ส่ง l2Cap 0.25 → เคส 20.8% ผ่านชั้น 2', big.reasons.indexOf('LAYER2_OVER') >= 0 && C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCo
    -eq('7E-2b-1: shareCap 0.20 → 3 ตัวเดิม+1 ใหม่ เกิน', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL], shareCap:
    +eq('7E-2b-1: ส่ง l2Cap 0.25 → เคส 20.8% ผ่านชั้น 2', big.reasons.indexOf('LAYER2_OVER') >= 0 && C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCo
    +eq('7E-2b-1: shareCap 0.20 → 3 ตัวเดิม+1 ใหม่ เกิน', C.canPlaceLadder({ tank: 700000, tier: 'A', gate: okGate, ladder: NL, wCost: 0, existingLadders: [NL, NL], shareCap:
    -eq('รวมเหตุผลหลายข้อ', C.canPlaceLadder({ tank: 700000, tier: 'B', gate: { open: false, reason: 'green' }, ladder: NL, wCost: 650000 }).reasons.length >= 3, true);
    +eq('รวมเหตุผลหลายข้อ', C.canPlaceLadder({ tank: 700000, tier: 'B', gate: { open: false, reason: 'green' }, ladder: NL, wCost: 650000 }).reasons.length === 1, true);   /*
    +/* ───────── RG2b · ถังแยก Winner / Ladder / Sat ───────── */
    +section('RG2b poolSplit');
    +var ps = C.poolSplit({ total: 1000000 });
    +eq('poolSplit ค่าเริ่ม 50/30/20 ok', ps.ok, true);
    +near('poolSplit Winner 500,000', ps.winner, 500000);
    +near('poolSplit Ladder 300,000', ps.ladder, 300000);
    +near('poolSplit Sat 200,000', ps.sat, 200000);
    +eq('poolSplit รวม 99 → SUM_NOT_100', C.poolSplit({ total: 1e6, pct: { winner: 50, ladder: 30, sat: 19 } }).err, 'SUM_NOT_100');
    +eq('poolSplit ติดลบ → BAD_PCT', C.poolSplit({ total: 1e6, pct: { winner: -10, ladder: 60, sat: 50 } }).err, 'BAD_PCT');
    +eq('poolSplit เกิน 100 → BAD_PCT', C.poolSplit({ total: 1e6, pct: { winner: 101, ladder: 0, sat: -1 } }).err, 'BAD_PCT');
    +eq('poolSplit 0/100/0 ผ่าน', C.poolSplit({ total: 1e6, pct: { winner: 0, ladder: 100, sat: 0 } }).ladder, 1e6);
    +eq('poolSplit ไม่มียอดรวม → NO_TOTAL', C.poolSplit({ total: 0 }).err, 'NO_TOTAL');
    +eq('poolSplit ค่าเริ่ม DEFAULTS.poolSplit', JSON.stringify(C.DEFAULTS.poolSplit), '{"winner":50,"ladder":30,"sat":20}');
    +
    +section('RG2b poolFree · ถังอิสระ');
    +var pfW = C.poolFree({ pool: 500000, held: 200000 });
    +near('Winner ว่าง = ถัง − ถือ', pfW.free, 300000);
    +var LB = C.ladder({ tier: 'A', tank: 300000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }], budgetPct: 0.1667 });
    +var pfL0 = C.poolFree({ pool: 300000, held: 0, reserved: 0 });
    +var pfL1 = C.poolFree({ pool: 300000, held: LB.heldCost, reserved: LB.reservedCost });
    +near('วางบันไดแล้ว Ladder ว่างลด', pfL0.free - pfL1.free, LB.cost);
    +near('วางบันไดแล้ว Winner ว่างเท่าเดิม', C.poolFree({ pool: 500000, held: 200000 }).free, pfW.free);
    +eq('ใช้เกินถัง = over (เตือน ไม่ปิด)', C.poolFree({ pool: 100000, held: 150000 }).over, true);
    +eq('ใช้เกินถัง ว่าง = 0', C.poolFree({ pool: 100000, held: 150000 }).free, 0);
    +eq('ไม่มีถัง → NO_POOL', C.poolFree({}).err, 'NO_POOL');
    +
    +section('RG2b ladderBudget · 5% ของบัญชี × f');
    +var lb = C.ladderBudget({ acct: 1000000, pool: 300000, f: 1 });
    +near('งบเต็ม 5% ของบัญชี = 50,000', lb.full, 50000);
    +near('f 100% → 50,000', lb.budget, 50000);
    +near('≈ 16.67% ของถัง Ladder 30%', lb.budgetPctPool, 50000 / 300000, 1e-9);
    +near('f 75% → 37,500', C.ladderBudget({ acct: 1000000, pool: 300000, f: 0.75 }).budget, 37500);
    +near('f 50% → 25,000', C.ladderBudget({ acct: 1000000, pool: 300000, f: 0.5 }).budget, 25000);
    +near('ตั้ง maxAcctPct 4 → 40,000', C.ladderBudget({ acct: 1000000, pool: 300000, maxAcctPct: 4 }).budget, 40000);
    +eq('ไม่มีบัญชี → NO_ACCT', C.ladderBudget({ pool: 1 }).err, 'NO_ACCT');
    +
    +section('RG2b canPlaceLadder · ถัง Ladder อิสระ ไม่มีประตู');
    +var NL2 = C.ladder({ tier: 'A', tank: 300000, sl: 70, levels: [{ px: 100 }, { px: 90 }, { px: 80 }], budgetPct: 50000 / 300000 });
    +var cp0 = C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, wCost: 9e9 });
    +eq('ผ่านแม้ Winner ใช้เงินเต็ม (wCost ไม่เกี่ยว)', cp0.allowed, true);
    +eq('ไม่มีเหตุผล GATE_*', cp0.reasons.filter(function (r) { return /^GATE_/.test(r); }).length, 0);
    +var cp1 = C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, existingLadders: [NL2, NL2, NL2, NL2, NL2, NL2] });
    +eq('ถัง Ladder เต็ม → NO_CASH', cp1.reasons.indexOf('NO_CASH') >= 0, true);
    +eq('ไม่มี L_SHARE_OVER / LAYER2_OVER', cp1.reasons.indexOf('L_SHARE_OVER') + cp1.reasons.indexOf('LAYER2_OVER'), -2);
    +eq('maxCost 40,000 < ทุนบันได → STOCK_OVER', C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, maxCost: 40000 }).reasons.indexOf('STOCK_OVER') >= 0, true);
    +eq('maxCost 60,000 ผ่าน', C.canPlaceLadder({ tank: 300000, tier: 'A', ladder: NL2, maxCost: 60000 }).allowed, true);
    +eq('Winner cap 25% ของถัง Winner: 500,000 × 25% ÷ 100 = 1,250 หุ้น', C.firstLot({ tank: 500000, entry: 100, stop: 99, f: 1, tier: 'A', tierCapPct: 1, stockCapPct: 0.25, 
    +eq('firstLot ของ Winner ไม่กระทบถัง Ladder (ถังแยก ใส่ tank Winner)', C.firstLot({ tank: 500000, entry: 100, stop: 90, f: 1, tier: 'A', tierCapPct: 1, stockCapPct: 0.25 
    +

## tests/ln3fix_common.py

    -def launch(pw, w, h, cards=True, mut=None):
    +def launch(pw, w, h, cards=True, mut=None, pin_winner=False):
    +        if pin_winner: P24.pin_winner_pool(doc)   # RG2b — ตรึงถัง Winner = ทุน Core เดิม
    -def launch2(pw, w, h, trades, cards, mut=None, fx=33, core_risk=None):
    +def launch2(pw, w, h, trades, cards, mut=None, fx=33, core_risk=None, pin_winner=False):
    +        if pin_winner: cr["winnerCap"] = 15   # RG2b — เพดานต่อหุ้นเดิม (Tier A 15%) สำหรับเทสเก่าที่ตรึงถัง
    +        if pin_winner: P24.pin_winner_pool(doc)   # RG2b — ตรึงถัง Winner = ทุน Core เดิม

## tests/run_tests.py

    -    check(f"[{label}] Calc.satLot XAUUSD pure -> 0.19 lot",
    +    check(f"[{label}] Calc.satLot XAUUSD pure -> 0.15 lot",
    -    check(f"[{label}] Calc.satLot S50 pure -> 6 สัญญา",
    +    check(f"[{label}] Calc.satLot S50 pure -> 5 สัญญา",
    -    check(f"[{label}] sat7dCalc (live path) XAUUSD main/XM -> 0.19 lot",
    -          xau_live.get("lot") is not None and abs(xau_live["lot"] - 0.19) < 1e-9,
    +    check(f"[{label}] sat7dCalc (live path) XAUUSD main/XM -> 0.15 lot",
    +          xau_live.get("lot") is not None and abs(xau_live["lot"] - 0.15) < 1e-9,
    -    check(f"[{label}] sat7dCalc (live path) S50 main/Pi -> 6 สัญญา",
    -          s50_live.get("lot") == 6,
    +    check(f"[{label}] sat7dCalc (live path) S50 main/Pi -> 5 สัญญา",
    +          s50_live.get("lot") == 5,

## tests/run_tests_phase106.py

    -        check(f"{tag} B3 กาง: ทีละ sub-portfolio (Core.US 19% $98k→$160k · อื่น No goal set)", len(subs) == 4 and "Core.US" in subs[0] and "$98k→$160k" in subs[0] and "1
    +        check(f"{tag} B3 กาง: ทีละ sub-portfolio (RG2b: Winner 19% $98k→$160k · อื่น No goal set)", len(subs) == 4 and "Winner" in subs[0] and "$98k→$160k" in subs[0] an
    -        check(f"{tag} บันทึก sub-goal (Sat) ถูกเก็บ · ของเดิม (Core.US) ไม่หาย", sg and sg["main"]["Sat"]["target"] == 12000 and sg["main"]["Sat"]["now"] == 5000 and sg[
    +        check(f"{tag} บันทึก sub-goal (Sat) ถูกเก็บ · ของเดิม (Core.US) ย้ายเป็น Winner ไม่หาย (RG2b §4.7)", sg and sg["main"]["Sat"]["target"] == 12000 and sg["main"]["

## tests/run_tests_phase109.py

    -      s.ddState = {core: mk(700000, cd), sat: mk(26000, sd)}; B.trades = []; saveBook(A); render(); todayRefresh(true); }""", [sat_dd, core_dd]); settle(page, 500)
    +      s.pools = {winner: 700000/1740000*100, ladder: 0, sat: 1040000/1740000*100, mig:'RG2b', reviewed:true}; s.ddState = {core: mk(700000, cd), winner: mk(700000, cd), 
    -        check(f"{tag} §B5b DD Core ถึงขั้น → ชิป '⚠ DD Core … ›' ที่หัว Core Port เท่านั้น (Sat กลับเป็น Risk ✓)", cc.startswith("⚠ DD Core") and "12.5%" in cc and abs(s
    +        check(f"{tag} §B5b DD Core ถึงขั้น → ชิป ⚠ DD Winner … › ที่หัว Core Port (RG2b §4.7 ชื่อถัง) เท่านั้น (Sat กลับเป็น Risk ✓)", cc.startswith("⚠ DD Winner") and "

## tests/run_tests_phase11.py

    -    check(f"{tag} PF3 ขนาดไม้ตาม Macro อย่างเดียว: Macro ▼ → 'ขนาดไม้: ลด 40% (สวน Macro)' + มีสวิตช์ [ใช้ไม้เต็ม] โดยไม่ขึ้นกับ Trend", "ลด 40% (สวน Macro)" in (txt(pag
    +    check(f"{tag} PF3 ขนาดไม้ตาม Macro อย่างเดียว: Macro ▼ → 'ขนาดไม้: ลด 40% (สวน Macro)' + มีสวิตช์ [ใช้ไม้เต็ม] โดยไม่ขึ้นกับ Trend", "ลด 40%" not in (txt(page, f"{C}
    -    check(f"{tag} การ์ด: 'ขนาดไม้: ลด 40% (สวน Macro)'", "ขนาดไม้: ลด 40% (สวน Macro)" in txt(page, f'{C} [data-f2c-row="size"]'), txt(page, f'{C} [data-f2c-row="size"]'
    +    check(f"{tag} การ์ด: 'ขนาดไม้: ลด 40% (สวน Macro)'", "ขนาดไม้: เต็ม" in txt(page, f'{C} [data-f2c-row="size"]'), txt(page, f'{C} [data-f2c-row="size"]'))   # RG2b
    -          exp["factor"] == 0.6 and abs(exp["lot"] - exp["expCut"]) < 1e-9 and 0.55 <= exp["lot"] / exp["full"] <= 0.65, json.dumps(exp))
    +          exp["factor"] == 1 and abs(exp["lot"] - exp["full"]) < 1e-9, json.dumps(exp))   # RG2b — ไม่ลดตาม Macro: lot = เต็ม
    -    # สวิตช์ไม่ตามกฎ
    -    page.click(f'{C} [data-size-switch]'); page.wait_for_timeout(250)
    -    check(f"{tag} สวิตช์: 'ใช้ไม้เต็ม (ไม่ตามกฎ)' → idea.size_full_override = true · ป้ายส้ม 'ไม่ตามกฎ' · 'ขนาดไม้: เต็ม'",
    -          idea(page, "iA").get("size_full_override") is True and page.locator(f"{C} [data-off-rule]").count() == 1 and "ขนาดไม้: เต็ม" in txt(page, f'{C} [data-f2c-row="
    +    # RG2b — สวิตช์ 'ใช้ไม้เต็ม' ถอดพร้อมตัวคูณ Macro: ไม่มีปุ่ม · lot เท่าเต็มเสมอ · ไม่มีป้าย 'ไม่ตามกฎ'
    +    check(f"{tag} สวิตช์ 'ใช้ไม้เต็ม' ไม่มีแล้ว · ไม่มีป้าย 'ไม่ตามกฎ' · size_full_override ไม่ถูกตั้ง",
    +          page.locator(f"{C} [data-size-switch]").count() == 0 and page.locator(f"{C} [data-off-rule]").count() == 0 and not idea(page, "iA").get("size_full_override"))
    -    check(f"{tag} lot: ใช้ไม้เต็ม → lot เท่าเต็ม ({full['lot']}) · heat คิดจาก lot ใหม่ (สูงกว่าตอนลด)", full["factor"] == 1 and full["lot"] == exp["full"] and (full["he
    -    page.click(f'{C} [data-size-switch]'); page.wait_for_timeout(250)
    -    check(f"{tag} สวิตช์: กดอีกครั้ง = กลับตามกฎ (override=false · ป้ายหาย · ลด 40%)", idea(page, "iA").get("size_full_override") is False and page.locator(f"{C} [data-o
    +    check(f"{tag} lot: เท่าเต็ม ({full['lot']}) · heat เท่าเดิม", full["factor"] == 1 and full["lot"] == exp["full"] and (full["heatPct"] or 0) == (heat_cut or 0), f"{fu
    -    check(f"{tag} ก่อนบันทึก: ลด 40% (Macro ▼ สวน Long + Trend ▼ สวน)", "ลด 40%" in txt(page, f'{O} [data-f2c-row="size"]'))
    +    check(f"{tag} ก่อนบันทึก: ไม่ลด 40% (RG2b ถอดตัวคูณ Macro · Macro ▼ สวน Long + Trend ▼ สวน)", "ลด 40%" not in txt(page, f'{O} [data-f2c-row="size"]'))
    -          got["size_rule"] == 0.6 and got["off_rule"] is False and got["sizeFactor"] == 0.6 and got["macro_state"] == "against" and got["macro_stance"] == "down"
    +          got["size_rule"] == 1 and got["off_rule"] is False and got["sizeFactor"] is None and got["macro_state"] == "against" and got["macro_stance"] == "down"
    -    check(f"{tag} บันทึก order (สวนทั้งคู่): qty = lot ที่ลด ~60% ({t['qty']} vs เต็ม {lot_full})", 0.55 <= t["qty"] / lot_full <= 0.65, f"{t['qty']} {lot_full}")
    +    check(f"{tag} บันทึก order (สวนทั้งคู่): qty = lot ที่ลด ~60% ({t['qty']} vs เต็ม {lot_full})", t["qty"] == lot_full, f"{t['qty']} {lot_full}")   # RG2b — ไม่ลดตาม M
    -    check(f"{tag} รายละเอียดไม้: 'Macro สวน (▼ v001) · Trend ตาม? …' — Long + Trend ▼ = 'Trend สวน' · Driver P2 · ลด 40% (ไม่มีป้าย)", line.startswith("Macro สวน (▼ v001
    +    check(f"{tag} รายละเอียดไม้: 'Macro สวน (▼ v001) · Trend ตาม? …' — Long + Trend ▼ = 'Trend สวน' · Driver P2 · ลด 40% (ไม่มีป้าย)", line.startswith("Macro สวน (▼ v001
    -    check(f"{tag} บันทึก order (ใช้ไม้เต็มทั้งที่กฎ 0.6): off_rule true · size_rule 0.6 · sizeFactor null", t["off_rule"] is True and t["size_rule"] == 0.6 and t["sizeFa
    +    check(f"{tag} บันทึก order (ใช้ไม้เต็มทั้งที่กฎ 0.6): off_rule true · size_rule 0.6 · sizeFactor null", t["off_rule"] is False and t["size_rule"] == 1 and t["sizeFac
    -    check(f"{tag} รายละเอียดไม้: มีป้าย 'ไม่ตามกฎ' เมื่อ off_rule", "ไม่ตามกฎ" in line and "· เต็ม" in line, line)
    +    check(f"{tag} รายละเอียดไม้: มีป้าย 'ไม่ตามกฎ' เมื่อ off_rule", "ไม่ตามกฎ" not in line and "· เต็ม" in line, line)   # RG2b — ไม่มีกฎให้ไม่ตาม

## tests/run_tests_phase111.py

    -    return C.launch2(pw, w, h, trades or [], cards or {})
    +    return C.launch2(pw, w, h, trades or [], cards or {}, pin_winner=True)   # RG2b — ถัง Winner ตรึงเท่าทุน Core เดิม
    -        check(f"{tag} ฟอร์มยังมี: บัญชี · Ticker · กลยุทธ์ · Entry · Stop · ขนาดไม้ · ปุ่มบันทึก", cnt(page, "#cnAcctBox, #cnTicker, #cnStratBox, #cnEntry, #cnStop, #cnR
    +        check(f"{tag} ฟอร์มยังมี: บัญชี · Ticker · Entry · Stop · ขนาดไม้ · ปุ่มบันทึก (RG2b ถอดตัวเลือกกลยุทธ์ · ไม่มี #cnStratBox)", cnt(page, "#cnAcctBox, #cnTicker, 
    -    b, page, ce, pe = C.launch(pw, w, h, cards=cd)
    +    b, page, ce, pe = C.launch(pw, w, h, cards=cd, pin_winner=True)

## tests/run_tests_phase13.py

    -    page.wait_for_timeout(150)
    +    page.wait_for_timeout(1000)   # RG2b: ddSync เขียน DD 3 ถัง → รอ echo ของ mock Firestore ก่อนอ่าน
    +    page.wait_for_timeout(600)
    +    seed(page, main=[T("m1", "core", "open", date="2020-01-06")], fam=[T("f1", "satB", "open", qty=1, date=__import__("datetime").date.today().isoformat())])   # RG2b: s

## tests/run_tests_phase23.py

    -        check(f"{tag} tests/core_size_test.js (รันบนสำเนาใน index.html ผ่านเบราว์เซอร์) = 471/471 (CZ1: +22 เคส · LN3fix2: +29 เคส · เดิม 420 ผ่านครบ) · exit 0", bool(m)
    +        check(f"{tag} tests/core_size_test.js (รันบนสำเนาใน index.html ผ่านเบราว์เซอร์) = 502/502 (RG2b: +31 เคส · เดิม 471 ผ่านครบ) · exit 0", bool(m) and m.group(1) ==
    -              vals == {"mk": "US", "ra": "1.25", "rb": "1.25", "a": "15", "b": "10", "ca": "25", "cb": "25", "add": "50", "cap": "20", "warn": "15", "em": "7", "lb": "10
    +              vals == {"mk": "US", "ra": "1.25", "rb": "1.25", "a": "25", "b": "25", "ca": "25", "cb": "25", "add": "50", "cap": "20", "warn": "15", "em": "7", "lb": "5"
    -        check(f"{tag} ตั้งค่า: ทุกช่องมีป้ายหน่วย (% ของถัง Core · % ของไม้ก่อนหน้า · ไม้ (1–6) · % ใต้ Stop · สัปดาห์) · ป้าย '% ของถัง Core' ≥ 8 ช่อง (TIER2: +6 ช่องเก
    +        check(f"{tag} ตั้งค่า: ทุกช่องมีป้ายหน่วย (% ของถัง Core · % ของไม้ก่อนหน้า · ไม้ (1–6) · % ใต้ Stop · สัปดาห์) · ป้าย '% ของถัง Core' ≥ 8 ช่อง (TIER2: +6 ช่องเก
    +               json.dumps(units, ensure_ascii=False))
    -              bm["settings"]["coreRisk"]["riskPct"] == 0.75 and len(bm["settings"]["coreRisk"]) == 29 and bm["settings"]["coreRisk"]["market"] == "US", json.dumps(bm["se
    +              bm["settings"]["coreRisk"]["riskPct"] == 0.75 and len(bm["settings"]["coreRisk"]) == 22 and bm["settings"]["coreRisk"]["market"] == "US", json.dumps(bm["se
    -              opts["tierCap"] == {"A": 0.15, "B": 0.1} and opts["addRatio"] == 0.5 and abs(opts["layer2Cap"] - 0.2) < 1e-12 and abs(opts["layer2Warn"] - 0.15) < 1e-12 an
    -              and abs(opts["ladderBudget"] - 0.1) < 1e-12 and abs(opts["ladderRiskCap"] - 0.025) < 1e-12 and abs(opts["ladderShareCap"] - 0.3) < 1e-12 and opts["gateStre
    +              opts["tierCap"] == {"A": 0.25, "B": 0.25} and opts["addRatio"] == 0.5 and abs(opts["layer2Cap"] - 0.2) < 1e-12 and abs(opts["layer2Warn"] - 0.15) < 1e-12 a
    +              and opts["ladderMaxAcctPct"] == 5 and abs(opts["ladderRiskCap"] - 0.04) < 1e-12 and "ladderShareCap" not in opts and "gateStreak" not in opts, json.dumps(o

## tests/run_tests_phase24.py

    -def doc_with(main_trades=None, core_cap=700000, main_market="both", fam_market=None):
    +def pin_winner_pool(doc):
    +    """RG2b — เทส W เก่าคิดจากถัง Core = capital.core ทั้งก้อน: ตรึงสัดส่วนถังให้ถัง Winner = ทุน Core เดิม (ที่เหลือแบ่ง Ladder/Sat เท่ากัน) · ไม่แตะค่าที่คาดหวังของเคส
    +    for b in doc["books"].values():
    +        s = b["settings"]; cap = s.get("capital") or {}; fx = s.get("fx") or 1
    +        core, sat = float(cap.get("core") or 0), float(cap.get("satB") or 0) * fx
    +        if core <= 0: continue
    +        wp = core / (core + sat) * 100; s["pools"] = {"winner": wp, "ladder": (100 - wp) / 2, "sat": (100 - wp) / 2, "mig": "RG2b", "reviewed": True}
    +
    +
    +def pin_both_pools(doc):
    +    """RG2b — ตรึงถัง Winner = ทุน Core เดิม และถัง Sat = ทุน Sat เดิม (Ladder 0) — เทสที่ไม่เกี่ยวกับบันได"""
    +    for b in doc["books"].values():
    +        s = b["settings"]; cap = s.get("capital") or {}; fx = s.get("fx") or 1
    +        core, sat = float(cap.get("core") or 0), float(cap.get("satB") or 0) * fx
    +        if core + sat <= 0: continue
    +        s["pools"] = {"winner": core / (core + sat) * 100, "ladder": 0, "sat": sat / (core + sat) * 100, "mig": "RG2b", "reviewed": True}
    +
    +
    +def doc_with(main_trades=None, core_cap=700000, main_market="both", fam_market=None, pin_winner=False):
    +    doc = _doc_with(main_trades, core_cap, main_market, fam_market)
    +    if pin_winner: pin_winner_pool(doc)
    +    return doc
    +
    +
    +def _doc_with(main_trades=None, core_cap=700000, main_market="both", fam_market=None):
    -    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with())
    +    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(pin_winner=True))
    -        check(f"{tag} scope หุ้น กด ＋ → เปิด sheet 'แผน Core ใหม่'", sheet_open(page, "new") and "แผน Core ใหม่" in (txt(page, ".core-sheet h3") or ""))
    +        check(f"{tag} scope หุ้น กด ＋ → เปิด sheet 'แผน Core ใหม่'", sheet_open(page, "new") and "New Winner plan" in (txt(page, ".core-sheet h3") or ""))   # RG2b — หัว
    -        check(f"{tag} Tier B เพดาน 5% (35,000) · Entry 100 Stop 99 → ชนเพดาน Tier: จาก 350 → ปัดหลัก 100 = 300 (TH)", q() == "300" and txt(page, "#cnRes [data-c-tag]") =
    +        check(f"{tag} RG2b เพดานต่อหุ้นค่าเดียว 25% ของถัง Winner (175,000) · Entry 100 Stop 99 → ชนเพดาน: 1,700 หุ้น (TH · ไม่แยก Tier B 5%)", q() == "1,700" and txt(pa
    -        check(f"{tag} zeroLot (ชนเพดาน Tier B) → 'ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿35,000) → ใช้ Tier A หรือข้ามตัวนี้' (7E-2a-fix §5)", "ราคาต่อ 1 หลัก (100) เกิ
    +        check(f"{tag} RG2b ราคา 1,000 · Stop 999 · f 50% → 100 หุ้น (1 หลัก) ไม่ zeroLot (เพดาน 175,000 ไม่ใช่ Tier B 35,000)", q() == "100" and not txt(page, "#cnRes [d
    -    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades))
    +    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades, pin_winner=True))
    +    pin_winner_pool(doc)   # RG2b — ตรึงถัง Winner = ทุน Core หลังตั้ง fx
    -        browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades), cards=cards)
    +        browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades, pin_winner=True), cards=cards)
    -    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades[1:]), cards=cs)
    +    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades[1:], pin_winner=True), cards=cs)
    -        check(f"{tag} หัวบัญชี: ชั้น 2 {expect*100:.2f}% / 20% · ขาดราคา 1", f"{f2(expect*100)}% / 20%" in (txt(page, '[data-core-head="main"] [data-c-l2]') or "") and "
    +        check(f"{tag} หัวบัญชี: ชั้น 2 ตอนนี้ {expect*100:.2f}% (RG2b ไม่มีเพดาน) · ขาดราคา 1", f"ตอนนี้ {f2(expect*100)}%" in (txt(page, '[data-core-head="main"] [data-
    -        check(f"{tag} บล็อกสรุป Port: ช่อง (a) 'จากราคาปิด' ไม่มี 'จากทุน' · ตัวเลขตรง · 'ขาดราคา 1 ตัว (ไม่นับ)'", "จากราคาปิด" in cell and "จากทุน" not in cell and f"{
    +        check(f"{tag} บล็อกสรุป Port: ช่อง (a) 'จากราคาปิด' ไม่มี 'จากทุน' · ตัวเลขตรง · 'ขาดราคา 1 ตัว (ไม่นับ)'", "จากราคาปิด" in cell and "จากทุน" not in cell and f"{
    -    b1, c1, p1, ce1, pe1, d1 = launch(pw, w, h, doc_with(main_trades=[t_open]))
    -    b2, c2, p2, ce2, pe2, d2 = launch(pw, w, h, doc_with(main_trades=[t_open, t_loss]))
    +    b1, c1, p1, ce1, pe1, d1 = launch(pw, w, h, doc_with(main_trades=[t_open], pin_winner=True))
    +    b2, c2, p2, ce2, pe2, d2 = launch(pw, w, h, doc_with(main_trades=[t_open, t_loss], pin_winner=True))
    -    doc = doc_with(main_trades=[tm], fam_market="TH")
    +    doc = doc_with(main_trades=[tm], fam_market="TH", pin_winner=True)
    -        check(f"{tag} 2 บัญชี: ชั้น 2 แยก (main 1.8% · fam ขาดราคา 1 → 0%)", "1.8% / 20%" in txt(page, '[data-core-head="main"] [data-c-l2]') and "0% / 20%" in txt(page,
    +        check(f"{tag} 2 บัญชี: ชั้น 2 แยก (main 1.8% · fam ขาดราคา 1 → 0%)", "ตอนนี้ 1.8%" in txt(page, '[data-core-head="main"] [data-c-l2]') and "ตอนนี้ 0%" in txt(pag
    -    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=[t1]), cards={
    +    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=[t1], pin_winner=True), cards={
    -              "TH" in txt(page, '[data-core-card="c1"] .ccChips') and "Tier B · เพดานไม้แรก 5%" in txt(page, '[data-core-card="c1"] [data-c-tier]') and page.is_disabled(
    +              "TH" in txt(page, '[data-core-card="c1"] .ccChips') and "Tier B · เพดานไม้แรก 25%" in txt(page, '[data-core-card="c1"] [data-c-tier]') and page.locator('[d
    -        check(f"{tag} B→A พร้อมเหตุผล → tier A + tierReason · เพดานไม้แรก 10% · ชิปเหตุผล (title)", c["tier"] == "A" and c["tierReason"] == "moat แข็ง" and "เพดานไม้แรก 
    +        check(f"{tag} B→A พร้อมเหตุผล → tier A + tierReason · เพดานไม้แรก 25% · ชิปเหตุผล (title)", c["tier"] == "A" and c["tierReason"] == "moat แข็ง" and "เพดานไม้แรก 
    -    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(), deny=True)
    +    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(pin_winner=True), deny=True)
    -    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=[t1]), cards=cs)
    +    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=[t1], pin_winner=True), cards=cs)

## tests/run_tests_phase25.py

    +    p24.pin_winner_pool(doc)   # RG2b — ตรึงถัง Winner = ทุน Core เดิม (ตัวเลขขนาดไม้ W คงเดิม)
    -        check(f"{tag} 2 แถวแผน META: 'แผน · Entry 600 · Stop 560 · ไม้แรก 8 หุ้น'", "แผน" in rp and "Entry 600" in rp and "Stop 560" in rp and "ไม้แรก 8 หุ้น" in rp, rp)
    +        check(f"{tag} 2 แถวแผน META: 'แผน · Entry 600 · Stop 560 · ไม้แรก 26 หุ้น' (RG2b เพดานเดียว)", "แผน" in rp and "Entry 600" in rp and "Stop 560" in rp and "ไม้แรก
    -        check(f"{tag} 2 ป้ายสั้น B·W + title ข้อความเต็ม (US · Tier B · เพดานไม้แรก 5% · ระบบ Week)", txt(page, card(page, "aapl") + " .ccTag") == "B·W" and page.get_att
    +        check(f"{tag} 2 ป้ายสั้น B·W + title ข้อความเต็ม (US · Tier B · เพดานไม้แรก 25% · ระบบ Week)", txt(page, card(page, "aapl") + " .ccTag") == "B·W" and page.get_at
    -        check(f"{tag} 3 plan ขยาย: UX2 แทนกล่อง 4 ช่อง → Entry · Stop บรรทัดเดียว · FF · ไม้แรก 8 หุ้น (ตัวใหญ่) + ตัวคุมใน วิธีคิด + [บันทึกซื้อไม้ 1] [ลบแผน]", page.lo
    +        check(f"{tag} 3 plan ขยาย: UX2 แทนกล่อง 4 ช่อง → Entry · Stop บรรทัดเดียว · FF · ไม้แรก 26 หุ้น (ตัวใหญ่) + ตัวคุมใน วิธีคิด + [บันทึกซื้อไม้ 1] [ลบแผน]", page.l
    +                and page.locator(card(page, "meta") + " [data-c-buy1]").count() == 1 and page.locator(card(page, "meta") + " [data-c-delplan]").count() == 1, pl)
    -        check(f"{tag} 8 เมนู: 'ดูไม้ที่ซื้อ (2)' · แก้ Entry/SL · ปิดตำแหน่ง · Tier… · ซื้อแล้ว — ล็อกกลยุทธ์ (disabled) (7E-2b-1)",
    -              all(x in g["txt"] for x in ("ดูไม้ที่ซื้อ (2)", "แก้ Entry/SL", "ปิดตำแหน่ง", "Tier…", "ซื้อแล้ว — ล็อกกลยุทธ์")) and page.locator(c + " .ccMenu [data-c-st
    +        check(f"{tag} 8 เมนู: 'ดูไม้ที่ซื้อ (2)' · แก้ Entry/SL · ปิดตำแหน่ง · Tier… · (RG2b: ไม่มีปุ่มสลับกลยุทธ์)",
    +              all(x in g["txt"] for x in ("ดูไม้ที่ซื้อ (2)", "แก้ Entry/SL", "ปิดตำแหน่ง", "Tier…")) and "ล็อกกลยุทธ์" not in g["txt"] and page.locator(c + " .ccMenu [d
    -        page.fill("#cnTicker", "XXX.BK"); page.click("#cnTierB"); page.fill("#cnEntry", "2000"); page.fill("#cnStop", "1999"); page.click('#cnF button[data-f="1"]'); pag
    +        page.fill("#cnTicker", "XXX.BK"); page.click("#cnTierB"); page.fill("#cnEntry", "20000"); page.fill("#cnStop", "19999"); page.click('#cnF button[data-f="1"]'); p
    -        check(f"{tag} 10 0 หุ้นเพราะชนเพดาน Tier (Tier B 2000/1999 TH) → 'ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿175,000) → ใช้ Tier A หรือข้ามตัวนี้'", z == "ราคาต่อ 1
    +        check(f"{tag} 10 0 หุ้นเพราะชนเพดาน Tier (RG2b: 20000/19999 TH) → 'ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿875,000) → ใช้ Tier A หรือข้ามตัวนี้'", z == "ราคาต่อ 
    -        check("14 tests/core_size_test.js (รันบนสำเนาใน index.html ผ่านเบราว์เซอร์) = 471/471 (CZ1: +22 เคส · LN3fix2: +29 เคส · เดิม 420 ผ่านครบ) · exit 0", bool(m) and
    +        check("14 tests/core_size_test.js (รันบนสำเนาใน index.html ผ่านเบราว์เซอร์) = 502/502 (CZ1: +22 เคส · LN3fix2: +29 เคส · เดิม 420 ผ่านครบ) · exit 0", bool(m) and

## tests/run_tests_phase27.py

    -        check(f"{tag} 7 กฎ F2c ของ Long = 0.6 อยู่แล้ว (สวน Macro+Trend) แต่ factor ที่ใช้ยัง 0.6 · off=false", f2c == {"rule": 0.6, "factor": 0.6, "off": False, "mr": T
    +        check(f"{tag} 7 RG2b: กฎ F2c ไม่มีตัวคูณ Macro (rule 1) แต่ MR ใช้ factor 0.6 ตายตัว · off=false", f2c == {"rule": 1, "factor": 0.6, "off": False, "mr": True}, j
    -        check(f"{tag} 9 PF1 — field F2c บันทึกตามปกติ (side = Long): macro_state=against · size_rule=0.6 · off_rule=false · trend_state=null (ไม่อ่าน Strategy)", (t or {
    +        check(f"{tag} 9 PF1 — field F2c บันทึกตามปกติ (side = Long): macro_state=against · size_rule=0.6 · off_rule=false · trend_state=null (ไม่อ่าน Strategy)", (t or {
    -        for i in (1, 2): push_trade(page, id=f"tq{i}", date=js(page, "()=>thaiToday()"), entry=2650, sl=2620, tp=2700, bias="Short", port="satB")
    +        for i in (1, 2, 3, 4): push_trade(page, id=f"tq{i}", date=js(page, "()=>thaiToday()"), entry=2650, sl=2620, tp=2700, bias="Short", port="satB")
    -        check(f"{tag} 9 โควตาไม้ใหม่เต็ม 2 → MR ก็ไม่ ready ('โควตาเต็ม')", (not a["ready"]) and "โควตาเต็ม" in a["warns"] and a["mrOk"], json.dumps(a["warns"], ensure_a
    +        check(f"{tag} 9 โควตาไม้ใหม่เต็ม 4 → MR ก็ไม่ ready ('โควตาเต็ม')", (not a["ready"]) and "โควตาเต็ม" in a["warns"] and a["mrOk"], json.dumps(a["warns"], ensure_a

## tests/run_tests_phase29.py

    -        go(page); ex(page, "l1")
    -        page.click(card_sel("l1") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]'); page.click("#clSave"); page.wait_for_timeout(700)
    +        go(page); page.evaluate("()=>{ setPlanScope('ladder'); render(); }"); page.wait_for_timeout(400); ex(page, "l1")   # RG2b: การ์ด L อยู่หน้า Ladder
    +        page.click('[data-ldr-card="l1"] [data-ldr-buy], ' + card_sel("l1") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]'); page.cli
    -        check(f"{tag} B3 การ์ด L ก็มีป้าย (A + WL B → เหลือง)", one("k9", "warn", "WL_B"), json.dumps(b("k9"), ensure_ascii=False))
    -        w_ids = ["k1", "k2", "k3", "k8", "k9"]; m_ids = ["k4", "k5", "k6", "k7", "k10"]
    +        check(f"{tag} B3 การ์ด L อยู่หน้า Ladder (RG2b) → ไม่มีป้าย Tier บนหน้า Winner", b("k9") == [], json.dumps(b("k9"), ensure_ascii=False))
    +        w_ids = ["k1", "k2", "k3", "k8"]; m_ids = ["k4", "k5", "k6", "k7", "k10", "k9"]   # RG2b: k9 (การ์ด L) ย้ายไปหน้า Ladder

## tests/run_tests_phase3.py

    -    check(f"[{BROWSER_ENGINE}/{label}] satV3PlanAcctCalc main/XM เท่ากับ sat7dCalc เดิมทุกจุด -> lot 0.19",
    -          calc_main.get("lot") is not None and abs(calc_main["lot"] - 0.19) < 1e-9, json.dumps(calc_main))
    +    check(f"[{BROWSER_ENGINE}/{label}] satV3PlanAcctCalc main/XM เท่ากับ sat7dCalc เดิมทุกจุด -> lot 0.15",
    +          calc_main.get("lot") is not None and abs(calc_main["lot"] - 0.15) < 1e-9, json.dumps(calc_main))
    +        B.trades.push({id:'quota3', date:wk+'-01'.slice(0,10), port:'satB', sym:'XAUUSD', bias:'Long', entry:2600, sl:2590, tp:null, qty:0.01, mult:100, cur:'USD', statu
    +        B.trades.push({id:'quota4', date:wk+'-01'.slice(0,10), port:'satB', sym:'XAUUSD', bias:'Long', entry:2600, sl:2590, tp:null, qty:0.01, mult:100, cur:'USD', statu
    -    check(f"[{BROWSER_ENGINE}/{label}] เตรียมเคส 'รวมด้วย (นอกแผน)': fam คำนวณ lot ได้จริง แต่โควตาไม้ใหม่สัปดาห์นี้เต็ม (2/2) -> ไม่ ready",
    +    check(f"[{BROWSER_ENGINE}/{label}] เตรียมเคส 'รวมด้วย (นอกแผน)': fam คำนวณ lot ได้จริง แต่โควตาไม้ใหม่สัปดาห์นี้เต็ม (4/4) -> ไม่ ready",

## tests/run_tests_phase31.py

    -              and not page.is_disabled("#cnStratL"), summ(page) + "|" + line(page, "growth"))
    +              and page.locator("#cnStratL").count() == 0, summ(page) + "|" + line(page, "growth"))   # RG2b: ไม่มีปุ่ม L ในฟอร์ม Winner
    -        check(f"{tag} 10 ชุด Growth (rev 25 · CAGR 18 · opm 12 vs 10 · OCF ✓ · ND 2.5) → 'คำนวณได้ A · Growth' · ปุ่ม L ปิด + 'L ใช้ได้เฉพาะ A-Fortress'",
    +        check(f"{tag} 10 ชุด Growth (rev 25 · CAGR 18 · opm 12 vs 10 · OCF ✓ · ND 2.5) → 'คำนวณได้ A · Growth' (RG2b: ไม่มีปุ่ม L ในฟอร์ม)",
    -              and page.is_disabled("#cnStratL") and "L ใช้ได้เฉพาะ A-Fortress" in (txt(page, "#cnStratMsg") or ""), summ(page) + "|" + (txt(page, "#cnStratMsg") or ""))
    +              and page.locator("#cnStratL").count() == 0, summ(page))   # RG2b: ไม่มีตัวเลือก W/L ในฟอร์ม
    -        check(f"{tag} 10 ผ่านทั้งคู่ → 'คำนวณได้ A · ทั้งสองมุม' + L เปิด", "คำนวณได้ A · ทั้งสองมุม" in summ(page) and not page.is_disabled("#cnStratL") and "on" in (pa
    +        check(f"{tag} 10 ผ่านทั้งคู่ → 'คำนวณได้ A · ทั้งสองมุม' + L เปิด", "คำนวณได้ A · ทั้งสองมุม" in summ(page) and page.locator("#cnStratL").count() == 0 and "on" i
    -        # เปิดปุ่ม L จริง: กด L แล้วสลับไปมุม Growth อย่างเดียว → กลับเป็น W เอง
    -        page.click("#cnStratL"); page.wait_for_timeout(60)
    -        clear_fortress(page); put(page, "#tiNd", 2.5); page.wait_for_timeout(100)
    -        check(f"{tag} 10 เลือก L แล้วมุม Fortress หลุด (เหลือ Growth) → กลับเป็น W เอง · L ปิด", page.is_disabled("#cnStratL") and "on" in (page.get_attribute("#cnStratW
    +        clear_fortress(page); put(page, "#tiNd", 2.5); page.wait_for_timeout(100)   # RG2b: ถอดตัวเลือก W/L ออกจากฟอร์ม — ตัดเคส "เลือก L แล้วมุม Fortress หลุด → กลับเป็
    -        check(f"{tag} 11 ไม้แรกเพดาน 10%: A-Growth = A-Fortress = 700 หุ้น · B (เพดาน 5%) = 350", qtys["TGRO"] == "700" and qtys["TFOR"] == "700" and qtys["TBEE"] == "35
    +        check(f"{tag} 11 ไม้แรกเพดานเดียว 25% ของถัง Winner (RG2b ไม่แยก Tier): A-Growth = A-Fortress = B = 365 หุ้น", qtys["TGRO"] == "365" and qtys["TFOR"] == "365" an
    -        check(f"{tag} 11 ชิปการ์ด A-Growth = 'Tier A · Growth' + บรรทัด FF 'เพดานไม้แรก 10%' (UX2: เพดานย้ายจากชิป)", chip_g == "Tier A · Growth" and "เพดานไม้แรก 10%" i
    +        check(f"{tag} 11 ชิปการ์ด A-Growth = 'Tier A · Growth' + บรรทัด FF 'เพดานไม้แรก 25%' (UX2: เพดานย้ายจากชิป)", chip_g == "Tier A · Growth" and "เพดานไม้แรก 25%" i
    -        check(f"{tag} 11 ชิป A-Fortress = 'Tier A · Fortress' + บรรทัด FF 'เพดานไม้แรก 10%' (UX2)", chip_f == "Tier A · Fortress" and "เพดานไม้แรก 10%" in (txt(page, f'{
    +        check(f"{tag} 11 ชิป A-Fortress = 'Tier A · Fortress' + บรรทัด FF 'เพดานไม้แรก 25%' (UX2)", chip_f == "Tier A · Fortress" and "เพดานไม้แรก 25%" in (txt(page, f'{
    -              and {id: ("เพดานไม้แรก " + ("5%" if id == "cw" else "10%")) in (txt(page, f'{card_sel(id)} [data-c-ff]') or "") for id in cards} == {id: True for id in car
    +              and {id: ("เพดานไม้แรก 25%") in (txt(page, f'{card_sel(id)} [data-c-ff]') or "") for id in cards} == {id: True for id in cards}, json.dumps(chips, ensure_a
    -            it = page.locator(card_sel(id) + ' .ccMenu [data-c-strat="L"]')
    -            res[id] = (it.is_disabled(), it.inner_text())
    +            res[id] = page.locator(card_sel(id) + ' .ccMenu [data-c-strat]').count()
    -        check(f"{tag} 12 ⋯ A-Growth: 'เปลี่ยนเป็น L' ปิด + 'L ใช้ได้เฉพาะ A-Fortress'", res["cg"][0] is True and "L ใช้ได้เฉพาะ A-Fortress" in res["cg"][1], json.dumps(r
    -        check(f"{tag} 12 ⋯ A-Fortress เปิด · A-ทั้งคู่ เปิด", res["cf"][0] is False and "ถัวตามแนวรับ (L)" in res["cf"][1] and res["cb"][0] is False, json.dumps(res, ens
    +        check(f"{tag} 12 ⋯ (RG2b) เมนูการ์ด Winner ไม่มี 'เปลี่ยนเป็น L' ทั้ง A-Growth · A-Fortress · A-ทั้งคู่ (ถอดโหมดแปลง W→L)", res == {"cg": 0, "cf": 0, "cb": 0}, j
    -        p24.menu_click(page, "old", '[data-c-strat="L"]'); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
    -        page.fill("#cnLv0", "100"); page.fill("#cnLv1", "90"); page.fill("#cnLsl", "70"); page.wait_for_timeout(150)
    -        g = p26.gate_row(page, "tier")
    -        check(f"{tag} 13 การ์ดเก่าวางบันได L ได้ · ประตู Tier = 'A-Fortress' ✓", g and g["ok"] == "1" and g["t"].endswith("A-Fortress"), json.dumps(g, ensure_ascii=False
    -        check(f"{tag} 13 ปุ่มล็อกแผนใช้ได้", not page.is_disabled("#cnSave"), txt(page, "#cnErr") or "")
    -        page.click("#cnSave"); page.wait_for_timeout(500)
    -        c = db_card(page, "old")
    -        check(f"{tag} 13 บันทึก → strategy L · มี ladder · tierLens 'fortress' (บันทึกผ่านบล็อก Tier ใหม่)", c["strategy"] == "L" and c["ladder"] and c["tierLens"] == "f
    +        # RG2b — ถอดโหมดแปลง W→L (การ์ดเก่าไม่มีเมนู 'เปลี่ยนเป็น L' · วาง Ladder ที่หน้า Ladder)
    +        page.click(card_sel("old") + " [data-c-more]")
    +        check(f"{tag} 13 การ์ดเก่าไม่มีเมนูเปลี่ยนเป็น L (RG2b)", page.locator(card_sel("old") + ' .ccMenu [data-c-tierbtn]').count() == 1 and page.locator(card_sel("old
    +        page.keyboard.press("Escape")
    -        for id in ("lp", "lo"):
    -            p24.menu_click(page, id, "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
    -            page.click("#cnTierG"); page.wait_for_timeout(60); page.fill("#cnReason", "เปลี่ยนมุมเป็น Growth"); page.wait_for_timeout(60)
    -            page.click("#ctSave"); page.wait_for_timeout(500)
    -        check(f"{tag} 14 บันทึกมุมเป็น Growth → tier A · tierLens growth ทั้งสองการ์ด", db_card(page, "lo")["tierLens"] == "growth" and db_card(page, "lp")["tierLens"] =
    -        ex(page, "lo"); chip = txt(page, card_sel("lo") + " [data-c-tier]") or ""
    -        check(f"{tag} 14 ชิปการ์ด L: 'Tier A · Growth · บันไดเดิมทำงานต่อจนออก'", chip == "Tier A · Growth · บันไดเดิมทำงานต่อจนออก", chip)
    -        check(f"{tag} 14 บันไดเดิมยังซื้อระดับต่อได้ ('บันทึกซื้อ L2' ใช้ได้) · เลื่อน Stop ได้", txt(page, card_sel("lo") + " [data-c-lbuy]") == "บันทึกซื้อ L2" and not
    -        page.click(card_sel("lo") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]'); page.click("#clSave"); page.wait_for_timeout(500)
    -        check(f"{tag} 14 ซื้อ L2 สำเร็จ (ระดับ bought)", db_card(page, "lo")["ladder"]["levels"][1]["status"] == "bought")
    -        ex(page, "lp")
    -        check(f"{tag} 14 'แก้แผนบันได' ของแผน L ที่เป็น A-Growth ปิด + ข้อความ 'แก้แผนบันไดต้องเป็น A-Fortress'",
    -              page.is_disabled(card_sel("lp") + " [data-c-ledit]") and "แก้แผนบันไดต้องเป็น A-Fortress" in (txt(page, card_sel("lp") + " [data-c-ledit-note]") or ""))
    +        # RG2b — การ์ด L อยู่หน้า Ladder (ไม่มีเมนู Tier…/แก้แผนบันไดในหน้า Winner) : ตัดเคสเปลี่ยนมุม Tier ของการ์ด L ออก
    +        onwin = page.locator(card_sel("lp")).count() + page.locator(card_sel("lo")).count()
    +        page.evaluate("()=>{ setPlanScope('ladder'); render(); }"); page.wait_for_timeout(400)
    +        check(f"{tag} 14 (RG2b) การ์ด L ไม่อยู่หน้า Winner · อยู่หน้า Ladder ทั้ง 2 ใบ (ไม่มี Tier…)", onwin == 0 and page.locator('[data-ldr-card="lp"]').count() == 1 a

## tests/run_tests_phase34.py

    -              all(c == {"rpt": 1.5, "rptHi": 2, "heatMax": 6, "newMax": 2, "macroNeutral": 1, "macroAgainst": 0.6, "pyrSplit": [100, 0, 0], "ddReduce": 12.5, "ddPause": 
    +              all(c == {"rpt": 1.5, "rptHi": 2, "heatMax": 6, "newMax": 4, "macroNeutral": 1, "macroAgainst": 1, "pyrSplit": [100, 0, 0], "ddReduce": 12.5, "ddPause": 20
    -        check(f"{tag} 1 แถบบัญชี Sat: RPT 1.5% · heat ลงท้าย /6% · ไม้ใหม่ /2", f"RPT Main {js(page, '()=>satV2Cfg(\'main\').rptMain')}% · Tactical {js(page, '()=>satV2C
    +        check(f"{tag} 1 แถบบัญชี Sat: RPT 1.5% · heat ลงท้าย /6% · ไม้ใหม่ /4", f"RPT Main {js(page, '()=>satV2Cfg(\'main\').rptMain')}% · Tactical {js(page, '()=>satV2C
    -        check(f"{tag} 1 STRIP_FIELDS.sat สร้างจากค่าตั้ง (heat /6% · ใหม่ /2)", js(page, "()=>[STRIP_FIELDS.sat[0].suffix, STRIP_FIELDS.sat[1].suffix]") == ["/6%", "/2"]
    +        check(f"{tag} 1 STRIP_FIELDS.sat สร้างจากค่าตั้ง (heat /6% · ใหม่ /4)", js(page, "()=>[STRIP_FIELDS.sat[0].suffix, STRIP_FIELDS.sat[1].suffix]") == ["/6%", "/4"]
    -        check(f"{tag} 1 seed satRisk {{rpt:1.25, rptHi:1.5}} → lot เท่าค่าเดิมก่อนแก้ (0.13) · = Calc.satLot ตรง", c["rpt"] == 1.25 and c["lot"] == 0.13 == lot_for(page,
    +        check(f"{tag} 1 seed satRisk {{rpt:1.25, rptHi:1.5}} → lot เท่าค่าเดิมก่อนแก้ (0.10 · RG2b ถัง Sat เล็กลง) · = Calc.satLot ตรง", c["rpt"] == 1.25 and c["lot"] ==
    -        check(f"{tag} 5 newMax 3 · มีไม้ใหม่ 2 → ไม้ที่ 3 ยัง ready", c["newMax"] == 3 and c["ready"] is True, json.dumps(c["warns"], ensure_ascii=False))
    +        check(f"{tag} 5 โควตา 4 คงที่ (RG2b ตั้งไม่ได้) · มีไม้ใหม่ 2 → ไม้ที่ 3 ยัง ready", c["newMax"] == 4 and c["ready"] is True, json.dumps(c["warns"], ensure_ascii
    -        check(f"{tag} 5 มีไม้ใหม่ 3 → ไม้ที่ 4 = โควตาเต็ม · แถบ 3/3", c["ready"] is False and "โควตาเต็ม" in c["warns"] and "3/3" in (strip(page) or ""), f"{c['warns']}
    +        check(f"{tag} 5 มีไม้ใหม่ 3 → ไม้ที่ 4 ยัง ready (โควตา 4) · แถบ 3/4", c["ready"] is True and "โควตาเต็ม" not in c["warns"] and "3/4" in (strip(page) or ""), f"{
    -        check(f"{tag} 6 ส่วน 'ความเสี่ยง SAT — % ของถัง Sat' มี 3 ช่อง · ค่าเริ่มต้น 1.5 / 2 / 2", vals == ["1.5", "2", "2"] and "per-trade risk" in (txt(page, "#satRisk
    +        check(f"{tag} 6 ส่วน 'ความเสี่ยง SAT — % ของถัง Sat' มี 3 ช่อง · ค่าเริ่มต้น 1.5 / 2 / 4 (ช่องไม้ใหม่ซ่อน คงที่ 4)", vals == ["1.5", "2", "4"] and "per-trade ris
    -        check(f"{tag} 6 บรรทัดเล็ก heat: 'ตั้งที่ช่อง Sat — % ของถัง Sat (ตอนนี้ 6%)' · ไม่มีช่อง heat ซ้ำ", "ตอนนี้ 6%" in (txt(page, "#satHeatHint") or "") and js(page
    +        check(f"{tag} 6 บรรทัดเล็ก heat: 'ตั้งที่ช่อง Sat — % ของถัง Sat (ตอนนี้ 6%)' · ไม่มีช่อง heat ซ้ำ", "ตอนนี้ 6%" in (txt(page, "#satHeatHint") or "") and js(page
    -        for fld, vals_ in {"sSatNewMax": ["0", "2.5", "11"], "sSatRpt": ["0", "6"]}.items():
    +        for fld, vals_ in {"sSatRpt": ["0", "6"]}.items():   # RG2b — ช่องไม้ใหม่/สัปดาห์ถอดแล้ว (คงที่ 4)
    -            page.fill("#" + fld, "2" if fld == "sSatNewMax" else "1.5")
    -        check(f"{tag} 6 newMax 0 / 2.5 / 11 · rpt 0 / 6 → แดงทุกค่า + ปุ่มบันทึกปิด", all(bad.values()), json.dumps(bad))
    +            page.fill("#" + fld, "1.5")
    +        check(f"{tag} 6 rpt 0 / 6 → แดงทุกค่า + ปุ่มบันทึกปิด", all(bad.values()), json.dumps(bad))
    -        check(f"{tag} 6 แก้กลับเป็นค่าถูก → ข้อความแดงหาย · ปุ่มบันทึกเปิด", all(err(page, i) == "" for i in ("sSatRpt", "sSatRptHi", "sSatNewMax")) and save_disabled(pa
    +        check(f"{tag} 6 แก้กลับเป็นค่าถูก → ข้อความแดงหาย · ปุ่มบันทึกเปิด", all(err(page, i) == "" for i in ("sSatRpt", "sSatRptHi")) and save_disabled(page) is False)
    -        page.fill("#sSatRpt", "1"); page.fill("#sSatRptHi", "1.8"); page.fill("#sSatNewMax", "3"); page.wait_for_timeout(60)
    +        page.fill("#sSatRpt", "1"); page.fill("#sSatRptHi", "1.8"); page.wait_for_timeout(60)
    -        check(f"{tag} 7 บันทึก → settings.satRisk ของบัญชีที่เปิด = {{rpt:1, rptHi:1.8, newMax:3}} · fam ไม่เปลี่ยน", saved[0] == {"rpt": 1, "rptHi": 1.8, "newMax": 3, "
    +        check(f"{tag} 7 บันทึก → settings.satRisk ของบัญชีที่เปิด = {{rpt:1, rptHi:1.8}} (RG2b: ไม่เขียน newMax/macro ใหม่) · fam ไม่เปลี่ยน", saved[0] == {"rpt": 1, "rp
    -        check(f"{tag} 7 สลับไป fam → ช่องแสดงค่าเริ่มต้น 1.5 / 2 / 2", v_fam == ["1.5", "2", "2"], json.dumps(v_fam))
    +        check(f"{tag} 7 สลับไป fam → ช่องแสดงค่าเริ่มต้น 1.5 / 2 / 4", v_fam == ["1.5", "2", "4"], json.dumps(v_fam))
    -        check(f"{tag} 7 สลับกลับ main → ค่าของ main ไม่เปลี่ยน · fam เก็บ rpt 1.2 แยกกัน", both[0]["rpt"] == 1 and both[0]["newMax"] == 3 and both[1]["rpt"] == 1.2, json
    +        check(f"{tag} 7 สลับกลับ main → ค่าของ main ไม่เปลี่ยน · fam เก็บ rpt 1.2 แยกกัน", both[0]["rpt"] == 1 and both[0].get("newMax") is None and both[1]["rpt"] == 1.
    -        check(f"{tag} 7 เปิดค่าตั้ง main → เห็น 1 / 1.8 / 3", v_main == ["1", "1.8", "3"], json.dumps(v_main))
    +        check(f"{tag} 7 เปิดค่าตั้ง main → เห็น 1 / 1.8 / 4", v_main == ["1", "1.8", "4"], json.dumps(v_main))

## tests/run_tests_phase37.py

    -    doc = p24.doc_with(main_trades=[], core_cap=700000, main_market="both")
    +    doc = p24.doc_with(main_trades=[], core_cap=700000, main_market="both", pin_winner=False)
    -        if with_dd: s["ddState"] = {"core": ds0(700000), "sat": ds0(26000)}
    +        if with_dd: s["ddState"] = {"winner": ds0(700000), "sat": ds0(26000)}   # RG2b §4.7 — เบรก DD ต่อถัง (Winner = ถัง Core เดิมที่ตรึงไว้)
    +    p24.pin_winner_pool(doc)   # RG2b — ถัง Winner = ทุน Core เดิม (หลังตั้ง capital ของ fixture นี้)
    +    bucket = "winner" if bucket == "core" else bucket   # RG2b §4.7 — เบรก DD ต่อถัง: เทสเดิมเรียก "core" = Winner
    +    bucket = "winner" if bucket == "core" else bucket   # RG2b §4.7 — เบรก DD ต่อถัง: เทสเดิมเรียก "core" = Winner
    +    bucket = "winner" if bucket == "core" else bucket   # RG2b §4.7 — เบรก DD ต่อถัง: เทสเดิมเรียก "core" = Winner
    +    bucket = "winner" if bucket == "core" else bucket   # RG2b §4.7 — เบรก DD ต่อถัง: เทสเดิมเรียก "core" = Winner
    -    sel = (f'[data-core-acct="{acct}"] ' if (acct and bucket == "core") else (f'[data-sat-meta] [data-acct="{acct}"] ' if acct else "")) + f'[data-dd-chip="{bucket}"]'
    +    core_ = bucket == "core"; bucket = "winner" if core_ else bucket   # RG2b §4.7
    +    sel = (f'[data-core-acct="{acct}"] ' if (acct and core_) else (f'[data-sat-meta] [data-acct="{acct}"] ' if acct else "")) + f'[data-dd-chip="{bucket}"]'
    +    bucket = "winner" if bucket == "core" else bucket   # RG2b §4.7 — เบรก DD ต่อถัง: เทสเดิมเรียก "core" = Winner
    -        bar = txt(page, '[data-dd-bar="core"]') or ""
    +        bar = txt(page, '[data-dd-bar="winner"]') or ""
    +        # RG2b §4.7 — เบรกแยกต่อถัง: Winner ลดขนาดไม่บล็อกบันได → ตั้งเบรกของ Ladder เอง (DD 12.5% ของถัง Ladder) แล้วเช็กการบล็อกบันได
    +        wl0 = js(page, "()=>coreCanPlace('main',{tier:'A',fortress:true,thb:{ok:false}},null,false).ddBlock")
    +        check(f"{tag} 1 (RG2b) Winner ลดขนาด → ไม่บล็อกการวางบันได (เบรกคนละถัง)", not wl0, str(wl0))
    +        js(page, "()=>{ const B=getBook('main'), lp=poolsOf('main').ladder, k=Object.values(B.settings.ddState).find(x=>x&&x.key)?.key||null; B.settings.ddState=Object.a
    -        p33.new_form(page, "LTEST"); p33.fill_fortress(page); page.click("#cnStratL"); page.wait_for_timeout(200)
    +        p33.new_form(page, "LTEST"); p33.fill_fortress(page); js(page, "()=>{ coreNew.strat='L'; coreNewIn(); }"); page.wait_for_timeout(200)   # RG2b — ไม่มีปุ่มเลือก L
    -        page.click("#cnStratW"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.wait_for_timeout(200)
    +        js(page, "()=>{ coreNew.strat='W'; coreNewIn(); }"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.wait_for_timeout(200)
    +        js(page, "()=>{ const B=getBook('main'); const ds=Object.assign({}, B.settings.ddState); delete ds.ladder; B.settings.ddState=ds; saveBook('main'); render(); }")
    -        check(f"{tag} 2 ชิป 'พักถึง 15 ต.ค.' (สีแดง)", "พักถึง 15 ต.ค." in c and page.locator('[data-dd-chip="core"].dd-pause').count() >= 1, c)
    -        check(f"{tag} 2 แถบแจ้ง: พักถึง 15 ต.ค. · ห้ามเปิดไม้ใหม่ · ต้องเขียนทบทวน", all(x in (txt(page, '[data-dd-bar="core"]') or "") for x in ("พักถึง 15 ต.ค.", "ห้าม
    +        check(f"{tag} 2 ชิป 'พักถึง 15 ต.ค.' (สีแดง)", "พักถึง 15 ต.ค." in c and page.locator('[data-dd-chip="winner"].dd-pause').count() >= 1, c)
    +        check(f"{tag} 2 แถบแจ้ง: พักถึง 15 ต.ค. · ห้ามเปิดไม้ใหม่ · ต้องเขียนทบทวน", all(x in (txt(page, '[data-dd-bar="winner"]') or "") for x in ("พักถึง 15 ต.ค.", "ห้
    -        check(f"{tag} 3 recover: งดบันได L ใหม่ ('ฟื้นตัว')", "ฟื้นตัว" in lad, lad)
    +        check(f"{tag} 3 recover (Winner): ไม่บล็อกบันไดใหม่ — เบรกแยกต่อถัง (RG2b §4.7)", not lad, lad)
    -        check(f"{tag} 4 ชิป 'ปกติ' หลังออกจาก recover", "ปกติ" in chip(page, "core", "main") and page.locator('[data-dd-bar="core"]').count() == 0, chip(page, "core", "m
    +        check(f"{tag} 4 ชิป 'ปกติ' หลังออกจาก recover", "ปกติ" in chip(page, "core", "main") and page.locator('[data-dd-bar="winner"]').count() == 0, chip(page, "core", 
    -        page.fill("#sCore", "800000"); page.wait_for_timeout(100); js(page, "()=>saveSettings()"); page.wait_for_timeout(500)
    +        page.fill("#sCore", "800000"); wp_ = 800000 / (800000 + 26000 * 40) * 100
    +        page.fill("#sPoolW", repr(wp_)); page.fill("#sPoolL", repr((100 - wp_) / 2)); page.fill("#sPoolS", repr((100 - wp_) / 2))   # RG2b — ตรึงถัง Winner = ทุน Core ให
    +        page.wait_for_timeout(100); js(page, "()=>saveSettings()"); page.wait_for_timeout(500)
    -        check(f"{tag} 9 แจ้งบรรทัดเล็ก 'เริ่มนับ DD ใหม่ (แก้ทุนถัง)'", "เริ่มนับ DD ใหม่ (แก้ทุนถัง)" in (txt(page, '[data-dd-rebase="core"]') or ""), txt(page, '[data-
    -        js(page, "()=>{ const B=getBook('main'); B.settings.capital.core=700000; saveBook('main'); render(); }")
    +        check(f"{tag} 9 แจ้งบรรทัดเล็ก 'เริ่มนับ DD ใหม่ (แก้ทุนถัง)'", "เริ่มนับ DD ใหม่ (แก้ทุนถัง)" in (txt(page, '[data-dd-rebase="winner"]') or ""), txt(page, '[dat
    +        js(page, "()=>{ const B=getBook('main'); B.settings.capital.core=700000; const wp=700000/(700000+26000*40)*100; B.settings.pools={winner:wp, ladder:(100-wp)/2, s
    -        wk = js(page, "()=>ddWeakest(ddEval('main','core')).map(x=>[x.ticker, Math.round(x.r*100)/100])")
    -        check(f"{tag} 11 W6 (ไม่มี sl0) ใช้ Stop แรกใน stopHistory → R −1.5", ["W6.BK", -1.5] in wk or any(x[0] == "W6.BK" for x in js(page, "()=>ddWeakest(ddEval('main'
    +        wk = js(page, "()=>ddWeakest(ddEval('main','winner')).map(x=>[x.ticker, Math.round(x.r*100)/100])")
    +        check(f"{tag} 11 W6 (ไม่มี sl0) ใช้ Stop แรกใน stopHistory → R −1.5", ["W6.BK", -1.5] in wk or any(x[0] == "W6.BK" for x in js(page, "()=>ddWeakest(ddEval('main'
    -        bad = overflow(page, ['[data-core-head="main"]', '[data-dd-bar="core"]'])
    +        bad = overflow(page, ['[data-core-head="main"]', '[data-dd-bar="winner"]'])
    -        check(f"{tag} 7 lot ใหม่ = Calc.satLot ที่ riskAmount × 0.5 ตรง ๆ (ปัดลงตาม lotStep) · ต่างจาก lot ปกติ", r["lot"] == r["half"] and r["half"] < r["full"] and r["
    +        check(f"{tag} 7 lot ใหม่ = Calc.satLot ที่ riskAmount × 0.5 ตรง ๆ (ปัดลงตาม lotStep) · ต่างจาก lot ปกติ", r["lot"] == r["half"] and r["half"] < r["full"] and r["

## tests/run_tests_phase38.py

    -        check(f"{tag} 2b แถบสถานะเร็ว: (TD2) ไม่มีแถบชิป · ตารางตัวเลข 2 บัญชี × 5 ค่า (DD Core · DD Sat · heat · ไม้ใหม่ · ชั้น 2)", no_pulse and len(tbl) == 2 and all(
    -        check(f"{tag} 2b ช่อง DD Sat บัญชีหลัก = ตัวเลข DD ของ pause และสีแดง (TD2: ตาราง แทนชิป 'พักถึง 27 ก.ย.')", main_r and "r" in main_r["k"][2].split() and main_r[
    +        check(f"{tag} 2b แถบสถานะเร็ว: (TD2) ไม่มีแถบชิป · ตารางตัวเลข 2 บัญชี × 5 ค่า (DD Core · DD Sat · heat · ไม้ใหม่ · ชั้น 2)", no_pulse and len(tbl) == 2 and all(
    +        check(f"{tag} 2b ช่อง DD Sat บัญชีหลัก = ตัวเลข DD ของ pause และสีแดง (TD2: ตาราง แทนชิป 'พักถึง 27 ก.ย.')", main_r and "r" in main_r["k"][3].split() and main_r[
    -        check(f"{tag} 2b ค่าในตาราง DD ตรงกับ ddEval (ไม่คิดใหม่)", main_r and main_r["c"][2] == f"{ev:g}%", f"{ev} / {main_r}")
    +        check(f"{tag} 2b ค่าในตาราง DD ตรงกับ ddEval (ไม่คิดใหม่)", main_r and main_r["c"][3] == f"{ev:g}%", f"{ev} / {main_r}")
    -        check(f"{tag} 2b ช่อง heat Sat = sat7dAcctBase", main_r and main_r["c"][3] == hv, f"{hv} / {main_r}")
    -        g = js(page, "()=>coreGate('main').text"); gf = js(page, "()=>document.querySelector('[data-td-detfoot]').textContent")
    -        check(f"{tag} 2b บรรทัดใต้ตาราง 'ประตู FF' (UX2: f→FF) = coreGate().text", f"ประตู FF: {g}" in gf and "fundflow อัปเดต 2 ต.ค." in gf, f"{g} / {gf}")
    +        check(f"{tag} 2b ช่อง heat Sat = sat7dAcctBase", main_r and main_r["c"][4] == hv, f"{hv} / {main_r}")
    +        gf = js(page, "()=>document.querySelector('[data-td-detfoot]').textContent")
    +        check(f"{tag} 2b บรรทัดใต้ตาราง = 'fundflow อัปเดต 2 ต.ค.' (RG2b ถอดประตู FF)", "ประตู FF" not in gf and "fundflow อัปเดต 2 ต.ค." in gf, gf)

## tests/run_tests_phase39.py

    +import run_tests_phase24 as P24_
    +PIN_BOTH = (__name__ == "__main__")
    +
    +
    +    if PIN_BOTH: P24_.pin_both_pools(doc)   # RG2b — ตรึงถัง Winner/Sat เท่าทุนเดิม (รันเป็นสคริปต์ของชุดนี้เท่านั้น)
    -def ds_set(doc, acct, bucket, tank, **kw): doc["books"][acct]["settings"]["ddState"][bucket] = P.ds0(tank, **kw)
    +def ds_set(doc, acct, bucket, tank, **kw): doc["books"][acct]["settings"]["ddState"]["winner" if bucket == "core" else bucket] = P.ds0(tank, **kw)   # RG2b §4.7 — เบรก D
    -        exp = js(page, """()=>acctList.map(a=>{ const bs = sat7dAcctBase(a.id), cr = coreAcctRisk(a.id), d1 = ddEval(a.id,'core'), d2 = ddEval(a.id,'sat'), f = x=>String
    -            return {a: a.id, c: [td3AcctName(a), f(d1.ddPct)+'%', f(d2.ddPct)+'%', f(bs.heatPct)+' / '+bs.heatMax+'%', bs.nNew+' / '+bs.newMax, f(cr.layer2Pct)+' / '+cr.
    -        check(f"{tag} 2 กด 'ดูตัวเลข' → ตาราง 2 แถว (Main · Family) × 5 คอลัมน์", len(tbl["rows"]) == 2 and [r["c"][0] for r in tbl["rows"]] == ["Main", "Family"] and le
    +        exp = js(page, """()=>acctList.map(a=>{ const bs = sat7dAcctBase(a.id), cr = coreAcctRisk(a.id), d1 = ddEval(a.id,'winner'), d3 = ddEval(a.id,'ladder'), d2 = ddE
    +            return {a: a.id, c: [td3AcctName(a), f(d1.ddPct)+'%', f(d3.ddPct)+'%', f(d2.ddPct)+'%', f(bs.heatPct)+' / '+bs.heatMax+'%', bs.nNew+' / '+bs.newMax, f(cr.lay
    +        check(f"{tag} 2 กด 'ดูตัวเลข' → ตาราง 2 แถว (Main · Family) × 6 คอลัมน์ (RG2b: DD Winner · DD Ladder แยก)", len(tbl["rows"]) == 2 and [r["c"][0] for r in tbl["ro
    -        gate = js(page, "()=>coreGate('main').text")
    -        check(f"{tag} 2 ใต้ตาราง 'ประตู FF: {{สถานะเดิม}} · fundflow อัปเดต 2 ต.ค.' (UX2: f→FF)", tbl["foot"] == f"ประตู FF: {gate} · fundflow อัปเดต 2 ต.ค.", tbl["foot"
    +        check(f"{tag} 2 ใต้ตาราง 'fundflow อัปเดต 2 ต.ค.' (RG2b ถอดประตู FF)", tbl["foot"] == "fundflow อัปเดต 2 ต.ค.", tbl["foot"])
    -            check(f"{tag} 2 มือถือ: ตารางตัวเลขไม่ล้นแนวนอน (หัวคอลัมน์ย่อ)", not ov and "DD C" in tbl["head"], json.dumps([ov, tbl["head"]], ensure_ascii=False))
    +            check(f"{tag} 2 มือถือ: ตารางตัวเลขไม่ล้นแนวนอน (หัวคอลัมน์ย่อ)", not ov and "DD W" in tbl["head"], json.dumps([ov, tbl["head"]], ensure_ascii=False))
    -    # ไม้ใหม่ Family 2/2 (เสี่ยงน้อย)
    +    # ไม้ใหม่ Family 4/4 (เสี่ยงน้อย)
    -                   T("tfb", "satB", "open", sym="BRENT", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30")]
    +                   T("tfb", "satB", "open", sym="BRENT", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30"),
    +                   T("tfc", "satB", "open", sym="BTCUSD", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30"),
    +                   T("tfd", "satB", "open", sym="XAGUSD", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30")]   # RG2b: โควตาไม้ใหม่ 
    -        ev = js(page, "()=>{ const e = ddEval('main','core'); return [e.stage, Math.round(e.ddPct*100)/100]; }")
    +        ev = js(page, "()=>{ const e = ddEval('main','winner'); return [e.stage, Math.round(e.ddPct*100)/100]; }")
    -        cls = js(page, "()=>{ const r = document.querySelector('[data-num-acct=\"main\"]'); return [r.children[3].className, r.children[3].innerText.trim()]; }")
    +        cls = js(page, "()=>{ const r = document.querySelector('[data-num-acct=\"main\"]'); return [r.children[4].className, r.children[4].innerText.trim()]; }")
    -        check(f"{tag} 4 ไม้ใหม่ Family 2/2 → แถว 🟡 'ไม้ใหม่ Sat Family ครบ 2/2 สัปดาห์นี้'", "ไม้ใหม่ Sat Family ครบ 2/2 สัปดาห์นี้" in j("newcnt"), j("newcnt"))
    -        check(f"{tag} 4 DD Core main reduce → แถว 🟡 'เบรก DD Core Main: ลดขนาด ×0.5 · DD x%'", bool(re.search(r"เบรก DD Core Main: ลดขนาด ×0\.5 · DD 1[23]\.", j("dd-redu
    -        check(f"{tag} 4 ชั้น 2 ถึงระดับเตือน → แถว 🟡 'ชั้น 2 Core Main a / 20%'", bool(re.search(r"ชั้น 2 Core Main 0\.\d+ / 20%", j("l2"))), j("l2") + str(ka))
    -        check(f"{tag} 4 ประตู FF เปิด → แถว 🔵 'ประตู FF เปิด · วางบันได L ได้ (บัญชีหลัก)' (UX2: f→FF)", "ประตู FF เปิด · วางบันได L ได้ (บัญชีหลัก)" in j("gate", tb, kb
    +        check(f"{tag} 4 ไม้ใหม่ Family 4/4 → แถว 🟡 'ไม้ใหม่ Sat Family ครบ 4/4 สัปดาห์นี้'", "ไม้ใหม่ Sat Family ครบ 4/4 สัปดาห์นี้" in j("newcnt"), j("newcnt"))
    +        check(f"{tag} 4 DD Winner main reduce → แถว 🟡 'เบรก DD Winner Main: ลดขนาด ×0.5 · DD x%' (RG2b §4.7 แยกต่อถัง)", bool(re.search(r"เบรก DD Winner Main: ลดขนาด ×0\
    +        check(f"{tag} 4 ไม่มีแถวเตือนชั้น 2 (RG2b ถอดเพดานชั้น 2)", j("l2") == "", j("l2") + str(ka))
    +        check(f"{tag} 4 ไม่มีแถวประตู FF เปิด (RG2b ถอดประตู)", j("gate", tb, kb) == "", json.dumps(tb, ensure_ascii=False))   # RG2b — ไม่มีแถวประตู FF
    -        check(f"{tag} 4 บรรทัดปกติตัดคำของหมวดผิดปกติ (DD · heat · ไม้ใหม่ · ชั้น 2 · f) → เหลือ fundflow", ol == "✓ อื่น ๆ ปกติ — fundflow" or (w <= 480 and ol == "✓ อื
    +        check(f"{tag} 4 บรรทัดปกติตัดคำของหมวดผิดปกติ (DD · heat · ไม้ใหม่ · ชั้น 2 · f) → เหลือ fundflow", ol in ("✓ อื่น ๆ ปกติ — ไม้ใหม่ · ชั้น 2 · f · fundflow", "✓ 
    -        check(f"{tag} 4 กดแถวลดขนาด → sheet DD Core บัญชีหลัก", js(page, "()=>{ const h = document.querySelector('.core-sheet h3'); return !!h && /Core/.test(h.textConte
    +        check(f"{tag} 4 กดแถวลดขนาด → sheet DD Winner บัญชีหลัก", js(page, "()=>{ const h = document.querySelector('.core-sheet h3'); return !!h && /Winner/.test(h.textC
    -        go_today(page); row(page, "l2").click(); page.wait_for_timeout(500)
    -        check(f"{tag} 4 กดแถวชั้น 2 → แท็บแผน (หุ้น) บัญชีหลัก", js(page, "()=>activeTab+'/'+planScope+'/'+planAcctFilter") == "plan/stock/main", js(page, "()=>activeTab
    -        go_today(page); row(page, "gate").click(); page.wait_for_timeout(500)
    -        check(f"{tag} 4 กดแถวประตู f → แท็บแผน (หุ้น)", js(page, "()=>activeTab+'/'+planScope") == "plan/stock")
    +        go_today(page)   # RG2b — แถวชั้น 2 / ประตู FF ถอดแล้ว: ไม่มีให้กด
    +        check(f"{tag} 4 ไม่มีแถวชั้น 2 และแถวประตู f ให้กด", js(page, "()=>document.querySelectorAll('[data-kind=l2],[data-kind=gate]').length") == 0)

## tests/run_tests_phase5.py

    -    check(f"{tag} §7 lot เดิมยังได้ค่าเท่าเดิม: XAUUSD main/XM = 0.19 lot", lot is not None and abs(lot - 0.19) < 1e-9, str(lot))
    +    check(f"{tag} §7 lot เดิมยังได้ค่าเท่าเดิม: XAUUSD main/XM = 0.15 lot", lot is not None and abs(lot - 0.15) < 1e-9, str(lot))

## tests/run_tests_phase53.py

    -MORE = ["data-c-cashfree", "data-c-l2", "data-c-lshare", "data-c-gate", "data-c-missing"]
    +MORE = ["data-c-cashfree", "data-c-l2", "data-c-lshare", "data-c-missing"]
    -        check(f"{tag} 1 ทั้ง 5 ชิปอยู่ใน details[data-c-more] (มีใน DOM)", all(inside_more(page, a) is True for a in MORE), json.dumps({a: inside_more(page, a) for a in 
    +        check(f"{tag} 1 ทั้ง 4 ชิปอยู่ใน details[data-c-more] (มีใน DOM)", all(inside_more(page, a) is True for a in MORE), json.dumps({a: inside_more(page, a) for a in 
    -        check(f"{tag} 1 กดเปิด → เห็นครบ 5 ชิป", all(visible(page, a) is True for a in MORE), json.dumps({a: visible(page, a) for a in MORE}))
    +        check(f"{tag} 1 กดเปิด → เห็นครบ 4 ชิป (RG2b ถอดชิปประตู)", all(visible(page, a) is True for a in MORE), json.dumps({a: visible(page, a) for a in MORE}))
    -        fam_inline = js(page, """()=>{ const o={}; ['data-c-cashfree','data-c-l2','data-c-lshare','data-c-gate','data-c-missing'].forEach(a=>{ const e=document.querySele
    -        check(f"{tag} 3 บัญชีที่ไม่ active (fam): เงินสดว่าง/ชั้น 2/L/บันไดใหม่ บนหัวครบ · ขาดราคา 0 อยู่ใน details", fam_inline["data-c-cashfree"] is True and fam_inlin
    +        fam_inline = js(page, """()=>{ const o={}; ['data-c-cashfree','data-c-l2','data-c-lshare','data-c-missing'].forEach(a=>{ const e=document.querySelector('[data-co
    +        check(f"{tag} 3 บัญชีที่ไม่ active (fam): เงินสดว่าง/ชั้น 2/L/บันไดใหม่ บนหัวครบ · ขาดราคา 0 อยู่ใน details", fam_inline["data-c-cashfree"] is True and fam_inlin
    -        patch(page, lpct=0.99)
    -        check(f"{tag} 2 L เกินส่วน → [data-c-lshare] บนหัว (lv-over)", inside_more(page, "data-c-lshare") is False and js(page, f"()=>document.querySelector('{HEAD} [dat
    +        patch(page, lpct=1.2)
    +        check(f"{tag} 2 Ladder เกินถัง (ใช้ 120%) → [data-c-lshare] บนหัว (lv-over)", inside_more(page, "data-c-lshare") is False and js(page, f"()=>document.querySelect

## tests/run_tests_phase54.py

    -def launch(pw, w, h, mutate=None):
    +def pin_sat_pool(doc):
    +    """RG2b — เทส Sat เก่าคิดจากถัง Sat = capital.satB ทั้งก้อน: ตรึงสัดส่วนถังให้ถัง Sat = ทุน Sat เดิม (Winner:Ladder = 5:3 ของส่วนที่เหลือ) · ไม่แตะตัวเลขที่คาดหวังขอ
    +    for b in doc["books"].values():
    +        s = b["settings"]; cap = s.get("capital") or {}; fx = s.get("fx") or 1
    +        core, sat = float(cap.get("core") or 0), float(cap.get("satB") or 0) * fx
    +        if core + sat <= 0: continue
    +        sp = sat / (core + sat) * 100
    +        s["pools"] = {"winner": (100 - sp) * 5 / 8, "ladder": (100 - sp) * 3 / 8, "sat": sp, "mig": "RG2b", "reviewed": True}
    +
    +
    +def launch(pw, w, h, mutate=None, pin_sat=False):
    +    if pin_sat: pin_sat_pool(doc)   # หลัง mutate: fixture อาจตั้ง capital/fx ใหม่

## tests/run_tests_phase64.py

    -        check(f"{tag} 10 มี 'FF' แทน (Core: FF x% · ตั้งค่า: ประตู FF)", "FF" in pages["core"] and "FF gate" in pages["settings"], pages["core"][:100])
    +        check(f"{tag} 10 มี 'FF' แทน (Core: FF x% · ตั้งค่า: ประตู FF)", "FF" in pages["core"] and "FF gate" not in pages["settings"], pages["core"][:100])   # RG2b — ถอ

## tests/run_tests_phase65.py

    -        check(f"{tag} 1 บัญชีไม่มี coreRisk → ตาราง A 1.25/15/25 · B 1.25/10/25", v == {"sCrRiskA": "1.25", "sCrRiskB": "1.25", "sCrTierA": "15", "sCrTierB": "10", "sCrC
    +        check(f"{tag} 1 บัญชีไม่มี coreRisk → ตาราง A 1.25/15/25 · B 1.25/10/25", v == {"sCrRiskA": "1.25", "sCrRiskB": "1.25", "sCrTierA": "25", "sCrTierB": "25", "sCrC
    -        check(f"{tag} 1 หัวตาราง 'Risk/ไม้ · เพดานไม้แรก · เพดานรวม/หุ้น' · แถว A | B · ไม่มีช่อง sCrRisk เดิม", hdr == "|Risk/lot|1st-lot cap|Max/stock" and rows == "A|
    +        check(f"{tag} 1 หัวตาราง 'Risk/ไม้ · เพดานไม้แรก · เพดานรวม/หุ้น' · แถว A | B · ไม่มีช่อง sCrRisk เดิม", hdr == "" and rows == "" and js(page, "()=>!!document.ge
    +                js(page, "()=>!document.getElementById('sCrRisk')"), hdr + rows)
    -        check(f"{tag} 1 บรรทัดสูตรใต้ตาราง (ใช้ FF)", "min(Risk × FF ÷ (Entry − Stop), first-lot cap, cash)" in fm and "total cap/stock" in fm, fm)
    +        check(f"{tag} 1 บรรทัดสูตรใต้ตาราง (ใช้ FF)", "min(Risk × Regime size ÷ (Entry − Stop), max per stock, free Winner cash)" in fm and "max per stock" in fm, fm)
    -        check(f"{tag} 2 บันทึกไว้ riskPct:1.25 · tierA:12 → A Risk 1.25 · เพดานไม้แรก A 12 (คงเดิม) · B เพดานไม้แรก 10 (ใหม่) · รวม 25", v == {"sCrRiskA": "1.25", "sCrRi
    +        check(f"{tag} 2 บันทึกไว้ riskPct:1.25 · tierA:12 → A Risk 1.25 · เพดานไม้แรก A 12 (คงเดิม) · B เพดานไม้แรก 10 (ใหม่) · รวม 25", v == {"sCrRiskA": "1.25", "sCrRi
    -        fillnum(page, "sCrRiskA", 1.5); fillnum(page, "sCrRiskB", 1.0)
    +        fillnum(page, "sCrRiskA", 1.5)   # RG2b — Risk B ถูกถอด (B = A)
    -        check(f"{tag} 3 บันทึก → riskPct = 1.5 (= Risk A) · riskA 1.5 · riskB 1.0 · เพดานทั้งหมดครบ", saved["riskPct"] == 1.5 and saved["riskA"] == 1.5 and saved["riskB"
    +        check(f"{tag} 3 บันทึก → riskPct = 1.5 (= Risk A) · riskA 1.5 · winnerCap 25 · ไม่เขียน key Tier เดิมที่ไม่เคยตั้ง (riskB/tierA/tierB/capTotal)", saved["riskPct"
    -        check(f"{tag} 3 การ์ดแผน Tier A กับ B ราคาเดียวกัน (Entry 100 Stop 90) ได้จำนวนตามสูตร (เทียบ Calc.coreSize.firstLot ตรง) · Risk A 1.5% ≠ B 1.0% · เห็นบนการ์ด", 
    +        check(f"{tag} 3 การ์ดแผน Tier A กับ B ราคาเดียวกัน (Entry 100 Stop 90) ได้จำนวนตามสูตร (เทียบ Calc.coreSize.firstLot ตรง) · RG2b: Risk A = B = 1.5% จึงได้จำนวนเท
    -        case("sCrCapTotA", 10, "ต้องไม่น้อยกว่าเพดานไม้แรก", "เพดานรวม A (10) < เพดานไม้แรก A (15)")
    +        case("sCrWinCap", 0.5, "1–100", "เพดานต่อหุ้น 0.5 (RG2b ค่าเดียว · แทนเพดานรวม A/B)")
    -        case("sCrCapTotB", 5, "ต้องไม่น้อยกว่าเพดานไม้แรก", "เพดานรวม B (5) < เพดานไม้แรก B (10)")
    -        case("sCrRiskB", 6, "0.1–5", "Risk B 6")
    -        case("sCrTierA", 60, "1–50", "เพดานไม้แรก A 60")
    -        case("sCrCapTotA", 120, "1–100", "เพดานรวม A 120")
    -        open_settings(page); fillnum(page, "sCrCapTotA", 10)
    +        case("sCrRiskA", 6, "0.1–5", "Risk 6")
    +        case("sCrWinCap", 120, "1–100", "เพดานต่อหุ้น 120")
    +        open_settings(page); fillnum(page, "sCrWinCap", 120)
    -        check(f"{tag} 4 ค่าผิด: เรียก saveSettings() ตรง ๆ ก็ไม่บันทึก", js(page, "()=>{ const d=window.firebase.__mockDb.__dump()['users/testuid'].books.main.settings.c
    +        check(f"{tag} 4 ค่าผิด: เรียก saveSettings() ตรง ๆ ก็ไม่บันทึก", js(page, "()=>{ const d=window.firebase.__mockDb.__dump()['users/testuid'].books.main.settings.c
    -        check(f"{tag} 5 เพดานไม้แรก 30 · รวม 25 · Stop แคบ → ป้าย 'ชนเพดานรวม/หุ้น' · จำนวน = 25% ของถัง ÷ ราคา (ปัด 1 หุ้น US)", tag_txt == "ชนเพดานรวม/หุ้น" and f["sto
    +        check(f"{tag} 5 เพดานไม้แรก 30 · รวม 25 · Stop แคบ → ป้าย 'ชนเพดานรวม/หุ้น' · จำนวน = 25% ของถัง ÷ ราคา (ปัด 1 หุ้น US)", tag_txt == "ชนเพดาน Tier" and f["capped

## tests/run_tests_phase68.py

    -        check(f"{tag} 5 F2c ใช้ท่าที XAG: Long สวน Macro ▼ → align=against · ขนาด ×0.6 (WA1: ตัวคูณตาม Macro อย่างเดียว)", f["mac"] == "down" and f["align"] == "against"
    +        check(f"{tag} 5 F2c ใช้ท่าที XAG: Long สวน Macro ▼ → align=against · ขนาด ×1 (RG2b: ไม่มีตัวคูณ Macro)", f["mac"] == "down" and f["align"] == "against" and f["lf
    -        check(f"{tag} 5 สวน Macro + Trend สวน → ×0.6 (Trend ไม่มีผลเพิ่ม)", f == 0.6, str(f))
    +        check(f"{tag} 5 สวน Macro + Trend สวน → ×1 (RG2b: ไม่มีตัวคูณ Macro)", f == 1, str(f))

## tests/run_tests_phase69.py

    -        check(f"{tag} 4 Playbook XAU ▲ · แผน Long (ตาม) → ×1 · แผน Short (สวน) → ×0.6", L["f"] == 1 and S["f"] == 0.6, json.dumps([L["f"], S["f"]]))
    +        check(f"{tag} 4 Playbook XAU ▲ · แผน Long (ตาม) → ×1 · แผน Short (สวน) → ×1 (RG2b)", L["f"] == 1 and S["f"] == 1, json.dumps([L["f"], S["f"]]))   # RG2b — ไม่มีต
    -        check(f"{tag} 4 ตั้ง Neutral 0.8 → BRENT ×0.8 · Asset นอก Macro (S50) ×0.8 (เท่า Neutral)", bn["f"] == 0.8 and out["f"] == 0.8, json.dumps([bn["f"], out["f"]]))
    +        check(f"{tag} 4 ตั้ง Neutral 0.8 → BRENT ×0.8 · Asset นอก Macro (S50) ×0.8 (เท่า Neutral)", bn["f"] == 1 and out["f"] == 1, json.dumps([bn["f"], out["f"]]))   # 
    -        check(f"{tag} 4 ตั้ง สวน Macro 0.5 → ×0.5", S["f"] == 0.5)
    +        check(f"{tag} 4 ตั้ง สวน Macro 0.5 → ไม่มีผล ×1 (RG2b)", S["f"] == 1)
    -        check(f"{tag} 4 ปุ่ม 'ใช้ไม้เต็ม (ไม่ตามกฎ)' ยังใช้ได้กับสวน Macro → ×1", full["f"] == 1 and full["rf"] == 0.5)
    -        exp = js(page, "([c,r,f])=>Calc.satLot({riskAmount:r*f, dist:1, contract:c.contract, lotStep:c.lotStep, minLot:c.minLot}).lot", [S["cfg"], S["risk"], 0.5 * 0.5])
    +        check(f"{tag} 4 ปุ่ม 'ใช้ไม้เต็ม (ไม่ตามกฎ)' ยังใช้ได้กับสวน Macro → ×1", full["f"] == 1 and full["rf"] == 1)   # RG2b
    +        exp = js(page, "([c,r,f])=>Calc.satLot({riskAmount:r*f, dist:1, contract:c.contract, lotStep:c.lotStep, minLot:c.minLot}).lot", [S["cfg"], S["risk"], 1 * 0.5])  
    -        check(f"{tag} 4 ตั้งต่อบัญชี: main สวน 0.5 · fam สวน 0.7 (Neutral fam ค่าเริ่ม 1)", fa == [0.5, 0.7, 1], json.dumps(fa))
    +        check(f"{tag} 4 ตั้งต่อบัญชี: main สวน 0.5 · fam สวน 0.7 (Neutral fam ค่าเริ่ม 1)", fa == [1, 1, 1], json.dumps(fa))   # RG2b — ค่าที่ตั้งถูกเก็บไว้แต่ไม่อ่าน
    -        check(f"{tag} 4 ค่าผิดรูปใน settings (2) → ใช้ค่าเริ่ม 0.6", js(page, "()=>satRiskCfg('main').macroAgainst") == 0.6)
    +        check(f"{tag} 4 ค่าผิดรูปใน settings (2) → ไม่อ่าน = 1 (RG2b)", js(page, "()=>satRiskCfg('main').macroAgainst") == 1)
    -        check(f"{tag} 5 Macro สวน + Trend ตาม (Short, Trend ▼) → ×0.6 (กติกาเปลี่ยน — เดิม ×1)", b["f"] == 0.6, json.dumps(b["f"]))
    +        check(f"{tag} 5 Macro สวน + Trend ตาม (Short, Trend ▼) → ×1 (RG2b ถอดตัวคูณ Macro)", b["f"] == 1, json.dumps(b["f"]))   # RG2b
    -        check(f"{tag} 6 บันทึก order → ไม้เก็บ macro_note + macro_state against + size_rule 0.6 + sizeFactor 0.6", t and t["note"] == "เข้าสวนเพราะแนวรับแข็ง" and t["rul
    +        check(f"{tag} 6 บันทึก order → ไม้เก็บ macro_note + macro_state against + size_rule 1 + sizeFactor null", t and t["note"] == "เข้าสวนเพราะแนวรับแข็ง" and t["rule
    -        for fld in ("sSatMacroNeutral", "sSatMacroAgainst"):
    -            for v in ("0", "1.5", "", "0.05", "0.555"):
    -                page.fill("#" + fld, v); page.wait_for_timeout(60)
    -                bad[f"{fld}={v!r}"] = (err(fld) != "" and dis() is True)
    -            page.fill("#" + fld, "0.8"); page.wait_for_timeout(60)
    -        check(f"{tag} 7 ค่า 0 / 1.5 / ว่าง / 0.05 / 0.555 → error + ปุ่มบันทึกปิด ทั้ง 2 ช่อง", all(bad.values()), json.dumps(bad))
    -        check(f"{tag} 7 ค่าถูก (0.8) → ข้อความหาย · ปุ่มบันทึกเปิด", err("sSatMacroNeutral") == "" and err("sSatMacroAgainst") == "" and dis() is False)
    -        page.fill("#sSatMacroNeutral", "0.9"); page.fill("#sSatMacroAgainst", "0.4"); page.wait_for_timeout(60)
    -        js(page, "()=>saveSettings()"); page.wait_for_timeout(300)
    -        sv = js(page, "()=>[getBook('main').settings.satRisk, getBook('fam').settings.satRisk || null]")
    -        check(f"{tag} 7 บันทึก → main macroNeutral 0.9 · macroAgainst 0.4 · fam ไม่เปลี่ยน", sv[0]["macroNeutral"] == 0.9 and sv[0]["macroAgainst"] == 0.4 and "macroNeut
    +        # RG2b — ถอดตัวคูณขนาดตาม Macro (Neutral/Against) ออกจากหน้าตั้งค่า: ช่องไม่แสดงให้กรอก · ค่าที่ใช้จริง = 1 เสมอ แม้มีค่าเก่าค้างในข้อมูล
    +        vis = js(page, "()=>['sSatMacroNeutral','sSatMacroAgainst'].map(i=>{ const e = document.getElementById(i); return !e || !e.offsetParent; })")
    +        check(f"{tag} 7 (RG2b) ช่อง Macro Neutral/Against ไม่แสดงให้กรอก (ถอดแล้ว)", vis == [True, True], vis)
    -        check(f"{tag} 7 บัญชี Family ตั้งต่างจาก main ได้", js(page, "()=>[satRiskCfg('main').macroNeutral, satRiskCfg('fam').macroNeutral]") == [0.9, 0.5])
    +        check(f"{tag} 7 (RG2b) ค่า Macro ค้างในข้อมูล (0.5) ไม่มีผล: satRiskCfg macroNeutral/Against = 1", js(page, "()=>[satRiskCfg('main').macroNeutral, satRiskCfg('fa

## tests/run_tests_phase70.py

    -    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, mutate)
    +    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, mutate, pin_sat=True)   # RG2b — ถัง Sat ตรึงเท่าทุน Sat เดิม
    -        exp = sat_lot(page, c["riskCur"] * 0.6 * 0.5, 10)
    -        check(f"{tag} 1 สวน Macro (ตัวคูณ 0.6) ซ้อน 50%: riskAmount = RPT × 0.6 × 0.5 ({c['lot']} vs {exp})", c["f"] == 0.6 and c["lot"] == exp, json.dumps(c))
    +        exp = sat_lot(page, c["riskCur"] * 1 * 0.5, 10)   # RG2b — ไม่มีตัวคูณ Macro
    +        check(f"{tag} 1 สวน Macro (RG2b ไม่มีตัวคูณ) ซ้อน 50%: riskAmount = RPT × 0.5 ({c['lot']} vs {exp})", c["f"] == 1 and c["lot"] == exp, json.dumps(c))

## tests/run_tests_phase77.py

    -def launch(pw, w, h, pb=False, opt=0, bias="Long"):
    -    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(opt))
    +def launch(pw, w, h, pb=False, opt=0, bias="Long", pin_sat=None):
    +    if pin_sat is None: pin_sat = (__name__ == "__main__")   # RG2b — เมื่อรันชุดนี้เอง ตรึงถัง Sat = ทุน Sat เดิม (30%) · ชุดอื่นที่ใช้ launcher นี้ไม่ตรึงเว้นแต่ขอ
    +    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(opt), pin_sat=pin_sat)
    -        exp = {"mainPct": "70", "tacPct": "30", "rptMain": "2", "rptTac": "2", "maxDd": "20", "capMain": "2", "capTac": "4", "brkN": "5", "brkDd": "10", "tp1R": "2", "tp
    +        exp = {"rptMain": "1.5", "rptTac": "0.75", "maxDd": "20", "capMain": "1.4", "capTac": "1.2", "brkN": "5", "brkDd": "3", "tp1R": "2", "tp1Pct": "50", "tp2R": "3",
    -        check(f"{tag} 1 ตั้งค่า › Sat v2: ค่าเริ่มต้นครบ 21 ช่อง (PV2c: เดิม 19)", vals == exp, vals)
    +        check(f"{tag} 1 ตั้งค่า › Sat v2: ค่าเริ่มต้นครบ 19 ช่อง (RG2b: ถอด Main%/Tactical% · RPT 1.5/0.75 · cap 1.4×/1.2× · เบรก 3%)", vals == exp, vals)
    -        check(f"{tag} 1 ข้างช่องแสดง % ของพอร์ตรวม: Main 21% · Tactical 9% · RPT 0.42% / 0.18% · Max DD = 6% · เบรก DD = 0.9%",
    -              (hint("sV2Main"), hint("sV2Tac"), hint("sV2RptMain"), hint("sV2RptTac"), hint("sV2MaxDd"), hint("sV2BrkDd")) ==
    -              ("= 21% ของพอร์ตรวม", "= 9% ของพอร์ตรวม", "= 0.42% ของพอร์ตรวม", "= 0.18% ของพอร์ตรวม", "= 6% ของพอร์ตรวม", "= 0.9% ของพอร์ตรวม"),
    -              [hint(i) for i in ("sV2Main", "sV2Tac", "sV2RptMain", "sV2RptTac", "sV2MaxDd", "sV2BrkDd")])
    +        check(f"{tag} 1 ข้างช่องแสดง % ของพอร์ตรวม (RG2b ถัง Sat 30% ตรึง): RPT 0.45% / 0.23% · Max DD = 6% · เบรก DD = 0.9%",
    +              (hint("sV2RptMain"), hint("sV2RptTac"), hint("sV2MaxDd"), hint("sV2BrkDd")) ==
    +              ("= 0.45% ของพอร์ตรวม", "= 0.23% ของพอร์ตรวม", "= 6% ของพอร์ตรวม", "= 0.9% ของพอร์ตรวม"),
    +              [hint(i) for i in ("sV2RptMain", "sV2RptTac", "sV2MaxDd", "sV2BrkDd")])
    -        page.fill("#sV2Main", "60"); page.fill("#sV2Tac", "40"); page.wait_for_timeout(200)
    -        check(f"{tag} 1 แก้ 60:40 → Main 18% · Tactical 12% · ปุ่มบันทึกใช้ได้", hint("sV2Main") == "= 18% ของพอร์ตรวม" and hint("sV2Tac") == "= 12% ของพอร์ตรวม" and not
    -        check(f"{tag} 1 RPT เลือกได้ 4 ค่า 1 · 1.25 · 1.5 · 2", js(page, "()=>[...document.querySelectorAll('#sV2RptMain option')].map(o=>o.value)") == ["1", "1.25", "1.
    -        page.fill("#sV2Tac", "50"); page.wait_for_timeout(200)
    -        err = txt(page, '[data-err-for="sV2Tac"]') or ""
    -        check(f"{tag} 1 สัดส่วนรวม ≠ 100 → error + บันทึกไม่ได้", "100" in err and js(page, "()=>document.getElementById('setSaveBtn').disabled"), err)
    -        page.fill("#sV2Tac", "40")
    +        page.select_option("#sV2RptMain", "1.25"); page.wait_for_timeout(200)   # RG2b — ไม่มีสัดส่วน Main/Tactical แล้ว: เปลี่ยน RPT Main แทน
    +        check(f"{tag} 1 แก้ RPT Main 1.25 → 0.375% ของพอร์ตรวม · ปุ่มบันทึกใช้ได้", hint("sV2RptMain") == "= 0.38% ของพอร์ตรวม" and not js(page, "()=>document.getElement
    +        check(f"{tag} 1 RPT เลือกได้: Main 0.5 · 0.75 · 1 · 1.25 · 1.5 · 2 / Tactical 0.25 · 0.5 · 0.75 · 1 (RG2b)", js(page, "()=>[...document.querySelectorAll('#sV2Rpt
    +        pl_old = page.input_value("#sPoolS"); page.fill("#sPoolS", "25"); page.wait_for_timeout(200)
    +        err = txt(page, '[data-err-for="sPoolS"]') or ""
    +        check(f"{tag} 1 สัดส่วนถังรวม ≠ 100 → error + บันทึกไม่ได้ (RG2b: แทนสัดส่วน Main/Tactical)", "100" in err and js(page, "()=>document.getElementById('setSaveBtn'
    +        page.fill("#sPoolS", pl_old)
    -        fillx(page, "#sV2SetupsMain", "Break EMA20\nแนวรับ Day"); page.select_option("#sV2RptTac", "1.25"); fillx(page, "#sV2Tf" + "Tac", "15m"); page.wait_for_timeout(1
    +        fillx(page, "#sV2SetupsMain", "Break EMA20\nแนวรับ Day"); page.select_option("#sV2RptTac", "1"); fillx(page, "#sV2Tf" + "Tac", "15m"); page.wait_for_timeout(150)
    -        check(f"{tag} 1 บันทึกแล้วอ่านกลับได้ (60:40 · RPT Tactical 1.25 · TF 15m · Setup Main แก้ชื่อ/ลบ/เพิ่ม)", (cfg["mainPct"], cfg["tacPct"], cfg["rptTac"], cfg["tf
    -        check(f"{tag} 1 บัญชี Family ยังเป็นค่าเริ่มต้น (ตั้งต่างบัญชีได้)", js(page, "()=>{ const c = satV2Cfg('fam'); return [c.mainPct, c.rptTac, c.tfTac]; }") == [70
    +        check(f"{tag} 1 บันทึกแล้วอ่านกลับได้ (RPT Main 1.25 · RPT Tactical 1 · TF 15m · Setup Main แก้ชื่อ/ลบ/เพิ่ม)", (cfg["rptMain"], cfg["rptTac"], cfg["tfTac"], cfg
    +        check(f"{tag} 1 บัญชี Family ยังเป็นค่าเริ่มต้น (ตั้งต่างบัญชีได้)", js(page, "()=>{ const c = satV2Cfg('fam'); return [c.rptMain, c.rptTac, c.tfTac]; }") == [1.
    -        check(f"{tag} 1 เปิดตั้งค่าบัญชี Family → เห็นค่าของ Family (70:30 · 4H)", page.input_value("#sV2Main") == "70" and page.input_value("#sV2TfTac") == "4H")
    -        page.fill("#sV2Main", "80"); page.fill("#sV2Tac", "20"); page.wait_for_timeout(150); page.click("#setSaveBtn"); page.wait_for_timeout(500)
    -        check(f"{tag} 1 Family ตั้ง 80:20 ได้ แยกจากบัญชีหลัก (60:40)", js(page, "()=>[satV2Cfg('fam').mainPct, satV2Cfg('main').mainPct]") == [80, 60])
    +        check(f"{tag} 1 เปิดตั้งค่าบัญชี Family → เห็นค่าของ Family (RPT Main 1.5 · 4H)", page.input_value("#sV2RptMain") == "1.5" and page.input_value("#sV2TfTac") == "
    +        page.select_option("#sV2RptMain", "2"); page.wait_for_timeout(150); page.click("#setSaveBtn"); page.wait_for_timeout(500)
    +        check(f"{tag} 1 Family ตั้ง RPT Main 2 ได้ แยกจากบัญชีหลัก (1.25)", js(page, "()=>[satV2Cfg('fam').rptMain, satV2Cfg('main').rptMain]") == [2, 1.25])
    -        js(page, "()=>switchTab('mix')"); page.wait_for_timeout(500)
    -        segs = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-pv2-port=main] [data-pv2-seg]')].map(e=>[e.dataset.pv2Seg, +e.dataset.pct]))")
    -        check(f"{tag} 2 Port: Core 70 · Main 21 · Tactical 9", segs == {"core": 70, "main": 21, "tactical": 9}, segs)
    -        rows = js(page, "()=>[...document.querySelectorAll('[data-pv2-port=main] [data-pv2-row]')].map(e=>e.dataset.pv2Row)")
    -        t = txt(page, "[data-pv2-port=main]") or ""
    -        check(f"{tag} 2 ไม่มี Option ในการแบ่งเงิน (บัญชีหลักไม่มีแถว อื่น ๆ) · มีเงินแต่ละส่วน", rows == ["core", "main", "tactical"] and "Option" not in t and "$31,500
    -        shot(page, f"pv2a-port-{sfx}.png", "[data-pv2-port=main]")
    -        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(500); js(page, "()=>switchTab('mix')"); page.wait_for_timeout(400)
    -        lg = txt(page, "[data-pv2-port=fam] [data-pv2-row=legacy]") or ""
    -        check(f"{tag} 2 ข้อมูล Option เดิม (Family ฿50,000) → 'อื่น ๆ (เดิม)' อ่านอย่างเดียว ไม่นับในแถบ", "อื่น ๆ (เดิม)" in lg and "50,000" in lg and js(page, "()=>doc
    +        js(page, "()=>{ switchTab('mix'); ln3PortSet('main'); renderPortfolioMix(); }"); page.wait_for_timeout(500)
    +        line = txt(page, "[data-pool-txt]") or ""
    +        check(f"{tag} 2 Port (RG2b เส้นถัง แทนแถบ Core/Main/Tactical): เป้า Winner · Ladder · Sat 30 (ตรึงเท่าทุน Sat เดิม)", line.endswith("Sat 0/30") and "Winner 0/44"
    +        js(page, "()=>{ document.querySelector('[data-pool-line]').open = true; }")
    +        rows = js(page, "()=>[...document.querySelectorAll('[data-pool-line] [data-pool-bar]')].map(e=>e.dataset.poolBar)")
    +        t = txt(page, "[data-pool-line]") or ""
    +        check(f"{tag} 2 ไม่มี Option ในการแบ่งเงิน (บัญชีหลักไม่มีแถว อื่น ๆ) · มีเงินแต่ละถัง", rows[:3] == ["winner", "ladder", "sat"] and len(rows) % 3 == 0 and "Opti
    +        shot(page, f"pv2a-port-{sfx}.png", "[data-pool-line]")
    +        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(500); js(page, "()=>{ switchTab('mix'); ln3PortSet('fam'); renderPortfolioMix(); document.querySelector(
    +        lg = js(page, "()=>{ const e = document.querySelector('[data-pool-line] [data-pv2-row=legacy]'); return e ? e.textContent : ''; }")
    +        check(f"{tag} 2 ข้อมูล Option เดิม (Family ฿50,000) → 'อื่น ๆ (เดิม)' อ่านอย่างเดียว ไม่นับในแถบ", "อื่น ๆ (เดิม)" in lg and "50,000" in lg and js(page, "()=>doc
    -        check(f"{tag} 3 Tactical: lot ตาม Risk 0.135 · เพดาน 4× → ใช้ 0.12 (จำกัดโดยเพดานมูลค่า)", abs(c["rawRisk"] - 0.135) < 1e-6 and c["limit"] == "cap" and c["lot"] 
    +        check(f"{tag} 3 Tactical: lot ตาม Risk 0.169 · เพดาน 1.2× → ใช้ 0.12 (จำกัดโดยเพดานมูลค่า)", abs(c["rawRisk"] - 0.16875) < 1e-6 and c["limit"] == "cap" and c["lo
    -        check(f"{tag} 3 ตารางขนาดไม้บอก RPT $270 → 0.135 · เพดาน 0.127 · ใช้ 0.12 · 'เพดานมูลค่า'", "$270" in sz and "0.135" in sz and "0.12" in sz and "เพดานมูลค่า" in 
    +        check(f"{tag} 3 ตารางขนาดไม้บอก RPT $338 → 0.169 · เพดาน 0.127 · ใช้ 0.12 · 'เพดานมูลค่า'", "$338" in sz and "0.1688" in sz and "0.12" in sz and "เพดานมูลค่า" in
    -        check(f"{tag} 4 ตารางขนาดไม้: RPT Main 2% $630 → 0.1 · ใช้ 0.1 lot · Risk $630", "$630" in sz and "0.1" in sz and "RPT Main 2%" in sz, sz)
    +        check(f"{tag} 4 ตารางขนาดไม้: RPT Main 1.5% $675 → 0.107 · ใช้ 0.1 lot · Risk $630", "$630" in sz and "0.1071" in sz and "RPT Main 1.5%" in sz, sz)
    -        check(f"{tag} 6 สวน Macro (Short vs Playbook ▲) → ตัวคูณ ×0.6 ใช้กับ Tactical: Risk $162 → 0.081", c["factor"] == 0.6 and abs(c["rawRisk"] - 0.081) < 1e-6 and c[
    -        check(f"{tag} 6 สวน Macro ต้องเขียนเหตุผลก่อน (ไม่ ready) · บอก 'ลด 40%'", not c["ready"] and "ลด 40%" in (txt(page, "[data-f2c-row=size]") or ""), [c["ready"], 
    +        check(f"{tag} 6 สวน Macro (Short vs Playbook ▲) → RG2b ไม่มีตัวคูณ Macro (×1): Risk $338 → 0.169 (ติดเพดาน 0.12)", c["factor"] == 1 and abs(c["rawRisk"] - 0.1687
    +        check(f"{tag} 6 สวน Macro ต้องเขียนเหตุผลก่อน (ไม่ ready) · ไม่มีข้อความ 'ลด 40%' (RG2b)", not c["ready"] and "ลด 40%" not in (txt(page, "[data-f2c-row=size]") o

## tests/run_tests_phase78.py

    -import json, os
    +import functools, json, os
    -launch, idea = P77.launch, P77.idea
    +launch, idea = functools.partial(P77.launch, pin_sat=True), P77.idea
    -    return T(id, "satB", status, sym=sym, bias=bias, entry=entry, sl=sl, qty=qty, mult=100 if sym == "XAUUSD" else 1, cur="USD", sleeve=sleeve, date="2026-09-29", opened
    +    kw.setdefault("date", "2026-09-29"); kw.setdefault("openedAt", kw["date"])
    +    return T(id, "satB", status, sym=sym, bias=bias, entry=entry, sl=sl, qty=qty, mult=100 if sym == "XAUUSD" else 1, cur="USD", sleeve=sleeve, **kw)
    -        def tl(i, d, pnl_usd, k="x"): return sat_t(f"{k}{i}", status="closed", sleeve="tactical", entry=4180, sl=4160, qty=0.10, exitPrice=4180 + pnl_usd / 10.0, exitDat
    +        def tl(i, d, pnl_usd, k="x"): return sat_t(f"{k}{i}", status="closed", sleeve="tactical", entry=4180, sl=4160, qty=0.10, exitPrice=4180 + pnl_usd / 10.0, exitDat
    -        check(f"{tag} 5 DD Tactical 10.4% ≥ 10% (เสียติดแค่ 2) → หยุด · ข้อความ DD", br[1] and br[0] == 2 and br[2] == 10.4 and "DD 10.4%/10%" in br[3] and not cT["ready
    +        check(f"{tag} 5 DD Sat 3.1% ≥ 3% (เสียติดแค่ 2 · RG2b เบรก DD ฐานถัง Sat) → หยุด · ข้อความ DD", br[1] and br[0] == 2 and br[2] == 3.1 and "DD 3.1%/3%" in br[3] a
    -        check(f"{tag} 5 ชนะ 1 ไม้ (DD เหลือ 8.1% < 10%) → ปลด", br is False)
    +        check(f"{tag} 5 ชนะ 1 ไม้ (DD เหลือ 2.4% < 3%) → ปลด", br is False)

## tests/run_tests_phase79.py

    -import json, os
    +import functools, json, os
    -launch, idea, calc = P77.launch, P77.idea, P77.calc
    +launch, idea, calc = functools.partial(P77.launch, pin_sat=True), P77.idea, P77.calc

## tests/run_tests_phase80.py

    -import json, os, re
    +import functools, json, os, re
    -launch, idea, calc = P77.launch, P77.idea, P77.calc
    +launch, idea, calc = functools.partial(P77.launch, pin_sat=True), P77.idea, P77.calc

## tests/run_tests_phase81.py

    -    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture())
    +    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(), pin_sat=True)   # RG2b — ถัง Sat ตรึงเท่าทุน Sat เดิม
    -        check(f"{tag} 1 พับ 'รายละเอียดและกฎบัญชี': เงิน Sat · Main/Tactical · เพดาน Sat/ต่อสินค้า/Core+Sat · วิธีนับ", all(k in det for k in ("เงิน Sat", "Main 70%", "T
    +        check(f"{tag} 1 พับ 'รายละเอียดและกฎบัญชี': เงิน Sat · Main/Tactical · เพดาน Sat/ต่อสินค้า/Core+Sat · วิธีนับ", all(k in det for k in ("เงิน Sat", "Main + Tactic
    -        check(f"{tag} 4 Tactical: '▲ · 2% · OUN $x · FAM $y · ● Loss 0/5 · DD 0/10%' (LN3 + LN3fix3c) · ไม่แสดงไม้ใหม่", ft and ft["k"] == "tactical" and ft["t"] == (f"▲
    +        check(f"{tag} 4 Tactical: '▲ · 2% · OUN $x · FAM $y · ● Loss 0/5 · DD 0/10%' (LN3 + LN3fix3c) · ไม่แสดงไม้ใหม่", ft and ft["k"] == "tactical" and ft["t"] == (f"▲
    -        check(f"{tag} 4 ถึงเกณฑ์ → '⛔ พัก Tactical' (สีแดง) + 'พัก Tactical · แพ้ติด 5 ไม้ → ชนะ 1 ไม้ หรือขาดทุนลดต่ำกว่า 10% แล้วเทรดได้เอง' (LN3)", ft2 == f"⛔ พัก Tac
    +        check(f"{tag} 4 ถึงเกณฑ์ → '⛔ พัก Tactical' (สีแดง) + 'พัก Tactical · แพ้ติด 5 ไม้ → ชนะ 1 ไม้ หรือขาดทุนลดต่ำกว่า 3% แล้วเทรดได้เอง' (LN3)", ft2 == f"⛔ พัก Tact

## tests/run_tests_phase82.py

    -        check(f"{tag} 7 สถานะ Tactical: '▲ · 2% · <บัญชี> $270 · <บัญชี> $180 · ● Loss 0/5 · DD 0/10%' (LN3fix3c: ทุกบัญชี · ≤340px แสดงจุดสีแทนชื่อ)", re.fullmatch(r"▲ 
    +        check(f"{tag} 7 สถานะ Tactical (RG2b: RPT 0.75% ของถัง Sat · DD 3%): '▲ · 0.75% · <บัญชี> $225 · <บัญชี> $203 · ● Loss 0/5 · DD 0/3%' (LN3fix3c: ทุกบัญชี · ≤340p
    -        check(f"{tag} 7 สถานะ Main: '▲ · Macro ▲ · 2% · <บัญชี> $630 · <บัญชี> $420 · ไม้ใหม่ 0/5' (LN3fix3c: ทุกบัญชี)", re.fullmatch(r"▲ Up · Macro ▲ · 2% · (?:\S+ )?\
    +        check(f"{tag} 7 สถานะ Main (RG2b: RPT 1.5% · โควตา 4): '▲ · Macro ▲ · 1.5% · <บัญชี> $450 · <บัญชี> $405 · ไม้ใหม่ 0/4' (LN3fix3c: ทุกบัญชี)", re.fullmatch(r"▲ U

## tests/run_tests_phase83.py

    -        all_ = js(page, "()=>({pies: document.querySelectorAll('#mixBody .piechart').length, structs: document.querySelectorAll('[data-pv2-port]').length, line: !!docume
    -        check(f"{tag} 2 โหมดรวม: วงกลมเดียวของ Core (+ Sat ถ้ามีหุ้น/ETF) · โครงพอร์ตทุกบัญชี · ไม่มีบัญชีเรียงซ้อนแบบเดิม", all_["pies"] == 1 and all_["structs"] == 2 a
    +        all_ = js(page, "()=>({pies: document.querySelectorAll('#mixBody .piechart').length, structs: document.querySelectorAll('[data-pool-line]').length, line: !!docum
    +        check(f"{tag} 2 โหมดรวม: วงกลมเดียวของ Core (+ Sat ถ้ามีหุ้น/ETF) · โครงพอร์ตทุกบัญชี · ไม่มีบัญชีเรียงซ้อนแบบเดิม", all_["pies"] == 1 and all_["structs"] == 1 a
    -        check(f"{tag} 2 เลือกบัญชีหลัก → โครงพอร์ตเหลือบัญชีเดียว · จำค่าไว้ (localStorage) แม้วาดใหม่", cnt(page, "[data-pv2-port]") == 1 and js(page, "()=>localStorage
    +        check(f"{tag} 2 เลือกบัญชีหลัก → โครงพอร์ตเหลือบัญชีเดียว · จำค่าไว้ (localStorage) แม้วาดใหม่", cnt(page, "[data-pool-line]") == 1 and js(page, "()=>localStorag
    -        st = js(page, "()=>{ const e = document.querySelector('[data-pv2-port]'); return {rows: [...e.querySelectorAll('[data-pv2-row]')].map(r=>r.dataset.pv2Row), segs:
    -        check(f"{tag} 3 โครงพอร์ต: แถบ Core/Main/Tactical + แถวยอด 3 บรรทัด", st["segs"] == ["core", "main", "tactical"] and st["rows"] == ["core", "main", "tactical"], 
    +        st = js(page, "()=>{ const e = document.querySelector('[data-pool-line]'); e.open = true; return {rows: [...e.querySelectorAll('[data-pool-bar]')].map(r=>r.datas
    +        check(f"{tag} 3 โครงพอร์ต (RG2b: เส้นถัง): แถบ Winner/Ladder/Sat ในแถบพับ", st["rows"] == ["winner", "ladder", "sat"], st)
    -        check(f"{tag} 3 Family (มีถัง Option) → แถว 'อื่น ๆ (เดิม) · ถัง Option' ยังอยู่ อ่านอย่างเดียว", cnt(page, "[data-pv2-row=legacy]") == 1 and "ถัง Option" in (bo
    +        check(f"{tag} 3 Family (มีถัง Option) → แถว 'อื่น ๆ (เดิม) · ถัง Option' ยังอยู่ อ่านอย่างเดียว", cnt(page, "[data-pv2-row=legacy]") == 1 and "ถัง Option" in (js
    -        check(f"{tag} 4 พับ 'ความเสี่ยง Core (ชั้น 2 · W/L · บันได)': ถึง Stop ตอนนี้ · เต็ม / เพดาน · L รวม · เงินว่าง · บันไดใหม่", all(k in rk for k in ("ถึง Stop ตอน
    +        check(f"{tag} 4 พับ 'ความเสี่ยง Core (ชั้น 2 · W/L · บันได)': ถึง Stop ตอนนี้ · เต็ม · Ladder · เงินว่าง (RG2b: ไม่มีเพดานรวม/L รวม/บันไดใหม่)", all(k in rk for 

## tests/run_tests_phase84.py

    -        check(f"{tag} 5 ตาราง 'ดูตัวเลข': คอลัมน์ heat → 'Open Risk Sat' · ยังมี DD Core · DD Sat · ไม้ใหม่ · ชั้น 2 + ประตู FF", "Open Risk Sat" in th and not any("heat
    +        check(f"{tag} 5 ตาราง 'ดูตัวเลข': คอลัมน์ heat → 'Open Risk Sat' · ยังมี DD Core · DD Sat · ไม้ใหม่ · ชั้น 2 + ประตู FF", "Open Risk Sat" in th and not any("heat

## tests/run_tests_phase89.py

    -        check(f"{tag} 1 บนสุดปุ่ม 'Core | Sat' (ไม่มี 'Port หุ้น / Port Future') · Core ติดอยู่", sw["a"] == "Core" and sw["b"] == "Sat" and sw["onA"], sw)
    +        check(f"{tag} 1 บนสุดปุ่ม 'Core | Sat' (ไม่มี 'Port หุ้น / Port Future') · Core ติดอยู่", sw["a"] == "Winner" and sw["b"] == "Sat" and sw["onA"], sw)   # RG2b — 
    -        check(f"{tag} 1 กล่องมืดกล่องเดียว: 'Core' + 'ทุน ฿4.2M'", box["n"] == 1 and box["cap"] == "ทุน ฿8.4M", box)   # LN3fix3c §4: หัว Core = ทุนรวมทุกบัญชี (2 × ฿4.2
    +        check(f"{tag} 1 กล่องมืดกล่องเดียว: 'Core' + 'ทุน ฿4.2M'", box["n"] == 1 and box["cap"] == "ทุน ฿9.6M", box)   # LN3fix3c §4: หัว Core = ทุนรวมทุกบัญชี (2 × ฿4.2
    -          return {now: fmt2(rk.layer2Pct)+'%', lim: fmt2(cfg.l2Cap)+'%', full: fmt2(rk.layer2FullPct)+'%', wPct: fmt2(cx.wCost/tank*100), lPct: fmt2(sp.lPct*100), lcap: 
    -            free: '฿'+fmt0(sp ? tank-cx.wCost-sp.lUsed : tank-cx.held), ff: Math.round(cx.F.f*100)+'%', dd: fmt2(Math.round(ddEval(A,'core').ddPct*100)/100)+'%'}; }""")
    -        got = js(page, "()=>({now: document.querySelector('[data-lf-row=main] [data-lf-now]').innerText.trim(), lim: document.querySelector('[data-lf-row=main] [data-lf-
    -        ok = got["now"] == ref["now"] and got["lim"] == ref["lim"] and got["full"] == ref["full"] and got["wp"] == ref["wPct"] + "%" and got["lp"] == ref["lPct"] and f"L
    +          return {now: fmt2(rk.layer2Pct)+'%', full: fmt2(rk.layer2FullPct)+'%', wPct: fmt2(cx.wCost/tank*100), lPct: fmt2(sp.lPct*100), lcap: fmt2(cfg.ladderShare),
    +            free: '฿'+fmt0(sp ? (sp.cashFree + sp.lCashFree) : (tank-cx.held)), ff: Math.round(cx.F.f*100)+'%', dd: fmt2(Math.round(ddEval(A,'winner').ddPct*100)/100)+'%
    +        got = js(page, "()=>({now: document.querySelector('[data-lf-row=main] [data-lf-now]').innerText.trim(), full: document.querySelector('[data-lf-full]').textConten
    +        ok = got["now"] == ref["now"] and got["full"] == ref["full"] and got["wp"] == ref["wPct"] + "%" and got["lp"] == ref["lPct"] and f"Ladder {ref['lPct']}%" in got[
    -        check(f"{tag} 1 พับ 'รายละเอียดและกฎ': ตำแหน่ง · Ladder ใหม่/ประตู · เพดานต่อตัว · Stop ฉุกเฉิน · ถ้าทุกไม้โดน Stop บัญชีลด", all(k in det for k in ("ตำแหน่ง 1 ต
    +        check(f"{tag} 1 พับ 'รายละเอียดและกฎ': ตำแหน่ง · Ladder ใหม่/ประตู · เพดานต่อตัว · Stop ฉุกเฉิน · ถ้าทุกไม้โดน Stop บัญชีลด", all(k in det for k in ("ตำแหน่ง 1 ต
    -        check(f"{tag} 1 การ์ด 2 บรรทัด: NVDA 'A · Winners' + 'ไม้ 1 · SL 115' · AVGO 'B · Winners' + 'แผน · 300 / 270 · ไม้แรก 17 หุ้น'",
    -              nv.get("tag") == "A · Winners" and nv.get("l2") == "ไม้ 1 · SL 115" and av.get("tag") == "B · Winners" and av.get("l2") == "แผน · 300 / 270 · ไม้แรก 17 หุ้
    +        check(f"{tag} 1 การ์ด 2 บรรทัด: NVDA 'A · Winners' + 'ไม้ 1 · SL 115' · AVGO 'B · Winners' + 'แผน · 300 / 270 · ไม้แรก 15 หุ้น' (RG2b ถัง Winner 50%)",
    +              nv.get("tag") == "A · Winners" and nv.get("l2") == "ไม้ 1 · SL 115" and av.get("tag") == "B · Winners" and av.get("l2") == "แผน · 300 / 270 · ไม้แรก 15 หุ้
    -            # กลยุทธ์ Winners|Ladder
    -            page.fill("#cnTicker", "TSM"); page.fill("#cnEntry", "300"); page.fill("#cnStop", "270"); page.wait_for_timeout(250)
    -            sg = js(page, "()=>({w: document.getElementById('cnStratW').innerText.trim(), l: document.getElementById('cnStratL').innerText.trim(), ld: document.getElemen
    -            check(f"{tag} 2 กลยุทธ์ 'Winners | Ladder' + บรรทัด 'Ladder (ถัวตามแนวรับ) ใช้ได้เฉพาะ A Fortress' · A Fortress → Ladder กดได้", sg["w"] == "Winners" and sg[
    +            # RG2b — ถอดตัวเลือกกลยุทธ์ Winners|Ladder ออกจากฟอร์ม (หน้า Winner สร้างแผน Winner เท่านั้น · Ladder ไปสร้างที่หน้า Ladder)
    +            sg = js(page, "()=>({box: !!document.getElementById('cnStratBox'), w: !!document.getElementById('cnStratW'), l: !!document.getElementById('cnStratL'), strat:
    +            check(f"{tag} 2 (RG2b) ฟอร์ม Winner ไม่มีตัวเลือก 'Winners | Ladder' และไม่มีบรรทัดอธิบาย Ladder · strat = W", sg == {"box": False, "w": False, "l": False, "
    -            sg2 = js(page, "()=>({ld: document.getElementById('cnStratL').disabled, strat: coreNew.strat})")
    -            check(f"{tag} 2 Tier ไม่ใช่ A Fortress → Ladder กดไม่ได้ (ปิด) · กลับเป็น Winners", sg2["ld"] and sg2["strat"] == "W", sg2)
    +            sg2 = js(page, "()=>coreNew.strat")
    +            check(f"{tag} 2 (RG2b) Tier ไม่ใช่ A Fortress → ยังเป็น Winners (W)", sg2 == "W", sg2)
    -        r = js(page, "()=>{ const e = [...document.querySelectorAll('#corePanel .ccRow')].find(x=>x.querySelector('[data-c-ticker]').innerText==='ZZZ'); return e ? {tag:
    -        check(f"{tag} 3 การ์ดแผน Ladder: ป้าย 'A · Ladder' · บรรทัด 2 'แผน · L1 … · SL …' (ไม่มีคำ 'บันได')", r is not None and r["tag"] == "A · Ladder" and r["l2"].star
    +        onwin = js(page, "()=>[...document.querySelectorAll('#corePanel .ccRow')].some(x=>x.querySelector('[data-c-ticker]').innerText==='ZZZ')")
    +        js(page, "()=>{ setPlanScope('ladder'); render(); }"); page.wait_for_timeout(400)
    +        r = js(page, "()=>{ const e = document.querySelector('[data-ldr-card][data-ldr-tk=ZZZ]'); return e ? e.innerText.replace(/\\s+/g,' ') : null; }")
    +        check(f"{tag} 3 (RG2b) การ์ดแผน Ladder ไม่อยู่หน้า Winner · อยู่หน้า Ladder (T1 … SL …)", (not onwin) and r is not None and "ZZZ" in r and "T1" in r, [onwin, r])
    -        check(f"{tag} 3 โหมดเดิม (legacy) แผน Core เหมือนเดิม: ปุ่ม 'Port หุ้น' · การ์ดบัญชี Hold/Plan · กล่อง 4 ช่อง · Positions · หัวบัญชี Core · ไม่มีกล่อง Lean", lg[
    +        check(f"{tag} 3 โหมดเดิม (legacy) แผน Core เหมือนเดิม: ปุ่ม 'Winner' (RG2b) · การ์ดบัญชี Hold/Plan · กล่อง 4 ช่อง · Positions · หัวบัญชี Core · ไม่มีกล่อง Lean",
    -        lf = js(page, "()=>({w: !!document.getElementById('cnStratW'), txt: document.getElementById('cnStratW').innerText, tierbtn: !!document.getElementById('cnTierB'),
    -        check(f"{tag} 3 ฟอร์ม legacy เหมือนเดิม: 'ระบบ Week' · ปุ่ม Tier 4 ตัวเลือก · บัญชี 'ทั้งคู่'", lf["txt"] == "ระบบ Week" and lf["tierbtn"] and not lf["lean"] and
    +        lf = js(page, "()=>({w: !!document.getElementById('cnStratW'), txt: 'ไม่มี', tierbtn: !!document.getElementById('cnTierB'), lean: !!document.querySelector('[data
    +        check(f"{tag} 3 ฟอร์ม legacy เหมือนเดิม: (RG2b ไม่มีตัวเลือกกลยุทธ์) · ปุ่ม Tier 4 ตัวเลือก · บัญชี 'ทั้งคู่'", not lf["w"] and lf["tierbtn"] and not lf["lean"] 
    -        check(f"{tag} 3 สลับกลับ Lean → ปุ่ม 'Core' + กล่อง Lean กลับมา", back["a"] == "Core" and back["lf"] == 1, back)
    +        check(f"{tag} 3 สลับกลับ Lean → ปุ่ม 'Winner' + กล่อง Lean กลับมา", back["a"] == "Winner" and back["lf"] == 1, back)

## tests/run_tests_phase91.py

    -    b, page, ce, pe = C.launch2(pw, w, h, trades, cards, **kw)
    +    b, page, ce, pe = C.launch2(pw, w, h, trades, cards, pin_winner=True, **kw)   # RG2b — ถัง Winner ตรึงเท่าทุน Core เดิม
    -        check(f"{tag} 9 กล่องสรุป: 'ทุน ฿8.4M' (รวมทุกบัญชี · LN3fix3c) · 'Risk Core x% / 20%' · 'ว่าง ฿' · บรรทัด 'DD · FF · n ตัว' (ไม่มี Winners/Ladder/฿/ถ้า Ladder เ
    +        check(f"{tag} 9 กล่องสรุป: 'ทุน ฿9.88M' (RG2b = Winner + Ladder ของทั้ง 2 บัญชี) (รวมทุกบัญชี · LN3fix3c) · 'Risk Core x% / 20%' · 'ว่าง ฿' · บรรทัด 'DD · FF · n
    -        check(f"{tag} 9 พับ 'รายละเอียดและกฎ' มี ฿ · ถ้า Ladder เต็ม · Winners ถือ · Ladder % · ตำแหน่ง · Ladder ใหม่ · Stop ฉุกเฉิน · บัญชีลด", all(k in det for k in ("
    +        check(f"{tag} 9 พับ 'รายละเอียดและกฎ' มี ฿ · ถ้า Ladder เต็ม · Winners ถือ · Ladder % · ตำแหน่ง · Ladder ใหม่ · Stop ฉุกเฉิน · บัญชีลด", all(k in det for k in ("
    -        v0 = js(page, "()=>({first: document.getElementById('sCrRiskFirst').value, acc: document.getElementById('sCrRiskAcc').value, cap: document.getElementById('sCrCap
    +        v0 = js(page, "()=>({first: document.getElementById('sCrRiskFirst').value, acc: document.getElementById('sCrRiskAcc').value, cap: document.getElementById('sCrWin
    -        page.fill("#sCrRiskFirst", "0.5"); page.fill("#sCrCapTotA", "30"); page.wait_for_timeout(250)
    -        e2 = js(page, "()=>document.querySelector('[data-err-for=sCrCapTotA]').innerText")
    -        check(f"{tag} 11 เพดานเงินต่อหุ้น > 25 → ข้อความ 'ต้องอยู่ระหว่าง 1–25'", "1–25" in e2, e2)
    -        page.fill("#sCrCapTotA", "10"); page.wait_for_timeout(250)
    +        page.fill("#sCrRiskFirst", "0.5"); page.fill("#sCrWinCap", "101"); page.wait_for_timeout(250)
    +        e2 = js(page, "()=>document.querySelector('[data-err-for=sCrWinCap]').innerText")
    +        check(f"{tag} 11 เพดานเงินต่อหุ้น > 100 → ข้อความ 'ต้องอยู่ระหว่าง 1–100' (RG2b: ช่อง Max per stock ค่าเดียว)", "1–100" in e2, e2)
    +        page.fill("#sCrWinCap", "10"); page.wait_for_timeout(250)
    -        check(f"{tag} 11 เพดานไม้แรก (15) > เพดานต่อหุ้น (10) → บรรทัดเตือนใต้ช่อง (ไม่บล็อกการบันทึก)", "⚠" in warn and "เพดานเงินต่อหุ้น" in warn and not js(page, "()=
    -        page.fill("#sCrCapTotA", "20"); page.fill("#sCrRiskAcc", "0.4"); page.wait_for_timeout(250)
    +        check(f"{tag} 11 (RG2b) เพดานต่อหุ้นค่าเดียว (10) → ไม่มีบรรทัดเตือนเทียบเพดานไม้แรก · ไม่บล็อกการบันทึก", "⚠" not in warn and not js(page, "()=>document.getElem
    +        page.fill("#sCrWinCap", "20"); page.fill("#sCrRiskAcc", "0.4"); page.wait_for_timeout(250)
    -        cr = js(page, "()=>{ const c = getBook('main').settings.coreRisk; return {first: c.riskFirst, acc: c.riskAcc, cap: c.capTotalA, riskA: c.riskA, maxLots: c.maxLot
    +        cr = js(page, "()=>{ const c = getBook('main').settings.coreRisk; return {first: c.riskFirst, acc: c.riskAcc, cap: c.winnerCap, riskA: c.riskA, maxLots: c.maxLot
    -        cfg = js(page, "()=>{ const c = coreRiskCfg('main'), o = coreSizeOpts('main'); return [c.riskFirst, c.riskAcc, c.capTotalA, o.riskFirst, o.riskAcc, o.stockCap.A]
    +        cfg = js(page, "()=>{ const c = coreRiskCfg('main'), o = coreSizeOpts('main'); return [c.riskFirst, c.riskAcc, c.winnerCap, o.riskFirst, o.riskAcc, o.stockCap.A]
    -    b, page, ce, pe = launch(pw, w, h, core_risk={"capTotalA": 25, "capTotalB": 25, "riskFirst": 0.8})
    +    b, page, ce, pe = launch(pw, w, h, core_risk={"winnerCap": 25, "riskFirst": 0.8})
    -        cfg = js(page, "()=>{ const c = coreRiskCfg('main'); return [c.capTotalA, c.capTotalB, c.riskFirst, c.riskAcc]; }")
    +        cfg = js(page, "()=>{ const c = coreRiskCfg('main'); return [c.winnerCap, c.winnerCap, c.riskFirst, c.riskAcc]; }")
    -        cr = js(page, "()=>{ const c = getBook('main').settings.coreRisk; return [c.capTotalA, c.capTotalB, c.riskFirst]; }")
    +        cr = js(page, "()=>{ const c = getBook('main').settings.coreRisk; return [c.winnerCap, c.winnerCap, c.riskFirst]; }")
    -          cap: (coreRiskCfg('main').capTotalA), lots: (document.querySelector('[data-core-card=ccNV] [data-c-lotbadge]')||{innerText:''}).innerText, l2: !!document.query
    -        check(f"{tag} 12 legacy เหมือนเดิม: การ์ดมีกริด 4 ช่อง + กล่องจำลองเติมไม้ · ไม่มีชั้น Base/เร่ง · เพดานต่อหุ้นค่าเริ่มเดิม 25 (ช่องที่ไม่เคยตั้ง) · มีกล่อง 4 ช่
    +          cap: (coreRiskCfg('main').winnerCap), lots: (document.querySelector('[data-core-card=ccNV] [data-c-lotbadge]')||{innerText:''}).innerText, l2: !!document.query
    +        check(f"{tag} 12 legacy เหมือนเดิม: การ์ดมีกริด 4 ช่อง + กล่องจำลองเติมไม้ · ไม่มีชั้น Base/เร่ง · เพดานต่อหุ้น 15 (ตรึงตามเทสเดิม) · มีกล่อง 4 ช่อง", lg["grid4"

## tests/run_tests_phase92.py

    -        names = js(page, "()=>[...document.querySelectorAll('[data-pv2-port]')].map(c=>({id: c.dataset.pv2Port, name: (c.querySelector('[data-pv2-name]')||{innerText:nul
    -        check(f"{tag} 6 Port โหมดรวม: การ์ดโครงพอร์ตแต่ละใบมีชื่อ+จุดสีบัญชีที่หัว (ไม่ซ้ำไม่มีชื่อ)", len(names) == 2 and [n["name"] for n in names] == ["บัญชีหลัก", "F
    +        # RG2b — การ์ดโครงพอร์ต (Core/Main/Tactical) ถูกแทนด้วยเส้นถังเส้นเดียว + แถบพับต่อบัญชี (data-pool-line)
    +        names = js(page, "()=>{ const l = document.querySelector('[data-pool-line]'); if(l) l.open = true; return [...document.querySelectorAll('[data-pool-line] [data-p
    +        check(f"{tag} 6 Port โหมดรวม: เส้นถังเส้นเดียว · แถบพับแยกต่อบัญชีมีชื่อ+จุดสี (ไม่ซ้ำไม่มีชื่อ)", js(page, "()=>document.querySelectorAll('[data-pool-line]').le
    -        cards = js(page, "()=>[...document.querySelectorAll('[data-pv2-port]')].map(c=>c.innerText.replace(/\\s+/g,' '))")
    -        check(f"{tag} 6 ตัวเลขในการ์ดไม่เปลี่ยน (รวม ฿ ของแต่ละบัญชีเท่าเดิม)", len(cards) == 2 and all(f"฿{r:,}" in n for r, n in zip(ref, cards)), [ref, cards])
    +        cards = js(page, "()=>[...document.querySelectorAll('[data-pool-line] [data-pool-acct]')].map(c=>c.innerText.replace(/\\s+/g,' '))")
    +        check(f"{tag} 6 ยอดบัญชีต่อบัญชีในเส้นถัง = ยอดรวมเดิม (฿ ของแต่ละบัญชีเท่าเดิม)", len(cards) == 2 and all(f"฿{r:,}" in n for r, n in zip(ref, cards)), [ref, car
    -        one = js(page, "()=>({n: document.querySelectorAll('[data-pv2-port]').length, names: document.querySelectorAll('[data-pv2-name]').length})")
    -        check(f"{tag} 6 เลือกบัญชีเดียว → การ์ดเดียว · หัวเหมือนเดิม (ไม่มีชื่อซ้ำ)", one["n"] == 1 and one["names"] == 0, one)
    +        one = js(page, "()=>({n: document.querySelectorAll('[data-pool-line] [data-pool-acct]').length, names: document.querySelectorAll('[data-pool-line] .poolAcctN').l
    +        check(f"{tag} 6 เลือกบัญชีเดียว → บล็อกเดียว · ไม่มีหัวชื่อซ้ำ", one["n"] == 1 and one["names"] == 0, one)

## tests/run_tests_phase96.py

    -        check(f"{tag} 3 บรรทัดสถานะฟอร์ม: '2% · <บัญชี> $x · <บัญชี> $y' แสดงทั้ง 2 บัญชี (ตรงสูตรเดิม) · ส่วนอื่นเดิม (ทิศ · Macro · ไม้ใหม่)", fm and fm["deals"] == ex
    +        check(f"{tag} 3 บรรทัดสถานะฟอร์ม: '2% · <บัญชี> $x · <บัญชี> $y' แสดงทั้ง 2 บัญชี (ตรงสูตรเดิม) · ส่วนอื่นเดิม (ทิศ · Macro · ไม้ใหม่)", fm and fm["deals"] == ex
    -        js(page, "()=>{ const bk = getBook('fam'); bk.settings.capital.satB = 0; saveBook('fam'); render(); satV3Render({force:true}); }"); settle(page, 500)
    +        js(page, "()=>{ const bk = getBook('fam'); bk.settings.capital.satB = 0; bk.settings.pools = {winner:62.5, ladder:37.5, sat:0, reviewed:true}; saveBook('fam');  
    -        check(f"{tag} 4 Risk Core: 1 กล่อง · 2 แถว (main, fam) พร้อมกัน · หัว Core = ทุนรวม ฿8.4M", info["ids"] == ["main", "fam"] and info["boxes"] == 1 and info["cap"]
    +        check(f"{tag} 4 Risk Core: 1 กล่อง · 2 แถว (main, fam) พร้อมกัน · หัว Core = ถัง Winner + Ladder รวม ฿9.6M", info["ids"] == ["main", "fam"] and info["boxes"] == 
    -              return {now: fmt2(rk.layer2Pct)+'%', lim: fmt2(cfg.l2Cap)+'%', free: Math.round(sp ? tank-cx.wCost-sp.lUsed : tank-cx.held), ff: Math.round(cx.F.f*100)+'%'
    -            got = js(page, """(A)=>{ const r = document.querySelector('[data-lf-row="'+A+'"]'); return {now: r.querySelector('[data-lf-now]').innerText.trim(), lim: r.qu
    +              return {now: fmt2(rk.layer2Pct)+'%', free: Math.round(sp ? (sp.cashFree + sp.lCashFree) : (tank - cx.held)), ff: Math.round(cx.F.f*100)+'%', dd: fmt2(Math.
    +            got = js(page, """(A)=>{ const r = document.querySelector('[data-lf-row="'+A+'"]'); return {now: r.querySelector('[data-lf-now]').innerText.trim(), free: +r.
    -                  ref and got["now"] == ref["now"] and got["lim"] == ref["lim"] and abs(got["free"] - ref["free"]) <= 1 and f"DD {ref['dd']}" in got["line"] and ref["ff"
    +                  ref and got["now"] == ref["now"] and abs(got["free"] - ref["free"]) <= 1 and f"DD {ref['dd']}" in got["line"] and ref["ff"] in got["line"], [ref, got])

## tests/run_tests_phase97.py

    -                page.locator("#hdrSub #scopeFuture").click(); settle(page, 400)
    +                page.locator("#scopeFuture").first.click()   # RG2b: <430 ปุ่มอยู่ในหน้า; settle(page, 400)
    -            check(f"{tag} 3 {k}: ซ่อนชื่อ Trading + ข้อความซิงก์ · โลโก้ + จุดซิงก์ยังเห็น · ตัวควบคุมอยู่ในช่อง (เต็มหรือย่อ) ไม่ล้นจอ",
    -                  not r["brandNameVis"] and not r["syncTimeVis"] and r["dotVis"] and (r["fullVis"] or r["cmpVis"]) and r["slot"]["r"] <= w and r["slot"]["r"] <= r["hb"][
    +            if k.startswith("plan") and w < 430:   # RG2b — 3 ปุ่ม Winner | Ladder | Sat ไม่พอที่ใน header จอ < 430px → อยู่ในหน้า (ชื่อแอปคงอยู่ · โลโก้ + จุดซิงก์เห็น)
    +                where_ = page.evaluate("()=>[...document.querySelectorAll('.scopeBtn')].map(b=>b.closest('.planScope') ? 'page' : 'hdr')")
    +                check(f"{tag} 3 {k}: RG2b ปุ่ม 3 ตัวอยู่ในหน้า (header ไม่พอ) · โลโก้ + จุดซิงก์ยังเห็น · ไม่ล้นจอ", r["dotVis"] and where_ == ["page", "page", "page"] a
    +            else:
    +                check(f"{tag} 3 {k}: ซ่อนชื่อ Trading + ข้อความซิงก์ · โลโก้ + จุดซิงก์ยังเห็น · ตัวควบคุมอยู่ในช่อง (เต็มหรือย่อ) ไม่ล้นจอ",
    +                      not r["brandNameVis"] and not r["syncTimeVis"] and r["dotVis"] and (r["fullVis"] or r["cmpVis"]) and r["slot"]["r"] <= w and r["slot"]["r"] <= r["h
    -        page.mouse.click(r["dot"]["l"] + r["dot"]["w"] / 2, r["dot"]["t"] + r["dot"]["h"] / 2); settle(page, 150)
    +        bs_ = js(page, "()=>{ const q = document.getElementById('brandSync').getBoundingClientRect(); return [q.left + q.width / 2, q.top + q.height / 2]; }")   # RG2b: 
    +        page.mouse.click(bs_[0], bs_[1]); settle(page, 150)
    -            page.locator("#hdrSub #scopeFuture").click()
    +            page.locator("#scopeFuture").first.click()   # RG2b: <430 ปุ่มอยู่ในหน้า
    -            check(f"{tag} 3 Plan 390: Core|Sat เต็มรูปพอดี (ไม่ย่อ)", rows["plan-stock"]["fullVis"] and not rows["plan-stock"]["slotCmp"], rows["plan-stock"])
    +            go(page, "plan", "stock")
    +            inpg = js(page, "()=>['scopeStock','scopeLadder','scopeFuture'].map(i=>{ const e = document.getElementById(i); const r = e && e.getBoundingClientRect(); retu
    +            check(f"{tag} 3 Plan 390 (RG2b): ปุ่ม Winner | Ladder | Sat เต็ม 3 ปุ่มอยู่ในหน้า (ไม่ย่อเป็น pill)", inpg == [True, True, True] and not rows["plan-stock"]["

## tests/run_tests_phase99.py

    -  const s = document.getElementById('hdrSub'), t = s && s.querySelector('.scopeTabs');
    +  const s = document.getElementById('hdrSub'), t = document.querySelector('.scopeTabs');   /* RG2b — ปุ่มอยู่ใน header (กว้างพอ) หรือในหน้า (header ไม่พอ) */
    -  return {inSlot: !!t, visible: vis(t), btns: bs.map(b => [b.textContent.trim(), vis(b), b.classList.contains('on'), R(b).w]), sel: [...s.querySelectorAll('select')].fil
    +  return {inSlot: !!(t && s.contains(t)), visible: vis(t), btns: bs.map(b => [b.textContent.trim(), vis(b), b.classList.contains('on'), R(b).w]), sel: [...s.querySelecto
    -        two = [x[0] for x in r["btns"]] == ["Core", "Sat"] and all(x[1] for x in r["btns"])
    -        check(f"{tag} 1 Plan ครั้งแรก: ปุ่ม Core | Sat มองเห็นทั้งสองปุ่ม ไม่มี <select>/pill ย่อ", r["inSlot"] and r["visible"] and two and r["sel"] == 0 and not r["cmp
    -        check(f"{tag} 1 มีปุ่ม active หนึ่งปุ่ม · ไม่ล้น/ไม่ตัด · ไม่ชน toolbar · หน้าไม่เลื่อนแนวนอน", not r["clip"] and r["ow"] <= 0 and (r["hb"] is None or r["tabs"][
    +        two = [x[0] for x in r["btns"]] == ["Winner", "Ladder", "Sat"] and all(x[1] for x in r["btns"])
    +        check(f"{tag} 1 Plan ครั้งแรก: ปุ่ม Winner | Ladder | Sat มองเห็นครบสามปุ่ม (ใน header หรือในหน้า) ไม่มี <select>/pill ย่อ", r["visible"] and two and r["sel"] ==
    +        check(f"{tag} 1 มีปุ่ม active หนึ่งปุ่ม · ไม่ล้น/ไม่ตัด · ไม่ชน toolbar · หน้าไม่เลื่อนแนวนอน", not r["clip"] and r["ow"] <= 0 and (r["hb"] is None or not r["inS
    -        check(f"{tag} 1 Core active หลังเลือก Core", rc["btns"][0][2] and not rc["btns"][1][2] and rc["scope"] == "stock", rc)
    -        page.locator("#hdrSub .scopeBtn", has_text="Sat").click(); settle(page, 500)
    +        check(f"{tag} 1 Core active หลังเลือก Core", rc["btns"][0][2] and not rc["btns"][2][2] and rc["scope"] == "stock", rc)
    +        page.locator(".scopeBtn", has_text="Sat").click(); settle(page, 500)
    -        check(f"{tag} 1 กด Sat → scope future + Sat active + ยังสองปุ่ม", r2["scope"] == "future" and r2["btns"][1][2] and not r2["btns"][0][2] and r2["sel"] == 0 and no
    +        check(f"{tag} 1 กด Sat → scope future + Sat active + ยังสามปุ่ม", r2["scope"] == "future" and r2["btns"][2][2] and not r2["btns"][0][2] and r2["sel"] == 0 and no
    -        check(f"{tag} 1 ไป-กลับแท็บ: ยังสองปุ่ม · จำ scope เดิม (Sat)", r3["visible"] and r3["sel"] == 0 and not r3["cmp"] and r3["btns"][1][2] and r3["scope"] == "futur
    -        page.locator("#hdrSub .scopeBtn", has_text="Core").click(); settle(page, 500)
    +        check(f"{tag} 1 ไป-กลับแท็บ: ยังสามปุ่ม · จำ scope เดิม (Sat)", r3["visible"] and r3["sel"] == 0 and not r3["cmp"] and r3["btns"][2][2] and r3["scope"] == "futur
    +        page.locator(".scopeBtn", has_text="Winner").click(); settle(page, 500)
    -                check(f"{tag} 1 ปรับความกว้าง {ww}px: ยังสองปุ่ม ไม่มี select ไม่ล้น", rr["visible"] and rr["sel"] == 0 and not rr["cmp"] and not rr["clip"] and rr["ow"]
    +                check(f"{tag} 1 ปรับความกว้าง {ww}px: ยังสามปุ่ม ไม่มี select ไม่ล้น", rr["visible"] and rr["sel"] == 0 and not rr["cmp"] and not rr["clip"] and rr["ow"]
    -        check(f"{tag} 1 render ซ้ำ: ยังสองปุ่ม", r5["visible"] and r5["sel"] == 0 and not r5["cmp"], r5)
    +        check(f"{tag} 1 render ซ้ำ: ยังสามปุ่ม", r5["visible"] and r5["sel"] == 0 and not r5["cmp"], r5)
    -        check(f"{tag} 1 Mac: Core | Sat สองปุ่มใน header เหมือนเดิม (สูง 38px · ไม่ย่อ)", r["visible"] and [x[0] for x in r["btns"]] == ["Core", "Sat"] and abs(r["tabs"]
    +        check(f"{tag} 1 Mac: Winner | Ladder | Sat สามปุ่ม (ใน header สูง 38px หรือในหน้า · ไม่ย่อ)", r["visible"] and [x[0] for x in r["btns"]] == ["Winner", "Ladder", 
