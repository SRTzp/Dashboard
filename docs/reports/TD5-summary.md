# TD5 — My own to-dos in Today › To do (final, with the delta)

## What it does
- **"+" in the To do header** (28px, left of the Exec pill) opens an input as the first row under the header, with the hint `Enter save · Esc close · n/120`. It closes after save or Esc. No keyboard shortcut (N still opens New plan). At 30 open items "+" is disabled with the tooltip `30 open — finish one first`.
- **Own rows reuse the existing row anatomy:** the 46px tag slot holds the round tick, no MINE tag, × is 28px (44px on phone), one line with ellipsis and the full text in a `title`. Clicking the text opens a 2-line textarea (Enter saves, Esc cancels, empty = no change), then back to one line.
- **Done / delete:** the row shows ✓ + strikethrough, then leaves. A 6 s toast `Done|Deleted: <text> · Undo` appears; Undo restores the item in its old place.
- **Order and cap:** red engine items, then my to-dos (oldest first), then the rest. Own rows share the existing cap (4 Mac / 3 phone) and the existing `+N more` fold. They count in the header number.
- **Card height** is unchanged when not adding (measured with and without the "+"). With nothing to do, the card shows only the header (`To do 0 +`), with no extra text.
- Typing guard: global shortcuts (digits, `n`, `/`, `.`) do not fire inside the add input or the inline edit.

## Data
`settings.myTodos = [{id, t, at, done:false}]` in the home account's settings in the existing user doc (the same path as `glWrite`). Same list for Main and Family. No new collection, so no Firestore rule change. The settings doc holds it: 30 items ≈ 5 KB at most. Done/deleted items leave the array and Undo writes them back. `render()` stays pure; every change goes through `glWrite`. After a refresh, focus and caret in the add input or edit field are restored.

## Code
`index.html`: TD5 block (`td5*` functions + CSS) next to `ln4TodoHtml`; `ln4TodoHtml` merges own rows into the ordered list; `todayRefresh` restores focus. The card is no longer hidden when empty. Hooks: none removed.

## Proof
- `python3 tests/run_tests_td5.py` — 127 checks at 1440 / 390 / 360, 0 failing. It covers: "+" placement · hint and counter · Esc · **N still opens New plan** · empty/space Enter · trim · 120 limit · tick-slot anatomy, no MINE · one-line ellipsis · order · cap and `+N` fold · textarea edit (Enter/Esc/empty) · tick + Undo · × + Undo · 6 s toast · 30 cap and tooltip · card height with/without "+" and while adding · single saved doc, no new collection · persistence after reload · typing guard · empty header-only card · no overflow · phone targets ≥ 44px.
- Side PNGs vs mockup states 1/2/3: `tests/screenshots/td5/td5-side-1440.png`, `td5-side-390.png` (made by `tests/td5_side.py`).
- `python3 tests/hooks_test.py` — hooks superset PASS.
- `JOBS=2 bash tests/run_regression.sh` — see REGRESSION below.
- `run_tests_td5` is added to the regression list.

## Notes
- The mockup panel 3 shows the textarea at 2 rows; a 120-char item can need a third line while editing (it scrolls inside the textarea), as in the mockup.
- The fixture replaces `ln4TodoItems` (display layer only) to get red/amber/grey rows.

REGRESSION: 75/75 ok · 0 failing · 2107s (JOBS=2 bash tests/run_regression.sh, clean run on branch rebased on origin/main 2f9ffb3). run_tests_td5 127/127, hooks_test superset PASS.
