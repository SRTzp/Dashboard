# LR3 — Lean redesign step 3: Plan board · confirm sheet · plan forms

Approved by SRTp 18 Nov 2026. Design: `docs/briefs/lr/Plan.dc.html` (desktop), `PlanPhone.dc.html`, `PlacePhone.dc.html` (390). Base: latest `origin/main` **with LR2 merged**. Branch: `claude/lr3`. Commits: A board → B confirm sheet → C forms → D tests/report, push each.
LR rules: zero feature loss; never rename/remove an `id`, `data-*`, `name` or inline handler (`tests/hooks_test.py` green); each screen same length or shorter at 390 (report if not, with reason); English UI; no overflow 1440 / 1280 / 390; `render()` pure; no data migration. Sizing / gates / engine unchanged.

## A · Plan board (active account, as today)
- Header line: `Plans · N planned · N ordered · N holding · open risk X% / 3%` — **open risk = the same per-account value as Today's Act header** (fixes the old "risk in use 0.0%" that ignored Core risk). Port chips All · MMT · COMP · SAT with port-colour dots; **Family hides MMT** (acctDefaults) — a Family MMT plan still shows under a "Hidden port: MMT (n)" line.
- Columns: Planned wider, Ordered narrow, Holding (≈ 5 : 3 : 4). An empty column shrinks to its header + "Nothing here" (no tall empty box). Phone: segmented **Planned · Ordered · Holding** (counts) above the port chips; one column visible.
- Cards keep the PV1b/EF1b content (who · money · orders, Blocked line, Ready text, `Place ›`, ✕, More on tap) restyled with LR tokens; "closest to entry first" in Planned.
- **Waiting** (incomplete) plans: one collapsed row at the bottom of Planned: `Waiting · N need entry or stop ▸`; expands in place.
- **`also in F ›` / `also in M ›`** on a card when the other account has a plan or holding for the same ticker (Sat: same asset) — taps switch account and scroll to it. No link when there is none.

## B · Confirm sheet (Place order — Core and Satellite, all entry points incl. later levels)
Order top → bottom (LR1 account band stays first):
1. Account band (LR1).
2. **Orders to place**: one row per leg in order-ticket form — side (BUY/SELL, coloured), `#qty @ price`, order type, `entry 1/2`; then a STOP row (`Stop 150 · target 175 · sell #40`). Large, tabular numbers.
3. Three tiles: **Risk** (money + % of account) · **Reward** (money + R) · **Size** (effective % + "limited by …" from RM1).
4. Existing items unchanged: Setup line (EF1b), news-window amber line (EF1), replace-pick line, warnings.
5. `More ▾` (size working, FX, limits) · buttons **Not yet** / **Confirm** (primary) · footnote "Records only · place the order at your broker".
Phone: bottom sheet, buttons ≥ 44 px, sticky footer so Confirm is always visible.

## C · Plan forms (Core new/edit, Satellite) — English, tidy, same fields
- All Thai labels/buttons → English (e.g. "ยกเลิก" → Cancel, "บันทึกแผน" → Save plan, "บันทึกร่าง" → Save draft, "แสดงบัญชีอื่น" → Show other accounts). Thai stays only in user content.
- Field order: account pill (LR1) · market (US/TH) · ticker · Entry / SL (+ Entry / + SL) · Targets (optional) · Details ▸ (rest unchanged). Two-column on desktop, one column on phone; labels above inputs; errors under the field.
- Footer: Cancel · Save draft · **Save plan** (primary), sticky on phone.
- Satellite form gets the same tokens and English; EMA50 + Structure (+ MSS when Structure = No) stay in the form (EF1).

## Tests / proof
- `tests/run_tests_lr3.py`: header open risk equals Today's per account; Family hides MMT chip + Hidden-port line; empty column shrinks; phone segmented tabs; Waiting row collapse/expand; `also in` link appears only when the other account has the ticker and switches correctly; confirm sheet order (band · legs · stop · tiles · Confirm) for Core, Sat and a later level; sticky footer at 390; forms have no Thai UI strings (scan form DOM for Thai characters outside user content); Save plan / Save draft / Cancel keep their handlers.
- Hook test · node suites unchanged · full `tests/run_regression.sh` = 0 failing.
- Row count / height at 390 for Plan (before / after).
- Screenshots (`git add -f`): `lr3-plan-1440`, `lr3-plan-390`, `lr3-sheet-390`, `lr3-sheet-1440`, `lr3-form-core-390`, `lr3-form-sat-1440`.

## Report — `docs/reports/LR3-summary.md`
Moved controls · Thai strings replaced (list) · open-risk source · tests changed and why · heights · anything uncertain (ask, keep the rest).
