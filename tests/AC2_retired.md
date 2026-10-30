# AC2 — เทสเก่าที่แก้ความคาดหวัง

เหตุ: brief AC2 เปลี่ยนการ์ดเงื่อนไขเข้า Sat เป็นแถวกรอกตัวเลข (ปิดแท่ง 4H|D → Break Price ▲▼ → Break Vol ▲▼ → Pullback · ติ๊กเฉพาะหน้างาน)
ตัด: ช่องข้อความเงื่อนไข · ชิปปุ่มลัด · `+ เพิ่มเอง` · `✎ แก้รายการ` · บรรทัด `Setup x/3 · ต่ำกว่า 65%` · ปุ่ม `ยกเลิก Activate` · แถว `Pullback zone` แยก · ปุ่ม ✎ ของแถบสรุป Active
ไม่ลบเคส ไม่ทำให้อ่อนลง — ค่าที่คาดเดิม (lot · R:R · บล็อก · TP เริ่มต้น · active ข้อเดียว · ไม้/entry_condition) ตรวจเท่าเดิม · จำนวนเคสเท่าเดิมทุกชุด
สำรองต้นฉบับไว้ที่ `_bk_ac2/` (phase3 · 4 · 5 · 6 · 7 · 30 · 60)

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase3 | การ์ดร่าง setup 0/3 → ข้อความเตือน | `Setup 0/3` + `ต่ำกว่า 65% = Setup ไม่ครบ` อยู่ใน HTML การ์ด | **ไม่อยู่**ในการ์ด + `satV3SetupsReady` n=0 total=3 pass:false + `satV3SetupLabel` ยังมีข้อความ | AC2 ตัดบรรทัด · ค่าคำนวณคงไว้ |
| phase4 | 7D.4 สร้างเงื่อนไขด้วยชิปลัด + พิมพ์ | คลิกชิป `Break & Pullback @` แล้วพิมพ์ 2650 | กรอก Break Price 2650 ในช่องของเงื่อนไขที่มากับแผนใหม่ | ไม่มีชิป/ช่องข้อความ |
| phase4 | setup ยังไม่ครบ → เตือน | HTML มี `ต่ำกว่า 65%…` | HTML ไม่มี + `satV3SetupsReady().pass===false` | เหมือน phase3 |
| phase5 | ไอเดียใหม่ conditions | `[]` | 1 ข้อ `kind:'bp'` | AC2 สร้างเงื่อนไขทันที |
| phase5 | ปุ่มลัด → โฟกัสช่องข้อความ · ข้อความ=… (2 เคส) | คลิกชิป + พิมพ์ | (ก) ไม่มีชิป/ช่องข้อความ (ข) Break Price=2650 · text='' · active=false · TP/Inval ว่าง | ไม่มีชิป · เคสเดิม 3 → 3 |
| phase5 | ข้อ B / C ('Swing back…' · 'พิมพ์เอง') | ชิป/`+ เพิ่มเอง` | เรียก `satV3CondAdd` ตรง (ข้อมีข้อความ · แผนหลายเงื่อนไขแบบเก่า) | ไม่มีชิป |
| phase5 | reload: ข้อความของเงื่อนไข | `["Break & Pullback @ 2650", "Swing…"]` | `["", "Swing back in demand zone @ 2620"]` + brk_px 2650 | ข้อ A เก็บเป็นตัวเลข |
| phase5 | S50 Short zone / BTC พิมพ์ค้างแล้วกดบันทึก | ชิป `+ เพิ่มเอง` / ชิป `Break` + พิมพ์ | ใช้เงื่อนไขที่มีอยู่ + `satV3CondEdit text` / พิมพ์ในช่อง Break Price แล้วกด [บันทึกแผน] ค้าง 300ms → `brk_px==65000` | ไม่มีชิป · ค่าคาดเดิม (กดไม่หาย · planned=true · ค่าถูกเก็บ) เท่าเดิม |
| phase5 | ✎ แก้ที่ข้อ Active | คลิก `.ui-cs-edit` | คลิกแถบ `[data-ac-bar]` | AC2 ใช้แถบแทน ✎ |
| phase5 | Setup 0/3 · 2/3 · 1/3 | อ่านข้อความจากการ์ด | ไม่มีในการ์ด + ค่าคำนวณ n/pass/label ตรงเดิม | ตัดบรรทัด |
| phase6 | `add_cond_typed` | ชิปลัด/`+ เพิ่มเอง` + พิมพ์ | ใช้เงื่อนไขว่างของแผนใหม่ (`satV3CondEdit text`) หรือ `satV3CondAdd` · ข้อความ = ข้อความชิปเดิม + ค่า | ไม่มีชิป · ข้อความที่แถวพับเหมือนเดิม (ข้อมูลเก่ามี text) |
| phase6 | แตะข้อความแถวพับ → โฟกัสช่องข้อความ | `dataset.condText == B` | โฟกัสช่อง Break Price ของข้อ B | ไม่มีช่องข้อความ |
| phase6 | บรรทัดสรุป `✅ ข้อความ · TP · Inval + ✎ + ยกเลิก Activate` | `.ui-cond-sum` | แถบ `● Active · 4H` + `TP 4,550–4,500 · Inval 4,650` · ไม่มี `ยกเลิก Activate` | AC2 (ตัวเลข fmt2 มีจุลภาค) |
| phase6 | หลังสลับ: สรุปเป็นข้อ B / ✎ เสร็จแล้ว / TP — · Inval — | อ่านข้อความใน `.ui-cond-sum` | ตรวจ `data-cond` ของแถบ + ข้อความ TP | แถบไม่แสดงข้อความเงื่อนไข |
| phase6 | [ยกเลิก Activate] | คลิกปุ่ม + ปุ่มลัดกลับมา ≥ 3 | เรียก `satV3CondActivate(..., false)` ตรง · ไม่มีชิป · เงื่อนไข 2 ข้อ | ไม่มีปุ่ม/ชิป |
| phase6 | ปุ่มลัด 7 (11 เคส) | คลิกชิป/✎ แก้รายการ/ช่องในตัวแก้ | ตรวจผ่านฟังก์ชันตรง: `satV3CondTplAdd/Rename/Remove` · ตัวแก้ `satV3CondTplEditorHtml` · เอกสาร `satConfig/conditionTemplates` ยังเขียน/อ่านเท่าเดิม · การ์ดไม่มีชิป/✎ | UI ถูกตัด · ฟังก์ชัน+เอกสาร Firestore คงไว้ตามบรีฟ |
| phase7 | [ยกเลิก Activate] คลิก | `.ui-cs-off` | `satV3CondActivate(P3b, active.id, false)` | ไม่มีปุ่ม |
| phase7 | พับการ์ดไม่เลื่อนจอ | `scrollY` เท่าเดิม | `scrollY == min(เดิม, ความสูงหน้า − จอ)` | การ์ดเตี้ยลง เบราว์เซอร์ clamp เอง |
| phase30 | ข้อความ `Setup 0/3 · ต่ำกว่า 65%…` ในการ์ด | อยู่ในการ์ด | `satV3SetupLabel` ได้ข้อความเดิม · ไม่แสดงในการ์ด | ตัดบรรทัด |
| phase60 (AC1) | ชิป 3 ตัว · ป้ายชิป · select TF · ช่อง zone จาก/ถึง | `[data-step]` ชิปข้อความ · `<select>` · `[data-ac-z]` | ช่องติ๊ก `[data-step]` + แถว `.ui-ac-nm` (Break Price · Break Vol · Pullback) · TF segmented · ช่อง Pullback เดียว | AC2 |
| phase60 | `MISS_ALL` | `ขาด: Break ราคา · … · Pullback zone · TP · Invalidation` | `ขาด: Break Price · Break Vol · Pullback · TP · Invalidation` | ตามบรีฟ |
| phase60 | ติ๊ก Break Price/Vol | ติ๊กได้เลย | กรอกตัวเลขก่อน (`lvl`) แล้วติ๊ก (fixture มี `brk_px/vol_px` เริ่ม 2400/2410) | ติ๊กได้เมื่อกรอกตัวเลข |
| phase60 | Break ครบแต่ไม่มี zone → ติ๊ก Pullback ไม่ได้ | จากช่อง zone ว่าง | ตรวจที่ `satAcPbBlock` กับข้อมูลที่ติ๊ก Break แต่ไม่มีตัวเลข = `กรอก Pullback ก่อน` · + เคสใหม่: มีตัวเลข Break → ติ๊กได้ pb_from/pb_to ยัง null | ค่าเริ่มจากกรอบ Break |
| phase60 | zone 0 → ล้างเป็น null | พิมพ์ 0 ในช่อง from | พิมพ์ `0` ในช่อง Pullback → ไม่เขียน ค่าเดิมคงอยู่ | บรีฟ: รูปแบบผิด = ไม่เขียน |
| phase60 | ลบ zone → active:false | ล้างช่อง zone | ล้างช่อง Pullback ที่พิมพ์เอง → กลับตามกรอบ Break ยัง active · **และ** ลบตัวเลข Break Vol → ติ๊กหลุด + หลุด active | บรีฟ: ลบช่องว่าง = กลับตาม Break |
| phase60 | แผนเก่า: กรอก zone แล้ว (grandfather) ขาด Inval → ยกเลิกเอง | `active:false` | `kind:'bp'` · steps ครบ · `legacy_ok:true` · **ยัง active** | บรีฟข้อ "แก้ AC1 ข้อกังวล (แผนเก่าหลุด)" |
| phase60 | เลย์เอาต์ ชิป/TF บรรทัดเดียว · สูง ≥ 32 · font ≥ 16 (2 ช่อง) | แถวเดียว | ช่องติ๊ก 3 ช่องอยู่คนละแถวเรียงบนลงล่าง · ติ๊ก/TF สูง ≥ 30 · ช่องกรอก 6 ช่อง font ≥ 16 | ตามบรีฟ (≥ 30px) |
| phase60 | XAG: มี 3 ชิป | `[data-step]` = 3 | Break สรุป 1 บรรทัด + Pullback รอติ๊ก | fixture ติ๊ก Break ครบแล้ว |

## ที่ไม่ต้องแก้
- เคส MR (phase27 · 34 · 42) — ข้อ MR ยังใช้ UI เดิม (ช่องข้อความ/Activate/ยกเลิก Activate)
- phase61 · 62 · 56–59 ฯลฯ — ผ่านโดยไม่ต้องแก้

## ไม่เกี่ยวกับ AC2
- phase13 ล้มมาตั้งแต่ก่อน GL1 (ต้องใช้ `index.backup-pre-UI1.html` ที่ไม่มีอยู่) — จำนวนเคส 34 เท่าเดิม

## แก้โค้ดจากเทสเก่า (ไม่ใช่การแก้ความคาดหวัง)
- phase5 (BTC พิมพ์ค้างแล้วกดบันทึก): พบว่าการ commit ตัวเลขทำให้วาดแผงทับปุ่ม / ปุ่มบันทึกยัง disabled → แก้ในแอป: `satAcRender()` รอวาดหลังปล่อยเมาส์ (กลไก sat7dPtr เดิม) + ปลด disabled ของ [บันทึกแผน] ทันทีเมื่อค่าที่ commit ทำให้พร้อม
