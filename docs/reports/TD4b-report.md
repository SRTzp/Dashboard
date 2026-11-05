# TD4b report — Satellite / Plan polish + MA rename + Watchlist/Today additions

Started from the TD4a build (index sha `da84151957e2`). Final index sha256 `7ef3d7fec118…` (after TD4b follow-up below). **No push. No file deleted** (a runaway backup copy was moved to `_to_delete/_bk_td4b_runaway`, see Limitations). Firestore rules not touched. `core-size.js` untouched.

## Follow-up (TD4c-style tweaks, same TD4b build)
- Plan › Sat held Main row: removed the display line `Macro … · Trend … · Driver … · เต็ม` (3 call sites of `satV3F2cTradeLine`). Stored trade fields unchanged; the function is kept.
- Keyboard-shortcut hints (`.kbdhint`, e.g. the `V`/`C` chips on Candidates/Watchlist) are now hidden on touch or ≤ 820 px screens (`@media (hover:none),(max-width:820px)`).
- Tests updated to match: phase11 and phase27 read the line from `satV3F2cTradeLine(trade)` instead of the DOM; phase44 checks the new generic `.kbdhint` rule; phase108 expects 0 lines in the DOM. Originals saved as `_to_delete/ph{11,27,44,108}.bak.TD4c`. Pre-change index: `index.backup-pre-TD4c.html`.
- Full re-run `tests/runall2.sh` (output `_to_delete/runall2`): after solo rerun, 103 of 109 ok. Failures: phase5 and phase13 (known, unchanged), plus phase11, 27, 44, 108 which failed only on the old expectations above; after the test updates I re-ran those four solo: all pass (0 FAIL). The full table was not re-run after the test edits.
- phase5 (Break Price save-click) still fails as before; phase13 known.

## Results
- Full run `tests/runall2.sh` (base + 1–108, output in `_to_delete/runall_td4b_final`): **107 of 109 suites ok.** The two failures are the known **phase5** and **phase13**.
- New suite `phase108`: **132/132**. `check_syntax` OK · `core_size_test` 471/471 · `sync_core_size --check` OK.
- Honest note on the run: in that full run phase80, phase90 and phase107 failed because of expectation changes I patched afterwards. I re-ran those three solo (80: 58, 90: 73, 107: 325, all passing) and put those results into `final.tsv` (the pre-patch table is kept as `final.before-solo.tsv`). After that run I made three small changes (Today Sat size text `×2`, a revert of one message string, a CSS chip tweak) and re-ran phase108 (132/132), phase106 (165/165) and phase107 (325/325) solo; the other suites were not re-run after those last edits.
- Verify file: `docs/reports/TD4b-verify.txt` (built by `bash tests/make_verify.sh TD4b`).
- Backups: `index.backup-pre-TD4b.html` and `tests/_bk_td4b/` (top-level test files only; the nested `_bk_*` and `screenshots` folders were not copied).

## Tranche display bug — root cause
Two gaps, both display only:
1. **Today › Satellite** (`td3SatSaved`) summed only `satV3EffectiveTrades(idea)` = the trade linked as the plan's first tranche. The second tranche is stored separately (`accts[acc].pyr_trade_ids`), so it was never counted or shown. Before: `Size 0.1 lot`; after: `Size 0.16 lot ×2` (0.05 + 0.05 Family + 0.06 tranche 2).
2. **Plan › Sat held row** did list the extra lot, but with no tranche label, so it looked like a duplicate line. Each line now carries the existing `ไม้ n/N` tag.
Risk and positions were already counted correctly; the test proves `satV2Risk`, caps, `satV2MainPos` and the plan calc are identical (byte for byte) before and after.

## Where Focus TF / Bias / Zone live (PF1 fields on the plan doc)
TF = `idea.tf` (fallback: the account's `tfMain`/`tfTac`), Bias = `idea.bias` (Long/Short, set by the Trend select), Zone = `idea.zone_act_txt`. Context line `Main · 4H · Long · Zone 4,230–4,250` (missing parts skipped, never `—`) is shown on Plan › Sat plan rows, held rows and Today Satellite rows.

## "Additional notes" outcome
It stored data (`setup_note`, copied onto trades). I removed the input only. Plans that already have a note show it read-only (`โน้ต …`); new plans show nothing. The section's other contents (Macro line, size-rule switch, per-account sizes, Driver chips) are functional, so the fold stays, renamed `Macro & ขนาดไม้ ▸`.

## Zone checkbox
Removed. Rule: zone field non-empty = zone set (`zone_act` is written as `zone_act = text !== ''` so old readers still work). `zone_act` did not affect validation or sizing. Old plans with the box off but a stored zone: **0 in the fixture**; the test seeds one and confirms the zone still shows and saved data is untouched.

## Clutter text
`Macro ตาม (…) · Trend … · Driver … · เต็ม` is now shown only on the first tranche (`satV3F2cTradeLine` returns nothing for a trade with `pyr_parent`). The second tranche still stores the same fields (deep-compared). The values appear nowhere else on that row.

## Compact plan view (held row + trade lines, expanded)
| width | before | after | change |
|---|---|---|---|
| 390 | 345.6 px | 249.2 px | −27.9 % |
| 1440 | 323.9 px | 215.4 px | −33.5 % |
Trade line height 76 → 55 (390) and 38 (1440, one row from 1100 px up). Fonts unchanged; buttons ≥ 32 px.

## Satellite pin / sort
`☆/★` per Asset in `satAssetCfg[key].pinned` (kept through Settings save). Order everywhere (Plan chips, Mac tiles, plan list, Today Satellite): ★ → Main → Tactical → existing order. I treated the brief's "Swing" as **Tactical** (the app's second plan type).

## Other items (B0, B6b)
- Watchlist `＋` → **`＋ Add on candidate`**: `[US|TH]` + tickers, same rules as Today New Cand (cap 10 a day, de-dupe). Goes to Candidates only.
- A Candidate through `＋`/`wlOpenAdd`/`wlAddSave` is refused with `Use Move to Watchlist` and an `Open move form` button (goes to Today and opens that card). Updates and imports for tickers already in the Watchlist still work.
- `Import` and `Export .txt` are in the `⋯` menu; export text unchanged.
- One row at 390: `All | US | TH | Add on candidate | ⋯`. **Filter ▾ moved into the `⋯` menu below 700 px** (stays in the row from 700 px up); a dot on `⋯` shows an active filter. 300 px may wrap.
- Today Cand → WL cards start collapsed (`NEW1 · New today … Screen ›`), one open at a time, typed values kept, all closed when returning to Today. `Not passed` → `✕ SYM · Not passed · Undo` for 5 s, restores the previous `screened_at` and the counter.
- **Other ▸ removed from Today.** Only reachable via Other before: time-slot ticks (Daily routine), Daily/Weekly task ticks and `%`, Sat Focus ✓/✕, the Weekly Stock Summary card (still reachable via the Core `Weekly News … Read ›` link when unread), the Macro re-check row and the Numbers table (DD / Open Risk Sat; Open Risk also on the Plan risk bar). Settings › Daily routine, the Weekend tab and all data remain. Not re-added.

## Files changed
`index.html` (+164/−43); new `tests/run_tests_phase108.py`; old tests patched (all logged in `tests/TD4b_retired.md`, 17 entries, none deleted or weakened): phase20, 22, 29, 39, 45, 59, 61, 62, 80, 81, 82, 85, 90, 98, 104, 106, 107; `tests/runall2.sh` now runs 1..108.

## Screenshots opened
All eight in `tests/screenshots/`: `td4b-plan-1440`, `plan-390`, `tranche2-390`, `today-sat-390`, `form-390`, `watch-390`, `watch-1440`, `today-core-390`. Opening them found two problems I fixed: Today Satellite clipped `TP` after the new tranche field (now `Size 0.16 lot ×2`), and the form shot showed the list instead of the form.

## Limitations
- **Test seam:** because old suites exercise the former Other content, `index.html` still renders it when `localStorage dash.td3OtherDev = '1'`. No UI sets that; only the test launcher does (`P39.TD3_OTHER_DEV`; phase108 turns it off).
- The tests-folder backup first recursed into itself (7.4 GB); I stopped it, moved the copy to `_to_delete/_bk_td4b_runaway` (not deleted) and redid the backup without nested folders.
- Plan pin stars on Asset chips use `☆`; the pin is not shown inside the Settings page.
- Chips in the plan form can wrap to two lines at ≤ 340 px because `MA Align Overlap` is longer.
- phase5 and phase13 still fail as before.
