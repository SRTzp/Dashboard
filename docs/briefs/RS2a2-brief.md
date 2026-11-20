# RS2a2 · Screen polish: market cap, column sort, tab moves, compact add

Decided by SRTp 20 Nov 2026. Small follow-up to RS2a (merged). Build before HW1. No new mockup: start from `ScreenRS.dc.html` / `ScreenRSPhone.dc.html` and apply the changes below; list the differences in the summary.

## 1. Market cap replaces Price
- Data: weekly cached lookup (same pattern as `rs2/_earn`, e.g. `rs2/_mc`) for all liquid names; row key `mc` (USD). Use yfinance `fast_info` market cap, or shares × last close. Missing → `—`. The daily run must not get slower (reuse the cache).
- Desktop column `M.Cap` in Price's place, format `$4.2B` / `$860M` / `$1.3T`. Price moves to the detail panel line (`Price 182.40 · M.Cap $4.4T · Avg $vol …`).
- Phone: no new column; add M.Cap to the detail sheet only.
- Filter ▾: add `Min M.Cap` (off by default).

## 2. Sort by column header (desktop)
- Clickable headers: RS · from high (sort by RS; second click flips) · % from high (if the cell has its own sort target, else part of the RS header) · M.Cap · Avg $vol · Earnings (soonest first).
- Active header shows ▲/▼; clicking one sets the `Sort ▾` dropdown to the same choice. `Near high + RS` stays the default and the phone's only control. Remember the choice (localStorage), Reset clears it.

## 3. Moving between Watch segments
- Mac/keyboard: the existing Tab shortcut (today Momentum ⇄ Compounder, `wl1TrkToggle`) now cycles Momentum → Compounder → Ideas → Screen → Momentum; Shift+Tab goes back. Same guards as today (not while typing, not with a sheet/menu open: `wl1Blocked`).
- Phone: horizontal swipe on the list area (≥ 60px, mostly horizontal) moves to the next/previous segment. Not on buttons, inputs or a horizontally scrollable element.

## 4. Compact add + choose the list
- Row button becomes a compact `+` (44px tap target on phone, small square on desktop) → adds to **Momentum** as No plan, then shows `✓` in the same row (no navigation). Watching rows show `✓` (muted). Keep the `+ Watch` hooks on the new button.
- Detail panel/sheet: `Add to: [Momentum] [Compounder]` (segmented, Momentum preselected) above `+ Add to Watch`. Compounder adds with the same track field Edit uses. `it.src` saved as today.
- Already watching → detail shows `On Watch · Momentum ✓` (or Compounder).

## Proof
- `run_tests_rs2a.py` extended (or `run_tests_rs2a2.py`): M.Cap format + missing, header sort both ways + dropdown sync, Tab cycle 4 + Shift+Tab + guard while typing, swipe next/prev + ignored on buttons, `+` → `✓` without navigation, Compounder add from detail, 360/390/1440 no overflow.
- Selftest: M.Cap cache (fresh/stale/missing).
- Side-by-side PNGs (`tests/screenshots/rs2a2/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh`.
- Update `docs/reports/RS2a-summary.md` (RS2a2 section): M.Cap coverage %, runtime change, mockup differences.
- If the workflow file needs a change, put it in `docs/proposals/prices.yml` again and say so.
