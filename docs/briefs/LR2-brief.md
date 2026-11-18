# LR2 — Lean redesign step 2: Today (glance band · one Act list for Main + Family · quiet side column)

Approved by SRTp 18 Nov 2026. Design: `docs/briefs/lr/Main.dc.html` (desktop) + `docs/briefs/lr/TodayPhone.dc.html` (390). Base: latest `origin/main` **with LR1 merged**. Branch: `claude/lr2`. Commits: 0 tab shortcuts → A glance band → B Act list (both accounts) → C side column + Risk room → D tests/report, push each.
LR1 rules apply: zero feature loss; never rename/remove an `id`, `data-*`, `name` or inline handler (`tests/hooks_test.py` must pass); each screen same length or shorter at 390; English UI; no overflow 1440 / 1280 / 390; `render()` pure; no data migration.

## 0 · Tab shortcuts follow the new tab order (first commit)
`TAB_ORDER` is still `today, flow, watch, plan, journal, mix` while LR1 shows Today · Plan · Flow · Watch · Journal · Port → set `TAB_ORDER = ['today','plan','flow','watch','journal','mix']` so keys **1 Today · 2 Plan · 3 Flow · 4 Watch · 5 Journal · 6 Port**, swipe order and slide direction match the bar; update the TD1 comment. Tab-number keys must do nothing while the New-plan chooser (`#bdPop`, its 1/2 = account keys) or any sheet/drawer is open (`bdSheetsOpen()` / `td3SheetUp()`), not only `.overlay.show`. Show the key in each tab's tooltip (`Today · 1`). Test each key + no tab switch with the chooser open.

## A · Market at a glance (replaces the Risk-ON / MACRO / GOAL block; same data, no new source)
Four equal cards in one row (desktop), one two-line amber block (phone). Each card taps through to its source (Flow / Plan / calendar).
1. **Market mood** — from the RM1 shared regime result: both green = "Risk-on", one red = "Mixed", both red = "Risk-off", unavailable/stale = "Unclear". Card tinted by mood (green / amber / amber / grey). Line 2: `New entries at <effective %> size`. Replaces the old "Risk-ON · New entries 100%" text, which must read the same `regimeState` value (no second rule).
2. **This week moves** — from Weekly Impact: up to 2 chips `XAU ▲ HIGH`, `BTC ▼ MED` (bias arrow + impact); line 2 = quiet assets. Empty → "No Weekly Impact · Import ›".
3. **Hot sectors · vs SPY** — from the shared RRG (Daily): up to 3 chips from Leading (↗, green) by strength, sector names (not tickers); line 2 = first Improving (⤴, blue) + up to 2 Lagging (↘, red). One chip row, never wraps (fixed card height).
4. **Next news** — next key event (time ICT + name + HIGH/MED) from Weekly Impact events + Settings key news days. None → "No key news this week".
All four cards same height. The old Playbook / Goal links move into the side column (C).

## B · Act — one list for Main + Family
- Act lists Enter / Check orders / Manage items **from both accounts** (Family only if it has the `core` / `satB` ports). Each row: port colour bar (TS1b), symbol, port tag, **account pill M/F** (LR1), direction, distance to entry; line 2 in card format (`Buy #0.19 @ 2,643 · SL · TP · Risk −$285 · 2.7R`, PV1b/EF1b); one primary button.
- **The row's button acts on the row's account** (Place / Filled / Keep / Homework …) without switching the active account; the confirm sheet shows that account's band (LR1). Verify every Act action path passes the row's account id.
- Same idea in both accounts = two rows next to each other (sizes differ).
- Header: `Act · Main + Family` badge · status · `Open risk M 0.36% · F 0.12% / 3% · F futures 1.8×` (futures leverage = S50 + GO notional ÷ Family equity; hide when no futures).
- Enter keeps the EF1b cap (3 closest + "+N ›"), now across both accounts.
- Account filter: none on Today (always both). The top-bar switch still sets the active account for Plan / Port / Journal.

## C · Side column + Risk room
- Desktop: right column (≈ 1/3): **To do** as a short list (port/flow tag · one line · one link, max 4 + "+N ›"), then **Details · risk · sectors · accounts** collapsed (existing content moved inside, unchanged). Phone: To do after Act.
- Playbook / Goal links from the old block become To do items when missing ("Playbook 2026 Q4 missing · Add ›"), otherwise live in Details.
- **Risk room**: show Momentum only for accounts that use it (Family hides MMT per `acctDefaults`); per-account values with M/F pills. Same numbers as before.
- Weekly News line (restored in TS1b) stays; place it under the glance band or inside To do — keep its hook.

## Tests / proof
- `tests/run_tests_lr2.py`: mood text for green/green, one red, red/red, stale (fixture); moves / hot / news cards from fixtures incl. empty states; Act shows Main + Family rows with pills; Place on an F row opens the sheet with the Family band and records to Family while the active account stays Main; Family hides MMT in Risk room; Enter cap across accounts; card heights equal; no overflow 1440 / 1280 / 390.
- Hook test superset · node suites unchanged · full `tests/run_regression.sh` = 0 failing.
- Row count at 390 before / after (Today must not get longer).
- Screenshots (`git add -f`): `lr2-today-1440`, `lr2-today-390`, `lr2-act-family-place-390`, `lr2-glance-empty-1440`.

## Report — `docs/reports/LR2-summary.md`
What moved where · data source per glance card · account routing of every Act action · tests changed and why · row counts.
