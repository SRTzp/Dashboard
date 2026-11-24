# HF3 — Place order Confirm "does nothing" · RRG job never saves (index limit) · RRG says why it is slow

Branch from fresh origin/main (after MV1 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-hf3 -b claude/hf3 origin/main`. First commit = this brief. UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md` (rule 9: a blocked state names the fix; rule 11: iPhone 390).

## A · Bug: Sat Place order → Confirm → nothing happens (SRTp 24 Nov, Short XAUUSD)
Cause found in review: every block path in `pb2PlaceYes` (~30361) returns early with `re1Toast(...)` → `sdToast`, whose `.sd-toast` has `z-index:80`, while the sheet backdrop `.ui-sheet-backdrop` is `z-index:200`. The sheet stays open and the message is drawn UNDER it → the user sees nothing. Paths: `sdWrongOf`, `re1SatBlocks`, re-entry not confirmed, `efPickEnsure` (`{ok:false, full:true}` with no msg when this week already has `SAT_WEEK_PICK_MAX = 3` picks and the asset is not one of them → "Could not update this week's picks").
Fix:
1. All toasts above sheets: `.sd-toast`, `#td3Toast`, `ln4Toast` and any other toast element → z-index above every sheet/overlay (e.g. 10050). Test: a toast shown while a `.ui-sheet-backdrop` is open is on top (elementFromPoint at the toast centre = the toast).
2. Inside the Place order sheet, a block never leaves the user guessing: show the reason as an amber line right above Confirm (`⚠ <reason> · <Fix ›>`), keep the sheet open. Toast optional on top.
3. Picks full: the line reads `⚠ This week already has 3 Sat picks · Replace one:` followed by one small button per current pick (`Replace BTCUSDT`, …). Tapping one = that pick is swapped for this asset and the order is placed in the same tap (use the existing `repC/repI` + `efPickEnsure(i, key)` path). No browser confirm().
4. Same treatment for the Core sheet `efCorePlaceYes` (check its early returns; any silent `return` that the user can reach after pressing Confirm must show a line).
5. Uncaught error guard: wrap the body of `pb2PlaceYes` / `efCorePlaceYes`; on exception show `⚠ Could not record the order · <short error>` in the sheet and `console.error` the full error (no more silent stop).
Tests (new `tests/run_tests_hf3.py`): each block path (wrong side, engine block, re-entry, picks full) → visible line in the sheet + sheet still open; picks full → Replace swaps the pick and records the order; a thrown error → error line; happy path unchanged (Order working ✓). Short and Long both.

## B · Flow RRG: say why tails are slow / missing (no silent fallback)
`ux3RrgJob` (~25471) falls back to Twelve Data silently on any read error (`console.warn`) — e.g. Firestore rule missing for `users/{uid}/rrg/bars` (permission-denied), doc missing, or doc older than 1 trading day. Make the reason visible in the existing RRG status line (one line, no new card):
- permission-denied → amber `⚠ Can't read the job's RRG data · add the Firebase rule for rrg (see Settings) · loading from Twelve Data…`
- doc missing → `No RRG data from the 05:30 job yet · loading from Twelve Data…`
- stale → `Job data from <date> (old) · loading from Twelve Data…`
- Partial doc: today `rrgJobOk` rejects the WHOLE doc if even one of `RRG_SYMS` is missing (the job writes a `missing` list). Change: accept the doc when SPY + at least 80% of symbols are there; draw those tails now, and only the missing ones (if any) come later from Twelve Data. Status line adds `· no job data for XHB, JETS` (names, wrap, no "…").
- Twelve Data path: show progress `Loading 8 / 25 symbols…` while batches run (it already batches 8 with 61 s waits).
Settings (the data / backup section that exists today): one short help block with the exact rule to paste (copy button):
`match /users/{uid}/rrg/{doc} { allow read: if request.auth != null && request.auth.uid == uid; }`
Test: mocked get() rejecting with code `permission-denied` → that line; missing doc → that line; doc with 2 symbols missing → the other tails draw from the job + that line; fresh doc → tails from job, no Twelve Data call (existing test keeps passing).

## C · ROOT CAUSE of slow RRG: the job's write fails every run
Live log (24 Nov, `build_prices.py`): `rrg bars failed: 400 too many index entries for entity /users/…/rrg/bars [reason: "INDEX_ENTRIES_COUNT_LIMIT_EXCEEDED"]`. Firestore indexes every array element; 25 symbols × 800 bars × (c + h) + dates ≈ 41k > the 40,000 per-document limit. So `rrg/bars` has never been written and the app always falls back to Twelve Data. The selftest missed it (fixture = 500 bars).
Fix in `scripts/rrg_bars.py`:
- Store the bulk as JSON strings: `dates` → `datesJ` (string), `syms` → `symsJ` (string of `{SYM:{c:[…],h:[…]}}`). Keep small fields (`v` bump, `asOf`, `bench`, `bars`, `missing`, `at`) as normal fields. One string field = 1 index entry; doc size stays well under 1 MB (check).
- App (`rrgJobGot` / `rrgJobOk`): read `datesJ`/`symsJ` when present (JSON.parse in try/catch), else the old shape. Bad JSON = treated as "doc missing" line from part B.
- Selftest: build the doc with the REAL bar count (`RRG_CFG.bars`, 800) for all 25 symbols and assert (a) estimated index entries < 2,000 (count array elements + map keys of non-string fields), (b) JSON size < 900 KB, (c) round-trip app-side parse gives the same rows as before.
- Job log stays green when only RRG fails (as today), but print `rrg bars FAILED` in capitals so it is easy to spot.
After merge SRTp runs the `prices` workflow once by hand → log must show `rrg bars: 25 symbols · 800 bars · asOf …` and Flow tails draw instantly.

## Screenshots (only `hf3-*.png`)
`hf3-place-picks-full` (1440 + 390), `hf3-place-blocked` (390), `hf3-rrg-denied` (1440 + 390), `hf3-rrg-loading` (1440).

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks after the last change · revert tracked screenshot rewrites · new suite in REST= · no push until I review — report tests, judgment calls, PNG list.
