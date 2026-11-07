#!/usr/bin/env python3
"""PS1b screenshots 390 / 1440 -> tests/screenshots/ps1b-*.png"""
from playwright.sync_api import sync_playwright
import ln3fix_common as C, run_tests_phase77 as P77, run_tests_phase105 as P105, run_tests_phase107 as T, run_tests_phase111 as P111, run_tests_phase120 as B
import run_tests_phase121 as X
js = C.js; settle = T.settle

with sync_playwright() as pw:
    for w, h in ((390, 844), (1440, 1000)):
        # Today (collapsed / expanded / goals) with core data
        tr = [P111.P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
        b, page, ce, pe = C.launch2(pw, w, h, tr, {"cR": B.open_card("RED", "tR", px=100)}, pin_winner=True)
        B.ps_on(page)
        js(page, "()=>{ localStorage.removeItem('ps1TodayOpen'); ps1TodayOpen=null; switchTab('today'); render(); }"); settle(page, 600)
        C.shot(page, f"ps1b-today-collapsed-{w}.png")
        js(page, "()=>{ document.querySelector('[data-ps1-today]').open=true; document.querySelectorAll('details.td3-acct').forEach(x=>x.open=true); }"); settle(page, 300)
        C.shot(page, f"ps1b-today-expanded-{w}.png", full=True)
        b.close()
        # Settings loss + min stop, Sat strategy box + details
        b, page, ce, pe = P77.launch(pw, w, h)
        X.ps_set(page)
        js(page, "()=>{ openSettings(); }"); settle(page, 800)
        js(page, "()=>{ document.getElementById('ps1Sec').open=true; }"); settle(page, 400)
        import os
        js(page, "()=>{ document.querySelector('[data-ps1-loss]').scrollIntoView({block:'start'}); }"); settle(page, 400)
        page.screenshot(path=os.path.join(C.SHOTS, f"ps1b-settings-{w}.png"))
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); }")
        iid = X.sat_plan(page, "XAUUSD", 2000, 1985, 2040)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); const d=document.querySelector('[data-ln2-det]'); if(d) d.open=true; }"); settle(page, 600)
        C.shot(page, f"ps1b-sat-strategy-{w}.png", full=True)
        b.close()
        # RRG cards
        b, page, ce, pe = T.launch(pw, w, h)
        R = P105.R
        rows = [R("XLK", "Technology", "imp", dm=0.9, ratio=99.0, mom=103.0, days=2, off=-1.2), R("XLU", "Utilities", "lead", dm=-0.7, ratio=103.2, mom=102.1, days=2, off=-1.6),
                R("SMH", "Semiconductors", "lead", dm=0.3), R("XLE", "Energy", "lead", dm=1.4), R("XLV", "Health", "lag", dm=-1.2)]
        P105.seed_rrg(page, d=rows, wk=P105.rows_w()); P105.go_flow(page)
        C.shot(page, f"ps1b-rrg-{w}.png", sel="#ffThemes")
        b.close()
print("shots done")
import run_tests_phase122 as R122, run_tests_phase105 as P105b
with sync_playwright() as pw:
    for w, h in ((390, 844), (1440, 1000)):
        # §7 plan form: single, then 2 entries / 2 SLs; min-stop error
        b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
        B.ps_on(page); B.form(page, "NVDA"); B.fill(page, 100, 90)
        C.shot(page, f"ps1b-form-single-{w}.png")
        js(page, "()=>{ ps1RowAdd('e'); ps1RowAdd('s'); }"); settle(page, 200)
        js(page, "()=>{ document.getElementById('cnEn1').value='110'; ps1In('e',1,'110'); document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); document.getElementById('cnEr0').value='0.2'; ps1In('er',0,'0.2'); document.getElementById('cnEr1').value='0.2'; ps1In('er',1,'0.2'); document.querySelector('#cnDet').open=true; }"); settle(page, 300)
        C.shot(page, f"ps1b-form-multi-{w}.png")
        js(page, "()=>{ ps1RowDel('e',1); ps1RowDel('s',1); const B=getBook('main'); delete B.settings.psRisk.minStopStock; saveBook('main'); }"); settle(page, 200); B.fill(page, 100, 97)
        C.shot(page, f"ps1b-form-mintoo-{w}.png")
        b.close()
        # §8 fast-track: Today pin + plan card badge
        tr = [P111.P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
        b, page, ce, pe = C.launch2(pw, w, h, tr, {"cR": B.open_card("RED", "tR", px=100)}, pin_winner=True)
        B.ps_on(page); js(page, "()=>{ ftToday = ()=>'2026-11-10'; }")
        B.form(page, "AVGO"); B.fill(page, 100, 90); js(page, "()=>coreNewSave()"); settle(page, 800)
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 500)
        C.shot(page, f"ps1b-fasttrack-card-{w}.png")
        js(page, "()=>{ ftToday = ()=>'2026-11-15'; switchTab('today'); todayRefresh(true); }"); settle(page, 600)
        C.shot(page, f"ps1b-fasttrack-today-{w}.png")
        b.close()
        # §10/§11 Fresh filter + Ask why toast
        b, page, ce, pe = T.launch(pw, w, h)
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        rows = [R122.Rp("AAA", "lead", 2, 8, dm=0.1, off=-1.0), R122.Rp("BBB", "imp", 1, 3, dm=0.1), R122.Rp("CCC", "lag", 1, 9, dm=0.1), R122.Rp("DDD", "lead", 9, 9, dm=0.9), R122.Rp("EEE", "lead", 1, 6, dm=-0.8)]
        P105b.seed_rrg(page, d=rows, wk=[]); P105b.go_flow(page)
        C.shot(page, f"ps1b-rrg-fresh-all-{w}.png", sel="#ffThemes")
        js(page, "()=>document.querySelector('[data-rr-f=fresh]').click()"); settle(page, 400)
        js(page, "()=>{ navigator.clipboard.writeText = ()=>Promise.resolve(); document.querySelector('[data-sd-ask]').click(); }"); settle(page, 500)
        C.shot(page, f"ps1b-rrg-fresh-{w}.png")
        b.close()
        # §7f Sat 2nd entry
        import run_tests_phase125 as R125
        b, page, ce, pe = P77.launch(pw, w, h)
        X.ps_set(page, extra={"minStop": {"XAUUSD": 0.1}})
        iid = X.sat_plan(page, "XAUUSD", 2000, 1980, 2060)
        js(page, "([i])=>{ satE2Toggle(i,true); }", [iid]); settle(page, 300); js(page, "([i])=>satE2Edit(i,'entry2','1990')", [iid]); settle(page, 400)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); settle(page, 600)
        C.shot(page, f"ps1b-sat-2entry-{w}.png", full=True)
        b.close()
print("shots2 done")

