#!/usr/bin/env python3
"""CL2-a — รีเซ็ตข้อมูลครั้งเดียว (gate) + ลบโค้ด Weekly Plan / ทาง V3-off / Sat.A / _v migration / Watchlist เดิม
mock Firestore (ไม่ต่อเน็ต) · 1440px + 430px · ภาพเก็บที่ tests/screenshots/cl2a-*.png
รัน: python3 run_tests_phase19.py   (ใช้ seed.pre-CL2a.json เป็นฐานของเอกสาร "ก่อนรีเซ็ต" + เติมข้อมูลเก่าครบทุก key ในไฟล์นี้)
หมายเหตุ mock: __denyPath ปฏิเสธทั้ง get/set/delete ของ path นั้น — เคส "ลบ satWeek ไม่ได้" จึง deny ทีละเอกสาร (get ของคอลเลกชันยังผ่าน · delete ของเอกสารล้ม)
        ซึ่งตรงกับสถานการณ์จริง (rules อนุญาต read แต่ยังไม่อนุญาต delete)"""
import copy, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "tools")))
import cl2a_seed  # noqa: E402  (สคริปต์สร้าง seed — phase19 ตรวจว่าสูตรตรงกับ cl2aStripLegacy ตัวจริง)

SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
INDEX = base.DEFAULT_INDEX
results = []
UID = "testuid"
WORD = "รีเซ็ต"
RS_WORD = "กู้คืน"


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


# ───────────────────────── ชุดข้อมูล "ก่อนรีเซ็ต" (ข้อมูลเก่าครบทุก key ที่ต้องล้าง/เก็บ) ─────────────────────────
PRE = json.load(open(os.path.join(HERE, "seed.pre-CL2a.json"), encoding="utf-8"))


def trade(id, port, status, sym, **kw):
    d = {"id": id, "date": "2026-09-10", "sym": sym, "port": port, "bias": "Long", "entry": 100, "sl": 95, "tp": None, "qty": 10, "mult": 1,
         "cur": "THB" if port == "core" else "USD", "status": status, "unplanned": False}
    d.update(kw); return d


def old_book(prefix, cap_core, cap_satb):
    return {
        "settings": {
            "fx": 33, "fxAuto": False,
            "capital": {"core": cap_core, "satA": 5000, "satA_archived": 1000, "satB": cap_satb, "option": 1500},
            "posSize": {"core": 4, "satA": 4, "satB": 15},
            "limits": {"trade": 1, "port": {"core": 3, "satA": 3, "satB": 3}, "total": 6},
            "sizing": {"r": {"core": 1, "satA": 1}, "cap": {"core": 12.5, "satA": 25}, "ffThrottle": True},
            "satBVol": {"XAUUSD": {"lo": 0, "hi": 0}}, "satBVolV2": True, "satBLowRisk": 1, "szCapSatA25": True, "sz1Rv2": True,
            "brokers": {"XM": {"XAUUSD": {"contract": 100, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}}},
        },
        "trades": [trade(prefix + "c1", "core", "open", "AOT"), trade(prefix + "c2", "core", "closed", "PTT", exitPrice=110, exitDate="2026-09-20"),
                   trade(prefix + "b1", "satB", "plan", "XAUUSD", qty=0.1, mult=100), trade(prefix + "a1", "satA", "open", "NVDA"),
                   trade(prefix + "a2", "satA", "closed", "AMD", exitPrice=90, exitDate="2026-09-21")],
        "watchlist": [{"id": "OLD", "sym": "OLD", "port": "core", "note": "เดิม"}],
        "ideas": [{"id": "i1", "sym": "AAA"}], "checklistDrafts": [{"id": "d1"}], "failLog": [{"id": "f1"}],
        "weeklyPlan": {"2026-09-27": {"XAUUSD": {"on": True, "trend": "Long", "locked": True}}},
        "sbPlan": {"XAUUSD": {"zoneOn": True}}, "sbProducts": [{"key": "XAUUSD", "on": True}],
        "tabsOffsetV2": True, "satBNoteV1": True, "phase" + "7mV1": True,
        "watchSortMode": {"core": "date", "satA": "date", "satB": "date"},
        "industries": ["Semis", "Banks"], "sat_since": "2026-01-01", "_probeX": prefix + "probe",
        "fundflow": {"ctx": {"f": "", "rsp": 1}, "dials": []},
        "reasonTags": {"exit": [{"id": "t1", "label": "TP", "offPlan": False}]},
    }


def pre_doc():
    d = copy.deepcopy(PRE)
    d["books"] = {"main": old_book("m", 3000000, 31515.15), "fam": old_book("f", 2000000, 20000.0)}
    d["accounts"] = [{"id": "main", "name": "บัญชีหลัก", "ports": ["core", "satA", "satB"]}, {"id": "fam", "name": "Family", "ports": ["core", "satA"]}]
    d["activeAccount"] = "main"
    d.pop("cl2aResetAt", None); d.pop("cl2aSatCleanAt", None)
    return d


def flagged_doc():
    d = cl2a_seed.build_seed(json.load(open(os.path.join(HERE, "seed.pre-CL2a.json"), encoding="utf-8")))
    return d


EXTRA_DOCS = [
    (["users", UID, "satIdeas", "i1"], {"v3": True, "asset": "XAUUSD", "bias": "Long", "week": "2026-W40", "status": "active"}),
    (["users", UID, "satIdeas", "i2"], {"v3": True, "asset": "BTCUSD", "bias": "Short", "week": "2026-W40", "status": "closed"}),
    (["users", UID, "satIdeas", "i3"], {"asset": "BRENT", "bias": "Long", "week": "2026-W39", "status": "draft"}),
    (["users", UID, "satWeek", "2026-W40"], {"XAUUSD": {"bias": "Long"}}),
    (["users", UID, "satWeek", "2026-W39"], {"XAUUSD": {"bias": "None"}}),
    (["users", UID, "satConfig", "setups"], {"setups": {"XAUUSD": ["Sweep", "BigBar"]}}),
    (["users", UID, "macroPlaybook", "2026Q4-v001"], {"schema": "macroPlaybook/v1", "quarter": "2026Q4", "status": "active", "versionNo": 1, "savedAt": "2026-09-01T00:00:00.000Z",
                                                        "view": {"headline": "h", "thesis": "t", "pillars": []}, "assets": {}}),
    (["users", UID, "watchlist", "AAPL"], {"ticker": "AAPL", "market": "US", "port": "core", "note": "", "industry": "Semis", "added_at": "2026-09-01"}),
    (["research", "AAPL"], {"ticker": "AAPL", "name": "Apple", "port": "core", "in_watchlist": True}),
]
KEEP_COUNTS = {"satConfig": 1, "macroPlaybook": 1, "watchlist": 1, "research": 1}


# ───────────────────────── launcher ─────────────────────────
def launch(pw, w, h, doc, extra=None, wait="app"):
    launch_kwargs = {"headless": True}
    if base.CHROMIUM_PATH:
        launch_kwargs["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**launch_kwargs)
    context = browser.new_context(viewport={"width": w, "height": h})
    from ff_stub import FF_STUB; context.add_init_script(FF_STUB)
    page = context.new_page()
    ce, pe, dialogs = [], [], []
    page.on("console", lambda m: ce.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: pe.append(str(e)))
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))
    page.route(re.compile(r"gstatic\.com/firebasejs"), lambda r: r.fulfill(status=200, content_type="application/javascript", body=base.MOCK_FB))
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), lambda r: r.fulfill(status=200, content_type="text/css", body=""))
    page.route(re.compile(r"fundflow\.json|open\.er-api\.com|api\.twelvedata\.com"), lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps({})))
    page.goto("file://" + INDEX, wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("() => localStorage.setItem('bkLastBackupAt', String(Date.now()))")   # กันรอบ backup อัตโนมัติ (Mac) ยิงเองระหว่างเทส
    page.evaluate("""([doc, extra])=>{ window.__MOCK_UID='testuid'; const db=window.firebase.__mockDb;
        if(doc) db.__seedDoc(['users','testuid'], doc);
        (extra||[]).forEach(([p,d])=>db.__seedDoc(p, d));
        window.__seq = 0; window.__ops = []; window.__dl = []; window.__rc = {};
        const wrap = (o) => new Proxy(o, {get(t, k){ const v = t[k]; if(typeof v!=='function') return v;
          return (...a)=>{ const r = v.apply(t, a);
            if(['set','update','delete','add'].indexOf(String(k))>=0) window.__ops.push({seq:++window.__seq, m:String(k), p:t.path||'?'});
            return (r && typeof r==='object' && r.path!==undefined && typeof r.then!=='function') ? wrap(r) : r; }; }});
        const oc = db.collection.bind(db); db.collection = n => wrap(oc(n));
        window.bkTriggerDownload = (json, name) => { window.__dl.push({name, json, seq:++window.__seq}); };
        ['render','renderAcctBar','renderPlanSections','renderWatchlist','renderJournal','renderPortfolioMix','renderFundflow','pbRender','renderSat7d'].forEach(n=>{
          const o = window[n]; if(typeof o!=='function') return; window.__rc[n]=0;
          window[n] = function(){ window.__rc[n]++; return o.apply(this, arguments); }; });
    }""", [doc, extra])
    page.fill("#authEmail", "test@example.com")
    page.fill("#authPass", "password123")
    page.click("#authSubmit")
    sel = {"app": "#mainWrap", "gate": "#cl2aGate", "error": "#errorScreen"}.get(wait)
    if sel:
        page.wait_for_selector(sel, state="visible", timeout=8000)
    page.wait_for_timeout(500)
    return browser, context, page, ce, pe, dialogs


def dump(page): return page.evaluate("() => window.firebase.__mockDb.__dump()")
def ops(page): return page.evaluate("() => window.__ops")
def user_ops(page): return [o for o in ops(page) if o["p"] == "users/" + UID and o["m"] in ("set", "update")]
def vis(page, sel): return page.evaluate("(s)=>{ const e=document.querySelector(s); return !!e && getComputedStyle(e).display!=='none' && e.getBoundingClientRect().height>0; }", sel)
def count_col(d, col): return len([k for k in d if re.match(r"users/%s/%s/[^/]+$" % (UID, col), k)])
def canon(o): return json.dumps(o, sort_keys=True, ensure_ascii=False)

DROP_KEYS = cl2a_seed.DROP_KEYS
DROP_PATHS = cl2a_seed.DROP_PATHS


def has_path(o, path):
    for k in path:
        if not isinstance(o, dict) or k not in o: return False
        o = o[k]
    return True


def dropped_left(book):
    # ideas/checklistDrafts/failLog: โค้ดยังอ่านถึง CL2-b → buildStateFromBookRaw ใส่ [] ให้ (spec §3.5) — ยอมรับเฉพาะค่า [] ว่าง
    left = [k for k in DROP_KEYS if k in book and not (k in ("ideas", "checklistDrafts", "failLog") and book[k] == [])]
    left += [".".join(p) for p in DROP_PATHS if has_path(book, p)]
    left += [t["id"] for t in (book.get("trades") or []) if t.get("port") not in ("core", "satB")]
    return left


def type_word(page, word=WORD):
    page.fill("#cl2aWord", word)
    page.wait_for_timeout(80)


def run_gate(page, wait_ms=2500):
    type_word(page)
    page.click("#cl2aGo")
    page.wait_for_timeout(wait_ms)


def sheet_rows(page):
    return page.evaluate("() => Object.fromEntries([...document.querySelectorAll('.cl2a-sheet [data-cl2a-res]')].map(e=>[e.dataset.cl2aRes, e.innerText.replace(/\\s+/g,' ').trim()]))")


def close_sheet(page):
    page.evaluate("() => { if(typeof cl2aSheetClose==='function') cl2aSheetClose(); }")


# ═══════════════════════════ A) ฟังก์ชันบริสุทธิ์ ═══════════════════════════
def pure_tests(page, tag):
    old = old_book("m", 3000000, 31515.15)
    r = page.evaluate("""(b)=>{ const before = JSON.stringify(b); const s = cl2aStripLegacy(b), z = cl2aResetBook(b);
        return {s, z, untouched: JSON.stringify(b)===before, same: s===b, zsame: z===b}; }""", old)
    s, z = r["s"], r["z"]
    check(f"{tag} Strip: key บนสุดที่ต้องตัด (weeklyPlan · sbPlan · sbProducts · ideas · checklistDrafts · failLog · watchlist · tabsOffsetV2 · satBNoteV1 · phase7mV1) หายครบ",
          not [k for k in DROP_KEYS if k in s], json.dumps([k for k in DROP_KEYS if k in s]))
    check(f"{tag} Strip: ฟิลด์ settings ที่ต้องล้าง (capital.satA · satA_archived · posSize.satA · limits.port.satA · sizing.r.satA · sizing.cap.satA · satBVol · satBVolV2 · satBLowRisk · szCapSatA25) + watchSortMode.satA หายครบ",
          not [".".join(p) for p in DROP_PATHS if has_path(s, p)], json.dumps([".".join(p) for p in DROP_PATHS if has_path(s, p)]))
    check(f"{tag} Strip: ของที่เก็บอยู่ครบ — _probeX · settings.brokers · capital.core/satB/option · fx · industries · reasonTags · fundflow · sat_since · sizing.r.core · limits.port.core/satB · sz1Rv2",
          s.get("_probeX") == "mprobe" and s["settings"]["brokers"] == old["settings"]["brokers"] and s["settings"]["capital"] == {"core": 3000000, "satB": 31515.15, "option": 1500}
          and s["settings"]["fx"] == 33 and s["industries"] == old["industries"] and s["reasonTags"] == old["reasonTags"] and s["fundflow"] == old["fundflow"]
          and s["sat_since"] == "2026-01-01" and s["settings"]["sizing"]["r"] == {"core": 1} and s["settings"]["limits"]["port"] == {"core": 3, "satB": 3} and s["settings"]["sz1Rv2"] is True
          and s["watchSortMode"] == {"core": "date", "satB": "date"}, json.dumps(s, ensure_ascii=False)[:500])
    check(f"{tag} Strip: ไม้ satA หาย · ไม้ core/satB อยู่ครบตามลำดับ", [t["id"] for t in s["trades"]] == ["mc1", "mc2", "mb1"], json.dumps([t["id"] for t in s["trades"]]))
    check(f"{tag} Reset: trades = [] · ของอื่นเท่ากับ Strip ทุกอย่าง", z["trades"] == [] and canon({k: v for k, v in z.items() if k != "trades"}) == canon({k: v for k, v in s.items() if k != "trades"}))
    check(f"{tag} ไม่แก้ object ต้นฉบับ (JSON ก่อน=หลัง) · ไม่คืน object เดิม", r["untouched"] and not r["same"] and not r["zsame"])
    e = page.evaluate("""()=>{ const o = {}; [null, undefined, {}, [], 'x', 5].forEach((v,i)=>{ try{ o['s'+i] = JSON.stringify(cl2aStripLegacy(v)); o['z'+i] = JSON.stringify(cl2aResetBook(v)); }catch(err){ o['e'+i] = String(err); } }); return o; }""")
    check(f"{tag} null/undefined/{{}}/[]/สตริง/ตัวเลข → {{}} ไม่ throw (ทั้ง Strip และ Reset)", not [k for k in e if k.startswith("e")] and all(v == "{}" for v in e.values()), json.dumps(e))
    only_legacy = page.evaluate("()=>JSON.stringify(cl2aResetBook({weeklyPlan:{}, sbPlan:{}}))")
    check(f"{tag} Reset ของสมุดที่มีแต่ key เก่าล้วน ๆ → {{}}", only_legacy == "{}", only_legacy)
    # สูตรใน tools/cl2a_seed.py ต้องตรงกับฟังก์ชันจริง (กัน seed ของเทสเพี้ยนจากแอป)
    py = cl2a_seed.strip_legacy(old)
    check(f"{tag} tools/cl2a_seed.py strip_legacy() = cl2aStripLegacy() ตัวจริงในแอป (ข้อมูลเก่าครบทุก key)", canon(py) == canon(s), canon(py)[:200] + " || " + canon(s)[:200])
    py2 = cl2a_seed.reset_book(old)
    check(f"{tag} tools/cl2a_seed.py reset_book() = cl2aResetBook() ตัวจริง", canon(py2) == canon(z))


# ═══════════════════════════ B) gate ═══════════════════════════
def gate_tests(pw, w, h, tag):
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, pre_doc(), EXTRA_DOCS, wait="gate")
    try:
        check(f"{tag} seed ก่อนรีเซ็ต (ไม่มี cl2aResetAt) → เห็น #cl2aGate · ไม่เห็น #mainWrap", vis(page, "#cl2aGate") and not vis(page, "#mainWrap"))
        rc = page.evaluate("() => window.__rc")
        check(f"{tag} gate เปิด: ไม่มีการวาดหน้า (render · renderPlanSections · renderWatchlist · renderJournal · renderPortfolioMix · renderFundflow · pbRender · renderSat7d = 0 ครั้ง)",
              all(v == 0 for k, v in rc.items() if k != "renderAcctBar"), json.dumps(rc))
        check(f"{tag} gate เปิด: ไม่มีการเขียน Firestore ก่อนกด (ops ว่าง) · ไม่มีดาวน์โหลด", ops(page) == [] and page.evaluate("() => window.__dl.length") == 0, json.dumps(ops(page)))
        check(f"{tag} gate เปิด: schedulePersist/persistTimer ไม่ทำงาน (แตะ schedulePersist ตรง ๆ แล้วยังไม่มีเขียน)",
              (page.evaluate("() => { schedulePersist(); return [persistTimer, pendingLocalWrite]; }") == [None, False]) and (page.wait_for_timeout(700) is None) and ops(page) == [])
        check(f"{tag} gate เปิด: autoFetchFxOnce/rrgAutoOnce ไม่ทำงาน (fxAutoDone=false · rrgAutoDone=false)", page.evaluate("() => [fxAutoDone, rrgAutoDone]") == [False, False])
        txt = page.inner_text("#cl2aGate")
        check(f"{tag} gate: หัว 'รีเซ็ตข้อมูลก่อนใช้ v1' · ตาราง เก็บ/ล้าง · จำนวนจริงต่อบัญชี (ไม้ 5 ต่อบัญชี · แผนสัปดาห์ 1) · ไอเดีย Sat 3 · Bias สัปดาห์ 2",
              "รีเซ็ตข้อมูลก่อนใช้ v1" in txt and "เก็บ" in txt and "ล้าง" in txt and "ไม้ 5" in txt and "แผนสัปดาห์ 1" in txt and "ไอเดีย Sat 3" in txt and "Bias สัปดาห์ 2" in txt,
              re.sub(r"\s+", " ", txt)[:400])
        check(f"{tag} gate: มีชื่อทั้งสองบัญชี (บัญชีหลัก · Family) ในคอลัมน์ 'ล้าง'", "บัญชีหลัก — ไม้ 5" in txt and "Family — ไม้ 5" in txt, re.sub(r"\s+", " ", txt)[:300])
        check(f"{tag} gate: ปุ่ม 'ดาวน์โหลด backup แล้วรีเซ็ต' disabled ตอนยังไม่พิมพ์ · มีปุ่มรอง 'ออกจากระบบ'",
              page.evaluate("() => document.getElementById('cl2aGo').disabled") is True and page.locator("#cl2aGate button:has-text('ออกจากระบบ')").count() == 1)
        shot(page, f"cl2a-gate-empty-{w}.png")
        type_word(page, "รีเซ็ตผิด")
        d_wrong = page.evaluate("() => document.getElementById('cl2aGo').disabled")
        type_word(page, " " + WORD + " ")
        d_trim = page.evaluate("() => document.getElementById('cl2aGo').disabled")
        type_word(page, "รีเซ็")
        d_part = page.evaluate("() => document.getElementById('cl2aGo').disabled")
        type_word(page, WORD)
        d_ok = page.evaluate("() => document.getElementById('cl2aGo').disabled")
        check(f"{tag} ปุ่ม disabled จนพิมพ์ 'รีเซ็ต' ตรง (ผิด/ไม่ครบ = disabled · ตรง = enabled)", d_wrong is True and d_part is True and d_ok is False and d_trim is False, json.dumps([d_wrong, d_part, d_ok, d_trim]))
        # กดตอนไม่ตรง (เรียก cl2aRun ตรง ๆ) → ไม่เขียนอะไร
        page.evaluate("() => { document.getElementById('cl2aWord').value='ผิด'; cl2aRun(); }"); page.wait_for_timeout(300)
        check(f"{tag} เรียก cl2aRun() ตอนคำยืนยันไม่ตรง → ไม่ดาวน์โหลด · ไม่เขียน · gate ยังอยู่", page.evaluate("() => window.__dl.length") == 0 and ops(page) == [] and vis(page, "#cl2aGate"))
        type_word(page, WORD)
        shot(page, f"cl2a-gate-typed-{w}.png")
        if w <= 700:
            hit = page.evaluate("""() => { const b=document.getElementById('cl2aGo'); b.scrollIntoView({block:'center'}); const r=b.getBoundingClientRect();
                const e=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); const i=document.getElementById('cl2aWord').getBoundingClientRect();
                const ie=document.elementFromPoint(i.left+i.width/2, i.top+i.height/2);
                return {btn: b.contains(e), h:r.height, inp: ie===document.getElementById('cl2aWord'), sw: document.documentElement.scrollWidth, w: innerWidth}; }""")
            check(f"{tag} มือถือ ≤700px: gate มองเห็นและกดได้จริง (hit-test ปุ่ม + ช่องพิมพ์ · ปุ่มสูง ≥ 40px · ไม่ล้นแนวนอน)", hit["btn"] and hit["inp"] and hit["h"] >= 40 and hit["sw"] <= hit["w"] + 1, json.dumps(hit))
        else:
            sw = page.evaluate("() => [document.documentElement.scrollWidth, innerWidth]")
            check(f"{tag} gate: ไม่ล้นแนวนอน", sw[0] <= sw[1] + 1, json.dumps(sw))
        check(f"{tag} gate: console zero error · zero page error", not ce and not pe, "; ".join((ce + pe)[:3]))
    finally:
        browser.close()


def flag_tests(pw, w, h, tag):
    # seed ใหม่ (มีธง) → ไม่มี gate
    browser, context, page, ce, pe, _ = launch(pw, w, h, flagged_doc(), None, wait="app")
    try:
        check(f"{tag} seed ใหม่ (มีธง cl2aResetAt/cl2aSatCleanAt) → ไม่มี gate · เห็นแอป", vis(page, "#mainWrap") and not vis(page, "#cl2aGate") and page.evaluate("() => cl2aGateOn") is False)
        u0 = dump(page).get("users/" + UID) or {}
        check(f"{tag} seed ใหม่: ธงเดิมไม่ถูกแตะ (ค่า cl2aResetAt/cl2aSatCleanAt เท่าที่ seed ไว้) · ไม่มีการดาวน์โหลด backup ตอนเปิด",
              u0.get("cl2aResetAt") == "2026-09-30T00:00:00.000Z" and u0.get("cl2aSatCleanAt") == "2026-09-30T00:00:00.000Z" and page.evaluate("() => window.__dl.length") == 0)
    finally:
        browser.close()
    # ผู้ใช้ใหม่ (ไม่มีเอกสาร) → ไม่มี gate · เขียนครั้งแรกมีธงทั้งสอง
    browser, context, page, ce, pe, _ = launch(pw, w, h, None, None, wait="app")
    try:
        check(f"{tag} ผู้ใช้ใหม่ (ไม่มีเอกสาร) → ไม่มี gate · เห็นแอป", vis(page, "#mainWrap") and not vis(page, "#cl2aGate"))
        page.evaluate("() => { state.settings.fx = 35; schedulePersist(); }"); page.wait_for_timeout(900)
        d = dump(page).get("users/" + UID) or {}
        check(f"{tag} ผู้ใช้ใหม่: เขียนครั้งแรกมีธง cl2aResetAt และ cl2aSatCleanAt ทั้งคู่ (ISO เวลาปัจจุบัน)",
              bool(re.match(r"^\d{4}-\d\d-\d\dT", str(d.get("cl2aResetAt")))) and bool(re.match(r"^\d{4}-\d\d-\d\dT", str(d.get("cl2aSatCleanAt")))), json.dumps({k: d.get(k) for k in ("cl2aResetAt", "cl2aSatCleanAt")}))
        check(f"{tag} ผู้ใช้ใหม่: ไม่มีปุ่ม 'ลบไอเดีย/Bias Sat เดิมที่ค้าง' ในตั้งค่า › บัญชี", page.evaluate("() => { renderAcctMgr(); return !document.getElementById('cl2aCleanBtn'); }"))
        check(f"{tag} ผู้ใช้ใหม่: console zero error", not ce and not pe, "; ".join((ce + pe)[:3]))
    finally:
        browser.close()
    # เอกสารรูปแบบเก่า (แบน ไม่มี _v) → errorScreen · ห้ามเขียน
    flat = {"settings": {"fx": 33, "capital": {"core": 100, "satA": 1, "satB": 1}}, "trades": [trade("x1", "core", "open", "AOT")], "watchlist": []}
    browser, context, page, ce, pe, _ = launch(pw, w, h, flat, None, wait="error")
    try:
        msg = page.inner_text("#errorMsg")
        check(f"{tag} เอกสารรูปแบบเก่า (ไม่ใช่ _v≥2) → #errorScreen 'เอกสารรูปแบบเก่า (ก่อน ก.ย. 2569) — ใช้ไฟล์ backup' · ไม่เห็นแอป/gate",
              "เอกสารรูปแบบเก่า (ก่อน ก.ย. 2569) — ใช้ไฟล์ backup" in msg and not vis(page, "#mainWrap") and not vis(page, "#cl2aGate"), msg)
        page.evaluate("() => { try{ schedulePersist(); }catch(e){} }"); page.wait_for_timeout(700)
        check(f"{tag} เอกสารรูปแบบเก่า: ห้ามเขียนอะไร (ops ว่าง · state=null)", ops(page) == [] and page.evaluate("() => state") is None, json.dumps(ops(page)))
    finally:
        browser.close()


# ═══════════════════════════ C) รีเซ็ต 2 บัญชี ═══════════════════════════
def reset_tests(pw, w, h, tag):
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, pre_doc(), EXTRA_DOCS, wait="gate")
    try:
        before = dump(page)
        run_gate(page)
        d = dump(page)
        u = d["users/" + UID]
        left = {b: dropped_left(u["books"][b]) for b in ("main", "fam")}
        check(f"{tag} รีเซ็ต 2 บัญชี: ทุก books.<id> ใน mock ไม่มี key/ฟิลด์ที่ล้าง (main + fam)", all(not v for v in left.values()), json.dumps(left))
        check(f"{tag} รีเซ็ต: trades = [] ทั้งสองบัญชี", u["books"]["main"]["trades"] == [] and u["books"]["fam"]["trades"] == [], json.dumps({b: len(u["books"][b]["trades"]) for b in u["books"]}))
        keep_ok = True; keep_detail = []
        for b, cap in (("main", (3000000, 31515.15)), ("fam", (2000000, 20000.0))):
            bk = u["books"][b]
            ok = (bk.get("_probeX") == b[0] + "probe" and bk["settings"]["brokers"] == before["users/" + UID]["books"][b]["settings"]["brokers"]
                  and bk["settings"]["capital"] == {"core": cap[0], "satB": cap[1], "option": 1500} and bk["settings"]["fx"] == 33
                  and bk.get("industries") == ["Semis", "Banks"] and bk.get("sat_since") == "2026-01-01" and "reasonTags" in bk and "fundflow" in bk)
            keep_ok = keep_ok and ok
            if not ok: keep_detail.append(b)
        check(f"{tag} รีเซ็ต: ของที่เก็บอยู่ครบ (_probeX · brokers · capital.core/satB/option · fx · industries · sat_since · reasonTags · fundflow)", keep_ok, json.dumps(keep_detail))
        check(f"{tag} รีเซ็ต: accounts[].ports ไม่มี satA (main=core,satB · fam=core)", all("satA" not in a["ports"] for a in u["accounts"]) and [a["ports"] for a in u["accounts"]] == [["core", "satB"], ["core"]], json.dumps([a["ports"] for a in u["accounts"]]))
        check(f"{tag} รีเซ็ต: satIdeas = 0 · satWeek = 0", count_col(d, "satIdeas") == 0 and count_col(d, "satWeek") == 0, json.dumps({c: count_col(d, c) for c in ("satIdeas", "satWeek")}))
        check(f"{tag} รีเซ็ต: satConfig / macroPlaybook / watchlist / research จำนวนเท่าเดิม",
              all(count_col(d, c) == n for c, n in KEEP_COUNTS.items() if c != "research") and len([k for k in d if re.match(r"research/[^/]+$", k)]) == 1
              and all(d[k] == before[k] for k in before if re.match(r"users/%s/(satConfig|macroPlaybook|watchlist)/" % UID, k) or k.startswith("research/")), json.dumps({c: count_col(d, c) for c in KEEP_COUNTS}))
        check(f"{tag} รีเซ็ต: มีธง cl2aResetAt และ cl2aSatCleanAt (ISO) ที่ root", bool(re.match(r"^\d{4}-", str(u.get("cl2aResetAt")))) and bool(re.match(r"^\d{4}-", str(u.get("cl2aSatCleanAt")))))
        dl = page.evaluate("() => window.__dl"); o = ops(page)
        first_user_set = next((x["seq"] for x in o if x["p"] == "users/" + UID and x["m"] == "set"), None)
        first_del = next((x["seq"] for x in o if x["m"] == "delete"), None)
        check(f"{tag} รีเซ็ต: ดาวน์โหลด backup 1 ไฟล์ 'dashboard-backup-before-CL2a-*.json' ก่อนการเขียนครั้งแรก (users/{{uid}}) และก่อนลบใดๆ",
              len(dl) == 1 and dl[0]["name"].startswith("dashboard-backup-before-CL2a-") and dl[0]["name"].endswith(".json") and first_user_set and dl[0]["seq"] < first_user_set and (first_del is None or dl[0]["seq"] < first_del),
              json.dumps({"dl": [(x["name"], x["seq"]) for x in dl], "first_set": first_user_set, "first_del": first_del}))
        bk_obj = json.loads(dl[0]["json"]) if dl else {}
        check(f"{tag} backup ที่ดาวน์โหลด = ข้อมูลเดิมครบ (ไม้ satA ยังอยู่ในไฟล์ · satIdeas 3 · satWeek 2 · ไม่ partial)",
              [t["id"] for t in bk_obj.get("doc", {}).get("books", {}).get("main", {}).get("trades", [])] == ["mc1", "mc2", "mb1", "ma1", "ma2"] and len(bk_obj.get("satIdeas", [])) == 3
              and len(bk_obj.get("satWeek", [])) == 2 and "partial" not in bk_obj.get("_meta", {}), json.dumps(bk_obj.get("_meta", {}), ensure_ascii=False)[:300])
        check(f"{tag} รีเซ็ตเสร็จ: gate ปิด · เห็นแอป · cl2aGateOn=false · syncBadge ไม่ error", vis(page, "#mainWrap") and not vis(page, "#cl2aGate") and page.evaluate("() => cl2aGateOn") is False
              and "error" not in page.evaluate("() => document.getElementById('syncBadge').className"))
        rows = sheet_rows(page)
        check(f"{tag} sheet ผลลัพธ์แยกหมวด: บัญชีหลัก ok · Family ok · satIdeas ลบ 3/3 · satWeek ลบ 2/2",
              "รีเซ็ตแล้ว" in rows.get("acct:main", "") and "รีเซ็ตแล้ว" in rows.get("acct:fam", "") and "ลบ 3/3" in rows.get("satIdeas", "") and "ลบ 2/2" in rows.get("satWeek", "") and page.locator(".cl2a-sheet .bkRsRes.bad").count() == 0,
              json.dumps(rows, ensure_ascii=False))
        shot(page, f"cl2a-result-ok-{w}.png")
        # ในหน่วยความจำ
        mem = page.evaluate("() => ({m:getBook('main').trades.length, f:getBook('fam').trades.length, ports:acctList.map(a=>a.ports), extra:Object.keys(acctExtra).sort()})")
        check(f"{tag} รีเซ็ต: หน่วยความจำตรงกับที่เขียน (trades 0/0 · ports ไม่มี satA · acctExtra มีสองธง)", mem["m"] == 0 and mem["f"] == 0 and all("satA" not in p for p in mem["ports"]) and "cl2aResetAt" in mem["extra"] and "cl2aSatCleanAt" in mem["extra"], json.dumps(mem))
        close_sheet(page)
        # หลังรีเซ็ต: ไม่มีปุ่มลองใหม่ · เปิดทุกแท็บ + ตั้งค่า ไม่มี console error
        page.evaluate("() => { openSystemSettings(); }"); page.wait_for_timeout(200)
        check(f"{tag} หลังรีเซ็ตครบ: ตั้งค่า › บัญชี ไม่มีปุ่ม 'ลบไอเดีย/Bias Sat เดิมที่ค้าง' · ไม่มีปุ่ม Migrate/กู้คืนบัญชีเดิม/ล้างข้อมูลทั้งหมด",
              page.locator("#cl2aCleanBtn").count() == 0 and page.locator("#sysOverlay button:has-text('Migrate')").count() == 0 and page.locator("button:has-text('ล้างข้อมูลทั้งหมด')").count() == 0
              and page.locator("button:has-text('กู้คืนบัญชีจาก backup JSON')").count() == 0)
        page.evaluate("() => document.getElementById('sysOverlay').classList.remove('show')")
        tab_err = None
        for t in ["flow", "mix", "watch", "plan", "journal"]:
            try:
                page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(250)
                if t == "plan":
                    page.evaluate("() => setPlanScope('stock')"); page.wait_for_timeout(200)
                    shot(page, f"cl2a-port-{w}.png")
                    page.evaluate("() => setPlanScope('future')"); page.wait_for_timeout(300)
                    shot(page, f"cl2a-sat-{w}.png")
                    page.evaluate("() => setPlanScope('stock')")
                if t == "journal":
                    shot(page, f"cl2a-journal-{w}.png")
            except Exception as ex:
                tab_err = f"{t}: {ex}"; break
        page.evaluate("() => { openSettings(); }"); page.wait_for_timeout(250)
        st = page.evaluate("() => ({sSatA: !!document.getElementById('sSatA'), sPortSatA: !!document.getElementById('sPortSatA'), sbMgr: !!document.getElementById('sbProdMgr'), lowRisk: !!document.getElementById('sSatBLowRisk'), total: document.getElementById('totalHint').innerText})")
        page.evaluate("() => document.getElementById('setOverlay').classList.remove('show')")
        check(f"{tag} หลังรีเซ็ต: เปิดทุกแท็บ (Flow · Mix · Watch · Plan(หุ้น/Future) · Journal) + ตั้งค่า ไม่ throw · ช่อง sSatA/sPortSatA/สินค้า Sat.B/SatBLowRisk ถูกลบ",
              tab_err is None and not any(st[k] for k in ("sSatA", "sPortSatA", "sbMgr", "lowRisk")), str(tab_err) + json.dumps(st, ensure_ascii=False))
        check(f"{tag} หลังรีเซ็ต: console zero error · zero page error (ทุกแท็บ + ตั้งค่า)", not ce and not pe, "; ".join((ce + pe)[:4]))
        sw = page.evaluate("() => [document.documentElement.scrollWidth, innerWidth]")
        check(f"{tag} หลังรีเซ็ต: ไม่ล้นแนวนอน", sw[0] <= sw[1] + 1, json.dumps(sw))
    finally:
        browser.close()


# ═══════════════════════════ D) backup ล้ม (partial) ═══════════════════════════
def partial_tests(pw, w, h, tag):
    browser, context, page, ce, pe, _ = launch(pw, w, h, pre_doc(), EXTRA_DOCS, wait="gate")
    try:
        page.evaluate("() => window.firebase.__mockDb.__denyPath(['users','testuid','satWeek'])")   # bkFetchCol('satWeek') ล้ม → partial
        page.evaluate("() => { window.__ops.length = 0; }")
        run_gate(page, 1500)
        msg = page.inner_text("#cl2aMsg")
        check(f"{tag} bkBuild ล้ม (partial=satWeek): หยุด · แสดงข้อความบน gate · ไม่มีดาวน์โหลด · ไม่มีอะไรถูกเขียน · gate ยังอยู่",
              "satWeek" in msg and "ยังไม่มีอะไรถูกเขียน" in msg and page.evaluate("() => window.__dl.length") == 0 and ops(page) == [] and vis(page, "#cl2aGate") and not vis(page, "#mainWrap"), msg + json.dumps(ops(page)))
        u = dump(page)["users/" + UID]
        check(f"{tag} bkBuild ล้ม: ข้อมูลบน server ไม่เปลี่ยน (ไม้ satA ยังอยู่ · ไม่มีธง) · ปุ่มกดใหม่ได้", len(u["books"]["main"]["trades"]) == 5 and "cl2aResetAt" not in u and page.evaluate("() => document.getElementById('cl2aGo').disabled") is False)
        # bkBuild ที่ throw
        page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid','satWeek'])")
        page.evaluate("() => { window.__realBuild = window.bkBuild; window.bkBuild = async () => { throw new Error('boom'); }; }")
        run_gate(page, 800)
        msg2 = page.inner_text("#cl2aMsg")
        check(f"{tag} bkBuild throw: หยุด · ข้อความ 'ดาวน์โหลด backup ไม่สำเร็จ' · ยังไม่เขียนอะไร", "boom" in msg2 and ops(page) == [] and vis(page, "#cl2aGate"), msg2)
        # เขียน server ล้ม → คืนค่าในหน่วยความจำ + ลองใหม่ได้
        page.evaluate("() => { window.bkBuild = window.__realBuild; window.firebase.__mockDb.__denyPath(['users','testuid']); }")
        run_gate(page, 2000)
        msg3 = page.inner_text("#cl2aMsg")
        mem = page.evaluate("() => ({n:getBook('main').trades.length, has:('cl2aResetAt' in acctExtra), dirty:dirtyBooks.size, pend:pendingLocalWrite})")
        check(f"{tag} เขียน users/{{uid}} ล้ม: แจ้ง fail + คืนค่าในหน่วยความจำ (ไม้ 5 · ไม่มี cl2aResetAt · ไม่ค้าง dirty/pending) · gate ยังอยู่ · ลองใหม่ได้",
              "ไม่สำเร็จ" in msg3 and mem == {"n": 5, "has": False, "dirty": 0, "pend": False} and vis(page, "#cl2aGate") and page.evaluate("() => document.getElementById('cl2aGo').disabled") is False, msg3 + json.dumps(mem))
        # ลองใหม่ (allow) → สำเร็จ
        page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid'])")
        page.evaluate("() => { window.__dl.length = 0; }")
        run_gate(page, 2500)
        u2 = dump(page)["users/" + UID]
        check(f"{tag} ลองใหม่หลังเขียนล้ม → รีเซ็ตสำเร็จ · backup ใหม่มีไม้เดิมครบ (ไม่ใช่ข้อมูลที่รีเซ็ตแล้วในหน่วยความจำ)",
              "cl2aResetAt" in u2 and u2["books"]["main"]["trades"] == [] and len(page.evaluate("() => window.__dl")) == 1 and
              len(json.loads(page.evaluate("() => window.__dl[0].json"))["doc"]["books"]["main"]["trades"]) == 5, json.dumps(page.evaluate("() => window.__dl.map(x=>x.name)")))
    finally:
        browser.close()


# ═══════════════════════════ E) satWeek ลบไม่ได้ → ปุ่มลองใหม่ ═══════════════════════════
def deny_tests(pw, w, h, tag):
    browser, context, page, ce, pe, _ = launch(pw, w, h, pre_doc(), EXTRA_DOCS, wait="gate")
    try:
        wk_paths = [["users", UID, "satWeek", "2026-W40"], ["users", UID, "satWeek", "2026-W39"]]
        page.evaluate("(ps)=>ps.forEach(p=>window.firebase.__mockDb.__denyPath(p))", wk_paths)
        run_gate(page)
        d = dump(page); u = d["users/" + UID]
        rows = sheet_rows(page)
        sheet_txt = page.inner_text(".cl2a-sheet") if page.locator(".cl2a-sheet").count() else ""
        check(f"{tag} satWeek ลบไม่ได้: บัญชีรีเซ็ตแล้ว · satIdeas ลบครบ · satWeek fail (ค้าง 2) · มี cl2aResetAt ไม่มี cl2aSatCleanAt",
              u["books"]["main"]["trades"] == [] and u["books"]["fam"]["trades"] == [] and count_col(d, "satIdeas") == 0 and count_col(d, "satWeek") == 2
              and "cl2aResetAt" in u and "cl2aSatCleanAt" not in u, json.dumps({"satIdeas": count_col(d, "satIdeas"), "satWeek": count_col(d, "satWeek"), "flags": [k for k in u if k.startswith("cl2a")]}))
        check(f"{tag} sheet: satWeek ล้มเหลวแสดงชัด (ลบ 0/2 · permission-denied) · บอก 'ข้อมูลหลักรีเซ็ตแล้ว' + วิธีแก้ (เปิด delete ใน Firestore rules · ปุ่มในตั้งค่า › บัญชี) · satIdeas ok",
              "ลบ 0/2" in rows.get("satWeek", "") and "ล้มเหลว" in rows.get("satWeek", "") and "ลบ 3/3" in rows.get("satIdeas", "") and "ข้อมูลหลักรีเซ็ตแล้ว" in sheet_txt and "permission-denied" in sheet_txt
              and "เปิด delete ใน Firestore rules" in sheet_txt and "ตั้งค่า › บัญชี" in sheet_txt and page.locator(".cl2a-sheet .bkRsRes.bad").count() == 1, json.dumps(rows, ensure_ascii=False) + sheet_txt[:300])
        shot(page, f"cl2a-result-satweek-fail-{w}.png")
        close_sheet(page)
        check(f"{tag} satWeek ลบไม่ได้: แอปเปิดใช้งานได้ปกติ (หลักรีเซ็ตแล้ว · gate ปิด)", vis(page, "#mainWrap") and not vis(page, "#cl2aGate"))
        page.evaluate("() => { openSystemSettings(); }"); page.wait_for_timeout(250)
        check(f"{tag} ตั้งค่า › บัญชี มีปุ่ม 'ลบไอเดีย/Bias Sat เดิมที่ค้าง' (มี cl2aResetAt · ไม่มี cl2aSatCleanAt)", page.locator("#cl2aCleanBtn").count() == 1 and vis(page, "#cl2aCleanBtn"))
        shot(page, f"cl2a-settings-retry-{w}.png", "#sysOverlay .modal")
        # ยังล้ม → ปุ่มยังอยู่
        page.click("#cl2aCleanBtn"); page.wait_for_timeout(1200)
        check(f"{tag} กดปุ่มตอนยัง deny → ยังล้ม: sheet แจ้ง satWeek fail อีกครั้ง · ปุ่มยังอยู่ · ไม่มี cl2aSatCleanAt",
              "ลบ 0/2" in sheet_rows(page).get("satWeek", "") and "cl2aSatCleanAt" not in dump(page)["users/" + UID] and page.locator("#cl2aCleanBtn").count() == 1)
        close_sheet(page)
        # เปิดสิทธิ์ แล้วกด
        page.evaluate("(ps)=>ps.forEach(p=>window.firebase.__mockDb.__allowPath(p))", wk_paths)
        page.evaluate("() => { window.__ops.length = 0; }")
        page.click("#cl2aCleanBtn"); page.wait_for_timeout(1500)
        d2 = dump(page); u2 = d2["users/" + UID]
        rows2 = sheet_rows(page)
        check(f"{tag} __allowPath แล้วกดปุ่ม → satWeek ลบครบ · มีธง cl2aSatCleanAt · ปุ่มหาย · sheet ok (ลบ 2/2 · satIdeas 0/0)",
              count_col(d2, "satWeek") == 0 and "cl2aSatCleanAt" in u2 and page.locator("#cl2aCleanBtn").count() == 0 and "ลบ 2/2" in rows2.get("satWeek", "") and "ลบ 0/0" in rows2.get("satIdeas", "") and page.locator(".cl2a-sheet .bkRsRes.bad").count() == 0,
              json.dumps(rows2, ensure_ascii=False))
        check(f"{tag} กดปุ่มลองใหม่: ไม่แตะสมุดบัญชี (ไม่มีการเขียน books ใหม่ นอกจากธงสถานะ) · ไม้ยังว่าง", u2["books"]["main"]["trades"] == [] and len([o for o in ops(page) if o["m"] == "delete"]) == 2)
        check(f"{tag} deny/retry: console zero error · zero page error", not [c for c in ce if "permission" not in c.lower()] and not pe, "; ".join((ce + pe)[:3]))
    finally:
        browser.close()


# ═══════════════════════════ F) กู้ backup เก่า ═══════════════════════════
def restore_tests(pw, w, h, tag):
    browser, context, page, ce, pe, _ = launch(pw, w, h, flagged_doc(), None, wait="app")
    try:
        main_b, fam_b = old_book("m", 3000000, 31515.15), old_book("f", 2000000, 20000.0)
        accts = [{"id": "main", "name": "บัญชีหลัก", "ports": ["core", "satA", "satB"]}, {"id": "fam", "name": "Family", "ports": ["core", "satA"]}]
        FILE = {"_meta": {"app": "trading-dashboard", "schema": 3, "exportedAt": "2026-09-01T00:00:00.000Z", "uid": UID, "accounts": accts, "activeAccount": "main", "counts": {}},
                "doc": {"_v": 2, "accounts": accts, "activeAccount": "main", "books": {"main": main_b, "fam": fam_b}}, "state": main_b}
        page.evaluate("async ([t,n]) => await bkRestoreLoad(t, n)", [json.dumps(FILE), "old.json"]); page.wait_for_timeout(250)
        hint = page.evaluate("() => { const e=document.querySelector('.bk-sheet [data-cl2a-legacy-note]'); return e ? e.innerText : null; }")
        check(f"{tag} หน้ากู้คืน: มีบรรทัด 'ไฟล์ก่อน 30 ก.ย. 2569: ไม้ Sat.A และแผน/ไอเดียเดิมจะไม่ถูกกู้'", hint == "ไฟล์ก่อน 30 ก.ย. 2569: ไม้ Sat.A และแผน/ไอเดียเดิมจะไม่ถูกกู้", str(hint))
        page.evaluate("() => { document.querySelector('.bk-sheet input[data-bk=\"acct:main\"]').checked = true; document.querySelector('.bk-sheet input[data-bk=\"acct:fam\"]').checked = true; }")
        page.fill("#bkRsConfirm", RS_WORD); page.click("#bkRsGo"); page.wait_for_timeout(1500)
        u = dump(page)["users/" + UID]
        m, f = u["books"]["main"], u["books"]["fam"]
        check(f"{tag} กู้ backup เก่า (จาก seed ก่อนรีเซ็ต): ไม้ core/satB กลับมา (main: c1 c2 b1 · fam: c1 c2 b1) · ไม้ satA ไม่กลับมา",
              [t["id"] for t in m["trades"]] == ["mc1", "mc2", "mb1"] and [t["id"] for t in f["trades"]] == ["fc1", "fc2", "fb1"], json.dumps([[t["id"] for t in m["trades"]], [t["id"] for t in f["trades"]]]))
        check(f"{tag} กู้ backup เก่า: weeklyPlan / sbPlan / sbProducts / watchlist / ไอเดียเดิมไม่กลับมา · ฟิลด์ Sat.A ไม่กลับ · _probeX/brokers กลับ",
              not dropped_left({k: v for k, v in m.items() if k not in ("ideas", "checklistDrafts", "failLog") or v}) and m.get("_probeX") == "mprobe" and m["settings"]["brokers"] == main_b["settings"]["brokers"]
              and "weeklyPlan" not in m and "sbPlan" not in m and "watchlist" not in m, json.dumps(dropped_left(m)))
        check(f"{tag} กู้ backup เก่า: ไม่มี console error", not ce and not pe, "; ".join((ce + pe)[:3]))
        page.evaluate("() => { bkRsClose(); }")
    finally:
        browser.close()


# ═══════════════════════════ G) grep ในโค้ด ═══════════════════════════
def grep_tests():
    html = open(INDEX, encoding="utf-8").read()
    for k in ["SAT_V3_ON", "SAT7D_ON", "SAT_VIEW_ON", "wpBulletsLeft", "sbPlanOf", "renderSBPlan", "szSatBCalc", "phase7m", "__legacyWatchlist", "wlHasWrapper", "resetAll", "ensureSatACap25", "satA:{name"]:
        check(f"grep index.html: ไม่พบ '{k}'", html.count(k) == 0, str(html.count(k)))
    for k in ["wpWeekKey", "wpWeekRangeText", "wpOpenedKey", "makeTradeObject", "closePosOverlay", "Calc.newCount"]:
        check(f"grep index.html: ยังพบ '{k}'", html.count(k) > 0)


def main():
    with sync_playwright() as pw:
        for (w, h, lab) in ((1440, 900, "1440px"), (430, 932, "430px")):
            tag = f"[{ENGINE}/{lab}]"
            browser, context, page, ce, pe, _ = launch(pw, w, h, flagged_doc(), None, wait="app")
            try:
                pure_tests(page, tag)
            finally:
                browser.close()
            gate_tests(pw, w, h, tag)
            flag_tests(pw, w, h, tag)
            reset_tests(pw, w, h, tag)
            partial_tests(pw, w, h, tag)
            deny_tests(pw, w, h, tag)
            restore_tests(pw, w, h, tag)
        grep_tests()
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 19 / CL2-a) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:400])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
