# PL2b — Swipe zones + "เลือกศึกษา" ordering

Status: AGREED SCOPE (2026-11-05). Build on branch `claude/pl2` AFTER the PL2 items are done.
Supersedes any earlier mobile-layout proposal: do NOT stack Value Chain cards, do NOT turn the Evidence table into cards.

## 8. Main-tab swipe: restrict where it can START
Orientation = device orientation (use `matchMedia('(orientation: portrait)')`, re-evaluate on change/rotate).
- **Portrait:** a swipe may switch main tabs ONLY if it starts inside the bottom nav bar (Today / Flow / Watch / แผน / Journal / Port).
- **Landscape:** ONLY if it starts in (a) the top header/nav strip, incl. the sync-status area ("ซิงก์แล้ว") and empty space around the nav, or (b) the visible left/right outer gutters outside the content panels. Gutter zones never overlap cards, tables or other content.
- Eligibility is decided at touchstart from the start point only. A gesture that starts in content can never become a tab swipe, even if it crosses an allowed zone.
- Keep: horizontal scroll inside cards / tables / tab strips (including at their scroll ends), vertical page scroll, normal button taps. A recognised swipe must not also fire a click on the element where it ends.
- Keep the existing tab order and swipe direction. Don't intercept OS/browser edge gestures (use the app's visible gutters only).
- Make sure the Value Chain card row and the Evidence table actually scroll horizontally (not clipped): check overflow-x, touch-action and any parent overflow:hidden.

Tests (Playwright, touch emulation, portrait 390×844 + landscape 844×390):
- Portrait: swipe in bottom nav → tab changes; swipe in content / on Value Chain / on Evidence → tab unchanged, element scrolls.
- Landscape: swipe from header, sync area, each gutter → tab changes; swipe on cards/table → no tab change.
- Start in content, end in an allowed zone → no tab change.
- Rotate (resize + orientation change) → zones switch correctly.
- Swipe ending on a button → no click fired. Tap on a button → click works.

## 9. "เลือกศึกษา" (Value Chain segment pick)
Existing behaviour (audited by SRTp's planning chat — verify, don't change):
- Saved in the Ideas doc: `user.pick[<segment name>] = true/false` via `ideaPick()` → `ideaUserPatch()` (overrides the AI's `segments[].pick`). Read in `ideaView()` (~14517).
- Only downstream use: `ideaExportObj()` writes it into the exported JSON (`chain.segments[].pick`). The `idea-scout` skill's `pick` mode then researches companies only for segments with `pick: true`.
- It does NOT generate picks inside the dashboard. It is a saved selection for the next idea-scout run.

Add (display only):
- Checked segments are shown first (leftmost) in the horizontal Value Chain row. Stable order: keep the original relative order inside the checked group and inside the unchecked group.
- Unchecking puts the card back in its original relative position among the unchecked ones.
- After checking, scroll the ROW horizontally so the card is visible (`scrollTo({left})` on the row only). Never move the page vertically (no `scrollIntoView` on the page).
- Order is rebuilt from the saved `user.pick` on reload. Never reorder the stored `chain.segments` array or the export order.

Tests: check → card moves to the left group + visible in the row, page scrollY unchanged; uncheck → back in place; reload → order rebuilt; export JSON segment order unchanged.

## Report
Include the "เลือกศึกษา" purpose + downstream effect (confirmed or corrected) next to the implementation summary.

## Additions (2026-11-05, from SRTp's self-contained brief — these override anything above)
- Layout: also no text shrinking or truncation to fit the phone. Wide content scrolls inside its own container.
- Portrait: no tab swipe from the top header or side margins either — bottom nav ONLY.
- Landscape gutters = the visible empty background outside the content panels. No invisible overlays on content. If no gutter is visible at the current width, there is no gutter zone.
- Detail-tab strips (Summary / Mechanism / Evidence / Value Chain / Companies) count as scrollable content: never a tab-swipe start.
- Applies to the global main-tab gesture handler (all tabs/screens), not just Ideas.
- "เลือกศึกษา": keep the user's selection visually and logically separate from any AI-recommended label/flag on the segment (e.g. the scan's recommended segments). Report the existing AI-recommended field (if any) and confirm the two never overwrite each other. Note: ideaView() currently falls back to the AI's segments[].pick when the user hasn't set one — report this and confirm whether that fallback makes an AI value look like a user selection.
- Verification: Playwright WebKit with iPhone device emulation (touch, portrait + landscape, rotation). List anything that can only be confirmed on a real iPhone so SRTp can check it by hand.
