# SET1 report — Lean Settings + product sizing specs + Copy for AI (follow-up included)

Start sha `6269baee7171` · end sha `bca659c0e76306184e10948d833a2acad409dc195435786a5a6533e0fd063991` · backups `index.backup-pre-SET1.html`, `tests/_bk_set1/` · verify `docs/reports/SET1-verify.txt` · retired log `tests/SET1_retired.md`.
**Last index.html edit: Oct 29 20:25 · full run (runall2, base + 1–110) started 21:55, DONE 23:37** (p91 re-run solo afterwards after a test-only edit; no index edit).

## Result
- phase110 **141/141**. Full run **109/111 ok**. Remaining failures, both pre-existing:
  - **phase13** — opens `index.backup-pre-UI1.html`, which doesn't exist (known).
  - **phase5** — BTC Break Price check. **Verified pre-existing**: it fails identically (same check, both widths, 122 pass) when run against `index.backup-pre-SET1.html` with the pre-SET1 tests (copy in `_to_delete/pre/`). Not caused by SET1.
- All 24 earlier failures were triaged: each was either an intentional change (expectation updated, logged) or an infrastructure/fixture issue. **No index.html regression found by them**; two index.html fixes came out of triage: (a) the Sat heat hint text no longer says "MAX HEAT ด้านล่าง" (section merged), (b) nothing else. Per-check list: `tests/SET1_retired.md` (27 entries).

## The six you asked to verify
- **p55 XAUUSD lot vs AS1:** lot identical (0.32 old = new). Only the `broker` label changed ("XM" → "" since there are no brokers) → expectation compares the lot value.
- **p60 / p63 XAG sizing:** XAG now needs a product spec; the fixture writes `settings.products.XAG` = same 5000 / 0.01 / USD as its old broker row → sizes the same, both suites pass (120 / 170).
- **p70 minLot:** XAUUSD minLot is fixed at 0.01 in code, so the 0.05 case sets `PRODUCTS.XAUUSD.minLot = 0.05` in-page; the "too small to split" rule itself still passes (110).
- **p39 DD table values:** table shows "Main" (intended); the test's expected value came from `a.name` → now `td3AcctName(a)`; numbers unchanged. Passes.
- **p56 Today text:** only difference vs the old build was "บัญชีหลัก" → "Main" in the numbers table; the old text is normalised. Passes (155).
- **p5 fixture:** pre-existing failure, see above.

## Changes in this follow-up
1. **Sat page view forced to Lean for everyone:** `ln1Mode()` ignores any stored "legacy". Only a developer localStorage flag `dash.ln1Legacy=1` (seeded by the test stubs, like `dash.td3OtherDev`) re-enables the old view for the old suites. Real users have no flag.
2. **Custom % loss products now have a currency (USD/THB)**; built-in Thai stocks (key/alias ending `.BK`) size as % loss, 100-share lots, **THB** (risk in THB, display ฿). BTC/ETH stay USD.
3. **No more file deletion:** run output moved to `_to_delete/old_runs/`. (Earlier I deleted the old `_to_delete/runall2` once, and ran one `rm -f` on a marker file that didn't exist — both disclosed.)
4. Tests: phase110 adds currency, `.BK`, forced-Lean checks.

## Earlier parts (unchanged)
- v1/v2 Sat audit: v1 fields still read (rpt/rptHi/newMax, Macro ×, DD brake fields, `limits.port.satB`) → moved into Sat › Advanced.
- Removed from UI (stored values kept, hidden inputs feed the old save code): font sizes, tab offset, Lean/legacy switch, default TF, Setup lists, Ideas min group, broker settings; Core layer-2 cap merged with Max open risk (Core).
- Brokers: sizing reads the product only; `settings.brokers`, `brokerList`, `trade.broker` untouched and no longer written.
- Sizing: XAUUSD main 4180/4117 → 0.05 lot, $630 before and after; GO ฿300/pt (฿3,000, 10 pts → 1); BTC $200, 100,000→98,000 → $10,000 · 0.10 BTC; TH stock 1,250 → 1,200.
- Copy by phase `⧉` in the Leadership header row; Copy list in the `…` menu (Watchlist + Candidates); Export .txt removed; row heights unchanged at 300/390/1440.
- "Main" on DD / Risk Sat / Risk Core chips and Today DD/heat rows.
- Screenshots (all six opened): `tests/screenshots/set1-{settings-390,settings-1440,products-390,sat-390,plan-btc-390,plan-xau-390}.png`.

## Limitations / notes
- Retired (print RETIRED, not failing): phase54 §2–4 (broker CRUD, ≈25 checks), phase88 (LN3 six-group Settings), phase90 Mac two-pane Settings (4 checks). New equivalents live in phase110.
- Old suites rely on dev flags `dash.set1Open` (expand all Settings cards) and `dash.ln1Legacy`; phase110 clears both.
- Custom Sat assets still need a product spec (`+ Add product`); US stocks in Sat are added as custom % loss products (only `.BK` is built in). No push; Firestore rules untouched.
