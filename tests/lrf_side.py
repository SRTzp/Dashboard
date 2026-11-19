#!/usr/bin/env python3
"""LR-F — side-by-side proof: mockup (left) | live (right), same width, same fixture data.
Writes tests/screenshots/lrf/<screen>-<width>-side.png (+ -live.png / -mock.png).
Run: LRF='plan sheet' python3 tests/lrf_side.py   screens: plan today sheet"""
import os, sys, base64
from playwright.sync_api import sync_playwright
import net_stub
import re1d_common as K
from re1d_common import js, launch, plan_card
import pv1_common as PV

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "lrf")
MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr")
os.makedirs(OUT, exist_ok=True)


def fixture():
    """Mockup data: XAU SAT long (ready) · AVGO MMT 2 levels tp 175 · BTC SAT short (blocked) · PLTR/MSFT waiting · NVDA ordered · NVDA COMP + BTC SAT holding."""
    d = PV.doc_sat()
    cs = PV.cards_pv()                                   # cN = NVDA COMP holding (11 @ 158, stop 110)
    cs["mA"] = plan_card("AVGO", 158, 150, px=160, ready=True)
    cs["mA"]["plan"]["ps1"]["rows"] = [{"px": 158, "qty": 20}, {"px": 150, "qty": 20}]
    cs["mA"]["plan"]["tp"] = 175
    cs["mW"] = plan_card("PLTR", 0, 0, px=30); cs["mW"]["plan"] = {"entry": 0, "stop": 0}
    cs["mM"] = plan_card("MSFT", 0, 0, px=400); cs["mM"]["plan"] = {"entry": 0, "stop": 0}; cs["mM"]["track"] = "ladder"
    cs["mO"] = plan_card("NVDA", 120, 112, px=121, ready=True); cs["mO"]["plan"]["ps1"]["rows"] = [{"px": 120, "qty": 50}]
    import datetime
    cs["mO"]["ln4"] = {"placedAt": (datetime.datetime.utcnow() - datetime.timedelta(hours=30)).strftime("%Y-%m-%dT%H:%M:%SZ")}
    return d, cs


def go(page, tab):
    js(page, "()=>{ serverConfirmed = true; stateFromServer = true; if(acctActive !== 'main') acctSwitch('main'); bdChip='all'; bdSeg='plan'; re1Cache = {}; }")
    js(page, PV.SAT_JS); js(page, PV.SAT_PLANS_JS.replace("mk('pb','XAGUSD','Long',30,29.5,32);", "")); page.wait_for_timeout(500)
    js(page, "()=>{ const B=getBook('main'); B.settings.psRisk = Object.assign({}, B.settings.psRisk||{}, {minStop:{XAUUSD:0.1}}); saveBook('main'); }")
    js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','XAGUSD']); re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(300)
    js(page, "(t)=>{ switchTab(t); if(t==='plan') bdRender(); }", tab); page.wait_for_timeout(500)


def live(pw, w, h, tab, name, prep=None, full=False):
    d, cs = fixture()
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    try:
        go(page, tab)
        page.add_style_tag(content="@media (max-width:600px){#tabsMain{display:none!important}}")  # CLEAN1: whole-page shots hide the nav only at <=600px
        if prep: prep(page)
        p = os.path.join(OUT, f"{name}-{w}-live.png")
        page.screenshot(path=p, full_page=full)
        return p
    finally:
        b.close()


def mock(pw, w, h, file, name, full=False):
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": w, "height": h})
    page.goto("file://" + os.path.abspath(os.path.join(MOCK, file))); page.wait_for_timeout(900)
    p = os.path.join(OUT, f"{name}-{w}-mock.png"); page.screenshot(path=p, full_page=full); b.close(); return p


def side(pw, a, b_, out, w):
    def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px'><img src='{uri(a)}' style='display:block;width:{w}px'><img src='{uri(b_)}' style='display:block;width:{w}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 2 * w + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close()


def make(pw, screen, w, h, mfile, tab, prep=None, full=False):
    name = screen
    m = mock(pw, w, h, mfile, name, full); l = live(pw, w, h, tab, name, prep, full)
    side(pw, m, l, os.path.join(OUT, f"{name}-{w}-side.png"), w)
    print("wrote", f"{name}-{w}-side.png")


def fam_fixture(page):
    """LR-F2 — a 2-account book: Main (above) + Family = XAU same idea (Family size) · MSFT core plan · open S50 futures (F futures leverage in the open-risk line)."""
    K.seed(page, {"fM": dict(plan_card("MSFT", 400, 380, px=401, ready=True), acct="fam")})
    js(page, """()=>{ sat7dWrite('satIdeas','fX',{id:'fX',v3:true,v2:true,ready:true,readyAt:new Date().toISOString(),asset:'XAUUSD',bias:'Long',entry:2643,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'fam'});
      const FB = getBook('fam'); FB.settings.psRisk = Object.assign({}, FB.settings.psRisk||{}, {minStop:{XAUUSD:0.1}}); 
      const B = getBook('fam'); B.trades = (B.trades || []).concat([{id:'tfut', sym:'S50', port:'fut', status:'open', qty:80, entry:900, mult:1, date:'2026-11-17'}]); saveBook('fam'); (satIdeasList || []).filter(i=>i && i.asset === 'XAUUSD').forEach(i=>sat7dWrite('satIdeas', i.id, Object.assign({}, i, {ready:true, readyAt:new Date().toISOString()}))); re1Cache = {}; }""")
    page.wait_for_timeout(400)


def today_prep(page):
    import run_tests_lr2 as L2
    fam_fixture(page)
    js(page, "()=>{ re2GrpAll = {}; lr2DetOpen = false; }"); L2.seed_wi(page); L2.seed_rrg(page); L2.set_regime(page, "red", "red"); page.wait_for_timeout(300)


def sheet_prep(page):
    js(page, "()=>efCorePlaceOpen('mA')"); page.wait_for_timeout(500)


def extras(pw):
    """live-only phone views the phone mockups do not draw: Ordered and Holding tabs (Holding fixture included)"""
    for seg in ("ord", "hold"):
        live(pw, 390, 844, "plan", "plan-%s" % seg, prep=lambda p, s=seg: (js(p, "(s)=>{ bdSetSeg(s); }", s), p.wait_for_timeout(300)))


JOBS = {
    "plan": [(390, 844, "PlanPhone.dc.html", "plan", None, False), (1440, 900, "Plan.dc.html", "plan", None, False)],
    "today": [(390, 844, "TodayPhone.dc.html", "today", today_prep, False), (1440, 900, "Main.dc.html", "today", today_prep, False)],
    "sheet": [(390, 844, "PlacePhone.dc.html", "plan", sheet_prep, False), (1440, 900, "PlacePhone.dc.html", "plan", sheet_prep, False)],
}

if __name__ == "__main__":
    want = os.environ.get("LRF", "").split() or list(JOBS)
    with sync_playwright() as pw:
        for s in want:
            for (w, h, f, tab, prep, full) in JOBS[s]:
                make(pw, s, w, h, f, tab, prep, full)
        if "plan" in want: extras(pw)
        if "today" in want: live(pw, 390, 844, "today", "today-full", prep=today_prep, full=True)   # LR-F2: whole phone page incl. To do → Risk room → Details
