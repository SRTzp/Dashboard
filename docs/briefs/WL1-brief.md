# WL1 — Watchlist Overview ใหม่ (Catalysts · Blockers · Tripwire · โน้ตของฉัน · เอา FQC ออก) + เก็บงานเล็ก · เทส 35

> ผู้ใช้ 1 ต.ค.: ม็อกอัป `docs/mockups/wl-overview-mockup.html` = **ok** · **เอา FQC ออกจาก dashboard เลย — ใช้ Tier แทน** (รวมชิป "เกณฑ์ลงทุนเดิม" ที่อิง FQC) · ข้อมูลใน Firestore ไม่แตะ
> สำรองก่อนแก้: `index.backup-pre-WL1.html` · `research-card.backup-pre-WL1.js` · **ห้ามแตะ** core-size.js · Core/Sat · schema `research-card/1.0` (ฟิลด์/จำนวนสูงสุด/validate/merge) · `research_card.py` · ข้อมูล `fqc` / `investment_clearance` ใน Firestore (ไม่ลบ ไม่เขียนทับ · แค่โค้ดไม่อ่านแล้ว) · `import_pine.py` / สคริปต์ฝั่ง Research
> ใช้ชื่อฟังก์ชันเป็นหลัก (เลขบรรทัดอ้างจากไฟล์หลัง SR1 · 1,041,514 bytes)

## A. Overview ใหม่ (`wlDetailHtml` ส่วน `wlSub==='ov'` ~7797)
ลำดับบนลงล่างตามม็อกอัป · แหล่งข้อมูล = `d.research_card` (Research doc) + watchlist item (`r.item` / `w`)
1. **แถวชิป** (`.wlOvChips`): Industry (`wlIndChip` เดิม) · `Research {as_of} · {n} วัน` (n = วันนับจาก as_of ถึง `thaiToday()` · ไม่มีการ์ด = ชิปเหลือง `รอสร้าง Research Card`) · ชิปสถานะเดิม `wlActionChip` (ถ้ามี) · **ไม่มี FQC** · ชิป Tier อยู่ที่หัวรายละเอียดแล้ว (WT1) — ไม่ซ้ำในแถวนี้
   - `wlScoreChips` ฝั่ง core: ตัดชิป FQC และชิป "Research Card" สีเขียวออก · ฝั่ง candidate (`mode_a`) คงเดิม
   - ตัดบรรทัด "ต้องทำ: …" (`.wlTodo`) — แทนด้วยชิปเหลืองข้างบนเมื่อไม่มีการ์ด
2. **แถบเตือน** `data-wl-alert`: แสดง**เฉพาะ**เมื่อ tripwire ใด `status` = `check` (เหลือง) หรือ `confirmed` (แดง) · ข้อความ `⚠ ต้องตรวจ: Tripwire "{text}" มีข่าวเข้าเงื่อนไข — เปิดแท็บ Research` (confirmed = `⛔ Tripwire "{text}" ยืนยันแล้ว — ทบทวนการถือ`) · กดแล้วไปแท็บ Research · ไม่มี = ไม่มีแถบ
3. **ธุรกิจ**: `business.sells` (ไม่มีการ์ด → `wlLine2` เดิม) · ตัดป้าย "Business" ซ้าย ให้เป็นย่อหน้าอ่านง่าย (ฟอนต์ใหญ่กว่าบรรทัดอื่นเล็กน้อย)
4. **▲ สิ่งที่รอ (Catalysts)** `data-wl-sec="cat"`: จาก `research_card.catalysts` เรียงวันใกล้ก่อน (วันผ่านไปแล้วซ่อน) + โน้ตของฉันฝั่ง catalyst
   - ชิปวันที่ซ้าย: รูปแบบไทยสั้น `11 ธ.ค.` · `date_status==='estimated'` = `~11 ธ.ค.` กรอบเส้นประ · โน้ตไม่มีวัน = `—`
   - หัวข้อขวามีปุ่ม `＋ โน้ต`
5. **▼ สิ่งที่ต้องระวัง (Blockers)** `data-wl-sec="blk"`: `severe_risks` 3 ข้อแรก (จุดแดง) + โน้ตของฉันฝั่ง blocker (ทั้งหมด) · เกิน 3 → `+ อีก n ข้อในแท็บ Research` · ปุ่ม `＋ โน้ต`
6. **◎ Tripwire · ถ้าเกิด → ทบทวนการถือ** `data-wl-sec="tw"`: ทุก tripwire (≤ 2) · ไอคอน 🟢 watching (หรือไม่มี status) · 🟡 check · 🔴 confirmed · บรรทัดแรก `text` · บรรทัดสอง `ตอนนี้ {current_value}` (ตัวหนาเฉพาะค่า) · threshold ใส่ใน title/tooltip
7. **ท้ายการ์ด**: `ข้อมูล ณ {as_of}` · `Note: {w.note}` (ถ้ามี) · Industry ลิงก์ (`indLink`) ย้ายมาบรรทัดนี้
- ไม่มี research_card: แสดงแค่ชิปเหลือง + ธุรกิจ (`wlLine2`) + โน้ตของฉัน (ถ้ามี) + Note
- Candidate (ไม่อยู่ Watchlist): Overview เดิม ไม่มีส่วนโน้ต

## B. โน้ตของฉัน (เก็บใน watchlist doc · แยกจาก Research Card)
- ฟิลด์ใหม่ `my_notes = {cat:[{id, text, date|null}], blk:[{id, text}]}` ใน `users/{uid}/watchlist/{ticker}` · `wlItems` อ่านและตรวจชนิด (ไม่ใช่ array = ว่าง · text ≤ 200 ตัว · สูงสุด 10 ต่อฝั่ง)
- `＋ โน้ต` → ฟอร์มเล็กในที่ (input ข้อความ + ฝั่ง catalyst มีช่องวันที่ไม่บังคับ `type=date`) + ปุ่ม `บันทึก` / `ยกเลิก` · Enter = บันทึก · ว่าง = ปิดฟอร์ม
- แสดงสีม่วง (`--me` ตามม็อกอัป) + ป้าย `โน้ตของฉัน` · ปุ่ม `×` ลบ (เฉพาะโน้ตของตัวเอง · ลบใน doc ทันที)
- โน้ต catalyst ที่มีวัน เรียงรวมกับ catalysts ของการ์ดตามวัน · ไม่มีวัน = ท้ายรายการ
- อัปเดต/นำเข้า Research Card ใหม่ → **โน้ตไม่หาย** (อยู่คนละ doc)
- Firestore rules เดิมของ watchlist ครอบคลุมแล้ว (เขียน doc ตัวเอง)

## D. เอา FQC ออกจากโค้ด (ไม่แตะข้อมูล)
- ลบโค้ดที่อ่าน `d.fqc` ทั้งหมด (~7512–7514 ชิป · ~7826 ใน `wlEntryChip`) + คอมเมนต์ที่อ้าง FQC (~7537 ฯลฯ) · grep `fqc` `FQC` ให้เหลือ 0 ใน index.html (ยกเว้นคอมเมนต์ประวัติสั้น ๆ 1 บรรทัด `/* WL1 — FQC เลิกใช้ 1 ต.ค. 2569 · ใช้ Tier แทน · ข้อมูลเดิมใน Firestore ไม่ลบ */`)
- ลบ `wlEntryChip` (ชิป "เกณฑ์ลงทุนเดิมผ่าน/ต้องทบทวน/ยังไม่ประเมิน") และทุกจุดที่เรียก · ข้อมูล `investment_clearance` ไม่แตะ
- คอมเมนต์ ~4387 (doc จาก import_pine.py ที่มีแค่ fqc/growth_gate) — ตรวจว่าโค้ดตรงนั้นยังจำเป็นไหม (ticker สำรองจาก doc id): **ยังใช้กับ doc อื่นได้ → คงโค้ด แก้แค่คอมเมนต์** · ห้ามทำให้ doc เก่าที่มีแค่ fqc ทำให้หน้าพัง (ข้ามได้เงียบ ๆ)
- ปุ่มส่งออก/สำรองข้อมูล (backup) ที่ดึงทั้ง doc → คงเดิม (ข้อมูล fqc ติดไปใน backup ได้ ไม่เป็นไร)

## C. งานเล็กค้าง (รวมรอบนี้)
1. **คำสั่ง Research Card** (`research-card.js` → `promptText`): เพิ่มประโยคต่อจาก "Return exactly these 15 top-level fields … changes." (อังกฤษ):
   `Hard limits (the import rejects anything larger): metrics at most 12, drivers at most 3, additional_drivers at most 12, catalysts at most 8, tripwires 1 to 2, severe_risks at most 8, sources at most 30, missing_data at most 20, changes at most 20. Output the JSON object only — no text before or after it.`
2. **ช่องนำเข้า** (`research-card.js` ~129 `JSON.parse(box.value)` และ ~144 `pending.raw`): ก่อน parse ตัดเหลือตั้งแต่ `{` ตัวแรกถึง `}` ตัวสุดท้าย (ตัด ```json fence ด้วย) · ไม่มี `{` = ข้อความผิดพลาดเดิม
3. **แท็บ Research — ช่องเช็ก Tier** (`rcMetricGrid` · metric code `chk`): แสดงค่าเป็น `FCF 3 ปี ✓ · ปันผล/ซื้อคืน ✓ · OCF ✓` (no = ✗ · ไม่รู้ = ?) แทนสตริงดิบ · ค่าใน doc ไม่เปลี่ยน
4. **ค่าตั้ง SR1** (`#satHeatHint` ~8653): "ด้านบน" → `ในส่วน MAX HEAT ด้านล่าง`
- ข้อ 1–3 แก้ `research-card.js` → `python3 inline-research-card.py` (sha ใหม่ใน index.html)

## เทส
### `research-card-test.js` (node)
- prompt มี `Hard limits` · `tripwires 1 to 2` · `no text before or after` · ประโยค RC1/RC2 เดิมครบ
- นำเข้าข้อความ `"กำลังตรวจ…\n{…}\nจบ"` และ ```` ```json\n{…}\n``` ```` → parse ได้การ์ดเดียวกับ JSON ล้วน · ข้อความไม่มี `{` → error เดิม
- การ์ด tripwires 3 ข้อ → ยังถูกปฏิเสธ (schema เดิม)
### `tests/run_tests_phase35.py` (Chromium · 1440 + 430 · mock Firestore · นาฬิกาปลอม 2026-10-01)
seed: `AVGO` Watchlist + research_card (catalysts: 1 estimated `2026-12-10` + 1 confirmed + 1 วันผ่านแล้ว · severe_risks 5 ข้อ · tripwires 2 ข้อ: 1 `check` 1 watching · fqc มีข้อมูล) · `CALM` (tripwire ไม่มี check) · `NOCARD` (ไม่มี research_card) · `CAND1` candidate
1. AVGO Overview: ไม่มีคำ `FQC` ทั้งแผง · ไม่มีบรรทัด "ต้องทำ" · ชิป `Research 2026-…· n วัน` ถูก
2. แถบเตือนขึ้น (เพราะ check) · ข้อความมีชื่อ tripwire · กดแล้ว `wlSub==='rs'` · CALM ไม่มีแถบ · tripwire `confirmed` → แถบแดงข้อความ "ยืนยันแล้ว"
3. Catalysts: 2 รายการ (วันผ่านแล้วซ่อน) · estimated = `~10 ธ.ค.` + คลาสเส้นประ · เรียงใกล้ก่อน
4. Blockers: 3 ข้อ + `+ อีก 2 ข้อในแท็บ Research`
5. Tripwire: 2 แถว 🟡/🟢 · แสดง `ตอนนี้ {current_value}`
6. ＋ โน้ต (catalyst มีวัน 2026-11-01) → doc `my_notes.cat` มี 1 · แสดงสีม่วง + ป้าย "โน้ตของฉัน" · เรียงก่อน 10 ธ.ค. · ＋ โน้ต blocker → `my_notes.blk` · × ลบ → หายจาก doc และจอ
7. นำเข้า Research Card ใหม่ให้ AVGO (ผ่าน `rcMerge`/ทางนำเข้าเดิม) → โน้ตยังอยู่
8. NOCARD: ชิปเหลือง "รอสร้าง Research Card" · ไม่มีส่วน Catalysts/Tripwire จากการ์ด · ยังเพิ่มโน้ตได้
9. CAND1: Overview เดิม · ไม่มีปุ่ม ＋ โน้ต · ชิป Screen เดิมยังอยู่
10. แท็บ Research AVGO: ช่องเช็ก Tier แสดง `FCF 3 ปี ✓ · ปันผล/ซื้อคืน ✓ · OCF ✓` (seed `yes/yes/yes`) · `yes/no/?` → `✓ · ✗ · ?`
11. ค่าตั้ง: `#satHeatHint` มีคำ "MAX HEAT ด้านล่าง"
12. FQC ออกหมด: grep `fqc`/`FQC` ใน index.html = 0 (นอกคอมเมนต์ประวัติ) · ไม่มีชิป "เกณฑ์ลงทุนเดิม…" ทุกหน้า · doc ที่มี `fqc` + `investment_clearance` ยังโหลด/แสดงได้ไม่พัง · หลังแก้หุ้นแล้วบันทึก doc → ฟิลด์ `fqc` ใน mock DB ยังอยู่ (ไม่ถูกลบ/เขียนทับ)
13. 430px: Overview ไม่ล้นแนวนอน (เช็กราย element: ชิปวันที่ · แถวโน้ต · ฟอร์มโน้ต) · ไม่มี console error
- ภาพ `tests/screenshots/wl1-*` (1440 + 430): `overview-alert` · `overview-calm` · `note-form` · `nocard` · `research-chk` — เทียบกับม็อกอัปให้ลำดับ/สีตรง

### เทสเก่า
- เคสที่คาดชิป FQC / ชิป "เกณฑ์ลงทุนเดิม…" / `wlEntryChip` / "Research Card" สีเขียว / บรรทัด "ต้องทำ" / ป้าย Business / Blockers แบบเดิมใน Overview (เช่น phase 19 · 21 · 29 · 33) → **แก้ความคาดหวังของเคส (ห้ามลบ ห้ามปล่อยล้ม)** ให้ตรงหน้าตาใหม่ · จดใน `tests/WL1_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- รันครบ: `node research-card-test.js` · `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–35 (รันทีละชุด ไม่ขนาน)

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ตารางจุดที่แก้ · diff `promptText` · sha ใหม่ · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
