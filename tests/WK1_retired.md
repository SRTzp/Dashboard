# WK1 — changed / retired expectations

| Test | Old expectation | New expectation | Why |
|---|---|---|---|
| phase106 B4 item list | 7 items in 3 panels: `wk_macro, wsector, wk_news, wk_cands, wk_picks, wk_impact, wk_assets` | one list: `wk_impact, wk_assets, wk_news, wk_cands, wk_ideas, wk_stops, wk_chg` | brief §1 |
| phase106 B4 badge | starts `0/6` (`wsector` not counted) | starts `1/7` (every item counted; ⑥ Raise stops auto-ticks when no open position has a stop below avg) | brief §1/§2 |
| phase106 B4 manual tick | clicks `wk_macro` | clicks `wk_chg` (replaces weekly "Review Macro Playbook") | brief §2 ⑦ |
| phase106 B4 `wsector` | manual, not counted, ticks into `weekLog` | item removed (assert 0 rows) | "Review drivers for selected sectors" replaced by ⑤ New ideas |
| phase106 B4 `wk_cands` + `wk_picks` | two manual ticks | one `wk_cands` tick (merged ④); also tick `wk_ideas` (manual, 0 ideas) to complete the week | brief §1 merge |
| phase102 §2 "อ่านแล้ว" | `stockNewsRead == {ED: true}` | `{ED: {readIds:[all item tickers]}}` (button text "Mark all read", same `data-stk-read`) | brief §3 per-item read state; old `true` still read as "all read" |
| Today Daily line (no old assertion) | `Weekly News · n updates unread · [Read ›]` | single `<button>` `Weekly News · x/y unread ›` | brief §4 |

## Removed done-state ids (weekLog[Mon].done)
- `wk_macro` (replaced by `wk_chg`) · `wsector` (replaced by `wk_ideas`) · `wk_picks` (merged into `wk_cands`; an old `wk_picks` tick still counts ④ as done).
| phase362 PL2·4 "Satellite label kept" | page source contains `P('sat', 'Satellite'` (Weekend Satellite panel builder) | source contains the Weekend `'SAT'` group tag (`'SAT', 'Weekly Impact'`); Daily's Plans panel unchanged | Weekend no longer has a Satellite panel (one list with SAT/CORE/OVERVIEW tags) |
