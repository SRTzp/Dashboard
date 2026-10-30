# AC1 — เทสเก่าที่แก้ความคาดหวัง

เหตุ: brief AC1 ตัดปุ่ม/ช่องติ๊ก `Activate` ของเงื่อนไขปกติ (ไม่ใช่ MR) ออกจาก UI — แผน Activate เองเมื่อติ๊กครบ 3 ขั้น + zone + TP + Inval
ไม่ลบเคส ไม่ทำให้อ่อนลง — ความคาดหวังเดิม (TP เริ่มต้น · active ข้อเดียว · ช่อง Entry/SL · lot · R:R · บล็อก) ยังตรวจเท่าเดิม
เคสที่เดิม "คลิกปุ่ม Activate" เปลี่ยนเป็นเรียก `satV3CondActivate(ideaId, condId, true)` ตรง ๆ (ตัวทำงานเดิมที่ UI ใหม่ก็เรียก) เพราะเคสนั้นไม่ได้ทดสอบ UI ติ๊ก (UI ใหม่ทดสอบใน phase60)
สำรองต้นฉบับไว้ที่ `_bk_ac1/`

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase4 | 7D.4 Activate แล้วมีช่อง Entry/SL | คลิก `.ui-cond-act input` | เรียก `satV3CondActivate` ตรง (ข้อแรก) | ไม่มีช่อง Activate แล้ว |
| phase5 | ขั้นหน้างาน กด [เปิด] → การ์ดกาง (ยังไม่ Activate) | `.ui-cond-act` = 2 | `.ui-cond[data-cond] .ui-ac` = 2 และ `.ui-cond-act` = 0 | 2 เงื่อนไขยังอยู่ครบ แต่แทนช่อง Activate ด้วยแถวชิป |
| phase5 | Activate A / Activate B (ย้าย) / ข้อ Short TP กรอกกลับด้าน | คลิก checkbox / ปุ่ม [ใช้ข้อนี้] | เรียก `satV3CondActivate` ตรง | ไม่มีปุ่มแล้ว · ค่าที่คาด (TP 2700 / 2680 / 4600) เท่าเดิม |
| phase6 | แถว A มี `[Activate] [ยกเลิก]` | "Activate" in แถว | "Activate" **ไม่อยู่** ในแถว + ยังมี `ยกเลิก` | AC1 ตัดปุ่ม |
| phase6 | [Activate] จากแถว / [ใช้ข้อนี้] / Activate ข้อไม่มี TP zone | คลิกปุ่ม | เรียก `satV3CondActivate` ตรง | ค่าที่คาดเท่าเดิม |
| phase6 | แตะ ▸ → แถวสั้นข้อ B | มี `ใช้ข้อนี้` · `ยกเลิก` | ไม่มี `ใช้ข้อนี้` · มี `ยกเลิก` | ข้อ B เปลี่ยนสถานะด้วยการติ๊ก (แก้ในที่ใต้แถว) |
| phase7 | Activate จากแถวพับ (ล่างสุด) · Activate P1 | คลิก `.ui-wc-act` | เรียก `satV3CondActivate` ตรง | ไม่มีปุ่มแล้ว · เลื่อนจอ/ลำดับกลุ่มยังตรวจเท่าเดิม |

## ที่ไม่ต้องแก้
- เคส MR (phase27 · phase34 · phase42) — ข้อ MR (`kind:'mr'`) ยังใช้ checkbox/ปุ่ม Activate เดิม (AC1 พูดถึงเงื่อนไข Break & Pullback เท่านั้น)
- เคสที่ใส่ fixture `active:true` แบบไม่มี `kind`/`steps` (ST1 · SR1 · AS1 · PY1 ฯลฯ) — ข้อเก่าอ่านเป็นติ๊กครบ ยัง active ไม่ต้องแก้

## ไม่เกี่ยวกับ AC1
- phase13 ล้มมาตั้งแต่ก่อน GL1 (ต้องใช้ `index.backup-pre-UI1.html` ที่ไม่มีอยู่)
