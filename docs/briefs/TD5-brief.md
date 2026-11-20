# TD5 · My own to-dos in Today › To do

Decided by SRTp 20 Nov 2026. Spec: mockup `docs/briefs/lr/TodayMyTodo.html`. Small job; git fetch and branch from fresh origin/main (branch `claude/td5`).
Lean UI: no new panel (lives inside the existing To do card), one line per item, no primary button, tags JetBrains Mono 11 neutral, 44px phone targets, 16px phone input.

## Behaviour
- **Add:** the last row of the To do card is an input `+ Add a to-do…` (always visible). Enter saves (trimmed, 1–120 chars); Esc clears; empty Enter does nothing. Max 30 open items (at 30: placeholder `30 open — finish one first`, input disabled).
- **Item row:** round tick · text (ellipsis) · tag `MINE` · `×` (delete). Click the text → edit in place (Enter saves, Esc cancels, empty = no change).
- **Done:** tick → row shows ✓ + strikethrough, then leaves; toast `Done: <text> · Undo` (6 s, the app's light toast). `×` removes the same way with toast `Deleted: <text> · Undo`. Undo restores it in its old place.
- **Order:** red engine items first, then my to-dos (oldest first), then the rest (current ranking unchanged). They count in the header number. They never fold behind the `+N more` button (they are always shown).
- Keyboard: none added (typing guard: the global shortcuts must not fire while the input or an inline edit has focus).

## Data
- Stored with the user's existing app settings doc (no new collection, so no Firestore rule change): `myTodos: [{id, t, at, done?:false}]`. Done/deleted items are removed from the array (Undo writes them back). Save on each change; `render()` stays pure.
- Per user, same list for Main and Family (not per account).
- If the settings doc can't hold it (size or rules), stop and report instead of creating a new collection.

## Proof
- `tests/run_tests_td5.py`: add (Enter, trim, 120 limit, empty ignored, 30 cap) · edit in place · tick → done + Undo · × → delete + Undo · order (after red, before amber/grey) · never folded · persists after reload · global shortcuts don't fire while typing · 360/390/1440 no overflow.
- Side-by-side vs the mockup (`tests/screenshots/td5/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/TD5-summary.md`. No unrelated PNGs.
