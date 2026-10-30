# TD4a — expectation changes (old tests never deleted; each row = behaviour the brief changed)

| suite | check | was | now | brief |
|---|---|---|---|---|
| phase20 | Watch: wlOpenAdd opens add form / add ZZTEST | empty `wlOpenAdd()` + typed new ticker | ZZTEST first made a Candidate (candMeta), then `wlOpenAdd('ZZTEST')` | §4 pipeline |
| phase22 | same (Watch add ZZTEST) | same | same | §4 |
| phase29 | WT1 add modal NEWT/NEWU | new tickers added directly | made Candidates first | §4 |
| phase33 | 3 NEWX via "บันทึกเฉพาะ Tier" | button label `(เพิ่มเข้า Watchlist)` + creates doc | NEWX pre-seeded as promoted; label without the suffix; doc fields unchanged | §4 |
| phase40 | 1 / 5 Import living-thesis for new ticker | Import created the Watchlist doc | ticker pre-seeded (`promoted()`), Import then updates it; checks 1 and 5 compare the seeded doc | §4 |
| phase41 | 1 Import v3 | same | same (`P40.promoted`) | §4 |
| phase44 | 2 pills order | Watchlist · Ideas · Candidates | Ideas · Candidates · Watchlist | §1 |
| phase85 | 1 list order / header pills | AVGO → NOCARD → CALM; pill[0] = Watchlist | AVGO → CALM → NOCARD (has-data first); pills Ideas · Candidates · Watchlist | §4 sort / §1 |
| phase84 | 4 goals card | 1 `[data-gl-valopen]` | 2 (one per account, inside the expanded row) | §1 |
| phase94 | 3 BRK.B row on one line | passes with no star | passes: list row shows only a compact `★n` when rated; the rating control is in the detail header | §4 |
| phase105 | 3 / 6 caps | driver 400 · summary 800 · revisit 300; 2 textareas | 1200 · 2000 · 600; 3 textareas (revisit is a textarea) | §6 |
| phase105 | 7 Today sector row | `Improving` · Δ ▲ · driver cut at 80 chars + … | `IMPROVING · 4 d · -3.0%↗` after the name · full driver, 1 line via CSS, tap expands | §2 / §6 |
| phase105 | 9 hover layout | row measured before hover | scrolled into view first (★ now re-sorts rows) | §2 sorting |
| phase106 | B2 empty news | `No high-impact events today` | `Please check the Calendar for Major Economic Numbers.` | §2 |
| phase106 | B5 Macro header | `Macro Playbook Q4/26` | `Macro` + direction chips | §2 |
| phase106 | B6 core_tests (all) | Cand→WL 0/2 · New Candidates 0/4 · tick Tier = promote · Toast | retired (stub, original kept as `core_tests_td3a`); replaced by phase107 §3 (Cand→WL min 3, promote form, New Cand 3/10, Deep dive US/TH) + `ifnext_tests` for If-time-permits / Screen / Draft plan | FINAL Core panel spec |
| phase33 | 8 wlOpenAdd(NEWY) modal | new ticker added directly | NEWY pre-seeded in Watchlist (pipeline) | §4 |
