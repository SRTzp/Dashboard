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

## 7. Plan form fixes (from live screenshot 2026-11-08)
### 7a. Bug: form ignores the Momentum/Compounder switch
- Seen: header switch = Momentum, form title "New Compounder plan", but the numbers use Momentum rules (max position 7.5%, "Momentum risk after"). Title and rules disagree.
- Fix: the open plan form follows the active scope. Switching scope while the form is open → title, risk range, size cap, bucket cap and summary all update to the new bucket (keep typed prices). One source of truth for the bucket; test both directions.

### 7b. Lean multi-row layout (only after ＋; stocks only — Sat stays single entry + single SL)
```
Entry       Risk
100.00     0.25%    #14 · 1.0%
110.00     0.25%     #8 · 0.6%   ✕
SL          Out
90.00  −13.2%  50%
85.00  −18.0%  50%                 ✕
──────────────────────────────────────
#22 · 1.6% · Avg 103.64 · Risk 0.25%
```
- Units as muted suffixes inside/after the field (%, sh); no extra header row, no "Shares" column for SL rows.
- Each entry row: shares + size as % of portfolio (muted, 1 decimal). Summary shows total size % after the shares.
- Each SL row (and the single-SL form): distance from the (average) entry as −x.x% in muted text next to the price.
- Fit rule (390px): if a row would wrap, drop the row's size % first (it stays in Details), then the SL −x.x%. Never wrap, never overflow.
- "Risk" column appears only with 2+ entries; "Out" column only with 2+ SLs.
- Summary = `shares · size % · Avg (only if 2+ entries) · Risk`. "Avg SL" and "Left" move to Details (Left shown there only when ≥ 0.05%).
- If a multiplier applies, append ONE tag to Risk: `Risk 0.25% (half size: regime)`.
- 390px: each row fits on one line; ✕ never wraps.

### 7c. Rounding
- Seen: 18 sh × 10 + 9 sh × 20 = $360 = exactly 0.25% of E, but summary shows "Risk 0.24% · Left 0.01%". Percentages must be ROUNDED (not truncated) to 2 decimals and computed from the same THB numbers as the shares. Test this exact case (E ฿5,019,200, FX as used, regime 50%).

### 7d. Details = 3 lines max
1. `Portfolio ฿5.02M · prices as of 26 Oct` (amber if older than 3 days: "update account value")
2. `0.50% × regime 50% = 0.25% = $360 (= x.x% of Momentum)`
3. `After this: Momentum 0.25% of 1.5% · Total 0.25% of 5% · Size $2,790 (1.9%) of max 7.5%`
Remove "Shares rounded down to 1" (lot size is implied).

### 7e. Minimum stop for stocks (SRTp 2026-11-08)
- Settings › Portfolio & Risk: "Min stop" per bucket — Momentum **4%**, Compounder **7%** (prefilled with these values, editable; empty = off).
- Check: distance from EACH entry row to SL1 (the first real stop) must be ≥ min. Too tight → the SL row shows "Stop too tight — min 4%" and Save is blocked. Never auto-widen.
- Same style as the Sat min stop (§2). Tests: 3.9% blocked, 4.0% OK (Momentum); 6.9% blocked, 7.0% OK (Compounder); multi-entry checks every row.

### 7f. Sat Main: optional 2nd entry (SRTp 2026-11-08) — fits the CURRENT Sat form
Current form: `Entry | SL | TP*` row → `ความเสี่ยง 20 · กำไร 50 · R:R 2.5 ✓` → one row per account `OUN 0.1 lot · 20 pts · Risk $200 ✅ ข้าม`.
Change only this:
```
Entry ＋        SL            TP *
[4050]         [4070]        [4000]
[4062] 50% ✕                                   ← only after ＋
ความเสี่ยง 20/8 · กำไร 50/62 · R:R 2.5 ✓      ← avg-based, see below
OUN  0.05 + 0.04 lot · Risk $200   ✅ ข้าม
```
- Max 2 entries, 1 SL, 1 TP (single SL + full exit rule unchanged). Main only (Tactical stays single entry).
- Small ＋ in the Entry label; the 2nd row shows price + one small % field (risk share of entry 2, default 50%; entry 1 = the rest) + ✕.
- Lots per account per entry = (account risk × share) ÷ (|entry − SL| × multiplier), rounded DOWN to lot step. Account row shows `0.05 + 0.04 lot` and the total risk of both.
- Risk/reward line: with 2 entries use the lot-weighted average entry for R:R (one R:R number, same ✓/✗ min R:R rule). Points shown as `20/8` only if it fits; otherwise show avg only.
- If either entry rounds to 0 lots for an account → that account row shows "Too small to split — use 1 entry" (no wrong numbers).
- Min stop (§2) applies to EACH entry vs SL. §4b verify multiplier and §5 loss limits apply to the whole idea (one budget).
- Entering: "Buy" fills entry 1; entry 2 is a pending add on the same idea (not a pyramid — no breakeven rule, it's part of the original budget).
- Tests: 50/50 split math per account, rounding-to-0 message, R:R on avg entry, min stop per entry, entry 2 uses the same budget, Tactical unchanged, 390px no wrap.

## 8. Fast-track plans: enter first, homework right after (SRTp 2026-11-08)
Replaces PL1 A5 "Ready" BLOCK for Momentum/Compounder. Never blocks a plan any more — it nags hard instead.
- A plan can be saved even if: the stock is not on the Watchlist, not screened, or My Thesis ① Why buy / ④ Wrong if is empty.
- Form: instead of the red "Not ready" box, one amber line: "Fast-track — homework due in 3 days (thesis ① ④ + screening)". Save button text: "Save plan (homework due)".
- On save, if the stock isn't on the Watchlist: add it with its Track, fast-track flag in data (onboarding = "Unscreened"). Nothing else changes visually except the one badge.
- Homework = My Thesis ① + ④ filled AND the screening modal saved (Trend 40 EMA + lenses). Due = 3 calendar days after the plan is saved.
- Hard reminders until done:
  1. ONE small badge everywhere (plan card, position card, Watchlist row): "⚠ Homework" amber → "⚠ Overdue 2d" red. No separate "Fast-track" tag on rows/cards (the tag lives in data + Journal only). Don't add any other new chips.
  2. Today: pinned at the very TOP (above everything) — "Homework: AVGO — thesis + screening · due in 2 days" with "Do it ›" (opens My Thesis / screening). Cannot be dismissed or snoozed.
  3. Overdue (> 3 days): turns red "OVERDUE 2 days" and is counted in the Unfinished-today banner.
  4. Add-ons / pyramid / 2nd entry on that idea are blocked until homework is done ("Do homework first").
- Journal: trades from fast-track plans keep a "Fast-track" tag (so results can be compared later).
- Done = badge, Today item and add-on block disappear automatically.
- Tests: save without thesis/Watchlist works; auto-add to Watchlist with tag; Today pinned item + countdown (fake clock); overdue red after 3 days; add-on blocked until homework done; badge clears when done; Sat unaffected.

## 9. Share count notation (SRTp 2026-11-08)
- Stock share counts display as `#45`, `#60` instead of "45 sh" / "45 หุ้น" — in all PS1/PS1b UI: plan form rows + summary, Details, Port/Today risk panel, cards, add-on ticket.
- Sat stays in lots ("0.05 lot"). Stored data unchanged (display only).
- Update the brief's examples accordingly (e.g. `#14 · 1.0%`, summary `#22 · 1.6% · Avg 103.64 · Risk 0.25%`).

## 10. RRG "Fresh" highlight (SRTp 2026-11-08)
- NEW tag on a card ("NEW · 2d" / "NEW · 1w") when ALL of:
  - the card entered its current state ≤ 3 bars ago (Daily) or ≤ 1 COMPLETED week ago (Weekly; the partial week never counts);
  - the previous state lasted ≥ 5 bars (Daily) / ≥ 2 weeks (Weekly) — filters back-and-forth flicker;
  - the new state is one of: Beating SPY ↗ (strengthening), Lagging SPY ↗ (recovering), Beating SPY ↘ (fading). Not for Neutral or Lagging ↘.
- The ⚡ speed tag (§3) stays as specified.
- One filter at the top of Flow: `[ All ] [ Fresh N ]` — Fresh = cards with NEW or ⚡. Remember the choice per device (try/catch).
- Same thresholds in one constant block so they can be tuned later. In the PR, report how many cards would be Fresh on the current data (target ~3–6 of 23).
- Fit: NEW and ⚡ follow the RRG1b fit rule (52W text hides first; tags shorten to "NEW" / "⚡▲" / "⚡▼"); never wrap.
- Tests: flicker (previous state 2 bars) → no NEW; real change → NEW for 3 bars then gone; weekly partial week ignored; Neutral/worsening never NEW; Fresh filter count.

## 11. "Ask why ›" on Fresh RRG cards (SRTp 2026-11-08)
- No new row. Inside the existing "▸ Drivers & evidence" line, append a small link "Ask why ›" ONLY on cards that are Fresh (§10: NEW or ⚡). Other cards unchanged. Text shortened to "Not recorded · Ask why ›" to fit; never wraps.
- Tap → copy to clipboard (same copy + fallback pattern as other AI copy buttons, no download) and toast "Copied — paste into Claude (idea-scout)". Prompt:
  `idea-scout scan: <TICKER> <Name> turned <state label> on <date> (<Daily|Weekly>, NEW·<n>, <speed tag if any>). Find the dated driver first (evidence from before/around the turn), then the value chain and tickers.`
- When an imported idea is linked to this sector, the line shows `▸ Drivers & evidence · Idea: <idea title> ›` (opens the idea) and "Ask why" disappears. If linking doesn't exist today, use the sector's existing drivers/notes link if any; otherwise only the copy link (report in PR).
- Tests: link only on Fresh cards; copy text matches card data; no download; hidden after an idea is linked; 390px no wrap.
