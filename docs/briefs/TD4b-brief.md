# TD4b — Satellite / Plan polish · tests 108

> **Part A = user text verbatim (authoritative)**; this round implements **§5 + the "Align MA50 → MA Align Overlap" rename from §1**. Everything else was TD4a. Part B = orchestrator notes; if B conflicts with A, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/TD4b-verify.txt`). **Run after TD4a** (start from the TD4a build; record its sha). Backups **before any edit, including test files**: `index.backup-pre-TD4b.html` · `tests/_bk_td4b/` (copy the whole tests folder first).
> Do not change risk/sizing formulas, caps, validation rules or save behaviour unless an item below says so.

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

**User addition (28 Oct):** "yes ok" — block the Watchlist ＋ for Candidates too: a ticker reaches the Watchlist **only** through the Cand → WL move form.

**User additions for TD4b (28 Oct, verbatim):**
1. Change the "Add" button in the watchlist to an "Add on candidate" button.
2. Move `Export.txt` to be grouped together with "Import" under the `...` menu.
3. Fit all US and TH filters + `…` into a single row.
4. On the Today tab, make the toggle switch (on/off) inactive for now; it should start in the closed/off state. Also, you can remove the "Other" section below Today entirely.
Clarified: (4) means the Candidate → Watchlist cards on Today (META · New today · Tier passed · RS Leader · Revenue ↗ · Need: … · ★★★ · Not passed · Move to Watchlist) — "When starting out, all of them should be turned off/collapsed by default." · "If someone accidentally clicks "Not passed", there should be a small "Undo" button available."

## Part B — Orchestrator notes

### B0. Watchlist entry (from TD4a check)
- TD4a blocked `＋` / `wlOpenAdd` / `wlAddSave` / Tier-only save for tickers not in Watchlist or Candidates, but a ticker that **is** a Candidate can still be added via `＋`. Close that: any **new** Watchlist doc may be created only by the Cand → WL move form (Today Core and, if present, the same form in Watch › Candidates). `＋` on a Candidate ticker → message `Use Move to Watchlist (Tier/RS · rating · note)` with a link that opens that candidate's move form. Updates/imports for tickers already in the Watchlist keep working. Test it in phase108.


### B1. Rename (§1)
- `Align MA50` → `MA Align Overlap` everywhere it is shown (Plan › Sat setup checkboxes, Today Satellite "Setup: …", Journal/stats labels, tooltips). **Keep the stored key** (`setup_ck` id) so old plans and stats still match. Old tests: update expected text only.

### B2. Satellite context (§5)
- Today Satellite rows and Plan › Sat plan rows show one compact context line: `Main · 4H · Long · Zone 4,230–4,250` (plan type · Focus TF · Focus Bias/direction · Zone). Missing parts are skipped, not shown as "—". Find where Focus TF / Bias / Zone live per plan (PF1 fields) and report.
- **Star/pin assets**: ☆/★ per Sat asset (stored per asset in the existing Sat asset settings `satAssetCfg[key].pinned`, not per week). Sort everywhere Sat assets/plans are listed (Plan › Sat asset cards + plan list, Today Satellite panel): ★ first → then **Main before Tactical** (the user wrote "Swing"; in the app the second plan type is **Tactical** — treat "Swing" = Tactical and say so in the report) → then the existing order.

### B3. Tranche display bug (§5)
- Reproduce: add a second tranche (ไม้สอง) to a **Main** plan → it does not appear in the UI. Find the cause (render filter, accordion state, wrong key, sleeve mismatch…), fix it, and add a regression test (tranche 2 visible in Plan › Sat and counted in risk/positions exactly as before). Report the root cause.

### B4. Clutter (§5)
- Second-tranche form/row: remove the auto-generated summary text (e.g. `Macro ตาม (▼▬ v005) · Trend — · Driver P1 · เต็ม`). Remove the **display** only; keep any stored values the app uses (sizing/stats). If a value in that text is used nowhere else, say so.
- "Additional notes" (`เพิ่มเติม`) section at the bottom of the new plan form: remove it **if** nothing else depends on it. If it stores data (notes) used elsewhere, keep existing notes visible read-only on plans that have them and hide the empty section on new plans. Report which case.

### B5. Compact plan view (§5)
- "Plans & Current Holdings" (แผน & ไม้ที่ถือ) expanded rows: reduce row height (padding/gaps/line-height), keep font sizes, keep all info and tap targets ≥ 32px. Target ≈ −25% row height at 390 and 1440 on the fixture; report before/after numbers.

### B6. Zone (§5)
- Remove the `Zone Activation` checkbox; keep the zone text input. Rule: zone field non-empty = zone set (same meaning the checkbox had when ticked with a value). Old plans with checkbox off + a stored zone → report how many in the fixture and keep their zone shown (don't silently change saved plans' logic; if the checkbox affected validation/sizing, keep that behaviour keyed on "zone non-empty" and report).

### B6b. User additions — how
- **Watchlist `＋` → `Add on candidate`** (label; same place): opens a small input (`[US|TH]` + tickers, same rules as Today New Cand incl. the daily cap 10 and dedupe) that adds them as **Candidates**, never to the Watchlist. With this, nothing on the Watchlist screen adds directly to the Watchlist, including tickers that are already Candidates (they must go through the Today Cand → WL form). Remove the old direct-add path from the UI; keep `wlAddSave` only as the internal save used by the promote form.
- **`…` menu**: `Import` and `Export .txt` grouped there (Export removed from the toolbar). Export behaviour unchanged.
- **One row**: `All | US | TH` filter chips + `…` on one row (Mac sidebar and iPhone). If `Filter ▾` exists, it joins the same row or moves into `…` — report which. No wrap at 390; at 300 it may wrap.
- **Today Cand → WL cards start collapsed**: each candidate shows one line `META · New today` (or `Candidate 18d`) with `Screen ›`; tapping opens its form (one open at a time; opening another closes the first, typed values kept in memory). On load/return to Today all are closed.
- **Not passed → Undo**: after `Not passed`, the row collapses to `✕ META · Not passed · Undo` (5 s, same toast style as Move). Undo restores `screened_at` to its previous value and the counter.
- **Remove "Other ▸" from Today entirely** (lean Today). Do not delete the underlying features/data: time slots/routine settings, Daily/Weekly tasks (weekLog), Sat Focus, DD/Open Risk stay available where they live elsewhere (Settings, Plan, Port). If something was reachable **only** via Other, list it in the report (don't re-add it).

### B7. Tests — `phase108`
- Rename shown everywhere, stored key unchanged, old plans still show the criterion ticked.
- Context line content/skip rules (Today + Plan); ★ pin persists, sort ★ → Main → Tactical in Plan and Today.
- Tranche 2 on Main: visible, counted, regression covered.
- Clutter text gone; stored values unchanged (deep-compare saved plan before/after).
- Additional notes per B4 outcome; Zone: no checkbox, zone input works, old plans keep their zone.
- Row height reduced (numbers); risk/sizing outputs byte-identical on the fixture before/after.
- Additions: `Add on candidate` adds to Candidates only (cap/dedupe), no direct Watchlist add anywhere on Watch (incl. a ticker that is a Candidate); Import + Export in `…`, export text unchanged; filter row single line at 390/1440; Today Cand→WL all collapsed on load, one open at a time, values kept; Not passed Undo restores state + counter; Today has no "Other" section; its former items still reachable elsewhere (list).
- 300/390/1280/1440 no overflow; no console errors. Screenshots `tests/screenshots/td4b-{plan-1440,plan-390,tranche2-390,today-sat-390,form-390,watch-390,watch-1440,today-core-390}.png` — open every one.
- Old tests: never delete/weaken; log in `tests/TD4b_retired.md`. Full run (runall2.sh, base + 1–108). Known: p13, p5.

## Report back
Tranche bug root cause · where TF/Bias/Zone live · Additional-notes outcome · Zone checkbox handling · row-height numbers · files changed · full-run results · screenshots opened · limitations · no push, no file deletion.
