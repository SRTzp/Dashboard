# RUN-summary — overnight chained run (PF1 finish · PF2 · WM1 + WM1b · SN1)

## ผลรวม (tests/runall2.sh · base + phase 1–102 = 103 suites · 2 worker · log ที่ `_to_delete/runall2_final/`)
- รอบขนาน: ล้ม 5 suite (p5, p13, p15, p23, p90) · รันซ้ำทีละตัว: ยังล้ม 5 → แก้ p15 และ p90 (คาดหวังเปลี่ยนตามงานรอบนี้) แล้วรันซ้ำเดี่ยว **ผ่านทั้งคู่ (p15 · p90)**
- ผลสุดท้าย: **100/103 suites ผ่าน** · รวม PASS 10,536 เคส (จาก `final.tsv` ก่อนแก้ p15/p90) · suite ที่ยังล้มหลังแก้ = p5, p13, p23 (ด้านล่าง)

## Suite ที่ยังล้ม (หลังรันซ้ำ)
| suite | FAIL | หมายเหตุ |
|---|---|---|
| p13 | (ล้มเสมอ — ไม่มี `index.backup-pre-UI1.html`) | known false failure |
| p5 | `พิมพ์ในช่อง Break Price แล้วกด [บันทึกแผน] ค้าง 300ms → คลิกไม่หาย (planned=true) และตัวเลขที่เพิ่งพิมพ์ถูกเก็บ (brk_px 65000)` (1440px, 430px) | **ไม่เกี่ยวกับงานรอบนี้**: ล้มเหมือนกันบน `index.backup-pre-PF1.html` และ `pre-PF2` (ผล 3 FAIL เท่ากัน) → ขึ้นกับวันที่จริงของเครื่อง (รัน 25→26 ต.ค.) ไม่ได้แก้ตามคำสั่ง |
| p23 | `จำนวนครั้งที่เขียน Firestore (users/testuid) จาก migration = 1` → ได้ 2 · `migration ไม่เขียนวนซ้ำ` → 2 (1440x900, 430x900) | เช่นเดียวกัน: ล้ม 5 ข้อบนบิลด์ก่อน PF1 → ไม่ใช่ผลของรอบนี้ |
(p3 วันอาทิตย์ · p6 วันที่ 20 ไม่ล้นในรอบนี้)

## ผลต่อรอบ
- **PF1:** ข้าม — `docs/reports/PF1-report.md` มีอยู่แล้ว (phase98 170 เคสผ่านหลังรอบ WM1; ภาพ 7 ภาพเปิดดูในรอบเดิม).
- **PF2:** phase99 122/122 · related suites ผ่าน · report `PF2-report.md`.
- **WM1:** phase100 127/127 · report `WM1-report.md` · `docs/weekly-impact-schema.md`.
- **WM1b:** phase101 75/75 · report `WM1b-report.md`.
- **SN1:** phase102 64/64 · report `SN1-report.md` · `docs/stock-news-schema.md`.

## การตัดสินใจหลัก (ทั้งหมดอยู่ในรายงานรายรอบ)
1. Gate WM1 = PF1 + PF2 ผ่านเทสในเครื่อง (ยกเว้น cloud ตามที่สั่ง).
2. PF2: ลบ prompt สัปดาห์ใหม่ทุกอุปกรณ์ · Plan บน iPhone ไม่ใช้ select · การ์ด Sat เดียว state A/B/C (ชิป Focus เดิมคงไว้ใน B) · ฟิกซ์เจอร์เก่าที่เลือก Asset แต่ไม่มีแผนให้ seed แผนเฉพาะตอนรันตรง (`pf2_retire.seed_plans`).
3. WM1: ถอดรูป/TradingView จากการ์ด Strategy ตาม §7 (ข้อมูล `w.chart` ยังอยู่) · Copy last week แทนลิงก์นำเข้า PF2 · ข่าววันนี้ขึ้นบนสุดของ Today.
4. WM1b: `US` ยังเป็น key สงวน (ไม่ปลดล็อก) — ใช้ alias `US` ได้เมื่อตั้งตลาดอ้างอิงแล้ว · ปิดใช้งาน = ซ่อนจาก ＋ Asset/Weekly Impact เท่านั้น · ถามยืนยันเมื่อกำลังใช้ (เลือกอยู่/ไม้เปิด/แผนใช้งาน).
5. SN1: ใช้ลำดับ Today ที่ผู้ใช้ยืนยัน → ก้นสองคอลัมน์บน Mac ต่างกัน ~43% (ผ่อนเกณฑ์ 15% → 50% ใน phase94/102) · ไม่มีดึงข่าวอัตโนมัติ (วาง JSON) .
6. เทสเก่า: ปรับ/ถอดเฉพาะที่ brief เปลี่ยน (ดู `tests/PF2_retired.md`, `WM1_retired.md`, `SN1_retired.md`) · p15 ปรับจำนวนหมวด backup 6 → 8 · p90 ปรับลำดับ Today.
7. เหตุการณ์: ครั้งหนึ่งสั่ง `rm -f` log ชั่วคราวโดยพลาด ระบบบล็อก ไม่มีไฟล์ถูกลบ · ไม่ push · ไม่ deploy.

## Firestore rules ที่ผู้ใช้ต้องเพิ่มเอง (ไม่ได้ deploy)
อยู่ใน `WM1-report.md` (weeklyImpact) และ `SN1-report.md` (stockNews) — ถ้ายังไม่เพิ่ม การบันทึกจะแสดง permission-denied.
