# LN4 — Lean Today + Lean Watch + execution aids (2026-11-09)
Branch claude/ln4 from origin/main. Mockups (docs/briefs/): **forms-half.html** (plan forms, §4 — final), **ln4-tabs.html** (Plan list/Journal/Port/Settings for §8 — its plan *form* is superseded by form-ab), **today-v5.html** (Today, final, incl. decision table at the bottom), **lean-mockup.html** (Watch part only, right side). Goal (SRTp): Today/Watch lean and simple; help SRTp take trades again (less hesitation). Principle: **show only what needs action; normal = hidden; details one tap away. Nothing is deleted — only moved/collapsed.**

Decisions: Starter ¼ **ON by default** (Settings toggle to turn default off). "Missed" uses the **Plan's Entry** as trigger (only stocks with a plan are checked). Core rows tagged **MMT / COMP**.

## 0. Audit (in report; build without waiting)
- Current Today Lean builder (tdHtmlLean, td3*/td4*/ps1TodayLine, SK1 skills line, news line, td3NewsHtml key events, goals, regime verdict, pool lines) → map each existing block to its new place (table in report). Nothing may silently disappear.
- Plan data: draft/open states, Sat plans, how to add `order_working` + fill; where Core/Sat checks (min stop, risk range, caps) are computed today (reuse — no new rule logic).
- Watch Candidates/Watchlist row builders from TV1/TV1b (groups, tags, 14-day Drop?).

## 1. Today · status card (one card)
- Line 1: Regime pill · `Risk x / 5% · room yR this week` (week loss limit 5R − realised this week) · port status pill **only when not Normal** (e.g. `Momentum Half`, `Momentum ½ (regime)`) · Daily|Weekend switch on the right.
- `HOT` line: all HOT sectors from Flow (Leading amber ↗ / Fresh blue), max 5 then `+N`; tap → Flow › Leadership.
- `MACRO` line: current Playbook one-liner + `Playbook ›`. `GOAL` line: existing goals one-liner + small bar.
- `TODAY` line: today's HIGH key events (existing td3 news model): time ICT · name · linked assets; < 4h = amber with "in 3h 12m"; past = faded. Hidden when none.
- `To do` row (replaces separate Homework row + SK1 Skills due line + EX Missed prompts): max 3 chips by urgency (red overdue → amber due today → grey), `+N` opens the rest; right side `Exec x/y` badge. Hidden when nothing to do.
- iPhone (≤560px): MACRO + GOAL behind `More ▾ macro · goal` (one tap); everything else visible.

## 2. Today · Act (Daily)
- One card "Act · Core + Sat". Groups `CORE` (MMT rows first, then COMP) and `SAT`. One line per plan/position (iPhone: 2 lines, no extra rows).
- Row: ticker · `MMT`/`COMP` tag (turns amber `MMT ½` when that port is Half / regime half) · sector tag (`HOT Semis` amber / cold grey; Sat = `SAT`) · grey details (`Buy Stop 182.50 · ¼ size`, Sat timeframe + news warning) · status · one button.
- States: **Draft** → `Place order ›` · **Order working** (blue, new) → `Record fill` · **Filled/Open** → `Raise stop ›` when stop < avg entry, else no button.
- Readiness checks (reuse existing rules): Setup ✓ present (Core) · stop set & ≥ min stop · risk within range/caps. All pass → green `Place order ›`. First failing check → red reason replaces "Draft" (e.g. `Risk 0.30% > 0.25%`) + amber button `Setup ✓ ›` / `Set stop ›` / `Fix risk ›` that opens the Plan form at that field. **No extra check row.**
- `Place order ›` = confirm "Placed at broker" → status Order working (stores time). `Record fill` → existing Buy record flow (pre-filled).
- Act header right: confidence ladder badge `Stage 1 · ¼ size · 6/10 ›` (§5).
- Empty → "Nothing to act on — see Find ↓".

## 3. Today · Find (Daily)
- 3 counters (Deep dive x/2 · Cand → WL x/3 · New Cand x/3 ✓) — tap one → its list opens below (rows with sector tag, HOT first; actions as today: Deep dive › / Pass / Drop / ticker input + Add). One open at a time.
- Weekly News line (unchanged WK1 look + Read ›) below, only when unread.
- Removed from Daily view (moved, not deleted): Overview panel → its content is now in the status card lines; anything else found in §0 goes to its tab or behind a tap — list it in the report.

## 4. Plan forms — FINAL (SRTp): Core = **Form B** (PS1c rows), Sat = **current structure + Starter**. Both must fit the right-half column (~420px) next to the left macro/strategy half. Mockup: docs/briefs/forms-half.html (supersedes form-ab.html and the form in ln4-tabs.html)
### 4a. Core (Momentum / Compounder) — PS1c form as it is today + Starter
- Keep: header (New plan · % note · Momentum|Compounder · ×), บัญชี + Ticker, Risk per idea + regime/status pill, Entry · split and SL · out rows with ＋ / ✕, summary, port % line, Details, ยกเลิก / บันทึกแผน, per-port drafts, all maths.
- Add one Starter ¼ switch row above Risk per idea. ON → Entry row 1 split 25% (normal price), auto row 2 split 75% labelled "Add-on · stop ≥ BE" (price optional); user can still edit splits / add rows. OFF → single row 100% as today.
- Summary: `Now: … (risk now)` + `Planned total: …` (2nd line only when Starter ON).
### 4b. Sat — today's form, same blocks and order, + Starter
- Keep exactly: title + Main tag + ×, Main | Tactical, macro/default-risk line, **Trade Overview** — row 1: **TF · Trend · Verify (EMA50 / Structure checkboxes stacked) on ONE row, Verify right after Trend like the old layout**; row 2: Zone (existing rules: EMA50 ✗ → 60% size, Structure required; CS1 Tactical lock). **Setup on minor on ONE row**: label + 3 compact chips, renamed and reordered (§4d), Entry ＋ / SL / TP*, R:R line, per-account rows (OUN / FAM sizing, "Can't size → Set ›", ข้าม), "Macro & ขนาดไม้" fold, บันทึก · N บัญชี.
- Add: one compact line of check pills under Entry/SL/TP (Structure · EMA50 · Setup n/3 · R:R · Stop ≥ min · Risk) — the first red one is the reason Today shows with `Fix … ›`; and the Starter ¼ switch above the account rows (account rows then show the "now" size).
- Phone 390: same order, wraps.
### 4c. Settings — Starter can be switched off completely
- **"Starter ¼ feature" On/Off** (default On). Off = the Starter switch is removed from BOTH Core and Sat forms, no auto add-on row, no "¼ size" labels in Today/Plan/Port/Journal, no confidence-ladder badge. **Manual scale-in/out stays**: ＋ Entry / split %, ＋ SL / out %, Sat Entry ＋ / Entry 2 all work as today. Exec score + Missed stay.
- "Starter on by default" (only when feature On). Ladder stage (only when feature On).

### 4d. Sat rules change (SRTp 2026-11-09) — Verify matrix, counter trend, Setup rename
- Verify matrix (same for Trend Up and Trend Down):
  | EMA50 | Structure | Result |
  |---|---|---|
  | ✓ | ✓ | Normal · 100% size |
  | ✗ | ✓ | Allowed · 60% size (existing rule) |
  | ✓ | ✗ | **Counter trend** · allowed after confirmation · **60% of full size** |
  | ✗ | ✗ | **Blocked**: red pill "Need EMA50 or Structure verify", Save disabled (Today Act: `Verify ›`) |
- Counter-trend confirmation: when Save is pressed (all fields filled incl. TP), show a small confirm sheet: "Counter trend — Trend <Up/Down> but Structure not verified. Suits high-volatility markets (more room). Size = 60% of full." Buttons `Save as counter trend` / `Back`. Store `counter_trend:true` on the plan.
- Show a `Counter` tag on that plan everywhere (Sat form header, Today Act row, Plan list, Journal + Journal filter chip "Counter trend"). Check-pill row shows `Counter · 60%` (amber) instead of the red Structure pill.
- Size factor order: full × 60% (counter trend or EMA50 ✗; never stacked 36%) × other existing non-macro factors × Starter ¼ (if on).
- **Macro no longer cuts Sat size (SRTp 2026-11-09): warning only.** Remove the macro factor from Sat sizing (satMacroFactors mr / F.rule.factor macro cut → treated as 1.0; report every place it was applied). When the Playbook stance for the asset is against the plan's Trend (or 'flat/none'), show an amber pill `Macro against ▼` / `No Playbook` in the check-pill row and on the Today Act row — never blocks Save. "Macro & ขนาดไม้" fold stays (stance text, Driver chips, per-account size); its size text reads `เต็ม (macro = warning only)`.
- Setup on minor — rename, keep stored keys, new order: **1 In Zone** (in_zone) · **2 MMT Neutral** (was "MMT Shift Pivot", key mmt_shift_pivot) · **3 Pivot align MA** (was "MA Align Overlap", key align_ma50). Old ticks carry over.
- Small `✓ all` button at the END of the Setup row, deliberately a little hard to use: tiny (text-size link, ~24px hit area, faint grey) and needs **press-and-hold ~0.8 s** (a fill bar shows progress; a normal click does nothing except a tooltip "Hold to tick all 3"). Releasing early cancels. Keyboard: focus + hold Enter/Space 0.8 s. When all 3 are already ticked it's hidden.
- **All 3 Setup chips must be ticked before Save** (SRTp confirmed: "3 should be checked"); otherwise pill `Setup n/3` red + Save disabled, Today Act button `Setup ›`. CS1 Tactical lock unchanged.
- Tests: the 4 matrix rows × Up/Down; confirm sheet appears only for EMA50 ✓ Structure ✗ and only at Save; Back keeps the form; Counter tag shows in Today/Plan/Journal; sizes 100/60/60/blocked; no 36%; macro against → warning pill only, size unchanged; Setup 2/3 blocks, 3/3 allows; ✓ all needs a 0.8 s hold (click does nothing, early release cancels), hidden at 3/3; renamed labels with old data.

## 5. Execution score + Missed + confidence ladder
- Valid setup = a plan reached Order working, OR a plan whose Entry was crossed (latest price) while still Draft. Taken = filled. Missed = Entry crossed while Draft/no position → To do chip `ETN trigger passed · Missed?` (one tap records Missed; dismiss option "Not valid anymore" doesn't count).
- `Exec x/y` = taken / valid this ISO week (Mon–Sun ICT). Tap → toast with goal ≥ 80%.
- Missed stored for Journal (filter "Missed"). No P&L in this score.
- Ladder: Stage 1 = ¼ (Starter default), Stage 2 = ½, Stage 3 = full. Move up suggestion when ≥ 8 of last 10 valid setups taken; never automatic (one tap "Move to Stage 2"). Stage sets Starter fraction.

## 6. Weekend view
- Unchanged WK1 list, inside the same page under the status card.

## 7. Lean Watch (Candidates + Watchlist)
- Header: tabs (Ideas · Candidates n · Watchlist n) + small icon buttons `+` (Add) and `TV n` (TradingView menu from TV1). Market filter = one `All ▾` dropdown (All/US/TH).
- Groups unchanged (TV1 Option 1: HOT · <Sector> / Other; Watchlist Setup ✓ first).
- Row: ticker · **one** tag (reason/source or sector) · age; amber `set reason` when none. Actions (Pass / Drop / Thesis on Candidates; Setup ✓ / Thesis on Watchlist) appear when the row is tapped (one row open at a time).
- 14-day rule: ⚠ next to the age instead of the banner; tap ⚠ → Drop / Keep 7 more days.

## 8. Other tabs that must follow the 6 functions (same data, no second source of truth)
- **Plan tab**
  - Plan form (Core + Sat): Starter ¼ switch + planned add-on line (§4); risk/stop/Setup checks show the same reason text as Today; `Fix risk ›`/`Set stop ›` from Today opens this form with that field focused.
  - Plan cards/list: same states as Today Act — Draft · **Order working** (blue, `Record fill` / `Cancel order`) · Filled/Open · `Add-on ›` when stop ≥ break-even. Same MMT/COMP tag (+ `½` when Half).
- **Journal tab**
  - Filter chips: All · Taken · **Missed** · Starter vs Full size.
  - Small weekly row: `Week 45 · Exec 2/3 · Stage 1` (history of Exec score + ladder stage per ISO week).
  - Each trade shows `¼ starter` / `+ add-on` / `full` so later the Feedback loop report can compare.
- **Port tab**
  - Open positions show `¼ starter · add-on planned` and `stop below avg entry` badge (same rule as `Raise stop ›`).
  - Risk summary shows `room yR this week` (same number as Today).
- **Settings**
  - Starter default ON/OFF; current ladder Stage (manual change allowed) + rule text "move up at 8/10"; week loss limit in R (existing 5R) used for "room".
- **Watch**: no new functions (Setup ✓ already there). **Flow**: no change.
- Tests: Plan/Journal/Port/Settings show the same values as Today for the same fixture (state, Exec, Stage, room, Starter).

## Tests
- Status card: port pill only when abnormal; HOT max 5 + N; TODAY hidden with no events, amber < 4h; To do merges homework/skills/missed (max 3 + N, order); iPhone More toggle.
- Act: MMT before COMP; MMT ½ when Half; one line per row at 1440; 2 lines at 390 (no third row); state flow Draft → Order working → Filled; each failing check → right reason + right button opening the right field; Raise stop / Add-on conditions.
- Starter: default ON, risk ¼, add-on stored; Settings default OFF respected.
- Exec/Missed: crossing Entry while Draft → Missed chip; tap records; week boundary ICT; ladder suggestion at 8/10, manual only.
- Find: counters, one list open, actions work; news line rule.
- Watch: header icons, one tag per row, actions on tap, ⚠ flow.
- §0 mapping table: every old Today block accounted for.
- 390 + 1440 screenshots. Update old Today/Watch tests → tests/LN4_retired.md. Commit, push, compare URL. Don't merge.
