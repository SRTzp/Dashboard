#!/usr/bin/env python3
"""CL2-d — ตาราง Positions (แทน Trading Plan & Positions) · ลบ sizing เดิม (SZ/sz*/Heat 1R/บล็อก CL3/ค่าตั้ง 1R) · เก็บกวาด
mock Firestore (ไม่ต่อเน็ต) · 1440px + 430px · seed.json + ไม้ที่ใส่เองในเทส
รัน: python3 run_tests_phase22.py [/path/to/index.html] · ภาพเก็บที่ tests/screenshots/cl2d-*.png"""
import copy, datetime, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))
results = []


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


def bkk_today_minus(n):
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7)))
    return (now - datetime.timedelta(days=n)).strftime("%Y-%m-%d")


def T(id, port, status, **kw):
    d = {"id": id, "date": "2026-09-01", "sym": id.upper(), "port": port, "bias": "Long", "entry": 100, "sl": 90, "tp": None, "qty": 10,
         "mult": 1, "cur": "THB", "status": status, "unplanned": False}
    d.update(kw); return d


SIZING = {"r": {"core": 1.7, "satA": 0.9}, "cap": {"core": 11, "satA": 22}, "ffThrottle": False}
POSSIZE = {"core": 7, "satB": 3}
LIMITS = {"trade": 1.5, "port": {"core": 3, "satB": 3}, "total": 6}


def make_doc(main_trades=None, with_legacy=True):
    doc = copy.deepcopy(SEED)
    if with_legacy:
        doc["books"]["main"]["settings"].update({"sizing": copy.deepcopy(SIZING), "posSize": copy.deepcopy(POSSIZE), "limits": copy.deepcopy(LIMITS), "sz1Rv2": True, "rsBench": "NASDAQ:IXIC"})
    if main_trades is None:
        main_trades = [
            T("ta", "satB", "open", sym="XAUUSD", date=bkk_today_minus(5), openedAt=bkk_today_minus(5), entry=2650, sl=2620, tp=2700, qty=0.19, mult=100, cur="USD"),
            T("tb", "core", "open", sym="NVDA", date="2026-09-02", entry=100, sl=90, qty=10),
            T("tc", "core", "open", sym="AAPL", date="2026-09-03", entry=200, sl=205, qty=5, unplanned=True),
            T("td", "satB", "plan", sym="BRENT", date="2026-09-25", entry=2600, sl=2580, qty=0.1, mult=100, cur="USD"),
            T("te", "core", "closed", sym="CLOSEDX", date="2026-09-01", entry=100, sl=90, qty=10, exitPrice=120, exitDate="2026-09-10"),
        ]
    doc["books"]["main"]["trades"] = main_trades
    doc["books"]["fam"]["trades"] = [T("tf", "core", "open", sym="FAMX", bias="Short", entry=50, sl=55, qty=100)]
    return doc


def launch(pw, w, h, doc):
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
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(500)
    return browser, context, page, ce, pe, dialogs


def dump_book(page, acct="main"):
    return page.evaluate("(a)=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return d && d.books && d.books[a]; }", acct)


def present(page, sel): return page.evaluate("(s)=>!!document.querySelector(s)", sel)


def go_plan(page):
    page.evaluate("() => { switchTab('plan'); setPlanAcct('all'); }"); page.wait_for_timeout(350)


def sec(acct): return f'#planSections .acctSec[data-acct="{acct}"]'


def vis_rows(page, acct, w):
    """แถว/การ์ดที่มองเห็นได้ตาม viewport → [{id,text,risk}]"""
    sel = sec(acct) + (" .tcard" if w <= 700 else " tbody tr")
    return page.evaluate("""(s)=>[...document.querySelectorAll(s)].filter(e=>e.getBoundingClientRect().width>0).map(e=>({id:e.dataset.pos, text:e.innerText.replace(/\\s+/g,' ').trim(),
        risk:(e.querySelector('[data-pos-risk]')||{}).innerText||''}))""", sel)


def positions_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, make_doc())
    try:
        go_plan(page)
        fx = page.evaluate("() => state.settings.fx")
        title = page.evaluate("() => document.getElementById('planSections').parentElement.querySelector('.panel-head h2').innerText.trim()")
        check(f"{tag} หัวแผง = Positions · ไม่มีชิป filter (#filters) · ไม่มีแผง #szHeatPanel",
              title == "Positions" and not present(page, "#filters") and not present(page, "#szHeatPanel"), title)
        chips = page.evaluate("() => [...document.querySelectorAll('#acctFilters .chip')].map(c=>c.innerText.trim())")
        check(f"{tag} ชิปเลือกบัญชียังอยู่ (ทุกบัญชี · บัญชีหลัก · Family)", len(chips) == 3, json.dumps(chips, ensure_ascii=False))
        check(f"{tag} หัวบัญชีแสดงชื่อ + จุดสี · ไม่มี ป้าย 'ความเสี่ยงค้าง' ในหัว",
              page.evaluate("() => [...document.querySelectorAll('#planSections .acctSecHead')].every(h=>h.querySelector('.acctDotC') && !h.querySelector('.acctSecRisk'))"))
        # ───── main ─────
        rows = vis_rows(page, "main", w)
        ids = [r["id"] for r in rows]
        check(f"{tag} Positions main: แสดง B C A เท่านั้น (Core ก่อน Sat · วันเข้าเก่าก่อน) · ไม่มี D plan · ไม่มี E closed", ids == ["tb", "tc", "ta"], json.dumps(ids))
        txt = " ".join(r["text"] for r in rows)
        check(f"{tag} Positions main: ไม่มีสัญลักษณ์ BRENT (plan) / CLOSEDX (closed)", "BRENT" not in txt and "CLOSEDX" not in txt)
        byid = {r["id"]: r for r in rows}
        a_amt = f"{570:,}"
        check(f"{tag} เสี่ยงค้าง A = $570 (≈฿{round(570*fx):,} ตาม fx {fx})", "$" + a_amt in byid["ta"]["risk"] and f"≈฿{round(570*fx):,}" in byid["ta"]["risk"], byid["ta"]["risk"])
        check(f"{tag} เสี่ยงค้าง B = ฿100", byid["tb"]["risk"].strip().startswith("฿100") and "ล็อกกำไร" not in byid["tb"]["risk"], byid["tb"]["risk"])
        check(f"{tag} เสี่ยงค้าง C (SL เลยทุน) = ฿0 + ป้าย ล็อกกำไร", byid["tc"]["risk"].strip().startswith("฿0") and "ล็อกกำไร" in byid["tc"]["risk"], byid["tc"]["risk"])
        check(f"{tag} ถือมา A = 5 วัน", "ถือมา 5 วัน" in byid["ta"]["text"] or " 5 วัน" in byid["ta"]["text"], byid["ta"]["text"])
        check(f"{tag} ป้าย 'นอกแผน' เฉพาะ C (unplanned)", "นอกแผน" in byid["tc"]["text"] and "นอกแผน" not in byid["tb"]["text"] and "นอกแผน" not in byid["ta"]["text"])
        check(f"{tag} คอลัมน์: Port · Asset · Long/Short · ทุน · จำนวน · SL · TP (ว่าง = —) · ถือมา",
              all(k in byid["tb"]["text"] for k in ("Core", "NVDA", "Long", "100", "10", "90", "—", "วัน")) and "Sat" in byid["ta"]["text"] and "XAUUSD" in byid["ta"]["text"], byid["tb"]["text"])
        pure = page.evaluate("""() => { const T = state.trades.reduce((m,t)=>(m[t.id]=t,m),{}); const r = id => posOpenRisk(T[id]);
            const s = posOpenRisk({bias:'Short', entry:50, sl:45, qty:1, mult:1, port:'core', cur:'THB'});
            return {a:r('ta'), b:r('tb'), c:r('tc'), s, fx:state.settings.fx}; }""")
        check(f"{tag} posOpenRisk: A 570 USD thb=570×fx · B 100 THB · C locked amt 0 · Short sl≤entry locked",
              abs(pure["a"]["amt"] - 570) < 1e-6 and pure["a"]["cur"] == "USD" and abs(pure["a"]["thb"] - 570 * pure["fx"]) < 1e-6 and pure["b"]["amt"] == 100 and pure["b"]["cur"] == "THB"
              and pure["c"]["locked"] and pure["c"]["amt"] == 0 and pure["s"]["locked"] and pure["s"]["amt"] == 0, json.dumps(pure))
        sumtxt = page.evaluate("(s)=>{ const e=document.querySelector(s+' [data-pos-sum]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : ''; }", sec("main"))
        check(f"{tag} แถวรวม main: เสี่ยงค้างรวม · Core ฿100 · Sat $570 (≈฿{round(570*fx):,})", "เสี่ยงค้างรวม" in sumtxt and "Core ฿100" in sumtxt and "Sat $570" in sumtxt and f"≈฿{round(570*fx):,}" in sumtxt, sumtxt)
        # ───── fam ─────
        frows = vis_rows(page, "fam", w)
        check(f"{tag} Positions fam: F เสี่ยงค้าง = ฿500 (|50−55|×100) · ป้าย Short", len(frows) == 1 and frows[0]["risk"].strip().startswith("฿500") and "Short" in frows[0]["text"], json.dumps(frows, ensure_ascii=False))
        fsum = page.evaluate("(s)=>{ const e=document.querySelector(s+' [data-pos-sum]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : ''; }", sec("fam"))
        check(f"{tag} แถวรวม fam: Core ฿500 · ไม่มี Sat", "Core ฿500" in fsum and "Sat" not in fsum, fsum)
        fb = page.evaluate("""(s)=>[...document.querySelectorAll(s+' '+(innerWidth<=700?'.tcard':'tbody tr')+' button')].filter(b=>b.getBoundingClientRect().width>0).map(b=>[b.innerText.trim(), b.getAttribute('onclick')])""", sec("fam"))
        check(f"{tag} fam: ปุ่ม ปิด/แก้/ยกเลิก/ลบ ส่งบัญชี 'fam' ทั้งหมด", [b[0] for b in fb] == ["ปิด", "แก้", "ยกเลิก", "ลบ"] and all("'tf','fam'" in b[1] for b in fb), json.dumps(fb, ensure_ascii=False))
        # ───── ปุ่ม main ─────
        btn = lambda id, label: page.locator(sec("main") + (" .tcard" if w <= 700 else " tbody tr") + f'[data-pos="{id}"] button:has-text("{label}")').first
        check(f"{tag} ปุ่ม: onclick ผูก openClosePos/openTradeEdit/openCancelModal/delTrade ของไม้และบัญชี main",
              all((btn("tb", l).get_attribute("onclick") or "").startswith(f + "('tb','main')") for l, f in (("ปิด", "openClosePos"), ("แก้", "openTradeEdit"), ("ยกเลิก", "openCancelModal"), ("ลบ", "delTrade"))))
        btn("ta", "ปิด").click(); page.wait_for_timeout(250)
        check(f"{tag} กด ปิด A → #closePosOverlay เปิด", page.evaluate("() => document.getElementById('closePosOverlay').classList.contains('show')"))
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        btn("tb", "แก้").click(); page.wait_for_timeout(250)
        check(f"{tag} กด แก้ B → #teOverlay เปิด", page.evaluate("() => document.getElementById('teOverlay').classList.contains('show')"))
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        btn("tb", "ยกเลิก").click(); page.wait_for_timeout(250)
        check(f"{tag} กด ยกเลิก B → #cancelOverlay เปิด", page.evaluate("() => document.getElementById('cancelOverlay').classList.contains('show')"))
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        # ───── layout ─────
        lay = page.evaluate("""(s)=>{ const q=x=>document.querySelector(s+' '+x); const vis=e=>!!e && e.getBoundingClientRect().width>0;
            return {tbl:vis(q('.tablewrap')), cards:vis(q('.cards .tcard')), sw:document.documentElement.scrollWidth}; }""", sec("main"))
        if w <= 700:
            check(f"{tag} ≤700px: การ์ดแสดง · .tablewrap ซ่อน · ไม่ล้นแนวนอน (scrollWidth={lay['sw']} ≤ {w})", lay["cards"] and not lay["tbl"] and lay["sw"] <= w, json.dumps(lay))
            check(f"{tag} ≤700px: การ์ดครบ 3 ใบ · มีคำว่า เสี่ยงค้าง/ถือมา/ทุน/จำนวน", len(rows) == 3 and all(k in " ".join(r["text"] for r in rows) for k in ("เสี่ยงค้าง", "ถือมา", "ทุน", "จำนวน")))
        else:
            check(f"{tag} ≥701px: ตารางแสดง · การ์ดซ่อน", lay["tbl"] and not lay["cards"], json.dumps(lay))
        shot(page, f"cl2d-positions-main-{w}.png", "#tabPlan .panel:has(#planSections)")
        page.evaluate("() => setPlanAcct('fam')"); page.wait_for_timeout(300)
        shot(page, f"cl2d-positions-fam-{w}.png", "#tabPlan .panel:has(#planSections)")
        page.evaluate("() => setPlanAcct('all')"); page.wait_for_timeout(200)
        # ───── บล็อกสรุป Core ─────
        blk = page.evaluate("""() => ({heat: !!document.querySelector('[data-sum="heat"]'), open: !!document.querySelector('#portsSum [data-sum="open"]'), plan: !!document.querySelector('#portsSum [data-sum="plan"]'),
            txt: (document.getElementById('portsSum')||{innerText:''}).innerText, foot: document.getElementById('foot').innerText})""")
        check(f"{tag} บล็อกสรุป Core: ไม่มี data-sum=heat · ช่องความเสี่ยงค้าง (data-sum=open) ยังอยู่ · ช่อง 'แผนที่รอ' ซ่อนเมื่อไม่มีไม้ plan ของ Core (7E-1) · ไม่มีคำว่า Heat 1R", not blk["heat"] and blk["open"] and not blk["plan"] and "Heat 1R" not in blk["txt"], json.dumps(blk, ensure_ascii=False))
        check(f"{tag} footer: 'heat: Core x% / 20% ของถัง · Sat y% / 6% ของถัง · รวม z% ของบัญชี' · ไม่มี 1R (7E-1)", re.search(r"heat: Core [\d.]+% / [\d.]+% ของถัง · Sat [\d.]+% / [\d.]+% ของถัง · รวม [\d.]+% ของบัญชี", blk["foot"]) and "1R" not in blk["foot"], blk["foot"])
        shot(page, f"cl2d-portsum-{w}.png", "#portsSum")
        check(f"{tag} Positions/บล็อกสรุป: ไม่มี console error · page error", not ce and not pe, json.dumps([ce[:3], pe[:3]], ensure_ascii=False))
    finally:
        browser.close()


def empty_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc = make_doc(main_trades=[T("td", "satB", "plan", sym="BRENT", date="2026-09-25", entry=2600, sl=2580, qty=0.1, mult=100, cur="USD"),
                                T("te", "core", "cancelled", sym="CX", date="2026-09-01")])
    doc["books"]["fam"]["trades"] = []
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc)
    try:
        go_plan(page)
        msg = "ยังไม่มีไม้ที่ถืออยู่ — ไม้ Sat เปิดจากการ์ดในหน้า Sat · ไม้ Core เปิดจากการ์ด Core (กด ＋ หรือ T ในแท็บแผน)"
        got = page.evaluate("() => [...document.querySelectorAll('#planSections .acctSec [data-pos-empty]')].map(e=>e.innerText.trim())")
        check(f"{tag} ว่าง: บัญชีที่ไม่มีไม้ open → ข้อความ §1.4 ทั้ง 2 บัญชี · ไม่มีตาราง", got == [msg, msg] and not present(page, "#planSections table"), json.dumps(got, ensure_ascii=False))
        shot(page, f"cl2d-positions-empty-{w}.png", "#tabPlan .panel:has(#planSections)")
        # Journal ว่าง
        page.evaluate("() => switchTab('journal')"); page.wait_for_timeout(300)
        je = page.evaluate("() => document.getElementById('jEmpty').innerText.trim()")
        want = "ยังไม่มีไม้ที่ปิด — ปิดไม้จากการ์ด Sat หรือตาราง Positions แล้วรายการจะมาโผล่ที่นี่"
        check(f"{tag} Journal ว่าง: ข้อความใหม่ (ตาราง)", je == want, je)
        if w <= 700:
            ce2 = page.evaluate("() => (document.getElementById('jCards')||{innerText:''}).innerText")
            check(f"{tag} Journal ว่าง: การ์ดมือถือใช้ข้อความใหม่", want in ce2, ce2)
        check(f"{tag} ว่าง/Journal: ไม่มี console error", not ce and not pe, json.dumps([ce[:3], pe[:3]], ensure_ascii=False))
    finally:
        browser.close()


def settings_watch_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, make_doc())
    try:
        go_plan(page)
        page.evaluate("() => openSettings()"); page.wait_for_timeout(300)
        gone = ["sRCore", "sRSatA", "sCapCore", "sCapSatA", "sPosSatB", "sRsBench", "sFfThrottle", "sFfNow"]
        left = [g for g in gone if present(page, "#" + g)]
        check(f"{tag} ตั้งค่า: ไม่มีช่อง sRCore/sRSatA/sCapCore/sCapSatA/sPosSatB/sRsBench/sFfThrottle/sFfNow", not left, json.dumps(left))
        heads = page.evaluate("() => [...document.querySelectorAll('#setOverlay .setsec>summary')].map(s=>s.innerText.trim())")
        check(f"{tag} ตั้งค่า: ไม่มีหมวด Position Sizing / เพดาน Fund-flow · หมวดอื่นยังอยู่", not any("position sizing" in s.lower() or "เพดาน fund-flow" in s.lower() for s in heads) and any("core rules" in s.lower() for s in heads) and any(s.lower().startswith("app") for s in heads), json.dumps(heads, ensure_ascii=False))
        shot(page, f"cl2d-settings-{w}.png", "#setOverlay .modal")
        before = dump_book(page, "main")["settings"]
        page.fill("#sCore", "3210000"); page.evaluate("() => saveSettings()"); page.wait_for_timeout(2000)
        after = dump_book(page, "main")["settings"]
        check(f"{tag} บันทึกตั้งค่า: ทุน Core ใหม่ถูกบันทึก (3,210,000)", after["capital"]["core"] == 3210000, json.dumps(after["capital"]))
        check(f"{tag} บันทึกตั้งค่า: settings.sizing ยังเป็นค่าเดิมเป๊ะ", after.get("sizing") == SIZING, json.dumps(after.get("sizing")))
        check(f"{tag} บันทึกตั้งค่า: settings.posSize ยังเป็นค่าเดิมเป๊ะ", after.get("posSize") == POSSIZE, json.dumps(after.get("posSize")))
        check(f"{tag} บันทึกตั้งค่า: settings.limits.trade ยังเป็นค่าเดิม (1.5) · limits.total ยังอยู่ · limits.port = {{core:20,satB:6}} (7E-1: migration heatV2 แทนค่าเดิม 3/3)", after["limits"].get("trade") == 1.5 and after["limits"].get("total") == 6 and after["limits"].get("port") == {"core": 20, "satB": 6}, json.dumps(after.get("limits")))
        check(f"{tag} บันทึกตั้งค่า: key อื่นที่ไม่ได้แก้ยังอยู่ (brokers · rsBench · sz1Rv2 · capital.option)", after.get("brokers") == before.get("brokers") and after.get("rsBench") == "NASDAQ:IXIC" and after.get("sz1Rv2") is True and after["capital"].get("option") == 0, json.dumps(sorted(after.keys())))
        # ผู้ใช้ใหม่ (ไม่มี sizing ในเอกสาร) → บันทึกแล้วไม่เขียน key ที่ไม่มี
        # ───── Watch ─────
        page.evaluate("() => switchTab('watch')"); page.wait_for_timeout(300)
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','ZZTEST'], {ticker:'ZZTEST', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(500)   # TD4b: Candidate ก็เพิ่มตรงไม่ได้แล้ว → seed เป็นตัวที่อยู่ใน Watchlist ก่อน
        page.evaluate("() => wlOpenAdd('ZZTEST')"); page.wait_for_timeout(200)
        check(f"{tag} Watch: เปิดฟอร์มเพิ่มหุ้น (#wlAddOverlay)", page.evaluate("() => document.getElementById('wlAddOverlay').classList.contains('show')"))
        page.fill("#wlAddSym", "ZZTEST"); page.evaluate("() => wlAddOnSym()"); page.wait_for_timeout(100)
        page.evaluate("() => wlAddSave()"); page.wait_for_timeout(500)
        rows = page.evaluate("() => wlRowsAll().wl.map(r=>r.sym)")
        check(f"{tag} Watch: เพิ่มหุ้น ZZTEST ได้ (อยู่ในรายการ)", "ZZTEST" in rows, json.dumps(rows))
        wt = page.evaluate("() => document.getElementById('tabWatch').innerText")
        check(f"{tag} Watch: ไม่มีป้าย R/GG (ไม่มี 'GG' · ไม่มี 'R 1.25/1.00/0.75/0.50')", not re.search(r"\bGG\b|\bR\s?(1\.25|1\.00|0\.75|0\.50)\b", wt), wt[:200])
        check(f"{tag} Watch: ไม่มี FC chip (Fundamental Checklist ในเครื่อง)", "FC " not in wt.replace("FQC", ""), "")
        shot(page, f"cl2d-watch-{w}.png")
        # ───── Flow ─────
        page.evaluate("() => switchTab('flow')"); page.wait_for_timeout(400)
        fl = page.evaluate("""() => { let cap=null, core=null; try{ cap = ffDeployCap('core'); core = ffCoreNow().cap; }catch(e){ cap = 'ERR '+e.message; }
            return {cap, core, regime: !!document.querySelector('#tabFlow [data-ff="regime"]'), capCell: !!document.querySelector('#tabFlow [data-ff="cap"]'), txt: document.getElementById('tabFlow').innerText.slice(0,4000)}; }""")
        check(f"{tag} Flow: การ์ด Regime + เพดาน Core ยังแสดง · ffDeployCap('core') ทำงาน = ffCoreNow().cap", fl["regime"] and fl["capCell"] and isinstance(fl["cap"], (int, float)) and fl["cap"] == fl["core"], json.dumps({k: fl[k] for k in ("cap", "core", "regime", "capCell")}))
        shot(page, f"cl2d-flow-{w}.png")
        # ───── ทุกแท็บ + Sat ─────
        for t in ("flow", "mix", "watch", "plan", "journal"):
            page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(250)
            page.evaluate("() => { if(typeof render==='function') render(); }")
            if w <= 700:
                sw = page.evaluate("() => document.documentElement.scrollWidth")
                check(f"{tag} แท็บ {t}: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w)
        page.evaluate("() => { switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(500)
        sat = page.evaluate("() => { const p=document.getElementById('satV3Panel'); return p && p.getBoundingClientRect().height>0 ? p.innerText.length : 0; }")
        check(f"{tag} การ์ด Sat (satV3Panel) แสดงได้ · scope Future ยังเห็น Positions", sat > 0 and present(page, "#planSections .acctSec"), str(sat))
        shot(page, f"cl2d-sat-{w}.png")
        page.evaluate("() => setPlanScope('stock')")
        for fn in ("openSystemSettings()", "openSettings()"):
            page.evaluate("() => " + fn); page.wait_for_timeout(200); page.keyboard.press("Escape"); page.wait_for_timeout(100)
        check(f"{tag} เปิดทุกแท็บ + ตั้งค่า + การ์ด Sat: ไม่มี console error", not ce, json.dumps(ce[:5], ensure_ascii=False))
        check(f"{tag} เปิดทุกแท็บ + ตั้งค่า + การ์ด Sat: ไม่มี uncaught page error", not pe, json.dumps(pe[:5], ensure_ascii=False))
    finally:
        browser.close()


def header_plus_checks(pw, w, h, label):
    """ปุ่ม ＋ แถวหัว (goPlanTop) + ปุ่มลัด T"""
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, make_doc())
    try:
        info = page.evaluate("""() => { const b=document.getElementById('hdrPlanBtn'); const btns=[...document.querySelectorAll('.hbtns>button')].filter(x=>x.getBoundingClientRect().width>0);
            const r=b.getBoundingClientRect(), br=document.querySelector('.topbar .brand').getBoundingClientRect();
            return {first: btns[0]===b, txt:b.innerText.trim(), cls:b.className, title:b.title, aria:b.getAttribute('aria-label'), w:r.width, h:r.height, top:r.top, brandTop:br.top,
                    sizeOthers:[...btns].filter(x=>x!==b).map(x=>[x.getBoundingClientRect().width, x.getBoundingClientRect().height]), sw:document.documentElement.scrollWidth}; }""")
        check(f"{tag} ปุ่ม ＋: id=hdrPlanBtn · ไอคอน ＋ · title/aria 'ไปหน้าแผน (T)' · ซ้ายสุดของกลุ่ม", info["first"] and info["txt"] == "＋" and info["title"] == "ไปหน้าแผน (T)" and info["aria"] == "ไปหน้าแผน (T)", json.dumps(info, ensure_ascii=False))
        check(f"{tag} ปุ่ม ＋: ขนาด ≥ 36px · ไม่มีคลาส primary" + (" · สูงเท่าปุ่มข้างเคียง" if w <= 700 else ""),
              info["w"] >= 36 and info["h"] >= 36 and "primary" not in info["cls"].split() and (w > 700 or all(abs(o[1] - info["h"]) < 1.5 and abs(o[0] - info["w"]) < 1.5 for o in info["sizeOthers"])), json.dumps(info))
        if w <= 700:
            check(f"{tag} ปุ่ม ＋: แถวเดียวกับ brand (top ต่างกัน {abs(info['top'] - info['brandTop']):.1f} < 8px)", abs(info["top"] - info["brandTop"]) < 8)
            check(f"{tag} ไม่ล้นแนวนอน (scrollWidth={info['sw']} ≤ {w}) · 4 ไอคอน + brand", info["sw"] <= w, str(info["sw"]))
        if w <= 430:
            page.click("#hdrMoreBtn"); page.wait_for_timeout(200)
            mr = page.evaluate("""() => { const m=document.getElementById('moreMenu'), r=m.getBoundingClientRect(), b=document.getElementById('hdrMoreBtn').getBoundingClientRect();
                return {show:m.classList.contains('show'), l:r.left, r:r.right, t:r.top, b:r.bottom, btnB:b.bottom, vh:innerHeight}; }""")
            check(f"{tag} เมนู ⋯: เปิดใต้ปุ่ม ⋯ · อยู่ในจอ", mr["show"] and mr["l"] >= 0 and mr["r"] <= w and mr["t"] >= mr["btnB"] - 1 and mr["b"] <= mr["vh"] + 1, json.dumps(mr))
            shot(page, f"cl2d-header-menu-{w}.png")
            page.click("#hdrPlanBtn"); page.wait_for_timeout(250)
            page.evaluate("() => coreSheetClose()")   # 7E-2: scope หุ้น → ＋ เปิด sheet แผน Core ใหม่
            check(f"{tag} เมนู ⋯ เปิดอยู่ → กด ＋ → เมนูปิด", not page.evaluate("() => document.getElementById('moreMenu').classList.contains('show')"))
        shot(page, f"cl2d-header-{w}.png", ".topbar")
        # Journal + เลื่อนลง → กด ＋
        for scope in ("future", "stock"):
            page.evaluate("(s)=>{ setPlanScope(s); switchTab('journal'); window.scrollTo(0, 800); }", scope); page.wait_for_timeout(300)
            page.evaluate("() => window.scrollTo(0, 800)"); page.wait_for_timeout(150)
            before = page.evaluate("() => window.scrollY")
            page.click("#hdrPlanBtn"); page.wait_for_timeout(700)
            page.evaluate("() => coreSheetClose()")   # 7E-2: scope หุ้น → ＋ เปิด sheet แผน Core ใหม่
            r = page.evaluate("""() => { const vis=id=>{ const r=document.getElementById(id).getBoundingClientRect(); return r.width>0 && r.top>=0 && r.bottom<=innerHeight; };
                return {tab:activeTab, y:window.scrollY, scope:planScope, a:vis('scopeStock'), b:vis('scopeFuture')}; }""")
            check(f"{tag} Journal (scrollY={before}) → กด ＋ (scope={scope}): แท็บแผน · scrollY ≤ 5 · เห็น #scopeStock/#scopeFuture · planScope คง '{scope}'",
                  r["tab"] == "plan" and r["y"] <= 5 and r["a"] and r["b"] and r["scope"] == scope, json.dumps(r))
        if w == 430: shot(page, "cl2d-header-after-plus-430.png")
        # ปุ่มลัด T
        page.evaluate("() => { switchTab('journal'); window.scrollTo(0, 500); document.activeElement && document.activeElement.blur(); }"); page.wait_for_timeout(200)
        page.keyboard.press("t"); page.wait_for_timeout(600)
        page.evaluate("() => coreSheetClose()")   # 7E-2: scope หุ้น → T เปิด sheet แผน Core ใหม่
        r = page.evaluate("() => ({tab:activeTab, y:window.scrollY})")
        check(f"{tag} กด T (ไม่ได้โฟกัสช่องกรอก) → ผลเดียวกับ ＋ (แท็บแผน · scrollY ≤ 5)", r["tab"] == "plan" and r["y"] <= 5, json.dumps(r))
        page.evaluate("() => { switchTab('journal'); }"); page.wait_for_timeout(200)
        page.evaluate("() => { const i=document.createElement('input'); i.id='zzInp'; document.body.appendChild(i); i.focus(); }")
        page.keyboard.press("t"); page.wait_for_timeout(300)
        r = page.evaluate("() => ({tab:activeTab, v:document.getElementById('zzInp').value})")
        check(f"{tag} กด T ขณะโฟกัสในช่องกรอก → ไม่เปลี่ยนแท็บ · พิมพ์ลงช่องได้", r["tab"] == "journal" and r["v"] == "t", json.dumps(r))
        check(f"{tag} ปุ่ม ＋/ปุ่มลัด T: ไม่มี console error · page error", not ce and not pe, json.dumps([ce[:3], pe[:3]], ensure_ascii=False))
    finally:
        browser.close()


def newuser_checks(pw):
    """เอกสารที่ไม่มี sizing/posSize ในตั้งค่า (ผู้ใช้ที่เริ่มหลัง CL2-d) → บันทึกตั้งค่าแล้วไม่สร้าง key เหล่านั้นขึ้นมา"""
    tag = "[chromium/1440x900]"
    doc = make_doc(with_legacy=False)
    browser, context, page, ce, pe, dialogs = launch(pw, 1440, 900, doc)
    try:
        page.evaluate("() => openSettings()"); page.wait_for_timeout(200)
        page.fill("#sCore", "3100000"); page.evaluate("() => saveSettings()"); page.wait_for_timeout(2000)
        st = dump_book(page, "main")["settings"]
        check(f"{tag} เอกสารไม่มี sizing/posSize: บันทึกตั้งค่าแล้วไม่สร้าง sizing/posSize · ทุนใหม่ถูกบันทึก", "sizing" not in st and "posSize" not in st and st["capital"]["core"] == 3100000, json.dumps(sorted(st.keys())))
        check(f"{tag} เอกสารไม่มี sizing: ไม่มี console error", not ce and not pe, json.dumps([ce[:3], pe[:3]]))
    finally:
        browser.close()


def grep_tests():
    src = open(INDEX, encoding="utf-8").read()
    lines = src.split("\n")
    must_not = ["SZ.", "const SZ", "szHeat", "szCfg", "szTradeLimit", "holdLimitPct", "renderHeatPanel", "szHeatPanel", "ggScoreOfSym", "GG_MAX", "SETUPS", "setupFactor", "wlGG",
                "ensure1RModel", "sRCore", "sPosSatB", "sRsBench", "sFfThrottle", "toggleSubmitted", "trendWord", "ensureIndustryExists", "populateIndustrySelect",
                "Trading Plan &amp; Positions", "พอกด Closed"]
    for n in must_not:
        left = [i + 1 for i, t in enumerate(lines) if n in t]
        check(f"grep index.html: ไม่เจอ {n}", not left, json.dumps(left[:5]))
    must = ["ffDeployCap", "ffCoreNow", "posOpenRisk", "openClosePos", "openTradeEdit", "openCancelModal", "delTrade", "makeTradeObject", "Calc.newCount", "cl2aStripLegacy", "portHeatLimit", "goPlanTop", "hdrPlanBtn"]
    for n in must:
        check(f"grep index.html: ยังเจอ {n}", any(n in t for t in lines))
    check("ไฟล์ tests/_extracted.js ไม่อยู่ใน tests/ แล้ว (ย้ายไป _to_delete/)", not os.path.exists(os.path.join(HERE, "_extracted.js")) and os.path.exists(os.path.join(HERE, "..", "_to_delete", "_extracted.js")))


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            positions_checks(pw, w, h, label)
            empty_checks(pw, w, h, label)
            settings_watch_checks(pw, w, h, label)
        newuser_checks(pw)
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900"), (375, 812, "375x812")):
            header_plus_checks(pw, w, h, label)
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
