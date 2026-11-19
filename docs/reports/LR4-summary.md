# LR4 — Flow tab (Main = Family)

Branch `claude/lr4` (from `origin/main`). Parts: A glance + tiles → B RRG chart/list + calendar/macro tabs → C Details, English → D phone polish, tests, report. Spec: `docs/briefs/lr/Flow.dc.html` + `FlowPhone.dc.html`. Hooks superset PASS (additions only). No engine files, RRG model numbers, regime or data-job changes. Light theme only. English only inside `#tabFlow`.

## What changed
- Desktop: header (Flow · week range · Import JSON · "Same in Main and Family") → 3-card glance (mood / why / next news) → asset tiles (max 4 per row, then +n) → RRG scatter with 5-bar tails, speed list, Daily/Weekly toggle, "All 23 sectors ›" → calendar card with tabs (Economic calendar default · Macro quarter with "Q4 missing" chip) → one collapsed `Details ▾` holding the old rows.
- Phone (390): mood band, 2-per-row tiles, compact RRG with arrow lines, `Economic calendar · n this week ›` row (opens a sheet), `Macro quarter ›`, `Details ▾`.
- `rrgCompute` returns an additive `tail` (last 5 z-points); the last point equals the current ratio/mom exactly (tested). Cached rows without a tail draw a dot only.
- `td3GoCal` opens the calendar sheet on the phone and the calendar tab on desktop.
- Thai → English in the Flow chrome, Weekly Impact panel, playbook buttons/badges, `Calc.pbStanceText`, `WI_MON`/`WI_DOW`.

## Heights (same fixture, `#tabFlow` height)
| | before (origin/main) | after |
|---|---|---|
| 390 | 1688 px | 869 px |
| 1440 | 1250 px | 1127 px |

## Remaining differences vs the mockups
| Screen | Difference | Reason |
|---|---|---|
| Both | ★ focus button kept on tiles, `+ Asset` and the week select kept in the section header | existing hooks / features (`data-bd-focus`, week picker) must not be removed |
| 390 | Import JSON hidden | brief: phone header stays compact; same handler is reachable via the tile empty state / Details |
| Both | Fixture shows Brent where the mockup shows GO | live asset list comes from settings, not the mockup |
| Both | Speed-list order follows `rrgSortRows` | existing sort is the product rule; mockup order is illustrative |
| Both | English applied to the Flow chrome only | Thai elsewhere (other tabs) belongs to other briefs |

## Tests changed and why
Old suites asserted the retired layout; they now assert the same behaviour on the new one:
- `run_tests_phase373.py`: Flow top order is macro → RRG (risk strip became the mood card; events became the next-news card + calendar tab); the old ⑤|⑥ pair, 4-quadrant tiles and More rows are covered by `run_tests_lr4.py`; Import opens through `wiOpenPaste()`.
- `run_tests_phase375.py`: RRG name tooltip targets speed-list rows (desktop) and chart groups (phone); `.lr4-rrg` got the no-select / no-callout CSS.
- `run_tests_pv1.py`: tiles replace the card Details button; tap on the tile opens the same panel.
- New `run_tests_lr4.py` (61 checks at 1440/390/360) in `run_regression.sh`.

## Proof
`tests/screenshots/lr4/`: `flow-1440-side.png`, `flow-390-side.png`, `flow-390-calendar-live.png`, `flow-1440-macro-live.png` (+ live/mock).
