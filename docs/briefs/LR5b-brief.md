# LR5b · Journal tab (match the mockups)

Branch `claude/lr5b` from main (after LR5a merges, or in its own worktree with a rebase before the final regression).

## Rule
Spec: `docs/briefs/lr/Journal.dc.html` (1440) + `JournalPhone.dc.html` (390). Same hook, engine, light-only and English rules as LR5a.

## Desktop
1. **Header row:** "Journal" · account switch `Main · Family · Both` (default = active account; Both = read-only merge) · port chips `All · MMT · COMP · SAT` · period `Week · Month · Quarter · All` (right).
2. **Five stat cards:** Result · net (money + R + trade count) · Win rate · avg R (win / loss) · Followed the plan (n / total + discretionary exits) · Not taken (count + hesitated / missed / invalidated, amber card) · To review (closed with no reason yet).
3. **Closed table** (one line per trade): Closed date · Trade (ticker · port tag · account pill) · R · P&L (account currency) · Plan (✓ Followed / × Early exit / Late exit …) · Reason · lesson (reason chip + one-line lesson, or amber "needs a lesson"). Bottom link: `Not taken (n) · why didn't I enter? ›` opens the existing Not-taken list (RE4 reasons).
4. **Review panel** (right) for the selected trade: Planned vs Actual table (Entry, Stop, Target, Result); note "R measured on the planned stop (1R = x), never the moved one"; WHY IT CLOSED chips (Planned exit · Stop · Gap / slippage · Discretionary); ONE LESSON (optional textarea); `Thesis when I entered ›` (collapsed, from the stored snapshot if any); black `Save review`.
5. **R rule:** R = P&L ÷ risk at the ORIGINAL planned stop. Use the existing stored original stop; if a trade has none, show R as "—" with a tooltip. Do not change engine numbers; this is display.
6. Data: reuse existing fields (RE4 not-taken reasons, exec review, trade notes). If "why it closed" or "lesson" has no field yet, store them on the trade doc as `review: {why, lesson, at}`. Additive only, and note it in the summary.

## Phone (390)
Follow JournalPhone: compact header (account + period), stat cards 2 per row (Result, Followed, Not taken, To review), trades as 2-line rows (ticker · R · P&L / plan mark · reason), tap → review as a bottom sheet with the same content, `Not taken ›` row.

## Proof (required)
- `tests/screenshots/lr5b/journal-1440-side.png`, `journal-390-side.png` (fixture: winners, losers, an early exit, a gap through the stop, not-taken rows, both accounts), `journal-390-review-live.png`, `journal-1440-both-live.png`.
- `tests/run_tests_lr5b.py` in `run_regression.sh`: stats match the fixture by hand, R on the original stop (moved-stop case), Both = sum of both accounts with correct currency, review save round-trip, period/port filters, no Thai in `#tabJournal`, one line per row at 360/390/1440.
- `docs/reports/LR5b-summary.md`: remaining differences + reasons, new fields (if any), full regression 0 failing. Commit in parts A–D.
