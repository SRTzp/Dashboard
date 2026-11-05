# WM1b — Week mapping · asset identity · flexible Sat asset list · tests 101

> Addendum to WM1 (same area). **Part A = user text verbatim (authoritative)**, Part B = orchestrator notes. If they conflict, A wins — stop and report.
> **Run as part of the WM1 round** (after WM1 is implemented and its tests pass, before the full run). Mockup: `docs/mockups/sn1-mockup.html` sections ④–⑥ + `docs/mockups/overall-mockup.html` ("ตั้งค่า › Sat › สินค้า Sat").
> Backups: `index.backup-pre-WM1b.html` · `tests/_bk_wm1b/` · do not touch core-size.js · temp → `_to_delete/` · never rm · no push.

## Part A — User text (verbatim)

FINAL ADDENDUM — WEEK MAPPING & ASSET IDENTITY
This overrides conflicting assumptions in the previous brief.
Keep the existing PF1/PF2 implementation gate.

1. WEEK MAPPING
- Keep Strategy weeks starting Sunday.
- Keep Weekly Impact weeks starting Monday.
- Map each Strategy Sunday to the immediately following Monday,
  using Asia/Bangkok calendar dates.
- Use one shared mapping helper.
- Separate “Different week” from freshness; display asof independently.
- Today must select events by actual event timestamps, including Sunday
  events from the previous snapshot. Deduplicate by stable event ID.

2. ASSET SETTINGS — MINIMAL CHANGE
Use existing Asset settings as the source of truth.

Keep these concepts separate:
- Internal Asset ID: stable; preserves plans, positions, and history.
- Display name: what the user sees.
- Reference market: what the Asset actually represents.

For an ambiguous Asset such as US:
- Reuse an existing reference-market field if available.
- Otherwise add a small “Reference market” selector in Settings.
- Support explicit choices such as S&P 500 and Nasdaq-100.
- Leave unresolved entries unset; never choose a default silently.
- Recommend clear display names: “S&P 500” or “Nasdaq 100.”
- The user may retain “US” as the display name if the reference market
  is explicitly configured.
- Show a small “Set reference market” action only when unresolved.

Do not automatically rename Assets, change their internal IDs,
or reinterpret historical plans.
Do not change pricing symbols, contract specifications, or sizing rules.
If existing records appear to represent different markets under one ID,
report the conflict instead of migrating them automatically.

3. IMPORT MAPPING
- Match incoming data to existing canonical IDs and explicit aliases.
- BTC may map to BTCUSD through a declared alias.
- XAG and USDJPY are usable only when matching Assets exist.
- US is not a universal alias for both S&P 500 and Nasdaq-100.
- Accept market-specific research only when its reference market matches
  the configured Asset.
- If US remains ambiguous, skip its market-specific mapping and report it.
- No fuzzy matching and no automatic Asset creation.
- Preview matched/skipped Assets before import.
- Permit valid matched entries without clearing unrelated data because
  another symbol failed mapping.

4. SKILL INPUT
Provide the Skill with a compact Asset manifest:
internal ID, display name, reference market, and explicit aliases.

The Skill must return the supplied IDs and analyze the configured markets.
The previous seven-ticker list is a default research list,
not a requirement to create seven Assets.

5. SELECTION MEANING
The ＋ button in Weekly Impact selects an existing Asset into
the current Strategy week.
It does not create or modify an Asset in Settings.

CHECKS
- Sunday/Monday mapping works across month/year boundaries.
- Sunday events remain visible in Today.
- BTC does not create a duplicate BTCUSD Asset.
- Ambiguous US cannot silently receive S&P or Nasdaq-specific research.
- Changing a display label preserves existing record links.
- Existing risk calculations and trading settings remain unchanged.

---

"Sat assets are the instruments I choose to trade with leverage, and they may change over time. Please keep the asset list flexible so I can add, select, or deactivate instruments and assign their reference markets and Playbook links without affecting existing plans or trade history."

## Part B — Orchestrator notes

### B1. What exists today (verified in code, HD1)
- Built-in `SAT_ASSETS` = `XAUUSD`, `BTCUSD` (label BTC), `S50`, `BRENT` (label Brent). Custom assets = `satCustomAssets [{key,label,unit}]` (`satCustomList`). `satAssets({all:true})` = built-in + custom.
- **`US` is a reserved key** (`SAT_KEY_RESERVED` incl. `XAUUSD BTCUSD BTCUSDT S50 BRENT BTC XAU OIL US`) → today "US" cannot be a Sat asset. To trade an index the user adds a custom asset with its own ID (e.g. `NDX`, `SPX`) and sets its reference market. Do **not** un-reserve `US`.
- Display name override: `satAssetCfg()[key].label` (`satLabelCustom` / `sat7dLabel` / `symDisp`).
- Playbook link: `satPbLink {satKey: playbookKey|'none'}` + `satPbKeyOf` (BTCUSDT → BTC built in).
- Missing: **active/deactivate** and **reference market**, and an explicit **alias** list.

### B2. Flexible asset settings (minimal change, Settings › Sat › "สินค้า Sat")
- One list of all Sat assets (built-in + custom), each row: ID (fixed, read-only) · display name · on/off switch · tap → edit: display name · reference market · Playbook link · aliases · unit (custom only, as today) · `＋ เพิ่มสินค้า` stays.
- New per-asset fields in the existing `satAssetCfg` store (no new collection): `active` (default **true** when missing), `ref_market` (`''` = unset; choices: `S&P 500`, `Nasdaq-100`, `Dow Jones`, `Russell 2000`, `Gold spot`, `Silver spot`, `Brent crude`, `WTI crude`, `Bitcoin`, `USD/JPY`, `SET50`, `Other…` free text ≤ 30 chars), `aliases` (array of ≤ 5 uppercase strings, A–Z 0–9 2–10 chars; must not equal another asset's ID or alias; `US` allowed as alias **only** when `ref_market` is set).
- Built-ins get sensible **suggested** ref markets shown greyed as a hint (Gold spot, Bitcoin, SET50, Brent crude) but stored unset until the user confirms — never silently set.
- **Deactivated** asset: hidden from `＋ Asset`, Weekly Impact chips and new-plan pickers; **everything already recorded keeps working**: plans, open positions, Journal, Port, history labels (resolve names through the full list, not the active list). If the asset is picked in the current week or has open positions/active plans, show a confirm before deactivating and keep those visible (parked list).
- Changing display name / ref market / Playbook link / aliases never changes the ID, plans, trades, sizing, brokers or contract specs.
- Unresolved ref market → small `ตั้งตลาดอ้างอิง` chip on that row (and in the Weekly Impact import preview).

### B3. Week mapping
- One helper, e.g. `wiWeekOfStrategy(sundayKey) → mondayKey` and `wiStrategyWeekOf(mondayKey) → sundayKey`, using Asia/Bangkok calendar dates (string date math, no local-TZ Date arithmetic). Used everywhere WM1 compares weeks.
- Labels: `ต่างสัปดาห์` (week mismatch) and `อัปเดต <asof>` are separate; a matching week never implies fresh.
- Today event selection (WM1 §8) = by each event's `scheduled_at` / `date_local` in ICT across **the current and previous snapshot** (a Sunday event lives in the previous Monday-week snapshot), dedup by event ID.

### B4. Import mapping (Weekly Impact)
- Resolve each incoming key: exact ID → explicit alias → label equality (case-insensitive, exact) → else **skipped**. No fuzzy matching, never create assets. `BTC` resolves to `BTCUSD` through the built-in alias.
- If an entry carries a reference market (`ref_market` in the JSON asset entry, optional) and the target asset's `ref_market` is set and differs → skip with reason. If the target's `ref_market` is unset and the research is market-specific (any `ref_market` given) → skip with `ตั้งตลาดอ้างอิงก่อน`.
- Preview before save: ✓ matched (with `BTC → BTCUSD`), skipped (reason). Save stores matched entries only; skipped ones do not clear other data. Deactivated assets: matched and stored, shown greyed.

### B5. Skill manifest
- Add a small `คัดลอก Asset manifest` button in the Weekly Impact panel (paste area): copies JSON `{"assets":[{"id","name","ref_market","aliases"}…]}` of **active** assets for the user to paste into the skill. Document it in `docs/weekly-impact-schema.md` (skill input + output use the supplied IDs).

### B6. Tests — `phase101`
- Mapping: Sun 2026-12-27 → Mon 2026-12-28; Sun 2026-11-29 → Mon 2026-11-30; Sun 2027-01-31 → Mon 2027-02-01; reverse helper; device TZ set to UTC and to America/New_York gives the same keys.
- Today: a Sunday 20:00 ICT event from the previous snapshot shows on that Sunday; same event ID in two snapshots → shown once.
- Assets: deactivate an asset with history → hidden from ＋ Asset / Weekly Impact, Journal/Port/plan rows still show its name and numbers; rename display label → plans/trades still linked (same ID); ref market unset → chip shown, import of market-specific entry skipped with reason; set it → accepted; alias `BTC` → `BTCUSD` (no duplicate asset created); unknown `XAG` (not configured) → skipped, others saved; invalid alias (duplicate / equals other ID) rejected in Settings.
- Risk / sizing / broker settings byte-identical before/after edits (compare settings objects except the touched asset cfg fields).
- 300 / 390 / 1440 no overflow; no console error. Screenshots `tests/screenshots/wm1b-{assets-390,assets-1440,import-preview-390}.png` — open every one.
- Old tests: never delete/weaken; log expectation changes in `tests/WM1b_retired.md`.

## Report back
What changed · conflicts found in existing records (one ID used for different markets) · files changed · test results · screenshots opened · limitations · no push, no file deletion.
