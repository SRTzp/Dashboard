#!/usr/bin/env python3
"""HF5 screenshots → docs/screenshots/hf5-*.png (manage 1440 + 390 · price-sheet 390 · movestop-sheet 390 · queue-blocked 390)."""
import sys
from playwright.sync_api import sync_playwright
from re1d_common import js
import hf5_common as H


def setup(page):
    H.mk(page, "x1", "XAUUSD", "Short"); H.place(page, "x1"); H.fill(page, "x1")
    js(page, "()=>{ sat7dWrite('satIdeas','x1',{lastPx:{v:2621, at:new Date().toISOString()}}); sat7dIdea('x1').lastPx={v:2621, at:new Date().toISOString()}; }")
    H.move_stop(page, "x1", 2650)
    H.mk(page, "b1", "BTCUSD", "Long"); H.place(page, "b1"); H.fill(page, "b1")   # second holding, no price
    js(page, "()=>{ re1Cache={}; re2GrpAll={enter:true,check:true,manage:true}; todayRefresh(true); }"); page.wait_for_timeout(400)


def manage_shot(page, name):
    js(page, "()=>{ const c=document.querySelector('[data-re2-col=\"manage\"]'); if(c) c.scrollIntoView({block:'center'}); }"); page.wait_for_timeout(300)
    H.shot(page, name)


with sync_playwright() as pw:
    for w, h in ((1440, 900), (390, 844)):
        b, page, ce, pe = H.start(pw, w, h); setup(page)
        manage_shot(page, "manage-%d" % w)
        if w == 390:
            js(page, "()=>document.querySelector('[data-hf5-row=\"BTC\"] [data-hf5-btn=\"price\"]').click()"); page.wait_for_timeout(300); H.shot(page, "price-sheet"); js(page, "()=>coreSheetClose()")
            js(page, "()=>document.querySelector('[data-hf5-row=\"XAU\"] [data-hf5-btn=\"stop\"]').click()"); page.wait_for_timeout(300)
            js(page, "()=>{ const el=document.getElementById('csStop'); el.value='2645'; re1SatStopIn(); }"); page.wait_for_timeout(200); H.shot(page, "movestop-sheet"); js(page, "()=>coreSheetClose()")
        b.close()
    b, page, ce, pe = H.start(pw, 390, 844)
    H.mk(page, "x1", "XAUUSD", "Short"); H.place(page, "x1"); H.fill(page, "x1")
    H.mk(page, "b1", "BTCUSD", "Long")
    js(page, "()=>pb2PlaceOpen('b1')"); page.wait_for_timeout(400); H.shot(page, "queue-blocked"); b.close()
print("shots done")
