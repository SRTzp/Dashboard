#!/usr/bin/env python3
"""RS2a3 — side-by-side proof: mockup ScreenRS3.html (left) | live (right). Writes tests/screenshots/rs2a3/*. Run: python3 tests/rs2a3_side.py"""
import os, base64
from playwright.sync_api import sync_playwright
import rs2a_common as C
import run_tests_rs2a3 as T
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "rs2a3")
MOCK = os.path.abspath(os.path.join(HERE, "..", "docs", "briefs", "lr", "ScreenRS3.html"))
os.makedirs(OUT, exist_ok=True)


def mock(pw, w, h, sel, name):
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": w, "height": h})
    page.goto("file://" + MOCK); page.wait_for_timeout(1000)
    p = os.path.join(OUT, f"{name}-mock.png"); page.locator(sel).first.screenshot(path=p); b.close(); return p


def side(pw, a, b_, out, wa, wb):
    def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{wa}px'><img src='{uri(b_)}' style='display:block;width:{wb}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": wa + wb + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close()


def live(pw, w, h, name, prep, sel=None, go=True):
    b, page, pe, ce = C.open_screen(pw, w, h, data=T.data(), wl=T.WL, go=go)
    try:
        (w <= 600) and page.add_style_tag(content="#tabsMain{display:none!important}")
        prep(page); page.mouse.move(2, 2); p = os.path.join(OUT, f"{name}-live.png")
        (page.locator(sel).first.screenshot(path=p) if sel else page.screenshot(path=p, full_page=(w <= 600))); return p
    finally:
        b.close()


def prep_a(p):
    p.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"); p.wait_for_timeout(300)
    for s in ("NVDA", "ZETA", "APP"): p.click(f"[data-rs2-tick={s}]")
    p.click("[data-rs2-row][data-sym=GE] [data-rs2-add=done]"); p.wait_for_timeout(300)


def prep_c(p):
    p.click("[data-rs2-dots]"); p.wait_for_timeout(300)


def prep_c2(p):
    p.click("[data-rs2-row][data-sym=NVDA] [data-rs2-add=done]"); p.wait_for_timeout(300)


def prep_b(p):
    js(p, "(c)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','rs2','changes'], c); rs2Chg.at = 0; rs2Chg.doc = null; localStorage.removeItem('dash.rs2ChgSeen'); switchTab('today'); }", {"asOf": "2026-11-19", "prevAsOf": "2026-11-18", "items": [
        {"sym": "ZETA", "k": "b", "from": 84, "to": 78}, {"sym": "GE", "k": "a", "from": 91, "to": 91}, {"sym": "CRDO", "k": "d", "from": 78, "to": 95}]})
    p.wait_for_timeout(1200); js(p, "()=>todayRefresh(true)"); p.wait_for_timeout(500)


def main():
    with sync_playwright() as pw:
        m = mock(pw, 1440, 900, ".frame", "screen-1440"); l = live(pw, 1440, 900, "screen-1440", prep_a)
        side(pw, m, l, os.path.join(OUT, "screen-1440-side.png"), 1392, 1440); print("A ok")
        m = mock(pw, 1440, 900, ".today", "today"); l = live(pw, 1440, 900, "today", prep_b, sel="[data-ln4-todorow]", go=False)
        side(pw, m, l, os.path.join(OUT, "today-side.png"), 640, 480); print("B ok")
        m = mock(pw, 1440, 900, ".ph", "screen-390"); l = live(pw, 390, 844, "screen-390", prep_c)
        side(pw, m, l, os.path.join(OUT, "screen-390-side.png"), 390, 390); print("C ok")
        l = live(pw, 390, 844, "sheet-390", prep_c2)
        side(pw, m, l, os.path.join(OUT, "screen-390-sheet-side.png"), 390, 390); print("C2 ok")
    for f in os.listdir(OUT):
        if f.endswith(("-mock.png", "-live.png")): os.remove(os.path.join(OUT, f))


if __name__ == "__main__":
    main()
