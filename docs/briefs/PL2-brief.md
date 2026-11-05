# PL2 — Today / Watch / Sat fixes (7 items)

Status: AGREED SCOPE (2026-11-05). Code not modified yet.
Base: build on top of PL1 (PR #6). Merge PR #6 first, then branch `claude/pl2` from updated `main`.
File: repo `index.html` (the user called it "index-3.html").

## Global rules
- Preserve all user data. Remove obsolete UI/dependencies, never user content.
- No new trading rules, sizing changes, or invented values. Missing input → say what's missing.
- Audit first per item group, write the audit to docs/briefs/PL2-audit.md, wait for OK (unless told it's an overnight run).
- Log every changed/retired test expectation in tests/PL2_retired.md.
- Report at the end in 3 separate lists: What changed · What was verified · Unresolved trading-rule decisions.

---

## 1. Weekly Impact — Monday runs
- The SKILL is updated separately in the user's account (not in the repo): Monday (Asia/Bangkok) run → `week` = that same Monday. Schema unchanged (weeklyImpact/v2).
- Dashboard side: check import validation + week mapping (`wpWeekKey` = Sunday start, `wiCurMon` = Sunday+1, `wiCurDoc`, `wiOtherDoc`, import at ~18532).
  - A Monday-run doc with `week` = this Monday must show as the CURRENT week, with no "expired" or "wrong week" warning.
  - Also check Saturday: `wpWeekKey(Sat)` gives the PAST Sunday, so a Saturday run for next Monday may be treated as "other week". Report the behaviour; fix only if it shows a wrong-week warning.
- Test: fake clock Monday + Saturday + Sunday, import a doc for the matching week → correct week, no warning.

## 2. "Unfinished today" banner → real navigation
- `td4RemBanner()` renders the buttons; fix `td4RemGo()` so each one navigates, not just scrolls:
  - Deep dive US → switch to Today/Watch as needed, select US market, open the deep-dive workspace for the next stock.
  - Cand→WL → open the Candidate screening flow (first unscreened candidate, market from the counter).
  - New Cand → open the Add Candidate input/popup with focus.
  - Satellite → open the outstanding Sat planning task. Selector must work for both `data-td3-panel="sat"` and the weekday `"plans"` layout (PL1 A7).
- If the target isn't rendered: switch tab, expand sections, render, then scroll. If still not found, show a toast ("Couldn't open X") — never fail silently.
- Test each of the 4 from the current Today layout.

## 3. My Thesis replaces "มุมมอง"
- Rename tab `มุมมอง` → **My Thesis** in `LT_TABS`. That tab = one My Thesis section:
  - Fields kept: ① Why buy, ④ Wrong if, Next check (date), What to check, Save, Archive (from PL1).
  - **Images**: add / view / remove (chart screenshots), reusing the existing image storage + thumbnail/viewer code from the old view block (`vwBlockHtml` and its image functions). No new storage system.
- Remove the duplicate legacy personal-view block (Event / Fund. / Tech rows) from the UI.
  - Its existing notes + images must stay visible inside My Thesis (e.g. a "Previous notes" list with original tags + dates, images shown in the My Thesis gallery). No data deleted or rewritten.
- AI Thesis stays separate:
  - Tabs สรุป / ธุรกิจ / ทำไมซื้อ / ติดตาม / ออกเมื่อ = the full AI Thesis (unchanged content, import, data structure).
  - On wide screens, a small **AI Thesis preview card** beside My Thesis: short summary + "imported <date>" (or "data as of <date>" for old records) + "View AI analysis" button → opens the same full AI view (same record). On narrow screens it may sit below My Thesis or be hidden.
  - No AI thesis → empty state with the existing import action. No placeholder text.
- Ownership: saving My Thesis never touches AI data; importing AI never touches My Thesis text, dates or images. Never copy AI research into My Thesis.
- Test: edit text + add image → reload → both persist; import AI thesis → My Thesis unchanged; legacy notes/images still visible.

## 4. Today: "Core Port" → "Selection"
- Change the Today panel label only: `P('core', 'Core Port', core)` → "Selection". Keep "Satellite". No other "Core Port" renames.

## 5. Trade summary when a setup qualifies (Momentum + Compounder plans)
- When the plan's setup conditions pass, show one summary block: **Entry · Size (shares) · SL · Risk (money + % of the pool used for sizing) · RS stars · Reason tags**.
- All values come from the existing plan, sizing calc (Base Risk 1%), `rs_stars`, and the candidate's stored reasons (`CRS_DEFAULT` / candReasons labels). No duplicate tag model.
- Any missing input → show "Missing: Entry / SL / …" instead of a value. RS Unrated → "RS: Unrated". Never invent numbers.
- Same values as the saved plan (test: summary == plan form values).

## 6. Sat: Classify dropdown → 2 checkboxes  (UPDATED 2026-11-05 — supersedes earlier text)
- Replace `Classify` in the TF | Trend | Classify row with two independently saved checkboxes: **EMA50 Verify** and **Structure Verify** (own booleans `ema50_ok`, `structure_ok` on the idea).
- Derived classification: both checked = **Clear Trend**; one or none = **Unclear**. Use this derived value everywhere the system reads classify (badges, readiness, `satTacLock`, `td3PlanStatus`, summaries). All other trading conditions unchanged.
- Legacy plans: keep using the stored `classify` until verification is saved through the new controls. Do NOT auto-tick both boxes from an old "Clear Trend". Show "Legacy classification — verification pending" on these.
- Once saved through the new controls, the checkboxes are the source of truth.
- Message "Needs Clear Trend" → "Needs EMA50 + Structure verify".
- Never alter recorded trades (lock still applies only to unentered Tactical plans).
- Test: each box persists after reload; Tactical unlocks only with both (new) / legacy clear still unlocks until saved; entered trades unchanged.

## 7. Candidate-first workflow (no Ideas stage, no Tier A/B)
- Flow: Add Candidate → Evaluate (screening modal) → Promote to Watchlist → Thesis + plan.
- Remove the stock **Ideas** stage as a required step before Candidate (nav, counters, reminders, "Back in Ideas", onboarding text).
  - Migration (D6, automatic once): migrate only stock ideas with a valid ticker into Candidates (keep notes, mark source "From Ideas"). Skip thematic-only records and tickers already in Candidates/Watchlist. Satellite `satIdeas*` untouched. Completion flag + idempotent (safe re-run, no duplicates). Keep all source records. Final report: migrated count, skipped count, skip reasons.
  - Do NOT touch Satellite trade ideas (`satIdeas*`, `ideaList` usage for Sat, etc.) even if names contain "idea".
- Remove Tier A/B everywhere in stock selection: badges, selectors ("ตั้ง Tier…" in the Edit modal), filters, sorts, promotion checks, and any sizing/eligibility that still reads tier for NEW plans. Stored tier data stays; old plans/trades keep their stored numbers.
  - If removing tier would change sizing math for new plans, STOP and report — don't change it.
- Keep: market filters, Track, reason tags, thesis, images, Archive/Restore.
- Test: new stock → Candidate → screen → Watchlist with no Tier step; legacy Candidates/Watchlist/Ideas records still open and work.

---

## Build order
1. Audit all 7 (one file), wait for OK.
2. Items 4 + 1 (small).
3. Item 2.
4. Item 6.
5. Item 5.
6. Item 3.
7. Item 7.
8. Full suite vs main + screenshots (390/1440) of: Today banner + Selection, My Thesis tab with images + AI preview, Sat plan row, trade summary, Candidate flow. Draft PR. Don't merge.
