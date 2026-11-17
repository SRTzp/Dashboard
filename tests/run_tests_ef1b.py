#!/usr/bin/env python3
"""EF1b — Today Enter cap · no counter-trend confirm · level place sheet · Ready as text.  Run: python3 tests/run_tests_ef1b.py
Screenshots -> tests/screenshots/ef1b-*.png (env EF1B_SHOTS = other folder)."""
import os, re, sys, copy
from playwright.sync_api import sync_playwright
from pv1_common import *

SHOTS = os.environ.get("EF1B_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
SIZES = [(1440, 900), (1280, 800), (390, 844)]
XP_JS = "()=>{ sat7dWrite('satIdeas','xp',{id:'xp',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }"
READY = "()=>{ window.ps1MinStopMsg = ()=>''; re1Cache = {}; }"



def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "ef1b-%s.png" % name))


def has(page, sel):
    return js(page, "(s)=>!!document.querySelector(s)", sel)


def seed_n(page, n):
    js(page, """(n)=>{ for(let k=1;k<=n;k++) sat7dWrite('satIdeas','xp'+k,{id:'xp'+k,v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642+k,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }""", n)
    page.wait_for_timeout(600); refresh(page)
    js(page, "()=>{ window.ps1MinStopMsg = ()=>''; re1Cache = {}; satWeekPickWrite(wpWeekKey(), ['XAUUSD']); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)


def enter_rows(page):
    return js(page, "()=>document.querySelectorAll('[data-re2-col=enter] [data-re2-row]').length")


def run(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 5)
        n_ready = js(page, "()=>bdItems().filter(i=>i.status==='plan' && re2ReadyOf(i)).length")
        check("[%s] 1 fixture: 5 Ready plans" % tag, n_ready == 5, n_ready)
        check("[%s] 1 Today › Enter shows 3 Ready plans + '+2 ›'" % tag, enter_rows(page) == 3 and txt(page, "[data-re2-more]") == "+2 ›", [enter_rows(page), txt(page, "[data-re2-more]")])
        check("[%s] 1 header count = rows shown (3)" % tag, txt(page, "[data-re2-col=enter] [data-re2-n]") == "3")
        if w == 390: shot(page, "today-390-collapsed")
        if w == 1440: shot(page, "today-1440-collapsed")
        page.click("[data-re2-more]"); page.wait_for_timeout(300)
        check("[%s] 1 '+2 ›' expands in place: 5 rows, still on Today" % tag, enter_rows(page) == 5 and js(page, "()=>activeTab") == 'today', enter_rows(page))
        if w == 390: shot(page, "today-390-expanded")
        page.click("[data-re2-more]"); page.wait_for_timeout(300)
        check("[%s] 1 'Show less' collapses back to 3" % tag, enter_rows(page) == 3)
        js(page, "()=>{ bdItems().filter(i=>i.status==='plan').slice(0,2).forEach(i=>sat7dWrite('satIdeas', i.id, {status:'cancelled', archived:true})); refresh_=1; re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(400)
        check("[%s] 1 3 or fewer Ready plans: no '+N' button" % tag, not has(page, "[data-re2-more]") and enter_rows(page) <= 3, enter_rows(page))
        check("[%s] 1 no overflow / errors" % tag, no_overflow(page) and not ce and not pe, ce + pe)
    finally:
        b.close()

    # row count at 390 vs. before (EF1b can only shorten Today)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 5)
        after = js(page, "()=>({rows:document.querySelectorAll('[data-re2-row]').length,h:document.documentElement.scrollHeight})")
        js(page, "()=>{ re2EnterCap = r=>r; todayRefresh(true); }"); page.wait_for_timeout(300)
        before = js(page, "()=>({rows:document.querySelectorAll('[data-re2-row]').length,h:document.documentElement.scrollHeight})")
        print("INFO [%s] Today rows %s -> %s · page height %s -> %s" % (tag, before["rows"], after["rows"], before["h"], after["h"]))
        check("[%s] 1 Today row count not longer than before (%s <= %s)" % (tag, after["rows"], before["rows"]), after["rows"] <= before["rows"] and after["h"] <= before["h"])
    finally:
        b.close()

    # 2 counter trend: no extra confirm, amber tag stays
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 1)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp1'); i.structure_ok=false; i.mss=true; re1Cache={}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        js(page, "()=>pb2OpenEdit('xp1')"); page.wait_for_timeout(350)
        if has(page, "[data-pb2-save]"):
            page.click("[data-pb2-save]"); page.wait_for_timeout(500)
        check("[%s] 2 Save of a counter-trend plan: no 'Save as counter trend?' confirm" % tag, not has(page, "[data-ln4-cs-ok]") and not has(page, ".ln4-cs"))
        check("[%s] 2 plan saved (sheet closed)" % tag, not has(page, "[data-pb2-save]"))
        t = js(page, "()=>{const c=document.querySelector('[data-bd-card=xp1]'); return c? c.innerText.replace(/\\s+/g,' ') : ''}")
        check("[%s] 2 amber 'Counter trend' tag stays on the card" % tag, "Counter trend" in t, t)
        check("[%s] 2 ln4CounterAsk / pb2CounterAsk no longer reached by Save" % tag, js(page, "()=>{ let hit=0; const a=window.ln4CounterAsk; window.ln4CounterAsk=()=>{hit++}; try{ satV3SaveReadyAccounts('xp1'); }catch(e){} window.ln4CounterAsk=a; return hit===0; }"))
    finally:
        b.close()

    # 4 Ready = plain green text
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 1)
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        st = js(page, "()=>{const e=document.querySelector('[data-bd-card=xp1] [data-ef-ready]'); if(!e) return null; const s=getComputedStyle(e); return {t:e.textContent.trim(), bg:s.backgroundColor, bw:s.borderTopWidth, br:s.borderTopLeftRadius, col:s.color}}")
        check("[%s] 4 card 'Ready' is text, not a pill (no background / border / radius)" % tag, st and st["t"] == "Ready" and st["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and st["bw"] == "0px" and st["br"] == "0px", st)
        g = js(page, "()=>{const p=document.createElement('i'); p.style.color='var(--green)'; document.body.appendChild(p); const c=getComputedStyle(p).color; p.remove(); return c}")
        check("[%s] 4 'Ready' is green" % tag, st and st["col"] == g, [st, g])
        if w == 1440: shot(page, "card-ready-1440")
        if w == 390: shot(page, "card-ready-390")
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        c = js(page, "()=>{const e=document.querySelector('[data-re2-chip-st].rdy'); if(!e) return null; const s=getComputedStyle(e); return {bg:s.backgroundColor, col:s.color}}")
        check("[%s] 4 Today › Enter 'Ready' is plain green text too" % tag, c and c["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and c["col"] == g, c)
    finally:
        b.close()

    # 3 later entry level -> same confirm sheet
    c = copy.deepcopy(NVDA_CARD); c["ln4"] = {"placedLv": {"0": "2026-11-13T03:05:39.227Z"}}
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"h_card": c} if False else cards_pv())
    try:
        js(page, "()=>{ window.ps1MinStopMsg = ()=>''; re1Cache = {}; window.ftHwDone = ()=>true; window.wl1HwDone = ()=>true; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        cid = js(page, "()=>{ const it=bdItems().find(i=>i.kind==='core' && i.sym==='NVDA'); return it && it.id }")
        lv = js(page, "(id)=>{ const it=bdById(id); return it ? {nl:it.nl, k:it.k, placed:[...(it.placed||[])]} : null }", cid)
        js(page, "(id)=>bdPlaceLv(id,1)", cid); page.wait_for_timeout(400)
        sheet = has(page, "[data-ef-core-place]")
        placed_before = js(page, "(id)=>{const it=bdById(id); return [...(it.placed||[])]}", cid)
        check("[%s] 3 bdPlaceLv(#2) opens the confirm sheet (nothing recorded yet)" % tag, sheet and 1 not in placed_before, [lv, sheet, placed_before])
        sh = txt(page, "[data-ef-core-place]")
        check("[%s] 3 sheet says 'Place order #2' with the level price, same Confirm / Not yet buttons" % tag, "#2" in sh and "Confirm" in sh and "Not yet" in sh and has(page, "[data-pb2-yes]"), sh)
        check("[%s] 3 sheet: no overflow" % tag, no_overflow(page))
        if w == 390: shot(page, "level-sheet-390")
        if w == 1440: shot(page, "level-sheet-1440")
        page.click("[data-pb2-no]"); page.wait_for_timeout(300)
        check("[%s] 3 Not yet → nothing recorded" % tag, 1 not in js(page, "(id)=>[...(bdById(id).placed||[])]", cid))
        js(page, "(id)=>bdPlaceLv(id,1)", cid); page.wait_for_timeout(350)
        page.click("[data-pb2-yes]"); page.wait_for_timeout(500)
        check("[%s] 3 Confirm records level #2 once, sheet closed" % tag, 1 in js(page, "(id)=>[...(bdById(id).placed||[])]", cid) and not has(page, "[data-ef-core-place]"))
        check("[%s] 3 no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


with sync_playwright() as pw:
    for w, h in SIZES:
        run(pw, w, h)
fails = [r for r in results if not r[1]]
print("\n%d checks pass · %d fail" % (len(results) - len(fails), len(fails)))
sys.exit(1 if fails else 0)
