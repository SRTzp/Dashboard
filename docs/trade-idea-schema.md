# Schema ไอเดียเทรด — `trade@1` / `trade-batch@1` (TR1)

เก็บที่ `users/{uid}/ideas/{id}` (collection เดิมของ Ideas) · field `kind: 'trade'` (ไม่มี = ไอเดียลงทุน `idea@1` เดิม) · rules เดิมครอบคลุมทั้ง collection (ไม่มีการเปลี่ยน)

## Document

```
{ kind: 'trade',
  ai:  <JSON trade@1 ล่าสุดจาก AI | null>,        // Import ใหม่ = แทนที่ ai เท่านั้น
  me:  { title, news, date, dir:'long'|'short', strength:'low'|'mid'|'high', horizon, tf:'4H'|'D'|'W',
         asset_hint, chain:[{step,note?}], one_line, counter:[], wrong_if:[], alts:[], entry, products:[{name,type,lev}] },
  user:{ status:'draft'|'watch'|'planned'|'parked', product, ack:{<row>:true}, sat_key, week, expires:'YYYY-MM-DD', plan_id, updated_at },
  idea_log:[{date,new,changed,decision}] }
```
- `me` ไม่มีอะไรเขียนทับนอกจากผู้ใช้ (ปุ่ม `ใช้ข้อของ AI` = คัดลอกค่าแถวเดียวเข้า `me`)
- สถานะที่แสดง: `ร่าง · เฝ้า · ในแผน (มี pick สัปดาห์นี้) · พัก · หมดอายุ (expires < วันนี้ และไม่ได้อยู่ในแผน/พัก)`
- แผน Sat ที่สร้างจากไอเดียเก็บ `idea_id` ที่ `users/{uid}/satIdeas/{id}`

## `trade@1`

```json
{"schema":"trade@1","id":"cxmt-kospi-2026-10","title":"CXMT กดราคา Memory → KOSPI ▼",
 "date":"2026-10-15","expires":"2026-10-29","asset_hint":"KOSPI200","dir":"short","tf":"D","horizon":"1–2 สัปดาห์",
 "one_line":"…","chain":[{"step":"CXMT ขยาย DDR5/HBM","note":"ตัวจุดชนวน"}],
 "strength":"mid","counter":["…"],"wrong_if":["…"],"alts":["…"],
 "products":[{"name":"KOSPI200 Futures","type":"futures","lev":"สูง"},{"name":"Inverse 2X ETF","type":"etf_lev","lev":"2X รายวัน"}],
 "entry":"Break ใต้แนวรับ D + Vol","sources":[{"title":"…","url":"https://…","date":"2026-10-14"}]}
```

| field | ต้องมี | กติกา |
|---|---|---|
| schema | ✔ | `"trade@1"` |
| id | ✔ | `[a-z0-9-]` ยาว ≤ 60 · ห้ามซ้ำกับไอเดียลงทุน (`idea@1`) |
| title | ✔ | ไม่ว่าง |
| date / expires | ✔ | `YYYY-MM-DD` · `expires ≥ date` |
| dir | ✔ | `long` \| `short` |
| tf | ✔ | `4H` \| `D` \| `W` |
| strength | – | `low` \| `mid` \| `high` |
| one_line | – | ≤ 120 ตัวอักษร |
| counter / wrong_if / alts / chain / products / sources | – | รายการ (`products[].type` ∈ `futures cfd etf etf_lev option stock other`) |

## `trade-batch@1`

```json
{"schema":"trade-batch@1","date":"2026-10-15","ideas":[ <trade@1>, … ]}
```
`ideas` 0–3 ตัว → เข้าเป็นสถานะ `ร่าง` ที่มีแต่ฝั่ง AI · id ซ้ำใน batch = error

## Import
ปุ่ม 📥 Import เดิมของ Ideas แยก schema อัตโนมัติ (`idea@1` / `trade@1` / `trade-batch@1`) · ผิด = ข้อความ error ระบุ field · id เดิม = แทนที่ `ai` เท่านั้น (`me`/`user` ไม่แตะ)

## ＋ วางแผน
ต้องมี `me.dir` และ `me.wrong_if` ≥ 1 ข้อ · หา Sat key จาก `user.product` → `me.asset_hint` → `ai.asset_hint` (ตรงกับ key หรือชื่อที่แสดง) · ตรง → `satWeekPickAdd` · ไม่ตรง → sheet เพิ่มสินค้า (AS1) เติม key/ชื่อ แล้วเข้าสัปดาห์เมื่อบันทึก · สร้างแผน Sat (draft) ทิศ = `me.dir` เก็บ `idea_id` · สวน/นอก Macro เติม `macro_note` จาก `one_line` (≤ 80 ตัว)
