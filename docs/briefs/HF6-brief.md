# HF6 — URGENT: account saves fail ("Nested arrays are not supported") · repair XAU dangling order · make save failures visible

Branch from fresh origin/main: `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-hf6 -b claude/hf6 origin/main`. First commit = this brief. Small + urgent: when tests pass, commit, push, give the PR link. Runs BEFORE E2E1 and HW2.

## What SRTp saw (25 Nov, Safari console, live)
`firestore set error: FirebaseError [invalid-argument]: Function DocumentReference.set() called with invalid data. Nested arrays are not supported (found in document users/<uid>)` from `doPersistImpl` (~10559).
Console check of the active XAUUSD Sat idea `i1795527402088` (Main): `accts.main = {lot:0.11, trade_id:'t1795561345680_main'}`, `ln4.placedAt 2026-11-24T23:02:22Z`, but **no trade with that id in getBook('main').trades** → `pb2Filled` → `sat7dMarkOpen` finds no trade → silent `return` → "Filled does nothing".

## Cause (found in review)
RRG rows carry `tail = [[ratio, mom], …]` (LR4 B, `rrgCompute` ~25287) — an array of arrays. Rows are stored in the fund-flow state (`ffState().rrg.rowsD/rowsW`, persisted with the account book or `settings.flowShared`). Since HF3/RR4 the rows are built on every Flow open from the job data, so every later save of that account's book is rejected by Firestore client-side validation → nothing saved (trades, plans in the book, settings) on that device since then. The satIdeas collection is a separate doc, so the idea kept its `trade_id` while the trade itself was never saved → dangling.

## Fix
1. **Store tails without nested arrays.** Keep `tail` in memory for drawing, but never persist it as `[[a,b]]`: persist as a flat list (`tailF:[a1,b1,a2,b2…]`) or objects (`[{r,m}]`) and rebuild on read; `lr4Pts` reads both. Simplest acceptable: strip `tail` from rows before they go into the persisted state and recompute/keep it in a non-persisted cache.
2. **Clean on load:** when state loads, remove any `tail` (or other nested array) already sitting in fundflow / `settings.flowShared` / any account book, so the next save succeeds.
3. **Save guard (permanent):** before every Firestore `set/update` the app does (doPersistImpl, saveBook, sat7dWrite, coreWrite, settings writes), run one `fsSafe(obj)` check: nested arrays (and `undefined`, NaN, Infinity) → fix where safe (drop the field) + `console.error` with the exact path. Never let one bad field block the whole account save.
4. **Visible failure (rule 9):** if a save still fails, show a red-free amber bar at the top: `⚠ Not saved · <short reason> · Retry ›` (stays until a save succeeds). Today a failed save only logs to the console — that is why this went unnoticed for hours.
5. **Repair dangling Sat orders:** on load and in `pb2Filled`, if `accts[acc].trade_id` points to a trade that does not exist in that account's book → treat the slot as having no trade (clear `trade_id`, keep `lot`/`ln4.snap`) so Filled creates the trade again from the plan + order snapshot. Filled must never return silently: any refusal shows the reason line (as HF3).
6. Strict test mock: reject nested arrays exactly like the SDK (extend HF4's undefined check) so this can never pass tests again.

## Tests (`tests/run_tests_hf6.py`)
- Flow open with job RRG data → persist succeeds under the strict mock; tails still draw; reload → tails still draw (rebuilt).
- Old state containing `tail:[[…]]` loads → cleaned → next save succeeds.
- `fsSafe` drops a nested array / undefined / NaN and logs the path; the rest saves.
- Forced save failure → amber "Not saved · Retry ›" bar; Retry after fix → bar gone.
- Dangling Sat slot (trade_id missing in book) → Filled → trade created, status open, Manage row shows; no silent return.
- Regression of HF4/HF5 suites.

## Rules
Full `JOBS=2 bash tests/run_regression.sh` + hooks · only `hf6-*.png` (the Not saved bar 1440 + 390) · commit, push, PR link. Report: which writes were failing (all paths the guard caught in the full run), and confirm nothing else in state has nested arrays.
