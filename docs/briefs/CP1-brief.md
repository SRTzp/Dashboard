# CP1 — Compounder first when the market pulls back (opportunity, not fear) · buy zone · 40-week average · Compounder size rule 100/75

Branch from fresh origin/main (after RX1 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-cp1 -b claude/cp1 origin/main`. First commit = this brief + `cp1-mockup.html` (~/Documents/Dashboard/mockups/). UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md`. Locked brief. Keep e2e1 green. Commits A–E separate.

## Intent (SRTp 26 Nov)
Compounder chances are rare and come when the market rests. In a pullback the Dashboard must (1) put Compounder first, (2) push homework on Compounder stocks, (3) frame the pullback as a **buying opportunity, not a reason to fear** — no words like "downtrend", "risk-off", "danger" in the Compounder parts. Momentum stays as now (just below). Sat unchanged.

## A · Data (prices job)
- For every Watch stock (US + TH) the daily job also writes: `ma200` (200-day simple average of closes = "40-week average"), `hi52` (52-week high close), `offHi` (% from hi52), `vsMa` (% vs ma200). Use the bars it already downloads; no new source.
- Market doc `users/{uid}/market/index`: SPY and SET index (`^SET.BK` via yfinance) `{close, hi52, offHi, asOf}`. SPY may reuse rrg/bars.
- Selftest: values for a fixture series; missing history (< 200 bars) → field omitted (app shows "—"), never 0.

## B · Market state + Compounder size rule (engine)
- `pullback(market)` = SPY **or** SET ≥ **7%** below its 52-week high, **or** exactly one regime signal (ACWI/BIL, HYG/IEI) red. US stocks use SPY, Thai stocks use SET; Today's line shows both.
- Constants in ONE place: `MARKET_PULLBACK_PCT = 7` and `COMP_REGIME_FACTOR = { green:1.00, oneRed:1.00, bothRed:0.75 }` (was 1.00 / 0.75 / 0.50). Only Compounder uses it; Momentum and Sat unchanged. `factor = min(regime, emergency)` stays. This intentionally changes the engine (risk-engine.js / re1-adapter.js / sync tools): update the nt1d guard to allow exactly this change, and update RE1 tests that expected 75/50.
- Engine tests: one red → Compounder Pilot full 0.50%; both red → 0.375%; Momentum unchanged in all three states.

## C · Today (mockup section A)
- **Mood card**: add one line `MARKET  SPY −9% from high · SET −6% · HYG/IEI green`. In a pullback the Mood pill reads `Pullback` (amber) + `good time for Compounder · Compounder size 100%` (or `75%` when both red: `Compounder size 75% · buy in steps`). Normal: grey `… · normal`.
- **Act, pullback**: new group `COMPOUNDER FIRST · market pullback · n to look at` ABOVE Enter. Rows in this order:
  1. In buy zone (price inside the stock's zone) — `Now 905 · zone 880–920 · 40-wk avg 912 (−1%) · homework ✓` → `Make plan ›` (the one dark button) — or `Homework ›` if homework not done.
  2. Near the 40-week average (vsMa between −5% and +3%, no zone or outside zone) — same line, button `Homework ›` if not done, else `Make plan ›` (white).
  3. Holding with add-on room (engine allows Add-on) — `Add-on ›`.
  Max 5 rows + `+n ›`. Stocks already planned/ordered show their existing plan row instead (no duplicate).
- **Act, normal market**: Today as now; only a one-line summary at the bottom of Act when ≥ 1 Compounder is in its buy zone: `COMPOUNDER · 1 in buy zone · show ›` (expands the same rows in place).
- **To do (homework nudge)**: in a pullback add one row `Market pullback · finish homework on n Compounder stocks ›` (opens Watch › Compounder filtered to "homework not done"), amber.

## D · Homework page + Watch (mockup section B)
- Homework page, Compounder only, under field 3: optional `Buy zone` (from – to; numbers, 16px). Helper line `Now 905 · 40-wk avg 912 · 52-wk high 1,008 (−10%) · use 40-wk avg ±3%` (tap fills the zone). Not part of the 3 required answers. Stored on the Watch item (`buyZone:{lo,hi}`).
- Watch › Compounder list: two columns `vs 40-wk` (e.g. −1%) and `Buy zone` (`in 880–920` green pill · `above 250–265` grey · `—`). iPhone: line 2 adds `vs 40-wk −1% · in zone`.

## E · iPhone + tests
- iPhone 390 as mockup: Mood two lines, Compounder rows stack with full-width buttons, no "…".
- `tests/run_tests_cp1.py`: pullback on/off from SPY 6.9% vs 7.0%, SET only, one red, both red; row ordering + buttons; normal-market summary line; To do nudge only in a pullback; buy zone save + Today alert; Watch columns; wording check: no "downtrend/risk-off/danger" text inside the Compounder group or Mood pullback line; e2e1 still green; add a J9 journey (pullback → Make plan from Compounder row → Pilot at 100%).

## Screenshots (only `cp1-*.png`)
`cp1-today-pullback` (1440 + 390), `cp1-today-normal` (1440), `cp1-buyzone` (390), `cp1-watch-comp` (1440 + 390).

## Rules
Full `JOBS=2 bash tests/run_regression.sh` + hooks · Python selftests for A · revert tracked screenshot rewrites · new suite in REST= · no push until I review — report tests, judgment calls, PNG list.
