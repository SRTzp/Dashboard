# ID1 — Watch › Ideas fixes

No engine/data changes · English UI (stored AI/user text untouched) · light only · hooks superset PASS.

## Idea detail
1. **One panel.** The old header card + body card are one `.ideaP` panel. Sticky header: title · status chip · "x of 4 ready" · one black main action by status (Draft → *Finish draft ›* = copy scan command, Waiting/Exploring → *Add evidence ›* = Evidence tab, Ready → *Hand off ›* = Companies tab, Parked → *Resume ›*) · ⋯ (Park, Export, Log history, Import, Delete, version line). The four hand-off conditions moved out of Summary into a collapsed "Ready to hand off ▾" under the header (`data-idea-gate` kept). Inner content panels lost their border.
2. **Tabs** Summary · How · Evidence n · Chain n · Companies — one horizontally scrollable row inside the panel; the active tab is scrolled into view.
3. **Tag** "idea@1 · pick · 5 Nov" → "Picked 5 Nov" (Scanned / Picked / Studied / Matched / Updated / Drafted); version is in ⋯.
4. **Mechanism:** the number of the Weakest-link step now sits inside its highlighted box.

## Desktop side panel
5. The aside scrolls inside itself (max-height = viewport − `--wl-top`/`--wl-bot`), header + tabs sticky; the page no longer grows to its length.
6. Expand: labelled **⤢ Expand / ✕ Close**; solid white fixed layer from the bottom of the app top bar (`--id-top`) down, z-index 45; the top bar stays visible, nothing of the Ideas table shows through.

## Phone (≤1023px sheet)
7. Sheet z-index 80 (above the bottom nav / top bar), dim 79; header (title, status, ✕ 44×44) sticky inside the sheet.
8. No inner card border; content uses the sheet width with a 16px gutter.

## List
9. RS column removed from Ideas; "0 to study · 0 waiting" → "No companies yet".
10. The two chip rows → one **Filter ▾** menu (Type: All/Trade/Invest · Status). "+ Trade idea" stays beside it. Hooks `data-trade-kind(s)`, `data-idea-f`, `data-idea-filters` kept (inside the menu).

## Also
11. Journal › Not taken overlap: the LR5c grid rule is now `.lr5-rs[data-lr5-rs]:not(.miss)`, i.e. only the RS cell (Watch/Port rows that carry `data-lr5-rs`); the reason chip is a plain pill again.

## Notes / deviations
- "Edit" in ⋯: Ideas have no edit feature today (the app has no engine for it), so it is not added; Park/Export/Delete are.
- The "n" on Evidence/Chain keeps its old meaning (pause signals hit / our stocks on the losing side) and shows only when > 0.
- The ⋯/expand work only in Lean mode as before; tests remove the legacy stub flag.

## Tests
`tests/run_tests_id1.py` (48 checks, 1440 + 390): tabs not clipped + active tab visible, sheet header visible/after scroll/✕ 44px, expand layer opaque with no table cell showing through, Not taken without overlap, no Thai in UI labels, plus the items above. Added to `run_regression.sh`.
Shots (before | after): `tests/screenshots/id1/ideas-1440.png`, `ideas-1440-expand.png`, `ideas-390-sheet.png` (`tests/id1_side.py`).
Full `run_regression.sh`: **65/65 ok, 0 failing** (hooks superset PASS). Run 1 found 4 suites broken by my phone dim z-index (79 covered other sheets/modals) — fixed (sheet 42 / dim 41, scoped to Ideas); LR5a's "Ideas RS column '—'" check updated to "no RS column" (item 9).
