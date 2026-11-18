# LR1 — progress

## A0 · Hook inventory (base: origin/main fac328a)
- `tools/hook_inventory.py` scans `index.html` (static markup + HTML inside JS strings) → ids, `name=`, `data-*` names (+ static literal values), inline `on*=` handlers and the functions they call.
- `tests/hooks_baseline.json` saved from origin/main. `tests/hooks_test.py` asserts the branch inventory ⊇ baseline; added to `tests/run_regression.sh` (fast checks).
- Baseline counts: ids 541 · names 6 · data-* attribute names 747 (478 static values) · handler events 18 · handler functions 717.
- Branch = baseline at A0 (PASS, 0 failing).
