# LN4 — Lean Today + Lean Watch + execution aids (report)

Branch `claude/ln4` (from `origin/main`) · backup `index.backup-pre-LN4.html` · run unattended; every decision below was taken from the brief without asking.

## §0 Audit

### Old Today block → new place (nothing silently disappears)
| Old block (tdHtmlLean) | New place |
|---|---|
| `ftTodayPin` (Homework pin, fast-track) | **To do** chips (red overdue → amber due ≤ 1d → grey); the original pin row is kept inside **Details ▸** |
| `sk1Html` Skills due (weekly-impact / living-thesis / playbook / stock-news / idea-scout) | **To do** chips (same `sk1Items()` rules; `living-thesis +N more` chip for the hidden ones). Tap copies the prompt exactly as before |
| `td4RemBanner` "Unfinished today" (after 20:00) | **To do** grey/amber chips after 20:00 (same `td4RemList`, same dismiss key); banner kept in Details ▸ |
| `tdRegimeVerdict` | Regime pill (same function, same click → Flow › Regime) |
| `td3NewsHtml` Today's news (HIGH) + key events | **TODAY** line (same `td3NewsModel`): time ICT · name · assets; < 4 h amber `in 3h 12m`; past faded; hidden when none. Tap an event → the old detail (`td3EvDetail`: forecast/actual/read ✓) opens under the line; `Calendar ›` = old US-calendar link. The "Please check the Calendar" empty text is gone (line hidden instead) |
| `td3GoalsHtml` account goals | **GOAL** line (first account, % + bar). `Accounts ›` opens the full per-account/sub-port goals panel; the full panel is also in Details ▸ |
| `ps1TodayLine` Risk / left / give-back | Status card `Risk x / 5% · room yR this week`; the full collapsible Portfolio-Risk panel is in Details ▸ |
| `td3PoolLinesHtml` Momentum/Compounder used % | Details ▸ (the regime caps are already in the Regime pill text) |
| `td4RiskChipHtml` (DD / Open-Risk / New / L2 chips) | Details ▸ ; abnormal Momentum/Compounder/Sat state → **port status pill** |
| `td3OverviewDaily` Macro line + chips + Sectors · Daily | **MACRO** line (+ `Playbook ›`); chips and Sectors block kept in Details ▸. Sectors → also **HOT** line |
| Panel "Selection" `td3CoreDaily`: Deep dive / Cand → WL / New Cand / If time permits / Weekly News | **Find** card: 3 counters → one list at a time (same functions: `td3HwGo`, `td4ProPick` screening form, `td3NotPassed`, `td4CandDelete`, `td4AddCands`); Weekly News line unchanged (only when unread). *"If time permits"* (next candidate) is dropped from Today — the next unscreened candidate is the first row of the Cand → WL list |
| Panel "Plans" Core draft/open rows (`td3PlansHtml`) | **Act › CORE** (MMT first, COMP second) |
| Panel "Plans" Satellite rows (`td3SatDaily`) | **Act › SAT**. "No trade" (nt) rows are hidden (normal = hidden) |
| Daily \| Weekend switch + badge | Status card, right side (same `data-td3-sw`) |
| Weekend panel `td3WeekPanelHtml` | unchanged WK1 list under the status card |
| `Other ▸` (dev flag only) | unchanged (still reachable by `dash.td3OtherDev`) |

### Plan data used
Core plan = `coreCards` doc (`status plan` → Draft, `open` → Open/Filled); Sat plan = `satIdeas` (+ trades in `plan`/`open`). **Order working** is new data: `coreCards.ln4.placedAt` / `satIdeas.ln4.placedAt`. Checks reuse existing rules (no new rule logic): Setup ✓ = `tv1SetupLeft` (Core), Sat setup/verify = `td3PlanStatus`; min stop = `ps1StockMin` / `ps1MinStopMsg`; risk range + caps = `Ps1.capCheck` with the stored `plan.ps1` snapshot.

### Watch builders reused
`wlRowsAll`, `tv1EtfOf/tv1HotOf/tv1SecName`, `tv1ReasonText`, `tv1CandInfo`, `tv1SetupLeft/Toggle`, `tv1KeepMore`, `td3NotPassed`, `td4CandDelete`, `tv1Changes/Download/Import`.

## Decisions taken (brief was silent)
1. **Room** = week-loss limit (settings `loss.weekR`, 5R) − the larger of Momentum / Sat realised week-loss units (`lossEval(...).weekR`) of the home account. Omitted when Portfolio & Risk is off.
2. **Port pill** from `lossEval` (Half / Stop …) per bucket, else regime factor `Momentum ½ (regime)` / `¾` when `ffPoolFactor.cap < 100`.
3. **HOT sectors** = RRG rows `lead|weak` (amber ↗) then `rrgIsFresh` (blue Fresh).
4. **Missed** is checked for **Core plans only** (latest price `c.px` ≥ plan Entry, long). Sat has no latest-price source on the plan. Recorded setups = *Order working* (valid) + *recorded Missed*; a plan filled without ever being Order working is not counted. `Exec` badge stays visible once there is a count even when there are no to-do chips (brief: row hidden when nothing to do).
5. **Pass / Screen / Drop** in Find → Cand→WL: `Screen ›` opens the existing screening form (Move to Watchlist), `Pass` = existing "Not passed", `Drop` = existing delete.
6. **Core Starter** (see "Deviations") scales the risk used by the Starter fraction and stores `plan.starter` + `plan.addon {riskPct, frac, cond:'stop>=be'}`. `Add-on ›` shows when an open starter plan has stop ≥ avg and only 1 lot; it opens the existing add-lot form.
7. **Fix buttons** open the Plan tab with the plan form in a new `editw` mode (edit existing Draft plan, Stop/Risk field focused). `Setup ✓ ›` opens the Watchlist row (where Setup ✓ is ticked).
8. **Buy Stop / Buy Limit** label: Buy Limit if latest price is above Entry, else Buy Stop.
9. Stage fraction: 1 = ¼, 2 = ½, 3 = full (Starter switch hidden at Stage 3).

## Late brief changes (received mid-run)
| Item | Status |
|---|---|
| 1 Settings **Starter ¼ feature** Off removes the switch from Core + Sat forms; manual ＋Entry/＋SL still work | **Done** (`settings.ln4.starterFeatureOff`). Off also hides ¼ labels, Stage badge, add-on button, Journal Starter chip. Test F1 |
| 2 Sat Trade Overview TF · Trend · Verify on one row, Zone below | Already the structure of the form; verified by test D8 (+390 screenshot: order kept) |
| 3 Setup row: In Zone · MMT Neutral · Pivot align MA (keys kept), all 3 required, `✓ all` 0.8 s hold | **Done** — labels/order renamed in `PF_SETUP_CK`; Save blocked `Setup n/3`; `✓ all` (click = tooltip only, early release cancels, hidden at 3/3, keyboard hold). Tests D1 D3 D7 |
| 4 Verify matrix ✓✓ 100 · EMA✗ 60 · Structure✗ = Counter 60 (confirm at Save) · ✗✗ blocked; Up/Down; never 36 % | **Done** (`ln4VerifyOf`, one 60 % factor). Confirm sheet only at Save for EMA ✓ + Structure ✗; stores `counter_trend:true` and `trade.counterTrend`. `Counter` tag: Sat form header, Today Act row, Journal row + filter chip. Tests D2 (4 rows × Up/Down) D5 |
| 5 Macro no longer cuts Sat size — warning only | **Done**. Places the macro factor was applied and are now 1.0: (a) `satMacroFactors()` neutral/against/mr; (b) `satV3F2c` `rule` (was `Calc.sizeRule`) and `factor`; (c) `satV3PlanAcctCalc` `ruleF`/`facA` (v1 calc, incl. MR fixed 0.6); (d) `satV2PlanCalc` `ruleF`/`fac`; (e) "Macro & ขนาดไม้" text now `เต็ม (macro = warning only)` and the "use full size" switch removed; (f) the mandatory reason box (`needNote`) no longer blocks Save. Warning pill `Macro against ▼` / `No Playbook` in the form's check-pill row and on the Today Act row. Test D4 |
| §4b check-pill row under Entry/SL/TP; Starter in Sat form | **Done** (Structure · EMA50 · Setup n/3 · R:R · Stop ≥ min · Risk · Counter/Macro). Sat Starter multiplies the sat risk by the stage fraction |
| iPhone readiness (390) | Done for LN4-owned screens (test 370, screenshots below). Pre-existing legacy elements outside LN4 scope are not re-styled |

### Gaps closed (follow-up round, same branch) — all Done
| Gap | Status |
|---|---|
| §4a Core Starter = Entry split rows | **Done.** ON → row 1 split 25 % (normal price) + auto row 2 split 75 % "Add-on · stop ≥ BE" (price optional, editable; blank = estimated at Entry 1). ＋Entry still works. Summary `Now: … ` + `Planned total: …` (2nd line only with Starter ON). OFF → single row 100 %. Feature Off → no switch, rows untouched. Stored shape unchanged (`plan.starter`, `plan.addon {riskPct, frac, cond, px?}`, snapshot = "Now" rows) so Today/Port/Journal keep working. Removing the add-on row turns Starter off. Tests S1–S4 |
| §8 Plan cards | **Done.** Strip under every Core card (Plan tab) and in the Sat plan form: MMT/COMP tag (+ ½) · Draft (reason + Fix button / `Place order ›`) → **Order working** (`Record fill` / `Cancel order`) → Open (`Add-on ›` / `Raise stop ›`). Built from the same rows as Today Act (`ln4CoreRows` / `ln4SatRows`). `Cancel order` clears `placedAt` (setup stays counted as valid, not taken). Test 8 |
| §8 Port | **Done.** Open-position list: `¼ starter · add-on planned`, `stop below avg`, `0 risk`; risk summary `room yR this week` — same function (`ln4RoomR`) as Today |
| Journal "Taken" chip | **Done.** Closed trades whose plan was a valid setup and was filled (core card `trade_id` / Sat `accts.*.trade_id`) |
| Suites 117 / 120 | **Done** — rewritten to the new expectations (see `tests/LN4_retired.md` list; now pass 64/64 and 128/128) |
| Sat Missed detection | Skipped as agreed (no latest-price source on Sat plans) |
| Sat `Add-on ›` | Not built (unchanged) |
| Plan form `Fix` reason-text parity beyond the focused field | Not built (unchanged) |

## Visual match pass (mockup ↔ app)
Side-by-side shots (mockup | app) at 1440 and 390: `tests/screenshots/ln4-match-<screen>-<1440|390>.png` · generator: `tests/ln4_match.py` (`LN4RAW=dir python3 ln4_match.py`). App tokens only (no mockup CSS copied); no function removed.

| Screen | Difference found | Fixed? |
|---|---|---|
| Today | `Record fill` / `Add-on ›` were green; mockup has green only for `Place order` (Record fill = white outline) | Fixed |
| Today | Find: counters sat flush under the header (no gap) | Fixed (10px gap) |
| Today | Regime shown as long text (`Risk-ON · Momentum 100% …`) vs mockup's short `Bull` pill | Not changed — existing `tdRegimeVerdict` text kept (function reuse) |
| Today | `Calendar ›` link after TODAY chips; chips ≥36px tall on 390 vs mockup ~26px | Kept (existing link; 36px tap rule from suite 370) |
| Today | Block order, one-line Act rows, 2 lines at 390, HOT/TODAY/To do/Exec chips, status colours | Already matched |
| Core form | Starter was a plain checkbox *below* Risk; mockup = teal toggle bar *above* Risk with "25% now · 75% add-on at break-even" | Fixed |
| Core form | Risk per idea label above a bare input; mockup = one inline row (label · input · % · Momentum·Normal pill) | Fixed |
| Core form | Inputs unstyled (square); mockup = rounded 10px inputs | Fixed |
| Core form | ＋ buttons in the header; mockup = dashed `＋ Entry` / `＋ SL` pills under the rows | Fixed (same ids) |
| Core form | Add-on row: "price (optional)" placeholder + long note; mockup = `at BE` + `Add-on · stop ≥ BE · #48` | Fixed |
| Core form | Summary italic labels; mockup = bold `Now:` line + muted `Planned total:` with teal numbers | Fixed |
| Core form | Save button black; mockup green | Fixed (plan forms only) |
| Sat form | Starter row plain checkbox + long text | Fixed (same toggle bar, "25% now · rest at break-even") |
| Sat form | `Setup on minor` label above chips; mockup = label + chips on one row | Fixed ≥561px; at 390 label wraps above (chips + `✓ all` stay on one row) |
| Sat form | Verify labels `EMA50 Verify` / `Structure Verify`, per-account OUN/FAM rows only when sizeable | Kept (existing text; rows appear once the plan can be sized) |
| Plan list | Mockup = dense Act-style rows; app = existing cards + new state strip | Strip restyled (tag · detail · status · buttons; MMT grey unless ½); card list kept |
| Journal | Weekly row was plain text; mockup = tinted bar with `Week n · Exec x/y`, taken/missed squares, `Stage 1 · ¼` pill | Fixed |
| Journal | Chip order/labels: mockup All · Taken · Missed · Starter ¼ · Full | Fixed (added `Full`; other chips follow) |
| Port | Badges + room were only in the Plan-tab risk panel; Port tab had none | Fixed — new `Port · risk` card (Risk used · Room this week · Week loss) + Open positions with badges (starter badge blue) |
| Settings | Checkboxes + teal bold labels; mockup = toggles, stage buttons `1·¼ 2·½ 3·full`, Week loss limit, Exec goal | Fixed |
| Watch | Rows flat with borders, tag glued to ticker; mockup = tinted rounded rows with lime bar, aligned tag column, sans ages | Fixed |
| Watch | Group headers (HOT · Sector n / Other n) not verifiable with stubbed rows | Not checked; extra `Filter` / `…` buttons are existing functions, kept |

## Tests
See `tests/LN4_retired.md` for changed expectations. New suites: `run_tests_phase369.py` (status card, Act, Starter, Exec/Missed/ladder, To do, Find, Watch, Sat matrix/counter/setup/macro/✓ all/feature Off) and `run_tests_phase370.py` (iPhone 390 audit + screenshots).

## Results (final run, Chromium)
| Suite | Result |
|---|---|
| 369 (new, LN4) | 201/201 |
| 370 (new, iPhone 390 audit) | 26/26 |
| 59 | 86/86 |
| 106 | 48/48 (old-layout groups retired → `tests/LN4_retired.md`) |
| 365 | 68/68 |
| 366 | 116/116 |
| 367 | 61/61 |
| 368 | 120/120 |
| cg1 | 46/46 |
| 117 | 64/64 (rewritten) |
| 120 | 128/128 (rewritten) |

## 390 screenshots (iPhone-width, `tests/screenshots/`)
Today `ln4-390-today.png` · Watch `ln4-390-watch.png` · Core form `ln4-390-core-form.png` · Sat form `ln4-390-sat-form.png` · Plan list `ln4-390-plan-list.png` · Journal `ln4-390-journal.png` · Port `ln4-390-port.png` · Settings `ln4-390-settings.png` (+ 1440/390 `ln4-today-*.png`, `ln4-watch-*.png`).
iPhone audit covers LN4-owned elements (no horizontal scroll on every screen; text ≥ 12px; tap ≥ 36px; Core summary ≤ 2 lines; Sat TF→Trend→Verify order and Setup + `✓ all` on one row; Watch row on one line; Settings switch on the right). Port screen only checked for overflow (no LN4 elements added there). Legacy elements outside LN4 (e.g. Sat plan-card internals) were only touched where the audit flagged them.


## Branch
Compare: https://github.com/SRTzp/Dashboard/compare/main...claude/ln4 (not merged)
