# CL2-b — ตารางเคสที่เลิกใช้/แก้ (tests)

## ก) เคสที่เลิกใช้ (พิมพ์ `RETIRED - …` ในเอาต์พุต · ไม่นับใน PASS/FAIL)

| phase | เคส | เหตุผล | จำนวน (รวมทุก viewport) |
|---|---|---|---|
| phase1 | wPort: ยังมี core/satB ครบ (CL2-a: satA ถูกลบจากพอร์ตของบัญชี) ไม่ใช้กฎ satA-ไม้ใหม่ | CL2-b ลบฟอร์ม Watchlist เดิม (#wPort/#watchOverlay/toggleWBiasField) — acctSyncPortSelect ยังถูกเทสผ่าน #tPort | 2 |
| phase1 | wPort: ไม่มี <option hidden> หลงเหลือ | เหมือนข้างบน | 2 |
| phase1 | wPort: ป้าย satB = 'Sat' | เหมือนข้างบน | 2 |
| phase13 | Journal: แตะแถว missed → เปิดโมดัลเหตุผล · โฟกัสช่องแท็ก | CL2-b ลบ Missed ทั้งระบบ (ไม่มีแถว missed ใน 'ข้อมูลไม่ครบ' · ไม่มี #missedOverlay) | 3 |
| phase16 | B ★ ดู fam กดแก้ Missed → โมดัลเป็นของ fam (ไม้ FMISS) | CL2-b ลบ Missed ทั้งระบบ (ไม่มีพาเนล/โมดัล Missed ใน Journal) | 2 |

รวมเลิกใช้ 11 เคส: phase1 6 · phase13 3 · phase16 2

## ข) เคสที่แก้ให้ใช้ทางใหม่ (จำนวนเคสเท่าเดิม — ไม่ใช่เลิกใช้)

| phase | เคส | สิ่งที่แก้ |
|---|---|---|
| phase13 | Journal: นับถูก แยกบัญชี — main 3 → 2 · ช่องที่ขาดระบุถูก · แถบส้ม "ข้อมูลไม่ครบ n รายการ" · กางแล้วเห็นรายการ | ไม้ missed (b2/NOWHY) ไม่ถูกนับแล้ว (JINC_STATUS ตัด missed) → คาดหวัง 2 รายการ (exit + เหตุผลยกเลิก) |
| phase13 | แตะ Hold (fam): เลื่อนถึงตารางบัญชี fam | ลบแผง Ideas/Checklist ใต้ตารางแผน หน้าสั้นลง → รับกรณีเลื่อนสุดหน้าแล้ว (atBottom) และรอให้ smooth scroll นิ่งก่อนวัด (เดิมรอ 900ms คงที่) · ยังต้องอยู่ในจอ |
| phase16 | B ปุ่มในแถวทุกปุ่ม … ส่ง account 'fam' | ตัดตัวเลือก #missedTbody/#missedCards (closed/cancel เท่านั้น) |
| phase16 | B ★ ดู fam กด Restore Cancel → FCANC กลับ plan · FMISS (missed เก่า) ไม่ถูกแตะ | เดิม Restore ทั้ง Missed/Cancel · ตอนนี้ Cancel อย่างเดียว + ยืนยันว่าไม้ missed เก่าไม่ถูกแก้ |
| phase15 / phase19 | เทียบ books ไม่นับ [] ว่างของ ideas/checklistDrafts/failLog | ไม่ต้องแก้ — ยอมรับ [] ว่างอยู่แล้ว (ตอนนี้ไม่มี [] ถูกใส่กลับ) |

## ค) ตารางนับเคส ก่อน → หลัง (บรรทัด PASS / summary ของแต่ละชุด)

| ชุด | ก่อน | เลิกใช้ | หลัง | ผลต่าง = เลิกใช้ |
|---|---|---|---|---|
| run_tests.py | 52 | 0 | 52 | ✓ |
| phase1 | 36 | 6 | 30 | ✓ |
| phase2 | 54 | 0 | 54 | ✓ |
| phase3 | 78 | 0 | 78 | ✓ |
| phase4 | 47 | 0 | 47 | ✓ |
| phase5 | 124 | 0 | 124 | ✓ |
| phase6 | 114 | 0 | 114 | ✓ |
| phase7 | 47 | 0 | 47 | ✓ |
| phase8 | 115 | 0 | 115 | ✓ |
| phase9 | 155 | 0 | 155 | ✓ |
| phase10 | 11 | 0 | 11 | ✓ |
| phase11 | 196 | 0 | 196 | ✓ |
| phase12 | 138 | 0 | 138 | ✓ |
| phase13 | 106 | 3 | 103 | ✓ |
| phase14 | 192 | 0 | 192 | ✓ |
| phase15 | 87 | 0 | 87 | ✓ |
| phase16 | 135 | 2 | 133 | ✓ |
| phase17 | 52 | 0 | 52 | ✓ |
| phase18 | 84 | 0 | 84 | ✓ |
| phase19 | 145 | 0 | 145 | ✓ |
| phase20 (ใหม่) | — | — | 95 | — |

หมายเหตุ: "ก่อน" วัดจาก index.backup-pre-CL2b.html รันในสำเนาโฟลเดอร์แยก (phase 6–16 ใช้ ../index.html เป็นค่าเริ่มต้น จึงรันกับไฟล์ที่กำลังแก้ไม่ได้) · ทุกชุด FAIL 0
