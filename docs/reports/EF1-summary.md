# EF1 — Entry friction: summary

Branch `claude/ef1` from origin/main `00a36ae` (RM1 + PV1b). Commits: A0 map → A → B → C → D.

## Tap counts, before → after (Plan tab open, clean plan; after = measured by `run_tests_ef1.py`)
| Plan type | Before (Plan board) | After | Before (Today › Enter) | After |
|---|---|---|---|---|
| Satellite main plan | 2 | **2** (Place › → Confirm) | 4 (⚑ + Place › + Yes + open Today) | **2** |
| Satellite carried plan | 3 (Use this week ›) | **2** | 5 | **2** |
| Satellite, asset not picked | 3 (Add to week ›); full picks = dead end | **2** (full: replace line in the sheet, still 2) | 5 | **2** |
| Satellite, against Macro | 5 (note) | **2** (amber chip) | 7 | **2** |
| Satellite, verify unanswered | 5–7 | form answers it once, then **2** | 7–9 | **2** |
| Satellite, CPI/NFP window | blocked | **2** at 65 % size | blocked | **2** |
| Momentum plan | 2 (native confirm) | **2** (sheet) | 4 | **2** |
| Compounder pilot | 2 (native confirm) | **2** (sheet) | 4 | **2** |
Opening the Plan tab is +1 as before; total with it ≤ 3.

## Removed / softened gates and what replaced them
| Gate | Now |
|---|---|
| `carryBlock` | no longer in `ready`/warns; Place re-dates the plan to this week (`carried_from` kept); grey "Carried from …" row in More |
| `unpickBlock` | Save / Place auto-adds the asset to `satWeekPickList`; list full (3) → one line "Replace <asset> in this week's picks?" (+ "Other ›") in the confirm sheet |
| `noteBlock` | already warning-only since LN4; card gets amber "Against Macro" chip (and in the sheet); reason field optional |
| manual ⚑ Ready | removed (card, drawer, Today); `re2ReadyOf` = complete + no block + sized; stored `ready` / `readyAt` ignored, not deleted |
| verify "pending" step | `td3PlanStatus` now returns `incomplete` with "Needs EMA50 + Structure" / "Needs MSS (Structure = No)" (also `pb2Model`, drawer, Today). EMA50 + Structure + MSS already live in the plan form |
| news window block | warning + size cut: `newsSizePct` (Settings › Key news days, default 65) applied in `Re1Adapter.sizeSat` as **min(condition, news)**; amber "News window until HH:MM ICT · size 65%" on the card and in the sheet; Satellite only; full size returns when the window ends |
| native `confirm()` for Momentum / Compounder | same confirm sheet (legs, stop, Risk, Reward, "limited by …", More › size working), one Confirm |
Sheet button "Yes · mark ordered" → "Confirm".

## Gates kept (all verified in `run_tests_ef1.py`)
stop missing · stop below min · wrong-side stop · emergency brake 0 % · engine size gate (`re1PlanGate` / `wl1PlaceGate` incl. homework cap) · MSS = No / blank · queue ("Another Satellite setup is active") · R:R. Heat / total risk / value cap / re-entry are in untouched `risk-engine.js` (313 + 63 + 43 node assertions pass).

## Tests changed and why
- `run_tests_pv1b` — unpick / carry / news "block" checks rewritten to "not a block" (+ news amber line).
- `run_tests_pv1` — blocked card no longer says "Not picked this week" (shows min-stop reason).
- `run_tests_re1c2` — manual ⚑ toggle removed; Enter lists every Ready plan; chip "Ready" with signed distance.
- `run_tests_re1d` — after Keep a (now automatically Ready) plan stays in Enter without the "passed entry" prompt.
- `run_tests_phase373` / `phase374` — Place › now opens the sheet (extra Confirm click); label "Needs MSS (Structure = No)"; "Confirm" button text.
- Regression: pre-existing failures identical on base (`phase122/365/366/367/cg1/ht1`, `phase373` 390 crash). Everything else passes after the updates above (`run_tests_ef1` 129 pass).

## Row counts at 390 (same fixture: 1 Satellite + 1 Momentum plan)
Plan board: 2 cards, same height before / after. Today: 0 Enter rows before → 2 after (page 844 → 896 px): Ready is now automatic, so plans show in Enter without the ⚑ tap. Not shorter — inherent to §4.

## Open questions
1. Today › Enter now lists every Ready plan (no ⚑ filter). With many plans it grows; cap at 3 + "more" or require ≤ 3 % to entry for core?
2. Legacy (non-v2) Satellite plans keep the news block: they have no engine size, so no cut is possible.
3. Counter-trend save still asks one extra "Save as counter trend" confirm (PB1b rule, untouched) — drop it?
4. `bdPlaceLv` (placing a later entry level) still records directly, without the sheet.
