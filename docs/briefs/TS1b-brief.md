# TS1b — green test suite · Watch clean-up · Archived view

Approved by SRTp 17 Nov 2026. Base: latest `origin/main` **after EF1b is merged**. Branch: `claude/ts1b`. Commits: A tests green → B Watch clean-up → C Archived view + C2 port colours → D report, push each.
Lean UI rules apply (no new panels; each screen same length or shorter; report row counts at 390). No data migration, no deletes of stored fields. English UI.

## A · Make the regression suite green (7 failing on main: phase122, 365, 366, 367, 373, cg1, ht1)
For each failure: decide **app bug** (fix the app) or **outdated test** (update the test to the approved behaviour), and list it in the report with the reason. Starting points from the earlier triage:
- App: `＋` button covered by the account-compare label on Port at 390 (AW1); the 4-line "pick" guide toast; phase373 `[390] Locator.click` timeout (find the covered / off-screen element).
- Tests: To do chip cap (4 + "+N ›"), Skills chips show all 3, wording "Not recorded · Ask why ›".
- Investigate: Weekly News line missing on Today › Daily at 390 — restore it unless a merged job removed it on purpose (name the job).
- Harness: `tests/re1d_common.py` stubs `tv1SetupLeft = ()=>1` — remove the stub so suites see real Setup behaviour (EF1b note).
Goal: `tests/run_regression.sh` = all suites pass.

## B · Watch clean-up (settings frozen since TS1, decided 17 Nov)
Remove UI and the leftover readers; keep every stored field untouched:
- **RS rating stars (★0–3, `rs_stars`)** on Watch rows + the star sort (`star` at ~9079) + `wlStarSet`. Automatic RS (Fund-flow / RRG) replaces it.
- **LN4 Starter / stage** UI and code paths gated by `ln4Feature()` (feature is off since RE1; user does not use it): starter checkbox rows, stage labels, `LN4_FRAC` paths. Sizing must not change (verify with node suites + `re1c_live_test`).
- **Stock phase / tier** readers (`tqCode`, phase / tier chips and filters) — no setter exists.
- **Watch filter / sort state** readers with no setter: `wlTrackF`, `wlReasonF`, `wlRsF`, `wlSortMode`, `wlHotFirst` (keep `wlShowArch` logic only if reused by C).
- `keep_until` comment.
List every removed function in `docs/reports/TS1b-removed.md` and grep that no remaining code reads a removed name.

## C · Archived view (option A)
- One line at the bottom of each Watch list: `Archived (n) ›` (hidden when n = 0). Tap → expands in place a compact list: ticker · archived date · reason · `Restore`. Tap again / `Show less ‹` collapses.
- Restore uses the existing `wlRestore`. Archive flow (`wlArchiveOpen`, reason required) unchanged.
- Archived stocks stay out of lists, deep-dive queue, Today homework and plans (unchanged).

## C2 · Port colours (Today › Act + same tags everywhere)
- One colour per port, used only for the port tag chip and a 3 px left bar on each Today › Act row (Enter / Check orders / Manage): **SAT = purple** (existing `--sat` / `--satbg`), **MMT = blue** (`#2f5bd3` text on `#e8eefc`), **COMP = teal** (`#0f766e` text on `#e3f3f1`). Define as CSS variables (`--port-sat`, `--port-mmt`, `--port-comp` + bg) and reuse them for the same tag chips on the Plan board, drawer and confirm sheet so the colours match everywhere.
- Do not colour numbers, buttons or status words (green / red / amber keep their meaning: gain / loss / warning). Contrast ≥ 4.5:1 for chip text; works in dark mode if the app has it.
- No layout change, no new rows.

## Tests / proof
- `tests/run_tests_ts1b.py`: Archived line count, expand / collapse, Restore puts the stock back in its list; no RS stars / Starter / phase / tier UI left; no overflow 1440 / 1280 / 390.
- Node suites unchanged: risk_engine 313, re1_adapter 63, re1c_live 88, rm1_engine 43, pv1_posview 44, core_size, ps1_size, ps1b_size.
- Full `tests/run_regression.sh` result in the report (target: 0 failing).
- Screenshots (`git add -f`): `ts1b-watch-390`, `ts1b-archived-open-390`, `ts1b-port-390` (＋ button visible), `ts1b-today-act-390` (three port colours).

## Report — `docs/reports/TS1b-summary.md`
Per failing suite: cause · app fix or test update · reason. Removed items (B). Row counts at 390. Anything uncertain → ask, keep the rest.
