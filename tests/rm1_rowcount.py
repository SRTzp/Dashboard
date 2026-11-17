#!/usr/bin/env python3
"""RM1 — screen length at 390 for Flow · Today · Plan board (same fixture, run once on the base tree and once on the branch).
Prints JSON: rows = visible row-like elements (lines, board rows, strip cells, summary rows) · height = scrollHeight in px."""
import json, sys
from playwright.sync_api import sync_playwright
import net_stub
import re1d_common as K
from re1d_common import js

SEL = "tr,li,.line,[data-re2-row],.bd-rs,.bd-rc,.ffActRg,.ln3-fr,.bd-card,.sumRow,.td3-rg,[data-bd-row]"
def count(page, tab):
    js(page, "(t)=>{ switchTab(t); try{ if(t==='plan'){ bdSetSeg('plan'); bdRender(); } if(t==='today') todayRefresh(true); }catch(e){} }", tab); page.wait_for_timeout(500)
    return js(page, "(s)=>{ const v=e=>{ const r=e.getBoundingClientRect(); const cs=getComputedStyle(e); return r.width>0 && r.height>0 && cs.visibility!=='hidden' && cs.display!=='none' && !e.closest('[hidden],details:not([open]) > :not(summary)'); }; return {rows:[...document.querySelectorAll(s)].filter(v).length, height:document.documentElement.scrollHeight}; }", SEL)
with sync_playwright() as pw:
    b, page, ce, pe = K.launch(pw, 390, 844)
    out = {t: count(page, t) for t in ('flow', 'today', 'plan')}
    b.close()
print(json.dumps(out))
