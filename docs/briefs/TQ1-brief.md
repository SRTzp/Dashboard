# TQ1 — ด่าน Tier เร็วที่แถว Candidate (A-Fortress · A-Growth · B · ไม่ผ่าน · ยังไม่เช็ก) + การบ้านเริ่มที่ Tier · เทส 62

> ผู้ใช้ตัดสิน 11 ต.ค. · ทำหลัง PH1 · สำรองก่อนแก้: `index.backup-pre-TQ1.html` · `tests/_bk_tq1/` · ห้ามแตะ core-size.js · ห้ามย้อนงานรอบก่อน (WT1 Tier ใน Watchlist · GL3 การบ้าน 5 part · VW1 · PH1)
> ไฟล์ชั่วคราวที่สร้างเองให้ย้ายไป `_to_delete/` ห้าม rm
> เป้า: เช็กตัวเลข Tier ก่อนลงแรงเจาะ Thesis · ไม่ผ่าน = เฝ้าดู ไม่ใช่ทิ้ง

## ข้อตัดสิน
- ระดับคง **A / B** เหมือน WT1 (ไม่เพิ่ม S ตอนนี้) · A แยกมุม Fortress / Growth ตามเกณฑ์เดิม (TIER2) · B = ดุลพินิจผู้ใช้ (ไม่มีเกณฑ์ตัวเลข)
- ค่า Candidate: `A-Fortress` · `A-Growth` · `B` · `ไม่ผ่าน` · `ยังไม่เช็ก` (ค่าเริ่มต้น)
- ที่เก็บ Candidate: `stockNotes/{SYM}.tier = {tier:'A'|'B'|'fail', tier_lens:'fortress'|'growth'|null, tier_set_at}` · **รูปแบบเดียวกับ `WL_TIER_FIELDS` ของ WT1** (ไม่มีค่า = ยังไม่เช็ก)
- เพิ่มเข้า Watchlist (`ideaCandAdd` / ปุ่มในแถวขยาย): A/B → คัดลอก `tier` `tier_lens` `tier_set_at` ลง watchlist doc (ถ้า doc ยังไม่มี tier) · `fail` → เพิ่มได้ แต่ยืนยันก่อน `CAMT ไม่ผ่าน Tier — เพิ่มเข้า Watchlist ต่อไหม` · ไม่คัดลอก fail ลง watchlist
- หุ้นที่อยู่ Watchlist แล้ว: Tier ยังตั้งที่ Watchlist ตาม WT1 เหมือนเดิม (ไม่ย้ายที่เก็บ)

## 1. แถว Candidate (แถวขยายของ VW1)
- เพิ่มแถว `Tier` บนสุด (ก่อน Event/Fund./Tech): ชิปเลือก 4 ค่า `A-F` `A-G` `B` `ไม่ผ่าน` (แตะซ้ำ = กลับเป็นยังไม่เช็ก) · บรรทัดเล็กเกณฑ์ A ทั้ง 2 มุม (อ่านค่าจากค่าตั้ง TIER2 · ไม่เขียนตายตัว)
- แถวที่ยังไม่ขยาย: ป้ายเล็กหลังชื่อ `A` / `B` / `✕` (ไม่ผ่าน) · ยังไม่เช็ก = ไม่มีป้าย · แถวยังบรรทัดเดียว (ร่วมกับชิป phase ของ PH1)
- ตัวกรอง Candidates: เพิ่มชิป `ผ่าน Tier` (A+B) · `ไม่ผ่าน` · `ยังไม่เช็ก`

## 2. การบ้าน (GL3)
- ลำดับชิป part ใหม่: **`Tier` ก่อน** → ธุรกิจ · ทำไม · ติดตาม · ออก (id เดิม · แค่ลำดับแสดง · log เก่าไม่ต้องแปลง)
- ที่มาหุ้น (Candidates ต่อท้าย Watchlist ของ GL3): **ข้าม Candidate ที่ `fail`** · Candidate ที่ยังไม่เช็กมาก่อน Candidate ที่ผ่านแล้ว (ให้เช็ก Tier ก่อน)
- การบ้านเป็น Candidate และติ๊ก part `Tier` → เปิดแถว Candidate ที่ขยายไว้ให้ตั้งค่า (ไม่ตั้งแทนผู้ใช้)

## เทส `tests/run_tests_phase62.py` (Chromium · 1440 + 390 · mock Firestore)
1. Candidate ใหม่ → ยังไม่เช็ก · ไม่มีป้าย · แถวขยายมีแถว Tier บนสุด + เกณฑ์อ่านจากค่าตั้ง (แก้ค่าตั้ง ROIC 12→15 → ข้อความเปลี่ยน)
2. เลือก A-G → `stockNotes/CAMT.tier = {tier:'A', tier_lens:'growth', tier_set_at:วันนี้}` · ป้าย `A` · แตะซ้ำ → ล้าง
3. A-F → ＋ เพิ่มเข้า Watchlist → watchlist doc มี tier A / fortress · ป้าย Tier ใน Watchlist = `A · Fortress` · Watchlist ที่มี tier อยู่แล้ว → ไม่ทับ
4. ไม่ผ่าน → ป้าย `✕` · เพิ่มเข้า Watchlist → มี confirm · ยกเลิก = ไม่เพิ่ม · ตกลง = เพิ่ม (ไม่มี tier)
5. ตัวกรอง ผ่าน Tier / ไม่ผ่าน / ยังไม่เช็ก ถูกต้อง
6. การบ้าน: ชิปแรก = Tier · Watchlist หมดแล้ว → Candidate ที่ยังไม่เช็กมาก่อนตัวที่ผ่าน · ตัวที่ fail ไม่ถูกเสนอ
7. log การบ้านเก่า (parts ลำดับเดิม) → นับ n/5 เท่าเดิม
8. 390px: แถว Candidate (ชื่อ + phase + ป้าย Tier) บรรทัดเดียว · ชิป Tier สูง ≥ 32px · ไม่ล้น · ไม่มี console error
- ภาพ `tests/screenshots/tq1-*` (1440 + 390): `cand-tier` · `cand-row` · `hw`

### เทสเก่า
- GL3 (p58) / GL1 (p56) / VW1 (p59) ที่เทียบลำดับชิปหรือแถวขยาย Candidate → แก้ความคาดหวังตาม brief · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/TQ1_retired.md`
- อัปเดต `ไฟล์ที่ห้ามลบ.md`
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–62

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ฟังก์ชันใหม่/ที่แก้ · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
