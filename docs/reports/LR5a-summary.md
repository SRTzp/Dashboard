# LR5a — Watch tab (match the mockups) + RS1 display

Branch `claude/lr5a` (from `origin/main`). Parts: A desktop table + panel → B sort/filter + RS → C phone + sheet → D tests, report. Spec: `docs/briefs/lr/Watch.dc.html` + `WatchPhone.dc.html`. Hooks superset PASS (additions only). No engine or data-job changes. Light only. English only in Watch, its sheets and the detail panel.

## What changed
- Header: Watch · `Momentum n · Compounder n · Ideas n` · `n stocks · n need homework · shared by Main and Family` · Sort ▾ / Filter ▾ · Find ticker · + Add stock.
- Table: one line per stock — Stock · Status chip (Holding / Add-on planned / Plan ready / Setup ✓ / No plan, from `wl1Status` + the Setup tag) · Sector vs SPY (name + RRG arrow) · RS · Thesis · homework · Next check · one action (`Homework ›` / `Open plan ›` / `Make plan ›`, black when it is the next step).
- Sort (Default · RS high first · Next check soonest · Homework first) and Filter (All · Holding · Plan ready · No plan · Needs homework, with counts); both remembered per device (`dash.wl5Sort` / `dash.wl5Filter`). Null RS / no date sort last. Default order unchanged.
- Detail panel: ticker · status · exchange · sector; WHY / TRIGGER / EXIT WHEN ("Not written yet" amber); Sector vs SPY + RS block (`RS 87 ← 72 (4 wks ago) · line ↗ · new high 18 Nov`, TradingView RS link); one black action; ⋯ holds Full thesis, News & catalysts, Edit, Import, Export, History, Archive…, Delete. Full thesis = the old tabbed panel with a ‹ Summary button.
- Archived (n): collapsed `<details>` with the hint "A stock you stopped watching, kept with its notes", rows ticker · date · reason · Restore.
- Phone (390): 2-line rows (RS at the end of line 2), Sort / Filter icon buttons, detail as a bottom sheet (same content).
- Ideas tab: same header and table style, RS shows "—", `+ Idea` / Import in the header.
- RS display only (`prices/{ySym}.rs`): `87 ↗` + `new high` chip; missing → `—` with the reason as tooltip (`history<252`, no doc). Price docs without `close` verified (stored, no error, no 0 price). The old manual RS stars field is not drawn anywhere in Watch (field kept in the data, hidden).
- English: ~550 Thai UI strings in Watch, thesis panel, import/history/note sheets, Add-stock modal, Ideas and Trade ideas translated (data text from AI/users untouched).

## Heights (`#tabWatch`, same fixture)
| | before (origin/main) | after |
|---|---|---|
| 390 | 590 px | 521 px |
| 1440 | 752 px (fixed viewport box) | 506 px |

## Remaining differences vs the mockups
| Screen | Difference | Reason |
|---|---|---|
| Both | Fixture has 5 Momentum stocks (mockup 3–4) and shows Setup ✓ / RS rows | proof fixture covers every state |
| 1440 | Sector names are the full RRG names ("Semiconductors") | existing `RRG_SYMS` names; no new short-name table |
| 1440 | `Sort ▾` / `Filter ▾` are native selects styled as buttons | accessible, no custom popover |
| 390 | Mockup footnote "Exchange, sector and RS live in the detail sheet" not drawn | explanatory text for the mock only |
| 390 | Archived is collapsed by default (mock shows it open) | brief: collapsed |
| Both | "Need homework" counts every stock without finished homework (including No plan) | matches the mockup (PLTR counted); old count excluded No plan |
| Both | App header (logo, account switch, + Plan) differs | shared chrome, other briefs |
| Ideas | Idea detail tabs keep their layout, only text translated | "no new features" |

## Tests changed and why
- New `run_tests_lr5a.py` (157 checks at 1440/390/360) in `run_regression.sh`: header, chips, actions, RS text/arrows/new high/missing, sort orders (null last), filter counts, search, remembered choice, detail content, ⋯ menu, full thesis, no Thai in `#tabWatch` (list, panel, menu, every thesis tab, Ideas), one line per row, no overflow, phone sheet, archive, price doc without close.
- `run_tests_ts1b` (Archived is a `<details>`, "Archived (0)" stays with the hint), `run_tests_phase370` (row line selector, 36px pickers), `run_tests_phase374` (chip wording, summary count, one-line table rows, thesis opened through Full thesis), `run_tests_phase35` and `run_tests_phase49` (English UI strings, Thai months).

## Proof
`tests/screenshots/lr5a/`: `watch-1440-side.png`, `watch-390-side.png`, `watch-390-sheet-live.png`, `watch-1440-ideas-live.png` (+ live/mock). Bottom nav hidden in whole-page shots.

## Regression
Rebased onto `origin/main`, full `tests/run_regression.sh`: **60/60 ok · 0 failing** (1138 s). Hooks superset PASS. `rrg_hold_test` added to the run. The phone sheet sits below the app modals (z-index 40) so import/answer dialogs stay clickable.
