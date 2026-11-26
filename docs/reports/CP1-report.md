# CP1 report — Compounder first when the market pulls back

Branch `claude/cp1` (from origin/main 971865d, RX1 merged). Commits: brief+mockup · A data · B engine · C Today · D Homework+Watch · E tests (+ review fix).

## Tests (final commit, `JOBS=2 bash tests/run_regression.sh`)
- Full regression: **104/104 ok**, 0 failing (3919 s). Hooks superset: **pass**.
- e2e1 (incl. new J9): green. rx1 110/110. cl2 49/49.
- New: cp1 suite **96/96** · cp1 engine 15/15 · prices-job selftest 104 checks (rs2_selftest) · J9 (pullback → Make plan → Pilot 100%; both red → 75%) 11/11.
- Updated for the intended UI/engine change: re1c_live, pc2_engine, rm1_engine (Compounder one red = 100%), nt1d guard (only CP1 lines allowed in the engine files), lr2 / nt1b (MARKET row, "Pullback" instead of "Mixed"), hw1 (optional Buy zone chip).

## Judgment calls
1. Brief said the old table was 100/75/50; the engine had 100/80/60. Compounder is now 100/100/75 (`COMP_REGIME_FACTOR`, one place); Momentum and Sat stay 100/80/60.
2. Stale / unknown regime data caps Compounder at 75% (never 100%).
3. Daily job also writes `last` (+`lastDate`) per Watch stock — "Now 905" needs a daily price; Watch stocks had none.
4. New Firestore rule needed for `users/{uid}/market/{doc}` (text in docs/firestore-rules-stockNotes.txt). Without it: MARKET shows "—", pullback falls back to the regime signals.
5. Pullback is per stock: US → SPY, Thai → SET; a SET-only dip lists Thai stocks only.
6. Stocks with a plan / order / holding are not repeated in the group; an Add-on row shown in the group is removed from Manage while the pullback lasts.
7. Normal market: summary line lists only in-zone stocks of markets that are not in a pullback.
8. Buy zone saves when focus leaves the box (not per field) so a snapshot re-render never eats typing.
9. Review fix (also on origin/main): a Homework page left open when changing tab came back under the list on phone / instead of it on desktop — `switchTab('watch')` now clears `hwSym` / `wl5FullSym`; tested at 1440 + 390.
10. Watch › Compounder: the two new columns narrow Sector / Thesis; thesis text wraps (no "…").

## PNGs (docs/screenshots)
- cp1-today-pullback-1440 · cp1-today-pullback-390
- cp1-today-normal-1440
- cp1-buyzone-1440 · cp1-buyzone-390
- cp1-watch-comp-1440 · cp1-watch-comp-390
