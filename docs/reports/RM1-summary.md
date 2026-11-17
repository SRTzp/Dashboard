# RM1 — summary (brief rev 4)

Status: **A, B, C, D done and pushed on `claude/rm1`.** Intentional strategy-rule change: the old regime signals (EMA 20/50 + 50/100, 100/75/50 factors, fixed Momentum 100%) are replaced by one shared SMA 20/50 modifier.

## Data source + adjustment method
- yfinance, **`auto_adjust=True`** (total-return-adjusted closes) for ACWI, BIL, HYG, IEI only. Other ratios keep raw closes (`auto_adjust=False`).
- A missing leg or an adjusted-data failure makes that ratio `unavailable`. There is no raw fallback. If no adjusted symbol arrives at all, the script refuses to overwrite `fundflow.json`.
- Completed US sessions only: the bar for the current US date is dropped when the run is before 16:15 America/New_York.
- The Mac cannot reach Yahoo (HTTP 429). The data came from the GitHub Actions run `e986a4c`. Nothing was fetched from this machine.

## Formulas
- ratio = numerator ÷ denominator on common dates; **SMA20 and SMA50 of the ratio** (not of each ETF).
- State: SMA20 > SMA50 → green; < → red; equal → previous valid state, else neutral; fewer than 50 aligned observations → unavailable.
- Modifier table (policy, "initial settings to test"): green/green 100% · green/red 80% · red/green 80% · red/red 60% · fallback 80%.
- Effective multiplier = **min(regime modifier, emergency)**, applied once to the base budget (never multiplied).
- Compounder: pilot 0.50% × modifier; total-risk cap 1.25% × modifier with thesis (0.50% without); one add-on ≤ 0.50% × modifier; 12.5% value cap (not × modifier, counts holdings). Final qty = min(risk qty, total-risk room qty, value-cap room qty).
- Momentum: 0.45% × modifier; qty = budget ÷ (|entry − stop| × multiplier × FX), rounded down.
- Policy settings (all in `risk-engine.js` `POLICY.regime`): the four table values, the fallback, `freshDays` 4, `smaFast` 20, `smaSlow` 50. `build_fundflow.py` reads the SMA periods from the same file. The app treats a ratio built with other periods, or unadjusted, as unavailable.

## Freshness rule
age = today (Asia/Bangkok) − **oldest of the four `inputs_asof` dates**. ≤ 4 calendar days is fresh, > 4 is stale. The file's `as_of` (the run date) is never used. One function, `RiskEngine.regimeFromFundflow`, serves the engine and every view. The old 5-business-day panel rule is gone (the Data panel now uses the same age and the 4-day limit).

## Every place that read the old signal, now reading the shared one
All read `rm1Regime()` / `rm1Eff()` (index.html) or `L.regime` (adapter); both come from `regimeFromFundflow`.
- Engine / adapter: `build()`, `live()`, `compCheck`, `sizeComp`, `sizeMomentum`, report text (`re1-adapter.js`).
- Flow: Risk strip (`bdRiskHtml`: Momentum and Compounder cells + the one-line "New-entry budget: N% of normal · reason" / fallback line), Regime card chips + details + warnings + header, More summary bar (`ffRenderActionBar`: pills, budget cell, hero line), previous-week budget (`ffChangesData`, via the engine table).
- Today: regime line (`tdRegimeVerdict`, which used the fast pair), status pill (`ln4PortPills`), SIZE line, to-do task for stale data, "Other" footer (`coreFNow`).
- Port: "New-entry budget" cell (was "Regime size"), Port heat helpers (`coreFNow`, `ffPoolFactor`).
- Risk room (`re2Room`, via `L.regime`).
- Plan board, drawer and forms: size line (`re1BoxHtml`, plan line `ps1MultPill`), form warning text (`coreFWarn`), Compounder Ladder budget (`ffPoolFactor`), Add-on note.
- `Calc.ffCoreCap` now delegates to `RiskEngine.regimeModifier`. `ffPoolFactor` / `ffCoreNow` / `coreFNow` are thin views of the shared result.
- Menu / help text: `BD_NEW` (new-plan menu) and the Add-on note read pilot / total / Momentum values from `POLICY`.

## The explicit recalculation path
Saved plans and executed holdings are never resized by a signal change. A new size is written only by the plan form: **Plan board → plan → Edit → Save** (`coreNewOpen(..., {mode:'editw'})` → `ps1FormRun0` → `coreNewSave`, which writes `plan.ps1 = n.ps1Last`). Place order only compares the saved qty with today's size (`re1PlanGate`, "Above today's size — allowed now N"). It does not rewrite the plan. Tests confirm that holdings, stored trades and cards are byte-identical after a signal change.

## Today's live result (fundflow run `e986a4c`, 17 Nov 2026)
| ratio | state | SMA20 | SMA50 | days in state | inputs (last date per leg) |
|---|---|---:|---:|---:|---|
| ACWI/BIL | red | 1.713655 | 1.738649 | 32 | ACWI 16 Nov · BIL 16 Nov |
| HYG/IEI | red | 0.672824 | 0.677476 | 24 | HYG 16 Nov · IEI 16 Nov |

Oldest input 16 Nov, so age 1 day and fresh. **Modifier: red/red → 60%** (Flow line: "New-entry budget: 60% of normal · equity red, credit red."). The file's `as_of` was 17 Nov and is not used.

## Tests
- `tests/rm1_engine_test.js` (new, 43 assertions): four combinations, neutral / unavailable / stale (4 days fresh, 5 stale, oldest-input rule), `min()` with emergency, no compounding, holdings untouched, Compounder limited by risk / total-risk room / value-cap room, Momentum with multiplier + FX, round-down.
- `tests/run_tests_rm1.py` (new, 60 checks at 1440 / 1280 / 390): same state, % and date in Flow, Today, Port helpers and Risk room; "SMA 20/50" labels; fallback text; plan-form "limited by regime"; no overflow.
- `scripts/build_fundflow.py --selftest`: rewritten for SMA (hand-computed cases, equal→previous, equal with no previous → neutral, 49 vs 50 observations, missing leg, adjusted-only, partial-session drop).
- Node suites: risk_engine 313/313, re1_adapter 63/63, re1c_live 88/88, core_size, ps1_size, ps1b_size, pv1_posview all pass.
- Screenshots (`git add -f`): `rm1-flow-1440`, `rm1-flow-390`, `rm1-today-390`, `rm1-plan-1440`, `rm1-fallback-1440`.

### Existing assertions changed, and why
| file | change | reason |
|---|---|---|
| `tests/risk_engine_test.js` | one red 75→80, both red 50→60, stale cap 75→80 (×3 incl. "stale both red stays 60"); "whole plan = 1%" → 1.25%; legacy-card total 0.9+0.2 → 1.1+0.2 vs 1.25%; two labels | rev 4 table and total cap 1.25% |
| `tests/re1_adapter_test.js` | fixture ff now `state` + `inputs_asof`; regime 0.75 → 0.80; labels | new data shape + table |
| `tests/re1c_live_test.js` | same fixture; Pilot 0.375 → 0.40, qty 53 → 57, Momentum 0.225 → 0.18 / 0.45 → 0.36 (Momentum now takes the modifier); "total risk 0.9% + 0.375% > 1.00% → blocked" → qty cut to the room, `limit.code = total_risk`; multi-entry caps 0.375 / 0.75 → 0.40 / 1.00 | Momentum × modifier, total cap 1.25% × 80%, rule is now "cut to room" |
| `tests/run_tests_phase373.py` | new-plan menu text `0.35–0.50%` → `0.45%` | menu now reads the policy value |
| `tests/lib_phase24.py` | `set_ff` converts old `{"up": bool}` fixtures to the new shape (input date = fixture `as_of`) | app reads state / inputs_asof |
| `tests/lib_phase39.py` | default fund-flow fixture = fresh green/green (was acwi red / hyg green); a fresh `__FF_JSON` is injected at launch | missing data is now an 80% fallback, never 100%; plans in these suites assume full size |
| `tests/run_tests_phase374.py` | fixture `as_of` = harness clock (was the real date) | otherwise stale → 80% |

### Regression vs base
`tests/run_regression.sh` (full, 44 suites): the branch run had 7 failing suites. **All 7 fail identically on the base tree** (`4b82f00`): phase122 (2), phase365 (2), phase366 (1), phase367 (1), phase373 (1, a 390px crash), phase_cg1 (1), phase_ht1 (2). The only extra failure on the branch was phase373 "10 popup" (menu text), now updated. Net: **not worse than base.** phase373 was re-run after that edit: 419 pass / 1 fail, identical to base (the 390px crash).

## Screen length at 390 (before → after)
Measured with `tests/rm1_rowcount.py` (same fixture on the base tree and the branch). Visible row-like elements / page height:
| screen | before | after |
|---|---|---|
| Flow | 8 rows · 1729 px | 8 rows · 1729 px |
| Today | 2 rows · 893 px | 2 rows · 893 px |
| Plan board | 0 rows · 844 px | 0 rows · 844 px |

No screen got longer. Caveat: the fixture's Plan board shows no rows (collapsed), so that line proves little. The Flow strip's text changed in place (one line, no new element).

## Compare add-on (display only)
`scripts/compare_regime.py` + the workflow `scripts/regime-compare.workflow.yml` (`workflow_dispatch`; **copy it to `.github/workflows/regime-compare.yml`** — the push was refused because the token has no `workflow` scope) write `docs/reports/RM1-compare.md`: 5 years of ACWI/BIL + HYG/IEI adjusted, SMA 10/20 vs 20/50, flips per year, % of days at 100 / 80 / 60, sessions from the 2020 and 2022 lows back to 100%. The table is read from `risk-engine.js`. Selftest passes. **Not run yet** (needs the workflow added, then Actions → regime-compare → Run workflow).

## Open questions
1. **Stale + both signals known:** I used `min(table value, fallback)`, so a stale red/red stays 60% and a stale green/green becomes 80%. The brief says "stale → fallback 80%". If stale red/red should be 80% (looser), say so.
2. **Compounder menu text** now reads "0.50–1.25%" (pilot → total). The old text said "0.80–1.25%" (PS1 plan range). Confirm which range the menu should show.
3. **Value cap with no room** blocks with a new reason `COMP_VALUE_CAP`. Previously the Compounder adapter had no value cap at all (`maxSizePct: null`); the 12.5% only existed in PS1 settings.
4. **Missing / demo fund-flow data** now sizes new entries at the 80% fallback (including Momentum, which was fixed at 100%). Test harnesses that assumed full size now inject a fresh file.
5. **Port Core cell** ("New-entry budget") was not reachable in the test fixture; it is checked through its source and the shared helpers (`coreFNow`, `ffPoolFactor`), not through the DOM.
6. **`emergency 0%`** gives qty 0 and a block; nothing is sold (no exit code touched).
7. Stashed `claude/tw1` working changes are still in `git stash` ("pre-rm1 tw1 working changes").
