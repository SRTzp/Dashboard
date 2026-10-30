# RC2 — เคสที่แก้ความคาดหวัง/อินพุต (tests)

ไม่มีเคสในชุด `run_tests` / phase 1–31 ที่ขัดกับ brief RC2 — ไม่ต้องแก้ความคาดหวัง ไม่มีเคสที่ลบหรือเลิกใช้ · ทุกชุดผลเท่าเดิม (ดูรายงาน) · เพิ่มชุดใหม่ phase32 (43 เคส) และเคสใหม่ใน `research-card-test.js`

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| research-card-test.js | โหลดการ์ดตัวอย่างหลัก (`original`) | อ่าน `../Projects/Research-team/shared/examples/EXAMPLE-research-card.json` อย่างเดียว → เครื่องนี้ไม่มีไฟล์ (โฟลเดอร์ Research-team ว่าง) ทำให้ `node research-card-test.js` ล้มด้วย ENOENT ตั้งแต่ก่อน RC2 | ใช้ไฟล์เดิมถ้ามี · ไม่มี → ใช้ `avgo-research-card-original.json` (ตั้ง ticker EXAMPLE · researched_at 2026-09-18T09:00:00Z · driver แรก unconfirmed ไม่มีหลักฐาน) · ความคาดหวังของทุกเคสเดิมไม่เปลี่ยน | ห้ามปล่อยล้ม · ต้องรันได้บนเครื่องนี้ (ไม่ใช่ผลจาก RC2 โดยตรง) |
| phase23 | `sync_core_size.py: สำเนาเพี้ยน → --check…` | ผ่าน | ล้มครั้งเดียวตอนรัน 2 ชุด (before/after) พร้อมกัน เพราะใช้ไฟล์ temp ร่วมกัน · รันเดี่ยวผ่าน 123/123 | ไม่ใช่ปัญหาโค้ด · อย่ารัน phase23 ขนานกัน |
