# PV1 progress

## Part A · A0 — reconciliation (BLOCKED: real stored data not available to me)

**What I could check**
- Arithmetic of the brief's reading: filled 11 sh @158, planned 18 @140, stop 110, FX 33.8 → (11×48 + 18×30) × 33.8 = 1,068 × 33.8 = ฿36,098 ≈ ฿36.1k; shares 11 + 18 = 29 → `#29`. Consistent with `tw1SizeRisk` (index.html ~29517), which reads `plan.ps1.qty / riskMoney / riskPct` (whole plan), not `lots`.
- Code path confirms the row is plan-total, not holdings: `re2Row` → `tw1SizeRisk(it)` → `it.ref.plan.ps1`.

**What I could not check**
- The actual stored NVDA card (lots + `plan.ps1` + price/date + FX). Live data is in the browser / Firestore, not in the repo. The newest backup in ~/Downloads (`dashboard-backup-2026-11-01-2012.json`) has no NVDA entry, and `tests/seed.json` has no NVDA Compounder card. A fixture built only from the brief's own numbers would just restate the brief, not verify it.

**Status:** no application code changed. Baseline regression on the base commit was started separately (results in scratchpad `base/`).
Needed to continue: a fresh dashboard backup JSON (taken after the NVDA buy), or the NVDA card's stored `lots`, `plan.ps1`, `px`/`pxDate` and the FX rate from Settings.
