# WA1fix — เทสเก่าที่แก้ความคาดหวัง (ไม่ลบเคส · ไม่ทำให้อ่อนลง)

เหตุร่วม: เลิกโหมด legacy (ไม่มี `satWeekPick` = แสดง 4 ตัว) → Strategy/Today/Bias นับเฉพาะ Asset ที่ **เลือกสัปดาห์นี้ (≤ 3)** · ไม่มีการซ่อน (hidden) แล้ว

| ชุด | เคส | เปลี่ยนอย่างไร |
|---|---|---|
| p4 (launch_page) | ทุกเคส | `PICK_DEFAULT` = XAUUSD/BTCUSD/S50 seed ให้สัปดาห์ปัจจุบันหลัง login (ค่าตั้งเดิมอื่นไม่แตะ) |
| p3 | satV3ReadyCount · บันทึก order | seed pick 3 ตัวหลัง login |
| p5 / p6 / p7 / p11 | ใช้การ์ด BRENT ฯลฯ | `ensure_pick(asset)` ใน p5.open_editor / p6.new_plan: ถ้า asset ไม่อยู่ใน pick → ใส่เป็นตัวแรก (≤ 3) แล้วตรวจเท่าเดิม |
| doc38 (p38/p39/p56/p59) | fixture | seed `satWeekPick` XAUUSD/BTCUSD/S50 ให้ 4 สัปดาห์ของนาฬิกาปลอม · P54.launch ลบทิ้ง (ชุด WA1+ เริ่มจากว่าง) |
| p38 | 5 เช็กแผน Sat: ช่อง 4 → 3 (XAU·BTC·S50) · 5 Bias: `BTC · S50` (ไม่มี Brent) | เพดาน 3 · Today นับเฉพาะที่เลือก |
| p39 | 6/7/9/F1–F6/13 | ชุดนี้ใช้ pick XAU·BTC·Brent (`PICK39`) · S50 → ไม่ขึ้น · F2 disabled เหลือ Brent ตัวเดียว · F6 log เก่า ✓3 ใช้ XAU·BTC·Brent (ตรวจ "Brent disabled" ย้ายไป F2 ที่ตรวจอยู่แล้ว) · 13 ตาราง 3 ช่อง (2 คอลัมน์) · ปุ่ม ≥ 7 |
| p55 | 1 · 2 · 5 · 7 | สินค้าทั้งหมด (`satAssets({all:true})`) ยังตรวจ 4/5/6 ตัวเท่าเดิม + ช่อง Strategy ตาม pick · Today เตือน Bias ตามที่เลือก · "ซ่อน Silver" → เอา Silver ออกจากสัปดาห์ (`waRemove`) เพราะไม่มีการซ่อนแล้ว |
| p56 | 1 · 7 · 8 | `day()` ใช้ XAU·BTC·Brent · ตัวเลข Daily 16 → 15 หน่วย (10/15 · 67% · 11/15 · 73% · แท่ง 100/93/60/67) · Bias 3/3 · เคส 1 (เทียบไฟล์ก่อน GL1) ตัดแถว Sat-daily/Bias ออกจากการเทียบทั้งสองฝั่ง + เลือก S50 ให้ป้ายจำนวนงาน Plan TH เท่าเดิม |
| p59 | 1d · 2 · 3 · 7 | ช่องกราฟ 4 → 3 · XAG ใช้ pick XAU·BTC·XAG · "ซ่อน BTCUSD" → เอาออกจากสัปดาห์ (เหลือ 2) |
| p54 | 1 Strategy 4 ช่อง | pick 3 ตัว + `satAssets({all:true})` = 4 · ลบบรรทัดโค้ดตาย `P51.fresh(page, None) if False else None` · จำนวน `check(` ที่ลด 59→54 (ตอน WA1 ตัด checkbox ซ่อน) ตรวจแล้ว: เทียบกับ _bk_wa1 (ก่อน WA1): เคสที่หายคือกลุ่ม 'ซ่อน/เลิกซ่อน' ของ 6–7 (8 ชื่อเคส: ซ่อน BRENT ×3, หน้าตั้งโบรกไม่มีแถว Brent, เลิกซ่อน, ซ่อนที่มีไม้เปิด, ซ่อนที่มีแผน, ซ่อนจนเหลือ 0, บันทึกเหลือ 1 ตัว) ซึ่ง WA1 ตัดเพราะเลิก checkbox ซ่อน (จดไว้แล้วใน WA1_retired.md) · เคส '1 Strategy มี 4 ช่อง' เปลี่ยนชื่อ ไม่ได้ตัด · เคสอื่นของ p54 (ค่าตั้งโบรกไม่หาย · ไม่มี hidden ใหม่ · การ์ดตาม pick) ยังอยู่ครบ |
| p69 | 2b | ไม่มี satWeekPick → empty state (ไม่มีการ์ด · ไม่มี data-wa-legacy) แทนแสดง 4 ตัว + hint |

p38 ใช้ `tdRoutine(raw)` ใหม่ → หน้าตั้งค่า Daily routine ยังเห็นครบ 4 ตลาด (เคส 14 เดิมผ่านโดยไม่แก้)

## เพิ่มหลังรันเต็มชุด (พบตอนจบคิว TR1)
| ชุด | เคส | เปลี่ยนอย่างไร |
|---|---|---|
| p2 | แถบ Strategy ครบ 4 ช่อง · tile Bias ฯลฯ | seed pick XAU·BTC·Brent · "ครบ 4 ช่อง" ตรวจ 3 ที่เลือก + S50 ที่เลือกแยก (รวมครบ 4 ตัวเท่าเดิม) |
| p14 | Future: tile/pill/ข้อความ เทียบไฟล์ก่อน UI1b | เทียบ 3 ช่องที่เลือก (ไม่นับ Brent) · pill ของ Brent ตรวจโดยเลือกชั่วคราวแล้วคืน · "4 tile" → 3 · คืนค่าฟอนต์ขั้นต่ำ ≥ 0.72rem ด้วยการแก้แอป `.waMac` 11px → .72rem (ชิป Macro ใน Strategy ที่เพิ่งขึ้นเพราะไม่มีโหมด legacy) |
| p15 | tile: 4 tile / คีย์บอร์ด Brent | tile ที่เลือก 3 + สินค้าทั้งหมด 4 · คีย์บอร์ดทดสอบกับ S50 |
| p14/p16 (index เก่า) | `satWeekPickWrite` ไม่มีในไฟล์เก่า | `launch_page` ใน p4 ข้ามการ seed ถ้าไฟล์ที่ทดสอบไม่มีฟังก์ชันนี้ |
| p37 | 7 reduce ยัง ready | seed pick XAU·BTC·S50 ก่อนคำนวณแผน (Asset ไม่ได้เลือก = คำนวณไม่ได้) |
| p58 | 5 Daily 7/12 · 58% | Sat 3 ตลาดที่เลือก → 7/11 · 64% · ชิป Sat 2/3 |
| p60 · p63 | XAG ครบ → Activate / คำนวณ lot | launch ด้วย pick XAU·BTC·XAG |
