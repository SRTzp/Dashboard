# RE-C1 — cut-over summary (2026-11-15) · branch `claude/re1c1`

## §0 — RE-B follow-up (NVDA, Compounder, holding): qty 7 ≈ 0.25%, reasons HOMEWORK_50 + EQUITY_PROXY
**Cause (confirmed in the code):** `engineSize` in `re1-adapter.js` treated the Compounder like Momentum: base = Pilot 0.50% **and** `frac = 0.5` (homework not done) → 0.50% × 50% = **0.25%**, and the regime factor was never applied.
**Correct arithmetic** (decisions §4): the homework cap for a Compounder is a *phase cap* — "thesis incomplete → Pilot only" — i.e. the Pilot (0.50%) **is** the 50%. It is never a second multiplier. The regime factor applies to NEW entries (`min(Regime, Emergency)`).
`Pilot 0.50% × regime 75% = 0.375%` (one signal red) · `× 100%` = 0.50% (both green) · Starter ON: `× 50% (starter ¼ of the plan)`.
For the NVDA row that is 0.375 / 0.25 = **1.5× the dry-run size (≈ 10 shares at regime 75%, ≈ 14 at 100%)**, not 7.
**Fixed:** homework multiplier removed for the Compounder; regime / emergency / Starter applied; every result now carries the named factors (`PILOT_0.5`, `REGIME_75`, `EMERGENCY_50`, `STARTER_25`, Momentum `HOMEWORK_50`, Satellite `STEP_n`, `CONDITION_65`). Tests: `tests/re1c_live_test.js`, `run_tests_re1c.py`.

## Owner amendment applied (Add-on rule, final)
Add-on / further buys = **total-risk rule only**: thesis done + (existing tranches at current stop + working orders + new order) ≤ 1.00% of week-start equity for the ticker (0.50% without thesis) + new order alone ≤ 0.50% × min(Regime, Emergency). Entry above or below the average entry; below → one warning line "Adding below entry — re-check ④ Wrong if" (`ADDON_BELOW_ENTRY_WARN`, never a block). Multi-entry plans are sized so all levels stay within the cap in force. Removed from engine, reason codes, form text and tests: +1.5R, breakeven stop, at-or-above-entry (`COMP_PILOT_R`, `COMP_PILOT_STOP`, `COMP_TOPUP_STOP`, `COMP_THESIS` → `ADDON_THESIS`, `ADDON_TOTAL_RISK`). Momentum's net-breakeven release (Option C) unchanged.
