# NT1b — Ideas you don't forget

Branch `claude/nt1b` (from origin/main with NT1 + PC2). Not merged.

## What changed (all in `index.html`)
- **My ideas data** — new optional fields on `users/{uid}/ideas_my`: `next` (≤120), `level` (number), `snoozeTo` (date), `planId` (core card id), `dropped` (bool). AI ideas keep `user.snoozeTo` / `user.done` in their existing `ideas` doc.
  **Firestore: only new fields on the existing collection — the NT1 rule already covers them. No rule change.**
- **Sheet** — green group before Save: Next step · Check again on (pre-filled +3 trading days, never empty) · Price level (stock / Sat only, "remind within 3%"). Old ideas without a date get created + 3 trading days (computed, written only on edit).
- **Today › Ideas card** (right column, first) — due ideas from both sources, max 3, order: price near level → overdue → today → AI; reason pill, one outline button per row (`Make plan ›` / `Open ›` / `Add evidence ›`), `Next: …` line; ⋯ (header + row hover / long-press): Snooze 3 days · 1 week · Done (+3 trading days) · Drop idea (Undo toast). Nothing due → one line. Replaces NT1's To do `IDEA · Check:` line.
- **Watch nav** — amber count pill (top nav = phone nav).
- **My ideas** — `Next · due` line, trail Idea → Plan → Holding (`planId`, set when a plan saved after `Make plan ›`), stale prompt after 30 days (Keep · 1 week / Drop), `Due` filter chip, Next-step block above the chart in the detail.
- **Today status card** (left column above Act): MOOD (+goal) · TODAY (`in 6h 48m` pill < 8 h) · HOT · MACRO; replaces Market mood + Hot sectors cards. CHECK ORDERS hidden at 0 working.
- **UIUX fixes ①–⑥** — one dark primary (first Place/Filled/Add-on in Act), homework group amber, Act homework text replaced by muted `Homework → unlocks adds ›`, Risk room one line per account (long text + regime note in tooltip), right column 440px, 1440×900 fits without scroll, phone order status → Act → Ideas → To do → Risk room.

## Notes / limits
- Price proximity uses the last close (`pxAuto`) → stocks only. Sat assets have no price source, so Sat ideas get date reasons only. trade@1 has no numeric entry level, so trades have no price level.
- Dropped My ideas are hidden (Undo toast restores); no "dropped" list view.
- Make plan › stores `planId` through a pending link (≤2 h, same ticker) set in `coreNewSave`.
- Older suites updated for the new layout: lr2, lrf, lrf2, clean1, rk1, pv1, nt1 (glance cards → status card, Risk room short text, SAT per-trade value now in tooltip/hidden text, Today height re-baselined 975 → 1129 at 390).

## Proof
- `tests/run_tests_nt1b.py` (273 checks) — added to `run_regression.sh`.
- Side-by-side PNGs: `tests/screenshots/nt1b/` (Today-1440, Ideas-card, New-idea-sheet, My-ideas-list, My-ideas-1440; Today-390 / My-ideas-390 live only).
- Hooks superset: PASS.
