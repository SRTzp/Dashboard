# WM1b — Report back

## สิ่งที่เปลี่ยน
- **Mapping สัปดาห์:** ตัวช่วยเดียว `Calc.wiMondayOfStrategy` / `wiStrategyOfMonday` (คณิตศาสตร์วันที่แบบข้อความ ไม่พึ่ง TZ เครื่อง · ทดสอบ Asia/Bangkok, UTC, America/New_York ได้ผลเดียวกัน · ข้ามเดือน/ปี) · "ต่างสัปดาห์" แยกจาก "อัปเดต <asof>" · Today เลือก event ตามเวลา ICT จริงจากสแนปช็อตปัจจุบัน + ก่อนหน้า (event วันอาทิตย์ยังขึ้น) dedupe ด้วย event id.
- **ตั้งค่าสินค้า Sat (ตั้งค่า › ตั้งโบรก › สินค้า Sat):** ต่อสินค้าเพิ่ม `ใช้งาน` (active) · `ตลาดอ้างอิง` (S&P 500 / Nasdaq-100 / Dow / Russell / Gold / Silver / Brent / WTI / Bitcoin / USD/JPY / SET50 / อื่น ๆ ≤30) · `Alias` (≤5, A–Z0–9 2–10) · ลิงก์ Playbook · เก็บใน `satAssetCfg[key]` เดิม (ไม่มี collection ใหม่ · ไม่เก็บ active:true) · built-in แสดงคำแนะนำสีจาง (Gold spot / Bitcoin / SET50 / Brent crude) แต่ไม่ตั้งให้ · chip "ตั้งตลาดอ้างอิง" เมื่อยังไม่ตั้ง.
- **กติกา alias:** ซ้ำรหัสสินค้า/alias อื่น/alias ในตัว (BTC → BTCUSD) = ปฏิเสธ · `US` เป็น alias ได้เมื่อตั้งตลาดอ้างอิงแล้วเท่านั้น (`US` ยังเป็น key สงวน ไม่ถูกปลดล็อก).
- **ปิดใช้งาน:** ซ่อนจาก ＋ Asset และชิป Weekly Impact · ถามยืนยันเมื่อถูกใช้ (เลือกสัปดาห์นี้ / ไม้เปิด / แผนใช้งาน) · แผน ไม้ Journal Port ป้ายชื่อยังทำงาน (ใช้รายการเต็ม).
- **Import mapping:** ID → alias ประกาศ → ชื่อที่แสดง (ตรงตัว) · ไม่ fuzzy · ไม่สร้าง Asset · งานวิจัยเฉพาะตลาดต้องตรงกับตลาดที่ตั้ง · ยังไม่ตั้ง → ข้าม "ตั้งตลาดอ้างอิงก่อน" · `US` ไม่ใช่ alias สากล · preview ✓/⊘ ก่อนบันทึก · ข้ามตัวหนึ่งไม่ล้างตัวอื่น.
- **Manifest:** ปุ่ม `คัดลอก Asset manifest` ในหน้า Paste (เฉพาะ Asset ที่ใช้งาน: id · name · ref_market · aliases) + เอกสารใน `docs/weekly-impact-schema.md`.

## ความขัดแย้ง / ข้อสังเกตในข้อมูลเดิม
ไม่พบ ID เดียวที่ใช้แทนตลาดต่างกัน (ไม่มีการ migrate อัตโนมัติ) · ผู้ใช้ที่อยากเทรดดัชนี: เพิ่มสินค้าเอง (เช่น NDX/SPX) แล้วตั้งตลาดอ้างอิง (+ alias US ถ้าต้องการ) — `US` ไม่ถูกปลดล็อกเป็น key.

## ไฟล์ / เทส
index.html · tests/run_tests_phase101.py (75/75) · run_tests_phase39.py (เพิ่ม `TZID`) · ภาพ wm1b-{assets-390,assets-1440,import-preview-390} เปิดดูแล้ว (assets-1440 เป็นภาพ element สูงมาก) · suites เก่าที่เกี่ยวข้องดูผลท้ายรายงานชุดเต็ม.
## ข้อจำกัด
ไม่ push · ไม่ลบไฟล์.
