# RRG1 — Relative-trend model fix (Flow › themes / sector cards)

Status: proposal agreed for build (2026-11-06). Repo index.html ("index-3.html"). Branch from main: claude/rrg1.
Planning-chat trace was done on origin/main (line numbers approximate).

## A. Confirmed in code (no market data needed)
1. `rrgQuadOf(ratio, mom)` (~22950) classifies only on z-scored values (100 + z over 252 D / 52 W). `ratio ≥ 100` = raw above its OWN mean, not raw > 0. A still-negative RS trend can be "Leading" (reproduced: rsTrend −1.00 → lead).
2. Same for momentum: `mom ≥ 100` ≠ underlying change > 0.
3. `sdChip()` (~23278): "↗ strong + rising" = quad lead + dMom ≥ 0.15 (z units). No check on raw > 0, raw rising, or price.
4. "Strong / แข็ง" label (~23183) comes from z ≥ 0.3 — same issue.
5. Inconsistency: breadth (~23668) already uses `rsTrend > 0` = "beating SPY now"; the quadrant does not. Same card can be counted "not beating SPY" in breadth and "Leading" in the quadrant.
6. `rrgCacheFresh()` (~23015) = fetched today. Does not check the last market-data date.
7. `rrgToWeekly()` (~22940) includes the current partial week and dates it by its Monday; the last real observation date is lost.
8. Card "4 d" = consecutive bars in the same quadrant (D or W bars). "−12.0%" = close vs max HIGH of last 252 D / 52 W bars. Neither is labelled.
9. Model is custom (EMA12/26 of close/SPY, z-scored). Not JdK RS-Ratio/RS-Momentum. Don't claim equivalence.

## B. Hypotheses — need real PAVE/SPY data to confirm
- Whether PAVE's current raw RS trend is negative (likely, given chart + weekly indicator).
- How much of the gap vs the TradingView indicator comes from Daily-vs-Weekly and SPY-vs-SPX.
- Whether the screenshot used stale prices.
→ The diagnostic view (E) must make these checkable for any card.

## C. Decision: Option B (explicit relative-trend states), z-scores kept as context
Why B: the dashboard uses RRG to pick current relative leaders (Momentum "Strong RS", theme rotation). Breadth already defines "winning" as raw > 0, so B makes the quadrant agree with it. Option A would keep a misleading 4-box picture and rely on users reading fine print.
Trade-off: more states flip near zero → handled with deadband + hysteresis. "Improving from very weak" signal is kept as a context line, not lost.

### States (internal keys kept for stored phase history)
| raw (EMA spread) | change (raw − raw[lag]) | key | Label | Colour |
|---|---|---|---|---|
| > +ε | > +δ | lead | Outperforming · strengthening | teal |
| > +ε | ≤ +δ | weak | Outperforming · fading | amber |
| < −ε | > +δ | imp | Underperforming · recovering | blue |
| < −ε | ≤ +δ | lag | Underperforming · worsening | red |
| within ±ε | any | flat | Neutral vs benchmark | grey |
- ε, δ: proposal = 0.10 × SD of raw / of change over the same window (D 252 / W 52). Hysteresis: once in a state, leave only when crossing the opposite threshold (e.g. stay "Outperforming" until raw < −ε… or < 0 — coder to test both and report flip counts on scenarios). Calibrate on scenarios; report chosen values and why.
- Change uses raw (not z). Lag unchanged (D 5, W 4).
- z-scores stay as "vs own 1y history": e.g. "Unusually strong vs its 1y range" / "Unusually weak" / "Normal range". Never used to decide outperform/underperform.
- `flat` is new: any code that switches on quad must handle it (breadth, transitions list, SD phase, filters, colours).

### Labels / copy
- Feature name: "Relative Trend vs SPY" (+ timeframe). Remove "RRG" wording from the UI or footnote "custom model, not JdK RRG".
- sdChip: "↗ strengthening" only when raw > +ε AND change > +δ. "↗ recovering (still below SPY)" when raw < −ε AND change > +δ. Nothing otherwise.
- "Strong/แข็ง" z-label → "Above its 1y norm" / "Below its 1y norm".
- Card: "4 d" → "4 bars in state" (tooltip: "consecutive daily/weekly bars"). "−12.0%" → "12.0% below 52W high".
- Absolute price direction shown separately (e.g. "Price 20D: −3.1%") so "outperforming" ≠ "price rising".
- Tooltip on every state: benchmark, timeframe, lookback, "relative to SPY, not absolute price".

## D. Freshness + weekly bars
- Store per series `lastBarDate` (latest market date in the data). Fresh = fetched today AND benchmark + asset lastBarDate ≥ last expected US session (handle weekends/holidays loosely: ≤ 4 calendar days old). Otherwise show "Data as of <date> · stale".
- Asset and benchmark must end on the same date; if not, mark "mismatched dates" and don't classify.
- Weekly: keep Monday as week key, but store `lastObs` date per weekly bar. The current week is PARTIAL until its last session closes.
  - Classify on the last COMPLETED week. Show the partial week as a preview line: "This week so far (to Wed): …".

## E. Diagnostic view (per card, collapsed by default "Details ›")
Benchmark · timeframe · bars used · last observation date (asset / benchmark) · last close used (asset / benchmark) · raw RS trend (EMA spread %) · raw change (lag n) · z vs own history (ratio, mom) · state + thresholds ε/δ · freshness status · "custom model" note.

## F. Validation (synthetic, deterministic tests)
1. Persistent underperformance → Underperforming · worsening.
2. Recovering underperformance (the planning-chat counterexample) → Underperforming · recovering, NOT lead.
3. Outperformance during a market decline (asset falls less than benchmark) → Outperforming, with price-down shown separately.
4. Weakening leadership (raw > 0, falling) → Outperforming · fading.
5. Near-zero oscillation → flat / limited flips (report flip count with vs without hysteresis).
6. Stale data (last bar 7 days old) → stale badge; mismatched asset/benchmark end dates → not classified.
7. Partial week → classification from completed week; preview shown.
8. Breadth and quadrant agree on every scenario (raw > ε ⇔ outperforming).

## G. Migration
- `RRG_BUILD` 6 → 7 and a model version on cached results (`f.rrg.model = 2`). On load with an older model: recompute from cached prices if they are stored; otherwise refetch (respect API batch/cooldown).
- Sector-note phases recorded under the old model: do NOT raise "Revisit · phase changed" just because the model changed. Re-baseline once (store the new phase, mark "model updated <date>").
- Transitions list ("→ Leading") must not show a burst of fake transitions after the upgrade.

## H. Own price trend (separate dimension — build AFTER C–G, separate commit)
Purpose: "outperforming SPY" must never be read as "price rising". Adding this does NOT fix the z-score issue; C must land first.
- Card shows 3 separate chips, same timeframe as the view (D or W), plus the latest price date:
  1. **Price trend:** Up / Down / Mixed
  2. **Relative trend:** Positive / Negative / Neutral (= sign of raw with ε, from C)
  3. **Relative momentum:** Strengthening / Weakening (= sign of change with δ, from C)
- Price-trend rule (matches SRTp's existing trend rules / holding period):
  - Weekly view: close vs 40-week EMA, slope = EMA now vs EMA 4 bars ago.
  - Daily view: close vs 50-day EMA, slope = EMA now vs EMA 5 bars ago.
  - Up = close above EMA AND EMA rising. Down = close below EMA AND EMA falling. Anything else = Mixed.
  - Weekly uses the last COMPLETED week (same as D).
- Never combine the three into one score or let price trend change the relative state.
- Tooltip lists the rule, timeframe, and last price date. Diagnostic view (E) adds: EMA value, EMA slope, close used.
- Tests (add to F):
  9. ETF −3% while SPY −8% → Relative Positive + Price Down (not "rising").
  10. Price above a falling EMA → Mixed.
  11. Rising and outperforming → Up + Positive + Strengthening.

## Out of scope
Changing benchmark (SPY), EMA lengths, lags, or adding SPX/weekly-indicator parity. No changes to trading rules or sizing.

## Deliver
Audit first (confirm A1–A9 still true on main, list every consumer of quad/rrgQuadOf/dMom/sdChip/rrgCacheFresh), wait for OK. Then build C–G, then H (separate commit), tests F1–F8 + H9–H11, screenshots (390/1440) of a card + diagnostic view, draft PR. Don't merge.
