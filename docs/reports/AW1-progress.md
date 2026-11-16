# AW1 progress
- §1 account switch `#acSw` in top bar (tabs+pill grouped in `#topMid`), ⋯ menu `#mmAcct` removed, iPhone ≤600: letters, logo + sync dot (tap → ⋯ menu). DONE
- §2 `[` / `]` in the global keydown handler. Existing per-tab `[ ]` filter cycling moves to `Shift+[` / `Shift+]` when ≥2 accounts (single account unchanged). DONE
- §3 badge: `aw1Count(acct)` = re2Model(acct) Act rows + snapshot due + re4Due. Computed in renderAcctBar (called by render). DONE
- §4 Equity snapshot sheet (`aw1SnapOpen`) from To do 'Snapshot due' + Today Act state chip (any snapshot state); `re1SnapConfirm(acct, pfx)` reused. DONE
- §5 ✕, §6 chip, tests, summary DONE
