# RV1b — summary

Branch `claude/rv1b` (from `origin/main`, includes SH1/SH2: the RRG cache is `settings.flowShared` on the home account). Code commit: 55c34e2.

## What changed

1. **IRBO → ROBO.** `RRG_SYMS`: `{s:'ROBO', n:'Robotics'}` replaces `IRBO`. `RRG_BUILD` 7 → 8, so the shared cache is refetched. Watch sector links: the keyword map (robot/ai/artificial) now suggests `ROBO`; stored `sector_etf` values of `IRBO` are read as `ROBO` on load (item normalisation and `tv1EtfOf`), so they do not fall out of `sectorValid`. Hint/tooltip texts mention ROBO. `tools/rrg_verify.py` symbol list and `scripts/rrg_data_check.py` updated.
2. **Daily RRG close cut.** `rrgSeries` drops any bar dated today in America/New_York while it is before 16:15 ET (`rrgProvCut`, `rrgEtNow`; applies to the ETFs and SPY, so no end-date mismatch). The weekly series is built from the same trimmed data, so the Friday weekly preview is covered. The run records `rrg.prov` (the ET date whose bar was dropped); `rrgCacheFresh` treats such a cache as stale once the ET clock passes 16:15, so a mid-session fetch is replaced after the close. Header text: `Fresh · as of <date> close` (plus a note while the cut is active); stale text: `As of <date> close · stale`.
3. **Adjusted closes — see below. No change made, `RRG_MODEL` stays 2.**

## Item 3 — dividend-adjusted closes

Twelve Data `time_series` has an `adjust` parameter (`all`, `splits`, `dividends`, `none`; default `splits`) and the endpoint costs a flat **1 credit per symbol**, with no plan restriction stated for `adjust` (docs: twelvedata.com/docs/market-data/time-series). So a single request with `adjust=dividends`/`all` costs nothing extra.

However the response carries one `close` field only — there is no raw close beside the adjusted one. The app needs raw/split-adjusted closes for the price-trend (EMA50 / EMA40), 52-week-high distance and `close`, and adjusted closes for RS only. That requires a **second request per symbol (2× credits; 48 per refresh instead of 24, ≈ 6 batches at 8/min)**, so it is not "no extra credit". Result: **not available at no extra credit in the form requested → left as is, no change needed, `RRG_MODEL` not bumped.** (Not verified against the live API; this is from the documentation.) Option for later: use adjusted closes for everything, at the cost of changing price-trend/52w numbers.

## Tests

- `tests/rrg_verify_test.py`: PASS 17/17 (0 mismatches vs the pandas reference).
- New `tests/rrg_close_cut_test.js` (fake clock; added to `run_regression.sh`): PASS 16/16 — 16:14 vs 16:15 ET, pre-market, after UTC midnight but still the same ET day, EST and EDT, Friday mid-session (weekly preview as of Thursday) vs after close (no preview), mid-session cache fresh until 16:15 ET then stale, ROBO/Robotics present and IRBO absent.
- Full `tests/run_regression.sh`: **50/50 ok · 0 failing · 1158 s. Failing set: empty.**
