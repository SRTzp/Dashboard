# WM1 — Report back

**Gate:** PF1 (`PF1-report.md`, phase98 ผ่าน) และ PF2 (`PF2-report.md`, phase99 + related ผ่าน) เสร็จและผ่านในเครื่อง · user ยกเว้นเงื่อนไข "verified on the cloud" สำหรับ run นี้.

**แผน (≤ 8):** 1) Calc.wi* pure (mapping/validate/merge/state) · 2) listener + backup weeklyImpact · 3) แผง Weekly Impact (HIGH/MED ชิป 2 คอลัมน์ · พับ LOW/ไม่มีข้อมูล) · 4) รายละเอียดทีละตัว · 5) ＋ Asset sheet (ป้าย+เรียง) · 6) การ์ด Strategy (แถบ + ป้ายใหม่ + Note Copy/Clear · ถอดรูป) · 7) Today ข่าววันนี้ + จับเวลา + อัปเดตผล · 8) เทส phase100.

## การเปลี่ยนแปลง
- **สัญญาข้อมูล:** `docs/weekly-impact-schema.md` (weeklyImpact/v2 · v1 legacy · SAMPLE ชัดเจน · manifest · Rules).
- **เก็บข้อมูล:** `users/{uid}/weeklyImpact/{จันทร์}` · reimport = แทนสแนปช็อต แต่ไม่ทับ actual ที่ยืนยันแล้วด้วย null (เก็บ provenance) · event id ชนต่างตัวตน → รายงาน ไม่ merge · เพิ่มใน `BK_COLS` + กู้คืน.
- **แผง** (Strategy สัปดาห์ปัจจุบัน): Paste · ช่วงสัปดาห์ · ICT · อัปเดต asof · ชิป ● ชื่อ + ระดับ (ข้อความเสมอ) + ＋/✓ แยกการกด · ไม่มีหัว HIGH/MED · พับ "LOW / ไม่มีข้อมูล · n" (ป้ายต่างกัน) · รายละเอียดทีละ 1 ใต้แถวที่แตะ.
- **การ์ด Strategy:** แถบ `Weekly Impact · ช่วง` + `[HIGH] เหตุการณ์หลัก · เวลา ICT` + More · `Quarterly Macro · 2026Q4` · `Change if · Quarterly` · `Note · This week` + Copy last week (ซ่อนเมื่อไม่มี · ถามก่อนทับ) + Clear Note · ถอดรูป/ลิงก์ TradingView ออกจากการ์ด (ข้อมูล `w.chart` ยังอยู่).
- **Today:** "ข่าววันนี้ · เวลาไทย" (event ตามเวลาจริง ICT · เฉพาะ Asset ที่เลือก · ซ้ำ=ครั้งเดียว) · ≤30 นาที = ใกล้ประกาศ · ถึงกำหนด · รออัปเดตผล (พับ ค้างข้ามวัน) · date-only/tentative ไม่มีนับถอยหลัง · ยกเลิกไม่เตือน · เลื่อนแสดงสถานะ · อัปเดตผล manual (actual+ที่มา+เวลา · แก้ previous เก็บต้นฉบับ) · ตัวจับเวลาเดียว + visibility/focus.

## ความขัดแย้ง B1 ที่จัดการ
#1 ถอดรูป/TradingView · #2 Note ป้าย/ปุ่ม (เอาออกจากสัปดาห์ยังอยู่) · #3 Copy last week แทน PF2 · #4 แผงตาม §6 · #5 การ์ด Sat (A/B/C) กับข่าววันนี้อยู่คู่กัน (ข่าวขึ้นก่อนที่ด้านบนของ Today) · #6 mapping อาทิตย์↔จันทร์ (`Calc.wiMondayOfStrategy`) · #7 map ผ่าน ID/alias/ชื่อตรงตัว (WM1b) · #8 collection ใหม่ · #9 ป้าย Quarterly.

## Firestore rules (ผู้ใช้เพิ่มเอง — ไม่ deploy)
```
match /users/{uid}/weeklyImpact/{week} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow create, update: if request.auth != null && request.auth.uid == uid
    && week.matches('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    && request.resource.data.schema in ['weeklyImpact/v1', 'weeklyImpact/v2'];
  allow delete: if false;
}
```
`permission-denied` → แจ้งชัด ข้อความที่วางยังอยู่ (ทดสอบแล้ว).

## US / XAG / USDJPY ในแอป
`US` เป็น key สงวน (`SAT_KEY_RESERVED`) — ไม่ใช่ Sat Asset · ใน Playbook เป็นกลุ่ม "หุ้น Core" · ไม่มีการเดา S&P/Nasdaq (กำกวมถูกข้ามพร้อมเหตุผลจนกว่าจะตั้ง alias+ตลาดอ้างอิงใน WM1b) · XAG / USDJPY ใช้ได้เมื่อผู้ใช้เพิ่มเป็นสินค้า Sat เอง (custom) เท่านั้น.

## เทส / ภาพ
phase100: 127/127 · suites เก่าที่เกี่ยวข้อง (9, 11, 17, 38, 39, 45, 56, 59, 60, 63, 69, 72–99) ผ่านหลังปรับตาม `tests/WM1_retired.md` · ภาพ wm1-{panel-390,panel-detail-390,panel-300,addasset-390,card-390,card-1440,today-390,today-1440} เปิดดูแล้ว (ภาพ card-1440 จางเพราะเป็นภาพ element ยาวเกินจอใต้ header — ไม่ใช่บั๊ก).

## ข้อจำกัด
ไม่มี push แจ้งเตือน/ข้อมูลอัตโนมัติ (ตามสเปก) · เขตเวลา Strategy ใช้ปฏิทินเครื่อง (`wpWeekKey` เดิม) แล้ว map เป็นจันทร์ด้วยคณิตศาสตร์ข้อความ · ไม่มีการยืนยันบน cloud.
