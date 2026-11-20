#!/usr/bin/env python3
"""TD5 — side-by-side: mockup (docs/briefs/lr/TodayMyTodo.html states 1 · 2 · 3) vs the app's To do card in the same state. Writes tests/screenshots/td5/td5-side-{1440,390}.png"""
import os, base64, tempfile
from playwright.sync_api import sync_playwright
from re1d_common import js, launch

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "screenshots", "td5"); os.makedirs(OUT, exist_ok=True)
MOCK = os.path.join(os.path.dirname(HERE), "docs", "briefs", "lr", "TodayMyTodo.html")
ENGINE = """()=>{ window.__o = window.__o || ln4TodoItems; ln4TodoItems = function(M){ return [
  {c:'r', id:'t:r1', t:'Move stop AVGO +1.5R', fn:"void 0"}, {c:'a', id:'t:a1', t:'WHSE homework · 2 of 3', fn:"void 0"}, {c:'g', id:'t:g1', t:'Snapshot due Friday', fn:"void 0"}, {c:'g', id:'t:g2', t:'Weekly impact', fn:"void 0"}, {c:'g', id:'t:g3', t:'Playbook review', fn:"void 0"}]; }; todayRefresh(true); }"""
CARD = "[data-ln4-todorow]"
enc = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

with sync_playwright() as pw, tempfile.TemporaryDirectory() as td:
    bm = pw.chromium.launch(); pm = bm.new_page(viewport={"width": 1200, "height": 900}); pm.goto("file://" + MOCK)
    mk = []
    for i, c in enumerate(pm.query_selector_all(".col")[:3]):
        p = os.path.join(td, "m%d.png" % i); c.screenshot(path=p); mk.append(p)
    bm.close()
    for w, h in ((1440, 900), (390, 844)):
        b, page, ce, pe = launch(pw, w, h)
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
        js(page, ENGINE); page.wait_for_timeout(200)
        for t in ("Call broker about W-8BEN renewal", "Read NVDA 10-Q segment table before Wednesday's call"):
            page.click("[data-td5-plus]"); page.fill("[data-td5-add]", t); page.press("[data-td5-add]", "Enter"); page.wait_for_timeout(150)
        ap = []
        p = os.path.join(td, "a0.png"); page.query_selector(CARD).screenshot(path=p); ap.append(p)
        page.click("[data-td5-plus]"); page.fill("[data-td5-add]", "Rebalance Family account"); page.wait_for_timeout(100)
        p = os.path.join(td, "a1.png"); page.query_selector(CARD).screenshot(path=p); ap.append(p)
        page.press("[data-td5-add]", "Escape"); page.wait_for_timeout(100)
        js(page, "()=>document.querySelectorAll('[data-td5-row] .td5-t')[1].click()"); page.wait_for_timeout(200)
        p = os.path.join(td, "a2.png"); page.query_selector(CARD).screenshot(path=p); ap.append(p)
        b.close()
        rows = "".join(f"<div style='display:flex;gap:24px;align-items:flex-start;margin-bottom:16px'><div><div>Mockup {i+1}</div><img src='{enc(mk[i])}'></div><div><div>App {w}px</div><img src='{enc(ap[i])}'></div></div>" for i in range(3))
        bb = pw.chromium.launch(); pg = bb.new_page(viewport={"width": 900, "height": 700}); pg.set_content(f"<body style='margin:0;background:#fff;font:600 13px sans-serif'><div style='padding:16px'>{rows}</div>"); pg.wait_for_timeout(300)
        pg.screenshot(path=os.path.join(OUT, "td5-side-%d.png" % w), full_page=True); bb.close()
print("ok")
