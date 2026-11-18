# LR3 — Plan board · confirm sheet · plan forms

Branch `claude/lr3` (from `origin/main` with LR2 merged). Commits: A board → B confirm sheet → C forms → D tests / report. Hook test (`tests/hooks_test.py`) green: nothing renamed or removed (ids / `data-*` / names / inline handlers only added). Sizing, gates and the engine are untouched.

## Moved controls
- Plan header: `Plans · N planned · N ordered · N holding · open risk X% / 3%` (was `N plans · Holding N · risk in use X / 3`).
- Phone: Planned · Ordered · Holding segments moved **above** the port chips (were beside them, one row). Desktop keeps chips left / segments right.
- Port chips carry a coloured dot; the chip for a port the account hides (Family → MMT) is gone. Its plans sit under **Hidden port: MMT (n)** (a collapsed row below the columns).
- "Waiting for setup" sub-heading + cards → one collapsed row at the bottom of Planned: `Waiting · N need entry or stop ▸` (expands in place, stays open across re-renders).
- `also in F ›` / `also in M ›` pill on a card when the other account has a plan, order or holding on the same ticker (Sat: same asset). Tap = switch account, show that card, scroll to it.
- Confirm sheet (Core + Satellite): band → **Orders to place** (BUY/SELL · #qty @ price · Limit/Stop · entry k/n) → STOP row (stop · target · sell #qty) → Risk / Reward / Size tiles → Setup / news / replace-pick / warnings → `More ▾` → Not yet / Confirm → footnote. Old summary block and the separate "limited by" line moved into the tiles / More.
- Forms: Core footer is Cancel · Save draft · **Save plan**; Cancel / Save draft / Save plan are sticky on phone with ≥ 44 px buttons (Core + Satellite). Core form is one column on phone; the Targets inputs get the same input style.

## Thai strings replaced (Core form: Momentum / Compounder new + edit, Tier block, validation lines)
Account · e.g. AAPL or XXX.BK · First entry · Price levels (high to low · 2–3 levels) · ＋ Level 3 · SL (below the last level) · Budget % of the Compounder bucket · Cancel · Save plan · Close · Show other accounts (+ "N account(s) hidden — market differs from the ticker") · US+TH (was ทั้งคู่) · Enter Ticker / Enter Entry and Stop / Enter Risk % / Enter price levels · SL · budget · A card for X already exists · Tier A needs a reason · Editing a ladder plan needs Tier A / A-Fortress · No <bucket> bucket set for this account · Entry must be above Stop · Risk up to X% (Base budget · FF …) · enter less for a smaller first entry · Risk is over the Base budget · (manual · system N%) · Go to card · Save Tier only (adds to Watchlist) · Split 50 / 50 · Save new plan / Lock plan · Invalid ladder · Calculation failed · L1 gets 0 shares … · Buys the first level only · risk … · reserves … · Ladder does not meet all conditions · Remove · ladder-error texts (LEVELS_NOT_DESC …) · whole Tier block (lenses, labels, Yes / No, "Tier used", "cap", reason, Save Tier only). The satellite form had no Thai UI strings left.
The "fill-in" error prefix the form used to hide (`กรอก…`) is now `Enter …` (`/^Enter /` filter) — same behaviour.

## Open-risk source
`bdSummary` reads `lr2OpenRisk(activeAccount)` — the function Today's Act header uses (engine Active week usage ÷ week equity, cap `POLICY.active.weeklyPct`). The old "risk in use" (`bdRiskNow`, left in place) read `re1L(tdHome())` for the home account only, i.e. it ignored the active account and Core risk.

## Tests changed and why
- `run_tests_phase375.py` §4: phone now expects segments above the chips (two rows); desktop check unchanged.
- `run_tests_ef1b.py` M: sheet text now `RISK −฿540 · REWARD +฿2,836 · 5.3R` as tiles (checked case-insensitively).
- New `run_tests_lr3.py` + `lr3_sheet.py` + `lr3_forms.py`: header open risk = Today's; Family hides MMT chip + Hidden-port line; empty column shrinks; phone segments; Waiting collapse / expand / persist; `also in` only when the other account has the ticker and switches correctly (both ways); confirm-sheet order for Core, Sat and a later level (+ two-entry plan); sticky footer + ≥ 44 px at 390 (sheet and forms); no Thai UI strings in Core (7 states) and Satellite forms; Save plan / Save draft / Cancel handlers kept.

## Heights (390, same fixture, Plan tab, scrollHeight)
| | before (origin/main) | after |
|---|---|---|
| page | 1352 px, 8 cards on the board | 923 px, 5 cards |
The board now shows the **active account** only (before it listed Main and Family together); the drop is mostly that. Per card the height is unchanged; the Planned column with its Waiting row is shorter (one row instead of a heading + full cards). Confirm sheet at 390 is about the same length as before, with the Confirm button always on screen.

## Uncertain / decided without asking
- **Active-account board.** The brief says "active account, as today", but the old board listed every account's plans. I filter to the active account (needed for `also in` and the per-account header). Nothing is hidden for good: the other account is one tap away and Today still lists both.
- **Errors under the field** (brief, forms): validation lines still render in the one error block above the footer, not under each field. Moving them is a larger change in `coreNewIn`; left as is — say if you want it.
- Desktop keeps the Planned / Ordered / Holding segment control (it was already visible beside the chips, although the CSS meant to hide it); I did not remove it.
- Core sizing text in the sheet's Size tile shows the engine's `effPct` and its own "limited by …" text; "full size" when the engine reports no limit.
- Thai remains in other sheets (add-on fill, cancel, close position, Tier-only flows outside the plan form) — out of scope for LR3.

## Review fixes (second pass)
1. **Currency.** Money follows the account currency: Main (USD) shows `$` (= ฿ ÷ Settings FX) on plan cards, Today rows, the drawer and the confirm-sheet tiles; Family stays ฿. Display only (`pv.dcur` / `pv.dfx`), numbers unchanged. "x% of account" on the sheet and Size % now share one base, the engine week equity (`lr3Base` = `re1L(acct).basis.weekEquity`); before, Risk % used total equity and disagreed with Size %. Test: `partA2` (card $, tiles $, same base, no ฿ in the sheet).
2. Segment control only at ≤ 600 px; desktop shows the three columns, empty column shrinks.
3. Blocked reason = one line `Blocked · MMT weekly limit 4/4` (generic gates: first clause); full engine text under More (`data-pv-whyfull`, also the tooltip).
4. Sheet 390: "Setup ready today" is its own full-width row below the tiles, no overlap.
5. Core form 390: Cancel · Save draft · Save plan in one sticky row; `+ Entry` / `+ SL` moved into the label row.
6. Form errors sit under their field (ticker: "already exists" + Go to card; SL: "Entry must be above SL" / split). Errors without a field stay in the block above the footer.
7. Tests updated for the currency change (`run_tests_pv1`: ฿ → $) and for desktop without segments (`run_tests_phase375`).

**Full `tests/run_regression.sh`: 54/54 ok · 0 failing** (1165 s). Hooks superset PASS. `lr3-*` screenshots regenerated by that run.
