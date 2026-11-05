# FX — แก้เล็ก 3 เรื่อง (วันที่เวลาไทย · สี P&L · เตือน Fund-flow เก่า) · เทส 28

> รอบเล็ก ไม่มีฟีเจอร์ใหม่ · ส่งได้ทุกเมื่อหลังรอบก่อนหน้าตรวจผ่าน (ไม่ต้องรอ 7E-2b/7E-4 — แตะคนละจุด)
> สำรองก่อนแก้: `index.backup-pre-FX.html` · **ห้ามแตะ** core-size.js · Calc.coreSize · สูตร Calc.ffCoreCap · หน้าตาการ์ด Core/Sat
> เลขบรรทัดอ้างจากไฟล์หลัง 7E-2a — ใช้ grep ตามข้อความเป็นหลัก

## A. วันที่ = เวลาไทยเสมอ (บั๊กจริง)
ปัญหา: `new Date().toISOString().slice(0,10)` = วันที่ **UTC** → ช่วง 00:00–06:59 เวลาไทย ได้วันที่ "เมื่อวาน" (ไม้/วันปิด/วันยกเลิกบันทึกผิดวัน) · `jDateShort` ตัด 10 ตัวแรกของ ISO ที่มีเวลา (เช่น `cancelled_at` = `…T20:00:00Z`) → แสดงวันผิดเหมือนกัน
1. helper เดียว: `thaiToday()` = `posThaiToday()` เดิม (Asia/Bangkok · 'YYYY-MM-DD') — ให้ `posThaiToday` เรียกตัวนี้หรือเป็นชื่อเดียวกันก็ได้ · `todayISO()` → คืน `thaiToday()`
2. แทน "วันนี้" แบบ UTC ด้วย `thaiToday()` (grep `toISOString().slice(0,10)` ทั้งไฟล์):
   - makeTradeObject date (open/closed) · cancelDate (3 จุด) · `tOpenDate` · `cpExitDate` ค่าเริ่มต้น + fallback ตอนปิด · sat7d date/openedAt · satV3SaveSlot date · `ffTouch` updatedIso · `rrgToday` · validator `tomorrow` · research card `today`
   - **ไม่แตะ** จุดที่เป็นเลขคณิตวันที่แบบ UTC ล้วน (`coreLastFriday` · `rrgWeekKey` · validator ตรวจรูปแบบ `new Date(v).toISOString().slice(0,10)!==v`) — ถูกอยู่แล้ว
   - รายงานเป็นตาราง: บรรทัด/ฟังก์ชัน · แก้หรือไม่ · เหตุผล
3. `jDateShort(iso)`: มีเวลา (มี `T`) → แปลงเป็นวันที่ Asia/Bangkok ก่อน · วันที่ล้วน `YYYY-MM-DD` → ใช้ตามเดิม (ห้ามเลื่อนวัน) · ปีที่ซ่อน/แสดง เทียบกับปีไทยปัจจุบัน (`thaiToday()`)
4. ข้อมูลเก่าที่บันทึกไปแล้ว ไม่ migrate

## B. สี P&L ใช้ `pnlCls` ทุกจุด
- แทน `x>=0?'pnl-pos':'pnl-neg'` ด้วย `pnlCls(x)`: ตาราง Closed (แถว + กลุ่ม) · การ์ด Closed มือถือ (แถว + กลุ่ม) · ข้อความปิดบางส่วนใน sheet ปิดไม้ (`cpInfo`/msg)
- หน้าต่างแก้ไม้ (`openTradeEdit` · บรรทัด "P&L ≈") ใช้ `style="color:…"` → เปลี่ยนเป็น `class="${pnlCls(pnl)}"`
- ไม่แตะ Flow (`ffEsc(up?…)` สีขึ้น/ลงของ Fund-flow ไม่ใช่ P&L)
- กติกาเดิมของ pnlCls: ปัดแล้ว 0 = ไม่มีสี · >0 เขียว · <0 แดง

## C. เตือน Fund-flow เก่าในที่ที่ใช้ f
ตอนนี้เตือนเฉพาะแท็บ Flow · แผง Core แสดงแค่ตัวเล็ก "Fund-flow เก่า · ไม่ลด"
- หัวบัญชีในแผง Core (`data-c-f`) + sheet แผน Core ใหม่ (ส่วน f):
  - `stale` (อายุ > 5 วันทำการ ตาม Calc เดิม) → ชิปสีเหลือง "⚠ Fund-flow เก่า n วันทำการ · f ไม่ลด (100%)"
  - ไม่มีไฟล์จริง (`ffCoreNow().demo`) → ชิปสีเหลือง "⚠ ยังไม่มีข้อมูล Fund-flow · f 100%"
  - ขาดบาง ratio (`missing`) → สีเหลือง + ชื่อที่ขาด (ข้อความเดิม)
  - สดปกติ → เหมือนเดิม ไม่มีเตือน
- ใช้ `ffCoreNow()` / `coreFNow()` เดิม (เพิ่ม `age` · `demo` ใน coreFNow ได้) · ห้ามเปลี่ยนเกณฑ์ 5 วันหรือค่า f

## D. เทส `tests/run_tests_phase28.py` (Chromium · 1440 + 430)
เวลา: ใช้ Playwright `timezone_id` + ตั้งนาฬิกา (`page.clock` หรือ override `Date`) — ทดสอบทั้งเครื่องตั้ง **UTC** และ **Asia/Bangkok** ต้องได้ผลเดียวกัน
1. นาฬิกา **2026-10-01 02:00 เวลาไทย** (= 2026-09-30T19:00Z): `thaiToday()` = "2026-10-01" · `todayISO()` = "2026-10-01"
2. บันทึกไม้ (ผ่านการ์ด Core ไม้ 1 หรือ satV3SaveSlot) ตอนนั้น → `date` = "2026-10-01" · ยกเลิกไม้ → cancelDate = "2026-10-01" · เปิด sheet ปิดไม้ → ช่องวันออก = "2026-10-01"
3. `jDateShort('2026-09-30T20:00:00Z')` = "1 ต.ค." · `jDateShort('2026-09-30')` = "30 ก.ย." · `jDateShort('2025-12-31')` มีปี "25" · ค่าผิด → "—"
4. นาฬิกา 2026-10-01 12:00 ไทย → ผลเหมือนเดิมทุกข้อ (ไม่ถดถอยช่วงกลางวัน)
5. pnlCls ในตาราง Closed/การ์ดมือถือ: P&L 1 → pnl-pos · −1 → pnl-neg · 0 → ไม่มีคลาส · −0.4 → ไม่มีคลาส (แสดง "0") · กลุ่มรวม 0 → ไม่มีคลาส
6. หน้าต่างแก้ไม้ "P&L ≈": ไม่มี inline style สี · คลาสตาม pnlCls
7. Fund-flow as_of 6 วันทำการก่อน → แผง Core + sheet แผนใหม่ มี "⚠ Fund-flow เก่า 6 วันทำการ" · 5 วัน → ไม่มี · ไม่มีไฟล์ → "⚠ ยังไม่มีข้อมูล Fund-flow" · f ที่ใช้คำนวณเท่าเดิมทุกกรณี (เทียบ coreFNow().f ก่อน/หลัง)
8. 430px ไม่ล้นแนวนอน
- ภาพ `tests/screenshots/fx-*`: core-ff-stale · newplan-ff-stale · closed-pnl (1440 + 430)

## E. เทสเก่า
- ทุกชุดต้องผ่าน · เคสที่เช็กวันที่แบบ UTC หรือสี 0 = เขียว → แก้ + บันทึกใน `tests/FX_retired.md` (ชุด · เคส · เดิม · ใหม่ · เหตุผล) · ห้ามลบเคส
- รันครบ: `check_syntax` · `sync_core_size --check` · run_tests + phase ทั้งหมดที่มี

## F. รายงานกลับ
ตารางจำนวนเคสก่อน→หลัง · ตาราง A2 (จุดที่แก้/ไม่แก้) · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
