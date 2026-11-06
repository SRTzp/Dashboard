#!/usr/bin/env python3
"""PS1 — screenshots 390 / 1440: plan form (single · 2×2 rows) · Sat plan verify states · Port risk panel · Today line. ภาพ → tests/screenshots/ps1-*.png"""
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase120 as T
import run_tests_phase77 as P77
js = C.js
settle = T.settle
P13 = T.P13


def main():
    tr = [P13.T("p1", "core", "open", sym="BE", entry=100, sl=100, qty=100, cur="USD", date="2026-10-20"),
          P13.T("p2", "core", "open", sym="MSFT", entry=400, sl=370, qty=40, cur="USD", date="2026-10-20"),
          P13.T("p3", "core", "open", sym="NOSL", entry=50, sl=0, qty=100, cur="USD", date="2026-10-20"),
          P13.T("p4", "core", "open", sym="NOPX", entry=50, sl=45, qty=100, cur="USD", date="2026-10-20")]
    cards = {"c1": T.open_card("BE", "p1", px=120, plan={"entry": 100, "stop": 100}, stop=100), "c2": T.open_card("MSFT", "p2", px=455, track="ladder", plan={"entry": 400, "stop": 370}, stop=370),
             "c3": T.open_card("NOSL", "p3", px=60, stop=0), "c4": T.open_card("NOPX", "p4", px=None, stop=45)}
    with sync_playwright() as pw:
        for w, h, tag in ((1440, 1000, "1440"), (390, 844, "390")):
            b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
            try:
                T.ps_on(page)
                # plan form — single
                T.form(page, "AAA"); T.fill(page, 100, 90)
                C.shot(page, f"ps1-form-single-{tag}.png", sel=".core-sheet")
                # 2 entries + 2 SLs
                js(page, "()=>{ ps1RowAdd('e'); ps1RowAdd('s'); }"); settle(page, 200)
                js(page, "()=>{ document.getElementById('cnEn1').value='95'; ps1In('e',1,'95'); document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); }"); settle(page, 200)
                js(page, "()=>{ ps1In('er',0,'0.25'); document.getElementById('cnEr0').value='0.25'; ps1In('er',1,'0.15'); document.getElementById('cnEr1').value='0.15'; }"); settle(page, 300)
                C.shot(page, f"ps1-form-2x2-{tag}.png", sel=".core-sheet")
                js(page, "()=>coreSheetClose()")
                # panel
                js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 500)
                C.shot(page, f"ps1-panel-{tag}.png", sel="#ps1Panel")
                # today line
                js(page, "()=>switchTab('today')"); settle(page, 600)
                C.shot(page, f"ps1-today-{tag}.png", full=True)
                print(tag, "form/panel/today errors:", ce[:2], pe[:2])
            finally:
                b.close()
            # Sat plan — verify states
            b, page, ce, pe = P77.launch(pw, w, h)
            try:
                T.ps_on(page, {"def": {"winner": 0.4, "ladder": 1.0, "satMain": 0.1, "satTac": 0.15}})
                iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
                js(page, "([i])=>satV2SetDir(i,'Long')", [iid]); settle(page, 300)
                for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
                    js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)]); settle(page, 120)
                for name, ema, st in (("blocked", False, False), ("unclear", False, True), ("clear", True, True)):
                    js(page, "([i,e,s])=>{ pfVerifySet(i,'structure_ok',s); pfVerifySet(i,'ema50_ok',e); }", [iid, ema, st]); settle(page, 500)
                    C.shot(page, f"ps1-sat-{name}-{tag}.png", sel=f'[data-sat-plan="{iid}"], [data-v2-card="{iid}"], #satV3Panel')
                print(tag, "sat errors:", ce[:2], pe[:2])
            finally:
                b.close()


if __name__ == "__main__":
    main()
