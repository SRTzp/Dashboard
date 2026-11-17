# EF1 — Entry friction: fewer steps from plan to placed order

Approved by SRTp 17 Nov 2026. Goal of the dashboard: **reduce friction to enter trades** (the problem is getting in, not FOMO). Priority order set by SRTp: trust the numbers (RM1) → fewer steps (EF1) → clear blocks (PV1b) → confidence at entry (later).
Base: latest `origin/main` **after PV1b and RM1 are merged**. Branch: `claude/ef1`. Commits: A0 map → A admin blocks → B Ready + verify + news → C 2-tap Place → D tests/report, push each.
No new mockup: reuse the existing place-confirm sheet and PV1b cards; remove steps, don't add screens.

## Rules
- **Keep every money-protecting block unchanged:** stop missing / below min stop, size / lot, heat, total risk, value cap, emergency brake, engine gates. Their texts and buttons stay as PV1b made them.
- Change only admin / process steps listed below. No data migration, no deletes (existing flags / fields stay stored, just not required). `render()` pure. English UI. No overflow 1440 / 1280 / 390.
- Lean UI rules (RM1 §UI rules) apply: no new panels; each screen same length or shorter (report row counts at 390).

## A0 · Map first → `docs/reports/EF1-progress.md`
Count taps and screens from app open to a placed order today, for: Satellite main plan, Satellite carried plan, Momentum plan, Compounder pilot. List every gate on the path with its code (`carryBlock`, `unpickBlock`, `noteBlock`, `newsBlock`, verify / MSS pending, manual Ready, confirm sheet). Target after EF1: **≤ 3 taps** (open card → Place › → Confirm).

## A · Admin blocks → automatic
1. **Carry-over:** a plan carried from last week stays valid in the new week (no "Use this week" step), whether edited or not. Remove `carryBlock` from `ready`; keep the carried marker as a small grey note in More only.
2. **Not picked this week:** saving or placing a valid plan auto-adds its asset to this week's picks (`satWeekPickList`). If the pick list is full (`SAT_WEEK_PICK_MAX` = 3) → the card's Place opens a one-line "Replace <asset> in this week's picks?" choice inside the existing confirm sheet, not a block.
3. **Against Macro:** `noteBlock` becomes a warning: amber "Against Macro" chip on the card; the reason field stays in the form, optional. Never blocks Place.

## B · Ready, verify, news
4. **Ready = automatic:** a plan with no blocking item is Ready. Remove the manual ⚑ toggle from cards and Today; Today › Enter lists plans that are Ready by this rule. Stored `ready` flags are ignored, not deleted.
5. **EMA50 + Structure verify inside the plan form (Satellite only)** (`ema50_ok`, `structure_ok`; MSS `mss` is asked only when Structure = No — `ln4VerifyOf`): answered once as part of the form (existing controls), saved with the plan. Remove the separate pending step and its Today item; rename the old labels "needs Trend" / "needs MSS answer" to "Needs EMA50 + Structure" / "Needs MSS (Structure = No)" wherever they remain. Rules unchanged: Structure = No with MSS = Yes → allowed at reduced size (Counter trend / Reversal @ MSS); MSS = No or blank → still blocks.
6. **News window = warning + automatic size cut, never a block** (decided 17 Nov 14:01; replaces "no new Sat entries in the CPI/NFP window"). Inside the window (same window definition, `newsSatBlock`): the plan stays placeable; size is cut to **65%** (policy setting `newsSizePct`, default 65 = the existing reduced-condition size, editable in Settings); amber line on the card and in the confirm sheet: `News window until 20:00 ICT · size 65%`. **Satellite only.** Combine with the other Satellite reduction (Unclear Trend / MSS 65%) by **min()**, never multiplied → 65%. Regime does not apply to Satellite; Momentum and Compounder use only the RM1 regime modifier (no news or trend cut). After the window, full size returns automatically with no tap. Open-position news protocol (cancel limits, stop to entry) unchanged.

## C · 2-tap Place
7. Card `Place ›` opens the existing confirm sheet directly (no intermediate step / popup). Sheet shows, per entry leg: side, price, quantity, order type, plus stop and targets; Risk and Reward totals; the RM1 "limited by …" line. One `Confirm` button records the order as today. Size working ("qty = risk ÷ (entry − stop) × FX") under More in the sheet.
8. Same path from Today › Enter.

## Tests / proof
- `tests/run_tests_ef1.py`: carried plan placeable with no extra tap; unpicked asset auto-added; full pick list → replace choice in sheet; against-Macro plan placeable with amber chip; Ready appears automatically and disappears when a block appears; verify answered in form, no pending step; inside the news window the plan is placeable at 65% with the amber line, full size after the window (fake clock), min() with Unclear Trend 65% → 65%; a Momentum / Compounder plan is unaffected by the news window; card → Place → Confirm = 2 taps after opening; every money-protecting block still blocks (stop, size, heat, total risk, value cap, emergency 0%).
- Tap count before / after in the report (A0 table). Row counts at 390 for Today and Plan board.
- Update existing tests only where they assert a removed step (list each). `tests/run_regression.sh` not worse than base.
- Screenshots (`git add -f`): `ef1-card-ready-1440`, `ef1-confirm-390`, `ef1-today-390`, `ef1-news-window-1440`.

## Report — `docs/reports/EF1-summary.md`
Tap counts before / after per plan type · each removed / softened gate and what replaced it · gates kept · tests changed and why · open questions.
