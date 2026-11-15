# RE-C1 — cut-over summary · branch `claude/re1c1` (not merged)

## §0 — RE-B follow-up (NVDA, Compounder, holding): qty 7 ≈ 0.25%, reasons HOMEWORK_50 + EQUITY_PROXY
**Cause:** `engineSize` in `re1-adapter.js` treated the Compounder like Momentum: base = Pilot 0.50% **and** `frac = 0.5` (homework not done) → 0.50% × 50% = **0.25%**; the regime factor was never applied.
**Correct arithmetic** (decisions §4): for a Compounder the homework cap is a *phase cap* — "thesis incomplete → Pilot only" — the Pilot (0.50% of the 1% plan) **is** the 50%. It is never a second multiplier. The regime factor applies to NEW entries, `min(Regime, Emergency)`.
`Pilot 0.50% × regime 75% = 0.375%` (one signal red) · × 100% = 0.50% (both green) · Starter ON: × 50% (¼ of the plan). NVDA at 0.375% is 1.5× the dry-run size.
**Fixed** in the adapter/engine path. Results name every factor (`PILOT_0.5`, `REGIME_75`, `EMERGENCY_50`, `STARTER_25`; Momentum `HOMEWORK_50`; Satellite `STEP_n`, `CONDITION_65`). Proof: `re1c_live_test.js` ("Compounder effective % = 0.50 × 0.75 …"), `run_tests_re1c.py` ("WL1 (Compounder): 0.50% Pilot without thesis…", "dry-run Compounder rows never carry HOMEWORK_50").

## Owner amendment (Add-on = total-risk rule) — applied
Thesis done + (existing tranches at current stop + working orders + new order) ≤ 1.00% of week-start equity (0.50% without thesis) + new order ≤ 0.50% × min(Regime, Emergency). Entry above or below the average entry; below → one warning line "Adding below entry — re-check ④ Wrong if" (`ADDON_BELOW_ENTRY_WARN`, never a block). Multi-entry plans stay within the cap in force. Removed from engine, codes, form text and tests: +1.5R, breakeven stop, at-or-above-entry (`COMP_PILOT_R`, `COMP_PILOT_STOP`, `COMP_TOPUP_STOP`, `COMP_THESIS` → `ADDON_THESIS`, `ADDON_TOTAL_RISK`). Momentum's net-breakeven release (Option C) unchanged.

## (a) Removed / neutralised — every function and setting
**Neutralised to inert one-line shells** (logic deleted; the shell stays only because a legacy UI call site still renders through it):
- Loss brakes: `lossOn lossRaw lossStartMs lossPortValue lossItems lossEval lossSync lossResumeOpen lossResumeIn lossResumeSave lossUntilTxt lossWdTxt lossBlockMsg lossChipHtml`
- DD steps: `ddEval ddSync ddNote ddChipHtml ddBarHtml ddWeakest ddSheetHtml ddSheetOpen ddReviewIn ddReviewSave ddCoreBlockNew ddCoreBlockLadder ddCoreBlockAdd ddSatBlock ddBucketsOf`, `coreBlkNew`, `coreBlkAdd`
- Satellite caps / pyramid: `satV2Brake satV2Caps satV2Risk satPyrSplitOf`
- PS1 panel / status: `ps1PanelHtml ps1RenderPanel ps1TodayLine bdPortRiskHtml` (Port-top caps panel), `td3PoolLinesHtml td4RiskChipHtml`, `ln4RoomR`
- Constants / flags: `SAT_NEW_WEEK_MAX` (weekly new-idea quota → `Infinity`), `SAT_MACRO_CUT` (→ 1, Macro cut and 0.6 factor gone), `SAT_RED_FAC` 0.6 → 0.65 (engine Condition), `ffPoolFactor('winner')` (Momentum regime throttle → neutral 100%), `ps1Off()` (legacy `dash.ps1Off` toggle → always false; no dual runtime).
**Logic replaced by the engine** (code rewritten): `ps1FormRun0` (Momentum/Compounder plan form), `ps1AddCalc` (additions / Add-on), `satV2PlanCalc` (Satellite size, queue, daily slot, re-entry, budgets, condition table), `pb2Calc`, `ln4PortPills`, `ln4RiskLine`, `bdRiskNow` (Plan header: Active week usage vs 3% summary, was PS1 principal / 5% cap), `wl1PlaceGate` (engine gate + WL1 aggregate), `wl1FillErr` (→ never blocks), `outcomeOfPnl` (strict sign), `realizedPnlOf` (net of recorded costs). Removed checks inside: PS1 risk-range / caps in `ln4CoreChecks`; PS1 / old Open-Risk caps in the Satellite add-to-position check; Sat Starter row and `t.starter`.
**Settings:** removed from "Settings · execution": Starter feature, Starter default, Stage ladder, Week loss limit rows (replaced by "Settings · risk": snapshots, cash flows, costs, Training · Starter ¼).
**Stored data kept, unread (no deletes):** `psRisk.*` caps / loss, `lossState`, `coreRisk.*`, `satRisk` / DD, `sV2*`, `ln4.stage`, `ln4.starterOff`.
**Still present, not removed (see (d)):** the old Settings cards for those caps (Portfolio & Risk caps/loss, Core risk, Sat Main/Tactical) are still visible but no longer read; `ps1-size.js` / `core-size.js` still contain the old pure helpers (no longer called for sizing or limits); the legacy "L" ladder editor for existing Compounder cards.

## (b) Behaviour changes the owner will notice, screen by screen
- **Plan › New plan / Edit (Momentum, Compounder):** the editable "Risk per idea" is gone; a result box shows one formula line naming every factor (`0.45% × homework 50% = 0.225%`), then `#qty · ฿amount`, then the room line (`Week room … · idea n of 4 · full size after homework`). Blocked = red box with the reason(s) and `allowed now #x (needs #y)`. Compounder shows `Pilot | Add-on` (Add-on 🔒 + the missing list until the thesis is done), regime/emergency in the formula, and the below-entry warning line. Save plan / Save draft stay enabled; the Plan board and Today layout are unchanged.
- **Plan › Satellite form (PB1b):** same result box (`Step 2 · 0.30% × 65% = 0.195%`, R:R · queue · setup of the day · week room). Condition factor 65% (was 60%). Place order shows a one-tap **Re-entry** confirm after a stop-out; no Starter row.
- **Plan board / Today Act:** Place order is disabled with the engine reason (the row stays visible, button disabled). Plan header "risk in use" now = Active week usage / 3%.
- **Filled ✓ / Close trade:** always accepted; a breach is flagged (`FILL_OVER_LIMIT`) and the form says "Over limit — the fill is accepted and flagged". Close form takes optional fees / swap; "Add costs ›" appears when costs are missing.
- **Stop move:** estimated net-breakeven line, `Risk ฿0 · frees 1 idea`, tick "The stop is placed at the broker"; a To do `Move stop · SYM` appears at +1.5R.
- **Port:** the PS1 caps panel (risk in use / 5%, COMP 3 / MMT 1.5 / SAT 0.5) is replaced by one risk block per account (Momentum · Satellite · Compounder with room · Active total `summary` · Emergency · basis line · Compounder unlock flow when locked); capital pools are labelled "Allocation — not the risk basis"; Give-back stays read-only.
- **Today:** status text and chip come from the engine (snapshot due/stale, Emergency, locks, regime); To do gets `Snapshot due · account`, `Move stop · SYM`, `… still valid?`. Momentum regime throttle text is gone (Compounder regime only).
- **Settings:** Equity snapshot per account (amount · date · Confirm), `+ Cash flow`, Costs per account × strategy, Training · Starter ¼ (set OFF once at cut-over).
- **Journal:** strict sign rule everywhere (−0.4 is a loss); old trades show "costs not recorded"; event timeline per closed idea.
- **First run:** no snapshot → entered capital as `Provisional` for 14 days from cut-over; then new orders are blocked until a snapshot is confirmed.

## (c) Counts (final run)
| Suite | Result |
|---|---|
| `tests/risk_engine_test.js` (engine) | 313 pass / 0 fail |
| `tests/re1_adapter_test.js` (adapter) | 63 / 0 |
| `tests/re1c_live_test.js` (live layer) | 63 / 0 |
| `run_tests_re1c.py` (360 / 390 / 1280 / 1440) | 203 pass / 0 fail |
| 375 (`run_tests_phase375.py`) | 158 / 0 |
| 374 (`run_tests_phase374.py`) | 254 pass / 0 fail · 3 retired (1 check × 3 viewports) |
| 373 (`run_tests_phase373.py`) | 547 pass / 0 fail · 9 retired (3 checks × 3 viewports) |
| SW2 (`run_tests_phase_sw2.py`) | 33 / 33 |
| re1b (`run_tests_re1b.py`) | 19 / 0 |
| `ui_audit.py` | exit 0 · `screens not ok: []` · identical to origin/main (table below) |

Retired checks are printed as `RETIRED (RE-C1, not counted as PASS)` and are **not** in any pass count above.

## (3) Retired checks — reported separately, NOT counted as PASS
 After review **5 were restored** (their asserted behaviour is not changed by the brief) and **4 remain retired** (listed below, with `RETIRED_RE1C1` in `run_tests_phase373.py` / `run_tests_phase374.py`):
1. `374 · "5 Filled ✓ above the cap → Save disabled with the reason + allowed qty (50)"` — contradicts the hard rule "actual fills are always accepted and flagged". Replaced by `run_tests_re1c`: "Filled ✓ over a cap: Save stays enabled and the form says it is accepted + flagged" and "Filled ✓ succeeded … carries FILL_OVER_LIMIT".
2. `373 · "8 Port top: Risk in use 1.2% / 5% · Week loss · Room · Open plans · COMP/MMT/SAT used / cap"` — the PS1 caps panel (5% total, COMP 3 / MMT 1.5 / SAT 0.5) is removed by §3; replaced by the Port risk blocks ("Port shows one risk block per account", "Port block rows…").
3. `373 · "8 bar colours: ≥80% of cap amber (MMT 1.3/1.5) · over cap red (SAT 0.6/0.5)"` — colours of the same removed PS1 caps bars.
4. `373 · "8 Plan summary line uses the same risk number"` — it compared the Plan header with the removed PS1 panel number; the header now shows Active week usage vs the 3% summary check.

**Restored and passing (retired earlier by mistake; no Plan board / Today code was changed to make them pass):**
- `373 · "1 split plan = ONE card with '¼ in'; full = 'full'"`, `373 · "3 Ordered → Filled ✓; Holding add-on rule met → Add-on ›; below avg → Edit"`, `374 · "6 add-on condition met → ONE Today reminder"`: they failed only because Starter ¼ is OFF after cut-over (the brief mandates OFF once). The Plan board and Today layout did **not** change. The 373 / 374 launchers now switch Training ON, as a user who wants Starter would, and the checks pass unchanged.
- `373 · "9 Act follows the board (Fix risk → Add-on → < 2% → check fill), max 5"`: failed for the same Starter reason (the Add-on row needs the Starter plan). Passing again with Training ON; no board / Act code changed except that an engine-blocked plan stays visible in Act with a disabled button.
- `374 · "5 plan B (same stock) would make working 80 > 50 → BLOCKED across plans"`, `"5 done: A (40) + B (40) fit, third plan blocked"`, `"5 plan form cap box …"`: WL1 aggregate / cap box were lost in my first wiring; restored (the engine plan stores the full-size quantity, `wl1PlaceGate` = engine gate + WL1 aggregate, cap box redrawn). Passing unchanged.

## (4) Guarantees and the tests that prove them (`run_tests_re1c.py`)
- **No code path changes the quantity of an existing position or working order:** "NO existing position / working order / plan quantity changed by snapshot, costs, Emergency, flows, Training, forms, Port, Today" (Emergency ON, 4 holdings + 1 working order, snapshot / costs / flow / Training / forms / tabs exercised, JSON of all quantities identical); "no write changed an existing position's quantity or stop"; live-layer "live layer is read-only (input unchanged)"; "a moved stop … quantity untouched".
- **Place order is the only thing blocked:** "Place order IS blocked by the engine when a limit is hit"; "a blocked form still lets you Save plan and Save draft"; "Save draft stays enabled while blocked"; "Place order gate: blocked with the engine reason".
- **Filled ✓ and Close trade always succeed and flag:** "Filled ✓ over a cap: Save stays enabled and the form says it is accepted + flagged"; "Filled ✓ succeeded with the real quantity and carries FILL_OVER_LIMIT"; "Close trade always succeeds (Emergency on, account over its limits)"; "close is accepted (status closed, fees stored)".
- **WL1 homework rules through the engine:** Momentum 50% until the thesis ("WL1 (Momentum): 50% until the thesis is done, named in the formula"; "Momentum homework 50%: 0.45 × 50% = 0.225"); Compounder 0.50% without thesis ("WL1 (Compounder): 0.50% Pilot without thesis (× regime/emergency), no extra homework cut"); aggregate per stock across plans ("WL1 aggregate per stock across plans: plan A working 25 + plan B 10 > 50% of full (25) → blocked with allowed qty", "…and Place order of plan B is refused", "once the thesis is done the cap lifts to full size"); plus restored 374 checks "plan B (same stock) would make working 80 > 50 → BLOCKED across plans" and "A (40) + B (40) fit, third plan blocked".

## (d) Unresolved / stopped on
- **Snapshot basis rule:** the brief ("latest confirmed snapshot at or before the period start") and engine spec §5.1 ("first on or after Monday 00:00") disagree. Followed the brief inside the adapter; the engine is untouched. They differ only with a mid-week manual snapshot.
- **Add-on entry wording:** `RE1-answers-A.md` item 16 (main folder) still said "at or above the Pilot's average entry"; the owner message says above or below (warning only). Followed the message and edited the repo copy.
- **Plan save while a limit blocks:** Save plan / Save draft stay enabled (a plan reserves nothing); only Place order is disabled. Say if Save plan should be blocked too.
- **Starter Stage 2/3 (½ / full):** not in RE1; the engine only has ¼. The Stage control is hidden; data kept.
- **Not excised (listed in (a)):** inert shells, the old Settings cards for the removed caps, the old helpers in `ps1-size.js` / `core-size.js`, the legacy "L" ladder editor. Full excision belongs with RE-C2 / RE-D (it touches Settings and the legacy ladder UI).
- **Not built:** stop-confirm form for Satellite trades; the per-idea Journal timeline is basic (log + stop confirmation + close + flags).
- **FX:** snapshots store the FX at confirm time but sizing uses the account's current FX setting (not frozen per snapshot).
- **ui_audit:** exit 0 and `screens not ok: []`; it still prints non-zero audit counts (rule 6 font/tap target, rule 8 gap, rule 2/4 at 390). They were not compared with main, so I cannot say they are new.
- `tests/screenshots/` is git-ignored; the `re1c-*.png` files were added with `git add -f`.

## Screenshots (`tests/screenshots/re1c-*.png`, animations off)
form-momentum-390/1440 · form-satellite-1440 · form-compounder-390 · form-blocked-390/1440 · compounder-locked-1440 · compounder-addon-below-entry-1440 · port-risk-390/1440 · settings-390/1440 (snapshot + costs + Training) · move-stop-1440 · confirm-stop-1440 · sat-reentry-confirm-1440 · fill-flagged-over-cap-1440.

## Fix round (after review)
1. **iPhone plan form:** the result box lived inside the Entry / SL grid cell; it now sits full width below the inputs (`#cnRe1` after the grid) and `word-break` is normal (no `anywhere`). Layout is asserted at 360 / 390 / 1280 / 1440 for Momentum, Compounder and Satellite, allowed and blocked ("result box full width BELOW the inputs, no mid-word break").
2. **Blocked room line:** it now agrees with the reason — ammunition: `Ideas 4 of 4 used or reserved · week room …`; money: `Week room … · this order needs … · ideas n of 4 used or reserved`; never a count above 4 (tests: live "blocked by ammunition…", "blocked by money…", UI "blocked room line agrees with the reason").
3. **Old Settings cards hidden (data kept, unread):** Portfolio & Risk caps / loss limits / legacy limits, Core rules (DD brake, tier, ladder, add-ons), Sat RPT / DD / pyramid split / value caps / Tactical brake / old per-trade risk. Min stop (stocks and Satellite) and the TP1 / TP2 exit split stay. Test: "old cap / loss / Core-rules / Sat Main-Tactical settings are hidden".
4. **Snapshot basis — the brief wins:** the engine's `snapshotBasis` and the adapter both use the latest confirmed snapshot at or before the period start; spec §5.1, §2 and the engine comment are aligned. New tests: engine "mid-week manual snapshot (Wed) does NOT replace the week-start basis", "a snapshot dated Monday IS the week-start basis", "BASIS_FIRST"; the live-layer test already covered the same in the adapter.
5. **ui_audit, origin/main vs this branch** (same `ui_audit.py`, `--index` on a worktree of origin/main). First branch run had new findings; fixed at 390 (lone chip row on Today, small fonts / tap targets in the new Port blocks, Settings rows and the result box). Final:

| rule | main 390 / 1280 / 1440 | branch 390 / 1280 / 1440 |
|---|---|---|
| 1 word broken | 0 / 0 / 0 | 0 / 0 / 0 |
| 2 chip wraps | 2 / 0 / 0 | 2 / 0 / 0 |
| 3 overflow | 0 / 0 / 0 | 0 / 0 / 0 |
| 4 lone control row | 0 / 0 / 0 | 0 / 0 / 0 |
| 5 duplicate message | 0 / 0 / 0 | 0 / 0 / 0 |
| 6 font / tap target | 41 / 35 / 35 | 41 / 35 / 35 |
| 7 overlap | 0 / 0 / 0 | 0 / 0 / 0 |
| 8 empty gap | 0 / 1 / 1 | 0 / 1 / 1 |

6. **Screenshots retaken** (`re1c-form-*-390.png` incl. Satellite and blocked variants; `re1c-settings-390/1440.png` taller viewport scrolled to Equity snapshot · + Cash flow · Costs · Training · Starter ¼).
