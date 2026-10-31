#!/usr/bin/env python3
"""TD1 — แท็บ "วันนี้" (Daily routine + รายการต้องทำ) · เทส 38
mock Firestore · Chromium 1440 + 430 · นาฬิกาปลอม = 2026-10-02 13:20 ไทย (ศุกร์ · สัปดาห์เริ่ม 2026-09-27) · timezone Asia/Bangkok
seed ตาม docs/briefs/TD1-brief.md · ภาพเก็บที่ tests/screenshots/td1-*.png (full · routine · empty · settings · weekend × 1440/430)
รัน: python3 run_tests_phase38.py"""
import copy, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22
import run_tests_phase24 as p24
import run_tests_phase26 as p26
from ff_stub import FF_STUB

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
ENGINE = base.BROWSER_ENGINE
BASE_CARD = json.load(open(os.path.join(HERE, "..", "avgo-research-card-th.json"), encoding="utf-8"))   # WL2: เหลือไว้ให้เทสเก่าที่อ้างไฟล์ (ไม่ใช้สร้าง research_card แล้ว)
TH_FX = json.load(open(os.path.join(HERE, "fixtures", "avgo_thesis.json"), encoding="utf-8"))
SRC = "https://www.sec.gov/Archives/edgar/data/1/x.htm"
results = []
TODAY, WK = "2026-10-02", "2026-09-27"
FRI = "2026-10-02T06:20:00Z"      # 13:20 เวลาไทย
SAT = "2026-10-03T06:20:00Z"
T = p22.T


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    page.wait_for_timeout(450)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=True)
    except Exception as e: print("shot fail", name, e)


CLOCK_JS = """(iso) => { const R = Date, base = R.parse(iso), start = R.now();
  class FD extends R { constructor(...a){ if(a.length===0) super(base + (R.now()-start)); else super(...a); } static now(){ return base + (R.now()-start); } }
  window.Date = FD; }"""


def ds0(tank, **kw):
    d = {"peak": tank, "baseAt": "2026-09-01", "tank": tank, "stage": "normal", "stageSince": "2026-09-01", "pauseUntil": None, "review": None,
         "recoverDd0": None, "weekly": {}, "rebasedAt": None}
    d.update(kw); return d


def th(tk, tws=(), cats=(), date="2026-09-28"):
    """WL2 — Thesis (living-thesis@1) ของ tk แทน research_card เดิม · tws = [(signal, level)] · cats = [(event, date, date_status)]"""
    c = copy.deepcopy(TH_FX); c["sym"] = tk; c["date"] = date
    c["catalysts"] = [{"event": e, "date": d, "date_status": st, "thesis": 1} for (e, d, st) in cats]
    c["tripwires"] = [{"thesis": 1, "area": "demand", "signal": t, "now": "-", "level": lv} for (t, lv) in tws]
    return c


def wl_th(tk, t=None, **kw):
    """doc watchlist/{tk} (+ thesis ถ้าให้) — thesis ไม่มี log · log อยู่ที่ thesis_log"""
    d = {"ticker": tk, "market": "US", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"}
    if t is not None:
        d["thesis"] = {k: v for k, v in t.items() if k != "log"}; d["thesis_log"] = t.get("log", []); d["thesis_history"] = []; d["thesis_hits"] = {}
    d.update(kw); return d


ROUTINE_LOG = {"2026-06-01": {"slots": ["planTH"], "sat": []}, "2026-09-30": {"slots": ["planTH", "selUS1"], "sat": ["XAUUSD"]}, TODAY: {"slots": ["planTH"], "sat": []}}


def doc38(clean=False, log=None):
    doc = p26.doc26(core=7000000)
    for acct in ("main", "fam"):
        b = doc["books"][acct]; s = b["settings"]
        s["fx"] = 40; s["capital"]["core"] = 7000000; s["capital"]["satB"] = 26000
        s.setdefault("coreRisk", {})["maxLots"] = 6; s["coreRisk"].update({"riskPct": 1, "tierA": 10, "tierB": 5})   # CZ1: ค่าเริ่มต้นใหม่ (1.25/15/10) → seed ค่าเดิม ให้ตัวเลขที่คาดเท่าเดิม
        s["satRisk"] = {"rpt": 1.25, "rptHi": 2, "newMax": 2}
        s["ddState"] = {"core": ds0(7000000), "sat": ds0(26000)}
        b["trades"] = []
    for acct in ("main", "fam"):   # WA1fix — ไม่มีโหมด legacy: เลือก 3 Asset ให้ทุกสัปดาห์ที่ชุดเทสใช้ (Brent = ตัวที่ 4 เทสที่ต้องใช้เลือกเอง)
        doc["books"][acct]["settings"]["satWeekPick"] = {w: ["XAUUSD", "BTCUSD", "S50"] for w in ("2026-09-20", "2026-09-27", "2026-10-04", "2026-10-11")}
    doc["books"]["main"]["settings"]["coreRisk"]["market"] = "US"
    doc["books"]["fam"]["settings"]["coreRisk"]["market"] = "TH"
    if not clean:
        doc["books"]["main"]["settings"]["ddState"]["sat"] = ds0(26000, stage="pause", stageSince="2026-09-20", pauseUntil="2026-09-27")
        doc["books"]["main"]["trades"] = [
            T("tbbb", "core", "open", sym="BBB", entry=100, sl=75, qty=100, cur="USD", date="2026-09-10", openedAt="2026-09-10"),
            T("tmsft", "core", "open", sym="MSFT", entry=400, sl=380, qty=10, cur="USD", date="2026-09-10", openedAt="2026-09-10"),
            T("tnvw", "core", "open", sym="NVW", entry=100, sl=105, qty=100, cur="USD", date="2026-09-10", openedAt="2026-09-10")]
        doc["books"]["fam"]["trades"] = [T("taaa", "core", "open", sym="AAA.BK", entry=100, sl=90, qty=1000, cur="THB", date="2026-09-10", openedAt="2026-09-10")]
    doc["books"]["main"]["settings"]["routineLog"] = copy.deepcopy(log if log is not None else ROUTINE_LOG)
    return doc


def cards38():
    oc = p24.open_card
    return {"cbbb": oc("cbbb", "tbbb", ticker="BBB", acct="main", qty=100, entry=100, sl=75, px=72.5, pxDate="2026-09-25", emaW=70, tier="A"),
            "cmsft": oc("cmsft", "tmsft", ticker="MSFT", acct="main", qty=10, entry=400, sl=380, px=410, pxDate="2026-09-23", emaW=390, tier="A"),
            "cnvw": oc("cnvw", "tnvw", ticker="NVW", acct="main", qty=100, entry=100, sl=105, px=120, pxDate="2026-09-25", emaW=100, tier="A"),
            "caaa": oc("caaa", "taaa", ticker="AAA.BK", acct="fam", qty=1000, entry=100, sl=90, px=110, pxDate="2026-09-23", emaW=100, tier="A")}


IDEA = {"v3": True, "asset": "XAUUSD", "bias": "Long", "created_at": "2026-09-30T00:00:00Z", "entry": 2410, "sl": 2390, "tp": 2450, "cancel_level": None,
        "conditions": [], "planned": False, "setups": [], "status": "active", "accts": {"main": {"skip": True}}, "week": WK}


def seed_all(page, clean=False):
    ev = lambda p, a: page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [p, a])
    if clean:
        ev(["users", "testuid", "satWeek", WK], {k: {"bias": "Long", "flips": 0} for k in ("XAUUSD", "BTCUSD", "S50", "BRENT")})
        return
    ev(["users", "testuid", "satWeek", WK], {"XAUUSD": {"bias": "Long", "flips": 0}})
    ev(["users", "testuid", "satIdeas", "iX"], IDEA)
    for tk, d in (("AVGO", {"ticker": "AVGO", "name": "Broadcom"}), ("NVDA", {"ticker": "NVDA", "name": "Nvidia"}), ("MSFT", {"ticker": "MSFT", "name": "Microsoft"})):
        ev(["research", tk], d)
    ths = {"AVGO": th("AVGO", [("ลูกค้า 5 รายใหญ่ > 55%", "broken")]),
           "NVDA": th("NVDA", [("ชิป AI Q4 ต่ำกว่าเป้า", "review")]),
           "MSFT": th("MSFT", [("Azure โตช้าลง", "watch")], [("งบ Q1 FY27", "2026-10-07", "estimated"), ("อีเวนต์ไกลเกิน", "2026-10-12", "confirmed")])}
    for tk in ("AVGO", "NVDA", "MSFT"):   # WL2: Thesis อยู่ที่ watchlist/{T} (เดิม research_card อยู่ที่ research/{T})
        ev(["users", "testuid", "watchlist", tk], wl_th(tk, ths[tk]))


def launch(pw, w, h, doc=None, cards=None, iso=FRI, clean=False, ff=True):
    lk = {"headless": True}
    if base.CHROMIUM_PATH: lk["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    context = browser.new_context(viewport={"width": w, "height": h}, timezone_id="Asia/Bangkok")
    context.add_init_script(FF_STUB)
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
    page.evaluate("(d)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], d); }", doc if doc is not None else doc38())
    for cid, c in ((cards if cards is not None else ({} if clean else cards38())).items()):
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    seed_all(page, clean)
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(1200)
    if ff:
        p24.set_ff(page, {"as_of": "2026-10-02", "ratios": {"ACWI_BIL": {"up": False}, "HYG_IEI": {"up": True}}})
    page.evaluate("()=>{ if(window.rsLoad) return rsLoad(true); }"); page.wait_for_timeout(600)
    page.evaluate("()=>render()"); page.wait_for_timeout(300)
    if __name__ == "__main__":   # PF2 — pick (XAU · BTC · S50) มีแผนใช้งานแล้ว = state C
        from pf2_retire import seed_plans; seed_plans(page, ["XAUUSD", "BTCUSD", "S50"])
    return browser, context, page, ce, pe, dialogs


def js(page, code, arg=None): return page.evaluate(code, arg) if arg is not None else page.evaluate(code)
def dump(page): return page.evaluate("()=>window.firebase.__mockDb.__dump()")
def settings_db(page, acct="main"): return dump(page)["users/testuid"]["books"][acct]["settings"]
def kinds(page, grp): return page.evaluate("(g)=>[...document.querySelectorAll('[data-td-grp=\"'+g+'\"] .tdRow')].map(e=>e.dataset.kind)", grp)
def rows_text(page, grp): return page.evaluate("(g)=>[...document.querySelectorAll('[data-td-grp=\"'+g+'\"] .tdRow')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())", grp)
def row(page, kind, i=0): return page.locator(f'.tdRow[data-kind="{kind}"]').nth(i)
def row_txt(page, kind, i=0): return row(page, kind, i).text_content().replace("\n", " ")
def go_today(page): js(page, "()=>switchTab('today')"); page.wait_for_timeout(250)


def overflow_x(page, sels):
    return page.evaluate("""(sels)=>{ const W = window.innerWidth, bad = [];
      sels.forEach(s=>document.querySelectorAll(s).forEach(e=>{ const r = e.getBoundingClientRect(); if(r.width && (r.right > W + 1 || r.left < -1 || e.scrollWidth > e.clientWidth + 1)) bad.push(s+':'+Math.round(r.left)+'-'+Math.round(r.right)+'/'+e.scrollWidth+'>'+e.clientWidth); }));
      if(document.documentElement.scrollWidth > W + 1) bad.push('page:'+document.documentElement.scrollWidth+'>'+W); return bad.slice(0, 8); }""", sels)


def in_view(page, sel):
    return page.evaluate("""(s)=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return r.top >= -1 && r.bottom <= innerHeight + 1 && r.height > 0; }""", sel)


# ───────────────────────── 1–3 แท็บ · เลขแดง · หัว ─────────────────────────
def tab_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        info = js(page, """()=>({active: activeTab, today: getComputedStyle(document.getElementById('tabToday')).display, flow: getComputedStyle(document.getElementById('tabFlow')).display,
            first: document.querySelector('#tabsMain .tabbtn').id, btns: [...document.querySelectorAll('#tabsMain .tabbtn')].map(b=>b.id),
            on: [...document.querySelectorAll('#tabsMain .tabbtn.on')].map(b=>b.id), order: TAB_ORDER, vis: visibleTabs(), label: document.getElementById('tabBtnToday').textContent.trim().replace(/\\s+/g,' ')})""")
        check(f"{tag} 1 เปิดแอป = แท็บ วันนี้ (activeTab · #tabToday แสดง · #tabFlow ซ่อน)", info["active"] == "today" and info["today"] != "none" and info["flow"] == "none", json.dumps(info))
        check(f"{tag} 1 ปุ่ม วันนี้ อยู่ซ้ายสุด · ติดสถานะ on · TAB_ORDER = today,flow,watch,plan,journal,mix (ป้าย Today)", info["first"] == "tabBtnToday" and info["on"] == ["tabBtnToday"]
              and info["order"] == ["today", "flow", "watch", "plan", "journal", "mix"] and len(info["btns"]) == 6, json.dumps(info))
        check(f"{tag} 1 visibleTabs() รวมแท็บนี้ (ปัดซ้าย/ขวาวน)", info["vis"] == ["today", "flow", "watch", "plan", "journal", "mix"], json.dumps(info["vis"]))
        js(page, "()=>switchTab('plan')"); page.wait_for_timeout(200)
        res = []
        for k, t in (("1", "today"), ("2", "flow"), ("3", "watch"), ("4", "plan"), ("5", "journal"), ("6", "mix")):
            page.keyboard.press(k); page.wait_for_timeout(200); res.append(js(page, "()=>activeTab") == t)
        check(f"{tag} 1 คีย์ตามตำแหน่ง 1 Today · 2 Flow · 3 Watch · 4 แผน · 5 Journal · 6 Port", all(res), json.dumps(res))
        page.keyboard.press("0"); page.wait_for_timeout(200)
        check(f"{tag} 1 เลิกใช้คีย์ 0 (กดแล้วแท็บไม่เปลี่ยน)", js(page, "()=>activeTab") == "mix")
        hints = js(page, "()=>[...document.querySelectorAll('#tabsMain .tabbtn')].map(b=>b.id.replace('tabBtn','')+':'+b.querySelector('.kbdhint').textContent)")
        check(f"{tag} 1 .kbdhint เลขใหม่ตามตำแหน่ง · ชื่อปุ่ม 'Today'", hints == ["Today:1", "Flow:2", "Watch:3", "Journal".replace("Journal","Plan")+":4", "Journal:5", "Mix:6"] and js(page, "()=>document.getElementById('tabBtnToday').firstChild.textContent") == "Today", json.dumps(hints))
        js(page, "()=>{ switchTab('flow'); window.__rt = 0; const o = window.renderToday; window.renderToday = ()=>{ window.__rt++; return o(); }; switchTab('today'); }")
        check(f"{tag} 1 switchTab('today') เรียก renderToday()", js(page, "()=>window.__rt") == 1)
        # วนปัดซ้าย/ขวา: จาก journal ไป today ผ่าน visibleTabs
        nxt = js(page, "()=>{ const o = visibleTabs(); return [o[0], o[o.length-1]]; }")
        check(f"{tag} 1 แท็บแรกของการปัด = today", nxt[0] == "today" and nxt[1] == "mix", json.dumps(nxt))
        # ── 2 เลขแดง ──
        go_today(page)
        bd = js(page, "()=>{ const b = document.getElementById('tabBadgeToday'); return {t: b.textContent, shown: getComputedStyle(b).display !== 'none'}; }")
        check(f"{tag} 2 เลขแดงบนปุ่มแท็บ = จำนวน 🔴 (3)", bd == {"t": "3", "shown": True}, json.dumps(bd))
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(300)
        bd2 = js(page, "()=>{ const b = document.getElementById('tabBadgeToday'); const r = b.getBoundingClientRect(); return {t: b.textContent, shown: getComputedStyle(b).display !== 'none', vis: r.width > 0}; }")
        check(f"{tag} 2 อยู่แท็บอื่นยังเห็นเลขแดง", bd2["t"] == "3" and bd2["shown"] and bd2["vis"], json.dumps(bd2))
        # ── 3 หัว ──
        go_today(page)
        hd = js(page, """()=>({r: (document.querySelector('[data-td-cnt="r"]')||{}).textContent, a: (document.querySelector('[data-td-cnt="a"]')||{}).textContent, b: (document.querySelector('[data-td-cnt="b"]')||{}).textContent,
            na: document.querySelectorAll('[data-td-grp="a"] .tdRow').length, nb: document.querySelectorAll('[data-td-grp="b"] .tdRow').length, nr: document.querySelectorAll('[data-td-grp="r"] .tdRow').length,
            when: (document.querySelector('[data-td-when]')||{}).textContent})""")
        check(f"{tag} 3 ชิปหัว: '3 ด่วน' · ภายในสัปดาห์/โอกาสตรงกับจำนวนแถว", hd["r"] == "3 ด่วน" and hd["nr"] == 3 and hd["a"] == f"{hd['na']} ภายในสัปดาห์" and hd["b"] == f"{hd['nb']} โอกาส" and hd["na"] == 6 and hd["nb"] == 2, json.dumps(hd, ensure_ascii=False))
        check(f"{tag} 3 ขวาหัว = 'ศุกร์ 2 ต.ค. · ปิดสัปดาห์ 25 ก.ย.'", hd["when"] == "ศุกร์ 2 ต.ค. · ปิดสัปดาห์ 25 ก.ย.", hd["when"])
        check(f"{tag} 1-3 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── 4–8 รายการงาน · ลิงก์ ─────────────────────────
def task_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        kr = kinds(page, "r"); tr = rows_text(page, "r")
        check(f"{tag} 4 🔴 ครบ 3 แถวตามลำดับ ขายหมด → Tripwire ยืนยัน → DD", kr == ["sell", "tw-confirmed", "dd-review"], json.dumps(kr))
        check(f"{tag} 4 แถว BBB: 'BBB ปิดสัปดาห์ใต้ Stop 75 → ขายหมด' · รอง 'Core · บัญชีหลัก · ปิด 72.5' · ป้าย Plan US", "BBB ปิดสัปดาห์ใต้ Stop 75 → ขายหมด" in tr[0] and "Core · บัญชีหลัก · ปิด 72.5" in tr[0] and "Plan US" in tr[0], tr[0])
        check(f"{tag} 4 แถว AVGO: Tripwire ยืนยันแล้ว \"ลูกค้า 5 รายใหญ่ > 55%\" → ทบทวนการถือ · ป้าย Selection US", 'AVGO Tripwire พัง "ลูกค้า 5 รายใหญ่ > 55%" → ทบทวนการถือ' in tr[1] and "Selection US" in tr[1], tr[1])
        check(f"{tag} 4 แถว DD: 'เบรก DD Sat Main: รอเขียนทบทวน' (TD2) · รอง 'Main · DD' · ป้าย Plan US", "เบรก DD Sat Main: รอเขียนทบทวน" in tr[2] and "Main · DD" in tr[2] and "Plan US" in tr[2], tr[2])
        ka = kinds(page, "a"); ta = rows_text(page, "a")
        check(f"{tag} 5 🟡 ลำดับ: เช็กแผน Sat · ราคาเก่า×2 · NVDA ตรวจ · งบ MSFT (PF1: ไม่มีงาน Bias)", ka == ["sat-daily", "homework", "stale", "stale", "tw-review", "catalyst"], json.dumps(ka))
        check(f"{tag} 5 เช็กแผน Sat: ช่อง XAU · BTC · S50 ตามที่เลือกสัปดาห์นี้ (WA1fix: เพดาน 3 · Brent ไม่ได้เลือก = ไม่ขึ้น · TD2 ชื่อแสดง · log วันนี้ว่าง)", js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=\"sat-daily\"] .tdAs .nm')].map(e=>e.textContent)") == ["XAU", "BTC", "S50"])
        check(f"{tag} 5 เช็กแผน Sat: ป้ายช่วง Plan TH (S50) + Plan US (อีก 3)", "Plan TH" in ta[0] and "Plan US" in ta[0], ta[0])
        check(f"{tag} 5 ราคาเก่าแยกบัญชี: main = MSFT · Family = AAA.BK", "ราคาปิดเก่าเกิน 7 วัน 1 ตัว — MSFT" in ta[2] and "Main" in ta[2] and "Plan US" in ta[2]
              and "ราคาปิดเก่าเกิน 7 วัน 1 ตัว — AAA.BK" in ta[3] and "Family" in ta[3] and "Plan TH" in ta[3], json.dumps(ta[2:4], ensure_ascii=False))
        check(f"{tag} 5 PF3 ไม่มีข้อความ 'Bias ยังไม่ประเมิน: BTC · S50' ใน 🟡 (งาน Bias ถอด · งานอื่นยังครบตามลำดับ)", "Bias ยังไม่ประเมิน: BTC · S50" not in " ".join(ta) and ka == ["sat-daily", "homework", "stale", "stale", "tw-review", "catalyst"], json.dumps(ta, ensure_ascii=False)[:300])
        check(f"{tag} 5 PF1 — ไม่มีงาน Bias ยังไม่ประเมิน ในรายการ 🟡", not any("Bias ยังไม่ประเมิน" in x for x in ta), json.dumps(ta, ensure_ascii=False)[:300])
        check(f"{tag} 5 NVDA: 'Tripwire ถึงระดับทบทวน' (WL2 · level review แทน tw-check เดิม)", 'NVDA Tripwire ถึงระดับทบทวน "ชิป AI Q4 ต่ำกว่าเป้า"' in ta[4], ta[4])
        check(f"{tag} 5 MSFT งบ: '~' + อีก 5 วัน + catalyst +10 วันไม่ขึ้น", "MSFT" in ta[5] and "งบ Q1 FY27" in ta[5] and "~7 ต.ค." in ta[5] and "อีก 5 วัน" in ta[5] and "อีเวนต์ไกลเกิน" not in " ".join(ta), ta[5])
        kb = kinds(page, "b"); tb = rows_text(page, "b")
        check(f"{tag} 6 🔵 ลำดับ: แผน Sat พร้อม · Core เติมไม้", kb == ["ready", "core-add"], json.dumps(kb))
        check(f"{tag} 6 XAU Long แผนพร้อมบันทึก 1 บัญชี (Family) (TD2 ชื่อแสดง)", "XAU Long · แผนพร้อมบันทึก 1 บัญชี (Family)" in tb[0] and "Plan US" in tb[0], tb[0])
        check(f"{tag} 6 NVW: Stop ≥ ทุนแล้ว · เติมไม้ได้ #2/6", "NVW Stop ≥ ทุนแล้ว · เติมไม้ได้ #2/6" in tb[1], tb[1])
        # TD2 — แถบชิปสถานะเร็วถูกแทนด้วยตาราง "ดูตัวเลข" (ค่าจากฟังก์ชันเดิม)
        no_pulse = js(page, "()=>!document.querySelector('[data-td-pulse]') && !document.querySelector('.tdPc')")
        page.locator('[data-td-numbtn]').click(); page.wait_for_timeout(200)
        tbl = js(page, "()=>[...document.querySelectorAll('[data-td-nums] tbody tr')].map(r=>({a:r.dataset.numAcct, c:[...r.children].map(c=>c.textContent.trim()), k:[...r.children].map(c=>c.className)}))")
        main_r = next((x for x in tbl if x["a"] == "main"), None); fam_r = next((x for x in tbl if x["a"] == "fam"), None)
        check(f"{tag} 2b แถบสถานะเร็ว: (TD2) ไม่มีแถบชิป · ตารางตัวเลข 2 บัญชี × 5 ค่า (DD Core · DD Sat · heat · ไม้ใหม่ · ชั้น 2)", no_pulse and len(tbl) == 2 and all(len(x["c"]) == 7 for x in tbl), json.dumps(tbl, ensure_ascii=False))   # RG2b §4.7 — DD Winner · DD Ladder แยกคอลัมน์ (7 คอลัมน์)
        check(f"{tag} 2b ช่อง DD Sat บัญชีหลัก = ตัวเลข DD ของ pause และสีแดง (TD2: ตาราง แทนชิป 'พักถึง 27 ก.ย.')", main_r and "r" in main_r["k"][3].split() and main_r["c"][3].endswith("%"), json.dumps(main_r, ensure_ascii=False))
        ev = js(page, "()=>{ const e = ddEval('main','sat'); return Math.round(e.ddPct*100)/100; }")
        check(f"{tag} 2b ค่าในตาราง DD ตรงกับ ddEval (ไม่คิดใหม่)", main_r and main_r["c"][3] == f"{ev:g}%", f"{ev} / {main_r}")
        hv = js(page, "()=>{ const b = sat7dAcctBase('main'); return Math.round(b.heatPct*100)/100 + ' / ' + b.heatMax + '%'; }")
        check(f"{tag} 2b ช่อง heat Sat = sat7dAcctBase", main_r and main_r["c"][4] == hv, f"{hv} / {main_r}")
        gf = js(page, "()=>document.querySelector('[data-td-detfoot]').textContent")
        check(f"{tag} 2b บรรทัดใต้ตาราง = 'fundflow อัปเดต 2 ต.ค.' (RG2b ถอดประตู FF)", "ประตู FF" not in gf and "fundflow อัปเดต 2 ต.ค." in gf, gf)
        okl = js(page, "()=>(document.querySelector('[data-td-okline] .txt .full')||{}).textContent || ''")
        check(f"{tag} 6b บรรทัดเขียว (TD2 แทนกลุ่มปกติ): ไม่มี 'DD' (เบรกทำงานอยู่) · มี heat · fundflow", okl.startswith("✓ อื่น ๆ ปกติ —") and "DD" not in okl and "heat" in okl and "fundflow" in okl and not js(page, "()=>!!document.querySelector('[data-td-grp=g]')"), okl)
        shot(page, f"td1-full-{label.replace('px','')}.png")
        # ── 7 ลิงก์ ──
        row(page, "sell").click(); page.wait_for_timeout(1500)
        st = js(page, "()=>({tab: activeTab, acct: planAcctFilter, open: (document.querySelector('[data-core-card=\"cbbb\"]')||{classList:{contains:()=>false}}).classList.contains('open')})")
        check(f"{tag} 7 กดแถว BBB → แท็บแผน · ชิปบัญชี main · การ์ดขยาย", st["tab"] == "plan" and st["acct"] == "main" and st["open"], json.dumps(st))
        check(f"{tag} 7 การ์ด BBB อยู่ในจอ (getBoundingClientRect ภายใน viewport)", in_view(page, '[data-core-card="cbbb"]'))
        go_today(page)
        row(page, "tw-confirmed").click(); page.wait_for_timeout(500)
        st = js(page, "()=>({tab: activeTab, sel: wlSel, sub: wlSub})")
        check(f"{tag} 7 กดแถว AVGO → แท็บ Watch · แท็บ ออกเมื่อ ของ AVGO (WL2 · เดิม Research)", st == {"tab": "watch", "sel": "AVGO", "sub": "exit"}, json.dumps(st))
        go_today(page)
        row(page, "dd-review").click(); page.wait_for_timeout(400)
        sh = js(page, "()=>({sheet: !!document.querySelector('.core-sheet [data-core-sheet=\"dd\"]'), ta: !!document.getElementById('ddReview'), h: (document.querySelector('.core-sheet h3')||{}).textContent})")
        check(f"{tag} 7 กดแถว DD → sheet DD Sat main เปิดพร้อมช่องเขียนทบทวน", sh["sheet"] and sh["ta"] and "Sat" in sh["h"] and "บัญชีหลัก" in sh["h"], json.dumps(sh, ensure_ascii=False))
        js(page, "()=>coreSheetClose()"); page.wait_for_timeout(200)
        go_today(page)
        row(page, "stale", 0).click(); page.wait_for_timeout(500)
        sh = js(page, "()=>({sheet: !!document.querySelector('.core-sheet [data-core-sheet=\"px\"]'), h: (document.querySelector('.core-sheet h3')||{}).textContent, tab: activeTab})")
        check(f"{tag} 7 กดราคาเก่า (main) → sheet อัปเดตราคาของ MSFT", sh["sheet"] and "MSFT" in sh["h"], json.dumps(sh, ensure_ascii=False))
        js(page, "()=>coreSheetClose()"); page.wait_for_timeout(200)
        go_today(page)
        row(page, "stale", 1).click(); page.wait_for_timeout(500)
        sh = js(page, "()=>({h: (document.querySelector('.core-sheet h3')||{}).textContent, acct: planAcctFilter})")
        check(f"{tag} 7 กดราคาเก่า (Family) → sheet ของ AAA.BK · ชิปบัญชี fam", "AAA.BK" in sh["h"] and sh["acct"] == "fam", json.dumps(sh, ensure_ascii=False))
        js(page, "()=>coreSheetClose()"); page.wait_for_timeout(200)
        # ลิงก์อื่น
        go_today(page); row(page, "tw-review").click(); page.wait_for_timeout(400)
        st = js(page, "()=>({tab: activeTab, sel: wlSel, sub: wlSub})")
        check(f"{tag} 7 กดแถว NVDA ตรวจ → Watch · แท็บ ออกเมื่อ ของ NVDA (WL2 · เดิม Research 'rs')", st == {"tab": "watch", "sel": "NVDA", "sub": "exit"}, json.dumps(st))
        go_today(page); row(page, "catalyst").click(); page.wait_for_timeout(400)
        st = js(page, "()=>({tab: activeTab, sel: wlSel, sub: wlSub})")
        check(f"{tag} 7 กดแถวงบ MSFT → Watch · แท็บ ติดตาม (Catalysts) ของ MSFT (WL2 · เดิม Overview 'ov')", st == {"tab": "watch", "sel": "MSFT", "sub": "trk"}, json.dumps(st))
        check(f"{tag} 7 PF3 ไม่มีแถว Bias ให้กด (งาน Today Bias ถอดแล้ว) · แถวอื่นยังกดได้ (ตามเช็กถัดไป)", js(page, "()=>document.querySelectorAll('.tdRow[data-kind=\"bias\"]').length") == 0)
        go_today(page); row(page, "ready").click(); page.wait_for_timeout(500)
        check(f"{tag} 7 กดแถวแผน Sat พร้อม → แท็บแผน (Future) · การ์ดแผน XAUUSD", js(page, "()=>activeTab+'/'+planScope") == "plan/future" and bool(js(page, "()=>!!document.querySelector('#satV3Panel .ui-plan[data-id=\"iX\"]')")))
        go_today(page); row(page, "core-add").click(); page.wait_for_timeout(1400)
        check(f"{tag} 7 กดแถว NVW เติมไม้ → การ์ด NVW ขยายและอยู่ในจอ", js(page, "()=>activeTab") == "plan" and in_view(page, '[data-core-card="cnvw"]'))
        go_today(page)
        vis = "()=>getComputedStyle(document.querySelector('[data-td-det]')).display!=='none'"
        open0 = js(page, vis)   # ค่าจำสถานะ: ตารางกางค้างจากเคส 2b
        page.locator('[data-td-numbtn]').click(); page.wait_for_timeout(200)
        open1 = js(page, vis)
        page.locator('[data-td-numbtn]').click(); page.wait_for_timeout(150)
        open2 = js(page, vis)
        check(f"{tag} 7 กด 'ดูตัวเลข' → สลับกาง/พับ (TD2: แทนกดชิป DD Sat) · จำสถานะข้ามการเปลี่ยนแท็บ · กดซ้ำ = กลับ", open0 and (not open1) and open2, json.dumps([open0, open1, open2]))
        # ปลายทางหาไม่เจอ = แค่เปลี่ยนแท็บ ไม่ error
        go_today(page)
        js(page, "()=>{ const el = document.createElement('div'); el.dataset.go = 'card'; el.dataset.args = JSON.stringify({tid:'nope', A:'main'}); tdGo(el); }"); page.wait_for_timeout(300)
        check(f"{tag} 7 ปลายทางหาไม่เจอ (การ์ดถูกลบ) = แค่เปลี่ยนแท็บ ไม่ error", js(page, "()=>activeTab") == "plan" and not pe, "; ".join(pe[:2]))
        # ── 8 แก้ BBB ให้ปิด ≥ Stop ──
        go_today(page)
        js(page, "()=>coreWrite('cbbb', {px: 80, pxDate: '2026-09-25'})"); page.wait_for_timeout(700)
        kr = kinds(page, "r")
        bd = js(page, "()=>document.getElementById('tabBadgeToday').textContent")
        check(f"{tag} 8 อัปเดตราคา BBB ≥ Stop → แถว BBB หาย · เลขแดงเหลือ 2", kr == ["tw-confirmed", "dd-review"] and bd == "2", json.dumps([kr, bd]))
        check(f"{tag} 4-8 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── 9–13 Routine ─────────────────────────
def routine_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        st = js(page, "()=>Object.fromEntries([...document.querySelectorAll('.tdSs')].map(e=>[e.dataset.slot, {st: e.dataset.st, g: e.querySelector('.k').textContent.trim(), sub: (e.querySelector('[data-slot-sub]')||{}).textContent}]))")
        check(f"{tag} 9 09:00 ติ๊กแล้ว = ✓ · 11:00 ไม่ติ๊ก = ข้าม –", st["planTH"]["st"] == "done" and st["planTH"]["g"] == "✓" and st["selUS1"]["st"] == "skip" and st["selUS1"]["g"] == "–" and "ข้าม" in st["selUS1"]["sub"], json.dumps(st, ensure_ascii=False))
        check(f"{tag} 9 13:00 = ตอนนี้ ● + 'เหลือ 40 นาที' · 15:30/19:00 = ยังไม่ถึง ○", st["selUS2"]["st"] == "cur" and st["selUS2"]["g"] == "●" and "เหลือ 40 นาที" in st["selUS2"]["sub"]
              and st["planUS"]["st"] == "future" and st["planUS"]["g"] == "○" and st["selTH"]["st"] == "future", json.dumps(st, ensure_ascii=False))
        now_txt = js(page, "()=>document.querySelector('[data-td-now]').textContent")
        check(f"{tag} 9 หัว Routine 'ตอนนี้ 13:20' (เวลาไทย)", "13:20" in now_txt, now_txt)
        n_us = js(page, "()=>{ const e = document.querySelector('[data-slot-n=\"planUS\"]'); return e ? +e.textContent : null; }")
        want = js(page, "()=>tdLast.tasks.filter(t=>(t.tags||[]).includes('planUS')).length")
        rows_us = js(page, "()=>document.querySelectorAll('.tdRow [data-tag=\"planUS\"]').length")
        check(f"{tag} 9 ช่อง Plan US มีเลข = จำนวนงานที่ติดป้าย Plan US ({want})", n_us == want and want == rows_us and want >= 5, f"{n_us} {want} {rows_us}")
        n_th = js(page, "()=>{ const e = document.querySelector('[data-slot-n=\"planTH\"]'); return e ? +e.textContent : null; }")
        check(f"{tag} 9 ช่อง Plan TH มีเลข = งานติดป้าย Plan TH (ราคาเก่า AAA.BK + เช็ก S50 = 2)", n_th == 2, str(n_th))
        n_sel = js(page, "()=>[...document.querySelectorAll('[data-slot-n]')].map(e=>e.dataset.slotN+':'+e.textContent).join(',')")
        check(f"{tag} 9 ช่อง Selection US มีเลข 3 (AVGO ยืนยัน · NVDA ตรวจ · การบ้าน AVGO) ทั้ง #1 และ #2", "selUS1:3" in n_sel and "selUS2:3" in n_sel, n_sel)
        wk = js(page, "()=>document.querySelector('[data-td-week]').textContent")
        check(f"{tag} 9 ใต้ Routine: 'สัปดาห์นี้ทำครบ x/y ช่วง' (นับจาก routineLog จ.–วันนี้)", wk == "สัปดาห์นี้ทำครบ 3/23 ช่วง · การบ้าน 0/5 วัน", wk)   # y = จ.–พฤ. 4 วัน×5 + ช่องของวันนี้ที่เริ่มแล้ว 3 = 23 · x = 09-30 สอง + วันนี้ หนึ่ง = 3
        shot(page, f"td1-routine-{label.replace('px','')}.png")
        # ── 10 ติ๊กช่อง ──
        page.locator('[data-tick-slot="selUS2"]').click(); page.wait_for_timeout(500)
        d1 = js(page, "()=>document.querySelector('.tdSs[data-slot=\"selUS2\"]').dataset.st")
        lg = settings_db(page)["routineLog"][TODAY]["slots"]
        check(f"{tag} 10 กดวงกลม 13:00 → ✓ · routineLog['2026-10-02'].slots มี selUS2 (ใน mock DB)", d1 == "done" and "selUS2" in lg, json.dumps([d1, lg]))
        page.locator('[data-tick-slot="selUS2"]').click(); page.wait_for_timeout(500)
        d2 = js(page, "()=>document.querySelector('.tdSs[data-slot=\"selUS2\"]').dataset.st")
        lg = settings_db(page)["routineLog"][TODAY]["slots"]
        check(f"{tag} 10 กดซ้ำ → เอาออก (กลับเป็น ตอนนี้ ●)", d2 == "cur" and "selUS2" not in lg and "planTH" in lg, json.dumps([d2, lg]))
        if w <= 480:   # TD2 ข้อ 7: มือถือพับช่องที่ผ่านแล้ว — กางก่อนติ๊กย้อน
            page.locator('[data-td-fold]').click(); page.wait_for_timeout(200)
        page.locator('[data-tick-slot="selUS1"]').click(); page.wait_for_timeout(500)
        d3 = js(page, "()=>document.querySelector('.tdSs[data-slot=\"selUS1\"]').dataset.st")
        check(f"{tag} 10 ติ๊กย้อนช่องที่ 'ข้าม' ภายในวันเดียวกัน → ✓", d3 == "done" and "selUS1" in settings_db(page)["routineLog"][TODAY]["slots"], d3)
        page.locator('[data-tick-slot="selUS1"]').click(); page.wait_for_timeout(300)
        page.locator('.tdSs[data-slot="planUS"] .tdGo').click(); page.wait_for_timeout(700)
        st = js(page, "()=>({tab: activeTab, acct: planAcctFilter, scope: planScope})")
        check(f"{tag} 10 กดชื่อช่อง Plan US → แท็บแผน · ชิปบัญชี main (Core US แรก)", st == {"tab": "plan", "acct": "main", "scope": "stock"}, json.dumps(st))
        go_today(page); page.locator('.tdSs[data-slot="planTH"] .tdGo').click(); page.wait_for_timeout(700)
        st = js(page, "()=>({tab: activeTab, acct: planAcctFilter})")
        check(f"{tag} 10 กดชื่อช่อง Plan TH → แท็บแผน · ชิปบัญชี fam (Core TH แรก)", st == {"tab": "plan", "acct": "fam"}, json.dumps(st))
        go_today(page); page.locator('.tdSs[data-slot="selUS1"] .tdGo').click(); page.wait_for_timeout(300)
        check(f"{tag} 10 กดชื่อช่อง Selection US → แท็บ Flow", js(page, "()=>activeTab") == "flow")
        go_today(page); page.locator('.tdSs[data-slot="selTH"] .tdGo').click(); page.wait_for_timeout(300)
        check(f"{tag} 10 กดชื่อช่อง Selection TH → แท็บ Watch (กรองหุ้นไทย)", js(page, "()=>activeTab+'/'+wlPort") == "watch/TH", js(page, "()=>activeTab+'/'+wlPort"))
        go_today(page)
        # ── 11 เช็กแผน Sat ──
        page.locator('[data-sat-ok="XAUUSD"]').click(); page.wait_for_timeout(350)
        page.locator('[data-sat-no="S50"]').click(); page.wait_for_timeout(350)
        check(f"{tag} 11 กด ✓ XAU + ✕ S50 → แถวยังอยู่ · ช่อง ✓ เขียว 1 (TD2-fix: Focus ≤ 2)", kinds(page, "a")[0] == "sat-daily" and js(page, "()=>document.querySelectorAll('.tdRow[data-kind=\"sat-daily\"] .tdAs.ok').length") == 1)
        check(f"{tag} 11 หลังตัดสิน S50 ป้ายแถวเหลือ Plan US อย่างเดียว", "Plan TH" not in row_txt(page, "sat-daily") and "Plan US" in row_txt(page, "sat-daily"), row_txt(page, "sat-daily"))
        page.locator('[data-sat-ok="BTC"]').click(); page.wait_for_timeout(450)
        sat = settings_db(page)["routineLog"][TODAY]["satState"]
        check(f"{tag} 11 ✓ ครบ 2 (XAU · BTC) → แถวเช็กแผน Sat หาย · routineLog.satState (TD2-fix: หายเมื่อ ✓ ครบ 2)", "sat-daily" not in kinds(page, "a") and sat == {"XAUUSD": "ok", "BTC": "ok", "S50": "no"}, json.dumps([kinds(page, 'a'), sat]))
        # ── 12 ตัด log เก่า ──
        lg = settings_db(page)["routineLog"]
        check(f"{tag} 12 routineLog เก่ากว่า 60 วัน (2026-06-01) ถูกตัดตอนเขียน · 2026-09-30 ยังอยู่", "2026-06-01" not in lg and "2026-09-30" in lg, json.dumps(list(lg.keys())))
        # ── 16 ไม่เขียนอื่น ──
        d0 = json.dumps(dump(page), sort_keys=True)
        js(page, "()=>{ renderToday(); render(); switchTab('flow'); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(700)
        d1 = json.dumps(dump(page), sort_keys=True)
        check(f"{tag} 16 แท็บนี้ไม่เขียนอะไร (เทียบ mock DB ก่อน/หลัง render หลายรอบ)", d0 == d1)
        main_keys = sorted(set(settings_db(page).keys()))
        before = json.loads(json.dumps(settings_db(page)))
        # เขียนเฉพาะ routine/routineLog: ติ๊ก → เทียบ settings ที่เหลือเท่าเดิม
        d_before = json.loads(json.dumps(dump(page)))
        page.locator('[data-tick-slot="selUS2"]').click(); page.wait_for_timeout(500)
        d_after = dump(page)
        diffs = []
        for k in set(d_before) | set(d_after):
            if k == "users/testuid":
                for acct in ("main", "fam"):
                    b0, b1 = d_before[k]["books"][acct], d_after[k]["books"][acct]
                    for kk in set(b0) | set(b1):
                        if kk == "settings":
                            for s in set(b0[kk]) | set(b1[kk]):
                                if b0[kk].get(s) != b1[kk].get(s): diffs.append(f"{acct}.settings.{s}")
                        elif b0.get(kk) != b1.get(kk): diffs.append(f"{acct}.{kk}")
                other = [x for x in d_after[k] if x not in ("books", "accounts", "activeAccount") and d_before[k].get(x) != d_after[k].get(x)]
                diffs += other
            elif d_before.get(k) != d_after.get(k): diffs.append(k)
        check(f"{tag} 16 ติ๊กช่อง → เขียนเฉพาะ settings.routineLog ของบัญชีแรก (ไม่แตะอย่างอื่น)", diffs == ["main.settings.routineLog"], json.dumps(diffs))
        # สลับบัญชีที่ใช้งาน → ค่าติ๊กไม่หาย (เก็บที่บัญชีแรก)
        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(500); go_today(page)
        st = js(page, "()=>document.querySelector('.tdSs[data-slot=\"selUS2\"]').dataset.st")
        check(f"{tag} 16 สลับบัญชีเป็น Family → ค่าติ๊กยังอยู่ (เก็บที่บัญชีแรก)", st == "done", st)
        js(page, "()=>acctSwitch('main')"); page.wait_for_timeout(400)
        check(f"{tag} 9-12 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── 13 เสาร์ · 15 ว่าง ─────────────────────────
def weekend_empty_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, iso=SAT)
    try:
        go_today(page)
        wk = js(page, """()=>({routine: !!document.querySelector('[data-td-routine]'), off: (document.querySelector('[data-td-off]')||{}).textContent, daily: !!document.querySelector('.tdRow[data-kind="sat-daily"]'),
            stale: !!document.querySelector('.tdRow[data-kind="stale"]'), bias: !!document.querySelector('.tdRow[data-kind="bias"]'), slots: document.querySelectorAll('.tdSs').length, when: document.querySelector('[data-td-when]').textContent})""")
        check(f"{tag} 13 เสาร์ → ไม่มี Routine · มีข้อความวันหยุด", not wk["routine"] and wk["slots"] == 0 and "วันหยุด" in (wk["off"] or "") and "Routine จ.–ศ." in wk["off"], json.dumps(wk, ensure_ascii=False))
        check(f"{tag} 13 เสาร์ → ไม่มีแถวเช็กแผน Sat · งานอื่นยังแสดง (ราคาเก่า) · ไม่มีงาน Bias (PF1)", (not wk["daily"]) and wk["stale"] and not wk["bias"], json.dumps(wk, ensure_ascii=False))
        check(f"{tag} 13 หัวแสดงวันเสาร์ 3 ต.ค.", wk["when"].startswith("เสาร์ 3 ต.ค."), wk["when"])
        shot(page, f"td1-weekend-{label.replace('px','')}.png")
        check(f"{tag} 13 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()
    # 15 ไม่มีงานเลย
    clean_log = {TODAY: {"slots": [], "sat": ["XAUUSD", "BTC", "S50", "BRENT"]}}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=doc38(clean=True, log=clean_log), clean=True)
    try:
        go_today(page)
        g = js(page, """()=>({grps: [...document.querySelectorAll('[data-td-grp]')].map(e=>e.dataset.tdGrp), rows: document.querySelectorAll('.tdRow').length,
            badge: getComputedStyle(document.getElementById('tabBadgeToday')).display, cnts: document.querySelectorAll('.tdCnt').length, okline: (document.querySelector('[data-td-okline] .txt .full')||{}).textContent || ''})""")
        check(f"{tag} 15 ไม่มีงานเลย → ไม่มีกลุ่มงาน (TD2: เหลือบรรทัดเขียวบรรทัดเดียว) · ไม่มีแถวงาน", g["grps"] == [] and g["rows"] == 0 and g["okline"].startswith("✓ อื่น ๆ ปกติ —"), json.dumps(g, ensure_ascii=False))
        check(f"{tag} 15 ไม่มีเลขแดงบนปุ่มแท็บ · ไม่มีชิปนับหัว", g["badge"] == "none" and g["cnts"] == 0, json.dumps(g, ensure_ascii=False))
        shot(page, f"td1-empty-{label.replace('px','')}.png")
        check(f"{tag} 15 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── 14 ค่าตั้ง ─────────────────────────
def settings_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        js(page, "()=>{ openSystemSettings(); document.getElementById('tdSetSec').open = true; }"); page.wait_for_timeout(300)
        rows = js(page, "()=>[...document.querySelectorAll('[data-rt-row]')].map(r=>[...r.querySelectorAll('[data-rt-f]')].map(i=>i.value))")
        check(f"{tag} 14 ค่าเริ่มต้น 5 ช่วงครบ (เวลา · ชื่อ · ลิงก์)", len(rows) == 5 and rows[0] == ["09:00", "10:00", "Trading Plan TH", "planTH"] and rows[4] == ["19:00", "20:00", "Stock Selection TH", "watch"], json.dumps(rows, ensure_ascii=False))
        sats = js(page, "()=>[...document.querySelectorAll('[data-rt-sat]')].map(c=>c.checked)")
        check(f"{tag} 14 ช่อง ☐ 4 ตลาดเช็กแผน Sat รายวัน ติ๊กครบตามค่าเริ่มต้น", sats == [True] * 4)
        shot(page, f"td1-settings-{label.replace('px','')}.png")
        # เพิ่ม 21:00–21:30
        page.locator("[data-rt-add]").click(); page.wait_for_timeout(200)
        dis = js(page, "()=>document.getElementById('tdSetSave').disabled")
        check(f"{tag} 14 เพิ่มช่วงเปล่า → แดง + ปุ่มบันทึกปิด", dis and js(page, "()=>document.querySelectorAll('[data-rt-row].bad').length") == 1)
        last = page.locator("[data-rt-row]").last
        last.locator('[data-rt-f="name"]').fill("ทบทวนท้ายวัน"); last.locator('[data-rt-f="end"]').fill("21:30"); last.locator('[data-rt-f="start"]').fill("21:00"); last.locator('[data-rt-f="start"]').press("Tab")
        page.wait_for_timeout(200)
        last = page.locator("[data-rt-row]").last
        check(f"{tag} 14 กรอกครบ 21:00–21:30 → ปุ่มบันทึกเปิด · ไม่แดง", js(page, "()=>!document.getElementById('tdSetSave').disabled && document.querySelectorAll('[data-rt-row].bad').length===0"))
        page.locator("[data-rt-save]").click(); page.wait_for_timeout(600)
        saved = settings_db(page)["routine"]
        check(f"{tag} 14 บันทึก → settings.routine มี 6 ช่วงเรียงตามเวลา + satDaily 4", [s["start"] for s in saved["slots"]] == ["09:00", "11:00", "13:00", "15:30", "19:00", "21:00"] and saved["satDaily"] == ["XAUUSD", "BTC", "S50", "BRENT"], json.dumps(saved, ensure_ascii=False))
        js(page, "()=>{ document.getElementById('sysOverlay').classList.remove('show'); switchTab('today'); }"); page.wait_for_timeout(300)
        check(f"{tag} 14 Routine มี 6 ช่อง · ช่องใหม่ชื่อ 'ทบทวนท้ายวัน' 21:00–21:30", js(page, "()=>document.querySelectorAll('.tdSs').length") == 6 and "21:00–21:30" in js(page, "()=>document.querySelector('.tdSs[data-st=\"future\"]:last-child').innerText"))
        # ตรวจผิด
        js(page, "()=>{ openSystemSettings(); document.getElementById('tdSetSec').open = true; }"); page.wait_for_timeout(300)
        errs = []
        def probe(i, f, v, expect_bad, what):
            inp = page.locator(f"[data-rt-row] >> nth={i}").locator(f'[data-rt-f="{f}"]'); old = inp.input_value()
            inp.fill(v); page.wait_for_timeout(150)
            bad = js(page, "()=>document.querySelectorAll('[data-rt-row].bad').length"); dis = js(page, "()=>document.getElementById('tdSetSave').disabled")
            ok = (bad >= 1 and dis) if expect_bad else (bad == 0 and not dis)
            errs.append((what, ok, [bad, dis]))
            return old
        old = probe(1, "start", "09:30", True, "ทับกัน"); probe(1, "start", old, False, "คืนค่า")
        old = probe(1, "end", "10:30", True, "จบ ≤ เริ่ม"); probe(1, "end", old, False, "คืนค่า")
        old = probe(1, "name", "", True, "ชื่อว่าง"); probe(1, "name", old, False, "คืนค่า")
        old = probe(1, "start", "25:00", True, "เวลาไม่ใช่ HH:MM"); probe(1, "start", old, False, "คืนค่า")
        old = probe(1, "name", "ก" * 31, True, "ชื่อยาวเกิน 30"); probe(1, "name", old, False, "คืนค่า")
        check(f"{tag} 14 ตรวจ: ทับกัน / จบ ≤ เริ่ม / ชื่อว่าง / เวลาผิดรูปแบบ / ชื่อยาว → แดง + ปุ่มบันทึกปิด · แก้แล้วกลับปกติ", all(e[1] for e in errs), json.dumps(errs, ensure_ascii=False))
        # ลบช่วง
        n0 = js(page, "()=>document.querySelectorAll('[data-rt-row]').length")
        page.locator("[data-rt-del]").last.click(); page.wait_for_timeout(200)
        check(f"{tag} 14 ลบช่วง (×) → จำนวนแถวลด 1", js(page, "()=>document.querySelectorAll('[data-rt-row]').length") == n0 - 1)
        # คืนค่าเริ่มต้น + ปิด Brent
        page.locator("[data-rt-reset]").click(); page.wait_for_timeout(200)
        r5 = js(page, "()=>document.querySelectorAll('[data-rt-row]').length")
        page.locator('[data-rt-sat="BRENT"]').uncheck(); page.wait_for_timeout(100)
        page.locator("[data-rt-save]").click(); page.wait_for_timeout(600)
        saved = settings_db(page)["routine"]
        check(f"{tag} 14 คืนค่าเริ่มต้น → 5 ช่วง · ปิด Brent → settings.routine.satDaily 3 ตลาด", r5 == 5 and len(saved["slots"]) == 5 and saved["satDaily"] == ["XAUUSD", "BTC", "S50"], json.dumps(saved, ensure_ascii=False))
        js(page, "()=>{ document.getElementById('sysOverlay').classList.remove('show'); switchTab('today'); }"); page.wait_for_timeout(300)
        chips = js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=\"sat-daily\"] .tdAs .nm')].map(e=>e.textContent)")
        check(f"{tag} 14 ช่องเช็กแผน Sat เหลือ 3 (ไม่มี Brent · ชื่อแสดง XAU)", chips == ["XAU", "BTC", "S50"], json.dumps(chips))
        check(f"{tag} 14 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── 17 มือถือ / จอใหญ่ layout ─────────────────────────
def layout_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        L = js(page, """()=>{ const bs = [...document.querySelectorAll('#tabsMain .tabbtn')].filter(b=>b.offsetParent!==null).map(b=>{ const r = b.getBoundingClientRect(); return {id:b.id, top: Math.round(r.top), left: Math.round(r.left), right: Math.round(r.right), bottom: Math.round(r.bottom), sw: b.scrollWidth, cw: b.clientWidth}; });
            return {n: bs.length, tops: [...new Set(bs.map(b=>b.top))], maxR: Math.max(...bs.map(b=>b.right)), minL: Math.min(...bs.map(b=>b.left)), overflowBtn: bs.filter(b=>b.sw > b.cw + 1).map(b=>b.id), W: innerWidth}; }""")
        check(f"{tag} 17 ปุ่มแท็บ 6 ตัวอยู่บรรทัดเดียว ไม่ล้น (top เดียว · อยู่ในจอ · ข้อความไม่ถูกตัด)", L["n"] == 6 and max(L["tops"]) - min(L["tops"]) <= 3 and L["maxR"] <= L["W"] + 1 and L["minL"] >= -1 and not [x for x in L["overflowBtn"] if x != "tabBtnToday"], json.dumps(L))
        if w <= 480:
            tl = js(page, "()=>[...document.querySelectorAll('.tdSs')].filter(e=>e.offsetParent!==null).map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width)]; })")
            check(f"{tag} 17 Routine เรียงลง (ซ้ายเท่ากัน · top เพิ่มขึ้น) · TD2: มือถือเห็น 3 ช่อง (ตอนนี้ + ยังไม่ถึง)", len(tl) == 3 and len({t[0] for t in tl}) == 1 and all(tl[i][1] < tl[i + 1][1] for i in range(2)), json.dumps(tl))
            hide = js(page, "()=>[...document.querySelectorAll('.tdRow .tdWhere:not(.tdWhereKeep)')].every(e=>getComputedStyle(e).display==='none') && [...document.querySelectorAll('.tdBtn .short')].every(e=>getComputedStyle(e).display!=='none') && [...document.querySelectorAll('.tdBtn .full')].every(e=>getComputedStyle(e).display==='none')")
            check(f"{tag} 17 มือถือ: ซ่อนบรรทัดรอง · ปุ่มขวาเหลือ →", hide)
            ga = js(page, "()=>document.querySelectorAll('[data-td-grp=\"a\"] .tdRow').length")
            check(f"{tag} 17 มือถือ: กลุ่มสัปดาห์นี้แสดงครบ (ไม่ย่อ) = 6 แถว (รวมการบ้าน · PF1: ไม่มีงาน Bias)", ga == 6, str(ga))
            hint = js(page, "()=>[...document.querySelectorAll('#tabsMain .kbdhint')].every(e=>getComputedStyle(e).display==='none')")
            check(f"{tag} 17 มือถือ: ซ่อน .kbdhint", hint)
        else:
            tl = js(page, "()=>[...document.querySelectorAll('.tdSs')].map(e=>Math.round(e.getBoundingClientRect().top))")
            check(f"{tag} 17 จอใหญ่: 5 ช่อง Routine เรียงแถวเดียว", len(tl) == 5 and len(set(tl)) == 1, json.dumps(tl))
        bad = overflow_x(page, [".tdWrap", ".tdRow", ".tdRt", ".tdSs", ".tdPc", ".tdWhat"])
        check(f"{tag} 17 ไม่ล้นแนวนอน (ราย element: wrap · แถวงาน · routine · ช่อง · ชิป)", not bad, json.dumps(bad))
        pts = js(page, """()=>[...document.querySelectorAll('.tdRow[data-go]')].slice(0, 12).map(e=>{ e.scrollIntoView({block:'center'}); const r = e.getBoundingClientRect(); const x = r.left + r.width*0.4, y = r.top + r.height/2;
            const hit = document.elementFromPoint(x, y); return !!hit && e.contains(hit); })""")
        check(f"{tag} 17 elementFromPoint ของแถว = แถวนั้น (ไม่มีอะไรบัง)", pts and all(pts), json.dumps(pts))
        pts = js(page, """()=>[...document.querySelectorAll('.tdSs')].filter(e=>e.offsetParent!==null).map(e=>{ e.scrollIntoView({block:'center'}); const k = e.querySelector('.k').getBoundingClientRect(); const hit = document.elementFromPoint(k.left + k.width/2, k.top + k.height/2); return !!hit && hit.closest('.k') === e.querySelector('.k'); })""")
        check(f"{tag} 17 elementFromPoint ของวงกลมติ๊กทุกช่อง = ปุ่มวงกลม", pts and all(pts), json.dumps(pts))
        check(f"{tag} 17 ไม่มี console error", not ce and not pe, "; ".join((ce + pe)[:3]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (430, 932, "430px")):
            tab_tests(pw, w, h, label)
            task_tests(pw, w, h, label)
            routine_tests(pw, w, h, label)
            weekend_empty_tests(pw, w, h, label)
            settings_tests(pw, w, h, label)
            layout_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 38 / TD1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
