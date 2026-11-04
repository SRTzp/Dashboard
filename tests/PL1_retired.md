# PL1 — expectation changes (no test deleted · each row = behaviour the PL1 brief changed)

Phase A, Step 2 (A4 single Base Risk + A3 manual RS stars)

| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase111 `calc` | `starsFromEval` table, `evalGate`, `starBudget` formulas | **RETIRED** (prints RETIRED) | A4 removed these functions; `Calc.riskBudget` (same formula, flat Base) is covered in phase114 |
| phase111 `size` | size by ★★★/★★/★ (127/95/63), banner `★ · Base risk x% · Manual`, snapshot `stars:3`, buy-1 risk 1 | **RETIRED** | Base Risk is one value; covered by phase114 `size` |
| phase111 `gate` (3 funcs) | open-plan gate (Stars · RS · Gate 5), `Missing:` banner, Candidate→WL gate, Pending Review chip | **RETIRED** | A4 removed `evalGate`/Pending Review; the new Ready rule (A5) and screening (A2) arrive in Step 4 |
| phase111 `budget` | AAPL→MSFT switch expected `★★ · 0.75%` | now `Base risk 1.00%` / risk 1.0 | flat Base Risk |
| phase111 `budget` | switch to ticker with no stars → `No stars · Unassigned`, empty risk | **RETIRED** (comment) | no stars gate; every ticker gets flat Base |
| phase111 `budget` | reload check `e.stars == 3 and gate5 == passed` | only `date` checked | evaluation sheet no longer edits stars/gate5 (data kept) |
| phase107 §3 | `Need: Stars · RS · Gate 5 (0/3)` and `Need: Stars`, ☆☆☆ row | `Ready` (note present); star step **RETIRED** | interim `td4ProMissing` = note only (`// PL1 interim — replaced in Step 4`) |
| phase107 §3 | tap star again to clear; `stars=2` on promoted doc; `✓ … · ★★ · Undo` | **RETIRED** / `stars==0` / no ★ in moved line | no ★ control on the Candidate form; promoted doc no longer writes `stars` |
| phase107 `pro_fill` | clicks `[data-td4-star]` | star click removed | same |
| phase107 §3 layout | hint row left + ☆☆☆ right | hint row only | same |
| phase107 `W()` fixture | `stars=n` | also sets `rs_stars=n` | Watchlist sort/filter now reads `rs_stars` (A3) |
| phase107 §4 | tap star 1→2→3→3 = 1,2,3,0; `wl-sd` `★3` | RS dropdown → `rs_stars` 1,2,3,null; row badge `RS ★★★` | A3: Unrated ≠ 0, dropdown replaces 3-button control |
| phase109 §2 | 3 star buttons ≥32px, tap-again→0, aria-pressed, `stars` persisted | RS dropdown ≥30px high; `rs_stars`/`rs_rated_at`; MSFT legacy `stars=1` untouched | A3 |
| phase109 §3 | click `[data-td4-star="2"]` in Candidate form | removed | no ★ control there |
| phase65 | Settings default `sCrRiskA` = 1.25 | = 1 | the field is now Base Risk per trade (key `baseRisk`, default 1) |
| phase65 | save → `riskPct 1.5` · `riskA 1.5` | save → `baseRisk 1.5`, `riskA`/`riskPct` not written (kept as stored) | A4: legacy keys kept, not migrated |
| phase65 | Tier A/B plan cards sized at Risk A = 1.5% | A = B (stored `riskA`, default 1.25) | legacy cards still size from stored `riskA`; the Base Risk field no longer moves them |
| phase66 | multi-error line `A · Risk/ไม้ ต้องอยู่ระหว่าง 0.1–5` | `Base Risk per trade ต้องอยู่ระหว่าง 0.1–5` | field label |
| phase91 #11 | "first-lot risk > Base → ต้องไม่เกินงบเสี่ยง Base" | **RETIRED** | `riskFirst` no longer coupled to the Base Risk field (legacy-only) |

## Known pre-existing failures (also fail on main — not caused by PL1)
- phase66 S2 (`index.backup-pre-POL1.html + tests/_bk_pol1/` — folder not in repo)
- phase23 (migration writes 2×), phase13, phase5 — see `docs/reports/RUN-summary.md`

## New suite
- `tests/run_tests_phase114.py` — A4 (Calc.riskBudget, flat 1%, Settings label/default/save, old plan snapshot untouched) + A3 (rs_stars Unrated≠0, rank-only, old `stars` ignored) + interim note-only promote form
