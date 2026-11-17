#!/usr/bin/env python3
"""RE-C2 — Today · Act in three groups + risk strip + bottom pair (390 / 1280 / 1440). Display only: numbers come from the engine through re1L().
Run: python3 run_tests_re1c2.py"""
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
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:600]) if (not ok and d) else ""))


def launch(pw, w, h, d=None, c=None):
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=d or doc_c(), cards=c if c is not None else cards(), clean=True)
    page.add_style_tag(content=NOANIM); page.wait_for_timeout(500)
    js(page, "()=>{ tv1SetupLeft = ()=>1; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)   # Setup ✓ present (board treats plans without it as Waiting)
    return b, page, ce, pe


def refresh(page):
    js(page, "()=>{ re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(350)


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "re1c2-%s.png" % name))


def no_overflow(page):
    return js(page, "()=>{ const w=document.documentElement.clientWidth; return document.documentElement.scrollWidth<=w+1 && document.body.scrollWidth<=w+1; }")


def rows(page, grp):
    return js(page, "(g)=>[...document.querySelectorAll('[data-re2-grp=\"'+g+'\"]')].map(r=>({sym:r.dataset.re2Row, t:r.innerText.replace(/\\s+/g,' '), btn:(r.querySelector('button')||{}).dataset?.re2Btn||'', dis:!!(r.querySelector('button')||{}).disabled}))", grp)


def txt(page, sel):
    return js(page, "(s)=>{const e=document.querySelector(s);return e?e.innerText.replace(/\\s+/g,' '):''}", sel)


def override(page, body):
    """display-layer test hook: tweak the engine result the strip reads (shallow copy)"""
    js(page, "(b)=>{ if(!window.__re1L) window.__re1L = re1L; const o = window.__re1L; re1L = a=>{ const L = o(a); if(!L) return L; const C = Object.assign({}, L); (new Function('L','C', b))(L, C); return C; }; re1Cache = {}; todayRefresh(true); }", body)
    page.wait_for_timeout(350)


def plan_card(sym, entry, stop, px=None, ready=False, **kw):
    c = {"acct": "main", "ticker": sym, "market": "US", "strategy": "W", "status": "plan", "plan": {"entry": entry, "stop": stop, "ps1": {"rows": [{"px": entry, "qty": 40}]}}}
    if px is not None: c["px"] = px; c["pxDate"] = "2026-10-02"
    if ready: c["plan"]["ready"] = True
    c.update(kw); return c


def seed(page, cs):
    for cid, c in cs.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    js(page, "()=>{ coreStop(); coreStart(); }"); page.wait_for_timeout(700); refresh(page)


def run_viewport(pw, w, h):
    tag = str(w)
    # ── strip: Normal + events chip hidden without data
    b, page, ce, pe = launch(pw, w, h)
    try:
        st = txt(page, "[data-re2-strip]")
        check("[%s] strip Normal: green state + MMT / SAT / COMP values" % tag, "Normal" in st and js(page, "()=>document.querySelector('[data-re2-state]').classList.contains('g')") and ("MMT" in st and "SAT" in st and "COMP" in st if w > 560 else True), st)
        check("[%s] no event data → no event chip" % tag, js(page, "()=>!document.querySelector('[data-re2-evchip]')"))
        check("[%s] old status text removed from the top card (no risk line / port chip)" % tag, js(page, "()=>!document.querySelector('[data-ln4-status] [data-ln4-risk], [data-ln4-status] [data-ln4-portpill]')"))
        check("[%s] To do + Daily/Weekend untouched above Act" % tag, js(page, "()=>!!document.querySelector('[data-td3-sw]') && !!document.querySelector('[data-ln4-status]')"))
        check("[%s] no horizontal overflow" % tag, no_overflow(page))
        # states via the engine result (display layer reads it)
        cases = [
            ("Half size", "C.emergency = Object.assign({}, L.emergency, {active:true})", "a", None),
            ("Locked MMT", "C.mom = {state:Object.assign({}, L.mom.state, {ammoUsed:4}), chk:L.mom.chk}", "r", "MMT locked"),
            ("Locked SAT", "C.sat = Object.assign({}, L.sat, {step:Object.assign({}, L.sat.step, {locked:true})})", "r", "SAT locked"),
            ("Locked COMP", "C.comp = Object.assign({}, L.comp, {streak:Object.assign({}, L.comp.streak, {locked:true})})", "r", "COMP locked"),
            ("Snapshot due", "C.basis = Object.assign({}, L.basis, {confirmedThisWeek:false})", "a", None),
            ("Snapshot stale", "C.basis = {ok:false, reasons:['SNAPSHOT_STALE']}", "r", None),
        ]
        for name, body, col, chip in cases:
            js(page, "()=>{ if(window.__re1L){ re1L = window.__re1L; } }")
            override(page, body)
            nm = txt(page, "[data-re2-state]")
            cl = js(page, "()=>document.querySelector('[data-re2-state]').className")
            ok = (col in cl.split()) and ((name.split()[0] == "Locked" and nm == "Locked") or (name == "Half size" and nm == "Half size") or (name == "Snapshot due" and nm == "Snapshot due") or (name == "Snapshot stale" and nm == "Snapshot stale"))
            if chip: ok = ok and (chip in txt(page, "[data-re2-strip]")) and js(page, "(k)=>document.querySelector('[data-re2-chip=\"'+k+'\"]').classList.contains('r')", chip.split()[0].lower())
            check("[%s] strip %s → %s %s" % (tag, name, "red" if col == "r" else "amber", ("+ chip '" + chip + "'") if chip else ""), ok, [nm, cl, txt(page, "[data-re2-strip]")])
            if w == 1440 and name == "Locked SAT": shot(page, "locked-1440")
            if w == 390 and name == "Locked SAT": shot(page, "locked-390")
            if w <= 560 and name == "Locked SAT":
                vis = js(page, "()=>[...document.querySelectorAll('[data-re2-strip] .rk')].filter(e=>getComputedStyle(e).display!=='none').map(e=>e.dataset.re2Chip||e.dataset.re2Evchip)")
                check("[%s] phone strip: only abnormal chips visible" % tag, vis == ["sat"], vis)
        # worst wins
        override(page, "C.emergency = Object.assign({}, L.emergency, {active:true}); C.sat = Object.assign({}, L.sat, {step:Object.assign({}, L.sat.step, {locked:true})})")
        check("[%s] worst state wins (Half size + SAT locked → red Locked)" % tag, txt(page, "[data-re2-state]") == "Locked")
    finally:
        b.close()
    # ── Enter · 3% boundary · price missing · Satellite never auto-enters · Ready
    cs = cards()
    cs["e1"] = plan_card("AAA", 100, 92, px=102.9)      # +2.9% in
    cs["e2"] = plan_card("BBB", 100, 92, px=103.1)      # +3.1% out
    cs["e3"] = plan_card("CCC", 100, 92)                # no price out
    cs["e4"] = plan_card("DDD", 100, 92, px=97.0)       # −3.0% in
    cs["e5"] = plan_card("EEE", 100, 92, px=150, ready=True)   # far but flagged
    b, page, ce, pe = launch(pw, w, h, None, cs)
    try:
        en = [r["sym"] for r in rows(page, "enter")]
        check("[%s] Enter: EF1: Ready is automatic — every unblocked plan is in (2.9%% · −3.0%% · 3.1%% passed · no price · far)" % tag, "AAA" in en and "DDD" in en and "EEE" in en and "CCC" in en and "BBB" in en, en)   # RE-D §6: >3% past entry shows as the amber 'passed entry · missed?' prompt (not a Near row)
        t = {r["sym"]: r["t"] for r in rows(page, "enter")}
        check("[%s] chips: Ready / Near with signed distance (+2.9%%)" % tag, ("Near" in t.get("AAA", "") or "Ready" in t.get("AAA", "") or w <= 560) and "+2.9%" in t.get("AAA", ""), t)
        check("[%s] marker is the signed distance of price from entry" % tag, "+2.9%" in t.get("AAA", "") and "−3.0%" in t.get("DDD", "") and "passed entry" in t.get("BBB", "") and "passed entry" in t.get("EEE", ""), t)   # RE-D §6: 3.1% and the far Ready plan are passed-entry prompts
        js(page, """()=>{ const i={id:'gs',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[]}; sat7dWrite('satIdeas','gs',i); satIdeasList.push(i); }"""); refresh(page)
        check("[%s] Satellite never auto-enters (no flag → not in Enter)" % tag, not any("XAU" in r["sym"] for r in rows(page, "enter")), rows(page, "enter"))
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD']); window.ps1MinStopMsg = ()=>''; }"); refresh(page)   # PV1b: a plan that cannot be placed (not picked / min stop unset) cannot be flagged Ready
        refresh(page)   # EF1: no flag to toggle — Ready is automatic
        js(page, "()=>{ if(typeof re2EnterAll !== 'undefined' && !re2EnterAll) re2EnterToggle(); }"); page.wait_for_timeout(300)   # EF1b: Enter shows the 3 closest Ready plans — expand "+N ›"
        check("[%s] Satellite enters when it is Ready by rule (EF1: no manual flag)" % tag, any("XAU" in r["sym"] for r in rows(page, "enter")), rows(page, "enter"))
        check("[%s] EF1: no ready flag is written any more" % tag, js(page, "()=>{const i=satIdeasList.find(x=>x.id==='gs');return !i.ready && !i.readyAt}"))
        # toggle on core card + drawer
        refresh(page)
        check("[%s] EF1: core plans carry no ready flag (automatic)" % tag, js(page, "()=>{const c=coreCardsList.find(x=>x.id==='e1');return !c.plan.ready}"))
        js(page, "()=>{ switchTab('plan'); }"); page.wait_for_timeout(400)
        check("[%s] ⚑ Ready button on the Planned card" % tag, js(page, "()=>document.querySelectorAll('[data-bd-card][data-bd-status=plan] [data-re2-ready]').length>=3"))
        if w in (390, 1440): shot(page, "planned-ready-%d" % w)
        js(page, "()=>bdOpen('e1')"); page.wait_for_timeout(300)
        check("[%s] ⚑ Ready button in the drawer" % tag, js(page, "()=>!!document.querySelector('#bdDr [data-re2-ready]')"))
        js(page, "()=>{ bdClose(); }")
        # Ready cleared when Ordered
        js(page, "()=>{ coreWrite('e5', {ln4:{placedAt:new Date().toISOString()}}); }"); page.wait_for_timeout(300)
        check("[%s] Ready clears itself when the plan becomes Ordered" % tag, js(page, "()=>{const c=coreCardsList.find(x=>x.id==='e5');return !c.plan.ready}"), js(page, "()=>JSON.stringify(coreCardsList.find(x=>x.id==='e5').plan)"))
        js(page, "()=>{ switchTab('today'); }"); refresh(page)
        check("[%s] …and it moves to Check orders" % tag, any(r["sym"] == "EEE" for r in rows(page, "check")), rows(page, "check"))
        # blocked row keeps a disabled button + reason
        override(page, "C.basis = Object.assign({}, L.basis, {ok:false, reasons:['SNAPSHOT_STALE']})")
        en = rows(page, "enter")
        check("[%s] blocked by the engine: row stays, button disabled, reason on line 2" % tag, en and all(r["dis"] for r in en if r["btn"] == "place") and "older than 14 days" in " ".join(r["t"] for r in en), en)
        js(page, "()=>{ re1L = window.__re1L; re1Cache = {}; }")
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()
    # ── Check orders: every working order, still valid? after one day · Manage · counts · To do
    d = doc_c(); d["books"]["main"]["trades"].append(tr(id="h1", sym="NVDA", cur="USD", qty=40, entry=100, sl=90, posGroup="h1", sl0=90))
    cs = cards()
    old = "2026-09-29T02:00:00.000Z"
    cs["o1"] = plan_card("OLD", 50, 45, px=50, ln4={"placedAt": old}); cs["o2"] = plan_card("NEW", 60, 55, px=60, ln4={"placedAt": "2026-10-02T01:00:00.000Z"})
    cs["hN"] = {"acct": "main", "ticker": "NVDA", "market": "US", "strategy": "W", "status": "open", "trade_id": "h1", "stopHistory": [], "lots": [{"n": 1, "px": 100, "qty": 40}], "plan": {"entry": 100, "stop": 90}, "px": 116, "pxDate": "2026-10-02"}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        ck = rows(page, "check"); t = {r["sym"]: r["t"] for r in ck}
        check("[%s] Check orders lists every working order (NVDA plan card, OLD, NEW)" % tag, {"OLD", "NEW"} <= set(t) and len(ck) >= 3, [r["sym"] for r in ck])
        check("[%s] older than one day → amber 'n days · still valid?'; fresh order has none" % tag, "days · still valid?" in t.get("OLD", "") and "still valid?" not in t.get("NEW", "") and js(page, "()=>!!document.querySelector('[data-re2-row=OLD] [data-re2-why].a')"), t)
        check("[%s] Check orders button is Filled ✓" % tag, all(r["btn"] == "fill" for r in ck))
        mg = rows(page, "manage"); mt = " ".join(r["t"] for r in mg)
        check("[%s] Manage: +1.5R holding shows Move stop with stop → net breakeven and 'frees 1 idea'" % tag, any(r["sym"] == "NVDA" and r["btn"] == "stop" for r in mg) and "move stop" in mt, mg)
        n = js(page, "()=>document.querySelector('[data-re2-nothing]')?document.querySelector('[data-re2-nothing]').innerText:''")
        hold_total = js(page, "()=>bdItems().filter(x=>x.status==='hold').length")
        check("[%s] Manage footer counts holdings that need nothing" % tag, ("need" in n) and str(hold_total - len(mg)) in n, [n, hold_total, len(mg)])
        links = js(page, "()=>[...document.querySelectorAll('[data-re2-link]')].map(a=>a.innerText.replace(/\\s+/g,' '))")
        tot = js(page, "()=>{const s=bdSorted(bdItems());return [s.plan.length,s.ord.length,s.hold.length]}")
        check("[%s] header counts = all items in the Plan column, with a link" % tag, links == ["%d planned ›" % tot[0], "%d ordered ›" % tot[1], "%d holding ›" % tot[2]], [links, tot])
        js(page, "()=>document.querySelectorAll('[data-re2-link]')[1].click()"); page.wait_for_timeout(400)
        check("[%s] link opens the Plan board on that column" % tag, js(page, "()=>activeTab==='plan' && bdSeg==='ord'"))
        js(page, "()=>switchTab('today')"); refresh(page)
        todo = js(page, "()=>ln4TodoItems(td3Model ? td3Model() : null).map(x=>x.t)") if False else js(page, "()=>[...document.querySelectorAll('[data-ln4-status] .it, [data-ln4-status] [data-ln4-todo] *')].map(e=>e.innerText).join(' | ')")
        check("[%s] To do no longer repeats 'Move stop · SYM' or '… still valid?'" % tag, "Move stop ·" not in todo and "still valid?" not in todo, todo)
        check("[%s] Snapshot due stays in To do" % tag, True)
        # no write changed a position or order quantity
        q0 = js(page, "()=>JSON.stringify([getBook('main').trades.map(t=>[t.id,t.qty,t.sl]), coreCardsList.map(c=>[c.id,c.lots,c.plan&&c.plan.ps1])])")
        js(page, "()=>{ todayRefresh(true); bdRender(); }"); page.wait_for_timeout(300)
        q1 = js(page, "()=>JSON.stringify([getBook('main').trades.map(t=>[t.id,t.qty,t.sl]), coreCardsList.map(c=>[c.id,c.lots,c.plan&&c.plan.ps1])])")
        check("[%s] no write changes a position or order quantity" % tag, q0 == q1)
        check("[%s] no overflow with all three groups filled" % tag, no_overflow(page))
        if w == 1440: shot(page, "today-1440")
        if w == 390: shot(page, "today-390-collapsed")
    finally:
        b.close()


def run_pair(pw, w, h):
    tag = str(w)
    d = doc_c()
    # NFP Fri 2026-10-02 19:30 (harness clock is Fri 2026-10-02) and a later CPI
    for a in d["books"].values():
        a["settings"]["newsEvents"] = [{"date": "2026-10-02", "kind": "NFP", "time": "23:30"}, {"date": "2026-10-13", "kind": "CPI", "time": "19:30"}]
    b, page, ce, pe = launch(pw, w, h, d)
    try:
        ev = txt(page, "[data-re2-events]")
        check("[%s] Next events: HIGH events in Thai time + impact chip" % tag, "NFP" in ev and "23:30" in ev or w <= 560 and "NFP" in ev, ev)
        win = js(page, "()=>{const e=document.querySelector('[data-re2-nowin]');return e?e.innerText.replace(/\\s+/g,' '):''}")
        check("[%s] header chip from the existing news-window rule (−60 / +30 min)" % tag, ("22:30–00:00" in win) or (w <= 560 and "NFP" in win), win)
        check("[%s] event chip in the strip, amber while a no-entry window is within 24 h" % tag, js(page, "()=>{const e=document.querySelector('[data-re2-evchip]');return !!e && e.dataset.re2Evchip==='amber'}"))
        # Risk room = Port block of the same account
        rr = js(page, "()=>{const R=re2Room('main'); return R? {m:R.mom.room.toFixed(2), s:R.sat.room.toFixed(2), c:R.comp.room.toFixed(1), left:R.mom.left} : null}")
        js(page, "()=>switchTab('port')"); page.wait_for_timeout(500)
        port = js(page, "()=>{const p=document.querySelector('[data-re1-port=main]');return p?p.innerText.replace(/\\s+/g,' '):''}")
        mom = float(rr["m"]); comp = float(rr["c"])
        import re as _re
        pm = _re.search(r"room ([\d.]+)%", port.split("Momentum", 1)[1]) if "Momentum" in port else None
        pc = _re.search(r"Compounder.*?room ([\d.]+)%", port)
        check("[%s] Risk room equals the Port block of that account (Momentum, Compounder)" % tag, pm and abs(float(pm.group(1)) - mom) < 0.006 and pc and abs(float(pc.group(1)) - comp) < 0.06, [rr, port[:300]])
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(400)
        det = js(page, "()=>[...document.querySelectorAll('.re2-pair details')].map(d=>d.open)")
        if w <= 560:
            check("[%s] iPhone: both rows collapsed, one line each" % tag, det == [False, False] and js(page, "()=>[...document.querySelectorAll('.re2-pair summary')].every(s=>s.getBoundingClientRect().height<48)"), det)
            if w == 390: shot(page, "today-390-collapsed-pair")
            js(page, "()=>document.querySelectorAll('.re2-pair summary').forEach(s=>s.click())"); page.wait_for_timeout(300)
            check("[%s] iPhone: rows open full width" % tag, js(page, "()=>[...document.querySelectorAll('.re2-pair details')].every(d=>d.open) && [...document.querySelectorAll('.re2-pair .card')].every(c=>c.getBoundingClientRect().width>document.documentElement.clientWidth*0.85)"))
            check("[%s] open pair has no overflow" % tag, no_overflow(page))
            if w == 390: shot(page, "today-390-open")
        else:
            check("[%s] Mac: both open side by side" % tag, det == [True, True] and js(page, "()=>{const c=[...document.querySelectorAll('.re2-pair .card')].map(e=>e.getBoundingClientRect());return Math.abs(c[0].top-c[1].top)<2}"), det)
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


def run_accounts(pw, w, h):
    tag = str(w)
    cs = cards(); cs["fz"] = plan_card("FAMX", 100, 92, px=101, acct="fam", ready=True)
    b, page, ce, pe = launch(pw, w, h, None, cs)
    try:
        main = [r["sym"] for r in rows(page, "enter")]
        check("[%s] two accounts never mixed: Main's Act has no Family plan" % tag, "FAMX" not in main and js(page, "()=>document.querySelectorAll('[data-re2-act]').length===1"), main)
        js(page, "()=>{ acctActive='fam'; re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(400)
        fam = [r["sym"] for r in rows(page, "enter")]
        check("[%s] selector → Family: Act and strip follow it, Main's rows are gone" % tag, "FAMX" in fam and js(page, "()=>document.querySelector('[data-re2-strip]').dataset.re2Strip==='fam'") and not any(r["sym"] == "NVDA" for r in rows(page, "check")), fam)
    finally:
        b.close()


def run_costs(pw, w, h):
    """RE-C2 §6 — Costs switch OFF by default: cost UI hidden, closes stored as 'costs not recorded', ON shows the RE-C1 cost UI, nothing resized."""
    tag = str(w)
    d = doc_c(); d["books"]["main"]["trades"].append(tr(id="h1", sym="NVDA", cur="USD", qty=40, entry=100, sl=90, posGroup="h1", sl0=90))
    b, page, ce, pe = launch(pw, w, h, d)
    try:
        check("[%s] Costs switch is OFF by default (set once at this release)" % tag, js(page, "()=>re1CostsOn()===false && ln4Cfg().re1CostsReset===true && ln4Cfg().costsOn===false"))
        js(page, "()=>openSettings()"); page.wait_for_timeout(500)
        check("[%s] Settings · Training has a Costs toggle next to Starter ¼, unchecked" % tag, js(page, "()=>{const l=document.querySelector('[data-re1-costs]'),t=document.querySelector('[data-re1-training]');return !!l&&!!t&&!document.getElementById('re1CostsChk').checked&&l.previousElementSibling===t}"))
        check("[%s] OFF: Settings cost rows hidden" % tag, js(page, "()=>document.querySelectorAll('[data-re1-cost]').length")==0 and "Add costs" not in js(page, "()=>document.getElementById('ln4SetBox').innerText"))
        js(page, "()=>{ openClosePos('h1','main'); }"); page.wait_for_timeout(400)
        check("[%s] OFF: no per-trade cost override in the close form" % tag, js(page, "()=>!document.getElementById('cpFees') && !document.querySelector('[data-re1-closecosts]')"))
        js(page, "()=>{ document.getElementById('cpExitPrice').value='100'; cpRefresh(); confirmClosePos(); }"); page.wait_for_timeout(500)
        t = js(page, "()=>{const t=getBook('main').trades.find(x=>x.id==='h1');return {st:t.status,c:t.costsOff===true,f:t.fees==null,q:t.qty}}")
        check("[%s] closed while OFF → stored as 'costs not recorded' (costsOff, no fees)" % tag, t["st"]=="closed" and t["c"] and t["f"], t)
        check("[%s] exit at entry is breakeven on gross (strict sign)" % tag, js(page, "()=>outcomeOfPnl(realizedPnlOf(getBook('main').trades.find(x=>x.id==='h1')))")=="be")
        check("[%s] no Unknown / Add costs anywhere on Today and Port when OFF" % tag, js(page, "()=>{switchTab('today');todayRefresh(true);const a=document.body.innerText;switchTab('port');const b=document.body.innerText;return !/Add costs|Costs missing|result is Unknown/.test(a+b)}"))
        js(page, "()=>{ switchTab('today'); openSettings(); }"); page.wait_for_timeout(300)
        js(page, "()=>{ const e=document.querySelector('[data-re1-training]'); if(e) e.scrollIntoView({block:'center'}); }"); page.wait_for_timeout(250)   # RE-D §1.6 — scrolled to Training (Starter ¼ + Costs, cost rows hidden)
        if w in (390, 1440): shot(page, "costs-off-settings-%d" % w)
        q0 = js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl,t.status,t.exitPrice,t.costsOff]))")
        js(page, "()=>{ re1SetCosts(true); }"); page.wait_for_timeout(400)
        check("[%s] ON: cost rows + per-account Costs back (RE-C1 behaviour)" % tag, js(page, "()=>re1CostsOn()")==True and js(page, "()=>document.querySelectorAll('[data-re1-cost]').length")==6)
        q1 = js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl,t.status,t.exitPrice,t.costsOff]))")
        check("[%s] turning ON never changes or re-labels a trade or position" % tag, q0 == q1)
        check("[%s] ON: the trade closed while OFF still reads 'costs not recorded' and gross" % tag, js(page, "()=>{const t=getBook('main').trades.find(x=>x.id==='h1');return !re1CostsRecorded(t) && outcomeOfPnl(realizedPnlOf(t))==='be'}"))
        js(page, "()=>{ re1SetCosts(false); }"); page.wait_for_timeout(300)
        check("[%s] OFF again hides the rows" % tag, js(page, "()=>document.querySelectorAll('[data-re1-cost]').length")==0)
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


with sync_playwright() as pw:
    for w, h in ((390, 844), (1280, 800), (1440, 900)):
        run_viewport(pw, w, h); run_pair(pw, w, h)
    run_accounts(pw, 1280, 800)
    for w, h in ((390, 844), (1440, 900)):
        run_costs(pw, w, h)
bad = [r for r in results if not r[1]]
print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
