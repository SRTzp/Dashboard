# PS1 audit — current sizing vs PS1-brief (read-only, nothing built)

Branch `claude/ps1` (from main a48ab2a). Source: `index.html` (line numbers on this branch) + `core-size.js`.

## 0. TL;DR
Today's model is **per-bucket-pool risk**, not **% of whole-portfolio E**. Three structural gaps drive most of PS1:
1. All risk % is relative to a *pool* (Momentum pool, Compounder pool, Sat pool); the brief wants **E = whole account**.
2. Plan form has **one Entry + one Stop**; no multi-entry-by-risk, no multi-SL blended stop.
3. There is **no total principal-risk cap, no per-bucket cap, no give-back panel**. Closest things: Core "layer-2" cap (20% of Momentum pool — a *different* quantity) and Sat Open Risk caps.

## 1. Current sizing

### 1.1 E / pools
- `poolsOf(A)` `index.html:9895`: account total = `capital.core` (฿) + `capital.satB` ($×fx). Pools split by `settings.pools` default **50/30/20 = Momentum(`winner`) / Compounder(`ladder`) / Sat** (`POOL_DEF` 9886). Strategic Cash/Option excluded.
- Per account (main, Family each own book). USD→THB via `settings.fx`. **Matches the brief's E and weights.** No "E + its date" is shown anywhere yet.
- Brief keys `ladder`=Compounder, `winner`=Momentum, `sat` → already the code's keys.

### 1.2 Base Risk (Momentum + Compounder) — PL1
- `coreRiskCfg().baseRisk` (`9110`): **default 1** (% of *pool*), one value for both buckets. Settings field `sCrRiskA` "Base Risk per trade (% of pool)" (`3852`). **Hardcoded default 1 ← brief says default must start EMPTY.**
- `Calc.riskBudget` (`18361`): `full = pool × base%`, `adj = full × f × dd`, `left = adj − used`. `used` = `csUsedOther()` (`14405`) sum of other open/planned risk on the *same ticker*.
- First lot = `Calc.coreSize.firstLot` (`core-size.js`): `min(risk÷(E−S), tank×tierCap÷entry, tank×stockCap÷entry, free cash÷entry)`, floored to lot (TH 100, US 1). Risk % = `plan.risk` typed by user, capped by budget. Size cap today = `winnerCap` **25% of Momentum pool** (Compounder: `ladderMaxAcctPct` **5% of account**), not 10–12.5% / 6–7.5% of E.

### 1.3 Caps / multipliers
| Item | Today | Brief |
|---|---|---|
| Risk per idea | Base 1% of pool (single value) | 0.80–1.25 / 0.35–0.50 / 0.10–0.25 % of **E**, per bucket |
| Max position size | 25% of Momentum pool; Compounder 5% of acct | 10–12.5 / 6–7.5 % of **E** |
| Bucket risk cap | none per bucket. Layer-2 "Core" cap = 20% of Momentum pool (`limits.port.core`, warn 15%) — total *open risk to stop* | 3.0 / 1.5 / 0.5 % of E |
| Total cap | `limits.total` = 6 (% of account, legacy Max Heat); Sat `orTot` 6 (Core+Sat) | 5.0 % of E principal risk |
| Regime multiplier `f` | `coreFNow()` (`9962`): 1 / 0.75 / 0.5 from Fund-flow cap | keep (PARKED D1) |
| DD multiplier | `ddEval` sizeFactor 1 / 0.5 / 0 (reduce 12.5, pause 20) | keep (PARKED D1) |
| Sat Macro × | removed in RG2b | n/a |

### 1.4 Max Heat rows (Settings)
- `limits.port` `{core:20, satB:6}` (% of own pool), `limits.total` 6 — default at `4787`; Settings rows "Core — % of Core bucket" (`3843`) and "Sat — % of Sat bucket" (`3919`), "All ports — % of account" (`sTotal`). Hint says Max Heat is mostly "checked in the background" (`13245`).
- Sat caps (`SAT_V2_DEF`, `18203`): `orSat` 1.2, `orAsset` 0.6, `orTot` 6 — **% of total portfolio**, enforced at save (`21568–21571`, `21866–21869`). Closest to brief's style, different numbers/meaning (open risk incl. Core).

### 1.5 Add-on logic
- Core: `Calc.coreSize.addLot` — add = prev lot × 50% (`addRatio`), allowed when `carry (held×max(0,avg−stop)) + new ≤ budget×f`; `move_stop` tag when no room; stock cap by cost. `csAddRisk` (`14420`): `base − used-other/(pool×f)`. Max 3 Base lots + a separate Accelerator budget (`riskAcc` 0.35).
- Net effect today ≈ brief's "stops ≥ avg entry ⇒ carry 0 ⇒ room opens", but **the budget is still the same Base %, not a NEW budget**, and gated by 50%-of-previous ratio + max-lots + accelerator layer. Brief says: new idea budget only when *every tranche* stop ≥ avg entry, otherwise use what's left; recheck size/bucket/total caps.
- Sat: pyramid chain `satPyr*` (`21446–21581`), split % of budget (PY2), carry check `satPyrCheck`. Separate logic, per-sleeve split.

### 1.6 Sat lot calc
- `Calc.satLot` (`18372`): `lot = floor(riskAmount ÷ (|entry−sl| × contract) ÷ lotStep)·lotStep`, minLot → "SL wide" msg. **Formula matches the brief.**
- **Gap:** `riskAmount` = `sat7dAcctBase().riskTHB = satPool × rpt% × ddFactor` (`19197`; `satV2Money.satTHB` = Sat pool). Brief: **E × risk%** (whole portfolio). Sat RPT today: Main 0.5–2% / Tactical 0.25–1% *of Sat pool* (selects only; defaults 1.5 / 0.75) — brief: 0.10–0.25% of E (≈ 0.5–1.25% of a 20% pool, so ranges are comparable but different base).
- Contract multiplier / lot step: per-product `productCfg(asset)` (`contract`, `lotStep`, `minLot`) — reuse as is.
- Free margin of sub-account: not shown beside the lot today.

### 1.7 Plan form
- Momentum/Compounder new-plan sheet: single `cnEntry`, `cnStop`, `cnRisk %` (`11592–11594`; legacy `11637`). Stored `plan.{entry,stop,risk}`, `cs` snapshot (`csSnap`). No rows, no average entry/SL, no "Left x.xx%".
- Ladder (strategy `L`) multi-level cards exist but are retired from use (`coreTrackOfCard`).

### 1.8 Portfolio Risk panel
- Port tab: `#portsSum` summary (`12326`) with held %, positions count, "Regime size", and *"ถ้าทุกไม้โดน Stop บัญชีลด ≈ x%"* (`coreAcctRisk`, drop-to-stop from last close; unknown prices fall back to cost). Sat meters in `satV2` panel (`21764`). 
- **Missing:** principal-risk vs bucket caps, risk-budget-left, give-back (price→stop incl. open profit) with 8/10% bands, per-idea list, Normal/Stop-opening chips, explicit "Missing stop/price = unknown". Today "unknown price ⇒ falls back to cost" (counted, not flagged) — conflicts with brief's "never 0".

## 2. Gap → work (what PS1 will build)
| # | Brief item | Plan |
|---|---|---|
| S | Settings › Portfolio & Risk | New compact card: weights, range + default (EMPTY) per bucket, max size %, bucket caps, total 5%, give-back band 8–10. New `settings.psRisk` per account. Old Base Risk field kept for old plans only. |
| 1 | E | New pure `ps1E(acct)` = `poolsOf().total` + date shown (latest price/fx date available; will state which). |
| 2 | Form rows | New pure module `ps1-size.js` (Node-testable, like core-size.js): `entries[]` (price, risk%), `stops[]` (price, % exit); shares=floor(risk·E/(entry−stop_blend)); caps; avg entry/SL; summary line. Wire into new-plan sheet only; old plans untouched. |
| 3 | Add-on | `ps1AddOn()` gate: tranche stops ≥ avg entry ⇒ new budget else remaining. Re-check caps. |
| 4 | Sat | `satLot` input base → E×risk% for new orders; show sub-account free margin as info. Old orders keep stored numbers. |
| 5 | Panel | New `ps1Panel()` on Port tab top + one-line on Today. Reads open trades + plans; uses last price; unknowns flagged. |

## 3. Questions / decisions I need before building (assumptions marked *A*)
1. **Which trade fields hold price & stop for "current price → stop" (give-back)?** *A:* use the dashboard's existing last-close map (same as `coreAcctRisk`); position with no price/stop → "Missing stop/price".
2. **E date:** *A:* show the latest of (fx date, newest price date) — tell me if you want the capital-edit date instead.
3. **Where entries/SL rows live for Compounder:** *A:* same new-plan sheet (Momentum + Compounder share it, bucket picks the range/cap).
4. **Sat risk % input:** brief says 0.10–0.25% of E — *A:* free numeric field inside the range, default EMPTY ("Set default risk in Settings"), replacing the RPT Main/Tactical selects *for new orders only*; old orders and the old selects keep working. OK?
5. **Existing Sat Open-Risk caps (`orSat/orAsset/orTot`)** and Core layer-2 cap: *A:* leave as-is (not removed) and add the new PS1 caps beside them; the new panel shows only PS1 numbers. Two cap systems coexist until you retire one — say if you want the old ones hidden for new plans.
6. **Idea budget with the existing `f`/DD multiplier (D1 PARKED):** *A:* risk% × f × dd is applied exactly as today to the *idea budget*, shown in Details only.
7. **Rounding for TH** stays 100-share lots; US 1 share. AAA test (2,500 / 1,200 sh) assumes 1-share lots — will use lot=1 in the test.
8. **Where PS1 data lives:** per-account `settings.psRisk` + `plan.ps1` snapshot (entries, stops, E, multiplier) — new keys only, no migration of old data.

## 4. Not touched (PARKED D1–D7)
Regime/DD multipliers on top of new risk (D1), Momentum half-size (D2), Sat daily 0.5% stop (D3), Sat −10% half size (D4), Theme ID (D5), quarterly sweep (D6), margin-buffer per broker (D7). "Half size" status chip not built.

**Waiting for your OK (and answers/overrides on §3) before any build.**
