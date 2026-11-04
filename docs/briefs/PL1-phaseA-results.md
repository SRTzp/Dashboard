# PL1 Phase A — results (overnight run, 2026-11-04 → 11-05)

> **Summary (5 lines)**
> 1. **Built:** Phase A (A1–A8) on `claude/pl1-phase-a` — Add popup + Candidate reasons, screening modal (Trend 40 EMA must-pass), Ready rule (My Thesis ①/④), RS stars, flat 1% Base Risk, Watchlist management + Archive, Compounder = Momentum card layout, Today Plans block; Winner→Momentum / Ladder→Compounder labels. Phase B not started.
> 2. **Tests vs main:** 120 suites on the branch vs 114 on main (+6 new suites: 114–119). Branch: 105 pass / 15 fail → after the one real regression found (phase94, fixed) **all 14 remaining failures also fail on main** (same FAIL lines). PASS lines 12449 (branch) vs 11980 (main).
> 3. **PR:** PR_LINK_PLACEHOLDER (Draft — not merged).
> 4. **Overnight decisions:** 8 small ones, listed below (e.g. Watchlist row status is a dot + tooltip; Sat prompt row kept).
> 5. **Needs SRTp:** dormant ladder-code cleanup PR (~2 weeks after merge), review of the 14 known-failing suites, and your eyes on the screenshots in `docs/briefs/PL1-screens/`.

## What changed (by step)
| Step | Commit | What |
|---|---|---|
| 2 (A4+A3) | `99abdcd` | One Base Risk per trade (default 1% of the pool) stored as `coreRisk.baseRisk`; removed ★→risk (`starBaseRisk/starBudget/starsFromEval/evalGate`) and the open-plan gate; RS stars manual & rank-only (`rs_stars`, Unrated ≠ 0). Old stored numbers untouched. |
| 2b / 2c | `e258b07`, `ffb8c1c` | Labels Winner→Momentum, Ladder→Compounder; "Core"→"Momentum" only where it means that bucket/page. Keys unchanged. |
| 3 (A1) | `d7e5911` | Add popup (Track + ≥1 Reason required per row, Apply-to-all, partial save, quota counts saved rows, success only after write, drafts survive refresh) + Settings › Candidate reasons. |
| 4 (A2+A5) | `6545544` | Screening modal (Fortress / Proven / Emerging / Trend 40 EMA, Weekly=Momentum, Monthly=Compounder; only Pass counts), onboarding record, carry of Track/Reasons/Note/Link/add date; Ready rule = on Watchlist (not archived) + My Thesis ① and ④; Fortress gate for Compounder dropped. |
| 5 (A6) | `2541899` | Status tags, Next check, Track/Reason/RS filters + sort, Archive/Restore, Delete only for empty stocks, `thesis_imported_at`, candidate rows show Track/Reasons. |
| 6 (A8) | `98e2554`, `ba41353` | Compounder = `strategy:'W'` + `track:'ladder'`; Base 1% of the Compounder pool, 5%-of-account cap, ladder FF/DD bucket, manual 40W EMA status; Compounder page uses the Momentum components; ladder page retired (stored ladder data untouched; legacy L cards = read-only line). Archive warning for stocks with an open plan. |
| 7 (A7) | `124032f` | Today › Plans block (Momentum · Compounder · Sat; Draft | Open; ≤5 rows + "+N more ›"). |
| fix | `3655c2f` | Watchlist row status as a dot (the text tag wrapped rows — found by phase94). |

## Test results (RG2b method: runall-style, parallel run then solo rerun of failures)
- Branch: 120 suites → **105 pass, 15 fail** in the run; after the phase94 fix (re-run solo: 32/32) the failing set is the 14 below.
- Main (worktree of `main` @ 3b358b8): 114 suites. The main worktree lacked local, git-ignored backup files (`index.backup-pre-*.html`), so 18 main suites were re-run after copying those files into the *temporary worktree* (not the repo). Main then fails: p13,p22,p23,p40,p41,p42,p43,p44,p45,p46,p47,p5,p66,p73,p75,p80,p81.
- Branch failing set: p13,p23,p41,p42,p43,p44,p45,p46,p47,p5,p66,p75,p80,p81,p94 (p94 is fixed since). **Every branch failure is also a main failure with identical FAIL lines** (p5, p23, p75, p80, p81 compared line by line; p13 and p41–p47/p66 are missing-backup/`_bk_*` folder or `index.backup-pre-UI1.html` checks).
- Branch passes p22 / p40 / p73, which fail on main only because of a tracked/ignored-file difference (`tests/_extracted.js`, backup-folder checks).
- New suites (all pass): phase114 (53) · 115 (56) · 116 (67) · 117 (64) · 118 (52) · 119 (26). `core_size_test.js` 502/502, `sync_core_size --check` OK, `check_syntax` OK.
- Every changed/retired expectation is logged in `tests/PL1_retired.md` (incl. a "TEST STUBS" section: `READY_STUB` in `tests/ff_stub.py` and `tests/scr_helper.py`; phase116 runs the real `wlReady`).
- Logs: `_to_delete`-style folders are not committed; full-run TSVs were kept in the job dir (`full_branch/final.tsv`, `full_main/final.tsv`).

## Screenshots (390px + 1440px) — `docs/briefs/PL1-screens/`
`add-popup`, `screening-modal`, `watchlist-rows`, `watchlist-card`, `compounder-page`, `compounder-page-lean`, `today-plans` (each `-390.png` / `-1440.png`); `overflow-log.txt` shows horizontal overflow = 0 for all. No styling changes were made for the shots. Sample data only.

## Decisions made overnight (least-code option, logged)
1. Watchlist **row** status = coloured dot + tooltip/aria-label; the full "Drafting Thesis / Awaiting Setup / Plan Ready" tag is on the **card** (the text tag wrapped rows; phase94).
2. Today Sat rows keep `Selected this week` as the info text for "No plan" rows; link labels (`Criteria ›`, `Continue ›`, `Open ›`) unchanged.
3. The Sat group stays visible whenever the week has assets (or the "No assets selected — Pick assets ›" prompt); only Momentum/Compounder groups are hidden when empty.
4. Compounder page also works in non-Lean ("legacy") mode: same track filter and a read-only ladder row.
5. After saving a plan the page switches to the plan's track (Momentum/Compounder) so the new card is visible.
6. Archived stocks: hidden behind "Archived (n)", excluded from Today deep-dive queue and the plan form's ticker list; open plans/positions untouched.
7. For the main baseline, local ignored backup files were copied into the temporary worktree outside the repo (no repo files touched).
8. `phase25` timed out once in a parallel batch and passed on a solo rerun (load flake).

## Needs SRTp
- **Dormant ladder code** (`coreLCardHtml`, ladder form/budget code, `coreLadderTableHtml`, etc.) is still in `index.html` but unreachable. Plan: separate cleanup PR after Phase A has run ~2 weeks without problems.
- The 14 pre-existing failures (p5, p13, p23, p41–p47, p66, p75, p80, p81) — environment/date/backup-folder related; not touched.
- Visual review of the screenshots (no styling pass was done).
- Stored-data additions to be aware of (all additive, nothing migrated/deleted): Watchlist doc `rs_stars`, `rs_rated_at`, `reasons`, `link`, `cand_added_at`, `onboarding`, `my_thesis`, `archived*`, `next_check_*`, `thesis_imported_at`; settings `candReasons`, `coreRisk.baseRisk`; `candMeta` `track/reasons/note/link`; Core card `track:'ladder'`, `emaW40`. Watchlist/settings paths are unchanged, so no new Firestore rules are needed.
- Phase B (My Thesis 5 sections, Previous Notes, AI thesis versions) not started.
