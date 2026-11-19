# AU2 · Drawdown stop + execution nudges

Start after AU1 Phase B is merged. Decided by SRTp 19 Nov 2026: no daily loss limit and no minimum-trades quota (they push toward fear or forced trades). Instead, measure execution and make placing easier.

## A. Stop new trades at 20% drawdown (engine rule, per account)
- Same equity basis as the existing emergency rule (`POLICY.emergency`, 10% → half size). Add `POLICY.emergency.stopPct: 20`.
- Drawdown ≥ 20% from the account's peak confirmed equity → block every NEW risk-increasing order (reason `DD_STOP`: "Account is 20% below its peak · new entries stopped"). Closing, reducing, moving stops and recording fills are always allowed (actionPolicy unchanged).
- It recovers by the same recovery rule as the emergency half-size (recoverPct), so it steps back down to half size, then full size.
- Applies to Momentum, Compounder and Sat. No override.
- UI: the existing state chip on the Act header shows "Stopped · DD 20%"; Blocked rows use the reason text. Engine tests: the trigger, block vs allowed actions, and recovery.

## B. Execution goal (revised 19 Nov)
- Setting `executionGoalPct` (default 100, options 80/90/100).
- Count for the current week, both accounts: denominator = plans that reached Ready this week; numerator = placed. A plan answered "Not taken" with reason Invalidated or Thesis/news changed is removed from the denominator (a correct skip is not a miss). Hesitated / missed / unanswered stay in.
- Today chip at the end of the Act "Open risk" line: `· Placed 4/5 · goal 100%` (phone `· 4/5 → 5/5`, nowrap; it never wraps the line). Green ✓ when rate ≥ goal; amber when below (tooltip: n unanswered / n hesitated); grey when no Ready plans this week. Tap → Journal › Not taken (this week).
- Weekly checklist: new item "Execution goal met" (auto from the rate; grey weeks count as met).
- Journal: weekly execution history + streak ("Goal met 3 weeks in a row"); Invalidated / Thesis-changed answers list their reason text in the weekly review.
- Same formula/helper everywhere; Today 390 must not get taller.

## C. Every Ready plan gets an answer
- The existing "passed entry · missed?" row on Today gets two buttons: `Placed` (opens the record-fill flow) and `Not taken ›` (the existing reason picker: Missed / Hesitated / Invalidated / Thesis or news changed). The row stays until it's answered.
- Weekly reset: unanswered Ready plans from last week are counted as unanswered in last week's rate (shown in the Journal), not carried into this week's chip.

## D. Place the order when planning
- On Save plan (Core and Sat), when the plan is complete and allowed: a one-line choice under the buttons: `Place order now (stop/limit at your broker) · Later`. "Place order now" opens the existing Place order sheet straight away. "Later" just saves. Remember the last choice per device; no extra dialog.

## Proof
- Engine tests for DD_STOP; `run_tests_au2.py` for the chip (counts, colours, phone nowrap, tap target), the answer buttons, the save → place flow, and that Today 390 does not get taller.
- Hooks superset PASS · full run_regression.sh 0 failing · `docs/reports/AU2-summary.md`.
