# NT1 · Ideas first on Watch · AI generated redesign · My ideas · Reviews in Journal

Decided by SRTp 21 Nov 2026. Spec: mockups `docs/briefs/lr/IdeasAI.html` (Watch order + AI generated redesign) and `docs/briefs/lr/TradeNotes.html` (A My ideas · B New idea sheet · C context lines · D Journal › Reviews). Build after RK1 and FS2 are merged; git fetch and branch from fresh origin/main (`claude/nt1`).
Lean UI: no new top tab (segments inside Ideas and Journal), one primary per screen, light only, English UI, tags mono grey, view chips use gain/neutral/loss colours, 44px phone targets.

## 0. Watch order + start page
- Watch segments in this order: **Ideas** · Momentum · Compounder · Screen. **Every time the Watch tab opens it starts on Ideas** (not the last segment). Tab / Shift+Tab and phone swipes follow the new order. Deep links (e.g. Homework ›, Screen rows, Today lines) still open their own segment.
- Inside Ideas: `AI generated | My ideas` — **←/→ switch between them** (stop at the ends; not while typing or with a sheet/menu open); remember the last of the two. ↑/↓ move in the list, Enter opens.

## 0b. AI generated — redesign (data unchanged: idea@1 / trade@1)
- Chips: All · Themes · Trades · Needs evidence · Ready (Parked shown in All, faded). Header right: `Import JSON` (existing import). The separate `+ Trade idea` / `+ Idea` buttons go (own ideas = My ideas `+ Idea`).
- **List row** (no Open button; the row opens it): type tag `THEME`/`TRADE` · title · status in plain words with evidence count (`Needs evidence · 2/4`, `Ready`, `Parked`, `Exploring`, `Draft`) · next check / event date · one-line what it is · `Gains` tickers (with RS when known, max 3 + “+n”) · `Loses` tickers. Trade ideas show `Asset XAU`.
- **Detail = answer-first, fits 1440 × 900:** header (type, title, status, `+ My idea on this`, primary `Add evidence ›` — existing action, ⋯ menu keeps today’s items) → evidence progress bar + scope · nature · scanned date · next check → the idea in one sentence (big, from the existing “When X makes Y pay more for Z because W” fields) → rows: What changed · Why now · Who gains (all tickers with RS, tap → the stock on Watch, or Screen if not on Watch) · Who loses · Proven so far (✓) · Still an assumption (amber) · Park it when → fold-outs replacing the 5 tabs: How it works (the chain) · Evidence (proven/open counts) · Companies (gain/lose counts). Trade ideas use the same pattern with their own fields (setup, levels, invalidation, event).
- Plain words: “Ready to hand off” → “Ready”, “Waiting for evidence” → “Needs evidence”, “Chain” → “How it works”. Keep every existing hook (map tab hooks to the fold-outs) and every action (status change, evidence add, companies, hand-off to living-thesis).

## 1. Watch › Ideas: `AI generated | My ideas`
- My ideas keyboard: ↑/↓ move the selection, Enter opens Edit; ←/→ as in 0.
- **My ideas view:** list left (5/12), selected idea right (7/12). Filter chips All · Markets · Stocks · Sat · Plan; `⌕ Find` (title/text/subject); `+ Idea` (primary).
  - List row: chart thumbnail (or empty box) · subject tag · title · view chip · date + one-line summary (Plan text, else the first filled angle). Newest first. List scrolls inside its card; the page fits 1440 × 900.
  - Detail: subject · title · view · date · Edit · ⋯ (Delete with Undo toast, Copy text) · chart (TradingView snapshot image, link opens TradingView) · angle boxes Technical · Sentiment · Fundamental · Macro/news (only filled ones) · Plan (full width) · `Built on: <AI idea> ›` if linked · review row (see 3).
- **New / Edit idea sheet:** About (subject picker: US market · TH market · Gold · BTC · Oil · S50 · any Watch stock · Plan · free tag ≤ 20 chars) · My view (Bull/Neutral/Bear, optional) · Title (≤ 80) · Chart link · 4 angle boxes (≤ 600 each) · Plan (≤ 600) · Check again on (date, optional) · Built on (optional, AI idea picker). Required: subject + title + at least one angle or Plan. Save idea (primary) · Cancel. Unsaved-changes guard as in Homework.
- **Chart link:** accept `tradingview.com/x/<id>/` (and `tradingview.com/x/<id>`); show the image from `https://s3.tradingview.com/snapshots/<first letter lowercased>/<id>.png`; on image error or any other URL → a `Chart ↗` link only. Never upload images.
- **Old notes** (`my_notes.cat` “Waiting for”, `my_notes.blk` “Watch out for”) appear in My ideas as read-only text ideas (subject = the stock, title = “Waiting for” / “Watch out for”, date kept); Edit converts one into a real idea. Keep the old data and its current readers (Today catalysts).

## 2. Context lines (read where needed, write anywhere)
- **Flow:** under the page header, the latest market idea (subject US/TH market or Plan): `subject · title · view · date · Ideas n ›` (opens My ideas filtered to Markets). Hidden when none.
- **Watch detail + Homework header:** latest idea for that stock: `title · view · date · Ideas n · + Idea` (+ Idea opens the sheet with the subject set).
- **AI idea card:** `My ideas n ›` when own ideas are built on it.
- **Today › To do:** on the “check again” date: `IDEA` tag · `Check: <title> — right?` · `Open ›` (same row anatomy as TD5; counts in the cap).

## 3. Review → Journal › Reviews
- On/after the check date the detail shows `Right · Partly · Wrong` + an optional one-line “what happened” (≤ 140). Saving sets `review = {result, text, at}` and removes the Today line. Changeable later (keeps `at` of the latest change).
- **Journal** gets segments `Trades | Reviews n`. Reviews = read-only view of reviewed ideas (no copies): period picker (30 / 90 days / all), 4 stat tiles — Hit rate (right = 1, partly = 0.5, wrong = 0; show counts), Markets, Stocks, By view (Bull / Bear / Neutral %) — and the list `date · subject · title · view · result chip · what happened` (tap → the idea in My ideas).

## Data
- New Firestore subcollection `users/{uid}/ideas_my/{id}`: `{subject:{type:'market'|'stock'|'sat'|'plan'|'tag', key}, title, view|null, chart|null, ang:{tech,sent,fund,macro}, plan, checkOn|null, builtOn|null (AI idea id), review|null, created_at, updated_at}`. Shared across Main and Family (ideas are not per account).
- **Firestore rule needed** (put the snippet in `docs/proposals/firestore-ideas-my.rules` and say so in the summary): `match /users/{uid}/ideas_my/{doc} { allow read, write, delete: if request.auth != null && request.auth.uid == uid; }`. Until the rule is added the view shows `Could not load My ideas (permission-denied) · Retry`.

## Proof
- `tests/run_tests_nt1.py`: Watch order + always opens on Ideas (deep links excepted) + Tab/swipe order · ←/→ AI ↔ My ideas · AI list rows (status words, gains/loses tickers, no Open button) · AI detail answer-first + fold-outs + all old actions/hooks · no overflow (the old table cut off “Open” and the tab row); segments + memory · create/edit/delete+Undo · required fields · chart link → image URL, bad link → Chart ↗ · filters + find · old notes shown read-only and convertible · Built on link both ways · context lines (Flow, Watch detail, Homework header, AI idea card) · Today check line on the date, gone after review · review save/change · Journal Reviews stats (hit rate maths incl. partly) + list → open · permission-denied state · keyboard · 360/390/1440 no overflow, 1440×900 no page scroll.
- Side-by-side vs the mockup (`tests/screenshots/nt1/`, `git add -f`) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/NT1-summary.md`. No unrelated PNGs.
