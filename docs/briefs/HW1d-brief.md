# HW1d · Fact Sheet import: lenient on missing groups, track from Watch, command includes the track

Found 21 Nov 2026: importing a facts-only JSON for a **Compounder** stock failed with `Fact Sheet not valid — a momentum Fact Sheet needs lines in group expected`. Causes: (1) the skill's `facts` mode was described as "for Momentum stocks", so it wrote `track: momentum`; (2) it found no consensus data and left the `expected` group out; (3) the app rejects the whole Fact Sheet when a required group is missing. The skill is being fixed separately (track from the command, a "Not found" line instead of a missing group). This job fixes the app. git fetch, branch from fresh origin/main (`claude/hw1d`). If RK1 is open, rebase after it merges.

## 1. Missing required groups → import with a warning (not an error)
- `facts` validation: a required group with no lines is **not** an error. Import the Fact Sheet, add one entry per missing group to `facts.missing` (`Expected — not in this Fact Sheet`), and show it in the toast: `Fact Sheet updated (Q3 FY26) · missing: expected`.
- Hard errors stay only for broken structure: wrong types, `q` not 4 columns, `calc` without `formula`, line without `src`, text over limits (trim long text to the limit instead of failing; keep failing only for wrong types).

## 2. Track comes from the Watch item
- The Homework page renders with the stock's Watch track (Momentum / Compounder), not `facts.track`.
- If `facts.track` differs: import anyway, store as given, toast adds `· made for momentum, shown as Compounder`. Required-group checks use the Watch track.

## 3. The copy-command chip includes the track
- Empty state step 1 copies `living-thesis facts TICKER compounder` (or `momentum`) from the Watch track. Same in Copy for AI challenge header line (already has the track).

## Proof
- `tests/run_tests_hw1d.py`: Compounder stock + momentum Fact Sheet missing `expected` → imports, missing entry added, toast text, page shows the Compounder layout · required group missing on the matching track → imports with warning · broken structure still errors · over-limit text trimmed · command chip text per track · existing hw1c/lt2 tests still pass (update the ones that expected the old error).
- Hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/HW1d-summary.md`. No unrelated PNGs.
