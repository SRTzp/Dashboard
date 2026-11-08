# SK1 — Today: Skills-due line · Weekend default on Sat/Sun · ← → Daily/Weekend (2026-11-08)
Branch claude/sk1 from origin/main. Mockup: docs/briefs/sk1-mockup.html (Project claude/mockups/sk1-mockup.html). Code: tdHtmlLean, td3Mode / td3SetMode.

## 0. Audit (report in PR; build without waiting)
- Where AI Thesis date per Watchlist stock is stored (living-thesis import "data as of"); where Macro Playbook quarter is stored; weekly-impact current-week check (wiCurDoc).

## 1. Skills due line
- Position: one line directly under the Homework row, above the Daily/Weekend switch; shown in BOTH modes. Hidden when nothing is due.
- Look: small muted grey text like the Daily news line (no border, no colour): `Skills due · <item> · <item> · Copy ›` (Copy = existing dashed pill style). Phone 390: items shorten to names only, one row (overflow → "+N").
- Items (rules, ICT):
  - **weekly-impact** — only on **Monday**, when this week's Weekly Impact is missing: `weekly-impact (last day today)`. Sat/Sun are covered by Weekend step ①; from Tuesday it's hidden (week missed — no nagging).
  - **living-thesis** — Watchlist stock with no AI Thesis, or AI Thesis "data as of" > 30 days: `living-thesis: AVGO 35d` (oldest first, max 2 shown + "+N").
  - **macro-playbook-loop** — within 7 days before quarter end (or past it with no new playbook for the new quarter): `playbook: quarter end in 5d`.
  - **weekly-stocks-news** — Saturday + Sunday only, when no edition for this week yet: `weekly-stocks-news`. Hidden Mon–Fri (can still be run any time; also Weekend ③).
  - **idea-scout** — Saturday + Sunday only, when 0 new ideas this week: `idea-scout (0/2 ideas)`. Hidden Mon–Fri (can run any time; also Weekend ⑤).
- Copy ›: copies the prompt for the first item + CG1 guide toast. Tapping an item name copies that item's prompt. Prompts start with the skill name (e.g. `living-thesis update: AVGO`).

## 2. Weekend default
- Saturday and Sunday (ICT) → Today opens on **Weekend**; Mon–Fri → **Daily**.
- Manual switch is remembered for the rest of that day only (localStorage with date key, try/catch); next day the default applies again.

## 3. ← / → keys
- Only when the Today tab is active, no input/textarea/select/contenteditable focused, and no sheet/popup open.
- ← = Daily, → = Weekend. No wrap: → on Weekend and ← on Daily do nothing. Counts as a manual switch (§2).
- Must not affect the existing Watch/Ideas arrow handlers.

## Tests
- Skills due: Sat/Sun + no stock-news edition → shown, Mon → hidden; Sat/Sun + 0 ideas → shown, 1 idea → hidden, Fri → hidden; Monday + no WI → shown; Tuesday + no WI → hidden; Sat → WI not in line; thesis 31d shown / 29d hidden / missing shown; 3 stale → 2 + "+1"; quarter end −5d shown, −10d hidden; nothing due → line absent.
- Copy: first-item prompt + toast; item tap copies that item.
- Default: Sat/Sun → Weekend; Mon → Daily; manual switch kept same day, reset next day; storage blocked → still works.
- Keys: ←/→ switch with no wrap; ignored while typing / sheet open / other tab; Watch arrows unchanged.
- 390 + 1440 screenshots. Retired → tests/SK1_retired.md. Commit, push, compare URL. Don't merge.
