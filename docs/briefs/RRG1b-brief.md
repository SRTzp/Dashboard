# RRG1b — Flow relative-trend panel: fix after first live load (2026-11-06)

Branch from main (after RRG1 merge): claude/rrg1b. UI + fetch handling only. No model/threshold changes.

## 1. Rate-limit failure during the one-time refetch
Seen live: "You have run out of API credits for the current minute. 16 API credits were used, the current limit being 8" → panel stays "outdated".
- Cause to confirm: two batches (8 + 8 credits) sent inside the same minute (migration + auto refresh / manual refresh overlapping, or cooldown not applied between migration batches).
- Fix:
  - One fetch queue only. Never more than 8 credits per rolling 60 s (wait ≥ 61 s between batches, including migration, auto and manual refresh). A refresh click while the queue runs joins the queue, it doesn't start a second one.
  - On a Twelve Data credit/429 error: keep the batches already received, wait 61 s, retry the failed batch automatically (max 3 tries).
  - Replace the raw API text with a short status line: "Updating prices · batch 2/3 · next in 45 s" / "Price limit reached — retrying in 60 s". Raw error only in Details/console.
- Partial success: save the batches that arrived; only mark the model migrated when ALL symbols + SPY have new-model results.

## 2. Old-model results must not be shown with new-model meaning
Seen live: cards say "Outperforming · strengthening (old model)" and the 2×2 places them in the new boxes. That repeats the exact error RRG1 fixed (old "Leading" ≠ outperforming).
- While a symbol has only old-model results: do NOT place it in the new 2×2 / Neutral strip and do NOT show the new labels.
  - Put it in a grey "Waiting for refresh (old model)" strip, ticker only.
  - Card line: "Old model — refreshing…" (no state label, no gauges).
- Breadth "x/23 beat SPY": count only new-model results; show "(n waiting)" if some are pending.

## 3. Legend collapsible
- The explanation block ("Relative Trend vs SPY — custom model … Δ over the last 5 days … bars in state … 52W gap … RS gauges …") becomes a collapsed "How to read ›" toggle, closed by default. Remember open/closed per device (localStorage, try/catch).
- Shorten the text to max 4 short lines, plain English:
  - Relative = vs SPY, not price going up/down.
  - Price chip = the ETF's own trend (40W EMA weekly / 50D EMA daily).
  - Cycle: Recovering → Strengthening → Fading → Worsening.
  - Custom model, not JdK RRG.

## 4. Lean card (Flow list + Today Sectors row)
Current card is unreadable (state + "(old model)" + bars in state + 52W gap + two gauges + "Well above 1y norm ▲Very fast").
New card = 2 lines:
- Line 1: ★ TICKER Name
- Line 2: [Relative chip] [Price chip] · "−5.9% from 52W high" (short)
  - Relative chip text: "Beating SPY ↗" (strengthening) / "Beating SPY ↘" (fading) / "Lagging SPY ↗" (recovering) / "Lagging SPY ↘" (worsening) / "≈ SPY" (neutral). Colour = state colour. Tooltip = full state name + "relative to SPY, not absolute price".
  - Price chip (compact): "▲ Up +3.2%" / "▼ Down −4.1%" / "◆ Mixed +0.8%" / "Price n/a". The % = close vs the view's EMA (50D EMA daily, 40W EMA weekly), 1 decimal. Tooltip: "Own price vs 50-day EMA (rising) — not compared with SPY".
  - Fit rule: line 2 never wraps or overflows (390px and up). If space runs out, hide the 52W-gap text first (it stays in Details); the two chips always show in full.
  - Momentum is already the arrow in the Relative chip — no separate third chip on the card.
- Move to Details ›: bars in state, both 1y-norm gauges + their words, raw values, thresholds, dates, freshness. Keep "Drivers & evidence" as is.
- Text size consistent with the rest of Flow; no monospace for the card.
- Same lean line in the Today › Sectors row.

## Tests
- Rate limit: simulate a credit error on batch 2 → auto retry after 61 s (fake timers), batch 1 kept, no second parallel fetch on refresh click, migrated flag only after all batches.
- Old-model symbols never appear in the new boxes / labels; breadth excludes them.
- Legend collapsed by default, state remembered.
- Card: 2 lines, chip texts as above, gauges only inside Details. Screenshots 390 / 1440 (fixture data, new model + one waiting symbol).
- Log changed expectations in tests/RRG1_retired.md. Draft PR → main, don't merge.
