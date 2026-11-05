# CZ1 — ขนาดไม้ Core ตาม Tier: Risk/ไม้ · เพดานไม้แรก · เพดานรวม/หุ้น แยก A / B (core-size.js + ตั้งค่า) · เทส 65

> ผู้ใช้ตัดสิน 11 ต.ค. · ทำหลัง UX2 · ม็อกอัป `docs/mockups/ux2-mockup-v2.html` ส่วน ③ (sha256 ca64fd27…)
> สำรองก่อนแก้: `index.backup-pre-CZ1.html` · `core-size.backup-pre-CZ1.js` · `tests/_bk_cz1/` · **รอบนี้แก้ core-size.js ได้** แล้ว sync สำเนาใน index.html ด้วย `tools/sync_core_size.py`
> ห้ามย้อนงานรอบก่อน (DD1 ลดขนาด/ฟื้นตัว · TIER2 เกณฑ์ · UX2 การ์ดแผน · บันได L)
> ไฟล์ชั่วคราวที่สร้างเองให้ย้ายไป `_to_delete/` ห้าม rm
> เป้า Dashboard ข้อ 2: ขนาดไม้คิดตาม Tier ตรงกติกา · ลดการคำนวณเองตอนเข้าไม้

## ข้อตัดสิน
| ค่า (ต่อบัญชี · % ของถัง Core) | A ค่าเริ่ม | B ค่าเริ่ม | ใช้กับ |
|---|---|---|---|
| Risk/ไม้ | 1.25 | 1.25 | firstLot + addLot (× FF · × DD factor เหมือนเดิม) |
| เพดานไม้แรก | 15 | 10 | firstLot (เดิม `tierA`/`tierB`) |
| เพดานรวม/หุ้น | 25 | 25 | firstLot + addLot (ใหม่) |
- **คงค่าที่ผู้ใช้ตั้งไว้เดิม:** ค่าเริ่มใหม่ใช้เฉพาะเมื่อไม่มีค่าที่บันทึก
  - Risk/ไม้ A/B ไม่มีค่าที่บันทึก → ใช้ `coreRisk.riskPct` เดิมของบัญชีนั้น (ถ้ามี) · ไม่มีอีก → 1.25
  - เพดานไม้แรก = ใช้ `tierA` / `tierB` เดิม (มีค่าที่บันทึก → คงไว้ · ไม่มี → 15 / 10 ใหม่)
  - ไม่เขียนกลับตอนอ่าน (กติกา 7E-1 เดิม) · บันทึกเมื่อกดบันทึกตั้งค่าเท่านั้น
- เพดานรวม/หุ้น คิดจาก **ทุน (cost basis)**: `ถือ × ทุนเฉลี่ย + ไม้ใหม่ × ราคา ≤ ถัง × เพดานรวม` · ไม่ใช้ราคาตลาด
- บันได L (Tier A) ไม่เกี่ยว — ใช้ค่า L เดิม (`ladderBudget` · `ladderRisk` · `ladderShare`)
- Tier ที่ใช้ = Tier ของการ์ด (`c.tier` · A หรือ B เหมือนเดิม)

## 1. core-size.js
- `DEFAULTS.tierCap` → `{A:0.15, B:0.10}` · เพิ่ม `DEFAULTS.tierRisk:{A:0.0125, B:0.0125}` · `DEFAULTS.stockCap:{A:0.25, B:0.25}`
- `firstLot(o)`: รับ `o.stockCapPct` (ไม่ส่ง = `DEFAULTS.stockCap[tier]`) · `byStock = tank × stockCapPct / e` · `base = min(byRisk, byCap, byStock)` · ผลเพิ่ม `byStock` · `stockCapped` (true เมื่อ byStock คุม) · `riskPct` ยังรับจาก `o.riskPct` เหมือนเดิม (ผู้เรียกส่งค่าตาม Tier)
- `addLot(o)`: รับ `o.stockCapPct` (ไม่ส่ง = ไม่จำกัด → **เคสเก่าใน core_size_test ต้องได้ผลเท่าเดิม**) · `byStock = max(0, tank × stockCapPct − heldQty × avgCost) / px` · `m = min(target, byRisk, byStock)` · tag ใหม่ `stock_capped` เมื่อ byStock คุมและ qty > 0 · qty = 0 เพราะเพดานรวม → tag `stock_full`
- ฟังก์ชันอื่นไม่แตะ
- `tests/core_size_test.js`: เพิ่มเคส (เดิม 420 ต้องผ่านครบ ไม่แก้ความคาดหวังเดิม — ถ้าเคสเดิมพึ่ง `DEFAULTS.tierCap` ค่าเก่า ให้ส่ง `tierCapPct` ตรงในเคสนั้นแทน และจด retired):
  - firstLot: tank 100k · e 100 · s 99 (byRisk สูงมาก) · tierCap 0.30 · stockCap 0.25 → qty 250 · `stockCapped:true`
  - addLot: ถือ 200 @ 100 · tank 100k · stockCap 0.25 · px 110 → byStock = (25,000 − 20,000)/110 = 45.45 → qty ≤ 45 · tag `stock_capped` (ถ้าน้อยกว่า target/byRisk)
  - addLot: ถือ 250 @ 100 · stockCap 0.25 → qty 0 · tag `stock_full`
  - addLot ไม่ส่ง stockCapPct → ผลเท่าเดิมทุก field
  - DEFAULTS ใหม่: firstLot ไม่ส่ง tierCapPct tier B → ใช้ 0.10

## 2. index.html
- `CORE_RISK_DEFAULTS`: `tierA:15` · `tierB:10` · เพิ่ม `riskA` · `riskB` (ค่าเริ่มตามกติกาข้างบน — ต้อง fallback ไป `riskPct` ที่บันทึกไว้ จึงตั้งใน `coreRiskCfg` ไม่ใช่ค่าคงที่ตายตัว) · `capTotalA:25` · `capTotalB:25`
- `coreSizeOpts`: เพิ่ม `tierRisk:{A,B}` (× DD factor เหมือน `riskPct` เดิม) · `tierRiskBase:{A,B}` · `stockCap:{A,B}` · คง `riskPct` / `riskPctBase` เดิมไว้ (= ค่าของ Tier A) เพื่อที่อื่นที่ยังอ่าน
- `coreFirstLotCalc` ส่ง `riskPct: cx.opts.tierRisk[tier]` · `stockCapPct: cx.opts.stockCap[tier]`
- เรียก `addLot` (จุดเดียวที่ ~บรรทัด 7284 + จุดอื่นถ้ามี) ส่ง `riskPct` ตาม Tier ของการ์ด (base ไม่คูณ DD ตามกติกาเดิม) + `stockCapPct`
- ข้อความ/ป้ายใหม่: firstLot `stockCapped` → ป้าย `ชนเพดานรวม/หุ้น` · addLot `stock_capped` → `ชนเพดานรวม/หุ้น (x%)` · `stock_full` → ปุ่มเติมไม้ปิด + title `ถือครบเพดานรวม/หุ้น x% แล้ว` · ใน `วิธีคิด` (UX2) เพิ่มบรรทัด `เพดานรวม/หุ้น x% = $…`
- การ์ดแผน (UX2 ข้อ 7): `FF x% · เพดานไม้แรก y%` ใช้ค่าตาม Tier ใหม่ · sheet Tier (`coreTiPick`) `เพดาน x%` อ่านค่าใหม่

## 3. ตั้งค่า (ส่วนความเสี่ยง Core เดิม)
- แทน 3 ช่องเดิม `งบเสี่ยงต่อตัว` · `เพดานไม้แรก Tier A` · `เพดานไม้แรก Tier B` ด้วย **ตาราง 2 แถว × 3 คอลัมน์** ตามม็อกอัป: หัว `Risk/ไม้` · `เพดานไม้แรก` · `เพดานรวม/หุ้น` · แถว `A` · `B` · หน่วย % ของถัง Core · ช่อง font ≥ 16px · ใต้ตารางบรรทัดสูตรสีจาง (ตามม็อกอัป · ใช้ `FF`)
- id ช่อง: `sCrRiskA` `sCrRiskB` `sCrTierA` `sCrTierB` (คง id เดิม) `sCrCapTotA` `sCrCapTotB` · ลบช่อง `sCrRisk` ออกจาก UI แต่ **ไม่ลบค่า `riskPct` ที่บันทึกไว้** (ยังเป็น fallback) · ตอนบันทึก เขียน `riskPct` = ค่า Risk A (ให้ค่าเดิมสอดคล้อง)
- ตรวจค่า (`crOnInput` เดิม): Risk 0.1–5 · เพดานไม้แรก 1–50 · เพดานรวม 1–100 และ **≥ เพดานไม้แรกของแถวเดียวกัน** (ไม่ผ่าน = ข้อความแดงใต้ช่อง · ปุ่มบันทึกปิดเหมือนกติกาเดิม)
- ภาษา: คำทับศัพท์ใช้ English ตามม็อกอัป (`Risk/ไม้`) · คำไทยอื่นคงไว้
- 390px: ตารางไม่ล้นแนวนอน · ช่อง ≥ 44px กว้างพอพิมพ์ `1.25`

## เทส `tests/run_tests_phase65.py` (Chromium · 1440 + 390 · mock Firestore)
1. บัญชีไม่มี coreRisk → ตารางแสดง A 1.25/15/25 · B 1.25/10/25
2. บัญชีที่บันทึก `riskPct:1.25, tierA:12` (แบบผู้ใช้จริง) → A Risk 1.25 · เพดานไม้แรก A **12** (คงเดิม) · B เพดานไม้แรก 10 (ไม่เคยตั้ง → ค่าใหม่) · เปิดอ่านแล้ว Firestore ไม่ถูกเขียน
3. บันทึก A Risk 1.5 / B Risk 1.0 → การ์ดแผน Tier A กับ B ราคาเดียวกัน ได้จำนวนหุ้นตามสูตร (เทียบ `Calc.coreSize.firstLot` ตรง) · `riskPct` ที่เก็บ = 1.5
4. เพดานรวม < เพดานไม้แรก → error · บันทึกไม่ได้
5. firstLot ชนเพดานรวม (เพดานไม้แรก 30 · รวม 25 · Stop แคบ) → ป้าย `ชนเพดานรวม/หุ้น` · จำนวนหุ้น = 25% ของถัง ÷ ราคา (ปัดตามตลาด)
6. เติมไม้: ถือใกล้เพดานรวม → จำนวนเติมถูกจำกัด + ป้าย · ถือเต็ม → ปุ่มเติมไม้ปิด + title
7. DD ลดขนาด (×0.5) → Risk ตาม Tier × 0.5 ทั้ง A และ B (firstLot) · ไม้เติมใช้ base เหมือนเดิม
8. บันได L / ชั้น 2 / gate FF ผลเท่าเดิม (เทียบกับ `index.backup-pre-CZ1.html` บน fixture เดียวกัน)
9. 390px: ตารางตั้งค่าไม่ล้น · ไม่มี console error
- ภาพ `tests/screenshots/cz1-*` (1440 + 390): `settings` · `settings-err` · `core-plan-capped` · `add-capped`

### เทสเก่า
- เคสที่อ่านช่อง `sCrRisk` หรือพึ่งค่าเริ่ม `tierA:10`/`tierB:5` (p17–p26 · p30 · p36 · p53 ฯลฯ) → seed ค่าเดิมใน fixture (`coreRisk:{riskPct:1, tierA:10, tierB:5}`) ให้ผลเท่าเดิม หรือใช้ช่องใหม่ · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/CZ1_retired.md`
- อัปเดต `ไฟล์ที่ห้ามลบ.md` (สำรอง CZ1 ทั้ง 2 ไฟล์ + `tests/_bk_cz1/`)
- รันครบ **ทีละชุด**: `core_size_test` (420 → ใหม่) · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–65

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ฟังก์ชันที่แก้ (core-size.js + index) · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
