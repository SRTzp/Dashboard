# CL2-a — ตารางเคสที่เลิกใช้/แก้ (tests)

## ก) เคสที่เลิกใช้ (พิมพ์ `RETIRED - …` ในเอาต์พุตของแต่ละชุด · ไม่นับใน PASS/FAIL)

| phase | เคส | เหตุผล | จำนวน (รวมทุก viewport) |
|---|---|---|---|
| run_tests.py | §0.7 SAT_V3_ON exists (7D.3 Phase 4: ตั้งเป็น true แล้ว — หน้า Sat ใหม่ mount จริง) | CL2-a ลบค่าคงที่ SAT_V3_ON (ทางเดียวที่เหลือ = v3) | 2 |
| run_tests.py | §0.7 SAT7D_ON (old switch) untouched, still true | CL2-a ลบค่าคงที่ SAT7D_ON | 2 |
| phase1 | แก้ไม้ satA เดิม: satA ยังอยู่ใน tPort ให้แก้ได้ (ไม่ถูกลบทิ้งไปด้วย) | CL2-a ลบ Sat.A — ไม่มีไม้ satA ให้แก้ | 2 |
| phase1 | แก้ไม้ satA เดิม: ค่าที่เลือกอยู่ยังเป็น satA (ไม่ถูกเปลี่ยนค่าเงียบ ๆ) | CL2-a ลบ Sat.A — ไม่มีไม้ satA ให้แก้ | 2 |
| phase1 | แก้ไม้ satA เดิม: satB ไม่ถูกเสนอเป็นตัวเลือก (ไม่ได้กำลังแก้ไม้ satB) | CL2-a ลบ Sat.A — ไม่มีไม้ satA ให้แก้ | 2 |
| phase4 | SAT_V3_ON === true ในไฟล์ทดสอบ | CL2-a ลบค่าคงที่ SAT_V3_ON (ทางเดียวที่เหลือ = v3) | 2 |
| phase4 | SAT_V3_ON === false (ค่าจริงในไฟล์ก่อนขึ้นจริง) | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | SAT_V3_ON=false -> หน้า 7D.2 เดิม (#sat7dPanel โชว์) · #satV3Panel ถูกซ่อน · ไม่มี error | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | หน้า 7D.2 เดิมมีครบ: ปุ่ม ＋ไอเดียใหม่ / s7NewAsset / s7Sum (การ์ดสรุปเดิม) | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | scope future: การ์ด Satellite.B/Sat เดิม (.ports) ยังโชว์ปกติเหมือนก่อน Phase 4 (ไม่ตัดตอน false) | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | ไม่ล้นแนวนอน (scrollWidth <= 1440) หน้า fallback เดิม | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 1 |
| phase4 | §A Core (scope stock) หัว Core เป็น .sumBlk ก้อนเดียว (ไม่มี ui-acctStrip) · ฟิลด์ครบ ทุน/% ของทุนรวม/Open Risk/Planned/Positions/Heat 1R · ค่าเท่ากับก่อน UI-1b | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | satA อยู่ในบล็อกสรุปก้อนเดียวกัน (.sumBlk) · ฟิลด์ครบ · ค่าเท่ากับการ์ด satA เดิมก่อน UI-1b | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | console: zero error-level messages | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | console: zero uncaught page errors | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 2 |
| phase4 | ไม่ล้นแนวนอน (scrollWidth <= 430) หน้า fallback เดิม | CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด) | 1 |
| phase14 | หุ้น (ปกติ): satA — ตัวเลขทุกค่าก่อน-หลังเท่ากัน | CL2-a ลบ Sat.A — ไม่มีบล็อก satA ในแท็บหุ้นแล้ว | 3 |
| phase14 | หุ้น (เกิน limit): satA — ตัวเลขทุกค่าก่อน-หลังเท่ากัน | CL2-a ลบ Sat.A — ไม่มีบล็อก satA ในแท็บหุ้นแล้ว | 3 |
| phase16 | B main มี satA → ชิป 'เก็บถาวร' ขึ้น (ค่า filter satA) + Core + Sat | CL2-a ลบ Sat.A — ไม่มีชิป/การ์ด 'เก็บถาวร' ใน Journal แล้ว | 2 |
| phase16 | B การ์ดพอร์ต satA ชื่อ 'เก็บถาวร (Sat.A เดิม)' | CL2-a ลบ Sat.A — ไม่มีการ์ดพอร์ต satA ใน Journal แล้ว | 2 |
| phase16 | B กรอง เก็บถาวร → ตารางเหลือไม้ satA | CL2-a ลบ Sat.A — ไม่มีชิป 'เก็บถาวร' | 2 |
| phase18 | satV3Render ไม่เรียก sat7dOldPlanHtml (spy = 0) | CL2-a ลบ sat7dOldPlanHtml | 2 |
| phase18 | ฟังก์ชันเดิมยังอยู่ (ไม่ลบโค้ด) | CL2-a ลบ sat7dOldPlanHtml (ตั้งใจให้ไม่มีแล้ว) | 2 |
| phase18 | satA มีแต่ไม้ปิด (ทุน 0) → ยังไม่แสดง · Core เท่าเดิม | CL2-a ลบ Sat.A — ไม่มีบล็อก satA/ไม้ satA/ทุน satA | 2 |
| phase18 | satA มีไม้ open (ทุน 0) → แสดง · Core เท่าเดิม | CL2-a ลบ Sat.A — ไม่มีบล็อก satA/ไม้ satA/ทุน satA | 2 |
| phase18 | satA มีไม้ plan (ทุน 0) → แสดง | CL2-a ลบ Sat.A — ไม่มีบล็อก satA/ไม้ satA/ทุน satA | 2 |
| phase18 | satA ทุน > 0 → แสดง (ไม่ถูกซ่อน) | CL2-a ลบ Sat.A — ไม่มีบล็อก satA/ไม้ satA/ทุน satA | 2 |
| phase18 | Journal: ไม้ satA ที่ปิดแล้วยังมีชิป/พอร์ต 'เก็บถาวร' | CL2-a ลบ Sat.A — ไม่มีชิป/พอร์ต 'เก็บถาวร' ใน Journal | 2 |

รวมเลิกใช้ 56 เคส: run_tests.py 4 · phase1 6 · phase4 20 · phase14 6 · phase16 6 · phase18 14

## ข) เคสที่แก้ให้ใช้ core/satB หรือของใหม่ (จำนวนเคสเท่าเดิม — ไม่ใช่เลิกใช้)

| phase | เคส | สิ่งที่แก้ |
|---|---|---|
| run_tests.py | แท็บแผน (scope future) มี #sat7dPanel → #satV3Panel | #sat7dPanel ถูกลบ · ตรวจ #satV3Panel ตัวเดียว |
| phase1 | wPort: core/satA/satB ครบ → core/satB | satA ถูกลบจากพอร์ตของบัญชี |
| phase1 | เปิดไม้ใหม่ต่อจากแก้ไม้ satA → ต่อจากแก้ไม้ satB (tPort ต้องเป็น ['core']) | ไม่มีไม้ satA ให้แก้แล้ว · ยังเช็ค state ถูก reset |
| phase4 | mount ถูกจุด: #sat7dPanel ถูกซ่อน → ถูกลบออกจาก DOM | ทาง V3-off ถูกลบ |
| phase13 | ทุกเคส (seed/ข้อมูลตัวอย่าง) | ไม้ satA → core · ports ['core','satB'] · heat ['core'] |
| phase14 | ชุดข้อมูลกลาง (m4/m5 satA → core) · หัวบล็อก Core Port แถวเดียว · 👁 Core ตาเดียว · ports ตัด satA | บล็อก satA ถูกลบ |
| phase15 | round-trip: books เทียบกับ Strip ของก้อนตอน export (ไม่นับ [] ว่างของ ideas/checklistDrafts/failLog) | กู้ผ่าน cl2aStripLegacy |
| phase15 | ปุ่มเดิม phase7mRestoreFromFile → ต้องไม่มีแล้ว · ปุ่ม bkRestoreOpen ยังอยู่ | ปุ่มถูกลบตาม §1.5 |
| phase16 | ชุดข้อมูล (m5 satA → core) · ports · เคส 'เก็บถาวร→fam' ใช้ชิป core แทน | ชิป/การ์ดเก็บถาวรถูกลบ |
| phase18 | set_trades ไม่เขียนทุน satA · เคสที่ไม่เกี่ยวกับ satA/sat7dOldPlanHtml ผ่านโดยไม่แก้ | — |

## ค) ตารางนับเคส ก่อน → หลัง (จำนวนบรรทัด PASS)

| ชุด | ก่อน | เลิกใช้ | หลัง | ผลต่าง = เลิกใช้ |
|---|---|---|---|---|
| run_tests.py | 56 | 4 | 52 | ✓ |
| phase1 | 42 | 6 | 36 | ✓ |
| phase2 | 54 | 0 | 54 | ✓ |
| phase3 | 78 | 0 | 78 | ✓ |
| phase4 | 67 | 20 | 47 | ✓ |
| phase5 | 124 | 0 | 124 | ✓ |
| phase6 | 114 | 0 | 114 | ✓ |
| phase7 | 47 | 0 | 47 | ✓ |
| phase8 | 115 | 0 | 115 | ✓ |
| phase9 | 155 | 0 | 155 | ✓ |
| phase10 | 11 | 0 | 11 | ✓ |
| phase11 | 196 | 0 | 196 | ✓ |
| phase12 | 138 | 0 | 138 | ✓ |
| phase13 | 106 | 0 | 106 | ✓ |
| phase14 | 198 | 6 | 192 | ✓ |
| phase15 | 87 | 0 | 87 | ✓ |
| phase16 | 141 | 6 | 135 | ✓ |
| phase17 | 58 | 0 | 58 | ✓ |
| phase18 | 104 | 14 | 90 | ✓ |
| phase19 (ใหม่) | — | — | 145 | — |
