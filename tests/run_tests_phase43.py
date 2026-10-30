#!/usr/bin/env python3
"""PX1 — ราคาปิดสัปดาห์ + EMA10 อัตโนมัติ (หุ้น Core) จาก users/{uid}/prices · เทส 43
mock Firestore (มี prices) · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 13:03 ไทย (จันทร์) · timezone Asia/Bangkok
ภาพ tests/screenshots/px1-{card-auto,sheet-px,status-line}-{1440,390}.png
รัน: python3 run_tests_phase43.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase26 as p26
import run_tests_phase37 as P37
import run_tests_phase38 as P
import run_tests_phase39 as P39

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
CLK = "2026-10-05T06:03:00Z"
results = []
js, T = P.js, P37.T


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(500)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; }", sel)
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


def px_doc(sym, close, close_date="2026-10-02", ema=None, suspect=False):
    return {"sym": sym.replace(".BK", ""), "ySym": sym, "close": close, "closeDate": close_date, "ema10w": ema, "weeks": 30, "suspect": suspect, "src": "yfinance", "at": "2026-10-03T00:00:00Z"}


def meta_doc(run_at, ok=("AAA",), failed=()):
    return {"runAt": run_at, "ok": list(ok), "failed": [{"ySym": y, "why": "no data"} for y in failed], "n": len(ok) + len(failed), "ver": 1}


def base_doc():
    doc = P.doc38(clean=True, log={})
    doc["books"]["main"]["trades"] = [T("tw", "core", "open", sym="AAA", entry=100, sl=80, qty=100, cur="USD", date="2026-09-10", openedAt="2026-09-10")]
    doc["books"]["fam"]["settings"]["coreRisk"].update({"riskPct": 1, "tierA": 10, "tierB": 5}); doc["books"]["fam"]["settings"]["coreRisk"]["market"] = "both"   # CZ1: ค่าเริ่มต้นใหม่ (1.25/15/10) → seed ค่าเดิม ให้ตัวเลขที่คาดเท่าเดิม
    return doc


def w_card(px=100, px_date="2026-09-26", ema=95, **kw):
    return p24.open_card("cw", "tw", ticker="AAA", acct="main", qty=100, entry=100, sl=80, px=px, pxDate=px_date, emaW=ema, tier="A", **kw)


def launch(pw, w, h, prices=None, meta=None, cards=None, doc=None, deny=False):
    def extra(pg):
        if deny: pg.evaluate("()=>window.firebase.__mockDb.__denyPath(['users','testuid','prices'])")
        for k, v in (prices or {}).items(): pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "prices", k], v])
        if meta is not None: pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "prices", "_meta"], meta])
    r = P39.launch(pw, w, h, doc=doc if doc is not None else base_doc(), cards=cards if cards is not None else {"cw": w_card()}, iso=CLK, clean=True, extra=extra)
    p24.go_stock(r[2]); r[2].wait_for_timeout(300)
    return r


def state(page, cid="cw"):
    return js(page, """(id)=>{ const c = coreCardsList.find(x=>x.id===id); return c ? {px:c.px, pxDate:c.pxDate, emaW:c.emaW, src:c.pxSrc||null, sus:!!c._pxSuspect, man:c._pxMan||null} : null; }""", cid)


def equity(page): return js(page, "()=>ddEval('main','core').equity")
def missing(page): return js(page, "()=>{ const e=document.querySelector('[data-core-head=main] [data-c-missing]'); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; }")
def card_status(page, cid="cw"): return js(page, "(id)=>{ const e=document.querySelector('[data-core-card=\"'+id+'\"]'); return e ? e.dataset.status : null; }", cid)
def nums(page, cid="cw"): return js(page, "(id)=>{ const e=document.querySelector('[data-core-card=\"'+id+'\"] .ccNums'); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; }", cid)
def db_card(page, cid="cw"): return p24.cards_db(page).get(cid)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ───── 1 · auto ใหม่กว่า → ใช้ auto ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, meta_doc("2026-10-03T23:31:00Z"))
    try:
        s = state(page)
        check(f"{tag} 1 กรอกเอง 100 (26 ก.ย.) + auto 105 (2 ต.ค.) → ใช้ 105 · pxSrc=auto · emaW = 110", s["px"] == 105 and s["pxDate"] == "2026-10-02" and s["src"] == "auto" and s["emaW"] == 110 and s["man"]["px"] == 100, json.dumps(s))
        check(f"{tag} 1 การ์ดแสดง 'ปิด 105' + ป้าย 'อัตโนมัติ · ศ. 2 ต.ค.'", "ปิด 105" in (nums(page) or "") and "อัตโนมัติ · ศ. 2 ต.ค." in (txt(page, '[data-core-card="cw"] [data-c-pxsrc]') or ""), json.dumps([nums(page), txt(page, '[data-core-card="cw"] [data-c-pxsrc]')], ensure_ascii=False))
        eq_auto = equity(page)
        # 3 · ema 110 > close 105 (W) → เหลือง
        check(f"{tag} 3 ema10w 110 > close 105 (W) → สถานะเหลือง 'ปิดใต้ EMA10 · งดเพิ่มไม้'", card_status(page) == "yellow" and "งดเพิ่มไม้" in (js(page, "()=>{ const e=document.querySelector('[data-core-card=cw] [data-c-status]'); return e ? e.title : ''; }") or ""), json.dumps([card_status(page), js(page, "()=>document.querySelector('[data-core-card=cw] [data-c-status]').title")], ensure_ascii=False))
        # 8 · สถานะระบบ
        st = txt(page, "[data-core-head=main] [data-px-status]") or ""
        check(f"{tag} 8 สถานะ: 'ราคาอัตโนมัติ: อัปเดต อา. 4 ต.ค. 06:31 · 1/1 ตัว' (ไม่เหลือง)", "ราคาอัตโนมัติ: อัปเดต อา. 4 ต.ค. 06:31 · 1/1 ตัว" in st and js(page, "()=>document.querySelector('[data-px-status]').dataset.pxStatus") == "ok" and not js(page, "()=>document.querySelector('[data-px-status]').classList.contains('warn')"), st)
        # 7 · sheet + action อื่นไม่ทำให้ auto ไปอยู่ใน coreCards
        js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(200)
        shot(page, f"px1-card-auto-{sfx}.png", '[data-core-card="cw"]')
        shot(page, f"px1-status-line-{sfx}.png", "[data-core-head=main]")
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        line = txt(page, "[data-px-autoline]") or ""
        check(f"{tag} 7 sheet (การ์ดใช้ auto) มีบรรทัด 'ตอนนี้ใช้ราคาอัตโนมัติ — แก้ตัวเลขแล้วบันทึกเพื่อใช้ค่าที่กรอกเองแทน'", "ตอนนี้ใช้ราคาอัตโนมัติ — แก้ตัวเลขแล้วบันทึกเพื่อใช้ค่าที่กรอกเองแทน" in (txt(page, "[data-px-usingauto]") or ""), txt(page, "[data-px-usingauto]"))   # NUM2: เดิมคาดบรรทัด 'ราคาอัตโนมัติล่าสุด…'
        check(f"{tag} 7 ช่องกรอกใน sheet = ค่า auto (105 / 110) · วันที่ = closeDate ของ auto (2026-10-02)", js(page, "()=>[document.getElementById('cpxPx').value, document.getElementById('cpxEma').value, document.getElementById('cpxDate').value]") == ["105", "110", "2026-10-02"], json.dumps(js(page, "()=>[document.getElementById('cpxPx').value, document.getElementById('cpxEma').value, document.getElementById('cpxDate').value]")))   # NUM2: เดิมคาดค่ากรอกเอง 100 / 95
        shot(page, f"px1-sheet-px-{sfx}.png", ".core-sheet .ui-sheet, .core-sheet")
        js(page, "()=>coreSheetClose()")
        # action อื่น: เลื่อน Stop
        js(page, "()=>coreStopOpen('cw')"); page.wait_for_selector("#csStop"); page.fill("#csStop", "85"); page.wait_for_timeout(150)
        js(page, "()=>coreStopSave()"); page.wait_for_timeout(500)
        dc = db_card(page)
        check(f"{tag} 7 เลื่อน Stop → coreCards: stop 85 · px/pxDate/emaW ยังเป็นค่ากรอกเอง (100 / 2026-09-26 / 95) · ไม่มีค่า auto",
              dc and dc["stop"] == 85 and dc["px"] == 100 and dc["pxDate"] == "2026-09-26" and dc["emaW"] == 95, json.dumps({k: (dc or {}).get(k) for k in ("stop", "px", "pxDate", "emaW")}))
        # บันทึกราคาจาก sheet: วันเท่ากัน (ศุกร์ล่าสุด 2 ต.ค.) → ใช้ที่กรอกเอง · เขียนเฉพาะที่กรอก
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx"); page.fill("#cpxPx", "106"); page.fill("#cpxEma", "99"); page.wait_for_timeout(100)
        js(page, "()=>corePxSave()"); page.wait_for_timeout(500)
        dc3 = db_card(page); s3 = state(page)
        check(f"{tag} 7 บันทึกใน sheet → coreCards px 106 · pxDate 2026-10-02 · emaW 99 (ค่าที่กรอก) ไม่ใช่ 105/110", dc3["px"] == 106 and dc3["pxDate"] == "2026-10-02" and dc3["emaW"] == 99, json.dumps({k: dc3.get(k) for k in ("px", "pxDate", "emaW")}))
        check(f"{tag} 2 วันเท่ากัน (กรอก 2 ต.ค. = auto 2 ต.ค.) → ใช้ที่กรอกเอง 106 · src=manual", s3["px"] == 106 and s3["src"] == "manual" and s3["emaW"] == 99, json.dumps(s3))
        check(f"{tag} 10 ไม่ล้นแนวนอน", overflow(page) <= 0, str(overflow(page)))
        check(f"{tag} 10 ไม่มี console error (auto)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 1 · เทียบ equity / ขาดราคา ─────
    b, c, page, ce, pe, d = launch(pw, w, h)
    try:
        eq_man = equity(page)
    finally:
        b.close()
    b, c, page, ce, pe, d = launch(pw, w, h, None, None, {"cw": w_card(px=100, px_date="2026-10-01", ema=95)})
    try:
        s = state(page)
        check(f"{tag} 4 ไม่มี auto doc → การ์ดเท่าเดิมทุกค่า (100 / 2026-10-01 / 95 · src=manual) · ไม่มีบรรทัดสถานะ", s == {"px": 100, "pxDate": "2026-10-01", "emaW": 95, "src": "manual", "sus": False, "man": None} and txt(page, "[data-px-status]") is None, json.dumps(s))
        check(f"{tag} 4 ค่าที่คำนวณ = ค่าจาก fixture เดิม (ปิด 100 · ไม่มีป้ายอัตโนมัติ)", "ปิด 100" in (nums(page) or "") and txt(page, "[data-c-pxsrc=auto]") is None, nums(page))
    finally:
        b.close()
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)})
    try:
        eq_auto = equity(page)
        check(f"{tag} 1 DD equity ใช้ 105 (ต่างจากกรอกเอง 100 = 5 × 100 × fx 40 = ฿20,000)", abs((eq_auto - eq_man) - 20000) < 1e-6, json.dumps([eq_auto, eq_man]))
    finally:
        b.close()
    # ขาดราคา: การ์ดไม่มี px
    b, c, page, ce, pe, d = launch(pw, w, h, None, None, {"cw": w_card(px=None, px_date=None, ema=None)})
    try:
        m0 = missing(page)
    finally:
        b.close()
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, None, {"cw": w_card(px=None, px_date=None, ema=None)})
    try:
        m1 = missing(page)
        check(f"{tag} 1 การ์ดไม่เคยกรอกราคา: ไม่มี auto → 'ขาดราคา 1' · มี auto → 'ขาดราคา 0'", m0 and m0.endswith("1") and m1 and m1.endswith("0"), json.dumps([m0, m1], ensure_ascii=False))
    finally:
        b.close()

    # ───── 2 · กรอกเองใหม่กว่า ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, None, {"cw": w_card(px=101, px_date="2026-10-03", ema=96)})
    try:
        s = state(page)
        check(f"{tag} 2 กรอกเอง 3 ต.ค. (ใหม่กว่า auto 2 ต.ค.) → ใช้ที่กรอกเอง 101 · src=manual · emaW 96", s["px"] == 101 and s["src"] == "manual" and s["emaW"] == 96, json.dumps(s))
    finally:
        b.close()
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, None, {"cw": w_card(px=101, px_date="2026-10-02", ema=96)})
    try:
        s = state(page)
        check(f"{tag} 2 วันที่เท่ากัน (2 ต.ค.) → ใช้ที่กรอกเอง 101", s["px"] == 101 and s["src"] == "manual", json.dumps(s))
    finally:
        b.close()

    # ───── 7 · ซื้อไม้เติม (auto ปิดเหนือ EMA10 → เติมได้) ไม่ทำให้ค่า auto ไปอยู่ใน coreCards ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=100)})
    try:
        js(page, "()=>{ coreSim['cw'] = {px:'106', stop:'100'}; coreBuyAddOpen('cw'); }"); page.wait_for_timeout(300)
        opened = js(page, "()=>!!document.getElementById('caSave')")
        if opened:
            js(page, "()=>coreBuyAddSave()"); page.wait_for_timeout(500)
        dc2 = db_card(page)
        check(f"{tag} 7 ซื้อไม้เติม: sheet เปิดได้ + บันทึกแล้ว (lots +1)", opened and len(dc2.get("lots", [])) == 2, json.dumps([opened, dc2.get("lots")]))
        check(f"{tag} 7 ซื้อไม้เติมแล้ว coreCards ไม่มีค่า auto (px 100 · pxDate 2026-09-26 · emaW 95 · ไม่มี pxSrc/_pxMan)",
              dc2 and dc2["px"] == 100 and dc2["pxDate"] == "2026-09-26" and dc2["emaW"] == 95 and not any(k in dc2 for k in ("pxSrc", "_pxMan", "_pxSuspect")), json.dumps(dc2)[:300])
    finally:
        b.close()

    # ───── 3 · L ไม่ใช้ EMA · 6 · TH จับคู่ .BK ─────
    doc = base_doc()
    doc["books"]["fam"]["trades"] = [p26.ltrade("lf", sym="AAA")]
    lf = p26.lopen("lf", ticker="AAA", acct="fam", px=96.5, pxDate="2026-09-26")
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, None, {"cw": w_card(), "lf": lf}, doc=doc)
    try:
        sl = state(page, "lf")
        check(f"{tag} 3 การ์ด L ตัวเดียวกัน → ใช้ px auto 105 แต่ไม่ใช้ EMA (emaW ว่าง)", sl["px"] == 105 and sl["src"] == "auto" and not sl["emaW"], json.dumps(sl))
    finally:
        b.close()
    doc = base_doc()
    doc["books"]["fam"]["trades"] = [T("tp", "core", "open", sym="PTT", entry=30, sl=25, qty=1000, cur="THB", date="2026-09-10", openedAt="2026-09-10")]
    ptt = p24.open_card("cp", "tp", ticker="PTT", acct="fam", qty=1000, entry=30, sl=25, px=None, pxDate=None, emaW=None, tier="A")
    ptt["market"] = "TH"
    b, c, page, ce, pe, d = launch(pw, w, h, {"PTT.BK": px_doc("PTT.BK", 33.5, ema=31)}, None, {"cw": w_card(), "cp": ptt}, doc=doc)
    try:
        s = state(page, "cp")
        check(f"{tag} 6 การ์ด 'PTT' ตลาด TH จับคู่ doc 'PTT.BK' ได้ (px 33.5 · ema 31)", s["px"] == 33.5 and s["src"] == "auto" and s["emaW"] == 31, json.dumps(s))
        p2 = js(page, "()=>[pxYSym({ticker:'ptt.bk'}), pxYSym({ticker:'PTT', market:'TH'}), pxYSym({ticker:'avgo', market:'US'})]")
        check(f"{tag} 6 pxYSym: ptt.bk / PTT+TH → PTT.BK · avgo → AVGO", p2 == ["PTT.BK", "PTT.BK", "AVGO"], json.dumps(p2))
    finally:
        b.close()

    # ───── 5 · suspect ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 160, ema=110, suspect=True)})
    try:
        s = state(page)
        sus = txt(page, '[data-core-card="cw"] [data-c-pxsuspect]') or ""
        check(f"{tag} 5 auto suspect:true → ใช้ค่าที่กรอกเอง 100 + ⚠ 'ราคาอัตโนมัติเปลี่ยนเกิน 40% — ตรวจก่อน (ใช้ค่าที่กรอกเองแทน)'", s["px"] == 100 and s["src"] == "manual" and s["sus"] and "⚠ ราคาอัตโนมัติเปลี่ยนเกิน 40% — ตรวจก่อน (ใช้ค่าที่กรอกเองแทน)" in sus, json.dumps([s, sus], ensure_ascii=False))
    finally:
        b.close()

    # ───── 8 · _meta ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, meta_doc("2026-09-26T23:31:00Z"))
    try:
        st = txt(page, "[data-core-head=main] [data-px-status]") or ""
        check(f"{tag} 8 _meta.runAt 26 ก.ย. (วันนี้ 5 ต.ค. = 9 วัน) → เหลือง 'ระบบราคาอัตโนมัติไม่ได้อัปเดต — ตรวจ GitHub Actions (prices)'", "ระบบราคาอัตโนมัติไม่ได้อัปเดต — ตรวจ GitHub Actions (prices)" in st and js(page, "()=>document.querySelector('[data-px-status]').classList.contains('warn')"), st)
    finally:
        b.close()
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, meta_doc("2026-10-03T23:31:00Z", ok=("AAA",), failed=("XYZ",)))
    try:
        st = txt(page, "[data-core-head=main] [data-px-status]") or ""
        check(f"{tag} 8 failed ['XYZ'] → '… 1/2 ตัว · ดึงไม่ได้: XYZ' สีเหลือง", "1/2 ตัว · ดึงไม่ได้: XYZ" in st and js(page, "()=>document.querySelector('[data-px-status]').classList.contains('warn')"), st)
    finally:
        b.close()
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, None)
    try:
        check(f"{tag} 8 ไม่มี _meta → ไม่มีบรรทัดสถานะ", txt(page, "[data-px-status]") is None)
    finally:
        b.close()

    # ───── 9 · อ่าน prices ไม่ได้ ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 105, ema=110)}, meta_doc("2026-10-03T23:31:00Z"), deny=True)
    try:
        s = state(page); st = txt(page, "[data-core-head=main] [data-px-status]") or ""
        check(f"{tag} 9 prices permission-denied → แอปทำงานเดิม (px 100 กรอกเอง) + 'อ่านราคาอัตโนมัติไม่ได้ — ตรวจ Firestore Rules ของ users/{{uid}}/prices'", s["px"] == 100 and s["src"] == "manual" and "อ่านราคาอัตโนมัติไม่ได้ — ตรวจ Firestore Rules ของ users/{uid}/prices" in st, json.dumps([s, st], ensure_ascii=False))
        check(f"{tag} 9 การ์ด Core ยังแสดงปกติ (มีการ์ด AAA · ไม่มี error ของ coreCards)", js(page, "()=>!!document.querySelector('[data-core-card=cw]') && !coreErr"), str(js(page, "()=>coreErr")))
        check(f"{tag} 10 ไม่ล้นแนวนอน (prices ไม่ได้)", overflow(page) <= 0, str(overflow(page)))
    finally:
        b.close()


def static_tests():
    root = os.path.join(HERE, "..")
    check("[static] สำรอง index.backup-pre-PX1.html + tests/_bk_px1/ อยู่", os.path.exists(os.path.join(root, "index.backup-pre-PX1.html")) and os.path.isdir(os.path.join(HERE, "_bk_px1")))
    check("[static] P2-prices-upload: scripts/build_prices.py · .github/workflows/prices.yml · README-อัปโหลด.md อยู่", all(os.path.exists(os.path.join(root, "P2-prices-upload", p)) for p in ("scripts/build_prices.py", ".github/workflows/prices.yml", "README-อัปโหลด.md")))
    html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    wf = open(os.path.join(root, "P2-prices-upload", ".github", "workflows", "prices.yml"), encoding="utf-8").read()
    check("[static] workflow: cron เสาร์+อาทิตย์ 06:30 ไทย · ไม่ commit กลับ (permissions contents: read · ไม่มี git push)", "30 23 * * 5" in wf and "30 23 * * 6" in wf and "contents: read" in wf and "git push" not in wf and "FIREBASE_SA: ${{ secrets.FIREBASE_SA }}" in wf)
    check("[static] coreWrite ไม่มีที่ไหนส่งการ์ดที่ merge แล้ว (ไม่มี coreWrite(…, c) / coreCardsList item)", not re.search(r"coreWrite\([^)]*,\s*c\s*\)", html) and "coreWrite(c.id, c)" not in html)
    check("[static] ไม่มี coreCardsRaw/pxAuto ถูกส่งเข้า coreWrite", not re.search(r"coreWrite\([^\n]*(pxAuto|_pxMan|coreCardsRaw)", html))


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 43 / PX1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
