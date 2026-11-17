# PV1 progress

## Part A · A0 — reconciliation (BLOCKED: real stored data not available to me)

**What I could check**
- Arithmetic of the brief's reading: filled 11 sh @158, planned 18 @140, stop 110, FX 33.8 → (11×48 + 18×30) × 33.8 = 1,068 × 33.8 = ฿36,098 ≈ ฿36.1k; shares 11 + 18 = 29 → `#29`. Consistent with `tw1SizeRisk` (index.html ~29517), which reads `plan.ps1.qty / riskMoney / riskPct` (whole plan), not `lots`.
- Code path confirms the row is plan-total, not holdings: `re2Row` → `tw1SizeRisk(it)` → `it.ref.plan.ps1`.

**What I could not check**
- The actual stored NVDA card (lots + `plan.ps1` + price/date + FX). Live data is in the browser / Firestore, not in the repo. The newest backup in ~/Downloads (`dashboard-backup-2026-11-01-2012.json`) has no NVDA entry, and `tests/seed.json` has no NVDA Compounder card. A fixture built only from the brief's own numbers would just restate the brief, not verify it.

**Status:** no application code changed. Baseline regression on the base commit was started separately (results in scratchpad `base/`).
Needed to continue: a fresh dashboard backup JSON (taken after the NVDA buy), or the NVDA card's stored `lots`, `plan.ps1`, `px`/`pxDate` and the FX rate from Settings.

## A0 — update after reading `~/Downloads/dashboard-backup-2026-11-17-0905.json` (in place, not copied)
Found in the backup (NVDA only):
- Filled trade `t1794539144994595`: port core, Long, USD, qty 11, entry 158, sl 110 (sl0 110), mult 1, opened 2026-11-13. Matches "11 sh filled @158, stop 110".
- Settings FX: **33.76** (manual, `fxAuto:false`, updated 2026-10-26) — brief used 33.8 (rounded). With 33.76: cost 11×158×33.76 = ฿58,675 (brief ฿58.7k ✓); loss at stop on held 11×48×33.76 = ฿17,825 (brief ฿17.8k ✓).
- Watchlist entry NVDA/US/core added 2026-11-12.
NOT in the backup: the NVDA **core card** (Firestore `users/<uid>/coreCards`: `lots`, `plan.ps1.rows/qty/riskMoney/riskPct`, `px`/`pxDate`). The export contains no card collection at all (0 hits for `ps1`, `lots`, `rows`, `qtyFull`).
So the "18 planned @140", the `#29`, the ฿36.1k plan loss, and the 162.80 price/date are **unverified**. With FX 33.76 the brief's plan loss would be 1,068 × 33.76 = ฿36,056 (still ฿36.1k).
Result: filled side confirmed; planned side and price cannot be reconciled from the backup. Part A code NOT started.
Side finding: the backup/export does not include core cards (plans, lots, prices) — worth a separate look.

## A0 — FINAL reconciliation (stored NVDA card pasted by user · card `ccmwdlk56w91` · trade `t1794539144994595`)
Stored: lots = [11 @158 · 2026-11-13 · stop 110] · plan.ps1.rows = [11 @158, 18 @140] · qty 29 · div (FX) 33.76 · E 5,019,200 · stops [110] · riskMoney 36,055.68 · riskPct 0.71836 · px 162.85 (2026-11-13, auto) · mult f 0.75 (regime) · ln4.placedLv {0} (row 1 placed + filled; row 2 planned only).
Reproduce the displayed Today row (`tw1SizeRisk` → plan.ps1): `#29` = ps1.qty (11+18 all planned rows) · ฿36.1k = riskMoney = (11×(158−110) + 18×(140−110)) × 33.76 = 1,068 × 33.76 = 36,055.68 ✓ · 0.72% = 36,055.68 / 5,019,200 = 0.7184% ✓.
**Brief's reading confirmed**: the row shows the WHOLE PLAN (planned shares + loss at stop if both rows fill), not holdings. Only differences: FX is 33.76 (not 33.8), price is 162.85 (not 162.80).
Honest numbers for this holding (what posView must return): heldQty 11 · plannedQty 29 · avgEntry 158 · cost 11×158×33.76 = ฿58,675 · value 11×162.85×33.76 = ฿60,477 (1.205% of 5,019,200) · uPnl +฿1,802 (+3.07%) · openRisk 11×48×33.76 = ฿17,825 (0.355%) · toStop 11×52.85×33.76 = ฿19,627 · plannedRisk ฿36,056 / 0.718% · R = 48.
