# macro-playbook-schema.md — Macro Playbook (schema `macroPlaybook/v2` · v1 ยังรับได้)

> **MF1 (15 ต.ค. 2569) — v2:** `assets` = Asset กี่ตัวก็ได้ (≥ 1) · key `A–Z 0–9` 2–12 ตัว (เช่น `XAUUSD` `XAG` `BTC` `BRENT` `US` `USDJPY` `S50`) ไม่บังคับครบ 4 ตัวเดิม ·
> ต่อ Asset เพิ่ม `focus: true|false` (★ Macro ชี้ว่าน่าสนใจตอนนี้) และ `label` (ชื่อแสดง ไม่บังคับ) · `view.watch` ยาวได้ ≤ 200 ตัวอักษร (เดิม 140) ·
> กติกาตรวจเดิมใช้ต่อ (why/change_if บังคับเมื่อ stance ≠ none · drivers ต้องมีจริง · ท่าทีผสมควรมี posture) ·
> **v1 (ครบ 4 Asset: XAUUSD · BTC · BRENT · US) ยังผ่านการตรวจและอ่านเหมือนเดิม** · เวอร์ชันที่เก็บแล้วไม่ถูกแก้
> จับคู่ Sat Asset ↔ Playbook Asset: `satPbKeyOf(satKey)` = (1) `satPbLink[satKey]` ที่ผู้ใช้ตั้ง (`none` = ไม่ผูก) (2) ค่าในตัว `XAUUSD→XAUUSD` · `BTCUSD/BTCUSDT→BTC` · `BRENT→BRENT` (3) key ตรงกับ Asset ใน Playbook ที่ใช้จริงล่าสุด (4) ไม่มี = null ·
> ผูกเองที่แท็บ Flow › แถว Asset › `⋯` › `ใช้กับ Sat` (settings ของ `acctList[0]`)
> `stanceChanges` คิดเฉพาะ Asset ที่เปลี่ยน: Asset ใหม่ (`from:'none'`) · Asset ที่หายไป (`to:'none'`)

ด้านล่างเป็นรายละเอียดช่อง (เขียนตอน v1 — ใช้กับ v2 ได้ยกเว้นตามกล่องด้านบน)

วางเป็น JSON ในแท็บ Flow → panel "Macro ไตรมาส" → [วาง JSON] · เก็บที่ `users/{uid}/macroPlaybook` (ใช้ `sat7dCol('macroPlaybook')`)
**ไม่ใช่** collection `macro` เดิม (ห้ามอ่าน/เขียน) · ฟังก์ชันตัดสินอยู่ที่ `Calc.pb*` (pure) — งาน F2c ใช้ตัวเดียวกัน
`confidence` / `posture` / `if_alt` = แสดงผลอย่างเดียว ไม่มีผลกับฟังก์ชันใดที่เกี่ยวกับขนาดไม้

## ช่องทั้งหมด

| ช่อง | บังคับ | ความหมาย |
|---|---|---|
| `schema` | ✔ | `"macroPlaybook/v2"` (หรือ `"macroPlaybook/v1"` ของเดิม) |
| `quarter` | ✔ | รูปแบบ `YYYYQn` เช่น `2026Q4` (เก่ากว่าไตรมาสปัจจุบัน = เตือน) |
| `status` | ✔ | `draft` (ร่าง ไม่มีผล) · `active` (ใช้จริง) |
| `doc_url` | – | ลิงก์รายงานเต็มของไตรมาส (ไม่มี = เตือน "ยังไม่มีลิงก์รายงานเต็ม") |
| `view.headline` · `view.thesis` | ✔ | หัวข้อ / ใจความ |
| `view.pillars[]` | ✔ ≥1 | `{id, title, note?}` · `id` ไม่ซ้ำ (แสดงเป็นชิป) |
| `view.base` · `view.alt` | – | Scenario สั้น (Base / Alternative) |
| `view.watch` | – | ข้อควรติดตามสัปดาห์นี้ (ข้อความ · ยาว >200 ตัวอักษร = เตือน บันทึกได้ · ไม่ใช่ข้อความ = error) · แสดงใต้ thesis ใน `#pbPanel` และเป็นกล่องจางในช่อง Macro ของแถบดำ (ตัด 2 บรรทัด) |
| `assets` | ✔ | v2: Asset ≥ 1 ตัว (key A–Z 0–9 2–12 ตัว) · v1: ครบ 4 key `XAUUSD` · `BTC` · `BRENT` · `US` |
| `assets.X.focus` | – (v2) | `true` = ★ น่าสนใจ — เรียงขึ้นก่อน · แถบดำแสดงเฉพาะ ★ (≤ 4) |
| `assets.X.label` | – (v2) | ชื่อแสดง (ไม่ใส่ = key) |
| `assets.X.stance` | ✔ | `up` · `up_flat` · `flat` · `down_flat` · `down` · `none` |
| `assets.X.why` · `change_if` | ✔ เมื่อ stance ≠ none | เหตุผล / เงื่อนไขที่จะเปลี่ยนแผน |
| `assets.X.drivers[]` | – | pillar id ที่อ้างถึง — ต้องมีใน `view.pillars` |
| `assets.X.confidence` | – | `low` ต่ำ · `mid` กลาง · `high` สูง |
| `assets.X.posture` | – | วิธีวางตัว/สมมติฐาน (ท่าทีผสมควรมี) |
| `assets.X.if_alt` | – | ถ้า Alternative เกิด |
| `assets.X.doc_url` | – | ลิงก์อ่านเต็มของ asset (ลำดับปุ่ม "อ่านเต็ม": asset → ไตรมาส → "—") |

key ที่ไม่รู้จัก: เก็บไว้ตามเดิม ไม่ลบ · แสดงเป็นคำเตือน (บันทึกได้)

## ตารางแปลงคำ

| คำที่ใช้ในรายงาน | `stance` | แสดง |
|---|---|---|
| Bullish | `up` | ▲ ขึ้น |
| Bullish/Neutral | `up_flat` | ▲▬ ขึ้น/ผสม |
| Neutral | `flat` | ▬ ผสม |
| Bearish/Neutral | `down_flat` | ▼▬ ลง/ผสม |
| Bearish | `down` | ▼ ลง |
| ยังไม่มี / ไม่ครอบคลุม | `none` | — ยังไม่มี |

## ท่าทีผสม (`up_flat` / `down_flat`)

Bias เดิม แต่คาดว่าระยะจำกัด — เขียนสมมติฐานลง `posture` (เช่น "downside อาจจำกัด")
หน้าจอแสดงเป็นบรรทัดจางใต้แถว asset (ข้อความมาจาก `posture` ไม่ใช่ข้อความตายตัว) · ไม่มี `posture` = คำเตือน "ท่าทีผสมควรมีวิธีวางตัว/สมมติฐาน" (บันทึกได้)
`Calc.pbAlign` ให้ป้ายเหมือนท่าทีเต็ม (`up_flat` = `up`) — ความต่างเก็บด้วย `macro_stance` ลงไม้ใน F2c

## เอกสารที่เก็บ (1 เวอร์ชัน = 1 เอกสาร · create เท่านั้น ไม่มี update/delete)

id = `<quarter>-v<3 หลัก>` นับต่อจากเวอร์ชันสูงสุดของไตรมาสนั้น (`2026Q4-v001`, `-v002`, …) · เนื้อหา = JSON ที่วาง + `savedAt` (serverTimestamp) ·
`versionNo` · `prevId` (เวอร์ชันล่าสุดก่อนหน้าทุกไตรมาส หรือ null) · `reason` `{type,text}` | null · `stanceChanges` `{ASSET:{from,to}}` เทียบเวอร์ชัน active ก่อนหน้า
`reason.type`: `trigger` เงื่อนไขเปลี่ยนแผนเกิดแล้ว · `evidence` หลักฐานใหม่ยังไม่ถึงเงื่อนไข · `review` ทบทวนตามรอบ · `fix` แก้คำผิด/ข้อมูล (แต่ท่าทีเปลี่ยน = เตือนส้ม ไม่บล็อก)
เวอร์ชันแรกสุด: reason ไม่บังคับ · หลังจากนั้นบังคับทั้ง type และ text · [เปลี่ยนเป็นใช้จริง] = สร้างเวอร์ชันใหม่เนื้อหาเดิม `status:"active"` (ร่างเดิมยังอยู่)

## ฟังก์ชัน Calc

- `Calc.pbValidate(obj|string, now?)` → `{errors[], warnings[]}` (ข้อความไทยระบุช่อง)
- `Calc.pbDiff(prevActive, next)` → `stanceChanges`
- `Calc.pbEffective(versions, asset, atTime)` → `{state, versionId|null, changedAt|null, stale, posture|null}` — ใช้เฉพาะ active ล่าสุดที่ `savedAt ≤ atTime`; `changedAt` = savedAt ของเวอร์ชัน active แรกในชุดต่อเนื่องที่ท่าทีเท่าค่าปัจจุบัน; `stale` = quarter เก่ากว่าไตรมาสของ atTime (เตือนเท่านั้น)
- `Calc.pbAlign(state, side)` → `with | neutral | against | none` (ป้ายไทย: ตาม · Neutral · สวน · ไม่มี Playbook)

| | long | short |
|---|---|---|
| up / up_flat | with | against |
| flat | neutral | neutral |
| down_flat / down | against | with |
| none | none | none |

- `Calc.pbStanceText(state)` → ไอคอน+คำ · `Calc.pbNextId(list, quarter)` → `{versionNo, id}`

## ตัวอย่างเต็ม (ข้อความตัวอย่าง ไม่ใช่มุมมองจริง)

```json
{
  "schema": "macroPlaybook/v2",
  "quarter": "2026Q4",
  "status": "draft",
  "doc_url": "https://docs.google.com/document/d/EXAMPLE",
  "view": {
    "headline": "หัวข้อตัวอย่าง",
    "thesis": "ข้อความตัวอย่างอธิบายภาพรวม ไม่ใช่มุมมองจริง",
    "pillars": [
      {"id": "P1", "title": "เสาหลักตัวอย่าง 1", "note": "หมายเหตุตัวอย่าง"},
      {"id": "P2", "title": "เสาหลักตัวอย่าง 2"}
    ],
    "base": "Scenario หลักตัวอย่าง",
    "alt": "Scenario ทางเลือกตัวอย่าง",
    "watch": "ข้อควรติดตามตัวอย่าง เช่น ตัวเลขที่จะประกาศสัปดาห์นี้"
  },
  "assets": {
    "XAUUSD": {"stance": "up", "why": "เหตุผลตัวอย่าง", "change_if": "เงื่อนไขเปลี่ยนแผนตัวอย่าง", "drivers": ["P1", "P2"], "confidence": "mid", "focus": true},
    "XAG": {"stance": "up", "why": "เหตุผลตัวอย่าง", "change_if": "เงื่อนไขตัวอย่าง", "focus": true},
    "USDJPY": {"stance": "down", "why": "เหตุผลตัวอย่าง", "change_if": "เงื่อนไขตัวอย่าง", "label": "USD/JPY"},
    "BTC": {"stance": "down_flat", "why": "เหตุผลตัวอย่าง", "change_if": "เงื่อนไขตัวอย่าง", "drivers": ["P1"], "confidence": "low",
            "posture": "downside อาจจำกัด", "if_alt": "ถ้า Alternative เกิด: ตัวอย่าง", "doc_url": "https://docs.google.com/document/d/EXAMPLE-BTC"},
    "BRENT": {"stance": "flat", "why": "เหตุผลตัวอย่าง", "change_if": "เงื่อนไขตัวอย่าง"},
    "US": {"stance": "none"}
  }
}
```
