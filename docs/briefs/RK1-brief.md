# RK1 · Risk per idea in Settings (new values) + hide unused settings

Decided by SRTp 20 Nov 2026 after a risk-of-ruin comparison (fixed risk, lower values, Sat ladder removed — the ladder raised risk after losses, which also makes entering harder). Spec: mockup `docs/briefs/lr/SettingsRisk.html`. git fetch and branch from fresh origin/main (`claude/rk1`).
Lean UI: one line per row, no new panel beyond the one section, no primary button, English UI.

## 1. New risk values (engine `POLICY`, used for new plans only)
| | Now | New default |
|---|---|---|
| Compounder | pilot 0.50 · total cap 1.25 | **pilot 0.50 · total 1.00** |
| Momentum | 0.45 per idea | **0.40** |
| Sat | step ladder 0.20 / 0.30 / 0.30 / 0.40 (steps up after a loss) | **fixed 0.20** (keep the weekly lock after the 4th loss; the step machine stays, every step = the Sat value) |
- Derived limits follow the per-idea value (no separate setting): weekly = 4 × per-idea (Momentum 1.60, Sat 0.80); monthly = 4 × weekly (6.40 / 3.20). Momentum `ammo` 4 unchanged.
- **Loss-streak rules stay as they are and must agree with the new values:** Momentum max 4 losing ideas per week (`ammo`, AMMO_EXHAUSTED) · Sat locked for the week after the 4th loss · Compounder locked after 6 consecutive losing ticker-cycles, unlock after 7 days. The weekly budgets are derived as 4 × per-idea so the money check and the count check stop at the same point (a loss bigger than 1R from slippage can still use the budget up before the 4th loss — same as today; show which rule stopped it).
- Unchanged: regime factor 100/80/60 (fallback 80), emergency half size from −10 % and stop at −20 %, Compounder heat 6 % and value cap 12.5 %, homework cap 50 %, min stops (Momentum 4 %, Compounder 7 %, Sat per asset).
- **Never resize saved plans or holdings.** Plans saved before RK1 keep their stored risk/qty; only new plans and edits that increase risk use the new values.

## 2. Settings › Portfolio & Risk › “Risk per idea” (top of that section)
- Rows: Compounder total + First entry · Momentum · Sat (fixed). 2-decimal % inputs. Bounds: Compounder total 0.50–1.50 with first entry ≤ total · Momentum 0.20–0.60 · Sat 0.10–0.40; out of bounds → inline message, not saved. `Reset` → 1.00 / 0.50 / 0.40 / 0.20.
- Muted derived box (read-only): weekly limits, “Applies to new plans …”, and the engine modifiers still applied.
- One set for both accounts (stored with the existing shared settings; no new collection). Replace the line “risk limits now come from the engine” with this section.
- Every view that shows risk % (plan form, Plan board, Today, Port, drawer) reads the same values (no hard-coded 0.45 / 1.25 / step labels left in the UI; Sat step labels like “Step 2 · 0.30 %” become just the value; the weekly lock message stays).

## 3. Hide unused settings (UI only — keep the stored data)
- **Daily routine** (incl. Sat daily check XAU/BTC/S50/Brent, other daily tasks, weekly tasks): hide the section; Today stops showing routine/weekly-task items and any routine % derived from them. Own to-dos (TD5) stay.
- **Sub-port goals:** hide the per-sub-port goal fields; keep the main account goal.
- **Key news days (Sat):** hide. The Sat news window (warn + forced size cut) and Today events read high-impact CPI / NFP / FOMC events from Weekly Impact (`wiDocs`) instead. No Weekly Impact for the week → no news window and a muted line in the Sat plan form `No news calendar this week`.
- **Sat rules › Advanced › Tactical TP1 / TP2:** hide (Tactical unused).
- List in the summary every function/view that read the hidden settings and what it does now.

## Proof
- Engine selftest: new defaults; Momentum 4th losing idea blocks at 0.40 (count and 1.60 % budget agree); Sat lock after 4 losses at 0.20 (0.80 % budget); Compounder 6-loss lock unchanged; Sat every step 0.20 + lock after 4 losses; weekly/monthly derived; old saved plan unchanged; override via settings; bounds.
- `tests/run_tests_rk1.py`: section render + bounds + Reset; values flow to the plan form sizing (Compounder pilot/total, Momentum, Sat) at 1440/390; no `0.45` / `1.25` / step-ladder labels in rendered UI; hidden sections absent; Today without routine items; news window from a Weekly Impact CPI event and absent without one; main goal still shown; 360/390/1440 no overflow.
- Update existing tests that asserted 0.45 / 1.25 / the ladder (list them). Side-by-side vs the mockup (`tests/screenshots/rk1/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/RK1-summary.md`. No unrelated PNGs.
