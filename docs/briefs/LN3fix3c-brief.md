# LN3fix3c — "+ Asset" starts empty · Watch full screen full width · Risk of both accounts always visible (Sat + Core) · tests 96

> User request 23 Oct. Mockups: §2 full-screen look = `docs/mockups/ln3fix3b-mockup.html` (header and cards span the window; text lines capped) · §3–4 = `docs/mockups/ln3fix3c-risk-mockup.html` (view at 300 / 390 / 1440; **user chose Sat = A, Core = C1**; "Now", B and C2 are for comparison only — do not build them; yellow notes are explanations). UI text stays Thai.
> Objective: Simple · Clear · Easy to use · Effective. **Do not change formulas / caps / blocking rules.** Never delete features. Legacy view (`ln1_plan_view = legacy`) unchanged. Mobile unchanged.
> Continue from LN3fix3b (index sha `c0619f01…`). Backups: `index.backup-pre-LN3fix3c.html` · `tests/_bk_ln3fix3c/` · do not touch core-size.js · every temp file (including your own) → `_to_delete/` · **never rm**.

## 1. "+ Asset" on Strategy (แผนเทรด Sat) = start empty (Lean)
- **Bug the user sees:** add BTC with `＋ Asset` → Trend already shows `▼ Down`. Cause: Trend is read from **this week's** satWeek doc (`satwWeek(wpWeekKey(), asset).bias`), and BTC still had `bias: 'Short'` saved earlier this week (added before, then removed). `waPick()` → `satWeekPickAdd()` never clears it.
- **Fix:** whenever an asset is added to the current week through `＋ Asset` (`waPick`, including re-adding a parked asset from "ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้", and including an asset that was removed earlier this week), reset its current-week fields — same as a kept asset at the start of a new week:
  - `bias: null`, `trend_dir: null` (Trend = nothing chosen, incl. Flat / งดเทรด) · `zone_up: ''` · `zone_dn: ''` · `zone_bp: false` · `invalidation: null` (Shift) · `opinion_txt: ''` · old `support/resistance: []` · `updated_at` now.
  - **Keep:** `trend_log` (history stays visible in `ประวัติสลับ Trend (n)`), chart link/image, Macro (from Playbook), plans and trades (they store their own data).
  - Write it unconditionally (merge write — do not depend on the doc being in memory). Put the field list in **one shared helper** used by both `nwStart()` and `+ Asset`, so the two never drift.
- After the reset the existing LN3fix3 rules apply: amber hint `ยังไม่เลือก Trend · สัปดาห์ก่อน ▼ Down` (or `ยังไม่เลือก Trend`), `+ แผน` disabled until a pick, **first pick needs no reason and is not a flip**.
- `คัดลอกจากสัปดาห์ก่อน` still works as before.
- An asset that is already picked this week (no add happens) is **not** reset. Only an actual add resets.

## 2. Watch full screen — use the full width (Mac ≥1024 · Lean)
- Now the whole expanded detail is capped at `max-width:104ch` → at 1440 it is ≈925px, about the same as the normal detail column (≈890px). The user wants the extra width.
- Change: in `body.wl-full`, the header panel (`.wlDPanel`), cards / blocks in `.wlDBody` and tables span the **full window width** minus the side padding (`clamp(16px,3vw,48px)` as now) — remove the 104ch cap.
- **Keep text readable:** running text (`dd, li, p, .dr>span` etc.) stays max **80ch** per line; label/value rows (e.g. ธุรกิจ / Thesis / ความเสี่ยง) keep the label column, value text capped at 80ch. Wide tables and long strings still scroll sideways inside their own box; page horizontal overflow = 0.
- Normal (not expanded) view unchanged.

## 3. Sat plan — Risk Sat of every account visible at once (Lean · mockup A)
- **Now:** the `บัญชีหลัก | Family` switch (`ln2HeaderHtml`, `[data-ln2-accsw]`) shows one account's Risk Sat; the user taps every time to see the other.
- **New:** remove that switch from the Lean Strategy header. One `Risk Sat (ถ้าโดน SL ทุกไม้)` box with **one row per account** (`sat7dAccts()` order, account dot + short name as in the app):
  - `$used / $cap` · `เหลือ $left` (right-aligned) · bar (Main blue / Tactical purple, same widths as today) · line `Main $x · Tac $y` + `DD a/b%` link (still opens `ddSheetOpen(acc,'sat')`).
  - Alerts from `ln2Alerts()` sit **under their own account's row**, prefixed by nothing extra (the row already names the account). `over` styling per row.
  - Account without Sat money set up → its row says `ยังไม่ได้ตั้งเงิน Sat — ตั้งค่า` (link to Settings › Sat) instead of numbers.
  - One fold `รายละเอียดและกฎบัญชี` (same `ln2DetOpen` memory) listing each account's existing detail text under its name.
- **Mac ≥1000px:** one mini box per account **side by side** (2 columns; 3+ accounts wrap), title `● OUN · Risk Sat`, layout as in mockup A-Mac; the shared fold below them.
- **iPhone 300 / 320 / 390:** rows as in mockup A; nothing clipped (`$1,614`, `เหลือ $1,614` stay on the row's first line at 300 — tighten font to 12.5px on ≤340px if needed), no horizontal overflow.
- One account only → a single row/box, no switch (same as today minus the switch).
- **Plan form status line** (`ln2FormLine`, e.g. `▲ · Macro ▼ · 2% $630 · ไม้ใหม่ 1/5`) used the switched account. Now it shows the per-trade $ for each account compactly: `2% · OUN $630 · FAM $380` (dots instead of names allowed at ≤340px); every other part unchanged. Do not change any formula.
- Legacy view unchanged. `localStorage` key of the old switch may stay (unused in Lean).

## 4. Core plan — Risk Core of every account visible at once (Lean · mockup C1)
- **Now:** `lfCoreBoxHtml` switch (`[data-lf-accsw]`, `lfCoreSetAcc`) picks the account for **both** the Risk Core box and the stock card list.
- **New:**
  - `Risk Core (ถ้าโดน Stop ทุกตัว · ชั้น 2)` box shows **one row per account** (`lfCoreAccts()`): `x% / lim%` · `ว่าง ฿free` (right) · bar (now + reserved, account colour) · line `DD a% · FF n%` + `n ตัว`. Alerts (missing price, FF, DD, over-committed, L2 near/over cap, price status) under their own account's row. Account with no Core tank → its row says `ยังไม่ได้ตั้งถัง Core — ตั้งค่า › Core`.
  - One fold `รายละเอียดและกฎ` (same `lfDetOpen`) listing each account's existing detail lines under its name.
  - **The switch moves down**, directly above the stock card list, and only chooses the cards: labels `● OUN · n ตัว` / `● FAM · n ตัว` (n = cards that list would show). Remembered as today.
  - Header line `Core · ทุน …` shows the total of all accounts (or keep per account inside rows — your call, keep it short).
- **Mac ≥1000px:** risk boxes side by side (like §3); switch + cards below as today.
- **iPhone 300 / 320 / 390:** no clipping, no horizontal overflow.
- Legacy view unchanged. No formula / cap / gate change.

## Tests (Chromium · FF_STUB_BASE = Lean)
- `phase96`:
  - + Asset: seed this week's BTC doc with `bias:'Short'`, `trend_dir:'down'`, zones, Shift, opinion, `zone_bp:true` and 2 `trend_log` entries, BTC **not** picked → `waPick('BTCUSD')` → no Trend button `.on`, amber hint shown, `+ แผน` disabled, Zone/Shift/opinion empty, B&P unticked, `ประวัติสลับ Trend (2)` still 2 · seeded with `__seedDoc` (no listener notify) → still reset (run 3× in a loop) · first pick → no reason box, no new trend_log entry · second (opposite) pick → reason box (existing rule) · re-add from the parked list → reset too · an asset already picked (no add) keeps its values · new-week start still clears as in phase93 (shared helper) · 300 / 390 / 1440 no overflow · legacy unchanged.
  - Watch full screen 1280 + 1440: `.wlDPanel` width ≥ viewport − 2×48px − 2px · a card in `.wlDBody` same · a paragraph line ≤ 80ch (measure: width ≤ 80 × `ch` of its font, ±2%) · wide table scrolls inside its box · page overflow 0 · normal view widths unchanged vs LN3fix3b (±2px).
  - Risk Sat (2 accounts, one near cap): no `[data-ln2-accsw]` in Lean · 2 rows (iPhone) / 2 side-by-side boxes (1280, 1440: same top, both visible without scrolling) · each row's used/cap/left/Main/Tac/DD equal the values the old per-account box showed for that account (compute via the existing functions) · near-cap alert under the right account · DD link opens that account's sheet · fold lists both accounts · account without Sat money shows the set-up hint · 1 account → 1 row, no switch · plan form line shows both accounts' $ · 300/320/390: `$1,614` and `เหลือ` not clipped, same line, no overflow · legacy still has the switch.
  - Risk Core (2 accounts): rows for both with values equal to the old per-account box · alerts under the right account · switch sits right above the card list with `n ตัว` matching the cards shown · switching changes cards only (risk rows unchanged) · Mac side by side · 300/390 no overflow · legacy unchanged.
  - No console error.
- Screenshots `tests/screenshots/ln3fix3c-{addasset-390,addasset-1440,watch-fullscreen-1440,watch-fullscreen-1280,risksat-300,risksat-390,risksat-1440,riskcore-390,riskcore-1440}.png` — **open and check every one**.

### Old tests
- Never delete or weaken cases; only update expected values this brief changes (log in `tests/LN3fix3c_retired.md`, e.g. phase95 full-screen width ≤ 104ch if it checks that; old suites that click `[data-ln2-acc]` / `[data-lf-acc]` in Lean: Sat ones now read the right row; Core ones use the moved switch). Update `ไฟล์ที่ห้ามลบ.md`.
- During work: related suites (p93 · p95 · p76–p82 · p86 · p90 · p92 · Watch p85 · every suite that uses `data-ln2-acc`, `data-lf-acc`, `ln2SetAcc`, `lfCoreSetAcc` — grep for them). **At the end:** full run once, one suite at a time (base + phase 1–96). Keep the Mac awake during the run (e.g. `caffeinate -i`) — the last run was cut off by sleep.
- Known false failures: p3 on Sundays (re-run with another TZ) · p6 'ยกเลิก 20' on the 20th · p13 missing backup-pre-UI1 — do not edit tests/index for these.

## Report back
What was done per section · your own interpretations · old tests changed · screenshots opened · full-run result · no push, no file deletion.
