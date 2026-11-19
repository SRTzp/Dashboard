# WL2 — Watch fixes + RS from high

Spec: `docs/briefs/lr/WatchRS.dc.html` + `WatchRSPhone.dc.html`. Side-by-side (mockup | live): `tests/screenshots/wl2/wl2-1440-side.png`, `wl2-390-side.png` (+ `wl2-list-360-live.png`).

## A · Data (`scripts/build_prices.py`, additive)
- `rs` += `hi52`, `hi52Date`, `offHigh` (close/hi52 − 1), `r3m`, `r6m`, `r9m`, `r12m` (adjusted closes, last 252 bars). Rating maths untouched.
- `prices/{ySym}` += `sector`, `industry` (yfinance, fetched once per ticker; the existing field is the cache). No workflow change.
- `tests/rs1_selftest.py` +9 checks (46 total).

## B · Use this thesis
"From living thesis" label on the WHY / TRIGGER / EXIT block. When the thesis has an exit (+ trigger for Momentum) and homework isn't done, `Use this thesis ✓` sits above the main action. It copies exit → `my_thesis.exit` and trigger → `hw.trigger` (blanks only), then sets `hw.confirmedAt` + `doneAt`. Tested: `wl1HwDone` false→true, row "Done <date>", cap 50% → 100%, an existing own exit is kept.
Compounder (not in the brief): needs Why + Exit, so it copies lt thesis → `my_thesis.why` (blank only) as well.

## C · Sector auto-fill
`tv1EtfOf` last fallback = `sectorSuggest(prices industry, then sector)`; manual `sector_etf` still wins. Added "consumer cyclical / defensive" keywords (yfinance sector names).

## D–F · RS column, detail, sort
- Column "RS · from high": 24 / 16 / 64px grid, tabular, % right-aligned; 0..−10% muted, −10..−25% ink, beyond −25% amber; `newHigh5d` chip takes the % slot. Stock column 108→124px, RS 96→112px, table min-width unchanged (900). Legend under the table.
- Phone line 2 ends `RS 98 ↘ −42%`, pinned right; left text ellipsizes.
- Detail: `RS 98 ← 99 (4 wks ago) · line ↘`, `−42% from 52w high (1,255 · 18 Jun)`, `3m · 6m · 9m · 12m`, `Holdings ↗` next to the sector.
- Sort "Near high + RS": by rating; rows beyond −25% go below the rest (also by rating); unrated rows rank last inside their group.
- Missing new fields (old price docs) → rating + arrow only, no errors (TEAM case).

## G · Exch? chip
nowrap, shrinks inside its cell (`overflow:hidden`), no overlap with the status chip.

## Deviations from the mockup
- (resolved in wrap-up) The RS block is now the grey card at the top of the detail, above "From living thesis".
- Sort is still the native select (note in its tooltip), not a custom menu.
- Muted % uses the app token `#5F6672` (mock `#8A919C`) for contrast.

## Tests
`tests/run_tests_wl2.py` (64 checks at 1440 / 390 / 360), `lr5a` expectations updated (header "RS · from high", phone "new high" chip). Added to `run_regression.sh`. Hooks superset unchanged; no engine changes.

## Final regression
`bash tests/run_regression.sh` after the RS-card move (rebased on origin/main): **62/62 ok · 0 failing** (1131s). Hooks superset PASS. Branch diff vs origin/main contains only WL2 files (screenshots under `tests/screenshots/wl2/`, force-added because the folder is gitignored).
