# WL1 — Watch × TradingView workflow, homework size cap, no Candidate list (2026-11-12)
New branch `claude/wl1` from origin/main **after PB1/PB1b/PB1c are merged** (if not merged yet, branch from `claude/pb1` and say so). Don't merge. Mockup: `docs/briefs/mockups/wl1-watch.html`.
Scope: reuse existing pages/components; no new multi-step Research/Setup states; no order sending; no auto-sync back to TradingView.

## 0. Roles
- **TradingView:** 2 lists (Compounder, Momentum), each with sections `CANDIDATE` (scanning) and `WATCHLIST` (following). Planned/Holding colour tags set by hand by the user — the Dashboard never reads or writes them.
- **Dashboard = source of truth** for plans, size, orders, fills, homework, status.
- Plan: Entry / SL / risk budget → size; record Order / Fill (manual, real qty + price). Watch: homework + thesis (before and after buying). Port: real positions. Today: homework not done + add-on reviews.

## 1. Remove the Candidate list from the Dashboard (data kept)
- Remove the Candidates tab/list and its UI entry points (Watch header, Today Find/Triage links, Inbox deck, CSV candidate scoring) — keep pages otherwise as they are.
- **Before removing:** keep all candidate docs (no delete). Add a one-time, dismissible notice on Watch: "Candidates moved to TradingView · Export N as .txt ›" that downloads `###CANDIDATE,EXCH:SYM,…` per strategy (Momentum / Compounder) so the user can paste them into TradingView. Candidates that already have a plan, position or homework are moved into Watch automatically (no duplicates).
- **Remove TV1 export** (`###HOLD / ###READY / ###SCREEN` builder, button, its tests). Keep the Import below.

## 2. Watch rows — status from Dashboard data
Key = **exchange + symbol + strategy** (store `SET:HANA`, `NASDAQ:NVDA`). Status chip next to the name, computed (never stored, never from TV tags):
| Status | Rule |
|---|---|
| No plan | no active plan and no open position |
| Planned | active plan (incl. ordered), nothing filled |
| Holding | open position with remaining qty |
| Holding · Add-on planned | holding + an active plan/level not yet filled |
Row also shows: homework done / not done + current size cap (50% / 100%), what is missing (e.g. `④ missing`), action `Do homework ›` / `Open ›`. One stock can be in Watch and Port at once — same homework/plan records linked, never copied.

### UI (lean, symmetric, no overflow — mockup A/B/C)
- Header: `Watch` · segmented `Momentum n | Compounder n` · `⇩ Import from TradingView` (iPhone: ⇩ icon in the top bar). Summary line `n stocks · k need homework`.
- Mac: see the split layout below.
- **iPhone row = 2 lines:** line 1 symbol + exchange · status chip right; line 2 homework text (ellipsis) · action pill right. No horizontal overflow at 360/390.
- Sort: homework missing (Holding → Planned) → No plan → done.
- Import: Mac centred popup, iPhone bottom sheet; 3 equal preview tiles (new / already in / skipped).
- Plan cap box: headline `Homework not done · max 50%`, one number line `full · cap · filled + working`, one bar with the cap mark, Starter ¼ note when on.
- Today Act: one line per task (icon · symbol · reason ellipsis · one pill).

### Mac layout = split, narrow list + wide thesis panel (overrides the 4-column row above)
- Left list as narrow as possible (~300px, min 280): 2-line rows like iPhone (symbol + exchange · status chip / cap tag + homework text). No buttons in the row — click the row to open. Header: `Momentum n | Compounder n` segmented + `⇩` Import icon + summary line.
- Right = the existing thesis/detail panel (`wlOpen`), taking all remaining width; **keep the existing font sizes** (`--read-fs`, `.pbThesis` etc.) — wider column = easier reading, no size change.
- Panel **always opens on the Summary tab** (ignore the remembered per-ticker sub-tab; old `wlSub` memory no longer used for opening). Homework state + `Fill ④ ›` + `I've reviewed this` (disabled until required fields are filled) at the bottom of the panel.
- iPhone unchanged: 2-line rows with one action, tap → full-screen sheet (also opens on Summary).

### Keys / gestures
- **`←` / `→` keep switching the thesis tabs** in the panel (existing, unchanged).
- **`Tab`** (the key that used to toggle Candidate ⇄ Watchlist) now toggles **Momentum ⇄ Compounder**. Ignored while typing or with a popup/sheet open; Shift+Tab / normal focus navigation inside inputs unaffected.
- iPhone: middle-screen swipe left/right toggles Momentum ⇄ Compounder (SW2 gesture rules; bottom-bar swipe unchanged; one-time hint). Choice remembered per device.
- Switching list keeps the panel if the selected stock is in the new list, else selects the first row.

## 3. Import from TradingView (Watch header button)
- Popup: strategy switch Momentum | Compounder · paste box · upload `.txt`.
- Parse: split on commas/newlines; a token starting `###` starts a section (case-insensitive). Read **only `###WATCHLIST`**; ignore tokens before the first section, `###CANDIDATE` and all other sections.
- Valid item = `EXCHANGE:SYMBOL` (`[A-Z0-9_.!-]+:[A-Z0-9_.!&-]+`, uppercased). Anything else (formulas like `SPY/QQQ`, spreads, bare symbols) → listed as skipped with reason, never guessed.
- No `###WATCHLIST` section → message "No WATCHLIST section found", nothing imported (never fall back to the whole file).
- **Preview before save:** counts new / already in Watch / skipped + the list; button `Add N to <strategy>`.
- One stock = one list: a symbol already in Watch under the OTHER strategy is shown as "already in Watch (<strategy>)" and is not added or moved.
- Import only adds Watch items (status No plan unless plans exist). It never creates a plan/order/position, never unlocks size, never overwrites thesis/status/plan/order/fill/position, never removes stocks missing from a new file.

## 4. Entry workflow
1. User scans in TV (CANDIDATE). 2. Sees a setup → **New plan** (existing popup: S / D / F). Strategy, Entry, SL, risk budget → full size. 3. Size cap applies (§5). 4. User places the order at the broker; records `Ordered` / `Filled ✓` with real qty + price.
5. **First fill (even partial):** auto-add to Port (existing) and to **Watch** for that strategy if not there (key §2; no duplicates). If homework not done → **one** Today task `📚 <SYM> · Holding · homework not done · cap 50%` (not re-created on later fills; closes automatically when homework is done or position closed). User moves it to WATCHLIST + tag Holding in TV by hand.
6. Homework done → cap 100%.
7. Add-on condition met (existing add-on rule) → Today `🛡️ <SYM> add-on condition met · Review add-on ›` (opens the plan; no auto order).
- Cancelled order with no fill → no auto-add to Watch/Port. Sold out → position closed, history + thesis kept, Watch row stays (status No plan).

## 5. Size rules (all active rules must pass for every order)
- **Homework cap (permanent):** homework not done → total position (filled + working buy orders, across ALL active plans/levels for the same exchange+symbol+strategy) ≤ **50% of full size** (full = from risk budget + SL, existing formula). Done → ≤ 100% total (includes what is already held; not "another 100%").
- **Starter ¼ (training mode, Settings toggle, existing):** when ON, first entry = ¼ of full; add-on brings the total up to the cap in force — **the old 75% add-on never exceeds the homework cap** (homework not done → add-on max to 50% total). When OFF, only the homework cap applies.
- Several plans for the same position cannot bypass the cap (aggregate per key).
- Add-on re-checks total risk, SL and existing position (existing checks) + cap.
- Plan form shows a cap box (mockup B): `Homework not done → max 50%` · full / cap / filled + working · bar with the cap mark · Starter ¼ note when on · `Do homework ›`. Place order / Filled ✓ that would exceed the cap → blocked with the reason (show allowed qty).

## 6. Homework = existing checklist + confirm
- MMT: ④ Wrong if + trigger. COMP: ① Why buy + ④ Wrong if (living-thesis fields). Plus a final **"I've reviewed this" confirm** (stores time). Done = all required fields non-empty **and** confirmed (text alone is not enough). Editing ①/④ later keeps "done" (no re-confirm needed) unless a required field becomes empty.
- Homework lives on the Watch item (linked from Plan drawer THESIS and Port).

## 7. Data safety
- No deletes. Candidates kept (hidden). Old docs without the new fields work. New fields only: `exch` on Watch items if missing (derive from existing symbol data; ambiguous → ask user once per item in the row, don't guess), `hw.doneAt`, `hw.confirmedAt`.
- Existing Watch items keep thesis/data; duplicates found by the key are listed in the PR (not auto-merged).

## Tests (new `tests/run_tests_phase374.py`, 390/1280/1440)
Import: example `###WATCHLIST,SET:HANA,###CANDIDATE,SET:BAFS,SET:EPG` → only SET:HANA; case-insensitive `###watchlist`; tokens before first section ignored; no WATCHLIST → message, 0 added; formula skipped with reason; preview counts; existing item untouched; re-import without an item doesn't remove it; .txt upload. Status chips for all 4 states incl. Add-on planned. First partial fill → Watch + Port once; second fill → no duplicate, no second Today task; cancelled unfilled → nothing. Cap: not done → filled+working ≤ 50% across 2 plans (second plan blocked); done → total ≤ 100% incl. held; Starter ¼ on → first ¼, add-on stops at 50% when not done; off → only cap. Homework done needs fields + confirm; Today task closes. Add-on reminder once. Sold out → closed, Watch row No plan. Candidates tab gone, export notice works, candidate docs still in storage. TV1 export gone; Import kept. Tab key / middle swipe switch Momentum ⇄ Compounder (ignored in inputs and sheets; ← → still switch thesis tabs; bottom-bar swipe unchanged); panel always opens on Summary; Mac list ≤ 320px, panel font sizes unchanged. Rerun SW2, 369, 370, 373, ui_audit → 0 (retire 368 TV1, say so). Screenshots `tests/screenshots/wl1-*.png`. Commit, push, short summary + results.
