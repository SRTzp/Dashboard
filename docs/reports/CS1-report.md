# CS1 report — Core plan = planning only · ★ risk (manual) · Sat Classify/Tactical/Main · Settings in English

Start sha `bca659c0e763` → end sha `b003f4b511f3433a789ec9ba20c676847aedb7ba7a8bddcb8196d3e91ba744bb`. Backups: `index.backup-pre-CS1.html`, `tests/_bk_cs1/` (top-level tests files). Audit written first: `docs/reports/CS1-audit.md`. Verify: `docs/reports/CS1-verify.txt` (built by `tests/make_verify.sh CS1`). Retired/changed expectations: `tests/CS1_retired.md`.
**Last index.html edit: 30 Oct 03:1x · full run (runall2, base + 1–111) 03:18 → DONE 04:56.** No push, no file deleted, Firestore rules untouched (`eval` lives inside existing `stockNotes` docs → no new rule). `core-size.js` untouched.

## Results
- phase111 **133/133**. Full run **110/112 ok**; only the two known failures remain: **phase5** (BTC Break Price, pre-existing since before SET1) and **phase13** (opens missing `index.backup-pre-UI1.html`).
- 22 suites failed on the first triage run; each was an intended change (expectation updated + logged) or fixture need — no index regression found except two fixes made from triage (Candidate row order: Tier box stays first; Settings table header width at 390).

## Audit summary + migration decisions
(see CS1-audit.md for the full table)
- **Removed from the plan form:** Tier block (Fortress/Growth numbers, Yes/No, Gate 5, "Tier ที่ใช้" override, reason, fill-from-Thesis), `บันทึกเฉพาะ Tier`, editable Risk %. Replaced by a read-only banner: `★★★ · Base risk 1.00% · Manual` / `Fortress + Proven · RS Passed · Gate 5 clear` / budget line / `Missing: … · Edit Stock Evaluation ›`. Account rows show **Main**.
- **Evaluation data:** `stockNotes/{key}.eval = {fortress, proven, emerging, rs:{sustained,b26,b52}, gate5[3], stars, stars_src:'manual', date}` — one record per ticker+market, edited in the shared **Edit Stock Evaluation** sheet (Candidate row, Watchlist edit modal, Today Cand→WL form, plan-form banner). Defaults `untested`; Gate 5: passed = "No", failed = "Yes". Legacy Watchlist `stars` are read as fallback and mirrored.
- **Manual ★ now, auto later:** `Calc.starsFromEval` implements the table top-to-bottom (12-row truth table tested), not wired; mismatch shows `Eval suggests ★★`. `★ · RS only` label supported.
- **Gate (★≥1 + RS + Gate 5 all No):** enforced in `coreNewIn` and again in `coreNewSave` (single choke point for Plan tab, Watch button, Today, manual ticker typing) and in the Today Cand→WL form. Watch add / imports cannot create new Watchlist docs (TD4b rule kept). Existing Watchlist items that now fail get a **Pending Review** chip, never deleted/moved.
- **Decisions where the brief was open:** (1) capital caps (per-first-lot and per-stock) are not risk: ★ plans use one fixed column — Settings › Core **"A"** — for every star level (`CS_CAP_KEY`), stated in Settings; not a ★→Tier mapping. (2) Ladder **L** eligibility for new plans = `eval.fortress = passed`. (3) **"Tier passed"** (old Today checkbox) has **no mapping** (Tier A-F/A-G/B definitions ≠ Fortress/Proven/Emerging; mapping would be a guess); **RS Leader → rs.sustained**. Old `promoted_by:['rs']` docs are not auto-passed. (4) Existing Tier data/cards untouched; legacy cards keep Tier logic; dev-flag legacy form (`dash.ln1Legacy`) untouched.
- **Old tests:** phase89 §2 and phase91 §10 (old Tier block / editable Risk %) retired (print RETIRED); the rest updated in place — see CS1_retired.md.

## Sizing (Core ฿4.2M, fx 33 → $127,273 bucket, entry 100 / stop 90)
| Stars | Base | Budget | First lot |
|---|---|---|---|
| ★★★ | 1.00% | $1,273 | 127 sh (risk $1,270) |
| ★★ | 0.75% | $955 | 95 sh |
| ★ | 0.50% | $636 | 63 sh |
| none | Unassigned | — | no plan (save disabled; `coreNewSave` direct call creates nothing) |

Budget = Base % × Core equity × FF × DD (applied once) − risk already used by other positions/plans of the same ticker+account (editing plan excluded). Example: ★★★ with an existing $600 position → `Risk budget $1,273 · used $600 · this tranche ≤ $673` → 67 sh. Add-on tranches use the card's snapshot Base and the existing carry, so they share the one budget. Switching ticker/account/entry/stop recomputes from scratch (tested: no residue). Snapshot `cs` saved with the plan (eval, dates, ★, source, base %, riskAmt, equity, used, budget, FF/DD); later eval/★ edits don't change it (tested).

## Sat (Plan › Sat)
Classify = **Clear Trend / Unclear** (old strong/normal → clear, uncertain → unclear on read; written only on next save; no Journal grouping by classify exists in code, mapper `pfClsKey` provided). Tactical without Clear Trend (with or without Main): Setup + Entry/SL/TP disabled, hint `Tactical needs Clear Trend`, calc block → can't save; Today shows Pending `Needs Clear Trend`. Filled Tactical + no Main: Main plan blocked on `+ แผน`, Today Create plan, sleeve switch, Trade-Idea plan, and at save (`Close the Tactical (XAU) first`); Main exists / unfilled Tactical plan / Main tranche add unaffected (tested).

## Settings → English
All labels/hints/buttons in the Settings and System-settings overlays (values and ids unchanged). Left in Thai: validation error messages, dynamically built texts outside those overlays.

## Files changed
index.html (+438/−159); tests: run_tests_phase111.py (new), runall2.sh (1–111), phase77 helper, and the updated suites listed in CS1-verify.txt.

## Screenshots (all opened)
`tests/screenshots/cs1-plan-390.png`, `cs1-plan-1440.png`, `cs1-eval-390.png`, `cs1-gate-390.png`.

## Limitations
- Capital-cap column for ★ plans is the shared "A" column (no separate star caps yet).
- L-plan risk isn't counted in `used` (ladders use a capital budget).
- Orphan trades are assumed to be in the ticker's market currency.
- Dev-flag legacy plan form keeps the old Tier UI (only old suites use it).
