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
