# TS1 progress

Branch claude/ts1 (from origin/main 2739856). Order note: §4 (node-only) and §2 were done before §1 finished because §1 needs a full browser re-run; each has its own commit.

## §1 — "before": every browser suite on the base commit (origin/main 2739856, 4 parallel)

Totals: 149 suites · 19 pass · 130 fail

| suite | status | PASS | FAIL | sec | first failing check / error |
|---|---|---|---|---|---|
| run_tests | fail | 51 | 3 | 6 | FAIL - [1440px] console: zero error-level messages  :: Failed to load resource: the server responded with a st |
| run_tests_aw1 | ok | 113 | 0 | 77 |  |
| run_tests_phase1 | ok | 20 | 0 | 3 |  |
| run_tests_phase2 | ok | 54 | 0 | 6 |  |
| run_tests_phase3 | fail | 72 | 7 | 9 | FAIL - [chromium/1440px] เตรียมเคส 'รวมด้วย (นอกแผน)': fam คำนวณ lot ได้จริง แต่โควตาไม้ใหม่สัปดาห์นี้เต็ม (4/ |
| run_tests_phase4 | fail | 5 | 0 | 32 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase5 | fail | 4 | 0 | 32 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase6 | fail | 1 | 0 | 32 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase7 | fail | 0 | 0 | 32 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase8 | fail | 16 | 0 | 4 | playwright._impl._errors.Error: Page.evaluate: TypeError: Cannot read properties of null (reading 'textContent |
| run_tests_phase9 | fail | 62 | 2 | 33 | FAIL - [chromium/1440px] panel อยู่ใต้แถบดำ (#ffAction) ติดกัน ไม่มี #ffChanges แล้ว |
| run_tests_phase10 | ok | 11 | 0 | 12 |  |
| run_tests_phase11 | fail | 13 | 3 | 33 | FAIL - [chromium/1440px] Calc.sizeRule: ครบ 24 คู่ (macroAlign 4 × trend 3 × side 2)  :: against/up/Long={"fac |
| run_tests_phase12 | fail | 12 | 6 | 5 | FAIL - [chromium/1440px] #pbPanel กาง: [UI2a แก้] กล่อง 'ข้อควรติดตาม' (หัวแยก) + 'ดู CPI วันพฤหัส' ใต้ thesis |
| run_tests_phase13 | fail | 10 | 0 | 39 | playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded. |
| run_tests_phase14 | fail | 0 | 0 | 3 | playwright._impl._errors.Error: Page.evaluate: TypeError: Cannot read properties of undefined (reading 'length |
| run_tests_phase15 | fail | 58 | 0 | 44 | TypeError: 'NoneType' object is not subscriptable |
| run_tests_phase16 | fail | 0 | 0 | 0 | playwright._impl._errors.Error: Page.goto: net::ERR_FILE_NOT_FOUND at file:///Users/peach/Dashboard-ts1/index. |
| run_tests_phase17 | fail | 1 | 2 | 3 | FAIL - [chromium/1440px] .pbWatch: หัว 'ข้อควรติดตาม' แยก element + เนื้อความแยก |
| run_tests_phase18 | fail | 12 | 0 | 36 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase19 | fail | 143 | 3 | 70 | FAIL - [chromium/1440px] หลังรีเซ็ต: console zero error · zero page error (ทุกแท็บ + ตั้งค่า)  :: Failed to lo |
| run_tests_phase20 | fail | 74 | 3 | 26 | FAIL - [chromium/1440x900] เปิดทุกแท็บ + ตั้งค่า: ไม่มี console error  :: ["Failed to load resource: the serve |
| run_tests_phase21 | fail | 4 | 2 | 34 | FAIL - [chromium/1440x900] กด T → ไปแท็บแผน (goPlanTop) · ไม่มี overlay เปิด · ไม่มี error (CL2-d+: เดิมไม่เกิ |
| run_tests_phase22 | fail | 4 | 1 | 2 | FAIL - [chromium/1440x900] Positions main: แสดง B C A เท่านั้น (Core ก่อน Sat · วันเข้าเก่าก่อน) · ไม่มี D pla |
| run_tests_phase23 | fail | 13 | 1 | 35 | FAIL - sync_core_size.py: สำเนาเพี้ยน → --check = exit 1 · รันแทนที่ → --check = exit 0 · ไฟล์ตรงกับ index.htm |
| run_tests_phase24 | fail | 0 | 2 | 33 | FAIL - [chromium/1440x900] scope หุ้น กด ＋ → เปิด sheet 'แผน Core ใหม่' |
| run_tests_phase25 | fail | 7 | 1 | 93 | FAIL - [chromium/1440x900] 2 แถวแผน META: 'แผน · Entry 600 · Stop 560 · ไม้แรก 26 หุ้น' (RG2b เพดานเดียว)  ::  |
| run_tests_phase26 | fail | 1 | 0 | 1 | FileNotFoundError: [Errno 2] No such file or directory: '/Users/peach/Dashboard-ts1/core-size.backup-pre-7E2b1 |
| run_tests_phase27 | fail | 15 | 1 | 33 | FAIL - [chromium/1440px] console: zero error-level messages  :: Failed to load resource: the server responded  |
| run_tests_phase28 | fail | 1 | 0 | 32 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase29 | fail | 88 | 10 | 231 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase30 | fail | 10 | 1 | 43 | shot fail su-sat-active-label-1440px.png Locator.screenshot: Timeout 29996ms exceeded. |
| run_tests_phase31 | fail | 17 | 0 | 47 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase32 | fail | 15 | 0 | 37 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase33 | fail | 25 | 0 | 44 | playwright._impl._errors.TimeoutError: Page.click: Timeout 30000ms exceeded. |
| run_tests_phase34 | fail | 14 | 6 | 66 | FAIL - [chromium/1440px] 1 ไม่มี satRisk → ค่าเริ่มต้น rpt 1.5 · rptHi 2 · heat 6 · ใหม่ 2 (ทั้ง 2 บัญชี)  ::  |
| run_tests_phase35 | ok | 72 | 0 | 41 |  |
| run_tests_phase36 | fail | 1 | 1 | 2 | FAIL - [chromium/1440px] 15 console: zero error-level messages  :: Failed to load resource: the server respond |
| run_tests_phase37 | fail | 10 | 0 | 40 | playwright._impl._errors.TimeoutError: Page.is_checked: Timeout 30000ms exceeded. |
| run_tests_phase38 | fail | 12 | 4 | 11 | FAIL - [chromium/1440px] 2 เลขแดงบนปุ่มแท็บ = จำนวน 🔴 (3)  :: {"t": "2", "shown": true} |
| run_tests_phase39 | fail | 4 | 0 | 6 | playwright._impl._errors.Error: Page.evaluate: ReferenceError: ddEval is not defined |
| run_tests_phase40 | fail | 4 | 2 | 35 | FAIL - [static] 18 ไฟล์ทั้งหมดอยู่ใน _to_delete/research-card/ (ไม่ลบ)  :: [] |
| run_tests_phase41 | fail | 5 | 1 | 37 | FAIL - [static] สำรอง index.backup-pre-WL3.html + tests/_bk_wl3/ อยู่ |
| run_tests_phase42 | fail | 1 | 1 | 34 | FAIL - [static] สำรอง index.backup-pre-NUM1.html + tests/_bk_num1/ อยู่ |
| run_tests_phase43 | fail | 0 | 2 | 0 | FAIL - [static] สำรอง index.backup-pre-PX1.html + tests/_bk_px1/ อยู่ |
| run_tests_phase44 | fail | 131 | 13 | 140 | FAIL - [chromium/1440px] 2 pills ลำดับ Ideas · Candidates · Watchlist (TD4a เดิม: Watchlist · Ideas · Candidat |
| run_tests_phase45 | fail | 1 | 4 | 4 | FAIL - [static] wlRowsAll().cand ไม่อ่าน research (ไม่มี rsAll() ใน cand) |
| run_tests_phase46 | fail | 29 | 8 | 44 | FAIL - [static] สำรอง index.backup-pre-NUM2.html + tests/_bk_num2/ อยู่ |
| run_tests_phase47 | fail | 1 | 0 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/Users/peach/Dashboard-ts1/core-size.backup-pre-CZ1.j |
| run_tests_phase48 | fail | 24 | 0 | 104 | shot fail px2-ema-fill-1440.png Locator.screenshot: Timeout 29993ms exceeded. |
| run_tests_phase49 | ok | 94 | 0 | 76 |  |
| run_tests_phase50 | ok | 40 | 0 | 48 |  |
| run_tests_phase51 | ok | 123 | 0 | 274 |  |
| run_tests_phase52 | fail | 35 | 5 | 23 | FAIL - [chromium/1440px] 1 Candidates (NVDA US) มีปุ่ม 📊 → /symbols/NVDA/financials-revenue/  :: https://www.t |
| run_tests_phase53 | fail | 4 | 0 | 65 | shot fail cx1-core-head-normal-1440.png Locator.screenshot: Timeout 29993ms exceeded. |
| run_tests_phase54 | fail | 5 | 0 | 7 | playwright._impl._errors.Error: Page.goto: net::ERR_FILE_NOT_FOUND at file:///Users/peach/Dashboard-ts1/index. |
| run_tests_phase55 | fail | 4 | 0 | 7 | playwright._impl._errors.Error: Page.goto: net::ERR_FILE_NOT_FOUND at file:///Users/peach/Dashboard-ts1/index. |
| run_tests_phase56 | fail | 4 | 0 | 4 | playwright._impl._errors.Error: Page.goto: net::ERR_FILE_NOT_FOUND at file:///Users/peach/Dashboard-ts1/index. |
| run_tests_phase57 | ok | 44 | 0 | 29 |  |
| run_tests_phase58 | fail | 0 | 0 | 5 | playwright._impl._errors.Error: Page.goto: net::ERR_FILE_NOT_FOUND at file:///Users/peach/Dashboard-ts1/index. |
| run_tests_phase59 | fail | 2 | 0 | 41 | playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded. |
| run_tests_phase60 | fail | 1 | 0 | 35 | playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded. |
| run_tests_phase61 | fail | 0 | 4 | 36 | FAIL - [chromium/1440px] 1 Watchlist ไม่มี phase → ชิป '—' ทุกแถว (3 แถว)  :: [{"s": "AVGO", "ph": null, "t":  |
| run_tests_phase62 | ok | 0 | 0 | 1 |  |
| run_tests_phase63 | fail | 9 | 0 | 66 | shot fail ac2-plan-1440.png Locator.screenshot: Timeout 29993ms exceeded. |
| run_tests_phase64 | fail | 3 | 1 | 35 | FAIL - [chromium/1440px] 1 Candidates: ไม่มีแถว data-cand-filters/data-tq-filters/data-ph-filters (3 แถวเดิม)  |
| run_tests_phase65 | fail | 10 | 0 | 69 | shot fail cz1-settings-1440.png Locator.screenshot: Timeout 29993ms exceeded. |
| run_tests_phase66 | fail | 0 | 0 | 0 | FileNotFoundError: [Errno 2] No such file or directory: '/Users/peach/Dashboard-ts1/tests/../core-size.backup- |
| run_tests_phase67 | fail | 21 | 4 | 85 | FAIL - [chromium/1440px] 1 เมนู phase (PH1): เปิด (0) → Esc → ปิด (0) |
| run_tests_phase68 | fail | 3 | 1 | 7 | FAIL - [chromium/1440px] 1 การ์ดแสดง 6 แถว เรียง ★ ก่อน → ▲▼ เต็ม → ▲▬ → ▬  :: [] |
| run_tests_phase69 | fail | 1 | 0 | 66 | shot fail wa1-week-empty-1440.png Locator.screenshot: Timeout 29993ms exceeded. |
| run_tests_phase70 | fail | 6 | 1 | 75 | shot fail py2-plan-size-1440.png Locator.screenshot: Timeout 29993ms exceeded. |
| run_tests_phase71 | fail | 8 | 0 | 106 | shot fail co1-carried-1440.png Locator.screenshot: Timeout 29997ms exceeded. |
| run_tests_phase72 | fail | 47 | 3 | 243 | shot fail wa1fix-empty-1440.png Locator.screenshot: Timeout 29989ms exceeded. |
| run_tests_phase73 | fail | 44 | 0 | 113 | shot fail tr1-plan-link-1440.png Locator.screenshot: Timeout 29997ms exceeded. |
| run_tests_phase74 | fail | 2 | 0 | 36 | playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded. |
| run_tests_phase75 | fail | 4 | 2 | 5 | FAIL - S4 RR1fix: มีตัวกันซ้อน rrBusy/rrPending + blur() ก่อน replaceChildren |
| run_tests_phase76 | fail | 0 | 1 | 35 | FAIL - [chromium/1440px] 0 เตรียม: ภาพ XAUUSD โหลดแล้ว · แผนร่าง 1 ใบมีปุ่ม TF |
| run_tests_phase77 | fail | 2 | 0 | 36 | playwright._impl._errors.TimeoutError: Page.select_option: Timeout 30000ms exceeded. |
| run_tests_phase78 | fail | 6 | 13 | 67 | FAIL - [chromium/1440px] PF3 1 Strategy bias เก่า Long · Tactical Short (ไม่มี Main): ประเภท = accel (ไม่ใช่ h |
| run_tests_phase79 | fail | 1 | 0 | 36 | playwright._impl._errors.TimeoutError: Page.fill: Timeout 30000ms exceeded. |
| run_tests_phase80 | fail | 5 | 1 | 65 | shot fail ln1-old-mode-1440.png Locator.screenshot: Timeout 29991ms exceeded. |
| run_tests_phase81 | fail | 0 | 1 | 7 | FAIL - [chromium/1440px] 1 (LN3fix3c) ไม่มีสวิตช์เลือกบัญชี · กล่องเดียว · 2 แถว (บัญชีหลัก · Family) เห็นพร้อ |
| run_tests_phase82 | fail | 0 | 0 | 6 | playwright._impl._errors.Error: Page.evaluate: TypeError: Cannot read properties of null (reading 'innerText') |
| run_tests_phase83 | fail | 57 | 6 | 60 | FAIL - [chromium/1440px] 4 การ์ด Momentum: หัว 'Momentum Port · DD x% · สถานะ' ไม่ซ้ำทุน (ไม่มีคำว่า ทุน/฿ ในห |
| run_tests_phase84 | fail | 1 | 2 | 4 | FAIL - [chromium/1440px] 1 หัวกล่อง: 'พฤ. 8 ต.ค.' · 'n/N วันนี้ · m/M สัปดาห์' ตรงผลคำนวณเดิม · ปุ่ม Daily / W |
| run_tests_phase85 | fail | 2 | 4 | 6 | FAIL - [chromium/1440px] 1 AVGO: Tier A · ป้ายเตือน '🟠 ทบทวน' (tripwire review) · มีจุดถืออยู่ + จุด Thesis  : |
| run_tests_phase86 | fail | 0 | 0 | 2 | playwright._impl._errors.Error: Page.evaluate: TypeError: Cannot read properties of undefined (reading 'length |
| run_tests_phase87 | fail | 51 | 5 | 23 | FAIL - [chromium/1440px] 2 ชิปกรอง: ทั้งหมด · Win · Loss · นอกแผน · Setup ไม่ครบ · ไม้เร่ง · ＋ ย้อนหลัง (ไม่มี |
| run_tests_phase88 | ok | 0 | 0 | 0 |  |
| run_tests_phase89 | fail | 2 | 2 | 6 | FAIL - [chromium/1440px] 1 บนสุดปุ่ม 'Core / Sat' (ไม่มี 'Port หุ้น / Port Future') · Core ติดอยู่  :: {"a": " |
| run_tests_phase90 | fail | 16 | 7 | 70 | FAIL - [chromium/1440px] 1 Mac: ไม่มีแถบปุ่ม Asset (ไม่แสดงปุ่มต่อ Asset) · การ์ด 2 คอลัมน์ เห็นทุก Asset  ::  |
| run_tests_phase91 | fail | 46 | 4 | 147 | FAIL - [chromium/1440px] 2 แถวการ์ด 'ไม้ 1 · SL 115 · เร่ง 140' · กางเห็นกล่อง 2 แถว 'Base 80 @131 SL 115' / ' |
| run_tests_phase92 | fail | 1 | 3 | 12 | FAIL - [chromium/1440px] 1 หัวการ์ด 'แผน & ไม้ที่ถือ' · 'ถือ 2 · แผน 1' (XAU ที่เข้าแล้ว + BTC นอกแผน · BTC ร่ |
| run_tests_phase93 | fail | 4 | 0 | 37 | playwright._impl._errors.TimeoutError: Locator.fill: Timeout 30000ms exceeded. |
| run_tests_phase94 | fail | 1 | 2 | 14 | FAIL - [chromium/1440px] 1 งาน 'XAU เติมไม้ … ได้' ของ 2 บัญชีบอกชื่อบัญชี (จุดสี + ชื่อ) ไม่ซ้ำคลุมเครือ  ::  |
| run_tests_phase95 | fail | 29 | 1 | 29 | FAIL - [chromium/1280px] 1 1280px ไม่ล้นแนวนอน · ไม่มี console error  :: [0, ["Failed to load resource: the se |
| run_tests_phase96 | fail | 49 | 5 | 65 | FAIL - [chromium/1440px] 2 เต็มจอ: .wlDPanel กว้าง ≥ จอ − 2×48px − 2 (760 ≥ 1342) · เริ่มชิดขอบด้านใน  :: {"W" |
| run_tests_phase97 | fail | 0 | 0 | 0 | SyntaxError: invalid syntax. Perhaps you forgot a comma? |
| run_tests_phase98 | fail | 2 | 1 | 40 | FAIL - [chromium/300px] 1 Strategy: แท็บ Asset · เลือกสัปดาห์ · Risk Sat ทุกบัญชี ยังอยู่ · + แผน กดได้โดยไม่ม |
| run_tests_phase99 | fail | 2 | 1 | 37 | FAIL - [chromium/300px] 1 Plan ครั้งแรก: ปุ่ม Momentum / Compounder / Sat มองเห็นครบสามปุ่ม (ใน header หรือในห |
| run_tests_phase100 | fail | 96 | 2 | 102 | FAIL - [chromium/390px] 6 เหตุการณ์ของวันนี้: แสดงใต้ 'ข่าววันนี้ · เวลาไทย' · Core PCE แถวเดียว รวม Asset ที่ |
| run_tests_phase101 | fail | 14 | 2 | 69 | FAIL - [chromium/390px] 2 อาทิตย์ 20:00 ICT: event 20:30 ของวันอาทิตย์ (อยู่สแนปช็อตสัปดาห์ก่อน + ซ้ำในสแนปช็อ |
| run_tests_phase102 | fail | 4 | 5 | 31 | FAIL - [chromium/390px] 1 TD3a: 3 panels (Overview · Core Port · Satellite) ชิดบนเท่ากันบน Mac · ไม่ล้นแนวนอน  |
| run_tests_phase103 | fail | 60 | 16 | 98 | FAIL - [chromium/1280px/long] 4 TD3a: 3 panels ชิดบนเท่ากัน (Mac) · ไม่ล้นแนวนอน  :: {"n": 2, "tops": [306, 46 |
| run_tests_phase104 | fail | 5 | 11 | 103 | FAIL - [chromium/390px] 1 เปิด Plan › Sat → Strategy วาดแผง Weekly Impact + การ์ด Asset ตามสแนปช็อต · ธงล้าง   |
| run_tests_phase105 | fail | 35 | 24 | 68 | FAIL - [chromium/1440px] 1 หัวมุมมอง lean = 'Leadership' (ไม่ใช่ เงินไหลเข้าธีมไหน) |
| run_tests_phase106 | fail | 42 | 3 | 86 | FAIL - [chromium/1440px] B6 คิว: ยังไม่เคย screen เก่าสุดก่อน (C1 20d, A1 3d, D1 1d) แล้วค่อยตัวที่เคย screen  |
| run_tests_phase107 | fail | 4 | 6 | 19 | FAIL - [chromium/1440px] §1 ลำดับแท็บ Watch: Ideas → Candidates → Watchlist  :: [] |
| run_tests_phase108 | fail | 2 | 2 | 38 | FAIL - [chromium/390px] §1 ป้ายใหม่ 'MA Align Overlap' · key เดิม align_ma50 ไม่เปลี่ยน · ไม่มีคำว่า Align MA5 |
| run_tests_phase109 | fail | 5 | 5 | 70 | FAIL - [chromium/390px] §1 หัวเดียว 'Sectors · Daily' (ไม่มีป้าย SECTORS ซ้อนบน)  :: [0, ""] |
| run_tests_phase110 | fail | 13 | 0 | 14 | playwright._impl._errors.Error: Page.goto: net::ERR_FILE_NOT_FOUND at file:///Users/peach/Dashboard-ts1/index. |
| run_tests_phase111 | fail | 44 | 13 | 85 | FAIL - [chromium/budget/390] แผนใหม่ AAPL ★★★: งบ $1,273 − ใช้ $600 → tranche ≤ $673 → 67 หุ้น (ไม่แจกงบใหม่ซ้ |
| run_tests_phase112 | fail | 112 | 29 | 41 | playwright._impl._errors.Error: Page.evaluate: TypeError: Cannot read properties of undefined (reading 'length |
| run_tests_phase113 | fail | 0 | 0 | 0 | SyntaxError: '(' was never closed |
| run_tests_phase114 | fail | 7 | 8 | 18 | FAIL - [chromium/size/390] A4: หุ้นไม่มีการประเมิน/ไม่มี ★ → 'Base risk 1.00% of Momentum pool' · ไม้แรก 127 ห |
| run_tests_phase115 | fail | 7 | 0 | 43 | playwright._impl._errors.TimeoutError: Page.fill: Timeout 30000ms exceeded. |
| run_tests_phase116 | fail | 50 | 17 | 72 | FAIL - [chromium/scrfail/390] ยัง Candidate อยู่ (ไม่มีเอกสาร Watchlist) |
| run_tests_phase117 | fail | 1 | 1 | 7 | FAIL - [chromium/mgmt/390] A6 (LN4 §7): lean row — one tag per row, no status dots (status stays in wlStatusKe |
| run_tests_phase118 | fail | 44 | 8 | 51 | FAIL - [chromium/plan/390] A8: แผนใหม่ของหุ้น track Compounder → Base 1% ของ 'ถัง Compounder' + เพดาน 5% ของบั |
| run_tests_phase119 | fail | 0 | 1 | 7 | FAIL - [chromium/plans/390] A7: Plans block แทนแผง Satellite · กลุ่ม Momentum · Compounder (Sat ไม่ปรากฏเพราะไ |
| run_tests_phase120 | fail | 7 | 5 | 15 | FAIL - [chromium/1440] 2 Form: ยังไม่ตั้ง default risk → 'Set default risk in Settings' + บันทึกไม่ได้  :: [] |
| run_tests_phase121 | fail | 5 | 1 | 8 | FAIL - [chromium/today/1440] §1 Today: บรรทัดสรุปเดิมอยู่ · พับไว้ตั้งต้น · มีชิป Loss limits ต่อ port 3 ใบ ·  |
| run_tests_phase122 | fail | 44 | 6 | 35 | FAIL - [chromium/1440] §10 โหมดเดิม (ps1Off) ไม่มี NEW / ตัวกรอง  :: [2, 1] |
| run_tests_phase123 | fail | 5 | 4 | 11 | FAIL - [chromium/1440] §8 Today: ปักบนสุด 'Homework: ZZZ — thesis + screening · due in 3 days' + 'Do it ›' · ป |
| run_tests_phase124 | fail | 23 | 14 | 28 | FAIL - [chromium/1440] §7e MS1: Momentum SL ห่าง 3.9% → ไม่บล็อก · amber pill 'Sized on min stop 4% (your SL 3 |
| run_tests_phase125 | fail | 2 | 0 | 8 | TypeError: unsupported operand type(s) for +: 'NoneType' and 'NoneType' |
| run_tests_phase126 | fail | 48 | 37 | 114 | FAIL - [chromium/390] 1 switch → Compounder: port, switch, top scope, risk default (1) follow · typed Momentum |
| run_tests_phase362 | fail | 15 | 1 | 57 | FAIL - PL2·4 Today panel shows 'Selection' (not 'Core Port')  :: Mixed |
| run_tests_phase363 | fail | 52 | 2 | 51 | FAIL - [chromium] no console errors  :: [["Failed to load resource: the server responded with a status of 403  |
| run_tests_phase364 | ok | 26 | 0 | 20 |  |
| run_tests_phase365 | fail | 66 | 2 | 129 | FAIL - [chromium/390] 5 archived stock: Restore stays on the card |
| run_tests_phase366 | fail | 37 | 1 | 56 | FAIL - [chromium/390] 7 Daily line (Find card — LN4): plain muted div 'Weekly News · 1/3 unread · Read ›' · no |
| run_tests_phase367 | fail | 16 | 1 | 51 | FAIL - [chromium/1440] 3 stale → 2 shown + '+1'  :: [["living-thesis: C 60d", "living-thesis: B 50d", "living- |
| run_tests_phase369 | fail | 53 | 24 | 84 | FAIL - [chromium/1440] 1 Momentum Half → ONE amber chip 'MMT Half' (LN4c)  :: null |
| run_tests_phase370 | fail | 27 | 1 | 41 | FAIL - [chromium/390] settings: switch stays on the right  :: null |
| run_tests_phase371 | fail | 7 | 6 | 56 | TypeError: '>=' not supported between instances of 'NoneType' and 'float' |
| run_tests_phase372 | fail | 10 | 6 | 26 | FAIL - [390] single merged port chip :: {"chips": [], "swSameRowAsRegime": true, "rgTxt": "Risk-OFF", "room":  |
| run_tests_phase373 | fail | 419 | 1 | 453 | playwright._impl._errors.TimeoutError: Locator.click: Timeout 30000ms exceeded. |
| run_tests_phase374 | ok | 254 | 0 | 266 |  |
| run_tests_phase375 | ok | 135 | 0 | 173 |  |
| run_tests_phaseMS1 | fail | 0 | 0 | 8 | TypeError: unsupported operand type(s) for -: 'NoneType' and 'NoneType' |
| run_tests_phase_cg1 | fail | 45 | 1 | 53 | FAIL - [chromium/390] ทุก guide toast ไม่เกิน 3 บรรทัดที่มองเห็น  :: {"scanNew": 3, "ask": 3, "match": 3, "pic |
| run_tests_phase_ht1 | fail | 39 | 2 | 53 | FAIL - [to-do 1440] all 7 stock chips show, no +N :: [['AMZN', 'MU', 'NVDA', 'AVGO'], '+3 ›'] |
| run_tests_phase_sw2 | ok | 33 | 0 | 24 |  |
| run_tests_re1b | ok | 19 | 0 | 9 |  |
| run_tests_re1c2 | ok | 155 | 0 | 91 |  |
| run_tests_re1c | ok | 203 | 0 | 172 |  |
| run_tests_re1d | ok | 336 | 0 | 190 |  |

## Done so far
- **§4** (commit 1aaf1af): Compounder heat uses the week-snapshot FX (existing usage); `tests/re1c_live_test.js` 88/88 (7 new heat/FX checks that fail on the old adapter), `risk_engine_test` 313/313, `re1_adapter_test` 63/63, sync tool OK.
- **§2** (commit 6fd8737): old hidden Settings cards removed (markup + read sites). New `tests/run_tests_ts1.py` 26/0 (both accounts, 1440 + 390): no-edit Save leaves the stored settings deep-equal; Settings screenshots byte-identical before/after (closed and fully expanded).
- **§1** (done, commit below): shared causes first — `tests/net_stub.py` (no real network; fixed `run_tests` 403 console check), obsolete `backup-pre` / `_bk_` static checks removed, two broken suite files repaired (`# comment` swallowed the closing `)`), `ui_audit` writes `ui-audit-latest.md`. Re-run of the 130 failing suites after those fixes: 126 still failing, 4 fixed (`run_tests`, 19, 20, 363).
  - Dispositions: 26 suites stay and pass · 7 stay and FAIL (kept visible: real findings, see summary) · 2 empty suites (62, 88: every check already retired inside) moved · 119 retired to `tests/_retired/` with reason (README) · 40 of those are still imported as helpers by current suites → `tests/lib_phase*.py` · 1 check-level retirement set in `tests/ts1_retire.py` (phase35 `#satHeatHint`, TS1 §2).
  - `tests/run_regression.sh` (+ `--quick`): first full run 963 s (16 min).
  - Real app finding (not fixed, outside TS1 scope): at 390 px on the Port tab the header `＋` button (`#hdrPlanBtn`) is covered by the account-compare label (`.hdrCmp`, x 196–230 vs button 208–248) — introduced by AW1 (pre-AW1 c4bc75b: button at x=196, clickable). Fails `run_tests_phase373` (419 pass / 1 fail).
- **§3** (done): dead code removed from `index.html` (180 function definitions, 398 CSS rules + 33 selectors, 15 element ids) — lists in `docs/reports/TS1-removed.md`. Proof: 26 screens byte-identical before/after (1440 + 390); regression before/after identical (34/41 ok, same 7 failing). Tracked `*.backup-pre-*` files in tests deleted.
- **§3b** (done, commit 84fe312): 235 old briefs/reports/mockups/logs and 355 old screenshots deleted (list: `docs/reports/TS1-deleted-files.md`, added in the next commit — folding it into 84fe312 would need a force-push); 17 files kept because a script / test / index.html / kept doc still reads or links them.
