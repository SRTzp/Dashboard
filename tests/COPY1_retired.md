# COPY1 — Idea Export JSON is copy-only

| Test | Old assertion | New assertion | Why |
|---|---|---|---|
| tests/run_tests_phase44.py check 7 (Export) | Export triggers a download `{id}_idea_YYYYMMDD.json` | No download fires; message "คัดลอกแล้ว — แนบให้ idea-scout pick/update" still shown | ideaExport no longer calls ideaDownload. If both clipboard paths fail, a sheet with a selectable textarea opens (no file). |

Unchanged: ideaDelDo backup download, bkTriggerDownload.

Note: phase44 static check 'tests/_bk_id1/ exists' fails on main too (directory absent) — unrelated, pre-existing. Result: 143 pass / 1 pre-existing fail.
