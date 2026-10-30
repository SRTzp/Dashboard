# WL2 — เทสเก่าที่แก้ความคาดหวัง (ไม่ลบเคส · ไม่ปล่อยล้ม)

brief: `docs/briefs/WL2-brief.md` · ลบ Research Card ทั้งระบบ + การ์ด Watchlist v2 (Living Thesis `living-thesis@1`)
สำรองไฟล์เทสเดิมไว้ที่ `tests/_bk_wl2/` (ทุกไฟล์) · จำนวนเคสต่อชุด **ก่อน = หลัง** (ไม่มีเคสหายจากการแก้ความคาดหวัง)

รูปแบบ: ชุด · เคส · เดิม → ใหม่ · เหตุผล

## ภาพรวมการแมป (Research Card → Thesis)
| เดิม | ใหม่ |
|---|---|
| `research/{T}.research_card` | `users/{uid}/watchlist/{T}.thesis` (+ `thesis_log` · `thesis_history` · `thesis_hits`) |
| แท็บ `Overview` / `Research` (`wlSub` `ov` / `rs`) | แท็บ `สรุป` `ธุรกิจ` `ทำไมซื้อ` `ติดตาม` `ออกเมื่อ` (`sum` `biz` `why` `trk` `exit`) · `ov`/`rs` = `sum` |
| tripwire `confirmed` / `check` / `watching` | tripwire level `broken` / `review` / `watch` (+ ปุ่ม "ชนแล้ว" = broken) |
| ปุ่ม `เติมจาก Research` (`#tiFillRc` · `coreTiFillRc`) | ปุ่ม `เติมจาก Thesis` (`#tiFillTh` · `coreTiFillTh`) จาก `thesis.tier_inputs` |
| การบ้าน `ยังไม่มี Research Card` / `Research เก่า n วัน` | `ยังไม่มี Thesis` / `ควร update: …` / `Thesis เก่า n วัน` |
| Today `tw-check` ("มีข่าวเข้าเงื่อนไข") | ไม่มีแล้ว → `tw-review` ("ถึงระดับทบทวน") จาก level review |

## phase8 (RC/news · Watchlist)
- **Watchlist: ไม่มีแถบข่าว / แท็บ News** · เดิม: seed `research/AVGO.research_card` · เปิดจาก Candidates · แท็บ `["Overview","Research"]` → ใหม่: seed `watchlist/AVGO.thesis` (fixture `avgo_thesis.json`) · แท็บ `["สรุป","ธุรกิจ","ทำไมซื้อ","ติดตาม","ออกเมื่อ"]` (อ่านจาก `.ltTab`) · เหตุผล: ไม่มี Research Card/แท็บ Research แล้ว · สาระ (ไม่มีแถบข่าว/ตัวนับข่าว/แท็บ News) คงเดิม
- **Tripwire ที่มี news_id** · เดิม: `wlSetSub('rs')` · `.rcWire` · "ยืนยันแล้ว" → ใหม่: `wlSetSub('exit')` · `.ltTwr` · ระดับ `review` · ยังเช็กว่าไม่แสดงชื่อข่าว/ลิงก์ข่าว

## phase32 (RC2 · ปุ่มเติม Tier)
- เคสทั้งชุด (1–9) · เดิม: seed `research/{T}.research_card.metrics` (`[T:roic]` ฯลฯ) · กด `#tiFillRc` "เติมจาก Research" → ใหม่: seed `watchlist/{T}.thesis.tier_inputs` · กด `#tiFillTh` "เติมจาก Thesis" · ค่าที่เติมเท่าเดิมทุกช่อง (24.5 · -0.3 · 92 · 25.3 · 18 · 12 · 10 + ติ๊ก 4 ช่อง) · เหตุผล: brief ข้อ 8
- เคส 1 ข้อความ · เดิม `เติม 11 ช่อง · ข้าม 0 ช่องที่กรอกแล้ว · จาก Research 2026-09-20` → ใหม่ `เติม 11 ช่อง · ข้าม 0 ช่องที่กรอกแล้ว · จาก Thesis 20 ก.ย. (ข้อมูล ณ 20 ก.ย.)` · เหตุผล: รูปข้อความตาม brief ข้อ 8
- เคส 5 TOLD · เดิม: การ์ด RC1 ไม่มีรหัส · netcash = ไม่ใช่ จาก ND (คำนวณ) → ใหม่: thesis มี 4 ช่อง (`roic` `ndEbitda` `fcfConv` + `netCash.v=false` ระบุตรง) · ยัง "เติม 4 ช่อง" · เหตุผล: thesis ให้ `netCash` มาเอง ไม่คำนวณจาก ND
- เคส 6 TNONE · เดิม: ไม่มี research_card → ใหม่: thesis ไม่มี `tier_inputs` ที่มีค่า (และ ZZNOPE ไม่อยู่ Watchlist) · ไม่เห็นปุ่ม
- เคส 8 (`metrics_checks` · แท็บ Research แสดง metric + ชิป `Tier` 7 อัน · ชื่อตัดรหัส `[T:]`) · เดิม → ใหม่: **เปลี่ยนเป็นเช็กว่า "ไม่มีแล้ว"** (ไม่มี `.rcMetric` / `.rcTierTag` / `.rcCard` · ไม่มีแท็บ Research · `wlSetSub('rs')` = แท็บ สรุป · ไม่มีฟังก์ชัน `rcTierMetrics` `rcCardHtml` `rcMerge` `rcTrimJson` · ไม่มี `[T:` บนจอ) · เหตุผล: ไม่มีของเทียบ (brief ข้อ "เทสเก่า")
- เคส 9 430px (ช่อง metric ไม่ล้น) · เดิม `.rcMetric` → ใหม่ `.wlDPanel .wlDBody .ltSum .ltDecide` ไม่ล้นแนวนอน · เหตุผล: ของเทียบบนการ์ดใหม่

## phase33 (WT1 · Tier ที่ Watchlist)
- `seed_research` · เดิม: seed `research/PTT.research_card` (7 รหัส Tier) → ใหม่: seed `research/PTT` (ชื่อ) + `watchlist/PTT.BK.thesis` มี `tier_inputs` 11 ช่อง (ค่าเดิมทุกตัว)
- เคส 10 PTT.BK · เดิม: "เห็นปุ่ม 'เติมจาก Research' (doc PTT)" `#tiFillRc` → ใหม่: "เห็นปุ่ม 'เติมจาก Thesis' (thesis ใน watchlist/PTT.BK)" `#tiFillTh` · เหตุผล: Thesis เก็บที่ doc Watchlist เอง (ไม่ต้องจับคู่ doc PTT ↔ PTT.BK ผ่าน research)

## phase35 (WL1 · Overview)
ชุดนี้ตรวจ Overview ที่ถูกแทนด้วยแท็บ สรุป/ติดตาม/ออกเมื่อ — แมปทุกเคสไปยังพฤติกรรมเทียบเท่า (ข้อ 11–12 SR1/FQC ไม่เปลี่ยน)
- seed · เดิม: `research/{T}.research_card` (catalysts 3 · severe_risks 5 · tripwires check/watching · metrics `[T:chk]`) → ใหม่: `watchlist/{T}.thesis` (catalysts 3 วันเดิม · tripwires level review/watch · `tier_inputs` 3 ช่องเช็ก) · `research/{T}` เหลือแค่ชื่อ/`fqc`/`investment_clearance`
- เคส 1 · เดิม: ชิป `Research 2026-09-28 · 3 วัน` (`[data-wl-reschip]`) · ชิป `Research Card` → ใหม่: `Thesis lite · 28 ก.ย.` (`[data-lt-chip]`) · ไม่มีคำ `Research Card` ทั้งหน้า
- เคส 2 แถบเตือน · เดิม: `⚠ ต้องตรวจ: Tripwire "…" มีข่าวเข้าเงื่อนไข — เปิดแท็บ Research` (check) · กดแล้ว `wlSub==='rs'` · confirmed = แดง `ยืนยันแล้ว` → ใหม่: `🟠 Tripwire ถึงระดับทบทวน: … → ดูแท็บ ออกเมื่อ` (level review) · กดแล้ว `wlSub==='exit'` · broken = แดง `⛔ Tripwire พัง`
- เคส 3 Catalysts · เดิม: 2 รายการ (วันที่ผ่านแล้วซ่อน) เรียง 20 พ.ย. → ~10 ธ.ค. · อยู่ใน Overview → ใหม่: 3 รายการ (วันที่ผ่านแล้ว **แสดง** พร้อมป้าย `ผ่านไปแล้ว` · เรียง 1 ก.ย. → 20 พ.ย. → ~10 ธ.ค.) · อยู่ในแท็บ ติดตาม · เหตุผล: brief ข้อ 6 (catalyst ที่เลยวันแล้ว = ยังไม่ update → ⚠)
- เคส 4 Blockers · เดิม: 3 ข้อจาก `severe_risks` + `+ อีก 2 ข้อในแท็บ Research` → ใหม่: ไม่มีข้อจากการ์ด (0 ข้อ · ไม่มี `+ อีก n ข้อ`) เหลือเฉพาะโน้ตของฉัน · เหตุผล: Thesis ไม่มี severe_risks (brief ข้อ 3 แท็บ ติดตาม = `my_notes.blk`)
- เคส 5 Tripwire · เดิม: 2 แถว 🟡/🟢 `ตอนนี้ …` + threshold ใน title ในหน้า Overview → ใหม่: 2 การ์ดในแท็บ ออกเมื่อ (review ก่อน watch) `ตอนนี้: …` · เหตุผล: tripwire ย้ายไปแท็บ ออกเมื่อ
- เคส 5 ท้ายการ์ด · เดิม `ข้อมูล ณ 2026-09-28` → ใหม่ `ข้อมูล ณ 28 ก.ย.` (รูป d MMM) · เคส 5 ลำดับส่วน · เดิม ชิป→แถบเตือน→ธุรกิจ→Catalysts→Blockers→Tripwire→ท้าย → ใหม่ ชิป→แถบเตือน→กล่องตัดสินใจ→รายการสรุป→ท้าย (แท็บ สรุป)
- เคส 6 โน้ตของฉัน · ย้ายไปแท็บ ติดตาม · จำนวนแถว +1 (งานที่ผ่านแล้ว) และตำแหน่งโน้ตวันที่ 1 พ.ย. = แถวที่ 2 · เคส 6 โน้ต blocker · เดิม 3 ข้อการ์ด + 1 โน้ต (4 ข้อ) → ใหม่ 1 โน้ต
- เคส 7 · เดิม: นำเข้า Research Card ใหม่ด้วย `rcMerge` → โน้ตของฉันไม่หาย · `ข้อมูล ณ 2026-09-30` → ใหม่: Import Thesis ฉบับใหม่ผ่าน sheet 📥 Import (วันที่ 2026-09-30) → โน้ตของฉันยังอยู่ใน doc/จอ · `thesis.date` = 2026-09-30
- เคส 8 NOCARD · เดิม: ชิปเหลือง `รอสร้าง Research Card` → ใหม่: การ์ด `ยังไม่มี Thesis — รัน living-thesis แล้ว 📥 Import` · ยังเพิ่มโน้ตได้
- เคส 9 CAND1 · selector ชิป `.wlOvChips` → `.ltChips` (ชิป Screen เดิมยังอยู่)
- เคส 10 (ช่องเช็ก Tier ในแท็บ Research `FCF 3 ปี ✓ · ปันผล/ซื้อคืน ✓ · OCF ✓` · `yes/no/?` → `✓ ✗ ?`) · เดิม → ใหม่: **ปุ่ม `เติมจาก Thesis`** ติ๊ก FCF 3 ปี / ปันผล / OCF จาก `thesis.tier_inputs` (✓✓✓ แล้ว ✓ ✗ ยังไม่ตอบ) · ค่าใน doc ไม่ถูกแก้ · เหตุผล: ของเทียบของช่องเช็กบนแท็บ Research
- เคส 13 · เปิดแท็บ ติดตามก่อนกด `＋ โน้ต`

## phase38 (TD1 · Today)
- seed · เดิม: `research/{T}.research_card` (AVGO confirmed · NVDA check · MSFT watching + catalysts) → ใหม่: `watchlist/{T}.thesis` (AVGO broken · NVDA review · MSFT watch + catalysts เดิม) · MSFT เข้า Watchlist (catalyst ของ Today อ่านจาก Watchlist)
- เคส 4 แถว AVGO · เดิม `Tripwire ยืนยันแล้ว "…" → ทบทวนการถือ` → ใหม่ `Tripwire พัง "…" → ทบทวนการถือ` (kind `tw-confirmed` เหมือนเดิม)
- เคส 5 ลำดับ 🟡 · เดิม `[…, "bias", "tw-check", "catalyst"]` → ใหม่ `[…, "bias", "tw-review", "catalyst"]` · NVDA · เดิม `Tripwire มีข่าวเข้าเงื่อนไข → ตรวจ` → ใหม่ `Tripwire ถึงระดับทบทวน "…"` · เหตุผล: brief ข้อ 7 (ลบแถว tw-check)
- เคส 7 ลิงก์ · AVGO เดิม `wlSub==='rs'` → `'exit'` · NVDA เดิม (`tw-check` · `'rs'`) → (`tw-review` · `'exit'`) · MSFT งบ เดิม `'ov'` → `'trk'`

## phase39 (TD2 · การบ้านหุ้น)
- `hw_extra` · เดิม: seed `research/{T}.research_card.as_of` → ใหม่: `watchlist/{T}.thesis.date` (วันเดิมทุกตัว)
- เหตุผลการบ้าน · เดิม `ยังไม่มี Research Card` / `Research เก่า 93|60|30 วัน` → ใหม่ `ยังไม่มี Thesis` / `Thesis เก่า 93|60|30 วัน` (ลำดับ NOCARD → OLD → MID เหมือนเดิม)
- เคส 10 กดแถว · เดิม `wlOpen('OLD','ov')` · `sub=='ov'` → ใหม่ `sub=='sum'`

## เทสโครง (ไม่ใช่เคส)
- `tests/mock-firebase.js` · `update()` แทนที่ค่าของ field ทั้งก้อนตาม Firestore จริง (เดิม deep-merge ลงใน map เดิม → map ที่ล้างด้วย `{}` ยังเหลือ key เก่า) · key มีจุดแก้ที่ path · สำรองเดิมที่ `tests/_bk_wl2/mock-firebase.pre-update-semantics.js` · ทุกชุดที่เหลือผ่านเท่าเดิมหลังแก้
- `research-card-test.js` ถูกย้ายไป `_to_delete/research-card/` แล้ว → ไม่อยู่ในรายการรัน (ไม่มีเคสนี้ใน `run_tests*.py`)
- phase22 (เช็กไฟล์ใน `_to_delete/`) ไม่แตะ
