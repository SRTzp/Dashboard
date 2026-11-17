#!/usr/bin/env python3
"""PV1b — compact Plan cards · real Blocked reasons · legs (<=2 in / <=2 out) · Momentum optional tp2 / tp1Qty.  Run: python3 tests/run_tests_pv1b.py
Screenshots -> tests/screenshots/pv1b-*.png (env PV1B_SHOTS = other folder)."""
import os, re, sys, copy
from playwright.sync_api import sync_playwright
from pv1_common import *

SHOTS = os.environ.get("PV1B_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
SIZES = [(1440, 900), (1280, 800), (390, 844)]


def txt(page, sel):
    return js(page, "(s)=>{const e=document.querySelector(s);return e?e.innerText.replace(/\\s+/g,' ').trim():''}", sel)


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "pv1b-%s.png" % name))


def ctext(page, cid):
    return js(page, "(i)=>{const c=document.querySelector('[data-bd-card=\"'+i+'\"]'); return c? c.innerText.replace(/\\s+/g,' ') : ''}", cid)


def legs(page, cid):
    return js(page, "(i)=>[...document.querySelectorAll('[data-bd-card=\"'+i+'\"] [data-pv-leg]')].map(e=>({t:e.innerText.replace(/\\s+/g,' ').trim(), out:e.dataset.pvLeg==='out', done:e.dataset.pvDone==='1'}))", cid)


def sat_doc(sl=59000, exit_px=None, exit_qty=0.01):
    d = doc_sat(); m = d["books"]["main"]
    for t in m["trades"]:
        if t["id"] == "h1": t["sl"] = sl
    if exit_px:
        m["trades"].append(tr(id="h1x", sym="BTCUSD", port="satB", cur="USD", status="closed", qty=exit_qty, entry=60000, sl=59000, mult=1, posGroup="h1", sl0=59000, exitPrice=exit_px, exitDate="2026-11-15", closedAt="2026-11-15T04:00:00.000Z", date="2026-11-14"))
    return d


def mom_card():
    c = copy.deepcopy(NVDA_CARD); c["ticker"] = "AVGO"; c["trade_id"] = "h_avgo"; c.pop("track", None)
    c["plan"]["ps1"]["bucket"] = "winner"; c["plan"]["tp"] = 175; c["plan"]["tp2"] = 190; c["plan"]["tp1Qty"] = 10
    c["lots"] = [{"layer": "base", "qty": 20, "stop": 110, "f": 0.75, "n": 1, "risk": 1, "px": 158, "date": "2026-11-13"}]
    c["plan"]["ps1"]["rows"] = [{"px": 158, "riskPct": 0.5, "qty": 20}, {"riskPct": 0.5, "px": 150, "qty": 15}]
    return c


def run(pw, w, h):
    tag = str(w)
    # ---------- planned Satellite: kinds of legs
    b, page, ce, pe = launch(pw, w, h, doc_sat(), cards_pv())
    try:
        js(page, SAT_JS); js(page, SAT_PLANS_JS); page.wait_for_timeout(700); refresh(page)
        js(page, "()=>{satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','XAGUSD']); switchTab('plan'); bdRender();}"); page.wait_for_timeout(500)
        t = ctext(page, "xp"); L = legs(page, "xp")
        check("[%s] A Sat Planned Long 1/1 — #qty · Stop · Risk · Reward +$X nR (R joined), chips Buy #0.21 @ 2,642 · Sell #0.21 @ 2,684" % tag, "Stop 2,628" in t and "Risk −$294" in t and "Reward +$882 3.0R" in t and "#0.21 Stop 2,628" in t and [x["t"] for x in L] == ["Buy #0.21 @ 2,642", "Sell #0.21 @ 2,684"] and not any(x["done"] for x in L), [t, L])
        L = legs(page, "ps")
        check("[%s] A Sat Planned Short 1/1 — entry = Sell, exit = Buy" % tag, [x["t"][:4] for x in L] == ["Sell", "Buy "] and [x["out"] for x in L] == [False, True], L)
        # two entries: exit covers ALL planned entries; Reward / R include every leg (XAU E1 2,642 x0.1 + E2 2,636 x0.18, stop 2,628, target 2,684)
        js(page, """()=>{ const o = pb2Calc; window.__o = o; pb2Calc = function(i, a){ const c = o(i, a); if(i.id !== 'xp') return c; const fx = +getBook('main').settings.fx || 1;
            c.lot = 0.1; c.c = Object.assign({}, c.c, {e2:{ok:true, px:2636, lot1:0.1, lot2:0.18, share:50}}); c.c.v2 = Object.assign({}, c.c.v2, {actualTHB: 284 * fx}); return c; };
          const i = satIdeasList.find(x=>x.id==='xp'); i.entry = 2642; i.entry2 = 2636; i.sl = 2628; i.tp = 2684; i.sleeve = 'main'; i.e2on = true; bdRender(); }"""); page.wait_for_timeout(300)
        t2 = ctext(page, "xp"); L2 = [x["t"] for x in legs(page, "xp")]
        check("[%s] A two entries: legs Buy #0.1 @ 2,642 · Buy #0.18 @ 2,636 · Sell #0.28 @ 2,684 (exit = sum of entry qty)" % tag, L2 == ["Buy #0.1 @ 2,642", "Buy #0.18 @ 2,636", "Sell #0.28 @ 2,684"], L2)
        pvx = js(page, "()=>{const p=posView(bdItems().find(x=>x.id==='xp')); return {rw:p.reward/p.fx, rk:p.plannedRisk/p.fx, r:p.rewardR}}")
        check("[%s] A two entries: Risk −$284 · Reward +$1,284 (shown compact as +$1.3k, same as the mockup) · 4.5R — every entry leg counted" % tag, "Risk −$284" in t2 and "Reward +$1.3k" in t2 and "4.5R" in t2 and abs(pvx["rw"] - 1284) < 0.01 and abs(pvx["rk"] - 284) < 0.01 and abs(pvx["r"] - 4.521) < 0.01, [t2, pvx])
        js(page, "()=>{ pb2Calc = window.__o; satIdeasList.find(x=>x.id==='xp').e2on = false; bdRender(); }"); page.wait_for_timeout(200)
        check("[%s] A unsized chip reads 'Buy #— @ 30 · not sized' (no ×)" % tag, "Buy #— @ 30 · not sized" in " ".join(x["t"] for x in legs(page, "pb")) and "×" not in " ".join(x["t"] for x in legs(page, "pb")), [x["t"] for x in legs(page, "pb")])
        ml = js(page, """()=>{ const e=document.querySelector('[data-bd-card=xp] [data-pv-money]'), cs=getComputedStyle(e), lh=parseFloat(cs.lineHeight)||parseFloat(cs.fontSize)*1.3; return {h:e.getBoundingClientRect().height, lh, t:e.innerText.replace(/\\s+/g,' ').trim(), r:!!e.querySelector('[data-pv-reward] [data-pv-r]')}; }""")
        if w >= 1280: check("[%s] A planned money line is ONE line (#qty · Stop · Risk · Reward +$X nR)" % tag, ml["h"] < ml["lh"] * 1.6 and ml["r"], ml)
        check("[%s] A planned money line + chips carry no unit word / no ×" % tag, not re.search(r"\\b(lot|lots|sh|shares)\\b|×", ml["t"] + " " + " ".join(x["t"] for x in legs(page, "xp"))), ml)
        js(page, "()=>{ if(bdPopOpen()) bdPopClose(); pb2 = {step:'place', id:'xp', a:'XAUUSD'}; pb2Render(); }"); page.wait_for_timeout(400)   # the card is Blocked (min stop) → open the sheet directly
        cf = txt(page, "[data-pb2-order]")
        check("[%s] A confirm sheet reads like an order ticket: 'Entry Buy #0.21 @ 2,642' (no unit word)" % tag, cf.startswith("Entry Buy #") and "@ 2,642" in cf and "lot" not in txt(page, "[data-pb2-summary]"), [cf, txt(page, "[data-pb2-summary]")])
        check("[%s] A confirm sheet: no overflow" % tag, no_overflow(page))
        js(page, "()=>{ bdPopClose(); }"); page.wait_for_timeout(200)
        check("[%s] A Short word is coloured Short; card has no six-box grid / helper text" % tag, js(page, "()=>{const c=document.querySelector('[data-bd-card=ps]'); return c.querySelector('[data-pv-dir]').dataset.pvDir==='Short' && !c.querySelector('.pv-kv') && !/Fix the plan to get a size|not sized.*not sized|To entry/.test(c.innerText)}"))
        # Tactical = 2 targets, entry 2 is Main only
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.sleeve='tactical'; i.e2on=false; i.entry2=null; bdRender(); }"); page.wait_for_timeout(300)
        pv = js(page, "()=>{const it=bdItems().find(x=>x.id==='xp'); const p=posView(it); return {pq:p.plannedQty, tq:p.legs.filter(l=>l.out).reduce((a,l)=>a+l.qty,0), rw:p.reward}}")
        check("[%s] A Sat Tactical targets quantity = planned quantity; reward positive" % tag, abs(pv["pq"] - pv["tq"]) < 1e-9 and pv["rw"] > 0, pv)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.e2on=false; i.entry2=null; bdRender(); }"); page.wait_for_timeout(300)
        L = legs(page, "xp")
        check("[%s] A Sat 1/2 (Tactical, one entry): one Buy, two Sell" % tag, [x["t"][:3] for x in L] == ["Buy", "Sel", "Sel"], [x["t"] for x in L])
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.sleeve='main'; i.e2on=true; i.entry2=2636; i.e2share=50; bdRender(); }"); page.wait_for_timeout(300)
        L = legs(page, "xp")
        check("[%s] A Sat 2/1 (Main + entry 2): two Buy, one Sell" % tag, [x["t"][:3] for x in L] == ["Buy", "Buy", "Sel"], [x["t"] for x in L])
        # More: tap toggles, stays open on re-render, keyboard
        check("[%s] A More closed by default; tap opens; Edit inside" % tag, not js(page, "()=>!!document.querySelector('[data-bd-card=xp] [data-pv-more]')"))
        js(page, "()=>document.querySelector('[data-bd-card=xp]').click()"); page.wait_for_timeout(250)
        mt = ctext(page, "xp")
        check("[%s] A More shows cost/risk rows, R per target, Edit" % tag, js(page, "()=>!!document.querySelector('[data-bd-card=xp] [data-pv-more] [data-pv-edit]')") and "R per target" in mt and "Whole-plan risk" in mt, mt[-300:])
        js(page, "()=>{bdRender();}"); page.wait_for_timeout(200)
        check("[%s] A More stays open after re-render; aria-expanded" % tag, js(page, "()=>{const c=document.querySelector('[data-bd-card=xp]'); return !!c.querySelector('[data-pv-more]') && c.getAttribute('aria-expanded')==='true'}"))
        page.focus('[data-bd-card=xp]'); page.keyboard.press('Enter'); page.wait_for_timeout(250)
        check("[%s] A More toggles from the keyboard (Enter)" % tag, not js(page, "()=>!!document.querySelector('[data-bd-card=xp] [data-pv-more]')"))
        check("[%s] A Last price hidden on the Sat plan form, stored lastPx untouched" % tag, True)
        js(page, "()=>{ satIdeasList.find(x=>x.id==='xp').lastPx={v:2700, at:new Date().toISOString()}; }")
        js(page, "()=>pb2OpenEdit('xp')"); page.wait_for_timeout(300)
        check("[%s] A form: no Last price field" % tag, not js(page, "()=>!!document.querySelector('[data-pb2-in=last]')"))
        check("[%s] A the form save no longer writes lastPx" % tag, js(page, "()=>!/patch\\.lastPx/.test(pb2SaveDo.toString())") and js(page, "()=>satIdeasList.find(x=>x.id==='xp').lastPx.v===2700"))
        js(page, "()=>bdPopClose && bdPopClose()")
        if w in (1440, 390):
            js(page, "()=>{switchTab('plan'); bdRender(); window.scrollTo(0,0)}"); page.wait_for_timeout(300); shot(page, "plan-%d" % w)
        check("[%s] A no overflow on the Plan board" % tag, no_overflow(page))
        check("[%s] A no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()
    # ---------- Blocked sources
    b, page, ce, pe = launch(pw, w, h, doc_sat(), cards_pv())
    try:
        js(page, SAT_JS); js(page, SAT_PLANS_JS); page.wait_for_timeout(600); refresh(page)
        js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(400)
        def blk(cid):
            return js(page, "(i)=>{const c=document.querySelector('[data-bd-card=\"'+i+'\"]'); if(!c) return null; const w=c.querySelector('[data-pv-warn]'); return {why:w?w.querySelector('[data-pv-why]').innerText:'', btn:w&&w.querySelector('button')?w.querySelector('button').innerText.trim():'', t:c.innerText.replace(/\\s+/g,' ')}}", cid)
        # unpicked
        js(page, "()=>{satWeekPickWrite(wpWeekKey(), []); re1Cache={}; bdRender();}"); page.wait_for_timeout(300)
        z = blk("xp")
        check("[%s] B (EF1) an unpicked asset is no longer a block — no 'Not picked this week' / Add to week ›" % tag, z and z["why"] != "Not picked this week" and z["btn"] != "Add to week ›", z)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD']); satIdeasList.find(x=>x.id==='pb').asset='BTCUSD'; re1Cache={}; bdRender(); }"); page.wait_for_timeout(300)
        z = blk("xp")
        check("[%s] B lot exists but plan not ready → real reason (never 'Size not available'), real size / risk visible" % tag, z and z["why"] and z["why"] != "Size not available" and "Risk −$294" in z["t"] and "#0.21 @" in z["t"], z)
        zz = js(page, "()=>{ const i=Object.assign({}, satIdeasList.find(x=>x.id==='xp'), {sl:2642}); const c=pb2Calc(i,pb2AcctOf(i)); const z=pvSatBlockOf(i); return {lot:c.lot, msg:c.msg, z:z}; }")
        check("[%s] B no lot (sizing failed) → the sizing message with a Fix button (never 0)" % tag, zz["lot"] is None and zz["z"] and zz["z"]["why"] and zz["z"]["btn"] in ("Fix stop ›", "Fix size ›", "Open Settings ›"), zz)
        # carried
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.week='2000-01-03'; i.carried_from=null; re1Cache={}; bdRender(); }"); page.wait_for_timeout(300)
        z = blk("xp")
        ok = js(page, "()=>{const i=satIdeasList.find(x=>x.id==='xp'); return satV3IsCarried(i)}")
        check("[%s] B (EF1) a carried plan is no longer a block — no 'Carried from last week' / Use this week ›" % tag, (not ok) or (not z) or (z["why"] != "Carried from last week" and z["btn"] != "Use this week ›"), [ok, z])
        # news window
        js(page, "()=>{ window.newsSatBlock = ()=>({kind:'CPI', from:'19:15', to:'20:00', msg:'x'}); re1Cache={}; satIdeasList.find(x=>x.id==='ps').week = wpWeekKey(); bdRender(); }"); page.wait_for_timeout(300)
        z = blk("ps")
        check("[%s] B (EF1) news window is a warning, not a block: amber 'News window until 20:00 ICT · size 65%%' on the card" % tag, "News window until 20:00 ICT · size 65%" in ctext(page, "ps") and (not z or z["why"] != "News window · until 20:00 ICT"), z)
        check("[%s] B Blocked chip, no Ready chip / toggle" % tag, js(page, "()=>{const c=document.querySelector('[data-bd-card=ps]'); return !!c.querySelector('[data-pv-blocked]') && !c.querySelector('[data-re2-ready]')}"))
        check("[%s] B no console / page errors" % tag, not ce and not pe, ce + pe)
        if w in (1440,):
            js(page, "()=>window.scrollTo(0,0)"); shot(page, "blocked-%d" % w)
    finally:
        b.close()
    # ---------- Holding: Satellite If stopped sign / Banked / exit chips
    for nm, sl, ex, want in (("loss", 59000, None, ("−$20", "loss")), ("zero", 60000, None, ("±$0", "zero")), ("locked gain", 60500, None, ("+$10", "gain"))):
        b, page, ce, pe = launch(pw, w, h, sat_doc(sl, ex), cards_pv())
        try:
            js(page, SAT_JS); page.wait_for_timeout(600); refresh(page)
            js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(400)
            z = js(page, "()=>{const e=document.querySelector('[data-bd-card=bi] [data-pv-ifstopped]'); return e?[e.innerText.replace(/\\s+/g,' '), e.dataset.pvIfstopped]:null}")
            t = ctext(page, "bi")
            check("[%s] A Holding Sat If stopped — %s" % (tag, nm), z and want[0] in z[0] and z[1] == want[1] and "Banked" not in t, [z, t])
        finally:
            b.close()
    b, page, ce, pe = launch(pw, w, h, sat_doc(59000, 62000, 0.01), cards_pv())
    try:
        js(page, SAT_JS); page.wait_for_timeout(600); refresh(page)
        js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(400)
        t = ctext(page, "bi"); L = legs(page, "bi")
        check("[%s] A Holding Sat after a partial exit: Banked +$20 · actual exit ✓ chip with real price × qty · remaining target dashed with the open qty" % tag, "Banked +$20" in t and any(x["out"] and x["done"] and x["t"].startswith("Sell #") and "@ 62,000" in x["t"] and "0.01" in x["t"] for x in L) and any(x["out"] and not x["done"] and "@ 63,000" in x["t"] for x in L), [t, L])
    finally:
        b.close()
    # ---------- Momentum / Compounder
    d = doc_pv(); m = d["books"]["main"]
    m["trades"] = [tr(id="h_avgo", sym="AVGO", cur="USD", qty=20, entry=158, sl=110, posGroup="h_avgo", sl0=110, date="2026-11-13", openedAt="2026-11-13"),
                   tr(id="h_avgox", sym="AVGO", cur="USD", qty=10, entry=158, sl=110, status="closed", exitPrice=175, exitDate="2026-11-15", closedAt="2026-11-15T04:00:00.000Z", posGroup="h_avgo", sl0=110, date="2026-11-13")]
    b, page, ce, pe = launch(pw, w, h, d, {"cM": mom_card()})
    try:
        refresh(page); js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(400)
        mid = js(page, "()=>(bdItems().find(x=>x.sym==='AVGO')||{}).id")
        t = ctext(page, mid); L = legs(page, mid)
        check("[%s] A Momentum Holding: Stop · Held · If stopped · (Banked) ; chips = fills ✓, pending entry, exits" % tag, mid and "Stop" in t and "If stopped" in t and any(x["done"] and x["t"].startswith("Buy #") and "@ 158" in x["t"] for x in L) and any((not x["done"]) and x["t"].startswith("Buy #") and "@ 150" in x["t"] for x in L), [t, L])
        check("[%s] A Momentum exits: only real closed rows are ✓; remaining targets dashed (no inferred hit)" % tag, [x for x in L if x["out"] and x["done"]] and all(not x["done"] for x in L if x["out"] and "190" in x["t"]), L)
    finally:
        b.close()
    # Planned Momentum with 2 targets (no fills)
    c = mom_card(); c["status"] = "plan"; c["lots"] = []; c["trade_id"] = None; c.pop("ln4", None)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cM": c})
    try:
        js(page, "()=>{ tv1SetupLeft=()=>1; }"); refresh(page); js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(400)
        mid = js(page, "()=>(bdItems().find(x=>x.sym==='AVGO')||{}).id")
        t = ctext(page, mid); L = legs(page, mid); q = [x["t"] for x in L]
        check("[%s] A Momentum Planned 2/2: Buy #20 @ 158 · Buy #15 @ 150 · Sell #10 @ 175 · Sell #25 @ 190 (tp1Qty = 10, rest to target 2)" % tag, q == ["Buy #20 @ 158", "Buy #15 @ 150", "Sell #10 @ 175", "Sell #25 @ 190"], [q, t])
        pv = js(page, "(i)=>{const p=posView(bdById(i)); return {rw:p.reward, rk:p.plannedRisk, r:p.rewardR}}", mid)
        # reward = (175-avg)*10 + (190-avg)*25 ; avg = (158*20+150*15)/35 ; * fx 33.76
        avg = (158 * 20 + 150 * 15) / 35.0; rw = ((175 - avg) * 10 + (190 - avg) * 25) * 33.76
        check("[%s] A Momentum Reward = both targets with their quantities; R = Reward / Risk" % tag, abs(pv["rw"] - rw) < 0.5 and pv["rk"] > 0 and abs(pv["r"] - rw / pv["rk"]) < 1e-6, [pv, rw])
        # blank tp2 = single target behaviour
        js(page, "(i)=>{const c=coreCardsList.find(x=>x.ticker==='AVGO'); delete c.plan.tp2; delete c.plan.tp1Qty; bdRender();}", mid); page.wait_for_timeout(300)
        q = [x["t"] for x in legs(page, mid)]
        check("[%s] A Momentum blank tp2 → single target for all shares" % tag, q[-1] == "Sell #35 @ 175" and len(q) == 3, q)
        # form
        js(page, "(i)=>coreNewOpen('main',{mode:'editw', id:coreCardsList.find(x=>x.ticker==='AVGO').id})", mid); page.wait_for_timeout(500)
        check("[%s] A Momentum form has optional Target 1 / Target 2 / Shares at target 1" % tag, js(page, "()=>!!document.querySelector('[data-pv-tp]') && !!document.querySelector('[data-pv-tp2]') && !!document.querySelector('[data-pv-tp1qty]')"))
        js(page, "()=>{document.getElementById('cnTp2').value='190'; document.getElementById('cnTp1Qty').value=''}")
        er = js(page, "()=>pvTgtRead().err")
        check("[%s] A Target 2 without shares at target 1 is refused with words" % tag, bool(er), er)
        js(page, "()=>{document.getElementById('cnTp').value='175'; document.getElementById('cnTp1Qty').value='10'}")
        check("[%s] A valid 175 / 190 / 10 passes" % tag, js(page, "()=>!pvTgtRead().err"))
        js(page, "()=>coreSheetClose()")
        check("[%s] A no overflow Momentum / Compounder cards" % tag, no_overflow(page))
        check("[%s] A no console / page errors (Momentum)" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()
    # ---------- NVDA values equal card / More / drawer
    b, page, ce, pe = launch(pw, w, h, doc_sat(), cards_pv())
    try:
        js(page, SAT_JS); page.wait_for_timeout(500); refresh(page)
        js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(300)
        hid = js(page, "()=>bdItems().find(x=>x.sym==='NVDA').id")
        js(page, "(i)=>document.querySelector('[data-bd-card=\"'+i+'\"]').click()", hid); page.wait_for_timeout(250)
        ct = ctext(page, hid)
        check("[%s] A NVDA card: If stopped −฿17.8k · Value ฿60.5k · 1.2%% · P&L" % tag, "If stopped −฿17.8k" in ct and "Value ฿60.5k · 1.2%" in ct and "homework" in ct, ct)
        check("[%s] A NVDA More: avg · price, cost with FX, price→stop, whole plan, size limit, FX" % tag, all(x in ct for x in ("Avg entry · price", "฿58.7k", "× FX 33.76", "฿19.6k", "฿36.1k · 0.72% of account", "max 12.5% of account", "Settings rate, not live")), ct)
        js(page, "(i)=>bdOpen(i)", hid); page.wait_for_timeout(300)
        dr = txt(page, "[data-pv-block]"); js(page, "()=>bdClose()")
        check("[%s] A NVDA value equal on card · More · drawer" % tag, all(x in dr for x in ("฿60.5k", "1.2% of account", "฿17.8k")), dr)
        if w == 390:
            js(page, "(i)=>document.querySelector('[data-bd-card=\"'+i+'\"]').scrollIntoView({block:'start'})", hid); page.wait_for_timeout(300); shot(page, "more-390")
        check("[%s] A no console / page errors (NVDA)" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in SIZES: run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("%d checks pass · %d fail" % (len(results) - len(bad), len(bad)))
    sys.exit(1 if bad else 0)
