# LT2 — Fact Sheet (`facts`) in the living thesis · import + store

Brief: `docs/briefs/LT2-brief.md` (mockups `lr/HomeworkWatch2.html`, `lr/HomeworkFacts.html`). Dashboard part only; the skill change and HW1 rendering are separate jobs.

## What changed (`index.html`)
- `ltFactsCheck(f)` → `{ok}` | `{err}` (first problem). Checks types, enums (`track`, `kind`, `lines[].g`, `more[].g`, `q.rows[].k` incl. max 2 `kpi_*`), limits (biz 90 · text 80 · mix 4 · lines 10 · more 14 · mgmt 2 · missing 3), exactly 4 `q.cols` and 4 values per row (number|null), `src` on every row/line/mgmt, `formula` on every `calc`, `date` on every `web`, and the per-track required groups (momentum: `lastq` + `expected`; compounder: `cash` + `expected` + `exposure` + `more`).
- **Import:** `ltParse` validates `facts` separately from `IMP_LT_SPEC`. Invalid → `facts` dropped, everything else imported, `warn` = "Fact Sheet not imported — <first problem> (the rest was imported)", shown as one line in the import preview. Valid → preview row "Fact Sheet: <track> · <asOf> · <date>". `facts` can never block an import.
- **Store:** `facts` lives inside the `thesis` object (same doc, same 200 KB guard). A new import replaces `facts` whole (an import without `facts` leaves none). Log handling untouched.
- **Accessors:** `ltFacts(it)` → validated object | `null`. `ltTrend(row)` → `accel` / `slow` (last 2 changes both up / both down) · `rising` / `falling` for level rows (`op_margin`, `gm`, `kpi_*` renewal/retention/margin/rate/util) · `steady` otherwise, incl. any null in the last 3 values.
- **UI:** one muted line in the Full thesis view, `Fact Sheet · Q3 FY26 · 18 Nov` (nothing when no facts).
- **Export JSON:** already spreads the thesis, so `facts` is included (tested round trip).

## Proof
- `tests/run_tests_lt2.py` (added to `run_regression.sh`): 50 checks × 2 viewports (100) — valid import both tracks, 20 invalid cases each → rest imported + warning, `ltTrend` cases (accel, slow, rising, falling, steady, nulls), store through the real Import sheet, Full thesis line, export → import round trip, update replaces whole, thesis without facts unchanged, no console errors.
- Fixtures: `tests/fixtures/lt2/compounder.json` (COST), `momentum.json` (AVGO).
- Hooks superset PASS · RS1 selftest OK (46) · `JOBS=2 bash tests/run_regression.sh`: **65/65 ok · 0 failing** (1904 s).

## Notes / decisions
- `note` is not enforced (the app cannot tell which `calc` ratios could be misread); it is type-checked only.
- `mgmt[].text` also gets the 80-char limit.
- Level-row detection is by key name; HW1 can pass other rows as `steady`/`accel`/`slow`.
