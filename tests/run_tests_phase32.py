#!/usr/bin/env python3
"""RC2 → WL2 — ปุ่ม "เติมจาก Thesis" ในบล็อก Tier (เดิม RC2 "เติมจาก Research" จาก research_card · ตอนนี้จาก thesis.tier_inputs ของ watchlist/{T}) · เทส 32
mock Firestore · 1440px + 430px · บัญชี US (main) · seed watchlist 3 ตัว (thesis): TGRW (tier_inputs ครบ 11 ช่อง) · TOLD (มี 4 ช่อง) · TNONE (ไม่มี tier_inputs)
ภาพเก็บที่ tests/screenshots/rc2-*.png
รัน: python3 run_tests_phase32.py [/path/to/index.html]"""
import copy, json, os, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase26 as p26

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
results = []
txt = p24.txt; go = p24.go_stock; ex = p24.ex; card_sel = p26.card_sel
launch = p26.launch; doc26 = p26.doc26; FF_OPEN = p26.FF_OPEN
AS_OF = "2026-09-20"
BASE = json.load(open(os.path.join(HERE, "..", "avgo-research-card-th.json"), encoding="utf-8"))


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot_el(page, sel, name, tall=False):
    """tall=True: ขยาย viewport ชั่วคราวให้เห็นทั้งบล็อก (ปุ่ม + ข้อความ + บรรทัดผล) แล้วคืนขนาดเดิม"""
    vp = page.viewport_size
    try:
        if tall: page.set_viewport_size({"width": vp["width"], "height": 2400})
        page.wait_for_timeout(500)
        page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e: print("shot fail", name, e)
    finally:
        if tall: page.set_viewport_size(vp); page.wait_for_timeout(200)


def m(name, value, unit="%", period="TTM"):
    return {"name": name, "value": value, "unit": unit, "period": period, "source_url": "https://www.sec.gov/Archives/edgar/data/1/x.htm"}


OTHERS = [m("รายได้รวม", "29591", "ล้านดอลลาร์", "Q3 FY2026"), m("รายได้ชิป AI", "6500", "ล้านดอลลาร์", "Q3 FY2026"), m("รายได้ซอฟต์แวร์", "6800", "ล้านดอลลาร์", "Q3 FY2026"),
          m("สัดส่วนลูกค้า 5 รายใหญ่", "40", "%", "FY2025"), m("เงินสดคงเหลือ", "11000", "ล้านดอลลาร์", "Q3 FY2026")]
TIER7 = [m("ROIC = NOPAT ÷ IC [T:roic]", "24.5"), m("ND/EBITDA [T:nd]", "-0.3", "x"), m("FCF conversion [T:fcf]", "92"), m("รายได้โต TTM [T:rev]", "25.3"),
         m("CAGR รายได้ 3 ปี [T:cagr]", "18.0"), m("Op margin [T:opm]", "12.0 / 10.0", "%", "FY2026 / FY2025"), m("เช็ก 3 ข้อ [T:chk]", "yes/yes/yes", "-", "FY2026")]


def rcard(ticker, metrics):
    c = copy.deepcopy(BASE); c["ticker"] = ticker; c["as_of"] = AS_OF; c["metrics"] = metrics; return c


TH_FX = json.load(open(os.path.join(HERE, "fixtures", "avgo_thesis.json"), encoding="utf-8"))


def ti(v, tag="C"): return {"v": v, "tag": tag, "period": "FY2026", "src": "ทดสอบ"}


def thesis(sym, tier_inputs):
    t = copy.deepcopy(TH_FX); t["sym"] = sym; t.pop("log", None); t["date"] = AS_OF; t["asOf"] = AS_OF; t["tier_inputs"] = tier_inputs; return t


def seed(page):
    """WL2 — Tier metrics มาจาก thesis.tier_inputs ใน watchlist/{T}"""
    full = {"roic": ti(24.5), "ndEbitda": ti(-0.3), "fcfConv": ti(92), "revGrowth": ti(25.3), "revCagr3": ti(18.0), "opMargin": ti(12.0), "opMarginPrev": ti(10.0),
            "fcfPositive3y": ti(True, "F"), "capitalReturn": ti(True, "F"), "ocfPositive": ti(True, "F"), "netCash": ti(True)}
    old = {"roic": ti(24.5), "ndEbitda": ti(1.2), "fcfConv": ti(92), "netCash": ti(False)}
    docs = {"TGRW": thesis("TGRW", full), "TOLD": thesis("TOLD", old), "TNONE": thesis("TNONE", {})}
    for k, t in docs.items():
        page.evaluate("([k,t])=>wlCol().doc(k).set({ticker:k, market:'US', port:'core', note:'', industry:'', added_at:'2026-01-01T00:00:00.000Z', thesis:t, thesis_log:[], thesis_history:[], thesis_hits:{}})", [k, t])
        page.evaluate("([k,d])=>window.firebase.__mockDb.__seedDoc(['research',k], d)", [k, {"ticker": k, "name": k + " Co"}])
    page.evaluate("() => rsLoad(true)"); page.wait_for_timeout(400)


def tick(page, key, v, attr="data-tk"):
    cur = page.evaluate("([a,k])=>{ const on=[...document.querySelectorAll('['+a+'=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; }", [attr, key])
    if cur == v: return
    page.click(f'[{attr}="{key}"] button[data-v="{(1 if cur else 0) if v is None else (1 if v else 0)}"]')


def tkv(page, key, attr="data-tk"):
    return page.evaluate("([a,k])=>{ const on=[...document.querySelectorAll('['+a+'=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; }", [attr, key])


def val(page, sel): return page.input_value(sel)
def vis(page, sel): return page.locator(sel).count() > 0 and page.locator(sel).first.is_visible()
def new_form(page, ticker, acct="main"):
    page.evaluate("(a)=>coreNewOpen(a)", acct)
    page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
    page.fill("#cnTicker", ticker); page.wait_for_timeout(80)


NUMS = {"#tiRoic": "24.5", "#tiNd": "-0.3", "#tiFcf": "92", "#tiRev": "25.3", "#tiCagr": "18", "#tiOpm": "12", "#tiOpmPrev": "10"}
TKS = ("fcf3y", "capret", "ocf", "netcash")


def fill_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    old_card = p24.card("c1", "main", "TGRW", tier="B")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards={"c1": old_card}, ff=FF_OPEN())
    try:
        go(page); seed(page)
        # 1 ─ TGRW
        new_form(page, "TGRW")
        check(f"{tag} 1 แผน Core ใหม่ ticker TGRW → เห็นปุ่ม 'เติมจาก Thesis'", vis(page, "#tiFillTh") and "เติมจาก Thesis" in (txt(page, "#tiFillTh") or ""))
        shot_el(page, "[data-c-tierblock]", f"rc2-fill-before-{w}.png", tall=True)
        page.click("#tiFillTh"); page.wait_for_timeout(120)
        got = {s: val(page, s) for s in NUMS}
        check(f"{tag} 1 กดเติม → ช่องตัวเลขตรงค่า (24.5 · -0.3 · 92 · 25.3 · 18 · 12 · 10)", got == NUMS, json.dumps(got))
        tk = {k: tkv(page, k) for k in TKS}
        check(f"{tag} 1 ติ๊ก FCF3y/ปันผล/OCF = ใช่ · เงินสดสุทธิ = ใช่ (ND ≤ 0)", tk == {"fcf3y": True, "capret": True, "ocf": True, "netcash": True}, json.dumps(tk))
        msg = txt(page, "#tiFillMsg") or ""
        check(f"{tag} 1 ข้อความ 'เติม 11 ช่อง · ข้าม 0 ช่องที่กรอกแล้ว · จาก Thesis 20 ก.ย. (ข้อมูล ณ 20 ก.ย.)'", msg == "เติม 11 ช่อง · ข้าม 0 ช่องที่กรอกแล้ว · จาก Thesis 20 ก.ย. (ข้อมูล ณ 20 ก.ย.)", msg)
        for key in ("substitute", "customerMigrating", "singleProduct"): tick(page, key, False, "data-g5")
        page.wait_for_timeout(100)
        gl = txt(page, '[data-c-lensline="growth"]') or ""
        check(f"{tag} 1 ตอบ Gate 5 'ไม่' ×3 เอง → บรรทัด Growth = 'Growth: ✓ ผ่าน'", gl == "Growth: ✓ ผ่าน", gl)
        shot_el(page, "[data-c-tierblock]", f"rc2-fill-after-{w}.png", tall=True)
        # ทับค่า/ติ๊กซ้ำ: กดอีกครั้ง = ไม่มีช่องว่างให้เติม
        page.click("#tiFillTh"); page.wait_for_timeout(80)
        check(f"{tag} 1 กดซ้ำ → 'ไม่มีช่องว่างให้เติม' · ค่าเดิมไม่เปลี่ยน", (txt(page, "#tiFillMsg") or "") == "ไม่มีช่องว่างให้เติม" and {s: val(page, s) for s in NUMS} == NUMS)
        # 2 ─ ROIC = 5
        new_form(page, "TGRW"); page.fill("#tiRoic", "5"); page.click("#tiFillTh"); page.wait_for_timeout(100)
        msg = txt(page, "#tiFillMsg") or ""
        check(f"{tag} 2 กรอก ROIC = 5 ก่อนกด → ROIC ยัง 5 · ข้อความ 'ข้าม 1 ช่อง' · 'เติม 10 ช่อง'", val(page, "#tiRoic") == "5" and "ข้าม 1 ช่อง" in msg and msg.startswith("เติม 10 ช่อง") and val(page, "#tiFcf") == "92", msg)
        # 3 ─ OCF = ไม่ใช่
        new_form(page, "TGRW"); tick(page, "ocf", False); page.click("#tiFillTh"); page.wait_for_timeout(100)
        msg = txt(page, "#tiFillMsg") or ""
        check(f"{tag} 3 ติ๊ก OCF = ไม่ใช่ ก่อนกด → ยังเป็นไม่ใช่ · ข้าม 1 ช่อง · ติ๊กอื่นเติมตามปกติ", tkv(page, "ocf") is False and tkv(page, "fcf3y") is True and "ข้าม 1 ช่อง" in msg, msg)
        # 4 ─ Gate 5 / ปุ่ม Tier / เหตุผล ไม่เปลี่ยน
        new_form(page, "TGRW")
        tick(page, "substitute", True, "data-g5"); tick(page, "singleProduct", False, "data-g5")
        page.click("#cnTierG"); page.wait_for_timeout(60); page.fill("#cnReason", "เหตุผลของฉัน"); page.wait_for_timeout(60)
        snap = lambda: json.dumps({"g5": [tkv(page, k, "data-g5") for k in ("substitute", "customerMigrating", "singleProduct")],
                                   "pick": page.evaluate("()=>[...document.querySelectorAll('.ccSegTier button.on')].map(b=>b.dataset.pick)"),
                                   "reason": page.evaluate("()=>(document.getElementById('cnReason')||{}).value")}, ensure_ascii=False)
        before = snap(); page.click("#tiFillTh"); page.wait_for_timeout(100)
        check(f"{tag} 4 Gate 5 / ปุ่ม Tier / เหตุผล ไม่เปลี่ยนหลังกด", before == snap() and val(page, "#tiRoic") == "24.5", before + " → " + snap())
        # 5 ─ TOLD
        new_form(page, "TOLD"); check(f"{tag} 5 TOLD (thesis มี tier_inputs 4 ช่อง) → เห็นปุ่ม", vis(page, "#tiFillTh"))
        page.click("#tiFillTh"); page.wait_for_timeout(100)
        growth_empty = all(val(page, s) == "" for s in ("#tiRev", "#tiCagr", "#tiOpm", "#tiOpmPrev")) and all(tkv(page, k) is None for k in ("fcf3y", "capret", "ocf"))
        check(f"{tag} 5 TOLD → เติม ROIC 24.5 / ND 1.2 / FCF 92 + netcash = ไม่ใช่ (จาก ND) · ช่อง Growth ยังว่าง",
              (val(page, "#tiRoic"), val(page, "#tiNd"), val(page, "#tiFcf")) == ("24.5", "1.2", "92") and tkv(page, "netcash") is False and growth_empty, txt(page, "#tiFillMsg") or "")
        check(f"{tag} 5 TOLD ข้อความ 'เติม 4 ช่อง'", (txt(page, "#tiFillMsg") or "").startswith("เติม 4 ช่อง"), txt(page, "#tiFillMsg") or "")
        # 6 ─ TNONE / ไม่อยู่ Watchlist / เปลี่ยน ticker
        new_form(page, "TNONE")
        a = vis(page, "#tiFillTh")
        page.fill("#cnTicker", "ZZNOPE"); page.wait_for_timeout(80)
        b = vis(page, "#tiFillTh")
        check(f"{tag} 6 TNONE (thesis ไม่มี tier_inputs) และ ticker ที่ไม่อยู่ Watchlist → ไม่เห็นปุ่ม", not a and not b, json.dumps([a, b]))
        page.fill("#cnTicker", "TNONE"); page.wait_for_timeout(60); page.fill("#cnTicker", "TGRW"); page.wait_for_timeout(80)
        check(f"{tag} 6 เปลี่ยน ticker TNONE → TGRW ในฟอร์ม → ปุ่มขึ้น", vis(page, "#tiFillTh"))
        page.click("#tiFillTh"); page.wait_for_timeout(60); page.fill("#cnTicker", "TOLD"); page.wait_for_timeout(80)
        check(f"{tag} 6 เปลี่ยน ticker → ข้อความผลเติมของ ticker เดิมถูกล้าง", (txt(page, "#tiFillMsg") or "") == "")
        # 7 ─ sheet Tier… ของการ์ดเดิม
        page.evaluate("()=>coreSheetClose()"); page.wait_for_timeout(200)
        go(page); p24.menu_click(page, "c1", "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
        ok7 = vis(page, "#tiFillTh")
        page.click("#tiFillTh"); page.wait_for_timeout(100)
        check(f"{tag} 7 sheet Tier… ของการ์ดเดิม TGRW → ปุ่มใช้ได้เหมือนกัน (เติมช่อง + ข้อความ)",
              ok7 and val(page, "#tiRoic") == "24.5" and tkv(page, "netcash") is True and (txt(page, "#tiFillMsg") or "").startswith("เติม 11 ช่อง"), txt(page, "#tiFillMsg") or "")
        if w <= 700:
            ov = page.evaluate("""()=>{ const W = window.innerWidth, bad = [];
              ['tiFillRow','tiFillTh','tiFillMsg'].forEach(id=>{ const e = document.getElementById(id), r = e.getBoundingClientRect();
                if(r.right > W + 1 || r.left < -1 || e.scrollWidth > e.clientWidth + 1) bad.push(id + ':' + Math.round(r.left) + '-' + Math.round(r.right) + '/' + e.scrollWidth + '>' + e.clientWidth); });
              const sh = document.querySelector('.core-sheet'); if(sh && sh.scrollWidth > sh.clientWidth + 1) bad.push('sheet'); return bad; }""")
            check(f"{tag} 9 430px: แถวปุ่ม + ข้อความไม่ล้นแนวนอน (เช็กราย element)", ov == [], json.dumps(ov))
        else:
            check(f"{tag} 9 1440px: แถวปุ่ม + ข้อความอยู่ในกรอบ sheet", page.evaluate("""()=>{ const s = document.querySelector('.core-sheet').getBoundingClientRect(), r = document.getElementById('tiFillRow').getBoundingClientRect(); return r.left >= s.left - 1 && r.right <= s.right + 1; }"""))
        check(f"{tag} 9 ไม่มี console error (เติมจาก Thesis)", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def metrics_checks(pw, w, h, label):
    """WL2 — เดิม: แท็บ Research แสดง metric + ชิป 'Tier' · ตอนนี้ไม่มีแท็บ Research/การ์ด metric แล้ว → เช็กว่า "ไม่มีแล้ว" + การ์ด Thesis ไม่ล้นจอ"""
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page); seed(page)
        page.evaluate("() => { switchTab('watch'); wlSetView('wl'); wlOpen('TGRW'); wlSetSub('rs'); }"); page.wait_for_timeout(300)
        r = page.evaluate("""()=>({metrics: document.querySelectorAll('.rcMetric, .rcTierTag, .rcCard').length, bracket: document.getElementById('tabWatch').innerText.includes('[T:'),
          tabs: [...document.querySelectorAll('.wlDHead .ltTab')].map(b=>b.textContent.trim()), research: [...document.querySelectorAll('.wlDHead button')].some(b=>/^Research$/.test(b.textContent.trim())), sub: wlSub})""")
        check(f"{tag} 8 แท็บ Research / การ์ด metric / ชิป 'Tier' ไม่มีแล้ว (WL2) · wlSetSub('rs') = แท็บ สรุป · ไม่มี '[T:' บนจอ",
              r["metrics"] == 0 and not r["bracket"] and not r["research"] and r["tabs"] == ["สรุป", "มุมมอง", "ธุรกิจ", "ทำไมซื้อ", "ติดตาม", "ออกเมื่อ"] and r["sub"] == "sum", json.dumps(r, ensure_ascii=False))
        check(f"{tag} 8 ไม่มีฟังก์ชัน/ตัวแปร Research Card เหลือในหน้า (rcTierMetrics · rcCardHtml · rcMerge)", page.evaluate("()=>typeof rcTierMetrics==='undefined' && typeof rcCardHtml==='undefined' && typeof rcMerge==='undefined' && typeof rcTrimJson==='undefined'"))
        shot_el(page, ".wlDBody", f"rc2-research-metrics-{w}.png")
        if w <= 700:
            ov = page.evaluate("""()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('.wlDPanel, .wlDBody, .ltSum, .ltDecide').forEach((e,i)=>{ const r = e.getBoundingClientRect(); if(r.right > W + 1 || e.scrollWidth > e.clientWidth + 1) bad.push(i); }); return bad; }""")
            check(f"{tag} 9 430px: การ์ด Thesis (แทนช่อง metric) ไม่ล้นแนวนอน", ov == [], json.dumps(ov))
        check(f"{tag} 9 ไม่มี console error (การ์ด Thesis)", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            fill_checks(pw, w, h, label)
            metrics_checks(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:400])
        sys.exit(1)


if __name__ == "__main__":
    main()
