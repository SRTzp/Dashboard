# WT1 — ปุ่ม "บันทึกเฉพาะ Tier" ในฟอร์มแผน Core (ไม่ต้องมี Entry/SL) → เก็บที่ Watchlist → แผนดึงไปใช้ · เทส 33

> ผู้ใช้ 1 ต.ค.: "จะบันทึก Tier ต้องใส่ Entry/SL ด้วย ทำไว้ก่อนใน Watchlist ไม่ได้" → ตัดสิน **แบบ B**: กรอก Tier ในฟอร์มแผนเดิม แล้วกด "บันทึกเฉพาะ Tier" · **Tier เก็บที่เดียว = watchlist doc** · แผนใหม่ดึงจาก Watchlist · หน้าตั้ง Tier แยกในแท็บ Watch = ยังไม่ทำ (ค่อยพิจารณาทีหลัง)
> ตอนนี้: Watchlist มีแค่ dropdown A/B (`#wlAddTier` ใน `wlOpenEdit`/`wlAddSave` · 7E-2b-2) · กล่อง Tier คำนวณ (`coreTierBlockHtml` · TIER2 + RC2) อยู่ในฟอร์มแผน Core กับ sheet "Tier…" ของการ์ด
> สำรองก่อนแก้: `index.backup-pre-WT1.html` · **ห้ามแตะ** core-size.js (classifyTier/tierBadge ใช้ของเดิม) · research-card.js · ขนาดไม้/heat/บันได · หน้าตาการ์ด Core
> ใช้ชื่อฟังก์ชันเป็นหลัก (เลขบรรทัดอ้างจากไฟล์หลัง RC2 · 1,023,929 bytes)

## ข้อมูล (watchlist doc `users/{uid}/watchlist/{ticker}`)
เพิ่มฟิลด์ (เขียนพร้อม `tier` + `tier_set_at` เดิม):
| ฟิลด์ | ค่า |
|---|---|
| `tier_lens` | `'fortress'` \| `'growth'` \| `'both'` \| `null` (B = null) |
| `tier_inputs` | รูปเดียวกับ `card.tierInputs` (ตัวเลข + ติ๊ก + gate5) |
| `tier_computed` | `'A'`\|`'B'` ผลคำนวณก่อน override |
| `tier_reason` | string \| null (บังคับเมื่อเลือกมุมที่คำนวณไม่ผ่าน · กติกาเดิมของ TIER2) |
- `wlItems` อ่านฟิลด์ใหม่ด้วย (ตรวจชนิดเหมือนที่อ่าน `tier`) · doc เก่ามีแค่ `tier:'A'` = มุม Fortress (เดิม) เหมือนการ์ด (`coreLensOf`)
- ล้าง Tier = ลบทั้ง 6 ฟิลด์ (`FieldValue.delete` · mock = null) เหมือนที่ทำกับ `tier` ตอนนี้

## แก้
### 1. ปุ่ม "บันทึกเฉพาะ Tier" ในฟอร์มแผน Core (`coreNewOpen` · โหมด `new` เท่านั้น)
- ปุ่มใหม่ท้ายกล่อง Tier (ใต้ "Tier ที่ใช้จริง" / เหตุผล) `id="cnTierOnly"` `data-cn-tieronly` ข้อความ **"บันทึกเฉพาะ Tier"** + บรรทัดเล็ก "ยังไม่สร้างแผน · ไม่ต้องใส่ Entry/Stop"
- กดได้เมื่อ: ticker ถูกต้อง (`wlValidTicker`) และ `coreTiEval()` ไม่ติด `REASON_REQUIRED` · **ไม่ตรวจ** Entry/Stop/f/บันได/โควตา
- กด → เขียน watchlist doc (ฟิลด์ตามตาราง + `tier_set_at = thaiToday()`) → ปิดฟอร์ม → **ไม่สร้างการ์ด** · แจ้งสั้น ๆ "บันทึก Tier {ticker} = A · Fortress แล้ว (Watchlist)" (ใช้ toast/แถบแจ้งที่มีอยู่ ถ้าไม่มีใช้ข้อความในหน้า ไม่ใช้ `alert`)
- ticker **ไม่อยู่ใน Watchlist** → ปุ่มเป็น "บันทึกเฉพาะ Tier (เพิ่มเข้า Watchlist)" → สร้าง doc ใหม่ `{ticker, market: coreMarketOf(ticker), port:'core', note:'', industry:'', added_at}` + ฟิลด์ Tier
- จับคู่ Watchlist ด้วย `wlSymKey` (PTT = PTT.BK) · เขียนลง doc เดิมที่เจอ (ไม่สร้างซ้ำ)
- โหมด `edit` / `convert` / sheet "Tier…" ของการ์ด: ไม่มีปุ่มนี้ (ของเดิมทำงานเหมือนเดิม)

### 2. แผนใหม่ดึง Tier จาก Watchlist
- `coreNewOpen` โหมด `new`: ticker ตรงกับ Watchlist ที่มี `tier_inputs` → กล่อง Tier เริ่มด้วยค่าจาก Watchlist (ตัวเลข · ติ๊ก · Gate 5 · ปุ่ม Tier = `tier`+`tier_lens` · เหตุผล)
- ticker เปลี่ยนในฟอร์ม (จุดที่ `coreNewIn` เรียก `coreTiWlShow`) → ถ้า**ผู้ใช้ยังไม่ได้แตะกล่อง Tier** ให้โหลดค่าของ ticker ใหม่ (หรือเคลียร์ถ้าไม่มี) · แตะแล้ว = ไม่ทับ
- `#tiWlInfo` เมื่อดึงมา: `Tier จาก Watchlist (ตั้งเมื่อ YYYY-MM-DD)` · ไม่มี = ข้อความเดิม
- "บันทึกแผน" ตามปกติ = เขียน Tier ลงการ์ดเหมือนเดิม **และไม่เขียนกลับ Watchlist** (ถ้าอยากอัปเดต Watchlist ให้กด "บันทึกเฉพาะ Tier" ก่อน) · ป้ายเทียบ Tier การ์ด↔Watchlist เดิมยังทำงาน

### 3. Watchlist
- โมดัลแก้ไข (`wlOpenEdit`): **แทน** dropdown `#wlAddTier` ด้วยบรรทัดสถานะ `Tier A · Fortress · ตั้งเมื่อ …` / `ยังไม่ตั้ง Tier` + ปุ่ม `ตั้ง Tier…` (`id="wlAddTierBtn"` → ปิดโมดัล → `wlOpenCorePlan(ticker)` ที่มีอยู่แล้ว) + ลิงก์ `ล้าง Tier` (เมื่อมี tier · ลบ 6 ฟิลด์) · โมดัลเพิ่มหุ้นใหม่ = ไม่มีส่วน Tier · `wlAddSave` **ไม่เขียนฟิลด์ tier อีกแล้ว**
- `wlTierChips`: แบบ long (Overview) แสดง `A · Fortress` / `A · Growth` / `A · ทั้งคู่` / `B` (doc เก่า = `A · Fortress (เดิม)`) · แบบสั้นคง `A`/`B` · ชิป "ทบทวน" (เกิน 12 เดือน) เหมือนเดิม
- ชิป Tier ใน Overview กดได้ → `wlOpenCorePlan(ticker)` · หุ้นที่ยังไม่ตั้ง = ชิปจาง `ตั้ง Tier` (เฉพาะ Overview)

### 4. จับคู่ ticker หุ้นไทย (ค้างจาก RC2)
- `coreTiRcFound` และการหา Watchlist item ในข้อ 1–2 ใช้ `wlSymKey` แบบเดียวกับ `coreWatchInfo` — ไม่ใช่ `coreNorm` ตรง ๆ

## เทส `tests/run_tests_phase33.py` (Chromium · 1440 + 430 · mock Firestore)
seed: Watchlist `AVGO` (US · ไม่มี tier) · `OLDA` (tier `'A'` เก่า ไม่มีฟิลด์ใหม่) · `PTT.BK` (TH · research doc `PTT` มีการ์ดแบบ RC2) · บัญชี US + TH
1. แผนใหม่ AVGO · ไม่กรอก Entry/Stop · กรอกชุด Fortress + Gate 5 "ไม่" ×3 → ปุ่ม "บันทึกเฉพาะ Tier" กดได้ (ปุ่ม "บันทึกแผน" ยังปิด) → กด → ฟอร์มปิด · **ไม่มีการ์ดใหม่** · doc: `tier:'A'` · `tier_lens:'fortress'` · `tier_inputs` ครบ · `tier_computed:'A'` · `tier_set_at` = วันนี้ไทย · มีข้อความแจ้ง
2. เลือก A · Growth ที่คำนวณไม่ผ่าน ไม่ใส่เหตุผล → ปุ่มปิด · ใส่เหตุผล → กดได้ · `tier_reason` ถูกเก็บ
3. ticker `NEWX` (ไม่อยู่ Watchlist) → ป้ายปุ่มมี "(เพิ่มเข้า Watchlist)" → กด → มี doc `NEWX` market US port core + ฟิลด์ Tier
4. Overview AVGO: ชิป `A · Fortress` · กดชิป → เปิดฟอร์มแผนใหม่ ticker AVGO · กล่อง Tier มีค่าครบ · ปุ่ม A · Fortress ติด · `#tiWlInfo` = "Tier จาก Watchlist (ตั้งเมื่อ …)"
5. ต่อจากข้อ 4: กรอก Entry/Stop → บันทึกแผน → การ์ดได้ Tier A · Fortress · **ไม่มี**ป้าย "ยังไม่ได้ตั้ง Tier ใน Watchlist"
6. แผนใหม่ AVGO: แก้ ROIC แล้ว "บันทึกแผน" → การ์ดได้ค่าใหม่ · Watchlist doc **ไม่เปลี่ยน**
7. แผนใหม่: ticker AVGO แล้วเปลี่ยนเป็นตัวที่ไม่มี tier (ยังไม่แตะกล่อง) → กล่องเคลียร์ · แตะกล่องแล้วค่อยเปลี่ยน ticker → ค่าที่กรอกไม่หาย
8. โมดัลแก้ไข AVGO: ไม่มี dropdown A/B · มีสถานะ + "ตั้ง Tier…" (เปิดฟอร์มแผน) · "ล้าง Tier" → 6 ฟิลด์หาย/null · ชิปกลับเป็น "ตั้ง Tier" · โมดัลเพิ่มหุ้นใหม่ไม่มีส่วน Tier และบันทึกแล้ว doc ไม่มีฟิลด์ tier
9. OLDA → ชิป `A · Fortress (เดิม)` · แผนใหม่ OLDA → กล่อง Tier ว่าง (ไม่มี inputs) · ป้ายการ์ดเดิมยังทำงาน
10. PTT.BK: แผนใหม่บัญชี TH → ปุ่ม "เติมจาก Research" เห็น (doc `PTT`) · "บันทึกเฉพาะ Tier" เขียนลง doc Watchlist ที่มีอยู่ (ไม่สร้างซ้ำ)
11. โหมด edit/convert และ sheet "Tier…" ของการ์ด → ไม่มีปุ่ม "บันทึกเฉพาะ Tier"
12. 430px: ปุ่ม + บรรทัดเล็กไม่ล้นแนวนอน (เช็กราย element) · ไม่มี console error
- ภาพ `tests/screenshots/wt1-*` (1440 + 430): `tieronly-btn` (scroll ให้เห็นปุ่ม + ปุ่มบันทึกแผนที่ปิด) · `wl-chip` · `wl-edit` · `plan-prefill`

## เทสเก่า
- เคสที่ใช้ `#wlAddTier` / คาด dropdown A/B (เช่น phase 29) → **แก้ความคาดหวังของเคส (ห้ามลบ ห้ามปล่อยล้ม)** ให้ตั้งผ่านปุ่มใหม่ หรือ seed ฟิลด์ใน doc ตรง ๆ · จดใน `tests/WT1_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- รันครบ: `node research-card-test.js` · `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–33

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ตารางจุดที่แก้ · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์

## หลังขึ้นเว็บ (ผู้ใช้)
แผน → ＋ แผน Core → ticker AVGO → "เติมจาก Research" → ตอบ Gate 5 → **บันทึกเฉพาะ Tier** → Watch → AVGO เห็นชิป A · … · วันที่จะเข้าไม้: กดชิป/เปิดแผน → กล่อง Tier มาเอง → ใส่ Entry/Stop → บันทึกแผน
