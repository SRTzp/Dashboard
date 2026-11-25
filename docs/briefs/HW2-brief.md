# HW2 — Homework: one way in · Your thesis fitted to holding time (Momentum vs Compounder) · editable chips

Branch from fresh origin/main (after the HF5 merge): `cd ~/Dashboard-rg2b && git fetch origin && git worktree add ../Dashboard-hw2 -b claude/hw2 origin/main`. First commit = this brief + `hw2-page.html` (mockup, ~/Documents/Dashboard/mockups/). UI rules: `~/Documents/Dashboard/briefs/uiux-concept.md`. Locked brief — nothing gets added mid-job. Keep A / B / C in separate commits.

## A · One way into Homework
Today "Homework ›" lands on 3 different screens:
1. Today rows (`td3HwGo(t,'W','')`: Manage `Homework → unlocks adds ›` ~29587, plan card ~28636, ADDON_THESIS fix ~28527) → `wlOpen(sym,'')` = Watch list only.
2. Today homework list (~12212 / ~13474, `td3HwGo(t, src, TD3_HW_SUB[…])`) → `wlOpen(sym, sub)` → the OLD full-thesis view (`wl5FullSym`, tabs biz/why/trk/exit).
3. Watch `Homework ›` / `Continue homework ›` (`wl5Hw` / `hwOpen`) → the HW1 Homework page; on phone `hwOpen` picks Facts or Mine by progress.
Fix:
- Every homework entry (all of the above + Place order fix + Watch row/detail buttons) calls one `hwGo(sym)` = `switchTab('watch')` + `hwOpen(sym)`. No homework entry may reach `wlOpen(sym, sub)` or `wl5Full`. `td3HwGo` stays only for non-homework uses (Candidates) or becomes a thin wrapper.
- Landing: desktop shows both columns and scrolls/focuses the FIRST missing required field (short amber outline). Phone: always opens on **My thesis** at that field; Facts is one tap.
- `‹ Back` returns to where the user came from (Today: same tab + scroll; else Watch list).
- The old full-thesis view stays reachable only from ⋯ (`Full thesis`, `News & catalysts`).

## B · Your thesis, fitted to holding time (mockup `hw2-page.html`, SRTp 25 Nov)
Momentum holds 2 weeks – 3 months (usually 1–3 m); Compounder 6 months – 3 years (usually 1–3 y). Same anatomy for both: header → left = facts to read → right = 3 numbered answers → footer with one dark button.

**Header (both):** `‹ Back · TICKER · MMT|COMP · Hold 2 wk – 3 m | Hold 6 m – 3 y · progress bar · n of 3 · size X% until done` (X = the engine's real homework cap for that type; amber). Compounder also: `next check <date> (Q results)` = next earnings date, filled automatically (rs2/_earn or Fact Sheet), stored to the existing next-check field; not required. No date known → omit.

**Momentum**
- Left, above the Fact Sheet tabs: context pills from Screen data (no typing): `RS 94 ↗` · `Semis ↗ vs SPY` · `Earnings 3 Dec · in 8d` (amber + `· inside your hold` when ≤ 30 days) · `−6% from high`. Stock not in the Screen list → pills omitted (no "—" row). Fact Sheet opens on **Results** (as now).
- Right, 3 required fields:
  1. `Catalyst & setup` — hint `Why should it move in the next few weeks? Chart and/or news`. Two chip rows: `CHART` (Base breakout · Pullback to EMA50 · New high · Sector leading) and `NEWS · BUSINESS` (Earnings beat · Guide raised · New product / deal · Analyst upgrade). Stored in the EXISTING `catalyst` field (no new field, no data loss).
  2. `Trigger` — hint `When do you buy? One line`. Chips: Close above base high · + volume ≥ 1.5× · Bounce off EMA50.
  3. `What would change my thesis?` — hint `Not the stop (that's in the plan) — what makes the idea wrong` (fixes today's wrong Compounder hint). Chips: RS below 70 · Close below EMA50 · Sector turns lagging · Earnings miss · No progress in 3 weeks.
- Required for done: catalyst + trigger + exit. **Stocks already marked done stay done** (size not cut back); on revisit an empty Catalyst shows a small amber `add` label only.

**Compounder**
- Left: Fact Sheet opens on **Business** (as now). No context pills (facts are already there — rule 4).
- Right, 3 required fields (same fields as today: why, evidence, exit):
  1. `I believe…` — hint `What will happen in the business over the next 1–3 years?`. Chips: Pricing power · Earnings growth speeding up · New product / segment ramp · Margin expansion · Market share gains · Recurring revenue.
  2. `My evidence is…` — hint `Facts from the left that support it — tap to add`. Chips are BUILT from this stock's Fact Sheet (dashed border, label `FROM FACT SHEET`), max 4, e.g. `Revenue +7% YoY`, `EPS +12% vs revenue +7%`, `Op margin ↗ 4 qtrs`, `Shares −2% YoY`, from the same values the Fact Sheet shows (`ltFacts` / HW2_ASK metrics). No Fact Sheet → line `No Fact Sheet yet · Import ›` instead of chips.
  3. `What would change my thesis?` — hint `A business result, not a price · number + within how many quarters (checked each earnings)`. Chips: Growth below X% for 2 qtrs · Key milestone missed · Margin falls 2 qtrs · Lose key customer / renewal drops · Management changes course · Share count rises.
  - `+ Not proven yet (optional)` stays, folded.

**Chips (both types)**
- Tap = adds the chip text to the box (joined with ` · `), chip turns **blue** (selected); tap again = removes that text. The box stays free text. A field is "done" when its box is not blank.
- Phone: each chip row shows the first 1–2 chips + `+n` (opens the rest in place); wrap, never "…".
- Footer: `Save draft` (white) · `Save · mark done` (the only dark button; **grey until all 3 are filled**) · small `Edit chips` link on the right.
- Field badges: `required` amber until filled, `done` green after.

## C · Edit chips
- `Edit chips` opens a small sheet for the current type. Momentum: 4 lists (Catalyst · chart, Catalyst · news / business, Trigger, Change my thesis). Compounder: 2 lists (I believe, Change my thesis) — evidence chips come from facts, not editable.
- Each list = one text box, one chip per line or per ` · `. Save → stored once in settings (`settings.hwChips = {mmt:{…}, comp:{…}}`, all devices). `Reset to default` per type restores the defaults above. Empty list → that chip row is hidden (the field still works as free text).

## Tests (`tests/run_tests_hw2.py`)
- A: for a Momentum and a Compounder stock press every homework entry (Today Manage row, Today homework list, Plan card fix, Place order ADDON_THESIS fix, Watch detail, Watch row) → Homework page (`[data-hw1-page]`), first missing field focused; at 390 `My thesis` active. Back from Today → Today, same scroll. No entry opens `wl5Full`.
- B: Momentum shows the 4 pills from a mocked rs2 row (and none for a stock not in Screen); earnings ≤ 30 d → amber + `inside your hold`. Chip tap adds/removes text and toggles blue. Done needs all 3; Mark done grey until then; old done Momentum without catalyst stays done (size cap not re-applied) and shows `add`. Compounder evidence chips equal the Fact Sheet numbers; no Fact Sheet → Import line. Next-check date auto-filled from earnings. Header hold text per type.
- C: edit a list → chips change on both types' pages after reload; Reset restores defaults; empty list hides the row.

## Screenshots (only `hw2-*.png`)
`hw2-comp` (1440 + 390), `hw2-mmt` (1440 + 390), `hw2-edit-chips` (390), `hw2-nofacts` (390), `hw2-from-today` (390, landed on the first missing field).

## Rules
One full `JOBS=2 bash tests/run_regression.sh` + hooks · revert tracked screenshot rewrites · new suite in REST= · no push until I review — report tests, judgment calls (list every homework entry point you changed, with line), PNG list. Compare your 1440 and 390 screenshots against `hw2-page.html` before reporting.
