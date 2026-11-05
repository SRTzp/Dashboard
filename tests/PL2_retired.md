# PL2 — expectation changes (no test deleted · each row = behaviour the PL2 brief changed)

| Suite | Check | Old expectation | New expectation | Why |
|---|---|---|---|---|
| run_tests_phase100.py (line 277) | `4 2026-10-03: Strategy ↔ Weekly Impact` | Saturday: Weekly Impact week = Monday before (2026-09-28) | Saturday: Weekly Impact week = upcoming Monday (2026-10-05); Strategy week key unchanged (2026-09-27) | PL2 item 1 / D1 — Saturday runs are for next Monday |
| run_tests_phase111.py | `Classify เหลือแค่ Clear Trend / Unclear` | `<select data-pf-classify-sel>` has options Clear Trend/Unclear | no dropdown; two checkboxes `[data-pf-ema50]` + `[data-pf-structure]` in `[data-pf-verify]` | PL2 item 6 |
| run_tests_phase111.py | `ข้อมูลเก่าแสดงชื่อใหม่ (Strong/Normal → Clear Trend …)` | select value mirrors legacy value | legacy value still displayed (badge) and stored; no select; third tuple member = legacy-derived key | PL2 item 6 (legacy rule: stored classify used until verification saved) |
| run_tests_phase111.py | Tactical hint / block / Today status texts | `Tactical needs Clear Trend`, `Needs Clear Trend` | `Tactical needs EMA50 + Structure verify`, `Needs EMA50 + Structure verify` | PL2 item 6 (message rename) |
| run_tests_phase111.py | `tfield().cls` helper | select disabled | any Verify checkbox disabled | PL2 item 6 (helper follows markup) |
