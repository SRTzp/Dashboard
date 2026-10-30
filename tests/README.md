# Tests — Trading Dashboard (7D.3 §0.6)

ชุดทดสอบนี้รันกับ `index.html` ตัวจริง (ไม่มีสำเนา) ผ่าน mock Firestore + Playwright
(headless Chromium) ไม่ต้องมี Firebase project จริง ไม่ต้องต่อเน็ต

## โครงสร้าง
- `mock-firebase.js` — จำลอง `firebase.auth()` / `firebase.firestore()` (compat API) แบบ in-memory
  เก็บ state ในหน่วยความจำของหน้าเว็บ, รองรับ `collection/doc/get/set/onSnapshot/update/delete`,
  `mergeFields`, `FieldValue.delete()` และ auth แบบ email/password จำลอง
- `seed.json` — (CL2-a: ผ่าน `cl2aStripLegacy` แล้ว + มีธง `cl2aResetAt`/`cl2aSatCleanAt` ที่ root = เปิดแอปตรง ๆ ไม่เจอ gate · สร้างใหม่ด้วย `python3 ../tools/cl2a_seed.py` จาก `seed.pre-CL2a.json`) ข้อมูลตั้งต้น: 2 บัญชี (main/fam) มี broker + ทุน Sat ตรงกับเคส §7
  (XAUUSD main/XM → 0.19 lot, S50 main/Pi → 6 สัญญา) และมี field แปลก `_probeX` ติดไว้ในก้อนของ main
  (ทดสอบ §0.5 ว่า field ที่ไม่รู้จักไม่หายตอนโหลด/เซฟ)
- `run_tests.py` — ตัวรันหลัก: เปิดหน้าเว็บที่ 1440px และ 430px, seed ข้อมูล, login, รันชุด assertion
  ทั้งหมด (ดูรายการเคสด้านล่าง), เก็บ console error ทุกข้อความ, จบด้วยสรุป PASS/FAIL
- `check_syntax.py` — เทียบเท่า `node --check` (ดึง inline `<script>` ทุกก้อนมาต่อกันแล้วเช็ค syntax)

## วิธีรัน

ต้องมี **Node.js** และ **Python 3 + playwright (พร้อม Chromium)** เครื่องนี้ไม่มีทั้งคู่ (ไม่มี shell
ที่รัน Chromium ได้) — งานที่ผ่านมาทั้งหมด (7D/7D.2/7D.3) รันชุดนี้ในคอนเทนเนอร์คลาวด์ที่มี Playwright
ติดตั้งไว้แล้ว ไม่ใช่บนเครื่อง Mac นี้โดยตรง ถ้าจะรันบนเครื่องนี้เองครั้งแรก:

```bash
pip install playwright
python3 -m playwright install chromium
```

จากนั้นรันจากโฟลเดอร์นี้ (หรือระบุ path ไปที่ index.html เอง):

```bash
cd ~/Documents/Dashboard/tests
python3 check_syntax.py            # node --check
python3 run_tests.py               # ชุดทดสอบเต็ม (ค่าเริ่มต้นอ่าน ../index.html)

# หรือรันกับไฟล์อื่น/สำเนาที่ staged ไว้ที่อื่น:
python3 run_tests.py /path/to/index.html
# หรือ
INDEX_HTML=/path/to/index.html python3 run_tests.py
```

ถ้า Chromium ที่ลงเองอยู่คนละที่กับ `/opt/pw-browsers/...` (ค่าเริ่มต้นที่ script คาดไว้จากสภาพแวดล้อม
ที่ทดสอบรอบ 7D.3 นี้) ให้ตั้ง `CHROMIUM_PATH=/path/to/chrome` — ถ้าไม่ตั้งและ path เริ่มต้นไม่มีอยู่จริง
script จะปล่อยให้ Playwright หา Chromium ที่ติดตั้งไว้เองแทน

## รวมเคสที่ทดสอบ (ทุกเคสรันซ้ำที่ 1440px และ 430px)

**§7 ตัวอย่างทดสอบมาตรฐาน (จาก dashboard-phase7-spec-v2.md / 7D-brief.md)**
- `Calc.satLot()` ล้วน (ไม่ผ่าน UI) — XAUUSD → 0.19 lot, S50 → 6 สัญญา
- `sat7dCalc()` เส้นทางจริงที่แอปใช้ (ตอนนี้ผ่าน `Calc.satLot` แล้ว) — ได้ค่าเดียวกัน
- BTCUSD ที่ยังไม่ตั้งขนาดสัญญา → lot ว่าง + คำเตือน ไม่ throw
- SL ผิดฝั่ง → lot ว่าง + คำเตือน "SL ผิดฝั่ง"
- 2 บัญชีไม่ปนกัน — fam เห็นเฉพาะโบรกของตัวเอง (IC) ไม่ใช่ของ main (XM) และถัง Sat ไม่ยืมข้ามบัญชี

**§0.5 — field ไม่หายตอนโหลด**
- ใส่ field แปลก `_probeX` ในก้อนข้อมูลจำลอง → โหลด → ยังอยู่ใน `state`
- สั่งบันทึก (`saveBook`) → เอกสารที่เขียนจริงใน mock Firestore ยังมี `_probeX` อยู่ (ไม่ถูกตัดทิ้ง
  เพราะ `TRANSIENT_KEYS` ว่างอยู่ในรอบนี้)
- ตรวจว่ามีแค่ `_probeX` เท่านั้นที่ขึ้นเป็น "unknown field" (ไม่มี field จริงของระบบหลุดมาปนโดยไม่ตั้งใจ)

**§0.1/0.2/0.7 — ฐานรากที่วางไว้รอบนี้**
- ตัวแปรกลางใน `:root` มีค่าเลขฐาน 16 ตรงกับ mockup เป๊ะ (--card/--up/--dn/--warn/--dark/--line/--mute/--soft/--bg/--ink)
- `UI.acctStrip / UI.tiles / UI.planCard / UI.row / UI.chips / UI.sheet` คืน HTML string ที่ถูกต้องสำหรับ
  ตัวอย่าง input (ยังไม่ถูกเรียกใช้จริงในหน้าไหน — ทดสอบแยกได้อิสระ)
- `SAT_V3_ON` มีอยู่จริง (ค่าเริ่มต้น false — ดูเหตุผลในรายงาน) และ `SAT7D_ON` (สวิตช์เดิม) ยังเป็น true ไม่ถูกแตะ

**รีเกรสชัน 7D / 7D.2 — ต้องทำงานเหมือนเดิมทุกอย่าง**
- สลับทุกแท็บ (`switchTab`) ไม่ throw
- ไม่ล้นแนวนอน (`scrollWidth <= viewport width`) ทั้ง 1440px และ 430px
- แท็บแผน (scope future) ยังมี `#sat7dPanel` เหมือนเดิม
- ผังบันทึกไอเดียของ 7D.2 (`sat7dNew()` → เขียนเอกสารจริงใน `satIdeas/`) ยังทำงาน
- จุดเปิด Add Trade ยังอยู่ ไม่ throw (smoke check — ดูหมายเหตุ "ที่ทดสอบไม่ได้" ในรายงานฉบับเต็ม
  เรื่องความลึกของ Core-only Add Trade restriction)
- **console ต้องไม่มี error เลย** ทั้งสอง viewport (รวม `pageerror`/uncaught exception)

## งานต่อไปต้องรันชุดนี้ + รายงานผล
ตามข้อ 0.6 ของสเปก 7D.3 — งานทุกรอบถัดจากนี้ (รวมส่วนที่ 1 — หน้า Sat ใหม่) ต้องรัน
`check_syntax.py` + `run_tests.py` แล้วรายงานผล PASS/FAIL ก่อนส่งงาน และควรเพิ่มเคสใหม่ของงานนั้น ๆ
เข้าไปใน `run_tests.py` (หรือไฟล์แยกในโฟลเดอร์นี้) แทนที่จะลบเคสเดิมทิ้ง

## Phase 1 (7D.3 รอบที่ 2) — `run_tests_phase1.py`
ไฟล์แยก (ไม่แตะ `run_tests.py` เดิม — 56 เคสรอบ 1 ยังต้องผ่าน 100% เหมือนเดิม) ครอบคลุม:

- **item E — บั๊ก Safari `<select>`**: `acctSyncPortSelect()` เปลี่ยนจากซ่อน `<option>` ด้วย `.hidden`
  (Safari native `<select>` เพิกเฉยค่านี้) มาเป็นลบ/เพิ่ม `<option>` จริงใน DOM ทดสอบทั้ง 3 โหมดของ `tPort`:
  1. ไม้ใหม่ (`openTrade`) → เหลือแค่ `core`
  2. บันทึก closed ย้อนหลัง (`openUnplannedClosed`) → `core` + `satB` (satA ไม่มี)
  3. แก้ไม้ satB เดิม (`editTrade`) → `core` + `satB`, ค่าที่เลือกอยู่ยังเป็น satB
  4. แก้ไม้ satA เดิม (`editTrade`) → satA ยังอยู่ให้แก้ได้ ค่าไม่หลุด, satB ไม่ถูกเสนอ
  5. เปิดไม้ใหม่ต่อจากแก้ไม้ satA แล้ว — satA ต้องไม่หลุดกลับมา (regression guard บนตัวแปร module-level
     `tradeSatAOptionValue`)
  6. ไม่มี `<option hidden>` เหลืออยู่เลยในทุกโหมด (นี่คือแก่นของบั๊ก Safari — ทดสอบด้วย DOM inspection ตรง ๆ
     ไม่ใช่แค่เช็คค่า `.value`)
  7. `wPort` (ฟอร์ม Watchlist) ก็ผ่าน DOM-rebuild fix เดียวกัน แต่ยังใช้กติกาเดิม (`portOn()` เฉย ๆ ไม่ผ่านกฎ
     satA-ไม้ใหม่ที่เพิ่มใหม่เฉพาะ `tPort`)
  8. ป้ายที่แสดงของ satB = "Sat" ทุกจุด (`tPort`/`wPort` option label, `PORTS.satB.name`) — key ข้อมูลยังเป็น
     `satB` เหมือนเดิม (ไม่เปลี่ยน storage)
- **รวม `SAT_ASSETS`/`SAT7D_ASSETS` เป็นแหล่งเดียว**: `SAT7D_ASSETS`/`SAT7D_LABEL`/`SATW_MACRO_KEY` (ของเดิม
  ใช้โดย 7D/7D.2) ตอนนี้ derive มาจาก `SAT_ASSETS` ทั้งหมด — ทดสอบว่า shape/ค่าที่ callers เดิมคาดหวังยังเหมือนเดิม
  ทุกประการ (ไม่ประกาศอาเรย์ asset ซ้ำ) และหน้า 7D.2 (`#s7NewAsset`, ขับเคลื่อนด้วย `SAT7D_ASSETS`) ยังเรนเดอร์
  ครบ 4 สินค้า label ถูกต้องหลังรวม

**รัน:**
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase1.py                     # Chromium (ค่าเริ่มต้น)
BROWSER=webkit python3 run_tests_phase1.py       # WebKit — item E เป็นบั๊กเฉพาะ Safari/WebKit ต้องรันที่นี่ด้วย
```

**หมายเหตุสภาพแวดล้อมทดสอบรอบนี้ (25 ก.ย. 2569):** คอนเทนเนอร์คลาวด์ที่ใช้รันชุดนี้ดาวน์โหลด WebKit build
ของ Playwright ไม่ได้ (`playwright install webkit` โดน egress policy บล็อก 403 ที่ `cdn.playwright.dev` และ
`playwright.download.prss.microsoft.com`) — รันได้แค่ Chromium จริงในรอบนี้ ตัวแก้ (ลบ/เพิ่ม `<option>` จริงใน
DOM แทนการซ่อนด้วย `.hidden`) เป็นพฤติกรรม `<select>` มาตรฐานที่ทุก browser (รวม Safari/WebKit) รองรับเหมือนกัน
ไม่ได้พึ่งพฤติกรรมเฉพาะ engine ใดที่ทดสอบไม่ได้ แต่ยังไม่มีการยืนยันด้วย Playwright WebKit จริงในรอบนี้ —
ต้องรันคำสั่ง `BROWSER=webkit python3 run_tests_phase1.py` ซ้ำในสภาพแวดล้อมที่ดาวน์โหลด WebKit ได้ ก่อนถือว่า
"ทดสอบบน WebKit แล้ว" ตามที่สเปกข้อ E ต้องการ

## Phase 2 (7D.3 รอบที่ 2) — `run_tests_phase2.py`
Strategy tile bar (ส่วนที่ 1 ช่อง B, namespace `satV3` — ดู `docs/ui-components.md` §5b) ไฟล์แยกอีกไฟล์
(ไม่แตะเคสรอบ 1/Phase 1 เดิม) — เรียก `satV3*` ตรง ๆ (ยังไม่ mount เข้า DOM จริง ตาม `SAT_V3_ON=false`) ครอบคลุม:

- แถบ 4 ช่องมีครบตาม `SAT_ASSETS` · ช่องที่ยังไม่ประเมินเลย = ไอคอน `?` + "ยังไม่ประเมิน" + ไม่มีปุ่ม [+ แผน]
- แตะวนองค์ประกอบ: `null → ▲ → ▬ → ▼ → null` ครบรอบพอดี (ไม่ใช่แค่ toggle แบบเดิม)
- รวมองค์ประกอบ (▲/▬/▼) ถูกต้อง, ครบ 5/5 ไม่มีข้อความ "ประเมินแล้ว", ยังไม่ครบขึ้น "ประเมินแล้ว n/5"
- เลือก Bias แล้วตัวแก้พับเอง, tile อัปเดต badge/dots ทันที, ปุ่ม [+ แผน] โผล่เมื่อ Long/Short เท่านั้น
- คำเตือน Bias ครบ 4 แบบ: สวนองค์ประกอบ / สวน Trend / ยังไม่มีจุดผิด (หายไปหลังตั้งค่า) / เกินโควตาสลับ
- แนวรับ: fallback จาก `comps.zone.levels` เดิมแบบ readonly จนกว่าจะแก้ครั้งแรก (เขียน `support` จริงแล้วไม่ readonly อีก, `comps.zone.levels` เดิมไม่ถูกลบ)
- why: fallback จาก `inv_note` เดิมถ้ายังไม่มี `why` — เขียน `why` ใหม่แล้ว `inv_note` เดิมไม่หาย
- Bias=งดเทรด: tile จาง (`ui-dim`) badge="งดเทรด" ไม่มีปุ่ม [+ แผน]
- Macro: แสดง Fund-flow จริงเมื่อมี mapping (seed ผ่าน `sat7dWrite`/`rsLoad`) · ไม่มี mapping (S50) → ข้อความ degrade ไม่ throw
- คัดลอกจากสัปดาห์ก่อน: คัดลอก comps/invalidation/inv_note มา แต่ **ไม่คัดลอก Bias** (ต้องเลือกใหม่เสมอ ตามสเปก)
- `UI.tiles` เดิม (round 1, ไม่ส่ง `head`) ยังเรนเดอร์ตาม title/value/sub/cls แบบเดิมทุกประการ (backward-compat)

**ข้อควรระวังตอนเขียนเทสกับ mock Firestore (บันทึกไว้กันหลงอีกรอบ):** `window.firebase.__mockDb.__seedDoc(...)`
เขียนเข้า store ตรง ๆ โดย**ไม่เรียก `notify()`** — ถ้า onSnapshot listener ของ collection นั้นแนบอยู่แล้ว (เช่น
หลัง `sat7dStart()`) การ seed แบบนี้จะไม่มีวันเข้าไปถึง `satWeekMap`/`satIdeasList` เลย ให้เขียนผ่าน path จริงแทน
(เช่น `sat7dWrite('satWeek', weekKey, patch)`) ซึ่งใช้ `doc.set({merge:true})` ของจริงที่เรียก `notify()` ด้วย
— ส่วน one-shot `.get()` (เช่น `rsLoad()` ที่อ่าน `db.collection('macro')...get()`) ไม่ผ่าน listener จึง seed
ด้วย `__seedDoc` ได้ตามปกติ

**รัน:**
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase2.py
BROWSER=webkit python3 run_tests_phase2.py       # ติดปัญหา egress policy เดียวกับ Phase 1 ในคอนเทนเนอร์รอบนี้
```

## Phase 3 (7D.3 รอบที่ 2) — `run_tests_phase3.py`
Trade Plan card (ส่วนที่ 1 ช่อง C, `UI.planCard` + adapter Sat, namespace `satV3` ต่อ — ดู `docs/ui-components.md`
§5c) ไฟล์แยกอีกไฟล์ (ไม่แตะเคสรอบ 1/Phase 1/Phase 2 เดิม) — เรียก `satV3*` ตรง ๆ (ยังไม่ mount เข้า DOM จริง ตาม
`SAT_V3_ON=false`) ครอบคลุม:

- **satConfig graceful degradation** (`users/{uid}/satConfig/setups`): ไม่มีเอกสารเลย → default 3 รายการ
  (Sweep/BigBar/Break Trendline) ไม่ throw · จำลอง permission-denied ด้วย `__denyPath()` ตัวช่วยใหม่ใน
  `mock-firebase.js` (rules ยังไม่ deploy) → ก็ยังไม่ throw ใช้ default ต่อได้ทันที แค่ตั้ง `satConfigErr` ไว้เตือน
- setup add/rename/remove แยกตามสินค้าจริง (แก้ของ XAUUSD ไม่กระทบ S50)
- `satV3NewPlan`: สร้างไอเดียจาก Bias ของ Strategy สัปดาห์นี้ · กด [+ แผน] ซ้ำขณะมีร่างค้างอยู่ → ไม่สร้างซ้ำ
- การ์ดร่าง: price chips จากแนวรับ/แนวต้านเติม Entry ได้ · R-multiple คำนวณถูก (ผ่าน `Calc.rr`) · setup ยังไม่ครบ
  → ข้อความเตือน "ยังไม่ครบ = นอกแผน" เท่านั้น (ไม่บล็อกอะไร)
- `satV3PlanAcctCalc` ให้ค่าตรงกับ `sat7dCalc` เดิมทุกจุด (ตัวเลข §7 canonical case เดิม)
- บันทึก order: ปุ่มเดียว "บันทึก order ทุกบัญชีที่พร้อม (n)" เขียนไม้จริงผ่าน `makeTradeObject()` เดิมทั้งดุ้น —
  `port=satB status=plan cancel_level/setups` ติดไปกับไม้ด้วย field ใหม่ · setup ไม่ครบ → `offplanOverride:true`
- **★ CRITICAL**: หลังบันทึก order แล้ว plan row **ต้องขึ้นทันที** (`satV3PlanRowState()` อ่านจากไม้ในสมุดจริง
  ของแต่ละบัญชี ไม่ใช่จาก `idea.status`) แม้ setup ยังไม่ครบ — และ idea **ไม่ปิดเองเพียงเพราะ 1 บัญชีเปิดไม้อยู่**
  ปิดเองเฉพาะเมื่อทุกบัญชีข้ามหมด หรือไม้ที่ผูกไว้ทุกไม้ปิด/ยกเลิกแล้วเท่านั้น (`satV3ShouldAutoClose`)
- แถว plan/open ที่ยุบแล้ว: ปุ่ม [เข้าแล้ว]/[ยกเลิก] reuse `sat7dMarkOpen`/`sat7dCancelSlot` เดิม (ผ่าน prompt()
  ราคาเข้าจริงเหมือนเดิมทุกจุด — เทสจำลอง dialog ด้วย `page.on('dialog', ...)`), แถว open ปุ่ม [ปิดไม้]/[แก้ SL]
  reuse `openClosePos`/`editTrade` เดิมตรง ๆ (ไม่สร้างฟังก์ชันใหม่ซ้ำ)
- "รวมด้วย (นอกแผน)": ทดสอบด้วยเคสบัญชีที่ **คำนวณ lot ได้จริงแต่ไม่ ready** (โควตาไม้ใหม่สัปดาห์นี้เต็ม
  ไม่ใช่แค่ "ไม่มีโบรก" ซึ่งคำนวณ lot ไม่ได้เลยจึงไม่มีอะไรให้กดยืนยัน) → ลิงก์ปรากฏและกดบันทึกได้จริงแม้ไม่ ready
- ✕ ลบร่าง: ลบเอกสารไอเดียเท่านั้น ไม่แตะจำนวนไม้ในสมุดบัญชีไหนเลย
- ข้ามทุกบัญชี (`satV3SkipToggle`) → idea ปิดเองโดยไม่ต้องบันทึก order สักบัญชี
- `UI.planCard`/`UI.row`/`UI.chips` — payload แบบเดิมของรอบ 1 (ไม่ส่ง field ใหม่ใด ๆ ของ Phase 3) ยังเรนเดอร์
  เหมือนเดิมทุกประการ (backward-compat, ซ้ำกับที่ `run_tests.py` เช็คอยู่แล้ว — ยืนยันอีกชั้นเพราะไฟล์นี้แก้
  `UI.planCard`/`UI.row`/`UI.chips` โดยตรง)

**บั๊กที่เจอจากการเขียนเทสรอบนี้ + วิธีแก้ (แก้ไว้ใน `index.html` แล้ว ไม่ใช่แค่ปรับเทสให้ผ่าน):**
`satV3SkipToggle()` เดิมเรียก `satV3MaybeAutoClose(ideaId)` ทันทีหลัง `sat7dWrite()` — แต่ `sat7dWrite()` เป็น
async (เขียนแล้วรอ `onSnapshot` อัปเดต `satIdeasList` อีกที ไม่ใช่เขียนแบบ synchronous) ทำให้เช็ค auto-close
อ่านค่า `skip` ของ**บัญชีตัวเองที่เพิ่งเขียนไปหมาด ๆ ไม่ทัน** — กรณีข้ามครบทุกบัญชีติดกันเร็ว ๆ (คลิกข้ามบัญชีสุดท้าย)
เช็คจะพลาดค่าที่เพิ่งเขียนไปของตัวเองเสมอ และไม่มีจุดไหนเรียกเช็คซ้ำอีก ⇒ ไอเดียไม่มีวันปิดเอง แก้โดยเปลี่ยนมา
เช็คจาก state ที่ merge เอง (optimistic — เอา `idea` ปัจจุบันมา merge ค่า skip ที่เพิ่งเขียนทับเข้าไปตรง ๆ)
แทนที่จะพึ่ง `satIdeasList` ที่ยังไม่ sync — เคสนี้ครอบคลุมโดยเทส "ข้ามทุกบัญชี -> idea ปิดเอง" ด้านบน
(ตัวเช็คเงื่อนไข "ทุกไม้ปิด/ยกเลิกแล้ว" ไม่โดนบั๊กนี้ เพราะอ่านสถานะไม้จาก `getBook()` ซึ่งเป็น object ในหน่วยความจำ
ตัวเดียวกัน ถูกแก้ synchronous ก่อน `saveBook()` เสมอ ไม่ผ่าน listener แบบ accounts[].skip)

**mock-firebase.js เพิ่มใหม่:** `db.__denyPath(path)` / `db.__allowPath(path)` — จำลอง Firestore security-rules
denial (permission-denied) แบบเจาะจง path ได้ (ใช้กับ `get/set/update/delete/onSnapshot` ทุกจุด) สำหรับทดสอบ
graceful-degradation โดยเฉพาะ — ทดสอบแล้วว่าไม่กระทบชุดเทสเดิม (56+42+52 เคสยังผ่านครบหลังเพิ่ม)

**รัน:**
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase3.py
BROWSER=webkit python3 run_tests_phase3.py       # ติดปัญหา egress policy เดียวกับ Phase 1/2 ในคอนเทนเนอร์รอบนี้
```

## Phase 4 (7D.3 รอบที่ 2) — `run_tests_phase4.py` — mount จริง + `SAT_V3_ON=true`
Phase สุดท้าย — ประกอบหน้า Sat ใหม่เข้า DOM จริง (`#satV3Panel`) แทนหน้า 7D.2 เดิม (`#sat7dPanel`) เมื่อ
`SAT_V3_ON=true` (ค่าจริงในไฟล์ ณ จบรอบนี้) ทดสอบผ่าน **DOM interaction จริง** (คลิก/พิมพ์/dialog) ไม่ใช่เรียก
ฟังก์ชันตรง ๆ แบบ Phase 2/3 อีกต่อไป — ไฟล์แยก ไม่แตะเคสเดิม (round1/Phase1/2/3 ยังผ่านครบ 228 เคสหลัง Phase 4)

ทดสอบ 2 สถานะคู่กัน:
- **v3on** — จาก `../index.html` (ค่าจริง `SAT_V3_ON=true` หลัง Phase 4): mount ถูกจุด (`#satV3Panel` โชว์,
  `#sat7dPanel` ซ่อน) · การ์ด "Satellite.B — Swing" เดิมหายจาก `.ports` เฉพาะตอนนี้ · ลำดับหน้า §D ถูกต้อง
  (แถบบัญชี → Strategy → Trade Plans → แผนเดิม) · คลิก tile จริง + คลิกปุ่ม Bias จริง → tile อัปเดต · คลิก
  `[+ แผน]` จริง → การ์ดร่างโผล่ · grid `.ui-pgrid` ใช้ `repeat(auto-fill,minmax(420px,1fr))` จริงตาม computed style
  · กรอก Entry/SL/TP/Cancel Level ผ่าน `<input>` จริง (ไม่เรียก `satV3PlanEdit` ตรง ๆ) · **ช่องพิมพ์ Setup ใหม่
  โฟกัสอัตโนมัติจริงตอนคลิก `[+ เพิ่ม]`** (แทน `prompt()` ของ Phase 3) พิมพ์ + Enter จริง → เพิ่ม setup จริง ·
  คลิกปุ่มบันทึกจริง → ไม้จริงถูกเขียน (`makeTradeObject`) → การ์ดยุบเป็นแถว → คลิก `[เข้าแล้ว]` จริง (จัดการ
  `prompt()` ราคาเข้าจริงของ `sat7dMarkOpen` เดิมด้วย `page.on('dialog',...)`) → แถวเปลี่ยนเป็น open พร้อมปุ่ม
  `[ปิดไม้]`/`[แก้ SL]` (reuse `openClosePos`/`editTrade` เดิม) · `satConfig` permission-denied บนหน้า mount จริง
  ไม่ throw · แท็บอื่นไม่กระทบ · ไม่ล้นแนวนอนทั้ง 2 viewport
- **v3off** — จากสำเนาที่ตั้ง `SAT_V3_ON=false` กลับชั่วคราว (**regression escape hatch ตามสเปก**): หน้า 7D.2
  เดิมยังทำงานเป๊ะทุกจุด (`#sat7dPanel` โชว์, มี `s7NewAsset`/`s7Sum` ครบ) · การ์ด "Satellite.B — Swing" เดิมใน
  `.ports` **ยังโชว์ปกติเหมือนก่อน Phase 4 ทุกประการ** (ไม่ถูกตัดทิ้งตอน false — นี่คือจุดที่พบบั๊กจริงระหว่างเขียน
  เทสและแก้แล้ว ดูหัวข้อ "บั๊กที่เจอ" ด้านล่าง) · §A Core account strip (scope stock) ใช้ `UI.acctStrip` แล้ว
  (ฟิลด์เดิมครบ: Open Risk/Planned/Positions) — จุดนี้ไม่ผูกกับ `SAT_V3_ON` เลย จึงเหมือนกันทั้ง 2 สถานะ · satA
  ไม่ถูกแตะเลย (การ์ดเดิมยังอยู่)

**บั๊กที่เจอจากการเขียนเทสรอบนี้ + วิธีแก้:** ตอนแรกตัดการ์ด satB ออกจาก `.ports` **แบบไม่มีเงื่อนไข** (ไม่ผูกกับ
`SAT_V3_ON`) ทำให้ `SAT_V3_ON=false` ก็เสียการ์ดเดิมไปด้วย ขัดกับข้อกำหนด "keeping the OLD 7D.2 view fully
intact" — แก้โดยผูกเงื่อนไขการตัดการ์ดกับ `SAT_V3_ON===true` เท่านั้น (`!(k==='satB' && SAT_V3_ON)`)

**ข้อควรระวังตอนเขียนเทส DOM จริง (บันทึกไว้กันหลงอีกรอบ):** field ของ `UI.planCard` (Entry/SL/TP/Cancel Level)
ใช้ `onchange` (ไม่ใช่ `oninput`) — `page.fill()` เพียงอย่างเดียว**ไม่ commit ค่าจนกว่า input จะ blur ก่อน** ถ้า
`page.fill()` ติด ๆ กันหลายช่องโดยไม่ blur ค่าจะ "เหลื่อมไปหนึ่งจังหวะ" (ช่องแรกยังไม่ commit จนกว่าช่องถัดไปจะโฟกัส
ทำให้ช่องแรก blur) ต้อง `el.blur()` เอง (ผ่าน `page.evaluate`) หลัง `page.fill()` ทุกครั้งก่อนอ่านผลกลับ — ดู
`fill_and_blur()` helper ใน `run_tests_phase4.py`

**WebKit (25 ก.ย. 2569):** เช็ค `curl -sS "$HTTPS_PROXY/__agentproxy/status"` แล้วลอง
`python3 -m playwright install webkit` ซ้ำในรอบนี้ — ยังติด policy 403 เดิมที่ `cdn.playwright.dev` และ
`playwright.download.prss.microsoft.com` เหมือน Phase 1-3 ทุกประการ (ไม่ใช่ transient) — ไม่ได้พยายามหาทาง
ดาวน์โหลดผ่านช่องทางอื่น ตามที่สั่งไว้ชัดเจนว่าห้าม workaround — Chromium เท่านั้นในรอบนี้เหมือนเดิม

**รัน:**
```bash
cd ~/Documents/Dashboard/tests
# แหล่ง v3on = ../index.html ตรง ๆ (ค่าจริง SAT_V3_ON=true) — ไม่ต้อง generate อะไรเพิ่ม
# แหล่ง v3off = สำเนาที่ตั้ง false กลับชั่วคราว ต้อง generate ก่อนรันครั้งแรก:
sed 's/const SAT_V3_ON = true;/const SAT_V3_ON = false;/' ../index.html > /tmp/index_v3off.html
python3 run_tests_phase4.py
BROWSER=webkit python3 run_tests_phase4.py       # ติดปัญหา egress policy เดียวกับ Phase 1/2/3
```

## สรุปสถานะ ณ จบ 7D.3 รอบที่ 2 (Phase 4 เสร็จสมบูรณ์)
`SAT_V3_ON = true` — หน้า Sat ใหม่ (ส่วนที่ 1) ขึ้นจริงแล้ว หน้า 7D.2 เดิมยังอยู่ครบ (ไม่ถูกลบทิ้ง) reachable
ทันทีด้วยการตั้ง `SAT_V3_ON = false` กลับ (regression escape hatch) รวมเคสทดสอบทั้งหมด ณ จุดนี้:
`run_tests.py` 56 + `run_tests_phase1.py` 42 + `run_tests_phase2.py` 52 + `run_tests_phase3.py` 78 +
`run_tests_phase4.py` 63 = **291 เคส ผ่านครบทุกจุด** (Chromium, 1440px+430px, console error/uncaught = 0)

## 7D.5 — ปรับการ์ดเงื่อนไข (`run_tests_phase6.py`)
รันเหมือนเฟสอื่น: `CHROMIUM_PATH=".../Google Chrome" python3 run_tests_phase6.py` (Mac นี้: Chrome จริง ไม่มี node)
ครอบคลุม: แถวพับ "รอเงื่อนไข" · Activate จากแถว · ยกเลิก=ซ่อน (reload ยังซ่อน · "ดูที่ยกเลิก") · ✕ ข้อที่ยังไม่บันทึก=ลบจริง ·
ขั้นหน้างานย่อ + ใช้ข้อนี้/✎ · ไม่มี TP zone เตือนแต่บันทึก order ได้ · แก้ข้อความหลังบันทึก order ไม่กระทบ `entry_condition` ·
ปุ่มลัดร่วมทุก asset (`satConfig/conditionTemplates`) · ข้อมูล 7D.4/ก่อน 7D.4 · 1440+430 · ภาพ `screenshots/7d5-*.png`
รอบ 7D.5 แก้เทสเดิมเท่าที่พฤติกรรมเปลี่ยนตามสเปกเท่านั้น: `page.check()`→`click()` (Activate แล้วการ์ดวาดใหม่) ·
สลับข้อ Activate ผ่าน `▸ เงื่อนไขอื่น → [ใช้ข้อนี้]` · ข้อความแถวพับ 'รอเงื่อนไข · n ข้อ' → 'รอเงื่อนไข' + นับแถว `.ui-wc` · แก้ TP zone ข้อ active ผ่าน ✎
รวมทั้งชุด ณ จบ 7D.5: 56 + 42 + 54 + 78 + 67 + 122 + 114 = **533 เคส ผ่านครบ** (phase4 ต้องมีสำเนา v3off ตามด้านบน)

## 7D.6 — จัดวาง Trade Plans (`run_tests_phase7.py`)
`CHROMIUM_PATH=".../Google Chrome" python3 run_tests_phase7.py` — grid เดียวของการ์ดกาง+แถวพับ · ลำดับกาง→พับ เก่า→ใหม่ · align-items:start ·
Activate/เปิด จากแถวพับ → ขึ้นก่อน + อยู่ในจอ · พับไม่เลื่อนจอ · แถว plan/open + "แผนเดิม" อยู่นอก grid · ภาพ `screenshots/7d6-*.png`
รวมทั้งชุด ณ จบ 7D.6: 56 + 42 + 54 + 78 + 67 + 122 + 114 + 47 = **580 เคส ผ่านครบ** (เทสเดิมทุกไฟล์ไม่ต้องแก้)

## 7D.4 — ปรับหน้าแผน Future (`run_tests_phase5.py`) — วิธีรัน (ค้างจาก 7D.4)
ไฟล์นี้ยืมตัวเปิดหน้า (`launch_page` = login + mock Firebase) จาก `run_tests_phase4.py` จึงต้องมีไฟล์นั้นอยู่โฟลเดอร์เดียวกัน
แต่ **ไม่ต้อง generate สำเนา v3off** (phase5 ใช้ `../index.html` ตรง ๆ ที่ `SAT_V3_ON=true`)
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase5.py                          # Chromium ของ Playwright (1440px แล้ว 430px) ~40 วินาที
CHROMIUM_PATH=".../Google Chrome" python3 run_tests_phase5.py   # หรือชี้ Chrome จริงเอง
python3 run_tests_phase5.py /path/to/index.html      # หรือ INDEX_HTML=... ทดสอบไฟล์อื่น
```
ครอบคลุม: Strategy เหลือ 2 องค์ประกอบ (Trend · Macro) · Macro ไม่มี Fund-flow · Trend Shift · การ์ดแผน 2 ขั้น
(conditions → บันทึกแผน → Activate → Entry/SL → บันทึก order) · Setup ผ่านที่ 65% · แนวรับ 3 ค่า/ลบทีละค่า/reload (ค้างจาก 7D.3) · ภาพ `screenshots/7d4-*.png`
จบด้วย `PASS/FAIL/TOTAL` — ไม่ผ่านจะ `exit 1` พร้อมรายการที่ล้ม · helper ที่ phase6/7/8 ใช้ต่อ: `goto_sat` · `open_editor` · `set_bias_dom` · `reload_keep_state`
`open_editor(page, asset)` คลิกที่ **ชื่อสินค้า `.ui-tile-a`** (ไม่ใช่กึ่งกลาง `.ui-tile-th`) — จอ 430 กึ่งกลางแถวหัวไปตกบนปุ่ม [+ แผน] แล้วกดพลาด

## F1 — แท็บ Flow (`run_tests_phase8.py`)
```bash
python3 run_tests_phase8.py        # 1440px + 430px + เคสปฏิทินโหลดไม่ขึ้น (รอ timeout 8 วินาที) ~2 นาที
```
- เปลี่ยนชื่อแท็บ Flow · ถอดระบบ Macro/ข่าว (ไม่มี request ไป `news`/`macro` · ไม่มีกระดิ่ง · กด N ไม่เกิดอะไร · Watchlist/Tripwire ไม่ error)
- **เพดาน Core แบบ f** (`Calc.ffCoreCap`): 0/1/2 ตัวแดง = 100/75/50% · ไฟล์เก่าเกิน 5 วันทำการ → 100% + เตือนส้ม · ไม่มี `HYG_IEI` → คิดจาก ACWI/BIL ตัวเดียว + เตือน
  และเทสหลัก: เพดานใน **Add Trade · Port Heat · ตั้งค่า Sizing = ตัวเลขในแถบดำแท็บ Flow** ทุกกรณี
- แถบดำ "ผลที่ต้องทำ" (4 ช่อง · 430 = 2×2) · การ์ดปฏิทิน (ไม่มี iframe จนกว่าจะกาง · src ตรงสเปก) · ธีม RRG เรียง นำ→ดีขึ้น→อ่อนลง→ตาม · บอร์ดจดเองพับไว้ล่างสุด
- งานเก็บ 7D.6: `satV3NewPlan` เหลือตัวเดียว + [+ แผน] ยังทำงาน · `open_editor` คลิกชื่อสินค้า · phase7 เปิดขั้นตั้ง Strategy ซ้ำกลับมา
- ภาพ `screenshots/f1-flow-{folded,open}-{1440,430}.png`

### ตัวช่วยที่เพิ่มรอบ F1 (ใช้กับทุก phase)
- `ff_stub.py` — จำลอง `fetch('fundflow.json')` (เปิดหน้าแบบ `file://` แล้ว Chrome บล็อก fetch → เดิมขึ้น console error 2 เคส/ชุด)
  ตั้ง `window.__FF_JSON = {as_of, ratios:{...}}` เพื่อป้อนไฟล์จำลอง · `null` = 404 จำลอง (โหมดข้อมูลตัวอย่าง) · ทุก launcher เรียก `context.add_init_script(FF_STUB)`
- `mock-firebase.js` บันทึกทุก path ที่แอปแตะไว้ที่ `window.__fsAccess` (ใช้ยืนยันว่าไม่มี collection `news`/`macro`)
- `check_syntax.py` — ไม่มี `node` (เช่น Mac เครื่องนี้) → fallback คอมไพล์ด้วย Chromium (`new Function`) แทน · ยังเป็น `SYNTAX_OK/FAIL` เหมือนเดิม
- ติดตั้งครั้งแรกบนเครื่องนี้: `python3 -m playwright install chromium` (ลงแล้ว)

รวมทั้งชุด ณ จบ F1: `run_tests.py` 56 + phase1 42 + phase2 54 + phase3 78 + phase4 49 + phase5 122 + phase6 114 + phase7 47 + phase8 115 (phase4 นับ 49 เมื่อรันเฉพาะ v3on)


## CL2-a — รีเซ็ตข้อมูลครั้งเดียว + ลบโค้ด 4 ก้อน (`run_tests_phase19.py`)
ลบจริง: Weekly Plan · ทาง `SAT_V3_ON=false`/`SAT7D_ON`/`SAT_VIEW_ON` + Sat.B เดิม · Sat.A · migration `_v` + Watchlist เดิม · เพิ่ม gate `#cl2aGate` (รีเซ็ตครั้งเดียว)

**เปลี่ยนวิธีรันเทส**
- `run_tests_phase4.py` **ไม่ต้องสร้าง `/tmp/index_v3off.html` อีกแล้ว** — ส่วน v3off เลิกใช้ทั้งหมด (พิมพ์ `RETIRED - …` แทน) ทุกเคสที่เหลือรันกับ `../index.html` ตัวเดียว
- ทุกชุดมี helper `retired(name, reason)` — เคสที่เลิกใช้เพราะโค้ดถูกลบพิมพ์ `RETIRED - …` (ไม่นับ PASS/FAIL แต่ตามรอยได้) · ตารางครบที่ `CL2a_retired.md`
- `seed.json` ใหม่ = เอกสารที่รีเซ็ตแล้ว (มีธงสองตัว) · `seed.pre-CL2a.json` = เอกสารเดิมก่อนรีเซ็ต (phase19 ใช้เป็นฐานของเคส gate/รีเซ็ต/กู้ backup)
- `tools/cl2a_seed.py` ทำสูตรเดียวกับ `cl2aStripLegacy()` — phase19 ตรวจว่าผลตรงกับฟังก์ชันจริงในแอป
- ตัวเลข "เคส" ในรายงานนับจากบรรทัด `PASS - …` (phase17 พิมพ์ 58 บรรทัดแต่ summary รายงาน 52 · phase18 พิมพ์ 104 → 90 บรรทัดแต่ summary 98 → 84 — ส่วนต่างเท่ากันก่อน/หลัง เพราะบางเคสไม่ผ่าน `results`)

**phase19 (145 เคส · 1440px + 430px)**: ฟังก์ชันบริสุทธิ์ (Strip/Reset · null/{} · ไม่แก้ต้นฉบับ · ตรงกับ `tools/cl2a_seed.py`) · gate (เปิด/ไม่เปิดตามธง · ไม่ render/เขียน/ดึง FX ตอนเปิด · ปุ่ม disabled จนพิมพ์ "รีเซ็ต" · มือถือ hit-test) ·
ผู้ใช้ใหม่ (ไม่มีเอกสาร → เขียนครั้งแรกมีสองธง) · เอกสารแบนเก่า → errorScreen ไม่เขียน · รีเซ็ต 2 บัญชี (main + fam) ตรวจข้อมูลใน mock ครบ + ลำดับดาวน์โหลดก่อนเขียน ·
bkBuild partial/throw/เขียนล้ม → หยุด/คืนค่า/ลองใหม่ได้ · satWeek ลบไม่ได้ → sheet + ปุ่มลองใหม่ในตั้งค่า › บัญชี · กู้ backup เก่า (Strip ไม่ใช่ Reset) · grep โค้ด
- mock: `__denyPath` ปฏิเสธทั้ง get/set/delete ของ path นั้น → เคส "ลบ satWeek ไม่ได้" deny ทีละเอกสาร (`users/testuid/satWeek/<id>`) ให้ get ของคอลเลกชันยังผ่านเหมือน rules จริงที่อนุญาต read แต่ไม่อนุญาต delete
- `launch()` ใน phase19 ไม่รอ `#mainWrap` (gate ซ่อนมันอยู่) · ตั้ง `bkLastBackupAt=now` กัน backup อัตโนมัติ (Mac) ปนกับ `window.__dl` ของเทส

ภาพเก็บที่ `tests/screenshots/cl2a-*.png` (gate ก่อน/หลังพิมพ์ · sheet ผลลัพธ์ · sheet satWeek fail · ตั้งค่า › บัญชีมีปุ่มลองใหม่ · Port · Journal · หน้า Sat)
diff ย่อของฟังก์ชันที่แก้: `CL2a_diffs.txt`


## CL2-b — ลบโค้ด Checklist · Ideas · Missed · Fund Checklist + Import JSON + ฟอร์ม Watchlist เดิม + ฟอร์ม Growth Gate (`run_tests_phase20.py`)
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase20.py                       # 1440px แล้ว 430px · mock Firestore · seed.json ปัจจุบัน (95 เคส)
python3 run_tests_phase20.py /path/to/index.html   # ระบุไฟล์เอง (เทียบปุ่ม ＋ กับ index.backup-pre-CL2b.html ในโฟลเดอร์เดียวกัน)
```
ครอบคลุม: ปุ่ม ＋ (`onclick="openTrade()"` ขนาด/ไอคอนเท่าไฟล์ก่อนแก้) · ปุ่มลัด T → `#tradeOverlay` · DOM ไม่มี `#checklistOverlay/#ideasPanel/#ideaOverlay/#missedOverlay/#fcDetailOverlay/#impOverlay/#watchOverlay/jColBtn_missed/option[value=missed]` ·
Journal เหลือ Closed + Cancelled (`JV_KINDS`/`JINC_STATUS`) · ไม้ cancelled แสดง/แก้ได้ · คะแนนวินัย/Setup แก้และบันทึกได้ · ตัวจัดการแท็ก exit/cancel เปิดได้ ไม่มี missed และ `reasonTags.missed` ในบัญชียังอยู่หลังเซฟ ·
Watch เพิ่มหุ้นผ่าน `wlOpenAdd` · `wlGG/ggRow/ggScoreOfSym/setupFactor` ไม่พัง · Industry manager เพิ่ม/ลบ · Add Trade บันทึกไม้ core · books ไม่มี key `checklistDrafts/ideas/failLog` ใหม่ · ทุกแท็บ + ตั้งค่าไม่มี console error · ≤700px ไม่ล้นแนวนอน · grep `index.html` (ต้องไม่เจอ/ต้องเจอ)
ภาพ `screenshots/cl2b-*.png` (topbar · addtrade · journal · reasontags · watch · watch-add · plan × 1440/430)

**เทสเก่าที่แก้/เลิกใช้** — phase1 (wPort ของฟอร์ม Watchlist เดิม −6) · phase13 (แถว missed −3 + ปรับตัวเลขข้อมูลไม่ครบ 3→2 + รอ smooth scroll ให้นิ่ง) · phase16 (Missed −2 + Restore เหลือ Cancel) — ตารางครบที่ `CL2b_retired.md` · diff ย่อของโค้ดที่แก้: `CL2b_diffs.txt`
**หมายเหตุวิธีรัน**: phase 6–16 ใช้ `../index.html` เป็นค่าเริ่มต้น (ไม่รับ path จาก argv) และบางชุดเรียกไฟล์ `index.backup-pre-*.html`/`avgo-research-card-th.json` ข้างเคียง — จะรันไฟล์ก่อนแก้ให้เทียบ ต้องคัดลอก `tests/`+`tools/` ไปโฟลเดอร์ใหม่ใส่ index เดิมเป็น `index.html` แล้วลิงก์ไฟล์ข้างเคียงมาด้วย
ค่าฐานหลัง CL2-b: run_tests 52 · p1 30 · p2 54 · p3 78 · p4 47 · p5 124 · p6 114 · p7 47 · p8 115 · p9 155 · p10 11 · p11 196 · p12 138 · p13 103 · p14 192 · p15 87 · p16 133 · p17 52 · p18 84 · p19 145 · p20 95


## CL2-c — หน้าต่าง "แก้ไม้" ใหม่ + ลบฟอร์ม Add Trade + แถวหัวแบบย่อ (`run_tests_phase21.py`)
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase21.py [/path/to/index.html]   # หน้าต่าง 1440+430 · แถวหัว 1440+430+375 · 168 เคส
```
ครอบคลุม: `openTradeEdit(id, acct, {toOpen})` (Sat "แก้ SL" · Journal ✎ · ตารางแผน →Open · บัญชี fam) · หัวอ่านอย่างเดียว · บรรทัดเสี่ยง/P&L/R สด · ตรวจก่อนบันทึก (ข้อความแดง ไม่ alert ไม่เขียน Firestore) ·
ฟิลด์นอก makeTradeObject (setups/condition_id/trend_state/_probeT/fills/parentId) คงอยู่ · Esc · ≤700px ไม่ล้น · ฟอร์มเดิม/ปุ่ม ＋/ปุ่มลัด T/ปุ่ม Watch/ปุ่ม Journal หาย ·
แถวหัวไอคอนล้วน (ไม่มี ::after) ปุ่ม ≥36px ห่าง ≥4px แถวเดียวกับ brand เมนู ⋯ เปิดใต้ปุ่ม อยู่ในจอ · grep ต้องไม่เจอ/ต้องเจอ · ภาพ `screenshots/cl2c-*.png`
เทสเก่าที่เลิกใช้/แก้: `CL2c_retired.md` · diff ย่อ: `CL2c_diffs.txt`
ค่าฐานหลัง CL2-c: run_tests 52 · p1 20 · p2 54 · p3 78 · p4 47 · p5 124 · p6 114 · p7 47 · p8 115 · p9 155 · p10 11 · p11 196 · p12 138 · p13 103 · p14 192 · p15 87 · p16 129 · p17 52 · p18 84 · p19 145 · p20 83 · p21 168


## CL2-d — ตาราง Positions แทน Trading Plan + ลบ sizing เดิม (SZ/sz*/Heat 1R/บล็อก CL3/ค่าตั้ง 1R) + เก็บกวาด (`run_tests_phase22.py`)
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase22.py [/path/to/index.html]   # 1440px + 430px · mock Firestore · seed.json + ไม้ในเทส · 129 เคส
```
ครอบคลุม: Positions (แสดงเฉพาะ open · Core ก่อน Sat แล้ววันเข้าเก่าก่อน · เสี่ยงค้าง = |entry−sl|×qty×mult · SL เลยทุน = 0 + "ล็อกกำไร" · ถือมา n วัน (เวลาไทย) · ป้าย "นอกแผน" · แถวรวมท้ายบัญชี · fam ปุ่มส่งบัญชี 'fam' · ปุ่ม ปิด/แก้/ยกเลิก เปิด #closePosOverlay/#teOverlay/#cancelOverlay · ลบ = ตรวจ onclick) ·
ว่าง (ข้อความ §1.4) · ≤700px การ์ดครบ ไม่ล้นแนวนอน · `posOpenRisk` บริสุทธิ์ (Long/Short) · บล็อกสรุป Core (ไม่มี `data-sum="heat"` · Open Risk/Planned อยู่) · footer ไม่มี 1R ·
ตั้งค่า (ไม่มีช่อง sRCore/sRSatA/sCapCore/sCapSatA/sPosSatB/sRsBench/sFfThrottle · **บันทึกแล้ว settings.sizing/posSize/limits.trade ยังเป็นค่าเดิมเป๊ะ** · key อื่นไม่หาย · เอกสารที่ไม่มี sizing ไม่ถูกสร้าง key ขึ้นมา) ·
Watch (ไม่มีป้าย R/GG · เพิ่มหุ้นได้) · Journal ว่างข้อความใหม่ (ตาราง+การ์ด) · Flow (Regime/เพดาน Core · `ffDeployCap('core') = ffCoreNow().cap`) · การ์ด Sat · ทุกแท็บไม่มี console error · grep (ต้องไม่เจอ/ต้องเจอ) · `tests/_extracted.js` ย้ายไป `_to_delete/`
- `posOpenRisk(t, fx?)` → `{amt, cur, thb, locked}` · `fx` ไม่ส่ง = `state.settings.fx`
- `saveSettings` เปลี่ยนเป็น `{...state.settings, …ช่องที่แก้}` — key ที่หน้าตั้งค่าไม่ได้แก้ (sizing · posSize · posTier · limits.trade · rsBench · sz1Rv2 ฯลฯ) คงอยู่ครบ
เทสเก่าที่เลิกใช้/แก้: `CL2d_retired.md` · diff ย่อของโค้ดที่แก้: `CL2d_diffs.txt` · ภาพ `screenshots/cl2d-*.png`
ค่าฐานหลัง CL2-d: run_tests 52 · p1 20 · p2 54 · p3 78 · p4 47 · p5 124 · p6 114 · p7 47 · p8 115 · p9 155 · p10 11 · p11 196 · p12 138 · p13 103 · p14 189 · p15 87 · p16 129 · p17 52 · p18 84 · p19 145 · p20 76 · p21 161 · p22 129


## 7E-1 — Calc.coreSize + ค่าตั้ง Core + heat % ของถัง + ความเสี่ยงค้างสูตรเดียว + บล็อกสรุป Core ใหม่ (`run_tests_phase23.py`)
```bash
cd ~/Documents/Dashboard/tests
python3 run_tests_phase23.py [/path/to/index.html]   # 1440px + 430px · mock Firestore · seed.json · 123 เคส · ภาพ screenshots/7e1-*.png
```
ครอบคลุม: `Calc.coreSize` (สำเนา core-size.js ใน index.html ตรงทุกตัวอักษร · เลขตัวอย่าง 700/500/300/300 · บันได 280/233/262 · เสี่ยงเต็ม 15,680 · openGate) · `core_size_test.js` รันบนสำเนาในเบราว์เซอร์ = 287/287
(เครื่องนี้ไม่มี node จึงรันผ่านเบราว์เซอร์ด้วย shim `require`/`process` — ถ้ามี node ใช้ `node tests/core_size_test.js` ได้ตามปกติ) · ตั้งค่าความเสี่ยง Core (`settings.coreRisk` ต่อบัญชี · ตลาด main=US / Family=TH / อื่น=both ·
ตรวจค่าผิดด้วยข้อความแดง + ปุ่มบันทึกล็อก) · เพดานชั้น 2 = `limits.port.core` (ค่าเดียวกัน) · migration `heatV2` (เขียน Firestore ครั้งเดียว ไม่ทับค่าที่ผู้ใช้แก้ต่อ) · `openRiskTHB` สูตรเดียว 3 จุดตรงกัน (บล็อก · แถบบัญชี · Positions) ·
สีช่องความเสี่ยง 14.9/15/20% · เงินที่ถือ/เงินว่าง · "ถ้าทุกไม้โดน Stop" · footer · ทุน Sat แสดง ≤2 ทศนิยม (บันทึกโดยไม่แก้ = คงค่าเดิม) · ปุ่มลัด T
### แก้สูตรใน core-size.js แล้วคัดลอกลง index.html
```bash
python3 tools/sync_core_size.py            # แทนที่สำเนาระหว่าง BEGIN/END ใน index.html
python3 tools/sync_core_size.py --check    # exit 1 ถ้าไม่ตรง (ไม่แก้ไฟล์)
```
เทสเก่าที่แก้: `7E1_retired.md` (ไม่มีเคสเลิกใช้ · แก้ p13 p14 p18 p21 p22)
ค่าฐานหลัง 7E-1: run_tests 52 · p1 20 · p2 54 · p3 78 · p4 47 · p5 124 · p6 114 · p7 47 · p8 115 · p9 155 · p10 11 · p11 196 · p12 138 · p13 103 · p14 189 · p15 87 · p16 129 · p17 52 · p18 84 · p19 145 · p20 76 · p21 161 · p22 160 · p23 123

## 7E-2 — การ์ดตำแหน่ง Core (โหมด W) + coreCards + แผน Core ใหม่ + ชั้น 2 จากราคา + ตัด loss ออกจาก heat (`run_tests_phase24.py`)
mock Firestore (รองรับคอลเลกชัน `users/testuid/coreCards` + `__denyPath` เคส permission-denied) · 1440px + 430px · seed.json · ตั้ง f ด้วย `window.__FF_JSON = {...}; await ffLoadJson(true)` (ตัวช่วยใน `launch(... ff="green"|"red1"|"red2")`)
รัน: `python3 run_tests_phase24.py /path/เต็ม/index.html` · ภาพเก็บที่ `tests/screenshots/7e2a-*.png`
เคสหลัก: ＋/T (scope หุ้น = sheet แผนใหม่ · Future = เดิม) · firstLot (f 100/75/50 · เงินสดคุม · ชนเพดาน Tier · zeroLot · US ปัด 1 หุ้น) · Tier A ต้องมีเหตุผล · ซื้อไม้ 1 (สร้าง trade + การ์ด) · pyramid (เลื่อน Stop → ไม้เติม → trade.qty/entry/sl) · ป้ายไม้เติม 4 แบบ · ป้ายสถานะ 🟢🟡🔴⚪ · ชั้น 2 ตรง `Calc.coreSize.layer2` · ปิดตำแหน่ง → การ์ด "ปิดแล้ว" · heat ไม่รวม loss · 2 บัญชี · permission-denied · ≤700px
**หมายเหตุตัวเลข pyramid:** ตัวเลข 350 → 175 (สเปก) ไม่ใช่ทวีคูณ 100 → บัญชี TH (`XXX.BK`) คิดตาม core-size (market TH) ได้ 300 → 100 · เทสชุดนี้จึงรัน 2 แบบ: TH (300/100 · trade 1000 @104.5 → 1100 @106.82) และ US ที่ fx=1 (350/175 · trade 1050 @105 → 1225 @108.57)

### ⚠ Firestore rules — ต้องเพิ่มก่อนขึ้นเว็บ (คอลเลกชันใหม่ 7E-2)
ในไฟล์ Firestore rules (ก้อน `match /databases/{database}/documents { ... }`) เพิ่ม — ถ้ายังไม่เพิ่ม การ์ดจะขึ้น "ยังไม่ได้เปิดสิทธิ์ coreCards ใน Firestore rules" และบันทึกแผน/ซื้อไม้ผ่านการ์ดไม่ได้:

```
match /users/{uid}/coreCards/{doc} {
  allow read, write, delete: if request.auth != null && request.auth.uid == uid;
}
```
(ถ้า rules เดิมเป็น wildcard `match /users/{uid}/{document=**}` อยู่แล้ว ไม่ต้องเพิ่ม)

## Phase 40 (WL2) — `run_tests_phase40.py`
การ์ด Watchlist v2 (Living Thesis `living-thesis@1`) + ลบ Research Card · fixture `tests/fixtures/avgo_thesis.json` · นาฬิกาปลอม 2026-10-02 13:03 ไทย · 1440 + 390
ครอบคลุม: Import/Export/ประวัติ · ตรวจ JSON (error ไทย) · XSS · 5 แท็บ · กล่องตัดสินใจ · แถบพับ · ปุ่ม "ชนแล้ว" · ⚠ ควร update · Today (tripwire/catalyst) · การบ้าน · เติมจาก Thesis ในฟอร์ม Tier · จำแท็บต่อ ticker · grep Research Card = 0
เคสเก่าที่แก้ความคาดหวังเพราะ WL2: ดู `tests/WL2_retired.md`

## Phase 42 (NUM1) · 43 (PX1) · 44 (ID1)
- `run_tests_phase42.py` — เก็บกวาดตัวเลข 7 จุด (การ์ดแผน Sat USD `$ · ≈฿` · BE/WIN `pnlOutcome` · `฿-0` · "0 ตัวรอสร้าง Thesis" · "ตัวที่อ่อนสุด" · คำ f · ตาราง Thesis 390px) · เคสเก่าที่แก้: `NUM1_retired.md`
- `run_tests_phase43.py` + `test_build_prices.py` — ราคาปิดสัปดาห์ + EMA10 อัตโนมัติ (หุ้น Core) จาก `users/{uid}/prices` · สคริปต์อยู่ `P2-prices-upload/` (ผู้ใช้อัปขึ้น repo เอง) · `PX1_retired.md` (ไม่มี)
- `run_tests_phase44.py` — แท็บ Ideas (อ่านอย่างเดียว + Import) · fixture `tests/fixtures/idea_semis.json` (scan จริง ไม่มีบริษัท → เทสต่อ KLAC/AMAT/LRCX/NORS เข้าไปเอง) · `ID1_retired.md`

### ⚠ Firestore rules — ต้องเพิ่มก่อนขึ้นเว็บ (PX1 + ID1)
```
match /users/{uid}/prices/{doc} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow write: if false;            // เขียนได้เฉพาะ Admin SDK (GitHub Actions)
}
match /users/{uid}/ideas/{doc} {
  allow read, write, delete: if request.auth != null && request.auth.uid == uid;   // แบบเดียวกับ users/{uid}/watchlist
}
```
(ถ้า rules เดิมเป็น wildcard `match /users/{uid}/{document=**}` อยู่แล้ว ไม่ต้องเพิ่ม ยกเว้น prices ที่อยากให้เขียนไม่ได้จากแอป)
