# PS1b — changed test expectations

PS1b changes where the Portfolio Risk panel lives, what the Sat Strategy box shows, how new Sat orders are sized, and which drawdown/loss rules apply to NEW plans. No stored number of any old plan/trade changed.

| Suite / check | Old expectation (PS1) | PS1b behaviour |
|---|---|---|
| phase120 §5 Panel (5 checks) | Portfolio Risk panel is on the Plan page (`#ps1Panel`) | Panel lives inside the Today "Risk …" row (collapsed by default); the suite now opens it (`ps1TodayOpen = true`) on Today before reading it |
| phase120 §5 Today | `[data-ps1-today]` is a one-line div that jumps to Plan on click | It is a `<details>`: tap = expand/collapse, state kept in `localStorage.ps1TodayOpen` |
| phase120 Sat tests (sat / pyr) | A new Sat order only needs a default risk | A new Sat order also needs a min stop for the asset (required); `ps_on()` gives every Sat asset 0.05% so these older checks keep testing what they tested before |
| phase120 4b (Sat sizing) | Details table "RPT … / เพดานมูลค่า / ใช้" | New orders: 3 lines (Risk … of portfolio / Stop … pts × multiplier / Used … rounded); value cap no longer limits new orders. Old orders keep the old table |
| Old Sat DD bar, Tactical brake, weekly new-trade counter on NEW Sat orders | blocked / reduced new orders | not applied to new orders (Loss limits replace them). Old orders and `ps1Off` runs keep the old rules |
| Old Momentum/Compounder DD brake (`ddEval`) on NEW PS1 plan cards | size ×0.5 / pause | not applied to cards with `plan.ps1`; Loss limits (10% half · 20% stop & review) apply instead. Older cards keep the old brake |
| Today goals card | sub-port rows visible inside the open goal | rows live in a closed "Sub-port goals ›" row |
| runall2.sh | phases 1–113 | phases 1–121 |

New suite: `tests/run_tests_phase121.py` + `tests/ps1b_size_test.js`.

### Read-method changes (assertions unchanged)
| Test | Change | Why |
|---|---|---|
| phase106 B3 (sub rows, Sat 4.1k→12k) and phase113 §4.7 | `innerText` → `textContent` when reading `[data-td3-sub]` rows | PS1b §4 puts the sub-port rows inside a closed "Sub-port goals ›" row; `innerText` is empty when hidden. Expected texts are the same. |

### §8 / §9 expectation changes
| Test | Change | Why |
|---|---|---|
| phase120 §2/§3 summary | accepts `#68` as well as `68 sh` | §9: share counts show as `#68` (display only) |
| phase120 free-cash | reads `#n` as well as `n sh` | same |
| phase120 add-on prefill (MSL) | marks MSL's screening saved before opening the add-on | §8: add-ons on a fast-track idea are blocked until homework (thesis ①④ + screening) is done |

### §7 plan-form expectation changes (phase120)
| Test | Change | Why |
|---|---|---|
| phase120 §2 layout | "Entry · SL · Risk on one row, equal width" → stacked blocks in order Entry < SL < Risk, no overflow | §7b lean multi-row layout |
| phase120 §2 summary | no longer needs "of portfolio" / "Avg entry" / "Left" in the summary; reads Avg SL + Left from Details | §7b/§7d: `#68 · 3.9% · Risk 0.39%`; Avg SL/Left moved to Details |
| phase120 extra-row selectors | `[data-ps1-er]`,`[data-ps1-sp]`,`.ps1X` → `.ps1Pc`,`.ps1R` | per-entry Risk and SL Out % fields now sit inline in each row |
| phase120 `ps_on` | adds `minStopStock:{winner:null,ladder:null}` | §7e: stock min stop (Momentum 4% / Compounder 7%) is on by default; old tests use narrow stops |
