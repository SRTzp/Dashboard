# TV1 — Dashboard ⇄ TradingView link (2026-11-08, final)
Branch claude/tv1 from origin/main. SRTp: TradingView Premium. Model: **Dashboard = notebook (all decisions recorded here) · TradingView = chart screen (look only)**.
Checked facts: TV .txt = one line, comma-separated `EXCHANGE:SYMBOL`, `###Name` = section; Import list always creates a NEW list (user deletes the old one first); pasting many symbols into "Add symbol" does NOT work. Section names: plain ASCII with " - " (SRTp tested: `·`/`—` work but look worse).

## 0. Audit (in report; build without waiting)
- Reuse the Ideas › Match TradingView CSV parser (matchSt): which columns it reads (symbol/exchange, description, sector, industry).
- Where to store per-stock `tvSym` (e.g. `NASDAQ:NVDA`), `sector`/`industry`, `setupAt`, `source` on candMeta / wlItems. Does an idea-sourced candidate store its idea id / sector?
- How Flow knows a sector is HOT (Leading or Fresh in RRG) and how to map a stock's TV industry → Flow theme (e.g. Semiconductors → SMH theme). Report the mapping you use.

## 1. Export: Dashboard → TradingView (2 files)
- Watch header button "TradingView ›" → `Download Momentum` · `Download Compounder` · `Import…`.
- Files: `Dash_Momentum.txt`, `Dash_Compounder.txt` (fixed names). Only Core stocks of that track. No Sat.
- Sections, in this order (empty omitted; a symbol only in its first section):
  1. `###HOLD` — open positions
  2. `###READY - SETUP` — Watchlist/draft Plan items with Setup ✓
  3. `###READY` — other Watchlist + draft Plans (HOT-sector stocks first)
  4. `###SCREEN - HOT - <Sector>` — one per HOT sector (Leading/Fresh in Flow now), readable sector name
  5. `###SCREEN` — other Candidates (cold or unknown sector), newest first
- SCREEN cap: max 15 Candidates per file (HOT first, then newest); the rest stay in the Dashboard only.
- Symbol: tvSym if known; TH → `SET:<SYM>`; US unknown → bare ticker + counted.
- Toast after download: "Saved Dash_Momentum.txt" · "TradingView: delete old Dash_Momentum → ⋯ → Import list" · "N symbols without exchange" (only if N>0).

## 2. Import: TradingView → Dashboard (Candidates only)
- "Import…" sheet: drop file or paste. Accept **screener .csv (main use)** and **watchlist .txt** (sometimes, incl. shared lists).
- .csv: read symbol+exchange, industry/sector (reuse Match parser). .txt: `###` sections + comma/newline symbols.
- Reason: from file name or section name (case-insensitive contains "volume" → Volume Spike, "earning" → Earnings Spike, other existing reason labels match too); else "TradingView".
- Track: from file name ("momentum"/"compounder"); else one required choice per import.
- Preview: **New** (added) · Already Candidate · Already Watchlist · Archived (skip, Restore ›) · Non-stock (skip).
- New → Candidates only; save tvSym, market (SET → TH), sector/industry (csv), source = "TradingView". Existing → only learn tvSym/sector, nothing else.
- Imports don't count toward daily New Cand 0/3 and aren't blocked by its max; toast shows "Added N".

## 3. Dashboard: same groups + tags (no restructure)
- Candidates tab: light group headers `HOT · <Sector>` (one per HOT sector) then `Other`. Inside: newest first.
- Watchlist tab: `Setup ✓` group first, then the rest.
- Each Candidate row: ticker · source/reason (e.g. `Volume spike`, `Event: AI power`, `Sector: Semis`, `TradingView`) · age `9d`; ⚠ at ≥ 12d. No reason → `—` shown amber (prompt to set one).
- Small note in each tab header: `= SCREEN in TV` / `= READY in TV`.

## 4. Setup ✓ tag
- One tap on a Watchlist item or draft Plan: "Setup ✓" (toggle). Stored `setupAt`. Auto-expires after 5 trading days (Mon–Fri) without an entry. Shown as a badge; sorts first.

## 5. Candidate expiry
- Candidate not screened (no Pass/Drop) for 14 days → "Drop?" suggestion on the row (one tap Drop / Keep 7 more days). Never automatic.

## 6. Change count
- Button shows `TradingView · N changes` = stocks whose export section changed since the last download (per file; counted from a stored snapshot of the last export). Hidden when 0. Download resets it.

## Tests
- Export: sections/order, HOT per sector, cap 15, de-dup, track split, no Sat, TH → SET:, tvSym, toast.
- Import: .csv (industry saved, HOT grouping) + .txt; reason from file/section; track from name vs choice; skip groups; tvSym learning; New Cand counter unchanged; round trip export→import = 0 new.
- Dashboard groups match the export sections for the same data; row tags; amber `—`.
- Setup ✓ toggle + 5-trading-day expiry; Candidate 14d suggestion (Keep +7d); change count up/down/reset.
- 390 + 1440. Retired → tests/TV1_retired.md. Commit, push, compare URL. Don't merge.
