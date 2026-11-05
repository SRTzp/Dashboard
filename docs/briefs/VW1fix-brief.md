# VW1fix — รับลิงก์ TradingView โดเมนภาษา (th. ฯลฯ) + แถบ "วางลิงก์กราฟ" ไม่ตัดบรรทัดบนมือถือ · เทส 59 (เพิ่มเคส)

> ต่อจาก VW1 · ตรวจ 11 ต.ค. · สำรองก่อนแก้: `index.backup-pre-VW1fix.html` · `tests/_bk_vw1fix/` · ห้ามแตะ core-size.js · ห้ามย้อน VW1
> ไฟล์ชั่วคราวที่สร้างเองให้ย้ายไป `_to_delete/` ห้าม rm

## 1. `tvSnapImg` รับโดเมนภาษา (บั๊ก)
- ตอนนี้รับแค่ `tradingview.com` / `www.tradingview.com` · แต่ผู้ใช้ไทยที่ตั้ง TV เป็นภาษาไทยจะได้ลิงก์ `https://th.tradingview.com/x/<id>/` (ตรวจแล้ว 11 ต.ค.: หน้า `th.tradingview.com/x/pSb8OxWO/` มี og:image = `https://s3.tradingview.com/snapshots/p/pSb8OxWO.png` เหมือนกัน) → ตอนนี้ขึ้น "ลิงก์นี้ไม่ใช่ภาพ TradingView"
- แก้ regex ให้รับ subdomain ภาษา 2–3 ตัวอักษรเล็ก หรือ `www` : `^https?://(?:(?:www|[a-z]{2,3})\.)?tradingview\.com/x/<id>/?(?:[?#].*)?$` · ผลลัพธ์ภาพเหมือนเดิม (`s3.tradingview.com/snapshots/<ตัวแรก lower>/<id>.png`)
- ห้ามรับ: `evil-tradingview.com` · `tradingview.com.evil.com` · `abcd.tradingview.com` (4 ตัวขึ้นไป ยกเว้น www)

## 2. แถบว่าง `＋ วางลิงก์กราฟ TradingView` ตัดบรรทัดที่ 390px
- ช่อง Strategy ที่ 390px กว้างแค่ครึ่งจอ → ข้อความตัดเป็น 2 บรรทัด การ์ดสูงขึ้นเกิน 40px ทุกช่อง
- ≤ 480px แสดง `＋ กราฟ TV` (บรรทัดเดียว · สูง 40px คงที่) · จอกว้างคงข้อความเต็ม · `aria-label` เป็นข้อความเต็มทั้งสองแบบ

## เทส — เพิ่มเคสใน `tests/run_tests_phase59.py` (ห้ามแก้/ลดเคสเดิม)
1. `tvSnapImg`: `https://th.tradingview.com/x/pSb8OxWO/` → `…/snapshots/p/pSb8OxWO.png` · `https://jp.tradingview.com/x/Ab12Cd34` → `snapshots/a/…` · `https://evil-tradingview.com/x/abcdef/` · `https://tradingview.com.evil.com/x/abcdef/` · `https://abcd.tradingview.com/x/abcdef/` → `null`
2. Sat: วางลิงก์ `th.` ในช่อง XAU → บันทึกได้ · แสดงภาพ
3. 390px: แถบว่างทุกช่อง สูง ≤ 44px · ข้อความบรรทัดเดียว (`scrollHeight` ≤ 1 บรรทัด) · ข้อความ `＋ กราฟ TV` · 1440 ยังเป็นข้อความเต็ม
- เทสเก่าที่ขัด (เช่น phase14 ที่ตัดข้อความแถบออกก่อนเทียบ) → แก้ให้ตัดได้ทั้ง 2 แบบ · **ห้ามลบเคส ห้ามทำให้อ่อนลง** · จด `tests/VW1fix_retired.md`
- อัปเดต `ไฟล์ที่ห้ามลบ.md` (สำรอง VW1fix + `_bk_vw1fix`)
- รันครบ **ทีละชุด**: `core_size_test` · `check_syntax` · `sync_core_size --check` · `run_tests` + phase 1–59
- ภาพ `tests/screenshots/vw1fix-sat-{1440,390}.png`

## รายงานกลับ
จำนวนเคสก่อน → หลัง · ฟังก์ชันที่แก้ · เทสเก่าที่แก้ · ภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
