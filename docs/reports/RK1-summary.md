# RK1 — Risk per idea in Settings + hide unused settings

Branch `claude/rk1` (from fresh origin/main). Not merged.

## What changed
**Engine (`risk-engine.js`, copied into `index.html` by `tools/sync_re1.py`)**
- New `POLICY` defaults: Compounder pilot 0.50 · total 1.00 (was 1.25) · Momentum 0.40 (was 0.45) · Sat fixed 0.20 on every step (was 0.20/0.30/0.30/0.40). Weekly = 4 × per-idea (Momentum 1.60, Sat 0.80), monthly = 4 × weekly (6.40 / 3.20). `ammo` 4, 6-loss Compounder lock, Sat lock after the 4th loss, regime, emergency, heat 6 %, value cap 12.5 %, homework cap, min stops: unchanged. The Active 3 % / 12 % summary check was not in the brief and is unchanged.
- New `RiskEngine.RISK_DEFAULTS / RISK_BOUNDS / riskValidate / applyRisk / riskDerived`. `applyRisk(null)` = defaults; invalid values change nothing. Compounder add-on size (`addonPct`) follows the first-entry value (it was 0.50 = the first entry).

**Settings › Portfolio & Risk › "Risk per idea"** (top of the section; replaces "risk limits now come from the engine"): Compounder total + First entry · Momentum · Sat; 2-decimal inputs, bounds 0.50–1.50 (first ≤ total) · 0.20–0.60 · 0.10–0.40 with inline message and Save off; Reset → 1.00 / 0.50 / 0.40 / 0.20; muted derived box. Stored once in the shared settings (`settings.shared.riskPerIdea`, no new collection), written only when a field changed. `rk1Sync()` (called from `shStore()` and `re1L()`) applies it to the engine; it only reads, never creates the shared store.
- Views reading the values: plan forms (Momentum / Compounder / Sat sizing), Plan board, Today (risk room, chips), Port block, drawer, New-plan popup subtitles (`BD_NEW` → `bdNew()`, read at render). Sat labels "Step 2 · 0.30 %" / "SAT step n" are now just the value (the weekly-lock message stays; the step machine still runs, every step = the Sat value).
- Saved plans / holdings are never rewritten: only sizing of new plans and edits reads the values. A saved plan above today's size is gated by the existing "Above today's size — allowed now n (plan has m)" rule, it is not resized.

## Hidden settings (UI only, stored data kept; one switch `RK1_HIDE`)
| Setting | Readers that used it → what they do now |
|---|---|
| Daily routine (time slots, Sat daily check XAU/BTC/S50/Brent) | `tdRoutine()` returns empty slots / satDaily (raw=true still returns the stored data for the Settings editor) → `tdBuild` guards `satplan` / `satdaily` skip; `tdSlotHtml` / `tdFocusHtml` / `td3OtherBody` timeline + focus get nothing (`td3OtherBody` is dev-only and now returns ''). The editor `#tdRtSet` is hidden; the section is renamed "Reminders" and keeps the Enable-reminders button. |
| Other daily tasks (`dailyExtra`), Weekly tasks (`weekTasks`) | `glExtraList()` / `glWeekTasks()` return [] unless raw → `glDayStat`, `glWeekStat`, `ln3TdWeekCount` (routine % and week counts) now count nothing; settings editor reads raw. The fixed WK1 weekend list is not from these settings and stays. TD5 own to-dos untouched. |
| Sub-port goals (`subGoals`) | `glSetRender` no longer inserts `glSubHtml` (the per-sub-port fields); Today goals card (`td3GoalsHtml`) no longer renders the "Sub-port goals" block. Main account goal unchanged. `td3SubOf` / `glSubSave` remain, unused. |
| Key news days (`newsEvents`) | `newsEvents()` now derives from Weekly Impact (`wiDocs`): confirmed time, not cancelled, HIGH-impact CPI / NFP / FOMC (title/metric match). Readers get the new source with no change: `newsSatBlock`, `newsWarnLine`, `newsSizePctNow`, `newsSatBlockMsg` (Sat window warn + size cut), `re2Events` / `re2EvData` (Today events + window chip), `lr4Events`, Today `ln4NewsLine` and pre-news checklist, week calendar. No Weekly Impact doc for the week → no window, and the Sat plan form (`pb2Refresh`) shows a muted "No news calendar this week". The section `#newsSetSec` is hidden. |
| Sat rules › Advanced › Tactical TP1 / TP2 | Block hidden (`satV2` values stay and are still read by `satV2Cfg`). The now-empty "Sat rules" card keeps one row "Min stop per asset ›" that opens Portfolio & Risk (as in the mockup). |

## Tests
- Engine selftest `node tests/risk_engine_test.js` 410/410 (new RK1 block: defaults, derived limits, Momentum 4th losing idea blocks with count and 1.60 % budget agreeing, Sat lock after 4 losses at 0.20 / 0.80 %, every Sat step 0.20, Compounder 6-loss lock, old plan unchanged, override via settings, bounds, Reset).
- `tests/run_tests_rk1.py` (new; added to `run_regression.sh`): section render, bounds, Reset, save → shared settings + engine, sizing at 1440/390/360, no 0.45 / "Step n ·" / "SAT step" in Today · Plan board · Port · Settings, hidden sections, stored data byte-for-byte after a save, Today without routine items, news window from a Weekly Impact CPI event and none without, "No news calendar this week", main goal shown, no overflow, saved trades untouched.
- Updated existing tests that asserted 0.45 / 1.25 / the Sat ladder (or the hidden settings):
  - `risk_engine_test.js` (G2, G3, G6, G7, B blocks → 0.40 / 1.00 / Sat 0.20 / caps 1.60 and 0.80)
  - `rm1_engine_test.js` (total cap 1.00, Momentum 0.40)
  - `re1_adapter_test.js` (Momentum 0.40, Sat 0.2 × 65 %)
  - `re1c_live_test.js` (Momentum 0.16 / 0.32, total room 0.8 %, Sat label is the value)
  - `run_tests_re1c.py` (formula strings, Sat box text)
  - `re1d_common.py` / `run_tests_re1c2.py` (fixture plan qty 40 → 36 so saved plans stay inside the new size; re1c2 news checks now seed Weekly Impact instead of `settings.newsEvents`)
  - `run_tests_clean1.py` and `run_tests_lrf2.py` (SAT line "0.2% · x/y%" instead of "step n")
  - `run_tests_phase373.py` (popup subtitle 0.40 %)
  - `run_tests_phase51.py`: retired from the regression list because RK1 hides the Key-news-days form it fills; the news window is covered by `run_tests_rk1.py`. The file stays in `tests/` because `lib_phase54/100/106` import it as a helper (noted in `_retired/README.md`).
- Side-by-side vs the mockup: `tests/screenshots/rk1/side-1440.png`, `side-390.png` (`tests/rk1_side.py`).

## Notes / judgement calls
- The live Today (LR2/LN4) never rendered the routine slots; the hidden readers are mostly the legacy `tdBuild` / `td3OtherBody` paths. Today's visible items were already independent of them, so the visible change on Today is small.
- Out-of-bounds values are blocked by disabling Save with an inline message (existing Settings pattern).

## RK1-fix
Rebased onto origin/main (HW1d, #90); `run_tests_rk1` appended to main's REST list. Risk-per-idea inputs restyled to match the mockup (rounded inputs, "%" inside, disabled grey "—" cells). Last full `JOBS=2` run: 79/80, the one failure being `run_tests_phase51` (now dropped from the list as above); no further full run after dropping it.
