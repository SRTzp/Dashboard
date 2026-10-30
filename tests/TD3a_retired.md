# TD3a — expectation changes (old cases changed/retired because the brief changes Today)

| suite | case | change | reason |
|---|---|---|---|
| test launcher (run_tests_phase39.py `launch`) | Today items now live in the lazy "Other ▸" fold | `TD3_OTHER_OPEN=True` sets localStorage `dash.td3Other=1` for every old suite (phase106 sets False and tests the closed default) | B1: old Today items moved into Other ▸ (closed by default); setup change only, no expectation weakened |
| phase81 | tile buttons: + แผน / Clear Note / เอาออก | + "Not trading this week" | B5 new Not-trading flag button |
| phase82 | card buttons: + แผน / Clear Note / เอาออก | + "Not trading this week" | same |
| phase84 | 4 goal card at top of left column / bottom, `.glA`==2 | `[data-td3-goals]`==1 · 2 `[data-td3-acct]` · 1 `[data-gl-valopen]` | B3 Account goals box replaces the goal card |
| phase84 | 5 button 'ดูตัวเลข ▸' | 'Numbers ▸' | Today labels are English |
| phase90 | 2 Today (Mac) 2-column order | RETIRED → "3 panels top-aligned, no overflow" | B2 layout: 3 panels |
| phase94 | 1 Today 2 columns, bottoms ≤35%, mobile goal line | RETIRED → "3 panels top-aligned, no overflow" | same |
| phase100 | 6 Today news (Thai strings, 'ใกล้ประกาศ', 'อีก 25 นาที', 'ถึงกำหนด…', 'รออัปเดตผล') | English strings: `Forecast 2.6% · Previous 2.7%`, countdown `in 0:24`, `awaiting actual`; hot selector `.td3-news.hot` | B4 News box: HIGH only, English, live countdown |
| phase100 | 6 after-day: Core PCE moves to folded 'รออัปเดตผล' group | not shown next day (Today shows today's events only) | B4 |
| phase100 | 6 postponed BRENT event shown | not shown (BRENT is not HIGH in the sample) | B4 HIGH-only |
| phase100 | 6 released event leaves Today | stays, dimmed, with `actual 2.9%` | B4 |
| phase100 | 6 Update › flow | expand the (collapsed) row first via `td3EvTog` | B4 rows are collapsible |
| phase101 | 2 Sunday event fixture impact MED | HIGH | B4 HIGH-only (data change) |
| phase102 | 1 Today order (mobile list, goal line, Mac columns, bottoms ≤15%) | RETIRED → "3 panels top-aligned, no overflow" | B2 |
| phase103 | 4 tdBalance / 2 columns / Sat card moves / debounce / hidden-tab | RETIRED → "3 panels top-aligned, no overflow" | B2 (tdBalance is a no-op: no `[data-td-col]`) |
| phase104 | 2 Today 'ครั้งก่อน (Sep 2026) 2.7%' | 'Previous (Sep 2026) 2.7%' | English labels |
| phase104 | 3 tdBalance (p94 fixture ≤35%, ≤15%, right-column order) | RETIRED → "3 panels top-aligned, no overflow" | B2 |
| phase105 | 7 Sectors block in right column after the goal card | Sectors block inside the Overview panel (first panel) | B2/B3 |
