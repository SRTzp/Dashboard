# PF1 — เคสเก่าที่ถูกถอด/เปลี่ยน (B8)

รูปแบบ: suite · เคส · ความคาดหวังเดิม · เหตุผล · ตัวแทน

| suite | เคส (ชื่อเดิม) | เหตุผล | ตัวแทน |
|---|---|---|---|
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] ช่องที่ยังไม่มีข้อมูลเลย: ไอคอน '?' + 'ยังไม่ประเมิน' + ไม่มีปุ่ม [+ แผน] | ป้าย 'ยังไม่ประเมิน' / '+ แผน' ตาม Bias ของ Strategy ถอดแล้ว (PF1 A1/A8: + แผน กดได้เสมอ) | phase98 |
| run_tests_phase5.py | {tag} ช่องที่ยังไม่ประเมิน: 'ยังไม่ประเมิน' + 0/2 | ป้ายประเมิน Bias ของ Strategy ถอดแล้ว | phase98 |
| run_tests_phase5.py | {tag} ตัวแก้: ป้ายช่องเป็น 'Trend Shift' ไม่มี 'ผิดเมื่อ' | ช่อง Trend Shift ใน Strategy ถอดแล้ว (PF1 A1) | phase98 |
| run_tests_phase4.py | [{BROWSER_ENGINE}/{label}/v3on] คลิก tile จริง + คลิกปุ่ม Long จริง -> tile โชว์ 'Long · ขนาดไม้ เต็ม' + ปุ่ม [+ แผน] โผล่ (F2c: แทน x/2) | tile แสดง Long · ขนาดไม้ (Bias Strategy) ถอดแล้ว | เช็กใหม่ในตัวเอง |
| run_tests_phase5.py | {tag} ช่องพับ: 'Long · ขนาดไม้ เต็ม' และ 'Trend Shift <2,600' | ป้าย Bias/Trend Shift บนช่อง Strategy ถอดแล้ว | phase98 |
| run_tests_phase8.py | {tag} satV3NewPlan เหลือตัวเดียว (ลบ stub Phase 2) | satV3NewPlan ถอดจากแอป (ไม่มีผู้เรียก · อ่าน Bias Strategy) — เหลือเป็นตัวช่วยเทสใน mock-firebase.js | เช็กใหม่ในตัวเอง |
| run_tests_phase5.py | {tag} Bias: Long เมื่อ trend/macro ▲ ไม่ขึ้นเตือนสวนองค์ประกอบ | เตือน Bias สวนองค์ประกอบ/สวน Trend (satV3Warnings) ถอดแล้ว (PF1 A8) | phase98 |
| run_tests_phase11.py | {tag} tile: 'Long · ขนาดไม้ เต็ม' (Macro ▲ + Trend ▲) ไม่มี 'x/2' | ป้าย Bias/ขนาดไม้ บน tile Strategy และแถว Trend (Strategy จ.) ในการ์ดแผน ถอดแล้ว (PF1 A1/A8) — กฎขนาดไม้ตาม Macro ยังอยู่ (phase98/phase27) | phase98 |
| run_tests_phase11.py | {tag} tile: 'Long · ลด 40%' เมื่อ Macro ▼ + Trend ▼ (สวนทั้งคู่) | ป้าย Bias/ขนาดไม้ บน tile Strategy และแถว Trend (Strategy จ.) ในการ์ดแผน ถอดแล้ว (PF1 A1/A8) — กฎขนาดไม้ตาม Macro ยังอยู่ (phase98/phase27) | phase98 |
| run_tests_phase11.py | {tag} tile: Short + Macro ▼ + Trend ▼ (ตามทั้งคู่) = 'Short · ขนาดไม้ เต็ม' | ป้าย Bias/ขนาดไม้ บน tile Strategy และแถว Trend (Strategy จ.) ในการ์ดแผน ถอดแล้ว (PF1 A1/A8) — กฎขนาดไม้ตาม Macro ยังอยู่ (phase98/phase27) | phase98 |
| run_tests_phase11.py | {tag} การ์ด: 'Trend ▼ (Strategy จ.)' + [เปลี่ยน] | ป้าย Bias/ขนาดไม้ บน tile Strategy และแถว Trend (Strategy จ.) ในการ์ดแผน ถอดแล้ว (PF1 A1/A8) — กฎขนาดไม้ตาม Macro ยังอยู่ (phase98/phase27) | phase98 |
| run_tests_phase11.py | {tag} Trend Shift: Long และ Entry 4600 < 4650 → เตือนส้ม + เปิด [ขึ้น][ผสม][ลง] ทันที | เตือนราคาผ่าน Trend Shift ของ Strategy + ตัวเปลี่ยน Trend ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase11.py | {tag} Trend Shift: ข้อความ 'ราคาผ่าน Trend Shift — Trend อาจเปลี่ยนแล้ว · ราคาปิดรายวัน… · แค่ Sweep แล้วกลับ → Trend เดิม ไม่ต้องทำอะไร' | เตือนราคาผ่าน Trend Shift ของ Strategy + ตัวเปลี่ยน Trend ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase11.py | {tag} Trend Shift: Short และ Entry 4700 > 4650 → เตือน + เปิดปุ่ม | เตือนราคาผ่าน Trend Shift ของ Strategy + ตัวเปลี่ยน Trend ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase14.py | {tag} Future: ข้อความ tile (ไอคอน/ชื่อ/ป้าย/+ แผน/รับ-ต้าน-Trend Shift) เท่าเดิม (VW1: ไม่นับแถบ ＋ วางลิงก์กราฟ ที่เพิ่มใหม่) | snapshot ข้อความ/ตัวเลข/ฟอร์มตัวแก้ของ Strategy เทียบก่อนหน้า — Bias/ป้าย/Trend Shift/ปุ่ม Bias ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase14.py | {tag} Future: ตัวเลข tile ทุกใบ (badge/sub/เหตุผล) + ค่าแถบ Sat ต่อบัญชี (ถัง·heat·ไม้ใหม่·RPT·ไม้ Sat) ก่อน-หลังเท่ากัน | snapshot ข้อความ/ตัวเลข/ฟอร์มตัวแก้ของ Strategy เทียบก่อนหน้า — Bias/ป้าย/Trend Shift/ปุ่ม Bias ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase14.py | {tag} Future: ฟอร์มตัวแก้ Strategy ข้างในไม่เปลี่ยน (innerHTML เท่าเดิม · ยกเว้นปุ่ม Neutral ที่เพิ่ม PV2b) | snapshot ข้อความ/ตัวเลข/ฟอร์มตัวแก้ของ Strategy เทียบก่อนหน้า — Bias/ป้าย/Trend Shift/ปุ่ม Bias ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase14.py | {tag} Future: ตัวแก้ = ฟอร์มเดิมครบ (ปุ่ม Long/Short/Neutral(PV2b)/งดเทรด · Trend Shift · แนวรับ/ต้าน) | ปุ่ม Bias 4 ปุ่ม + ช่อง Trend Shift ในตัวแก้ Strategy (legacy) ถอดแล้ว (PF1 B6) | เช็กใหม่ในตัวเอง |
| run_tests_phase15.py | {tag} tile: มี 3 tile ที่เลือก (XAUUSD/BTCUSD/S50 · สินค้าทั้งหมด 4) · ทุกใบ role=button tabindex=0 cursor:pointer (รวมใบงดเทรดที่จาง) | ใบงดเทรดที่จาง (ui-dim) ถอดแล้ว (PF1 B4) | เช็กใหม่ในตัวเอง |
| run_tests_phase27.py | {tag} 6 Trend Shift tag ยังเป็นของแผน (Short: '>2,600') | ป้าย Trend Shift ของ Strategy บนการ์ดแผน ถอดแล้ว (PF1 A1) | phase98 |
| run_tests_phase27.py | {tag} 9 field F2c เดิมบันทึกตามปกติ (side = Long): macro_state=against · size_rule=0.6 · off_rule=false · trend_state=down | trend_state มาจาก Trend ของ Strategy — ไม่อ่านแล้ว บันทึกเป็น null (PF1 A8) | เช็กใหม่ในตัวเอง |
| run_tests_phase54.py | {tag} 5 Today: เช็ก Bias แสดงชื่อ XAU | งาน Today 'Bias ยังไม่ประเมิน' ถอดแล้ว (PF1 A8) | phase98 |
| run_tests_phase55.py | {tag} 1 Today เตือน Bias: 'XAU · BTC · S50' ที่เลือก (Brent ไม่ได้เลือก = ไม่เตือน · ชื่อ XAU ใน Today) | งาน Today 'Bias ยังไม่ประเมิน' ถอดแล้ว (PF1 A8) | phase98 |
| run_tests_phase55.py | {tag} 5 Today: ยังไม่ตั้ง Bias Silver → อยู่ในรายการเตือนเหมือนสินค้าเดิม | งาน Today 'Bias ยังไม่ประเมิน' ถอดแล้ว (PF1 A8) | phase98 |
| run_tests_phase69.py | {tag} 8 Today Bias: ยังไม่ประเมิน 2 ตัวที่เลือก (XAU · Brent) · ไม่มี BTC / S50 | งาน Today 'Bias ยังไม่ประเมิน' ถอดแล้ว (PF1 A8) | phase98 |
| run_tests_phase56.py | {tag} 1 Today ส่วนเดิม ([data-td-wrap]) ข้อความเหมือนก่อน GL1 ทุกตัวอักษร (ยกเว้นแถวการบ้านที่ GL3 เปลี่ยนตาม brief · f→FF ของ UX2 · แถวเช็กแผน Sat/Bias ที่ WA1fix นับเฉพาะ Asset ที่เลือก ไฟล์เก่าแสดง | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 1 ปุ่ม Weekly เป็น 'Weekly · 0%' ที่ไม่มีเป้า · แต่ละข้อ Bias auto เส้นประ กดไม่ได้ / Journal กดเองได้ | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 8 Bias ครบ 3/3 ที่เลือก (Long/Short/None นับ) → ✓ อัตโนมัติ (เส้นประ กดไม่ได้) | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 8 ก่อนติ๊ก Journal รวม '1/4 · 25%' (มีแค่ Bias ครบ) | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 8 ปิดงาน auto (on:false) → ตัวหารลดเหลือ 3 · ไม่นับ Bias | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 8 แถว Weekly: ช่องติ๊ก · ชื่อ · ขวา n/N หรือ 'กดเอง' ครบ | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 9 งานรายสัปดาห์เริ่มต้น 4 ข้อ · ปุ่มลบมีเฉพาะงานที่ติ๊กเอง (Journal) · งาน auto ลบไม่ได้ | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 9 บันทึก: dailyExtra 2 ข้อ (ชื่อเปลี่ยนได้) · weekTasks เก็บชื่อใหม่ + on:false + งานที่เพิ่มเอง auto:null | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase56.py | {tag} 1 Weekly ใช้ชุดเริ่มต้น 4 ข้อ · ข้อ 2 (กรอกค่าพอร์ต) ซ่อนเพราะไม่มีบัญชีตั้งเป้า → เหลือ 3 แถว | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' (auto จาก Bias Strategy) เปลี่ยนเป็น 'ทำแผน Sat สัปดาห์นี้' กดเอง (PF1 A8) — ตัวเลข/ลำดับงาน weekly เปลี่ยนตาม | phase98 |
| run_tests_phase59.py | {tag} 3 ข้อความ 3 ช่อง (ที่เลือก) Strategy เท่ากับไฟล์ก่อน VW1 ทุกตัวอักษร | เทียบข้อความ/ความสูง tile Strategy (legacy) กับไฟล์ก่อน VW1 — ป้าย Bias/ขนาดไม้/Trend Shift/ลูกศรบนหัว tile ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase59.py | {tag} 3 ช่อง XAU ไม่มีกราฟสูงเท่าก่อน VW1 + แถบ ＋ วางลิงก์ (40px + ระยะ ≤ 52) · ส่วนที่เกินจากขึ้นบรรทัดใหม่ ≤ 1 บรรทัด (line-height จริง {lh:.1f}px) | เทียบข้อความ/ความสูง tile Strategy (legacy) กับไฟล์ก่อน VW1 — ป้าย Bias/ขนาดไม้/Trend Shift/ลูกศรบนหัว tile ถอดแล้ว (PF1 A1/A8) | phase98 |
| run_tests_phase59.py | {tag} 3 ส่วนอื่นของการ์ด (Bias · แนวรับ/ต้าน · Trend Shift · จุด) ข้อความเหมือนเดิมทุกช่อง | เทียบข้อความ/ความสูง tile Strategy (legacy) กับไฟล์ก่อน VW1 — ป้าย Bias/ขนาดไม้/Trend Shift/ลูกศรบนหัว tile ถอดแล้ว (PF1 A1/A8) | phase98 |

## เคสที่ใช้ `retired(...)` / `lr.py` แก้ตรง ๆ (ไม่ผ่าน retire_tool) — สรุปตาม suite

| suite | สิ่งที่เปลี่ยน | เหตุผล |
|---|---|---|
| phase4 | คลิกปุ่ม Bias → seed ด้วย `satV3SetBias` (ตัวช่วยเทสใน mock-firebase.js) · เช็กใหม่: ตัวแก้ legacy ไม่มีปุ่ม Bias/Trend Shift | A1/B6 |
| phase5 | `set_bias_dom` seed ด้วยตัวช่วยเทส · ช่อง Trend Shift/เตือน satV3Warnings ถอด | A1/A8 |
| phase8 | `satV3NewPlan` ไม่อยู่ในแอป (เช็กกลับเป็น 0 ตัว) | PF1 ถอดฟังก์ชันที่ไม่มีผู้เรียก |
| phase11 | ตัวเปลี่ยน Trend ต่อแผน (trend_override) 6 เคส + เตือน Trend Shift 3 เคส → retired · trend_state/trend_changed = null · บรรทัดไม้ `Trend —` | A8 |
| phase14 | snapshot tile/ตัวแก้ เทียบก่อนหน้า 3 · pill Bias/งดเทรด 2 → retired + เช็กใหม่ (ไม่มี pill) · ปุ่ม + แผน top ≤ 16 | A1/A8 |
| phase15 | tile 3 ใบ: ไม่มีใบ `ui-dim` (งดเทรด) | B4 |
| phase27 | ป้าย Trend Shift บนการ์ด · trend_state=down → null | A1/A8 |
| phase34 | SR1 'สวน Bias สัปดาห์' ทั้งบล็อก 11: กลับเป็น "ไม่บล็อก/ไม่มีข้อความ" | A8 |
| phase36/37 | ปุ่มเติมไม้ไม่ถูกบล็อกด้วยสวน Bias | A8 |
| phase38/39 | Today ไม่มีงาน `bias` (ลำดับ/จำนวน/แถว) | A8 |
| phase54/55/69 | Today เช็ก Bias | A8 |
| phase56 | งาน Weekly 'ตั้ง Bias สัปดาห์ Sat ครบ' → 'ทำแผน Sat สัปดาห์นี้' กดเอง (ตัวเลข n/N เปลี่ยน) | A8 |
| phase59 | เทียบ tile กับไฟล์ก่อน VW1 (3 เคส) | A1 |
| phase60/63 | 'สวน Bias' → ไม่บล็อก | A8 |
| phase71 | แถบยกมา: ไม่มี 'เช็ก Bias ใหม่' · ปุ่ม ใช้ต่อ ไม่ต้องทำ Bias | A8 |
| phase75 | เปลี่ยนค่าที่เฝ้าดูจาก bias เป็น support (tile ไม่แสดง Bias แล้ว) | A1 |
| phase77 | TF Tactical 30m → 4H · แผนใหม่ bias ว่าง · helper `idea()` ตั้ง Trend + TP 2R ให้ (A3/A4) | A3/A4 |
| phase78 | Hedge/Range/Neutral/สวน Bias ตาม Strategy → Hedge จาก Main vs Trend ของแผน · Range ถอด (14 retired) | A5/A8 |
| phase79/80/81/82 | Trend/Flat/Zone/Shift/Idea/Setup ชิปเดิม/ประวัติสลับ ในฟอร์ม+tile → retired (ตรวจใหม่ใน phase98) · สถานะ `▲ Up` | A1/A2/A3/A8 |
| phase90/92/93/95/96 | ลูกศร/งด/ยังไม่ตั้ง บนปุ่ม Asset · Zone/B&P/Trend ใน tile · ＋ Asset/สัปดาห์ใหม่ล้างเฉพาะความเห็น (hint `ถือ n ไม้`/`—`) | A1/A8/B4 |

ตัวช่วยเทสที่เพิ่ม (ไม่ใช่โค้ดแอป): `tests/mock-firebase.js` ท้ายไฟล์ — `satwSetBias` · `satwSetInvalidation` · `satV3SetBias` · `satV3NewPlan` (เขียนข้อมูล Strategy เก่า/สร้างไอเดีย v1 สำหรับเทสที่ต้อง seed) · `tests/pf1_retire.py`
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] Bias=งดเทรด: badge แสดง 'งดเทรด' ในช่อง BRENT ไม่มีปุ่ม [+ แผน] สำหรับ BRENT | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] Bias=งดเทรด: tile จาง (class ui-dim อยู่บน .ui-tile ของ BRENT) | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] คัดลอกจากสัปดาห์ก่อน (S50): comps/invalidation/inv_note ถูกคัดลอกมา แต่ Bias ไม่ถูกคัดลอก | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] หลังตั้ง Bias=Long: tile โชว์ 'Long · ขนาดไม้ เต็ม' และปุ่ม [+ แผน] ปรากฏ | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] เตือน 'Bias สวนองค์ประกอบ' เมื่อ Long แต่ down มากกว่า up | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] เตือน 'ยังไม่มี Trend Shift' เมื่อยังไม่ตั้ง invalidation (7D.4: เปลี่ยนชื่อจาก 'จุดผิด') | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] เตือน 'สวน Trend' เมื่อ Long แต่ Trend factor = down | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |
| run_tests_phase2.py | [{BROWSER_ENGINE}/{label}] เลือก Bias=Long แล้ว satV3Sel พับเอง (เป็น null) | Bias/ขนาดไม้/เตือน Bias/Trend Shift/งดเทรด ในตัวแก้และ tile Strategy (legacy) + คัดลอก invalidation จากสัปดาห์ก่อน ถอดแล้ว (PF1 A1/A8/B4) | phase98 |

## PF3 — คืนเป็น assertion จริง (ไม่มีผู้เรียก `pf1_retire.retired()` แล้ว)

แต่ละข้อด้านบนที่เคยพิมพ์ `RETIRED(PF1)` ถูกแทนด้วย `check(...)` ที่มีชื่อขึ้นต้น `PF3 …` ที่จุดเดิม: ถ้า UI/กฎถูก PF1 ถอด = เช็กว่า **หายจริง** (absent-check) และหน้าที่เหลือยังทำงาน · ถ้ามีของใหม่แทน = เช็กพฤติกรรม PF1 ใหม่ (new) · ไฟล์ `tests/pf1_retire.py` คงไว้ (ไม่ลบ)

| suite | ข้อเดิม (ที่เคย retired) | assertion ใหม่ |
|---|---|---|
| run_tests_phase2.py | ช่องที่ยังไม่มีข้อมูลเลย ('?' + ยังไม่ประเมิน + ไม่มี [+ แผน]) | new: ไม่มีป้าย ยังไม่ประเมิน/ui-dim · [+ แผน] ≥3 |
| run_tests_phase2.py | เลือก Bias=Long แล้ว satV3Sel พับเอง | new: ไม่ auto-fold (satV3Sel ยัง XAUUSD) |
| run_tests_phase2.py | หลังตั้ง Bias=Long tile 'Long · ขนาดไม้ เต็ม' + [+ แผน] | new: ไม่มี 'Long ·' / 'ขนาดไม้ เต็ม/ลด' · [+ แผน] ยังอยู่ |
| run_tests_phase2.py | เตือน 'Bias สวนองค์ประกอบ' | absent-check (สวนองค์ประกอบ) |
| run_tests_phase2.py | เตือน 'สวน Trend' | absent-check |
| run_tests_phase2.py | เตือน 'ยังไม่มี Trend Shift' | absent-check (Trend Shift/จุดผิด ไม่มีในตัวแก้) |
| run_tests_phase2.py | Bias=งดเทรด tile จาง (ui-dim) | new: tile BRENT ไม่จาง |
| run_tests_phase2.py | Bias=งดเทรด badge + ไม่มี [+ แผน] | new: ไม่มีป้ายงดเทรด · มี [+ แผน] |
| run_tests_phase2.py | คัดลอกจากสัปดาห์ก่อน (S50) comps/invalidation/inv_note | new: คัดลอก comps + opinion_txt · ไม่คัดลอก bias/invalidation/inv_note (seed เพิ่ม opinion_txt) |
| run_tests_phase4.py | คลิก tile จริง + คลิกปุ่ม Long → tile 'Long · ขนาดไม้ เต็ม' + [+ แผน] | absent-check: ไม่มี 'Long · ขนาดไม้' / x/2 / ui-tile-b (เช็ก [+ แผน] อยู่ในเช็กถัดไปเดิม) |
| run_tests_phase14.py | ตัวเลข tile ทุกใบ + แถบ Sat ต่อบัญชี ก่อน-หลังเท่ากัน | new: meta (ถัง·heat·ไม้ใหม่·RPT) เท่าไฟล์ก่อน UI1b ทุกค่า · badge ว่าง · sub = รับ/ต้านไม่มี Trend Shift |
| run_tests_phase14.py | ข้อความ tile (ไอคอน/ชื่อ/ป้าย/+ แผน/รับ-ต้าน-Trend Shift) เท่าเดิม | new: tile = ชื่อ+[+ แผน]+รับ/ต้าน ไม่มีไอคอนทิศ/Long-Short/ขนาดไม้/Trend Shift · S50 มี 'รอสัญญาณ' |
| run_tests_phase14.py | ฟอร์มตัวแก้ Strategy innerHTML เท่าเดิม | new: ตัวแก้ไม่มีปุ่ม Bias/Neutral/Trend Shift · มีแนวรับ/ต้าน + Macro + ความเห็น |
| run_tests_phase14.py | pill 'Long · ลด 40%' warn/dn/nt | absent-check: ไม่มีข้อความ pill เดิมบนทุก tile · ไม่มี .ui-pill/.ui-tile-b |
| run_tests_phase14.py | งดเทรด = ช่องจาง | absent-check: ทุก tile opacity=1 ไม่มี ui-dim |
| run_tests_phase14.py | ตัวแก้ฟอร์มเดิมครบ (Long/Short/Neutral/งดเทรด · Trend Shift · แนวรับ/ต้าน) | new: ตัวแก้มีบล็อก Macro อ่านอย่างเดียว + ช่องความเห็นของฉัน |
| run_tests_phase5.py | ช่องที่ยังไม่ประเมิน 'ยังไม่ประเมิน' + 0/2 | absent-check: ไม่มี 'ยังไม่ประเมิน'/ui-dim · [+ แผน] ≥3 |
| run_tests_phase5.py | ตัวแก้: ป้ายช่อง 'Trend Shift' ไม่มี 'ผิดเมื่อ' | absent-check: ตัวแก้ไม่มี Trend Shift/ผิดเมื่อ |
| run_tests_phase5.py | ช่องพับ 'Long · ขนาดไม้ เต็ม' + 'Trend Shift <2,600' | absent-check บน tile |
| run_tests_phase5.py | Bias Long เมื่อ trend/macro ▲ ไม่ขึ้นเตือนสวนองค์ประกอบ | absent-check: ตัวแก้ไม่มีเตือนสวนองค์ประกอบ/สวน Trend/ui-warn |
| run_tests_phase11.py | tile 'Long · ขนาดไม้ เต็ม' (Macro▲+Trend▲) ไม่มี x/2 | absent-check บน tile (ไม่มี Long/ขนาดไม้/x/2) |
| run_tests_phase11.py | tile 'Long · ลด 40%' | absent-check |
| run_tests_phase11.py | tile Short + Macro ▼ 'Short · ขนาดไม้ เต็ม' | absent-check |
| run_tests_phase11.py | การ์ด 'Trend ▼ (Strategy จ.)' + [เปลี่ยน] | absent-check: ไม่มีแถว trend / Strategy จ. / ปุ่มเปลี่ยน |
| run_tests_phase11.py | กด [เปลี่ยน] → [ขึ้น][ผสม][ลง] | absent-check: [data-trend]=0 ไม่มีปุ่ม ผสม |
| run_tests_phase11.py | [ขึ้น] เขียน trend_override | new: แผนไม่มี trend_override |
| run_tests_phase11.py | satWeek ไม่เปลี่ยน (Trend ▼) | new: comps.trend.v='down' ยังอยู่ (ไม่ถูกแตะ) |
| run_tests_phase11.py | 'Trend ▲ (เปลี่ยนจาก ▼)' + ยกเลิก override | absent-check: ไม่มี เปลี่ยนจาก/ยกเลิก override |
| run_tests_phase11.py | Trend ▲ → ขนาดไม้ไม่ตาม Trend · ลด 40% (สวน Macro) + สวิตช์ | new: ลด 40% (สวน Macro) + สวิตช์ 1 ปุ่ม (ตาม Macro อย่างเดียว) |
| run_tests_phase11.py | ยกเลิก override → trend_override=null | new: trend_override ว่าง |
| run_tests_phase11.py | Trend Shift Long 4600<4650 เตือน+เปิดปุ่ม | absent-check: ไม่มี [data-trend-shift] / ปุ่ม |
| run_tests_phase11.py | ข้อความ 'ราคาผ่าน Trend Shift…' | absent-check |
| run_tests_phase11.py | Trend Shift Short 4700>4650 เตือน+เปิดปุ่ม | absent-check |
| run_tests_phase8.py | satV3NewPlan เหลือตัวเดียว | absent-check: ไม่มี satV3NewPlan ในแอปเลย (แก้ในรอบนี้) |
| run_tests_phase15.py | 3 tile role=button tabindex=0 cursor:pointer (รวมใบงดเทรดที่จาง) | absent-check: ไม่มี .ui-dim · ทุก tile opacity=1 |
| run_tests_phase34.py | เรียก satV3SaveOffplanAccount/SaveSlot/SaveReady ตรง ๆ → ไม่สร้างไม้ (บล็อกสวน Bias) | new: ไม่บล็อกแล้ว — ทั้ง 2 บัญชีสร้างไม้ได้ (main 1→5 · fam 0→3) |
| run_tests_phase36.py | satPyrSave ตอนสวน Bias → ไม่สร้างไม้ | new: บันทึกสำเร็จ · สร้างไม้เติม 1 ไม้ (n0→n0+1) |
| run_tests_phase38.py | Bias 2 ตลาด: 'Bias ยังไม่ประเมิน: BTC · S50' | absent-check + ลำดับงาน 🟡 ครบ |
| run_tests_phase38.py | กดแถว Bias → แท็บแผน · Strategy | absent-check: ไม่มีแถว kind=bias |
| run_tests_phase39.py | ✕ Brent ไม่กระทบงานอื่น: แถว Bias ยังมี Brent | absent-check: ไม่มีแถว bias ใน kinds · ไม่ซ้ำ |
| run_tests_phase54.py | Today เช็ก Bias แสดงชื่อ XAU | absent-check (bias_row ว่าง) + แถวเช็กแผน Sat ยังแสดง XAU |
| run_tests_phase55.py | Today เตือน Bias 'XAU · BTC · S50' | absent-check + ชิป Sat = XAU/BTC/S50 |
| run_tests_phase55.py | ยังไม่ตั้ง Bias Silver → อยู่ในรายการเตือน | absent-check (ไม่มีแถว Bias · ไม่มี Silver) |
| run_tests_phase27.py | 6 Trend Shift tag ยังเป็นของแผน (Short '>2,600') | absent-check: การ์ดแผนไม่มี Trend Shift/2,600 · ทิศของแผนยัง Short |
| run_tests_phase27.py | 9 field F2c: trend_state=down | new: trend_state = null และ trend_changed = null (ไม่อ่าน Strategy) |
| run_tests_phase56.py | Weekly ชุดเริ่มต้น 4 ข้อ ซ่อนข้อ 2 → 3 แถว | new: ids = wbias · wjournal · wdaily |
| run_tests_phase56.py | ปุ่ม Weekly · 0% · Bias auto เส้นประ กดไม่ได้ / Journal กดเอง | new: wbias เป็นกดเอง (ไม่มี auto เส้นประ · มีช่องติ๊ก) · wdaily auto |
| run_tests_phase56.py | Today ส่วนเดิมเหมือนก่อน GL1 ทุกตัวอักษร | new: เทียบกับไฟล์ก่อน GL1 หลัง normalise 3 จุดที่ PF1 เปลี่ยนจริง (ชื่องาน Weekly · ต้องทำ 3→2 · Trading Plan US 2→1) |
| run_tests_phase56.py | Bias ครบ 3/3 → ✓ auto | new: wbias กดเอง (auto=false · done=false · ขวา 'กดเอง') |
| run_tests_phase56.py | ก่อนติ๊ก Journal รวม 1/4 · 25% | new: ก่อนติ๊ก = 0/4 · 0% |
| run_tests_phase56.py | แถว Weekly ช่องติ๊ก·ชื่อ·ขวา n/N หรือ กดเอง | new: 4 แถว · ติ๊กเฉพาะงานกดเอง · ขวา n/N ของ auto |
| run_tests_phase56.py | ปิดงาน auto → ตัวหารเหลือ 3 | new: ปิด wbias → N=3 (แก้บรรทัดเตรียมให้ปิดด้วย id) |
| run_tests_phase56.py | งานรายสัปดาห์เริ่มต้น ปุ่มลบมีเฉพาะงานกดเอง | new: ปุ่มลบแถว 0 (ทำแผน Sat) และ 2 (Journal) เท่านั้น |
| run_tests_phase56.py | บันทึก weekTasks ชื่อใหม่ + on:false + งานเพิ่มเอง auto:null | new: wt[0] ชื่อใหม่ auto=null · wt[3].on=false · wt[4] สรุปสัปดาห์ auto=null |
| run_tests_phase59.py | ส่วนอื่นของการ์ด (Bias · แนวรับ/ต้าน · Trend Shift · จุด) เหมือนเดิม | new: t1 == t0 หลังใส่กราฟ · ไม่มี Trend Shift/ขนาดไม้ |
| run_tests_phase59.py | ข้อความ 3 ช่องเท่าไฟล์ก่อน VW1 | new: XAU = ชื่อ+[+ แผน]+แนวรับ/ต้านชุดเดิมเท่าไฟล์เก่าทุกตัวอักษร · BTC/Silver = 'รับ — · ต้าน —' |
| run_tests_phase59.py | ช่อง XAU ไม่มีกราฟสูงเท่าก่อน VW1 + แถบ | new: สูงไม่เกินเดิม + แถบ (≤ 52 + line-height) · เกินจากขึ้นบรรทัดใหม่ ≤ 1 บรรทัด |
| run_tests_phase69.py | Today Bias: ยังไม่ประเมิน 2 ตัวที่เลือก | absent-check (ไม่มีแถว Bias) + ชิป Sat = XAU · Brent |
| run_tests_phase78.py | Bias Long · Tactical Short → บล็อก สวน Bias | new: tacType = accel · blocks = [] |
| run_tests_phase78.py | Bias Neutral: ปุ่ม Neutral · ป้าย · ปุ่ม + แผน | absent-check: ไม่มี [data-bias-neutral]/คำว่า Neutral |
| run_tests_phase78.py | Neutral + Main Long: ทิศเริ่มต้น = สวน Main | new: ทิศ Short มาจาก Trend ที่ผู้ใช้ตั้งในแผน · Main ยัง Long (+ เช็กแผนใหม่ไม่มีทิศเริ่มต้นท้าย block 3) |
| run_tests_phase78.py | Neutral + Main ▲ · Tactical ▲ → บล็อก รอ Bias เปลี่ยน | absent-check: ไม่มีข้อความ รอ Bias/สวน Bias ใน blocks/warns |
| run_tests_phase78.py | Neutral ไม่มี Main → Range + เตือน 3× SL / ป้าย Range / ไม้ tac_type range | absent-check: tacType ≠ range · การ์ดไม่มี Range/กรอบควรกว้าง · tac_type ที่บันทึก ≠ range + แผนใหม่ไม่มีทิศเริ่มต้น |
| run_tests_phase79.py | แผนเดิม (bp) ยังมีแถว Trend + [เปลี่ยน] | absent-check |
| run_tests_phase79.py | กด [เปลี่ยน] → ขึ้น/ผสม/ลง | absent-check: [data-trend] = 0 |
| run_tests_phase80.py | 9 รายการ (Trend/Flat/งดเทรด/Neutral เก่า/Zone·Shift/ทิศค่าเริ่ม/สวน Trend SR1/Setup ชิปเดิม) | absent-check ต่อรายการบน tile Lean + new: แผนใหม่ Trend ว่าง · Short vs Bias เก่า Long ไม่ถูกบล็อก · ฟอร์มไม่มีชิปเดิม มี In the zone/Align MA50 |
| run_tests_phase81.py | 6 รายการ Flat ไม่นับสลับ/สลับ Up↔Down/ปุ่ม Neutral | absent-check: ไม่มีช่อง Flat/ปุ่ม Trend/กล่องเหตุผล · flips=0 · ไม่มี dialog · โหมดเดิมไม่มีปุ่ม Neutral |
| run_tests_phase82.py | 13 รายการ Zone ▲/▼ · Shift · สลับ Trend ต้องมีเหตุผล · ประวัติสลับ | absent-check ต่อรายการ (ไม่มี input/ปุ่ม/ฟังก์ชัน/trend_log) + ข้อมูลเก่า (support/resistance/invalidation) ไม่ถูกแตะ |
| run_tests_phase82.py | การ์ดสินทรัพย์: กราฟเต็ม + TradingView · Trend · Flat · Macro · ประวัติ · งดเทรด | absent-check: ไม่มี Flat/งดเทรด/ประวัติ · มีแถว Macro · ไม่มีรูป/ลิงก์ (WM1) |
| run_tests_phase82.py | 6 รายการ Zone จาก Strategy/ติ๊กอยู่ใน Zone/Idea | absent-check + new: Zone Activation ([data-pf-zact]) แทน · zone_ok/idea_txt ไม่ถูกเขียน |
| run_tests_phase82.py | Tactical: ไม่มี Idea · Zone กรอกเอง + ติ๊ก · zone_txt | absent-check + new: มี Zone Activation · zone_txt ไม่ถูกเขียน |
| run_tests_phase82.py | ลูกศรมีสี ▼ #ff7b6e ในปุ่ม Trend ที่เลือก | absent-check: ไม่มี [data-ln1-trend] · สีลูกศร Macro/Trend ของแผนยังอ่านได้ |
| run_tests_phase90.py | มือถือ: แถบปุ่ม Asset ลูกศรสี/งด | new: 3 ปุ่มชื่อล้วน + ＋ Asset |
| run_tests_phase90.py | ลูกศรมีสี ▲เขียว ▼แดง ในปุ่มที่ไม่ได้เลือก | absent-check: สีตัวอักษรปุ่มที่ไม่ได้เลือกเท่ากันหมด |
| run_tests_phase90.py | Asset ที่ยังไม่ตั้ง Trend = Brent ยังไม่ตั้ง จาง | new: ชิป Brent แสดงปกติ ไม่จาง ไม่มีป้าย |
| run_tests_phase93.py | 10 รายการ ประวัติสลับ · เหตุผลสลับ · Zone ▲/▼ · B&P · zone_side | absent-check ต่อรายการ (ไม่มี hist/zone/bp/ask · ฟังก์ชันเขียนถอด) |
| run_tests_phase93.py | 4 รายการ Trend ว่าง: ไม่มีปุ่ม · แถบเหลือง · + แผนกดไม่ได้ · trend_log · ถามเหตุผล | new: ไม่มีปุ่ม/แถบเหลือง · + แผนกดได้ · ไม่มี trend_log/กล่องถาม |
| run_tests_phase96.py | 5 รายการ ＋ Asset รีเซ็ต Trend/Zone/Shift/B&P/ประวัติ | new: UI ไม่มีของเดิม · DB เก็บของเก่า (trend_log 2 · zone_up · invalidation) · รีเซ็ตเฉพาะ opinion_txt |
