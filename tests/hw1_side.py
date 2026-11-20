#!/usr/bin/env python3
"""HW1 — side-by-side proof: docs/briefs/lr/HomeworkWatch2.html (left, A / B / C) | live app (right). Writes tests/screenshots/hw1/{A-1440,B-1440,C-390}-side.png. Run: python3 tests/hw1_side.py"""
import os, base64, copy
from playwright.sync_api import sync_playwright
import hw1_common as H
import lr5_common as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "screenshots", "hw1")
MOCK = "file://" + os.path.abspath(os.path.join(HERE, "..", "docs", "briefs", "lr", "HomeworkWatch2.html"))
os.makedirs(OUT, exist_ok=True)
CF = copy.deepcopy(H.COMP)


def uri(p): return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


def side(a, b, out, wa, wb):
    html = f"<body style='margin:0;background:#888;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{wa}px'><img src='{uri(b)}' style='display:block;width:{wb}px'></body>"
    return html


def mock_shot(pw, w, sel_idx, kind, path):
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": w + 60, "height": 900}); pg.goto(MOCK); pg.wait_for_timeout(800)
    el = pg.query_selector_all(".frame")[sel_idx] if kind == "frame" else pg.query_selector(".ph")
    el.screenshot(path=path); b.close()


def seed(page):
    items = [("WHSE", {"ladder_watch": True, "ladder_watch_set": True, "exch": "NYSE", "sector_etf": "XLK", "my_thesis": {"why": "Fee increase next year → profit jumps", "evidence": "Fee revenue is large vs operating income (50%) · margin rising 4 quarters · renewals still above 92%.", "unproven": "Timing of the fee increase · how much profit a fee rise adds"}, **{"thesis": H.tok(C.thesis_fields("AVGO"))["thesis"]}}),
             ("MSFT", {"ladder_watch": True, "ladder_watch_set": True, "exch": "NASDAQ", "sector_etf": "IGV", "my_thesis": {"why": "Cloud + AI", "evidence": "Azure growth", "exit": "Azure growth under 25%"}, "hw": {"catalyst": "Q2 28 Jan", "confirmedAt": "2026-11-12T03:00:00Z", "doneAt": "2026-11-12T03:00:00Z"}}),
             ("VISA", {"ladder_watch": True, "ladder_watch_set": True, "exch": "NYSE", "sector_etf": "XLK"})]
    for t, x in items:
        js(page, "([t,x])=>wlCol().doc(t).set(Object.assign({ticker:t, market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'}, x))", [t, x])
    th = {"track": "compounder"}
    page.wait_for_timeout(400)
    page.evaluate("(f)=>{ const it = wlItemOf('WHSE'); it.thesis = Object.assign({}, it.thesis, {facts:f}); }", CF)
    js(page, "()=>{ for(const t of ['AAPL','AVGO','GE','PLTR','AMD','COST']){ const it = wlItemOf(t); if(it) it.archived = true; } wl1Trk = 'ladder'; wlSetView('wl'); renderWatchlist(); }")
    page.wait_for_timeout(300)


def live(pw, w, h, name, prep):
    b, page, pe = C.open_watch(pw, w, h, ideas=False)
    try:
        seed(page)
        if w <= 600: page.add_style_tag(content="#tabsMain{display:none!important}")
        prep(page); page.wait_for_timeout(500); page.mouse.move(2, 2)
        p = os.path.join(OUT, f"{name}-live.png"); page.screenshot(path=p, full_page=True); return p
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        jobs = [("A-1440", 1440, 900, 0, "frame", lambda p: js(p, "()=>{ wlOpen('WHSE'); }")),
                ("B-1440", 1440, 900, 1, "frame", lambda p: (js(p, "()=>{ hwOpen('WHSE'); document.querySelectorAll('.hw1-fr.tap').forEach(x=>{ if(x.innerText.includes('Fees vs profit')) x.click(); }); }"))),
                ("C-390", 390, 844, 0, "ph", lambda p: js(p, "()=>{ hwOpen('WHSE'); hw1SegSet('WHSE','mine'); }"))]
        for name, w, h, idx, kind, prep in jobs:
            m = os.path.join(OUT, f"{name}-mock.png"); mock_shot(pw, w, idx, kind, m)
            l = live(pw, w, h, name, prep)
            br = pw.chromium.launch(); pg = br.new_page(viewport={"width": 2 * w + 8, "height": 900})
            pg.set_content(side(m, l, None, w, w)); pg.wait_for_timeout(300)
            pg.screenshot(path=os.path.join(OUT, f"{name}-side.png"), full_page=True); br.close(); print(name, "ok")
    for f in os.listdir(OUT):
        if f.endswith(("-mock.png", "-live.png")): os.remove(os.path.join(OUT, f))


if __name__ == "__main__":
    main()
