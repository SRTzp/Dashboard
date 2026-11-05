# PF1 — Strategy = Macro only · new plan form (TF / Trend / Classify · Zone Activation · Setup) · Strategy Trend system removed · tests 98

> User spec 24 Oct (Thai, below in **Part A — verbatim, authoritative**). **Mockup:** `docs/mockups/pf1-mockup.html` (view at 300 / 390 / 1440; section ② is clickable; grey "ที่ถูกตัดออก" boxes and yellow notes are explanations — do not build them). Part B = orchestrator notes: code anchors, decisions on gaps, tests, process. If Part B ever conflicts with Part A, Part A wins — stop and report.
> **This spec replaces earlier instructions for Strategy and the Main/Tactical plan form** (LN1 → LN3fix3c decisions about Strategy Trend / Zone / B&P / Shift / new-week Trend reset / Trend flip reasons no longer apply).
> Keep UI and theme; reuse existing CSS / controls; no redesign; no refactor of unrelated parts. Legacy view (`ln1_plan_view = legacy`) — see B6.
> Continue from HD1 (index sha `3e3c4ed6…`). Backups: `index.backup-pre-PF1.html` · `tests/_bk_pf1/` · do not touch core-size.js · every temp file (including your own) → `_to_delete/` · **never rm** · no push.

---

## Part A — User spec (verbatim)

ปรับ Dashboard โดยใช้ index.html เป็นฐาน สเปกนี้แทนคำสั่งก่อนหน้าในส่วน Strategy และฟอร์มแผน Main/Tactical

คง UI และธีมเดิม ใช้ CSS/control เดิม ห้าม redesign หรือ refactor ส่วนที่ไม่เกี่ยวข้อง

### 1. Strategy — เหลือเฉพาะ Macro
เก็บ:
- ภาพรวม Macro
- เปลี่ยนเมื่อ
- ความคิดเห็นเรา
- รูปแนบ พร้อมคำกำกับ “ภาพ Week with EMA50”
- เพิ่มปุ่มลบรูป โดยใช้ระบบจัดเก็บรูปเดิม

ตัดออกจาก Strategy:
- Trend และปุ่ม Up/Down/Flat
- Zone และ B&P
- Shift
- คำเตือนและ control ที่มีไว้สำหรับรายการข้างต้น

เก็บการเลือก Asset, การเลือกสัปดาห์ และ Risk บัญชีเดิม
การสร้างแผนใหม่ต้องไม่ต้องเลือก Trend ใน Strategy อีกต่อไป
ไม่ลบข้อมูลเก่าทิ้ง เพียงหยุดใช้ฟิลด์เหล่านี้เป็นเงื่อนไขของ workflow ใหม่

### 2. ฟอร์มแผนใหม่ — ใช้ทั้ง Main และ Tactical
คงตัวเลือก Main/Tactical และข้อมูลบัญชีเดิม
จัดส่วนประเมินการเทรดเป็น 3 แถว:

แถว 1: TF | Trend | Classify
- TF เป็น dropdown: 15m / 30m / 1H / 4H / Daily / Weekly
- Trend เป็น dropdown: Up / Down เท่านั้น
- Classify เป็น dropdown: Strong / Normal / Uncertain
- Trend เริ่มต้น “— เลือก —” ไม่ตั้งทิศให้อัตโนมัติ
- Classify เริ่มต้น “— เลือก —”
- TF ใช้ค่าเดิมหรือค่า default ของ Main/Tactical จาก settings
- หาก TF ของแผนเก่าอยู่นอกตัวเลือก ให้แสดงค่าเดิมได้ ไม่ทิ้งค่า

Trend และทิศเทรด:
- Up = Long
- Down = Short
- แสดง Up เป็นสีเขียว Down เป็นสีแดง ทั้งค่าที่เลือกและสถานะบนการ์ด
- ต้องมีข้อความ Up/Down เสมอ ไม่สื่อด้วยสีอย่างเดียว
- ใช้โทนสีเขียว/แดงของระบบเดิม
- เมื่อเปลี่ยน Trend ให้ sync bias ผ่านเส้นทางอัปเดตเดิม เพื่อคำนวณข้อมูลที่เกี่ยวข้องใหม่อย่างถูกต้อง
- ยังไม่เลือก Trend ให้เก็บเป็นร่างได้ แต่ห้ามสร้าง order
- Classify เป็นข้อมูลประกอบ ไม่เปลี่ยนสูตร Risk หรือขนาดไม้

แถว 2: Zone Activation
- Checkbox “Zone Activation”
- ช่องกรอก Zone เช่น 4,230–4,250
- ใช้ทั้ง Main และ Tactical
- เก็บ Zone เป็นข้อมูลของแต่ละแผน ไม่ดึงจาก Strategy
- Checkbox ให้ผู้ใช้ติ๊กเอง ไม่ตรวจราคาอัตโนมัติ
- ไม่แสดงคำเตือนเดิม “⚠ ไม่อยู่ใน Zone”
- ไม่เพิ่มกฎบล็อก order จาก checkbox นี้

แถว 3: Setup
มี checkbox แบบเดิมเพียง 2 ตัว:
- Into the zone
- Average support
เลือกได้อิสระทั้งสองตัว เก็บแยกจาก Zone Activation
ไม่เพิ่มเงื่อนไขบังคับใหม่ว่าต้องติ๊กครบ

### 3. ตัดออกจากฟอร์ม
- ช่อง Idea
- ปุ่ม Long / Short เพราะทิศมาจาก Trend
- Setup ตัวเลือกเดิมใน UI แทนด้วย 2 ตัวตามข้อ 2
- ไม่สร้าง Activation แบบ Key Criteria / Support Criteria ตามข้อเสนอเก่า
- ไม่แสดง TF ซ้ำในส่วน “เพิ่มเติม”

ลำดับ:
Main/Tactical selector และข้อมูลบัญชีเดิม
→ TF / Trend / Classify
→ Zone Activation + ช่อง Zone
→ Setup
→ Entry / SL / TP ตามรูปแบบเดิมของแต่ละประเภท
→ ส่วนอื่นเดิม

### 4. ข้อมูลและความเข้ากันได้
- เก็บค่าผ่านระบบบันทึก/โหลดเดิม
- ข้อมูลเป็นของแต่ละแผน ไม่รั่วข้ามแผน
- สลับ Main/Tactical ในร่างเดียวกันแล้วค่าที่กรอกต้องไม่หาย
- แผนเก่า: map bias Long → Up, Short → Down; ไม่มีทิศให้ว่าง
- Classify ของแผนเก่าให้ว่าง
- รักษาข้อมูล Idea, Setup และ Zone เก่าไว้ ไม่ลบทิ้งหรือแปลงว่าเป็น Setup ใหม่ที่ผ่านแล้วโดยอัตโนมัติ
- ไม่เปลี่ยนทิศหรือข้อมูลย้อนหลังของ order/position ที่สร้างไปแล้ว
- การลบรูปต้องคงข้อความความคิดเห็นและข้อมูลอื่นไว้

### 5. ตรวจ dependency ให้ครบ
ตรวจทุกจุดที่เคยพึ่ง Trend/Zone/Shift ของ Strategy โดยเฉพาะ:
- ปุ่มสร้างแผน
- ทิศเทรดและ readiness
- Tactical ที่เคยอ้าง Bias จาก Strategy
- คำเตือน/การบล็อก/ป้ายสถานะที่อ้างข้อมูลเหล่านี้

ให้ใช้ Trend ของแผนเป็นทิศอ้างอิงใหม่ ห้ามเหลือเงื่อนไขซ่อนที่บังคับให้ตั้ง Trend ใน Strategy ที่ถูกนำออกแล้ว
ส่วนกฎ Macro และกฎความเสี่ยงอื่นให้คงเดิม

จุดเริ่มตรวจ:
- ln1TileHtml
- ln1CardHtml
- ln3ZoneCheckHtml
- satV2SetDir
- satV3IdeaWrite
รวมถึงเส้นทางบันทึก โหลด และ validation ที่เกี่ยวข้องจริง

### 6. ขอบเขตที่ห้ามเปลี่ยน
- ธีม สีหลัก ฟอนต์ และ layout หลัก
- สูตร Risk ขนาดไม้ และกฎบัญชี
- การคำนวณ Entry/SL/TP เดิม
- แท็บและฟีเจอร์อื่นที่ไม่เกี่ยวข้อง

### 7. ตรวจหลังแก้
- Strategy เหลือข้อมูลตามสเปก รูปแสดงคำกำกับและลบได้
- สร้างแผนได้โดยไม่ตั้ง Trend ใน Strategy
- Main/Tactical ใช้ฟอร์มใหม่ครบทั้ง 3 แถว
- Up/Down แสดงสีถูกต้องและสร้าง bias ถูกฝั่ง
- ไม่มี Trend → ยังสร้าง order ไม่ได้
- บันทึก เปิดใหม่ และสลับ Main/Tactical แล้วข้อมูลไม่หาย
- Setup และ Zone Activation ไม่ติ๊กแทนกัน
- แผนเก่าเปิดได้ ข้อมูลและ position เดิมไม่เสีย
- ไม่มี control หรือคำเตือนเก่าหลงเหลือ
- ตรวจ desktop/mobile โดยคงหน้าตาเดิม

ลงมือแก้ได้เลย แล้วสรุปสิ่งที่เปลี่ยน ผลการตรวจ และส่วนที่ยังตรวจไม่ได้

### 8. ยกเลิกระบบล็อกและตรวจเทียบ Trend จาก Strategy ทั้งหมด
- ยกเลิกการ fix/lock Trend ระดับ Strategy
- เอาคำเตือน “สวน Trend / สวน Bias / เปลี่ยนทิศจาก Strategy” ออกทั้งหมด
- เอา popup ยืนยัน ช่องบังคับใส่เหตุผล โควตาการเปลี่ยนทิศ และประวัติสลับ Trend ออกจาก workflow
- ยกเลิกการบล็อก การลดขนาดไม้ และการจัดเป็น “นอกแผน” ที่เกิดจากทิศไม่ตรงกับ Strategy
- ไม่อ่าน Trend/Bias เก่าของ Strategy มาเป็น fallback หรือใช้ตัดสินใจเบื้องหลัง

Trend ของแผนเป็นแหล่งกำหนดทิศเพียงจุดเดียว:
- Up → Long
- Down → Short
- เปลี่ยนได้โดยตรง ไม่เตือนหรือถามยืนยันเพราะเปลี่ยน Trend
- คำนวณข้อมูลของร่างใหม่ตามทิศที่เลือก ผ่านฟังก์ชันเดิม
- ไม่แก้ order หรือ position ที่สร้างไปแล้ว

ตรวจและถอด dependency ให้ครบทั้ง UI, validation, readiness, position sizing และการบันทึก ไม่ใช่แค่ซ่อนข้อความเตือน
ลบโค้ดที่ใช้เฉพาะระบบ Trend เดิมเมื่อไม่มีผู้เรียกแล้ว แต่รักษาข้อมูลประวัติที่บันทึกไว้ ไม่ลบข้อมูลผู้ใช้

ขอบเขตการยกเลิกนี้หมายถึงระบบ Trend/Bias จาก Strategy เท่านั้น
กฎ Macro, Risk, SL/TP และกฎบัญชีที่ยังอยู่ในสเปกล่าสุดให้คงเดิม
ไม่เพิ่มฟังก์ชันหรือเงื่อนไขใหม่

### Part A2 — User addendum 25 Oct (verbatim, overrides Part A where it differs)
"For TF (Timeframe), use shorter text and make the column narrower—use 'D' for Daily and 'W' for Weekly. For Classify, use phrases instead. Apply colors based on the wording: for example, in an Uptrend, use Green for 'Strong',Blue for 'Normal', and Yellow for 'Uncertain'. For the opposite (Downtrend), use Red, Purple, and Yellow respectively.Setup has 3 conditions: 1. In the zone, 2. Align MA50, and 3. MMT Shift Pivot — try to make everything fit into 1 row, especially on an iPhone."

---

### Part A3 — User addendum 25 Oct, 2nd (verbatim, overrides Part A / A2 where it differs)
"1. Use the wording 'Trade Overview (ภาพหลัก)' instead of 'ประเมินเทรด', and group it together with Zone Activation so they appear inside the same frame.
2. Fix the default timeframes: set Main to Day and Tactical to 4H.
3. For Setup, change the label to 'Setup on minor'."

### Part A4 — User addendum 25 Oct, 3rd (verbatim, overrides earlier parts where it differs)
"Mandatory TP & R:R Display: Force the user to input TP (Take Profit) (make it a required field) so the system can calculate the Risk:Reward (R:R) ratio. Display the calculated R:R cleanly with a sleek, lean layout that fits seamlessly into the UI.
Mobile Single-Row Fix (iPhone): The summary status bar (▲ Up · Macro ▲ · 2% · ● OUN $630 · ● FAM $380 · ไม้ใหม่ 0/5) currently wraps into multiple lines on an iPhone screen. Optimize the spacing, font size, or padding so the entire bar fits strictly on a single row without wrapping."

---

## Part B — Orchestrator notes

### B1. Order of work (one section at a time, related suites green before the next)
1. Dependency map first (no code change): grep and list every reader/writer of Strategy Trend/Bias/Zone/Shift (B2) → write it into `tests/PF1_depmap.md` (function · what it does · keep/remove/repoint). Report it in the final report.
2. Plan form (A2–A4) with plan Trend as the single direction source.
3. Remove Strategy Trend system + repoint dependencies (A5, A8).
4. Strategy tile = Macro only + image caption + delete (A1).
5. Tests, screenshots, full run.

### B2. Known dependency hit-list (start here; not exhaustive — grep for more)
- Strategy tile / card: `ln1TileHtml` · `ln1CardHtml` · `ln1TrendOf` · `ln1Trend` · `ln1Flat` · `ln1NoTrade` (งดเทรด = `bias:'None'`) · `ln3Ask` (flip reason box) · `trend_log` / `ประวัติสลับ Trend (n)` link · `flips` · `[data-ln3-trend-empty]` hint · `+ แผน` disabled while Trend empty · Zone ▲/▼ rows + `zone_bp` B&P + Shift (`invalidation`) inputs + zone order by Trend.
- Bias writers/readers: `satwSetBias` · `satwWeek(wk, asset).bias` / `.trend_dir` · `satWeekBiasNow` · `satOffBias` / `satOffBiasMsg` / `satTradeOffBias` (SR1 "สวน Bias สัปดาห์" block + trade warning tags) · the "เตือนเดิมของ Bias" block that pushes `'สวน Trend'` (~line 16860) · carry banner text "… เช็ก Bias" (`satV3CarryBlockMsg` area) · plan-row / card status arrows that come from the Strategy bias · `ln2FormLine` (Main/Tactical status line arrow `▲ ·` comes from Strategy Trend → use the plan's Trend) · new-plan default `bias` taken from Strategy (must start empty).
- Zone: `ln3ZoneCheckHtml` · `ln3ZoneSet` · `ln3ZoneSideSet` · `ln3ZoneIdea` / `ln3ZoneTxt` / `ln3ZoneSide` / `ln3ZoneBp` (pull Zone from Strategy) · `⚠ ไม่อยู่ใน Zone`.
- Direction / sleeve: `satV2SetDir` (Long/Short buttons) · `satV2SetSleeve` (TF + setups filter on switch) · `satV2SetupToggle` + settings lists `setupsMain` / `setupsTac`.
- Today: task kind `'bias'` "Bias ยังไม่ประเมิน: …" (~line 5877) reads Strategy bias → remove.
- New-week prompt (`nwRows` / `nwState` / `nwStart`, LN3fix3): row hints `สัปดาห์ก่อน ▼` and default-tick rule use Strategy bias → see B4.
- `satWeekFreshPatch` / `satWeekFreshWrite` (LN3fix3c "+ Asset starts empty"): stop writing/clearing Trend-system fields as workflow; it may keep clearing `opinion_txt` (see B4).
- Journal/F2c snapshot fields on trades (`trend_state`, `trend_changed`, `plan_bias`, …): if they are filled from the Strategy Trend, fill from the plan Trend instead (or leave empty) — never rewrite existing trades.
- MR (7E-4, `satMrOn`, `Calc.mrSide`): "สวน Bias ของแผน" = the plan's own direction, not Strategy — keep working off the plan Trend; if `SAT_MR_ENABLED` is off, leave as is.
- **Keep (Macro rules):** "สวน Macro" (plan Trend vs Macro stance) with its required reason and the "ขนาดไม้เมื่อสวน Macro" size rule · "นอก Macro / Macro Neutral" · DD / news / Tactical brake / caps · "นอกแผน" for trades **without a plan** (only the direction-vs-Strategy part goes).

### B3. Data model (per plan doc in `satIdeas`; written only through `satV3IdeaWrite` / existing save path)
- **Trend:** no new field — the plan's existing `bias` is the Trend (`Long` ⇄ Up, `Short` ⇄ Down, empty/`Neutral`/other ⇄ "— เลือก —"). Changing Trend = write `bias` through the existing direction path (reuse `satV2SetDir` logic, extended to allow clearing) so every derived value recomputes. New plans: `bias` empty.
- **Classify (A2):** new field `classify`: `'strong' | 'normal' | 'uncertain' | ''`. Display only (no Risk/size effect). **Phrase + colour follow the plan Trend** (same in the select and on plan rows/cards): Trend Up → `Strong Up` green · `Normal Up` blue · `Uncertain` yellow; Trend Down → `Strong Down` red · `Normal Down` purple · `Uncertain` yellow; no Trend → `Strong` / `Normal` / `Uncertain` in normal text. Use existing tokens (green/red of Long/Short, the app's blue `#2B5BD7`, purple `#8a63e6`-family, amber/yellow warning colour); yellow text must stay readable on white (use the darker amber text + light amber fill as in the mockup). Changing Trend re-labels/re-colours Classify; the stored key does not change.
- **TF (A2):** existing `tf`. Options (short text) `15m` · `30m` · `1H` · `4H` · `D` · `W` in a **narrow column** (≈ 60px; ≈ 40–48px at ≤ 340px). Show aliases as selected without rewriting: `Daily`/`1D` → D, `Weekly`/`1W` → W, `4h` → 4H, `1h` → 1H. Any other old value → extra option with that text, selected. Store only when the user changes it. **Defaults (A3):** Main = `D`, Tactical = `4H` — change the settings defaults (`tfMain:'D'`, `tfTac:'4H'`, Settings › Sat fields still editable); if the user's saved Sat settings still hold the old defaults (`tfTac === '30m'`), migrate that value once to `4H` through the existing settings write (other user-changed values untouched). New plans take the default of their sleeve; switching sleeve follows the existing rule (TF still equal to the old sleeve's default → new sleeve's default).
- **Zone Activation:** new fields `zone_act` (bool) + `zone_act_txt` (string ≤ 60, free text). Old `zone_ok` / `zone_txt` / `zone_side` stay stored, untouched, not shown, not converted.
- **Setup (A2 — 3 conditions):** new field `setup_ck`: array of `'in_zone' | 'align_ma50' | 'mmt_shift_pivot'` (labels `In the zone` · `Align MA50` · `MMT Shift Pivot`), each independent, none required. Block title **`Setup on minor`** (A3). Shown as **one row of 3 toggle chips** (real checkboxes inside, keyboard/aria OK) at every width incl. 300px — see mockup: ✓ + dark fill when on; at ≤ 340px the chips shrink (font ≈ 11–11.5px, padding 3–4px, no box icon, dark fill = on). No wrap, no clipping. Old `setups` array + `setup_note` stay stored, untouched, not shown in the form, not converted. Zone Activation (Row 2) stays a separate checkbox + Zone text.
- **Idea text:** existing field stays stored; input removed from the form.
- **Sleeve switch** (`satV2SetSleeve`): must not drop `classify`, `zone_act*`, `setup_ck`, `bias`; TF: keep the existing rule (only follows the new default when the TF was still the old default/empty) — report if you think it loses a user choice.
- **"Create order" gate:** with no Trend the plan saves as draft but the account save / order creation (`บันทึก · n บัญชี` and any other path that creates a trade) is disabled with the existing disabled style + a short hint `เลือก Trend ก่อน`. No other new block.

### B4. Gaps decided by the orchestrator (report if you disagree)
- **งดเทรด** (Strategy link, `bias:'None'`) is part of the Strategy Trend/Bias system → remove from the workflow (data stays). The asset stays in the week; it simply has no plan.
- **Link row** under My opinion becomes: `คัดลอกจากสัปดาห์ก่อน` (copies opinion only) · `เอาออกจากสัปดาห์นี้`. `ประวัติสลับ Trend` and `งดเทรด` go.
- **New-week prompt** stays (keep/remove assets). Row hint = `ถือ n ไม้` / `มีแผน n` / `—` (no Strategy direction). Default ticked = every asset of last week (open-position assets locked ticked as now). Kept assets start with empty My opinion; Macro from Playbook as now.
- **"+ Asset"** keeps adding to the week; reset = empty My opinion only (Trend-system fields no longer matter).
- **Strategy image:** keep the existing storage (`w.chart` via `vwSatOpen` / `vwSatSave` / `vwSatDel`). Caption on the image `ภาพ Week with EMA50` (replaces the `W | D · date` tag; date may stay small after it). Add a visible delete button (🗑 / `ลบรูป`) on the image for the current week → existing `vwSatDel` path; confirm with the app's existing small confirm pattern if one exists, else no confirm. Deleting must not touch `opinion_txt` or any other field. TradingView link button stays.
- **Strategy keeps:** asset tab bar / tiles, week select, Risk Sat box (LN3fix3c), Macro line, `เปลี่ยนเมื่อ`, `My opinion (Trend + Macro)` — rename label to `ความคิดเห็นเรา` (A1 wording), image. Mac 2-column tiles stay.
- **Flip history data** (`trend_log`, `flips`) stays stored; not shown anywhere.
- **Journal "สถิติตาม Setup":** new plans store `setup_ck`; if Journal grouping reads plan/trade setups, include the three new labels so new trades are not lost from the stats (display only). If that needs more than a small mapping, skip and report.
- **Settings › Sat setups lists** (`setupsMain/Tac`) stay in Settings untouched (unused by the new form). Report this.

### B5. Layout, colours and labels
- **Frames (A3):** frame 1 titled **`Trade Overview (ภาพหลัก)`** contains Row 1 (TF · Trend · Classify) **and** Row 2 (Zone Activation + Zone) inside the same box; frame 2 titled **`Setup on minor`** contains the 3 chips. Use the form's existing sub-box style (as in the mockup). The word `ประเมินการเทรด` does not appear.
- Trend select + card/row status: `▲ Up` green / `▼ Down` red using the existing green/red tokens already used for Long/Short; text always present.
- Row 1 = TF (narrow) · Trend · Classify in **one row at every width** (300 included): at ≤ 340px the selects may drop the native arrow (`appearance:none`, centred text) and use 12.5px text so `▼ Down` and `Strong Down` are never clipped (measured in the mockup: fits at 300). Row 2 Zone Activation + Zone input one row (`4,230–4,250` not clipped at 300). Row 3 = 3 Setup chips one row.

### B5b. TP required + R:R (A4 · Main and Tactical · mockup ②)
- TP label gets a red `*`; placeholder `ต้องใส่` (replaces `ไม่บังคับ`). Empty TP = soft red border on the TP input.
- **One thin line right under Entry / SL / TP** (no new box): left = muted text, right = R:R pill.
  - No TP → `ใส่ TP เพื่อคำนวณ R:R` · grey pill `R:R —`.
  - TP on the wrong side → `TP อยู่ผิดฝั่ง` · red pill `R:R —`.
  - R:R below the existing minimum → `ต่ำกว่าขั้นต่ำ 1.5` · red pill `R:R 1.2`.
  - OK → `ความเสี่ยง 63 · กำไร 120` (price distance) · green pill `R:R 1.9 ✓`.
- **Use the existing ST1 functions** (`satRrCheck` / `satRrFmt` / `SAT_RR_MIN` = 1.5 — first TP vs Entry vs SL, multi-leg handling as today). No new formula, no new minimum. Live update while typing.
- Gate: the account save / order button stays disabled until Trend is chosen **and** TP passes the existing R:R check (it already blocks R:R < 1.5 / no TP / wrong side — keep that, now for **both** Main and Tactical). Hint under the button: `เลือก Trend ก่อน` or `ใส่ TP ให้ R:R ≥ 1.5 ก่อน`. Drafts still save without TP.
- Existing ST1 Activate block / 2-step exit line / `tp1R tp1Pct tp2R` settings stay as they are; if the old R:R display duplicates the new line in the same form, keep only the new line (same data).
- Plan rows / cards may show the R:R next to Entry · SL only if it already fits; not required.

### B5c. Status line one row (A4 · `ln2FormLine`)
- The form status line (`▲ Up · Macro ▲ · 2% · ● OUN $630 · ● FAM $380 · ไม้ใหม่ 0/5`, Tactical `▲ Up · 2% · … · Loss 0/5 · DD 0/10%`) must be **one line, never wrapping, never clipped**, at 300 / 320 / 375 / 390 / 430 and Mac.
- How (as in the mockup): `white-space:nowrap`; ≤ 480px: account **names hidden, colour dots + amounts kept** (`●$630 ●$380`), separators tighter, font 12.5px; ≤ 340px: 11.5px; ≤ 310px: 10.5px with smaller gaps/dots. `ไม้ใหม่` → `ใหม่` on mobile. Mac keeps names. Same content and data otherwise (no field removed).
- Different RPT per account (`OUN 2% $630 · FAM 1% $380` case) must also fit: drop names first, keep `%` per account.
- Measure in the real form (its inner width at 300 is what matters, not the mockup).

### B6. Legacy view
- Legacy (`ln1_plan_view = legacy`) uses old Strategy screens. Apply the **direction-source change everywhere** (no Strategy-bias block / warning in either view — A8 is global), but do not rebuild legacy layouts; if a legacy screen only shows Strategy Trend controls, hide those controls there too. Report what legacy now shows.

### B7. Tests (Chromium · FF_STUB_BASE = Lean)
- `phase98`:
  - Strategy tile (300 / 390 / 1440): no Trend/Flat buttons, no Zone ▲/▼, no B&P, no Shift, no trend-empty hint, no flip link, no งดเทรด · Macro line, `เปลี่ยนเมื่อ`, `ความคิดเห็นเรา` textarea, image with caption `ภาพ Week with EMA50`, delete button → `w.chart` removed, `opinion_txt` unchanged · asset tabs, week select, Risk box still there · `+ แผน` enabled with no Strategy Trend.
  - Form Main + Tactical (300 / 390 / 1440): order = sleeve → frame `Trade Overview (ภาพหลัก)` [Row1 TF · Trend · Classify + Row2 Zone Activation + Zone] → frame `Setup on minor` [In the zone · Align MA50 · MMT Shift Pivot] → Entry/SL/TP → rest · Row1, Row2, Row3 each on **one line** at 300/320/390 (same top ± 2px) and no text clipped (`▼ Down`, `Strong Down`, `MMT Shift Pivot`, `4,230–4,250`) · no Idea input, no Long/Short buttons, no old setup chips, no TF in "เพิ่มเติม", no `⚠ ไม่อยู่ใน Zone` · Trend/Classify default `— เลือก —` · TF options exactly `15m 30m 1H 4H D W`, new Main plan = `D`, new Tactical plan = `4H` (and saved `tfTac:'30m'` migrated to `4H`), `Daily` alias shows D, unknown old TF (e.g. `2H`) shown and kept.
  - Classify colours: Up → Strong green / Normal blue / Uncertain yellow; Down → Strong red / Normal purple / Uncertain yellow; phrase text `Strong Up` etc. in the select and on the plan row; switching Trend re-colours without changing `classify`.
  - Trend Up → `bias:'Long'`, Down → `'Short'`, colours green/red with text; derived values (side, risk line, status arrow) follow; switch Up→Down with no prompt, no reason box, no trend_log write.
  - No Trend → draft saves, account save / order disabled with `เลือก Trend ก่อน`; pick Trend → enabled.
  - Zone Activation and the three Setup chips are independent (ticking one never ticks another); values saved per plan; two plans don't share values; switch Main ⇄ Tactical keeps all new fields; reload keeps them.
  - Old plan fixture (bias Long, tf `D`, old setups, zone_ok/zone_txt, idea text) opens: Trend Up, Classify empty, TF Daily, new Zone/Setup empty, old fields still in the doc unchanged; an open position keeps its direction and numbers.
  - Strategy bias set to the opposite of a plan (seed `satWeek` bias `Short`, plan `Long`): no "สวน Bias / สวน Trend" text anywhere, plan is ready, size not reduced, trade not tagged off-plan · "สวน Macro" still appears when the plan Trend is against the Macro stance and still needs its reason.
  - Today: no "Bias ยังไม่ประเมิน" task · new-week prompt hints without arrows.
  - TP required + R:R (Main and Tactical, 390 + 300): no TP → grey `R:R —`, button disabled with hint · wrong-side TP → red · R:R < 1.5 → red, disabled · valid → green `R:R x.x ✓`, value equals `satRrCheck` · drafts save without TP.
  - Status line: one line (all children same top ± 1px, `scrollWidth <= clientWidth`) at 300/320/375/390/430 for Main and Tactical, incl. 2 accounts with different RPT · Mac keeps account names.
  - No console error · no horizontal overflow at 300 / 390 / 1280 / 1440.
- Screenshots `tests/screenshots/pf1-{strategy-300,strategy-390,strategy-1440,form-main-390,form-tactical-390,form-main-1440,form-tactical-1440}.png` — open and check every one.

### B8. Old tests
- Many old suites assert the removed Strategy Trend system (LN1–LN3fix3c, SR1, …). Do **not** delete cases: change them to assert the new behaviour (e.g. "Trend buttons absent", "no สวน Bias block") or, where a case only exercised removed UI, mark it in `tests/PF1_retired.md` with suite · case · old expectation · reason ("removed by PF1 A1/A8") and replace it with the nearest equivalent check of the new behaviour. Never weaken unrelated checks. Update `ไฟล์ที่ห้ามลบ.md`.
- During work: related suites (grep the B2 names in `tests/`) + p76–p96. **At the end:** full run once, one suite at a time (base + phase 1–98), keep the Mac awake (`caffeinate -i`).
- Known false failures: p3 on Sundays (re-run with another TZ) · p6 'ยกเลิก 20' on the 20th · p13 missing backup-pre-UI1.

## Report back
Dependency map (B1.1) · what changed per section · decisions in B3/B4 you followed or changed (and why) · legacy view result · old tests changed (count + file) · screenshots opened · full-run result · what could not be verified · no push, no file deletion.
