# NT1d — My ideas: 2-column detail · level alert · Today "no next step" · Evidence fix · Settings hints

Mockups (commit them first): `claude/mockups/nt1d-ideas.html` (sections 1–5) · `claude/mockups/nt1d-watch-full.html` (full page 1440×900, v2) · `claude/mockups/nt1d-sheet.html` (the edit sheet + field audit — **wins over the sheet text in nt1d-ideas.html §4**).
UIUX lens applies to every part (plain words, one dark button per area, amber = to do, blue = distance, nothing twice, no "…" cuts).
Single file `index.html`. No new Firestore rule (ideas_my has no field whitelist). No new price feed.

## A · Bug: `.nt1-x` is defined twice (do first, own commit)
- CSS line ~5709 `.nt1-x{all:unset;width:44px…}` is the sheet's ✕ button. Line ~5689 `.nt1-x{font-size:13px;margin:6px 0}` is used for text rows (Recheck, AI suggestion `call`, Study order, assets) in the AI-generated Evidence / Companies folds → squeezed into 44px and drawn over the fold headers.
- Rename the TEXT-row class to `.nt1-note` (CSS + the 3 template sites in `ideaDetailHtml`: `evd`, `callTx`, `co`). Keep `.nt1-x` = close button only.
- Test: at 1440 the Recheck row is > 300px wide, does not overlap the fold summary (bounding boxes), computed `width` ≠ 44px; ✕ button still 44×44.

## B · My idea detail = 2 columns (mockup §1, §5 phone, watch-full)
Real widths at 1440: list 440 + detail 820. Detail panel, top to bottom:
1. Header (unchanged: tag · title · view chip · date · Edit · ⋯).
2. Row 1 grid `3fr 2fr` gap 14, `align-items:stretch`. Left: chart, `min-height` 372, stretches to the right column's height, `object-fit:contain` on white, no dead bars. Overlays: `⤢ Enlarge` bottom-left, `TradingView snapshot ↗` bottom-right (existing). Right column, top to bottom: Next step card (incl. level + TV-alert lines + Snooze · Done · Level hit), then the angle cards that are not empty (Technical, Sentiment, Fundamental, Macro / news — compact, one per row), then a `Plan (old)` card ONLY if an old Plan text exists.
3. Footer row: `Built on: … ›` left · review hint/buttons right (existing `nt1ReviewHtml`). "Check again" is shown once, in the Next step card (remove the duplicate footer line).
- ⤢ Enlarge → in-app large view (modal): image max 90vh/90vw, Esc / click outside / ✕ closes, focus returns, `↗ Open in TradingView` link inside. The ↗ on the chart keeps opening TradingView.
- No chart / chart link only → single column (Next step + Plan on top, angles below). Image load error → existing fallback (`nt1ChartErr`).
- Next step card colour: next step set → green; "Not set" → amber with the one dark button `Set next step ›` (opens the edit sheet focused on Next step). Level-hit state: see D.
- Phone (≤ 760): chart (full width, 230) → Next step → Plan → angles (1 col) → footer.
- Fits 1440×900 with no page scroll when everything is filled (watch-full mockup). Panel scrolls internally if it ever doesn't.

## C · Today › Ideas card: new idea without a Next step
Add to `nt1bDueMy`: not reviewed / dropped / snoozed ahead, `next` empty, subject is not `old` → due, rank 2, pill `no next step` (amber `p-a`), button `Set next step ›` (plain, `nt1OpenMy` + focus Next step), sub `New · <date> · <view>`. Leaves as soon as a Next step is saved. Rank order: **level hit 0 → near level 1 → no next step 2 → late 3 → check today 4 → AI 5**. Max 3 rows unchanged. Snooze / Done / Drop work as now (snooze hides the "no next step" row until the date).

## D · Price level → "level hit" (mockup §4)
Data (all optional, on `ideas_my`, whitelist in `nt1Payload` + parse at ~30698): `level` (existing), `levelDir` `'up'|'down'|null`, `lastPx` `{v:number, at:ISO}|null`, `tvAlert` bool, `hitAt` ISO|null.
**Edit sheet (see `nt1d-sheet.html`; replaces the current sheet layout).** 8 fields + one fold, each with one job:
- Identity: `About` · `My view` (optional) · `Title` · `Chart`.
- `FOLLOW-UP`: `Next step` · `Check again on` · `Alert level` (number) + segmented `≥ | ≤` (neither selected until chosen; level without direction saves, state stays `near`-only; helper `Reached when price goes ≤ 3,340`) · `Last price` (number; shown ONLY when About is not a stock — stocks use the daily close; stores `{v, at:now}` when changed; label "display only").
- `MY NOTES` fold `More notes ▸` (closed by default; opens if any of them has text): Technical · Sentiment · Fundamental · Macro / news · Built on. Empty ones are never drawn in the detail.
- **Removed from the sheet:** `Plan` (overlaps Next step; the real plan is made on the Plan board with `Make plan ›`; existing text is kept and shown read-only as `Plan (old)`), the TradingView `Copy level` button and `I set the alert` tick (auto-copy on Save replaces the copy; the tick lives once, in the detail card).
- Save needs only `About` + `Title`. Data is never deleted; stored `plan` is untouched.
- Detail card TV row: `TV alert: not set` (amber) `· Copy text · Copy level · I set it`, or `TV alert: set ✓`; `Copy text` = the D2 line, `Copy level` = the plain number.
Price used for the level check — `nt1bLevelPx(m)`: stock → existing `nt1bPx` (last close, `pxAuto`); everything else → `lastPx.v`. Shown as `now 3,412 (manual · 22 Nov)`; manual older than 24h → amber `old price`. **Display + this alert only** — never an engine / sizing / gate input.
`nt1bLevelState(m)` → `{state:'hit'|'near'|'none', px, distPct, src, old}`:
- `hit` when `hitAt` is set, OR level + direction + price exist and (`up`: px ≥ level · `down`: px ≤ level). When the price condition first becomes true on load, write `hitAt` (merge) once; it is never cleared by price moving back (the touch happened). 
- `near` = existing rule (stock, within `NT1B_NEAR` 3%, not hit) → blue pill `1.8% to level` (wording unchanged, matches Act).
- Detail › Next step card, not hit: line `Level ≤ 3,340 · now 3,412 (manual · 22 Nov) · 2.1% to level`; line `TV alert: not set` (amber) `· Copy 3,340 · I set it`, or `TV alert: set ✓`; quiet link `Level hit` (the dashboard cannot see TradingView: after the TradingView push arrives you press it → writes `hitAt`).
- Detail › hit: card turns amber, header `LEVEL HIT · 25 Nov 21:42`. The one dark button is the action: stock → `Make plan ›`; any other subject with an empty Next step → `Set next step ›`; otherwise no dark button. Quiet link `Not yet · snooze 3 days` (sets `snoozeTo`, keeps `hitAt`, removes the row from Today until that date).
- Today › Ideas row: rank 0, amber pill `level hit`, button `Make plan ›` (stock) / `Open ›`; sub `Level ≤ 3,340`. Watch list row: same amber pill. Watch nav pill counts it as due.
- Browser notification: while the app is open and a level becomes hit, one `new Notification('Level hit', {body, tag:'nt1-hit-'+id})` if permission already granted (reuse the TD4a permission helper; do NOT prompt). Never a popup/alarm. Real-time push when closed = TradingView alert on the phone (stated in a one-line hint under the TV row: "TradingView sends the push; the dashboard marks it when you open it").
- Edge: level without price source → `now —`, `near`/`hit` impossible except the manual `Level hit` button.

### D2 · Save idea → auto-copy the alert text for TradingView
- On `Save idea` (`nt1SheetSave`): if the idea has a `level` and (it is new, OR `level` / `levelDir` changed in this edit) and `tvAlert` is not ticked → copy ONE line: `<TAG> ≤ 3,340 · <Title>` (`≥` for above; no direction → `<TAG> 3,340 · <Title>`; TAG = subject tag like XAU / AVGO). That line is the TradingView alert name / message, so the phone push reads the same as the idea.
- Call `navigator.clipboard.writeText(...)` synchronously at the start of the click handler (before any await / Firestore write) so it stays inside the user gesture; fall back to the existing `nt1CopyText` textarea+execCommand path if it rejects.
- Toast (existing `nt1Toast`, 6 s): `Saved · copied for TradingView: XAU ≤ 3,340 · Opportunity to Buy Gold` + link `Open TradingView ↗` (the idea's chart link if any, else `https://www.tradingview.com/chart/`) . If both copy paths fail: toast shows the line with a `Copy` button instead (never silent).
- Plain edits (no level change), ideas without a level, and ideas with `tvAlert` ticked do NOT touch the clipboard. The level number is inside the line; the separate `Copy 3,340` button (plain number for TradingView's value box) stays.
- Test: new idea with level → clipboard equals the line, toast shown, Firestore write still happens; edit title only → clipboard unchanged; level changed 3,340→3,300 → copied again; clipboard denied → toast with Copy button; `tvAlert` ticked → no copy.

## E · Settings: old mono hints (queue item 1)
`.ps1Rg` (Min stop (stocks) / Satellite min stop / loss-limit rows) uses `font-family:var(--mono)` and `.72rem`. Change `.ps1Rg` to Inter 12px muted (`color:var(--muted)`), and drop `.ps1Rg` from the mono font lists at lines ~3820 / ~3823 if they force mono; same pass for `.set1sm` sub-labels if they render mono. Plain words, nothing cut. Also check Settings at 1440 and 390: hints wrap, never truncate with "…". No behaviour change.

## Tests (new `tests/run_tests_nt1d.py`, Chromium 1440 + 390, mock Firestore; add to REST=)
1. A: as above. 2. B: 1440 filled idea — chart left col stretching to the right column (Next step + angle cards), no Plan card unless old plan text exists, no row-2 grid, no page scroll at 1440×900, Enlarge opens/closes (Esc, outside, focus return), no-chart → single column, 390 order. 3. C: new idea no Next → Today row `no next step` + `Set next step ›`; save a Next step → row gone; snooze hides it; order ranks. 4. D (sheet): exactly the 8 fields + fold above; no `Plan` textarea and no TV copy / tick in the sheet; `Last price` hidden for a stock, shown for XAU; `More notes` closed by default, open when a note has text; Save works with only About + Title; old `plan` text still shown as `Plan (old)` and survives a save. D (alert): down-level 3,340 with last price 3,412 → `2.1% to level`, TV row amber; set last price 3,300 → `hitAt` written once, Today row `level hit` first, detail amber `LEVEL HIT`; price back to 3,500 → still hit; `Level hit` button on a fresh idea → hit; stock via `pxAuto` close crosses → hit; manual price > 24h → `old price`; no direction → no hit from price; Copy puts `3340` on clipboard; no engine input changed (grep sizing code unchanged). 5. E: `.ps1Rg` computed font-family is Inter, no `text-overflow` ellipsis.
Hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` after the last change · only nt1d PNGs (`git diff --name-only origin/main...HEAD | grep png`).
Screenshots (docs/screenshots/nt1d-*.png): watch-full 1440×900 filled · no-chart · phone 390 · level-hit detail + Today row · evidence fold fixed.

## Out of scope
Real-time or server-side price alerts (TradingView does that) · new price feed for XAU/BTC/S50/Brent · AI-idea levels · RS2c.
