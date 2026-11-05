# PF3 — Report back

PF3 เสร็จตามที่สั่งเกือบทั้งหมด ชุดเต็ม `tests/runall2.sh` (base + phase 1–103) ผ่าน 100/104 suite · ที่ล้ม 4 ตัว: p5, p13 (รู้อยู่แล้ว), **p23 (regression จาก WM1)**, **p94 (เกณฑ์ 15% ที่ fixture นั้นเป็นไปไม่ได้ ไม่ได้ลดเกณฑ์)** · ไม่ push · ไม่ลบไฟล์ · ไฟล์ verify: `docs/reports/PF3-verify.txt`

## 1. weeklyImpact/v2 — enum/ฟิลด์
- `kind` เพิ่ม `event` → release / decision / speech / event / carryover
- `status` ชุดเดิมรับครบ 5 ค่าอยู่แล้ว (scheduled / released / ongoing / postponed / cancelled) จึงแค่เรียงใหม่ ไม่มีค่าไหนถูกตัด
- ฟิลด์ใหม่เก็บผ่าน import → save → reload: `previous_period` (ข้อความ ≤40 | null) · `source_refs` (string[] ทุกตัวต้องอยู่ใน `sources`) · `src_actual` (null ได้ · ตรวจเมื่อมีค่า)
- ข้อมูลเดิมไม่มีฟิลด์เหล่านี้ → normalise เป็น null / null / [] ไม่ถูกปฏิเสธ · `src_previous` ยังถูกตรวจเหมือนเดิม (ไม่ได้อยู่ในรายการของ Part A แต่เป็นพฤติกรรมเดิม)
- `scenarios_th`: เก็บ `label_th` (trim ≤80 · ว่าง = ไม่เก็บ) · ป้าย = `wiScLabel()`: label_th → ตารางไทย → 'กรณีอื่น' (ไม่โชว์ key ดิบ · กัน key ชื่อ `toString`/`__proto__`) · `occurs`=เกิดขึ้น · delayed=เลื่อนออกไป · escalates=ตึงเครียดขึ้น · eases=คลี่คลายลง · `post`=หลังประกาศผล (เดิม 'สิ่งที่ควรดูหลังประกาศ') · คง above/below/inline และ hawkish/dovish/expected ที่มีอยู่
- `ครั้งก่อน (Sep 2026)` แสดงใน 3 จุด (การ์ดเหตุการณ์ · บรรทัดย่อใน Today · ฟอร์มกรอกผล) · ไม่มี period = `ครั้งก่อน` เหมือนเดิม
- แก้ `docs/weekly-impact-schema.md` · Firestore rules ไม่ต้องแก้ · fixture "ใหม่" ใน phase103 ทำตามรูปที่ skill `weekend-macro-update` ส่ง (ไม่ได้ดึงไฟล์ผลลัพธ์จริงของ skill)

## 2. Today Mac
ฟังก์ชัน `tdBalance()` (index.html) หลังวาด Today: ถ้าคอลัมน์ซ้ายยาวกว่าขวาเกิน 15% (วัดก้นคอลัมน์ เหมือนเทส) และการย้ายทำให้สมดุลดีขึ้น → ย้ายการ์ดแผน Sat ไปขวา หลังเป้าหมาย Port ก่อนการบ้านหุ้น · ตรวจซ้ำตอน resize (debounce 150ms) และเมื่อเปิดแท็บที่วาดไว้ตอนซ่อน · ถ้าอยู่ถูกที่แล้วไม่แตะ DOM · จอ <1000px ลำดับเดิม คืน 15% ใน phase94/102 (บันทึกใน `tests/PF3_retired.md`)

| fixture (Mac) | ก่อน ซ้าย/ขวา | หลัง ซ้าย/ขวา | Sat |
|---|---|---|---|
| long (4 Asset ไม่มีแผน · การ์ด 316–334px) 1280 | 1260/704 (44.1%) | 915/1048 (12.7%) | ขวา |
| long 1440 | 1242/704 (43.3%) | 915/1030 (11.1%) | ขวา |
| short (1 Asset มีแผน · ไม่มีข่าว · Re-check Macro ถึงกำหนด) 1280 | 859/801 (6.8%) | เดิม | ซ้าย |
| short 1440 | 841/801 (4.8%) | เดิม | ซ้าย |
| short+ข่าววันนี้ 1280 / 1440 | 1085/704 (35.1%) / 1067/704 (34.0%) | 915/873 (4.6%) / 915/855 (6.6%) | ขวา |
| **phase94 fixture** 1280 / 1440 | 1034/704 (31.9%) / 1016/704 (30.7%) | ไม่ย้าย (ย้ายแล้วแย่กว่า ≈ 32%) | ซ้าย |

หมายเหตุ: การ์ด Sat สูงตามจำนวน Asset ที่ยัง*ไม่มีแผน* ไม่ใช่ที่มีแผน (4 Asset ที่มีแผนครบเหลือแค่ ~66px) จึงใช้ "4 Asset ไม่มีแผน" เป็น long · short ที่ไม่มีข่าว + Re-check ถึงกำหนดจึงอยู่ที่เดิมและ ≤15% · ถ้า short มีข่าววันนี้ด้วย ซ้ายยาวกว่าอยู่ดีจึงย้ายตามกติกา (ต่างจากที่ brief คาดว่า short = ที่เดิม) · **phase94 ล้มที่ 15%**: fixture ไม่มีข่าว/Weekly Stock Summary ฝั่งขวา ซ้ายมีช่วงเวลา 452px จึงเป็นไปไม่ได้ด้วยการย้ายการ์ด Sat อย่างเดียว ไม่ได้ผ่อนเกณฑ์

## 3. เคส PF1 ที่ retire (คืนครบ)
`pf1_retire.py` เหลือ 0 ผู้เรียก (ลบ import ออกทั้ง 29 ไฟล์ · ไฟล์ยังอยู่) · ชุดเต็มไม่มีบรรทัด `RETIRED(PF1)` เลย · brief บอก 132 · ที่นับได้จริง: 80 จุดเรียก / 126 เช็ก (ขยาย loop) ใน 29 suite (4 suite — 37, 60, 63, 71 — มีแค่ import ไม่มีการเรียก) · ต่อ run พิมพ์ RETIRED(PF1) 307 บรรทัด (หลาย viewport) · เลข 132 ของ brief ผมยืนยันไม่ได้ว่านับยังไง
| suite | call sites | checks (loops expanded) | RETIRED(PF1) lines/run (ก่อน) |
|---|---|---|---|
| phase2 | 9 | 9 | 18 |
| phase4 | 1 | 1 | 2 |
| phase5 | 4 | 4 | 8 |
| phase8 | 1 | 1 | 2 |
| phase11 | 13 | 13 | 26 |
| phase14 | 6 | 6 | 18 |
| phase15 | 1 | 1 | 2 |
| phase27 | 2 | 2 | 4 |
| phase34 | 1 | 1 | 2 |
| phase36 | 1 | 1 | 2 |
| phase37 | 0 | 0 | 0 |
| phase38 | 2 | 2 | 4 |
| phase39 | 1 | 1 | 3 |
| phase54 | 1 | 1 | 2 |
| phase55 | 2 | 2 | 4 |
| phase56 | 9 | 9 | 18 |
| phase59 | 3 | 3 | 6 |
| phase60 | 0 | 0 | 0 |
| phase63 | 0 | 0 | 0 |
| phase69 | 1 | 1 | 2 |
| phase71 | 0 | 0 | 0 |
| phase78 | 7 | 7 | 14 |
| phase79 | 2 | 2 | 4 |
| phase80 | 1 | 9 | 18 |
| phase81 | 1 | 6 | 12 |
| phase82 | 5 | 22 | 66 |
| phase90 | 3 | 3 | 7 |
| phase93 | 2 | 14 | 48 |
| phase96 | 1 | 5 | 15 |
| **รวม 29 suite** | **80** | **126** | **307** |

คืนด้วยวิธี: พฤติกรรม PF1 ใหม่ (เช่น งาน Weekly 'ทำแผน Sat สัปดาห์นี้' กดเอง · ไม่มีปุ่ม Bias · ฟอร์มมี Zone Activation · ไม้เติม/บันทึกไม่ถูกบล็อกสวน Bias · แผนใหม่ Trend ว่าง) หรือ absent-check (ไม่มี Trend/Flat/Zone/Shift/ประวัติสลับ/ปุ่ม Neutral/งดเทรด) ที่จุดเดิม ชื่อเช็กขึ้นต้น `PF3` · ตารางข้อต่อข้ออยู่ท้าย `tests/PF1_retired.md` (+85 บรรทัด)

## 4. regression
- **ที่พบในเคส PF1 ที่คืน:** ไม่มีบั๊กโค้ด · ที่ต่างจากของเดิมอธิบายได้ด้วย PF1: p56 (ต้องทำ 3→2 · Trading Plan US 2→1 จากงาน Bias ที่ถอด) · ที่เหลือเป็นความผิดของเช็กที่ผมเขียนเองแล้วแก้ในรอบ
- **p23 = regression จริง ไม่ใช่ของเดิมตั้งแต่ก่อน PF1:** ผมรันบน `index.backup-pre-PF1.html` ผ่าน 123/0 (pre-PF2, pre-WM1 ก็ผ่าน · pre-WM1b ล้ม) → เกิดใน WM1 · สาเหตุ: `wiRefreshAll()` (listener weeklyImpact snapshot แรก) เรียก `satV3Render()` → `satCarrySync` → `satWeekPickWrite` ทำให้เขียนเอกสารผู้ใช้เป็นครั้งที่ 2 (~400ms หลังเขียน migration) · **ยังไม่ได้แก้** (นอกขอบเขต PF3 และกระทบทั้งหน้า Strategy) · แนวทางแก้: ให้ `wiRefreshAll` วาด Strategy เมื่อแท็บแผนเปิดอยู่ ที่เหลือติดธงแล้ววาดตอนเปิดแท็บ หรือให้ carry-sync รวมกับ persist ที่รออยู่ — ขอให้สั่งถ้าจะให้แก้
- **p5:** ล้มบน pre-PF1 เหมือนกัน (Break Price 2 เคส · 122/124) = ของเดิมจริง
- p13 ล้มหลอกตามที่รู้

## 5. ผลชุดเต็ม
base + phase 1–103 = 104 suite · ผ่าน 100 · ล้ม p5 · p13 · p23 · p94 (หลังรันซ้ำเดี่ยวแล้ว) · phase103 ใหม่ 114/114 · core_size_test 471/471 · check_syntax OK · sync_core_size OK

## 6. ไฟล์ที่แก้
index.html (+42/−13) · docs/weekly-impact-schema.md · tests/run_tests_phase103.py (ใหม่) · แก้ 31 ไฟล์ run_tests_phase*.py (ส่วนใหญ่ลบ import + คืนเช็ก; 94/102 คืน 15% และสลับลำดับคอลัมน์) · tests/PF3_retired.md · tests/PF1_retired.md · tests/runall2.sh (→103) · tests/make_verify.sh · ไฟล์ที่ห้ามลบ.md · backup: index.backup-pre-PF3.html · tests/_bk_pf3/

## 7. ภาพ (เปิดดูครบ 5)
pf3-today-long-1440 · pf3-today-short-1440 · pf3-today-390 ดูถูกต้อง · pf3-wi-event-390 ถูกต้อง (ป้ายสถานการณ์ครบ) · pf3-wi-event-1440 เนื้อหาถูกต้องแต่ภาพออกสีจาง/เทา — น่าจะเป็นอนิเมชันหรือฉากหลังตอนถ่าย ผมยังไม่ได้หาสาเหตุ

## 8. ข้อจำกัด
วัดบน Chromium เท่านั้น · เทสความสมดุลวัดที่ก้นคอลัมน์ตามเกณฑ์เดิมของเทส (ไม่ใช่ความสูงจริง) · ตัวเลข 132 ใน brief ยืนยันไม่ได้
