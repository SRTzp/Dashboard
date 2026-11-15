# RE1 — Risk engine: final decisions + build plan (rev 2, 2026-11-15)

Companion to `docs/briefs/RE1-risk-engine-replacement-plan.md` (the plan: scope, inventory, screens, architecture, phases).
**Where this file and the plan (or any older brief) disagree, this file wins.** List every conflict you find before coding; do not resolve silently.
Workflow briefs that stay in force: PB1b rev 3.1, PB1c, PB1d, WL1, MS1 (min-stop sizing).

## 0. Fixed constraints
- Keep Today / Flow / Watch / Plan / Journal / Port / Settings, the Planned → Ordered → Holding board, Trend/MSS entry checks, thesis/homework workflow, order-confirmation records, Starter ¼ toggle.
- Keep all real data: trades, working orders, fills, stops, Journal. No deletes.
- **Never automatically resize or change an existing position or working order.**
- Block proposed orders that exceed a limit. Always accept actual fills, flag the breach, restrict new risk. Reductions, exits and stop updates are always allowed.
- All limits are **projected controls**, not guarantees (gaps, slippage, cost changes).
- Remove only superseded risk/sizing logic (PS1 caps, old loss brakes, Main/Tactical sizing, legacy multipliers, old ladders). One engine, one source of formulas.

## 1. Basis
- Risk is separate per account: **Main** and **Family** (owner level, all brokers combined). No transfer of capacity.
- Equity includes unrealized P&L. One base currency; FX fixed at each snapshot. Limits converted to currency at the snapshot and tracked in currency.
- Sizing + weekly budgets: week-start snapshot. Monthly budgets: month-start snapshot. Open risk also shown against current equity.
- Snapshot is confirmed by the user (Weekend routine). Missing → use the last confirmed one with a warning; older than 14 days → block new risk-increasing orders.
- Deposits change the basis at the next snapshot; withdrawals reduce it immediately. Cash flows tracked apart from performance.
- Resets (Asia/Bangkok): daily 00:00 · weekly Monday 00:00 · monthly day 1 00:00. A reset never erases risk from carried positions or working orders.
- Results belong to the week/month of the **close time**. Partial exits count toward budgets immediately; step / ammunition / streak logic runs only when the idea or attempt completes.
- **Strict sign rule:** net realized P&L after fees and swap < 0 = loss, > 0 = win, = 0 = breakeven. No ±R tolerance.
- Idea-level projected result = realized partial exits + incurred fees/swap + estimated remaining exit costs (no double counting). **Estimated net-breakeven stop** = stop where that result is ≥ 0.
- Cost settings: editable per account + strategy, per-trade override, shown in the stop prompt. Missing costs are never silently zero.

| Strategy | Base RPT | Weekly | Monthly |
|---|---:|---:|---:|
| Momentum | 0.45% per full idea | 1.80% | 7.20% |
| Satellite | 0.20 → 0.30 → 0.30 → 0.40% | 1.20% | 4.80% |
| Compounder | Pilot 0.50% + Add-on 0.50% | heat cap 6% | separate |

Active (Momentum + Satellite) weekly 3% / monthly 12% = **summary check**: sum of each strategy's projected usage, each floored at 0 separately (one strategy's profit never offsets the other).

## 2. Momentum
- Fixed RPT, no progression. Size = full × homework cap (50% until thesis done: ④ Wrong if + trigger + "I've reviewed this") × Starter (¼ first entry when ON) × Emergency.
- An addition completes the same idea (no second allocation); it needs the thesis, and is checked when ordered (no reservation for an unplaced second half).
- **Money check** before any risk-increasing order:
  `gross realized weekly losses + remaining open principal risk + working-order risk + candidate risk ≤ 1.80% of week-start equity`. Wins never offset. Risk per tranche floored at 0 before summing. (Same form for the monthly limit.) No separate open-risk cap; open risk stays visible.
- **Ammunition check:** `completed losing ideas this week + distinct active ideas still reserved + distinct candidate ideas ≤ 4`. One idea counts once across holdings, orders and additions. A half-size idea stopped out = one full allowance. Cancelling a fully unfilled idea releases it. Wins don't reset the weekly count.
- **Release (Option C):** at +1.5R prompt the user to move the stop to the estimated net-breakeven price. Monetary exposure falls as projected net loss falls; the ammunition reservation is released only when the confirmed stop projects ≥ 0. Re-evaluate only on events (confirmed stop change, quantity change, partial exit, addition, cost edit). A returning reservation counts against new orders only.
- An idea that ends in a net loss counts as a loss; if the weekly count reaches 4 or more, block risk-increasing Momentum orders (accept and flag any overshoot).
- Flow ① "Momentum %" is not an engine input (Momentum regime rule still parked).

## 3. Satellite
`Effective RPT = Step RPT × Condition factor (1.0 or 0.65) × Emergency factor`; Condition applied once. Lots round down; below minimum lot → blocked with the reason.

| EMA50 | Structure | MSS | Result |
|---|---|---|---|
| ✓ | ✓ | n/a | 100% |
| ✗ | ✓ | n/a | 65% + nearest-target warning |
| ✓ | ✗ | Yes | Counter trend @ MSS, 65% |
| ✗ | ✗ | Yes | Reversal @ MSS, 65% + warning |
| any | ✗ | No / blank | Blocked |

Keep: mandatory TP, R:R ≥ 1.5, Entry/SL/TP order check, Setup confirm + MSS reconfirm at Place order, min-stop sizing, news-window rules.
- **Steps** (after a completed attempt): loss → +1 step (whatever the size) · win and weekly net ≥ 0 → Step 1 · win and weekly net < 0 → **stay** · breakeven → stay · loss at Step 4 → locked until the weekly reset. Weekly reset → Step 1. Net is after costs, tested when the attempt completes. A stopped-out attempt and its re-entry are two results.
- **Queue:** one active setup (incl. working orders) per account across all products; others may stay Planned. Cancel before any fill → release, no step change. Partial exits / breakeven stops don't release until the attempt finishes. A working order older than one day → Today reminder "still valid?" (no auto-cancel).
- **Daily:** one setup per product per day, plus **one re-entry** if stopped by a whipsaw while the setup is still valid. Re-entry = one extra one-tap confirm at Place order (same direction and zone · Trend inputs unchanged · at least one closed setup-timeframe candle since the stop), tagged "Re-entry" in Journal. First loss still advances the step. Re-entry uses the **current step's normal RPT** (no cap) and current conditions; it cannot bypass budgets or a lock.
- **Budget check:** `max(0, −weekly net realized P&L) + open risk + reserved order risk + candidate risk ≤ 1.20%` (monthly same form, 4.80%).
- 65% is provisional: Journal tracks result in R per condition class; review at 30 trades per class, no automatic block.

## 4. Compounder
- Whole plan 1%: **Pilot** = first 0.50%, **Add-on** = second 0.50%. Share quantities need not be equal.
- Thesis incomplete → Pilot only (WL1 homework cap 50%).
- Starter ON → first entry 0.25%; **top-up** to the full Pilot needs the first tranche's stop confirmed at estimated net breakeven (no thesis needed).
- **Add-on** needs: thesis complete + Pilot ≥ +1.5R + Pilot stop confirmed at estimated net breakeven. Top-up and Add-on may go together when Add-on conditions are met.
- Heat = current open principal risk (same idea-level calculation), cap 6%.
- Regime (ACWI/BIL, HYG/IEI): both green 100% · one red 75% · both red 50%. Applies to new-entry risk at entry time only. With Emergency: `factor = min(Regime, Emergency)`.
- Signal freshness: last completed US session, fetched ≤ 4 days ago. Stale → factor capped at 75%, unlock blocked.
- **Lock:** six consecutive losing ticker-cycles (first fill → flat; a win resets; exact breakeven neither counts nor resets). **Unlock:** at least 7 days after the sixth loss closes + both signals green + fresh data + short written review note + explicit confirm. Streak returns to 0. No EMA40W rule.

## 5. Shared
- **Min-stop:** `sizing distance = max(actual Entry–SL distance, configured minimum)`; risk and results use the actual SL; never move the user's stop.
- **Emergency:** active from the first snapshot (weekly or manual) showing a cash-flow-adjusted decline ≥ 10% from month-start equity; factor 0.5; new risk-increasing orders only. Keep that month's reference until recovery above −5%, tested at snapshots; a new month does not reset it.
- Draft/Planned reserves nothing; Ordered reserves its real quantity; Holding uses actual remaining risk.
- Append-only event log (order, cancel, fill, partial close, close, stop confirm, snapshot, cost edit, emergency, lock/unlock); counters are derived; event IDs prevent double counting. Backdated edits recompute current state and never retro-block past trades.

## 6. Not adopted (do not implement)
Step-down after a win · original-attempt cap on re-entry · ±0.1R outcome band · high-water-mark Emergency · 05:00 day boundary · max-open-ideas cap · auto-block of a condition class · separate Momentum open-risk cap.

## 7. Build plan — one branch per phase, each reviewed before the next, never merge yourself
| Phase | Branch | Delivers | Changes behaviour? |
|---|---|---|---|
| **RE-A** | `claude/re1a` | `docs/briefs/RE1-tech-spec.md` (inventory keep / replace / remove with callers, data mapping, schemas for snapshots, FX, costs, event log, open questions) + `risk-engine.js` pure functions (no DOM, clock or storage) + engine tests | No — engine not wired in |
| **RE-B** | `claude/re1b` | Read-only migration dry run on the user's data: report of open trades, missing data (Unknown, never 0), old vs new size, counters rebuilt from history; backup/export step | No — no data writes |
| **RE-C** | `claude/re1c` | UI wiring + one-time migration + removal of superseded logic. Starts only after the orchestrator's mockup of the changed screens (form result box, Port risk rows, Today status, Settings) is approved | Yes — cut-over |
| **RE-D** | `claude/re1d` | Full regression, 390/1440 screenshots, ui_audit 0, updated `GUIDE-daily-use.md`, list of what was removed | No |

### RE-A engine tests must include
1. Satellite: −0.130 −0.300 −0.195 +0.600 = −0.025 → stays at Step 4; one more loss → locked; Monday → Step 1.
2. Satellite full path 0.20 + 0.30 + 0.30 + 0.40 = 1.20% → budget and lock agree; cancel before fill → no step change; re-entry after a Step 1 loss sizes at Step 2.
3. Momentum: realized 1.35% → at most 0.45% combined open + pending + new; four half-size losses (≈0.90%) → locked; four carried full-risk positions on Monday → no new entry until a stop is confirmed at net breakeven.
4. Momentum Option C: stop at entry (not net breakeven) keeps the reservation; net-breakeven stop releases it; later cost edit can bring it back without touching the position; fifth loss accepted and flagged.
5. Strict sign rule: stop-at-entry exit netting negative = loss (Satellite step +1, Momentum allowance used).
6. Compounder: Starter top-up without thesis allowed, Add-on without thesis blocked; `min(Regime 75%, Emergency 50%) = 50%`; six-loss lock; unlock refused before day 7, with stale data, or without a note.
7. Emergency: −10% at a mid-month snapshot → half size immediately; stays through month change; off above −5% of the retained reference; cash flows excluded.
8. Min-stop: actual 2%, minimum 4% → size on 4%, risk reported on 2%.
9. Accounts never mix; fills over a cap are accepted and flagged; snapshot older than 14 days blocks new risk; lot below minimum blocks.
