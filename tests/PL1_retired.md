# PL1 — expectation changes (no test deleted · each row = behaviour the PL1 brief changed)

Phase A, Step 2 (A4 single Base Risk + A3 manual RS stars)

| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase111 `calc` | `starsFromEval` table, `evalGate`, `starBudget` formulas | **RETIRED** (prints RETIRED) | A4 removed these functions; `Calc.riskBudget` (same formula, flat Base) is covered in phase114 |
| phase111 `size` | size by ★★★/★★/★ (127/95/63), banner `★ · Base risk x% · Manual`, snapshot `stars:3`, buy-1 risk 1 | **RETIRED** | Base Risk is one value; covered by phase114 `size` |
| phase111 `gate` (3 funcs) | open-plan gate (Stars · RS · Gate 5), `Missing:` banner, Candidate→WL gate, Pending Review chip | **RETIRED** | A4 removed `evalGate`/Pending Review; the new Ready rule (A5) and screening (A2) arrive in Step 4 |
| phase111 `budget` | AAPL→MSFT switch expected `★★ · 0.75%` | now `Base risk 1.00%` / risk 1.0 | flat Base Risk |
| phase111 `budget` | switch to ticker with no stars → `No stars · Unassigned`, empty risk | **RETIRED** (comment) | no stars gate; every ticker gets flat Base |
| phase111 `budget` | reload check `e.stars == 3 and gate5 == passed` | only `date` checked | evaluation sheet no longer edits stars/gate5 (data kept) |
| phase107 §3 | `Need: Stars · RS · Gate 5 (0/3)` and `Need: Stars`, ☆☆☆ row | `Ready` (note present); star step **RETIRED** | interim `td4ProMissing` = note only (`// PL1 interim — replaced in Step 4`) |
| phase107 §3 | tap star again to clear; `stars=2` on promoted doc; `✓ … · ★★ · Undo` | **RETIRED** / `stars==0` / no ★ in moved line | no ★ control on the Candidate form; promoted doc no longer writes `stars` |
| phase107 `pro_fill` | clicks `[data-td4-star]` | star click removed | same |
| phase107 §3 layout | hint row left + ☆☆☆ right | hint row only | same |
| phase107 `W()` fixture | `stars=n` | also sets `rs_stars=n` | Watchlist sort/filter now reads `rs_stars` (A3) |
| phase107 §4 | tap star 1→2→3→3 = 1,2,3,0; `wl-sd` `★3` | RS dropdown → `rs_stars` 1,2,3,null; row badge `RS ★★★` | A3: Unrated ≠ 0, dropdown replaces 3-button control |
| phase109 §2 | 3 star buttons ≥32px, tap-again→0, aria-pressed, `stars` persisted | RS dropdown ≥30px high; `rs_stars`/`rs_rated_at`; MSFT legacy `stars=1` untouched | A3 |
| phase109 §3 | click `[data-td4-star="2"]` in Candidate form | removed | no ★ control there |
| phase65 | Settings default `sCrRiskA` = 1.25 | = 1 | the field is now Base Risk per trade (key `baseRisk`, default 1) |
| phase65 | save → `riskPct 1.5` · `riskA 1.5` | save → `baseRisk 1.5`, `riskA`/`riskPct` not written (kept as stored) | A4: legacy keys kept, not migrated |
| phase65 | Tier A/B plan cards sized at Risk A = 1.5% | A = B (stored `riskA`, default 1.25) | legacy cards still size from stored `riskA`; the Base Risk field no longer moves them |
| phase66 | multi-error line `A · Risk/ไม้ ต้องอยู่ระหว่าง 0.1–5` | `Base Risk per trade ต้องอยู่ระหว่าง 0.1–5` | field label |
| phase91 #11 | "first-lot risk > Base → ต้องไม่เกินงบเสี่ยง Base" | **RETIRED** | `riskFirst` no longer coupled to the Base Risk field (legacy-only) |

## Known pre-existing failures (also fail on main — not caused by PL1)
- phase66 S2 (`index.backup-pre-POL1.html + tests/_bk_pol1/` — folder not in repo)
- phase23 (migration writes 2×), phase13, phase5 — see `docs/reports/RUN-summary.md`

## New suite
- `tests/run_tests_phase114.py` — A4 (Calc.riskBudget, flat 1%, Settings label/default/save, old plan snapshot untouched) + A3 (rs_stars Unrated≠0, rank-only, old `stars` ignored) + interim note-only promote form

## Step 2b — label rename (display text only · keys `winner`/`ladder`/`Winner`/`Ladder` kept)
Winner/Winners → **Momentum**, Ladder → **Compounder** in user-visible text (scope tabs, Settings, Today pools/verdict/DD chips, Journal buckets, plan-form titles/errors, Watchlist track pills, Goals rows via `TD3_SUB_LBL`). "Core" wording is untouched (awaiting user decision).

| Suite(s) | Change | Why |
|---|---|---|
| phase106, 109, 112, 113, 89, 91, 83, 84, 77, 53, 39, 14, 23, 24, 56, 99 | expected strings `Winner(s)`→`Momentum`, `Ladder`→`Compounder` (verdict line, pool lines, DD chips/rows, scope buttons, tags `A · Momentum`, Settings pool row, DD table headers, `New Momentum plan`, track-change errors) | label rename |
| phase23 | `sCrRiskA` default 1; save writes `coreRisk.baseRisk` (no `riskPct`/`riskA`); `coreSizeOpts` check reads `coreRiskCfg().baseRisk` | A4 (Step 2) |
| phase97, 99, 113 (§UI1/§UI3) | no expectation change — header scope tabs tightened (`#hdrSub .scopeBtn` 4px/.76rem, hint hidden; in-page ≤480px padding/font; `#ldrAddSel{max-width:100%}`) so longer labels still fit | layout |

## Step 2c — "Core" → "Momentum" where it means the Momentum bucket/page (display only)
Renamed: "การ์ด Core" (cards/empty state/confirm sheets), "ถัง Core" (no-tank messages, `% ของถัง Core` summary), "Core · การ์ดตำแหน่ง", Settings units `% of Core bucket` → `% of Momentum bucket` (first-lot / accelerator / layer-2 fields), pool summary heads `Core Port` → `Momentum Port` (Plan summary + Plan header). Kept: port name `Core Port` (Settings/PORTS), Max Heat row `Core — % of Core bucket`, `Core.US`/`Core.TH`, Settings port toggle, Today `Core ·` subtitles + `Core Port` panel head (A7 replaces them).
Suites with updated expectations: phase14, 22, 23, 29, 83, 89. phase43 `index.backup-pre-PX1.html + tests/_bk_px1/` fails on main too (backup folder not in repo).

## Step 3 — A1 Add popup + Candidate reasons
| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase107 `add()` helper | Add wrote candidates directly | after clicking Add, test fills Track `winner` + reason `strong-rs` on every popup row and Saves (`candPopSave`) | Add now opens the popup (Track + ≥1 reason required) |
| phase108 §B6b (Watch Add on candidate) | same direct-add flow (4 spots) | same helper step; message texts unchanged (`Added 2 to Candidates`, `already a Candidate`, `Daily limit 10 reached`, `already in Watchlist`) | same |
| phase108 §B6b | NEW1 form memory check expected `stars: 2` and clicked `[data-td4-star]` | `stars: 0`, no star click | Step 2 removed the ★ control (missed in Step 2) |
| New | `tests/run_tests_phase115.py` (52 checks: reasons settings, popup rows/Apply-to-all/override/remove, required Track + reason inline errors (no alert), partial save, quota counts saved rows only, Cancel keeps draft, glWrite=false keeps entries, refresh keeps picks, legacy "Old risk rule" hint) | — | A1 |

## Step 4 — A2 screening modal + A5 Ready rule
| Suite | Check / area | Change | Why |
|---|---|---|---|
| shared `tests/ff_stub.py` | init script | adds `READY_STUB` — after page load `wlReady()` returns true unless `window.__READY_REAL` is set | legacy suites open plans for arbitrary tickers; the Ready rule is tested for real only in phase116 |
| new `tests/scr_helper.py` | `promote(page, sym, track, why)` | sets candMeta track if missing, opens the modal, Proven Pass + Trend Pass + Why, saves | replaces `td4ProSave()` / the inline Move form in legacy suites |
| phase61, 62 | direct `td4Pro = {...}; td4ProSave()` | `scr_helper.promote(...)` (Tier/Phase carry unchanged) | inline form removed |
| phase107 §3 | form with Note / Sector / Track / Need-hint / Move button, `promoted_by ['rs']`, `note` = typed note | form = summary + `Screen ›` + `Not passed`; Move happens in the modal (`onboarding.why_watch`, `note` carried from candMeta) | A2 |
| phase107 `pro_fill` | typed Note + clicked Move | promotes via the modal | A2 |
| phase107 §3 | RS-Leader promote `promoted_by ['rs']` | `promoted_by` empty; `onboarding.why_watch`; `rs_stars` Unrated | RS removed from screening |
| phase108 §B6b | NEW1 form memory (Note · Tier · ★) | memory check moved to the modal (`scr.why`, `scr.proven`, `scrMem`) | A2 |
| phase109 §3 | typed into `[data-td4-pro-note]` | clicks the summary line (form no longer has a Note) | A2 |
| phase111 width | `.csSh` evaluation sheet overflow | `.scrSh` screening sheet | evaluation sheet replaced |
| phase112 §3.5 | `td4ProFormHtml` contains `data-td4-pro-sector` | Sector ETF select lives in the modal (`[data-scr-sector]`) | A2 |
| phase113 §4.3 | ladder Add select lists Fortress-passed stocks only (`["", "FRTA"]`) | lists all Momentum-track stocks (`["", "FRTA", "NOFT"]`) | Fortress gate dropped (user decision) |
| phase113 §UI5 | "Compounder needs Fortress passed" block; Track select in the Candidate form (disabled Ladder until Fortress) | not blocked; Track chosen in the modal (no default) | same |
| phase114 | note-only interim promote form | `Screen ›` button + modal | interim rule replaced |
| phase33 | `[data-cs-sheet]`, `csEvalClose()` | `[data-scr-sheet]`, `scrClose()` | sheet replaced |
| New | `tests/run_tests_phase116.py` (65 checks): modal rules (Trend label by Track, only Pass counts, Fail stays a Candidate, exception path, Proven-only Compounder, legacy no-Track asks inline, carry of Track/Reasons/Note/Link/add date, onboarding timestamp), write failure keeps entries, draft survives refresh, Fortress gate gone, Ready rule (needs ① and ④, AI thesis ignored, archived/not-on-Watchlist blocked, RS never counts, save guard, edit mode unaffected, card editor, Onboarding Data card) | — | A2 + A5 |
Known failures also on main: phase45 (`_bk_id2/`), phase47 (`_bk_id3a/`).

## TEST STUBS (for the final review)
| Stub | Where | What it does | Who runs the real thing |
|---|---|---|---|
| `READY_STUB` | `tests/ff_stub.py` (appended to `FF_STUB` / `FF_STUB_BASE`, so every launcher gets it) | after `load`, replaces `wlReady(sym)` with `window.__READY_REAL ? realWlReady(sym) : true` | `tests/run_tests_phase116.py` (ready_tests) sets `window.__READY_REAL = true` and asserts it (`wlReady('NOT_ON_WATCHLIST') === false`) |
| `scr_helper.promote` | `tests/scr_helper.py` | drives the real screening modal via JS (`scrOpen` → set Proven/Trend/Why → `scrSave`) for legacy suites that only need a stock on the Watchlist | UI path tested in phase116 (screening_tests) |

## Step 5 — A6 Watchlist management
| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase64 | Filter ▾ panel groups `Idea · Tier · Phase · เรียง` / `Phase · เรียง` / `Idea` | now include `Track · Reason` (and `RS · Sort` on the Watchlist view) | new filter groups |
| phase85 | card ⋯ menu `✎ แก้ไข · 📥 Import · Export JSON · ทบทวน · ✕ ลบ` | `🗄 Archive… · ✎ แก้ไข · 📥 Import · Export JSON · ทบทวน` — `✕ ลบ` only shows for a stock with no My Thesis / AI thesis / notes / versions (the test stock has a thesis) | user decision (Delete only for typo tickers) |
| New | `tests/run_tests_phase117.py` (56 checks): status tags, Next check (row + sort), Last-updated sort, RS/Track/Reason filters (Unrated ≠ 0), "My Thesis updated … / AI Thesis imported | data as of …" lines, Archive requires a reason, archived hidden + `Archived (n)` + excluded from Today deep-dive queue, Restore, Delete visibility, Candidate rows show Track + Reasons and filter by Track/Reason | — | A6 |
| phase116 | added assertion that the real `wlReady` runs (stub off) | — | note 2 |

## Step 6 part 1 — Compounder = Momentum-layout card (strategy 'W' + track:'ladder')
Engine/data/status/sizing only; the Compounder *page* switch and ladder-page retirement are part 2. Stored `strategy:'L'` cards and ladder data are untouched.
| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase113 §4.1 (×3 FF levels) | "ladder budget starts at 5% of account × f% of the Compounder pool" (ladder form `cnLbud`) | **RETIRED** (`retired(...)`) | new Compounder plans no longer use the ladder-budget form; size = Base 1% of the Compounder pool, cap 5% of account (covered by phase118) |
| phase113 §UI4 | "+ New ladder: strat L only · no W/L choice · Ladder box shown · Winner box hidden" | **RETIRED** | ＋ in the Compounder scope opens the normal plan form with Track = Compounder |
| phase113 §UI5 | "+ New ladder lists Ladder-track stocks in Base/Sideways-Up only" · "+ New plan (Winner) lists Winner-track stocks only" | **RETIRED** | the ticker list shows all non-archived Watchlist stocks; Track comes from the Watchlist |
| phase113 §UI5 | "Momentum form + Compounder-track ticker → blocked ('use + New ladder')" · "Compounder form + Momentum-track ticker → blocked" · "Ladder form + Broken stock → blocked" | **RETIRED** | single rule: a new plan uses the stock's Watchlist Track (one stock = one track) |
| New | `tests/run_tests_phase118.py` (40 checks): Base 1% of the Compounder pool + cap 5% of account (banner + first-lot qty), Momentum unchanged, saved card = strategy 'W' + track 'ladder', scope switches to Compounder, per-track card lists, per-track holdings/pool split, DD bucket = ladder, 40W EMA status (green/yellow/red, empty = Stop only), cap on plan card, price sheet saves `emaW40`, legacy `strategy:'L'` data untouched | — | A8 |

## Step 6 part 2 — Compounder page = Momentum components; ladder page retired
Removed from the UI/code: `ldrHtml`, `ldrCardHtml`, `renderLadderPanel`, `ldrNew`, `ldrOpenSheet`, `ldrWatchAdd/Del`, `ldrStateSet`, `ldrDistSet`, `ldrToJournal`, the `#ladderPanel` host and the `scope-ladder` CSS rule. Kept: `ldrWlSet` (used by the Watchlist Track switch), stored `strategy:'L'` cards / `ladder*` fields / ladder settings, `coreLadderCalc` / `canPlaceLadder` (Calc tests untouched), `coreLCardHtml` (dormant). `core_size_test.js` unchanged (502/502).
Legacy `strategy:'L'` cards show as one read-only line on the Compounder page (`ticker · qty · avg · stop`, or `plan · stop` for an unbought plan) with no buy/cancel actions.
| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase113 §4.1 | "ladder budget starts at 5% of account × f%" (3 FF levels, `ldrNew` + `cnLbud`) | **RETIRED** (prints RETIRED) | see part 1 |
| phase113 §4.3 | header: Pool used/total, Free, Size chip (`[data-ldr-head]`, `[data-ldr-used]`, `[data-ldr-size]`) · Size 100/75/50 chip per FF level | **RETIRED** | ladder page header gone; FF/pool shown by the Momentum box and phase118 |
| phase113 §4.3 | ladder card: T1 bought / T2 waiting / T3 cancelled + progress dots; avg cost + `Exit: SL` line; buttons mark-bought / cancel-level / edit-zones | **RETIRED** | ladder-level table/card removed |
| phase113 §4.3 | `+ New ladder` button and Journal link; tap card → detail sheet; Mark T2 bought → ladder buy form | **RETIRED** | no ladder page / ladder buy form in the UI |
| phase113 §4.3 | Watching table: add-select (`#ldrAddSel`), state select Base/Sideways-Up/Broken, EMA20/50/200 distance fields; set state + EMA distance | **RETIRED** | Watchlist + Track filter replaces it; `ladder_state` / `ladder_dist` data kept (not rendered) |
| phase113 §4.3 | `scopeLadder` click → "ladder page shown, Winner/Sat panels hidden" | rewritten: Compounder scope shows `corePanel` with a Compounder head, no `#ladderPanel`; legacy ladder = read-only row without buttons; no overflow | A8 |
| phase113 §UI3 | ladder page: account chips on one line, header not overlapping, T1–T3 rows not clipped | **RETIRED** (overflow check kept as "หน้า Compounder") | ladder page gone |
| phase113 §UI4/§UI5 | legacy L card appears on the Ladder page | now: appears as a read-only legacy row on the Compounder page | A8 |
| phase113 §UI5 | opening from `+ New ladder` pre-fills the first eligible ladder stock | **RETIRED** | no ladder form |
| phase29 A3 | legacy L card: buy first level (`[data-ldr-buy]` / `coreLBuySave`) → trade `unplanned:false` | **RETIRED** | ladder buy UI removed |
| phase31 #14 | L cards not on Winner page, shown on the Ladder page (`[data-ldr-card]`) | now `[data-lf-legacy-row]` on the Compounder page | A8 |
| phase89 #3 | L plan card on the Ladder page with `T1 … SL …` | now read-only legacy row (`ZZZ … plan · stop`) | A8 |
| New | phase118 `page_tests`: Compounder page (Lean) = Momentum box/cards filtered by track, legacy read-only row (no buttons), Momentum page unaffected, `＋ แผน` opens "New Compounder plan" | — | A8 |
| New | phase117 `archive_warn_tests`: archiving a stock with an open plan → inline "Has an open position/plan — archive anyway?", button becomes "Archive anyway", second tap archives, the plan is untouched; stock without a plan archives in one tap | — | A6 add-on |
Pre-existing/known: phase23 (sync_core_size check), phase45/47/66/43 (missing backup folders) fail on main too. phase25 passed on a solo rerun after one load-related timeout in the parallel batch.

## Step 7 — A7 Today › Plans block
Plans (Momentum · Compounder · Sat; Draft | Open; ≤5 rows per group then "+N more ›"; empty groups hidden) takes the Satellite panel's position in Daily mode (Weekend unchanged). The Sat group keeps `data-td3-panel="sat"` + its risk chip; Core Port keeps its risk/pool lines; the old Core Port "drafts" section and `td3CoreDrafts()` are gone.
| Suite | Check / area | Change | Why |
|---|---|---|---|
| phase106 B1 | panel keys `ov · core · sat` (3 columns / stacked) | `ov · core · plans`; `rects()` counts only top-level panels (`[data-td3-panels] > [data-td3-panel]`) | Plans panel replaces the Satellite panel |
| phase106 B7 | "+n" expander expands remaining pending items | **RETIRED** | expander lives on the Sat plan card only |
| phase106 B7 | Saved row: `Entry 4,180 Size 0.3 lot SL 4,117 TP 4,300` one-line strip; strip font/one line/narrow hides SL/TP | now `Saved · Entry · SL · TP · Open ›` (no Size); strip checks **RETIRED** | one-line Sat row (user decision) |
| phase108 §5 | Today Sat row context line `Main · 4H · Long · Zone …` | **RETIRED** | context line only on the Sat plan card |
| phase108 §5 | Today Sat shows `Size 0.1 lot ×2` | row shows `Open · Entry · SL · TP`, no Size | same |
| phase109 §4 | "+n in the row expands the list, no navigation" | **RETIRED** | expander removed from Today |
| phase109 §B5b | Sat risk chip must not overflow `[data-td3-panel="sat"]` | measured against the Plans panel (`[data-td3-panels] > [data-td3-panel]:last-child`) | the Sat group sits inside the Plans panel |
| New | `tests/run_tests_phase119.py` (26 checks): Plans replaces old drafts; Open order red → yellow → green; archived-with-open-position still Open; Draft text (missing / Ready to enter); 5-row cap + "+1 more ›"; Compounder group; legacy `strategy:'L'` excluded; tap targets (`coreOpenCardOfTrade` for Open, `coreOpenCard` for Draft, "+N more" → Plan tab on the group's page); empty Momentum/Compounder groups hidden | — | A7 |
