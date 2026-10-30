#!/usr/bin/env python3
"""7E-1 — Calc.coreSize (สำเนา core-size.js) · ค่าตั้ง Core ต่อบัญชี · heat = % ของถังตัวเอง (migration heatV2) · ความเสี่ยงค้างสูตรเดียว · บล็อกสรุป Core ใหม่ · เก็บกวาด
mock Firestore (ไม่ต่อเน็ต) · 1440px + 430px · seed.json + ไม้ที่ใส่เองในเทส
รัน: python3 run_tests_phase23.py [/path/to/index.html] · ภาพเก็บที่ tests/screenshots/7e1-*.png
หมายเหตุ: เครื่องนี้ไม่มี node → เทส core_size_test.js รันในเบราว์เซอร์ (shim require/process) กับ "สำเนาใน index.html" — ต้องได้ 420/420 (7E-2b-1: +7 เคส)"""
import copy, json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))
results = []
T = p22.T



def fillx(page, sel, v):
    """SET1 — sCrL2Cap เป็นช่องซ้ำที่ซ่อน (รวมกับ Max open risk Core): ตั้งผ่าน JS แล้วยังซิงก์กับ sPortCore เหมือนเดิม"""
    page.evaluate("([s,v])=>{ const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event('input',{bubbles:true})); }", [sel, v])

def f2(x):
    """เหมือน fmt2 ในแอป: ทศนิยมสูงสุด 2 ตำแหน่ง ตัดเลข 0 ท้าย"""
    s = f"{x:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


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


COUNT_JS = """() => { const fs = window.firebase.firestore(); const orig = fs.collection.bind(fs); window.__setLog = [];
  fs.collection = n => { const c = orig(n); const od = c.doc.bind(c);
    c.doc = id => { const d = od(id); const os = d.set.bind(d); d.set = (data, o) => { window.__setLog.push({path:d.path, o:o||null}); return os(data, o); }; return d; };
    return c; }; }"""


def launch(pw, w, h, doc):
    """เหมือน p22.launch แต่ครอบ set() นับจำนวนครั้งที่เขียนเอกสารผู้ใช้ก่อน login (window.__setLog)"""
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
    page.evaluate(COUNT_JS)
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(1200)
    return browser, context, page, ce, pe, dialogs


def user_sets(page):
    return page.evaluate("() => (window.__setLog||[]).filter(x=>x.path==='users/testuid').length")


def dump_book(page, acct="main"):
    return page.evaluate("(a)=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return d && d.books && d.books[a]; }", acct)


def dump_doc(page):
    return page.evaluate("() => window.firebase.__mockDb.__dump()['users/testuid']")


def doc_with(main_trades=None, core_cap=None, limits=None, heat_flag=None):
    doc = p22.make_doc(main_trades=main_trades, with_legacy=False)
    if core_cap is not None:
        doc["books"]["main"]["settings"]["capital"]["core"] = core_cap
    for a in ("main", "fam"):
        st = doc["books"][a]["settings"]
        if limits is not None: st["limits"] = copy.deepcopy(limits)
        if heat_flag: st["heatV2"] = True
    return doc


def go_port(page):
    page.evaluate("() => { switchTab('plan'); setPlanScope('stock'); setPlanAcct('all'); }"); page.wait_for_timeout(300)


def core_tests_in_browser(page):
    return page.evaluate("""() => {
      const C = Calc.coreSize, o = {};
      o.has = !!C && typeof C.firstLot === 'function' && typeof window.CoreSize === 'object';
      const f = (f, m, extra) => C.firstLot(Object.assign({tank:700000, entry:100, stop:90, f:f, tier:'A', market:m}, extra||{})).qty;
      o.f1 = f(1,'US'); o.f75TH = f(0.75,'TH'); o.f50TH = f(0.5,'TH'); o.cash = f(1,'US',{cash:30000});
      const L = C.ladder({tier:'A', tank:700000, sl:70, levels:[{px:100},{px:90},{px:80}], budgetPct:0.10});
      o.ladderQty = L.rows.map(r=>r.qty); o.ladderRisk = L.fullRisk;
      o.gateOpen = C.openGate({fHistory:[0.75,0.75]}).open; o.gateUnknown = C.openGate({fHistory:[null]});
      return o; }""")


NODE_SHIM = """(src) => {
  const logs = []; let code = null;
  const path = {join: (...a) => a.join('/')};
  const fakeReq = m => { if (m === 'path') return path; return window.CoreSize; };
  const proc = {exit: c => { code = c; throw new Error('__exit__'); }};
  const con = {log: (...a) => logs.push(a.join(' '))};
  try { new Function('require','process','__dirname','console','module', src)(fakeReq, proc, '/x', con, {}); } catch (e) { if (e.message !== '__exit__') logs.push('ERR ' + e.message); }
  return {code, last: logs.slice(-2), fails: logs.filter(l => l.startsWith('FAIL')).length};
}"""


def calc_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with())
    try:
        o = core_tests_in_browser(page)
        check(f"{tag} Calc.coreSize มีใน window (getter · ผูกกับ CoreSize)", o["has"], json.dumps(o))
        check(f"{tag} coreSize.firstLot: ถัง 700,000 · Entry 100 · Stop 90 · f 1 → 700 · f 0.75 TH → 500 · f 0.5 TH → 300 · เงินสด 30,000 → 300",
              o["f1"] == 700 and o["f75TH"] == 500 and o["f50TH"] == 300 and o["cash"] == 300, json.dumps(o))
        check(f"{tag} coreSize.ladder A 100/90/80 SL 70 งบ 10% → 280/233/262 · เสี่ยงเต็ม 15,680", o["ladderQty"] == [280, 233, 262] and abs(o["ladderRisk"] - 15680) < 1e-6, json.dumps(o))
        check(f"{tag} coreSize.openGate [0.75,0.75] → เปิด · [null] → ไม่ทราบ (ไม่เปิด)", o["gateOpen"] is True and o["gateUnknown"]["reason"] == "unknown" and o["gateUnknown"]["open"] is False, json.dumps(o))
        src = open(os.path.join(ROOT, "tests", "core_size_test.js"), encoding="utf-8").read()
        r = page.evaluate(NODE_SHIM, src)
        m = re.search(r"(\d+) ผ่าน · (\d+) ไม่ผ่าน", " ".join(r["last"]))
        check(f"{tag} tests/core_size_test.js (รันบนสำเนาใน index.html ผ่านเบราว์เซอร์) = 471/471 (CZ1: +22 เคส · LN3fix2: +29 เคส · เดิม 420 ผ่านครบ) · exit 0", bool(m) and m.group(1) == "471" and m.group(2) == "0" and r["code"] == 0 and r["fails"] == 0, json.dumps(r, ensure_ascii=False))
        html = open(INDEX, encoding="utf-8").read()
        B = "/* === core-size.js BEGIN (สำเนา · ห้ามแก้ที่นี่ · แก้ที่ core-size.js แล้วคัดลอกใหม่) === */\n"
        E = "/* === core-size.js END === */"
        b = html.find(B); e = html.find(E, b) if b >= 0 else -1
        src_js = open(os.path.join(ROOT, "core-size.js"), encoding="utf-8", newline="").read()
        check(f"{tag} สำเนาใน index.html ตรงกับ core-size.js ทุกตัวอักษร (ตัดช่วง BEGIN/END)", b >= 0 and e > b and html[b + len(B):e] == src_js, f"b={b} e={e}")
        rc = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), "--check", INDEX], capture_output=True, text=True)
        check(f"{tag} python3 tools/sync_core_size.py --check = exit 0", rc.returncode == 0, rc.stdout + rc.stderr)
        html_pre = html[:b]
        check(f"{tag} สำเนาอยู่ใน <script> ก้อนแยกก่อนสคริปต์หลัก (ก้อนแรกไม่มีโค้ดอื่น)", html_pre.rstrip().endswith("<script>") and html[e + len(E):].lstrip().startswith("</script>"), html_pre[-40:])
        check(f"{tag} ไม่มี console error", not ce and not pe, json.dumps([ce[:3], pe[:3]]))
    finally:
        browser.close()


def sync_tool_checks():
    tmp = os.path.join(HERE, "_sync_tmp.html")
    try:
        html = open(INDEX, encoding="utf-8").read()
        B = "/* === core-size.js BEGIN (สำเนา · ห้ามแก้ที่นี่ · แก้ที่ core-size.js แล้วคัดลอกใหม่) === */\n"
        b = html.find(B) + len(B)
        open(tmp, "w", encoding="utf-8", newline="").write(html[:b] + "// stale\n" + html[b + 20:])
        r1 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), "--check", tmp], capture_output=True, text=True)
        r2 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), tmp], capture_output=True, text=True)
        r3 = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), "--check", tmp], capture_output=True, text=True)
        check("sync_core_size.py: สำเนาเพี้ยน → --check = exit 1 · รันแทนที่ → --check = exit 0 · ไฟล์ตรงกับ index.html จริงทุกไบต์",
              r1.returncode == 1 and r2.returncode == 0 and r3.returncode == 0 and open(tmp, encoding="utf-8").read() == html, f"{r1.returncode}{r2.returncode}{r3.returncode}")
    finally:
        if os.path.exists(tmp): os.remove(tmp)


def settings_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(heat_flag=True))
    try:
        page.evaluate("() => openSettings()"); page.wait_for_timeout(250)
        page.evaluate("() => document.querySelectorAll('#setOverlay details').forEach(d=>d.open=true)")
        vals = page.evaluate("""() => { const g = id => document.getElementById(id).value; return {mk:g('sCrMarket'), ra:g('sCrRiskA'), rb:g('sCrRiskB'), a:g('sCrTierA'), b:g('sCrTierB'), ca:g('sCrCapTotA'), cb:g('sCrCapTotB'), add:g('sCrAdd'), cap:g('sCrL2Cap'), warn:g('sCrL2Warn'),
            em:g('sCrEmerg'), lb:g('sCrLBudget'), lr:g('sCrLRisk'), ls:g('sCrLShare'), gate:g('sCrGate'), heatCore:g('sPortCore'), heatSat:g('sPortSatB')}; }""")
        check(f"{tag} ตั้งค่า: ส่วนความเสี่ยง Core มีค่าเริ่มต้นครบ (CZ1: Risk A/B 1.25/1.25 · เพดานไม้แรก 15/10 · เพดานรวม 25/25 · 50 · 20 · 15 · 7 · 10 · 2.5 · 30 · 2) · main ตลาด = US",
              vals == {"mk": "US", "ra": "1.25", "rb": "1.25", "a": "15", "b": "10", "ca": "25", "cb": "25", "add": "50", "cap": "20", "warn": "15", "em": "7", "lb": "10", "lr": "2.5", "ls": "30", "gate": "2", "heatCore": "20", "heatSat": "6"}, json.dumps(vals))
        units = page.evaluate("() => [...document.querySelectorAll('#crSec .f')].map(f=>(f.querySelector('.crUnit')||{}).textContent||'')")
        check(f"{tag} ตั้งค่า: ทุกช่องมีป้ายหน่วย (% ของถัง Core · % ของไม้ก่อนหน้า · ไม้ (1–6) · % ใต้ Stop · สัปดาห์) · ป้าย '% ของถัง Core' ≥ 8 ช่อง (TIER2: +6 ช่องเกณฑ์ Tier = 19 ช่อง)", len(units) == 24 and units.count("") == 1 and sum("% of Core bucket" in u for u in units) >= 8, json.dumps(units, ensure_ascii=False))
        mk = page.evaluate("() => ({main: coreRiskCfg('main').market, fam: coreRiskCfg('fam').market})")
        check(f"{tag} ตลาดเริ่มต้น: main = US · fam (ชื่อ Family) = TH · ชื่ออื่น = both", mk == {"main": "US", "fam": "TH"} and
              page.evaluate("() => { acctList.push({id:'zz', name:'Other', ports:['core']}); const m = coreRiskCfg('zz').market; acctList.pop(); return m; }") == "both", json.dumps(mk))
        maxheat = page.evaluate("""() => ['sTotal','sPortCore','sPortSatB'].map(id=>document.getElementById(id).closest('.f').textContent.replace(/\\s+/g,' ')).join(' ')""")   # SET1 — หมวด Max Heat ถูกรวมเข้าการ์ด Core/Sat · ตรวจป้ายที่ช่องเดิม
        check(f"{tag} Max Heat: ป้าย 'Core — % ของถัง Core' · 'Sat — % ของถัง Sat' · 'รวมทุก Port — % ของทุนบัญชี' · บรรทัด 'ใช้เป็นเพดานชั้น 2 ของ Core ด้วย'",
              all(k in maxheat for k in ("Core — % of Core bucket", "Sat — % of Sat bucket", "All ports — % of account capital", "Also used as the Core layer-2 cap")), maxheat)
        before_fam = json.dumps(dump_book(page, "fam"), sort_keys=True)
        # sync 2 ทาง
        fillx(page, "#sCrL2Cap", "18"); sync1 = page.input_value("#sPortCore")
        page.fill("#sPortCore", "17"); sync2 = page.input_value("#sCrL2Cap")
        check(f"{tag} เพดานชั้น 2 ↔ Max Heat Core เป็นค่าเดียวกัน (แก้ช่องไหน อีกช่องตาม)", sync1 == "18" and sync2 == "17", f"{sync1} {sync2}")
        fillx(page, "#sCrL2Cap", "20")
        # sat note
        page.fill("#sPortSatB", "8"); n8 = page.evaluate("() => { const e=document.getElementById('satHeatNote'); return e.style.display!=='none' ? e.innerText : ''; }")
        page.fill("#sPortSatB", "6"); n6 = page.evaluate("() => document.getElementById('satHeatNote').style.display")
        check(f"{tag} Sat ≠ 6 → ไม่มีบรรทัด 'หน้า Sat ใช้ค่าคงที่ 6%' อีกแล้ว (SR1: หน้า Sat อ่านช่องนี้จริง) · = 6 → ซ่อนเช่นกัน", n8 == "" and n6 == "none", f"{n8!r} {n6!r}")
        # แก้ 1 → 0.75 บันทึก
        page.fill("#sCrRiskA", "0.75")
        check(f"{tag} ค่าถูกต้อง → ปุ่มบันทึกกดได้ · ไม่มีข้อความแดง", page.evaluate("() => !document.getElementById('setSaveBtn').disabled && [...document.querySelectorAll('.crErr')].every(e=>!e.textContent)"))
        page.click("#setSaveBtn"); page.wait_for_timeout(1500)
        bm = dump_book(page, "main")
        check(f"{tag} แก้งบเสี่ยง 1 → 0.75 บันทึก → books.main.settings.coreRisk.riskPct = 0.75 (ครบ 19 ช่อง รวม maxLots · market US · TIER2 +6 เกณฑ์ Tier)",
              bm["settings"]["coreRisk"]["riskPct"] == 0.75 and len(bm["settings"]["coreRisk"]) == 29 and bm["settings"]["coreRisk"]["market"] == "US", json.dumps(bm["settings"].get("coreRisk")))
        check(f"{tag} books.fam ไม่เปลี่ยน (ไม่มี coreRisk) · coreSizeOpts('main').riskPct = 0.0075",
              json.dumps(dump_book(page, "fam"), sort_keys=True) == before_fam and "coreRisk" not in dump_book(page, "fam")["settings"] and abs(page.evaluate("() => coreSizeOpts('main').riskPct") - 0.0075) < 1e-12, "")
        opts = page.evaluate("() => coreSizeOpts('main')")
        check(f"{tag} coreSizeOpts: tierCap {{A:.15,B:.10}} (CZ1) · addRatio .5 · layer2Cap .20 · Warn .15 · emergency .07 · ladderBudget .10 · ladderRiskCap .025 · ladderShareCap .30 · gateStreak 2",
              opts["tierCap"] == {"A": 0.15, "B": 0.1} and opts["addRatio"] == 0.5 and abs(opts["layer2Cap"] - 0.2) < 1e-12 and abs(opts["layer2Warn"] - 0.15) < 1e-12 and abs(opts["emergencyPct"] - 0.07) < 1e-12
              and abs(opts["ladderBudget"] - 0.1) < 1e-12 and abs(opts["ladderRiskCap"] - 0.025) < 1e-12 and abs(opts["ladderShareCap"] - 0.3) < 1e-12 and opts["gateStreak"] == 2, json.dumps(opts))
        chk = page.evaluate("() => { const o = coreSizeOpts('main'); const r = Calc.coreSize.firstLot({tank:700000, entry:100, stop:90, f:1, tier:'A', riskPct:o.riskPct, tierCapPct:o.tierCap.A}); return r.qty; }")
        check(f"{tag} ส่งค่าตั้งเข้า Calc.coreSize: งบ 0.75% → ไม้แรก 525", chk == 525, str(chk))
        # ค่าผิด
        bad = [("sCrTierB", "20", "Tier B ต้องไม่เกิน Tier A"), ("sCrL2Warn", "25", "เหลืองที่ ต้องน้อยกว่าเพดานชั้น 2"), ("sCrRiskA", "0", "มากกว่า 0"), ("sCrRiskA", "-1", "มากกว่า 0"), ("sCrAdd", "150", "1–100")]
        for fid, v, msg in bad:
            page.evaluate("() => openSettings()"); page.wait_for_timeout(120)
            page.fill("#" + fid, v)
            st = page.evaluate("(id)=>({dis:document.getElementById('setSaveBtn').disabled, err:(document.querySelector('.crErr[data-err-for=\"'+id+'\"]')||{}).textContent||'', red:getComputedStyle(document.querySelector('.crErr[data-err-for=\"'+id+'\"]')).color})", fid)
            check(f"{tag} ค่าผิด {fid}={v} → ข้อความแดงใต้ช่อง ('{msg}') + ปุ่มบันทึกกดไม่ได้", st["dis"] and msg in st["err"] and st["red"] != "rgba(0, 0, 0, 0)", json.dumps(st, ensure_ascii=False))
        page.evaluate("() => saveSettings()"); page.wait_for_timeout(600)
        check(f"{tag} ค่าผิด: เรียก saveSettings() ตรง ๆ ก็ไม่บันทึก (ค่ายังเป็น 0.75) · ไม่ใช้ alert/confirm", dump_book(page, "main")["settings"]["coreRisk"]["riskPct"] == 0.75 and not dialogs, json.dumps(dialogs))
        # บันทึก sync cap
        page.evaluate("() => openSettings()"); page.wait_for_timeout(120)
        page.fill("#sPortCore", "17"); page.fill("#sCrL2Warn", "12"); page.click("#setSaveBtn"); page.wait_for_timeout(1500)
        bm = dump_book(page, "main")["settings"]
        check(f"{tag} บันทึก: limits.port.core = coreRisk.l2Cap = 17 (ค่าเดียวกัน) · coreRiskCfg().l2Cap = 17 · heatV2 คงอยู่", bm["limits"]["port"]["core"] == 17 and bm["coreRisk"]["l2Cap"] == 17 and page.evaluate("() => coreRiskCfg().l2Cap") == 17 and bm["heatV2"] is True, json.dumps(bm["limits"]))
        # ปิด core → ซ่อนส่วน
        page.evaluate("() => { acctList.find(a=>a.id==='main').ports = ['satB']; openSettings(); }"); page.wait_for_timeout(150)
        hid = page.evaluate("() => getComputedStyle(document.getElementById('crSec')).display")
        check(f"{tag} บัญชีที่ปิด port core → ซ่อนส่วนความเสี่ยง Core (acctApplyPortVisibility) · ปุ่มบันทึกยังกดได้", hid == "none" and page.evaluate("() => !document.getElementById('setSaveBtn').disabled"), hid)
        shot(page, f"7e1-settings-{w}.png", "#setOverlay .modal")
        check(f"{tag} ตั้งค่า: ไม่มี console error", not ce and not pe, json.dumps([ce[:3], pe[:3]]))
    finally:
        browser.close()


def settings_shot(pw, w, h):
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(heat_flag=True))
    try:
        page.evaluate("() => openSettings()"); page.wait_for_timeout(250)
        page.evaluate("() => document.querySelectorAll('#setOverlay details').forEach(d=>d.open=true)")
        page.evaluate("() => { const m=document.querySelector('#setOverlay .modal'); m.style.maxHeight='none'; m.style.overflow='visible'; }")
        page.fill("#sCrTierB", "20"); page.wait_for_timeout(100)
        shot(page, f"7e1-settings-risk-{w}.png", "#crSec")
        page.fill("#sCrTierB", "5")
        page.evaluate("() => { const s = document.getElementById('sPortCore').closest('.setsec'); s.scrollIntoView();   /* SET1 — หมวด Max Heat รวมเข้าการ์ด Core */ }")
        shot(page, f"7e1-settings-maxheat-{w}.png", "#setOverlay .setsec:has(#sTotal)")
    finally:
        browser.close()


def satcap_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(heat_flag=True))
    try:
        raw = SEED["books"]["main"]["settings"]["capital"]["satB"]
        page.evaluate("() => openSettings()"); page.wait_for_timeout(200)
        shown = page.input_value("#sSatB")
        tot = page.evaluate("() => document.getElementById('totalHint').innerText")
        check(f"{tag} ทุน Sat ในตั้งค่า: ค่า {raw} → ช่องแสดง 31515.15 · ทุนรวมใต้ช่องใช้ fmt0 (ไม่มีทศนิยม)", shown == "31515.15" and re.search(r"\$31,515 ", tot) is not None, f"{shown!r} {tot!r}")
        page.click("#setSaveBtn"); page.wait_for_timeout(1500)
        got = dump_book(page, "main")["settings"]["capital"]["satB"]
        check(f"{tag} บันทึกโดยไม่แก้ช่อง → ค่าที่เก็บ = ค่าเดิม {raw} (ไม่ปัดทับ · แบบ 'คงค่าเดิม')", got == raw, repr(got))
        page.evaluate("() => openSettings()"); page.wait_for_timeout(150)
        page.fill("#sSatB", "12345.678"); page.click("#setSaveBtn"); page.wait_for_timeout(1500)
        got2 = dump_book(page, "main")["settings"]["capital"]["satB"]
        check(f"{tag} แก้ช่องเอง 12345.678 → เก็บตามที่พิมพ์ (ปัดเฉพาะตอนแสดง)", got2 == 12345.678, repr(got2))
    finally:
        browser.close()


def migration_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    old = {"trade": 1, "port": {"core": 25, "satB": 50}, "total": 6}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(limits=old))
    try:
        page.wait_for_timeout(1500)
        d = dump_doc(page)
        m, f = d["books"]["main"]["settings"], d["books"]["fam"]["settings"]
        check(f"{tag} heat migration: limits.port {{core:25,satB:50}} ไม่มีธง → {{core:20,satB:6}} + heatV2 true (ทั้ง main และ fam) · trade/total คงเดิม",
              m["limits"]["port"] == {"core": 20, "satB": 6} and m.get("heatV2") is True and f["limits"]["port"] == {"core": 20, "satB": 6} and f.get("heatV2") is True and m["limits"]["trade"] == 1 and m["limits"]["total"] == 6, json.dumps([m.get("limits"), f.get("limits")]))
        n = user_sets(page)
        check(f"{tag} จำนวนครั้งที่เขียน Firestore (users/testuid) จาก migration = 1", n == 1, str(n))
        page.wait_for_timeout(2000)
        check(f"{tag} migration ไม่เขียนวนซ้ำ (รออีก 2 วินาที ยัง = 1)", user_sets(page) == 1, str(user_sets(page)))
        check(f"{tag} portHeatLimit ตามค่าใหม่ (core 20 · satB 6)", page.evaluate("() => [portHeatLimit('core'), portHeatLimit('satB')]") == [20, 6])
        seed2 = copy.deepcopy(d)
        seed2["books"]["main"]["settings"]["limits"]["port"]["core"] = 18
        browser.close()
        browser, context, page, ce, pe, dialogs = launch(pw, w, h, seed2)
        page.wait_for_timeout(1500)
        d2 = dump_doc(page)
        check(f"{tag} โหลดใหม่หลังผู้ใช้แก้ core เป็น 18 (มีธงแล้ว) → ยังเป็น 18 · ไม่เขียนกลับ (จำนวนเขียน = 0)", d2["books"]["main"]["settings"]["limits"]["port"]["core"] == 18 and user_sets(page) == 0 and page.evaluate("() => portHeatLimit('core')") == 18, f"{d2['books']['main']['settings']['limits']} sets={user_sets(page)}")
    finally:
        try: browser.close()
        except Exception: pass


def formula_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc = doc_with(core_cap=100000, heat_flag=True)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc)
    try:
        go_port(page)
        st = page.evaluate("() => ({fx: state.settings.fx, core: state.settings.capital.core, sat: state.settings.capital.satB, strat: state.settings.strategicCash||0})")
        fx, tank = st["fx"], st["core"]
        cap = st["core"] + st["sat"] * fx + st["strat"]
        blk = page.evaluate("""() => { const q = s => document.querySelector('#portsSum '+s); const t = e => e ? e.innerText.replace(/\\s+/g,' ').trim() : null;
            return {open:t(q('[data-sum="open"]')), held:t(q('[data-sum="held"]')), pos:t(q('[data-sum="pos"]')), plan:t(q('[data-sum="plan"]')), drop:t(q('[data-sum="acctdrop"]')), head:t(q('.sumHead')), all:t(document.getElementById('portsSum'))}; }""")
        check(f"{tag} สูตรเดียว: บล็อกสรุป ความเสี่ยงค้าง Core = ฿100 (ไม่ใช่ 125) · % ของถัง = 100 ÷ ทุน Core × 100 = {f2(100/tank*100)}%",
              "฿100 " in blk["open"] + " " and "125" not in blk["open"] and f"{f2(100/tank*100)}%" in blk["open"] and "/ 20%" in blk["open"], blk["open"])
        check(f"{tag} บล็อกสรุป: 'จากทุน' · '≈ x% ของบัญชี' = {f2(100/cap*100)}%", "จากทุน" in blk["open"] and f"≈ {f2(100/cap*100)}% ของบัญชี" in blk["open"], blk["open"])
        strip = page.evaluate("""() => { const g = document.querySelector('#strip .acctCard[data-priv="p-acct-main"] .acctGrp[data-grp="stock"]'); return {th: g && +g.dataset.openTh, txt: g && g.innerText.replace(/\\s+/g,' ')}; }""")
        possum = page.evaluate("() => { const e=document.querySelector('#planSections .acctSec[data-acct=\"main\"] [data-pos-sum]'); return e ? e.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} สูตรเดียว 3 จุดตรงกัน: บล็อกสรุป ฿100 · แถบบัญชี Hold ฿100 · Positions แถวรวม Core ฿100", strip["th"] == 100 and "Hold 2 · ฿100" in strip["txt"] and "Core ฿100" in possum, json.dumps([strip, possum], ensure_ascii=False))
        check(f"{tag} แถบบัญชี: % ข้างหลัง Hold = % ของถัง Core ({f2(100/tank*100)}%) + ตัวเล็ก 'ถัง'", f"({f2(100/tank*100)}% ถัง)" in strip["txt"], strip["txt"])
        rr = page.evaluate("""() => { const T = state.trades.reduce((m,t)=>(m[t.id]=t,m),{}); return {riskC: riskOf(T.tc), riskTB: riskTHBOf(T.tb), rClosed: realizedROf(T.te), sumOpen: summarize().per.core.open, ot: openRiskTHB(T.tc), oa: openRiskTHB(T.ta), od: openRiskTHB(T.td), oe: openRiskTHB(T.te)}; }""")
        check(f"{tag} riskOf/riskTHBOf/realizedROf ไม่เปลี่ยน (C riskOf = 25 · Journal R ของไม้ปิด = 2) · openRiskTHB: ล็อก = 0 · Sat open = 570×fx · plan = riskTHBOf · closed = 0",
              rr["riskC"] == 25 and rr["riskTB"] == 100 and rr["rClosed"] == 2 and rr["ot"] == 0 and abs(rr["oa"] - 570 * fx) < 1e-6 and abs(rr["od"] - 0.1 * 20 * 100 * fx) < 1e-6 and rr["oe"] == 0 and rr["sumOpen"] == 100, json.dumps(rr))
        check(f"{tag} เงินที่ถือ: B+C = 100×10 + 200×5 = ฿2,000 · {f2(2000/tank*100)}% ของถัง · เงินว่าง = ถัง − 2,000 = ฿{tank-2000:,}", "฿2,000" in blk["held"] and f"{f2(2000/tank*100)}% ของถัง" in blk["held"] and f"เงินว่าง ฿{tank-2000:,}" in blk["held"], blk["held"])
        check(f"{tag} ตำแหน่ง: 2 ตัว · ล็อกกำไร 1 ตัว · ไม่มีช่องแผนที่รอ (ไม่มีไม้ plan ของ Core)", "2 ตัว" in blk["pos"] and "ล็อกกำไร 1 ตัว" in blk["pos"] and blk["plan"] is None, json.dumps(blk, ensure_ascii=False))
        exp = round((100 + 570 * fx) / cap * 100, 2)
        check(f"{tag} 'ถ้าทุกไม้โดน Stop บัญชีลด' = (100 + 570×fx) ÷ totalTHB × 100 = {f2(exp)}% · '(Core จากราคาปิด · Sat จากทุน)' + เทียบทุน −฿75 (7E-2: แก้ข้อความ · ตัวเลขเท่าเดิมเพราะไม่มีการ์ด = Core นับจากทุน)", f"≈ {f2(exp)}%" in blk["drop"] and "(Core จากราคาปิด · Sat จากทุน)" in blk["drop"] and "เทียบทุน: −฿75" in blk["drop"], f"{blk['drop']} exp={exp}")
        check(f"{tag} หัวบล็อก: 'Core Port' · ทุน ฿ · ≈ % ของทุนรวม · ป้ายตลาด US", "Core Port" in blk["head"] and "ทุน ฿100,000" in blk["head"] and "ของทุนรวม" in blk["head"] and "US" in blk["head"], blk["head"])
        check(f"{tag} ตัดของเดิม: ไม่มีป้าย 'เกิน limit' · ไม่มี Open Risk/Planned แบบเดิม · ไม่มีบรรทัด Positions n open", "เกิน limit" not in blk["all"] and "Open Risk" not in blk["all"] and "Planned" not in blk["all"] and " open" not in blk["all"].replace("ล็อก", ""), blk["all"])
        foot = page.evaluate("() => document.getElementById('foot').innerText")
        expF = f"heat: Core {f2(100/tank*100)}% / 20% ของถัง · Sat {f2(570*fx/(st['sat']*fx)*100)}% / 6% ของถัง · รวม {f2(exp)}% ของบัญชี (ฐาน THB @ {f2(fx)}) — sync ผ่าน Firestore"
        check(f"{tag} footer รูปแบบใหม่: 'heat: Core x% / 20% ของถัง · Sat y% / 6% ของถัง · รวม z% ของบัญชี (ฐาน THB @ fx) — sync ผ่าน Firestore'", foot.strip() == expF, f"{foot!r} vs {expF!r}")
        # grid
        lay = page.evaluate("""() => { const g = document.querySelector('#portsSum .sumG3'); return {cols: getComputedStyle(g).gridTemplateColumns.split(' ').length, sw: document.documentElement.scrollWidth}; }""")
        want = 3 if w > 700 else 2
        check(f"{tag} sumGrid {want} คอลัมน์ ({'desktop' if w>700 else '≤700px'}) · ไม่ล้นแนวนอน (scrollWidth {lay['sw']} ≤ {w})", lay["cols"] == want and lay["sw"] <= w, json.dumps(lay))
        # สี 14.9 / 15 / 20
        res = {}
        for pctv, qty in ((14.9, 1490), (15, 1500), (20, 2000)):
            page.evaluate("(q)=>{ state.trades = [{id:'x1', date:'2026-09-01', sym:'NVDA', port:'core', bias:'Long', entry:100, sl:90, tp:null, qty:q, mult:1, cur:'THB', status:'open'}]; render(); }", qty)
            r = page.evaluate("""() => { const c = document.querySelector('#portsSum [data-sum="open"]'); return {lv:c.dataset.level, big:(c.querySelector('.sumBig').innerText+' '+c.querySelector('[data-sum-full]').innerText).replace(/\\s+/g,' '), col:getComputedStyle(c.querySelector('.sumBig')).color, stop:!!c.querySelector('[data-stop-buy]'), txt:c.innerText}; }""")
            res[pctv] = r
            shot(page, f"7e1-portsum-{ {14.9:'ok',15:'warn',20:'over'}[pctv] }-{w}.png", "#portsSum")
        check(f"{tag} สีช่องความเสี่ยง: 14.9% → ปกติ · 15% → เหลือง · 20% → แดง + 'งดซื้อเพิ่ม' (เฉพาะแดง)",
              res[14.9]["lv"] == "ok" and res[15]["lv"] == "warn" and res[20]["lv"] == "over" and res[20]["stop"] and not res[14.9]["stop"] and not res[15]["stop"] and "งดซื้อเพิ่ม" in res[20]["txt"]
              and len({res[14.9]["col"], res[15]["col"], res[20]["col"]}) == 3, json.dumps(res, ensure_ascii=False))
        check(f"{tag} ตัวใหญ่ = % ของถัง Core ({res[15]['big']})", "15% / 20%" in res[15]["big"] and "14.9% / 20%" in res[14.9]["big"], json.dumps(res[15]))
        # ถือเกินถัง / plan cell
        page.evaluate("() => { state.settings.capital.core = 1500; state.trades = [{id:'x1', date:'2026-09-01', sym:'NVDA', port:'core', bias:'Long', entry:100, sl:90, tp:null, qty:20, mult:1, cur:'THB', status:'open'},{id:'x2', date:'2026-09-01', sym:'PLN', port:'core', bias:'Long', entry:50, sl:45, tp:null, qty:10, mult:1, cur:'THB', status:'plan'}]; render(); }")
        r2 = page.evaluate("""() => { const q = s => document.querySelector('#portsSum '+s); const t = e => e ? e.innerText.replace(/\\s+/g,' ').trim() : null;
            return {free:t(q('[data-sum-free]')), neg:!!q('[data-sum-free].sumNeg'), col:q('[data-sum-free]') && getComputedStyle(q('[data-sum-free]')).color, plan:t(q('[data-sum="plan"]'))}; }""")
        check(f"{tag} ถือเกินถัง (ถือ 2,000 > ถัง 1,500) → แดง 'ถือเกินถัง ฿500' · มีไม้ plan → ช่อง 'แผนที่รอ (Planned)' แสดง (1 ตัว · เสี่ยง +฿50)",
              r2["neg"] and "ถือเกินถัง ฿500" in r2["free"] and r2["plan"] and "แผนที่รอ" in r2["plan"] and "1 ตัว" in r2["plan"] and "+฿50" in r2["plan"], json.dumps(r2, ensure_ascii=False))
        check(f"{tag} สูตรเดียว/บล็อกสรุป: ไม่มี console error", not ce and not pe, json.dumps([ce[:3], pe[:3]]))
    finally:
        browser.close()


def strip_shot(pw, w, h):
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(core_cap=100000, heat_flag=True))
    try:
        go_port(page)
        page.evaluate("() => document.querySelectorAll('#strip .acctCard .acctRow1').forEach(r=>{ if(!r.parentElement.classList.contains('open')) r.click(); })"); page.wait_for_timeout(200)
        shot(page, f"7e1-strip-{w}.png", "#strip")
        page.evaluate("() => window.scrollTo(0, document.body.scrollHeight)"); page.wait_for_timeout(200)
        shot(page, f"7e1-footer-{w}.png", "#foot")
    finally:
        browser.close()


def misc_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc_with(core_cap=100000, heat_flag=True))
    try:
        page.evaluate("() => openKbHelp()"); page.wait_for_timeout(200)
        rows = page.evaluate("() => [...document.querySelectorAll('#kbHelpOverlay .kbRow')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} ปุ่มลัด: หน้า (?) มีแถว 'T — ไปหน้าแผน' · ปุ่มอื่นคงอยู่ (1–6 · C · V · ? · Esc)", any(r.startswith("T") and "ไปหน้าแผน" in r for r in rows) and all(any(r.startswith(k) for r in rows) for k in ("1–6", "C", "V", "?", "Esc")), json.dumps(rows, ensure_ascii=False))
        page.keyboard.press("Escape")
        errs = None
        for t in ("flow", "mix", "watch", "plan", "journal"):
            try:
                page.evaluate(f"() => switchTab('{t}')"); page.wait_for_timeout(200)
            except Exception as e:
                errs = f"{t}: {e}"
        page.evaluate("() => { switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        page.evaluate("() => setPlanScope('stock')"); page.wait_for_timeout(200)
        page.evaluate("() => openSettings()"); page.wait_for_timeout(200)
        sw = page.evaluate("() => document.documentElement.scrollWidth")
        check(f"{tag} เปิดทุกแท็บ + หน้า Sat (scope future) + ตั้งค่า ไม่ throw · ไม่ล้นแนวนอน ({sw} ≤ {w}) · ไม่มี console error/page error", errs is None and sw <= w and not ce and not pe, json.dumps([errs, ce[:3], pe[:3]]))
        sat = page.evaluate("() => SAT7D_HEAT_MAX")
        check(f"{tag} SAT7D_HEAT_MAX ยังเป็น 6 (ไม่ถูกแตะ)", sat == 6, str(sat))
        # new user: ธงใหม่ในหนังสือเปล่า
    finally:
        browser.close()


def newuser_checks(pw):
    tag = "[chromium/1440]"
    browser, context, page, ce, pe, dialogs = launch(pw, 1440, 900, {})
    try:
        page.wait_for_timeout(800)
        st = page.evaluate("() => ({heat: state.settings.heatV2, port: state.settings.limits.port, cr: state.settings.coreRisk === undefined})")
        check(f"{tag} ผู้ใช้ใหม่ (เอกสารว่าง): settings.heatV2 = true · limits.port = {{core:20,satB:6}} · ไม่มี coreRisk (อ่านแบบเติมค่าเริ่มต้น ไม่เขียนกลับ)", st["heat"] is True and st["port"] == {"core": 20, "satB": 6} and st["cr"], json.dumps(st))
    finally:
        browser.close()


def grep_tests():
    src = open(INDEX, encoding="utf-8").read()
    for n in ("core-size.js BEGIN", "Calc.coreSize", "coreSize:", "coreRiskCfg", "coreSizeOpts", "openRiskTHB", "heatV2", "จากทุน"):
        check(f"grep index.html: ยังเจอ {n}", n in src)
    orig = os.path.join(ROOT, "core-size.js")
    check("core-size.js ต่างจากต้นฉบับก่อน 7E-2b-1 เฉพาะ 2 จุดตามข้อ 0 (roicMin 0.12 · canPlaceLadder shareCap/l2Cap · +TIER2 +DD1 รวม 13 hunk · CZ1 +12 = 25 · LN3fix2 +8 = 33 hunk)", core_size_only_two_spots())


def core_size_only_two_spots():
    """7E-2b-1: core-size.js ต่างจาก core-size.backup-pre-7E2b1.js เฉพาะ 2 จุดตามข้อ 0 (roicMin · canPlaceLadder shareCap/l2Cap) = 3 hunk เดิม · TIER2 เพิ่มรวมเป็น 11 hunk · DD1 +2 = 13 · CZ1 +12 = 25"""
    import difflib
    a = open(os.path.join(ROOT, "core-size.backup-pre-7E2b1.js"), encoding="utf-8").read().splitlines()
    b = open(os.path.join(ROOT, "core-size.js"), encoding="utf-8").read().splitlines()
    d = list(difflib.unified_diff(a, b, lineterm="", n=0))
    ch = [l for l in d if (l.startswith("+") or l.startswith("-")) and not l.startswith("+++") and not l.startswith("---")]
    return sum(1 for l in d if l.startswith("@@")) == 33 and any("roicMin: 0.12" in l for l in ch) and any("shareCap" in l for l in ch) and any("l2Cap" in l for l in ch)

def main():
    with sync_playwright() as pw:
        sync_tool_checks()
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            calc_checks(pw, w, h, label)
            settings_checks(pw, w, h, label)
            satcap_checks(pw, w, h, label)
            migration_checks(pw, w, h, label)
            formula_checks(pw, w, h, label)
            misc_checks(pw, w, h, label)
            settings_shot(pw, w, h)
            strip_shot(pw, w, h)
        newuser_checks(pw)
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
