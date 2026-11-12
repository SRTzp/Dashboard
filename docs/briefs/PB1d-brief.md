# PB1d — Drawer closes on form open · Flow lower half in 2 columns (2026-11-12)
New branch `claude/pb1d` from origin/main (PB1/PB1b/PB1c merged in #40). Small. Don't merge. Mockup: `docs/briefs/mockups/pb1d-flow.html`. Run before WL1.

## 1. Plan drawer closes when it opens a form (all types · Mac + iPhone)
- Any drawer button that opens a form / popup / sheet (`Update levels`, `Edit`, `Complete ›`, `Place order ›` confirm, `Filled ✓` price prompt, `Add-on ›`, `Close trade`, `Fix risk ›`, per-level actions in ENTRIES) → **close the drawer first**, then open the form. Applies to Sat, MMT and COMP.
- After Save / Cancel the drawer does **not** reopen (board + toast only).
- iPhone: same — the bottom sheet closes before the form sheet opens (never two sheets stacked).
- Tests: for each type, drawer → Update levels → drawer element closed/hidden while the form is open; Esc on the form → board, no drawer.

## 2. Flow: 4 blocks on top (unchanged) + "Details" in 2 columns, duplicates folded
Below RRG tiles, one header `Details · closed by default · open in place`, then **two independent columns** (Mac ≥ 900px; each column stacks on its own so an opened row never leaves a gap in the other); iPhone = one column. Each row = existing content inside a `<details>` closed by default: icon · title · one-line hint · ›. Content unchanged, only moved/wrapped.
| Left column | Right column |
|---|---|
| 📖 Playbook · full quarter (`pbPanel` — Macro ไตรมาส, history, change-if) | 🧭 Regime details (`ffActionDet` + `ffRegime` + QE bar `ffQeBar` — merged into one) |
| 📅 Weekly Impact · all assets (existing "all assets & import" row) | 🔭 RRG details (`ffThemesPanel`: chart, Fresh, Flat, How to read — the old Leadership card; tiles above stay the summary) |
| 🗓️ US calendar · high impact (`ffCal`) | ✍️ Manual boards · layer 1–2 (`ffManualBoards`) |
- Remove duplicates: the old Leadership/RRG card and the old regime block are no longer shown as full cards (only inside their Details rows). Nothing deleted from data.
- Open/closed state per row remembered per device (try/catch localStorage). Existing deep links (`ln4GoLeadership` → opens "RRG details" and scrolls to it; Playbook links → opens Playbook row).
- Equal row height when closed; hint text ellipsis; no overflow at 390/1280/1440.

## Tests (extend phase373)
Drawer closes on every form-opening action (3 types, Mac + 390). Flow: Details header + 6 rows closed by default, 2 columns at 1280/1440, 1 column at 390; opening a left row doesn't move right-column rows; each row expands to its old content; no old full Leadership/regime card outside Details; deep links open the right row. Rerun 373, phase100, SW2, ui_audit → 0. Screenshots `pb1d-flow-1440.png`, `pb1d-flow-390.png`, `pb1d-drawer-form-390.png`. Commit, push, compare URL, short summary.
