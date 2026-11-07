# PS1b audit — read-only, nothing built (branch `claude/ps1b`, from main)

Line numbers = `index.html` on this branch. Brief: `docs/briefs/PS1b-brief.md` (committed first).

## §1 Portfolio Risk panel → Today only
- Plan panel: `<div id="ps1Panel">` (3549) filled by `ps1RenderPanel()` (12170, called 12938) from `ps1PanelHtml()` (12148). CSS `#tabPlan.lf-stock>#ps1Panel` grid row 2 (2246).
- Today line: `ps1TodayLine()` (12175), placed in `td3` render (8231). Click now goes `switchTab('plan')` → will become expand/collapse of the full panel (reuse `ps1PanelHtml`). Open/closed per device in localStorage (try/catch).
- Plan › Sat "Strategy" dark box = `ln2HeaderHtml/ln2RowHtml` (22778–22800). It still reads the **old** Sat caps: `satV2Risk`, `satV2Caps` (22355: orSat/orAsset/orTot) and shows "Risk Sat $used / $cap, เหลือ $x, DD n/20%". → switch to PS1: `ps1Used(A).bucket.sat` ÷ E vs `ps1Cfg(A).buckets.sat.cap` (0.5%). Old numbers move to Details as "Legacy" (only if account has positions opened before PS1).
- Still reading old Sat caps (to be gated by "new vs legacy"): `satV2Caps` callers 22189–22192 (save check, already skipped when PS1 on), 22385–22388 (Sat meters panel `pv2m`), 22410 (asset risk), 22500–22503 (blocks, already `!psx`), 22786 (ln2 Details text), `ln2Alerts` 22770–22773 (cap alert "ใกล้เพดาน", Tactical pause, DD pause). Settings: Legacy limits card (3898) stays.
- "Legacy positions: N — cleanup when 0" in Settings: N = open `satB` trades without `trade.ps1`. New small line, no data change.

## §2 Sat min stop (% of entry price)
- Sizing: `satV3PlanAcctCalc` 22440–22510. Today: `deal = min(rawRisk, rawCap)`; `rawCap = sleeveTHB×capX ÷ (entry×contract)` (capX = `satV2Cfg.capMain 1.4 / capTac 1.2`). For PS1 orders the cap **still applies** (that is the bug in the brief). Fix: when `psx` (new order) drop `rawCap` from `min`; keep `capVal/rawCap/capX` only for old orders (`slotEx` or ps1Off) and for Details "Legacy value cap".
- Details renderer `satV2SizeLine` (22596–22615): 3 rows incl. "RPT Main 1.25%" and the "% ของเงิน Main" limit warning → replace by the 3 lines for PS1 orders; old orders unchanged.
- New setting: `settings.psRisk.minStop = {XAUUSD: 0.5, ...}` (% of entry, per Sat asset). Asset list = the products from `productCfg(asset)` (19747). Form shows "min 0.5% ≈ N pts" using last entry/price (pts = entry × % ÷ point size; I'll confirm point-size convention in `productCfg`).
- Plan form: |entry−SL| < entry×min% → inline "Stop too tight — min N pts (x%)", Save blocked (push into `blocks`). No min set → "Set min stop in Settings", Save blocked. Existing saved orders (`slotEx`) not re-checked.
- Pure fn `Ps1.satLots` (ps1-size.js 175) already has no cap; add `Ps1.minStopCheck`. `tools/sync_ps1.py` keeps the copy in `index.html` identical.

## §3 RRG speed tag
- `rrgLeanHtml` (24370–24385). Gauge source: `rrgDeltaHtml(d)` (24065): Fast = |d|≥0.5, Very fast = |d|≥1.0, sign of `x.dMom`. Tag uses `x.dMom` with the same thresholds (extract `rrgSpeed(d)` helper, reused by gauge).
- ▲ → green "⚡ speeding up"; ▼ → amber "⚡ slowing fast"; tooltip as in brief. Narrow-card rule: CSS `.rr-lean` is one row, `overflow:hidden`, `.rr-gap` last → add `.rr-sp` chip after rel chip; at narrow width swap text to "⚡▲/⚡▼" (two spans, CSS container/media toggle). Chips stay `flex:none`.

## §4 Sub-port goals
- Render: `td3GoalsHtml` (7843–7860) draws `.td3-sub` rows (Momentum/Compounder/Sat/Option). → wrap the rows in a closed `<details>` "Sub-port goals ›"; main goal row unchanged. Editor `glSubSave` (8939+) unchanged.
- Who reads `subGoals`: **only** `td3SubGoals/td3SubOf` → `td3GoalsHtml` (display) and the Settings editor. No warnings, reminders, colours, sizing or risk read it. Result: **no effect confirmed**, nothing to stop.

## §5 Loss limits — what exists and what is new
Exists today (old system, per port):
- `ddEval(A,bucket)` (9486) for `winner`, `ladder`, `sat`: tank + realised + unrealised, peak, stages normal / reduce (12.5%) / pause (20%) with cooldown weeks + recover-R (DD1, `ddCfgFix`). Used by: size factor (`ddFactor`), `ddCoreBlockAdd` (9680), `ddSatBlock` (9674), DD bars/sheet, Sat Strategy box.
- Sat Max DD `satV2.maxDd` 20 (18815), Tactical brake `satV2Brake` (22360–22372: `brkN` 5 losses in a row, `brkDd` 3%), weekly new-trade counter `SAT_NEW_WEEK_MAX = 4` (18787; `nNew/newMax` → quotaFull 22484 and readiness).
- No day/week realised-loss counter, no "Reviewed — resume" note, no 06:00 reset (Thai day boundary exists: `thaiToday`/`posThaiToday`).
New (Settings › Portfolio & Risk › Loss limits): `psRisk.loss = {ddMax:20, ddHalf:10, dayR:2, weekR:5}` + per-port state in settings: `lossState[port] = {peak, peakAt, reviewed:[{at,note,value}]}` (new keys only; nothing existing touched).
- New pure module (in ps1-size.js, testable with a fake clock): `lossStatus({port, now, trades, ports value, R})` → Normal / Half size / Stop today / Stop week / Stop & review + "opens at" time.
- Loss counting from closed trades: loss > ¼ of planned risk. Planned risk of a closed trade = `|entry−sl|×qty×mult` at close — **if SL was moved the original risk is lost**; I'll use `trade.ps1.riskMoney` when present, else `riskOf(t)`.
- Wiring: plan form blocks (Momentum/Compounder via PS1 form `ps1FormRun` 12230; Sat via `satV3PlanAcctCalc` blocks), half-size multiplier into `riskTHB` (Sat) and PS1 plan sizing; chip on Today line + plan form.
- "Old Sat DD / Tactical brake / weekly counter stop applying to NEW plans": gate with `psx`/`slotEx` as for caps (the `quotaFull`, `ddB`, `br.stop`, `ddFactor` paths in 22440–22510); shown "Legacy" only in Details for old positions.

## §6 Risk also as % of port (Details only)
- Places: Sat Details (`satV2SizeLine` psTxt 22617), Core plan form summary (`ps1SumHtml` 12185), Panel rows (`ps1PanelHtml` list), Today panel rows. Port value = `poolsOf(A).winner/ladder` for Core, `capital.satB×fx` for Sat. Format `Risk 0.30% of portfolio (= 1.5% of Sat)`.

## Questions — I stop here until you answer
1. **Existing D1 drawdown (`ddEval`) vs new Loss limits for Momentum/Compounder.** The brief says new plans use ONLY the new limits and names old Sat DD/Tactical/weekly counter to retire, but is silent on Momentum/Compounder `ddEval` (12.5% reduce, 20% pause, recover-R, cooldown) which today also cuts size and blocks add-ons. It also says half size "stacks with f/DD from D1". Do I (a) keep D1 `ddEval` running for Momentum/Compounder *unchanged* and add the new 10%/20% on top (two DD systems, stricter wins), or (b) switch off `ddEval` for NEW Momentum/Compounder plans too (one system)? I recommend (b), same as Sat.
2. **Which port value for drawdown with open P&L**: Sat has no fresh prices (`px:null`) → "approx., realised only" per the brief. OK, and for Momentum/Compounder use the same logic as `ddEval` (live card prices, realised since `baseAt`)? (I'll reuse `ddEval`'s equity number as the port value.)
3. **Half size recovery** "until half of the drop is recovered": from the trough or from the 10% line? I'll implement: stays half until port value ≥ peak − ½ × (peak − lowest value since the trigger).
4. **Min stop in points**: the "≈ N pts" display uses `productCfg(asset)` contract/lot step; is "1 pt" = 1.00 price unit (XAUUSD 1 pt = $1) for all Sat assets, or per-asset point size? I'll use 1 price unit unless `productCfg` has a point field.
5. **Day R for Momentum**: day R = default risk of the Momentum bucket (`def.winner`), for a Sat order = `satMain` for Main and `satTac` for Tactical — a day limit of 2R using which? I'll use the bucket's Main default for Sat (Tactical losses count in R-units of Main). Tell me if you want otherwise.
6. Minor: closed trades from before PS1b count toward day/week/peak? I'll count only trades closed **on/after the PS1b first-run date** (stored once) so old history never blocks you; peak starts at current value at that date.

No rule changed, no data touched. Waiting for your OK (and answers to 1, 3, 5 — the rest I'll default as stated).
