# TV1 — Dashboard ⇄ TradingView link (report)

Branch `claude/tv1` from origin/main. Built in `index.html` (+347/−9), new suite `tests/run_tests_phase368.py` (84 checks, 390 + 1440). Nothing merged, no Firestore rules changes.

## §0 Audit (done before building)
**Match CSV parser (`matchCsv` / `matchParseList`)** reads: `Symbol` (required header; strips `EXCHANGE:` prefix), `Description`, `Industry`, `Price - Currency` (USD→US, THB→TH, else guessed from `.BK`). It does **not** read exchange or sector, and it drops the exchange. TV1 therefore uses its own `tv1Parse` on top of the same RFC-4180 reader (`matchCsv`): Symbol (accepts plain or `EXCH:SYM`), `Exchange`, `Description`, `Industry`, `Sector`, `Type` (ETF/crypto/etc → Non-stock). The Match tool itself is untouched.

**Storage** (all in `settings` of acctList[0], written with `glWrite`; no new Firestore collections):
- `candMeta[KEY]` (existing): now also `industry`, `sector`, `tv` (e.g. `NASDAQ:NVDA`), `source:'TradingView'`, `keep_until` (Keep +7d). It already had `track`, `reasons`, `cand_at`, `screened_at`, `manual`, `market`.
- `tvInfo[KEY] = {x:'NASDAQ:NVDA', i:industry, s:sector}` — new, **for every stock** (Candidate or Watchlist; wlItems have no exchange field, so the learned tvSym lives here).
- `tvSetup[KEY] = 'YYYY-MM-DD'` — new (`setupAt`), keyed by symbol so one tag covers a Watchlist item and its draft Plan.
- `tvSnap{winner,ladder}[KEY] = sectionName` — new, snapshot of the last download (drives the change count).
- Watchlist items already carry `industry`, `sector_etf`, `market`; Plans are `coreCards` (status `plan`) with ticker + track.
- **Idea-sourced candidates store no idea id and no sector** (they are computed from `ideaList` on the fly). Their row reason is derived: `Event: <idea>` / `Sector: <idea>` from the idea's `nature`; sector for HOT grouping comes from nothing → they land in `Other` until a TV import teaches `tvInfo`.

**HOT sector / mapping.** Flow has no "Fresh" state; the existing Watch rule is `sectorHot()` = RRG quadrant Outperforming ↗ (`lead`) or Outperforming ↘ (`weak`), or ★-followed (`sectorState`). TV1 reuses that exact rule (same as the existing "Hot sector first" button). Stock → sector ETF: Watchlist `sector_etf`, else `sectorSuggest()` (existing keyword table) on `industry` → `tvInfo.i` → `tvInfo.s` → `candMeta.sector`. Examples: Semiconductors → SMH · Software/SaaS/Cloud → IGV · Cybersecurity → HACK · Aerospace/Defense → ITA · Oil/Gas/Energy → XLE · Electronic Components/Hardware → XLK. Section name = the RRG name of that ETF (`SMH` → "Semiconductors"), ASCII only.

## What was built
- **Export** (Watch header `TradingView ›` → Download Momentum / Download Compounder / Import…): `Dash_Momentum.txt`, `Dash_Compounder.txt`; Core only (no Sat); sections HOLD · READY - SETUP · READY (HOT first) · SCREEN - HOT - <Sector> · SCREEN; a symbol only in its first section; SCREEN cap 15 per file (HOT first, then newest); symbol = learned tvSym → `SET:` for TH → bare US ticker (counted). Toast: Saved · delete old → Import list · "N symbols without exchange" (only if N>0).
- **Import…** sheet: drop/choose file or paste; screener .csv and watchlist .txt (`###` sections). Reason from file/section name (volume → Volume Spike, earning → Earnings Spike, any other active reason label contained) else "TradingView"; track from file name else a required choice. Preview groups New / Already Candidate / Already Watchlist (incl. held) / Archived (Restore ›) / Non-stock (crypto/FX/index/ETF type/other exchanges). New → Candidates only (tvSym, market (SET→TH, `.BK`), industry/sector, source); existing → only tvSym/industry/sector learned. Does not touch `candAddLog` (daily New Cand) or its max; toast "Added N".
- **Groups + tags**: Candidates tab `HOT · <Sector>` headers then `Other` (newest first inside); Watchlist `Setup ✓` group first then `Watchlist`; headers only appear when there is something to separate. Same function builds both the file and the headers. Note `= SCREEN in TV` / `= READY in TV` per tab. Candidate row: reason/source · age (`⚠` ≥ 12d); no reason → amber `—`.
- **Setup ✓**: toggle on Watchlist rows (badge `Setup ✓ · 4d left`); expires after 5 trading days (Mon–Fri) or when the stock has an open position; sorts first; draft-Plan stocks pick it up via the same symbol key.
- **14-day Drop?** row suggestion (base = screened_at or cand_at) with one-tap Drop / Keep 7 more days (`keep_until`); never automatic.
- **Change count**: `TradingView · N changes` (sum of both files, per-file count in the menu), hidden at 0, download resets it.

## Notes / judgment calls
- Setup ✓ is toggled on the Watchlist row only (not on the Plan card UI); a draft Plan of a Watchlist stock is covered by the shared symbol key.
- Candidate reason chips (old) were folded into the new reason tag so the reason does not appear twice → one old expectation changed, logged in `tests/TV1_retired.md`.
- Held (open Core) stocks that are not on the Watchlist count as "Already Watchlist" on import (so a round trip gives 0 New).
- Classic (non-Lean) row template did not get the new tags (Lean is the app default and the only one the tests drive).

## Tests
`phase368` 84/84 (export, import, groups/tags, Setup ✓, 14d, change count, round trip, 390 + 1440, no overflow/console errors). Related run (35 suites): all green except failures that are the same on origin/main (verified for phase35/106/110 by swapping in the pre-TV1 index): phase35 (SET1 hint), 106 (Sunday default, SK1), 110 (Leadership header), 44/45/47 (missing old backups), 123 (syntax error inside the test file), 62 (0 checks). Details: `docs/reports/TV1-verify.txt`. Screenshots: `tests/screenshots/tv1-*.png`.
