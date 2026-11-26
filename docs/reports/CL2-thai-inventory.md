# CL2 · Thai text the user sees — inventory

Crawl: seeded data (the E2E1 crawl seed + the HW1 Watch fixture), 1440 and 390; every tab / segment / Today Daily + Weekend / Plan (Planned · Ordered · Holding · Momentum · Compounder · Future) / Flow / Watch (Ideas · Momentum · Compounder · Screen · detail · Homework for 4 stocks · Add stocks) / Journal / Port / Settings (Portfolio · System · Industries) / drawers, every sheet and menu reachable by one click (delete / import / export / external skipped), plus the static sheets that only open from a data state (edit trade, close position, cancel plan, goal sheets, Fund-flow sheets, reason/score managers, weekly-backup banner) forced open once. Script: `python3 tests/cl2_inventory.py [--write]`.

## Count

| | rows (screen × text) | distinct texts |
|---|---|---|
| **Before** (origin/main, after HW2) | **685** | **123** |
| **After** this branch | **25** (all user-typed data) | **5** (all user-typed data) |

The 5 left after are not UI text: the Fund-flow note `· flip 2 ต.ค.` is a date the user typed into the fixture (user-entered data stays as typed).

Not reachable by this crawl and **not changed** (legacy / data-dependent code that is not rendered with the seed): the one-time reset gate (CL2-a), the Restore-from-backup preview, Weekly Impact / Playbook paste sheets, the Today task rows built by `tdBuild`, the old Journal backfill form. Per the brief, hidden legacy code that is never rendered is left; the permanent crawl assertion will catch any of it the day it shows up on a crawled screen.

## Before — every visible Thai item (screen · kind · text · source line in origin/main)

| Screen | Kind | Text | Source line (before) |
|---|---|---|---|
| Flow | text | (ไม่ใช่วันเริ่มทำจริง — ตลาด price in ตั้งแต่ประกาศ) | 27863 |
| Flow | text | Is the market rewarding risk-takers? · flip 2 ต.ค. | 9326 |
| Flow | option | QT — ดูดสภาพคล่องออก | 27860 |
| Flow | text | Real economy vs fear · flip 2 ต.ค. | 9326 |
| Flow | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Flow | text | Weekly Impact · เวลา ICT (UTC+7) | 23818 |
| Flow | text | World equities beat cash — the divisor cannot fall · flip 2 ต.ค. | 9326 |
| Flow | text | credit risk appetite — the one that leads equities · flip 2 ต.ค. | 9326 |
| Flow | text | · flip 2 ต.ค. | 9326 |
| Flow | title | ขึ้นบนสุด | 10739 |
| Flow | text | คำนวณจาก | 12076 |
| Flow | text | คำนวณอัตโนมัติจากราคาจริง ไม่ต้องตั้งเอง · ติดตาม 23 ตัวเทียบ SPY — XLU · PAVE · XHB · XLB · XLC · XBI · JETS · IGV · XRT · HACK · XLF · KRE · XLE · XLV · ITA · SMH · ARKX · ROBO · XLK · XLI · XLY · XLP · XLRE | 25223 |
| Flow | aria-label | ค้นหา Asset | 23819 |
| Flow | placeholder | ค้นหา Asset… | 23819 |
| Flow | text | ชั้น 1 — บอร์ดจดเอง: Is money entering capital markets? (weekly) | 27827 |
| Flow | text | ชั้น 2 — บอร์ดจดเอง: Is money entering speculative stocks? (daily) | 27827 |
| Flow | text | ตั้งค่า Fund-flow — proxy & น้ำหนัก | 27877 |
| Flow | placeholder | ตีความ — UP แปลว่าอะไร | 27817 |
| Flow | text | ที่โหลดจาก | 9479 |
| Flow | text | นอก Macro | 22592 |
| Flow | text | น้ำหนักแก้ได้เฉพาะที่นี่ เพื่อกันการปรับตอนกำลังอ่านผล · เกณฑ์ Risk-on/off ล็อกไว้ตายตัว | 27878 |
| Flow | aria-label | บัญชีหลัก | 2056 |
| Flow | title | บัญชีหลัก · . previous · / next | dynamic |
| Flow | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Flow | text | บันทึก | 2163 |
| Flow | title | ปฏิทินข่าว US | 27738 |
| Flow | text | ประกาศ | 9667 |
| Flow | text | ประวัติการแก้บอร์ด | 27835 |
| Flow | text | ปิด | dynamic |
| Flow | text | ยกเลิก | 2727 |
| Flow | text | ยังไม่มี | 9325 |
| Flow | text | ลบ | dynamic |
| Flow | text | วันที่ | 6427 |
| Flow | aria-label | วันนี้ | 274 |
| Flow | text | สภาพคล่องกลาง (QE / QT) | 27855 |
| Flow | placeholder | เช่น ชะลอความเร็ว QT | 27865 |
| Flow | text | เท่านั้น · บอร์ดจดเองชั้น 1–2 ด้านบนไม่เปลี่ยนเพดาน | 27830 |
| Flow | text | เปลี่ยนโหมดแล้วระบบจะเก็บของเดิมเป็นประวัติให้อัตโนมัติ · แถบนี้เป็นบริบท ไม่คิดคะแนน | 27866 |
| Flow | text | เพดานลงเงินจริง | 27829 |
| Flow | title | เพิ่มเติม | 121 |
| Flow | text | เลือก | 2159 |
| Flow | text | เสร็จ | 10179 |
| Flow | text | แก้บ่อย = กำลังจูนเข้าหาความอยาก ไม่ใช่ปรับปรุงระบบ | 27836 |
| Flow | text | แผนที่ธีม (Relative Trend vs SPY) | 27831 |
| Flow | text | โน้ต | 1324 |
| Flow | text | โหมด | 121 |
| Flow | text | ใช้บันทึกมุมมองเท่านั้น · ไม่ได้คุมเพดาน | 27827 |
| Flow | title | ไปหน้าแผน (T) | 6157 |
| Flow | text | ＋ Asset สัปดาห์นี้ | 10791 |
| Flow | text | ＋ เพิ่ม proxy | 27824 |
| Flow | text | ＋ เพิ่มสินค้าใหม่ | 23821 |
| Journal | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Journal | aria-label | บัญชีหลัก | 2056 |
| Journal | title | บัญชีหลัก · . previous · / next | dynamic |
| Journal | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Journal | aria-label | วันนี้ | 274 |
| Journal | title | เพิ่มเติม | 121 |
| Journal | title | ไปหน้าแผน (T) | 6157 |
| Manage drawer | aria-label | Equity บัญชี 3 | dynamic |
| Manage drawer | text | Is the market rewarding risk-takers? · flip 2 ต.ค. | 9326 |
| Manage drawer | text | Qty ที่จะปิด (สูงสุด | 6504 |
| Manage drawer | text | Real economy vs fear · flip 2 ต.ค. | 9326 |
| Manage drawer | text | Snapshot due · บัญชี 3 | dynamic |
| Manage drawer | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Manage drawer | text | World equities beat cash — the divisor cannot fall · flip 2 ต.ค. | 9326 |
| Manage drawer | text | credit risk appetite — the one that leads equities · flip 2 ต.ค. | 9326 |
| Manage drawer | text | · Entry 2,643 · Qty คงเหลือ | 476 |
| Manage drawer | text | · flip 2 ต.ค. | 9326 |
| Manage drawer | title | ขึ้นบนสุด | 10739 |
| Manage drawer | text | ทั้งหมด | 700 |
| Manage drawer | text | บ | dynamic |
| Manage drawer | text | บัญชี 3 | dynamic |
| Manage drawer | title | บัญชี 3 · . previous · / next | dynamic |
| Manage drawer | text | บัญชี 3 · ฿830,000 | dynamic |
| Manage drawer | aria-label | บัญชี 3, 1 waiting | dynamic |
| Manage drawer | aria-label | บัญชีหลัก | 2056 |
| Manage drawer | title | บัญชีหลัก · . previous · / next | dynamic |
| Manage drawer | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Manage drawer | title | ปฏิทินข่าว US | 27738 |
| Manage drawer | text | ปิด | dynamic |
| Manage drawer | text | ปิด Position — เลือกจำนวน | 6498 |
| Manage drawer | text | ยกเลิก | 2727 |
| Manage drawer | text | ยืนยันปิด | 6516 |
| Manage drawer | aria-label | วันนี้ | 274 |
| Manage drawer | text | สรุปสัปดาห์นี้ยังไม่พร้อม | 27613 |
| Manage drawer | title | เพิ่มเติม | 121 |
| Manage drawer | title | ไปหน้าแผน (T) | 6157 |
| Manage drawer | text | ⚠ กรอก Exit Price | 21865 |
| More menu | text | Snapshot due · บัญชี 3 | dynamic |
| More menu | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| More menu | text | บ | dynamic |
| More menu | text | บัญชี 3 | dynamic |
| More menu | title | บัญชี 3 · . previous · / next | dynamic |
| More menu | aria-label | บัญชี 3, 1 waiting | dynamic |
| More menu | title | บัญชีหลัก · . previous · / next | dynamic |
| More menu | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| More menu | aria-label | วันนี้ | 274 |
| More menu | title | เพิ่มเติม | 121 |
| More menu | title | ไปหน้าแผน (T) | 6157 |
| Plan drawer | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan drawer | text | บ | dynamic |
| Plan drawer | text | บัญชี 3 | dynamic |
| Plan drawer | title | บัญชี 3 · . previous · / next | dynamic |
| Plan drawer | aria-label | บัญชี 3, 1 waiting | dynamic |
| Plan drawer | aria-label | บัญชีหลัก | 2056 |
| Plan drawer | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan drawer | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan drawer | aria-label | วันนี้ | 274 |
| Plan drawer | title | เพิ่มเติม | 121 |
| Plan drawer | title | ไปหน้าแผน (T) | 6157 |
| Plan · Future | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan · Future | text | บ | dynamic |
| Plan · Future | text | บัญชี 3 | dynamic |
| Plan · Future | title | บัญชี 3 · . previous · / next | dynamic |
| Plan · Future | aria-label | บัญชี 3, 1 waiting | dynamic |
| Plan · Future | aria-label | บัญชีหลัก | 2056 |
| Plan · Future | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan · Future | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan · Future | aria-label | วันนี้ | 274 |
| Plan · Future | title | เพิ่มเติม | 121 |
| Plan · Future | title | ไปหน้าแผน (T) | 6157 |
| Plan · Holding | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan · Holding | aria-label | บัญชีหลัก | 2056 |
| Plan · Holding | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan · Holding | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan · Holding | aria-label | วันนี้ | 274 |
| Plan · Holding | title | เพิ่มเติม | 121 |
| Plan · Holding | title | ไปหน้าแผน (T) | 6157 |
| Plan · Ordered | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan · Ordered | aria-label | บัญชีหลัก | 2056 |
| Plan · Ordered | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan · Ordered | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan · Ordered | aria-label | วันนี้ | 274 |
| Plan · Ordered | title | เพิ่มเติม | 121 |
| Plan · Ordered | title | ไปหน้าแผน (T) | 6157 |
| Plan · Planned | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan · Planned | aria-label | บัญชีหลัก | 2056 |
| Plan · Planned | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan · Planned | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan · Planned | aria-label | วันนี้ | 274 |
| Plan · Planned | title | เพิ่มเติม | 121 |
| Plan · Planned | title | ไปหน้าแผน (T) | 6157 |
| Plan · Stocks (Compounder) | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan · Stocks (Compounder) | text | บ | dynamic |
| Plan · Stocks (Compounder) | text | บัญชี 3 | dynamic |
| Plan · Stocks (Compounder) | title | บัญชี 3 · . previous · / next | dynamic |
| Plan · Stocks (Compounder) | aria-label | บัญชี 3, 1 waiting | dynamic |
| Plan · Stocks (Compounder) | aria-label | บัญชีหลัก | 2056 |
| Plan · Stocks (Compounder) | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan · Stocks (Compounder) | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan · Stocks (Compounder) | aria-label | วันนี้ | 274 |
| Plan · Stocks (Compounder) | title | เพิ่มเติม | 121 |
| Plan · Stocks (Compounder) | title | ไปหน้าแผน (T) | 6157 |
| Plan · Stocks (Momentum) · Planned | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Plan · Stocks (Momentum) · Planned | text | บ | dynamic |
| Plan · Stocks (Momentum) · Planned | text | บัญชี 3 | dynamic |
| Plan · Stocks (Momentum) · Planned | title | บัญชี 3 · . previous · / next | dynamic |
| Plan · Stocks (Momentum) · Planned | aria-label | บัญชี 3, 1 waiting | dynamic |
| Plan · Stocks (Momentum) · Planned | aria-label | บัญชีหลัก | 2056 |
| Plan · Stocks (Momentum) · Planned | title | บัญชีหลัก · . previous · / next | dynamic |
| Plan · Stocks (Momentum) · Planned | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Plan · Stocks (Momentum) · Planned | aria-label | วันนี้ | 274 |
| Plan · Stocks (Momentum) · Planned | title | เพิ่มเติม | 121 |
| Plan · Stocks (Momentum) · Planned | title | ไปหน้าแผน (T) | 6157 |
| Port | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Port | aria-label | บัญชีหลัก | 2056 |
| Port | title | บัญชีหลัก · . previous · / next | dynamic |
| Port | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Port | aria-label | วันนี้ | 274 |
| Port | title | เพิ่มเติม | 121 |
| Port | title | ไปหน้าแผน (T) | 6157 |
| Settings · Industries | aria-label | Equity บัญชี 3 | dynamic |
| Settings · Industries | text | Is the market rewarding risk-takers? · flip 2 ต.ค. | 9326 |
| Settings · Industries | text | Real economy vs fear · flip 2 ต.ค. | 9326 |
| Settings · Industries | text | Snapshot due · บัญชี 3 | dynamic |
| Settings · Industries | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Settings · Industries | text | World equities beat cash — the divisor cannot fall · flip 2 ต.ค. | 9326 |
| Settings · Industries | text | credit risk appetite — the one that leads equities · flip 2 ต.ค. | 9326 |
| Settings · Industries | text | · flip 2 ต.ค. | 9326 |
| Settings · Industries | alert | กรอกชื่อ Industry | 21382 |
| Settings · Industries | title | ขึ้นบนสุด | 10739 |
| Settings · Industries | text | จัดการ Industry | 6731 |
| Settings · Industries | placeholder | ชื่อ Industry ใหม่ เช่น Semiconductor | 6735 |
| Settings · Industries | text | บ | dynamic |
| Settings · Industries | text | บัญชี 3 | dynamic |
| Settings · Industries | title | บัญชี 3 · . previous · / next | dynamic |
| Settings · Industries | text | บัญชี 3 · ฿830,000 | dynamic |
| Settings · Industries | aria-label | บัญชี 3, 1 waiting | dynamic |
| Settings · Industries | aria-label | บัญชีหลัก | 2056 |
| Settings · Industries | title | บัญชีหลัก · . previous · / next | dynamic |
| Settings · Industries | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Settings · Industries | title | ปฏิทินข่าว US | 27738 |
| Settings · Industries | text | ปิด | dynamic |
| Settings · Industries | text | ยังไม่มี Industry — เพิ่มด้านบนได้เลย | 21377 |
| Settings · Industries | aria-label | วันนี้ | 274 |
| Settings · Industries | text | สรุปสัปดาห์นี้ยังไม่พร้อม | 27613 |
| Settings · Industries | text | เพิ่ม | 25 |
| Settings · Industries | title | เพิ่มเติม | 121 |
| Settings · Industries | text | ใช้เฉพาะ Core Port และ Satellite.A — เพิ่มชื่อ Industry ไว้เป็น selection ตอนเพิ่มหุ้นใน Watchlist | 6732 |
| Settings · Industries | text | ใส่ URL คู่มือของ industry นั้นได้ด้วย แล้วชื่อ industry ในตาราง Watchlist และใน legend ของ pie หน้า Portfolio จะกดเปิดได้ | 6733 |
| Settings · Industries | title | ไปหน้าแผน (T) | 6157 |
| Settings · Portfolio | text | ($) · ล่าสุดก่อน | 14208 |
| Settings · Portfolio | text | Is the market rewarding risk-takers? · flip 2 ต.ค. | 9326 |
| Settings · Portfolio | text | Real economy vs fear · flip 2 ต.ค. | 9326 |
| Settings · Portfolio | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Settings · Portfolio | text | World equities beat cash — the divisor cannot fall · flip 2 ต.ค. | 9326 |
| Settings · Portfolio | text | credit risk appetite — the one that leads equities · flip 2 ต.ค. | 9326 |
| Settings · Portfolio | text | · flip 2 ต.ค. | 9326 |
| Settings · Portfolio | title | ขึ้นบนสุด | 10739 |
| Settings · Portfolio | text | ค่าเริ่ม = ยอดตอนตั้งเป้า (ใส่ย้อนหลังได้) · ไม่ตั้งเป้า = บัญชีนั้นไม่แสดงแถว · ต้องมี เป้า > ค่าเริ่ม > 0 และ วันครบ > วันเริ่ม | 14205 |
| Settings · Portfolio | text | ค่าเริ่มต้น | 6758 |
| Settings · Portfolio | alert | ดึงอัตราแลกเปลี่ยนไม่สำเร็จ ลองใหม่อีกครั้ง หรือกรอกเองได้ | 22152 |
| Settings · Portfolio | text | ทุนรวม ≈ | 481 |
| Settings · Portfolio | text | บัญชี | 178 |
| Settings · Portfolio | aria-label | บัญชีหลัก | 2056 |
| Settings · Portfolio | title | บัญชีหลัก · . previous · / next | dynamic |
| Settings · Portfolio | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Settings · Portfolio | text | บันทึกเป้า | 14206 |
| Settings · Portfolio | title | ปฏิทินข่าว US | 27738 |
| Settings · Portfolio | text | ประวัติค่าพอร์ต บัญชีหลัก | dynamic |
| Settings · Portfolio | text | ปิด | dynamic |
| Settings · Portfolio | text | ยังไม่มีประวัติ | 14209 |
| Settings · Portfolio | text | ยังไม่เคยดึงอัตโนมัติ — ใส่เองด้านบน หรือกด "ดึงเรทล่าสุด" | 22131 |
| Settings · Portfolio | text | ลบ | dynamic |
| Settings · Portfolio | text | วันครบกำหนด | 14202 |
| Settings · Portfolio | aria-label | วันนี้ | 274 |
| Settings · Portfolio | text | วันเริ่ม | 14204 |
| Settings · Portfolio | text | สกุลเงิน | 14200 |
| Settings · Portfolio | text | สรุปสัปดาห์นี้ยังไม่พร้อม | 27613 |
| Settings · Portfolio | text | สลับไป | 9820 |
| Settings · Portfolio | text | สำรองล่าสุดจากเครื่องนี้: 2026-10-02 13:03 น. | 28268 |
| Settings · Portfolio | title | สีประจำบัญชี | 9770 |
| Settings · Portfolio | text | เปิดอยู่ | 9585 |
| Settings · Portfolio | text | เป้า | 372 |
| Settings · Portfolio | title | เพิ่มเติม | 121 |
| Settings · Portfolio | text | แสดงในหน้ารวม | 9771 |
| Settings · Portfolio | title | ไปหน้าแผน (T) | 6157 |
| Settings · Portfolio | text | 🔄 ดึงเรทล่าสุด | 22131 |
| Settings · System | text | ($) · ล่าสุดก่อน | 14208 |
| Settings · System | text | Is the market rewarding risk-takers? · flip 2 ต.ค. | 9326 |
| Settings · System | text | Real economy vs fear · flip 2 ต.ค. | 9326 |
| Settings · System | text | Snapshot due · บัญชี 3 | dynamic |
| Settings · System | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Settings · System | text | World equities beat cash — the divisor cannot fall · flip 2 ต.ค. | 9326 |
| Settings · System | text | credit risk appetite — the one that leads equities · flip 2 ต.ค. | 9326 |
| Settings · System | text | · flip 2 ต.ค. | 9326 |
| Settings · System | title | ขึ้นบนสุด | 10739 |
| Settings · System | text | ค่าเริ่ม = ยอดตอนตั้งเป้า (ใส่ย้อนหลังได้) · ไม่ตั้งเป้า = บัญชีนั้นไม่แสดงแถว · ต้องมี เป้า > ค่าเริ่ม > 0 และ วันครบ > วันเริ่ม | 14205 |
| Settings · System | text | ค่าเริ่มต้น | 6758 |
| Settings · System | text | ค่าเริ่มต้นต้องมากกว่า 0 | 14253 |
| Settings · System | prompt | ชื่อบัญชีใหม่ | 10195 |
| Settings · System | text | บ | dynamic |
| Settings · System | text | บัญชี | 178 |
| Settings · System | text | บัญชี 3 | dynamic |
| Settings · System | title | บัญชี 3 · . previous · / next | dynamic |
| Settings · System | aria-label | บัญชี 3, 1 waiting | dynamic |
| Settings · System | aria-label | บัญชีหลัก | 2056 |
| Settings · System | title | บัญชีหลัก · . previous · / next | dynamic |
| Settings · System | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Settings · System | text | บันทึกเป้า | 14206 |
| Settings · System | title | ปฏิทินข่าว US | 27738 |
| Settings · System | text | ประวัติค่าพอร์ต บัญชีหลัก | dynamic |
| Settings · System | text | ปิด | dynamic |
| Settings · System | text | ยังไม่มีประวัติ | 14209 |
| Settings · System | text | ลบ | dynamic |
| Settings · System | text | วันครบกำหนด | 14202 |
| Settings · System | aria-label | วันนี้ | 274 |
| Settings · System | text | วันเริ่ม | 14204 |
| Settings · System | text | สกุลเงิน | 14200 |
| Settings · System | text | สรุปสัปดาห์นี้ยังไม่พร้อม | 27613 |
| Settings · System | text | สลับไป | 9820 |
| Settings · System | text | สำรองล่าสุดจากเครื่องนี้: 2026-10-02 13:03 น. | 28268 |
| Settings · System | title | สีประจำบัญชี | 9770 |
| Settings · System | text | เปิดอยู่ | 9585 |
| Settings · System | text | เป้า | 372 |
| Settings · System | title | เพิ่มเติม | 121 |
| Settings · System | text | แสดงในหน้ารวม | 9771 |
| Settings · System | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · cancelOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · cancelOverlay | text | บ | dynamic |
| Sheet (forced open) · cancelOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · cancelOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · cancelOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · cancelOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · cancelOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · cancelOverlay | text | บันทึก Cancel | 6794 |
| Sheet (forced open) · cancelOverlay | text | บันทึกเพิ่ม (ถ้ามี) | 6787 |
| Sheet (forced open) · cancelOverlay | text | ปิด | dynamic |
| Sheet (forced open) · cancelOverlay | text | ยกเลิกแผนเทรด | 6780 |
| Sheet (forced open) · cancelOverlay | text | รูปภาพ Chart (ลิงก์ Google Drive, ถ้ามี) | 6435 |
| Sheet (forced open) · cancelOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · cancelOverlay | placeholder | เช่น รอ breakout แต่แท่งปิดต่ำกว่าแนวรับ setup เสียแล้ว | 6787 |
| Sheet (forced open) · cancelOverlay | title | เพิ่ม/แก้ไขแท็ก | 6482 |
| Sheet (forced open) · cancelOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · cancelOverlay | text | เหตุผลที่ยกเลิก | 6441 |
| Sheet (forced open) · cancelOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · closePosOverlay | text | Qty ที่จะปิด (สูงสุด | 6504 |
| Sheet (forced open) · closePosOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · closePosOverlay | text | · Entry 2,643 · Qty คงเหลือ | 476 |
| Sheet (forced open) · closePosOverlay | text | ทั้งหมด | 700 |
| Sheet (forced open) · closePosOverlay | text | บ | dynamic |
| Sheet (forced open) · closePosOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · closePosOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · closePosOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · closePosOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · closePosOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · closePosOverlay | text | ปิด Position — เลือกจำนวน | 6498 |
| Sheet (forced open) · closePosOverlay | text | ยกเลิก | 2727 |
| Sheet (forced open) · closePosOverlay | text | ยืนยันปิด | 6516 |
| Sheet (forced open) · closePosOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · closePosOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · closePosOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · closePosOverlay | text | ⚠ กรอก Exit Price | 21865 |
| Sheet (forced open) · ffQeOverlay | text | (ไม่ใช่วันเริ่มทำจริง — ตลาด price in ตั้งแต่ประกาศ) | 27863 |
| Sheet (forced open) · ffQeOverlay | option | QT — ดูดสภาพคล่องออก | 27860 |
| Sheet (forced open) · ffQeOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · ffQeOverlay | text | บ | dynamic |
| Sheet (forced open) · ffQeOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · ffQeOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · ffQeOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · ffQeOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · ffQeOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · ffQeOverlay | text | บันทึก | 2163 |
| Sheet (forced open) · ffQeOverlay | text | ประกาศ | 9667 |
| Sheet (forced open) · ffQeOverlay | text | ยกเลิก | 2727 |
| Sheet (forced open) · ffQeOverlay | text | วันที่ | 6427 |
| Sheet (forced open) · ffQeOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · ffQeOverlay | text | สภาพคล่องกลาง (QE / QT) | 27855 |
| Sheet (forced open) · ffQeOverlay | placeholder | เช่น ชะลอความเร็ว QT | 27865 |
| Sheet (forced open) · ffQeOverlay | text | เปลี่ยนโหมดแล้วระบบจะเก็บของเดิมเป็นประวัติให้อัตโนมัติ · แถบนี้เป็นบริบท ไม่คิดคะแนน | 27866 |
| Sheet (forced open) · ffQeOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · ffQeOverlay | text | โน้ต | 1324 |
| Sheet (forced open) · ffQeOverlay | text | โหมด | 121 |
| Sheet (forced open) · ffQeOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · ffSetOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · ffSetOverlay | text | คำนวณจาก | 12076 |
| Sheet (forced open) · ffSetOverlay | text | คำนวณอัตโนมัติจากราคาจริง ไม่ต้องตั้งเอง · ติดตาม 23 ตัวเทียบ SPY — XLU · PAVE · XHB · XLB · XLC · XBI · JETS · IGV · XRT · HACK · XLF · KRE · XLE · XLV · ITA · SMH · ARKX · ROBO · XLK · XLI · XLY · XLP · XLRE | 25223 |
| Sheet (forced open) · ffSetOverlay | text | ชั้น 1 — บอร์ดจดเอง: Is money entering capital markets? (weekly) | 27827 |
| Sheet (forced open) · ffSetOverlay | text | ชั้น 2 — บอร์ดจดเอง: Is money entering speculative stocks? (daily) | 27827 |
| Sheet (forced open) · ffSetOverlay | text | ตั้งค่า Fund-flow — proxy & น้ำหนัก | 27877 |
| Sheet (forced open) · ffSetOverlay | placeholder | ตีความ — UP แปลว่าอะไร | 27817 |
| Sheet (forced open) · ffSetOverlay | text | ที่โหลดจาก | 9479 |
| Sheet (forced open) · ffSetOverlay | text | น้ำหนักแก้ได้เฉพาะที่นี่ เพื่อกันการปรับตอนกำลังอ่านผล · เกณฑ์ Risk-on/off ล็อกไว้ตายตัว | 27878 |
| Sheet (forced open) · ffSetOverlay | text | บ | dynamic |
| Sheet (forced open) · ffSetOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · ffSetOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · ffSetOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · ffSetOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · ffSetOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · ffSetOverlay | text | ประวัติการแก้บอร์ด | 27835 |
| Sheet (forced open) · ffSetOverlay | text | ยังไม่มี | 9325 |
| Sheet (forced open) · ffSetOverlay | text | ลบ | dynamic |
| Sheet (forced open) · ffSetOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · ffSetOverlay | text | เท่านั้น · บอร์ดจดเองชั้น 1–2 ด้านบนไม่เปลี่ยนเพดาน | 27830 |
| Sheet (forced open) · ffSetOverlay | text | เพดานลงเงินจริง | 27829 |
| Sheet (forced open) · ffSetOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · ffSetOverlay | text | เสร็จ | 10179 |
| Sheet (forced open) · ffSetOverlay | text | แก้บ่อย = กำลังจูนเข้าหาความอยาก ไม่ใช่ปรับปรุงระบบ | 27836 |
| Sheet (forced open) · ffSetOverlay | text | แผนที่ธีม (Relative Trend vs SPY) | 27831 |
| Sheet (forced open) · ffSetOverlay | text | ใช้บันทึกมุมมองเท่านั้น · ไม่ได้คุมเพดาน | 27827 |
| Sheet (forced open) · ffSetOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · ffSetOverlay | text | ＋ เพิ่ม proxy | 27824 |
| Sheet (forced open) · glValOverlay | text | (ยอดรวมทุกโบรกของบัญชี) | 6620 |
| Sheet (forced open) · glValOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · glValOverlay | text | กรอกค่าพอร์ต | 6617 |
| Sheet (forced open) · glValOverlay | text | ช่องว่าง = ไม่บันทึกบัญชีนั้น · วันเดียวกันกรอกซ้ำ = แทนที่ · ดู/ลบประวัติได้ใน ตั้งค่าระบบ → เป้าหมาย Port | 6623 |
| Sheet (forced open) · glValOverlay | text | บ | dynamic |
| Sheet (forced open) · glValOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · glValOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · glValOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · glValOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · glValOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · glValOverlay | text | บันทึก | 2163 |
| Sheet (forced open) · glValOverlay | text | ยกเลิก | 2727 |
| Sheet (forced open) · glValOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · glValOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · glValOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · industryOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · industryOverlay | text | จัดการ Industry | 6731 |
| Sheet (forced open) · industryOverlay | placeholder | ชื่อ Industry ใหม่ เช่น Semiconductor | 6735 |
| Sheet (forced open) · industryOverlay | text | บ | dynamic |
| Sheet (forced open) · industryOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · industryOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · industryOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · industryOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · industryOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · industryOverlay | text | ปิด | dynamic |
| Sheet (forced open) · industryOverlay | text | ยังไม่มี Industry — เพิ่มด้านบนได้เลย | 21377 |
| Sheet (forced open) · industryOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · industryOverlay | text | เพิ่ม | 25 |
| Sheet (forced open) · industryOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · industryOverlay | text | ใช้เฉพาะ Core Port และ Satellite.A — เพิ่มชื่อ Industry ไว้เป็น selection ตอนเพิ่มหุ้นใน Watchlist | 6732 |
| Sheet (forced open) · industryOverlay | text | ใส่ URL คู่มือของ industry นั้นได้ด้วย แล้วชื่อ industry ในตาราง Watchlist และใน legend ของ pie หน้า Portfolio จะกดเปิดได้ | 6733 |
| Sheet (forced open) · industryOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · ltOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · ltOverlay | text | บ | dynamic |
| Sheet (forced open) · ltOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · ltOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · ltOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · ltOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · ltOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · ltOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · ltOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · ltOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · reasonMgrOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · reasonMgrOverlay | text | ค่าเริ่มต้น | 6758 |
| Sheet (forced open) · reasonMgrOverlay | text | บ | dynamic |
| Sheet (forced open) · reasonMgrOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · reasonMgrOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · reasonMgrOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · reasonMgrOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · reasonMgrOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · reasonMgrOverlay | text | ปิด | dynamic |
| Sheet (forced open) · reasonMgrOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · reasonMgrOverlay | text | หลุดแผน | 6753 |
| Sheet (forced open) · reasonMgrOverlay | placeholder | เช่น ปรับพอร์ต, ต้องใช้เงิน | 6751 |
| Sheet (forced open) · reasonMgrOverlay | text | เพิ่ม | 25 |
| Sheet (forced open) · reasonMgrOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · reasonMgrOverlay | text | แท็กเหตุผล | 6482 |
| Sheet (forced open) · reasonMgrOverlay | text | แท็กใหม่ | 6751 |
| Sheet (forced open) · reasonMgrOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · scoreMgrOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · scoreMgrOverlay | text | ค่าเริ่มต้น | 6758 |
| Sheet (forced open) · scoreMgrOverlay | text | บ | dynamic |
| Sheet (forced open) · scoreMgrOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · scoreMgrOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · scoreMgrOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · scoreMgrOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · scoreMgrOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · scoreMgrOverlay | text | ปิด | dynamic |
| Sheet (forced open) · scoreMgrOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · scoreMgrOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · scoreMgrOverlay | text | แก้ข้อความคะแนน | 6764 |
| Sheet (forced open) · scoreMgrOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · setOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · setOverlay | text | ทุนรวม ≈ | 481 |
| Sheet (forced open) · setOverlay | text | บ | dynamic |
| Sheet (forced open) · setOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · setOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · setOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · setOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · setOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · setOverlay | text | ยังไม่เคยดึงอัตโนมัติ — ใส่เองด้านบน หรือกด "ดึงเรทล่าสุด" | 22131 |
| Sheet (forced open) · setOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · setOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · setOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · setOverlay | text | 🔄 ดึงเรทล่าสุด | 22131 |
| Sheet (forced open) · sysOverlay | text | ($) · ล่าสุดก่อน | 14208 |
| Sheet (forced open) · sysOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · sysOverlay | text | ค่าเริ่ม = ยอดตอนตั้งเป้า (ใส่ย้อนหลังได้) · ไม่ตั้งเป้า = บัญชีนั้นไม่แสดงแถว · ต้องมี เป้า > ค่าเริ่ม > 0 และ วันครบ > วันเริ่ม | 14205 |
| Sheet (forced open) · sysOverlay | text | ค่าเริ่มต้น | 6758 |
| Sheet (forced open) · sysOverlay | text | บ | dynamic |
| Sheet (forced open) · sysOverlay | text | บัญชี | 178 |
| Sheet (forced open) · sysOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · sysOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · sysOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · sysOverlay | option | บัญชีหลัก | 2056 |
| Sheet (forced open) · sysOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · sysOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · sysOverlay | text | บันทึกเป้า | 14206 |
| Sheet (forced open) · sysOverlay | text | ประวัติค่าพอร์ต บัญชีหลัก | dynamic |
| Sheet (forced open) · sysOverlay | text | ยังไม่มีประวัติ | 14209 |
| Sheet (forced open) · sysOverlay | text | ลบ | dynamic |
| Sheet (forced open) · sysOverlay | text | วันครบกำหนด | 14202 |
| Sheet (forced open) · sysOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · sysOverlay | text | วันเริ่ม | 14204 |
| Sheet (forced open) · sysOverlay | text | สกุลเงิน | 14200 |
| Sheet (forced open) · sysOverlay | text | สลับไป | 9820 |
| Sheet (forced open) · sysOverlay | text | สำรองล่าสุดจากเครื่องนี้: 2026-10-02 13:03 น. | 28268 |
| Sheet (forced open) · sysOverlay | title | สีประจำบัญชี | 9770 |
| Sheet (forced open) · sysOverlay | text | เปิดอยู่ | 9585 |
| Sheet (forced open) · sysOverlay | text | เป้า | 372 |
| Sheet (forced open) · sysOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · sysOverlay | text | แสดงในหน้ารวม | 9771 |
| Sheet (forced open) · sysOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · teOverlay | text | Invalidation — อะไรจะบอกว่าไม้นี้ผิดทาง | 6432 |
| Sheet (forced open) · teOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · teOverlay | text | จำนวน (Qty / สัญญา / Lot) | 6426 |
| Sheet (forced open) · teOverlay | text | บ | dynamic |
| Sheet (forced open) · teOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · teOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · teOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · teOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · teOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · teOverlay | text | บันทึก | 2163 |
| Sheet (forced open) · teOverlay | text | ยกเลิก | 2727 |
| Sheet (forced open) · teOverlay | text | รูปภาพ Chart (ลิงก์ Google Drive, ถ้ามี) | 6435 |
| Sheet (forced open) · teOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · teOverlay | placeholder | เช่น ปิดต่ำกว่า EMA50 รายวัน, volume แห้งติดกัน 3 วัน | 6433 |
| Sheet (forced open) · teOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · teOverlay | text | แก้ไม้ | 6415 |
| Sheet (forced open) · teOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet (forced open) · wlAddOverlay | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet (forced open) · wlAddOverlay | text | บ | dynamic |
| Sheet (forced open) · wlAddOverlay | text | บัญชี 3 | dynamic |
| Sheet (forced open) · wlAddOverlay | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet (forced open) · wlAddOverlay | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet (forced open) · wlAddOverlay | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet (forced open) · wlAddOverlay | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet (forced open) · wlAddOverlay | aria-label | วันนี้ | 274 |
| Sheet (forced open) · wlAddOverlay | title | เพิ่มเติม | 121 |
| Sheet (forced open) · wlAddOverlay | title | ไปหน้าแผน (T) | 6157 |
| Sheet · Core weekly-close price | text | EMA10 รายสัปดาห์ (ว่างได้) | 16633 |
| Sheet · Core weekly-close price | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet · Core weekly-close price | text | บ | dynamic |
| Sheet · Core weekly-close price | text | บัญชี 3 | dynamic |
| Sheet · Core weekly-close price | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet · Core weekly-close price | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet · Core weekly-close price | aria-label | บัญชีหลัก | 2056 |
| Sheet · Core weekly-close price | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet · Core weekly-close price | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet · Core weekly-close price | text | บันทึก | 2163 |
| Sheet · Core weekly-close price | text | ยกเลิก | 2727 |
| Sheet · Core weekly-close price | text | ราคาปิด | 6447 |
| Sheet · Core weekly-close price | text | วันที่ (ศุกร์ล่าสุด) | 16632 |
| Sheet · Core weekly-close price | aria-label | วันนี้ | 274 |
| Sheet · Core weekly-close price | text | อัปเดตราคาปิดสัปดาห์ · AAA | dynamic |
| Sheet · Core weekly-close price | title | เพิ่มเติม | 121 |
| Sheet · Core weekly-close price | title | ไปหน้าแผน (T) | 6157 |
| Sheet · New Core plan | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Sheet · New Core plan | text | บ | dynamic |
| Sheet · New Core plan | text | บัญชี 3 | dynamic |
| Sheet · New Core plan | title | บัญชี 3 · . previous · / next | dynamic |
| Sheet · New Core plan | aria-label | บัญชี 3, 1 waiting | dynamic |
| Sheet · New Core plan | aria-label | บัญชีหลัก | 2056 |
| Sheet · New Core plan | title | บัญชีหลัก · . previous · / next | dynamic |
| Sheet · New Core plan | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Sheet · New Core plan | aria-label | วันนี้ | 274 |
| Sheet · New Core plan | title | เพิ่มเติม | 121 |
| Sheet · New Core plan | title | ไปหน้าแผน (T) | 6157 |
| Today · Daily | text | ($) · ล่าสุดก่อน | 14208 |
| Today · Daily | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Today · Daily | title | ขึ้นบนสุด | 10739 |
| Today · Daily | text | ค่าเริ่ม = ยอดตอนตั้งเป้า (ใส่ย้อนหลังได้) · ไม่ตั้งเป้า = บัญชีนั้นไม่แสดงแถว · ต้องมี เป้า > ค่าเริ่ม > 0 และ วันครบ > วันเริ่ม | 14205 |
| Today · Daily | text | ค่าเริ่มต้น | 6758 |
| Today · Daily | text | บัญชี | 178 |
| Today · Daily | aria-label | บัญชีหลัก | 2056 |
| Today · Daily | title | บัญชีหลัก · . previous · / next | dynamic |
| Today · Daily | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Today · Daily | text | บันทึกเป้า | 14206 |
| Today · Daily | text | ประวัติค่าพอร์ต บัญชีหลัก | dynamic |
| Today · Daily | text | ยังไม่มีประวัติ | 14209 |
| Today · Daily | text | ลบ | dynamic |
| Today · Daily | text | วันครบกำหนด | 14202 |
| Today · Daily | aria-label | วันนี้ | 274 |
| Today · Daily | text | วันเริ่ม | 14204 |
| Today · Daily | text | สกุลเงิน | 14200 |
| Today · Daily | text | สลับไป | 9820 |
| Today · Daily | text | สำรองล่าสุดจากเครื่องนี้: 2026-10-02 13:03 น. | 28268 |
| Today · Daily | title | สีประจำบัญชี | 9770 |
| Today · Daily | text | เปิดอยู่ | 9585 |
| Today · Daily | text | เป้า | 372 |
| Today · Daily | title | เพิ่มเติม | 121 |
| Today · Daily | text | แสดงในหน้ารวม | 9771 |
| Today · Daily | title | ไปหน้าแผน (T) | 6157 |
| Today · Weekend | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Today · Weekend | title | ขึ้นบนสุด | 10739 |
| Today · Weekend | aria-label | บัญชีหลัก | 2056 |
| Today · Weekend | title | บัญชีหลัก · . previous · / next | dynamic |
| Today · Weekend | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Today · Weekend | text | ปิด | dynamic |
| Today · Weekend | aria-label | วันนี้ | 274 |
| Today · Weekend | text | สรุปสัปดาห์นี้ยังไม่พร้อม | 27613 |
| Today · Weekend | title | เพิ่มเติม | 121 |
| Today · Weekend | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · AAPL Homework | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · AAPL Homework | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · AAPL Homework | text | บัญชีหลัก (2 trades) | dynamic |
| Watch (fixture) · AAPL Homework | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · AAPL Homework | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · AAPL Homework | aria-label | วันนี้ | 274 |
| Watch (fixture) · AAPL Homework | title | เพิ่มเติม | 121 |
| Watch (fixture) · AAPL Homework | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · AAPL detail | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · AAPL detail | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · AAPL detail | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · AAPL detail | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · AAPL detail | aria-label | วันนี้ | 274 |
| Watch (fixture) · AAPL detail | title | เพิ่มเติม | 121 |
| Watch (fixture) · AAPL detail | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · Add stocks sheet | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · Add stocks sheet | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · Add stocks sheet | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · Add stocks sheet | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · Add stocks sheet | aria-label | วันนี้ | 274 |
| Watch (fixture) · Add stocks sheet | title | เพิ่มเติม | 121 |
| Watch (fixture) · Add stocks sheet | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · COST Homework | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · COST Homework | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · COST Homework | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · COST Homework | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · COST Homework | aria-label | วันนี้ | 274 |
| Watch (fixture) · COST Homework | title | เพิ่มเติม | 121 |
| Watch (fixture) · COST Homework | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · Compounder list | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · Compounder list | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · Compounder list | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · Compounder list | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · Compounder list | aria-label | วันนี้ | 274 |
| Watch (fixture) · Compounder list | title | เพิ่มเติม | 121 |
| Watch (fixture) · Compounder list | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · Ideas | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · Ideas | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · Ideas | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · Ideas | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · Ideas | aria-label | วันนี้ | 274 |
| Watch (fixture) · Ideas | title | เพิ่มเติม | 121 |
| Watch (fixture) · Ideas | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · Momentum list | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · Momentum list | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · Momentum list | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · Momentum list | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · Momentum list | aria-label | วันนี้ | 274 |
| Watch (fixture) · Momentum list | title | เพิ่มเติม | 121 |
| Watch (fixture) · Momentum list | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · Screen | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · Screen | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · Screen | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · Screen | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · Screen | aria-label | วันนี้ | 274 |
| Watch (fixture) · Screen | title | เพิ่มเติม | 121 |
| Watch (fixture) · Screen | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · WHSE Homework | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · WHSE Homework | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · WHSE Homework | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · WHSE Homework | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · WHSE Homework | aria-label | วันนี้ | 274 |
| Watch (fixture) · WHSE Homework | title | เพิ่มเติม | 121 |
| Watch (fixture) · WHSE Homework | title | ไปหน้าแผน (T) | 6157 |
| Watch (fixture) · ZZ Homework | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch (fixture) · ZZ Homework | aria-label | บัญชีหลัก | 2056 |
| Watch (fixture) · ZZ Homework | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch (fixture) · ZZ Homework | aria-label | บัญชีหลัก, 2 waiting | dynamic |
| Watch (fixture) · ZZ Homework | aria-label | วันนี้ | 274 |
| Watch (fixture) · ZZ Homework | title | เพิ่มเติม | 121 |
| Watch (fixture) · ZZ Homework | title | ไปหน้าแผน (T) | 6157 |
| Watch · Homework page | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch · Homework page | aria-label | บัญชีหลัก | 2056 |
| Watch · Homework page | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch · Homework page | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Watch · Homework page | aria-label | วันนี้ | 274 |
| Watch · Homework page | title | เพิ่มเติม | 121 |
| Watch · Homework page | title | ไปหน้าแผน (T) | 6157 |
| Watch · Ideas | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch · Ideas | aria-label | บัญชีหลัก | 2056 |
| Watch · Ideas | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch · Ideas | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Watch · Ideas | aria-label | วันนี้ | 274 |
| Watch · Ideas | title | เพิ่มเติม | 121 |
| Watch · Ideas | title | ไปหน้าแผน (T) | 6157 |
| Watch · Momentum/Compounder list | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch · Momentum/Compounder list | aria-label | บัญชีหลัก | 2056 |
| Watch · Momentum/Compounder list | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch · Momentum/Compounder list | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Watch · Momentum/Compounder list | aria-label | วันนี้ | 274 |
| Watch · Momentum/Compounder list | title | เพิ่มเติม | 121 |
| Watch · Momentum/Compounder list | title | ไปหน้าแผน (T) | 6157 |
| Watch · Screen | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch · Screen | aria-label | บัญชีหลัก | 2056 |
| Watch · Screen | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch · Screen | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Watch · Screen | aria-label | วันนี้ | 274 |
| Watch · Screen | title | เพิ่มเติม | 121 |
| Watch · Screen | title | ไปหน้าแผน (T) | 6157 |
| Watch · stock detail | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Watch · stock detail | aria-label | บัญชีหลัก | 2056 |
| Watch · stock detail | title | บัญชีหลัก · . previous · / next | dynamic |
| Watch · stock detail | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Watch · stock detail | aria-label | วันนี้ | 274 |
| Watch · stock detail | title | เพิ่มเติม | 121 |
| Watch · stock detail | title | ไปหน้าแผน (T) | 6157 |
| Weekly backup banner (forced open) | title | Trading Dashboard — ความเสี่ยงรวม + Trading Journal · ฐานคำนวณ THB | 6136 |
| Weekly backup banner (forced open) | text | ดาวน์โหลด | 10263 |
| Weekly backup banner (forced open) | text | ถึงเวลาสำรองข้อมูลประจำสัปดาห์ | 27891 |
| Weekly backup banner (forced open) | text | บ | dynamic |
| Weekly backup banner (forced open) | text | บัญชี 3 | dynamic |
| Weekly backup banner (forced open) | title | บัญชี 3 · . previous · / next | dynamic |
| Weekly backup banner (forced open) | aria-label | บัญชี 3, 1 waiting | dynamic |
| Weekly backup banner (forced open) | title | บัญชีหลัก · . previous · / next | dynamic |
| Weekly backup banner (forced open) | aria-label | บัญชีหลัก, 9 waiting | dynamic |
| Weekly backup banner (forced open) | aria-label | วันนี้ | 274 |
| Weekly backup banner (forced open) | title | เพิ่มเติม | 121 |
| Weekly backup banner (forced open) | text | แตะเพื่อบันทึกไฟล์ backup ลงเครื่อง | 27892 |
| Weekly backup banner (forced open) | title | ไปหน้าแผน (T) | 6157 |
| Weekly backup banner (forced open) | text | ไว้ก่อน | 10631 |

## B · Browser pop-ups

**Replaced** (trade flows; in-app sheet, Enter = confirm / save, Esc = cancel; `cl2Ask` / `cl2FillOpen`):

| Flow | Was | Now |
|---|---|---|
| Filled ✓ (`sat7dMarkOpen`) | `prompt('ราคาเข้าจริง')` + `alert('ราคาไม่ถูกต้อง')` | Sheet "Filled · XAUUSD" — Entry price prefilled with the planned entry, ⚠ line if not a number above 0, Cancel / Save |
| Close / partial exit (`confirmClosePos`) | `alert` ×2 | toast ("Type the exit price first" / "Qty must be between 0 and N") — the sheet already shows the ⚠ line and keeps Confirm off |
| Cancel plan (`confirmCancel`) | `alert` | ⚠ line inside the Cancel sheet ("Pick a reason tag or type a note") |
| Delete trade (`delTrade`) | `confirm` | confirm sheet "Delete this trade?" |
| Cancelled → back to Plan (`restoreCancelled`) | `confirm` | confirm sheet "Move X back to Plan?" |
| Remove from Candidates (`td4CandDelete`) ×2 | `confirm` ×2 | confirm sheet "Remove X?" |
| Homework leave with unsaved changes (`hwBack`) | `confirm` | confirm sheet "Leave this page?" (Leave / Stay) |
| Homework / thesis Cancel with edits (`wlMtCancel`) | `confirm` | confirm sheet "Discard your changes?" |
| Place at broker (`ln4Place`, unreachable old path) | `confirm` | removed (Place order already uses its own sheet) |
| Watch Remove / Undo / Restore (`ux3RemoveDo`, `ux3RemoveUndo`, `wlRestore`) | `alert` ×3 | toast |

Spy test (`tests/run_tests_cl2.py`): `window.prompt / alert / confirm` are never called through plan → Place → Filled → Move stop → partial exit → Close, the confirm sheets, and Homework leave.

**Remaining** (outside those flows — not changed this round; Thai texts in them are now English):
- Accounts / Settings: `acctSetShow`, `lrDefSet`, `acctSwitch` (alert) · `acctAdd` (**prompt**) · `acctTogglePort`, `acctDelete` ×1 alert + ×2 confirm · `glCapGo`, `glSetDel`, `glHistDel` (confirm) · `addIndustry` ×2 (alert) · `deleteIndustry` (confirm) · `addReasonTag` ×2 (alert) · `deleteReasonTag`, `resetReasonTags`, `resetScoreLabels` (confirm) · `setScoreLabel` (alert) · `jBackfillOpen` (alert) · `refreshFxField` (alert) · `brDelAsset`, `sat7dBrokerSave` (confirm) · `satwCopyFromPrev` (alert)
- Fund-flow / backup: `ffDelProxy` (confirm) · `exportBackupNow` ×2, `bkRestoreOpen` ×2, `bkRestoreLoad` (alert)
- Watch / Ideas / Notes: `vwDelImg`, `vwDel` (confirm) · `wlDeleteItem` (confirm + alert) · `wlOpenAdd`, `wlAddSave` ×2, `wlTierClear`, `wlNoteWrite`, `wlNoteSave`, `wlFocusToggle` (alert) · `ideaUserPatch`, `ideaImportOpen`, `ideaImpSave` ×2, `ideaDelDo`, `ideaCreateDraft` ×2, `ideaNewOpen` (alert) · `trdPatch`, `trdNewOpen`, `trdNewSave` ×2, `trdDelDo`, `trdImpSave` ×3 (alert) · `ltImportOpen`, `ltImpSave` ×4, `ltHit` (alert) · `nt1Write`, `nt1Del`, `nt1ReviewSave`, `nt1SheetOpen`, `nt1bPatchMy`, `nt1bPatchAi` (alert) · `nt1SheetCancel` (confirm) · `mv1Move`, `mv1Undo` (alert)

Live call sites: **prompt 3 → 1 · confirm 25 → 16 · alert 64 → 56** (grep; the one other `prompt(` hit is a comment).
