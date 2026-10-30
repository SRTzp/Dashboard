# LN1 — เทสเก่าที่แก้ความคาดหวัง

ไม่มีเคสถูกลบ · ไม่มีเคสถูกทำให้อ่อนลง · สำรองไฟล์เดิมไว้ที่ `tests/_bk_ln1/`

| ไฟล์ | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| run_tests_phase77.py | 1 ตั้งค่า › Sat v2: ค่าเริ่มต้นครบ 21 ช่อง | setupsMain = `Break EMA20 / Break Weekly PoC` · setupsTac = `Break EMA50 / Break Daily PoC` | `Break EMA20 / Break PoC Week` · `Break EMA50 / PoC Support` | brief LN1 §2: เปลี่ยนค่าเริ่ม Setup ใน SAT_V2_DEF |
| run_tests_phase77.py | 3 การ์ด Tactical: Setup ค่าเริ่ม | `["Break EMA50","Break Daily PoC"]` | `["Break EMA50","PoC Support"]` | เหมือนกัน |
| run_tests_phase77.py | 4 การ์ด Main: Setup ค่าเริ่ม | `["Break EMA20","Break Weekly PoC"]` | `["Break EMA20","Break PoC Week"]` | เหมือนกัน |

## Fixture (ไม่ใช่การแก้ความคาดหวัง)
- `tests/ff_stub.py`: เดิม `FF_STUB` อย่างเดียว · ตอนนี้ `FF_STUB = seed โหมด "แบบเดิม" (localStorage ln1_plan_view=legacy) + FF_STUB_BASE` — ทุก launcher ที่ใช้ FF_STUB (ชุดเก่าทั้งหมด) จึงรันกับหน้า PV2c เดิม · phase80 ตั้ง `ff_stub.FF_STUB = FF_STUB_BASE` เพื่อทดสอบค่าเริ่ม Lean
- ไฟล์สำรอง: `tests/_bk_ln1/ff_stub.py`

## พฤติกรรมที่เปลี่ยนโดยตั้งใจ (นอกหน้าจอ Lean)
- `satwSetBias(asset, b, extra)` รับช่องเสริม (trend_dir) · `satV2NewPlan`: Bias Neutral + ไม่มี Main ค้าง → ทิศตาม `trend_dir` (down = Short · อื่น ๆ = Long เหมือนเดิม) — ข้อมูลเก่าไม่มี trend_dir จึงเหมือนเดิม
