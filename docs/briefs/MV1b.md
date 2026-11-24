# MV1b — same branch claude/mv1 (fix-ups + part D you missed)

The brief got a part D after you started (`~/Documents/Dashboard/briefs/MV1-brief.md`, section "D · + Add stock"). Do it now on the same branch, plus these decisions. UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md` (copy into docs/briefs/ in your first commit).

1. **Part D** exactly as written in the brief (typed tickers + .csv upload in the + Add stock sheet; .txt path unchanged). Ask SRTp for a real TradingView Screener CSV before finishing D and use it as `tests/fixtures/tv-screener.csv`.
2. **Dark buttons (decision):** the header `＋ New plan` = its own area, keep it. Screen `+ Add to Watch` and Homework `Save · mark done` = one per area, keep. Fix only the Watch list: on desktop (≥ 1100, panel visible) the row `Make plan ›` becomes white, so the dark one is only in the panel. Phone list (no panel) keeps it dark.
3. **iPhone Screen line 2** (same layout, no new row): use the same short name you made for the tooltip (`Celestica · Tech`, not `Celestica Inc. Common Shares · Tech…`). Wrap rather than "…".
4. Test PNGs: `mv1-add-typed`, `mv1-add-csv` (1440 + 390), `mv1-dark-watch` (1440, GE row white), `mv1-screen-390` again.

Then one full `JOBS=2 bash tests/run_regression.sh` + hooks, only `mv1-*.png` in the diff, no push. Report tests and PNGs.
