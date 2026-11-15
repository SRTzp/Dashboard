# RE-C2 — progress (branch `claude/re1c2`)
Started from origin/main d828732 (RE-C1 merged: risk-engine.js + re1-adapter.js wired, verified).

## Done
- §0 answered (see summary when written): account = selector (`acctActive`) when >1 account; last price = `c.px` of Core cards (cached, Sat has none); events = Weekly Impact docs + Settings CPI/NFP/FOMC dates (cached).
- §1 risk strip (`re2StripHtml`, `re2State`) · old status text/chip removed from the top card.
- §2 Enter / Check orders / Manage (`re2Model`, `re2Row`) · To do no longer repeats Move stop / still valid?.
- §3 ⚑ Ready flag (`re2ReadyToggle`, clears on Ordered/Filled/Cancelled via write wrappers).
- §4 bottom pair (`re2RoomCard`, `re2EventsCard`).
- §5 new suite `tests/run_tests_re1c2.py` in progress.
Note: §1–§4 were built in one pass in the same code block, so they are committed together.

## Left
- Full test reruns, ui_audit compare, screenshots, summary.
