#!/usr/bin/env python3
"""NT1 — side-by-side proof: mockup (left) | live app (right) → tests/screenshots/nt1/*-side.png. Run: python3 tests/nt1_side.py
 AI-generated-1440 (IdeasAI.html) · My-ideas-1440 (TradeNotes.html A) · New-idea-sheet (B) · Context-lines (C: Flow · Watch detail · Today) · Journal-Reviews-1440 (D) · AI-generated-390 / My-ideas-390 (phone, live only)"""
import os, base64
from playwright.sync_api import sync_playwright
import nt1_common as N, run_tests_nt1 as T
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "nt1")
LR = os.path.abspath(os.path.join(HERE, "..", "docs", "briefs", "lr"))
os.makedirs(OUT, exist_ok=True)


def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def pw_w(p):
    import struct
    return struct.unpack('>I', open(p, 'rb').read()[16:20])[0]


def mock_shot(pw, file, sel, idx, path, w=1500):
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 900}); pg.goto("file://" + os.path.join(LR, file)); pg.wait_for_timeout(800)
    pg.query_selector_all(sel)[idx].screenshot(path=path); b.close()


def compose(pw, a, b_, out, wa, wb):
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": wa + wb + 8, "height": 100})
    pg.set_content(f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{wa}px'><img src='{uri(b_)}' style='display:block;width:{wb}px'></body>")
    pg.wait_for_timeout(300); pg.screenshot(path=out, full_page=True); br.close()


def rich_ai(page):
    import lr5_common as C
    d = C.idea_doc("nt1-idea-3", "Grid power demand"); d["status"] = "need_evidence"; d["scope"] = ["US"]
    d["candidates"] = [{"sym": s, "name": s, "state": "study", "segments": [], "relevance_src": "10-K"} for s in ("VST", "CEG", "ETN", "GEV", "PWR", "NRG")]
    page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", ["nt1-idea-3", {"idea": {k: v for k, v in d.items() if k != "log"}, "idea_log": d.get("log", []), "user": {}}])
    page.wait_for_timeout(400)


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 300" preserveAspectRatio="none"><rect width="800" height="300" fill="#EEF2F9"/><polyline fill="none" stroke="#14161A" stroke-width="2" points="0,220 80,200 160,210 240,170 320,180 400,140 480,150 560,110 640,120 720,90 800,80"/><polyline fill="none" stroke="#9A5B00" stroke-width="1.5" stroke-dasharray="4 4" points="0,150 160,160 320,175 480,190 640,205 800,215"/></svg>"""


def live(pw, w, h, path, prep, clip=None):
    b, page, pe = N.open_nt1(pw, w, h)
    try:
        page.route("**://s3.tradingview.com/**", lambda r: r.fulfill(status=200, content_type="image/svg+xml", body=SVG))   # the sample chart image (no network in tests)
        if w <= 600: page.add_style_tag(content="#tabsMain{display:none!important}")
        T.extra_ai(page); rich_ai(page)
        prep(page); page.wait_for_timeout(500); page.mouse.move(2, 2)
        (page.query_selector(clip).screenshot(path=path) if clip else page.screenshot(path=path))
    finally:
        b.close()


def sheet(p):
    js(p, "()=>{ switchTab('watch'); wlView='idea'; nt1SegSet('my'); }"); js(p, "()=>nt1SheetOpen({})"); p.wait_for_timeout(200)
    p.select_option("#nt1fSubj", "market:US"); p.fill("#nt1fTitle", "Rally narrowing to AI names"); p.fill("#nt1fChart", "https://www.tradingview.com/x/AbC123/")
    p.fill("#nt1f-tech", "SPX at highs but % of stocks above the 50-day fell from 68% to 49%."); p.fill("#nt1f-plan", "Keep Momentum to RS ≥ 90 leaders only, half size."); p.fill("#nt1fCheck", "2026-12-17"); p.click('[data-nt1-fv="neutral"]')


def main():
    jobs = [
        ("AI-generated-1440", "IdeasAI.html", ".scr", 0, 1440, 900, None, lambda p: (N.goto_watch(p), js(p, "()=>{ wlView='idea'; nt1SegSet('ai'); ideaOpen('nt1-idea-3'); }"))),
        ("My-ideas-1440", "TradeNotes.html", ".scr", 0, 1440, 900, None, lambda p: (N.goto_watch(p), T.to_my(p, "m1"))),
        ("New-idea-sheet", "TradeNotes.html", ".scr", 1, 1440, 900, "#ltModal", sheet),
        ("Journal-Reviews-1440", "TradeNotes.html", ".scr", 2, 1440, 900, None, lambda p: (js(p, "()=>{ switchTab('journal'); nt1JSet('rev'); }"))),
    ]
    with sync_playwright() as pw:
        for name, f, sel, idx, w, h, clip, prep in jobs:
            m, l = os.path.join(OUT, name + "-mock.png"), os.path.join(OUT, name + "-live.png")
            mock_shot(pw, f, sel, idx, m); live(pw, w, h, l, prep, clip)
            compose(pw, m, l, os.path.join(OUT, name + "-side.png"), min(pw_w(m), 1100 if clip else 720), min(pw_w(l), 1100 if clip else 720)); print(name, "ok")
        # context lines C: three live crops next to the mockup strip
        ctxs = []
        b, page, pe = N.open_nt1(pw, 1440, 900)
        try:
            js(page, "()=>switchTab('flow')"); page.wait_for_timeout(400); page.query_selector("#nt1FlowCtx").screenshot(path=os.path.join(OUT, "c1.png"))
            js(page, "()=>{ switchTab('watch'); wl1Go('AAPL'); }"); page.wait_for_timeout(400); page.query_selector("[data-lr5-det] [data-nt1-ctx]").screenshot(path=os.path.join(OUT, "c2.png"))
            js(page, "()=>{ switchTab('today'); ln4TodoAll = true; todayRefresh(true); }"); page.wait_for_timeout(500); page.query_selector("[data-ln4-todo='idea:m3']").evaluate_handle("e=>e.closest('[data-lr2-ti]')").as_element().screenshot(path=os.path.join(OUT, "c3.png"))
        finally:
            b.close()
        mc = os.path.join(OUT, "Context-lines-mock.png"); mock_shot(pw, "TradeNotes.html", ".ctx", 0, mc)
        br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 1500, "height": 100})
        pg.set_content(f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(mc)}' style='width:720px'><div style='display:flex;flex-direction:column;gap:6px;width:720px;background:#F4F5F7;padding:8px'><img src='{uri(os.path.join(OUT, 'c1.png'))}'><img src='{uri(os.path.join(OUT, 'c2.png'))}'><img src='{uri(os.path.join(OUT, 'c3.png'))}'></div></body>")
        pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(OUT, "Context-lines-side.png"), full_page=True); br.close()
        for n in ("c1", "c2", "c3"): os.remove(os.path.join(OUT, n + ".png"))
        os.remove(mc)
        for name, prep in (("AI-generated-390", lambda p: (N.goto_watch(p), js(p, "()=>{ wlView='idea'; nt1SegSet('ai'); }"))), ("My-ideas-390", lambda p: (N.goto_watch(p), T.to_my(p)))):
            live(pw, 390, 844, os.path.join(OUT, name + "-live.png"), prep); os.replace(os.path.join(OUT, name + "-live.png"), os.path.join(OUT, name + ".png")); print(name, "ok")
    for f in os.listdir(OUT):
        if f.endswith(("-mock.png", "-live.png")): os.remove(os.path.join(OUT, f))


if __name__ == "__main__":
    main()
