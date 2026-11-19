# AU1 · Phase B summary — one sizing engine

Branch `claude/au1-b` (pushed after every batch). Every size, risk, lot, heat and drawdown number on screen now comes from RE1 (`risk-engine.js` + `re1-adapter.js` + `pos-view.js`). RE1 POLICY values were not touched.

## Numbers

| | before (origin/main `bf8449f`) | after |
|---|---|---|
| `index.html` lines | 33,912 | 30,169 (**−3,743**) |
| top-level functions in `index.html` | 2,699 | 2,432 (**−270 removed, +3 added**: `wrongSideOf`, `coreAddRe1`, `satV1CopyToV2`) |
| `core-size.js` (and its inline copy) | 560 lines | 61 lines — `poolSplit`, `poolFree`, `status` only |
| `tests/core_size_test.js` | 737 lines | 54 lines (25 checks, same three functions + "the sizing functions are gone") |
| `Calc.*` methods deleted | — | `satLot`, `pctLoss`, `heat`, `newCount`, `readiness`, `mrCheck`, `riskBudget`, `sizeRule`, `rr` |
| `CoreSize.*` deleted | — | `firstLot`, `addLot`, `ladder`, `ladderBudget`, `applyStopMove`, `layer2`, `vsCost`, `emergencyStop`, `classifyTier`, `tierBadge`, `ddStep` (+ `dd*` helpers), `openGate`, `canPlaceLadder`, `portfolioSplit`, `ladderShare`, `accountDrop`, `floorLot` |

Functions removed by family: `core*` 86 · `satV3*` 80 · `lf*` 35 · `pf*` 16 · `sat7d*` 13 · `cs*` 12 · `satV2*` 9 · `satPyr*` 8 · `ln1*` 6 · `ln2*` 1 · other 4 (`ddCfgFix`, `wlTierStale`, `ffDeployCap`, `brokerName`). Full list: `git diff origin/main -- index.html | grep '^-function'`.

## What moved to RE1 (and what changed on screen)

| Item | Was | Now |
|---|---|---|
| Add-on size (board "Add-on ›", `coreBuyAddOpen`) | `coreSimCalc` → `CoreSize.addLot`. **It read an empty simulator field, so the button silently did nothing.** | `coreAddRe1` → `ps1AddCalc` → `Re1Adapter.sizeMomentum / sizeComp`; a block reason is shown as a toast |
| Record buy #1 for a card without a PS1 plan (`coreBuy1Open`) | `coreFirstLotCalc` → `CoreSize.firstLot` | `re1CardModel` quantity (allowed qty when blocked) |
| Watch "planned qty" for cards without PS1 rows | `coreFirstLotCalc` | `re1CardModel` |
| Core plan form, non-PS1 branch | first-lot calculator + HTML | levels check only (`wrongSideOf`); the PS1/RE1 box is the only sizing |
| Move stop (`coreStopOpen/Save`) | also cancelled Ladder (L) levels via `applyStopMove` | stop move only (L cards are read-only legacy) |
| Port › Core risk line (`data-ln3-risk`) — **Port rows 7–8** | "to SL now x% · full y%" from `coreAcctRisk` / `CoreSize.layer2` | "Active risk {used}% of {cap}% cap · Compounder heat {h}%" from `L.active` + `L.comp.heat`; no snapshot → "Confirm a snapshot in Settings ›". The pool/free-cash half of the line is unchanged (D1) |
| Account base for % (`ps1E`, `lr3Base`) — **row 8** | `poolsOf().total` (capital) | `L.basis.weekEquity` only; none → 0 / "not sized" (D4). RE1's own provisional first-week base is unchanged |
| Old (v1) Sat plans (`satV3PlanAcctCalc`) | legacy lot / heat / readiness | read-only: no size, never Ready, warning "Old plan · read-only"; the blocked row offers **Copy to new plan ›** (`satV1CopyToV2`: same asset / side / levels, nothing sized) (D3) |
| `sat7dAcctBase` | rpt / heat / nNew / riskTHB / ddFactor | plumbing only: `B, fx, cap, trades, cnt` |
| Today tasks `heat Sat` · `new count` · `Core layer 2`, the "numbers" table | legacy calculators (never rendered in Lean Today) | removed |
| `render()` account summary (heat / layer-2 / "if every stop hits") | computed every draw, `#strip`/`#ports` hidden | removed |
| DD1 config fields (`ddReduce / ddPause / ddPauseWeeks / ddRecoverR`) | stamped by `ddCfgFix`, no reader | writer removed; stored fields stay readable |

Kept per decisions: `poolSplit` / `poolFree` (read-only allocation: Port pool lines, Settings hint) · `CoreSize.status` + tests · stored fields (`settings.coreRisk / satRisk`, `coreRisk.tier*`, `satV2.*`, card `cs`, `plan.risk`, `ln4.snap`) are read-only: no writers.

## One wrong-side helper (D-brief)
`wrongSideOf(side, entry, sl, tp)` → `'SL' | 'TP' | null`, built only on `RiskEngine.satEntryOrder` (`SAT_BAD_ORDER`; each leg is tested with the other leg replaced by a valid probe). Used by `pb2Model` (form + board), `sdWrongOf` (text + flip → Today, board, drawer, Place sheet via `pvSatBlockOf`), `satRrCheck`, and the Core form's "Entry must be above Stop". The duplicate `s>=e` / `t<=e` logic is gone.

## Gates
- Today / Plan card / drawer / sheet fixture numbers: unchanged (the re1d · pv1 · lr3 · lr5 · lrf · sd1 · wl · ts1 suites assert them and pass). Port changed only where listed above (rows 7–8).
- Hooks superset: PASS. The baseline was **trimmed on purpose** for the deleted dead UI — removed hooks listed in `docs/reports/AU1-hooks-removed-b2.json` and `-b3.json` (48 ids · 146 data-* names · 116 literal values · 1 handler event · 108 handler functions; all belonged to the hidden Core card panel, the hidden Sat strategy panel, the pre-Lean Core form and the dead tier / add-on / ladder sheets).
- Engine suites (risk_engine 313 · re1_adapter 63 · re1c_live 88 · ps1_size · ps1b_size · pv1_posview · core_size 25): PASS.
- Full `run_regression.sh`: see the last line of this file.

## Tests changed
- Retired with a printed `RETIRED` line (bodies are in git history): `run_tests_phase2` (whole suite — the hidden Sat strategy bar / editor), `run_tests` §7 Sat lot cases + `sat7dNew` flow, `run_tests_phase35` check 10 (tier boxes of the deleted Core form), `run_tests_phase51` sections 2–4 (news window / R:R chip / TP2 line on v1 plans in the hidden panel).
- Updated: `run_tests_phase19/20` (no longer grep for `Calc.newCount`), `run_tests_en1` (expected-hook lists drop deleted handlers).
- Shims: `tests/ff_stub.py` carries the old single-field Sat setters (`satV2SetDir`, `satV3PlanEdit`, `satV2Edit`, `satV2SetSleeve`), `satV3SaveReadyAccounts`, `satV3IdeaDelete` for legacy suites that seed plans with them — the app no longer has them.

## Open questions (decided unattended → option that keeps on-screen numbers unchanged)
1. **`ln1On()` legacy-mode branches (71 sites in Journal / Watch / Flow / Today / Settings)** are UI mode switches, not calculators, so they were left in place. The real app is always Lean (`ln1Mode()` only returns "legacy" when a test pre-sets `LN1_KEY`). Removing them is a separate clean-up (CLEAN2?) and would retire more old suites.
2. **Other orphans outside the sizing families** (e.g. TV1 import, `match*` helper, `bd*` panels, `wl1*` archive — ~110 functions with no caller anywhere) were **kept**: deleting them is outside AU1 and their hooks are in the hooks baseline. Candidate for a "dead code" pass.
3. **L (Ladder) strategy cards** are read-only legacy: no ladder reservation maths any more (`coreLadders` reports held cost only, reserved = 0), no ladder level auto-cancel on stop moves, the form refuses to create L plans. Port pool lines for an account that still has L cards would show reserved ฿0. The fixture has no L cards, so no fixture number changed. Confirm no real account still holds an active L card.
4. **`coreAddBlockReason`** lost its capital-based per-stock cap line (`cx.opts.stockCap`); the `maxLots` count rule and the price-state rules stay. RE1's add-on rule (`ADDON_TOTAL_RISK`) is the cap now.
5. **Pre-PS1 star-evaluation snapshot (`cs` field, CS1)** is no longer written on save (reader kept). Confirm nothing downstream needs a fresh `cs` on new cards.
6. **`satV3PlanAcctCalc` v1 branch** returns `ready:false` always; v1 plans that already have a trade are unaffected (trade rows come from RE1). A v1 plan with no trade can only be copied to a v2 plan.
7. **Branch hygiene:** the remote `claude/au1` still holds only the Phase A report (a force-push was not permitted). Work is on `claude/au1-b` (history contains replayed SD1/EN1 commits because local `main` was stale); `claude/au1-pr` is the same work rebased onto `origin/main` for the PR.
8. Stale Thai/English code comments that mention `Calc.satLot` / `Calc.readiness` / `coreAcctRisk` remain in a few places; harmless, not rewritten.

## Final full run
`bash tests/run_regression.sh` on the final code: **67/67 ok · 0 failing** (1040 s). Baseline before AU1 on the same base: 67/67.
