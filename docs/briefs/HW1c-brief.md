# HW1c · Import a Fact Sheet from the Homework page (facts-only JSON)

Spec: mockup `docs/briefs/lr/HomeworkImport.html` (A fallback · B Import › in the header · C result line · D ⋯ menu). Found 20 Nov 2026: `living-thesis` mode `facts` outputs `facts` + `summary.biz` + `catalysts` with **no `sections`**, and the importer (`ltParse`) rejects it with "No sections". The Homework page also has no import button. git fetch and branch from fresh origin/main (`claude/hw1c`); if HW1b is open, rebase on it after it merges.

## 1. Accept facts-only JSON (`ltParse` / import)
- A JSON with `schema: "living-thesis@1"` and a valid `facts`, but **no `sections`** (or `mode: "facts"`) = **facts-only import**:
  - Stock already has a thesis → replace only `thesis.facts` (and add new `catalysts` not already present). Never touch `summary`, `sections`, `kpi`, `tripwires`, `evidence`, `log` of the existing thesis. Add one `log` line `facts updated (Q3 FY26)`.
  - Stock has no thesis → store a minimal thesis `{facts, summary:{biz}, catalysts, mode:'facts', date, asOf, basis}`; everything that reads a thesis must treat a facts-only thesis as "no AI thesis yet" (no empty tabs, no "No sections", Full thesis menu item hidden, Compare with thesis hidden; Today's living-thesis reminders treat it as missing).
  - `summary` optional in facts-only (only `biz` used). All LT2 `facts` validation still applies; invalid `facts` in a facts-only JSON = error (nothing else to import).
- A full JSON (with `sections`) behaves exactly as today.
- Success message names what changed: `Fact Sheet imported (Q3 FY26) · thesis unchanged`.

## 2. Import button on the Homework page
- Fact Sheet header: small secondary `Import ›` (tooltip `Paste living-thesis JSON (facts or full)`) → the existing import sheet (`ltImportOpen(sym)`), bound to this stock.
- Fallback (no `facts`): the muted line becomes `No Fact Sheet yet — run living-thesis facts TICKER, then Import ›` (Import as a link to the same sheet).
- After import the Homework page re-renders in place (stays on the page, draft kept).
- Phone: same, in the Facts tab.

## Not changing
Full thesis view stays under ⋯ › Full thesis (it shows only when a full thesis exists — see item 1).

## Proof
- `tests/run_tests_hw1c.py`: facts-only on a stock with a full thesis (only facts changes, log +1, sections intact) · facts-only on a stock without thesis (no "No sections", no Full thesis item, Compare hidden, Homework shows the Fact Sheet) · invalid facts-only → error · full JSON unchanged behaviour · Import › from the Homework page binds to the stock and returns to the page with the draft kept · fallback link · phone Facts tab.
- Hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/HW1c-summary.md`. No unrelated PNGs.
