# PH1 — Trend Phase ต่อหุ้น (Side · Start▲ · Up · Weak▼) ใน Watchlist / Candidates + ตัวกรอง + แสดงในแผน Core · เทส 61

> ผู้ใช้ตัดสิน 11 ต.ค. · ทำหลัง AC1 · สำรองก่อนแก้: `index.backup-pre-PH1.html` · `tests/_bk_ph1/` · ห้ามแตะ core-size.js · ห้ามย้อนงานรอบก่อน (ID2 แถวบรรทัดเดียว · VW1 แถว Candidate ขยาย)
> ไฟล์ชั่วคราวที่สร้างเองให้ย้ายไป `_to_delete/` ห้าม rm
> เป้า: ขั้นแรกของการคัดหุ้น Core = price structure เปลี่ยน phase (sideway → uptrend) · กรอง/เรียงได้

## ข้อตัดสิน
- **กรอกเองเป็นหลัก** · แอปแสดง "ข้อมูลช่วย" เฉพาะหุ้นที่มีราคาปิดรายสัปดาห์จาก PX1 (`prices/{SYM}`: close + ema10w) = ข้อความ `ปิด W เหนือ EMA10` / `ปิด W ใต้ EMA10` · **ไม่เขียนทับค่าที่ผู้ใช้เลือก · ไม่เดา phase เอง**
- 4 ค่า + ว่าง: `side` Side · `start` Start▲ · `up` Up · `weak` Weak▼ · ไม่มีค่า = `—`
- ที่เก็บ: `stockNotes/{SYM}` (ที่เดียวกับ VW1 · ใช้ร่วม Watchlist + Candidates) ช่องใหม่ `phase:{v, at:'YYYY-MM-DD'}` · ย้าย Candidate → Watchlist ค่าตามไปเอง

## 1. ชิป phase
- แถว Watchlist และแถว Candidate: ชิปเล็กหลังชื่อ (สี: start = teal · up = green · side = เทา · weak = amber · ว่าง = เส้นประ `—`) · **แถวยังบรรทัดเดียว** (กติกา ID2)
- แตะชิป → เมนูเล็ก 4 ค่า + `ล้าง` (ไม่ขยายแถว/ไม่เปิดการ์ด) · มีข้อมูลช่วย → แสดงบรรทัดเล็กในเมนู
- อายุ: `phase.at` เก่ากว่า 14 วัน → ชิปมีจุดเล็ก (ควรทบทวน) · title บอกวันที่ตั้ง

## 2. ตัวกรอง
- แถบตัวกรอง Watchlist และ Candidates: เพิ่มชุดชิป `Start▲` `Up` `Side` `Weak▼` `—` (เลือกได้หลายค่า · ไม่เลือก = ทั้งหมด) · จำค่าต่อเครื่อง (localStorage ห่อ try/catch)
- เรียง: ปุ่มเรียง `Phase` (start → up → side → weak → ว่าง) เพิ่มต่อจากการเรียงเดิม
- 390px: แถบตัวกรองไม่ล้นแนวนอน (เลื่อนในแถบได้)

## 3. การ์ดแผน Core
- หัวการ์ด: ชิป phase ของหุ้น (อ่านอย่างเดียว · แตะ = ไปแถว Watchlist)
- phase = `side` / `weak` / ว่าง → บรรทัดเตือนสีเหลือง `Phase: Side — ยังไม่เข้า uptrend` (เตือนเท่านั้น ไม่บล็อก)

## เทส `tests/run_tests_phase61.py` (Chromium · 1440 + 390 · mock Firestore)
1. ไม่มี phase → ชิป `—` ทุกแถว · ตัวกรองไม่กรองอะไร · แถวบรรทัดเดียว
2. ตั้ง AVGO = Start▲ → `stockNotes/AVGO.phase = {v:'start', at:วันนี้}` · ชิปสี teal · แตะชิปไม่เปิดการ์ด/ไม่ขยายแถว
3. Candidate CAMT = Up → กด ＋ เพิ่มเข้า Watchlist → แถว Watchlist แสดง Up
4. ตัวกรอง Start▲ + Up → แสดงเฉพาะ 2 ค่านี้ · `—` → เฉพาะที่ยังไม่ตั้ง · เรียง Phase ถูกลำดับ
5. ข้อมูลช่วย: มี prices close > ema10w → `ปิด W เหนือ EMA10` ในเมนู · ไม่มี prices → ไม่มีบรรทัด · ค่า phase ไม่เปลี่ยนเอง
6. phase.at เก่า 15 วัน → จุดทบทวน · 13 วัน → ไม่มี
7. การ์ดแผน Core: Side → เตือน · Up → ไม่เตือน · บันทึกแผนได้ทั้งคู่
8. ไม่มีสิทธิ์อ่าน stockNotes → ชิปไม่แสดง · ส่วนอื่นทำงานปกติ
9. 390px: แถวบรรทัดเดียว · แถบตัวกรองไม่ล้นหน้า · ไม่มี console error
- ภาพ `tests/screenshots/ph1-*` (1440 + 390): `wl` · `cand` · `menu` · `filter` · `core-card`

### เทสเก่า
- เคสที่นับ/เทียบข้อความแถว Watchlist/Candidate หรือแถบตัวกรอง → แก้ความคาดหวัง (ไม่มี phase = ชิป `—`) · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/PH1_retired.md`
- อัปเดต `ไฟล์ที่ห้ามลบ.md`
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–61

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ฟังก์ชันใหม่/ที่แก้ · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
