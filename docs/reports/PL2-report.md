# PL2 + PL2b — final report

Branch `claude/pl2` (based on `claude/pl1-phase-a` — PR #6 is not merged into main). Draft PR + merge are left to the user (see "PR" at the bottom). Files: `index.html` only (+ tests/docs). `core-size.js` untouched.

## 1. What changed

**Item 1 — Weekly Impact (Monday / Saturday)**
- Monday and Sunday already mapped correctly (a Monday-run doc for this Monday = current week, no warning). Saturday did show "ต่างสัปดาห์" for a run meant for next Monday → `wiCurMon()` now rolls forward to the upcoming Monday **on Saturdays only** (Weekly Impact only; `wpWeekKey`/Strategy weeks untouched). Import validation unchanged (week must be a Monday).

**Item 2 — "Unfinished today" banner** — `td4RemGo()` now navigates: Deep dive → Watch workspace of the pick (market switched); Cand→WL → first unscreened candidate + screening modal; New Cand → Add-Candidate input focused; Satellite → first outstanding Sat plan (Plan › Sat) or the Sat/Plans panel. Missing target → toast "Couldn't open X".

**Item 3 — My Thesis** — tab `มุมมอง` → **My Thesis** (one editor: ① Why buy, ④ Wrong if, Next check, What to check, Save, Archive) + chart images (add / view / remove, same stockNotes storage and viewer) + "Previous notes" (all legacy Event/Fund./Tech notes with tag + date). AI Thesis preview card beside it (wide) / below (narrow) with "imported <date>" / "data as of <date>" + **View AI analysis**; empty state keeps the existing Import action. The Watchlist card keeps only a read-only summary (status, Next check, ① first line) + "Edit in My Thesis ›". Legacy Event/Fund./Tech block removed from the Watchlist tab and Candidate cards (data untouched). Saving My Thesis never writes AI data; importing AI never touches My Thesis.

**Item 4** — Today panel label `Core Port` → `Selection` (nothing else renamed).

**Item 5** — Trade summary block in the Momentum/Compounder plan form: Entry · Size · SL · Risk (money + % of pool) · RS stars · reason tags, same values as the first-lot calc. Always shown (no "qualifies" flag exists, per decision D4); missing input → `Missing: Entry / SL / Pool / Risk budget / …`; RS unrated → `RS: Unrated`.

**Item 6 — Sat Verify** — Classify dropdown → two independently saved checkboxes **EMA50 Verify / Structure Verify** (`ema50_ok`, `structure_ok`). Both = Clear Trend, otherwise Unclear, used everywhere `classify` was read (badge, Tactical lock, readiness, Today status "Needs EMA50 + Structure verify"). Legacy plans keep using the stored `classify` until verification is saved through the new controls (never auto-ticked; "Legacy classification — verification pending" shown). Recorded trades never touched. An empty "unchecked" change event on an unsaved plan is ignored (found by the p80 regression run).

**Item 7 — Candidate-first**
- Ideas is no longer a required stage: the "already in Ideas" gate, "Back in Ideas" chips/panels, Ideas pill counter, the Today `idea-study` / `idea-recheck` reminders and the onboarding text are gone. The Ideas tab and all idea data stay; `idea-kill` / `idea-held` reminders stay.
- **One-time automatic Ideas → Candidates migration** (flag `settings.candFromIdeasDone {at, migrated, skipped, reasons}`, idempotent, additive, runs only after a server-confirmed Ideas snapshot): stock companies of counted ideas (`need_evidence`/`ready`, state ≠ park) with a symbol-like ticker; skips: no valid ticker · parked in idea · already in Watchlist · already a Candidate · previously deleted · thematic-only idea · idea status not counted. Migrated records: `manual:true, source:'From Ideas', idea_id, note`. Until the flag is set the old derived list is still shown (nothing disappears if the write fails). `satIdeas*` untouched.
- Tier A/B removed from selection UI: Edit-modal Tier box, Watchlist/Candidate chips + "ทบทวน", Candidate Tier row + filter chips, Tier warning on "add anyway", Deep-dive homework "Tier" part (5 → 4 parts). Stored tier data and old plans/trades are unchanged; new plans already used the single cap (PL1).

**Item 8 — Swipe zones (PL2b)** — global handler decides at `touchstart` from the start point only: portrait → bottom nav only; landscape → header strip (incl. sync status/nav area) or a visible outer gutter (≥ 8px of empty background outside `#mainWrap`). Detail-tab strips, `.ltTw` tables, `.ideaVc`, inputs etc. are never a start. A recognised swipe swallows the click that follows. Orientation read live via `matchMedia`.

**Item 9 — "เลือกศึกษา" (PL2b)** — *purpose / downstream effect confirmed*: the checkbox saves `user.pick[<segment name>]` in the Ideas doc (`ideaPick` → `ideaUserPatch`); its only consumer is `ideaExportObj()` which writes `chain.segments[].pick` for the idea-scout `pick` mode. It generates nothing inside the dashboard. *Changed per D8*: the checkbox shows **only the user's choice**; the AI's `segments[].pick` is shown as a separate **"AI pick"** chip (next to the existing "AI เสนอ" = `suggest`); export `pick` = user choice only (true only if ticked). Display only: ticked cards first (stable order in both groups), row scrolled horizontally to the card (no page scroll), order rebuilt from `user.pick` on reload, stored `chain.segments` and export order untouched. Helper `plAiPickStats()` (console) returns how many segments have an AI `pick:true` with no user choice — **real count not available to me** (no access to your Firestore); the test fixture gives 2/6.

## 2. What was verified
- New suites: `run_tests_phase362.py` (PL2 items 1–7, 69 checks), `run_tests_phase363.py` (swipe zones, **WebKit with iPhone UA/touch + Chromium mobile touch**, portrait 390×844 / landscape 844×390 / rotation, 27 checks each, all pass), `run_tests_phase364.py` (item 9, 26 checks).
- Full suite on this branch (2 parallel + solo reruns of failures): 123 suites, 12,158 checks passed, 18 suites still failing. **All 18 also fail on `main`** (main baseline on the same machine: 116 suites, 34 failing after solo reruns). They are the known environment/date failures (static "backup folder exists" checks in p41–p47/p66/p75, p13, p21, p23, p36, p5, p81, …) plus p80 (`6 แถวบัญชี`, also failing on the PL1-only base). I also compared failing check names of the shared failures: none new except p59/p64 expectation fixes made afterwards (re-run green). PL2b-only suites (363/364) and the Ideas suites (p41/42/44/46/49) were re-run after the last change; only the same static-backup failures remain. Logs: `/private/tmp/full/{pl2,pl2b,main}` (not in the repo).
- Every changed/retired expectation is in `tests/PL2_retired.md` (33 rows). `tests/make_verify.sh PL2` → `docs/reports/PL2-verify.txt`.
- Screenshots 390 / 1440 in `docs/briefs/PL2-screens/` (Today banner + Selection, My Thesis + images + AI card, Sat plan row, trade summary, Candidates + screening, Value Chain order).
- WebKit (78 MB) was downloaded into the Playwright cache to run the swipe tests.

**Only a real iPhone can confirm** (checklist for you): (1) a swipe starting in the 16px landscape gutters — iOS may take the Safari back/forward edge gesture instead (as agreed, no workaround); (2) swipe from the bottom nav near the home indicator; (3) momentum/rubber-band feel while scrolling the Value Chain row and Evidence table, and that a diagonal start inside them never changes the tab; (4) a rotation mid-gesture; (5) that a swipe ending on a button never taps it on real touch; (6) Safari URL-bar collapse does not change which zone is "bottom nav"; (7) My Thesis image viewer (pinch/zoom) on a real TradingView snapshot (emulation used placeholders).

## 3. Unresolved trading-rule / product decisions
1. **Daily-goal numbers changed**: removing the Tier part makes the Deep-dive homework 4 parts, so Daily goal totals (e.g. `10/15 → 9/14`) and past-day percentages (e.g. 60% → 57%) shift. Old routine logs are not edited (stored `tier` entries are ignored). Confirm this is acceptable.
2. **Plan-card `Tier…` button** (existing plans) and **Settings › Tier criteria / tier caps** were kept: legacy plans still size from their stored tier. Remove them too, or keep until legacy plans are closed?
3. **Sizing for new plans** was already tier-free (PL1: `CS_CAP_KEY='A'`); nothing in PL2 changed sizing math.
4. After the one-time migration **new Ideas never feed Candidates automatically** — Candidates are added manually (or by re-running the migration, which I did not build). OK?
5. Migrated Candidates have **no Ideas source info**, so the "＋ เพิ่มเข้า Watchlist" button on the Candidate card is disabled ("no confirming source"); promotion goes through Evaluate (screening modal). Intended?
6. Candidate cards **no longer show the old Event/Fund./Tech notes** (data kept; visible in My Thesis after promotion). Needed earlier?
7. Watchlist rows now show the **market chip** where the Tier chip used to be; the worst-case row (long alerts + phase + 3 dots) wraps its dots to a 2nd line at 355px (`run_tests_phase94` relaxed to ≤ 2 lines).
8. Saturday Weekly Impact roll-forward (D1) applies only to Weekly Impact; Plan/Strategy weeks still use Sunday-start keys.
9. Existing Ideas with AI `pick:true` and no user choice will export `pick:false` from now on (per D8) — re-tick what you want studied.

## Migration numbers
Real migrated / skipped counts are written when the app first loads after the update: `settings.candFromIdeasDone` and a console line `PL2 Ideas→Candidates migration: {…}`. Fixture run (test 362): migrated 2, skipped 7 (parked 1, invalid ticker 1, already in Watchlist 1, already Candidate 1, previously deleted 1, thematic-only 1, idea not counted 1).

## PR
`gh` is not installed here and the standing rules say no push, so the Draft PR was **not** created. To create it: `git push -u origin claude/pl2` then open a **draft** PR `claude/pl2 → claude/pl1-phase-a` (or → main after PR #6 merges). Suggested body = this report. Do not merge.
