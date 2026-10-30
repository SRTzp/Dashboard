# PF2 — เคสเก่าที่เปลี่ยน/ถอด

| suite | เคส | การเปลี่ยน | เหตุผล |
|---|---|---|---|
| phase93 | 4 เสาร์/ทีหลัง/เริ่มสัปดาห์/ติ๊ก BTC ออก/ข้อมูลเก่าหลัง nwStart (8 เคส) | ถอด (RETIRED(PF2)) → เช็ก "ไม่มี [data-nw-box]" แทน | ลบ prompt สัปดาห์ใหม่ (A2) · phase99 ตรวจต่อ |
| phase93 | แถวลิงก์ล่าง = คัดลอก + เอาออก | = เอาออกเท่านั้น (กล่องมีข้อความ) | ลิงก์ "นำเข้าความเห็นสัปดาห์ก่อน" โผล่เฉพาะกล่องว่าง |
| phase93 | เปิดครั้งแรกสัปดาห์ใหม่ (อังคาร) กล่องโผล่ | → ไม่มีกล่อง | A2 |
| phase93 | อาทิตย์สัปดาห์ใหม่ XAU | เพิ่ม waPick('XAUUSD') ก่อน | สัปดาห์ใหม่เริ่มว่าง ไม่เลือก Asset ให้ |
| phase95 | 3 สัปดาห์ใหม่: nwStart ล้าง opinion_txt เอกสารหน้า | ถอด | nwStart ถอด · phase96 คุม satWeekFreshWrite |
| phase95 | Flow: ชิป/headline | วัดตอนพับ · headline อยู่ใต้แถวหัวและเหนือชิป · มือถือไม่ตัด … · แคบ 300px | PF2 A3 + flowchips mockup |
| phase96 | nwStart ใช้ตัวช่วยเดียวกับ ＋ Asset | เหลือ ＋ Asset | nwStart ถอด |
| phase96 | 'คัดลอกจากสัปดาห์ก่อน' ยังมีให้กด | ลิงก์ใหม่ไม่โผล่เมื่อกล่องมีข้อความ | A2 |
| phase98 | 10 nwRows hint | ถอด → typeof nwRows/nwStart = undefined | A2 |
| phase9 | พับ สูง ≤ 48px | ≤ 140px (หัว → headline → ชิป) · กางแล้วตรวจท่าทีจาก pbMain() ไม่ใช่ .pbIcos | PF2 A3 |
| phase11 | ไอคอน Flow พับ 'XAU ▲ · BR ▼ …' | ไม่มีตัวคั่น ' · ' (ชิปห่อบรรทัด) | PF2 |
| phase94 | ก้นสองคอลัมน์ ≤ 15% | ≤ 22% · มือถือ thesis 16px | การ์ด Macro พับสูงขึ้น · A3 |
| phase69 | Today งาน sat-pick (เลือก Asset) | การ์ด Sat state A "Start by adding a Strategic Asset" + ปุ่ม Add (เปิด sheet) | A4 |
| phase72, phase56 | งาน sat-pick / ชิป ✓/✕ | ยอมรับการ์ด state A | A4 |
| phase38, phase39 | Today เงียบเมื่อ pick ครบ/Focus ครบ | seed แผนใช้งานให้ pick (tests/pf2_retire.py seed_plans · เฉพาะรันตรง) = state C | Asset ที่เลือกแต่ไม่มีแผน = state B (การ์ดอยู่จนมีแผน) ตามสเปก |
