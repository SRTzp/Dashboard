import sys
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, plan_card
import run_tests_lrf as LF
with sync_playwright() as pw:
    cs = dict(LF.L3.cards_board()); cs["mA"] = plan_card("AAA", 100, 92, px=100.5, ready=True)
    b, page, ce, pe = launch(pw, 1440, 900, c=cs)
    LF.today(page)
    js(page, "()=>{ window.prompt=(m,d)=>String(d); window.wl1PlaceGate=()=>true; }")
    print(js(page, """()=>{ const c=coreCardsList.find(x=>x.id==='mA'); const rm=re1CardModel(c,null,+c.plan.entry,+c.plan.stop); const m=rm.m; return {ps1:!!c.plan.ps1, planKeys:Object.keys(c.plan), m:{qty:m.qty, allowed:m.allowedQty, blocked:m.blocked, reasons:m.reasons, cap:m.cap, capped:m.capped, hw:m.homework, keys:Object.keys(m)}}; }"""))
    print(js(page, "()=>document.querySelector('[data-bd-card=\"mA\"]').innerText.replace(/\\s+/g,' ')"))
    js(page, "()=>efCorePlaceOpen('mA')"); page.wait_for_timeout(400)
    print(js(page, "()=>document.querySelector('[data-ef-core-place]').innerText.replace(/\\s+/g,' ')")[:500])
    js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(700)
    print('AFTER', js(page, "()=>document.querySelector('[data-bd-card=\"mA\"]')?.innerText.replace(/\\s+/g,' ')"))
    print(js(page, "()=>{const c=coreCardsList.find(x=>x.id==='mA'); return {st:c.status, tid:c.trade_id, rows:c.plan.ps1&&c.plan.ps1.rows.map(r=>r.qty), ps1:JSON.stringify(c.plan.ps1).slice(0,400)}}"))
    js(page, "()=>coreBuy1Open('mA')"); page.wait_for_timeout(400)
    print(js(page, "()=>{const e=document.getElementById('cbQty'); return e&&[e.value, e.parentElement.innerText]}"))
    b.close()
