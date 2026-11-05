# Weekly Stock Summary — data contract `stockNews/v1`

ใช้กับการ์ด "Weekly Stock Summary" ในแท็บ Today · ข้อมูลเข้าโดยการ **วาง JSON** (จากสกิล `weekly-stock-news` ที่ผู้ใช้สั่งรันเอง) · **ยังไม่มีการดึงข่าวอัตโนมัติ** — UI จะบอกตรง ๆ ว่า "สรุปสัปดาห์นี้ยังไม่พร้อม" เมื่อไม่มีข้อมูล
เก็บที่ `users/{uid}/stockNews/{editionId}` (editionId = `YYYY-MM-DD` ของ `period_end`) · เก็บฉบับเก่าไว้ · อ่านแล้ว = `stockNewsRead {editionId:true}` ใน settings (ซิงก์ข้ามเครื่อง เก็บ 12 ฉบับ)

## Skill input — รายชื่อหุ้น (ปุ่ม `คัดลอกรายชื่อหุ้น`)
```json
{"stocks":[{"ticker":"AAA","groups":["candidate"]},{"ticker":"BBB","groups":["watchlist"]},{"ticker":"CCC","groups":["candidate","watchlist"]}]}
```
## Output
| field | type | หมายเหตุ |
|---|---|---|
| `schema` | `"stockNews/v1"` | |
| `edition_id` | `YYYY-MM-DD` | = `period_end` |
| `period_start`, `period_end` | `YYYY-MM-DD` | ช่วงข่าวที่ครอบคลุม (แสดงตามจริง ไม่เรียกว่า "สัปดาห์นี้" ถ้าเก่ากว่า 7 วันหลังจบ) |
| `asof` | ISO + offset | เวลาที่ตรวจล่าสุด |
| `sources` | `{id:{name,url?,published_at?}}` | url ต้อง http(s) |
| `stocks` | `{TICKER:{…}}` | |

`stocks[TICKER]`: `groups` [`candidate`/`watchlist`] · `coverage`: `news` (มีข่าวสำคัญ) / `none` (ไม่มีข่าวสำคัญ) / `incomplete` (ข้อมูลไม่ครบ — ไม่ใช่ "ไม่มีข่าว") ·
`status` (เฉพาะ coverage=news): `supports` สนับสนุนมุมมอง / `review` ควรทบทวน / `info` ข้อมูลเพิ่มเติม · `headline_th` · `happened_th` = **ข้อเท็จจริง** · `why_th` = **การตีความ** · `monitor_th` · `source_refs` [id ใน sources] ·
`thesis_ref`: true เฉพาะเมื่อหุ้นนั้นมี Thesis ที่บันทึกไว้จริง (ไม่งั้น UI ไม่อ้างว่าข่าวเปลี่ยน Thesis).
หุ้นที่ไม่อยู่ใน Watchlist/Candidates ตอนนี้ → เก็บไว้แต่แสดงใต้ "ไม่อยู่ในรายการแล้ว" (ไม่สร้าง Watchlist item) · ข้อความทั้งหมดแสดงเป็นข้อความธรรมดา ไม่ใช่ HTML.

## SAMPLE (ตัวอย่างสำหรับเทส ไม่ใช่ข่าวจริง)
```json
{"schema":"stockNews/v1","edition_id":"2026-10-25","period_start":"2026-10-19","period_end":"2026-10-25","asof":"2026-10-25T09:00:00+07:00",
 "sources":{"s1":{"name":"SAMPLE source","url":"https://example.com/a","published_at":"2026-10-21"}},
 "stocks":{"AAA":{"groups":["candidate"],"coverage":"news","status":"review","headline_th":"SAMPLE พาดหัว","happened_th":"SAMPLE ข้อเท็จจริง","why_th":"SAMPLE การตีความ","monitor_th":"SAMPLE ติดตาม","source_refs":["s1"],"thesis_ref":false},
           "BBB":{"groups":["watchlist"],"coverage":"none"}}}
```
## Firestore rules (ผู้ใช้เพิ่มเอง — ไม่ deploy โดยโค้ด)
```
match /users/{uid}/stockNews/{edition} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow create, update: if request.auth != null && request.auth.uid == uid
    && request.resource.data.schema == 'stockNews/v1';
  allow delete: if false;
}
```
