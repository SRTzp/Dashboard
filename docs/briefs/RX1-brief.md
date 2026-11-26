# RX1 — R marks inline (per strategy, one constant) · TP1 reminder + Exit 50% sheet (Sat only)

Branch from fresh origin/main (after CL2 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-rx1 -b claude/rx1 origin/main`. First commit = this brief + mockups `rr-mockup.html`, `tp1-mockup.html` (~/Documents/Dashboard/mockups/). UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md`. Locked brief. Keep e2e1 green. A and B in separate commits.

## A · R marks, inline, no new line (mockup `rr-mockup.html`, SRTp 26 Nov)
- **One constant, easy to edit later** (top of the plan/board code, with a comment):
  `const R_MARKS = { sat:[2, 3], mmt:[3, 5], comp:[5, 10] };   /* SRTp 26 Nov — R levels shown in plans; edit here */`
  Everything reads this constant; no other hard-coded 2/3/5/10.
- 1R = |entry − stop| (planned stop; after a fill keep R on the ORIGINAL stop, same as Journal). Long: entry + n×R · Short: entry − n×R. Format like the plan's other prices. Hidden when entry or stop is missing.
- **Plan card** (Plan board + Today Enter rows): append to the existing risk line, grey, smaller: `Risk −$180 · 0.12% · 3R 75 · 5R 85` (Momentum) / `· 2R 2,609 · 3R 2,592` (Sat) / `· 5R … · 10R …` (Compounder). No new row at 1440 or 390.
- **Today › Manage (holding)**: append to the existing Last/price line: `· 2R ✓ · 3R 2,592` — a level the typed price has passed turns green with ✓ (needs Price ›; no price → show levels grey).
- **Plan form**: when TP is empty, the TP box shows `2R 2,609 · 3R 2,592` (that strategy's marks) as tappable hint text; tap one → TP = that price. Hidden once TP is filled.
- Tests: values for Long/Short per strategy; constant change (e.g. sat [1.5, 3]) flows to card, Manage and form; no extra line (card height unchanged vs main at 1440 and 390); ✓ appears when price passes.

## B · TP1 reminder + Exit 50% sheet — Sat only (mockup `tp1-mockup.html`)
Sat rule: exit 50% at TP1, move the stop on the rest to entry, let the rest run to TP2.
- Trigger (Sat holding only, from the typed price): Short price ≤ TP1 / Long price ≥ TP1 and no TP1 exit recorded yet → Manage row amber, pill `TP1 reached`, line `⚠ TP1 2,600 reached · exit 50% and move the stop on the rest to entry 2,643`; button `Exit 50% ›` replaces `Move stop ›` (white; Price › stays).
- **Exit 50% sheet** (in-app, Enter = Save, Esc = Cancel): Lots to close = 50% rounded DOWN to the product step (shows the math line `50% of #0.17 = 0.085 → 0.08 · keeps #0.09`); Exit price = TP1; ☑ `Move the stop on the rest to entry 2,643 (no risk left)` (ticked by default); summary `Locks in +$344 · Risk on the rest: $0 (was $289)`. All editable. %-sized products (BTC): qty step from the product spec.
- Save = one partial exit through the EXISTING partial-exit path (Journal shows it, R on the original stop) + stop move through the existing Sat Move stop path (HF5) + log line `TP1: 0.08 closed at 2,600 · stop → 2,643`. Risk room and the HF5 queue rule update (risk cut 100% → new Sat setup allowed).
- After: row green pill `Runner`, line `50% taken at 2,600 (+$344) · rest #0.09 · stop 2,643 (entry · no risk) · TP2 2,560` + `✓ TP1 done · new Sat setup allowed`.
- TP2: when the typed price reaches TP2 on a runner → `⚠ TP2 2,560 reached · close the rest ›` (opens the existing Close sheet prefilled with the rest + TP2 price).
- Momentum / Compounder: no TP1 reminder (only the R marks from A).
- Tests (add a journey to e2e1, real clicks, 1440 + 390): XAU Short + BTC Long: price past TP1 → amber + Exit 50% → Save → partial in Journal, stop at entry, Risk room 0, Runner row; lot rounding (0.17 → 0.08); untick the stop box → only the partial; TP2 → close the rest; no browser dialogs.

## Screenshots (only `rx1-*.png`)
`rx1-marks-card` (1440 + 390, one per strategy), `rx1-manage-tp1` (1440 + 390), `rx1-exit50-sheet` (390), `rx1-runner` (390), `rx1-form-tp-hint` (1440).

## Rules
Full `JOBS=2 bash tests/run_regression.sh` + hooks · revert tracked screenshot rewrites · new suite `tests/run_tests_rx1.py` in REST= · no push until I review — report tests, judgment calls, PNG list.
