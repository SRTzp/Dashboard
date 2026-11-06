# RRG1 — Audit (main @ 4e… , line numbers = current index.html)

## A1–A9 on main
| # | Claim | Result | Where |
|---|---|---|---|
| A1 | quadrant uses z only (`ratio>=100`, `mom>=100`) | **Confirmed** | `rrgQuadOf` 22978; called from `rrgCompute` 23017/23022/23032 |
| A2 | mom `>=100` ≠ raw change > 0 | **Confirmed** (`momRaw` z-scored, 23006–23012) | `rrgCompute` |
| A3 | sdChip "strong + rising" = lead & dMom≥0.15 (z units), no raw/price check | **Confirmed** | `sdChip` 23306 (brief says ~23278) |
| A4 | "Strong/แข็ง" from z | **Confirmed** | `rrgLevel` 23209 → `rrgGaugeHtml` 23231 (thresholds on `v-100`) |
| A5 | breadth uses `rsTrend>0`, quadrant doesn't | **Confirmed** | `ffRenderThemes` 23700–23701 vs quad |
| A6 | `rrgCacheFresh` = fetched today only | **Confirmed** | 23043; no lastBarDate stored anywhere |
| A7 | `rrgToWeekly` includes partial week, keyed by Monday, last obs date lost | **Confirmed** | 22968; row `date` for W = Monday key (23156) |
| A8 | "4 d" = bars in quad; "−12.0%" = close vs max HIGH 252D/52W, unlabelled | **Confirmed** | `days` 23019–23025; `hi52` 23035; rendered 23511, 23599, 23752 (bare `x.off52.toFixed(1)%`) |
| A9 | custom EMA12/26 model | **Confirmed** | `RRG_CFG` |

Extra findings relevant to the build
- **Raw prices are NOT cached** (only results; comment at 23147: "ไม่เก็บราคาดิบ… Firestore บวม"). So G's "recompute from cached prices if stored" → not possible; migration = **refetch** (existing build check 22824 already clears `day`; 24 symbols = 3 batches ≈ 2 min, 25 credits). Alternative to avoid refetch: none, new fields (raw, ε, δ, lastBarDate) can't be derived from old rows.
- Daily row `date` = last date common to asset+benchmark (23142). So mismatched end dates are silently *hidden* by the intersection today; D's "mismatched → don't classify" needs the per-series last dates captured **before** intersecting.
- Twelve Data `datetime` for the current session may be intraday/partial for a still-open day (not handled today). I'll treat "last bar" as given, no intraday logic.
- No raw-price series is stored → H's EMA40w/EMA50d price trend must also be computed at fetch time and stored on the row (a few scalars per row; no Firestore bloat).

## Consumers
**`rrgQuadOf`**: only inside `rrgCompute` (quad, days loop, prevQuad). Will be replaced by a state function with hysteresis (needs history → computed in the bar loop).

**`quad` (row field) / `prevQuad`** — every site must handle new key `flat`:
1. `sectorState` 13600–13606 → `sectorHot` 13609, `sectorBadgeHtml` 13611 (`SECTOR_QN` 13608; `hot` for lead/imp, `cold` weak/lag; `flat` → off/neutral). Watchlist/sector badge surface.
2. `SD_QPH`/`SD_PHL` 23245–23246 → `sdCur` 23297, `sdFlag` 23301 ("Revisit · phase changed"), `sdWrite` 23351 (stores `reviewed_phase`), `sdNorm` 23282 (`SD_PHL[...]` whitelist ⇒ stored `FLAT` would be dropped unless added), `sdPhaseLbl` 23312, line 23376 text ("Daily RRG"), TD4c Today value 23580–23581 (+ `stale` = `r.day !== today`).
3. `sdRowHtml` 23503–23512 + `SD_QLBL` 23516 (Today/Flow row, uses `QLBL[x.quad]`; undefined for `flat` → crash).
4. `rrgSortRows` 23556 (`ORDER` map lacks `flat`) → used by `sdOrderSig` 23325, `rrgCopyText` 23628, row lists 23730.
5. `rrgCopyText` 23634–23636 (hard-coded 4 groups; `flat` rows would vanish from the copy).
6. `ffRenderThemes` 23690 (`ffQ<quad>` boxes — HTML 3634–3637 has only 4 boxes; `flat` needs a box or an explicit "Neutral" bucket), 23712–23752 table (`QLBL[x.quad]`).
7. `ffLeadThemes` 23960 (`quad==='lead'`) → Action bar.
8. `ffChangesData` 23980 (transitions from `prevQuad`→`quad`; `RRG_QUAD_LABEL` 23970 lacks `flat`; **must not burst after migration** → G).
9. Line 7836 (has-data check only; unaffected).
Also text refs "RRG"/"Leading": quadrant subtitles in HTML 3634–3637, `SD_FOOT` 23249, `SD_TAG`, UI string "rrg v6" 23678.

**`dMom`**: produced 23030; consumed by `sdChip` 23306; `rrgGaugeHtml(x.mom, x.dMom)` 23512/23750; sort tie-breakers `rrgSortRows` 23562 and `ffLeadThemes` 23961. Z-unit delta stays valid as *context/sort*, but must not drive state. (`dRatio` similarly in the gauge.)

**`sdChip`**: 2 call sites — 23511 (Flow card) and 23599 (Today row). Rewrite per C.

**`rrgCacheFresh`**: 3 sites — `rrgRefresh` 23114, `rrgAutoOnce` 23177, definition. (`sdCur` uses its own `r.day===today` test, 23294; `rrgBusy`/cooldown logic unaffected.) New freshness = day + lastBarDate ≤4 calendar days; staleness *display* additionally needed in `sdCur`/TD4c.

**`RRG_BUILD`**: 22824 (migration clear), 22938 def, 23159 write, 23678 display.

## Decisions / questions I need OK on
1. **Refetch on migration** (no raw prices cached). OK? (Respects 61 s batch cooldown; one-time.)
2. **Hysteresis default**: I'll test both exits (cross −ε vs cross 0) on scenarios and report flip counts; default pick whichever has fewer flips without lagging the F1/F2 scenarios.
3. **`flat` in the Flow 2×2 grid** (HTML 3634–3637): add a 5th "Neutral vs SPY" box beneath the grid, rather than dropping flat chips. Per brief, card display = section H's 3 chips; the 5-state label lives in Details + sector badge/sort/copy. OK?
4. **Phase keys**: keep `lead/weak/imp/lag` + new `flat` (`FLAT` in `SD_QPH`/`SD_PHL`). Stored `reviewed_phase` values stay valid; add `reviewed_model` = 2 stamp (re-baseline once on first load, no "Revisit" from model change).
5. **Copy language**: new strings English (matches Sector Drivers / Today); the Flow tab's Thai text left alone except the quadrant subtitles and gauge "แข็ง" labels I must change.
6. **Tests**: existing suites touching this: run_tests_phase11/12/86/105 (+ p85). I'll update expectations that are intentionally changed, log them in `tests/RRG1_retired.md`, and add `tests/rrg1_check.py` (+ node harness for F1–F11 synthetic series).
