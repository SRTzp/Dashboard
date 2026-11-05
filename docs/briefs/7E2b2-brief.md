# 7E-2b-2 — Watchlist Tier + ทางเข้าเดิม + บันทึกไม้ย้อนหลัง + ผูกการ์ด↔Positions + ป้าย BE · เทส 29

> ✅ พร้อมส่ง (1 ต.ค.) — ชื่อฟังก์ชันอ้างจากไฟล์หลัง 7E-2b-1-fix (964,093 bytes)
> รอบที่สองของ 7E-2b · กติกา = `claude/core-risk-framework.md` · สเปก = `claude/7E-card-spec.md` §3 (ป้าย Tier เทียบ Watchlist)
> สำรองก่อนแก้: `index.backup-pre-7E2b2.html` · **ห้ามแตะ** core-size.js · สูตรทั้งหมด · การ์ด Sat · หน้าตาการ์ด Core (เพิ่มได้แค่ชิปป้าย Tier ข้อ B3)
> เลขบรรทัดอ้างจาก `index.backup-pre-7E2b1.html` (ก่อน 2b-1) — ใช้ grep ตามชื่อฟังก์ชัน

## ข้อตัดสินที่ใช้
- ผู้ใช้ ok 1 ต.ค.: ไม้ที่ซื้อผ่านการ์ด Core ไม่นับ "นอกแผน" · Positions [แก้] ของไม้ที่ผูกการ์ด → เปิดการ์ดแทน · [ยกเลิก]/[ลบ] → ยืนยัน + ปิดการ์ดด้วย · ป้าย "BE" แทน "LOSS" เมื่อ P&L = 0
- ช่อง Tier ใน Watchlist = ป้ายเตือนอย่างเดียว ไม่ล็อก ไม่เปลี่ยน Tier การ์ดเอง
- ฟอร์มย้อนหลัง = ไม้ปิดแล้วเท่านั้น · ติด "นอกแผน" เสมอ · ไม่สร้างการ์ด

---

## A. ไม้ที่มาจากการ์ด Core ไม่นับ "นอกแผน"
ตอนนี้ `makeTradeObject` (บรรทัด ~7199) ตั้ง `unplanned` = ไม่อยู่ใน Watchlist → ไม้ที่ซื้อผ่านการ์ด (เช่น AAPL) ขึ้น "นอกแผน"
1. `makeTradeObject` รับ `o.fromCard` (true) → `unplanned: false` เสมอ (มาก่อนเงื่อนไขอื่น · `prevTrade` ของไม้ผูกการ์ดก็ต้องได้ false)
2. จุดสร้าง/อัปเดตไม้จากการ์ดส่ง `fromCard:true`: `coreBuy1Save` (~5891) · `coreLBuySave` (~6005 · ซื้อระดับ L ครั้งแรก)
3. **ไม้เก่าที่บันทึกไปแล้ว** (ไม่ migrate ข้อมูล): helper `tradeOffPlan(t)` = `!!t.unplanned && !coreCardOfTrade(t)` · `coreCardOfTrade(t)` = การ์ดใน `coreCardsList` ที่ `trade_id === t.id` (ต้องเช็ก `acct` ตรงด้วย)
   - แทนการอ่าน `t.unplanned` เพื่อแสดงผล/นับ ทุกจุด: `posSymHtml` (~4682) · สถิตินอกแผน `offList` (~4631) · ตัวกรอง Journal `offplan` (~6051) · แถว Closed (~6113) · หัวกลุ่ม (~6135) · การ์ด Closed มือถือ (~6153) · grep `unplanned` ให้ครบ · รายงานตาราง จุด/แก้หรือไม่/เหตุผล
   - **ไม่แตะ** จุดที่ใช้ `unplanned` ตัดสิน `plannedEntry` (~7257) และการ์ด Sat
   - coreCards ยังโหลดไม่เสร็จ → ถือว่าไม่มีการ์ด (แสดงแบบเดิม · วาดใหม่เมื่อ listener มา — `coreRefresh` เรียก `render()` อยู่แล้ว)

## B. Watchlist: ช่อง Tier + ป้ายเทียบบนการ์ด Core
### B1. ข้อมูล
- `users/{uid}/watchlist/{TICKER}` เพิ่ม `tier` ('A' | 'B' | ไม่มี) + `tier_set_at` ('YYYY-MM-DD' · `thaiToday()`)
- listener `wlStart` (~3125) map เพิ่ม `tier` (รับเฉพาะ 'A'/'B' · อื่น = null) + `tier_set_at` (รูปแบบผิด = null) · อัปเดตคอมเมนต์ `wlItems`
- ✅ Firestore rules ตรวจแล้ว (1 ต.ค.): `match /users/{uid}/watchlist/{ticker} { allow read, write: if request.auth != null && request.auth.uid == uid; }` — ไม่จำกัดชื่อฟิลด์ · เพิ่ม `tier`/`tier_set_at` ได้เลย ไม่ต้องแก้ rules · เขียนไม่ผ่าน = alert เดิมของ `wlAddSave`

### B2. ตั้ง Tier ในหน้า Watch
- โมดัล `wlAddOverlay` (~2339) เพิ่มแถว **Tier** `<select id="wlAddTier">` : ยังไม่ตั้ง · A · B + ตัวเล็ก "ตั้งเมื่อ …" เมื่อแก้ไข
- `wlOpenAdd` = ยังไม่ตั้ง · `wlOpenEdit` = ค่าเดิม
- `wlAddSave` (~6754): ค่าเปลี่ยน → เขียน `tier` + `tier_set_at = thaiToday()` · ไม่เปลี่ยน = ไม่แตะ `tier_set_at` · เลือก "ยังไม่ตั้ง" = ลบฟิลด์ (`firebase.firestore.FieldValue.delete()` — ตรวจว่า mock-firebase รองรับ · ไม่รองรับ = เขียน `null`)
- แสดงชิป Tier: หัวรายละเอียด `wlDetailHtml` (ข้าง `wlPortTag`) + แถวในรายการ Watchlist (ชิปเล็ก `A`/`B` · ยังไม่ตั้ง = ไม่แสดง) · Tier A ตั้งเกิน 12 เดือน = ชิปเทา "ทบทวน"

### B3. ป้ายบนการ์ด Core (ทั้ง W และ L)
- `coreWatchInfo(ticker)` → `{loaded: wlStoreReady && !wlStoreErr, found, tier, setAt}` · จับคู่ด้วย `wlSymKey` (PTT = PTT.BK)
- `Calc.coreSize.tierBadge({cardTier, watch, today: thaiToday()})` → badges
- แสดง: ในตัวการ์ด (ขยาย) ต่อท้ายชิป Tier ใน `.ccChips` — warn = ชิปเหลือง · muted = ชิปเทา · แถวยุบ: มี warn อย่างน้อย 1 → ไอคอน ⚠ เล็กข้างป้าย `A·W`/`A·L` (title = ข้อความ) · muted ไม่แสดงในแถวยุบ
- โหลด Watchlist ไม่ได้ / ยังโหลดไม่เสร็จ = ไม่แสดงอะไรเลย · ไม่ล็อกปุ่มใด ๆ · ไม่เปลี่ยน Tier การ์ด
- บล็อก Tier ในฟอร์ม (2b-1) แสดงบรรทัดข้อมูล "Watchlist: Tier A (ตั้งเมื่อ …)" / "Watchlist: ยังไม่ตั้ง Tier" / "ไม่อยู่ใน Watchlist" — เพิ่มใน `coreTierBlockHtml(cfg, ti)` (~5579 · ใช้ทั้งฟอร์มใหม่และ `coreTierOpen`) ผ่านพารามิเตอร์ ticker/ข้อมูล Watchlist · ข้อมูลอย่างเดียว ไม่เปลี่ยนผลคำนวณ

## C. ทางเข้าเดิมกลับมา
### C1. Watch → "เปิดแผนเทรด →"
- `wlDetailHtml` (~6784 · คอมเมนต์ "7E-2: เปิดใหม่") เพิ่มปุ่ม **"เปิดแผน Core →"** ในแถว `wlActs` (เฉพาะแถวที่อยู่ใน Watchlist)
- กด → `switchTab('plan')` → `setPlanScope('stock')` → เปิด sheet แผน Core ใหม่พร้อม ticker — `coreNewOpen(acct, opt)` (~5640) มี `opt` อยู่แล้ว → เพิ่ม `opt.ticker` (เติมช่อง Ticker แล้วเรียก `coreNewIn()`) · ไม่กระทบโหมด `opt.id`/`opt.mode` เดิม
  - บัญชี = บัญชีที่ตลาดตรงกับ ticker (ตามกติกาเดิมของ sheet) · มีการ์ดเปิดของ ticker นี้ในบัญชีนั้นอยู่แล้ว = ข้อความเดิม + ปุ่ม "ไปที่การ์ด"
- ลบคอมเมนต์ "7E-2: เปิดใหม่" ทั้งสองจุด (~2020 · ~6784) เมื่อทำแล้ว

### C2. Journal → "บันทึกไม้ย้อนหลัง"
- ปุ่มที่หัวแผง Closed Trades (~2020) → sheet ฟอร์มเล็ก (ใช้ `UI.sheet` แบบเดียวกับ core sheet)
- ช่อง: บัญชี · Port [Core | Sat] · Ticker/Asset · Long/Short · Entry · SL · Qty · (Sat: โบรก → `sat7dBrokerOpts(B, asset)` ได้ mult/สกุล · Core: mult 1 · สกุลตามตลาด `.BK` = THB) · วันเข้า · ราคาปิด · วันปิด (ค่าเริ่ม `thaiToday()`) · เหตุผลปิด (แท็ก exit เดิม · ไม่บังคับ)
- ตรวจ: ตัวเลข > 0 · Long: SL < Entry · Short: SL > Entry · วันปิด ≥ วันเข้า · วันปิด ≤ วันนี้ (เวลาไทย)
- บันทึก → `makeTradeObject({status:'closed', unplannedMode:true, ...})` → push ลง `getBook(acct).trades` → `saveBook` · ไม่สร้างการ์ด · ติดป้าย "นอกแผน"
- Sat: port `satB` · Core: port `core`

## D. ผูกการ์ด ↔ Positions
ไม้ที่มีการ์ด = `coreCardOfTrade(t)` ไม่ว่าง
1. **[แก้]** (`posBtns` ~4688) → ไม่เปิด `openTradeEdit` · เปิดการ์ดแทน: `setPlanScope('stock')` (ถ้าไม่ใช่) → `coreExpand(id)` → `coreGoto(id)` (เลื่อนไป + กระพริบ) · title "แก้ผ่านการ์ด Core"
2. **[ยกเลิก]** → sheet ยืนยัน "ยกเลิกไม้ {sym} จะปิดการ์ด Core {sym} ด้วย (ประวัติไม้ในการ์ดยังอยู่)" → ยืนยันแล้วเปิดโมดัล Cancel เดิม (`openCancelModal`) → บันทึกสำเร็จ → การ์ด `status:'closed'`, `closed_at`, `closedBy:'cancel'`
3. **[ลบ]** → sheet ยืนยัน "ลบไม้ {sym} จะปิดการ์ด Core {sym} ด้วย" แทน `confirm()` เดิม → ลบไม้ + การ์ด `status:'closed'`, `closedBy:'delete'`
4. **[ปิด]** (`openClosePos`) — เหมือนเดิม (การ์ดไปกลุ่มปิดแล้วเองผ่าน `coreEff`)
5. Journal ✎ / ✕ ของไม้ปิดที่มีการ์ด (~6170 · ~6238): ✎ เปิด `openTradeEdit` ได้ตามเดิม (ไม้ปิดแล้ว) · ✕ = ยืนยันแบบข้อ 3
6. `coreEff` รับ `status:'closed'` → `kind:'closed'` · กลุ่มปิดแล้ว (`coreClosedHtml`) แสดงเหตุผล: ปิดตำแหน่ง / ยกเลิกไม้ / ลบไม้
7. การ์ดที่ `closed` ห้ามนับในงบ/ชั้น 2/บันได — `coreLadders` (~5033) ตัดด้วย `coreEff(c).kind==='closed'` อยู่แล้ว · ⚠ `coreEff` (~4996) ตอนนี้คืน `plan` เมื่อ `status!=='open'` → ต้องเช็ก `status==='closed'` **ก่อน** (ข้อ 6) ไม่งั้นการ์ดที่ปิดจะกลับไปเป็นแผนและจองเงินต่อ
8. `openTradeEdit` ถูกเรียกตรงกับไม้ผูกการ์ดที่ยังเปิด (ทางอื่น เช่น คีย์ลัด) → เปิดการ์ดแทนเหมือนข้อ 1 (กันทุนเฉลี่ย/Stop ในการ์ดไม่ตรง)

## E. ป้าย BE
- Journal ตาราง Closed (~6119) + การ์ดมือถือ (~6154): P&L ปัดแล้ว = 0 (กติกาเดียวกับ `pnlCls`/`fmtPnl0`) → `<span class="tag be">BE</span>` (สีเทา — เพิ่มคลาส `.tag.be`) · > 0 WIN · < 0 LOSS
- ตัวกรอง Journal: `win` = P&L > 0 (เดิม) · `loss` = P&L < 0 **หลังปัด** (เดิม ≤ 0 → BE ไม่อยู่ใน Loss) · BE เห็นใน "ทั้งหมด"
- สถิติ Win Rate ไม่เปลี่ยน (BE ไม่นับเป็น win · เหมือนเดิม)

## F. เทส `tests/run_tests_phase29.py` (Chromium · 1440 + 430)
**A นอกแผน**
1. ซื้อไม้ 1 ผ่านการ์ด W ของ ticker ที่ไม่อยู่ใน Watchlist → trade `unplanned:false` · Positions ไม่มีป้าย "นอกแผน"
2. fixture ไม้เก่า `unplanned:true` + มีการ์ดผูก → ไม่มีป้ายทุกจุด (Positions · Journal แถว/กลุ่ม/มือถือ · ตัวกรองนอกแผน · สถิติ nOffPlan) · ไม่มีการ์ด → ยังมีป้าย
3. การ์ด L ซื้อระดับแรก (`coreLBuySave`) → `unplanned:false`

**B Watchlist Tier**
4. ตั้ง A ใน Watchlist → เขียน `tier:'A'`, `tier_set_at` = วันนี้ไทย · แก้ Note อย่างเดียว → `tier_set_at` ไม่เปลี่ยน · เปลี่ยนเป็น B → วันที่ใหม่ · ยังไม่ตั้ง → ลบ/null
5. ป้ายการ์ด (ตรงตาราง §3 สเปก): การ์ด A + WL B → เหลือง "Watchlist = B · การ์ดยังเป็น A" · A + WL ไม่ตั้ง → เหลือง · A + ไม่อยู่ WL → เหลือง "ไม่อยู่ใน Watchlist · ยังไม่ได้ทำการบ้าน" · A + WL A ตั้ง 2025-09-30 (วันนี้ 2026-10-01) → เทา "ทบทวน Tier" · A + WL A ตั้ง 2025-10-01 → ไม่มีป้าย · B + WL A → เทา · B + ไม่อยู่ → เทา · Watchlist error → ไม่มีป้ายเลย
6. PTT.BK ในการ์ด จับคู่ PTT ใน Watchlist ได้
7. แถวยุบมี ⚠ เมื่อมี warn · ไม่มีเมื่อมีแค่ muted
8. ปุ่มทุกปุ่มบนการ์ดยังกดได้เมื่อมีป้ายเตือน

**C ทางเข้า**
9. Watch → "เปิดแผน Core →" → อยู่แท็บแผน scope หุ้น · sheet แผนใหม่เปิด · ticker เติมแล้ว · บัญชีตลาดตรง
10. บันทึกไม้ย้อนหลัง Core (US) + Sat (โบรกจาก fixture) → ไม้ `status:'closed'`, `unplanned:true`, mult/สกุลถูก · ไม่มีการ์ดใหม่ · วันปิดในอนาคต → บันทึกไม่ได้ · Long SL ≥ Entry → บันทึกไม่ได้

**D ผูก Positions**
11. [แก้] ไม้ผูกการ์ด → ไม่มีโมดัลแก้ไม้ · การ์ดขยาย + อยู่ในจอ (`elementFromPoint` กลางการ์ด = การ์ด) · ไม้ไม่ผูก → โมดัลเดิม
12. [ยกเลิก] ไม้ผูกการ์ด → ยืนยัน → Cancel → การ์ด `closed` `closedBy:'cancel'` · กดยกเลิกใน sheet ยืนยัน → ไม่มีอะไรเปลี่ยน
13. [ลบ] ไม้ผูกการ์ด → การ์ด `closed` `closedBy:'delete'` · ไม่มี `confirm()` ของเบราว์เซอร์
14. หลังข้อ 12/13: ชั้น 2 / เงินสดว่าง / งบ L เท่ากับตอนไม่มีการ์ดนั้น

**E BE**
15. P&L 0 และ −0.4 (ปัดเป็น 0) → "BE" · 1 → WIN · −1 → LOSS · ตัวกรอง Loss ไม่มีแถว BE · Win Rate เท่าเดิม

**รวม**
16. 430px ไม่ล้นแนวนอน · sheet ย้อนหลัง/ยืนยันเห็นปุ่มครบ
- ภาพ `tests/screenshots/7e2b2-*` (เต็มจอ): wl-tier-modal · card-tier-badges · backfill-form · pos-link-confirm · journal-be (1440 + 430)

## G. รัน / รายงานกลับ
- `check_syntax` · `sync_core_size --check` · `node tests/core_size_test.js` · run_tests + ทุก phase (p24 · p25 · p26 · p28 ต้องผ่าน)
- เคสเดิมที่เปลี่ยน (เช่น เคสที่คาด "นอกแผน" บนไม้การ์ด · ตัวกรอง loss รวม 0) → `tests/7E2b2_retired.md` · ห้ามลบเคส
- รายงาน: จำนวนเคสก่อน → หลัง · ตารางจุด `unplanned` (ข้อ A3) · รายชื่อภาพ · ข้อที่ตีความเอง · ไม่ push ไม่ลบไฟล์
