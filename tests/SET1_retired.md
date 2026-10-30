# SET1 — expectation changes (nothing deleted; features removed by the brief are listed)

| Suite | Check(s) | Change | Why |
|---|---|---|---|
| run_tests (base) | BTCUSD "no broker configured → lot null" | now expects lot computed with sys `pct` | BTC has a built-in % loss spec |
| run_tests (base) | "fam sees only IC options" | expects `[""]` (single product option) | no brokers in sizing |
| phase5 | BTC Break Price check | **unchanged, still fails** | fails identically on index.backup-pre-SET1 (run in `_to_delete/pre`) → pre-existing, not SET1 |
| phase13 | opens index.backup-pre-UI1.html | unchanged | known (file missing) |
| phase20 | font-size label 'Closed Trade' | expects no label (`[]`) | font size UI removed |
| phase22 | Settings section heads | expects "Core rules" + "App" instead of "Max Heat" + "RRG" | cards rebuilt |
| phase23 | unit labels in #crSec | 23 → 24 fields, one without a unit (Max open risk, moved in) | Max Heat merged into Core card |
| phase24 | "Max Heat" summary label | checks the `sPortCore` label instead | section merged |
| phase29 | C2 backfill broker list | expects product option "XAUUSD · ×100 · USD" | broker select now shows product spec |
| phase34 | SAT risk block title / input count | "Per-trade risk" · 9 → 8 inputs (Macro × moved to Advanced) | v1 block moved under Sat › Advanced |
| phase38, 39 | DD / heat / L2 chip account name | "บัญชีหลัก" → "Main" (phase39 table expectation uses `td3AcctName`) | user request |
| phase47, 77 | fill TF / Setup / Ideas-min inputs | set via JS (`fillx`) instead of typing | inputs have no UI now; validation logic still tested |
| phase54 | §2 rename broker, §3 add broker, §4 delete broker (~25 checks) | **RETIRED** (prints RETIRED) | broker UI removed |
| phase54 | broker list / sheet / lot "XM" | lot compared by value; sheet has no broker/rows | brokers removed |
| phase55 | lot vs AS1, new-asset row, contract fill, NQ cleanup, broker label | lot by value; no contract field; broker data left untouched | brokers removed; fixture adds `settings.products` for XAG/NQ |
| phase56 | Today text vs pre-GL1 | old text `บัญชีหลัก` → `Main` | user request |
| phase70 | minLot 0.05 case | test sets `PRODUCTS.XAUUSD.minLot = 0.05` in-page | minLot fixed in code; rule itself still tested |
| phase80 | Lean/legacy switch in Settings | asserts switch is absent; legacy via `ln1SetMode` + dev flag | switch removed |
| phase88 | whole LN3 6-group Settings suite | **RETIRED** (prints RETIRED, exit 0) | replaced by 5 cards (phase110) |
| phase90 | Mac two-pane Settings (4 checks) | **RETIRED** (prints RETIRED); mobile width check now targets `#setOverlay .modal` | LN3 layout gone |
| phase91 | `[data-ln3-save]` click | `#setSaveBtn` | same save |
| phase107, 108 | Export .txt checks | now check Copy list (clipboard text, order, filter, no export button) | Export .txt replaced (user request) |
| phase60, 63 | XAG sizing | unchanged expectations; fixture also writes `settings.products.XAG` (same 5000/0.01/USD) | sizing reads product |
| phase23 | "Max Heat" labels / screenshot anchor / `sCrL2Cap` fill | labels read from the 3 fields; screenshot anchors on `sPortCore`'s card; `sCrL2Cap` set via JS (hidden duplicate, still synced) | Max Heat merged; L2 cap = one visible field |
| phase35 | `#satHeatHint` wording | contains "ด้านล่างในกล่องนี้" instead of "MAX HEAT ด้านล่าง" | no Max Heat section any more |
| phase80 | account row text | needs "lot" + "pts" instead of broker "XM" | broker name no longer shown |
| phase91 | core-group summary text, `[data-ln3-gsum]` | removed from the check (LN3 group header gone); field labels still checked | LN3 grouped header removed |

Infrastructure: `tests/ff_stub.py` (`SET1_DEV_FLAGS`, part of `FF_STUB_BASE`/`FF_STUB`) seeds dev flags `dash.set1Open=1` (open all Settings cards) and `dash.ln1Legacy=1` (allow the old view in tests). Real users have neither: Sat page view is Lean for everyone. `tests/runall2.sh` runs 1–110. phase110 clears both flags.
