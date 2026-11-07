# Overnight run summary — TX1 → WK1 (2026-11-07/08)

Both rounds finished and are pushed. Nothing merged. Briefs and `wk1-mockup.html` left untracked. Full suite NOT run (per instructions); related suites only.

| Round | Result | Tests | Branch / commit | Compare URL |
|---|---|---|---|---|
| TX1 | ✅ done | new phase365 **68/68** · related 116 (67) 117 (64) 362 (69) 99 (122) 102 (54) 106 (155) 108 (130) 15 (85) all pass · syntax OK · core_size 502/502 · sync OK | `claude/tx1` @ 2477140 (from origin/main fc85d0c) | https://github.com/SRTzp/Dashboard/compare/main...claude/tx1?expand=1 |
| WK1 | ✅ done | new phase366 **86/86** · related 106 (155) 102 (54) 108 (130) 365 (68) 99 (122) 15 (85) 116 (67) 362 (69) pass · phase105 = 186 PASS + a pre-existing Playwright timeout (same result in the earlier full run) | `claude/wk1` @ 5dbed3b (stacked on `claude/tx1`) | https://github.com/SRTzp/Dashboard/compare/claude/tx1...claude/wk1?expand=1 (vs main: `main...claude/wk1` includes TX1) |

## Decisions (details in each report)
**TX1** — `--read-fs/--read-lh` = measured Watchlist stock-data body (.ltMd) 15.64px / 1.65, applied to Brent/Playbook asset sheet, news panel/sheet, AI preview. Whole-card Edit ⇄ Read with one Save; no saved text → Edit; saved + draft → Edit with amber tag. Archive… removed from the card (kept in ⋯, Restore unchanged). Draft = `localStorage tx1.draft.<T>.<field>`, 1 s debounce, leave-page prompt only with drafts. News panel kept at 440px (widening broke an old test). App has no dark theme (dark shots = media emulation). Old tests adjusted: 116, 362 (press Edit first), 99 (phone sheet 17px→15.64px) → `tests/TX1_retired.md`.
**WK1** — one 7-item list (SAT/CORE/OVERVIEW tags, `n/N done · ~45 min`, bar). Fallbacks used: per-item news key = edition + ticker; ⑦ change_if is a manual tick (no hit status stored); ⑥ counts only trades that have a stop and says how many were skipped. ④ merges wk_cands+wk_picks; removed ids wk_macro / wsector / wk_picks. Read state `stockNewsRead[ed] = {readIds}`; old `true` = all read. Daily line is one `<button>`. Old tests adjusted: 106 B4, 102 §2, 362 → `tests/WK1_retired.md`.

## Things to look at
- phase105 times out at `[data-sd-hd="IGV"] .l2 .g` (pre-existing, unrelated).
- `bkDue` (backup reminder) reads localStorage unguarded → throws if storage is blocked (pre-existing; not touched).
- WK1's Mark all read button wraps to its own line at 390px (cosmetic).
- Added helper `tests/run_related.sh` (runs listed suites only, writes logs + final.tsv for `make_verify.sh`) and tweaked `tests/make_verify.sh` to list only untracked files as `[new]`.
