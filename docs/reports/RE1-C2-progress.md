# RE-C2 — progress (branch `claude/re1c2`)
Started from origin/main d828732 (RE-C1 merged: risk-engine.js + re1-adapter.js wired, verified).

## Done
- §0 answered (see summary when written): account = selector (`acctActive`) when >1 account; last price = `c.px` of Core cards (cached, Sat has none); events = Weekly Impact docs + Settings CPI/NFP/FOMC dates (cached).
- §1 risk strip (`re2StripHtml`, `re2State`) · old status text/chip removed from the top card.
- §2 Enter / Check orders / Manage (`re2Model`, `re2Row`) · To do no longer repeats Move stop / still valid?.
- §3 ⚑ Ready flag (`re2ReadyToggle`, clears on Ordered/Filled/Cancelled via write wrappers).
- §4 bottom pair (`re2RoomCard`, `re2EventsCard`).
- §5 suite `tests/run_tests_re1c2.py` 131/0; all reruns green; ui_audit = main (124).
Note: §1–§4 were built in one pass in the same code block, so they are committed together.

## Left
- Nothing (summary written: RE1-C2-summary.md).

## §6 Costs switch (own commit)
- Done: Settings · Training `Costs` toggle (default OFF, set OFF once), one flag read in the adapter (`src.costsOn`), OFF = costs 0 / net = gross / net-breakeven = entry / never Unknown; cost rows + per-trade override hidden; closes while OFF stamped `costsOff` (never re-costed when ON later); gross strict sign.
- Tests: live-layer +10 (OFF/ON), suite re1c2 +24 (155/0). RE-C1 cost tests now run with the switch ON.
- Reruns on final code all green (re1c 203, 375 135, 374 254, 373 544, SW2 33, re1b 19, engine 313, adapter 63, live 73, re1c2 155); ui_audit 124 = main; summary updated.

## Left
- Nothing.
