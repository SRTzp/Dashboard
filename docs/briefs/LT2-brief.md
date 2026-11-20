# LT2 · Fact Sheet in the living thesis (`facts` block) · import + store

Decided by SRTp 20 Nov 2026. Mockups: `docs/briefs/lr/HomeworkWatch2.html` (B · left column) and `HomeworkFacts.html`. Build after RS2a2, before HW1.
Two parts: **(1)** the living-thesis skill writes a new optional `facts` block (done by the orchestrator as a skill update, not by CC); **(2)** the Dashboard imports, validates and stores it (this CC job). HW1 renders it.
Principle: **facts only.** Numbers, dates, sources, formulas and management's own words. No opinions, no "AI thinks". The user writes the thesis.

## `facts` schema (additive, optional key in `living-thesis@1`; no schema bump)
```json
"facts": {
  "track": "compounder",                 // compounder | momentum
  "asOf": "Q3 FY26", "date": "2026-11-18",
  "biz": "Membership warehouse stores · yearly fee · low prices",
  "mix":  [ {"seg":"Food","pct":40,"yoy":7}, {"seg":"Fees","pct":2,"yoy":11} ],
  "mixMeta": {"basis":"revenue","period":"Q3 FY26","src":"10-Q p.14","kind":"rpt"},
  "q": {
    "cols": ["Q4'25","Q1'26","Q2'26","Q3'26"],
    "rows": [ {"k":"rev_yoy","label":"Revenue y/y","unit":"%","v":[7,7,8,8],"kind":"calc",
               "formula":"Revenue ÷ same quarter last year − 1","src":"8-K EX-99.1 ×4"} ]
  },
  "lines": [
    {"g":"profit","label":"Fees vs profit","text":"Fee revenue ÷ operating income = 50%","kind":"calc",
     "formula":"Fee revenue $1.3B ÷ Operating income $2.6B","period":"Q3 FY26","src":"10-Q p.14 · p.6",
     "note":"Shows size only; does not prove half the profit comes from fees"}
  ],
  "more":    [ {"g":"competition","label":"Peer op. margin","text":"2.9% / 3.1%","kind":"rpt","period":"FY25","src":"peer 10-K"} ],
  "mgmt":    [ {"text":"Renewal dip from new online sign-ups","src":"Q3 call"} ],
  "missing": [ "Timing of next fee increase — not disclosed" ]
}
```
- `kind`: `rpt` (from the filing) · `calc` (needs `formula`) · `mgmt` (management's words) · `web` (consensus/quote site, needs `src` + `date`).
- `note` (optional): what the number does **not** prove. Required on any `calc` ratio that could be misread as a conclusion.
- `lines[].g` groups: `growth` `profit` `cash` `expected` `exposure` `lastq`. `more[].g`: `segments` `competition` `capital` `guidance` `valuation` `history` `owners`.
- `q.rows` keys: both tracks `rev_yoy`, `eps_yoy`; momentum `gm`; compounder `op_margin`, `shares_yoy`, plus 0–2 business KPIs (`kpi_*`, e.g. same-store, renewal). Exactly 4 columns (oldest → newest); missing value = `null`.
- Momentum must have `lastq` (revenue/EPS vs estimate, guidance raised/cut/kept) and `expected` (estimate revisions). Compounder adds `cash`, `expected`, `exposure`, and `more`.
- Limits: `biz` ≤ 90 chars · `text` ≤ 80 chars (one line in the UI) · `mix` ≤ 4 items (top 3 + Other, split by business type) · `lines` ≤ 10 · `more` ≤ 14 · `mgmt` ≤ 2 · `missing` ≤ 3. English (UI text).

## CC job (Dashboard)
1. **Import:** accept `facts` in the living-thesis importer (`IMP_LT_SPEC` optional object) and validate: types, enums, limits, 4 columns, `formula` present on `calc`, `src` on every line. Invalid `facts` → import the rest, drop `facts`, show one warning line naming the first problem. Never block the import because of `facts`.
2. **Store:** with the thesis as today (same doc, same size guard). `update` mode replaces `facts` whole; `log` behaviour unchanged.
3. **Accessor:** `ltFacts(it)` → the validated object or `null`, plus `ltTrend(row)` → `accel` (last 2 changes both up) · `slow` (both down) · `rising`/`falling` for level rows (margin, renewal) · `steady` otherwise. Used by HW1; no UI here except one muted line in the Full thesis view: `Fact Sheet · Q3 FY26 · 18 Nov` (or nothing).
4. **Export:** Export JSON includes `facts`.

## Proof
- `tests/run_tests_lt2.py`: valid import (both tracks) · each validation failure → rest imported + warning · `ltTrend` cases (accel, slow, rising, falling, steady, nulls) · export round-trip · thesis without `facts` unchanged.
- Hooks superset PASS · selftest PASS · one clean `JOBS=2 bash tests/run_regression.sh`.
- `docs/reports/LT2-summary.md` + a sample JSON for each track in `tests/fixtures/lt2/`.
