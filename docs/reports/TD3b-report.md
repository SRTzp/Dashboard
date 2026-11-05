# TD3b — Sector Drivers & Evidence (Flow RRG → Today)

Backups: `index.backup-pre-TD3b.html` · `tests/_bk_td3b/`. Verify file: `docs/reports/TD3b-verify.txt` (built mechanically by `bash tests/make_verify.sh TD3b`). No push, no file deleted, no Firestore rule deployed.

## 1. Settings doc verification
- Store: `getBook(tdHome()).settings.sectorNotes[SYM]` (home = `acctList[0]`), written with the GL1 pattern `glWrite → saveBook → doPersist`. No new collection.
- **Merge behaviour:** `doPersist` writes `set(payload, {mergeFields:['_v','accounts','activeAccount','books.<id>', …]})`. It replaces the whole `books.<id>` map from the in-memory book — it does **not** merge field-by-field inside `settings`. Other accounts' books and top-level fields are untouched. The in-memory book is kept live by `onSnapshot` (and `pendingLocalWrite` blocks stale snapshots), so unrelated settings are preserved (tested: deep-compare of settings minus `sectorNotes` before/after follow / save / mark-reviewed is identical; `sectorNotes` appears only at `books.main.settings.sectorNotes`, not at doc root).
- Brief B1 asked for a field-path update only if the *whole doc* were written. It is the whole *book* (the app-wide pattern used by routine / goals / weekLog), so I kept the standard path rather than adding a second write path that would race with `pendingLocalWrite`. Residual risk (same as every other setting): two devices editing the same account's settings within the same few seconds — last writer wins for the book.
- **Rule:** notes live inside `users/{uid}` (`books.<id>.settings`), already covered by the existing rule for that doc. No rule change needed (nothing to deploy). The rules file is not in the repo, so I could not read it — please confirm in the console that `users/{uid}` write is allowed for the owner (it must be, since all settings already live there).

## 2. Files changed
- `index.html` — new module `SD_*/sd*` (before `ffRenderThemes`), `tdSectorsHtml()`, `rrgSortRows()` (sort extracted unchanged), English labels via optional `en` arg on `rrgLevel/rrgDeltaHtml/rrgGaugeHtml` (legacy callers unchanged), lean row markup, CSS block, `#ffThemesTitle`, Today insertion (Mac right column after Port goal; iPhone after the goal line), `tdBalance` anchor (moved cards go after the Sectors block), weekly task `wsector` + `Flow ›` link, name-cap exemption for default task names.
- Tests: new `tests/run_tests_phase105.py`; expectation updates in `run_tests_phase56/94/102/103/104.py` (logged in `tests/TD3b_retired.md`); `tests/runall2.sh` (1–105); `tests/make_verify.sh` (ignores `*.backup-pre-*.py`).

## 3. Timeframe / stale / missing data
`sdCur(sym, tf)` reads only the cached RRG (`ffState().rrg`) — Today never calls `rrgRefresh` (tested). Valid = cache day is today (`rrgToday()`), both `rowsD` and the requested tf's rows are non-empty, the sector's row exists, has no `err` and has a known quadrant. Otherwise: no flag, Today phase `—`, Save & mark reviewed stores `reviewed_phase/reviewed_tf = null` ("Reviewed <d> · phase not recorded"; never flags later). The flag compares only against current data of the **same tf** as `reviewed_tf`, regardless of which tf the Flow toggle shows. Flow rows keep showing whatever rows are cached (existing behaviour); only the record/flag logic requires fresh data.

## 4. What was built
Flow (lean view): ☆/★ before the symbol (≥32 px hit area, stops propagation); whole row tappable / Enter / Space, `role=button`, `aria-expanded`; collapsed "Drivers & evidence" line (Reviewed d MMM (Phase · Daily/Weekly) · tag · "Drivers not yet recorded" · "Supporting evidence not yet recorded."); expanded form (Driver, Evidence + ≤3 link chips, Revisit if, meta line separating AI research date from your review date, Copy AI prompt, Import answer, Save, Save & mark reviewed); unsaved text survives re-render; English labels; ↗ chip; header **Leadership**; one footer line. Import dialog reuses `#ltOverlay`; validation per Part A/B5; invalid import never touches the stored note. Today: `Sectors` block (followed only, Flow order, phase colour, Δ word, ↗ chip, tag, driver ≤80 chars, "Reviewed Nd ago", empty state). Weekend: one manual weekly task "Review drivers for selected sectors" with `Flow ›` link, no counter, no auto-complete.

## 5. Test results
See the numbers filled in below (full run via `tests/runall2.sh`).

Full run `tests/runall2.sh` (base + phase 1–105, 106 suites; solo rerun of failures): **104/106 suites pass**.
- New `phase105`: **204/204** checks (follow/unfollow, Save vs Save & mark reviewed, flag cases incl. tf mismatch / err / stale / no cache, 19 invalid-import cases byte-identical, prompt contents, reload persistence, Today block + navigation, weekend task, keyboard, legacy view, 300/390/1280/1440 no overflow, no console errors).
- Failing after solo rerun — both known and unrelated to TD3b:
  - `run_tests_phase5`: `FAIL - [chromium/1440px] พิมพ์ในช่อง Break Price แล้วกด [บันทึกแผน] ค้าง 300ms → คลิกไม่หาย (planned=true) …` (and the same at 430px) — pre-existing.
  - `run_tests_phase13`: fails with no FAIL lines (known).
- `check_syntax` OK · `core_size_test` 471/471 · `sync_core_size --check` OK. `phase94` stays at the approved 35% balance threshold (PF3b); this run also covers the pending PF3b re-run.
- Expectation changes (9 entries, `tests/TD3b_retired.md`): phase56 (weekly task count/indices, 5 default tasks), phase94/102/103/104 (new Sectors block sits between the Port goal and moved cards). Balance thresholds were **not** relaxed (empty Sectors state is a one-line row).
- Earlier in the round: first full run flagged phase56/94/102/103/104 for the reasons above; these were test-expectation / layout fixes (empty-state made a slim line to keep ≤15% balance), not behaviour regressions.

## 6. Screenshots (all five opened and looked at)
`tests/screenshots/td3b-flow-1440.png`, `td3b-flow-390.png`, `td3b-import-390.png`, `td3b-today-1440.png`, `td3b-today-390.png`.

## 7. Header wording conflict
The legacy-view header `เงินไหลเข้าธีมไหน` ("where is money flowing into") still says it; I only changed the lean header to **Leadership** as the user asked. The legacy header conflicts with the new footer ("not proof of fund inflows"); legacy view also has no footer/☆ by design (B1).

## 8. Limitations
- Accepted: a sector that changes phase and returns to its reviewed phase between checks shows no flag (no phase history).
- Existing users with a **customised** `weekTasks` list will not get the new weekly task automatically (only the default list gained it); add it in Settings → Daily routine.
- Today shows phase `—` until that day's RRG refresh has run (it never fetches).
- Mac Today: when no sector is followed the block is a single muted line (not a card) so column balance (≤15%) is unchanged; with followed sectors the full card appears and `tdBalance` picks the best arrangement.
- Default weekly task name is 35 chars (> the 30-char custom-name cap); default names are exempt from the cap.
- Structural JSON validation does not verify the research.
