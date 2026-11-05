# RC1 — คำสั่ง Research Card: ตัวเลขซ้อนชั้น · ตัวเลข Tier · ภาระนอกงบ · วันงบถัดไป

> รอบเล็ก (หลัง v1) · แก้**ข้อความคำสั่ง (prompt) อย่างเดียว** · schema `research-card/1.0` เดิม ห้ามเปลี่ยน (ฟิลด์ · จำนวนสูงสุด · validate · merge ไม่แตะ)
> ที่มา: ผู้ใช้ตรวจการ์ด AVGO (1 ต.ค.) — อ่านตัวเลขซ้อนชั้นผิด (รายได้ชิป AI 16.7B อยู่ในรายได้เซมิฯ 20.8B) · ไม่มี ROIC/ND-EBITDA/FCF conversion ให้ตั้ง Tier · พลาด purchase commitments $126.8B + financing backstop ~$29B จาก 10-Q · เหตุการณ์ถัดไปว่าง
> สำรองก่อนแก้: `research-card.backup-pre-RC1.js` + `index.backup-pre-RC1.html`

## แก้
1. `research-card.js` ฟังก์ชัน `promptText` — **เพิ่ม 4 ประโยคนี้ (ภาษาอังกฤษตามต้นฉบับ)** ต่อจากประโยค "Mark thin evidence unconfirmed; do not invent numbers or fill slots." ห้ามแก้หรือลบประโยคเดิม

```
Metric hierarchy: when a metric is a part of another listed metric (for example AI revenue within semiconductor revenue, upfront license revenue within software revenue), name the parent in the Thai metric name, e.g. "รายได้ชิป AI (ส่วนหนึ่งของรายได้เซมิคอนดักเตอร์)"; when two shares are measured on overlapping bases (for example top-5 end customers vs one distributor), say in the name that they overlap and must not be added together.
Quality metrics for Tier: always include ROIC, ND/EBITDA and FCF conversion computed from the latest 10-K or annual report plus later 10-Q/interim reports (use TTM when available, otherwise the latest fiscal year). Definitions: ROIC = NOPAT ÷ (total debt + total equity − cash and equivalents), NOPAT = operating income × (1 − effective tax rate); ND/EBITDA = (total debt − cash and equivalents) ÷ EBITDA; FCF conversion = FCF ÷ net income. Put the short formula in the metric name, state TTM or the fiscal year in period, write value as a string such as "24.5" with unit "%" or "x", and use the filing as source_url. If net income or EBITDA is zero or negative, or an input is missing, put the item in missing_data instead of estimating. Keep metrics within the 12-item limit by dropping the least useful existing metrics first.
Off-balance-sheet obligations: read the commitments and contingencies notes of the latest 10-Q/10-K (or interim report). If purchase commitments, guarantees, financing backstops or similar obligations exceed 10% of annual revenue or materially affect a driver, add each to additional_drivers with amount, timing and source URL, and add it to severe_risks when it could force losses if demand weakens.
Next earnings: always include the next earnings report in catalysts. If the date is not announced, estimate it from the company's usual reporting pattern, set date_status "estimated", and cite the prior-period results release as source_url.
```

2. `python3 inline-research-card.py` → index.html ได้ sha ใหม่ในคอมเมนต์ `/* source: research-card.js · sha256 … */`
3. ถ้า `~/Documents/Projects/Research-team/shared/research-card-v1.md` มีข้อความคำสั่งชุดเดียวกัน (หรือกติกาที่ขัดกับ 4 ข้อข้างบน) → แก้ให้ตรงกัน และรายงานว่าแก้ไฟล์ไหนบ้าง · ถ้าไม่มี = ไม่ต้องแตะ · **ห้ามแก้ `research_card.py` / validator ฝั่ง Python** (schema ไม่เปลี่ยน)

## เทส
- `research-card-test.js` เพิ่มเคส: เรียก `rcCopy` ด้วย clipboard จำลอง (หรือเปิด `promptText` ผ่าน `window` เฉพาะในเทสก็ได้) → ข้อความต้องมีครบ: `Metric hierarchy` · `ROIC = NOPAT` · `ND/EBITDA = (total debt − cash` · `FCF conversion = FCF ÷ net income` · `commitments and contingencies` · `Next earnings` · และยังมีประโยคเดิม `Return exactly these 15 top-level fields` · การ์ดเดิม (มี prior) และการ์ดใหม่ (prior null) ได้ประโยคใหม่ทั้งคู่
- เคส validate เดิมทั้งหมดต้องผ่านเหมือนเดิม (schema ไม่เปลี่ยน)
- รัน: `node research-card-test.js` · `check_syntax` · `sync_core_size --check` · phase 8 (Research Card) · ชุดเต็มทั้งหมด
- ภาพ: ไม่ต้อง (หน้าตาไม่เปลี่ยน)

## รายงานกลับ
diff ของ `promptText` · sha ใหม่ใน index.html · ผลเทส (จำนวนเคสก่อน → หลัง) · ไฟล์นอก Dashboard ที่แก้ (ถ้ามี) · ไม่ push ไม่ลบไฟล์

## หลังขึ้นเว็บ (ผู้ใช้)
หุ้นที่จะใช้ตั้ง Tier (เริ่ม AVGO) → Watch → Research → "อัปเดต Research · คัดลอกคำสั่ง" → รันใน AI ที่ค้นเว็บได้ → นำเข้า → ตรวจว่า 3 ตัวเลข Tier ลิงก์ไป sec.gov/หน้า IR บริษัท
