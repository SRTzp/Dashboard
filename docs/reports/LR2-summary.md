# LR2 — Lean redesign step 2: Today (glance band · one Act list · quiet side column)

Branch `claude/lr2` (from `origin/main` with LR1). Brief: `docs/briefs/LR2-brief.md` · design: `docs/briefs/lr/Main.dc.html`, `TodayPhone.dc.html`.
Commits: `0` tab shortcuts → `A` glance band → `B+C` Act list + side column (one commit — the two share the same render functions and could not be split without a broken middle state) → `D` tests / report.
Zero feature loss: `tests/hooks_test.py` (ids · names · data-* · inline handlers) = PASS (superset). No data migration; `render()` stays pure; English UI.

## What moved where

| Before | Now |
|---|---|
| `TAB_ORDER` today·flow·watch·plan… | `today·plan·flow·watch·journal·mix` → keys 1 Today · 2 Plan · 3 Flow · 4 Watch · 5 Journal · 6 Port; swipe/slide follow the bar; tooltips `Today · 1`; digits ignored while `#bdPop` chooser, a sheet or a drawer is open |
| Status card: Risk-ON · HOT · MACRO · GOAL · SIZE · TODAY events · To do | **Glance band**: 4 equal cards (desktop) / one 2-line block (phone). HOT · MACRO · GOAL · SIZE · TODAY events (all hooks) → Details |
| One Act block per account (active account only) | **One Act list for Main + Family** (rows from `re2Model` per account, sorted closest-first, same symbol on both accounts adjacent) |
| Risk room + Next events under Act | **Inside Details (collapsed) on every width**: ONE card, one line per account × port (`M · MMT 1 of 4 ideas · room 1.68% / 1.8%`, `M · SAT step 1 · room 1.2% / 1.2%`, `F · COMP room 6% / 6% · regime 100%`) — no tiles, no truncation at 1440 / 1280; Family has no Momentum line; locked / reduced shows as a small chip on its line |
| To do = chips in the status card | **To do** = short list in the side column (desktop, ≤4 + `+N ›`) / after Act (phone, ≤3): tag · one line · one link. Grouped items (living-thesis / homework) = one row that opens the stock chips |
| Weekly News line (TS1b) | Same hook, under the glance band |
| Act strip chips (MMT/SAT/COMP room, `N not taken`, event chip) | State (now the Regime-details button) + cause + `N not taken` per account in the Act header. The old strip markup is kept visually hidden (`.lr2-vh`, aria-hidden, `tabindex=-1`) so every hook stays — nothing is shown twice |
| Daily / Weekend switch alone on a row | Page-header row: **Today** · date on the left, switch on the right (no empty band above the cards) |

## Glance data (no new source)
1. **Market mood** — `rm1Regime()` (RiskEngine.regimeState): green+green = Risk-on · one red = Mixed · red+red = Risk-off · unavailable / stale / demo = Unclear (tints green / amber / amber / grey). Line 2 = `rm1Eff().pc` ("New entries at N% size"). `tdRegimeVerdict()` now calls the same `lr2Mood()` — one rule.
2. **This week moves** — Weekly Impact current doc (`wiCurDoc`, `wiTier`) + Playbook bias (`bdBias`): up to 2 HIGH/MED chips `XAU ▲ HIGH`; line 2 = the quiet assets. No doc → "No Weekly Impact · Import ›".
3. **Hot sectors · vs SPY** — shared RRG Daily rows (`ffState().rrg.rowsD`): ≤3 Leading by strength (↗), first Improving (⤴), ≤2 Lagging (↘); one non-wrapping chip row; fixed card height. Names come from `LR2_SEC` — an explicit short name for **all 23 RRG symbols** (e.g. XLC → Comm, ITA → Defense, SMH → Semis, XLY → Cons. Disc.; tested: ≤12 chars, never the ticker). The old HOT line in Details uses the same names. Phone: line 2 = ≤2 moves chips + ≤2 hot chips + `+N`, no `Hot:` label.
4. **Next news** — `re2EvData` (Weekly Impact events + Settings key-news days), HIGH/MED within 7 days; time in ICT. None → "No key news this week".
Taps: mood → Flow ▸ Regime · moves → Flow ▸ Weekly Impact · hot → Flow ▸ Leadership · news → calendar.

## Account routing of every Act action (never switches the active account)
Rows carry `it.acct` (card `c.acct` / idea `accts` · `pb_acct`). Verified paths:
- **Place** (core) `ln4Place → efCorePlaceOpen(id)` → sheet band `lrBandCore(it)` = the row's account → `efCorePlaceYes → bdWriteWithLog(it …)` writes that card. **Place** (Sat) `pb2PlaceOpen(id)` → `lrBandSat(i)` / `pb2AcctOf(i)`.
- **Filled** `bdFill → ln4RecordFill(id)` → `coreBuy1Open(id)` (card) / `pb2Filled(id)` (`acc = pb2AcctOf(i)`, `getBook(acc)`).
- **Keep / Cancel plan / Update levels** `re4Keep / re4Open / bdEditLv (id)`; **Move stop** `coreStopOpen(id)`; **Add-on** `bdAddon → coreBuyAddOpen(id)`; **Homework** `td3HwGo(sym)`; **Review** `td3Screen(sym)`; **Fix / Complete** `bdFix / bdComplete(id)`; **Execution review** `re4ReviewOpen('<acct>')` per account chip.
All take an item / card id, never `acctActive`. Test: Place on an F row opens the sheet with the Family band, records `ln4.placedAt` on the Family card only, `acctActive` stays Main; Filled on an F order opens that Family card's dialog.
Header: `Act · Main + Family` · worst state (+cause) · `Open risk M x% · F y% / 3%` (= engine Active week usage ÷ week equity per account, cap = POLICY.active.weeklyPct) · `F futures n×` (open S50 + GO notional ÷ account equity; hidden when none).

## Tests
New `tests/run_tests_lr2.py` (136 checks · 1440/1280/390): tab keys + chooser/sheet guard · mood ×6 fixtures · moves/hot/news incl. empty states · equal heights · no-wrap chip row · tap-through · Act rows both accounts + pills · Place routing · futures · Enter cap across accounts · side column / Details / To do / Risk room (Family hides MMT) · no overflow · page height guard.
Adjusted (and why — layout changed, behaviour kept): `phase370` (HOT/MACRO/GOAL now inside Details), `phase372` (regime is a glance card; HOT fits the side column), `phase375` (2 accounts → 2 strips), `phase367` / `phase_ht1` (To do is a list in the side column; stocks open from a grouped row), `re1c2` / `re1d` / `aw1` (Today shows both accounts; strip lives in the Risk room card; chip carries the account pill), `ts1b` (scroll to top before hit-test), `lib_phase38` (new tab order), `re1d_common` (phone keeps Details open).

## Row count / height at 390 (same fixture: 3 Main plans incl. one working order; Details collapsed)
| | rows | page height |
|---|---|---|
| before (origin/main + LR2-0) | 12 | 975 px |
| after, Main only | 10 | 1002 px (+2.8 %) |
| after, + one Family plan row | 13 | 1071 px |
The +27 px is the account pill / direction / 2-line header; the glance band, To do list and collapsed Details saved the rest. **Today at 390 is therefore not strictly shorter (+2.7 % in that fixture)** — flagged for review.

## Follow-up fixes (this round)
1. Risk room → Details, one line per account × port (above). 2. Page-header row with the switch. 3. Short sector names for every RRG symbol (+ HOT line). 4. Phone glance 2 lines, ≤2 hot chips + `+N`, no orphan label. 5. To do card left-aligned (title at the card padding, rows flush, no tinted box; was inheriting the old centred `.todo r` styles). Tests: `run_tests_lr2.py` now 150 checks (risk lines per account × port, no clipping / tiles / visible duplicate strip chips, header row, name map ×23, To do alignment, phone glance). Adjusted: `re1c2` (no per-account summary tiles any more), `aw1` (risk-room state read from the hidden chip). Phone page height with the same fixture: **1002 px vs 975 before (+2.8 %)**, rows 10 vs 12.

## Full regression (`bash tests/run_regression.sh`) — final state
**53/53 ok · 0 failing · 1119 s** (node + every browser suite). Hook test (`tests/hooks_test.py`): PASS, superset of baseline.

## Notes
- B and C are one commit (see top). The brief's "Verify every Act action path" was done by reading the paths above plus the Place/Filled tests; Sat Place/Filled on a Family idea share `pb2AcctOf` and were not separately exercised.
- Phone: Risk room + events cards live inside Details (collapsed) to keep the screen short; state and `N not taken` stay in the Act header.
