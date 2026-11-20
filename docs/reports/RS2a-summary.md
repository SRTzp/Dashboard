# RS2a — Ranked RS list (Watch › Screen) · summary (2026-11-20)

Branch `claude/rs2a` (from origin/main f2781d5). Scope: `scripts/build_rs2.py` (new) · `scripts/build_prices.py` (calls it) · `index.html` (Screen view only) · tests · `docs/proposals/prices.yml`. **No engine changes** (risk-engine / re1 / core-size / ps1 / pv1 untouched), **no workflow edit** (proposal only).

## Data numbers (live run against Yahoo + Nasdaq Trader, Mac, 2026-11-20, asOf 2026-11-19 close)
| | |
|---|---|
| Common stocks after symbol-file filtering (NYSE + Nasdaq + NYSE American) | **5,080** |
| **Liquid universe** (close ≥ $10 and 50-day avg $ volume ≥ $10M) | **2,179** (brief expected 1,800–2,200) |
| Rated (≥ 253 bars; the rest are recent IPOs) = rows in the list | 2,120 |
| Runtime, full weekly scan incl. 300 s of sector lookups | **431 s (7.2 min)** — target < 15 min. Daily runs skip the 5,080-symbol scan (only the ~2,179 liquid names) → expect ~4–5 min |
| `rs2/latest` size | **409 KB** with 1,207 of 2,120 sectors filled; ≈ 470 KB when all are filled (limit 900 KB; split into `latest_0..k` of ≤ 500 rows automatically if it ever grows — tested) |
| `rs2/_meta` | asOf, n (liquid), nRated, runAt, runSecs, universeAt, failedChunks, parts, bytes, error, rule · the liquid name list lives in `rs2/_universe` (kept out of `_meta` so the app reads a small doc) |

## 10 ratings sanity check (new liquid-universe table vs the RS1 numbers in RS1-summary, 2026-11-18)
RS1 table was ~512 S&P 500 + Nasdaq 100 names; the new table is 2,120 liquid stocks and one trading day later, so a one-time shift is expected (brief: "note it").
| ticker | RS1 (18 Nov) | RS2a (19 Nov) | 4w ago | line | from high |
|---|---|---|---|---|---|
| NVDA | 5 | 8 | 59 | ↘ | −39% |
| AAPL | 89 | 84 | 79 | ↗ | −2% |
| MSFT | 68 | 71 | 80 | ↗ | −10% |
| TSLA | 36 | 38 | 43 | ↗ | −24% |
| META | 53 | 51 | 43 | → | −23% |
| PLTR | 37 | 41 | 89 | ↘ | −27% |
| INTC | 15 | 30 | 90 | ↘ | −61% |
| KO | 85 | 82 | 83 | ↗ | −3% |
| UNH | 66 | 39 | 67 | ↘ | −24% |
| AVGO | — | 38 | 20 | ↗ | −28% |
Mostly ±5. Big movers: **UNH 66→39, INTC 15→30** (a broader universe has many more small/mid caps that did worse/better than the megacaps; INTC's 12m return is huge so it now sits above more low-cap losers). Not a formula change: `build_rs2` calls the RS1 functions (`rs_table`, `rs_for`) unchanged — selftest checks the list rating equals `rs_for` on the same table, and that `run_rs` rates Watch stocks from the same cuts. Please eyeball a few against TradingView/IBD.

## What changed
- **`scripts/build_rs2.py`**: symbol-file parser (drops ETFs, test issues, non-normal status, warrants, units, rights, preferreds, notes, funds, Arca/BATS; BRK.B → BRK-B), `adv50`/liquidity filter, chunked yfinance download (200/call, sleep, retry once, failed chunk counted and skipped), rows with short keys (`t n e s i r p l h o x xd c v a3 a6 a9 a12`), doc split, sector cache (`rs2/_sectors`, time-budgeted lookups best-rated first — converges over ~2–3 runs), weekly universe refresh (`UNIVERSE_REFRESH_DAYS=6`, `RS2_FULL=1` forces), failure → `_meta.error`, yesterday's doc untouched.
- **`build_prices.py`**: `main()` runs `build_rs2.build()`; the returned liquid-universe table becomes the **US RS table for the Watch ratings** (`run_rs(..., us_table=)`), so one stock = one rating everywhere. If rs2 fails it falls back to `data/universe_us.txt` as before. TH unchanged.
- **UI** (`index.html`): Watch segment **Screen** (4th), `wlView==='screen'`, `rs2*` functions + CSS block (`.rs2-*`). Desktop = table + detail panel + chips; phone = 2-line rows with `+`/`✓`, 50 rows then Show more, `⚲` reveals Avg $vol + Reset. Phone segment labels are now Mom/Comp (mockup).
- Proof: `tests/rs2_selftest.py` (29 offline checks; added to run_regression FAST list), `tests/run_tests_rs2a.py` (104 checks at 1440/390/360 + states: filters, sorts, search, + Watch round-trip, archived, missing data, empty/no doc, split docs), `tests/rs2a_side.py` → `tests/screenshots/rs2a/screen-{1440,390}-side.png` (mockup left | live right).
- Two existing tests updated for the new 4th segment / phone short labels: `run_tests_lr5a` (A header), `run_tests_phase374` (segment counts).

## For you to do (not done by me)
1. Paste `docs/proposals/prices.yml` into `.github/workflows/prices.yml` (adds the rs2 selftest step; timeout 20 → 30 min).
2. **Firestore Rules**: the app reads `users/{uid}/rs2/*` (get on `_meta`, `latest`, `latest_i`). If your rules only list known sub-collections, add `match /users/{uid}/rs2/{doc} { allow read: if request.auth.uid == uid; }`. Without it Screen shows "Could not load the ranked list (…permission-denied) · Retry".
3. First Action run: the weekly full scan has only been run from my Mac. Check Actions log for `rs2: liquid …` and `_meta.error`.

## Doubts / decisions I made unattended
- **Earnings column**: the mockup has it, the brief's column list doesn't, and there is no cheap bulk earnings-date source. It shows a date only for stocks already on Watch (next check / thesis catalyst, amber when ≤ 7 days) and `—` otherwise. Say if you want a real earnings feed (per-ticker yfinance calendar calls are too slow for 2k names) or the column dropped.
- **Filter UI**: brief says one `Filter ▾`; the mockup has chips (RS · distance · new high · sector · $vol · Reset) — I followed the mockup. Sort has 5 options (Near high + RS default, RS high first, Closest to high, Biggest RS gain, Avg $vol). Filters + sort persist in localStorage (`dash.rs2`).
- **RS options** include "Any RS"/"Any distance" in addition to 70/80/90 and 10/15/25 so you can see everything.
- **New-high chip** uses the same rule as Watch (new high within the last 5 sessions).
- **Universe edge cases**: ADRs / foreign ordinary shares are included (they're US-listed common-equivalents); anything with "Fund", "Trust … Preferred", "Acquisition Corp", rights/warrants/units/notes in the name is dropped. Class shares appear as `BRK-B` (Yahoo form); + Watch stores that ticker as-is so prices work.
- **History** is 410 calendar days (~280 sessions) rather than exactly "13 months" — 13 months is ~273 sessions, too tight for the 4-weeks-ago rating (needs 273).
- **Weekly universe refresh**: daily runs reuse `rs2/_universe`; a stock that becomes liquid mid-week appears at the next weekly scan (names that fall below the filter drop out immediately).
- Sector lookups are cached; the first 2–3 runs fill the sector column progressively (rows without a sector show "—" in the Sector column and are skipped by the sector filter).
- Real-Firestore behaviour (rules, 1 MiB doc limit, GitHub runner speed/rate limits) is untested here; only the in-memory mock + Yahoo from a Mac were exercised.
- Phone detail: the mockup has no phone detail panel, so tapping a row does nothing on phone (the `+` is the action).

## Regression
Full `bash tests/run_regression.sh`: see the final line appended below.

**Full `run_regression.sh` (after updating the two segment tests): 69/70 ok, 1164 s.** hooks superset PASS · rs2 selftest PASS · run_tests_rs2a 104/104 PASS. The one failure, `run_tests_lr2`, crashed with `Cannot read properties of null (reading 'click')` on the Today screen under 4-way parallel load; run alone it passes (150 checks, 0 failing), and it passed in the earlier full run (68/70, whose only 2 failures were the segment-count tests I then updated). Not a clean 70/70 in a single run — I did not spend a third 20-minute run on it; re-run `JOBS=2 bash tests/run_regression.sh` if you want that proof.
