# EF1b notes

## phase373 (run alone)
- origin/main: 419 pass · 1 fail — `[390] crashed :: Locator.click: Timeout 30000ms exceeded`
- claude/ef1b: 422 pass · 1 fail — the same `[390]` timeout (failing set identical; +3 = new EF1b assertions)
- Two phase373 assertions were updated for EF1b: level place goes through the confirm sheet; a multi-level plan no longer waits for Setup, so it shows its 3 entry legs on the PV card.

## TS1 (249e74f) — readers whose writer was removed
- **tvSetup** (writer `tv1SetupToggle`): readers `tv1SetupAt` / `tv1SetupLeft` → `ln4CoreChecks` (the bug, fixed here: now written by the Place confirm sheet), Watch sort `tv1`-section ("Setup ✓" vs "Watchlist"), LN4 stats.
- **ln4 flags `starterOff` / `starterFeatureOff` / `stage`** (writers `ln4SetStarterDef`, `ln4SetFeature`, `ln4SetStageManual`): readers `ln4Feature` / `ln4Stage` etc. remain; the values can no longer be changed, defaults apply.
- **stockNotes `phase`** (writer `phSet`) and **`tier` / `tier_set_at`** (writer `tqSet`): readers (`tqCode`, phase/tier filters and chips) remain; no UI sets them any more.
- **`keep_until`** (writer `tv1KeepMore`): only a comment still mentions it (reader `tv1DropDue` also removed) — harmless.
- **`ladder_watch_set`** (writer `wlTrackSet`): reader `wlTrackOf` remains; flag is still derived on read from the doc, harmless.
- **Watch view filters `wlTrackF`, `wlReasonF`, `wlRsF`, `wlSortMode`, `wlShowArch`, `wlHotFirst`** (setters removed): readers remain, always the default value.
- Test-harness note: `tests/re1d_common.py` stubs `tv1SetupLeft = ()=>1`, which hid the Setup bug in every suite built on it.
