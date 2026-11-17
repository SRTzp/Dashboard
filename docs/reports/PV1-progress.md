# PV1 progress

## Part A · A0 — reconciliation (BLOCKED: real stored data not available to me)

**What I could check**
- Arithmetic of the brief's reading: filled 11 sh @158, planned 18 @140, stop 110, FX 33.8 → (11×48 + 18×30) × 33.8 = 1,068 × 33.8 = ฿36,098 ≈ ฿36.1k; shares 11 + 18 = 29 → `#29`. Consistent with `tw1SizeRisk` (index.html ~29517), which reads `plan.ps1.qty / riskMoney / riskPct` (whole plan), not `lots`.
- Code path confirms the row is plan-total, not holdings: `re2Row` → `tw1SizeRisk(it)` → `it.ref.plan.ps1`.

**What I could not check**
- The actual stored NVDA card (lots + `plan.ps1` + price/date + FX). Live data is in the browser / Firestore, not in the repo. The newest backup in ~/Downloads (`dashboard-backup-2026-11-01-2012.json`) has no NVDA entry, and `tests/seed.json` has no NVDA Compounder card. A fixture built only from the brief's own numbers would just restate the brief, not verify it.

**Status:** no application code changed. Baseline regression on the base commit was started separately (results in scratchpad `base/`).
Needed to continue: a fresh dashboard backup JSON (taken after the NVDA buy), or the NVDA card's stored `lots`, `plan.ps1`, `px`/`pxDate` and the FX rate from Settings.

## A0 — update after reading `~/Downloads/dashboard-backup-2026-11-17-0905.json` (in place, not copied)
Found in the backup (NVDA only):
- Filled trade `t1794539144994595`: port core, Long, USD, qty 11, entry 158, sl 110 (sl0 110), mult 1, opened 2026-11-13. Matches "11 sh filled @158, stop 110".
- Settings FX: **33.76** (manual, `fxAuto:false`, updated 2026-10-26) — brief used 33.8 (rounded). With 33.76: cost 11×158×33.76 = ฿58,675 (brief ฿58.7k ✓); loss at stop on held 11×48×33.76 = ฿17,825 (brief ฿17.8k ✓).
- Watchlist entry NVDA/US/core added 2026-11-12.
NOT in the backup: the NVDA **core card** (Firestore `users/<uid>/coreCards`: `lots`, `plan.ps1.rows/qty/riskMoney/riskPct`, `px`/`pxDate`). The export contains no card collection at all (0 hits for `ps1`, `lots`, `rows`, `qtyFull`).
So the "18 planned @140", the `#29`, the ฿36.1k plan loss, and the 162.80 price/date are **unverified**. With FX 33.76 the brief's plan loss would be 1,068 × 33.76 = ฿36,056 (still ฿36.1k).
Result: filled side confirmed; planned side and price cannot be reconciled from the backup. Part A code NOT started.
Side finding: the backup/export does not include core cards (plans, lots, prices) — worth a separate look.

## A0 — FINAL reconciliation (stored NVDA card pasted by user · card `ccmwdlk56w91` · trade `t1794539144994595`)
Stored: lots = [11 @158 · 2026-11-13 · stop 110] · plan.ps1.rows = [11 @158, 18 @140] · qty 29 · div (FX) 33.76 · E 5,019,200 · stops [110] · riskMoney 36,055.68 · riskPct 0.71836 · px 162.85 (2026-11-13, auto) · mult f 0.75 (regime) · ln4.placedLv {0} (row 1 placed + filled; row 2 planned only).
Reproduce the displayed Today row (`tw1SizeRisk` → plan.ps1): `#29` = ps1.qty (11+18 all planned rows) · ฿36.1k = riskMoney = (11×(158−110) + 18×(140−110)) × 33.76 = 1,068 × 33.76 = 36,055.68 ✓ · 0.72% = 36,055.68 / 5,019,200 = 0.7184% ✓.
**Brief's reading confirmed**: the row shows the WHOLE PLAN (planned shares + loss at stop if both rows fill), not holdings. Only differences: FX is 33.76 (not 33.8), price is 162.85 (not 162.80).
Honest numbers for this holding (what posView must return): heldQty 11 · plannedQty 29 · avgEntry 158 · cost 11×158×33.76 = ฿58,675 · value 11×162.85×33.76 = ฿60,476 (1.205% of 5,019,200) · uPnl +฿1,802 (+3.07%) · openRisk 11×48×33.76 = ฿17,825 (0.355%) · toStop 11×52.85×33.76 = ฿19,627 · plannedRisk ฿36,056 / 0.718% · R = 48.

## Part A — done (commit 1)
- `pos-view.js` (pure `PosView.calc`, synced into index.html by `tools/sync_pv1.py`, `--check` added to run_regression) + `posView(it)` adapter in index.html (fills = card lots / engine tranches · plan rows = `plan.ps1.rows` · price = card px or Sat manual Last price · FX = Settings · equity = `ps1E` · open risk = engine `ideaResult.exposure`).
- Today row (`tw1SizeRisk` → `pvRowParts`): holding `#11/#29 · ฿60.5k · 1.2% · open risk ฿17.8k` (Sat `0.02/0.05 lot`); planned/ordered `plan #29 · risk ฿36.1k · 0.72%`; no price → `value: no live price`; homework note stays text (`size limited to 50% · homework not done`). Phone: numbers moved to line 2 (symbol no longer wraps).
- Drawer: new POSITION block (same posView). Satellite optional "Last price" (form + drawer), stored `lastPx {v, at}`, display only (test proves pb2Calc unchanged), amber "old price" after 24 h.
- Tests: `node tests/pv1_posview_test.js` (38 pass) · `tests/run_tests_pv1.py` part A (48 pass at 1440/1280/390).
- Baseline (base commit, full run): 34/41 ok, failing = run_tests_phase122, 365, 366, 367, 373, cg1, ht1 (saved list). Note: the baseline run overlapped my first edits (marker block only).

## Part B — done (commit 2)
- Flow "Which asset moves this week · why": cards size independently (`align-items:start`), short text in normal text colour, 3 lines max (also on phone), real `Details ▾` / `Close ▴` button (44 px). One full-width panel (`data-pv-panel`) under the card's row (phone: directly under the opened card); one open at a time.
- Panel (stored data only): full Weekly Impact note + `carryover_th`; every `event_refs` event with time (ICT / date / ongoing), title, forecast / previous / actual, mechanism, scenarios, watch; Quarter view (bias, posture, quarter, confidence, why, change-if, drivers, since); sources + "Weekly Impact as of … ICT"; separate "Your note · this week" (same textarea/save). No Playbook → "No Playbook for X · Add ›" (opens the Playbook panel). No Weekly Impact → existing empty text.
- `tests/run_tests_phase373.py`: the check "Macro card heights equal per row" contradicted the brief (no stretch) → replaced by "cards size independently".
- Tests: run_tests_pv1 parts A+B = 111 pass at 1440/1280/390. Screenshots pv1-flow-open-1440/390.

## Part C — done (commit 3)
- Plan board cards: header (symbol · tag · Long/Short chip · ⚑ Ready / red Blocked / R chip), six always-visible numbers (Planned: Entry · Stop+distance · Target+R:R · Size+value · Loss at stop · To entry; Holding: Held+avg · Price+date · Value+weight · Unrealised P&L · Stop+loss if stopped · Entries+next), `More ▾` (cost+FX line, loss vs entry, price→stop, R definition, whole-plan risk, % pool, size limits, FX source; stays open across re-renders). Waiting (incomplete) plans keep the compact card.
- Blocked plans: red chip replaces ⚑ Ready, "Can't place: <first reason of the sizing result>", button `Fix stop ›` / `Fix size ›`, size/loss "not sized"; Ready cannot be set while blocked; an existing flag is shown off, not deleted. Engine-gated plans keep their size and a disabled Place order with the reason. "Fix risk" / "Risk / size not OK" removed everywhere (Today included). Ready tooltip: "You marked this plan ready to enter."
- Planned size value now needs the contract multiplier (`pos-view.js` gained `plannedValue`).
- Phone Today row: wrap fix so 3-button prompts don't overflow at 360 (re1d regression found by the Part A snapshot run).
- Tests: run_tests_pv1 A+B+C; phase373 'Fix risk ›' expectations → 'Fix size ›'.
