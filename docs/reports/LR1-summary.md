# LR1 — Lean redesign step 1: shared styles · top bar · M/F tags · per-account defaults

Branch `claude/lr1` (from origin/main, RV1b merged). Commits: A0 hooks → A styles → B top bar → C tags + defaults → D tests/report.

## Hook inventory (tools/hook_inventory.py · tests/hooks_test.py)
| | baseline (origin/main) | branch |
|---|---|---|
| ids | 541 | 542 |
| `name=` | 6 | 6 |
| `data-*` attribute names | 747 | 752 |
| static `data-*` values | 478 | 479 |
| inline handler events | 18 | 18 |
| inline handler functions | 717 | 722 |

Superset holds (additions only). `tests/hooks_test.py` is in `run_regression.sh`.

## Moved / changed controls (ids and handlers unchanged)
| Control | Before | Now |
|---|---|---|
| Tabs `#tabBtn*` | Today Flow Watch **แผน** Journal Port | Today · **Plan** · Flow · Watch · Journal · Port (DOM order changed; `data-t="แผน"`, ids, `switchTab`, key hints 1–6 kept) |
| `#hdrPlanBtn` | icon ＋ | primary "＋ New plan" (phone "＋ Plan"); `goPlanTop()` |
| 🛠 `openSystemSettings()` | header icon | ⋯ menu → "System settings" |
| portfolio icon `openSettings()` | header icon | ⋯ menu → "Portfolio settings" |
| industry icon `openIndustryManager()` | header icon | ⋯ menu → "Industries" |
| `moreMenuGo('settings'/'system')` items | visible | kept, `hidden` (handler contract; the moved buttons are the visible entries) |
| Account switch `#acSw` | dot + name | M / F pill + name (phone: pill only; the old `.acSwL.p` letter is now the pill) |
| Sync status `#brandSync` | unchanged (text still Thai: it is referenced by Thai alerts) | phone: dot on the logo corner |

## CSS added (A) — `--lr-*`, light + dark
ground/card/line/line2/ink/on-ink/text2/muted/seg · gain/loss/warn (+ink/bg) · SAT/MMT/COMP (+bg) · acc-m / acc-f · radii 10/14/999 · type scale 26/18/15/14/13/12/11 · `--lr-sans` Inter, `--lr-mono` JetBrains Mono. Classes: `.lr-btn(.pri/.ghost)`, `.lr-acc(.lr-acc-m/-f)`, `.lr-chip`, `.lr-tag`, `.lr-card`, `.lr-seg`, `.lr-lbl`, `.lr-num`. (Pill modifiers are `lr-acc-m/-f`, not `.m/.f`, which collide with global `.f`/`.m`.)

## Per-account defaults (C)
`book.settings.acctDefaults` per account — additive, nothing migrated; built-ins apply until edited (Settings › Accounts › Defaults for new plans).
- Main: markets US (default) + TH · USD (+THB) · ports MMT, COMP, SAT · brokers IBKR, Webull · SAT XAUUSD, BTCUSD, S50, BRENT.
- Family: market TH · THB · ports COMP, SAT · SAT S50, GO.
- Pre-fill only: market segment (US·USD | TH·THB) in the new-plan form (switching adds/removes `.BK`), account picker also accepts an account's allowed markets, SAT asset list ordered by the account's products (others still listed), New-plan chooser / form switch hide Momentum in Family (key S falls through to Compounder).
- Family MMT data is never hidden: one line "Hidden port: MMT (n)" (`[data-lr-hidden-port]`) lists it.
- Place confirm sheets (Momentum/Compounder and Satellite) start with an account band: `M · Main account · IBKR · US · USD · records to Main only` (F magenta). Satellite market = TH for THB products, else US; broker = first default broker (omitted when none).

## Tests changed and why
- `run_tests_aw1.py`: `.hbtns>button` ≥ 4 → ≥ 2 (tools moved into ⋯).
- `run_tests_ts1b.py`: the ＋ hit-test uses `contains()` (button now holds label spans).
- New `run_tests_lr1.py` (104 checks × 3 widths incl. tabs, ⋯ handlers, pills, band text, Family/Main forms, market switch, defaults write, overflow 1440/1280/390), added to `run_regression.sh`.
- Hook baseline = origin/main `index.html` (unchanged by RV1b).

## 390 px page height (px, before → after)
Today 893 → see final run below; header row 50 → 50. Phone touch targets are ≥ 44 px (bottom bar 44, account/＋/⋯ 44).

## Not done in LR1 (later steps)
English sync text; hiding Momentum in the Core page-level switch / Risk room for Family (data stays visible); Today/Plan layout (LR2/LR3).
