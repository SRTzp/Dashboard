# TD3b — Sector Drivers & Evidence (Flow RRG → Today) · tests 105

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/TD3b-verify.txt`). Mockups: `docs/mockups/td3b-flow-rrg-mockup.html` (Flow) · `docs/mockups/td3-sector-mockup.html` (Today rows).
> Start from the PF3b build (index sha `a0d1361f544e…`). Backups: `index.backup-pre-TD3b.html` · `tests/_bk_td3b/`.
> TD3b runs **before** TD3a (the Today 3-panel redesign). It must work on the current Today and be easy for TD3a to move into the Overview panel.

## Part A — User text (verbatim)

Implement a lean Sector Drivers & Evidence workflow within the existing Dashboard. Keep it compact, mobile-friendly, and visually consistent. Minimize changes to the current layout and reuse existing components.

1. Flow › Existing sector rows
* Add a small ☆ / ★ Follow toggle.
* Add a collapsed "Drivers & evidence" section containing:
   * Driver: Short explanation of the potential support behind momentum.
   * Evidence: Supporting or conflicting evidence, with up to three source links.
   * Revisit if: Conditions that would weaken the explanation.
* Show the last reviewed date.
* Keep these details collapsed by default. Do not introduce a separate page or large cards.

2. Copy question → External AI → Import JSON
Add two compact actions inside the expanded section:
* Copy AI prompt: Copy a ready-to-use research prompt containing the sector ID, name, market/reference ETF, current RRG phase, and RRG data date.
* Import answer: Open a small dialog to paste JSON, validate it, and preview the three fields.

The copied prompt should ask:
What supports this sector's relative strength, what evidence supports or contradicts that explanation, and what would invalidate it?
Require the AI to research current sources, distinguish facts from interpretation, avoid assuming price strength proves fund inflows, and explicitly state when evidence is insufficient. Include the required JSON format in the copied prompt.
Use a small payload such as:
```
{
  "schema": "sectorDrivers/v1",
  "sector_id": "EXISTING_SECTOR_ID",
  "research_as_of": "YYYY-MM-DD",
  "driver": "Short explanation; label interpretations clearly.",
  "evidence": {
    "summary": "Supporting evidence and any material contradiction.",
    "sources": [
      { "title": "Source title", "url": "https://example.com/source" }
    ]
  },
  "revisit_if": "Conditions that would weaken the explanation."
}
```
Validate the schema, field types, matching sector ID, and source URLs; allow up to three sources. Invalid imports must not overwrite existing notes. Structural validation does not verify the research itself.
Allow manual editing before and after import.

3. Save and review behavior
* Use "Save & mark reviewed" to save the note and record the app's current review timestamp and valid RRG phase.
* Keep the AI's research date separate from the user's review date.
* Ordinary edits or Follow changes must not reset the review baseline.
* If evidence is empty, show "Supporting evidence not yet recorded."
* If RRG data is unavailable, do not record a fabricated phase or trigger a phase-change flag.

4. Today › Existing Overview
Show only followed sectors, using compact rows:
Sector · Current phase · Driver summary · Reviewed 3d ago
* Following a sector makes it appear immediately, even without a note.
* Without a note, show "Drivers not yet recorded."
* When valid current phase differs from the phase recorded at review, show a quiet "Revisit · phase changed" tag.
* Unfollowing removes the sector from Today but preserves its note.
* Empty state: "No sectors followed — pick 1–3 in Flow ›"
The phase flag is a review reminder, not a conclusion that the underlying explanation has changed.

5. Weekend and storage
* Keep one linked task: "Review drivers for selected sectors." No counter or automatic completion merely because notes exist.
* Store the latest note and follow state per sector in the existing settings document, after verifying its structure and permissions.
* Preserve unrelated settings when saving.
* Do not add daily phase history, weekly note copies, or a new Firestore collection.

Scope and acceptance
* Preserve the existing navigation, RRG calculations, sector ordering, and unrelated Dashboard features.
* Reuse typography, spacing, buttons, expandable rows, and dialogs. Keep iPhone rows readable without horizontal scrolling.
* Include one subtle footer: "RRG shows relative price strength and momentum, not proof of fund inflows."
* No AI API integration, new skill, bulk import, or redesign in this version.
* Verify follow/unfollow, valid and invalid imports, persistence after reload, review-baseline behavior, and missing RRG data handling.

**Agreed earlier (user, 27 Oct):** accepted limitation: with no phase history, a sector that changes phase and returns to its reviewed phase between checks shows no flag. "Revisit if" is the user's own condition; the phase flag is a separate automatic reminder. Starring never touches the note or the review baseline. A newly starred sector with no review never shows the flag.

**User additions (27 Oct, verbatim):**
1. OK to add the "↗" chip to TD3b.
2. For the header, using "Leadership" works well.
3. Make the entire sector card/row fully clickable/tappable, rather than just a small toggle button.
4. Keep the UI headers and labels in English, while allowing user-entered content (drivers, evidence, notes) to be written in Thai.
5. Everything looks good—please proceed with the implementation.

## Part B — Orchestrator notes

### B1. Where things are (verify first)
- Sector rows = Flow RRG `#ffThemes`. Lean view (`ln1On()`): `.ln3-rr[data-rr=SYM]` (l1 = SYM · name · quadrant · days · OFF52W; l2 = gauges). Legacy table `rrgTbl`: **leave unchanged** (legacy view stays as is).
- `sector_id` = the row's `sym` (the ETF, e.g. SMH). Name = `x.name`. Benchmark = SPY (as in the RRG code; confirm). Phase = `x.quad` → `LEADING/WEAKENING/LAGGING/IMPROVING`. Error rows (`x.err`) = no valid phase.
- **Timeframe:** RRG has a Daily/Weekly toggle (`rrgTf()`). Record `reviewed_tf` with `reviewed_phase`. The flag compares only against current data of the **same** tf. If that tf's data is missing, stale (`rrgCacheFresh` false for that tf) or the row has `err` → no flag, and the Today row shows phase "—".
- Today needs the current phase without opening Flow: read the existing RRG cache (`ffState().rrg`, `rowsD`/`rowsW`). Never trigger an RRG fetch from Today.
- Settings store = `getBook(tdHome()).settings` written via the GL1 pattern (`glWrite`/`saveBook`). **Verify** that `saveBook` merges and does not drop fields written by another device (if it writes the whole doc, use a field-path update for `sectorNotes.<SYM>` only). Confirm the Firestore rule for that doc allows these fields; report. No new collection, no rule change expected.

### B2. Data
`settings.sectorNotes = { SYM: { follow:boolean, driver:string, evidence:{summary:string, sources:[{title,url}] ≤3}, revisit_if:string, research_as_of:'YYYY-MM-DD'|null, reviewed_at:ISO|null, reviewed_phase:'LEADING'|…|null, reviewed_tf:'D'|'W'|null, updated_at:ISO } }`
- Caps: driver ≤ 400, summary ≤ 800, revisit_if ≤ 300, title ≤ 120, url ≤ 500 (http/https only; reject `javascript:` etc.). Text rendered as text only. Links `target=_blank rel=noopener`.
- **Save** = writes the fields + `updated_at`. Does not touch `reviewed_*`.
- **Save & mark reviewed** = Save + `reviewed_at = now`, `reviewed_phase`/`reviewed_tf` = the current valid phase/tf of that row, or **null** if there's no valid phase (then show "Reviewed <date> · phase not recorded").
- Follow toggle writes only `follow` (creates the entry with empty fields if none). Unfollow keeps everything.
- Never delete entries (unknown SYM no longer in RRG list → kept, hidden).

### B3. Flow UI (mockup `td3b-flow-rrg-mockup.html`)
- **Keep every existing row element unchanged**: quadrant colour/label, days, OFF52W, both gauges (`rrgGaugeHtml` colour fill + แข็งมาก…อ่อนมาก label) and the Δ ▲/▼ words. New items are added around them only. The mockup shows the real gauges.
- ☆/★ button before the symbol (≥ 32px hit area via padding, not a bigger glyph). Does not toggle row expand.
- `▸ Drivers & evidence` under l2, collapsed; summary line shows `Reviewed <d MMM> (<Phase> · <D/W>)`, the `Revisit · phase changed` tag, or `Drivers not yet recorded`.
- Expanded: Driver (textarea) · Evidence summary (textarea) + up to 3 link chips (`+ link` → title + url) · Revisit if (input) · meta `AI research as of <d> · reviewed by you <d>` · buttons `Copy AI prompt` `Import answer` … `Save` `Save & mark reviewed`.
- Empty evidence (no summary and no sources) → show `Supporting evidence not yet recorded.` in collapsed/Today views.
- Today rows also show the phase in its quadrant colour and the momentum Δ (▲/▼ word, same colours as Flow).
- Footer (one line, muted): `RRG shows relative price strength and momentum, not proof of fund inflows.`
- The existing header "เงินไหลเข้าธีมไหน" is **not** changed in this round (scope). Mention it in the report as a wording conflict with the footer.

### B3b. User additions — how
- **↗ chip** (lean RRG rows + Today rows): only when the row has valid data and momentum Δ ▲ with |Δ| ≥ 0.15 (the existing "ขยับ" threshold). IMPROVING → `↗ momentum rising`, LEADING → `↗ strong + rising`; WEAKENING/LAGGING/err → none. Small green pill, same style family as the tags. A hint, not a signal; computed from existing values only.
- **Header** `เงินไหลเข้าธีมไหน` → `Leadership` (lean view; legacy view unchanged).
- **Whole row tappable**: tapping anywhere on a sector row expands/collapses its Drivers & evidence (one open at a time is not required). ☆/★, links, inputs and buttons inside stop propagation (tapping ★ only follows/unfollows). Keyboard: row is focusable, Enter/Space toggles, `aria-expanded` set. Cursor pointer + subtle hover on Mac; no layout shift.
- **English UI labels** in the RRG panel (lean view) and the Today sector block: `ความแข็ง/โมเมนตัม` → `Strength/Momentum`; levels `แข็งมาก/แข็ง/กลาง/อ่อน/อ่อนมาก` → `Very strong/Strong/Neutral/Weak/Very weak`; Δ words `นิ่ง/ขยับ/ขยับแรง/ขยับแรงมาก` → `Flat/Moving/Fast/Very fast`; `วัน` → `d`; legend/hint line in English. Same thresholds and colours (labels only). User-entered fields accept Thai (no ASCII restriction; caps count characters, not bytes). Old tests asserting the Thai labels: update expected text only, log in `tests/TD3b_retired.md`.

### B4. Copy AI prompt (English, plain text)
Include: sector_id, name, reference ETF + benchmark, current phase + tf + RRG data date (or "RRG data unavailable"), today's date; the question verbatim; rules (research current sources with dates; separate facts from interpretation and label interpretation; price strength ≠ fund inflows; say "Evidence insufficient" when it is; ≤ 3 sources with URLs); the exact JSON template with this `sector_id`; "Return only the JSON". Clipboard API with a select-textarea fallback; toast `Prompt copied`.

### B5. Import answer
- Small dialog (reuse the existing paste dialog/sheet). Validate: valid JSON · `schema === 'sectorDrivers/v1'` · `sector_id` === this row (exact, case-insensitive) · `research_as_of` YYYY-MM-DD and not in the future · string types + caps · `evidence.sources` array ≤ 3, each `{title,url}` with http(s) url. Unknown extra keys ignored.
- Valid → preview the 3 fields → `Apply to form` fills the form (unsaved). The user then picks Save or Save & mark reviewed. Invalid → concise error, form and stored note unchanged.

### B6. Today (before TD3a)
- Current Today: add one compact block `Sectors` at the top of the Mac right column (after Port goal) / after Port goal on iPhone, styled like neighbouring cards. Rows: `SYM · Name · Phase · <driver first ~80 chars> · Reviewed 3d ago` (+ the tag). Order = Flow's sector order. Tap → Flow, RRG panel open, scrolled to that row, its section expanded.
- Empty state `No sectors followed — pick 1–3 in Flow ›`.
- Build it as one function (`tdSectorsHtml()`) so TD3a can place it in the Overview panel.
- Weekend: add one weekly task "Review drivers for selected sectors" to the existing weekly task list (`weekTasks`, manual tick, link → Flow RRG). No counter, no auto-complete.

### B7. Tests — `phase105`
- Follow/unfollow → Today shows/hides immediately; note kept after unfollow + re-follow; reload persists (mock Firestore).
- Save vs Save & mark reviewed: Save changes text but `reviewed_*` unchanged; Follow toggle unchanged; mark reviewed sets date + phase + tf.
- Flag: reviewed LEADING (D) → current WEAKENING (D) → tag; same phase → none; current tf W while reviewed D → none; row `err` / no cache / stale cache → none and phase "—"; mark reviewed with no data → `reviewed_phase:null`, never flags.
- Import: valid → preview → apply → save; wrong schema / wrong sector_id / bad JSON / 4 sources / `javascript:` url / future date / over-cap text → error and stored note byte-identical.
- Copy prompt contains sector_id, phase, tf, data date, the question and the JSON template.
- Other settings fields unchanged after saves (deep-compare minus `sectorNotes`); RRG order/calculation outputs unchanged.
- 300 / 390 / 1280 / 1440 no overflow; no console errors. Screenshots `tests/screenshots/td3b-{flow-1440,flow-390,import-390,today-1440,today-390}.png`. Open every one.
- Full run (runall2.sh, base + 1–105). Known: p13, p5. **This full run also covers the pending PF3b re-run** (phase94 stays at 35%, user approved; exclude `tests/*.backup-pre-*.py` from make_verify "files changed").

## Report back
Settings doc verification (merge behaviour + rule) · files changed · how tf/stale data are handled · test results (full run) · screenshots opened · the header wording conflict · limitations · no push, no file deletion.
