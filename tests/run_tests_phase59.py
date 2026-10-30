#!/usr/bin/env python3
"""VW1 — กราฟ TradingView (ลิงก์ภาพ) ในการ์ด Sat Strategy + โน้ต 3 มุม (Event · Fund. · Tech) ของหุ้น Watchlist / Candidate · เทส 59
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-09 (ศ.) เวลาไทย · ดัก request ภาพ s3.tradingview.com ด้วย PNG ปลอม
ภาพ tests/screenshots/vw1-{sat-chart,sat-empty,wl-view,wl-tech-open,cand-open,lightbox}-{1440,390}.png
รัน: python3 run_tests_phase59.py"""
import base64, copy, json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase40 as P40
import run_tests_phase41 as P41
import run_tests_phase44 as P44
import run_tests_phase56 as G
import run_tests_phase58 as GL3
import run_tests_phase55 as P55

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-VW1.html"))
results = []
js = P37.js
CLK = "2026-10-09T05:00:00Z"        # ศ. 12:00 ไทย
TODAY = "2026-10-09"
WK = "2026-10-04"                   # อาทิตย์เริ่มสัปดาห์ของ 9 ต.ค.
PWK = "2026-09-27"
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
TV1 = "https://www.tradingview.com/x/pSb8OxWO/"
TV2 = "https://www.tradingview.com/x/Ab12Cd34/"
SNAP1 = "https://s3.tradingview.com/snapshots/p/pSb8OxWO.png"
BAD_MSG = "ลิงก์นี้ไม่ใช่ภาพ TradingView (📷 → Copy link)"
RULE_MSG = "ยังอ่านโน้ตไม่ได้ (ต้องเพิ่ม Firestore rule stockNotes)"
AVGO_TH = P41.V3


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


def cand(sym, name, rank, state="wait"): return P44.cand(sym, name, rank, state, src="10-K ตัวอย่าง")


def idea(cands, iid="idea-vw1"):
    d = copy.deepcopy(P44.SEMIS); d["id"] = iid; d["name"] = "ธีมทดสอบ"; d["date"] = "2026-10-02"; d["status"] = "need_evidence"
    d["candidates"] = cands; d["losers"] = []; d["assets"] = []
    return d


class Env:
    """ตัวดักภาพ s3.tradingview.com: mode png (ปกติ) / 404 · เก็บ URL ที่ถูกขอ"""
    def __init__(self, mode="png"): self.mode = mode; self.urls = []


PICK59 = ['XAUUSD', 'BTCUSD', 'S50']   # WA1fix: ไม่มีโหมด legacy → เลือก 3 ตัวของสัปดาห์ (XAG/Brent เลือกเองในเคสที่ต้องใช้)
PICK59_XAG = ['XAUUSD', 'BTCUSD', 'XAG']


def launch(pw, w, h, mut=None, wl=(), ideas=(), notes=None, deny=False, mode="png", index=None, prev_chart=None, pick=None):
    env = Env(mode)
    def handler(route):
        env.urls.append(route.request.url)
        if env.mode == "404": route.fulfill(status=404, body="")
        else: route.fulfill(status=200, content_type="image/png", body=PNG)
    def extra(page):
        page.route(re.compile(r"s3\.tradingview\.com"), handler)
        if deny: page.evaluate("()=>window.firebase.__mockDb.__denyPath(['users','testuid','stockNotes'])")
        for t in wl:
            sym, th, kw = (t if isinstance(t, tuple) else (t, None, {}))
            P40.seed_wl(page, sym, th, **kw)
        for it in ideas: P44.seed_idea(page, it)
        for k, v in (notes or {}).items(): P39.seed(page, ["users", "testuid", "stockNotes", k], v)
        if prev_chart:
            P39.seed(page, ["users", "testuid", "satWeek", PWK], {"XAUUSD": {"bias": "Long", "invalidation": 3800, "support": [3900], "chart": prev_chart, "comps": {"trend": {"v": "up"}}}})
    doc = P38.doc38(clean=True, log={})
    if mut: mut(doc)
    saved = P39.INDEX
    if index: P39.INDEX = index
    try: r = P39.launch(pw, w, h, doc=doc, clean=True, iso=CLK, extra=extra, pick=pick or PICK59)
    finally: P39.INDEX = saved
    r[2].wait_for_timeout(400)
    return r + (env,)


def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def cnt(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def rect(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); return {x:r.left, y:r.top, w:r.width, h:r.height, r:r.right, b:r.bottom}; }", sel)
def wait(page, ms=300): page.wait_for_timeout(ms)
def doc_of(page, *path): return page.evaluate("(p)=>window.firebase.__mockDb.__getDoc(p)", ["users", "testuid", *path])
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
def real_errs(ce): return [e for e in ce if "Failed to load resource" not in e]

SAT_JS = "()=>{ satwWrite('XAUUSD', {bias:'Long', support:[3920,3860], resistance:[4080], invalidation:3840}); }"


def go_sat(page, set_xau=True):
    if set_xau: js(page, SAT_JS); wait(page, 300)
    P37.go_sat(page); wait(page, 300)


def tile_txt(page, key):
    """ข้อความของช่อง Strategy โดยตัดแถบกราฟออก (ส่วนอื่นของการ์ดต้องเหมือนเดิม)"""
    return js(page, "(k)=>{ const e=document.querySelector('.ui-tile[data-key=\"'+k+'\"]'); if(!e) return null; const c=e.cloneNode(true); c.querySelectorAll('.vwImg,.vwSatAdd,.vwSatF').forEach(x=>x.remove()); return c.innerText.replace(/\\s+/g,' ').trim(); }", key)


def tile_h(page, key, strip=True):
    """สูงของช่อง (strip=False → ซ่อนแถบกราฟชั่วคราวเพื่อวัดความสูงเดิม)"""
    return js(page, "([k,s])=>{ const e=document.querySelector('.ui-tile[data-key=\"'+k+'\"]'); const xs=[...e.querySelectorAll('.vwImg,.vwSatAdd,.vwSatF')]; if(!s) xs.forEach(x=>x.style.display='none'); const as=e.style.alignSelf; e.style.alignSelf='start'; const h=e.getBoundingClientRect().height; e.style.alignSelf=as; xs.forEach(x=>x.style.display=''); return h; }", [key, strip])


def week_xau(page): return (doc_of(page, "satWeek", WK) or {}).get("XAUUSD") or {}


def sat_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ── 1 tvSnapImg
    b, c, page, ce, pe, dl, env = launch(pw, w, h)
    try:
        cases = [
            (TV1, SNAP1), ("https://tradingview.com/x/pSb8OxWO/", SNAP1), ("https://www.tradingview.com/x/pSb8OxWO", SNAP1),
            ("https://www.tradingview.com/x/pSb8OxWO/?x=1", SNAP1), ("  " + TV1 + "  ", SNAP1),
            (TV2, "https://s3.tradingview.com/snapshots/a/Ab12Cd34.png"),
            ("https://s3.tradingview.com/snapshots/p/pSb8OxWO.png", "https://s3.tradingview.com/snapshots/p/pSb8OxWO.png"),
            ("https://google.com/x/abc", None), ("https://www.tradingview.com/x/ab/", None), ("สวัสดี", None), ("", None), (None, None),
            ("https://www.tradingview.com/chart/AbCdEf12/", None), ("https://evil.com/?https://www.tradingview.com/x/pSb8OxWO/", None),
        ]
        got = js(page, "(cs)=>cs.map(c=>tvSnapImg(c[0]))", [[c_[0], c_[1]] for c_ in cases])
        bad = [(cases[i][0], got[i], cases[i][1]) for i in range(len(cases)) if got[i] != cases[i][1]]
        check(f"{tag} 1 tvSnapImg: {len(cases)} รูปแบบลิงก์ (www/ไม่มี www · / ท้าย · ?query · ช่องว่าง · s3 ตรง · ลิงก์มั่ว → null)", not bad, json.dumps(bad, ensure_ascii=False))
    finally: b.close()

    # ── 1b VW1fix: โดเมนภาษา
    b, c, page, ce, pe, dl, env = launch(pw, w, h)
    try:
        cs = [("https://th.tradingview.com/x/pSb8OxWO/", SNAP1), ("https://jp.tradingview.com/x/Ab12Cd34", "https://s3.tradingview.com/snapshots/a/Ab12Cd34.png"),
              ("https://evil-tradingview.com/x/abcdef/", None), ("https://tradingview.com.evil.com/x/abcdef/", None), ("https://abcd.tradingview.com/x/abcdef/", None)]
        got = js(page, "(cs)=>cs.map(c=>tvSnapImg(c))", [c_[0] for c_ in cs])
        bad = [(cs[i][0], got[i], cs[i][1]) for i in range(len(cs)) if got[i] != cs[i][1]]
        check(f"{tag} 1b VW1fix tvSnapImg: th./jp. รับ · evil-/.evil.com/abcd. → null", not bad, json.dumps(bad, ensure_ascii=False))
    finally: b.close()

    # ── 1c VW1fix: Sat วางลิงก์ th.
    b, c, page, ce, pe, dl, env = launch(pw, w, h)
    try:
        go_sat(page)
        page.locator(".ui-tile[data-key=XAUUSD] [data-vw-sat-add]").click(); wait(page)
        page.locator("[data-vw-sat-in]").fill("https://th.tradingview.com/x/pSb8OxWO/"); page.locator("[data-vw-sat-save]").click(); wait(page, 600)
        ch = week_xau(page).get("chart")
        check(f"{tag} 1c VW1fix Sat: วางลิงก์ th. ในช่อง XAU → บันทึกได้ · แสดงภาพ", ch and ch.get("url") == "https://th.tradingview.com/x/pSb8OxWO/" and cnt(page, ".ui-tile[data-key=XAUUSD] .vwSat img") == 1 and SNAP1 in env.urls, json.dumps([ch, env.urls]))
        shot(page, f"vw1fix-sat-{sfx}.png", "#satV3Sum")
    finally: b.close()

    # ── 1d VW1fix: แถบว่างบรรทัดเดียว
    b, c, page, ce, pe, dl, env = launch(pw, w, h)
    try:
        go_sat(page)
        m = js(page, """()=>[...document.querySelectorAll('[data-vw-sat-add]')].map(e=>{const r=e.getBoundingClientRect(); const v=[...e.children].find(x=>getComputedStyle(x).display!=='none'); const lh=parseFloat(getComputedStyle(v).lineHeight)||parseFloat(getComputedStyle(v).fontSize)*1.4; return {h:r.height, sh:e.scrollHeight, ch:e.clientHeight, lines:v.getBoundingClientRect().height/lh, t:e.innerText.trim(), al:e.getAttribute('aria-label')}})""")
        want = "＋ กราฟ TV" if w <= 480 else "＋ วางลิงก์กราฟ TradingView"
        check(f"{tag} 1d VW1fix แถบว่างทุกช่อง: สูง ≤ 44 · บรรทัดเดียว · ข้อความ '{want}' · aria-label เต็ม", len(m) == 3 and all(x["h"] <= 44 and x["sh"] <= x["ch"] + 1 and x["lines"] < 1.6 and x["t"] == want and x["al"] == "＋ วางลิงก์กราฟ TradingView" for x in m), json.dumps(m, ensure_ascii=False))
    finally: b.close()

    # ── 2 Sat XAU: ไม่มีกราฟ → วางลิงก์ → แถบภาพ → เปลี่ยน → ลบ
    b, c, page, ce, pe, dl, env = launch(pw, w, h)
    try:
        go_sat(page)
        add = rect(page, ".ui-tile[data-key=XAUUSD] [data-vw-sat-add]")
        check(f"{tag} 2 ไม่มีกราฟ → แถบเส้นประ '＋ วางลิงก์กราฟ TradingView' สูง 40px (ทุกสินค้าที่เลือก 3 ช่อง · WA1fix)", add and abs(add["h"] - 40) <= 1 and (("＋ กราฟ TV" if w <= 480 else "＋ วางลิงก์กราฟ TradingView") == txt(page, ".ui-tile[data-key=XAUUSD] [data-vw-sat-add]")) and cnt(page, "[data-vw-sat-add]") == 3, json.dumps(add))
        shot(page, f"vw1-sat-empty-{sfx}.png", "#satV3Sum")
        sel_before = js(page, "()=>satV3Sel")
        page.locator(".ui-tile[data-key=XAUUSD] [data-vw-sat-add]").click(); wait(page)
        fs = js(page, "()=>{ const i=document.querySelector('[data-vw-sat-in]'); return i ? {fs:parseFloat(getComputedStyle(i).fontSize), foc:document.activeElement===i} : null; }")
        check(f"{tag} 2 กดแล้วเป็นช่องกรอก + บันทึก/ยกเลิก · font ≥ 16px · ไม่ขยายตัวแก้ Strategy", fs and fs["fs"] >= 16 and cnt(page, "[data-vw-sat-save]") == 1 and cnt(page, "[data-vw-sat-cancel]") == 1 and js(page, "()=>satV3Sel") == sel_before, json.dumps(fs))
        page.locator("[data-vw-sat-in]").fill("https://google.com/x/abc"); page.locator("[data-vw-sat-save]").click(); wait(page, 400)
        check(f"{tag} 2 ลิงก์ผิด → ข้อความ '{BAD_MSG}' · ไม่บันทึก (satWeek ไม่มี chart)", txt(page, "[data-vw-sat-msg]") == BAD_MSG and "chart" not in week_xau(page), json.dumps([txt(page, "[data-vw-sat-msg]"), week_xau(page)], ensure_ascii=False))
        page.locator("[data-vw-sat-cancel]").click(); wait(page)
        check(f"{tag} 2 ยกเลิก → กลับเป็นแถบ ＋ วางลิงก์", cnt(page, "[data-vw-sat-add]") == 3 and cnt(page, "[data-vw-sat-form]") == 0)
        page.locator(".ui-tile[data-key=XAUUSD] [data-vw-sat-add]").click(); wait(page)
        page.locator("[data-vw-sat-in]").fill("  " + TV1 + "?x=1  "); page.locator("[data-vw-sat-save]").click(); wait(page, 600)
        ch = week_xau(page).get("chart")
        check(f"{tag} 2 วางลิงก์ถูก → satWeek[XAUUSD].chart = {{url, at:'{TODAY}'}}", ch and ch.get("url") == TV1 + "?x=1" and ch.get("at") == TODAY, json.dumps(ch))
        strip = rect(page, ".ui-tile[data-key=XAUUSD] .vwSat")
        tag_t = txt(page, ".ui-tile[data-key=XAUUSD] .vwSat .vwTag")
        fit = js(page, "()=>{ const i=document.querySelector('.ui-tile[data-key=XAUUSD] .vwSat img'); const s=getComputedStyle(i); return {fit:s.objectFit, ref:i.getAttribute('referrerpolicy'), lazy:i.getAttribute('loading'), src:i.getAttribute('src')}; }")
        rt = js(page, "(s)=>{ const i=document.querySelector(s+' img'); const w=i.getBoundingClientRect(); return {fit:getComputedStyle(i).objectFit, w:w.width, h:w.height, exp:w.width*i.naturalHeight/i.naturalWidth, nw:i.naturalWidth}; }", ".ui-tile[data-key=XAUUSD] .vwSat")
        check(f"{tag} 2 [ESC1] แถบภาพเห็นทั้งภาพ: สูงตามสัดส่วนจริง (ไม่ตายตัว 92px) · object-fit contain · ป้ายมุมล่างซ้าย 'W | D · 9 ต.ค.' · lazy + no-referrer · src = {SNAP1}", strip and rt["fit"] == "contain" and abs(rt["h"] - rt["exp"]) <= 2 and tag_t == "W | D · 9 ต.ค." and {k: fit[k] for k in ("ref", "lazy", "src")} == {"ref": "no-referrer", "lazy": "lazy", "src": SNAP1}, json.dumps([strip, tag_t, fit, rt], ensure_ascii=False))
        check(f"{tag} 2 มีการขอภาพ {SNAP1} (ดักด้วย PNG ปลอม)", SNAP1 in env.urls, json.dumps(env.urls))
        order = js(page, "()=>{ const t=document.querySelector('.ui-tile[data-key=XAUUSD]'); const kids=[...t.children].map(e=>e.className.split(' ')[0]); return kids; }")
        check(f"{tag} 2 แถบอยู่ใต้หัวการ์ด เหนือแนวรับ/ต้าน (ลำดับลูก: ui-tile-th → vwImg → ui-tile-s)", order.index("ui-tile-th") < order.index("vwImg") < order.index("ui-tile-s"), json.dumps(order))
        shot(page, f"vw1-sat-chart-{sfx}.png", "#satV3Sum")
        page.locator(".ui-tile[data-key=XAUUSD] [data-vw-sat-chg]").click(); wait(page)
        check(f"{tag} 2 ปุ่ม 'เปลี่ยน' → ช่องวางลิงก์ + ปุ่ม 'ลบกราฟ' (ยังเห็นภาพเดิม)", cnt(page, "[data-vw-sat-form]") == 1 and cnt(page, "[data-vw-sat-del]") == 1 and cnt(page, ".ui-tile[data-key=XAUUSD] .vwSat") == 1)
        page.locator("[data-vw-sat-in]").fill(TV2); page.locator("[data-vw-sat-save]").click(); wait(page, 500)
        check(f"{tag} 2 เปลี่ยนเป็นลิงก์ใหม่ → chart.url ใหม่ (1 ภาพ/สินค้า/สัปดาห์)", week_xau(page).get("chart", {}).get("url") == TV2 and SNAP1.replace("p/pSb8OxWO", "a/Ab12Cd34") in env.urls, json.dumps(week_xau(page).get("chart")))
        page.locator(".ui-tile[data-key=XAUUSD] [data-vw-sat-chg]").click(); wait(page)
        page.locator("[data-vw-sat-del]").click(); wait(page, 500)
        check(f"{tag} 2 'ลบกราฟ' → ช่องกราฟหาย (chart ว่าง) · กลับเป็นแถบ ＋ วางลิงก์", not week_xau(page).get("chart") and cnt(page, ".ui-tile[data-key=XAUUSD] .vwSat") == 0 and cnt(page, ".ui-tile[data-key=XAUUSD] [data-vw-sat-add]") == 1, json.dumps(week_xau(page)))
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()

    # ── 3 ความสูง · ส่วนอื่นของการ์ดเหมือนเดิม · copy prev · XAG · ซ่อน
    def hidden_btc(doc): doc["books"]["main"]["settings"]["satAssetCfg"] = {"BTCUSD": {"hidden": True}}
    b, c, page, ce, pe, dl, env = launch(pw, w, h, mut=P55.with_custom(P55.XAG), prev_chart={"url": TV2, "at": "2026-10-02"}, pick=PICK59_XAG)
    try:
        go_sat(page)
        t0 = {k: tile_txt(page, k) for k in ("XAUUSD", "BTCUSD", "XAG")}
        h_empty = tile_h(page, "XAUUSD", True); h_base = tile_h(page, "XAUUSD", False)
        check(f"{tag} 3 สินค้าที่เพิ่มเอง (XAG) มีแถบกราฟ ＋ วางลิงก์ เหมือนสินค้าอื่น", cnt(page, ".ui-tile[data-key=XAG] [data-vw-sat-add]") == 1 and cnt(page, "[data-vw-sat-add]") == 3)   # WA1fix: XAU · BTC · XAG ที่เลือก
        js(page, "()=>satwWrite('XAG', {chart:{url:'https://www.tradingview.com/x/Zz9Yy8Xx/', at:'2026-10-08'}})"); wait(page, 400)
        rtx = js(page, "(s)=>{ const i=document.querySelector(s+' img'); const w=i.getBoundingClientRect(); return {fit:getComputedStyle(i).objectFit, w:w.width, h:w.height, exp:w.width*i.naturalHeight/i.naturalWidth, nw:i.naturalWidth}; }", ".ui-tile[data-key=XAG] .vwSat")
        check(f"{tag} 3 [ESC1] XAG ใส่กราฟได้ → ป้าย 'W | D · 8 ต.ค.' · สูงตามสัดส่วนภาพ (±2px)", txt(page, ".ui-tile[data-key=XAG] .vwTag") == "W | D · 8 ต.ค." and rtx["fit"] == "contain" and abs(rtx["h"] - rtx["exp"]) <= 2, json.dumps(rtx))
        js(page, "()=>satwWrite('XAUUSD', {chart:{url:'" + TV1 + "', at:'2026-10-09'}})"); wait(page, 400)
        h_chart = tile_h(page, "XAUUSD", True)
        strip_h = rect(page, ".ui-tile[data-key=XAUUSD] .vwSat")["h"]
        check(f"{tag} 3 [ESC1] ช่องที่มีกราฟสูง = เดิม + ความสูงแถบภาพจริง ({strip_h:.0f}px) ± 12 (เดิม {h_base:.0f} → {h_chart:.0f})", abs((h_chart - h_base) - strip_h) <= 12, json.dumps([h_base, h_chart, h_empty, strip_h]))
        t1 = {k: tile_txt(page, k) for k in t0}
        check(f"{tag} PF3 3 ส่วนอื่นของการ์ด (แนวรับ/ต้าน · จุด) ข้อความเหมือนเดิมทุกช่องหลังใส่กราฟ · ไม่มี Bias/ขนาดไม้/Trend Shift ในช่อง", t1 == t0 and all(v and "Trend Shift" not in v and "ขนาดไม้" not in v for v in t1.values()), json.dumps([t0, t1], ensure_ascii=False))
        js(page, "()=>{ satV3Sel = 'XAUUSD'; satV3Render(); }"); wait(page, 300)
        pre_cnt = cnt(page, ".ui-editor[data-asset=XAUUSD]")
        js(page, "()=>{ satwWrite('XAUUSD', {chart:null}); }"); wait(page, 300)
        js(page, "()=>satwCopyFromPrev('XAUUSD')"); wait(page, 500)
        w_ = week_xau(page)
        check(f"{tag} 3 satwCopyFromPrev: คัดลอก chart จากสัปดาห์ก่อนด้วย (ป้ายวันที่เป็นของเดิม 2 ต.ค.) · Bias ไม่คัดลอก", w_.get("chart") == {"url": TV2, "at": "2026-10-02"} and txt(page, ".ui-tile[data-key=XAUUSD] .vwTag") == "W | D · 2 ต.ค." and pre_cnt == 1, json.dumps(w_, ensure_ascii=False))
        js(page, "()=>{ satV3Sel = null; satV3Render(); }")
        check(f"{tag} 3 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()
    # เทียบกับก่อน VW1: ข้อความทุกช่องเหมือนเดิม (ไม่นับแถบกราฟ)
    b, c, page, ce, pe, dl, env = launch(pw, w, h, mut=P55.with_custom(P55.XAG), pick=PICK59_XAG)
    b2, c2, page2, ce2, pe2, dl2, env2 = launch(pw, w, h, mut=P55.with_custom(P55.XAG), index=BACKUP)
    try:
        go_sat(page); go_sat(page2)
        keys = ("XAUUSD", "BTCUSD", "XAG")   # WA1fix: ที่เลือกสัปดาห์นี้
        a = {k: tile_txt(page, k) for k in keys}; o = {k: tile_txt(page2, k) for k in keys}
        check(f"{tag} PF3 3 ข้อความ 3 ช่อง (ที่เลือก) Strategy: XAU = ชื่อ + [+ แผน] + แนวรับ/ต้านชุดเดิมเท่าไฟล์ก่อน VW1 ทุกตัวอักษร (ไม่มี Bias/ขนาดไม้/Trend Shift) · BTC/Silver (ยังไม่มีแนว) = ชื่อ + [+ แผน] + 'รับ — · ต้าน —'", a["XAUUSD"] == "XAUUSD+ แผน" + re.search(r"(รับ .*?)(?: · Trend Shift.*)?$", o["XAUUSD"]).group(1) and a["BTCUSD"] == "BTC+ แผนรับ — · ต้าน —" and a["XAG"] == "Silver+ แผนรับ — · ต้าน —", json.dumps([a, o], ensure_ascii=False))
        ha = js(page2, "(k)=>document.querySelector('.ui-tile[data-key=\"'+k+'\"]').getBoundingClientRect().height", "XAUUSD")
        # RR1fix: ที่ ≤430 ชื่อ/ป้ายในการ์ดขึ้นบรรทัดใหม่ได้ (ฟอนต์ต่างเครื่องตัดบรรทัดไม่เท่ากัน) → วัดเป็น "จำนวนบรรทัด" ด้วย line-height จริง (computed) ไม่ใช่ px ตายตัว
        lh = js(page, "(k)=>{ const e=document.querySelector('.ui-tile[data-key=\"'+k+'\"]'); let m=0; e.querySelectorAll('*').forEach(x=>{ if(![...x.childNodes].some(n=>n.nodeType===3 && n.textContent.trim())) return; const c=getComputedStyle(x); const l=parseFloat(c.lineHeight)||parseFloat(c.fontSize)*1.4; if(l>m) m=l; }); return m; }", "XAUUSD")
        extra = (tile_h(page, "XAUUSD", True) - ha) - 46
        extra_lines = max(0.0, extra - 6) / lh if lh else 99
        check(f"{tag} PF3 3 ช่อง XAU ไม่มีกราฟ: สูงไม่เกินก่อน VW1 + แถบ ＋ วางลิงก์ (40px + ระยะ ≤ 52) · ส่วนที่เกินจากขึ้นบรรทัดใหม่ ≤ 1 บรรทัด (line-height จริง {lh:.1f}px) · tile สั้นลงเพราะไม่มีป้าย Bias", (tile_h(page, "XAUUSD", True) - ha) <= 52 + lh and extra_lines <= 1, json.dumps([tile_h(page, "XAUUSD", True), ha, lh, extra_lines]))
    finally: b.close(); b2.close()
    b, c, page, ce, pe, dl, env = launch(pw, w, h, mut=P55.with_custom(P55.XAG), pick=PICK59_XAG)
    try:
        go_sat(page)
        js(page, "()=>{ waRemove('BTCUSD'); }"); wait(page, 300)   # WA1fix: ไม่มีการซ่อนแล้ว → เอาออกจากสัปดาห์นี้
        ks = js(page, "()=>[...document.querySelectorAll('.ui-tile[data-key]')].map(e=>e.dataset.key)")
        check(f"{tag} 3 สินค้าที่เอาออกจากสัปดาห์ (แทนซ่อน BR1: BTCUSD) ไม่แสดงแถบกราฟ · ที่เหลือมีแถบ", "BTCUSD" not in ks and cnt(page, "[data-vw-sat-add]") == len(ks) == 2, json.dumps(ks))
    finally: b.close()

    # ── 4 ภาพโหลดไม่ได้ · lightbox
    b, c, page, ce, pe, dl, env = launch(pw, w, h, mode="404")
    try:
        go_sat(page)
        js(page, "()=>satwWrite('XAUUSD', {chart:{url:'" + TV1 + "', at:'2026-10-09'}})"); wait(page, 800)
        bad = js(page, "()=>{ const a=document.querySelector('.ui-tile[data-key=XAUUSD] .vwBad'); return a ? {t:a.innerText.trim(), href:a.getAttribute('href'), tg:a.target, bg:getComputedStyle(a).backgroundColor, h:a.getBoundingClientRect().height} : null; }")
        check(f"{tag} 4 ภาพ 404 → กล่องเทา 'เปิดกราฟใน TradingView ↗' (ลิงก์เดิม · แท็บใหม่) สูง 92px", bad and bad["t"] == "เปิดกราฟใน TradingView ↗" and bad["href"] == TV1 and bad["tg"] == "_blank" and abs(bad["h"] - 92) <= 2, json.dumps(bad, ensure_ascii=False))
        page.locator(".ui-tile[data-key=XAUUSD] .vwSat").click(position={"x": 8, "y": 8}); wait(page, 250)
        check(f"{tag} 4 แตะกล่องเสีย → ไม่เปิด overlay · ไม่ขยายการ์ด", cnt(page, "#vwLb") == 0 and js(page, "()=>satV3Sel") is None)
        check(f"{tag} 4 ภาพโหลดไม่ได้ → ไม่มี console error ของแอป (ไม่นับบรรทัด 'Failed to load resource' ของเบราว์เซอร์)", not real_errs(ce) and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()
    b, c, page, ce, pe, dl, env = launch(pw, w, h)
    try:
        go_sat(page)
        js(page, "()=>satwWrite('XAUUSD', {chart:{url:'" + TV1 + "', at:'2026-10-09'}})"); wait(page, 600)
        page.locator(".ui-tile[data-key=XAUUSD] .vwSat").click(position={"x": 40, "y": 40}); wait(page, 300)
        lb = js(page, "()=>{ const o=document.getElementById('vwLb'); if(!o) return null; const r=o.getBoundingClientRect(); const a=o.querySelector('a'); return {w:r.width, h:r.height, bg:getComputedStyle(o).backgroundColor, img:o.querySelector('img').getAttribute('src'), a:a.innerText.trim(), href:a.getAttribute('href'), tg:a.target, vw:innerWidth, vh:innerHeight}; }")
        check(f"{tag} 4 แตะภาพ → overlay เต็มจอ พื้นดำ + รูปใหญ่ + ปุ่ม 'เปิดใน TV ↗' (ลิงก์เดิม · แท็บใหม่) · การ์ดไม่ขยาย", lb and lb["w"] == lb["vw"] and lb["h"] == lb["vh"] and lb["bg"] == "rgb(0, 0, 0)" and lb["img"] == SNAP1 and lb["a"] == "เปิดใน TV ↗" and lb["href"] == TV1 and lb["tg"] == "_blank" and js(page, "()=>satV3Sel") is None, json.dumps(lb, ensure_ascii=False))
        shot(page, f"vw1-lightbox-{sfx}.png")
        page.mouse.click(w // 2, h // 2); wait(page, 250)
        check(f"{tag} 4 แตะที่ใดก็ได้ → ปิด", cnt(page, "#vwLb") == 0)
        page.locator(".ui-tile[data-key=XAUUSD] .vwSat").click(position={"x": 40, "y": 40}); wait(page, 250)
        page.keyboard.press("Escape"); wait(page, 200)
        check(f"{tag} 4 กด Esc ปิดได้ด้วย", cnt(page, "#vwLb") == 0)
        check(f"{tag} 4 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def wl_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); narrow = w < 500

    def open_card(page, sym="AVGO", sub="view"):
        P40.go_watch(page); js(page, "([s,b])=>wlOpen(s,b)", [sym, sub]); wait(page, 350)

    def rows(page): return js(page, "()=>[...document.querySelectorAll('.wlDBody [data-vw-row]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
    def add(page, ang, text, url=None):
        if not cnt(page, f'.wlDBody [data-vw-ang="{ang}"]'):
            page.locator(f'.wlDBody [data-vw-row="{ang}"]').click(); wait(page, 200)
        page.locator(f'.wlDBody [data-vw-ang="{ang}"] [data-vw-t]').fill(text)
        if url is not None: page.locator(f'.wlDBody [data-vw-ang="{ang}"] [data-vw-url]').fill(url)
        page.locator(f'.wlDBody [data-vw-ang="{ang}"] [data-vw-save]').click(); wait(page, 400)
    def notes_of(page, sym="AVGO"): return doc_of(page, "stockNotes", sym) or {}

    # ── 5 Watchlist AVGO · แท็บ มุมมอง
    b, c, page, ce, pe, dl, env = launch(pw, w, h, wl=[("AVGO", AVGO_TH, {})])
    try:
        open_card(page, "AVGO", "sum")
        tabs = js(page, "()=>[...document.querySelectorAll('[data-lt-tab]')].map(e=>[e.dataset.ltTab, e.innerText.trim()])")
        check(f"{tag} 5 แท็บการ์ด 6 แท็บ: สรุป · มุมมอง · ธุรกิจ · ทำไมซื้อ · ติดตาม · ออกเมื่อ (มุมมองเป็นแท็บที่ 2)", [t[0] for t in tabs] == ["sum", "view", "biz", "why", "trk", "exit"] and tabs[1][1] == "มุมมอง" and tabs[0][1] == "สรุป", json.dumps(tabs, ensure_ascii=False))
        tb = js(page, "()=>{ const t=document.querySelector('[data-lt-tabs]'); return {sw:t.scrollWidth, cw:t.clientWidth, ovf:document.documentElement.scrollWidth-innerWidth, right:t.getBoundingClientRect().right, vw:innerWidth}; }")
        check(f"{tag} 5 แถบแท็บไม่ล้นหน้า (เกินให้เลื่อนในแถบเอง)", tb["ovf"] <= 0 and tb["right"] <= tb["vw"] + 1, json.dumps(tb))
        check(f"{tag} 5 ป้าย 'สรุป' ของการ์ดไม่เปลี่ยน", tabs[0] == ["sum", "สรุป"])
        page.locator('[data-lt-tab="view"]').click(); wait(page, 300)
        r0 = rows(page)
        check(f"{tag} 5 ว่าง → 3 แถว Event · Fund. · Tech ทุกแถว '— แตะเพื่อเพิ่ม'", len(r0) == 3 and all("— แตะเพื่อเพิ่ม" in x for x in r0) and r0[0].startswith("Event") and r0[1].startswith("Fund.") and r0[2].startswith("Tech"), json.dumps(r0, ensure_ascii=False))
        shot(page, f"vw1-wl-view-{sfx}.png", ".wlDBody")
        # Event 2 รายการ คนละวัน
        add(page, "event", "ดีล custom ASIC รายใหม่")
        js(page, "(iso)=>(" + P38.CLOCK_JS + ")(iso)", "2026-10-10T05:00:00Z"); wait(page, 100)
        add(page, "event", "รอยืนยัน capex")
        ev = notes_of(page).get("event", [])
        r1 = rows(page)
        check(f"{tag} 5 เพิ่ม Event 2 รายการ (คนละวัน) → doc stockNotes/AVGO.event 2 รายการ ใหม่อยู่หน้า (d 10-10 แล้ว 10-09)", [(x["d"], x["t"]) for x in ev] == [("2026-10-10", "รอยืนยัน capex"), (TODAY, "ดีล custom ASIC รายใหม่")], json.dumps(ev, ensure_ascii=False))
        check(f"{tag} 5 แถว Event โชว์ล่าสุด + วัน (10 ต.ค.) · ประวัติเรียงใหม่ก่อน", "รอยืนยัน capex" in r1[0] and "10 ต.ค." in r1[0] and js(page, "()=>[...document.querySelectorAll('.wlDBody [data-vw-ang=event] [data-vw-item] .vwHT')].map(e=>e.innerText)") == ["รอยืนยัน capex", "ดีล custom ASIC รายใหม่"], json.dumps(r1, ensure_ascii=False))
        # Tech + ลิงก์กราฟ
        add(page, "tech", "พักใกล้ EMA10 W", TV2)
        thumb = js(page, "()=>{ const e=document.querySelector('.wlDBody [data-vw-row=tech] .vwMini'); if(!e) return null; const r=e.getBoundingClientRect(); return {w:r.width, h:r.height, src:e.querySelector('img').getAttribute('src')}; }")
        tech = notes_of(page).get("tech", [])
        check(f"{tag} 5 Tech + ลิงก์กราฟ → เก็บลิงก์ใน tech[0].chart · ภาพย่อ 54×30 ในแถว", tech and tech[0].get("chart") == TV2 and thumb and thumb["w"] == 54 and thumb["h"] == 30 and thumb["src"].endswith("/a/Ab12Cd34.png"), json.dumps([tech, thumb], ensure_ascii=False))
        hi = rect(page, ".wlDBody [data-vw-ang=tech] .vwTop .vwImg")
        rth = js(page, "(s)=>{ const i=document.querySelector(s+' img'); const w=i.getBoundingClientRect(); return {fit:getComputedStyle(i).objectFit, w:w.width, h:w.height, exp:w.width*i.naturalHeight/i.naturalWidth, nw:i.naturalWidth}; }", ".wlDBody [data-vw-ang=tech] .vwTop .vwImg")
        check(f"{tag} 5 [ESC1] แตะแถว Tech ที่มีกราฟ → กราฟล่าสุดเต็มกว้างบนสุด สูงตามสัดส่วนภาพ (เดิมภาพย่อ 110px ในประวัติ)", hi and rth["fit"] == "contain" and abs(rth["h"] - rth["exp"]) <= 2, json.dumps([hi, rth]))
        shot(page, f"vw1-wl-tech-open-{sfx}.png", ".wlDBody")
        # ลิงก์ผิดใน Tech
        page.locator('.wlDBody [data-vw-ang=tech] [data-vw-t]').fill("ทดสอบลิงก์ผิด"); page.locator('.wlDBody [data-vw-ang=tech] [data-vw-url]').fill("https://google.com/x/abc")
        page.locator('.wlDBody [data-vw-ang=tech] [data-vw-save]').click(); wait(page, 300)
        check(f"{tag} 5 ลิงก์กราฟผิด → '{BAD_MSG}' · ไม่บันทึก (tech ยัง 1 รายการ)", txt(page, ".wlDBody [data-vw-msg]") == BAD_MSG and len(notes_of(page).get("tech", [])) == 1, txt(page, ".wlDBody [data-vw-msg]") or "")
        # 141 ตัว
        page.locator('.wlDBody [data-vw-ang=tech] [data-vw-url]').fill("")
        page.locator('.wlDBody [data-vw-ang=tech] [data-vw-t]').fill("x" * 141); wait(page, 100)
        st = js(page, "()=>({dis:document.querySelector('.wlDBody [data-vw-ang=tech] [data-vw-save]').disabled, cnt:document.querySelector('.wlDBody [data-vw-ang=tech] [data-vw-cnt]').innerText, over:document.querySelector('.wlDBody [data-vw-ang=tech] [data-vw-cnt]').classList.contains('over')})")
        js(page, "()=>document.querySelector('.wlDBody [data-vw-ang=tech] [data-vw-save]').click()"); wait(page, 250)
        check(f"{tag} 5 141 ตัว → ตัวนับ 141/140 สีเตือน · ปุ่มบันทึกกดไม่ได้ · ไม่เขียน", st == {"dis": True, "cnt": "141/140", "over": True} and len(notes_of(page).get("tech", [])) == 1, json.dumps(st))
        page.locator('.wlDBody [data-vw-ang=tech] [data-vw-t]').fill("x" * 140); wait(page, 100)
        check(f"{tag} 5 140 ตัวพอดี → กดบันทึกได้ (140/140)", js(page, "()=>!document.querySelector('.wlDBody [data-vw-ang=tech] [data-vw-save]').disabled") and txt(page, ".wlDBody [data-vw-ang=tech] [data-vw-cnt]") == "140/140")
        # ลบ (ยืนยัน)
        n_dl = len(dl)
        page.locator('.wlDBody [data-vw-ang=tech] [data-vw-item]').first.locator("[data-vw-del]").click(); wait(page, 400)
        check(f"{tag} 5 ลบรายการ → ถามยืนยัน (confirm) แล้วลบออกจาก doc", len(dl) == n_dl + 1 and notes_of(page).get("tech") == [] and "— แตะเพื่อเพิ่ม" in rows(page)[2], json.dumps([dl[n_dl:], notes_of(page).get("tech")], ensure_ascii=False))
        check(f"{tag} 5 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()
    # รายการที่ 51
    seed50 = {"AVGO": {"event": [{"id": f"e{i}", "d": "2026-09-01", "t": f"เก่า {i}"} for i in range(50)], "fund": [], "tech": [], "updated_at": "2026-09-01T00:00:00Z"}}
    b, c, page, ce, pe, dl, env = launch(pw, w, h, wl=[("AVGO", AVGO_TH, {})], notes=seed50)
    try:
        open_card(page)
        add(page, "event", "รายการที่ 51")
        ev = notes_of(page).get("event", [])
        check(f"{tag} 5 รายการที่ 51 → ตัดเก่าสุดทิ้ง เหลือ 50 (ใหม่อยู่หน้า · e49 หาย · e48 ยังอยู่)", len(ev) == 50 and ev[0]["t"] == "รายการที่ 51" and ev[-1]["id"] == "e48" and not any(x["id"] == "e49" for x in ev), json.dumps([len(ev), ev[0], ev[-1]], ensure_ascii=False))
        check(f"{tag} 5 ประวัติบนจอแสดงครบ 50 รายการ", cnt(page, ".wlDBody [data-vw-ang=event] [data-vw-item]") == 50)
    finally: b.close()

    # ── 6 Candidates
    ideas = [idea([cand("CAA", "Cand A", 1, "study"), cand("CBB", "Cand B", 2, "wait")])]
    b, c, page, ce, pe, dl, env = launch(pw, w, h, ideas=ideas)
    try:
        P40.go_watch(page); js(page, "()=>wlSetView('cand')"); wait(page, 350)
        h_rows = js(page, "()=>[...document.querySelectorAll('.wlRows .wlR')].map(e=>Math.round(e.getBoundingClientRect().height))")
        one_line = js(page, "()=>[...document.querySelectorAll('.wlRows .wlR')].every(e=>{ const kids=[...e.children].filter(k=>k.getBoundingClientRect().height>0); const tops=kids.map(k=>k.getBoundingClientRect().top+k.getBoundingClientRect().height/2); return Math.max(...tops)-Math.min(...tops) < 6; })")
        check(f"{tag} 6 Candidates: แถวบรรทัดเดียว (ID2) ก่อนแตะ · ยังไม่มีแถวขยาย", len(h_rows) == 2 and one_line and cnt(page, "[data-cand-x]") == 0, json.dumps([h_rows, one_line]))
        page.locator('.wlRows .wlR[data-sym="CAA"]').click(); wait(page, 400)
        check(f"{tag} 6 แตะแถว CAA → ขยายลงมา 3 แถว (Event · Fund. · Tech)", cnt(page, "[data-cand-x]") == 1 and js(page, "()=>document.querySelector('[data-cand-x]').dataset.sym") == "CAA" and js(page, "()=>[...document.querySelectorAll('[data-cand-x] [data-vw-row]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().split(' ')[0])") == ["Event", "Fund.", "Tech"])
        after = js(page, "()=>{ const r=document.querySelector('.wlRows .wlR[data-sym=CAA]'), x=document.querySelector('[data-cand-x]'); return r.nextElementSibling===x; }")
        check(f"{tag} 6 แถวขยายอยู่ใต้แถวที่แตะ", after)
        page.locator('.wlRows .wlR[data-sym="CBB"]').click(); wait(page, 350)
        check(f"{tag} 6 แตะแถวอื่น → เปิดได้ทีละแถว (CAA พับ · CBB ขยาย)", cnt(page, "[data-cand-x]") == 1 and js(page, "()=>document.querySelector('[data-cand-x]').dataset.sym") == "CBB")
        page.locator('.wlRows .wlR[data-sym="CBB"]').click(); wait(page, 300)
        check(f"{tag} 6 แตะหัวแถวซ้ำ → พับ", cnt(page, "[data-cand-x]") == 0)
        page.locator('.wlRows .wlR[data-sym="CAA"]').click(); wait(page, 350)
        page.locator('[data-cand-x] [data-vw-row="fund"]').click(); wait(page, 200)
        page.locator('[data-cand-x] [data-vw-ang="fund"] [data-vw-t]').fill("backlog โต · margin 50%")
        page.locator('[data-cand-x] [data-vw-ang="fund"] [data-vw-save]').click(); wait(page, 450)
        d = doc_of(page, "stockNotes", "CAA") or {}
        check(f"{tag} 6 บันทึก Fund. ในแถวขยาย → stockNotes/CAA.fund 1 รายการ", len(d.get("fund", [])) == 1 and d["fund"][0]["t"] == "backlog โต · margin 50%" and d["fund"][0]["d"] == TODAY, json.dumps(d, ensure_ascii=False))
        shot(page, f"vw1-cand-open-{sfx}.png")
        dot = js(page, "()=>({caa:!!document.querySelector('.wlRows .wlR[data-sym=CAA] [data-vw-dot]'), cbb:!!document.querySelector('.wlRows .wlR[data-sym=CBB] [data-vw-dot]'), h:Math.round(document.querySelector('.wlRows .wlR[data-sym=CAA]').getBoundingClientRect().height), h2:Math.round(document.querySelector('.wlRows .wlR[data-sym=CBB]').getBoundingClientRect().height)})")
        check(f"{tag} 6 แถวที่มีโน้ตมีจุด • หลังชื่อ (CAA มี · CBB ไม่มี) · แถวยังบรรทัดเดียว สูงเท่ากัน", dot["caa"] and not dot["cbb"] and abs(dot["h"] - dot["h2"]) <= 2, json.dumps(dot))
        before = js(page, "()=>document.querySelector('[data-cand-x]') ? document.querySelector('[data-cand-x]').dataset.sym : null")
        page.locator('[data-cand-x] [data-c-add]').click(); wait(page, 350)
        ov = js(page, "()=>({um: !!document.querySelector('[data-td4-usemove]'), show:document.getElementById('wlAddOverlay').classList.contains('show'), x:document.querySelector('[data-cand-x]') ? document.querySelector('[data-cand-x]').dataset.sym : null})")
        check(f"{tag} 6 กด ＋ เพิ่มเข้า Watchlist ที่ Candidate → TD4b: ข้อความ 'Use Move to Watchlist' (ไม่เปิดฟอร์มเพิ่ม) · แถวไม่ถูกสลับขยาย/พับ", ov == {"um": True, "show": False, "x": before == "CAA" and "CAA" or None}, json.dumps([before, ov]))
        js(page, "()=>ltSheetClose()")
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','CAA'], {ticker:'CAA', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); wait(page, 600)   # TD4b: ย้ายเข้า Watchlist ได้ทางเดียวคือฟอร์ม Move — ในเทสนี้ seed ตรง ๆ
        check(f"{tag} 6 เพิ่มเข้า Watchlist แล้ว (CAA อยู่ใน Watchlist)", js(page, "()=>wlHas('CAA')"))
        open_card(page, "CAA", "view")
        r_ = rows(page)
        check(f"{tag} 6 เปิดการ์ด CAA → แท็บ มุมมอง เห็นโน้ตเดิมทันที (Fund. 'backlog โต · margin 50%')", len(r_) == 3 and "backlog โต · margin 50%" in r_[1], json.dumps(r_, ensure_ascii=False))
        js(page, "()=>wlDeleteItem('CAA')"); wait(page, 600)
        d = doc_of(page, "stockNotes", "CAA") or {}
        check(f"{tag} 6 ลบ CAA ออกจาก Watchlist → ไม่ลบ stockNotes (ยังมี fund 1 รายการ)", not js(page, "()=>wlHas('CAA')") and len(d.get("fund", [])) == 1, json.dumps(d, ensure_ascii=False))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()

    # ── 7 ไม่มีสิทธิ์อ่าน stockNotes
    ideas = [idea([cand("CAA", "Cand A", 1, "study")])]
    b, c, page, ce, pe, dl, env = launch(pw, w, h, wl=[("AVGO", AVGO_TH, {})], ideas=ideas, deny=True)
    try:
        open_card(page)
        check(f"{tag} 7 mock ปฏิเสธ stockNotes → จุดโน้ตแสดง '{RULE_MSG}'", txt(page, ".wlDBody [data-vw-err]") == RULE_MSG and cnt(page, "[data-vw-row]") == 0, txt(page, ".wlDBody [data-vw-err]") or "")
        js(page, "()=>wlSetView('cand')"); wait(page, 300)
        page.locator('.wlRows .wlR[data-sym="CAA"]').click(); wait(page, 300)
        check(f"{tag} 7 Candidates ทำงานปกติ: แถวขยายแสดงข้อความ rule · ปุ่ม ＋ เพิ่มเข้า Watchlist ยังอยู่", txt(page, "[data-cand-x] [data-vw-err]") == RULE_MSG and cnt(page, "[data-cand-x] [data-c-add]") == 1)
        js(page, "()=>wlSetView('wl')"); wait(page, 250)
        check(f"{tag} 7 Watchlist ปกติ (AVGO ในรายการ · เปลี่ยนแท็บอื่นได้)", cnt(page, '.wlRows .wlR[data-sym="AVGO"]') == 1)
        go_sat(page)
        check(f"{tag} 7 Sat ปกติ: ช่อง Strategy 3 ช่อง (ที่เลือก) + แถบกราฟ", cnt(page, ".ui-tile[data-key]") == 3 and cnt(page, "[data-vw-sat-add]") == 3)
        page.locator(".ui-tile[data-key=XAUUSD] [data-vw-sat-add]").click(); wait(page, 200)
        page.locator("[data-vw-sat-in]").fill(TV1); page.locator("[data-vw-sat-save]").click(); wait(page, 500)
        check(f"{tag} 7 Sat เขียนกราฟได้ตามปกติแม้ stockNotes ถูกปฏิเสธ", week_xau(page).get("chart", {}).get("url") == TV1)
        check(f"{tag} 7 ไม่มี error ค้าง (console / pageerror)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()

    # ── 8 TH: PTT.BK = PTT
    b, c, page, ce, pe, dl, env = launch(pw, w, h, wl=[("PTT.BK", None, {"market": "TH"})])
    try:
        P40.go_watch(page)
        sym = js(page, "()=>wlRowsAll().wl.map(r=>r.sym)")[0]
        js(page, "([s])=>wlOpen(s,'view')", [sym]); wait(page, 350)
        check(f"{tag} 8 การ์ด PTT.BK ไม่มี Thesis → ยังมีส่วน มุมมอง ให้บันทึก (3 แถว)", len(rows(page)) == 3, json.dumps([sym, rows(page)], ensure_ascii=False))
        add(page, "fund", "ปันผลสม่ำเสมอ")
        d1 = doc_of(page, "stockNotes", "PTT") or {}
        d2 = doc_of(page, "stockNotes", "PTT.BK")
        same = js(page, "()=>JSON.stringify(vwList('PTT','fund'))===JSON.stringify(vwList('PTT.BK','fund')) && vwList('PTT','fund').length===1")
        check(f"{tag} 8 PTT.BK กับ PTT ใช้โน้ตชุดเดียวกัน (doc stockNotes/PTT เท่านั้น · ไม่มี PTT.BK)", len(d1.get("fund", [])) == 1 and d2 is None and same, json.dumps([d1, d2], ensure_ascii=False))
        check(f"{tag} 8 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def gl3_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, c, page, ce, pe, _ = GL3.launch(pw, w, h)
    try:
        G.go_today(page)
        names = js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=homework] [data-hw-part]')].map(e=>e.innerText.trim())")
        check(f"{tag} 9 ชิปการบ้านครบ 5: ธุรกิจ · ทำไม · ติดตาม · ออก · Tier (part ที่ 3 = 'ติดตาม')", names == ["Tier", "ธุรกิจ", "ทำไม", "ติดตาม", "ออก"], json.dumps(names, ensure_ascii=False))
        m = js(page, "()=>{ const bs=[...document.querySelectorAll('.tdRow[data-kind=homework] .tdHp')]; const cs=bs.map(b=>b.getBoundingClientRect()); const mid=cs.map(r=>r.top+r.height/2); return {clip:bs.map(b=>b.scrollWidth>b.clientWidth+0.5), ell:bs.map(b=>getComputedStyle(b).textOverflow), oneRow:Math.max(...mid)-Math.min(...mid)<4, ovf:document.documentElement.scrollWidth-innerWidth, cntClip:(()=>{const r=document.querySelector('.tdRow[data-kind=homework]').getBoundingClientRect(); return cs.some(x=>x.right>r.right+0.5);})()}; }")
        check(f"{tag} 9 ชิป 5 ตัวแถวเดียว · ข้อความชิปไม่ถูกตัด (scrollWidth ≤ clientWidth) · ไม่ล้นแนวนอน", m["oneRow"] and not any(m["clip"]) and m["ovf"] <= 0 and not m["cntClip"], json.dumps(m))
        check(f"{tag} 9 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def narrow_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    ideas = [idea([cand("CAA", "Cand A", 1, "study"), cand("CBB", "Cand B", 2, "wait")])]
    notes = {"AVGO": {"event": [{"id": "e1", "d": "2026-10-07", "t": "ประกาศดีล custom ASIC รายใหม่ · รอยืนยัน capex และวันที่ส่งมอบจริงจากผู้บริหารรอบหน้า"}], "fund": [], "tech": [{"id": "t1", "d": "2026-10-08", "t": "พักใกล้ EMA10 W · รอ break 380 และต้องดูปริมาณซื้อขายประกอบด้วย", "chart": TV2}], "updated_at": "x"},
             "CAA": {"event": [], "fund": [{"id": "f1", "d": "2026-10-09", "t": "backlog โต · margin 50% ซึ่งสูงกว่าคู่แข่งในกลุ่มอย่างมีนัย"}], "tech": [], "updated_at": "x"}}
    b, c, page, ce, pe, dl, env = launch(pw, w, h, wl=[("AVGO", AVGO_TH, {})], ideas=ideas, notes=notes)
    try:
        P40.go_watch(page); js(page, "()=>wlOpen('AVGO','view')"); wait(page, 400)
        rows_h = js(page, "()=>[...document.querySelectorAll('.wlDBody [data-vw-row]')].map(e=>{ const kids=[...e.children]; const mid=kids.map(k=>k.getBoundingClientRect().top+k.getBoundingClientRect().height/2); return {h:Math.round(e.getBoundingClientRect().height), one:Math.max(...mid)-Math.min(...mid)<8, ell:getComputedStyle(e.querySelector('.vwT')).textOverflow, ws:getComputedStyle(e).whiteSpace}; })")
        check(f"{tag} 10 แถวมุมมองบรรทัดเดียว (ข้อความยาว → …) ทั้ง 3 แถว", all(r["one"] and r["ell"] == "ellipsis" and r["ws"] == "nowrap" for r in rows_h) and len(rows_h) == 3, json.dumps(rows_h))
        tb = js(page, "()=>{ const t=document.querySelector('[data-lt-tabs]'); return {ovf:document.documentElement.scrollWidth-innerWidth, sw:t.scrollWidth, cw:t.clientWidth}; }")
        check(f"{tag} 10 แถบแท็บการ์ดไม่ล้นหน้า (6 แท็บ เลื่อนในแถบเอง)", tb["ovf"] <= 0 and tb["sw"] >= tb["cw"], json.dumps(tb))
        page.locator('.wlDBody [data-vw-row="tech"]').click(); wait(page, 300)
        fs = js(page, "()=>[...document.querySelectorAll('.wlDBody .vwX input')].map(i=>parseFloat(getComputedStyle(i).fontSize))")
        check(f"{tag} 10 ช่องกรอกโน้ต/ลิงก์ font ≥ 16px (ไม่ซูมบน iOS)", len(fs) == 2 and all(x >= 16 for x in fs), json.dumps(fs))
        bad = js(page, "()=>{ const W=innerWidth; return [...document.querySelectorAll('.wlDBody *')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && (r.right>W+1 || r.left<-1); }).slice(0,5).map(e=>e.className+':'+Math.round(e.getBoundingClientRect().right)); }")
        check(f"{tag} 10 ไม่ล้นแนวนอนราย element ในการ์ด (เปิดมุม Tech + ภาพ 110px)", not bad and overflow(page) <= 0, json.dumps(bad))
        js(page, "()=>wlSetView('cand')"); wait(page, 300)
        page.locator('.wlRows .wlR[data-sym="CAA"]').click(); wait(page, 400)
        rh = js(page, "()=>[...document.querySelectorAll('.wlRows .wlR')].map(e=>{ const mid=[...e.children].filter(k=>k.getBoundingClientRect().height>0).map(k=>k.getBoundingClientRect().top+k.getBoundingClientRect().height/2); return {sym:e.dataset.sym, h:Math.round(e.getBoundingClientRect().height), one:Math.max(...mid)-Math.min(...mid)<6}; })")
        check(f"{tag} 10 แถว Candidate บรรทัดเดียว (มี • และกำลังขยาย)", all(r["one"] and r["h"] <= 52 for r in rh), json.dumps(rh))
        bad2 = js(page, "()=>{ const W=innerWidth; return [...document.querySelectorAll('.wlRows *')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && (r.right>W+1 || r.left<-1); }).slice(0,5).map(e=>e.className+':'+Math.round(e.getBoundingClientRect().right)); }")
        rows_c = js(page, "()=>[...document.querySelectorAll('[data-cand-x] [data-vw-row]')].map(e=>{ const mid=[...e.children].map(k=>k.getBoundingClientRect().top+k.getBoundingClientRect().height/2); return Math.max(...mid)-Math.min(...mid)<8; })")
        check(f"{tag} 10 แถวขยายใน Candidate: 3 แถวบรรทัดเดียว · ไม่ล้นแนวนอน", not bad2 and all(rows_c) and len(rows_c) == 3 and overflow(page) <= 0, json.dumps([bad2, rows_c]))
        go_sat(page)
        js(page, "()=>satwWrite('XAUUSD', {chart:{url:'" + TV1 + "', at:'2026-10-09'}})"); wait(page, 500)
        bad3 = js(page, "()=>{ const W=innerWidth; return [...document.querySelectorAll('#satV3Sum *')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && (r.right>W+1 || r.left<-1); }).slice(0,5).map(e=>e.className+':'+Math.round(e.getBoundingClientRect().right)); }")
        check(f"{tag} 10 Sat Strategy มีแถบกราฟ ไม่ล้นแนวนอนราย element · หน้าไม่ล้น", not bad3 and overflow(page) <= 0, json.dumps(bad3))
        page.locator(".ui-tile[data-key=BTCUSD] [data-vw-sat-add]").click(); wait(page, 250)
        fs3 = js(page, "()=>parseFloat(getComputedStyle(document.querySelector('[data-vw-sat-in]')).fontSize)")
        check(f"{tag} 10 ช่องวางลิงก์กราฟ Sat font ≥ 16px", fs3 >= 16, str(fs3))
        check(f"{tag} 10 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            sat_tests(pw, w, h, label)
            wl_tests(pw, w, h, label)
            gl3_tests(pw, w, h, label)
            if w < 500: narrow_tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
