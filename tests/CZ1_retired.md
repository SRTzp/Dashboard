# CZ1 — เทสเก่าที่แก้ความคาดหวัง

เหตุ: brief CZ1 เปลี่ยนค่าเริ่มต้นขนาดไม้ Core (เพดานไม้แรก A 15 / B 10 · Risk/ไม้ 1.25 · เพิ่มเพดานรวม/หุ้น 25) แยกตาม Tier + แก้ `core-size.js`
(firstLot / addLot / DEFAULTS) + ตารางตั้งค่าใหม่แทนช่อง `sCrRisk`
ไม่ลบเคส ไม่ทำให้อ่อนลง — ค่าที่คาด (จำนวนหุ้น · ทุน · เสี่ยง · บล็อก · ไม้เติม) ตรวจเท่าเดิม โดย **seed ค่าเดิมใน fixture** (`coreRisk:{riskPct:1, tierA:10, tierB:5}`) ตามบรีฟ
สำรองต้นฉบับไว้ที่ `_bk_cz1/` (core_size_test.js · phase23 · 24 · 25 · 26 · 28 · 37 · 38 · 39 · 43 · 47) · สำรอง `core-size.backup-pre-CZ1.js` + `index.backup-pre-CZ1.html`

| ชุด | เคส | เดิม | ใหม่ | เหตุผล |
|---|---|---|---|---|
| core_size_test.js | ชนเพดาน Tier A/B (3 เคส) | เรียก `firstLot` โดยไม่ส่ง `tierCapPct` (พึ่ง DEFAULTS 10%/5%) | ส่ง `tierCapPct: 0.10` / `0.05` ตรง (ความคาดหวัง 700 / 350 / 700 เท่าเดิม) | DEFAULTS.tierCap เปลี่ยนเป็น A15/B10 |
| core_size_test.js | เคสใหม่ | — | +22 เคส (420 → 442): firstLot เพดานรวม/DEFAULTS · addLot stock_capped / stock_full / ไม่ส่ง stockCapPct = เท่าเดิม | บรีฟ §1 |
| phase23 | core_size_test ผ่านเบราว์เซอร์ | `420/420` | `442/442` | +22 เคส |
| phase23 | ตั้งค่า: ค่าเริ่มต้นครบ | `risk 1 · A 10 · B 5` | `ra 1.25 · rb 1.25 · A 15 · B 10 · cap รวม 25/25` | ค่าเริ่มต้นใหม่ + ตาราง |
| phase23 | ทุกช่องมีป้ายหน่วย | `#crSec .f` = 23 | = 21 | ตาราง Tier 1 กล่อง แทน 3 ช่อง |
| phase23 | แก้งบเสี่ยง → บันทึก | `#sCrRisk` · `coreRisk` 23 คีย์ | `#sCrRiskA` · 27 คีย์ (+riskA +riskB +capTotalA +capTotalB) · `riskPct` = Risk A | ช่องใหม่ |
| phase23 | `coreSizeOpts.tierCap` | `{A:.10,B:.05}` | `{A:.15,B:.10}` | ค่าเริ่มต้นใหม่ |
| phase23 | ค่าผิด (2 เคส) | `sCrRisk = 0 / -1` | `sCrRiskA = 0 / -1` | ช่องใหม่ |
| phase23 | core-size.js ต่างจากต้นฉบับ | 13 hunk | 25 hunk | CZ1 +12 hunk |
| phase24 · 25 · 26 · 28 · 37 · 38 · 39 · 43 | fixture บัญชี Core | ไม่ตั้ง coreRisk (พึ่งค่าเริ่มต้นเก่า 1/10/5) | `coreRisk` seed `riskPct:1 · tierA:10 · tierB:5` (p37: `riskPct:1.25` เดิม + `tierA:10 · tierB:5`) | ค่าที่คาดทั้งหมดเท่าเดิม |
| phase25 | 14 core_size_test + hunk | `420/420` · 13 hunk | `442/442` · 25 hunk | ตามข้างบน |
| phase26 | 0 core-size.js ต่างจาก backup · core_size_test | 13 hunk · ห้ามเปลี่ยน `firstLot`/`addLot` · `420/420` | 25 hunk · อนุญาต firstLot/addLot (CZ1 ตามบรีฟ) · ยังห้าม `ffCoreCap` · `442/442` | บรีฟให้แก้ firstLot/addLot |
| phase47 | ไม่แตะ core-size.js (sha) | sha ของ `core-size.js` | sha ของ `core-size.backup-pre-CZ1.js` (= สถานะก่อน CZ1 ซึ่ง ID3a ไม่แตะ) | CZ1 แก้ไฟล์ตามบรีฟ |

## ที่ไม่ต้องแก้
- phase1–22 · 27 · 29–36 · 40–46 · 48–63 · 64 ผ่านโดยไม่ต้องแก้ (ไม่พึ่งค่าเริ่มต้นขนาดไม้)

## ไม่เกี่ยวกับ CZ1
- phase13 ล้มมาตั้งแต่ก่อน GL1 (ต้องใช้ `index.backup-pre-UI1.html` ที่ไม่มีอยู่) — จำนวนเคส 34 เท่าเดิม
