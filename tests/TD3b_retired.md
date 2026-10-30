# TD3b — ค่าที่คาดหวังที่เปลี่ยน

รูปแบบ: suite · เคส · ความคาดหวังเดิม → ใหม่ · เหตุผล

| suite | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| run_tests_phase56.py | PF3 1 Weekly ชุดเริ่มต้น (ไม่มีบัญชีตั้งเป้า) | wbias · wjournal · wdaily | wbias · wsector · wjournal · wdaily | เพิ่มงาน Weekly เริ่มต้น "Review drivers for selected sectors" (TD3b) |
| run_tests_phase56.py | PF3 8 ก่อนติ๊ก รวม | 0/4 · 0% | 0/5 · 0% | งานเริ่มต้นเพิ่ม 1 ข้อ |
| run_tests_phase56.py | 8 ติ๊ก Journal | 1/4 · 25% / Weekly · 25% | 1/5 · 20% / Weekly · 20% | ตัวหาร +1 |
| run_tests_phase56.py | PF3 8 แถว Weekly ครบ | 4 แถว | 5 แถว (เพิ่ม wsector · กดเอง) | งานเริ่มต้นเพิ่ม 1 ข้อ |
| run_tests_phase56.py | PF3 8 ปิดงาน wbias → ตัวหาร | 3 | 4 | งานเริ่มต้นเพิ่ม 1 ข้อ |
| run_tests_phase56.py | PF3 9 ปุ่มลบงานกดเอง (index) | ["0","2"] | ["0","1","3"] | wsector เป็นงานกดเอง ลบได้ (index 1) · Journal เลื่อนเป็น 3 |
| run_tests_phase94.py / phase102 / phase103 | ลำดับการ์ดคอลัมน์ขวาบน Mac | goal → sat → hw … | goal → ? (บล็อก Sectors) → sat → hw … | TD3b เพิ่มบล็อก Sectors ต่อจากเป้าหมาย Port (B6) · tdBalance ย้ายการ์ดมาต่อท้ายบล็อก Sectors |
| run_tests_phase104.py | 3 ลำดับขวา: การ์ดที่ย้ายต่อจาก goal | ถัดจาก goal ทันที | ถัดจากบล็อก Sectors (goal + 1) | เหตุผลเดียวกัน |

สมดุลคอลัมน์ (≤15% / ≤35%): ไม่ผ่อนเกณฑ์ — ตอนยังไม่ follow บล็อก Sectors เป็นบรรทัดเดียว (.sd-slim) ไม่กินที่ · บล็อกการ์ดเต็มเฉพาะเมื่อมี sector ที่ follow
| run_tests_phase56.py | 9 ตั้งค่า: ดัชนีแถวงานรายสัปดาห์ (เพิ่มเอง · ปิด · ลบ · จำนวนหลังลบ) | 4 / 3 / 4 / 4 | 5 / 4 / 5 / 5 | งานเริ่มต้นเพิ่ม 1 ข้อ (wsector) เลื่อนดัชนี |
