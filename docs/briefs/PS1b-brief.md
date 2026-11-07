# PS1b — Clean-up after first live use of PS1 + RRG chip speed (2026-11-08)

Branch from main (after rrg1c is merged): claude/ps1b. Lean UI. No new rules except §2 (decided by SRTp).

## 1. Portfolio Risk panel → Today only, collapsible (ONE risk system: PS1)
- Remove the Portfolio Risk panel from the Plan page (all scopes).
- Today: keep the existing one-line summary; tapping it expands the full panel (collapsed by default, remember open/closed per device, try/catch).
- Plan › Sat "Strategy" dark box: it still shows the OLD Sat open-risk cap ($ used / $ cap / left) — two cap systems on screen. For NEW plans the PS1 Sat cap applies, so the box shows PS1 numbers per account: "Risk x.xx% of 0.5% cap · left x.xx%" (+ $ in small text). Keep the DD line as is (D4 parked). Old Sat cap system is retired for NEW plans (SRTp: pick one system = PS1). Old cap numbers only in Details for positions opened before PS1, labelled "Legacy". Per-asset grouping across accounts will come with D5 (Theme ID).

## 2. Sat: minimum stop distance replaces the 1.4× value cap (SRTp decision)
Problem: Details shows "RPT Main 1.25% → 0.1487 lot · เพดานมูลค่า 1.4× → 0.1028 lot · ใช้ 0.1 lot · Risk จริง $200 (0.67% ของเงิน Main)" — mixes the old RPT with the new % of portfolio, and the value cap is unclear.
- Settings › Portfolio & Risk › Sat: **Min stop distance per asset as % of entry price** (e.g. XAUUSD 0.5%, BTC 1.5% — SRTp sets the values). Show the equivalent in points next to it in the form ("min 0.5% ≈ 20 pts"). **Required**: a Sat asset with no min stop set → "Set min stop in Settings", Save blocked (no unlimited lots).
- Plan form: if |entry − SL| < min stop → inline "Stop too tight — min N pts (x%)", Save blocked. Never auto-widen the stop.
- New orders: lots = (E × Sat risk %) ÷ (stop pts × contract multiplier), × §4b multiplier, rounded down to lot step. The 1.4× value cap no longer limits NEW orders (min stop does the job); keep it stored + shown only in Details as "Legacy value cap" for old orders.
- Details for Sat sizing = 3 lines max: `Risk 0.20% of portfolio = $297` · `Stop 20 pts × multiplier → 0.14 lot` · `Used 0.14 lot (rounded) · Risk $280`. Remove "RPT Main 1.25%" and "% of เงิน Main" lines for PS1 orders.
- Per-account default risk: an account with no Sat default shows "Set default risk in Settings" (as now) — keep.

## 3. RRG card: show fast RS-momentum moves without opening Details
Keep the 2 chips. Add ONE tiny speed tag after the Relative chip, ONLY when the RS-momentum gauge is Fast or Very fast:
- momentum ▲ Fast/Very fast → green "⚡ speeding up"
- momentum ▼ Fast/Very fast → amber "⚡ slowing fast"
- otherwise nothing.
Example: `[Lagging SPY ↗] ⚡ speeding up  [▼ Down −2.7%]` · `[Beating SPY ↗] ⚡ slowing fast  [▼ Down −1.6%]`.
- Same source as the Details gauge (same thresholds). Tooltip: "RS momentum is changing fast (last 5 bars)".
- Fit rule from RRG1b still applies: on narrow cards hide the 52W text first, then shorten the tag to "⚡▲" / "⚡▼". Chips never wrap.

## 4. Sub-port goals: keep, no effect
- Goals card: show the main goal only. Sub-port rows (Momentum / Compounder / Sat / Option "No goal set") collapse into one muted line "Sub-port goals ›" (closed by default).
- Confirm sub-port goals drive nothing (no warnings, no Today reminders, no colours). If anything reads them, report it and stop using it.

## Tests
- Plan page has no Portfolio Risk panel; Today panel collapsed by default and expands.
- Sat Strategy box shows PS1 numbers; legacy cap only in Details.
- Min stop (% of price): tighter stop blocks Save; equal/wider OK; not set = Save blocked with hint; lots formula without value cap; old orders unchanged.
- RRG speed tag shown only for Fast/Very fast, correct colour/direction; no wrap at 390.
- Goals: sub-port rows collapsed; no behaviour depends on them.
- Screenshots 390/1440. Log changes in tests/PS1_retired.md. Draft PR → main, don't merge.

## 5. Loss limits (replaces D3/D4 — decided by SRTp 2026-11-08)
Goal: total portfolio max drawdown 20% by capping EACH port (Compounder, Momentum, Satellite) at 20%. Settings must be lean.

### Settings › Portfolio & Risk › "Loss limits" (one small block)
| Field | Default | Applies to |
|---|---|---|
| Max drawdown per port | 20% | all 3 ports |
| Half size from | 10% | all 3 ports |
| Max loss per day | 2R | Momentum, Sat |
| Max loss per week | 5R | Momentum, Sat |
- R = that port's default risk per idea (Settings), so the day limit scales by itself (e.g. Sat 0.15% → day limit 0.30% of portfolio; Momentum 0.40% → 0.80%).
- "Max loss per day 2R" = 2 normal losing trades, OR fewer if a loss is bigger than planned (gap/slippage). One field replaces "2 trades/day" + "0.5%/day".
- Compounder: drawdown tiers only (long holds; a day/week loss count is not meaningful and could block buying after one stop).
- One help line only: "Each port is checked on its own. R = the port's default risk per idea. Day resets 06:00, week Monday 06:00 (Thai time)."

### Rules
| Status | Trigger (per port) | Effect on NEW trades / add-ons in that port |
|---|---|---|
| Normal | — | — |
| Half size | down ≥ 10% from its peak | risk × 0.5 until half of the drop is recovered |
| Stop for today | realised loss today ≥ 2R (Momentum, Sat) | blocked until 06:00 next day |
| Stop for the week | realised loss this week ≥ 5R (Momentum, Sat) | blocked until Monday 06:00 |
| Stop & review | down ≥ 20% from its peak | blocked until SRTp presses "Reviewed — resume" (required note); the peak resets to the current value |
- No override for day/week stops. Existing positions are never touched (no auto-sell).
- Losing trade = closed trade (incl. partial exits of the same idea, counted once) whose loss > ¼ of its planned risk. Breakeven/scratch exits don't count.
- Same idea across accounts (same asset + direction, opened within the same day) = one loss.
- Drawdown base = the port's value (allocated capital + realised P&L + open P&L where a fresh price exists; otherwise realised only, shown as "approx."). Peak = highest port value since start/last reset.
- Half size stacks with the other multipliers (f/DD from D1, Sat §4b 0.6).
- New plans use ONLY these limits. The old Sat DD bar (0/20%), Tactical loss counter/pause and weekly new-trade counter stop applying to NEW plans (shown in Details as "Legacy" for old positions only).
- UI: one status chip per port (Normal / Half size / Stop today / Stop week / Stop & review) on Today (inside the Portfolio Risk line) and in the plan form; blocked form shows one line with the reason and when it lifts ("Sat: 2 losses today — opens 06:00").
- Tests: day 2R and week 5R (incl. one big gap loss counted by size, not count), each trigger and reset time (fake clock), scratch exit not counted, same idea in 2 accounts = 1 loss, half size × other multipliers, 20% needs manual resume with note, old positions untouched.

## 6. Risk shown two ways (Details only)
- Main screens: risk always as % of portfolio.
- Details (plan form, Port panel rows, Today panel rows): add the port equivalent in brackets, e.g. `Risk 0.30% of portfolio (= 1.5% of Sat)`. Port % = risk ÷ that port's current value.
- Drawdown chips/tiers stay as % of the port's own value (unchanged).
