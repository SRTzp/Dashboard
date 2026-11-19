#!/usr/bin/env python3
"""LR5b — side-by-side proof: mockup (left) | live (right), same width. Writes tests/screenshots/lr5b/*
Run: python3 tests/lr5b_side.py"""
import os, base64
from playwright.sync_api import sync_playwright
import lr5b_common as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "lr5b"); os.makedirs(OUT, exist_ok=True)


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
    b, page, pe = C.open_journal(pw, w, h)
    try:
        js(page, "()=>lrSwPick('journal','both')"); page.wait_for_timeout(300)
        page.add_style_tag(content="@media (max-width:600px){#tabsMain{display:none!important}}")  # CLEAN1: whole-page shots hide the nav only at <=600px
        if prep: prep(page)
        page.mouse.move(2, 2); p = os.path.join(OUT, f"{name}-{w}-live.png"); page.screenshot(path=p, full_page=True)
        return p
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h, mf in ((1440, 900, "Journal.dc.html"), (390, 844, "JournalPhone.dc.html")):
            m = mock(pw, w, h, mf, "journal"); l = live(pw, w, h, "journal")
            side(pw, m, l, os.path.join(OUT, f"journal-{w}-side.png"), w)
        def rv(page): js(page, "()=>lr5Pick('main:x1')"); page.wait_for_timeout(400)
        p = live(pw, 390, 844, "journal-review", rv); os.replace(p, os.path.join(OUT, "journal-390-review-live.png"))
        def nt(page): js(page, "()=>{ document.querySelector('[data-lr5-nt]').open = true; }"); page.wait_for_timeout(200)
        p = live(pw, 1440, 900, "journal-both", nt); os.replace(p, os.path.join(OUT, "journal-1440-both-live.png"))


if __name__ == "__main__":
    main()
