# MV1 — Move between Momentum ↔ Compounder (⋯ menu) · Screen desktop without company column · one dark button check

Branch from fresh origin/main (`cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-mv1 -b claude/mv1 origin/main`). First commit = this brief + `mv1-mockup.html`. Read `claude/uiux-concept.md` (11 rules; rule 11 = iPhone 390 every time). Keep A / B / C in separate commits.

## A · Move to Compounder / Move to Momentum (stock ⋯ menu)
- Add one item to the existing stock ⋯ menu in Watch › Momentum: **Move to Compounder**, second line (small, grey) `Keeps notes, homework and alerts`. In Watch › Compounder the same item reads **Move to Momentum**.
- Order in the menu: Edit note → Move to … → divider → Remove · kept in Archived. No new button anywhere else.
- Allowed only for status **Watching / Focus** (No plan). For **Holding / Planned**: item shown grey, not clickable, second line `Has a plan · change it in Plan ›` (the "Plan ›" part links to that stock's plan).
- Action: one tap, no confirm. The stock moves list with everything it owns (notes, homework/thesis, Fact Sheet, TV alerts, Focus ☆, scenarios/ideas links). Toast `Moved HOOD to Compounder · Undo` (6 s); Undo puts it back exactly (same list, same Focus state).
- After the move: stay on the current list; select the next row (same as Remove today).
- iPhone: ⋯ opens the bottom sheet (rows ≥ 44 px), same items and grey state.
- Data: one field change per stock (whatever marks the list today) + `movedAt`. No copy, no duplicate doc. If the ticker already exists in the target list → item grey, second line `Already in Compounder`.
- Tests: move both ways; Holding/Planned blocked; duplicate blocked; Undo restores; Focus and notes survive the move.

## B · Watch › Screen, desktop only: remove the Company column
- Desktop table (≥ 1100 px): drop the **Company** column. Columns: Ticker · Industry · RS · From high · (rest as today). The space goes to Industry, which now shows in full (no "…").
- Hover a row (or keyboard focus) → small dark tooltip with a **short name**: strip suffixes like `Class A`, `Common Stock`, `Common Shares`, `Ordinary Shares`, `American Depositary Shares`, `Inc.`-trailing junk after the comma ("Robinhood Markets, Inc. Class A…" → "Robinhood Markets"). Use the same short-name function in the stock panel header if it shows the long name today.
- Search still matches company names (unchanged).
- **iPhone / < 1100 px: no change** (name + industry stays exactly as today; SRTp's call).
- Tests: column count at 1440; tooltip text for 5 sample names (APP, CLS, HOOD, an ADR, a "Common Shares" name); 390 layout unchanged (snapshot compare).

## C · One dark button per screen (check, then fix)
- Rule: one dark (`.pri`) button per area. On stock screens that is **Make plan ›**. Homework ›, Set TV alert, Clean up, Import stay white.
- Grep every `pri` use; list in the report any screen/area that shows 2+ dark buttons at the same time (desktop and 390) and fix them. If a fix changes a layout, stop and report instead of guessing.

## Screenshots (only `mv1-*.png` in the diff)
- `mv1-move-menu` (1440 + 390), `mv1-move-blocked` (Holding, 390), `mv1-move-toast` (1440)
- `mv1-screen` (1440 with tooltip on one row) + `mv1-screen-390` (proves unchanged)
- One shot per screen changed in C (1440 + 390)

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks after the last change · revert tracked screenshot rewrites · new suite `tests/run_tests_mv1.py` in REST= · no push until I review — report tests, judgment calls, PNG list.
