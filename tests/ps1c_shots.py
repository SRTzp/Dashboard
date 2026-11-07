#!/usr/bin/env python3
"""PS1c screenshots 390 / 1440 -> tests/screenshots/ps1c-*.png"""
from playwright.sync_api import sync_playwright
import ln3fix_common as C, run_tests_phase107 as T, run_tests_phase120 as P, run_tests_phase121 as X
js = C.js; settle = T.settle

with sync_playwright() as pw:
    for w, h in ((390, 844), (1440, 1000)):
        # Core plan form: single row, then 2 columns after ＋ (with regime pill), over-cap message
        b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
        P.ps_on(page); P.form(page, "NVDA"); P.fill(page, 100, 95)
        C.shot(page, f"ps1c-form-single-{w}.png")
        js(page, "()=>{ const o=coreCtxTrack; window.coreCtxTrack=(cx,t)=>{ const r=o(cx,t); r.F=Object.assign({}, r.F, {f:0.75}); return r; }; ps1RowAdd('e'); ps1RowAdd('s'); }"); settle(page, 200)
        js(page, "()=>{ document.getElementById('cnEn1').value='98'; ps1In('e',1,'98'); document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); }"); settle(page, 250)
        C.shot(page, f"ps1c-form-multi-{w}.png")
        js(page, "()=>{ coreFormPort('ladder'); }"); settle(page, 250)
        C.shot(page, f"ps1c-form-compounder-{w}.png")
        b.close()
        # Plan page top bar (Core | Sat) + Core header switch
        b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
        P.ps_on(page)
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 600)
        C.shot(page, f"ps1c-plan-core-{w}.png")
        js(page, "()=>{ setPlanScope('future'); render(); }"); settle(page, 600)
        C.shot(page, f"ps1c-plan-sat-{w}.png")
        b.close()
        # Sat form: single + Entry 2
        b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
        X.ps_set(page); X.sat_plan(page, "XAUUSD", 2000, 1985, 2040)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); settle(page, 600)
        js(page, "()=>document.querySelector('[data-ln1-prices]').scrollIntoView({block:'center'})"); settle(page, 300); C.shot(page, f"ps1c-sat-form-{w}.png")
        js(page, "()=>document.querySelector('[data-sat-e2add]').click()"); settle(page, 500)
        js(page, "()=>document.querySelector('[data-ln1-prices]').scrollIntoView({block:'center'})"); settle(page, 300); C.shot(page, f"ps1c-sat-form-e2-{w}.png")
        b.close()
        # Today: homework row (3 items, one overdue) + 5 items expanded + Plans badges
        for n, syms in (("3", ["AVGO", "GLBE", "NVDA"]), ("5", ["AVGO", "GLBE", "NVDA", "MSFT", "AMZN"])):
            cards = {f"hw{i}": P.card(ticker=s_, plan={"entry": 100, "stop": 90, "ft": {"at": "2026-11-07", "due": "2026-11-08" if i == 2 else "2026-11-13"}}) for i, s_ in enumerate(syms)}
            b, page, ce, pe = C.launch2(pw, w, h, [], cards, pin_winner=True)
            P.ps_on(page); js(page, "()=>{ ftToday = ()=>'2026-11-10'; switchTab('today'); render(); }"); settle(page, 700)
            C.shot(page, f"ps1c-today-hw{n}-{w}.png")
            if n == "5":
                js(page, "()=>document.querySelector('[data-ft-more]').click()"); settle(page, 200)
                C.shot(page, f"ps1c-today-hw5-open-{w}.png")
            b.close()
print("shots done")
