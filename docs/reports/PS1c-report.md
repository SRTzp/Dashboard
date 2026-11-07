# PS1c report — plan form redesign + Today homework row

Branch `claude/ps1c` (from `origin/main` after PS1b #16). Draft PR, not merged. Brief `docs/briefs/PS1c-brief.md` (FINAL LAYOUT §7–§10), audit `docs/briefs/PS1c-audit.md`, mockup `docs/mockups/ps1c-mockup-proper.html`.

## What changed (all in `index.html`; sizing maths untouched)
- **Port bug (root cause)**: `coreNewIn()` re-derived the plan's port from the Watchlist track on every keystroke. Now `n.track` changes only through the form's own **Momentum | Compounder** switch (or the Core header / top switch, synced both ways). Watchlist track = starting value when the form opens; muted note `Watchlist track: Momentum (unchanged)` when it differs; Watchlist never modified.
- **Per-port drafts** (`ps1DraftSave/Load`): entry, SL, risk, rows, splits kept per port, never carried across.
- **Split %**: entry field = % of the idea's risk (even defaults 50/50 · 34/33/33 · 25×4), total must be 100, adding/removing a row resets to even; risk edit updates rows automatically. Shares use the same `Ps1.planSize`; saved data format unchanged.
- **Form layout**: single trade one row; after ＋ `Risk per idea [x %] + regime pill`, then two columns Entry · split | SL · out; ✕ column reserved on row 1 so every row is the same width; result under its own box.
- **Summary** `#57 · 4.0% · Risk ฿9.9k (0.20%)` (all % of total portfolio, ฿ at the dashboard FX/E), amber multiplier pill, "Above max size 7.5% — shares will be trimmed", always-visible light grey port line `x% of MMT · cap 7.5% (y% of MMT) · Details ›`.
- **Plan top bar** `Core | Sat` (2 buttons, `planScope` values unchanged, last Core port restored); Momentum | Compounder switch in the dark Core header and in the form; main tabs no longer shift (`.hd-plan` removed); S / D / F keys unchanged. On narrow phones Core | Sat falls back to the line under the header.
- **Sat form**: ＋ on the label line (20px), Entry 2 is the same size/column as Entry 1, its % + ✕ in the SL column, TP column empty.
- **Today**: Plans rows carry the ⚠ Homework / ⚠ Overdue badge; homework = ONE row with chips (amber / red overdue, `+N` expands in place, `Do it ›` = most urgent).

## Tests
- New `tests/run_tests_phase126.py`: 85/85 PASS (390 + 1440). phase120 124/124 · 121 108/108 · 22/89/97/99/113/118/123/124 updated and passing.
- Full `runall2.sh`: all remaining failures are identical on `origin/main` (list in `tests/PS1c_retired.md`).
- Changed expectations: `tests/PS1c_retired.md`. Backup: `index.backup-pre-PS1c.html` (local, git-excluded).
- Screenshots 390 / 1440: `docs/reports/ps1c-shots/`.

## Deviations / notes
- Core | Sat does **not** fit in the header at 390 → on the compact line under the header (as agreed). Mac: in the header before the icons.
- Single-trade regime pill shows only when a multiplier applies (m < 1); 2-column mode shows it beside Risk per idea under the same rule.
- The `ps1Off` developer mode keeps the old summary text.
