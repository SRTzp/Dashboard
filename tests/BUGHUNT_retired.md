# BUGHUNT — expectation changes (no test deleted · each row = a stale expectation, UI behaviour unchanged by this branch)

| Suite | Check | Old expectation | New expectation | Why |
|---|---|---|---|---|
| run_tests_phase64.py | `3 Tier ผ่าน + Phase Up (n=2)` | clicks `[data-tq-f="pass"]` in the Filter panel; badge n=2 | step removed; badge n=1 (Phase Up only) | Tier filter chips removed on purpose in PL2 item 7 (commit 627cf37, `tqFilterHtml()` returns ''); the same suite already asserts no `[data-tq-f]` in the panel. Not a UI regression. |
| run_tests_phase64.py | `4 ปุ่ม Port … ยังอยู่เดิมนอกแผง` | Port pills text contains `Core.US` and `Core.TH` | pills end with `All US TH` | PL2c renamed the Port chips. |
| run_tests_phase85.py | `7 โหมดแบบเดิม` (1440/390/300) | legacy Watch row Port pills contain `Core.US`/`Core.TH` | pills end with `All US TH`; also asserts `📥 Import` button still present | PL2c renamed the Port chips (the buttons ✎ แก้ไข / ✕ ลบ / 📥 Import were unchanged). Not a UI regression. |
