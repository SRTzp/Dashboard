# PS1c — Plan form redesign + Today homework row (2026-11-08)
Branch from main AFTER PS1b is merged: claude/ps1c. UI + display only; sizing math unchanged except §3 input meaning. Mockup: claude/mockups/ps1c-plan-form-mockup.html (Project).

## 1. Sat form alignment
- Entry / SL / TP inputs on one baseline: the Entry "＋" sits on the LABEL line (small 20px icon), never pushes the Entry box down.
- Entry 2 row stays inside the Entry column: `[price][50 %][✕]` with the same column width as Entry 1. SL and TP columns stay empty on that row. No full-width row.

## 2. Bug (again): form ignores the Momentum / Compounder switch
- Seen after PS1b: header "New Compounder plan" but chip "Momentum · Normal" and Momentum regime "half size". §7a didn't fix it.
- Fix: the form gets its OWN segmented switch `[Momentum | Compounder]` in its header (synced both ways with the top switch). Each port keeps its OWN draft (switching does not carry typed values across; switching back restores that port's draft). Title, risk range, regime factor, size cap, bucket cap, min stop and status chip ALWAYS come from the selected port. Test: switch 5 times with typed values; every visible rule matches the selected port; the chip, title and regime always agree.

## 3. Entry split = % of the idea's risk
- Each entry row's field is "Split %" of the idea risk (default even: 50/50, 34/33/33, 25/25/25/25; editable). Must total 100% → otherwise one-line error, Save blocked.
- Changing "Risk per idea" updates all rows automatically. Stored per row: split %. Same shares maths as now (row risk = idea risk × multipliers × split).

## 4. Redesigned stock plan form (see mockup A/B)
- Header: "New plan" + [Momentum | Compounder] switch.
- Row: Account | Ticker.
- Default (single entry + single SL): one row `Entry ＋ | SL ＋ (−x.x%) | Risk %` + summary `#57 · 4.0% · Risk 0.20%` + small amber pill for any multiplier ("½ regime").
- After ＋: "Risk per idea [0.50 %]" with pill "× regime 75% → 0.375%", then two compact tables with IDENTICAL column grid on every row: `price (flex) | 76px % | 92px result | 24px ✕` — the ✕ column is reserved (empty) on row 1, so row 1 is never wider than rows 2–4.
  - Entries: price | Split % | `#17 · 0.6%`
  - SL: price | Out % | distance `−19.6%`
- Summary: `#51 · 1.6% · Avg 44.80 · Risk 0.37%`; Details collapsed.
- Inputs ≥ 16px font; 390px: grid shrinks the price column only; nothing wraps or overflows.

## 5. Today › Plans: homework visible
- Plan rows whose idea has pending homework show the same "⚠ Homework" / "⚠ Overdue 2d" badge (PS1b §8) next to Draft.

## 6. Today homework = ONE row
- Replace one card per stock with a single pinned row: `Homework  [AVGO 3d] [GLBE 3d] [NVDA overdue]  thesis + screening  [Do it ›]`.
- Chips amber, overdue chips red; > 3 → "+N". Row border red if any overdue.
- Tap a chip → open that stock's homework; "Do it ›" → the most urgent one. Still not dismissible.

## Tests
- Sat alignment at 390/1440; Entry 2 width = Entry 1 width.
- Scope: per-port drafts, all rules follow the selected port (title/chip/regime/caps/min stop).
- Split %: even defaults, total≠100 blocks, risk change updates rows, shares match PS1b maths for the same inputs.
- Row widths equal (row 1 vs rows 2–4) at 390/1440.
- Today: Plans badge; homework single row with 1, 3, 5 items (+N), overdue colour.
- Log changed expectations in tests/PS1c_retired.md. Screenshots 390/1440. Draft PR → main. Don't merge.

## FINAL LAYOUT (overrides §1, §4 where different) — follow the mockup claude/mockups/ps1c-mockup-proper.html
### 7. Plan page top bar: Core | Sat
- The Plan scope switch becomes 2 buttons: **Core | Sat** (replaces Momentum | Compounder | Sat).
- Main tabs (Today … Port) stay EXACTLY where they are on every other page (centered); Core | Sat sits on the right, before the action icons. Remove the PL2c "shift main tabs left on Plan" rule.
- Inside Core: Momentum | Compounder switch in the dark Core header AND in the New plan header (both synced, per-port drafts as §2).
- Existing keyboard shortcuts keep working: the old Momentum / Compounder keys open Core and flip the switch; the old Sat key opens Sat.

### 8. Stock form — 2 columns after ＋ (replaces the stacked tables in §4)
- Single trade (default): one row `Entry ＋ | SL ＋ | Risk %`; SL distance (−5.0%) under the SL box.
- After ＋: `Risk per idea [x %]` + regime pill; then two columns side by side: **Entry · split** (price | split % | ✕) and **SL · out** (price | out % | ✕). Each row's result sits UNDER its own box in small text: entries `#17 · 1.2% of Comp`, SLs `−19.6%`. Row 1 reserves the ✕ space so all rows are equal width. 390px: price boxes ~85px, nothing wraps.

### 9. Sat form alignment (replaces §1 details)
- Entry ＋ on the right of the "Entry" label line. Entry 2 box is the SAME size as Entry 1 (same column); its 50 % field + ✕ sit right after it in the SL column. TP column empty on that row.

### 10. Summary line — every % = % of TOTAL portfolio (SRTp 2026-11-08, replaces option A)
- One standard on all main screens: every % shown is of the total portfolio. Form header shows a small muted note "· % = of total portfolio" (Mac; hidden on 390px if no room).
- Summary: `#57 · 4.0% · Risk ฿9.9k (0.20%)` + regime pill when a multiplier applies. Risk money in THB (k, 1 decimal).
- Entry rows: `#17 · 0.6%` (of total). Size-cap message: "Above max size 7.5% — shares will be trimmed".
- Port % line is ALWAYS visible directly under the summary, smaller and lighter (≈11.5px, light grey #a3a8b0): `13.2% of MMT · cap 7.5% (25% of MMT)` with a small "Details ›" at the right end (the rest of Details stays collapsed). It must look clearly secondary to the summary.
- Port cards keep risk as % of total vs the bucket cap (e.g. `0.20% of 1.5% cap`).
