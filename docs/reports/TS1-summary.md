# TS1 summary

Branch `claude/ts1` (from origin/main 2739856, AW1 merged). **Not merged.**
Commits: brief c60aee0 · §4 1aaf1af · §2 6fd8737 · §1 e3678db · §3 249e74f · §3b 84fe312 + f7a226c (list of deleted paths, a separate commit because folding it in would have needed a force-push) · this summary.
Order note: §4 (node only) and §2 were done before §1 finished because §1 needed a full browser re-run; each has its own commit.

## Headline — read this first
**The regression run is NOT fully green: 34 of 41 items pass, 7 browser suites fail.** I did not hide or retire those 7: each one still has valid checks (36 to 419 passing) and 1 or 2 failing checks that I could not attribute to a deliberate change in a brief / report. They are kept in the run so that red means "look at this". They are candidates for real app findings:

| suite | failing check | what I found |
|---|---|---|
| run_tests_phase373 (PB1 board, 419 pass / 1 fail) | `#hdrPlanBtn` click times out at 390 px | **Real app bug, introduced by AW1.** On the Port tab at 390 px the header ＋ button (x 208–248) is covered by the account-compare label `.hdrCmp` (x 196–230); a tap at the button centre hits the label. Before AW1 (c4bc75b) the button sat at x 196 and was tappable. Not fixed: outside TS1 ("no visible change") |
| run_tests_phase365 (TX1) | archived stock: Restore stays on the card (390 + 1440) | not attributed — needs a decision: test stale or app changed by WL1? |
| run_tests_phase366 (WK1) | Daily line `[data-td3-wnews]` not found on Today › Daily at 390 | LN4 report says the Weekly News line is unchanged, but it is not rendered in the test state |
| run_tests_phase367 (SK1) | stale Skills chips: expects 2 shown + "+1 more", app shows all 3 | LN4 report mentions a "+N more" chip; app now shows all |
| run_tests_phase_cg1 (CG1) | the "pick" guide toast is 4 lines at 390 (limit 3) | toast text is longer than the CG1 limit |
| run_tests_phase_ht1 (HT1) | To do shows 4 stock chips + "+3 ›" at 1280 / 1440, test expects all 7 | chip cap differs from the HT1 rule |
| run_tests_phase122 (PS1b §10-11) | `Not recorded · Ask why ›` line text (390 + 1440) | text differs; the 2 ps1Off checks in the same suite are retired (see below) |

## §1 — tests
**Before** (every browser suite on the base commit, 4 in parallel): 149 suites · **19 pass · 130 fail** (table with first failing check per suite: `docs/reports/TS1-progress.md`).
**Shared causes, fixed first**
- 403 / external frame (`sslecal2.investing.com`): `tests/net_stub.py` answers every http(s) request a suite did not stub itself with an empty 200 (low-priority route on every context); imported by every suite → `run_tests` console check passes, tests never use the network.
- Missing `*.backup-pre-*` / `tests/_bk_*`: 17 static "backup exists" checks removed (phases 41–47, 66, 75). Suites that compare the app with a backup copy were retired (13 of them listed in `_retired/README.md`).
- Hard-coded `/Users/peach/...`: none left (RE-D already fixed them; `grep` clean).
- Click / fill timeouts on the first step: the old Sat Strategy tile page (`.ui-tile`) is in the DOM but never shown — the Plan tab is the PB1 board — so ~60 suites stop at their first click. Not a helper bug; the screen was replaced on purpose (PB1-brief §1, §5).
- Two suites (97, 113) were syntactically invalid (a `# comment` swallowed the closing `)`); repaired — then retired on their real failures.
- After these fixes: 126 still failing, 4 fixed (`run_tests`, 19, 20, 363).

**Dispositions (149 base suites + new `run_tests_ts1`)**
| | count | |
|---|---|---|
| pass in the final run | 22 browser suites + 12 node / sync / syntax checks (aw1 wrapper among them) | |
| **fixed** | 4 + 1 | `run_tests`, 19, 20, 363 (shared causes); `phase35` one check retired by TS1 §2 |
| **retired** (moved to `tests/_retired/`) | 117 | + 2 empty suites + 3 runner scripts;  reason + job per suite in `tests/_retired/README.md`; never counted as pass |
| **merged** | 0 | not done (see below) |
| kept failing (table above) | 7 | |
| empty suites | 2 | phase62, phase88 ran 0 checks (everything already retired inside) → moved (119 suite files in `_retired/` in total), no vacuous pass |
| helper modules | 40 | retired suites whose launchers / fixtures current suites import → `tests/lib_phase*.py` |

Check-level retirements (suite stays, retired check printed as RETIRED, never PASS): `tests/ts1_retire.py` — phase35 (`#satHeatHint`, TS1 §2), phase122 (2 × `ps1Off` mode, RE1-C1 33b4a2f), phase370 + phase372 (AW1 / RE1-C2 chip moves).
Also moved: `runall2.sh`, `make_verify.sh`, `run_related.sh` (old runners, need the removed backup copies) → replaced by `tests/run_regression.sh` (+ `--quick`). `ui_audit` now writes `docs/reports/ui-audit-latest.md`; `UA1-audit.md` is untouched. "How to run tests" added to `tests/README.md`.

**Reasons for retirement are per group (screen), checked against the first failing step of each suite and the named jobs (LN4-report §0, PB1-brief §1/§5, WL1-brief §1, RE1-C1/C2/D summaries). They were not re-derived check by check.** Suites that still have valid checks inside were not split or ported (not done: that is the "merged" path; it needs per-check judgement). `tests/_retired/README.md` says so too.

**Runtime of the regression run:** 967 s (16 min) full, 4 browsers in parallel; `--quick` runs node + 10 core suites.

### Regression run (final, after §3b) — summary lines
```
PASS check_syntax                                        1s  0 checks pass · 0 fail
PASS sync_re1                                            0s  0 checks pass · 0 fail
PASS sync_ps1                                            0s  0 checks pass · 0 fail
PASS sync_core_size                                      0s  0 checks pass · 0 fail
PASS node risk_engine                                    0s  PASS 313/313 risk-engine assertions
PASS node re1_adapter                                    0s  PASS 63/63 adapter assertions
PASS node re1c_live                                      0s  PASS 88/88 live-layer assertions
PASS node core_size                                      0s  1 checks pass · 0 fail
PASS node ps1_size                                       0s  0 checks pass · 0 fail
PASS node ps1b_size                                      0s  0 checks pass · 0 fail
PASS node aw1 (wrapper → run_tests_aw1.py)            77s  SUMMARY: 113 pass / 0 fail
PASS run_tests_re1d                                    187s  SUMMARY: 336 pass / 0 fail
PASS run_tests_re1c                                    171s  SUMMARY: 203 pass / 0 fail
PASS run_tests_re1c2                                    91s  SUMMARY: 155 pass / 0 fail
PASS run_tests_re1b                                     10s  SUMMARY: 19 pass / 0 fail
PASS run_tests_ts1                                      23s  TS1 settings: 26 pass / 0 fail
PASS run_tests_phase364                                 20s  26 checks pass · 0 fail
PASS run_tests_phase374                                261s  SUMMARY: 254 pass / 0 fail
PASS run_tests_phase375                                169s  SUMMARY: 135 pass / 0 fail
PASS run_tests_phase372                                 26s  10 checks pass · 0 fail
PASS run_tests_phase370                                 41s  27 checks pass · 0 fail
PASS run_tests                                           6s  53 checks pass · 0 fail
PASS run_tests_phase1                                    3s  20 checks pass · 0 fail
PASS run_tests_phase2                                    6s  54 checks pass · 0 fail
PASS run_tests_phase10                                  12s  11 checks pass · 0 fail
PASS run_tests_phase19                                  71s  145 checks pass · 0 fail
PASS run_tests_phase20                                  25s  76 checks pass · 0 fail
PASS run_tests_phase35                                  40s  70 checks pass · 0 fail
PASS run_tests_phase49                                  77s  94 checks pass · 0 fail
PASS run_tests_phase50                                  50s  40 checks pass · 0 fail
PASS run_tests_phase51                                 275s  123 checks pass · 0 fail
PASS run_tests_phase57                                  30s  44 checks pass · 0 fail
PASS run_tests_phase363                                 53s  54 checks pass · 0 fail
PASS run_tests_phase_sw2                                24s  33 checks pass · 0 fail
FAIL run_tests_phase122                                 35s  46 checks pass · 2 fail
FAIL run_tests_phase365                                127s  66 checks pass · 2 fail
FAIL run_tests_phase366                                 55s  37 checks pass · 1 fail
FAIL run_tests_phase367                                 50s  16 checks pass · 1 fail
FAIL run_tests_phase373                                454s  SUMMARY: 419 pass / 1 fail
FAIL run_tests_phase_cg1                                30s  44 checks pass · 1 fail
FAIL run_tests_phase_ht1                                54s  39 checks pass · 2 fail
----
regression: 34/41 ok · 7 failing · 967s · logs: <temp folder>/logs
```

## §2 — old hidden Settings cards
Removed markup: `#crSec`, `#satRiskSec`, the hidden `#ps1Sec` rows (weights, Compounder / Momentum / Satellite default · max · cap, total, give-back, loss limits, Legacy limits), the hidden Sat RPT / Max-DD fields and the hidden Sat advanced fields (split, caps, brake, TF, setups), plus the CSS that hid them. Left on screen (unchanged): Pools, capital, fx, Min stop (stocks / per Sat asset), Tactical TP1 / TP1 % / TP2, API key.

| former read site | what it did | replaced by |
|---|---|---|
| `openSettings` (load of ~60 inputs) | filled hidden fields from `coreRiskCfg` / `satRiskCfg` / `psRisk` / `limits` | removed; visible fields only |
| `crOnInput` (validate) | range / order checks of the hidden fields; could disable Save over a value nobody could see | only Pools, TP1 / TP2 (via `satV2Errs` on the stored config + the 3 fields) and min stop |
| `saveSettings` → `coreRisk`, `satRisk`, `limits.port/total` | rebuilt from the hidden inputs, wrote defaults over missing values | carried over untouched (`...old`) |
| `saveSettings` → `satV2` | all 19 fields from hidden inputs + stamps `tfMig` / `poolMig` / `rptNoticed` | stored object + only the 3 visible fields, and only if the user changed them; no stamps (the read-time migration in `satV2Cfg` is unchanged) |
| `saveSettings` → `psRisk` | def / max / cap / total / gb / loss from hidden inputs | stored `psRisk` + `minStop` / `minStopStock` (only when min stop was touched) |
| `ps1FormFill / Read / Errs` | hidden fields | min stop only |
| `satV2FormRead / Fill / Hints` | 19 fields + hints | stored config + 3 fields; hints removed |
| `acctApplyPortVisibility` | per-port show / hide of the removed fields | trimmed |
| `ln3SetBuild` & co (Lean layout, 17 functions) + 2 listeners + `set1RptLive` + `setGo` targets | moved / read the removed nodes; never called since SET1 | removed (zero callers); `setGo` core-risk / sat-risk now just opens Settings |

Stored fields: nothing is stripped from existing data; fields still read elsewhere keep their stored value (they are never touched on save). `tdKey` is not written as `''` when it was absent.
**Proof** — `tests/run_tests_ts1.py` (26 checks, 1440 + 390): no removed id in the page; a **Save with no edits leaves the stored settings object deep-equal, for both accounts**, and a second Save changes nothing; edits to TP1 / TP2 / min stop land and nothing else changes; TP2 ≤ TP1 disables Save; zero console / page errors. (Before the change the same test showed 16 `coreRisk` default fields written by a no-edit Save.) The only thing a Save on a *fresh* book still writes is `pools` (50 / 30 / 20, `reviewed: true`) — by design (RG2b notice "Review the split and press Save"); the test seeds `pools`.
Screenshots: `ts1-settings-1440/390.png` (closed) and `ts1-settings-open-1440/390.png` (every card + Advanced open) are **byte-identical** to the same shots on the base commit (compared with `cmp`).

**Sub-port goals:** kept hidden and untouched — they are not among the §2 read sites and block no test (first case of the brief).

## §3 — dead code
`docs/reports/TS1-removed.md` lists every removed item: 180 function definitions (all with zero users in index.html, tests, tools, scripts), 15 element ids (attribute only), 398 CSS rules + 33 selectors (incl. `.ln4-chip`, `.ln4-x`, the dead `.bd-reason` parts). Already gone before this job: `#mmAcct` / `#acctSel` (AW1), the "Review due" chip branch. Doubtful, not removed: `#crsSetSec` (hidden "Candidate reasons" block), `satV2Fl` / `satV2Pct1` (local helpers the scanner could not parse), anything built from run-time names. Kept as instructed: Tactical (Satellite) hidden, "Legacy" data-shape / migration paths. Tracked `*.backup-pre-*` files deleted (3).
**Proof of no visible change:** 26 screens (Today · Flow · Watch · Plan · Journal · Port · New-plan popup · Core form · Watch full-screen · Settings expanded · second account, 1440 + 390) on the original and on this branch are byte-identical. The first attempt of the CSS cleanup changed two things (the "50%" homework chip background, a collapse arrow) — caught by this comparison and fixed by treating run-time-built class / id names as used. Regression before and after §3: identical (34 / 41, same 7).

## §3b — old files
`docs/reports/TS1-deleted-files.md`: 235 files from docs/briefs + docs/reports and 355 screenshots deleted; 17 files kept because a script / test / index.html / kept doc still reads or links them. Everything stays in git history (before 84fe312).

## §4 — Compounder heat, FX frozen
`re1-adapter.js` (+ inline copy via `tools/sync_re1.py`): the heat check now uses the week-snapshot FX for existing usage (`ideasW`) and the current rate for the new order; no stored rate → current rate. 6 new node checks in `tests/re1c_live_test.js` (heat money = $1,000 × snapshot FX; unchanged when only the current FX moves 35 → 40 → 28; no stored rate → current rate; new-order room line) — they **fail on the old adapter and pass on the new one**. All existing engine tests unchanged: risk_engine 313 / 313, adapter 63 / 63, live 88 / 88 (was 82).

## Not done / open
- The 7 failing suites above (decisions needed; one is a real AW1 layout bug).
- Retired suites were not mined for still-valid checks ("merged" = 0).
- Retirement reasons are group-level inferences backed by the named reports, not per-check proofs.
- `docs/reports/TS1-deleted-files.md` is a second commit (force-push to fold it in was refused).
- `tests/_cg1_shots/` (4 tracked PNGs) and the old `*_retired.md` notes in `tests/` were left (not in the brief's delete rules).

## Screenshots (force-added)
`tests/screenshots/ts1-settings-1440.png`, `ts1-settings-390.png`, `ts1-today-1440.png`, `ts1-today-390.png` (+ `ts1-settings-open-1440/390.png`).
