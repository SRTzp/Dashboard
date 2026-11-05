# TD3a report — Today: "What do I need to do next?"

No push. No file deleted. Firestore rules: not deployed (see "Data added").
Backups: `index.backup-pre-TD3a.html` (sha256 a6b62c23…bb614) and `tests/_bk_td3a/` (every test file as it was before; five files I edited without a backup first — phase39/81/82/84/100/101 and pf2_retire — were rebuilt by reversing my edits, so those copies are reconstructed, not byte-for-byte).
Verify file: `docs/reports/TD3a-verify.txt` (built by `bash tests/make_verify.sh TD3a`).

## B0 findings (checked before building)
- **Candidates are not a standalone list.** `ideaCandRows(inList)` derives them from ideas (`ideaCounted()` → `v.cands`, state ≠ park) minus anything already in the Watchlist. There was no "add candidate" path and no `cand_at`.
  Decision: new `settings.candMeta{KEY:{note,cand_at,manual,market,sym,screened_at}}`; `ideaCandRows` appends `manual:true` entries so the Watch tab shows them (one list, not a second data model). Idea-based candidates without `cand_at` use the idea's `created_at/as_of/date/user.updated_at`, otherwise sort last.
- **Promotion** reuses the `wlAddSave` write shape (`ticker, market, port:'core', note, industry, added_at` + `tqCarryOf`) plus `promoted_by` / `promoted_at`. Undo deletes the watchlist doc and leaves `candMeta` untouched, so Undo restores exactly.
- **Sat plan status** is read from `satIdeasList` (v3/v2 ideas; sleeve; `setup_ck` in PF_SETUP_CK; bias/entry/sl/tp), `satV3PlanRowState`, `satV3ClosedKind`, `satV3ReadyCount`, `satV3EffectiveTrades`. Selected assets: `satWeekPickList()` / `satAssets()`.
- **Weekly Impact has no per-event impact field** (impact is per asset: `assets[KEY].impact`). Rule used: an event is HIGH when any linked, picked asset's tier in that doc is HIGH. `wiTodayModel(now, opts)` gained `opts.released` so released events stay (dimmed, with actual).
- **Goals** are per account `{cur,start,startDate,target,deadline}` + `goalLog`. **Port has no sub-portfolio values** (Core.US/TH are only watch-market filters) → new `settings.subGoals{acct:{Core.US|Core.TH|Sat|Option:{cur,start,target,deadline,startDate,now}}}` with a **manually entered current value** (the "else" branch of the brief).

## Data added (all inside existing documents — no new collection, no rules change)
- `users/{uid}` settings (book `settings`): `candMeta` (note, `cand_at`, `screened_at`, manual, market, sym), `subGoals`, `satWeekNoTrade{weekKey:[satKey|'*']}` (the **not-trading flag**, stored beside `satWeekPick`; `'*'` = whole week), weekly tick ids `wk_macro`, `wk_cands`, `wk_picks` in the existing `weekLog[Monday].done`.
- `users/{uid}/watchlist/{TICKER}`: `promoted_by` (`tier`|`rs`), `promoted_at`.
- Device only (localStorage): `dash.td3Other` (Other fold open/closed), `dash.pbOpen` (Flow Quarterly Macro open preference).
- Firestore rules: nothing to deploy — existing paths only.

## What was built
Lean Today (legacy Today unchanged), top to bottom: News box · Account goals · Daily|Weekend switch (red badge n/m) · 3 panels (Overview · Core Port · Satellite) · "Other ▸".
- **News**: HIGH only, English, live countdown (`in h:mm:ss`, red under 1 h, shown under 4 h), collapsible rows (next event open), US-calendar button jumps to Flow and opens the calendar, released events stay dimmed with the actual, empty state.
- **Account goals**: one collapsed line per account (progress bar · % · elapsed `3m 12d` · pace On track/Ahead/Behind); expands to the four sub-portfolios; "Start date not set" / "No goal set" cases. Settings › Goals has the sub-goal editor (writes only `subGoals`; other settings byte-identical, tested). Added a **＋ Enter account value** button so the portfolio value can still be logged from Today.
- **Overview / Core / Satellite panels**, Weekend checklist (7 items, 6 counted; auto items `wk_news`, `wk_impact`, `wk_assets`; manual `wk_macro`, `wk_cands`, `wk_picks`; `wsector` shown, not counted), Not-trading toggle on Plan › Sat asset cards, Flow Quarterly Macro open by default on Mac.
- **Core**: screening queue (Tier passed / RS Leader promote to Watchlist, 5 s toast with Undo, "Not passed"), add candidate with note, homework + "If time permits".
- **Other ▸ is lazy (B1 addition)**: closed = no DOM and no work for its items; built only when opened and re-rendered on refresh only while open. phase106 checks: closed → none of its items in the DOM; open → they render and work (tick, tasks, Daily/Weekly).

## Decisions made without the user (brief-first)
1. Candidate store `candMeta` + merge into `ideaCandRows` (above). 2. Sub-goal current value entered by hand; currency is a per-sub select. 3. Event HIGH rule derived from asset tier. 4. Saved-plan row hides SL first, then TP, via container queries at 340/270 px. 5. "Pending" uses the app's own criterion names without "on minor"; fields complete but not ready → "Incomplete · Check the plan before saving". 6. Screening queue order: unscreened first, oldest first, previously screened at the back. 7. Not-trading flag lives in `satWeekNoTrade`. 8. News box keeps the WM1 picked-assets filter. 9. Console errors from the external `ffCal` iframe (403 / X-Frame-Options) are filtered in tests as external. 10. Other-fold state in `dash.td3Other`; Flow Macro preference in `dash.pbOpen`. 11. Wrap rule `overflow-wrap:anywhere` on panels (long URLs overflowed in the sample). 12. Settings sub-goal inputs are 16 px on narrow screens (p56 iPhone-zoom check caught 13.6 px). 13. Old-selector aliases kept on news rows/buttons (`data-wi-td`, `data-wi-state`, `data-wi-res`, `data-wi-upd`).

## Files changed
`index.html` (+550/−33 at verify time: TD3a module replacing `tdHtmlLean`, `wiTodayModel` opts, `ideaCandRows`, `wlItems` mapping, `ln3WlRowHtml`, Settings sub-goals, Plan›Sat Not-trading button, Flow `pbOpenInit`, `.td3-*` CSS) · new `tests/run_tests_phase106.py` · `tests/runall2.sh` (seq 1..106) · `tests/pf2_retire.py` (+`retired_td3a`, `PANELS_JS`, `panels_ok`) · old suites with expectation changes: phase39 (launcher), 81, 82, 84, 90, 94, 100, 101, 102, 103, 104, 105 · `tests/TD3a_retired.md` (18 entries). `core-size.js` not touched.

## Test results (full run, `tests/runall2.sh`, once, then automatic solo rerun)
- Suites: **105 / 107 ok** (base + phases 1–106). Failures after solo rerun: **phase5** and **phase13** — the known, pre-existing failures (phase13 = DD1 note; phase5 = Break Price save). Not caused by TD3a; not touched.
- **phase106: 219 / 219**. check_syntax OK · core_size_test 471/471 · sync_core_size --check OK.
- Old-suite expectation changes (18 rows, `tests/TD3a_retired.md`): English labels, HIGH-only news, Not-trading button, goals box, and the two-column/tdBalance balance cases retired → replaced by "3 panels top-aligned, no overflow". Nothing deleted or weakened.
- Note: phase106's first full pass had one flaky `Locator.check()` on a re-rendering checkbox; changed to `.click()` (same assertion afterwards).

## Screenshots opened and inspected
td3a-today-1440, -1280, -390, -300, td3a-weekend-1440, -390, td3a-news-390, td3a-core-390, td3a-sat-390 (all nine). Findings fixed: long URL overflow in Overview; goals box lacked value entry. No remaining visual problems seen.

## Limitations
- Core has no draft-plan concept (plans lock on save), so "unfinished Core plan drafts" only covers Core cards with `status==='plan'`, non-L strategy, missing entry or stop.
- Event impact is inferred from asset tier (no per-event field in Weekly Impact).
- Sub-portfolio values are manual (Port has none).
- The Watch tab reorder (TD3c) is out of scope.
- Next-day Today no longer shows yesterday's unreleased events (today's events only, per the HIGH-only box).
- The `verify` "files changed" list shows a few touched docs/md files from earlier rounds' timestamps; only the files named above were edited by this round.
