# PV1b — summary (17 Nov 2026)

Branch `claude/pv1b` (from origin/main f4c029e, contains PV1 #51). Commits: A0 check → A cards → B blocked reasons → C tests / report.

## A0 findings — leg fields per kind
| Kind | Entries | Exits | Fill / hit record |
|---|---|---|---|
| Satellite | `entry`, `entry2` (Main only, `e2on`, `e2share`) | `tp` = TP1; TP2 derived (`satV2Tps`, Tactical only, split by Settings TP1 %) | filled entries = trade tranches; exits taken = closed trade rows |
| Momentum (Core, winner) | `plan.ps1.rows[]`, fills = `lots[]` | `plan.tp` (one target) → **new optional `plan.tp2` + `plan.tp1Qty`** (approved) | exits taken = closed trade rows; no "target hit" marker, none inferred |
| Compounder (Core, ladder) | same as Momentum | single `plan.tp` | same |

Sat shapes possible: 1/1, 2/1 (Main + entry 2), 1/2 (Tactical). Momentum: 1–N entries (rows) / 1–2 exits. 2/2 is only possible on Momentum.

## What changed
- **Cards** (`pvCardHtml`, `pvMoneyLine`, `pvLegChip`): 3 lines + optional Blocked line. Who (symbol · tag · Long/Short word · state · `Place ›`/add-on/filled · ✕) · Money · Orders chips. Planned: `Stop · Risk · Reward · nR`. Holding Sat/Momentum: `Stop (↑/↓ if moved) · Held · If stopped (red / green / ±0) · Banked (only after an exit)`. Holding Compounder: `Stop · If stopped · Value % · P&L`. Missing input is words (`not sized`, `no target`), never 0.
- **Orders chips**: entries then exits; `Buy|Sell price × qty` (Short reversed); dashed = to place; grey ✓ = filled / actual exit. Exits taken come from real closed trade rows (price × qty); remaining targets are dashed with the remaining open qty. No inference of which target was hit; an open position always keeps at least its last target.
- **More** = tap card (keyboard Enter / Space, `aria-expanded`), state kept in `pvMoreOpen` across re-renders. Rows: avg · price, Momentum unrealised P&L, cost + FX line, entry→stop, price→stop, R (+ R per target), whole-plan risk, % of pool, size limits, FX source. `Edit` opens the drawer.
- **Removed from cards**: six-box grid, "not sized" pair, To entry / no live price (Sat and Momentum), "Fix the plan to get a size", the stray "full"/"¼ in" labels, separate More / Edit rows. Waiting (incomplete) plans keep the compact card.
- **pos-view.js** (display only): `initialStop`, `reward`, `rewardR`, `banked` (inputs `targets`, `exits`). Synced into index.html.
- **Momentum fields**: optional Target 1 / Target 2 / Shares at target 1 on the Core plan form (`plan.tp`, `plan.tp2`, `plan.tp1Qty`; validated: tp2 needs tp1Qty and vice versa, tp2 > tp1 > entry). Blank = single target. Not read by sizing, risk, gates or limits. No migration.
- **Last price**: hidden in the Sat form, card and drawer. Stored `lastPx` untouched (still read as the display price for value / P&L).

## Blocked reasons (B) — `pvSatBlockOf`, first match wins
| Order | Source | Card text | Button (action reused) |
|---|---|---|---|
| 0 | trend rule | its own text (e.g. Not an MSS) | none |
| 1 | `carryBlock` | Carried from last week | Use this week › (`satV3CarryConfirm`) |
| 2 | `unpickBlock` | Not picked this week | Add to week › (`satWeekPickAdd`) |
| 3 | `noteBlock` | Needs a reason (against Macro) | Add note › (opens the plan) — note: `needNote` is currently hard-off in code, so this never fires today |
| 4 | `newsBlock` | News window · until HH:MM ICT | none |
| 5 | min stop / Settings msg | e.g. Set min stop in Settings | Open Settings › |
| 6 | stop-distance msg | its own text | Fix stop › |
| 7 | engine reasons (`re1SatBlocks`, R:R, other warns) | first reason text | none |
| 8 | no lot | sizing message | Fix size › |
Root cause fixed in `pvSatFail`: a lot existed but the plan was not ready → "Size not available". Now the real blocker shows, and the real size / risk stay on the card.

**Behaviour change to be aware of:** `re2ReadyToggle` uses `pvBlock`, so a Sat plan that cannot be placed (e.g. not picked this week, min stop unset) can no longer be flagged ⚑ Ready (the brief's "cannot be set while blocked", now applied to every real blocker, not only fix / disabled pills).

## Fields missing / not done
- Momentum 2nd target did not exist → added (approved).
- "Pilot / total-risk room" row (Compounder More): no stored source on the card (it comes from a live sizing call) → not shown.
- Satellite 2/2 is not a possible shape (entry 2 is Main-only, TP2 is Tactical-only).

## Tests
- New `tests/run_tests_pv1b.py` — 123 checks × (1440 / 1280 / 390): Sat Planned Long / Short, 2/1, 1/2; Momentum 2/2 with qty split and Reward / R, blank tp2 = single target, form fields and validation; Holding If stopped loss / ±0 / locked gain; Banked only after an exit; exit ✓ chip with real price × qty and dashed remaining target; each Blocked source → text + button + real size; More toggle / stays open / keyboard; Last price hidden but `lastPx` stored; NVDA values equal on card · More · drawer; no overflow; no console errors.
- PV1 tests changed (layout): `run_tests_pv1.py` — Last price field now hidden (3 checks rewritten to use the stored value), card six-number checks → money line, Blocked wording, More details → tap toggle.
- Other suites updated only where the card layout changed: `run_tests_aw1.py` (drawer opened via `bdOpen`, not card tap), `run_tests_re1d.py` (card header class), `run_tests_re1c2.py` (a plan must be placeable to be flagged Ready), `run_tests_phase373.py` (removed "¼ in" / "full" labels, Edit pill now in More, blocked card has no Place button, drawer via `bdOpen`, scroll before header click).
- Regression: failures not worse than base (base fails: phase122 ×2, phase365 ×2, phase366 ×1, phase367 ×1, phase373 ×1, phase_cg1 ×1, phase_ht1 ×2).
- Screenshots (force-added): `pv1b-plan-1440`, `pv1b-plan-390`, `pv1b-blocked-1440`, `pv1b-more-390`.
