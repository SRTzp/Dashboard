# AW1 — account switch in the top bar · Cancel plan as ✕

Approved by SRTp 16 Nov 2026. (Called "AC1" in the 16 Nov hand-off; renamed AW1 because AC1 / AC2 are older, finished jobs.) Mockup: `docs/briefs/ac1-switch.html` (open it first; iPhone = option **B**).
Base: latest `origin/main` (must contain RE-D, `re4CancelBtn` exists). Branch: `claude/aw1`.

## Goal
Switching Main ↔ Family takes one tap / one key from any tab, and the user sees when the other account needs attention. No change to risk rules, sizing or data.

## Rules for this job
- UI text in English as in the mockup. No formulas or field names on screen.
- No overflow at 1440, 1280 and 390. Tap targets ≥ 44 px on iPhone.
- Reuse what exists: `acctSwitch(id)`, `acctActive`, `acctList`, `acctColor(a)`, the engine To-do list (`re1snap:` items), `re1SnapConfirm(acct)`, `coreSheet(...)`, `re4Open(...)`. No new stored data except the remembered account (keep the existing persistence if `acctSwitch` already remembers it).
- `render()` stays pure; no persist calls from render paths.
- No deletes of user data. Do not touch `risk-engine.js` rules.

## 1 · Account switch (all tabs)
- New segmented pill `#acSw` in `<header class="topbar">`, directly right of the tab pill; tabs + switch are centred together as one group. One button per account in `acctList` order, label = account name (`Main`, `Family`), leading dot = `acctColor(a)` (faded when inactive). Active = light grey fill, dark text. Must look different from the black active tab.
- Hidden when `acctList.length < 2`.
- Click → `acctSwitch(id)`; stays on the same tab; scroll position reset is fine.
- Remove the `#mmAcct` section (`#acctSel` select) from the ⋯ menu. Keep any other code that reads the active account working (search every `acctSel` use; Settings `ln3SetAcctSeg` keeps working and stays in sync).
- **iPhone (≤ 600 px):** the pill sits in the top bar between the logo and the buttons, labels shortened to the first letter (`M`, `F`; if two names share a letter use the first two letters). Hide the word "Trading" and the sync text; keep the logo and a sync dot (same colour states as now); tapping the dot opens the ⋯ menu where the full sync line already is. All four header buttons stay.
- `aria-pressed` on the buttons, `title` = full name + "[ previous · ] next".

## 2 · Shortcuts
- `[` = previous account, `]` = next (wraps). Ignored when focus is in input / textarea / select / contenteditable, when a modifier key is held, or when a sheet / modal is open. Add to the existing global keydown handler, do not add a competing one.

## 3 · Badge on the inactive account
- Amber count on each **inactive** account button = number of things waiting there:
  Today Act rows for that account (Enter + Check orders + Manage) + 1 if its snapshot is due / stale + 1 if its execution review is due.
- Compute from the same functions Today uses, called with the other account id; no second copy of the logic. If those functions only work for `acctActive`, add an account parameter rather than switching state temporarily.
- No badge at 0. Show `9+` above 9. Update on every render and after `acctSwitch`.
- Must be cheap: compute once per render, not per tab.

## 4 · Snapshot sheet (both accounts)
- To do "Snapshot due · <name>" and the Today "Snapshot due" chip open one sheet `Equity snapshot` (via `coreSheet`) instead of `openSettings()`.
- One row per account: name · "last <date>" · editable equity value (same input and validation as the Settings card) · `Confirm` (shows `✓ Confirmed` after).
- Footer: `Later` (close) · `Confirm both` (primary; confirms every row not yet confirmed this week; label `Confirm` when only one is due). Uses `re1SnapConfirm` per account — same FX freeze and rules as Settings.
- The Settings card stays as is.

## 5 · Cancel plan → ✕
- `re4CancelBtn(it, true)` (Planned card header, Plan board): render a round ✕ button (28 px circle, 1 px line border, muted colour, hover = dark), `aria-label` and `title` = "Cancel plan". Keep `data-re4-cancel data-re4-card` and the same `re4Open` call. iPhone: 44 px hit area without growing the card.
- `re4CancelBtn(it, false)` (drawer foot) keeps the words `Cancel plan ›`.
- The Today "passed entry" row button keeps its text.

## 6 · Risk room chip
- The Risk room summary chip shows only the risk state (`Normal` / `Half size` / `Locked` / snapshot states). Remove `set('Review due', …)` from that chip. The execution-review signal stays where it already is (red `3 not taken`, To do, form block) — check it is still visible on Today after the change.

## Tests
- New `tests/aw1_test.js` (same runner style as `re1c_live_test.js`): switch by click and by `[` `]`; shortcut ignored while typing; badge count = Act rows + snapshot due of the other account and 0 → hidden; pill hidden with one account; ⋯ menu has no account select; snapshot sheet confirms both; ✕ opens the cancel sheet and Keep changes nothing; drawer still shows the words; Risk room chip never says "Review due".
- Still green: `node tests/risk_engine_test.js`, `re1_adapter_test.js`, `re1c_live_test.js`.
- Overflow check (scrollWidth ≤ clientWidth) at 1440 / 1280 / 390 on Today, Plan, Journal, Port.
- Screenshots (`git add -f`): `aw1-today-1440`, `aw1-today-390`, `aw1-plan-1440`, `aw1-plan-390`, `aw1-snapshot-sheet-390`, `aw1-family-active-1440`.

## Report
`docs/reports/AW1-progress.md` (update after each section) and `docs/reports/AW1-summary.md`: what changed, anything that differs from this brief and why, test results, list of every removed line that deletes or hides a feature.
