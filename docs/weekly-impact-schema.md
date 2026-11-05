# Weekly Impact — data contract `weeklyImpact/v2`

ใช้ร่วมกันระหว่างสกิล `weekend-macro-update` (ผลิต JSON) และ Dashboard (วางใน Strategy › Weekly Impact › Paste)
เวลาทั้งหมดแสดงเป็น **ICT (UTC+7)** · เก็บที่ `users/{uid}/weeklyImpact/{YYYY-MM-DD}` (1 เอกสาร = 1 สัปดาห์ จันทร์ Asia/Bangkok)

## สัปดาห์
- Strategy เริ่ม **วันอาทิตย์** · Weekly Impact เริ่ม **วันจันทร์** · mapping = อาทิตย์ → จันทร์ถัดไป (`Calc.wiMondayOfStrategy`, คณิตศาสตร์วันที่แบบข้อความ ไม่พึ่ง timezone เครื่อง)
- `week` ที่ไม่ใช่วันจันทร์ → ถูกปฏิเสธ · สัปดาห์ที่ไม่ตรง = ป้าย `ต่างสัปดาห์` (แยกจาก `อัปเดต <asof>` — สัปดาห์ตรงไม่ได้แปลว่าสด)

## Skill input — Asset manifest (ปุ่ม `คัดลอก Asset manifest` ในหน้า Paste)
```json
{"assets":[{"id":"XAUUSD","name":"XAUUSD","ref_market":"","aliases":[]},
           {"id":"BTCUSD","name":"BTC","ref_market":"","aliases":["BTC"]}]}
```
สกิลต้องคืน **id ที่ส่งให้** (หรือ alias ที่ประกาศไว้) และวิเคราะห์ตลาดที่ตั้งไว้ · รายการ 7 ตัว (XAUUSD, XAG, BTC, BRENT, USDJPY, S50, US) เป็นเพียง default research list ไม่ใช่ข้อบังคับให้สร้าง Asset.

## Top level
| field | type | หมายเหตุ |
|---|---|---|
| `schema` | `"weeklyImpact/v2"` | v1 (legacy) = ไม่มี `schema` หรือ `"weeklyImpact/v1"` + `{week, assets:{KEY:{impact,note,mechanism?}}}` · อ่านได้ ไม่สร้างเตือนเวลา |
| `week` | `YYYY-MM-DD` | วันจันทร์ |
| `asof` | ISO + offset | บังคับใน v2 เช่น `2026-10-25T09:00:00+07:00` |
| `sources` | `{id:{name,url?,checked_at?}}` | url ต้องเป็น http(s) |
| `events` | `{eventId:{…}}` | event id คงที่ `[A-Za-z0-9][A-Za-z0-9_.:-]{0,59}` |
| `assets` | `{KEY:{…}}` | KEY = id / alias / ชื่อที่แสดงของ Asset ในแอปเท่านั้น (ไม่ fuzzy · ไม่สร้างให้) |

## events[id]
`title` (บังคับ) · `label_th` · `kind`: release / decision / speech / event / carryover · `metric` · `basis` (YoY · MoM · QoQ SAAR …) · `period` · `unit` ·
`scheduled_at` (ISO+offset | null) · `date_local` (YYYY-MM-DD เมื่อยืนยันแค่วัน) · `time_status`: confirmed / tentative / unknown / unscheduled (`confirmed` ต้องมี `scheduled_at`) · `occurred_at` (carryover) ·
`forecast` / `previous` / `actual`: **ตัวเลขหรือ null** (ห้ามใส่ 0 แทนค่าที่ไม่มี) · `previous_revised`: boolean|null · `actual_updated_at` · `status`: scheduled / released / ongoing / postponed / cancelled ·
`previous_period` (string ≤40 | null · เช่น `Sep 2026` → UI แสดง `ครั้งก่อน (Sep 2026)`) · `source_refs`: string[] (id ใน `sources` ทุกตัว · ไม่มี = `[]`) ·
`src_schedule` / `src_forecast` / `src_previous` / `src_actual` = id ใน `sources` หรือ null (ตรวจเมื่อมีค่า).
**เข้ากันได้ย้อนหลัง:** event เก่าไม่ต้องมี `previous_period` / `src_actual` / `source_refs` — แอป normalise เป็น `null` / `null` / `[]` (ไม่ reject).
เขียนเพิ่มโดยแอป (อัปเดตผลเอง): `actual_source` (URL) · `previous_original` (ค่าก่อนแก้ย้อนหลัง) · `previous_source` · `actual_prev` {value,at,source} · `result_note` (event เชิงคุณภาพ).

## assets[KEY]
`impact`: `HIGH` / `MED` / `LOW` / `null` (null = ไม่มีข้อมูล ≠ LOW) · `note` (สรุปแรงขับสัปดาห์) · `event_refs`: [event id…] (2 รายการแรกขึ้นก่อน · รายการอื่นอยู่ใน "อีก n ข่าว") · `carryover_th` · `ref_market` (ถ้ามี งานวิจัยเฉพาะตลาด) ·
`interp`: `{eventId:{mechanism_th, scenarios_th:[{key,label_th?,text_th}], watch_th}}` — `key` = `above` / `below` / `inline` / `occurs` (เกิดขึ้น) / `delayed` (เลื่อนออกไป) / `escalates` (ตึงเครียดขึ้น) / `eases` (คลี่คลายลง) / `post` (หลังประกาศผล) / `hawkish` / `dovish` / `expected` (ป้ายไทยมาตรฐาน) หรืออื่น ๆ + `label_th`.
**ลำดับป้ายที่แสดง:** `label_th` ที่ไม่ว่าง → ป้ายไทยในตัวของ key → `กรณีอื่น` (ไม่โชว์ key ดิบ) · `label_th` ว่าง/ช่องว่างล้วน = ไม่เก็บ.
ข้อเท็จจริงของ event อยู่ที่ `events` ที่เดียว — ห้ามคัดลอก forecast/เวลาไปแต่ละ Asset.

## การ import
1. ตรวจทั้งหมดก่อน (รูปแบบ · วันที่ · timezone · ตัวเลข · tier · event_refs) — ผิด = ไม่เขียนอะไร ข้อมูลเดิมครบ
2. map KEY → Asset: id → alias ที่ประกาศ (`BTC` → `BTCUSD`) → ชื่อที่แสดง (ตรงตัว) · ไม่พบ/กำกวม (`US`) = ข้ามพร้อมเหตุผล ไม่สร้าง Asset · ข้อมูลเฉพาะตลาด (`ref_market`) ต้องตรงกับ Asset ที่ตั้งไว้
3. แสดง preview ✓ matched / ⊘ skipped ก่อนบันทึก · บันทึกเฉพาะที่ map ได้ (ตัวที่ข้ามไม่ล้างข้อมูลอื่น)
4. นำเข้าซ้ำสัปดาห์เดิม = แทนสแนปช็อต (Asset ที่ไม่อยู่ในไฟล์ใหม่ = ไม่มีข้อมูล) แต่ **ไม่ทับ actual ที่ยืนยันแล้วด้วย null** (เก็บ provenance) · event id เดียวกันแต่ kind/metric/period/basis ต่างกัน = รายงาน conflict ใช้ของเดิม
5. ไม่แตะ: Asset ที่เลือก · Note · แผน · ไม้ · Quarterly Macro (Playbook) · สัปดาห์อื่น

## SAMPLE (ตัวเลข/เวลา/ระดับเป็นตัวอย่างเทส ไม่ใช่ข้อมูลจริง)
```json
{"schema":"weeklyImpact/v2","week":"2026-09-28","asof":"2026-09-27T09:00:00+07:00",
 "sources":{"s1":{"name":"SAMPLE calendar","url":"https://example.com/cal","checked_at":"2026-09-27T08:30:00+07:00"}},
 "events":{"sample_core_pce":{"title":"SAMPLE Core PCE","label_th":"SAMPLE เงินเฟ้อ Core PCE","kind":"release","metric":"Core PCE","basis":"YoY","period":"Aug 2026","unit":"%",
   "scheduled_at":"2026-10-01T19:30:00+07:00","time_status":"confirmed","forecast":2.6,"previous":2.7,"previous_revised":false,"actual":null,"status":"scheduled","src_schedule":"s1","src_forecast":"s1"}},
 "assets":{"XAUUSD":{"impact":"HIGH","note":"SAMPLE: เงินเฟ้อกำหนดทิศดอกเบี้ย","event_refs":["sample_core_pce"],
   "interp":{"sample_core_pce":{"mechanism_th":"ตัวเลขเงินเฟ้อมีผลต่อความคาดหวังดอกเบี้ย → ผลตอบแทนจริง → ทอง",
     "scenarios_th":[{"key":"above","text_th":"ถ้าสูงกว่าคาด อาจกดความหวังลดดอกเบี้ย ทองอาจเผชิญแรงขาย"},{"key":"below","text_th":"ถ้าต่ำกว่าคาด ความหวังลดดอกเบี้ยอาจกลับมา"},{"key":"inline","text_th":"ถ้าใกล้เคียงคาด ตลาดอาจหันไปดูข่าวถัดไป"}],
     "watch_th":"ดู Core MoM และการแก้ตัวเลขก่อนหน้า"}}},
  "BTC":{"impact":"LOW","note":"SAMPLE: ไม่มีข่าวสำคัญ","event_refs":[]},"BRENT":{"impact":null,"note":"","event_refs":[]}}}
```
## Firestore rules (ผู้ใช้เพิ่มใน `~/Projects/Research-team/firestore.rules` เอง — โค้ดไม่ deploy)
```
match /users/{uid}/weeklyImpact/{week} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow create, update: if request.auth != null && request.auth.uid == uid
    && week.matches('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    && request.resource.data.schema in ['weeklyImpact/v1', 'weeklyImpact/v2'];
  allow delete: if false;
}
```
