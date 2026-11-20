# RS2a — Ranked RS list (Watch › Screen) · summary (updated 2026-11-20 for the final brief)

Branch `claude/rs2a`. First pass was built from the old brief; **RS2a-fix** re-copied the 20 Nov brief + mockups (Leaders / Emerging / Pullback) and implemented the delta. Scope: `scripts/build_rs2.py` · `scripts/build_prices.py` · `index.html` (Screen view + a `src` field on watchlist items) · tests · `docs/proposals/prices.yml`. **No engine changes, no workflow edit.**

## Data numbers (live run, Mac, 2026-11-20 — weekly full path with the whole-market table)
| | |
|---|---|
| Common stocks after symbol-file filtering | 5,080 |
| Liquid universe (close ≥ $10 · 50-day avg $vol ≥ $10M) | **2,179** · rated / in the list: **2,120** |
| Whole-market table (`rs2/_meta.cuts`, `cuts4w`, `cuts3m`, `cuts1m`) | **n = 3,620** = 2,120 liquid + **1,500 random non-liquid** (seed `2026-W47`), `cutsStale: false`, 100% of symbols downloaded |
| Runtime | **462 s** (7.7 min) incl. sector/earnings lookups (target < 15 min) |
| `rs2/latest` | **434 KB** (≈ 500 KB when sectors/earnings are filled; limit 900 KB, auto-split tested) |
| Preset sizes on the live data | Leaders 376 · Emerging 31 · Pullback 27 |

## Old vs new ratings, same 10 tickers (old = liquid-only table, 19 Nov · new = whole-market table, 20 Nov run)
Whole-market grading is easier than liquid-only (the 1,500 sampled non-liquid names are mostly weaker), so ratings rise by ~5–15 once — expected ("ratings will shift once").
| ticker | old 12M | new 12M | new 3M | new 1M |
|---|---|---|---|---|
| NVDA | 8 | 24 | 22 | 9 |
| AAPL | 84 | 86 | 92 | 71 |
| MSFT | 71 | 76 | 81 | 46 |
| TSLA | 38 | 51 | 81 | 55 |
| META | 51 | 60 | 88 | 30 |
| PLTR | 41 | 53 | 43 | 17 |
| INTC | 30 | 44 | 17 | 6 |
| KO | 82 | 85 | 85 | 77 |
| UNH | 39 | 52 | 43 | 21 |
| AVGO | 38 | 51 | 62 | 74 |
(Part of the move is also one extra trading day.) The formula is untouched; Watch ratings use the same stored table (`run_rs(..., us_table=)`).

## Delta implemented
1. **Weekly whole-market table**: weekly full run scores liquid + a seeded random 1,500 non-liquid names (≥ 252 bars) → `_meta.cuts/cuts4w/cuts3m/cuts1m` (+ `cutsN`, `sample`, `seed`, `asOf`). Daily runs map scores with the stored table. < 80% of requested symbols downloaded → keep last table + `cutsStale`; no stored table yet → liquid+sample table still flagged stale. **Stooq reader** (`parse_stooq_csv`, `_stooq_fetch_chunk`) behind `RS2_SOURCE=stooq`, off; **not needed — Yahoo worked** (it was not tested against the live Stooq service; Stooq prices are unadjusted).
2. **`m3` / `m1` per row** = 3-month and 1-month RS ratings (return ranked on the same table method, own cut-offs). `r` = 12M rating, `p` = rating 4 weeks ago (kept in data, no longer shown on Screen).
3. **UI**: segmented presets Leaders (default) / Emerging / Pullback (thresholds in `RS2_PRESET_DEFAULTS`, overridable via localStorage `dash.rs2Presets`; the job's `PRESETS` mirror them); `Filter ▾` panel = RS min · % from high · new high only · sector · min $vol (button shows the count) + Reset; RS 4W column removed; conditional **3M · 1M** column (Emerging/Pullback only); phone line 2 ends `3M 94 · 1M 88` in those presets; detail line `12M x · 3M y · 1M z` with falling values amber (≥ 30-point fall red).
4. **Earnings**: weekly cached lookup (`rs2/_earn`) for names matching any preset (cap 300, best RS first); row key `nx`; "in Nd" amber ≤ 7 days; names not looked up fall back to a Watch next-check date, else "—".
5. **`+ Watch`** saves `it.src = {from:'screen', preset, r12, r3, r1, at}` (watchlist items now carry `src` through the snapshot mapping).

## Tests / proof
`tests/rs2_selftest.py` 53 offline checks (cut-offs from a known synthetic set, clamp, 1M/3M ratings, sample determinism, stale-table path ×4, symbol conversion, Stooq CSV, earnings cache, miss guard) · `tests/run_tests_rs2a.py` 134 checks at 1440/390/360 (presets, Filter panel, new column, phone line 2, detail colours, `src`, thresholds override, states, split docs) · side-by-side PNGs `tests/screenshots/rs2a/screen-{1440,390}-side.png` (force-added) · hooks superset PASS.
Updated existing tests only for the 4th segment / phone labels (`run_tests_lr5a`, `run_tests_phase374`).

## For you to do (not done by me)
1. Paste `docs/proposals/prices.yml` into `.github/workflows/prices.yml` (adds the rs2 selftest step; timeout 20 → 30 min).
2. **Firestore Rules**: the app reads `users/{uid}/rs2/*` (get on `_meta`, `latest`, `latest_i`). If your rules only list known sub-collections, add `match /users/{uid}/rs2/{doc} { allow read: if request.auth.uid == uid; }`. Without it Screen shows "Could not load the ranked list (…permission-denied) · Retry".
3. First Action run: the weekly full scan has only been run from my Mac. Check Actions log for `rs2: liquid …` and `_meta.error`.

## Doubts / things to know
- **Yahoo throttled the per-ticker endpoints right after the bulk download** (HTTP 429 / "Invalid Crumb"): on the live run **0 of 300 earnings lookups returned a date** and the sector cache stayed small. The earnings path is unit-tested but **not proven live**. Misses are no longer cached and the job stops a lookup loop after 30 misses in a row; on the GitHub runner (different IP, weekly schedule) it may behave better. If not, a separate small earnings job / another source is the fix. Until then the Earnings column is "—" except stocks on Watch (next check date).
- Sector column fills progressively; rows without a sector show "—".
- The weekly scan still downloads every symbol (it needs prices to know who is liquid); the 1,500 sample is drawn from the non-liquid names that downloaded with ≥ 252 bars. The "80% download" rule is therefore applied to all requested symbols, not only the sample.
- A past earnings date is hidden (shows "—").
- Filter is an inline panel below the presets (not a popover) — works the same on phone via ⚲.
- Real Firestore (rules, doc limits) and the GitHub runner are still untested.


**Final: `JOBS=2 bash tests/run_regression.sh` → 70/70 ok, 0 failing, 2124 s** (hooks superset PASS · rs2 selftest PASS · run_tests_rs2a 134/134).
