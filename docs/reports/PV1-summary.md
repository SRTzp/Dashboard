# PV1 — honest position numbers · Flow asset panel · Planned / Holding cards

Branch `claude/pv1` (not merged). Commits: brief · A0 notes · Part A · Part B · Part C · fixes.

## Root causes (confirmed, with the A0 reconciliation)
Stored NVDA card (user-pasted): lots = 11 @158; `plan.ps1.rows` = 11 @158 + 18 @140; qty 29; FX 33.76; E 5,019,200; `riskMoney` 36,055.68; price 162.85 (13 Nov).
- Today row `#29 · ฿36.1k · 0.72%` = `tw1SizeRisk` → `plan.ps1`: whole-plan shares (11+18), whole-plan loss at stop (11×48 + 18×30) × 33.76 = 36,055.68 = 0.7184% of 5,019,200. Not holdings, not value. Brief's reading confirmed (FX is 33.76, price 162.85 rather than the brief's rounded 33.8 / 162.80).
- `cap 50%` = WL1 homework limit; it scaled nothing.
- "Fix risk ›": `td3PlanStatus` returned `incomplete` with an empty list when sizing failed; the reason lived in `pb2Calc(i).msg` / `reasonTexts` and was dropped.
- ⚑ Ready is a manual flag independent of validity. Flow cards were stretched by the grid and the reason text was clamped + muted.

## What changed
**A** `pos-view.js` (pure `PosView.calc`, synced into index.html, `--check` in regression) + `posView(it)` adapter; Today row `#11/#29 · ฿60.5k · 1.2% · open risk ฿17.8k` (Sat `0.02/0.05 lot`), planned/ordered `plan #29 · risk ฿36.1k · 0.72%`; no price → `value: no live price`; drawer POSITION block; Satellite optional **Last price** (form + drawer, `lastPx {v, at}`, amber "old price" after 24 h, display only).
**B** Flow cards size independently, 3-line normal-colour text, real `Details ▾`/`Close ▴` button (44 px), one full-width panel (phone: directly under the card): full Weekly Impact note + carry-over, every catalyst (time, forecast/previous/actual, mechanism, scenarios, watch), Playbook (bias, posture, quarter, confidence, why, change-if, drivers), sources + "as of", separate "Your note · this week"; "No Playbook for X · Add ›".
**C** Plan cards: header (tag · Long/Short · Ready/Blocked/R), six numbers, `More ▾`; Blocked state = red chip, "Can't place: <sizing reason>", `Fix stop ›`/`Fix size ›`, size/loss "not sized"; Ready cannot be set while blocked, existing flag shown off not deleted; "Fix risk" / "Risk / size not OK" removed everywhere.

## Formulas (money in account currency; Core ฿, Sat shown in $)
- heldQty = Σ filled qty · plannedQty = Σ all plan rows (never counted as held) · avgEntry = Σqty×px / Σqty (fills only)
- cost = Σ qty×px×mult×FX · value = held × price × mult × FX · weight = value ÷ account value (`ps1E`, same basis as risk %) · pool % = value ÷ strategy pool
- uPnl = dir × (price − avg) × held × mult × FX (% vs cost) · toStop = held × |price − stop| × mult × FX
- openRisk = engine `ideaResult.exposure` on held quantity (≤ 0 → "none · stop at or beyond entry") · stopPnl = dir × (stop − avg) × held × mult × FX (loss vs entry if stopped)
- plannedRisk = stored `plan.ps1.riskMoney` (Sat: sizing result) · R = |first entry − first stop|, shown R = (price − avg)/R.
NVDA: cost ฿58,675 · value ฿60,476 (1.205%) · uPnl +฿1,801 (+3.07%) · open risk ฿17,825 (0.355%) · price→stop ฿19,626 · plan ฿36,056 (0.718%) · 1R = $48 · +0.10R.

## Verified
node `pv1_posview_test.js` 42 pass (long/short, partial fill, mult ≠ 1, no price, no FX, stop beyond entry, the 153,497 / 58,223 cases, planned rows never change held/cost/value) · `run_tests_pv1.py` 165 checks at 1440/1280/390 · full `run_regression.sh` vs base (see end).
Existing tests intentionally changed: phase373 "card heights equal per row" → "size independently"; "Fix risk ›" → "Fix size ›"; Holding card hooks; re1d "r1/r2/r3" structure.

## Data still unavailable / notes
- Satellite has no live price (by design): value/P&L/to-entry appear only with the optional manual Last price.
- Engine "Another Satellite setup is active" gate shows as "Can't place" with the size kept.
- The dashboard backup/export omits core cards (plans, lots, prices) — separate issue.
- Planned Sat entry 2 (split entries) is not shown as a second row in the card numbers.
- No policy question found; no investment rule, sizing, limit or gate changed.

## Final regression (committed tree vs base)
Base `origin/main`: 34/41 ok, 7 failing (phase122, 365, 366, 367, 373, cg1, ht1 — the same pre-existing failures, e.g. phase373's 390 px `#hdrPlanBtn` click timeout).
PV1: **37/44 ok, 7 failing — the identical set**, with per-suite fail counts equal to base (phase373 419 pass / 1 fail as on base). Added green suites: `sync_pv1`, `node pv1_posview`, `run_tests_pv1` (165 checks).
