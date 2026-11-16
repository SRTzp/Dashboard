# TS1 — test clean-up + old Settings cards + left-overs

Agreed with SRTp 16 Nov 2026. Run **after AW1 is merged**. Base: latest `origin/main` (must contain `tests/aw1_test.js`; if not, stop and say so). Branch: `claude/ts1`.
Read first: `docs/reports/RE1-D-summary.md` §3, §4 (table of 131 failing suites) and "Unresolved".

## Goal
One trusted test run that is green on main, no hidden dead Settings markup, no known left-overs. **No visible change for the user** except where stated. No change to risk rules except §4.

## Rules for this job
- Never make a test pass by weakening a check that still describes current behaviour. A check is retired only when the feature / text it tests was removed or redesigned on purpose — name the job that removed it (from briefs, reports or git log).
- Nothing is "retired and counted as PASS". Retired suites are moved, not run.
- No deletes of user data, no change to the stored data shape. `render()` stays pure.
- Order: §1 → §2 → §3 → §3b → §4. Commit + push after each section; keep `docs/reports/TS1-progress.md` current.

## 1 · Tests
1. Run every suite on the base commit; save the table (suite · pass/fail · first failing check) as the "before" in the progress file.
2. Group the failures by **first cause**, fix shared causes first, then re-run before judging single suites:
   - 403 on an external resource → block / stub external requests in the shared test setup so tests never depend on the network.
   - Missing `*.backup-pre-*` files / `tests/_bk_*` folders → those checks are obsolete (backups live in git history): remove the checks; if a suite only checked that, retire it.
   - Hard-coded `/Users/peach/...` paths → relative to the running worktree.
   - Click / fill / select timeouts on the first step → usually an old selector, old tab name or a removed screen. Check the shared open-the-app / go-to-tab helpers first.
3. Then per suite, one of: **fixed** (selector / text updated, same intent) · **retired** (feature removed — say by which job) · **merged** (still-valid checks moved into a current suite).
4. Retired suites: `git mv` to `tests/_retired/` with a one-line reason in `tests/_retired/README.md`. Suites named `*.backup-pre-*` are old copies → retire.
5. Regression set: add `tests/run_regression.sh` (or the repo's existing runner style) that runs, in order: `check_syntax`, sync tools check, the 3 node tests (`risk_engine`, `re1_adapter`, `re1c_live`), `aw1_test.js`, and every remaining browser suite. Exit non-zero on any failure, print one summary line per suite. Target: **all green, under ~15 minutes**; if slower, split into `--quick` (node + ~10 core browser suites covering Today, Plan board, plan forms ×3 strategies, Cancel, Journal, Port risk, Settings, snapshot) and full.
6. `ui_audit` must write to `docs/reports/ui-audit-latest.md` and stop overwriting `UA1-audit.md` (restore `UA1-audit.md` from git if it was changed).
7. Add a short "How to run tests" section to `docs/GUIDE-daily-use.md` or `tests/README.md` (5 lines).

## 2 · Old hidden Settings cards
- Remove the markup of `#crSec`, `#satRiskSec`, the extra `#ps1Sec` rows and the old Sat RPT / DD block, plus their handlers.
- Rewrite the ~40 read sites (Settings load / validate / save, Lean layout) so they no longer read those DOM nodes. Stored fields that other code still reads keep their current saved value (carry over on save — do not write `undefined`, `NaN` or defaults over them). Fields nothing reads any more: stop writing, do not strip from existing data.
- Proof in the summary: for each removed id, the list of former read sites and what replaced them; a test that opens Settings, saves with no edits, and shows the stored settings object is deep-equal before / after (both accounts); Settings screenshots before / after at 1440 and 390 are visually the same.

## 3 · Dead code
- Remove dead CSS `.ln4-chip`, `.ln4-x`, unused parts of `.bd-reason`, and anything left unused by AW1 (old `#mmAcct` / `#acctSel` styles and helpers, old "Review due" chip branch). Grep to prove zero users before each removal.
- Tracked `*.backup-pre-*` files in the repo: remove if nothing loads them (they stay in git history). Do not touch untracked files in the user's main folder.
- **Unused scan:** list every function, CSS rule and element id in `index.html` and the `.js` files with zero users (count inline `onclick=` / template strings / tests / tools as users). Remove the ones with zero users; anything doubtful → list in the summary, do not remove.
- **Keep, do not touch (user decisions 16 Nov):** Tactical (Satellite) stays hidden as it is. "Legacy" data-shape / migration paths stay (separate later job).
- **Sub-port goals:** keep hidden as they are, unless their code is among the §2 Settings read sites or blocks a test — then remove the UI and code but keep the stored values untouched. Say which case applied.

## 3b · Old files in the repo (user decision: delete what is no longer used)
- Before deleting anything: grep code, tests, tools, scripts and the kept docs for the file name; a file that is read or linked stays.
- `tests/screenshots/`: delete all except `re1d-*`, `aw1-*`, `ts1-*`.
- `docs/briefs/` and `docs/reports/`: delete everything except — `RE1-tech-spec.md`, `RE1-decisions.md`, `RE1-answers-A.md`, `AW1-brief.md`, `ac1-switch.html`, `TS1-brief.md`, `RE1-D-summary.md`, `AW1-summary.md`, `TS1-*.md`, `UA1-audit.md`, `ui-audit-latest.md`, and anything the grep shows is still read. `docs/GUIDE-daily-use.md` and other top-level docs stay.
- One commit for this section only, with the full list of deleted paths in the summary (everything stays in git history).

## 4 · Compounder heat — FX frozen (only rule change)
- The Compounder heat check must use the same frozen-FX basis as the other limits (week snapshot rate for existing usage, current rate for the new order; no stored rate → current rate). Add node tests next to the existing FX tests: heat does not move when only the FX rate moves after the snapshot. All existing engine tests stay green with unchanged expectations — if one must change, stop and report instead.

## Report
`docs/reports/TS1-summary.md`: before / after table (pass · fixed · retired · merged, with reason per retired suite), runtime of the regression run, §2 proof, list of every removed function / id / CSS rule with its last caller, anything not done and why. Screenshots (`git add -f`): `ts1-settings-1440`, `ts1-settings-390`, `ts1-today-1440`, `ts1-today-390`.
