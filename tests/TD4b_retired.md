# TD4b — expectation changes (none deleted or weakened; each follows a behaviour change in the brief)

| # | Test | Change | Why |
|---|------|--------|-----|
| 1 | run_tests_phase107.py (§3 Cand → WL) | Added `open_first` / `open_card` helpers: click `Screen ›` before touching the form; after Move the next card is no longer auto-open (`[data-td4-pro]` count 1 → 0) | Today Cand → WL cards start collapsed (user addition 4) |
| 2 | run_tests_phase20.py, 22, 29 | The step "seed ticker as Candidate → `wlOpenAdd` → save" now seeds the ticker as an existing Watchlist doc first | A Candidate can no longer be added to the Watchlist through `＋`/`wlOpenAdd` (B0); only the Move form creates new docs |
| 3 | run_tests_phase45.py | Idea "→ Watchlist" button now asserts the `Use Move to Watchlist` sheet; the add-sheet prefill check runs on a seeded Watchlist doc | Same (B0) |
| 4+ | see bottom of this file for any further entries added after the full run | | |
| 5 | run_tests_phase80.py, 98, 106 | Expected text `Align MA50` → `MA Align Overlap` | Rename (§1); stored key `align_ma50` unchanged |
| 6 | run_tests_phase82.py | `[data-pf-zact]` count 1 → 0 and `[data-pf-ztxt]` count 1 (2 checks) | Zone Activation checkbox removed (§5) |
| 7 | run_tests_phase98.py | Removed the `[data-pf-zact]` check/uncheck steps; the "uncheck → zone_act false, txt kept" check became "Zone stays set while Setup chips are ticked"; the narrow-width chip check now requires "not clipped" only (chips may wrap to 2 lines) | Zone is a plain text field; zone_act = zone non-empty; longer chip label |
| 8 | run_tests_phase104.py | Note is written via `satV2Edit` (no input any more) and read back from `[data-ln1-oldnote]`; Zone typed in the text field instead of ticking the checkbox | "Additional notes" input removed; Zone checkbox removed |
| 9 | run_tests_phase81.py, 82 | Button list on an Asset tile now includes `☆` (pin) | Pin star (§5) |
| 10 | run_tests_phase59.py | `＋ เพิ่มเข้า Watchlist` on a Candidate now asserts the `Use Move to Watchlist` sheet, then seeds the doc | B0 |
| 11 | run_tests_phase61.py, 62 | Candidate → Watchlist step uses the Move form function (`td4ProSave`) instead of the removed add form; Tier/Phase carry assertions unchanged | B0 |
| 12 | run_tests_phase85.py | `＋` now opens the Add-on-candidate panel; legacy head text `＋ เพิ่มหุ้น` → `＋ Add on candidate` | User addition 1 |
| 13 | run_tests_phase39.py (launcher) | New `TD3_OTHER_DEV` (default True) sets `localStorage dash.td3OtherDev=1` so old suites can still exercise the former Today "Other" content (Today no longer renders Other without it) | User addition 4 (Other removed) |
| 14 | run_tests_phase90.py | Asset chip text may start with the pin star `☆` | Pin star on Asset chips (§5) |
| 15 | run_tests_phase80.py | Removed `[data-pf-zact]` from the list of controls clicked | Checkbox removed |
| 16 | run_tests_phase107.py | Export .txt: open the `⋯` menu first; the `＋` check calls `wlOpenAdd()` instead of clicking `＋` (which is now Add on candidate) | User additions 1–2 |
| 17 | run_tests_phase107.py | A Candidate through wlOpenAdd/＋ now shows the `Use Move to Watchlist` sheet instead of opening the add form | B0 (a ticker reaches the Watchlist only through the Move form) |
