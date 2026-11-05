# PL1 — Pipeline Redesign Brief (Momentum / Compounder)

Status: AGREED SCOPE (2026-11-04). Code not modified yet.
Repo: `main`. Run `git pull` first.

## Core idea — Ready vs Rank
- **Screen** (Candidate → Watchlist) = who may be watched.
- **Ready** (hard rule) = may I open a trade plan.
- **Rank** (RS stars, sort only) = where I look first. Never blocks anything.
- **Setup** = when (already defined elsewhere, not in this brief).

## Global rules
- Rename UI labels only: Winner (and "Core" where it means the Winner bucket/page) → **Momentum**, Ladder → **Compounder**. Where "Core" means the whole stock portfolio (Core.US / Core.TH accounts, Core pool total), ask before renaming. Keep internal keys `winner` / `ladder` so all data/history stays.
- No auto move / auto delete anywhere. Legacy records show "Unspecified" for new fields.
- No automated TradingView/AI calls. All lens / EMA values are manual.
- Success messages only after the database write succeeds. Drafts must survive refresh/network errors.

---

## Phase A — Pipeline

### A1. Add Candidate (Today and Watch use the same flow)
- Ticker box → Add → one popup listing every typed ticker as a row.
- Per row: **Track** (Momentum / Compounder) · **Reasons** (multi-select) · **Note/Link** (optional) · Remove-row button.
- "Apply to all" for Track + Reasons, with per-row override.
- Validate before save: duplicates, ticker format, daily quota. Save only valid rows; quota counts only saved rows.
- Cancel = nothing saved, typed tickers stay in the box.
- **Settings → Candidate Reasons:** add / rename / deactivate (never hard delete; old records keep their reason).
- Starter reasons: Strong RS · Volume Spike · Earnings Spike · Break 52W High · Legendary Copy · Investing Copy.

### A2. Candidate → Watchlist (screening modal)
| Field | Type |
|---|---|
| Fortress | dropdown |
| Proven Growth | dropdown |
| Emerging Growth | dropdown |
| **Trend 40 EMA** (Weekly if Momentum · Monthly if Compounder — label follows Track) | dropdown |
| Why Watch | text, required |
| Concerns | text, optional |
| Exception Reason | text, shown + required only when no lens passes |

Dropdown values (all 4): Not Evaluated (default) · Pass · Fail · Insufficient Data · N/A.
Only **Pass** counts as passing.

**Rule to enter Watchlist:**
1. Trend 40 EMA = Pass (**mandatory** — otherwise stays in Candidates), AND
2. ≥ 1 lens Pass + Why Watch, OR no lens Pass + Why Watch + Exception Reason.

- Removed from screening: RS, Gate 5, Stars.
- Save the screening record with timestamp → visible on the Watchlist card as **Onboarding Data**.
- Carry Track, Reasons, Note, Link, add date into the Watchlist record.

### A3. RS Stars (manual rank only)
Values: Unrated · 0 · ★ · ★★ · ★★★ (Unrated ≠ 0). Save last-rated date.
- ★ = starting to outperform, not consistent · ★★ = consistently beats market · ★★★ = clear leader.
- Used only to sort/filter the Watchlist. Not a queue, not a gate, no effect on risk or size.
- Do NOT convert old stars. Old star values are ignored (kept in data, not shown as RS).

### A4. Risk — one value
- **Settings → Base Risk per trade: 1% of the portfolio pool** (Momentum pool and Compounder pool each).
- **Remove entirely:** stars → base risk formula (`starBaseRisk`, `starBudget`, `starsFromEval`), auto star suggestions, the "Stars required" check, and the old open-plan gate (RS + Gate 5 + Stars, `evalGate`). Audit all ~12 call sites.
- **Keep:** size = risk ÷ (entry − stop), existing regime/DD multipliers, per-stock caps, account caps.
- **Add-ons:** keep the current add-on feature as is. Start with one entry; deciding which positions get adds is done later, per position.
- Old plans and closed trades keep their stored risk/size numbers — never recalculate history.

### A5. New "Ready" rule to open a trade plan
- Stock is on the Watchlist (not archived), AND
- My Thesis has **① Why buy** and **④ Wrong if** filled (any length). Old Event/Fund./Tech notes do not count.
- Nothing else. Stars/RS/Gate 5 never block. Existing open trades are not affected.

### A6. Watchlist management
- Filter: Track · Reason · RS stars. Sort: RS stars (default), last updated.
- Show separate "Last updated" for My Thesis and AI Thesis.
- **Next check:** a date field + short text "what to check". Sortable. (No reminder system.)
- Status tag (auto): **Drafting Thesis** (① or ④ empty) · **Awaiting Setup** (Ready, no plan) · **Plan Ready** (plan exists).
- **Archive with reason** + Restore. Archive keeps thesis, notes, reasons, versions. No delete as a substitute.

### A7. Today — one "Plans" block (compact)
- One block on Today with 3 small groups: **Momentum · Compounder · Sat**. Fit the existing Today style (same row/height/typography as current td3 rows). No new page.
- Each row, one line: `TICKER · Draft|Open · <short info>`
  - Draft → missing fields (e.g. "Entry / SL missing") or "Ready to enter".
  - Open → status dot only (🟢 / 🟡 / 🔴 / ⚪ from the card status).
- Tap row → opens that card/plan (reuse existing open functions: td3 draft open, coreOpenCardOfTrade, td3SatOpen).
- Sat's current Today section moves into this block (same data: td3SatRows). Keep its "No-trade this week" and "no plan" handling.
- Hide empty groups. Max ~5 rows per group, then "+N more ›" (opens Plan tab). No overflow on mobile.
- Momentum drafts: today only incomplete drafts show (td3CoreDrafts) — extend to complete drafts + open positions. Include Compounder (remove the `strategy!=='L'` exclusion).

### A8. Compounder page = Momentum layout
- Render the Compounder scope with the same components as Momentum (lfCoreBoxHtml / lfCoreSwHtml / lfCoreCardsHtml), filtered by track. Retire the separate Ladder page (ldrHtml / renderLadderPanel / ladder-level table).
- Same card, same plan form, same add-on feature, same sizing (1% of the Compounder pool, per-stock cap stays).
- Card status line: **Momentum = existing EMA10 rule** (unchanged). **Compounder = Weekly 40 EMA**: close below → 🟡 "no adding"; below Stop → 🔴. Needs a 40W EMA value per card (manual field, like the existing EMA input); empty → status from Stop only.
- No live ladders exist → no migration needed. Do not delete ladder code paths' stored data; just stop rendering them. Retire ladder-only tests (log in tests/PL1_retired.md).

---

## Phase B — Thesis

### B1. Watch → Thesis view: 3 panels
**My Thesis** · **AI Living Thesis** · **Previous Notes**

### B2. My Thesis — 5 sections (with example prompt text in each box)
1. Why buy — what is improving and not yet priced in?
2. Price driver & timing — what moves the price, and when?
3. Key numbers — 2–3 metrics to watch.
4. Wrong if — what breaks the thesis (data, event, or time limit).
5. Trade plan — entry / stop / targets, or "Pending Plan".

- Save Draft (auto + manual). Works even with no AI thesis.
- TradingView chart **link** + reference links (no image upload).
- **Versions:** each "Save version" stores a dated copy. Show a list; open any version read-only. Start new from blank or from a copy. (No diff viewer.)

### B3. Previous Notes
- Show old Event / Fund. / Tech notes in date order with their original tags. Read-only. Do not copy them into the 5 sections.

### B4. AI Living Thesis
- Keep the current manual import. Show data date + last updated.
- Never writes into My Thesis.
- Keep **latest full version only** + a list of **dated short summaries** of older imports (labelled "summary").

---

## Out of scope (dropped)
Image upload/paste · side-by-side diff · full-text AI history · reminder scheduler · strict star queue · automated EMA/lens data · per-Track screening rules · Gate 5 anywhere.

## Tests (must pass)
- Multi-ticker popup: validation, partial save, cancel, quota, write failure.
- Screening: EMA Fail keeps stock in Candidates; exception path; record saved with timestamp.
- Changing RS stars never changes risk or size.
- New plans use 1%; old plans/trades unchanged.
- Ready rule: blocked without ① and ④; allowed with them.
- Archive/Restore keeps everything. Thesis versions open correctly after refresh and backup/restore.
- Labels show Momentum / Compounder; old data intact. Update existing test expected values for renamed labels and removed star/gate logic (log in a retired-tests file like RG2b).
- Desktop + mobile layout.

## Build order
1. Backup + audit star/gate/risk call sites.
2. A4 (risk) + A3 (RS stars) — together, since stars and risk are linked today.
3. A1 popup + Settings reasons.
4. A2 screening + A5 Ready rule.
5. A6 Watchlist management.
6. A8 Compounder page = Momentum layout.
7. A7 Today Plans block.
8. Phase B.
9. Full test run vs main.
