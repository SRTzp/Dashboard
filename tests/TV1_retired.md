# TV1 — expectation changes (old tests keep their intent; only the changed behaviour is updated)

| Suite | Check | Was | Now | Why |
|---|---|---|---|---|
| phase117 | A6: Candidate row Track + Reasons | chips `Momentum · Strong RS · Volume Spike` (two reason chips) | chip `Momentum` + one tag `Strong RS +1` (CAA) / `Earnings Spike` (CBB) / `—` (CCC, no reason) | TV1 §3: each Candidate row = ticker · source/reason · age; the reason moves from chips into the single reason tag (otherwise the reason would show twice). Filtering by Reason is unchanged (same check below still passes). |

Failures seen in the related run that are NOT from TV1 (same on origin/main, unrelated files/behaviour): phase35 (SET1 `#satHeatHint`), phase44/45/47 (missing `index.backup-pre-ID*.html` static checks), phase106 (B4 Sunday default = SK1 change), phase110 (Leadership header layout), phase123 (syntax error in the test file itself), phase62 (0 checks).
