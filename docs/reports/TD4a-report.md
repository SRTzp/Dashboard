# TD4a report

Scope: brief §1 (except the MA rename), §2, §3, §4, §6, plus the two small fixes. The ★ FINAL Core panel spec and User additions 4 supersede all earlier Core/Candidate numbers. §5 and the MA rename are left for TD4b.

**No push. No file deleted. Firestore rules not deployed and not changed. `core-size.js` untouched.**

## Results
- Full run `tests/runall2.sh` (output in `_to_delete/runall_b`): 106 of 108 suites ok.
- Two failures, both known from before this round: **phase5** (Break Price) and **phase13** (DD1). Neither is caused by TD4a.
- phase33 failed in the full run. I fixed the test (see retired log) and re-ran it solo: 69/69. I replaced its row in `final.tsv` with that result. The failing log is kept as `logs_rerun/run_tests_phase33.before-fix.log`.
- New suite `phase107`: 325/325.
- `check_syntax` OK · `core_size_test` 471/471 · `sync_core_size --check` OK.
- Verify file: `docs/reports/TD4a-verify.txt`, built by `bash tests/make_verify.sh TD4a`.
- Backups: `index.backup-pre-TD4a.html` and `tests/_bk_td4a/`.

## Entry points blocked (B4)
A new Watchlist doc can only be created by Promote from a Candidate (`td4ProSave`).
- The `＋` button, `wlOpenAdd` and `wlAddSave` for a ticker not in Watchlist or Candidates show "Add it as a Candidate first". The modal links to Candidates and Today › New Cand.
- Import Thesis for a new ticker is rejected in `ltImpCheck` and `ltImpSave`.
- "บันทึกเฉพาะ Tier" for a new ticker is blocked in `coreTierOnlySave`.
- Still working: existing Watchlist tickers, existing Candidates, `ideaToWatchlist` and `ideaCandAdd`.
- Generic backup restore is untouched.

## Segment-link source
It is not in the add form. It is the existing `wlRevBtnHtml` from the Watchlist/Candidate detail. The Core panel reuses it with the label shortened to `Revenue ↗`.

## Deep-dive done rule
A market is done when at least one thesis part is saved today for that market's stock. The state is kept in `routineLog[day].hwm[US|TH]` as `{pick, parts, d, seen}`. `d` is the number of dives finished earlier today and `seen` is the picks already offered. `Next from Watchlist ›` picks by stars (high first), then the oldest without a complete thesis. The legacy `hw` field is still mirrored.

## Data added
- Settings: `candMeta[KEY]` gains `dismissed`, `dismissed_at`, `asked_stamp`, `restored_at`, `market`.
- Settings: `candAddLog{day:[KEY]}` is the daily New Cand quota, so deleting a candidate doesn't refund it.
- Settings: `newsRead{day:[eventId]}` keeps 7 days.
- Settings: `routineLog[day].hwm`.
- Watchlist: `promoted_by` (array of `tier`/`rs`; the old string is still readable), `promoted_at`, `stars` (0–3), `promote_reason` (read-only, unused).
- Ideas: `imported_at`.
- localStorage: `dash.td4Mk`, `dash.td4ScrMk`, `dash.td4HwMk`, `dash.td4Draft`, `dash.td4Batch`, `dash.td4RemDismiss`, `dash.td4RemNotif`.
- Firestore rules: no change needed.

## Decisions (made by the brief, not asked)
- TH tickers are stored as `XXX.BK`. Candidate keys strip `.BK`.
- The Candidates filter is labelled All/US/TH.
- Reminder:
  - It runs on weekdays only, after 20:00 ICT.
  - It checks only the minimums: Deep dive US 1 + TH 1, Cand→WL 3, New Cand 3, plus Satellite rows.
  - It shows an in-app banner, dismissable until tomorrow.
  - The browser Notification fires once per day, and only if permission is already `granted`.
  - Settings › Daily routine has an `Enable reminders` button.
- Stars: the interactive control sits in the Watchlist detail header. List rows show a compact `★n` only when rated, so dense rows (BRK.B) stay on one line.
- The Today sector row drops the delta word and shows `SYM name · PHASE · N d · off%` plus the ↗ chip.
- New Cand: duplicates are dropped silently, invalid tickers stay in the box, and over the cap of 10 the box keeps the extras with `Daily limit 10 reached`.
- Delete: an idea-derived candidate is marked dismissed. A manual-only candidate is removed after a confirm.
- The "Next batch" state is kept in `dash.td4Batch`.
- Other small fixes: `บัญชีหลัก` shows as `Main` on Today, and the Flow error row now says `No data`.

## Files changed
- `index.html` (+518/−107).
- New `tests/run_tests_phase107.py`.
- Old tests patched: phase20, 22, 29, 33, 40, 41, 44, 84, 85, 105, 106, plus `tests/pf2_retire.py`.
- `tests/runall2.sh` now runs 1..107.
- `tests/TD4a_retired.md` logs 17 entries; each is a changed expectation, none is a deletion or weakening.
- Docs: this report and the verify file.

## Screenshots opened
All in `tests/screenshots/`. Re-opened after the final spec: `td4a-newcand-390.png` and `td4a-promote-390.png` (both match the spec). Opened earlier, before the final spec changes: today-1440, cands-390, reminder-390, flow-fields-390 and watchlist-1440. Not opened: `td4a-today-390.png`.

## Limitations
- Notifications need browser permission and a tab that is open. The in-app banner is the dependable path.
- The reminder is evaluated every 60 s while the app is open. It does not run in the background.
- phase5 and phase13 still fail as before.
- The screenshots from before the final Core spec were not all re-viewed.
