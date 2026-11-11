#!/usr/bin/env python3
"""PB1 — screenshots 390 / 1440: Plan board · drawer · Flow top · Port top · Today (tests/screenshots/pb1-*.png)"""
import os
from playwright.sync_api import sync_playwright
import run_tests_phase373 as X
import run_tests_phase120 as P120

js, settle = X.js, X.settle
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")


def shot(page, name, full=False):
    page.screenshot(path=os.path.join(OUT, "pb1-%s.png" % name), full_page=full)


with sync_playwright() as pw:
    for w, h in ((1440, 900), (390, 844)):
        b, page, ce, pe = X.launch(pw, w, h)
        X.seed(page, X.fixtures()); X.setup_ok(page, ["AMD", "TSLA", "AVGO", "ORCL", "NOPX"])
        try: P120.ps_on(page)
        except Exception: pass
        X.stub(page, "window.ps1Model = (A)=>({A:A||tdHome(), E:1000000, cfg:{total:5, buckets:{winner:{cap:1.5,label:'MMT'},ladder:{cap:3,label:'COMP'},sat:{cap:0.5,label:'SAT'}}}, P:{principalPct:1.2, buckets:{winner:{principalPct:1.3,cap:1.5},ladder:{principalPct:0.9,cap:3},sat:{principalPct:0.1,cap:0.5}}, ideas:[]}, pos:[]});")
        js(page, "()=>render()"); settle(page, 500)
        X.plan(page); settle(page, 500)
        shot(page, "plan-%d" % w, True)
        if w <= 560:
            for s in ("ord", "hold"):
                js(page, "(s)=>bdSetSeg(s)", s); settle(page, 300); shot(page, "plan-%s-%d" % (s, w))
            js(page, "()=>bdSetSeg('plan')")
        js(page, "()=>bdOpen('ccMH')"); settle(page, 500); shot(page, "drawer-%d" % w)
        js(page, "()=>bdClose()")
        js(page, "()=>{ switchTab('flow'); }"); settle(page, 900); shot(page, "flow-top-%d" % w)
        js(page, "()=>{ switchTab('mix'); }"); settle(page, 900); shot(page, "port-top-%d" % w)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 900); shot(page, "today-%d" % w)
        js(page, "()=>bdNewOpen()"); settle(page, 400); shot(page, "popup-%d" % w)
        b.close()
print("shots done")
