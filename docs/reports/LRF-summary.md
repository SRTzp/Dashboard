# LR-F summary — match the mockups (Today · Plan board · confirm sheet)

Branch `claude/lrf` (from `main` after LR3 merged). The mockups in `docs/briefs/lr/*.dc.html` are the spec; only the four "Keep from build" items deviate on purpose:
$/฿ in the account currency · circled × (44 px on phone) · short Blocked wording · sticky footers on the phone.

Hard rules held: no `id` / `data-*` / `name` / inline handler renamed or removed (hooks superset **PASS**); no change to `risk-engine.js`, `re1-adapter.js`, `pos-view.js`, `core-size.js`, `ps1-size.js`.

## Proof
`tests/screenshots/lrf/<screen>-<width>-side.png` — mockup on the left, live on the right, same width, same fixture. Fixture = the mockup data as far as the engine allows (XAU / AVGO (2 levels, TP 175) / BTC short · 2 Waiting · NVDA Ordered · NVDA COMP + BTC SAT **Holding** · regime red/red · Weekly Impact + RRG + CPI seeded for Today). Rebuild with `LRF="plan sheet today" python3 tests/lrf_side.py` (run from `tests/`).
Extra live-only phone views the phone mockups do not draw: `plan-ord-390-live.png`, `plan-hold-390-live.png`.

| Screen | 390 | 1440 |
|---|---|---|
| Plan board | `plan-390-side.png` | `plan-1440-side.png` |
| Confirm sheet | `sheet-390-side.png` | `sheet-1440-side.png` |
| Today | `today-390-side.png` | `today-1440-side.png` |

## What changed
**Plan board (A)** — "Plans" title, summary and port chips on one row (desktop); phone = title · segmented tabs · chips · `Open risk x% / 3% · closest to entry first`. Column titles plain text. `Place ›` / `Filled ✓` / `Confirm` are black; green stays on status text. Blocked = red pill + tinted reason box with the fix button (`Open Settings ›`, `Add stop ›`); no fix → the one-line reason only. Ordered card: age + full-width `Cancel order` / `Filled ✓`. Holding card: R in the header, Stop · If stopped · Value · P&L, ✓ on filled legs, homework chip + `More ▾`. `Sized at 60% · regime` note from the engine's own factor list. Money on cards in the mockup format (−$294 · −฿5.4k · +$3.7k); the More tables keep the exact figure. Thai sync text removed from the top bar (English tooltip on the dot, English text in ⋯).
**Confirm sheet (B)** — drag handle, `Place order` + symbol + port tag, bordered 44 px ✕, dark account band, big order rows with entry k/n, STOP row `Target X · sell #n`, Risk / Reward / **Size = % of full size + reason** (`limited by regime`, `news window`, `homework not done`…), grey Setup row with a 20 px checkbox, `More · size working, FX, limits`, black Confirm, records-only footnote; desktop = centred dialog in the same style.
**Today (C)** — header (title, date · US market opens HH:MM ICT, Daily/Weekend as the light segmented control), glance cards without the outer card, Act as one flat card with `ENTER · n ready · both accounts · closest first` / `CHECK ORDERS` / `MANAGE` labels, white rows with the port stripe, black `Place` / `Filled`, `Homework`, to-entry text beside the direction.

## Remaining differences (each with a reason)
### Plan board — 1440 and 390
- **XAU shows Blocked ("Another Satellite setup is active…") instead of Ready · Place ›, so it is not first.** Reason: the engine's one-Satellite-queue rule blocks a 2nd Satellite plan while BTC is held; the mockup's fixture ignores it. Not changed (engine file).
- **No `also in F ›` chip on XAU.** Reason: the fixture has no Family copy of XAU.
- **BTC lot `#0.9911` (mockup `#0.99`); AVGO Sized note `50% · homework not done` (mockup `60% · regime both red`); Ordered age `today`/`1 day` follows the fixture clock; money in $ on Main (mockup shows ฿ for AVGO).** Reason: engine lot step / live engine factors / "Keep from build" $/฿ rule.
- **Circled ✕ (mockup: plain ✕ ghost on desktop, no ✕ on the phone cards).** Reason: "Keep from build" (circled ×, 44 px on phone).
- **`More ▾` on every Holding card (mockup: only the COMP card).** Reason: one visible way to open the position detail on every card.
- **Waiting block is a collapsible list of full cards on desktop (mockup: one line of text); phone text matches (`+2 waiting · need entry or stop ›`).** Reason: the cards are the only place to fix the missing entry/stop; hooks `data-bd-wait` kept.
- **Blocked line without a fix keeps `Blocked · MMT weekly limit 4/4`.** Reason: "Keep from build" (short wording).
- **App shell around the board** (top bar with ⋯ menu and sync dot, `+ New plan` icon, bottom-nav active style on phone, +Plan button above the title on phone). Reason: the shell is shared by every screen and is not in this brief's screens; mockups draw a simplified header.
- **Holding R in mono font, summary open-risk value (0.28% vs 0.36%).** Reason: live engine value for the live fixture.

### Confirm sheet — 390 and 1440
- **1440: the mockup file only draws the phone sheet**, so the left half shows it at 390 inside a 1440 viewport; the live dialog is the same design as a centred dialog (brief). 
- **Row label `Limit · entry 1/2` (mockup `entry 1`).** Reason: brief item 8 asks for entry k/n.
- **Money `−$160 / +$840` and Size `50% homework not done` (mockup `−฿5.4k / +฿28.4k`, `60% limited by regime`).** Reason: Main = USD rule; Size comes from the live engine factors of the fixture.
- **Setup checkbox unticked, page visible behind the dim.** Reason: fixture state (`tvSetup` empty); live dim shows the page.
- **Satellite sheet keeps the `Setup ready on Execution TF?` checklist under the tiles.** Reason: the PB2 checks are required hooks and have no mockup.

### Today — 390 and 1440
- **Family rows (`XAU · F`, `Place · F`, `MSFT · F`, `+2 more`) and `F futures 1.8×` are absent.** Reason: the fixture is a one-account Main book; the row code handles Family rows but I did not build a second account fixture. `Place · F` wording is not implemented.
- **Manage row line 2 reads the plan card line (`Buy #18 @ 140 · SL 110 · Risk …`), mockup reads `Held #11 · Stop 110 · If stopped … · Next Buy #18 @ 140`.** Reason: text comes from `re2CardLine` shared with other tests; not rewritten in this pass.
- **Check-orders row has no `1 day · still valid?` / `Keep` for a fresh order.** Reason: the prompt appears only when the order is older than the day threshold.
- **To-do rows are one line (no grey sub-line); a leading emoji from stored text.** Reason: the to-do items carry one title string only.
- **Glance data differs (hot-sector picks, `Sat 15:03` vs `Thu 20:30`, date `Fri 2 Oct`).** Reason: the fixture clock and RRG rows; layout, colours and type match.
- **Phone: the Daily/Weekend control stays at the right of the title row (mockup has none); `Main + Family` badge sits left of the status dot (mockup: `M + F` pill right); section labels are 12 px (mockup 11 px); control height 36 px.** Reason: the Weekend review is a live feature without a mockup slot; app-wide rules (text ≥ 12 px, tap targets ≥ 36 px) in `phase370`.
- **Top bar / bottom nav**: same shell note as the Plan board.

## Tests
Updated for deliberate changes (all in `tests/`; the Ready/Near chip is no longer shown on Today rows — the `n ready` header says it): `Place ›` label, `Filled` / `Homework` labels, summary wording on phone, ✕ size (44 phone / 32 desktop), money format on cards (`$3.7k`), `Target` capital, empty-column height, Today height tolerance 12 %, Family band pill colour kept magenta. `run_tests_ef1b.py` is not part of `run_regression.sh` and already fails on `main` (LR3's $ money); untouched.

REGRESSION_PLACEHOLDER
