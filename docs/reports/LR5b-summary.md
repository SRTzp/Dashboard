# LR5b — Journal tab (match the mockups)

Branch `claude/lr5b` (from `origin/main`, rebased before the final run). Spec: `docs/briefs/lr/Journal.dc.html` + `JournalPhone.dc.html`. Hooks superset PASS (additions only). No engine, data-job or `journalStats` changes. Light only. English only inside `#tabJournal`.

## Parts
- **A** reusable account switch `Main · Family · Both` — `lrSwitchHtml(tab)`, `lrSwCur/lrSwIds/lrSwPick/lrSwReset`, callback registry `LR_SW_CB[tab]`, styles `.lr-sw` / `.lr-seg`. Default = active account; reset each time the tab opens. **LR5c (Port): call `lrSwitchHtml('port')`, set `LR_SW_CB.port`, read `lrSwIds('port')`.**
- **B** header (Journal · switch · port chips All/MMT/COMP/SAT · period Week/Month/Quarter/All), 5 stat cards, closed table (one line per position; scale-out legs merged), `Not taken (n) · why didn't I enter? ›`.
- **C** review panel (desktop) / bottom sheet (phone): Planned vs Actual, planned-stop note, Why it closed chips, one lesson, thesis snapshot (only if stored), Save review.
- **D** old Journal content kept under a collapsed `Details ▾` (all old ids/hooks intact) and translated to English; phone layout; tests; proofs.

## Definitions
- **R** = P&L ÷ risk at the original stop (`sl0Of`: stored `sl0`, or first `stopHistory`). None stored → "—" with tooltip. Display only; engine `realizedROf` untouched.
- **Result · net** is in THB (each account's own fx); rows show P&L in the trade's currency.
- **Plan**: ✓ Followed · × Early exit (discretionary win/flat) · × Late exit (discretionary loss) · × Off plan (`unplanned`). Discretionary = review chip or an exit-reason tag that is off-plan.
- **To review** = closed with neither a review chip nor an exit-reason tag. Existing exit tags map to the chips (tp/trail/partial/time → Planned, sl → Stop, early/thesis/risk → Discretionary).
- **Periods**: Week = Mon–Sun, Month, Quarter of today (Bangkok); Not taken follows the same period/port/account.

## New field (additive)
`trade.review = {why: 'planned'|'stop'|'gap'|'disc'|null, lesson, at}` written to every leg of the position, in the trade's own account book. Nothing else stored.

## Remaining differences vs mockups
| Screen | Difference | Reason |
|---|---|---|
| Both | Ticker shows `XAUUSD` not `XAU`; fixture numbers differ | live symbols/data |
| Both | `Save review` works in Both (writes to the row's own account) | mockup shows Save under Both; "read-only" kept for edit/delete (those stay in Details, per-account) |
| 1440 | Not taken card wraps to 2 lines when 4 reasons are present | no truncation of counts |
| 390 | Period is a native select beside the title | compact header; 4 segments would not fit with the account switch |
| Both | Thesis row only when a snapshot exists | brief: "if any" |
| Both | Details ▾ keeps the old table/summary | existing hooks must not be removed |

## Tests
New `tests/run_tests_lr5b.py` (106 checks at 1440/390/360) in `run_regression.sh`: stats by hand, moved-stop R, no-stop R, Both sum + currencies, period/port filters, Not taken, review round-trip (persisted), no Thai (Details open), overflow, one line per row. Proofs in `tests/screenshots/lr5b/`: `journal-1440-side.png`, `journal-390-side.png`, `journal-390-review-live.png`, `journal-1440-both-live.png`.
