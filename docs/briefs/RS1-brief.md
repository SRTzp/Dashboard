# RS1 — stock RS: RS line vs index (A) + RS Rating 1–99 (C)

Approved by SRTp 18 Nov 2026 · **queued: start after the redesign steps are merged.**
Purpose: help pick which watchlist stocks to focus on first when the list gets long. **Display and ranking only** — never a gate for screening, plans or trades (RS was dropped as a gate in Nov 2026). Approximate is fine.

## Data (GitHub Actions, extend `scripts/build_prices.py` / `prices.yml`)
- Runs **daily** after the US close (same pattern as `fundflow`; Yahoo is rate-limited on the Mac). Keep the weekend run.
- Tickers: Watchlist + Candidates + open Core cards, both accounts, US and TH (`to_ysym`).
- Benchmarks: US → SPY · TH → ^SET.BK. Adjusted closes.
- **A · RS line** = stock ÷ benchmark: direction over 4 weeks (↗ / → / ↘) and `newHigh` = RS line at its 52-week high (also `newHigh` within the last 5 sessions).
- **C · RS Rating 1–99**: score = 0.4·r3m + 0.2·r6m + 0.2·r9m + 0.2·r12m (price returns, adjusted); percentile vs a universe — **US: S&P 500 + Nasdaq 100 (deduplicated) · TH: SET100**. Universe lists stored in the repo (`data/universe_us.txt`, `data/universe_th.txt`), refreshed by hand quarterly. Stocks outside the universe still get a rating (ranked against it).
- Write to Firestore `users/{uid}/prices/{ySym}`: `rs: {rating, rating4wAgo, line: 'up'|'flat'|'down', newHigh, newHigh5d, bench, asOf}`. Keep existing fields.
- Universe prices are not stored per stock (only the percentile table + `asOf` in `_meta`).

## UI (redesigned Watch)
- Watch row: `RS 87 ↗ · new high` next to the sector arrow; missing data → "RS —" with the reason in a tooltip.
- Sort option on Watch: RS Rating (high first). Default order unchanged.
- Detail panel: rating now vs 4 weeks ago (`87 ← 72`), RS line direction, new-high date, link to the TradingView RS chart (unchanged).

## Tests / proof
- Python selftest: weighted score, percentile (ties, < 252 bars → `null` with reason), TH ticker mapping, new-high logic.
- UI test: row text, sort, missing-data state; no overflow 1440 / 390. Full regression.

## Report — `docs/reports/RS1-summary.md`
Universe sizes · runtime of the Action · sample of 10 ratings vs IBD/TradingView for a sanity check (not exact) · fields written.

## Clarifications for the data half (added 18 Nov, orchestrator)
- Periods in sessions: 3m = 63, 6m = 126, 9m = 189, 12m = 252. r = close_t / close_{t−n} − 1 (adjusted).
- Rating = percentile rank of the score within the universe (stock included if in it), mapped to 1–99 (round, clamp). Ties → same rating. < 252 bars → `rating: null`, `reason: 'history<252'`.
- `rating4wAgo` = same calculation as of 20 sessions ago.
- `line`: RS line slope over 20 sessions: change > +2% → 'up', < −2% → 'down', else 'flat'.
- `newHigh`: RS line today ≥ its max of the last 252 sessions. `newHigh5d`: true if newHigh held on any of the last 5 sessions.
- `bench`: 'SPY' or '^SET.BK'. `asOf`: date of the last close used (ISO).
- Percentile table in `prices/_meta`: `rsTable: {us: {asOf, n, cuts[99]}, th: {...}}` (score cut-offs), so new stocks can be rated without the universe.
- If a universe list can't be fetched, write the list by hand from a public source and note the source + date in the summary.
