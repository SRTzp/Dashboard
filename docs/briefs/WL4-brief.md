# WL4 — ปุ่ม 📊 รายได้แยกส่วน · เลิกอ่าน research ทั้งหมด · เทส 52

> ต่อจาก ST1 · ผู้ใช้ตกลง 6 ต.ค. ให้ทำทั้ง 2 เรื่องในรอบเดียว · ไม่แตะ pusher ฝั่ง Python · ข้อมูล `research` / `meta/push` ใน Firestore **ไม่ลบ** แค่แอปเลิกอ่าน
> สำรองก่อนแก้: `index.backup-pre-WL4.html` · `tests/_bk_wl4/` · ห้ามแตะ core-size.js · ห้ามย้อนงานรอบก่อน

## 1. ปุ่ม `📊 รายได้แยกส่วน` (spec Ideas ข้อ 6 · ลิงก์ตรวจแล้ว 6 ต.ค.)
- อยู่ในหัวการ์ดหุ้น (Watchlist และ Candidates) ถัดจากปุ่มเดิม · ปุ่มรอง (ไม่ใช่ primary) · มือถือไม่ล้น
- เปิดแท็บใหม่ (`target="_blank" rel="noopener"`):
  - หุ้น US: `https://www.tradingview.com/symbols/{SYM}/financials-revenue/` (ไม่ต้องรู้ตลาด — TradingView redirect ไป `NASDAQ-NVDA/financials-segments/` เอง · ตรวจกับ NVDA แล้ว)
  - หุ้น TH: `https://www.tradingview.com/symbols/SET-{SYM ไม่มี .BK}/financials-revenue/` (ตรวจกับ PTT แล้ว)
  - ตลาดดูจาก market ของรายการ (`r.market` / `wlGuessMarket`) · SYM ตัวใหญ่ · encodeURIComponent
- title: `ดูรายได้แยกส่วนบน TradingView — ใช้ดูคร่าว ๆ · ตัวเลขที่ใช้เป็นหลักฐานต้องมาจากเอกสารบริษัท`
- ไม่ใช้ token · ไม่ดึงข้อมูลเข้าแอป

## 2. เลิกอ่าน collection `research` และ `meta/push`
- `rsLoad`: ไม่อ่าน `research` และ `meta/push` อีก (ลบการอ่าน หรือทำให้เป็น no-op) · ทุกจุดที่เรียก `rsLoad()` (switchTab watch / flow / today) ต้องไม่ error
- `wlRowsAll` / `wlDocMap`: แถว Watchlist ไม่ join research (`r.d` = null เสมอ) · ทุกจุดที่อ่าน `r.d` ต้องรับ null ได้ (เช่น ชื่อบริษัท fallback · Overview)
- `wlSortRows`: ลำดับ = ความด่วนจาก Thesis (เดิม) → ชื่อ (ตัดการเรียงด้วยคะแนน Screen ออก)
- ชิป `Screen x/15` / `Screen —` (`wlScoreChips`) ออกทั้งหมด (ตอนนี้เหลือแค่ใน Candidates และขึ้น `Screen —` เพราะ Candidates มาจาก Ideas แล้ว)
- แถบสถานะ Watchlist: ข้อความ `โหลดรีเสิร์ชไม่สำเร็จ` / `กำลังโหลดรีเสิร์ช…` ออก
- เมนู ⋯: ป้าย `push ล่าสุด` (`#pushBadge` / `rsUpdatePushBadge`) ออก
- ข้อมูลตัวอย่าง `RS_DEMO` / `RS_DEMO_ON`: ถ้าไม่มีใครใช้แล้ว เอาออกได้ (รายงานว่าเอาออกหรือไม่)
- ห้ามกระทบ: Ideas · Candidates (มาจาก Ideas) · Thesis · การบ้าน Today · Fundflow (มาจากไฟล์ GitHub ไม่ใช่ research)

## เทส `tests/run_tests_phase52.py` (Chromium · 1440 + 390 · mock Firestore)
1. 📊: AVGO (US) → href `https://www.tradingview.com/symbols/AVGO/financials-revenue/` · PTT.BK (TH) → `…/symbols/SET-PTT/financials-revenue/` · target _blank · มีทั้งการ์ด Watchlist และ Candidates · 390px ไม่ล้น
2. seed `research` + `meta/push` ใน mock → เปิด Watch / Flow / Today: mock ไม่ถูกอ่าน 2 collection นี้ (นับการเรียก) · ไม่มีชิป Screen · ไม่มี `#pushBadge` · ไม่มีข้อความโหลดรีเสิร์ช
3. ลำดับ Watchlist: 2 ตัวความด่วนเท่ากัน → เรียงตามชื่อ (ไม่สนคะแนนใน research)
4. ไม่มี console error ทุกแท็บ
5. [static] ไม่มี `collection('research')` และ `doc('push')` ใน index.html
- ภาพ `tests/screenshots/wl4-*` (1440 + 390): `card-revenue-btn` · `menu-no-push`

### เทสเก่า
- เคสที่คาดชิป Screen · `#pushBadge` · ข้อความโหลดรีเสิร์ช · การเรียงตามคะแนน (เช่น p8 · p19 · p32 · p33 · p35 · p38 · p39 · p40) → แก้ความคาดหวังเป็น "ไม่มี" / เรียงตามชื่อ · seed research ในเทสเก่าเก็บไว้ได้ (ต้องไม่มีผล) · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/WL4_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล)
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–52

## รายงานกลับ
จำนวนเคสก่อน → หลังทุกชุด · รายชื่อเทสเก่าที่แก้ · ฟังก์ชันที่ลบ/แก้ · RS_DEMO เอาออกหรือไม่ · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
