# PS1 — Portfolio & Risk (simple) · Phase 1: essentials only

Status: agreed scope 2026-11-07. Source: SRTp "Portfolio & Risk Rules — ฉบับเรียบง่าย".
Branch from main: claude/ps1. Audit first, wait for OK. UI copy: short Thai/English as today; NO formulas or field names on main screens (Details only).
Anything marked PARKED is not built in PS1.

## Rules to implement (from SRTp's spec, unchanged)
| Bucket (keys) | Weight | Target positions | Risk per idea (% of E) | Max position size (% of E) | Bucket risk cap (% of E) |
|---|---:|---:|---:|---:|---:|
| Core Compounder (`ladder`) | 50% | 4–5 | 0.80–1.25% | 10–12.5% | 3.0% |
| Core Momentum (`winner`) | 30% | 4–5 | 0.35–0.50% | 6–7.5% | 1.5% |
| Satellite (`sat`) | 20% | 2–3 ideas | 0.10–0.25% | by risk + stop | 0.5% |
- Total principal risk (all buckets) ≤ 5.0% of E. Each bucket ≤ its own cap.
- Target positions are a target only. If the budget is used up, the dashboard blocks new risk; it never forces filling.
- E (portfolio value) = the account's total value as the dashboard computes it today (each account separately, main and Family each have their own E). Use the existing USD/THB rate. Show E and its date.

## 1. Settings › Portfolio & Risk (one compact section)
- Bucket weights (50/30/20), per-bucket risk range + **default risk per idea**, max position size %, bucket risk cap, total cap 5%, give-back review band 8–10%.
- No hardcoded default risk: the default-risk field starts EMPTY; Add Trade shows "Set default risk in Settings" until filled (within the range).
- Replaces PL1's single "Base Risk 1% of pool" for NEW plans. Old plans/trades keep their stored numbers (same rule as PL1).

## 2. Add Trade / plan form (Momentum + Compounder)
**Main use = 1 entry + 1 SL. Multi-row is an optional extra. Keep the form lean.**
- Default form = exactly what a single trade needs: Entry · SL · Risk % (prefilled with the bucket default). Nothing else visible. No per-row %, no weights.
- A small, low-key "＋" next to Entry and next to SL (max 4 rows each, ✕ to remove). Only when a 2nd row exists:
  - Entry rows show a small risk % field each (parts of this idea's budget; SRTp's AAA example). Shares per row = row risk ÷ (row entry − stop), rounded DOWN. Sum of rows ≤ the idea's risk %.
  - SL rows show a small "% of shares" field each (must total 100). Risk uses the weighted exit (blended stop).
  - Removing back to 1 row hides these fields again.
- One summary line under the form: `Shares · Risk x.xx% · Size x.x% of portfolio`. With 2+ rows it also shows `Avg entry · Avg SL · Left x.xx%`. Nothing else on the form.
- Caps: total size ≤ max position size % of E (shares reduced to fit, one short note); bucket/total risk checked before Save. Over a cap → one-line reason, Save blocked.
- Existing regime/DD size multipliers: keep exactly as today (PARKED D1). Shown in Details only.
- **Layout: Entry · SL · Risk on ONE row, at every width incl. 390px. No overflow, no wrap.** Three equal-width compact inputs (grid 1fr 1fr 1fr, small gap), small labels ABOVE the inputs (not beside) to save width. The ＋ is a tiny icon in the Entry / SL label line, not a separate column. Summary line directly below: `2,000 sh · Risk 0.40% · Size 2.0% of portfolio`.
- Extra rows (after ＋) appear under their own column header in the same 3-column grid; they never push the first row wider.

## 3. Add-ons (pyramid)
- A NEW risk budget for an existing idea is allowed only when every existing tranche's stop is at or above its average entry (principal risk = 0). Otherwise the add-on uses what's left of the same idea budget.
- Re-check size cap and bucket/total risk caps on every add-on.

## 4. Satellite sizing (futures / CFD)
- Contracts/lots = (E × risk %) ÷ (|entry − stop| × contract multiplier), rounded DOWN to the broker's lot step. Single stop, full exit.
- Uses E (whole portfolio), not the sub-account balance. Show the sub-account's free margin next to it as information ("margin is not risk").
- Existing Sat rules (TP, min R:R, news window, EMA50/Structure verify) unchanged.

## 4b. Sat plan defaults + verify rule (added 2026-11-07)
- New Sat plans default to **Main** sleeve. Tactical stays available (unchanged rules), just not the default.
- Default TF for new Main plans = **4H** (existing plans keep their TF).
- Verify checkboxes (EMA50 Verify / Structure Verify) now drive Main entry + size:
  | EMA50 | Structure | State | Main |
  |---|---|---|---|
  | ✓ | ✓ | Clear Trend | 100% size |
  | ✗ | ✓ | Unclear Trend | **60% size** (risk budget × 0.6 → lots rounded down) |
  | any | ✗ | — | **Blocked**: "Check Structure first" — can't save as ready / enter |
- The 0.6 multiplies the Sat idea risk (after the existing f/DD multiplier, D1 parked). Summary shows "Size 60% (Unclear Trend)"; formula in Details only.
- Tactical keeps its current rule (needs Clear Trend).
- Legacy plans still on stored classify ("verification pending"): before a NEW entry they must tick at least Structure; already-entered trades untouched.
- Tests: ✓✓ → 100%; ✗✓ → 60% lots (rounded down); Structure ✗ → blocked; new plan defaults Main + 4H; Tactical unchanged; legacy pending plan blocked until Structure ticked.

## 5. Portfolio Risk panel (Port tab top + compact line on Today)
Show only:
- Portfolio value + each bucket's actual vs target weight.
- Principal at risk: per bucket (x.x% of cap) and total (x.x% / 5%), and **Risk budget left** (total and per bucket).
- Give-back (current price → stop, incl. open profit): total % of E, amber when ≥ 8%, red ≥ 10% with "Review: take partial profit or raise stops".
- Per idea list: ticker · bucket · risk now · give-back.
- Status chip per bucket: **Normal** / **Stop opening** (cap reached). "Half size" appears only after PARKED rules are built.
- Principal risk per position = 0 when stop ≥ average entry. Footnote: "Gaps/slippage can still cause a loss."
- Any position missing a stop or price → listed as "Missing stop/price" and counted as unknown, never as 0.

## PARKED — needs SRTp's decision (do not build)
- D1 Keep today's regime/DD multipliers on top of the new risk %, or replace them with the new throttles?
- D2 Momentum half-size: define "benchmark bearish" (e.g. SPY below a falling 40-week EMA?).
- D3 Satellite daily stop 0.5%: floating P&L needs live prices the dashboard doesn't have — manual entry or realized-only?
- D4 Satellite −10% from peak → half size: confirm it replaces the current Sat DD rules.
- D5 Same idea across brokers (Theme ID, ≤ 0.25% combined): how to tag (manual Theme field?).
- D6 Quarterly sweep: reminder + amount only (you move the cash)?
- D7 Margin buffer check per account: which balance field counts as free margin per broker?

## Tests
- AAA example: E 1,000,000, entry 10 risk 0.5% SL 8 → 2,500 sh; entry 10.5 risk 0.3% → 1,200 sh; total 0.80%, left 0.20%, avg 10.16.
- Blended stop: 2 SLs 50/50 → risk = weighted exit; % ≠ 100 blocks Save.
- Size cap trims shares; bucket/total cap blocks Save; add-on new budget only when stops ≥ avg entry.
- Sat contracts with multiplier + lot step, rounded down.
- Panel: principal risk 0 at breakeven; missing stop = unknown; give-back amber/red bands.
- Old plans/trades unchanged. No formulas/field names visible on main screens.
- Screenshots 390/1440: plan form (default single trade, and 2+2 rows), Port risk panel, Today line.
- Log changed expectations in tests/PS1_retired.md. Draft PR → main. Don't merge.
