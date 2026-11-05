# CS1 — Core Trade Plan = planning only · Star-based risk (manual ★ first) · tests 111

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/CS1-verify.txt`). **Run after SET1** (start from the SET1 build; record its sha). Backups before any edit, incl. tests: `index.backup-pre-CS1.html` · `tests/_bk_cs1/`.
> **Step 1 is an audit only** (B1). Write `docs/reports/CS1-audit.md` first, then implement. Do not introduce hidden Star → Tier mappings.

## Part A — User text (verbatim, 29 Oct)

Refactor the **Core Trade Plan to focus strictly on trade planning**, and implement an **automated Star System to determine Risk sizing** while preserving the existing compact, iPhone-friendly layout.

### 1. Remove evaluation fields from the plan creation screen
* Remove Tier A/B, Tier override, Fortress / Proven / Emerging evaluation forms, Gate 5, and all fundamental metric input fields from the plan screen.
* Move the input/editing of evaluation results into the **existing Add/Edit Candidate and Watchlist forms**. Use a single centralized data source per ticker + market; do not require re-evaluation when creating a plan.
* For this release, use manual selection of evaluation results first (no API or Webhook integration needed yet).

### 2. Determine stars and Base risk from evaluation results
| Evaluation Result | Stars | Base Risk |
| --- | --- | --- |
| Passes Fortress + Proven | ★★★ | 1.00% |
| Passes Fortress or Proven | ★★ | 0.75% |
| Passes Emerging (without passing F/PG) | ★ | 0.50% |
| Passes RS only (no fundamental pass) | ★ · RS only | 0.50% |
| Fails fundamentals AND fails/untested RS | No stars | Unassigned |
* Evaluate strictly from top to bottom; do not sum stars based on condition count, and do not auto-convert existing Tiers or Setup scores into stars.
* Store statuses for **Failed / Insufficient Data / Not Applicable** separately. Default status must be "Untested"—never assume a pass.

### 3. Prerequisites for opening a new plan
* Candidates can hold tickers even if evaluation is incomplete.
* Adding a ticker to a new Watchlist and opening a new plan require: **Stars ≥ 1 + RS passed + Gate 5 answered "No" for all three checks**.
* RS passes when any of the following passes: Sustained RS Leader / 26W Breakout + RS / 52W Breakout + RS.
* If data is incomplete, display what is missing along with an **"Edit Stock Evaluation"** button that routes back to the evaluation form.
* Enforce these conditions across all entry paths, including manual ticker input.
* If an existing Watchlist ticker subsequently fails evaluation, keep the item in place and mark it as "Pending Review"; do not automatically delete or move it.

### 4. Retain trade parameters on the plan screen
* Keep existing fields: Account, Ticker, Strategy, Entry, SL, Ladder prices, Fund-flow, calculated position size, and the Save button.
* Add a compact summary banner:
> ★★★ · Base risk 1.00% · Auto
> Fortress + Proven · RS Passed
* Stars and Risk % must be **read-only** (derived from the stock's evaluation results), while Entry / SL and strategy details remain fully editable.

### 5. Link stars to the actual position sizing engine
* Base risk is calculated from the **Core bucket equity of the selected account**.
* This serves as a **total risk budget per stock**, shared between the initial entry and add-on tranches; do not allocate a fresh risk budget for each new plan.
* Deduct risk already used or reserved in other plans before calculating a new tranche, without double-counting the plan currently being edited.
* Retain existing FF/DD adjustments (apply once), and display the adjusted Risk along with the remaining risk budget.
* Changing Account, Ticker, Entry, or SL must trigger a full recalculation; never retain stale values from a previous stock.
* Maintain existing constraints: cash limits, FX rates, lot rounding, max capital allocation per stock, and total portfolio risk limits.
* **Risk % is NOT Capital Allocation %**; do not substitute one for the other.
* Audit existing Tier-coupled dependencies (e.g., Ladder eligibility, capital allocation caps) and report the migration path before changing these rules; do not introduce hidden Star → Tier mappings.

### 6. Preserve existing plans and positions
* When saving a new plan, create a snapshot of: evaluation results, evaluation date, stars, Base risk, and adjustments applied.
* Subsequent changes to a stock's evaluation **must not retroactively modify the Risk of existing plans or active positions**, and users must be able to manage legacy positions without forced re-evaluation.

### Acceptance Criteria
* Each star tier yields the exact Risk % and position size specified in the table.
* RS / Gate 5 cannot be bypassed via alternative plan creation routes.
* Add-on tranches and multiple plans do not duplicate the assigned risk budget.
* Switching tickers leaves no residual stars or Risk values from the previous stock.
* Evaluation data remains intact across item movements and page reloads.
* Legacy plans remain fully functional, and forms render cleanly without overflowing on iPhone screens.

Please submit a diff along with a summary of changes, Tier dependencies, and test results before deploying.

**User decisions (29 Oct):** "Start with manual first and we will do the auto part later — keep room for auto later." · Order: TD4c → SET1 → **CS1**.

**Sat addition (30 Oct, verbatim — Plan › Sat):**
"1. If there is no existing Main position and you want to open a Tactical position directly, the Trend Classify must be at "Clear Trend" (adjusted to leave only Clear Trend and Unclear). Furthermore, you cannot open a Main position until the Tactical position for that product is closed.
2. If a Main position already exists, you can open a Tactical position, but it also requires a Clear Trend first before a setup can be planned."
User answers: old values **Strong + Normal → Clear Trend**, **Uncertain → Unclear** · "open Tactical" that blocks Main = **filled Tactical position only** (an unfilled Tactical plan does not block Main).

## Part B — Orchestrator notes

### B0. Manual ★ now, auto later (user decision — overrides "automated" in Part A for this release)
- **★ is the existing manual 1–3 rating** (TD4a: Watchlist + the Today Cand → WL form). In CS1 the ★ value drives Base risk via the table: ★★★ 1.00% · ★★ 0.75% · ★ 0.50% · none = Unassigned (no new plan).
- **Keep room for auto:** add the evaluation record per ticker+market now — `eval{fortress, proven, emerging, rs:{sustained, b26, b52}, gate5:[q1,q2,q3], date}` with each status ∈ `untested | passed | failed | insufficient | na` (default `untested`) — editable in the Candidate/Watchlist forms (manual selection). Store also `stars_src: 'manual'` and a pure function `Calc.starsFromEval(eval)` implementing the Part A table top-to-bottom (with unit tests), **but do not use it to set ★ yet**. When `stars_src` later becomes `'auto'`, ★ comes from that function. If manual ★ and `starsFromEval` disagree, show a small muted hint `Eval suggests ★★` (no change).
- "★ · RS only" label: if ★ = 1 and fundamentals are all non-passed but RS passed → banner shows `★ · RS only`.
- Gate (Part A §3): new Watchlist add (the Cand → WL form) and new plan require **★ ≥ 1 + RS passed + Gate 5 all "No"**. Where the TD4a form had `Tier passed / RS Leader` checkboxes, map them to the new eval fields (RS Leader → `rs.sustained = passed`; "Tier passed" → audit: what it meant, propose the mapping in the audit, don't guess). Missing items → `Missing: RS · Gate 5 (2/3)` + `Edit Stock Evaluation ›`.

### B1. Audit first (`docs/reports/CS1-audit.md`, then continue)
- Every place Tier A/B, Tier override, Fortress/Proven/Emerging, Gate 5 and fundamental fields are read: plan form, sizing (Risk/ไม้ by Tier from Settings › Core), ladder L eligibility, capital caps per stock, Today/Watch displays, Journal stats, imports (living-thesis, core-checklist JSON).
- For each: the proposed migration (to ★ / eval / keep as is). No hidden Star → Tier mapping. Existing Tier data is kept (read-only history), not converted to ★.

### B2. Sizing
- Base risk % × **Core bucket equity of the selected account** = per-stock total risk budget; minus risk used/reserved by other open plans/positions of the same ticker+account (exclude the plan being edited); then existing FF/DD adjustment once; then existing caps (cash, FX, lot rounding, max capital per stock, total portfolio risk). Show: `Risk budget ฿42,000 · used ฿18,000 · this tranche ≤ ฿24,000 (FF 75%)`.
- Account/Ticker/Entry/SL change → full recompute from scratch.
- Snapshot on save: `eval`, eval date, ★, `stars_src`, base risk %, adjustments. Later eval/★ changes never alter saved plans/positions.

### B3. UI
- Plan form: remove the evaluation UI; add the 2-line banner (Part A §4) read-only; everything else unchanged and compact (390 no overflow).
- Candidate/Watchlist forms: compact eval section (status chips per item; Gate 5 three Yes/No) — keep it collapsed by default on iPhone.

### B3b. Sat Classify + Tactical/Main rules (Plan › Sat)
- `PF_CLS` → two values: `clear` = **Clear Trend**, `unclear` = **Unclear** (colours: Clear Trend keeps the old Strong colours by trend direction; Unclear keeps the yellow). Read old values as: `strong`/`normal` → `clear`, `uncertain` → `unclear` (map on read; rewrite only when the plan is saved again). Journal/stats group old + new the same way.
- **Tactical needs Clear Trend (both cases):** in the plan form, with Tactical selected and Classify ≠ Clear Trend → the Setup checks and Entry/SL/TP stay disabled and a one-line hint shows `Tactical needs Clear Trend` (save disabled). Applies whether or not a Main position exists.
- **No Main while a Tactical is held without Main:** if the product has a **filled Tactical position** and **no Main position**, `+ แผน` / the plan form cannot create a **Main** plan (Main segment disabled, hint `Close the Tactical (XAU) first`). Existing Main plans/positions are unaffected; adding a tranche to an existing Main is unaffected.
- Enforce on every route that creates/saves a Sat plan (Plan › Sat form, Today `Create plan ›`, any import). Main sizing/rules otherwise unchanged. Main does not require Clear Trend.
- Today Satellite status uses the new names (e.g. Pending `Needs Clear Trend`).

### B4. Tests — `phase111`
- ★★★/★★/★ → exact risk % and size on a fixture; none → no plan + message; `Calc.starsFromEval` truth table (all rows, top-to-bottom, untested default) — not wired to ★.
- Gate on every route (Today form, Watch add, plan button, manual ticker input, imports creating plans).
- Budget sharing: plan 1 uses 60% → plan 2 limited to 40%; editing plan 1 doesn't double-count; add-on tranches share the budget.
- Ticker switch clears ★/risk; reload keeps eval; moving Candidate → Watchlist keeps eval.
- Legacy plans/positions open, edit and close without eval; snapshot unchanged after eval edits.
- Sat: Classify shows only Clear Trend / Unclear; old strong/normal → Clear, uncertain → Unclear (display + Journal grouping); Tactical with Unclear → setup/fields/save disabled + hint (with and without Main); filled Tactical + no Main → Main plan blocked on every route, Main tranche add still allowed when Main exists; unfilled Tactical plan does not block Main.
- 300/390/1440 no overflow; no console errors. Screenshots `tests/screenshots/cs1-{plan-390,plan-1440,eval-390,gate-390}.png` — open every one.
- Old tests: never delete/weaken; log `tests/CS1_retired.md`. Full run (base + 1–111) after the last index.html edit. Known: p13, p5.

## Report back
Audit summary + migration decisions · "Tier passed" mapping · sizing before/after examples · files changed · full-run results (timestamps) · screenshots opened · limitations · no push, no file deletion.
