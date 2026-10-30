# PF1 — dependency map (B1.1) · index.html sha 3e3c4ed6c4bb (HD1) · line numbers are pre-PF1

Legend: KEEP = unchanged · REMOVE = delete (no callers left) · REPOINT = same job, now reads the plan's own Trend (`idea.bias`) · HIDE = stays in code for data/legacy but no UI

## Strategy Trend / Bias / Zone / Shift readers + writers
| Function / site (line) | What it does | Action |
|---|---|---|
| `ln1TrendOf(w)` 19222 | Strategy bias/trend_dir → {dir,flat,none} | REMOVE callers (tile, ln2FormLine, lfAtState, nwRows) · function removed |
| `ln1Trend` / `ln3TrendOk` / `ln3TrendNo` / `ln3AskSync` / `ln3Ask` 19230-19252 | Up/Down pill + "สลับเป็น … เพราะ?" reason box + trend_log write | REMOVE |
| `ln1Flat` 19268 · `ln1NoTrade` 19274 | Flat checkbox · งดเทรด (`bias:'None'`) | REMOVE (data stays) |
| `ln3fLogToggle` / `ln3fLogOpen` + tile `ประวัติสลับ Trend (n)` | flip-history list | REMOVE UI (trend_log/flips data stay) |
| `satwSetZone` / `satwSetZoneBp` / `satwSetInvalidation` (Shift input) 16758, 19250 | Strategy Zone ▲/▼, B&P, Shift writers | REMOVE from Lean tile (functions: `satwSetInvalidation` kept for legacy editor) |
| `ln3ZoneTxt(w,k)` 19254 | Strategy zone text (+ S/R fallback) | REMOVE (only tile used it, after ln3ZoneIdea gone) |
| `ln1TileHtml` 19282 | Lean Strategy tile | REPOINT → Macro-only tile (A1) |
| `ln1MacroTxt` | Macro line | KEEP |
| `satV3TileDirHtml(bias)` 16874 | ▲▼?–↔ arrow from Strategy bias on tile head | REMOVE from Lean head; legacy tile hidden |
| `ln2FormLine` 19388 | status line `▲ ·` from Strategy trend | REPOINT → plan Trend ▲ Up / ▼ Down (coloured, with text) |
| `ln3ZoneCheckHtml` / `ln3ZoneSet` / `ln3ZoneSideSet` / `ln3ZoneIdea` / `ln3ZoneSide` / `ln3ZoneBp` 19429-19463 | form "อยู่ใน Zone" check (Main from Strategy zone, Tac own), `⚠ ไม่อยู่ใน Zone` | REMOVE (replaced by Zone Activation row: `zone_act`/`zone_act_txt`). `zone_ok/zone_txt/zone_side` stay in docs untouched |
| `satV2SaveSlot` 19059 `zone_ok` auto-write | wrote zone_ok:false on first save | REMOVE |
| `ln3IdeaSet` + Idea input 19460/19528 | idea_txt input | REMOVE input (field stays) |
| `satV2SetDir` 19112 | Long/Short buttons → `bias` | REPOINT → Trend select handler, allows clearing ('' ) ; legacy card still calls it |
| `satV2SetSleeve` 19116 | switch Main/Tactical, TF + setups filter | REPOINT: keep TF rule; stop filtering `setups` (new fields untouched) |
| `satV2SetupToggle` / `setupsMain/Tac` lists | old setup chips | REMOVE from Lean form · Settings lists untouched · legacy card keeps |
| `satV2NewPlan` 19085 | needs Strategy bias (Long/Short/Neutral), bias default from it | REPOINT: no gate; new plan `bias:''`; fields `classify/zone_act/zone_act_txt/setup_ck` init |
| `satV3NewPlan` 17468 | older + Plan gate on Strategy bias | REMOVE gate |
| `lfNoFormHtml` 17068 | `+ แผน` disabled when no Strategy bias | REPOINT: always enabled |
| `lfAtState` 17060 | asset tab sfx 'งด'/'ยังไม่ตั้ง' + arrow from Strategy | REPOINT: no sfx/arrow from Strategy |
| `satV3TileHead` 16916 (legacy tile) | `+ แผน` only when Strategy bias | REPOINT: always |
| `satV3TileBadgeSub` / `satV3WeekSizeRule` | legacy badge from Strategy bias | HIDE bias badge (legacy) |
| `satV3Warnings` 16861 | "สวน Trend / Bias สวนองค์ประกอบ / ไม่มี Trend Shift / เกินโควตาสลับ" | REMOVE |
| `satV3SetBias` / legacy editor Bias buttons 17025 | set Strategy bias (Long/Short/Neutral/งดเทรด) | HIDE in legacy editor |
| `satwSetBias` 16790 | week bias writer with flip quota + confirm() | REMOVE confirm/quota path; function stays only as data writer for legacy tests (no UI caller) → removed if no caller |
| `satWeekBiasNow` / `satOffBias` / `satOffBiasMsg` / `satTradeOffBias` / `satOffBiasTagHtml` 17604-17618 | SR1 "สวน Bias สัปดาห์" block + tags + F2c/pyr use | REMOVE; callers: `satV3PlanAcctCalc` (18419), `satV2PlanCalc` (19031/19049), carry banner (17533), trade row tag (7581, 18858), pyramiding check (18688), save guards (18464, 18515, 19060) |
| `sat7dIdeaFlags` / `sat7dCalc` offBias + overFlip 16214-16251 | v1 flow vs week bias/flips | REMOVE bias/flip part (off = false) |
| `satV2PlanCalc` Tactical type 18995-19003 (`wbias`) | accel/hedge/range from Strategy bias | REPOINT: from Main position vs plan Trend: opposite Main → `hedge`; otherwise `accel` (see report decision) |
| `satV3F2c` 18184 `wk.comps.trend.v` / `trend_override` | trend_state for trade snapshot | REPOINT: `trend=null` (no Strategy read) → trade `trend_state:null`, `trend_changed:null` |
| `satV3TrendSet/Toggle` + F2c html trend picker | legacy per-plan override | HIDE (data stays) |
| `satV3CarryBannerHtml` / `satV3CarryConfirm` 17528-17548 | carry-over requires Strategy bias | REPOINT: no bias requirement, no `เช็ก Bias` text, no off-bias tag |
| `nwRows` / `nwState` / `nwStart` 17160-17210 | new-week prompt hints `สัปดาห์ก่อน ▼`, default tick, "already started if any bias" | REPOINT: hint `ถือ n ไม้` / `มีแผน n` / `—`; default tick = all last-week assets; started-check via pick list |
| `satWeekFreshPatch` 17193 | clears bias/trend_dir/zone/shift on new week/+Asset | REPOINT: clears `opinion_txt` only |
| `satwCopyFromPrev` 16800 | copies Shift/Zone/opinion/chart | REPOINT: opinion only (+chart kept as before) |
| Today task `'bias'` 5877 · `tdSatMk` 6617 | "Bias ยังไม่ประเมิน" task · count of assessed | REMOVE task; 6617 count → picks count |
| Journal snapshot `trend_state/trend_changed/plan_bias` 18481, 19070, 14685, 18823 | trade F2c snapshot | REPOINT/leave null; existing trades untouched |
| MR `satMrOn` / `Calc.mrSide(idea.bias)` 15730, 17598-17652 | MR "สวน Bias ของแผน" | KEEP (already plan's own bias) |
| `ln3MacroBoxHtml` / `satV3F2c` Macro align / `Calc.sizeRule` | สวน Macro + reason + size factor | KEEP (uses plan side `idea.bias`; when empty → side 'long' default would mis-tag: guard so no Trend = no Macro box) |
| Strategy image `vwSatStripHtml` / `vwSatOpen/Save/Del` 11754 | chart W/D + TV link | KEEP storage · add caption "ภาพ Week with EMA50" + delete button |
| Settings `setupsMain/setupsTac` | setup lists | KEEP (unused by Lean form) |
| Journal "สถิติตาม Setup" | groups by `setups` | add 3 labels if a small mapping |
