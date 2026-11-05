# RR2 — รูปกราฟยังกระพริบตอนกดปุ่ม (เกิดจาก rrKeepImgs ย้าย <img> ผ่าน <template>) · เทส 76

> ผู้ใช้ 17 ต.ค. (หลัง deploy RR1fix): หน้าไม่กระตุกเองแล้ว แต่ **รูป Chart กระพริบเวลากดปุ่ม** เช่น ปุ่ม TF 4H/D/W ในการ์ดแผน · ป้าย `?debug=render`: `satV3Render 8 (วาดจริง 4 · ข้าม 4)` ตัวเรียก `satAcRender < satAcSync < satAcWrite < satAcSetTf` และ `renderSat7d < sat7dRefresh < anon@14128` (snapshot หลังเขียน)
> **สาเหตุ (Orchestrator ยืนยันบนคลาวด์ด้วยหน้าเทสเล็ก):** `rrKeepImgs` เอา `<img>` เดิม `replaceWith` เข้าไปใน `tpl.content` ของ `<template>` = **คนละ document** → เบราว์เซอร์ถือว่า img ถูก adopt → โหลดภาพใหม่ (ยิง `load` ซ้ำ 1 ครั้ง) → กระพริบ · ถ้าย้ายใน document เดียวกัน (div/fragment ของ document หลัก) → `load` ไม่ยิงซ้ำ (0 ครั้ง)
> สำรองก่อนแก้: `index.backup-pre-RR2.html` · `tests/_bk_rr2/` · ห้ามแตะ core-size.js · ห้ามย้อน RR1/RR1fix · ไฟล์ชั่วคราว → `_to_delete/` ห้าม rm
> **ชุดที่เกี่ยวข้อง:** phase76 (ใหม่) · p75 · p59 · p67 · p69 · p74

## แก้
1. **ห้ามให้ `<img>` เดิมเข้าไปใน `template.content`** — ลำดับใหม่: สร้าง DOM ใหม่จาก template → `el.replaceChildren(content)` (ตอนนี้ node ใหม่อยู่ใน document หลักแล้ว) → **แล้วค่อย** สลับ `<img>` ใหม่ออก ใส่ `<img>` เดิมแทน (img เดิมอยู่ document เดียวกัน ไม่โหลดใหม่) · หรือสร้าง DOM ใหม่ใน fragment ของ document หลักแทน template (เลือกแบบที่ไม่ทำให้ `<img>` ใหม่ยิงโหลดเกินจำเป็น)
2. ถ้าทำได้ไม่ยาก: **วาดใหม่เฉพาะส่วนที่ HTML เปลี่ยน** (แถบ Strategy / การ์ด Asset แต่ละใบ / แผนแต่ละใบ แยกกัน) — กดปุ่ม TF ในแผน → การ์ด Asset (ที่มีรูป) ไม่ถูกแตะเลย · ถ้ายาก/เสี่ยง ข้ามข้อนี้ได้ (ข้อ 1 พอแก้อาการ) — บอกในรายงานว่าทำหรือไม่
3. ใช้กติกาเดียวกันกับจุดอื่นที่ใช้ `rrKeepImgs` หรือรูปแบบ template คล้ายกัน (ถ้ามี)

## เทส `tests/run_tests_phase76.py` (Chromium · 1440 + 390)
- fixture: pick XAUUSD (มีลิงก์กราฟ · ภาพ local) + BTC · แผน XAUUSD ร่าง 1 ใบที่มีเงื่อนไข
1. นับ event `load` ของ `<img>` กราฟ XAUUSD (ติด listener หลังโหลดครั้งแรก) → กดปุ่ม TF 4H → D → W ในแผน (รอ snapshot สะท้อนกลับ) → `load` เพิ่ม **0 ครั้ง** · `img` เป็น node เดิม · `img.complete` = true ตลอด
2. `satV3Render({force:true})` 5 ครั้ง → `load` เพิ่ม 0 · node เดิม
3. เปลี่ยน URL กราฟจริง (ลิงก์ใหม่) → โหลดภาพใหม่ 1 ครั้ง (ต้องยังทำงาน)
4. กดปุ่มอื่นในการ์ดแผน (ทิศ Break ▲/▼ · ✕ เงื่อนไข · กรอก Price) → `load` เพิ่ม 0
5. (ถ้าทำข้อ 2 ของการแก้) กดปุ่ม TF → MutationObserver บนการ์ด Asset XAUUSD = 0
6. ไม่มี console error · 390 ไม่ล้น
- ภาพ `tests/screenshots/rr2-*` (1440 + 390)
- รันเทสใหม่กับ `index.backup-pre-RR2.html` ต้องล้มเคส 1 (ยืนยันว่าเทสจับอาการได้)

### เทสเก่า
- ห้ามลบเคส ห้ามทำให้อ่อนลง · จด `tests/RR2_retired.md` · อัปเดต `ไฟล์ที่ห้ามลบ.md`
- **ระหว่างทำ:** รันชุดที่เกี่ยวข้อง · **จบ:** รันเต็มชุดครั้งเดียว ทีละชุด (base + phase 1–76)

## รายงานกลับ
จุดที่แก้ · ทำข้อ 2 หรือไม่ · จำนวนเคส · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
