# HW1d — Fact Sheet import: lenient on missing groups, track from Watch, command includes the track

## What changed (`index.html`)
- `ltFactsCheck(f, trk)`: a required group with no lines is no longer an error. Each missing group is added to `facts.missing` as `<Group> — not in this Fact Sheet` (compounder with no `more` items → `More — …`). The function works on a copy and never mutates its input.
- Over-limit text (`biz` > 90, line/mgmt `text` > 80) is trimmed instead of failing. Still errors: wrong types, `q.cols` ≠ 4, `calc` without `formula`, line without `src`, bad enums, list-size limits (the auto-added "missing" entries don't count toward the 3-item limit).
- Required groups are checked against the **Watch track** (`wl1TrkOf`), both on import (`ltParse`, facts-only path) and when reading the stored sheet (`ltFacts`). `facts.track` is stored as given.
- Toast: `Fact Sheet updated (Q3 FY26) · missing: expected · made for momentum, shown as Compounder · your notes and the AI thesis are unchanged`.
- Empty-state step 1 chip now copies `living-thesis facts TICKER compounder|momentum` from the Watch track (Copy for AI challenge already had the track).
- Full JSON import unchanged except the same leniency in its `facts` block (it no longer drops facts for missing groups or over-limit text).

## Tests
- New `tests/run_tests_hw1d.py` (30 checks, 1440 + 390): Compounder + momentum sheet missing `expected` → imports, missing entry, toast, Compounder layout; matching-track missing group → warning; broken structure still errors (4 cases); long text trimmed; chip text per track; challenge header.
- Updated: `run_tests_hw1c.py` (toast, chip text), `run_tests_lt2.py` (removed the 4 old "invalid" cases for biz/text length and missing groups, added trim and missing-group-imports checks).
- Added `run_tests_hw1d` to `tests/run_regression.sh`.
- Hooks superset: PASS. hw1c 68/68, lt2 96/96, hw1d 30/30.
- Regression: see result below.
- Regression: `JOBS=2 bash tests/run_regression.sh` → 79/79 ok, 0 failing (includes hooks superset PASS).
