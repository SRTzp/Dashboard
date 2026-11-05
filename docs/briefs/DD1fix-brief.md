# DD1-fix — ออกจาก "ฟื้นตัว" ตอน DD ยังลึก + ระยะกันพักซ้ำ 1R · เทส 37 (ต่อ) + core_size_test

> ที่มา: ตรวจ DD1 (2 ต.ค.) ชุดเต็มผ่าน · เจอกรณีขอบใน `ddStep` · ผู้ใช้ตัดสิน 2 ต.ค.
> สำรองก่อนแก้: `index.backup-pre-DD1fix.html` · `core-size.backup-pre-DD1fix.js` · เทสที่แก้ → `tests/_bk_dd1fix/`
> แตะเฉพาะ `ddStep` (core-size.js → `python3 tools/sync_core_size.py`) + `ddEval` ส่งค่าเพิ่ม 1 ตัว + บรรทัดเล็กใน sheet · ห้ามแตะส่วนอื่นของ DD1 / สูตรขนาดไม้

## ปัญหาที่เจอ (รันจริงใน node)
1. recover → ได้ +2R ตอน DD ยัง ≥ 20% (เช่น พักที่ 25% → DD 23%) → คืน `normal` → รอบถัดไป normal → **pause ใหม่ 2 สัปดาห์** (ข้อตีความ 4 ของ CC บอกว่าเข้า reduce — จริงเฉพาะ DD < 20)
2. recover → DD ลึกกว่าตอนออกจากพักแค่ 0.1% (22 → 22.1) ก็ pause ใหม่

## ข้อตัดสิน (ผู้ใช้ 2 ต.ค.)
| เรื่อง | เดิม | ใหม่ |
|---|---|---|
| ออกจาก recover (+2R หรือ DD < 12.5 ติดกัน 2 สัปดาห์) | → `normal` เสมอ (แล้วรอบถัดไปค่อยเข้า reduce/pause ตาม DD) | DD ตอนนี้ ≥ `ddReduce` → **`reduce` ทันทีในรอบเดียวกัน** (×0.5 · งดบันได L ใหม่) · DD < `ddReduce` → `normal` |
| พักซ้ำ (จาก recover หรือจาก reduce ที่มาจาก recover) | DD ≥ `ddPause` และ > DD ตอนออกจากพัก | DD ≥ `ddPause` **และ** DD ≥ DD ตอนออกจากพัก + **1R** (1R เป็น % = RPT ปกติ: Core `riskPct` · Sat `rpt`) |
| reduce ปกติ (ไม่ได้มาจาก recover) | DD ≥ 20 → pause | เหมือนเดิม |

## 1. core-size.js · `ddStep`
- รับเพิ่ม `o.repauseGapPct` (ตัวเลข % · ไม่ส่ง/ไม่ใช่ตัวเลข = 0 → พฤติกรรมเดิม "ลึกกว่า")
- `recoverDd0` (ชื่อคีย์เดิม ไม่ migrate) = **DD ตอนออกจากพัก** · เก็บไว้ตลอด `recover` และ `reduce` ที่ต่อมาจาก recover · ล้างเมื่อเป็น `normal` หรือ `pause`
- เงื่อนไขพักซ้ำ (stage `recover` หรือ `reduce` ที่มี `recoverDd0`): `ddPct ≥ pauseAt − EPS` และ `ddPct ≥ recoverDd0 + repauseGapPct − EPS` (gap = 0 → ใช้ `ddPct > recoverDd0 + EPS` แบบเดิม)
- ออกจาก recover: (+2R หรือ below2) → `ddPct ≥ LO ? to('reduce') : to('normal')` · `entered` = stage ที่เข้าจริง · reduce ที่เข้าแบบนี้ `stageSince = today` (นับ 2 สัปดาห์ติดกันใหม่จากสัปดาห์นี้)
- reduce ที่มี `recoverDd0`: ออกเป็น normal ด้วย below2 เหมือนเดิม (ล้าง `recoverDd0`)
- คอมเมนต์หัวฟังก์ชัน: แก้ข้อ "recover → pause ซ้ำ" ให้ตรงกติกาใหม่

## 2. index.html
- `ddEval`: ส่ง `repauseGapPct: isCore ? cfg.riskPct : cfg.rpt` เข้า `ddStep` (ใช้ RPT ปกติ ไม่ใช่ rptHi)
- `next.recoverDd0` เก็บตามที่ `ddStep` คืน (ตอนนี้อาจมีค่าใน reduce ด้วย) · canon เดิมใช้ได้
- sheet DD: stage `recover`/`reduce` ที่มี `recoverDd0` → บรรทัดเล็ก `พักใหม่เมื่อ DD ≥ {max(ddPause, dd0+gap)}%` (ทศนิยม 2)
- ไม่แตะชิป/แถบ/บล็อก (stage reduce ใช้ของเดิม)

## 3. เทส
### `tests/core_size_test.js` (เพิ่ม · cfg Core 12.5/20/2/2 · gap 1.25)
1. recover · dd0 25 · +2R ครบ · DD 23 → `reduce` (รอบเดียว) · `recoverDd0` 25 · `entered 'reduce'` · sizeFactor 0.5 · allowLadder false
2. ต่อจากข้อ 1: รอบถัดไป DD 23 → ยัง `reduce` (ไม่ pause)
3. reduce · dd0 25: DD 26.24 → reduce · DD 26.25 → `pause` · `recoverDd0` null · pauseUntil = today + 14
4. recover · dd0 22: DD 22.1 → recover · DD 23.24 → recover · DD 23.25 → pause
5. recover · dd0 15 (ออกจากพักตอน DD < 20): DD 20 → pause (เพราะ 20 ≥ 16.25)
6. recover · +2R · DD 14 → reduce · DD 10 → normal (`recoverDd0` null)
7. reduce · dd0 25 · below2 (2 สัปดาห์ที่จบแล้ว < 12.5 · หลังสัปดาห์ที่เข้า) → normal · `recoverDd0` null
8. ไม่ส่ง `repauseGapPct` → พฤติกรรมเดิม (dd0 22 · DD 22.1 → pause)
9. reduce ปกติ (ไม่มี dd0) DD 20 → pause (เหมือนเดิม)
### `tests/run_tests_phase37.py` (เพิ่ม · 1440 + 430)
10. Core recover (seed ddState stage recover · recoverDd0 25 · pause ผ่านแล้ว) + ปิดไม้กำไร 2R แต่ DD ยัง ≥ 20 → ชิป `ลดขนาด ×0.5` (ไม่ใช่ `พักถึง`) · ไม้ W ใหม่ ×0.5 · บันได L ปิด · sheet มีบรรทัด `พักใหม่เมื่อ DD ≥ 26.25%`
11. Sat เดียวกัน (gap = Sat rpt 1.25)
- ภาพ `dd1fix-recover-to-reduce` (1440 + 430)

**เทสเก่าที่ขัด** (เคส ddStep "recover → pause ซ้ำ" ที่ลึกกว่านิดเดียว · "+2R → normal" ตอน DD ≥ 12.5): แก้ความคาดหวังตามตารางข้อตัดสิน (ห้ามลบ ห้ามปล่อยล้ม) + จด `tests/DD1fix_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)

## 4. รัน / รายงานกลับ
`check_syntax` · `sync_core_size --check` · `node tests/core_size_test.js` · `node research-card-test.js` · run_tests + phase 1–37 **ทีละชุด** · รายงาน: จำนวนเคสก่อน → หลัง · diff `ddStep` · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
