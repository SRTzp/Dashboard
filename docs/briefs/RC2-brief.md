# RC2 — Research Card ดึงตัวเลข Tier ครบ 2 มุม + ปุ่ม "เติมจาก Research" ในบล็อก Tier · เทส 32

> ต่อจาก RC1 + TIER2 · ผู้ใช้ตัดสิน 1 ต.ค.: ทำ**ทั้งคำสั่ง + ปุ่มเติม** · ตัวเลข Tier กิน metrics **7 ช่อง** (เหลือ 5 ให้ตัวเลขธุรกิจ)
> schema `research-card/1.0` **ห้ามเปลี่ยน** (ฟิลด์ · จำนวนสูงสุด · validate · merge ไม่แตะ) · **ห้ามแก้** `research_card.py` / validator ฝั่ง Python · core-size.js / classifyTier ไม่แตะ
> สำรองก่อนแก้: `research-card.backup-pre-RC2.js` · `index.backup-pre-RC2.html` · `research-card-test.backup-pre-RC2.js`

## หลักการ
- metric ที่ใช้ตั้ง Tier ระบุตัวด้วย **รหัสท้ายชื่อ** `[T:<code>]` (schema ไม่มีช่อง id ของ metric) · หน้าจอซ่อนรหัส แสดงชิป "Tier" แทน
- ปุ่มเติม **เติมเฉพาะช่องที่ยังว่าง/ยังไม่ตอบ** · ไม่ทับค่าที่ผู้ใช้กรอก · **ไม่เติม Gate 5** (เป็นวิจารณญาณ) · ผู้ใช้ยังกดเลือก Tier เองเหมือนเดิม

## รหัส 7 ตัว
| code | ช่องในบล็อก Tier | value (string) | unit | ความหมาย |
|---|---|---|---|---|
| `roic` | `#tiRoic` | `"24.5"` | `%` | ROIC (นิยาม RC1) |
| `nd` | `#tiNd` (+ ติ๊ก `netcash`) | `"1.2"` · ติดลบได้ | `x` | ND/EBITDA (นิยาม RC1) · ค่า ≤ 0 = เงินสดสุทธิ |
| `fcf` | `#tiFcf` | `"92"` | `%` | FCF conversion (นิยาม RC1) |
| `rev` | `#tiRev` | `"25.3"` | `%` | รายได้โต TTM เทียบ TTM ปีก่อน |
| `cagr` | `#tiCagr` | `"18.0"` | `%` | CAGR รายได้ 3 ปี (ปีงบล่าสุด เทียบ 3 ปีงบก่อนหน้า) |
| `opm` | `#tiOpm` / `#tiOpmPrev` | `"12.0 / 10.0"` (ปีนี้ / ปีก่อน) | `%` | Op margin ปีงบล่าสุด / ปีงบก่อน |
| `chk` | ติ๊ก `fcf3y` / `capret` / `ocf` | `"yes/yes/no"` (`?` = ไม่รู้) | `-` | FCF บวกครบ 3 ปีงบล่าสุด / มีปันผลหรือซื้อหุ้นคืนใน 12 เดือน / OCF TTM บวก |

## แก้
### 1. `research-card.js` → `promptText`
เพิ่มประโยคนี้ (อังกฤษตามต้นฉบับ) **ต่อจากประโยค "Quality metrics for Tier: …dropping the least useful existing metrics first."** ห้ามแก้/ลบประโยคเดิม

```
Tier metrics: also include revenue growth (TTM vs the prior-year TTM), 3-year revenue CAGR ((latest fiscal-year revenue ÷ revenue three fiscal years earlier)^(1/3) − 1), operating margin for the latest and prior fiscal year written as value "latest / prior" such as "12.0 / 10.0", and one check metric with unit "-" and value "yes/no/?" in this order: FCF positive in each of the last three fiscal years / dividends paid or shares repurchased in the last 12 months / operating cash flow positive over TTM (use "?" when unknown). End each Tier metric name with exactly one code: [T:roic] [T:nd] [T:fcf] [T:rev] [T:cagr] [T:opm] [T:chk]; never put these codes on other metrics. Write Tier values as plain numbers without % or x inside value. Put these seven Tier metrics first and use at most five other metrics; if a Tier input is missing, omit that metric and add it to missing_data instead of estimating.
```

### 2. `research-card.js` → ฟังก์ชันใหม่ (เปิดผ่าน `window`)
- `rcTierCode(name)` → code หรือ `null` (จับ `[T:xxx]` ท้ายชื่อ ไม่สนช่องว่างรอบ)
- `rcMetricLabel(name)` → ชื่อที่ตัดรหัสออก (ใช้ตอนแสดง)
- `rcTierMetrics(card)` → `{roic, nd, fcf, rev, cagr, opm, opmPrev, fcf3y, capret, ocf, netCash, asOf, periods:{code:period}, found:[codes]}`
  - ตัวเลข: ตัด `,` `%` `x` ช่องว่าง → `Number` · ไม่ใช่ตัวเลขจำกัด = `null`
  - `opm`: แยกด้วย `/` → 2 ตัว (ขาดตัวไหน = `null` ตัวนั้น)
  - `chk`: แยกด้วย `/` → `yes`=true · `no`=false · อื่น ๆ = `null` (รับ `ใช่`/`ไม่ใช่` ด้วย)
  - `netCash`: `nd` ≤ 0 → true · `nd` > 0 → false · ไม่มี `nd` → null
  - **การ์ดเก่า (RC1 · ไม่มีรหัส):** ถ้าไม่มี `[T:roic|nd|fcf]` ให้หาจากชื่อแทน — `/ROIC/i` · `/ND\s*\/\s*EBITDA/i` · `/FCF\s*conversion/i` (ตัวแรกที่เจอ) · ตัวอื่นไม่เดา
  - code ซ้ำ = ใช้ตัวแรก · ไม่มี card = `null`
- จุดแสดง metric ใน `render` (บรรทัด `rcMetricGrid` · และจุดอื่นที่แสดง `m.name` ถ้ามี) → ใช้ `rcMetricLabel` + ถ้ามี code ต่อชิปเล็ก `<span class="rcTierTag">Tier</span>`
- `python3 inline-research-card.py` → index.html ได้ sha ใหม่

### 3. `index.html` → บล็อก Tier (`coreTierBlockHtml` · ใช้ทั้งฟอร์มแผนใหม่และ sheet "Tier…")
- แถวปุ่มใต้หัวบล็อก (ต่อจาก `#tiWlInfo`): ปุ่ม **"เติมจาก Research"** `id="tiFillRc"` `data-c-tierfill` + ข้อความเล็ก `id="tiFillMsg"`
  - แสดงเมื่อ ticker นี้มี doc ใน `wlDocMap()` ที่มี `research_card` และ `rcTierMetrics(card).found.length > 0` · ไม่งั้นซ่อนทั้งแถว
  - ฟอร์มแผนใหม่: ticker เปลี่ยน → อัปเดตการแสดงปุ่ม (จุดเดียวกับที่เรียก `coreTiWlShow`)
- กด → `coreTiFillRc()`:
  - ช่องตัวเลข (`tiRoic tiNd tiFcf tiRev tiCagr tiOpm tiOpmPrev`) ว่าง + มีค่า → ใส่ค่า (ตามหน่วยในช่อง: % ใส่เลข % ตรง ๆ เช่น 24.5)
  - ติ๊ก (`fcf3y capret ocf netcash`) ยังไม่ตอบ (`null/undefined`) + มีค่า true/false → ตั้งค่าผ่านทางเดียวกับ `coreTiTk` (ปุ่ม on ตรง)
  - เรียก `coreTiIn()` ครั้งเดียวตอนจบ
  - `#tiFillMsg` = `เติม n ช่อง · ข้าม m ช่องที่กรอกแล้ว · จาก Research {as_of}` · ไม่มีอะไรเติม = `ไม่มีช่องว่างให้เติม`
  - ไม่แตะ Gate 5 · ไม่แตะปุ่มเลือก Tier · ไม่แตะเหตุผล
- ข้อความ "ตัวเลขจาก Research {as_of}" ไม่ต้องบันทึกลงการ์ด (ไม่เพิ่มฟิลด์ใน Firestore)

## เทส
### `research-card-test.js` (node)
- `promptText` (ผ่าน `rcCopy` จำลอง เหมือน RC1) มี `Tier metrics:` · `[T:roic]` · `[T:chk]` · `"12.0 / 10.0"` · และประโยค RC1 ยังอยู่ครบ (`ROIC = NOPAT` · `Return exactly these 15 top-level fields`)
- `rcTierCode` / `rcMetricLabel`: `"ROIC = NOPAT ÷ IC [T:roic]"` → `roic` / `"ROIC = NOPAT ÷ IC"` · ไม่มีรหัส → `null` / ชื่อเดิม
- `rcTierMetrics` การ์ดครบ 7: roic 24.5 · nd −0.3 → netCash true · opm 12/10 · chk `yes/no/?` → true/false/null · ค่า `"24.5%"`/`"1,234"`/`"1.2x"` อ่านได้ · `"n/a"` → null
- การ์ดเก่าไม่มีรหัส (ชื่อ RC1) → ได้ roic/nd/fcf · rev/cagr/opm/chk = null
- การ์ด 12 metrics (7 Tier + 5 อื่น) ผ่าน `rcValidate` (schema เดิม)
- **context ของเทสต้องมี `thaiToday`** (มีแล้วจากการแก้รอบ RC1 — ห้ามลบ)

### `tests/run_tests_phase32.py` (Chromium · 1440 + 430 · mock Firestore)
seed watchlist doc 3 ตัว: `TGRW` การ์ดครบ 7 รหัส (ผ่าน Growth) · `TOLD` การ์ดแบบ RC1 (ไม่มีรหัส) · `TNONE` ไม่มี research_card
1. แผน Core ใหม่ ticker `TGRW` → ปุ่ม "เติมจาก Research" เห็น · กด → ช่องตรงค่า · ติ๊กตรง · ข้อความ "เติม 11 ช่อง …" (7 ตัวเลข + 4 ติ๊ก) · บรรทัด Growth = "Growth: ✓ ผ่าน" หลังตอบ Gate 5 "ไม่" ×3 เอง
2. กรอก ROIC = 5 ก่อนกด → ROIC ยังเป็น 5 · ข้อความบอก "ข้าม 1 ช่อง"
3. ติ๊ก OCF = ไม่ใช่ ก่อนกด → ยังเป็นไม่ใช่
4. Gate 5 / ปุ่ม Tier / เหตุผล ไม่เปลี่ยนหลังกด
5. `TOLD` → เติมแค่ ROIC/ND/FCF (+ netcash จาก ND) · ช่อง Growth ยังว่าง
6. `TNONE` และ ticker ที่ไม่อยู่ Watchlist → ไม่เห็นปุ่ม · เปลี่ยน ticker ในฟอร์มจาก `TNONE` → `TGRW` → ปุ่มขึ้น
7. sheet "Tier…" ของการ์ดเดิม ticker `TGRW` → ปุ่มใช้ได้เหมือนกัน
8. แท็บ Research ของ `TGRW`: ชื่อ metric ไม่มี `[T:` · มีชิป "Tier" 7 อัน · ตัวเลขธุรกิจ 5 ตัวไม่มีชิป
9. 430px: แถวปุ่ม + ข้อความไม่ล้นแนวนอน (เช็กราย element) · ไม่มี console error
- ภาพ `tests/screenshots/rc2-*` (1440 + 430): `fill-before` · `fill-after` (scroll ให้เห็นปุ่ม + ข้อความ + บรรทัดผล) · `research-metrics`

### เทสเก่า
- เคสที่ขัด (เช่น นับ metric / ข้อความชื่อ metric ใน phase 8/19/29) → **แก้ความคาดหวังของเคส (ห้ามลบ ห้ามปล่อยล้ม)** และจดใน `tests/RC2_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- รันครบ: `node research-card-test.js` · `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–32

## นอก Dashboard
- ถ้า `~/Documents/Projects/Research-team/shared/research-card-v1.md` มีข้อความคำสั่งชุดเดียวกัน → เพิ่มประโยค Tier metrics ให้ตรงกัน และรายงานว่าแก้ไฟล์ไหน · ไม่มี = ไม่แตะ

## รายงานกลับ
diff `promptText` + ฟังก์ชันใหม่ · sha ใหม่ · ผลเทส (จำนวนเคสก่อน → หลัง ทุกชุด) · รายชื่อภาพ · ข้อที่ตีความเอง · ไฟล์นอก Dashboard ที่แก้ · ไม่ push ไม่ลบไฟล์

## หลังขึ้นเว็บ (ผู้ใช้)
AVGO → Watch → Research → "อัปเดต Research · คัดลอกคำสั่ง" → รันใน AI ที่ค้นเว็บได้ → นำเข้า → แผน Core / Tier… → "เติมจาก Research" → ตอบ Gate 5 เอง → เลือก Tier
