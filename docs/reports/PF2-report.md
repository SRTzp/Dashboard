# PF2 — Report back

**แผน (≤ 8 ข้อ, ทำตามนี้):**
1. A1 — ปุ่ม Core|Sat บน iPhone ไม่ใช้ select/pill เด็ดขาด · sync header ทันทีตอน render แรก · ≤340px ลดขนาด/ช่องว่าง
2. A2 — ลบ prompt สัปดาห์ใหม่ (nwHtml/nwState/nwRows/nwStart…) ทุกอุปกรณ์ · สัปดาห์ใหม่เริ่มว่าง
3. A2 — ลิงก์ "นำเข้าความเห็นสัปดาห์ก่อน" (กล่องว่าง + สัปดาห์ก่อนมีข้อความเท่านั้น)
4. A3 — Strategy iPhone: Macro / เปลี่ยนเมื่อ แยกบล็อก 16px/1.5 ตัด 3 บรรทัด + "อ่านต่อ" → pbAssetSheet เดิม
5. A3 — แผ่นอ่าน pbSheet เต็มกว้าง ~92vh, 16–18px, ปุ่ม ✕ ปิดติดบน
6. A3 — Flow: พับ = ▸ ไตรมาส · vNNN · ใช้จริง → headline → ชิป Asset (ห่อ) · กาง = ไม่มีแถวชิป
7. A4 — Today การ์ด Sat เดียว: A (Add Strategic Asset) · B (รายการ Asset ไม่มีแผน + ＋ แผน) · C (เดิม)
8. เทส phase99 + ปรับเทสเก่า (PF2_retired.md)

## สิ่งที่เปลี่ยน
- **A1:** `hdrSubFit` คืน 'full' เสมอสำหรับ Plan ที่ ≤480px · `hdrSubCmpBuild` ไม่สร้าง pill ของ Plan บนมือถือ · `lfPlanChrome` เรียก `hdrSubSync()` ตรง ๆ · ที่ ≤340px: ปุ่ม scope padding 6px / .78rem, gap hbtns 2px (300px พอดีไม่ชน toolbar). Mac ไม่เปลี่ยน.
- **A2:** ลบ `nw*` ทั้งชุด + CSS `.nw-*` · คง `satWeekFreshPatch/Write` (＋ Asset ใช้) · `satWeekStart` เดิมไม่อ่าน/ไม่เขียนแล้ว (ข้อมูลยังอยู่) · ลิงก์ใหม่ `data-pf2-import` (`satwCanImportOpinion`) เรียก `satV3CopyPrev` เดิม.
- **A3:** `pf2ReadBtn`/`pf2ClampScan` (ตรวจว่าถูกตัดจริงถึงแสดง "อ่านต่อ") · CSS ใน `@media (max-width:480px)` ทั้งหมด · `pbSheet` เพิ่ม `.pbXtop` (ซ่อนบน Mac) · `pbCardHtml` จัดหัวใหม่ (ทุกอุปกรณ์ ตามคำสั่ง flowchips) · ไม่มีตัวคั่น " · " ระหว่างชิป.
- **A4:** `pf2SatPlanState` (picks = `satAssets()` · แผนใช้งาน = `satV3ShownIdeas` ที่ status ไม่ closed/cancelled และ `satV3PlanRowState !== 'closed'`) · `pf2AddAsset` · `pf2NewPlan` (switchTab › Sat › lfSatSet › satV2NewPlan) · งาน `sat-pick` เดิมไม่ขึ้นใน state A แล้ว (ซ้ำ).

## ที่ตัดสินใจเอง
- ลบ prompt ทุกอุปกรณ์ (ไม่ใช่เฉพาะ iPhone) เพื่อให้สอดคล้อง.
- ลิงก์นำเข้าคัดลอกด้วย `satwCopyFromPrev` เดิม (ความเห็น + comps + chart ของสัปดาห์ก่อน, ไม่แก้สัปดาห์ก่อน).
- State B ยังแสดงชิป ✓/✕ Focus เดิม (ตาม routine) ไว้ด้วย + รายการ Asset ที่ขาดแผน; State A ไม่มีชิป. A/B แสดงทุกวัน (รวมเสาร์–อาทิตย์) ตามสเปก "ไม่ขึ้นกับวัน"; C ใช้กติกาเดิม.
- แผนยกมาที่รอยืนยัน (carry) นับเป็นแผนของ Asset นั้น (เห็นใน Strategy).
- หน้าตา "Reload" ทดสอบด้วยการ render ซ้ำ/ไป-กลับแท็บ (mock Firestore ไม่คงข้อมูลข้าม reload) · การจำแท็บเดิมไม่ได้แตะ.
- ปุ่มปิดบนสุด ใช้ `aria-label="ปิด"` + CSS ::before "✕ ปิด" (กันตัวเลือก `has-text('ปิด')` ของเทสเก่าชนกัน).

## ข้อที่ยังค้าง (A2 · ตามที่สั่ง)
- สเปกให้ "Note/My opinion preserve current behavior · report as unresolved" — ตอนนี้: เริ่มว่างทุกสัปดาห์ + ลิงก์นำเข้าเมื่อกล่องว่าง (user ตัดสินใจ 25 ต.ค.) ยังเป็นข้อที่ WM1 เปลี่ยนต่อ (Copy last week / Clear Note).

## เทส / ภาพ
- phase99: 122/122 · เทสเก่าที่ปรับ: ดู `tests/PF2_retired.md` · ภาพ pf2-{plan-header-300,plan-header-390,strategy-macro-390,macro-sheet-390,flow-macro-390,today-A-390,today-B-390,today-B-1440} เปิดดูครบแล้ว.
- ไม่ push · ไม่ลบไฟล์ (หมายเหตุ: ครั้งหนึ่งผมเผลอสั่ง `rm -f` log ชั่วคราว ระบบบล็อกไว้ ไม่มีอะไรถูกลบ).

## ผลเทส (related suites หลังแก้เทสเก่า)
phase99 122/122 · phase 2, 9, 11, 17, 38, 39, 40, 43, 45, 50–52, 54, 56, 58–60, 63, 67–69, 72–86, 93–98 ผ่านทั้งหมด (0 FAIL) · ชุดเต็ม base + 1–102 รันท้าย run (ดู RUN-summary.md)
