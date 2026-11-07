# CG1 — "Copy → what next" toast + mode prefix (2026-11-08)
Branch from main: claude/cg1. UI only, no changes to data or schemas. Spec source: BACKLOG "Copy → what next guide". No mockup (small toast).

## 0. Audit first (report before building)
- List every idea-scout copy button that exists now (file + function), what mode its prompt currently uses, and the first line of the prompt it copies.
- Confirm where candidates store industry + Earnings / Volume Spike flags + their dates.

## 1. Shared toast component
- One function `showGuideToast(lines[])`, reused by all copy buttons (and later by others).
- Bottom-centre, never a modal, max 3 short lines, only a tiny ✕. Never blocks clicks elsewhere.
- Auto-hide: `clamp(5 s, 2.5 s + 60 ms × total characters, 10 s)`. Pause the timer while hovered/touched, resume on leave. Tap anywhere on the toast → close.
- Only one at a time: a new toast replaces the old one and restarts the timer.
- `prefers-reduced-motion` → fade only (no slide). Light/dark theme tokens. 390px: width = viewport − 32px.
- `role="status"`, `aria-live="polite"`.

## 2. Prompt prefix = mode
- Every copied prompt starts with `idea-scout <mode>:` on line 1 (scan / pick / match / update). Rest of the prompt unchanged.

## 3. Guide text per button (show right after a successful copy)
| Button | Mode | Toast lines |
|---|---|---|
| Ideas › New (event idea) | scan | Goal: find who benefits from this event. · Paste in Claude → idea-scout scan → import JSON. · Then tick "เลือกศึกษา" on 1–2 segments. |
| Flow › Fresh card "Ask why ›" | scan | Goal: find the dated reason this sector turned. · Paste → scan → if real driver, tick segments → "pick". · No dated driver = price-only move, ignore. |
| Ideas › Match "copy match" | match | Goal: check if these stocks share one driver. · Paste → idea-scout match. · Shared theme → import it as an idea. |
| Idea card › Export JSON, idea has NO companies yet | pick | Goal: get companies for the ticked segments. · Paste → idea-scout pick → import. · Then move tickers to Candidates. |
| Idea card › Export JSON, idea HAS companies | update | Goal: refresh evidence/status. · Paste → idea-scout update → import. |
- Export JSON picks pick vs update automatically from the idea's data.
- If copy fails → toast "Copy failed — select and copy manually" (no guide).

## 4. Find cluster — DROPPED (SRTp 2026-11-08)
- Candidates have no industry; Ideas › Match already clusters TradingView rows by industry. Match copy gets the guide toast instead (see §3).

## 5. Decisions after §0 audit (SRTp 2026-11-08)
- Line 1 = `idea-scout <mode>:` everywhere, English, colon. Any extra text on that line (e.g. update "· ตอบข้อที่ขาด") moves to line 2.
- Gap-answers (update) and trade-check copies: prefix fix only, no toast.
- Export JSON: copy = line 1 `idea-scout pick:` or `idea-scout update:` (auto: idea has companies → update), blank line, then the JSON. Toast per §3 replaces the fixed text. Keep the manual-copy modal fallback. Any dashboard JSON import must ignore a leading `idea-scout …:` line, so pasting an export back in still works.
- Ask why: replace sdAskToast/sdAskMs with showGuideToast; retired tests → tests/CG1_retired.md.
- Copy failure: "Copy failed — select and copy manually" toast only on paths that use a toast today; keep existing inline/modal fallbacks.

## Tests
- Toast timing: 40-char → 5 s, 200-char → 10 s (capped), 120-char → 9.7 s; hover pauses; new toast replaces old; ✕ and tap close.
- Reduced-motion: no transform animation.
- Each of the 5 toast buttons + gap/trade-check: prompt line 1 = correct mode; correct toast text.
- Export JSON: idea without companies → pick, with companies → update; JSON after line 2 parses.
- 390 / 1440 screenshots of toast in light + dark. Log changed expectations in tests/CG1_retired.md. Draft PR → main. Don't merge.
