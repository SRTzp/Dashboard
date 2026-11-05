# TIER2 — Tier 2 มุมมอง: A-Fortress / A-Growth · เทส 31

> ส่งหลัง RC1 ตรวจผ่าน (แก้ index.html คนละจุดแต่ห้ามทำพร้อมกัน) · สำรอง `index.backup-pre-TIER2.html` + `core-size.backup-pre-TIER2.js`
> ที่มา (ผู้ใช้ 1 ต.ค.): แบ่ง Tier ตามช่วงวัยบริษัทของ Damodaran (Corporate Life Cycle) เป็น 2 มุม · ผ่านมุมไหนก็ได้ A · ผ่านทั้งคู่ = A ทั้งสองมุม
> เลขบรรทัดอ้างจากไฟล์หลัง SU — ใช้ชื่อฟังก์ชันเป็นหลัก

## ข้อตัดสิน (ผู้ใช้ยืนยัน 1 ต.ค.)
| เรื่อง | กติกา |
|---|---|
| **A-Fortress** (Mature / ป้อมปราการ) | ROIC > 12% · ND/EBITDA < 2 · FCF conversion > 80% · **FCF เป็นบวก 3 ปีติดกัน** · **มีปันผลหรือซื้อหุ้นคืน** · Gate 5 "ไม่" ทั้ง 3 ข้อ |
| **A-Growth** (High Growth) | รายได้โต ≥ 20% (TTM เทียบปีก่อน) · รายได้โตเฉลี่ย 3 ปี (CAGR) ≥ 15% · Op margin > 0 **และ** ไม่ต่ำกว่าปีก่อน · เงินสดจากการดำเนินงาน (OCF) > 0 · ND/EBITDA < 3 **หรือ** เงินสดสุทธิ (หนี้ − เงินสด ≤ 0) · Gate 5 "ไม่" ทั้ง 3 ข้อ |
| Tier | ผ่านอย่างน้อย 1 มุม = **A** · ไม่ผ่านทั้งคู่ = **B** · ขาดข้อมูลข้อไหน = ข้อนั้นไม่ผ่าน |
| เพดานไม้แรก | A ทุกมุม = `tierA` เดิม (10%) · B = `tierB` (5%) — ไม่แยกตามมุม |
| บันได L | **เฉพาะ A ที่มีมุม Fortress** · A-Growth อย่างเดียว = วางบันไดใหม่ไม่ได้ ("L ใช้ได้เฉพาะ A-Fortress") · บันไดเดิมที่มุมเปลี่ยนภายหลัง = ทำงานต่อจนออก (กติกาเดียวกับ Tier ถูกลด) |
| ยกขึ้นเกินผลคำนวณ | เลือกมุม A ที่คำนวณไม่ผ่าน = ต้องพิมพ์เหตุผล (เหมือนเดิม) · ลดลงไม่ต้องมีเหตุผล |
| เกณฑ์ | เป็นค่าเริ่มต้น ปรับได้ในค่าตั้ง |

## 1. core-size.js (แก้แล้ว `python3 tools/sync_core_size.py`)
- `DEFAULTS.tier` **คงคีย์เดิม** (`roicMin 0.12` · `ndEbitdaMax 2` · `fcfConvMin 0.8`) = เกณฑ์ Fortress · เพิ่ม `growth: {revGrowthMin 0.20, revCagr3Min 0.15, ndEbitdaMax 3}`
- `classifyTier(o)` รับอินพุตใหม่ (ไม่ส่ง = ไม่มีข้อมูล): `fcfPositive3y` (bool) · `capitalReturn` (bool) · `revGrowth` · `revCagr3` · `opMargin` · `opMarginPrev` · `ocf` · `netDebt` (ใช้เช็กเงินสดสุทธิ) · override `{tier, lens:'fortress'|'growth'|'both', reason}` · ค่าเกณฑ์ส่งทับได้ (`roicMin` เดิม + `growth:{…}`)
- คืนค่าเดิมทั้งหมด (`tier · computed · passed · failedNumbers · gate5Yes · gate5Unanswered · overridden · reason`) — **ความหมายเดิม = ฝั่ง Fortress ตัวเลข 3 ข้อ** (เทสเก่าต้องผ่านเหมือนเดิม) + เพิ่ม:
  - `lenses: {fortress:{pass, failed:[…]}, growth:{pass, failed:[…]}}` (failed ใช้รหัส: roic · nd · fcf · fcf3y · capret · gate5 · rev · cagr · opm · opm_trend · ocf · nd_g)
  - `lens`: 'fortress' | 'growth' | 'both' | null (ตามผลจริงหลัง override)
  - `computed` = 'A' เมื่อผ่านอย่างน้อย 1 มุม
- ⚠ `computed` เดิมคิดแค่ตัวเลข 3 ข้อ + Gate 5 → ตอนนี้ Fortress ต้องมี `fcfPositive3y` + `capitalReturn` ด้วย → เคสเก่าที่คาด A จากตัวเลข 3 ข้อ + Gate 5 อย่างเดียว ให้**เพิ่มสองช่องนี้เป็น true ในอินพุตของเคส** (ไม่เปลี่ยนความคาดหวัง) และจดใน `tests/TIER2_retired.md`
- `canPlaceLadder(o)`: รับ `o.fortress` (ไม่ส่ง = true เพื่อไม่ทำโค้ดเดิมพัง) · false → เหตุผล `NOT_FORTRESS`
- `ladder()` ไม่แตะ (ยังเช็กแค่ tier A)

## 2. ข้อมูลการ์ด (`coreCards`)
- เพิ่ม `tierLens: 'fortress'|'growth'|'both'|null` · `tierInputs` เพิ่มฟิลด์ใหม่ข้อ 1 · `tier` ยังเป็น 'A'|'B' เหมือนเดิม (เพดาน/ป้าย Watchlist/โค้ดเดิมไม่ต้องแก้)
- **การ์ดเก่า** tier A ที่ไม่มี `tierLens` → ถือว่า `fortress` (เกณฑ์ Tier A เดิม = Fortress) · แสดง "Tier A · Fortress (เดิม)" จนกว่าจะเปิด Tier… แล้วบันทึกใหม่ · ไม่ migrate ข้อมูล

## 3. UI
### บล็อก Tier (`coreTierBlockHtml` · ใช้ทั้งฟอร์มแผนใหม่และ `coreTierOpen`)
- แบ่ง 2 ส่วนหัว: **Fortress** (ROIC % · ND/EBITDA · FCF conversion % · ☐ FCF บวก 3 ปีติด · ☐ มีปันผล/ซื้อหุ้นคืน) และ **Growth** (รายได้โต TTM % · CAGR 3 ปี % · Op margin ปีนี้ % · ปีก่อน % · OCF บวก ☐) · ND/EBITDA ใช้ช่องเดียวร่วมกัน + ☐ เงินสดสุทธิ · Gate 5 สามข้อ (ใช้ร่วม) ไว้ล่างสุด
- ช่องติ๊กเป็น 3 สถานะ (ใช่ / ไม่ใช่ / ยังไม่ตอบ) แบบเดียวกับ Gate 5 — ยังไม่ตอบ = ไม่ผ่าน
- ผลสด 2 บรรทัด: "Fortress: ✓ ผ่าน" / "Fortress: ✗ ROIC ≤ 12% · ไม่มีข้อมูลปันผล" · "Growth: …" + บรรทัดรวม "คำนวณได้ A · Fortress" / "A · ทั้งสองมุม" / "B"
- ปุ่มเลือก Tier ที่ใช้จริง: [B] [A · Fortress] [A · Growth] [A · ทั้งคู่] · เริ่ม = ผลคำนวณ · เลือกมุมที่ไม่ผ่าน = ช่องเหตุผลบังคับ
- จอ ≤ 700px: สองส่วนเรียงบน-ล่าง · ปุ่ม 4 ตัวขึ้น 2 แถวได้ · ไม่ล้นแนวนอน

### ป้ายบนการ์ด Core
- ชิปในตัวการ์ด: "Tier A · Fortress · เพดาน 10%" / "Tier A · Growth · …" / "Tier A · Fortress + Growth · …" / "Tier B · …" · แถวยุบ (`A·W` / `A·L`) คงเดิม แต่ `title` บอกมุม
- ป้ายเทียบ Watchlist (`tierBadge`) คงเดิม — Watchlist ยังเก็บ A/B (ไม่แยกมุมในรอบนี้)

### บันได L
- ปุ่มสลับกลยุทธ์ในฟอร์มแผนใหม่ + เมนู ⋯ "เปลี่ยนเป็น L" : เปิดเฉพาะ `tierLens` มี fortress · ไม่งั้นปิด + "L ใช้ได้เฉพาะ A-Fortress" (แทนข้อความ "L ใช้ได้เฉพาะ Tier A" ทุกจุด ~5362 · ~5830 · grep ให้ครบ)
- `coreCanPlace` ส่ง `fortress` · รายการประตูข้อ Tier: "A-Fortress" ✓ / "ต้องเป็น A-Fortress · ตอนนี้ A-Growth" ✗
- "แก้แผนบันได" ของแผนเดิมที่มุมไม่ใช่ Fortress = ปิด (เหมือนกรณี Tier B เดิม)

### ค่าตั้ง (ส่วนความเสี่ยง Core ต่อบัญชี · ที่เดียวกับ `tierA`/`tierB`)
- เพิ่มหัวข้อ "เกณฑ์ Tier": Fortress ROIC % · ND/EBITDA · FCF conversion % · Growth รายได้โต % · CAGR 3 ปี % · ND/EBITDA · ค่าเริ่มต้นตามตาราง · ส่งเข้า `classifyTier` ผ่าน `coreSizeOpts`
- `CORE_RISK_DEFAULTS` เพิ่มคีย์ใหม่ · ค่าเก่าที่บันทึกไว้ไม่มีคีย์ = ใช้ค่าเริ่มต้น

## 4. ไม่ทำรอบนี้
- Research Card ดึงตัวเลข Growth (→ RC2) · ตอนนี้ผู้ใช้กรอกเองในบล็อก Tier
- Watchlist แยกมุม Tier · หน้า Overview ใหม่ (→ WL1)

## 5. เทส
**`tests/core_size_test.js` (เพิ่ม · เคสเก่าต้องผ่าน)**
1. Fortress ผ่าน: ROIC 15% · ND 1.5 · FCF 90% · fcf3y ✓ · capret ✓ · Gate 5 ไม่×3 → `lens 'fortress'` · tier A
2. เหมือนข้อ 1 แต่ capret ไม่มีข้อมูล → fortress ไม่ผ่าน (`capret`) · growth ไม่มีข้อมูล → B
3. Growth ผ่าน: rev 25% · CAGR 18% · opm 12% vs ก่อน 10% · OCF ✓ · ND 2.5 · Gate 5 ไม่×3 → `lens 'growth'`
4. rev 19.9% → growth ไม่ผ่าน (`rev`) · opm 9% vs 10% → ไม่ผ่าน (`opm_trend`) · opm −1% → ไม่ผ่าน (`opm`) · ND 3.5 → ไม่ผ่าน (`nd_g`) · ND 3.5 แต่ netDebt −100 (เงินสดสุทธิ) → ผ่าน
5. ผ่านทั้งข้อ 1 + 3 → `lens 'both'`
6. Gate 5 ใช่ 1 ข้อ + ตัวเลขผ่านทั้งสองมุม → B ทั้งคู่ (`gate5`)
7. override `{tier:'A', lens:'growth', reason:''}` ตอนคำนวณได้ B → REASON_REQUIRED · มีเหตุผล → tier A · lens growth · overridden
8. `canPlaceLadder` `fortress:false` → `NOT_FORTRESS` · ไม่ส่ง → เหมือนเดิม
9. เกณฑ์ส่งทับ: `growth.revGrowthMin 0.15` → rev 19.9% ผ่าน

**`tests/run_tests_phase31.py` (Chromium · 1440 + 430)**
10. ฟอร์มแผนใหม่: กรอกชุดข้อ 1 → "คำนวณได้ A · Fortress" · ปุ่ม L เปิด · กรอกชุดข้อ 3 → "A · Growth" · ปุ่ม L ปิด + "L ใช้ได้เฉพาะ A-Fortress" · ทั้งคู่ → "A · ทั้งสองมุม" + L เปิด
11. บันทึกแผน A-Growth → การ์ดเก็บ `tier:'A'` · `tierLens:'growth'` · ชิป "Tier A · Growth" · ไม้แรกเพดาน 10% (ตัวเลขเท่า A เดิม)
12. เมนู ⋯ การ์ด A-Growth "เปลี่ยนเป็น L" ปิด · การ์ด A-Fortress เปิด
13. การ์ดเก่า tier A ไม่มี `tierLens` → ชิป "Tier A · Fortress (เดิม)" · วางบันได L ได้ · Tier… เปิดแล้วปิดไม่บันทึก = ไม่มีอะไรเปลี่ยน
14. บันได L เดิมของการ์ดที่เปลี่ยนเป็น A-Growth → ซื้อระดับต่อ/เลื่อน Stop ได้ · "แก้แผนบันได" ปิด
15. ค่าตั้ง: เปลี่ยน Growth รายได้โต 20 → 15 แล้วกลับฟอร์ม → rev 19.9% กลายเป็นผ่าน
16. 430px: บล็อก Tier ไม่ล้นแนวนอน · ปุ่ม Tier 4 ตัวกดได้ (≥ 36px) · `elementFromPoint` ของช่องติ๊ก = ตัวมันเอง
- ภาพ `tests/screenshots/tier2-*`: block-fortress · block-growth · block-both · card-chip · L-disabled · settings (1440 + 430)

**เทสเก่า:** เคสที่ขัด (ข้อความ "L ใช้ได้เฉพาะ Tier A" · เคส classifyTier ที่ต้องเติม fcf3y/capret) → **แก้ความคาดหวัง/อินพุตของเคส ห้ามลบ ห้ามปล่อยล้ม** + จดใน `tests/TIER2_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)

## 6. รัน / รายงานกลับ
check_syntax · sync_core_size --check · `node tests/core_size_test.js` · ชุดเต็มทั้งหมด · รายงาน: จำนวนเคสก่อน → หลัง · diff ของ `classifyTier`/`canPlaceLadder` · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
