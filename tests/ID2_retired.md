# ID2 — เคสเก่าที่แก้ความคาดหวัง/ข้อมูล seed (ไม่ลบเคส · ไม่ทำให้อ่อนลง)

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| phase35 | 9 CAND1 (candidate): ไม่มีปุ่ม ＋ โน้ต · ชิป Screen เดิมยังอยู่ · ไม่มีส่วนโน้ต (1440 + 430 = 2 เคส) | CAND1 เป็น Candidates เพราะมีใน `research` อย่างเดียว | seed ไอเดีย `cand-fixture` (รอหลักฐาน) ที่มี CAND1 เป็นบริษัท (ศึกษา · มี relevance_src) เพิ่มใน `seed()` · assertion เดิมไม่เปลี่ยน | ID2 ข้อ 1: Candidates มาจากไอเดีย ไม่อ่าน research (ชิป Screen มาจาก research join ของแถวซึ่งคงเดิม) |
| phase35 | 12 (เคสที่เปิด CAND1 ต่อ) | — | ผ่านเหมือนเดิมโดยไม่แก้ assertion (ใช้ seed เดียวกัน) | เหมือนข้างบน |
| phase40 | 14 Candidates กดเข้า = การ์ด 'ยังไม่มี Thesis' + ปุ่ม ＋ เพิ่มเข้า Watchlist + 📥 Import (1440 + 390) | CAND1 จาก research | seed ไอเดีย `cand-fixture` ที่มี CAND1 ใน `extra()` · assertion เดิมไม่เปลี่ยน | เหมือนข้างบน |
| phase44 | คาดปุ่ม ▲ ▼ เลื่อนลำดับ | — | ไม่มีเคสเดิมที่ assert ข้อความปุ่ม → ไม่ต้องแก้ · เคสใหม่ใน phase45 ตรวจ `↑ ↓` แทน | ID2 ข้อ 4 |

สำรอง: `index.backup-pre-ID2.html` · `tests/_bk_id2/`
