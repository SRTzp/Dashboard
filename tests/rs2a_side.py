#!/usr/bin/env python3
"""RS2a — side-by-side proof: mockup (left) | live (right). Writes tests/screenshots/rs2a/*. Run: python3 tests/rs2a_side.py"""
import os, base64
from playwright.sync_api import sync_playwright
import rs2a_common as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "rs2a")
MOCKS = os.path.join(HERE, "..", "docs", "briefs", "lr")
os.makedirs(OUT, exist_ok=True)


def mock(pw, w, h, file, name):
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": w, "height": h})
    page.goto("file://" + os.path.abspath(os.path.join(MOCKS, file))); page.wait_for_timeout(1200)
    p = os.path.join(OUT, f"{name}-{w}-mock.png"); page.screenshot(path=p, full_page=True); b.close(); return p


def side(pw, a, b_, out, w):
    def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{w}px'><img src='{uri(b_)}' style='display:block;width:{w}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 2 * w + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close()


def live(pw, w, h, name, prep=None):
    b, page, pe, ce = C.open_screen(pw, w, h)
    try:
        (w <= 600) and page.add_style_tag(content="#tabsMain{display:none!important}")
        if prep: prep(page)
        page.mouse.move(2, 2); p = os.path.join(OUT, f"{name}-{w}-live.png"); page.screenshot(path=p, full_page=True); return p
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h, mf in ((1440, 900, "ScreenRS.dc.html"), (390, 844, "ScreenRSPhone.dc.html")):
            m = mock(pw, w, h, mf, "screen"); l = live(pw, w, h, "screen")
            side(pw, m, l, os.path.join(OUT, f"screen-{w}-side.png"), w); print("screen", w, "ok")


if __name__ == "__main__":
    main()
