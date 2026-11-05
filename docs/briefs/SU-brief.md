# SU — "Setup ไม่ครบ" แยกจาก "นอกแผน" (แผน Sat ทุกแบบ) · เทส 30

> รอบเล็ก (ต่อจาก v1) · ผู้ใช้ตัดสิน 1 ต.ค.: Setup ไม่ถึงเกณฑ์ (65%) **ไม่ใช่ "นอกแผน"** → ป้าย **"Setup ไม่ครบ"** · ใช้กับแผน Sat ทุกแบบ (ปกติ + MR) · ไม่นับในสถิติ/ตัวกรองนอกแผน · มีตัวกรองของตัวเองใน Journal
> สำรองก่อนแก้: `index.backup-pre-SU.html` · **ห้ามแตะ** Core · core-size.js · Calc.setupPass/เกณฑ์ 65% · ขนาดไม้/heat/โควตา · หน้าตาการ์ด Sat (เปลี่ยนแค่ข้อความ)
> เลขบรรทัดอ้างจากไฟล์หลัง 7E-4 (997,849 bytes) — ใช้ชื่อฟังก์ชันเป็นหลัก

## ความหมายหลังแก้
| กรณี | `unplanned` (นอกแผน) | `setup_incomplete` (ใหม่) |
|---|---|---|
| Setup ไม่ถึงเกณฑ์ อย่างเดียว | false | **true** |
| บัญชีไม่ ready แล้วกด "รวมด้วย (นอกแผน)" (heat/โควตา/Bias ฯลฯ) | true (เดิม) | ตาม Setup |
| ไม้ย้อนหลัง · ไม่อยู่ Watchlist ฯลฯ | ตามกติกาเดิม | false |

## แก้
1. `makeTradeObject` (~7898): field ใหม่ `setup_incomplete` = `!!o.setupIncomplete` · ไม่ส่ง + มี `prevTrade` → คงค่าเดิมของ prevTrade · ไม่ส่งและไม่มี prev → false (ไม้เก่า/ไม้ Core ไม่มีผล)
2. `satV3SaveSlot` (~10398): `offplanOverride: !su.pass` → **`offplanOverride: false`** + `setupIncomplete: !su.pass`
3. `satV3SaveOffplanAccount` (~10430): คงธงนอกแผนเดิม (บัญชีไม่ ready) + ส่ง `setupIncomplete: !su.pass` เพิ่ม
4. ข้อความ: `satV3SetupLabel` → `Setup 2/3 · ต่ำกว่า 65% = Setup ไม่ครบ` · แก้คอมเมนต์ที่บอก "setup ไม่ครบ = นอกแผน" (~8927 · ~10349 · ~10379) · grep `= นอกแผน` ให้ครบ — **ไม่แตะ** เส้นทาง 7D.2 เดิม (`sat7dCalc` / `c.offplan` ~9208) และปุ่ม "รวมด้วย (นอกแผน)" (นั่นคือนอกแผนจริง)
5. ป้าย: helper `tradeSetupInc(t)` = `!!t.setup_incomplete` · ชิป **"Setup ไม่ครบ"** (สีเหลือง/ส้มอ่อน · คลาสใหม่ ต่างจาก `.offplan`) ทุกจุดที่แสดงป้ายนอกแผนของไม้: Positions (แถว + การ์ดมือถือ · `posSymHtml`) · Journal แถว Closed / หัวกลุ่ม / การ์ดมือถือ · การ์ดไม้ Sat ที่เปิดอยู่ · ไม้มีทั้งสองธง = แสดงทั้งสองชิป
6. Journal:
   - ชิปตัวกรองใหม่ **"Setup ไม่ครบ"** (ต่อจาก "นอกแผน" · `jFilter==='setupinc'` → `rows.filter(tradeSetupInc)`)
   - สถิตินอกแผน (`offList`/`nOffPlan` ~4688 · บรรทัดเตือน ~6673) ใช้ `tradeOffPlan` เหมือนเดิม → ไม้ Setup ไม่ครบอย่างเดียวไม่ถูกนับแล้ว
   - (เล็ก) ถ้ามีไม้ Setup ไม่ครบในช่วงที่ดู และไม่มีบรรทัดเตือนอื่นสำคัญกว่า → บรรทัดสรุป "Setup ไม่ครบ n ไม้ · P&L ฿x — ดูชิป Setup ไม่ครบ" (ลำดับความสำคัญต่ำกว่านอกแผน)
7. ข้อมูลเก่า: ไม่ migrate (ผู้ใช้ยังไม่เริ่มใช้จริง · ไม้ Sat เก่าที่ `unplanned:true` คงเดิม)

## เทส `tests/run_tests_phase30.py` (Chromium · 1440 + 430)
1. แผน Sat ปกติ Setup 0/3 · บัญชี ready → บันทึก order → `unplanned:false` · `setup_incomplete:true` · Positions มีชิป "Setup ไม่ครบ" · ไม่มี "นอกแผน"
2. Setup 2/3 (≥ 65%) → ทั้งสองธง false · ไม่มีชิป
3. MR (7E-4) Setup 0/3 → `setup_incomplete:true` · `unplanned:false` · ชิป "MR · สวน Bias" + "Setup ไม่ครบ"
4. บัญชีไม่ ready (โควตาเต็ม) → กด "รวมด้วย (นอกแผน)" + Setup 0/3 → `unplanned:true` + `setup_incomplete:true` · เห็นทั้งสองชิป
5. ข้อความขั้นหน้างาน = "Setup 0/3 · ต่ำกว่า 65% = Setup ไม่ครบ" · ไม่มีคำ "= นอกแผน" ในการ์ด Sat
6. Journal: ตัวกรอง "Setup ไม่ครบ" เห็นเฉพาะไม้ข้อ 1/3/4 · ตัวกรอง "นอกแผน" เห็นเฉพาะข้อ 4 (+ ไม้ย้อนหลัง) · `nOffPlan` ไม่นับข้อ 1/3
7. แก้ไม้ (openTradeEdit) ของไม้ข้อ 1 แล้วบันทึก → `setup_incomplete` ยัง true
8. ไม้ Core / ไม้ย้อนหลัง → `setup_incomplete:false`
9. 430px ไม่ล้นแนวนอน · ชิปสองตัวในแถว Positions มือถือไม่ทับกัน
- ภาพ `tests/screenshots/su-*`: positions-chips · journal-filter · sat-active-label (1440 + 430)

## เทสเก่า
- เคสที่คาด "นอกแผน" จาก Setup ไม่ครบ (หา `= นอกแผน` · `unplanned` ในชุด Sat เช่น phase 12/15/17/18/20/27) → **แก้ความคาดหวังของเคส (ห้ามลบ ห้ามปล่อยล้ม)** และจดใน `tests/SU_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- รันครบ: check_syntax · sync_core_size --check · run_tests + phase ทั้งหมด

## รายงานกลับ
จำนวนเคสก่อน → หลัง · ตารางจุดที่แก้ข้อความ/ธง · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
