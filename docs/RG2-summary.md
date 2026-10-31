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
