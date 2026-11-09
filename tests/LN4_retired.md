# LN4 — expectation changes (old tests keep their intent; only the changed behaviour is updated/retired)

Replacement coverage: `run_tests_phase369.py` (Today/Act/Find/Starter/Exec/Watch/Sat rules) and `run_tests_phase370.py` (iPhone 390 audit).

| Suite | Check(s) | Was | Now | Why |
|---|---|---|---|---|
| phase106 | `layout_tests` B1 (order News→Goals→Switch→3 panels→Other; 3 equal columns) | 3-panel Overview · Core · Satellite Today | one status card + Act + Find (+ Details fold) | LN4 §1–3. Retired (function skipped via `LN4_RETIRED`); layout/overflow now in 369/370 |
| phase106 | `other_tests` | `Other ▸` body checks | unchanged feature (dev flag only) but the suite clicked a summary that no longer exists in default layout | Retired |
| phase106 | `news_tests` B2 | "Today's news" block, expandable list | `TODAY` line chips (same HIGH model); detail opens on tap | LN4 §1. Covered by 369 (past/amber<4h/hidden) |
| phase106 | `goals_tests` B3 | per-account goal rows on Today | one `GOAL` line + `Accounts ›` (panel opens on tap, also in Details ▸) | LN4 §1 |
| phase106 | `overview_tests` B5 | Overview panel: Macro + Sectors | `MACRO` line + `HOT` line; sectors block moved into Details ▸ | LN4 §3 |
| phase106 | `sat_tests` B7 | Satellite panel pills | Act › SAT rows (`No plan` + `Create plan ›`) | LN4 §2 |
| phase366 | 7 Daily news line | line inside the Core panel | same line inside the Find card (`[data-ln4-find]`) | selector only |
| phase367 | SK1 Skills-due line (`[data-sk1]`, `.sk1-f`, phone one-row, `+N`) | dedicated line above the switch | chips in To do (rules unchanged → test reads `ln4TodoItems`); `living-thesis +N more` chip; position/phone checks replaced by "chips sit in the status card" | LN4 §1 |
| phase368 | header button/note, change count, group header note | `TradingView · n change` bar + `= READY in TV` note | icon button `TV n` in the header, no bar/note | LN4 §7 |
| phase368 | no reason tag / 12d ⚠ / Drop? banner / Setup ✓ badge | `—` amber · `12d ⚠` · banner row on the 16d row · badge on every row | amber `set reason` · `12d⚠` · tap ⚠ → Drop / Keep 7 more days · Setup ✓ in the tapped row's actions | LN4 §7 |
| phase117 (not in required list) | A6 row dots / Next check / Track chips / Candidate Track + reasons | rich Watchlist row | one tag + age, actions on tap (details live in the detail pane) | LN4 §7. 9 checks fail by design, not fixed |
| phase120 (not in required list) | Form default shares (68 → 17 with Starter ON by default); Portfolio Risk panel + Today `ps1-today` line selectors; Sat 4b "Check Structure first" / sizes / Setup | old rules | Starter ¼ default ON; risk panel now inside Today › Details ▸ (collapsed); Sat verify matrix + Setup 3/3 required (LN4 §4d) | expected; not rewritten |


## Follow-up round — 117 / 120 rewritten (now pass)
- phase117: row status dots → one tag, no dots; Archived toggle read via textContent (sort fold is collapsed); Next check no longer on the row (still built by `wlNextHtml` for the detail); Candidate row = ONE reason tag / amber `set reason`.
- phase120: Starter ON by default → Entry split rows (Now ¼ / Planned total; extra rows = 3); manual ＋Entry/＋SL checks run with Starter switched OFF (intent unchanged); Portfolio Risk panel read inside Today › Details ▸ (opened); Today line = status-card `Risk x / 5% · room yR`; Sat verify matrix (`Need EMA50 or Structure verify`, EMA ✓/Structure ✗ = Counter 60 %), Setup 3/3 ticked, Starter feature Off for full-size maths.
- phase369: S1/S2 updated for split rows; added §8 Plan/Port/Journal checks.
