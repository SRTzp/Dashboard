# RV1 — verify the RRG calculation, symbol by symbol (research + test only)

Approved by SRTp 17 Nov 2026. Goal: prove the Flow › RRG states are computed correctly for every symbol (23 ETFs vs SPY, Daily and Weekly), and show where the data source changes the answer. **No app change in this job** unless a defect is found (then: isolate it, report, propose the fix; do not fix silently).
Base: latest `origin/main`. Branch: `claude/rv1`. Commits: A independent check → B data checks → C report, push each.

## What the app does today (read from index.html, verify)
- Data: Twelve Data `time_series` 1day, 1,200 bars, from the user's browser (key in Settings), cached in Firestore. Closes are split-adjusted, **not dividend-adjusted**.
- Alignment: only dates present in both ETF and SPY; if the last dates differ → "Mismatched end dates · not classified".
- `rrgCompute`: rs = ETF ÷ SPY · raw = 100 × (EMA12(rs) − EMA26(rs)) ÷ EMA26(rs) · momRaw = raw − raw[lag] (D lag 5, W lag 4) · ratio = 100 + z(raw, win) · mom = 100 + z(momRaw, win) (D win 252, W 52, population SD) · state from the sign of raw (ε = 0.10 × SD) and momRaw (δ = 0.10 × SD) with 'zero' hysteresis → lead / weak / imp / lag / flat · days in state.
- Weekly: daily → weekly (last close of week, Monday key); an unfinished week is excluded from the state and shown only as a preview.

## A · Independent re-implementation (code correctness)
- `tools/rrg_verify.py`: a second implementation written from the formula above (pandas `ewm(adjust=False)`, own z-score, own state machine) — do not copy the JS.
- Run the app's own `rrgCompute` / `rrgToWeekly` in node on the **same** arrays (extract the functions from index.html, like `sync_pv1.py`).
- For every symbol × D / W on one fixed price set: compare raw, momRaw, ratio, mom, ε, δ, state, days, prevDays. Pass = equal state and days; numbers within 1e-9.
- Edge cases: missing SPY day, missing ETF day, mismatched last date, a week with 1–4 sessions, holiday weeks, exactly `need` bars, flat series (sd = 0), rs crossing ±ε repeatedly (hysteresis), first bars (EMA seed).

## B · Data checks (does the source change the state?)
Run in GitHub Actions (`workflow_dispatch`, yfinance; Yahoo is rate-limited on the Mac) on the last 5 years, all 23 symbols:
1. **Raw vs dividend-adjusted closes:** state, days and ratio / mom per symbol, D and W, today and over 5 years (% of days where the state differs). Expect high-yield ETFs (XLU, XLRE, XLP, XLE, KRE, XLF) to be most affected — show it.
2. **Unfinished daily bar:** does the app ever classify on a bar that is still trading (fetch during the US session = 21:30–04:00 ICT)? Find the code path; show how often the state on the partial bar differs from the closed bar.
3. **Twelve Data vs Yahoo:** if possible from the stored cache / a user export, compare the last 30 closes per symbol (only report; no key handling).
4. **Benchmark sanity:** SPY vs itself → flat; a synthetic ETF = SPY × 1.01ⁿ → outperforming, strengthening; each quadrant reachable.

## C · Report — `docs/reports/RV1-summary.md`
- Table per symbol (D and W): app state · independent state · match ✓/✗ · raw · ratio · mom · days · adjusted-close state · changes with adjusted? 
- List every mismatch with cause (code vs data vs definition).
- Findings + proposed fixes as separate items for the user to approve (e.g. "use adjusted closes", "skip the unfinished daily bar").
- `tests/rrg_verify_test` (node + python) added to `tests/run_regression.sh` so the two implementations stay equal.

## Rules
- No app behaviour change, no data writes, no API key in code or logs. English report.
