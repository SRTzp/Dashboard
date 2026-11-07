# PS1b report

**Summary (5 lines)**
1. All of the brief is built on `claude/ps1b`: §1–§6 (Today-only risk panel, Sat min stop %, RRG ⚡ tag, collapsed goals, Loss limits, port % in Details) plus §7 plan form, §8 fast-track homework, §9 `#45`, §10 RRG Fresh, §11 Ask why.
2. New suites all pass: ps1b_size 44, ps1_size 41, phase120 124, phase121 108, phase122 50, phase123 30, phase124 37, phase125 30 (390 / 1440 px; 320 px fit check).
3. Full regression (126 suites): the 17 suites that fail are the same ones that fail on `main` (missing old backup files, p13, p105, p110, p80/p81, …) — nothing new. Verify file: `docs/reports/PS1b-verify.txt`.
4. Changed expectations in old tests are logged, never deleted: `tests/PS1b_retired.md`.
5. Not done / limits: Fresh count on real data is not reported (no live RRG data here; old stored rows lack `prevDays` until the next refresh); Sat port value is realised-only (approx.); ideas↔sector linking does not exist, so "Ask why" only copies.

## Per section
- §1 Risk panel lives only on Today (collapsible, remembered per device); Plan › Sat Strategy box shows PS1 numbers; old Sat caps only as "Legacy" in Details; Settings "Legacy positions: N — cleanup when 0".
- §2 Sat min stop = % of entry per asset (required), replaces the 1.4× value cap for new orders; Details ≤ 3 lines.
- §3 RRG ⚡ speeding up / slowing fast only for Fast / Very fast.
- §4 Sub-port goals collapsed ("Sub-port goals ›").
- §5 Loss limits: drawdown 10% half / 20% stop & review per port; day 2R + week 5R (Momentum + Sat); old DD / Tactical / weekly counters do not apply to new plans. Counting starts at the first PS1b run (`settings.lossState`); `trade.closedAt` is stamped at close (falls back to exit date noon Thai).
- §6 Risk in Details also as % of the port.
- §7 a scope switch updates an open form · b stacked Entry / SL / Risk blocks, Risk / Out columns only after ＋, per-row `#shares · size%` and `−x.x%`, fit rule by container width · c rounded (not truncated) % · d Details = 3 lines · e stock min stop Momentum 4% / Compounder 7% (Settings, empty = off, every entry row checked) · f Sat Main optional 2nd entry (max 2 entries, share %, lots per entry rounded down, "0.05 + 0.04 lot", R:R on the average entry, min stop per entry, entry 2 stored as a pending add on the trade as `entry2Plan`).
- §8 No Ready block for Momentum / Compounder: amber line + "Save plan (homework due)"; unlisted tickers auto-added to the Watchlist with a `fasttrack` flag (no onboarding); one badge ⚠ Homework → ⚠ Overdue Nd; Today pin at the very top (no dismiss/snooze); overdue counted in "Unfinished today"; add-ons blocked ("Do homework first"); Journal tag "Fast-track" on trades; everything clears when thesis ①④ + screening are saved.
- §9 `#45` for stock share counts (display only); Sat stays in lots.
- §10 NEW · nd / nw tag with one constant block `RRG_FRESH`; `[All][Fresh N]` filter remembered per device.
- §11 "Ask why ›" only on Fresh cards; copies an idea-scout prompt and shows the 3-line toast (auto-hide clamp(5 s, 2.5 s + 60 ms × chars, 10 s), pause on hover/touch, tap to close).

## Notes / decisions to check
- Fresh count on current data: not reported (see 5 above). Thresholds D ≤ 3 bars / prev ≥ 5, W ≤ 1 week / prev ≥ 2 are in `RRG_FRESH`.
- "Entered ≤ 3 bars ago" is implemented as bars-in-state ≤ 3 (the entry bar counts as 1).
- Old stored RRG rows have no `prevDays`, so no NEW tag until the next refresh.
- Linking an imported idea to a sector does not exist today; the Drivers line only offers the copy link.
- Never touched: stored numbers of old plans/trades; nothing deleted; no auto-sell; no Firestore rules deployed.
