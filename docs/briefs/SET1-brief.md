# SET1 — Lean Settings + product sizing specs (no brokers) · tests 110

> **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> Follow `docs/briefs/STANDING-rules.md` (incl. `docs/reports/SET1-verify.txt`). **Run after TD4c** (start from the TD4c build; record its sha). Backups before any edit, incl. tests: `index.backup-pre-SET1.html` · `tests/_bk_set1/`. Mockup: `docs/mockups/set1-mockup.html` (iPhone).
> Sizing results for XAUUSD and S50 must stay **identical** to today. No other formula changes.

## Part A — User text (verbatim, 29 Oct)
1. "I feel that Settings is really hard to use and overwhelming—there's just too much clutter. For example, recently when I tried to trade BTC in the Sat Port, the position sizing in the plan wouldn't calculate because I entered the numbers in the Port settings incorrectly, and I wasn't sure how to configure it properly. Can we make Settings lean and simple?"
2. "Anything that can be hard-coded and no longer needs tweaking in Settings should just be fixed—like the font size adjustments; I feel there's no need to adjust them anymore. For the BTC calculation, we take the initial Risk amount in dollars ($ Loss) and divide it by the % risk derived from the Entry and Stop Loss. For example, with a 2% risk, it would be $200 / 2% to get the position size. However, gold (XAU) sizing is calculated in lots based on point distance instead. These are two different calculation systems."
3. "Please hard-code the calculation specs for me since I won't be changing them anyway. We don't even need broker accounts like XM or Pi anymore—just base the sizing directly on the product itself. If new products are added in the future, we can deal with them then. Products using lot size: XAUUSD, S50, GO. Products using % loss: BTC, ETH, and various stocks. The ones I'm still unsure about are Brent and S&P 500 (traded on XM). If there are to be settings going forward, the two systems must be completely separated, requiring only the product name and the absolute essentials needed for calculation. Remember keep it lean, simple"
4. "For GO, use the same calculation as S50, but change from 200 to 300 per 1 point (e.g., 4000 -> 4001 equals a profit of 300 THB for 1 contract)."

5. (added 29 Oct) "Want to match hot sectors with stocks in candidates and watchlist to see if they align, then copy and paste them down for AI to help. This can be done by creating a button that allows direct copying by sector -> copying which ETFs belong to each phrase, such as Leading -> XRT, XLE, etc. Similarly, on the watchlist page, instead of exporting a `.txt` file, copy it as text formatted with stock names instead, such as AAA, BBB, CCC, etc."

## Part B — Orchestrator notes

### B1. Products (hard-coded table, one place in code, e.g. `PRODUCTS`)
| Product | System | Spec |
|---|---|---|
| XAUUSD | Lot | $100 per 1.00 move per lot · step 0.01 · min 0.01 · USD (= current XM/IC default) |
| S50 | Lot | ฿200 per point per contract · step 1 · min 1 · THB (= current Pi default) |
| GO | Lot | ฿300 per point per contract · step 1 · min 1 · THB |
| BTC, ETH (incl. `BTCUSD`/`BTCUSDT` aliases) | % loss | position $ = risk $ ÷ (|Entry−SL| ÷ Entry) · qty = position ÷ Entry · qty step 0.0001 |
| Stocks (US / TH) | % loss | same formula · qty whole shares; TH rounded **down** to 100-share board lots |
| Brent, S&P 500 (XM) | Lot | **spec not set yet** — user will add via `+ Add product`; until then sizing shows the "spec missing" message |
- Lot sizing = existing `Calc.satLot` (risk in product currency via the existing FX rate; round down to step; below min → existing "too small" behaviour). % loss = new small pure helper in `Calc` with unit tests.
- Plan display: Lot → `0.19 lot · 32.5 pts` (S50/GO: `6 contracts · 18 pts`); % loss → `$10,000 · 0.10 BTC · stop 2.0%` (stocks: `25 sh`).
- **Brokers removed from sizing**: sizing reads only the product. The broker settings UI (XM/IC/Pi, contract/lotStep/minLot per broker) is removed. Stored broker data and broker fields on old trades stay untouched (hidden); history/Journal still show them if they did before.
- **Custom products** (`+ Add product` in Settings › Products): Lot → name · value per point per lot · lot step · min lot · currency (USD/THB). % loss → name · qty step. Nothing else; the two forms share no fields. Stored in the existing settings doc (`products` map). Built-ins are read-only (shown, not editable). A custom product with the same name as a built-in is rejected.
- Products map to Sat assets by ID/alias (existing `satAssetCfg`/aliases from WM1b).

### B2. "Can't size" message (plan form)
- Replace generic `คำนวณไม่ได้` in Sat sizing with the exact reason + link: `Can't size: Brent spec missing → Set ›` · `Can't size: Sat capital not set (Main) → Set ›` · `Can't size: Entry = SL`. Each `›` opens Settings at that exact field.

### B3. Settings layout (mockup)
- Top: **Setup check** — one line per requirement (capital per account · Core risk · Sat risk · every product used by a current Sat asset has a spec); ⚠ items with `Fix ›`. Hidden when all ✓? No — show a single muted `✓ All set` line.
- 5 collapsible cards, English labels: **Accounts & Capital** (accounts, Core ฿ / Sat $ / Cash ฿ per account, USD/THB auto, goals + sub-goals link) · **Core rules** (Basics: market, max per stock %, max open risk %, DD reduce/pause %; `Advanced ▸`: Tier criteria, ladder L, add-ons, emergency stop, FF gate, other Core fields) · **Sat rules** (Basics: Main/Tactical split, RPT Main, RPT Tactical with live `= $38 per XAU Main trade`, Max DD, max open risk; `Advanced ▸`: tranche splits, Macro ×, TP1/TP2, Tactical brakes, contract-value caps, per-product open-risk cap) · **Products** (B1) · **App** (accounts sign-out, reminders, news days, RRG API key, Industry manager, backup).
- Duplicates merged (e.g. Core layer-2 cap = Max Heat Core → one field). Each field: label + unit; one-line hint only where needed.
- **Removed → fixed in code at the user's current value** (or default if unset): font size (rem), top tab bar, Sat page view Lean/legacy (fix to Lean), default TF Main/Tactical, Setup label lists, Ideas min group size, the old v1 "ความเสี่ยง SAT" block (only if v2 fully replaces it — **audit which fields any calc still reads**; a v1 field still used moves into Sat › Advanced instead), broker settings. Stored values are kept. List every removed field + its fixed value in the report.
- Every save writes only the fields that card owns (other settings byte-identical).

### B3b. Copy for AI (Part A item 5)
- **Flow › Leadership:** a small `Copy by phase` button in the panel header (or its `…`). Copies plain text, current tf, using the same quadrant data as the rows:
```
RRG Daily · as of 2026-10-29 · vs SPY
Leading: XLU (Utilities), XRT (Retail)
Improving: SMH (Semiconductors), KBE (Banks)
Weakening: IGV (Software)
Lagging: XBI (Biotech)
```
  Empty phase → `Leading: —`. Rows with no data are listed last as `No data: XLF`. ★ followed sectors get a `★` before the symbol. Toast `Copied`.
- **Watch › Watchlist and Watch › Candidates:** `Copy list` (in `…`) copies the current filter's tickers in display order as `AAA, BBB, CCC` (plain tickers as shown in the list, e.g. `PTT.BK` stays as displayed; no exchange prefix). **Replaces** `Export .txt` on the Watchlist (remove the .txt export). Toast `Copied 12 tickers`.
- Clipboard API with the select-textarea fallback (as TD3b's Copy AI prompt). No other change.
- **No new rows, no overflow** (user, 29 Oct: "Make sure the added buttons don't overflow from the old rows. Try to fit them in and avoid wasting rows."): `Copy by phase` = a small icon-style button (e.g. `⧉ Copy`, ≥ 32px hit area) placed in the **existing** Leadership header row next to `Daily | Weekly` / refresh — if it doesn't fit at 390, put it in that panel's existing `…`/header menu instead. `Copy list` goes **inside the existing `…` menu** (replacing the Export .txt item), so the `All | US | TH | Add on candidate | …` row is unchanged. Test: header and filter rows keep the same height and line count as before at 300/390/1440 (measure before/after), and no horizontal overflow.

### B4. Tests — `phase110`
- Sizing: XAUUSD and S50 fixture results identical before/after (lots, risk $); GO ฿300/pt (e.g. risk ฿3,000, 10 pts → 1 contract); BTC $200, Entry 100,000, SL 98,000 → $10,000 · 0.10 BTC; ETH; US stock whole shares; TH stock 100-share lots; Brent without spec → `Can't size: Brent spec missing → Set ›`, add custom Lot product → sizes.
- Custom product forms: Lot vs % fields separate; duplicate name rejected; persists after reload.
- Broker UI gone; old trades with broker data still render.
- Setup check states; `Fix ›` deep links focus the right field.
- Removed settings: app uses the fixed values; no UI to change them; other settings byte-identical after saves.
- 300/390/1280/1440 no overflow; no console errors. Screenshots `tests/screenshots/set1-{settings-390,sat-390,products-390,plan-btc-390,plan-xau-390,settings-1440}.png` — open every one.
- Copy by phase text exact for a fixture (incl. ★, empty phase, No data); Copy list = current filter + order, Candidates too; Export .txt gone.
- Old tests: never delete/weaken; log in `tests/SET1_retired.md`. Full run (runall2.sh, base + 1–110) **after the last index.html edit**. Known: p13, p5.

## Report back
v1 vs v2 Sat field audit · removed fields + fixed values · broker data handling · sizing before/after numbers · files changed · full-run results (timestamps of last index edit and run end) · screenshots opened · limitations · no push, no file deletion.
