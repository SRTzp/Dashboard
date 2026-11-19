# AU1 · Phase A — map of the legacy calculators (no code changed)

Branch `claude/au1` (from origin/main bf8449f). Report only. Nothing is deleted or edited in this phase.

## 0. How this map was made (read this first — it says how much to trust each claim)

| Evidence | What it proves | What it does not prove |
|---|---|---|
| **Runtime probe** (Playwright, 1440 px, the RE-D fixture `doc_c()` + `cards()` + extra Momentum / Compounder plans + Sat ideas `XAUUSD` / `BTCUSD`). Every legacy function wrapped; steps: Today · Plan board (plan / hold) · drawer (plan / ordered / holding) · Port (both / core / sat) · Journal · Flow · Watch · Settings · Stock form · Sat form. | "This function ran when screen X was drawn." | Whether the number reached the glass (a function can run and its result be thrown away). |
| **DOM visibility scan** (same steps): every element carrying a legacy `data-*` hook, with computed visibility. | "This hook is on screen / not on screen." | Hooks that are never built are simply absent. |
| **Coverage run** (§6): an instrumented scratch copy of `index.html`, every legacy-family function + every `Calc.*` / `CoreSize.*` method reports its first call; the whole `run_regression.sh --quick` set (node + 17 core browser suites) was run against it. | "Never called by any of the core suites" = strong dead evidence. | Not the full 149-suite run (131 of those already fail on main, RE1-D summary) and not hand-driven paths. |
| **Static name graph** (identifier references between top-level declarations; comments stripped). | A function with **no** referrer at all is dead. | A function with a referrer may still be unreachable (the referrer can be dead) — the graph over-approximates. |

Legacy-vs-RE1 numbers (§4) are the real numbers produced by the app on the fixture, read in the page (`coreFirstLotCalc`, `lfAddCalc`, `satV3PlanAcctCalc`, `re1CardModel`, `Re1Adapter.*`). Probe scripts are not committed (scratch only).

Fixture (main account): Core capital ฿7,858,000 total, pools 50/30/20 → Momentum ฿3,929,000 · Compounder ฿2,357,400 · Sat ฿1,571,600 (`poolsOf`). RE1 base = confirmed weekly snapshot **฿5,000,000**. fx 33 · Regime factor 1.00 · Emergency 1.00 · no thesis done (homework 50 %).

> **Headline.** The app has two risk bases side by side. Legacy sizes from the *pool capital* (`poolsOf` → ฿7.858M split 50/30/20, % of **pool**); RE1 sizes from the *week-start equity snapshot* (฿5.0M, % of **equity**). Every legacy-vs-RE1 mismatch in §4 traces to that, plus RE1 having no "50 % of the previous lot" add rule.

---

## 1. Callers → what they feed → is it visible today?

Legend: **VIS** = reaches the screen today · **HID** = computed, thrown away / behind a flag / not rendered · **DEAD** = no live caller (see §6 for the coverage proof).
"Hook" = the `data-*` / id to look for. "dev flag" = only runs when `dash.ln1Legacy` (localStorage) is set; users never have it.

### 1.1 `Calc.coreSize.*` (inline copy of `core-size.js`; also `Calc.coreSize` getter at `index.html:23391`)

| Method | Callers (function:line) | Feeds | Hook | Status |
|---|---|---|---|---|
| `poolSplit` | `poolsOf:14589` · `poolPctOf:14572/14575` · `crOnInput:22883` · `poolHintUpd:22954` | Pool ฿ split used everywhere (Port pool lines, Settings hint, Sat cap, ps1E equity fallback) | `data-pool-line/-bar/-txt`, `[data-pool-hint]`, `#poolHint` | **VIS** (Port pool line — closed fold, one tap · Settings hint) |
| `poolFree` | `coreCtx:14814/14816` | `cx.cashTHB`, `cx.split` (free cash Momentum / Compounder, Compounder % of pool) | `data-ln3-risk` (Port, 2nd line) | **VIS** (Port › Core risk fold, closed by default; the Plan form's legacy cash/first-lot HTML is not rendered) |
| `layer2` | `coreLayer2:14932/14937` ← `coreL2Positions` ← `coreAcctRisk` | "to SL now x% · full y%" | `data-ln3-risk` (Port) | **VIS** (Port › Core risk fold, closed by default) · Today `l2` task + `nums` table are **DEAD** (`coreL2Level` is hard-coded `'ok'`, table `[data-td-det]` not rendered) |
| `vsCost` | `coreAcctRisk:14953` · Today code `~10300` | `vsCostTHB` (P&L if every stop hits) | not rendered (only returned) | **HID** |
| `status` | `coreView:14976…` | green / yellow / red / na position state | Today: *Sell all* task, *stale price* task, *green → add* chip; `td3-dot` in Today plans block | **VIS** (position-health signal, not sizing) |
| `emergencyStop` | `coreView:14981/14987/14991` | emergency stop price `v.emg` | only inside dead `coreEmgOpen` | **HID** (computed on every card draw, never shown) |
| `firstLot` | `coreFirstLotCalc:14856` ← `coreNewIn`, `coreNewSave`, `coreBuy1Open`, `csUsedOther`, `wl1Lot` | legacy first-lot numbers | `data-c-qty`, `.ccQty` (`coreFirstLotHtml` / `PlanHtml`) | **HID** — the HTML builders are not on any visible surface; `coreNewSave`/`coreBuy1Open` read only `.ok`. Run-time hits come from `csUsedOther` (cap bookkeeping). |
| `addLot` | `coreSimCalc:15012` · `lfAddCalc:15741/15756` | add-on size for cards **without `plan.ps1`** | `data-c-addqty`, `[data-sim-res]` | **DEAD** (never hit in probe or coverage; PS1 cards go to RE1 via `ps1AddCalc`) |
| `ladderBudget` / `ladder` | `coreLadderCalc:14756/14762` ← `coreView:14967`, `coreLadders`, `coreStopPreview`, `coreNewInL` | Compounder ladder budget (strategy `L` cards) | `data-c-lad*` | **HID** for the board/Today (value computed, `v.lc` unused outside dead card HTML); `coreLadders` feeds `poolStats` / Port pool lines → **VIS** via `heldTHB / reservedTHB` |
| `tierBadge` / `classifyTier` | `coreTierBadges:16048/16049` · `coreTiEval:16180…` · `wlTierStale:18952` | A / B tier chips | `coreTierBadgeChips` | `tierBadge` runs (via `coreTiEval` while the stock form is filled) but chips are only in dead card HTML → **HID**; `classifyTier` **DEAD** (`wlTierStale` has no caller; badges only in dead card HTML) |
| `ddStep` | no call in `index.html` (only comments at `14022…`) | — | — | **DEAD** (DD1 UI was removed in RE-D; only `core_size_test.js` calls it) |
| `emergencyStop`, `applyStopMove` | `coreStopPreview:17182` · `coreStopSave:17197` | Move-stop form (preview / save) | `#coreStop*` | **VIS** only through "Move stop" from the card menu in the legacy panel → **HID** on the board (board uses `re1SatStopOpen` / `ln4RaiseStop`) |
| `portfolioSplit` `ladderShare` `accountDrop` `openGate` `canPlaceLadder` | `coreCanPlace:14825/14828` ← `coreNewInL` only | Compounder new-ladder gates | `data-c-gates` | **DEAD** |

### 1.2 `Calc.satLot` · `Calc.heat` · `Calc.pctLoss` · `Calc.readiness` · `Calc.newCount`

| Function | Callers | Feeds | Status |
|---|---|---|---|
| `Calc.satLot` | `sat7dCalc:24242` · `satV3PlanAcctCalc:26111` (v1 branch only) · `satPyrCalc:26446` | lot for **pre-v2 Sat ideas** (`idea.v2` falsy) and the pyramid add | v2 ideas never reach it (RE1 `sizeSat`). **VIS only for old v1 ideas** via `satV3ReadyAccts` → Today/`ln4SatRows` ready accounts and `satV3SaveSlot` |
| `Calc.pctLoss` | `sat7dNum:24119` ← `satV3CondEdit` | %-loss product sizing in old condition editor | **DEAD** |
| `Calc.heat` | `sat7dAcctBase:24216` · `sat7dCalc` · `satV3PlanAcctCalc:26118` · `satPyrCalc:26459` | `heatPct` of the Sat pool | Today `heat Sat` task (`tdBuild:~10365`): Lean branch uses constant `CP.sat = 0` → never fires → **DEAD**; non-Lean branch = dev flag. `satV2PlanCalc` sets `heatPct:null`. → **HID** |
| `Calc.readiness` | `sat7dCalc:24252` · `satV3PlanAcctCalc:26120` · `ln1StrategyBarHtml:26975` (comment) | v1 ready/warns | v1 ideas only (as `satLot`) |
| `Calc.newCount` | `sat7dAcctBase:24211` | `nNew` vs `newMax` | Today `newcnt` task + `nums` table; Lean Today shows no counter → **HID** |

### 1.3 Sat family

| Function | Callers | Feeds | Hook | Status |
|---|---|---|---|---|
| `satV2PlanCalc` (66 lines) | `pb2Calc:32443` · `pb2Filled:32827` · `satV2SaveSlot` · `ln4PillsHtml` · `satV3PlanAcctCalc:26094` | **already RE1**: it calls `Re1Adapter.sizeSat`; legacy residue = `sat7dAcctBase` (broker opts, `cap`, `nNew`), `ps1Min*`, `satV3F2c` | Sat form size line · board card · drawer · Place order | **VIS** (RE1 inside) |
| `satV3PlanAcctCalc` (45 lines) | `satV3ReadyAccts` · `satV3SaveSlot` · `satV2SizeLine` · `ln1CardHtml` (dead) · `satV3SaveOffplanAccount` | v2 idea → delegates to `satV2PlanCalc`; **v1 idea → legacy lot/heat/ready** | `data-sat*` ready chips | **VIS for v2 (RE1) · VIS for v1 (legacy)** |
| `sat7dCalc` (33) | `sat7dSaveOrder:24285` (dead) | original 7D lot | — | **DEAD** (no caller anywhere live) |
| `sat7dAcctBase` (15) | `tdBuild` · `satV2PlanCalc` · `satV3PlanAcctCalc` · `satV3AcctMetaHtml` · `ln2FormLine` · `satPyrCalc` · `pfHasTrend` | Sat pool `cap` (= `poolsOf.sat`), `rpt`, `heatMax`, `nNew`, broker book `B`, `openRisk` | `bs.heatPct`/`nNew` only in dead/Lean-off branches; `bs.B` / `bs.trades` used by v2 | **VIS (as plumbing)** — the number-bearing fields (`riskTHB`, `heatPct`, `rpt`) are legacy-only |
| `satPyrCalc` (52) + `satPyrOpen/Refresh/Save/El/Read` | `satPyrOpen` ← `lfHeldIdeaRow`/`satV3PlanRowsHtml` (dead lists) | Sat pyramid add | `data-pyr*` | **DEAD** (never hit) |
| `satV2Money` | `lfHeldRowHtml`, `ln3PlanRowHtml`, `poolsPortHtml`… | Sat Open-risk cards | — | Lean branches use constant zeros (`R = {sat:0…}`) → **HID** |

### 1.4 DD1, core helpers

| Function | State |
|---|---|
| `ddEval`, `ddSync`, `settings.ddState` | **gone** — only comments remain (`14022-14024`, `10023`, `10025`, `15393`, `15432`, `18454`, `26974`). Nothing to remove but the comments. `ddCfgFix` (9 lines, `14029`) still runs and stamps `ddReduce/ddPause/ddPauseWeeks/ddRecoverR` onto `coreRiskCfg` and `satRiskCfg` → no reader → **HID**, delete with `ddStep` |
| `coreSizeOpts` (19) | builds the `opts` bag read by `coreBase` → `cx.opts`; every reader of `cx.opts.*` is in the legacy first-lot / add / ladder / tier code (`coreFirstLotCalc`, `lfAddCalc`, `coreSimCalc`, `coreView:emergencyPct`, `coreTiEval`) → **HID** (feeds only HID/DEAD) |
| `poolsOf` (18) | **VIS** — see 1.1; it is *allocation*, not sizing (see §5 decisions) |
| `coreAcctRisk` (20) | **VIS** — Port `data-ln3-risk`; Today `l2` task dead. RE1 equivalent: partial (§2) |
| `coreSimCalc` (20), `lfAddCalc` (49), `ps1AddCalc` (31) | legacy add-on for non-PS1 cards: **DEAD** · `ps1AddCalc` is the RE1 add-on (kept; it is already RE1) |
| `coreNewInL` (35), `coreLBuyIn` (17) | Compounder-ladder (strategy `L`) new / buy forms: `coreNewInL` reached only from `coreNewIn` when the form is in `L` mode (the form no longer offers it); `coreLBuyIn` only from dead `coreLBuyOpen` → **DEAD** |

### 1.5 What does NOT use the legacy numbers (so cannot regress)

Today rows · Plan board cards · drawer · Place-order sheet · plan sheet (`lr3Sheet`) · PosView figures — all read `re1L` / `Re1Adapter.size*` / `PosView.calc`. Probe: on those screens no legacy `data-c-*`, `data-lf-*`, `data-ln1-*`, `data-ln2-*`, `data-sat*` hook is visible. The only legacy-fed pixels left are on **Port** (pool line and "Core risk" fold — both `<details>`, closed by default: probe found the nodes in the DOM with empty visible text until opened), **Settings** (pool hint), and the position-health dots / tasks on **Today**. The old account summary (`render()` at `17303`: "ถ้าทุกไม้โดน Stop", `data-sum-vs`, `data-lf-drop`) is not on any tab (probe: 0 nodes, 0 text matches on Today / Plan / Flow / Watch / Journal / Port).

---

## 2. Visible outputs → RE1 equivalent

| # | Visible output (where) | Legacy source | RE1 equivalent | Verdict |
|---|---|---|---|---|
| V1 | Port › "to SL now x% · full y%" (`data-ln3-risk`) | `coreAcctRisk` (`layer2`) | exposure at current stops: `Re1Adapter.live().ideas[i]` via `R.ideaResult(...).exposure` · whole-account Momentum usage `L.mom.chk.usageWeek / weekCap` · Compounder `L.comp.heat.{money,pct}` | **Replaceable** (different base: % of equity, and reservations differ — see §4 row 7) |
| V2 | Port › "Compounder x% of pool" | `cx.split.lPct` (`poolFree`) | `L.comp.heat.pct` is % of equity heat, **not** pool fill | **No exact RE1 equivalent** (pool fill is allocation) → decision D1 |
| V3 | Port › "free cash Momentum ฿ · Compounder ฿" | `cx.split.cashFree / lCashFree` | none (RE1 has no cash book) | **No RE1 equivalent** → D1 |
| V4 | Port pool lines / bars (`data-pool-*`) | `poolStats` ← `poolsOf` ← `poolSplit` | none (pool split is the account's capital allocation, `settings.pools`) | **No RE1 equivalent** → D1 |
| V5 | Settings › pool hint (`#poolHint`) | `poolSplit` | none | → D1 |
| V6 | Today › Sell-all / stale price / green dots (`td3-dot`) | `CoreSize.status` (EMA10 / 40W EMA vs close) | none (RE1 has no price-state) | **No RE1 equivalent** → D2 |
| V7 | Plan board / drawer / sheet size, risk, room, chips | **already RE1** (`re1CardModel`, `sizeMomentum/Comp/Sat`, `pb2Calc`→`satV2PlanCalc`) | — | nothing to do |
| V8 | Sat v1 ready accounts / lot / warns (old ideas) | `satV3PlanAcctCalc` v1 branch → `Calc.satLot` / `Calc.heat` / `Calc.readiness` | `Re1Adapter.sizeSat` (what v2 already uses) | **Replaceable** — but changes numbers (§4 rows 5–6) and needs old-idea migration → D3 |
| V9 | Today `heat Sat` / `ชั้น 2 Core` / `ไม้ใหม่ Sat` tasks | `sat7dAcctBase`, `coreL2Level` | RE1 week/month budget check (`satBudL`) already blocks; no task exists | **DEAD** (never fire) |
| V10 | Equity base used by `lr3Base`, `ps1E`, `posView` | `poolsOf.total` as fallback when `L.basis.weekEquity` missing | `L.basis.weekEquity` | **Replaceable** (keep fallback = "not sized", not pool total) → D4 |

---

## 3. Wrong-side / order checks (where each lives)

| # | Check | Place | Notes |
|---|---|---|---|
| W1 | **Engine** `satEntryOrder` — Entry/SL/TP order + R:R ≥ 1.5, TP mandatory (`SAT_BAD_ORDER`, `SAT_RR`, `PRICE_MISSING`) | `risk-engine.js:397`; inline copy `index.html:7165`; callers `satCheck` (`7239`), `sizeSat` (`8085`), adapter copy (`7442`, `7805`) | the authority |
| W2 | **Engine** `sizeOrder` — `STOP_WRONG_SIDE` (stop on the wrong side of entry, both directions) | `risk-engine.js:280` (inline `7048`); message table `6813` | authority for sizing; Momentum / Compounder / Sat all pass through it |
| W3 | `pb2Model` — Sat board / form: wrong side (SL **or** TP), R:R < `SAT_RR_MIN`, missing fields, Trend | `index.html:32392`; callers `bdItems:30938`, `pb2Refresh:32544`, `pb2PlaceOpen:32767` | **duplicate** of W1 (own `wrong` + `satRrCheck`) |
| W4 | `sdWrongOf` — text + one-tap flip | `index.html:32410`; callers `bdItems:30940`, `pvSatBlockOf:31034`, `sdFlip`, `pb2Key`, `pb2Save`, `pb2SaveDo`, `pb2PlaceOpen`, `sdBanner`, `pb2PlaceHtml`, `pb2PlaceYes` | **duplicate** of W1 (re-derives `slBad` / `tpBad`); owns the *wording* and the flip |
| W5 | `satRrCheck` / `satRrFmt` (`SAT_RR_MIN`) | `25476…` | duplicate of the R:R half of W1 |
| W6 | `sat7dSideOk`, `satV3SideOf`, `satV2PlanCalc` `side` | `24218`, `26093`, `26662` | v1 + v2 side test (`s<e` / `s>e`) feeding `readiness` / `ready`; v2 also passes the engine's `STOP_WRONG_SIDE` |
| W7 | `Calc.mrCheck` (MR level side), `Calc.readiness` (`SL ผิดฝั่ง`) | `23481`, `23516` | legacy v1 / MR |
| W8 | Core form: `coreNewInL` ("Entry must be above Stop" `16816`), `coreNewIn` PS1 (`ENTRY_NOT_ABOVE_STOP` `16653/16680`, `LEVEL_BELOW_SL`), `coreFirstLotHtml:14863/14886`, `coreSimCalc:15010`, `lfAddCalc:15740`, `ps1AddCalc:15781`, `coreBuyAddOpen:16966/17022`, `coreLBuyIn:17079` | long-only checks (`px > stop`) — Core has no shorts | each re-implements `entry > stop`; only the PS1 path ends in the engine (`STOP_WRONG_SIDE` is in the `inputErr` list `16693`) |
| W9 | Journal / manual trade form (`22540/22541/22752/22753`) | Long/Short SL side on a *closed* trade | not sizing — leave |

Proposed single helper (Phase B): `wrongSideOf({side, entry, stop, tp})` built on `RiskEngine.satEntryOrder` + `STOP_WRONG_SIDE`; returns `{code, which: 'SL'|'TP', text}`. `pb2Model`, `sdWrongOf`, the Core form and `ps1AddCalc` call it; `sdWrongOf` keeps only the flip button text.

---

## 4. Legacy vs RE1 on the fixture (same plan, both numbers)

Money columns in ฿ (fx 33). "Base" = what the % is a % of.

| # | Plan | Legacy | RE1 | Match? |
|---|---|---|---|---|
| 1 | **Momentum** plan NVDA2 US 120 / 110, no thesis (homework 50 %) | **119 sh** · risk $1,190 = ฿39,270 · 1.00 % of Momentum pool ฿3,929,000 (`coreFirstLotCalc`, tier B) | **34 sh** · ฿11,220 · eff 0.225 % of ฿5.0 M (`0.45 % × homework 50 %`) | **MISMATCH** (×3.5; different base and a 50 % homework cut RE1 has and legacy doesn't) |
| 2 | **Compounder pilot** CMP US 120 / 110 | **71 sh** · $710 = ฿23,430 · 0.99 % of Compounder pool ฿2,357,400 | **75 sh** · ฿24,750 · pilot 0.50 % of ฿5.0 M | **MISMATCH** (71 vs 75 — near-equal by coincidence of the two bases) |
| 3 | **Momentum add-on** (AAPL held, add at 210 / SL 200) | **2 sh** · newRisk $20 · budget 1.00 % · tag `normal` (50 %-of-previous-lot rule + per-stock cap) | **24 sh** · ฿7,920 · eff 0.159 % · **blocked `ADDON_THESIS`** (needs thesis) | **MISMATCH** + different gate |
| 4 | **Compounder add-on** (MSFT add at 400 / SL 390) | **64 sh** · $640 · max 0.958 % · tag `stock_capped` | **27 sh** · ฿8,910 · add-on 0.50 % · **blocked `ADDON_THESIS`** | **MISMATCH** + different gate |
| 5 | **Sat, lot product** XAUUSD Long 2642 / SL 2628 / TP 2684 (dist 14, contract 100, step 0.01) | v1 path (`satV3PlanAcctCalc`): **0.21 lot** · risk $297.65 (= 1.25 % × 50 % first-leg split × Sat pool ฿1,571,600) · heat 0.62 % of Sat pool. (`sat7dCalc` direct = **0.42 lot**, dead) | v2 path (`sizeSat`): **0.21 lot** · ฿9,702 = $294 · step 1 = 0.20 % of ฿5.0 M | **SAME lot, DIFFERENT base** (1.25 %×50 % of pool ฿19,645 vs 0.20 % of equity ฿10,000 — equal here by rounding luck; 0.42 vs 0.21 for the dead `sat7dCalc`) |
| 6 | **Sat, %-loss product** BTCUSD Long 60000 / SL 58800 / TP 63600 (stop 2 %) | v1: **0.2480 BTC** · $297.65 | v2: **0.2525 BTC** · ฿9,999 · 0.20 % of ฿5.0 M | **MISMATCH** (1.8 %) |
| 7 | **Port "to SL now" / "full"** (all open + planned) | `layer2THB` 0 (stops ≥ cost) · "full" counts only reserved ladder levels · `vsCost` ฿−5,940 | `L.mom.chk`: open 0 · reserved ฿16,500 · week used ฿17,500 of cap ฿90,000 · Compounder heat ฿4,950 = 0.099 % | **Different definition**: both say open risk 0; legacy "full" ignores Momentum working orders RE1 reserves |
| 8 | **Account base** | `poolsOf.total` ฿7,858,000 (Core capital ฿ + Sat $×fx) | `L.basis.weekEquity` ฿5,000,000 (snapshot) | **MISMATCH** (fixture's capital field ≠ snapshot; RE1 is the one the board prints; `lr3Base` already prefers RE1) |
| 9 | Sat weekly budget | `sat7dAcctBase`: `rpt` 1.25 % → `riskTHB` ฿19,645, `heatMax` 6 %, `newMax` | `L.sat.budget.weekCap` ฿60,000 (1.2 % of ฿5.0 M) · Step 1 | **MISMATCH** (different caps; legacy ones are no longer enforced anywhere live) |

Flagged mismatches that need a decision before Phase B: **1, 2, 3, 4, 6, 7, 8, 9** (5 is a coincidence, not agreement). None of 1–4 is *on screen* today (those screens already show the RE1 number — rows are legacy-only), so deleting the legacy side changes no visible Today / Plan / drawer / sheet figure. Rows 7–8 change Port.

---

## 5. Proposed removal list (3 buckets)

Counts are from `index.html` (spans of top-level declarations); `core-size.js` is 560 lines and has an inline copy in `index.html` (the `sync_core_size` tool keeps them identical).

### Bucket 1 — DEAD (safe to delete)
Proven by the coverage run (§6: zero hits across the core suites) **and** no live referrer in the name graph. Phase B re-greps each name before deleting.

**292 functions, 3121 lines** never called by any core suite and with no live path (full list, `name · line · length`):

Families: Core legacy card / ladder / add-on / tier / delete UI (`core*`, `lf*`, `cs*`) · Sat v1 editor, plan lists, pyramid, `sat7d*` (`satV3*`, `satV2*`, `satPyr*`, `sat7d*`, `ln1*`, `ln2*`, `pf*`).

<details><summary>List</summary>

`coreOpenCard` 11839 (8) · `coreRiskDefaultMarket` 13980 (5) · `coreErrText` 14444 (4) · `coreDelete` 14551 (5) · `coreNewId` 14556 (1) · `coreLastFriday` 14561 (9) · `coreLadderBudgetTHB` 14750 (5) · `coreCanPlace` 14824 (18) · `coreGatesHtml` 14842 (4) · `coreFirstLotHtml` 14859 (22) · `coreSimCalc` 15006 (20) · `coreSimHtml` 15026 (14) · `coreSimIn` 15040 (8) · `coreAccts` 15048 (2) · `coreLoadOpen` 15052 (4) · `coreSaveOpen` 15056 (2) · `coreCardEl` 15059 (1) · `coreSetOpen` 15060 (7) · `coreToggle` 15067 (1) · `coreExpand` 15068 (1) · `coreAll` 15069 (4) · `coreSimToggle` 15073 (8) · `coreMenuToggle` 15081 (21) · `coreMoneyDual` 15102 (1) · `coreLotBadge` 15106 (6) · `coreAddBlockReason` 15112 (13) · `coreLadderTableHtml` 15145 (13) · `coreLadderRows` 15158 (7) · `coreLadderTot` 15165 (2) · `coreLCardHtml` 15167 (68) · `coreClosedHtml` 15317 (8) · `coreIsClosedCard` 15325 (4) · `coreDelClosedAsk` 15329 (7) · `coreClosedFlagTrade` 15336 (5) · `coreDeleteClosed` 15341 (10) · `coreAcctHtml` 15351 (43) · `lfCoreSetAcc` 15403 (5) · `lfCoreEnsureAcc` 15408 (6) · `lfPortSet` 15477 (1) · `lfCoreLegacyRowsHtml` 15496 (5) · `coreLadderTrackWords` 15551 (3) · `coreOpenCardOfTrade` 15615 (11) · `coreLinkAsk` 15626 (11) · `coreLinkGo` 15637 (6) · `coreCloseCardOfTrade` 15643 (17) · `coreStopHistOpen` 15660 (9) · `lfAddPrev` 15723 (4) · `lfAddCalc` 15727 (49) · `ps1AddCalc` 15776 (31) · `lfAddOpen` 15816 (20) · `lfAddLayer` 15836 (8) · `lfAddSl` 15844 (1) · `lfAddRisk` 15845 (1) · `lfAddRead` 15846 (5) · `lfAddIn` 15851 (29) · `lfAddSave` 15880 (38) · `lfStopLayer` 15930 (6) · `lfStopIn` 15936 (15) · `lfStopSave` 15951 (18) · `coreEmgOpen` 15969 (9) · `coreLotsOpen` 15978 (16) · `coreToggleReason` 15994 (1) · `coreGoto` 15996 (8) · `coreIsFortress` 16030 (1) · `coreLensTxt` 16033 (3) · `coreThVal` 16079 (6) · `coreTiTicker` 16096 (6) · `coreTiG5Paint` 16132 (3) · `coreTiG5` 16135 (6) · `coreTiTkPaint` 16141 (3) · `coreTiTk` 16144 (7) · `coreTiFillTh` 16151 (20) · `coreTiPick` 16171 (2) · `coreTiAcct` 16173 (6) · `coreTiEval` 16179 (18) · `coreTiWhy` 16197 (24) · `coreTiShow` 16221 (18) · `coreTiIn` 16239 (4) · `coreTiLoadWl` 16259 (10) · `coreTierOnlyOk` 16269 (3) · `coreTierNote` 16272 (6) · `coreTierOnlySave` 16278 (16) · `lfTierShow` 16297 (25) · `lfFirstLine` 16322 (11) · `csReasonIds` 16333 (1) · `csSummaryHtml` 16334 (15) · `coreNewF` 16452 (1) · `coreNewRisk` 16453 (1) · `coreNewShowAll` 16488 (1) · `coreNewBud` 16489 (1) · `coreNewLvIn` 16495 (1) · `coreNewLvAdd` 16496 (1) · `coreNewLvDel` 16497 (2) · `coreNewLdraft` 16507 (6) · `coreNewInL` 16837 (35) · `coreLEditOpen` 16935 (6) · `coreBuyAddOpen` 16999 (14) · `coreBuyAddRead` 17013 (5) · `coreBuyAddIn` 17018 (14) · `coreBuyAddSave` 17032 (21) · `coreLBuyOpen` 17053 (17) · `coreLBuyRead` 17070 (5) · `coreLBuyIn` 17075 (17) · `coreLBuySave` 17092 (26) · `coreLCancelOpen` 17118 (12) · `coreLCancelIn` 17130 (6) · `coreLCancelSave` 17136 (11) · `coreStopIn` 17159 (21) · `coreStopPreview` 17180 (8) · `coreStopSave` 17188 (19) · `corePxOpen` 17207 (18) · `corePxAutoAsk` 17225 (10) · `corePxAutoGo` 17235 (6) · `corePxIn` 17241 (13) · `corePxSave` 17254 (12) · `coreTierOpen` 17266 (10) · `coreTierIn` 17276 (10) · `coreTierSave` 17286 (9) · `coreDelAsk` 17295 (6) · `coreDelGo` 17301 (2) · `csStarTxt` 19667 (1) · `csMoney` 19668 (1) · `csLbl` 19669 (1) · `csChipHtml` 19670 (1) · `csEvalOf` 19671 (1) · `csFundTxt` 19672 (1) · `csLine` 19673 (1) · `csEvalRowHtml` 19674 (4) · `csEvalWrite` 19678 (5) · `csAfter` 19683 (10) · `csUsedOther` 19778 (28) · `csAddRisk` 19807 (6) · `csPlanState` 19813 (14) · `csSnap` 19827 (5) · `satV2Split` 23320 (1) · `sat7dErrText` 23985 (1) · `sat7dBrokers` 24066 (1) · `sat7dNum` 24116 (5) · `sat7dHasAnyBroker` 24160 (2) · `sat7dSideOk` 24218 (5) · `sat7dChecksOk` 24223 (4) · `sat7dWeekOf` 24227 (1) · `sat7dIdeaFlags` 24228 (1) · `sat7dCalc` 24229 (33) · `sat7dNew` 24262 (11) · `sat7dSlotWrite` 24273 (9) · `sat7dSaveOrder` 24282 (33) · `sat7dMarkOpen` 24315 (16) · `sat7dCancelSlot` 24331 (14) · `sat7dSinceApply` 24345 (13) · `sat7dSinceChanged` 24358 (1) · `sat7dSinceToday` 24359 (2) · `sat7dBrokerOpen` 24489 (11) · `sat7dBrokerSave` 24500 (87) · `sat7dMoney` 24587 (3) · `satV3WhyValue` 24785 (6) · `satV3SupportDisplay` 24791 (8) · `satV3ResistanceDisplay` 24799 (4) · `satV3LevelChipsHtml` 24803 (9) · `satV3TileBadgeSub` 24813 (6) · `satV3TileDotsHtml` 24819 (7) · `satV3TileHead` 24826 (4) · `satV3TileModel` 24830 (6) · `satV3Pick` 24836 (7) · `satV3CycleFactor` 24843 (8) · `satV3ToggleNote` 24851 (5) · `satV3CopyPrev` 24856 (5) · `satV3MacroBlockHtml` 24866 (19) · `satV3EditorHtml` 24885 (40) · `lfSatSet` 24943 (1) · `lfSatPick` 24944 (1) · `satV3AcctMetaHtml` 25054 (23) · `satV3ConfigStop` 25245 (6) · `satV3ConfigWrite` 25260 (7) · `satV3SetupAdd` 25267 (5) · `satV3SetupRename` 25272 (4) · `satV3SetupRemove` 25276 (6) · `satV3PlanDraftFor` 25282 (4) · `satV3CondLive` 25302 (1) · `satV3CondCancelled` 25303 (2) · `satV3CondSaved` 25305 (2) · `satV3IsHeldCross` 25317 (6) · `satV3CarryBlockMsg` 25328 (1) · `satV3CarryBannerHtml` 25329 (10) · `satV3CarryConfirm` 25339 (12) · `satV3CarryDrop` 25351 (13) · `satV3MrTagHtml` 25401 (2) · `satV3MrLevels` 25403 (5) · `satV3MrAdd` 25408 (8) · `satV3MrLevelSet` 25416 (6) · `satV3MrLevelChipsHtml` 25422 (8) · `satV3MrLineHtml` 25430 (8) · `satV3TpFar` 25449 (7) · `satV3TpPlanHtml` 25486 (12) · `satV3TpNear` 25498 (7) · `satV3CondAdd` 25514 (8) · `satV3CondEdit` 25522 (16) · `satV3CondRemove` 25538 (6) · `satV3CondCancel` 25544 (15) · `satV3CondActivate` 25559 (33) · `satV3PlanHasCond` 25826 (2) · `satV3PlanSave` 25828 (7) · `satV3PlanToggleOpen` 25835 (12) · `satV3WaitEditCond` 25847 (7) · `satV3PlanClose` 25854 (6) · `satV3ActiveEditToggle` 25860 (4) · `satV3OthersToggle` 25864 (4) · `satV3CancelledToggle` 25868 (8) · `satV3CondTplEditorClose` 25876 (3) · `satV3NumTxt` 25879 (2) · `satV3CondMeta` 25881 (5) · `satV3CondTextHtml` 25886 (4) · `satV3CondNumsHtml` 25890 (9) · `satV3ShortRowHtml` 25899 (10) · `satV3CancelledBlockHtml` 25909 (8) · `satV3MacroNoteSet` 25941 (5) · `satV3DriverSet` 25946 (5) · `satV3SizeSwitch` 25951 (5) · `satV3F2cHtml` 25956 (28) · `satV3ActiveBlockHtml` 25988 (27) · `satV3CondListHtml` 26015 (28) · `satV3WaitRowHtml` 26043 (11) · `satV3PlanSetupToggle` 26061 (9) · `satV3IdeaDelete` 26070 (7) · `satV3SetupPassRatio` 26077 (4) · `satV3SetupsReady` 26081 (7) · `satV3SetupLabel` 26088 (5) · `satV3SkipToggle` 26148 (15) · `satV3SaveSlot` 26163 (47) · `satV3SaveReadyAccounts` 26210 (9) · `satV3SaveOffplanAccount` 26219 (8) · `satV3ShouldAutoClose` 26242 (15) · `satV3MaybeAutoClose` 26257 (7) · `satV3ClosedDelAsk` 26291 (8) · `satV3ClosedDelClose` 26299 (1) · `satV3ClosedDelGo` 26300 (4) · `satV3RowMarkOpenAll` 26304 (4) · `satV3RowCancelAll` 26308 (6) · `satV3F2cTradeLine` 26322 (20) · `satPyrAcctOf` 26349 (2) · `satPyrTagHtml` 26360 (5) · `satPyrIdea` 26370 (4) · `satPyrCfg` 26383 (8) · `satPyrRiskAt` 26391 (6) · `satPyrCheck` 26397 (19) · `satPyrCalc` 26416 (52) · `satPyrEl` 26469 (1) · `satPyrOpen` 26471 (27) · `satPyrRead` 26498 (5) · `satPyrRefresh` 26503 (16) · `satPyrSave` 26519 (34) · `satPyrSiblings` 26553 (4) · `satPyrSibling` 26557 (2) · `satV3MrRowLine` 26559 (8) · `satV2MainPos` 26595 (9) · `satV2HeaderHtml` 26604 (21) · `satV2TileHtml` 26625 (19) · `pfTfNorm` 26648 (2) · `pfClsKey` 26652 (3) · `pfClassifyText` 26658 (1) · `pfClassifyCls` 26659 (1) · `satV2SaveSlot` 26728 (39) · `satV2Edit` 26782 (5) · `satV2SetSleeve` 26791 (8) · `satV2SetupToggle` 26799 (7) · `satV2SizeLine` 26809 (31) · `satV2CardHtml` 26840 (48) · `ln1SetMode` 26896 (10) · `ln2FormLine` 26981 (27) · `ln1AcctStatus` 27008 (17) · `pfAssessHtml` 27036 (15) · `pfRrParts` 27051 (16) · `pfRrHtml` 27067 (4) · `pfRrHintText` 27071 (7) · `pfRrLive` 27078 (10) · `pfTrendSet` 27088 (1) · `pfVerifySet` 27089 (7) · `pfZoneTxt` 27096 (1) · `pfSetupCk` 27097 (6) · `lfHeldToggle` 27142 (5) · `lfTradeMenu` 27147 (9) · `lfHeldRowHtml` 27170 (26) · `lfHeldIdeaRow` 27196 (16) · `lfHeldOrphanRow` 27212 (5) · `ln1CardHtml` 27240 (66) · `satV3PlanRowsHtml` 27306 (45) · `satV3DraftCardHtml` 27378 (49) · `satV3SetupEditorOpen` 27428 (1) · `satV3SetupEditorClose` 27429 (1) · `satV3SetupAddConfirm` 27430 (7) · `satV3SetupRenameCommit` 27437 (8) · `satV3SetupEditorHtml` 27445 (32)

</details>

Also dead: `CoreSize.addLot / ladder / ladderBudget / applyStopMove / portfolioSplit / ladderShare / accountDrop / openGate / canPlaceLadder / classifyTier / ddStep`, `Calc.satLot / pctLoss / readiness / mrCheck` (cold in every suite), `ps1AddCalc` (only caller is dead `lfAddCalc`; the live RE1 add-on goes through `re1CardModel` / `bdAddon`), the DD comments, and the inline copy of those methods in `index.html` + `core-size.js` bodies + their cases in `tests/core_size_test.js`.

**Caveat:** names whose only callers are cold are listed even when a regexp-level referrer exists. A few (`coreStopOpen`, `coreBuyAddOpen`, `coreBuy1Open`, `coreStopSave`, `coreNewSave`) are also reached from live board buttons — they are cold in the list only if no suite pressed them; Phase B must keep any whose live caller (`bdAddon`, `ln4RaiseStop`, `ln4RecordFill`) still needs them (check `coreBuyAddOpen` before deleting: `bdAddon` calls it).

### Bucket 2 — Visible, replaceable by RE1

| Item | Replace with | Screen |
|---|---|---|
| `satV3PlanAcctCalc` v1 branch (`Calc.satLot`/`Calc.heat`/`Calc.readiness`, `sat7dBrokerOpts` use stays) | `satV2PlanCalc` / `Re1Adapter.sizeSat` for every idea (needs v1-idea migration rule, D3) | Today ready accounts, Sat save slot, size line (old ideas only) |
| `coreAcctRisk` + `coreLayer2` + `coreL2Positions` (+ `CoreSize.layer2`, `vsCost`) | V1 mapping above (`L.mom` usage + `L.comp.heat` + exposure at stops) | Port "to SL now / full" |
| `sat7dAcctBase` number fields (`riskTHB`, `heatPct`, `rpt`, `heatMax`, `nNew`, `newMax`, `ddFactor`), `satRiskCfg` rpt/heat/new keys | RE1 `L.sat.budget` / `RP.sat` (policy) | none visible (v2 uses only `cap`, `B`, `trades`) |
| `poolsOf.total` as an equity fallback (`ps1E`, `lr3Base`, `posView`) | `L.basis.weekEquity`; no snapshot = "not sized" (RE1 already says so) | Plan sheet / drawer |
| W3 / W4 / W8 wrong-side copies | one helper on `satEntryOrder` / `STOP_WRONG_SIDE` (§3) | Sat form, board, Today, sheet, Core form |
| `coreSizeOpts` / `cx.opts` consumers | delete with their only readers (all in bucket 1 once the legacy forms go); `emergencyPct` read by `coreView` is **HID** | none |

### Bucket 3 — Needs a decision (no RE1 equivalent)

| ID | Item | Why RE1 can't replace it | Options |
|---|---|---|---|
| **D1** | **Pool split** `poolsOf` / `CoreSize.poolSplit` / `poolFree`, Settings pools %, Port pool lines + "free cash", `poolStats`, `coreLadders` (held / reserved per ladder) | It is capital *allocation* (Core vs Sat, Momentum / Compounder / Sat %), not risk sizing. RE1 sizes from equity snapshot and has no cash book. | (a) keep as a read-only "allocation" helper, no sizing use; (b) retire Port pool lines. Recommend (a): keep `poolSplit`/`poolFree` + tests, delete everything else |
| **D2** | **Position-health state** `CoreSize.status` (+ EMA10 / 40W EMA fields on cards, Today sell/stale/green tasks, `td3-dot`) and `emergencyStop` price | Price-vs-stop/EMA state is a *signal*, not size/risk. RE1 has no price state. | keep `status` (stays tested); delete `emergencyStop` (computed on every card draw, never shown) |
| **D3** | **Old (v1) Sat ideas**: `idea.v2` falsy docs still size through the legacy lot/heat | RE1 `sizeSat` could size them but numbers change (§4 row 5/6) and v1 ideas carry `checks`/`invalidation` readiness rules RE1 doesn't have | (a) read-only: show old ideas, no size/ready; (b) migrate on load (`v2:true`); (c) leave the v1 branch. Recommend (a) |
| **D4** | **Equity fallback** when no confirmed snapshot (`poolsOf.total`) | RE1 refuses to size without a snapshot (`NO_SNAPSHOT`); legacy sizes from capital | accept RE1's refusal everywhere (recommended) vs keep a labelled "capital-based" fallback |
| **D5** | **Stored fields** (`settings.coreRisk.*`, `settings.satRisk.*`, `ddReduce/ddPause/ddPauseWeeks/ddRecoverR`, `coreRisk.tier*`, `satV2.*`, card `cs.baseRiskPct`, `plan.risk`, `ln4.snap`) | Read-only after Phase B per the brief ("old docs must still load") | confirm: keep readers only for load/migration + export, no writers |
| **D6** | **`core-size.js` + inline copy + `sync_core_size.py` + `tests/core_size_test.js`** | After bucket 1/2 only `poolSplit`, `poolFree`, `status` (+ their tests) survive | shrink the module to those three (and its inline copy) vs move them into `pos-view.js`/`risk-engine.js` |

---

## 6. Coverage run (dead-evidence)

Instrumented scratch copy of `index.html` (every legacy-family function + `Calc.*` / `CoreSize.*` / `Ps1.*` reports its first call over a local WebSocket), run with `bash tests/run_regression.sh --quick`: **673 instrumented names, 304 called, 292 legacy-family functions never called** (3121 lines).

Called (so live): `CoreSize.{firstLot, layer2, vsCost, emergencyStop, status, poolSplit, poolFree, tierBadge}`, `Calc.{heat, newCount}`, `poolsOf`, `coreSizeOpts`, `coreCtx/coreBase/coreView`, `coreFirstLotCalc`, `coreAcctRisk`, `sat7dAcctBase`, `satV3PlanAcctCalc`, `satV2PlanCalc`, `ddCfgFix`. Never called: `sat7dCalc`, `satPyrCalc`, `coreSimCalc`, `lfAddCalc`, `ps1AddCalc`, `coreNewInL`, `coreLBuyIn`, `render`, `renderCorePanel`, `coreAcctHtml`, `coreEmgOpen`, `Calc.satLot / pctLoss / readiness / mrCheck`.

Caveats: the quick set is 17 browser suites; in the instrumented copy 11 of 30 items FAIL (aw1, pv1, re1d, re1c, re1c2, re1b, ts1, ts1b, phase364/372/370). I did not compare with an uninstrumented run (RE1-D summary records many suites already failing on main), so a failure caused by the instrumentation is not ruled out; hits are still valid (they come from page loads that ran). Hit names are first-call only. Not covered: hand-driven flows (legacy-mode flag `dash.ln1Legacy`, Sat v1 old-idea docs, strategy-`L` forms).

Also seen: `ddCfgFix` is called (it stamps `ddReduce/ddPause/ddPauseWeeks/ddRecoverR` onto the cfg objects) but nothing reads those fields except `ddStep`, which only the unit test calls.

## 7. Phase B gates (for the follow-up, not done here)

1. Re-run this probe after each deletion batch; the bucket-1 list must stay at zero hits.
2. Hooks superset PASS · `risk_engine` / `re1_adapter` / `re1c_live` / `core_size` (shrunk) / `ps1_size` / `pv1_posview` node suites PASS · `run_regression.sh` 0 failing.
3. Fixture numbers on Today, Plan card, drawer, sheet, Port unchanged except rows 7–8 above, only if the review approves.
4. Report `docs/reports/AU1-summary.md`: lines removed, functions removed, what moved to RE1.
