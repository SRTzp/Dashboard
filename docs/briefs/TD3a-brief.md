# TD3a — Today redesign: "What do I need to do next?" · tests 106

> **Part A = user text verbatim (authoritative; later messages override earlier ones)**, Part B = the consolidated spec the orchestrator derived from Part A + the agreed mockup. If B conflicts with A, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/TD3a-verify.txt`). Mockup (agreed): `docs/mockups/td3-mockup.html` **v4** + `docs/mockups/td3-sector-mockup.html` (sector rows, already built in TD3b).
> Start from the TD3b build (index sha `a6b62c23e4e2…`). Backups: `index.backup-pre-TD3a.html` · `tests/_bk_td3a/`.
> Scope = the **lean** Today (`tdHtmlLean` path). Legacy Today (`tdHtml`, `ln1_plan_view = legacy`) unchanged. Watch tab reordering = TD3c (not now).

## Part A — User text (verbatim, in order)

**A1 — proposal (26 Oct)**
I suggest making Today answer one question: **"What do I need to do next?"** Keep three panels, with a **Daily | Weekend** switch that changes the tasks inside them.
**1. Today layout** — At the top, show **goals for every account**, followed by the **Daily | Weekend** switch and these three panels:
| Panel | Weekend — prepare the week | Daily — take action |
|---|---|---|
| **Overview** | Review Macro → identify strong industries through RRG → investigate fundamental and sentiment drivers → choose themes to follow | Check what has changed and whether any assumptions need reviewing |
| **Core Port** | Read Weekly News → review Idea / Candidate / Watchlist → select stocks for further research | Complete selected research → review stocks of interest → create or update plans |
| **Satellite** | Read Weekly Impact → select assets for the week | Check plans for selected assets → identify missing requirements → continue the relevant task |
Daily opens by default. Weekend shows **"This week's review is incomplete"** until completed. You can access it on any day.
**2. Satellite: reminders based on actual plan status** — Today should **read directly from Plan**, so you don't have to maintain a second checklist.
| Actual status | Today displays |
|---|---|
| Asset selected, no plan | "Plan not created" |
| Draft exists, criteria incomplete | Name the missing criteria |
| Criteria complete, required fields missing | For example, "Entry / SL missing" |
| All requirements complete, not saved | "Ready to save" |
| Plan saved | "Plan saved · Review execution conditions" with a link |
| Plan cancelled or closed | Stop reminders for that plan |
- **Unchecked does not mean the market condition hasn't occurred.** If the app cannot verify the chart, say "MMT Shift pivot not yet confirmed."
- If several requirements are missing, show the first plus **"2 more"**, expandable.
- Track Main and Tactical separately when both exist.
- Allow **"Not trading this week"** as a valid completed decision.
**4. Core and Watch** — Today shows only **stocks selected for today's research** and **unfinished planning tasks**, rather than the entire Watchlist. Weekly News belongs in the Weekend workflow. If unread, Daily can show a compact reminder linking to it.
**5. Account goals and display behaviour**
- Show **every account as a collapsed row** on both Mac and iPhone; click to expand.
- Each row shows the account name, goal progress, and elapsed time—for example, **"3 months, 12 days elapsed."**
- Calculate elapsed time from the recorded goal start date. If unavailable, show "Start date not set"; don't infer it from the last edit.
- On Mac, place the three panels side by side. On iPhone, stack Overview → Core → Satellite.
- In Flow, make **Quarterly Macro expanded by default on Mac**, while allowing manual collapse.
Every Today item should clearly communicate **what remains unfinished and where to continue**. Full details and editing stay in Flow, Watch, and Plan.

**A2 — 27 Oct**
1. For the news, how about showing today's events with their scheduled time and impact level? If an event is under 4 hours away, display an active countdown timer.
2. For goals, the collapsed view should display the high-level Account goals. When expanded, break down the specific goal details for each sub-portfolio.
3. Core Port: In the "Potential Candidate" section (identifying the trigger to promote from Candidate → Watchlist), prompt the homework required to advance the stock to the Watchlist.
4. Core Port: Once the daily task is completed, suggest the next candidate to consider, allowing extra research and plan drafting if time permits.
* Satellite (Saved State): For the "review entry conditions" section, replace it with Entry / SL / TP / Size. Ensure it fits the container width neatly, with priority visibility given to Entry and Size.

**A3 — 27 Oct**
1. Try to keep it on a single line if possible, such as for "Main Account" (บัญชีหลัก).
* Overview: Label it as "Macro Playbook Q4/26" (formatted like this), and include topic headers.
* Show the number of days elapsed since the latest update (remove "no change / ไม่เปลี่ยน").
* News: Show High Impact events only, and provide a button linking to the US Economic Calendar.
3. Satellite (Saved Plan): Keep the font size uniform across all values and maintain them on a single line. If the panel becomes narrow, hide the other values, prioritizing Entry and Size first.
4. Candidate to Watchlist Workflow:
* Candidate entry: A stock enters Candidate status when the chart begins showing an uptrend and catches interest. Provide a field to record our own notes/opinions.
* Promotion from Candidate to Watchlist: A stock is promoted to the Watchlist once it passes the Tier List (Pine Script) or qualifies as a Leader (via the RS Indicator)—this step serves as the science-based screening filter.
* Watchlist Homework: For stocks in the Watchlist, the homework involves deep-dive research and thesis development.
* Core Homework breakdown: 1. Deep-dive research on Watchlist stocks. 2. Screen Candidate → Watchlist: 2 tickers per day. 3. Scan and source new Candidates: 4 tickers per day.
5. Satellite Page Direct Action: When clicking a link (e.g., "Create Plan: BTC"), have it trigger the plan-creation modal/form directly at that specific entry point, rather than just navigating to the Plans tab.
Sub-portfolio goals (start, target, deadline and start date for each sub-portfolio, set in Settings › Goals) — "Ok". Next candidate order — "Oldest yes".

**A4 — 27 Oct**
Today's News: When clicking the US Calendar link, have it automatically expand the details upon opening. Localization: Switch to English wherever applicable (e.g., change "3ด 12ว" to "3m 23d", or translate terms like "ตามเส้นทาง" to "On track"). Dashed Links: Make the dashed outline more subtle/muted, matching the font size and styling of the "สมมติฐาน" (Hypothesis) tag—fade it out one step further. Macro: Include a descriptive headline, for example: "High oil prices while the market questions AI ROI". Candidate → Watchlist: Let's make it a checkbox to select either Tier Passed or Leader RS. Once checked, can it automatically move the ticker from Candidate to Watchlist in the Watch tab? New Candidates: Can the input field directly append the newly entered ticker into the Candidate list under the Watch tab? Setup Labeling: make "Setup on minor: MMT Shift pivot" more concise (drop "on minor"); cleaner English instead of "ยังไม่ยืนยัน" (agreed: **Pending**).

**A5 — 27 Oct**
1. Macro Headline: The headline placed under the Playbook name should be pulled directly from the Macro section in the Flow tab.
2. US Calendar Link: this is already inside `index.html` under the Flow tab; it's just currently collapsed under the section "ปฏิทินข่าว US · สำคัญสูง · สัปดาห์นี้". Expanding it directly there when navigated from this link is what was meant.
(Sector drivers → built in TD3b; Today Overview uses that block.)

## Part B — Consolidated spec

### B0. Verify first (report each)
- Where Candidates live (Watch `wlView==='cand'`, from Ideas) and the **existing** add-candidate and move-to-Watchlist paths. Today must call those same paths (no second data model). Find a "date entered Candidate" field (else add `cand_at` on create; legacy items without it sort by their created/updated time, oldest first).
- How Sat plan status can be read: selected assets for the week (`satWeekPick…`), drafts (`satIdeas`), the 3 Setup criteria (In the zone · Align MA50 · MMT Shift pivot), Trend/TF, Entry/SL/TP/size, planned/saved, cancelled/closed.
- How Weekly Impact events are marked high impact (event field vs asset tier). Rule if no event field: an event is HIGH when any linked asset's tier for it is HIGH. Report which.
- Where the current per-account goal value comes from (GL1 `goals`/`goalLog`) and whether Port already has sub-portfolio values (Core.US / Core.TH / Sat / Option).

### B1. Layout (lean Today)
Top → bottom: **News box** (full width) · **Account goals** (Mac: side by side; iPhone: stacked) · **Daily | Weekend** switch · **3 panels** (≥ 1000px: 3 equal columns, top-aligned; below: stacked Overview → Core → Satellite) · **Other ▸** (one folded line, full width).
- **Other ▸** holds, unchanged, everything from the current Today that is not mapped below: time slots/routine, the Daily/Weekly task % lists, the Sat Focus ✓✕ card, Re-check Macro, DD/Open Risk numbers. Nothing is deleted; it is just folded (closed by default, open state remembered per device).
- `tdBalance` two-column balancing is no longer used in the lean Today. The balance tests (p94/p102/p103/p104) become "3 panels top-aligned, no overflow"; log in `tests/TD3a_retired.md`.
- All Today UI labels in English. User-entered text stays as typed (Thai OK).
- Direct-action links = small faded dashed pill: font-size like the Hypothesis tag (≈11.5px), border `1px dashed` one step lighter than the Hypothesis tag, link colour.

### B2. News box
- Today's (ICT) **HIGH-impact** events only, from Weekly Impact (current + previous snapshot, dedup by event ID — existing WM1b rule). Row: time · name · affected assets · right side = countdown or actual.
- Countdown when < 4 h away: `in h:mm:ss`, live each second, red when < 1 h. Past events dimmed, show actual if known.
- Tap a row → expands details (forecast · previous with `previous_period` · scenarios). The next upcoming event is expanded by default.
- Button `US calendar ↗` (on narrow: `↗` only) → switch to Flow, **open** `#ffCal` (the existing "ปฏิทินข่าว US · สำคัญสูง · สัปดาห์นี้" details, which loads its iframe on toggle), scroll it into view.
- No HIGH events today → one muted line `No high-impact events today`. Keep WM1's rule: an event ≤ 30 min away must be the first thing seen (the box is first).

### B3. Account goals
- Collapsed row, one line: `Main` (account label) · bar · `24%` · `3m 12d` · pace (`Behind −4.8%` amber / `On track` green). Narrow: pace hides first. No start date → `Start date not set` (link to Settings › Goals). Elapsed = calendar months + days from `startDate` to today (ICT).
- Expanded: one line per sub-portfolio `Core.US · bar · % · start→target`; missing → `No goal set`.
- **New data:** sub-portfolio goals `{start, target, deadline, startDate}` per account, edited in Settings › Goals (extend GL1 store; same write path; preserve other settings). Current value: reuse Port's sub-portfolio values if they exist, else a manual "current" entry like GL1. Report which.

### B4. Daily | Weekend switch
- Daily opens by default every day. Weekend shows a red badge `n/m` while incomplete (`This week's review is incomplete` as tooltip/aria); no badge when complete.
- Weekend items (auto = derived from real data; manual = tick stored in the existing `weekLog`):
  - Overview: Review Macro Playbook Q4/26 (manual) · Review drivers for selected sectors (manual, link Flow › Leadership — TD3b task; no counter).
  - Core: Read Weekly News (auto: current edition read) · Review Candidates n · Watchlist n (manual, link Watch) · Pick deep-dive stocks for the week (reuse the homework queue if one exists — else manual).
  - Satellite: Weekly Impact for this week (auto: current Monday-week doc exists) · Pick assets for the week (auto: ≥ 1 asset picked **or** the week marked `Not trading this week`).

### B5. Overview (Daily)
- Header `Macro` → `Macro Playbook Q4/26` (from the active Playbook's quarter, format `Qn/yy`) · right `12d ago` (days since that version's created/updated date) · line below = the active Playbook's `view.headline` (same text as Flow's Macro card). No active Playbook → `No active Playbook`.
- Header `Sectors` → the TD3b block (`tdSectorsHtml()`), moved here from its current place. No changes to its logic.

### B6. Core Port (Daily) — three daily tasks + extras
1. **Deep-dive Watchlist** — today's homework stock (existing `tdHw` mechanism): `ABC · Thesis 2/5 · Left: Why · Monitor · Exit` + `Continue ›` (opens Watch at that stock's thesis section).
2. **Candidate → Watchlist `x/2`** — oldest Candidates first (not screened today). Row: `MSFT · Candidate 18d · oldest` + checkboxes `Tier passed` / `RS Leader` + `Not passed`. Checking either → move to Watchlist via the existing path, store `promoted_by:'tier'|'rs'`, `promoted_at`; toast `MSFT moved to Watchlist · Undo` (5 s; Undo restores exactly). `Not passed` → stays Candidate, `screened_at = today` (goes to the back of the queue). Counter = rows screened today (passed or not passed). Done rows show `✓ CRWD → Watchlist · RS Leader`.
3. **New Candidates `x/4`** — inline `Ticker` + `Our note` + `Add` → creates a Candidate via the existing path with the note and `cand_at`. Uppercase; A–Z 0–9 . - ≤ 10; already in Ideas/Candidates/Watchlist → message, nothing added. Counter = Candidates added today. Done rows `✓ ANET · note`.
- When 1–3 are all done → light box `If time permits` · next oldest Candidate · `Screen ›` · `Draft plan ›` (opens Plan › Core with the plan form open for that ticker).
- Unfinished Core plan drafts: one row each `NVDA · Draft plan · Entry / SL missing` + `Continue ›` (form open).
- Weekly News unread → one muted line `Weekly News · 3 updates unread · Read ›` (opens the existing SN1 sheet/panel). Read → line hidden.
- Watch: Candidate rows show the note (one line) and Watchlist rows show `via Tier`/`via RS` — minimal, no reordering (TD3c).

### B7. Satellite (Daily)
- One row per **selected asset × plan type** (Main and Tactical separately when both exist); assets marked `Not trading this week` show a grey pill and no reminder.
| Status | Pill | Line | Link (opens in place) |
|---|---|---|---|
| Selected, no plan | `No plan` (red) | `Selected this week` | `Create plan ›` → Plan › Sat, new plan form for that asset open (`satV2NewPlan`), PF3b accordion |
| Draft, criteria incomplete | `Pending` (amber) | `Setup: MMT Shift pivot · +2` (first missing; `+n` expands the rest) | `Criteria ›` → that draft expanded, scrolled to Setup |
| Criteria complete, fields missing | `Incomplete` (amber) | `Entry / SL missing` | `Continue ›` → draft expanded at the first missing field |
| All complete, not saved | `Ready to save` (blue) | — | `Open ›` |
| Saved | `Saved` (green) | `Entry 4,180  Size 0.30 lot  SL 4,117  TP 4,300` — one line, same font size; narrow panel hides SL then TP | `Open ›` |
| Cancelled / closed | — | no row | — |
- "Pending" never claims the market condition hasn't happened. Wording for criteria = the app's own criterion names, without "on minor".
- `Not trading this week`: a per-asset decision stored in the existing Strategy week data (report the field). Settable from the Weekend item and the Plan › Sat asset row.

### B8. Flow
- Quarterly Macro (`pbOpen`) open by default on Mac (≥ 1000px); manual collapse remembered per device (localStorage, try/catch). iPhone unchanged.

### B9. Tests — `phase106`
- Layout order + 3 columns at 1280/1440, stacked at 390/300; Other ▸ contains the old items and they still work (tick a slot, Sat Focus ✓).
- News: HIGH only; countdown appears at < 4 h, red < 1 h, absent ≥ 4 h; past dimmed; tap expands; next upcoming open; `US calendar ↗` → Flow, `#ffCal` open + in view; empty state.
- Goals: one line at 390 and 1440 (no wrap of the summary row); elapsed `3m 12d` from fixture; `Start date not set`; expanded sub-portfolios; Settings › Goals edits sub-goals and keeps other settings byte-identical.
- Switch: Daily default; badge counts; each auto item flips from real fixture data; manual ticks persist in weekLog.
- Overview: `Macro Playbook Q4/26`, days ago, headline = Flow's text; sectors block present.
- Core: screening order oldest-first; Tier/RS check → item in Watchlist (Watch tab shows it), Undo restores; Not passed → back of queue; counters; add Candidate (valid / duplicate / bad ticker); next-pick box only when 1–3 done; Draft plan opens the form.
- Satellite: each status row from fixtures (incl. Main + Tactical same asset, Not trading, cancelled → no row); saved line hides SL/TP at narrow width, Entry/Size always visible; each link opens the right form in place.
- Flow Quarterly Macro open on 1440, closed on 390; collapse remembered after reload.
- No overflow 300/390/1280/1440; no console errors. Screenshots `tests/screenshots/td3a-{today-1440,today-1280,today-390,today-300,weekend-1440,weekend-390,news-390,core-390,sat-390}.png` — open every one.
- Old tests: never delete/weaken; update only expectations this redesign changes; log `tests/TD3a_retired.md`. Full run at the end (runall2.sh, base + 1–106). Known: p13, p5.

## Report back
B0 findings · data added (sub-goals, cand_at/promoted_by/screened_at, not-trading flag) · files changed · test results (full run) · screenshots opened · limitations · no push, no file deletion.
