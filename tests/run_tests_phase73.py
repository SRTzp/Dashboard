#!/usr/bin/env python3
"""TR1 — Trade Ideas: ไอเดียเทรดจากข่าว/ธีม (AI vs เรา) ใน Watch › Ideas + ＋ วางแผน เข้า Strategy สัปดาห์ · เทส 73
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย (สัปดาห์นี้ = 2026-09-27) · Playbook ตัวอย่างจาก p68 (XAUUSD ▲ · BTC ▲▬ · BRENT ▬ · USDJPY ▼)
ภาพ tests/screenshots/tr1-{list,summary,vs,product,add,plan-link}-{1440,390}.png
รัน: python3 run_tests_phase73.py"""
import copy, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase44 as P44
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase68 as P68

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
overflow = P54.overflow
WK = "2026-09-27"; TODAY = "2026-10-01"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def fixture(doc):
    P68.fixture(doc)
    s = doc["books"]["main"]["settings"]
    for k in ("BTCUSD", "S50", "BRENT", "XAUUSD"):
        s["brokers"]["XM"].setdefault(k, {"contract": 100, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"})


def trade_ai(**kw):
    d = {"schema": "trade@1", "id": "cxmt-kospi-2026-10", "title": "CXMT กดราคา Memory → KOSPI ▼", "date": "2026-09-30", "expires": "2026-10-14", "asset_hint": "KOSPI200",
         "dir": "short", "tf": "D", "horizon": "1–2 สัปดาห์", "one_line": "ผู้ผลิต Memory จีนขยายกำลังผลิต → ราคา DRAM อาจกดลง → ดัชนีเกาหลีเสี่ยงลง",
         "chain": [{"step": "CXMT ขยาย DDR5/HBM", "note": "ตัวจุดชนวน"}, {"step": "Supply DRAM เพิ่ม"}, {"step": "KOSPI ▼"}],
         "strength": "mid", "counter": ["HBM ยังขาดตลาด"], "wrong_if": ["ราคา DRAM contract ไม่ลง"], "alts": ["Short Samsung แทนดัชนี"],
         "products": [{"name": "KOSPI200 Futures", "type": "futures", "lev": "สูง"}, {"name": "Inverse 2X ETF", "type": "etf_lev", "lev": "2X รายวัน"}, {"name": "Put option ETF เกาหลี", "type": "option", "lev": "Option"}],
         "entry": "Break ใต้แนวรับ D + Vol", "sources": [{"title": "ข่าว CXMT", "url": "https://example.com/cxmt", "date": "2026-09-29"}]}
    d.update(kw); return d


def seed_trade(page, id_, ai=None, me=None, user=None, log=None):
    doc = {"kind": "trade", "ai": ai, "me": me or {}, "user": user or {}, "idea_log": log or []}
    page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "ideas", id_], doc])


def reload_ideas(page):
    js(page, "()=>{ ideaStop(); ideaStart(); }"); page.wait_for_timeout(400)


def launch(pw, w, h, trades=(), invs=()):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture)
    P51.fresh(page, None)
    P11.seed_pb(page, [P68.v2doc()])
    for t in trades: seed_trade(page, *t[0], **t[1]) if isinstance(t[0], tuple) else seed_trade(page, t[0], **t[1])
    for it in invs: P44.seed_idea(page, it)
    reload_ideas(page)
    return browser, page, ce, pe


def go(page, sel=None):
    js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250)
    js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(250)
    if sel: js(page, "(s)=>ideaOpen(s)", sel); page.wait_for_timeout(250)


def tab(page, k): page.click(f'[data-idea-tab="{k}"]'); page.wait_for_timeout(200)
def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def cnt(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def rows(page): return js(page, "()=>[...document.querySelectorAll('[data-idea-rows] .wlR')].map(e=>e.dataset.idea)")
def idb(page, i): return page.evaluate("(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas',i])", i)
def settings(page, k): return P54.settings(page, k)
def picks(page): return js(page, "()=>satWeekPickList()")


def import_text(page, text):
    js(page, "()=>ideaImportOpen()"); page.wait_for_timeout(250)
    page.fill("#ideaJson", text); page.click("[data-idea-check]"); page.wait_for_timeout(250)
    return txt(page, "#ideaErrBox") or ""


def import_save(page):
    page.click("[data-idea-save]"); page.wait_for_timeout(500)


def parse_err(page, o):
    return js(page, "(t)=>{ const r = ideaParse(t); return r.err || ('OK:' + (r.items||[]).length); }", json.dumps(o))


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 Import trade@1 · ตัวกรองประเภท · error
    browser, page, ce, pe = launch(pw, w, h, invs=[P44.semis()])
    try:
        go(page)
        check(f"{tag} 1 ตัวกรองประเภท 'ทั้งหมด · เทรด n · ลงทุน n' ขึ้นเหนือตัวกรองสถานะ (เริ่ม เทรด 0 · ลงทุน 1)", txt(page, "[data-trade-kinds]").startswith("ทั้งหมด เทรด 0 ลงทุน 1") and cnt(page, "[data-idea-filters]") == 1, txt(page, "[data-trade-kinds]"))
        err = import_text(page, json.dumps(trade_ai()))
        check(f"{tag} 1 Import trade@1 ตรวจผ่าน → ตัวอย่างบอกสร้างใหม่ (ไม่มี error)", err == "" and "สร้างไอเดียเทรดใหม่" in (txt(page, "[data-trade-prev]") or ""), [err, txt(page, "[data-trade-prev]")])
        import_save(page)
        d = idb(page, "cxmt-kospi-2026-10")
        check(f"{tag} 1 บันทึก → kind:'trade' · ai เก็บ JSON · me ว่าง · สถานะ ร่าง", d and d["kind"] == "trade" and d["ai"]["title"].startswith("CXMT") and d["me"] == {} and d["user"].get("status") == "draft" and len(d["idea_log"]) == 1, json.dumps(d, ensure_ascii=False)[:300])
        check(f"{tag} 1 แถวขึ้นในรายการ · ป้าย 'เทรด' · Short · AI · pill Ideas 2", "cxmt-kospi-2026-10" in rows(page) and js(page, "()=>ideaKind") == "trade" and "Ideas 2" in txt(page, ".wlPills"), rows(page))
        js(page, "()=>ideaSetKind('inv')"); page.wait_for_timeout(250)
        check(f"{tag} 1 ตัวกรอง ลงทุน → เห็นเฉพาะไอเดีย idea@1 เดิม (ไม่มีแถวเทรด)", rows(page) == ["semis-ai-memory-2026"] and cnt(page, "[data-trade]") == 0, rows(page))
        js(page, "()=>ideaSetKind('trade')"); page.wait_for_timeout(250)
        check(f"{tag} 1 ตัวกรอง เทรด → เห็นเฉพาะไอเดียเทรด", rows(page) == ["cxmt-kospi-2026-10"], rows(page))
        js(page, "()=>ideaSetKind('all')"); page.wait_for_timeout(250)
        check(f"{tag} 1 ตัวกรอง ทั้งหมด → ทั้งสองประเภทอยู่ด้วยกัน · นับ เทรด 1 ลงทุน 1", sorted(rows(page)) == ["cxmt-kospi-2026-10", "semis-ai-memory-2026"] and txt(page, "[data-trade-kinds]").startswith("ทั้งหมด เทรด 1 ลงทุน 1"), txt(page, "[data-trade-kinds]"))
        inv_ok = js(page, "()=>{ ideaOpen('semis-ai-memory-2026'); return !!document.querySelector('[data-idea-tabs] [data-idea-tab=mech]') && !document.querySelector('[data-trade-tabs]'); }")
        check(f"{tag} 1 ไอเดีย idea@1 เดิมเปิดแล้วหน้าตาเดิม (แท็บ สรุป/กลไก/หลักฐาน…) ไม่ปนแท็บเทรด", inv_ok)
        shot(page, f"tr1-list-{sfx}.png", ".wlm")
        bad = {"dir": trade_ai(dir="up"), "tf": trade_ai(tf="1H"), "id": trade_ai(id="Bad ID!"), "expires": trade_ai(expires="2026-09-01"), "one_line": trade_ai(one_line="ก" * 121),
               "schema": trade_ai(schema="trade@2"), "title": trade_ai(title=""), "strength": trade_ai(strength="huge"), "ptype": trade_ai(products=[{"name": "x", "type": "bogus"}])}
        errs = {k: parse_err(page, o) for k, o in bad.items()}
        check(f"{tag} 1 JSON ผิด (dir/tf/id/expires/one_line/schema/title/strength/products.type) → error ชัดเจนทุกข้อ", all(not v.startswith("OK:") for v in errs.values()) and "dir" in errs["dir"] and "tf" in errs["tf"] and "id" in errs["id"] and "expires" in errs["expires"], errs)
        e2 = import_text(page, json.dumps(trade_ai(id="cxmt-new", dir="sideways")))
        check(f"{tag} 1 Import UI: dir ผิด → ขึ้นข้อความ error ในกล่อง · ไม่มีปุ่มบันทึก", "dir" in e2 and js(page, "()=>document.getElementById('ideaSaveBtn').style.display") == "none", e2)
        js(page, "()=>ideaSheetClose()")
        e3 = parse_err(page, {"schema": "trade-batch@1", "date": "2026-10-01", "ideas": [trade_ai(id=f"b{i}") for i in range(4)]})
        check(f"{tag} 1 trade-batch@1 เกิน 3 ไอเดีย → error", "0–3" in e3, e3)
        e4 = parse_err(page, trade_ai(id="semis-ai-memory-2026"))
        check(f"{tag} 1 id ชนกับไอเดียลงทุน (idea@1) → error", "ซ้ำกับไอเดียลงทุน" in e4, e4)
        check(f"{tag} 1 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()

    # ── 2 ＋ ไอเดียเทรด (⑦)
    browser, page, ce, pe = launch(pw, w, h)
    try:
        go(page)
        check(f"{tag} 2 ว่าง: ไม่มีแถว · ปุ่ม ＋ ไอเดียเทรด อยู่ในแถวตัวกรอง · ปุ่ม ＋ ไอเดีย (ลงทุน) เดิมยังอยู่", cnt(page, "[data-trade-new]") == 1 and cnt(page, "[data-idea-new-top]") == 1)
        page.click("[data-trade-new]"); page.wait_for_timeout(250)
        page.fill("[data-trade-new-news]", "https://example.com/news1"); page.fill("[data-trade-new-chain]", "CXMT → DRAM → Samsung → KOSPI")
        page.click("[data-trade-new-save]"); page.wait_for_timeout(200)
        check(f"{tag} 2 ไม่เลือกทิศ → error 'เลือกทิศ' · ไม่บันทึก", "เลือกทิศ" in (txt(page, "[data-trade-new-err]") or "") and not js(page, "()=>tradeList.length"), txt(page, "[data-trade-new-err]"))
        page.click("[data-trade-new-dir=short]"); page.click("[data-trade-new-tf='W']"); page.fill("[data-trade-new-asset]", "KOSPI")
        shot(page, f"tr1-add-{sfx}.png", "#ltModal")
        page.click("[data-trade-new-save]"); page.wait_for_timeout(500)
        ids = js(page, "()=>tradeList.map(x=>x.id)")
        d = idb(page, ids[0]) if ids else None
        check(f"{tag} 2 บันทึก → kind:'trade' · me.dir=short · tf=W · asset_hint · ai=null", d and d["kind"] == "trade" and d["me"]["dir"] == "short" and d["me"]["tf"] == "W" and d["me"]["asset_hint"] == "KOSPI" and d["ai"] is None, json.dumps(d, ensure_ascii=False)[:300])
        check(f"{tag} 2 chain แยกตาม → เป็น 4 ข้อ", d and [c["step"] for c in d["me"]["chain"]] == ["CXMT", "DRAM", "Samsung", "KOSPI"], d and d["me"].get("chain"))
        check(f"{tag} 2 หมดอายุเริ่มต้น = วันนี้ + 14 วัน ({TODAY} → 2026-10-15)", d and d["user"]["expires"] == "2026-10-15", d and d["user"])
        check(f"{tag} 2 แถวแรกขึ้น · เปิดการ์ดอัตโนมัติ · ผู้ใส่ 'เรา' · จุดเหลือง (ฝั่งเรายังไม่มีผิดเมื่อ? ทิศมีแล้ว → เทา/เหลืองตามกติกา)", cnt(page, "[data-trade]") == 1 and txt(page, "[data-trade-who]") == "เรา" and js(page, "()=>ideaSel") == ids[0])
        v = js(page, "()=>trdView(tradeList[0]).dot")
        check(f"{tag} 2 จุด: ทิศมีแล้ว ไม่มี AI ไม่มี gap · อีกกว่า 3 วัน → เทา (n)", v == "n", v)
        if w <= 480: js(page, "()=>wlBack()"); page.wait_for_timeout(250)
        page.click("[data-trade-new]"); page.wait_for_timeout(250)
        page.fill("[data-trade-new-news]", "ข่าวสอง"); page.click("[data-trade-new-dir=long]"); page.click("[data-trade-new-savecopy]"); page.wait_for_timeout(600)
        pr = js(page, "()=>window.__trdLastPrompt || ''")
        id2 = [i for i in js(page, "()=>tradeList.map(x=>x.id)") if i != ids[0]][0]
        check(f"{tag} 2 บันทึก + คัดลอก prompt → prompt มี id · 'trade-check' · 'trade@1 id: <id>'", id2 in pr and "trade-check" in pr and f"trade@1 id: {id2}" in pr, pr[:300])
        check(f"{tag} 2 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()

    # ── 3 Import ซ้ำ id เดียวกัน → ai อัปเดต · me/user ไม่เปลี่ยน
    me0 = {"title": "ของฉัน", "date": "2026-09-30", "dir": "long", "tf": "D", "strength": "high", "wrong_if": ["แตกแนวรับ"], "chain": [{"step": "a"}, {"step": "b"}]}
    us0 = {"status": "watch", "product": "KOSPI200 Futures", "expires": "2026-10-20", "ack": {"strength": True}}
    browser, page, ce, pe = launch(pw, w, h, trades=[(("cxmt-kospi-2026-10",), {"ai": trade_ai(), "me": me0, "user": us0})])
    try:
        go(page)
        import_text(page, json.dumps(trade_ai(title="CXMT ฉบับแก้", strength="low", dir="long"))); import_save(page)
        d = idb(page, "cxmt-kospi-2026-10")
        check(f"{tag} 3 Import id เดิม → ai ถูกแทนที่ (title/strength/dir ใหม่)", d["ai"]["title"] == "CXMT ฉบับแก้" and d["ai"]["strength"] == "low" and d["ai"]["dir"] == "long", d["ai"])
        check(f"{tag} 3 me ไม่เปลี่ยน · user ไม่เปลี่ยน (status/product/expires/ack)", d["me"] == me0 and d["user"]["status"] == "watch" and d["user"]["product"] == "KOSPI200 Futures" and d["user"]["expires"] == "2026-10-20" and d["user"]["ack"] == {"strength": True}, [d["me"], d["user"]])
        import_text(page, json.dumps(trade_ai(title="CXMT ฉบับสาม"))); import_save(page)
        d2 = idb(page, "cxmt-kospi-2026-10")
        check(f"{tag} 3 Import ซ้ำอีกรอบ → ai ใหม่ · me/user ยังอยู่ครบ · log เพิ่ม", d2["ai"]["title"] == "CXMT ฉบับสาม" and d2["me"] == me0 and d2["user"]["product"] == "KOSPI200 Futures" and len(d2["idea_log"]) == len(d["idea_log"]) + 1, [d2["ai"]["title"], len(d2["idea_log"])])
        check(f"{tag} 3 ไม่เกิดเอกสารซ้ำ (1 แถวเทรด)", js(page, "()=>tradeList.length") == 1)
    finally: browser.close()

    # ── 4 AI vs เรา
    me4 = {"title": "ไอเดียของฉัน", "date": "2026-09-30", "dir": "long", "tf": "D", "strength": "high", "horizon": "1 สัปดาห์", "wrong_if": ["แตกแนวรับ"]}
    browser, page, ce, pe = launch(pw, w, h, trades=[(("t-vs",), {"ai": trade_ai(id="t-vs"), "me": me4, "user": {"expires": "2026-10-20"}})])
    try:
        go(page, "t-vs"); tab(page, "vs")
        flags = js(page, "()=>[...document.querySelectorAll('[data-trade-row]')].map(r=>[r.dataset.tradeRow, (r.querySelector('[data-trade-flag]')||{dataset:{}}).dataset.tradeFlag||''])")
        check(f"{tag} 4 ทิศต่าง (เรา Long · AI Short) → ต่าง · ความแรงต่าง → ต่าง · ข้อโต้แย้ง/ทางเลือก AI มีแต่เราว่าง → ขาด · ผิดเมื่อเรามีแล้ว → ไม่ขาด", dict(flags) == {"dir": "diff", "strength": "diff", "horizon": "", "counter": "gap", "wrong_if": "", "alts": "gap"}, flags)
        check(f"{tag} 4 badge แท็บ = 4 (ต่าง 2 + ขาด 2)", txt(page, "[data-trade-badge]") == "4", txt(page, "[data-trade-badge]"))
        shot(page, f"tr1-vs-{sfx}.png", ".wlm")
        page.click("[data-trade-ack=dir]"); page.wait_for_timeout(300)
        d = idb(page, "t-vs")
        check(f"{tag} 4 คงของเรา (รับทราบเดิม) ทิศ → ป้ายจางลง+ปุ่มหาย · badge เหลือ 3 · เก็บ user.ack.dir=true · me ไม่เปลี่ยน", cnt(page, "[data-trade-row=dir] [data-trade-flag]:not([data-trade-decided])") == 0 and cnt(page, "[data-trade-ack=dir]") == 0 and txt(page, "[data-trade-badge]") == "3" and d["user"]["ack"].get("dir") is True and d["me"]["dir"] == "long", [txt(page, "[data-trade-badge]"), d["user"]])
        page.click("[data-trade-use=counter]"); page.wait_for_timeout(300)
        d = idb(page, "t-vs")
        check(f"{tag} 4 ← ใช้ของ AI (ข้อโต้แย้ง) → me.counter = ค่า AI เฉพาะแถวนั้น · แถวอื่นของ me ไม่เปลี่ยน · แถว ขาด หาย · badge 2", d["me"]["counter"] == ["HBM ยังขาดตลาด"] and d["me"]["dir"] == "long" and d["me"]["strength"] == "high" and not d["me"].get("alts") and cnt(page, "[data-trade-row=counter] [data-trade-flag]") == 0 and cnt(page, "[data-trade-use=counter]") == 0 and txt(page, "[data-trade-badge]") == "2", [d["me"], txt(page, "[data-trade-badge]")])
        page.click("[data-trade-me=alts]"); page.wait_for_timeout(200)
        page.fill("#trdEditIn", "ทางของฉัน 1\nทางของฉัน 2"); page.keyboard.press("Enter"); page.wait_for_timeout(300)   # TR1fix: แตะช่อง "เรา" แก้ inline · Enter = บันทึก (แทนปุ่ม เขียนของเรา/บันทึก)
        d = idb(page, "t-vs")
        check(f"{tag} 4 แก้ช่องเรา inline (ทางเลือก) → me.alts 2 ข้อ · ไม่แตะ ai · แถว ขาด หาย", d["me"]["alts"] == ["ทางของฉัน 1", "ทางของฉัน 2"] and d["ai"]["alts"] == ["Short Samsung แทนดัชนี"] and cnt(page, "[data-trade-row=alts] [data-trade-flag]") == 0, d["me"])
        check(f"{tag} 4 ไม่มีอะไรเขียนทับ me ที่ผู้ใช้ไม่ได้กด (Import ใหม่ไม่แตะ me ตรวจในข้อ 3)", d["me"]["strength"] == "high" and d["me"]["horizon"] == "1 สัปดาห์")
        check(f"{tag} 4 {label} ตาราง AI vs เรา ไม่ล้นแนวนอน", overflow(page) <= 1 and js(page, "()=>{ const t = document.querySelector('[data-trade-vs]'); return t.scrollWidth <= t.parentElement.clientWidth + 1; }"), [overflow(page)])
    finally: browser.close()
    browser, page, ce, pe = launch(pw, w, h, trades=[(("t-noai",), {"ai": None, "me": {"title": "เรา", "dir": "long", "date": "2026-09-30"}, "user": {"expires": "2026-10-20"}})])
    try:
        go(page, "t-noai"); tab(page, "vs")
        check(f"{tag} 4 ไม่มีฝั่ง AI → คอลัมน์ AI = '— ยังไม่ได้ขอ AI มอง' · ไม่มีป้าย ต่าง/ขาด", "ยังไม่ได้ขอ AI มอง" in (txt(page, "[data-trade-vs]") or "") and cnt(page, "[data-trade-flag]") == 0 and cnt(page, "[data-trade-use]") == 0)
    finally: browser.close()

    # ── 5 ＋ วางแผน
    def plan_launch(trades):
        b, p, c, e = launch(pw, w, h, trades=trades); return b, p, c, e
    browser, page, ce, pe = plan_launch([(("t-p1",), {"ai": None, "me": {"title": "ไม่มีผิดเมื่อ", "dir": "long", "date": "2026-09-30", "asset_hint": "XAUUSD"}, "user": {"expires": "2026-10-20"}})])
    try:
        go(page, "t-p1")
        dis = js(page, "()=>document.querySelector('[data-trade-plan]').disabled")
        check(f"{tag} 5 ไม่มี 'ผิดเมื่อ' ของเรา → ปุ่ม ＋ วางแผน ปิด + ข้อความ 'เขียนทิศ และ \"ผิดเมื่อ\" ของเราก่อน'", dis and (txt(page, "[data-trade-plan-hint]") or "") == 'เขียนทิศ และ "ผิดเมื่อ" ของเราก่อน', txt(page, "[data-trade-plan-hint]"))
        js(page, "()=>trdPlan('t-p1')"); page.wait_for_timeout(250)
        check(f"{tag} 5 เรียกตรงก็ไม่ผ่าน (ไม่มี pick · ไม่มีแผน)", picks(page) == [] and js(page, "()=>satIdeasList.filter(x=>x.idea_id).length") == 0)
    finally: browser.close()
    browser, page, ce, pe = plan_launch([(("t-p2",), {"ai": trade_ai(id="t-p2", asset_hint="XAUUSD", dir="long"), "me": {"title": "Fed ลดดอก → ทองขึ้น", "dir": "long", "date": "2026-09-30", "asset_hint": "XAUUSD", "wrong_if": ["Fed เซอร์ไพรส์เหยี่ยว"], "one_line": "Fed ลดดอกเบี้ย ทองขึ้นต่อ"}, "user": {"expires": "2026-10-20"}})])
    try:
        go(page, "t-p2")
        page.click("[data-trade-plan]"); page.wait_for_timeout(500)
        pl = js(page, "()=>satIdeasList.filter(x=>x.idea_id==='t-p2').map(x=>({asset:x.asset, bias:x.bias, week:x.week, note:x.macro_note||null, id:x.id}))")
        check(f"{tag} 5 (ก) Asset มีใน Sat (XAUUSD ตรง asset_hint) → เพิ่มเข้า pick สัปดาห์นี้ · สร้างแผน Long · idea_id เก็บ", picks(page) == ["XAUUSD"] and len(pl) == 1 and pl[0]["asset"] == "XAUUSD" and pl[0]["bias"] == "Long" and pl[0]["week"] == WK, [picks(page), pl])
        check(f"{tag} 5 Playbook XAUUSD ▲ + Long = ตาม Macro → ไม่ต้องมี macro_note", pl[0]["note"] is None and js(page, "()=>trdView(tradeList[0]).mac.align") == "with", pl)
        d = idb(page, "t-p2")
        check(f"{tag} 5 ไอเดีย → ในแผน · user.sat_key/week/plan_id · log เพิ่ม · ปุ่มเป็น '✓ สัปดาห์นี้'", d["user"]["status"] == "planned" and d["user"]["sat_key"] == "XAUUSD" and d["user"]["week"] == WK and d["user"]["plan_id"] == pl[0]["id"], d["user"])
        check(f"{tag} 5 ไปหน้า Strategy (แท็บแผน) หลังวางแผน", js(page, "()=>activeTab") == "plan")
        link = js(page, "()=>!!document.querySelector('[data-trade-planlink=\"t-p2\"]')")
        shot(page, f"tr1-plan-link-{sfx}.png", "#satV3Panel")
        check(f"{tag} 5 การ์ดแผนมีลิงก์ '💡 ไอเดียต้นเรื่อง'", link and "ไอเดียต้นเรื่อง" in (txt(page, "[data-trade-planlink]") or ""))
        page.click("[data-trade-planlink] button"); page.wait_for_timeout(400)
        check(f"{tag} 5 แตะลิงก์ → ไปการ์ดไอเดียใน Watch › Ideas", js(page, "()=>activeTab==='watch' && wlView==='idea' && ideaSel==='t-p2'") and txt(page, "[data-trade-planned]") == "✓ สัปดาห์นี้", txt(page, "[data-trade-planned]"))
        row = txt(page, "[data-trade='t-p2'] [data-trade-due]")
        check(f"{tag} 5 รายการ: ขวา '✓ สัปดาห์นี้' · จุดเขียว · สถานะ ในแผน", row == "✓ สัปดาห์นี้" and js(page, "()=>document.querySelector('[data-trade=\"t-p2\"] [data-trade-dot]').dataset.tradeDot") == "g" and txt(page, "[data-trade-status]") == "ในแผน", [row])
    finally: browser.close()
    # (ข) ยังไม่มีใน Sat → sheet AS1 · สวน Macro → macro_note
    me_b = {"title": "ยูโรเยนลง", "dir": "long", "date": "2026-09-30", "asset_hint": "USDJPY", "wrong_if": ["BoJ ไม่ขยับ"], "one_line": "ข้อความหนึ่งบรรทัดที่ใช้เป็นเหตุผลสวน Macro " + "ก" * 90}
    browser, page, ce, pe = plan_launch([(("t-p3",), {"ai": None, "me": me_b, "user": {"expires": "2026-10-20"}})])
    try:
        go(page, "t-p3")
        page.click("[data-trade-plan]"); page.wait_for_timeout(500)
        sheet = js(page, "()=>document.getElementById('sat7dBrokerOverlay').classList.contains('show')")
        row = js(page, "()=>{ const r = document.querySelector('#sat7dBrokerOverlay [data-as-row=USDJPY], #sat7dBrokerOverlay [data-as-key=USDJPY]'); return !!r || document.getElementById('sat7dBrokerOverlay').innerText.includes('USDJPY'); }")
        check(f"{tag} 5 (ข) ยังไม่มีใน Sat → เปิด sheet เพิ่มสินค้า (AS1) เติม key USDJPY ให้ · ยังไม่เข้า pick จนกว่าจะบันทึก", sheet and row and picks(page) == [], [sheet, row, picks(page)])
        page.click("#sat7dBrokerOverlay [data-br-save]"); page.wait_for_timeout(600)
        pl = js(page, "()=>satIdeasList.filter(x=>x.idea_id==='t-p3').map(x=>({asset:x.asset, bias:x.bias, note:x.macro_note||''}))")
        check(f"{tag} 5 บันทึกสินค้า → เข้า pick สัปดาห์นี้ (USDJPY) · สร้างแผนผูกไอเดีย", picks(page) == ["USDJPY"] and len(pl) == 1 and settings(page, "satCustomAssets") and any(c["key"] == "USDJPY" for c in settings(page, "satCustomAssets")), [picks(page), pl])
        check(f"{tag} 5 Playbook USDJPY ▼ + Long = สวน Macro → macro_note เติมจาก one_line ตัดเหลือ ≤ 80 ตัว", len(pl) == 1 and 0 < len(pl[0]["note"]) <= 80 and pl[0]["note"].startswith("ข้อความหนึ่งบรรทัด") and js(page, "()=>trdView(tradeList[0]).mac.align") == "against", pl)
    finally: browser.close()
    # นอก Macro + ครบ 3
    me_c = {"title": "ไอเดีย S50", "dir": "short", "date": "2026-09-30", "asset_hint": "S50", "wrong_if": ["x"], "one_line": "S50 ลง"}
    browser, page, ce, pe = plan_launch([(("t-p4",), {"ai": None, "me": me_c, "user": {"expires": "2026-10-20"}})])
    try:
        js(page, "()=>{ ['XAUUSD','BTCUSD','BRENT'].forEach(k=>satWeekPickAdd(k)); }"); page.wait_for_timeout(300)
        go(page, "t-p4")
        page.click("[data-trade-plan]"); page.wait_for_timeout(400)
        check(f"{tag} 5 pick ครบ 3 แล้ว → ข้อความเดิมของ MF1 'สัปดาห์นี้ครบ 3 ตัวแล้ว' · ไม่สร้างแผน · ไม่ไป Strategy", "ครบ 3 ตัวแล้ว" in (txt(page, "[data-trade-msg]") or "") and js(page, "()=>satIdeasList.filter(x=>x.idea_id).length") == 0 and js(page, "()=>activeTab") == "watch", txt(page, "[data-trade-msg]"))
        js(page, "()=>satWeekPickRemove('BRENT')"); page.wait_for_timeout(200)
        page.click("[data-trade-plan]"); page.wait_for_timeout(500)
        pl = js(page, "()=>satIdeasList.filter(x=>x.idea_id==='t-p4').map(x=>({asset:x.asset, note:x.macro_note||''}))")
        check(f"{tag} 5 S50 ไม่อยู่ใน Playbook → นอก Macro → macro_note เติมจาก one_line", pl and pl[0]["asset"] == "S50" and pl[0]["note"] == "S50 ลง" and js(page, "()=>trdView(tradeList[0]).mac.txt") == "นอก Macro", pl)
        check(f"{tag} 5 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()

    # ── 6 trade-batch@1 3 ไอเดีย
    browser, page, ce, pe = launch(pw, w, h)
    try:
        go(page)
        batch = {"schema": "trade-batch@1", "date": "2026-10-01", "ideas": [trade_ai(id=f"b-{i}", title=f"ไอเดีย {i}", dir=("long" if i % 2 else "short")) for i in range(3)]}
        err = import_text(page, json.dumps(batch)); import_save(page)
        ids = sorted(js(page, "()=>tradeList.map(x=>x.id)"))
        check(f"{tag} 6 batch 3 ไอเดีย → 3 ร่าง ฝั่ง AI เท่านั้น (me ว่าง · ผู้ใส่ AI)", err == "" and ids == ["b-0", "b-1", "b-2"] and all(idb(page, i)["me"] == {} and idb(page, i)["ai"] is not None for i in ids) and js(page, "()=>[...document.querySelectorAll('[data-trade-who]')].map(e=>e.textContent)") == ["AI", "AI", "AI"], [err, ids])
        check(f"{tag} 6 ทั้ง 3 จุดเหลือง (ฝั่งเรายังว่าง) · สถานะ ร่าง", js(page, "()=>[...document.querySelectorAll('[data-trade-dot]')].map(e=>e.dataset.tradeDot)") == ["y", "y", "y"] and js(page, "()=>[...document.querySelectorAll('[data-trade-st]')].map(e=>e.dataset.tradeSt)") == ["draft"] * 3)
        e0 = import_text(page, json.dumps({"schema": "trade-batch@1", "date": "2026-10-01", "ideas": []}))
        check(f"{tag} 6 batch 0 ไอเดีย → ตรวจผ่าน แต่บอกว่าไม่มีอะไรให้บันทึก", e0 == "" and "ไม่มีไอเดียในไฟล์นี้" in (txt(page, "[data-trade-prev]") or ""), e0)
        js(page, "()=>ideaSheetClose()")
        check(f"{tag} 6 หมายเหตุ AI เสนอ 0–3 รายสัปดาห์: ไม่เกิน 3 แถวใหม่ต่อ batch", len(ids) == 3)
    finally: browser.close()

    # ── 7 หมดอายุ
    browser, page, ce, pe = launch(pw, w, h, trades=[(("t-soon",), {"ai": trade_ai(id="t-soon"), "me": {"title": "ใกล้หมด", "dir": "short", "date": "2026-09-20", "wrong_if": ["x"]}, "user": {"expires": "2026-09-29"}}),
                                                      (("t-old",), {"ai": None, "me": {"title": "หมดแล้ว", "dir": "short", "date": "2026-09-10", "wrong_if": ["x"]}, "user": {"expires": "2026-09-25"}}),
                                                      (("t-far",), {"ai": None, "me": {"title": "ไกล", "dir": "short", "date": "2026-09-30", "wrong_if": ["x"]}, "user": {"expires": "2026-10-25"}})])
    try:
        go(page)
        info = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-trade]')].map(e=>[e.dataset.trade, [e.querySelector('[data-trade-dot]').dataset.tradeDot, e.querySelector('[data-trade-st]').dataset.tradeSt]]))")
        check(f"{tag} 7 หมดอายุ −2 วัน (29 ก.ย. · วันนี้ 1 ต.ค.) → เหลือง · สถานะหมดอายุ · เลยแล้ว (25 ก.ย.) → เหลือง + หมดอายุ · ไกล → เทา", info == {"t-soon": ["y", "expired"], "t-old": ["y", "expired"], "t-far": ["n", "draft"]}, info)
        check(f"{tag} 7 ขวาของแถว: 'หมดอายุแล้ว 29 ก.ย.' / 'หมดอายุ 25 ต.ค.'", txt(page, "[data-trade='t-soon'] [data-trade-due]") == "หมดอายุแล้ว 29 ก.ย." and txt(page, "[data-trade='t-far'] [data-trade-due]") == "หมดอายุ 25 ต.ค.", txt(page, "[data-trade='t-soon'] [data-trade-due]"))
        js(page, "()=>ideaOpen('t-old')"); page.wait_for_timeout(250); tab(page, "go")
        check(f"{tag} 7 แท็บ เข้า/ยกเลิก: ป้าย 'หมดอายุแล้ว' + ปุ่ม 'ต่ออายุ 1 สัปดาห์'", cnt(page, "[data-trade-expired]") == 1 and cnt(page, "[data-trade-renew]") == 1)
        page.click("[data-trade-renew]"); page.wait_for_timeout(350)
        d = idb(page, "t-old")
        check(f"{tag} 7 ต่ออายุ 1 สัปดาห์ → เริ่มนับจากวันนี้ (1 ต.ค. + 7 = 8 ต.ค.) · สถานะกลับเป็นร่าง · ป้ายหมดอายุหาย", d["user"]["expires"] == "2026-10-08" and cnt(page, "[data-trade-expired]") == 0 and txt(page, "[data-trade-status]") == "ร่าง", [d["user"], txt(page, "[data-trade-status]")])
        js(page, "()=>ideaOpen('t-far')"); page.wait_for_timeout(250); tab(page, "go")
        page.click("[data-trade-renew]"); page.wait_for_timeout(300)
        check(f"{tag} 7 ต่ออายุที่ยังไม่หมด → ต่อจากวันหมดเดิม (25 ต.ค. + 7 = 1 พ.ย.)", idb(page, "t-far")["user"]["expires"] == "2026-11-01", idb(page, "t-far")["user"])
        js(page, "()=>trdSetExpiry('t-far','2026-12-01')"); page.wait_for_timeout(250)
        check(f"{tag} 7 แก้วันหมดอายุเองได้ (ช่องวันที่)", idb(page, "t-far")["user"]["expires"] == "2026-12-01")
    finally: browser.close()

    # ── 8 Product
    browser, page, ce, pe = launch(pw, w, h, trades=[(("t-pr",), {"ai": trade_ai(id="t-pr"), "me": {"title": "พร็อด", "dir": "short", "date": "2026-09-30", "wrong_if": ["x"]}, "user": {"expires": "2026-10-20"}})])
    try:
        go(page, "t-pr"); tab(page, "prod")
        check(f"{tag} 8 Product จาก ai.products 3 ตัว · type etf_lev → กล่องเตือน decay · option → ป้าย 'Option · นอก Sat'", cnt(page, "[data-trade-prod]") == 3 and cnt(page, "[data-trade-decay]") == 1 and "reset รายวัน" in (txt(page, "[data-trade-decay]") or "") and txt(page, "[data-trade-opt]") == "Option · นอก Sat", [cnt(page, "[data-trade-prod]"), txt(page, "[data-trade-opt]")])
        page.click("[data-trade-pick='KOSPI200 Futures']"); page.wait_for_timeout(300)
        d = idb(page, "t-pr")
        check(f"{tag} 8 เลือก 1 ตัว → user.product = ชื่อนั้น · ป้าย 'เลือก' ย้ายตาม (เลือกได้ทีละตัว)", d["user"]["product"] == "KOSPI200 Futures" and cnt(page, "[data-trade-picked]") == 1, d["user"])
        page.fill("[data-trade-prod-name]", "CFD Korea 200"); page.select_option("[data-trade-prod-type]", "cfd"); page.fill("[data-trade-prod-lev]", "≈ 1:20"); page.click("[data-trade-prod-add]"); page.wait_for_timeout(350)
        d = idb(page, "t-pr")
        check(f"{tag} 8 เพิ่ม Product เอง → me.products มี 1 · ขึ้นในรายการ (รวม 4)", len(d["me"]["products"]) == 1 and d["me"]["products"][0]["type"] == "cfd" and cnt(page, "[data-trade-prod]") == 4, d["me"])
        page.fill("[data-trade-prod-name]", "cfd korea 200"); page.click("[data-trade-prod-add]"); page.wait_for_timeout(250)
        check(f"{tag} 8 ชื่อซ้ำ → error ไม่เพิ่ม", "มี Product ชื่อนี้แล้ว" in (txt(page, "[data-trade-prod-err]") or "") and cnt(page, "[data-trade-prod]") == 4)
        shot(page, f"tr1-product-{sfx}.png", ".wlm")
        check(f"{tag} 8 {label} ไม่ล้น", overflow(page) <= 1, overflow(page))
    finally: browser.close()

    # ── 9 คีย์ Ideas · ไอเดีย idea@1 เดิม
    browser, page, ce, pe = launch(pw, w, h, trades=[(("t-k1",), {"ai": trade_ai(id="t-k1"), "me": {"title": "คีย์ 1", "dir": "short", "date": "2026-10-01", "wrong_if": ["x"]}, "user": {"expires": "2026-10-25"}}),
                                                      (("t-k2",), {"ai": None, "me": {"title": "คีย์ 2", "dir": "long", "date": "2026-09-30", "wrong_if": ["x"]}, "user": {"expires": "2026-10-25"}})], invs=[P44.semis()])
    try:
        go(page)
        order = rows(page)
        page.keyboard.press("Escape")
        js(page, "()=>ideaOpen('t-k1')"); page.wait_for_timeout(250)
        if w > 480:
            page.keyboard.press("ArrowRight"); page.wait_for_timeout(200)
            check(f"{tag} 9 → เปลี่ยนแท็บการ์ดเทรด สรุป → AI vs เรา (ตามรายการแท็บของเทรด ไม่ใช่ของลงทุน)", js(page, "()=>ideaSubMem('t-k1')") == "vs" and cnt(page, "[data-trade-vs]") == 1)
            page.keyboard.press("ArrowRight"); page.keyboard.press("ArrowRight"); page.keyboard.press("ArrowRight"); page.wait_for_timeout(200)
            check(f"{tag} 9 → ซ้ำ หยุดที่แท็บสุดท้าย (เข้า/ยกเลิก) ไม่วน", js(page, "()=>ideaSubMem('t-k1')") == "go")
            page.keyboard.press("ArrowLeft"); page.wait_for_timeout(200)
            check(f"{tag} 9 ← ถอยแท็บ", js(page, "()=>ideaSubMem('t-k1')") == "prod")
            before = js(page, "()=>ideaSel")
            page.keyboard.press("ArrowDown"); page.wait_for_timeout(200)
            idx = order.index(before)
            check(f"{tag} 9 ↓ เลื่อนไอเดียถัดไปในรายการผสม (เทรด+ลงทุน)", js(page, "()=>ideaSel") == order[min(idx + 1, len(order) - 1)], [before, order])
            page.keyboard.press("ArrowUp"); page.wait_for_timeout(200)
            check(f"{tag} 9 ↑ กลับ", js(page, "()=>ideaSel") == before)
        else:
            check(f"{tag} 9 มือถือ: เปิดการ์ดแล้วมีปุ่ม ‹ Ideas กลับรายการ", js(page, "()=>!!document.querySelector('.wlBackBtn')") and js(page, "()=>wlMobOpen"))
            js(page, "()=>wlBack()"); page.wait_for_timeout(250)
            check(f"{tag} 9 มือถือ: กลับแล้วเห็นรายการ (ไม่ล้น)", cnt(page, "[data-idea-rows]") == 1 and overflow(page) <= 1)
        js(page, "()=>{ ideaOpen('semis-ai-memory-2026'); }"); page.wait_for_timeout(250)
        if w > 480:
            page.keyboard.press("ArrowRight"); page.wait_for_timeout(200)
            check(f"{tag} 9 ไอเดียลงทุนเดิม: → ไปแท็บกลไก (ยังใช้ชุดแท็บเดิม)", js(page, "()=>ideaSubMem('semis-ai-memory-2026')") == "mech")
        js(page, "()=>ideaCycleFilter(1)"); page.wait_for_timeout(250)
        check(f"{tag} 9 [ ] วนตัวกรองสถานะเดิมยังทำงาน (need_evidence)", js(page, "()=>ideaFilter") == "need_evidence")
        check(f"{tag} 9 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: browser.close()

    # ── 10 สรุป (ภาพ) + ที่มา + ⋯ เมนู
    browser, page, ce, pe = launch(pw, w, h, trades=[(("t-sum",), {"ai": trade_ai(id="t-sum"), "me": {"title": "สรุป", "news": "https://example.com/n", "dir": "short", "date": "2026-09-30", "wrong_if": ["ผิดตรงนี้"], "chain": [{"step": "A"}, {"step": "B"}, {"step": "KOSPI ▼"}]}, "user": {"expires": "2026-10-25"}})])
    try:
        go(page, "t-sum")
        check(f"{tag} 10 สรุป: หนึ่งบรรทัด · ห่วงโซ่ (ของเราก่อน · จุดท้ายสีตามทิศ) · ที่มา (ลิงก์ · ผู้ใส่ เรา · AI)", "หนึ่งบรรทัด" in (txt(page, "[data-trade-one]") or "") and cnt(page, "[data-trade-chain] li") == 3 and cnt(page, "[data-trade-chain] li.end.dn") == 1 and "ผู้ใส่: เรา" in (txt(page, "[data-trade-src]") or "") and "AI (idea-scout โหมด trade)" in (txt(page, "[data-trade-src]") or "") and cnt(page, "[data-trade-src] a") >= 1, txt(page, "[data-trade-src]"))
        check(f"{tag} 10 ปุ่ม ＋ วางแผน (เปิด · ครบเงื่อนไข) · ขอ AI มอง · ⋯", js(page, "()=>!document.querySelector('[data-trade-plan]').disabled") and cnt(page, "[data-trade-ask]") == 1 and cnt(page, "[data-idea-menu]") == 1 and cnt(page, "[data-trade-plan-hint]") == 0)
        page.click("[data-trade-ask]"); page.wait_for_timeout(400)
        check(f"{tag} 10 ขอ AI มอง → ข้อความ 'คัดลอก prompt แล้ว' + prompt มีฝั่งเรา (ทิศ/ผิดเมื่อ) และคำสั่ง trade@1 id", "คัดลอก prompt แล้ว" in (txt(page, "[data-trade-copymsg]") or "") and "ผิดเมื่อ (เรา): ผิดตรงนี้" in js(page, "()=>window.__trdLastPrompt") and "trade@1 id: t-sum" in js(page, "()=>window.__trdLastPrompt"))
        shot(page, f"tr1-summary-{sfx}.png", ".wlm")
        page.click("[data-idea-menu]"); page.wait_for_timeout(200); page.click("[data-trade-setst=parked]"); page.wait_for_timeout(300)
        check(f"{tag} 10 ⋯ → ตั้งเป็น พัก → สถานะพัก (user.status=parked) · ไม่ขึ้นใน 'ทั้งหมด' · ขึ้นใน ตัวกรอง พัก", idb(page, "t-sum")["user"]["status"] == "parked" and "t-sum" not in rows(page), rows(page))
        js(page, "()=>ideaSetFilter('parked')"); page.wait_for_timeout(250)
        check(f"{tag} 10 ตัวกรองสถานะ พัก เห็นไอเดียเทรดที่พัก", "t-sum" in rows(page), rows(page))
        js(page, "()=>ideaOpen('t-sum')"); page.wait_for_timeout(200)
        page.click("[data-idea-menu]"); page.wait_for_timeout(200); page.click("[data-idea-del]"); page.wait_for_timeout(250); page.click("[data-trade-delok]"); page.wait_for_timeout(400)
        check(f"{tag} 10 ลบ (พัก) → เอกสารหาย · รายการว่าง", idb(page, "t-sum") is None and js(page, "()=>tradeList.length") == 0, idb(page, "t-sum"))
        check(f"{tag} 10 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()


def static_checks():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("static: field kind:'trade' อยู่ที่ users/{uid}/ideas เดิม (ไม่มี collection ใหม่)", "kind:'trade'" in src and "collection('tradeIdeas')" not in src and "collection('trades_ideas')" not in src)
    check("static: Import แยก schema อัตโนมัติ idea@1 / trade@1 / trade-batch@1", "trade-batch@1" in src and "trdParse" in src)
    check("static: เอกสาร schema docs/trade-idea-schema.md มีอยู่", os.path.exists(os.path.join(HERE, "..", "docs", "trade-idea-schema.md")))


if __name__ == "__main__":
    static_checks()
    with sync_playwright() as pw:
        for (w, h, label) in [(1440, 900, "1440px"), (390, 844, "390px")]:
            tests(pw, w, h, label)
    bad = [r for r in results if not r[1]]
    print(f"engine={ENGINE}  PASS: {len(results)-len(bad)}  FAIL: {len(bad)}  TOTAL: {len(results)}")
    if bad: print("FAILURES:"); [print(" -", r[0]) for r in bad]
