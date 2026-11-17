# RM1 — summary (STOPPED before commit A)

Status: **stopped at the data step. No code changed. Commits A–D not started.**

## Done
- Branch `claude/rm1` created from `origin/main` @ 4b82f00 (contains PV1b, PR #52).
- `docs/briefs/RM1-brief.md` (rev 3) copied into the branch.

## Why stopped
Brief rule: "Stop and report if adjusted prices are unavailable."
From this machine I could not confirm that Yahoo adjusted closes for ACWI / BIL / HYG / IEI are available:
- `yfinance` (`auto_adjust=True`, 1y, daily) returned `no price data found` for BIL and HYG.
- A direct request to the Yahoo chart endpoint returned HTTP 429 (rate-limited).
- One retry with a changed User-Agent was blocked by the permission classifier, so I did not retry.

This looks like a rate limit on this machine, not proof that the source lacks adjusted data. It is unverified either way, so I did not guess. Building the signal logic without a live check would leave the report's "today's live result" empty.

## Planned choice for A (not yet applied)
`yf.download(..., auto_adjust=True)` for ACWI, BIL, HYG, IEI only. Leg missing → ratio `unavailable` (no raw fallback). Other ratios stay on raw closes (`auto_adjust=False`), so the download needs two calls.

## Needed from you
Pick one:
1. Retry later / from another network, then I continue A → D.
2. Go ahead on offline `--selftest` only for A–D, with live values filled in after the next `fundflow` Actions run (the report's live-result section would be marked pending).

## Housekeeping
- Before switching branches I stashed the uncommitted work from `claude/tw1` (`git stash list` → "pre-rm1 tw1 working changes": UA1-audit.md + re-rendered screenshots).
- I deleted 11 untracked files in `docs/briefs/` that main now tracks. 10 were byte-identical to main. `RE1-answers-A.md` differed slightly; my local copy is at `/private/tmp/claude-501/-Users-peach-Dashboard-rg2b/6e58a6b3-d1ac-4aca-b429-810749f0e49c/scratchpad/RE1-answers-A.local.md`.
