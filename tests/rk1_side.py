#!/usr/bin/env python3
"""RK1 — side-by-side: mockup (docs/briefs/lr/SettingsRisk.html) | built Settings › Portfolio & Risk at 1440 and 390 → tests/screenshots/rk1/side-<w>.png"""
import os, sys
from playwright.sync_api import sync_playwright
import base64
from re1d_common import js, launch
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "screenshots", "rk1"); os.makedirs(OUT, exist_ok=True)
MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr", "SettingsRisk.html")
with sync_playwright() as pw:
    for w, h in ((1440, 900), (390, 844)):
        b = pw.chromium.launch(); pg = b.new_page(viewport={"width": 640 if w > 600 else 430, "height": 760}); pg.goto("file://" + os.path.abspath(MOCK)); pg.wait_for_timeout(300)
        pg.locator(".card").first.screenshot(path=os.path.join(OUT, "_mock-%d.png" % w)); b.close()
        b, page, ce, pe = launch(pw, w, h)
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; openSettings(); const s = document.getElementById('ps1Sec'); s.open = true; s.scrollIntoView({block:'start'}); }"); page.wait_for_timeout(500)
        page.add_style_tag(content="@media (max-width:600px){#tabsMain{display:none!important}}")
        page.locator("#ps1Sec").screenshot(path=os.path.join(OUT, "_app-%d.png" % w)); b.close()
        uri = lambda n: "data:image/png;base64," + base64.b64encode(open(os.path.join(OUT, n), "rb").read()).decode()
        b2 = pw.chromium.launch(); p2 = b2.new_page(viewport={"width": 1500 if w > 600 else 900, "height": 400})
        p2.set_content('<body style="margin:0;background:#E9EBEF"><div style="display:flex;gap:24px;align-items:flex-start;padding:0"><div><div style="font:600 12px sans-serif;color:#555;padding:4px">built</div><img src="%s"></div><div><div style="font:600 12px sans-serif;color:#555;padding:4px">mockup</div><img src="%s"></div></div></body>' % (uri("_app-%d.png" % w), uri("_mock-%d.png" % w)))
        p2.wait_for_timeout(300); p2.locator("body").screenshot(path=os.path.join(OUT, "side-%d.png" % w)); b2.close()
        os.remove(os.path.join(OUT, "_mock-%d.png" % w)); os.remove(os.path.join(OUT, "_app-%d.png" % w))
print("ok")
