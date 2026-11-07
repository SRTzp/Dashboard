# TX1 — changed / retired expectations

| Test | Old expectation | New expectation | Why |
|---|---|---|---|
| phase116 A5 (Watchlist card has ① / ④ editor) | item with saved ① shows the textareas straight away | test presses Edit (`wlMtEditOpen`) first; textareas then count 1/1 | whole My Thesis card opens in Read mode when saved text exists (brief §3) |
| phase362 My Thesis tab "one editor" | editor textarea present on opening the tab for a stock with saved text | test presses Edit first (`wlMtEditOpen('MTA')`), same assertions after | Read mode is the default for saved thesis |
| phase362 "after reload: edited text persists" | `[data-wl-mt-why].value` readable straight after reload | Edit pressed first, then value read | same |
| (new) `Archive…` button on the My Thesis card | present when not archived | removed from the card (still in the stock ⋯ menu; Restore unchanged on the card) | brief §3 — no test asserted it |
| phase99 §3 Brent/XAUUSD sheet at 390 / 300 | body text 16–18px, line-height 1.45–1.6 | body = `--read-fs` 15.64px, line-height 1.65 (same as Watchlist stock-data) | brief §4: popups use the one reading size (phone sheet was 17px/1.5) |
