# HW1b · Backspace / Esc to go back from the Homework page

Decided by SRTp 20 Nov 2026. Tiny job; git fetch and branch from fresh origin/main (`claude/hw1b`). No mockup (keyboard only).

- On the Homework page (`hw1On()`), **Backspace** (Mac "delete") or **Esc** = `‹ Watch` (`hwBack()`): same unsaved-draft guard, back to the list with the same stock selected and the list scroll restored.
- Same keys on the Full thesis view (`wl5FullSym`) → back to the summary (same as `‹ Summary`).
- Only when focus is **not** in an input, textarea, select or contenteditable (Backspace while typing deletes text as usual; Esc while typing first blurs the field, a second Esc goes back). Not while a menu, popover, sheet or toast-with-focus is open (Esc closes that first).
- Phone: no change (no hardware keys); the on-screen `‹` stays.
- Small hint: the `‹ Watch` button gets `title="Back (Esc or Backspace)"`.

## Proof
- `tests/run_tests_hw1b.py`: Backspace and Esc go back (1440) with the stock still selected; Backspace inside a field deletes text and stays; Esc in a field blurs, second Esc goes back; dirty draft → confirm guard (dismiss = stay); open Fact Sheet popover → Esc closes it first; Full thesis view → back to summary; other tabs unaffected.
- Hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/HW1b-summary.md`. No unrelated PNGs.
