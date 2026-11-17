# RM1 — regime signal comparison (research only)

Adjusted closes (yfinance `auto_adjust=True`), ratio = numerator ÷ denominator, SMA of the **ratio**. Modifier table from `risk-engine.js`: green/green 100% · green/red 80% · red/green 80% · red/red 60% · fallback 80%. Display only — no effect on the app.

Window: 2021-11-16 → 2026-11-16 (1255 aligned sessions).

## Flips per year

| SMA | ACWI/BIL | HYG/IEI |
|---|---:|---:|
| 10/20 | 13.1 | 12.9 |
| 20/50 | 7.0 | 5.8 |

## Share of days at each modifier

| SMA | 100% | 80% | 60% |
|---|---:|---:|---:|
| 10/20 | 49.5% | 24.4% | 26.1% |
| 20/50 | 54.5% | 22.7% | 22.8% |

## Sessions from the low back to a 100% modifier

| SMA | 2020 low (23 Mar 2020) | 2022 low (12 Oct 2022) |
|---|---:|---:|
| 10/20 | 0 | 10 |
| 20/50 | 0 | 23 |

_Generated 2026-11-17 10:08 UTC · source yfinance_
