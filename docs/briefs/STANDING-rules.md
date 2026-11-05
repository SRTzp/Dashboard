# Standing rules for every CC round (applies to every brief, even if the brief doesn't repeat them)

## Safety
- Backups before editing: `index.backup-pre-<ROUND>.html` + `tests/_bk_<round>/`. Don't touch core-size.js unless the brief says so.
- Temp files → `_to_delete/` · never rm · no push · never deploy Firestore rules (show the block in the report only).
- Old tests: never delete or weaken; change an expected value only where the brief changes behaviour, and log it in `tests/<ROUND>_retired.md`.

## Verify file (required, every round)
At the end of the round, write `tests/make_verify.sh` once (reuse it afterwards) and run `bash tests/make_verify.sh <ROUND>`.
It must build `docs/reports/<ROUND>-verify.txt` **mechanically from command output and runner logs, never typed by hand**. Max 60 lines, in this order:
```
round: <ROUND>   date: <ISO local time>
index.html sha256: <full>
backup index.backup-pre-<ROUND>.html sha256: <full>
check_syntax: OK|FAIL · core_size_test: <pass>/<total> · sync_core_size --check: OK|FAIL
new suite <phaseNNN>: <pass>/<total> checks
suites run: <pass>/<total>  (full run: yes|no)
FAIL <suite> [after solo rerun]: <first 3 FAIL lines>      (one block per failing suite; "none" if none)
expectation changes: tests/<ROUND>_retired.md · <n> entries
screenshots: <name> <bytes>                                (one line each)
files changed: <path> (+added/-removed lines)              (one line each, from diff vs the backups)
```
The written report (`<ROUND>-report.md`) stays as the brief asks; the verify file is in addition to it.
