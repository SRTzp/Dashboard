## RRG1 — Relative Trend vs SPY (replaces z-score quadrant)

Brief: `docs/briefs/RRG1-brief.md` · Audit: `docs/briefs/RRG1-audit.md`. **Draft — not merged.**

### What changed
**C–G (commit 828c529)**
- State now comes from the raw EMA12/26 spread of close/SPY and its raw change (lag D5 / W4), not from z-scores. 5 states: `lead` Outperforming·strengthening, `weak` Outperforming·fading, `imp` Underperforming·recovering, `lag` Underperforming·worsening, **`flat`** Neutral (±ε). Internal keys unchanged + `flat`.
- ε, δ = 0.10 × SD of raw / raw-change over the z window (D 252 / W 52). z-scores kept only as "vs own 1y history" context (gauges relabelled "Above/Below 1y norm").
- `sdChip`, breadth, sector badges, sort, Copy-by-phase, transitions, Sector Drivers phases all read the same state; `flat` handled everywhere (5th "Neutral vs SPY" strip under the 2×2).
- Freshness: `lastBar` stored; fresh = fetched today **and** last market bar ≤ 4 calendar days. Asset/SPY end dates captured *before* the date intersection — mismatch ⇒ row not classified.
- Weekly: classified on the last **completed** week (dated by its last real session); partial week kept as a preview in Details / status bar.
- Card: "N bars in state", "X% below 52W high"; Details panel (benchmark, TF, bars, last obs/close both series, raw trend/change, z context, state + ε/δ, freshness, custom-model note). "RRG" wording replaced; "custom model, not JdK RRG" footnotes.
- Migration: `RRG_BUILD 7`, `model 2`. Raw prices aren't cached, so old results are **kept as explicitly outdated** and refetched (24 calls = 3 batches of 8, existing cooldown). If the fetch fails they stay outdated (never stamped migrated/fresh). Notes recorded under the old model are re-baselined once after a successful refetch (`reviewed_model`, `model_updated`) — no fake "Revisit · phase changed", no transition burst (prevQuad is computed within the same model).

**H (commit 5c238a8, separate)** — card shows 3 separate chips + price date: **Price** Up/Down/Mixed (D: close vs EMA50, slope 5 bars; W: EMA40, slope 4 bars), **Relative** Positive/Negative/Neutral, **Momentum** Strengthening/Weakening. Price trend never feeds the relative state. The 5-state label, EMA value/slope and close used are in Details.

### Hysteresis variants (F5, near-zero oscillation, flips over last 252 bars)
| variant | flips | Neutral bars |
|---|---|---|
| none (table verbatim) | 43 | 13 |
| `opp` (leave only at the opposite ∓ε/∓δ) | 32 | **0** |
| **`zero` (leave when raw crosses 0 / change crosses 0) — chosen** | 40 | 8 |

Per scenario flips (none/opp/zero): F1 0/0/0 · F2 1/1/1 · F3 1/1/1 · F4 0/1/1.
**Why `zero`:** `opp` cuts flips most but makes Neutral practically unreachable after start (pos→neg jumps over the dead band), which defeats the `flat` state. `zero` keeps Neutral reachable and still flips less than no hysteresis — but the gain is modest (−7%) on this adversarial two-sine series; honest caveat. One constant (`RRG_HYST`) to change if you prefer `opp`.

### Tests
- New `tests/rrg1_check.py`: F1–F8, G (old-model/outdated, failed refetch, re-baseline), H9–H11 + rule/independence/DOM — **26/26**.
- Existing suites updated for intended changes and logged in `tests/RRG1_retired.md` (p8, 11, 12, 14, 19, 86, 88, 90, 94, 105, 107, 109, 110, 112, `run_tests.py` green; legacy fixtures go through `tests/rrg1_fixture.py`). I did **not** run the whole phase1–113 sweep, only suites that touch this area.
- Screenshots: `tests/screenshots/rrg1-card-details-390.png`, `…-1440.png` (card + Details, synthetic series through the real `rrgCompute`).

### Things to know
- Real-data validation (PAVE vs the TradingView indicator, B1–B3 in the brief) is **not** done — it needs live prices; Details now makes it checkable per card.
- Daily bars: "last bar" is taken as given from Twelve Data; no intraday-partial-day handling.
- `sectorHot` still treats `imp` (underperforming·recovering) as "hot" — unchanged trading rule, only badge text changed.
- Old-model rows seen before refresh show the new labels with "(old model)" and a status-bar "Outdated model" notice.

### Full suite vs main (`tests/runall2.sh`: run_tests.py + phases 1–113 = 114 suites, 2 workers, failures re-run singly)
Run after the `sectorHot` commit, branch `claude/rrg1` vs a clean `origin/main` worktree.

| | suites ok | suites failing | PASS lines |
|---|---|---|---|
| `claude/rrg1` | 100 / 114 | 14 | 11,770 |
| `main` (worktree) | 83 / 114 | 31 | 10,282 |

- **No suite fails on the branch that passes on main.** The 14 branch failures (p5, 13, 23, 41, 42, 43, 44, 45, 46, 47, 66, 75, 80, 81) all also fail on main, and where both ran to completion the FAIL counts match (p5 3, p23 1, p41 2, p42 2, p44 2, p45 1, p46 2, p75 2, p80 2, p81 4).
- Their causes are unrelated to RRG: missing git-ignored backup files/dirs (`index.backup-pre-UI1.html`, `tests/_bk_*`), `sync_core_size.py`, and Plan/Tactical lot/risk checks (p80/p81) — pre-existing.
- The extra 17 main-only failures are an artifact of the clean worktree: git-ignored files (`index.backup-pre-*.html`, `tests/_extracted.js`, `_to_delete/…`) don't exist there, so those suites crash on `ERR_FILE_NOT_FOUND`/`FileNotFoundError` (e.g. p14, 16, 22, 25, 40, 58, 108, 110). So `main` is a noisy baseline; the comparison that matters is the superset relation above.
- Known false failures per runall2.sh (p13 always) show up as expected.
