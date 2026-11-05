# WL2 — Watchlist card v2 (Living Thesis) + ลบ Research Card ทั้งระบบ · เทส 40

> ผู้ใช้ 2 ต.ค.: ย้าย Watchlist ไป skill `living-thesis` (JSON `living-thesis@1`) · ของดีจาก Research Card อยู่ใน thesis แล้ว (catalysts มีวันที่ · tier_inputs) → **ลบ Research Card ทั้งระบบ**
> หน้าตา = ม็อกอัป `docs/mockups/wl2-mockup.html` (v3 · ข้อมูล AVGO จริง · ok แล้ว) · spec พื้นฐาน `docs/specs/watchlist-card-spec.md` (brief นี้ทับ spec ตรงที่ต่างกัน)
> JSON ตัวอย่าง = `AVGO_thesis.json` (root) → คัดลอกเป็น `tests/fixtures/avgo_thesis.json`
> สำรองก่อนแก้: `index.backup-pre-WL2.html` · `tests/_bk_wl2/` (ทุกไฟล์เทสที่จะแก้) · ห้ามแตะ core-size.js · กติกา/สูตร Core/Sat/DD เดิมทั้งหมด
> ต่อจาก TD2-fix (`tdBuild`, `tdHomeworkCandidates` ฯลฯ) · ใช้ชื่อฟังก์ชันเป็นหลัก

## 1. ที่เก็บข้อมูล (Firestore · path เดิม)
- `users/{uid}/watchlist/{TICKER}` เพิ่ม field:
  - `thesis` = JSON ทั้งก้อน **ยกเว้น `log`**
  - `thesis_log` = array (append เท่านั้น)
  - `thesis_history` = array ≤ 5 ฉบับล่าสุด `{date, summary}` (snapshot ก่อนแทนที่)
  - `thesis_hits` = `{ "<signal>": "YYYY-MM-DD" }` (ปุ่ม "ชนแล้ว" ข้อ 5) · Import ฉบับใหม่ = ล้างทั้งหมด
- `wlStart()` อ่าน 4 field นี้เข้า `wlItems[]` (ไม่ใช่ object = null/[]/{}) · **อย่าสับสน:** `thesis.tier_inputs` (จาก skill) ≠ `tier_inputs` เดิมของ WT1 (ค่าที่ผู้ใช้กรอกในฟอร์ม Tier) — ห้ามเขียนทับกัน
- Firestore rules ไม่ต้องแก้ · ข้อมูลเก่า `research` collection (`research_card`, `research_card_history`) **ไม่ลบ แค่ไม่อ่าน**

## 2. Import / Export
- ปุ่ม `📥 Import` ที่หัวการ์ด (Watchlist + Candidates) และแถบบนของหน้า Watch (ไม่ผูก ticker) → sheet: ช่องวาง JSON + ปุ่มเลือกไฟล์ `.json` · ตัดข้อความหน้า/หลัง JSON และ ```json fence ได้ (ย้ายฟังก์ชันแบบ `rcTrimJson` มาใช้)
- ตรวจ: parse ได้ · `schema === "living-thesis@1"` · มี `sym` · `summary` เป็น object · `sections.s1–s4.md` เป็น string · array อื่นไม่มี = `[]` · ขนาด ≤ 200KB · ผิด = ข้อความ error ภาษาไทย ไม่บันทึก
- Import จากหัวการ์ด แต่ `sym` ไม่ตรง ticker การ์ด → error `JSON นี้เป็นของ {sym} ไม่ใช่ {ticker}` (เทียบด้วย `wlSymKey`)
- ไม่มี ticker ใน Watchlist → สร้าง doc ใหม่ (`port:'core'` · `market` จาก JSON · `added_at` วันนี้)
- มีอยู่แล้ว → แสดง diff สั้นก่อนยืนยัน: `status` เดิม→ใหม่ · Thesis 1–3 เปลี่ยนไหม · tripwire ที่ level เปลี่ยน · จำนวน catalyst · `date` เดิม→ใหม่ → กด `บันทึก`
- บันทึก: `thesis` แทนที่ · `thesis_log` append เฉพาะบรรทัดที่ยังไม่มี (key = `date + new`) ห้ามลบของเก่า · snapshot เดิมเข้า `thesis_history` (unshift · ตัดเหลือ 5) · `thesis_hits = {}` · **ไม่แตะ** `tier*` · `note` · `industry` · `my_notes` · `added_at`
- เมนู `⋯` ที่หัวการ์ด: `Export JSON` (copy `thesis` + `log: thesis_log` กลับเป็น JSON เต็ม ใช้ส่ง skill โหมด update · มีข้อความ "คัดลอกแล้ว") · `ประวัติ (n)` (รายการ date + ข้อสรุป ของ `thesis_history` · อ่านอย่างเดียว)

## 3. การ์ด (แผงขวาหน้า Watch) — ตามม็อกอัป
**หัวการ์ด:** `TICKER` · ชื่อ · ป้ายพอร์ต · ป้าย Tier เดิม (ผู้ใช้ตั้ง) · ป้ายถือ (เดิม) · ปุ่ม `เปิดแผน Core →` `✎` `✕` (เดิม) + `📥 Import` `⋯`
- บรรทัดรอง: ชิป `Thesis {mode} · {d MMM}` · ชิปสถานะ (`summary.status`: screen คัดกรอง · watch เฝ้าดู · deep ศึกษาลึก · wait_price รอราคา · hold ถือ · pause พัก · exit ออก) · `⚠ ควร update` (ข้อ 6) · `summary.tier_note` ตัวเล็ก `ⓘ` ใต้ชิป
- ไม่มี thesis → ตัวการ์ดแสดง `ยังไม่มี Thesis — รัน living-thesis แล้ว 📥 Import` + ปุ่ม Import (Candidates: + ปุ่ม `＋ เพิ่มเข้า Watchlist` เดิม)

**แท็บ** `[สรุป] [ธุรกิจ] [ทำไมซื้อ] [ติดตาม] [ออกเมื่อ]` (แทน `Overview | Research`) · pill เดิม · 390px ต้องพอดี 5 แท็บ (ลด padding ได้) ถ้าไม่พอ = เลื่อนแนวนอน + แท็บที่เลือก scrollIntoView · จำแท็บล่าสุดต่อ ticker ใน localStorage (try/catch) · แท็บ ออกเมื่อ มีเลขส้ม = จำนวน tripwire ระดับ review/broken
- `wlSub` ใหม่: `sum` `biz` `why` `trk` `exit` · ค่าเก่า `ov`/`rs` = `sum` (ลิงก์เดิมไม่พัง)

| แท็บ | เนื้อหา (เรียงตามนี้) |
|---|---|
| สรุป | แถบแดง/ส้ม ถ้ามี tripwire review/broken (กด = ไปแท็บ ออกเมื่อ) · แถบเหลือง `⚠ ควรรัน living-thesis โหมด update: {เหตุผล}` · **กล่องตัดสินใจ (ฟ้า) 3 บรรทัด:** `ข้อสรุป` (call.action แปลไทย: study ศึกษาต่อ · wait_evidence รอหลักฐาน · wait_price รอราคา · drop ตัดออก — `call.why`) · `ออกถ้า` (`breaker`) · `ถัดไป` (`next`) + บรรทัดเล็ก `📅 ใกล้สุด {~}{d MMM} · อีก n วัน — {event ≤48 ตัว…}` + `+k` ถ้ามีมากกว่า 1 (catalyst ที่ใกล้ที่สุด ≥ วันนี้ จาก `thesis.catalysts` + โน้ตของฉันที่มีวันที่ · ≤ 7 วัน = สีเหลือง · กด = ไปแท็บ ติดตาม · ไม่มี = ไม่แสดงบรรทัดนี้) · จากนั้นรายการ label→ค่า: ธุรกิจ · Thesis (1–3) · ความเสี่ยง #1 · ราคา · Life cycle · Power · เครื่องยนต์ · Unknown |
| ธุรกิจ | `sections.s1.md` |
| ทำไมซื้อ | `sections.s2.md` |
| ติดตาม | 📅 สิ่งที่รอ (Catalysts: thesis + โน้ตของฉัน เรียงวัน · ไม่มีวันไว้ท้าย · ปุ่ม `＋ โน้ต` เดิม) · ⚠ สิ่งที่ต้องระวัง (โน้ตของฉัน `my_notes.blk` · `＋ โน้ต`) · 📊 KPI (`kpi[]`) · ❓ ยังไม่รู้ — must (`gaps` priority must) · **แถบพับ:** คำถามรอง (track/skip) · Milestones & จุดตัดสินใจ (`s3.md`) · Log (`thesis_log` ใหม่สุดบน) |
| ออกเมื่อ | tripwire ระดับ watch ขึ้นไป เรียง broken → review → watch (การ์ดขอบซ้ายสี: watch เหลือง · review ส้ม · broken แดง · ป้ายระดับ · `ตอนนี้: {now} · thesis n · {area}` · ปุ่ม `ชนแล้ว`) · **แถบพับ:** `✓ ปกติ (ok) · n ข้อ` · วิธีอ่าน (`s4.md`) |
- ท้ายแท็บ สรุป/ธุรกิจ/ทำไมซื้อ/ติดตาม: แถบพับ `หลักฐาน & แหล่งที่มา · {evidence} · {sources}` → ตาราง evidence + ลิงก์ sources (`target=_blank rel=noopener`) + `audit`
- **แถบพับ (ผู้ใช้: ของรองต้องกดดูง่าย):** ปุ่มกว้างเต็มการ์ด สูง ≥ 44px · ชื่อซ้าย · ชิปจำนวนขวา (`3 ข้อ` / `17 · 8` / `3.1–3.4`) · ▾/▴ · กดทั้งแถบได้ · `aria-expanded` · ค่าเริ่มต้นพับ · จำสถานะในหน่วยความจำของหน้า
- **มือถือ ≤ 430px:** ตาราง `gaps` และ `kpi` เป็นรายการซ้อน (ตามม็อกอัป) · ตาราง markdown/evidence/log = wrapper `overflow-x:auto` · หน้าไม่เลื่อนข้าง
- ไม่มีข้อมูลส่วนไหน (array ว่าง) = ซ่อนหัวข้อนั้น (ไม่มีหัวข้อเปล่า)

## 4. Markdown renderer (เขียนเอง ไม่ใช้ lib · ฟังก์ชันเดียว `ltMd(src)`)
- **escape HTML ก่อน parse เสมอ** · รองรับ: `###` · `-`/`*` bullet (ข้าม bullet ว่าง เช่น `- ` เปล่า — มีจริงใน AVGO s1) · `1.` ลำดับเลข · ตาราง `| |` (ข้ามแถว `|---|`) · `>` quote · `**bold**` · บรรทัดว่าง = ย่อหน้า
- ป้าย `[F] [C]` เขียว · `[M]` ม่วง · `[I]` ฟ้า · `[A]` ส้ม · `[?]` เทา → chip เล็ก (ใช้ทั้งใน md และ summary/kpi/gaps/evidence)
- ลิงก์ใน md ไม่ต้องรองรับ (แสดงเป็นตัวอักษร)

## 5. ปุ่ม "ชนแล้ว" (tripwire กดเอง · ผู้ใช้ 2 ต.ค.)
- ทุก tripwire มีปุ่ม `ชนแล้ว` · กด = `thesis_hits[signal] = วันนี้` → level ที่แสดง = broken (ป้าย `broken · กดเอง`) · กดซ้ำ (`✓ ชนแล้ว (กดยกเลิก)`) = ลบ
- ใช้กับ: เลขบนแท็บ ออกเมื่อ · แถบแดงในแท็บ สรุป · Today 🔴 · `⚠ ควร update`
- เก็บที่ watchlist doc (`update({thesis_hits})`) · Import ใหม่ล้าง

## 6. ⚠ ควร update (หัวการ์ด · ผู้ใช้ 2 ต.ค.)
แสดงเมื่อข้อใดข้อหนึ่ง (เหตุผลต่อกันด้วย ` · ` ใน title และแถบเหลืองในแท็บ สรุป):
1. `thesis.date` เก่ากว่า **100 วัน** (`WL_THESIS_STALE_DAYS = 100`) → `Thesis อายุ n วัน`
2. มี `thesis.catalysts` ที่ `date` < วันนี้ (skill โหมด update ลบอันที่ผ่านแล้ว → ยังอยู่ = ยังไม่ update) → `{event สั้น} {d MMM} ผ่านไปแล้ว`
3. มี `thesis_hits` → `กด "ชนแล้ว" n ข้อ`
- **ไม่สร้างแถวใน Today** (ปกติ = เงียบ) → ใช้ดันลำดับการบ้านแทน (ข้อ 7)

## 7. แท็บ Today (แทนส่วนที่อ่าน research_card)
- 🔴 `⛔ {T} Tripwire {พัง|ชนแล้ว} "{signal ≤60}" → ทบทวนการถือ` — level broken จาก skill หรือ `thesis_hits` · ไป `wlOpen(T,'exit')`
- 🟡 `🟠 {T} Tripwire ถึงระดับทบทวน "{signal ≤60}"` — level review · ไป `wlOpen(T,'exit')` · **watch/ok = เงียบ**
- 🟡 catalyst ≤ 7 วัน (≤ 5 แถว · เดิม) = `thesis.catalysts` **+ `my_notes.cat` ที่มีวันที่** (ผู้ใช้ 2 ต.ค.) · บรรทัดรอง `Watch · ติดตาม` (+ ` · โน้ตของฉัน`) · ไป `wlOpen(T,'trk')`
- ลบ guard เดิม `tripwire` / `tw-check` / `catalyst` ที่อ่าน `research_card` (แถว `tw-check` "มีข่าวเข้าเงื่อนไข" หายไป — ข่าวอัตโนมัติไปทำรอบ research-team pusher ภายหลัง)
- **การบ้าน `tdHomeworkCandidates()`** ลำดับใหม่: (1) ยังไม่มี Thesis → `ยังไม่มี Thesis` · (2) ⚠ ควร update → `ควร update: {เหตุผลแรก}` · (3) `thesis.date` เก่าสุด → `Thesis เก่า n วัน` · กติกาอื่นเดิม (ข้าม 14 วัน · เปลี่ยนตัว · วน)

## 8. ฟอร์ม Tier — "เติมจาก Thesis" (แทน "เติมจาก Research")
- แสดงปุ่มเมื่อ watchlist item ของ ticker นี้มี `thesis.tier_inputs` ที่มีค่า (`v` ไม่ null) ≥ 1 ช่อง
- จับคู่: `roic→tiRoic` · `ndEbitda→tiNd` · `fcfConv→tiFcf` · `revGrowth→tiRev` · `revCagr3→tiCagr` · `opMargin→tiOpm` · `opMarginPrev→tiOpmPrev` · `fcfPositive3y→fcf3y` · `capitalReturn→capret` · `ocfPositive→ocf` · `netCash→netcash`
- เติมเฉพาะช่องว่าง/ยังไม่ตอบ · ไม่แตะ Gate 5 / ปุ่ม Tier / เหตุผล (เหมือน RC2) · ช่องที่เติม `title` = `{tag} · {period} · {src}`
- ข้อความ: `เติม n ช่อง · ข้าม m ช่องที่กรอกแล้ว · จาก Thesis {d MMM} (ข้อมูล ณ {asOf d MMM})` · ไม่มีช่องว่าง = `ไม่มีช่องว่างให้เติม`

## 9. ลบ Research Card ทั้งระบบ
- ลบออกจาก index.html: โค้ด inline ของ research-card.js (ทั้งบล็อก `/* source: research-card.js … */`) · `wlResearchHtml` · `wlOvResChip` · ส่วน research_card ใน `wlActionChip`/`rsUrgency`/`wlLine2`/`wlRowHtml`/สถานะ `n ตัวรอสร้าง Research Card` · ปุ่ม/ข้อความ "เติมจาก Research" · RC prompt/validate/merge · `research_card_history`
- แทนด้วย thesis: จุดสถานะในรายชื่อ (`มี Thesis` / `รอสร้าง Thesis`) · สถานะบน `n ตัวรอสร้าง Thesis` · `wlLine2` core = `thesis.summary.biz` · บรรทัดวันที่หัวการ์ด
- `RS_DEMO`: ถ้ามี `research_card` ให้ลบ field นั้น (ไม่ต้องใส่ thesis ตัวอย่าง)
- **Acceptance:** `grep -c "research_card\|research-card\|rcTierMetrics\|เติมจาก Research" index.html` = 0 (คอมเมนต์ประวัติก็เอาออก)
- ไฟล์ (ห้ามลบ · **ย้ายด้วย `mv -n`**): `research-card.js` · `research-card-test.js` · `inline-research-card.py` · `research-card.backup-*.js` · `research-card-test.backup-*.js` → `_to_delete/research-card/` (ผู้ใช้ลบเอง)
- Candidates: เก็บรายชื่อเดิม (จาก `research` collection ที่ไม่อยู่ใน Watchlist) · กดเข้า = การ์ด "ยังไม่มี Thesis" + Import + เพิ่มเข้า Watchlist (เดิม)

## เทส `tests/run_tests_phase40.py` (Chromium · 1440 + 390 · mock Firestore · นาฬิกาปลอม 2026-10-02 13:03 ไทย · fixture `tests/fixtures/avgo_thesis.json`)
1. Import AVGO (วาง JSON มี ```json fence + ข้อความหน้า/หลัง) → doc `watchlist/AVGO` มี `thesis` (ไม่มี log) · `thesis_log` 1 บรรทัด · 5 แท็บแสดงครบ · ไม่มี HTML หลุด · ไม่มี `undefined`/`null`/`[object` ในข้อความ
2. Import ซ้ำ: log ใหม่ 1 บรรทัด + บรรทัดเดิม → `thesis_log` = 2 · diff แสดงก่อนยืนยัน · `tier`/`tier_inputs` (WT1)/`my_notes`/`note` ไม่เปลี่ยน · `thesis_history` = 1 · ยกเลิก = ไม่เขียน
3. ผิด: schema อื่น · JSON พัง · sym ไม่ตรงการ์ด · เกิน 200KB → error ไทย · DB ไม่เปลี่ยน
4. `<script>` / `<img onerror>` ใน summary/md/evidence → แสดงเป็นตัวอักษร · ไม่มี element ใหม่
5. ticker ใหม่ (ไม่อยู่ใน Watchlist) → สร้าง doc `port:'core'` · market จาก JSON
6. แท็บ สรุป: กล่องตัดสินใจ 3 บรรทัด (ข้อสรุป `ศึกษาต่อ` · ออกถ้า · ถัดไป) อยู่บนสุด · บรรทัด 📅 = `~10 ธ.ค. · อีก 69 วัน` · เพิ่มโน้ต cat วันที่ 2026-10-05 → บรรทัด 📅 เปลี่ยนเป็นโน้ตนั้น `อีก 3 วัน` สีเหลือง + `+2` · กดบรรทัด → แท็บ ติดตาม · ไม่มี catalyst → ไม่มีบรรทัด 📅
7. renderer: `1.` เป็น `<ol>` · bullet ว่างไม่มี `<li>` ว่าง · ตาราง s1.2 เป็น `<table>` ใน wrapper overflow · `[F]` เป็น chip
8. ติดตาม: ลำดับหัวข้อ catalysts → ระวัง → KPI → must · gaps must 3 ตัว · แถบพับ 3 แถบพร้อมจำนวน (`3 ข้อ` · `3.1–3.4` · `1 รายการ`) · กดแถบ = กาง (`aria-expanded=true`) · กดซ้ำ = พับ · แถบสูง ≥ 44px
9. ออกเมื่อ: แสดง watch 3 ตัว · แถบ `✓ ปกติ (ok) · 4 ข้อ` · กด `ชนแล้ว` ข้อแรก → `thesis_hits` มี signal · ป้าย `broken · กดเอง` · เลขบนแท็บ = 1 · หัวการ์ด `⚠ ควร update` · แท็บ สรุป มีแถบแดง · Today มีแถว 🔴 → กดยกเลิก = กลับครบ · Import ใหม่ → `thesis_hits` ว่าง
10. ⚠ ควร update: `date` 101 วันก่อน → มี · 99 วัน → ไม่มี · catalyst วันที่เมื่อวาน → มี (เหตุผลมีวันที่)
11. Today: tripwire level review (fixture แก้ 1 ข้อ) → แถว 🟡 ไป `wlOpen(T,'exit')` · level watch → ไม่มีแถว · catalyst thesis ภายใน 7 วัน + โน้ตมีวันที่ภายใน 7 วัน → ขึ้นทั้งคู่ (≤ 5) · catalyst +10 วัน → ไม่ขึ้น
12. การบ้าน: NOTH (ไม่มี thesis) · STALE (มี hit) · OLD (date 60 วัน) · NEW (date 5 วัน) → ลำดับ NOTH → STALE → OLD → NEW · เหตุผล `ยังไม่มี Thesis` / `ควร update: …` / `Thesis เก่า 60 วัน`
13. ฟอร์ม Tier: ปุ่ม `เติมจาก Thesis` → เติม 11 ช่อง (ROIC 15.5 · ND 1.4 · FCF 148 · …) · netCash = ไม่ใช่ · ช่องที่กรอกไว้ก่อนไม่ถูกทับ · ข้อความถูก · ticker ที่ไม่มี thesis = ไม่มีปุ่ม
14. ไม่มี thesis → การ์ด "ยังไม่มี Thesis" + Import · Candidates กดเข้าเหมือนกัน + ปุ่มเพิ่มเข้า Watchlist
15. Export JSON → clipboard (stub) = JSON ที่ `schema` ครบ + `log` = thesis_log · `⋯ ประวัติ (1)` หลังข้อ 2
16. จำแท็บต่อ ticker หลังรีโหลด · ลิงก์เก่า `wlOpen(T,'ov')` / `'rs'` → แท็บ สรุป
17. 390px: 5 แท็บมองเห็นครบ/เลื่อนได้ · แท็บที่เลือกอยู่ในจอ · gaps/kpi เป็นรายการซ้อน · ไม่ล้นแนวนอน (`overflow_x` เดิม) · `elementFromPoint` ของแถบพับ/ปุ่มชนแล้ว = ตัวมันเอง · ไม่มี console error
18. grep index.html: research_card / research-card / rcTierMetrics / เติมจาก Research = 0 · ไฟล์ research-card* อยู่ใน `_to_delete/research-card/` ไม่อยู่ที่ root
- ภาพ `tests/screenshots/wl2-*` (1440 + 390): `sum` · `trk-open` · `exit-hit` · `import-diff` · `no-thesis` · `today` · `tier-fill` — เทียบม็อกอัป

### เทสเก่า (แก้ความคาดหวัง ห้ามลบ ห้ามปล่อยล้ม · จด `tests/WL2_retired.md` ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- เคสที่อ้าง Research Card/แท็บ Overview-Research → ทดสอบพฤติกรรมเทียบเท่าบน thesis (เช่น "เติมจาก Research" → "เติมจาก Thesis" · Overview → แท็บ สรุป/ติดตาม · ชิป Research → ชิป Thesis) · ถ้าไม่มีของเทียบ → เปลี่ยนเป็นเช็กว่า "ไม่มีแล้ว"
- จุดที่รู้: phase32 (~26 จุด · RC2) · phase35 (~21 · WL1 Overview) · phase33 (~4 · WT1) · phase38 (~4 · Today tripwire/catalyst) · phase39 (การบ้าน "ยังไม่มี Research Card") · phase8 (~3) · grep `research_card|Research Card|wlSetSub\('rs'\)|tiFillRc` ทั้ง tests/ ให้ครบ
- `research-card-test.js` ย้ายไป `_to_delete/` แล้ว → เอาออกจากรายการรัน (จดใน retired) · เทส p22 ที่เช็กไฟล์ใน `_to_delete/` ไม่ต้องแตะ
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–40

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ตารางจุดที่แก้ · ไฟล์ที่ย้าย · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
