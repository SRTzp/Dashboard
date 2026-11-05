# MF1 — Macro Playbook v2: Asset ไม่จำกัด 4 ตัว + ★ น่าสนใจ + `＋ วางแผน` จากแท็บ Flow + Link Asset · เทส 68

> ผู้ใช้ตัดสิน 15 ต.ค. — **Macro เป็นจุดเริ่ม ไม่ fix Asset:** ดู Macro → Asset ไหนน่าสนใจ → วางแผนสัปดาห์นั้น (หรือเจอ Chart สวย → เช็กกลับ Macro) · แทน SW1 (ยกเลิก) · คิว MF1 → WA1 → PY2 → CO1
> ม็อกอัป `docs/mockups/mf1-mockup.html` ส่วน ① · สำรองก่อนแก้: `index.backup-pre-MF1.html` · `tests/_bk_mf1/` · ห้ามแตะ core-size.js · ห้ามย้อนงานรอบก่อน (F2b/F2c Playbook เดิม · AS1 · ESC1)
> ไฟล์ชั่วคราวที่สร้างเองให้ย้ายไป `_to_delete/` ห้าม rm
> **ชุดที่เกี่ยวข้อง (รันระหว่างทำ):** phase68 (ใหม่) · ชุด Playbook/Flow เดิม (หาด้วย grep `macroPlaybook|pbPanel|pbValidate` ใน tests) · p55 (AS1) · p51 · p3–p7 (Macro ในการ์ด Sat) · ID2 (p45 ลิงก์ Playbook จาก Candidates)
> เป้า Dashboard ข้อ 1+2: เริ่มวางแผนจากภาพ Macro · เห็นทันทีว่า Asset ไหนตาม/สวน Macro

## ข้อตัดสิน
- **schema ใหม่ `macroPlaybook/v2`** (v1 ยังรับได้ · อ่านเหมือนเดิม):
  - `assets` = **Asset กี่ตัวก็ได้ (≥ 1)** · key = A–Z 0–9 2–12 ตัว (เช่น `XAUUSD` `XAG` `BTC` `BRENT` `US` `USDJPY` `S50`) · ไม่บังคับครบ 4 ตัวเดิม
  - ต่อ Asset: ช่องเดิมทั้งหมด (`stance` · `why` · `change_if` · `drivers` · `confidence` · `posture` · `if_alt` · `doc_url`) + **`focus: true|false`** (★ Macro ชี้ว่าน่าสนใจตอนนี้) + `label` (ชื่อแสดง ไม่บังคับ)
  - กติกาตรวจเดิมใช้ต่อ (why/change_if บังคับเมื่อ stance ≠ none · drivers ต้องมีจริง · ท่าทีผสมควรมี posture)
  - `view.watch` ยาวได้ ≤ 200 ตัวอักษร (เดิม 140)
- `Calc.pbEffective(versions, asset, atTime)` รองรับ Asset ใดก็ได้ · Asset ที่ไม่มีในเวอร์ชันนั้น = `none`
- **จับคู่ Sat Asset ↔ Playbook Asset:** ฟังก์ชันกลาง `satPbKeyOf(satKey)` = (1) ที่ผู้ใช้ตั้ง `satPbLink[satKey]` (2) alias ในตัว: `BTCUSD`/`BTCUSDT` → `BTC` (3) key ตรงกัน (`XAUUSD`, `XAG`, `BRENT`, `S50`…) (4) ไม่มี = null · **แทนการอ่าน `SAT_PB_ASSET[...]` / `IDEA_ASSET_PB[...]` ตรงทุกจุด**
- **Link Asset ที่แถว Asset ในการ์ด Playbook:** ถ้าจับคู่อัตโนมัติไม่ได้ หรืออยากผูกตัวอื่น → แตะ `⋯` ที่แถว → `ใช้กับ Sat: [XAG ▾]` (เลือก Sat Asset · 1 Sat Asset ผูกได้ 1 Playbook Asset · ย้ายอัตโนมัติ + ข้อความ `ย้าย XAG จาก …`) · เก็บ `satPbLink` (settings ของ `acctList[0]`)

## 1. หน้าตา แท็บ Flow › Macro (ตามม็อกอัป ①)
- การ์ด Playbook: หัว quarter · version · วันที่ · Thesis · Pillars (เดิม) · **รายการ Asset ทั้งหมด** เรียง: ★ ก่อน → ▲/▼ เต็ม → ▲▬/▼▬ → ▬ → none · แถว: ไอคอนท่าที (▲ เขียว ▼ แดง ▬ เทา) · ชื่อ (★ นำหน้าถ้า focus) · why ตัด `…` · ปุ่มขวา
  - ปุ่มขวา: `＋ วางแผน` (ยังไม่อยู่ใน Strategy สัปดาห์นี้) · `✓ สัปดาห์นี้` (อยู่แล้ว · แตะ = ไปการ์ดใน Strategy) · `US` = ป้าย `หุ้น Core` (ไม่มีปุ่ม)
  - แตะแถว = กางรายละเอียดเดิม (why เต็ม · change_if · posture · drivers · ความมั่นใจ · อ่านเต็ม)
- `＋ วางแผน` → เรียก `satWeekPickAdd(satKey)` ของ WA1 (รอบนี้ทำแค่ฟังก์ชันเพิ่มเข้า `satWeekPick[สัปดาห์นี้]` + ไปแท็บ แผน · หน้าตา Strategy ทำใน WA1):
  - Sat Asset มีอยู่แล้ว (4 ตัวเดิม/เพิ่มเอง) → เพิ่มเข้าสัปดาห์นี้ (ถ้าครบ 3 แล้ว → ข้อความ `สัปดาห์นี้ครบ 3 ตัวแล้ว — เอาตัวอื่นออกก่อน`)
  - ยังไม่มีใน Sat → เปิด sheet เพิ่มสินค้า (AS1) เติม key/label ให้ · บันทึกแล้วเพิ่มเข้าสัปดาห์นี้
- แถบดำ / ช่อง Macro ที่เดิมแสดง 4 Asset → แสดง Asset ที่ ★ (สูงสุด 4 · ไม่มี ★ = 4 ตัวแรกตามลำดับ)
- เอกสาร `docs/macro-playbook-schema.md` อัปเดตเป็น v2 (ตัวอย่าง JSON ใหม่ · ระบุว่า v1 ยังรับได้)

## 2. ที่เก็บ
- เวอร์ชัน Playbook: ที่เดิม (`macroPlaybook` · create เท่านั้น) · `stanceChanges` คิดเฉพาะ Asset ที่มีทั้ง 2 เวอร์ชัน + Asset ใหม่ (`from:'none'`) + Asset ที่หายไป (`to:'none'`)
- `satWeekPick: {'2026-10-11':['XAUUSD','XAG'], …}` (settings ของ `acctList[0]` · ≤ 3 ต่อสัปดาห์ · เก็บ 12 สัปดาห์ล่าสุด) — สร้างฟังก์ชัน `satWeekPickList(wk)` · `satWeekPickAdd(key, wk?)` · `satWeekPickRemove(key, wk?)` ในรอบนี้ (WA1 ใช้ต่อ)
- `satPbLink: {satKey: pbKey | 'none'}`

## เทส `tests/run_tests_phase68.py` (Chromium · 1440 + 390 · mock Firestore)
1. วาง JSON v2 ที่มี 6 Asset (XAUUSD★ · XAG★ · BTC · USDJPY · BRENT · US) → ตรวจผ่าน · บันทึกได้ · การ์ดแสดง 6 แถว เรียง ★ ก่อน · สีท่าทีถูก
2. JSON v1 เดิม (4 Asset) → ยังผ่าน แสดงเหมือนเดิม · v2 ที่ไม่มี XAUUSD → ผ่าน (ไม่บังคับ 4 ตัว) · key ผิดรูป / stance ผิด / ไม่มี why → error
3. `stanceChanges`: v1 → v2 เพิ่ม XAG → `XAG:{from:'none',to:'up'}` · ตัด BRENT → `BRENT:{to:'none'}`
4. `satPbKeyOf`: BTCUSD → BTC · XAG (เพิ่มเองใน Sat) → XAG · S50 ไม่มีใน Playbook → null · ตั้ง link NVDA→US → US · static: ไม่เหลือการอ่าน `SAT_PB_ASSET[` / `IDEA_ASSET_PB[` ตรงนอกฟังก์ชันนี้
5. การ์ด Sat XAG (มีอยู่แล้ว) แสดง Macro ของ XAG ใน Playbook v2 · F2c ใช้ท่าทีนี้
6. `＋ วางแผน` XAG (มีใน Sat) → `satWeekPick[สัปดาห์นี้]` มี XAG · ปุ่มเป็น `✓ สัปดาห์นี้` · ไปแท็บ แผน · ครบ 3 → ข้อความเต็ม · USDJPY (ไม่มีใน Sat) → sheet เพิ่มสินค้าเติม key ให้ → บันทึก → อยู่ในสัปดาห์นี้
7. Link ที่แถว: ผูก Sat `GOLD2` → Playbook XAUUSD → การ์ด Sat GOLD2 ใช้ท่าที XAUUSD · ผูกซ้ำที่อื่น → ย้าย + ข้อความ
8. แถบดำแสดง Asset ★ (≤ 4)
9. 390px: แถว Asset บรรทัดเดียว (why ตัด …) · ปุ่มไม่ล้น · ไม่มี console error
- ภาพ `tests/screenshots/mf1-*` (1440 + 390): `flow-v2` · `row-open` · `link` · `add-new-asset`

### เทสเก่า
- ชุด Playbook (F2b/F2c) ที่คาด "ต้องครบ 4 Asset" / watch ≤ 140 / อ่าน `SAT_PB_ASSET` → แก้ความคาดหวังตามกติกาใหม่ · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/MF1_retired.md`
- อัปเดต `ไฟล์ที่ห้ามลบ.md`

## รายงานกลับ (ต่อด้วย WA1 ทันที)
จำนวนเคสชุดที่เกี่ยวข้อง · ฟังก์ชันใหม่/ที่แก้ · จุดที่เปลี่ยนเป็น satPbKeyOf · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
