# PC2 · Planned entries count as one plan + one simple card pattern for the whole Plan board (Sat · Momentum · Compounder) + drawer

Found 21 Nov 2026 (NVDA Compounder: plan ① 158 × 4 + ② 140 × 7; after ① filled, `Place ②` failed with “Thesis not complete — Add-on / further buys need it”). Spec: mockups `docs/briefs/lr/PlanBoardV2.html` (whole board, all strategies — wins on layout) and `docs/briefs/lr/PlanCardV2.html` (Compounder card + drawer details). git fetch, branch from fresh origin/main (`claude/pc2`); build after FS2 is merged (or rebase on it).

## 1. Logic fix (engine + adapter)
- Today `re1CardModel` sizes any Compounder buy after the first fill as `kind:'addon'`, and add-ons need the thesis (`ADDON_THESIS`). Wrong for rows that were **in the plan before the first fill**.
- New rule: a plan row that existed **before the first fill** is part of the plan’s first build: no `ADDON_THESIS`; it is sized/checked against the **Compounder total** (Settings, default 1.00 %) × homework factor (50 % until done) × regime factor, counting the risk of filled rows at their current stop (same total-risk rule as today). Rows **added after the first fill** stay add-ons (thesis required, as today).
- Store `createdAt` per plan row (backfill: rows without it and present in the plan’s first saved version count as planned; if unknown, treat as planned when the plan was created before the first fill date).
- Block / allowed texts say the real limiting rule with numbers, e.g. `Risk 0.36% is over today’s limit 0.30% (1.00% × homework 50% × risk-off 60%)`, `Fits: total 0.27% of 0.30%`, `Allowed now #3 (plan has 7)`.
- Never resize saved plans or fills.

## 1b. Show the saved plan, not a re-sized one
- Planned rows show the **saved** quantity (e.g. ② `#18`), never today’s re-computed size. Today’s allowance appears only in the next-step line / drawer (`Allowed now #x (plan has #18)` or `Can’t add today · 0.36% over 0.30%`). (The NVDA drawer showed 4 / 7 while the saved plan was 11 / 18 — confusing.)

## 2a. Board layout (all strategies)
- Same 4-line card for Sat, Momentum and Compounder (see 2). Line 1 right side: planned → distance to entry (`0.3% to entry`); ordered → `order placed d ago`; holding → P&L `$ · R` (Sat without a price → `no price`).
- Line 2 levels: `#size · entry → target · stop` (Sat), `#size · entry · stop · trigger: …` (Momentum), `#held @ avg · stop` (holding). Sat “Buy/Sell” leg chips are replaced by `entry → target` (Short reads 74,700 → 71,000). Multi-entry plans add ① ② chips; single-entry plans don’t.
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
- **Homework:** `0 of 3` + bar + `size 50% until done` + `Open ›` (replaces the old Why buy / Wrong if box).
- Folded: **Formulas & FX ▸** (every row from today’s “More” list: cost of filled shares × FX, loss vs entry, from today’s price to stop, 1R maths, whole plan, size limits, FX source) · **Log (n) ▸**.
- When blocked, an amber box on top: reason, what fixes it (homework → limit, regime → limit), primary `Do homework ›` (stocks) and `Edit plan`.
- Footer: Update levels · Close trade · Edit plan.
- No dark toast for a blocked Place (the reason is shown before the tap). Light theme, tabular numbers, dates in Inter (no mono).

## Proof
- Engine selftest: planned ② after ① fill → no ADDON_THESIS, sized by total × homework × regime; row added after the fill → ADDON_THESIS as before; over-limit text with numbers; saved plans/fills unchanged.
- `tests/run_tests_pc2.py`: saved qty shown (not re-sized) · Sat entry → target wording incl. Short · amber blocked with named fix · empty column strip · same card pattern per strategy · card 4 lines (fits / blocked / fill ≠ plan), ①② for entries and `#n` for share counts everywhere (no “sh”, no “Buy #”), drawer groups + meter values, folded Formulas & FX contain every old row, Place disabled with reason, Place visible on a complete planned Momentum card at 0.5% (primary) and 6% (secondary + `6.0% to entry`) from entry · far cards not on Today › Enter · Edit in ⋯ menu · Later toast text, 360/390/1440 no overflow.
- Side-by-side vs the mockup (`tests/screenshots/pc2/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/PC2-summary.md`. No unrelated PNGs.
