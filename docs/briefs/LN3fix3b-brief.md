# LN3fix3b — Watch "expand detail" (Mac) · Flow Macro head fix · New-week clear fix · tests 95

> User request 22 Oct, after LN3fix3 cloud verification. **Design = mockup** `docs/mockups/ln3fix3b-mockup.html` (view at 1280 and 1440; it is clickable — try F / ⤢, ← →, ↑ ↓, Esc). **User chose Full screen** (detail covers the whole screen, app header hidden). Yellow note boxes are explanations — do not build them.
> Objective: Simple · Clear · Easy to use · Effective. **Do not change formulas / caps / blocking rules.** Never delete features. Legacy view (`ln1_plan_view = legacy`) unchanged. Mobile (< 1024px, `wlNarrow()`) unchanged.
> Continue from LN3fix3 (index sha `3375f6bd…`). Backups: `index.backup-pre-LN3fix3b.html` · `tests/_bk_ln3fix3b/` · do not touch core-size.js · every temp file (including your own) → `_to_delete/` · **never rm**. UI text stays Thai as in the mockup.

## 1. Watch — expand the detail column (Mac ≥ 1024px · Watchlist, Ideas and Candidates)
- **Button** icon-only `⤢` (tooltip/aria-label `ขยายเต็มจอ (F)`) in the detail header, next to the existing `⋯`, same size as `⋯`. Shortcut **F** (`e.code==='KeyF'`, no Ctrl/Cmd/Alt, not while typing in an input/textarea, not when a menu/sheet/popup is open — same guards as the existing ←/→ handler). While expanded it shows `⤡` (tooltip `ย่อกลับ (Esc)`, primary style).
- **Expanded = Full screen:** the detail covers the whole window (`position:fixed; inset:0`, above everything) — list, app header and top tab bar hidden. **No browser Fullscreen API** (no `requestFullscreen` — instant, no macOS Space animation; the user can press Ctrl+Cmd+F if they want). Body behind must not scroll. On expand show a **toast for ~2 s**: `เต็มจอ · ← → เปลี่ยนหัวข้อ · Esc = ย่อกลับ` (no permanent hint bar).
- **Keys while expanded:**
  - `↑ / ↓`, mouse wheel, trackpad = **scroll the detail text only — never change stock/idea** (skip `wlStep` / `ideaStep`; let the browser scroll, or scroll the detail container if it is the scroll box).
  - `← / →` = switch sections (สรุป → มุมมอง → …) exactly as today.
  - **Esc** or `⤡ ย่อ` = collapse → back to list + detail, **same item, same section, same scroll position**. Hook into the existing central Esc handling (`escCloseTop()` / ESC1) with the right priority: an open popup/menu/sheet/lightbox closes first; the next Esc collapses.
- **Reading width:** article text max ~80ch, centred, while expanded (72ch rule stays in normal view). **Wide tables** (e.g. รายได้แยกส่วน) and long unbroken strings scroll left/right **inside their own box** — no page-level horizontal overflow.
- Expanded state is **not saved**: switching tab, reloading, or going below 1024px returns to the normal view.
- Add `F = ขยาย/ย่อ รายละเอียด (Watch)` to the keyboard help (Shift + ?).

## 2. Flow — Macro card head (Mac · mockup ②)
- LN3fix3 made `.pbHl` wrap **inside** the head row → a long headline becomes a narrow 4-line block next to the chips. Fix (Lean, ≥1000px): head row = `▾ 2026Q4 · ใช้จริง · asset chips`; the **headline goes on its own full-width line below**, 16px bold, wraps, no "…".
- Asset chips in the head **wrap to the next line** instead of being clipped (now "BR ▬" is cut off).
- Give the Macro ไตรมาส card content its normal inner padding (now flush against the card's left edge), and remove the stray "◂" before "Macro ไตรมาส" if it is not a working control (if it is the fold control, keep it but align it).
- Mobile Flow unchanged.

## 3. New week — always clear kept assets (bug, no UI change)
- `nwStart()` clears Zone ▲/▼ · Shift · My opinion · B&P only `if(satwWeek(T, k))` (doc already in memory). If next week's doc exists in Firestore but is not loaded yet, old values survive. Fix: write the clear for **every kept asset unconditionally** (merge write; keep `bias` untouched/empty as now). This also makes phase93 case 4 deterministic (it fails on the cloud because `__seedDoc` doesn't notify listeners).

## Tests (Chromium · FF_STUB_BASE = Lean)
- `phase95`:
  - Watch 1280 + 1440: icon `⤢` present next to ⋯ (tooltip `ขยายเต็มจอ (F)`) · click and F both expand · detail covers the viewport (0,0 → full width/height, ±2px), list + app header/tab bar hidden, body not scrollable · `requestFullscreen` never called (spy) · toast appears and is gone after ~3 s · `↓` while expanded does **not** change the selected stock and the detail scrolls · `→` changes section · Esc collapses → same stock, same section, scroll position kept (±5px) · Esc with a ⋯ menu open closes the menu first, stays expanded · wide table and long URL scroll inside their box, page horizontal overflow = 0 · same for Ideas and Candidates (one case each) · switching tab and back = normal view · F ignored while typing in an input · 390: no expand button, Watch unchanged.
  - Flow 1440: headline is a separate line below the chip row and spans ≥ 90% of the card width, no ellipsis · last chip fully visible (not clipped) · card content left padding ≥ 12px · 390 unchanged.
  - New week: seed next week's doc **without** listener notify (`__seedDoc`) → `เริ่มสัปดาห์` → doc has empty zone_up/zone_dn/opinion_txt, invalidation null, zone_bp false (deterministic, run 3× in a loop).
  - No console error.
- Screenshots `tests/screenshots/ln3fix3b-{watch-1440,watch-fullscreen-1440,watch-fullscreen-1280,flow-1440}.png` — **open and check every one**.

### Old tests
- Never delete or weaken cases; only update expected values this brief changes (log in `tests/LN3fix3b_retired.md`). Update `ไฟล์ที่ห้ามลบ.md`.
- During work: related suites (Watch p85 + other Watch/keyboard suites that use ↑/↓/←/→/Esc · Flow p86/p94 · Sat p93). **At the end:** full run once, one suite at a time (base + phase 1–95).
- Known false failures: p3 on Sundays (re-run with another TZ) · p6 'ยกเลิก 20' on the 20th · p13 missing backup-pre-UI1 — do not edit tests/index for these.

## Report back
What was done per section · your own interpretations · old tests changed · screenshots opened · full-run result · no push, no file deletion.
