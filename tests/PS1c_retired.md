# PS1c — changed test expectations

PS1c changes layout and display only. Sizing maths is unchanged (same `Ps1.planSize`); only the *meaning* of the per-entry field changed (split % of the idea risk instead of an absolute risk %). No stored card/trade changed.

| Suite / check | Old expectation | PS1c behaviour |
|---|---|---|
| phase120 §2 form layout | Entry · SL · Risk stacked as blocks | single trade = ONE row (Entry ＋ · SL ＋ · Risk %) on one baseline |
| phase120 §2 summary | `#68 · 3.9% · Risk 0.39%` | `#68 · 3.9% · Risk ฿22.4k (0.39%)` (THB money, every % of TOTAL portfolio); regime tag is an amber pill |
| phase120 §2 trim note | "Shares reduced to fit max position" | "Above max size 7.5% — shares will be trimmed" |
| phase120 §2 two entries | per-entry field = absolute risk % (0.3 + 0.2 > 0.4 → "more than") | per-entry field = Split % of idea risk (default 50/50) · total ≠ 100 → "Entry split must total 100%" · Save blocked |
| phase124 §7a | switching scope with the form open keeps typed prices | per-port drafts: typed values stay with their port, are NOT carried across; title is "New plan" + the form's own Momentum \| Compounder switch |
| phase124 §7b | row meta `#N · x%` on every row; headers `Risk` / `Out`; blocks stacked vertically | single trade: no entry meta; after ＋ headers `Entry · split` / `SL · out`, two side-by-side columns, Risk per idea above them |
| phase118 A8 | box title `Compounder`; new-plan title `New Compounder plan` | dark box title `Core` + Momentum \| Compounder switch; form title `New plan` + switch state |
| phase89 / 97 / 99 / 113 / 22 | Plan scope = 3 buttons `#scopeStock #scopeLadder #scopeFuture` (Momentum \| Compounder \| Sat) | 2 buttons `#scopeCore #scopeFuture` (Core \| Sat); Compounder is selected with `setPlanScope('ladder')` or the Core-header switch |
| phase97 §2 / §2b (PL2c·10) | on Plan the main tabs shift left, scope 16px from the tabs | main tabs stay exactly where they are on every page (centred); Core \| Sat sits on the right before the action icons (`.hd-plan` rule removed) |
| phase123 §8 | one pinned bar per stock `Homework: ZZZ — thesis + screening · due in 3 days`, `OVERDUE 2 days` | ONE row `Homework [ZZZ 3d] … thesis + screening [Do it ›]` · chips amber / `ZZZ overdue` red · >3 → `+N` expands in place |
| runall2.sh | phases 1–125 | phases 1–126 (new suite `run_tests_phase126.py`) |

New suite: `tests/run_tests_phase126.py` (85 checks at 390 + 1440). Screenshots: `docs/reports/ps1c-shots/`.

### Known failures that are NOT from PS1c (same result on `origin/main`)
phase5, 23, 35, 41–46, 75, 80, 81 (date-dependent), phase13 (always), phase47/66 (removed backup files), phase105 (timeout), phase110 ("Settings = 5 cards" is stale since PS1 added the Portfolio & Risk card).

### Follow-up fix: phase110 stale card count
| Suite / check | Old expectation | Current behaviour |
|---|---|---|
| phase110 "Settings = 5 cards" | `acct · core · sat · prod · app` | 6 cards: `acct · ps1 (Portfolio & Risk) · core · sat · prod · app` (PS1 added Portfolio & Risk). Test updated; passes at 300/390/1280/1440. |

### Follow-up fix 2: Settings save no longer writes `psRisk` unless a Portfolio & Risk field changed
Product fix in `index.html` (not a test whitelist): `ps1FormFill()` snapshots what the form reads; `saveSettings()` keeps `old.psRisk` untouched (or absent) while `ps1FormDirty()` is false. Any edited field writes the full `psRisk` as before.

| Suite / check | Old | Now |
|---|---|---|
| phase110 "save without editing → keys outside owner unchanged" | failed (`psRisk` was added with defaults) | passes **unchanged** (no `psRisk` added to OWN) |

Verified directly: (A) no `psRisk` + untouched save → still absent; (B) custom stored `psRisk` (incl. minStop and an extra key) + untouched save → identical JSON; (C) edit one field → written, other stored values kept; (D) no `psRisk` + edit → created. Suites: phase110 141 pass / 0 fail; phase120 124 pass / 0 fail.
