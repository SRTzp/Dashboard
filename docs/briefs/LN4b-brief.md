# LN4b — Text size on Mac + iPhone usability fixes for Today (2026-11-10)
Branch claude/ln4b from origin/main (LN4 merged). iPhone mockup: docs/briefs/ln4b-iphone.html (right phone = target). From SRTp's real use: MacBook Air 13" = layout OK but text a bit small; iPhone = hard to use (screenshot: HOT 5 big chips + "+17" over 2 rows, 3 big event boxes, To do = 3 big living-thesis chips, "Exec 0/0", Act row "Brent" wrapping one letter per line because tags + red reason squeeze the ticker).

## 1. Mac: bigger text, no overflow
- Raise the LN4 small text one step on screens ≥ 900px: 11–11.5px → 12.5px, 12–12.5px → 13.5px, 13–13.5px → 14.5px (labels, pills, grey details, status lines, Act rows, Find, forms' helper text). Headings/ticker unchanged or +1px. Use the existing size tokens/--read-fs where possible.
- Must not overflow at 1280×800 (MacBook Air 13" default) and 1440: no row wraps to an extra line that didn't wrap before, except grey detail text; pills keep one line.

## 2. iPhone (≤ 560px) — compact Today
- **Readable sizes on iPhone (minimums, SRTp: must stay readable):** body/rows 14px · secondary/grey 13px · chips/pills 13px · caps section labels (HOT/TODAY/SAT) 11px · ticker 17px · section titles 16px · buttons 14px with ≥ 36px tap height. Nothing below 11px anywhere. Compactness comes from fewer items / grouping / one-line layouts, NOT from shrinking text.
- **HOT**: one row only: as many chips as fit (max 3) + `+N`; tapping `+N` opens the full list (sheet). Same for Mac max 5.
- **HOT definition**: today 22 of 23 sectors show as HOT → too broad. HOT = RRG **Leading (lead)** + **Fresh** only; drop "weak" (outperforming but fading). Sort: Fresh first, then Leading by strength. Report the new count on current data.
- **TODAY events**: compact list, one line each, small text: `20:30 US Core CPI (Oct) · XAU`; same-time events grouped (`20:30 US CPI + Core CPI · XAU`); unknown time `--:--` → `time tbc` at the end. Max 3 lines + `+N ›`. `Calendar ›` becomes a small text link on the TODAY label line.
- **To do**: group skills of the same kind into ONE chip: `living-thesis · 7 stocks ›` (opens list), same for others. Max 3 chips on one/two lines (13px). Exec badge hidden when there are no valid setups yet (0/0).
- **Act rows on phone**: never squeeze the ticker. Layout: line 1 = ticker (no wrap, ellipsis only if > 10 chars) + type tag + status (right); line 2 = sector/macro tags + reason text (wraps), line 3 = grey details + button. Red reason may wrap; ticker never breaks mid-word. Applies to Core and Sat rows.
- Status line ("Risk-ON · …") and Daily|Weekend switch: switch stays right of line 1 if it fits, else under it — never pushes HOT down by a full extra row of empty space.
- Target: on iPhone 15 the first screen shows status + HOT + TODAY + To do + start of Act.

## 3. Status card details (SRTp 2026-11-10)
- **MACRO colours**: each stance glyph coloured — ▲ green (teal), ▼ red, ▬ grey; mixed stances keep per-glyph colours (e.g. `▼▬` = red ▼ + grey ▬). Asset code in normal text. Same in Mac and iPhone.
- **HOT = best top 3 + starred**: always show ★-followed sectors first (with a small ★), then the top 3 by strength (RRG Leading/Fresh, strongest first; Fresh keeps its blue "Fresh" tag), no duplicates; the rest behind `+N`. iPhone: as many as fit in one row in that order.
- **TODAY economic events show impact**: each event gets an impact dot/label from its tier — **HIGH = red dot**, **MED = amber dot** (LOW hidden). Sort by time; HIGH events < 4h also get the amber "in 3h 12m". Legend not needed (tooltip "High impact" / "Medium impact"). If the model only has HIGH today, report which tiers are available.

## Tests
- 1280 and 1440: font sizes raised (computed ≥ new values), no new wraps/overflow in Today, Act, Find, Watch rows, Core + Sat forms.
- 390 (iPhone 15): computed font sizes ≥ the minimums above on every Today element; HOT one row (3 + N); HOT count uses lead + fresh only; events ≤ 3 lines grouped; To do grouped chips, Exec hidden at 0/0; ticker "Brent" on one line with long red reason + 3 tags; first viewport contains Act header.
- MACRO glyph colours (▲ teal / ▼ red / ▬ grey); HOT order = ★ first then top-3 strength, no duplicates; events show red HIGH / amber MED dots, LOW hidden.
- Screenshots 1280, 1440, 390 (viewport, not fullPage). Retired → tests/LN4b_retired.md. Commit, push, compare URL. Don't merge.
