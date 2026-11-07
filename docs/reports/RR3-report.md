# RR3 report — Flow › Leadership header + "sector list missing"

## §0 Bug: could NOT reproduce on origin/main (fc85d0c)
Tried with a Playwright fixture (23 rows, fake timers, mocked batches), through batch 1→2→3:
- current-model rows, old-model rows (all "waiting"), Daily and Weekly, Fresh ON and OFF: **the list kept all 23 rows at every batch**; the header breadth moved 12→15→19→23/23 as expected. No console errors.
- Code reading: `rrgRun` never clears `rowsD/rowsW` (it merges per batch); `ffState()` only resets `loading`, not rows. Nothing filters rows to 0 while `r.loading`.
- Most plausible cause of the screenshot, unproven: **Fresh filter ON** (persisted in localStorage `rrgFreshOnly`) + Weekly or a quiet day → list becomes just "Nothing fresh right now." with no way back except the small All button — reads as "list gone" while the header still shows 16/23. Also possible: a stale WK1/TX1 working copy (brief said not to test there).
Decision: since no root cause is provable, apply defensive fixes that match the brief's rule ("never an empty list while refreshing"):
1. `rrgLastGood[tf]`: if live rows for the timeframe are empty while `r.loading`, render the last good rows instead.
2. List is dimmed (opacity .6, `.rrgDim`) while loading.
3. Fresh-empty message now has a **Show all** button.
If you see it again, check localStorage `rrgFreshOnly` first, and tell me the tf + whether "Nothing fresh right now." was visible.

## §1 Layout (decisions)
- `#ffThemesPanel` is now a CSS grid; `#ffRrgBar` is `display:contents` and renders two blocks: `.rrgCtl` (controls) and `.rrgStatus` (one muted line). Keeps `#ffRrgBar` selectors/text for old tests.
- ≥900px: title + score (left) | `[All|Fresh n] [Daily|Weekly] ⧉ ↻` (right) on one row; status full-width beneath. The long grey caption above "Leadership" is now single-line ellipsis so the row stays compact (the panel is only ~550px wide at 1440, so this was needed to avoid overlap). Score font reduced to .8rem in this header for the same reason.
- <900px: row 1 title+score, row 2 controls (space-between, no wrap), row 3 status.
- ↻ = 32×28 icon like ⧉, tooltip "Refresh prices · rrg v7 · build check"; spins and is disabled while loading. "rrg v7" lives only in the ⧉/↻ tooltips.
- App has no real dark theme (only a few `prefers-color-scheme` rules), so dark shots equal light; kept for completeness.

## Tests
- New `tests/rr3_check.py` — 20/20 (data through 3 batches, tf/Fresh switches mid-run, last-good fallback, Fresh-empty Show all, 1440 + 390 geometry, loading state). Shots in `docs/shots/rr3/`.
- Related: rrg1_check 26/26, rrg1b_check 31/31, rrg1c_check 9/9, phase86 51/51 (after retiring one expectation → `tests/RR3_retired.md`), phase122 exit 0.
- Not mine, fail identically on origin/main: phase105 (IGV `.l2 .g` locator timeout), phase110 (missing `index.backup-pre-SET1.html`).

Compare / draft PR: https://github.com/SRTzp/Dashboard/compare/main...claude/rr3?expand=1
