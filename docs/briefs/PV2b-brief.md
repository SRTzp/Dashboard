# PV2b — โครงพอร์ต v2 รอบ 2: กติกา Main/Tactical ตาม Bias · Hedge · เพดาน Open Risk · เบรก DD · แถบงบ Risk · เทส 78

> ต่อจาก PV2a ทันที · **Objective: Simple · Clear · ใช้งานง่าย · Effective** — แอปเตือน/บล็อกด้วยข้อความสั้นบอกเหตุผล ผู้ใช้ไม่ต้องจำกติกา
> กติกา: `docs/specs/port-structure-v2.md` ข้อ 4–5 · ม็อกอัป `docs/mockups/pv2-mockup.html` ② ③ ⑤
> สำรองก่อนแก้: `index.backup-pre-PV2b.html` · `tests/_bk_pv2b/` · ห้ามแตะ core-size.js · ห้ามย้อน PV2a · ไฟล์ชั่วคราว → `_to_delete/` ห้าม rm
> **ชุดที่เกี่ยวข้อง:** phase78 (ใหม่) · p77 · p69 · p72 · p74 · p75/p76 · ชุด SR1 (ห้ามสวน Bias) · ชุด DD (grep `ddPct|ddPause`)

## 1. กติกา Tactical ตาม Bias สัปดาห์ (ตอนบันทึก order / Activate)
| Bias | Tactical ทิศเดียวกับ Bias | Tactical สวน Bias |
|---|---|---|
| Long / Short | ได้ · ป้าย `เร่งกำไร` | **บล็อก** "สวน Bias" (ไม้ค้างเดิมจัดการได้ปกติ) |

| Bias Neutral | Tactical |
|---|---|
| มีไม้ Main (asset เดียวกัน) · ทิศ**สวน** Main | ได้ · ป้าย `Hedge` · **จำนวนสัญญา ≤ Main** (ขนาดใช้ค่าน้อยสุดรวมเงื่อนไขนี้ · เกิน → บล็อก "Hedge ใหญ่กว่า Main") |
| มีไม้ Main · ทิศ**เดียวกับ** Main | **บล็อก** "รอ Bias เปลี่ยนเป็น Long/Short ก่อน" |
| ไม่มี Main | ได้ · ป้าย `Range` · ข้อความเตือนเบา ๆ "กรอบควรกว้าง ≥ 3× SL" (ไม่บล็อก · ไม่ต้องกรอกกรอบ) |
- Main ใช้กติกาเดิม (SR1 ห้ามสวน Bias Long/Short) · Main ตอน Neutral เข้าได้ตามเดิม
- ป้ายประเภท (`เร่งกำไร` / `Hedge` / `Range`) แอปตั้งเอง เก็บในไม้ (`tac_type`) ไว้ดู stat
- Main โดน SL → Hedge ไม่ปิดตาม

## 2. เพดาน Open Risk (ค่าจากตั้งค่า PV2a)
- Open Risk ไม้ Sat = |Entry − SL ปัจจุบัน| × ขนาด (SL เลย Entry ไปฝั่งกำไรแล้ว = 0) — แอปไม่มีราคา Sat สด
- **Satellite ≤ 1.2%** · **ต่อสินค้า (Main+Tactical) ≤ 0.6%** · **Core + Satellite ≤ 6%** ของพอร์ตรวม · Core นับเฉพาะไม้ที่ SL ยังต่ำกว่าทุน (ส่วนที่เสียจากทุน)
- ไม้ใหม่ที่ทำให้เกิน → **บล็อก** + บอกตัวเลข ("Satellite จะเป็น $1,950 > $1,800") · นับทั้ง Hedge และ Main เต็ม ไม่หักกัน

## 3. เบรก
- **Max DD Satellite** (ค่าเริ่ม 20% · จาก peak ของเงิน Satellite) → บล็อกไม้ใหม่ทั้ง Main + Tactical · ระบบลดขนาดเดิม (ddReduce ฯลฯ) คงไว้ตามค่าตั้งเดิม แค่จุดหยุดใช้ค่านี้
- **เบรก Tactical**: เสียติดกัน 5 ไม้ หรือ DD 10% ของเงิน Tactical → บล็อกไม้ Tactical ใหม่ (Main เปิดได้) · ปลดเมื่อ DD กลับต่ำกว่าเกณฑ์ / มีไม้ชนะ (บอกเงื่อนไขปลดในข้อความ)

## 4. หน้าตา (ม็อกอัป ② ③)
- หัว Strategy: แถบ `Satellite Open Risk $x / $y (1.2%)` แยกสี Main/Tactical · แถบ `Core + Satellite` · บรรทัดเบรก Tactical (`เสียติด n/5 · DD x%/10%` + ป้าย `เปิดได้` / `หยุด`)
- การ์ด Asset: ไม้ Main + Tactical แยกแถว (ป้ายส่วน + ป้ายประเภท + ทิศ + lot + Entry/SL + Risk) · แถบ `Risk รวม {asset} $x / $y (0.6%)`
- ข้อความบล็อก/เตือนสั้นตามม็อกอัป ⑤ · ปุ่มที่บล็อก = ปิด + เหตุผลใต้ปุ่ม

## เทส `tests/run_tests_phase78.py` (Chromium · 1440 + 390 · mock Firestore)
1. Bias Long · Tactical Short → บล็อก · Tactical Long → ได้ ป้ายเร่งกำไร
2. Neutral + Main Long 0.10 · Tactical Short → Hedge · ขนาด ≤ 0.10 (Risk จริงแสดง) · Tactical Long → บล็อก "รอ Bias"
3. Neutral ไม่มี Main → Range + เตือนเบา ไม่บล็อก
4. เพดาน: Satellite เกิน 1.2% → บล็อก + ตัวเลข · ต่อสินค้าเกิน 0.6% → บล็อก · Core+Sat เกิน 6% → บล็อก · SL เลย Entry → Open Risk 0 → เปิดไม้ใหม่ได้
5. Max DD Satellite 20% → บล็อกทั้งสองส่วน · เบรก Tactical (5 แพ้ติด) → บล็อกเฉพาะ Tactical · Main เปิดได้
6. แถบหัว Strategy + การ์ด Asset แสดงตัวเลขตรงกับข้อมูล · เปลี่ยนค่าตั้ง (เช่น 1.2 → 1.5) → แถบ/บล็อกตามค่าใหม่
7. Main โดน SL → Hedge ยังเปิดอยู่
8. 390 ไม่ล้น · ไม่มี console error · ภาพกราฟไม่โหลดซ้ำตอนกดปุ่ม (กติกา RR2 ยังผ่าน)
- ภาพ `tests/screenshots/pv2b-*` (1440 + 390): `header` · `asset-hedge` · `blocks` · `brake`

### เทสเก่า
- ห้ามลบเคส ห้ามทำให้อ่อนลง · จด `tests/PV2b_retired.md` · อัปเดต `ไฟล์ที่ห้ามลบ.md`
- **จบคิว (หลัง PV2b): รันเต็มชุดครั้งเดียว ทีละชุด (base + phase 1–78)**

## รายงานกลับ
จำนวนเคส · ฟังก์ชันใหม่/ที่แก้ · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง (ยึด Objective) · ไม่ push ไม่ลบไฟล์
