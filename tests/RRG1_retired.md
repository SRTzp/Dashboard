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

## RRG1b (claude/rrg1b) — lean card, waiting state, queue
| Suite | Old | New | Why |
|---|---|---|---|
| rrg1_check H | card = 3 chips `Price: Down · Relative: Positive · Momentum: Strengthening` + `to 4 Nov` date chip | card = 2 chips `Beating SPY ↗` + `▼ Down −1.1%`; no momentum chip (arrow in the Relative chip), no date chip (date stays in Details) | brief item 4 replaces section H's 3-chip card |
| rrg1_check H | price-chip tooltip lists EMA rule + timeframe + last price date | tooltip = "Own price vs 50-day EMA (falling) — not compared with SPY"; rule/timeframe/date are in Details | brief item 4 |
| p86 / p105 / p107 / p109 (card/Today text) | "bars in state", 52W gap sentence, "↗ strengthening" sdChip, two 1y-norm gauges visible on the card; Today row "OUTPERFORMING · STRENGTHENING · n bars in state · x% below 52W high" | card/Today = `★ SYM Name` + `[Relative chip][Price chip] −5.9% from 52W high`; bars in state, 52W sentence, gauges + words, Δ legend → Details | item 4 (see full-suite section of the PR for which suites changed) |
| Flow bar | "ดึงราคาไม่สำเร็จ: <raw API text>", "ดึงแล้ว 8/24 · รออีก n วิ" | "Updating prices · batch 2/3 · next in 45 s" / "Price limit reached — retrying in 60 s" / short failure line; raw text → Details › Last fetch error + console | item 1 |
| Flow legend | always-visible hint (Thai + "Δ over the last 5 days … 52W gap … RS gauges …") | collapsed `How to read ›` (4 lines), state in localStorage `rrgLegendOpen` | item 3 |
| `rrgRefresh` | returned undefined; `f.rrg` replaced only after all 3 batches; one cooldown only between batches of one run | returns the running promise (click joins it); each batch merged + persisted on arrival; `pending` list resumes; 61 s window measured from the last request across runs/reloads (`rrgLastBatchAt`); model stamp only when pending is empty | item 1 |
New coverage: `tests/rrg1b_check.py` (31 checks), screenshots via `tests/rrg1b_shots.py`.
