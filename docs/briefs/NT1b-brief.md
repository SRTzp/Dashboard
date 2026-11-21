# NT1b · Ideas you don't forget — Today follow-up box · next step · price level · idea → plan trail

Decided by SRTp 21 Nov 2026 (“if I don't see an idea, I forget it”). Scope: Watch › Ideas — **AI generated and My ideas**. Plan board unchanged. **No phone reminders.** Spec: mockup `docs/briefs/lr/IdeasFollowUp.html` (parts) + full-page Today `lr/TodayIdeasV5.html` (**final for Today**, approved 21 Nov — built on the real current Today; blue numbers ①–⑥ = §6 fixes; V4 / V3 / V2 / `TodayFull.html` superseded) and `lr/WatchIdeasFull.html` (My ideas list + detail with the Next step block above the chart). Non-NT1b parts in the full pages are context only — don't change them. Build **after NT1 is merged**: git fetch, new worktree from fresh origin/main (`claude/nt1b`). Same UI rules as NT1 (light, English, one primary per row/screen, tags mono grey, 44px phone targets).

## 1. Every idea has a next step and a check date
- My ideas sheet (NT1 §1) gets one green-tinted group at the end, before Save: **Next step** (one line ≤ 120, optional) · **Check again on** (NT1 field, now **pre-filled +3 trading days** on new ideas, can be changed, not empty) · **Price level** (optional number; only when the subject is a stock or Sat asset; hint `remind within 3%`).
- AI generated ideas: use their existing next-check / event date (idea@1 / trade@1); trade ideas with an entry level use it as the price level. No new AI fields.
- Data: add `next` (string|null), `level` (number|null), `snoozeTo` (date|null), `planId` (string|null), `dropped` (bool) to `ideas_my`; AI ideas store `snoozeTo` / `done` in their existing doc. Old ideas without a check date get one = created + 3 trading days (computed, not written until edited).

## 2. Today › “Ideas” card (right column, top: Ideas → To do → Risk room)
- Act rows, To do and Risk room keep their content (Market mood + Hot sectors become the status card, §5; small fixes in §6). The new card uses the same card style as To do / Risk room (title 17px bold + count, rows with the 62px tag column).
- Lists **due** ideas from both sources, **max 3**, one line each + the next step under it:
  - row: subject tag · title · reason pill · **one button** (outline; ⋯ actions via header menu / hover, see §6.6)
  - reason pill: price within 3 % of level → blue `1.8% to level`; check date today → amber `check today`; overdue → amber `2 days late`; AI idea → grey status (`needs evidence 2/4`).
  - button: price near level (stock) → `Make plan ›`; My idea → `Open ›` (review Right/Partly/Wrong stays inside Open, NT1 §3); AI idea → `Add evidence ›` / `Open ›`.
  - ⋯: `Snooze 3 days` · `Snooze 1 week` · `Done — nothing to do` (moves the check date +3 trading days) · `Drop idea` (red, Undo toast).
- Order: price near level → overdue → today → AI next check; ties newest first.
- Header: `Ideas` + amber `n due` + right `n open · All ›` (opens Watch › Ideas). Each row = 2 lines: line 1 tag · title · reason pill · one button; line 2 `Next: …` muted. Nothing due → the card is **one line**: `Ideas · none due · n open · All ›`.
- This box **replaces** NT1's per-idea Today › To do line (`IDEA · Check: … — right?`) so the same idea never shows twice; the To do cap is unchanged.

## 3. Watch tab count
- Top nav `Watch` shows a small amber count pill when ideas are due (`Watch 3`); none due → no pill. Phone bottom nav: same pill.

## 4. My ideas list — next step and trail
- List row adds: `Next: <next step> · due <date>` (amber only when due) and a trail `Idea → Plan → Holding` (step green with ✓ when reached: Plan = a plan linked by `planId`, Holding = that plan has a fill).
- `Make plan ›` (Today and idea detail) opens the plan editor with ticker (+ level as entry when given) filled and the track from Watch; on save it stores `planId` on the idea, so the trail updates by itself.
- **Stale ideas:** no check, edit or plan for 30 days → under the row once: `Still valid?` `Keep · check in 1 week` · `Drop`. Keep moves the check date; Drop as above. Asked once per 30 days.
- Filter chips add `Due` (first after All).

## 5. Today top: one status card + hide empty Check orders
- **Replace** the two top cards (Market mood · Hot sectors) with one status card **in the left column, above Act** (same width as Act). The right column starts at the top of the content, so the Ideas card sits level with the status card. Rows in this order (label column 62px, one line each):
  - `MOOD` regime pill (`Risk-off` amber · Risk-on green · Neutral grey) + `new entries at 60% size` + muted `Goal · Main +4.2% of 15%` + small bar on the same line (no separate GOAL row)
  - `TODAY` today's HIGH/MED key events (existing model), red/amber dot, `in 6h 48m` pill when < 8h, past events faded; none → row hidden
  - `HOT` leading sectors vs SPY as green chips (max 3, then `+n`) + muted `↥ Robotics · ↘ Semis · ↘ Tech` on the same line (same data as today's Hot sectors card)
  - `MACRO` Playbook one-liner (▲/▼/▬) + `Playbook ›`
  - **Leave out** anything already shown elsewhere: weekly risk / room (Risk room card), open risk (Act header), port status (Act). Labels 11px uppercase Inter grey (no serif), body 14px, same card style as Act.
- **Act › CHECK ORDERS:** when 0 working, hide the whole section (heading + “Nothing to check”). Shown again as soon as one order is working.
- Data and links unchanged (Playbook ›, sector tap → Flow, event tap → details as today).

## 6. UIUX fixes for the whole Today page (approved 21 Nov, mockup V5 ①–⑥)
1. **One dark primary button on the page = Act.** Ideas card buttons (`Make plan ›`, `Open ›`, `Add evidence ›`) are secondary (outline), even when the idea is near its level.
2. **Colour meaning:** red only for money lost / overdue risk. To do `homework · n stocks` → amber (to-do colour), not red.
3. **No duplicate homework message in Act:** remove `size limited to 50% · homework not done` from Act rows. Compounder holding without homework → muted `Homework → unlocks adds ›` in the button slot (PC2 §2e text); a planned next entry shows `Place ②` (PC2). Momentum keeps PC2's `Homework 0/2 · #17 when done`. To do keeps the one summary row. (If PC2 is not merged yet, rebase on it — PC2 owns the sizing; NT1b only removes the old text.)
4. **Risk room = one line per account:** `M  MMT 1.6% · SAT 0.8% · COMP 5.4/6%`, `F  SAT 0.8% · COMP 6/6%` (room left this week, tags as now; regime note moves to the tooltip / Details). Goal: the whole Today fits 1440 × 900 without page scroll with the sample data (3 ideas, 4 To do rows, 2 Enter + 2 Manage rows, Check orders hidden).
5. **Status card order:** MOOD (+ goal) · TODAY · HOT · MACRO (see §5).
6. **Same pattern in every Ideas row:** each row has exactly one real button (no row with only ⋯); the ⋯ menu (Snooze / Done / Drop) sits in the card header and on row hover / long-press. Distance wording `1.8% to level` (matches Act's `to entry`), not `away`.
- **Phone (≤ 700px) order:** status → Act → Ideas → To do → Risk room.

## Proof
- `tests/run_tests_nt1b.py`: sheet fields + default +3 trading days + level only for stock/Sat · Today box picks due items from both sources, max 3, order rules, reason pills, one button per row, ⋯ actions (snooze 3d/1w, done, drop + Undo) · one-line state when none due · NT1 To do idea line gone (no duplicates) · Watch count pill on/off · list trail Idea → Plan → Holding via Make plan · stale prompt after 30 days, shown once · Due filter · 360/390/1440 no overflow · Today: status card in the left column above Act with rows MOOD (+goal) / TODAY / HOT / MACRO, Ideas card top aligned with the status card (±4px), no Risk/room duplicate in it, TODAY row hidden with no events, CHECK ORDERS hidden at 0 working and shown at 1, To do rows unchanged except the amber homework colour, Ideas card first in the right column · §6: exactly one dark primary on Today (in Act), Ideas buttons outline, homework row amber, no `size limited to 50%` text, Risk room 2 lines (one per account), 1440×900 no page scroll with the sample data, `to level` wording, phone order status → Act → Ideas → To do → Risk room.
- Side-by-side vs the mockup (`tests/screenshots/nt1b/`, `git add -f`, ONLY those) · hooks superset PASS · one clean `JOBS=2 bash tests/run_regression.sh` · `docs/reports/NT1b-summary.md`.
