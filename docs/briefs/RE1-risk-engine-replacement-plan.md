# RE1 — แผนแทนระบบ Portfolio Risk & Position Sizing เดิมทั้งหมด

วันที่: 13 พฤศจิกายน 2026
สถานะ: ผู้ใช้ยืนยันคำแนะนำทั้ง 6 ข้อ (รวม 2A/2B) วันที่ 15 พฤศจิกายน 2026 — สรุปแผนงานเท่านั้น ยังไม่ใช่คำสั่งพัฒนา
อ้างอิง: Technical Specification ที่ผู้ใช้แนบ + โค้ด Dashboard ใน workspace ปัจจุบัน

อัปเดตตรวจเทียบ: 14 พฤศจิกายน 2026 — อ่าน Handoff 2026-11-12 ที่ผู้ใช้แนบแล้ว พร้อม `PB1b-brief.md` rev 3.1, `PB1c-brief.md`, `PB1d-brief.md` และ `WL1-brief.md` ใน docs/briefs

ลำดับแหล่งอ้างอิง: สเปก Risk ใหม่และข้อความแก้ไขของผู้ใช้กำหนด RPT/Step/loss limits; handoff และ PB1b/WL1 กำหนด entry conditions และ workflow ที่ตกลงไว้แล้ว ข้อสรุปล่าสุดวันที่ 14 พฤศจิกายนให้เก็บ Starter ¼ / training toggle เพราะเปิด–ปิดได้ใน Settings แทนข้อเสนอให้ตัดก่อนหน้า; ส่วนข้อเสนอเพิ่มเติมใน RE1 ไม่ลบกฎอื่นเหล่านั้นโดยอัตโนมัติ หากขัดกันให้แสดง conflict ก่อนพัฒนา

Handoff เป็นสถานะ ณ 12 พฤศจิกายน ไม่ใช่การยืนยันสถานะ merge ปัจจุบัน และคำสั่ง CC/merge ภายในเป็นข้อมูลส่งต่อ ไม่ใช่ขอบเขตงานรอบนี้ ซึ่งยังเป็นแผนงานเท่านั้น

## 1. เป้าหมายและขอบเขต

ให้ Dashboard ใช้ Risk Engine ใหม่เพียงชุดเดียวสำหรับ Momentum / Satellite / Compounder ตามสรุปที่แนบมา โดยแทนสูตร RPT/Step/loss budgets และเส้นทางคำนวณเก่าที่ถูก supersede ทั้งหมด ส่วน Trend/MSS, Homework cap และ workflow ที่ handoff ระบุให้คงไว้ ต้องเชื่อมเข้า engine กลาง ไม่ลบเพียงเพราะเป็นกฎเดิม

- ใช้หน้าปัจจุบัน: Today → Flow → Watch → Plan → Journal → Port และ Settings
- ใช้ Plan board เดิม: Planned / Ordered / Holding พร้อม drawer และฟอร์มเดิมที่ปรับเนื้อหา
- ไม่สร้าง Calculator หรือ Dashboard อีกชุดแยกจาก workflow ซื้อขายจริง
- เก็บประวัติเทรด ราคาเข้า จำนวนหุ้น/สัญญา SL การปิดบางส่วน และสถานะออเดอร์จริง
- “ลบของเก่า” หมายถึงระบบ Risk/Sizing และพฤติกรรมที่ถูกแทน ไม่ใช่ลบ Journal หรือข้อมูลพอร์ต
- งานรอบนี้ส่งเฉพาะแผน; การลงมือพัฒนาเป็นงานถัดไป

## 2. สิ่งที่ตรวจพบใน Dashboard

| ส่วนปัจจุบัน | สิ่งที่ต้องเปลี่ยน |
|---|---|
| Strategy keys: `winner`, `ladder`, `sat` | ใช้ keys เดิมได้ เพื่อไม่ต้องเปลี่ยนความสัมพันธ์ข้อมูล; แสดง MMT / COMP / SAT |
| `ps1-size.js` และสำเนาที่ฝังใน `index.html` | แทนกฎ PS1 ด้วย engine ใหม่ และมีแหล่งสูตรหลักเพียงแห่งเดียว |
| `core-size.js` และเส้นทาง Core/Ladder เดิม | ตรวจผู้เรียก แล้วลบส่วน sizing, ladder, risk gate ที่ถูกแทน; เก็บเฉพาะ utility ที่ยังจำเป็น |
| PS1 cap: COMP 3%, MMT 1.5%, SAT 0.5%, รวม 5% | ยกเลิก ไม่คงเป็นเพดานแอบซ้อนกฎใหม่ |
| Risk default แบบช่วงและช่องแก้ Risk ในฟอร์ม | เปลี่ยนเป็น RPT ตาม Strategy/Step ที่ระบบกำหนด |
| Satellite Main/Tactical, RPT แยก sleeve, pyramid | ยกเลิกการแบ่งกฎ sizing สองชุดสำหรับระบบใหม่ |
| `lossEval`, `lossSync`, `Ps1.lossStep/lossUnits` | แทนวงจร DD และ daily/weekly loss เดิมด้วย event/state ใหม่ |
| Regime/Macro/DD multipliers, Starter ¼, Unclear Trend เดิม 60% | แทน legacy multipliers ด้วย policy ใหม่; SAT คง Trend/MSS factor 1.0/0.65 เพียงครั้งเดียว; คง Homework cap ตาม WL1; เก็บ Starter ¼ และ training toggle เดิม ใช้เฉพาะเมื่อเปิดใน Settings; เมื่อปิดไม่มีการลดขนาดจาก training |
| Min-stop sizing ของ MS1 และ position-size cap ของ PS1 | PS1 position-size cap เดิมอยู่ในกลุ่มแทนที่; คง min-stop สำหรับ sizing ตามข้อสรุปล่าสุด ใช้ SL จริงวัด risk/ผลเทรด; คง Homework cap ของ WL1 |
| `ps1E()` อ่าน `poolsOf().total` | ปัจจุบันเป็นผลรวม capital ที่ตั้งไว้ ไม่ใช่หลักฐานว่าเป็น mark-to-market equity; ต้องทำฐาน Equity ให้ชัดก่อนใช้กฎใหม่ |
| `ps1Used()` นับ planned Core บางส่วนเป็น risk | เปลี่ยนเป็น Draft ไม่จองงบ, Ordered จองงบ, Holding ใช้ความเสี่ยงจริง |

ค่าข้างต้นเป็น defaults/logic ที่พบในโค้ด ไม่ใช่การยืนยัน Settings หรือยอดเงินสดในบัญชีจริงของผู้ใช้

## 3. กฎใหม่ที่เป็นแกนหลัก

| Strategy | RPT ปกติ | Weekly loss cap | Monthly loss cap | เงื่อนไขเพิ่ม |
|---|---:|---:|---:|---|
| Momentum | คงที่ 0.45% ต่อ full idea | 1.80% | 7.20% | Thesis ยังไม่เสร็จเริ่ม 50%; เติมได้หลัง thesis เสร็จ; SL ครึ่งไม้ก็นับเสีย 1 กระสุน; ขาดทุนครบ 4 ideas ในสัปดาห์หยุด |
| Satellite | 0.20 → 0.30 → 0.30 → 0.40% | 1.20% | 4.80% | Base step × Condition 1.0/0.65; ชนะและ weekly net ≥ 0 จึงกลับ Step 1; แพ้ขยับ step; 1 setup/product/day + re-entry ได้อีก 1 ครั้งเมื่อโดน SL จากราคาสะบัดและ setup เดิมยังใช้ได้ |
| Compounder | Pilot 0.50% + Add-on 0.50% | ไม่มี reset heat | ไม่มี active loss cap | Rolling heat ≤ 6%; แพ้ติดกัน 6 ticker-cycles หยุดเปิดเพิ่ม |

- Active = Momentum + Satellite: weekly 3%, monthly 12%; Compounder แยกจากงบนี้
- ตรวจ monthly limits จริงทุกครั้งก่อนเพิ่มความเสี่ยง ไม่ใช่แสดงตัวเลขอย่างเดียว
- Emergency: เดือนที่ DD แตะ −10% ทำให้เดือนถัดไปใช้ RPT ×0.5 ทุก Strategy; ใช้ฐานต้นเดือนที่เกิด trigger ปรับ cash flow และคงฐานนั้นจน recovery > −5%; COMP ใช้ min(regimeFactor, emergencyFactor) ไม่คูณลดซ้อน
- เมื่อ strategy ถูกล็อก ยังต้องแก้ SL ลดสถานะ ยกเลิกออเดอร์ และบันทึกการปิดได้
- คง entry gates ตาม PB1b/handoff: Trend/MSS, TP บังคับ, R:R ≥ 1.5, ราคาถูกฝั่ง และ Place-order setup confirm; Macro เป็นข้อมูลประกอบ ไม่มีตัวคูณเก่าแอบซ้อน

## 4. ทำ Logic ให้ครบก่อนเริ่มเขียน

### Equity และรอบเวลา

- ยืนยันให้คำนวณแยก Main/Family ต่อบัญชีตามโครงสร้างเดิม; หน้า All accounts รวมเพื่อรายงาน ไม่ย้ายงบระหว่างบัญชี
- แยก `currentEquity`, `weekStartEquity`, `monthStartEquity` พร้อม timestamp และแหล่งข้อมูล
- Week/month cap แปลงเป็นเงินจาก snapshot ต้นรอบ; รวมเงินก่อนแปลงเป็น % เพื่อไม่ปน denominator
- ยืนยัน sizing และ weekly budget ใช้ weekStartEquity; monthly budget ใช้ monthStartEquity; rolling heat/open risk รายงานจากสถานะจริงเทียบ currentEquity ซึ่งรวม unrealized P&L ไม่ใช่เพียง capital ที่กรอกไว้
- ยืนยัน reset เขต Asia/Bangkok: daily quota 00:00 ทุกวัน, weekly counters/Step จันทร์ 00:00, monthly counters วันที่ 1 เวลา 00:00; ไม่อิง timezone ของเครื่อง
- ถ้าแอปไม่ได้เปิดตอนต้นรอบ ห้ามนำยอดวันนี้ไปอ้างว่าเป็นยอดต้นรอบ; ต้องมี snapshot ย้อนหลังที่เชื่อถือได้หรือให้ผู้ใช้ระบุ
- Cash deposit/withdrawal ต้องบันทึกแยก เพื่อไม่ทำให้ drawdown ดูเหมือนกำไรหรือขาดทุน

### Risk และขนาดไม้

```text
eligibility = evaluateTrendAndMSS(ema50, structure, mss)  // SAT only
ถ้า SAT และ eligibility ไม่ผ่าน: ห้าม Place order (ยัง Save draft ได้)
conditionMultiplier = SAT ? eligibility.multiplier : 1.0
riskFactor = COMP ? min(regimeFactor, emergencyFactor) : emergencyFactor
effectiveRPT = baseRPT × conditionMultiplier × riskFactor
riskBudget = weekStartEquity × effectiveRPT / 100
actualDistance = abs(entry − stop)
sizingDistance = max(actualDistance, configuredMinStopDistance)
qtyBeforeWorkflowCaps = floorToLot(riskBudget / (sizingDistance × valuePerPriceUnit × FX))
qty = applyHomeworkAndEnabledTrainingCaps(qtyBeforeWorkflowCaps)
actualStopRisk = qty × actualDistance × valuePerPriceUnit × FX
```

- จำนวนหุ้น/สัญญาปัดลงตาม lot step; หากต่ำกว่า minimum lot ให้ขึ้น “งบไม่พอสำหรับขั้นต่ำ”
- หุ้นใช้ multiplier 1; Futures/CFD ใช้ instrument specification จริง ไม่เดา multiplier เมื่อข้อมูลขาด
- เงินและราคาในสูตรต้องอยู่ใน currency ที่สอดคล้องกัน; notional กับ margin แสดงแยกกัน
- SL ต้องถูกฝั่ง Long/Short; Entry=SL, Equity ไม่พร้อม, multiplier/FX ขาด ต้อง block การเปิดความเสี่ยง
- Open principal risk ใช้ SL ปัจจุบันและจำนวนที่เหลือ คิดราย tranche แล้วรวม; ห้ามกำไรที่ล็อกไว้ของไม้หนึ่งหักความเสี่ยงอีกไม้
- 1R / 1.5R / 2R ใช้ Entry และ initial SL ที่ freeze ณ fill; เลื่อน SL แล้วค่า R อ้างอิงไม่เปลี่ยน
- ถึง +1.5R เป็นเพียงการเตือน จนผู้ใช้ยืนยันว่าเลื่อน SL จริงจึงคืน risk budget
- การรับรู้ราคาขึ้นกับข้อมูลราคาที่ Dashboard มี แสดงเวลาอัปเดต ไม่อ้างว่าเป็นการเฝ้าราคาตลอดเวลา

### Loss และวงจรสถานะ

- ใช้ realized P&L จริงรวมค่าธรรมเนียมที่มีข้อมูล ไม่หัก 0.45% ทุกครั้งโดยสมมติว่าทุก loss เต็ม RPT
- Partial close รับรู้เงินทันที แต่นับ win/loss step หรือ losing idea เมื่อปิดครบทั้ง idea; ใช้ผลสุทธิของ idea
- Compounder นับหนึ่ง ticker-cycle ตั้งแต่เปิด Pilot จนปิดครบ; 6 losses ไม่ได้แปลว่าขาดทุนครบ 6% เสมอ
- เสนอ win reset consecutive losses เป็น 0 และ breakeven ไม่เพิ่ม/ไม่ reset; ใช้กติกานี้ใน replay และ tests เดียวกัน
- Satellite ใช้คิวร่วมทุก product ต่อบัญชีและมี active setup ครั้งละหนึ่ง; event replay ยังคงเรียงเวลาปิดและ event ID อย่างแน่นอนสำหรับข้อมูลเก่า/corrections ไม่เปิดทางให้วางหลาย setup ใหม่พร้อมกัน
- การแก้ประวัติย้อนหลังต้อง replay state ตามเหตุการณ์ ไม่เพิ่ม counter ซ้ำ

### ข้อสรุปเพิ่มเติม — 15 พฤศจิกายน 2026

- **Momentum ยืนยันแล้ว:** Open risk cap 1.80%; +1.5R เตือนเลื่อน SL; คืน risk เมื่อยืนยันเลื่อนจริงเท่านั้น ไม่คืน losing-trade allowance ที่เสียไปแล้ว
- **Satellite daily exception — ผู้ใช้ชี้แจงแล้ว:** หมายถึงโดน SL จากราคาสะบัด (stop-out/whipsaw) แล้ว setup เดิมยังใช้ได้ ไม่ใช่ execution slippage; อนุญาต re-entry บน product เดิมเพิ่มอีก 1 ครั้งในวันนั้น จึงมีได้สูงสุด 2 entry attempts ภายใต้ข้อยกเว้นนี้ ไม่ใช่ 2 setups อิสระ
- Re-entry เป็นข้อยกเว้นของ daily entry limit เท่านั้น ไม่ใช่ยกเว้นผลขาดทุน/Step: attempt แรกที่ปิดขาดทุนต้องรับรู้ loss และเลื่อนไป Step ถัดไปตามกฎเดิม; attempt ใหม่ใช้ Step และ Condition ปัจจุบัน ไม่ใช้ Step เดิมฟรี
- **ผู้ใช้ยืนยันให้ใช้ Step ถัดไปเต็มตาม policy ไม่ cap ตาม attempt แรก:** ข้อเสนอของอีกโมเดล/ผู้ช่วยเรื่อง min(current-step risk, original-attempt risk) ไม่ถูกเลือก เช่น Step 1 แพ้ → re-entry ใช้ Step 2 Base 0.30% × Condition ปัจจุบัน × Emergency factor; ไม่ได้บังคับให้ใช้ 100% หาก Condition เป็น 65%
- เจตนาของ progression: ช่วยให้กล้าเข้า attempt ถัดไปเมื่อ setup ยัง valid และเพิ่มจำนวนเงินที่อาจได้คืนหากชนะ ไม่ใช่รับประกันการคืนทุนหรือเพิ่ม probability of win; loss ต่อเนื่องย่อมเสียเงินมากขึ้นด้วย
- หากเริ่ม attempt แรกที่ Step 2 แล้วแพ้ re-entry ใช้ Step 3 ไม่ reset เป็น Step 2; ทุกครั้งยังต้องผ่าน budget และ eligibility ไม่เปิดเพียงเพราะต้องการคืนทุน
- แม้ผูก setup เดียวกัน แต่แต่ละ entry attempt มีรอบผลแพ้/ชนะของตนเอง; partial fills/exits ภายใน attempt เดียวไม่ทำให้ Step ขยับซ้ำ อย่ารวม attempt แรกกับ retry จนเลื่อนการรับรู้ loss/Step
- ตรวจ Trend/MSS, weekly/monthly/Active budgets และ strategy lock ก่อน re-entry; ถ้าแพ้ที่ Step 4 จน lock แล้ว สิทธิ re-entry ไม่ปลด lock
- ข้อเสนอวิธียืนยัน setup ยังใช้ได้ (ยังไม่ตกลงรายละเอียด UI/เกณฑ์): ผู้ใช้ยืนยันเหตุผลราคาสะบัดและ setup เดิมยัง valid พร้อมผูก originalAttemptId; ไม่ให้ระบบวินิจฉัยว่าเป็น whipsaw จากการโดน SL เพียงอย่างเดียว
- ยืนยัน Sat คิวร่วมทุก product ต่อบัญชี: มี active setup ได้ครั้งละหนึ่ง จองคิวตอน Ordered; ยกเลิกก่อน fill คืนคิวโดยไม่เลื่อน Step; partial close/BE ยังไม่ปล่อยคิวจนปิดครบ ส่วน product อื่นเก็บ Planned ได้
- **Weekly reset ยืนยันหลักการแล้ว:** คืน counters/Step ของสัปดาห์ โดย holdings/working risk ยังนับต่อ; monthly loss นับต่อถ้าเดือนเดิม; ใช้ Asia/Bangkok ตามรอบเวลาที่สรุปแล้ว
- **Compounder unlock ยืนยันแล้ว:** ใช้ ACWI/BIL + HYG/IEI ชุดช้าเดิม; หลังแพ้ 6 รอบต้องทั้งสองกลับเขียว ข้อมูลเป็นปัจจุบัน และผู้ใช้ยืนยันหลัง review จึงปลดล็อก ไม่เพิ่ม Benchmark > EMA40W อีกชุด
- ตรวจโค้ดพบ `ffPoolFactor('ladder')` ใช้ ACWI/BIL และ HYG/IEI โดยเลือก slow signal สำหรับ COMP; `Calc.ffCoreCap` ให้ 100%/75%/50% ตามจำนวนสัญญาณแดง และมีสถานะข้อมูลขาด/เก่า (ไม่ใช่การยืนยันว่ากฎนี้เหมาะที่สุด)
- ยืนยัน COMP Regime 100%/75%/50% ตามเดิม; เมื่อ Emergency ทำงานใช้ factor ที่เข้มกว่า = min(regimeFactor, emergencyFactor) เช่น 75% กับ 50% ใช้ 50% ไม่ใช่ 37.5%; แยก loss-streak lock ออกจาก sizing

### Momentum — Fixed risk, Thesis 50% และจำนวนกระสุน (ข้อสรุปผู้ใช้)

- ใช้ Base RPT เดิมเท่ากันทุก idea = 0.45%; ไม่เดินคิวเพิ่ม RPT แบบ Satellite คำว่า fixed size ในแผนนี้หมายถึงงบ risk ต่อ full idea ไม่ใช่จำนวนหุ้นหรือ notional เท่ากันเมื่อระยะ SL ต่างกัน
- ในโหมดปกติ (Starter training OFF): thesis ยังไม่เสร็จเริ่ม 50% ของ full size; ถ้าไม่มี Emergency factor งบ risk ก่อนปัด lot = 0.225% ของ sizing equity
- Thesis เสร็จก่อนเข้า → ใช้ full size ได้ภายใต้ caps; ถ้าเข้าครึ่งไม้ไปแล้ว → ต้องทำ thesis ให้เสร็จก่อนจึงเติมได้จนถึง full size รวมของที่ถือและออเดอร์ค้าง ไม่ใช่เพิ่มอีก 100%
- ใช้ definition การทำ homework/thesis ของ MMT เดิม: ④ Wrong if + trigger และ I've reviewed this; ไม่สร้าง checklist ใหม่
- การเติมครึ่งที่เหลือเป็นการเติมงบ idea เดิม ไม่ใช่ idea ใหม่หรือการได้ RPT ใหม่; ตรวจราคาเข้า/SL, actual risk รวม, cap และเงื่อนไขเติมที่ใช้อยู่ก่อนจองคำสั่ง ไม่ auto-fill เมื่อ thesis done
- ถ้าไม้ 50% ถูก SL ก่อนเติมจน idea ปิดขาดทุน ให้นับ `mom_weekly_loss_count += 1` เต็มหนึ่งกระสุน ไม่ใช่ 0.5 และไม่เก็บครึ่งที่ไม่ได้ใช้ไว้เป็นกระสุนฟรี
- แยกตัวนับสองชุด: loss count นับ idea ที่จบขาดทุน; realized loss รับรู้จำนวนเงินจริง ตัวอย่าง SL เต็มระยะของไม้ครึ่งขนาด = loss 0.225% แต่ใช้กระสุน 1 ไม้ (ก่อน fees/slippage และเมื่อฐาน Equity เดียวกัน)
- เติมแล้วปิดหลาย tranche ของ idea เดียวกัน ให้นับผลสุทธิเมื่อปิดครบเพียงครั้งเดียว; partial exits รับรู้เงินจริงทันทีตามกฎ event เดิม
- แพ้ครึ่งขนาด 4 ideas → weekly loss count = 4 จึง lock แม้ loss รวมเพียง 0.90%; ไม่ต้องรอให้เงินขาดทุนถึง 1.80% และการชนะไม่รีเซ็ต weekly loss count แบบ Satellite
- การคง Starter training toggle ตามข้อสรุปก่อนหน้ายังมีผล: ถ้าเปิดใช้ข้อจำกัด training เพิ่มตาม WL1; ไม่ตีความข้อความนี้ว่าเป็นการลบ toggle ส่วน Emergency factor ยังใช้ตาม policy
- UI แยก `Risk ที่เสียจริง` กับ `กระสุนที่เสีย x/4` และแสดง `Thesis ยังไม่เสร็จ · ขนาดสูงสุด 50%` เพื่อไม่ทำให้เงินที่ยังเหลือดูเหมือนเปิดได้เมื่อใช้ครบ 4 กระสุน

### Satellite — Condition multiplier และ Step (อัปเดตตามข้อความล่าสุด)

ผู้ใช้ยืนยันลดขนาดที่ 65% แทน 60% วันที่ 15 พฤศจิกายน 2026 ใช้กับทุก reduced-condition case ในตาราง PB1b; ไม่ใช่ 2/3 และไม่เปลี่ยน eligibility เดิม ค่านี้เป็น policy choice ไม่ใช่ optimal factor ที่พิสูจน์แล้ว

ยึดกฎสรุปท้ายข้อความล่าสุดของผู้ใช้: ชนะจะ reset ก็ต่อเมื่อ weekly realized net ≥ 0 ทั้งไม้ 100% และ 65%; ไม่ใช้ตัวเลือก “ชนะทุกครั้ง reset เสมอ” ในแผนนี้

| Step ที่แสดง | Index | Base RPT | Condition 100% | Condition 65% |
|---|---:|---:|---:|---:|
| 1 | 0 | 0.20% | 0.20% | 0.130% |
| 2 | 1 | 0.30% | 0.30% | 0.195% |
| 3 | 2 | 0.30% | 0.30% | 0.195% |
| 4 | 3 | 0.40% | 0.40% | 0.260% |

ตารางยังไม่รวม Emergency factor; หาก half-size ทำงาน เช่น Step 3 ×65% ×50% → effective RPT 0.0975%

```text
เมื่อปิด idea ครบ (รวม partial exits และค่าธรรมเนียม):
  update weekly realized net ด้วยเฉพาะเงินที่ยังไม่เคยรับรู้
  ถ้า ideaNetPnL < 0: stepIndex += 1
  ถ้า ideaNetPnL > 0 และ weeklyRealizedNet >= 0: stepIndex = 0
  ถ้า ideaNetPnL > 0 แต่ weeklyRealizedNet < 0: คง stepIndex
  ถ้า ideaNetPnL == 0: คง stepIndex
  ถ้า stepIndex > 3: lock จนรอบสัปดาห์ใหม่
```

- Condition เปลี่ยนได้แต่ละออเดอร์โดยไม่เปลี่ยน Step; การแพ้ที่ 65% ใช้หนึ่ง Step เท่ากับแพ้ที่ 100%
- คิวจึงนับ losses ตั้งแต่ reset ล่าสุด ไม่ใช่ total losses ทั้งสัปดาห์ และเมื่อชนะแล้วยังติดลบจะใช้ Step เดิมต่อได้
- ประเมิน Condition ตอน Place order แล้ว snapshot ค่า, เหตุผล และเวลา; เปลี่ยน Condition ทีหลังไม่ resize working order/holding อัตโนมัติ การแก้ออเดอร์ต้องตรวจและจองงบใหม่
- ค่า `is_full_condition` ต้องเป็น boolean ที่มีหลักฐาน; ไม่มีข้อมูลไม่ให้ตีความเป็น false/65% อัตโนมัติ
- แก้ mapping ที่ RE1 เคยย่อผิด โดยยึด PB1b rev 3.1 และ handoff ล่าสุด:

| EMA50 | Structure | MSS | ผล |
|---|---|---|---|
| ✓ | ✓ | ไม่ใช้ | 100% |
| ✗ | ✓ | ไม่ใช้ | 65% + เตือนออกที่เป้าหมายสำคัญใกล้สุด |
| ✓ | ✗ | Yes | Counter trend @ MSS · 65% |
| ✗ | ✗ | Yes | Reversal @ MSS · 65% + เตือนเป้าหมายใกล้สุด |
| ค่าใดก็ได้ | ✗ | No / ยังไม่ตอบ | Blocked |
| EMA50 หรือ Structure ยังไม่เลือก | — | — | Incomplete; ห้าม Place order |

- ใช้ eligibility ก่อน multiplier เสมอ: boolean `is_full_condition=false` อย่างเดียวไม่เพียงพอ เพราะอาจหมายถึงเคสที่ต้อง block; boolean นี้ derive หลังผ่าน Trend/MSS แล้ว
- EMA50/Structure เริ่ม unselected; hold all ✓ 0.8 วินาทีตามเดิม; Structure กลับ ✓ หรือ unselected ต้องล้าง MSS answer
- MSS Yes ตอนวางแผนเป็นเพียง intent; ยืนยัน candle closed อีกครั้งใน Place order และคง Counter-trend confirm ที่ Save สำหรับ EMA ✓/Structure ✗
- Snapshot เก็บ EMA50, Structure, MSS, label และ condition factor; รักษา tags/warnings บน card, drawer และ Journal
- Snapshot เพิ่ม stepIndex, baseRPT, is_full_condition, conditionMultiplier, emergencyFactor และ effectiveRPT เพื่ออธิบายขนาดไม้ย้อนหลัง
- คิวไม่ใช่ budget guard: ก่อนเปิดต้องตรวจ `max(0, -weeklyRealizedNetMoney) + openRiskMoney + reservedRiskMoney + candidateRiskMoney <= weekStartEquity × 1.20%` รวมทั้ง monthly/Active gates
- ใช้ risk หลังตัวคูณและการปัด lot ใน budget guard; ห้ามรวมเปอร์เซ็นต์คนละ Equity basis โดยตรง
- Step-4 loss lock ค้างจน weekly reset; สิทธิ re-entry และการเปลี่ยน Condition ไม่ปลดล็อก

**ความหมายของตัวอย่างและขีดจำกัด:**

- ตัวอย่างใหม่เมื่อใช้ 65%: loss −0.130/−0.300/−0.195 แล้ว win +0.600 รวม −0.025% ก่อนค่าธรรมเนียมบนฐานเดียวกัน จึงยังคง Step 4 ไม่ reset; ตัวอย่าง 60% เดิมที่กลับเท่าทุนใช้ไม่ได้กับ policy ใหม่
- ไม้ 100% ไม่รับประกันคืนทุน: แพ้เต็มสามไม้แรก −0.80% แล้วไม้ 4 ชนะ 1.5R ได้ +0.65% ยังเหลือ −0.20% จึงคง Step 4
- ผลรวมสี่ไม้ที่แพ้ติดกันอยู่ระหว่าง 0.78–1.20% ก่อน emergency เมื่อฐานคงที่; หากมีอย่างน้อยหนึ่งไม้ 65% ค่าสูงสุดคือ 1.13% (เฉพาะ Step 1 ใช้ 65%) ไม่ใช่ 1.00%
- ผลรวมข้างต้นเป็นหนึ่งชุดสี่ไม้ ไม่ใช่คำรับประกัน gross loss ทั้งสัปดาห์ เพราะอาจ reset แล้วเทรดอีก; weekly guard จำกัด projected net loss ตามนิยามในสรุปต้นทาง
- Stop risk เป็นค่าคาดการณ์ตาม SL; fill/slippage/gap อาจทำให้ loss จริงเกินตัวเลข จึงต้องบันทึก breach ได้ ไม่ปฏิเสธการบันทึกข้อเท็จจริง

### กฎ workflow ที่คงตาม handoff / WL1

- Satellite: TP บังคับ, R:R ≥ 1.5; Buy ต้อง SL < Entry < TP และ Sell ต้อง SL > Entry > TP
- Place order confirm คง 4 ข้อ: In Zone / Trend Neutral / EMA50 = HVN / Pivot MMT พร้อม MSS candle-closed confirm เมื่อเกี่ยวข้อง; บันทึกออเดอร์ใน Dashboard เท่านั้น ไม่ส่ง broker
- Core Homework cap เป็นกฎถาวร: ยังไม่ทำ → filled + working รวมทุกแผนของ exchange+symbol+strategy ≤ 50% ของ full size; ทำแล้ว ≤100% รวมของที่ถืออยู่
- Homework: MMT ต้อง ④ Wrong if + trigger; COMP ต้อง ① Why buy + ④ Wrong if และกด I've reviewed this; คง Today task และ first-fill auto-add Watch/Port แบบไม่ซ้ำ
- **เก็บ Starter ¼ และ training toggle ตามข้อสรุปล่าสุด:** เปิดใน Settings จึงใช้ข้อจำกัด training ตาม WL1; ปิดแล้วไม่มีการลดขนาดจาก training โดยยังต้องผ่าน Homework cap และ risk gates
- ไม่อยู่ในรายการลบ Settings/control/badge ของระบบใหม่ และไม่เปลี่ยนค่าเปิด–ปิดที่ผู้ใช้ตั้งไว้เอง
- การเติมตาม training ต้องไม่เกิน cap หรือข้าม Compounder Pilot/Add-on gate; เปลี่ยน toggle ไม่ resize holdings/working orders จริงย้อนหลัง
- คำนวณ full size จาก engine ใหม่ แล้วใช้ Homework cap และ training (เฉพาะเมื่อเปิด) จำกัดจำนวน จากนั้นคำนวณ actual risk และตรวจ budgets อีกครั้ง ไม่คูณลด RPT ซ้ำ
- ยืนยัน COMP full-size basis เป็น risk budget ทั้งแผน 1% ก่อน factors: thesis ไม่ครบเปิดเฉพาะ Pilot 0.50%; thesis ครบจึงมีสิทธิ Add-on 0.50% เมื่อ Pilot +1.5R/BE; Starter ON เริ่ม ¼ ของทั้งแผนและเติมได้ภายใน cap ของ phase ปัจจุบัน ไม่กำหนดจำนวนหุ้น Pilot/Add-on ให้เท่ากัน
- คง Watch import เฉพาะ ###WATCHLIST, ซ่อน Candidates แต่เก็บข้อมูล, เอา TV1 export ออกตาม WL1; ไม่รื้อฟื้น UI/export เก่าจาก tests เดิม
- ยืนยันแทน WL1 ข้อ block Filled: ก่อนสั่ง block การเพิ่ม risk เกิน cap; actual fill ที่เกิดแล้วต้องบันทึกได้พร้อม breach และหยุดเพิ่ม risk ตามกฎ แต่ยังลด/ปิด/แก้ SL ได้

### การจองงบและตรวจซ้ำ

- Planned/Draft: preview ได้ ไม่จองงบ
- Ordered: จอง risk และ daily setup quota; ยกเลิกก่อน fill คืนส่วนที่จอง
- Holding: เปลี่ยน reservation เป็น risk ตาม fill จริง โดยไม่บวกซ้ำ
- Partial fill: นับ filled risk + remaining order reservation
- ตรวจซ้ำตอน Place order และ Add-on; ตอน Record fill ต้องรับบันทึกสิ่งที่เกิดจริงได้ แม้ fill เกินงบ แล้วแจ้ง breach และหยุดเพิ่ม risk
- บันทึกการจองและ revision ร่วมกันผ่าน transaction/กลไก conflict detection ของ storage จริง เพื่อไม่ให้สองแท็บใช้ budget ก้อนเดียวกัน
- ผู้ใช้ยืนยัน 15 พฤศจิกายน: reset counters/Step ประจำสัปดาห์ แต่ไม่ล้าง risk ของ holdings/working orders และไม่ reset monthly loss เมื่อยังเป็นเดือนเดิม; เวลา reset ใช้ Asia/Bangkok ตามข้อสรุปแล้ว

## 5. หน้าจอที่ต้องปรับ

| หน้า | หน้าตา/พฤติกรรมใหม่ |
|---|---|
| Today | สรุปสถานะ Normal / Half size / Locked; งานที่ต้องทำ เช่น ยืนยันเลื่อน SL หรือแก้ข้อมูลที่ขาด |
| Plan board | คง Planned / Ordered / Holding; แสดง RPT ที่ใช้, reservation และเหตุผล block จาก engine เดียวกัน |
| ฟอร์ม ＋ / Edit / Add-on | Strategy, Asset, Entry, SL และ TP/Trend/MSS สำหรับ SAT; RPT อ่านอย่างเดียว; COMP เลือก Pilot/Add-on; SAT แสดง Step ปัจจุบัน + Condition 100%/65% + effective RPT โดยไม่ให้พิมพ์ RPT เอง |
| ผลคำนวณใต้ฟอร์ม | Qty, Risk เป็นเงินและ %, Notional; รายละเอียดแสดง 1R/1.5R/2R และ Equity basis |
| ปุ่ม | Save draft ยังได้; Place order ถูก block เมื่อไม่ผ่าน; Record fill/Close trade บันทึกเหตุการณ์จริงได้ |
| Port | MMT weekly used + open/reserved risk, SAT weekly used + next step (แสดง base และขนาด 100%/65% จนกว่าจะเลือก Condition ของแผน), COMP heat; แถว Active monthly + Emergency |
| Journal | P&L จริง, strategy, idea/tranche, initial risk, event timeline และสาเหตุเปลี่ยน state |
| Settings | แสดง policy ใหม่ชุดเดียว, Equity snapshots, contract/lot/FX, recovery/unlock พร้อมบันทึกเหตุผล |
| Flow / Watch | คง PB1d/WL1 workflow, homework และ cap tag; ตัดเฉพาะ legacy macro sizing multipliers; ไม่ใช้ RE1 ไปแก้งาน layout PB1d |

ไม่แสดง “เหลือ 4 slots” เป็นจำนวนตายตัวเมื่อใช้ half-size หรือความเสี่ยงบางไม้ถูกลดแล้ว; แสดงจำนวนที่เปิดเพิ่มได้จาก budget จริงพร้อมจำนวนไม้ที่ยังเสี่ยง

## 6. Architecture ที่เข้ากับโปรเจกต์

- เสนอ `risk-engine.js`: pure functions สำหรับ sizing, budgets, state transitions, eligibility และ reason codes; ไม่อ่าน DOM/clock/storage เอง
- Adapter ใน `index.html`: แปลงข้อมูลบัญชี/trade/card/order ให้เป็น input กลาง แล้วใช้ผลเดียวกันกับฟอร์ม, Plan, Today และ Port
- Snapshot ของแต่ละ order/fill: policyVersion, accountId, strategy, ideaId, tranche, initialEntry/SL, RPT, equity basis, FX, contract spec, qty, reserved risk
- Event log: order placed/cancelled, filled, partial closed, closed, stop confirmed, equity snapshot, emergency/unlock; event IDs ป้องกันการนับซ้ำ
- เก็บ state ที่ derive ได้เป็น cache พร้อม revision; event log และข้อมูลจริงเป็นฐานสำหรับตรวจย้อนหลัง
- หากยังต้องฝัง JS ใน `index.html` ให้มี sync tool แบบเดิม แต่ใช้ source หลักเดียวและตรวจว่าสำเนาตรงกัน
- ไม่มี legacy/new toggle สำหรับผู้ใช้เมื่อส่งงานเสร็จ; migration เป็นครั้งเดียว ไม่คำนวณสองระบบใน runtime

## 7. ลำดับงานและเงื่อนไขจบแต่ละเฟส

### RE1 — ล็อก Policy และ Data mapping

- ใช้ข้อสรุปหัวข้อ 9 เป็น policy; inventory ผู้เรียกสูตร/gates/settings เก่าและจุดเขียนข้อมูลทุกทาง พร้อมจัดทำรายละเอียดทางเทคนิคที่เหลือ
- ทำ mapping บัญชี, trade, partial exits, pending orders, symbol/product และ snapshots
- จบเมื่อมีตารางชัดเจนว่า “ลบ / แทน / เก็บเป็นประวัติ” และตัวอย่างคำนวณตรงกันทุกหน้า

### RE2 — Engine และ State ใหม่

- ทำ sizing, weekly/monthly gates, actual open risk, progression, Compounder unlock และ emergency state
- ทดสอบ pure functions ด้วยเวลา/ข้อมูลจำลอง ไม่ผูกกับหน้าจอ
- จบเมื่อ boundary cases และ event replay ผ่าน; ยังไม่สลับระบบจริงระหว่างทำเฟส

### RE3 — Migration และวงจร Order/Trade

- ทำ dry run รายงานข้อมูลขาดและผลต่าง; backup/export ก่อนเปลี่ยนข้อมูลจริง
- Open trades คง qty/entry/SL; นำมานับ exposure ใหม่; ข้อมูลขาดให้เป็น Unknown ไม่ใช่ 0
- Draft เก่าคำนวณใหม่; Ordered เก่ารักษา qty ที่สั่งจริงและจองความเสี่ยงตามนั้น; เกิน cap ให้แจ้ง ไม่แอบ resize
- Closed trades คงผลจริง; ประวัติรอบปัจจุบันใช้สร้าง counters หากครบ มิฉะนั้นต้องมี opening state ที่ผู้ใช้ระบุและตรวจสอบได้
- จบเมื่อ migration รันซ้ำไม่ซ้ำข้อมูล, partial fills ไม่ซ้ำ risk, บัญชีไม่ปนกัน และหลายแท็บไม่จองเกิน

### RE4 — UI และ Full replacement

- ต่อทุกหน้ากับ engine ใหม่ พร้อมแก้ copy/help/shortcut hints ให้ตรงกัน
- ลบ PS1/legacy sizing, legacy multipliers (เก็บ Condition, COMP Regime/Emergency และ workflow caps ตามที่นิยามใน engine ใหม่), old loss brakes, Main/Tactical risk controls, old ladders และค่าที่ไม่มีผู้ใช้แล้ว
- อัปเดต import/export เพื่ออ่านข้อมูลเก่าได้โดยไม่รื้อฟื้น policy เก่า
- เอกสารเก่าระบุ Superseded; ลบไฟล์ backup ของ runtime ที่หมดประโยชน์หลังเก็บจุดกู้คืนใน version control และตรวจว่าไม่มีผู้เรียก
- จบเมื่อการค้นหาและ dependency audit ยืนยันว่าไม่มีเส้นทางเปิดออเดอร์ที่ยังใช้กฎเก่า

### RE5 — Regression และส่งมอบ

- ทดสอบผ่าน mock Firestore/Playwright ที่มีอยู่ รวมฟอร์ม, board, drawer, fills, close, Today, Port, Settings และ import/export
- ตรวจหน้าจอ 390/1440px และตรวจสูตร source กับสำเนา inline
- สรุป policy ที่ใช้จริง, migration result, ส่วนเก่าที่ลบ และข้อจำกัดข้อมูลราคา/equity
- Release เมื่อผ่านทั้งหมดเป็นระบบเดียว; rollback ใช้ backup/revision ก่อน cutover ไม่ใช่เปิดสอง engine ค้างไว้

## 8. Acceptance cases สำคัญ

- E ต้นสัปดาห์ = 1,000,000, MMT 0.45%, Entry 100 / SL 95, min-stop ≤5, thesis done/training OFF → budget 4,500, 900 หุ้น เมื่อ lot step = 1; half-size → 450 หุ้น
- MMT ขาดทุนจริง 0.20% ให้นับเงิน 0.20% และ losing idea 1 ครั้ง ไม่หัก 0.45%
- MMT training OFF / ไม่มี emergency / thesis ไม่เสร็จ → 50% ของ full size, budget 0.225%; thesis ไม่เสร็จ block การเติม, เสร็จแล้วเติมได้เฉพาะส่วนที่เหลือถึง full idea ภายใต้ gates
- MMT ไม้ครึ่งขนาดถูก SL ก่อนเติม → loss count +1; แพ้แบบนี้ 4 ideas → lock ที่ loss count 4 แม้ realized loss รวม 0.90% เมื่อฐานคงที่และไม่มี fees/slippage
- MMT ครึ่งแรกและไม้เติมเป็น idea เดียวกัน ไม่เพิ่ม counter ซ้ำเมื่อปิดหลาย tranche; win ไม่ล้าง weekly loss count
- SAT loss/loss/loss/loss ที่ 100% → 0.20/0.30/0.30/0.40 แล้ว lock; เปลี่ยน 65%/100% ไม่เปลี่ยน Step เอง
- SAT −0.130/−0.300/−0.195/+0.600 จากฐานเดียวกันและไม่มี fees → net −0.025%, คง Step 4; win ที่ทำให้ weekly net ≥0 จึง reset
- SAT ชนะแล้ว net ยังลบ → คง Step ทั้ง 65% และ 100%; net เท่าศูนย์/บวก → reset; breakeven → ไม่ขยับ
- SAT Step 3 ×65% × emergency 0.5 → 0.0975%; ไม่มี Unclear Trend 0.6 เก่ามาคูณซ้ำ
- SAT mixed-loss 0.13+0.30+0.30+0.40 = 1.13%; net loss budget เหลือไม่พอ effective risk → block แม้ Step ยังเปิดได้
- SAT มี partial close แล้ว final close → weekly P&L ไม่ซ้ำและ step ขยับครั้งเดียว; win แต่ fees ทำให้ net weekly ลบ → ไม่ reset
- SAT ✓✓ →100%; ✗✓ →65%+warning; ✓✗/✗✗ + MSS Yes →65% พร้อม tag ที่ถูก; MSS No/blank →blocked; Structure เปลี่ยนกลับ ✓/unselected ล้าง MSS
- SAT Condition ขาด → ยัง place ไม่ได้; เปลี่ยน Condition หลัง order/fill ไม่เปลี่ยน qty ย้อนหลัง; TP ขาด/ผิดฝั่ง/R:R <1.5 ไม่ Place order
- WL1 homework cap รวมหลาย plans/working orders ไม่เกิน 50% ก่อน done และ 100% หลัง done; COMP ใช้ฐาน risk ทั้งแผน 1% ก่อน factors; thesis done ไม่ข้าม Add-on gate
- Starter toggle ON ใช้ training cap; OFF ไม่ใช้ training cap; ทั้งคู่ยังผ่าน Homework/risk gates และไม่ resize holdings/working orders เดิมย้อนหลัง
- SAT product เดียวกันต่าง symbol alias ใช้โควตาร่วมกัน; สองบัญชีใช้ขอบเขตตาม policy ที่เลือก
- SAT attempt แรกโดน SL จากราคาสะบัด → รับรู้ loss/เลื่อน Step; setup เดิมยัง valid จึง re-entry ได้อีกหนึ่ง attempt หลังผ่าน gates; ห้ามครั้งที่สามของ product/day
- SAT retry ไม่คืน loss budget ไม่ใช้ Step เดิมฟรี และไม่ข้าม Step-4 lock; partial fills ภายใน attempt ไม่ใช้สิทธิ retry เพิ่ม
- SAT Step 1 full loss 0.20% → re-entry Step 2 full risk 0.30% (ไม่ cap 0.20%); ถ้า Condition reduced ใช้ 0.195%; ถ้า Step 2 แพ้ → Step 3
- ตัวอย่างฐานคงที่ ไม่มี fees/slippage/min-stop trim: Step 1 −0.20% แล้ว Step 2 full win 1.5R +0.45% → net +0.25%; ถ้าแพ้ทั้งสอง → −0.50% ไม่ใช่ −0.40% ของข้อเสนอ capped retry
- Monthly cap เต็มแต่สัปดาห์เพิ่ง reset ยังเปิดใหม่ไม่ได้
- +1.5R แต่ยังไม่ยืนยัน SL: risk ไม่ลด; ยืนยัน SL ที่ entry: principal risk เป็น 0
- COMP Add-on ต้อง Pilot ถึง +1.5R และ SL บังทุนแล้ว; strategy lock ต้อง block ทั้ง Pilot และ Add-on
- COMP แพ้ 6 ticker-cycles ที่ขาดทุนไม้ละ 0.2% ยังเข้า loss-streak lock แม้ loss รวมไม่ถึง 6%
- เปลี่ยนเดือนแล้ว Half-size ไม่ถูกปลดเพียงเพราะ month-start baseline เปลี่ยน
- ออเดอร์ค้างข้ามสัปดาห์, partial fill, cancel, reload, duplicate events และ edit ย้อนหลังให้ผลคงเดิม
- ค่า SL/Equity/FX/spec ขาด → Unknown และไม่เปิด risk เพิ่ม; actual fill ที่เกิดแล้วบันทึกได้
- Import ข้อมูลเก่าไม่ทำให้ old caps หรือ multipliers กลับมาใช้งาน
- SAT XAU Ordered/Holding บล็อก BTC Place order แต่ไม่บล็อก Save draft; ยกเลิกก่อน fill คืนคิว; BE/partial exit ยังไม่คืนคิว
- COMP regime 75% + emergency 50% → factor 50%; unlock ต้องเขียวสองตัว+ข้อมูลปัจจุบัน+review confirm ไม่ปลดเอง
- Min-stop 4% กับ actual SL 2% → size ด้วย 4% แต่แสดง actualStopRisk จาก 2%; R targets อ้าง initial actual SL
- วันจันทร์/วันที่ 1 เปลี่ยน counters ตาม Asia/Bangkok แต่ exposure ค้างอยู่; เปลี่ยน timezone เครื่องไม่เปลี่ยนรอบ
- Actual fill เกิน cap รับบันทึกพร้อม breach; Place order ใหม่เกิน cap ยังถูก block

## 9. คำถามและคำตอบที่ผู้ใช้ยืนยันครบแล้ว — 15 พฤศจิกายน 2026

ผู้ใช้ระบุ “เอาทุกข้อตามแนะนำ” ครอบคลุม 1–6 รวม 2A/2B ด้านล่าง ยืนยัน policy ไม่ใช่อนุมัติให้ลงมือพัฒนา

| คำถาม | คำตอบที่ยืนยัน |
|---|---|
| 1. Sat เปิดหลาย product พร้อมกันได้ไหม? | คิวร่วมต่อบัญชี ครั้งละหนึ่ง active setup; อีก product เตรียม Planned ได้ จองคิวตอน Ordered ปิดครบจึงปล่อย; BE/partial close ไม่ปล่อยคิว |
| 2A. COMP Regime/unlock ใช้อะไร? | ACWI/BIL + HYG/IEI slow เดิม; sizing 100/75/50%; แพ้ 6 รอบล็อกจนทั้งคู่เขียว ข้อมูลปัจจุบัน และผู้ใช้ review/confirm; ไม่เพิ่ม EMA40W gate; ใช้ min(regime, emergency) |
| 2B. COMP Homework/Starter คิดจากอะไร? | ทั้งแผน risk 1% ก่อน factors; thesis ไม่ครบ Pilot ≤0.50%; เสร็จแล้วเปิดสิทธิ Add-on 0.50% แต่ต้อง +1.5R/BE; Starter ¼ ของทั้งแผนเมื่อ ON เติมได้ใน phase cap เท่านั้น |
| 3. Min-stop คงไหม? | คง ใช้ max(actual SL distance, min-stop) สำหรับ sizing; actual SL สำหรับ risk และผลเทรด ไม่ย้าย SL |
| 4. Equity/Emergency ใช้ฐานไหน? | แยก Main/Family; actual equity รวม unrealized; sizing/weekly budget ใช้ต้นสัปดาห์ monthly budget ใช้ต้นเดือน แยก cash flow; DD จากต้นเดือนที่ trigger −10%, เริ่มลดเดือนถัดไปและเก็บฐานเดิมจนฟื้น >−5% |
| 5. Reset เมื่อไร? | Asia/Bangkok: daily 00:00, weekly จันทร์ 00:00, monthly วันที่ 1 00:00; ไม่ล้าง open/working risk |
| 6. Fill จริงเกิน cap บันทึกได้ไหม? | ได้พร้อม breach; block ก่อนสั่งเพิ่มความเสี่ยง ไม่ปฏิเสธธุรกรรมที่เกิดจริง และยังลด/ปิดสถานะได้ |

### จุดเปลี่ยนจากสเปกต้นทางที่ต้องสื่อสารใน handoff

- SAT เปลี่ยนจาก win reset เสมอ → win และ weekly net ≥0 จึง reset; เพิ่ม Condition 100/65%, คิวทีละ setup และ whipsaw re-entry หนึ่งครั้ง
- MMT ยืนยัน thesis 50% แต่ stop-out ใช้กระสุนเต็มหนึ่งไม้; แยก loss count ออกจากเงินจริง
- COMP แทน unlock Benchmark >EMA40W ด้วย Regime เดิมทั้งสองเขียว+review/confirm และใช้ตัวลดที่เข้มกว่าระหว่าง Regime/Emergency
- คง min-stop, Homework และ Starter toggle ตาม workflow เดิม; ไม่ลบทุกกฎเดิมแบบเหมารวม
- ใช้ฐาน sizing ต้นสัปดาห์และบันทึก actual fill เกิน cap เพื่อให้ข้อมูลตรงพอร์ตจริง

### รายละเอียดที่ผู้พัฒนาต้องทำให้ชัดใน technical specification

ไม่ใช่การเปิดหกคำถามข้างต้นใหม่: ระบุ snapshot/FX/cash-flow arithmetic, freshness cutoff ของข้อมูล Regime, migration/replay ของไม้ค้างข้ามรอบ, deterministic event IDs และนิยาม net/gross ของ aggregate Active budget ให้ตรวจสอบได้ ข้อเสนอเดิมเรื่อง Momentum projected-loss guard ต้องแยกจากการยืนยันหกข้อนี้ ไม่ถือว่าถูกอนุมัติโดยอัตโนมัติ

คง universe/TF ที่มีอยู่เว้นแต่ผู้ใช้ระบุให้เปลี่ยน ไม่ถือ XAU/BTC ตัวอย่างเป็นคำสั่งลบ S50/Brent; ไม่มีการ merge/deploy/แก้ application code ในงานแผนนี้
