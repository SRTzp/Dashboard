# PB1c — Sat form polish + Flow v2 (2026-11-12)
Branch `claude/pb1` (on top of PB1 + PB1b rev 3.1). Don't merge. Mockup: `docs/briefs/mockups/pb1c-flow.html` (A = Sat trend row, B = Setup ready, C = Flow Mac, D = Flow iPhone 390×844).
Principles: lean, calm, symmetric; existing tokens/components; no empty columns; no wrapping/overflow at 390/1280/1440.

## 1. Sat form — Trend on ONE row (Mac + iPhone)
`TREND HTF · EMA50 [✓✗] · Structure [✓✗] · (all ✓)` on a single line, thin divider above/below. iPhone ≤ 400px: labels `HTF` / `Struct.`, toggles 26px, `all ✓` pill small at the end (still 0.8 s hold). Nothing wraps at 360–390.

## 2. Place-order confirm — numbered, easy to scan
Title `Setup ready on Execution TF?` then a numbered list (green number circles), item + small grey hint:
1. **In Zone**
2. **Trend Neutral** — ready to run, room to go
3. **EMA50 = HVN** — converging: accumulation, cost near price
4. **Pivot MMT** — break → momentum
(+ `MSS confirmed per your rules (candle closed)` line for MSS trades.) Then the summary box, `[Not yet] [Yes · mark ordered]`, tiny note "One tap confirms all 4 · records only — place the order at your broker." Same 4 items in the form's reminder line.

## 3. Flow v2 — 4 blocks, top → bottom
1. **Risk strip** (one card, 3 equal cells): `Momentum 100%` │ `Compounder 100%` │ `● Risk-ON · <reason>` — same numbers/regime the app already computes.
2. **Macro · this week** (header: "sorted by impact · tap a card for notes" + week selector). One card per asset, **4-col grid on Mac, 2×2 on iPhone**:
   - name + bias tag (Bull/Neutral/Bear) on one line, ★ focus toggle top-right (existing weekly-pick data);
   - Mac: one-line medium-term view (Playbook text, clamp 2 lines); iPhone: hidden;
   - bottom line: Weekly Impact badge HIGH/MED/LOW + its events (from Weekly Impact JSON);
   - tap → expands Change-if + this week's note (editable as before; restores content lost with the Strategy page);
   - sort: impact HIGH → MED → LOW → none, then ★ first. Show max 4 (★ first); more assets → small `+N ›` card that expands the rest. ＋ Asset stays (in the `+N` card or the header).
   - Equal card heights per row.
3. **Events row**: next 3 upcoming events only (past ones drop) — Mac: 3 pills in one row + `Import` button; iPhone: 3 compact lines under a small `Events · Import` header. Empty → one line "No Weekly Impact yet · Import".
4. **RRG · sectors vs SPY** (Daily | Weekly as now): **4 tiles = 4 quadrants** (Leading · Improving · Weakening · Lagging), 4-col on Mac, 2×2 on iPhone. Tile = quadrant name (quadrant colour) + subtitle by position only (`Beating SPY · momentum up`, `Lagging SPY · momentum up`, `Beating SPY · momentum down`, `Lagging SPY · momentum down`) + sectors.
   - **Per-sector motion from the EXISTING per-sector calculation** (the data behind Strengthening/Fading/Recovering/Worsening + Fresh) — not from the quadrant: `↗ speeding up` (green) · `→ slowing` (grey) · `↘ slowing fast` (amber). Mac row: `XLU ↘ slowing fast   +2.4`; iPhone: `XLU↘` inline + one legend line at the bottom.
   - Max 3 sectors per tile (by RS desc), `+N` for more; equal tile heights. Keep the existing "How to read" and breadth warning as a small link/tooltip, not a block.
   - Remove the old RRG card layout and any empty column next to it.
- Fund flow / other existing Flow content goes below these 4 blocks (unchanged content, full width, no empty column).

## 4. iPhone = one screen
At 390×844 (incl. app top bar + bottom tab bar) blocks 1–4 fit **without scrolling** (content below them may scroll). Test: content height of blocks 1–4 ≤ viewport minus bars.

## 5. Carry-over fixes from PB1b review (skip any already done, say which)
- Toast "Plan saved · View in Plan ›" never covers an open popup/sheet (queue until close); one line.
- Sat form macro line shows the asset bias + next event (`Macro: Bull · ⚠️ CPI Tue 19:30`), not "▲ Macro".
- Mockup/brief notes say rev 3.1.

## Tests (extend phase373, 390/1280/1440)
Trend row single line at 360/390/1440; confirm shows 4 numbered items (+MSS line when MSS). Flow order Risk → Macro → Events → RRG; Mac grids 3/4/3/4 with no empty column; card heights equal; sort by impact; ★ toggle; tap expands notes (editable, saved); `+N` when > 4 assets; events = next 3 upcoming; empty Weekly Impact state. RRG: 4 tiles, per-sector motion label matches the existing per-sector calc (fixture: a Leading sector with falling momentum shows ↘ slowing fast); max 3 + `+N`. iPhone 390×844: blocks 1–4 fit without scroll. Toast never overlaps a sheet. Rerun 373, phase100, SW2, 369, 370, ui_audit → 0. Screenshots `tests/screenshots/pb1c-*.png` (Flow 390/1440, Sat trend row 390/1440, confirm 390/1440). Commit, push, short summary + results.
