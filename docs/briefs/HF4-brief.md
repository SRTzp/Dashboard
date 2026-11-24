# HF4 — Place order write fails: "Unsupported field value: undefined" (urgent, small)

Branch from fresh origin/main (after HF3 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-hf4 -b claude/hf4 origin/main`. First commit = this brief.

## Bug (SRTp 24 Nov, live, after HF3)
Sat Place order → Confirm → `⚠ Could not record the order · Function DocumentReference.set() called with invalid data. Unsupported field value: undefined`.
Cause (found in review): `pb2PlaceYes` builds the snapshot with `reentry: isRe || undefined` and `re1: c.model ? {...} : undefined` (~30451). Firestore rejects `undefined` values. This was the real reason Confirm "did nothing" before HF3 (the throw was silent then). Same pattern exists elsewhere (e.g. ~24510 `tp1_pct`/`tac_type`, ~8295 `accelerator`).

## Fix
1. Global: `db.settings({... , ignoreUndefinedProperties: true})` at the existing settings call (~9181; Firebase 10.12 supports it). Undefined fields are then dropped on every write.
2. Local belt-and-braces: in `pb2PlaceYes` and the Core place path, build the snapshot without undefined keys (only add `reentry` / `re1` when they have a value).
3. Test mock: make the mock Firestore `set()/update()` throw `Unsupported field value: undefined` on any undefined value (nested too) UNLESS `ignoreUndefinedProperties` was set — exactly like the real SDK. Then run the FULL regression: any other write that sends undefined will now show up; with fix 1 they all pass. List in the report any write that would have failed without fix 1.
4. Tests (`tests/run_tests_hf4.py`): Sat Short and Long place (re-entry false, no model) → write succeeds, Order working ✓, snapshot has no `reentry` key; re-entry true → `reentry:true` stored; Core place → succeeds.

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks · only `hf4-*.png` if any (none needed) · commit, push, give PR link (small urgent fix — I review the report, no screenshots needed).
