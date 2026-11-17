# RM1 — shared new-entry budget modifier (SMA 20/50 on ACWI/BIL + HYG/IEI)

Approved by SRTp 17 Nov 2026 (rev 3 · final spec 11:14 · Compounder total 1.25% + lean UI rules 13:08). **Intentional strategy-rule change** (replaces the old regime signals). No mockup: layouts unchanged, labels and values only.
Base: latest `origin/main` **after PV1b is merged** (PV1 / PV1b touch the same Today / Plan rows). Branch: `claude/rm1`. Commits: A data → B engine + sizing → C UI → D tests/report, push each.

## Rules
- One shared signal result (`regimeState` or its successor) feeds sizing AND every view: Flow chips, Flow summary, Today, Port, Risk room, Plan board, drawer, forms. No second calculation in any view.
- Saved plans and executed holdings are never resized. New logic applies to a new entry or an explicit recalculation (the existing re-size / Edit → Save path; find and name it in the report). Holdings value, P&L, exit rules untouched.
- No data migration, no deletes. `render()` stays pure. English UI. No overflow at 1440 / 1280 / 390.
- Satellite (XAU / BTC / S50 / Brent) unchanged.

## A · Data — `scripts/build_fundflow.py` (+ `fundflow.yml` if needed)
- For `ACWI_BIL` and `HYG_IEI` only: use **total-return-adjusted daily closes** (yfinance `Adj Close`, or `auto_adjust=True` — pick one, state it). Never fall back to raw closes; if adjusted data is missing → that ratio is Unavailable.
- Align the two legs on common dates; ratio = numerator ÷ denominator; **SMA20 and SMA50 of the ratio** (not of each ETF).
- Completed sessions only: drop a bar for the current US date if the run is before the US close (+15 min, America/New_York).
- Signal per ratio: SMA20 > SMA50 → green; < → red; equal → previous valid signal, else neutral. Fewer than 50 valid aligned observations → unavailable.
- Write per ratio: `sma:[20,50]`, `adj:true`, `up` (true / false / null), `state` ('green'|'red'|'neutral'|'unavailable'), `days_in_state` (consecutive completed sessions in the current state), `bar` (last aligned date), `inputs_asof` {ACWI, BIL / HYG, IEI: last date of each leg}, `sma20`, `sma50`, `ratio`. Remove the `slow` (EMA 50/100) block and EMA fields for these two keys. Other ratios (HYG_IEF, HG_GC, …) unchanged.
- Update `--selftest`: hand-computed SMA cases, equal→previous, equal with no previous → neutral, 49 vs 50 observations, missing leg, adjusted-only (no raw fallback), partial-session drop.

## B · Engine + sizing
**Modifier table** (policy config, labelled "initial settings to test"):

| Equity (ACWI/BIL) | Credit (HYG/IEI) | Modifier |
|---|---|---:|
| green | green | 100% |
| green | red | 75% |
| red | green | 75% |
| red | red | 50% |

- Either signal neutral / unavailable, or data stale → **fallback 75%**. Missing data never yields 100%.
- Freshness: keep the engine's rule — **age = today (Asia/Bangkok, existing convention) − the OLDEST of the four `inputs_asof` dates**; ≤ 4 calendar days fresh, > 4 stale. One shared function used by engine and all views (removes the panel's 5-business-day rule).
- **effectiveMultiplier = min(regimeModifier, emergencyMultiplier)** — applied once to the original base risk budget; never multiplied together. Emergency 0% blocks new risk. Emergency triggers and exit behaviour unchanged; no automatic selling.
- Always compute from the base budget (never reduce an already-reduced number).
- **Compounder (risk-based, unchanged model):** pilot risk budget = account equity × 0.50% × effective modifier; qty = budget ÷ (loss per share at stop × FX). **Total risk cap = 1.25% × effective modifier** (decided 17 Nov 13:08: the whole-plan budget is 1.25%, matching plan sizing's 0.80–1.25% range), net of the ticker's existing position risk. Engine change: add `comp.totalCapPct: 1.25` and use it for the thesis-done total (today `pilotPct + addonPct` = 1.00%); keep pilot 0.50%, one new add-on order ≤ 0.50% × effective modifier, and 0.50% total without thesis. Update the engine tests that assert 1.00% (list them). The 12.5%-of-account **value cap stays unchanged** (not × modifier) and counts existing holdings; final qty = the smallest of risk qty, total-risk room qty and value-cap room qty. The modifier **replaces** the old regime factor (do not apply both). Existing thesis / Starter / homework rules unchanged.
- **Momentum:** per-idea risk budget × effective modifier; qty = budget ÷ (|entry − stop| × multiplier × FX). Replaces the fixed 100% left from RE1. Other Momentum caps unchanged.
- FX conversion, contract multipliers and lot / quantity steps as today; always round down.
- `re1-adapter.js` reads the new fields (`state`, `inputs_asof`), not `slow.up`.

## C · UI (labels / values only, existing places)
- Flow summary line shows the effective multiplier and its reason, e.g. **"New-entry budget: 75% of normal · equity red, credit green."** / **"New-entry budget: 50% of normal · emergency brake."** Fallback: **"Modifier unavailable · fallback cap 75%"**, plus the stricter effective limit when one applies (e.g. "· effective 50% (emergency brake)").
- Both indicators labelled **"SMA 20/50"** with the data date (oldest input date). If days are shown: **"green 16 days"** style — never a bare number that could read as an SMA period.
- Replace the fixed "Risk-on 100% / Core ceiling 100% / Momentum 100%" with the shared result; fix Today's regime line (it used the fast pair). All views show the same state, %, date and fresh/stale.
- Sizing results go into the existing fields. No new panel, confirmation step or Holding control.
- Where a size is reduced, the existing size line names the one limiting rule: e.g. `Risk ฿2,000 · limited by regime 50%` / `· limited by 12.5% value cap` / `· limited by total risk 1.25%`. Detail in More only.
- Rule text from the engine: the new-plan menu (`BD_NEW`) and any help text read pilot / total / Momentum ranges from policy config, not hard-coded strings (today the menu says "0.80–1.25%" while the engine caps at 1.00%).

## UI rules (lean · applies to every change in this job)
1. No new panels, pages or tabs; change existing rows in place.
2. Each screen same length or shorter: report row count at 390 before / after for Flow, Today, Plan board.
3. One line per item: reason + number + one button; detail in More.
4. No new number on a main screen unless one is removed.
5. Waiting items hidden or collapsed.
6. Plain short words; no new symbols to learn.

## Tests / proof
- Node: four combinations → 100 / 75 / 75 / 50; neutral, unavailable, stale (4 days valid, 5 stale, oldest-input rule) → 75; min() with emergency (emergency 50% + red/red → 50%, not 25%; emergency 0% → no new risk, nothing sold); repeated recalculation of the same plan gives identical qty (no compounding); saved plan + holding unchanged after a signal change; Compounder qty limited by each of risk / total-risk room (1.25% × modifier) / value-cap room in turn, with the matching "limited by" text; Momentum with multiplier ≠ 1 and FX; round-down.
- Browser suite `tests/run_tests_rm1.py`: same state, %, date in Flow, Today, Port, Risk room, Plan / drawer for one fixture; "SMA 20/50" labels; fallback text; no overflow 1440 / 1280 / 390.
- Existing engine suites updated only where the old EMA / slow-pair rule is asserted (list each changed assertion). `tests/run_regression.sh` must not get worse than base.
- Screenshots (`git add -f`): `rm1-flow-1440/390`, `rm1-today-390`, `rm1-plan-1440`, `rm1-fallback-1440`.

## Report — `docs/reports/RM1-summary.md`
Data source + adjustment method · formulas · freshness rule · every place that read the old signal and now reads the shared one · the explicit-recalculation path · today's live result (both states, SMA values, dates, modifier) · tests changed and why · open questions (isolate; keep independent parts).
