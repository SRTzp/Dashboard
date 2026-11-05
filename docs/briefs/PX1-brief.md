# PX1 — ราคาปิดสัปดาห์ + EMA10 อัตโนมัติ (หุ้น Core) · เทส 43

> คิว v2 ข้อ 1 · ผู้ใช้ตัดสิน 4 ต.ค.: **เฉพาะหุ้น Core** (ไม่ทำ XAU/BTC/Brent — Sat ต้องใช้ราคาโบรกเป๊ะ) · **GitHub Actions + yfinance** (แบบ `fundflow`) · **เก็บใน Firestore** (ไม่ใช่ไฟล์ใน repo — กันคนอื่นเห็นหุ้นที่ถือ)
> เป้า: ตัวที่ไม่ได้กรอกราคา = นับ 0 → DD Core ต่ำกว่าจริง · ป้าย "ปิดใต้ EMA10 งดเพิ่มไม้" ต้องทำงานเองทุกสัปดาห์
> สำรองก่อนแก้: `index.backup-pre-PX1.html` · `tests/_bk_px1/` · ห้ามแตะ core-size.js (ใช้ `Calc.coreSize.status` เดิม) · ใช้ชื่อฟังก์ชันเป็นหลัก
> ⚠ ส่งหลัง NUM1 ตรวจผ่าน · ID1 (แชตอื่น) จองเลขเทส 43 ไว้ชั่วคราว → ถ้าส่ง PX1 ก่อน ID1 ให้ ID1 ใช้ 44

## ภาพรวม
```
GitHub Actions (เสาร์ 06:30 + อาทิตย์ 06:30 ไทย · กดรันเองได้)
  → scripts/build_prices.py: อ่าน users/{uid}/coreCards (status plan/open) → ticker
  → yfinance รายวัน 2 ปี → แท่งสัปดาห์ (จบศุกร์) → ราคาปิดสัปดาห์ล่าสุดที่จบแล้ว + EMA10 รายสัปดาห์
  → เขียน users/{uid}/prices/{SYM} + users/{uid}/prices/_meta
แอป: ฟัง users/{uid}/prices → ใช้แทนราคาที่กรอกเองเมื่อใหม่กว่า (ไม่เขียนกลับการ์ด)
```

## A. สคริปต์ + workflow (ไฟล์ส่งให้ผู้ใช้อัปเอง — ไม่ push)
สร้างโฟลเดอร์ `P2-prices-upload/` แบบเดียวกับ `P1-fundflow-upload/`:
- `scripts/build_prices.py` · `.github/workflows/prices.yml` · `README-อัปโหลด.md` (ข้อ C)

### `build_prices.py`
- env: `FIREBASE_SA` (JSON service account ทั้งก้อน) · `FIREBASE_UID` · ใช้ `firebase-admin` (Admin SDK ข้าม rules ได้) + `yfinance` + `pandas`
- **ticker:** coreCards ที่ `status` เป็น `plan` หรือ `open` (ไม่เอา `closed`) · ตลาด TH (field `market==='TH'` หรือ ticker ลงท้าย `.BK`) → สัญลักษณ์ yfinance = `XXX.BK` · US = ticker ตัวใหญ่ · ตัดซ้ำ (ตัวเดียวหลายบัญชี = 1 ตัว)
- **ราคา:** `yf.download(..., interval='1d', period='2y', auto_adjust=False)` → ใช้ `Close` (ราคาจริง ปรับเฉพาะแตกหุ้น · ไม่ปรับปันผล → เทียบกับ Stop ที่ผู้ใช้ตั้งได้ตรง)
- **แท่งสัปดาห์:** รวมรายวันเป็นสัปดาห์จบวันศุกร์ (`W-FRI`) · **ตัดสัปดาห์ที่ยังไม่จบ** (วันนี้ตามเวลาตลาดนั้นยังไม่ถึงหลังปิดศุกร์) · `closeDate` = วันซื้อขายสุดท้ายจริงของสัปดาห์นั้น (ศุกร์หยุด → พฤหัส) รูปแบบ `YYYY-MM-DD`
- **EMA10:** `ewm(span=10, adjust=False)` บนราคาปิดสัปดาห์ (ตรงกับ TradingView) · มีข้อมูล < 10 สัปดาห์ → `ema10w: null`
- **ตรวจความผิดปกติ:** close ≤ 0 หรือ NaN → ไม่เขียน (นับเป็น failed) · เปลี่ยนจากสัปดาห์ก่อน > 40% → เขียนพร้อม `suspect: true`
- **เขียน** `users/{uid}/prices/{ySym}` (id = สัญลักษณ์ yfinance เช่น `AVGO`, `PTT.BK`):
  `{ sym, ySym, close, closeDate, ema10w, weeks, suspect, src:'yfinance', at: SERVER_TIMESTAMP }`
- **_meta** `users/{uid}/prices/_meta`: `{ runAt, ok:[ySym], failed:[{ySym, why}], n, ver:1 }`
- ตัวที่ดึงไม่ได้ → **ไม่เขียนทับ doc เดิม** · ทำตัวอื่นต่อ · ล้มทุกตัว → exit 1 (Actions แดง)
- แยกฟังก์ชันล้วน (ไม่แตะเน็ต) ให้เทสได้: `to_ysym(ticker, market)` · `weekly_closes(df, now_utc)` · `ema10(series)` · `check(close, prev)` · `run(cards, fetch, write, now)` (fetch/write ฉีดเข้าไปได้)

### `prices.yml`
- `on: schedule` → `30 23 * * 5` (เสาร์ 06:30 ไทย) · `30 23 * * 6` (อาทิตย์ 06:30 ไทย) · `workflow_dispatch`
- ubuntu-latest · Python 3.11 · `pip install yfinance pandas firebase-admin` · `env: FIREBASE_SA: ${{ secrets.FIREBASE_SA }}` · `FIREBASE_UID: ${{ secrets.FIREBASE_UID }}`
- **ไม่ commit อะไรกลับ repo** · ไม่ต้องใช้ permission write · log ห้ามพิมพ์ค่า secret / ห้ามพิมพ์ JSON กุญแจ

## B. แอป (index.html)
1. **ฟัง** `users/{uid}/prices` (onSnapshot เริ่ม/หยุดคู่กับ listener coreCards เดิม) → `pxAuto[ySym]` + `pxMeta`
2. **ราคาที่ใช้จริง (effective):** สำหรับการ์ดแต่ละใบ หา `pxAuto` ด้วยกติกาสัญลักษณ์เดียวกับข้อ A
   - auto มี + ไม่ `suspect` + (`closeDate` > `c.pxDate` หรือการ์ดไม่มี `pxDate`) → ใช้ `px = close` · `pxDate = closeDate` · `emaW = ema10w` (เฉพาะ W · L ไม่ใช้ EMA เหมือนเดิม) · `pxSrc = 'auto'`
   - วันที่เท่ากัน หรือที่กรอกเองใหม่กว่า → ใช้ค่าที่กรอกเอง (`pxSrc='manual'`)
   - ต้องได้ผลเดียวกันทุกจุดที่อ่าน `c.px` / `c.pxDate` / `c.emaW` (coreView · DD equity · ชั้น 2 · ตัวอ่อนสุด · ตรวจก่อนบันทึก · lastPx ฯลฯ) → แนะนำทำครั้งเดียวตอนสร้าง `coreCardsList` (เก็บค่าที่กรอกเองไว้ใน field ภายใน เช่น `_pxMan`) · ไล่ grep ให้ครบ + รายงานรายชื่อจุด
   - **ห้ามเขียนค่า auto ลง coreCards** — ทุกที่ที่เรียก `coreWrite` ต้องส่งเฉพาะ patch ของตัวเอง (ตรวจว่าไม่มีที่ไหนส่งทั้งการ์ดที่ merge แล้ว)
3. **หน้าการ์ด** ช่อง "ราคาปิด · EMA10": ป้ายเล็ก `อัตโนมัติ · ศ. 3 ต.ค.` หรือ `กรอกเอง · …` · `suspect` → ⚠ `ราคาอัตโนมัติเปลี่ยนเกิน 40% — ตรวจก่อน (ใช้ค่าที่กรอกเองแทน)`
4. **sheet อัปเดตราคาปิดสัปดาห์** เดิม: ยังใช้ได้ (เขียน `px/pxDate/emaW` ลงการ์ดเหมือนเดิม) · เพิ่มบรรทัดบน `ราคาอัตโนมัติล่าสุด: 105.20 · EMA10 110.00 (ศ. 3 ต.ค.) — ที่กรอกเองจะใช้แทนจนกว่าจะมีราคาอัตโนมัติวันที่ใหม่กว่า` (ไม่มี auto = ไม่แสดง)
5. **สถานะระบบ** 1 บรรทัดเล็กในหน้าแผน Core (ใกล้ส่วน DD/ชั้น 2): `ราคาอัตโนมัติ: อัปเดต ส. 4 ต.ค. 06:31 · 7/7 ตัว` · มี failed → `· ดึงไม่ได้: XYZ` (สีเหลือง) · `_meta.runAt` เก่ากว่า 8 วัน → เหลือง `ระบบราคาอัตโนมัติไม่ได้อัปเดต — ตรวจ GitHub Actions (prices)` · ไม่มี `_meta` เลย → ไม่แสดงบรรทัดนี้
6. **อ่าน prices ไม่ได้** (rules ยังไม่เพิ่ม / error) → แอปทำงานแบบเดิมทุกอย่าง + บรรทัดสถานะ `อ่านราคาอัตโนมัติไม่ได้ — ตรวจ Firestore Rules ของ users/{uid}/prices`
7. **Firestore rules** (สำเนาใน repo + บอกผู้ใช้): `match /users/{uid}/prices/{doc} { allow read: if request.auth != null && request.auth.uid == uid; allow write: if false; }`

## C. `README-อัปโหลด.md` (ภาษาไทยง่าย ทีละคลิก · ผู้ใช้ไม่ใช้ git)
1. **สร้างกุญแจ:** Firebase console → โปรเจกต์ `trading-dashboard-srtz` → ⚙ Project settings → Service accounts → Generate new private key → ได้ไฟล์ .json · ⚠ ห้ามอัปไฟล์นี้ขึ้น repo / ห้ามส่งให้ใคร · ใช้เสร็จเก็บไว้ที่ปลอดภัยหรือลบ
2. **หา UID:** Firebase console → Authentication → Users → คอลัมน์ User UID ของอีเมลตัวเอง
3. **ใส่ Secrets:** github.com/srtzp/Dashboard → Settings → Secrets and variables → Actions → New repository secret → `FIREBASE_SA` = วางเนื้อไฟล์ .json ทั้งหมด · `FIREBASE_UID` = UID
4. **เพิ่ม rules:** Firebase console → Firestore → Rules → วางบล็อกข้อ B7 ข้าง block coreCards เดิม → Publish
5. **อัป 2 ไฟล์** (วิธีเดียวกับ fundflow: Add file → Create new file · พิมพ์ path `.github/workflows/prices.yml` / `scripts/build_prices.py`)
6. **ทดสอบ:** Actions → prices → Run workflow → เขียว = เปิดแอป หน้าแผน Core เห็น "ราคาอัตโนมัติ: อัปเดต …" · แดง = เปิด log ดูบรรทัดสุดท้าย (มักเป็น secret ผิด / rules)
7. ยกเลิกระบบ: ลบไฟล์ `prices.yml` หรือ Disable workflow · ลบ secret · แอปกลับไปใช้ราคาที่กรอกเอง

## เทส
### Python `tests/test_build_prices.py` (ไม่ใช้เน็ต · `python3 tests/test_build_prices.py`)
1. `to_ysym`: `('PTT','TH')`→`PTT.BK` · `('PTT.BK',None)`→`PTT.BK` · `('avgo','US')`→`AVGO`
2. `weekly_closes`: ข้อมูลรายวันสมมติถึงพุธ → สัปดาห์ล่าสุดที่ได้ = ศุกร์ก่อน · ศุกร์หยุด → `closeDate` = พฤหัส · รันเสาร์ → รวมศุกร์ล่าสุด
3. `ema10`: เทียบกับค่าที่คำนวณมือ 12 สัปดาห์ (ทศนิยม 6 ตำแหน่ง) · < 10 สัปดาห์ → None
4. `check`: close 0 / NaN → ไม่ผ่าน · +45% → suspect
5. `run`: 3 ticker · ตัวที่ 2 fetch error → เขียนตัว 1, 3 + `_meta.failed` มีตัว 2 · ไม่มีการเขียน doc ตัว 2 · ล้มหมด → exit code 1 · การ์ด closed ไม่ถูกดึง · ticker ซ้ำ 2 บัญชี → fetch ครั้งเดียว
6. ไม่มีการพิมพ์ค่า `FIREBASE_SA` ใน stdout/stderr (จับ output ตรวจ)

### Playwright `tests/run_tests_phase43.py` (Chromium · 1440 + 390 · mock Firestore มี `prices`)
1. การ์ด W ถืออยู่ กรอกเอง 100 (2026-09-26) + auto 105 (2026-10-02) → แสดง 105 + ป้าย "อัตโนมัติ" · DD equity ใช้ 105 · "ขาดราคา" ไม่นับตัวนี้
2. กรอกเอง 2026-10-03 → ใช้ที่กรอกเอง · วันเท่ากัน → ใช้ที่กรอกเอง
3. auto ema10w 110 > close 105 (W) → สถานะเหลือง "ปิดใต้ EMA10 · งดเพิ่มไม้" · การ์ด L ตัวเดียวกัน → ไม่ใช้ EMA
4. ไม่มี auto doc → ทุกตัวเลขเท่ากับก่อน PX1 (เทียบค่าที่คำนวณจาก fixture เดิม)
5. auto `suspect:true` → ใช้ค่าที่กรอกเอง + ⚠
6. การ์ด `PTT` ตลาด TH จับคู่ doc `PTT.BK` ได้
7. sheet อัปเดตราคา: แสดงบรรทัดราคาอัตโนมัติ · บันทึก → doc coreCards มีแค่ค่าที่กรอก · **ทุก action อื่นที่เขียนการ์ด (เลื่อน Stop / ซื้อไม้เติม) ไม่ทำให้ค่า auto ไปอยู่ใน coreCards** (ตรวจ key ใน mock db)
8. `_meta` runAt 2026-09-26 (วันนี้ 2026-10-05) → เหลือง "ไม่ได้อัปเดต" · failed ['XYZ'] → "ดึงไม่ได้: XYZ" · ไม่มี `_meta` → ไม่มีบรรทัด
9. prices อ่านไม่ได้ (mock permission-denied) → แอปทำงานปกติ + ข้อความ rules
10. 390px ไม่ล้นแนวนอน · ไม่มี console error
- ภาพ `tests/screenshots/px1-*` (1440 + 390): `card-auto` · `sheet-px` · `status-line`

### เทสเก่า
- เคสเดิมที่สร้างการ์ดมีราคาแล้วคาดค่า (ไม่มี prices) ต้องผ่านเหมือนเดิมโดยไม่แก้ · ถ้าจำเป็นต้องแก้ → จด `tests/PX1_retired.md` (ห้ามลบ ห้ามปล่อยล้ม)
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–43 · `test_build_prices.py`

## รายงานกลับ
จำนวนเคสก่อน → หลัง · รายชื่อจุดที่อ่าน px/pxDate/emaW (ข้อ B2) · รายชื่อ coreWrite ที่ตรวจ · ไฟล์ใน `P2-prices-upload/` · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
