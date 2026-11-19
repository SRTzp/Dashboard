# LR5c — Port tab (mockups PortBoth / PortPhone)

Light only · English · no engine / data-job changes. Reuses the LR5b switch (`lrSwitchHtml('port')`, `LR_SW_CB.port`, `lrSwIds('port')`); default view = Both.

## Built
- **Header** Port · Main · Family · Both · note (Both only).
- **Cards**: Total value (Σ `ps1E` per account, M / F bar), Open risk (Σ engine week-used ฿ + each account's `lr2OpenRisk` % of the 3% cap, never combined), Futures leverage (`lr2Futures`; card hidden when no futures are open).
- **Holdings**: desktop table (Ticker + tag · Main · Family · Total ฿ · % of household · If stopped, sorted by value); phone 2-line rows. Main / Family views show the same layout for one account in its currency.
- **More ▾** wraps all previous Port sections (summary, risk blocks, per-account pies / ports) — nothing removed; the old Lean account switch is hidden and now follows the shared switch.
- 360 px: header ＋ Plan button fits (checked in tests).

## Remaining differences (and why)
- Cash row added under the table so "% of household" sums to 100: stock rows + cash = 100; futures are notional and listed apart (can exceed 100 with them).
- Futures "if stopped" uses |entry−SL| × qty × perPoint × mult (same basis as the notional in `lr2Futures`); `openRiskTHB` ignores perPoint and would show ฿80 for S50.
- Values are cost basis (entry × qty × mult), same definition as the existing "held" figure — no live-price source in these functions.
- Total value = `ps1E` equity (same denominator as futures leverage), not entry-based capital.
- Thai text remains inside **More ▾** (legacy sections, untouched by request "don't drop anything"); the new block has none (tested).
- Mockup fixture numbers differ from the test fixture (different data), layout matches.

## Proof
`tests/screenshots/lr5c/` — `port-1440-side.png`, `port-390-side.png`, `port-1440-main-live.png`, `port-1440-family-live.png`. Tests: `tests/run_tests_lr5c.py` (54 checks, 1440 / 390 / 360), in `run_regression.sh`.

## Regression
Full run on the rebased branch: 60/62 ok; the 2 failing suites (re1c, phase373) read the old Port sections that now sit under More ▾ — tests updated to open More; both re-run alone: re1c 203/0, phase373 475/0. Not re-run as one full pass afterwards. New suite lr5c 54/54.
