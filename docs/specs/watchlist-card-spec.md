# Spec — Watchlist Card v2 (Living Thesis)

ส่งให้ Claude Code แก้ `index.html` · แทนแท็บ `Overview | Research` เดิมทั้งหมด
ข้อมูลมาจาก JSON `living-thesis@1` (skill `living-thesis`)

## 1. Header การ์ด (คงเดิม)
`TICKER` · ชื่อบริษัท · ป้ายพอร์ต (`CORE.US` / `CORE.TH`) · **ป้าย Tier (`A · ทั้งคู่` ฯลฯ) — คงไว้ ผู้ใช้ตั้งเอง skill ไม่แตะ**
บรรทัดรอง: `Thesis {mode} · {date}` + ป้ายสถานะ (`summary.status`) + ⚠ ถ้า `asOf` เก่ากว่า 7 วัน

## 2. แท็บ (แทนวงกลมเดิม)
`[สรุป] [ธุรกิจ] [ทำไมซื้อ] [ติดตาม] [ออกเมื่อ]`
- 5 ปุ่ม แบบ segmented pill เดิม · มือถือ: เลื่อนแนวนอนได้ ห้ามตัดบรรทัด
- จำแท็บล่าสุดต่อ ticker ใน localStorage (try/catch)

| แท็บ | แสดงอะไร |
|---|---|
| สรุป | `summary` เป็นรายการ label → ค่า (ลำดับ: ธุรกิจ · Life cycle · Power · Thesis 1–3 · เครื่องยนต์ · ราคา · ความเสี่ยง #1 · Unknown · What's next · Thesis breaker · ข้อสรุป) + `tier_note` ถ้ามี (ตัวเล็ก ใต้ Tier) |
| ธุรกิจ | `sections.s1.md` |
| ทำไมซื้อ | `sections.s2.md` |
| ติดตาม | `sections.s3.md` + ตาราง `gaps[]` (เรียง must → track → skip) + ตาราง `kpi[]` + ตาราง `log[]` (ใหม่สุดบน) |
| ออกเมื่อ | ตาราง `tripwires[]` (สีตาม level: ok เทา · watch เหลือง · review ส้ม · broken แดง) + `sections.s4.md` |

ท้ายแท็บ 1–4: ปุ่มพับ "หลักฐาน & แหล่งที่มา" → `evidence[]` + `sources[]` (ลิงก์เปิดแท็บใหม่) + `audit`

## 3. Markdown renderer (ขนาดเล็ก เขียนเอง ไม่ใช้ lib)
รองรับเท่านี้: `###` · `-` bullet · `**bold**` · ตาราง `| |` · `>` quote · บรรทัดว่าง = ย่อหน้า
- **escape HTML ก่อน parse เสมอ** (กัน XSS จากข้อความใน JSON)
- ป้าย `[F] [C] [M] [I] [A] [?]` → chip สีเล็ก: F/C เขียว · M ม่วง · I ฟ้า · A ส้ม · ? เทา
- ตารางกว้างเกินจอ → wrapper `overflow-x:auto`

## 4. Import / Update
ปุ่ม 📥 Import รับ JSON:
- `schema !== "living-thesis@1"` → แจ้ง error ไม่บันทึก
- ไม่มี ticker นี้ใน watchlist → สร้างใหม่ (port `core`, market จาก JSON)
- มีอยู่แล้ว → แสดง diff สั้น (status · thesis · tripwire level ที่เปลี่ยน) → ยืนยัน → บันทึก:
  - `summary`, `sections`, `gaps`, `kpi`, `tripwires`, `evidence`, `sources`, `audit`, `mode`, `date`, `asOf`, `basis` → **แทนที่**
  - `log` → **append** เฉพาะบรรทัดที่ยังไม่มี (key = `date + new`) · ห้ามลบของเก่า
  - `tier`, `note`, `added_at`, `status` ที่ผู้ใช้ตั้งเป็น `hold`/`pause`/`exit` → **คงค่าเดิม** (AI เสนอสถานะได้แค่ screen/watch/deep/wait_price)
- เก็บ snapshot ก่อนแทนที่ไว้ใน `history[]` (เก็บ 5 ฉบับล่าสุด: date + summary) เพื่อย้อนดูความคิดเดิม

ปุ่ม ⋯ → **Export JSON** (copy JSON ปัจจุบัน ใช้ส่งให้ skill โหมด update)

## 5. Firestore
- path เดิม `users/{uid}/watchlist/{TICKER}` · เพิ่ม field `thesis` (object = JSON ทั้งก้อน ยกเว้น `log`) + `thesis_log` (array) + `history` (array)
- ขนาดต่อ doc ~20–40KB อยู่ในเกณฑ์ (limit 1MB)
- Firestore rules ไม่ต้องเปลี่ยน (อยู่ใต้ path เดิม)

## 6. ลบของเก่า
- แท็บ `Overview` / `Research` และ renderer ของ `fund-checklist@1` (gate, score s1–s8, note n1–n6)
- ข้อมูลเก่าใน Firestore: **ไม่ลบ** แค่ไม่อ่าน · การ์ดที่ยังไม่มี `thesis` แสดง "ยังไม่มี Thesis — รัน living-thesis แล้ว 📥 Import"

## 7. เชื่อมระบบอื่น (ทำหลัง v1 ได้)
- Research-team pusher / ข่าว: อ่าน `tripwires[].signal` ของทุกหุ้น → push เฉพาะข่าวที่ชน tripwire (สอดคล้องกับที่ตัด news feed ทั่วไปไปแล้ว)
- Core plan card: แสดง `summary.breaker` + tripwire ที่ level ≥ review ข้างปุ่มเข้าเทรด

## 8. Acceptance check
1. Import JSON ตัวอย่างจาก SKILL.md → 5 แท็บแสดงครบ ไม่มี HTML หลุด
2. Import ซ้ำด้วย log ใหม่ 1 บรรทัด → log มี 2 บรรทัด · tier ไม่เปลี่ยน
3. ใส่ `<script>` ในข้อความ → แสดงเป็นตัวอักษร
4. iPhone width: แท็บเลื่อนได้ ตารางเลื่อนแนวนอนได้ หน้าไม่เลื่อนข้าง
5. `node --check` ผ่าน
