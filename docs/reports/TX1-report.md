# TX1 — My Thesis Edit/Read card + readable text size (overnight run, 2026-11-07/08)

Branch `claude/tx1` from `origin/main` (fc85d0c). UI only; saved thesis schema unchanged (`my_thesis {why, exit, updated_at}`, `next_check_date`, `next_check_note`). Mockup file (`claude/mockups/tx1-mockup.html`) was not reachable → followed the brief.

## §0 Audit
**My Thesis fields** (`wlMtHtml`, index.html) — one card per stock, 4 inputs:
| Field | Was | Now |
|---|---|---|
| ① Why buy (`why`) | `<textarea rows=2>` 16px | auto-grow textarea, rows=3 |
| ④ Wrong if (`exit`) | `<textarea rows=2>` 16px | auto-grow textarea, rows=3 |
| Next check (`nc_date`) | `<input type=date>` | same, `--read-fs` |
| What to check (`nc_note`) | `<input type=text maxlength=120>` | same, `--read-fs` |

No other thesis text field exists (Notes/catalysts `wlNoteForm` are separate; AI Thesis is read-only). Save handler = `wlMtSave(sym)` → `watchlist/{T}.update({my_thesis, next_check_*})`; drafts lived in the in-memory `wlMtDraft` only. **Homework done** = `wlReady()` = saved `why` and `exit` both non-blank (+ screening for `ftHwDone`) — only `wlMtSave` changes this. Unchanged.

**Font reference** (measured in Chromium): Watchlist stock-data body = `.ltMd` / summary `dd` = **15.64px / line-height 1.65** (`.92rem`, root 17px) → `--read-fs: .92rem; --read-lh: 1.65`.
Content popups/panels found smaller (desktop, measured/CSS):
| Where | Was | Now |
|---|---|---|
| Macro Playbook asset sheet (Brent) body `.pbSecV` (+ `.pbThesis/.pbScn/.pbWhy/.pbWatchV` in `.pb-sheet`) | 13px (phone ≤480px: 17px/1.5) | token |
| News panel/sheet (`.stk-panel`/`.stk-sheet`): `.stkB` 14/1.55, `.stkHl` 14, `.stkNo` 14, labels `.stkK` 12, `.stkSecH` 12, meta `.wiSm` 13 | | body = token; labels/meta scaled to ≥ 12.5px (`.85×`) |
| My Thesis AI preview `.mtAiT` | 13px | token |
| `.ltMd` (reference itself) | `.92rem/1.65` literal | now uses the token |

## Plan (8 bullets)
1. Backups: `index.backup-pre-TX1.html`, `tests/_bk_tx1/`.
2. `--read-fs/--read-lh` tokens in `:root`; apply to popups listed above.
3. `wlMtHtml` → one Edit/Read card (Read when saved text exists and no draft; Edit otherwise).
4. Auto-grow textareas (`wlMtGrow`: min 3 lines, max 60vh then inner scroll), phone `max(16px, --read-fs)`.
5. Draft autosave to `localStorage tx1.draft.<T>.<field>` 1 s after typing stops (try/catch); restore on load → Edit + amber tag "Unsaved draft · Save / Discard"; `beforeunload` prompt only when a draft differs from saved.
6. Keys: Cmd/Ctrl+Enter = Save, Esc = Cancel (confirm only if changed), double-click on read text = Edit, Edit button (tap) on mobile.
7. Remove `Archive…` from the card (kept in ⋯ menu; Restore unchanged).
8. New suite `tests/run_tests_phase365.py` (68 checks, 390 + 1440) + related old suites.

## Decisions (pre-approved + mine)
- `--read-fs` = measured 15.64px/1.65 (pre-approved). Thesis card = whole-card Edit/Read with one Save (pre-approved). Archive… removed from the card (pre-approved).
- A stock with **no saved ① and ④** opens straight in Edit (nothing to read). Stock with saved text opens Read; a stored draft that differs from saved forces Edit.
- Draft tag shows as soon as the text differs from saved (not only after restore) and hides after Save/Discard; it sits next to the status pill.
- Next check line shows `not set` when empty (brief only specified the filled format).
- Widths: Brent sheet widens to ≤720px on desktop. **News panel kept at 440px** — widening it broke an old `~440px` test (phase102) and the brief says "if needed"; 15.64px text fits.
- The app has **no dark theme** (only a few `prefers-color-scheme` rules), so "dark" screenshots are taken with `emulate_media(dark)` and look identical except the draft tag; I added a dark rule for the tag.
- Pre-existing, not fixed: `bkDue` (backup reminder) reads `localStorage` unguarded → throws when storage is blocked. The localStorage-blocked test only asserts no error comes from thesis code.

## Tests
- New `phase365`: **68/68** (390 + 1440): fields/mode/size, auto-grow to 60vh + scroll, paste/line breaks, draft tag, localStorage draft, refresh restore, Discard, Save → homework, read card contents, Esc/Cmd+Enter, double-click, leave-page prompt only with draft, localStorage blocked, popup sizes (Brent, news panel/sheet) = reference, no overflow/console errors.
- Related old suites: 116 (67), 117 (64), 362 (69), 99 (122), 102 (54), 106 (155), 108 (130), 15 (85) — all pass. `check_syntax` OK · `core_size_test` 502/502 · `sync_core_size --check` OK. Full suite NOT run (as instructed).
- Retired/changed expectations: `tests/TX1_retired.md` (5 rows: 116, 362 ×2 need Edit pressed first; phase99 phone sheet 16–18px → 15.64px; Archive… on card).
- Verify file: `docs/reports/TX1-verify.txt` (`bash tests/make_verify.sh TX1` with `RUNALL_OUT=_to_delete/tx1final`; built from `tests/run_related.sh`, a new helper that runs only listed suites and writes logs + final.tsv).
- Also edited `tests/make_verify.sh` so untracked-only files show as `[new]` (was listing every phase file).

## Screenshots (`tests/screenshots/`, git-ignored)
`tx1-thesis-edit-{390,1440}`, `tx1-thesis-edit-dark-*`, `tx1-thesis-read-*`, `tx1-thesis-read-dark-*`, `tx1-brent-*`, `tx1-brent-dark-*`, `tx1-news-*`, `tx1-news-dark-*`.

## Compare URL
https://github.com/SRTzp/Dashboard/compare/main...claude/tx1?expand=1
