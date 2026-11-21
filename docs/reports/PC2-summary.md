# PC2 — Plan board + plan card redesign · planned-entry logic fix · Place always available · Compounder risk · homework per strategy · Momentum homework-at-Place / top up / T1 exit

Branch `claude/pc2` (from origin/main incl. FS2). Not merged.

## What changed
**Engine / adapter (`risk-engine.js`, `re1-adapter.js`, synced into `index.html`)**
- New sizing kind `plan` (first build): rows that were in the plan *before the first fill* need no `ADDON_THESIS`; sized/checked against plan % × homework factor × regime, counting filled rows at their current stop. Rows added after the first fill stay add-ons (thesis + total-risk rule; the old "0.50 % alone" cap is gone for the new path).
- `POLICY.hwFactor = {comp: 1.00, mom: 0.70}` replaces the single 50 %; `compRiskMax 2.0`, `compHighMaxOpen 2`, `momTopupDays 5`.
- Per-plan `riskPct` (absent = Settings default). Block / fit texts carry numbers: `Risk 0.36% is over today's limit 0.24% (0.40% × homework 100% × risk-off 60%)`.
- Momentum: planned rows after a fill, add-on rule (homework + total risk ≤ budget), top-up (first build, full budget).
- Saved plans and fills are never resized; `createdAt` is stamped per plan row on save (absent = planned).

**Plan board / card / drawer (`index.html`)**
- One 4-line card for Sat · Momentum · Compounder (levels · money · next step + one button); saved quantities only; `①②` chips for multi-entry, `#n` for share counts; blocked = amber with the fix named.
- Place is always on a complete, unblocked planned card (primary ≤ 3 %, secondary + `x.x% to entry` further out); Edit moved to the ⋯ menu / drawer; Today › Enter still only takes plans within 3 %.
- Flexible columns (empty column = slim 240 px strip), phone = one stacked column with sticky headers.
- Drawer grouped: Risk today (meter + formula) · Entries · Position · Homework / Setup check · folded Formulas & FX · Log; amber box when blocked.
- Compounder editor: `Risk 1.0% ▾` (0.5 … 2.0; above 1 % needs homework done and < 2 other plans above 1 %); card tag `Risk 1.5%` only when ≠ 1 %.
- Homework factor per strategy everywhere (Settings read-only line, Homework page footer, cards, drawer, Today hints, WL1 cap).
- Momentum: Place sheet `Fill 2 lines → full size #n ›` (same fields/storage as the Homework page; size updates live), `Top up to full · #n` within 5 trading days, single `Target 1 · Sell at T1 [50 % | #]` exit row, `T1 120 (sell #8)` on cards, `Place T1 sell` sheet, after T1 `#9 left · T1 done · trailing` + breakeven suggestion.
- FS2 nits: Homework header "reported <date>" no longer truncated; AI fold-out headings `1 · The business / 2 · Why it could be worth buying / 3 · What's next / 4 · When to exit`.

## Proof
- `node tests/pc2_engine_test.js` — engine selftest (18 assertions).
- `python3 tests/run_tests_pc2.py` — browser suite (board, drawer, Place availability, Compounder risk, 2e, 2f, 2g, 1440/1280/390/360), added to `run_regression.sh`.
- Side-by-side vs the mockups: `tests/screenshots/pc2/` (board 1440 / 390, drawer, Place sheet, Momentum cards; editor live shot).
- Hooks superset PASS (kept `cnTp2`/`cnTp1Qty` as hidden inputs, `pvCardTap`, `data-pv-fixbtn`).
- Older suites updated to the new rules (70 % homework, new card/drawer structure): pv1, re1c, re1c2, lr3, lr5a, ef1b, sd1, hw1, phase373, phase374, risk_engine.

## Notes
- Brief §1 example numbers use sample data; the NVDA fixture (real card) now shows `✓ ② fits · total risk 0.72% of 1.00% today` and Place ② works.
- The Momentum card keeps the amber Homework link next to Place (mockup MomentumPlaceExit); on narrow cards Place wraps to its own line.
