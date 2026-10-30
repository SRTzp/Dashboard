#!/usr/bin/env python3
"""CL2-c — หน้าต่าง "แก้ไม้" ใหม่ (openTradeEdit) · ลบฟอร์ม Add Trade · แถวหัวแบบย่อ · ซ่อนทางเข้า Add Trade
mock Firestore (ไม่ต่อเน็ต) · 1440px + 430px (หน้าต่าง) · 1440 + 430 + 375 (แถวหัว) · seed.json + ไม้ที่ใส่เองในเทส
รัน: python3 run_tests_phase21.py [/path/to/index.html] · ภาพเก็บที่ tests/screenshots/cl2c-*.png"""
import copy, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
UID = "testuid"
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))
results = []


def retired(name, reason):
    """CL2-d — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่พิมพ์ไว้ให้ตามรอย (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


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


def T(id, port, status, **kw):
    d = {"id": id, "date": "2026-09-01", "sym": id.upper(), "port": port, "bias": "Long", "entry": 100, "sl": 90, "tp": None, "qty": 10,
         "mult": 1, "cur": "THB", "status": status, "unplanned": False}
    d.update(kw); return d


def make_doc():
    doc = copy.deepcopy(SEED)
    doc["books"]["main"]["trades"] = [
        # A: Sat open + ฟิลด์ที่ makeTradeObject ไม่รู้จัก (_probeT) + setups/condition_id/trend_state ที่ต้องอยู่ครบหลังแก้
        T("ta", "satB", "open", sym="XAUUSD", date="2026-09-20", openedAt="2026-09-20", entry=2650, sl=2620, tp=2700, qty=0.19, mult=100, cur="USD",
          setups=["s1", "s2"], condition_id="c1", entry_condition="ราคายืนเหนือ 2640", trend_state="up", _probeT="x", plannedEntry=2648),
        # B: Core closed ยังไม่มีคะแนน
        T("tb", "core", "closed", sym="NVDA", date="2026-09-01", entry=100, sl=90, qty=10, exitPrice=120, exitDate="2026-09-10", cur="THB"),
        # C: Sat plan
        T("tc", "satB", "plan", sym="BRENT", date="2026-09-25", entry=2600, sl=2580, qty=0.1, mult=100, cur="USD"),
        # D: Core cancelled
        T("td", "core", "cancelled", sym="CANCX", date="2026-09-05", cancelDate="2026-09-12", cancelNote="เปลี่ยนใจ", cancelTag="other", parentId="pp1"),
    ]
    doc["books"]["fam"]["trades"] = [T("tf", "core", "closed", sym="FAMX", date="2026-09-01", entry=50, sl=45, qty=100, exitPrice=60, exitDate="2026-09-15", fills=[{"q": 100}])]
    return doc


def launch(pw, w, h, doc, path=None):
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
    page.goto("file://" + (path or INDEX), wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("() => localStorage.setItem('bkLastBackupAt', String(Date.now()))")   # กัน backup อัตโนมัติ
    page.evaluate("(d)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], d); }", doc)
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(500)
    return browser, context, page, ce, pe, dialogs


def dump_book(page, acct="main"):
    return page.evaluate("(a)=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return d && d.books && d.books[a]; }", acct)


def present(page, sel): return page.evaluate("(s)=>!!document.querySelector(s)", sel)




def dump_all(page):
    return page.evaluate("() => JSON.stringify(window.firebase.__mockDb.__dump()['users/testuid'])")


def dump_book(page, acct="main"):
    return page.evaluate("(a)=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return d && d.books && d.books[a]; }", acct)


def dtrade(page, id, acct="main"):
    b = dump_book(page, acct)
    return next((t for t in (b or {}).get("trades", []) if t["id"] == id), None)


def present(page, sel): return page.evaluate("(s)=>!!document.querySelector(s)", sel)


def te_open(page): return page.evaluate("() => document.getElementById('teOverlay').classList.contains('show')")


def te_save_disabled(page): return page.evaluate("() => document.getElementById('teSaveBtn').disabled")


def te_err(page): return page.evaluate("() => document.getElementById('teErr').innerText.trim()")


def setv(page, id, v):
    page.fill("#" + id, str(v)); page.wait_for_timeout(40)


def persist(page): page.wait_for_timeout(1900)   # รอ debounce persist


def header_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, make_doc())
    try:
        info = page.evaluate("""() => { const br = document.querySelector('.topbar .brand').getBoundingClientRect();
            const btns = [...document.querySelectorAll('.hbtns>button')].map(b=>{ const r=b.getBoundingClientRect(), cs=getComputedStyle(b), af=getComputedStyle(b,'::after');
                return {on:(b.getAttribute('onclick')||'').split('(')[0], vis: r.width>0 && r.height>0, w:Math.round(r.width*10)/10, h:Math.round(r.height*10)/10, top:r.top, left:r.left, right:r.right,
                        after:af.content, txt:(()=>{ const c=b.cloneNode(true); c.querySelectorAll('svg').forEach(x=>x.remove()); return c.textContent.replace(/\\s+/g,' ').trim(); })(), btnTxt: !!b.querySelector('.btnTxt'), title:b.title, aria:b.getAttribute('aria-label')}; });
            return {brandTop: br.top, brandRight: br.right, btns, sw: document.documentElement.scrollWidth,
                    sync: (()=>{ const e=document.getElementById('brandSync').getBoundingClientRect(); return {l:e.left, r:e.right}; })()}; }""")
        vis = [b for b in info["btns"] if b["vis"]]
        order = [b["on"] for b in info["btns"]]
        check(f"{tag} แถวหัว: ปุ่ม ＋ (goPlanTop · ไม่ใช่ openTrade) ซ้ายสุด · ลำดับ DOM = ＋ · 🛠 · พอร์ต · Industry · ⋯", order == ["goPlanTop", "openSystemSettings", "openSettings", "openIndustryManager", "toggleMoreMenu"], json.dumps(order))
        check(f"{tag} แถวหัว: ไม่มี ::after ข้อความ · ไม่มี .btnTxt · ไม่มีข้อความในปุ่ม", all(b["after"] in ("none", "normal") and not b["btnTxt"] for b in info["btns"]) and all(not b["txt"] or b["txt"] in ("＋", "🛠", "⋯") for b in info["btns"]), json.dumps([[b["after"], b["btnTxt"], b["txt"]] for b in info["btns"]], ensure_ascii=False))
        want = {"goPlanTop": "ไปหน้าแผน (T)", "openSystemSettings": "ตั้งค่าระบบ", "openSettings": "ตั้งค่าพอร์ต", "openIndustryManager": "อุตสาหกรรม", "toggleMoreMenu": "เพิ่มเติม"}
        check(f"{tag} แถวหัว: title + aria-label ครบ (ไปหน้าแผน (T) · ตั้งค่าระบบ · ตั้งค่าพอร์ต · อุตสาหกรรม · เพิ่มเติม)", all(b["title"] == want[b["on"]] and b["aria"] == want[b["on"]] for b in info["btns"]), json.dumps([[b["on"], b["title"], b["aria"]] for b in info["btns"]], ensure_ascii=False))
        check(f"{tag} แถวหัว: ไม่ล้นแนวนอน (scrollWidth={info['sw']} ≤ {w})", info["sw"] <= w)
        if w <= 700:
            check(f"{tag} แถวหัว: 🛠 ซ่อนบนมือถือ · เหลือ ＋/พอร์ต/Industry/⋯ 4 ปุ่ม", [b["on"] for b in vis] == ["goPlanTop", "openSettings", "openIndustryManager", "toggleMoreMenu"], json.dumps([b["on"] for b in vis]))
            check(f"{tag} แถวหัว: ปุ่ม ＋/พอร์ต/Industry/⋯ อยู่แถวเดียวกับ brand (top ต่างกัน < 8px)", all(abs(b["top"] - info["brandTop"]) < 8 for b in vis), json.dumps([round(b["top"] - info["brandTop"], 1) for b in vis]))
            check(f"{tag} แถวหัว: ปุ่มกว้าง/สูง ≥ 36px", all(b["w"] >= 36 and b["h"] >= 36 for b in vis), json.dumps([[b["w"], b["h"]] for b in vis]))
            gaps = [round(vis[i + 1]["left"] - vis[i]["right"], 1) for i in range(len(vis) - 1)]
            check(f"{tag} แถวหัว: ปุ่มห่างกัน ≥ 4px", all(g >= 4 for g in gaps), json.dumps(gaps))
            check(f"{tag} แถวหัว: brand + สถานะ sync ไม่ทับ/ไม่ล้นเข้าไปในกลุ่มปุ่ม (sync.right ≤ ปุ่มแรก.left) และปุ่มขวาสุดไม่เกินจอ",
                  info["sync"]["r"] <= vis[0]["left"] + 0.5 and vis[-1]["right"] <= w, json.dumps([info["sync"], vis[0]["left"], vis[-1]["right"]]))
            ell = page.evaluate("() => { const e=document.getElementById('brandSyncTime'); const cs=getComputedStyle(e); return [cs.textOverflow, cs.overflow]; }")
            check(f"{tag} แถวหัว: brandSyncTime ตัดด้วย text-overflow: ellipsis", ell == ["ellipsis", "hidden"], json.dumps(ell))
            # ข้อความ sync ยาวมาก ๆ → ยังไม่ล้น
            page.evaluate("() => { document.getElementById('brandSyncTime').textContent = 'push ล่าสุด 12 ชั่วโมง 34 นาทีที่แล้ว (ซิงก์ช้ามาก)'; }")
            sw2 = page.evaluate("() => [document.documentElement.scrollWidth, document.querySelector('.hbtns').getBoundingClientRect().right]")
            check(f"{tag} แถวหัว: ข้อความ sync ยาว → ยังไม่ล้น (scrollWidth ≤ {w} · กลุ่มปุ่มยังอยู่ในจอ)", sw2[0] <= w and sw2[1] <= w, json.dumps(sw2))
            page.evaluate("() => { document.getElementById('brandSyncTime').textContent = '—'; }")
            page.click("#hdrMoreBtn"); page.wait_for_timeout(200)
            mr = page.evaluate("""() => { const m=document.getElementById('moreMenu'), r=m.getBoundingClientRect(), b=document.getElementById('hdrMoreBtn').getBoundingClientRect();
                return {show:m.classList.contains('show'), l:r.left, t:r.top, r:r.right, b:r.bottom, btnB:b.bottom, btnR:b.right, vh:innerHeight}; }""")
            check(f"{tag} เมนู ⋯: เปิดแล้วอยู่ในจอทั้งหมด · เปิดใต้ปุ่ม ⋯", mr["show"] and mr["l"] >= 0 and mr["r"] <= w and mr["t"] >= mr["btnB"] - 1 and mr["b"] <= mr["vh"] + 1 and abs(mr["r"] - mr["btnR"]) < 12, json.dumps(mr))
            shot(page, f"cl2c-moremenu-{w}.png")
            page.evaluate("() => closeMoreMenu()")
        else:
            check(f"{tag} แถวหัว: ＋/🛠/พอร์ต/Industry/⋯ เห็นครบ 5 ปุ่ม", [b["on"] for b in vis] == ["goPlanTop", "openSystemSettings", "openSettings", "openIndustryManager", "toggleMoreMenu"], json.dumps([b["on"] for b in vis]))
            page.click("#hdrMoreBtn"); page.wait_for_timeout(200)
            mr = page.evaluate("""() => { const m=document.getElementById('moreMenu'), r=m.getBoundingClientRect(), b=document.getElementById('hdrMoreBtn').getBoundingClientRect();
                return {show:m.classList.contains('show'), l:r.left, t:r.top, r:r.right, b:r.bottom, btnB:b.bottom, vh:innerHeight}; }""")
            check(f"{tag} เมนู ⋯: เปิดใต้ปุ่ม ⋯ · อยู่ในจอ", mr["show"] and mr["l"] >= 0 and mr["r"] <= w and mr["t"] >= mr["btnB"] - 1 and mr["b"] <= mr["vh"] + 1, json.dumps(mr))
            page.evaluate("() => closeMoreMenu()")
        shot(page, f"cl2c-topbar-{w}.png", ".topbar")
        # กดปุ่มจริง
        page.click('.hbtns>button[onclick^="openSettings"]'); page.wait_for_timeout(250)
        check(f"{tag} กดปุ่มพอร์ต → #setOverlay เปิด", page.evaluate("() => document.getElementById('setOverlay').classList.contains('show')"))
        page.keyboard.press("Escape"); page.wait_for_timeout(120)
        page.click('.hbtns>button[onclick^="openIndustryManager"]'); page.wait_for_timeout(250)
        check(f"{tag} กดปุ่ม Industry → Industry manager (#industryOverlay) เปิด", page.evaluate("() => document.getElementById('industryOverlay').classList.contains('show')"))
        page.keyboard.press("Escape"); page.wait_for_timeout(120)
        if w > 700:
            page.click('.hbtns>button[onclick^="openSystemSettings"]'); page.wait_for_timeout(250)
            check(f"{tag} กดปุ่ม 🛠 → หน้าตั้งค่าระบบเปิด (มี overlay .show)", page.evaluate("() => !!document.querySelector('.overlay.show, .ui-sheet-backdrop')"))
            page.keyboard.press("Escape"); page.wait_for_timeout(120)
            page.click("#hdrMoreBtn"); page.wait_for_timeout(150)
            page.click('#moreMenu button[onclick*="settings"]'); page.wait_for_timeout(250)
            check(f"{tag} เมนู ⋯ → ตั้งค่าพอร์ต ทำงาน", page.evaluate("() => document.getElementById('setOverlay').classList.contains('show')"))
            page.keyboard.press("Escape"); page.wait_for_timeout(120)
        check(f"{tag} แถวหัว: ไม่มี console error · ไม่มี page error", not ce and not pe, json.dumps([ce[:3], pe[:3]], ensure_ascii=False))
    finally:
        browser.close()


def window_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, make_doc())
    try:
        page.wait_for_timeout(600)
        # ไอเดีย Sat v3 ที่ผูกไม้ A (open) ของบัญชี main — ให้การ์ด Sat แสดงแถว open พร้อมปุ่ม 'แก้ SL'
        page.evaluate("""() => { const d = {v3: true, asset: 'XAUUSD', bias: 'Long', created_at: new Date().toISOString(), entry: 2650, sl: 2620, tp: 2700, cancel_level: null,
            conditions: [{id: 'c1', text: 'ราคายืนเหนือ 2640', tp_from: 2700, tp_to: 2750, inval: null, active: true, saved: true}], planned: true, setups: [], status: 'active',
            accts: {main: {trade_id: 'ta', placed: true}}, week: wpWeekKey()}; sat7dWrite('satIdeas', 'idea1', d); }""")
        page.wait_for_timeout(400)
        # ───── ฟอร์มเดิมหาย ─────
        check(f"{tag} ฟอร์มเดิม: ไม่มี #tradeOverlay ใน DOM · ปุ่ม ＋ ในแถวหัวไม่ใช่ openTrade", not present(page, "#tradeOverlay") and not present(page, '.hbtns>button[onclick*="openTrade("]'))
        ce_before = len(ce) + len(pe)
        page.evaluate("() => document.activeElement && document.activeElement.blur && document.activeElement.blur()")
        page.keyboard.press("t"); page.wait_for_timeout(250)
        check(f"{tag} กด T → ไปแท็บแผน (goPlanTop) · ไม่มี overlay เปิด · ไม่มี error (CL2-d+: เดิมไม่เกิดอะไร)", page.evaluate("() => activeTab") == "plan" and not page.evaluate("() => !!document.querySelector('.overlay.show')") and len(ce) + len(pe) == ce_before, json.dumps([ce, pe], ensure_ascii=False)[:300])
        page.evaluate("() => coreSheetClose()")   # 7E-2: scope หุ้น → T เปิด sheet แผน Core ใหม่ (ปิดก่อนไปต่อ)
        page.evaluate("() => switchTab('journal')"); page.wait_for_timeout(250)
        jtxt = page.evaluate("() => document.getElementById('tabJournal').innerText")
        check(f"{tag} ฟอร์มเดิม: Journal ไม่มีปุ่มเดิม 'Closed นอกแผน' (7E-2b-2: ปุ่มใหม่ #jBackfillBtn แทน)", "Closed นอกแผน" not in jtxt and not present(page, '[onclick*="openUnplannedClosed"]') and present(page, '#jBackfillBtn'))
        page.evaluate("() => switchTab('watch')"); page.wait_for_timeout(250)
        wtxt = page.evaluate("() => document.getElementById('tabWatch').innerText")
        check(f"{tag} ฟอร์มเดิม: Watch ไม่มีปุ่ม 'เปิดแผนเทรด →'", "เปิดแผนเทรด" not in wtxt and not present(page, '[onclick*="wlTradeFor"]'))
        shot(page, f"cl2c-watch-{w}.png")
        kb = page.evaluate("() => KB_GLOBAL.map(x=>x[0])")
        check(f"{tag} ปุ่มลัด: มี T (ไปหน้าแผน) ในรายการ · ปุ่มลัดอื่นคงอยู่ (1–6 · C · V · ? · Esc) (7E-1: แก้จาก 'ไม่มี T')", "T" in kb and all(k in kb for k in ("1–6", "C", "V", "?", "Esc")), json.dumps(kb, ensure_ascii=False))

        # ───── 1) การ์ด Sat "แก้ SL" ไม้ A ─────
        page.evaluate("() => { switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(500)
        btn = page.locator('#satV3Panel .ui-row button:has-text("แก้ SL")')
        check(f"{tag} การ์ด Sat: มีปุ่ม 'แก้ SL' ของไม้ A ผูก openTradeEdit('ta','main')", btn.count() >= 1 and "openTradeEdit('ta','main')" in (btn.first.get_attribute("onclick") or ""), str(btn.count()))
        shot(page, f"cl2c-sat-{w}.png")
        btn.first.click(); page.wait_for_timeout(300)
        check(f"{tag} แก้ SL → หน้าต่างแก้ไม้เปิด", te_open(page))
        head = page.evaluate("() => ({t: document.getElementById('teHead').innerText.replace(/\\s+/g,' '), inp: document.querySelectorAll('#teHead input,#teHead select,#teHead button').length, title: document.getElementById('teTitle').textContent, ids: ['tSym','tPort','tStatus','tAcct','bLong','tMult'].filter(i=>document.getElementById(i))})")
        check(f"{tag} หัวหน้าต่าง: Symbol · Sat · Long · ชื่อบัญชี · สถานะ อ่านอย่างเดียว (ไม่มีช่องแก้ Symbol/Port/Bias/บัญชี)",
              all(x in head["t"] for x in ("XAUUSD", "Sat", "Long", "บัญชีหลัก", "Open")) and head["inp"] == 0 and not head["ids"], json.dumps(head, ensure_ascii=False))
        check(f"{tag} ไม้ open: ไม่มีช่องปิดไม้ (exitFields ซ่อน) · ไม่มีช่องวันที่เข้า", page.evaluate("() => document.getElementById('exitFields').offsetParent === null && document.getElementById('teOpenDateBox').offsetParent === null"))
        vals = page.evaluate("() => ['tEntry','tSL','tTP','tQty'].map(i=>document.getElementById(i).value)")
        check(f"{tag} ไม้ A: ช่อง Entry/SL/TP/จำนวน = 2650/2620/2700/0.19", vals == ["2650", "2620", "2700", "0.19"], json.dumps(vals))
        shot(page, f"cl2c-edit-open-{w}.png", "#teOverlay .modal")
        setv(page, "tSL", 2630)
        risk = page.evaluate("() => document.getElementById('teRisk').innerText")
        check(f"{tag} บรรทัดเสี่ยงสด = |2650−2630|×0.19×100 = 380 USD (ก่อนบันทึก)", "380" in risk and "USD" in risk and "เสี่ยงถึง SL" in risk, risk)
        if w <= 700:
            ov = page.evaluate("() => { const r=document.querySelector('#teOverlay .modal').getBoundingClientRect(); return [r.left, r.right, document.documentElement.scrollWidth]; }")
            check(f"{tag} ≤700px: หน้าต่างไม่ล้นจอ (left≥0 · right≤{w} · scrollWidth≤{w})", ov[0] >= 0 and ov[1] <= w + 0.5 and ov[2] <= w, json.dumps(ov))
        page.click("#teSaveBtn"); page.wait_for_timeout(400)
        check(f"{tag} บันทึกแล้วหน้าต่างปิด", not te_open(page))
        persist(page)
        ta = dtrade(page, "ta")
        check(f"{tag} books.main ไม้ A: sl=2630 · entry/qty เดิม (2650 / 0.19) · status open", ta and ta["sl"] == 2630 and ta["entry"] == 2650 and ta["qty"] == 0.19 and ta["status"] == "open", json.dumps(ta))
        check(f"{tag} ไม้ A: setups/condition_id/entry_condition/trend_state/_probeT/tp/mult/cur/plannedEntry/openedAt อยู่ครบ",
              ta and ta.get("setups") == ["s1", "s2"] and ta.get("condition_id") == "c1" and ta.get("entry_condition") == "ราคายืนเหนือ 2640" and ta.get("trend_state") == "up"
              and ta.get("_probeT") == "x" and ta.get("tp") == 2700 and ta.get("mult") == 100 and ta.get("cur") == "USD" and ta.get("plannedEntry") == 2648 and ta.get("openedAt") == "2026-09-20", json.dumps(ta))
        ptxt = page.evaluate("() => document.getElementById('satV3Panel').innerText")
        check(f"{tag} การ์ด Sat อัปเดตหลังบันทึก (แถวแสดง SL 2,630)", "2,630" in ptxt, ptxt[:300])

        # ───── 2) ตรวจก่อนบันทึก ─────
        before = dump_all(page)
        page.evaluate("() => openTradeEdit('ta','main')"); page.wait_for_timeout(200)
        setv(page, "tSL", -1)   # PY1 — ไม้ Sat ที่เปิดอยู่ย้าย SL ไปที่ทุน/เลยทุนได้ (ล็อกกำไร) จึงใช้ SL ติดลบเป็นค่าไม่ถูกต้องแทน 2660
        err = page.evaluate("() => { const e=document.getElementById('teErr'); return {txt:e.innerText.trim(), color:getComputedStyle(e).color, dis:document.getElementById('teSaveBtn').disabled}; }")
        check(f"{tag} SL -1 (ไม่ถูกต้อง) → ข้อความแดง · ปุ่มบันทึกกดไม่ได้", "SL ต้องมากกว่า 0" in err["txt"] and err["dis"] and err["color"].startswith("rgb"), json.dumps(err, ensure_ascii=False))
        shot(page, f"cl2c-edit-error-{w}.png", "#teOverlay .modal")
        page.evaluate("() => saveTradeEdit()"); page.wait_for_timeout(300)
        check(f"{tag} SL ไม่ถูกต้อง: บังคับเรียก saveTradeEdit() ก็ไม่บันทึก · หน้าต่างยังเปิด · ไม่มี alert", te_open(page) and not dialogs, json.dumps(dialogs))
        persist(page)
        check(f"{tag} SL ไม่ถูกต้อง: ไม่มีการเขียน Firestore (เอกสารผู้ใช้เหมือนเดิมทุกไบต์)", dump_all(page) == before)
        # PY1 — ไม้ Sat ที่เปิดอยู่: SL = ทุน (2650) และเลยทุน (2660) ผ่านได้ (ล็อกกำไร) · เดิมคาด 'ไม่เท่ากับ SL' / 'ผิดฝั่ง'
        for sl, msg in (("", "SL ต้องมากกว่า 0"), ("2650", ""), ("2660", "")):
            setv(page, "tSL", sl)
            if msg: check(f"{tag} SL={sl or 'ว่าง'} → '{msg}' · บันทึกไม่ได้", msg in te_err(page) and te_save_disabled(page), te_err(page))
            else: check(f"{tag} SL={sl} (ทุน/เลยทุน · ไม้ Sat เปิดอยู่) → ผ่าน · บันทึกได้ · 'ล็อกกำไร'", te_err(page) == "" and not te_save_disabled(page) and "ล็อกกำไร" in page.evaluate("() => document.getElementById('teRisk').innerText"), te_err(page))
        setv(page, "tSL", 2630); setv(page, "tQty", 0)
        check(f"{tag} จำนวน 0 → บันทึกไม่ได้", "จำนวน" in te_err(page) and te_save_disabled(page), te_err(page))
        setv(page, "tQty", 0.19); setv(page, "tEntry", 0)
        check(f"{tag} Entry 0 → บันทึกไม่ได้", "Entry" in te_err(page) and te_save_disabled(page), te_err(page))
        page.keyboard.press("Escape"); page.wait_for_timeout(200)
        check(f"{tag} Esc ปิดหน้าต่างได้ (ต่อกับ handler Esc เดิม)", not te_open(page))

        # ───── 3) Journal ✎ ไม้ B (closed) ─────
        page.evaluate("() => { jAcct = null; jFilter = 'all'; switchTab('journal'); render(); }"); page.wait_for_timeout(400)
        jb = page.locator("button[onclick*=\"openTradeEdit('tb'\"]:visible")
        check(f"{tag} Journal: ปุ่ม ✎/แก้ไข ของไม้ B ผูก openTradeEdit('tb','main')", jb.count() >= 1 and "openTradeEdit('tb','main')" in (jb.first.get_attribute("onclick") or ""), str(jb.count()))
        jb.first.click(); page.wait_for_timeout(300)
        fields = page.evaluate("() => ({exit: document.getElementById('exitFields').offsetParent !== null, ids: ['tEntry','tSL','tTP','tQty','tExitPrice','tExitDate','tExitReason','tExitNote','tImageUrl','tInvalidation','tDiscScore','tSetupScore'].filter(i=>{const e=document.getElementById(i); return e && e.offsetParent!==null;}), hit: document.getElementById('invalHitField').offsetParent !== null, opts: document.getElementById('tExitReason').options.length})")
        check(f"{tag} Journal ✎ B: เห็นช่อง closed ครบ (Entry SL TP จำนวน ราคาปิด วันปิด เหตุผล โน้ต ลิงก์รูป Invalidation วินัย Setup) · โดนไหมซ่อน (ไม่มี Invalidation)",
              fields["exit"] and len(fields["ids"]) == 12 and not fields["hit"] and fields["opts"] > 1, json.dumps(fields))
        setv(page, "tInvalidation", "ปิดต่ำกว่า EMA50")
        check(f"{tag} พิมพ์ Invalidation → ช่อง 'โดนไหม' โผล่", page.evaluate("() => document.getElementById('invalHitField').offsetParent !== null"))
        setv(page, "tInvalidation", "")
        shot(page, f"cl2c-edit-closed-{w}.png", "#teOverlay .modal")
        first_tag = page.evaluate("() => document.getElementById('tExitReason').options[1].value")
        page.select_option("#tDiscScore", "3"); page.select_option("#tSetupScore", "2"); page.select_option("#tExitReason", first_tag); setv(page, "tExitNote", "ปิดตามแผน")
        live = page.evaluate("() => document.getElementById('exitHint').innerText")
        check(f"{tag} บรรทัดสด closed: P&L ≈ 200 · R ≈ 2 (ราคาปิดเดิม 120)", "P&L ≈ 200" in live and "R ≈ 2" in live, live)
        setv(page, "tExitPrice", 130)
        live = page.evaluate("() => document.getElementById('exitHint').innerText")
        check(f"{tag} แก้ราคาปิด 130 → บรรทัดสด P&L ≈ 300 · R ≈ 3", "P&L ≈ 300" in live and "R ≈ 3" in live, live)
        page.click("#teSaveBtn"); page.wait_for_timeout(400); persist(page)
        tb = dtrade(page, "tb")
        check(f"{tag} books.main ไม้ B: discScore 3 · setupScore 2 · exitReason + exitReasonLabel · exitNote · exitPrice 130",
              tb and tb.get("discScore") == 3 and tb.get("setupScore") == 2 and tb.get("exitReason") == first_tag and tb.get("exitReasonLabel") and tb.get("exitNote") == "ปิดตามแผน" and tb.get("exitPrice") == 130, json.dumps(tb, ensure_ascii=False))
        row = page.evaluate("() => [...document.querySelectorAll('#tabJournal tr, #tabJournal .card')].filter(e=>e.innerText.includes('NVDA')).map(r=>r.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} Journal: คอลัมน์รีวิวแสดง 3 / 2 · P&L 300 · R 3", any(re.search(r"3\s*/\s*2", r) and "300" in r and re.search(r"\b3(\.0+)?R", r) for r in row), json.dumps(row, ensure_ascii=False)[:400])
        shot(page, f"cl2c-journal-{w}.png")
        # ตรวจ closed
        page.evaluate("() => openTradeEdit('tb','main')"); page.wait_for_timeout(200)
        setv(page, "tExitPrice", "")
        check(f"{tag} ราคาปิดว่าง → บันทึกไม่ได้", "ราคาปิด" in te_err(page) and te_save_disabled(page), te_err(page))
        setv(page, "tExitPrice", 130); setv(page, "tExitDate", "2026-08-31")
        check(f"{tag} วันปิดก่อนวันเข้า (2026-08-31 < 2026-09-01) → บันทึกไม่ได้", "วันปิด" in te_err(page) and te_save_disabled(page), te_err(page))
        setv(page, "tExitDate", "")
        check(f"{tag} วันปิดว่าง → บันทึกไม่ได้", te_save_disabled(page), te_err(page))
        setv(page, "tExitDate", "2026-09-10")
        check(f"{tag} แก้กลับให้ถูก → ปุ่มบันทึกกดได้ · ไม่มีข้อความผิดพลาด", not te_save_disabled(page) and te_err(page) == "", te_err(page))
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        # คะแนนว่าง = null (ยังไม่ให้คะแนน) แยกจาก 0
        page.evaluate("() => openTradeEdit('tb','main')"); page.wait_for_timeout(200)
        page.select_option("#tDiscScore", "")
        page.click("#teSaveBtn"); page.wait_for_timeout(300)
        check(f"{tag} คะแนนวินัยว่าง → discScore = null (ไม่ใช่ 0) · setupScore ยัง 2", page.evaluate("() => { const t=getBook('main').trades.find(x=>x.id==='tb'); return t.discScore===null && t.setupScore===2; }"))

        # ───── cancelled D ─────
        page.evaluate("() => openTradeEdit('td','main')"); page.wait_for_timeout(200)
        cf = page.evaluate("() => ({exit: document.getElementById('exitFields').offsetParent !== null, note: document.getElementById('teCancelNoteBox').offsetParent !== null, ids: ['tEntry','tSL','tTP','tQty'].every(i=>document.getElementById(i).offsetParent!==null), n: document.getElementById('tCancelNote').value})")
        check(f"{tag} ไม้ cancelled: Entry/SL/TP/จำนวน + โน้ต (ไม่มีช่องปิดไม้)", cf["ids"] and cf["note"] and not cf["exit"] and cf["n"] == "เปลี่ยนใจ", json.dumps(cf, ensure_ascii=False))
        setv(page, "tQty", 12); page.click("#teSaveBtn"); page.wait_for_timeout(300); persist(page)
        td = dtrade(page, "td")
        check(f"{tag} ไม้ cancelled: แก้ qty แล้วยังคง status/cancelDate/cancelNote/cancelTag/parentId", td and td["qty"] == 12 and td["status"] == "cancelled" and td.get("cancelDate") == "2026-09-12" and td.get("cancelNote") == "เปลี่ยนใจ" and td.get("cancelTag") == "other" and td.get("parentId") == "pp1", json.dumps(td, ensure_ascii=False))

        # ───── 4) ตารางแผน: quickOpen → toOpen ─────
        retired(f"{tag} ตารางแผน: ปุ่ม →Open ของไม้ C ผูก openTradeEdit('tc','main',{{toOpen:true}})", "CL2-d ตาราง Trading Plan → Positions (แสดงเฉพาะไม้ open · ไม่มีปุ่ม →Open) · ไม้ plan เปิดผ่านการ์ด Sat — ยังเรียก openTradeEdit(...,{toOpen:true}) ตรงเพื่อทดสอบหน้าต่างเหมือนเดิม")
        page.evaluate("() => openTradeEdit('tc','main',{toOpen:true})"); page.wait_for_timeout(300)
        m = page.evaluate("() => ({title: document.getElementById('teTitle').textContent, btn: document.getElementById('teSaveBtn').textContent, date: document.getElementById('tOpenDate').value, dateVis: document.getElementById('teOpenDateBox').offsetParent !== null})")
        check(f"{tag} โหมด toOpen: มีช่องวันที่เข้า (ค่าเริ่มต้นวันนี้) + ปุ่มหลัก 'บันทึก · เข้าแล้ว'", m["dateVis"] and m["btn"] == "บันทึก · เข้าแล้ว" and re.match(r"\d{4}-\d{2}-\d{2}$", m["date"] or ""), json.dumps(m, ensure_ascii=False))
        shot(page, f"cl2c-edit-toopen-{w}.png", "#teOverlay .modal")
        setv(page, "tOpenDate", "2026-09-28"); setv(page, "tEntry", 2601)
        page.click("#teSaveBtn"); page.wait_for_timeout(400); persist(page)
        tc = dtrade(page, "tc")
        check(f"{tag} บันทึก toOpen → status open · openedAt = 2026-09-28 · date = 2026-09-28 · entry 2601 · plannedEntry = 2600", tc and tc["status"] == "open" and tc.get("openedAt") == "2026-09-28" and tc["date"] == "2026-09-28" and tc["entry"] == 2601 and tc.get("plannedEntry") == 2600, json.dumps(tc))
        check(f"{tag} openTradeEdit ไม้ที่ไม่ใช่ plan + toOpen → ไม่เข้าโหมด toOpen (ไม้ open แก้ปกติ)", page.evaluate("() => { openTradeEdit('tc','main',{toOpen:true}); const r = document.getElementById('teOpenDateBox').offsetParent === null && document.getElementById('teTitle').textContent==='แก้ไม้'; closeTradeEdit(); return r; }"))

        # ───── 5) fam ─────
        main_before = json.dumps(dump_book(page, "main"), sort_keys=True)
        page.evaluate("() => { jFilter = 'all'; switchTab('journal'); setJAcct('fam'); }"); page.wait_for_timeout(400)
        jf = page.locator("button[onclick*=\"openTradeEdit('tf'\"]:visible")
        check(f"{tag} Journal ดูบัญชี fam: ปุ่ม ✎ ไม้ F ผูก openTradeEdit('tf','fam')", jf.count() >= 1 and "openTradeEdit('tf','fam')" in (jf.first.get_attribute("onclick") or ""), str(jf.count()))
        jf.first.click(); page.wait_for_timeout(300)
        fh = page.evaluate("() => document.getElementById('teHead').innerText")
        check(f"{tag} หัวหน้าต่าง fam แสดงชื่อบัญชี Family", "Family" in fh and "FAMX" in fh, fh)
        setv(page, "tExitPrice", 65); page.click("#teSaveBtn"); page.wait_for_timeout(400); persist(page)
        tf = dtrade(page, "tf", "fam")
        check(f"{tag} บันทึกไม้ F → เขียน books.fam เท่านั้น (exitPrice 65 · fills คงอยู่) · books.main ไม่เปลี่ยน",
              tf and tf["exitPrice"] == 65 and tf.get("fills") == [{"q": 100}] and json.dumps(dump_book(page, "main"), sort_keys=True) == main_before, json.dumps(tf))
        check(f"{tag} openTradeEdit ไม้ไม่เจอ → ไม่เปิด (console.warn) · ไม่ error", page.evaluate("() => { openTradeEdit('nope','main'); openTradeEdit('tf','main'); return !document.getElementById('teOverlay').classList.contains('show'); }"))

        # ───── ทุกแท็บ + ตั้งค่า ─────
        for t in ("flow", "mix", "watch", "plan", "journal"):
            page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(250)
            page.evaluate("() => { if(typeof render==='function') render(); }")
            if w <= 700:
                sw = page.evaluate("() => document.documentElement.scrollWidth")
                check(f"{tag} แท็บ {t}: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w)
        for fn in ("openSystemSettings()", "openSettings()"):
            page.evaluate("() => " + fn); page.wait_for_timeout(200); page.keyboard.press("Escape"); page.wait_for_timeout(100)
        check(f"{tag} เปิดทุกแท็บ + ตั้งค่า + หน้าต่างแก้ไม้: ไม่มี console error", not ce, json.dumps(ce[:5], ensure_ascii=False))
        check(f"{tag} เปิดทุกแท็บ + ตั้งค่า + หน้าต่างแก้ไม้: ไม่มี uncaught page error", not pe, json.dumps(pe[:5], ensure_ascii=False))
    finally:
        browser.close()


def grep_tests():
    src = open(INDEX, encoding="utf-8").read()
    lines = src.split("\n")
    must_not = ["tradeOverlay", "saveTradeCompute", "openTradeBody", "editTradeBody", "function editTrade", "function openTrade(", "openUnplannedClosed", "wlTradeFor", "formRun",
                "tradeFillAcctSelect", "acctSyncPortSelect", "tradeSatAOptionValue", "Add Trade"]
    for n in must_not:
        left = [i + 1 for i, t in enumerate(lines) if n in t]
        check(f"grep index.html: ไม่เจอ {n}", not left, json.dumps(left[:5]))
    must = ["makeTradeObject", "openTradeEdit", "closePosOverlay", "cancelOverlay", "populateReasonSelect", "populateBothScoreSelects", "Calc.newCount", "cl2aStripLegacy"]
    for n in must:
        check(f"grep index.html: ยังเจอ {n}", any(n in t for t in lines))
    for n in ["SZ", "szHeat", "renderHeatPanel", "planBuildSection", "ggScoreOfSym"]:
        retired(f"grep index.html: ยังเจอ {n}", "CL2-d ลบ SZ/sz*/แผง Heat/ตาราง Trading Plan/gg* — phase22 ตรวจว่าไม่เจอแทน")
    check("grep index.html: ไม่มีกฎ .hbtns ... ::after { content: 'ข้อความ' } เหลืออยู่ (ตัดทุกขนาดจอ)", not re.search(r"\.hbtns[^{]*::after\s*\{[^}]*content\s*:\s*'", src))


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            window_checks(pw, w, h, label)
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900"), (375, 812, "375x812")):
            header_checks(pw, w, h, label)
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
