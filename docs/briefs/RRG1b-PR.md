## RRG1b — Flow relative-trend panel: fixes after first live load
UI + fetch handling only. No model/threshold changes (RRG_MODEL / RRG_BUILD untouched).

1. **Fetch queue / rate limit** — one queue (`rrgRefresh` returns the running promise; clicks join it). 61 s is measured from the last request *across runs and reloads* (`rrgLastBatchAt`, localStorage). Credit/429 error → keep received batches, wait 61 s, retry the same batch (max 3). Batches are merged + persisted as they arrive; `pending` lets the next refresh resume only the missing symbols. Model stamp only when every symbol + SPY has new-model results. Status: "Updating prices · batch 2/3 · next in 45 s" / "Price limit reached — retrying in 60 s"; raw API text → Details › Last fetch error + console.
   *Cause (from code, not reproduced live):* the cooldown only existed between batches of one run, so a second run (auto / manual / reload) starting right after another sent its first 8 credits inside the same minute.
2. **Old-model rows** — never placed in the new 2×2 / Neutral strip. Grey "Waiting for refresh (old model)" strip (ticker only), card line "Old model — refreshing…", breadth counts new-model only "(n waiting)". Also excluded from Today, Copy-by-phase (listed as waiting), watchlist sector badges.
3. **Legend** — collapsed "How to read ›" (4 lines), open state in localStorage.
4. **Lean card** (Flow + Today › Sectors): `★ SYM Name` / `[Beating|Lagging SPY ↗↘ | ≈ SPY] [▲ Up +3.2% | ▼ Down | ◆ Mixed | Price n/a] −5.9% from 52W high`. Fit rule: chips first, 52W text wraps into a clipped row and disappears first. Bars in state, 52W sentence, 1y-norm gauges + words, Δ legend → Details.

Note: `sdChip` is now unused by the UI (arrow in the chip replaces it); kept because p105 unit-tests it.

### Tests
- `tests/rrg1b_check.py` 31/31 (fake clock in-page), `tests/rrg1_check.py` 26/26.
- Full suite (`runall2.sh`, 114 suites): the same 14 pre-existing failures as RRG1/main (p5, 13, 23, 41–47, 66, 75, 80, 81). Four suites asserting the old card text were updated (p86, p105, p107, p109) and pass; changes logged in `tests/RRG1_retired.md`.
- Screenshots: `tests/screenshots/rrg1b-{flow,legend-details,today-sectors}-{390,1440}.png`.
- Not verified: live Twelve Data behaviour (no key here).
