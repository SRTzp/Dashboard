# RRG1 — test expectations intentionally changed

Cause: state model changed from z-score quadrant (ratio/mom ≥ 100) to explicit raw relative-trend states
(lead/weak/imp/lag + new `flat`), labels renamed, card text changed. Fixtures that seed rows now go through
`tests/rrg1_fixture.py` (legacy-shaped row → model-2 row: adds model, eps, delta, rawChg, rel, momUp; rsTrend sign follows quad)
and seeds stamp `f.rrg.model = RRG_MODEL` + `lastBar`.

| Suite | Old expectation | New expectation | Why |
|---|---|---|---|
| p8 | row labels LEADING/IMPROVING/WEAKENING/LAGGING | "Outperforming · strengthening / Underperforming · recovering / Outperforming · fading / Underperforming · worsening" | renamed states (C) |
| p12 | transitions "→ Improving", "→ Weakening" | "→ Underperforming · recovering", "→ Outperforming · fading" | `RRG_QUAD_LABEL` renamed |
| p14 | action-bar text snapshot "↗ Energy → Improving" | …"→ Underperforming · recovering" | same |
| p86 | hero "(RRG Leading)"; row "LEADING · 6 · −3.2%" | "(Outperforming ↗)"; "Outperforming · strengthening · 6 bars in state · 3.2% below 52W high" | copy (C) |
| p105 | "IMPROVING · 4 d · -3.0%"; gauge labels Very strong…Very weak; hint "OFF52W"; footer "RRG shows…"; chip "momentum rising"/"strong + rising" with Δmom ≥ 0.15; prompt "Daily RRG" | "Underperforming · recovering · 4 bars in state · 3.0% below 52W high"; "Well above 1y norm…Well below 1y norm"; hint "52W gap … not JdK RRG"; footer "Relative Trend vs SPY (custom model, not JdK RRG)…"; chips "↗ strengthening"/"↗ recovering (still below SPY)" on raw>±ε & change>+δ; "Daily relative trend vs SPY" | A3/A4: z-labels and z-based chip removed from decisions; chip boundary test rewritten for ε/δ |
| p105 | notes written with reviewed_phase only | also `reviewed_model = 2` | Revisit flag is suppressed for notes recorded under the old model (G) |
| p107 / p109 | Sector row "LEADING · 2 d · -1.2%" + "↗ strong + rising" | "OUTPERFORMING · STRENGTHENING · 2 bars in state · 1.2% below 52W high" + "↗ strengthening" | copy |
| p110 | Copy by phase header "RRG Daily · … · vs SPY"; 4 groups | "Relative Trend vs SPY · Daily · as of … · custom model, not JdK RRG"; 5 groups incl. Neutral vs benchmark | copy + `flat` |
| p112 | badges "SMH · Improving ★", "IGV · Weakening", "XLK · Lagging" | "SMH · Underperforming ↗ ★", "IGV · Outperforming ↘", "XLK · Underperforming ↘" | `SECTOR_QN` |

Colour classes of the sector badge (`hot` = lead/imp, `cold` = weak/lag) are unchanged — only text.
New coverage: `tests/rrg1_check.py` (F1–F8, G migration; H9–H11 in the H commit).

## H commit (card = 3 chips)
| Suite | Old (C commit) | New | Why |
|---|---|---|---|
| p86 / p105 | card text contains the state label ("Outperforming · strengthening" / "Underperforming · recovering") | card text contains the three chips ("Price: Up · Relative: Positive · Momentum: Strengthening" etc.); the 5-state label lives in Details | brief H: card = 3 chips, C's 5 states = internal logic + Details |
| fixtures | — | `rrg1_fixture.py` adds pt/ptEma/ptEmaPrev/ptN/ptLag (pt follows quad sign) | H fields |
Today row (Sectors) keeps the state label — out of scope for the card.

## sectorHot = Outperforming only
`sectorHot`: lead or weak (or ★ followed). `imp` is no longer hot; its badge reads "Recovering" with its own class `rec` (blue).
| Suite | Old | New |
|---|---|---|
| p112 §3.5 | SMH(imp,★) "SMH · Underperforming ↗ ★" hot; IGV(weak) cold; XLE(imp) "… ↗" hot; hot-first = {NVDA, XOMX} | "SMH · Recovering ★" rec (hot-first via ★); IGV hot; "XLE · Recovering" rec; hot-first = {NVDA, MSFT} |
