# LR4 · Flow tab (match the mockups)

Branch `claude/lr4` from main. Can start before LR-F2 merges (separate worktree); rebase onto main before the final regression.

## Rule (same as LR-F)
The mockups are the spec: `docs/briefs/lr/Flow.dc.html` (1440) and `FlowPhone.dc.html` (390). Match layout, spacing, type, colours, wording. Mockup data is sample data; use live data.
Hooks: never rename or remove an `id`, `data-*`, `name` or inline handler. Restyle, move or wrap only. `hooks_test` superset PASS.
No change to engine files, to the RRG model numbers (`rrgCompute` results, `RRG_MODEL`), to regime (RM1) or to any data job. Light only. English UI (Flow still has Thai text: translate it).
Flow data is shared: same view in Main and Family. Show "Same in Main and Family" in the header (desktop), as in the mockup.

## Desktop (top → bottom)
1. **Header:** "Flow" + week range ("Week 17–21 Nov") on the left, `Import JSON` on the right (the existing Weekly Impact / playbook import).
2. **Glance row (3 cards):** Market mood (regime state + "New entries at x% size", from the RM1 result) · Why (Equity / Credit red/green + days in state, data date) · Next news (next 3 HIGH/MED events, Thai time, assets, `Full week ›` scrolls to the calendar).
3. **Which asset moves this week:** one tile per Weekly Impact asset (XAU, BTC, S50, Brent, GO… whatever the JSON has), max 4 on a row, ordered by impact, then `+n`. Tile: asset · direction (▲ Bull / ▼ Bear / — Range) · impact chip · one-line reason. Tap → the existing Weekly Impact detail for that asset. No Weekly Impact → "No Weekly Impact · Add ›".
4. **Sectors vs SPY · RRG:** a scatter chart on the left, a speed list on the right. Daily/Weekly toggle (existing `rrgTf`).
   - Chart: 4 tinted quadrants with labels, each sector = a 5-bar tail (dots) + an arrowhead at today + ticker label. Axis note: "weaker than SPY · RS-Ratio · stronger than SPY" and "Tail = last 5 days · arrow = today" (Weekly → "last 5 weeks").
   - Tail points: compute ratio/mom for the last 5 bars with the SAME formula as `rrgCompute` (the `zAt` path). Today's point must equal the current ratio/mom exactly (add a test). Cached rows without a tail draw the dot only, until the next refresh.
   - Speed list: Leading / Improving / Lagging groups, each row = ticker · name · chip (`speeding up`, `11d`, `1d · new`, `slowing 12d`) from the existing quad/days/dMom fields. Weakening collapsed: "Weakening (n) · Lagging +n".
   - The existing per-sector rows (Fresh, Flat, Details, How to read) stay reachable from a `All 23 sectors ›` link (opens the current list).
5. **Calendar card with two tabs:** `Economic calendar` (default) · `Macro quarter` (+ "Q4 missing" chip when there is no playbook).
   - Economic calendar = our own week grid (Mon–Fri columns, events as chips with time · name · HIGH/MED/LOW), built from Weekly Impact events + the key-news data Today already uses. Header right: "US · HIGH + MED · Thai time" + `Investing.com ↗` (opens the existing widget/link; the iframe is no longer the default view).
   - Macro quarter = the existing playbook panel (`#pbPanel`), unchanged inside.
6. **Details ▾** (one collapsed block at the bottom): Regime details (ACWI/BIL · HYG/IEI · QE mode), Weekly Impact · all assets, the manual fund-flow boards, log. All content kept, text in English. No more numbered section headers (1–6) or emoji summaries.

## Phone (390)
Mockup order: header "Flow 17–21 Nov" · mood band (mood + entries %, Equity/Credit dots, one "Next:" line with 2 events) · asset tiles 2 per row · RRG card (compact chart, D/W toggle, leaders/improving/laggards as 2 lines of arrows, `All 23 sectors ›`) · row `Economic calendar · n this week ›` (opens the calendar as a sheet) · row `Macro quarter ›` · `Details ▾`.
One line per item, no wrap in tiles (ellipsis). Flow 390 must be shorter than today's Flow 390 (measure before/after).

## Proof (required)
- `tests/screenshots/lr4/flow-1440-side.png`, `flow-390-side.png` (mockup | live, same width, a fixture with Weekly Impact + RRG + events), plus `flow-390-calendar-live.png` and `flow-1440-macro-live.png`.
- `tests/run_tests_lr4.py` in `run_regression.sh`: tail end-point = current ratio/mom; Daily/Weekly toggle; empty states (no Weekly Impact, no RRG, no events); no Thai characters in `#tabFlow`; no overflow at 360/390/1440.
- `docs/reports/LR4-summary.md`: remaining differences per screen with a reason each, heights before/after, full `run_regression.sh` 0 failing.
- Commit in parts: A glance + asset tiles · B RRG chart + list · C calendar/macro tabs + Details · D phone + report.
