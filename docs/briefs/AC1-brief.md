# AC1 — เงื่อนไขเข้า Sat: ติ๊ก Break ราคา · Break volume · Pullback + Pullback zone · ครบเงื่อนไข = Activate เอง (ตัดปุ่ม Activate) · เทส 60

> ผู้ใช้ตัดสิน 11 ต.ค. · ต่อจาก VW1fix · สำรองก่อนแก้: `index.backup-pre-AC1.html` · `tests/_bk_ac1/` · ห้ามแตะ core-size.js · ห้ามย้อนงานรอบก่อน (ST1 R:R/งดข่าว · SR1 ห้ามสวน Bias · AS1 สินค้าเพิ่มเอง · VW1)
> ไฟล์ชั่วคราวที่สร้างเองให้ย้ายไป `_to_delete/` ห้าม rm
> เป้า Dashboard ข้อ 2: ลดปัญหา execution — แผนจะ Activate ได้ต่อเมื่อเงื่อนไขเกิดจริงและกรอกครบ

## ข้อตัดสิน
- ตอนนี้มีเงื่อนไขแบบเดียว = **Break & Pullback** (ยังไม่ทำ "แบบอื่น" · ไม่เพิ่มในตั้งค่า) — แต่เก็บรายการขั้นไว้ในค่าคงที่ที่เดียว (`SAT_COND_STEPS`) เพื่อเพิ่มแบบอื่นภายหลังได้
- ต่อเงื่อนไข มี 3 ติ๊ก ตามลำดับ: `☐ Break แนวราคา` · `☐ Break แนว Volume` · `☐ Pullback เข้า zone`
  - 2 ติ๊ก Break ติ๊กก่อน/หลังกันได้ · `Pullback` ติ๊กได้เมื่อ Break ครบทั้ง 2 **และ** กรอก Pullback zone (จาก–ถึง) แล้ว
  - ข้าง Break แนวราคา มีตัวเลือก TF ปิดแท่ง `4H` | `D` (ต่อเงื่อนไข · ค่าเริ่มต้น 4H)
- **Activate อัตโนมัติ** เมื่อครบ 3 อย่าง: (1) ติ๊กครบ 3 ขั้น (2) TP zone กรอกอย่างน้อย 1 ช่อง (`tp_from` หรือ `tp_to`) (3) Invalidation (`inval`) กรอกแล้ว
- ตัดปุ่ม Activate ออกจาก UI · ใช้ `satV3CondActivate(ideaId, condId, true/false)` เดิมเป็นตัวทำงาน (ทิศ · TP เริ่มต้น · ล้าง Entry/SL ตอนสลับทิศ · เปิดช่อง Entry/SL ทำงานเหมือนเดิม)
- เงื่อนไขที่ Activate อยู่ ถ้าเอาติ๊กออก / ลบ Pullback zone / ลบ TP ทั้ง 2 ช่อง / ลบ Invalidation → ยกเลิก Activate อัตโนมัติ
- ใช้ได้ทีละเงื่อนไขเหมือนเดิม: อีกเงื่อนไขครบทีหลัง → สลับไปเงื่อนไขนั้น (เหมือนกด Activate ข้อใหม่เดิม) + ข้อความเล็ก `สลับไปเงื่อนไข #n`
- กติกาเดิมยังบล็อกเหมือนเดิมทุกข้อ: R:R ถึง TP แรก ≥ 1.5 · ช่วงงดข่าว · ห้ามสวน Bias · MR (ปิดอยู่)

## 1. ที่เก็บ (ในเงื่อนไขเดิมของ `satIdeas` · ไม่ต้องเพิ่ม rule)
- `conditions[i]` เพิ่ม: `kind:'bp'` · `steps:{brk:bool, vol:bool, pb:bool}` · `brk_tf:'4H'|'D'` · `pb_from:number|null` · `pb_to:number|null`
- เงื่อนไขเก่าที่ไม่มี `kind` = อ่านเป็น `'bp'` · ถ้าเดิม `active:true` → ถือว่าติ๊กครบ 3 ขั้น (อ่านอย่างเดียว ไม่ migrate · แผนที่ Activate อยู่แล้วต้องไม่หลุด) · ถ้าเดิมไม่ active → ติ๊กว่าง
- เงื่อนไขที่ cancelled → ติ๊กไม่ได้ (เหมือน Activate เดิม)

## 2. หน้าตา (ในการ์ดแผน Sat เดิม · ห้ามปรับส่วนอื่นของการ์ด)
- แถวเงื่อนไข: ข้อความเดิม · แถวติ๊ก 3 ชิป `Break ราคา [4H▾]` `Break Vol` `Pullback` (สูง ≥ 32px · บรรทัดเดียวที่ 390px) · ช่อง Pullback zone `จาก–ถึง` (font ≥ 16px) · ช่อง TP / Invalidation เดิม
- ยังไม่ครบ: บรรทัดเล็กสีจาง `ขาด: Pullback zone · Invalidation` (เรียงตามลำดับข้างบน) · ครบแล้ว: ป้าย `● Active` แทนปุ่มเดิม
- Pullback ติ๊กไม่ได้ (Break ไม่ครบ / ไม่มี zone) → ชิปเป็นสีเทา + `title` บอกเหตุ
- ตัวเลขตรวจ: `pb_from`/`pb_to` > 0 · ถ้ากรอกทั้งคู่ เรียงจากน้อยไปมากให้เอง

## 3. Today
- ในส่วนเช็กแผน Sat เดิม: แผนที่ Break ครบ 2 ติ๊กแต่ยังไม่ Pullback → แถวเตือน `XAU รอ Pullback เข้า zone <from–to>` (≤ 1 แถวต่อสินค้า · ปกติ = เงียบ)

## เทส `tests/run_tests_phase60.py` (Chromium · 1440 + 390 · mock Firestore)
1. เงื่อนไขใหม่: ไม่มีปุ่ม Activate · มี 3 ชิป · ค่าเริ่ม TF 4H · บรรทัด `ขาด: Break ราคา · Break Vol · Pullback · Pullback zone · TP · Invalidation`
2. ติ๊ก Pullback ก่อน Break → ไม่ได้ · Break ครบแต่ไม่มี zone → ไม่ได้ · มี zone → ได้
3. ติ๊กครบ + TP 1 ช่อง + Invalidation → `active:true` อัตโนมัติ · ทิศ/TP เริ่มต้นเหมือนกด Activate เดิม (เทียบ `act_side` · `tp`) · ช่อง Entry/SL เปิด
4. ขาด TP (ทั้ง 2 ว่าง) หรือขาด Invalidation → ไม่ active · ลบค่าหลัง active → `active:false`
5. 2 เงื่อนไข: ข้อ 1 active · ข้อ 2 ครบ → active ย้ายไปข้อ 2 · ข้อ 1 `active:false` · ข้อความ `สลับไปเงื่อนไข #2`
6. แผนเก่า (fixture ไม่มี `kind`/`steps` · `active:true`) → แสดงติ๊กครบ · ยัง active · คำนวณ lot/R:R เท่าเดิม
7. R:R < 1.5 / ช่วงงดข่าว / สวน Bias → ยังบล็อกบันทึก order เหมือนเดิม (กติกา ST1/SR1 ไม่เปลี่ยน)
8. Today: Break ครบไม่มี Pullback → แถว `รอ Pullback` · ติ๊ก Pullback แล้ว → แถวหาย
9. สินค้าเพิ่มเอง (AS1 · XAG) ใช้ได้เหมือนกัน
10. 390px: แถวชิปบรรทัดเดียว · ไม่ล้นแนวนอน · ช่องกรอก ≥ 16px · ไม่มี console error
- ภาพ `tests/screenshots/ac1-*` (1440 + 390): `cond-empty` · `cond-missing` · `cond-active` · `today-wait`

### เทสเก่า
- เคสที่กดปุ่ม Activate (ST1 · SR1 · 7E-4 · AS1 · PY1 ฯลฯ) → เปลี่ยนเป็นติ๊ก 3 ขั้น + กรอก zone/TP/Invalidation ใน fixture หรือเรียก `satV3CondActivate` ตรงเมื่อเคสไม่ได้ทดสอบ UI นี้ · ความคาดหวังเดิม (lot · R:R · บล็อก) ต้องเหมือนเดิม · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/AC1_retired.md`
- อัปเดต `ไฟล์ที่ห้ามลบ.md`
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–60

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ฟังก์ชันใหม่/ที่แก้ · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
