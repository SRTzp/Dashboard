# LR5c · Port tab (match the mockups)

Branch `claude/lr5c` from main (after LR5b, or own worktree + rebase).

## Rule
Spec: `docs/briefs/lr/PortBoth.dc.html` (1440) + `PortPhone.dc.html` (390). Same hook, engine, light-only and English rules as LR5a.

## Desktop
1. **Header row:** "Port" · `Main · Family · Both` · note "Read-only · plans, sizing and risk rules stay per account" (shown in Both).
2. **Three cards:**
   - Total value: household total in ฿ (FX from the shared settings) with a 2-colour bar M / F and `M ฿x · y% · F ฿x · y%`.
   - Open risk: total ฿ + `M x% of 3% · F x% of 3%` (the same per-account values as Today / Plan; never a combined %) + "Each account keeps its own 3% cap".
   - Futures leverage · F: `n×` + "S50 + GO notional ÷ Family equity" + cash per account. Hide the card when no futures are open.
3. **Holdings table:** Ticker + port tag · Main (#qty + value in account currency) · Family (#qty + value) · Total value (฿; futures = notional, labelled) · % of household · If stopped (฿, red). Sorted by total value. One line for the ticker, a muted second line for value under each qty.
4. Main / Family views: the same layout for one account, in that account's currency; the existing per-account sections (positions, ports, cash, settings links) stay reachable. Restyle, don't drop anything; anything that doesn't fit goes into `More ▾`.
5. All numbers come from existing functions (book, ps1E, lr2OpenRisk, lr2Futures, FX). No new maths; if a number has no source, show "—".

## Phone (390)
Follow PortPhone: account switch, the 3 cards stacked (compact), holdings as 2-line rows (ticker · tag · total / M qty · F qty · if stopped). The Port ＋ button must fit at 360 px (old backlog item).

## Proof (required)
- `tests/screenshots/lr5c/port-1440-side.png`, `port-390-side.png` (fixture: both accounts, a shared ticker, futures, a Thai stock), `port-1440-main-live.png`, `port-1440-family-live.png`.
- `tests/run_tests_lr5c.py` in `run_regression.sh`: household totals = sum of the accounts in ฿ (by hand), open risk per account equals Today's, futures leverage equals Today's, % of household sums to 100 ±0.5, no Thai in the Port tab, no overflow at 360/390/1440.
- `docs/reports/LR5c-summary.md`: remaining differences + reasons, full regression 0 failing. Commit in parts A–D.
