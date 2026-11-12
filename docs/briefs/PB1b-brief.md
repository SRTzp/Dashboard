# PB1b — Sat plan as a popup, Trend-only form, Strategy → Flow (2026-11-12, rev 3.1 — supersedes rev 2/3)
Same branch `claude/pb1` (on top of PB1). Mockup: `claude/mockups/pb1b-sat-popup.html`.

## 1. New-plan popup = 3 steps, any tab, no page switch
- N / ＋ → step 1 `S Momentum · D Compounder · F Satellite` (as built).
- F → step 2 "which asset?": `1 XAU · 2 BTC · 3 S50 · 4 Brent` (existing Sat asset list; ★ this week's focus first; asset with an open plan → "plan exists → edit" opens that plan).
- 1–4 → step 3 = the Sat form **inside the same popup** (Mac centred ≈ 460px; iPhone bottom sheet, scrolls inside). `‹` / Esc = back one step; ✕ / dim = close. Save → stay on the current tab + toast "Plan saved · View in Plan ›".
- Opening an existing Sat plan (board card "Edit" / "Complete ›" / drawer "Update levels") uses the same popup at step 3.

## 2. Sat form — lean, calm, no clutter
- Order (top → bottom): Buy|Sell · Main|Family → Entry · SL · TP → TREND (EMA50, Structure) → [MSS question if shown] → size box (label + lot · risk $ at SL · R:R) → [amber warning if any] → grey Setup reminder → small macro line → Save draft · Save plan.
- **EMA50 and Structure (higher TF) start UNSELECTED** for new plans; each is a ✓/✗ pair, tap again to unselect.
- Small pill **`hold · all ✓`** at the right end of the Trend row: press-and-hold **0.8 s** (fill animation; release early = nothing) sets EMA50 ✓ + Structure ✓ and clears any MSS answer. Mouse, touch and keyboard (hold Space/Enter when focused). Never triggers on a tap.
- Existing sizing formula + Sat risk rules; multiplier from §3. TP mandatory; min R:R 1.5 blocks (existing); min stop (existing).
- **Side check:** Buy needs SL < Entry < TP; Sell needs SL > Entry > TP → inline red hint, plan stays incomplete.
- **No Setup checkboxes / "✓ all" hold / Range option / MSS price field.** One grey reminder: `ⓘ Setup in TradingView: In Zone · EMA50/HVN converging · Pivot MMT · Trend Neutral`. Old `setup_ck` kept, not used.
- UI: one column, consistent 8/12px spacing, existing tokens; size box never wraps awkwardly (on iPhone the lot/risk line goes under the label); no element wider than the sheet at 390.

## 3. Trend rule (this table wins over anything earlier)
| EMA50 | Structure | Result |
|---|---|---|
| ✓ | ✓ | **Size 100%** |
| ✗ | ✓ | **Size 60%** + amber warning `⚠️ Don't ride the trend far — exit at the nearest key target.` |
| ✓ | ✗ | **MSS question** → Yes = `Counter trend @ MSS · 60%` · No / unanswered = **Blocked** |
| ✗ | ✗ | **MSS question** → Yes = `Reversal @ MSS · 60%` + the same amber warning · No / unanswered = **Blocked** |
- Every reduced size = **60%** (the existing Sat reduced multiplier, one Settings value). No 50%.
- MSS question shows inline as soon as Structure = ✗: **"Is this entry an MSS on the higher TF?"** [Yes] [No]. **Default = nothing selected** (neither button active); blank behaves as Blocked until answered. The entry is the MSS level (no extra field).
- Changing Structure to ✓ (or unselecting) hides the question and **clears the MSS answer** (an old Yes never re-unlocks).
- Yes at planning = intended condition only; it is re-confirmed at Place order (§2b).
- Existing Counter-trend confirm at Save stays for the EMA ✓ / Structure ✗ case.
- Card + drawer + Journal tags: `Counter trend @ MSS`, `Reversal @ MSS`; `nearest target` warning icon on the card for the two warned cases.

## 2b. Place order = one-tap confirm (records only)
- Card pill / drawer / Today Act `Place order ›` → small confirm (same popup style):
  title `Setup ready on Execution TF?` · grey line `In Zone · EMA50/HVN converging · Pivot MMT · Trend Neutral` · for MSS trades an extra line `MSS confirmed per your rules (candle closed)` · summary box `Buy XAUUSD · Main / Entry · SL · TP / label · lot · risk $`.
  Buttons `[Not yet]` `[Yes · mark ordered]` (one tap; Enter = Yes, Esc = Not yet) + tiny note `Records the order in the dashboard only — place it at your broker.`
- Yes → existing place-order state (Ordered) + **per-level snapshot** stored once and never rewritten by later edits: `{t, entry, sl, tp, dir, acct, ema, structure, mss, label, mult, lot, riskPct, riskAmt, macro, setupOk:true}`. Journal shows it on close.
- Not yet → nothing changes. Blocked plans: pill disabled with tooltip `Blocked by trend rule`.

## 3b. States (card, drawer, TV1 use the same function)
- 🕓 Waiting for setup (incomplete) = missing/invalid Entry, SL or TP, wrong side, R:R < 1.5, or Trend not fully chosen (incl. MSS unanswered → shows `needs MSS answer`). Card says what is missing.
- 📝 Planned = complete and not blocked → `Place order ›` allowed. Blocked = complete but rule says Blocked → Planned with red `Blocked` tag, no Place order.
- TV1 Sat `###READY - SETUP` = Planned & not blocked; Core TV1 output identical.

## 4. Strategy page removed from Plan → Flow
- Remove the Sat Strategy page / "Sat assets ›" link / `‹ Plan board` editor bar from Plan.
- Top of Flow, first card **"🌐 Macro · this week's Sat focus"**: week selector, regime, one chip per asset with macro bias; tap chip = ★ focus this week (existing Strategy weekly asset selection data); `＋ Asset` = existing add-asset flow. Then Weekly Impact (as PB1), then Fund flow / RRG.
- Any "go to Strategy / Plan › Sat" links → Flow.

## 5. Also finish PB1 §2c
- Holding card with next unfilled level Planned and < 2% away → pill `Place order ›` (that level).
- `% to entry` = to the nearest unfilled level (all card states).

## Tests (add to phase373, 390/1280/1440)
Popup from all 6 tabs without tab switch; ‹/Esc steps back; ★ first; open plan → edit; Edit/Complete/Update levels open the same form. Trend starts unselected (`needs Trend`); hold · all ✓ sets both ✓ only after 0.8 s (tap does nothing); MSS question starts with no button selected. ✓✓ 100%; ✗✓ 60% + warning; ✓✗ MSS Yes → Counter trend @ MSS 60%, No/blank → Blocked; ✗✗ MSS Yes → Reversal @ MSS 60% + warning, No/blank → Blocked; flip Structure to ✓ clears MSS answer. No Setup checkboxes / Range / MSS price field; reminder present. Side check + R:R 1.5. Blocked saves, Place order disabled. Place order confirm → snapshot stored; editing the plan later leaves the snapshot unchanged; Not yet changes nothing. Flow top weekly focus card (★ toggle, ＋ Asset), Weekly Impact below; Plan has no Strategy page. §2c: Holding next level < 2% → Place order ›; % to nearest unfilled level. Rerun SW2, 368, 369, 370, phase100, ui_audit → 0 (report any suite that is missing or can't run). Screenshots `tests/screenshots/pb1b-*.png`: popup steps 1–3, MSS question (Yes / Blocked), Place-order confirm, Flow top — 1440 and 390. Commit, push, short summary + test results. Don't merge.
