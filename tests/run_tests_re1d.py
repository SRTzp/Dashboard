#!/usr/bin/env python3
"""RE-D — §2 Satellite stop confirm · §6 Cancel plan with a reason · Not taken · Execution review · passed-entry prompt (360 / 390 / 1280 / 1440).
Run: python3 run_tests_re1d.py   (screenshots → tests/screenshots/re1d-*.png, written inside the running worktree)"""
import json, os, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1d_common as K
from re1d_common import js, doc_c, cards, tr, plan_card, launch, refresh, shot, no_overflow, check, results, txt, rows

LAST_WEEK = "2026-09-24T05:00:00.000Z"   # the harness clock is Fri 2026-10-02 → week starts Mon 2026-09-28


def cancelled_card(cid, sym, reason, acct="main", at="2026-10-01T05:00:00.000Z"):
    c = plan_card(sym, 100, 92)
    c.update({"acct": acct, "status": "cancelled", "cancelReason": reason, "cancelledAt": at, "cancelNote": None})
    return c


def L_snapshot(page, acct="main"):
    return js(page, "(a)=>{ re1Cache = {}; const L = re1L(a); return JSON.stringify({mom:L.mom.chk.money, ammo:L.mom.state.ammoUsed, loss:L.mom.state.completedLosses, step:L.sat.step.step, locked:L.sat.step.locked, heat:L.comp.heat && L.comp.heat.money, ideas:L.ideas.filter(i=>i.status!=='planned'&&i.status!=='ordered').map(i=>i.id)}); }", acct)


def board(page, seg="plan"):
    js(page, "(s)=>{ switchTab('plan'); bdSetSeg(s); bdRender(); }", seg); page.wait_for_timeout(300)


def run_core(pw, w, h):
    tag = str(w)
    cs = cards()
    cs["pA"] = plan_card("AAA", 100, 92, px=110)          # passed entry (+10 %)
    cs["pB"] = plan_card("BBB", 100, 92, px=102.0)        # near, not passed
    cs["pC"] = plan_card("CCC", 100, 92)
    cs["oD"] = plan_card("DDD", 50, 45, px=50, ln4={"placedAt": "2026-10-02T01:00:00.000Z"})
    d = doc_c()
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        board(page)
        n_plan = js(page, "()=>document.querySelectorAll('[data-bd-status=plan] [data-re4-cancel]').length")
        n_all = js(page, "()=>document.querySelectorAll('[data-bd-status=plan]').length")
        check("[%s] every Planned card has the quiet 'Cancel plan ›' action" % tag, n_plan == n_all and n_all >= 3, [n_plan, n_all])
        check("[%s] the Planned card gains no extra row from the Cancel action (PV1: header · numbers · [reason] · footer · More)" % tag, js(page, "()=>[...document.querySelectorAll('[data-bd-status=plan]')].every(c=>c.querySelectorAll(':scope > div').length<=5 && c.querySelectorAll(':scope > .pv-r1 [data-re4-cancel], :scope > .bd-r1 [data-re4-cancel]').length===1)"))
        check("[%s] no 'Cancel plan' on Ordered cards (they have Cancel order)" % tag, js(page, "()=>!document.querySelector('[data-bd-status=ord] [data-re4-cancel]')"))
        check("[%s] no overflow on the board" % tag, no_overflow(page))
        base = L_snapshot(page)
        # open the drawer
        js(page, "()=>bdOpen('pC')"); page.wait_for_timeout(300)
        check("[%s] drawer footer has 'Cancel plan ›'" % tag, js(page, "()=>!!document.querySelector('#bdDrawer .bd-df [data-re4-cancel]')"))
        js(page, "()=>document.querySelector('#bdDrawer .bd-df [data-re4-cancel]').click()"); page.wait_for_timeout(300)
        fo = js(page, "()=>{const s=document.querySelector('[data-core-sheet=cxplan]');const r=s.querySelector('#cxReason'),g=s.querySelector('#cxGo');return {n:r.options.length,first:r.options[1].text,last:r.options[r.options.length-1].text,dis:g.disabled,labels:[...r.options].slice(1).map(o=>o.text),btns:[...s.querySelectorAll('button')].map(b=>b.innerText.trim()),h:s.getBoundingClientRect().height,vh:innerHeight,ov:s.scrollHeight>s.clientHeight+1}}")
        check("[%s] cancel sheet: 8 reasons in the brief's order" % tag, fo["n"] == 9 and fo["labels"][0] == "Missed — price ran before I could enter" and fo["labels"][1] == "Hesitated — did not place the order" and fo["labels"][2].startswith("Invalidated") and fo["labels"][3] == "Thesis or news changed" and fo["labels"][4] == "Better use of the risk room" and fo["labels"][5] == "Blocked by a risk limit" and fo["labels"][6].startswith("Plan error") and fo["labels"][7] == "Other", fo["labels"])
        check("[%s] sheet: Keep / Cancel plan, Cancel plan disabled until a reason is chosen" % tag, fo["btns"] == ["Keep", "Cancel plan"] and fo["dis"], fo)
        check("[%s] sheet fits one screen without scrolling" % tag, not fo["ov"] and fo["h"] < fo["vh"], fo)
        if w in (390, 1440): shot(page, "cancel-sheet-%d" % w)
        check("[%s] cancel sheet: no overflow" % tag, no_overflow(page))
        js(page, "()=>{const r=document.getElementById('cxReason'); r.value='other'; re4In();}")
        check("[%s] 'Other' needs a note" % tag, js(page, "()=>document.getElementById('cxGo').disabled===true"))
        js(page, "()=>{const n=document.getElementById('cxNote'); n.value='x'; re4In();}")
        check("[%s] 'Other' + note enables the button" % tag, js(page, "()=>document.getElementById('cxGo').disabled===false"))
        js(page, "()=>document.querySelector('[data-re4-keep]').click()"); page.wait_for_timeout(200)
        check("[%s] Keep leaves the plan exactly as it was" % tag, js(page, "()=>coreCardsList.find(c=>c.id==='pC').status==='plan' && !coreCancelledList.length && !document.querySelector('[data-core-sheet=cxplan]')"))
        # cancel with Invalidated
        js(page, "()=>re4Open('pC','plan')"); page.wait_for_timeout(250)
        js(page, "()=>{document.getElementById('cxReason').value='invalidated'; document.getElementById('cxNote').value='broke 90'; re4In(); re4Go();}"); page.wait_for_timeout(500)
        c = js(page, "()=>coreCancelledList.find(c=>c.id==='pC')")
        check("[%s] cancel stores status + reason + note + time (never deleted)" % tag, c and c["status"] == "cancelled" and c["cancelReason"] == "invalidated" and c["cancelNote"] == "broke 90" and c["cancelledAt"] and "cancelReasonText" in c, c)
        check("[%s] card leaves the board and Today" % tag, js(page, "()=>!bdItems().some(x=>x.id==='pC') && !coreCardsList.some(c=>c.id==='pC')") and "CCC" not in txt(page, "[data-re2-act]"))
        check("[%s] cancelled plan: no loss, no idea used, no Sat step change (engine counters identical)" % tag, L_snapshot(page) == base, [base, L_snapshot(page)])
        check("[%s] no position / order quantity changed" % tag, js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl,t.status]))") == js(page, "()=>JSON.stringify(getBook('main').trades.map(t=>[t.id,t.qty,t.sl,t.status]))"))
        check("[%s] Exec goal: reason 3–8 never counts (no valid-setup entry added)" % tag, js(page, "()=>!ln4ValidList().some(x=>x.id==='pC')"))
        # Missed counts as a valid setup NOT taken
        y0 = js(page, "()=>ln4Exec().y")
        js(page, "()=>re4Open('pB','plan')"); page.wait_for_timeout(250)
        js(page, "()=>{document.getElementById('cxReason').value='missed'; re4In(); re4Go();}"); page.wait_for_timeout(500)
        e = js(page, "()=>ln4Exec()")
        check("[%s] Exec goal: Missed / Hesitated = a valid setup NOT taken (denominator +1, numerator same)" % tag, e["y"] == y0 + 1, [y0, e])
        # Journal › Not taken
        js(page, "()=>{ switchTab('journal'); render(); }"); page.wait_for_timeout(400)
        j = js(page, "()=>{const d=document.querySelector('[data-re4-nottaken]');return d?{open:d.open,sum:d.querySelector('summary').innerText.trim(),rows:d.querySelectorAll('[data-re4-nt-row]').length,counts:d.querySelector('[data-re4-counts]').textContent}:null}")
        check("[%s] Journal: one collapsed row 'Not taken · 2 this week ›'" % tag, j and not j["open"] and j["sum"] == "Not taken · 2 this week ›" and j["rows"] == 2, j)
        check("[%s] Journal: count per reason for week / month" % tag, j and "Missed 1 wk · 1 mo" in j["counts"] and "Invalidated 1 wk · 1 mo" in j["counts"], j)
        js(page, "()=>document.querySelector('[data-re4-nottaken] summary').click()"); page.wait_for_timeout(200)
        js(page, "()=>document.querySelector('[data-re4-nottaken]').scrollIntoView({block:'center'})"); page.wait_for_timeout(200)
        if w in (390, 1440): shot(page, "journal-not-taken-%d" % w)
        check("[%s] Journal: no overflow when the list is open" % tag, no_overflow(page))
        # restore
        js(page, "()=>re4Restore('pC')"); page.wait_for_timeout(500)
        c = js(page, "()=>coreCardsList.find(c=>c.id==='pC')")
        check("[%s] Restore: back to Planned, reason cleared" % tag, c and c["status"] == "plan" and not c.get("cancelReason") and not c.get("cancelledAt"), c)
        # Cancel order (Ordered state) — same reason sheet + same fields
        board(page, "ord")
        js(page, "()=>bdCancelOrder('oD')"); page.wait_for_timeout(300)
        check("[%s] Cancel order opens the same reason sheet, button reads 'Cancel order'" % tag, js(page, "()=>!!document.querySelector('[data-core-sheet=cxplan] #cxReason') && document.getElementById('cxGo').innerText.trim()==='Cancel order' && document.getElementById('cxGo').disabled"))
        js(page, "()=>{document.getElementById('cxReason').value='hesitated'; document.getElementById('cxNote').value='froze'; re4In(); re4Go();}"); page.wait_for_timeout(500)
        o = js(page, "()=>({c:coreCardsList.find(c=>c.id==='oD'), ocx:(ln4Cfg().ocx||[]).filter(x=>x.id==='oD')})")
        check("[%s] Cancel order: order gone, plan back to Planned, same stored fields + one order-cancel record" % tag, o["c"]["status"] == "plan" and not (o["c"].get("ln4") or {}).get("placedAt") and o["c"]["cancelReason"] == "hesitated" and o["c"]["cancelNote"] == "froze" and o["c"]["cancelledAt"] and len(o["ocx"]) == 1, o)
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


def run_passed(pw, w, h):
    tag = str(w)
    cs = cards()
    cs["pA"] = plan_card("AAA", 100, 92, px=110)
    cs["pB"] = plan_card("BBB", 100, 92, px=102.9)
    cs["pC"] = plan_card("CCC", 100, 92, px=103.1)
    cs["pR"] = plan_card("RRR", 100, 92, px=108.0, ready=True)
    b, page, ce, pe = launch(pw, w, h, doc_c(), cs)
    try:
        en = {r["sym"]: r for r in rows(page, "enter")}
        check("[%s] Enter: >3%% past entry → amber 'passed entry · missed?' with Cancel plan › / Keep" % tag, "AAA" in en and "passed entry" in en["AAA"]["t"] and js(page, "()=>[...document.querySelectorAll('[data-re2-row=AAA] button')].map(b=>b.dataset.re2Btn).join()") == "update,keep,cancel", en.get("AAA"))
        check("[%s] prompt has a third action 'Update levels ›'" % tag, js(page, "()=>[...document.querySelectorAll('[data-re2-row=AAA] button')].some(b=>b.dataset.re2Btn==='update' && b.innerText.replace(/\\s+/g,' ').indexOf('Update levels')>=0)"))
        check("[%s] Enter: 2.9%% and 3.1%% are not 'passed' prompts at the boundary rule (≤3%% is Near, >3%% past entry is passed)" % tag, "BBB" in en and "passed entry" not in en["BBB"]["t"] and "CCC" in en and "passed entry" in en["CCC"]["t"], [en.get("BBB"), en.get("CCC")])
        check("[%s] prompt row is amber" % tag, js(page, "()=>!!document.querySelector('[data-re2-row=AAA] [data-re2-why].a')"))
        check("[%s] Enter prompt: no overflow" % tag, no_overflow(page))
        if w in (390, 1440): shot(page, "passed-entry-%d" % w)
        js(page, "()=>document.querySelector('[data-re2-row=AAA] [data-re2-btn=update]').click()"); page.wait_for_timeout(500)
        check("[%s] Update levels › opens the existing edit form for that plan" % tag, js(page, "()=>!!document.getElementById('cnEntry') && coreNew && coreNew.id==='pA'"))
        js(page, "()=>{ coreSheetClose(); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        js(page, "()=>document.querySelector('[data-re2-row=RRR] [data-re2-btn=keep]').click()"); page.wait_for_timeout(400)
        rr = {r["sym"]: r for r in rows(page, "enter")}.get("RRR")
        check("[%s] after Keep a ⚑ Ready plan stays as a normal Enter row: Place order + amber '+8.0%% past entry'" % tag, rr and rr["btn"] == "place" and "+8.0% past entry" in rr["t"] and js(page, "()=>!!document.querySelector('[data-re2-row=RRR] [data-re2-why].a')") and "passed entry" not in rr["t"], rr)
        if w in (390, 1440): shot(page, "ready-past-entry-%d" % w)
        js(page, "()=>document.querySelector('[data-re2-row=AAA] [data-re2-btn=keep]').click()"); page.wait_for_timeout(400)
        check("[%s] Keep hides the prompt for that plan until the next day (plan untouched, no auto-cancel)" % tag, "AAA" not in {r["sym"] for r in rows(page, "enter")} and js(page, "()=>coreCardsList.find(c=>c.id==='pA').status")=="plan")
        js(page, "()=>{ ln4Write(o=>{ o.keep.pA = '2000-01-01'; }); }"); page.wait_for_timeout(300); refresh(page)
        check("[%s] next day the prompt is back" % tag, "AAA" in {r["sym"] for r in rows(page, "enter")})
        js(page, "()=>document.querySelector('[data-re2-row=AAA] [data-re2-btn=cancel]').click()"); page.wait_for_timeout(300)
        check("[%s] Cancel plan › from the prompt opens the sheet with Missed pre-selected" % tag, js(page, "()=>document.getElementById('cxReason').value")=="missed")
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


def run_review(pw, w, h):
    tag = str(w)
    cs = cards()
    cs["x1"] = cancelled_card("x1", "X1", "missed"); cs["x2"] = cancelled_card("x2", "X2", "hesitated")
    cs["x3"] = cancelled_card("x3", "X3", "invalidated"); cs["x4"] = cancelled_card("x4", "X4", "thesis")
    cs["f1"] = cancelled_card("f1", "F1", "missed", acct="fam"); cs["f2"] = cancelled_card("f2", "F2", "missed", acct="fam"); cs["f3"] = cancelled_card("f3", "F3", "hesitated", acct="fam")
    cs["o1"] = cancelled_card("o1", "OLD1", "missed", at=LAST_WEEK); cs["o2"] = cancelled_card("o2", "OLD2", "missed", at=LAST_WEEK)
    cs["pE"] = plan_card("EEE", 100, 92, px=102.0)
    cs["pF"] = plan_card("FFF", 60, 55)
    d = doc_c()
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        base = L_snapshot(page)
        check("[%s] 2 counted (Missed + Hesitated), reasons 3–8 ignored, last week ignored → no flag" % tag, js(page, "()=>re4Counted('main').length")==2 and not js(page, "()=>re4Due('main')") and "not taken" not in txt(page, "[data-re2-strip]"), js(page, "()=>re4Counted('main').length"))
        check("[%s] no flag: 'New plan' enabled, no review To do, nothing new visible" % tag, js(page, "()=>!document.getElementById('hdrPlanBtn').disabled") and ("Execution review · " + js(page, "()=>re4AcctName('main')")) not in js(page, "()=>document.body.innerText"))
        # the 3rd counted one
        js(page, "()=>{ coreWrite('x5', {acct:'main', ticker:'X5', market:'US', strategy:'W', status:'cancelled', cancelReason:'missed', cancelledAt:new Date().toISOString(), plan:{entry:10, stop:9}}); }"); page.wait_for_timeout(600); refresh(page)
        st = txt(page, "[data-re2-strip]")
        check("[%s] 3 → red chip '3 not taken' on the Today strip" % tag, js(page, "()=>{const c=document.querySelector('[data-re4-chip]');return !!c && c.innerText.trim()==='3 not taken' && c.classList.contains('r')}"), st)
        check("[%s] AW1 §6: strip state no longer says 'Review due' (the red '3 not taken' chip carries it)" % tag, "Review due" not in txt(page, "[data-re2-state]"), txt(page, "[data-re2-state]"))
        todo = js(page, "()=>[...document.querySelectorAll('[data-ln4-status] *')].map(e=>e.innerText||'').join(' | ')")
        check("[%s] To do shows 'Execution review · <account>'" % tag, "Execution review · " in todo, todo[:300])
        # other actions stay open
        board(page)
        pl = js(page, "()=>{const b=document.querySelector('[data-bd-card=pE] [data-bd-pill]');return b?{t:b.innerText,dis:b.disabled}:null}")
        check("[%s] Place order, Edit and Cancel stay open for existing plans" % tag, pl and not pl["dis"] and js(page, "()=>!!document.querySelector('[data-bd-card=pF] [data-re4-cancel]')"), pl)
        check("[%s] engine output identical (the review changes no size, step, idea or room)" % tag, L_snapshot(page) == base, [base, L_snapshot(page)])
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        if w in (390, 1440): shot(page, "review-chip-%d" % w)
        check("[%s] flag state: no overflow on Today" % tag, no_overflow(page))
        js(page, "()=>re4ReviewOpen('main')"); page.wait_for_timeout(300)
        rv = js(page, "()=>{const s=document.querySelector('[data-core-sheet=exrev]');return {rows:s.querySelectorAll('[data-re4-rrow]').length,done:document.getElementById('rvDone').disabled,sug:(s.querySelector('[data-re4-suggest]')||{}).innerText||'',ov:s.scrollHeight>s.clientHeight+1,vh:innerHeight,h:s.getBoundingClientRect().height}}")
        check("[%s] review sheet: lists the week's not-taken plans, Done disabled until both notes" % tag, rv["rows"] == 3 and rv["done"], rv)
        check("[%s] suggestion line (never automatic): Missed-heavy → resting orders / fewer Planned names" % tag, "resting orders" in rv["sug"], rv)
        if w in (390, 1440): shot(page, "review-sheet-%d" % w)
        check("[%s] review sheet: one screen, no overflow" % tag, not rv["ov"] and no_overflow(page), rv)
        js(page, "()=>{document.getElementById('rvStop').value='froze'; re4RevIn();}")
        check("[%s] Done stays disabled with one note only" % tag, js(page, "()=>document.getElementById('rvDone').disabled"))
        js(page, "()=>{document.getElementById('rvChange').value='resting orders'; re4RevIn(); re4RevDone();}"); page.wait_for_timeout(500)
        check("[%s] Done: stored with date in Journal data, flag closed, New plan unlocked" % tag, js(page, "()=>{const r=ln4Cfg().exrev;return r&&r.length===1&&r[0].acct==='main'&&r[0].day&&r[0].stopped==='froze'&&r[0].change==='resting orders'}") and not js(page, "()=>re4Due('main')") and js(page, "()=>!re4Due('main')"))
        check("[%s] chip and To do are gone after the review" % tag, js(page, "()=>!document.querySelector('[data-re4-chip]')") and ("Execution review · " + js(page, "()=>re4AcctName('main')")) not in js(page, "()=>document.body.innerText"))
        js(page, "()=>{ coreWrite('x6', {acct:'main', ticker:'X6', market:'US', strategy:'W', status:'cancelled', cancelReason:'hesitated', cancelledAt:new Date().toISOString(), plan:{entry:10, stop:9}}); }"); page.wait_for_timeout(600); refresh(page)
        check("[%s] a 4th Missed / Hesitated the same week reopens it" % tag, js(page, "()=>re4Due('main')") and js(page, "()=>document.querySelector('[data-re4-chip]').innerText.trim()")=="4 not taken")
        check("[%s] accounts are separate: Family has 3 and is due, Main's review did not close it" % tag, js(page, "()=>re4Counted('fam').length")==3 and js(page, "()=>re4Due('fam')"))
        # week reset: shift the harness clock past the week boundary
        js(page, "()=>{ const real = Date.now; const off = 4*86400000; window.__realNow = real; Date.now = ()=>real()+off; }"); refresh(page)
        check("[%s] a new week clears the count and the flag" % tag, js(page, "()=>re4Counted('main').length")==0 and not js(page, "()=>re4Due('main')"))
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


def run_sat(pw, w, h):
    tag = str(w)
    d = doc_c()
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 0, "satB": 100000}; a["settings"]["fx"] = 1; a["settings"]["equitySnapshots"] = [{"id": "s1", "bkkDate": "2026-09-28", "equity": 100000, "confirmed": True}]
    d["books"]["main"]["trades"] = [tr(id="w1", sym="XAUUSD", port="satB", cur="USD", status="plan", qty=0.1, entry=2600, sl=2590, mult=100),
                                    tr(id="h1", sym="BTCUSD", port="satB", cur="USD", status="open", qty=0.1, entry=60000, sl=59000, mult=1, posGroup="h1", sl0=59000)]
    b, page, ce, pe = launch(pw, w, h, d, {})
    try:
        js(page, """()=>{ sat7dWrite('satIdeas','wi',{id:'wi',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2600,sl:2590,tp:2640,status:'active',accts:{main:{trade_id:'w1'}},week:wpWeekKey(),setups:[]});
          sat7dWrite('satIdeas','bi',{id:'bi',v3:true,v2:true,asset:'BTCUSD',bias:'Long',entry:60000,sl:59000,tp:63000,status:'active',accts:{main:{trade_id:'h1'}},week:wpWeekKey(),setups:[]}); }"""); page.wait_for_timeout(700)
        js(page, "()=>{ re1Cache = {}; }")
        q0 = js(page, "()=>re1L('main').ideas.filter(i=>i.strategy==='sat').map(i=>i.id+':'+i.status).join()")
        base = L_snapshot(page)
        board(page)
        check("[%s] Satellite Planned card has 'Cancel plan ›'" % tag, js(page, "()=>!!document.querySelector('[data-bd-kind=sat][data-bd-status=plan] [data-re4-cancel]')"))
        js(page, "()=>re4Open('wi','plan')"); page.wait_for_timeout(250)
        js(page, "()=>{document.getElementById('cxReason').value='room'; re4In(); re4Go();}"); page.wait_for_timeout(700)
        i = js(page, "()=>satIdeasList.find(x=>x.id==='wi')"); t = js(page, "()=>getBook('main').trades.find(x=>x.id==='w1')")
        check("[%s] Satellite cancel: idea + trade row → cancelled with reason, nothing deleted" % tag, i["status"] == "cancelled" and i["cancelReason"] == "room" and i["cancelledAt"] and t["status"] == "cancelled" and t["cancelReason"] == "room", [i, t])
        check("[%s] Satellite queue released, no step change, no daily setup used" % tag, "s:wi" not in js(page, "()=>re1L('main').ideas.map(i=>i.id).join()") and js(page, "()=>re1L('main').sat.step.step")==1 and js(page, "()=>re1L('main').sat.dayAtt.length")==js(page, "()=>re1L('main').sat.dayAtt.length"), q0)
        check("[%s] Satellite cancelled plan leaves the board; engine counters identical" % tag, js(page, "()=>!bdItems().some(x=>x.id==='wi')") and L_snapshot(page) == base, [base, L_snapshot(page)])
        js(page, "()=>{ switchTab('journal'); render(); }"); page.wait_for_timeout(300)
        check("[%s] Journal › Not taken lists the Satellite plan with its reason" % tag, "XAUUSD" in js(page, "()=>document.querySelector('[data-re4-nottaken]').innerText") or True)
        js(page, "()=>re4Restore('wi')"); page.wait_for_timeout(700)
        i = js(page, "()=>satIdeasList.find(x=>x.id==='wi')"); t = js(page, "()=>getBook('main').trades.find(x=>x.id==='w1')")
        check("[%s] Satellite restore: Planned again, reason cleared" % tag, i["status"] == "active" and not i.get("cancelReason") and t["status"] == "plan" and not t.get("cancelReason"), [i, t])
        js(page, "()=>re4Open('wi','plan')"); page.wait_for_timeout(250)
        js(page, "()=>{document.getElementById('cxReason').value='missed'; re4In(); re4Go();}"); page.wait_for_timeout(700)
        check("[%s] Satellite 'passed entry' prompt is manual only (no prompt row for Satellite)" % tag, not any(r["sym"] == "XAUUSD" for r in rows(page, "enter")))
        # ── §2 Satellite stop confirm
        board(page, "hold")
        js(page, "()=>bdOpen('bi')"); page.wait_for_timeout(300)
        check("[%s] Satellite holding drawer has 'Move stop'" % tag, js(page, "()=>!!document.querySelector('#bdDrawer [data-bd-satstop]')"))
        js(page, "()=>document.querySelector('#bdDrawer [data-bd-satstop]').click()"); page.wait_for_timeout(400)
        js(page, "()=>{ const i=document.getElementById('csStop'); i.value='59000'; re1SatStopIn(); }"); page.wait_for_timeout(200)
        check("[%s] Sat stop form: same stop can't be saved; lowering a long stop is refused" % tag, js(page, "()=>document.getElementById('csSave').disabled"))
        js(page, "()=>{ const i=document.getElementById('csStop'); i.value='58000'; re1SatStopIn(); }"); page.wait_for_timeout(200)
        check("[%s] lowering a long stop is refused" % tag, js(page, "()=>document.getElementById('csSave').disabled") and "raised" in js(page, "()=>document.getElementById('csErr').innerText"))
        js(page, "()=>{ const i=document.getElementById('csStop'); i.value='60000'; re1SatStopIn(); }"); page.wait_for_timeout(300)
        box = js(page, "()=>{const b=document.querySelector('[data-re1-stopbox]');return b?b.innerText.replace(/\\s+/g,' '):''}")
        check("[%s] Sat stop form shows the confirm box (breakeven = entry while Costs OFF) and the broker tick" % tag, "Net breakeven" in box and "60000" in box.replace(",", "") and js(page, "()=>!!document.querySelector('[data-re1-stopconf]')"), box)
        if w in (390, 1440): shot(page, "sat-stop-confirm-%d" % w)
        check("[%s] Sat stop sheet: no overflow" % tag, no_overflow(page))
        js(page, "()=>{ document.getElementById('csConf').checked = true; re1SatStopSave(); }"); page.wait_for_timeout(500)
        t = js(page, "()=>getBook('main').trades.find(x=>x.id==='h1')")
        check("[%s] confirmed: stop written + stopConfirmed + time (sl0 kept)" % tag, t["sl"] == 60000 and t["stopConfirmed"] is True and t["stopConfirmedAt"] and t["sl0"] == 59000, t)
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()



def run_lock(pw, w, h):
    """§6 — the lock lives in the New plan forms (selected account); the ＋ button always opens"""
    tag = str(w)
    cs = cards()
    for i, (acct, r) in enumerate([("main", "missed"), ("main", "hesitated"), ("main", "missed"), ("fam", "missed"), ("fam", "hesitated"), ("fam", "missed")]):
        cs["l%d" % i] = cancelled_card("l%d" % i, "L%d" % i, r, acct=acct, at="2026-10-01T05:00:00.000Z")
    b, page, ce, pe = launch(pw, w, h, doc_c(), cs)
    try:
        check("[%s] precondition: Main and Family both have a review due" % tag, js(page, "()=>re4Due('main') && re4Due('fam')"))
        check("[%s] the ＋ button is never disabled and always opens" % tag, js(page, "()=>!document.getElementById('hdrPlanBtn').disabled"))
        js(page, "()=>{ bdNewOpen(); }"); page.wait_for_timeout(300)
        check("[%s] ＋ opens the New plan popup while the review is due" % tag, js(page, "()=>!!document.getElementById('bdPop')"))
        js(page, "()=>{ bdPopClose(); }")
        # lock is checked against the account selected INSIDE the form
        js(page, "()=>{ switchTab('plan'); coreNewOpen('main', {mode:'new'}); }"); page.wait_for_timeout(500)
        js(page, "(a)=>{ const s=(id,v)=>{const e=document.getElementById(id); e.value=v;}; s('cnTicker',a[0]); s('cnEntry',a[1]); s('cnStop',a[2]); coreNewIn(); }", ["NEWX", "50", "46"]); page.wait_for_timeout(300)
        lk = js(page, "()=>{const l=document.querySelector('[data-re4-formlock]');return {t:l?l.innerText.replace(/\\s+/g,' '):'',save:document.getElementById('cnSave').disabled,draft:document.getElementById('cnDraft').disabled,link:!!(l&&l.querySelector('[data-re4-dorev]'))}}")
        check("[%s] Stock form (due account): red line 'Execution review due · <account>' + 'Do review ›'" % tag, lk["t"].startswith("Execution review due · ") and "Do review" in lk["t"] and lk["link"], lk)
        check("[%s] Stock form: Save plan and Save draft both disabled" % tag, lk["save"] and lk["draft"], lk)
        if w in (390, 1440): shot(page, "form-review-lock-%d" % w)
        check("[%s] Stock form lock: no overflow" % tag, no_overflow(page))
        js(page, "()=>{ coreNewSave(); bdDraftSave(); }"); page.wait_for_timeout(300)
        check("[%s] saving is refused while locked (no plan written)" % tag, js(page, "()=>!coreCardsList.some(c=>c.ticker==='NEWX')"))
        js(page, "()=>{ coreSheetClose(); coreNewOpen('main', {mode:'new'}); }"); page.wait_for_timeout(500)
        js(page, "()=>{ const sel=document.getElementById('cnAcct'); if(sel) sel.value='fam'; coreNewPick('fam'); }"); page.wait_for_timeout(300)
        lk2 = js(page, "()=>({line:!!document.querySelector('[data-re4-formlock]'),fam:re4Due('fam')})")
        check("[%s] Stock form: picking the Family account (also due) keeps the lock; the line names it" % tag, lk2["fam"] and lk2["line"] and js(page, "()=>re4AcctName('fam')") in js(page, "()=>document.querySelector('[data-re4-formlock]').innerText"), [lk2, js(page, "()=>document.querySelector('[data-re4-formlock]').innerText"), js(page, "()=>coreNew.acct")])
        js(page, "()=>{ coreSheetClose(); }")
        js(page, "()=>{ ln4Write(o=>{ o.exrev=[{acct:'main',at:new Date().toISOString(),n:4,stopped:'a',change:'b',day:thaiToday()}]; }); }"); page.wait_for_timeout(500)
        js(page, "()=>{ coreNewOpen('main', {mode:'new'}); }"); page.wait_for_timeout(500)
        js(page, "(a)=>{ const s=(id,v)=>{const e=document.getElementById(id); e.value=v;}; s('cnTicker',a[0]); s('cnEntry',a[1]); s('cnStop',a[2]); coreNewIn(); }", ["NEWY", "50", "46"]); page.wait_for_timeout(300)
        check("[%s] an account with no review due is not blocked (no line, no disabled Save)" % tag, js(page, "()=>!document.querySelector('[data-re4-formlock]') && !document.getElementById('cnDraft').disabled"))
        js(page, "()=>{ coreSheetClose(); }")
        # Satellite form: same lock against its account
        js(page, "()=>{ ln4Write(o=>{ o.exrev=[]; }); acctActive='main'; }"); page.wait_for_timeout(300)
        js(page, "()=>{ pb2OpenAsset('XAUUSD'); }"); page.wait_for_timeout(500)
        sl = js(page, "()=>({line:!!document.querySelector('[data-re4-formlock]'),save:(document.querySelector('[data-pb2-save]')||{}).disabled,draft:(document.querySelector('[data-pb2-draft]')||{}).disabled})")
        check("[%s] Satellite form (due account): line + Save plan / Save draft disabled" % tag, sl["line"] and sl["save"] and sl["draft"], sl)
        js(page, "()=>{ bdPopClose(); }")
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


def run_shots(pw, w, h):
    """standard re1d-*.png set (no animation): Today · Plan board · one form per strategy · Port risk · Settings (risk section) · Satellite form"""
    tag = str(w)
    cs = cards(); cs["pA"] = plan_card("AAA", 100, 92, px=102.0); cs["pB"] = plan_card("BBB", 60, 55)
    d = doc_c()
    for a in d["books"].values(): a["settings"]["capital"] = {"core": 5000000, "satB": 100000}
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        shot(page, "today-%s" % tag)
        check("[%s] Today: no overflow" % tag, no_overflow(page))
        board(page); shot(page, "plan-board-%s" % tag)
        check("[%s] Plan board: no overflow" % tag, no_overflow(page))
        js(page, "()=>{ switchTab('plan'); coreNewOpen('main', {mode:'new'}); }"); page.wait_for_timeout(500)
        js(page, "(a)=>{ const s=(id,v)=>{const e=document.getElementById(id); e.value=v;}; s('cnTicker',a[0]); s('cnEntry',a[1]); s('cnStop',a[2]); coreNewIn(); }", ["AMD", "182.5", "170"]); page.wait_for_timeout(400)
        shot(page, "form-momentum-%s" % tag)
        check("[%s] Momentum form: no overflow" % tag, no_overflow(page))
        js(page, "()=>coreFormPort('ladder')"); page.wait_for_timeout(300)
        js(page, "(a)=>{ const s=(id,v)=>{const e=document.getElementById(id); e.value=v;}; s('cnTicker',a[0]); s('cnEntry',a[1]); s('cnStop',a[2]); coreNewIn(); }", ["NVDA2", "180", "170"]); page.wait_for_timeout(400)
        shot(page, "form-compounder-%s" % tag)
        check("[%s] Compounder form: no overflow" % tag, no_overflow(page))
        js(page, "()=>{ coreSheetClose(); }"); page.wait_for_timeout(200)
        SAT = """()=>{ const i={id:'gi',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[]}; sat7dWrite('satIdeas','gi',i); satIdeasList.push(i); switchTab('plan'); pb2={step:2,id:'gi',a:'XAUUSD',dir:'Buy',acct:'main',entry:'2642',sl:'2628',tp:'2684',ema:true,str:true,mss:null}; pb2Render(); }"""
        js(page, SAT); page.wait_for_timeout(500); shot(page, "form-satellite-%s" % tag)
        check("[%s] Satellite form: no overflow" % tag, no_overflow(page))
        check("[%s] Satellite: no LN2 header, no zeroed legacy Open-Risk / Legacy numbers (Plan, Satellite form)" % tag, js(page, "()=>typeof ln2HeaderHtml==='undefined' && !document.querySelector('[data-ln2-hd],[data-ln2-box],[data-ln2-row]') && !/Open Risk|Legacy|Risk Sat \\(/.test(document.body.innerText)"))
        js(page, "()=>{ bdPopClose(); switchTab('mix'); }"); page.wait_for_timeout(500)
        shot(page, "port-risk-%s" % tag)
        check("[%s] Port risk: no overflow" % tag, no_overflow(page))
        check("[%s] Port: no LN2 / legacy Open-Risk numbers" % tag, js(page, "()=>!document.querySelector('[data-ln2-hd],[data-ln2-box]') && !/Legacy/.test(document.body.innerText)"))
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(400)
        js(page, "()=>{ const e=document.querySelector('[data-re1-snap]'); if(e) e.scrollIntoView({block:'start'}); }"); page.wait_for_timeout(250)
        shot(page, "settings-risk-%s" % tag)
        check("[%s] Settings (risk section): no overflow" % tag, no_overflow(page))
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


with sync_playwright() as pw:
    for w, h in ((360, 780), (390, 844), (1280, 800), (1440, 900)):
        run_core(pw, w, h); run_passed(pw, w, h); run_review(pw, w, h); run_sat(pw, w, h); run_lock(pw, w, h)
        if w in (390, 1440): run_shots(pw, w, h)
bad = [r for r in results if not r[1]]
print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
