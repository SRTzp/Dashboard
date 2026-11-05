# HD1 — Plan & Port secondary controls move into the existing header (Mac + iPhone) · Journal unchanged · tests 97

> User request 24 Oct. **Design = mockup** `docs/mockups/hd1-mockup.html` (view at 1024, 1280, 1440, 1920 and 300, 390; pink dashed line = centre of the content container). Yellow notes are explanations — do not build them. UI text stays Thai.
> Objective: Simple · Clear · Easy to use · Effective. **No business logic / formula / filter-behaviour change.** Never delete features. Legacy view (`ln1_plan_view = legacy`) unchanged. Only the header, Plan and Port are touched.
> Continue from LN3fix3c (index sha `11bed72a…`). Backups: `index.backup-pre-HD1.html` · `tests/_bk_hd1/` · do not touch core-size.js · every temp file (including your own) → `_to_delete/` · **never rm**.

## Priority (user): fixed primary-nav position > visual symmetry > compact secondary controls

## 1. One shared header slot (single implementation, not per page)
- Add **one** slot in `header.topbar`, right after `#tabsMain`: `<div class="hdrSub" id="hdrSub">`. Pages do not build their own header logic: a small registry `hdrSubSet(page)` (called from `switchTab` / re-render) **moves the existing control node** into the slot for Plan and Port (Lean) and empties it for every other page. **Never clone or duplicate** a control; the old place is left empty (no gap / no empty row).
  - Plan → the existing `.scopeTabs` (`#scopeStock` / `#scopeFuture`, labels `Core` / `Sat` in Lean, `setPlanScope()`).
  - Port → the existing account switch `.ln3-pseg[data-ln3-accsw]` (`ln3PortSet('all'|acc)`), only when it exists (> 1 account).
  - Today / Flow / Watch / Journal / Settings etc. → slot empty.
  - When the page re-renders the control, keep it in the slot (re-render into the slot, or re-move after render) — still one node.
- Same pill language as the nav, a bit smaller: height = nav pill inner height (≈38px), same radius, `on` = dark pill like the nav; account choices keep the account colour dot. Short account names as in the app (e.g. OUN / FAM).
- State, selection memory and keyboard shortcuts (S / F for scope, etc.) unchanged.

## 2. Desktop header (nav in the top bar = wider than the app's mobile breakpoint, today `max-width:700px`; Mac / iPad) — nav never moves
- Header = **3-column grid** `minmax(0,1fr) auto minmax(0,1fr)` inside the same content container as today (same max width / side padding as the page). Column 1 = brand (logo · Trading · sync) at the left as today; column 2 = `#tabsMain`; column 3 = `#hdrSub` at its **start** (16px after the nav) + the action toolbar `.hbtns` pushed to its **end** (`margin-left:auto`) as today.
- Because columns 1 and 3 are equal, **the nav centre = container centre on every page** (± 0.5px), whatever is in the slot. Do **not** centre nav + slot as one group. Brand and toolbar stay where they are now.
- Slot vertical centre = nav vertical centre (± 1px). Gap nav → slot = 16px on every page.
- **Fit rule (no overlap, no 2nd row):** measure; if the full segmented control would leave < 12px to the toolbar, show the **compact form** in the same spot: one pill with the current choice + `▾` (account dot kept); tapping opens the same choices (a native `<select>` styled as the pill is fine, or a small menu). Re-check on resize (rAF/debounce). Never wrap, never push the nav or toolbar.
- **Where it applies:** the centred 3-column header needs each side column to hold the toolbar (≈192px) → about **≥ 900px** wide. Use one breakpoint constant (e.g. `HDR_DESK_MIN = 900`). Between 701 and 899px (iPad portrait / small windows) keep **today's header and today's in-page controls exactly as now** (slot empty, nothing moves) — no overlap, no new behaviour there. The brand's sync text may ellipsize to keep its column; logo + "Trading" never clipped.
- Note: today the nav is **not** exactly centred at 1000–1100 (it is pushed by the brand); after HD1 it is centred at every desktop width.
- Plan: the old Core | Sat row above the Plan content is gone (content moves up). Port: the old รวม | OUN | FAM row below the summary card is gone (cards move up). Mac 2-column Plan grids (`#tabPlan.lf-stock/.lf-future>.planScope` rules) must not leave an empty cell.

## 3. Mobile (≤ 700px, bottom tab bar — iPhone) — same top bar height, one row
- **Plan and Port only:** the control sits in the top bar **in place of the "Trading" title + sync text** (`.brandName`, `#brandSyncTime` hidden on these two pages). The logo stays, and the sync dot (`#acctDot`) stays visible on/next to the logo and keeps `retrySync()` on tap. Toolbar icons unchanged. Top bar height unchanged (measure before/after: equal ± 1px).
- If the full control does not fit (e.g. 300–340px, or long account names) → the same compact pill as on Mac.
- Bottom tab bar unchanged. Today / Flow / Watch / **Journal** top bar exactly as today (title + sync text shown).

## 4. Journal — unchanged
- Journal summary card keeps `OUN | FAM`, `รวม | Core | Sat`, `ทุกปี | ทุกเดือน` and the full-width warning banner exactly as today, on Mac and iPhone. The header slot is empty on Journal.

## Tests (Chromium · FF_STUB_BASE = Lean)
- `phase97`:
  - For 1280, 1440, 1920 (and 900, 1024): on **every** tab (Today, Flow, Watch, แผน Core, แผน Sat, Journal, Port) the `#tabsMain` centre = content-container centre (± 0.5px) and its left x is identical across tabs (± 0.5px); brand left x and toolbar right x identical across tabs.
  - Plan: `#hdrSub` contains `#scopeStock/#scopeFuture` (the same nodes — `document.querySelectorAll('#scopeStock').length === 1`), no `.planScope` row height left in the page; clicking Sat/Core switches scope exactly as before (same state as clicking the old buttons) · Port: slot contains the one `[data-ln3-accsw]`; รวม/OUN/FAM select as before; with 1 account the slot is empty · other tabs: slot empty.
  - Slot: 16px after the nav (± 1), vertical centre = nav centre (± 1), ≥ 12px clearance to `.hbtns`; at 900/1024 (and long account names) → compact pill where needed · 768: header + Plan/Port controls exactly as before HD1 (in-page), still one row, header height unchanged, selecting from it works.
  - iPhone 390 + 320 + 300: Plan/Port top bar height = Today's (± 1px), title/sync text hidden, logo + sync dot visible, control present (full at 390 if it fits, compact at 300), no horizontal overflow; Journal/Today top bar unchanged.
  - Journal (Mac + iPhone): its card controls and warning banner exist and work as before.
  - Switching tabs back and forth 3× causes no change in nav position and no console error. Legacy view: header and Plan/Port as today.
- Screenshots `tests/screenshots/hd1-{plan-1280,plan-1440,port-1440,port-1920,journal-1440,port-1024-compact,plan-390,port-390,port-300}.png` — **open and check every one**.

### Old tests
- Never delete or weaken cases; only update expected values this brief changes (log in `tests/HD1_retired.md`) — e.g. suites that expect `.planScope` above the Plan content or `[data-ln3-accsw]` under the Port summary card; they should find the same node in `#hdrSub`. Update `ไฟล์ที่ห้ามลบ.md`.
- During work: related suites (grep `scopeStock`, `scopeFuture`, `setPlanScope`, `planScope`, `data-ln3-acc`, `ln3PortSet`, `brandSync`, `brandName`, `tabsMain`, `topbar`) + p84 · p88–p92 · p96. **At the end:** full run once, one suite at a time (base + phase 1–97), keep the Mac awake (`caffeinate -i`).
- Known false failures: p3 on Sundays (re-run with another TZ) · p6 'ยกเลิก 20' on the 20th · p13 missing backup-pre-UI1 — do not edit tests/index for these.

## Report back
What was done per section · your own interpretations · old tests changed · screenshots opened · full-run result · no push, no file deletion.
