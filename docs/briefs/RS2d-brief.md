# RS2d — Screen presets editable (Leaders / Emerging / Pullback) + Reset to default

Branch from fresh origin/main. Mockup: `docs/briefs/nt2c/nt2c-rs2d-mockups.html` (section 3). UIUX lens applies.

## Today's code (found 22 Nov)
- `index.html` ~31889: `RS2_PRESET_DEFAULTS` (leaders `rs12Min 80, near 15` · emerging `m3Min 90, m1Min 90, rs12Max 85` · pullback `rs12Min 85, m3Min 80, m1Max 60, near 15`), `rs2Presets()` already merges an override from `localStorage 'dash.rs2Presets'` — there is NO UI for it.
- `scripts/build_rs2.py` ~146: `PRESETS` hard-codes the same numbers; used for (a) which names get an earnings-date lookup (EARN_CAP 300) and (b) the change alerts `b left Leaders · d new Leader · e new Emerging` (~419–442).

## Build
1. **Edit rules UI (Screen tab):** a small `Edit rules` link next to the active preset's rule line (`rs2PresetText`). Opens a sheet: preset chips `Leaders · Emerging · Pullback`, one labelled number input per rule in plain words (e.g. `12M RS at least`, `Within this % of the 52-week high`, `3M RS at least`, `1M RS under`), allowed range shown, live `Now: N match (was M with the default)`. Buttons: `Reset to default` (quiet link, per preset, restores the ORIGINAL defaults above — SRTp requirement), `Cancel`, `Save` (dark).
2. A preset with any custom value shows a small grey `custom` tag on its chip and rule line; Reset removes it.
3. **Storage:** save the overrides to the user's existing settings document in Firestore (same place as other dashboard settings; sync across devices) and mirror to `localStorage 'dash.rs2Presets'` (read path unchanged). If saving there needs a Firestore rule change, STOP and report the exact rule before building that part.
4. Validation: integers, 0–99 for RS, 1–50 for %; empty = default; invalid → inline amber hint, Save disabled.
5. **Today alerts must agree with the Screen.** Investigate how `b / d / e` reach the app. Preferred: the job also writes yesterday's raw values per row (`r, o, m1, m3`), and the app recomputes b / d / e with the user's presets; the job's own b / d / e become the fallback when no custom presets exist. If that is not practical, report the options before coding.
6. **Earnings lookups:** make `build_rs2.py` pick names with a looser envelope (e.g. RS ≥ 70 or 3M ≥ 80, still best RS first, cap 300) so edited presets still have earnings dates; keep a comment that the app's defaults live in `RS2_PRESET_DEFAULTS`.

## Tests (`tests/run_tests_rs2d.py`, add to REST=)
Edit + Save changes the match count and persists after reload; `custom` tag; Reset restores exact defaults and removes the tag; invalid input blocks Save; Today b/d/e follow the custom Leaders rule on a fixture; job selftest for the looser earnings envelope (`tests/rs2_selftest.py`).
One full `JOBS=2 bash tests/run_regression.sh` after the last change · hooks PASS · only `rs2d-*.png` in the diff · screenshots `rs2d-edit-sheet`, `rs2d-custom-tag`. No push until reviewed.
