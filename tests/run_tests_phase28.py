#!/usr/bin/env python3
"""FX — วันที่เวลาไทย (thaiToday) · jDateShort · สี P&L ใช้ pnlCls · เตือน Fund-flow เก่าในแผง Core + sheet แผนใหม่
เวลา: ตั้ง timezone_id ของเบราว์เซอร์ (UTC และ Asia/Bangkok) + override Date ด้วยนาฬิกาปลอม (2026-10-01 02:00 ไทย = 2026-09-30T19:00Z · และ 12:00 ไทย) → ต้องได้ผลเดียวกัน
รัน: python3 run_tests_phase28.py [/path/to/index.html] · ภาพ tests/screenshots/fx-*.png"""
import datetime, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22
import run_tests_phase24 as p24

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
results = []
T = p22.T
txt = p24.txt


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


CLOCK_JS = """(iso) => { const R = Date, base = R.parse(iso), start = R.now();
  class FD extends R { constructor(...a){ if(a.length===0) super(base + (R.now()-start)); else super(...a); } static now(){ return base + (R.now()-start); } }
  window.Date = FD; }"""


def launch(pw, w, h, doc, cards=None, tz="Asia/Bangkok", iso="2026-09-30T19:00:00Z"):
    lk = {"headless": True}
    if base.CHROMIUM_PATH: lk["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    context = browser.new_context(viewport={"width": w, "height": h}, timezone_id=tz)
    from ff_stub import FF_STUB; context.add_init_script(FF_STUB)
    context.add_init_script("(" + CLOCK_JS + ")(" + json.dumps(iso) + ")")
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
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(1000)
    return browser, context, page, ce, pe, dialogs


def closed(id, sym, entry, exit_, qty=1, **kw):
    return T(id, "core", "closed", sym=sym, entry=entry, sl=entry - 10, qty=qty, exitPrice=exit_, exitDate="2026-09-20", date="2026-09-10", **kw)


def make(extra=None):
    trades = [
        closed("cp1", "PPOS", 100, 101), closed("cn1", "PNEG", 100, 99), closed("cz0", "PZERO", 100, 100), closed("cf4", "PFRAC", 100, 99.6),
        closed("g1a", "PGRP", 100, 105, posGroup="g1"), closed("g1b", "PGRP", 100, 95, posGroup="g1"),
        T("tp", "core", "plan", sym="PLANX", entry=100, sl=90, qty=10),
        T("to", "core", "open", sym="OPENX", entry=100, sl=90, qty=10, date="2026-09-25"),
    ]
    doc = p22.make_doc(main_trades=trades + (extra or []), with_legacy=False)
    doc["books"]["main"]["settings"]["capital"]["core"] = 700000
    doc["books"]["main"]["settings"].setdefault("coreRisk", {}).update({"riskPct": 1, "tierA": 10, "tierB": 5}); doc["books"]["main"]["settings"]["coreRisk"]["market"] = "both"   # CZ1: ค่าเริ่มต้นใหม่ (1.25/15/10) → seed ค่าเดิม ให้ตัวเลขที่คาดเท่าเดิม
    cards = {"c1": p24.card("c1", "main", "XXX.BK", tier="B", plan={"entry": 100, "stop": 90}, stop=90)}
    return doc, cards


def date_checks(pw, w, h, tz, clock, label):
    tag = f"[chromium/{label}/{tz}/{clock}]"
    iso = "2026-09-30T19:00:00Z" if clock == "02:00" else "2026-10-01T05:00:00Z"
    doc, cards = make()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards, tz=tz, iso=iso)
    try:
        p24.go_stock(page)
        d = page.evaluate("()=>({t:thaiToday(), i:todayISO(), p:posThaiToday(), raw:new Date().toISOString().slice(0,10)})")
        check(f"{tag} 1 thaiToday()/todayISO()/posThaiToday() = 2026-10-01 (นาฬิกา {clock} ไทย · UTC ดิบ = {d['raw']})", d["t"] == d["i"] == d["p"] == "2026-10-01" and (d["raw"] == "2026-09-30") == (clock == "02:00"), json.dumps(d))
        # 2 ซื้อไม้ 1 ผ่านการ์ด
        p24.ex(page, "c1"); page.click('[data-core-card="c1"] [data-c-buy1]'); page.wait_for_timeout(200)
        dv = page.input_value("#cbDate")
        page.click("#cbSave"); page.wait_for_timeout(600)
        tr = [t for t in p24.book_trades(page) if t["sym"] == "XXX.BK"]
        cid, c = p24.one_card(page, "XXX.BK")
        check(f"{tag} 2 ซื้อไม้ 1: ช่องวันที่ = 2026-10-01 · trade.date/openedAt = 2026-10-01 · lots[0].date = 2026-10-01", dv == "2026-10-01" and tr and tr[0]["date"] == "2026-10-01" and tr[0]["openedAt"] == "2026-10-01" and c["lots"][0]["date"] == "2026-10-01", f"{dv} {tr[:1]} {c and c['lots']}")
        # ยกเลิกไม้
        page.evaluate("()=>openCancelModal('tp','main')"); page.wait_for_timeout(150)
        page.fill("#cancelNote", "ทดสอบ"); page.evaluate("()=>confirmCancel()"); page.wait_for_timeout(500)
        tp = [t for t in p24.book_trades(page) if t["id"] == "tp"][0]
        check(f"{tag} 2 ยกเลิกไม้ → cancelDate = 2026-10-01", tp["status"] == "cancelled" and tp["cancelDate"] == "2026-10-01", json.dumps(tp)[:200])
        # sheet ปิดไม้
        page.evaluate("()=>openClosePos('to','main')"); page.wait_for_timeout(150)
        check(f"{tag} 2 เปิด sheet ปิดไม้ → ช่อง Exit Date = 2026-10-01", page.input_value("#cpExitDate") == "2026-10-01")
        page.fill("#cpExitPrice", "105"); page.fill("#cpExitDate", ""); page.click("#cpConfirmBtn"); page.wait_for_timeout(500)
        to = [t for t in p24.book_trades(page) if t["id"] == "to"][0]
        check(f"{tag} 2 ปิดไม้โดยเว้นวันที่ → fallback exitDate = 2026-10-01", to["status"] == "closed" and to["exitDate"] == "2026-10-01", json.dumps(to)[:200])
        # 3 jDateShort
        j = page.evaluate("()=>[jDateShort('2026-09-30T20:00:00Z'), jDateShort('2026-09-30'), jDateShort('2025-12-31'), jDateShort('2026-10-01T05:00:00Z'), jDateShort('ผิด'), jDateShort(''), jDateShort(null), jDateShort('2026-13-01')]")
        check(f"{tag} 3 jDateShort: '…T20:00:00Z' → 1 ต.ค. · '2026-09-30' → 30 ก.ย. (ไม่เลื่อนวัน) · '2025-12-31' มีปี 25 · ค่าผิด → —", j[0] == "1 ต.ค." and j[1] == "30 ก.ย." and "25" in j[2] and j[2].startswith("31 ธ.ค.") and j[3] == "1 ต.ค." and j[4:] == ["—", "—", "—", "—"], json.dumps(j, ensure_ascii=False))
        # 5 pnlCls ตาราง Closed / การ์ดมือถือ
        page.evaluate("()=>switchTab('journal')"); page.wait_for_timeout(300)
        cls = page.evaluate("""()=>{ const o = {}; document.querySelectorAll('#jContent_closed *').forEach(e=>{ if(e.children.length) return; const t = e.textContent.trim(); if(/^฿-?\\d+$/.test(t)) (o[t] = o[t] || []).push(e.className.replace(/\\s+/g,' ').trim()); }); return o; }""")
        pos_ok = "฿1" in cls and all("pnl-pos" in x for x in cls["฿1"])
        neg_ok = "฿-1" in cls and all("pnl-neg" in x for x in cls["฿-1"])
        zero = cls.get("฿0", [])
        check(f"{tag} 5 P&L +1 → pnl-pos · −1 → pnl-neg (แถว Closed + การ์ดมือถือ)", pos_ok and neg_ok, json.dumps(cls, ensure_ascii=False))
        check(f"{tag} 5 P&L 0 และ −0.4 → แสดง '฿0' ไม่มีคลาส (ไม่มี '฿-0' · กลุ่มรวม +5−5 = 0 ไม่มีคลาส)", len(zero) >= 3 and all(("pnl-pos" not in x and "pnl-neg" not in x) for x in zero) and "฿-0" not in cls, json.dumps(cls, ensure_ascii=False))
        if clock == "02:00" and tz == "Asia/Bangkok":
            shot(page, f"fx-closed-pnl-{w}.png", "#jContent_closed")
        # 6 หน้าต่างแก้ไม้
        hint = {}
        page.evaluate("()=>openTradeEdit('cp1','main')"); page.wait_for_timeout(200)
        for nm, v in (("pos", "101"), ("neg", "99"), ("zero", "100"), ("frac", "99.6")):
            page.fill("#tExitPrice", v); page.wait_for_timeout(80)
            hint[nm] = page.evaluate("()=>{ const b=document.querySelector('#exitHint b'); return b ? {cls:b.className, style:b.getAttribute('style'), t:b.textContent.trim()} : null; }")
        check(f"{tag} 6 หน้าต่างแก้ไม้ 'P&L ≈': ไม่มี inline style สี · คลาสตาม pnlCls (+1 pos · −1 neg · 0/−0.4 ไม่มีคลาส · ไม่มี '-0')",
              all(v and v["style"] is None for v in hint.values()) and hint["pos"]["cls"] == "pnl-pos" and hint["neg"]["cls"] == "pnl-neg" and hint["zero"]["cls"] == "" and hint["frac"]["cls"] == "" and "-0" not in hint["frac"]["t"], json.dumps(hint, ensure_ascii=False))
        page.evaluate("()=>closeTradeEdit()")
        # sheet ปิดไม้บางส่วน
        page.evaluate("()=>openClosePos('cp1','main')") if False else None
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def cp_msg_checks(pw, w, h):
    tag = f"[chromium/{w}]"
    doc, cards = make(extra=[T("op2", "core", "open", sym="OPEN2", entry=100, sl=90, qty=10, date="2026-09-25")])
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        page.evaluate("()=>openClosePos('op2','main')"); page.wait_for_timeout(150)
        out = {}
        for nm, v in (("pos", "110"), ("neg", "95"), ("zero", "100"), ("frac", "99.96")):
            page.fill("#cpExitPrice", v); page.fill("#cpQty", "1" if nm == "frac" else "5"); page.wait_for_timeout(80)
            out[nm] = page.evaluate("()=>{ const b=document.querySelectorAll('#cpPreview b')[1]; return b ? {cls:b.className, t:b.textContent.trim()} : null; }")
        check(f"{tag} B sheet ปิดไม้ (ข้อความปิดบางส่วน): +50 → pnl-pos · −25 → pnl-neg · 0 และ −0.04 → ไม่มีคลาส ไม่มี '-0'", out["pos"]["cls"] == "pnl-pos" and out["neg"]["cls"] == "pnl-neg" and out["zero"]["cls"] == "" and out["frac"]["cls"] == "" and "-0" not in out["frac"]["t"], json.dumps(out, ensure_ascii=False))
    finally:
        browser.close()


def ff_checks(pw, w, h):
    tag = f"[chromium/{w}]"
    doc, cards = make()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards, tz="Asia/Bangkok", iso="2026-09-30T19:00:00Z")
    try:
        p24.go_stock(page)
        def cases(as_of, ups):
            j = None if as_of is None else {"as_of": as_of, "ratios": {"ACWI_BIL": {"up": ups[0]}, "HYG_IEI": {"up": ups[1]}}}
            p24.set_ff(page, j)
            page.evaluate("()=>render()"); page.wait_for_timeout(150)
            head = txt(page, '[data-core-head="main"] [data-c-ffwarn]')
            page.evaluate("coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
            sheet = page.evaluate("()=>{ const e=document.getElementById('cnFwarn'); return e && e.style.display!=='none' ? e.textContent.trim() : null; }")
            fnow = page.evaluate("()=>{ const F = coreFNow(); const C = ffCoreNow(); const ref = Calc.ffCoreCap({acwi:C.reds && C.reds.includes('ACWI/BIL') ? false : (C.missing.includes('ACWI/BIL') ? null : true), hyg:C.reds && C.reds.includes('HYG/IEI') ? false : (C.missing.includes('HYG/IEI') ? null : true), ageDays:C.age}); return {f:F.f, ref:ref.cap/100, age:C.age, demo:C.demo, stale:C.stale}; }")
            return head, sheet, fnow
        h6, s6, f6 = cases("2026-09-23", (True, True))
        check(f"{tag} 7 as_of 6 วันทำการก่อน → แผง Core + sheet แผนใหม่ มี '⚠ Fund-flow เก่า 6 วันทำการ · ไม่ลดขนาดไม้ (100%)'", h6 == "⚠ Fund-flow เก่า 6 วันทำการ · ไม่ลดขนาดไม้ (100%)" and s6 == h6, json.dumps([h6, s6, f6], ensure_ascii=False))
        check(f"{tag} 7 f ที่ใช้คำนวณเท่าเดิม (stale → 100% = Calc.ffCoreCap)", f6["f"] == f6["ref"] == 1 and f6["age"] == 6 and f6["stale"], json.dumps(f6))
        shot(page, f"fx-newplan-ff-stale-{w}.png", ".core-sheet .ui-sheet")
        page.evaluate("coreSheetClose()")
        shot(page, f"fx-core-ff-stale-{w}.png", '[data-core-head="main"]')
        h5, s5, f5 = cases("2026-09-24", (False, True))
        check(f"{tag} 7 as_of 5 วันทำการ → ไม่มีเตือน (ทั้งแผงและ sheet) · f 75% (แดง 1 ตัว) เท่าเดิม", h5 is None and s5 is None and f5["f"] == f5["ref"] == 0.75 and f5["age"] == 5 and not f5["stale"], json.dumps([h5, s5, f5], ensure_ascii=False))
        page.evaluate("coreSheetClose()")
        h0, s0, f0 = cases(None, (True, True))
        check(f"{tag} 7 ไม่มีไฟล์ Fund-flow → '⚠ ยังไม่มีข้อมูล Fund-flow · ไม่ลดขนาดไม้ (…%)' (แผง + sheet) · f เท่า Calc.ffCoreCap", h0 is not None and h0.startswith("⚠ ยังไม่มีข้อมูล Fund-flow · ไม่ลดขนาดไม้ (") and s0 == h0 and f0["demo"] and f0["f"] == f0["ref"], json.dumps([h0, s0, f0], ensure_ascii=False))
        page.evaluate("coreSheetClose()")
        hf, sf, ff = cases("2026-09-30", (True, False))
        check(f"{tag} 7 ไฟล์สด (แดง 1 ตัว) → ไม่มีเตือน · f 75%", hf is None and sf is None and ff["f"] == 0.75, json.dumps([hf, sf, ff], ensure_ascii=False))
        page.evaluate("coreSheetClose()")
        page.evaluate("""()=>{ window.__FF_JSON = {as_of:'2026-09-30', ratios:{HYG_IEI:{up:true}}}; return ffLoadJson(true); }"""); page.wait_for_timeout(300)
        page.evaluate("()=>render()"); page.wait_for_timeout(100)
        hm = txt(page, '[data-core-head="main"] [data-c-ffwarn]')
        check(f"{tag} 7 ขาด ratio (ACWI/BIL) → ชิปเหลือง + ชื่อที่ขาด", hm is not None and "ACWI/BIL" in hm, str(hm))
        ov = page.evaluate("()=>document.documentElement.scrollWidth <= innerWidth + 1 && (()=>{const e=document.getElementById('corePanel'); return e.scrollWidth <= e.clientWidth + 1})()")
        check(f"{tag} 8 แผง Core + ชิปเตือน ไม่ล้นแนวนอน", ov)
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def grep_checks():
    html = open(INDEX, encoding="utf-8").read()
    left = [l.strip()[:120] for l in html.split("\n") if "new Date().toISOString().slice(0,10)" in l and not l.strip().startswith("/*")]
    check("grep: ไม่เหลือ new Date().toISOString().slice(0,10) (วันนี้แบบ UTC) ในโค้ด", not left, str(left))
    check("grep: ไม่เหลือ 'pnl>=0?' / 'totalPnl>=0?' แบบ pnl-pos/pnl-neg เอง", "pnl>=0?'pnl-pos'" not in html and "totalPnl>=0?'pnl-pos'" not in html)
    check("grep: thaiToday / pnlCls / coreFWarn มีอยู่", all(x in html for x in ("function thaiToday", "function pnlCls", "function coreFWarn")))


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (430, 900)):
            label = f"{w}x{h}"
            for tz in ("UTC", "Asia/Bangkok"):
                for clock in ("02:00", "12:00"):
                    date_checks(pw, w, h, tz, clock, label)
            cp_msg_checks(pw, w, h)
            ff_checks(pw, w, h)
    grep_checks()
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:300])
        sys.exit(1)


if __name__ == "__main__":
    main()
