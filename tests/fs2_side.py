#!/usr/bin/env python3
"""FS2 — side-by-side proof: mockup (left) | live app (right) → tests/screenshots/fs2/*-side.png. Run: python3 tests/fs2_side.py
 Business-1440 (Business6.html) · Results-Compounder-1440 + Results-Momentum-1440 (HomeworkFit.html B / A) · AI-Lite-1440 (FactSheetTabs.html panel 2, left card only) · Phone-390 (FactSheetV2.html C)."""
import os, base64
from playwright.sync_api import sync_playwright
import fs2_common as F
import lr5_common as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "fs2")
LR = os.path.abspath(os.path.join(HERE, "..", "docs", "briefs", "lr"))
os.makedirs(OUT, exist_ok=True)


def pw_w(p):
    import struct
    return struct.unpack('>I', open(p, 'rb').read()[16:20])[0]


def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def mock_shot(pw, file, sel, idx, path, w=1500):
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 900}); pg.goto("file://" + os.path.join(LR, file)); pg.wait_for_timeout(800)
    pg.query_selector_all(sel)[idx].screenshot(path=path); b.close()


def live(pw, w, h, path, prep, clip_sel=None):
    b, page, pe = F.open_fs2(pw, w, h)
    try:
        if w <= 600: page.add_style_tag(content="#tabsMain{display:none!important}")
        prep(page); page.wait_for_timeout(500); page.mouse.move(2, 2)
        if clip_sel: page.query_selector(clip_sel).screenshot(path=path)
        else: page.screenshot(path=path)
    finally:
        b.close()


def compose(pw, a, b_, out, wa, wb):
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": wa + wb + 8, "height": 900})
    pg.set_content(f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{wa}px'><img src='{uri(b_)}' style='display:block;width:{wb}px'></body>")
    pg.wait_for_timeout(300); pg.screenshot(path=out, full_page=True); br.close()


def main():
    jobs = [
        ("Business-Compounder-1440", "Business6.html", ".scr", 0, 1440, 900, None, lambda p: F.go(p, "COST", "ladder", "business")),
        ("Results-Compounder-1440", "HomeworkFit.html", ".scr", 1, 1440, 900, None, lambda p: F.go(p, "COST", "ladder", "results")),
        ("Results-Momentum-1440", "HomeworkFit.html", ".scr", 0, 1440, 900, None, lambda p: F.go(p, "AAPL", "winner", "results")),
        ("AI-Lite-1440", "FactSheetTabs.html", ".p", 1, 1440, 900, ".hw1-facts", lambda p: F.go(p, "COST", "ladder", "ai")),
        ("Phone-390", "FactSheetV2.html", ".ph", 0, 390, 844, None, lambda p: F.go(p, "COST", "ladder", "results")),
    ]
    with sync_playwright() as pw:
        for name, f, sel, idx, w, h, clip, prep in jobs:
            m, l = os.path.join(OUT, name + "-mock.png"), os.path.join(OUT, name + "-live.png")
            mock_shot(pw, f, sel, idx, m)
            live(pw, w, h, l, prep, clip)
            wm, wl = pw_w(m), pw_w(l)
            compose(pw, m, l, os.path.join(OUT, name + "-side.png"), min(wm, 720 if name.startswith("AI") else wm), min(wl, 720 if name.startswith("AI") else wl))
            print(name, "ok")
    for f in os.listdir(OUT):
        if f.endswith(("-mock.png", "-live.png")): os.remove(os.path.join(OUT, f))


if __name__ == "__main__":
    main()
