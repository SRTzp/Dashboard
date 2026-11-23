# NT2c — Ideas polish: TV undo · Today Ideas fill to 3 · AI rows fit · Today resizable split

After NT2 is merged → branch from fresh origin/main. Mockup: `docs/briefs/nt2c/nt2c-rs2d-mockups.html` (sections 1–2). UIUX lens as always (no "…" cuts, nothing twice, amber = to do, blue = distance, one dark button per area).
Single file `index.html`. No Firestore rule change.

## 1 · TV tick can be undone (SRTp: pressed ✓ Set by mistake, no way back)
- After `✓ Set` the TV row shows `● TV alerts set ✓` (green) + a quiet `Undo` link at the right of the SAME line (always present while set, not a timed toast).
- `Undo` → `tvAlert=false` → the row goes back to `● TV  Copy A · Copy B · Copy ✕ · ✓ Set`. No dialog. Same for any card state that shows the TV row.
- Test: set → line shows set + Undo; Undo → chips back, Firestore `tvAlert` false; keyboard reachable.

## 2 · Today › Ideas card: fill to 3 + AI row anatomy
- Rows: due rows first (existing ranks). If fewer than 3 are due, fill up to 3 with the nearest WATCHING ideas (My ideas with a price distance, nearest first; then AI ideas by next check date) under a small label `WATCHING` (10px caps, muted). Watching rows: grey title, plain `Open ›`, one pill (blue distance / grey evidence). Never fill with dropped / in-plan / snoozed / old ideas.
- Header keeps `N due` (amber) + `N open · All ›`.
- **AI rows (theme / trade)** use the same 2-line anatomy as My-idea rows: line 1 title (wraps if long, never cut); line 2 = `check 6 Nov` + ONE pill: overdue → amber `16 days late` (replaces "AI generated" text — the THEME / TRADE tag already says it); not due → grey `evidence 3/4`. No third line, nothing clipped at any card width 320–560 (this also fixes the clipped "AI generated" descenders).
- Tests: 1 due + 2 watching fill; 3 due → no WATCHING label; overdue AI row amber `n days late`; no row taller than 2 text lines at 360 and 560 card widths; no ellipsis.

## 3 · Today page: drag to resize the 2 columns (same handle as My ideas)
- Generalise the NT2 splitter into one helper (e.g. `splitInit(el, {key, def, min, max, minOther})`) and use it for Watch › My ideas (unchanged behaviour) and Today.
- Today: right column (Ideas / To do / Risk room) default = current width; limits right 340–600px, left never under 640px; key `localStorage 'td.rightW'`; double-click / Enter resets; ←/→ keys; hidden < 1100px (phone order unchanged).
- Tests: drag → widths change + persist; clamps; reset; hidden at 1000px; Act / Ideas rows still fit (no ellipsis) at both extremes.

## 4 · Watch › AI generated list must fit any list width (bug: after resizing My ideas, AI rows overflow — chips cut at the edge, title squeezed beside the status pill)
- The list width is shared (`nt.listW`) — keep that, but make the AI list rows fit 300–500px:
  - Line 1: `TAG` + title (wraps, full width). Line 2: status pill (`Needs evidence · 3/4`) + `check 6 Nov` (wrap allowed). Line 3: summary text (wraps, no clamp with "…"; max 3 lines then the rest is in the detail — use line-clamp ONLY with a visible `more` link, never a bare "…").
  - Gains / Loses chips: one row each, `flex-wrap:wrap`; chips that do not fit on the line collapse into `+n` (count what is hidden; never cut a chip at the card edge, never `overflow:hidden` mid-chip).
  - List header: chips `All · Themes · Trades · Needs evidence · Ready` wrap to a second line if needed; `Import JSON` moves to the list ⋯ (or stays as an icon button) so it never pushes the chips.
- Tests at list 300 / 380 / 500: no element's right edge beyond the card; no text-overflow ellipsis; title never shares its line with the pill; `+n` equals hidden chip count.

## Rules
One full `JOBS=2 bash tests/run_regression.sh` after the last change · hooks PASS · only `nt2c-*.png` in the diff (revert tracked screenshot rewrites) · screenshots named after the state they show: `nt2c-tv-set`, `nt2c-today-fill`, `nt2c-today-resized`, `nt2c-ai-list-300`, `nt2c-ai-list-500`. No push until reviewed.
