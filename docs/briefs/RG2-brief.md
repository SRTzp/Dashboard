# Brief RG2 — Regime v2 · Journal by bucket · Sector link · Separate pools · Ladder page

Written 30 Oct 2026 (orchestrator chat). Baseline: `main` @ `549f304` (index sha256 `b003f4b511f3…` = CS1, + fundflow 2026-10-30).
Run on the Mac with Claude Code (tests live there). Two rounds: **RG2a = Run 1**, **RG2b = Run 2**. Ladder rules (#21) are **not** in scope.

## 0. Standing rules (apply to both rounds)

- Work on a new branch per round; never push to `main`. Open a PR at the end; do not merge or deploy.
- Backup before editing: `index.backup-pre-RG2a.html` / `index.backup-pre-RG2b.html`.
- `core-size.js` lives on the Mac (not in git). `Calc.coreSize` inside `index.html` is a copy: edit `core-size.js`, then run `python3 tools/sync_core_size.py`; check with `--check`. Run `node tests/core_size_test.js`.
- Old tests: only change **expected values** that this brief changes on purpose; never delete or weaken a case; log every change in `tests/RG2a_retired.md` / `tests/RG2b_retired.md`.
- New tests: `tests/run_tests_phase112.py` (RG2a) and `tests/run_tests_phase113.py` (RG2b). Full suite once at the end of each round; write `docs/reports/<ROUND>-verify.txt` with `tests/make_verify.sh`.
- App UI text: English for new labels (keep existing Thai text unless the brief changes it).
- Mockup rule: every new UI must fit 300 / 320 / 390 / 1280 / 1440 px with no horizontal page scroll.
- Temp files → `_to_delete/`; never `rm`.

## 1. Decisions (final unless marked open)

| # | Decision |
|---|---|
| Regime | Daily timeframe, **raw closes** (TradingView default). **Winner signal = EMA20/50**, **Ladder signal = EMA50/100**, same proxies ACWI/BIL + HYG/IEI. |
| Sizing | Same factor for both pools: both green 100 % · one red 75 % · both red 50 %. Each pool uses its own signal. **No buy bans** (size only). Ladder factor applies when a ladder is placed; sizes are not resized later. |
| #1 | Stale regime data must **not** switch to 100 %: keep the last known factor + red "data X days old" bar. |
| #2 | One-line verdict on Today: label + existing factors, no new rules. |
| #3 | EMA backtest done (branch `claude/ema-backtest`); results in §6. |
| #4 #6 #8 #9 #11 #24 | On hold (Thai regime, RRG source, auto EMA50/RS, auto stars, volatility, file split). |
| #7 | Sector link: yes, + add XLK · XLI · XLY · XLP · XLRE to RRG. |
| #10 | Limits decided (§4.5): drop Layer 2 cap, total cap A/B, Tier A/B, Macro size ×; one per-stock cap 20 % of Winner pool; new Sat trades max 4/week (Main + Tactical). |
| #12 | Stale tags: minimal, only when stale. |
| #13 #14 | Journal by bucket + planned vs actual R: yes. |
| #15 | Port: one always-visible line + collapsed bars. |
| #16 | Remove the Ladder "risk-off only" opening gate. |
| #17 | Winner and Ladder get **separate cash pools**; drop the shared Core tank + 30 % Ladder share completely. Split = % of account, default **50 / 30 / 20** (Winner / Ladder / Sat), editable. First load re-splits the **whole** account 50/30/20 (current Sat ≈ 30 % shrinks to 20 %). Ladder: max **5 % of the account per stock**. |
| #18 | Sat risk = % of the whole Sat pool; remove the Main/Tactical 70/30 sleeve split. Choices Main **0.5 · 0.75 · 1.0 · 1.25 · 1.5 · 2.0** (default 1.5), Tactical **0.25 · 0.5 · 0.75 · 1.0** (default 0.75). Fixed choices (no free box). Contract-value caps converted to keep today's ฿ limits: **Main 1.4× · Tactical 1.2× of the Sat pool** — editable in Settings for later tuning. |
| #19 | Pools per account (option A) + a combined summary. |
| #20 | Ladder page inside Plan: scope switch `Winner | Ladder | Sat`. Watching states: `Base · Sideways-Up · Broken` (no Uptrend — Ladder never buys an uptrend). |
| #21 | Ladder rules: discussion only — **do not implement**. |
| #22 | One data-freshness panel. |
| #23 | Tests moved to git (PR #2). |
| Paused | Portfolio stop-risk / gap settings (0.625 %) — not in RG2. |

## 2. Code anchors (`index.html` @ baseline; line numbers approximate)

- Regime data: `scripts/build_fundflow.py` (`RATIOS`, `FAST/SLOW`, `fetch`); app `FF_RATIOS` (~22832), chip render (~22925, suffix `w`/`d`), `ffJsonData` (~22872), `ffCoreNow` (~22879), `Calc.ffCoreCap` (~17445), `coreFNow` (~9262), `coreFWarn` (~9271), `ffDeployCap` (~17143).
- Ladder / Core math: `Calc.coreSize` (core-size.js; in index ~4080–4590): `DEFAULTS.ladderBudget/ladderRiskCap/ladderShareCap`, `ladder()`, `portfolioSplit()`, `ladderShare()`, `openGate()`, `canPlaceLadder()`, `layer2()`. App side: `CORE_RISK_DEFAULTS` (~8502), `coreBase` / `coreLadderCalc` (~9285) / `coreLadders`, card strategy `c.strategy==='L'`.
- Sat: `SAT_V2_RPTS` (~17240), `SAT_V2_DEF` / `SAT_V2_FIELDS` (~17243), `satV2Errs`, `satV2Cfg` (~17286), `satV2Money` (~17308), `satV2Caps`.
- Settings: `openSettings` (~16795), `saveSettings` (~17025), `set1CheckItems` (~12556).
- Today: `tdHtmlLean` (~7369). Plan scope: `setPlanScope`, header slot `hdrSubSync` (~5261). Port: `ln3RenderPort` (~12691).
- Journal: `journalStats` (~8808). Playbook freshness: `pbStaleInfo` (~23142). Weekly Impact: `wi*` (~23460+). RRG: `RRG_SYMS` (~21988), `sdRowHtml`. Watchlist: `wlAddSave` (~15449), promote form `td4Pro*`.

## 3. RG2a (Run 1)

### 3.1 Regime script — `scripts/build_fundflow.py`
- Prices: `auto_adjust=False` (raw closes) for all ratios. `yf.download(..., threads=False)`; if any symbol is missing, wait 20 s and retry once for the missing symbols only.
- ACWI_BIL and HYG_IEI become daily (`tf:'D'`) with **two pairs**:
  - top level (Winner): `up`, `flip_days`, `prev_week`, `ema:[20,50]`
  - `slow` (Ladder): `{up, flip_days, prev_week, ema:[50,100]}`
- Other ratios keep their current TF and EMA10/20 (only the raw-price change applies). Make EMA lengths per ratio, not global.
- `MIN_BARS` must cover the slow EMA (use ≥ 300 daily bars for the 50/100 pair).
- Add `"ver": 2` and update `method`. Keep the "do not write a partial file" rule.
- Update `--selftest` (two pairs, raw, retry path with a fake fetch).

### 3.2 App regime
- Read `slow` when present; old files without `slow` → Ladder uses the top-level state (log once to console).
- Chip suffix for daily ratios = `d`.
- New helper `ffPoolFactor(pool)` → `'winner' | 'ladder'` → `{cap, red, reds, stale, age}` via `Calc.ffCoreCap`. `ffCoreNow` = winner.
- **Stale fix (#1):** in `ffCoreCap`, `stale:true` must no longer force `cap:100`. Use the cap from the (old) values, keep `stale:true`. Update `coreFWarn` text: `⚠ Regime data is N business days old — size from last known state`.
- **Verdict line (#2)** at the top of Today (lean), one line, tap → Flow regime section:
  - Label from the **Winner** pair: both green `Risk-ON` · ACWI green + HYG red `Caution` · ACWI red + HYG green `Mixed` · both red `Risk-OFF`.
  - Text: `Caution · Winner 75% · Ladder 100%`; stale → append red `· data 3d old`.
  - Must stay one line at 300 px (shorten to `Caution · W 75 · L 100` ≤ 340 px).

### 3.3 Freshness (#12 + #22)
- Tag shown **only when stale**: small grey `9d` next to the item title.

  | Source | Stale when |
  |---|---|
  | Regime (`fundflow.json`) | > 2 business days |
  | Weekly Impact | edition week older than current week |
  | Weekly Stock Summary | > 8 days |
  | Macro Playbook | existing `pbStaleInfo().due` |
  | RRG sectors | cache not from today (keep existing "as of") |

- One panel in Settings › Basics: "Data freshness" — one row per source: dot 🟢/🟡/🔴 + age + source name. No new Today block.

### 3.4 Journal by bucket (#13) + planned vs actual (#14)
- Bucket of a closed trade: Core trade linked to a card with `strategy==='L'` → **Ladder**; other Core → **Winner** (legacy/unlinked = Winner); Sat `sleeve==='tactical'` → **Sat Tactical**; other Sat → **Sat Main**. Find the trade↔card link in code; document it in the report.
- Journal: a bucket filter chip row (`All · Winner · Ladder · Sat Main · Sat Tactical`) + a compact 4-row table: trades · win rate · avg R · total P/L (฿) · max drawdown of that bucket's closed-trade equity curve.
- Per closed trade (detail row): `Planned 1R · target 2.5R → got 1.8R` and `Stop respected ✓/✗` (✗ = loss worse than −1.25 R). Use entry/SL/TP stored on the trade; missing SL → show `—`.

### 3.5 Sector link (#7)
- Add to `RRG_SYMS`: `XLK Technology`, `XLI Industrials`, `XLY Consumer Discretionary`, `XLP Consumer Staples`, `XLRE Real Estate`.
- Watchlist / Candidate field `sector_etf` (`''` · an RRG symbol · `'TH'`). Edit in the Watchlist edit form and the promote form; suggest from `industry` via a small keyword map (e.g. semiconductor → SMH, software → IGV, bank → XLF/KRE); user confirms.
- Watchlist row badge `SMH · Leading` (+ `★` when the sector is followed); grey when Weakening/Lagging; none when empty.
- Sort option `Hot sector first` = Leading/Improving and ★ first.

### 3.6 RG2a tests (phase112)
- Script: two pairs, raw prices, retry, old-file fallback.
- Factor table for both pools (4 combos × 2 pools) + stale keeps the last factor.
- Verdict text at 300 / 390 / 1440, all 4 labels, stale suffix.
- Freshness tags appear only when stale; panel rows.
- Journal bucket mapping (W/L/Main/Tactical + legacy) and R math (win, loss at SL, loss beyond SL, no SL).
- Sector field save/load, badge states, sort order.

## 4. RG2b (Run 2)

### 4.1 Separate pools (#17, #19)
- Per account in Settings › Basics: existing capital amounts stay the source of the account total. New split % `winner / ladder / sat`, default **50 / 30 / 20**, must total 100.
  - Derived: `poolWinner`, `poolLadder`, `poolSat` (฿). Option bucket and Strategic Cash stay outside the split.
  - Migration (first load): total = core + satB; apply **50 / 30 / 20 to the whole total** (Sat shrinks from today's ≈ 30 %). Open positions are untouched; only new trades use the new pools. If existing exposure is above a new limit, show a warning — never close or resize anything. Show a one-time notice to review the split.
- Winner tank = `poolWinner`; Ladder tank = `poolLadder`.
  - Remove the shared tank logic: `portfolioSplit` shared cash, `ladderShare` 30 % cap, `L_SHARE_OVER`, and the open gate (`openGate` / `GATE_*` reasons) from `canPlaceLadder`.
  - Winner free cash = Winner pool − Winner cost. Ladder free cash = Ladder pool − held − reserved (waiting levels).
  - Ladder per-stock budget = **5 % of the account** (setting `ladderMaxAcctPct: 5`; ≈ 16.7 % of a 30 % Ladder pool). `ladderRiskCap` is % of the **Ladder pool**.
  - Winner: **one per-stock cap = 20 % of the Winner pool** (setting, default 20). Remove Tier A/B caps and labels from Core sizing/UI (CS1 ★ already replaced Tier; keep stored keys, ignore them).
  - Remove Settings fields `ladderShare` and `gateWeeks` (keep stored keys, ignore them).
- Sizing factor: Winner sizing × Winner factor (existing path). New ladders: budget × Ladder factor at placement.
- Existing cards: W → Winner pool, L → Ladder pool. Nothing deleted.
- Rename visible `Core` scope to `Winner` where it means the Winner strategy (keep `Core` for the Port bucket name if needed).
- **Prerequisite:** this section changes `Calc.coreSize` (`portfolioSplit`, `ladderShare`, `canPlaceLadder`, `openGate`). `core-size.js` and `tools/sync_core_size.py` must be in the repo first (user uploads them from the Mac). If they are missing when RG2b starts, stop and report — do not edit only the copy inside `index.html`.

### 4.2 Sat risk (#18)
- Remove `mainPct / tacPct` from sizing: Main and Tactical both size from the whole Sat pool.
- `SAT_V2_RPTS` split into Main `[0.5,0.75,1,1.25,1.5,2]` (default 1.5) and Tactical `[0.25,0.5,0.75,1]` (default 0.75). Old saved values outside the list → default + one-time notice.
- Keep today's ฿ limits when the base changes from sleeve to whole pool (user choice A): contract-value caps **Main 2× → 1.4×**, **Tactical 4× → 1.2×**; Tactical brake DD **10 % of Tactical → 3 % of Sat pool**. Migrate saved values the same way (× 0.7 / × 0.3). All stay editable in Settings; label them "of Sat pool".
- New Sat trades per week: **max 4, Main + Tactical counted together** (replace the current per-week count setting with this rule; default 4).
- Remove Macro size multipliers (`macroNeutral`, `macroAgainst`): Sat size no longer shrinks for Neutral / Against Macro. Keep the "against Macro needs a reason" rule if it exists separately.

### 4.3 Ladder page (#20)
- Plan scope switch `Winner | Ladder | Sat` (header slot `hdrSub` and in-page). Mobile keeps two-tap-free buttons (3 short labels must fit 300 px).
- Page:
  1. Header: Ladder pool used (held + reserved) / pool · free cash · chip `Size 100%` / `75%` / `50%`.
  2. Watching: Watchlist items with `ladder_watch:true` (Fortress only); manual trend state select `Base · Sideways-Up · Broken`; optional manual distances to EMA20/50/200.
  3. Active ladders: card per stock — T1/T2/T3 rows (price, amount, status waiting/bought/cancelled), progress dots, avg cost, exit line; mobile tap → sheet.
  4. Closed ladders: short list → Journal (Ladder bucket).
  5. Actions: `+ New ladder` (from Fortress Watchlist), edit zones, mark bought, cancel level.
- Reuse existing `ladder()` / `coreLadderCalc` and level statuses. **No new Ladder rules** (#21 pending).

### 4.4 Port line (#15)
- Always visible: `Winner 48/50 · Ladder 22/30 · Sat 18/20` (actual % of account vs target); amber dot when any pool is > 5 points off.
- Collapsed: bars + ฿ amounts. Per account; `รวม` shows the sum.

### 4.5 Limits (#10) — decided
| Limit | Decision |
|---|---|
| Core risk per trade (★ base) | Keep |
| Per-stock cap | Keep as **one cap: 20 % of Winner pool**; Tier A/B removed |
| Regime factor 100/75/50 | Keep |
| DD brakes (Core, Sat, Tactical) | Keep (Tactical DD converted, §4.2) |
| Layer 2 cap 20 % | **Drop** (remove check + setting; keep stored key) |
| Total cap A/B 25 % | **Drop** |
| Ladder share 30 % · Ladder gate | Removed by §4.1 |
| Sat Open Risk 1.2 % | Keep until the paused 0.625 % stop-risk cap replaces it |
| Open Risk per product 0.6 % | Keep |
| Core + Sat Open Risk 6 % | Keep as a quiet backstop |
| Contract value cap | Keep, converted to 1.4× / 1.2× of Sat pool (§4.2) |
| New Sat trades per week | Max 4, Main + Tactical together |
| Macro size × (Neutral / Against) | **Drop** |

### 4.6 RG2b tests (phase113)
- Split validation (sum 100, each 0–100), migration from old capital, notice once.
- Winner/Ladder free cash independent; placing a ladder never reduces Winner cash and vice versa; no gate reasons; ladder budget = 5 % of account × Ladder factor.
- Winner per-stock cap 20 % of Winner pool; no Tier labels; Layer 2 / total-cap checks gone.
- Sat sizing from whole pool; preset lists; old values → defaults; caps 1.4× / 1.2× and brake 3 % (migrated from 2× / 4× / 10 %); max 4 new Sat trades/week across Main + Tactical; no Macro size ×.
- Migration with an over-limit open position → warning only, nothing changed.
- Ladder page at 300 / 390 / 1440; scope switch in header + mobile.
- Port line + amber threshold.
- Existing ladder/core math byte-identical where the brief does not change it (`core_size_test.js` stays green; new cases for the pool split).

## 5. Out of scope (both rounds)
Ladder rules (#21) · auto EMA50 / RS (#8) · auto stars (#9) · volatility (#11) · Thai regime (#4) · RRG source move (#6) · stop-risk / gap settings · file split.

## 6. Backtest reference (ACWI as proxy, 2008-10 → 2026-10, `claude/ema-backtest`)

| Signal | Flips/yr ACWI · HYG | CAGR (100/75/50 on ACWI) | Max DD | Size changes/yr |
|---|---|---|---|---|
| Weekly EMA10/20 adjusted (old) | 1.4 · 2.1 | 10.1 % | −24.3 % | 3.4 |
| Daily EMA20/50 raw (**Winner**) | 4.4 · 5.4 | 9.1 % | −22.1 % | 8.4 |
| Daily EMA50/100 raw (**Ladder**) | 1.5 · 2.3 | 9.4 % | −24.3 % | 3.3 |
| Buy & hold ACWI | — | 11.8 % | −32.1 % | 0 |

### 6.1 Notes
- Ladder signal is calm (whipsaws in 18 yrs: ACWI 3 · HYG 7, vs Winner 30 · 32).
- Trade-off: it turns red late (2020: ACWI already −21 %) and HYG/IEI on 50/100 stayed red through the 2008 and 2010 recoveries → Ladder would size at 75 % during part of those rebounds.
- Model limits: ACWI index as proxy (not the user's stocks) · 7 major falls only · daily signals read at weekly closes · no costs/taxes.
