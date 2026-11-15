# RE-D — Clean-up, regression and guide (2026-11-16)
Branch `claude/re1d` from origin/main (RE-C1 #46 and RE-C2 merged — verify the Today Act groups and the `Costs` switch are on main; if not, stop). Don't merge.
Authority: this brief → `RE1-C2-brief.md` → `RE1-C1-brief.md` → `RE1-answers-A.md` → `RE1-decisions.md` rev 2 → `RE1-tech-spec.md`.
Rules that never bend: no rule or number changes — this phase only removes dead code, fixes the listed items and proves nothing broke · no automatic resize or change of positions/orders · fills and closes always accepted and flagged · no deletes of user data (stored old settings stay, unread) · existing look and tokens · no overflow at 360 / 390 / 1280 / 1440.
Commit and push after each section; keep `docs/reports/RE1-D-progress.md` (done / left) so the same command can be re-run to continue.

## 1. Small fixes from the RE-C1 / RE-C2 reviews
1. Today › Manage, 1440: the `Move stop ›` button text is faded (low contrast) — same style as the phone `Stop ›` button.
2. Today › Risk room, 1440: the Compounder line is cut (`regime 7…`) — must show in full at 1280 / 1440 (wrap to a second line if needed).
3. Satellite form blocked by R:R / TP: hide `allowed now 0.21 lot (needs 0.21 lot)` when size is not the blocking reason.
4. Enter threshold: one constant for "near entry" = 3%, used by both Today › Enter and the Plan board (board is 2% today). List what changes on the board.
5. `tests/run_tests_phase375.py` (and any other suite): no hard-coded `/Users/peach/Dashboard-rg2b/...` output path — write inside the running worktree.
6. Retake `re1c2-costs-off-settings-390/1440.png` scrolled to Training (Starter ¼ + Costs, cost rows hidden).

## 2. Carried over from RE-C1
- **Satellite stop confirm:** the Satellite stop-update form gets the same confirm step as stocks (estimated net-breakeven price, what confirming does, tick `The stop is placed at the broker`, stores `stopConfirmed` + time). With Costs OFF, breakeven = entry.
- **FX per snapshot:** each confirmed snapshot freezes its FX rate; the week / month basis uses the rate of its snapshot, not the current Settings rate. Sizing of a new order still converts at the current rate. Older snapshots without a stored rate use the current rate and are labelled so. Engine / adapter tests for both.

## 3. Remove what is dead
- Inert shells left by RE-C1 (functions kept only as no-ops, e.g. the PS1 panel / status helpers, old sizing paths) and their callers.
- The old Settings cards hidden in the RE-C1 fix round (caps, loss limits, Core rules, Sat RPT / DD / pyramid / Tactical): remove the markup and handlers. Stored values stay in the data, unread.
- `ps1-size.js` / `core-size.js` and backups such as `index.backup-pre-LN4.html`: remove only if nothing loads them — report each decision.
- The formula sync tool must still fail when the inline copy differs.
List every removal with its last caller in the summary.

## 4. Full regression
- Run **every** suite in `tests/` (not only the recent ones), at 390 / 1280 / 1440 where it applies. Suites that read text removed by RE-C1 / RE-C2 (e.g. phase 369 / 372 / 120 `data-ln4-risk`): update the check to the new location, or retire it with the reason. Retired checks are listed, never counted as PASS.
- Engine, adapter, live, `run_tests_re1c`, `run_tests_re1c2` green with Costs OFF (default) and with Costs ON.
- `ui_audit` compared with main: no new findings; fix rule 2 (chip wraps at 390) and rule 8 (empty gap) if they are in screens touched by RE1.
- Screenshots `tests/screenshots/re1d-*.png` (no animation), 1440 + 390: Today, Plan board, one form per strategy, Port risk, Settings (risk section), Satellite stop confirm.

## 5. Guide
Update `GUIDE-daily-use.md` (find it in the repo; if missing, create `docs/GUIDE-daily-use.md`) in plain language, short: Monday snapshot · reading the Today strip and the three Act groups · ⚑ Ready · how each strategy is sized and what each block reason means · move stop / confirm · what Starter ¼ and Costs do while OFF and what changes when turned ON · what was removed and where it went.

## 6. Cancel a Planned trade, with a reason (new — additive data only)
First report what exists (`bdMissed`, `bdReasonSkip`, `bdCancelOrder`, `satV3IdeaDelete`, "เหตุผลที่ยกเลิก", `restoreCancelled`) and why the newest Planned card shows no way to cancel. Reuse those paths; do not build a second one.
- **Where:** `Cancel plan ›` on every Planned card (overflow / secondary action) and in its drawer, all strategies (Momentum, Compounder, Satellite). Same control and reason list on the Today › Enter row menu is NOT needed.
- **Form:** one small sheet — reason dropdown (required), optional note, `Cancel plan` / `Keep`. Reasons, in this order:
  1. `Missed — price ran before I could enter`
  2. `Hesitated — did not place the order`
  3. `Invalidated — setup broke / invalidation level hit`
  4. `Thesis or news changed`
  5. `Better use of the risk room`
  6. `Blocked by a risk limit`
  7. `Plan error — wrong levels / duplicate`
  8. `Other` (note becomes required)
- **What it does:** status → cancelled (never deleted); stores `cancelReason`, `cancelNote`, `cancelledAt`, last cached price if any; clears ⚑ Ready; the card leaves the board and Today. A cancelled plan never counts as a loss, an idea used, a Satellite step change or a daily setup; if it was the active Satellite setup the queue is released. No position or order is touched. `Restore` (existing) puts it back to Planned and clears the reason.
- **Cancel order (Ordered state, already exists):** add the same reason dropdown to it, same stored fields.
- **Journal:** a `Not taken` list (date · symbol · strategy · reason · note) with a count per reason for the week / month. **Exec goal** (`Valid setups taken per week`): report how it is computed now; reasons 1 and 2 count as a valid setup NOT taken, reasons 3–8 are left out of the ratio.
- **Execution review (limit, no size penalty):** count reasons 1 + 2 per account per week (same week boundary as the engine); reasons 3–8 never count.
  - At 3: red chip `3 not taken` on the Today strip (state red, worst-wins) and To do `Execution review · <account>`.
  - While the review is open, **New plan is locked** for that account (button disabled with the reason `Execution review due`). Place order, Filled ✓, Close, Edit of existing plans and Cancel all stay open. The risk engine is not involved: no size, step, idea or room changes.
  - Review sheet: lists the week's not-taken plans, two required notes (`What stopped me` · `What I change`), `Done`. Stored with date in the Journal; closes the flag for that week. A further Missed / Hesitated the same week reopens it (review needed again at 4, 5 …).
  - Suggestion line only, never automatic: mostly Hesitated → `Turn on Starter ¼ for the next entries ›` (opens Settings · Training); mostly Missed → `Use resting orders or keep fewer Planned names`.
  - **Passed-entry prompt (stocks with a cached price only):** a Planned stock whose price has moved through its entry by more than 3% in the plan's direction shows in Today › Enter as amber `passed entry · missed?` with `Cancel plan ›` / `Keep`. `Keep` hides the prompt for that plan until the next day. No auto-cancel. Satellite: manual only.
- **UI — keep it light (applies to all of §6):** reuse existing components only (the small sheet, chip, To do pill, disabled-button-with-reason, `docs/ui-components.md`); no new colours, cards or layouts. The Planned card gains no visible row: `Cancel plan ›` sits in the card's existing overflow / drawer footer as a quiet text action. Cancel sheet = one screen without scrolling at 390 (dropdown, one-line note, two buttons). Review sheet = short list (max 5 rows, then `+n more`), two one-line inputs, one button. Today shows at most one extra chip and one To do pill; when nothing is flagged, nothing new is visible. Journal `Not taken` is one collapsed row (`Not taken · 3 this week ›`) that opens the list. Every label fits on one line at 390 with no mid-word break and no overflow at 360 / 390 / 1280 / 1440. Screenshots of each new piece at 390 + 1440 go in the summary for review before merge.
- Tests (review): 2 → no flag, 3 → chip + To do + New plan locked, other actions open, reasons 3–8 not counted, review done unlocks, 4th reopens, accounts separate, week reset clears, engine output identical before / after, passed-entry prompt + Keep.
- Tests: each strategy cancel → stored fields, off the board and Today, engine counters unchanged, Satellite queue released, restore works, `Other` needs a note, Journal list + counts, Exec goal ratio, 390 / 1440 no overflow. Screenshots: cancel sheet 390 + 1440, Journal Not taken.

Commit, push, compare URL, `docs/reports/RE1-D-summary.md`: fixes done, removals, suite table (pass / updated / retired), behaviour changes the user will notice, anything unresolved.
