# PS1c audit — read-only, nothing built (branch `claude/ps1c`)

Line numbers = `index.html` on this branch. Brief: `docs/briefs/PS1c-brief.md` (FINAL LAYOUT §7–§10 overrides). Mockup: `docs/mockups/ps1c-mockup-proper.html` (brief says `claude/mockups/...`; the file is in `docs/mockups/`).

## Setup note (deviation)
- PS1b is merged (PR #16). `main` is checked out in another worktree (`_to_delete/wt_main`), so `git checkout main` is impossible here → branched `claude/ps1c` from `origin/main`.
- The two doc files were **not untracked**: they were already committed on `claude/ps1b` (25ed182, 7c8a59b). They are not in main, so I cherry-picked both onto `claude/ps1c` (a3b4ada, 92a7708). Nothing else carried over.

## §2 / §7 Root cause of "form ignores the Momentum / Compounder switch" (bug seen twice)
- `coreNewIn()` line **12722**: `if(n.mode==='new'){ n.track = wi0 ? wlTrackOf(wi0) : (n.track||'winner') }` — every keystroke re-derives the track from the **Watchlist item's** track (PL1·A8 "one stock = one track"). PS1b §7a `coreScopeSync` (5791) sets `n.track` from `planScope` and rewrites the title, but the very next `coreNewIn()` overwrites it for any ticker that is in the Watchlist. Result: title says Compounder, chip/regime/caps say Momentum.
- Title is only written in `coreNewOpen` (12416) and `coreScopeSync` (not re-derived) → can disagree with `n.track`.
- Fix: one source of truth `n.track` driven only by the form switch / top switch; delete the Watchlist override for new plans (Watchlist track becomes only the **initial** value when the form opens); title, chip, regime factor, risk range, size cap, bucket cap, min stop all rendered from `n.track` in one function. Needs a decision — see Q1.

## §7 Plan top bar: Core | Sat
- Markup 3564–3570: `.scopeTabs` with `scopeStock / scopeLadder / scopeFuture`; node moved into `#hdrSub` by `hdrSubSync` (5866); compact-mode, `HDR_SCOPE3_MIN = 430` (5819) hides it from header on 390.
- `planScope` ('stock' | 'ladder' | 'future') is read in ~15 places (5794, 6489, 8722, 9381, 11311, 11377, 11558, 12401, 12879…). **I will not change its values.** New UI state: Core|Sat buttons map `core → last core port (stock|ladder)`, `sat → future`; remember the last core port in a variable (screen state only, not stored). Momentum|Compounder switch is a second control that calls the same `setPlanScope('stock'|'ladder')`.
- "PL2c shift main tabs left on Plan" = `body.lf-lean .topbar.hd-plan{grid-template-columns:…auto auto…}` (3356–3357) + `topbar.classList.toggle('hd-plan', …)` (5889, 5892). Remove all three → main tabs stay centred (grid `1fr auto 1fr` like other pages). Core|Sat goes in `#hdrSub` right side before `.hbtns`; with 2 buttons the 390px threshold (`HDR_SCOPE3_MIN`) can drop so it fits in the header on phone as in the mockup.
- Dark Core header: `ln2HeaderHtml` area (Core strategy box) gets the Momentum|Compounder segmented switch; New-plan header gets its own; both call `setPlanScope`. Sat header unchanged.
- Keys (9381–9382): `S`→Momentum (stock), `D`→Compounder (ladder), `F`→Sat (future) already map directly to `setPlanScope` → they keep working unchanged (S/D open Core + flip, F opens Sat). `[ ]` cycle list stays `['stock','ladder','future']`. Hint labels in the old 3-button bar disappear; keyboard help text unchanged.
- `SWIPE_NEVER_SEL` (9314) keeps `.scopeTabs`; add the new segmented classes.

## §2 Per-port drafts
- Current draft is a single `coreNew` object (12401): `pxE[3] pxS[3] rkE[4] pcS[4] ne ns riskEdited` + DOM inputs `cnEntry cnStop cnRisk`. Switching port keeps typed values.
- Plan: `n.drafts = {winner:{…}, ladder:{…}}`; on switch save the visible port's fields (entry/SL prices, rows, splits, risk, riskEdited) into its slot and load the other's (empty/defaults first time). Ticker and account are shared (not per port). Tests: 5 switches with typed values; everything visible matches `n.track`.

## §3 / §8 Entry split = % of idea risk
- Today: entry rows store **absolute risk %** `rkE[i]` (`ps1Reset` 12602: `t/c`), shares via `Ps1.planSize({ideaRiskPct, entries:[{px, riskPct}]})` (12668–12690); error `ROWS_OVER_BUDGET`; saved on card as `plan.ps1.rows[i].riskPct`.
- Change is **input meaning only**: field = split % (default even 50/50, 34/33/33, 25×4), `entry riskPct_i = typed × m × split_i/100` → same `planSize` call, same maths. Save blocked unless Σ = 100 (new message "Entry split must total 100%", replaces ROWS_OVER_BUDGET). Risk-per-idea edit no longer needs to rewrite rows (splits are %, so rows follow automatically).
- Saved cards keep `rows[i].riskPct` (absolute, already ÷m); no migration. Edit/readback shows split = rows.riskPct / sum.
- Stops already use `pcS` = "out %" (Σ=100, existing `STOP_PCT_100`) → unchanged.

## §4 / §8 Stock form layout
- Current form `lfFormHtml` 12365–12390: `.ps1G` 3 equal columns (Entry / SL / Risk %) with `.ps1R` rows; extra rows in `#cnEx/#cnSx`; per-row meta `ps1MetaSet` (12669, `#qty · size%` right of the box, hidden by container queries). Row 1 has `.ps1Rx` (display:contents) vs rows 2+ have a ✕ → row 1 is wider. That is the width bug in §4.
- New markup per mockup: default single trade = one row `Entry ＋ | SL ＋ | Risk %` with SL distance below SL box. After ＋ on either: `Risk per idea [x %]` + regime pill, then two columns (Entry·split | SL·out); each row = grid `price(flex) | 64px % | 18px ✕` with ✕ column reserved on row 1; result text **under** its box (`.sub`, min-height 16px so rows do not jump). 390px: price ≈85px, no wrap.
- Entry ＋ on the label line: `.ps1Hd` already has the button in the label; keep. Risk-per-idea row shows the regime pill (existing `lossChipHtml` stays in `#cnRiskHint`).
- Existing hooks to keep working (tests rely on them): `data-ps1-form data-ps1-ebox data-ps1-sbox data-ps1-row data-ps1-meta data-ps1-sum data-ps1-details`, ids `cnEntry cnStop cnRisk cnEplus cnSplus cnSave`, `ps1RowAdd/ps1RowDel/ps1In/ps1Draw`. I will keep ids/data-attrs and change layout/CSS + `ps1Draw`. Several PS1b tests (layout, row widths) will be retired/updated → `tests/PS1c_retired.md`.

## §10 Summary line (all % = of TOTAL portfolio)
- Today `ps1SumHtml` (12555): `#57 · 4.0% · Avg … · Risk 0.20% (tag)`; size% (`snap.sizePct`) and risk% (`riskPct`) are **already of total** (planSize gets `E`). Needed: add money `Risk ฿9.9k (0.20%)` (THB, `ps1M`-style k with 1 decimal; US plans convert via `div`/fx), move tag to the amber pill, header note "· % = of total portfolio" (hidden ≤ 430px).
- Per-row meta currently `#17 · 0.6%` (of total, `qty·px/Ediv`) — already matches §10.
- Port line (new, always visible under summary): `13.2% of MMT · cap 7.5% (25% of MMT) · Details ›`. Today that content sits in Details line 3 (`ps1DetHtml` 12571) and `sizeMax` message is `Shares reduced to fit max position …` (12741) → reword to "Above max size 7.5% — shares will be trimmed". Details keeps l1/l2/l3 minus what moves up.
- Port cards `0.20% of 1.5% cap`: `ps1PanelHtml` (12508) shows `x% of portfolio · target y%` per bucket; will check against mockup copy (the bucket cap numbers come from `cfg.buckets[k].cap`).

## §1 / §9 Sat form alignment
- Markup line **23595–23598**: `.ln1-g3` = Entry/SL/TP grid; Entry 2 is a separate flex row `.ln1-e2` (full width, CSS 3458) with Entry 2 input `flex:1 1 96px`, `.ps1Pc` (62px) and ✕ → wider than Entry 1 and not in the SL column. Entry "＋" is inside `<label>` (fine) but label height differs from SL/TP labels → pushes Entry box down.
- Fix: render Entry 2 as a second row of the **same** `.ln1-g3` grid: col1 = Entry 2 input (same width), col2 = `[50 %][✕]` (62px + 18px), col3 empty. Fixed label height (24px) on all three columns. Data/handlers (`satE2Toggle/Edit`, `data-v2-entry2`, `data-v2-e2share`, 23412 read) unchanged.

## §5 Today › Plans badge
- `td3PlanRowHtml` (8258): row = `<b>ticker</b> Draft/Open dot|missing-text`. Add `ftBadge(c.ticker)` after the Draft/Open label (function exists, 7648; same badge as Core cards 11157+).

## §6 Today homework = one row
- `ftTodayPin` (7662) renders **one `.ftPin` per symbol**, placed at the top of Today (8424, before `td4RemBanner`). Replace with one row: `Homework [AVGO 3d] [GLBE 3d] [NVDA overdue] thesis + screening [Do it ›]`, chips from `ftList()` (already sorted by due), amber/red (`.od`), >3 → `+N` (non-clickable or opens the first hidden? → Q4), chip click → `ftGo(sym)`, "Do it ›" → first overdue / earliest due. Row border red if any `over>0`. Not dismissible (already isn't). CSS `.ftPin` (inline in a long rule near 927) to be rewritten; also check the existing homework *task* row (`kind:'homework'` 6842 / 7156 "การบ้านหุ้นวันนี้") — separate Today task, left alone; mention only so the two don't look duplicated.

## Retired / affected tests
`tests/ps1b_size_test.js` (summary text, rows), `tests/ps1b_shots.py` (layout), `PS1b_retired.md`: will append expectations to new `tests/PS1c_retired.md`; new `tests/ps1c_*` for the listed brief tests (Sat alignment 390/1440, per-port drafts, split %, row widths, Today row 1/3/5 items).

## Questions — I stop here until you answer
1. **Port vs Watchlist track.** Today a stock has ONE track from the Watchlist (PL1·A8, line 12722) — that is the bug. With the form switch the user can plan AVGO as Compounder even if Watchlist says Momentum. OK that (a) the form switch wins and the Watchlist track is only the **initial** value when the form opens, and (b) the saved card uses the switch's port (`card.track`), Watchlist track **not** changed? (I recommend yes/yes; `ftEnsureWl` only uses the track when it creates a missing watchlist item.)
2. **`% of Comp` vs total (brief §8 vs §10).** §8 shows entry result `#17 · 1.2% of Comp`, §10 (later, overrides) says every % is of total (`#17 · 0.6%`, mockup too). I will follow §10 everywhere and show "of MMT/Comp" only in the port line. Confirm.
3. **Risk money in `Risk ฿9.9k (0.20%)` for US stocks:** converted to THB with the dashboard FX (same as the panel), correct? And when portfolio value is missing → keep the `Set account capital in Settings` block (no ฿).
4. **Homework "+N" chip** (>3 items): static label, or tap opens a small list of the rest? (Default: static; "Do it ›" still goes to the most urgent.)
5. **Core|Sat on 390px:** mockup puts it in the header next to the logo (drop `HDR_SCOPE3_MIN` for the 2-button switch). If the real header is too tight with sync status I'll put it on the line under the header instead — okay?
6. **Split rounding:** default even splits for 3 rows = 34/33/33 (first row gets remainder, like mockup `even()` and the SL `out` default today). Changing row count resets splits to even (as ＋/✕ do now for SL). OK?

No code or data touched. Waiting for your OK (answers to 1, 2 matter most; others I will default as stated).
