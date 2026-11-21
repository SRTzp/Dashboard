#!/usr/bin/env python3
"""PC2 — side-by-side proof: mockup (left) | live (right). Writes tests/screenshots/pc2/*.png. Run: python3 tests/pc2_side.py"""
import os, sys, base64
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, launch
import lrf_side as S
import run_tests_pc2 as T

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "screenshots", "pc2"); MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr")
os.makedirs(OUT, exist_ok=True)


def mock_shot(pw, file, sel, w, name, idx=0):
    b = pw.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 900}); pg.goto("file://" + os.path.abspath(os.path.join(MOCK, file))); pg.wait_for_timeout(700)
    p = os.path.join(OUT, name + "-mock.png"); pg.locator(sel).nth(idx).screenshot(path=p); b.close(); return p


def side(pw, a, b_, out, wa, wb):
    uri = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
    html = f"<body style='margin:0;background:#777;display:flex;gap:8px;align-items:flex-start'><img src='{uri(a)}' style='display:block;width:{wa}px'><img src='{uri(b_)}' style='display:block;width:{wb}px'></body>"
    br = pw.chromium.launch(); pg = br.new_page(viewport={"width": wa + wb + 8, "height": 900}); pg.set_content(html); pg.wait_for_timeout(300)
    pg.screenshot(path=out, full_page=True); br.close(); os.remove(a); os.remove(b_); print("wrote", os.path.basename(out))


def live_page(pw, w, h, cards=None, trades=None):
    d, cs = S.fixture()
    if trades: d["books"]["main"]["trades"] += trades
    if cards: cards(cs)
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs); S.go(page, "plan")
    page.add_style_tag(content="@media (max-width:600px){#tabsMain{display:none!important}}")
    return b, page


def main():
    with sync_playwright() as pw:
        # A · board 1440
        m = mock_shot(pw, "PlanBoardV2.html", ".scr", 1440, "board-1440", 0)
        b, page = live_page(pw, 1440, 900); l = os.path.join(OUT, "board-1440-live.png"); page.screenshot(path=l); b.close()
        side(pw, m, l, os.path.join(OUT, "board-1440-side.png"), 1440, 1440)
        # B · phone 390
        m = mock_shot(pw, "PlanBoardV2.html", ".ph2", 390, "board-390", 0)
        b, page = live_page(pw, 390, 844); l = os.path.join(OUT, "board-390-live.png"); page.screenshot(path=l, full_page=True); b.close()
        side(pw, m, l, os.path.join(OUT, "board-390-side.png"), 390, 390)
        # C · drawer (NVDA Compounder)
        m = mock_shot(pw, "PlanCardV2.html", "body", 1440, "drawer-1440", 0)
        b, page = live_page(pw, 1440, 900); js(page, "()=>bdOpen('cN')"); page.wait_for_timeout(500)
        l = os.path.join(OUT, "drawer-1440-live.png"); page.screenshot(path=l); b.close()
        side(pw, m, l, os.path.join(OUT, "drawer-1440-side.png"), 1000, 1000)
        # D · Momentum place sheet, homework not done, fields open
        def cards(cs): cs["pl"] = T.mom_plan("MOMP", 94.34, qty=1, hwf=False, tp=120, rows=[{"px": 100, "qty": 1}])
        m = mock_shot(pw, "MomentumPlaceExit.html", ".row", 1100, "place-sheet", 0)
        b, page = live_page(pw, 1100, 900, cards)
        T.hw(page, "MOMP", False)
        js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='MOMP'); const m = re1CardModel(c, null, 100, 90).m; c.plan.ps1.rows[0].qty = m.qty; coreWrite(c.id, {plan:c.plan}); }"); page.wait_for_timeout(300)
        js(page, "()=>efCorePlaceOpen('pl')"); page.wait_for_timeout(500); js(page, "()=>{ pb2.hwOpen = true; pb2Render(); }"); page.wait_for_timeout(400)
        l = os.path.join(OUT, "place-sheet-live.png"); (page.locator("#bdPop").first if page.locator("#bdPop").count() else page).screenshot(path=l); b.close()
        side(pw, m, l, os.path.join(OUT, "place-sheet-side.png"), 1100, 460)
        # E · Momentum cards (planned · top up · after T1) + editor exit row
        trades = [T.tr_held("MOMT", 17, 100, 90, "t1"), T.tr_held("MOMU", 12, 100, 90, "u1"),
                  {"port": "core", "bias": "Long", "mult": 1, "cur": "USD", "status": "closed", "date": "2026-11-13", "qty": 8, "entry": 100, "sl": 90, "tp": None, "id": "t1x", "sym": "MOMT", "posGroup": "t1", "sl0": 90, "exitPrice": 120, "exitDate": "2026-11-18", "closedAt": "2026-11-18T04:00:00.000Z"}]
        def cards2(cs):
            cs["t1"] = T.held_card("MOMT", 17, 100, 90, "t1", [{"px": 100, "qty": 17}], lots_date="2026-09-01", price=125); cs["t1"]["plan"]["tp"] = 120
            cs["pl"] = T.mom_plan("AVGOP", 94.34, qty=12, hwf=False, tp=120)
        m = mock_shot(pw, "MomentumPlaceExit.html", ".row", 1100, "mom-cards", 2)
        b, page = live_page(pw, 1100, 900, cards2, trades)
        for t in ("MOMT", "AVGOP"): T.hw(page, t, t == "MOMT")
        js(page, "()=>{ bdChip='MMT'; bdSeg='plan'; bdRender(); }"); page.wait_for_timeout(400)
        l = os.path.join(OUT, "mom-cards-live.png"); page.screenshot(path=l); b.close()
        side(pw, m, l, os.path.join(OUT, "mom-cards-side.png"), 1100, 1100)
        # F · compounder editor risk select
        b, page = live_page(pw, 1440, 900); T.hw(page, "NEWC", True); T.open_editor(page, "ladder"); T.fill_ed(page, "NEWC", 100, 90)
        l = os.path.join(OUT, "editor-comp-live.png"); page.screenshot(path=l); print("wrote editor-comp-live.png"); b.close()


if __name__ == "__main__":
    main()
