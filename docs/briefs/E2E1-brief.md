# E2E1 — Whole trade loop, end to end, real clicks · no dead buttons · fix what breaks

Branch from fresh origin/main (after HF5 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-e2e1 -b claude/e2e1 origin/main`. First commit = this brief. UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md`. Locked brief. Run this BEFORE HW2.

## Why (SRTp 25 Nov, live)
XAUUSD Short sits in Today › Check orders as Ordered; pressing **Filled** does nothing visible. Earlier this week: Place order Confirm did nothing (undefined field, HF4), Last price button led nowhere (HF5), a working Sat order reserved no risk (HF5). Each bug was a button that silently did nothing. SRTp wants the whole loop checked once so it does not happen again.

## Part 1 · Fix the Filled bug first
Path: `bdPill` (status 'ord') → `bdFill` → `ln4RecordFill` → `pb2Filled(id)`. Silent exits to check: `sat7dIdea(id)` missing → `return` with no message; `satV3SaveSlot` throws (caught by `console.warn` only) or is refused by the engine (weekly budget, step lock, HF5 queue counting the order itself, min lot) → toast + `pb2OpenEdit` (does the toast show and does the edit open?); account slot missing for orders placed from the plan form vs from Place order (HF5 D finding). Reproduce with a Sat **Short XAUUSD lot** order placed (a) from the Place order sheet and (b) from the plan form, Main account, then press Filled on Today and on the Plan board. Fix so Filled always either records the fill (→ Manage row, Holding) or shows the exact reason + fix in a visible line (rule 9). Report the cause.

## Part 2 · End-to-end suite `tests/run_tests_e2e1.py` (real clicks, not JS calls)
Use Playwright clicks on the visible buttons (no calling app functions directly except to seed data and read results). Strict Firestore mock (rejects undefined, as HF4). Run every journey at **1440 and 390**.
Journeys (each to the end):
1. **Sat lot (XAUUSD) Short, Main**: + New plan → fill → Save → Today Enter row → Place › → Confirm → Check orders row → Filled → Manage row → Price › → Move stop › (to ≥ 50% cut) → TP1 rule (exit 50% + stop to entry, if the app has it; else close) → Close (win) → Journal shows the trade with R and $ → Risk room back to 0 → step state correct.
2. **Sat % (BTC) Long, Main**: same, close as a loss → step advances; re-entry offered once, works, then blocked the second time.
3. **Sat queue (HF5 rule)**: XAU full risk → BTC blocked with the right line; move XAU stop → BTC allowed; 3 open → 4th blocked.
4. **Momentum stock, Main**: Watch › Make plan › (homework not done → 70% size shown everywhere) → Place › → Filled (qty = card) → Move stop → Close → Journal.
5. **Compounder, Family**: Pilot → Filled → Add-on gate (blocked until thesis + +1.5R + stop at BE, reason shown) → Close.
6. **Cancel paths**: cancel a working order before fill (reason sheet) → reserved risk released; cancel a plan.
7. **From an Idea**: My idea scenario → Make plan › → lands in the plan form with the levels → continue to Place.

## Part 3 · "No dead button" guard (permanent)
In the same suite, after EVERY click assert at least one of: DOM changed in the clicked area, a sheet/overlay opened or closed, or a visible message (toast / ⚠ line) appeared within 1.5 s; also no `console.error` / uncaught error / `console.warn` from a click handler. Additionally crawl Today, Plan board (all segments), Watch detail and Manage rows with seeded data: click every enabled button once (skip ones that send/delete/open external links) and apply the same assertion. List any button that fails → fix it (or report if not small).

## Fix rules
Fix every failure the suite finds. Small fixes (< ~30 lines, no engine formula change) → fix and list. Anything bigger or touching the risk formula → stop and report with the exact step and cause.

## Report
Table journey × step × (1440 / 390) → pass/fail, the Filled cause, every fix (file line), any dead buttons found. Screenshots (only `e2e1-*.png`): XAU after Filled (Manage row, 1440 + 390), Journal row of journey 1 (1440), any fixed error line (390).

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks after the last change · new suite in REST= (it must stay in the regression permanently) · revert tracked screenshot rewrites · no push until I review.
