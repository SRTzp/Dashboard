# LR1 — Lean redesign step 1: shared styles · top bar · M/F account tags · per-account defaults

Approved by SRTp 18 Nov 2026. Design canvas: "Trading Dashboard — Lean redesign" (claude.ai artifact). Static copies of every artboard: `docs/briefs/lr/*.dc.html` (open in a browser; they are mockups, not code to paste). Goal of the whole redesign: **easy to use, lean, less friction**, every existing function kept.
Base: latest `origin/main`. Branch: `claude/lr1`. Commits: A0 hook inventory → A styles → B top bar → C account tags + defaults → D tests/report, push each.
Later steps (separate briefs): LR2 Today (two-account Act list, glance band) · LR3 Plan + confirm sheet · LR4 Flow (RRG chart with 5-day tails, calendar tab) · LR5 Watch / Journal / Port Both.

## Hard rules (every LR step)
- **Zero feature loss.** Every button, input, filter, table column, chart container and data point stays present and working.
- **Never rename or remove** an `id`, `data-*` attribute, `name`, or inline handler (`onclick`, `onchange`, …) that code or tests use. Move or restyle elements; do not rewrite their contract.
- No data migration except the account-defaults field in C (additive). No deletes. `render()` pure. English UI. No overflow at 1440 / 1280 / 390.
- Lean UI rules: no new panels; each screen same length or shorter (row counts at 390 before / after).

## A0 · Hook inventory (before any change) → `docs/reports/LR1-progress.md`
- `tools/hook_inventory.py`: from `index.html` list every `id`, every `data-*` attribute name (with its literal values where static), every `name`, and every inline handler with its function name. Save `tests/hooks_baseline.json` from `origin/main`.
- `tests/hooks_test.py`: on the branch, the new inventory must be a **superset** of the baseline (allowed: additions). Add to `tests/run_regression.sh`. This runs in every LR step.

## A · Shared styles (CSS only)
CSS variables, used by new rules; old rules may keep their own values until their screen's LR step:
- Ground `#F4F5F7` · card `#FFFFFF` · border `#ECEEF1` / `#E1E4E9` · ink `#14161A` · text-2 `#3D434C` · muted `#5F6672` (≥ 4.5:1 on white).
- Semantic: gain `#12805C`/`#0E6B4C` on `#E5F4EC` · loss `#C2362F`/`#A62D27` on `#FBE9E8` · warn `#9A5B00` on `#FFF4E0`.
- Ports (from TS1b, keep): SAT `#6741B8`/`#EFE9FA` · MMT `#2F5BD3`/`#E8EEFC` · COMP `#0F766E`/`#E3F3F1`.
- Accounts (new): **M** `#14161A` text white · **F** `#B4387A` text white (pill, 11 px bold).
- Type: Inter (Google Fonts) with system fallback; numbers `font-variant-numeric: tabular-nums`; tags JetBrains Mono 11 px. Scale 26 / 18 / 15 / 14 / 13 / 12 / 11.
- Radius 10 (buttons) · 12–16 (cards) · 999 (pills). Buttons: one **primary** style (ink background, white text) for the main action of a row/screen; secondary = white with border; ghost for "more". Touch targets ≥ 44 px on phone. Dark-mode overrides if the app has dark mode.

## B · Top bar (desktop + phone)
- Desktop: logo · sync status · labelled tabs **Today · Plan · Flow · Watch · Journal · Port** (English everywhere; replaces "แผน") · account switch with M/F pills · **+ New plan** (primary) · one **⋯** menu holding the existing icon buttons (tools/settings, skills, imports …) with text labels. Every moved button keeps its id / handler.
- Phone (≤ 560 px): compact header (logo · M/F switch · + Plan) + the existing bottom tab bar with the same six labels; active tab marked.
- Keyboard shortcuts unchanged (`.` / `/` account, `[` `]` filters).

## C · M/F account tags + per-account defaults
- Account pill component (`M` / `F`, colours above) shown next to the account name in the switch, and available for later steps (rows, sheets).
- Confirm sheet (existing): add a prominent account band at the top — `M · Main account · <broker> · <market> · <currency> · records to Main only` (F: magenta) — reading the plan's account. Nothing else in the sheet changes yet.
- **Per-account defaults** (Settings › Accounts, additive field `settings.acctDefaults` per account; migrate nothing):
  - Main: markets US (default) + TH allowed · currency USD (+THB) · ports MMT · COMP · SAT · brokers IBKR, Webull · SAT products XAU, BTC, S50, Brent.
  - Family: market TH · currency THB · ports COMP · SAT (**MMT hidden** in Family views and forms) · SAT products S50, GO (Thai futures).
  - Defaults pre-fill a new plan (market, currency, broker, port list, SAT product list). **Not locks**: the user can switch market in the form (e.g. a Thai Compounder in Main).
  - Hiding MMT in Family hides UI only; any existing Family MMT data stays visible under a "Hidden port: MMT (n)" line, never lost.

## Tests / proof
- `tests/hooks_test.py` (superset) · `tests/run_tests_lr1.py`: top bar tabs + ⋯ menu items reach the same handlers; account pills; confirm-sheet account band text; Family new-plan form has no MMT and defaults to TH/THB; Main defaults US/USD; switching market in the form works; no overflow 1440 / 1280 / 390.
- Node suites unchanged (risk_engine 313 · re1_adapter 63 · re1c_live 88 · rm1_engine 43 · pv1_posview 44 · core_size 502 · ps1 41 · ps1b 44). Full `tests/run_regression.sh` = 0 failing.
- Screenshots (`git add -f`): `lr1-top-1440`, `lr1-top-390`, `lr1-menu-1440`, `lr1-sheet-account-390`, `lr1-family-form-390`.

## Report — `docs/reports/LR1-summary.md`
Hook inventory counts (baseline vs branch) · every moved control and where it went · CSS variables added · per-account defaults field · tests changed and why · row counts at 390.
