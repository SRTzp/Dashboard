# RS2a3 · Screen: undo/change after add · ←/→ presets · tick + TradingView .txt · Today alerts

Decided by SRTp 20 Nov 2026. Small follow-up to RS2a2 (merged). Can run in parallel with LT2/HW1 (different code areas); if HW1 is merged first, rebase on it. Spec: mockup `docs/briefs/lr/ScreenRS3.html` (A Screen · B Today · C phone) on top of the RS2a/RS2a2 Screen; side-by-side against it.

## 1. Undo and change after `+` (Screen)
- After `+` (row) or `+ Add to Watch` (detail): toast `Added NVDA to Momentum · Undo · Move to Compounder` for 8 s (one toast; a new add replaces it).
  - **Undo** deletes the Watch item only if this add created it and it hasn't been edited since (no plan, no homework, no notes); otherwise the toast says `Edited — remove it from Watch instead`.
  - **Move to Compounder** (or `Move to Momentum`) switches the track with the same field Edit uses.
- The muted `✓` on a row becomes a button: click → small menu `Momentum ✓ / Compounder` (switch) · `Remove from Watch` (same guard as Undo; edited items → disabled with the reason) · `Open in Watch ›`.
- Detail panel when already on Watch: `On Watch · Momentum ✓` + a `Change ▾` with the same menu.

## 2. ←/→ switches presets on Screen (desktop)
Leaders ↔ Emerging ↔ Pullback, stop at the ends (no wrap). Same guards as the other keys (not while typing, menus/sheets open). Other tabs unchanged (←/→ keep changing thesis card tabs).

## 3. Tick + download for TradingView
- Desktop: a checkbox column first; header checkbox = all rows **shown** (current preset/filter, incl. loaded "Show more" rows); **Shift+click** selects the range from the last clicked row. Selection clears when the preset or filters change.
- When ≥ 1 ticked: a bar above the table `12 selected · Download for TradingView (.txt) · Add to Watch · Clear` (Add to Watch → Momentum, skips names already on Watch, one summary toast with Undo for the batch).
- File: plain text, one line, comma-separated `EXCH:SYMBOL` (from the row's exchange: `NASDAQ` · `NYSE` · `AMEX`; TradingView symbol form, e.g. `NYSE:BRK.B`), no trailing comma. Name `screen-<preset>-YYYY-MM-DD.txt`.
- Phone: no checkboxes; the header menu gets `Download shown list (.txt)` (all rows in the current preset/filter).
- ↑/↓ (HW1) still moves the selected row; Space toggles the tick of the selected row.

## 4. Today alerts from Screen changes
- **Job** (`build_rs2.py`): compare today's rows with the previous run and write `rs2/changes` = `{asOf, prevAsOf, items:[{sym, k, from, to}]}` (≤ 30 items, compact). Missing previous run → empty list.
  - `a` **new 52w high** for a stock on Watch (Watch tickers already passed to the job).
  - `b` **left Leaders** for a stock on Watch (RS < 80 or > 15% from high, using the Leaders thresholds; was in yesterday).
  - `d` **new Leader, RS ≥ 90**, not on Watch (top 3 by RS).
  - Also computed, off by default: `c` Watch stock RS −15 or more vs 4 weeks ago · `e` new Emerging name (top 3).
- **App:** Today's existing list gets up to 3 lines (no new panel), priority b → a → d, e.g. `PLTR left Leaders · RS 78` · `GE new 52w high` · `New Leader: CRDO RS 95`. Tap → Watch › Screen with that row selected. Hidden after viewed once per `asOf`. Settings › Screen alerts: toggles a–e (a, b, d on).
- If HW1 is merged, the Watch stock's homework state isn't involved; alerts are display only, never a gate.

## Proof
- Tests (extend `run_tests_rs2a2.py` or new `run_tests_rs2a3.py`): Undo (new item / edited item), Move to Compounder, ✓ menu, ←/→ preset + ends + typing guard, tick + shift-range + header + clear on preset change, `.txt` content and name (incl. BRK.B), phone download, Today lines (each kind, cap 3, priority, seen-once, settings off), 360/390/1440 no overflow.
- Selftest: changes diff (each kind, no previous run, cap 30).
- Side-by-side PNGs `tests/screenshots/rs2a3/` (`git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · RS2a3 section in `docs/reports/RS2a-summary.md`.
