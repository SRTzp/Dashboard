# MV1 · part D (same branch claude/mv1)

## D · + Add stock: also plain tickers and TradingView CSV (same sheet, no new button)
Sheet = `wl1ImpOpen` (Momentum / Compounder toggle already at the top). Keep the TradingView `.txt` (`###WATCHLIST,EX:SYM`) path exactly as today.
- **Typed tickers**: when the text has no `###` section, read every token split by comma / space / new line as a ticker: `NVDA`, `nasdaq:nvda`, `PTT.BK`, `SET:PTT`. Rules: `EX:SYM` → same as today's parser; `XXX.BK` → TH; plain symbol → US. Same `wlValidTicker` check; bad ones go to "skipped" with a plain reason.
- **CSV upload**: file input accepts `.txt,.csv`. For `.csv`: find the header column named `Symbol` or `Ticker` (case-insensitive; also `Exchange` if present). Value with `:` → EX:SYM; else Exchange column + value; else plain-ticker rule. All other columns ignored. Handle quotes and a BOM. No Symbol/Ticker column → error `No Symbol column found in this CSV`. **Ask SRTp for a real TradingView Screener CSV (5–10 rows) before finishing D, and use it as the test fixture** (`tests/fixtures/tv-screener.csv`).
- Preview unchanged in look: new · already in · skipped. Extra amber hint per US plain ticker that is not in the Screen list (`rs2` rows): `ZZZ · not in the US list · check spelling` — still addable (small caps are not in the list).
- Placeholder: `NVDA, PTT.BK — or paste the TradingView export`. Upload label: `upload .txt / .csv`. Button stays `Add n to Momentum|Compounder`.
- Tests: `NVDA` → 1 new US; `PTT.BK` → TH; `nvda, amd\nNASDAQ:TSLA` → 3; existing ticker → "already in"; `$$$` → skipped; old `###WATCHLIST` text gives the same result as before; CSV fixture; CSV without Symbol column → error.
- Screenshots `mv1-add-typed` and `mv1-add-csv` (1440 + 390).


## Also
- Short name: strip trailing `Inc.` / `Inc` / `Corp.` / `Corporation` / `Ltd` / `Ltd.` / `Holdings` / `Group` / `PLC` / `N.V.` / `S.A.` too (tooltip, panel header and iPhone line 2 all use the same function): `Celestica Inc.` → `Celestica`. Never strip to an empty name — keep the original then. Add 3 cases to the test.

Then one full `JOBS=2 bash tests/run_regression.sh` + hooks, only `mv1-*.png` in the diff, no push. Report tests and PNGs.
