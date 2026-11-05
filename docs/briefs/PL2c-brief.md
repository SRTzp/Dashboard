# PL2c — 3 UI fixes (on top of PR #7, branch claude/pl2)

Status: requested by SRTp 2026-11-05. Small UI changes only. No data, sizing or rule changes.

## 10. Mac/desktop Plan page — sub-tabs back in the top bar
- On the Plan (แผน) page, desktop/Mac layout only: put the Momentum | Compounder | Sat scope switch back in the top header bar.
- On this page only, shift the main tabs (Today / Flow / Watch / แผน / Journal / Port) to the left to make room.
- Other pages and mobile/portrait layouts unchanged. The swipe zones (PL2b item 8) must still work: the header strip stays a landscape swipe zone, but a swipe starting ON the scope switch buttons is a tap target, not a tab swipe.
- Check at 1440 and 1024 widths: no overlap, no wrap.

## 11. Watchlist ticker badge = Track
- The badge next to each ticker (today e.g. "CORE.US" / market chip) shows the stock's Track: **Momentum** or **Compounder**. Old records with no track: "Unspecified" (or no badge — pick the less cluttered, report which).
- Market stays available through the market filter (US / TH) only. Rename any remaining "Core.US / Core.TH" filter labels to **US / TH** (display text only, keep stored keys).

## 12. My Thesis — remove the duplicate summary card
- Remove the duplicate read-only summary card (added under decision D3) that repeats ① / ④ / Next check above or beside the My Thesis editor. SRTp shared a screenshot; if more than one card matches, list them with a screenshot and ask before removing.
- The original My Thesis input fields stay, fully editable, and Save still works.
- Do NOT remove the AI Thesis preview card (it's a different thing). Watchlist ROW status tag + Next check stay.

## Tests
- Affected suites + screenshots (390 + 1024 + 1440) of the Plan page header, Watchlist rows, My Thesis tab.
- Log changes in tests/PL2_retired.md. Commit, push to claude/pl2 (PR #7 updates). Don't merge.
