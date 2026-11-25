# CL2 — UI clean-up: English everywhere the user looks · no browser pop-ups in trade flows · accurate limit wording

Branch from fresh origin/main (after HW2 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-cl2 -b claude/cl2 origin/main`. First commit = this brief. UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md`. Locked brief. Keep tests/run_tests_e2e1.py green.

## A · Find what the user actually sees in Thai (inventory first)
The file has ~1,000 non-comment lines with Thai — most are legacy/hidden. Do NOT translate blindly. Reuse the E2E1 crawl: with seeded data, visit every tab and segment (Today Daily/Weekend, Plan all segments, Flow, Watch all views + detail + Homework page, Journal, Port, Settings every card) and open every sheet/menu reachable by one click (skip delete/external). Collect every visible text node containing Thai (`/[฀-๿]/`), with the screen + element. Write `docs/reports/CL2-thai-inventory.md` (screen · text · source line).
Translate every item in that inventory into short plain English matching the words already used around it (Move stop · Cancel · Save · Filled · Entry price …). Data values the user typed stay as typed. Hidden legacy code that is never rendered: leave it.
Known examples: weekly-close price sheet; `sat7dMarkOpen` prompt "ราคาเข้าจริง" / alert "ราคาไม่ถูกต้อง".

## B · No browser pop-ups in the trade flows
The file uses `prompt(` ×3, `alert(` ×64, `confirm(` ×25. Browser dialogs can be blocked or look broken (Safari) and are in Thai in places. Replace, in these flows only: plan save/edit, Place order, Filled (incl. `sat7dMarkOpen` entry price → a small sheet like the HF5 Price sheet, prefilled with the planned entry), Move stop, partial exit / Close, Cancel order/plan, Archive/Remove, Homework leave-with-unsaved-changes.
- `prompt` → small in-app sheet (one field, Enter = save, Esc = cancel).
- `alert` → the ⚠ line in the sheet or a toast (rule 9: say the fix).
- `confirm` → the app's confirm sheet (Enter = confirm), as Clean up uses.
List every remaining `prompt/alert/confirm` outside those flows in the report (not changed this round).

## C · Limit wording that says what it is
- `ADDON_TOTAL_RISK` (~8671): "Risk 1.5% is over today's limit 1%" → `Risk 1.5% is over the 1% limit for this stock (all lots at their current stop)`.
- `PLAN_TOTAL_RISK` (same place): keep the numbers but say `over the limit for this plan` instead of "today's limit", with the breakdown in brackets as now.
- ~9078 `Over today's limit: …` → `Over the limit for this plan: …`.
- Add stocks sheet: the selected Momentum/Compounder toggle is dark (two dark things with the Add button) → selected = white segment on grey (like other segmented controls); Add stays the only dark button.

## Tests (`tests/run_tests_cl2.py`)
- Crawl assertion (permanent, add to the E2E1 crawl): no visible Thai text on any crawled screen/sheet at 1440 and 390, except user-entered data fixtures.
- Each replaced prompt/confirm path works with keyboard (Enter/Esc) and mouse; Filled entry-price sheet records the price; no `window.prompt/alert/confirm` is called in the listed flows (spy).
- Wording checks for the 3 texts in C; Add stocks sheet has exactly one dark button.

## Screenshots (only `cl2-*.png`)
`cl2-fill-price` (390), `cl2-weekly-close` (390), `cl2-addon-blocked` (1440), `cl2-add-stocks` (390).

## Rules
Full `JOBS=2 bash tests/run_regression.sh` + hooks · revert tracked screenshot rewrites · new suite in REST= · no push until I review — report the inventory count (before → after), what was replaced in B, the remaining pop-ups list, PNG list.
