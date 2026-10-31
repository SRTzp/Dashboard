#!/usr/bin/env python3
"""TD2 — แท็บ Today ลดความรก (ปกติ = เงียบ) · เช็กแผน Sat ✓/✕ + Focus · การบ้านหุ้นวันละ 1 ตัว · เทส 39
mock Firestore · Chromium 1440 + 390 + 430 · นาฬิกาปลอม = 2026-10-02 13:03 ไทย (ศุกร์ · สัปดาห์เริ่ม 2026-09-27) · timezone Asia/Bangkok
seed ตาม docs/briefs/TD2-brief.md · ภาพเก็บที่ tests/screenshots/td2-*.png (normal · numbers-open · abnormal · sat-focus · homework × 1440/390)
รัน: python3 run_tests_phase39.py"""
import copy, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase38 as P
from ff_stub import FF_STUB

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = P.INDEX
ENGINE = base.BROWSER_ENGINE
T, TODAY, WK = P.T, P.TODAY, P.WK
CLK = "2026-10-02T06:03:00Z"        # 13:03 ไทย (ศุกร์)
CLK_SAT = "2026-10-03T06:03:00Z"
CLK_LATE = "2026-10-02T13:30:00Z"   # 20:30 ไทย (หลังช่องสุดท้าย)
results = []
OK_FULL = "✓ อื่น ๆ ปกติ — DD · heat · ไม้ใหม่ · ชั้น 2 · f · fundflow"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    page.wait_for_timeout(900)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=True)
    except Exception as e: print("shot fail", name, e)


js, dump, settings_db, kinds, rows_text, row, go_today = P.js, P.dump, P.settings_db, P.kinds, P.rows_text, P.row, P.go_today


PICK39 = ['XAUUSD', 'BTCUSD', 'BRENT']


SEED_PLANS = (__name__ == '__main__')
TZID = "Asia/Bangkok"   # WM1b — เทสเขตเวลาเครื่อง (run_tests_phase101 สลับเป็น UTC / America/New_York)


TD3_OTHER_OPEN = True
TD3_OTHER_DEV = True   # TD4b — Today ไม่มี Other ▸ แล้ว: ชุดเก่าเปิดจุดต่อ dash.td3OtherDev เพื่อยังทดสอบของเดิมใน Other ได้ (phase108 ตั้งเป็น False)


import run_tests_phase24 as P24_
PIN_BOTH = (__name__ == "__main__")


def launch(pw, w, h, doc=None, cards=None, iso=CLK, clean=False, ff=None, extra=None, pick=None):
    """เหมือน P.launch แต่มี extra(page) ให้ seed เพิ่มก่อน login (watchlist/research ตามเคส)"""
    lk = {"headless": True}
    if base.CHROMIUM_PATH: lk["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    context = browser.new_context(viewport={"width": w, "height": h}, timezone_id=TZID)
    context.add_init_script(FF_STUB)
    if TD3_OTHER_DEV: context.add_init_script("try{ localStorage.setItem('dash.td3OtherDev','1'); }catch(e){}")
    if TD3_OTHER_OPEN: context.add_init_script("try{ localStorage.setItem('dash.td3Other','1'); }catch(e){}")   # TD3a — งานเดิมของ Today อยู่ใน Other ▸ (พับ lazy) → ชุดเก่าเปิดไว้ก่อน
    context.add_init_script("(" + P.CLOCK_JS + ")(" + json.dumps(iso) + ")")
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
    doc = doc if doc is not None else P.doc38()
    if PIN_BOTH: P24_.pin_both_pools(doc)   # RG2b — ตรึงถัง Winner/Sat เท่าทุนเดิม (รันเป็นสคริปต์ของชุดนี้เท่านั้น)
    PK = PICK39 if pick is None else pick   # pick=False → ไม่ override (ชุด WA1+ ตั้ง pick เอง)
    if PK:   # WA1fix — Today นับเฉพาะ Asset ที่เลือกสัปดาห์นี้ (เพดาน 3): ชุดนี้ใช้ XAU · BTC · Brent (S50 ไม่ได้เลือก)
        for _b in doc["books"].values():
            _m = _b["settings"].get("satWeekPick")
            if _m is not None: _b["settings"]["satWeekPick"] = {w_: list(PK) for w_ in _m}
    page.evaluate("(d)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], d); }", doc)
    for cid, c in ((cards if cards is not None else ({} if clean else P.cards38())).items()):
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    if extra is None: P.seed_all(page, clean)
    else:
        P.seed_all(page, True)
        extra(page)
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(1200)
    p24.set_ff(page, ff if ff is not None else {"as_of": "2026-10-02", "ratios": {"ACWI_BIL": {"up": False}, "HYG_IEI": {"up": True}}})
    page.evaluate("()=>{ if(window.rsLoad) return rsLoad(true); }"); page.wait_for_timeout(600)
    page.evaluate("()=>render()"); page.wait_for_timeout(300)
    if SEED_PLANS and PK:   # PF2 — pick มีแผนใช้งานแล้ว = state C (เทสเก่าคาดว่า Today เงียบเมื่อปกติ)
        from pf2_retire import seed_plans; seed_plans(page, PK)
    return browser, context, page, ce, pe, dialogs


def seed(page, path, d): page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [path, d])


def ds_set(doc, acct, bucket, tank, **kw): doc["books"][acct]["settings"]["ddState"]["winner" if bucket == "core" else bucket] = P.ds0(tank, **kw)   # RG2b §4.7 — เบรก DD ต่อถัง (core → Winner)


def okfull(page): return js(page, "()=>{ const e = document.querySelector('[data-td-okline] .txt .full'); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; }")
def okline(page): return js(page, "()=>{ const e = document.querySelector('[data-td-okline] .txt'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }")
def txt_of(page, sel): return js(page, "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def sat_cls(page, i): return js(page, "(i)=>{ const e = document.querySelector('[data-sat-chip=\"'+i+'\"]'); return e ? e.dataset.state : null; }", i)
def ri(page): return js(page, "()=>(document.querySelector('[data-td-grp=\"a\"]')||{innerText:''}).innerText")


def overlap_check(page, sel):
    """ข้อความในแถวกับป้าย/ปุ่มต้องไม่ซ้อนกัน (bounding box)"""
    return page.evaluate("""(sel)=>{ const bad = [];
      const inter = (a, b) => Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1.5 && Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1.5;
      document.querySelectorAll(sel).forEach((el, n)=>{
        if(!el.getClientRects().length) return;
        const boxes = [...el.querySelectorAll('.tdTag,.tdCntTag,.tdBtn,.tdHwBtns,.tdN,.tdNow,button')].filter(b=>b.getClientRects().length).map(b=>({r: b.getBoundingClientRect(), k: b.className || b.tagName}));
        const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
        let nd; while((nd = walker.nextNode())){
          if(!nd.textContent.trim()) continue;
          const par = nd.parentElement; if(!par || par.closest('.tdTag,.tdCntTag,.tdBtn,.tdHwBtns,.tdN,.tdNow,button') || getComputedStyle(par).display === 'none') continue;
          const rg = document.createRange(); rg.selectNodeContents(nd);
          [...rg.getClientRects()].forEach(tr=>{ if(tr.width < 1) return; boxes.forEach(b=>{ if(inter(tr, b.r)) bad.push((el.dataset.kind || el.className) + ' ‹' + nd.textContent.trim().slice(0, 24) + '› × ' + b.k); }); });
        }
      });
      return bad.slice(0, 6); }""", sel)


def vis_slots(page): return js(page, "()=>[...document.querySelectorAll('.tdSs')].filter(e=>e.offsetParent!==null).map(e=>e.dataset.slot)")


# ───────────────────────── 1–2 ปกติ = เงียบ · ดูตัวเลข ─────────────────────────
def quiet_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(clean=True, log={}), clean=True)
    try:
        go_today(page)
        g = js(page, """()=>({pulse: !!document.querySelector('[data-td-pulse]') || !!document.querySelector('.tdPc'), grpG: !!document.querySelector('[data-td-grp="g"]'), oks: document.querySelectorAll('.tdOk').length,
            okline: !!document.querySelector('[data-td-okline]'), rows: [...document.querySelectorAll('.tdRow')].map(e=>e.dataset.kind)})""")
        t = okline(page)
        check(f"{tag} 1 ทุกอย่างปกติ → ไม่มีแถบชิปสถานะ · ไม่มีกลุ่ม 'ปกติ'", not g["pulse"] and not g["grpG"] and g["oks"] == 0, json.dumps(g, ensure_ascii=False))
        want = OK_FULL if w > 480 else "✓ อื่น ๆ ปกติ"
        check(f"{tag} 1 มีบรรทัดเขียวบรรทัดเดียว '{want}'", g["okline"] and t == want, str(t))
        check(f"{tag} 1 งานที่เหลือ = เช็กแผน Sat เท่านั้น (ยังไม่ดู) — ไม่มีงานผิดปกติ", g["rows"] == ["sat-daily"], json.dumps(g["rows"]))
        shot(page, f"td2-normal-{label.replace('px','')}.png") if w in (1440, 390) else None
        # ── 2 ดูตัวเลข ──
        det = lambda: js(page, "()=>getComputedStyle(document.querySelector('[data-td-det]')).display!=='none'")
        check(f"{tag} 2 ค่าเริ่มต้นพับ (ตารางไม่แสดง)", not det())
        page.locator('[data-td-numbtn]').click(); page.wait_for_timeout(200)
        tbl = js(page, """()=>({head: [...document.querySelectorAll('[data-td-nums] thead th')].map(e=>e.innerText.trim()), rows: [...document.querySelectorAll('[data-td-nums] tbody tr')].map(r=>({a:r.dataset.numAcct, c:[...r.children].map(c=>c.innerText.trim())})),
            foot: document.querySelector('[data-td-detfoot]').innerText.trim()})""")
        exp = js(page, """()=>acctList.map(a=>{ const bs = sat7dAcctBase(a.id), cr = coreAcctRisk(a.id), d1 = ddEval(a.id,'winner'), d3 = ddEval(a.id,'ladder'), d2 = ddEval(a.id,'sat'), f = x=>String(Math.round(x*100)/100);
            return {a: a.id, c: [td3AcctName(a), f(d1.ddPct)+'%', f(d3.ddPct)+'%', f(d2.ddPct)+'%', f(bs.heatPct)+' / '+bs.heatMax+'%', bs.nNew+' / '+bs.newMax, f(cr.layer2Pct)+'%']}   /* RG2b — DD แยก Winner/Ladder · ชั้น 2 ไม่มีเพดาน */; })""")
        check(f"{tag} 2 กด 'ดูตัวเลข' → ตาราง 2 แถว (Main · Family) × 6 คอลัมน์ (RG2b: DD Winner · DD Ladder แยก)", len(tbl["rows"]) == 2 and [r["c"][0] for r in tbl["rows"]] == ["Main", "Family"] and len(tbl["head"]) == 7 and det(), json.dumps(tbl, ensure_ascii=False))
        check(f"{tag} 2 ค่าในตารางตรงกับฟังก์ชันเดิม (ddEval · sat7dAcctBase · coreAcctRisk)", [(r["a"], r["c"]) for r in tbl["rows"]] == [(e["a"], e["c"]) for e in exp], json.dumps([tbl["rows"], exp], ensure_ascii=False))
        check(f"{tag} 2 ใต้ตาราง 'fundflow อัปเดต 2 ต.ค.' (RG2b ถอดประตู FF)", tbl["foot"] == "fundflow อัปเดต 2 ต.ค.", tbl["foot"])
        if w in (1440, 390): shot(page, f"td2-numbers-open-{label.replace('px','')}.png")
        if w <= 480:
            ov = P.overflow_x(page, ["[data-td-det]", "[data-td-nums]", ".tdWrap", ".tdOkLine"])
            check(f"{tag} 2 มือถือ: ตารางตัวเลขไม่ล้นแนวนอน (หัวคอลัมน์ย่อ)", not ov and "DD W" in tbl["head"], json.dumps([ov, tbl["head"]], ensure_ascii=False))
        page.locator('[data-td-numbtn]').click(); page.wait_for_timeout(150)
        check(f"{tag} 2 กดซ้ำ = พับ", not det())
        check(f"{tag} 1-2 console: ไม่มี error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()


# ───────────────────────── 3–4 ผิดปกติ = ขึ้นเป็นงาน ─────────────────────────
def abnormal_doc():
    doc = P.doc38(clean=True, log={})
    m, f = doc["books"]["main"], doc["books"]["fam"]
    # heat Sat main 5.0/6% (ความเสี่ยงค้าง $1,300 × 40 ÷ ทุน $26,000 × 40)
    m["trades"] = [T("tsh", "satB", "open", sym="XAUUSD", entry=100, sl=90, qty=130, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30"),
                   T("tms", "core", "open", sym="MSFT", entry=400, sl=380, qty=10, cur="USD", date="2026-09-10", openedAt="2026-09-10")]
    # ไม้ใหม่ Family 4/4 (เสี่ยงน้อย)
    f["trades"] = [T("tfa", "satB", "open", sym="XAUUSD", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-29", openedAt="2026-09-29"),
                   T("tfb", "satB", "open", sym="BRENT", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30"),
                   T("tfc", "satB", "open", sym="BTCUSD", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30"),
                   T("tfd", "satB", "open", sym="XAGUSD", entry=100, sl=99, qty=10, mult=1, cur="USD", date="2026-09-30", openedAt="2026-09-30")]   # RG2b: โควตาไม้ใหม่ 4/สัปดาห์ (เดิม 2)
    m["settings"].setdefault("coreRisk", {}).update({"l2Warn": 0.1, "l2Cap": 20, "gateWeeks": 1, "riskPct": 1, "tierA": 10, "tierB": 5})   # CZ1: seed ค่าเดิม   # ชั้น 2 ถึงเตือน · ประตู f เปิดเมื่อแดง 1 สัปดาห์
    ds_set(doc, "main", "core", 7000000, peak=8050000)   # DD Core main ≈ 13.04% → ลดขนาด
    return doc


def abnormal_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    cards = {"cms": p24.open_card("cms", "tms", ticker="MSFT", acct="main", qty=10, entry=400, sl=380, px=410, pxDate="2026-09-30", emaW=390, tier="A")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=abnormal_doc(), cards=cards, clean=True)
    try:
        go_today(page)
        ka, kb = kinds(page, "a"), kinds(page, "b")
        ta, tb = rows_text(page, "a"), rows_text(page, "b")
        j = lambda k, arr=ta, ks=ka: next((arr[i] for i, x in enumerate(ks) if x == k), "")
        ev = js(page, "()=>{ const e = ddEval('main','winner'); return [e.stage, Math.round(e.ddPct*100)/100]; }")
        bs = js(page, "()=>{ const b = sat7dAcctBase('main'); return [Math.round(b.heatPct*100)/100, b.heatMax, b.nNew]; }")
        check(f"{tag} 3 ฐาน: DD Core main = reduce · heat main {bs[0]}/{bs[1]}% (≥ 80%)", ev[0] == "reduce" and abs(bs[0] - 5) < 0.01 and bs[1] == 6, json.dumps([ev, bs]))
        check(f"{tag} 3 heat Sat 5.0/6% → แถว 🟡 'heat Sat Main 5/6% · เหลือที่ 1%'", bool(re.search(r"heat Sat Main 5(\.0+)?/6% · เหลือที่ 1(\.0+)?%", j("heat"))) and ka.count("heat") == 1, j("heat") + str(ka))
        ol = okfull(page)
        check(f"{tag} 3 บรรทัดปกติไม่มีคำ 'heat' (แต่ยังมี fundflow)", ol is not None and "heat" not in ol and "fundflow" in ol, str(ol))
        page.locator('[data-td-numbtn]').click(); page.wait_for_timeout(200)
        cls = js(page, "()=>{ const r = document.querySelector('[data-num-acct=\"main\"]'); return [r.children[4].className, r.children[4].innerText.trim()]; }")
        check(f"{tag} 3 ตารางค่า heat main เป็นสีเหลือง (class a)", cls[0] == "a" and cls[1].startswith("5"), json.dumps(cls))
        check(f"{tag} 4 ไม้ใหม่ Family 4/4 → แถว 🟡 'ไม้ใหม่ Sat Family ครบ 4/4 สัปดาห์นี้'", "ไม้ใหม่ Sat Family ครบ 4/4 สัปดาห์นี้" in j("newcnt"), j("newcnt"))
        check(f"{tag} 4 DD Winner main reduce → แถว 🟡 'เบรก DD Winner Main: ลดขนาด ×0.5 · DD x%' (RG2b §4.7 แยกต่อถัง)", bool(re.search(r"เบรก DD Winner Main: ลดขนาด ×0\.5 · DD 1[23]\.", j("dd-reduce"))), j("dd-reduce"))
        check(f"{tag} 4 ไม่มีแถวเตือนชั้น 2 (RG2b ถอดเพดานชั้น 2)", j("l2") == "", j("l2") + str(ka))
        check(f"{tag} 4 ไม่มีแถวประตู FF เปิด (RG2b ถอดประตู)", j("gate", tb, kb) == "", json.dumps(tb, ensure_ascii=False))   # RG2b — ไม่มีแถวประตู FF
        ol = okline(page)
        check(f"{tag} 4 บรรทัดปกติตัดคำของหมวดผิดปกติ (DD · heat · ไม้ใหม่ · ชั้น 2 · f) → เหลือ fundflow", ol in ("✓ อื่น ๆ ปกติ — ไม้ใหม่ · ชั้น 2 · f · fundflow", "✓ อื่น ๆ ปกติ — ชั้น 2 · f · fundflow", "✓ อื่น ๆ ปกติ — ชั้น 2 · fundflow", "✓ อื่น ๆ ปกติ — f · fundflow") or (w <= 480 and ol == "✓ อื่น ๆ ปกติ"), str(ol))   # RG2b — ชั้น 2 และ f ไม่เป็นเรื่องผิดปกติแล้ว
        row(page, "heat").click(); page.wait_for_timeout(500)
        st = js(page, "()=>({tab: activeTab, scope: planScope})")
        check(f"{tag} 4 กดแถว heat → แท็บแผน scope Future", st == {"tab": "plan", "scope": "future"}, json.dumps(st))
        go_today(page); row(page, "dd-reduce").click(); page.wait_for_timeout(400)
        check(f"{tag} 4 กดแถวลดขนาด → sheet DD Winner บัญชีหลัก", js(page, "()=>{ const h = document.querySelector('.core-sheet h3'); return !!h && /Winner/.test(h.textContent) && /บัญชีหลัก/.test(h.textContent); }"))
        js(page, "()=>coreSheetClose()"); page.wait_for_timeout(200)
        go_today(page)   # RG2b — แถวชั้น 2 / ประตู FF ถอดแล้ว: ไม่มีให้กด
        check(f"{tag} 4 ไม่มีแถวชั้น 2 และแถวประตู f ให้กด", js(page, "()=>document.querySelectorAll('[data-kind=l2],[data-kind=gate]').length") == 0)
        go_today(page)
        if w in (1440, 390): shot(page, f"td2-abnormal-{label.replace('px','')}.png")
        if w <= 480:
            ov = P.overflow_x(page, ["[data-td-det]", "[data-td-nums]", ".tdOkLine", "[data-td-nums] td", "[data-td-nums] th"])
            tw = js(page, "()=>{ const d = document.querySelector('[data-td-det]'); const t = document.querySelector('[data-td-nums]'); return [d.clientWidth, t.scrollWidth, d.scrollWidth]; }")
            check(f"{tag} 4 มือถือ: ตารางตัวเลขตอนค่ายาว (12.99% · 0.17 / 20%) ไม่ล้นแนวนอน", not ov and tw[1] <= tw[0] + 1, json.dumps([ov, tw]))
            bad = overlap_check(page, ".tdRow")
            check(f"{tag} 4 งานผิดปกติ: ข้อความกับป้ายไม่ซ้อนกัน", not bad, json.dumps(bad, ensure_ascii=False))
        check(f"{tag} 3-4 console: ไม่มี error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()
    # fundflow เก่า
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(clean=True, log={}), clean=True, ff={"as_of": "2026-09-22", "ratios": {"ACWI_BIL": {"up": False}, "HYG_IEI": {"up": True}}})
    try:
        go_today(page)
        ka = kinds(page, "a"); ta = rows_text(page, "a")
        age = js(page, "()=>coreFNow().age")
        r = next((ta[i] for i, k in enumerate(ka) if k == "ff-stale"), "")
        check(f"{tag} 4 fundflow เก่า → แถว 🟡 'fundflow เก่า {age} วัน — ค่า FF/ประตูไม่แม่น' (UX2: f→FF)", f"fundflow เก่า {age} วัน — ค่า FF/ประตูไม่แม่น" in r and age >= 5, r + " / " + str(age))
        ol = okline(page)
        check(f"{tag} 4 fundflow เก่า → บรรทัดปกติไม่มีคำ 'fundflow'", ol is not None and "fundflow" not in ol, str(ol))
        row(page, "ff-stale").click(); page.wait_for_timeout(300)
        check(f"{tag} 4 กดแถว fundflow เก่า → แท็บ Flow", js(page, "()=>activeTab") == "flow")
    finally:
        browser.close()


# ───────────────────────── 5 DD พักครบเวลา ไม่ทบทวน ─────────────────────────
def review_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    doc = P.doc38(clean=True, log={})
    ds_set(doc, "main", "sat", 26000, stage="pause", stageSince="2026-09-20", pauseUntil="2026-09-27")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=doc, clean=True)
    try:
        go_today(page)
        kr, tr = kinds(page, "r"), rows_text(page, "r")
        r = next((tr[i] for i, k in enumerate(kr) if k == "dd-review"), "")
        check(f"{tag} 5 DD Sat pause หมดเวลา ไม่มีรีวิว → แถว 'เบรก DD Sat Main: รอเขียนทบทวน' (ไม่มี 'พักถึง 27 ก.ย.')", "เบรก DD Sat Main: รอเขียนทบทวน" in r and "พักถึง" not in r and "27 ก.ย." not in r, r)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(500)
        chips = js(page, "()=>[...document.querySelectorAll('[data-dd-chip=\"sat\"]')].map(e=>e.textContent.trim())")
        check(f"{tag} 5 ชิป DD ในแท็บแผน = 'รอเขียนทบทวน' (ไม่มีวันที่ที่ผ่านไปแล้ว)", any("รอเขียนทบทวน" in c for c in chips) and not any("พักถึง" in c for c in chips), json.dumps(chips, ensure_ascii=False))
        # ยังไม่ครบเวลา → ยังเป็น 'พักถึง' (อย่างอื่นเดิม)
        js(page, "()=>switchTab('today')")
    finally:
        browser.close()
    doc = P.doc38(clean=True, log={})
    ds_set(doc, "main", "sat", 26000, stage="pause", stageSince="2026-09-30", pauseUntil="2026-10-07")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=doc, clean=True)
    try:
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(500)
        chips = js(page, "()=>[...document.querySelectorAll('[data-dd-chip=\"sat\"]')].map(e=>e.textContent.trim())")
        check(f"{tag} 5 pause ที่ยังไม่ครบเวลา → ชิปยังเป็น 'พักถึง 7 ต.ค.' (อย่างอื่นเดิม)", any("พักถึง 7 ต.ค." in c for c in chips) and not any("รอเขียนทบทวน" in c for c in chips), json.dumps(chips, ensure_ascii=False))
    finally:
        browser.close()


# ───────────────────────── 6–9 เช็กแผน Sat ✓/✕ + Focus ─────────────────────────
def sat_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        st0 = {i: sat_cls(page, i) for i in ("XAUUSD", "BTC", "BRENT")}   # WA1fix: 3 ตัวที่เลือก (S50 ไม่ได้เลือก = ไม่ขึ้น)
        check(f"{tag} 6 เริ่มต้น: ยังไม่ดูทั้ง 3 (XAU · BTC · Brent) · S50 ไม่ขึ้น (ไม่ได้เลือกสัปดาห์นี้) · ป้าย Focus 0/2 · ไม่มีบรรทัด Focus", all(v == "none" for v in st0.values()) and not js(page, "()=>!!document.querySelector('[data-sat-chip=\"S50\"]')") and txt_of(page, "[data-sat-count]") == "Focus 0/2" and not js(page, "()=>!!document.querySelector('[data-td-focus]')"), json.dumps(st0))
        page.locator('[data-sat-ok="XAUUSD"]').click(); page.wait_for_timeout(400)
        lg = settings_db(page)["routineLog"][TODAY]
        fc = txt_of(page, "[data-td-focus]")
        check(f"{tag} 6 กด ✓ XAU → ช่องเขียว · satState.XAUUSD = 'ok' · ป้าย Focus 1/2", sat_cls(page, "XAUUSD") == "ok" and lg["satState"].get("XAUUSD") == "ok" and txt_of(page, "[data-sat-count]") == "Focus 1/2", json.dumps([sat_cls(page, "XAUUSD"), lg.get("satState")]))
        want = "Focus วันนี้: XAU · ยังไม่ดู: BTC · Brent" if w > 480 else "Focus: XAU · ยังไม่ดู BTC · Brent"
        check(f"{tag} 6 บรรทัด Focus มี XAU + ยังไม่ดู (ส่วนว่างไม่แสดง: ไม่มีคำ 'ไม่มีแผน')", fc == want, str(fc))
        green = js(page, "()=>{ const e = document.querySelector('[data-sat-chip=\"XAUUSD\"]'); const k = e.querySelector('[data-sat-ok]'); return [getComputedStyle(e).backgroundColor, getComputedStyle(k).backgroundColor]; }")
        check(f"{tag} 6 ช่อง ✓ = พื้นเขียว · ปุ่ม ✓ ทึบเขียว (ต่างจากช่องที่ยังไม่ดู)", green[0] != "rgb(255, 255, 255)" and green[1] != "rgb(255, 255, 255)" and green[0] != green[1], json.dumps(green))
        page.locator('[data-sat-ok="XAUUSD"]').click(); page.wait_for_timeout(400)
        lg = settings_db(page)["routineLog"][TODAY]
        check(f"{tag} 6 กด ✓ ซ้ำ → กลับยังไม่ดู · ไม่มีคีย์ใน satState · Focus หาย", sat_cls(page, "XAUUSD") == "none" and "XAUUSD" not in lg["satState"] and not js(page, "()=>!!document.querySelector('[data-td-focus]')"), json.dumps(lg.get("satState")))
        page.locator('[data-sat-no="BRENT"]').click(); page.wait_for_timeout(400)
        lg = settings_db(page)["routineLog"][TODAY]
        fc = txt_of(page, "[data-td-focus]")
        strike = js(page, "()=>getComputedStyle(document.querySelector('[data-sat-chip=\"BRENT\"] .nm')).textDecorationLine")
        check(f"{tag} 6 กด ✕ Brent → ขีดฆ่า · satState.BRENT = 'no' · ป้าย Focus 0/2 (นับเฉพาะ ✓)", sat_cls(page, "BRENT") == "no" and "line-through" in strike and lg["satState"].get("BRENT") == "no" and txt_of(page, "[data-sat-count]") == "Focus 0/2", json.dumps([strike, lg.get("satState")]))
        check(f"{tag} 6 Focus line มี 'ไม่มีแผน: Brent' (ยังไม่ดู BTC · S50 · XAU)", ("ไม่มีแผน: Brent" in fc and "ยังไม่ดู" in fc and "XAU" in fc) if w > 480 else ("Focus:" in fc and "ยังไม่ดู" in fc), str(fc))
        page.locator('[data-sat-ok="BRENT"]').click(); page.wait_for_timeout(400)
        check(f"{tag} 6 กดอีกปุ่ม = สลับ (✕ → ✓)", sat_cls(page, "BRENT") == "ok" and settings_db(page)["routineLog"][TODAY]["satState"]["BRENT"] == "ok")
        page.locator('[data-sat-no="BRENT"]').click(); page.wait_for_timeout(400)
        # ── ชื่อ → การ์ด Strategy ──
        page.locator('[data-sat-chip="BTC"] .nm').click(); page.wait_for_timeout(500)
        st = js(page, "()=>({tab: activeTab, scope: planScope})")
        check(f"{tag} 6 กดชื่อตลาด → แท็บแผน Future (การ์ด Strategy)", st == {"tab": "plan", "scope": "future"} and P.in_view(page, '#satV3Panel .ui-tile[data-key="BTCUSD"]'), json.dumps(st))
        go_today(page)
        # ── 7 ตัดสินครบ ──
        for i in ("XAUUSD", "BTC"):
            page.locator(f'[data-sat-ok="{i}"]').click(); page.wait_for_timeout(300)
        # BRENT = no อยู่แล้ว · TD2-fix: ✓ ครบ 2 → แถวหาย (S50 ยังไม่ดูก็ได้)
        ka = kinds(page, "a"); fc = txt_of(page, "[data-td-focus]")
        check(f"{tag} 7 ✓ ครบ 2 → แถวเช็กแผน Sat หายจากรายการ · บรรทัด Focus ยังอยู่ (WA1fix: ไม่มีตัวที่ยังไม่ดูเหลือ — S50 ไม่ได้เลือก)", "sat-daily" not in ka and fc is not None and "XAU" in fc and "ไม่มีแผน: Brent" in fc, json.dumps([ka, fc], ensure_ascii=False))
        if w > 480: check(f"{tag} 7 Focus: 'Focus วันนี้: XAU BTC · ไม่มีแผน: Brent แก้'", fc == "Focus วันนี้: XAU BTC · ไม่มีแผน: Brent แก้", str(fc))
        ta = rows_text(page, "a"); bi = next((ta[i] for i, k in enumerate(ka) if k == "bias"), "")
        check(f"{tag} 7 PF3 ✕ Brent: ไม่มีแถว Bias ในรายการ (งานถอดแล้ว) · แถวงานอื่นที่เหลือยังอยู่ครบลำดับ (การบ้าน · ราคาเก่า×2 · NVDA ตรวจ · งบ)", "bias" not in ka and ka == ["homework", "stale", "stale", "tw-review", "catalyst"], json.dumps(ka))
        check(f"{tag} 7 PF1 — ✕ Brent ไม่กระทบงานอื่น: ไม่มีแถว Bias", bi == "", bi)
        shot(page, f"td2-sat-focus-{label.replace('px','')}.png") if w in (1440, 390) else None
        page.wait_for_timeout(700)
        # เขียนรูปใหม่ ไม่มี sat:[…] เดิม
        lg = settings_db(page)["routineLog"][TODAY]
        check(f"{tag} 7 เขียนรูปใหม่ (satState) — ไม่มี sat:[…] เดิมใน log วันนี้", "sat" not in lg and lg["satState"] == {"XAUUSD": "ok", "BTC": "ok", "BRENT": "no"}, json.dumps(lg, ensure_ascii=False))
        check(f"{tag} 6-7 console: ไม่มี error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()
    # ── 7 ทุกตัว ✕ ──
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(log={TODAY: {"slots": [], "satState": {"XAUUSD": "no", "BTC": "no", "S50": "no", "BRENT": "no"}}}))
    try:
        go_today(page)
        check(f"{tag} 7 ทุกตัว ✕ → 'วันนี้ไม่มีแผน Sat' · แถวเช็กแผนหาย", txt_of(page, "[data-td-focus]") == "วันนี้ไม่มีแผน Sat แก้" and "sat-daily" not in kinds(page, "a"), str(txt_of(page, "[data-td-focus]")))
    finally:
        browser.close()
    # ── 8 log เก่า sat:['XAUUSD'] ──
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(log={"2026-09-30": {"slots": [], "sat": ["XAUUSD", "BTC"]}, TODAY: {"slots": ["planTH"], "sat": ["XAUUSD"]}}))
    try:
        go_today(page)
        fc = txt_of(page, "[data-td-focus]")
        check(f"{tag} 8 log เก่า sat:['XAUUSD'] (TD1) → XAU แสดงเป็น ✓ · Focus มี XAU", sat_cls(page, "XAUUSD") == "ok" and sat_cls(page, "BTC") == "none" and fc is not None and "XAU" in fc, f"{sat_cls(page, 'XAUUSD')} {fc}")
        d0 = json.dumps(settings_db(page)["routineLog"], sort_keys=True)
        js(page, "()=>{ renderToday(); render(); todayRefresh(true); }"); page.wait_for_timeout(500)
        raw = settings_db(page)["routineLog"][TODAY]
        check(f"{tag} 8 ไม่ migrate เขียนทับตอนอ่าน (log เดิมยังเป็น sat:[…])", raw.get("sat") == ["XAUUSD"] and "satState" not in raw, json.dumps(raw))
        page.locator('[data-sat-ok="BTC"]').click(); page.wait_for_timeout(400)
        raw = settings_db(page)["routineLog"][TODAY]
        check(f"{tag} 8 เขียนครั้งต่อไปใช้รูปใหม่ — XAUUSD (เดิม) ยังเป็น ok + BTC ok", raw.get("satState") == {"XAUUSD": "ok", "BTC": "ok"} and "sat" not in raw, json.dumps(raw))
    finally:
        browser.close()
    # ── 9 ชื่อแสดง ──
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        tx = js(page, "()=>document.getElementById('tabToday').innerText")
        names = js(page, "()=>[...document.querySelectorAll('.tdAs .nm')].map(e=>e.innerText.trim())")
        check(f"{tag} 9 ชื่อแสดง XAU · BTC · Brent (ที่เลือกสัปดาห์นี้) ในแท็บ Today · ไม่มีคำ 'XAUUSD'", names == ["XAU", "BTC", "Brent"] and "XAUUSD" not in tx and "BRENT" not in tx, json.dumps([names, "XAUUSD" in tx]))
        js(page, "()=>{ openSystemSettings(); document.getElementById('tdSetSec').open = true; }"); page.wait_for_timeout(300)
        lbl = js(page, "()=>[...document.querySelectorAll('[data-rt-sat]')].map(c=>c.parentElement.innerText.trim())")
        check(f"{tag} 9 ค่าตั้ง Daily routine: ชื่อ XAU · BTC · S50 · Brent", lbl == ["XAU", "BTC", "S50", "Brent"], json.dumps(lbl))
        js(page, "()=>{ document.getElementById('sysOverlay').classList.remove('show'); }")
        keys = js(page, "()=>TD_SAT_MK.map(m=>m.id)")
        check(f"{tag} 9 รหัสข้างในเดิม (XAUUSD · BTC · S50 · BRENT)", keys == ["XAUUSD", "BTC", "S50", "BRENT"], json.dumps(keys))
    finally:
        browser.close()


# ───────────────────────── 10–12 การบ้านหุ้น ─────────────────────────
def hw_extra(page):
    """WL2 — การบ้านดู Thesis ใน watchlist/{T} (เดิมดู research_card.as_of ใน research/{T}) · date = วันที่ Thesis"""
    dates = {"OLD": "2026-08-03", "MID": "2026-09-02", "DONE": "2026-07-01"}
    for tk in ("NOCARD", "OLD", "MID", "DONE"):
        seed(page, ["users", "testuid", "watchlist", tk], P.wl_th(tk, P.th(tk, date=dates[tk]) if tk in dates else None))


def hw_doc(log=None):
    return P.doc38(clean=True, log=log if log is not None else {"2026-09-29": {"slots": [], "satState": {}, "hw": {"pick": "DONE", "done": True}}})


def hw_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=hw_doc(), clean=True, extra=hw_extra)
    try:
        go_today(page)
        pick = lambda: js(page, "()=>{ const r = document.querySelector('.tdRow[data-kind=\"homework\"]'); return r ? [r.querySelector('b').textContent, r.querySelector('[data-hw-reason]').textContent] : null; }")
        cand = js(page, "()=>tdHomeworkCandidates().map(x=>[x.t, x.skip, x.reason])")
        p0 = pick()
        r0 = txt_of(page, '.tdRow[data-kind="homework"]')
        check(f"{tag} 10 เสนอ NOCARD + เหตุผล 'ยังไม่มี Thesis' (ไม่เสนอ DONE ที่ทำเมื่อ 3 วันก่อน)", p0 == ["NOCARD", "ยังไม่มี Thesis"] and ["DONE", True, "Thesis เก่า 93 วัน"] in cand, json.dumps([p0, cand], ensure_ascii=False))
        check(f"{tag} 10 แถว: '📚 การบ้านหุ้นวันนี้: NOCARD' + ป้ายช่วง Selection US + ปุ่ม ✓ เสร็จ · เปลี่ยนตัว [GL3: ปุ่ม ✓ เดียว → ปุ่ม 5 part ธุรกิจ/ทำไม/Next/ออก/Tier]", "การบ้านหุ้นวันนี้: NOCARD" in r0 and "Selection US" in r0 and js(page, "()=>document.querySelectorAll('[data-hw-part]').length===5 && !!document.querySelector('[data-hw-next]')"), r0)
        ka = kinds(page, "a")
        check(f"{tag} 10 แถวการบ้านอยู่ในกลุ่ม 🟡 ใต้เช็กแผน Sat", ka[:2] == ["sat-daily", "homework"], json.dumps(ka))
        seq = [p0]
        for _ in range(3):
            page.locator('[data-hw-next]').click(); page.wait_for_timeout(350); seq.append(pick())
        check(f"{tag} 10 เปลี่ยนตัว → OLD (Thesis เก่า 60 วัน) → MID (30 วัน) → วนกลับ NOCARD · ไม่มี DONE",
              seq == [["NOCARD", "ยังไม่มี Thesis"], ["OLD", "Thesis เก่า 60 วัน"], ["MID", "Thesis เก่า 30 วัน"], ["NOCARD", "ยังไม่มี Thesis"]], json.dumps(seq, ensure_ascii=False))
        page.locator('[data-hw-next]').click(); page.wait_for_timeout(350)   # → OLD
        hw = settings_db(page)["routineLog"][TODAY]["hw"]
        check(f"{tag} 10 เก็บ routineLog[วัน].hw = {{pick:'OLD', done:false, parts:[]}} [GL3: เพิ่ม parts]", hw == {"pick": "OLD", "done": False, "parts": []}, json.dumps(hw))
        js(page, "()=>{ switchTab('flow'); switchTab('today'); render(); }"); page.wait_for_timeout(400)
        check(f"{tag} 10 สลับแท็บ/วาดใหม่ → ตัวที่เลือกล่าสุดยังอยู่ (คงที่ทั้งวัน)", pick()[0] == "OLD", json.dumps(pick()))
        shot(page, f"td2-homework-{label.replace('px','')}.png") if w in (1440, 390) else None
        page.locator('.tdRow[data-kind="homework"] .tdWhat').click(); page.wait_for_timeout(500)
        st = js(page, "()=>({tab: activeTab, sel: wlSel, sub: wlSub})")
        check(f"{tag} 10 กดชื่อ/แถว → wlOpen('OLD') แท็บ สรุป (WL2 · เดิม Overview 'ov')", st == {"tab": "watch", "sel": "OLD", "sub": "sum"}, json.dumps(st))
        go_today(page)
        # ── 11 ติ๊กเสร็จ ──
        wk0 = txt_of(page, "[data-td-hwweek]")
        for pid in ["biz", "why", "next", "exit", "tier"]:   # GL3: ติ๊กครบ 5 part แทนปุ่ม ✓ เดียว
            page.locator(f'[data-hw-part="{pid}"]').first.click(); page.wait_for_timeout(300)
        page.wait_for_timeout(600)
        hw = settings_db(page)["routineLog"][TODAY]["hw"]
        line = txt_of(page, "[data-hw-donetxt]")
        check(f"{tag} 11 ✓ เสร็จ → แถวหาย · เหลือบรรทัด 'การบ้านวันนี้: OLD ✓' · hw.done = true", "homework" not in kinds(page, "a") and line == "การบ้านวันนี้: OLDW ✓" and hw == {"pick": "OLD", "done": True, "parts": ["biz", "why", "next", "exit", "tier"]}, json.dumps([kinds(page, "a"), line, hw], ensure_ascii=False))
        wk1 = txt_of(page, "[data-td-hwweek]")
        check(f"{tag} 11 ใต้ Routine 'การบ้าน x/y วัน' (สัปดาห์นี้ จ.–วันนี้ · อังคารทำไปแล้ว 1): 1/5 → 2/5", wk0 == "· การบ้าน 1/5 วัน" and wk1 == "· การบ้าน 2/5 วัน", json.dumps([wk0, wk1], ensure_ascii=False))
        shot(page, f"td2-homework-done-{label.replace('px','')}.png") if w == 1440 else None
        js(page, "()=>tdHwDone(false)"); page.wait_for_timeout(400)   # GL3: ยกเลิกทั้งหมดรวดเดียว (บรรทัดไม่ใช่ปุ่มแล้ว)
        hw = settings_db(page)["routineLog"][TODAY]["hw"]
        check(f"{tag} 11 กดบรรทัดยกเลิก → แถวกลับ (OLD) · hw.done = false · การบ้าน 1/5", pick() and pick()[0] == "OLD" and hw == {"pick": "OLD", "done": False, "parts": []} and txt_of(page, "[data-td-hwweek]") == "· การบ้าน 1/5 วัน", json.dumps([pick(), hw]))
        # ── 14 เขียนเฉพาะ routineLog ──
        d_before = json.loads(json.dumps(dump(page)))
        page.locator('[data-hw-next]').click(); page.wait_for_timeout(300)
        page.locator('[data-hw-part="biz"]').first.click(); page.wait_for_timeout(300)   # GL3: ติ๊ก part แทนปุ่ม ✓ เดียว
        page.locator('[data-sat-ok="BTC"]').click(); page.wait_for_timeout(400)
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
            elif d_before.get(k) != d_after.get(k): diffs.append(k)
        check(f"{tag} 14 ติ๊ก/เปลี่ยนตัว/เช็กแผน → เขียนเฉพาะ settings.routineLog ของบัญชีแรก", diffs == ["main.settings.routineLog"], json.dumps(diffs))
        wl_keys = sorted(k for k in d_after if k.startswith("users/testuid/watchlist") or k.startswith("research/"))
        same = all(d_before.get(k) == d_after.get(k) for k in wl_keys) and len(wl_keys) >= 4
        check(f"{tag} 14 ไม่เขียน watchlist / research (เทียบ mock DB ก่อน/หลัง)", same, json.dumps(wl_keys))
        d0 = json.dumps(dump(page), sort_keys=True)
        js(page, "()=>{ renderToday(); render(); switchTab('flow'); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(600)
        check(f"{tag} 14 วาดแท็บใหม่หลายรอบไม่เขียนอะไรเพิ่ม", d0 == json.dumps(dump(page), sort_keys=True))
        check(f"{tag} 10-14 console: ไม่มี error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()
    # ── รีโหลดหน้า: log เดิมมี hw MID → ยังเป็น MID (ไม่คำนวณใหม่) ──
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=hw_doc({TODAY: {"slots": [], "satState": {}, "hw": {"pick": "MID", "done": False}}, "2026-09-29": {"slots": [], "hw": {"pick": "DONE", "done": True}}}), clean=True, extra=hw_extra)
    try:
        go_today(page)
        r = js(page, "()=>{ const r = document.querySelector('.tdRow[data-kind=\"homework\"]'); return r ? [r.querySelector('b').textContent, r.querySelector('[data-hw-reason]').textContent] : null; }")
        check(f"{tag} 10 รีโหลดหน้า (โหลด log เดิมที่เลือก MID) → ยังเป็น MID ไม่เด้งกลับ NOCARD", r == ["MID", "Thesis เก่า 30 วัน"], json.dumps(r, ensure_ascii=False))
    finally:
        browser.close()
    # ── .BK → Selection TH · ticker ซ้ำ ──
    def th_extra(page):
        for tk in ("ABC.BK",):
            seed(page, ["users", "testuid", "watchlist", tk], {"ticker": tk, "market": "TH", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"})
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(clean=True, log={}), clean=True, extra=th_extra)
    try:
        go_today(page)
        r = txt_of(page, '.tdRow[data-kind="homework"]')
        check(f"{tag} 10 หุ้น .BK → ป้ายช่วง Selection TH", r is not None and "ABC.BK" in r and "Selection TH" in r and "Selection US" not in r, str(r))
    finally:
        browser.close()
    # ── 12 Watchlist ว่าง / เสาร์ ──
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(clean=True, log={}), clean=True)
    try:
        go_today(page)
        check(f"{tag} 12 Watchlist ว่าง → ไม่มีแถวการบ้าน", "homework" not in kinds(page, "a") and not js(page, "()=>!!document.querySelector('[data-hw-doneline]')"), json.dumps(kinds(page, "a")))
    finally:
        browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=hw_doc({}), clean=True, extra=hw_extra, iso=CLK_SAT)
    try:
        go_today(page)
        g = js(page, "()=>({hw: !!document.querySelector('.tdRow[data-kind=\"homework\"]'), sat: !!document.querySelector('.tdRow[data-kind=\"sat-daily\"]'), focus: !!document.querySelector('[data-td-focus]'), off: !!document.querySelector('[data-td-off]')})")
        check(f"{tag} 12 เสาร์ → ไม่มีแถวการบ้าน / เช็กแผน Sat / Focus", g == {"hw": False, "sat": False, "focus": False, "off": True}, json.dumps(g))
        lg = (settings_db(page).get("routineLog") or {})
        check(f"{tag} 12 เสาร์ → ไม่เขียน pick การบ้านลง log", not any("hw" in v for v in lg.values()), json.dumps(lg))
    finally:
        browser.close()


# ───────────────────────── 13 มือถือ (Routine พับ · Sat 2×2 · ปุ่ม · ไม่ซ้อน) ─────────────────────────
def mobile_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        vs = vis_slots(page)
        fold = txt_of(page, "[data-td-fold]")
        check(f"{tag} 13 Routine แสดงเฉพาะ 'ตอนนี้' + 'ยังไม่ถึง' (selUS2 · planUS · selTH)", vs == ["selUS2", "planUS", "selTH"], json.dumps(vs))
        check(f"{tag} 13 ช่องที่ผ่านแล้วพับเป็นบรรทัด 'ผ่านแล้ว 2 ช่วง · ✓ 1' (09:00 ติ๊กไว้)", fold == "ผ่านแล้ว 2 ช่วง · ✓ 1", str(fold))
        page.locator('[data-td-fold]').click(); page.wait_for_timeout(200)
        vs2 = vis_slots(page)
        check(f"{tag} 13 กดบรรทัดพับ → กางครบ 5 ช่อง (ติ๊กย้อนได้)", vs2 == ["planTH", "selUS1", "selUS2", "planUS", "selTH"], json.dumps(vs2))
        page.locator('[data-tick-slot="selUS1"]').click(); page.wait_for_timeout(500)
        check(f"{tag} 13 ติ๊กย้อนช่อง 11:00 ได้ · บรรทัดพับอัปเดตเป็น '✓ 2'", "ผ่านแล้ว 2 ช่วง · ✓ 2" == txt_of(page, "[data-td-fold]") and "selUS1" in settings_db(page)["routineLog"][TODAY]["slots"])
        page.locator('[data-tick-slot="selUS1"]').click(); page.wait_for_timeout(300)
        page.locator('[data-td-fold]').click(); page.wait_for_timeout(200)
        check(f"{tag} 13 กดอีกครั้ง → พับกลับเหลือ 3 ช่อง", vis_slots(page) == ["selUS2", "planUS", "selTH"])
        # ช่อง Sat 2×2
        pos = js(page, "()=>[...document.querySelectorAll('.tdAs')].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.right)]; })")
        check(f"{tag} 13 ช่อง Sat (3 ที่เลือก) ตาราง 2 คอลัมน์ (ซ้าย 2 ค่า · บน 2 ค่า · WA1fix: เดิม 4 ช่อง 2×2)", len(pos) == 3 and len({p[0] for p in pos}) == 2 and len({p[1] for p in pos}) == 2, json.dumps(pos))
        sz = js(page, "()=>[...document.querySelectorAll('.tdAs .b, .tdHb')].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })")
        check(f"{tag} 13 ปุ่ม ✓ ✕ และการบ้านสูง ≥ 34px · กว้าง ≥ 34px", len(sz) >= 7 and all(s[0] >= 34 and s[1] >= 34 for s in sz), json.dumps(sz))   # GL3: ปุ่ม ✓ เดียวหาย → 9 ปุ่ม (Sat 8 + เปลี่ยนตัว) · WA1fix: Sat 3 ตลาด = 6 + เปลี่ยนตัว = 7
        szp = js(page, "()=>[...document.querySelectorAll('.tdHp')].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })")
        check(f"{tag} 13 [GL3] ปุ่ม part ทั้ง 5 สูง ≥ 32px · กว้าง > 0", len(szp) == 5 and all(s[0] > 0 and s[1] >= 32 for s in szp), json.dumps(szp))
        hit = js(page, """()=>[...document.querySelectorAll('.tdAs .b, .tdHb')].map(b=>{ b.scrollIntoView({block:'center'}); const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); return !!e && (e === b || b.contains(e)); })""")
        check(f"{tag} 13 elementFromPoint ของปุ่ม ✓ ✕ เสร็จ เปลี่ยน = ปุ่มนั้น", hit and all(hit), json.dumps(hit))
        ov = P.overflow_x(page, [".tdWrap", ".tdRow", ".tdRt", ".tdSs", ".tdAs", ".tdWhat", ".tdFocus", ".tdOkLine", ".tdHwBtns"])
        check(f"{tag} 13 ไม่ล้นแนวนอน (ราย element)", not ov, json.dumps(ov))
        js(page, "()=>window.scrollTo(0,0)")
        page.locator('[data-sat-ok="XAUUSD"]').click(); page.wait_for_timeout(400)
        ov2 = P.overflow_x(page, [".tdWrap", ".tdFocus", ".tdRow"])
        fh = js(page, "()=>{ const f = document.querySelector('[data-td-focus]'); return [f.getBoundingClientRect().height, parseFloat(getComputedStyle(f).lineHeight) || 20]; }")
        check(f"{tag} 13 บรรทัด Focus ไม่ล้น · สูงไม่เกิน 1 บรรทัดเมื่อมี ✓ + ยังไม่ดู", not ov2 and fh[0] <= fh[1] * 1.6, json.dumps([ov2, fh]))
        bad = overlap_check(page, ".tdRow, .tdRt, .tdSs")
        check(f"{tag} 13 ข้อความกับป้ายในทุกแถวไม่ซ้อนกัน (bounding box · แถวงาน · Routine)", not bad, json.dumps(bad, ensure_ascii=False))
        check(f"{tag} 13 ไม่มี console error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()
    # ข้อ 7: หลัง 20:00 → บรรทัดพับ + จบวัน
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, iso=CLK_LATE)
    try:
        go_today(page)
        fold = txt_of(page, "[data-td-fold]")
        check(f"{tag} 13 หลัง 20:00 (ไม่มีช่องที่ยังไม่ถึง) → บรรทัดพับ 'ผ่านแล้ว 5 ช่วง · ✓ 1 · จบวัน' · ไม่มีช่องแสดง", fold == "ผ่านแล้ว 5 ช่วง · ✓ 1 · จบวัน" and vis_slots(page) == [], json.dumps([fold, vis_slots(page)], ensure_ascii=False))
    finally:
        browser.close()


def desktop_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        vs = vis_slots(page)
        fold_vis = js(page, "()=>{ const f = document.querySelector('[data-td-fold]'); return f ? getComputedStyle(f).display !== 'none' : false; }")
        check(f"{tag} 7 จอใหญ่: Routine เหมือนเดิม (แสดงครบ 5 ช่อง · ไม่มีบรรทัดพับ)", len(vs) == 5 and not fold_vis, json.dumps([vs, fold_vis]))
        pos = js(page, "()=>[...document.querySelectorAll('.tdAs')].map(e=>Math.round(e.getBoundingClientRect().top))")
        check(f"{tag} 3 จอใหญ่: ช่อง Sat 3 ช่อง (ที่เลือก) แถวเดียว", len(pos) == 3 and len(set(pos)) == 1, json.dumps(pos))
        hit = js(page, """()=>[...document.querySelectorAll('.tdAs .b')].map(b=>{ b.scrollIntoView({block:'center'}); const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); return !!e && (e === b || b.contains(e)); })""")
        sz = js(page, "()=>[...document.querySelectorAll('.tdAs .b')].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })")
        check(f"{tag} 6 ปุ่ม ✓ ✕ ≥ 34px · elementFromPoint = ปุ่ม", hit and all(hit) and all(s[0] >= 34 and s[1] >= 34 for s in sz), json.dumps([hit, sz]))
        bad = overlap_check(page, ".tdRow, .tdRt, .tdSs")
        check(f"{tag} 8 จอใหญ่: ข้อความกับป้ายไม่ซ้อนกัน", not bad, json.dumps(bad, ensure_ascii=False))
        check(f"{tag} 7 console: ไม่มี error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()


# ───────────────────────── TD2-fix: Focus ≤ 2 + แก้ ─────────────────────────
def fix_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    sh = lambda n: shot(page, f"td2fix-{n}-{label.replace('px','')}.png") if w in (1440, 390) else None
    rowv = lambda: js(page, "()=>!!document.querySelector('.tdRow[data-kind=\"sat-daily\"]')")
    state = lambda: (settings_db(page).get("routineLog") or {}).get(TODAY, {}).get("satState")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_today(page)
        page.locator('[data-sat-ok="XAUUSD"]').click(); page.wait_for_timeout(350)
        page.locator('[data-sat-ok="BTC"]').click(); page.wait_for_timeout(500)
        fc = txt_of(page, "[data-td-focus]")
        check(f"{tag} F1 ✓ XAU + ✓ BTC → แถวหาย · Focus line 'XAU BTC' · satState ok 2 ตัว", (not rowv()) and fc is not None and "XAU BTC" in fc and state() == {"XAUUSD": "ok", "BTC": "ok"}, json.dumps([fc, state()], ensure_ascii=False))
        e = js(page, "()=>{ const b = document.querySelector('[data-sat-edit]'); if(!b) return null; const r = b.getBoundingClientRect(); const cs = getComputedStyle(b); return {t: b.textContent.trim(), h: r.height, bg: cs.backgroundColor, bd: cs.borderTopWidth, col: cs.color, fs: cs.fontSize}; }")
        check(f"{tag} F2 ลิงก์ 'แก้' ท้ายบรรทัด Focus: ตัวหนังสือเล็กสีเทา ไม่มีกรอบ/พื้น · สูง ≥ 34px", e and e["t"] == "แก้" and e["h"] >= 34 and e["bg"] == "rgba(0, 0, 0, 0)" and e["bd"] == "0px", json.dumps(e))
        sh("focus-max")
        page.locator('[data-sat-edit]').click(); page.wait_for_timeout(400)
        dis = js(page, "()=>['BRENT'].map(i=>{ const b = document.querySelector('[data-sat-ok=\"'+i+'\"]'); return [b.disabled, b.title]; })")
        want_t = "Focus ได้สูงสุด 2 ตัว/วัน — เอา ✓ ตัวอื่นออกก่อน"
        check(f"{tag} F2 กด 'แก้' → แถวกลับ · ปุ่ม ✓ ของ Brent disabled (WA1fix: S50 ไม่ได้เลือก) + title ถูก · ป้าย 'Focus 2/2'", rowv() and all(d[0] and d[1] == want_t for d in dis) and txt_of(page, "[data-sat-count]") == "Focus 2/2" and not js(page, "()=>!!document.querySelector('[data-sat-edit]')"), json.dumps([dis, txt_of(page, "[data-sat-count]")], ensure_ascii=False))
        sh("edit")
        before = json.dumps(state(), sort_keys=True)
        js(page, "()=>document.querySelector('[data-sat-ok=\"BRENT\"]').click()"); page.wait_for_timeout(400)
        check(f"{tag} F2 กดปุ่ม ✓ ที่ disabled → state ไม่เปลี่ยน", json.dumps(state(), sort_keys=True) == before, json.dumps(state()))
        page.locator('[data-sat-no="BRENT"]').click(); page.wait_for_timeout(450)
        check(f"{tag} F2 ✕ Brent ยังกดได้ → 'no' (แถวยังเปิดเพราะกด แก้)", state().get("BRENT") == "no" and rowv(), json.dumps(state()))
        js(page, "()=>tdSatMark('BRENT','ok')"); page.wait_for_timeout(450)
        check(f"{tag} F3 เรียก tdSatMark('BRENT','ok') ตรงขณะ ✓ ครบ 2 → satState.BRENT ยังเป็น no (ไม่เป็น ok)", state().get("BRENT") == "no" and len([v for v in state().values() if v == "ok"]) == 2, json.dumps(state()))
        page.locator('[data-sat-ok="BTC"]').click(); page.wait_for_timeout(450)
        en = js(page, "()=>['BRENT'].map(i=>document.querySelector('[data-sat-ok=\"'+i+'\"]').disabled)")
        check(f"{tag} F4 เอา ✓ BTC ออก → ปุ่ม ✓ เปิด · ป้าย 'Focus 1/2'", en == [False] and txt_of(page, "[data-sat-count]") == "Focus 1/2", json.dumps([en, txt_of(page, "[data-sat-count]")]))
        page.locator('[data-sat-edit-done]').click(); page.wait_for_timeout(400)
        check(f"{tag} F4 กด 'เสร็จ' → แถวยังอยู่ (✓ 1 · BTC ยังไม่ตัดสิน · Brent ✕)", rowv() and not js(page, "()=>!!document.querySelector('[data-sat-edit-done]')"))
        # F5 ✓1 + ✕3 → แถวหาย + แก้
        page.locator('[data-sat-no="BTC"]').click(); page.wait_for_timeout(350)
        check(f"{tag} F5 ✓ 1 + ✕ 2 (ตัดสินครบ 3 ที่เลือก) (ตัดสินครบ) → แถวหาย · Focus line มีปุ่ม 'แก้'", (not rowv()) and js(page, "()=>!!document.querySelector('[data-td-focus] [data-sat-edit]')"), json.dumps(state()))
        page.locator('[data-sat-edit]').click(); page.wait_for_timeout(350)
        page.locator('[data-sat-edit-done]').click(); page.wait_for_timeout(350)
        check(f"{tag} F4 'แก้' แล้ว 'เสร็จ' เมื่อเงื่อนไขหายครบ → แถวพับกลับ", not rowv())
        check(f"{tag} F1-5 console: ไม่มี error", not pe and not ce, "; ".join((pe + ce)[:3]))
    finally:
        browser.close()
    # F5 ทุกตัว ✕
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(log={TODAY: {"slots": [], "satState": {"XAUUSD": "no", "BTC": "no", "S50": "no", "BRENT": "no"}}}))
    try:
        go_today(page)
        check(f"{tag} F5 ทุกตัว ✕ → 'วันนี้ไม่มีแผน Sat' + ปุ่ม 'แก้' → กดแล้วแถวกลับ", txt_of(page, "[data-td-focus]") == "วันนี้ไม่มีแผน Sat แก้" and (page.locator('[data-sat-edit]').click() or page.wait_for_timeout(350) or rowv()))
    finally:
        browser.close()
    # F6 log เก่า ✓ 3 ตัว
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=P.doc38(log={TODAY: {"slots": [], "sat": ["XAUUSD", "BTC", "BRENT"]}}))   # WA1fix: ✓ 3 ตัวต้องอยู่ใน pick (XAU · BTC · Brent)
    try:
        go_today(page)
        d0 = json.dumps(dump(page), sort_keys=True)
        page.locator('[data-sat-edit]').click(); page.wait_for_timeout(350)
        info = js(page, "()=>({ok: [...document.querySelectorAll('.tdAs.ok')].length, cnt: document.querySelector('[data-sat-count]').textContent, warn: document.querySelector('[data-sat-count]').classList.contains('warn'), brent: !document.querySelector('[data-sat-ok=\"BRENT\"]').disabled, col: getComputedStyle(document.querySelector('[data-sat-count]')).color})")
        check(f"{tag} F6 log เก่า sat:[3 ตัว] → แสดง ✓ 3 · ป้าย 'Focus 3/2' สีเหลือง · ปุ่ม ✓ Brent (ที่ติ๊กไว้) กดเอาออกได้ (WA1fix: ไม่มีตัวที่ 4 ให้ตรวจ disabled — เคส disabled อยู่ที่ F2)", info["ok"] == 3 and info["cnt"] == "Focus 3/2" and info["warn"] and info["brent"], json.dumps(info))
        check(f"{tag} F6 ไม่เขียน DB จนกว่าจะกด (เปิดดู/กด แก้ ไม่เขียน)", d0 == json.dumps(dump(page), sort_keys=True))
        page.locator('[data-sat-ok="BRENT"]').click(); page.wait_for_timeout(450)
        st = state()
        check(f"{tag} F6 เอา ✓ ออกเอง → ได้ (เหลือ 2 ตัว) แล้วเขียนรูปใหม่", st == {"XAUUSD": "ok", "BTC": "ok"}, json.dumps(st))
    finally:
        browser.close()
    if w <= 480:
        browser, context, page, ce, pe, dialogs = launch(pw, w, h)
        try:
            go_today(page)
            page.locator('[data-sat-ok="XAUUSD"]').click(); page.wait_for_timeout(350)
            page.locator('[data-sat-ok="BTC"]').click(); page.wait_for_timeout(450)
            ov = P.overflow_x(page, [".tdWrap", ".tdFocus", ".tdEdit", ".tdRow"])
            hit = js(page, "()=>{ const b = document.querySelector('[data-sat-edit]'); b.scrollIntoView({block:'center'}); const r = b.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); return !!e && (e === b || b.contains(e)); }")
            fh = js(page, "()=>{ const f = document.querySelector('[data-td-focus]'); return [f.getBoundingClientRect().height, parseFloat(getComputedStyle(f).lineHeight) || 20]; }")
            check(f"{tag} F7 มือถือ: ปุ่ม 'แก้' ไม่ล้น · elementFromPoint = ปุ่ม · บรรทัด Focus ไม่เกิน 1 บรรทัด (✓ 2 + ยังไม่ดู)", not ov and hit and fh[0] <= fh[1] * 1.6, json.dumps([ov, hit, fh]))
            bad = overlap_check(page, ".tdFocus")
            check(f"{tag} F7 บรรทัด Focus: ข้อความกับปุ่มไม่ซ้อน", not bad, json.dumps(bad, ensure_ascii=False))
            page.locator('[data-sat-edit]').click(); page.wait_for_timeout(350)
            bad = overlap_check(page, ".tdRow")
            ov = P.overflow_x(page, [".tdWrap", ".tdRow", ".tdAs"])
            check(f"{tag} F7 แถวในโหมดแก้ (ปุ่ม เสร็จ): ไม่ล้น ไม่ซ้อน", not bad and not ov, json.dumps([bad, ov], ensure_ascii=False))
        finally:
            browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px"), (430, 932, "430px")):
            quiet_tests(pw, w, h, label)
            abnormal_tests(pw, w, h, label)
            review_tests(pw, w, h, label)
            sat_tests(pw, w, h, label)
            fix_tests(pw, w, h, label)
            hw_tests(pw, w, h, label)
            if w <= 480: mobile_tests(pw, w, h, label)
            else: desktop_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 39 / TD2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
