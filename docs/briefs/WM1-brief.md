# WM1 — Weekend Macro Update (Weekly Impact) + Strategy simplification + Today event reminders · tests 100

> User final handoff 25 Oct. **Part A = verbatim, authoritative** (it says it supersedes conflicting earlier briefs). **Part B = orchestrator conflict check + anchors + tests.** If Part B conflicts with Part A, Part A wins — stop and report.
> **Gate (Part A "WORK ORDER"):** start only when **PF1 and PF2 are both finished and verified on the cloud** (the user will tell you). Check the real code state yourself. If not satisfied → stop and report.
> Backups: `index.backup-pre-WM1.html` · `tests/_bk_wm1/` · do not touch core-size.js · temp files → `_to_delete/` · never rm · no push.
> **The skill part (Part A §2–3) is NOT for Claude Code** — the orchestrator writes the `weekend-macro-update` skill in claude.ai once the JSON contract (B4) is fixed. Claude Code builds only the Dashboard side (Part A §4–10) and a sample JSON for tests.

---

## Part A — User spec (verbatim)

FINAL HANDOFF — WEEKEND MACRO UPDATE + DASHBOARD

This brief supersedes conflicting earlier briefs.
Goal: Effective & Pragmatic, while keeping the interface Lean.
Optimize for useful, understandable information—not minimum tokens at the expense of clarity.

WORK ORDER
- Dashboard implementation must wait until PF1 and PF2 are completed and verified.
- Inspect their actual status. Do not infer completion from comments or filenames.
- If either is unfinished, queue this as the next separate brief.
- Work from the latest code, not old screenshots or mockup data.
- Preserve completed work and unrelated functionality.
- Give a short implementation plan, then proceed when the gate is satisfied.
- Read relevant code only. Reuse existing components, handlers, and storage patterns.
- No unrelated refactoring, new dependencies without necessity, push, or file deletion.
- Report changed files, focused validation, and remaining limitations. No full-code response.

==================================================
1. OVERALL WORKFLOW
==================================================

Weekend Macro Update skill:
Research → concise ranked summary + JSON → user pastes into Dashboard.

Dashboard:
Imported weekly data → Asset selection → selected Strategy cards → Today event reminders.

Use one shared weekly/event dataset.
Do not duplicate event facts separately for each surface or Asset.
No automatic trading, order blocking, or changes to trade sizing.

Keep these distinct:
- Weekly Impact: near-term catalysts and event interpretation.
- Quarterly Macro: existing Playbook thesis and Change if.
- Note: user’s view for the current week.
- Trading plan: existing plan workflow and direction logic.

==================================================
2. WEEKEND MACRO UPDATE SKILL
==================================================

ASSET UNIVERSE
Use only the configured Sat Assets:
XAUUSD, XAG, BTC, BRENT, USDJPY, S50, US.

Map to existing canonical IDs/aliases.
Check what US represents in the current app; do not silently switch between
broad US equities and Nasdaq.
Do not create new tradable Assets.

TARGET WEEK / TIME
- Target week starts Monday, Asia/Bangkok.
- Store week as YYYY-MM-DD.
- Store asof as an ISO timestamp with timezone.
- Show event times in ICT, UTC+7.
- Verify full dates and convert from the source timezone correctly,
  including daylight-saving changes.
- Do not infer dates from text such as “Thu 19:30” alone.

RESEARCH BUDGET
Replace the rigid one-search-call limit with:
- One main research pass covering shared events.
- Targeted verification only for important missing or conflicting facts.
- Research events once, then map their relevance to Assets.
- Stop when decision-relevant coverage is sufficient.
- Prefer official sources for schedules and releases.
- Use a credible calendar/poll source for consensus, with attribution.
- Do not invent information to fill gaps.

LOOKBACK / CARRYOVER
For a target week beginning Monday:
- Review the immediately preceding Monday–Sunday, only through the run time.
- Include unresolved catalysts with evidence of continuing relevance.
- Use occurrence dates, not republished article dates.
- Older themes may qualify through a verified new development in this window.
- Do not assume excluded older news is fully priced in.
- Price momentum alone is not enough for a carryover upgrade.

CALENDAR TIERS — ASSET-SPECIFIC
HIGH:
Major, directly relevant catalyst.

MED:
Secondary or meaningful indirect catalyst.

LOW:
Coverage is sufficient and no significant catalyst was identified.

Unknown:
Evidence is insufficient. Output impact: null.
Never treat Unknown as LOW.

CARRYOVER ADJUSTMENT
- No supported active carryover → keep calendar tier.
- Supported ongoing catalyst → +1 tier, capped at HIGH.
- Confirmed, material, directly relevant shock with unresolved implications → HIGH.
- Apply only the strongest adjustment once.
- Do not stack upgrades or double-count the same catalyst.
- Do not describe news as “unpriced” without evidence.
- A verified qualifying shock can justify HIGH despite incomplete calendar
  coverage, but disclose the coverage limitation.

Impact is a qualitative catalyst assessment.
It is not a forecast of realized volatility, direction, or trade attractiveness.

==================================================
3. CONTENT QUALITY — UNDERSTANDABLE, NOT CRYPTIC
==================================================

CHAT OUTPUT
- Brief ranked list covering all seven Assets.
- Main drivers and ICT times.
- Short explanation of meaningful carryover upgrades.
- Brief coverage limitations where relevant.
- Source citations.
- One valid, reasonably compact JSON block.

Do not repeat all expanded UI content in prose.

EVENT FACTS
For numeric releases, include when verified:
- Precise indicator name: headline/core, MoM/YoY, etc.
- Reference period.
- Unit.
- Scheduled timestamp.
- Consensus forecast.
- Previous value.
- Whether previous value was revised, when known.
- Source and checked-at timestamp.

Do not conflate:
- Headline and core.
- MoM and YoY.
- Different reference periods or GDP annualization bases.
- Original and revised previous values.
- Market consensus and an individual analyst forecast.

Missing forecast or previous = null, not zero.
Do not fabricate numeric consensus for qualitative announcements.

EVENT INTERPRETATION — THAI
Help the user understand what the result could mean.

For suitable numeric releases, provide:
1. Above forecast.
2. Below forecast.
3. In line with forecast.
4. One useful post-release observation.

Each scenario:
- Use 1–2 short, plain-Thai sentences.
- Explain result → transmission channel → possible Asset effect.
- Use conditional language.
- Do not use a universal “hot = bearish / cool = bullish” rule.
- Do not invent a numeric “in-line” tolerance.
- Exact equality is only equality to the displayed forecast, not proof
  of an economically insignificant surprise.

For rate decisions, speeches, or qualitative events:
- Use appropriate scenarios instead of forcing above/below forecasts.
- Example categories: more hawkish / more dovish / broadly expected.
- Account for guidance when it matters, not just the headline decision.

MECHANISM / REACTION NOTE
- Explain the main transmission channel in Thai.
- Add one specific observation that helps interpret the release.
- No unsupported claims such as “always hunts stops before the real move.”
- No current technical-position claims without verified chart evidence.
- Avoid repetitive generic warnings on every Asset.
- No Direction Risk versus Playbook, price targets, ATR estimates,
  or expected price ranges.
- Do not automatically change Quarterly Macro or trade direction.

==================================================
4. DATA CONTRACT — STRUCTURED EVENTS
==================================================

The earlier note-only JSON is insufficient for timed reminders.
Use a versioned contract with shared events and Asset references.

Proposed schema: weeklyImpact/v2.

Top level:
- schema
- week
- asof
- sources
- events
- assets

sources:
A source dictionary with:
- name
- url
- checked_at

events:
A dictionary keyed by stable event IDs.
Each event contains, as applicable:
- title
- label_th
- kind: release / decision / speech / carryover
- metric
- period
- unit
- scheduled_at: ISO timestamp with offset, or null
- date_local: YYYY-MM-DD when only the date is verified
- time_status: confirmed / tentative / unknown / unscheduled
- occurred_at: for carryover, when known
- forecast: number or null
- previous: number or null
- previous_revised: boolean or null
- actual: number or null
- actual_updated_at: timestamp or null
- status: scheduled / released / postponed / cancelled / ongoing
- source references for schedule, forecast, previous, and actual as applicable

Store YoY/MoM or other measurement basis explicitly, either in metric
or a dedicated basis field. Avoid ambiguous numeric values.

assets:
Exactly the configured seven ticker keys in skill output.
Each contains:
- impact: HIGH / MED / LOW / null
- note: brief overall weekly driver summary
- event_refs: references to relevant shared events
- optional carryover explanation
- Asset-specific interpretation for relevant event references:
  mechanism_th
  scenarios_th
  watch_th

Use descriptive but concise keys consistently.
Do not create separate copies of one event’s forecast/time for each Asset.
Asset-specific interpretation may differ while event facts stay shared.

CONTENT PRIORITY
- Surface the two most relevant drivers per Asset first.
- Preserve additional verified material events in the expanded view
  so Today does not miss them because of a display limit.
- Do not add low-value events merely to fill the list.

BACKWARD COMPATIBILITY
- Older weekly JSON with week/assets/impact/note/optional mechanism
  should remain readable.
- Legacy text-only events must not generate timed reminders.
- Do not guess structured timestamps by parsing free-form notes.
- Explain that timed reminders require structured event data.

==================================================
5. IMPORT / STORAGE
==================================================

- Reuse current import/storage conventions.
- Validate fully before committing.
- Invalid imports leave existing data intact.
- Reject or clearly report unknown Asset IDs and broken event references.
- Validate dates, timezones, numeric units, tiers, and field types.
- Treat imported text as plain text, never HTML.
- Store weekly snapshots separately from Quarterly Macro.
- Retain prior weeks.
- Do not change selected Assets, Notes, plans, or positions during import.
- Same-week reimport updates that week’s snapshot.
- Omitted Assets in an accepted snapshot become No impact data;
  never silently keep stale scores.
- Skill output should normally contain all seven Assets.

RESULT MERGE SAFETY
- Never replace a verified actual with null during a later calendar import.
- Preserve recorded actuals by stable event ID.
- If a newer verified result revises an actual, keep source/time provenance.
- Report conflicting event identities instead of merging by title alone.

FRESHNESS
- Display target week and asof.
- A different week must be labeled and not used as current-week data.
- A matching week alone does not prove freshness.
- Show the last checked time; do not claim automatic live updates.

==================================================
6. WEEKLY IMPACT PANEL — COMPACT DEFAULT VIEW
==================================================

Keep the title “Weekly Impact.”

Default layout:
Weekly Impact                         [Paste]
[week range] · ICT
Updated [asof]

[● XAUUSD  ＋] [● USDJPY  ＋]
[● US      ＋] [● BTC     ＋]
[● BRENT   ＋]

› LOW / ไม่มีข้อมูล · n

- Two columns on iPhone when they fit without shrinking text.
- Fall back to one column when necessary.
- No separate HIGH/MED headers that consume vertical space.
- HIGH red/orange first, MED amber next.
- Preserve configured order within tiers.
- Keep HIGH/MED visible.
- Combine LOW and Unknown in one collapsed group.
- Inside that group retain distinct labels:
  LOW versus No impact data.
- Hide empty groups.

ACCESSIBILITY
- Colored indicators have accessible HIGH/MED/LOW labels.
- Expanded details display the full tier label.
- Do not rely exclusively on color to communicate status.

INTERACTIONS
- Tap Asset name → expand details.
- Tap ＋ → select Asset.
- These are independent actions.
- Selected state is ✓, with an accessible label.
- Prevent duplicate selection.

EXPANSION
- Open at most one Asset detail panel at a time.
- Details span the full width directly below the tapped two-column row.
- Tapping the same Asset collapses it.
- Tapping its neighbor replaces content in the same detail location.
- Tapping an Asset in another row moves the detail panel below that row.
- Preserve keyboard focus and selection state.
- LOW/Unknown Assets remain selectable.
- Collapsing the group must not hide already selected Strategy cards.

EXPANDED CONTENT
Asset · full Impact label

ข่าวที่ต้องจับตา · เวลาไทย
[Event name + short Thai meaning]
[date/time + metric basis + reference period]
ตลาดคาด [forecast] | ครั้งก่อน [previous]

ถ้าสูงกว่าคาด
[understandable conditional interpretation]

ถ้าต่ำกว่าคาด
[understandable conditional interpretation]

ถ้าใกล้เคียงคาด
[interpretation]

สิ่งที่ควรดูหลังประกาศ
[one specific observation]

Adapt scenario labels to qualitative events.
Show additional events/carryover only when relevant.
Keep sources and checked-at details accessible without crowding the default view.

==================================================
7. SELECTED STRATEGY CARDS
==================================================

Keep:
Asset                                      [+ Plan]

Weekly Impact · [week range]
[Impact] [main event + ICT time]             [More]
Expanded: same event facts, scenarios, and reaction note as above.

Quarterly Macro · [quarter/year]
[existing Playbook content]

Change if · Quarterly
[existing quarterly invalidation conditions]

Note · This week
[editable text]
[Copy last week]                         [Clear Note]

- Use shared weekly data across the panel, ＋ Asset sheet, and cards.
- Do not copy event text into Note.
- Show Unknown distinctly from LOW.
- No chart/image links or attachments in this Strategy content.
- Remove old Strategy Trend/Zone/Shift controls if still present.
- Preserve historical fields and shared calculations used elsewhere.
- Keep trading-plan Trend/direction controls unchanged.

NOTE
- No automatic carry-forward.
- Copy the same Asset’s previous-week Note only on request.
- Hide/disable copy when no prior Note exists.
- Confirm before replacing a non-empty current Note.
- Keep copied text editable.
- Clear affects only this Asset’s current-week Note.

==================================================
8. TODAY — EVENT REMINDERS
==================================================

V1 reminders are IN-APP ONLY.
No push notifications, background delivery, or automatic release-data feed.

Use structured events associated with currently selected Strategy Assets.
Deduplicate shared events:
one event row lists all selected affected Assets.

Default:
ข่าววันนี้ · เวลาไทย

19:30  Core PCE                 [อีก 30 นาที]
กระทบ: XAUUSD · USDJPY · US · BTC
ตลาดคาด 2.6% | ครั้งก่อน 2.7%
[อ่านผลข่าว]

Illustrative values only; never hardcode mockup data.

STATUS RULES
- On the event’s ICT calendar day: show under “ข่าววันนี้.”
- Within 30 minutes before a confirmed scheduled time:
  highlight “ใกล้ประกาศ.”
- At scheduled time with no actual:
  “ถึงกำหนดประกาศ · รอข้อมูลจริง.”
- After the scheduled time with no actual:
  “รออัปเดตผล.”
- Never infer that a release occurred just because its time passed.
- Once actual is verified and recorded:
  show Actual / Forecast / Previous and the numerical difference.
- Do not color a surprise as good/bad for an Asset automatically.

DATE BOUNDARIES
- An event within the next 30 minutes must appear even if it falls
  just after midnight on the next ICT day.
- Date-only / tentative / unknown-time events display their uncertainty;
  do not create precise countdowns.
- Cancelled events do not trigger alerts.
- Postponed events show their status and only use a verified replacement time.

AFTER THE DAY ENDS
- Keep elapsed events without verified results in a collapsed
  “รออัปเดตผล” section for the active week.
- Do not silently lose pending results at midnight.
- Released past events can remain in the week’s event history,
  without crowding Today.

APP LIFECYCLE
- Refresh status when Today opens, the app resumes, or the tab regains focus.
- While visible, update at a modest interval and at relevant time boundaries.
- Clean up timers; do not duplicate them on repeated renders.
- No repeated popups or audible alarms required.

MANUAL RESULT UPDATE — V1
- Provide an on-demand “อัปเดตผล” action.
- Record actual, source URL, and update time.
- Keep metric, unit, period, forecast, and previous visible to avoid mismatch.
- Allow verified previous-value revisions without losing provenance.
- Missing actual stays null.
- Do not fabricate an actual or assume a headline confirms all submetrics.
- For speeches/qualitative events, record verified completion/summary;
  do not require numeric actual.

Actual − Forecast is a numeric surprise, not an automatic trading signal.
Do not revise trade plans or Quarterly Macro from this difference.

==================================================
9. PREVIOUSLY AGREED FIXES — ONLY IF STILL OUTSTANDING
==================================================

IPHONE CORE | SAT
- Adjacent buttons visible from first render.
- No dropdown or interaction required to reveal both.
- Preserve remembered selection.
- Do not change Mac appearance unnecessarily.

START NEW WEEK
- Remove the old blocking Asset/data carry-forward prompt.
- Preserve required initialization, history, plans, and open positions.
- Apply the Note rules above.

MOBILE READABILITY
- Main expanded content approximately 16px with comfortable line spacing.
- No global font enlargement.
- Flow quarterly Macro summary can wrap.
- Expanded content is fully accessible without horizontal overflow.
- Preserve working Mac layouts.

TODAY → SAT PLAN
- No selected Assets:
  “Start by adding a Strategic Asset” + navigation to Strategy selection.
- Selected Assets without an active/current plan:
  identify them and offer plan creation.
- Existing plans:
  preserve relevant actions, without duplicate missing-plan warnings.
- Closed/cancelled plans do not count as current.
- Keep management access to open positions whose Assets are not selected.
- Do not reintroduce removed Strategy Bias controls.

==================================================
10. VALIDATION / COMPLETION
==================================================

Verify:
- PF1/PF2 gate satisfied before Dashboard changes.
- Skill output maps to exactly seven configured Assets.
- Supported scoring; no automatic upgrade from price momentum.
- Correct reference periods, units, timezones, and null handling.
- Shared events remain consistent across all surfaces.
- Import failures preserve data.
- Reimports preserve verified actuals and historical weeks.
- Legacy imports work without fabricated reminders.
- Two-column rows, one expanded detail panel, and separate Select actions work.
- LOW/Unknown share a toggle but remain distinguishable.
- Notes copy/clear safely.
- Weekly and Quarterly data remain clearly separated.
- Today handles 30-minute alerts, midnight, resume/focus, missing actuals,
  revised schedules, cancelled events, and manual result updates.
- No duplicate timers or duplicated shared-event alerts.
- iPhone has no clipping or horizontal overflow.
- Mac, Risk, trade sizing, plan direction, positions, and quarterly imports
  are unaffected outside the explicit scope.

Use sample data only in mockups/tests and label it clearly.
Do not ship sample event schedules, consensus numbers, or impact tiers
as real production data.

---

## Part B — Orchestrator notes

### B1. Conflicts with PF1 / PF2 / earlier messages (WM1 wins; implement as stated here)
| # | Earlier | WM1 (final) | What to do |
|---|---|---|---|
| 1 | PF1 A1: Strategy keeps the image with caption `ภาพ Week with EMA50` + delete button | §7: **no chart/image links or attachments** in Strategy | Remove the image strip / TradingView link / add-image entry from the Strategy card. Keep `w.chart` data stored (other views may read it — report any). |
| 2 | PF1 B4: label `ความคิดเห็นเรา` · link `คัดลอกจากสัปดาห์ก่อน` + `เอาออกจากสัปดาห์นี้` | §7: `Note · This week` · `[Copy last week]` `[Clear Note]` | Rename label. Copy = same asset's previous-week `opinion_txt`, hidden/disabled when none, **confirm before replacing non-empty**, result editable. Clear = this asset, this week only. `เอาออกจากสัปดาห์นี้` (unpick asset) stays as a separate small action — it is asset selection, not Note. |
| 3 | PF2 B2 (decided 25 Oct): link `นำเข้าความเห็นสัปดาห์ก่อน` shown **only when the box is empty** | §7 Note rules (copy shown whenever last week has a Note; confirm if current is non-empty) | Follow WM1. If PF2 already built the empty-only link, change it to WM1 behaviour. |
| 4 | Earlier user message (before the final handoff): Weekly Impact panel "do not duplicate the full Asset list"; JSON `{week, assets:{impact, note}}` | §6 panel shows HIGH/MED asset chips with ＋, LOW/Unknown folded; §4 `weeklyImpact/v2` | Follow §6 / §4. v1 `{week, assets{impact,note}}` stays importable (§4 backward compatibility) without reminders. |
| 5 | PF2 B4 Today Sat card (states A/B/C) | §8 Today "ข่าววันนี้" event block | Both exist: Sat plan card (A/B/C) and a separate compact "ข่าววันนี้ · เวลาไทย" block. Order on Today: time-critical news first only when an event is ≤ 30 min away; otherwise after the Sat card. No duplicate Sat cards. |
| 6 | Strategy weeks are keyed **Sunday** (`wpWeekKey` = Sunday 00:00, Sun–Sat) | §2/§5: weekly `week` = **Monday** (Asia/Bangkok) | Store Weekly Impact by its Monday key. Mapping helper: Strategy week key `S` (Sunday) ↔ impact week `S + 1 day`. "Outdated" = imported Monday ≠ Monday of the active Strategy week. Test the Saturday/Sunday boundary (Sunday is the first day of the app week but the impact week starts Monday). |
| 7 | App Sat asset keys: built-in `XAUUSD`, `BTCUSD` (label BTC), `S50`, `BRENT` (label Brent); XAG / USDJPY / US exist only if the user added them as custom assets (`satCustomAssets`); Playbook uses keys like `US` | §2 universe `XAUUSD, XAG, BTC, BRENT, USDJPY, S50, US` | Map JSON keys through existing labels/aliases (`BTC` → `BTCUSD`, `Brent`/`BRENT`). Keys that are not app assets → reported as unknown, **not created**. Report what `US` is in the user's app (custom asset label/unit, Playbook asset) — do not guess S&P vs Nasdaq. |
| 8 | Quarterly Macro data lives in `macroPlaybook` (create-only rules) | §5 store weekly separately | New collection **`users/{uid}/weeklyImpact/{YYYY-MM-DD}`** (one doc per Monday). Needs **Firestore rules** (see B2) before it can save. Same-week reimport = update; manual actual = update. |
| 9 | PF1 Strategy shows Macro + `เปลี่ยนเมื่อ` | §7 labels `Quarterly Macro · [quarter/year]`, `Change if · Quarterly` | Rename the labels; content unchanged; PF2 iPhone clamp + More stays. |

### B2. Firestore rules (blocking — user must publish first)
Rules file: `~/Projects/Research-team/firestore.rules` (not in Dashboard). Without a rule every save fails with `permission-denied` (same as the macroPlaybook v2 incident). Add, next to the macroPlaybook block:
```
match /users/{uid}/weeklyImpact/{week} {
  allow read: if request.auth != null && request.auth.uid == uid;
  allow create, update: if request.auth != null && request.auth.uid == uid
    && week.matches('^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
    && request.resource.data.schema in ['weeklyImpact/v1', 'weeklyImpact/v2'];
  allow delete: if false;
}
```
Claude Code: show this block in the report; do not deploy. The app must show a clear message on `permission-denied` (reuse the pbSave pattern) and keep the pasted text.

### B3. Anchors (reuse)
- Paste/validate/preview/save pattern: Playbook paste sheet (`pbPaste*`, `pbCheck`, `pbSave`, `Calc.pbValidate`) → copy the pattern into a `Calc.wiValidate` (pure, testable) + `wi*` UI; do **not** touch Playbook code paths.
- Collection access: `sat7dCol('weeklyImpact')` + a listener next to the `macroPlaybook` one (read-only handler).
- Asset list / select: `satAssets()` · `satWeekPickAdd` / `waPick` · `＋ Asset` sheet `waSheetOpen` / `waListHtml` (add badge + driver line + sort HIGH → MED → LOW → no data, stable within group).
- Strategy card: PF1's Lean tile (`ln1TileHtml`) — add the Weekly Impact strip above Quarterly Macro.
- Today: `todayRefresh` task model (`mkTask`, `guard`) for "ข่าววันนี้"; one interval timer guarded against duplicates (clear on hide / re-render); `visibilitychange` + `focus` refresh.
- Backup: add `weeklyImpact` to `BK_COLS` / backup payload (BK1 pattern) so weekly data is included in backups.

### B4. JSON contract — fix it before the skill is written
- Implement exactly Part A §4 (`schema: "weeklyImpact/v2"`). Add a `basis` field on events (e.g. `"YoY"`, `"MoM"`, `"QoQ SAAR"`) rather than packing it into `metric`.
- Put the final contract in `docs/weekly-impact-schema.md` (fields, types, required/optional, one **clearly labelled sample** with placeholder values, the v1 legacy shape). The orchestrator writes the skill from this file.
- Manual "อัปเดตผล": writes `actual`, `actual_updated_at`, `actual_source` (URL) on the event inside that week's doc; previous revision keeps `previous_original` + source. Re-import merge: keep a non-null verified `actual` (and its provenance) when the incoming value is null; conflicting event IDs → report, don't merge by title.

### B5. Lean UI notes
- Panel default height on iPhone ≈ head (2 lines) + chip rows + 1 fold line. Chip = dot + asset + ＋ (✓ when picked), two columns when each chip text fits at the normal size; otherwise one column (never shrink below the app's body size).
- Tier colours: HIGH = existing red/orange token, MED = amber, LOW = grey; label text always present (`HIGH`/`MED`/`LOW`, `ไม่มีข้อมูล`).
- One detail panel open at a time, inserted after the row of the tapped chip (full width).
- `Times: ICT (UTC+7)` shown once in the panel and once in the ＋ Asset sheet.
- All imported strings rendered with `escHtml`/`textContent`.

### B6. Tests — `phase100` (Chromium · FF_STUB_BASE = Lean · sample data labelled `SAMPLE`)
- Import: valid v2 → panel, ＋ Asset sheet and selected cards update together; invalid JSON / bad tier / broken `event_refs` / bad timestamp / unknown asset → concise error, stored data unchanged; v1 legacy → readable, no reminders; same-week reimport replaces snapshot, omitted asset → "No impact data", verified actual kept when new value is null; other weeks retained; Monday ↔ Sunday mapping + "Outdated" label; `permission-denied` → message, text kept.
- Panel: tier order HIGH → MED (configured order inside), LOW + Unknown folded with distinct labels, empty groups hidden; 2 columns at 390 when they fit / 1 column at 300; one detail open; neighbour replaces; other row moves; ＋ selects, ✓ state, no duplicate; LOW selectable.
- Strategy card: strip `[HIGH] event · time` + More; Unknown ≠ LOW; no image/link; labels `Quarterly Macro · …`, `Change if · Quarterly`, `Note · This week`; Copy last week (hidden when none, confirm when non-empty, never edits last week) and Clear Note.
- Today: event today → listed once with all affected selected assets; ≤ 30 min → `ใกล้ประกาศ`; at time → `ถึงกำหนดประกาศ · รอข้อมูลจริง`; after → `รออัปเดตผล` and kept past midnight in the collapsed section; event 00:10 next day appears at 23:45; date-only/tentative → no countdown; cancelled → no alert; postponed → status; manual `อัปเดตผล` records actual + source + time, shows Actual / Forecast / Previous + difference without good/bad colour; timers not duplicated after 5 re-renders; resume/focus refresh (fake clock).
- 300 / 390 / 1440 no horizontal overflow; Mac unchanged elsewhere; no console error.
- Screenshots `tests/screenshots/wm1-{panel-390,panel-detail-390,panel-300,addasset-390,card-390,card-1440,today-390,today-1440}.png` — open and check every one.
- Old tests: never delete/weaken; update only expectations this brief changes (log in `tests/WM1_retired.md`). Full run once at the end (base + phase 1–100), one suite at a time, `caffeinate -i -s`.

## Report back
Gate check result · ≤ 8-bullet plan · changes per Part A section · conflicts B1 handled · Firestore rules block (B2) · `docs/weekly-impact-schema.md` · files changed · test results · screenshots opened · what `US` (and XAG/USDJPY) map to in the app · remaining limitations · no push, no file deletion.
