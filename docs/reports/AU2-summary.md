# AU2 — Parts A + B (C and D deferred until AU1 is merged)

## Done (revised 19 Nov brief)
**A · DD_STOP (peak basis)** — new engine function `ddStopStep(state, snaps, flows)`: drawdown from the PEAK of confirmed equity snapshots, cash-flow adjusted (performance equity = equity − flows since the first snapshot; drawdown = (peak − now) / (peak + flows), so deposits / withdrawals never move it). Stops at ≥ 20% (`stopPct`), lifts when back within 15% (`stopRecoverPct`) of the peak. The 10% half-size rule is unchanged (month-start basis, `emergencyStep` restored to its original form). The peak is stored per account in `settings.re1.peak = {peakP, peakAt}` (raised only; used as a floor so deleting old snapshots cannot lower it). `DD_STOP` blocks new orders in Momentum / Sat / Compounder checks and every adapter model; `actionPolicy` untouched (fills, closes, reductions, stop moves allowed). Act state chip + Port pill show "Stopped · DD 20%".
**B · Execution goal** — Settings › Execution goal 80/90/100 (`ln4.executionGoalPct`, default 100). Chip at the end of the Open risk line: `· Placed 4/5 · goal 100%` (phone `· 4/5 → 5/5`, nowrap, one line). Green ✓ when rate ≥ goal, amber below (tooltip: placed · n unanswered · n hesitated · missed/other · goal), grey with no Ready plans. Tap → Journal › Not taken, week. Weekend checklist has the auto item "Execution goal met" (grey week = met). Journal has an "Execution" section: last 8 weeks (x/y, met / below goal), streak ("Goal met 3 weeks in a row"), and the Invalidated / Thesis / Blocked / Room / Error answers listed with their reason text + note. One helper (`au2Exec`) feeds chip, checklist, Journal card and history.
**Rules** — misses = hesitated, missed, other, unanswered. Neutral (out of the denominator) = invalidated, thesis, blocked, room, error.

## Notes / doubts
1. "Ready" is derived, so a ledger `ln4.rdy[id] = {day, wk, acct, sym}` is stamped when a plan is first seen Ready (deferred write) or placed. A plan belongs to its first Ready week and is not re-stamped later. Plans deleted with no answer drop out.
2. Streak: the running week counts as met while it is grey or at/above goal; a running week below goal is skipped (not counted, doesn't break). Weeks before the first ledger week are not counted.
3. Peak: if the only snapshot is the peak, drawdown is 0. Mid-week provisional (unconfirmed) snapshots are ignored. After a lift, a new drop to −20% of the SAME peak stops again.
4. Journal card / history follow the Journal's account switch; the chip and checklist cover all accounts.
5. Peak write happens from the Act head render (deferred, only when it rises).

## Tests
- `node tests/risk_engine_test.js` 353/353 (peak tracking, new peak, flows both ways, trigger 20% boundary, lift 15% boundary, stored-peak floor, unconfirmed, half-size rule unchanged, block vs allowed actions).
- `tests/run_tests_au2.py` 59/59 (chip text desktop/phone, nowrap, not taller, tap target, neutral vs miss rules, goal 80/90/100 colours, tooltip, setting, checklist item incl. grey = met, history + streak + reason text, adapter peak, peak store, state chip). In `run_regression.sh`.
- re1_adapter 63/63, re1c_live 88/88, hooks superset PASS, syntax OK, sync_re1 OK.
- **Full `run_regression.sh` NOT run** — AU1 is not merged and the Mac is busy. After AU1 merges: rebase `claude/au2` and run it once.

## Rebase onto main (AU1 merged) · full regression
- Rebased `claude/au2` onto origin/main (clean, no conflicts; RE1-only paths from AU1 kept). `sync_re1.py --check` OK.
- Full `run_regression.sh`: 66/68 on the first run (1052s). The 2 failures were both caused by AU2:
  - `phase366` (Weekend review): expected 7 items; AU2 adds the auto item `wk_exec` → 8. Test expectations updated (8 rows, header 2/8, bar 25%, tags/numbers incl. the new row).
  - `phase370` (tap targets ≥ 36px): the execution chip was a 16px-high button on the phone. The chip now has a 36px hit area (`padding:10px 2px; margin:-10px 0`, so the header line height is unchanged). The `au2` phone-chip test now checks one line (h ≤ 40) instead of h < 24.
- After the fixes I re-ran only `phase366` (116 pass), `phase370` (27 pass) and `au2` (59/59). I did NOT re-run the whole regression a second time; the CSS change is limited to the chip.
