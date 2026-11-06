# PS1 report — Portfolio & Risk (simple), Phase 1

1. **Built:** Settings › Portfolio & Risk card (defaults empty, caps, give-back, Legacy limits collapsed) · lean plan form (Entry ＋ / SL ＋ / Risk, 3 equal columns on one row, ＋ rows only on demand, summary line + Details) · add-on gate · Sat lots = E × risk % with Main/Tactical defaults, §4b verify rule (Structure ✗ blocked · EMA50 ✗ = 60%) + Main/4H defaults · Portfolio Risk panel (Plan tab top) + Today line.
2. **Tests vs main:** `phase120` 124/124 · `ps1-size` 41/41 · full suite (125 suites, same `runall2` method, both trees run in parallel): main 88 ok / 32 failing (pre-existing, day/data dependent), branch had 3 extra failing suites (34, 114, 118) → all fixed and re-run green; phase23 = same single pre-existing failure as main. Old suites run with the dev flag `dash.ps1Off=1` (see `tests/PS1_retired.md`). **Caveat:** the full run was started on an earlier commit; after it I re-ran only the suites that differed (23, 34, 114, 118) + phase120 on the final commit.
3. **PR:** `gh` not installed → compare link: https://github.com/SRTzp/Dashboard/compare/main...claude/ps1?expand=1 (branch `claude/ps1` is pushed; not merged).
4. **Decisions made overnight** (least code change each):
   - Weights (50/30/20) stay editable only in Accounts & Capital › Pools (one source of truth); the PS1 card shows them read-only.
   - Dev flag `dash.ps1Off` (like `dash.ln1Legacy`) so the ~120 older suites keep checking old behaviour; users never have it.
   - Default risk empty → form shows "Set default risk in Settings" and Save is blocked (Risk field read-only until set); same for Sat (per account).
   - Multiplier on the idea: typed risk × regime f × DD (Details only, D1 untouched); §4b 0.6 stacks on top.
   - Plan with several entries: "Buy 1" uses entry-row 1's shares; later rows are not auto-bought.
   - **Review fixes (round 2):** (1) multi-SL: the card/position stop (status, alerts) = SL row 1; blended SL is only used for sizing and for the Portfolio Risk panel while the stop has not been moved; all SL rows stay in `plan.ps1`. (2) Existing free-cash check now applies to PS1 plans (shares cut to free pool cash, note "เงินสดคุม"). (3) Add-on ticket on a plan with unbought entry rows pre-fills the next row's price + risk % (no automatic buys). Answers: weights read-only OK · D7 stays parked · Legacy limits stay.
   - Add-on gate evaluates every tranche stop against the NEW stop entered in the add-on ticket; budget left = idea budget − risk at that stop. Old-ratio (50% of previous lot) and max-lots do not apply to PS1 cards; EMA10/red-status/DD blocks still do.
   - Caps count open positions' principal risk + risk of planned (not yet bought) PS1 plans; positions with no stop are listed as unknown and not counted (shown in Details).
   - Panel give-back uses the Core card close only when fresh (≤7 days, same rule as card status); Sat has no price → give-back "unknown". Sat "actual weight" = Sat sub-account balance ÷ E.
   - Sat free margin (D7 parked): shows the Sat sub-account balance as information with "margin is not risk".
   - Old Sat orders (already saved) keep their numbers; orders saved now carry `trade.ps1` {E, risk %, riskTHB}; their pyramid uses that budget and PS1 caps.
   - Free-cash check of the old Momentum form is not applied to PS1 plans (brief does not ask for it).
5. **Needs you:** (a) confirm weights stay read-only in the PS1 card; (b) D7 — which balance is "free margin"; (c) whether PS1 plans with extra entry rows should create the later buys automatically; (d) decide when to retire the Legacy limits rows entirely; (e) PARKED D1–D7 untouched (no half-size chip, no Theme ID, no daily Sat stop, no sweep).

## Files
`ps1-size.js` (+ copy in `index.html` via `tools/sync_ps1.py`) · `tests/ps1_size_test.js` · `tests/run_tests_phase120.py` · `tests/ps1_shots.py` · `tests/PS1_retired.md` · screenshots `tests/screenshots/ps1-*.png` (form single / 2×2, Sat blocked / unclear / clear, panel, Today · 390 + 1440).
