# TD4a — Today polish · Candidate → Watchlist pipeline · Deep dive US/TH · Flow fields · tests 107

> **Part A = user text verbatim (authoritative)**; this round implements **§1 (all except the MA rename) · §2 · §3 · §4 · §6**. §5 + the MA rename = TD4b. Part B = orchestrator notes; if B conflicts with A, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/TD4a-verify.txt`). Start from the TD3a build (index sha `6a272229bd71…`). Backups **before any edit, including test files**: `index.backup-pre-TD4a.html` · `tests/_bk_td4a/` (copy the whole tests folder first).
> Also fix (small, from TD3a/TD3b checks): account label shows `บัญชีหลัก` → show `Main` on Today (default label only; a user-renamed label is kept) · Flow sector error row `ไม่มีข้อมูล` → `No data`.

## Part A — User text (verbatim, 28 Oct)

1. Global UI & Sidebar Navigation
* Sidebar Order: Reorder the left sidebar tabs to: `Idea -> Candidate -> Watchlist`.
* Terminology: Rename "Align MA50" to "MA Align Overlap".
* Space Optimization: Move the "Enter account value" input into the expanded "Account" tab to save row space on the main view.
* Auto-Collapse: When a user expands a "Sector" and navigates to another page, it should auto-collapse back to its default state upon returning.
* Daily Reminders: Trigger a reminder/alert at around 8:00 PM if there are any incomplete tasks left on the Today tab.

2. Today Tab (Overview, News, Macro, Sector)
* Macro Section: Rename "Macro Playbook" to just "Macro". Display directional indicators (e.g., `★BR ▲▬`, `XAU ▼▬`, `USDJPY ▼▬`). Completely exclude assets with a "Neutral" direction.
* Sector Status Context: Append status metrics directly after the Sector name (e.g., `LEADING · 2 d · -1.2%↗ strong + rising`) to provide immediate context on its type and trend.
* Sector Sorting: Within the same market phase (e.g., "Leading"), prioritize and move starred (★) sectors to the top.
* News Feed: Add a "Mark as Read" feature (or a click-to-dismiss toggle) after expanding individual news items, as users might read some and skip others.
* News Empty State: If there are no High Impact events in "Today's news", display a placeholder message: "Please check the Calendar for Major Economic Numbers."

3. Candidate Workflow (Input & Processing)
* "Today New Cand" UI: Rename the new candidate section to "Today New Cand" to save space. Add `US` / `TH` toggle buttons right before the Ticker input field.
* Input Streamlining: Remove the "Note" field from the New Candidate input; keep only the Ticker field.
   * Allow batch inputs (multiple tickers separated by a space).
   * Keep the typed text in the input box until explicitly submitted.
   * Limit: Max 5 tickers per day (can be submitted incrementally, e.g., 1-2 at a time, but strictly max 5 per day).
* Candidate List Management: Add `ALL`, `US`, and `TH` filters to the Candidate page (matching the Watchlist). Add a "Delete" button for each candidate row.
* Homework / Evaluation UI (Candidate -> Watchlist):
   * Increase the daily Candidate -> Watchlist limit from 2 to 5. If 5 new candidates aren't found today, allow pulling older pending candidates to fulfill the quota.
   * Include `US` / `TH` toggles during this homework phase. Show a progress tracker (how many completed today) and allow alerts/reminders.
   * When moving a candidate to the Watchlist, restore the "Note" input field here. Add checkboxes/dropdowns for `Tier passed` and `RS Leader`, a text field for `Reason`, and keep the segmented revenue link exactly as before.

4. Watchlist Tab
* Strict Pipeline Constraint: Enforce that tickers cannot be added or imported directly into the Watchlist. They MUST go through the Candidate pipeline first.
* Sorting & Rating: Sort tickers that already contain data to the top. Add a 1 to 3-star rating system, sorting by the highest stars first.
* Export Feature: Add an "Export to .txt" button for easy TradingView importing. Format the output as comma-separated or newline-separated (e.g., `AAPL,MSFT,GOOGL` or `SET:PTT`, `BINANCE:BTCUSDT`), ensuring correct market prefixes.

5. Trading Plans & Satellite
* Satellite Context: Satellite trades are missing context. Clearly display which plan it belongs to (Main vs. Tactical),Focus Timeframe (TF), Focus Bias (direction), and Zone.
* Satellite Prioritization: Allow starring/pinning assets in Satellite to prioritize them. Default sorting rule: "Main" is prioritized over "Swing", with starred items pushed to the absolute top.
* Tranche Display Bug: Fix the issue in Satellite where adding a second tranche (ไม้สอง) to the "Main" plan does not display on the UI.
* UI Clutter Removal:
   * When adding a second tranche to "Main", remove the redundant auto-generated text clutter (e.g., "Macro ตาม (▼▬ v005) · Trend — · Driver P1 · เต็ม").
   * Delete the "Additional Notes" section at the bottom of the new plan layout if it's easily removable.
* Compact Plan View: When expanding "Plans & Current Holdings (Tranche 1)", optimize the layout to be more compact and lean—minimize row height while maintaining readability.
* Zone Activation: Remove the checkbox for "Zone Activation"; a simple text input field for the zone is sufficient.

6. Deep Dive & Flow Tabs
* Flow Tab Responsiveness: The "Driver", "Evidence", and "Revisit" text fields (which return long JSON) are locked and unreadable on iPhone. Make this container responsive/scrollable for mobile viewing.
* Data Quality Improvement: Ensure the data fetched for "Driver & Evidence" is comprehensive. Currently, it feels too short and lacks actionable utility.
* Deep Dive Tracking: Add `US` / `TH` toggle buttons in the Deep Dive section. Enforce a minimum requirement of doing at least one Deep Dive per market per day.

**User answers (28 Oct):** 8 PM reminder = in-app (banner + browser notification while the app is open; no server) · TradingView export = plain US tickers, `SET:` prefix for TH · Watchlist pipeline = block **new** tickers only (imports/updates for tickers already in the Watchlist keep working; existing items untouched) · split into **2 rounds**: TD4a (Today + Candidate/Watchlist + Deep dive + Flow fields) and TD4b (Satellite/Plan + MA rename).

**User additions (28 Oct, verbatim; override Part A where they differ):**
* Is it possible to fit this entirely into a single row?`Today New Cand 3/5 [US] [TH] [__________] Add`
* For the Candidate -> Watchlist section, I want the progress tracker to be formatted like `US 0/1 · TH 1/1 ✓`, just like in the Watchlist.
* Do the "Note" and "Reason" fields overlap in purpose? Should we just keep one of them? (Maybe just keep "Note"?) → agreed: keep **Note** only, no Reason field.
**User additions 2 (28 Oct, verbatim; override earlier text):**
* On the Today tab, auto-collapse the card immediately after clicking "Move to Watchlist". The button must remain disabled (unclickable) until all required fields are filled out.
* Move the "Segment revenue ↗" link next to the "Tier passed" and "RS Leader" checkboxes. (You can shorten it to just "Revenue ↗" to make the layout more compact).
* Allow users to assign star ratings directly during the Cand -> WL promotion step. Place the 3-star rating selector next to or below the Revenue link (clicking 1 gives 1 star, 2 gives 2 stars, max 3 stars).
* The daily quotas (1 US and 1 TH for Deep Dive, and 4 tickers [changed from 5] for Cand -> WL) are daily minimums, meaning work can continue beyond them. Once the quota is met, provide an option/button to feed the next stock from the Watchlist for another Deep Dive, or fetch a new batch of stocks from Candidates to continue the Cand -> WL workflow.

**How (orchestrator):**
- Promote form row 1: `☐ Tier passed` `☐ RS Leader` `Revenue ↗` (the same segment-revenue link, shorter label) `☆☆☆` (tap n = n stars; tap the current value again = clear). Row 2: Note (optional). Row 3: hint `Need: Tier or RS · rating` → `Ready` · `Not passed` · `Move to Watchlist`.
- **Required = at least one of Tier/RS + a rating 1–3.** Note optional. `Move to Watchlist` is `disabled` until required is met. The chosen stars are saved as the Watchlist item's `stars` (same field as the Watchlist rating).
- After Move: the card collapses immediately into `✓ MSFT → Watchlist · ★★ · Undo` (5 s Undo) and the next candidate shows.
- **Quotas are minimums:** Cand → WL **4/day** (tracker `US n · TH n · x/4`, ✓ at 4; counting continues past it, e.g. `6/4 ✓`). Deep dive **US 1 + TH 1/day**. Today New Cand stays **max 5/day** (a limit, not a minimum).
- After a quota is met: Deep dive shows `Next from Watchlist ›` (per market: next Watchlist stock by stars desc → oldest without a complete thesis; becomes the current deep-dive stock); Cand → WL shows `Next batch ›` (loads the next 4 oldest pending Candidates of the selected market). The 20:00 reminder only checks the minimums.
**User additions 3 (28 Oct, verbatim; override everything above where they differ):**
* Today New Cand: The maximum limit is now capped at 10 tickers per day, with a minimum requirement of 2 tickers per day.
* Required fields: You must check at least one box (Tier or RS), assign a 1–3 star rating, and filling out the "Note" is now mandatory. If incomplete, the button will be greyed out and unclickable, showing a hint like "Need: Tier or RS · rating · note". Once moved, the star rating assigned here will be saved as the stock's rating in the Watchlist.
* Layout adjustments: Move the star rating (☆☆☆) to where "Not passed" was originally located. Then, push "Not passed" down to the same row as the "Move to Watchlist" button, placing it in the bottom right corner.

**How (orchestrator, final form):** row 1 `☐ Tier passed` `☐ RS Leader` `Revenue ↗` · row 2 `Note` (required, non-empty after trim) · row 3 hint left (`Need: Tier or RS · rating · note`, listing only what's missing; `Ready` when complete) + `☆☆☆` right · row 4 `Move to Watchlist` left (disabled until complete) + `Not passed` bottom-right. Today New Cand tracker `x/2` (✓ at 2 = daily minimum, counts on past it), hard cap **10/day** (replaces 5; a batch beyond 10 adds up to the cap and leaves the rest in the box with `Daily limit 10 reached`). The 20:00 reminder checks New Cand ≥ 2 too.
**User additions 4 (28 Oct, verbatim; override everything above where they differ):**
* Switch the positions of the "Move to Watchlist" and "Not passed" buttons.
* Rename/Cut "Today New Cand" down to just "New Cand".
* Cand -> WL batch size: Let's do 3 tickers at a time.
* New Cand minimum: Set the minimum to 3 tickers as well.

### ★ FINAL Core panel spec (supersedes every earlier Core/Candidate number or layout in this brief)
- **Deep dive:** `[US|TH]` · tracker `US 0/1 · TH 1/1 ✓` · minimum US 1 + TH 1/day · after a market is done: `Next from Watchlist ›` (next stock of that market: stars desc → oldest without a complete thesis).
- **Cand → WL:** `[US|TH]` filters the queue · queue = today's new candidates of that market first, then oldest pending · **minimum 3/day**, shown `US n · TH n · x/3` (✓ at 3, counts on past it) · after 3: `Next batch ›` loads the next **3** oldest pending candidates of the selected market.
  - Form: row 1 `☐ Tier passed` `☐ RS Leader` `Revenue ↗` (the existing segment-revenue link) · row 2 `Note` (**required**) · row 3 hint left (`Need: Tier or RS · rating · note`, only missing items; `Ready` when complete) + `☆☆☆` right (tap n = n stars; tap again = clear) · row 4 **`Not passed` left · `Move to Watchlist` right** (disabled until Tier or RS + rating + note).
  - Move → saves via the existing Watchlist path with `promoted_by` (tier/rs), `promoted_at`, note, and `stars` (= the Watchlist rating) → card collapses at once to `✓ MSFT → Watchlist · ★★ · Undo` (5 s) → next candidate shows. Not passed → stays Candidate, `screened_at` today, back of the queue.
- **New Cand** (label exactly `New Cand`), one row: `New Cand` · `x/3` · `[US|TH]` · ticker input (space/comma batch; text stays until Add) · `Add`. **Minimum 3/day** (✓ at 3), **hard cap 10/day** (extra tickers stay in the box with `Daily limit 10 reached`). No note field.
- **20:00 reminder** checks the minimums only: Deep dive US 1 + TH 1 · Cand → WL 3 · New Cand 3 (+ Satellite rows as before).
Layout reference: `docs/mockups/td4a-core-mockup.html` (Core panel, iPhone).

## Part B — Orchestrator notes

### B1. Global (§1)
- **Watch view order** (Mac left sidebar + iPhone switcher): `Ideas → Candidates → Watchlist`. Labels/views and their content unchanged; default view stays as today unless it was index-based (report).
- **Enter account value**: remove the floating `＋ Enter account value` row from Today; put the same action inside each expanded account row (top or bottom of the sub-portfolio list).
- **Sector auto-collapse**: any expanded Drivers & evidence (Flow) / expanded sector row returns to collapsed when the user leaves the tab and comes back. Unsaved edits in an open form: keep them (draft in memory) but collapse; reopening shows the draft. Report.
- **20:00 reminder (in-app)**: after 20:00 ICT, if any Daily item is incomplete (Deep dive US/TH, Candidate → Watchlist x/5, Today New Cand x/5, Satellite rows not Saved/Not trading), Today shows a slim banner at the top: `Unfinished today: Deep dive TH · Cand→WL 2/5 · …` with links. Once per day per device, also a browser `Notification` **if** the user has granted permission (ask only from a small `Enable reminders` button in Settings › Daily routine; never prompt automatically). Uses a timer while the app is open + a check on load/visibilitychange. No server, no service-worker push. Dismiss = hidden until tomorrow (localStorage, try/catch).

### B2. Today (§2)
- **Macro**: header `Macro` · right `4d ago` · one line of direction chips from the active Playbook assets: `★` when focus, short name (same `PB_SHORT` used in Flow), stance icon (`Calc.pbStanceIcon`); **skip neutral stance** (`none`/neutral). Then the headline line (unchanged).
- **Sector rows** (Today Overview): `XLU Utilities · LEADING · 2 d · −1.2% ↗ strong + rising` — phase in its colour, days in quadrant, OFF52W, ↗ chip — then the driver line + `Reviewed …` as now.
- **Sector sorting**: in Flow (lean) within the same quadrant, ★ followed sectors first, then the existing Δmom order. Quadrant order unchanged. Today rows follow the same order.
- **News**: each expanded event gets `Mark as read` (toggle `Read ✓`). Read events collapse, dim and stay in place. Store in settings `newsRead{YYYY-MM-DD:[eventId]}` (sync across devices; keep last 7 days). The "next event open by default" rule skips read events.
- **Empty**: `Please check the Calendar for Major Economic Numbers.` + the `US calendar ↗` button.

### B3. Candidates (§3)
- **Today New Cand** = **one row**: `Today New Cand` · `3/5` · `[US|TH]` segmented toggle (remembers last choice per device) · ticker input (flex, min ≈70px; space/comma separated batch) · `Add`. Wraps only when the panel is too narrow (e.g. 300). No note field. Text stays in the box until Add (also survive re-render/tab switch: keep in memory + localStorage draft). Per ticker: uppercase, valid pattern (US `A–Z . -` ≤ 6; TH `A–Z 0–9 -` ≤ 10 — confirm against existing market rules), dedupe vs Ideas/Candidates/Watchlist and within the batch. **Max 5 added per day (both markets together)**; a batch that would exceed it adds the first allowed ones and leaves the rest in the input with `Daily limit 5 reached`. Counter `x/5`. Stores `market` in `candMeta`.
- **Watch › Candidates**: `ALL | US | TH` filter (same component as Watchlist) + a `Delete` button per row. Manual candidates (`candMeta.manual`) → remove the entry (confirm). Idea-derived candidates → `dismissed:true` in `candMeta` (hidden from Candidates; the Idea itself untouched). Report.
- **Re-ask when a dismissed ticker comes back in an Idea** (user, 28 Oct: "instead of keeping the same ticker hidden permanently, could the system prompt and ask me again if I am still interested in it? … a list with checkboxes … lean, simple, and effective"):
  - Store `dismissed_at` on Delete. A dismissed ticker is **"back"** when it appears in an Idea whose content is newer than `dismissed_at` (idea `updated_at`/`as_of`/import time) and newer than the last time the user was asked about it (`asked_stamp`).
  - Ask with **one checklist, never one by one**: `Back in Ideas · 2` — rows `☐ NVDA · US · dismissed 12 Oct · from "<idea title>"`, all **unchecked** by default; buttons `Bring back` (checked ones) · `Keep hidden` (the rest) · `Later` (close, decide nothing).
  - Where: (1) inside the Idea import preview (idea-scout paste) as a small section, applied on save; (2) if the Idea changed without a preview (other device / sync), a chip `Back in Ideas · n · Review` in the Watch › Candidates header opens the same checklist. No popups elsewhere.
  - `Bring back` → `dismissed:false`, `cand_at = now` (treated as new today), `restored_at`. `Keep hidden` → `asked_stamp = that Idea's stamp` → not asked again until that Idea changes again. `Later` → chip stays.
  - Manually re-adding the ticker via Today New Cand also clears `dismissed`.
- **Homework Candidate → Watchlist (min 4/day, see User additions 2)** (Today Core): `[US|TH]` toggle filters the queue. Queue = today's new candidates of that market first, then oldest pending (by `cand_at`), excluding screened-today and dismissed. Tracker: see "User additions 2" (x/4 minimum).
  - Promote opens a compact inline form: `☐ Tier passed` `☐ RS Leader` (at least one required) · `Note` (textarea, placeholder `Note — why it passed / thoughts`) · no Reason field · the **segment-revenue link exactly as in the existing Watchlist add form** (find it in the current add-to-watchlist UI/`wlAddSave` path and reuse that element as is) · `Move to Watchlist`. Save uses the existing path + `promoted_by` (array: `tier`/`rs`), `promoted_at`, note. Undo toast stays (5 s).
  - `Not passed` stays as now (back of the queue).

### B4. Watchlist (§4)
- **Pipeline**: remove/disable every direct "add new ticker" entry point into the Watchlist (the Watchlist `＋` add form, JSON/research imports that would create a new watchlist doc). Message: `Add it as a Candidate first` with a link to Today New Cand / Watch › Candidates. Imports/updates for tickers **already** in the Watchlist keep working. List every entry point found and how it was handled.
- **Stars**: 1–3 ★ per Watchlist item (`stars` on the watchlist doc; tap cycles 0→1→2→3→0; ≥ 32px hit area).
- **Sort**: stars desc → has data (thesis / research card / any homework part) → existing order. Apply within the current filter.
- **Export to .txt**: button next to the filter. Exports the current filter's tickers, comma-separated on one line, US plain (`AAPL`), TH `SET:PTT`; crypto if any `BINANCE:BTCUSDT`. File `watchlist-<filter>-YYYY-MM-DD.txt` (Blob download; iOS falls back to opening the text in a new tab). Order = the displayed order.

### B5. Deep dive (§6)
- Today Core item 1 becomes `Deep dive · US 0/1 · TH 0/1` with a `[US|TH]` toggle choosing which market's homework stock is shown. One homework stock per market per day (extend the existing `tdHw` mechanism per market; report). Done = the day's stock has progressed (≥ 1 new thesis part saved today) — report the exact rule you used. Both markets count toward the 20:00 reminder.

### B6. Flow Drivers & evidence (§6)
- **iPhone**: Driver / Evidence / Revisit if fields must be fully readable and editable — textareas auto-grow with content (no fixed height, no inner scroll lock), wrap long words/URLs (`overflow-wrap:anywhere`), font ≥ 16px on iPhone (prevents iOS zoom), container never wider than the screen. If any field is `readonly`/disabled when it shouldn't be, fix it.
- **Data quality** (the app doesn't fetch; the content comes from the external AI via `Copy AI prompt`): strengthen the prompt — driver 2–4 sentences (labelled facts vs interpretation); evidence summary 3–6 dated facts with numbers where available + material contradictions; 2–3 sources; revisit_if 2–3 concrete, checkable triggers; plain language; Thai allowed. Raise caps: driver ≤ 1200, evidence.summary ≤ 2000, revisit_if ≤ 600 (validator + UI). Show the full text in Today's driver line on tap (truncate to 1 line collapsed).

### B7. Tests — `phase107`
- Watch order; account value inside expanded row; sector collapse after tab switch (draft kept); 20:00 banner with a fixed clock (before/after 20:00, nothing incomplete → none, dismiss → hidden until next day); notification only when permission granted (stub).
- Macro chips (focus ★, neutral excluded); sector rows metrics + ★-first sort in Flow and Today; news Mark as read persists after reload (mock Firestore) and skips default-open; empty-state text.
- New Cand: batch `AAPL MSFT, NVDA`, dedupe, invalid ticker, market toggle stored, text kept across re-render, limit 5 (incremental 2+2+2 → 5 added, 1 left in box); Candidates filter + delete (manual vs idea-derived).
- Re-ask: dismiss → Idea re-import with the ticker → checklist shows it (unchecked); Bring back → Candidate again (new today); Keep hidden → not asked again for the same Idea stamp, asked again after the Idea changes; Later → chip stays; sync-only change → chip in Candidates header; New Cand re-add clears dismissed.
- Homework 5/day: queue order (today's first, then oldest), market toggle, promote form requires Tier or RS, saves note/promoted_by (no reason field), segment link present and identical to the Watchlist form's, Undo.
- Watchlist: no direct add (UI + import of new ticker rejected), update of existing ticker works; stars cycle + persist; sort order; export text exact for a fixture (US plain, `SET:` TH).
- Deep dive US/TH counters; Flow fields on 390: auto-grow, no horizontal overflow, editable; prompt contains the new instructions; caps.
- 300/390/1280/1440 no overflow; no console errors. Screenshots `tests/screenshots/td4a-{today-1440,today-390,newcand-390,promote-390,cands-390,watchlist-1440,flow-fields-390,reminder-390}.png` — open every one.
- Old tests: never delete/weaken; log expectation changes in `tests/TD4a_retired.md`. Full run (runall2.sh, base + 1–107). Known: p13, p5.

## Report back
Entry points blocked (B4) · segment-link source · deep-dive done rule · data added · files changed · full-run results · screenshots opened · limitations · no push, no file deletion.
