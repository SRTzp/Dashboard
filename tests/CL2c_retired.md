# CL2-c — ตารางเคสที่เลิกใช้/แก้ (tests)

## ก) เคสที่เลิกใช้ (พิมพ์ `RETIRED - …` · ไม่นับใน PASS/FAIL)
| phase | เคส | เหตุผล | จำนวน (รวม 2 viewport) |
|---|---|---|---|
| phase1 | new trade: tPort มีแค่ core · ไม่มี option hidden | ลบฟอร์ม Add Trade (#tPort/acctSyncPortSelect) | 4 |
| phase1 | retroactive closed: tPort = core+satB · ป้าย satB = Sat | ลบ openUnplannedClosed | 4 |
| phase1 | เปิดไม้ใหม่ต่อจากแก้ไม้ satB แล้ว satB ไม่หลุดกลับมา | ลบ tradeAllowSatB | 2 |
| phase16 | B ดู fam กด ＋ Closed นอกแผน → ฟอร์มเป็นของ fam | ลบปุ่ม/ฟอร์ม | 2 |
| phase16 | B บันทึกแล้วไม้ไปอยู่ใน fam (closed นอกแผน) | ลบ saveTrade (สร้างไม้ผ่านฟอร์ม) | 2 |
| phase20 | ปุ่ม ＋ แถบบน · ขนาดปุ่ม ＋ · กดปุ่ม ＋ เปิดฟอร์ม · กด T เปิดฟอร์ม | ลบปุ่ม ＋ / ปุ่มลัด T | 8 |
| phase20 | Add Trade บันทึกไม้ core ใหม่ · SZ: szRenderCard ไม่ error | ลบฟอร์ม / szRenderCard | 4 |

## ข) เคสที่แก้ให้ใช้ทางใหม่ (จำนวนเคสเท่าเดิม)
| phase | เคส | สิ่งที่แก้ |
|---|---|---|
| phase1 | แก้ไม้ satB เดิม (2 เคส) | ตรวจหัวหน้าต่างแก้ไม้ (Port = Sat อ่านอย่างเดียว) + Port ยัง satB หลัง saveTradeEdit แทนตัวเลือกใน #tPort |
| phase3 | แถว open: ปุ่ม แก้ SL | ตรวจ `openTradeEdit(` แทน `editTrade(` |
| phase8 | เพดาน Core ทุกจุด (5 เคส) | ตัดส่วน "บรรทัด sizing ใน Add Trade" ออก เหลือแถบดำ = szTargetRisk = Port Heat = ตั้งค่า Sizing |
| phase13 | Journal แตะแถวข้อมูลไม่ครบ (2 เคส) | ใช้ #teOverlay / teCtx.acct แทน #tradeOverlay / formAcct (jIncGo → openTradeEdit) |
| phase16 | B ดู fam กดแก้ไข | ตรวจ teCtx.acct + หัวแสดง Family แทน formAcct/#tAcct |
| phase20 | คะแนนวินัย/Setup ในฟอร์มแก้ไม้ + แก้แล้วบันทึก (2 เคส) | openTradeEdit / saveTradeEdit |

## ค) นับเคส ก่อน → หลัง
| ชุด | ก่อน | เลิกใช้ | หลัง | ผลต่าง = เลิกใช้ |
|---|---|---|---|---|
| run_tests | 52 | 0 | 52 | ✓ |
| p1 | 30 | 10 | 20 | ✓ |
| p2 | 54 | 0 | 54 | ✓ |
| p3 | 78 | 0 | 78 | ✓ |
| p4 | 47 | 0 | 47 | ✓ |
| p5 | 124 | 0 | 124 | ✓ |
| p6 | 114 | 0 | 114 | ✓ |
| p7 | 47 | 0 | 47 | ✓ |
| p8 | 115 | 0 | 115 | ✓ |
| p9 | 155 | 0 | 155 | ✓ |
| p10 | 11 | 0 | 11 | ✓ |
| p11 | 196 | 0 | 196 | ✓ |
| p12 | 138 | 0 | 138 | ✓ |
| p13 | 103 | 0 | 103 | ✓ |
| p14 | 192 | 0 | 192 | ✓ |
| p15 | 87 | 0 | 87 | ✓ |
| p16 | 133 | 4 | 129 | ✓ |
| p17 | 52 | 0 | 52 | ✓ |
| p18 | 84 | 0 | 84 | ✓ |
| p19 | 145 | 0 | 145 | ✓ |
| p20 | 95 | 12 | 83 | ✓ |
| p21 (ใหม่) | – | – | 168 | – |
