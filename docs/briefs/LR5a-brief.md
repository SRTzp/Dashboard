# LR5a · Watch tab (match the mockups) + RS1 display

Branch `claude/lr5a` from main. Then LR5b Journal, LR5c Port (separate briefs).

## Rule (same as LR-F / LR4)
Mockups are the spec: `docs/briefs/lr/Watch.dc.html` (1440) and `WatchPhone.dc.html` (390). Match layout, spacing, type, colours, wording; sample data → live data.
Hooks: never rename or remove an `id`, `data-*`, `name` or inline handler. Restyle, move or wrap only. `hooks_test` superset PASS.
No engine files, no data-job changes. Light only. English UI (translate any Thai left in Watch, its sheets and the detail panel).
Watch is shared by Main and Family (say so in the summary line, as in the mockup).

## Desktop
1. **Header row:** "Watch" · segmented `Momentum n · Compounder n · Ideas n` · summary `n stocks · n need homework · shared by Main and Family` · `Find ticker` search · `+ Add stock`.
2. **Table** (one row per stock, one line each): Stock · Status chip (Holding / Plan ready / No plan / Setup ✓ …, from the existing status logic) · Sector vs SPY (name + RRG arrow, existing data) · **RS** (new, see RS1) · Thesis · homework (Done date + one-line note, or "Not started · adds at 50%" in amber) · Next check · one action button (`Homework ›` / `Open plan ›` / `Make plan ›` black when it's the next step).
3. **Sort and filter** (the user asked for both): a small `Sort ▾` (Default · RS high first · Next check soonest · Homework first) and a `Filter ▾` (All · Holding · Plan ready · No plan · Needs homework), on the summary row. Default order unchanged. Remember the choice per device.
4. **Detail panel** on the right for the selected row: ticker · status · exchange · sector; WHY / TRIGGER / EXIT WHEN (from the living thesis; "Not written yet" in amber); SECTOR VS SPY + RS block (below); one black main action; `⋯` menu holds full thesis, news, archive, delete.
5. **Archived (n)** at the bottom of the table, collapsed. Each archived row: ticker · date · reason · `Restore`. Archive = "stock I stopped watching, kept with its notes"; say that in the empty/collapsed hint.
6. Ideas tab: same table style; columns that don't apply show "—". No new features.

## Phone (390)
Mockup: header "Watch" + `+ Add`; segmented tabs (add `Ideas n` if there are ideas); summary line with Sort/Filter as two small icon buttons; each stock = 2 lines (ticker + status chip / one-line note in amber when homework is missing) + one action button on the right; Archived card with Restore. Tap a row → detail as a bottom sheet (same content as the desktop panel). One line per item, ellipsis, no wrap.

## RS1 display (the UI half of `docs/briefs/RS1-brief.md`)
Data: `prices/{ySym}.rs = {rating, rating4wAgo, line, newHigh, newHigh5d, bench, asOf, reason?}` (already written daily).
- Desktop RS column: `87 ↗` (line up ↗ / flat → / down ↘) + `new high` chip when `newHigh5d`. Missing → `—` with the reason in the tooltip.
- Phone: RS sits at the end of line 2 (`… · RS 87 ↗`).
- Detail panel: `RS 87 ← 72 (4 wks ago) · line ↗ · new high 18 Nov` + `RS chart on TradingView ↗` (existing link). Display only, never a gate.
- Remove any old leftover "RS rating" field the user saw stuck in Watch (it was manual/obsolete); keep its hook hidden if it has one.
- Check that price docs without `close` (watchlist-only tickers) don't break the price listener or show 0 prices anywhere.

## Proof (required)
- `tests/screenshots/lr5a/watch-1440-side.png`, `watch-390-side.png` (mockup | live, fixture with Holding / Plan ready / No plan / missing RS / archived rows), plus `watch-390-sheet-live.png`, `watch-1440-ideas-live.png`.
- `tests/run_tests_lr5a.py` in `run_regression.sh`: sort orders (RS high first puts null last), filter counts, RS text/arrow/new-high/missing, detail content, no Thai in `#tabWatch`, one line per row at 360/390/1440, no overflow.
- `docs/reports/LR5a-summary.md`: remaining differences with a reason each, Watch heights before/after, full `run_regression.sh` 0 failing.
- Commit in parts: A desktop table + panel · B sort/filter + RS · C phone + sheet · D report. Whole-page screenshots: hide the fixed bottom nav so it doesn't land mid-page.
