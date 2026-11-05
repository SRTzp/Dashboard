# 7E-4 — Mean Reversion (MR · เทรดสวน Bias สั้น ๆ ที่แนว) · เทส 27

> ส่งหลัง 7E-2a-fix (เทส 25) ตรวจผ่าน · ถ้า 7E-2b (เทส 26) ยังไม่มา ใช้เลข 27 ไว้ตามเดิม ไม่ต้องขยับ
> ผู้ใช้: "Trend = Bear · Macro = Bear · ราคาลงมาแนวรับ อยากเทรดสวนสั้น ๆ แต่กรอกแล้วเทรดไม่ได้" → **ไม่ปรับหน้าตาการ์ด Sat** · MR = เงื่อนไขชนิดหนึ่งในรายการเงื่อนไขของแผนเดิม
> สำรองก่อนแก้: `index.backup-pre-7E4.html` · **ห้ามแตะ** Core (core*/Calc.coreSize/core-size.js) · Flow · แถวหัว · Bias/Trend/Zone ของ Strategy สัปดาห์ (satWeek) ห้ามเปลี่ยนเพราะ MR
> เลขบรรทัดอ้างจากไฟล์หลัง 7E-2a (≈11,600 บรรทัด) — ใช้ชื่อฟังก์ชันเป็นหลัก

## 0. กติกา (ผู้ใช้ล็อกแล้ว)
| เรื่อง | กติกา |
|---|---|
| ชนิด | เงื่อนไข `kind:'mr'` ในแผน Sat เดิม (idea มี `conditions[]`) · แผนที่ Bias สัปดาห์ = Long/Short เท่านั้น |
| ทิศ | **ตรงข้าม Bias ของแผน** (Bias Short → MR Long ที่แนวรับ · Bias Long → MR Short ที่แนวต้าน) · `idea.bias` ไม่เปลี่ยน |
| แนว | เลือกจากแนวใน Strategy สัปดาห์นี้ (`satV3SupportDisplay` / `satV3ResistanceDisplay`) → เก็บ `cond.mr_level` |
| ระยะ Entry | \|Entry − แนว\| ÷ แนว ≤ **1%** ทุก asset (ค่าคงที่ตอนนี้ · ผู้ใช้จะตั้งต่อ asset ทีหลัง → ทำเป็น `satMrDistPct(asset)` คืน `SAT_MR_DIST_PCT = 1` จุดเดียว) |
| SL | ต้อง**เลยแนว**: MR Long → SL < แนว · MR Short → SL > แนว (และถูกฝั่งของ Entry ตามปกติ) |
| TP | **บังคับกรอก** · ต้องถูกฝั่ง (MR Long → TP > Entry · MR Short → TP < Entry) |
| ขนาด | **factor = `SAT_MACRO_CUT` (0.6) ตายตัว** ไม่คูณซ้ำกับกฎ F2c (ถ้ากฎ F2c = 0.6 อยู่แล้ว ก็ยัง 0.6 ไม่ใช่ 0.36) · ซ่อนสวิตช์ "ใช้ขนาดเต็ม" (size_full_override) เมื่อ MR |
| heat / โควตา | นับเหมือนไม้ปกติ (≤ 6% ถัง Sat · ไม้ใหม่ ≤ 2/สัปดาห์/บัญชี) |
| ถือนาน | เตือนเมื่อถือ **เกิน 2 วัน** นับจาก `openedAt` (ไม่มี → `date`) · วันทำการ (ใช้ `ffBizDaysSince`) · **BTCUSD นับวันปฏิทิน** · เตือนอย่างเดียว ไม่บังคับปิด |
| ป้าย | "MR · สวน Bias" ทุกที่ที่เห็นไม้/เงื่อนไขนี้ |

## 1. Calc (pure · ไม่แตะ core-size.js)
- `Calc.mrSide(bias)` → 'Long'↔'Short' (อื่น = null)
- `Calc.mrCheck({side, entry, sl, tp, level, distPct})` → `{ok, distPct: ระยะจริง %, reasons[]}` เหตุผล (ข้อความไทยตรงตัว):
  - ไม่มีแนว → "ยังไม่เลือกแนว MR"
  - ระยะ > distPct → "Entry ห่างแนว x.xx% (เกิน 1%)"
  - SL ไม่เลยแนว → "SL ต้องต่ำกว่าแนว 2,400" / "SL ต้องสูงกว่าแนว …"
  - ไม่มี TP → "MR ต้องกรอก TP" · TP ผิดฝั่ง → "TP ผิดฝั่ง"
- `Calc.mrHoldDays({openedAt, today, calendar})` → จำนวนวัน (ทำการ หรือ ปฏิทิน) · `> 2` = เตือน

## 2. ทิศที่ใช้จริงของแผน (จุดสำคัญที่สุด)
- เพิ่ม `satV3SideOf(idea)` = ข้อที่ Activate อยู่เป็น `kind:'mr'` → `Calc.mrSide(idea.bias)` · ไม่ใช่ → `idea.bias`
- **grep ทุก `idea.bias` ในโฟลว์ satV3** แล้วแยก 2 ความหมาย:
  - "ทิศของไม้ที่จะเข้า" → ใช้ `satV3SideOf(idea)`: `satV3PlanAcctCalc` (side) · `satV3SaveSlot` (bias ของไม้) · `satV3TpNear(…, bias)` ทุกจุด (ขอบใกล้ TP zone ขึ้นกับทิศไม้) · `satV3F2c` (side ที่ใช้ pbAlign/sizeRule/shift) · ป้ายทิศในการ์ดขั้นหน้างาน · `Calc.rr`
  - "ทิศของแผน/สัปดาห์" → คง `idea.bias`: `sat7dIdeaFlags` (offBias) · หัวแถวรอเงื่อนไข · Trend Shift tag · `zones` แนวของแผนปกติ
  - รายงานกลับเป็นตาราง: จุดไหนเปลี่ยน/ไม่เปลี่ยน + เหตุผล
- สลับ Activate ระหว่างข้อที่ทิศต่างกัน (ปกติ ↔ MR) → ล้าง `entry` / `sl` (ค่าเดิมจะผิดฝั่ง) · TP ใช้กติกา default เดิม
- ไอเดียเก่าแบบ 7D.2 (ไม่มี conditions) + `sat7dSideOk` → ไม่แตะ

## 3. UI (ในโครงเดิม · ไม่ปรับหน้าตาการ์ด)
- ขั้นวางแผน: แถวปุ่มลัดเงื่อนไข เพิ่มปุ่ม **`＋ MR สวน Bias`** (แยกจากรายการปุ่มลัดที่ผู้ใช้ตั้งเอง · ไม่เขียน satConfig) → เพิ่มเงื่อนไข `{kind:'mr', text:'MR ที่แนว ', mr_level:null, …}`
  - แถวเงื่อนไข MR: ป้าย "MR · สวน Bias" + ชิปเลือกแนว (แนวรับถ้า Bias Short · แนวต้านถ้า Bias Long · จาก Strategy สัปดาห์นี้) → เลือกแล้วเขียน `mr_level` · ไม่มีแนวใน Strategy → "ยังไม่มีแนวรับ/ต้านใน Strategy สัปดาห์นี้" + ปุ่ม Activate กดไม่ได้
  - TP zone / inval ใช้ช่องเดิมของเงื่อนไข
- ขั้นหน้างาน (Activate ข้อ MR):
  - ป้ายทิศ = ทิศ MR (เช่น Long) + ป้าย "MR · สวน Bias" + บรรทัด "แนว 2,400 · Entry ต้องอยู่ 2,376–2,424 · SL ต่ำกว่า 2,400 · TP บังคับ"
  - ขนาด: แสดง "MR · ลด 40% (ตายตัว)" แทนบรรทัดกฎ F2c · ไม่มีสวิตช์ขนาดเต็ม
  - บัญชี: `mrCheck` ไม่ผ่าน → บัญชีไม่ ready + เหตุผลจาก mrCheck ต่อท้าย `warns` (ห้ามแก้ `Calc.readiness` เดิม — ต่อท้ายใน satV3PlanAcctCalc)
- ไม้ที่บันทึก (`satV3SaveSlot` → makeTradeObject): `bias` = ทิศ MR · `sizeFactor: 0.6` · field ใหม่ `mr: true`, `mr_level`, `plan_bias: idea.bias` · field F2c เดิมบันทึกตามปกติ (side = ทิศ MR)
- แสดงไม้ MR: Positions (แถว + การ์ดมือถือ) · การ์ดไม้ Sat ที่เปิดอยู่ · Journal → ป้าย "MR · สวน Bias" · `satV3F2cTradeLine`: ไม้ mr → "MR · ลด 40%" แทน "ลด/เต็ม"
- เตือนถือนาน: ไม้ satB `mr:true` status open ถือ > 2 วัน → "⚠ MR ถือ n วัน (เกิน 2)" ใน Positions + การ์ดไม้ Sat · ไม่มี openedAt/date → ไม่เตือน

## 4. เทส `tests/run_tests_phase27.py` (Chromium · 1440 + 430)
ข้อมูล: XAUUSD สัปดาห์นี้ Bias **Short** · Trend down · แนวรับ **2,400** · แนวต้าน 2,520 · Macro Bear · บัญชี main โบรก XM (ใช้ค่าตั้งในข้อมูลทดสอบเดิม)
1. Calc.mrSide: Short→Long · Long→Short · None→null
2. Calc.mrCheck Long แนว 2,400 dist 1: Entry 2,410 / SL 2,390 / TP 2,450 → ok (ระยะ 0.42%) · Entry 2,430 → "Entry ห่างแนว 1.25% (เกิน 1%)" · Entry 2,376 → ok (ขอบพอดี 1.00% · เทียบด้วย epsilon 1e-9) · SL 2,405 → "SL ต้องต่ำกว่าแนว 2,400" · TP ว่าง → "MR ต้องกรอก TP" · TP 2,400 (< Entry) → "TP ผิดฝั่ง" · ไม่มีแนว → "ยังไม่เลือกแนว MR"
3. mrCheck Short (Bias Long · แนวต้าน 2,520): Entry 2,510 / SL 2,530 / TP 2,470 → ok · SL 2,515 → "SL ต้องสูงกว่าแนว 2,520"
4. Calc.mrHoldDays: เปิดวันศุกร์ → วันจันทร์ = 1 วันทำการ · วันพุธ = 3 → เตือน · BTCUSD เปิดศุกร์ → จันทร์ = 3 วันปฏิทิน → เตือน
5. ปุ่ม `＋ MR สวน Bias` สร้างเงื่อนไข kind mr · ชิปแนวแสดงแนวรับ (Bias Short) · เลือก 2,400 → mr_level = 2400 · ไม่มีแนว → Activate กดไม่ได้
6. Activate MR → ป้ายทิศ Long + "MR · สวน Bias" · idea.bias ยัง Short · satWeek ไม่ถูกเขียน
7. กรอก 2,410 / 2,390 / 2,450 → บัญชี ready · lot = `Calc.satLot` ด้วย riskAmount × **0.6** (เทียบค่าตรง) · กรณีกฎ F2c ของ Long เป็น 0.6 อยู่แล้ว → ยัง 0.6 (ไม่ใช่ 0.36) · ไม่มีสวิตช์ขนาดเต็ม
8. Entry 2,430 → บัญชีไม่ ready + เหตุผล "Entry ห่างแนว 1.25% (เกิน 1%)" · TP ว่าง → ไม่ ready
9. บันทึก order → ไม้ bias Long · mr true · mr_level 2400 · plan_bias Short · sizeFactor 0.6 · heat/โควตานับตามปกติ (โควตาเต็ม 2 → MR ก็ไม่ ready)
10. สลับ Activate จาก MR → เงื่อนไขปกติ: entry/sl ถูกล้าง · ทิศกลับเป็น Short · ขนาดกลับตามกฎ F2c
11. TP default จาก TP zone ของข้อ MR = ขอบใกล้ตามทิศ **Long** (min)
12. Positions / Journal / การ์ดไม้ Sat มีป้าย "MR · สวน Bias" · ไม้ MR เปิด 3 วันทำการ → "⚠ MR ถือ 3 วัน (เกิน 2)" · 2 วัน → ไม่เตือน · ไม้ปกติไม่เตือน
13. แผนปกติ (ไม่มี MR) ทุกตัวเลขเท่าเดิม (เทียบ phase เดิมของ Sat ผ่านครบ)
14. 430px ไม่ล้นแนวนอน
- ภาพ `tests/screenshots/7e4-*`: cond-mr (ขั้นวางแผน) · active-mr-ok · active-mr-far · positions-mr · hold-warn (1440 + 430)

## 5. เทสเก่า
- เคสเดิมทุกชุดต้องผ่าน · ถ้ากระทบ บันทึกใน `tests/7E4_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล) · ห้ามลบเคส
- รันครบ: `check_syntax` · `sync_core_size --check` · run_tests + phase 1–27 ที่มีอยู่

## 6. รายงานกลับ
ตารางจำนวนเคสก่อน→หลัง · ตาราง `idea.bias` ที่เปลี่ยน/ไม่เปลี่ยน (§2) · field ใหม่ของไม้/เงื่อนไข · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
