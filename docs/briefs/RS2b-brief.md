# RS2b · Screen › Industries (industry view per preset + Group RS)

Decided by SRTp 20 Nov 2026. Spec: mockup `docs/briefs/lr/ScreenIndustries.html` (A desktop · B filtered Stocks · C phone). git fetch and branch from fresh origin/main (`claude/rs2b`).
Lean UI: same table area (no new panel), one line per row on desktop, no primary button, neutral chip (no port colours), links in ink, 44px phone targets.

## Data (job, `build_rs2.py`)
- Industry is already cached (`sector|industry`). Add `_meta.indN` = liquid rows with an industry, and `_meta.indCov` = indN ÷ n. Log `rs2: industry coverage x%`.
- If coverage < 90%, raise the daily industry lookup budget until it catches up (keep the run < 15 min); weekly runs refill missing ones first.
- **Group RS** (computed in the job, written per row as `gr` = group rank and once in `rs2/_meta.groups = [{ind, sec, n, avg, rank}]`): average 12M rating of all liquid stocks in the industry, only industries with **≥ 5 liquid stocks**; rank 1 = strongest. Industries with < 5 → no group rank.

## UI (Screen, desktop + phone)
- Toggle **Stocks | Industries** in the preset row (after the preset segments). Remembered; Reset → Stocks.
- **Industries view** follows the current preset and filters: one row per industry with ≥ 5 liquid stocks and ≥ 1 match. Columns: `#` · Industry · Sector vs SPY (arrow) · **Matches** `6 of 41` (default sort, desc; tie → Group RS) · Breadth (bar + % = matches ÷ liquid stocks in the industry) · Group RS `88 #3` · Top 5 (ticker + RS, best first, one line, ellipsis when narrow) · `Stocks ›`. Header sort on Matches, Breadth, Group RS. Industries with exactly 1 match folded under `+ N industries with 1 match`. Header line: `27 match in 9 industries`.
- No detail panel in this view (table full width).
- Row click or `Stocks ›` → Stocks view filtered to that industry with a chip `Industry: Semiconductors ×` (neutral). × clears. The chip also shows when the industry filter is set from Filter ▾ (add Industry there).
- Missing industry: stocks without an industry count as `Unknown`, never shown as a row; if coverage < 90% show a muted line `Industry data 84% complete`.
- Keyboard: ↑/↓ moves the selected industry row, Enter opens its Stocks; ←/→ still switch presets. Tick/download (RS2a3) only in Stocks view.
- Phone: same toggle (44px), 2-line rows (`Industry · 6 of 41` / `Group RS 88 (#3) · top 3 names`), tap → filtered Stocks.

## Proof
- Selftest: group stats (avg, ≥ 5 rule, rank, ties), coverage counter.
- `tests/run_tests_rs2b.py`: toggle + memory, rows per preset, Matches/Breadth/Group RS values, sort, 1-match fold, ≥ 5 rule, Top 5 ellipsis at 1280, Stocks › and chip filter + ×, Filter ▾ industry, coverage line, keyboard, tick hidden in Industries, phone rows, 360/390/1440 no overflow.
- Side-by-side vs the mockup (`tests/screenshots/rs2b/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · RS2b section in `docs/reports/RS2a-summary.md` (coverage %, number of groups, runtime change). No unrelated PNGs. If the workflow needs a change, put it in `docs/proposals/prices.yml`.
