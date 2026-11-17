# EF1 — progress

Base: origin/main `00a36ae` (RM1 + PV1b merged). Branch `claude/ef1`.

## A0 · Tap-count map (from the code, `index.html`; counted as taps after the app is open)

"Tap 1" = opening the card / going to the list that holds the Place button. Target after EF1: **≤ 3 taps = open card → Place › → Confirm**.

### Path code (what a tap does today)
| Step | Code |
|---|---|
| Plan-board / Today Enter pill | `bdPill()` (≈29330) → `ln4Place(kind,id)` (11397) |
| Satellite Place | `pb2PlaceOpen` (30748) → sheet "Setup ready on Execution TF?" (`pb2PlaceHtml`) → `pb2PlaceYes` (30765) |
| Momentum / Compounder Place | `ln4Place` → `wl1PlaceGate` (31292, engine `re1PlanGate`) → **native `confirm('Placed at broker — X?')`** → write `ln4.placedAt` |
| Today › Enter list | `re2Model` (30190): shows plans that are **⚑ Ready (manual)** or ≤ 3 % to entry (core only; Sat has no price → only via ⚑) |
| Manual ⚑ Ready | `re2ReadyToggle` (30261), button `re2ReadyBtn`; refuses if `pvBlock(it)` |

### Gates on the Satellite path (in the order `pvSatBlockOf` ≈29378 checks them)
| Gate | Code | What the user does today | Taps added |
|---|---|---|---|
| Trend / EMA50 + Structure unset | `ln4VerifyOf().unset` → `pb2Model` "needs Trend", `td3PlanStatus` (10750) "needs Trend" / "needs MSS answer", pill `Complete ›` | open form, answer EMA50, Structure (+ MSS), Save | 4–5 |
| MSS = No / blank | `ln4VerifyOf().blocked` → block `trend` | — (stays blocked; kept) | n/a |
| Counter trend confirm | `pb2Save` → `pb2CounterAsk` (30716) | extra "Save as counter trend" tap | +1 |
| `carryBlock` (plan from last week) | `satV3PlanAcctCalc`/`satV2PlanCalc` (24663 / 25236), `pvSatBlockOf` → pill "Use this week ›" → `pvSatAct('carry')` → `satV3CarryConfirm` (23870) | 1 tap, fails if picks full (3) | +1 |
| `unpickBlock` (asset not in `satWeekPickList`) | same; pill "Add to week ›" → `satWeekPickAdd` | 1 tap; full → toast, user must go remove a pick elsewhere | +1 (+n) |
| `noteBlock` (against Macro, no reason) | same; pill "Add note ›" → `td3SatOpen` | open form, type a reason, Save | +3 |
| `newsBlock` (CPI/NFP window, `newsSatBlock` 9164) | same; no button, plan cannot be placed; `pb2Save`/`satV3SaveReadyAccounts` also return | wait for window to end | ∞ (until `to`) |
| Stop / size / lot / heat / total risk / value cap / emergency | `re1BoardGate`, `re1SatBlocks`, `ps1MinStopMsg`, `Calc.readiness` | fix or wait | kept |
| Manual ⚑ Ready | for Today › Enter only | 1 tap on card | +1 (Today path) |

Core (Momentum / Compounder) gates: `inc` (incomplete → Complete ›), `re1BoardGate` → `re1PlanGate`, `bad` stop/risk → Fix ›, `wl1PlaceGate`, `nearEntry` (else the pill is **Edit**, not Place, unless Today Enter `force`), manual ⚑ Ready. No `carryBlock`/`unpickBlock`/`noteBlock`/`newsBlock` apply to them.

### Tap counts (today, clean plan, after the Plan tab is open)
| Plan type | Plan-board path | Today › Enter path |
|---|---|---|
| Satellite main plan | Place order › → sheet Yes = **2** (3 with opening the tab) | ⚑ Ready (card) → Today → Place › → Yes = **4** |
| Satellite carried plan | Use this week › → Place › → Yes = **3** (+1 tab); fails if picks full | + ⚑ = **5** |
| Satellite, asset not picked | Add to week › → Place › → Yes = **3**; full picks: dead end | **5** |
| Satellite, against Macro | Add note › → type → Save → Place › → Yes = **5** | **7** |
| Satellite, verify unanswered | Complete › → EMA50 → Structure (→ MSS) → Save (→ counter confirm) → Place › → Yes = **5–7** | **7–9** |
| Satellite, in CPI/NFP window | blocked, no path | blocked |
| Momentum plan | Place order › (only if ≤ 3 % to entry, else Edit) → native confirm OK = **2** (3 with tab) | ⚑ → Today → Place › → OK = **4** |
| Compounder pilot | same as Momentum = **2** (3 with tab) | **4** |

Counts are derived from reading the handlers (no live run); the EF1 tests (D) re-measure "after" with the real DOM.

### Findings that affect the brief
1. Core (Momentum / Compounder) has **no confirm sheet** today — it uses a native browser `confirm()`. Brief §7 asks the sheet to show legs / stop / targets / Risk / Reward / "limited by" for every plan. For core I will reuse the same popup container (`bdPop`, same as `pb2PlaceHtml`) and render a sheet from the existing level rows (`tw1Lv`, `tw1SizeRisk`, `re1PlanGate`) — no new screen, but it is new content in an existing container.
2. The Sat confirm sheet today is a 4-item checklist ("Setup ready on Execution TF?"). It stays; the new rows are added above it, size working goes under More.
3. Sat items have no live price in `bdItems` (`pct = null`), so Today › Enter only shows Sat via ⚑. With "Ready = automatic" (§4) every complete, unblocked Sat plan would appear in Enter. To keep Enter short I plan to list only Ready plans ≤ 3 % away for core and all Ready Sat plans — **open question** below.
4. The verify answers are already in the Satellite form (`pb2` step 2: `ema`, `str`, `mss`); the "pending" step is `td3PlanStatus` / `pb2Model` / `ln4Fix 'verify'` and the old v3 rows.

## Open questions
- Today › Enter volume once Ready is automatic (see 3).
- Core confirm sheet content (see 1).
