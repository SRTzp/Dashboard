# NT2 — My ideas: Scenarios (Pullback zone / Breakout level) · reasons visible · In plan · flexible width

Status 22 Nov: design approved by SRTp. NT1d is merged → branch from fresh origin/main.
Mockups (commit both first):
- `docs/briefs/nt2/nt2-watch-full.html` — **full page 1440×900, binding for LAYOUT** (list 380 · detail rest; chart keeps its own shape; reasons strip below). Embeds SRTp's real chart as the sample image.
- `docs/briefs/nt2/nt2-scenarios-compare-v3.html` — **binding for CARD CONTENT** (the "Proposed v3" column: ruler, scenario rows, TV row, list rows, Today rows, edit sheet). Its 2-column card layout is superseded by the full-page mockup above.
UIUX lens applies (plain words, no "…" cuts, nothing twice, one dark button per area, amber = to do, red = money lost only, blue = distance, green = good/done, 1440×900 no page scroll).
Single file `index.html`. No new Firestore rule (ideas_my has no field whitelist). No new price feed.

## Objective (SRTp)
A My idea = a big-picture read of the chart, backed by Technical / Sentiment / Fundamental / Macro reasons, set out as 1–2 trade scenarios (max 3). A scenario is a WAY IN, not the invalidation:
- **Pullback** = a zone; price comes back into it (buy the dip / sell the rally).
- **Breakout** = one level; price goes through it. No touch/close options.
- Side comes from My view: Bull → buy scenarios, Bear → sell. No mixing in one idea. If My view is empty/neutral, the Scenarios block shows a `Buy | Sell` toggle (one per idea).
- "Wrong if" = one optional level that kills the whole idea.

## A · Data (ideas_my, all optional; whitelist in `nt1Payload` + parse)
- `scenarios: [{id:'A'|'B'|'C', kind:'pullback'|'breakout', lo, hi, level, note, hitAt}]` — pullback uses `lo`,`hi` (lo < hi); breakout uses `level`. Max 3. Letters follow order; deleting a row re-letters (keep `hitAt` with its row).
- `side: 'buy'|'sell'` — derived from view; stored only when chosen by toggle.
- Keep NT1d fields: `invLevel` (= Wrong if; direction derived: buy → ≤, sell → ≥; also write `invDir` for compatibility), `invHitAt`, `invAckAt`, `lastPx`, `tvAlert`, `planId`, `snoozeTo`, recheck date.
- **Migration (read-time view-model; written only on the next Save; never delete old fields):** old `level` + `levelDir` → A: buy idea & `down` → pullback with lo = hi = level; `up` → breakout. Sell mirrored. `next` text → A.note if ≤ 80 chars, else it stays stored and appears only in the Copy export. Old `hitAt` → A.hitAt. Stored `plan` / `next` are never deleted.

## B · Trigger logic (rewrite `nt1bLevelState` internals; keep the name)
Price = `nt1bLevelPx(m)` (stock → daily close `nt1bPx`; other → `lastPx.v`, typed; > 24h → `old price`). Display + this alert only — never an engine/sizing/gate input.
- Buy pullback hit: px ≤ hi. Buy breakout hit: px ≥ level. Sell pullback (rally zone): px ≥ lo. Sell breakout (breakdown): px ≤ level.
- Wrong: buy px ≤ invLevel, sell px ≥ invLevel.
- Write-once per scenario (`hitAt`) / `invHitAt`, merge write on load when first true; price moving back never clears it. **Wrong wins** over any hit.
- Distance (not hit): buy pullback (px − hi)/px, buy breakout (level − px)/px, mirrored for sell. Near = within `NT1B_NEAR` 3 % for any subject with a price (NT1d rule). |dist| < 0.05 % → text `at level`, never `0.0%`.
- Returns `{state:'wrong'|'hit'|'near'|'none', sc (fired / nearest scenario), px, distPct, src, old, list:[per-scenario {dist, hit}]}`.
- Edit rules: changing a scenario's kind/numbers clears that scenario's `hitAt`; changing invLevel clears `invHitAt` + `invAckAt`; any of these sets `tvAlert=false`. Title/notes edits change nothing (clipboard untouched).

## C · Page layout (full-page mockup)
- **Grid at ≥ 1100px:** list column default **380px**, detail = rest (880 at 1440). Both cards 708 tall at 1440×900. List header chips 12.5px, 4px gap, so All · Due · Markets · Stocks · Sat · Plan + `⌕` fit at 380. Replaces NT1d's 440 + rest.
- **Detail, top to bottom:** header full width (tag · title · view pill · date · Edit · ⋯) → row `1.55fr | 1fr`, `align-items:start`:
  - Left: chart box with the image's OWN aspect ratio (set `aspect-ratio` from naturalWidth/naturalHeight on load; fallback 16:10); never stretched to the right column; `max-height` so the page never scrolls; overlays `⤢ Enlarge` / `TradingView snapshot ↗` unchanged.
  - Right: the Scenarios card only (D).
  - Below the row, full width: **Reasons card** as a 2-column grid; each cell = 44px label column (`TECH` · `SENT` · `FUND` · `MACRO`) + text that wraps. Empty ones not drawn; card hidden if all empty.
  - Footer: `Built on: … ›` · review hint.
  - Detail scrolls inside its card if ever taller than 708.
- No chart → Scenarios card full width on top, reasons below. Phone ≤ 760: chart → Scenarios → Reasons (1 col) → footer.

## D · Scenarios card (card-content mockup, Proposed v3)
- Green = watching: `SCENARIOS · WATCHING` + `Check again 29 Nov` right.
- **Price ruler** (`nt1Ruler(m)` extended): pullback = blue band, breakout = blue tick, Wrong = amber tick, now = dark dot. Scenario labels ABOVE the track (`A 3,290–3,340`, `B 3,500`, blue), `Wrong 3,200` and `now 3,412 manual` BELOW. If two labels on one side are closer than ~30 % of the track, the second moves to the other side. Scale = min/max of all values padded 25 %, clamp 4–96 %. The ruler is the ONLY place the scenario numbers appear in the card.
- One row per scenario: letter chip · **Pullback** / **Breakout** · muted note (wraps, never "…") · right **pill** `2.1% away` (blue pill) or `▼ in zone` / `▲ broke out` (amber pill). Pills are real pills (background + colour), never plain grey text.
- TV row (one line): `● TV  Copy A · Copy B · Copy ✕ · ✓ Set` (one chip per scenario + ✕ when Wrong if is set; one tick covers all → `TV alerts set ✓`). Hint stays a tooltip.
- Actions: `Snooze 3 days · Done` left, `Mark ▾` right → `A reached` · `B reached` · `Idea wrong`.
- **Hit** (a scenario fired): card amber, header `A IN ZONE · 25 Nov 21:42` / `B BROKE OUT · …`; dark `Make plan ›` (stock); non-stock: no dark button (Sat-plan prefill = NT2b) — quiet `Not yet · snooze 3 days`, `Done`.
- **Wrong**: card amber (never red), header `IDEA WRONG · 26 Nov 03:12`, text `price below 3,200`; dark `Drop idea` (drop + Undo toast); quiet `Keep watching · snooze 3 days` (writes `invAckAt` + `snoozeTo`; fires again only after the price leaves and crosses again — keep NT1d behaviour).
- **In plan** (`planId` set and the plan card exists): card green `IN PLAN` + `Open plan ›`; ruler/rows stay visible; no hit/wrong alerts go to Today (the Plan board owns the trade).
- No scenarios → card shows `No scenario yet` + plain `Add scenario ›` (opens the sheet at Scenarios). Not amber.

## E · Edit sheet (card-content mockup §3)
Top unchanged: About · My view · Title · Chart.
- **SCENARIOS block** (tinted): heading `SCENARIOS · BUY (My view: Bull) · max 3` (or the Buy|Sell toggle when view is empty/neutral). Row: letter · `[Pullback | Breakout]` · Pullback → `from – to`; Breakout → one number · note (optional, one line) · small ✕ remove. `+ Add scenario` hidden at 3. New idea starts with one empty row A (Pullback).
- Inline hints (muted; amber only when it needs a fix): lo ≥ hi → `⚠ from must be below to`; buy breakout ≤ now → `already above — fires on save`; mirrored for sell.
- Divider row: `Wrong if below [n]` (`above` for sell) · right `Now [n] typed · 22 Nov` (non-stock only; stores `lastPx {v, at}`).
- **REASONS**: Technical · Sentiment · Fundamental · Macro / news — always open, one-line inputs that grow to 3 lines. No "More notes" fold. `Built on` moves to the ⋯ menu (`Built on…`).
- `Check again on` (date).
- **Removed**: Next step field, Alert/Invalid direction toggles, NT1d PRICE ALERTS rows and their ruler preview. Save needs only About + Title (no scenario = Draft).

### E2 · Auto-copy on Save (adapt NT1d D2)
If tvAlert is false and (new idea or any scenario/Wrong-if number changed) and a scenario has numbers → copy the first changed scenario's line (else A's) synchronously in the click handler: buy pullback `XAU ≤ 3,340 · A pullback · <Title>` (sell: `≥ lo`), buy breakout `XAU ≥ 3,500 · B breakout · <Title>` (sell: `≤`), Wrong `XAU ≤ 3,200 WRONG · <Title>` (copied when only Wrong if changed). Toast (6 s): `Saved · copied for TradingView: <line>` + links for the other lines + `Open TradingView ↗`. NT1d fallbacks (never silent).

## F · Watch list row + Today
- List row line 2: `A pullback 3,290–3,340 · B breakout 3,500` (letters blue; full text, wraps, no "…"); line 3: date + ONE **pill** — priority: `✕ idea wrong` (amber) > `▼ A in zone` / `▲ B broke out` (amber) > `2.1% to A` (blue, nearest) > `1 day late` (amber text) > `in plan` (green) > `Draft` (grey, no scenario) + `check 25 Nov` muted.
- Today › Ideas (`nt1bDueMy`) ranks: **wrong 0 → scenario hit 1 → near 2 → late 4 → check today 5 → AI 6**. Rank 3 "no next step" is REMOVED. Ideas with a live `planId` never appear. Drafts appear only through their Check-again date.
- Today row: `TAG title` / line 2 `A pullback 3,290–3,340 <pill>` / button: wrong → `Drop idea ›`; hit + stock → `Make plan ›`; otherwise `Open ›`.
- Browser notification (NT1d rule) wording: `A in zone` / `B broke out` / `Idea wrong`.

## G · Make plan › (stock)
`nt1bMakePlan`: entry = fired scenario (buy pullback → `hi`, sell pullback → `lo`, breakout → `level`; none fired → A); SL `cnStop` = invLevel when set and the box is empty; link `planId` (existing `nt1bLinkPlan`). Then the idea shows `IN PLAN` and leaves Today.

## H · Drag to resize the list / detail split (≥ 1100px only)
- A 8px-wide hit area on the gap between list and detail; invisible until hover/focus (thin 3px grip + `col-resize` cursor). `role="separator"`, `aria-orientation="vertical"`, `aria-valuemin/max/now`, `tabindex=0`; ←/→ move 20px; Home = min, End = max; **double-click or Enter resets to 380**.
- Pointer events (pointerdown/move/up + setPointerCapture); updates a CSS variable `--nt-list` used by `grid-template-columns: var(--nt-list,380px) 1fr`; no layout thrash (rAF).
- Limits: **300–520px**, and never leave the detail under 760px (clamp by viewport). At ≥ 760 the detail stays `chart | scenarios` side by side.
- Saved per device in `localStorage` key `nt.listW` (wrapped in try/catch; missing/invalid → 380). Not synced to Firestore.
- At < 300 effective space the list chips may wrap to 2 lines — never cut. Below 1100px: handle hidden, default stacked/phone layout.

## Carry-over from the NT1d review (fix here)
1. List-row and ruler status texts must be real pills (blue / amber backgrounds), as on Today.
2. Every screenshot must show the state it is named after (NT1d's level-hit-detail did not).
3. `0.0% to level` → `at level` (see B).

## Tests (new `tests/run_tests_nt2.py`, Chromium 1440 + 390, mock Firestore; add to REST=)
1. Migration: NT1d idea (level 3,340 down, Bull, next, invLevel) → A pullback 3,340, note = next, Wrong 3,200; nothing deleted after Save.
2. Logic, buy + sell: pullback hit inside/below zone; breakout hit ≥ level; wrong wins; write-once; edit clears only that scenario's hitAt + tvAlert false; distance + near; `at level`; typed price > 24h → old price.
3. Layout 1440×900: list 380 / detail rest; header above chart; chart box ratio = image ratio (no white bars beyond 2px); reasons 2-col under the row; no page scroll when filled; `⌕` fully inside the list card.
4. Card: ruler band/ticks/dot order both sides; labels above/below, no overlap (bounding boxes); numbers not repeated in rows; pills have a background colour (computed); hit / wrong / in-plan / no-scenario states; no text-overflow ellipsis; phone 390 order.
5. Sheet: Pullback ↔ Breakout swaps inputs; max 3; remove re-letters; lo ≥ hi hint; Now only for non-stock; Buy|Sell only when view empty; no Next step / More notes; Built on in ⋯; Save with About + Title → Draft.
6. TV: copy-line formats (buy/sell, pullback/breakout, WRONG); title-only edit leaves clipboard; one tick; chips.
7. Today: ranks, no "no next step" row, in-plan absent, Drafts only via date; Make plan fills entry + SL, links planId.
8. Resize: drag to 450 → list 450, persisted after reload; clamps at 300/520 and detail ≥ 760; double-click → 380; keyboard ←/→; handle hidden at 1000px wide; localStorage throwing → still 380, no error.
Update older nt1d/nt1b tests that assert the removed Next step field, rank 3 or the 440 width — name them in the PR.
Hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` after the last change · only nt2 PNGs in the diff (`git diff --name-only origin/main...HEAD | grep png`); revert tracked screenshot rewrites.
Screenshots `docs/screenshots/nt2-*.png` (each must show its named state): watch-full (1440×900, filled) · sheet · hit · wrong · in-plan · today · phone · resized (list 500).

## Out of scope / follow-ups
NT2b: `Make plan ›` for Sat subjects (XAU/BTC/S50/Brent) opening a Sat plan prefilled from the scenario · price feed for non-stocks (SRTp: none) · AI-idea scenarios · same resize handle on other list/detail pages.
