# PF3 — weeklyImpact/v2 alignment · Mac Today rebalance · restore PF1 tests · tests 103

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> Start from the current build (index sha `0a8b641e9d87…`, after the overnight PF1→SN1 run).
> Also follow `docs/briefs/STANDING-rules.md` (incl. the verify file `docs/reports/PF3-verify.txt`).
> Backups: `index.backup-pre-PF3.html` · `tests/_bk_pf3/` · do not touch core-size.js · temp → `_to_delete/` · never rm · no push.

## Part A — User text (verbatim)

# Task: PF3 — Align weeklyImpact/v2 Parser/UI, Rebalance Today Layout, and Restore PF1 Tests

## 1. Upgrade `weeklyImpact/v2` Schema, Validation & UI (`Plan › Sat › Weekly Impact`)
- **Allowed `kind` enum:** Accept `release | decision | speech | event | carryover`.
- **Allowed `status` enum:** Accept `scheduled | released | ongoing | postponed | cancelled`.
- **Persist new event fields:** Preserve `previous_period` (`string | null`), `src_actual` (`string | null`), and `source_refs` (`string[]`) through import, save, and reload.
- **Backward compatibility:**
  - Legacy events may omit `previous_period`, `src_actual`, and `source_refs`.
  - Normalize missing `previous_period` and `src_actual` to `null`, and missing `source_refs` to `[]`.
  - Validate source references when present; do not reject legacy records solely because the newly added fields are absent.
- **Source reference validation:** Validate `src_schedule`, `src_forecast`, `src_actual`, and all entries in `source_refs` against `sources` when present. Optional single-source references (`src_schedule`, `src_forecast`, `src_actual`) may be `null`.
- **UI display for `previous_period`:** When rendering `previous` / `previous_revised`, display `previous_period` alongside the "ครั้งก่อน" label when present (e.g., `ครั้งก่อน (Sep 2026)`).
- **Scenario labels (`scenarios_th`):**
  - Preserve `label_th` inside `scenarios_th` items (`{ key, label_th?, text_th }`) through import, save, and reload.
  - Render scenario labels strictly in this fallback order:
    1. Non-empty `label_th`
    2. Built-in Thai mapping (map `occurs` to `"เกิดขึ้น"`, NOT `"เกิดขึ้นตามคาด"`; map `delayed` to `"เลื่อนออกไป"`, `escalates` to `"ตึงเครียดขึ้น"`, `eases` to `"คลี่คลายลง"`, `post` to `"หลังประกาศผล"`)
    3. `"กรณีอื่น"`
  - Never display raw unknown keys as UI labels.
- **Round-trip testing:** Add/update tests verifying both legacy `weeklyImpact/v2` JSON and new `weeklyImpact/v2` JSON through the full **import → save → reload** cycle.

## 2. Rebalance Today Layout on Mac & Restore 15% Threshold
- Inspect the current 15% layout balance metric definition in the test suite first.
- Move the **Sat Plan** card to the right column on Mac/desktop when content is long so column heights stay balanced.
- Restore the layout balance test threshold back to **15%**.

## 3. Re-enable & Update PF1 Test Suite
- Check the exact assertion count and scope of the disabled **PF1** checks (~132 assertions) and re-enable them.
- Update expected values **only** where behavior intentionally changed; do not mask unintended regressions.
- Verify everything passes with actual test execution before completion.

## Part B — Orchestrator notes

### B1. Anchors (approx. lines, verify first)
- `Calc.wiKinds` (~16107) → add `event`. Find the status enum next to it → exactly `scheduled|released|ongoing|postponed|cancelled` (keep any value already accepted today only if old saved docs use it. If so, report it, don't drop it silently).
- `Calc.wiValidate` event normalisation (~16179): add `previous_period` (string ≤ 40 or null), `source_refs` (array of strings, default `[]`). Keep `src_actual`. Existing source check loop `['schedule','forecast','previous','actual']` → also loop over `source_refs` entries. Unknown ref → concise error (same style as now).
- Interp scenario parse (~16210): keep `label_th` (≤ 80, trimmed, empty → absent).
- `WI_SC_LBL` (~21398): add `occurs:'เกิดขึ้น'`, `delayed:'เลื่อนออกไป'`, `escalates:'ตึงเครียดขึ้น'`, `eases:'คลี่คลายลง'`, and set `post:'หลังประกาศผล'`. Keep `above`/`below`/`inline`. One helper `wiScLabel(sc)` = label_th → map → `'กรณีอื่น'`. Use it everywhere scenarios render (Plan Sat, Today news, Flow if any).
- "ครั้งก่อน" render: `ครั้งก่อน (<previous_period>)` when set, else unchanged. Same for the revised value.
- Update `docs/weekly-impact-schema.md` (enums + new fields + label rule). The `weekend-macro-update` skill already emits these fields. Use one of its outputs as the "new" fixture: `kind:"event"`, `status:"ongoing"`, `previous_period`, event `source_refs`, `src_actual:null`, `carryover_th:null`, custom scenario keys with and without `label_th`.
- Firestore rule needs no change (`schema in ['weeklyImpact/v1','weeklyImpact/v2']`).

### B2. Today Mac rebalance
- Today split = `ln3TdMac` / `todayRefresh` (SN1 order: left = ข่าววันนี้ → ช่วงเวลา → แผน Sat; right = Port goal → การบ้านหุ้น → Weekly Stock Summary → อื่น ๆ).
- Rule: after render, if left column height − right column height > 15% of the taller one (the same metric the test uses), move the **Sat plan card** to the right column, placed **after Port goal and before การบ้านหุ้น**. Re-check on resize/re-render (debounced). Keep the move only if it improves balance. Otherwise keep the default.
- iPhone (≤ 480px) and widths below the Mac split: DOM order unchanged (Sat plan stays after ช่วงเวลา).
- Restore 15% in phase94 + phase102 (SN1 raised them to 50%). Log the revert in `tests/PF3_retired.md`. Fixtures: long Sat (4 assets with plans) and short Sat (1 asset). Both must be ≤ 15%, or report the exact numbers if a fixture can't physically reach it (don't relax).

### B3. PF1 retired checks
- Source: `tests/pf1_retire.py` `retired()` = 132 calls across 29 suites, logged in `tests/PF1_retired.md`. First print the exact count per suite.
- For each one: turn it back into a real assertion. If the checked UI or rule was removed by PF1 (Trend/Bias, Range type, 30m TF…), assert the **new** PF1 behaviour at the same spot (e.g. Weekly task = "ทำแผน Sat สัปดาห์นี้", Tactical type hedge/accel, TF 4H, Setup labels) instead of the old one. If no equivalent exists, assert the old element is **absent** and the surrounding flow still works. Never assert nothing.
- Keep `pf1_retire.py` (don't delete). After PF3 it must have 0 callers. Add a note to `tests/PF1_retired.md` mapping each item → its new assertion (or "absent-check").
- Any check that fails for a reason **not** explained by PF1 = a regression. Fix the code, don't change the expectation. List these in the report.
- Do not touch PF2/WM1/WM1b/SN1 retired logs except where B2 requires it.

### B4. Tests — `phase103`
- Parser: `kind:event` and every status accepted; bad kind/status rejected; legacy v2 (no new fields) → normalised `null`/`[]`, saved, reloaded equal; new v2 → `previous_period`, `src_actual`, `source_refs`, `label_th` survive import → save → reload (deep-equal on those fields); unknown `source_refs` / `src_actual` ref → error, nothing written; `src_*: null` OK.
- UI: `ครั้งก่อน (Sep 2026)` shown; without period → plain `ครั้งก่อน`; scenario labels: label_th wins; `occurs` → `เกิดขึ้น` (and the text `เกิดขึ้นตามคาด` appears nowhere); `delayed/escalates/eases/post` mapped; unknown key without label → `กรณีอื่น`, and the raw key text is not in the DOM label.
- Today: 1280/1440 long-Sat fixture → Sat card in the right column, columns ≤ 15%; short-Sat → default place; 390/300 DOM order unchanged; no overflow; no console error.
- Screenshots `tests/screenshots/pf3-{wi-event-390,wi-event-1440,today-long-1440,today-short-1440,today-390}.png`. Open every one.
- Full run at the end: `tests/runall2.sh` (base + phase1–103, 2 workers, solo rerun of failures). Known false failure: p13. Also report p5 and p23 again: run each on `index.backup-pre-PF1.html` to confirm they really fail there too (CC said they're pre-existing).

## Report back
Enum/field changes · exact PF1 count per suite + how each was restored · regressions found and fixed · Today balance numbers (before/after, both fixtures) · files changed · test results (full run) · p5/p23 on pre-PF1 · screenshots opened · limitations · no push, no file deletion.
