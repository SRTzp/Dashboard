# RS1 — data half · summary (2026-11-18)

Branch `claude/rs1-data` · scope: `scripts/build_prices.py`, `data/universe_{us,th}.txt`, `tests/rs1_selftest.py`, `docs/proposals/prices.yml`. No `index.html` / engine edits.

## Universe sizes
| list | symbols in file | had ≥253 Yahoo bars on 2026-11-18 (n in rsTable) | source |
|---|---|---|---|
| US | 518 (S&P 500 = 503, Nasdaq 100 = 101, overlap 86) | **514** | en.wikipedia.org *List of S&P 500 companies*; api.nasdaq.com nasdaq100 list; fetched 2026-11-18 |
| TH | 100 | **100** | **approximate — see below** |

**TH list is NOT the official SET100.** set.or.th is behind bot protection (403) and Wikipedia only lists SET50 ("as of 2025"). The file = 51 SET50 names from Wikipedia + 49 large/liquid SET names I wrote by hand, each verified to have ≥253 Yahoo bars. **Please replace with the official list** (set.or.th → SET100 → constituents) — one name per line. Ratings are percentiles, so a wrong tail shifts TH ratings a little, not wildly.

## Runtime (local, Mac, live Yahoo)
~26 s for 618 universe symbols + 16 sample tickers + 2 benchmarks (chunks of 80, `auto_adjust=True`, 2y). The weekly job adds a few seconds. Action timeout proposed 20 min (huge margin). Yahoo is rate-limited from the Mac; the Action runner wasn't tested here — first Action run is the real check.

## Fields written
`users/{uid}/prices/{ySym}` (merge — existing weekly fields kept):
`sym, ySym, at, rs: {rating, rating4wAgo, line, newHigh, newHigh5d, bench, asOf, reason?}`
`prices/_meta` (merge): `rsTable: {us|th: {asOf, n, cuts[99], cuts4w[99]}}`, `rsRunAt` (+ existing `runAt, ok, failed, n, ver` — `ver` bumped to 2).
- `cuts4w` is my addition (not in the brief): the table as of 20 sessions ago, needed to compute `rating4wAgo` against that day's universe.
- `reason` (only when something is null): `history<252` · `bench<252` · `no-bench` · `no-data` · `universe<30`.
- Rating = 1 + number of cuts below the score, clamped 1–99 (equal scores → equal rating). Needs 253 bars (r12m looks back 252 sessions).
- Tickers = non-archived Watchlist (incl. Candidates) + Core cards plan/open, deduped; one uid (the script's `FIREBASE_UID`).
- **Changed existing behaviour:** the weekly writes used `set()` (overwrite), which would have wiped `rs`; both writers now `set(..., merge=True)`. RS failure is caught and cannot fail the weekly job.
- Watchlist-only tickers now get a `prices/{ySym}` doc with **no `close`/`ema10w`**. Worth checking the app's price listener (index.html ~13812) tolerates that when the UI half lands.

## Issue to decide: TH RS line (`^SET.BK`)
Yahoo returns **1 row** for `^SET.BK` (also ^SET50/^SET100/^SETHD) over every period I tried, today. So TH `line / newHigh / newHigh5d` are `null` with `reason: 'bench<252'`; TH **ratings still work** (they don't need the benchmark). It may be transient — re-check on the first Action run. Fallback if it persists: `TDEX.BK` (SET50 ETF; returns 483 bars) as TH bench — one-line change to `RS_BENCH`, but it deviates from the brief, so I did not do it. Your call.

## Sample ratings (live run, asOf 2026-11-18)
TradingView/IBD column is blank: I can't read TradingView or IBD from here. Please fill from the TradingView RS Rating indicator for a sanity check (the brief says approximate is fine).

| ticker | rating | 4w ago | line | newHigh / 5d | TV/IBD |
|---|---|---|---|---|---|
| NVDA | 5 | 70 | down | – / – | |
| AAPL | 89 | 82 | up | ✔ / ✔ | |
| MSFT | 67 | 86 | flat | – / – | |
| TSLA | 36 | 46 | up | – / – | |
| META | 53 | 61 | down | – / – | |
| PLTR | 35 | 94 | down | – / – | |
| INTC | 15 | 95 | down | – / – | |
| KO | 87 | 86 | up | – / ✔ | |
| UNH | 66 | 67 | down | – / – | |
| PTT.BK | 43 | 64 | null (bench) | null | |
| ADVANC.BK | 31 | 33 | null (bench) | null | |
| DELTA.BK | 3 | 41 | null (bench) | null | |
| AOT.BK | 59 | 39 | null (bench) | null | |
| CPALL.BK | 46 | 20 | null (bench) | null | |
| TTB.BK | 75 | 71 | null (bench) | null | |

Observations: some jumps look large (INTC 95 → 15, PLTR 94 → 35 in 4 weeks) — consistent with the 40%-weight 3-month return rolling off a big move, but worth eyeballing against TradingView first. (US rows were run before the `reason` rename; values unchanged.)

## Tests
`python3 tests/rs1_selftest.py` → 34 checks OK (weighted score, percentile/ties/clamp, <252 bars → null + reason, TH mapping & bench, RS-line ±2% band, newHigh / newHigh5d, bench gaps, run_rs with fake fetch/write). Added as a step in the proposed workflow. Not added to `run_regression.sh` (not touched).

## For you to do
1. Paste `docs/proposals/prices.yml` over `.github/workflows/prices.yml` (adds Mon–Thu 22:30 UTC cron, selftest step, 20-min timeout; weekend crons kept).
2. Replace `data/universe_th.txt` with the official SET100.
3. Decide TH benchmark (above) · fill the TV/IBD column.
4. Run the workflow manually once and check `prices/_meta.rsTable` in Firestore.
