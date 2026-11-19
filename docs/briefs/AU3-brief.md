# AU3 · Small cleanup after AU1

No rule or number changes. Everything on screen stays the same, except the hidden "L" option.

1. **Legacy mode (`ln1On()` / `ln1Mode()`, 71 sites in Journal, Watch, Flow, Today, Settings):** the real app is always Lean. Remove the legacy branches and keep the Lean branch only. Remove `LN1_KEY` and the `dash.ln1Legacy` dev flag. Tests that pre-set legacy mode: switch them to Lean or retire those parts (print RETIRED lines, as AU1 did).
2. **Uncalled functions (~110, listed in AU1-summary "Open questions" 2):** delete the ones with no caller anywhere (static + coverage), in small batches with a quick regression after each. Keep anything a test or an inline handler still reaches. Trim their hooks from the baseline and list them in `docs/reports/AU3-hooks-removed.json`.
3. **"L" (Ladder) option in the New plan form:** hide it (old L cards stay read-only and still open).
4. **Stale code comments** that mention removed calculators (`Calc.satLot`, `Calc.readiness`, `coreAcctRisk`, DD1…): delete or rewrite in English.
5. **Proof:** fixture numbers on Today, Plan card, drawer, sheet, Port and Journal unchanged; hooks superset PASS (with the listed removals); all engine suites PASS; one clean full `run_regression.sh` 0 failing; `docs/reports/AU3-summary.md` (lines and functions removed). Commit only code, tests and reports (no regenerated screenshots).
