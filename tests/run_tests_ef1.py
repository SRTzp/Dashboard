#!/usr/bin/env python3
"""EF1 — fewer steps from plan to placed order.  Run: python3 tests/run_tests_ef1.py
Screenshots -> tests/screenshots/ef1-*.png (env EF1_SHOTS = other folder)."""
import os, re, sys, copy
from playwright.sync_api import sync_playwright
from pv1_common import *

SHOTS = os.environ.get("EF1_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
SIZES = [(1440, 900), (1280, 800), (390, 844)]
XP_JS = "()=>{ sat7dWrite('satIdeas','xp',{id:'xp',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }"
READY = "()=>{ window.ps1MinStopMsg = ()=>''; re1Cache = {}; }"


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "ef1-%s.png" % name))


def card(page, cid):
    return js(page, "(i)=>{const c=document.querySelector('[data-bd-card=\"'+i+'\"]'); return c? c.innerText.replace(/\\s+/g,' ') : ''}", cid)


def has(page, sel):
    return js(page, "(s)=>!!document.querySelector(s)", sel)


def setup(page, picks="['XAUUSD','BTCUSD','XAGUSD']"):
    js(page, XP_JS); page.wait_for_timeout(600); refresh(page)
    js(page, READY)
    js(page, "()=>{ satWeekPickWrite(wpWeekKey(), %s); switchTab('plan'); bdRender(); }" % picks); page.wait_for_timeout(400)


def place_two_taps(page, cid):
    """card Place › → sheet Confirm. Returns the number of clicks used (both must exist)."""
    n = 0
    sel = "[data-bd-card=%s] [data-bd-pill=place]" % cid
    if not has(page, sel): return -1
    page.click(sel); n += 1; page.wait_for_timeout(350)
    if not has(page, "[data-pb2-yes]"): return -2
    page.click("[data-pb2-yes]"); n += 1; page.wait_for_timeout(450)
    return n


def placed(page, cid):
    return js(page, "(i)=>{const x=satIdeasList.find(y=>y.id===i)||coreCardsList.find(y=>y.id===i); return !!(x && x.ln4 && x.ln4.placedAt)}", cid)


def news_set(page, state):
    """fake clock by moving the CPI event around the real clock (the risk snapshot stays fresh): 'in' = release in 30 min (inside the window) · 'after' = release 3 h ago (window over)."""
    js(page, """(st)=>{ const B=getBook(tdHome()); const ms=Date.now() + (st==='in' ? 30*60000 : -3*3600000);
      const p=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Bangkok',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date(ms)).reduce((o,x)=>{o[x.type]=x.value;return o;},{});
      B.settings.newsEvents=[{date:p.year+'-'+p.month+'-'+p.day,kind:'CPI',time:p.hour+':'+p.minute}]; B.settings.newsSizePct=65; re1Cache={}; bdRender(); }""", state)
    page.wait_for_timeout(300)


def lotof(page, cid, patch=""):
    return js(page, "(i)=>{ const x=Object.assign({}, satIdeasList.find(y=>y.id===i)); %s const c=pb2Calc(x,pb2AcctOf(x)); return {lot:c.lot, label:c.label, news:c.c&&c.c.newsPct, warn:c.c&&c.c.newsWarn, ready:c.c&&c.c.ready}; }" % patch, cid)


def core_planned():
    c = copy.deepcopy(NVDA_CARD); c["ticker"] = "AVGO"; c["id"] = "cP"; c.pop("trade_id", None); c["lots"] = []
    c.pop("track", None); c["status"] = "plan"; c.pop("px", None); c.pop("stopHistory", None); c["ln4"] = {}; c["log"] = []; c["plan"]["ps1"]["bucket"] = "winner"
    c["plan"]["ps1"]["rows"] = [{"px": 158, "riskPct": 0.5, "qty": 2}, {"px": 150, "riskPct": 0.5, "qty": 2}]   # homework not done → first level may be at most 50% of the plan
    c["plan"]["tp"] = 175; c["plan"]["stop"] = 150; c["stop"] = 150
    return c


def run(pw, w, h):
    tag = str(w)
    # ---------- A · carry-over / unpicked / against Macro, B · Ready
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        setup(page)
        t0 = card(page, "xp")
        check("[%s] B a plan with no blocking item is Ready automatically (chip, no ⚑ toggle)" % tag, has(page, "[data-bd-card=xp] [data-ef-ready]") and not has(page, "button.bd-ready") and "⚑" not in t0, t0)
        check("[%s] B manual Ready toggle is gone (re2ReadyToggle removed)" % tag, js(page, "()=>typeof re2ReadyToggle==='undefined'"))
        # a stored flag is ignored (field stays stored, plan without Ready is not Ready)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.ready=true; i.sl=0; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        check("[%s] B stored ready=true is ignored: a plan with a block is not Ready; the field stays stored" % tag, not has(page, "[data-bd-card=xp] [data-ef-ready]") and js(page, "()=>satIdeasList.find(x=>x.id==='xp').ready===true"))
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.ready=null; i.sl=2628; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        # Today › Enter lists Ready plans, drops them when a block appears
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        ent = rows(page, "enter")
        check("[%s] B Today › Enter lists the Ready Satellite plan automatically" % tag, any(r["sym"] and "XAU" in r["sym"] for r in ent), ent)
        if w == 390: shot(page, "today-390")
        js(page, "()=>{ satIdeasList.find(x=>x.id==='xp').sl=0; refresh_ = 1; re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(400)
        ent = rows(page, "enter")
        check("[%s] B Ready disappears when a block appears (no stop) — Enter row gone / not placeable" % tag, not any(("XAU" in r["sym"]) and r["btn"] == "place" and not r["dis"] for r in ent), ent)
        js(page, "()=>{ satIdeasList.find(x=>x.id==='xp').sl=2628; re1Cache={}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        check("[%s] B Ready returns when the block is fixed" % tag, has(page, "[data-bd-card=xp] [data-ef-ready]"))

        # carried plan: placeable with no extra tap
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.week=wpWeekKey(new Date(Date.now()-7*864e5)); re1Cache={}; bdRender(); }"); page.wait_for_timeout(300)
        car = js(page, "()=>satV3IsCarried(satIdeasList.find(x=>x.id==='xp'))")
        t1 = card(page, "xp")
        check("[%s] A carried plan (from last week) is detected, shows Ready + Place ›, no 'Use this week' step" % tag, car and has(page, "[data-bd-card=xp] [data-ef-ready]") and "Use this week" not in t1 and "Carried from last week" not in t1, [car, t1])
        n = place_two_taps(page, "xp")
        check("[%s] A carried plan: card → Place › → Confirm = 2 taps, order recorded" % tag, n == 2 and placed(page, "xp"), n)
        check("[%s] A carried plan re-dated to this week with carried_from kept" % tag, js(page, "()=>{const i=satIdeasList.find(x=>x.id==='xp'); return i.week===wpWeekKey() && Array.isArray(i.carried_from) && i.carried_from.length===1}"))
    finally:
        b.close()

    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        setup(page, "[]")
        check("[%s] A unpicked asset: card is Ready (no 'Not picked this week' block)" % tag, has(page, "[data-bd-card=xp] [data-ef-ready]") and "Not picked" not in card(page, "xp"), card(page, "xp"))
        n = place_two_taps(page, "xp")
        check("[%s] A unpicked asset auto-added to this week's picks by Place (2 taps)" % tag, n == 2 and placed(page, "xp") and js(page, "()=>satIsPicked('XAUUSD')"), n)
    finally:
        b.close()

    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        full = js(page, "()=>satAssets({all:true}).map(a=>a.key).filter(k=>k!=='XAUUSD').slice(0,3)")
        setup(page, str(full))
        check("[%s] A picks full (3): card still Ready" % tag, len(full) == 3 and has(page, "[data-bd-card=xp] [data-ef-ready]"), full)
        page.click("[data-bd-card=xp] [data-bd-pill=place]"); page.wait_for_timeout(350)
        rep = txt(page, "[data-ef-replace]")
        check("[%s] A picks full → the confirm sheet carries one line: Replace <asset> in this week's picks?" % tag, rep.startswith("Replace") and "in this week's picks?" in rep, rep)
        if w == 390: shot(page, "confirm-390")
        check("[%s] A confirm sheet: no overflow" % tag, no_overflow(page))
        page.click("[data-pb2-yes]"); page.wait_for_timeout(450)
        check("[%s] A Confirm replaces the pick and places the order (still 2 taps after opening)" % tag, placed(page, "xp") and js(page, "()=>satIsPicked('XAUUSD') && satWeekPickList().length===3"), js(page, "()=>satWeekPickList()"))
    finally:
        b.close()

    # ---------- A3 against Macro
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        setup(page)
        js(page, "()=>{ const o=satV3F2c; window.__f2=o; satV3F2c=function(i,n){ const r=o(i,n); return Object.assign({}, r, {align:'against', needNote:false}); }; re1Cache={}; bdRender(); }"); page.wait_for_timeout(300)
        t = card(page, "xp")
        check("[%s] A against-Macro plan: amber 'Against Macro' chip, Ready, placeable, no block" % tag, has(page, "[data-bd-card=xp] [data-ef-macro]") and has(page, "[data-bd-card=xp] [data-bd-pill=place]") and "Needs a reason" not in t, t)
        n = place_two_taps(page, "xp")
        check("[%s] A against-Macro plan places in 2 taps (reason field optional)" % tag, n == 2 and placed(page, "xp"), n)
    finally:
        b.close()

    # ---------- B5 verify in the form
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        setup(page)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.ema50_ok=null; i.structure_ok=null; i.mss=null; re1Cache={}; bdRender(); }"); page.wait_for_timeout(300)
        t = card(page, "xp")
        check("[%s] B verify unanswered → 'Needs EMA50 + Structure' (new label) and Complete ›" % tag, "Needs EMA50 + Structure" in t and "needs Trend" not in t, t)
        st = js(page, "()=>td3PlanStatus(satIdeasList.find(x=>x.id==='xp'))")
        check("[%s] B no separate pending step: Today status is 'incomplete', not 'pending'" % tag, st and st["k"] == "incomplete" and st.get("hint") == "Needs EMA50 + Structure", st)
        js(page, "()=>pb2OpenEdit('xp')"); page.wait_for_timeout(350)
        check("[%s] B EMA50 + Structure are answered inside the plan form (existing controls)" % tag, has(page, "[data-pb2-tg=ema]") and has(page, "[data-pb2-tg=str]"))
        js(page, "()=>bdPopClose()")
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.ema50_ok=true; i.structure_ok=false; i.mss=null; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        m1 = js(page, "()=>pb2Model(satIdeasList.find(x=>x.id==='xp')).text")
        check("[%s] B MSS asked only when Structure = No — label 'Needs MSS (Structure = No)'" % tag, m1 == "Needs MSS (Structure = No)", m1)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.mss=true; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        l2 = lotof(page, "xp")
        check("[%s] B Structure = No + MSS = Yes → allowed at reduced size (Counter trend @ MSS 65%%)" % tag, "Counter trend" in l2["label"] and l2["lot"], l2)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.mss=false; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        check("[%s] B MSS = No → still blocks" % tag, js(page, "()=>ln4VerifyOf(satIdeasList.find(x=>x.id==='xp')).blocked===true") and not has(page, "[data-bd-card=xp] [data-bd-pill=place]"), card(page, "xp"))
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.mss=null; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        check("[%s] B MSS blank → still blocks / incomplete" % tag, not has(page, "[data-bd-card=xp] [data-bd-pill=place]"))
    finally:
        b.close()

    # ---------- B6 news window
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        setup(page)
        news_set(page, "after")
        full = lotof(page, "xp")
        news_set(page, "in")
        win = lotof(page, "xp")
        line = js(page, "()=>newsWarnLine()")
        until = js(page, "()=>newsSatBlock().to")
        check("[%s] B inside the window the plan stays placeable at 65%% (policy newsSizePct)" % tag, win["lot"] and full["lot"] and 0.55 <= win["lot"] / full["lot"] <= 0.70 and win["news"] == 65 and win["ready"] is True, [win, full])
        check("[%s] B amber line on the card: 'News window until %s ICT · size 65%%'" % (tag, until), line == "News window until %s ICT · size 65%%" % until and txt(page, "[data-bd-card=xp] [data-ef-news]") == line, [line, txt(page, "[data-bd-card=xp] [data-ef-news]")])
        check("[%s] B card is not blocked in the window (Place › present)" % tag, has(page, "[data-bd-card=xp] [data-bd-pill=place]") and not has(page, "[data-bd-card=xp] [data-pv-blocked]"))
        if w == 1440: shot(page, "news-window-1440")
        page.click("[data-bd-card=xp] [data-bd-pill=place]"); page.wait_for_timeout(350)
        check("[%s] B the confirm sheet shows the same amber line" % tag, txt(page, "[data-pb2-step=place] [data-ef-news]") == line, txt(page, "[data-pb2-step=place]"))
        js(page, "()=>bdPopClose()")
        # min(), not multiplied: Unclear Trend (65%) + news → 65%
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.structure_ok=false; i.mss=true; re1Cache={}; }")
        inn = lotof(page, "xp"); news_set(page, "after"); aft = lotof(page, "xp")
        check("[%s] B min(): Counter trend 65%% + news 65%% = 65%% (not 42%%): lot inside window == lot after window" % tag, inn["lot"] and aft["lot"] and abs(inn["lot"] - aft["lot"]) < 1e-9, [inn, aft])
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp'); i.structure_ok=true; i.mss=null; re1Cache={}; }")
        news_set(page, "after")
        aft2 = lotof(page, "xp")
        check("[%s] B after the window full size returns with no tap and no amber line" % tag, aft2["lot"] and abs(aft2["lot"] - full["lot"]) < 1e-9 and not has(page, "[data-bd-card=xp] [data-ef-news]") and js(page, "()=>newsWarnLine()") == "", aft2)
        # placing inside the window works
        news_set(page, "in")
        n = place_two_taps(page, "xp")
        check("[%s] B a plan placed inside the news window records the order (2 taps)" % tag, n == 2 and placed(page, "xp"), n)
    finally:
        b.close()

    # ---------- C · Momentum / Compounder: same confirm sheet, unaffected by news, 2 taps
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": core_planned()})
    try:
        setup(page); js(page, "()=>{ window.ftHwDone = ()=>true; window.wl1HwDone = ()=>true; re1Cache={}; bdRender(); }")   # homework done → full Momentum size (the 50% homework cap is covered by its own suites)
        news_set(page, "in")
        pill = has(page, "[data-bd-card=cP] [data-bd-pill=place]")
        t = card(page, "cP")
        check("[%s] C Momentum plan card has Place › and no news line / chip (news is Satellite only)" % tag, pill and not has(page, "[data-bd-card=cP] [data-ef-news]"), t)
        g_in = js(page, "()=>{const c=coreCardsList.find(x=>x.id==='cP'); const g=re1PlanGate(c,0); return {ok:g.ok, qty:g.model&&g.model.qty, f:g.model&&g.model.formula}}")
        news_set(page, "after")
        g_af = js(page, "()=>{const c=coreCardsList.find(x=>x.id==='cP'); const g=re1PlanGate(c,0); return {ok:g.ok, qty:g.model&&g.model.qty, f:g.model&&g.model.formula}}")
        check("[%s] C Momentum / Compounder size identical inside and outside the news window (no news / trend cut)" % tag, g_in == g_af, [g_in, g_af])
        if pill:
            page.click("[data-bd-card=cP] [data-bd-pill=place]"); page.wait_for_timeout(350)
            sh = txt(page, "[data-ef-core-place]")
            check("[%s] C Place › opens the confirm sheet directly (no native confirm), with legs · stop · Risk · Reward" % tag, "Buy" in sh and "Stop" in sh and "Risk" in sh and "Reward" in sh and "Confirm" in sh, sh)
            check("[%s] C core confirm sheet: size working under More, no overflow" % tag, has(page, "[data-ef-core-place] [data-ef-more]") and no_overflow(page))
            page.click("[data-pb2-yes]"); page.wait_for_timeout(450)
            check("[%s] C card → Place › → Confirm = 2 taps; order recorded" % tag, placed(page, "cP"))
    finally:
        b.close()

    # ---------- money-protecting blocks stay
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        setup(page)
        js(page, "()=>{ window.__msm = ps1MinStopMsg; }")
        js(page, "()=>{ satIdeasList.find(x=>x.id==='xp').sl=0; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        check("[%s] G stop missing → no Place ›" % tag, not has(page, "[data-bd-card=xp] [data-bd-pill=place]"), card(page, "xp"))
        js(page, "()=>{ satIdeasList.find(x=>x.id==='xp').sl=2628; window.ps1MinStopMsg=()=>'Stop below the minimum stop (test)'; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        check("[%s] G stop below the minimum → blocked, Open Settings ›" % tag, has(page, "[data-bd-card=xp] [data-pv-blocked]") and not has(page, "[data-bd-card=xp] [data-bd-pill=place]"), card(page, "xp"))
        js(page, "()=>{ window.ps1MinStopMsg=()=>''; satIdeasList.find(x=>x.id==='xp').sl=2642; re1Cache={}; bdRender(); }"); page.wait_for_timeout(250)
        check("[%s] G wrong-side / zero-distance stop → no Place ›" % tag, not has(page, "[data-bd-card=xp] [data-bd-pill=place]"))
        js(page, "()=>{ satIdeasList.find(x=>x.id==='xp').sl=2628; re1Cache={}; const o=re1L; window.__l=o; re1L=function(a){ const L=o(a); if(L) L.eF=0; return L; }; bdRender(); }"); page.wait_for_timeout(300)
        check("[%s] G emergency brake 0%% → the plan cannot be placed" % tag, not has(page, "[data-bd-card=xp] [data-bd-pill=place]"), card(page, "xp"))
        js(page, "()=>{ re1L=window.__l; re1Cache={}; bdRender(); }")
        # size block on a core plan: qty far above today's allowed size
        c = core_planned(); c["plan"]["ps1"]["rows"] = [{"px": 158, "riskPct": 0.5, "qty": 100000}]
    finally:
        b.close()
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": c})
    try:
        setup(page)
        g = js(page, "()=>{const c=coreCardsList.find(x=>x.id==='cP'); const g=re1PlanGate(c,0); return {ok:g.ok, msg:g.msg}}")
        check("[%s] G size above today's allowed (risk / total risk / value cap room) → engine gate still blocks" % tag, g["ok"] is False and not has(page, "[data-bd-card=cP] [data-bd-pill=place]"), g)
        # board row counts
        js(page, "()=>{ switchTab('plan'); bdRender(); window.scrollTo(0,0); }"); page.wait_for_timeout(300)
        rc = js(page, "()=>({cards:document.querySelectorAll('[data-bd-card]').length, h:document.documentElement.scrollHeight})")
        print("INFO [%s] Plan board: %s cards · page height %s" % (tag, rc["cards"], rc["h"]))
        js(page, "()=>{ switchTab('today'); todayRefresh(true); window.scrollTo(0,0); }"); page.wait_for_timeout(400)
        rt = js(page, "()=>({rows:document.querySelectorAll('[data-re2-row]').length, h:document.documentElement.scrollHeight})")
        print("INFO [%s] Today: %s rows · page height %s" % (tag, rt["rows"], rt["h"]))
        check("[%s] no overflow on Today / Plan board" % tag, no_overflow(page))
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()
    # card screenshot
    if w in (1440,):
        b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
        try:
            setup(page); js(page, "()=>{ switchTab('plan'); bdRender(); window.scrollTo(0,0); }"); page.wait_for_timeout(300); shot(page, "card-ready-1440")
        finally:
            b.close()


with sync_playwright() as pw:
    for w, h in SIZES:
        run(pw, w, h)
fails = [r for r in results if not r[1]]
print("\n%d checks pass · %d fail" % (len(results) - len(fails), len(fails)))
sys.exit(1 if fails else 0)
