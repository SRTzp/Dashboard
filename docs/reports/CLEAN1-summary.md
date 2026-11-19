# CLEAN1 — small fixes + Mac tidy

## A. Fixes (no engine changes)
1. **Journal review panel** — Planned entry already rendered `#qty @ price` in code; the committed `journal-1440-both-live` was stale. Regenerated: Planned and Actual both read `#0.21 @ 2,642`.
2. **Today Blocked row, line 2** — `Blocked · <short reason> · allowed #n` (n = engine `allowedQty` via new `re2AllowedN`; omitted when null/0). The phone no longer hides the `Blocked ·` prefix. Still one nowrap line.
3. **Desktop Risk room SAT** — text shortened to `step 1 · 1.19/1.2%` (busy → `· busy`); no truncation.
4. **Screenshot scripts** — whole-page shots hide `#tabsMain` only at ≤600px (`@media (max-width:600px)`) in lr4/lrf/lr5b/lr5c side scripts, lib_phase38/39/40, run_tests_phase373, ln4_match, ui_audit (lr5a_side already did).

Tests: `tests/run_tests_clean1.py` (14 checks; added to run_regression.sh). Full `run_regression.sh`: **64/64, 0 failing**.

## Noticed, not changed
Journal › Not taken list (1440): the reason pill is styled by the lr5c rule `.lr5 .lr5-rs:not(.miss){display:inline-grid;grid-template-columns:24px 16px 64px}`, so "Thesis or news changed" overlaps its date. Pre-existing on main (lr5c); needs a separate fix.
