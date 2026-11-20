#!/usr/bin/env python3
"""RS2b — side-by-side proof: mockup ScreenIndustries.html (left) | live (right). Writes tests/screenshots/rs2b/*-side.png only. Run: python3 tests/rs2b_side.py"""
import os, base64
from playwright.sync_api import sync_playwright
import rs2a_common as C
import run_tests_rs2b as T
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "rs2b")
MOCK = os.path.abspath(os.path.join(HERE, "..", "docs", "briefs", "lr", "ScreenIndustries.html"))
os.makedirs(OUT, exist_ok=True)
TMP = os.path.join(OUT, "_tmp"); os.makedirs(TMP, exist_ok=True)


def mock(pw, sel, idx, name):
    b = pw.chromium.launch(); page = b.new_page(viewport={"width": 1440, "height": 900})
    page.goto("file://" + MOCK); page.wait_for_timeout(800)
    p = os.path.join(TMP, name + "-mock.png"); page.locator(sel).nth(idx).screenshot(path=p); b.close(); return p


def side(pw, a, b_, out, wa, wb):
    def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{wa}px'><img src='{uri(b_)}' style='display:block;width:{wb}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": wa + wb + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close()


def live(pw, w, h, name, prep, sel=None):
    b, page, pe, ce = T.opened(pw, w, h, T.build(), view="stocks")
    try:
        (w <= 600) and page.add_style_tag(content="#tabsMain{display:none!important}")
        prep(page); page.mouse.move(2, 2); p = os.path.join(TMP, name + "-live.png")
        (page.locator(sel).first.screenshot(path=p) if sel else page.screenshot(path=p, full_page=(w <= 600))); return p
    finally:
        b.close()


def prep_a(p):
    p.click("[data-rs2-view=ind]"); p.wait_for_timeout(400)


def prep_b(p):
    p.click("[data-rs2-view=ind]"); p.wait_for_timeout(300)
    p.click("[data-rs2-ind-row][data-ind=Semiconductors] [data-rs2-ind-go]"); p.wait_for_timeout(400)


def main():
    with sync_playwright() as pw:
        m = mock(pw, ".frame", 0, "a"); l = live(pw, 1440, 900, "a", prep_a, sel=".lr5-screen")
        side(pw, m, l, os.path.join(OUT, "industries-1440-side.png"), 1392, 1440); print("A ok")
        m = mock(pw, ".frame", 1, "b"); l = live(pw, 1440, 900, "b", prep_b, sel="[data-rs2-filters]")
        side(pw, m, l, os.path.join(OUT, "industries-chip-1440-side.png"), 1392, 1100); print("B ok")
        m = mock(pw, ".ph", 0, "c"); l = live(pw, 390, 844, "c", prep_a)
        side(pw, m, l, os.path.join(OUT, "industries-390-side.png"), 390, 390); print("C ok")
    import shutil; shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    main()
