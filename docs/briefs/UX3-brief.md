# UX3 — Resizable splits everywhere it makes sense · import null fix · RR4 (RRG data from the job) · CR1 (backup price run)

Branch from fresh origin/main. Read `claude/uiux-concept.md` (11 rules; rule 11 iPhone). One worktree, but keep the 4 parts in 4 separate commits (A–D) so any one can be reverted.

## A · Drag-to-resize on every page-level 2-column layout (≥ 1100px only)
Reuse the NT2c helper `splitInit(handle, {key, def, min, max, minOther})` — same handle look/behaviour as Today and Watch › Ideas (invisible until hover, ←/→, Home/End, Enter / double-click = reset, saved per device in localStorage, hidden < 1100px, phone layout unchanged).
Add it to exactly these 3 layouts (all other 2-column grids are inner content — forms, tiles, KV rows — and stay fixed):
1. **Watch › Momentum / Compounder** list | detail (`.wlm`, today 300px / 355px lean + 1fr): key `wl.listW`, default = current width, list 280–480, detail ≥ 640.
2. **Watch › Homework full page**: Fact Sheet (left) | Your thesis (right): key `hw.factsW`, default = current split, each side ≥ 420px; when the window is too narrow for both minimums, keep today's behaviour (no handle).
3. **Watch › Screen** table | stock panel (right, ~280px): key `rs2.sideW`, panel 260–420, table ≥ 700 (table columns must not get cut; extra width goes to the table).
Rules: content never cut with "…", no horizontal page scroll at any allowed width, tables keep all columns (scroll inside the table only if it already does today). Screenshots at 1440: each page at min, default, max (9 PNGs, `ux3-split-*`), plus one 390 shot per page proving phone unchanged.

## B · Import: optional top-level text fields may be null
Bug (SRTp 24 Nov): a `living-thesis@1` file in `facts` mode had top-level `"asOf": null` → "Field asOf must be string … nothing saved". In the importer (`IMP_LT_SPEC` / validator ~19139–19166): for OPTIONAL top-level text fields (`asOf`, `basis`, `audit`, `market`, `name`, `mode`, `date` where optional), treat `null` or missing as "no value" — skip, do not reject the file. Required fields stay strict. When `asOf` is empty and `facts.date` exists, show the Fact Sheet date as before. Test: the attached GOOGL facts file (null asOf) imports; a file with `asOf: 5` (number) is still rejected with the same message.

## C · RR4 — RRG tails load instantly (data from the scheduled job)
Today the browser fetches ~1,200 daily bars for 24 ETFs (RRG_SYMS + SPY) from Twelve Data in batches of 8 with 61 s cool-downs → ≥ 2 min on the first open each day per device.
- In the `prices` job (`scripts/build_prices.py`, yfinance): also download daily OHLC for `RRG_SYMS` + `RRG_BENCH` (same symbol list — read it from one shared place or keep a mirrored list with a selftest that they match) with enough history for `RRG_CFG.bars`, and write `users/{uid}/rrg/bars` (close + high per symbol, dates, `asOf`). Keep size well under Firestore's 1 MB per doc (split per symbol if needed).
- In the app: on Flow open, if `rrg/bars` is ≤ 1 trading day old, build the rows with the EXISTING `rrgCompute` from those bars — no Twelve Data call, tails draw immediately. Status line: `Daily · Data as of <date> · from the 05:30 job`.
- Fallback unchanged: data older than 1 trading day, missing, or the user presses Refresh → current Twelve Data path.
- Guard: same results — a test feeds identical bars through both paths and compares quadrant + tail points.
- No visual change except the status line. Screenshot `ux3-rrg-instant` (1440 + 390).

## D · CR1 — scheduled price run that does not silently miss
Context: SRTp saw no 05:30 Tuesday run (24 Nov). GitHub delays/skips cron at busy minutes.
- `prices.yml`: move cron off :00/:30 (e.g. 22:17 UTC Mon–Thu, 23:17 UTC Fri/Sat) and add a backup run ~1h later (e.g. 00:13 UTC) every day.
- `build_prices.py`: at start, read `rs2/_meta.asOf` (and the new `rrg/bars.asOf`); if both already equal the latest completed US session → print "already fresh" and exit 0 within seconds. Otherwise run normally.
- App: on Today (Daily view, one line in the status card area, amber, only when stale) `⚠ Screen data from <date> · Refresh ›` when the newest data is more than 1 completed US session old; link opens the GitHub Actions `prices` workflow page in a new tab. Same check drives a small `stale` note on the Screen header (already exists — reuse). iPhone: same line wraps, no "…".
- Test the freshness function with a calendar fixture (weekends, US holidays → no false stale).

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks after the last change · only `ux3-*.png` in the diff (revert tracked screenshot rewrites) · new suite `tests/run_tests_ux3.py` in REST= · Python selftests for B-job changes (`tests/rs2_selftest.py` or new `rr4_selftest.py`) also run in the workflow. No push — report tests, judgment calls, PNG list.
