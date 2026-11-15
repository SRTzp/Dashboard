# RE-C2 — Today: Act in three groups + risk strip (2026-11-15)
Branch `claude/re1c2` from origin/main **after RE-C1 is merged** (if `risk-engine.js` wiring from RE-C1 is not on main, stop and say so). Don't merge. Mockup (settled): `docs/briefs/mockups/today-act.html` (Mac + iPhone 390; `#open` opens the iPhone rows).
Authority, in order: this brief → the mockup → `RE1-C1-brief.md` → `RE1-answers-A.md` → `RE1-decisions.md` rev 2 → `RE1-tech-spec.md`.
Rules that never bend: Today is display + shortcuts only — every number, state and block reason comes from `risk-engine.js` through the adapter (reuse the Port risk-block helpers, no second calculation) · no automatic resize or change of positions/orders · fills and closes always accepted and flagged · no data deletes · no network fetch from Today · existing look and tokens · no overflow at 360 / 390 / 1280 / 1440.

## 0. First (report in the summary)
- How Today chooses the account now. Default: follow the existing account selector; if there is none, show one strip line per account that has any plan, order or holding, prefixed `Main` / `Family`. Accounts are never summed.
- Which data sources already exist for last price (near-entry check) and for events + Satellite news windows. Use them as cached; if one is missing, show `—` and say so — do not add a fetch.

## 1. Act header — risk strip
`Act · ● <state> · MMT <ideas left> ideas · <week room %> · SAT step <n> · <step risk %> · COMP <room %> · <next HIGH event, Thai time>`
- State: `Normal` (green) · amber: `Half size` (Emergency), `Snapshot due`, Satellite reduced week · red: `Locked` (Momentum 4 ideas, Satellite Step 4 lock, Compounder six-loss lock), snapshot older than 14 days. Worst state wins; the chip of the strategy that causes it takes the same colour and names it (`MMT locked`, `SAT locked`, `COMP locked`).
- Event chip amber when a Satellite no-entry window falls inside the next 24 h, otherwise neutral; hidden if no event data.
- iPhone: state + abnormal chips + event chip only (normal strategy chips hidden).
- The old status text in the top card is removed. To do and Daily / Weekend stay untouched above.

## 2. Act — three groups, only items that need action
Columns on Mac (3), flat list with small group labels on iPhone. Header: name · count · link to the Plan board column (`7 planned ›`, `1 ordered ›`, `3 holding ›`; count = all items in that column, not only the shown ones).
Row = 2 lines. Line 1: symbol · strategy tag (MMT / SAT / COMP) · status chip · action button. Line 2: size + risk % · levels · reason (amber when it asks for action). iPhone: line 1 = symbol · tag · size + risk · short button; line 2 = reason · levels. One line each, ellipsis, never wraps.
- **Enter** — Planned items that are (a) stocks with last price within 3% of entry: `abs(price − entry) / entry ≤ 3%`, chip `Near`, marker = signed distance of price from entry (`+1.4%`); or (b) flagged ⚑ Ready (chip and marker `⚑ ready`). Satellite enters this group by the flag only. Button `Place order ›` = the existing flow and gates; when the engine blocks, the row stays, the button is disabled and line 2 shows the reason (RE-C1 behaviour).
- **Check orders** — every working order; button `Filled ✓`. Older than one day → amber `n days · still valid?`.
- **Manage** — holdings with an open action only: `Move stop ›` at ≥ +1.5R while the stop is not confirmed at net breakeven (line 2 `stop 165 → 171.60 · move stop · frees 1 idea`), `Do homework ›` (Compounder, thesis not done, `cap 50%`), `Add-on ›` when the engine allows it, plus any existing per-holding Today reminder (tripwire etc.). Footer `n holding need nothing`.
- Empty group: Mac shows a muted `Nothing to enter / check / manage`; iPhone hides the group.
- To do no longer repeats `Move stop · SYM` and `… still valid?` (they live in Act now). `Snapshot due · <account>` stays in To do.

## 3. ⚑ Ready flag (additive data only)
Toggle on the Planned card and in its drawer, all strategies. Stores `ready` + time on the plan. Clears itself when the plan becomes Ordered, Filled or Cancelled. Nothing else reads it — it never sizes, gates or places anything.

## 4. Bottom pair
- **Risk room · this week** — Momentum · week (`3 of 4 ideas` / `room 1.35% of 1.80%`), Satellite · week (`Step 2 · 0.30%` / `−0.20% of 1.20% · queue free|busy`), Compounder · **open now** (`room 4.0%` / `heat 2.0% of 6% · regime 75%`). Same values as the Port block of that account.
- **Next events** — next 3 HIGH / MED events, Thai time, impact chip, affected assets; header chip `No Sat entries <day hh:mm–hh:mm>` from the existing news-window rule.
- Mac: both open side by side. iPhone: two collapsed one-line rows (title · one-line summary · chip) that open full width.

## 5. Tests and screenshots
New suite `tests/run_tests_re1c2.py` (390 / 1280 / 1440): strip states (Normal, Half size, Locked per strategy, Snapshot due / stale) · Enter by 3% boundary (2.9% in, 3.1% out, no price → out) · Satellite never auto-enters · Ready set / cleared on Ordered · blocked row keeps a disabled button + reason · every working order listed, `still valid?` after one day · Manage shows only actionable holdings and the footer count · header counts and links · To do no longer duplicates the two items · Risk room equals the Port block · events in Thai time + no-entry chip · iPhone rows collapsed and open · two accounts never mixed · no write changes a position or order quantity.
Rerun engine, adapter, live, `run_tests_re1c`, 375, 374, 373, SW2, re1b; `ui_audit` counts compared with main (no new findings).
Screenshots `tests/screenshots/re1c2-*.png` (no animation): Today 1440, Today 390 collapsed, Today 390 open, one Locked state, Planned card with ⚑ Ready.
Commit, push, compare URL, `docs/reports/RE1-C2-summary.md`: answers to §0, what was removed from Today, behaviour changes the user will notice, anything unresolved.
