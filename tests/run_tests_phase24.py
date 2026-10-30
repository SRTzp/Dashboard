#!/usr/bin/env python3
"""7E-2 — การ์ดตำแหน่ง Core (โหมด W) · คอลเลกชัน coreCards + listener · แผน Core ใหม่ (＋/T) · ซื้อไม้ 1/ไม้เติม · เลื่อน Stop · ราคาปิด/EMA10/ป้ายสถานะ · ชั้น 2 จากราคา · ตัด loss ออกจาก heat
mock Firestore (ไม่ต่อเน็ต · รองรับ coreCards + __denyPath) · 1440px + 430px · seed.json + ไม้/การ์ดที่ใส่เองในเทส · f ตั้งด้วย window.__FF_JSON + ffLoadJson(true)
รัน: python3 run_tests_phase24.py [/path/to/index.html] · ภาพเก็บที่ tests/screenshots/7e2a-*.png"""
import copy, datetime, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
results = []
T = p22.T
bk = p22.bkk_today_minus
TODAY = bk(0)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:600] + "...(truncated)") if (detail and len(detail) > 600) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    try:
        if sel and page.locator(sel).count():
            page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else:
            page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e:
        print("shot fail", name, e)


def ff_json(acwi_up=True, hyg_up=True, days_old=0):
    d = datetime.datetime.now() - datetime.timedelta(days=days_old)
    return {"as_of": d.strftime("%Y-%m-%d"), "ratios": {"ACWI_BIL": {"up": acwi_up}, "HYG_IEI": {"up": hyg_up}}}


def card(id, acct, ticker, **kw):
    """การ์ด coreCards (สำหรับ seed) · status open ต้องส่ง trade_id"""
    c = {"acct": acct, "ticker": ticker, "market": "TH" if ticker.endswith(".BK") else "US", "strategy": "W", "tier": "B", "tierReason": None,
         "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": None, "pxDate": None, "emaW": None, "lots": [],
         "trade_id": None, "status": "plan", "created_at": "2026-09-20T00:00:00Z", "updated_at": "2026-09-20T00:00:00Z"}
    c.update(kw); return c


def open_card(id, tid, ticker="XXX.BK", acct="main", qty=700, entry=100, sl=90, **kw):
    lots = kw.pop("lots", [{"n": 1, "date": "2026-09-10", "px": entry, "qty": qty, "f": 1, "stop": sl}])
    return card(id, acct, ticker, status="open", trade_id=tid, stop=sl, lots=lots, tier=kw.pop("tier", "A"), **kw)


def doc_with(main_trades=None, core_cap=700000, main_market="both", fam_market=None):
    doc = p22.make_doc(main_trades=main_trades if main_trades is not None else [], with_legacy=False)
    doc["books"]["main"]["settings"]["capital"]["core"] = core_cap
    doc["books"]["main"]["settings"].setdefault("coreRisk", {}).update({"riskPct": 1, "tierA": 10, "tierB": 5})   # CZ1: ค่าเริ่มต้นใหม่ (1.25/15/10) → seed ค่าเดิม ให้ตัวเลขที่คาดเท่าเดิม
    doc["books"]["main"]["settings"]["coreRisk"]["market"] = main_market
    doc["books"]["main"]["settings"]["coreRisk"]["maxLots"] = 6   # 7E-2a-fix: เติมได้หลายไม้ (ตัวเลขทุกตัวเดิม)
    if fam_market: doc["books"]["fam"]["settings"].setdefault("coreRisk", {}).update(dict({"riskPct": 1, "tierA": 10, "tierB": 5}, market=fam_market))
    return doc


def launch(pw, w, h, doc, cards=None, deny=False, ff="green"):
    lk = {"headless": True}
    if base.CHROMIUM_PATH: lk["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    context = browser.new_context(viewport={"width": w, "height": h})
    from ff_stub import FF_STUB; context.add_init_script(FF_STUB)
    page = context.new_page()
    ce, pe, dialogs = [], [], []
    page.on("console", lambda m: ce.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: pe.append(str(e)))
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))
    page.route(re.compile(r"gstatic\.com/firebasejs"), lambda r: r.fulfill(status=200, content_type="application/javascript", body=base.MOCK_FB))
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), lambda r: r.fulfill(status=200, content_type="text/css", body=""))
    page.route(re.compile(r"fundflow\.json|open\.er-api\.com|api\.twelvedata\.com"), lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto("file://" + INDEX, wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("() => localStorage.setItem('bkLastBackupAt', String(Date.now()))")
    page.evaluate("(d)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], d); }", doc)
    for cid, c in (cards or {}).items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    if deny:
        page.evaluate("()=>window.firebase.__mockDb.__denyPath(['users','testuid','coreCards'])")
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(1000)
    if ff:
        set_ff(page, ff_json(*{"green": (True, True), "red1": (False, True), "red2": (False, False)}[ff]))
    return browser, context, page, ce, pe, dialogs


def set_ff(page, j):
    page.evaluate("async (j)=>{ window.__FF_JSON = j; await ffLoadJson(true); }", j)
    page.wait_for_timeout(200)


def go_stock(page):
    page.evaluate("() => { switchTab('plan'); setPlanScope('stock'); setPlanAcct('all'); }"); page.wait_for_timeout(300)


def cards_db(page):
    return page.evaluate("() => { const d = window.firebase.__mockDb.__dump(), o = {}; Object.keys(d).forEach(k=>{ const m = k.match(/^users\\/testuid\\/coreCards\\/(.+)$/); if(m) o[m[1]] = d[k]; }); return o; }")


def one_card(page, ticker):
    for k, c in cards_db(page).items():
        if c["ticker"] == ticker: return k, c
    return None, None


def book_trades(page, acct="main"):
    return page.evaluate("(a)=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return (d.books[a] && d.books[a].trades) || []; }", acct)


def txt(page, sel):
    # CX1: หัวบัญชี Core พับชิปที่ซ้ำแผงสรุปไว้ใน details[data-c-more] — เปิดก่อนอ่านข้อความ (เนื้อหา/ตัวเลขที่ตรวจเหมือนเดิม)
    if "core-head" in sel or any(k in sel for k in ("data-c-cashfree", "data-c-l2", "data-c-lshare", "data-c-gate", "data-c-missing")):
        page.evaluate("()=>document.querySelectorAll('details[data-c-more]').forEach(d=>{ d.open = true; })")
    return page.evaluate("(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def new_plan(page, ticker, entry, stop, tier="B", reason=None, f=None, acct=None, save=False):
    """เปิด sheet แผนใหม่ผ่าน coreNewOpen แล้วกรอกช่อง"""
    page.evaluate("(a)=>coreNewOpen(a)", acct)
    page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
    page.fill("#cnTicker", ticker)
    if acct: page.select_option("#cnAcct", acct)
    page.click("#cnTierA" if tier == "A" else "#cnTierB")
    if tier == "A" and reason is not None: page.fill("#cnReason", reason)
    page.fill("#cnEntry", str(entry)); page.fill("#cnStop", str(stop))
    if f is not None: page.click(f'#cnF button[data-f="{f}"]')
    page.wait_for_timeout(100)
    if save:
        page.click("#cnSave"); page.wait_for_timeout(500)


def ex(page, id):
    """7E-2a-fix: การ์ดยุบเป็นแถว → ขยายก่อนคลิกปุ่มในการ์ด"""
    page.evaluate("(id)=>coreExpand(id)", id); page.wait_for_timeout(60)


def open_sim(page, id):
    ex(page, id)
    if not page.locator(f'[data-core-card="{id}"] [data-c-simbox]').is_visible():
        page.click(f'[data-core-card="{id}"] [data-c-addbtn]'); page.wait_for_timeout(80)


def menu_click(page, id, sel):
    ex(page, id)
    page.click(f'[data-core-card="{id}"] [data-c-more]'); page.wait_for_timeout(60)
    page.click(f'[data-core-card="{id}"] .ccMenu {sel}')


def sheet_open(page, kind): return page.locator(f'.core-sheet [data-core-sheet="{kind}"]').count() > 0


# ─────────────────────────────────────────────────────────────
def plan_sheet_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with())
    try:
        # ＋ / T
        go_stock(page)
        page.click("#hdrPlanBtn"); page.wait_for_timeout(300)
        check(f"{tag} scope หุ้น กด ＋ → เปิด sheet 'แผน Core ใหม่'", sheet_open(page, "new") and "แผน Core ใหม่" in (txt(page, ".core-sheet h3") or ""))
        page.evaluate("coreSheetClose()")
        page.evaluate("() => { switchTab('journal'); }")
        page.keyboard.press("t"); page.wait_for_timeout(300)
        check(f"{tag} scope หุ้น กด T → ไปแท็บแผน + เปิด sheet แผน Core ใหม่", sheet_open(page, "new") and page.evaluate("()=>activeTab") == "plan")
        page.evaluate("coreSheetClose()")
        page.evaluate("() => { switchTab('journal'); setPlanScope('future'); }")
        page.click("#hdrPlanBtn"); page.wait_for_timeout(300)
        check(f"{tag} scope Future กด ＋ → ไปบนสุด (เดิม) ไม่เปิด sheet", (not sheet_open(page, "new")) and page.evaluate("()=>activeTab") == "plan" and page.evaluate("()=>window.scrollY") == 0)
        page.evaluate("() => { switchTab('journal'); }")
        page.keyboard.press("t"); page.wait_for_timeout(300)
        check(f"{tag} scope Future กด T → เหมือนกัน (ไม่เปิด sheet)", (not sheet_open(page, "new")) and page.evaluate("()=>activeTab") == "plan")
        go_stock(page)

        # firstLot — บัญชี main · ถัง 700,000 · XXX.BK · Tier A · Entry 100 Stop 90
        def q(): return txt(page, "#cnRes [data-c-qty]")
        new_plan(page, "XXX.BK", 100, 90, tier="A", reason="ทดสอบ", f="1")
        check(f"{tag} f 100% → 700 · จาก 700 → ปัดหลัก 100 = 700", q() == "700" and "จาก 700 → ปัดหลัก 100 = 700" in (txt(page, "#cnRes [data-c-round]") or ""), txt(page, "#cnRes") or "")
        check(f"{tag} ทุน ฿70,000 (10% ของถัง) · เสี่ยง ฿7,000 (1% ของถัง) · ป้าย FF 100% (UX2: f→FF) · เงินสดว่าง ฿700,000",
              "฿70,000 (10% ของถัง)" in txt(page, "#cnRes [data-c-cost]") and "฿7,000 (1% ของถัง)" in txt(page, "#cnRes [data-c-cost]")
              and txt(page, "#cnRes [data-c-tag]") == "FF 100%" and "เงินสดว่าง ฿700,000" in txt(page, "#cnRes [data-c-cash]"), txt(page, "#cnRes") or "")
        page.click('#cnF button[data-f="0.75"]')
        check(f"{tag} f 75% → 525 → ปัด 500 · ป้าย FF 75% (UX2: f→FF)", q() == "500" and "จาก 525 → ปัดหลัก 100 = 500" in txt(page, "#cnRes [data-c-round]") and txt(page, "#cnRes [data-c-tag]") == "FF 75%", txt(page, "#cnRes") or "")
        page.click('#cnF button[data-f="0.5"]')
        check(f"{tag} f 50% → 350 → ปัด 300", q() == "300" and "จาก 350 → ปัดหลัก 100 = 300" in txt(page, "#cnRes [data-c-round]"), txt(page, "#cnRes") or "")
        # Tier B เพดาน 5% + Entry 100 Stop 99
        page.click("#cnTierB"); page.click('#cnF button[data-f="1"]'); page.fill("#cnStop", "99")
        check(f"{tag} Tier B เพดาน 5% (35,000) · Entry 100 Stop 99 → ชนเพดาน Tier: จาก 350 → ปัดหลัก 100 = 300 (TH)", q() == "300" and txt(page, "#cnRes [data-c-tag]") == "ชนเพดาน Tier" and "จาก 350 → ปัดหลัก 100 = 300" in txt(page, "#cnRes [data-c-round]"), txt(page, "#cnRes") or "")
        # Entry <= Stop
        page.fill("#cnEntry", "90"); page.fill("#cnStop", "100")
        check(f"{tag} Entry ≤ Stop → 'Entry ต้องมากกว่า Stop' · บันทึกไม่ได้", "Entry ต้องมากกว่า Stop" in (txt(page, "#cnRes") or "") and page.is_disabled("#cnSave"))
        # zeroLot: Tier B Entry 1000 Stop 999 f 50% → งบ 3,500 → 3 หุ้น → 0 หลัก
        page.fill("#cnEntry", "1000"); page.fill("#cnStop", "999"); page.click('#cnF button[data-f="0.5"]')
        check(f"{tag} zeroLot (ชนเพดาน Tier B) → 'ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿35,000) → ใช้ Tier A หรือข้ามตัวนี้' (7E-2a-fix §5)", "ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿35,000) → ใช้ Tier A หรือข้ามตัวนี้" in (txt(page, "#cnRes [data-c-zero]") or ""), txt(page, "#cnRes") or "")
        shot(page, f"7e2a-newplan-zero-{w}.png", ".core-sheet .ui-sheet")
        # US: ticker AAPL → ปัด 1 หุ้น · สกุล $
        page.fill("#cnTicker", "AAPL"); page.click("#cnTierA"); page.fill("#cnReason", "x"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.click('#cnF button[data-f="1"]')
        check(f"{tag} ticker US → ปัด 1 หุ้น · สกุล $ · ทุน/เสี่ยงแปลง ≈฿", txt(page, "#cnRes [data-c-qty]") == "21" and "ปัด 1 หุ้น" in txt(page, "#cnRes [data-c-round]") and "$2,100" in txt(page, "#cnRes [data-c-cost]") and "≈฿" in txt(page, "#cnRes [data-c-cost]"), txt(page, "#cnRes") or "")
        # ซ่อนบัญชีที่ตลาดไม่ตรง + ปุ่มแสดงบัญชีอื่น (fam = TH)
        opts = page.evaluate("()=>[...document.querySelectorAll('#cnAcct option')].map(o=>o.value)")
        check(f"{tag} ticker US → ซ่อนบัญชี fam (ตลาด TH) + ปุ่ม 'แสดงบัญชีอื่น'", opts == ["main"] and page.locator("#cnShowAll").count() == 1, str(opts))
        page.click("#cnShowAll")
        opts = page.evaluate("()=>[...document.querySelectorAll('#cnAcct option')].map(o=>o.value)")
        check(f"{tag} กด 'แสดงบัญชีอื่น' → เห็น main + fam", opts == ["main", "fam"], str(opts))
        page.evaluate("coreSheetClose()")

        # Tier A ไม่มีเหตุผล → บันทึกไม่ได้ · มีเหตุผล → tier A + tierReason
        new_plan(page, "XXX.BK", 100, 90, tier="A", reason="")
        check(f"{tag} ตั้ง Tier A ไม่มีเหตุผล → บันทึกไม่ได้", page.is_disabled("#cnSave"))
        page.fill("#cnReason", "   ")
        check(f"{tag} Tier A เหตุผลเป็นช่องว่างล้วน → บันทึกไม่ได้", page.is_disabled("#cnSave"))
        page.fill("#cnReason", "ROIC สูง · รอทำการบ้านเพิ่ม"); page.click('#cnF button[data-f="1"]')
        check(f"{tag} Tier A มีเหตุผล → บันทึกได้", not page.is_disabled("#cnSave"))
        page.click("#cnSave"); page.wait_for_timeout(500)
        cid, c = one_card(page, "XXX.BK")
        check(f"{tag} การ์ดแผนถูกสร้าง: status plan · tier A · tierReason · plan entry/stop · market TH · ยังไม่มี trade",
              c and c["status"] == "plan" and c["tier"] == "A" and c["tierReason"] == "ROIC สูง · รอทำการบ้านเพิ่ม" and c["plan"] == {"entry": 100, "stop": 90} and c["market"] == "TH" and c["strategy"] == "W" and c["trade_id"] is None
              and len(book_trades(page)) == 0, json.dumps(c, ensure_ascii=False))
        check(f"{tag} การ์ด plan โผล่ในแผง #corePanel · ผลไม้แรกสด 700", page.locator(f'#corePanel [data-core-card="{cid}"][data-kind="plan"]').count() == 1 and txt(page, f'[data-core-card="{cid}"] [data-c-qty]') == "700")
        # ซ้ำ
        new_plan(page, "xxx.bk", 100, 90)
        check(f"{tag} ticker ซ้ำในบัญชีเดียวกัน → 'มีการ์ด XXX.BK อยู่แล้ว' + ปุ่มไปที่การ์ด · บันทึกไม่ได้", "มีการ์ด XXX.BK อยู่แล้ว" in (txt(page, "#cnErr") or "") and page.locator("#cnGoto").count() == 1 and page.is_disabled("#cnSave"))
        page.click("#cnGoto"); page.wait_for_timeout(200)
        check(f"{tag} ปุ่มไปที่การ์ด → ปิด sheet · การ์ดถูกไฮไลต์", not sheet_open(page, "new") and page.evaluate("(id)=>document.querySelector(`[data-core-card=\"${id}\"]`).classList.contains('flash')", cid))
        check(f"{tag} ไม่สร้างการ์ดซ้ำ (ยังมี 1 ใบ)", len(cards_db(page)) == 1)
        # ลบแผน (sheet ยืนยัน · ไม่ใช้ confirm)
        ex(page, cid); page.click(f'[data-core-card="{cid}"] [data-c-delplan]'); page.wait_for_timeout(200)
        check(f"{tag} [ลบแผน] → sheet ยืนยัน (ไม่ใช้ confirm) ", sheet_open(page, "del") and not dialogs)
        page.click("[data-del-cancel]"); page.wait_for_timeout(200)
        check(f"{tag} ยกเลิกลบ → การ์ดยังอยู่", len(cards_db(page)) == 1)
        ex(page, cid); page.click(f'[data-core-card="{cid}"] [data-c-delplan]'); page.click("[data-del-ok]"); page.wait_for_timeout(500)
        check(f"{tag} ยืนยันลบ → การ์ดหาย", len(cards_db(page)) == 0)
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def cash_tier_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    trades = [T("hold", "core", "open", sym="HOLD", entry=670, sl=600, qty=1000, date="2026-09-01")]
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades))
    try:
        go_stock(page)
        new_plan(page, "XXX.BK", 100, 90, tier="A", reason="ทดสอบ", f="1")
        check(f"{tag} เงินสดว่าง 30,000 (ถือไม้อื่นทุน 670,000) → 300 + ป้าย 'เงินสดคุม'", txt(page, "#cnRes [data-c-qty]") == "300" and txt(page, "#cnRes [data-c-tag]") == "เงินสดคุม" and "เงินสดว่าง ฿30,000" in txt(page, "#cnRes [data-c-cash]"), txt(page, "#cnRes") or "")
        shot(page, f"7e2a-newplan-cash-{w}.png", ".core-sheet .ui-sheet")
        page.evaluate("coreSheetClose()")
        check(f"{tag} หัวบัญชี: เงินสดว่าง ฿30,000 · ถัง ฿700,000", "30,000" in (txt(page, '[data-core-head="main"] [data-c-cashfree]') or "") and "700,000" in (txt(page, '[data-core-head="main"] [data-c-tank]') or ""))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def buy_pyramid_checks(pw, w, h, label, mk="TH"):
    """mk TH = XXX.BK (ปัดหลัก 100 · ไม้เติมได้ 300 → 100) · mk US = XXX ที่ fx=1 (ปัด 1 หุ้น · ตัวเลขตรงสเปก 350 → 175)
    หมายเหตุ: ตัวเลข 350/175 ในสเปกไม่ใช่ทวีคูณ 100 → ตลาด TH คิดตาม core-size (market TH) ได้ 300/100 · ใช้ค่าจาก core-size"""
    tag = f"[chromium/{label}/{mk}]"
    tk = "XXX.BK" if mk == "TH" else "XXX"
    a1, a2 = (300, 100) if mk == "TH" else (350, 175)
    q2 = 700 + a1; e2 = (100 * 700 + 115 * a1) / q2
    q3 = q2 + a2; e3 = (e2 * q2 + 130 * a2) / q3
    S = "฿" if mk == "TH" else "$"
    doc = doc_with()
    if mk == "US": doc["books"]["main"]["settings"]["fx"] = 1
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards={"c1": card("c1", "main", tk, tier="A", tierReason="ทดสอบ")})
    try:
        go_stock(page)
        if mk == "TH": shot(page, f"7e2a-card-plan-{w}.png", '[data-core-card="c1"]')
        ex(page, "c1"); page.click('[data-core-card="c1"] [data-c-buy1]'); page.wait_for_timeout(200)
        check(f"{tag} [บันทึกซื้อไม้ 1] → sheet: ราคา = entry แผน · จำนวน = 700 · วันที่วันนี้ · Stop = 90",
              sheet_open(page, "buy1") and page.input_value("#cbPx") == "100" and page.input_value("#cbQty") == "700" and page.input_value("#cbDate") == TODAY and page.input_value("#cbStop") == "90",
              page.evaluate("()=>[cbPx,cbQty,cbDate,cbStop].map(e=>e.value).join('|')"))
        if mk == "TH":
            page.fill("#cbQty", "750")
            check(f"{tag} จำนวนที่ไม่ใช่ทวีคูณ 100 → แจ้ง 'จะปัดลงเป็น 700'", "จะปัดลงเป็น 700" in (txt(page, "#cbErr") or ""))
            page.fill("#cbQty", "700")
        page.click("#cbSave"); page.wait_for_timeout(600)
        tr = book_trades(page)
        t = tr[0] if tr else {}
        check(f"{tag} ซื้อไม้ 1: trade ใน books.main (port core · Long · qty 700 · entry 100 · sl 90 · cur {'THB' if mk=='TH' else 'USD'} · open)",
              len(tr) == 1 and t.get("port") == "core" and t.get("qty") == 700 and t.get("entry") == 100 and t.get("sl") == 90 and t.get("cur") == ("THB" if mk == "TH" else "USD") and t.get("status") == "open" and t.get("sym") == tk and t.get("bias") == "Long" and t.get("mult") == 1, json.dumps(t, ensure_ascii=False)[:300])
        cid, c = one_card(page, tk)
        check(f"{tag} การ์ด: status open · trade_id ตรง · lots[0].f = 1 · lots[0] 700@100 · stop 90",
              c["status"] == "open" and c["trade_id"] == t.get("id") and len(c["lots"]) == 1 and c["lots"][0]["f"] == 1 and c["lots"][0]["qty"] == 700 and c["lots"][0]["px"] == 100 and c["stop"] == 90, json.dumps(c, ensure_ascii=False))
        page.wait_for_timeout(300)
        page.evaluate("(d)=>coreWrite('c1', {px:200, pxDate:d, emaW:100})", TODAY); page.wait_for_timeout(400)   # 7E-2a-fix: ⚪ ปิดปุ่มเติมไม้ → ใส่ราคาปิดก่อน (🟢)
        check(f"{tag} Positions แสดงแถวของ {tk}", page.locator('#planSections [data-pos]').count() >= 1 and tk in (page.inner_text('#planSections') or ""))
        check(f"{tag} การ์ด open แสดงในแผง (data-kind=open) · ไม่มีปุ่ม [บันทึกซื้อไม้ 1] (กันสร้าง trade ซ้ำ)", page.locator('#corePanel [data-core-card="c1"][data-kind="open"]').count() == 1 and page.locator('[data-core-card="c1"] [data-c-buy1]').count() == 0)

        # pyramid: เลื่อน Stop 100
        ex(page, "c1"); page.click('[data-core-card="c1"] [data-c-stop-btn]'); page.wait_for_timeout(200)
        page.fill("#csStop", "85")
        check(f"{tag} เลื่อน Stop ลง (85 < 90) → ข้อความแดง บันทึกไม่ได้", "ต่ำกว่า Stop เดิม" in (txt(page, "#csErr") or "") and page.is_disabled("#csSave"))
        page.fill("#csStop", "100"); page.click("#csSave"); page.wait_for_timeout(500)
        t = book_trades(page)[0]; cid, c = one_card(page, tk)
        check(f"{tag} เลื่อน Stop ขึ้น 100 → trade.sl = 100 · การ์ด stop 100 · stopHistory [{{from 90 to 100}}]",
              t["sl"] == 100 and c["stop"] == 100 and len(c["stopHistory"]) == 1 and c["stopHistory"][0]["from"] == 90 and c["stopHistory"][0]["to"] == 100 and c["stopHistory"][0]["date"] == TODAY, json.dumps(c["stopHistory"]))
        open_sim(page, "c1"); page.fill('[data-core-card="c1"] [data-c-simpx]', "115"); page.wait_for_timeout(150)
        sm = txt(page, '[data-core-card="c1"] [data-c-addsum]') or ""
        ref1 = page.evaluate("(m)=>Calc.coreSize.addLot({tank:700000, f:1, price:115, stop:100, heldQty:700, avgCost:100, prevLotQty:700, market:m}).qty", mk)
        check(f"{tag} ไม้เติม @115 Stop 100 → {a1} (= core-size {ref1}) · normal · 'ค้าง {S}0 + ใหม่ {S}{a1*15:,}'",
              txt(page, '[data-core-card="c1"] [data-c-addqty]') == str(a1) and ref1 == a1 and page.locator('[data-core-card="c1"] [data-c-addtag="normal"]').count() == 1 and f"ค้าง {S}0" in sm and f"ใหม่ {S}{a1*15:,}" in sm and f"≤ {S}7,000" in sm, txt(page, '[data-core-card="c1"] [data-sim-res]') or "")
        if mk == "TH": shot(page, f"7e2a-card-addlot-normal-{w}.png", '[data-core-card="c1"]')
        page.click('[data-core-card="c1"] [data-c-buyadd]'); page.wait_for_timeout(200)
        check(f"{tag} sheet ซื้อไม้เติม: ราคา 115 · จำนวน {a1} · วันที่วันนี้", sheet_open(page, "buyadd") and page.input_value("#caPx") == "115" and page.input_value("#caQty") == str(a1) and page.input_value("#caDate") == TODAY)
        page.click("#caSave"); page.wait_for_timeout(600)
        t = book_trades(page)[0]; cid, c = one_card(page, tk)
        check(f"{tag} บันทึกไม้เติม → trade qty {q2} · entry = {e2:g} · sl 100 (ตรง core-size)", t["qty"] == q2 and abs(t["entry"] - e2) < 1e-9 and t["sl"] == 100, json.dumps(t)[:200])
        check(f"{tag} การ์ด: lots 2 ไม้ ({a1}@115 · f 1 · Stop 100) · stop 100", len(c["lots"]) == 2 and c["lots"][1]["qty"] == a1 and c["lots"][1]["px"] == 115 and c["lots"][1]["f"] == 1 and c["lots"][1]["stop"] == 100 and c["stop"] == 100, json.dumps(c["lots"]))
        ref = page.evaluate("(a)=>Calc.coreSize.addLot({tank:700000, f:1, price:130, stop:112, heldQty:a[0], avgCost:a[1], prevLotQty:a[2], market:a[3]}).qty", [q2, e2, a1, mk])
        ex(page, "c1"); page.click('[data-core-card="c1"] [data-c-stop-btn]'); page.fill("#csStop", "112"); page.click("#csSave"); page.wait_for_timeout(500)
        open_sim(page, "c1"); page.fill('[data-core-card="c1"] [data-c-simpx]', "130"); page.wait_for_timeout(150)
        check(f"{tag} ไม้เติม @130 Stop 112 → {a2} (= core-size {ref}) · normal", txt(page, '[data-core-card="c1"] [data-c-addqty]') == str(a2) and ref == a2 and page.locator('[data-core-card="c1"] [data-c-addtag="normal"]').count() == 1, txt(page, '[data-core-card="c1"] [data-sim-res]') or "")
        open_sim(page, "c1"); page.click('[data-core-card="c1"] [data-c-buyadd]'); page.click("#caSave"); page.wait_for_timeout(600)
        t = book_trades(page)[0]; cid, c = one_card(page, tk)
        check(f"{tag} บันทึกไม้ 3 → trade qty {q3} · entry ≈ {e3:.2f} · sl 112", t["qty"] == q3 and abs(t["entry"] - e3) < 1e-9 and t["sl"] == 112, json.dumps(t)[:200])
        menu_click(page, "c1", "[data-c-lots-btn]"); page.wait_for_timeout(150)
        check(f"{tag} ตาราง pyramid 3 แถว (ไม้ · วันที่ · ราคา · หุ้น · f · Stop) — เปิดจากเมนู ⋯ 'ดูไม้ที่ซื้อ' (7E-2a-fix)", page.locator('.core-sheet [data-c-pyr] tbody tr').count() == 3 and "stop" in (txt(page, '.core-sheet [data-c-pyr]') or "").lower())
        page.evaluate("coreSheetClose()")
        check(f"{tag} stopHistory 2 รายการ (90→100 · 100→112)", len(c["stopHistory"]) == 2 and c["stopHistory"][1]["to"] == 112, json.dumps(c["stopHistory"]))
        if mk == "TH": shot(page, f"7e2a-card-pyramid-{w}.png", '[data-core-card="c1"]')
        open_sim(page, "c1"); page.fill('[data-core-card="c1"] [data-c-simpx]', "140"); page.fill('[data-core-card="c1"] [data-c-simstop]', "100"); page.wait_for_timeout(150)
        check(f"{tag} Stop ใหม่ (100) < Stop เดิม (112) → ปุ่ม [บันทึกซื้อไม้เติม] ปิด + เหตุผล", page.is_disabled('[data-core-card="c1"] [data-c-buyadd]') and "Stop ใหม่ต่ำกว่า Stop เดิม" in (txt(page, '[data-core-card="c1"] [data-c-block]') or ""))
        if mk == "US":
            check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
            return
        menu_click(page, "c1", "[data-c-edit-btn]"); page.wait_for_timeout(200)
        check(f"{tag} [แก้ Entry/SL] = openTradeEdit เดิม (#teOverlay)", page.locator("#teOverlay.show").count() == 1)
        page.evaluate("closeTradeEdit()")
        menu_click(page, "c1", "[data-c-close-btn]"); page.wait_for_timeout(200)
        check(f"{tag} [ปิดตำแหน่ง] = openClosePos เดิม (#closePosOverlay)", page.locator("#closePosOverlay.show").count() == 1)
        page.evaluate("()=>document.getElementById('closePosOverlay').classList.remove('show')")
        page.evaluate("""()=>{ const B = getBook('main'); const t = B.trades[0]; t.sl = 113; t.qty = 1200; saveBook('main'); render(); }""")
        page.wait_for_timeout(200)
        check(f"{tag} trade ถูกแก้ sl/qty → การ์ดอ่านค่าใหม่จาก trade (Stop 113 · ถือ 1,200)", txt(page, '[data-core-card="c1"] [data-c-stop]') == "113" and "1,200" in txt(page, '[data-core-card="c1"] [data-c-hold]'))
        page.evaluate("()=>openClosePos(getBook('main').trades[0].id,'main')")
        page.fill("#cpExitPrice", "95"); page.click("#cpConfirmBtn"); page.wait_for_timeout(500)
        check(f"{tag} ปิดตำแหน่งครบ → การ์ดแสดง 'ปิดแล้ว' (แถวเล็ก พับ) ไม่เขียนการ์ด", page.locator('#corePanel [data-c-closedgroup] [data-kind="closed"]').count() == 1 and "ปิดแล้ว 1 ตัว" in (txt(page, '#corePanel [data-c-closedgroup] > summary') or "") and not page.evaluate("()=>document.querySelector('#corePanel [data-c-closedgroup]').open"))   # PX2: การ์ดปิดแล้วรวมเป็น <details> เดียว
        jr = page.evaluate("""()=>{ const t = getBook('main').trades[0]; return {status:t.status, exit:t.exitPrice, r:realizedROf(t), entry:t.entry, sl:t.sl, sl0:sl0Of(t)}; }""")
        exp_r = (95 - jr["entry"]) / abs(jr["entry"] - jr["sl0"])   # DD1: R ใช้ SL ตอนเข้า (sl0) ไม่ใช่ SL ปัจจุบัน 113
        check(f"{tag} Journal: ไม้ปิด (exit 95) · R คิดจาก SL ตอนเข้า (DD1) = (95−ทุน)/|ทุน−sl0|", jr["status"] == "closed" and jr["exit"] == 95 and jr["r"] is not None and abs(jr["r"] - exp_r) < 1e-9, json.dumps(jr))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def addtag_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    # move_stop / risk_limited / too_small / cash_limited (ตัวเลขจาก tests/core_size_test.js · main = TH lot 100 · f 100%)
    def case(name, trades, cards, px, stop, want_tag, want_qty, shot_name=None):
        browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades), cards=cards)
        try:
            go_stock(page)
            open_sim(page, "c1")
            page.fill('[data-core-card="c1"] [data-c-simpx]', str(px)); page.fill('[data-core-card="c1"] [data-c-simstop]', str(stop)); page.wait_for_timeout(200)
            got = page.evaluate("()=>{ const e = document.querySelector('[data-core-card=\"c1\"] [data-c-addtag]'); return e ? e.dataset.cAddtag : null; }")
            qty = txt(page, '[data-core-card="c1"] [data-c-addqty]')
            check(f"{tag} ไม้เติม {name} → ป้าย {want_tag} · {want_qty} หุ้น", got == want_tag and qty == str(want_qty), f"{got} {qty}")
            if want_tag == "move_stop":
                check(f"{tag} move_stop → 'เลื่อน Stop ขึ้นก่อน' + คำเตือน + ปุ่มเติมปิด", "เลื่อน Stop ขึ้นก่อน" in txt(page, '[data-core-card="c1"] [data-sim-res]') and page.locator('[data-core-card="c1"] [data-c-warn]').count() == 1 and page.is_disabled('[data-core-card="c1"] [data-c-buyadd]'))
            if want_tag == "too_small":
                check(f"{tag} too_small → ปุ่มเติมปิด + คำเตือน", page.is_disabled('[data-core-card="c1"] [data-c-buyadd]') and page.locator('[data-core-card="c1"] [data-c-warn]').count() == 1)
            if shot_name: shot(page, shot_name, '[data-core-card="c1"]')
            check(f"{tag} ไม้เติม {name}: ไม่มี error", not ce and not pe, str(ce[:2] + pe[:2]))
        finally:
            browser.close()
    t1 = T("t1", "core", "open", sym="XXX.BK", entry=100, sl=90, qty=700, date="2026-09-10")
    case("move_stop (@115 Stop 90 · ค้างกินงบหมด)", [t1], {"c1": open_card("c1", "t1", px=120, pxDate=TODAY, emaW=100)}, 115, 90, "move_stop", 0, f"7e2a-card-addlot-movestop-{w}.png")
    case("risk_limited (@115 Stop 95 · TH ปัดหลัก 100)", [t1], {"c1": open_card("c1", "t1", px=120, pxDate=TODAY, emaW=100)}, 115, 95, "risk_limited", 100)
    t3 = T("t1", "core", "open", sym="XXX.BK", entry=100, sl=90, qty=100, date="2026-09-10")
    case("too_small (ไม้ก่อน 100 → เป้า 50)", [t3], {"c1": open_card("c1", "t1", qty=100, px=140, pxDate=TODAY, emaW=100)}, 130, 120, "too_small", 0)
    tc = [t1, T("hold", "core", "open", sym="HOLD", entry=610, sl=500, qty=1000, date="2026-09-01")]
    case("cash_limited (เงินสดว่าง 20,000 · @115 Stop 100)", tc, {"c1": open_card("c1", "t1", px=120, pxDate=TODAY, emaW=100)}, 115, 100, "cash_limited", 100)


def status_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    t1 = T("t1", "core", "open", sym="XXX.BK", entry=100, sl=90, qty=700, date="2026-09-10")
    old = bk(8)
    cases = [
        ("g", open_card("g", "t1", px=120, pxDate=TODAY, emaW=110), "green"),
    ]
    trades = [t1]
    for n in ("y", "r", "g", "n", "e"):
        trades.append(T("t_" + n, "core", "open", sym=n.upper() + "X.BK", entry=100, sl=90, qty=700, date="2026-09-10"))
    cs = {
        "y": open_card("y", "t_y", ticker="YX.BK", px=96.5, pxDate=TODAY, emaW=98),
        "r": open_card("r", "t_r", ticker="RX.BK", px=89, pxDate=TODAY, emaW=98),
        "g": open_card("g", "t_g", ticker="GX.BK", px=120, pxDate=TODAY, emaW=110),
        "n": open_card("n", "t_n", ticker="NX.BK", px=120, pxDate=old, emaW=110),
        "e": open_card("e", "t_e", ticker="EX.BK", px=96.5, pxDate=TODAY, emaW=None),
    }
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=trades[1:]), cards=cs)
    try:
        go_stock(page)
        st = lambda k: page.evaluate("(k)=>{ const e = document.querySelector(`[data-core-card=\"${k}\"]`); return e && e.dataset.status; }", k)
        check(f"{tag} px 96.5 วันนี้ EMA 98 Stop 90 → 🟡", st("y") == "yellow" and "🟡" in txt(page, '[data-core-card="y"] [data-c-status]'))
        ex(page, "y")
        check(f"{tag} 🟡 → ปุ่ม [เติมไม้] ปิด + title 'ปิดใต้ EMA10 — งดเพิ่มไม้' (7E-2a-fix: ระดับปุ่ม)", page.is_disabled('[data-core-card="y"] [data-c-addbtn]') and page.get_attribute('[data-core-card="y"] [data-c-addbtn]', "title") == "ปิดใต้ EMA10 — งดเพิ่มไม้")
        check(f"{tag} px 89 → 🔴 · ป้ายแดงเด่น 'ปิดใต้ Stop — ขายหมด' · ปุ่ม [ปิดตำแหน่ง] เน้น", st("r") == "red" and "ปิดใต้ Stop — ขายหมด" in (txt(page, '[data-core-card="r"] [data-c-redbanner]') or "") and page.evaluate("()=>document.querySelector('[data-core-card=\"r\"] [data-c-close-btn]').classList.contains('pri')"))
        check(f"{tag} px 120 EMA 110 → 🟢", st("g") == "green")
        check(f"{tag} pxDate 8 วันก่อน → ⚪", st("n") == "na" and "⚪" in txt(page, '[data-core-card="n"] [data-c-status]'))
        ex(page, "e")
        check(f"{tag} ไม่มี EMA10 (px 96.5 ใต้ 98 ไม่ตัดสิน) → ไม่มี 🟡 → 🟢 + 'ยังไม่กรอก EMA10'", st("e") == "green" and "ยังไม่กรอก EMA10" in (txt(page, '[data-core-card="e"]') or ""))
        # ชั้น 2: ตัวเลขตรง Calc.coreSize.layer2 (นับ y r g e · n = ขาดราคา)
        o = page.evaluate("""()=>{ const l = coreLayer2('main');
          const ref = Calc.coreSize.layer2({tank:700000, positions:[{qty:700,px:96.5,stop:90},{qty:700,px:89,stop:90},{qty:700,px:120,stop:90},{qty:700,px:null,stop:90},{qty:700,px:96.5,stop:90}], cap:0.2, warn:0.15});
          return {pct:l.pct, missing:l.missing, ref:ref.pct, refMissing:ref.missing, level:l.level}; }""")
        expect = (700 * 6.5 + 0 + 700 * 30 + 700 * 6.5) / 700000
        check(f"{tag} coreLayer2 ตรง Calc.coreSize.layer2 · ⚪ ไม่นับ · ขาดราคา 1", abs(o["pct"] - o["ref"]) < 1e-12 and abs(o["pct"] - expect) < 1e-9 and o["missing"] == 1 and o["refMissing"] == 1, json.dumps(o))
        check(f"{tag} หัวบัญชี: ชั้น 2 {expect*100:.2f}% / 20% · ขาดราคา 1", f"{f2(expect*100)}% / 20%" in (txt(page, '[data-core-head="main"] [data-c-l2]') or "") and "1" in txt(page, '[data-core-head="main"] [data-c-missing]'), txt(page, '[data-core-head="main"]') or "")
        cell = txt(page, '#portsSum [data-sum="open"]') or ""
        check(f"{tag} บล็อกสรุป Port: ช่อง (a) 'จากราคาปิด' ไม่มี 'จากทุน' · ตัวเลขตรง · 'ขาดราคา 1 ตัว (ไม่นับ)'", "จากราคาปิด" in cell and "จากทุน" not in cell and f"{f2(expect*100)}% / 20%" in cell.replace(" ", "").replace("%/", "% /") + "" or (f2(expect*100) in cell and "จากทุน" not in cell and "จากราคาปิด" in cell and "ขาดราคา 1 ตัว (ไม่นับ)" in cell), cell)
        drop = txt(page, '#portsSum [data-sum="acctdrop"]') or ""
        check(f"{tag} 'ถ้าทุกไม้โดน Stop': (Core จากราคาปิด · Sat จากทุน) + เทียบทุน", "Core จากราคาปิด · Sat จากทุน" in drop and "เทียบทุน:" in drop, drop)
        shot(page, f"7e2a-card-status-{w}.png", "#corePanel")
        for k, nm in (("g", "green"), ("y", "yellow"), ("r", "red"), ("n", "na")):
            shot(page, f"7e2a-card-{nm}-{w}.png", f'[data-core-card="{k}"]')
        shot(page, f"7e2a-corehead-{w}.png", '[data-core-head="main"]')
        shot(page, f"7e2a-portsum-{w}.png", "#portsSum")
        # อัปเดตราคาปิดสัปดาห์
        ex(page, "e"); page.click('[data-core-card="e"] [data-c-px-btn]'); page.wait_for_timeout(200)
        fri = page.input_value("#cpxDate")
        fri_ok = datetime.date.fromisoformat(fri).weekday() == 4 and 0 <= (datetime.date.fromisoformat(TODAY) - datetime.date.fromisoformat(fri)).days <= 6
        check(f"{tag} sheet ราคาปิด: วันที่เริ่ม = ศุกร์ล่าสุด ({fri})", fri_ok)
        page.fill("#cpxPx", "130"); page.fill("#cpxEma", "120"); page.click("#cpxSave"); page.wait_for_timeout(500)
        k, c = one_card(page, "EX.BK")
        check(f"{tag} บันทึกราคาปิด → การ์ด px 130 · pxDate · emaW 120", c["px"] == 130 and c["emaW"] == 120 and c["pxDate"] == fri, json.dumps(c)[:200])
        ex(page, "e"); page.click('[data-core-card="e"] [data-c-px-btn]'); page.fill("#cpxEma", ""); page.click("#cpxSave"); page.wait_for_timeout(500)
        k, c = one_card(page, "EX.BK")
        check(f"{tag} EMA10 ว่างได้ → emaW null", c["emaW"] is None)
        # ไม่มีข้อมูลนอกรายการ: ลำดับการ์ด 🔴 บนสุด
        order = page.evaluate("()=>[...document.querySelectorAll('#corePanel [data-core-card]')].map(e=>e.dataset.coreCard)")
        check(f"{tag} เรียงการ์ด: 🔴 บนสุด", order[0] == "r", str(order))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def f2(x):
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def summary_heat_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    # ไม้ open ที่ไม่มีการ์ด (นับจากทุน) + ไม้ปิดขาดทุน → heat ไม่รวม loss
    t_open = T("o1", "core", "open", sym="NOCARD", entry=100, sl=90, qty=1000, date="2026-09-01")
    t_loss = T("l1", "core", "closed", sym="LOSER", entry=100, sl=90, qty=1000, exitPrice=50, exitDate="2026-09-10", date="2026-09-01")
    def cell(page): return txt(page, '#portsSum [data-sum="open"]') or ""
    b1, c1, p1, ce1, pe1, d1 = launch(pw, w, h, doc_with(main_trades=[t_open]))
    b2, c2, p2, ce2, pe2, d2 = launch(pw, w, h, doc_with(main_trades=[t_open, t_loss]))
    try:
        go_stock(p1); go_stock(p2)
        a, b = cell(p1), cell(p2)
        exp = f2(1000 * 10 / 700000 * 100)
        check(f"{tag} ไม้ Core ที่ไม่มีการ์ด: ชั้น 2 นับจากทุน ({exp}%) + ป้าย 'ไม่มีการ์ด 1 ตัว'", exp in a and "ไม่มีการ์ด 1 ตัว" in a and "จากทุน" in (txt(p1, '#portsSum [data-sum-nocard]') or "") and "จากราคาปิด" in a, a)
        check(f"{tag} heat: มีไม้ปิดขาดทุน 1 ไม้ → ตัวเลขบล็อกสรุป Core ไม่เปลี่ยน (ไม่รวม loss)", a == b and txt(p1, "#portsSum [data-sum='acctdrop']") == txt(p2, "#portsSum [data-sum='acctdrop']"), a + " || " + b)
        check(f"{tag} heat: footer/แถบบัญชี ไม่เปลี่ยนเมื่อมีไม้ปิดขาดทุน", txt(p1, "#foot") == txt(p2, "#foot") and txt(p1, "#strip") == txt(p2, "#strip"))
        check(f"{tag} ตัดฟังก์ชัน loss ออก: portRealizedLossTHB / totalRealizedLossTHB ไม่มีแล้ว", p2.evaluate("()=>typeof portRealizedLossTHB==='undefined' && typeof totalRealizedLossTHB==='undefined'"))
        p2.evaluate("openSettings()"); p2.wait_for_timeout(200)
        lbls = p2.evaluate("()=>[...document.querySelectorAll('#settingsOverlay summary, .setsec summary')].map(e=>e.textContent.trim())") if p2.locator('.setsec summary').count() else []
        check(f"{tag} ป้ายตั้งค่า: 'Max Heat — ความเสี่ยงที่ถือค้าง + แผนที่รอ (% ของถัง)' (ไม่มี '+ loss')", "% of Core bucket" in p2.evaluate("()=>document.getElementById('sPortCore').closest('.f').querySelector('label').textContent") and not any("+ loss" in x for x in lbls), str(lbls))
        p2.evaluate("()=>document.querySelectorAll('.overlay.show').forEach(e=>e.classList.remove('show'))")
        check(f"{tag} ไม่มี console error / pageerror", not (ce1 + pe1 + ce2 + pe2), str((ce1 + pe1 + ce2 + pe2)[:3]))
    finally:
        b1.close(); b2.close()


def acct_sep_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    tm = T("m1", "core", "open", sym="MAIN.BK", entry=100, sl=90, qty=700, date="2026-09-10")
    tf = T("f1", "core", "open", sym="FAM.BK", entry=50, sl=45, qty=1000, date="2026-09-10")
    doc = doc_with(main_trades=[tm], fam_market="TH")
    doc["books"]["fam"]["trades"] = [tf]
    cs = {"cm": open_card("cm", "m1", ticker="MAIN.BK", px=108, pxDate=TODAY, emaW=100),
          "cf": open_card("cf", "f1", ticker="FAM.BK", acct="fam", qty=1000, entry=50, sl=45, px=None, lots=[{"n": 1, "date": "2026-09-10", "px": 50, "qty": 1000, "f": 1, "stop": 45}])}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards=cs)
    try:
        go_stock(page)
        inm = page.evaluate("()=>[...document.querySelectorAll('[data-core-acct=\"main\"] [data-core-card]')].map(e=>e.dataset.coreCard)")
        inf = page.evaluate("()=>[...document.querySelectorAll('[data-core-acct=\"fam\"] [data-core-card]')].map(e=>e.dataset.coreCard)")
        check(f"{tag} 2 บัญชี: การ์ด fam ไม่ปนกับ main", inm == ["cm"] and inf == ["cf"], f"{inm} {inf}")
        check(f"{tag} 2 บัญชี: ถัง Core แยก (main 700,000 · fam 2,000,000)", "700,000" in txt(page, '[data-core-head="main"] [data-c-tank]') and "2,000,000" in txt(page, '[data-core-head="fam"] [data-c-tank]'))
        check(f"{tag} 2 บัญชี: เงินสดว่างแยก (main 630,000 · fam 1,950,000)", "630,000" in txt(page, '[data-core-head="main"] [data-c-cashfree]') and "1,950,000" in txt(page, '[data-core-head="fam"] [data-c-cashfree]'))
        check(f"{tag} 2 บัญชี: ชั้น 2 แยก (main 1.8% · fam ขาดราคา 1 → 0%)", "1.8% / 20%" in txt(page, '[data-core-head="main"] [data-c-l2]') and "0% / 20%" in txt(page, '[data-core-head="fam"] [data-c-l2]') and "1" in txt(page, '[data-core-head="fam"] [data-c-missing]') and "0" in txt(page, '[data-core-head="main"] [data-c-missing]'), (txt(page, '[data-core-head="main"]') or "") + " || " + (txt(page, '[data-core-head="fam"]') or ""))
        # ชิปบัญชีเดิม: เลือกเฉพาะ fam → แผงมีเฉพาะ fam
        page.evaluate("setPlanAcct('fam')"); page.wait_for_timeout(200)
        check(f"{tag} ตัวกรองบัญชีเดิม (ชิป) → แผง Core เหลือเฉพาะบัญชีนั้น", page.locator("[data-core-acct]").count() == 1 and page.locator('[data-core-acct="fam"]').count() == 1)
        page.evaluate("setPlanAcct('all')")
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def tier_card_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    t1 = T("t1", "core", "open", sym="XXX.BK", entry=100, sl=90, qty=700, date="2026-09-10")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=[t1]), cards={
        "c1": open_card("c1", "t1", tier="B", px=110, pxDate=TODAY, emaW=100), "c2": card("c2", "main", "PLAN.BK", tier="B")})
    try:
        go_stock(page)
        check(f"{tag} การ์ด: ชิป ตลาด · Tier B + เพดานไม้แรก 5% · 'W' · ปุ่ม L ปิด + 'ซื้อแล้ว — ล็อกกลยุทธ์' (7E-2b-1)",
              "TH" in txt(page, '[data-core-card="c1"] .ccChips') and "Tier B · เพดานไม้แรก 5%" in txt(page, '[data-core-card="c1"] [data-c-tier]') and page.is_disabled('[data-core-card="c1"] [data-c-strat="L"]') and "ซื้อแล้ว — ล็อกกลยุทธ์" in txt(page, '[data-core-card="c1"] .ccMenu'))
        menu_click(page, "c1", '[data-c-tierbtn]'); page.wait_for_timeout(200); page.click("#cnTierA"); page.wait_for_timeout(80)   # 7E-2b-1: 'Tier…' ปุ่มเดียว + บล็อก Tier คำนวณ
        check(f"{tag} เปลี่ยน B→A (หลังซื้อแล้ว) ต้องพิมพ์เหตุผล · ว่าง = บันทึกไม่ได้", sheet_open(page, "tier") and page.is_disabled("#ctSave"))
        page.fill("#cnReason", "  "); check(f"{tag} เหตุผลเป็นช่องว่าง = บันทึกไม่ได้", page.is_disabled("#ctSave"))
        page.fill("#cnReason", "moat แข็ง"); page.click("#ctSave"); page.wait_for_timeout(500)
        k, c = one_card(page, "XXX.BK")
        check(f"{tag} B→A พร้อมเหตุผล → tier A + tierReason · เพดานไม้แรก 10% · ชิปเหตุผล (title)", c["tier"] == "A" and c["tierReason"] == "moat แข็ง" and "เพดานไม้แรก 10%" in txt(page, '[data-core-card="c1"] [data-c-tier]') and page.get_attribute('[data-core-card="c1"] [data-c-reason-chip]', "title") == "moat แข็ง")
        ex(page, "c1"); page.click('[data-core-card="c1"] [data-c-reason-chip]'); page.wait_for_timeout(200)
        check(f"{tag} แตะชิป Tier A → กางเหตุผล", "moat แข็ง" in (txt(page, '[data-core-card="c1"] [data-c-reason]') or ""))
        menu_click(page, "c1", '[data-c-tierbtn]'); page.wait_for_timeout(200); page.click("#cnTierB"); page.click("#ctSave"); page.wait_for_timeout(500)
        k, c = one_card(page, "XXX.BK")
        check(f"{tag} A→B ไม่ต้องพิมพ์เหตุผล · ไม่มี sheet", c["tier"] == "B" and not sheet_open(page, "tier"))
        # plan card: Tier ตั้ง A ต้องมีเหตุผลเหมือนกัน
        menu_click(page, "c2", '[data-c-tierbtn]'); page.wait_for_timeout(200); page.click("#cnTierA"); page.wait_for_timeout(80)
        check(f"{tag} การ์ด plan: ตั้ง A ต้องมีเหตุผลเช่นกัน", sheet_open(page, "tier") and page.is_disabled("#ctSave"))
        page.evaluate("coreSheetClose()")
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def denied_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(), deny=True)
    try:
        go_stock(page)
        err = txt(page, "[data-core-err]") or ""
        check(f"{tag} permission-denied coreCards → ข้อความบนแผง 'ยังไม่ได้เปิดสิทธิ์ coreCards ใน Firestore rules'", "ยังไม่ได้เปิดสิทธิ์ coreCards ใน Firestore rules" in err, err)
        page.evaluate("coreNewOpen()"); page.wait_for_timeout(200)
        page.fill("#cnTicker", "XXX.BK"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90")
        check(f"{tag} permission-denied: บันทึกแผนไม่ได้ (ปุ่มปิด) · แอปไม่พัง", page.is_disabled("#cnSave") and page.locator("#mainWrap").is_visible())
        page.evaluate("coreSheetClose()")
        for t in ("flow", "mix", "watch", "plan", "journal"):
            page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(120)
        check(f"{tag} permission-denied: เปิดทุกแท็บได้ ไม่มี pageerror", not pe, str(pe[:3]))
        # เขียนไม่ผ่าน (ปลดตรงนี้แล้ว deny ตอนเขียน) → แสดงข้อความ ไม่ throw
        page.evaluate("()=>{ coreErr = null; }")
        page.evaluate("()=>coreWrite('zz', {ticker:'ZZ'})"); page.wait_for_timeout(400)
        check(f"{tag} coreWrite ถูกปฏิเสธ → coreErr ตั้ง + แผงแสดงข้อความ", "ยังไม่ได้เปิดสิทธิ์ coreCards" in (txt(page, "[data-core-err]") or ""))
    finally:
        browser.close()


def layout_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    t1 = T("t1", "core", "open", sym="XXX.BK", entry=100, sl=90, qty=700, date="2026-09-10")
    cs = {"c1": open_card("c1", "t1", px=108, pxDate=TODAY, emaW=104, lots=[{"n": 1, "date": "2026-09-10", "px": 100, "qty": 500, "f": 1, "stop": 90}, {"n": 2, "date": "2026-09-17", "px": 115, "qty": 200, "f": 0.75, "stop": 100}]),
          "c2": card("c2", "main", "LONGNAMEPLAN.BK", tier="A", tierReason="เหตุผลยาว ๆ ทดสอบการล้น")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(main_trades=[t1]), cards=cs)
    try:
        go_stock(page)
        open_sim(page, "c1"); page.fill('[data-core-card="c1"] [data-c-simpx]', "115"); page.wait_for_timeout(150)
        ov = page.evaluate("()=>({sw:document.documentElement.scrollWidth, iw:window.innerWidth})")
        check(f"{tag} แท็บแผน (มีการ์ด open + plan) ไม่ล้นแนวนอน", ov["sw"] <= ov["iw"] + 1, json.dumps(ov))
        small = page.evaluate("()=>[...document.querySelectorAll('#corePanel .ccBtn')].filter(b=>b.offsetParent && b.getBoundingClientRect().height<35.5).map(b=>b.textContent.trim())")
        check(f"{tag} ปุ่มในแผง Core สูง ≥ 36px", not small, str(small))
        page.evaluate("coreNewOpen()"); page.wait_for_timeout(200)
        page.fill("#cnTicker", "AAPL"); page.click("#cnTierA"); page.wait_for_timeout(100)
        small = page.evaluate("()=>[...document.querySelectorAll('.core-sheet button, .core-sheet input, .core-sheet select')].filter(b=>b.offsetParent && b.getBoundingClientRect().height<35.5).map(b=>b.id||b.textContent.trim())")
        ov = page.evaluate("()=>{ const s = document.querySelector('.core-sheet .ui-sheet'); return {sw:s.scrollWidth, cw:s.clientWidth}; }")
        check(f"{tag} sheet แผนใหม่: ปุ่ม/ช่อง สูง ≥ 36px · ไม่ล้นแนวนอน", not small and ov["sw"] <= ov["cw"] + 1, f"{small} {ov}")
        shot(page, f"7e2a-newplan-normal-{w}.png", ".core-sheet .ui-sheet")
        page.evaluate("coreSheetClose()")
        for t in ("flow", "mix", "watch", "plan", "journal"):
            page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(150)
        page.evaluate("()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        page.evaluate("()=>{ switchTab('plan'); setPlanScope('stock'); }")
        page.evaluate("openSettings()"); page.wait_for_timeout(200)
        page.evaluate("()=>document.querySelectorAll('.overlay.show').forEach(e=>e.classList.remove('show'))")
        check(f"{tag} เปิดทุกแท็บ + หน้า Sat + ตั้งค่า ไม่มี console error", not ce and not pe, str(ce[:3] + pe[:3]))
        page.evaluate("()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(200)
        check(f"{tag} scope Future ซ่อนแผง Core", page.evaluate("()=>document.getElementById('corePanel').style.display") == "none")
    finally:
        browser.close()


def grep_tests():
    html = open(INDEX, encoding="utf-8").read()
    for needle in ("coreCards", "coreWrite", "coreLayer2", "Calc.coreSize.firstLot", "addLot", "ขาดราคา"):
        if needle == "Calc.coreSize.firstLot":
            ok = ("Calc.coreSize.firstLot" in html) or bool(re.search(r"cs\.firstLot\(", html)) or ("firstLot(" in html)
        else:
            ok = needle in html
        check(f"grep ต้องเจอ: {needle}", ok)
    check("grep ไม่เจอ: 'open + plan + loss'", "open + plan + loss" not in html)
    check("grep ไม่เจอ: 'จากทุน' ที่ป้ายช่อง (a) เดิม (sumPill nt จากทุน)", '<span class="sumPill nt">จากทุน</span>' not in html)
    rules = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    check("tests/README.md มีข้อความ Firestore rules ของ coreCards", "match /users/{uid}/coreCards/{doc}" in rules)
    src = open(os.path.join(ROOT, "core-size.js"), encoding="utf-8").read()
    B = "/* === core-size.js BEGIN (สำเนา · ห้ามแก้ที่นี่ · แก้ที่ core-size.js แล้วคัดลอกใหม่) === */\n"
    E = "/* === core-size.js END === */"
    i, j = html.find(B), html.find(E)
    check("สำเนา core-size.js ใน index.html ตรงต้นฉบับ (ไม่ถูกแตะ)", i >= 0 and j > i and html[i + len(B):j].strip() == src.strip())


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            plan_sheet_checks(pw, w, h, label)
            cash_tier_checks(pw, w, h, label)
            buy_pyramid_checks(pw, w, h, label, "TH")
            buy_pyramid_checks(pw, w, h, label, "US")
            addtag_checks(pw, w, h, label)
            status_checks(pw, w, h, label)
            summary_heat_checks(pw, w, h, label)
            acct_sep_checks(pw, w, h, label)
            tier_card_checks(pw, w, h, label)
            denied_checks(pw, w, h, label)
            layout_checks(pw, w, h, label)
    grep_tests()
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:300])
        sys.exit(1)


if __name__ == "__main__":
    main()
