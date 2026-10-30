# PV2b — เทสเก่าที่แก้ความคาดหวัง

ไม่มี — ไม่ได้แก้/ลบ/ทำให้อ่อนลงเคสเก่าใด ๆ ในรอบนี้ (เพิ่มเฉพาะ tests/run_tests_phase78.py)
- สิ่งที่เปลี่ยนพฤติกรรมโดยตั้งใจ: ไม้ Tactical ไม่นับโควตา "ไม้ใหม่ต่อสัปดาห์" ของ Main (sat7dAcctBase.nNew) · Max DD Satellite = จุดพักเดิม (ddPause) ผูกเป็นค่าเดียวกัน · Bias สัปดาห์เพิ่มค่า Neutral — เทสเก่ายังผ่านทั้งหมด (ดูรายงาน)

## แก้ความคาดหวัง (PV2b)
| ไฟล์ | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| run_tests_phase14.py | ตัวแก้ Strategy innerHTML เท่าเดิม | เทียบตรงกับ index เก่า | เทียบหลังตัดปุ่ม Neutral ที่เพิ่ม | Bias เพิ่มค่า Neutral (ปุ่มเดียว) |
| run_tests_phase14.py | ตัวแก้ = ฟอร์มเดิมครบ | ปุ่ม Bias 3 | 4 (Long/Short/Neutral/งดเทรด) | เหมือนกัน |
(แก้ตัวหนังสือแถบ PV2b ให้ ≥ 0.72rem ตามเคสขนาดฟอนต์ของ phase14 — แก้โค้ด ไม่แก้เทส)
| run_tests_phase2.py | ปุ่ม [+ แผน] ของ tile | onclick เรียก `satV3NewPlan('XAUUSD')` | เรียก `satV2NewPlan('XAUUSD')` | ปุ่มสร้างแผนฟอร์ม v2 (PV2a) |
| run_tests_phase11.py | แตะช่อง Macro (อ่านอย่างเดียว) | `page.click(..., force=True)` | `element.click()` ผ่าน JS | หัว Strategy ยาวขึ้น แถบแท็บล่างทับจุดกลางที่จอแคบ · assertion เท่าเดิม |
