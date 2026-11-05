# LN3fix3 — Lean Macro box · New-week reset · Zone order + Break&PB · Macro re-check reminder · Mac layout polish (Today / Flow / Watch) · tests 93–94

> User feedback 22 Oct after using LN3fix2 on a MacBook. **Design = mockups** `docs/mockups/ln3fix3-mac-mockup.html` (view at 1280 and 1440) and `docs/mockups/ln3fix3-plan-mockup.html` (view at 300 / 390 / 1440).
> Yellow note boxes, the "สลับ" toggle button and the "คงไว้ / ตัดออก" folds are explanations — do not build them, but follow what they list. Numbers in mockups are examples.
> Objective: Simple · Clear · Easy to use · Effective. **Do not change formulas / caps / blocking rules.** Never delete features (move/fold is fine). Legacy view (`ln1_plan_view = legacy`) must stay unchanged.
> Continue from LN3fix2. Backups: `index.backup-pre-LN3fix3.html` · `tests/_bk_ln3fix3/` · do not touch core-size.js · every temp file (including your own) → `_to_delete/` · **never rm**.
> UI text stays Thai as in the mockups.

## 1. Strategy asset tile — Lean Macro box (Sat plan tab · mockup section ①)
- **Remove the fold "รายละเอียด Macro"** and everything in it from Lean view: duplicate Macro summary lines · `Trend ✎` editor · duplicate `Macro ▼` · the ▲▬▼ opinion tally (`รวม ▲0 ▬0 ▼1 · ประเมินแล้ว 1/2`) · `เหตุผล 1 ประโยค` · `แนวรับ` / `แนวต้าน` inputs · `⚠️ ยังไม่มี Trend Shift` (the empty Shift field already shows it). Old data stays stored — only hidden in Lean.
- **Show directly (no fold), under the Macro/Zone/Shift rows:**
  - `เปลี่ยนเมื่อ …` — one muted line, read-only, from the Macro Playbook for that asset.
  - `My opinion (Trend + Macro)` — a textarea; one free-text comment for the week. New field `opinion_txt` on the satw week doc, saved on change.
- **Small link row at the bottom:** `ประวัติสลับ Trend (n)` (opens the existing trend_log list — keep it small) · `คัดลอกจากสัปดาห์ก่อน` · `งดเทรด` · `เอาออกจากสัปดาห์นี้`.

## 2. Zone order follows Trend + Break&PB checkbox (mockup ① and plan mockup)
- **Order:** the zone on the Trend side goes first. Trend ▼ (Bearish) → `Zone ▼` row on top, then `Zone ▲`. Trend ▲ (Bullish) → `Zone ▲` first. Flat / not set → `Zone ▲` first. Re-order immediately when Trend changes.
- **B&P (Break & Pullback):** a checkbox labelled **`B&P`** right after the input of the **opposite-side zone only** (Trend ▼ → on Zone ▲; Trend ▲ → on Zone ▼; none when Trend not set). New boolean field `zone_bp` on the satw doc. Meaning: waiting for that zone to break and pull back as an entry.
  - Plan form (Main): when `zone_bp` is ticked, the "อยู่ใน Zone" check may also use that opposite zone (show both zones as choices; default stays the Trend-side zone for the chosen direction).
- **Fit:** the checkbox always stays **inline, directly next to the input — never wraps below it**, at every width (300 / 320 / 390 / 1440). On ≤ 340px tighten only this row: zone input font 13px, horizontal padding 4px, row gap 4–6px, checkbox label 11px. The zone text must not be clipped, including long values like `100,000–102,000` at 300px. No horizontal overflow.

## 3. New week: reset + "which assets to keep?" prompt (mockup ①b)
- **When:** Saturday/Sunday (Thai time) when the coming week has no Strategy yet, or the first open of a new week. Show once per week per account until answered; `ทีหลัง` hides it until next app open.
- **Prompt:** title `เริ่มสัปดาห์ใหม่ · <date range>` · one row per asset of last week with a checkbox (ticked = keep) and a short hint (`สัปดาห์ก่อน ▼ · ถือ n ไม้` / `งดเทรด` / `ยังไม่ตั้ง`). Assets with an open position are always ticked and cannot be unticked. Buttons `ทีหลัง` / `เริ่มสัปดาห์ (เก็บ n)`.
- **Result for kept assets:** **Trend, Zone ▲/▼, Shift, My opinion start empty** (and `zone_bp` false). **Macro stays** (it comes from the Playbook). Old week data is not deleted. The existing `คัดลอกจากสัปดาห์ก่อน` link still copies last week's values on demand.
- **Trend empty rule (also when an asset is added mid-week):** Trend buttons show nothing selected + amber hint `ยังไม่เลือก Trend · สัปดาห์ก่อน ▼ Down`. While empty, `+ แผน` is disabled. The **first** pick needs no reason and is not a flip (not logged as a flip). This fixes Trend being carried over from older weeks.

## 4. Macro re-check reminder (mockup ③ and ②)
- If the active Macro Playbook was neither replaced (`วาง JSON`) nor confirmed for **> 30 days**:
  - Flow · Macro ไตรมาส card: amber bar `⚠ Macro ไม่ได้อัปเดต n วัน (ล่าสุด <date>) — Re-check เดือนละครั้ง · วาง JSON ใหม่ · ยืนยันว่ายังใช้ได้`.
  - `ยืนยันว่ายังใช้ได้` stores `checked_at` (per user) and resets the count without changing content.
  - Today: a task row `⚠ Re-check Macro · ไม่ได้อัปเดต n วัน` → `ไป Flow ›`.

## 5. Mac layout polish (≥ 1000px only · mobile unchanged)
1. **Today:** left column = **เป้าหมาย Port (top)** → การบ้านหุ้น → เช็กแผน Sat; right column = time slots → Re-check Macro (when due) → อื่น ๆ ปกติ. Columns should end at roughly the same height with typical data.
2. **Flow:** Macro ไตรมาส card body text 15–16px (same as Watch detail), column ratio ≈ **1.15 : 1** (Macro : RRG). Asset rows: headline **wraps instead of "…"** (no ellipsis), Bias line below; the arrow column narrow (~36px). `ข้อควรติดตาม · Base / Alt · P1–P4` folded by default.
3. **Watch:** list column **355px** fixed (the narrowest width where `BRK.B · A · P3 · ⛔ Tripwire · ควร update · ●●●` fits on one line); detail takes the rest. Badges wrap only if more than that. Long catalyst text and long unbroken strings wrap — no overflow. Detail article text max ~72ch per line.
4. Also fix: Today task `XAU เติมไม้ 2 ได้…` appears twice without saying which account → add the account name/dot, or merge into one row listing both accounts.

## Tests (Chromium · FF_STUB_BASE = Lean)
- `phase93` (Strategy · new week · Macro reminder · 300 / 390 / 1440): no "รายละเอียด Macro" fold in Lean · `เปลี่ยนเมื่อ` line shown from Playbook · opinion_txt saves/loads · link row present (history count matches trend_log) · zone order flips with Trend (▼ → Zone ▼ first) · B&P only on opposite zone, inline next to the input at 300/320/390 (same row), zone text not clipped, saves `zone_bp`, hidden when Trend empty · plan form can use the BP zone · no overflow · new-week prompt appears on a fake Saturday with last-week assets, open-position asset locked ticked, keep/remove works, kept assets have empty Trend/Zone/Shift/opinion and same Macro, old week docs unchanged · Trend empty → `+ แผน` disabled · first pick creates no flip/log, second pick asks reason (existing rule) · Macro reminder after 31 days (fake clock) in Flow + Today, `ยืนยัน` resets it, 29 days = no reminder · legacy unchanged · no console error.
- `phase94` (Mac layout · 1280 + 1440, plus 390 unchanged): Today left column first card is เป้าหมาย Port; column bottoms within ~15% of each other on the fixture · Flow Macro body font ≥ 15px, headline not ellipsized, Macro column wider than RRG · Watch list width 355 ±1, BRK.B-style row (A · P3 · Tripwire · ควร update · 3 dots) on one line, long catalyst / long URL wrap, no overflow · Today duplicate task shows account or is merged.
- Screenshots `tests/screenshots/ln3fix3-{strategy-300,strategy-390,strategy-1440,newweek-1440,today-1440,flow-1440,watch-1440,watch-1280}.png` — **open and check every one**.

### Old tests
- Never delete or weaken cases; only update expected values that this brief changes (log in `tests/LN3fix3_retired.md`). Update `ไฟล์ที่ห้ามลบ.md`.
- During work: related suites (Sat/LN: p76–p82 · p86 · p90 · p92 · Today p39 · Watch p85 · Flow p86). **At the end:** full run once, one suite at a time (base + phase 1–94).
- Known false failures: p3 on Sundays (re-run with another TZ) · p6 'ยกเลิก 20' on the 20th · p13 missing backup-pre-UI1 — do not edit tests/index for these.

## Report back
What was done per section · your own interpretations · old tests changed · screenshots opened · full-run result · no push, no file deletion.
