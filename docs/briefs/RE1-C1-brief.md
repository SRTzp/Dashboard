# RE-C1 — Cut-over: the risk engine drives sizing and limits (2026-11-15)
Branch `claude/re1c1` from origin/main (RE-A, RE-B, TW1 merged). Don't merge. Mockup: `docs/briefs/mockups/re1c-screens.html`.
Authority, in order: this brief → `RE1-answers-A.md` → `RE1-decisions.md` rev 2 → `RE1-tech-spec.md` → the plan. Workflows PB1b 3.1 / PB1c / PB1d / WL1 / MS1 / TW1 stay. Today's layout is NOT redesigned here (that is RE-C2); only its numbers change source.
Rules that never bend: no automatic resize or change of existing positions/orders · actual fills and closes are always accepted and flagged · no data deletes · keep the existing look and tokens · no overflow at 360/390/1280/1440.

## 0. First
RE-B follow-up: in the dry run NVDA (Compounder, holding) showed engine qty 7 ≈ 0.25% with reasons HOMEWORK_50, EQUITY_PROXY. Show the full arithmetic. Reason codes must name every factor applied (STARTER, REGIME_75 …). Confirm the homework cap is not applied on top of the Pilot (Pilot already is the 50%) and that the regime factor is applied to new Compounder entries. Fix engine/adapter + tests if wrong.

## 1. Foundations (additive data only)
- **Equity snapshots** (mockup C): Settings row per account — amount, date, `Confirm`; `+ Cash flow` (date, amount, deposit / withdrawal). A manual snapshot can be confirmed any time. To do shows `Snapshot due · <account>` from Monday until confirmed. Week-start / month-start basis = latest confirmed snapshot at or before the period start. Older than 14 days → new risk-increasing orders blocked (reason shown). Deposits count from the next snapshot; withdrawals reduce the basis at once.
  - First run: no snapshot yet → use entered capital, labelled `Provisional`, for at most 14 days after cut-over; then the 14-day block applies.
- **Costs** (mockup C): per account + strategy (stocks: per share + minimum; Satellite: per lot + swap per day), per-trade override in the fill/close form. Missing → results are Unknown, a stop cannot be recognised as net breakeven, and the form shows `Add costs ›`. Never assume zero for new trades.
- **Stop confirmation** (mockup D): the stop-update form shows the estimated net-breakeven price, what confirming does (`Risk ฿0 · frees 1 idea`), and a tick `The stop is placed at the broker`. Store `stopConfirmed` + time. At +1.5R add a To do item `Move stop · <SYM>` that opens this form.
- **Starter ¼**: becomes a `Training` toggle in Settings; set it OFF once at cut-over and say so in the summary; remove Starter from the Satellite form.

## 2. Wiring — one source for every number
All sizing, limits, blocks and states come from `risk-engine.js` through the adapter: New plan / Edit / Add-on / Sat popup, Plan board + drawer, Place-order confirm, `Filled ✓`, Close trade, Port, Today's status text, Journal outcomes.
- **Form result box** (mockup A) replaces the editable "Risk per idea": one formula line naming every factor (`0.45% × homework 50% = 0.225%`), then quantity + amount, then the room line. Blocked = red box with the reason and the allowed quantity; `Place order` disabled. `Save draft` is always allowed.
- **Momentum**: projected money check + ammunition check; homework cap; additions checked when ordered; Option C release on a confirmed net-breakeven stop.
- **Satellite**: Step × Condition (1.0 / 0.65) × Emergency; queue (one active setup per account); one setup per product per day + one re-entry with the one-tap confirm (same direction and zone · Trend inputs unchanged · one closed candle since the stop) tagged `Re-entry`; working order older than a day → To do `still valid?`; lots round down, below minimum blocked. Keep TP1/TP2 split, multi-entry inside one attempt, mandatory TP, R:R ≥ 1.5, Setup confirm, MSS rules, min-stop sizing, news windows.
- **Compounder**: `Pilot | Add-on` switch; Add-on locked until thesis done + Pilot ≥ +1.5R + stop confirmed at net breakeven (list the missing ones); regime factor on new entries; heat cap; legacy-shape cards flagged and untouched; six-loss lock with unlock flow (7 days · both signals green · fresh data · review note · confirm).
- **Emergency**: evaluated at each confirmed snapshot; ×0.5 on new risk; Compounder uses min(Regime, Emergency).
- **Port** (mockup B): one risk block per account — Momentum, Satellite, Compounder with room left; Active total labelled `summary`; Emergency; basis line. Capital pools stay as `Allocation — not the risk basis`. Give-back panel stays read-only, no caps.
- **Journal**: strict sign rule everywhere; old trades use gross P&L marked `costs not recorded`; event timeline per idea.

## 3. Remove what is superseded
Everything marked replace / remove in tech-spec §1 (PS1 caps and loss brakes, DD steps, Main/Tactical sizing, Sat weekly quota and fixed pyramid budgets, legacy multipliers incl. Macro cut and 0.6 factor, Momentum regime throttle, old day/week boundaries). Old stored settings stay in the data, unread. One formula source; the sync tool must fail if the inline copy differs. List every removal in the summary.

## 4. Tests and screenshots
New suite `tests/run_tests_re1c.py` (390 / 1280 / 1440): each form (allowed + blocked), reason texts, Place order blocked while fill/close still work and flag, snapshot confirm / stale block / provisional basis, cash flow, costs missing vs present, stop confirm releases the idea, Sat step path + queue + re-entry confirm + stale order reminder, Compounder Pilot → Add-on lock and unlock flow, Emergency on at a snapshot, two accounts never mixed, no write changes an existing position's quantity. Engine + adapter tests green. Update or retire tests of removed logic and say which. Rerun 375, 374, 373, SW2, re1b, ui_audit → 0.
Screenshots `tests/screenshots/re1c-*.png` (no-animation): three forms, one blocked form, Port risk 1440 + 390, Settings snapshot + costs, move stop, Sat re-entry confirm, Compounder locked.
Commit, push, compare URL, summary: answer to §0, removals, behaviour changes the user will notice, anything unresolved.
