# PV1 — honest position numbers · Flow asset panel · Planned / Holding cards

Approved by SRTp 17 Nov 2026. Mockup: `docs/briefs/pv1-cards.html` (open first; sections 2 and 3 approved as drawn, section 1 replaced by §A below).
Base: latest `origin/main` (must contain `tests/run_regression.sh`). Branch: `claude/pv1`. Three parts, one commit + push each, in order A → B → C.

## Rules
- No change to investment rules, sizing, limits or gates. Display and labels only, plus one optional field (§A4).
- One source per number: reuse the engine / adapter (`risk-engine.js`, `re1-adapter.js`, `ideaResult` exposure, `pb2Calc`, `plan.ps1`, card lots). No second formula in a view; add a shared helper if a number is needed in two places.
- Missing input → say why in words ("no live price", "not sized", "no FX"). Never a bare dash, never 0, never an assumed value.
- Never label cost as market value. Planned (unfilled) entries never count as held.
- Direction-aware (long / short), instrument-aware (shares vs lots × contract multiplier), currency-aware.
- No data migration, no deletes. `render()` stays pure. English UI text. No overflow at 1440 / 1280 / 390.

## Known root causes (verify, then fix)
- Today row `#29 · ฿36.1k · 0.72% · cap 50%` comes from `tw1SizeRisk` → `plan.ps1.qty / riskMoney / riskPct`: planned total shares and planned loss at stop for the whole plan. Not holdings, not value. `cap 50%` = homework limit on total size (WL1); it scales nothing.
- "Fix risk ›": `td3PlanStatus` returns `incomplete` with an empty list when all fields exist but sizing fails; the reason is in `pb2Calc(i).msg` / `c.re1.reasonTexts` and is dropped.
- "⚑ Ready" is a manual flag, independent of validity → can show with "Fix risk".
- Flow cards: reason text is clamped + muted (`.bd-av`); grid stretches all cards to the open one.

## Part A — numbers (commit 1)
**A0 · Verify first, write to `docs/reports/PV1-progress.md` before changing code:** for one real Compounder holding in a fixture copied from the actual stored shape (lots + plan.ps1), list filled lots (qty, price, date), planned rows, stop, price + its date, FX used, and reproduce the currently displayed row from those inputs. Confirm or correct this reading: 11 sh filled @158, 18 planned @140, stop 110, FX 33.8 → (11×48 + 18×30) × 33.8 = ฿36.1k. If stored data disagrees, report and stop Part A.

**A1 · Shared helper `posView(item, acct)`** (one place, used by Today, Plan board, drawer) returning, each with `null` + reason when unavailable:
`heldQty`, `plannedQty` (all rows), `avgEntry` (fills only), `cost` = Σ fill qty × fill price × mult × FX, `price` + `priceAt` + `priceSrc`, `value` = heldQty × price × mult × FX, `weightAcct` = value ÷ account equity (same equity basis the risk % uses), `weightPool` = value ÷ strategy pool, `uPnl` and `uPnlPct` (vs cost), `openRisk` = loss at the current stop on held quantity only (reuse the engine's idea exposure; ≤ 0 → "none · stop at or beyond entry"), `openRiskPct` of account, `toStop` = held × |price − stop| × mult × FX, `plannedRisk` + `plannedRiskPct` (whole plan), `R` + `rUnit` (entry − first stop), `fx` + `fxSrc`.

**A2 · Holding row format (Today › Manage and wherever the same row is used):**
`#11/#29 · ฿60.5k · 1.2% · open risk ฿17.8k`
= filled / total planned (no unit; single entry or fully filled → `#11`), market value, % of whole account, current open risk on held shares. Satellite uses lots: `0.02/0.05 lot`. No price → `value: no live price` and keep `open risk`. Homework note stays as text ("size limited to 50% · homework not done"), never as a number in this row.
Planned / Ordered rows keep planned size + planned risk, labelled: `plan #29 · risk ฿36.1k · 0.72%`.

**A3 · Tests (node, focused):** long + short; partial 1/2 fill; multiplier ≠ 1; missing price; missing FX; stop beyond entry; the two illustrative cases reproduce exactly when supplied (29 × 158 × 33.5 = 153,497 · 11 × 158 × 33.5 = 58,223); planned rows never change `heldQty`, `cost`, `value`.

**A4 · Satellite optional "Last price":** one optional field on a Satellite plan / holding (form + drawer), blank by default, stored with the time typed. When set: `value`, `uPnl`, `toStop`, "to entry %" are shown with "manual · <date time>"; older than 24 h → amber "old price". **Display only** — it must not feed sizing, gates, limits, Today › Enter or any engine input. Blank → "no live price".

## Part B — Flow "Which asset moves this week · why" (commit 2)
- Cards size independently (no stretch). Short text: normal text colour, max 3 lines, then `Details ▾` / `Close ▴` (real buttons, keyboard + 44 px tap).
- One full-width detail panel under the row for the selected asset (iPhone: directly under the tapped card); one open at a time. Content, only from stored data:
  - Why it matters this week — full Weekly Impact `note`, plus `carryover_th`.
  - Catalysts — each `event_refs` item: time (ICT, or date / "ongoing"), title, forecast / previous when present, and its `interp` (mechanism, scenarios, watch).
  - Quarter view (Playbook) — bias, `why`, `change_if`, and any other Playbook field for that asset the UI omits today.
  - Sources + Weekly Impact `asof`.
  - "Your note · this week" — the existing textarea, visually separate from research; saving unchanged.
- No Playbook → compact box "No Playbook for <asset> · Add ›" (existing add / link action). No Weekly Impact → existing empty text. Generate nothing.
- Existing notes, ★ focus and week switcher keep working.

## Part C — Planned / Holding cards on the Plan board (commit 3)
All numbers from `posView` / `pb2Calc` / `plan.ps1` (Part A).
- **Header:** symbol · strategy tag · `Long` / `Short` chip · state.
- **Planned, always visible (6):** Entry · Stop + distance (pts or %) · Target + R:R · Size + position value · Loss at stop (money + % of account) · To entry (% or "no live price"). Multi-entry: stages with size per stage under More.
- **Blocked plan:** red `Blocked` chip replaces ⚑ Ready (flag cannot be set while blocked; an existing flag is shown off, not deleted); a line "Can't place: <first reason text from the sizing result>"; button names the fix (`Fix stop ›`, `Fix size ›`, `Complete ›`). Size / loss show "not sized". Remove the generic "Fix risk" / "Risk / size not OK" wording everywhere (Today too).
- **⚑ Ready** tooltip / help line: "You marked this plan ready to enter."
- **Holding, always visible (6):** Held + avg entry · Price + date · Value + weight · Unrealised P&L (money + %) · Stop + loss vs entry if stopped · Entries done / total + next entry (price, qty).
- **More ▾ (both):** cost of filled shares with the FX line; loss vs entry if stopped (% of account); from today's price down to the stop (labelled separately); R with its definition; whole-plan risk + % of account; % of strategy pool; applicable size limits and whether exceeded; FX source ("Settings rate, not live").
- Do not validate stop side without direction: short with stop above entry is valid.

## Tests / proof
- Node tests of A3. Browser suite `tests/run_tests_pv1.py`: row format; values equal across Today, Plan card, drawer for the same item; blocked plan shows the reason and no Ready; short plan valid; Sat with / without last price; Flow panel shows full text, one panel, neighbours keep height, note still saves, no-Playbook state; no overflow 1440 / 1280 / 390.
- `tests/run_regression.sh` must not get worse (same failing set as base, or fewer).
- Screenshots (`git add -f`): `pv1-today-1440/390`, `pv1-flow-open-1440/390`, `pv1-plan-1440/390`, `pv1-holding-more-390`.

## Report — `docs/reports/PV1-summary.md`
Root causes confirmed (with the A0 reconciliation) · what changed · formula + meaning of each metric · what was verified · data still unavailable · any policy question found (isolate it, ask, keep the independent fixes).
