# SK1 — changed / retired expectations

None. Phase 365, 366 and 59 pass unchanged (fake clock is a Thursday → Daily default, no weekend-only items).

Notes for future tests:
- `td3Mode` is now set once per ICT day by `sk1ModeSync()` (first Today render of the day). A test that pre-sets `td3Mode` before the first render of a new day will be overridden once; click the tab or call `td3SetMode()` instead.
- New suite: `tests/run_tests_phase367.py` (63 checks, 390 + 1440).
