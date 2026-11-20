# HW1 · Homework page on Watch (Fact Sheet + your thesis)

Decided by SRTp 20 Nov 2026 (final). Build **after RS2a2 and LT2 are merged** (needs `it.src`, `ltFacts`, `ltTrend`). Branch from main.
Spec, in order of priority: **`docs/briefs/lr/HomeworkWatch2.html`** (A list + detail · B Homework page · C phone) → `HomeworkFacts.html` (Fact Sheet content) → `HomeworkWatch.dc.html` / `HomeworkWatchPhone.dc.html` (older; header, chips and button styles only).
Lean UI rules apply (light only, English UI, one line per item, one primary button per screen, 44px phone targets, tags in JetBrains Mono 11px, no port colours on tags).

## Replaces (keep every hook: map it to the new element or keep the function as a thin wrapper; list the mapping in the summary)
- My Thesis editor `wlMtHtml()` · Homework panel `wl1HwHtml()` (checklist, Trigger box, "I've reviewed this") · WL2 "Use this thesis ✓" (no longer rendered; `wl2UseThesis` / `data-wl2-use` kept as dead hooks).
- The Full thesis view (`wl5Full`) stays reachable from ⋯ › Full thesis. The Homework page reuses the same full-page pattern (list hidden, `‹ Watch` back), so no new panel.

## Fields and rules
| Track | Required | Optional |
|---|---|---|
| Momentum | **What would change my thesis?** (`my_thesis.exit`) · **Trigger** (`hw.trigger`) | Why buy (`my_thesis.why`) · Catalyst · Next check |
| Compounder | **I believe…** (`my_thesis.why`) · **My evidence is…** (`my_thesis.evidence`, new) · **What would change my thesis?** (`my_thesis.exit`) | Not proven yet (`my_thesis.unproven`, new) · Catalyst · Next check |

- Catalyst = `hw.catalyst` (≤ 40 chars). Next check = existing `next_check_date` / `next_check_note`.
- `wl1HwReq` changes for Compounder only (2 → 3 required). No grandfather rule: the user has no completed homework yet, so the new rule applies to every item from the start. (If any item is found with `hw.confirmedAt` set, list it in the summary; don't special-case it.)
- Done, cap and `wl1CapPct` logic otherwise unchanged. Emptying a required field after done → not done (as today).
- Hints (one line, muted): I believe = "What will happen in the business?" · My evidence = "Which facts on the left support it, and why?" · Change my thesis = "A business result, not a price · number + threshold + by when" · Trigger = "Price/RS condition + confirmation". Placeholders as in the mockup.
- Under My evidence: the prompt line **"Which part of your belief has no evidence yet?"** then the optional Not proven yet box.
- Under the fields: muted line "Price rules (stop, exit) live in the Plan card, not here."

## A · Watch list + detail panel
- Homework column: `Not started` · `2 of 3 · Change-my-thesis missing` (name the first missing field) · done = `Done · <catalyst>` or `Done 20 Nov`. Keep ` · adds at 50%` for holdings.
- Row action `Homework ›` (secondary). Detail panel: header, context line, **Why on Watch** (`it.src`: `Leaders · 12M 95 · 3M 92 · 1M 88 · from Screen 20 Nov`; none → `Added manually`), progress `Homework 2 of 3` + bar + first missing field, two summary lines (I believe / Not proven), the size line `Size: 50% until homework is done → 100% · set in Plan`, primary `Continue homework ›` (done → existing Make plan / Open plan button).

## B · Homework page (desktop, 2 columns)
- Top bar: `‹ Watch` · `TICKER · Homework` · status chip · `Track · Sector arrow · RS · % from high` · progress (`2 of 3` + bar).
- **Left: Fact Sheet** from `ltFacts(it)`:
  - legend line `rpt from filing · calc calculated, tap for formula · mgmt management says`;
  - Business, Revenue mix (`seg pct% +yoy`), the 4-quarter table with the `ltTrend` word (`↗ accel.`, `→ steady`, `↘ slipping`…; `↗`/`↘` coloured gain/loss), then `lines` by group, Mgmt says, Missing (warn colour);
  - each row one line with ellipsis; **tap/click a row** → small popover: Formula · Period · Source (link if URL) · `note` in warn colour;
  - `More facts ▾` (folded) lists `more` grouped; Momentum shows no More facts unless present.
  - No `facts` → fallback: Business (`summary.biz`), up to 3 KPIs `name · base`, next 2 catalysts, plus one muted line `Full Fact Sheet: run living-thesis (lite or facts mode)`. Never show `summary.thesis` / `next` / `breaker` on this page.
- **Right: Your thesis**: the fields above, `Compare with thesis ›` under a field only after it has text (read-only side-by-side with the thesis text for that field: why ← `summary.thesis[0]`, exit ← `summary.breaker`, trigger ← `summary.next`; no copy button), `▸ Optional` fold, buttons `Save draft` · primary `Save · mark done` (disabled until required are filled; sets `hw.confirmedAt` + `hw.doneAt`) · link `Copy for AI challenge ›`, then the muted size line `After done: size cap 50% → 100% (next step: Make plan ›)`.
- **Copy for AI challenge ›** copies plain text to the clipboard: a first line `living-thesis challenge · TICKER · track`, the Fact Sheet as `label: text (kind · period · src)` lines, then the user's fields. Toast "Copied — paste into Claude".
- Unsaved-draft guard: keep the `wlMtDirty` behaviour (leaving with changes keeps the draft and asks).

## C · Phone (390)
Full-height sheet: header (`‹`, `TICKER · Homework`, `2 of 3`), segmented **Facts | My thesis** (opens on Facts when every required field is empty, otherwise on My thesis), 16px inputs, Save draft / Mark done 44px at the bottom, popover becomes an inline expand. Swipe gestures from RS2a2 are off inside this sheet.

## Not changing
Today/Plan cap logic, Firestore rules, living-thesis import (LT2 owns it), ⋯ menu items, the RS / Sector columns.

## Proof
- `tests/run_tests_hw1.py`: required/optional per track; Save draft doesn't confirm; mark done disabled → enabled; done → empty field → not done; facts page never shows thesis/next/breaker text; Compare hidden while empty, shown after typing, fills nothing; popover shows formula + note; fallback without `facts`; Copy text format; list column text; `it.src` line + "Added manually"; no overflow at 360/390/1440.
- Side-by-side vs `HomeworkWatch2.html` A/B/C: `tests/screenshots/hw1/*-side.png` (`git add -f`).
- Hooks superset PASS · selftest PASS · one clean `JOBS=2 bash tests/run_regression.sh`.
- `docs/reports/HW1-summary.md`: hook mapping, retired tests (RETIRED lines), differences from the mockup.
- Commit only code, tests, side PNGs and the report.
