# AU1 · One sizing engine (retire the legacy calculators)

Goal: every number and warning a user sees about size, risk, lots, heat or drawdown comes from RE1 (risk-engine.js + re1-adapter.js + pos-view.js). No rule changes: RE1 POLICY values stay exactly as they are.

## Phase A: map only (no code change), then STOP for review
Write `docs/reports/AU1-map.md`:
1. Every caller of the legacy calculators and what it feeds on screen:
   - `Calc.coreSize.*` (poolSplit, addLot, ladderBudget, tierBadge, ddStep, emergencyStop, applyStopMove, status, vsCost, layer)
   - `Calc.satLot`, `Calc.heat`, `sat7dCalc`, `satV3PlanAcctCalc`, `satV2PlanCalc`, `satPyrCalc`, `sat7dAcctBase`
   - DD1 (`ddEval`, `ddSync`, `settings.ddState`), `coreSizeOpts`, `poolsOf`, `coreAcctRisk`, `coreSimCalc`, `lfAddCalc`, `coreNewInL`, `coreLBuyIn`
   - For each: function → which screen/element (data-* hook) shows its output → is that output visible today (yes / hidden / dead).
2. For every visible output: the RE1 equivalent (function + field) or "no RE1 equivalent".
3. Every place a wrong-side / order check is done (engine `satEntryOrder`, `pb2Model`, `sdWrongOf`, core form checks).
4. A side-by-side table on the test fixture: legacy number vs RE1 number for the same plan (Momentum, Compounder pilot + add-on, Sat lot product, Sat %-loss product). Flag every mismatch.
5. Proposed removal list in 3 buckets: dead (safe to delete) · visible but replaceable by RE1 · needs a decision (no RE1 equivalent).
Push the report only. Do not delete anything in Phase A.

## Phase B: after review (separate go)
- Switch every visible legacy output to RE1, then delete the dead calculators and their settings UI. Keep stored data fields (read-only) so old docs still load.
- One wrong-side helper used by the form, the board, Today and the sheet, built on the engine's `satEntryOrder` / `STOP_WRONG_SIDE` (no duplicate logic in the UI).
- Tests: the fixture numbers on Today, Plan card, drawer, sheet and Port are unchanged, or changed only where Phase A flagged a mismatch and the review approved it. Keep core_size tests only for the functions that stay.
- Hooks superset PASS · all engine suites PASS · full run_regression.sh 0 failing · `docs/reports/AU1-summary.md` (lines removed, functions removed, what moved to RE1).
