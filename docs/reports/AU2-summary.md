# AU2 — Parts A + B (C and D deferred until AU1 is merged)

## Done
**A · DD_STOP** — `POLICY.emergency.stopPct: 20`; `emergencyStep` returns `stopped`; reason `DD_STOP` ("Account is 20% below its peak · new entries stopped") blocks new orders in `momentumCheck`, `satCheck`, `compCheck` (flag `ddStop`) and in every adapter model via `finish()` (Momentum / Sat / Compounder sizing, Place sheet, Blocked rows, `wouldBeBlocked`). `actionPolicy` untouched: fills, closes, reductions, stop moves stay allowed. No override. Chips: Act state chip and Port/Today status pill show "Stopped · DD 20%" (red).
**B · Execution chip** — end of the Act "Open risk" line: `· Placed x/y this week` (desktop) / `· x/y` (+ ` ✓` when green, phone, nowrap). Green / amber / grey as briefed. Tap → Journal, period Week, Not taken open (sheet on phone). Journal "Not taken" card adds `placed x/y` from the same helper (`au2Exec`).

## Doubts / decisions to check
1. **Reference equity.** Brief says "peak confirmed equity" but also "same basis as the existing emergency rule" (month-start / retained reference). I used the existing emergency reference; no new peak tracking.
2. **Recovery.** "Same recovery rule": emergency has a 5-pt gap (trigger 10 → recover 5). The stop lifts when the drop is back above 15% (20 − 5), then half size stays until above −5%, then full size.
3. **Ready is derived, not stored**, so I added a small ledger `ln4.rdy[id] = {day, wk, acct, sym}`, stamped the first time a plan is seen Ready (deferred write from the Act head render) or when it is placed (`ln4Valid(..,'working')` — covers all four place flows). A plan belongs to the week it first reached Ready; it is not re-stamped in later weeks (so a plan still Ready next week is not double counted, and last week's unanswered ones stay in last week).
4. Only `invalidated` and `thesis` answers leave the denominator, literally as briefed. `room`, `blocked`, `error`, `other` count as misses — you may want `error`/`blocked` treated as correct skips.
5. Plans deleted/archived without any answer drop out of the count.
6. Journal card uses the Journal's own account switch and period; the chip uses the accounts on Today. For the same accounts and period=week they are equal (tested).

## Tests
- `node tests/risk_engine_test.js` 340/340 (new AU2 block: trigger, recovery 15 / 5, three checks block, actionPolicy).
- `tests/run_tests_au2.py` 28/28 (chip counts/colours, skip removal, hesitated stays, phone nowrap one line, no taller Act head/page, tap → Journal week Not taken, Journal card = helper, state chip, adapter `stopped`). Added to `run_regression.sh`.
- re1_adapter 63/63, re1c_live 88/88, hooks superset PASS, check_syntax OK, sync_re1 OK.
- **Full `run_regression.sh` NOT run**: AU1 (`origin/claude/au1`) was not merged when I finished and the Mac was busy. Rebase on main after AU1 merges and run it once.
