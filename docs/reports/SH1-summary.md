# SH1 — Flow data shared across accounts

## What moved now (Flow only)
`state.fundflow` (per-account book) → **`settings.flowShared` on the home account** (`tdHome()` = first account, "Main").
Covers l1 / l2 / ctx / dials, QE/QT note + history, log, themesCol, rrgTf, and the whole `rrg` cache (rowsD / rowsW / day / at / pending / err).

**Why home-account settings (not a user-level doc like `weeklyImpact`):**
- No Firestore Rules change needed (a new collection fails with "permission" until rules are deployed — see the weeklyImpact error text).
- Same document as `books`, so one snapshot syncs everything, and backup/restore already carries it.
- Same pattern already used for goals, ln4, candMeta, sectorNotes, newsRead, tvInfo… (written via `saveBook(home)`).
- Cost: writes rewrite `books.<home>` as a whole (rrg rows ride along). Acceptable; it is what the old per-book field did anyway.

**One-time migration** (`ffSharedMigrate`, runs only after the server snapshot is confirmed, never from cache):
- whole object = Main's `state.fundflow` (default if Main has none);
- `rrg` = the account whose `rrg.at` is newer (only if it has D or W rows).
- Old `state.fundflow` in every book is **left untouched and no longer read** (verified in test: Main/Family old notes unchanged).
- Before server confirmation `ffState()` returns a transient copy and `rrgRefresh` / `rrgAutoOnce` do not run, so a stale cache can't be written over the server.

All 6 `schedulePersist()` calls in Flow code → `ffPersist()` (marks the home book dirty, from any active account).

**Test:** `tests/run_tests_sh1.py` — 1440 + 390, all pass: migration picks Main's note/ctx/log and Family's newer RRG; switch Main→Family shows identical strip / RRG rows+dates / manual items; edit in Family shows on Main; stored once on home; old fields untouched; no console errors.

## Audit of other per-account fields (NOT moved — need your approval)

Top-level book fields:

| Field | Today | Class | Proposed | Note |
|---|---|---|---|---|
| `trades` | per-account | **per-account** | keep | money / trades |
| `settings.capital, fx*, strategicCash, limits, posTier, psRisk, coreRisk, satRisk, costSettings, equitySnapshots, cashFlows, pools, ladderMaxAcctPct, riskEvents, brokers, reserved, satV2, satPyrSplit` | per-account | **per-account** | keep | money / risk |
| `settings.fx, fxAuto, fxUpdatedAt` | per-account copy, fetched per book | shared (market rate) | move (low priority) | two books can show different FX |
| `settings.rsBench` | per-account | shared (research) | move | |
| `industries` | per-account | **shared** | move | research labels |
| `industryLinks` | per-account | **shared** | move | packet links per industry |
| `reasonTags` | per-account | **shared** | move | trades snapshot the label, so old trades stay readable |
| `exitReasons` | per-account (legacy, migrates into `reasonTags.exit`) | shared | move with `reasonTags` | |
| `scoreLabels`, `scoreCriteria` | per-account | **shared** | move | checklist wording |
| `journalView` | per-account | shared (UI pref) | move | |
| `fontSizes` | per-account | UI pref | shared, or per-device (localStorage) | your call |
| `tabsOffset` | per-account | UI pref | per-device would suit better | your call |
| `watchSortMode`, `watchCollapsed` | per-account (no live readers found by grep of `state.*`) | UI pref | shared, or delete as dead | |
| `watchlist` | already shared (`users/{uid}/watchlist`, 7W) | shared | done | legacy key in CL2A_DROP_KEYS |
| `sat_since` | per-account | per-account | keep | no readers found; likely dead |

Already on the home account (shared in effect, nothing to do): `candMeta, candReasons, candAddLog, subGoals, goals, goalLog, weekLog, weekTasks, dailyExtra, routine/routineLog, satWeekPick, satAssetCfg, satCustomAssets, sectorNotes, tvInfo, tvSetup, newsRead, newsEvents, ln4, satPbLink`.

**Suggested next step:** SH2 = move `industries, industryLinks, reasonTags(+exitReasons), scoreLabels, scoreCriteria, journalView, rsBench` to a `settings.shared*` block on home with the same migrate-once rule (Main wins; for lists, union). UI prefs (`fontSizes, tabsOffset, watchSortMode, watchCollapsed`) and FX: tell me per-device vs shared.

## Full regression (after SH1)
`tests/run_regression.sh` now includes `run_tests_sh1`. Full run: **48/48 ok · 0 failing** (2510 s). Failing set: empty. `run_tests_sh1`: 14 checks pass · 0 fail.

---

# SH2 — shared labels / industries / FX (approved)

## Moved to `settings.shared` on the home account
`industries · industryLinks · reasonTags (+legacy exitReasons) · scoreLabels · scoreCriteria · journalView · rsBench · fx · fxAuto · fxUpdatedAt`.
Same mechanism and reasons as `flowShared` (SH1). Code reads/writes via `sh()`; a hook in `schedulePersist` (`shSyncDirty`) flags the home book dirty whenever `settings.shared` changed, so every existing edit site persists without per-site changes.

**Migrate once** (after server confirmation, after the reset gate): single values = Main's (next account if Main has none); lists = union, Main first (industries case-insensitive; industryLinks Main wins on clash; reasonTags union by tag id, Main's label wins; legacy `exitReasons` folded into `exit` when an account has no `reasonTags.exit`). Old fields in every book are left as stored and no longer read.

## Per device (not synced)
`fontSizes` + `tabsOffset` → `localStorage['dash.devUi.v1']`, seeded once from Main's stored values; no longer written to Firestore.

## Removed dead code (stored data untouched)
`watchSortMode` / `watchCollapsed` normalisation and defaults (`defaultWatchSortMode`) removed from the book builder; `{...d}` still carries any stored values through.
**`sat_since` was NOT removed:** it is live (Sat "start counting trades" setting, read at `B.sat_since` in the Sat stats and shown in Settings). My SH1 audit said "likely dead" — that was wrong.

## Deviation to know about: FX
`settings.fx` is read in 20+ places per account (engine adapter, snapshots, pos sizing …). Instead of editing all of them, the shared FX is **overlaid onto every account's in-memory `settings.fx/fxAuto/fxUpdatedAt`** (`shApplyFx`), and edits (Settings save, auto-fetch) push back to `shared` (`shFxPush`). Consequence: an account's *stored* `settings.fx` is rewritten with the shared value the next time that account's book is written, so "old fields untouched" holds for everything except these three FX values. Source of truth is `settings.shared.fx`.

## Bugs found by the regression and fixed
- Migration wrote to Firestore **before** the CL2-a reset gate was confirmed (phase19) → migrations now wait for server confirmation and a passed gate.
- Migration ran lazily on the first account switch, dirtying/writing the home book on a plain switch (phase10) → now runs once at load.
- `acctBuildBook` temporarily swaps `state`, which made `sh()` create `shared` on the wrong account → the ensure* calls there were removed (they no longer touch the book).
- phase20 tests updated to the new location (`settings.shared.reasonTags`, `sh().industries`).

## Tests
`tests/run_tests_sh2.py` (in `run_regression.sh`), 1440 + 390, 28 checks: union/Main-wins for industries, links, labels, criteria, reason tags; FX identical and equal across accounts; switch account → same labels/industries/FX; edits in Family show on Main; stored on home only; old fields untouched; font size seeded from Main, per device (a second browser context keeps 0.9 while the first is 1.3), not written to Firestore.
**Full regression: 49/49 ok · 0 failing · 1121 s.**
