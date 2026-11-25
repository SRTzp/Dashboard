# HF5 — Sat: new setup only when every open one has risk cut ≥ 50% (max 3) · Manage shows Sat holdings (Price + Move stop) · Last price fix · risk check audit

Branch from fresh origin/main (after HF4 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-hf5 -b claude/hf5 origin/main`. First commit = this brief + `hf5-mockup.html`. UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md`. This brief is locked — nothing gets added mid-job.

## A · Sat queue rule (SRTp decision 25 Nov, replaces RE1 "one active setup per account"). Example from SRTp: setup 1 at no risk (stop at entry) + setup 2 with 50% risk left → setup 3 may open; max 3.
- A new Sat setup (Place order) is allowed when **(1)** the account has fewer than **3** live Sat setups (working orders + holdings), AND **(2)** every live Sat setup in that account has its **current risk ≤ 50% of its initial risk** — i.e. its stop was moved so risk is cut ≥ 50%. A working (unfilled) order counts as full risk → blocks the next one.
- Initial risk = the order snapshot risk (`ln4.snap` riskAmt / entry→stop × qty at fill). Current risk = |fill price − current stop| × qty × contract value (0 or less = stop at/through entry = 100% cut). Use the existing engine/Calc helpers, one function `satRiskCutPct(idea)`.
- Constants in ONE place: `POLICY.sat.maxActive = 3`, `POLICY.sat.newSetupRiskCut = 0.50`.
- Unchanged: one setup per product per day, re-entry rule, step machine, weekly 1.20% / monthly 4.80% budget check, Step 4 lock.
- Messages (name the OPEN setup, not the candidate — today's text wrongly said "open in BTC"):
  - `⚠ XAU is open with full risk · move its stop to cut risk ≥ 50% (now 0%) to open another Sat · Move stop ›` (link = the Sat Move stop sheet of XAU, part B)
  - `⚠ 3 Sat setups open (XAU, BTC, S50) · max 3 · Close one ›`
  - Shown on the plan card, the Place order sheet (HF3 line style, Confirm grey) and wherever SAT_QUEUE_BUSY shows.
- Tests: XAU working order → BTC blocked; XAU filled, stop unmoved → blocked (0%); stop moved to cut 49% → blocked; 50% → allowed; stop at entry → allowed; XAU at entry + BTC cut 50% → S50 allowed; XAU at entry + BTC cut 40% → blocked; 3 open → 4th blocked even if all at entry; budget check still blocks; Short and Long.

## B · Today › Act › Manage: every open Sat position gets a row with Price ›and Move stop ›
Mockup `hf5-mockup.html`. Today Sat holdings fall into `nothing++` (`by.hold` ~29576).
- Row: `XAU · SAT · M · Short · Holding` + buttons `Price ›` and `Move stop ›` (both white). Line 2: `Entry · Stop · TP · #lot · risk $X` (+ `(−59%)` once the stop moved). Line 3: no price → amber `No price yet · add it to see P&L` (row border amber); with price → `Last 2,621 (25 Nov 07:10) · +1.3R · +$374` (green if ≥ 0, red only if money lost) and, when the risk cut ≥ 50%, `✓ risk cut ≥ 50% · new Sat setup allowed`.
- Direction words Long / Short = plain ink (rule 7).
- **Price ›**: small sheet, one number field (decimal, 16px font), Enter = save. Stores the existing `lastPx` (+ `lastPxAt`) on the plan — display only, never an engine input except the P&L line. Older than 1 day → line shows the date in amber ("price from 23 Nov").
- **Move stop ›**: small sheet: current stop, new stop field, live preview `risk $289 → $119 (−59%)`; refuses a stop on the wrong side of the current price if a price is set (message names it). Save writes the plan stop + a log line (`Stop moved 2,660 → 2,650`) and the open trade's stop (same place the engine reads current risk). Reuse existing Sat stop-edit code if there is one; do not duplicate.
- iPhone 390: lines wrap, no "…", buttons side by side, 44px.
- Order: Core action rows first (as now), then Sat holdings. Header `n holding` counts them.

## C · Bug: "Last price" button leads nowhere
Plan card says `Add a last price to see P&L` + `Last price` button (`~28659`, opens the drawer), but PV1b hid the field (`if(false && …)` ~29027, form ~30138, save ~30240). Fix: the button opens the same **Price ›** sheet from part B. Remove the dead hidden code paths or leave them, but no button may lead to a missing field. Test: button → sheet → saved price shows on card + Today.

## D · Risk audit: Today and Plan agree after every order step (SRTp asked to check)
Write `tests/run_tests_hf5_risk.py` that walks one Sat (XAU lot) and one Momentum (US stock) plan through: plan → Place order (working) → Filled → Move stop → Close. At each step assert the SAME numbers in: Today › Risk room (open risk %, reserved, Sat/MMT/COMP chips), Plan board card, the engine budget check (`max(0,−weekly net) + open + reserved + candidate`). Also: cancel before fill releases reserved risk; Family vs Main kept apart. Report a table step × place → number; fix any mismatch you find (say which in the report). If a fix is not small (> ~30 lines or touches the engine formula), stop and report instead.

## Screenshots (only `hf5-*.png`)
`hf5-manage` (1440 + 390: one row without price, one with price + moved stop), `hf5-price-sheet` (390), `hf5-movestop-sheet` (390), `hf5-queue-blocked` (Place order sheet, BTC blocked by XAU full risk, 390).

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks after the last change · revert tracked screenshot rewrites · new suites in REST= · no push until I review — report tests, judgment calls, the D table, PNG list.
