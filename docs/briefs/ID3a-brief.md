# ID3a — 📋 จับคู่ list จาก TradingView + ＋ ไอเดีย (ร่าง) · เทส 47

> ต่อจาก ID2 + NUM2 · อ้างอิง `docs/specs/ideas-spec.md` ข้อ 3 (＋ ไอเดีย) · 8b (จับคู่ list) · 8d (กลุ่มที่วิ่งแต่ยังไม่มีไอเดีย) · skill `idea-scout` โหมด `match` (มี JSON `idea-match@1` แล้ว)
> สำรองก่อนแก้: `index.backup-pre-ID3a.html` · `tests/_bk_id3a/` · ห้ามแตะ core-size.js · ห้ามย้อนงาน NUM1 / PX1 / ID1 / ID2 / NUM2
> ไม่ทำรอบนี้: 📝 ตอบข้อที่ขาด / ปิด "หาไม่ได้" (= ID3b) · แท็บ Today (ID4) · ไม่เรียก AI จากแอป · list ที่วางไม่เก็บถาวร (เก็บแค่ผลที่ Import)
> ผู้ใช้ตัดสิน 5 ต.ค.: กลุ่มยังไม่มีไอเดีย = **≥ 3 ตัว** · ไม่สนใจ = **ซ่อน 30 วัน** (ปรับได้)

## ตัวอย่าง CSV จริง (TradingView screener · `tests/fixtures/tv_volume_spike_2026-10-05.csv` · 9 แถว)
- หัวตารางมี 17 คอลัมน์ เช่น `Symbol,Description,Price,Price - Currency,"Price change %, 1 day",…,Sector,Analyst rating,Industry` → **หาคอลัมน์จากชื่อหัว** (ไม่ใช้ตำแหน่ง) · ชื่อหัวและค่ามีจุลภาคในเครื่องหมายคำพูด (`"Teradyne, Inc."`) → ต้องใช้ตัวอ่าน CSV ที่รองรับ `"…"` + `""` จริง (เขียนเองสั้น ๆ ได้ ห้ามใช้ `split(',')`)
- `Symbol` ไม่มีตลาดนำหน้า (`TER`) แต่บาง export เป็น `NASDAQ:TER` → ตัดส่วนก่อน `:` ทิ้ง
- ตลาด: `Price - Currency` USD → US · THB → TH · ไม่มีคอลัมน์ → `wlGuessMarket`
- ชื่อ Industry ของ TradingView เป็นตัวพิมพ์แบบประโยค (`Electronic production equipment`) แต่ skill เขียน `industries[]` แบบ Title Case (`Electronic Production Equipment`) → **เทียบแบบไม่สนตัวพิมพ์ + ตัดช่องว่างหัวท้าย**

## 1. ＋ ไอเดีย (ร่าง · ไม่เรียก AI)
- หัวรายการ Ideas: ปุ่ม `＋ ไอเดีย` (ซ้ายของ 📥 Import) → sheet 5 ช่อง: ชื่อ* · ไอเดียประโยคเดียว* · ตลาด (US/TH) · โน้ตของฉัน · หุ้นที่นึกไว้ (คั่นด้วยจุลภาค/เว้นวรรค)
- บันทึก → doc ใหม่ `users/{uid}/ideas/{id}` · `id` = slug จากชื่อ (a-z0-9-) + `-YYYYMMDD` (ชื่อไทยล้วน → `idea-YYYYMMDD`) · ชนกับที่มี → ต่อท้าย `-2`, `-3`
- `idea` = `{schema:"idea@1", id, name, date: thaiToday(), mode:"draft", scope:[ตลาด], status:"draft", user_notes:{idea, mechanism:โน้ตของฉัน, tickers:[…], unsure:""}, origin:[]}` · **สถานะร่างเก็บใน `idea.status` ไม่ใช่ `user.status`** (Import ผล scan ทีหลังต้องได้สถานะตาม JSON ใหม่ — ถ้าเก็บใน user จะค้างเป็นร่างตลอด) · `idea_log` = 1 บรรทัด `สร้างร่างในแอป`
- การ์ดร่าง: แสดงเฉพาะ ไอเดีย · โน้ต · หุ้นที่นึกไว้ · ที่มา + ข้อความ `ร่าง — ยังไม่ได้รัน idea-scout` + ปุ่ม `คัดลอกคำสั่ง scan` (และใน ⋯) · แท็บอื่นที่ว่างต้องไม่ error (แสดง "ยังไม่มี — รัน scan ก่อน")
- คำสั่ง scan (คัดลอก · ช่องว่าง = ตัดบรรทัดทิ้ง):
```
idea-scout scan
ไอเดีย: {user_notes.idea}
ชื่อ: {name} · id: {id} (ใช้ id เดิม — Import แล้วแทนที่ร่างนี้)
ตลาด: {scope}
โน้ตของฉัน: {user_notes.mechanism}
หุ้นที่นึกไว้: {tickers คั่นด้วย ,}
ที่มา: {origin[].title}
```
- Import ผล scan (id เดียวกัน) → แทนที่ `idea` ตาม ID1 เดิม · สถานะตาม JSON

## 2. 📋 จับคู่ list (หน้า Candidates)
- หัวรายการ Candidates: ปุ่ม `📋 จับคู่ list` → sheet: ช่องวาง + เลือกไฟล์ `.csv` · ≤ 500 แถว · ≤ 300KB (เกิน = error ไม่ประมวลผล)
- 2 แบบ: มีหัวตารางที่มี `Symbol` = โหมด CSV · ไม่มี = ticker ล้วน (คั่นด้วยบรรทัด/จุลภาค/เว้นวรรค · ไม่มี Industry)
- **ชั้น 1 (ในแอป · 0 token)** เทียบกับไอเดียสถานะ รอหลักฐาน / พร้อมส่งต่อ เท่านั้น (ใช้ `ideaCounted` ของ ID2) · ต่อหุ้น:
  - (ก) ticker อยู่ใน `candidates[]` / `losers[]` ของไอเดียแล้ว → `อยู่ในไอเดียแล้ว` + ชื่อไอเดีย + ▲/▼
  - (ข) ไม่ใช่ (ก) แต่ Industry ตรง `chain.segments[].industries[]` → `Industry ตรง` + ชื่อไอเดีย + จำนวนส่วนที่ตรง + ทิศตาม `effect` (win ▲ · lose ▼ · mixed ▲▼) · **ไม่กำหนดส่วนให้** (ให้ match เป็นคนเลือก)
  - (ค) ที่เหลือ → `ไม่ตรง`
  - ทุกแถว: ชิป `อยู่ใน Watchlist` ถ้ามีแล้ว
- แสดงผล 3 กลุ่ม (นับจำนวนบนหัวกลุ่ม · กลุ่ม ไม่ตรง พับไว้) · แถวบรรทัดเดียว `SYM · Description (ตัด …) · Industry · ผล` · มือถือไม่ล้นแนวนอน
- **กลุ่มยังไม่มีไอเดีย (ข้อ 8d)** — เฉพาะโหมด CSV: นับกลุ่ม (ค) ตาม Industry · กลุ่มที่ ≥ `ideaGroupMin` (ค่าเริ่ม 3) → บรรทัดเดียวเหนือผล `กลุ่มยังไม่มีไอเดีย: Semiconductors (4) ＋ ✕ · …` (สูงสุด 3 กลุ่ม เรียงมาก → น้อย)
  - `＋` → สร้างไอเดียร่างทันที (ข้อ 1) ชื่อ `{Industry} วิ่ง — เพราะอะไร?` · `user_notes.idea` = `หุ้นกลุ่ม {Industry} ขึ้นพร้อมกันใน screen {วันที่}` · `tickers` = หุ้นกลุ่มนั้น · `origin` = `[{title:"TradingView screen {วันที่}"}]` · ตลาดจากหุ้นกลุ่มนั้น · แล้วเปิดการ์ดร่าง
  - `✕` (ไม่สนใจ) → ซ่อน Industry นั้น `ideaGroupHideDays` วัน (ค่าเริ่ม 30) · เก็บ localStorage (try/catch) แยกตามชื่อ Industry ตัวเล็ก
  - ค่า `ideaGroupMin` / `ideaGroupHideDays` เก็บใน settings ระดับผู้ใช้ที่เดียวกับ routine (`tdSettings()` / settings ของ `acctList[0]`) · แก้ได้ในหน้าตั้งค่า (เลขจำนวนเต็ม 2–10 / 1–90)
- **คัดลอกคำสั่ง match** · ค่าเริ่ม = ส่งเฉพาะกลุ่ม (ข) · ติ๊ก `ส่งตัวที่ถูกตัดด้วย` = เพิ่มกลุ่ม (ค) · กลุ่ม (ก) ไม่ส่ง · ไม่มีอะไรจะส่ง = ปุ่มกดไม่ได้ + เหตุผล
```
idea-scout match
วันที่: {thaiToday} · ที่มา: {ชื่อไฟล์ หรือ "TradingView screen"}
หุ้น (Symbol · Description · Industry · ตลาด):
TER · Teradyne, Inc. · Electronic production equipment · US
…
สรุปไอเดียสำหรับจับคู่:
[{id}] {name} — {one_liner รวมเป็นประโยคเดียว}
 ได้: {ชื่อส่วน} ({industries}) ; …
 เสีย: …
 ปนกัน: …
```
  (ต่อไอเดียไม่เกิน ~200 tokens: ตัด one_liner ที่ 300 ตัวอักษร · ไม่ใส่ส่วนอื่นของไอเดีย)

## 3. 📥 Import ผลจับคู่ (`idea-match@1`)
- ปุ่มใน sheet 📋 (ขั้นสุดท้าย) · ช่องวาง/ไฟล์ · ตัด ```json / ข้อความหน้า-หลังแบบเดียวกับ Import อื่น · ≤ 200KB
- Import ไอเดีย (ID1) ที่เจอ `idea-match@1` → เปลี่ยนข้อความ error เป็น `ไฟล์นี้เป็นผลจับคู่ — Import ที่ Candidates › 📋 จับคู่ list` (ยังไม่บันทึก)
- ตรวจ: `schema` · `results[]` · แต่ละแถว `sym` ไม่ว่าง · `side` win/lose · `fit` likely/unsure · `idea` ต้องเป็นไอเดียที่มีและนับ (รอหลักฐาน/พร้อมส่งต่อ) · `segments[]` เก็บเฉพาะชื่อที่มีในไอเดียนั้น (ชื่อที่ไม่มี → ตัด + แจ้งในตัวอย่าง)
- ตัวอย่างก่อนบันทึก (ต่อไอเดีย): `+n รอตรวจ ▲` · `+m รอตรวจ ▼` · ข้าม: อยู่ในไอเดียแล้ว / ไอเดียไม่พบ / ไอเดียไม่ได้อยู่สถานะที่นับ · `dropped` จากไฟล์
- บันทึก (ต่อไอเดีย · แทนที่ field `idea` ทั้งก้อน · **ไม่แตะ `user`**):
  - win → ต่อท้าย `idea.candidates[]`: `{sym, market, name: Description จาก list ที่วางอยู่ (ถ้ามี) หรือ "", from:"match", segments, why_this: why, fit, state:"screen", relevance_src:"", rank:null}`
  - lose → ต่อท้าย `idea.losers[]`: `{sym, market, why, src:"", state:"screen"}`
  - ticker ที่มีอยู่แล้วในไอเดียนั้น (ฝั่งเดียวกัน) → ข้าม ไม่ทับ
  - `idea_log` ต่อท้าย 1 บรรทัด `{date} match: +n ▲ +m ▼ รอตรวจ ({source})`
- ผลที่เห็น: Candidates `▲?` (ID2 มีแล้ว) · Value chain ticker เหลือง `?` · **ID2 ต้องรองรับ loser `state:"screen"`:** ป้าย `▼?` · กล่องแดง "หุ้นของเราฝั่งเสีย" นับด้วยแต่มี `?` · `คัดลอก Handoff (update)` กดไม่ได้ + `รอตรวจ — รัน pick ก่อน`
- Export JSON ของไอเดียต้องมีบริษัท/losers จาก match (ไว้แปะให้ `pick` ต่อ)

## เทส `tests/run_tests_phase47.py` (Chromium · 1440 + 390 · mock Firestore · นาฬิกาปลอม 2026-10-05 ไทย)
fixture: `tests/fixtures/tv_volume_spike_2026-10-05.csv` (ไฟล์จริงจากผู้ใช้ · ห้ามแก้) + `idea_semis.json` (สถานะ need_evidence)
1. ＋ ไอเดีย: บันทึก → doc มี `idea.status:"draft"` · `user.status` ว่าง · id ตามกติกา · ชื่อซ้ำ → `-2` · การ์ดร่างไม่ error ทุกแท็บ · คำสั่ง scan ตรงรูปแบบ (ช่องว่างถูกตัด) · Import JSON id เดียวกันสถานะ exploring → แสดง กำลังสำรวจ (ไม่ค้างร่าง)
2. วาง CSV จริง → อ่านได้ 9 แถว (ชื่อมีจุลภาคถูกต้อง) · ผลชั้น 1: TER · VECO = Industry ตรง ▲ (อุปกรณ์ผลิตชิป · ไม่สนตัวพิมพ์) · LSCC · QRVO · SYNA · PENG = Industry ตรง (4 ส่วน ▲) · CAMT = Industry ตรง ▼ (Electronic components อยู่ส่วนฝั่งเสีย) · NTAP · IBRX = ไม่ตรง
3. ใส่ KLAC ใน candidates ของไอเดีย + วาง `KLAC,TER` แบบ ticker ล้วน → KLAC = อยู่ในไอเดียแล้ว · TER = ไม่ตรง (ไม่มี Industry) · `NASDAQ:TER` → อ่านเป็น TER
4. กลุ่มยังไม่มีไอเดีย: ไอเดีย semis ตั้งพัก → วาง CSV → `Semiconductors (4)` ขึ้น · `Electronic production equipment (2)` ไม่ขึ้น (< 3) · ตั้ง min = 2 → ขึ้นทั้งคู่ · `✕` → หาย · เลื่อนนาฬิกา +31 วัน → กลับมา · `＋` → ไอเดียร่างชื่อ/โน้ต/tickers/origin ตามกติกา
5. คำสั่ง match: ค่าเริ่มมีเฉพาะ 7 ตัวกลุ่ม (ข) · ติ๊กส่งตัวถูกตัด → 9 ตัว · มีสรุปไอเดีย 1 ไอเดีย · ไม่มีส่วน "หลักฐาน/บริษัท" ของไอเดียปน
6. Import `idea-match@1` (fixture ในเทส: TER win · VECO win · CAMT win ส่วน "อุปกรณ์ผลิตชิป" · QRVO lose · แถว idea ไม่มีอยู่ 1 · segments ชื่อผิด 1): ตัวอย่างนับถูก · บันทึก → candidates +3 state screen · losers +1 state screen · log +1 · `user` เดิมไม่เปลี่ยน · Import ซ้ำ → ไม่เพิ่มซ้ำ
7. หลัง Import: Candidates มี TER/VECO/CAMT `▲?` · → Watchlist กดไม่ได้ (รอตรวจ) · QRVO ใน Watchlist (seed) → ป้าย `▼?` · Handoff (update) กดไม่ได้ + เหตุผล · Export มีบริษัทจาก match
8. Import ไอเดีย (ID1) ใส่ไฟล์ idea-match@1 → ข้อความใหม่ ไม่บันทึก
9. CSV > 500 แถว / > 300KB / ไม่มีแถวข้อมูล → error ไม่ประมวลผล · ไม่มี console error ทุกเคส · 390px ไม่ล้นแนวนอน
- ภาพ `tests/screenshots/id3a-*` (1440 + 390): `match-layer1` · `group-line` · `match-import` · `draft-card`

### เทสเก่า
- p44 เคส 8 (ข้อความ error ของ idea-match@1 ใน Import ไอเดีย) → แก้ความคาดหวังเป็นข้อความใหม่ · **ห้ามลบ ห้ามทำให้อ่อนลง** · จด `tests/ID3a_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–47

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · ฟังก์ชันใหม่/ที่แก้ · ตัวอย่างคำสั่ง scan + match จาก fixture · ผลชั้น 1 ของ CSV จริง (ตาราง 9 แถว) · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
