"""LN3fix — ตัวช่วยกลางของเทส phase89/90 และสคริปต์ถ่ายภาพ
เปิดแอปแบบ Lean (FF_STUB_BASE) บนข้อมูล P77.fixture (Core ฿4.2M · Sat $45k) + การ์ด Core ตัวอย่าง (NVDA เปิด ไม่มีราคา · AVGO แผน)"""
import json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE   # SET1 — แฟลกนักพัฒนา: โหมดเดิมตรวจได้ · เปิดการ์ด Settings ทั้งหมด
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase77 as P77

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
js = P37.js


def core_cards(extra=False):
    cards = {
        "ccNV": P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=128, sl=115, tier="A", tierLens="fortress",
                              lots=[{"n": 1, "date": "2026-09-10", "px": 128, "qty": 10, "f": 1, "stop": 115}]),
        "ccAV": P24.card("ccAV", "main", "AVGO", tier="B", plan={"entry": 300, "stop": 270}),
    }
    if extra:
        cards["ccL1"] = P24.open_card("ccL1", "tL1", ticker="MSFT", acct="main", qty=5, entry=400, sl=380, tier="A", tierLens="fortress", strategy="L")
    return cards


def mutate(doc):
    P77.fixture()(doc)


def launch(pw, w, h, cards=True, mut=None, pin_winner=False):
    def m(doc):
        mutate(doc)
        if mut: mut(doc)
        if pin_winner: P24.pin_winner_pool(doc)   # RG2b — ตรึงถัง Winner = ทุน Core เดิม
    browser, context, page, ce, pe, dl = P54.launch(pw, w, h, m)
    P51.fresh(page, None)
    if cards:
        js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("tNV", "core", "open", sym="NVDA", entry=128, sl=115, qty=10, cur="USD", date="2026-09-10")])
        page.wait_for_timeout(300)
        for cid, c in (cards if isinstance(cards, dict) else core_cards()).items():
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
        js(page, "()=>{ coreStop(); coreStart(); }"); page.wait_for_timeout(700)
    return browser, page, ce, pe


def launch2(pw, w, h, trades, cards, mut=None, fx=33, core_risk=None, pin_winner=False):
    """LN3fix2 — ถัง Core ฿4.2M fx 33 (≈ $127k) · ค่าตั้ง Base 1.0% · เทรด/การ์ดที่กำหนดเอง (ไม่ผ่านฟอร์ม)"""
    def m(doc):
        mutate(doc)
        for a in ("main", "fam"):
            doc["books"][a]["settings"]["fx"] = fx
        cr = {"riskA": 1.0, "riskB": 1.0, "riskPct": 1.0, "tierA": 15, "winnerCap": 15, "tierB": 10, "maxLots": 3, "addRatio": 50, "market": "both"}
        cr.update(core_risk or {})
        doc["books"]["main"]["settings"].setdefault("coreRisk", {}).update(cr)
        if mut: mut(doc)
        if pin_winner: P24.pin_winner_pool(doc)   # RG2b — ตรึงถัง Winner = ทุน Core เดิม
    browser, context, page, ce, pe, dl = P54.launch(pw, w, h, m)
    P51.fresh(page, None)
    js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", trades)
    page.wait_for_timeout(300)
    P24.set_ff(page, P24.ff_json(True, True))   # FF เขียวทั้งคู่ = 100% (ตัวเลขในม็อกอัป)
    for cid, c in cards.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    js(page, "()=>{ coreStop(); coreStart(); }"); page.wait_for_timeout(700)
    return browser, page, ce, pe


def go_core(page):
    js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); page.wait_for_timeout(400)


def go_sat(page):
    js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(400)


def shot(page, name, sel=None, full=False):
    """full = ถ่ายทั้งหน้า: ขยาย viewport ให้เท่าความสูงหน้า แล้วรอแอนิเมชันจบก่อนถ่าย (full_page ของ Playwright ทำให้ภาพจาง)"""
    page.wait_for_timeout(1300)   # รอแอนิเมชันสลับแท็บจบ (ไม่งั้นภาพจาง)
    try:
        if sel and page.locator(sel).count():
            page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name)); return
        if full:
            vp = page.viewport_size
            hh = page.evaluate("()=>Math.ceil(document.documentElement.scrollHeight)")
            page.set_viewport_size({"width": vp["width"], "height": max(vp["height"], min(hh, 3200))})
            page.wait_for_timeout(1500)
            page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
            page.set_viewport_size(vp); page.wait_for_timeout(300)
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def overflow(page): return P54.overflow(page)
