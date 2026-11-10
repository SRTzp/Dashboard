# LN4c — iPhone polish: Today status card + Sat form (2026-11-10)
Branch claude/ln4c from origin/main (after HT1 merged if it touches the same lines; else independent). From SRTp's iPhone screenshots — "don't like this": messy wrapping and duplicated rows.

## 1. Today status card (iPhone ≤ 560px)
Now: `● Risk-OFF · W 50 · L75 Risk 0.0%/5.0% · room 5.0R` wraps, Daily|Weekend sits alone on a right-aligned row with empty space, then two big pills `Momentum ½ (regime)` `Compounder ¾ (regime)`.
New (3 compact lines max before HOT):
- Line 1: regime dot + short label (`Risk-OFF`) · `Risk 0.0/5%` · Daily|Weekend switch on the RIGHT of the same line (smaller switch, 12.5px). W/L numbers move to Details (Mac keeps them).
- Line 2 (only when abnormal): ONE small amber chip combining ports: `MMT ½ · COMP ¾ (regime)` — no separate big pills. `room 5.0R` goes at the end of this line, or of line 1 if line 2 is hidden.
- Then HOT / TODAY / To do as now. No empty half-rows anywhere.
- Mac ≥ 900px unchanged except the port pills also merge into one chip.

## 2. Sat plan form (all widths, mainly iPhone)
- **Remove the embedded Today-style summary row** inside the form (`SAT Entry 4,500 · SL 4,480 · 4H · Need EMA50 or Structure verify · Verify ›`). It duplicates the check pills. The form keeps only: check-pill row + bottom hint line.
- **No duplicate messages**: each problem appears once — as a check pill (red/amber). Remove the separate "TP อยู่ผิดฝั่ง … R:R —" line when the R:R pill already says it (merge into the R:R pill: `R:R — · TP wrong side`).
- **Setup chips on iPhone**: one line each, no wrapping inside a chip (In Zone / MMT Neutral / Pivot align MA): chip font 12.5px, nowrap; the 3 chips + `✓ all` fit one row at 390 (shrink padding; if still too wide, the row may wrap to 2 lines but a chip never breaks inside).
- **Account rows (OUN / FAM)**: one line on iPhone — dot + name · status text (ellipsis) · `ข้าม` button on the right of the same line. "Can't size: Brent spec missing → Set ›" truncates with the Set link kept visible.
- Bottom hint stays one line (`ใส่ TP ให้ R:R ≥ 1.5 ก่อน — บันทึกเป็นร่างได้`).

## Tests
- 390: status card ≤ 3 lines before HOT, switch on line 1, single port chip, no lone switch row; Mac shows merged port chip.
- Sat form 390: no embedded summary row; each error text appears once; Setup chips never wrap inside; account rows one line with ข้าม on the right.
- Screenshots 390 (viewport) Today top + Sat form; 1280 Today. Rerun 369, 370 + Sat form suites. Commit, push, compare URL. Don't merge.
