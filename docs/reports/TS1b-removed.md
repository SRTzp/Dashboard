# TS1b · B — removed from index.html (Watch clean-up)

No stored field was deleted or migrated. Readers/normalisers that only *preserve* a stored field (e.g. the `wlStart` parse of `rs_stars` / `rs_rated_at`, the stored `plan.starter` read by the sizing adapter at `re1` call sites) stay so that old data round-trips untouched.

## Functions removed
**RS rating stars** — `wlStarsOf`, `wlStarHtml`, `wlStarSet` (+ `.wl-star`, `.wlRsSel` CSS); the star ranking in `td4HwNextWlPick`; the `RS ★` cell in `csSummaryHtml`.
**LN4 Starter / Stage (gated by `ln4Feature()`)** — `ln4Feature`, `ln4Stage`, `ln4Frac`, `ln4StarterDef`, `ln4StarterOn`, `ln4StarterSplit`, `ln4StarterIn`, `ln4StarterRowHtml`, `ln4SatStarter`, `ln4SatStarterSet`, `ln4SatStarterRow`, `ln4TradeStarter`, `ln4Ladder`, `ln4LadderBadge`, `ln4LadderTip`, `ln4SetStage`, `ln4AddOn`, `re1TrainingOn`, `re1SetTraining`; `LN4_FRAC`, `LN4_FRAC_TXT`; Settings › Training (Starter ¼) row; Journal `Starter ¼` / `Full` filters; the `Stage n` label in the week row; the Act-header ladder badge; the Starter add-on row in the plan form, the `starter` / `sfrac` fields of the new-plan state, `snap.starter`, `stOn` / `addPx` paths in the sizing preview; the Today "add-on condition met" reminder (`wl1ao`, only reachable with Starter on). The one-off `starterFeatureOff` write in `re1Ensure` is removed (the value already stored stays).
**Stock phase / tier readers** — `phApply`, `phChipHtml`, `phMenuToggle`, `phSave`, `phKey`, `phOf`, `phStale`, `phGoWl`, `phCoreChip`, `phCoreWarn`, `phCoreWarnText`; `tqApply`, `tqGroup`, `tqCode`, `tqSave`, `wlTierChips`; `PH_DEF`, `PH_KEYS`, `PH_LBL`, `PH_ORD`, `PH_STALE_DAYS`, `phFilter`, `phSort`, `phMenu`, `tqFilter`; the `phase` normaliser in `stockNotes` reads; `.phChip` / `.phMenu` CSS. (`tqOf` / `tqCarryOf` stay: they carry an existing tier onto a new Watch row.)
**Watch filter / sort state without a setter** — `wlMatchF`, `fltClear`, `fltOpen`, `FLT_TIER_NAMES`, `wlTrackF`, `wlReasonF`, `wlRsF`, `wlSortMode`, `wlHotFirst`, `wlShowArch` (replaced by the new Archived state in C).
**Comment** — `keep_until` removed from the candMeta comment (no code read it).

## Verification
`grep` over the remaining `index.html` for every name above: no reference left (script in the TS1b-summary). Node suites unchanged: risk_engine 313 · re1_adapter 63 · re1c_live 88 · core_size 502 · ps1_size 41 · ps1b_size 44 · pv1_posview 44 · sync checks OK.

## Left on purpose (flag)
- Sizing adapter still honours a stored `plan.starter` (`re1` call site, `wl1` fill-qty maths, `bd` size text): changing that would change sizing for any old plan. No UI can create one any more.
- Plan board add-on pill machinery (`flags.addon`, `bdAddon`) is now never triggered; kept to avoid touching the board in this job.
- `re1DryMount` still reads `ln4Cfg().starterOff` (Settings dry-run input); sizing unchanged.
