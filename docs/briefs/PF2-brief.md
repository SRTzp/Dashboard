# PF2 — iPhone Core|Sat always 2 buttons · no new-week prompt · readable Macro on iPhone · Today → Sat plan from Strategy assets · tests 99

> User request 25 Oct. **Part A = verbatim, authoritative.** Part B = orchestrator notes (anchors, decisions, tests). If B conflicts with A, A wins — stop and report.
> **Mockups:** `docs/mockups/pf2-mockup.html` + `docs/mockups/pf2-flowchips-mockup.html` (iPhone 390; yellow notes = explanations).
> **User decisions 25 Oct (resolve the two open points):** (1) `ความคิดเห็นเรา` starts **empty** each new week, with an option to **import last week's text** (see B2). (2) Asset selection starts **empty** each new week — fresh selection required (as in B2).
> **Run after PF1 is finished** (PF1 = Strategy Macro-only + new plan form, still running when this was written). Start from the latest index (PF1 result). Backups: `index.backup-pre-PF2.html` · `tests/_bk_pf2/` · do not touch core-size.js · temp files → `_to_delete/` · never rm · no push.

---

## Part A — User spec (verbatim)

Continue from the latest Dashboard version. Implement only the four changes below. These are incremental requirements, not a redesign or a request to restore an older version.

WORK EFFICIENTLY
- Reuse this conversation’s context. Check the current diff and unfinished work first.
- Search and read only relevant components, CSS, state, and handlers.
- Give a plan of no more than 8 bullets, then proceed.
- Reuse existing functions and data. No unrelated refactoring or new dependencies.
- Skip requirements already implemented. Run focused checks.
- Do not return full source code. Briefly report changed files, test results, and unresolved items.
- Do not push, delete files, or overwrite completed work.

1. IPHONE: CORE | SAT SWITCHER
On the Plan page, show Core and Sat as two adjacent buttons from the first render.
- Do not use a dropdown.
- The user must not need to interact before both buttons appear.
- Preserve existing tab selection and remembered-tab behavior.
- Keep the current Mac appearance.

2. IPHONE: “START NEW WEEK”
Remove the existing prompt for selecting which Assets/data to carry forward.
It must no longer block access to the new week’s Strategy.

My opinion / Note handling remains undecided:
- Preserve its current behavior for now.
- Report this as an unresolved decision at the end.
- Do not interpret removing the prompt as permission to delete data.

Preserve existing plans, open positions, history, and the latest behavior of other fields. If the prompt currently triggers required week initialization, retain that initialization without the selection prompt.

3. IPHONE: READABLE BUT COMPACT MACRO CONTENT
Scope:
- Strategy: Macro and “Change when” text.
- Flow: quarterly Macro summary and its expanded reading view.

Mobile changes only:
- Main text approximately 16px, with line-height around 1.5.
- In Strategy, clearly separate Macro and “Change when.”
  Show a 2–3-line preview for each, with “Read more.”
- In Flow, put quarter/version and Asset summaries on separate rows.
  Allow wrapping; do not squeeze everything onto one line or hide remaining Assets.
- The expanded view should use the available mobile width,
  with 16–18px text, vertical scrolling, and an obvious close/back control.
- Ensure all original text is accessible without horizontal scrolling.
- Preserve the original content. Do not generate new summaries.
- Adapt the existing reading view where possible; do not create a duplicate system.
- Do not increase font sizes globally or change the Mac layout.

4. ALL DEVICES: TODAY → SAT PLAN
Use the Strategic Assets selected in the current Strategy as the single source of truth.
Do not create a separate Asset selection list for Today.

State A — No Strategic Assets selected:
- Show “Start by adding a Strategic Asset.”
- Show an “Add Strategic Asset” button that opens the Asset selection area in Strategy.
- Do not use “Bias not assessed” or “Carried-over plans” as the initial action instead.

State B — Assets selected, but some have no trading plan:
- Identify the Assets missing a plan.
- Provide an action to create a plan for the relevant Asset.
- Use the latest existing rules for identifying an active/current plan.
- Closed or cancelled plans do not satisfy this requirement.

State C — Assets already have trading plans:
- Keep the existing plan-related actions.
- Do not show a duplicate “No trading plan” warning.

Today must reflect changes after Assets are added or plans are created.
Preserve access to existing open positions, including those whose Assets are not selected for the current week.

OUT OF SCOPE
Do not change:
- Trend, Zone, Bias calculations, Risk, Core/Sat forms, or other trading logic already updated.
- Macro Playbook data or versions. This task changes presentation only.
- Unrelated Dashboard sections.

ACCEPTANCE CHECKS
- iPhone: Core | Sat is visible on first load, reload, and tab navigation.
- Starting a new week no longer shows the old selection prompt; existing data remains intact.
- Long Macro content is fully readable without horizontal overflow.
- Today correctly handles states A/B/C, including several Assets where only some have plans.
- Open positions remain manageable.
- Mobile CSS changes do not alter the Mac appearance.

---

## Part B — Orchestrator notes

### B1. Core | Sat on iPhone (A1)
- Since HD1 the Plan control lives in the header slot `#hdrSub` (`hdrSubSync` / `hdrSubFit` / `hdrSubCmpBuild`, mobile rule ≤ 480px). On narrow widths it can fall back to the **compact pill / `<select>`** — for **Plan on iPhone never use the compact form**: always the two buttons `Core | Sat` (they fit: ≈ 100px; shrink padding/font at ≤ 340px if needed, never clip). Port may keep its compact rule.
- "From the first render": make sure `hdrSubSync()` runs on initial load / after auth / after the remembered tab (`planScope` memory) is applied / after `document.fonts.ready` — not only on `switchTab`. Test cold load straight into Plan (remembered tab), reload, and switching tabs.
- Mac (≥ 900px) unchanged.

### B2. New-week prompt removed (A2)
- Remove the LN3fix3 prompt from the Strategy render (`nwHtml` / `nwState` / `nwRows` / `nwStart` / `nwLater` / `[data-nw-box]`) on **all devices** (the prompt is the same component on Mac; the user's wording is iPhone but a Mac-only prompt would be inconsistent — report if you think otherwise). Remove its Today pointer if any.
- Initialization check: today `nwStart` only (a) writes the next week's pick list from the ticks, (b) writes `satWeekDrop` for unticked, (c) clears kept assets' fields via the shared fresh-patch helper, (d) sets `satWeekStart[wk]`. None is required for the week to work: a new week starts with **no manual picks**; assets with open positions / active plans still show through the existing auto-pick/parked logic; the user adds assets with `＋ Asset`. Keep that. **Do not** copy last week's picks automatically — **decided by the user: fresh selection each week**.
- My opinion (**decided**): empty in a new week (per-week field, as now). Import option = the existing `คัดลอกจากสัปดาห์ก่อน` link under the box (after PF1 it copies the opinion only): label it `นำเข้าความเห็นสัปดาห์ก่อน`, show it **only when the box is empty and last week has text for that asset**; one tap copies the text into this week (no overwrite of typed text). Old weeks unchanged.
- Keep stored `satWeekStart` data; just stop reading/writing it. Delete code only when nothing else calls it.

### B3. Readable Macro on iPhone (A3 · ≤ 480px only)
- **Strategy tile** (after PF1 it shows Macro · เปลี่ยนเมื่อ · ความคิดเห็นเรา · image): two clearly separated blocks, each with a small label (`Macro`, `เปลี่ยนเมื่อ`) on its own line above the text; text 16px / 1.5; preview clamped to **3 lines** (`-webkit-line-clamp:3`) + `อ่านต่อ` link only when clamped. `อ่านต่อ` opens the **existing Playbook asset sheet** (`pbAssetSheet` — same asset, current active version) rather than a new viewer; if that sheet can't show both texts in full, extend it (not a new system).
- **Flow Macro ไตรมาส card**: head row 1 = `▾ 2026Q4 · v001 · ใช้จริง`; row 2 = asset chips, **wrapping** (no clipping, no `…`, no hidden assets); headline on its own line (HD1/LN3fix3b rule); body text 16px / 1.5; asset rows wrap.
- **Flow chip row only when folded (user, 25 Oct · mockup `docs/mockups/pf2-flowchips-mockup.html`, all devices):** folded card = row 1 `▸ 2026Q4 · v001 · ใช้จริง` → **headline** (own line, wraps, no `…`) → asset chip row (wraps, none hidden). Unfolded card = row 1 → headline → body / asset rows, **no chip row** (each asset row already shows its stance). Black summary bar on top of Flow unchanged. Test: folded has chips + headline; unfolded has headline and 0 chip rows; all assets still visible in one of the two.
- **Reading view** = existing `pbSheet` / `pbAssetSheet` / `pbViewVer` sheets: on ≤ 480px full width (bottom sheet up to ~92vh), body 16–18px / 1.5, vertical scroll inside, a clear `✕ ปิด` (or `‹ กลับ`) button fixed at the top of the sheet; Esc / backdrop still close. `overflow-wrap:anywhere` so long tokens/URLs never cause horizontal scroll.
- Original text only (no new summaries). Mac CSS untouched (all rules inside `@media (max-width:480px)`).

### B4. Today → Sat plan (A4 · all devices)
- Source of truth = assets picked for the current Strategy week (`satWeekPickList(wpWeekKey())` / the same list Strategy shows — `satAssets()` if that is what Strategy renders). The Today Sat routine list `tdRoutine().satDaily` must **not** be used to decide which assets need plans (keep it only if something else needs it; report).
- Active plan = the latest existing rule (e.g. `satV3ShownIdeas()` + `satV3PlanRowState(x) !== 'closed'`, status not closed/cancelled — reuse the exact helper the Strategy plan list uses).
- Implement inside the existing Sat task card of Today (the `satdaily` / `เช็กแผน Sat วันนี้` card) so there is one Sat card, not three:
  - **A** (no assets): text `Start by adding a Strategic Asset` (Thai UI is fine as subtitle: `เริ่มจากเพิ่ม Strategic Asset`) + button `Add Strategic Asset` → `switchTab('plan')` → Sat scope (`setPlanScope('future')`) → open `waSheetOpen()`.
  - **B** (some without plan): list those assets, each with `＋ แผน XAUUSD` → `switchTab('plan')` → Sat → `lfSatSet(asset)` → `satV2NewPlan(asset)` (the same call the Strategy `+ แผน` button uses). Assets that have plans keep the existing ✓/✕ Focus actions.
  - **C** (all have plans): the existing card/actions only, no "no plan" warning.
- The card no longer depends on weekday-only / Focus-done rules for A and B (those are setup steps); C keeps today's rules.
- Re-render Today after `＋ Asset` and after a plan save (existing `todayRefresh()` hooks — add where missing).
- Open positions on assets not picked this week stay reachable exactly as now (parked list "ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้", plan rows, Port). Do not hide them.
- Do not show "Bias not assessed" (removed in PF1) or the carried-over-plans task as the first action in state A; the carried-over task may still appear below it.

### B5. Tests (Chromium · FF_STUB_BASE = Lean) — `phase99`
- Core|Sat: 300 / 320 / 390 cold load into Plan (remembered scope Core and Sat), reload, tab round-trip → two buttons visible, no `<select>`/compact pill, correct one active, clicking switches scope · Mac 1280/1440 unchanged vs PF1 (header boxes ± 1px).
- New week: fake clock Saturday/Monday of a new week → no `[data-nw-box]`, Strategy usable, no assets picked (Today shows state A); `นำเข้าความเห็นสัปดาห์ก่อน` appears only for an asset with last-week text and empty box, copies exactly that text; plans, open positions, old week docs, `opinion_txt` of old weeks unchanged; assets with open positions still reachable.
- Macro iPhone 390 + 300: Strategy Macro / เปลี่ยนเมื่อ separate, 16px, clamp 3 lines + `อ่านต่อ` only when long, opens the existing sheet with the full original text (string equal to the Playbook text), sheet has close control, 16–18px, no horizontal overflow; Flow folded = head + headline + all asset chips (6+ assets fixture), unfolded = head + headline + rows with no chip row, long URL/token wraps; Mac 1440 font sizes and layout unchanged.
- Today: A (0 assets) → message + button opens Strategy asset sheet; B (3 assets, 1 with an active plan, 1 with only a closed plan, 1 with none) → the 2 without active plans listed with `＋ แผน`, buttons open the form for the right asset; after adding a plan Today updates; C (all have plans) → no missing-plan text; open position on an unpicked asset still reachable.
- No console error.
- Screenshots `tests/screenshots/pf2-{plan-header-300,plan-header-390,strategy-macro-390,macro-sheet-390,flow-macro-390,today-A-390,today-B-390,today-B-1440}.png` — open and check every one.
- Old tests: never delete/weaken; update only expectations this brief changes (log in `tests/PF2_retired.md`, e.g. LN3fix3/p93 new-week prompt cases → assert "no prompt", HD1/p97 Plan compact on iPhone → assert two buttons). Update `ไฟล์ที่ห้ามลบ.md`. Related suites during work; at the end full run once, one suite at a time (base + phase 1–99), `caffeinate -i -s`.

## Report back
≤ 8-bullet plan (before starting) · what changed per section · files changed · test results · screenshots opened · anything unresolved · no push, no file deletion.
