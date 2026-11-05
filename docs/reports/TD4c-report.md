# TD4c report — Today/Watch interaction polish

Start sha `7ef3d7fec118…` (verified). Backups: `index.backup-pre-TD4c2.html`; `tests/_bk_td4c/` (all top-level tests files; **excluded** `tests/screenshots/` and older `tests/_bk_*` dirs — a first attempt with `cp -R tests/.` recursed into itself, was stopped and moved to `_to_delete/_bk_td4c_bad_*`).

## Causes
- **Sector metrics missing:** `tdSectorsHtml` read `sdCur()`, which returns "invalid" unless the RRG cache day == today. Any older cache → `—`. Also the metrics sat inline on the left. Fix: new `sdCurShow()` (latest cache for the tf, `stale` flag); `sdCur` (used by Revisit) untouched.
- **AVGO still showing:** the homework pool (`tdHomeworkCandidates`) had no completeness test, and parts were read only from the daily homework log — an imported living-thesis was never counted.

## Completeness rule (`tdHwThesisParts / tdHwMerge / tdHwComplete`)
Parts = saved homework ticks ∪ imported thesis ∪ Tier. Tier = watchlist `tier` A/B · Business = `sections.s1.md` · Why = `s2.md` · Monitor = kpi/gaps/`s3.md` · Exit = tripwires/`s4.md`. Complete tickers are skipped as auto-pick, Change, and Next from Watchlist (`cmp` flag). A chosen pick that is complete counts as done (so Next is offered). Incomplete shows `Thesis k/5 · Missing: Monitor · Exit`.

## Done
1. Sectors: single `Sectors · Daily` header; right block `LEADING · 2 d · -1.2%` + ↗ pill (same helpers as Flow); stale → values + `as of 29 Sep`; no cache → `—` + `Open Flow to refresh ›`; no fetch, no Revisit from stale.
2. Watch stars: 3 buttons, tap n = n, tap same again = 0, ≥32px.
3. Cand→WL: whole collapsed row toggles (role=button, aria-expanded, Enter/Space, hover/active); form outside row so no bubbling.
4. Satellite cards: whole card triggers its link; buttons stay; Not-trading not clickable.
5. Deep dive: above; scroll jump fixed generically in `todayRefresh` (save/restore scrollY around re-render), covers Change, US/TH, Next batch, Screen. No `href="#"` found.
5b. Macro row: `4d ago` muted; due (>30d, existing `pbStaleInfo`) → amber `34d ago · Re-check ›` → Flow, Macro open + scrolled. Risk chip on Satellite header row (`Risk ✓` / `⚠ worst · +n ›`), DD Core chip on Core header only when hit; tap → sheet (bottom on phone, centred ≥900px) with `tdNumsHtml(M, true)` (identical table, test-verified).
Other double headers: none found (`td3-sh` was only used for Sectors; now unused).

## Decisions
- Stage label uses app words `Reduce / Pause / Recover` (no "S1" exists in app). Colour: pause/over = red, else amber.
- FF gate item follows the old `okWords` rule (flag when gate is *open*, text `FF gate open`) instead of brief's "closed" — no new logic; Sat chip also includes heat/Open Risk, new-trade-full and L2 items.
- Sat chip omits DD Core (Core has its own chip).
- Macro row opens Flow/Macro only when due; otherwise just switches tab as before.

## Files changed
`index.html` (+136/−29), `tests/run_tests_phase109.py` (new, 165 checks), `tests/run_tests_phase107.py` (stars expectation), `tests/run_tests_phase105.py` (stale-cache expectation), `tests/runall2.sh` (→109), `tests/make_verify.sh` (`BK_OVERRIDE`), `tests/TD4c_retired.md` (2 entries), `docs/reports/TD4c-verify.txt`.

## Results
Last index.html edit: 29 Oct 14:25:21 · full run ended 16:19:04. After that only test files changed (p105, p109 expectations); those two suites re-run solo and pass (p109 165/165). Final: 108/110 ok; fails = known p5 (Break Price) and p13. Syntax OK · core_size 471/471 · sync OK.
Scroll probe note: Cand→WL market toggle shortens the page near its bottom, so the test allows clamping to max scroll.

## Screenshots opened
td4c-today-390 (re-opened after final), today-1440, sectors-390, watch-stars-390, deepdive-390, risk-390, risk-table-390.

## Limitations
- Backup of tests excludes screenshots/older backups. Screenshots 390 for sectors show the no-driver fixture.
- Firestore rules untouched · no push · no deletions (temp in `_to_delete/`).
