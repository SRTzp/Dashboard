# RE1 — Technical specification (phase RE-A)

Branch `claude/re1a` · base `origin/main` @ 8200345 (WL1 / PR #42 merged) · 2026-11-15.
Authority order: `RE1-decisions.md` (rev 2) > `RE1-risk-engine-replacement-plan.md` > older briefs. PB1b rev 3.1, PB1c, PB1d, WL1 and MS1 workflows stay in force.
RE-A delivers **this spec + `risk-engine.js` (pure) + `tests/risk_engine_test.js`**. Nothing is wired into `index.html` (not edited), no data written, no migration, no user-visible change.

---

## 0. Conflicts found (before coding) — resolved by following RE1-decisions.md

### 0.1 decisions vs plan
| # | Plan says | RE1-decisions rev 2 says | Followed |
|---|---|---|---|
| D1 | Momentum "Open risk cap 1.80%" (plan §Momentum, "confirmed 15 Nov"); also a "projected-loss guard" that is *not* auto-approved | **No separate open-risk cap.** One money check: gross realized weekly losses + open principal risk + working-order risk + candidate ≤ 1.80% of week-start equity (monthly 7.20%) | decisions |
| D2 | Momentum stops after "4 losing ideas" (count only) | Ammunition = completed losing ideas + **distinct active ideas still reserved + distinct candidates** ≤ 4; reservation released by Option C | decisions |
| D3 | +1.5R: confirmed stop move returns *risk budget*; "does not return the losing-trade allowance already spent" | Option C: confirmed stop projecting ≥ 0 releases the **reservation** (not a completed loss); money exposure falls with projected net loss; cost edit can bring it back | decisions (completed losses are never returned; only an *unfinished* idea's reservation is released) |
| D4 | Emergency: DD −10% in a month → **next** month ×0.5; base = month-start of the trigger month | Active **from the first snapshot** (weekly or manual) with cash-flow-adjusted decline ≥ 10% from month-start; keep that reference until recovery above −5% (tested at snapshots); new month does not reset | decisions |
| D5 | Compounder unlock: both signals green + fresh data + review confirm | …**plus at least 7 days after the sixth loss closes** + short written note + explicit confirm | decisions |
| D6 | Regime-data freshness cutoff "to be specified" | Last completed US session, fetched ≤ 4 days ago; stale → factor capped at 75%, unlock blocked | decisions |
| D7 | Re-entry: user confirms whipsaw + setup valid, "details of UI/criteria not agreed" | Fixed: one extra one-tap confirm at Place order — same direction and zone · Trend inputs unchanged · ≥ 1 closed setup-timeframe candle since the stop; tagged "Re-entry" | decisions |
| D8 | Heat/open risk "reported against currentEquity" | Limits use snapshots; "open risk also shown against current equity". Denominator of the Compounder 6% heat cap not stated → engine uses **week-start equity** for the cap and also returns the current-equity percentage | decisions + open question Q3 |
| D9 | Cash-flow / FX / snapshot arithmetic, event IDs, Active net/gross: "developer to specify" | Specified in decisions §1/§5 and here (§3, §4) | decisions |

### 0.2 decisions/plan vs current code (index.html, ps1-size.js, core-size.js)
| # | Current code | New rule | Followed / action |
|---|---|---|---|
| C1 | Day reset 06:00 Thai, week Monday **06:00** (`Ps1.dayStart/weekStart`) | 00:00 daily, Monday 00:00, month day 1 00:00, Asia/Bangkok | `RiskEngine.bkk` (pure arithmetic, UTC+7). Old helpers → remove |
| C2 | `wpWeekKey()` week = **Sunday**, device-local time; `ddWeekOf()` Sunday-based | Monday 00:00 Asia/Bangkok, never the machine zone | Journal/Plan week keys must switch to `bkk.weekKey` in RE-C (open question Q8: Sunday-keyed stored week maps, `satWeek`/`satWeekPick`, are data keys — keep as keys, don't re-key) |
| C3 | `outcomeOfPnl()` rounds P&L to whole currency units (|P&L| < 0.5 = BE); `lossUnits` ignores a loss ≤ ¼ of planned risk ("scratch") | **Strict sign rule**, no tolerance | `RiskEngine.outcome`; `outcomeOfPnl` / `lossUnits` scratch rule → replace/remove. Journal win-rate badges that use the rounded rule change behaviour in RE-C (flag to owner, Q9) |
| C4 | No fee / swap / cost field exists anywhere (`grep fee|commission|swap` = 0 code hits). P&L = (exit−entry)·qty·mult | Net P&L after fees + swap; cost settings per account + strategy; never silently 0 | New schema §5.2. Until entered, idea results are **Unknown** (not 0) and Option C never releases |
| C5 | Starter ¼ is in **Core and Sat forms** (`ln4Starter*`, "Off = no Starter switch in Core + Sat forms") | Starter ¼ applies to Momentum and Compounder first entries only (decisions §2/§4); nothing for Satellite | Keep toggle + Settings row; **Satellite starter path removed** in RE-C (Q7) |
| C6 | Satellite has Main / Tactical sleeves (`satV2Sleeve/Cfg`), RPT list 0.5–2 %, caps 1.4/1.2, pyramid split `50/30/20`, `SAT_NEW_WEEK_MAX = 4`, Macro cut `SAT_MACRO_CUT = 0.6`, red factor `SAT_RED_FAC = 0.6`, trade `sizeFactor 0.6` | One Step ladder 0.20→0.30→0.30→0.40 × Condition 1.0/0.65 × Emergency; queue + daily + re-entry; no Main/Tactical; "max-open-ideas cap" not adopted | all remove; 0.65 replaces 0.6; split / weekly-quota fate in Q5 |
| C7 | Compounder = ladder cards (`strategy 'L'`, `Core.ladder`, `maxLots` 1–6 default 3, base+accelerator lots, `ladderBudget`) and `strategy 'W'` track-ladder cards | Two tranches: Pilot 0.50 % + Add-on 0.50 %, no equal-qty requirement | Existing ladder cards must map to Pilot / Add-on (Q4); no auto-resize |
| C8 | Regime: `Calc.ffCoreCap` stale threshold 5 **business** days, stale keeps latest cap (no bounce to 100 %), missing signal not counted red; `ffPoolFactor('winner')` also throttles **Momentum** by regime | Fresh ≤ 4 days; stale ⇒ cap 75 % + unlock blocked; missing ⇒ not fresh; Momentum has **no** regime input (parked) | `regimeState` is Compounder-only; Momentum regime throttle removed |
| C9 | `ps1E()` = `poolsOf().total` = **sum of entered capital** (Core ฿ + Sat $·fx), not MTM equity; pools `winner/ladder/sat` 50/30/20 weights | Equity = confirmed snapshot incl. unrealized P&L; basis = week-start / month-start snapshot, separate Main / Family | new snapshots (§5.1). `poolsOf` capital pools stop being a risk basis (Q6: keep as display?) |
| C10 | Loss brakes: PS1 `lossStep` (20 % DD stop / 10 % half), day 2R / week 5R; DD1 `ddEval/ddStep` per bucket (reduce / pause); `Ps1.capCheck` caps COMP 3 / MMT 1.5 / SAT 0.5 / total 5 % | Emergency (10 % / 5 %, ×0.5), Satellite lock, Momentum ammunition, Compounder lock; PS1 caps gone | remove all; stored `lossState`, `psRisk.*`, `coreRisk.*` settings stay in the data (no deletes), just unread |
| C11 | `ps1Used()` counts planned Core cards partly as risk | Draft/Planned reserve nothing; Ordered reserves real qty; Holding uses actual remaining risk | `RiskEngine.exposures/reservedRisk` |
| C12 | Core homework: `ftHwDone`, `coreBlkAdd` "Do homework first" | Homework cap 50 % → 100 % (WL1) and Momentum "addition needs thesis" | keep; engine takes `homeworkDone` boolean. |
| C13 | Trade record holds **one** SL (`t.sl`), `sl0` optional (Core: first `stopHistory.from`), no `stopConfirmed`, no cost fields; partial exits = separate closed rows sharing `posGroup` | Needs initial stop frozen at fill, confirmed-stop marker, per-tranche stops, fees/swap | additive fields only (§4, §5) — no migration in RE-A |
| C14 | `Calc.satLot` / `Calc.pctLoss` take the sizing distance = actual `|entry−sl|` | `max(actual, min-stop)` for size, actual for risk | engine `sizeOrder`; MS1 `ps1MinInfo` keeps feeding `minStopDist` |

Not adopted and **not implemented** (RE1-decisions §6): step-down after a win · original-attempt cap on re-entry · ±0.1R outcome band · high-water-mark Emergency · 05:00 day boundary · max-open-ideas cap · auto-block of a condition class · separate Momentum open-risk cap.

---

## 1. Inventory of existing risk / sizing / loss-limit logic

Counts = lines referencing the symbol in `index.html` (grep, includes the definition). **keep** = stays as is · **replace** = formula/gate moves into `risk-engine.js` (caller becomes an adapter in RE-C) · **remove** = superseded, deleted in RE-C. Nothing is deleted in RE-A. Stored data (settings keys, trades, cards) is never deleted — removed logic simply stops reading it.

### 1.1 `ps1-size.js` (copy inline in index.html lines 5423–5760, synced by `tools/sync_ps1.py`) — tests: `tests/ps1_size_test.js`, `ps1b_size_test.js`
| Symbol | Callers | Mark | Note |
|---|---|---|---|
| `Ps1.minStopCheck`, `ps1MinInfo/MinStopMsg/MinPct/StockMin/MinStopHint/MinStopDraw`, `psRisk.minStop` | 2 + 5 | **keep** (MS1) | adapter supplies `minStopDist` to `sizeOrder`; settings UI stays |
| `Ps1.planSize` (multi-row entries + blended stop) | 2 (`ps1AddCalc`, form) | **replace** → `sizeOrder` | per-strategy RPT, no ladder rows |
| `Ps1.addOnBudget`, `Ps1.addOnQty` | 1 + 1 | **replace** → Momentum addition / `compEntryCheck` | |
| `Ps1.capCheck`, `Ps1.panel`, `Ps1.gbLevel`, `Ps1.cfg/cfgErrors`, `BUCKETS` caps (3/1.5/0.5/5 %), give-back amber/red | 5 + 3 + 0 + 1 | **remove** | give-back *display* on Port: decide in RE-C mockup (Q10) |
| `Ps1.positionRisk`, `Ps1.satLots`, `Ps1.blendStop` | 0 | **remove** | unused in index.html |
| `Ps1.portPct` | 4 | **replace** (`pct of equity` helper in adapter) | |
| `Ps1.lossCfg/lossCfgErrors/lossStep/lossResume/lossUnits/lossStatus`, `dayStart/weekStart` (06:00) | 2/–/2/1/2/1 | **remove** | → Emergency, locks, `bkk` |
### 1.2 `core-size.js` (copy inline 4858–5419, `tools/sync_core_size.py`) — tests: `tests/core_size_test.js`
| Symbol | `Calc.coreSize.*` refs | Mark |
|---|---:|---|
| `firstLot`, `ladder`, `ladderShare`, `portfolioSplit`, `poolFree`, `accountDrop`, `openGate`, `canPlaceLadder`, `classifyTier` | 0 | **remove** (unused by index.html) |
| `addLot` | 4 | **replace** (Momentum addition / Compounder Add-on) |
| `applyStopMove` (cancels ladder rungs on stop move) | 2 | **remove** with ladders (Q4) |
| `layer2` (Core 2nd-layer %) | 1 | **replace** → heat |
| `poolSplit`, `ladderBudget` | 3 + 1 | **replace** (capital pools no longer the risk basis) |
| `ddStep`, `ddWeekOf/AddDays/DaysBetween` | 1 | **remove** (DD1) — date helpers: engine has `bkk` |
| `status` (EMA10 / stop traffic light), `vsCost`, `emergencyStop` (price), `tierBadge`, `isOlderThanMonths` | 1/1/1/2/0 | **keep** (display, not risk). `tierBadge` / CS1 evaluation never feeds sizing (PL1·A4) |
### 1.3 Inline in `index.html`
| Area / symbols | Refs | Mark |
|---|---:|---|
| `Calc.satLot`, `Calc.pctLoss` | in `sat7dCalc` (6) | **replace** → `sizeOrder` (same floor-to-lot maths) |
| `Calc.riskBudget` (PL1·A4: base × equity × f × dd − used) | – | **replace** |
| `Calc.sizeRule`, `satMacroFactors` (=1 already), `SAT_MACRO_CUT`, `SAT_RED_FAC 0.6`, trade `sizeFactor` 0.6 | 3 / – | **remove** (Condition 0.65 = `satCondition`) |
| `Calc.heat`, `Calc.readiness` (heat / quota / checks gates), `SAT_NEW_WEEK_MAX = 4` | 6 | **replace** by `satCheck`; weekly new-idea quota **remove** (Q5) |
| `Calc.ffCoreCap`, `ffCoreNow`, `ffDeployCap`, `ffPoolFactor` (12), `coreFNow/coreEff` (31) | 6 / 5 / 12 / 31 | **replace** Compounder regime → `regimeState`; `ffPoolFactor('winner')` Momentum throttle **remove**; the fund-flow *fetch/display* adapter stays |
| `ps1E`, `ps1EDate`, `poolsOf` (13), `poolPctOf`, `poolsMigrate`, `poolsWarn`, `poolStats`, `poolsPortHtml` | 12 / 13 | **replace** equity basis (snapshots); capital-pool display fate = Q6 |
| `ps1Used`, `ps1AddCalc`, `ps1NextRow`, `ps1CardNew`, `coreBlkNew/Add` | 10 | **replace** reservations (`exposures`) + gates |
| `lossOn/lossRaw/lossStartMs/lossPortValue/lossItems/lossEval(18)/lossSync(2)/lossResume*/lossBlockMsg(6)/lossChipHtml`, `settings.lossState` | 18+ | **remove** (data stays) |
| `ddEval(21)/ddSync(2)/ddNote/ddChipHtml/ddBarHtml/ddWeakest/ddSheet*/ddReview*/ddCoreBlockNew/Ladder/Add/ddSatBlock (13)/ddCfgFix/DD_BUCKETS`, `satRiskCfg.ddReduce/ddPause…` | 21+13 | **remove** (DD1 brakes + chips/bars/sheet; UI in RE-C mockup) |
| `coreRiskCfg`, `coreSizeOpts`, `CORE_RISK_DEFAULTS` (riskA/B, baseRisk, winnerCap, maxLots, tierA/B, capTotal*) | – | **replace** (RPT fixed by strategy; `market` default may stay) |
| `coreCanPlace(4)`, `coreGatesHtml`, `coreFirstRisk*`, `coreFirstLot*`, `coreLadder*`, `coreLadders`, `coreCtx`, `coreView`, `coreSim*`, `coreAddBlockReason`, `coreL2Positions/Layer2/L2Level`, `coreAcctRisk` | many | **replace** (ladder + Tier/★ risk paths); card chrome stays |
| `satV2Cfg(20)`, `satV2Sleeve(20)`, `satV2Split/ParseSplit/Money/Errs`, `SAT_V2_*`, `satRiskCfg(10)`, `satPyrSplit`, Main/Tactical settings UI (`sV2*`) | 20 / 20 / 10 | **remove** |
| `sat7dCalc(6)`, `sat7dAcctBase`, `sat7dSaveOrder` (creates `status:'plan'` trade), `sat7dMarkOpen`, `sat7dCancelSlot` | – | **replace** lot/risk/gate parts; order/fill/cancel **record flow stays** and emits events (§5.3) |
| Homework: `ftState/ftHwDone/ftList/ftBadge`, WL1 cap tags | – | **keep** (feeds `homeworkDone`) |
| Starter ¼: `ln4Starter*`, `ln4Cfg().starterOff`, Settings row | – | **keep** for Momentum/Compounder; Sat part **remove** (C5) |
| Trend/MSS: PB1b entry checks (`pb*`), news-window rules (`newsSatBlock`), Setup confirm / MSS reconfirm | – | **keep** (they call `satCondition` for the factor) |
| `realizedPnlOf`, `realizedROf`, `sl0Of`, `riskOf`, `posGroup` grouping, `holdingDaysOf` | – | **keep** (add fees/swap + strict sign: `outcomeOfPnl` **replace**) |
| `ps1Off()` / `dash.ps1Off`, `dash.ln1Legacy` dev flags (47 refs to `ps1Off`) | 47 | **remove** at cut-over (no legacy toggle, no dual runtime) |
| `heatV2*` (heat v2 migration), `Calc.accountDrop`, `Core.accountDrop` | – | **remove** if unused after audit (RE-C dependency audit) |

Size of inventory: 33 grouped rows (each row = one or more symbols) → **6 keep · 16 replace · 15 remove** mark occurrences (two rows carry mixed marks: Starter ¼ and the trade-P&L helpers).
Tests that assert old behaviour (will need retiring in RE-C, not now): `ps1_size_test.js`, `ps1b_size_test.js`, `core_size_test.js`, `run_tests_phase*` PS1/DD1/RG2 groups.

---

## 2. Engine API (risk-engine.js)

Pure UMD module (`module.exports` / `globalThis.RiskEngine`). No DOM, clock, storage, network; `now` and all state are arguments. Bad input never throws: it returns `reasons[]` with a code from §6.
Result of every gate: `{allowed, reasons[], flags[], …detail}`; `reasons` block a **new risk-increasing order**, `flags` are markers.

| Area | Functions |
|---|---|
| Time (Asia/Bangkok) | `bkk.dayStart/weekStart/monthStart/dayKey/weekKey/monthKey` |
| Sign / cost | `outcome`, `resolveCosts`, `exitCost` |
| Idea math | `ideaResult` (realized, stop-P&L, principal, est. exit cost, projected net, exposure), `netBreakevenStop`, `ammoReleased`, `rMultiple`, `realizedEvents` |
| Basis | `snapshotBasis` (week/month equity, staleness), `emergencyStep`, `emergencyFactor` |
| Sizing | `sizeOrder` (all strategies, min-stop, lots, FX, multiplier), `entryFraction` (homework × Starter) |
| Momentum | `momentumState`, `momentumCheck` (money + ammunition) |
| Satellite | `satCondition`, `satEntryOrder`, `satStepState`, `satEffectiveRpt`, `satQueueCheck`, `satStaleOrders`, `satDailyCheck` (+ re-entry), `satBudgetCheck`, `satCheck` |
| Compounder | `regimeState`, `compFactor`, `compHeat`, `compStreak`, `compUnlockCheck`, `compEntryCheck` (Pilot / top-up / Add-on), `compCheck` |
| Shared | `activeSummary`, `actionPolicy`, `asFill`, `foldEvents` |

Key decisions embedded (also covered by tests):
- **Money units**: engine works in one account currency; each tranche carries `mult` (contract multiplier) and `fx` (fixed at the snapshot). Limits are converted to money at the snapshot (`equity × pct`), compared and tracked in money — percentages of different bases are never added.
- **Idea exposure** (what a holding idea still adds to usage): per tranche, loss at its stop after its own estimated exit cost and its share of not-yet-attributed entry fees, floored at 0 (no cross-tranche offset); reduced only by realized profit of the *same* idea; realized *losses* are in the realized term (no double counting). Unknown cost ⇒ `projectedNet = null`, exposure = principal only + `COST_UNKNOWN`; unknown stop ⇒ exposure `null`.
- **Estimated net-breakeven stop** solves `realized + Σ q·(s − entry)·dir·mult·fx − exitCost(s) = 0` (fixed-point, ≤ 40 iterations).
- **Option C**: ammunition reservation is released only if **every live tranche's stop is confirmed** and `projectedNet ≥ 0` (strict, costs included). Recomputed on events only — the caller re-runs it after: stop confirm, qty change, partial exit, addition, cost edit. A returning reservation counts against *new* orders only (no position is touched).
- **Momentum gross loss**: per idea, `max(0, −Σ realized exit events inside the period)`, summed over ideas (wins never offset across ideas). Partial exits count immediately; an idea becomes a *completed loss* (ammunition) only when closed with net < 0 (strict sign), by close-time week.
- **Satellite budget** uses *net* (`max(0, −weekly net)`, wins offset within Satellite); the Active summary floors each strategy's usage at 0 separately.
- **Snapshot**: only `confirmed` snapshots count; none ⇒ `NO_SNAPSHOT`; newest older than 14 days ⇒ `SNAPSHOT_STALE` (exactly 14.000 d still usable); no snapshot in the current week ⇒ carried with `SNAPSHOT_OLD` flag. Week basis = first confirmed snapshot on/after Monday 00:00, month basis = first on/after day 1.
- **Emergency**: trigger when cash-flow-adjusted decline ≥ 10 % (exact −10 % triggers); stays until decline < 5 % (exact −5 % stays); reference (equity + time) retained across month change; deposits/withdrawals after the reference are removed from the decline.
- **Fills / reductions**: `actionPolicy('fill', check)` always `accepted:true` with `FILL_OVER_LIMIT` + the breached codes; `cancel / reduce / close / stop_update / snapshot / cost_edit` are always accepted; only `order / addon / topup / edit_increase` can be refused.
- Unconfirmed / ambiguous data is never `0`: missing equity, FX, multiplier, lot step, price, cost ⇒ reason code.

---

## 3. Data mapping — what the adapter must read (RE-C) and what is missing

| Engine input | Where it lives today | Gap / rule |
|---|---|---|
| **Account** (`main`, `fam`) | `acctList[].id`, per-account book `acctBooks[id]` (`getBook(id)`), settings in `book.settings` | direct; engine receives only one account's ideas/snapshots (tests prove no mixing). "All accounts" = report only |
| **Equity basis** | `poolsOf(A).total` = entered capital sum (`settings.capital.core / satB`, fx) | **missing**: confirmed MTM snapshots → §5.1. Until the Weekend routine writes one, gates return `NO_SNAPSHOT` |
| **Trade = tranche** | `book.trades[]`: `id, date, sym, port ('core'|'satB'), bias ('Long'|'Short'), entry, sl, tp, qty, mult, cur, status ('plan'|'open'|'closed'|'cancelled'), openedAt, exitPrice, exitDate, posGroup, sl0, unplanned, fastTrack, setup_incomplete, offplanOverride` | tranche `{id, entry, qty, stop=sl, initialStop=sl0 ?? first stopHistory.from, mult, fx, stopConfirmed}`. `stopConfirmed` **missing** (additive field, default `false` ⇒ reservation kept — safe). `side` from `bias` |
| **Idea** | Core: card `coreCards{acct, ticker, strategy 'W'|'L', track, plan, stop, stopHistory[], lots[{n,date,px,qty,f,stop,layer}], trade_id, status}`; Sat: `satIdeas{accts[acct]{trade_id, broker, lot, placed}}` | idea = card (Core) or Sat idea×account slot; `ideaId` = card id / idea id; additions = extra tranche of the same idea (never a second allocation) |
| **Partial exits** | each partial = a **closed trade row** sharing `posGroup`, own `qty`, `exitPrice`, `exitDate` (Close modal) | exit event `{id, time, qty, price, fees, swap, trancheId}`; fees/swap **missing** (§5.2); `exitDate` is a date (no time) ⇒ engine needs `closedAt` ms — stamp at close (additive) or take 12:00 Bangkok of `exitDate` for history (Q9) |
| **Working orders** | trade `status:'plan'` (Sat `placed:false/true`), Core card `status:'plan'` + `plan`, PB1b board column Ordered; order-confirmation records | `workingOrders[{id, qty, entry, stop, mult, fx, at}]`; `at` = order time (needed for the 1-day stale reminder) — **missing as ms** on most records (additive `orderedAt`) |
| **Products / lots / multiplier / FX** | `productFor(asset)` → `{contract, lotStep, minLot, cur, sys 'lot'|'pct', pointSize}` (settings `products` + builtins), stock lot 100 (TH) / 1 (US) via `coreFloorLot`; FX `settings.fx` (USD→THB, one number) | `mult = contract`, `lotStep`, `minLot` direct; `fx` = snapshot FX (`snapshot.fx`) — today FX is "current setting", must be frozen per snapshot. Missing spec ⇒ `SPEC_MISSING` (never guess) |
| **Min-stop** | `psRisk.minStop[asset]` (% of price, MS1) → `ps1MinInfo` | convert to price distance in adapter → `minStopDist` |
| **Homework / Starter** | `ftHwDone(sym)` (Watch onboarding), WL1 `plan` caps, `ln4StarterOn`, `ln4Cfg().starterOff` | → `entryFraction({homeworkDone, starterOn, isFirstEntry, usedFraction})` |
| **Condition (Sat)** | PB1b form: EMA50 / Structure / MSS answers + snapshot `label/factor` on the plan | → `satCondition`; store `is_full_condition`, `conditionFactor`, `effectiveRpt` on the order snapshot |
| **Sat attempts / results** | closed Sat trades per account, `exitReason` (not stored today — **missing**: `stop`/`target`/`manual`), re-entry flag (**missing**) | `attempts[{id, closeAt, net}]` and `dayAttempts[{product, startAt, status, net, exitReason, reentry}]`; product identity via alias normalization (`productNorm`, `SAT_PB_ASSET`) |
| **Compounder cycles** | closed Core `ladder` cards/trades by ticker (first fill → flat) | `cycles[{id, flatAt, net}]` net after costs |
| **Regime signals** | `fundflow.json` → `ffCoreNow()` (acwi/hyg booleans, `ageDays`) | `{acwi, hyg, fetchedAt}`; today only business-day age is exposed ⇒ adapter needs the file's fetch timestamp (Q2) |
| **Cash flows** | not recorded | §5.1 `cashflow` events |

All data above is **read only** in RE-C's adapter; RE-B's dry run reports gaps as *Unknown*.

---

## 4. Idea / order snapshot at Place order (what the form must freeze)

`{policyVersion, accountId, strategy, ideaId, trancheKind ('pilot'|'topup'|'addon'|'first'|'addition'), initialEntry, initialStop, stepIndex?, baseRptPct, isFullCondition?, conditionFactor?, emergencyFactor, regimeFactor?, homeworkFraction, effectiveRptPct, equityBasis{snapshotId, weekEquity, monthEquity, fx}, minStopDist?, sizingDistance, actualDistance, qty, reservedRisk, costsUsed{…|unknown}, reentryOf?}`.
1R / 1.5R / 2R always use `initialEntry` / `initialStop` frozen at fill (`rMultiple`). Changing a condition / toggle later never resizes a holding or working order.

---

## 5. Proposed schemas (additive; nothing migrated in RE-A)

All new records live in the **account book** (per account) next to `trades`, written only by RE-C code. IDs are deterministic strings so replay is idempotent.

### 5.1 Equity snapshots + cash flows
```
equitySnapshots: [{
  id: "snap:<acct>:<YYYY-MM-DD>:<n>",
  acct, at (ms, UTC epoch) , bkkDate "2026-11-15",
  kind: "weekly" | "manual",
  equity: number,            // account base currency, includes unrealized P&L
  currency: "THB",
  fx: { USDTHB: 35.2 },      // fixed for this snapshot; limits are converted to money with this
  confirmed: boolean,        // set by the user in the Weekend routine; unconfirmed never counts
  confirmedAt, source: "user" | "import",
  note?
}]
cashFlows: [{ id, acct, at, amount (+deposit / −withdrawal, base currency), note }]
```
Rules: week basis = first confirmed snapshot on/after Monday 00:00 (Bangkok); month basis = first confirmed on/after day 1 00:00; deposits take effect on the next snapshot, withdrawals reduce the basis immediately (engine: a withdrawal after a snapshot is subtracted from the displayed/used equity in the adapter; Emergency excludes both). Equity ≤ 0 or missing ⇒ `EQUITY_MISSING`.

### 5.2 Cost settings
```
costSettings: { <acct>: { winner|sat|ladder: { perSidePct, perUnit, min, flat, updatedAt, note } } }
trade.costOverride?: { perSidePct, perUnit, min, flat }     // per trade; shown in the stop prompt
```
`perSidePct` % of notional per side · `perUnit` money per unit · `min` minimum per side · `flat` per exit. Resolution: per-trade override > account+strategy > **unknown** (`known:false`). Unknown is shown as "—"/Unknown, blocks Option C release, adds `COST_UNKNOWN`; it is never 0. Incurred fees/swap are stored per event: `fees` (cost ≥ 0), `swap` (cost; negative = credit). Estimated swap for the remaining holding period is **not** modelled in RE-A (Q11).

### 5.3 Append-only event log (per account)
```
riskEvents: [{
  id,            // deterministic: "<acct>:<type>:<refId>:<seq>" — a duplicate id is ignored on replay
  type,          // order · cancel · fill · partial_close · close · stop_confirm · snapshot · cashflow · cost_edit · emergency · lock · unlock · reentry_confirm
  at,            // ms; backdated edits append a NEW event, never rewrite
  acct, strategy, ideaId, trancheId?, product?,
  payload: { qty, price, stop, fees, swap, reason ('stop'|'target'|'manual'|…), condition?, note?, … },
  by: "user" | "system"
}]
```
- Counters (steps, ammunition, streak, locks) are **derived** by replaying (`foldEvents` + `satStepState` / `momentumState` / `compStreak`), sorted by `(at, id)`; a cached copy may carry a `revision`.
- Backdated edit ⇒ current state is recomputed from the corrected log; past orders are never retro-blocked (checks run only on new orders).
- `emergency`, `lock`, `unlock` events record transitions (with `note` on unlock) so a reviewer can see why a state changed; the engine re-derives them and never trusts the cached flag alone.

---

## 6. Reason codes (every block / flag)

`B` = blocks a **new risk-increasing order** · `F` = flag / marker (information; fills still accepted).

| Code | Kind | Emitted by | Meaning |
|---|---|---|---|
| NO_SNAPSHOT | B | snapshotBasis | no confirmed snapshot for the account |
| SNAPSHOT_STALE | B | snapshotBasis | newest confirmed snapshot > 14 days old |
| SNAPSHOT_OLD | F | snapshotBasis | no snapshot yet this week/period — last confirmed one used |
| EQUITY_MISSING / FX_MISSING / SPEC_MISSING / PRICE_MISSING | B | sizeOrder | equity ≤ 0 · fx · multiplier/lot/minLot · entry/stop missing |
| STOP_EQUALS_ENTRY / STOP_WRONG_SIDE | B | sizeOrder | invalid stop |
| LOT_BELOW_MIN | B | sizeOrder | budget below the minimum lot (never rounded up) |
| CAP_HOMEWORK | F | sizeOrder | fraction < 1 (thesis not done / Starter) |
| COST_UNKNOWN | F | ideaResult / checks | cost settings missing — not treated as 0 |
| MONEY_WEEK / MONEY_MONTH | B | momentumCheck, satBudgetCheck | weekly / monthly loss budget exceeded |
| AMMO_EXHAUSTED | B | momentumCheck | completed losses + reserved + candidate > 4 |
| AMMO_OVERSHOOT | F | momentumCheck | completed losing ideas > 4 (accepted fill/close; new risk restricted) |
| ACTIVE_WEEK / ACTIVE_MONTH | B | activeSummary | Active 3 % / 12 % summary check |
| SAT_LOCKED | B | satCheck | loss at Step 4 until Monday 00:00 |
| SAT_QUEUE_BUSY | B | satQueueCheck | another Satellite setup is ordered/holding in the account |
| SAT_DAILY_LIMIT / SAT_REENTRY_USED / SAT_REENTRY_COND | B | satDailyCheck | daily slot used · re-entry already used · re-entry conditions not met |
| SAT_REENTRY_TAG | F | satDailyCheck | re-entry accepted (tag "Re-entry") |
| SAT_COND_INCOMPLETE / SAT_COND_BLOCKED | B | satCondition | EMA50/Structure unanswered · no MSS |
| SAT_NEAREST_TARGET | F | satCondition | reduced / reversal ⇒ exit at nearest key target |
| SAT_BAD_ORDER / SAT_RR | B | satEntryOrder | SL/Entry/TP order wrong · R:R < 1.5 or TP missing |
| SAT_STALE_ORDER | F | satStaleOrders | working order > 1 day — "still valid?" reminder |
| COMP_LOCKED | B | compCheck | six consecutive losing ticker-cycles |
| COMP_HEAT | B | compCheck | open principal risk + candidate > 6 % |
| COMP_THESIS / COMP_PILOT_R / COMP_PILOT_STOP / COMP_TOPUP_STOP / COMP_PHASE_CAP | B | compEntryCheck | Add-on / top-up / phase-cap gates |
| COMP_REGIME_STALE | F | regimeState | signals stale/missing ⇒ factor ≤ 75 % |
| COMP_UNLOCK_WAIT / _SIGNALS / _STALE / _NOTE / _CONFIRM | B | compUnlockCheck | the five unlock conditions |
| EMERGENCY_ON | F | (adapter label) | Emergency active (factor 0.5) |
| FILL_OVER_LIMIT | F | asFill / actionPolicy | actual fill breached a limit — accepted, restricts new risk |
| UNKNOWN_DATA | B | any check | required number missing |

Full text in `RiskEngine.REASONS`.

---

## 7. Test coverage (tests/risk_engine_test.js)

Groups map 1:1 to RE1-decisions §7: **G1** Satellite step path (−0.130 −0.300 −0.195 +0.600 = −0.025 stays Step 4, loss ⇒ lock, Monday ⇒ Step 1) · **G2** full path 0.20+0.30+0.30+0.40 = 1.20 %, cancel before fill, re-entry sizes at Step 2 · **G3** Momentum 1.35 % realized, four half-size losses, four carried positions on Monday · **G4** Option C (stop at entry vs net breakeven, cost edit, fifth loss accepted + flagged) · **G5** strict sign · **G6** Compounder (top-up, Add-on, min(75 %, 50 %), six-loss lock, unlock gates) · **G7** Emergency · **G8** min-stop · **G9** account separation, fills over cap, stale snapshot, lot below minimum. **B** boundary cases (exactly at each limit, one cent over, Sunday 23:59:59 / Monday 00:00 Bangkok, month reset with carried risk, partial exits, two accounts, duplicate events). **X** condition table, queue, stale orders, R:R, Active summary floors, cost-unknown, short side, per-tranche floors.

---

## 8. Open questions for the owner

1. **Momentum realized-loss definition across partial exits.** Engine counts per idea `max(0, −Σ period exit events)`, so a partial *win* then a later *loss* in the same week nets inside the idea. Alternative: floor every exit event separately (stricter). Which?
2. **Regime freshness.** "Fetched ≤ 4 days ago" needs the `fundflow.json` fetch timestamp (today only business-day `ageDays` is exposed). Calendar days or business days? Where does the fetch time come from — `fundflow.json` field or the workflow commit time?
3. **Compounder heat denominator.** Cap 6 % vs week-start equity (engine default) or current equity (decisions say open risk is *also shown* vs current)?
4. **Existing Compounder ladder cards** (`strategy 'L'`, up to 3–6 lots, accelerator lots, `track:'ladder'` W-cards). Mapping to Pilot / Add-on for RE-B dry-run: lot 1 = Pilot and the rest = Add-on? Any card with > 2 tranches flagged "legacy shape" and left untouched?
5. **Satellite extras with no decision**: weekly new-idea quota `SAT_NEW_WEEK_MAX = 4`, pyramid split `50/30/20` (multiple entries per setup), Sat TP1/TP2 split (`tp1R/tp1Pct`), heat/"orSat" caps — treated as **remove**. Confirm (the "max-open-ideas cap" is in Not adopted; the others are not mentioned).
6. **Capital pools** (`capital.core/satB`, 50/30/20 weights, pool used/free, `poolsPortHtml`) — keep as a display of allocation (not a risk basis) or remove with PS1?
7. **Satellite Starter ¼** exists in the current form; decisions list Starter only for Momentum and Compounder. Remove it from the Sat form?
8. **Week keys.** Journal / Sat week maps use Sunday-start device-local keys (`wpWeekKey`). Keep for display/stored data and use `bkk` only for risk — or re-key?
9. **Journal outcome badges** (`outcomeOfPnl` rounds to whole currency units): moving to the strict sign rule changes win/loss/BE counts for old trades (|P&L| < 0.5 are BE today). Apply to history too? Also: historical trades have `exitDate` (day) not a close time — attribute to 12:00 Bangkok of that date?
10. **Port "Give-back to stops" panel** (`Ps1.panel`) is tied to PS1 caps — drop with the caps or keep as read-only info in the Port mockup?
11. **Swap/overnight cost estimate** for the remaining holding period is not in the engine (only incurred swap). Include an estimate per day held in the cost settings?
12. **Re-entry scope per account**: "product per day" uses the product after alias normalization (XAU/XAUUSD). Is the daily slot per product *per account* (engine) or across accounts?
13. **Entry fees timing.** Engine attributes the entry fee to the first exit event (close-time rule) while counting it in exposure from the fill. OK, or charge it to the week of the fill?
14. **Starter for Compounder = 0.25 % of the whole plan** (engine: half of the Pilot). Confirm that "top-up to the full Pilot" means up to 0.50 % (not to 1 %).
15. **Event IDs** — deterministic string scheme in §5.3; OK to use `<acct>:<type>:<refId>:<seq>` or prefer random UUIDs generated once at write time?
