# SD1 — wrong-side guard (Satellite plans)

## What changed (index.html only; no engine maths change)
- **Helper `sdWrongOf(idea)`** — returns `{to, why, btn}` when SL/TP point the other way ("Wrong side: SL above entry for Long", "Switch to Short ›"). `sdFlip(id)` writes `bias` (+ `wrongSide:false`) and re-renders; nothing changes without the tap.
- **Sat plan form** — red line under the levels: "These levels look like a Short · Switch to Short ›" (button keeps the numbers). **Save plan is disabled** until consistent; **Save draft is allowed** and stores `wrongSide:true`.
- **Auto side** — once Entry and SL are both filled, side follows them (SL < entry → Buy/Long, SL > entry → Sell/Short) with a small `auto` tag. A manual pick (toggle, Switch button, or editing an existing plan) wins; a contradiction shows the line and blocks Save plan.
- **Enter (EN1)** — Save plan keeps `data-enter-primary`; in the popup Enter saves only when Save plan is enabled, otherwise it focuses SL (wrong side) or the first empty field. Never submits past a disabled Save.
- **Blocked rows** — Today Act row (`Blocked · Wrong side: … ` + Switch button), Plan board card, drawer (enabled switch button), Place order sheet (banner + Confirm disabled). Stored wrong-side plans show Blocked on load.
- **Drafts** — a plan with `wrongSide:true` and still-wrong levels never appears on Today and `pb2PlaceOpen` refuses it; it stays on the board with the Blocked line.
- **`re1SatBlocks`** — `SAT_BAD_ORDER` removed from the skip list, so the engine reason is never hidden.

## Tests
- New `tests/run_tests_sd1.py` (69 checks, in `run_regression.sh`): Long/Short wrong-side rows on Today / board / drawer / Place sheet, switch → Place works, form line + Save plan off + draft allowed, auto-set, manual override, draft saved with `wrongSide:true` and kept off Today/Place, Enter on blocked and consistent forms, stored plans untouched, Core form still blocks Entry ≤ SL.
- `run_tests_phase373` PB1b side-check strings updated to the new line.
- Hooks superset: PASS.
