# RV1 — verify the RRG calculation, symbol by symbol (generated 2026-11-18)

Research + tests only. **No app behaviour changed, no data written, no API key.** Method: the app's own `rrgBuildRows → rrgCompute / rrgToWeekly` (extracted from `index.html` into node by `tools/rrg_app_run.js`, not re-typed) is compared with an independent pandas implementation written from the brief (`tools/rrg_verify.py`). Guard: `tests/rrg_verify_test.py` (in `tests/run_regression.sh`).

## Verdict

- **Code correctness (A): the app computes what the formula says.** 74 cases (46 symbol×end-date runs + 28 edge cases) × Daily and Weekly → **0 mismatches** in state, days, prevDays, date, raw, momRaw, ratio, mom, ε, δ (tolerance 1e-9).
- **Real data (B), as of 2026-11-17:** same comparison on Yahoo raw closes, 23 symbols × D/W → **0 mismatches**.

## A · Independent check (synthetic fixed set, 1,200 sessions, two end dates)

Why synthetic: the check is about code, so the price set must be fixed and reproducible; seeded random walks correlated with a SPY-like path (seed 20261117). Real-data runs are section B.

### Edge cases (app result · both implementations agree)

| Case | Daily | Weekly | Note |
|---|---|---|---|
| spy_vs_itself | คำนวณไม่ได้ — ข้อม | คำนวณไม่ได้ — ข้อม | rs ≡ 1 → SD 0 → "not classified" ✓ |
| synthetic_up_1.01^n | Out ↘ | Out ↗ (+preview Out ↘) | Outperforming ✓; D is "fading" because constant-rate outperformance has ~0 acceleration (see finding 4) |
| flat_series | Under ↘ | Out ↘ (+preview Out ↗) | rs ≡ 2 is NOT recognised as flat (see finding 3) |
| missing_spy_day | Under ↘ | Under ↘ (+preview Under ↘) | intersection of dates → same as missing ETF day ✓ |
| missing_etf_day | Under ↘ | Under ↘ (+preview Under ↘) | same ✓ |
| mismatch_last_date | Mismatched end dat | Mismatched end dat | "Mismatched end dates · not classified" ✓ |
| mismatch_last_date_bench_behind | Mismatched end dat | Mismatched end dat | same, other direction ✓ |
| D_need_minus_1 | ข้อมูลไม่พอ (มี 28 | ข้อมูลไม่พอ (มี 58 | 282 < 283 → error ✓ |
| D_need_exact | Under ↘ | ข้อมูลไม่พอ (มี 58 | 283 = 26+252+5 → classified ✓ |
| D_need_plus_1 | Under ↘ | ข้อมูลไม่พอ (มี 59 |  |
| no_data | No data | No data | "No data" ✓ |
| W_need_exact_82w | Out ↗ | Under ↘ | 82 weeks = 26+52+4 → classified ✓ |
| W_need_minus_1_81w | Out ↗ | ข้อมูลไม่พอ (มี 81 | error ✓ |
| last_week_1_sessions_partial | Out ↘ | Out ↗ (+preview Out ↗) | last week has 1 session(s) → partial, preview only ✓ |
| last_week_2_sessions_partial | Out ↗ | Out ↗ (+preview Out ↗) | last week has 2 session(s) → partial, preview only ✓ |
| last_week_3_sessions_partial | Under ↘ | Under ↘ (+preview Under ↘) | last week has 3 session(s) → partial, preview only ✓ |
| last_week_4_sessions_partial | Under ↘ | Out ↗ (+preview Out ↘) | last week has 4 session(s) → partial, preview only ✓ |
| holiday_week_ends_wed_ref_next_week | Out ↗ | Under ↗ | week closed once the next week starts (no preview) ✓ |
| holiday_week_ends_wed_ref_same_week | Out ↗ | Under ↗ (+preview Under ↗) | still inside the week → preview ✓ |
| hysteresis_oscillating | Out ↘ | Neutral (+preview Under ↘) | rs oscillates around 1 (crosses ±ε repeatedly); states agree bar by bar |
| hysteresis_noise_zero_drift | Out ↗ | Out ↗ (+preview Out ↗) | zero-drift noise; states agree |
| quadrant_lead | Out ↗ | Under ↗ (+preview Under ↗) | quadrant reachable ✓ |
| quadrant_weak | Out ↘ | Out ↗ (+preview Out ↗) | quadrant reachable ✓ |
| quadrant_flat | Neutral | Out ↗ (+preview Out ↗) | quadrant reachable ✓ |
| quadrant_lag | Under ↘ | Out ↗ (+preview Out ↗) | quadrant reachable ✓ |
| quadrant_imp | Under ↗ | Under ↘ (+preview Under ↘) | quadrant reachable ✓ |
| rs_exactly_1 | คำนวณไม่ได้ — ข้อม | คำนวณไม่ได้ — ข้อม |  |
| both_constant_100 | คำนวณไม่ได้ — ข้อม | คำนวณไม่ได้ — ข้อม |  |

### Per symbol (synthetic set ending Wed 18 Nov 2026 — last week unfinished → Weekly state is the last closed week)

| Symbol | TF | app state | independent | match | raw (EMA spread %) | ratio | mom | days | adjusted-close state | changes with adjusted? |
|---|---|---|---|---|---|---|---|---|---|---|
| XLU | D | Under ↗ | Under ↗ | ✓ | -0.373 | 100.08 | 101.65 | 6 | n/a (synthetic: no dividends) | — |
| XLU | W | Under ↘ | Under ↘ | ✓ | -5.130 | 98.83 | 99.98 | 4 | n/a (synthetic: no dividends) | — |
| PAVE | D | Out ↘ | Out ↘ | ✓ | 0.134 | 99.56 | 99.05 | 4 | n/a (synthetic: no dividends) | — |
| PAVE | W | Out ↗ | Out ↗ | ✓ | 3.267 | 101.86 | 99.99 | 12 | n/a (synthetic: no dividends) | — |
| XHB | D | Out ↘ | Out ↘ | ✓ | 2.261 | 101.24 | 99.81 | 1 | n/a (synthetic: no dividends) | — |
| XHB | W | Out ↗ | Out ↗ | ✓ | 6.276 | 101.82 | 100.23 | 3 | n/a (synthetic: no dividends) | — |
| XLB | D | Neutral | Neutral | ✓ | -0.047 | 99.51 | 99.57 | 3 | n/a (synthetic: no dividends) | — |
| XLB | W | Out ↘ | Out ↘ | ✓ | 3.388 | 100.21 | 99.44 | 10 | n/a (synthetic: no dividends) | — |
| XLC | D | Out ↘ | Out ↘ | ✓ | 0.533 | 100.16 | 98.05 | 17 | n/a (synthetic: no dividends) | — |
| XLC | W | Out ↗ | Out ↗ | ✓ | 2.058 | 100.77 | 101.42 | 5 | n/a (synthetic: no dividends) | — |
| XBI | D | Out ↘ | Out ↘ | ✓ | 2.269 | 101.04 | 97.08 | 10 | n/a (synthetic: no dividends) | — |
| XBI | W | Out ↗ | Out ↗ | ✓ | 7.934 | 102.39 | 102.45 | 9 | n/a (synthetic: no dividends) | — |
| JETS | D | Out ↗ | Out ↗ | ✓ | 1.619 | 101.46 | 100.75 | 10 | n/a (synthetic: no dividends) | — |
| JETS | W | Under ↗ | Under ↗ | ✓ | -0.532 | 98.31 | 101.72 | 1 | n/a (synthetic: no dividends) | — |
| IGV | D | Under ↘ | Under ↘ | ✓ | -2.428 | 97.20 | 97.92 | 5 | n/a (synthetic: no dividends) | — |
| IGV | W | Under ↘ | Under ↘ | ✓ | -0.257 | 99.45 | 98.08 | 1 | n/a (synthetic: no dividends) | — |
| XRT | D | Out ↗ | Out ↗ | ✓ | 1.716 | 100.80 | 100.25 | 12 | n/a (synthetic: no dividends) | — |
| XRT | W | Out ↗ | Out ↗ | ✓ | 2.678 | 100.49 | 100.25 | 2 | n/a (synthetic: no dividends) | — |
| HACK | D | Out ↘ | Out ↘ | ✓ | 2.566 | 101.11 | 98.64 | 18 | n/a (synthetic: no dividends) | — |
| HACK | W | Out ↗ | Out ↗ | ✓ | 8.003 | 103.10 | 101.71 | 7 | n/a (synthetic: no dividends) | — |
| XLF | D | Out ↗ | Out ↗ | ✓ | 2.422 | 101.47 | 101.65 | 9 | n/a (synthetic: no dividends) | — |
| XLF | W | Out ↘ | Out ↘ | ✓ | 4.118 | 101.60 | 98.80 | 3 | n/a (synthetic: no dividends) | — |
| KRE | D | Under ↗ | Under ↗ | ✓ | -0.194 | 100.53 | 100.22 | 4 | n/a (synthetic: no dividends) | — |
| KRE | W | Under ↗ | Under ↗ | ✓ | -4.992 | 100.74 | 100.80 | 7 | n/a (synthetic: no dividends) | — |
| XLE | D | Out ↘ | Out ↘ | ✓ | 1.419 | 101.21 | 99.58 | 5 | n/a (synthetic: no dividends) | — |
| XLE | W | Under ↗ | Under ↗ | ✓ | -0.476 | 103.14 | 101.47 | 11 | n/a (synthetic: no dividends) | — |
| XLV | D | Under ↗ | Under ↗ | ✓ | -0.887 | 99.96 | 101.56 | 9 | n/a (synthetic: no dividends) | — |
| XLV | W | Under ↘ | Under ↘ | ✓ | -4.215 | 98.74 | 99.42 | 7 | n/a (synthetic: no dividends) | — |
| ITA | D | Under ↘ | Under ↘ | ✓ | -1.672 | 98.56 | 98.91 | 8 | n/a (synthetic: no dividends) | — |
| ITA | W | Under ↘ | Under ↘ | ✓ | -1.279 | 98.29 | 99.45 | 6 | n/a (synthetic: no dividends) | — |
| SMH | D | Out ↘ | Out ↘ | ✓ | 1.641 | 100.77 | 99.48 | 4 | n/a (synthetic: no dividends) | — |
| SMH | W | Out ↗ | Out ↗ | ✓ | 2.482 | 100.77 | 100.45 | 2 | n/a (synthetic: no dividends) | — |
| ARKX | D | Out ↘ | Out ↘ | ✓ | 0.922 | 99.83 | 99.95 | 1 | n/a (synthetic: no dividends) | — |
| ARKX | W | Out ↗ | Out ↗ | ✓ | 3.267 | 99.77 | 99.85 | 7 | n/a (synthetic: no dividends) | — |
| IRBO | D | Under ↗ | Under ↗ | ✓ | -0.014 | 100.72 | 101.42 | 4 | n/a (synthetic: no dividends) | — |
| IRBO | W | Under ↗ | Under ↗ | ✓ | -3.817 | 99.96 | 100.81 | 7 | n/a (synthetic: no dividends) | — |
| XLK | D | Out ↗ | Out ↗ | ✓ | 2.169 | 101.14 | 101.11 | 7 | n/a (synthetic: no dividends) | — |
| XLK | W | Out ↗ | Out ↗ | ✓ | 0.380 | 100.23 | 100.94 | 1 | n/a (synthetic: no dividends) | — |
| XLI | D | Under ↘ | Under ↘ | ✓ | -3.772 | 98.58 | 99.85 | 10 | n/a (synthetic: no dividends) | — |
| XLI | W | Under ↘ | Under ↘ | ✓ | -5.572 | 98.56 | 99.09 | 5 | n/a (synthetic: no dividends) | — |
| XLY | D | Under ↘ | Under ↘ | ✓ | -4.828 | 97.30 | 97.87 | 4 | n/a (synthetic: no dividends) | — |
| XLY | W | Under ↘ | Under ↘ | ✓ | -2.390 | 98.10 | 98.00 | 3 | n/a (synthetic: no dividends) | — |
| XLP | D | Out ↗ | Out ↗ | ✓ | 3.190 | 100.83 | 101.05 | 7 | n/a (synthetic: no dividends) | — |
| XLP | W | Out ↘ | Out ↘ | ✓ | 12.448 | 101.98 | 99.32 | 2 | n/a (synthetic: no dividends) | — |
| XLRE | D | Under ↘ | Under ↘ | ✓ | -3.146 | 98.72 | 98.97 | 8 | n/a (synthetic: no dividends) | — |
| XLRE | W | Under ↗ | Under ↗ | ✓ | -6.431 | 98.32 | 100.57 | 3 | n/a (synthetic: no dividends) | — |

## B · Data checks (real prices)

### Per symbol — Yahoo raw closes (split-adjusted, no dividends = what Twelve Data sends), as of 2026-11-17

| Symbol | TF | app state | independent | match | raw (EMA spread %) | ratio | mom | days | adjusted-close state | changes with adjusted? |
|---|---|---|---|---|---|---|---|---|---|---|
| XLU | D | Out ↘ | Out ↘ | ✓ | 2.055 | 101.73 | 99.89 | 4 | Out ↘ | no |
| XLU | W | Under ↗ | Under ↗ | ✓ | -2.466 | 99.63 | 101.90 | 4 | Under ↗ | no |
| PAVE | D | Out ↘ | Out ↘ | ✓ | 0.408 | 100.44 | 99.91 | 1 | Out ↘ | no |
| PAVE | W | Under ↗ | Under ↗ | ✓ | -2.360 | 98.25 | 100.45 | 1 | Under ↗ | no |
| XHB | D | Out ↘ | Out ↘ | ✓ | 1.720 | 101.43 | 98.94 | 4 | Out ↘ | no |
| XHB | W | Under ↗ | Under ↗ | ✓ | -3.122 | 99.63 | 101.65 | 3 | Under ↗ | no |
| XLB | D | Out ↘ | Out ↘ | ✓ | 1.315 | 100.96 | 98.72 | 4 | Out ↘ | no |
| XLB | W | Under ↗ | Under ↗ | ✓ | -0.629 | 99.93 | 101.14 | 3 | Under ↗ | no |
| XLC | D | Out ↗ | Out ↗ | ✓ | 0.365 | 101.17 | 101.89 | 2 | Out ↗ | no |
| XLC | W | Under ↘ | Under ↘ | ✓ | -2.921 | 99.31 | 100.28 | 4 | Under ↘ | no |
| XBI | D | Out ↘ | Out ↘ | ✓ | 0.018 | 99.59 | 98.95 | 3 | Out ↘ | no |
| XBI | W | Out ↘ | Out ↘ | ✓ | 1.432 | 98.35 | 99.92 | 9 | Out ↘ | no |
| JETS | D | Out ↘ | Out ↘ | ✓ | 2.406 | 101.22 | 99.78 | 1 | Out ↘ | no |
| JETS | W | Under ↗ | Under ↗ | ✓ | -2.132 | 98.84 | 100.51 | 1 | Under ↗ | no |
| IGV | D | Under ↘ | Under ↘ | ✓ | -1.452 | 99.57 | 99.61 | 10 | Under ↘ | no |
| IGV | W | Out ↘ | Out ↘ | ✓ | 1.452 | 101.48 | 99.70 | 2 | Out ↘ | no |
| XRT | D | Out ↘ | Out ↘ | ✓ | 2.114 | 101.88 | 98.80 | 3 | Out ↘ | no |
| XRT | W | Under ↗ | Under ↗ | ✓ | -0.352 | 101.01 | 102.24 | 4 | Under ↗ | no |
| HACK | D | Under ↘ | Under ↘ | ✓ | -1.069 | 99.07 | 99.70 | 8 | Under ↘ | no |
| HACK | W | Out ↘ | Out ↘ | ✓ | 5.210 | 101.09 | 99.03 | 2 | Out ↘ | no |
| XLF | D | Out ↘ | Out ↘ | ✓ | 1.966 | 102.10 | 99.78 | 3 | Out ↘ | no |
| XLF | W | Out ↗ | Out ↗ | ✓ | 0.319 | 101.87 | 101.61 | 1 | Out ↗ | no |
| KRE | D | Out ↘ | Out ↘ | ✓ | 1.100 | 100.83 | 99.37 | 4 | Out ↘ | no |
| KRE | W | Under ↗ | Under ↗ | ✓ | -0.809 | 99.28 | 100.78 | 2 | Under ↗ | no |
| XLE | D | Under ↗ | Under ↗ | ✓ | -0.174 | 99.54 | 100.15 | 1 | Under ↗ | no |
| XLE | W | Out ↗ | Out ↗ | ✓ | 3.231 | 100.54 | 100.06 | 13 | Out ↗ | no |
| XLV | D | Out ↘ | Out ↘ | ✓ | 2.744 | 101.92 | 99.39 | 4 | Out ↘ | no |
| XLV | W | Out ↗ | Out ↗ | ✓ | 3.333 | 102.40 | 101.71 | 5 | Out ↗ | no |
| ITA | D | Out ↗ | Out ↗ | ✓ | 1.064 | 100.84 | 100.08 | 11 | Out ↗ | no |
| ITA | W | Under ↗ | Under ↗ | ✓ | -3.914 | 98.38 | 100.68 | 1 | Under ↗ | no |
| SMH | D | Under ↗ | Under ↗ | ✓ | -4.075 | 97.76 | 100.29 | 3 | Under ↗ | no |
| SMH | W | Under ↘ | Under ↘ | ✓ | -0.973 | 97.51 | 98.21 | 1 | Under ↘ | no |
| ARKX | D | Under ↘ | Under ↘ | ✓ | -1.449 | 99.25 | 99.92 | 1 | Under ↘ | no |
| ARKX | W | Under ↘ | Under ↘ | ✓ | -3.494 | 98.16 | 99.69 | 11 | Under ↘ | no |
| XLK | D | Under ↘ | Under ↘ | ✓ | -2.568 | 97.78 | 100.15 | 12 | Under ↘ | no |
| XLK | W | Out ↘ | Out ↘ | ✓ | 0.380 | 98.99 | 98.13 | 4 | Out ↘ | no |
| XLI | D | Out ↗ | Out ↗ | ✓ | 0.483 | 100.55 | 100.23 | 11 | Out ↗ | no |
| XLI | W | Under ↗ | Under ↗ | ✓ | -2.303 | 98.46 | 100.24 | 1 | Under ↗ | no |
| XLY | D | Out ↘ | Out ↘ | ✓ | 2.110 | 103.23 | 99.06 | 2 | Out ↘ | no |
| XLY | W | Under ↗ | Under ↗ | ✓ | -1.318 | 100.55 | 103.92 | 4 | Under ↗ | no |
| XLP | D | Out ↘ | Out ↘ | ✓ | 2.730 | 102.22 | 99.88 | 4 | Out ↘ | no |
| XLP | W | Out ↗ | Out ↗ | ✓ | 0.488 | 101.45 | 101.95 | 1 | Out ↗ | no |
| XLRE | D | Out ↘ | Out ↘ | ✓ | 2.000 | 102.31 | 99.48 | 3 | Out ↘ | no |
| XLRE | W | Under ↗ | Under ↗ | ✓ | -1.555 | 100.20 | 101.88 | 3 | Under ↗ | no |
| ARTY | D | Under ↗ | Under ↗ | ✓ | -3.287 | 98.01 | 100.71 | 4 | Under ↗ | no |
| ARTY | W | Out ↘ | Out ↘ | ✓ | 0.554 | 98.35 | 98.01 | 5 | Out ↘ | no |
| ROBO | D | Under ↘ | Under ↘ | ✓ | -2.013 | 98.22 | 99.68 | 2 | Under ↘ | no |
| ROBO | W | Under ↘ | Under ↘ | ✓ | -2.979 | 97.56 | 98.72 | 12 | Under ↘ | no |

Full B1–B4 tables (5-year % of days the state differs, partial-bar simulation, benchmark sanity): `docs/reports/RV1-data.md`.

### Mismatches (app vs independent, real closes)

None.

### Symbols whose state *today* changes with dividend-adjusted closes: 0 of 48 (symbol × TF)

none

## Mismatch list

Code (A): **none**. Data (B): see above.
Definition differences are listed as findings (not mismatches: both implementations agree on them).

## Findings — each is a separate item for you to approve (nothing was changed)

1. **Adjusted vs raw closes (data).** The app uses split-adjusted, not dividend-adjusted closes. RS = ETF ÷ SPY on raw prices drifts by the *yield difference* (an ETF paying 3–4 % vs SPY ~1.3 % loses ~2 %/yr of relative price that is not real underperformance). Effect size per symbol: `RV1-data.md` B1. *Proposed fix (needs approval):* fetch `adjusted=true` closes / use adjusted series for RS only (Twelve Data adjusts splits by default; dividend-adjust needs `adjust=all`), then bump `RRG_MODEL`.
2. **Unfinished daily bar (code path).** Nothing in `rrgFetchBatch`/`rrgSeries`/`rrgBuildRows` drops a bar that is still trading; `rrgBarsFresh` only checks recency and `rrgCacheFresh` keeps a fetch for the rest of the ICT calendar day. A fetch between 21:30 and 04:00 ICT classifies on the partial bar, and a fetch after ~00:00 ICT keeps that partial result until the next ICT day (so it can outlive the US close by up to ~20 h). Friday partial bars are also treated as a finished week. Impact: `RV1-data.md` B2. *Proposed fix:* drop the last daily bar when its date is today in New York and the market is open (or `date >= ET today` before 16:15 ET); mark the card "as of last close".
3. **Constant-but-not-1 relative strength is not detected as flat (code, low).** `sd > 0` is an exact test: rs ≡ 2 gives SD ≈ 1e-9 from float noise, so a state is produced from noise (case `flat_series`). Only rs ≡ 1 (SPY vs itself) returns "not classified". Not reachable with real ETFs. *Proposed fix:* relative tolerance `sd < 1e-9·|mean|` → not classified.
4. **Definition note — constant-rate outperformance is "fading", not "strengthening".** SPY×1.01ⁿ is correctly *Outperforming* but the momentum leg (raw − raw[lag]) is ~0 once the EMA spread saturates, so ↗/↘ is noise-driven. The brief expected "strengthening"; the definition (momentum = change of the EMA spread) cannot give that for a constant growth rate. *No fix proposed* — only the expectation changes. Quadrants are reachable with an accelerating/decelerating rs (5/5 reached).
5. **Definition note — history is recomputed with today's ε, δ.** ε and δ use the SD of the *last* window and are applied to the whole history, so "days in state" and previous-state length can change when SD changes, without any new price. Both implementations agree; it is how the spec reads. *No fix proposed* unless you want states frozen when first seen.
6. **Dead ticker in `RRG_SYMS`: IRBO (data/config).** IRBO (iShares Robotics & AI) was delisted and replaced by ARTY (iShares Future AI & Tech) in Aug 2024 — Yahoo/Twelve Data return no rows for IRBO, so its card can never compute. *Proposed fix (needs approval, `RRG_SYMS` NOT changed yet):* replace IRBO with **ARTY "AI & Tech"** and **ROBO "Robotics"** (ROBO Global Robotics & Automation, equal-weight, low overlap with SMH/XLK), and update `sector_etf` references. Caveat: ARTY's index changed in Aug 2024, so its history before that is the old robotics index — the 126-bar history used for ε/δ and "days in state" mixes two indices for the first months. ARTY and ROBO are included in the data check as extra symbols (marked “(extra)”) so their results are visible; symbols with no data are listed under “No data (skipped)”.

## Run

- Local (A, offline): `python3 tests/rrg_verify_test.py` · included in `bash tests/run_regression.sh` together with `python3 scripts/rrg_data_check.py --selftest`.
- **B needs you:** copy `scripts/rrg-data-check.workflow.yml` to `.github/workflows/rrg-data-check.yml` on `claude/rv1` (or main), then Actions → **rrg-data-check** → Run workflow. It writes `docs/reports/RV1-data.{md,json}` and regenerates this file (≈10–15 min).
- B3 (Twelve Data vs Yahoo): export once in the browser console — `copy(JSON.stringify(ffState().rrg.rowsD.map(r=>({sym:r.sym,date:r.date,close:r.close}))))` — save as `docs/reports/RV1-td-export.json`, add `--td-export docs/reports/RV1-td-export.json` to the workflow step. Only closes, no key.
