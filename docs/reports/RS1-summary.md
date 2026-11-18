# RS1 — data half · summary (2026-11-18)

Branch `claude/rs1-data` · scope: `scripts/build_prices.py`, `data/universe_{us,th}.txt`, `tests/rs1_selftest.py`, `docs/proposals/prices.yml`. No `index.html` / engine edits.

## Universe sizes
| list | symbols in file | had ≥253 Yahoo bars on 2026-11-18 (n in rsTable) | source |
|---|---|---|---|
| US | 518 (S&P 500 = 503, Nasdaq 100 = 101, overlap 86) | **514** | en.wikipedia.org *List of S&P 500 companies*; api.nasdaq.com nasdaq100 list; fetched 2026-11-18 |
| TH | 100 | **100** | **approximate — replace with official SET100** (see below) |

**TH universe: approximate — replace with official SET100 (left as is, per instruction).** set.or.th is behind bot protection (403) and Wikipedia only lists SET50 ("as of 2025"). The file = 51 SET50 names from Wikipedia + 49 large/liquid SET names I wrote by hand, each verified to have ≥253 Yahoo bars. **Please replace with the official list** (set.or.th → SET100 → constituents) — one name per line. Ratings are percentiles, so a wrong tail shifts TH ratings a little, not wildly.

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

## TH benchmark (resolved)
Rule: use `^SET.BK` if it has ≥ 252 rows, else `TDEX.BK` (SET50 ETF); the one actually used is written to `rs.bench`. On 2026-11-18 Yahoo returned **1 row** for `^SET.BK` (also ^SET50/^SET100/^SETHD) and 483 for `TDEX.BK`, so all TH rows used `TDEX.BK` and now have `line` / `newHigh` / `newHigh5d`. Re-evaluated on every run, so it switches back to `^SET.BK` by itself when Yahoo recovers. Reasons: `bench<252` now only occurs if *both* are short. US bench stays `SPY`.

## Sample ratings (live run, asOf 2026-11-18)
TradingView/IBD column is blank: I can't read TradingView or IBD from here. Please fill from the TradingView RS Rating indicator for a sanity check (the brief says approximate is fine).

| ticker | rating | 4w ago | line | newHigh / 5d | bench | TV/IBD |
|---|---|---|---|---|---|---|
| NVDA | 5 | 70 | down | – / – | SPY | |
| AAPL | 89 | 82 | up | ✔ / ✔ | SPY | |
| MSFT | 67–68 | 86 | flat | – / – | SPY | |
| TSLA | 36 | 46 | up | – / – | SPY | |
| META | 53 | 61 | down | – / – | SPY | |
| PLTR | 35–37 | 94 | down | – / – | SPY | |
| INTC | 15 | 95 | down | – / – | SPY | |
| KO | 85–87 | 86 | up | – / ✔ | SPY | |
| UNH | 66 | 67 | down | – / – | SPY | |
| PTT.BK | 43 | 64 | down | – / – | TDEX.BK | |
| AOT.BK | 59 | 39 | up | – / – | TDEX.BK | |

(Ranges: two live runs minutes apart differed by 1–2 points because Yahoo returned 512 vs 514 usable US symbols — a few universe tickers fail intermittently. Immaterial for a display rating.) The TV/IBD column is still blank — I can't read TradingView/IBD; please fill it in.

## Sanity check — returns, score, rating (now vs 20 sessions ago)
Score = 0.4·r3m + 0.2·r6m + 0.2·r9m + 0.2·r12m. US universe n = 512 (live run 2026-11-18; "−20s" = 2026-10-21, rated against the table as of that day).

| ticker | when | r3m | r6m | r9m | r12m | score | rating |
|---|---|---|---|---|---|---|---|
| INTC | now | −41.4% | −54.6% | +20.9% | +55.4% | −0.122 | **15** |
| INTC | −20s | −7.3% | +42.4% | +71.4% | +144.0% | +0.487 | **95** |
| PLTR | now | −10.5% | +13.5% | +15.4% | −9.1% | −0.002 | **37** |
| PLTR | −20s | +63.5% | +32.2% | +22.0% | +11.1% | +0.385 | **94** |
| MSFT | now | +4.7% | +20.1% | +26.9% | +0.1% | +0.113 | **68** |
| MSFT | −20s | +39.9% | +23.6% | +20.8% | +4.0% | +0.256 | **86** |
| KO | now | +8.6% | +21.3% | +26.2% | +41.9% | +0.213 | **85** |
| KO | −20s | +14.9% | +25.7% | +31.2% | +39.0% | +0.251 | **86** |
| JNJ | now | +3.6% | +21.5% | +13.4% | +41.2% | +0.167 | **80** |
| JNJ | −20s | −0.1% | +15.2% | +20.1% | +36.1% | +0.143 | **72** |

**Why the big jumps are real, not a bug.** The rating is a pure function of the returns above; I checked the arithmetic against raw closes.
- **INTC** closed 92.96 on 2026-10-21 and 53.95 now (−42% in 20 sessions; it was ~127 at its high inside the last 60 sessions). Because the 20-session-ago window anchors on 63/126/189/252 sessions back from a *high*, r3m was only −7% and r6m +42% then; now every anchor is measured from the post-crash price, so r3m −41% and r6m −55%. r3m carries 40% weight, so the score swings from +0.49 to −0.12 and the rank from 95 → 15.
- **PLTR** is the same shape: 201.72 → 155.70 (−23% in 20 sessions) flips r3m from +64% to −10%; score +0.39 → 0.00, rating 94 → 37.
- **MSFT** (r3m +40% → +5%) drops 86 → 68 for the same reason, milder. **KO / JNJ**, with steady multi-month returns, barely move (86→85, 72→80).

Takeaway: the design (40% on 3 months) makes the rating fast — a name that gains or loses ~25–40% in a month can move 50+ points. That matches the IBD-style behaviour; if it's too jumpy for watchlist ordering, lower the 3m weight — a one-line change in `RS_WEIGHTS`.

## Tests
`python3 tests/rs1_selftest.py` → 39 checks OK (weighted score, percentile/ties/clamp, <252 bars → null + reason, TH mapping & bench, RS-line ±2% band, TH bench rule (^SET.BK ≥252 else TDEX.BK, recorded in `bench`), newHigh / newHigh5d, bench gaps, run_rs with fake fetch/write). Added as a step in the proposed workflow. Not added to `run_regression.sh` (not touched).

## For you to do
1. Paste `docs/proposals/prices.yml` over `.github/workflows/prices.yml` (adds Mon–Thu 22:30 UTC cron, selftest step, 20-min timeout; weekend crons kept).
2. Replace `data/universe_th.txt` with the official SET100 (approximate until then).
3. Fill the TV/IBD column.
4. Run the workflow manually once and check `prices/_meta.rsTable` in Firestore.
