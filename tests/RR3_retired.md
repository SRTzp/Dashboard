# RR3 — test expectations intentionally changed

| Suite | Old expectation | New expectation | Why |
|---|---|---|---|
| run_tests_phase86 "5 แถบสถานะ…" | refresh button text "รีเฟรชราคา" (and "rrg v" in the name) in `#ffRrgBar` | refresh is the icon button `↻` (`[data-rrg-refresh]`, tooltip "Refresh prices"); "rrg vN" moved into the ⧉/↻ tooltips | RR3 §1: icon-only controls, debug build id off-screen |

Pre-existing failures on origin/main, untouched: run_tests_phase105 (waits for `[data-sd-hd="IGV"] .l2 .g`, fails identically with RR3 stashed), run_tests_phase110 (needs untracked `index.backup-pre-SET1.html`).
