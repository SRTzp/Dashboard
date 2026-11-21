# PC2 · Planned entries count as one plan + one simple card pattern for the whole Plan board (Sat · Momentum · Compounder) + drawer

Found 21 Nov 2026 (NVDA Compounder: plan ① 158 × 4 + ② 140 × 7; after ① filled, `Place ②` failed with “Thesis not complete — Add-on / further buys need it”). Spec: mockups `docs/briefs/lr/PlanBoardV2.html` (whole board, all strategies — wins on layout) `docs/briefs/lr/PlanCardV2.html` (Compounder card + drawer details) and `docs/briefs/lr/MomentumPlaceExit.html` (2f Place sheet + Top up, 2g exit row and Momentum cards — wins for those parts). git fetch, branch from fresh origin/main (`claude/pc2`); build after FS2 is merged (or rebase on it).

## 1. Logic fix (engine + adapter)
- Today `re1CardModel` sizes any Compounder buy after the first fill as `kind:'addon'`, and add-ons need the thesis (`ADDON_THESIS`). Wrong for rows that were **in the plan before the first fill**.
- New rule: a plan row that existed **before the first fill** is part of the plan’s first build: no `ADDON_THESIS`; it is sized/checked against the **Compounder total** (Settings, default 1.00 %) × homework factor (see 2e: Compounder 100 %, Momentum 70 % until done) × regime factor, counting the risk of filled rows at their current stop (same total-risk rule as today). Rows **added after the first fill** stay add-ons (thesis required, as today).
- Store `createdAt` per plan row (backfill: rows without it and present in the plan’s first saved version count as planned; if unknown, treat as planned when the plan was created before the first fill date).
- Block / allowed texts say the real limiting rule with numbers, e.g. `Risk 0.36% is over today’s limit 0.24% (0.40% × homework 100% × risk-off 60%)`, `Fits: total 0.27% of 0.30%`, `Allowed now #3 (plan has 7)`.
- Never resize saved plans or fills.

## 1b. Show the saved plan, not a re-sized one
- Planned rows show the **saved** quantity (e.g. ② `#18`), never today’s re-computed size. Today’s allowance appears only in the next-step line / drawer (`Allowed now #x (plan has #18)` or `Can’t add today · 0.36% over 0.30%`). (The NVDA drawer showed 4 / 7 while the saved plan was 11 / 18 — confusing.)

## 2a. Board layout (all strategies)
- Same 4-line card for Sat, Momentum and Compounder (see 2). Line 1 right side: planned → distance to entry (`0.3% to entry`); ordered → `order placed d ago`; holding → P&L `$ · R` (Sat without a price → `no price`).
- Line 2 levels: `#size · entry → target · stop` (Sat), `#size · entry · stop · T1 (sell #n)` (Momentum, see 2g; trigger text moves to the drawer), `#held @ avg · stop` (holding). Sat “Buy/Sell” leg chips are replaced by `entry → target` (Short reads 74,700 → 71,000). Multi-entry plans add ① ② chips; single-entry plans don’t.
- Line 3 money: planned `Risk −$ · reward +$ · nR`; holding `If stopped −$ · %` or `Locked +$` when the stop is above entry, plus value.
- Line 4 next step with one button: `✓ Ready` + Place order · homework (`Homework 1 of 2 · full size #34 when done` + Homework ›) · fix (`⚠ Needs BTC min stop` + Set in Settings ›) · holding (`Move stop`, `Last price`, `Why ›` when adds are blocked).
- **Blocked = amber with the fix named**, not a red “Blocked” chip + red box (red only for money lost).
- **Flexible column widths:** columns with cards share the width equally; an empty column becomes a slim column (~240px, never hidden, never squeezed below that) with one helpful line (`Nothing waiting at the broker. Placed orders show here until they fill.`). Cards: 14px padding, 8px line gap; no line may overflow at 1280/1440 (test). Phone: one column with sticky section headers. ✕ (cancel plan) stays top-right on planned cards.
- The drawer for every strategy uses the grouped layout in 3 (Sat: “Setup check” — EMA50 / structure — instead of Homework).

## 2c. Place is always available on planned cards (found 21 Nov: Momentum plan saved → no Place)
- Today `bdPill` shows `Place ›` only when `nearEntry(it.pct)` (`NEAR_ENTRY_PCT = 3`); further away the card shows `Edit`. Momentum entries are usually buy-stops above price, so right after planning there is no Place. Stop/limit orders can sit at the broker from day one.
- New rule: every **planned** card that is complete and not blocked shows `Place order` / `Place ②`:
  - within 3% of entry → **primary** (dark) button, as today;
  - further away → **plain (secondary)** button, and line 1 shows the distance (`5.2% to entry`) so the user sees it before tapping.
- `nearEntry` / 3% keeps controlling only **ordering** (top of the column), **Today › Enter** and the **teal tint**. It never hides Place.
- `Edit` leaves the card's button slot → ⋯ menu and drawer footer (`Edit plan`).
- Blocked cards keep the disabled Place + named fix (2 / 4). Incomplete plans (missing stop/size) show the fix instead of Place.
- AU2 “Place order now / Later” at Save plan is unchanged; when the remembered choice is Later, the toast after Save says `Saved · Place order anytime from the card` (no silent skip).

## 2d. Compounder: choose risk per plan (default 1%, max 2%)
- Everything else stays as today. Only Compounder plans get a per-plan risk choice; Sat and Momentum unchanged.
- Plan editor (Compounder only): the existing risk line gets one small select `Risk 1.0% ▾` with options 0.5 · 0.75 · **1.0 (default = Settings Compounder total)** · 1.25 · 1.5 · 2.0 %. Same style as the other plan-editor fields (light, Inter, tabular numbers); no new section, no new page.
- Options above 1% are enabled only when **both**: homework for that stock is done, and fewer than **2** other open Compounder plans/positions use more than 1%. Otherwise they show disabled with one muted line under the select naming the reason (`Above 1% needs homework done (1 of 3)` / `Already 2 plans above 1%`).
- The chosen % replaces the Compounder total for that plan in the existing sizing: plan % × homework factor × regime factor, counting filled rows at their stop (same rule as section 1). Heat 6 %, value cap 12.5 %, the 6-loss lock and emergency rules apply unchanged; when the value cap is what limits size, the next-step line says so (`Capped by value 12.5%`).
- Store `riskPct` on the plan (absent = default, so old plans behave exactly as today). Never resize saved plans or fills when the choice changes; the new % applies to unfilled rows only after Save.
- Card: only when the plan is not 1%, line 3 adds a small neutral tag `Risk 1.5%`. Drawer › Risk today formula shows it (`1.50% × homework 100% × risk-on 100%`).
- Constants in code (not in Settings): `COMP_RISK_MAX = 2.0`, `COMP_HIGH_MAX_OPEN = 2`.

## 2e. Homework factor per strategy (replaces the single 50 %) — decision 21 Nov
- **Compounder:** no homework → **full size** (plan % , default 1 %). Homework done unlocks (a) risk above 1 % (2d) and (b) add-ons (`ADDON_THESIS`, as today). Planned zones before the first fill stay part of the first build (section 1) and need no homework.
- **Momentum:** no homework → **70 %** of full size (0.40 % → 0.28 %); homework done → 100 %. Add-ons on Momentum also need homework done (same rule/text as Compounder).
- **Add-on risk rule (both):** an add-on fits only if total risk of the position (filled rows at their current stop + the new row) ≤ the plan's budget today (plan % × homework × regime). In practice: move the stop up first. Block text names the fix: `Add needs homework (1 of 2) ›` or `Add needs stop ≥ 152 (now 120) · Move stop ›`; fits → `Fits: total 0.80% of 1.00%`.
- Replace RK1's single homework cap 50 % with per-track factors in `POLICY` (`hwFactor: {comp: 1.00, mom: 0.70}`); the RK1 Settings “Homework cap 50 %” row shows the two values instead (`Homework not done: Momentum 70% · Compounder 100% (adds locked)`, read-only, same style). Grep for `50% until` / homework cap / the old factor and update every place (Homework page footer, card, drawer, Today hints). Sat unchanged (no homework).
- Card / drawer text:
  - Momentum not done: `Homework 0 of 2 · full size #34 when done` + `Homework ›` (existing pattern, 70 %).
  - Compounder not done: no size warning; holding cards show `Homework → unlocks adds & risk above 1% ›` in the next-step line (neutral, not amber).
  - Drawer › Homework: `0 of 3 · adds locked until done` (Comp) / `0 of 2 · size 70% until done` (Mom).
- Existing saved plans/fills are never resized; the new factors apply to unfilled rows.
- Where the mockups or older briefs say “50 % until homework is done”, **2e wins** (also the Homework page footer `Size: 50% until homework is done` → `Momentum: 70% until done` / `Compounder: adds & risk above 1% unlock when done`).

## 2f. Momentum: do homework at Place, top up later (keep timing and size)
- **Place order sheet (Momentum, homework not done):** under the size line `Buy #12 @ 100 · 70% · homework not done` show one link `Fill 2 lines → full size #17 ›`. It unfolds the two Momentum homework fields (What would change my thesis · Trigger — same fields/validation and same storage as the Homework page) inside the sheet. When both are valid, homework is saved as done and the size updates live to #17; Place uses the new size. Ignoring it and pressing Place sends #12 as today. No extra step when homework is already done.
- **Top up within 5 trading days:** if a Momentum position was entered at 70 % and homework is done within 5 trading days of the first fill, the card next-step shows `Top up to full · #5 ›` (secondary). It counts as part of the first build (section 1), not an add-on: no stop-raise rule; sized so total risk (filled at current stop + top-up at the stop) ≤ full budget × regime today. After 5 trading days it disappears and normal add-on rules (2e) apply. Constant `MOM_TOPUP_DAYS = 5`.
- Compounder: unchanged (already full size without homework).

## 2g. Momentum exit = sell part at Target 1, trail the rest
- Plan editor (Momentum) replaces “Targets optional · display only / Target 1 / Target 2 / Shares at target 1” with one row: `Target 1 [120]  Sell at T1 [50 %▾ | #]  · rest: trail stop`. Target 2 removed (old saved T2 kept in data, not shown). Hint (muted, one line): `Used for reward/R and the T1 sell. Rest exits by your trailing stop.` Target 1 stays optional; empty → no reward/R shown.
- Default sell at T1 = 50 % of the position (rounded down to whole shares, `#8` of `#17`); user can type a % or a share count.
- Card (planned): line 2 `#17 · entry 100 · stop 90 · T1 120 (sell #8)`; line 3 `Risk −$170 · reward at T1 +$170 · 2.0R`. **No Buy/Sell chips for Momentum** (they read as placed orders).
- Card (holding, T1 not hit): line 2 adds `T1 120 · sell #8`; Place-order sheet offers `Place T1 limit sell #8 @ 120` as an optional second order (one tap, same sheet pattern).
- After the T1 sell is filled/logged: card shows `T1 done +$170 · #9 left · trailing`, and the next-step line suggests `Move stop to breakeven 100 ›` (a suggestion, never automatic). Further exits via existing Move stop / Close trade.
- Sat targets unchanged (entry → target per 2a).

## 2. Card (Plan board, all widths) — 4 lines
1. Ticker · track tag · status · P&L ($ and R).
2. `#held @ avg · stop · if stopped −$x (y%)`.
3. Entries as chips `① 158 · #4 ✓` / `② 140 · #7` (dashed when planned); a fill different from the plan shows `plan 4` muted. **Share counts are written `#n` (e.g. `#4`, `#12`); entries are numbered ① ② (circled), so `#` only ever means a share count.**
4. **Next step**: fits → `✓ ② fits · total risk 0.27% of 0.30% today` + `Place ②`; doesn’t fit → `⚠ Can’t add · <reason>` + disabled `Place ②` with the reason as tooltip. The homework chip shows once (in the reason or as `Homework 0/3 ›`).
- `More ▾` removed from the card (all detail lives in the drawer).

## 3. Drawer — grouped, same facts
- **Risk today:** one sentence (now / with next entry) + meter (now · with next entry · today’s limit marker) + the limit’s plain formula.
- **Entries table:** # · price · shares · loss at stop · status / `Place ②` (primary when it fits; disabled + reason when not).
- **Position:** held, avg, price + date, value (% of account, % of strategy pool), P&L ($, %, R), stop (% below entry, 1R per share).
- **Homework:** `0 of 3` + bar + the 2e text (`adds locked until done` / `size 70% until done`) + `Open ›` (replaces the old Why buy / Wrong if box).
- Folded: **Formulas & FX ▸** (every row from today’s “More” list: cost of filled shares × FX, loss vs entry, from today’s price to stop, 1R maths, whole plan, size limits, FX source) · **Log (n) ▸**.
- When blocked, an amber box on top: reason, what fixes it (homework → unlocks adds / full Momentum size, regime → limit, stop not raised → `Move stop ›`), primary `Do homework ›` (stocks) and `Edit plan`.
- Footer: Update levels · Close trade · Edit plan.
- No dark toast for a blocked Place (the reason is shown before the tap). Light theme, tabular numbers, dates in Inter (no mono).

## Proof
- Engine selftest: planned ② after ① fill → no ADDON_THESIS, sized by total × homework × regime; homework factor comp 1.00 / mom 0.70 (not done) → 1.00 (done); add-on blocked until homework done and until total risk with the new row ≤ budget (stop moved up → fits); row added after the fill → ADDON_THESIS as before; over-limit text with numbers; saved plans/fills unchanged.
- `tests/run_tests_pc2.py`: saved qty shown (not re-sized) · Sat entry → target wording incl. Short · amber blocked with named fix · empty column strip · same card pattern per strategy · card 4 lines (fits / blocked / fill ≠ plan), ①② for entries and `#n` for share counts everywhere (no “sh”, no “Buy #”), drawer groups + meter values, folded Formulas & FX contain every old row, Place disabled with reason, Place visible on a complete planned Momentum card at 0.5% (primary) and 6% (secondary + `6.0% to entry`) from entry · far cards not on Today › Enter · Edit in ⋯ menu · Later toast text · Compounder risk select (default 1%, >1% disabled with reason when homework not done or 2 plans already >1%, 1.5% sizes ×1.5, value cap still limits, old plans unchanged, `Risk 1.5%` tag only when ≠ 1%) · 2e: no-homework Compounder plan sized at full default, no-homework Momentum at 70%, add blocked without homework / with stop not raised (named fix) and allowed after, Momentum 70% line, Compounder `unlocks adds & risk above 1%` line, no “50% until” text anywhere · 2f: Place sheet `Fill 2 lines → full size` saves homework and resizes #12→#17 live; Place without it sends #12; Top up shown ≤5 trading days after first fill when homework done, sized to full budget, gone after day 5 · 2g: Momentum editor single T1 row with sell 50% default (% or #), T2 hidden, card `T1 120 (sell #8)` and reward at T1, no Buy/Sell chips on Momentum, T1 limit-sell option, after T1 `#9 left · trailing` + breakeven suggestion, 360/390/1440 no overflow.
- Side-by-side vs the mockup (`tests/screenshots/pc2/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/PC2-summary.md`. No unrelated PNGs.
