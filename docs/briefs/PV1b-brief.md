# PV1b — compact Plan cards · real Blocked reasons · legs (≤2 in / ≤2 out)

Approved by SRTp 17 Nov 2026. Mockup: `docs/briefs/pv1b-cards.html` (approved as drawn; open first).
Base: latest `origin/main` (contains PV1, #51). Branch: `claude/pv1b`. Commits: A0 check → A cards → B blocked reasons → C tests/report, push each.
RM1 (regime modifier) starts after PV1b is merged.

## Rules
- Display only. No change to sizing, limits, gates, engine. Numbers from `posView` / `pb2Calc` / `satV2PlanCalc` / `plan.ps1` (one source each).
- Missing input → words, never 0 or a bare dash. No data migration, no deletes. `render()` pure. English UI. No overflow 1440 / 1280 / 390.
- SRTp trades Satellite + Momentum as entry / stop / target only (no price tracking). Compounder keeps position numbers.

## A0 · Verify first → `docs/reports/PV1b-progress.md`
- Stored shape of legs: Satellite (`entry`, `entry2`, `tps`, fills / partial exits), Momentum (entries, targets, partial-exit fills), Compounder (`plan.ps1.rows`, lots). Can each kind hold 2 entries and 2 exits, and record which leg is filled / hit?
- If a needed field does not exist (e.g. Momentum 2nd target or partial-exit record): **stop and report** — no new field without approval. Build the rest with the legs that exist.

## A · Card layout (Plan board; same component in the drawer header if reused)
3 lines + optional Blocked line, as in the mockup:
1. **Who:** symbol · port tag · `Long` / `Short` (coloured word) · state (⚑ Ready / red Blocked / amber `50% · homework` chip) · `Place ›` when placeable · ✕ (Planned only).
2. **Money:**
   - Planned (all kinds): `Stop X · Risk −$ · Reward +$ · nR`. Risk = loss if stop hit on all planned entries; Reward = gain at all targets with their quantities; R = Reward ÷ Risk.
   - Holding · Satellite / Momentum: `Stop X ↑ (if moved from the original) · Held q · If stopped ±$ · Banked +$ (only after an exit)`. If stopped = held qty × (stop − avg) × dir × mult × FX; ≥ 0 shown green / ±0.
   - Holding · Compounder: `Stop · If stopped · Value + % of account · P&L`.
3. **Orders:** one chip per leg, in order: entries then exits. Text `Buy|Sell price × qty` (Short: entry = Sell, exit = Buy). Dashed = to place; grey + ✓ = filled / hit. Unused legs hidden. Wraps on narrow cards.
- **More** = tap the card (toggle, stays open across re-renders, keyboard accessible). Content: avg + price (Compounder / Momentum), cost with FX line, price→stop, R per leg + stop distance, whole-plan risk, pilot / total-risk room (Compounder), size limits, FX source, Momentum unrealised P&L. `Edit` inside More.
- Remove from cards: the six-box grid, "not sized" pair, "To entry"/"no live price" for Satellite and Momentum, the "Fix the plan to get a size" helper, the stray "full" label, separate More / Edit rows.
- Satellite manual **Last price**: hide in form, card and drawer; keep stored `lastPx` untouched.
- Waiting (incomplete) plans keep their existing compact card.

## B · Real Blocked reasons
- Root cause: `pvSatFail` reads only the sizing message; when a lot exists but `satV2PlanCalc(...).ready` is false, it writes "Size not available" and hides the size.
- Fix: take the first blocking item from the plan calc, in this order, and show the real size / risk when a lot exists:

| Source | Card text (English) | Button |
|---|---|---|
| `carryBlock` | Carried from last week | `Use this week ›` (existing action) |
| `unpickBlock` | Not picked this week | `Add to week ›` (existing action) |
| `noteBlock` | Needs a reason (against Macro) | `Add note ›` (opens the field) |
| `newsBlock` | News window · until HH:MM ICT | none |
| min-stop / Settings msg | e.g. Set min stop in Settings | `Open Settings ›` |
| stop-distance msg | its own text | `Fix stop ›` |
| engine `blocks` | first `reasonTexts` | none / existing |
| no lot (sizing failed) | sizing message | `Fix size ›` |

- Thai source strings stay in their source; the card maps codes to the English texts above.
- Ready cannot be set while blocked (unchanged).

## Tests / proof
- `tests/run_tests_pv1b.py`: each card kind × Planned / Holding; 1/1, 2/2, 1/2, 2/1 legs incl. Short; filled / hit chips; If stopped sign (loss, ±0, locked gain); Banked only after an exit; each Blocked source → its text + button + real size; More toggle; Last price hidden but `lastPx` still stored; no overflow 1440 / 1280 / 390.
- Values equal between card, More and drawer for one fixture (NVDA: if stopped −฿17.8k, value ฿60.5k · 1.2%).
- Update PV1 tests only where the layout changed (list each). `tests/run_regression.sh` not worse than base.
- Screenshots (`git add -f`): `pv1b-plan-1440`, `pv1b-plan-390`, `pv1b-blocked-1440`, `pv1b-more-390`.

## Report — `docs/reports/PV1b-summary.md`
A0 findings (leg fields per kind) · what changed · each Blocked source and its mapping · fields missing (if any) · tests changed and why.
