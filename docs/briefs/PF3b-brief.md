# PF3b — fixes after PF3 + Sat draft accordion + Weekly Impact header + text size · tests 104

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/PF3b-verify.txt`). Start from index sha `2ce68136165f…` (PF3).
> Backups: `index.backup-pre-PF3b.html` · `tests/_bk_pf3b/`.

## Part A — User text (verbatim)

Sounds good, let's go ahead with PF3b for #1 and #4.
(#1 = p23 regression from WM1: two user-doc writes after migration · #4 = Today news line shows "ครั้งก่อน 2.7%" without previous_period)

For #2, let's try allowing the time slots to move first. If that still doesn't solve it cleanly, we can relax the threshold to 30% to keep things simple.
(#2 = phase94 Mac Today columns 31–32% apart at 1280/1440)

Also, I have a few additional tweaks I'd like to include:

Fixing
Update Plan › Sat so only one draft plan form can be expanded at a time.

Within "Plans & Open Positions," display:
1. Open positions and saved plans.
2. Inactive drafts, collapsed into compact rows using their existing headers.
3. The active draft, displayed as a fully expanded form.

Behavior:
- Selecting another draft collapses the current draft, moves it into the collapsed group above, and opens the selected draft below.
- Clicking "+ Plan" collapses the current draft and opens the new form.
- Clicking the expanded draft's header collapses it; all drafts may be collapsed.
- Preserve every entered value when collapsing or switching drafts. Do not reset fields or create duplicate records.
- Do not show the active draft again in the collapsed group.
- Apply the same behavior on desktop and mobile.
- Keep existing risk calculations, validation, and save behavior unchanged.

Verify with at least three drafts:
- No more than one form is expanded.
- Collapsed drafts always appear above the expanded form and below saved plans.
- All entered values remain intact after switching between drafts.

Show the diff and verification results. Do not deploy.

—

Make the Weekly Impact header more compact, especially on iPhone.

Move the date range and updated timestamp beside "Weekly Impact" instead of displaying them as separate full-width rows.

Desktop:
Weekly Impact  26 ต.ค.–1 พ.ย. · ICT  อัปเดต จ. 26 ต.ค. 10:43  [Paste]

iPhone:
Weekly Impact  26 ต.ค.–1 พ.ย. · ICT  [Paste]
               อัปเดต จ. 26 ต.ค. 10:43

Requirements:
- Use a compact flex/grid layout with minimal vertical spacing.
- Display metadata in smaller, muted text.
- Keep everything on one row when space allows.
- On narrow screens, wrap the updated timestamp beneath the date range, as part of the same header.
- Keep Paste accessible with an adequate touch target.
- No horizontal overflow, overlapping text, or truncated dates.
- Verify at 320px, 375px, 390px, and desktop widths.
- Change presentation only; preserve date/time values, timezone, and existing behavior.

Show the diff and verification results. Do not deploy.

Increase the text size by one step from the current sizing to improve readability, especially on iPhone.

Keep the layout compact by tightening unnecessary padding and gaps rather than shrinking the text. Allow natural wrapping where needed, with no clipping, overlap, or horizontal scrolling.

Preserve the existing visual hierarchy and functionality. The goal is simple: easier to read while staying compact.

Show the diff. Do not deploy.

**Scope of the text-size change (user's answer):** "Weekly Impact + Macro Card of each asset".

## Part B — Orchestrator notes

### B1. #1 p23 (WM1 regression)
- Cause (from PF3 report): the first `weeklyImpact` snapshot → `wiRefreshAll()` → `satV3Render()` → `satCarrySync` → `satWeekPickWrite` = a 2nd write to `users/{uid}` ~400ms after the migration write.
- Fix: `wiRefreshAll` re-renders Strategy only when Plan › Sat is visible (else set a dirty flag → render on tab open), **and** `satCarrySync` must not write when nothing changed (compare before write). Never skip a real change.
- p23 must pass as written (1 write, still 1 after 2 s). Don't edit p23.

### B2. #4 Today news previous_period
- Today "ข่าววันนี้" line uses the same rule as the panel: `ครั้งก่อน (<previous_period>) <value>` when set, else unchanged. Reuse the PF3 helper, don't duplicate.

### B3. #2 Mac Today balance
- Step 1: extend `tdBalance()` so the **ช่วงเวลา** card may also move to the right column (try: Sat only → slots only → both; keep the option with the smallest difference; never make it worse than default). Order inside the right column stays: Port goal → moved cards → การบ้านหุ้น → Weekly Stock Summary → อื่น ๆ. iPhone / < 1000px DOM order unchanged.
- Step 2: if phase94 (and phase102/103 long/short fixtures) still exceed 15% after step 1, set the threshold to **30%** in those suites and log it in `tests/PF3b_retired.md` with the measured numbers. Report which step ended it.

### B4. Sat draft accordion (Plans & Open Positions)
- One state value `satActiveDraft` (draft id or null), kept in memory. Values live in the draft objects that already exist; collapsing must not re-create the form from defaults. Read the fields into the draft before collapsing (same path the save uses, without saving to Firestore unless the current code already autosaves drafts — report which).
- Render order: open positions + saved plans → collapsed drafts (existing draft header row, tap = activate) → the active draft form. The active draft never appears in the collapsed group.
- "+ แผน" (+ Plan): collapse the current draft (keep values) → new draft becomes active. Header tap on the active one → `satActiveDraft = null`.
- Re-render after save/delete: saved draft → saved plans group; active = null.
- Do not change risk calc, validation, save or the PF2/LN3fix3 "+Asset reset" behaviour.

### B5. Weekly Impact header
- Header = one flex row with wrap: `Weekly Impact` (title) · meta (`<range> · ICT`, `อัปเดต <asof>`) small and muted · `Paste` pushed to the right (`margin-left:auto`), hit area ≥ 40×40 (padding, not bigger text).
- ≤ 480px: title + range + Paste on row 1, `อัปเดต …` wraps under the range (meta aligned with the range, not under the title's left edge if it fits; otherwise under the title). Dates must never be cut off (`white-space:nowrap` per date token, wrap between tokens).
- Same text and values as now (only layout).

### B6. Text +1 step (Weekly Impact panel + each asset's Macro card) — PINNED, follow `docs/mockups/pf3b-text-mockup.html`
- **Macro card = the per-asset Strategy tile** `.ln1-tile` (built in the function that renders `data-ln1-tile`): tile title, `.wiStrip` (`.wiS1` `.wiS2` `.wiSL` `.wiTierP` `.wiCardDet`), Quarterly Macro `.ln3-zr.pf2-blk` (+ its `.ln1-lab`, `.pf2-tx`), Change if `.ln3-chg` (`.pf2-k`), Note `.ln3-op` (label + textarea), links `.ln3-links` (`.ln1-link`). Scope every rule under `.ln1-tile` so `.ln1-lab` / `.ln3-zr` elsewhere (the plan form) do not change.
- **NOT in scope:** `.ui-mac*` (Macro block inside the plan editor form), Today `.wiTd*`, Flow `.pbCard`, the account boxes, the right column.
- **Weekly Impact panel** `.wi` and children: `.wiT` 15→16 · `.wiSm` 12→13 · `.wiWarn` 12.5→13.5 (margin-top 6→4) · `.wiNm` current+1 · `.wiTx` 10.5→11.5 · `.wiDet`/`.wiDetH` 14→15 (padding 10→8, margin-top 6→4, line-height 1.5→1.45) · `.wiK` 12→13 (margin-top 8→6) · `.wiEv` margin-top/padding-top 8→6 · `.wiAct` 13→14 · `.wiBdg` 11→12 · `.wi` padding 10px 12px → 8px 10px · `.wiRow` gap/margin-top 6→4.
- **Tile:** `.wiStrip` padding 8px 10px → 6px 8px, margin-top 10→8 · `.wiS1` 12→13 · `.wiSL` 14→15 · `.wiTierP` 11.5→12.5 · `.wiCardDet` 14→15 · tile title +1 · `.ln1-lab` (in tile) 12→13 · `.ln3-zr`/`.ln3-chg` text 13→14, line-height ≈1.38, margin-top 8→6 · Note textarea font +1 · links +1 · tile padding −2px.
- Header layout (B5) as in the mockup: grid `title | meta | Paste`; meta = range then `อัปเดต …` wrapping under the range; when the panel is narrower than ~300px, meta moves to its own row under the title. Each date token `white-space:nowrap`.
- Targets measured in the mockup (sample data): Mac WI panel 123→83px, tile −2%, Plan › Sat columns 20%→14%; iPhone 390 WI panel 123→101px, tile ≤ +10%. Report the real numbers.

### B7. Tests — `phase104`
- p23 passes unchanged; Strategy still renders the carry-over when you open Plan › Sat after a Weekly Impact snapshot.
- Today news `ครั้งก่อน (Sep 2026) 2.7%`; without period unchanged.
- Today balance: report numbers for default / Sat moved / slots moved / both at 1280 + 1440 for phase94 + the long/short fixtures; result ≤ 15% (or ≤ 30% with the log entry).
- Accordion with 3 drafts, at 390 and 1440: ≤ 1 expanded form at every step; DOM order = saved → collapsed → expanded; fill different values in each (entry, SL, TP, lot, notes, checkboxes), switch A→B→C→A, + แผน, collapse all → every value intact; draft count unchanged (no duplicates); risk numbers identical before/after switching; save one → it moves to saved plans and the others keep their values.
- WI header at 320 / 375 / 390 / 1440: Paste box ≥ 40×40; header height ≤ 2 text lines at 320–390 and 1 line at 1440; no overflow; date text not clipped (`scrollWidth <= clientWidth` for each meta span); same date/time strings as before.
- Text size: computed font sizes in both blocks = old + 1px; block heights within +10% of before at 390 and 1440; no overflow at 300/320.
- Screenshots `tests/screenshots/pf3b-{today-1440,today-1280,drafts-390,drafts-1440,wi-320,wi-390,wi-1440,macro-390}.png` — open every one.
- Full run at the end (runall2.sh, base + 1–104). Known: p13, p5 (pre-existing).

## Report back
Per item: what changed + diff excerpt · balance numbers + which step ended #2 · accordion: draft autosave yes/no, verification results · Macro card selector · files changed · full-run results · screenshots opened · limitations · no push, no file deletion.
