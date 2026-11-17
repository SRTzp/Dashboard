# PV1b — A0 progress (17 Nov 2026) — STOPPED: Momentum 2nd target missing

Base: origin/main f4c029e (contains PV1 #51). Branch `claude/pv1b`.

## Leg fields found (index.html, read-only check)

| Kind | Entries (≤2) | Exits (≤2) | Filled / hit record |
|---|---|---|---|
| **Satellite** (idea) | `idea.entry`, `idea.entry2` (+ `e2on`, `e2share`) — `satE2On` / `satE2Avg` | `idea.tp` = TP1; TP2 derived by `satV2Tps` (Tactical only; Main has one TP). Placed trade copies `tp`, `tp2` (`satTpTxt`) | Entry 1 fill = trade row; entry 2 stays `trade.entry2Plan` until filled. Partial exit = a closed trade row (`status:'closed'`, `exitPrice`, `qty`); no explicit "TP1 hit" flag — only derivable from the closed rows |
| **Momentum** (Core card, `winner` track) | `plan.ps1.rows[]` {px, qty} (any count) · filled = `lots[]` · placed = `ln4.placedLv` | **ONE target only:** `plan.tp \|\| plan.target`. **No `tp2` / second target anywhere on the card** | Entries: `lots.length` = filled count. Exits: closed trade rows via `trade_id`; no record of which target was hit |
| **Compounder** (Core card, `ladder`) | `plan.ps1.rows[]`, `lots[]` | single `plan.tp` | same as Momentum |

## Blocker (per brief: stop and report)
- **Momentum cannot hold 2 exits.** There is no second-target field on the plan (`plan.tp2` / `ps1.targets` do not exist; grep finds none). Card spec "≤2 out" for Momentum needs a new field → **not added without approval**.
- No "which exit leg was hit" marker for Satellite / Momentum. Chips could infer "hit" from closed trade rows (qty/price match) but that is a guess, not a stored fact.

## Decision needed from SRTp
1. Approve a new optional Momentum field (e.g. `plan.tp2`, with its qty share), **or** limit Momentum to 1 exit leg in PV1b.
2. For ✓ filled/hit chips on exits: OK to infer from closed trade rows (display only), or add an explicit marker?

Satellite (2 in / 2 out on Tactical) and the Blocked-reasons work (B: `satV2PlanCalc` exposes `carryBlock`, `unpickBlock`, `noteBlock`, `newsBlock`, `rrBlock`, `blocks`, `lotMsg`; root cause confirmed in `pvSatFail`, index.html:29264) are unaffected and can proceed once you answer.

No code changed. Commits A/B/C not started.
