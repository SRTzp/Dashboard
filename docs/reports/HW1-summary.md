# HW1 — Homework page on Watch (Fact Sheet + your thesis)

Spec: `docs/briefs/HW1-brief.md` → `lr/HomeworkWatch2.html` (A list+detail · B page · C phone) → `HomeworkFacts.html` → older `HomeworkWatch*.dc.html` (styles only).

## What changed
- **Fields / rule.** Momentum = `my_thesis.exit` + `hw.trigger` (unchanged). Compounder = `my_thesis.why` + **`my_thesis.evidence`** (new) + `my_thesis.exit` (2 → 3 required; the only rule change). Optional: `my_thesis.unproven` (new), `hw.catalyst` (≤ 40), `next_check_*`, Momentum "Why buy". No grandfather rule. Done / `wl1CapPct` / cap logic untouched; emptying a required field after done = not done.
- **A · list + detail.** Homework column: `Not started` · `2 of 3 · Change-my-thesis missing` (`3 of 3 · not marked done` after a draft that was never confirmed) · `Done · <catalyst>` / `Done 20 Nov` · ` · adds at 50%` for holdings. Detail: header · sector line · **Why on Watch** (`it.src` → `Leaders · 12M 95 · 3M 92 · 1M 88 · from Screen 20 Nov`, else `Added manually`) · `Homework n of m` + bar + first missing · two lines (Compounder: I believe / Not proven; Momentum: Trigger / Changes if) · size line · one primary (`Continue homework ›`, done → existing Make plan / Open plan).
- **B · page** (`hwOpen(sym)`; list hidden via the existing `.full` pattern; `‹ Watch` = `hwBack()`): left Fact Sheet from `ltFacts`/`ltTrend` (legend, Business, Revenue mix, 4-quarter table with trend word, lines by group, Mgmt says, Missing, folded More facts, row tap → Formula · Period · Source (link) · note popover); fallback without `facts` (Business, ≤ 3 KPIs, 2 catalysts + "run living-thesis" line; never thesis/next/breaker). Right: Your thesis (hints, prompt line, Compare with thesis › only after typing and lazily rendered, ▸ Optional fold, Save draft · Save · mark done · Copy for AI challenge ›, size line). `wlMtDirty` guard kept (leaving with changes confirms and keeps the draft).
- **C · phone**: full-height sheet, `‹ · TICKER · Homework · n of m`, Facts | My thesis (opens on Facts when no required field is filled), 16px inputs, 44px buttons (`Mark done`), popover = inline expand. Swipe stays off (`wlMobOpen`).
- **Copy for AI challenge**: `living-thesis challenge · TICKER · track`, Fact Sheet as `label: text (kind · period · src)`, then your fields; toast "Copied — paste into Claude".

## Hook mapping (hooks superset PASS, nothing removed)
| Old | Now |
|---|---|
| `wlMtHtml()` editor | `wlMtHtml()` now returns the Homework "Your thesis" form (`data-wl-mt`, `data-wl-mt-mode=edit`, `-why`, `-exit`, `-ta`, `-draft`, `-ddisc`, `-save`=Save draft, `-msg`, `data-wl-nc-date/note` reused). Old body kept as unrendered `wlMtLegacyHtml()` (read-mode / Restore / onboarding hooks). `wlMtSave` = thin wrapper → `hw1Save(sym,false)` |
| `wl1HwHtml()` panel | now one line in the Full-thesis view (`data-wl1-hw`, `-state`, `data-wl1-fill` → opens page); old panel kept as `wl1HwLegacyHtml()`. `data-wl1-trigger`, `data-wl1-confirm`, `data-wl1-hwi` reused on the page fields / Save · mark done. `wl1HwConfirm`→`hw1Save(...,true)`, `wl1Fill`→`hwOpen`, `wl5Hw`→`hwOpen`, `wl1HwTrigger` unchanged |
| WL2 "Use this thesis ✓" | not rendered; `wl2UseThesis`, `wl2CanUse`, `data-wl2-use` stay as dead hooks |
| old detail panel (Why/Trigger/Exit, `data-lr5-f=why/trigger/exit`) | `wl5DetLegacyHtml()` kept unrendered; `data-lr5-f=trigger/exit/why`, `-sector`, `-rs`, `-main`, `-empty`, `-det-chip`, `-close`, `data-wl2-holdings`, `data-lr5-rs-link`, RS card kept |
| `wl5Full`, ⋯ › Full thesis | unchanged (clears the homework page) |

## Retired / changed old checks (no suite deleted)
- `run_tests_wl2.py`: RETIRED ×3 per width — "From living thesis" block, RS card above it, "Use this thesis ✓" flow (button no longer rendered). "From living thesis" dropped from the phone-sheet text check.
- `run_tests_lr5a.py`: homework cell expectations (`Done 8 Nov`, `Done 12 Nov…`, phone `Industrials · Done 8 Nov`) · detail checks → Trigger / Changes if lines, `Continue homework ›`, header `· Momentum`, sector `Tech ↘ vs SPY`; hint line gone.
- `run_tests_phase374.py`: Compounder fixtures need `evidence` (3 fields); `1 of 2 · Trigger missing`; Full-thesis block is one line; Trigger box / confirm button now on the Homework page (`hwOpen`).
- `run_tests_phase365.py`: keeps testing the old My Thesis editor by pointing `wlMtHtml` at `wlMtLegacyHtml` inside `view()` (68/68).
- `tests/run_regression.sh`: + `run_tests_hw1`.

## Differences from the mockup
- Detail panel keeps the existing grey RS card (4-wk-ago, returns, TradingView link) and a `Holdings ↗` link, so the sector line has no RS / % from high (those are in the card). Momentum shows Trigger / Changes if (mockup is Compounder only).
- List Homework text can ellipsis in the narrower column at 1440 with the detail open (full text in the tooltip).
- Mockup tags `reported` → `rpt` (per the brief legend); live fonts/spacing follow the `--lr-*` tokens.
- No real `hw.confirmedAt` data was visible to me; none in fixtures. Please check Firestore: any item with `hw.confirmedAt` that is Compounder will drop to "not done" until `evidence` is written (by design, no special-casing).

## Proof
- `tests/run_tests_hw1.py` 222/222 (1440 · 390 · 360, incl. no overflow), `tests/hw1_side.py` → `tests/screenshots/hw1/{A-1440,B-1440,C-390}-side.png`.
- Hooks superset PASS · rs1/rs2 selftest PASS · final `JOBS=2 bash tests/run_regression.sh`: **73/73 ok, 0 failing** (1959 s).
