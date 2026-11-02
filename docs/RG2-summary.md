# RG2 summary (RG2a + RG2b) — read this first

Repo: SRTzp/Dashboard. RG2a = PR #4 (merged to main). RG2b = PR #5 (Draft, branch `claude/rg2b`, not merged).
Brief (not in main): branch `claude/rg2-brief`, file `docs/briefs/RG2-brief.md`.
App = single file `index.html` (~25k lines; do NOT read whole — grep function names) + `core-size.js` (pure sizing lib; edit it, then `python3 tools/sync_core_size.py`, check with `--check` and `node tests/core_size_test.js`).
Tests: `tests/run_tests_phase*.py` (Playwright + mock Firebase), full run `tests/runall2.sh`. Do not commit `index.backup-pre-*.html`. Ladder rules (#21) are NOT implemented on purpose.

## RG2a (Run 1, merged)
- `scripts/build_fundflow.py`: raw closes; ACWI_BIL + HYG_IEI daily with two EMA pairs — Winner EMA20/50 (top level), Ladder EMA50/100 (`slow`); `"ver":2`; retry for missing symbols.
- App: `ffPoolFactor(pool)` factor per pool (both green 100 / one red 75 / both red 50, size only, no bans); stale data keeps last factor + red "N business days old" bar; Today verdict line (Risk-ON / Caution / Mixed / Risk-OFF, `W 75 · L 100` under 340px).
- Freshness tags only when stale + "Data freshness" panel (Settings, App card).
- Journal by bucket (Winner / Ladder / Sat Main / Sat Tactical; Ladder = trades linked to cards `strategy==='L'`), planned vs actual R, stop respected.
- Sector link: XLK XLI XLY XLP XLRE added to RRG; watchlist `sector_etf`, badge, "Hot sector first".
- Tests: phase112 182 pass. Log: `tests/RG2a_retired.md`, report `docs/reports/RG2a-verify.txt`.

## RG2b (Run 2, PR #5)
- Pools: `settings.pools {winner,ladder,sat}` default 50/30/20 of (capital.core ฿ + capital.satB $×fx); derived at read time; one-time migration (`poolsMigrate`), over-limit positions → warning only. Seed: main ฿4.04M → W 2.02M / L 1.21M / S 0.81M.
- Winner: one per-stock cap = 25% of Winner pool; removed gate, Tier A/B table, Layer-2 cap, total cap, ladder share (stored keys kept, ignored).
- Ladder: own page (`#ladderPanel`), budget 5% of account × Ladder factor, free cash independent of Winner, states Base / Sideways-Up / Broken. `canPlaceLadder` reasons: TIER_B, NOT_FORTRESS, BAD_LADDER, STOCK_OVER, NO_CASH.
- Sat: whole-pool sizing; RPT Main [0.5..2] default 1.5, Tactical [0.25..1] default 0.75; caps 1.4× / 1.2×; brake DD 3% (old values migrated ×0.7/×0.3 once, `satV2.poolMig`); max 4 new trades/week (Main+Tactical); no Macro size × (MR keeps 0.6).
- Port: one line `Winner a/b · Ladder a/b · Sat a/b` + collapsed bars.
- §4.7: Today Core panel lines `Winner x% · used y%` / `Ladder x% · used y%` (`W x% · y%` ≤340px); DD brakes per pool (winner / ladder / sat); paused legacy Core DD → both pools start paused + one-time note; goals Winner / Ladder / Sat (+Option).
- UI feedback: Plan scope buttons Winner|Ladder|Sat always buttons (in-page below 430px); Ladder shortcut = D; W/L selector and W→L convert removed; per-stock Track Winner/Ladder (promote form, watchlist chips, restrictions, defaults).
- Key code names to grep: `poolsOf`, `poolsMigrate`, `satV2Cfg`, `satV2Money`, `ddEval`, `ddSync`, `td3PoolLinesHtml`, `ldrHtml`, `ldrCardHtml`, `renderLadderPanel`, `wlTrackOf`, `coreCanPlace`, `poolsPortHtml`.

## Test status (RG2b, cloud)
- core_size_test 502/502; sync --check OK; phase113 336/0.
- Full suite 114 suites: 77 green; other 37 fail identically on main, or crash on missing Mac-only files (index.backup-pre-*, core-size.backup-pre-*, P2-prices-upload), or date artifact (p27 p30 p34 p36 — Thai Sunday rollover; same on main).
- Old-test changes (expected values only) logged in `tests/RG2b_retired.md` (large, don't read; grep a suite name). Report: `docs/reports/RG2b-verify.txt`.
- Known always-failing: p13 (always), p3 (Sundays), p6 (day 20). Run date-sensitive suites on a weekday.

## Not verified
Real Mac run, real Firestore, per-pool DD on real history (seed only), weekday re-run of date-sensitive suites.

## FINAL STATUS (Mac, 2026-11-02) — read this, it overrides "Test status" above
Regression work is closed. Branch `claude/rg2b` (PR #5, Draft) is pushed; latest commit `55329b4`.

### What was done (all on the Mac, ~/Dashboard-rg2b)
- Fixed the 13 regression suites by changing **expected values only** (nothing weakened silently; every change logged in `tests/RG2b_retired.md`): p25 p53 p54 p55 p56 p64 p65 p79 p108 p110 p14 p66, plus p113 (passes 335/335 on the Mac, no change needed).
- p110 was NOT an app bug: Sat pool = 20% of (core + satB×fx), so clearing satB alone leaves a pool; the test now clears core too.
- One real app fix found while doing p66: the "max per stock" (`sCrWinCap`) range error did not appear in the settings summary box (label map lacked it) → added in `index.html`.
- p54/p55: first fix had old/new swapped; corrected (new app = 0.5 lot, old backup = 0.32).
- **p26 (decision: option 1)**: the Core-page ladder form (5 gates, `#cnStratL`, W↔L convert) is gone, so the sections tied to it were retired, not rewritten. Not called in `main()`: `ladder_checks`, `gate_checks`, `behave_checks` (functions kept as evidence). 41 individual checks turned into `removed(...)` (prints `REMOVED -`, not counted pass/fail): wl_checks B8/B9/B10, tier_checks D20, fix_checks fix2, regress_checks E26 (10 checks comparing head numbers with the old backup). Remaining expectations updated (core-size 35 hunks, core_size_test 502, D19, fix1). Result: p26 = 36 pass / 0 fail. New ladder page is covered by p113. E26 could be re-done as real-value checks later (not required).

### Full suite vs main (both run with tests/runall2.sh on the Mac; main = b6df185 in ~/Dashboard-main)
| Suite | main | branch |
|---|---|---|
| p14 | fail 4 | pass 195 |
| p66 | fail 2 (S2 missing backup file + 1) | fail 1 (S2 only), pass 42 |
| p23 | fail 2 | fail 1 (sync_core_size check, also fails on main) |
| p5 p13 p41–p47 p75 p80 p81 | fail | fail, identical counts |
| p26 | fail 3 (of 245) | was crashing on branch → now 36/0 after retirement (see above) |
| all others | pass | pass |
Branch full run (before the p26/p66 fixes): 99 pass / 15 fail; every remaining fail is the same as main except p26 (fixed since). Date-sensitive suites p3 p27 p30 p34 p36 all pass (run on a Monday).

### Known-failing on both main and branch (not RG2b)
p5 p13 (known false failure) p23 (sync_core_size check) p41–p47 p75 p80 p81, p66 S2 (missing `index.backup-pre-POL1.html` + `tests/_bk_pol1/`).

### Not verified / caveats
- Full suite was NOT re-run after the last commits (p66 fix, p26 retirement); only the touched suites were re-run individually (p26 36/0, p66 42/1, p65, p113). Owner decided this was acceptable.
- Real Firestore, per-pool DD on real history (seed data only) still unverified.
- Do not commit `index.backup-pre-*.html`. Ladder rules (#21) are intentionally not implemented.
- Next: mark PR #5 ready for review / merge when the owner decides.
