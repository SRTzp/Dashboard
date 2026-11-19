# RS2a · Ranked RS list (MarketSmith-style, price-only)

Decided by SRTp 19 Nov 2026: **liquid US stocks only**. Queued: after ID1 and the iPhone QA pass.
Purpose: one ranked list of the strongest liquid US stocks, to find Momentum candidates without typing tickers. Display and ranking only; never a gate.

## Universe (refreshed weekly by the job)
- All NYSE + Nasdaq + NYSE American common stocks from the Nasdaq Trader symbol files (`nasdaqlisted.txt`, `otherlisted.txt`). Drop ETFs, test issues, warrants, units, preferreds and rights.
- Liquid = last close ≥ $10 **and** 50-day average dollar volume ≥ $10M. Expect ~1,800–2,200 names. Store the list + counts in `rs2/_meta`.
- One universe for everything: the RS1 ratings on Watch switch to this same liquid universe, so a stock has the same rating on Watch and in the list. (Ratings will shift a little once; note it in the summary.)

## Data (GitHub Actions, extend `build_prices.py` or a new `build_rs2.py` in the same daily `prices` workflow)
- yfinance batch download in chunks (≤ 200 tickers per call, short sleeps, retry once); 13 months of daily adjusted closes + volume.
- Per stock: rating (same formula as RS1), rating4wAgo, line (20-session slope), newHigh / newHigh5d, offHigh, hi52, close, adv50 ($), sector, industry (cached), r3m–r12m.
- Industry group rank is RS2b (later); keep the `industry` field ready.
- Write one Firestore doc per day: `users/{uid}/rs2/latest` = `{asOf, n, rows:[...]}`, kept compact (short keys, rounded numbers, < 900 KB). If it grows too big, split into `rs2/latest_0..k` (≤ 500 rows each).
- Runtime target < 15 min; if the full set fails, keep yesterday's doc and set `_meta.error`.

## UI: Watch › "Screen" (4th segment: Momentum · Compounder · Ideas · Screen)
- Table: Ticker · Name · Sector (short) · RS · from high (the same 3-slot cell as WL2) · RS 4w Δ · Price · Avg $vol · `+ Watch`.
- Default view: RS ≥ 80, sorted by "Near high + RS". Filters (one `Filter ▾`): RS min (70/80/90), within x% of high (10/15/25/any), new high only, sector, min $vol.
- `+ Watch` adds the stock to the Momentum watchlist (status No plan) and turns into `Watching ✓`. Stocks already on Watch show `Watching ✓`.
- Phone: 2-line rows (ticker · RS · % / name · sector · $vol) plus `+`. 50 rows, then "Show more".
- Header line: "1,943 liquid US stocks · as of 18 Nov close".

## Proof
- Selftest: symbol-file filtering, liquidity filter, chunked download retry, doc size limit.
- `run_tests_rs2a.py`: filters, sort, + Watch round-trip, missing data, 360/390/1440 no overflow.
- Side-by-side vs a mockup (to be drawn before the build). `docs/reports/RS2a-summary.md`: universe size, runtime, 10 ratings sanity check, doc size.
