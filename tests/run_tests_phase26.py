#!/usr/bin/env python3
"""7E-2b-1 — บันไดถัวตามแนวรับ (L) + งบ W/L + ชั้น 2 เต็มบันได + Tier คำนวณ · เทส 26
mock Firestore · 1440px + 430px · บัญชี US (main) ถัง Core 700,000 fx = 1 (ตัวเลขบาท = ดอลลาร์ ตรงกับสเปก §9) + บัญชี TH (fam) ถัง 700,000
Fund-flow stub ผ่าน ff_stub.py (window.__FF_JSON + ffLoadJson(true)) · ภาพเก็บที่ tests/screenshots/7e2b1-*.png
รัน: python3 run_tests_phase26.py [/path/to/index.html]"""
import copy, json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22
import run_tests_phase23 as p23
import run_tests_phase24 as p24

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
BACKUP = os.path.join(ROOT, "index.backup-pre-7E2b1.html")
p24.INDEX = INDEX
results = []
T = p22.T; bk = p22.bkk_today_minus; TODAY = bk(0)
txt = p24.txt; set_ff = p24.set_ff; go = p24.go_stock; ex = p24.ex; sheet_open = p24.sheet_open


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    """ภาพเต็มจอ: sheet (ซ้อนทับหน้า) = เต็มหน้าต่าง · นอกนั้น = เต็มหน้า · รอ animation จบก่อนถ่าย"""
    page.wait_for_timeout(600)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=not page.locator(".core-sheet").count())
    except Exception as e: print("shot fail", name, e)


def ffj(acwi, hyg, pacwi=None, phyg=None, days_old=0):
    """fundflow.json จำลอง · acwi/hyg = up? · pacwi/phyg = prev_week.up (None = ไม่มี)"""
    j = p24.ff_json(acwi, hyg, days_old)
    if pacwi is not None: j["ratios"]["ACWI_BIL"]["prev_week"] = {"up": pacwi}
    if phyg is not None: j["ratios"]["HYG_IEI"]["prev_week"] = {"up": phyg}
    return j


FF_OPEN = lambda: ffj(False, False, False, False)          # f 50% · สัปดาห์ก่อน 50% → เปิด
FF_75_75 = lambda: ffj(False, True, False, True)           # f 75% · สัปดาห์ก่อน 75% → เปิด
FF_75_NOPREV = lambda: ffj(False, True)                    # f 75% · ไม่มี prev → แดง 1 สัปดาห์
FF_GREEN = lambda: ffj(True, True, True, True)             # f 100% → งด


def usT(id, sym, qty, entry, sl):
    return T(id, "core", "open", sym=sym, entry=entry, sl=sl, qty=qty, cur="USD", date="2026-10-05")


def lcard(id, acct="main", ticker="ZZZ", levels=None, sl=70, bud=0.1, tier="A", status="plan", trade_id=None, **kw):
    lv = levels or [{"px": 100, "status": "wait"}, {"px": 90, "status": "wait"}, {"px": 80, "status": "wait"}]
    split = [0.4, 0.3, 0.3] if len(lv) == 3 else [0.5, 0.5]
    c = p24.card(id, acct, ticker, strategy="L", tier=tier, plan=None, stop=sl, status=status, trade_id=trade_id,
                 ladder={"levels": lv, "sl": sl, "budgetPct": bud, "split": split, "lockedAt": "2026-10-01T00:00:00Z"})
    c.update(kw); return c


def lopen(id, ticker="ZZZ", px=96.5, **kw):
    """การ์ด L หลังซื้อ L1 (280 @ 100) · trade t_<id> qty 280 sl 70"""
    lv = [{"px": 100, "status": "bought", "qty": 280, "fillPx": 100, "boughtAt": "2026-10-05"}, {"px": 90, "status": "wait"}, {"px": 80, "status": "wait"}]
    kw.setdefault("pxDate", TODAY)
    return lcard(id, ticker=ticker, levels=lv, status="open", trade_id="t_" + id, px=px,
                 lots=[{"n": 1, "level": 1, "date": "2026-10-05", "px": 100, "qty": 280, "f": None, "stop": 70}], **kw)


def ltrade(id, sym="ZZZ", qty=280, entry=100, sl=70):
    return usT("t_" + id, sym, qty, entry, sl)


def doc26(main_trades=None, fam_trades=None, core=700000):
    doc = p24.doc_with(main_trades=main_trades if main_trades is not None else [], core_cap=core, main_market="US")
    doc["books"]["main"]["settings"]["fx"] = 1
    fs = doc["books"]["fam"]["settings"]
    fs["capital"]["core"] = core; fs["fx"] = 1
    fs.setdefault("coreRisk", {}).update({"riskPct": 1, "tierA": 10, "tierB": 5}); fs["coreRisk"]["market"] = "TH"   # CZ1: ค่าเริ่มต้นใหม่ (1.25/15/10) → seed ค่าเดิม ให้ตัวเลขที่คาดเท่าเดิม
    doc["books"]["fam"]["trades"] = fam_trades or []
    return doc


def launch(pw, w, h, doc, cards=None, ff=None):
    r = p24.launch(pw, w, h, doc, cards=cards, ff=None)
    if ff is not None: set_ff(r[2], ff)
    return r


def card_sel(id): return f'[data-core-card="{id}"]'
def head(page, acct="main", part=""): return txt(page, f'[data-core-head="{acct}"] {part}'.strip())
def jq(page, js, arg=None): return page.evaluate(js, arg) if arg is not None else page.evaluate(js)


def ladder_rows(page, sel):
    return page.evaluate("""(sel)=>[...document.querySelectorAll(sel+' tr[data-lv]')].map(r=>[...r.children].map(c=>c.innerText.replace(/\\s+/g,' ').trim()))""", sel)


def open_form(page, ticker="ZZZ", acct=None, levels=(100, 90, 80), sl=70, bud=None, tier="A", strat="L"):
    page.evaluate("(a)=>coreNewOpen(a)", acct)
    page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
    page.fill("#cnTicker", ticker)
    if acct: page.select_option("#cnAcct", acct)
    if tier == "A":
        page.click("#cnTierA"); page.fill("#cnReason", "ทดสอบ")
    if strat == "L":
        page.click("#cnStratL")
        page.fill("#cnLv0", str(levels[0])); page.fill("#cnLv1", str(levels[1]))
        if len(levels) == 3:
            page.click("#cnLadd"); page.fill("#cnLv2", str(levels[2]))
        page.fill("#cnLsl", str(sl))
        if bud is not None: page.fill("#cnLbud", str(bud))
    page.wait_for_timeout(120)


def gate_row(page, k):
    return page.evaluate("(k)=>{ const e=document.querySelector('#cnLgates [data-gate=\"'+k+'\"]'); return e ? {ok:e.dataset.ok, t:e.innerText.replace(/\\s+/g,' ').trim()} : null; }", k)


def fill_tier(page, roic=None, nd=None, fcf=None, g5=(False, False, False), fort=(True, True)):
    """กรอกบล็อก Tier · g5 แต่ละข้อ True = ใช่ · False = ไม่ใช่ · None = ยังไม่ตอบ (ปุ่มเป็น toggle → คลิกเฉพาะเมื่อสถานะต่างจากที่ต้องการ)
    TIER2: fort = (FCF บวก 3 ปี, ปันผล/ซื้อหุ้นคืน) — Fortress ต้องมีสองข้อนี้ด้วย · ค่าเริ่มต้น (True, True) = เคส 7E-2b-1 เดิมยังได้ผลเหมือนเดิม"""
    for key, v in zip(("fcf3y", "capret"), fort):
        cur = page.evaluate("(k)=>{ const on=[...document.querySelectorAll('[data-tk=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; }", key)
        if cur == v: continue
        if v is None: page.click(f'[data-tk="{key}"] button[data-v="{1 if cur else 0}"]')
        else: page.click(f'[data-tk="{key}"] button[data-v="{1 if v else 0}"]')
    for sel, v in (("#tiRoic", roic), ("#tiNd", nd), ("#tiFcf", fcf)):
        page.fill(sel, "" if v is None else str(v))
    for key, v in zip(("substitute", "customerMigrating", "singleProduct"), g5):
        cur = page.evaluate("(k)=>{ const on=[...document.querySelectorAll('[data-g5=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; }", key)
        if cur == v: continue
        if v is None: page.click(f'[data-g5="{key}"] button[data-v="{1 if cur else 0}"]')
        else: page.click(f'[data-g5="{key}"] button[data-v="{1 if v else 0}"]')
    page.wait_for_timeout(80)


def tier_res(page): return txt(page, "#tiRes") or ""


def db_card(page, id): return p24.cards_db(page).get(id)


def wait_db(page, fn, n=30):
    for _ in range(n):
        v = fn()
        if v: return v
        page.wait_for_timeout(100)
    return fn()


# ─────────────────────────────────────────────────────────────────────────
def core_size_checks(pw):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), "--check"], capture_output=True, text=True)
    check("0 tools/sync_core_size.py --check ผ่าน (สำเนาใน index.html ตรง core-size.js)", r.returncode == 0, r.stdout + r.stderr)
    a = open(os.path.join(ROOT, "core-size.backup-pre-7E2b1.js"), encoding="utf-8").read().splitlines()
    b = open(os.path.join(ROOT, "core-size.js"), encoding="utf-8").read().splitlines()
    import difflib
    ch = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if (l.startswith("+") or l.startswith("-")) and not l.startswith("+++") and not l.startswith("---")]
    hunks = [l for l in difflib.unified_diff(a, b, lineterm="", n=0) if l.startswith("@@")]
    check("0 core-size.js ต่างจาก backup แค่ 2 จุด: roicMin 0.15→0.12 · canPlaceLadder รับ shareCap/l2Cap (TIER2: 11 hunk รวม 3 เดิม · DD1 13 · CZ1 25 · LN3fix2 33)",
          any("roicMin: 0.12" in l for l in ch) and any("shareCap" in l for l in ch) and any("l2Cap" in l for l in ch) and not any("ffCoreCap" in l for l in ch) and len(hunks) == 33,   # CZ1: firstLot/addLot แก้ตามบรีฟ (+12 hunk) · ffCoreCap ยังห้ามแตะ
           " | ".join(hunks))
    doc = doc26()
    browser, context, page, ce, pe, dialogs = launch(pw, 1440, 900, doc)
    try:
        src = open(os.path.join(ROOT, "tests", "core_size_test.js"), encoding="utf-8").read()
        rr = page.evaluate(p23.NODE_SHIM, src)
        m = re.search(r"(\d+) ผ่าน · (\d+) ไม่ผ่าน", " ".join(rr["last"]))
        check("0 tests/core_size_test.js (รันบนสำเนาใน index.html) = 471/471 (CZ1: +22 เคส · LN3fix2: +29 เคส · เดิม 420 ผ่านครบ) · exit 0", bool(m) and m.group(1) == "471" and m.group(2) == "0" and rr["code"] == 0, json.dumps(rr, ensure_ascii=False))
    finally:
        browser.close()


def ladder_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    # ── A1 · A2 · ฟอร์มบันได US/TH ──
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        open_form(page, "ZZZ", acct="main")
        rows = ladder_rows(page, "#cnLres")
        qty = [r[3] for r in rows]
        tot = txt(page, "#cnLres [data-c-ltot]") or ""
        check(f"{tag} A1 งบ 10% · 40/30/30 · SL 70 · 100/90/80 → หุ้น 280 / 233 / 262", qty == ["280", "233", "262"], json.dumps(rows, ensure_ascii=False))
        check(f"{tag} A1 รวม 775 หุ้น · ทุนเฉลี่ย 90.23 · เสี่ยงเต็ม 2.24% / 2.5% · ไม่เตือนเกิน", "775" in tot and "90.23" in tot and "2.24% / 2.5%" in tot and "เกิน" not in tot, tot)
        check(f"{tag} A1 เสี่ยงถึง SL รายระดับ $8,400 / $4,660 / $2,620 (รวม 15,680)", [r[4] for r in rows] == ["$8,400", "$4,660", "$2,620"], json.dumps(rows, ensure_ascii=False))
        check(f"{tag} A1 ซื้อแค่ระดับแรก เสี่ยง 1.2% (8,400 ÷ 700,000)", "1.2%" in (txt(page, "#cnLres [data-c-lfirst]") or ""), txt(page, "#cnLres [data-c-lfirst]") or "")
        rr = jq(page, """()=>{ const cx = coreCtx('main'); const ld = {levels:[{px:100,status:'wait'},{px:90,status:'wait'},{px:80,status:'wait'}], sl:70, budgetPct:0.1, split:[0.4,0.3,0.3]};
            const a = coreLadderCalc(ld,'US',cx); cx.fx = 33.37; const b = coreLadderCalc(ld,'US',cx);
            return {natQ:a.nat.rows.map(r=>r.qty), thbQ:a.thb.rows.map(r=>r.qty), natQ2:b.nat.rows.map(r=>r.qty), thbQ2:b.thb.rows.map(r=>r.qty), risk:a.thb.fullRisk, first:a.thb.firstRisk, cost:a.thb.cost}; }""")
        check(f"{tag} A1 nat กับ thb จำนวนหุ้นเท่ากันทุกระดับ (fx 1 และ fx 33.37) · thb เสี่ยงเต็ม 15,680 · แค่ L1 8,400", rr["natQ"] == rr["thbQ"] == [280, 233, 262] and rr["natQ2"] == rr["thbQ2"] and abs(rr["risk"] - 15680) < 1e-6 and abs(rr["first"] - 8400) < 1e-6, json.dumps(rr))
        gates = jq(page, "()=>[...document.querySelectorAll('#cnLgates [data-gate]')].map(e=>[e.dataset.gate,e.dataset.ok,e.innerText.replace(/\\s+/g,' ').trim()])")
        check(f"{tag} A1 ประตู 5 ข้อผ่านทั้งหมด (Tier A · f · L รวม · ชั้น 2 · เงินสด) → ปุ่ม 'ล็อกแผน' ใช้ได้", len(gates) == 5 and all(g[1] == "1" for g in gates) and not page.is_disabled("#cnSave") and (txt(page, "#cnSave") == "ล็อกแผน"), json.dumps(gates, ensure_ascii=False))
        page.locator("#cnSave").scroll_into_view_if_needed(); page.wait_for_timeout(200)
        vis = jq(page, "()=>{ const g=document.querySelector('#cnLgates').getBoundingClientRect(), b=document.querySelector('#cnSave').getBoundingClientRect(); return g.top>=0 && g.bottom<=innerHeight && b.top>=0 && b.bottom<=innerHeight; }")
        check(f"{tag} fix3 ภาพ ladder-form-gates: เลื่อนใน sheet แล้วรายการประตู 5 ข้อ + ปุ่ม 'ล็อกแผน' อยู่ในจอ", vis)
        shot(page, f"7e2b1-ladder-form-gates-{w}.png")
        page.click("#cnSave"); page.wait_for_timeout(500)
        k, c = p24.one_card(page, "ZZZ")
        ld = (c or {}).get("ladder") or {}
        check(f"{tag} A1 ล็อกแผน → การ์ด strategy L · status plan · stop = sl = 70 · plan null · มี lockedAt · ระดับ wait ทั้งหมด · split 40/30/30 · งบ 0.1",
              c and c["strategy"] == "L" and c["status"] == "plan" and c["stop"] == 70 and ld.get("sl") == 70 and c["plan"] is None and ld.get("lockedAt") and [l["status"] for l in ld["levels"]] == ["wait"] * 3
              and ld["split"] == [0.4, 0.3, 0.3] and abs(ld["budgetPct"] - 0.1) < 1e-12 and c["tier"] == "A", json.dumps(c, ensure_ascii=False))
        check(f"{tag} A1 ล็อกแผน = จองเงินทันที: เงินสดว่าง 700,000 − 69,930 = 630,070", "630,070" in (head(page, "main", "[data-c-cashfree]") or ""), head(page, "main") or "")
        go(page)
        rowp = txt(page, card_sel(k) + " [data-c-row]") or ""
        check(f"{tag} A1 แถวแผน L: 'แผน' · A·L · L1 100.00 · SL 70.00 · จอง $69,930", all(x in rowp for x in ("แผน", "A·L", "L1", "100.00", "SL", "70.00", "จอง $69,930")), rowp)
        ex(page, k); shot(page, f"7e2b1-card-L-plan-{w}.png")
        # TH
        page.evaluate("()=>coreSheetClose()")
        open_form(page, "TTT.BK", acct="fam")
        rowsT = ladder_rows(page, "#cnLres")
        check(f"{tag} A2 TH เดียวกัน (ถัง 700,000 · งบ 10%) → 200 / 200 / 200 หุ้น (ปัดหลัก 100)", [r[3] for r in rowsT] == ["200", "200", "200"], json.dumps(rowsT, ensure_ascii=False))
        check(f"{tag} A1/A2 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()

    # ── A3 · A4 · A5 · A6 · A7 ──
    def seed_open(extra_cards=None, extra_trades=None, px=96.5):
        cards = {"l1": lopen("l1", px=px)}; cards.update(extra_cards or {})
        return doc26(main_trades=[ltrade("l1")] + (extra_trades or [])), cards

    # A3: ซื้อ L1 ผ่าน sheet จากแผน
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards={"l1": lcard("l1")}, ff=FF_OPEN())
    try:
        go(page); ex(page, "l1")
        btn = txt(page, card_sel("l1") + " [data-c-lbuy]")
        check(f"{tag} A3 ปุ่มหลักบนการ์ดแผน L = 'บันทึกซื้อ L1' · มี 'แก้แผนบันได' · 'ลบแผน' · ⋯", btn == "บันทึกซื้อ L1" and page.locator(card_sel("l1") + " [data-c-ledit]").count() == 1 and page.locator(card_sel("l1") + " [data-c-delplan]").count() == 1 and page.locator(card_sel("l1") + " [data-c-more]").count() == 1, btn)
        page.click(card_sel("l1") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]')
        d0 = {"px": page.input_value("#clPx"), "qty": page.input_value("#clQty"), "date": page.input_value("#clDate"), "stop": txt(page, "[data-cl-stop]")}
        check(f"{tag} A3 sheet ซื้อ L1: ราคาเริ่ม 100 · จำนวนเริ่ม 280 · วันที่วันนี้ · Stop = SL บันได 70.00 (แก้ไม่ได้)", d0["px"] == "100" and d0["qty"] == "280" and d0["date"] == TODAY and "70.00" in d0["stop"] and page.locator("#clStop").count() == 0, json.dumps(d0, ensure_ascii=False))
        page.fill("#clPx", "60"); chk = page.is_disabled("#clSave")
        page.fill("#clPx", "100"); page.fill("#clQty", "0"); chk2 = page.is_disabled("#clSave"); page.fill("#clQty", "280")
        check(f"{tag} A3 ราคาซื้อ ≤ SL → บันทึกไม่ได้ · จำนวน 0 → บันทึกไม่ได้", chk and chk2)
        page.click("#clSave"); page.wait_for_timeout(600)
        trs = p24.book_trades(page)
        t = [x for x in trs if x["sym"] == "ZZZ"]
        check(f"{tag} A3 ซื้อ L1 (280 @ 100) → trade เปิด 1 ตัว qty 280 sl 70 entry 100 port core Long", len(t) == 1 and t[0]["qty"] == 280 and t[0]["sl"] == 70 and t[0]["entry"] == 100 and t[0]["port"] == "core" and t[0]["status"] == "open" and t[0]["bias"] == "Long", json.dumps(t))
        c = db_card(page, "l1")
        check(f"{tag} A3 การ์ด: status open · trade_id · ระดับ L1 bought qty 280 fillPx 100 boughtAt · lots[0] level 1 f null · L2/L3 ยัง wait",
              c["status"] == "open" and c["trade_id"] == t[0]["id"] and c["ladder"]["levels"][0]["status"] == "bought" and c["ladder"]["levels"][0]["qty"] == 280 and c["ladder"]["levels"][0]["fillPx"] == 100 and c["ladder"]["levels"][0]["boughtAt"] == TODAY
              and c["lots"][0]["level"] == 1 and c["lots"][0]["f"] is None and [l["status"] for l in c["ladder"]["levels"][1:]] == ["wait", "wait"], json.dumps(c, ensure_ascii=False))
        check(f"{tag} A3 ถือ ฿28,000 · จอง ฿41,930 (เงินสดว่าง 630,070 เท่าเดิม)", "฿28,000" in (txt(page, card_sel("l1") + " [data-c-lhold]") or "") and "฿41,930" in (txt(page, card_sel("l1") + " [data-c-lhold]") or "") and "630,070" in head(page, "main", "[data-c-cashfree]"), txt(page, card_sel("l1") + " [data-c-lhold]") or "")
        page.evaluate("(d)=>coreWrite('l1',{px:96.5,pxDate:d})", TODAY); page.wait_for_timeout(300)
        l2 = jq(page, "()=>{ const r = coreAcctRisk('main'); return {now:r.l2.risk, full:r.l2.riskFull, np:r.layer2Pct, fp:r.layer2FullPct, n:r.l2.pct, f:r.l2.pctFull}; }")
        check(f"{tag} A3 ปิด 96.50 → ชั้น 2 ตอนนี้ 7,420 (1.06%) · เต็ม 14,700 (2.10%)", abs(l2["now"] - 7420) < 1e-6 and abs(l2["full"] - 14700) < 1e-6 and abs(l2["np"] - 1.06) < 0.005 and abs(l2["fp"] - 2.1) < 0.005, json.dumps(l2))
        hd = head(page, "main", "[data-c-l2]") or ""
        check(f"{tag} A3 หัวบัญชี: 'ชั้น 2 ตอนนี้ 1.06% · เต็ม 2.1% / 20%'", "ตอนนี้ 1.06%" in hd and "เต็ม 2.1% / 20%" in hd, hd)
        check(f"{tag} A3 ป้ายแถว 'L 1/3' · ไอคอน 🟢 · ไม่มี #n/N ของ W", (txt(page, card_sel("l1") + " [data-c-lbadge]") == "L 1/3") and page.locator(card_sel("l1") + " [data-c-lotbadge]").count() == 0 and (txt(page, card_sel("l1") + " [data-c-status]") or "").strip() == "🟢", txt(page, card_sel("l1") + " [data-c-row]") or "")
        ex(page, "l1"); shot(page, f"7e2b1-card-L-open-{w}.png")
    finally:
        browser.close()

    # A4: ซื้อ L2
    doc, cards = seed_open()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards=cards, ff=FF_OPEN())
    try:
        go(page); ex(page, "l1")
        check(f"{tag} A4 ปุ่มหลัก = 'บันทึกซื้อ L2' (ระดับ wait ตัวแรก)", txt(page, card_sel("l1") + " [data-c-lbuy]") == "บันทึกซื้อ L2")
        page.click(card_sel("l1") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]')
        check(f"{tag} A4 ค่าเริ่ม: ราคา 90 · จำนวน 233", page.input_value("#clPx") == "90" and page.input_value("#clQty") == "233")
        page.click("#clSave"); page.wait_for_timeout(600)
        t = [x for x in p24.book_trades(page) if x["sym"] == "ZZZ"][0]
        check(f"{tag} A4 ซื้อ L2 (233 @ 90) → trade qty 513 · ทุนเฉลี่ย (28,000+20,970)/513 · sl ไม่เปลี่ยน 70", t["qty"] == 513 and abs(t["entry"] - 48970 / 513) < 1e-9 and t["sl"] == 70, json.dumps(t))
        c = db_card(page, "l1")
        check(f"{tag} A4 lots 2 แถว (level 1, 2) · ระดับ L2 bought · badge 'L 2/3'", [l["level"] for l in c["lots"]] == [1, 2] and c["ladder"]["levels"][1]["status"] == "bought" and c["ladder"]["levels"][1]["qty"] == 233 and txt(page, card_sel("l1") + " [data-c-lbadge]") == "L 2/3", json.dumps(c["lots"]))
        page.click(card_sel("l1") + " [data-c-more]"); page.click(card_sel("l1") + " .ccMenu [data-c-lots-btn]"); page.wait_for_selector('.core-sheet [data-core-sheet="lots"]')
        lots = txt(page, "[data-c-pyr]") or ""
        check(f"{tag} A4 'ดูไม้ที่ซื้อ' ใช้ sheet เดิม · คอลัมน์ f แสดง '—'", "233" in lots and "—" in lots, lots)
    finally:
        browser.close()

    # A5: เลื่อน Stop
    doc, cards = seed_open()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards=cards, ff=FF_OPEN())
    try:
        go(page); ex(page, "l1")
        def stop_to(v):
            page.evaluate("(id)=>coreStopOpen(id)", "l1"); page.wait_for_selector('.core-sheet [data-core-sheet="stop"]')
            page.fill("#csStop", str(v)); page.wait_for_timeout(80)
        stop_to(85)
        pv = txt(page, "[data-cs-preview]") or ""
        check(f"{tag} A5 Stop 70 → 85: ตัวอย่าง 'L3 @80.00 (คืนเงินจอง $20,960 ≈฿20,960)' (สกุลตลาด US)", "ระดับที่จะถูกยกเลิก: L3 @80.00 (คืนเงินจอง $20,960 ≈฿20,960)" in pv, pv)
        shot(page, f"7e2b1-stop-preview-{w}.png")
        page.click("#csSave"); page.wait_for_timeout(500)
        c = db_card(page, "l1"); lv = c["ladder"]["levels"]
        t = [x for x in p24.book_trades(page) if x["sym"] == "ZZZ"][0]
        check(f"{tag} A5 บันทึก → L3 cancelled cancelBy stop + cancelledAt · L2 ยัง wait · L1 bought · t.sl = stop = ladder.sl = 85 · stopHistory +1",
              lv[2]["status"] == "cancelled" and lv[2]["cancelBy"] == "stop" and lv[2].get("cancelledAt") and lv[1]["status"] == "wait" and lv[0]["status"] == "bought" and lv[0]["qty"] == 280 and t["sl"] == 85 and c["stop"] == 85 and c["ladder"]["sl"] == 85 and len(c["stopHistory"]) == 1, json.dumps(c, ensure_ascii=False))
        stop_to(90)
        pv = txt(page, "[data-cs-preview]") or ""
        check(f"{tag} A5 → 90: ตัวอย่างมี L2 @90.00 (฿20,970)", "L2 @90.00" in pv and "$20,970" in pv, pv)
        page.click("#csSave"); page.wait_for_timeout(500)
        lv = db_card(page, "l1")["ladder"]["levels"]
        check(f"{tag} A5 → 90: L2 cancelled ด้วย (ราคา ≤ Stop ใหม่) · L1 bought ไม่ถูกแตะ", lv[1]["status"] == "cancelled" and lv[1]["cancelBy"] == "stop" and lv[0]["status"] == "bought", json.dumps(lv))
        stop_to(105)
        pv = txt(page, "[data-cs-preview]") or ""
        page.click("#csSave"); page.wait_for_timeout(500)
        c = db_card(page, "l1")
        check(f"{tag} A5 → 105: 'ไม่มีระดับที่ถูกยกเลิก' · L1 (bought) ไม่ถูกแตะ (qty 280 fillPx 100) · ladder.sl 105", "ไม่มีระดับที่ถูกยกเลิก" in pv and c["ladder"]["levels"][0]["status"] == "bought" and c["ladder"]["levels"][0]["fillPx"] == 100 and c["ladder"]["sl"] == 105 and len(c["stopHistory"]) == 3, pv + json.dumps(c["ladder"]))
        stop_to(100)
        check(f"{tag} A5 เลื่อนลง (105 → 100) = ปฏิเสธ · ปุ่มบันทึกปิด · ข้อความเดิม", page.is_disabled("#csSave") and "เลื่อนลงไม่ได้" in (txt(page, "#csErr") or ""), txt(page, "#csErr") or "")
    finally:
        browser.close()

    # A6: ยกเลิกระดับด้วยมือ
    doc, cards = seed_open()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards=cards, ff=FF_OPEN())
    try:
        go(page)
        before = jq(page, "()=>coreCtx('main').split.lReserved")
        p24.menu_click(page, "l1", "[data-c-lcancel-btn]"); page.wait_for_selector('.core-sheet [data-core-sheet="lcancel"]')
        page.select_option("#clcSel", "2"); page.wait_for_timeout(60)
        msg = txt(page, "[data-clc-msg]") or ""
        check(f"{tag} A6 ยืนยัน 'ยกเลิก L3 @80.00 · คืนเงินจอง $20,960 ≈฿20,960' (สกุลตลาด)", msg == "ยกเลิก L3 @80.00 · คืนเงินจอง $20,960 ≈฿20,960", msg)
        page.click("#clcOk"); page.wait_for_timeout(500)
        c = db_card(page, "l1"); lv = c["ladder"]["levels"]
        after = jq(page, "()=>coreCtx('main').split.lReserved")
        check(f"{tag} A6 L3 cancelled · cancelBy manual · L2 ยัง wait (ไม่กระจายเงินไประดับอื่น) · จองลดเท่า 20,960 พอดี", lv[2]["status"] == "cancelled" and lv[2]["cancelBy"] == "manual" and lv[1]["status"] == "wait" and abs((before - after) - 20960) < 1e-6, f"{before} -> {after} {json.dumps(lv)}")
        rws = ladder_rows(page, card_sel("l1") + " [data-c-ladder]")
        check(f"{tag} A6 ตาราง: แถว L3 เทา (class cancelled) · สถานะ 'ยกเลิก' · แถว L1 'ซื้อแล้ว' มีบรรทัด 'ซื้อจริง 280 @ 100.00'", page.locator(card_sel("l1") + ' tr[data-lv="L3"].cancelled').count() == 1 and "ยกเลิก" in rws[2][5] and "ซื้อแล้ว" in rws[0][5] and "ซื้อจริง 280 @ 100.00" in (txt(page, card_sel("l1") + ' [data-fill="L1"]') or ""), json.dumps(rws, ensure_ascii=False))
    finally:
        browser.close()

    # A7: ปิดตำแหน่ง
    doc, cards = seed_open()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards=cards, ff=FF_OPEN())
    try:
        go(page)
        b0 = jq(page, "()=>{ const s = coreCtx('main').split; return [s.lHeld, s.lReserved, s.cashFree]; }")
        p24.menu_click(page, "l1", "[data-c-close-btn]"); page.wait_for_timeout(200)
        page.fill("#cpExitPrice", "95"); page.click("#cpConfirmBtn"); page.wait_for_timeout(500)
        b1 = jq(page, "()=>{ const s = coreCtx('main').split; return [s.lHeld, s.lReserved, s.cashFree]; }")
        check(f"{tag} A7 ปิดตำแหน่ง → การ์ดไปกลุ่มปิดแล้ว · จอง + ถือ L = 0 · เงินว่างกลับ 700,000 (ก่อนปิด {b0[2]:,.0f})", page.locator(card_sel("l1") + '[data-kind="closed"]').count() == 1 and b0[0] == 28000 and b0[1] == 41930 and b1[0] == 0 and b1[1] == 0 and b1[2] == 700000, json.dumps([b0, b1]))
    finally:
        browser.close()


def wl_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    # B8 · B10
    trades = [usT("t_w", "WWW", 1000, 100, 90), ltrade("l1")]
    cards = {"l1": lopen("l1"), "w1": p24.card("w1", "main", "WWW", market="US", status="open", trade_id="t_w", stop=90, tier="B", px=100, pxDate=TODAY,
                                               lots=[{"n": 1, "date": "2026-10-01", "px": 100, "qty": 1000, "f": 1, "stop": 90}], plan=None)}
    cards["l2"] = lcard("l2", ticker="YYY")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=trades), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        free = jq(page, "()=>{ const s = coreCtx('main').split; return {free:s.cashFree, w:s.w, lh:s.lHeld, lr:s.lReserved, lp:s.lPct}; }")
        # W 100,000 + L ถือ 28,000 + L จอง (41,930 + 69,930) → เงินว่าง = 700,000 − 100,000 − 28,000 − 111,860 = 460,140
        check(f"{tag} B8 งบ: W ถือ 100,000 · L ถือ 28,000 · L จอง 111,860 (2 บันได) → เงินว่าง 460,140", free["w"] == 100000 and free["lh"] == 28000 and abs(free["lr"] - 111860) < 1e-6 and abs(free["free"] - 460140) < 1e-6, json.dumps(free))
        check(f"{tag} B8 หัวบัญชี 'เงินสดว่าง ฿460,140' · บล็อกสรุป 'เงินว่าง ฿460,140'", "460,140" in head(page, "main", "[data-c-cashfree]") and "เงินว่าง ฿460,140" in (txt(page, '#portsSum [data-sum-free]') or ""), head(page, "main", "[data-c-cashfree]") or "")
        bar = jq(page, """()=>{ const b = document.querySelector('#portsSum [data-sum-bar]'), bw = b.getBoundingClientRect().width;
            const o = {bw}; b.querySelectorAll('i').forEach(i=>o[i.dataset.seg] = i.getBoundingClientRect().width); return o; }""")
        exp = {"wheld": 100000, "lheld": 28000, "lres": 111860, "free": 460140}
        okb = all(abs(bar[k] - bar["bw"] * v / 700000) <= 1 for k, v in exp.items())
        check(f"{tag} B10 แถบ 4 ส่วน (W ถือ · L ถือ · L จอง · เงินว่าง) กว้างตรงสัดส่วนถัง ±1px", okb, json.dumps(bar))
        blk = txt(page, '#portsSum [data-sum="held"]') or ""
        check(f"{tag} B10 'งบ W / L' · 'L รวม 19.98% / 30%' · มีคำอธิบายสีใต้แถบ (W ถือ · L ถือ · L จอง · เงินว่าง)", "งบ W / L" in blk and "L รวม 19.98% / 30%" in blk and all(x in (txt(page, "#portsSum [data-sum-leg]") or "") for x in ("W ถือ", "L ถือ", "L จอง", "เงินว่าง")), blk)
        pos = txt(page, '#portsSum [data-sum="pos"]') or ""
        check(f"{tag} B10 ช่อง 'ตำแหน่ง': 2 ตัว · W 1 · L 1 · ล็อกกำไร", "2 ตัว" in pos and "W 1 · L 1" in pos and "ล็อกกำไร" in pos, pos)
        op = txt(page, '#portsSum [data-sum="open"]') or ""
        check(f"{tag} B10 ช่องชั้น 2: 'ตอนนี้ … ถ้าบันไดเต็ม …' + แถบ 2 ชั้น + ขีดเหลือง 15%", "ตอนนี้" in op and "ถ้าบันไดเต็ม" in op and page.locator('#portsSum [data-sum-bar2] i.now').count() == 1 and page.locator('#portsSum [data-sum-bar2] i.res').count() == 1 and page.locator('#portsSum [data-sum-bar2] b').count() == 1, op)
        gt = txt(page, '#portsSum [data-sum="gate"]') or ""
        check(f"{tag} B10 ช่องใหม่ 'ประตูบันได L' + ข้อความข้อ f ('แดง ≥ 2 สัปดาห์ · เปิดได้')", "ประตูบันได L" in gt and "แดง ≥ 2 สัปดาห์ · เปิดได้" in gt, gt)
        shot(page, f"7e2b1-sum-wl-bar-{w}.png")
        shot(page, f"7e2b1-acct-head-{w}.png")
        hd = head(page, "main") or ""
        check(f"{tag} B10 หัวบัญชีมี 'L x% / 30%' + 'บันไดใหม่: เปิด' (ประตู f เปิด)", "L 19.98% / 30%" in hd and "บันไดใหม่: เปิด" in hd, hd)
        # ลบแผน L → จองคืน
        page.evaluate("(id)=>coreDelAsk(id)", "l2"); page.click("[data-del-ok]"); page.wait_for_timeout(500)
        f2 = jq(page, "()=>coreCtx('main').split.cashFree")
        check(f"{tag} B8 ลบแผนบันไดที่จอง (69,930) → เงินว่างเพิ่มเท่าเงินจอง = 530,070", abs(f2 - 530070) < 1e-6, str(f2))
    finally:
        browser.close()
    # B8 เทียบสเปก: W 100,000 + L จอง 69,930 → 530,070 · L ออกหมด → 600,000
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[usT("t_w", "WWW", 1000, 100, 90)]), cards={"l2": lcard("l2", ticker="YYY")}, ff=FF_OPEN())
    try:
        go(page)
        c1 = jq(page, "()=>coreCtx('main').cashTHB")
        page.evaluate("(id)=>coreDelAsk(id)", "l2"); page.click("[data-del-ok]"); page.wait_for_timeout(500)
        c2 = jq(page, "()=>coreCtx('main').cashTHB")
        check(f"{tag} B8 W ถือ 100,000 + L จองเต็ม 69,930 → เงินว่าง 530,070 · L ออกหมด → 600,000", abs(c1 - 530070) < 1e-6 and abs(c2 - 600000) < 1e-6, f"{c1} {c2}")
    finally:
        browser.close()
    # B9: ไม้แรก W ตอนมีบันไดจอง
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[usT("t_big", "BIG", 1, 600070, 500000)]), cards={"l2": lcard("l2", ticker="YYY")}, ff=ffj(True, True, True, True))
    try:
        go(page)
        free = jq(page, "()=>coreCtx('main').cashTHB")
        page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.fill("#cnTicker", "NEWW"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.click('#cnF button[data-f="1"]'); page.wait_for_timeout(120)
        q = txt(page, "#cnRes [data-c-qty]"); tg = txt(page, "#cnRes [data-c-tag]")
        check(f"{tag} B9 ไม้แรก W ตอนมีบันไดจอง: เงินว่างเหลือ 30,000 → Entry 100 · Stop 90 · f 100% → 300 หุ้น + 'เงินสดคุม'", abs(free - 30000) < 1e-6 and q == "300" and tg == "เงินสดคุม", f"{free} {q} {tg}")
    finally:
        browser.close()


def gate_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    cases = [("[75%, 75%] → เปิด", FF_75_75(), True, "แดง ≥ 2 สัปดาห์ · เปิดได้"),
             ("[75%, ไม่มี prev] → แดง 1 สัปดาห์ · ยังไม่เปิด", FF_75_NOPREV(), False, "แดง 1 สัปดาห์ · ยังไม่เปิด"),
             ("[100%] → งด", FF_GREEN(), False, "FF เขียว · งดเปิดบันไดใหม่"),
             ("ไฟล์เก่า → ไม่ทราบ (ไม่ใช่ 100%)", ffj(False, True, False, True, days_old=12), False, "ไม่ทราบ (ไฟล์เก่า/ไม่มีข้อมูล)"),
             ("demo (ไม่มี fundflow.json) → ไม่ทราบ", None, False, "ไม่ทราบ (ไฟล์เก่า/ไม่มีข้อมูล)")]
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        for nm, j, openg, want in cases:
            set_ff(page, j)
            page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
            page.fill("#cnTicker", "GGG"); page.click("#cnTierA"); page.fill("#cnReason", "x"); page.click("#cnStratL")
            page.fill("#cnLv0", "100"); page.fill("#cnLv1", "90"); page.click("#cnLadd"); page.fill("#cnLv2", "80"); page.fill("#cnLsl", "70"); page.wait_for_timeout(120)
            g = gate_row(page, "gate"); dis = page.is_disabled("#cnSave")
            hd = head(page, "main", "[data-c-gate]") or ""
            check(f"{tag} C11 FF {nm}: ข้อ 'ประตู FF' = '{want}' · ปุ่มล็อกแผน {'เปิด' if openg else 'ปิด'} · หัวบัญชี {'บันไดใหม่: เปิด' if openg else 'งด'}",
                  g and want in g["t"] and (g["ok"] == "1") == openg and dis == (not openg) and (("บันไดใหม่: เปิด" in hd) == openg) and (openg or ("งด" in hd and want in hd)), json.dumps([g, dis, hd], ensure_ascii=False))
            page.evaluate("()=>coreSheetClose()")
    finally:
        browser.close()
    # C12 ชั้น 2 รวมบันไดใหม่
    for risk_txt, px, exp_ok, pctTxt in (("130,000 (18.6%)", 200, False, "20.8"), ("100,000 (14.3%)", 170, True, "16.5")):
        trades = [usT("t_w", "WWW", 1000, px, 70)]
        cards = {"w1": p24.card("w1", "main", "WWW", market="US", status="open", trade_id="t_w", stop=70, tier="B", px=px, pxDate=TODAY, plan=None,
                                lots=[{"n": 1, "date": "2026-10-01", "px": px, "qty": 1000, "f": 1, "stop": 70}])}
        browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=trades), cards=cards, ff=FF_OPEN())
        try:
            go(page); open_form(page, "GGG", acct="main")
            g = gate_row(page, "l2")
            if not exp_ok:
                page.locator("#cnSave").scroll_into_view_if_needed(); page.wait_for_timeout(200)
                vis = jq(page, "()=>{ const g=document.querySelector('#cnLgates').getBoundingClientRect(), b=document.querySelector('#cnSave').getBoundingClientRect(); return g.top>=0 && g.bottom<=innerHeight && b.top>=0 && b.bottom<=innerHeight; }")
                check(f"{tag} fix3 ภาพ ladder-form-gates-fail (ชั้น 2 20.8% ✗): รายการประตู + ปุ่มล็อกแผนอยู่ในจอ", vis)
                shot(page, f"7e2b1-ladder-form-gates-fail-{w}.png")
            check(f"{tag} C12 ถือเสี่ยง {risk_txt} + บันไดใหม่ 2.24% = {pctTxt}% → ข้อชั้น 2 {'✓' if exp_ok else '✗'} · ล็อกแผน {'ได้' if exp_ok else 'ไม่ได้'}",
                  g and (g["ok"] == "1") == exp_ok and f"{pctTxt}" in g["t"] and page.is_disabled("#cnSave") == (not exp_ok), json.dumps(g, ensure_ascii=False))
        finally:
            browser.close()
    # C13 L รวมเกิน 30% · เงินสดไม่พอ
    cards = {"x1": lcard("x1", ticker="XA", bud=0.125), "x2": lcard("x2", ticker="XB", bud=0.125)}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards=cards, ff=FF_OPEN())
    try:
        go(page); open_form(page, "GGG", acct="main")
        g = gate_row(page, "share")
        check(f"{tag} C13 มีบันไดอื่นจองอยู่ ~25% + ใหม่ 10% → 'L รวม 34.97% ≤ 30%' ✗ · ล็อกแผนไม่ได้", g and g["ok"] == "0" and "34.97% ≤ 30%" in g["t"] and page.is_disabled("#cnSave"), json.dumps(g, ensure_ascii=False))
    finally:
        browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[usT("t_big", "BIG", 1, 650000, 600000)]), ff=FF_OPEN())
    try:
        go(page); open_form(page, "GGG", acct="main")
        g = gate_row(page, "cash")
        check(f"{tag} C13 เงินสดไม่พอ (ว่าง 50,000 < 69,930) → ✗ 'เงินสดว่าง ฿50,000 ≥ ฿69,930' · ล็อกแผนไม่ได้", g and g["ok"] == "0" and "฿50,000 ≥ ฿69,930" in g["t"] and page.is_disabled("#cnSave"), json.dumps(g, ensure_ascii=False))
    finally:
        browser.close()
    # C14 Tier B
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards={"wb": p24.card("wb", "main", "WBB", market="US", tier="B", plan={"entry": 100, "stop": 90}, stop=90),
                                                                             "wa": p24.card("wa", "main", "WAA", market="US", tier="A", tierReason="moat", plan={"entry": 100, "stop": 90}, stop=90)}, ff=FF_OPEN())
    try:
        go(page)
        page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.fill("#cnTicker", "TBB")
        check(f"{tag} C14 Tier B (คำนวณว่าง = B) → ปุ่ม 'ถัวตามแนวรับ (L)' ในฟอร์มปิด + 'L ใช้ได้เฉพาะ A-Fortress'", page.is_disabled("#cnStratL") and "L ใช้ได้เฉพาะ A-Fortress" in (txt(page, "#cnStratMsg") or ""))
        page.click("#cnTierA"); page.wait_for_timeout(60)
        check(f"{tag} C14 เลือก Tier A → ปุ่ม L เปิดใช้ได้", not page.is_disabled("#cnStratL"))
        page.evaluate("()=>coreSheetClose()")
        ex(page, "wb"); page.click(card_sel("wb") + " [data-c-more]")
        it = page.locator(card_sel("wb") + ' .ccMenu [data-c-strat="L"]')
        check(f"{tag} C14 ⋯ ของการ์ด W Tier B: เมนู L ปิด + 'L ใช้ได้เฉพาะ A-Fortress'", it.is_disabled() and "L ใช้ได้เฉพาะ A-Fortress" in it.inner_text())
        page.keyboard.press("Escape")
        ex(page, "wa"); page.click(card_sel("wa") + " [data-c-more]")
        it = page.locator(card_sel("wa") + ' .ccMenu [data-c-strat="L"]')
        check(f"{tag} C14 ⋯ ของการ์ด W plan Tier A: 'เปลี่ยนเป็นถัวตามแนวรับ (L)' ใช้ได้ · ปุ่ม Tier 2 ปุ่มเดิมเหลือ 'Tier…' ปุ่มเดียว",
              not it.is_disabled() and "เปลี่ยนเป็นถัวตามแนวรับ (L)" in it.inner_text() and page.locator(card_sel("wa") + " .ccMenu [data-c-tierbtn]").count() == 1 and (page.locator(card_sel("wa") + " .ccMenu [data-c-tierbtn]").inner_text() == "Tier…"))
    finally:
        browser.close()
    # C15 แก้แผนบันได ตอน f เขียว
    cards = {"e1": lcard("e1", ticker="EDT")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards=cards, ff=FF_GREEN())
    try:
        go(page)
        page.evaluate("()=>coreLEditOpen('e1')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.wait_for_timeout(150)
        gates = jq(page, "()=>[...document.querySelectorAll('#cnLgates [data-gate]')].map(e=>[e.dataset.gate,e.dataset.ok,e.innerText.replace(/\\s+/g,' ').trim()])")
        gd = {g[0]: g for g in gates}
        check(f"{tag} C15 แก้แผนบันไดตอน f เขียว → ไม่ติดประตู f (ข้อ f ไม่นับ · ติดแค่ 4 ข้อที่เหลือ) · บันทึกได้", gd["gate"][1] == "1" and "ไม่เช็กตอนแก้แผน" in gd["gate"][2] and all(gd[k][1] == "1" for k in ("tier", "share", "l2", "cash")) and not page.is_disabled("#cnSave") and txt(page, "#cnSave") == "บันทึกแผนใหม่", json.dumps(gates, ensure_ascii=False))
        check(f"{tag} C15 ฟอร์มแก้ เติมค่าเก่า (100/90/80 · SL 70 · งบ 10) · ช่อง ticker/บัญชีล็อก · ไม่มีบล็อก Tier/กลยุทธ์", page.input_value("#cnLv0") == "100" and page.input_value("#cnLv2") == "80" and page.input_value("#cnLsl") == "70" and page.input_value("#cnLbud") == "10" and page.get_attribute("#cnTicker", "readonly") is not None and not page.locator("#cnTierBox").is_visible() and not page.locator("#cnStratBox").is_visible())
        page.fill("#cnLsl", "60"); page.fill("#cnLv0", "105"); page.wait_for_timeout(100)
        page.click("#cnSave"); page.wait_for_timeout(500)
        c = db_card(page, "e1")
        check(f"{tag} C15 บันทึกแผนใหม่ (SL ลงได้เพราะยังไม่ซื้อ): ladder.sl 60 · stop 60 · L1 105 · ยัง plan", c["ladder"]["sl"] == 60 and c["stop"] == 60 and c["ladder"]["levels"][0]["px"] == 105 and c["status"] == "plan", json.dumps(c["ladder"]))
        # ตัดบันไดตัวเองออก: เงินสดที่จองไว้ของตัวเองไม่ถูกนับซ้ำ → ถ้านับซ้ำจะไม่ผ่านเมื่อเงินว่างไม่พอ 2 ชุด
    finally:
        browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[usT("t_big", "BIG", 1, 560000, 500000)]), cards={"e1": lcard("e1", ticker="EDT")}, ff=FF_GREEN())
    try:
        go(page)
        page.evaluate("()=>coreLEditOpen('e1')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]'); page.wait_for_timeout(150)
        g = gate_row(page, "cash")
        check(f"{tag} C15 แก้แผนคิดใหม่โดยตัดบันไดตัวเองออก: ถือ 560,000 + จองเดิม 69,930 → เงินว่างคิด 140,000 (ไม่หักของตัวเอง) ≥ 69,930 ✓", g and g["ok"] == "1" and "฿140,000" in g["t"], json.dumps(g, ensure_ascii=False))
    finally:
        browser.close()
    # C16 RISK_OVER / ZERO_LOT
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        open_form(page, "RRR", acct="main", sl=20)
        tot = txt(page, "#cnLres [data-c-ltot]") or ""
        check(f"{tag} C16 RISK_OVER (SL 20 → เสี่ยงเต็ม 7.78% > 2.5%) → เตือนแดง 'เกิน 2.5% — ลดงบหรือยก SL' · ล็อกแผนได้ (ไม่บล็อก)",
              page.locator("#cnLres [data-c-riskover]").count() == 1 and "เกิน 2.5% — ลดงบหรือยก SL" in tot and not page.is_disabled("#cnSave"), tot)
        page.fill("#cnLsl", "70"); page.fill("#cnLbud", "0.01"); page.wait_for_timeout(120)
        er = txt(page, "#cnErr") or ""
        check(f"{tag} C16 ZERO_LOT (งบ 0.01%) → 'L1 ได้ 0 หุ้น — เพิ่มงบหรือลดจำนวนระดับ' · ล็อกแผนไม่ได้", "L1 ได้ 0 หุ้น — เพิ่มงบหรือลดจำนวนระดับ" in er and page.is_disabled("#cnSave"), er)
        page.fill("#cnLbud", "10"); page.fill("#cnLv1", "95"); page.fill("#cnLv2", "96"); page.wait_for_timeout(100)
        er = txt(page, "#cnErr") or ""
        check(f"{tag} C16 ระดับไม่เรียงลด → 'ระดับต้องเรียงจากสูงไปต่ำ' · ล็อกไม่ได้", "ระดับต้องเรียงจากสูงไปต่ำ" in er and page.is_disabled("#cnSave"), er)
        page.fill("#cnLv1", "90"); page.fill("#cnLv2", "80"); page.fill("#cnLsl", "85"); page.wait_for_timeout(100)
        er = txt(page, "#cnErr") or ""
        check(f"{tag} C16 SL สูงกว่าระดับ → 'ทุกระดับต้องสูงกว่า SL' · ล็อกไม่ได้", "ทุกระดับต้องสูงกว่า SL" in er and page.is_disabled("#cnSave"), er)
        page.click("#cnLdel"); page.fill("#cnLsl", "70"); page.wait_for_timeout(100)
        rws = ladder_rows(page, "#cnLres")
        check(f"{tag} C16 ลบระดับ 3 → 2 ระดับ แบ่ง 50/50 (350 / 388 หุ้น) · ข้อความแบ่งเงิน 50 / 50", txt(page, "#cnLsplit") == "แบ่งเงิน 50 / 50" and len(rws) == 2 and [r[3] for r in rws] == ["350", "388"], json.dumps(rws, ensure_ascii=False))
    finally:
        browser.close()


def tier_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.fill("#cnTicker", "TIER1"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90")
        fill_tier(page, 12.5, 1.5, 85, (False, False, False))
        check(f"{tag} D17 ROIC 12.5% · ND 1.5 · FCF 85% · FCF 3 ปี ✓ · ปันผล ✓ · Gate 5 ไม่ทั้ง 3 → 'คำนวณได้ A' · ปุ่ม A ติดเอง", "คำนวณได้ A" in tier_res(page) and "on" in (page.get_attribute("#cnTierA", "class") or ""), tier_res(page))
        shot(page, f"7e2b1-tier-block-{w}.png")
        fill_tier(page, 11.9, 1.5, 85, (None, None, None))
        r1 = tier_res(page)
        fill_tier(page, 12.5, 1.5, None, (None, None, None)); r2 = tier_res(page)
        fill_tier(page, 12.5, 1.5, 85, (True, None, None)); r3 = tier_res(page)
        check(f"{tag} D17 11.9% → B (ROIC ≤ 12%) · ขาด FCF → B · Gate 5 ใช่ 1 ข้อ → B พร้อมเหตุผล", "คำนวณได้ B" in r1 and "ROIC ≤ 12%" in r1 and "คำนวณได้ B" in r2 and "FCF conv" in r2 and "คำนวณได้ B" in r3 and "Gate 5 ข้อ 1 = ใช่" in r3, " | ".join([r1, r2, r3]))
        fill_tier(page, 12.5, 1.5, 85, (True, True, False))
        fill_tier(page, 10, 1.5, 85, (False, True, None))
        rr = tier_res(page)
        fl = txt(page, '[data-c-lensline="fortress"]') or ""
        check(f"{tag} D17 ข้อความไม่ผ่านครบ (TIER2: บรรทัด Fortress): 'Fortress: ✗ ROIC ≤ 12% · Gate 5 ข้อ 2 = ใช่ · Gate 5 ยังไม่ตอบ 1 ข้อ' + บรรทัดรวม 'คำนวณได้ B'", fl == "Fortress: ✗ ROIC ≤ 12% · Gate 5 ข้อ 2 = ใช่ · Gate 5 ยังไม่ตอบ 1 ข้อ" and (txt(page, "[data-c-lenssum]") or "") == "คำนวณได้ B", rr)
        # D18 override
        fill_tier(page, None, None, None, (None, None, None))
        page.click("#cnTierA"); page.wait_for_timeout(80)
        check(f"{tag} D18 คำนวณได้ B + เลือก A ไม่มีเหตุผล → ช่องเหตุผลโผล่ · บันทึกไม่ได้", page.locator("#cnReasonBox").is_visible() and page.is_disabled("#cnSave"))
        page.fill("#cnReason", "moat แข็ง ROIC ต่ำเพราะลงทุนขยาย"); page.wait_for_timeout(80)
        check(f"{tag} D18 มีเหตุผล → บันทึกได้", not page.is_disabled("#cnSave"))
        page.click("#cnSave"); page.wait_for_timeout(500)
        k, c = p24.one_card(page, "TIER1")
        check(f"{tag} D18 เก็บ tier A · tierComputed B · tierReason · tierInputs (เศษส่วน/ค่า null)", c and c["tier"] == "A" and c["tierComputed"] == "B" and c["tierReason"] == "moat แข็ง ROIC ต่ำเพราะลงทุนขยาย" and c["tierInputs"]["roic"] is None and c["tierInputs"]["gate5"]["substitute"] is None, json.dumps(c, ensure_ascii=False))
        page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.fill("#cnTicker", "TIER2"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90")
        fill_tier(page, 15, 1, 90, (False, False, False))
        page.click("#cnTierB"); page.wait_for_timeout(80)
        check(f"{tag} D18 คำนวณได้ A เลือก B → ไม่ต้องมีเหตุผล · บันทึกได้", not page.locator("#cnReasonBox").is_visible() and not page.is_disabled("#cnSave"))
        page.click("#cnSave"); page.wait_for_timeout(500)
        k2, c2 = p24.one_card(page, "TIER2")
        check(f"{tag} D18 เก็บ tier B · tierComputed A · tierReason null · tierInputs roic 0.15 · fcfConv 0.9 · gate5 ไม่ทั้ง 3", c2 and c2["tier"] == "B" and c2["tierComputed"] == "A" and c2["tierReason"] is None and abs(c2["tierInputs"]["roic"] - 0.15) < 1e-12 and abs(c2["tierInputs"]["fcfConv"] - 0.9) < 1e-12 and c2["tierInputs"]["gate5"] == {"substitute": False, "customerMigrating": False, "singleProduct": False}, json.dumps(c2, ensure_ascii=False))
    finally:
        browser.close()
    # D19 การ์ดเก่าไม่มี tierInputs
    old = p24.card("old", "main", "OLDX", market="US", tier="A", tierReason="moat เดิม", plan={"entry": 100, "stop": 90}, stop=90)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards={"old": old}, ff=FF_OPEN())
    try:
        go(page)
        chip = txt(page, card_sel("old") + " [data-c-tier]") or ""
        check(f"{tag} D19 การ์ดเก่าไม่มี tierInputs ยังแสดง Tier เดิม (ชิป 'Tier A…' + บรรทัด FF 'เพดานไม้แรก 10%' · UX2) + ชิป 'Tier A · มีเหตุผล'", "Tier A" in chip and "เพดานไม้แรก 10%" in (txt(page, card_sel("old") + " [data-c-ff]") or "") and page.locator(card_sel("old") + " [data-c-reason-chip]").count() == 1, chip)   # UX2: เพดานไม้แรกย้ายจากชิปไปบรรทัด FF
        before = json.dumps(db_card(page, "old"), sort_keys=True)
        p24.menu_click(page, "old", "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
        blank = all(page.input_value(s) == "" for s in ("#tiRoic", "#tiNd", "#tiFcf"))
        check(f"{tag} D19 'Tier…' → ช่องตัวเลขว่าง · ปุ่ม A ติด · เหตุผลเดิมถูกเติมให้ ('moat เดิม')", blank and page.input_value("#cnReason") == "moat เดิม" and "on" in (page.get_attribute("#cnTierA", "class") or ""), page.input_value("#cnReason"))
        shot(page, f"7e2b1-tier-block-sheet-{w}.png")
        page.click('.core-sheet .ccFoot button:has-text("ยกเลิก")'); page.wait_for_timeout(300)
        after = json.dumps(db_card(page, "old"), sort_keys=True)
        check(f"{tag} D19 เปิด 'Tier…' แล้วปิดโดยไม่บันทึก = ไม่มีอะไรเปลี่ยน (เอกสารเดิมทุกฟิลด์รวม updated_at)", before == after)
        # ลด A → B ได้เสมอ
        p24.menu_click(page, "old", "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
        page.click("#cnTierB"); page.wait_for_timeout(80); ok = not page.is_disabled("#ctSave")
        page.click("#ctSave"); page.wait_for_timeout(500)
        c = db_card(page, "old")
        check(f"{tag} D19 ลด A → B บันทึกได้เสมอ (ไม่ต้องมีเหตุผล) · tier B · tierReason null", ok and c["tier"] == "B" and c["tierReason"] is None and c["tierComputed"] == "B", json.dumps(c, ensure_ascii=False))
        p24.menu_click(page, "old", "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
        page.click("#cnTierA"); page.wait_for_timeout(80)
        dis = page.is_disabled("#ctSave")
        page.fill("#cnReason", "ยกกลับ"); page.wait_for_timeout(60)
        check(f"{tag} D19 ยก B → A ตอนคำนวณได้ B ต้องมีเหตุผล (ว่าง = บันทึกไม่ได้ · มี = ได้)", dis and not page.is_disabled("#ctSave"))
    finally:
        browser.close()
    # D20 L ถูกลดเป็น B
    cards = {"lp": lcard("lp", ticker="LPP"), "lo": lopen("lo", ticker="LOO")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[ltrade("lo", "LOO")]), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        for id in ("lp", "lo"):
            p24.menu_click(page, id, "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
            page.click("#cnTierB"); page.wait_for_timeout(60); page.click("#ctSave"); page.wait_for_timeout(500)
        chip = txt(page, card_sel("lo") + " [data-c-tier]") or ""
        check(f"{tag} D20 การ์ด L ถูกลดเป็น B → ชิปเทา 'Tier B · บันไดเดิมทำงานต่อจนออก' · ป้ายแถว B·L", "Tier B · บันไดเดิมทำงานต่อจนออก" in chip and "B·L" in (txt(page, card_sel("lo") + " [data-c-row]") or "") and page.locator(card_sel("lo") + " [data-c-tier].nt").count() == 1, chip)
        ex(page, "lo")
        check(f"{tag} D20 L ที่ถูกลดเป็น B ยังซื้อระดับที่เหลือได้ (ปุ่ม 'บันทึกซื้อ L2' ใช้ได้) · เลื่อน Stop ได้", txt(page, card_sel("lo") + " [data-c-lbuy]") == "บันทึกซื้อ L2" and not page.is_disabled(card_sel("lo") + " [data-c-lbuy]") and not page.is_disabled(card_sel("lo") + " [data-c-stop-btn]"))
        page.click(card_sel("lo") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]'); page.click("#clSave"); page.wait_for_timeout(500)
        check(f"{tag} D20 ซื้อ L2 ตอน Tier B สำเร็จ (ระดับ bought)", db_card(page, "lo")["ladder"]["levels"][1]["status"] == "bought")
        ex(page, "lp")
        check(f"{tag} D20 'แก้แผนบันได' ปิด (ต้องเป็น Tier A) บนแผน L ที่ลดเป็น B · ปุ่มซื้อ L1 ยังใช้ได้", page.is_disabled(card_sel("lp") + " [data-c-ledit]") and "Tier A" in (txt(page, card_sel("lp") + " [data-c-ledit-note]") or "") and not page.is_disabled(card_sel("lp") + " [data-c-lbuy]"))
    finally:
        browser.close()


def behave_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    # E21 ไม่มี 🟡 / ไม่มี EMA10
    cards = {"lo": lopen("lo", ticker="LOO", px=95, emaW=110)}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[ltrade("lo", "LOO")]), cards=cards, ff=FF_OPEN())
    try:
        go(page); ex(page, "lo")
        st = page.get_attribute(card_sel("lo"), "data-status")
        body = txt(page, card_sel("lo") + " .ccBody") or ""
        check(f"{tag} E21 L: ปิด 95 < EMA10 (110 ใน fixture) ก็ไม่เหลือง → 🟢 · ไม่มีคำว่า EMA10 ทั้งการ์ด", st == "green" and "EMA10" not in body and "EMA10" not in (txt(page, card_sel("lo") + " [data-c-row]") or ""), f"{st} {body[:200]}")
        page.click(card_sel("lo") + " [data-c-px-btn]"); page.wait_for_selector('.core-sheet [data-core-sheet="px"]')
        check(f"{tag} E21 sheet อัปเดตราคาของ L ไม่มีช่อง EMA10", page.locator("#cpxEma").count() == 0 and "EMA10" not in (txt(page, '[data-core-sheet="px"]') or ""))
        page.fill("#cpxPx", "99"); page.click("#cpxSave"); page.wait_for_timeout(500)
        c = db_card(page, "lo")
        check(f"{tag} E21 บันทึกราคา → px 99 · emaW null", c["px"] == 99 and c["emaW"] is None, json.dumps({"px": c["px"], "emaW": c["emaW"]}))
        # ปิดต่ำกว่า Stop → 🔴 (ไม่ใช่เหลือง)
        page.evaluate("(d)=>coreWrite('lo',{px:60,pxDate:d})", TODAY); page.wait_for_timeout(400)
        check(f"{tag} E21 ปิด 60 < Stop 70 → 🔴 ขยายเอง · ปุ่มแรก 'ปิดตำแหน่ง' + 'อัปเดตราคา' (เหมือน W) · ไม่มีปุ่มซื้อระดับ", page.get_attribute(card_sel("lo"), "data-status") == "red" and page.locator(card_sel("lo") + " [data-c-close-btn].pri.dn").count() == 1 and page.locator(card_sel("lo") + " [data-c-px-btn]").count() == 1 and page.locator(card_sel("lo") + " [data-c-lbuy]").count() == 0 and page.get_attribute(card_sel("lo") + " [data-c-row]", "aria-expanded") == "true")
        page.evaluate("(d)=>coreWrite('lo',{px:null,pxDate:null})", TODAY); page.wait_for_timeout(400)
        check(f"{tag} E21 ไม่มีราคา → ⚪ แต่ไม่บล็อกการซื้อระดับ (ปุ่ม 'บันทึกซื้อ L2' ใช้ได้) · ข้อความ 'อัปเดตราคา'", page.get_attribute(card_sel("lo"), "data-status") == "na" and not page.is_disabled(card_sel("lo") + " [data-c-lbuy]") and "อัปเดตราคา" in (txt(page, card_sel("lo") + " .ccBody") or ""))
    finally:
        browser.close()
    # E22 สลับกลยุทธ์
    cards = {"wa": p24.card("wa", "main", "WAA", market="US", tier="A", tierReason="moat", plan={"entry": 100, "stop": 90}, stop=90),
             "lp": lcard("lp", ticker="LPP"), "wo": p24.card("wo", "main", "WOO", market="US", status="open", trade_id="t_wo", stop=90, tier="A", tierReason="x", px=110, pxDate=TODAY, plan=None,
                                                             lots=[{"n": 1, "date": "2026-10-01", "px": 100, "qty": 10, "f": 1, "stop": 90}]), "lo": lopen("lo", ticker="LOO")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[usT("t_wo", "WOO", 10, 100, 90), ltrade("lo", "LOO")]), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        p24.menu_click(page, "wa", '[data-c-strat="L"]'); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        check(f"{tag} E22 W plan Tier A → 'เปลี่ยนเป็นถัวตามแนวรับ (L)' เปิดฟอร์ม L พร้อม ticker/บัญชีเดิม (ล็อก)", page.input_value("#cnTicker") == "WAA" and page.get_attribute("#cnTicker", "readonly") is not None and page.locator("#cnLBox").is_visible() and "ถัวตามแนวรับ" in (txt(page, ".core-sheet h3") or ""))
        page.fill("#cnLv0", "100"); page.fill("#cnLv1", "90"); page.fill("#cnLsl", "70"); page.wait_for_timeout(120)
        check(f"{tag} E22 ฟอร์มแปลง: Tier A เดิม · ประตูผ่าน → บันทึกได้", not page.is_disabled("#cnSave"))
        page.click("#cnSave"); page.wait_for_timeout(500)
        c = db_card(page, "wa")
        check(f"{tag} E22 บันทึก = แปลงการ์ดเดิม: strategy L · plan null · ladder 2 ระดับ (50/50) · stop 70 · ไม่สร้างการ์ดใหม่ · tier A คงเดิม",
              c["strategy"] == "L" and c["plan"] is None and c["ladder"]["split"] == [0.5, 0.5] and c["stop"] == 70 and c["tier"] == "A" and sum(1 for x in p24.cards_db(page).values() if x["ticker"] == "WAA") == 1, json.dumps(c, ensure_ascii=False))
        res0 = jq(page, "()=>coreCtx('main').split.lReserved")
        p24.menu_click(page, "lp", '[data-c-strat="W"]'); page.wait_for_selector('.core-sheet [data-core-sheet="tow"]')
        check(f"{tag} E22 L plan → 'เปลี่ยนเป็นระบบ Week': Entry เริ่ม = L1 (100) · Stop เริ่ม = SL (70)", page.input_value("#c2wEntry") == "100" and page.input_value("#c2wStop") == "70")
        page.click("#c2wSave"); page.wait_for_timeout(500)
        c = db_card(page, "lp"); res1 = jq(page, "()=>coreCtx('main').split.lReserved")
        check(f"{tag} E22 แปลงเป็น W: strategy W · plan {{entry 100, stop 70}} · ladder null · เงินจองคืนทันที (จองลด 69,930)", c["strategy"] == "W" and c["plan"] == {"entry": 100, "stop": 70} and c["ladder"] is None and abs((res0 - res1) - 69930) < 1e-6, json.dumps(c, ensure_ascii=False) + f" {res0}->{res1}")
        ex(page, "wo"); page.click(card_sel("wo") + " [data-c-more]")
        a = page.locator(card_sel("wo") + ' .ccMenu [data-c-strat="L"]'); a_t = a.inner_text(); a_d = a.is_disabled()
        page.keyboard.press("Escape")
        ex(page, "lo"); page.click(card_sel("lo") + " [data-c-more]")
        b = page.locator(card_sel("lo") + " .ccMenu [data-c-strat]"); b_t = b.inner_text(); b_d = b.is_disabled()
        check(f"{tag} E22 ซื้อแล้ว (ทั้ง W และ L) → เมนูกลยุทธ์ปิด 'ซื้อแล้ว — ล็อกกลยุทธ์'", a_d and "ซื้อแล้ว — ล็อกกลยุทธ์" in a_t and b_d and "ซื้อแล้ว — ล็อกกลยุทธ์" in b_t, f"{a_t} | {b_t}")
        # ไม่มี แก้ Entry/SL ในการ์ด L
        check(f"{tag} E22 การ์ด L (open) ไม่มี 'แก้ Entry/SL' ในเมนู ⋯ · มี 'ยกเลิกระดับที่จอง…' · 'ดูไม้ที่ซื้อ' · 'ปิดตำแหน่ง' · 'Tier…'",
              page.locator(card_sel("lo") + " .ccMenu [data-c-edit-btn]").count() == 0 and all(page.locator(card_sel("lo") + f" .ccMenu {s}").count() == 1 for s in ("[data-c-lcancel-btn]", "[data-c-lots-btn]", "[data-c-close-btn]", "[data-c-tierbtn]")))
    finally:
        browser.close()
    # E23 ตัด f ซ้ำ
    for nm, j, stale in (("Fund-flow เก่า", ffj(True, True, days_old=12), True), ("สด", ffj(True, True), False)):
        browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=j)
        try:
            go(page)
            hf = head(page, "main", "[data-c-f]") or ""; hw = head(page, "main", "[data-c-ffwarn]")
            page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
            sf = txt(page, "#cnFsrc") or ""; sw = txt(page, "#cnFwarn") if page.is_visible("#cnFwarn") else None
            if stale:
                check(f"{tag} E23 {nm}: หัวบัญชีมีชิปเตือน · data-c-f ไม่มี 'Fund-flow เก่า · ไม่ลด' ซ้ำ (เหลือ 'FF 100%') · sheet แผนใหม่มีเตือน แต่ #cnFsrc ไม่มีที่มาซ้ำ",
                      hw and "Fund-flow เก่า" in hw and "Fund-flow เก่า" not in hf and hf.strip() == "FF 100%" and sw and "Fund-flow เก่า" in sw and "Fund-flow เก่า" not in sf and sf == "", json.dumps([hf, hw, sf, sw], ensure_ascii=False))
                page.click('#cnF button[data-f="0.75"]'); page.wait_for_timeout(80)
                sf2 = txt(page, "#cnFsrc") or ""
                check(f"{tag} E23 {nm}: ผู้ใช้เลือก f เอง → เหลือแค่ '(เลือกเอง · ระบบ 100%)'", sf2 == "(เลือกเอง · ระบบ 100%)", sf2)
            else:
                check(f"{tag} E23 {nm}: ไม่มีชิปเตือน · data-c-f มีที่มาตามเดิม ('เขียวทั้งคู่') · sheet มี '(เขียวทั้งคู่)'", hw is None and "เขียวทั้งคู่" in hf and "เขียวทั้งคู่" in sf, json.dumps([hf, hw, sf], ensure_ascii=False))
        finally:
            browser.close()
    # E24 เมนู ⋯ ของการ์ด L มองเห็นจริง
    cards = {"lo": lopen("lo", ticker="LOO"), "lp": lcard("lp", ticker="LPP"), "lp2": lcard("lp2", ticker="LQQ", bud=0.05)}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[ltrade("lo", "LOO")]), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        order = page.evaluate("()=>[...document.querySelectorAll('#corePanel [data-core-acct=\"main\"] .ccList > .ccCard')].map(e=>e.dataset.coreCard)")
        def open_menu(id, place):
            ex(page, id)
            page.evaluate("()=>document.querySelectorAll('.ccMenu.on').forEach(x=>x.classList.remove('on'))")
            b = card_sel(id) + " [data-c-more]"
            page.evaluate("([b,place])=>{ const e=document.querySelector(b); e.scrollIntoView({block:'center'}); if(place==='bottom'){ const r=e.getBoundingClientRect(); window.scrollBy(0, r.top - (innerHeight - 60)); } }", [b, place])
            page.wait_for_timeout(120)
            if place == "bottom":
                page.set_viewport_size({"width": w, "height": 700}); page.wait_for_timeout(150)
                page.evaluate("(b)=>{ const e=document.querySelector(b); e.scrollIntoView({block:'end'}); window.scrollBy(0, 30); }", b); page.wait_for_timeout(150)
                page.evaluate("(b)=>document.querySelector(b).click()", b)
            else: page.click(b)
            page.wait_for_timeout(100)
            return page.evaluate("""(c)=>{ const m=document.querySelector(c+' .ccMenu'), r=m.getBoundingClientRect();
              const items=[...m.querySelectorAll('button')]; const bad=[];
              items.forEach(i=>{ const q=i.getBoundingClientRect(), e=document.elementFromPoint(q.left+q.width/2, q.top+q.height/2); if(!(e && m.contains(e))) bad.push(i.textContent.trim().slice(0,20)); });
              return {on:m.classList.contains('on'), n:items.length, bad, l:r.left, r:r.right, t:r.top, b:r.bottom, iw:innerWidth, ih:innerHeight}; }""", card_sel(id))
        for id in (order[0], order[-1]):
            g = open_menu(id, "center")
            check(f"{tag} E24 ⋯ ของการ์ด L '{id}' ({'ใบสุดท้าย' if id == order[-1] else 'ใบแรก'}): ทุกรายการ ({g['n']}) มองเห็นจริง · ขอบเมนูอยู่ในจอทั้ง 4 ด้าน",
                  g["on"] and not g["bad"] and g["l"] >= 0 and g["r"] <= g["iw"] and g["t"] >= 0 and g["b"] <= g["ih"], json.dumps(g, ensure_ascii=False))
        page.evaluate("()=>{ const d=document.createElement('div'); d.id='spacer'; d.style.height='1500px'; document.body.appendChild(d); }")
        g2 = open_menu(order[-1], "bottom")
        check(f"{tag} E24 ⋯ ของการ์ด L ชิดล่างจอ → เมนูเปิดขึ้นบนและเห็นครบ ({g2['n']} รายการ)", g2["on"] and not g2["bad"] and g2["t"] >= 0 and g2["b"] <= g2["ih"], json.dumps(g2, ensure_ascii=False))
        page.set_viewport_size({"width": w, "height": 900})
    finally:
        browser.close()
    # E25 หน้าตา 430
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[ltrade("lo", "LOO")]), cards={"lo": lopen("lo", ticker="LOO"), "lp": lcard("lp", ticker="LPP")}, ff=FF_OPEN())
    try:
        go(page); ex(page, "lo"); ex(page, "lp")
        m = jq(page, """()=>{ const tw = document.querySelector('[data-core-card="lo"] .ccTw'), t = tw.querySelector('table');
            const btns = [...document.querySelectorAll('[data-core-card="lo"] .ccBtns .ccBtn, [data-core-card="lp"] .ccBtns .ccBtn')].filter(b=>b.offsetParent);
            return {ov:getComputedStyle(tw).overflowX, twW:tw.clientWidth, tSW:t.scrollWidth, sw:document.documentElement.scrollWidth, minH:Math.min(...btns.map(b=>b.getBoundingClientRect().height)), nb:btns.length,
              inside: t.getBoundingClientRect().right <= tw.getBoundingClientRect().right + 1 || tw.scrollWidth > tw.clientWidth}; }""")
        check(f"{tag} E25 ตารางบันไดอยู่ในกรอบ .ccTw (overflow-x auto) · {'เลื่อนแนวนอนในกรอบได้ถ้ากว้างเกิน' if w <= 700 else 'พอดีกรอบ'} · หน้าไม่ล้นแนวนอน (scrollWidth {m['sw']} ≤ {w}) · ปุ่มสูง ≥ 36px (ต่ำสุด {m['minH']:.0f})",
              m["ov"] == "auto" and m["sw"] <= w and m["minH"] >= 36 and m["inside"], json.dumps(m))
        page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.fill("#cnTicker", "FFF"); page.click("#cnTierA"); page.fill("#cnReason", "x"); page.click("#cnStratL")
        page.fill("#cnLv0", "100"); page.fill("#cnLv1", "90"); page.fill("#cnLsl", "70"); page.wait_for_timeout(120)
        m2 = jq(page, """()=>({sw:document.documentElement.scrollWidth, shw:document.querySelector('.core-sheet .ccSh').scrollWidth, shc:document.querySelector('.core-sheet .ccSh').clientWidth,
            tw:getComputedStyle(document.querySelector('#cnLres .ccTw')).overflowX})""")
        check(f"{tag} E25 ฟอร์มบันไดใน sheet: หน้าไม่ล้นแนวนอน · ตารางอยู่ในกรอบเลื่อนได้", m2["sw"] <= w and m2["shw"] <= m2["shc"] + 1 and m2["tw"] == "auto", json.dumps(m2))
    finally:
        browser.close()
    check(f"{tag} ไม่มี console error / pageerror (ชุด behave)", True)


def fix_checks(pw, w, h, label):
    """7E-2b-1-fix: ช่องชั้น 2 มองเห็น 'ถ้าบันไดเต็ม y%' ครบ · สกุลเงินใน sheet เลื่อน Stop"""
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[ltrade("l1")]), cards={"l1": lopen("l1")}, ff=FF_OPEN())
    try:
        go(page)
        page.locator('#portsSum [data-sum="open"]').scroll_into_view_if_needed(); page.wait_for_timeout(200)
        r = jq(page, """()=>{ const cell=document.querySelector('#portsSum [data-sum="open"]'), full=cell.querySelector('[data-sum-full]'), b=full.querySelector('b');
            const cr=cell.getBoundingClientRect(), fr=full.getBoundingClientRect(), br=b.getBoundingClientRect();
            const els=[cell,...cell.querySelectorAll('*')]; const bad=els.filter(e=>e.scrollWidth>e.clientWidth+1 && e.clientWidth>0).map(e=>e.tagName+'.'+e.className);
            const x=br.left+br.width/2, y=br.top+br.height/2, top=document.elementFromPoint(x,y);
            return {txt:full.innerText.replace(/\\s+/g,' '), inBox: fr.left>=cr.left-0.5 && fr.right<=cr.right+0.5 && br.right<=cr.right+0.5 && fr.width>0, bad, hit: top===b || b.contains(top) || (top && top.closest('[data-sum-full]')===full), val:b.innerText}; }""")
        check(f"{tag} fix1 ช่องชั้น 2 (บล็อกสรุป): 'ถ้าบันไดเต็ม 2.1% / 20%' อยู่บรรทัดใต้ 'ตอนนี้' ครบ · กล่องไม่เกินขอบช่อง · ไม่มี element ที่ scrollWidth > clientWidth · elementFromPoint กลางตัวเลข = ตัวเลขนั้น",
              "ถ้าบันไดเต็ม" in r["txt"] and r["val"] == "2.1" and "/ 20%" in r["txt"] and r["inBox"] and not r["bad"] and r["hit"], json.dumps(r, ensure_ascii=False))
        shot(page, f"7e2b1-sum-l2-cell-{w}.png")
    finally:
        browser.close()
    if w != 430: return
    # สกุลเงินใน sheet เลื่อน Stop / ยกเลิกระดับ — TH
    th_lv = [{"px": 100, "status": "bought", "qty": 200, "fillPx": 100, "boughtAt": "2026-10-05"}, {"px": 90, "status": "wait"}, {"px": 80, "status": "wait"}]
    tc = lcard("t1", acct="fam", ticker="TTT.BK", levels=th_lv, status="open", trade_id="t_t1", px=96.5, pxDate=TODAY, lots=[{"n": 1, "level": 1, "date": "2026-10-05", "px": 100, "qty": 200, "f": None, "stop": 70}])
    tt = T("t_t1", "core", "open", sym="TTT.BK", entry=100, sl=70, qty=200, cur="THB", date="2026-10-05")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(fam_trades=[tt]), cards={"t1": tc}, ff=FF_OPEN())
    try:
        go(page)
        page.evaluate("(id)=>coreStopOpen(id)", "t1"); page.wait_for_selector('.core-sheet [data-core-sheet="stop"]')
        page.fill("#csStop", "85"); page.wait_for_timeout(80)
        pv = txt(page, "[data-cs-preview]") or ""
        check(f"{tag} fix2 sheet เลื่อน Stop (TH): 'คืนเงินจอง ฿16,000' ไม่มี $", "คืนเงินจอง ฿16,000" in pv and "$" not in pv, pv)
        page.evaluate("()=>coreSheetClose()")
        p24.menu_click(page, "t1", "[data-c-lcancel-btn]"); page.wait_for_selector('.core-sheet [data-core-sheet="lcancel"]')
        page.select_option("#clcSel", "2"); page.wait_for_timeout(60)
        m = txt(page, "[data-clc-msg]") or ""
        ln = txt(page, card_sel("t1") + " [data-c-lhold]") or ""
        check(f"{tag} fix2 sheet ยกเลิกระดับ (TH): '฿16,000' ไม่มี $ · บรรทัด 'ถือ/จอง' บนการ์ด TH เป็น ฿ ล้วน", "฿16,000" in m and "$" not in m and "$" not in ln and "฿" in ln, m + " | " + ln)
    finally:
        browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[ltrade("l1")]), cards={"l1": lopen("l1")}, ff=FF_OPEN())
    try:
        go(page)
        ln = txt(page, card_sel("l1") + " [data-c-lhold]") or ""
        check(f"{tag} fix2 การ์ด L (US): 'ถือ $28,000 ≈฿28,000 · จอง $41,930 ≈฿41,930' ใช้สกุลตลาดเหมือนตาราง", "ถือ $28,000 ≈฿28,000" in ln and "จอง $41,930 ≈฿41,930" in ln, ln)
    finally:
        browser.close()


def regress_checks(pw, w, h, label):
    """E26 ไม่มีการ์ด L → ตัวเลขหัวบัญชี/บล็อกสรุปเท่าก่อนแก้ (เทียบ index.backup-pre-7E2b1.html)"""
    tag = f"[chromium/{label}]"
    trades = [usT("t_aapl", "AAPL", 78, 103.33, 90), usT("t_nvda", "NVDA", 40, 125, 120), usT("t_nc", "NOCARD", 100, 50, 45)]
    cards = {"aapl": p24.card("aapl", "main", "AAPL", market="US", status="open", trade_id="t_aapl", stop=90, tier="B", px=101, pxDate=TODAY, emaW=90, plan=None,
                              lots=[{"n": 1, "date": "2026-10-01", "px": 103.33, "qty": 78, "f": 1, "stop": 90}]),
             "nvda": p24.card("nvda", "main", "NVDA", market="US", status="open", trade_id="t_nvda", stop=120, tier="A", tierReason="m", px=118, pxDate=TODAY, plan=None,
                              lots=[{"n": 1, "date": "2026-10-01", "px": 125, "qty": 40, "f": 1, "stop": 120}]),
             "meta": p24.card("meta", "main", "META", market="US", tier="B", plan={"entry": 600, "stop": 560}, stop=560)}
    def grab(index):
        p24.INDEX = index
        browser, context, page, ce, pe, dialogs = p24.launch(pw, w, h, doc26(main_trades=trades), cards=cards, ff="green")
        try:
            go(page)
            o = page.evaluate("""()=>{ document.querySelectorAll('details[data-c-more]').forEach(d=>{ d.open = true; }); const t = s=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; };
               return {head:t('[data-core-head="main"]'), open:t('#portsSum [data-sum="open"]'), held:t('#portsSum [data-sum="held"]'), pos:t('#portsSum [data-sum="pos"]'), drop:t('#portsSum [data-sum="acctdrop"]'), foot:t('#foot')}; }""")
            o["l2"] = page.evaluate("()=>{ const r = coreAcctRisk('main'); return [r.layer2Pct, r.layer2THB, r.dropCoreTHB, r.vsCostTHB, r.missing, r.nNoCard]; }")
            o["cash"] = page.evaluate("()=>coreCtx('main').cashTHB")
            return o
        finally:
            browser.close(); p24.INDEX = INDEX
    new, old = grab(INDEX), grab(BACKUP)
    num = lambda s, pat: (re.search(pat, s or "") or [None, None])[1]
    h_new, h_old = new["head"], old["head"]
    same = [
        ("ถัง Core", num(h_new, r"ถัง Core ฿([\d,]+)") == num(h_old, r"ถัง Core ฿([\d,]+)")),
        ("เงินสดว่าง", num(h_new, r"เงินสดว่าง ฿([\d,]+)") == num(h_old, r"เงินสดว่าง ฿([\d,]+)") and new["cash"] == old["cash"]),
        ("ขาดราคา", num(h_new, r"ขาดราคา (\d+)") == num(h_old, r"ขาดราคา (\d+)")),
        ("ชั้น 2 ตอนนี้ = เดิม = เต็ม", num(h_new, r"ชั้น 2 ตอนนี้ ([\d.]+)%") == num(h_old, r"ชั้น 2 ([\d.]+)%") == num(h_new, r"เต็ม ([\d.]+)%")),
        ("ชั้น 2 / ถ้าโดน Stop / เทียบทุน (เลขดิบ)", new["l2"] == old["l2"]),
        ("ช่องความเสี่ยง ฿ · ≈% ของบัญชี", num(new["open"], r"฿([\d,]+) · ≈ ([\d.]+)% ของบัญชี") == num(old["open"], r"฿([\d,]+) · ≈ ([\d.]+)% ของบัญชี") and num(new["open"], r"≈ ([\d.]+)%") == num(old["open"], r"≈ ([\d.]+)%")),
        ("ช่องความเสี่ยง % ตอนนี้ = เดิม", num(new["open"], r"ตอนนี้ ([\d.]+)%") == num(old["open"], r"\) · % ของถัง Core ([\d.]+)%")),
        ("เงินที่ถือ ฿ · % · เงินว่าง", num(new["held"], r"฿([\d,]+)") == num(old["held"], r"฿([\d,]+)") and num(new["held"], r"เงินว่าง ฿([\d,]+)") == num(old["held"], r"เงินว่าง ฿([\d,]+)") and num(new["held"], r"([\d.]+)% ของถัง") == num(old["held"], r"([\d.]+)% ของถัง")),
        ("ตำแหน่ง n ตัว · ล็อกกำไร", num(new["pos"], r"(\d+) ตัว") == num(old["pos"], r"(\d+) ตัว") and num(new["pos"], r"ล็อกกำไร (\d+)") == num(old["pos"], r"ล็อกกำไร (\d+)")),
        ("ถ้าทุกไม้โดน Stop / เทียบทุน (ข้อความเท่าเดิมทุกตัวอักษร)", new["drop"] == old["drop"]),
        ("footer เท่าเดิม", new["foot"] == old["foot"]),
    ]
    for nm, ok in same:
        check(f"{tag} E26 ไม่มีการ์ด L → {nm} เท่าก่อนแก้", ok, json.dumps([new, old], ensure_ascii=False)[:600])


def main():
    with sync_playwright() as pw:
        core_size_checks(pw)
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            ladder_checks(pw, w, h, label)
            wl_checks(pw, w, h, label)
            gate_checks(pw, w, h, label)
            tier_checks(pw, w, h, label)
            behave_checks(pw, w, h, label)
            regress_checks(pw, w, h, label)
            fix_checks(pw, w, h, label)
        fix_checks(pw, 375, 800, "375x800")
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:400])
        sys.exit(1)


if __name__ == "__main__":
    main()
