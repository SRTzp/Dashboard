# RE-C2 — Today: Act in three groups + risk strip + Costs switch OFF · branch `claude/re1c2` (not merged)
Base: origin/main d828732 (RE-C1 verified on main: `risk-engine.js` + `re1-adapter.js` inlined and wired, `re1L()` live layer present).

## §0 answers
- **Account:** Today follows the existing account selector (`acctActive`, shown when there is more than one account) — strip, Act groups, Risk room all use that account only. If there is no selector (one account), one block is built per account that has any plan / order / holding, prefixed `Main` / `Family`. Accounts are never summed. Note: before RE-C2, Act listed plans of every account together; it now shows only the selected account.
- **Last price (near-entry):** only `c.px` of Core cards (cached price, already used by the board). Satellite has no price source → Satellite enters Enter by the ⚑ flag only (as the brief says). No price → the plan is not "Near". No fetch added.
- **Events / Satellite news windows:** cached Weekly Impact docs (`wiDocs`, this / adjacent weeks, impact tier HIGH / MED) + the CPI / NFP / FOMC dates in Settings (`newsEvents`, existing −60 / +30 min no-entry rule). No data → event chip hidden / "no event data". No fetch added.

## §6 Costs switch — OFF (own commit `6eba781`)
- Settings · Training now has `Costs` next to `Starter ¼`. **Set OFF once in this release** (`costsOn=false`, `re1CostsReset`); default is OFF.
- One flag, read in one place: `src.costsOn` in `re1-adapter.js` (`unitCosts`). OFF → costs known and all zero: net = gross, estimated net-breakeven price = entry, no `Unknown`, no `COST_UNKNOWN`, no `Add costs ›`. Strict sign runs on gross P&L. Saved cost values stay in the data, unread.
- Hidden while OFF: Settings cost rows, the per-trade cost override in the close form.
- Trades closed while OFF are stamped `costsOff` and read `costs not recorded`; when ON later they are never re-costed or re-labelled, and no position or order changes.
- ON = RE-C1 behaviour: the RE-C1 cost tests run unchanged with the switch ON (live test source `costsOn:true`; `run_tests_re1c` launcher turns it on).
- Tests: live layer 63 → 73 (OFF: no Unknown, breakeven = entry, stop at entry frees the Momentum idea, exit at entry is breakeven with no Momentum loss / Satellite step change, ON later never re-costs); suite re1c2 +24 (cost UI hidden at 390 / 1440, close stored as `costs not recorded`, toggling ON/OFF changes nothing). Screenshots `re1c2-costs-off-settings-390/1440.png`.
- Note: the fill form has no per-trade cost field in this build, so only the close form override was hidden.

## What was built (all in `index.html`, block "RE1-C2")
- **§1 strip:** `Act · ● state · MMT <ideas left> · <week room %> · SAT step n · <step %> · COMP <room %> · <next HIGH event>`; Normal / amber (Half size, Snapshot due, Sat reduced) / red (Locked MMT·SAT·COMP, snapshot stale / none); worst wins and the causing chip turns red and names itself. Event chip amber when a no-entry window starts within 24 h. Phone: state + abnormal chips + event chip only.
- **§2 groups:** Enter (Near ≤ 3 % or ⚑ Ready; engine-blocked rows stay with disabled button + reason) · Check orders (every working order, amber `n days · still valid?` after one day) · Manage (Move stop at +1.5R with `stop → net breakeven`, Do homework, Add-on, tripwire review; footer `n holding need nothing`). Header counts + links to the Plan column.
- **§3 ⚑ Ready:** toggle on the Planned card and in its drawer (all strategies); stores `plan.ready` / `plan.readyAt` (Sat idea: `ready` / `readyAt`); cleared by the write path when the plan is Ordered, Filled or Cancelled. Nothing but the Enter group reads it.
- **§4 bottom pair:** Risk room (same helper values as the Port block) and Next events (3 HIGH/MED, Thai time, header chip `No Sat entries …`). Mac open side by side; phone two collapsed one-line rows.

## Removed from Today
Old status text / chip in the top card (risk line `Risk · Mom …`, port pill, room text); To do items `Move stop · SYM` and `… still valid?` (now in Act); the old single Act list (max 5 + `+N more`, Fix risk row). `Snapshot due · <account>` stays in To do. The regime link of the old status chip is kept on the strip's COMP chip.

## Behaviour changes you will notice
- Act only shows what needs action; plans far from entry and not flagged are not on Today.
- Plans 2–3 % from entry now offer Place order in Enter (board still uses 2 %).
- Today shows the selected account only (see §0).
- A ⚑ Ready button appears on every Planned card and drawer.

## Tests (final run on the committed code)
| Suite | Result |
|---|---|
| engine `risk_engine_test.js` | 313 / 0 |
| adapter `re1_adapter_test.js` | 63 / 0 |
| live `re1c_live_test.js` | 73 / 0 (63 RE-C1 with Costs ON + 10 §6) |
| **new `run_tests_re1c2.py`** (390/1280/1440) | **155 / 0** (131 + 24 for §6) |
| `run_tests_re1c.py` | 203 / 0 (launcher sets Costs ON; one check re-pointed: Move stop now asserted in Act › Manage) |
| 375 | 135 / 0 · retired (RE-C2) below |
| 374 | 254 / 0 |
| 373 | 544 / 0 · retired (RE-C2) below |
| SW2 | 33 / 33 |
| re1b | 19 / 0 |
| `ui_audit` | 124 findings = origin/main 124 (rule 6: 111 vs 111; screens not ok: []) — no new findings |

**Retired checks (not counted as PASS, behaviour the brief replaces):** 375 `2 Act has plan/position rows`, `2 stock row size/risk`, `2 multi-entry size`, `2 Sat row size`, `2 every row has size + risk` (old single Act list; 4 viewports each); 373 `9 Act follows the board (Fix risk → Add-on → < 2% → check fill), max 5`; 375 `3 Today status line button` **at 390 only** (the COMP chip is hidden while Normal on the phone; Mac/1280/1440 still pass). Earlier RE-C1 retirements unchanged.

Screenshots: `tests/screenshots/re1c2-today-1440.png`, `-today-390-collapsed.png`, `-today-390-open.png`, `-locked-1440.png` / `-locked-390.png`, `-planned-ready-1440.png` / `-390.png` (git-ignored; added with `-f`).

## Unresolved / judgement calls
- **"Satellite reduced week" (amber):** the brief does not define it. I show `Sat reduced` when the Satellite week room is smaller than the current step's risk. Say if you meant something else.
- **Add-on in Manage:** shown when the existing add-on flag is set and the engine does not hard-block (locked / thesis / snapshot). The engine's full Add-on sizing is still decided in the Add-on form.
- **Order age for Core orders** uses the order's `placedAt` time (the engine's stale rule covers Satellite only).
- §1–§4 were built in one pass, so they share one commit rather than one per section.
- Older suites that read the removed status text (e.g. phase 369 / 372 / 120 `data-ln4-risk`) were not in the required reruns and were not run; they likely need the same retirement.
- `run_tests_phase375.py` writes its screenshots to `/Users/peach/Dashboard-rg2b/tests/screenshots/tw1-*` (hard-coded path), so running it touches tracked screenshot files in that folder.
