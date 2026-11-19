#!/usr/bin/env python3
"""LR5a — side-by-side proof: mockup (left) | live (right), same width. Writes tests/screenshots/lr5a/* (+ before/after heights).
Run: python3 tests/lr5a_side.py"""
import os, sys, base64
from playwright.sync_api import sync_playwright
import lr5_common as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "lr5a")
os.makedirs(OUT, exist_ok=True)
HIDE_NAV = "#tabsMain{display:none!important}"


def mock(pw, w, h, file, name):
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": w, "height": h})
    page.goto("file://" + os.path.abspath(os.path.join(C.MOCK, file))); page.wait_for_timeout(1200)
    p = os.path.join(OUT, f"{name}-{w}-mock.png"); page.screenshot(path=p, full_page=True); b.close(); return p


def side(pw, a, b_, out, w):
    def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{w}px'><img src='{uri(b_)}' style='display:block;width:{w}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 2 * w + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close()


def live(pw, w, h, name, prep=None, ideas=False, full=True):
    b, page, pe = C.open_watch(pw, w, h, ideas=ideas)
    try:
        page.add_style_tag(content=HIDE_NAV)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(400)
        if prep: prep(page)
        page.mouse.move(2, 2); p = os.path.join(OUT, f"{name}-{w}-live.png"); page.screenshot(path=p, full_page=full)
        H = js(page, "()=>document.getElementById('tabWatch').getBoundingClientRect().height")
        return p, H
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h, mf in ((1440, 900, "Watch.dc.html"), (390, 844, "WatchPhone.dc.html")):
            m = mock(pw, w, h, mf, "watch"); l, H = live(pw, w, h, "watch", ideas=True)
            side(pw, m, l, os.path.join(OUT, f"watch-{w}-side.png"), w); print("watch", w, "live #tabWatch height", round(H))
        def sheet(page): js(page, "()=>wlOpen('AAPL')"); page.wait_for_timeout(400)
        p, _ = live(pw, 390, 844, "watch-sheet", sheet, full=False); os.replace(p, os.path.join(OUT, "watch-390-sheet-live.png"))
        def ideas(page): js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(500)
        p, _ = live(pw, 1440, 900, "watch-ideas", ideas, ideas=True); os.replace(p, os.path.join(OUT, "watch-1440-ideas-live.png"))


if __name__ == "__main__":
    main()
