# LR-F2 summary — Today follow-ups (items 1–9)

Branch `claude/lrf2` (from `origin/main` after LR-F merged). No change to `risk-engine.js`, `re1-adapter.js`, `pos-view.js`, `core-size.js`, `ps1-size.js`. No `id` / `data-*` / `name` / inline handler removed (hooks superset PASS).

## Proof
Side-by-side (mockup left, live right), rebuilt with `LRF=today python3 tests/lrf_side.py` (run from `tests/`):
`tests/screenshots/lrf/today-390-side.png` · `today-1440-side.png` · extra live-only full phone page `today-full-390-live.png` (To do → Risk room → Details).
Fixture is now a **2-account book**: Main (as before) + Family = XAU same idea (Family size) · MSFT core plan · open S50 futures (`F futures 1.8×`).

## What changed
1. **MANAGE row line 2** = `Held #11 · Stop 110 · If stopped −$528 · Next Buy #18 @ 140` (`re2HoldLine`; every part optional, money in the account currency). Same nowrap + ellipsis rule on the phone.
2. **To do text**: a leading emoji in stored text is stripped (`lr2NoEmoji`, applied to every item).
3. **Family rows**: `Place · F` button label on every non-Main account row (Main stays `Place`); `· same idea, Family size` after the direction when the same symbol also sits on the other account (desktop; hidden on the phone line 1 to keep rows at 2 lines); `F futures n×` already in the open-risk line, now shown by the fixture.
4. **Plan card at 390/360**: Risk and Reward stay on one line even with `#0.9911` (12px, 7px gaps, nowrap). No lot rounding.
5. **`run_tests_ef1b.py`** updated for $ on Main and the 2-row phone cap, and **added to `run_regression.sh`** (not retired — it still covers the sheet, level sheet and Today Enter rows that lrf tests do not).
6. **Risk room** (phone: one line per account, see Honest notes) is its own card (same style as To do) in the side column: desktop under To do, phone after To do. One line per account × port (`M MMT 3 of 4 ideas · room x / y`, `M SAT step 1 · room …`, `M COMP room … · regime 60%`; Family SAT + COMP only), locked / reduced chip at the line end. No snapshot → one line `Risk room — confirm a snapshot in Settings ›` (opens Settings). Hooks `data-lr2-risk` / `data-re2-room` / `data-re2-rr` kept. Details keeps events, sectors, accounts.
7. **Weekly News** is a To do row `NEWS · Weekly News · n unread · Read ›` (`data-td3-wnews`, same button class and `stkOpenView()` handler); the line under the glance band is gone; the row disappears when read. Not shown in Weekend mode (as before).
8. **Today header = ONE row** on all widths: desktop `Today  Thu 19 Nov · US market opens 21:30 ICT ··· [Daily | Weekend 2/7]`; phone `Today  Thu 19 · US 21:30 ···`; at ≤ 380px the `· US 21:30` part is dropped (full text stays in the date's `title`). Title, date and control share one baseline.
9. **Form inputs** (Core new / edit, Satellite new / edit, sheets): Inter 600, tabular numbers, ink colour, muted placeholders; 16px ≤ 600px, 15px on desktop. `＋ Entry` / `＋ SL` are plain text buttons (no border, background or shadow).
10. **Core "Record buy #1" sheet** (`coreBuy1Open` / `#cbErr`): fully English (title, labels, errors, buttons). The over-limit message is now plain numbers — `Over today's limit: 21 sh @ 282 risks $504, limit allows 18 ($432). Recorded anyway; new risk is reduced until it fits.` — from the new `re1FillInfo`; when the cause is the budget (MONEY_WEEK / MONEY_MONTH / AMMO_EXHAUSTED / COMP_HEAT / ADDON_TOTAL_RISK / snapshot) the engine's own `reasonTexts` line is shown instead (+ the same "Recorded anyway…" tail). Shown as an amber warning (`.ccErr.ccAmber`, same `#cbErr` hook), Save stays enabled; real errors stay red and disable Save. The Add-on buy sheet (`coreBuyAddOpen`) is not part of this item and is unchanged.
11. **Confirm sheet**: the visible `Setup ready today` checkbox is gone. Confirm always records `tvSetup[KEY] = today` (same `glWrite` as when it was ticked); the `data-ef-setup` label and `#efSetupCk` stay in the DOM, hidden and checked. The level sheet (no tick) is unchanged. Watch then shows `Setup ✓` (`tv1GroupOf`).

## Tests
- New `tests/run_tests_lrf2.py` (123 checks at 390 / 360 / 1440, in `run_regression.sh`): manage line, emoji, Family label / same idea / futures, Risk room card placement + lines + no-snapshot line, News row (shown, handler, disappears), header one row + baseline + date format per width, every form input font-size / weight / family / tabular numbers, record-buy sheet (numbers, amber, budget text, no Thai), Confirm writes tvSetup without touching anything.
- Updated for deliberate changes: `run_tests_lr2.py` (Risk room outside Details, date format, height guard), `run_tests_phase366.py` (News row), `run_tests_pv1.py` (manage line text), `run_tests_ef1b.py`, `lr3_sheet.py` + `run_tests_ef1b.py` (Setup tick hidden), `lib_phase24.py` (rounded-down text), `run_tests_re1c.py` (recorded-anyway text).

## Honest notes
- **Today at 390 height**: 922 px (after LR-F) → **996 px** with the Risk room card open (limit 1004 = 975 + 3 %). First cut (one line per port, 5 lines) was 1058 px; the phone now shows ONE line per account (`M MMT 3/4 · SAT step 1 · COMP 0.6/1.25%`, `F SAT step 1 · COMP 0.3/1.25%`), a locked / reduced port's segment in red / amber. Desktop keeps one line per port. The lr2 height guard is the original strict one again (includes the card).
- Main XAU stays Blocked in the fixture (one-Satellite-queue rule, BTC held); the Family XAU row is the visible one.
- Pre-existing console error `fmt0 … toLocaleString` from `ps1SumHtml` in the lrf_side fixture (also on main); not touched.
