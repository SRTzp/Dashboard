# DD1 — เคสเก่าที่แก้ความคาดหวัง (tests)

ผลรัน 2 ต.ค. 2026: ชุดเต็มทีละชุดกับ index.html ใหม่ → ล้มเฉพาะ phase 14 · 23 · 24 · 25 · 26 · 34 · 36 · แก้ความคาดหวังตามนี้ (ไม่ลบเคส · จำนวนเคสเท่าเดิม) · สำรองไฟล์เดิมใน `tests/_bk_dd1/*.backup-pre-DD1.py` (+ `run_tests_phase36.backup-pre-DD1.py` · `core_size_test.backup-pre-DD1.js`)
ล้มก่อนแก้โค้ดอยู่แล้ว (ไม่เกี่ยวกับ DD1): phase 13 (ต้องการ `index.backup-pre-UI1.html` ที่ไม่มีในโฟลเดอร์) · phase 22 เคส `_extracted.js` (ผ่านในโฟลเดอร์จริง)

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase14 | Future: แถบ Sat ต่อบัญชี ข้อความเท่าเดิม | แถบเท่าไฟล์สำรอง | เท่ากันหลังตัดชิป `DD0%ปกติ` ออก | DD1 เพิ่มชิป DD ในแถบบัญชี Sat |
| phase23 | core_size_test = 346/346 | 346 | 403 | DD1 เพิ่ม 57 เคส ddStep |
| phase23 | ป้ายหน่วยตั้งค่า Core 19 ช่อง | 19 | 23 | +4 ช่อง DD (reduce · pause · สัปดาห์ · R) |
| phase23 | coreRisk หลังบันทึก = 19 คีย์ | 19 | 23 | เก็บ ddReduce/ddPause/ddPauseWeeks/ddRecoverR |
| phase23/25/26 | core-size.js ต่างจาก backup 7E-2b-1 | 11 hunk | 13 hunk | +ddStep (2 hunk) · สูตรเดิมไม่แตะ |
| phase25/26 | core_size_test = 346/346 | 346 | 403 | ข้างบน |
| phase24 | Journal ไม้ปิด exit 95: R | (95−ทุน)/\|ทุน−SL ปัจจุบัน 113\| | (95−ทุน)/\|ทุน−sl0\| | §0: R ใช้ SL ตอนเข้า |
| phase34 | satRiskCfg ค่าเริ่มต้น | {rpt,rptHi,heatMax,newMax} | + ddReduce 12.5 · ddPause 20 · ddPauseWeeks 1 · ddRecoverR 2 | ค่าตั้ง DD ของ Sat |
| phase34 | ส่วนตั้งค่า Sat มี 3 ช่อง | 3 input | 7 input | +4 ช่อง DD |
| phase34 | บันทึกแล้ว settings.satRisk | {rpt,rptHi,newMax} | + 4 ค่า DD | saveSettings เก็บค่า DD |
| phase36 | ไม้ 1 หลังย้าย SL ร่วม เสี่ยง 0 | "0 USD" | "฿0" | §0.3 แสดงเป็น ฿ |

เคสใหม่ของ DD1 อยู่ใน `run_tests_phase37.py` (218 เคส · 109 ต่อหน้าจอ) และ `core_size_test.js` (+57)
