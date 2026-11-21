# NT1 — Watch › Ideas first · AI generated | My ideas · idea notes · Journal › Reviews

Branch `claude/nt1` (from `origin/main` at FS2 #92). Brief `docs/briefs/NT1-brief.md`, mockups `lr/IdeasAI.html` + `lr/TradeNotes.html` (first commit).

## ⚠ Before My ideas works — paste this Firestore rule (NOT deployed)
Add inside the existing `match /users/{uid}` area of the rules, then publish (snippet: `docs/proposals/firestore-ideas-my.rules`):

```
match /users/{uid}/ideas_my/{doc} {
  allow read, write, delete: if request.auth != null && request.auth.uid == uid;
}
```
Until it is there My ideas shows `Could not load My ideas (permission-denied) · Retry` (Retry works once the rule is live); AI generated is unaffected.

## What changed
- **Watch order** Ideas · Momentum · Compounder · Screen; Watch always opens on Ideas (deep links — stock, Screen rows, Homework ›, Today lines — still open their own segment). Tab / Shift+Tab / phone swipe follow the new order.
- **Ideas = `AI generated | My ideas`** (←/→ switch, stop at the ends, ignored while typing / with a sheet or menu open; last choice remembered). ↑/↓ move, Enter opens (My ideas: Edit).
- **AI generated redesign** (data unchanged): chips All · Themes · Trades · Needs evidence · Ready (Parked in All, faded) · `Import JSON`; `+ Idea` / `+ Trade idea` buttons removed. Rows have no Open button (the row opens), show THEME/TRADE · status in plain words with count (`Needs evidence · 2/4`) · next check · what it is · Gains (RS, max 3 +n) / Loses. Detail is answer-first (sentence → What changed · Why now · Who gains/loses (tap → Watch stock, else Screen) · Proven · Assumption · Park it when) with fold-outs How it works · Evidence · Companies. Old tab content/hook mapping: Summary → answer rows, How + Chain → How it works, Evidence → Evidence (+ ready checklist, gaps), Companies → Companies. All old actions (status menu, ⋯ items, evidence/gaps answer sheets, hand-off, company state) kept; old 5-tab render functions kept as `…Legacy` for the hook inventory.
  - Plain words: “Ready to hand off” → “Ready”, “Waiting for evidence” → “Needs evidence”, “Chain” → “How it works”.
  - Trade ideas follow the same pattern (Setup · Levels · Invalidation · Event; folds AI vs us · Product · Entry/cancel; ＋ Plan / Ask AI kept). Trade evidence count `n/3` = our direction set · “Wrong if” written · AI-vs-us nothing open (my definition — trade@1 has no evidence list).
- **My ideas** (`users/{uid}/ideas_my`, shared by Main and Family): list 5/12 + detail 7/12, chips All · Markets · Stocks · Sat · Plan, ⌕ Find, `+ Idea`; New/Edit sheet with required rules, view, chart link, 4 angles, plan, check-again date, Built on, unsaved-changes guard; Delete with Undo toast; ⋯ › Copy text. Chart: `tradingview.com/x/<id>` → `s3.tradingview.com/snapshots/<first letter>/<id>.png`; image error or any other URL → `Chart ↗` link only; nothing uploaded. Old `my_notes` “Waiting for / Watch out for” appear as read-only text ideas (the note’s date shows; the cat date becomes the check date when converted); Edit converts one (original note stays on the stock; converted ones are not listed twice).
- **Context lines**: Flow (latest market/Plan idea), Watch detail + Homework header (`title · view · date · Ideas n · + Idea`; in Homework it sits in the header row so the FS2 no-scroll fit is unchanged), AI idea card `My ideas n ›` (opens My ideas filtered to ideas built on it), Today › To do `IDEA · Check: <title> — right? · Open ›` on/after the check date (counts in the cap).
- **Review**: on/after the date `Right · Partly · Wrong` + one line (≤140) → `review = {result, text, at}`, removes the Today line, changeable later (`at` = latest change).
- **Journal** segments `Trades | Reviews n`: period 30 / 90 / all, tiles Hit rate (right 1, partly 0.5, wrong 0, counts) · Markets · Stocks · By view, list → tap opens the idea in My ideas. Read-only, no copies.

## Existing suites updated (old assumptions, not regressions)
`run_tests_lr5a` (header order + the Ideas list assertions), `rs2a` (segment order), `rs2a2` (Tab/swipe order), `phase374` (iPhone swipes start from Momentum; Screen is a horizontal scroller), `phase49` (Evidence is now a toggle fold-out — open it first). **`run_tests_id1` removed from the regression list**: it asserted the retired 5-tab/sticky-header layout of ID1 (same treatment RK1 gave phase51); its intent is covered by `run_tests_nt1`. `hooks superset` PASS (old markup kept in `…Legacy` functions).

## Proof
- `tests/run_tests_nt1.py` (added to `run_regression.sh`): 139 checks — order/start/Tab/swipe/deep links · ←/→ · AI rows & chips · AI detail + folds + old actions · no overflow · My ideas CRUD/Undo/required/chart/filters/find/old notes/Built on both ways · context lines · Today check line · review save/change · Journal Reviews maths (incl. partly) · permission-denied/Retry · keyboard · 390 / 360 phone sizes · 1440×900 no page scroll.
- Side-by-side vs mockups: `tests/screenshots/nt1/` (AI-generated, My-ideas, New-idea-sheet, Context-lines, Journal-Reviews at 1440; phone 390 live). The sample data differs (fixture names), layout is what is compared; the live chart images are a stubbed sample.
- Hooks superset: PASS.
- Clean `JOBS=2 bash tests/run_regression.sh`: **80/80 ok · 0 failing** (2275 s). Also `run_tests_lr5a` header/Ideas assertions rewritten for the new Ideas page (160/160).

## Notes
- No Plan board / plan card code touched (PC2). If the rebase conflicts it will be the `REST=` line in `run_regression.sh`.
- Known simplifications: Find searches title / text / subject / plan / angles; Flow `Ideas n` counts ideas of the same type as the latest (markets or Plan); Esc inside the sheet goes through the same discard guard.
