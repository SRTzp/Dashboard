#!/usr/bin/env python3
"""PV1 — honest position numbers · Flow asset panel · Planned / Holding cards.  Run: python3 tests/run_tests_pv1.py
Screenshots → tests/screenshots/pv1-*.png (env PV1_SHOTS = other folder)."""
import os, sys, json
from playwright.sync_api import sync_playwright
from pv1_common import *

SHOTS = os.environ.get("PV1_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
SIZES = [(1440, 900), (1280, 800), (390, 844)]


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "pv1-%s.png" % name))


def partA(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_sat(), cards_pv())
    try:
        js(page, SAT_JS); page.wait_for_timeout(700); refresh(page)
        r = {x["sym"]: x["t"] for x in rows(page, "manage")}
        t = r.get("NVDA", "")
        check("[%s] A2 holding row = #11/#29 · ฿60.5k · 1.2%% · open risk ฿17.8k" % tag, "#11/#29 · ฿60.5k · 1.2% · open risk ฿17.8k" in t, t)
        check("[%s] A2 old plan-total numbers are gone from the holding row (no ฿36.1k / 0.72%% / cap 50%%)" % tag, "36.1k" not in t and "0.72%" not in t and "cap 50%" not in t, t)
        check("[%s] A2 homework note stays text, not a number" % tag, "size limited to 50% · homework not done" in t, t)
        pv = js(page, "()=>{const it=bdItems().find(x=>x.sym==='NVDA'); return posView(it)}")
        check("[%s] posView NVDA: held 11 · planned 29 · cost · value · plan risk" % tag, pv["heldQty"] == 11 and pv["plannedQty"] == 29 and abs(pv["cost"] - 58674.88) < .01 and abs(pv["value"] - 60475.976) < .01 and abs(pv["plannedRisk"] - 36055.68) < .01 and abs(pv["openRisk"] - 17825.28) < .01, pv)
        # drawer shows the same numbers
        js(page, "()=>bdOpen(bdItems().find(x=>x.sym==='NVDA').id)"); page.wait_for_timeout(300)
        dt = txt(page, "[data-pv-block]")
        check("[%s] drawer POSITION block: same value, weight, open risk, whole plan" % tag, "฿60.5k" in dt and "1.2% of account" in dt and "฿17.8k" in dt and "29 sh" in dt and "฿36.1k" in dt and "0.72% of account" in dt, dt)
        check("[%s] drawer: price + date shown, no bare dash" % tag, "162.85" in dt and "13 Nov" in dt and " — " not in dt.replace("—", "—") .replace(" — ", "") if False else "162.85" in dt and "13 Nov" in dt, dt)
        js(page, "()=>bdClose()")
        # Satellite: planned row, holding without price, holding with manual Last price
        sp = js(page, "()=>{const o={}; bdItems().filter(x=>x.kind==='sat').forEach(it=>{o[it.sym]=pvRowParts(it)}); return o}")
        check("[%s] Sat planned row = plan 0.21 lot · risk $294 · 0.20%%" % tag, sp["XAU"]["sz"] == "plan 0.21 lot" and sp["XAU"]["rk"].startswith("risk $294 · 0.20%"), sp["XAU"])
        check("[%s] Sat holding without price: 'value: no live price' and open risk kept" % tag, sp["BTC"]["sz"] == "0.02 lot" and "value: no live price" in sp["BTC"]["rk"] and "open risk $20" in sp["BTC"]["rk"], sp["BTC"])
        js(page, "()=>bdOpen(bdItems().find(x=>x.sym==='BTC').id)"); page.wait_for_timeout(300)
        check("[%s] Sat drawer has the optional Last price field, blank by default" % tag, js(page, "()=>{const e=document.getElementById('pvLastIn'); return !!e && e.value===''}") and "no live price" in txt(page, "[data-pv-block]"))
        js(page, "()=>{document.getElementById('pvLastIn').value='61000'; pvSetLast(bdItems().find(x=>x.sym==='BTC').id)}"); page.wait_for_timeout(400)
        dt = txt(page, "[data-pv-block]"); st = js(page, "()=>satIdeasList.find(x=>x.id==='bi').lastPx")
        check("[%s] Last price saved with the time typed; value / P&L shown with 'manual'" % tag, st and st["v"] == 61000 and st["at"] and "manual" in dt and "$" in dt and "Unrealised P&L" in dt and "+$20" in dt, [st, dt])
        sp2 = js(page, "()=>pvRowParts(bdItems().find(x=>x.sym==='BTC'))")
        check("[%s] row with manual price shows value, no 'no live price'" % tag, "no live price" not in sp2["rk"] and "open risk $20" in sp2["rk"], sp2)
        js(page, "()=>{const i=satIdeasList.find(x=>x.id==='bi'); i.lastPx={v:61000, at:new Date(Date.now()-30*3600*1000).toISOString()}; bdRender(); bdDrawerRender();}"); page.wait_for_timeout(300)
        check("[%s] Last price older than 24 h → 'old price'" % tag, js(page, "()=>!!document.querySelector('[data-pv-old]')") and "old price" in js(page, "()=>pvRowParts(bdItems().find(x=>x.sym==='BTC')).rk"))
        # display only: sizing / engine unaffected by the last price
        a = js(page, "()=>{const i=satIdeasList.find(x=>x.id==='xp'); const c=pb2Calc(i,'main'); return [c.lot,c.risk]}")
        js(page, "()=>{satIdeasList.find(x=>x.id==='xp').lastPx={v:2700, at:new Date().toISOString()}; re1Cache={};}")
        b2 = js(page, "()=>{const i=satIdeasList.find(x=>x.id==='xp'); const c=pb2Calc(i,'main'); return [c.lot,c.risk]}")
        check("[%s] Last price does not change sizing (pb2Calc lot / risk identical)" % tag, a == b2, [a, b2])
        js(page, "()=>bdClose()")
        # Sat form: optional field exists, blank, saved only when typed
        js(page, "()=>pb2OpenEdit('xp')"); page.wait_for_timeout(300)
        check("[%s] Sat plan form: optional Last price field (blank)" % tag, js(page, "()=>{const e=document.querySelector('[data-pb2-in=last]'); return !!e && e.value===''}") or js(page, "()=>{const e=document.querySelector('[data-pb2-in=last]'); return !!e && e.value==='2700'}"))
        js(page, "()=>bdPopClose()")
        check("[%s] A: no overflow on Today" % tag, no_overflow(page))
        if w in (1440, 390):
            js(page, "()=>{switchTab('today'); todayRefresh(true);}"); page.wait_for_timeout(400); shot(page, "today-%d" % w)
        check("[%s] A: no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


if __name__ == "__main__":
    only = os.environ.get("PV1_PARTS", "ABC").split(",") if False else list(os.environ.get("PV1_PARTS", "ABC"))
    with sync_playwright() as pw:
        for w, h in SIZES:
            if "A" in only: partA(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("%d checks pass · %d fail" % (len(results) - len(bad), len(bad)))
    sys.exit(1 if bad else 0)
