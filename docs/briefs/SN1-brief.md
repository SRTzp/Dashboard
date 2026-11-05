# SN1 — Today layout order + Weekly Stock Summary (Watchlist + Candidates) · tests 102

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> **Run after WM1 + WM1b** (WM1 adds the "ข่าววันนี้" block this brief positions). Mockups: `docs/mockups/today-order-mockup.html` (**confirmed Today order**, user 25 Oct) + `docs/mockups/sn1-mockup.html` ①–③ (summary card + sheet + Mac side panel). Yellow notes = explanations; sample data only.
> Backups: `index.backup-pre-SN1.html` · `tests/_bk_sn1/` · do not touch core-size.js · temp → `_to_delete/` · never rm · no push.

## Part A — User text (verbatim)

Please add a Weekly Stock News Summary to the Today tab, covering stocks in Watchlist and Candidate. Keep it lean, simple, and effective.
1. Placement and layout
- Inspect the existing Today layout before choosing the final position. Daily plans and urgent events should retain priority.
- Suggested placement: below the daily plan and events, adjusted to fit the actual layout.
- Use one compact row or small card. Align its edges, width, spacing, and typography with existing components.
- On desktop, aim for visual balance and symmetry without adding empty space or unnecessary containers. On mobile, stack content naturally.
- Do not add a new tab, news buttons in Watchlist, or update badges on individual stock cards.
Example:
Weekly Stock Summary · New
Oct 19–25 · 3 stocks with updates · 1 Candidate needs review　Read →

Allow natural wrapping on smaller screens rather than squeezing everything onto one line.
2. Opening the summary
- Desktop: open a side panel.
- Mobile: open a full-screen view or sheet suitable for reading longer content.
- Show the news coverage period and last updated time.
- List Candidates first, followed by Watchlist stocks. Within each group, prioritize items needing review.
- Each collapsed stock row shows its ticker, status, and a concise headline. Expand it to read the details.
- Include “View stock in Watch”, using the existing navigation to open that specific stock.
3. Content per stock
Write the summaries in clear Thai. Keep them concise without losing meaning.
Section	Content
What happened	The week’s important facts
Why it matters	Implications for the business, growth, earnings, or risk
What to monitor	Specific developments or metrics to follow
Sources	Source names, publication dates, and links in an expandable section

Use only three statuses: Supports the view / Needs review / Additional information.
Clearly distinguish facts from interpretation. Do not claim that news changes the user’s investment thesis unless a saved thesis is available.
4. News selection
- Cover both groups and deduplicate stocks appearing in both.
- Focus on meaningful developments: earnings, guidance, major customers, new products, capital raises, and material risks.
- Combine duplicate coverage into one story.
- Exclude routine price-movement articles without meaningful new information.
- Group stocks with no significant news into a collapsed section at the bottom.
- Distinguish “No significant news found” from “Coverage incomplete.”
- Calculate all displayed counts from actual data; do not hardcode them.
5. Read state and data availability
- Show a “New” badge when a new weekly summary becomes available.
- Provide a “Mark as read” button. This removes the badge and reduces visual emphasis while keeping the summary accessible.
- Persist read status per summary edition so reopening the Dashboard does not flag the same edition as new.
- If no summary exists, show “This week’s summary is not available yet.” Do not imply there was no news.
- If the next edition is not ready, keep the previous summary accessible with its actual coverage dates. Do not relabel it as the current week.
6. Implementation scope
Inspect the existing news retrieval and summary-generation functionality first, and reuse it where available.
If that functionality does not exist, explain what is missing and propose the simplest integration. Do not mix mock data into production or imply that automatic updates are working when they are not.
Acceptance criteria: The normal Today view gains only one compact element. Users can open the summary, expand individual stories, and navigate to the relevant stock without disrupting their daily-plan workflow. Verify desktop and mobile layouts, and briefly explain why you chose the final placement.

---

**Today order — confirmed by the user (25 Oct, `today-order-mockup.html`):**
iPhone top → bottom: 0 date · Daily/Weekly · **Port goal as one line** (tap → full) → 1 ข่าววันนี้ → 2 ช่วงเวลา (current slot highlighted) → 3 แผน Sat สัปดาห์นี้ → 4 การบ้านหุ้น → 5 Weekly Stock Summary → 6 Re-check Macro · อื่น ๆ ปกติ.
Mac (≥ 1000px): left "now" = 1 ข่าววันนี้ → 2 ช่วงเวลา → 3 แผน Sat · right "this week" = 0 Port goal (full card) → 4 การบ้านหุ้น → 5 Weekly Stock Summary → 6 Re-check · อื่น ๆ. iPhone order = left column then right column (plus the one-line Port goal at the top).

## Part B — Orchestrator notes

### B1. What exists (verified)
- **No automatic news retrieval** in the app. Research enters by pasting JSON (living-thesis, idea-scout, Playbook, WM1 Weekly Impact). → SN1 uses the same pattern: a `weekly-stock-news` skill (written later by the orchestrator) produces JSON; the user pastes it. Say this plainly in the UI empty state — never imply automatic updates.
- Watchlist = `users/{uid}/watchlist` (`wlItems`); Candidates = the Watch "Candidates" view (`wlView==='cand'`, from Ideas) — reuse the same lists for the "Copy stock list" manifest and for matching.
- Navigation to a stock: the existing Watch open path (`switchTab('watch')` + set view + select ticker — reuse what the Today homework card / `kbOpenWatchView` use).

### B2. Today layout (Part A + confirmed order)
- Rework only ordering/placement inside the existing Today renderer (`todayRefresh`, `ln3TdMac` two-column split from LN3fix3 §5.1). Mac column split by the order above (not by height measurement); iPhone = same DOM order. Port goal: iPhone ≤ 480px renders a one-line summary (`🎯 เป้าหมาย 24% ▓▓░ · <worst account gap> ›`, tap expands the existing card in place); Mac shows the existing full card at top-right.
- "ข่าววันนี้" (WM1) collapses to one line when there are no events today; keep WM1's rule that an event ≤ 30 min away is the first thing seen.
- The summary is **one** compact card (same card style/width/padding as neighbours). No new tab, no Watch badges/buttons.

### B3. Data (new, pasted)
- Collection `users/{uid}/stockNews/{editionId}` (editionId = `YYYY-MM-DD` of `period_end`), separate from everything else; keep old editions.
- Contract `stockNews/v1` (write it to `docs/stock-news-schema.md` with one clearly labelled SAMPLE):
  `{schema, edition_id, period_start, period_end, asof, sources:{id:{name,url,published_at}}, stocks:{TICKER:{groups:["candidate"|"watchlist"…], status:"supports"|"review"|"info"|null, coverage:"news"|"none"|"incomplete", headline_th, happened_th, why_th, monitor_th, source_refs:[…], thesis_ref:boolean}}}`
  - `status` only `supports` / `review` / `info` (labels `สนับสนุนมุมมอง` / `ควรทบทวน` / `ข้อมูลเพิ่มเติม`); `coverage:"none"` = ไม่มีข่าวสำคัญ, `"incomplete"` = ข้อมูลไม่ครบ (status null).
  - `thesis_ref:true` only when a saved thesis existed for that ticker; otherwise UI never says the news changes the thesis.
  - `happened_th` = facts; `why_th` = interpretation (UI labels them `ข้อเท็จจริง` / `การตีความ`).
- Validate fully before save (same pattern as WM1 `Calc.wiValidate`): unknown tickers (not in Watchlist/Candidates now) → still stored but shown under "ไม่อยู่ในรายการแล้ว" at the bottom, never create watchlist items; invalid → concise error, nothing written. Text rendered as text only.
- **Firestore rule** (user publishes; show in report, do not deploy):
```
match /users/{uid}/stockNews/{edition} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow create, update: if request.auth != null && request.auth.uid == uid
    && request.resource.data.schema == 'stockNews/v1';
  allow delete: if false;
}
```
  `permission-denied` → clear message, pasted text kept.
- Read state: `stockNewsRead {editionId: true}` in the user's settings doc (existing settings write path — synced across devices, keep last 12). Badge `New` = latest edition not read.
- Add `stockNews` to the backup collections (BK1 pattern).

### B4. UI
- Card (iPhone wraps naturally): `Weekly Stock Summary` + `New` · `<period> · <n> ตัวมีอัปเดต · <m> Candidate ควรทบทวน` · `อ่าน →`. Counts computed from data. No edition → `สรุปสัปดาห์นี้ยังไม่พร้อม` + small `วาง JSON`. Latest edition older than the current week → show its real dates (no "this week" wording).
- Open: iPhone = full-height sheet (reuse `UI.sheet` / pb sheet styling from PF2: full width, 16–17px body, close button fixed at top); Mac = right side panel (reuse the existing side-panel pattern if any, else a fixed right drawer ≈ 420px over the page with Esc/✕).
- Inside: period + `อัปเดต <asof>` + `อ่านแล้ว` + `วาง JSON` (small) · `CANDIDATES · n` then `WATCHLIST · n` (stock in both = once, under Candidates, with both tags) · within group: `review` → `supports` → `info`, then ticker A–Z · row = ticker · status pill · headline; expand → ข้อเท็จจริง / การตีความ / ติดตามอะไร / `▸ แหล่งข่าว (n)` (name · date · link) / `ดูหุ้นใน Watch →` · bottom fold: `ไม่มีข่าวสำคัญ (n)` and `ข้อมูลไม่ครบ (n)` listed separately.
- Also a small `คัดลอกรายชื่อหุ้น` button (manifest of current Watchlist + Candidates tickers with group) for the skill input.

### B5. Tests — `phase102`
- Today order iPhone 390/300 and Mac 1280/1440 exactly as confirmed (DOM order + Mac column membership); Port goal one-line on iPhone expands in place; column bottoms within ~15% on the fixture; no overflow.
- Card states: none / new / read / older edition; counts from data (fixture with 2 candidates incl. 1 review, 3 watchlist, 1 in both, 2 none, 1 incomplete).
- Sheet / side panel: grouping, ordering, dedupe, expand, sources fold, "View in Watch" opens that ticker; Mark as read persists after reload (settings) and per edition (new edition → New again).
- Import: valid → saved + card updates; invalid → error, nothing changed; `permission-denied` → message, text kept; text never rendered as HTML.
- Screenshots `tests/screenshots/sn1-{today-390,today-1440,sheet-390,sheet-expanded-390,panel-1440}.png` — open every one.
- Old tests (Today p39/p84/p94 etc.): never delete/weaken; update only order/placement expectations (log `tests/SN1_retired.md`).

## Report back
Why the final placement · what exists vs missing for news (B1) · files changed · Firestore rule block · `docs/stock-news-schema.md` · test results · screenshots opened · limitations · no push, no file deletion.
