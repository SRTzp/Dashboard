# Daily use — short guide

Plain language. The numbers here are the ones the app shows; they all come from one place (`risk-engine.js`). Nothing in this guide changes a position or an order by itself.

## 1. Monday: confirm the snapshot
- **Settings › Snapshot** — type the account equity (including open P&L) and the date. One snapshot per account per week.
- Everything for the week is measured against the snapshot that was true at the start of the week (and the month). A snapshot also **freezes the FX rate** that was set when you confirmed it: the week and month usage is converted at that rate. A *new* order still converts at today's rate in Settings. Older snapshots without a stored rate use today's rate and say so on the Port block.
- No snapshot, or one older than 14 days: new orders that add risk are blocked (fills and closes are never blocked). `Snapshot due` on Today means this week's is not confirmed yet.

## 2. Today: the strip and the three Act groups
- **Strip** (top of Act): state (`Normal` · `Half size` · `Locked` · `Snapshot due` · `Review due`), `MMT` ideas left and room, `SAT` step and risk, `COMP` room and regime, next HIGH event. Worst state wins. On the phone only the chips that are not normal show.
- **Enter** — Planned names within 3 % of entry, and anything you flagged **⚑ Ready**. Blocked names stay with the reason; the button is disabled.
  A stock that has run more than 3 % past its entry shows an amber `passed entry · missed?` with `Cancel plan ›` or `Keep` (Keep hides it until tomorrow; nothing is cancelled for you).
- **Check orders** — every working order. After one day it says `n days · still valid?`. `Filled ✓` records the fill.
- **Manage** — holdings that need a decision, e.g. `Move stop ›` when a Momentum holding is at +1.5R or more.
- Below: **Risk room** (per strategy, this week) and **Next events** (HIGH only, Thai time).

## 3. ⚑ Ready
A flag on a Planned card (all strategies). It only puts the plan in Today › Enter. It clears itself when the plan is ordered, filled or cancelled. It never changes size or limits.

## 4. How each strategy is sized, and what a block means
| | size | blocked when |
|---|---|---|
| **Momentum** | 0.45 % of week-start equity × 50 % until the thesis is done × ½ in Emergency (× ¼ for a first entry if Starter ¼ is on) | week loss budget (1.8 %) or month (7.2 %) would be exceeded · all 4 ideas used or reserved · snapshot missing/old |
| **Satellite** | step 1–4 = 0.20 / 0.30 / 0.30 / 0.40 % × 1.0 (full trend) or 0.65 (reduced) × ½ in Emergency | step 4 loss = locked until Monday · another Satellite setup is active (queue) · one setup per product per day (+ one re-entry) · R:R below 1.5 or no TP · budget (1.2 % week) |
| **Compounder** | Pilot 0.50 % × regime (100 / 75 / 50 %) · Add-on follows the total-risk rule for the ticker | heat cap 6 % · six losing cycles in a row (locked until unlocked) · add-on before the thesis is done |

Reading a red box: it names the reason in words and, when size is the problem, how much would still be allowed (`allowed now …`). It does not show that line when the problem is something else (R:R, TP, queue, trend).
`Active` (Momentum + Satellite) is a summary check: 3 % a week, 12 % a month.
Fills and closes are always accepted. If a fill goes over a limit it is flagged and new risk is restricted.

## 5. Move stop and confirm (stocks and Satellite)
`Move stop ›` (Today › Manage, the Plan drawer, and the drawer of a Satellite holding) asks for the new stop, shows the **estimated net-breakeven price** and what confirming does (for Momentum: at net breakeven the idea is released), and has a tick **The stop is placed at the broker**. Ticking stores `stopConfirmed` and the time. With Costs OFF, breakeven = your entry.

## 6. Cancel a plan, and the Execution review
- **Cancel plan ›** (quiet text on every Planned card and in its drawer) → pick a reason (required, `Other` needs a note) → the plan is marked cancelled, never deleted. It never counts as a loss, an idea used, or a Satellite step. The same reason sheet appears on **Cancel order**.
- **Journal › Not taken** lists them (date · symbol · strategy · reason · note) with a count per reason for the week and month. `Restore ›` puts a cancelled plan back to Planned.
- **Exec goal** counts *Missed* and *Hesitated* as a valid setup **not** taken; the other reasons are left out of the ratio.
- **Execution review:** 3 × Missed/Hesitated in one week for one account → red `3 not taken` on the strip and a To do. While it is open, **New plan is locked for that account** (`Execution review due`). Everything else stays open: place order, filled, close, edit, cancel. Write two short notes (`What stopped me`, `What I change`) and press Done. A 4th one the same week asks again. It never changes any size or limit.

## 7. Starter ¼ and Costs (both in Settings › Training)
- **Starter ¼** — OFF by default. ON: the *first* entry of a Momentum or Compounder plan is sized at a quarter; you add the rest later. The review above may suggest it when you mostly hesitate.
- **Costs** — OFF by default. OFF: costs count as 0, net = gross, net-breakeven = your entry, results are never `Unknown`, and the cost fields are hidden. A trade closed while OFF stays `costs not recorded` forever. ON: fee, swap and per-trade overrides come back and results are net of costs. Turning it ON or OFF never changes a position, an order or a past trade.

## 8. What was removed, and where it went
- Loss limits, drawdown brakes (Core and Satellite), Port caps panel, Satellite weekly quota / fixed pyramid budgets, Macro cut / 0.6 factor, Momentum regime throttle → replaced by the rules in §4 (one engine, one source).
- The old Settings cards for them stay hidden; their stored values stay in your data, unread.
- "Risk per idea" boxes in the plan forms → the result box (formula · size · room).
- Candidate list → Watch › Momentum | Compounder. Reminders about candidates were removed.
