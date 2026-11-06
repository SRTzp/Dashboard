# PS1 — changed test expectations

PS1 changes how NEW plans and NEW Sat orders are sized (E-based risk, caps, verify rule). Older suites assert the pre-PS1 numbers and flows, so they keep running the **pre-PS1 code paths** through one developer flag, the same way `dash.set1Open` / `dash.ln1Legacy` already work:

- `tests/ff_stub.py` → `SET1_DEV_FLAGS` now also sets `localStorage['dash.ps1Off']='1'` in every launcher that uses the stub.
- With the flag on (`ps1Off()` in `index.html`): the plan form runs the old Base Risk path, Sat sizing uses the old RPT + Open-Risk caps, there is no Main "Check Structure first" block, new Main plans keep TF = Settings value, and the Portfolio Risk panel / Today line are not drawn.
- Users never have this flag. `tests/run_tests_phase120.py` removes it (`localStorage.removeItem('dash.ps1Off')`) and tests the PS1 behaviour.

| Old expectation (pre-PS1) | PS1 behaviour (covered by phase120) |
|---|---|
| New Momentum/Compounder plan: Risk = Base Risk 1% × pool × FF, one Entry/Stop/Risk, "ไม้แรก … หุ้น" line | Risk % of whole-portfolio E, default per bucket (empty until set), summary `sh · Risk · Size`, optional ＋ rows, size cap + bucket/total caps |
| New Sat order: lots = Sat pool × RPT Main/Tactical %, Open-Risk caps (orSat/orAsset/orTot) + Max Heat block | lots = E × default risk (Main / Tactical), PS1 bucket + total caps only |
| New Main Sat plan: TF = Settings value (D), no Structure requirement, Clear/Unclear affects nothing for Main | TF 4H, Structure ✗ → "Check Structure first" (blocked), EMA50 ✗ → size 60% |
| Core add-on: 50%-of-previous ratio, max 3 Base lots, Base budget minus carry | PS1 cards: new idea budget only when every stop ≥ its average entry, else what is left; size cap + bucket/total caps re-checked |
| Settings: Max Heat / Open-Risk caps visible in Core rules / Sat rules / Accounts | Same fields (same ids, still saved) inside the collapsed "Legacy limits" of Portfolio & Risk |
| Plan tab at ≥1000px: `#planTop` hidden in Lean | unchanged; new `#ps1Panel` is a sibling above it and is shown (grid row 2; core panel/side moved to row 3) |
| phase23: Core rules had 22 labelled fields incl. the unit-less "Core — % of Core bucket" (Max Heat) field | that field moved to Legacy limits → 21 fields, 0 without a unit label (`run_tests_phase23.py` updated) |

Nothing stored was changed or deleted: old plans, trades and settings keep their numbers; PS1 data lives in `settings.psRisk`, `plan.ps1` (cards) and `trade.ps1` (new Sat orders).
