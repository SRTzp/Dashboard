# PB1 — One Plan board (status tracker) + move Risk → Port, Macro → Flow (2026-11-11)
Branch `claude/pb1` from origin/main. Overnight run. Mockups: `claude/mockups/plan-board.html` (board + drawer + iPhone) and `claude/mockups/pb1-all.html` (all screens).

## 0. Principles (read first)
- **Keep the existing look and building blocks.** Reuse the current cards, pills, tags (MMT/COMP/SAT, HOT colours per HT1), fonts, spacing tokens, sheets, toasts. The mockups show layout and behaviour, not new CSS. No new colour system.
- **No data loss, no data migration that rewrites old docs.** Status is *derived* from existing plan fields (§2). Only new field: `log[]` on a plan (§4). Old plans without `log` work.
- Plan forms (Core form / Sat form, LN4/LN4b/LN4c/MS1 rules, Verify matrix, Setup row, Starter ¼, 🛡️ min-stop sizing) are **unchanged**.
- Watch, Settings, Fund flow, RRG, HOT logic, Weekly Stock Summary, TV1 export: **unchanged** (TV1 `###HOLD` / `###READY` must still read the same plans).
- Every user-visible action stays one tap (Mac: one click). No new confirm dialogs except the existing ones (Counter-trend at Save, Close trade).

## 1. Plan tab = plans only
Header row: `Plans` · summary `N plans · Holding H · risk in use X% / 5%` (same numbers the old risk panel used) · filter chips `All · MMT · COMP · Sat` · (existing ＋ button, see §9).
- Filter chip choice remembered per device (localStorage, try/catch).
- Remove from Plan: risk panel(s) → Port (§6); Macro + Weekly Impact → Flow (§5); the Core | Sat switch and separate Core/Sat sections → replaced by chips.
- Body: 3 columns (Mac ≥ 900px): **📝 Planned · 📌 Ordered · ✅ Holding**, each with a count. Empty column → "Nothing here".
- Sort inside a column: Planned = closest to entry first (abs % to entry); Ordered = closest to entry first; Holding = needs-action first (warn/add-on), then R desc.

## 2. Status mapping (derive, don't store)
Map from the current plan model (find the real field names; document them in the PR):
- **Planned** = active plan, no working order, nothing filled.
- **Ordered** = LN4 "Order working" state, nothing filled yet.
- **Holding** = any row executed (starter or full). Split plans (25/75) are one card; show `¼ in` / `full` small text.
- **Closed** = closed/exited → not on the board; goes to Journal (§7).
- Missed (LN4 Exec/Missed) → treat as Closed-missed (Journal, no P&L).
- Archived plans: not shown.

## 2b. Incomplete plans (draft) — e.g. XAUUSD saved, waiting for setup, no Entry yet
- A plan is **Incomplete** when any of: no Entry, no SL, or (Sat/Core forms with the LN4 Setup row) Setup not all ✓ (In Zone · MMT Neutral · Pivot align MA).
- Saving an incomplete plan must be allowed. If the existing form blocks Save without Entry/SL, add a secondary **"Save draft"** button that skips only Entry/SL/size validation (all other rules unchanged). Normal Save keeps current validation.
- Incomplete plans live in the **📝 Planned** column, in a small sub-group at the bottom: `🕓 Waiting for setup (n)`; complete plans sit above as `Ready`. Always expanded (no collapse). Columns stay 3 (iPhone segment count = Ready + setup).
- Card (incomplete): Row 2 shows what's known (e.g. `Zone 2,620–2,640` if a zone/note exists, otherwise `No entry yet`); Row 3 left shows what's missing as small grey text: `needs Entry · SL` or `Setup 1/3`; pill **Complete ›** (plain) → opens the form at the first missing field.
- Incomplete plans: **no risk counted** (summary line, Port risk), **no "Place order"**, **not in Today Act**, not in TV1 `###READY - SETUP` (keep in plain `###READY` if they were there before — TV1 output must stay identical for complete plans).
- When the last missing item is filled and saved → card moves to Ready automatically; log `Plan completed · Entry x · SL y`.
- Tests: save draft without Entry → card in "Waiting for setup" with `needs Entry · SL`; risk unchanged; Complete › opens form at Entry; fill + save → moves to Ready + log; Setup 1/3 shown for a Sat plan with entry but partial setup.

## 2c. Multiple entry levels (MMT starter + add-on, COMP ladder 2–3+ levels) — one card per plan
- Use the existing multi-entry model (LN4 split rows 25/75, ladder, add-on rows — find the real fields; document in the PR). Do not change how levels are stored.
- **Card column = overall state:** any level filled → ✅ Holding; else any level ordered → 📌 Ordered; else 📝 Planned.
- **Card, Planned/Ordered:** Row 2 = first (highest) entry + `+N lower` grey (e.g. `Entry 341.20 +2 lower · SL 326.00`). `% to entry` = to the **nearest unfilled** level.
- **Card, Holding:** Row 2 = `Avg` (filled-size-weighted average, same calc the app uses now) · SL · `Entries k/n`. Row 3 = R + next unfilled level and its state (`next 378.00 · ordered` / `add-on 176.00 · planned`).
- **Pill (Holding with unfilled levels):** next level Planned and < 2% away → `Place order ›` (that level); next level Ordered → `Record fill` (that level); MMT add-on keeps the existing add-on rule (`Add-on ›`). Otherwise as §3.
- **Drawer:** new section **ENTRIES** under LEVELS: one row per level `#k · price · size % · ✅ Filled / 📌 Ordered / 📝 Planned`; each unfilled row has its own small action (Place order / Record fill / Cancel order) calling the existing per-row handlers. LEVELS shows `Avg` instead of `Entry` once anything is filled.
- **Log** per level: `#2 order placed 390.00`, `#2 filled 390.00`, `#3 order cancelled`.
- **Cancel order** on one level returns only that level to Planned; the card column follows the overall rule above.
- **Today Act:** a Holding plan whose next level is < 2% away (or ordered) appears with that level's action.
- Risk: existing calculation (planned vs filled levels) unchanged.
- Tests: COMP 3-level plan — all planned → Planned `+2 lower`; #1 ordered → Ordered; #1 filled → Holding `Entries 1/3` + avg; #2 order/fill via drawer rows → log `#2 …`; cancel #3 → stays Holding. MMT starter ¼ filled + add-on planned → Holding `add-on … · planned`, Add-on pill only when rule met.

## 3. Card (one per plan)
Row 1: ticker (bold) · type tag · HOT tag if `hotSectors()` includes its sector · small `Family` tag when the plan's account is Family (no tag = Main).
Row 2: Entry · SL · TP (TP only if set). Use existing price formatter.
Prices: use the price source the app already has for that symbol (stocks and Sat). If none is available → show `—` for % to entry / R. **Do not add a new price feed.**
Row 3 (left): Planned/Ordered → `−1.2% to entry` (green when < 2%, grey otherwise); Holding → `+1.8R` (green/red) + short state text (`add-on ready` green, `0 risk` when SL ≥ avg).
Row 3 (right): **one action pill** = the next step:
| Condition | Pill | Style |
|---|---|---|
| plan breaks a risk cap / sizing rule (existing check) | Fix risk › | amber |
| Planned | Place order › | green when < 2% to entry, else plain `Edit` |
| Ordered | Record fill | plain |
| Holding, add-on rule met (LN4: stop ≥ BE, starter in) | Add-on › | green |
| otherwise | Edit | plain |
Pill actions call the **existing** handlers (place order → Order working; record fill → existing Exec flow incl. split row; add-on → existing add-on flow; Fix risk / Edit → existing form). Each status change appends to `log` (§4).
Card tap (not on pill) → drawer (§4). Cards are not draggable (status changes only via actions — avoids accidental moves).

## 4. Drawer (Mac: right panel ≈ 420px over a dim; iPhone: full-height bottom sheet, swipe down closes; Esc / dim click closes)
- Header: ticker · tags · current status as one small pill (`📝 Planned` / `📌 Ordered` / `✅ Holding`) · ✕. No step bar.
- LEVELS: Entry · SL · (TP) · To entry / P&L in R.
- THESIS: ① Why buy / ④ Wrong if — read from the existing thesis source for that ticker (Watchlist thesis / living-thesis@1 fields; COMP uses ① + ④, MMT may have only ④). Missing → small "Add thesis ›" link to the existing editor. Read-only here (bordered read card, same as current thesis card).
  **Sat plans** have no thesis and no note field (don't add one). Instead show **CHECKS** (read-only, from the saved checkbox state of the Sat form): `Trend: EMA50 ✓/✗ · Structure ✓/✗ → 100% / 60% / Counter trend` and `Setup: In Zone ✓/✗ · MMT Neutral ✓/✗ · Pivot align MA ✓/✗`. Tap → opens the Sat form (to tick the rest).
- UPDATE LOG (newest first): `dd Mon · text`. Auto entries: created, order placed, filled (price, ¼/full), add-on, SL change `SL a → b`, entry change `Entry a → b`, closed. 
- Footer: `Update levels` (opens existing form; on save, if Entry/SL/TP changed, ask one optional line "Reason?" in a small inline input, not window.prompt; appended to the log entry) + primary = same as the card pill; Holding with no pending action → `Close trade` (existing close flow).
- **Ordered → secondary `Cancel order`** (no confirm): status back to Planned (clear the LN4 Order working flag via the existing path), log `Order cancelled` (+ optional reason, same inline input).
- `log` = array of `{t: ISO date, k: 'create'|'order'|'cancel'|'fill'|'addon'|'sl'|'entry'|'tp'|'close'|'note', txt}`; cap 50 entries (drop oldest). Write with the same save path as the plan (Firestore merge), never overwrite other fields.

## 5. Flow ← Macro + Weekly Impact
Move (not copy) the Macro block (regime + Sat asset bias) and Weekly Impact (incl. Import JSON, WI2 full-replace behaviour) to the **top of Flow**, above Fund flow/RS and RRG. Same components, same data. Today's "Events today" and the Sat form's small macro line keep reading the same data (unchanged).
Update any "go to Plan › Sat › Weekly Impact" text/links (incl. GUIDE text in-app, toasts, the weekly-impact skill's paste hint if referenced in code) → "Flow › Weekly Impact".

## 6. Port ← Risk
Move the risk panel(s) to the **top of Port**: Risk in use X%/5% (bar) · Week loss (R) · Room (5R − week loss) · Open plans; then one row per bucket COMP / MMT / SAT `used / cap` with a bar (caps from existing rules: 3% / 1.5% / 0.5%). Amber bar ≥ 80% of cap, red > cap. Same calculations as today — move, don't rewrite.
Today's top line (`Risk-ON · risk … · room …`) unchanged.

## 7. Journal
Closing from the drawer uses the existing close flow; the Journal entry gets `thesis` snapshot (① + ④ text at close time) and the `log` attached, shown collapsed under the trade (`log 4 entries ›`). Existing Journal unchanged otherwise.

## 8. Today — Act card follows the board
Keep the existing Act card (no new card). Its rows come from the same board items, sorted by urgency: ⚠️ Fix risk → 🛡️ Add-on → 📝 Planned < 2% to entry → 📌 Ordered (check fill). Max 5 rows + `+N more ›` → Plan tab. Each row = type tag · ticker · short reason · the same action pill as the card. Nothing to do → existing empty state.

## 9. New plan = existing ＋ button + shortcut N → popup from ANY tab
- No new "＋ New plan" button: keep the **existing ＋ button** (same place/style). Remove any duplicate.
- **Global:** ＋ or key **N** works on every tab (Today, Flow, Watch, Plan, Journal, Port) → **small popup** (not a new page, no tab switch): centred on Mac, bottom sheet on iPhone; the current tab stays visible behind a dim. N is ignored while typing in an input/textarea/select or when another sheet/popup is open.
- Popup: 3 options in this order, each with its key and a one-line rule hint:
  - **S** · Momentum (Stock) — MMT · `0.35–0.50% · stop ≥ 4%`
  - **D** · Compounder — COMP · `0.80–1.25% · stop ≥ 7%`
  - **F** · Satellite (Future) — SAT · `XAU · BTC · S50 · Brent · 0.10–0.25%`
  Keys S / D / F pick (only while the popup is open, so no clash with other shortcuts), ↑↓ + Enter, Esc / dim click closes. Show the key letter as a small badge on each option.
- On the Plan tab with a chip MMT/COMP/Sat active → that option is pre-highlighted (Enter = go).
- Pick → opens the **existing form exactly as it opens today** (same container/size), type set, on top of the current tab. Save → stay on the current tab, toast "Plan saved · View in Plan ›". Cancel → back to where you were.
- From Watch "Plan ›": type known → skip the popup.
- iPhone bottom bar stays 6 tabs — nothing added.
- Tests: ＋ and N open the popup on all 6 tabs without switching tab; N ignored in inputs; S/D/F/Enter/Esc work; S/D/F do nothing when the popup is closed; preselect follows chip; save toast + stays on tab; Watch "Plan ›" skips it.

## 10. iPhone (≤ 560px)
- Plan: chips (horizontal scroll, nowrap) + segmented control `📝 n | 📌 n | ✅ n` → one column at a time; last segment remembered per device.
- **SW2 update:** content swipe on Plan now switches the status segment (left → next, right → previous, no wrap) instead of Core|Sat. All SW2 gesture rules unchanged. First-use hint text: "Swipe ← → to switch Planned / Ordered / Holding".
- Drawer = bottom sheet. Today/Flow/Port stack as now.
- Tablet 560–900px: 3 columns if each ≥ 260px, else iPhone layout.

## 11. Tests (new `tests/run_tests_phase3xx.py`, 390 + 1280 + 1440)
1. Status mapping: fixture plans (plain / order working / starter filled / full filled / missed / closed / archived) land in the right column or Journal.
2. Chips filter all three columns + summary line; choice persists after reload.
3. Each pill: Place order → card moves to 📌 + log entry; Record fill → ✅ + log; Cancel order (drawer) → back to 📝 + log `Order cancelled`; SL edit save → log `SL a → b`; Add-on visible only when rule met; Fix risk shown for an over-cap plan.
4. Drawer opens on card tap (not pill), shows status pill/levels/thesis (Sat → CHECKS from saved checkboxes)/log newest first, Esc + dim close; iPhone sheet swipe-down closes.
5. Update levels with reason → log text includes reason; without reason → still logged.
6. Old plan without `log` renders; log capped at 50.
7. Macro + Weekly Impact present on Flow, absent on Plan; Import JSON still works (WI2 replace test reused). Sat form macro line still shows.
8. Risk panel on Port with the same numbers as before (compare against the old function output on fixtures); absent on Plan; Plan summary line matches.
9. Today Act order follows §8; `+N more ›` goes to Plan.
10. New-plan popup tests as listed in §9.
11. TV1 export output identical before/after on fixtures.
12. SW2: Plan content swipe switches status segments; bottom-bar swipe still switches tabs; ignored zones unchanged.
13. Close trade → Journal entry with thesis snapshot + log.
14. Family tag shows only for Family-account plans; symbol without a price → `—`, no errors.
Rerun: 59, 106, 367, 369, 370, SW2 suite, LN4/LN4b/LN4c/MS1/HT1/TV1/WI2 suites, then `tests/ui_audit.py` → 0 issues at 390/1280/1440. Fix anything that breaks; if an old test asserts the old Plan layout (Core|Sat switch, risk on Plan, Macro on Plan), update that test and list it in the PR.

## 12. Deliver
Commit after each part (1–3 board, 4 drawer+log, 5–6 moves, 7–9, 10, tests). Push after each commit. PR description: field mapping used for §2, list of moved components, updated old tests, screenshots 390/1440 of Plan, drawer, Flow top, Port top, Today. Compare URL at the end. Don't merge.
