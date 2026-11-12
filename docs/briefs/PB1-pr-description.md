## PB1 — One Plan board (Planned · Ordered · Holding) + Macro → Flow, Risk → Port

Spec: `docs/briefs/PB1-brief.md` (+ mockups). Not merged — review first.

### What changed
- **Plan tab = one board** (3 columns on Mac ≥ 840 px, segmented control + one column on iPhone). Header: `Plans · N plans · Holding H · risk in use X% / 5%`, chips `All · MMT · COMP · Sat` (remembered per device), existing ＋ button.
- **Cards** reuse the existing tags/pills/`.go` buttons. One action pill per card (Place order › · Filled ✓ · Add-on › · Fix risk › · Complete › · Edit) calling the **existing** handlers (`ln4Place`, `coreBuy1Open`/`coreBuyAddOpen`, forms).
- **Drawer** (Mac right panel 420 px, iPhone full-height bottom sheet, swipe down / Esc / dim closes): LEVELS · ENTRIES (multi-level plans) · THESIS (Sat → CHECKS) · UPDATE LOG · footer (Update levels, primary pill, Cancel order, Close trade). Reason is an inline input, never `window.prompt`.
- **Update log**: new `log[]` on a core card / Sat idea (`{t,k,txt}`, cap 50, written with the same merge write). Old docs without `log` render (synthetic "Plan created" row). No migration.
- **§2b incomplete plans**: "🕓 Waiting for setup (n)" sub-group in Planned (`needs Entry · SL`, `Setup n/3`, `Complete ›`), no Place order, not in Today Act, not `READY - SETUP` in TV1. Core form got a secondary **Save draft** (skips only Entry/SL/size validation). Sat plans are already draft docs.
- **§2c entry levels**: one card per plan; column = any filled → Holding, else ordered → Ordered, else Planned. `Entry x +N lower`, or `Avg · Entries k/n · next level + state`; drawer ENTRIES rows with per-level actions; log `#2 filled @ …`; cancel clears only the working level (`Order cancelled · #2`).
- **Moved (not copied)**: Weekly Impact panel (`wiPanelHtml`, incl. Import JSON / WI2 replace) and a Macro block (regime + Sat asset bias from the active Playbook) → **top of Flow**; Sat "Risk Sat" header (`ln2HeaderHtml`) → Port, plus a Risk panel at the **top of Port** (Risk in use · Week loss · Room · Open plans · COMP/MMT/SAT used/cap bars, amber ≥ 80 %, red > cap) using the same `ps1Model` / `ln4RoomR` / `lossEval`. The old "Port · risk" tiles from LN4 §8 now live in that panel (same `data-ln4-pt` hooks). "Plan › Sat" Weekly Impact text/links → "Flow › Weekly Impact".
- **Today Act** is built from the board (`bdActRows`): ⚠️ Fix risk → 🛡️ Add-on → 📝 < 2 % → 📌 Filled ✓; max 5 + `+N more ›` → Plan. **No "Raise stop" pill anymore.**
- **New plan popup**: existing ＋ or key **N** on any tab → S Momentum · D Compounder · F Satellite (↑↓/Enter/Esc, pre-highlight from chip). Core forms open as the existing sheet on top of the current tab; save → toast `Plan saved · View in Plan ›`, stay on tab. Watch "Plan ›" (ticker known) skips the popup.
- **Journal**: a fully closed trade carries `thesis` (① + ④) and `log`, shown as `log N entries ›` under the trade.
- **SW2**: Plan content swipe now switches Planned/Ordered/Holding (hint "Swipe ← → to switch Planned / Ordered / Holding").

### §2 field mapping (status is derived, never stored)
| Board status | Core card (`coreCardsList`) | Sat idea (`satIdeasList`, v3) |
|---|---|---|
| 📝 Planned | `status:'plan'`, no `ln4.placedAt` | `satV3PlanRowState` = draft/plan, no `ln4.placedAt` |
| 📌 Ordered | `ln4.placedAt` set, nothing filled | `ln4.placedAt` set, nothing filled |
| ✅ Holding | `coreView().kind === 'open'` (any lot) | `satV3PlanRowState === 'open'` |
| Closed / Missed | `status:'closed'`, `ln4.valid[id].missed` → Journal | `closed`/`ln4.valid[id].missed` |
| Hidden | `c.archived === true` | — |
Levels: `plan.ps1.rows[]` (planned levels) vs `lots[]` (filled). Incomplete = no `plan.entry`/`plan.stop` (core) or no `entry`/`sl`, `setup_ck` < 3, or Verify missing (Sat). Family tag = account id/name matches /fam/.

### Decisions / deviations (please check)
- **Brief file on disk has no §2c / "Filled ✓" text** — implemented from the chat messages ("Filled ✓" everywhere, entry levels use `plan.ps1.rows` + `lots`). There is no per-level order flag in storage, so "ordered" for the *next* level uses the card-level `ln4.placedAt`; cancel therefore clears that flag.
- **No Sat price feed exists** → Sat cards show `— to entry` / `— R`; a clean Sat plan with unknown price gets a plain (not green) `Place order ›`.
- **Sat forms** have no overlay container (they are inline in the Plan tab). "Sat assets ›" (header) and `F` open the existing Sat view as an editor page with a `‹ Plan board` bar (`setPlanScope('future')` still works for old deep links). Core forms were already sheets.
- `plan` keys S/D/F (old scope shortcuts) removed; `[`/`]` now cycles the chips.
- Macro block uses the regime verdict + Playbook stance per Sat asset (the per-asset "Quarterly Macro" text stays inside the Sat form tiles — that is the "Sat form macro line").
- Risk panel renders only when PS1 is on (same condition as the old LN4 Port tiles).

### Tests
New: `tests/run_tests_phase373.py` (390 / 1280 / 1440 + iPhone swipe, §11 items 1–14 + §2b/§2c) — **235 checks, all pass**. Screenshots: `tests/pb1_shots.py` → `tests/screenshots/pb1-*.png`.
Rerun (all green except pre-existing failures that also fail on `origin/main`): 59 ✓ · 106 ✓ · 367 (2 pre-existing: "3 stale → 2 shown + '+1'") · 368 TV1 ✓ · 369 LN4 ✓ · 370 ✓ · 371 LN4b (2 pre-existing HOT-count/order failures) · 372 ✓ · MS1 ✓ · HT1 ✓ · SW2 ✓ · 100 (WI2) ✓ · `tests/ui_audit.py` (see below).
Old tests updated for the new layout: `run_tests_phase369.py` (Act rows now board-driven; no Raise-stop; Plan strips → board cards; "Record fill" → "Filled ✓"), `run_tests_phase371.py` (fixtures near entry + setup ✓; Act squeeze test stubs `bdActRows`), `run_tests_phase_sw2.py` (Plan swipe = status segments), `run_tests_phase100.py` (Weekly Impact on Flow), `ui_audit.py` (board / drawer / popup screens).

### Review-fix round
- **One extra stored field besides `log[]`: `ln4.placedLv = {levelIndex: ISO}`** (core cards). Several levels can be Ordered at once; Filled ✓ / Cancel are per level. Legacy `ln4.placedAt` is still read and treated as the first unfilled level; it is cleared when that level is filled. Flags for filled levels are ignored.
- Popup Momentum row fixed (the `.sel` class collided with LN4's Find selector → renamed `bd-sel`).
- Core | Sat switch removed from the top bar; "Sat assets ›" kept.
- Holding row 3 is one line: R · one state (add-on ready > `Entries k/n · next px [· ordered]` > 0 risk); "stop below avg" removed; size text only when no Entries text.
- Port Risk tiles: 4 in a row on Mac, 2×2 on iPhone. "Risk in use" (ps1: open positions, principal at stop, home account) and the legacy "Open Risk รวม" (all accounts, cost-to-SL) measure different things, so both stay and are labelled `Risk in use (open · home acct)` / `Open Risk รวม (all accts · to SL)`. Neither includes planned orders.
- Sat editor screenshots via F from Today: `tests/screenshots/pb1-sat-editor-{390,1440}.png`.
