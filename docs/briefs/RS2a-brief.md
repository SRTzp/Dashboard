# RS2a · Ranked RS list (MarketSmith-style, price-only)

Decided by SRTp 19 Nov 2026: **liquid US stocks only**. Mockup approved 20 Nov; build after AU3 is merged.
Purpose: one ranked list of the strongest liquid US stocks, to find Momentum candidates without typing tickers. Display and ranking only; never a gate.

## Universe (refreshed weekly by the job)
- All NYSE + Nasdaq + NYSE American common stocks from the Nasdaq Trader symbol files (`nasdaqlisted.txt`, `otherlisted.txt`). Drop ETFs, test issues, warrants, units, preferreds and rights.
- Liquid = last close ≥ $10 **and** 50-day average dollar volume ≥ $10M. Expect ~1,800–2,200 names. Store the list + counts in `rs2/_meta`.
- The list shows liquid stocks only, but ratings are graded against the whole US market (closer to MarketSmith), via the weekly percentile table below. The RS1 ratings on Watch use the same table, so a stock has the same rating on Watch and in the list. (Ratings will shift a little once; note it in the summary.)

## Weekly whole-market percentile table (decided 20 Nov)
- Weekend run (with the weekend `prices` schedule): score = the RS formula for all liquid stocks **plus a random sample of ~1,500 of the other (non-liquid) common stocks** (new seed each week; ≥ 252 bars only). Store the 99 score cut-offs + `asOf`, `n`, sample size in `rs2/_meta.cuts` (also `cuts4w` for rating4wAgo).
- Daily: score the liquid stocks (and Watch tickers) and map each score to 1–99 with that table. Stocks outside the table range clamp to 1 / 99.
- Source: Yahoo (yfinance) first, chunked with sleeps and one retry; convert symbols (`BRK.B` → `BRK-B`). If fewer than 80% of the sample download, keep last week's table and set `_meta.cutsStale`.
- Fallback (only if Yahoo keeps failing): Stooq bulk daily US data. Build the reader behind a flag (`RS2_SOURCE=stooq`), off by default; note in the summary whether it was needed.
- Selftest: cut-offs from a known synthetic set, clamp, stale-table path, symbol conversion.

## Data (GitHub Actions, extend `build_prices.py` or a new `build_rs2.py` in the same daily `prices` workflow)
- yfinance batch download in chunks (≤ 200 tickers per call, short sleeps, retry once); 13 months of daily adjusted closes + volume.
- Per stock: name (short), rating (same formula as RS1), rating4wAgo, line (20-session slope), newHigh / newHigh5d, offHigh, hi52, close, adv50 ($), sector, industry (cached), r3m–r12m, rs1m and rs3m (1-month and 3-month RS ratings, each ranked on that period's return with the same weekly table method), next earnings date (yfinance calendar; null if unknown).
- Industry group rank is RS2b (later); keep the `industry` field ready.
- Write one Firestore doc per day: `users/{uid}/rs2/latest` = `{asOf, n, rows:[...]}`, kept compact (short keys, rounded numbers, < 900 KB). If it grows too big, split into `rs2/latest_0..k` (≤ 500 rows each).
- Runtime target < 15 min; if the full set fails, keep yesterday's doc and set `_meta.error`.

## UI: Watch › "Screen" (4th segment: Momentum · Compounder · Ideas · Screen)
Spec = mockups `docs/briefs/lr/ScreenRS.dc.html` (1440) + `ScreenRSPhone.dc.html` (390), approved 20 Nov. Same layout as the Momentum table + detail panel.
- Desktop columns (fixed widths, numbers grouped left, action right): Stock (ticker + short muted name, ellipsis) · Sector vs SPY (short name + RRG arrow) · RS · from high (the 3-slot cell from WL2) · Price · Avg $vol · Earnings (date, or "in Nd" amber when ≤ 7 days) · `+ Watch` / `Watching ✓`.
- No Status, Thesis, Next check or RS 4w columns (Status/Thesis/Next check belong to stocks already on Watch; RS 4w is covered by the 12M · 3M · 1M line and the Emerging preset). Keep rating4wAgo in the data for the Watch detail.
- Preset row (segmented, replaces filter chips): **Leaders** (default: RS ≥ 80 · within 15% of high) · **Emerging** (3M ≥ 90 and 1M ≥ 90 · 12M < 85) · **Pullback** (12M ≥ 85 · 3M ≥ 80 · 1M < 60 · within 15% of high). Thresholds are settings (initial values to test). `Filter ▾` holds the rest (RS min, % from high, new high only, sector, min avg $vol) · Reset. Sort default "Near high + RS".
- Row click → detail panel (right): ticker, name, exchange · grey RS card (rating, line, % from 52w high with date, one line `12M x · 3M y · 1M z` with falling values amber/red, 3m–12m returns) · Sector vs SPY + Holdings ↗ · price · avg $vol · earnings · black `+ Add to Watch` (adds to Momentum as No plan).
- Phone: the preset segmented control replaces the chips row; 2-line rows (ticker · RS · % / name · sector, plus "earnings in Nd" amber when ≤ 7 days) and a `+` / `✓` button; detail as a bottom sheet; 50 rows then Show more.
- Header line: "1,943 liquid US stocks · 86 match · as of 18 Nov close".

## Proof
- Selftest: symbol-file filtering, liquidity filter, chunked download retry, doc size limit.
- `run_tests_rs2a.py`: filters, sort, + Watch round-trip, missing data, 360/390/1440 no overflow.
- Side-by-side vs the mockups (tests/screenshots/rs2a/*-side.png, git add -f). `docs/reports/RS2a-summary.md`: universe size, runtime, 10 ratings sanity check, doc size.
