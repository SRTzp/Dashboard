# WK1 — Weekend steps in routine order + per-item news read (overnight run, 2026-11-08)

Branch `claude/wk1`, **stacked on `claude/tx1`** (uses TX1's `--read-fs/--read-lh`). Mockup `docs/briefs/wk1-mockup.html` (untracked) followed.

## §0 Audit
**Weekend model** (`td3WeekModel` / `td3WeekRow` / `td3WeekPanel`, index.html): 7 items in 3 panels — Overview: `wk_macro` (manual), `wsector` (manual, not counted); Core: `wk_news` (auto = latest edition read), `wk_cands` (manual), `wk_picks` (manual); Sat: `wk_impact` (auto = `wiCurDoc()`), `wk_assets` (auto = ≥1 pick or "Not trading this week"). Badge = n/6. Manual ticks → `settings.weekLog[Monday].done[]` (`td3WeekTick`, 26 weeks kept, `glWeekDone`). Panel rendered by `tdHtmlLean` (`P('ov'|'core'|'sat')`).
**News read state:** `settings.stockNewsRead = {editionId: true}` (`stkReadMap/stkIsRead/stkMarkRead`, 12 editions kept). `stkModel(doc)` item = one stock per edition (`doc.stocks[ticker]`; **no per-item news id**) → key = edition id + ticker (pre-approved fallback).
**Data available:**
- Open positions with stop < avg entry: `getBook(id).trades` (`status:'open'`, `entry`, `sl`, `bias`) per account; `posOpenRisk(t).locked` already encodes "stop at/above entry (Long) / at/below (Short)" → N = open trades with `sl>0` and not locked. Trades with no `sl` can't be judged → not counted and the sub-text says how many (pre-approved fallback).
- Ideas this week: `ideaList[].imported_at` (ISO) via `td4IdeaStamp`; counted when its ICT date is Mon–Sun of the current week. (A re-import of an older idea stamps `imported_at` again, so it counts as imported this week.)
- Macro Playbook `change_if` hit status: **not stored** — `change_if` is free text per asset; the only trace is a *past* version's `reason.type:'trigger'`. → ⑦ is a **manual tick** (pre-approved fallback); the red "change_if hit: <asset>" path is not implemented.

## Plan (8 bullets)
1. Backups `index.backup-pre-WK1.html`, `tests/_bk_wk1/`.
2. New Weekend model: 7 counted items ① Weekly Impact ② Pick assets ③ Read stock news ④ Review Candidates/Watchlist ⑤ New ideas x/2 ⑥ Raise stops ⑦ change_if.
3. One panel `Weekend review · n/N done · ~45 min` + progress bar + numbered rows with SAT/CORE/OVERVIEW tags; keep ② chips + "Not trading this week".
4. ①/③ missing data → inline `Copy prompt ›` (clipboard text starts `weekly-impact:` / `weekly-stocks-news:` + manifest JSON) and `Paste JSON ›` (opens the existing paste sheets); hidden once data exists.
5. Per-item news read: `stockNewsRead[ed] = {readIds:[tickers]}`; old `true` = all read (no migration; expanded on first un-tick).
6. News sheet: ✓ toggle per item, read items fade, `Unread | All` (default Unread), `Mark all read`, empty Unread → `All read ✓ · Show all`, body text on TX1 tokens.
7. Daily line → one `<button>` `● Weekly News · x/y unread ›` (same spot/size); hidden when all read.
8. Tests: new `phase366` (86 checks) + retire/adjust old B4 (106), 102, 362.

## Decisions
- Pre-approved: per-item key = edition + ticker; ⑦ manual tick; positions without a stop counted out + said in the sub-text.
- ④ merges `wk_cands` + `wk_picks`: tick stores `wk_cands`; an old `wk_picks` tick still shows ④ done; un-tick clears both.
- Removed ids: `wk_macro`, `wsector`, `wk_picks` (logged in `tests/WK1_retired.md`).
- ⑤ and ⑥ are hybrids: auto-tick (no tick button) when satisfied (≥1 idea / N=0), otherwise a manual tick button. All 7 items count in n/N.
- Short trades mirror ⑥ (stop above entry counts; at/below is locked).
- "Weekly News" Daily line keeps `Hidden when all read`; an edition with 0 items is not auto-read (needs Mark all read, which stores `true`).
- Mark all read stores the current item tickers (so tickers added to an edition later show as unread).
- Weekend panel max width 760px on wide screens (single column).
- Not done / flagged: the news sheet header `Mark all read` wraps to its own line at 390px (cosmetic).

## Tests
- New `phase366`: **86/86** (390 + 1440) — order/tags/header/bar/badge, ⑤ Mon–Sun ICT boundaries, ⑥ fixture (stop<avg, =avg, >avg → N=1; multi-account; no-stop; Short), ⑦ manual, Copy prompt/Paste JSON only when missing (+ prompt text, paste sheet), news ✓/untick/filter/Mark all/Show all/reload/legacy flag, ③ and Daily-line counts, Daily line is one `<button>` (click + Enter + Space), hidden when all read, no overflow/console errors.
- Related suites: 106 (155), 102 (54), 108 (130), 365 (68), 99 (122), 15 (85), 116 (67), 362 (69 after retire) all pass; **105: 186 PASS then a Playwright timeout (`[data-sd-hd="IGV"] .l2 .g` click) → exit 1, 0 FAIL lines** — identical (`fail 1 0 186`) in the previous full run `_to_delete/runall2/final.tsv`, so pre-existing, not caused by TX1/WK1. `check_syntax` OK · core_size 502/502 · sync OK. No full suite (as instructed).
- Retired/changed: `tests/WK1_retired.md` (8 rows). Verify file `docs/reports/WK1-verify.txt` (via `tests/run_related.sh`).
- Screenshots (git-ignored, `tests/screenshots/`): `wk1-weekend-{390,1440}`, `wk1-weekend-dark-*`, `wk1-news-*`, `wk1-news-dark-*` (app has no dark theme, so dark = `prefers-color-scheme` emulation, identical).

## Compare URL (stacked on TX1 — merge TX1 first or compare against it)
https://github.com/SRTzp/Dashboard/compare/claude/tx1...claude/wk1?expand=1
