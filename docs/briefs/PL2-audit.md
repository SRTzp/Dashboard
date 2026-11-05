# PL2 — Audit (read-only, no code changed)

Base: `claude/pl2` rebased onto `claude/pl1-phase-a` (PR #6 is NOT merged into main; PL2 brief commit on top). Line numbers refer to `index.html` at that base (25323 lines).

## 1. Weekly Impact — Monday runs
**Findings**
- `wpWeekKey(d)` (17914) = local-clock Sunday of the week. `wiCurMon()` (24226) = that Sunday + 1 = the Monday of the current Sun–Sat week. `wiCurDoc()` = `wiDocs[wiCurMon()]`. `wiOtherDoc()` (24228) = newest doc by key.
- `Calc.wiValidate` (18445): `week` must be YYYY-MM-DD **and** a Monday. It does NOT compare `week` to the current week, so import never warns about wrong week. `wiSave` (24398) writes doc id = `week`.
- **Monday run, week = this Monday:** `wpWeekKey(Mon)` = yesterday's Sunday → `wiCurMon` = today → doc is CURRENT. Already correct; no change expected.
- **Sunday:** `wpWeekKey(Sun)` = today → `wiCurMon` = tomorrow → a doc for tomorrow's Monday is current. Correct.
- **Saturday:** `wpWeekKey(Sat)` = the past Sunday → `wiCurMon` = the Monday 5 days ago. A Saturday run for NEXT Monday is saved fine, but is shown as "other week": panel shows `ต่างสัปดาห์ · มีข้อมูลล่าสุดของ … (ไม่ใช้เป็นข้อมูลสัปดาห์นี้)` (24317) and the Today freshness chip (7800) uses `stale`/`old`. So the wrong-week warning DOES appear for Saturday-run-for-next-Monday. (Weekend Macro Update by design is a Sat/Sun run.)
- Not found: any "expired" wording in the Weekly Impact path (the `expired` hits are Trade ideas).
**Proposed change**: none for Monday/Sunday. For Saturday: brief says fix only if wrong-week warning shows — it does. Smallest fix: on Saturday (local day 6) treat the upcoming Monday as current, i.e. `wiCurMon()` = `Sun+1` of the *next* Sunday only when `getDay()===6`. This touches only the Weekly Impact week mapping (no trading rule). **Decision needed (D1)**: do you want Saturday to roll forward to next Monday for Weekly Impact only? Alternative: leave as-is and only report.
**Tests**: fake clock Mon/Sat/Sun × doc for matching Monday → no `data-wi-diffweek`, `wiCurDoc()` set.

## 2. Unfinished-today banner
**Findings**
- `td4RemList` (7925) emits `{sec,mk}`: `hw` (+US/TH), `screen`, `add`, `sat`.
- `td4RemGo` (7944) only (a) switches `td4HwMk` and (b) scrollIntoView on `[data-td3-sec="…"]` / `[data-td3-panel="sat"]`. It never switches tab, opens a section, or opens a flow; silent if element missing.
- Selectors present: `data-td3-sec` = add, hw, screen (1 each); `data-td3-panel="sat"` ×2. After PL1 A7 weekday layout renders a `plans` block — no `data-td3-panel="plans"` exists in markup (0 hits), so Sat selector must be found by inspecting the Plans block (`td3PlansHtml`, 7721) — to be confirmed in build.
**Proposed**: rewrite `td4RemGo` to: ensure Today tab (`switchTab('today')`), set market, then per item call the existing entry points: deep-dive open for next stock of that market (from `td4HwMk`/`M.hwm`), first unscreened candidate → existing screening modal, Add Candidate popup (PL1 A1) with focus, first non-saved `td3SatRows()` row (or Sat planning panel). Fallback: expand/render, scroll, else toast "Couldn't open X". Exact function names for each flow will be looked up in build (not guessed here).
**Tests**: 4 buttons from current Today layout; failure path shows toast.

## 3. My Thesis replaces "มุมมอง"
**Findings**
- `LT_TABS` (16206): `['sum','สรุป'],['view','มุมมอง'],['biz'..],['why'..],['trk'..],['exit'..]`. `sub==='view'` renders `vwBlockHtml(sym,'wl')` (16605).
- Legacy block `vwBlockHtml` (13986): `VW_ANGLES` rows (Event / Fund. / Tech), notes + images stored in `stockNotes` (via `vwList/vwWrite/vwSave/vwDel`), Tech angle holds chart image (`chart` url, `vwImgHtml`, `vwZoom` viewer, `tvSnapImg`). Also embedded in Candidate cards (14378, ctx `'cand'`) — brief says remove "duplicate legacy personal-view block from the UI": **Decision D2**: remove from Candidate cards too, or only the Watchlist `มุมมอง` tab? (I'd assume both, keeping data.)
- PL1 already has My Thesis on the Watchlist card: `wlMtHtml` (7194) = ① Why buy, ④ Wrong if, Next check date, What to check, Save, Archive/Restore; stored in `watchlist/{T}.my_thesis {why, exit, updated_at}` + `next_check_*`. AI thesis is separate (`it.thesis`, `thesis_imported_at`) and `wlMtHtml` already shows "AI Thesis: imported/data as of" dates.
- Images today live only inside stockNotes (Tech angle `chart`), NOT in `my_thesis`. Reusing existing storage = My Thesis gallery reads/writes stockNotes `tech` entries via `vwWrite/vwImgHtml/vwZoom` (no new storage, no migration).
**Proposed**: rename tab to `My Thesis` (key stays `view`); the tab renders `wlMtHtml`-style form + image gallery (add/view/remove via existing vw image functions) + "Previous notes" list (all legacy Event/Fund./Tech notes with original tag + date, read-only plus existing delete). Wide screens: AI Thesis preview card (summary + imported/as-of date + "View AI analysis" → `sub='sum'`). No AI → empty state with existing Import action. Saving My Thesis writes only `my_thesis`/`next_check_*`; AI import code untouched.
**Risks**: `wlMtHtml` is also on the Watchlist card at 13664 — decide whether it stays there (**D3**: I'd keep a single editor in the tab and leave the card's compact form untouched to avoid regressions).
**Tests**: edit text + add image → reload persists; import AI → My Thesis unchanged; legacy notes/images visible.

## 4. Today: "Core Port" → "Selection"
- One site: `P('core', 'Core Port', core)` in the Today build (line ~7882 template region). Label only. Existing tests grepping "Core Port" on Today will need log in `PL2_retired.md`.

## 5. Trade summary on qualified setup
**Findings**
- Plan data: `coreView` (10102) / `coreCardHtmlBase` (10374); sizing via `cs.firstLot` with `cs` snapshot (Base Risk 1%, `CS_CAP_KEY='A'`, 14181). RS stars: `rs_stars` on watchlist item (`wlStarsOf`, 7150; null = Unrated). Reason tags: `settings.candReasons` + `candMeta[KEY].reasons` (`CRS_DEFAULT`, 6831).
- No "setup qualifies" summary exists. "Setup conditions pass" for Momentum/Compounder is not an explicit flag I could locate (Sat has `Calc.setupPass`; stock plans use Ready rule + screening). **Decision D4**: what exactly is "setup conditions pass" for stock plans — (a) plan form complete with entry+stop and sizing OK, or (b) the Ready rule/screening status? I'll default to (a) unless told otherwise.
**Proposed**: read-only block built from the same values the plan form shows (entry, qty from the same firstLot call, stop, risk money and % of pool, RS stars or "RS: Unrated", reason labels). Any missing → "Missing: …". Test asserts summary == form values.

## 6. Sat: Classify → 2 checkboxes
**Findings** — all `classify` consumers (complete list): 
- 7602 `td3PlanStatus` "Needs Clear Trend"
- 21573 `pfClassifyHtml` (badge) · 21635 summary text "Tactical needs Clear Trend"
- 21970 `satTacLock` (also used 21982, 22186)
- 21981/21989 the TF | Trend | Classify row (select) · 22027 `pfClassifySet`
- 21692 idea default `classify:''`; `satV3IdeaWrite` stores fields on the idea.
- `PF_CLS` (21568) used by `pfClassifyText/Cls` (21571+).
**Proposed**: add booleans `ema50_ok`, `structure_ok` on the idea (via `satV3IdeaWrite`); replace the select with two checkboxes; new helper `satClearOk(idea) = ema50_ok===true && structure_ok===true` used in all 4 consumers; message → "Needs EMA50 + Structure verify". Old `classify` left stored, ignored for gating. Badge: show Clear Trend badge only when helper true (Up/Down still from trend).
**Risk**: entered trades unaffected (`satIdeaHasTrade` guard already in `satTacLock`). Existing tests that set `classify:'clear'` to unlock Tactical will need expectation changes → logged.

## 7. Candidate-first workflow
**Findings**
- Ideas data: collection `users/{uid}/ideas` (`ideaCol`, 14402) with themes → companies (`IDEA_*` constants 14384+, statuses exploring/need_evidence/ready/parked, companies with `IDEA_CSTATE`). This is idea-scout `idea@1`/`trade@1` content — **NOT the same as Satellite ideas (`satIdeas*`)**, which stay untouched. Trade ideas (`trd*`, `trade@1`) share the Watch › Ideas area.
- Candidate pipeline: TD4a (6815…): "Back in Ideas" chips (7048, 7053, 7085), New Cand counter, Cand→WL x/5.
- Tier: 450 mentions in `index.html`, 38 in `core-size.js`. **Sizing finding**: PL1 already routes NEW plans through `c.cs` and `csTier(c)` returns constant `CS_CAP_KEY='A'` (14186), and `cx.opts.tierCap/stockCap` are collapsed to a single value for new plans (9932). So removing tier selection from UI should not change math for new plans. Legacy cards without `c.cs` still read `c.tier` ('A'/'B' → different `tierCap`/`stockCap`/`tierRisk`) → those MUST keep reading stored tier (stored data stays), so `core-size.js` tier tables stay.
**Decisions needed**
- **D5**: "stock Ideas stage" — is it the thematic Ideas (idea@1 themes/companies) being retired as a required step (keeping the tab for browsing/import and only dropping gates, counters, reminders, "Back in Ideas", onboarding text), or should the Ideas tab itself be hidden? I plan the former: stop requiring it, keep tab and stored data, migrate stock-company entries that aren't yet Candidates/Watchlist into Candidates with source "From Ideas".
- **D6**: Migration trigger — one-time automatic (flag stored in settings), or a manual "Move to Candidates" button? Writing to Candidates is a stored-data change; I'll implement an idempotent, additive, flagged migration (never deleting Ideas) only if you approve.
- **D7**: `WL_TIER`/"ตั้ง Tier…" button (3962), tier review chip (13547), `NO_WL_TIER` warning (4577), tier text (11170, 16138) go away from UI; tier fields untouched in Firestore.
**Tests**: new stock → Candidate → screen → Watchlist without any Tier step; legacy Candidate/Watchlist/Ideas records open.

## Build order & risk
Per brief: 4+1 → 2 → 6 → 5 → 3 → 7. Backup `index.backup-pre-PL2.html` + `tests/_bk_pl2/` before first edit; commit after each item; `tests/PL2_retired.md` for changed expectations; `tests/make_verify.sh PL2` at end.

## Questions blocking edits
D1 Saturday roll-forward (Weekly Impact) · D2 remove legacy view block from Candidate cards too · D3 keep compact My Thesis on the Watchlist card · D4 definition of "setup qualifies" for stock plans · D5 scope of "Ideas stage" removal · D6 migration trigger.
No sizing change is required by any item as audited (item 7 sizing already tier-free for new plans).
