# TD4c — Today/Watch interaction polish · tests 109

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/TD4c-verify.txt`). Start from the TD4b final build (index sha `7ef3d7fec118…`). Backups **before any edit, including tests**: `index.backup-pre-TD4c2.html` (a file named `index.backup-pre-TD4c.html` already exists from the TD4b follow-up — do not overwrite it) · `tests/_bk_td4c/` (copy the whole tests folder first).
> Don't change formulas, risk/sizing, RRG calculations or saved data shapes unless an item says so.

## Part A — User text (verbatim, 29 Oct)

UI/UX & Feature Improvements Request
1. Today Page – Sector Section Enhancements & Header Cleanup
* Issue:
   * The Sector list in the Today tab currently displays minimal details (just ticker, name, and static text), lacking the flow status data.
   * There is redundant header text stacked vertically: an upper small label "SECTORS" and a lower bold header "Sectors Daily", wasting vertical row space.
* Requirements:
   * Header Cleanup: Remove the redundant duplicate header label. Consolidate it into a single clean section header row.
   * Data Integration: Pull and display the Sector Flow status dynamically on the right side of each sector row (matching the Flow view), including:
      * Stage/Regime badge: e.g., LEADING
      * Duration & Change: e.g., · 2 d · -1.2%
      * Trend tag/pill: e.g., ↗ strong + rising

2. Watch Page – Star Rating Interaction Alignment
* Issue:
   * In the Watch tab, tapping on the star rating requires sequential clicking to increment (e.g., clicking the 3rd star only increments it by 1 star per click rather than directly applying a 3-star rating).
* Requirements:
   * Align the interaction logic with the Today tab: clicking directly on a specific star (e.g., the 3rd star) should immediately set the rating to that exact value (3 stars), rather than cycling/incrementing one by one.

3. Candidate to Watchlist (Cand → WL) – Expand Click Target
* Issue:
   * In the Cand → WL list, each ticker row currently requires the user to tap specifically on the tiny "Screen >" button on the far right to expand/open the item.
* Requirements:
   * Make the entire ticker row/card container clickable to trigger the expand action, rather than restricting the tap target only to the "Screen >" button. Maintain proper click feedback (hover/active state) across the full row.

4. Today Page – Satellite Card Click Target Expansion
* Requirement:
   * For the Satellite section in the Today tab, currently users have to click specific action buttons (e.g., "Continue","Criteria") to navigate or open the linked page.
   * Update: Make the entire card/container clickable so tapping anywhere on the card triggers the navigation.
   * Note: Keep the existing action buttons visible in their current positions as visual indicators/labels so users can still clearly see the intended action/purpose of each card.

5. Today Page – Deep Dive Section Bug Fixes & UX Improvements
* Issue 1: Completed Tickers Still Appearing & Missing Field Ambiguity
   * Current Behavior: Tickers that already have data filled in (such as AVGO) are still being displayed in the Deep Dive section. Furthermore, the UI does not clearly indicate what specific fields/data are still missing or required for completion.
   * Requirements:
      * Filter Logic Update: Ensure that tickers with completed data inputs are properly filtered out from the pending Deep Dive list.
      * Clear Incompletion Indicator: If a ticker is considered incomplete and still needs to be shown, explicitly state which specific field or data point is missing (e.g., show a missing field badge or label like "Missing: [Field Name]"), rather than showing ambiguous placeholders.
* Issue 2: Viewport Scroll Jump on "Change" Action
   * Current Behavior: Clicking the "Change" button/option inside the Deep Dive section causes the screen/viewport to glitch and jump abruptly to the top of the page.
   * Requirements:
      * Fix the unwanted scrolling behavior. Prevent default page jump (e.preventDefault()) or retain the current scroll position when triggering the "Change" action, keeping the user anchored in place.

**User addition (29 Oct, verbatim):** "Can we place them directly in their respective section headers? For example, put Macro in Overview, or right on Macro itself since it already shows the days since the last update? As for the Risk line, would it fit on the same row as the Satellite header?" — context: bring back two items lost with "Other ▸" in TD4b — the **Macro re-check** reminder (Playbook not updated/confirmed > 30 days) and the **DD / Open Risk numbers** (DD Core · DD Sat · Heat · new · L2 · FF gate per account) with its "normal / warning" status.

## Part B — Orchestrator notes

### B1. Sectors (Today)
- One header row: `Sectors · Daily` (tf from the RRG data used) — remove the small `SECTORS` label above it. Same treatment for any other Today block that has the same double header (report which).
- Row: left = `★ XLU Utilities` + driver line below (unchanged); **right** = `LEADING · 2 d · −1.2%` (phase in quadrant colour, days in quadrant, OFF52W) + `↗ strong + rising` pill when it applies. Same values/rules as the Flow Leadership row (reuse the same helpers, no new calc). iPhone: right block wraps under the name if needed, no overflow.
- **First find why the metrics are missing today** (TD4a was meant to show them): likely the Today block only reads a *fresh* RRG cache. Rule: use the latest cached RRG for the selected tf; if it isn't today's, still show the values with a muted `as of <date>` on the header; if there is no cache at all, show `—` and a small `Open Flow to refresh ›`. Never fetch from Today. Never show a "Revisit" flag from stale data (TD3b rule stays: flag only on valid same-day data). Report the cause.

### B2. Watch stars
- Tap star n → rating = n; tap the current value's star again → 0. Same component/behaviour as the Today promote form (reuse it). Hit area ≥ 32px per star.

### B3. Cand → WL rows
- Whole collapsed row toggles its form (one open at a time — unchanged). `Screen ›` stays visible as a label. Hover (Mac) + `:active` feedback on the full row; `role="button"`, `aria-expanded`, Enter/Space. Inside the open form, clicks don't bubble to the row.

### B4. Satellite cards (Today)
- Whole card triggers the same action as its link (`Create plan ›` / `Criteria ›` / `Continue ›` / `Open ›`), opening the target in place as now. Buttons stay where they are. `Not trading this week` cards (no action) are not clickable. Same accessibility/feedback as B3.

### B5. Deep dive
- **Completeness:** define it in one helper used by Today, the reminder and `Next from Watchlist ›`: a ticker is complete when all 5 thesis parts (Tier · Business · Why · Monitor · Exit — use the app's own part names) have content **from any source** (homework parts saved in the app *or* an imported living-thesis that fills them). Find why AVGO still shows (likely only homework parts are counted, not the imported thesis) and report.
- Complete tickers are never offered as the day's deep-dive stock. If the current pick becomes complete, the day counts as done for that market and the next pick is offered via `Next from Watchlist ›`.
- Incomplete → `Missing: Why · Exit` (names of the empty parts), no placeholders like `—`/`0/5` alone.
- **"Change" scroll jump:** the Change control must not move the viewport — `preventDefault` on anchor/button, no `href="#"`, re-render without resetting scroll (save `scrollY` and restore after render, or update only the block). Check the same pattern on the other Today buttons (US/TH toggles, Next batch, Screen) and fix any that jump.

### B5b. Re-check + Risk in the headers (reuse existing logic: the old "Re-check Macro" rule ~L6178 / `pbRecheckBarHtml`, and `tdNumsHtml` + its status)
- **Macro row (Overview):** the existing right-side `4d ago` text becomes the re-check indicator. Not due → muted `4d ago` (unchanged). Due (same rule as before: > 30 days since update/confirm) → amber `34d ago · Re-check ›`; tap → Flow › Quarterly Macro (open, scrolled) where the existing confirm/update action lives. No extra row.
- **Satellite header row:** `SATELLITE` left · risk chip right, same row:
  - all normal → small muted `Risk ✓` (tap opens the numbers table — keeps the DD table reachable);
  - any DD stage hit / heat over its limit / FF gate closed → amber or red chip with the worst item, e.g. `⚠ DD Sat Main 6.2% · S1 ›` (+ `+1` if more), colour by stage as the old table did.
  - Tap → the existing DD / Open Risk table (`tdNumsHtml`) in a small sheet (iPhone) / popover (Mac). Same numbers, no new calc.
- **Core Port header row:** same chip only for **DD Core** (worst account), shown only when a DD Core stage is hit; nothing when normal.
- The chip must fit the header row at 390 (truncate the label with ellipsis before wrapping; the `›` and colour always visible). At 300 it may wrap under the title.

### B6. Tests — `phase109`
- Sectors: single header; right-side metrics equal Flow's for the fixture (fresh cache); stale cache → values + `as of`; no cache → `—` + link; no Revisit from stale data; 390 no overflow.
- Watch stars: tap 3rd → 3; tap 3rd again → 0; tap 1st from 3 → 1; persists after reload.
- Cand → WL: tapping the row body (not the button) opens the form; keyboard Enter; clicks inside the form don't close it.
- Satellite: tapping card body runs the same action as the link for each status; Not-trading card not clickable.
- Deep dive: fixture with AVGO thesis complete via import → not shown / not offered by Next; partial ticker shows exact `Missing: …`; Change keeps `window.scrollY` unchanged (±2px) at 390 after scrolling down; same for US/TH toggle and Next batch.
- Re-check: fixture 29d → muted `29d ago`; 34d → amber `34d ago · Re-check ›` → Flow Macro open. Risk: all-normal fixture → `Risk ✓` opens the table; DD Sat stage fixture → `⚠ DD Sat … · S1 ›` on the Satellite header row (same row at 390/1440), table values equal the old `tdNumsHtml` output; DD Core stage → chip on Core Port header; no chip on Core when normal.
- 300/390/1280/1440 no overflow; no console errors. Screenshots `tests/screenshots/td4c-{today-390,today-1440,sectors-390,watch-stars-390,deepdive-390,risk-390,risk-table-390}.png` — open every one.
- Old tests: never delete/weaken; log in `tests/TD4c_retired.md`. Full run (runall2.sh, base + 1–109) **after the last index.html edit**; if you edit index.html afterwards, run it again. Known: p13, p5.

## Report back
Cause of missing sector metrics · cause of AVGO showing · completeness rule · files changed · full-run results (with timestamps of the last index edit and run end) · screenshots opened · limitations · no push, no file deletion.
