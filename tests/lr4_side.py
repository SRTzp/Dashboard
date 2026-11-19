#!/usr/bin/env python3
"""LR4 — side-by-side proof: mockup (left) | live (right), same width. Writes tests/screenshots/lr4/*.
Run: python3 tests/lr4_side.py"""
import os, sys, base64
from playwright.sync_api import sync_playwright
import lr4_common as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "lr4")
os.makedirs(OUT, exist_ok=True)


def mock(pw, w, h, file, name):
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": w, "height": h})
    page.goto("file://" + os.path.abspath(os.path.join(C.MOCK, file))); page.wait_for_timeout(1200)
    p = os.path.join(OUT, f"{name}-{w}-mock.png"); page.screenshot(path=p, full_page=True); b.close(); return p


def side(pw, a, b_, out, w):
    def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{w}px'><img src='{uri(b_)}' style='display:block;width:{w}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 2 * w + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close()


def live(pw, w, h, name, prep=None):
    b, page, pe = C.open_flow(pw, w, h)
    try:
        page.add_style_tag(content="@media (max-width:600px){#tabsMain{display:none!important}}")  # CLEAN1: whole-page shots hide the nav only at <=600px
        if prep: prep(page)
        page.evaluate("()=>{ try{ tw1TipHide(); }catch(e){} document.querySelectorAll('[data-tw1-tip]').forEach(n=>n.remove()); }"); page.mouse.move(2, 2); p = os.path.join(OUT, f"{name}-{w}-live.png"); page.screenshot(path=p, full_page=True)
        H = js(page, "()=>document.documentElement.scrollHeight")
        return p, H
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h, mf in ((1440, 900, "Flow.dc.html"), (390, 844, "FlowPhone.dc.html")):
            m = mock(pw, w, h, mf, "flow"); l, H = live(pw, w, h, "flow")
            side(pw, m, l, os.path.join(OUT, f"flow-{w}-side.png"), w); print("flow", w, "live height", H)
        # extra live shots
        def cal(page): js(page, "()=>lr4CalSheet()"); page.wait_for_timeout(400)
        p, _ = live(pw, 390, 844, "flow-calendar", cal); os.replace(p, os.path.join(OUT, "flow-390-calendar-live.png"))
        def mac(page): js(page, "()=>lr4CalTab('macro')"); page.wait_for_timeout(300)
        p, _ = live(pw, 1440, 900, "flow-macro", mac); os.replace(p, os.path.join(OUT, "flow-1440-macro-live.png"))


if __name__ == "__main__":
    main()
