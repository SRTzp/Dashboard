# AW1 — summary

## What changed
1. **Account switch** `#acSw` in the top bar (tabs + pill centred as one group in `#topMid`), all tabs, hidden with <2 accounts, `aria-pressed`, title "Name · [ previous · ] next". `#mmAcct` / `#acctSel` removed from the ⋯ menu (`renderAcctBar` now draws the pill). iPhone ≤600 px (option B): letters, logo + sync dot (tap → ⋯ menu), pill ≥44 px; ≤380 px header buttons shrink to 36 px so 360 px fits.
2. **Shortcuts** `[` / `]` in the existing global keydown handler (ignored when typing, with modifiers, or with a sheet/modal open).
3. **Badge** on the inactive account = `re2Model(acct)` Act rows + snapshot due + `re4Due` — same functions Today uses, no state switch; computed once per `render()`; hidden at 0, `9+` above 9.
4. **Equity snapshot sheet** (`aw1SnapOpen`) from To do "Snapshot due · name" and the Today Act state chip (also No snapshot / Snapshot stale); rows, editable equity, Confirm, Later / Confirm both; uses `re1SnapConfirm(acct, 'aw1Sn')` (new optional id prefix; Settings card unchanged).
5. **Cancel plan ✕** on the Planned card (28 px circle, 44 px hit area on iPhone); drawer keeps "Cancel plan ›"; Today passed-entry button unchanged.
6. **Risk room chip / Act state** no longer set "Review due"; red "N not taken" chip, To do item and form block remain (tested).

## Differences from the brief
- **(superseded by Small fix) `[ ]` conflict:** `[` `]` already cycled per-tab filters (Plan chips, Watch, Journal, Port…). Account switching now owns plain `[ ]` when ≥2 accounts; the old cycle moved to `Shift+[` / `Shift+]` (single-account behaviour unchanged). Help overlay updated.
- `tests/aw1_test.js` is a thin node wrapper around `tests/run_tests_aw1.py` (Playwright) because the checks need a browser.
- Snapshot sheet has no date field (uses today, as the Settings card's default).
- `tests/run_tests_re1d.py`: one assertion ("strip state is red") replaced by "no 'Review due'" per §6.
- Account names come from data (fixture shows "บัญชีหลัก" / Family).

## Tests
`risk_engine_test` 313/313 · `re1_adapter_test` 63/63 · `re1c_live_test` 82/82 · `aw1_test` 104/104 (390/1280/1440, incl. no overflow on Today/Plan/Journal/Port) · `run_tests_re1d.py` 336/336 (incl. 360 px).

## Removed / hidden features
- ⋯ menu account section (`#mmAcct`, `#acctSel`) — replaced by the top-bar pill; its ports hint line (`#acctPortsHint`) is no longer shown.
- "Review due" state in the Risk room chip / Act state.
- Plain `[ ]` per-tab filter cycling when ≥2 accounts (now Shift+`[ ]`).
- Word "Trading" and sync text hidden on iPhone ≤600 px (dot stays).
- "Cancel plan ›" words on the Planned card (now ✕; drawer keeps words).

## Small fix — account shortcut keys
- Account switch is now `.` = previous, `/` = next (`e.code` Period / Slash, so Thai layout works; no Shift/Ctrl/Alt/Meta, so Shift+/ still opens the help overlay). Same ignore rules (typing, sheet/modal open, fewer than 2 accounts).
- Plain `[` `]` are back on the per-tab filter cycle exactly as before AW1; the "Shift+[ ]" wording is gone.
- Pill title now "Name · . previous · / next"; help overlay rows updated (`. /` account, `[ ]` tab filter). `docs/GUIDE-daily-use.md` did not mention the keys.
- Tests: `run_tests_aw1.py` now 113/113 (`.` `/` switch, `[ ]` cycle filters with 2 accounts, Shift+/ opens help, keys ignored while typing/modifier/sheet). `risk_engine` 313, `re1_adapter` 63, `re1c_live` 82, `run_tests_re1d` 336 — all pass.
- The "removed features" entry about plain `[ ]` cycling no longer applies.
