# ID1-fix — หน้าต่าง Import ไอเดีย: ช่องวาง JSON แคบ + ตัวเล็ก

> ตรวจ ID1 แล้ว (คลาวด์ 45 ชุด · p44 137/137 · เทสเก่าไม่ถูกแก้) เจอปัญหาหน้าตา 2 จุด
> สำรองก่อนแก้: `index.backup-pre-ID1fix.html` · `tests/_bk_id1fix/run_tests_phase44.py` · ห้ามแตะ core-size.js · แก้เฉพาะ CSS 2 จุดนี้

## 1. ช่องวาง JSON (`#ideaJson`) ไม่มีสไตล์
- CSS ของช่อง Import ผูกกับ id `#ltJson` อย่างเดียว (~บรรทัด 1252) → `#ideaJson` เป็น textarea เปล่า: กว้าง ~178px (ทั้ง 1440 และ 390) · ตัวอักษร 13px → **iPhone ซูมหน้าเว็บเองตอนแตะช่อง** (ช่องที่ตัวอักษร < 16px)
- ใหม่: `#ideaJson` ใช้สไตล์เดียวกับ `#ltJson` (เช่น `#ltJson,#ideaJson{…}`) → เต็มกว้าง · ตัวอักษร 16px · พื้น/ขอบ/ฟอนต์ mono เหมือน Import Thesis

## 2. คีย์ลัด `[ ]` ในแถวตัวกรอง Ideas โผล่บนมือถือ
- `.ideaFil .kbdhint` ไม่ถูกซ่อนบนจอสัมผัส (pills ซ่อนแล้วด้วย `@media (hover:none){ .wlPills .kbdhint{display:none} }`) → บน Safari มือถือ `[ ]` ตกไปอยู่บรรทัดเดียวโดด ๆ
- ใหม่: เพิ่ม `.ideaFil .kbdhint` เข้า `@media (hover:none)` แบบเดียวกัน · จอที่มีเมาส์แสดงเหมือนเดิม

## เทส — เพิ่มเคสท้าย `tests/run_tests_phase44.py` (เคสเดิมห้ามแก้ · จำนวนเคสเพิ่มขึ้น)
10. เปิด Import ไอเดีย (1440 + 390): ความกว้าง `#ideaJson` ≥ 90% ของความกว้างเนื้อหาใน `#ltModal` · `font-size` ≥ 16px · ความกว้างเท่ากับ `#ltJson` ในหน้าต่าง Import Thesis (±2px)
11. [static] มีกฎ `@media (hover:none)` ที่ซ่อน `.ideaFil .kbdhint`
- ภาพ `tests/screenshots/id1fix-import-{1440,390}.png`
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–44

## รายงานกลับ
จำนวนเคสก่อน → หลัง (phase44) · จุดที่แก้ · ไม่ push ไม่ลบไฟล์
