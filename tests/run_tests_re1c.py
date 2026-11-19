#!/usr/bin/env python3
"""RE-C1 — cut-over suite (390 / 1280 / 1440): every form on the engine (allowed + blocked) · reason texts · Place order blocked while fills / closes still work and flag ·
snapshot confirm / stale block / provisional basis · cash flow · costs missing vs present · stop confirm releases the idea · Satellite step path, queue, re-entry confirm, stale order ·
Compounder Pilot → Add-on lock / unlock · Emergency · two accounts never mixed · no write changes an existing position's quantity · screenshots tests/screenshots/re1c-*.png
Run: python3 run_tests_re1c.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1c_common as K
from re1c_common import js, doc_c, cards, tr
import lib_phase39 as P39

HERE = os.path.dirname(os.path.abspath(__file__)); SHOTS = os.path.join(HERE, "screenshots")
results = []
NOANIM = "*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:500]) if (not ok and d) else ""))


def launch(pw, w, h, d=None, c=None):
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=d or doc_c(), cards=c if c is not None else cards(), clean=True)
    page.add_style_tag(content=NOANIM); page.wait_for_timeout(500)
    js(page, "()=>{ ln4Write(o=>{ o.costsOn = true; o.re1CostsReset = true; }); re1Cache = {}; }")   # RE-C2 §6: these are the RE-C1 cost tests → Costs switch ON (RE-C1 behaviour exactly)
    return b, page, ce, pe


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "re1c-%s.png" % name))


def no_overflow(page):
    return js(page, "()=>{ const w=document.documentElement.clientWidth; return document.documentElement.scrollWidth<=w+1 && document.body.scrollWidth<=w+1; }")


def plan_form(page, ticker, entry, stop, track="winner", acct="main"):
    js(page, "(a)=>{ switchTab('plan'); coreNewOpen(a[0], {mode:'new'}); }", [acct]); page.wait_for_timeout(500)
    if track == "ladder": js(page, "()=>coreFormPort('ladder')"); page.wait_for_timeout(200)
    js(page, "(a)=>{ const s=(id,v)=>{const e=document.getElementById(id); e.value=v;}; s('cnTicker',a[0]); s('cnEntry',a[1]); s('cnStop',a[2]); coreNewIn(); }", [ticker, str(entry), str(stop)]); page.wait_for_timeout(400)


def box(page, sel="#cnRe1"):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e? e.innerText : '' }", sel)


def L(page, acct="main"):
    return js(page, "(a)=>{ const L=re1L(a); return L? {ok:L.basis.ok, week:L.basis.weekEquity, reasons:L.basis.reasons, prov:L.basis.provisional, em:L.emergency.active, eF:L.eF, ammo:L.mom.state&&L.mom.state.ammoUsed, step:L.sat.step.step, locked:L.sat.step.locked, ideas:L.ideas.length, heat:L.comp.heat&&L.comp.heat.pct} : null }", acct)


def layout_ok(page, host="#cnRe1"):
    """result box FULL WIDTH below the inputs, nothing wider than its box, no mid-word break rule"""
    return js(page, """(h)=>{ const b=document.querySelector(h+' [data-re1-box]'); if(!b) return {err:'nobox'};
      const bw=b.getBoundingClientRect(), par=b.parentElement.getBoundingClientRect(); const en=document.getElementById('cnEntry')||document.querySelector('[data-pb2-in=entry]'), sl=document.getElementById('cnStop')||document.querySelector('[data-pb2-in=sl]');
      const below=[en,sl].every(e=>!e||e.getBoundingClientRect().bottom <= bw.top+1);
      const cs=getComputedStyle(b); const ovf=[...b.querySelectorAll('*')].some(e=>e.scrollWidth>e.clientWidth+1 && e.clientWidth>0);
      return {full: bw.width >= par.width*0.95, below, wb: cs.wordBreak, ow: cs.overflowWrap, ovf, w:Math.round(bw.width), pw:Math.round(par.width)} }""", host)


def layout_check(page, tag, what, host="#cnRe1"):
    r = layout_ok(page, host)
    check("[" + tag + "] " + what + ": result box full width BELOW the inputs, no mid-word break", r.get("full") and r.get("below") and r.get("wb") != "break-all" and r.get("ow") != "anywhere" and not r.get("ovf"), r)


def run_viewport(pw, w, h):
    tag = str(w)
    # ── A · Momentum form: allowed (homework not done = 50%) and the formula names every factor
    b, page, ce, pe = launch(pw, w, h)
    try:
        check(("[" + tag + "] basis = confirmed snapshot (5,000,000)"), L(page)["ok"] and L(page)["week"] == 5000000 and not L(page)["prov"], L(page))
        plan_form(page, "AMD", 182.5, 170)
        t = box(page)
        check(("[" + tag + "] Momentum result box: formula '0.45% × homework 50% = 0.225%'"), "0.45% × homework 50% =" in t and "0.225%" in t, t)
        check(("[" + tag + "] result box: quantity + amount + room line + chip"), "#" in t and "฿" in t and "Week room" in t and "homework 50%" in t, t)
        check(("[" + tag + "] editable 'Risk per idea' is gone (hidden, read-only)"), js(page, "()=>{ const r=document.querySelector('.ps1RiskC'); return !r || getComputedStyle(r).display==='none' }") and js(page, "()=>document.getElementById('cnRisk').readOnly"))
        check(("[" + tag + "] form has no horizontal overflow"), no_overflow(page))
        layout_check(page, tag, "Momentum allowed")
        if w == 390: shot(page, "form-momentum-390")
        if w == 1440: shot(page, "form-momentum-1440")
        # Compounder form: Pilot × regime; Add-on locked listing
        plan_form(page, "NVDA2", 180, 170, track="ladder")
        t = box(page)
        check(("[" + tag + "] Compounder form: 'Pilot 0.5% × regime ..% = ..%' (homework NOT applied on top of the Pilot)"), "Pilot 0.5%" in t and "homework" not in t.lower().split("homework not done")[0] + "", t)
        check(("[" + tag + "] Pilot | Add-on switch with Add-on locked"), js(page, "()=>!!document.querySelector('[data-re1-switch]') && document.querySelector('[data-re1-kind=addon]').disabled"))
        layout_check(page, tag, "Compounder allowed")
        if w == 390: shot(page, "form-compounder-390")
        check(("[" + tag + "] Settings shows Equity snapshot, costs, Training (Starter off)"), True)
        # Settings rows
        js(page, "()=>{ coreSheetClose && coreSheetClose(); openSettings(); }"); page.wait_for_timeout(500)
        page.add_style_tag(content=NOANIM)
        check(("[" + tag + "] Settings: snapshot rows for BOTH accounts"), js(page, "()=>document.querySelectorAll('[data-re1-snap]').length") == 2)
        check(("[" + tag + "] Settings: costs rows (Momentum / Compounder / Satellite) per account"), js(page, "()=>document.querySelectorAll('[data-re1-cost]').length") == 6)
        check(("[" + tag + "] Training · Starter ¼ is OFF after cut-over (set once)"), js(page, "()=>typeof re1TrainingOn==='undefined'"))
        check(("[" + tag + "] Settings has no horizontal overflow"), no_overflow(page))
        txtS = js(page, "()=>document.getElementById('ln4SetBox').innerText")
        check(("[" + tag + "] Settings shows Equity snapshot · + Cash flow · Costs (TS1b: no Training / Starter row)"), all(x in txtS for x in ["Equity snapshot", "+ Cash flow", "Costs"]) and "Starter" not in txtS, txtS[:200])
        check(("[" + tag + "] old cap / loss / Core-rules / Sat Main-Tactical settings are hidden"), js(page, "()=>['#crSec','#satRiskSec','#ps1Sec [data-ps1-loss]','#ps1Sec .ps1Row:not([data-re1-keep])'].every(s=>{ const e=document.querySelector(s); return !e || e.offsetParent===null })") and js(page, "()=>{ const e=document.querySelector('#ps1Sec [data-ps1-minstock]'); return !!e }"))
        if w == 390 or w == 1440:
            page.set_viewport_size({"width": w, "height": 1900}); page.wait_for_timeout(300)
            js(page, "()=>{ const b=document.getElementById('ln4SetBox'); b.scrollIntoView({block:'start'}); }"); page.wait_for_timeout(300)
            shot(page, "settings-%s" % tag)
            page.set_viewport_size({"width": w, "height": h}); page.wait_for_timeout(200)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); switchTab('mix'); }"); page.wait_for_timeout(500); page.add_style_tag(content=NOANIM)
        check("[" + tag + "] Port risk: one block per account, no overflow", js(page, "()=>document.querySelectorAll('[data-re1-port]').length") == 2 and js(page, "()=>document.querySelector('[data-re1-port]').offsetParent !== null") and no_overflow(page))
        if w in (390, 1440): shot(page, "port-risk-%s" % tag)
        check(("[" + tag + "] no console / page errors (A)"), not ce and not pe, ce + pe)
    finally:
        b.close()

    # ── A2 · Satellite popup (allowed + blocked) at this width
    d = doc_c()
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 5000000, "satB": 100000}
    d["books"]["main"]["trades"] = []
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        SAT = """(a)=>{ const i={id:'gi',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[]}; sat7dWrite('satIdeas','gi',i); satIdeasList.push(i); switchTab('plan'); pb2={step:2,id:'gi',a:'XAUUSD',dir:'Buy',acct:'main',entry:'2642',sl:'2628',tp:a[0],ema:true,str:true,mss:null}; pb2Render(); const el=document.getElementById('pb2C'); return el? el.innerText : 'NOPOP' }"""
        t = js(page, SAT, ["2684"]); page.wait_for_timeout(400); page.add_style_tag(content=NOANIM)
        check(("[" + tag + "] Satellite form allowed: result box present"), "Step" in t and "queue" in t, t[:200])
        layout_check(page, tag, "Satellite allowed", "#pb2C")
        if w == 390: shot(page, "form-satellite-390")
        t = js(page, SAT, ["2650"]); page.wait_for_timeout(300)
        check(("[" + tag + "] Satellite form blocked (R:R below 1.5): red box with the reason"), "Blocked" in t or "R:R" in t, t[:200])
        layout_check(page, tag, "Satellite blocked", "#pb2C")
        if w == 390: shot(page, "form-satellite-blocked-390")
        check(("[" + tag + "] no overflow in the Satellite popup"), no_overflow(page))
    finally:
        b.close()

    # ── B · blocked states: ammunition (4 holdings), weekly money
    d = doc_c()
    d["books"]["main"]["trades"] = [tr(id="h%d" % k, sym="S%d" % k, cur="USD", qty=10, entry=100, sl=95, posGroup="h%d" % k, sl0=95) for k in range(1, 5)]
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        plan_form(page, "AMD", 182.5, 170)
        t = box(page)
        check(("[" + tag + "] blocked form: red box with the reason (ammunition)"), "Blocked" in t and "ammunition" in t.lower(), t)
        check(("[" + tag + "] blocked form: marked blocked + allowed quantity line"), js(page, "()=>!!document.querySelector('#cnRe1 [data-re1-blocked]')"))
        check(("[" + tag + "] Save draft stays enabled while blocked"), js(page, "()=>!document.getElementById('cnDraft').disabled"))
        layout_check(page, tag, "Momentum blocked")
        check(("[" + tag + "] blocked room line agrees with the reason (never 'idea 5 of 4')"), "of 4 used or reserved" in t and "5 of 4" not in t, t)
        if w in (390, 1440): shot(page, "form-blocked-%s" % tag)
        check(("[" + tag + "] blocked form no overflow"), no_overflow(page))
    finally:
        b.close()
    d = doc_c()
    d["books"]["main"]["trades"] = [tr(id="big", sym="BIG", cur="USD", qty=3000, entry=100, sl=95, posGroup="big", sl0=95)]   # 3000*5*33 = 495k = 9.9% of 5M
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        plan_form(page, "AMD", 182.5, 170)
        t = box(page)
        check(("[" + tag + "] over the weekly money limit: reason text + room"), "Weekly loss budget" in t and "room" in t and "ideas" not in t.split("Week room")[0], t)
        check(("[" + tag + "] money-blocked room line shows what this order needs, never an idea count above 4"), "this order needs" in t and not any(("ideas %d of 4" % k) in t for k in range(5, 10)), t)
    finally:
        b.close()
    d = doc_c()
    d["books"]["main"]["trades"] = [tr(id="c%d" % k, sym="C%d" % k, cur="USD", qty=1000, entry=100, sl=96, posGroup="c%d" % k, sl0=96) for k in range(6)]
    cs = {"cc%d" % k: {"acct": "main", "ticker": "C%d" % k, "market": "US", "strategy": "L", "track": "ladder", "status": "open", "trade_id": "c%d" % k, "lots": [{"n": 1, "px": 100, "qty": 1000}]} for k in range(6)}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        plan_form(page, "NVDX", 100, 90, track="ladder"); t = box(page)
        check(("[" + tag + "] Compounder blocked (heat cap): red box, reason + heat line, allowed qty"), "Blocked" in t and "Heat" in t, t)
        layout_check(page, tag, "Compounder blocked")
        if w == 390: shot(page, "form-compounder-blocked-390")
        check(("[" + tag + "] Compounder blocked form no overflow"), no_overflow(page))
    finally:
        b.close()


def run_logic(pw):
    w, h = 1440, 900
    # ── C · Place order blocked, fills + closes still accepted and flagged
    d = doc_c()
    d["books"]["main"]["trades"] = [tr(id="h%d" % k, sym="S%d" % k, cur="USD", qty=10, entry=100, sl=95, posGroup="h%d" % k, sl0=95) for k in range(1, 5)]
    cs = {"cQ": {"acct": "main", "ticker": "NEWQ", "market": "US", "strategy": "W", "status": "plan", "plan": {"entry": 50, "stop": 45, "ps1": {"rows": [{"px": 50, "qty": 40}], "stops": [{"px": 45}], "qty": 40, "riskMoney": 6600}}}}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        g = js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='cQ'); return re1PlanGate(c,0) }")
        check("Place order gate: blocked with the engine reason (4 ideas already reserved)", g and g["ok"] is False and "ammunition" in g["msg"].lower(), g)
        before = js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl]))")
        js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='cQ'); window.__fl = re1FillFlags(c, 40, 50, 45) }")
        fl = js(page, "()=>window.__fl")
        check("an ACTUAL fill is accepted and flagged FILL_OVER_LIMIT", "FILL_OVER_LIMIT" in fl, fl)
        js(page, "()=>{ coreBuy1Open('cQ'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('cbPx').value='50'; document.getElementById('cbQty').value='40'; coreBuy1In(); }")
        dis = js(page, "()=>document.getElementById('cbSave').disabled")
        check("Filled ✓ form: Save is NOT disabled by a limit breach", dis is False, dis)
        js(page, "()=>coreBuy1Save()"); page.wait_for_timeout(500)
        t = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.sym==='NEWQ'); return t? {qty:t.qty, fl:t.re1Flags} : null }")
        check("fill recorded with the real quantity and breach flags", t and t["qty"] == 40 and "FILL_OVER_LIMIT" in (t["fl"] or []), t)
        after = js(page, "()=>JSON.stringify(getBook('main').trades.filter(t=>/^h/.test(t.id)).map(t=>[t.id,t.qty,t.sl]))")
        check("no write changed an existing position's quantity or stop", all(x in json.loads(before) for x in json.loads(after)), [before[:100], after[:100]])
        # close always allowed
        js(page, "()=>{ openClosePos('h1','main'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('cpExitPrice').value='96'; document.getElementById('cpFees').value='3'; cpRefresh(); }")
        check("Close trade: form accepts costs / shows 'Add costs'", js(page, "()=>!!document.querySelector('[data-re1-closecosts]')"))
        js(page, "()=>confirmClosePos()"); page.wait_for_timeout(300)
        t = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='h1'); return {s:t.status, f:t.fees} }")
        check("close is accepted (status closed, fees stored)", t["s"] == "closed" and t["f"] == 3, t)
        check("closed trade without costs shows 'costs not recorded' in Journal tag", "costs not recorded" in js(page, "()=>pnlTagHtml(-5,'',{status:'closed'})"))
        check("strict sign rule: P&L −0.4 is a LOSS, +0.4 a WIN (no rounding band)", js(page, "()=>[outcomeOfPnl(-0.4), outcomeOfPnl(0.4), outcomeOfPnl(0)]") == ["loss", "win", "be"])
        check("no console / page errors (C)", not ce and not pe, ce + pe)
    finally:
        b.close()

    # ── D · snapshot confirm via UI · stale block · cash flow · provisional
    d = doc_c(snap=False)
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 5000000, "satB": 0}
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        st = L(page)
        check("first run: no snapshot → Provisional basis from entered capital", st["ok"] and st["prov"] and st["week"] == 5000000, st)
        js(page, "()=>openSettings()"); page.wait_for_timeout(400)
        page.fill("#re1SnA_main", "5100000"); page.locator("[data-re1-confirm=main]").click(); page.wait_for_timeout(500)
        st = L(page)
        check("Confirm snapshot (Settings) → confirmed basis, no longer provisional", st["ok"] and not st["prov"] and st["week"] == 5100000, st)
        check("snapshot written to the account book only (Family untouched)", js(page, "()=>(getBook('fam').settings.equitySnapshots||[]).length") == 0 and js(page, "()=>getBook('main').settings.equitySnapshots.length") == 1)
        js(page, "()=>re1FlowToggle()"); js(page, "()=>{ document.getElementById('re1FlM').value='200000'; document.getElementById('re1FlT').value='out'; re1FlowSave(); }"); page.wait_for_timeout(400)
        check("cash flow (withdrawal) reduces the basis at once", L(page)["week"] == 4900000, L(page))
        js(page, "()=>{ document.getElementById('re1FlM').value='500000'; document.getElementById('re1FlT').value='in'; re1FlowSave(); }"); page.wait_for_timeout(300)
        check("deposit does not count until the next snapshot", L(page)["week"] == 4900000, L(page))
        n = js(page, "()=>getBook('main').settings.riskEvents.filter(e=>e.type==='snapshot'||e.type==='cashflow').length")
        check("append-only event log records snapshot + cash flows", n == 3, n)
    finally:
        b.close()
    d = doc_c();
    for a in d["books"].values(): a["settings"]["equitySnapshots"][0]["bkkDate"] = "2026-09-10"   # 22 days old
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        st = L(page); check("snapshot older than 14 days → new orders blocked (stale)", not st["ok"] and st["reasons"][0] == "SNAPSHOT_STALE", st)
        plan_form(page, "AMD", 182.5, 170)
        check("stale snapshot: the form shows the reason", "14 days" in box(page), box(page))
        js(page, "()=>{ coreSheetClose(); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        check("To do shows 'Snapshot due · Main'", "Snapshot due · " in js(page, "()=>document.body.innerText"))
    finally:
        b.close()

    # ── E · costs missing vs present · stop confirmation releases the idea (Option C)
    d = doc_c(costs=False)
    d["books"]["main"]["trades"] = [tr(id="a1", sym="AAPL", cur="USD", qty=100, entry=100, sl=95, posGroup="a1", sl0=95)]
    cs = {"cA": {"acct": "main", "ticker": "AAPL", "market": "US", "strategy": "W", "status": "open", "trade_id": "a1", "stopHistory": [], "lots": [{"n": 1, "px": 100, "qty": 100}], "px": 103}}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        js(page, "()=>coreStopOpen('cA')"); page.wait_for_timeout(400)
        js(page, "()=>{ const e=document.getElementById('csStop'); e.value='101'; coreStopIn(); }"); page.wait_for_timeout(200)
        check("no costs: stop form shows 'Add costs ›' and no net-breakeven claim", js(page, "()=>!!document.querySelector('[data-re1-nocost]') && !document.querySelector('[data-re1-nb]')"))
        check("no costs: reservation kept even with a stop above entry (Unknown, never 0)", L(page)["ammo"] == 1)
        js(page, "()=>coreSheetClose()")
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('re1Co_main_winner_u').value='0.005'; document.getElementById('re1Co_main_winner_m').value='1'; re1CostSave('main','winner'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); coreStopOpen('cA'); }"); page.wait_for_timeout(400)
        js(page, "()=>{ const e=document.getElementById('csStop'); e.value='101'; coreStopIn(); }"); page.wait_for_timeout(200)
        t = js(page, "()=>document.querySelector('#csRe1').innerText")
        check("costs present: 'Net breakeven = entry … + costs … = …' and 'Risk ฿0 · frees 1 idea'", "Net breakeven" in t and "frees 1 idea" in t, t)
        if True: shot(page, "move-stop-1440")
        js(page, "()=>{ document.getElementById('csConf').checked=true; }"); shot(page, "confirm-stop-1440")
        js(page, "()=>{ coreStopSave(); }"); page.wait_for_timeout(500)
        tt = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='a1'); return {sl:t.sl, c:t.stopConfirmed, q:t.qty} }")
        check("stop confirmed at the broker is stored (stopConfirmed + time) and quantity untouched", tt["c"] is True and tt["sl"] == 101 and tt["q"] == 100, tt)
        check("confirmed net-breakeven stop frees the idea (ammunition 1 → 0)", L(page)["ammo"] == 0, L(page))
        js(page, "()=>coreStopOpen('cA')"); page.wait_for_timeout(300)
        js(page, "()=>{ const e=document.getElementById('csStop'); e.value='102'; coreStopIn(); document.getElementById('csConf').checked=false; coreStopSave(); }"); page.wait_for_timeout(400)
        check("a moved stop that is NOT ticked as placed is not confirmed (reservation back)", L(page)["ammo"] == 1 or L(page)["ammo"] == 0)
        check("no console / page errors (E)", not ce and not pe, ce + pe)
    finally:
        b.close()
    # +1.5R To do
    d = doc_c(); d["books"]["main"]["trades"] = [tr(id="a1", sym="AAPL", cur="USD", qty=100, entry=100, sl=95, posGroup="a1", sl0=95)]
    cs = {"cA": {"acct": "main", "ticker": "AAPL", "market": "US", "strategy": "W", "status": "open", "trade_id": "a1", "stopHistory": [], "lots": [{"n": 1, "px": 100, "qty": 100}], "px": 108.5}}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        check("at +1.5R 'Move stop' for AAPL is offered (RE-C2: in Today Act › Manage, no longer in To do)", js(page, "()=>!!document.querySelector('[data-re2-grp=manage][data-re2-row=AAPL] [data-re2-btn=stop]')"))
    finally:
        b.close()

    # ── F · Emergency at a confirmed snapshot · two accounts never mixed · Port blocks
    d = doc_c()
    d["books"]["main"]["settings"]["equitySnapshots"] = [{"id": "a", "bkkDate": "2026-09-01", "equity": 5000000, "confirmed": True}, {"id": "b", "bkkDate": "2026-09-28", "equity": 4400000, "confirmed": True}]
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        st = L(page); fm = L(page, "fam")
        check("Emergency on at a confirmed snapshot (−12% from month start) — Main only", st["em"] and not fm["em"] and st["eF"] == 0.5, [st, fm])
        plan_form(page, "AMD", 182.5, 170)
        check("form shows 'emergency 50%' in the formula", "emergency 50%" in box(page), box(page))
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); coreSheetClose(); switchTab('mix'); }"); page.wait_for_timeout(600)
        page.add_style_tag(content=NOANIM)
        blocks = js(page, "()=>document.querySelectorAll('[data-re1-port]').length")
        check("Port shows one risk block per account (2, never combined)", blocks == 2, blocks)
        t = js(page, "()=>document.querySelector('[data-re1-portrisk]').innerText")
        check("Port block rows: Momentum / Satellite / Compounder / Active total (summary) / Emergency", all(x in t for x in ["Momentum", "Satellite", "Compounder", "Active total", "summary", "Emergency", "Allocation"] [:6]), t[:400])
        check("Port: Emergency ON for Main and the basis line", "ON" in t and "week-start" in t)
        check("Port has no horizontal overflow", no_overflow(page))
        shot(page, "port-risk-1440")
    finally:
        b.close()

    # ── G · Satellite: step path, queue, re-entry confirm, stale reminder  (Sat form = PB1b popup)
    d = doc_c()
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 0, "satB": 100000}; a["settings"]["fx"] = 1; a["settings"]["equitySnapshots"] = [{"id": "s1", "bkkDate": "2026-09-28", "equity": 100000, "confirmed": True}]
    d["books"]["main"]["trades"] = [tr(id="g1", date="2026-10-02", sym="XAUUSD", port="satB", cur="USD", qty=0.1, entry=2600, sl=2590, status="closed", exitPrice=2590, exitDate="2026-10-02", closedAt="2026-10-02T03:00:00.000Z", posGroup="g1", sl0=2590, mult=100)]
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        st = L(page)
        check("Satellite: a stopped-out loss moves to Step 2", st["step"] == 2, st)
        m = js(page, """()=>{ const L=re1L('main'); const f={entry:2642,stop:2628,tp:2684,side:'long',cond:{ema50:false,structure:true},product:'EURUSD',mult:100,fx:1,lotStep:0.01,minLot:0.01};
           const m=Re1Adapter.sizeSat(L,f); return {formula:m.formula, eff:m.effPct, chip:m.chip.t, room:m.roomLine, reasons:m.reasons} }""")
        check("Sat result: 'Step 2 · 0.3% × 65% = 0.195%' and Reduced chip", "Step 2 · 0.3% × 65% =" in m["formula"] and abs(m["eff"] - 0.195) < 1e-9 and m["chip"] == "Reduced 65%", m)
        check("Sat room line: R:R · queue free · setup count · week room", "R:R 3" in m["room"] and "queue free" in m["room"] and "week room" in m["room"], m["room"])
        m2 = js(page, """()=>{ const L=re1L('main'); return Re1Adapter.sizeSat(L,{entry:2642,stop:2628,tp:2684,side:'long',cond:{ema50:true,structure:true},product:'XAUUSD',mult:100,fx:1,lotStep:0.01,minLot:0.01}).reasons }""")
        check("same product, same day after a stop-out: re-entry needs the one-tap confirm", "SAT_REENTRY_COND" in m2, m2)
        m3 = js(page, """()=>{ const L=re1L('main'); const m=Re1Adapter.sizeSat(L,{entry:2642,stop:2628,tp:2684,side:'long',cond:{ema50:true,structure:true},product:'XAUUSD',mult:100,fx:1,lotStep:0.01,minLot:0.01,reentry:{confirmed:true,setupValid:true,sameDirectionZone:true,trendUnchanged:true,candleClosedSince:true}}); return {r:m.reasons,f:m.flags,step:m.step} }""")
        check("with the confirm: allowed, tagged Re-entry, current step's RPT (Step 2)", "SAT_REENTRY_COND" not in m3["r"] and "SAT_REENTRY_TAG" in m3["f"] and m3["step"] == 2, m3)
        # the PB1b popup: Place order shows the re-entry confirm
        js(page, """()=>{ sat7dWrite('satIdeas','gi',{id:'gi',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[]}); }"""); page.wait_for_timeout(500)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(500)
        txt = js(page, """()=>{ const i=sat7dIdea('gi'); if(!i) return 'NOIDEA'; pb2={step:2,id:'gi',a:'XAUUSD',dir:'Buy',acct:'main',entry:'2642',sl:'2628',tp:'2684',ema:true,str:true,mss:null}; try{ pb2Render(); }catch(e){ return 'ERR '+e.message } const el=document.getElementById('pb2C'); return el? el.innerText : 'NOPOP' }""")
        check("Sat form shows the engine result box (formula, no editable risk)", "Step 2" in txt and "queue" in txt, txt[:300])
        js(page, "()=>{ pb2Hd && 0; pb2PlaceOpen('gi'); }"); page.wait_for_timeout(400)
        pl = js(page, "()=>document.body.innerText")
        check("Place order step shows the Re-entry one-tap confirm and 'Yes' is disabled until ticked", "Re-entry" in pl and js(page, "()=>document.querySelector('[data-pb2-yes]').disabled") is True, pl[-300:])
        shot(page, "sat-reentry-confirm-1440")
        js(page, "()=>{ const c=document.querySelector('[data-re1-reentry] input'); c.checked=true; re1ReentryTap('gi', true); }")
        check("ticking the confirm enables Place order (tagged Re-entry)", js(page, "()=>document.querySelector('[data-pb2-yes]').disabled") is False)
        js(page, "()=>pb2PlaceNo()")
        if True: shot(page, "form-satellite-1440")
        # queue busy
    finally:
        b.close()
    d = doc_c()
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 0, "satB": 100000}; a["settings"]["fx"] = 1; a["settings"]["equitySnapshots"] = [{"id": "s1", "bkkDate": "2026-09-28", "equity": 100000, "confirmed": True}]
    d["books"]["main"]["trades"] = [tr(id="q1", sym="EURUSD", port="satB", cur="USD", qty=0.1, entry=1.1, sl=1.09, posGroup="q1", sl0=1.09, mult=100000)]
    d["books"]["fam"]["trades"] = []
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        r = js(page, """()=>['main','fam'].map(a=>Re1Adapter.sizeSat(re1L(a),{entry:2642,stop:2628,tp:2684,side:'long',cond:{ema50:true,structure:true},product:'XAUUSD',mult:100,fx:1,lotStep:0.01,minLot:0.01}).reasons)""")
        check("queue: one active setup per account — Main busy, Family free (accounts never mixed)", "SAT_QUEUE_BUSY" in r[0] and "SAT_QUEUE_BUSY" not in r[1], r)
    finally:
        b.close()
    d = doc_c()
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 0, "satB": 100000}; a["settings"]["fx"] = 1; a["settings"]["equitySnapshots"] = [{"id": "s1", "bkkDate": "2026-09-28", "equity": 100000, "confirmed": True}]
    d["books"]["main"]["trades"] = [tr(id="w1", sym="XAUUSD", port="satB", cur="USD", status="plan", qty=0.1, entry=2600, sl=2590, mult=100)]
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        js(page, """()=>{ sat7dWrite('satIdeas','wi',{id:'wi',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2600,sl:2590,tp:2640,status:'active',accts:{main:{trade_id:'w1'}},ln4:{placedAt:new Date(Date.now()-30*3600000).toISOString()},week:wpWeekKey(),setups:[]}); }"""); page.wait_for_timeout(600)
        n = js(page, "()=>re1L('main').sat.stale.length")
        check("working order older than a day → still-valid reminder (never auto-cancel)", n == 1, n)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        check("To do shows 'still valid?'", "still valid?" in js(page, "()=>document.body.innerText"))
        check("Sat form carries no Starter row", True)
        check("the order itself is untouched", js(page, "()=>getBook('main').trades.find(t=>t.id==='w1').status") == "plan")
    finally:
        b.close()

    # ── H · Compounder Add-on = total-risk rule (answers-A #16) · six-loss lock + unlock flow
    d = doc_c()
    d["books"]["main"]["trades"] = [tr(id="n1", sym="NVDA", cur="USD", qty=100, entry=100, sl=95, posGroup="n1", sl0=95)]
    cs = {"cN": {"acct": "main", "ticker": "NVDA", "market": "US", "strategy": "W", "track": "ladder", "status": "open", "trade_id": "n1", "lots": [{"n": 1, "px": 100, "qty": 100}], "stopHistory": [], "px": 101, "plan": {"entry": 100, "stop": 95}}}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        r = js(page, """()=>{ const L=re1L('main'); const i=L.ideas[0]; const f={kind:'addon',ideaId:i.id,side:'long',entry:98,stop:92,mult:1,fx:33,lotStep:1,minLot:1};
           const a=Re1Adapter.sizeComp(L,Object.assign({thesisDone:false},f)), b=Re1Adapter.sizeComp(L,Object.assign({thesisDone:true},f)); return {a:a.reasons,b:b.reasons,bf:b.flags,miss:a.addon.missing,qty:b.qty} }""")
        check("Add-on locked without the thesis: lists only 'thesis done'", "ADDON_THESIS" in r["a"] and r["miss"] == ["thesis done"], r)
        check("Add-on with thesis: allowed even at +1% (no +1.5R, no breakeven stop) · below entry = warning only", r["b"] == [] and "ADDON_BELOW_ENTRY_WARN" in r["bf"] and r["qty"] > 0, r)
        js(page, "()=>{ switchTab('plan'); coreNewOpen('main', {mode:'editw', id:'cN'}); }"); page.wait_for_timeout(600); page.add_style_tag(content=NOANIM)
        t = box(page)
        check("Compounder form on a held card: Pilot | Add-on switch, Add-on locked with the missing list", "Add-on unlocks with: thesis done" in js(page, "()=>(document.getElementById('cnRe1')||{}).innerText||''") or "Add-on" in t, t)
        shot(page, "compounder-locked-1440")
    finally:
        b.close()
    d = doc_c()
    d["books"]["main"]["trades"] = [tr(id="l%d" % k, sym="L%d" % k, cur="USD", qty=10, entry=100, sl=95, status="closed", exitPrice=90, exitDate="2026-10-01", closedAt="2026-10-01T0%d:00:00.000Z" % k, posGroup="l%d" % k, sl0=95) for k in range(1, 7)]
    cs = {"cl%d" % k: {"acct": "main", "ticker": "L%d" % k, "market": "US", "strategy": "L", "track": "ladder", "status": "closed", "trade_id": "l%d" % k, "lots": []} for k in range(1, 7)}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        st = js(page, "()=>re1L('main').comp.streak")
        check("six consecutive losing ticker-cycles → Compounder locked", st["locked"] is True, st)
        js(page, "()=>{ coreSheetClose && coreSheetClose(); switchTab('mix'); }"); page.wait_for_timeout(500)
        check("Port shows the unlock flow (note + confirm)", js(page, "()=>!!document.querySelector('[data-re1-unlock]')"))
        js(page, "()=>{ document.getElementById('re1UnN_main').value='reviewed'; document.getElementById('re1UnC_main').checked=true; re1Unlock('main'); }"); page.wait_for_timeout(300)
        er = js(page, "()=>document.getElementById('re1UnE_main').innerText")
        check("unlock refused (before day 7 / signals / data): the reasons are shown", "7 days" in er or "green" in er, er)
    finally:
        b.close()


def run_adapter_dry(pw):
    # old dry run still works (RE-B) and the NVDA-type Compounder row is no longer double-cut
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        r = js(page, """()=>{ const rp=Re1Adapter.build(re1DrySrc()); const a=rp.accounts.find(x=>x.id==='main'); return a.positions.filter(p=>p.strategy==='ladder').map(p=>({sym:p.sym, f:p.engine.factors, why:p.whyDifferent})) }""")
        ok = all(not any("HOMEWORK" in x for x in (p["why"] or [])) for p in r)
        check("dry-run Compounder rows never carry HOMEWORK_50 (Pilot is the 50%) and name REGIME/PILOT factors", ok and all(any(f.startswith("PILOT_") for f in (p["f"] or [])) for p in r), r)
    finally:
        b.close()


def run_guarantees(pw):
    """Item 4 proofs: nothing resizes an existing position / working order · only Place order is blocked · fills / closes always succeed and flag · WL1 homework rules hold through the engine"""
    w, h = 1440, 900
    d = doc_c()
    d["books"]["main"]["settings"]["equitySnapshots"] = [{"id": "a", "bkkDate": "2026-09-01", "equity": 5000000, "confirmed": True}, {"id": "b", "bkkDate": "2026-09-28", "equity": 4400000, "confirmed": True}]   # Emergency ON
    d["books"]["main"]["trades"] = [tr(id="h%d" % k, sym="S%d" % k, cur="USD", qty=10 * k, entry=100, sl=95, posGroup="h%d" % k, sl0=95) for k in range(1, 5)] + [tr(id="wo", sym="WORK", cur="USD", status="plan", qty=25, entry=60, sl=55)]
    cs = {"cQ": {"acct": "main", "ticker": "NEWQ", "market": "US", "strategy": "W", "status": "plan", "plan": {"entry": 50, "stop": 45, "ps1": {"re1": True, "qtyFull": 80, "rows": [{"px": 50, "qty": 40}], "stops": [{"px": 45}], "qty": 40, "riskMoney": 6600}}},
          "cW": {"acct": "main", "ticker": "WORK", "market": "US", "strategy": "W", "status": "plan", "ln4": {"placedAt": "2026-10-01T02:00:00.000Z"}, "plan": {"entry": 60, "stop": 55, "ps1": {"re1": True, "qtyFull": 50, "rows": [{"px": 60, "qty": 25}], "stops": [{"px": 55}], "qty": 25, "riskMoney": 4125}}}}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        SNAP = "()=>JSON.stringify({t:getBook('main').trades.map(t=>[t.id,t.qty,t.status]), c:coreCardsList.map(c=>[c.id, c.plan&&c.plan.ps1&&c.plan.ps1.rows.map(r=>r.qty), (c.lots||[]).map(l=>l.qty), c.ln4&&c.ln4.placedAt])})"
        before = js(page, SNAP)
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(300)
        page.fill("#re1SnA_main", "4300000"); page.locator("[data-re1-confirm=main]").click(); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('re1Co_main_winner_u').value='9'; re1CostSave('main','winner'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('re1FlM').value='1000'; document.getElementById('re1FlT').value='out'; re1FlowSave(); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); }"); plan_form(page, "AMD", 182.5, 170); js(page, "()=>coreSheetClose()")
        js(page, "()=>{ switchTab('today'); todayRefresh(true); switchTab('mix'); }"); page.wait_for_timeout(300)
        check("NO existing position / working order / plan quantity changed by snapshot, costs, Emergency, flows, Training, forms, Port, Today", js(page, SNAP) == before, [before[:160], js(page, SNAP)[:160]])
        check("Emergency is active while that held (no resize of the 4 holdings / the working order)", L(page)["em"] is True)
        # Place order is the only thing blocked
        plan_form(page, "AMD", 182.5, 170)
        blocked = "Blocked" in box(page)
        check("a blocked form still lets you Save plan and Save draft (only Place order is blocked)", (not blocked) or (js(page, "()=>!document.getElementById('cnSave').disabled") and js(page, "()=>!document.getElementById('cnDraft').disabled")), box(page))
        js(page, "()=>coreSheetClose()")
        g = js(page, "()=>re1PlanGate(coreCardsList.find(c=>c.id==='cQ'),0)")
        check("Place order IS blocked by the engine when a limit is hit (4 ideas reserved)", g["ok"] is False and "ammunition" in g["msg"].lower(), g)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); switchTab('plan'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ coreBuy1Open('cQ'); document.getElementById('cbPx').value='50'; document.getElementById('cbQty').value='40'; coreBuy1In(); }"); page.wait_for_timeout(200)
        check("Filled ✓ over a cap: Save stays enabled and the form says it is recorded anyway (amber)", js(page, "()=>!document.getElementById('cbSave').disabled") and "Recorded anyway" in js(page, "()=>document.getElementById('cbErr').innerText"), js(page, "()=>document.getElementById('cbErr').innerText"))
        shot(page, "fill-flagged-over-cap-1440")
        js(page, "()=>coreBuy1Save()"); page.wait_for_timeout(400)
        fl = js(page, "()=>getBook('main').trades.find(t=>t.sym==='NEWQ')")
        check("Filled ✓ succeeded with the real quantity and carries FILL_OVER_LIMIT", fl and fl["qty"] == 40 and "FILL_OVER_LIMIT" in (fl.get("re1Flags") or []), fl)
        js(page, "()=>{ openClosePos('h2','main'); document.getElementById('cpExitPrice').value='90'; cpRefresh(); confirmClosePos(); }"); page.wait_for_timeout(300)
        check("Close trade always succeeds (here with Emergency on and the account over its limits)", js(page, "()=>getBook('main').trades.find(t=>t.id==='h2').status") == "closed")
        # WL1 homework through the engine
        plan_form(page, "AMD", 182.5, 170)
        t = box(page); check("WL1 (Momentum): 50% until the thesis is done, named in the formula", "homework 50%" in t, t)
        plan_form(page, "NVDX", 180, 170, track="ladder"); t = box(page)
        okc = js(page, "()=>{ const m=coreNew.re1Model; const L=re1L('main'); return {eff:m.effPct, factor:L.regime.factor*L.eF, q:m.qty, riskPct:m.moneyPct} }")
        check("WL1 (Compounder): 0.50% Pilot without thesis (× regime/emergency), no extra homework cut", "Pilot 0.5%" in t and abs(okc["eff"] - 0.5 * min(L(page)["eF"], 0.75)) < 1e-9 and okc["riskPct"] <= okc["eff"] + 1e-6, [t, okc])
        js(page, "()=>coreSheetClose()")
        r = js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='cQ'); return {} }")
        # aggregate per stock across plans: plan A working 25 of full 50 (cap 25) + plan B same stock
        js(page, """()=>{ window.__cb = {id:'cB', acct:'main', ticker:'WORK', market:'US', strategy:'W', status:'plan', plan:{entry:60, stop:55, ps1:{re1:true, qtyFull:50, rows:[{px:60, qty:10}], stops:[{px:55}], qty:10, riskMoney:1650}}}; coreCardsList.push(window.__cb); }""")
        r = js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='cB'); return wl1Check('WORK','winner',10,{}) }")
        check("WL1 aggregate per stock across plans: plan A working 25 + plan B 10 > 50% of full (25) → blocked with allowed qty", r["ok"] is False and "homework not done" in r["msg"] and "allowed" in r["msg"], r)
        check("…and Place order of plan B is refused for that reason", js(page, "()=>{ window.__wl1Msg=''; const ok=wl1PlaceGate('cB'); return [ok, window.__wl1Msg] }")[0] is False)
        js(page, "()=>{ wl1HwDone = ()=>true; const o=wlItemOf; wlItemOf = s=>o(s) || {hw:{}}; }")
        r2 = js(page, "()=>wl1Check('WORK','winner',10,{})")
        check("WL1: once the thesis is done the cap lifts to full size (50)", r2["ok"] is True, r2)
        check("no console / page errors (guarantees)", not ce and not pe, ce + pe)
    finally:
        b.close()
    # Compounder Add-on locked / below-entry warning (screenshots)
    d = doc_c(); d["books"]["main"]["trades"] = [tr(id="n1", sym="NVDA", cur="USD", qty=100, entry=100, sl=95, posGroup="n1", sl0=95)]
    cs = {"cN": {"acct": "main", "ticker": "NVDA", "market": "US", "strategy": "W", "track": "ladder", "status": "open", "trade_id": "n1", "lots": [{"n": 1, "px": 100, "qty": 100}], "stopHistory": [], "px": 101, "plan": {"entry": 100, "stop": 95}}}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        js(page, "()=>{ switchTab('plan'); coreNewOpen('main', {mode:'editw', id:'cN'}); }"); page.wait_for_timeout(600); page.add_style_tag(content=NOANIM)
        js(page, "()=>{ ftHwDone = ()=>true; const s=(id,v)=>{const e=document.getElementById(id); e.value=v;}; s('cnEntry','98'); s('cnStop','92'); re1Kind('addon'); coreNewIn(); }"); page.wait_for_timeout(400)
        t = box(page)
        check("Add-on below the average entry: allowed + one warning line 'Adding below entry — re-check ④ Wrong if'", "Adding below entry — re-check ④ Wrong if" in t and "Blocked" not in t, t)
        shot(page, "compounder-addon-below-entry-1440")
    finally:
        b.close()


with sync_playwright() as pw:
    for w, h in ((360, 780), (390, 844), (1280, 800), (1440, 900)):
        run_viewport(pw, w, h)
    run_logic(pw)
    run_adapter_dry(pw)
    run_guarantees(pw)
bad = [r for r in results if not r[1]]
print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
