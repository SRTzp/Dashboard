# LR-F · Match the mockups (Today, Plan, order sheet)

Starts after LR3 merges. Branch `claude/lrf` from main.

## Rule
The mockup files are the spec: `docs/briefs/lr/*.dc.html`. Match their layout, spacing, type sizes, colours, buttons and wording. Where this brief or an earlier brief disagrees with a mockup, the mockup wins. The only exceptions are the four "Keep from build" items below.
Hooks: never rename or remove an `id`, `data-*`, `name` or inline handler. Restyle or move elements, or wrap them in new markup. `hooks_test` superset must PASS.
Engine files: no change (risk-engine, re1-adapter, pos-view, core-size, ps1-size).

## Screens
| Mockup | Live screen | Widths |
|---|---|---|
| Main.dc.html | Today | 1440 |
| TodayPhone.dc.html | Today | 390 |
| Plan.dc.html | Plan board | 1440 |
| PlanPhone.dc.html | Plan board | 390 |
| PlacePhone.dc.html | Confirm sheet | 390, and 1440 as a centred dialog in the same style |

Forms have no mockup. Apply the same tokens, buttons and spacing.

## Known gaps (non-exhaustive — find the rest yourself)
1. Plan header: large "Plans" title and summary on one row, port chips on the right of that row. Remove the Thai sync text from the top bar (Plain English; move status to the ⋯ menu or a small dot with an English tooltip).
2. Column titles: plain text, no emoji.
3. Main action buttons are black (`Place ›`, `Confirm`, `Filled ✓`). Green stays for status text only (Ready, Long, profit).
4. Blocked: tinted reason box with a fix button when a fix exists (e.g. `Open Settings ›`, `Add stop ›`). No fix → the one-line reason only.
5. Ordered card: age ("1 day"), full-width `Cancel order` + `Filled ✓` buttons.
6. Holding card: Stop · If stopped · Value · P&L, filled legs marked ✓, `More ▾`. Add a holding fixture so the screenshot shows it.
7. Sizing note on a card when size was cut, e.g. `Sized at 60% · regime both red`.
8. Sheet: drag handle, title + port tag, dark account band, entry k/n on each order row, STOP row shows `Target X · sell #n`, Size tile shows % of full size + the reason (`limited by regime` / `news window` / …), grey Setup row with a large checkbox, `More · size working, FX, limits`, black Confirm.
9. Today: diff against Main/TodayPhone the same way (glance band, Act rows, colours, spacing).

## Keep from build (deliberate deviations)
- Money in the account currency: Main $, Family ฿. The mockup's ฿ on Main is a mockup error.
- Circled × button, 44px touch target on phone.
- Short Blocked wording (`Blocked · MMT weekly limit 4/4`), full text in More.
- Sticky footers on phone (sheet and forms), form footer in one row.

## Proof (required)
- `tests/screenshots/lrf/<screen>-<width>-side.png`: mockup on the left, live screen on the right, same width, same fixture data.
- `docs/reports/LRF-summary.md`: per screen, a list of the remaining differences with a reason each, or "none".
- Full `tests/run_regression.sh`: 0 failing, recorded in the summary.
