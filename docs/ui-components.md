# ui-components.md — 7D.3 §0.1–0.4 ฐานราก + Phase 2 (Strategy tile bar) + Phase 3 (Trade Plan card) + Phase 4 (mount จริง)

เอกสารนี้บันทึกฐานรากที่วางไว้ในรอบ 7D.3 ส่วนที่ 0 (0.1–0.8) ของ `index.html` และการต่อยอด Phase 2
(namespace `satV3` — Strategy tile bar, ดู §5b) + Phase 3 (Trade Plan card, ดู §5c) + Phase 4 (ประกอบหน้าจริง, ดู §5d)

**สถานะ ณ จบ 7D.3 รอบที่ 2: ขึ้นจริงแล้ว** — `SAT_V3_ON = true` หน้า Sat ใหม่ (ส่วนที่ 1) mount เข้า `#satV3Panel`
แทนหน้า 7D.2 เดิม (`#sat7dPanel`, ยังอยู่ครบใน DOM ไม่ถูกลบ — ตั้ง `SAT_V3_ON = false` กลับได้ทันทีเป็น regression
escape hatch) `Calc.*` ผูกเข้ากับ `sat7dAcctBase`/`sat7dCalc` เดิมมาตั้งแต่ §0 — ดู §3

---

## 1. ตัวแปรกลาง (§0.1 — design tokens)

ประกาศใน `:root` (ต้นไฟล์ `index.html`) ค่ามาจาก `mockups/sat-mockup.html` และ `mockups/app-mockup.html` เป๊ะ:

| ตัวแปร | ค่า | หมายเหตุ |
|---|---|---|
| `--bg` | `#EEF0F3` | พื้นหลังแอป (ของเดิม `#EBECEF` — เปลี่ยนค่าเท่านั้น ตัวแปรเดิมทั้งแอปยังใช้ชื่อเดิม) |
| `--ink` | `#16181D` | สีพื้นปุ่มหลัก/ตัวหนังสือเข้ม (ของเดิม `#141518`) |
| `--card` | `#FFFFFF` | พื้นการ์ด/panel — ตัวแปรใหม่ (เท่ากับ `--surface` เดิมของแอปอยู่แล้ว) |
| `--mute` | `#7B818C` | ตัวอักษรรอง (ของเดิม `--muted` คือ `#62666E`) |
| `--line` | `#E3E6EA` | เส้นคั่น (ของเดิม `--border` คือ `#E4E6EA`) |
| `--soft` | `#F5F6F8` | พื้นผิวจาง (การ์ดซ้อน/แถบ) |
| `--up` | `#1F9D6B` | สีขึ้น |
| `--dn` | `#D4493F` | สีลง |
| `--flat` | `#9AA0A8` | สีเฉย/ไม่มีทิศ |
| `--warn` | `#C98A12` | สีเตือน |
| `--dark` | `#1D2025` | สีเข้มสุด (ปุ่ม primary/ป้ายเข้ม) |
| `--r-card` / `--r-row` / `--r-btn` / `--r-chip` | `12px` / `10px` / `8px` / `999px` | รัศมีตามสเปก |
| `--sp-4/6/8/10/12/16` | `4px…16px` | ระยะมาตรฐาน |

**นำไปใช้กับสไตล์พื้นฐานทั้งแอปทันที** ตามสเปก 0.1 — ทำโดย "เปลี่ยนค่า" ของตัวแปรเดิมที่มีอยู่แล้ว
(`--bg`, `--border`, `--muted`, `--ink`) ให้ตรงกับ mockup แทนที่จะเปลี่ยนชื่อ selector ทั้งแอป
เพราะตัวแปรเหล่านี้ถูกใช้อยู่แล้วในสไตล์พื้นฐาน (พื้นหลัง/การ์ด/เส้น/ตัวอักษรรอง/ปุ่มหลัก/ชิป) — ผลคือทุกแท็บที่
ยังไม่ถึงคิวจะมีโทนสีใกล้ของใหม่ทันที โดยไม่แตะโครงสร้าง/พฤติกรรมของแท็บไหนเลย
สี `--up/--dn/--flat/--warn/--dark` (กลุ่มสีความหมาย) เป็นตัวแปรใหม่ล้วน **ไม่ได้ไปแทนที่ `--teal/--red/--yellow`
เดิมที่ใช้อยู่ทั่วแอป** (ตัดสินใจเอง — ดูเหตุผลในหัวข้อ "ที่ตัดสินใจเอง" ของรายงาน)

สีบัญชี — ยังใช้ `acctColor()` / `ACCT_PALETTE` เดิม ไม่แตะ

---

## 2. ชิ้นส่วนกลาง (§0.2 — namespace `UI`)

ทุกฟังก์ชันคืน **HTML string** เท่านั้น (ไม่แตะ DOM/state ตรง ๆ) คลาส CSS ทั้งหมดขึ้นต้นด้วย `ui-`
(กันชนกับ `.tile/.chip/.row` ที่มีอยู่แล้วในหน้าอื่นของแอป) สไตล์อยู่ใน `<style>` ท้าย `<head>`

### `UI.acctStrip(fields)`
แถบบัญชี 1 บรรทัด/บัญชี
```js
UI.acctStrip([
  {name:'บัญชีหลัก', color:'#3F6FD8', items:[
    {label:'heat', value:'1.2/6%'},
    {label:'ใหม่', value:'2/2', warn:true, secondary:true}
  ]}
]);
```
`items[].warn` → field นี้ใช้สี `--warn`. `items[].secondary` → บนจอ ≤430px field นี้ถูกซ่อน
**เว้นแต่** `warn:true` ด้วย (field ที่เตือนไม่ถูกซ่อนแม้จะเป็น secondary)

### `UI.tiles(list, selKey)`
ช่องภาพรวม 4 ช่อง (≤430px จัด 2×2 อัตโนมัติด้วย CSS grid)
```js
UI.tiles([{key:'x', title:'XAUUSD', value:'Long · 4/5', sub:'รับ 2600-2610', cls:'ok'}], 'x');
```
`cls` ใส่ได้ `ok|bad|warn|flat` (สีของ `.ui-tile-v`) · `selKey===key` → ใส่คลาส `ui-sel`

**★ 7D.3 Phase 2 — ต่อยอด (backward-compatible, caller เดิมด้านบนยังเรนเดอร์เหมือนเดิมทุกประการ):**
รับ field เสริม 3 ตัว แบบ optional สำหรับช่องที่ต้องการเนื้อหาแบบ Strategy tile (ไอคอนทิศ/badge/ปุ่ม/จุด 5 จุด)
แทนโครง title/value/sub เดิม:
```js
UI.tiles([{
  key:'XAUUSD',
  head: '<div class="ui-tile-th" onclick="...">...ไอคอน+ชื่อ+badge+ปุ่ม...</div>',   // แทน title/value/cls เมื่อส่งมา
  sub: 'รับ 2600 · ต้าน 2680 · ผิด <2580',    // ยัง escHtml ให้เหมือนเดิม (plain text)
  dotsHtml: '<i class="ui-tile-dot ui-dot-up"></i>...',   // HTML ดิบของแถวจุด 5 จุด ต่อท้าย sub
  dim: true   // เพิ่มคลาส ui-dim (ช่องจาง เช่น Bias=งดเทรด)
}], selKey);
```
`t.head` เมื่อไม่ส่งมา → เรนเดอร์ `title/value/sub/cls` แบบเดิมทุกกรณี (ดูเคสทดสอบ round 1 ที่ยังผ่านอยู่)
ตัวอย่างการประกอบจริง: ดู `satV3TileModel()`/`satV3TileHead()`/`satV3TileDotsHtml()` ในหัวข้อ §5 ด้านล่าง

### `UI.planCard(model, adapter)`
การ์ดแผน — ส่วนคำนวณขนาดไม้มาจาก `adapter.sizeLine(model, acct)` (Sat = lot/สัญญา · อนาคต Core = หุ้น)
```js
UI.planCard(
  {sym:'XAUUSD', dir:'L', entry:2650, sl:2630, tp:2700, cancel:2660, rr:'2.0R',
   setups:[{label:'Sweep', on:true}], accts:[{name:'บัญชีหลัก', color:'#3F6FD8'}]},
  {sizeLine:(m,a)=> `XM ${Calc.satLot({...}).lot} lot`}
);
```
**7D.3 Phase 3** — เพิ่ม field เสริมแบบ optional ทั้งหมด (ไม่ส่งมา = เรนเดอร์เหมือนเดิมทุกประการ, ดู payload
ด้านบน):
- `model.id` → ใส่ `data-id` บนการ์ด
- `model.editPrefix` → เช่น `"satV3PlanEdit('i123',"` ทำให้ Entry/SL/TP/Cancel Level กลายเป็น `<input>` แก้ได้
  (`onchange="<editPrefix>'entry',this.value)"` ฯลฯ) — ไม่ใส่ = `<div class="ui-num">` อ่านอย่างเดียวแบบเดิม
- `model.priceChips` → `[{value, onClick}]` แถวชิปราคา (แตะเติม Entry) วางเหนือ nums
- `model.closeBtn` → ปุ่ม ✕ มุมขวาบนของการ์ด (`onclick=`นี่)
- `model.setups[].id` / `.onClick` → ทำให้ชิป setup กดติ๊กได้ (เดิมมีแค่ `label`/`on` แสดงเฉย ๆ)
- `model.addSetupBtn` / `model.editSetupBtn` → ปุ่ม `[+ เพิ่ม]` / `[✎ แก้รายการ]` ต่อท้ายแถว setup chips
- `model.setupsLabel` → บรรทัดข้อความเหนือแถว setup chips (เช่น `"Setup 2/3 · ยังไม่ครบ = นอกแผน"`)
- `model.saveBtn` → `{label, onClick, disabled}` ปุ่มหลักท้ายการ์ด
- `adapter.rowExtra(model, acct)` → HTML เสริมต่อท้ายแต่ละแถวบัญชี (เช่น ✅/⚠️+เหตุผล + ปุ่ม `[ข้าม]`/`[รวมด้วย (นอกแผน)]`)

### `UI.row(model)`
แถว 1 บรรทัด (จุดสีบัญชี · ชื่อ · ป้าย · รายละเอียด · ปุ่ม)
```js
UI.row({color:'#3F6FD8', name:'บัญชีหลัก', tag:'Long', detail:'2650 / SL 2630', btns:[{label:'เข้าแล้ว'}]});
```
**7D.3 Phase 3** — `model.btns[].onClick` (optional) ทำให้ปุ่มกดได้จริง (เดิมเป็น `<span>` เฉย ๆ ไม่มี `onclick`
เปลี่ยนเป็น `<button type="button">` ตอนนี้ — ไม่กระทบ caller เดิมที่เช็คแค่ label/`ui-row` เป็น substring)

### `UI.chips(list)`
```js
UI.chips([{label:'Sweep', on:true}, {label:'BigBar', on:false}]);
```
**7D.3 Phase 3** — `item.onClick` (optional) ทำให้ชิปกดติ๊กได้จริง (เดิมแสดงเฉย ๆ)

### `UI.sheet(html)`
Mac = หน้าต่างลอยกลางจอ · iPhone (≤430px) = แผ่นเลื่อนขึ้นจากล่าง (ตัดสินใจล้วนด้วย CSS media query)
```js
UI.sheet('<b>เนื้อหาข้างใน</b>');
```

**ปุ่มหลักของการ์ดบน ≤430px** — คลาส `.ui-plan-cta.ui-sticky` (นิยามไว้ใน CSS แล้ว รอเรียกใช้ตอนสร้าง
การ์ดแผนจริง) ติดล่างจอเหนือแถบแท็บ เคารพ `env(safe-area-inset-bottom)`

---

## 3. เนื้อหาเป็นรายการข้อมูล (§0.3)

```js
const SAT_ASSETS = [
  {key:'XAUUSD', label:'XAUUSD', ff:'XAU'},
  {key:'BTCUSD', label:'BTC',    ff:'BTC'},
  {key:'S50',    label:'S50',    ff:null},
  {key:'BRENT',  label:'Brent',  ff:'OIL'}
];
const SAT_FACTORS = [
  {k:'trend', label:'Trend'}, {k:'momentum', label:'Momentum'}, {k:'zone', label:'Zone'},
  {k:'sentiment', label:'Sentiment'}, {k:'macro', label:'Macro'}
];
const STRIP_FIELDS = { sat: [...], core: [...] };  // ดูค่าจริงในโค้ด — เป็นแค่ป้าย/ลำดับ ไม่ใช่ตัวเลข
```

หมายเหตุสำคัญ: ค่าเหล่านี้**ยังไม่ได้แทนที่** `SAT7D_ASSETS`/`SAT7D_LABEL`/`SATW_COMPS`/`SATW_COMP_LABEL`/
`SATW_MACRO_KEY` เดิมที่ 7D/7D.2 ใช้งานจริงอยู่ตอนนี้ — เป็นการตัดสินใจเอง (ดูเหตุผลในรายงาน) เพื่อไม่แตะ
โค้ดที่ทำงานอยู่แล้ว ตอนสร้างส่วนที่ 1 จริงค่อยรวมเป็นแหล่งเดียวกัน

`STRIP_FIELDS` ยังเป็นแค่ป้าย/โครง ไม่ใช่ตัวเลขจริง — **ตัวเลขจริง (RPT · heat · โควตา) ต้องอ่านจาก
`settings` เสมอ ห้ามพิมพ์ลงโค้ด UI** (กติกาที่ต้องเคารพตอนต่อเป็น UI จริงในรอบถัดไป — รอบนี้ค่าคงที่
`SAT7D_RPT`/`SAT7D_HEAT_MAX`/`SAT7D_NEW_MAX` ของ 7D/7D.2 เดิมยังเป็นค่าคงที่ในโค้ดเหมือนเดิม ไม่ได้ย้ายไป
settings ในรอบนี้ เพื่อไม่เปลี่ยนพฤติกรรมที่มีอยู่)

---

## 4. ชั้นคำนวณแยก (§0.4 — namespace `Calc`)

ฟังก์ชันล้วน (pure) รับพารามิเตอร์ตรง ๆ ไม่อ่าน `state`/DOM เอง **ผูกเข้ากับโค้ดจริงแล้ว** —
`sat7dAcctBase()`/`sat7dCalc()` (ตัวคำนวณเดิมของ 7D/7D.2) เรียกผ่านชุดนี้แล้วตั้งแต่รอบนี้
พฤติกรรม/ค่าที่ได้เท่าเดิมทุกกรณี (ยืนยันด้วยชุดทดสอบ §7 ใน `tests/`)

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `Calc.satLot({riskAmount, dist, contract, lotStep, minLot})` | ขนาดไม้ Sat (lot/สัญญา) — คืน `{lot, msg}` |
| `Calc.rr(entry, sl, tp)` | Risk:Reward แบบง่าย |
| `Calc.heat(openRiskTHB, capTHB)` | heat% ของบัญชี |
| `Calc.newCount(trades, weekKey, openedKeyFn)` | จำนวนไม้ใหม่ในสัปดาห์ |
| `Calc.readiness({...})` | พร้อมเข้าไม้ไหม — คืน `{ok, reasons[]}` |
| `Calc.sizeRule({macroAlign, trendState, side})` | F2c — กฎขนาดไม้: สวนทั้ง Macro และ Trend = `SAT_MACRO_CUT` (0.6) นอกนั้น 1 — ดู §5h |

`Calc.rr` ยังไม่ถูกผูกเข้าจุดไหนในโค้ดเดิม (dormant เหมือน `UI.*`) — จุดคำนวณ RR ที่มีอยู่แล้วในแอป (ถ้ามี)
ยังใช้ของเดิม ไม่ได้ย้ายมาในรอบนี้ เพื่อจำกัดความเสี่ยงต่อ Core/แท็บอื่น

---

## 5. สวิตช์ (§0.7)

- `SAT7D_ON` — สวิตช์เดิม **ไม่ถูกแตะ** ยังเป็น `true` (แท็บ Sat = 7D.2 เหมือนเดิม)
- `SAT_V3_ON` — สวิตช์ใหม่สำหรับ "ส่วนที่ 1" (หน้า Sat แบบใหม่) ยังเป็น **`false`** จนกว่า Phase 2+3+4 จะเสร็จ
  และทดสอบรวมกันแล้ว (Phase 2 นี้แค่สร้างฟังก์ชัน — ยัง dormant ไม่ mount เข้าหน้าไหนจริง)

---

## 5b. namespace `satV3` (7D.3 Phase 2 — Strategy tile bar, dormant)

ต่อยอดชั้นข้อมูล `satw*` เดิม (ไม่เขียนซ้ำ — เรียกใช้ `satwWeek`/`satwTally`/`satwWrite`/`satwSetBias`/
`satwMacroFF`/`satwCopyFromPrev`/`satwWeekOptions`/`satwViewWeekChanged` ตรง ๆ ทุกจุด) เพิ่มเฉพาะชั้นแสดงผล
ของแถบ Strategy (สเปกส่วนที่ 1 ช่อง B) ยังไม่ถูก mount เข้า DOM จริงในรอบนี้ — เรียกทดสอบตรง ๆ ได้:

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `satV3StrategyBarHtml()` | จุดเข้าเดียว — คืน HTML ทั้งแถบ (4 tile ผ่าน `UI.tiles` + editor ถ้ามี asset ที่เลือกอยู่) |
| `satV3TileModel(asset, wk)` / `satV3TileHead(asset, w)` / `satV3TileDotsHtml(w)` | ประกอบ item สำหรับ `UI.tiles` (ไอคอนทิศ/badge/ปุ่ม [+ แผน]/จุด 5 จุด) |
| `satV3TileBadgeSub(asset, w)` | คืน `{badge, sub}` ตรงกับ `tileHtml()` ใน `sat-mockup.html` ทุกกรณี (Long/Short/งดเทรด/ยังไม่ประเมิน) |
| `satV3EditorHtml(asset, wk)` | ตัวแก้ใต้แถบ — 5 ช่ององค์ประกอบ (แตะวน) + tally + why/แนวรับ/แนวต้าน/ผิดเมื่อ + Bias + เตือน + Macro + คัดลอกสัปดาห์ก่อน |
| `satV3Pick(asset)` | แตะช่อง = กาง/พับ (เก็บที่ `satV3Sel`) |
| `satV3CycleFactor(asset, compKey)` | แตะวนองค์ประกอบ: `null → up → flat → down → null` (ตาม `SAT_V3_CYCLE`) — เขียนผ่าน `satwWrite` ตรง ๆ (ไม่ใช่ `satwSetComp` เดิม ซึ่งเป็นแค่ toggle ไม่ใช่วนครบ 4 สถานะ) |
| `satV3ToggleNote(asset, compKey)` | เปิด/ปิดโน้ตรายองค์ประกอบ (ซ่อนโดย default ตามสเปก — state เก็บใน `satV3NoteOpen`, UI-only ไม่ persist) |
| `satV3SetBias(asset,b)` | wrap `satwSetBias` แล้วพับตัวแก้เอง (`satV3Sel=null`) ตามสเปก "เลือก Bias แล้วพับเอง" |
| `satV3CopyPrev(asset)` | wrap `satwCopyFromPrev` แล้ว re-render |
| `satV3Warnings(asset, w)` | คำเตือน Bias เดิมครบ 4 แบบ: สวนองค์ประกอบ / สวน Trend / ยังไม่มีจุดผิด / เกินโควตาสลับ (flips≥2) |
| `satV3WhyValue(w)` | ค่า `why` ที่แสดง — ถ้า `why` ว่าง fallback ไปใช้ `inv_note` เดิม (ไม่เขียนทับ/ไม่ลบ `inv_note`) |
| `satV3SupportDisplay(w)` / `satV3ResistanceDisplay(w)` | คืน `{values, readonly}` — แนวรับ: ถ้ายังไม่เคยตั้ง `support` (ไม่ใช่ array) fallback ไปโชว์ `comps.zone.levels` เดิมแบบอ่านอย่างเดียว จนกว่าจะแก้ครั้งแรก (เขียนจริงแม้ว่าง) · แนวต้าน: field ใหม่ล้วน ไม่มี fallback |
| `satV3NewPlan(asset)` | Phase 2: stub เฉย ๆ · **แทนที่จริงใน Phase 3 แล้ว** (ดู §5c ด้านล่าง) |

**field ใหม่ของ `satWeek/{weekKey}/{asset}`** (setter ใหม่ใน `satw*`, เขียนผ่าน `satwWrite` เหมือนเดิมทุกตัว):
`satwSetWhy(asset,val)` → `why:string` · `satwSetSupport(asset,text)` → `support:number[]` ·
`satwSetResistance(asset,text)` → `resistance:number[]` (parse comma-separated เหมือน `satwSetZoneLevels` เดิม)
**ไม่ลบ field เดิม** — `inv_note`/`comps.zone.levels` ยังอยู่ครบ ใช้เป็นค่า fallback เท่านั้น

---

## 5c. namespace `satV3` ต่อ (7D.3 Phase 3 — Trade Plan card, dormant)

ต่อยอดจาก §5b — Trade Plan card (สเปกส่วนที่ 1 ช่อง C) ใช้ collection เดิม `satIdeas` (เดียวกับ 7D/7D.2)
ผูกกับ listener เดิมใน `sat7dStart()` — แยกจากไอเดียเก่าด้วย field ใหม่ `v3:true` เท่านั้น (ไอเดียเก่าไม่มี field
นี้ ยังอ่าน/แสดงตามปกติ ไม่ชนกัน) ยังไม่ถูก mount เข้า DOM จริงในรอบนี้ — เรียกทดสอบตรง ๆ ได้

**satConfig (`users/{uid}/satConfig/setups`) — graceful degradation บังคับ (rules อาจยังไม่ deploy):**

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `satV3ConfigStart()` / `satV3ConfigStop()` | เปิด/ปิด listener ของ `satConfig/setups` — อ่านไม่ได้ (permission-denied หรือเหตุอื่น) **ไม่ throw** ตกไปใช้ default ทันที แค่ตั้ง `satConfigErr` ไว้เตือน |
| `satV3DefaultSetups()` | ค่าเริ่มต้น 3 รายการ: Sweep / BigBar / Break Trendline (`SAT_V3_DEFAULT_SETUP_NAMES`) |
| `satV3SetupsFor(asset)` | รายการ setup ของสินค้านั้น — ไม่มีเอกสาร/ไม่มีสินค้านั้นในเอกสาร → default 3 รายการ (แยกตามสินค้าจริง แก้ของ asset หนึ่งไม่กระทบอีก asset) |
| `satV3SetupAdd/Rename/Remove(asset, ...)` | แก้รายการ setup ของสินค้านั้น เขียนผ่าน `satV3ConfigWrite` (`.set({[asset]:list},{merge:true})`) |

**ไอเดีย/แผน (`satIdeas`, `v3:true`):**

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `satV3NewPlan(asset)` | `[+ แผน]` จริง — asset+ทิศจาก Bias ของ Strategy สัปดาห์นี้ (ต้อง Long/Short เท่านั้น) · **มีร่างของ asset นี้อยู่แล้ว (`satV3PlanDraftFor`) → ไม่สร้างซ้ำ** (แค่ชี้ไปที่ร่างเดิมผ่าน `satV3PlanHighlight`) |
| `satV3PlanEdit(ideaId, field, val)` | แก้ `entry/sl/tp/cancel_level` (parse เป็นตัวเลข) หรือ field อื่น (string) |
| `satV3PlanSetupToggle(ideaId, setupId)` | ติ๊ก/เลิกติ๊ก setup ต่อไอเดีย |
| `satV3IdeaDelete(ideaId)` | ✕ ลบร่าง — ลบ**เอกสารไอเดียเท่านั้น** ไม่แตะสมุดไม้ของบัญชีไหนเลย |
| `satV3SetupsReady(idea)` | คืน `{n, total, complete}` — setup ไม่ครบเป็นแค่**คำเตือน** ("ยังไม่ครบ = นอกแผน") ไม่บล็อกการบันทึก |
| `satV3PlanAcctCalc(idea, accId)` | คำนวณต่อบัญชี — เทียบเท่า `sat7dCalc()` เดิมทุกจุด (โบรก/lot/heat/โควตา ผ่าน `Calc.satLot`/`Calc.heat`/`Calc.readiness` เดิมทั้งหมด) ต่างแค่ "setup ไม่ครบ" แทนที่ checklist เดิม เป็นคำเตือนไม่ใช่ตัวบล็อก |
| `satV3ReadyCount(idea)` | จำนวนบัญชีที่ `ready` (ไม่ข้าม ไม่มีไม้แล้ว) — ใช้ตั้งเลขบนปุ่มบันทึก |
| `satV3SkipToggle(ideaId, accId, on)` | ข้าม/เลิกข้ามบัญชีนั้นสำหรับไอเดียนี้ — ข้ามครบทุกบัญชี → ไอเดียปิดเอง |
| `satV3SaveSlot(ideaId, accId)` | บันทึก order 1 บัญชี — เรียก `makeTradeObject()` เดิมทั้งดุ้น (บวก `cancel_level`/`setups` ที่เพิ่มเข้าไปแบบ optional), port `satB` เสมอ, status `plan`, `offplanOverride: !setupsReady.complete` |
| `satV3SaveReadyAccounts(ideaId)` | ปุ่มเดียว "บันทึก order ทุกบัญชีที่พร้อม (n)" — เฉพาะบัญชี ready เท่านั้น |
| `satV3SaveOffplanAccount(ideaId, accId)` | ลิงก์ "รวมด้วย (นอกแผน)" ต่อบัญชี — บันทึกบัญชีที่ไม่ ready แต่ยังคำนวณ lot ได้จริง (เช่น โควตาเต็ม) |

**★ CRITICAL FIX (25 ก.ย. 2569) — plan/open row อ่านจากไม้ในสมุดจริง ไม่ใช่ `idea.status`:**

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `satV3EffectiveTrades(idea)` | ไม้จริงที่ผูกกับไอเดียนี้ (ต่อบัญชี ผ่าน `accts[accId].trade_id`) |
| `satV3PlanRowState(idea)` | `'draft'` (ยังไม่มีไม้ผูกเลย) / `'open'` (มีไม้เปิดอยู่) / `'plan'` (มีไม้รอ order) / `'closed'` (ทุกไม้ปิด/ยกเลิกแล้ว) — คำนวณจากสถานะไม้จริงเสมอ **ไม่ใช่จาก `idea.status`** |
| `satV3ShouldAutoClose(idea)` | true เมื่อทุกบัญชีข้ามหมด **หรือ** ทุกบัญชีที่มีไม้ผูกไว้ไม้นั้น `closed`/`cancelled` แล้วทั้งหมด |
| `satV3MaybeAutoClose(ideaId)` | เขียน `status:'closed'` เมื่อเข้าเงื่อนไขข้างบน — เรียกจาก `satV3SkipToggle`/`satV3RowCancelAll` |
| `satV3ClosedIdeas()` | ตัวกรอง "ปิดแล้ว" — ลบไอเดียจากตรงนี้ (`satV3IdeaDelete`) ไม่แตะไม้ในสมุดเลย |

**บั๊ก race condition ที่เจอ+แก้แล้วในรอบนี้:** `satV3SkipToggle()` เดิมเช็ค auto-close ทันทีหลัง `sat7dWrite()`
แต่ `satIdeasList` อัปเดตผ่าน `onSnapshot` (async) เท่านั้น — ทำให้เช็คแพ้ค่าที่เพิ่งเขียนไปเอง (กรณีข้ามครบทุกบัญชี
ติดกันเร็ว ๆ ไอเดียไม่เคยปิดเอง) แก้โดยเช็คจาก state ที่ merge เอง (optimistic) แทนการพึ่ง listener ตรงจุดนี้ —
ดูรายละเอียดในคอมเมนต์เหนือ `satV3SkipToggle()` ในโค้ด และ `tests/README.md` §Phase 3 (เงื่อนไข "ทุกไม้
ปิด/ยกเลิกแล้ว" ไม่โดนบั๊กนี้ เพราะอ่านสถานะไม้จาก `getBook()` ซึ่งถูกแก้ synchronous ก่อน `saveBook()` เสมอ)

**การประกอบหน้าจอ:**

| ฟังก์ชัน | หน้าที่ |
|---|---|
| `satV3PlanDraftFor(asset)` | หาร่างที่ยังไม่ได้บันทึกสักบัญชีของ asset นั้น (กันสร้างซ้ำใน `satV3NewPlan`) |
| `satV3PlanAdapter` | adapter สำหรับ `UI.planCard` (`sizeLine`/`rowExtra` จาก `satV3PlanAcctCalc`) |
| `satV3DraftCardHtml(idea)` | การ์ดร่าง 1 ใบ — ประกอบ model + เรียก `UI.planCard(model, satV3PlanAdapter)` |
| `satV3RowMarkOpenAll(ideaId)` / `satV3RowCancelAll(ideaId)` | ปุ่ม `[เข้าแล้ว]`/`[ยกเลิก]` บนแถว plan ที่ยุบแล้ว — reuse `sat7dMarkOpen`/`sat7dCancelSlot` เดิมตรง ๆ (ทำทุกบัญชีที่ยัง `plan` พร้อมกัน) |
| `satV3PlanRowsHtml(idea)` | แถว plan/open ที่ยุบแล้ว ผ่าน `UI.row` — แถว open reuse `openClosePos`/`editTrade` เดิมตรง ๆ (ไม่สร้างใหม่) |
| `satV3PlansSectionHtml()` | จุดเข้ารวมของทั้งส่วน Trade Plans — ร่างก่อนเสมอ ตามด้วยแถว plan/open ที่ยุบแล้ว |
| ~~`satV3SetupAddPrompt/EditPrompt(asset)`~~ | **ลบแล้วใน Phase 4** — แทนที่ด้วยช่องพิมพ์ inline จริง (`satV3SetupEditor*`, ดู §5d) |

**field ใหม่ของ `makeTradeObject()`** (additive, ไม่กระทบ caller เดิมที่ไม่ส่งมา): `cancel_level:number|null`,
`setups:string[]|null` — ทั้งคู่ fallback ไปใช้ `prevTrade` เมื่อแก้ไม้เดิม (เหมือน field อื่น ๆ ของฟังก์ชันนี้)

---

## 5d. การประกอบหน้าจริง (7D.3 Phase 4 — mount + `SAT_V3_ON=true`)

### จุดสลับหน้า (`renderSat7d()`)
`renderSat7d()` เป็นจุดเดียวที่ตัดสินว่าจะโชว์หน้าไหน: `SAT_V3_ON=true` → ซ่อน `#sat7dPanel` เดิม เรียก
`satV3ConfigStart()` + `satV3Render()` เข้า `#satV3Panel` แทน · `SAT_V3_ON=false` → พฤติกรรม/DOM เดิมทุกจุด
ไม่เปลี่ยนแม้แต่บรรทัดเดียว (ตัว `#satV3Panel` ก็แค่ถูกซ่อนไว้เฉย ๆ ถ้ามีอยู่ใน DOM) `sat7dRefresh()` (focus-guard
กันเคอร์เซอร์เด้งตอนพิมพ์อยู่) เช็คทั้งสอง panel ตาม `SAT_V3_ON` ปัจจุบัน — พิมพ์ Entry/SL/TP ในการ์ดร่างได้โดย
onSnapshot listener ไม่วาดทับกลางคัน

### §A — `satV3AcctStripHtml()`
แถบบัญชี Sat บนสุดของหน้าใหม่ ผ่าน `UI.acctStrip` — ฟิลด์: ถัง Sat · heat x/6% · ไม้ใหม่ x/2 · RPT · ไม้ Sat x/50
(ตัวเลขเดียวกับ `sat7dSummaryHtml()`/การ์ด `.ports` k==='satB' เดิมทุกจุด ย้ายมาแค่ที่แสดงผล) แทนที่ทั้ง
"การ์ด Satellite.B — Swing" เดิม (`.ports`, ซ่อนเฉพาะตอน `SAT_V3_ON=true` — ดูหัวข้อถัดไป) และ `sat7dSummaryHtml()`
เดิม (ไม่ถูกเรียกจากหน้า Sat อีกต่อไปเมื่อ flag เป็น true — ตัวฟังก์ชันเองยังอยู่ในโค้ด ไม่ได้ลบ เผื่ออนาคต)

**`.ports` (การ์ด port บนสุดของหน้า Plan, `render()`):** เดิมวนทุก port ที่เปิดในสโคปปัจจุบัน (`stock`→core+satA,
`future`→satB เท่านั้น) ตอนนี้ตัดการ์ด k==='satB' ออกจาก loop **เฉพาะตอน `SAT_V3_ON===true`** เท่านั้น
(`!(k==='satB' && SAT_V3_ON)`) — ตอน `false` การ์ดเดิมยังโชว์ปกติทุกจุดเหมือนก่อน Phase 4 (regression escape
hatch ตามสเปก ★ บั๊กที่เจอระหว่างพัฒนา: ตอนแรกตัดแบบไม่มีเงื่อนไข ทำให้ตอน false ก็เสียการ์ดไปด้วย แก้แล้ว)

**Core account strip (scope `stock`, k==='core'):** เปลี่ยนหัวการ์ด (เดิม `.pname`/`.alloc`/`.riskstats`) มาใช้
`UI.acctStrip` — ฟิลด์ตัวเลขเดิมทุกจุด (ทุน/Open Risk/Planned/Positions open-plan) ส่วน `.heatwrap`/`.heatbar`
(แถบภาพ heat) ยังเป็นของเดิม วาดต่อท้ายเหมือนเดิม ไม่ถูกแตะ — **satA ไม่ถูกแตะเลย** (การ์ดเดิม `.pname`/`.riskstats`
คงเดิมทุกจุด, ไม่อยู่ในสโคปของคำสั่ง Phase 4 นี้)

### §D — ลำดับหน้า (`satV3Render()`)
จุดเข้ารวม: `satV3AcctStripHtml()` → `satV3StrategyBarHtml()` (Phase 2) → `satV3PlansSectionHtml()` (การ์ดร่าง
ผ่าน `.ui-pgrid` ก่อน ตามด้วยแถว plan/open ที่ยุบแล้ว ผ่าน `UI.row`, Phase 3) → `sat7dOldPlanHtml()` ("แผนเดิม",
`<details>` พับไว้ อ่านอย่างเดียว — ของเก่าจาก 7D.2 เดิม reuse ตรง ๆ ไม่ต้องสร้างใหม่ เพราะรูปแบบตรงสเปกอยู่แล้ว)
วาดหลัง `sat7dRefresh()` ทุกครั้งจะโฟกัสช่องที่มี `data-autofocus="1"` อัตโนมัติ (ใช้กับช่องเพิ่ม Setup ด้านล่าง)

**`.ui-pgrid`** (CSS ใหม่): Mac `grid-template-columns:repeat(auto-fill,minmax(420px,1fr))` · ≤430px คอลัมน์เดียว
ตามสเปกเป๊ะ — การ์ดร่างแต่ละใบห่อด้วย `.ui-pcell` (รวมช่องแก้ setup inline ที่อาจเปิดอยู่ไว้ในกริดเซลล์เดียวกัน)

### ช่องพิมพ์เพิ่ม/แก้ Setup แบบ inline จริง (แทน `prompt()` ของ Phase 3)
| ฟังก์ชัน | หน้าที่ |
|---|---|
| `satV3SetupEditorOpen(asset, mode)` | เปิดช่องแก้ของ asset นั้น — `mode:'add'` (ช่องพิมพ์เดียว โฟกัสอัตโนมัติ) หรือ `'list'` (รายการทั้งหมด แก้ชื่อ/ลบทีละอัน) — เปิดได้ทีละสินค้าเดียว (`satV3SetupEditor` module var) |
| `satV3SetupEditorClose()` | ปิดช่องแก้ |
| `satV3SetupAddConfirm(asset, inputId)` | อ่านค่าจาก `<input>` จริง (ไม่ใช่ `prompt()`) ยืนยัน → `satV3SetupAdd` แล้วสลับไป mode `'list'` |
| `satV3SetupRenameCommit(asset, id, inputId)` | ผูกกับ `onchange` ของช่องแก้ชื่อในโหมด `'list'` |
| `satV3SetupEditorHtml(asset)` | HTML ของช่องแก้ (ว่างถ้าไม่ตรง asset ที่เปิดอยู่) — วางต่อท้ายการ์ดร่างของ asset นั้นใน `.ui-pcell` |

`addSetupBtn`/`editSetupBtn` ของ `satV3DraftCardHtml` เปลี่ยนจาก `satV3SetupAddPrompt/EditPrompt` (ลบแล้ว) มาเรียก
`satV3SetupEditorOpen(asset,'add'|'list')` แทน · `satV3ConfigStart()`'s onSnapshot เพิ่มเรียก `sat7dRefresh()`
หลังอัปเดต `satConfigSetups` (เดิมไม่เรียก — เพิ่ม/แก้/ลบ setup ไม่เคยขึ้นจอจนกว่าจะมีการ re-render จากที่อื่นโดยบังเอิญ)

---

## 5e. 7D.4 — Strategy 2 องค์ประกอบ + การ์ดแผน 2 ขั้น

**A) Strategy**
- `SAT_FACTORS` = Trend · Zone(`kind:'levels'`) · Macro → `SATW_COMPS_SCORED = ['trend','macro']` (ป้าย `Long · x/2` — F2c เปลี่ยนเป็นป้ายขนาดไม้) — ทุกจุดนับจากตัวนี้ที่เดียว
  ข้อมูลเดิม momentum/sentiment ใน `satWeek.comps` ไม่ลบ แค่ไม่นับ/ไม่แสดง · `SATW_COMPS` (5 ตัว) ยังอยู่สำหรับหน้า 7D.2 เดิม
- ตัวแก้ Strategy ไม่แสดง Fund-flow · **F2c: Macro อ่านจาก Playbook แทนช่องกรอกเอง, `satwMacroFF` ถูกลบ, ป้าย `x/2` → ขนาดไม้ (ดู §5h)**
- "ผิดเมื่อ" → **Trend Shift** (เปลี่ยนแค่ชื่อ · field เดิม `invalidation`) · ช่องพับ `Trend Shift <…` / `>…` · คำเตือน "ยังไม่มี Trend Shift"

**B) การ์ดแผน = 2 ขั้น** (ไอเดีย `v3:true` ที่มี `conditions[]`; ไอเดียเก่าที่ไม่มี `conditions` ใช้การ์ดเดิมทุกอย่าง)
- `conditions[] = {id, text, tp_from, tp_to, inval, active}` · ไอเดียใหม่: `conditions:[], planned:false`
- ขั้นวางแผน: `satV3CondAdd/Edit/Remove` · ปุ่มลัด `SAT_V3_COND_SHORTCUTS` · `satV3PlanSave` → `planned:true` (เขียน satIdeas เท่านั้น ไม่สร้างไม้) → แถว `satV3WaitRowHtml` "รอเงื่อนไข · n ข้อ" (`satV3PlanToggleOpen` กาง/พับ, `satV3Open`)
- ขั้นหน้างาน: `satV3CondActivate` (active ได้ข้อเดียว · ติ๊กข้ออื่น = ย้าย) → ช่อง Entry/SL/TP/Cancel + Setup + แถวบัญชีขึ้น · TP เริ่มต้น = `satV3TpNear` (Long=min · Short=max ของ tp_from/tp_to; TP ที่ผู้ใช้แก้เองแล้วไม่ถูกทับ)
- `satV3SaveSlot`: ไอเดียที่มี conditions ต้องมีข้อ active จึงบันทึกได้ · ไม้ได้ field เสริม `condition_id`, `entry_condition` (สำเนาข้อความ), `tp_zone {from,to}` (`makeTradeObject` เพิ่ม optional + คงค่าเดิมของ `prevTrade`)
- Setup ผ่านเมื่อ ติ๊ก/ทั้งหมด ≥ เกณฑ์: `Calc.setupPass(n,total,minRatio)` · เกณฑ์ `state.settings.satSetupPassRatio` (ค่าเริ่มต้น `SAT_SETUP_PASS_DEFAULT=0.65` · `saveSettings` เก็บค่าไว้ไม่ให้หาย) · ข้อความ `satV3SetupLabel`: "Setup x/y · ต่ำกว่า 65% = นอกแผน"
- `UI.planCard` เพิ่ม optional: `topHtml`, `hideNums`, `hideSetups`, `hideAccts`, `footHtml` (ไม่ส่ง = เหมือนเดิม)
- ช่อง Entry/SL/TP/Cancel Level: สูง 19→25px · ตัวเลข 13.3→15px (`.ui-plan-nums input`)
- **กัน re-render ทับ**: `sat7dTypingGuard(panel)` ใช้ทั้งใน `sat7dRefresh` และ `renderSat7d` (เดิม `render()` ทั้งแอปเรียก `renderSat7d()` ตรง ๆ ทับช่องที่กำลังพิมพ์) + ไม่วาดขณะกดเมาส์ค้างในแผง (ไม่งั้นพิมพ์แล้วกด [บันทึกแผน] ครั้งแรก click หาย)
- ภาพ: `tests/screenshots/7d4-*.png` · เทส: `tests/run_tests_phase5.py`

---

## 5f. 7D.5 — ปรับการ์ดเงื่อนไข (ต่อจาก 5e · โครง `conditions[]` เดิม)

- **แถวพับ "รอเงื่อนไข"** (`satV3WaitRowHtml`, แผน `planned:true` ที่ยังไม่มีข้อ Activate และไม่ได้กาง): หัว `XAUUSD Short · รอเงื่อนไข` + [เปิด] · ใต้หัว 1 แถวต่อเงื่อนไข (`satV3ShortRowHtml`): ข้อความ (ตัดด้วย … · แตะ = `satV3WaitEditCond` กางการ์ด + โฟกัสข้อนั้น) · `TP จาก–ถึง · Inval` (ขาด = "—") + [Activate] [ยกเลิก] · ≤480px ปุ่มลงแถวล่าง
- **`satV3CondActivate`** จากแถว = กางการ์ด (`satV3Open.add`) ที่ขั้นหน้างานโดยเลือกข้อนั้นไว้ · แผนที่มีข้อ active เป็นการ์ดเสมอ (`isWait` ต้อง `!satV3ActiveCond`)
- **ยกเลิก = ซ่อน ไม่ลบ** (`satV3CondCancel`): ข้อ "บันทึกแผนแล้ว" (`satV3CondSaved` = `idea.planned && c.saved!==false`) → `status:'cancelled'` + `cancelled_at` (+ `active:false`) · ข้อที่ยังไม่เคยบันทึก (`saved:false` = เพิ่งพิมพ์) → ลบจริง (`satV3CondRemove`) · ข้อ 7D.4 ที่ไม่มี `status`/`saved` = รออยู่ + บันทึกแล้ว
  - `saved:true` ถูกปั๊มตอน `satV3PlanSave` / พับการ์ด (`satV3PlanToggleOpen`) / Activate · ตัวกรอง: `satV3CondLive` / `satV3CondCancelled` (ทุกที่ที่นับ/แสดงเงื่อนไขใช้ตัวนี้)
  - "ดูที่ยกเลิก (n)" (`satV3CancelledBlockHtml`) แสดงจางอ่านอย่างเดียว · ไม่มีเงื่อนไขเหลือ + ไม่มีไม้ → "ไม่มีเงื่อนไขเหลือ" + [ปิดแผน] (`satV3PlanClose` → `status:'closed'` เฉพาะตอนผู้ใช้กด · ไม่ทำถ้ามีไม้ผูก)
- **ขั้นหน้างาน** (`satV3ActiveBlockHtml`): บรรทัดสรุป `✅ ข้อความ · TP · Inval` + ✎ (`satV3ActiveEditToggle` แก้ข้อความ/TP zone/Inval ในที่) + [ยกเลิก Activate] · เงื่อนไขอื่นย่อเป็น `▸ เงื่อนไขอื่นรออยู่ n ข้อ` (แตะ = แถวสั้น [ใช้ข้อนี้] [ยกเลิก]) · ซ่อนปุ่มลัด/+ เพิ่มเอง/รายการเต็ม · ไม่มี TP zone → เตือนส้ม "ยังไม่ใส่ TP zone" (ยังบันทึก order ได้)
  - [ยกเลิก Activate] / ยกเลิกข้อที่ active: TP ที่ยังเป็นค่าเริ่มต้นของข้อนั้น (`satV3TpNear`) ถูกล้าง ไม่ตกค้างไปข้อถัดไป (TP ที่ผู้ใช้แก้เองไม่ถูกแตะ)
- **แก้คำได้ทุกที่**: ร่าง · หลังบันทึกแผน (แตะข้อความบนแถว → การ์ด) · หลัง Activate (✎) · ไม้ที่บันทึกแล้วไม่เปลี่ยน (`entry_condition` เป็นสำเนา)
- **ปุ่มลัดใช้ร่วมทุก asset**: `users/{uid}/satConfig/conditionTemplates = {items:[{id,text}]}` (`satV3CondTemplates` — ไม่มีเอกสาร/อ่านไม่ได้ = ค่าเริ่มต้น `SAT_V3_COND_SHORTCUTS` ไม่ error, แสดงป้ายเตือนถ้าอ่านไม่สำเร็จ) · ✎ แก้รายการ = เพิ่ม/แก้ชื่อ/ลบ (`satV3CondTplAdd/Rename/Remove` → `satV3CondTplWrite` เขียนทั้งรายการ · เก็บข้อความตามพิมพ์รวมเว้นวรรคท้าย) · rules `satConfig/{docId}` เดิมครอบคลุม
- ไม่มีการเขียน Firestore ตอน render/onSnapshot — ทุกการเขียนมาจากการกดของผู้ใช้
- ภาพ: `tests/screenshots/7d5-*.png` · เทส: `tests/run_tests_phase6.py`

### 7D.6 — จัดวาง Trade Plans (`satV3PlansSectionHtml`) — จัดวางอย่างเดียว ไม่เปลี่ยนพฤติกรรมการ์ด
- การ์ดที่กาง + แถวพับ "รอเงื่อนไข" อยู่ `.ui-pgrid` เดียว (auto-fill `minmax(420px,1fr)` · ≤430px = 1 คอลัมน์ · `align-items:start` แถวพับสูงตามเนื้อหา)
- ลำดับ: กลุ่มกางก่อนเสมอ → กลุ่มพับ · แต่ละกลุ่มเรียง `created_at` เก่า→ใหม่ (เท่ากัน → `id`)
- [Activate]/[เปิด]/แตะข้อความ จากแถวพับ → `satV3ScrollTo` → `satV3Render()` `scrollIntoView` ที่ `.ui-pcell` (block `nearest`; การ์ดสูงเกินจอ = `start`; `scroll-margin` กันจมใต้หัว/แถบแท็บ) · พับการ์ด = ไม่เลื่อนจอ
- แถว plan/open ที่บันทึก order แล้ว (`satV3PlanRowsHtml`) และ "แผนเดิม" อยู่นอก grid ตำแหน่งเดิม
- ภาพ: `tests/screenshots/7d6-*.png` · เทส: `tests/run_tests_phase7.py`

---

## 5g. F2b — Macro Playbook (แท็บ Flow · คลาส `pb*` · ไม่ใช่ชิ้นส่วน UI ใหม่ — ประกอบจาก `UI.chips` + `UI.sheet`)

- panel `#pbPanel` ใต้แถบดำ `#ffAction` (F2c: มี `#ffChanges` คั่นกลาง) · วาดโดย `pbRender()` (เรียกจาก `renderFundflow()` + listener `macroPlaybook`) · ช่อง Macro ในแถบดำอ่านจาก Playbook แล้วใน F2c
- **หลัก 1 หน้า = 1 สรุป**: พับ = 1 บรรทัด (quarter · headline · ป้ายใช้จริง/ร่าง · ไอคอนท่าที 4 ตัว) · แตะหัว 1 ครั้ง = กาง/พับ (`pbToggle`)
- `pbCardHtml(ver, {open, toggle})` = การ์ดชิ้นเดียวที่ใช้ทั้งแผงจริง · พรีวิวก่อนบันทึก · ดูเวอร์ชันในประวัติ (ข้อมูล = เอกสาร `{id,...}`)
- แตะแถว asset → `pbAssetSheet(id, asset)` (`UI.sheet` ซ้อนได้: `pbSheet()` เพิ่มท้าย body · `pbSheetClose()` ปิดบนสุด · แตะพื้นหลังปิด)
- ท่าทีผสม: บรรทัดจาง `.pbMix` = `Calc.pbStanceText(state)` + ` · ` + `posture` (จากข้อมูล ไม่ใช่ข้อความตายตัว) · ช่องที่ไม่มีค่า = ไม่แสดงบรรทัดนั้น
- ตรรกะทั้งหมดอยู่ที่ `Calc.pb*` (pure) — ดู `docs/macro-playbook-schema.md` · เทส `tests/run_tests_phase9.py`

---

## 5h. F2c — ต่อ Macro Playbook เข้า Sat (Strategy · การ์ดขั้นหน้างาน · บันทึก order · แท็บ Flow)

F2c **อ่าน Playbook อย่างเดียว** — ไม่เขียน `macroPlaybook` · ไม่แตะ collection `macro` เดิม · ไม่ลบข้อมูลเดิมใน satWeek/satIdeas/trades

**A) ตัวกลาง**
- `SAT_PB_ASSET` = `{XAUUSD, BTCUSD/BTC→'BTC', BRENT/Brent→'BRENT', S50:null}` (รับทั้ง key จริงของ `SAT_ASSETS` และชื่อป้าย) · `SAT_MACRO_CUT = 0.6` (ค่าเดียว ห้าม hard-code 0.6 ที่อื่น)
- `satMacroOf(asset, atTime, list?)` → `{state, versionId, changedAt, stale, posture, why, change_if, quarter, drivers:[{id,title}]}` = `Calc.pbEffective` + ข้อความจากเวอร์ชันนั้น · S50/ไม่มี Playbook = `state:'none'`, `drivers:[]` · `list` ไม่ส่ง = `pbList` (ส่งเองได้ให้เทส)
- `satMacroTrendOf(state)` แปลง `up·up_flat→up · down·down_flat→down · flat→flat · none→null(ไม่นับ)` · `satwTally(w, asset, atTime)` ส่ง `asset` = Macro นับจาก Playbook (ไม่อ่าน `comps.macro.v`) · ไม่ส่ง = นับจาก comps ตรง ๆ
- `Calc.sizeRule({macroAlign, trendState, side})` → `{factor: 1|0.6, against:{macro, trend}}` · สวนทั้งคู่ = 0.6 · ไม่เจอค่า (`null`/`flat`/`neutral`/`none`) = ไม่สวน
- หน้า Sat วาดใหม่เมื่อ Playbook มาถึง/เปลี่ยน (listener `macroPlaybook` เรียก `sat7dRefresh()`)

**B) Strategy** — Macro ไม่ใช่ช่องกรอกเองอีกแล้ว
- ช่อง Macro (▲▬▼) แสดงจาก Playbook อ่านอย่างเดียว (ไม่มี onclick/✎) · `satV3MacroBlockHtml`: `pbStanceText` + why + "เปลี่ยนเมื่อ: change_if" · ท่าทีผสม = บรรทัดจาง `.pbMix` (`satMixLineHtml` ชิ้นเดียวกับ F2b)
- ไม่มี Playbook: "—" + เตือนส้ม "ยังไม่มี Playbook ใช้จริง" · S50: "— S50 ไม่อยู่ใน Playbook" ตัวจาง ไม่เตือน · stale: "Playbook เป็นของ <quarter>"
- ช่อง **My opinion** ใต้ Macro = `comps.macro.note` เดิม (แก้ได้เสมอ · ไม่มีผลกับคะแนน/ขนาดไม้) · `comps.macro.v` เดิมไม่ลบ ไม่อ่าน ไม่แสดง · ป้าย "ใส่เอง · จะเชื่อม Playbook…" ถูกลบ · `satwMacroFF` ถูกลบพร้อมจุดเรียก
- ป้าย tile `Long · x/2` → `Long · ขนาดไม้ เต็ม` / `Long · ลด 40%` (`satV3WeekSizeRule` = `Calc.sizeRule` จาก bias + Trend ของสัปดาห์ + Macro) · แถบ 2 ขีดเดิมคงไว้ · สัปดาห์เก่าอ่าน Playbook ณ สิ้นสัปดาห์นั้น (`satwAtTime`)
- หน้า 7D.2 เดิม (`SAT_V3_ON=false`): แถว Macro เป็นข้อความอ่านอย่างเดียวจาก Playbook + ช่องโน้ต "My opinion"

**C) การ์ดแผน ขั้นหน้างาน** (`satV3F2c(idea, at)` คำนวณค่าทั้งหมด ณ ตอนเรียก · `satV3F2cHtml` วาดใต้บรรทัดเงื่อนไขที่ Activate · ไอเดียเก่าไม่มี conditions ก็แสดงที่ `topHtml`)
- **Trend**: `Trend ▼ (Strategy จ.) [เปลี่ยน]` → `[ขึ้น][ผสม][ลง]` เขียน `idea.trend_override = {to, at}` เท่านั้น (ไม่แตะ satWeek) · มี override = `Trend ▲ (เปลี่ยนจาก ▼)` + "ใช้ค่า Strategy" (เขียน `trend_override:null`; เลือกเท่าค่า Strategy = ล้างด้วย)
- **Trend Shift**: Long และ Entry < ระดับ / Short และ Entry > ระดับ (ระดับ = `satWeek.invalidation`) → เตือนส้ม + เปิดปุ่ม 3 ตัวทันที · ไม่เปลี่ยน Trend ให้เอง · ไม่บล็อก · ไม่มีระดับ/Entry = ไม่เตือน
- **Macro**: `pbStanceText` + `.pbMix` · ไม่มี Playbook = "Macro: ไม่มี Playbook" · **Driver**: ชิป `P2 · <title>` จาก `satMacroOf().drivers` · ค่าเริ่มต้น = ตัวแรก (ไม่เก็บจนกว่าจะแตะ) · แตะ = `idea.driver` · ค่าที่เก็บไว้ไม่อยู่ในรายการ → ตัวแรก · ไม่มี drivers → "Driver —"
- **ขนาดไม้**: "ขนาดไม้: เต็ม" หรือ "ลด 40% (สวนทั้ง Macro และ Trend)" + ลิงก์ "ใช้ไม้เต็ม (ไม่ตามกฎ)" (`idea.size_full_override`; กดอีกครั้ง = "กลับตามกฎ"; override อยู่ = ป้ายส้ม "ไม่ตามกฎ") · กฎ = เต็ม ไม่มีสวิตช์
- `satV3PlanAcctCalc(idea, accId, f2c?)`: `riskAmount × factor` ผ่าน `Calc.satLot` เดิม · heat จาก lot ใหม่ · ต่ำกว่า minLot = ข้อความเดิมของ satLot · Playbook เปลี่ยนท่าทีภายใน 24 ชม. → ป้ายจาง "Playbook เพิ่งเปลี่ยน <เวลา>" (ข้อมูล ไม่ใช่คำเตือน)

**D) บันทึก order** (`satV3SaveSlot` → `makeTradeObject` เพิ่ม optional · ไม่ส่ง = ไม่มี field · แก้ไม้ภายหลังคงค่า `prevTrade`) — คำนวณใหม่ ณ วินาทีที่กดบันทึก ล็อกแล้วไม่เปลี่ยน
`trend_state` · `trend_changed{from,to}|null` · `macro_state` (`Calc.pbAlign`) · `macro_stance` (6 ค่า) · `playbook_version` · `driver` (อยู่ใน drivers ของเวอร์ชันที่ใช้ ไม่งั้น null) · `size_rule` (1|0.6) · `off_rule` · `macro_note` (สำเนา My opinion) · `macro_recent` · `sizeFactor` (0.6 เมื่อใช้จริง ไม่งั้น null)
- แถวไม้ plan/open มีบรรทัดอ่านอย่างเดียว `satV3F2cTradeLine`: "Macro สวน (▼ v002) · Trend สวน · Driver P2 · ลด 40%" + ป้าย ไม่ตามกฎ / Trend เปลี่ยน / Playbook เพิ่งเปลี่ยน · ไม้เก่าไม่มี field = ไม่แสดง

**E) แท็บ Flow**
- แถบดำ ช่อง Macro: `XAU ▲ · BTC ▲▬ · BR ▼ · US —` (active ล่าสุด · `pbStanceLineText`) + ป้าย `<quarter> v00n` / "ยังไม่มี Playbook ใช้จริง" · แตะ = `pbScrollTo()` เลื่อนไป `#pbPanel` · `pbRender` เรียก `ffRenderActionBar` ด้วย
- `#pbPanel` แถวพับ: ไอคอนมีชื่อ asset กำกับ (`PB_SHORT`) — แก้จาก F2b
- ~~`#ffChanges` (บล็อกพับได้ · `ffRenderChanges`)~~ **ถูกลบใน F2d (§5i)** — เหลือ `ffChangesData` (pure) ใช้ในแถบดำ · รายละเอียดเดิม: หัวพับ = "เพดาน 100% → 75% · 2 ratio พลิก · 3 ธีมเปลี่ยน" / "ไม่มีอะไรเปลี่ยน" / "—" · เพดาน = `Calc.ffCoreCap` จาก `ratios.<ACWI_BIL|HYG_IEI>.prev_week.up` (ต้องมีทั้งสองตัว ไม่งั้น "—") · ratio พลิก = `up ≠ prev_week.up` · ธีม = `quad ≠ prevQuad`
- `rrgCompute` เพิ่ม `prevQuad` (TF W = แท่ง last-1 · TF D = แท่ง last-5) · `RRG_BUILD` 5→6 (แคชเก่าที่ไม่มี prevQuad ถูกดึงใหม่)
- ไม่มี fundflow.json จริง (ข้อมูลตัวอย่าง) = ไม่แสดงบล็อก · ไม่มี prev_week = "—" ไม่ error
- ภาพ: `tests/screenshots/f2c-*.png` · เทส: `tests/run_tests_phase11.py`

---

## 5i. F2d — Playbook `view.watch` + แถบดำ `#ffAction` 4 ช่องใหม่

อ่านอย่างเดียว · ไม่เขียน `macroPlaybook` (นอกทางวาง JSON) · ไม่แตะ collection `macro` · ไม่แก้ `Calc.ffCoreCap` / `rrgCompute`

**A) `view.watch`** (ไม่บังคับ) — `Calc.pbValidate`: รู้จัก key `watch` · ไม่ใช่ string = error `view.watch: ต้องเป็นข้อความ` · ยาว >140 ตัวอักษร = warning (บันทึกได้) · ไม่มี = ไม่เตือน · `#pbPanel` แถวกาง: `ข้อควรติดตาม · <watch>` (`.pbWatch[data-pb=watch]`) ใต้ thesis · ไม่มี = ไม่แสดง · schema: `docs/macro-playbook-schema.md`

**B) แถบดำ** — บรรทัดสรุป (`.ffActSum`) + ป้ายขวา `ข้อมูล <d MMM> · สด` / `· เก่า N วันทำการ` (`[data-ff=fresh]` · เก่า = สีเตือน · ≤2 วันทำการ = สด · demo/ไม่มีไฟล์ = ไม่มีป้าย · แทนช่อง "ความสดข้อมูล" เดิม) · 4 ช่อง (คลาส `ffActCell ffActClick` · แตะ = `ffActGo(id)` เลื่อนไปเป้าหมาย · ข้อมูลขาด = "—")

| ช่อง `data-ff` | เนื้อหา | แตะไป |
|---|---|---|
| `regime` | `ACWI/BIL ↑ เขียว · 3w` / `HYG/IEI ↓ แดง · 1w` (เขียว/แดง · `flip_days` + w/d ตาม `FF_RATIOS.tf`) · ป้าย "เพิ่งพลิก" เมื่อ `up ≠ prev_week.up` (`ffChangesData().flips`) · ไม่มี prev_week = ไม่มีป้าย | `#ffRegime` |
| `lead` | `ffLeadThemes()` (≤2) แสดง `XLK · Technology` (ชื่อตัวเล็กจาง) · ไม่มี = "—" · ใต้นั้นธีม `quad ≠ prevQuad` ≤2 บรรทัด `Energy Lagging→Improving` + `+n` · demo = ไม่แสดง | `#ffThemesPanel` (panel ธีม RRG) |
| `cap` | `C.cap %` ตัวใหญ่ · เหตุผล: มีตัวแดง `<ชื่อ> แดง → ลดเพดาน <100-cap>%` · ไม่มี `ไม่มีตัวแดง` · stale/missing = ข้อความบรรทัดสรุปเดิม · `capChanged` → ป้าย `สัปดาห์ก่อน <capPrev>%` · warn เมื่อ cap<100/stale/missing | `#ffRegime` |
| `macro` | `XAU ▲ · BTC ▲▬ · BR ▼ · US —` แต่ละ asset ห่อ `.as{white-space:nowrap}` (ตัดบรรทัดได้เฉพาะระหว่าง asset) สีเขียว/แดง/เทา · ป้าย `<quarter> v00n` / `ยังไม่มี Playbook ใช้จริง` · `view.watch` ของ active ล่าสุด → กล่อง `ข้อควรติดตาม · …` line-clamp 2 · `savedAt` อยู่ในสัปดาห์นี้ (`wpWeekKey`) → ป้าย `เวอร์ชันใหม่สัปดาห์นี้` | `#pbPanel` |

- grid ใช้ `grid-template-areas`: จอกว้าง `reg lead cap mac` (4 คอลัมน์) · ≤700px 2×2 = `reg cap / lead mac`
- **ลบ**: `#ffChanges`, `ffRenderChanges`, `ffChgToggle`/`ffChgOpen`, CSS `ffChg*` · **เก็บ**: `ffChangesData()` (pure · demo = null) และ `prevQuad` ใน `rrgCompute` · เพิ่ม `id="ffThemesPanel"` บน panel ธีม RRG
- เทส: `tests/run_tests_phase12.py` · ภาพ `tests/screenshots/f2d-{1440,430}-{active,nopb,flow}.png`
- แก้เคสเดิม: phase8 (ช่อง "ความสดข้อมูล" → ป้ายบนบรรทัดสรุป · ชุดช่อง/ป้ายชื่อ 4 ช่องใหม่) · phase9 (`#ffChanges` ไม่แทรกคั่นแล้ว) · phase11 (ลดเคสบล็อก "อะไรเปลี่ยน" ที่ถูกลบ · เคสเทียบสัปดาห์ก่อนย้ายไป phase12)
> UI-1b: สีพื้น/ตัว/pill ของแถบนี้ย้ายไปเป็น token `--sum-*` + คลาสกลาง `.sumBlk/.sumCell/.sumPill/.sumRow…` แล้ว (หน้าตาเดิมเป๊ะ) — ดู §5k

**สไตล์ "ทาง A" (F2d รอบ 2 · ต้นแบบ `docs/mockups/flow-summary-options.html`)** — แก้ HTML/CSS เท่านั้น ไม่แตะตรรกะ/ข้อมูล
- พื้นแถบ `#16191E` · ช่อง `#262A31` padding 12px gap 10px line-height 1.5 · ฟอนต์ปกติของแอป (`--sans`) ทั้งแถบ ไม่มี `--mono` · ตัวเล็กสุด ≥ .72rem เนื้อความ ≥ .8rem · ตัวจาง `#B4BAC4`–`#D9DDE3`
- ป้ายความสดขวาบน: จุดเขียวนำหน้า `28 ก.ย. · สด` (เก่า = จุด/ตัวสีเตือน)
- Regime: ชื่อ ratio ขาวหนักชิดซ้าย + ป้าย `.ffActPill` (nowrap · พื้นเขียว/แดงโปร่ง) ชิดขวา `↑ เขียว · 12w` · เพิ่งพลิก = ป้ายเหลืองแยกใต้แถว `<ชื่อ> เพิ่งพลิก` (`[data-rg-flip]`) · ที่ 430px ป้ายอาจตกลงบรรทัดใต้ชื่อ (ไม่ล้น)
- ธีมนำ: sym หนา + ชื่อเทาอ่อน (ไม่มี " · ") · ธีมเปลี่ยน `↗ Energy → Improving` (ไป Leading/Improving) / `↘ Health Care → Weakening` · `+n ธีม`
- เพดาน: ตัวเลข ~1.9rem หนา (≤420px 1.6rem · warn = สีเตือน) · เหตุผล `HYG/IEI แดง → ลด 25%` · ป้าย `สัปดาห์ก่อน 100%`
- Macro: ตัวหนาเท่า Regime · ป้าย `ใหม่สัปดาห์นี้` (เหลืองเหมือนเพิ่งพลิก) · กล่อง watch = wrapper (`.ffActWatch` มี padding) → หัว `ข้อควรติดตาม` + `.ffActWatchTx[data-mac=watch-tx]` (line-clamp 2 · ไม่มี padding · max-height 3em)
- เคสเดิมที่แก้ตามข้อความ/สีใหม่: phase8 (สีพื้นแถบ `rgb(22,25,30)`) · phase12 (สีป้าย, "XLK Technology", "↗ …→…", "+1 ธีม", "ลด 25%", "ใหม่สัปดาห์นี้", ป้ายความสดไม่มีคำว่า "ข้อมูล")


---

## 5j. UI1 — แถบบัญชีแท็บแผน (2 แถว หุ้น/Future) + Journal แจ้งข้อมูลไม่ครบ

**A) `planStripCardHtml(a, b)` / `planAcctBundle(A)`** — ไม่มีสูตรใหม่ · แยกผลของ `summarize().per[k]` ตามกลุ่มพอร์ตเป็น `sum.split`
- หุ้น = `core`+`satA` · Future = `satB` · `%` = ของทุนรวมบัญชี (ฐานเดียวกับ Open% เดิม) · ผลรวมสองแถว = `s.tot.open/plan` เดิม
- พอร์ตที่บัญชีปิด (`portOn`) = ไม่มีแถวนั้น · ไม่มีไม้ = `Hold —` / `Plan —` (ไม่ใช่ปุ่ม)
- แต่ละแถว: `.acctGrp[data-grp=stock|future]` (data-open-th / plan-th / n-open / n-plan) · ปุ่ม `button.acctJump[data-jump=hold|plan]`
- `ใหม่ n` (`.acctNew`) แสดงเฉพาะ n>0 · รายละเอียดที่กาง (Open%/Plan%/Heat/จำนวนไม้) ไม่เปลี่ยน
- แตะ Hold/Plan → `planJumpToAcct(id)` : `scrollIntoView` ไป `.acctSec[data-acct]` (`scroll-margin` = แถบแท็บ + safe-area / แถบล่าง) + `.flash` 1.5 วิ · ไม่แตะ `planAcctFilter` (ถ้าตัวกรองซ่อนบัญชีนั้น → `'all'` ก่อน) · ไม่กาง/พับแถบ · ไม่มี popup
- แตะที่อื่นของหัวการ์ด = `togglePlanStrip` เดิม (`onkeydown` ตอบเฉพาะเมื่อ target เป็นหัวการ์ดเอง)
- เลย์เอาต์ (UI-1b แก้): `.strip.acctStrip` เป็น **grid** `repeat(auto-fit,minmax(min(360px,100%),1fr))` + `align-items:stretch` → การ์ดที่วางคู่กันสูงเท่ากันเมื่อสถานะเดียวกัน (พับทั้งคู่/กางทั้งคู่) · ต่างสถานะ = `:has(.open):has(:not(.open))` → `align-items:start` (ใบที่พับไม่ยืดตาม) · ≤480px คอลัมน์เดียว · ปุ่ม ≥36px บนมือถือ · ฟอนต์ปกติ ≥0.72rem
- **แถวหุ้น/Future** (`.acctGrp`): grid 2 คอลัมน์ `[ป้าย 3.6em | .acctBtns]` — ปุ่ม Hold/Plan อยู่ใน `.acctBtns` (flex-wrap) จึงตัดบรรทัดแล้วยังตรงแนวกับปุ่มแรก
- **ส่วนหัวสูงเท่ากัน**: `planStripSyncHeads()` (JS · จัดวางอย่างเดียว) วัดหลังวาด → การ์ดที่อยู่แถวเดียวกัน (offsetTop เท่ากัน) ตั้ง `min-height` ของ `.acctRow1` = ค่าสูงสุด ใบที่ไม่มีแถว Future เหลือที่ว่างเท่าหนึ่งแถว (ไม่ใส่ข้อความ) → ส่วนกางรายละเอียดเริ่ม y เดียวกัน · วัดใหม่เมื่อ "ความกว้าง" แถบเปลี่ยน (ResizeObserver) · `.acctRow1{align-content:flex-start}` เนื้อหาชิดบน
- **ลูกศร ▾/▴** (`.acctCaret2`) อยู่มุมขวาบนของการ์ด (`position:absolute` · แถวเดียวกับชื่อบัญชี) ทั้งตอนพับและกาง — ไม่มีช่องว่างเปล่าใต้แถว Future
- **รายละเอียดที่กาง** (`.acctDetail` / `.acctKV`): ฟอนต์ปกติของแอป (ไม่ใช้ `--mono`) ตัวเลขหนา 700 · `฿`/หน่วย (`small`) ตัวรองสีจาง · ตาราง 2 คู่ `[ป้าย|ค่า]` ต่อแถว (grid 4 คอลัมน์ · `.acctKV{display:contents}`): แถว 1 = Open · Plan · แถว 2 = Heat 1R · จำนวนไม้ · แถว 3 = ไม้ใหม่สัปดาห์นี้ (`.acctKV.solo` ชิดซ้าย ช่องขวาว่าง) · ≤480px 1 คู่ต่อแถว · ค่า nowrap (Heat 1R ตัดบรรทัดได้ระหว่างพอร์ต) ชิดขวาตรงแนวคอลัมน์ค่า
- ป้าย "ความเสี่ยงค้าง (Open) · % ของทุนรวมบัญชี" → **`Open`** (คำอธิบายเดิมอยู่ใน `title` ของป้าย) · ค่า = `0.37%฿20,497` · 👁 (`[data-priv-anchor]` บน `<b>` ของ Open) วางซ้ายมือของค่า (`position:absolute` — ไม่ดันเลขให้เยื้องจากแนวชิดขวา)
- `privAnchor()` รองรับ `[data-priv-anchor]` — ปุ่มตา 👁 ของการ์ดบัญชีอยู่ที่ช่อง Open ในรายละเอียดเหมือนเดิม (ไม่ไปเกาะในปุ่ม Hold/Plan)

**B) Journal — `journalMissingOf(t)` / `journalIncomplete()` / `renderJournalIncomplete()` / `jIncGo(acct,id)`** (อ่านอย่างเดียว)
| สถานะ | ช่องที่ต้องมี (ตามที่ฟอร์ม/โมดัลบังคับอยู่แล้ว) | ที่มาในโค้ด |
|---|---|---|
| closed / missed / cancelled | Symbol · Entry>0 · SL>0 · Qty>0 · Entry≠SL | `saveTradeCompute` |
| closed | Exit Price>0 | `saveTradeCompute` · `confirmClosePos` |
| missed | แท็กหรือเหตุผล อย่างน้อยหนึ่ง (`missedTag`\|`missedReason`) | `confirmMissed` |
| cancelled | แท็กหรือโน้ต อย่างน้อยหนึ่ง (`cancelTag`\|`cancelNote`) | `confirmCancel` |
| plan / open | ไม่ตรวจ (ไม่อยู่ใน Journal) | — |
ไม่ตรวจ: วินัย/Setup/exitReason/invalHit (ฟอร์มให้เว้นว่างได้) · field F2c (`trend_state` `macro_state` `driver` …) ไม่ใช่ช่องบังคับ
- `#jIncomplete` (เหนือ `#jStrip`): ต่อบัญชี 1 แถบส้ม `ข้อมูลไม่ครบ n รายการ` (ครบ = ว่างเปล่า) · แตะ = กางรายการในที่ (`jIncOpen`) : วันที่ · symbol · ช่องที่ขาด
- แตะแถว → เปิดตัวแก้ของบัญชีเจ้าของไม้ (`editTrade` / `openMissedModal` / `openCancelModal`) แล้วโฟกัสช่องแรกที่ขาด · แก้ครบแล้วหายเองหลัง `render()`
- คลาส: `.jInc` `.jIncHead` `.jIncList` `.jIncRow` · ทดสอบ: `tests/run_tests_phase13.py`

## 5k. UI-1b — บล็อกสรุป `.sumBlk` (token กลาง + คลาสกลาง) — ใช้ที่ไหน · กติกา "1 ก้อน / หน้า"

จัดวางและสีเท่านั้น — ตัวเลข/ข้อความทุกค่า (heat · risk · sizing · tally · sizeRule) เท่าเดิม · ข้อมูลขาด = "—" · `data-*` เดิมครบ · เทส `tests/run_tests_phase14.py` (เทียบ `index.backup-pre-UI1b.html` ในข้อมูลชุดเดียวกัน)

**Token กลาง** (`:root` · ยกจากแถบ Flow F2d รอบ 2 ค่าเดิมทุกตัว):
`--sum-bg #16191E` (พื้นบล็อก · ไม่ใช่ดำสนิท) · `--sum-cell #262A31` · `--sum-inset #1E2227` · `--sum-line #3A3F48` · `--sum-sel #E6E8EC` · `--sum-fg #F4F5F7` · `--sum-strong #fff` · `--sum-soft #D9DDE3` · `--sum-muted #B4BAC4` · `--sum-faint #9AA0AA` · `--sum-up #6EE7A0` · `--sum-dn #FCA5A5` · `--sum-warn #FCD34D` · `--sum-warn-val #F2B84B` · `--sum-ok #4ADE80` · pill พื้นโปร่ง `--sum-pill-{up,dn,warn,nt}-bg` (+ `--sum-pill-nt` ตัว)

**คลาสกลาง:** `.sumBlk` (บล็อก) · `.sumHead` (`.sumT` ชื่อ · `.sumR` ขวา) · `.sumHint` · `.sumMeta` (บรรทัดรอง · `.sumMr` แถวต่อบัญชี · `.sumM` nowrap · `.sumM.warn` = สีเตือน) · `.sumGrid` · `.sumCell` (+ `.warn` = ตัวเลขใหญ่สีเตือน) · `.sumL` ป้ายช่อง · `.sumBig` ตัวเลขใหญ่ · `.sumSub` · `.sumNw` (nowrap) · `.sumPill` (`.up/.dn/.warn/.nt`) · `.sumRow` + `.sumRowBox` (แถว "ชื่อ + pill" · ช่องเป็น container: แคบกว่า 200px → **ทุกแถวในช่องนั้นเรียงลงเหมือนกัน** ห้ามแถวหนึ่งบรรทัดเดียวอีกแถวสองบรรทัด)
กติกาสี: เขียว/แดงเป็นโทนอ่อนบนพื้นโปร่ง ห้ามสีอิ่มเต็มพื้นใหญ่ · ตัวเล็กสุด ≥ 0.72rem · เนื้อความ ≥ 0.8rem · **ห้าม `var(--mono)`** ในบล็อกสรุป

**ใช้ที่ไหน (กติกา: 1 แท็บ / 1 สโคป = บล็อกสรุป 1 ก้อน · ด้านล่างเป็นพื้นขาว = รายละเอียด/ลงมือ · แถบบัญชีบนสุดยังขาว):**
| ที่ | ก้อนเดียว | ประกอบด้วย |
|---|---|---|
| แท็บ Flow | `#ffAction` (F2d) | บรรทัดสรุป + ป้ายสด + 4 ช่อง (Regime · ธีมนำ · เพดาน Core · Macro) — ใช้ token/คลาสกลาง หน้าตาเดิมเป๊ะ (เทสเทียบ computed style กับก่อนย้าย) |
| Port Future | `#satV3Sum` ใน `#satV3Panel` (`satV3StrategyBarHtml()`) | หัว "Strategy สัปดาห์นี้" + ช่วงวันที่ · `.sumMeta` = แถบ Sat ต่อบัญชี (`satV3AcctMetaHtml()` · ถัง Sat · heat · ไม้ใหม่ · RPT · ไม้ Sat · ค่าเตือน = warn) · 4 tile (`UI.tiles(list, sel, {grid:'sumGrid', cell:'sumCell'})`) · ตัวแก้ `.ui-editor` = แผ่นขาวต่อใต้บล็อก (`.sumBlk.hasEd + .ui-editor` · ขอบบนติดบล็อก ขอบรอบเข้ม) · `satV3AcctStripHtml()` (UI.acctStrip ขาว) เลิกใช้ในหน้านี้ |
| Port หุ้น | `#portsSum` (`render()`) | `.sumSec[data-sum-sec=core]` "Core Port" + (ถ้าเปิด) `.sumSec[data-sum-sec=satA]` "Sat A" เป็นแถวที่ 2 **ในก้อนเดียวกัน** (ห้ามแยกก้อนเข้มที่ 2) · แต่ละ sec: หัว + `ทุน ฿x · y% ของทุนรวม` (👁 เดิม `data-priv="p-port-<k>"` ต่อ sec) · `Positions n open · n plan` · ช่อง Open Risk / Planned / Heat 1R (x.xx / 5R · n/5 ตัว · เพดาน · ป้าย `รวม x% · limit y%` · `.heatbar` เดิมปรับสีบนพื้นเข้ม) · over = ช่อง Open Risk `.warn` + ป้าย warn + `เกิน limit` · satB เดิม (SAT_V3_ON=false) ยังใช้การ์ด `.port` เดิม |
| Journal (7F) | `#jSum` (`renderJournalBody()`) | หัว `Journal · <ชื่อบัญชี>` + ช่วงเวลาพาเนล Closed (`ทั้งหมด` / `ก.ย. 2026`) · 6 ช่อง `.sumCell` (ไม้ปิด · Win Rate · Avg R · P&L ฿ · Max DD % + ฿ · วินัยเฉลี่ย x / 3 + `รีวิวแล้ว n/N`) — ค่าเดิมจาก `journalStats().overall` ของบัญชี `jAcct` · pill โทนอ่อน (Win ≥ 50% · Avg R ≥ 0 · P&L ≥ 0 = `.up` ไม่งั้น `.dn` · ไม่มีข้อมูล = `—`) · `.sumMeta[data-jsum=decision]` 1 บรรทัดตามลำดับ: ไม่มีไม้ปิด → นอกแผน (warn) → `luckyWins` (warn) → ตามแผน · grid 6 คอลัมน์ (≤1100px 3 · ≤700px 2) ช่องสูงเท่ากัน · `#jPorts` ยังเป็นพื้นขาวใต้บล็อก · ใต้แถบส้ม `#jIncomplete` (UI-1 ไม่แตะ) |


**Journal 7F — บริบทบัญชี + พาเนลใหม่:** `jAcct` (ค่าเริ่มต้น = `acctActive` ทุกครั้งที่เปิดแท็บ · ไม่เขียน state · ไม่เปลี่ยน `acctActive`) · แถวชิปบัญชี `#jAcctRow` (ซ่อนถ้ามีบัญชีเดียว) · ทั้งแท็บวาดใน `withAccount(jAcct)` · ปุ่มในแถว (`editTrade` · `delTrade` · `openMissedModal` · `openCancelModal` · `restoreMissed` · `restoreCancelled`) ส่ง account = `jAcct` ทุกจุด · ช่วงเวลา/หุบของพาเนลเขียนลง book ของ `jAcct` ผ่าน `saveBook` · ชิปพอร์ต `#jFilters`: ซ่อนพอร์ตที่บัญชีไม่มี · `satA` ชื่อ "เก็บถาวร" เฉพาะเมื่อมีไม้ satA · ชิปที่ไม่มีในบัญชีใหม่ → `ทั้งหมด`
พาเนลพื้นขาวใหม่ (หน้าจอล้วน อ่านอย่างเดียว): `#setupPanel` สถิติตาม Setup (ใต้ Closed · ใช้ไม้ปิดชุดเดียวกับตาราง = บัญชี + ช่วงเวลา + ชิปพอร์ต · กลุ่ม `< 5` ไม้ = จาง + "(น้อย)") · `#condPanel` เงื่อนไขที่ยกเลิก (จาก `satIdeasList` · หุบเป็นค่าเริ่มต้น · ไม่ขึ้นกับบัญชี/พอร์ต) · เทส `tests/run_tests_phase16.py` · เคสเดิมที่แก้: ไม่มี (ไม่มีเคสเก่าอ้าง `#jStrip`/ชิป "Sat.A")

**Tile Strategy (`.ui-tile.sumCell`):** ไอคอนทิศเดิม · ชื่อ asset หนา · pill `Long/Short · ขนาดไม้ เต็ม` (Long เขียว · Short แดง) / `· ลด 40%` (**warn**) / `ยังไม่ประเมิน` · `งดเทรด` (nt) · รับ/ต้าน/Trend Shift + เหตุผลตัวรอง (ตัดบรรทัดได้) · แถบ 2 ขีด (Trend · Macro) สีตามค่า · เลือกอยู่ = เส้นขอบสว่าง (`box-shadow inset`) · งดเทรด = จาง · ปุ่ม `+ แผน` พื้นสว่างตัวเข้ม มุมขวาบน (≥36px ที่ ≤700px) · grid 4 คอลัมน์ · ≤700px 2×2 · tile ในแถวเดียวกันสูงเท่ากัน (grid stretch)
**ย้ายกติกา:** ปุ่ม `+ แผน` ที่ ≤480px ไม่ลงแถวล่างเต็มความกว้างอีก (กติกาเดิม 7D.3 รอบ 3 เลิกใช้)

**เคสเดิมที่แก้ตาม selector/รูปแบบใหม่ (ไม่ใช่แก้ให้ผ่าน — ค่าที่ตรวจเหมือนเดิม):** phase4 (แถบ Sat = `.sumMr` ไม่ใช่ `ui-acctStrip`) · phase8 (`heat_caps` อ่านเพดานจาก `.sumCell[data-sum=heat]` ด้วย) · phase12 (Regime ที่ ≤700px ป้ายเรียงใต้ชื่อทั้งสองแถว) · phase13 (เทียบค่า acctDetail เฉพาะ `<b>` เพราะป้าย Open เปลี่ยน · เทียบ Port เป็นชุดตัวเลข — รายค่าเต็มอยู่ phase14)

## 5l. BK1 — Backup ครบ (schema 3) · กู้คืนจากไฟล์ · tile Strategy แตะได้ทั้งช่อง

เทส `tests/run_tests_phase15.py` (mock Firestore) · ภาพ `tests/screenshots/bk1-*.png`

**A) Export (`index.html` ส่วน "สำรองข้อมูลลงเครื่อง")** — `bkBuild()` (async) ดึง `satIdeas · satWeek · satConfig · macroPlaybook` สดจาก Firestore (`get({source:'server'})` ครั้งเดียวต่อ collection · timeout 10 วินาที) แล้วประกอบไฟล์ · `bkPayload()` = `(await bkBuild()).json` · `bkTriggerDownload(json, filename)` · `exportBackupNow(manual)` เป็น **async → Promise<boolean>** (เงื่อนไข `stateFromServer` เดิมคงไว้ · `bkCheck` เป็น async ด้วย รอบ/เวลาอัตโนมัติไม่เปลี่ยน · iOS ปิดเหมือนเดิม)
- key ใหม่: `satIdeas / satWeek / satConfig / macroPlaybook` = `[{...data, id}]` ทุก field ตามจริง (Timestamp → `{__ts:true,seconds,nanoseconds}` · restore แปลงกลับ) · คง `doc` / `state` / `watchlistV2` เดิม
- `_meta.schema = 3` · `_meta.counts = {books:{<acctId>:{trades,open,plan,closed}}, satIdeas, satWeek, satConfig, macroPlaybook}` · collection ที่ดึงไม่ได้ → ไม่ใส่ key นั้น · `counts.<k> = null` · `_meta.partial = [ชื่อ...]` + แถบเตือนส้ม "backup ไม่ครบ: …" (auto ไม่ทับด้วยข้อความ "สำเร็จ") · ยังดาวน์โหลดไฟล์ได้
- ใต้ปุ่ม Export (`#bkSummary`): `สำรองแล้ว: 2 บัญชี · 37 ไม้ · แผน Sat 5 · สัปดาห์ 4 · Playbook 1` (หมวดที่ดึงไม่ได้แสดง `?`)
- ข้อจำกัดที่รู้: export ต้องรอ `get()` ก่อนดาวน์โหลด → บน iOS Safari การดาวน์โหลดหลัง `await` อาจไม่นับเป็น user gesture (เดิมก็ถูกบล็อกอยู่แล้ว · auto ปิดบนมือถือ)

**B) กู้คืนจากไฟล์ (`bkRestoreOpen` → `bkRestoreLoad(text, name)` → `bkRsRender` → `bkRestoreRun`)** — ปุ่ม "⟲ กู้คืนจากไฟล์ backup…" ข้างปุ่ม Export · **แยกจาก `phase7mRestoreFromFile` (ไม่แตะ)** · รับ schema 2 และ 3 (`_meta.app` ต้องเป็น `trading-dashboard` · uid ต่าง = เตือนแดงแต่ไปต่อได้)
- พรีวิว = `UI.sheet` (คลาส `.bk-sheet` · `.bkRs*`): ต่อหมวดมี checkbox + "ในไฟล์ / ตอนนี้" (บัญชี = open/plan/closed · Sat = จำนวนรายการ · "ตอนนี้" = ค่าสดจาก Firestore) · **ค่าเริ่มต้นไม่ติ๊กอะไร** · หมวดที่ไม่มีในไฟล์ (schema 2) = disabled
- ยืนยัน: พิมพ์ `กู้คืน` (ไม่ใช่แค่ OK) · ไม่ติ๊ก/พิมพ์ผิด = ไม่เขียนอะไร (ข้อความในหน้าพรีวิว)
- ก่อนเขียน: ดาวน์โหลด `dashboard-backup-before-restore-*.json` ของสภาพปัจจุบัน — ดาวน์โหลดล้ม (หรือดึงหมวดที่จะทับไม่ได้) = **หยุด ไม่กู้**
- วิธีเขียน: บัญชี = `acctBuildBook` แล้ว `saveBook(id)` ทีละบัญชีที่ติ๊ก (ทับ `books.<id>` ทั้งก้อน · บัญชีที่ไม่ติ๊กไม่แตะ · บัญชีที่ไม่มีในแอป = ข้าม + แจ้ง) · `satIdeas/satWeek/satConfig` = `set` ทับทีละเอกสารตาม id (ไม่ลบเอกสารที่เกิน) · `macroPlaybook` = create เฉพาะ id ที่ยังไม่มี (`get()` แล้ว `set`) · id ที่มีแล้ว = ข้าม + แจ้งจำนวน · **ไม่เรียก update/delete**
- จบ: หน้าสรุป "สำเร็จ / ข้าม / ล้มเหลว" ต่อหมวด · ล้มเหลวบางส่วนบอกชัด (หัวข้อเปลี่ยน · แถวสีแดง) · `render()` ใหม่ · ผลอยู่ที่ `bkRestoreLast`

**C) Tile Strategy** — `UI.tiles` รับ field เสริม `t.pick` (โค้ด JS เช่น `satV3Pick('XAUUSD')`): กรอบ `.ui-tile.sumCell` ทั้งใบ = พื้นที่แตะเดียว (`role="button" tabindex="0"` · `.ui-tap` = `cursor:pointer` · Enter/Space เฉพาะเมื่อโฟกัสอยู่ที่กรอบเอง) · **`.ui-tile-th` ไม่มี onclick แล้ว** (กันแตะซ้อน) · ปุ่ม `+ แผน` ยัง `stopPropagation` แยก · tile งดเทรด (จาง) แตะได้ · `satV3Pick` คืนโฟกัสให้ tile เดิมเมื่อแตะด้วยคีย์บอร์ด

**เคสเดิมที่ตรวจ:** ไม่มีเคสเก่าอ้าง `bkPayload` schema 2 · เคส phase4/5 ที่คลิก `.ui-tile-th` / `.ui-tile-a` ยังผ่านตามเดิม (คลิกฟองขึ้นไปที่ tile · comment ใน phase4 ที่ว่า onclick อยู่บน `.ui-tile-th` ล้าสมัยแล้ว)

## 5m. UI2a — จัดหน้าแผง Macro ไตรมาสตอนกาง (`pbCardHtml` · คลาส `pb*` · ไม่แตะหัวพับ `.pbHead`)

เทส `tests/run_tests_phase17.py` (mock Firestore) · ภาพ `tests/screenshots/ui2a-*.png` · การ์ดเดียวกันใช้ทั้งแผงจริง · พรีวิววาง JSON · ดูประวัติ

- **โครง `.pbBody`:** `.pbColL` (thesis → `.pbWatch` → ชิป Pillars → Base/Alt) + `.pbRows` (4 แถว asset) · `.pbCard` เป็น container (`container-type:inline-size` · ชื่อ `pb`) → `@container pb (min-width:720px)` = grid `5fr 6fr` gap 20px (ซ้าย/ขวา) · แคบกว่านั้น (มือถือ · sheet พรีวิว/ประวัติ) = คอลัมน์เดียวตามลำดับ DOM เดิม · ใช้ขนาด container ไม่ใช่ viewport
- **ข้อความ:** thesis/Base/Alt/why `max-width:70ch` · `line-height:1.55` · เนื้อความ 13px · เล็กสุดในส่วนกาง 11.5px
- **`.pbWatch`** (`data-pb="watch"` เดิม): พื้น `--soft` · radius `--r-row` · padding 8px 10px · `.pbWatchK` หัว "ข้อควรติดตาม" (11.5px `--mute` แยกบรรทัด) + `.pbWatchV` (13px) · ถ้า `ver.doc_url` ผ่าน `pbSafeUrl` → `.pbWatchLink` "ดู scenario ↗" = `doc_url + '#events'` (แท็บใหม่) · ไม่มี doc_url = ไม่มีลิงก์ · ไม่มี watch = ไม่มีกล่อง
- **แถว asset `.pbRowW`** (แตะ = `pbAssetSheet` เดิม): บรรทัดบน `.pbRow` = ไอคอนท่าที · ชื่อ · ความมั่นใจ (จาง) · ใต้ลงมา `.pbWhy` 13px `line-clamp:2` (ไม่ใช่ nowrap/ellipsis บรรทัดเดียว · เยื้อง 32px) · padding แถว 8px · เส้นคั่นเดิม
- **`.pbMix` ในการ์ด Playbook:** แสดงเฉพาะ posture (จาง · ไม่มีไอคอน/คำท่าที) · ไม่มี posture = "ท่าทีผสม" · ท่าทีเต็มไม่มี `.pbMix` · **`.pbMix` ของ F2c (`satMixLineHtml` · การ์ด Strategy/Sat) ไม่เปลี่ยน** (ยัง "▼▬ ลง/ผสม · posture" · CSS `.ui-f2c .pbMix` / `.ui-mac .pbMix` เดิม) — CSS ใหม่ scope ใต้ `.pbBody` เท่านั้น
- **เคสเดิมที่แก้ตามหน้าตาใหม่:** phase9 (`.pbMix` ของการ์ด Playbook = posture ล้วน แทน "▲▬ ขึ้น/ผสม · …") · phase12 (`.pbWatch` = หัว `.pbWatchK` + `.pbWatchV` แทนบรรทัดเดียว "ข้อควรติดตาม · …") · เทส F2c (phase11) ไม่แก้

## 5n. CL1 — เก็บกวาด (ซ่อนของเก่า · "แผนที่ปิดแล้ว" · วันที่ยกเลิก · สี P&L 0)

ของที่ซ่อนทุกจุดมีคอมเมนต์ `/* CL1: ลบหลัง 7E */` และ "ไม่เรียกฟังก์ชันวาด" (ไม่ใช่ display:none) · ฟังก์ชัน/ข้อมูลเดิมไม่ถูกลบ

| เรื่อง | ทำอย่างไร |
|---|---|
| แผนเดิม (Weekly Plan) หน้า Sat | `satV3Render` ไม่ต่อ `sat7dOldPlanHtml()` แล้ว · ฟังก์ชันคงไว้ (หน้า 7D.2 ตอน `SAT_V3_ON=false` ยังเรียก — phase4 = 67 เคสเท่าเดิม) |
| บล็อก Sat A แท็บพอร์ต | `satAHide` = ทุน satA = 0 และไม่มีไม้ satA open/plan → ไม่วาด `sumSec` satA · มีไม้ค้าง = แสดงเหมือนเดิม · ไม้ปิดแล้วยังอยู่ Journal ชิป "เก็บถาวร" |
| ข้อความท้ายหน้า `#foot` | `1R: Core x% · heat: Core x% · Sat x% · รวม x% (ฐาน THB @ fx) — sync ผ่าน Firestore` (Sat = `portHeatLimit('satB')`) |
| สำรองข้อมูลลงเครื่อง | รายการหมวดตรง `bkBuild` (บัญชี · Trades · Watchlist · Settings · แผน Sat · Bias สัปดาห์ · Setup Sat · Macro Playbook · Fund-flow · Checklist) + คำเตือนสีเหลือง "ไฟล์มี API key (Twelve Data) ติดไปด้วย" |
| `pnlCls(v)` | หลัก P&L ที่ปัดแล้ว = 0 → ไม่มีคลาสสี · >0 `pnl-pos` · <0 `pnl-neg` · ใช้ที่ตาราง Setup + บล็อกสรุป Journal (`jPorts`) เท่านั้น (ตารางไม้/กลุ่ม ยังใช้ `>=0` เดิม) |
| `jDateShort(iso)` | "2026-09-28…" → `28 ก.ย.` · ปีอื่น `28 ก.ย. 25` · ว่าง/ผิดรูป `—` · ใช้ `JV_MONTHS` เดิม · `data-cond-at` ยังเก็บ ISO · ใช้ที่พาเนลเงื่อนไขที่ยกเลิก + รายการยกเลิกในการ์ด Sat |
| แผง Macro 2 คอลัมน์ | `@container pb (min-width:720px)`: `.pbRows .pbRowW:first-child{border-top:0}` |

### "แผนที่ปิดแล้ว (n)" — `satV3ClosedPlansHtml()` (ใต้ Trade Plans หน้า Sat)
- `<details data-closed-plans>` พับไว้ · n = `satV3ClosedIdeas().length` · n = 0 → ไม่วาดเลย · สถานะกาง/พับจำไว้ใน `satV3ClosedOpen` (snapshot re-render ไม่พับกลับ)
- แถว `.s7ClRow[data-closed-idea]`: asset · Bias · `jWeekLabel(week)` · ผลต่อบัญชี (ไม้ closed · `pnlCls`) · ปุ่ม `small ghost` "ลบ" (สูง ≥ 32px แตะได้บนมือถือ)
- กดลบ → `satV3ClosedDelAsk(id)` เปิด `UI.sheet` (คลาส `s7del-sheet`) ยืนยัน · **ห้าม `confirm()`** · ยืนยัน → `satV3IdeaDelete(id)` ลบเฉพาะเอกสาร `satIdeas/{id}` ไม่แตะ `B.trades`
- ลบล้ม → `satDelErr` → กล่อง `.s7Err[data-sat-del-err]` "ลบแผนไม่สำเร็จ (code)" บนหน้า (ไม่ใช่แค่ console.warn)

## 6. วิธีรันเทส

ดู `tests/README.md` — สรุปสั้น ๆ:
```bash
cd ~/Documents/Dashboard/tests
python3 check_syntax.py      # node --check
python3 run_tests.py         # ชุดทดสอบเต็ม (mock Firestore + Playwright, 1440px + 430px)
python3 run_tests_phase1.py … run_tests_phase18.py   # phase 4 ต้องมีสำเนา SAT_V3_ON=false ผ่าน INDEX_HTML_V3OFF
# เครื่อง Mac นี้: pip3 install playwright + CHROMIUM_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" (ไม่มี node → check_syntax.py รันไม่ได้)
```
