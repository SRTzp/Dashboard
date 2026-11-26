#!/usr/bin/env python3
"""E2E1 — the whole trade loop with REAL clicks (Plan form → Today → Place → Filled → Manage → Close → Journal), at 1440 and 390, plus the permanent 'no dead button' guard.
Every click goes through e2e1_common.click(): it must change the DOM / open-close a sheet / show a message within 1.5 s and raise no console.error / console.warn / page error.
Run: python3 tests/run_tests_e2e1.py   (E2E1_SHOTS=1 writes docs/screenshots/e2e1-*.png · E2E1_ONLY=J1,J2 to pick journeys · docs/briefs/E2E1-brief.md)"""
import sys, os, re
from playwright.sync_api import sync_playwright
from e2e1_common import *
import e2e1_common as E

ONLY = [x for x in os.environ.get("E2E1_ONLY", "").split(",") if x]
ROOM = "()=>{ const e=document.querySelector('[data-lr2-room=\"main\"]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
MANAGE = "()=>[...document.querySelectorAll('[data-hf5-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())"


def strict(page):
    return js(page, "()=>(window.__nestedWrites||[]).concat(window.__undefWrites||[]).map(x=>x.path+' :: '+x.field).concat(document.getElementById('hf6SaveBar') ? ['Not saved bar'] : [])")


def want(j): return not ONLY or j in ONLY


def trade_of(page, id, acct="main"):
    return js(page, "([id,a])=>{ const i=sat7dIdea(id); const s=i&&(i.accts||{})[a]; const t=s&&(getBook(a).trades||[]).find(x=>x.id===s.trade_id); return t?{status:t.status,sl:t.sl,qty:t.qty,entry:t.entry,exit:t.exitPrice}:null; }", [id, acct])


def newest_idea(page, asset):
    return js(page, "(a)=>{ const l=(satIdeasList||[]).filter(i=>i.asset===a); return l.length ? l[l.length-1].id : null; }", asset)


def j1(pw, w):
    J = "J1"; b, page, ce, pe = start(pw, w)
    try:
        room0 = js(page, ROOM)
        ok = new_sat_plan(page, w, J, 0, False, "main", 2643, 2660, 2600)
        ok &= click(page, "[data-pb2-save]", "Save plan", J)[0]; page.wait_for_timeout(500)
        id = newest_idea(page, "XAUUSD")
        step(J, w, "+ New plan → fill → Save plan", ok and id, "")
        has = page.locator('[data-re2-row="XAU"][data-re2-grp="enter"]').count()
        step(J, w, "Today · Enter row shows XAU", has == 1, has)
        ok, blk = place_from_today(page, "XAU", J)
        step(J, w, "Place › → Confirm (order working)", ok and not blk, blk)
        chk = page.locator('[data-re2-row="XAU"][data-re2-grp="check"]').count()
        step(J, w, "Check orders row (Filled ✓ button)", chk == 1, chk)
        ok = filled_from_today(page, "XAU", J)
        mr = js(page, MANAGE)
        step(J, w, "Filled → Manage row, Holding", ok and len(mr) == 1 and "Holding" in mr[0] and "Short" in mr[0], mr)
        tr = trade_of(page, id)
        step(J, w, "trade saved in the Main book, status open", tr and tr["status"] == "open", tr)
        if SHOTS_ON: shot(page, "xau-filled-%d" % w)
        ok = set_price(page, "XAU", 2630, J)
        mr = js(page, MANAGE)
        step(J, w, "Price › → 'Last 2,630' + P&L", ok and mr and "Last 2,630" in mr[0], mr)
        ok, err = move_stop_ui(page, "XAU", 2650, J)
        mr = js(page, MANAGE); tr = trade_of(page, id)
        step(J, w, "Move stop › to 2,650 (cut ≥ 50%) saved", ok and tr and tr["sl"] == 2650 and "✓ risk cut ≥ 50%" in (mr[0] if mr else ""), [err, mr, tr])
        ok = close_ui(page, "XAU", 2621.5, J, 0.5)
        mr = js(page, MANAGE)
        step(J, w, "TP1 rule (the app has none): exit 50% @ 2,621.5 → half left, still Holding", ok and mr and "#0.09" in mr[0], mr)
        ok, err = move_stop_ui(page, "XAU", 2643, J)
        tr = trade_of(page, id)
        step(J, w, "…stop to entry 2,643", ok and tr and tr["sl"] == 2643, [err, tr])
        ok = close_ui(page, "XAU", 2610, J)
        mr = js(page, MANAGE); tr = trade_of(page, id)
        step(J, w, "Close (win) → Manage row gone", ok and not mr and tr and tr["status"] == "closed", [mr, tr])
        ok = goto(page, "journal", J); page.wait_for_timeout(700)
        jt = js(page, "()=>document.body.innerText.replace(/\\s+/g,' ')")
        import re
        m = re.search(r"XAUUSD.{0,70}?\+([\d.]+)R.{0,12}\+\$([\d,]+)", jt)
        step(J, w, "Journal shows XAUUSD with R and $", ok and m is not None, jt[jt.find("XAUUSD"):][:200])
        if SHOTS_ON and w == 1440: shot(page, "journal-xau-1440")
        goto(page, "today", J); page.wait_for_timeout(500)
        step(J, w, "Risk room back to the start (no reserved Sat risk)", js(page, ROOM) == room0, [room0, js(page, ROOM)])
        chk = js(page, "(id)=>{ const i=sat7dIdea(id); const c=pb2Calc(i,'main'); return null; }", id)
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def save_plan(page, J):
    ok = click(page, "[data-pb2-save]", "Save plan", J)[0]; page.wait_for_timeout(450); return ok


def close_sheet(page, J):
    if js(page, "()=>!!document.getElementById('bdPop')"): click(page, "#bdPop [data-bd-popx]", "✕ close sheet", J)


def plan_card_text(page, id):
    js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(350)
    t = sel_text(page, f'[data-bd-card="{id}"]'); js(page, "()=>switchTab('today')"); page.wait_for_timeout(250); return t


def j2(pw, w):
    J = "J2"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        STEP = "()=>{ const i=satIdeasList[satIdeasList.length-1]; const c=pb2Calc(i,'main'); return {step:c.model&&c.model.step, reasons:(c.c&&c.c.re1&&c.c.re1.reasons)||[]}; }"
        ok = new_sat_plan(page, w, J, 1, True, "main", 90000, 88500, 94000); ok &= save_plan(page, J)
        id1 = newest_idea(page, "BTCUSD"); s0 = js(page, STEP)
        step(J, w, "+ New plan BTC Long (Buy) saved · step 1", ok and s0["step"] == 1, s0)
        ok, blk = place_from_today(page, "BTC", J); step(J, w, "Place › → Confirm", ok and not blk, blk)
        ok = filled_from_today(page, "BTC", J); tr = trade_of(page, id1)
        step(J, w, "Filled → trade open", ok and tr and tr["status"] == "open", tr)
        ok = close_ui(page, "BTC", 88500, J); tr = trade_of(page, id1)
        step(J, w, "Close at the stop (loss)", ok and tr and tr["status"] == "closed", tr)
        ok = new_sat_plan(page, w, J, 1, True, "main", 90000, 88500, 94000); ok &= save_plan(page, J)
        id2 = newest_idea(page, "BTCUSD"); s1 = js(page, STEP)
        step(J, w, "loss → step advances 1 → 2, re-entry needed", ok and s1["step"] == 2 and "SAT_REENTRY_COND" in s1["reasons"], s1)
        ok = click(page, enter_btn(page, "BTC"), "BTC Enter row · Place", J)[0]; page.wait_for_timeout(250)
        dis = js(page, "()=>{ const y=document.querySelector('[data-pb2-yes]'); return y ? y.disabled : null; }")
        has_tick = page.locator("#bdPop input[type=checkbox]").count()
        step(J, w, "re-entry offered once: Place sheet has the Re-entry tick, Confirm disabled until ticked", ok and has_tick == 1 and dis is True, [has_tick, dis])
        ok = click(page, "#bdPop input[type=checkbox]", "tick Re-entry", J)[0]
        dis = js(page, "()=>document.querySelector('[data-pb2-yes]').disabled")
        ok &= click(page, "[data-pb2-yes]", "Confirm re-entry", J)[0]; page.wait_for_timeout(300)
        step(J, w, "tick → Confirm enabled → re-entry order placed", ok and dis is False and not js(page, "()=>!!document.getElementById('bdPop')"), dis)
        ok = filled_from_today(page, "BTC", J); ok &= close_ui(page, "BTC", 88500, J); tr = trade_of(page, id2)
        step(J, w, "re-entry filled and closed (loss)", ok and tr and tr["status"] == "closed", tr)
        ok = new_sat_plan(page, w, J, 1, True, "main", 90000, 88500, 94000); ok &= save_plan(page, J)
        id3 = newest_idea(page, "BTCUSD"); s2 = js(page, STEP); card = plan_card_text(page, id3) or ""
        step(J, w, "second re-entry blocked (SAT_REENTRY_USED) with the reason on the plan card", ok and "SAT_REENTRY_USED" in s2["reasons"] and "Re-entry already used" in card, [s2, card[:160]])
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def card_info(page, id):
    """Plan board card of a plan: its ⚠ text + the fix button + whether a Place pill is enabled (the Today Enter row hides a queue-blocked plan)."""
    js(page, "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); }"); page.wait_for_timeout(350)
    r = js(page, "(id)=>{ const c=document.querySelector('[data-bd-card=\"'+id+'\"]'); if(!c) return null; const w=c.querySelector('[data-pc2-warn]'); const f=c.querySelector('[data-pv-fixbtn]'); const p=[...c.querySelectorAll('button')].find(b=>/Place/.test(b.innerText)); return {warn:w&&w.innerText.replace(/\\s+/g,' ').trim(), fix:f&&f.innerText.trim(), place:p?!p.disabled:null, txt:c.innerText.replace(/\\s+/g,' ').slice(0,200)}; }", id)
    js(page, "()=>switchTab('today')"); page.wait_for_timeout(300); return r


def j3(pw, w):
    J = "J3"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        ok = new_sat_plan(page, w, J, 0, False, "main", 2643, 2660, 2600); ok &= save_plan(page, J); xid = newest_idea(page, "XAUUSD")
        ok &= new_sat_plan(page, w, J, 1, False, "main", 90000, 91500, 86000); ok &= save_plan(page, J); bid = newest_idea(page, "BTCUSD")
        step(J, w, "two plans (XAU, BTC) saved", ok, "")
        ok, blk = place_from_today(page, "XAU", J); step(J, w, "XAU full risk placed", ok and not blk, blk)
        c = card_info(page, bid)
        step(J, w, "XAU working → BTC plan blocked, ⚠ line names XAU", c and c["warn"] and "XAU order is working" in c["warn"], c)
        er = js(page, "()=>{ const r=document.querySelector('[data-re2-row=\"BTC\"][data-re2-grp=\"enter\"]'); return r ? {txt:r.innerText.replace(/\\s+/g,' '), fix:[...r.querySelectorAll('button')].map(b=>b.innerText.trim()), placeDis:[...r.querySelectorAll('[data-re2-btn=\"place\"]')].every(b=>b.disabled)} : null; }")
        step(J, w, "Today › Enter keeps the blocked BTC plan: ⚠ reason + 'Open XAU ›' link, Place disabled", er and "XAU order is working" in er["txt"] and "Open XAU ›" in er["fix"] and er["placeDis"], er)
        ok = click(page, '[data-re2-row="BTC"][data-re2-grp="enter"] [data-re2-btn="keep"]', "Enter row fix link", J)[0]
        step(J, w, "the fix link opens XAU (drawer)", ok and js(page, "()=>!!document.getElementById('bdDrawer')"), "")
        js(page, "()=>{ try{ bdClose(); }catch(e){} }")
        filled_from_today(page, "XAU", J)
        er = js(page, "()=>{ const r=document.querySelector('[data-re2-row=\"BTC\"][data-re2-grp=\"enter\"]'); return r ? {txt:r.innerText.replace(/\\s+/g,' '), fix:[...r.querySelectorAll('button')].map(b=>b.innerText.trim())} : null; }")
        step(J, w, "XAU open unmoved: Enter row shows 'XAU is open with full risk … (now 0%)' + Move stop ›", er and "XAU is open with full risk" in er["txt"] and "Move stop ›" in er["fix"], er)
        c = card_info(page, bid)
        step(J, w, "XAU open, stop unmoved → 'XAU is open with full risk … (now 0%)' + Move stop ›", c and c["warn"] and "XAU is open with full risk" in c["warn"] and "now 0%" in c["warn"] and c["fix"] == "Move stop ›", c)
        js(page, "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); }"); page.wait_for_timeout(300)
        ok = click(page, f'[data-bd-card="{bid}"] [data-pv-fixbtn]', "card Move stop ›", J)[0]
        step(J, w, "card's Move stop › opens the stop sheet (XAU)", ok and js(page, "()=>!!document.getElementById('csStop')"), "")
        click(page, ".core-sheet button:has-text('Cancel')", "stop Cancel", J); js(page, "()=>switchTab('today')"); page.wait_for_timeout(250)
        ok, err = move_stop_ui(page, "XAU", 2650, J)
        c = card_info(page, bid)
        step(J, w, "move XAU stop (cut ≥ 50%) → BTC unblocked", ok and c and not c["warn"], [err, c])
        ok, blk = place_from_today(page, "BTC", J); ok &= filled_from_today(page, "BTC", J)
        step(J, w, "BTC placed + filled", ok and not blk, blk)
        ok2, _ = move_stop_ui(page, "BTC", 90750, J)
        ok = new_sat_plan(page, w, J, 2, False, "main", 800, 810, 770); ok &= save_plan(page, J)
        ok3, blk = place_from_today(page, "S50", J); ok3 &= filled_from_today(page, "S50", J)
        step(J, w, "XAU + BTC cut ≥ 50% → S50 allowed, 3 Sat open", ok and ok2 and ok3 and not blk, blk)
        ok = new_sat_plan(page, w, J, 3, False, "main", 80, 82, 75); ok &= save_plan(page, J); rid = newest_idea(page, "BRENT")
        c = card_info(page, rid)
        step(J, w, "3 open → 4th blocked '3 Sat setups open (XAU, BTC, S50) · max 3'", ok and c and c["warn"] and "3 Sat setups open (XAU, BTC, S50) · max 3" in c["warn"], c)
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def j6(pw, w):
    J = "J6"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        ok = new_sat_plan(page, w, J, 0, False, "main", 2643, 2660, 2600); ok &= save_plan(page, J); xid = newest_idea(page, "XAUUSD")
        ok &= new_sat_plan(page, w, J, 1, False, "main", 90000, 91500, 86000); ok &= save_plan(page, J); bid = newest_idea(page, "BTCUSD")
        ok, blk = place_from_today(page, "XAU", J); step(J, w, "XAU order placed", ok and not blk, blk)
        q = js(page, "(id)=>{ const i=sat7dIdea(id), c=pb2Calc(i,'main'); return (c.c&&c.c.re1&&c.c.re1.reasons||[]).filter(x=>/QUEUE/.test(x)); }", bid)
        step(J, w, "while XAU works, BTC reserved-risk queue is busy", q == ["SAT_QUEUE_BUSY"], q)
        ok = click(page, '[data-re2-row="XAU"][data-re2-grp="check"] .re2-main, [data-re2-row="XAU"][data-re2-grp="check"] .l1', "XAU check row", J)[0]
        ok &= click(page, '[onclick*="bdCancelOrder"]', "Cancel order", J)[0]
        sheet = js(page, "()=>!!document.querySelector('[data-re4-reason]')"); dis = js(page, "()=>document.getElementById('cxGo').disabled")
        step(J, w, "Cancel order opens the reason sheet, button disabled until a reason", ok and sheet and dis is True, [sheet, dis])
        if SHOTS_ON and w == 390: shot(page, "cancel-order-sheet-390")   # the sheet that used to sit under the drawer dim
        page.select_option("[data-re4-reason]", "hesitated"); page.wait_for_timeout(200)
        ok = click(page, "[data-re4-go]", "Cancel order (confirm)", J)[0]; page.wait_for_timeout(500)
        chk = page.locator('[data-re2-row="XAU"][data-re2-grp="check"]').count()
        q = js(page, "(id)=>{ const i=sat7dIdea(id), c=pb2Calc(i,'main'); return (c.c&&c.c.re1&&c.c.re1.reasons||[]).filter(x=>/QUEUE/.test(x)); }", bid)
        step(J, w, "cancelled → XAU leaves Check orders, reserved risk released (BTC queue free)", ok and chk == 0 and q == [], [chk, q])
        # cancel a plan: Plan board ✕ → reason → confirm
        js(page, "()=>{ closeDrawerIfAny && 0; }") if False else None
        js(page, "()=>{ try{ bdClose(); }catch(e){} switchTab('plan'); bdSetSeg('plan'); bdRender(); }"); page.wait_for_timeout(400)
        if page.locator(f'[data-bd-card="{bid}"] [onclick*="re4Open"]').first.is_visible():
            ok = click(page, f'[data-bd-card="{bid}"] [onclick*="re4Open"]', "plan ✕", J)[0]
        else:   # phone: ✕ lives in the ⋯ menu
            ok = click(page, f'[data-bd-card="{bid}"] [data-pc2-menu]', "plan ⋯", J)[0]
            ok &= click(page, f'[data-bd-card="{bid}"] [data-pc2-menupop] [onclick*="re4Open"]', "plan ⋯ › Cancel plan", J)[0]
        page.select_option("[data-re4-reason]", "plan_error") if page.locator("[data-re4-reason] option[value=plan_error]").count() else page.select_option("[data-re4-reason]", index=1)
        page.wait_for_timeout(200); ok &= click(page, "[data-re4-go]", "Cancel plan (confirm)", J)[0]; page.wait_for_timeout(500)
        gone = page.locator(f'[data-bd-card="{bid}"]').count()
        step(J, w, "cancel a plan → card leaves the Plan board", ok and gone == 0, gone)
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def stock_idea_plan(page, J):
    """My idea (AAPL breakout 100 fired, wrong-if 90) → Today Ideas row → Make plan › → the plan form. Returns the form state."""
    import run_tests_nt1b as B, run_tests_nt2 as T2
    from datetime import datetime, timezone
    t0 = js(page, "()=>thaiToday()")
    B.seed_my(page, {"h2": T2.idea(21, ("stock", "AAPL"), "AAPL breakout", t0, B.add(t0, 5), scs=[T2.sc("breakout", 100, hit=datetime.now(timezone.utc).isoformat())], view="bull", next=None, invLevel=90)})
    B.px(page, "AAPL", 101.0); js(page, "()=>{ lr2DetOpen = false; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
    ok = click(page, '[data-nt1b-it="my:h2"] [onclick*="nt1bMakePlan"]', "Idea › Make plan ›", J)[0]; page.wait_for_timeout(700)
    f = js(page, "()=>({tab:activeTab, entry:(coreEl('cnEntry')||{}).value, stop:(coreEl('cnStop')||{}).value, ticker:(coreEl('cnTicker')||{}).value, txt:(document.querySelector('.core-sheet')||{innerText:''}).innerText.replace(/\\s+/g,' ')})")
    f["ok"] = ok; return f


def j7(pw, w):
    J = "J7"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        f = stock_idea_plan(page, J)
        step(J, w, "My idea → Make plan › lands in the plan form with the levels (AAPL · entry 100 · stop 90)", f["ok"] and f["tab"] == "plan" and f["entry"] == "100" and f["stop"] == "90" and f["ticker"] == "AAPL", f)
        ok = click(page, "[onclick*=coreNewSave]", "Save plan", J)[0]; page.wait_for_timeout(900)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        has = page.locator('[data-re2-row="AAPL"][data-re2-grp="enter"]').count()
        step(J, w, "Save plan → Today Enter row AAPL", ok and has == 1, has)
        ok, blk = place_from_today(page, "AAPL", J)
        step(J, w, "continue to Place › → Confirm → Check orders row", ok and not blk and page.locator('[data-re2-row="AAPL"][data-re2-grp="check"]').count() == 1, blk)
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def j4(pw, w):
    J = "J4"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        f = stock_idea_plan(page, J)
        step(J, w, "plan form: homework not done → 'homework 70%' and #42 shown", "homework 70%" in f["txt"] and "#42" in f["txt"], f["txt"][:300])
        ok = click(page, "[onclick*=coreNewSave]", "Save plan", J)[0]; page.wait_for_timeout(900)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        row = sel_text(page, '[data-re2-row="AAPL"][data-re2-grp="enter"]')
        step(J, w, "Today Enter row shows the 70% size (#42 · risk $420)", ok and row and "#42" in row and "−$420" in row, row)
        js(page, "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); }"); page.wait_for_timeout(400)
        card = sel_text(page, "[data-bd-card]")
        step(J, w, "Plan board card shows the same size (#42 · 0.28%)", card and "#42" in card and "0.28%" in card, card)
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        ok = click(page, enter_btn(page, "AAPL"), "AAPL Place", J)[0]; page.wait_for_timeout(300)
        sh = sel_text(page, "#bdPop") or ""
        step(J, w, "Place sheet shows the 70% size", ok and "42" in sh and "70%" in sh, sh[:300])
        ok = click(page, "[data-pb2-yes], [data-ef-yes], #bdPop .go.p", "Confirm", J)[0]; page.wait_for_timeout(500)
        chk = page.locator('[data-re2-row="AAPL"][data-re2-grp="check"]').count()
        step(J, w, "Place › → Confirm → Check orders row", ok and chk == 1, chk)
        ok = click(page, enter_btn(page, "AAPL", "check"), "AAPL Filled", J)[0]; page.wait_for_timeout(500)
        q = js(page, "()=>(coreEl('cbQty')||{}).value")
        step(J, w, "Filled opens the buy sheet with qty = the card (42)", ok and q == "42", q)
        ok = click(page, "[onclick*=coreBuy1Save]", "Save buy", J)[0]; page.wait_for_timeout(700)
        js(page, "()=>{ switchTab('plan'); bdSetSeg('hold'); bdRender(); }"); page.wait_for_timeout(500)
        card = sel_text(page, "[data-bd-card]")
        step(J, w, "Holding card #42 @ 100 · stop 90", ok and card and "#42 @ 100" in card and "stop 90" in card, card)
        if SHOTS_ON: pass
        ok = click(page, "[data-bd-card] [onclick*=coreStopOpen]", "Move stop", J)[0]
        page.locator("#csStop").fill("95"); page.wait_for_timeout(400)
        ok &= click(page, "[onclick*=coreStopSave]", "Save stop", J)[0]; page.wait_for_timeout(600)
        card = sel_text(page, "[data-bd-card]")
        step(J, w, "Move stop › 90 → 95 saved on the card", ok and card and "stop 95" in card, card)
        ok = click(page, "[data-bd-card] .bd-tk, [data-bd-card]", "open card", J)[0]
        ok &= click(page, "[data-bd-close]", "Close trade", J)[0]
        page.locator("#cpExitPrice").fill("112"); page.wait_for_timeout(150)
        ok &= click(page, "#cpConfirmBtn", "Confirm close", J)[0]; page.wait_for_timeout(600)
        js(page, "()=>{ try{ bdClose(); }catch(e){} }")
        goto(page, "journal", J); page.wait_for_timeout(700)
        jt = js(page, "()=>document.body.innerText.replace(/\\s+/g,' ')")
        import re
        m = re.search(r"AAPL.{0,70}?\+([\d.]+)R.{0,12}\+\$([\d,]+)", jt)
        step(J, w, "Close (win) → Journal shows AAPL with R and $", ok and m is not None, jt[jt.find("AAPL"):][:200])
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def j5(pw, w):
    J = "J5"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        import run_tests_phase374 as P4
        roomM0 = js(page, ROOM)
        ok = click(page, "#hdrPlanBtn", "＋ New plan", J)[0]
        ok &= click(page, "#bdPop [onclick=\"lrNewAcct('fam')\"]", "Family", J)[0]
        ok &= click(page, "#bdPop [onclick=\"bdNewPick('D')\"]", "Compounder", J)[0]; page.wait_for_timeout(500)
        ok &= click(page, ".core-sheet button:has-text('TH · THB')", "TH market", J)[0]
        page.locator("#cnTicker").fill("CPALL"); page.locator("#cnEntry").fill("60"); page.locator("#cnStop").fill("55"); page.wait_for_timeout(500)
        acct = js(page, "()=>coreEl('cnAcct').value")
        f = js(page, "()=>(document.querySelector('.core-sheet')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
        step(J, w, "Family form: typing the ticker keeps the account Family (no flip to Main) · Pilot #20,000", ok and acct == "fam" and "Pilot" in f and "#20000" in f.replace(",", ""), [acct, f[:200]])
        ok = click(page, "[onclick*=coreNewSave]", "Save plan", J)[0]; page.wait_for_timeout(900)
        sv = js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='CPALL.BK'); return c && c.acct; }")
        step(J, w, "saved plan belongs to Family", ok and sv == "fam", sv)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        row = sel_text(page, '[data-re2-row="CPALL.BK"][data-re2-grp="enter"]')
        step(J, w, "Today Enter row CPALL.BK (F) · Pilot #20,000", ok and row and "COMP F" in row and "#20,000" in row, row)
        ok, blk = place_from_today(page, "CPALL.BK", J)
        step(J, w, "Place › → Confirm → Check orders (still Family)", ok and not blk and page.locator('[data-re2-row="CPALL.BK"][data-re2-grp="check"]').count() == 1 and "COMP F" in (sel_text(page, '[data-re2-row="CPALL.BK"][data-re2-grp="check"]') or ""), blk)
        ok = click(page, enter_btn(page, "CPALL.BK", "check"), "Pilot Filled", J)[0]; page.wait_for_timeout(500)
        q = js(page, "()=>(coreEl('cbQty')||{}).value")
        ok &= click(page, "[onclick*=coreBuy1Save]", "Save buy", J)[0]; page.wait_for_timeout(700)
        where = js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='CPALL.BK'); return {acct:c.acct, fam:(getBook('fam').trades||[]).some(t=>t.id===c.trade_id), main:(getBook('main').trades||[]).some(t=>t.id===c.trade_id)}; }")
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        step(J, w, "Pilot Filled (qty = card 20,000): trade is in the Family book, none in Main, Main risk room unchanged", ok and q == "20000" and where["acct"] == "fam" and where["fam"] and not where["main"] and js(page, ROOM) == roomM0, [q, where])
        rowF = js(page, "()=>{ const r=document.querySelector('[data-re2-row=\"CPALL.BK\"][data-re2-grp=\"manage\"]'); return r ? {txt:r.innerText.replace(/\\s+/g,' '), btns:[...r.querySelectorAll('button')].map(b=>b.innerText.trim())} : null; }")
        step(J, w, "add-on locked: Manage row offers 'Homework → unlocks adds ›', no Add-on ›", rowF and any("Homework" in x for x in rowF["btns"]) and not any("Add-on" in x for x in rowF["btns"]), rowF)
        # thesis done (seeded): Pilot was 1.0% → existing risk already at the 1.00% limit → the add-on is blocked (ADDON_TOTAL_RISK), reason on the row
        P4.put_wl(page, {"CPALL.BK": P4.wl_doc("CPALL.BK", exit_="e", why="w", trigger="t", confirmed=True)})
        js(page, "()=>{ coreWrite(coreCardsList.find(x=>x.ticker==='CPALL.BK').id, {px:60, pxDate:thaiToday()}); re1Cache={}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        click(page, "[onclick=\"acctSwitch('fam')\"]", "Family", J); js(page, "()=>{ switchTab('today'); re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(500)
        rowF = js(page, "()=>{ const r=document.querySelector('[data-re2-row=\"CPALL.BK\"][data-re2-grp=\"manage\"]'); return r ? {txt:r.innerText.replace(/\\s+/g,' '), btns:[...r.querySelectorAll('button')].map(b=>({t:b.innerText.trim(), dis:b.disabled}))} : null; }")
        step(J, w, "(b) thesis done, Pilot risk 1.0% + new order > 1.00% → Add-on blocked, ADDON_TOTAL_RISK reason on the row, button disabled", rowF and "Add-on blocked" in rowF["txt"] and "over the 1% limit for this stock (all lots at their current stop)" in rowF["txt"] and all(x["dis"] for x in rowF["btns"] if "Add-on" in x["t"]) and js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='CPALL.BK'); const cx=coreCtxC(c); return coreAddRe1(c, coreView(c,cx), cx).model.reasons.includes('ADDON_TOTAL_RISK'); }"), rowF)
        js(page, "()=>{ switchTab('plan'); bdSetSeg('hold'); bdRender(); }"); page.wait_for_timeout(400)
        ok = click(page, "[data-bd-card] .bd-tk, [data-bd-card]", "open card", J)[0]
        ok &= click(page, "[data-bd-close]", "Close trade", J)[0]
        page.locator("#cpExitPrice").fill("70"); page.wait_for_timeout(150)
        ok &= click(page, "#cpConfirmBtn", "Confirm close", J)[0]; page.wait_for_timeout(600)
        js(page, "()=>{ try{ bdClose(); }catch(e){} }")
        goto(page, "journal", J); page.wait_for_timeout(700)
        jt = js(page, "()=>document.body.innerText.replace(/\\s+/g,' ')")
        import re
        m = re.search(r"CPALL.{0,70}?\+([\d.]+)R", jt)
        step(J, w, "Close (win) → Journal shows CPALL.BK with R", ok and m is not None, jt[jt.find("CPALL"):][:200])
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


# ───────────────────────────── Part 3 · crawl: click every enabled button once on seeded screens
SKIP = r"delet|remov|sign ?out|log ?out|import|export|backup|restore|reset|clear|wipe|upload|download|window\.open|https?:|mailto|copy|paste|syncNow|brandSync|deleteAcct|delTrade|dropAll|purge"
RESET = """()=>{ try{ coreSheetClose(); }catch(e){} try{ bdPopClose(); }catch(e){} try{ bdClose(); }catch(e){} try{ closeMoreMenu(); }catch(e){}
  const c=document.getElementById('closePosOverlay'); if(c) c.classList.remove('show'); document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show')); document.querySelectorAll('.ui-sheet-backdrop,.wi-sheet,.cp-sheet').forEach(o=>{ if(o.id!=='bdDrawer') o.remove(); });
  window.prompt = (m, d)=>String(d); window.confirm = ()=>true; window.alert = ()=>{}; window.open = ()=>null; }"""
LIST = """(scope)=>{ const root=document.querySelector(scope)||document.body; return [...root.querySelectorAll('button,[role=button]')].filter(b=>b.offsetParent&&!b.disabled&&b.getAttribute('aria-disabled')!=='true'&&!b.closest('header,#tabsMain,.moreMenu,#sdToast')&&!(b.closest('details:not([open])')&&b.tagName!=='SUMMARY')&&b.getBoundingClientRect().width>0&&getComputedStyle(b).visibility!=='hidden').map((b,i)=>({i, sig:(b.innerText||b.getAttribute('aria-label')||b.title||'').replace(/\\s+/g,' ').trim().slice(0,30)+'|'+(b.getAttribute('onclick')||'').slice(0,80)+'|'+(b.dataset?Object.keys(b.dataset).slice(0,2).join(','):'')})); }"""
NTH = """([scope,i])=>{ const root=document.querySelector(scope)||document.body; const l=[...root.querySelectorAll('button,[role=button]')].filter(b=>b.offsetParent&&!b.disabled&&b.getAttribute('aria-disabled')!=='true'&&!b.closest('header,#tabsMain,.moreMenu,#sdToast')&&!(b.closest('details:not([open])')&&b.tagName!=='SUMMARY')&&b.getBoundingClientRect().width>0&&getComputedStyle(b).visibility!=='hidden'); const b=l[i]; if(!b) return false; b.setAttribute('data-e2crawl','1'); return true; }"""


def crawl(page, name, setup, scope="body", cap=80):
    done = set(); n = 0; skipped = 0
    for _ in range(cap * 3):
        js(page, RESET); setup(); page.wait_for_timeout(200)
        lst = js(page, LIST, scope)
        nxt = next((x for x in lst if x["sig"] not in done), None)
        if not nxt: break
        done.add(nxt["sig"])
        if re.search(SKIP, nxt["sig"], re.I): skipped += 1; continue
        js(page, "()=>document.querySelectorAll('[data-e2crawl]').forEach(e=>e.removeAttribute('data-e2crawl'))")
        if not js(page, NTH, [scope, nxt["i"]]): continue
        n += 1
        click(page, "[data-e2crawl=\"1\"]", "%s · %s" % (name, nxt["sig"][:60]), "crawl", wait=1500)
        E.thai_scan(page, "%s · after %s" % (name, nxt["sig"][:30].strip()))   # CL2 — no visible Thai after any crawled click
        if n >= cap: break
    return n, skipped, len(done)


def crawl_seed(pw, w):
    import run_tests_lrf as LF
    b, page, ce, pe = launch(pw, w, 900 if w >= 900 else 844, c=LF.cards_today())
    LF.today(page)
    js(page, "()=>satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50','BRENT'])")
    js(page, "()=>{ const s = tdSettings(); s.products = Object.assign({}, s.products || {}, {BRENT:{sys:'lot', perPoint:100, lotStep:0.01, minLot:0.01, cur:'USD'}}); }")
    js(page, "()=>{ window.prompt = (m, d)=>String(d); ['main','fam'].forEach(a=>{ const st = ps1Settings(a); st.psRisk = Object.assign({}, st.psRisk || {}, {minStop:{XAUUSD:0.3, BTCUSD:0.5, S50:0.3, BRENT:0.3}}); }); re1Cache = {}; }")
    H.mk(page, "x1", "XAUUSD", "Short"); H.place(page, "x1"); H.fill(page, "x1")          # seed: XAU held (Manage row)
    H.mk(page, "b1", "BTCUSD", "Short")                                                  # BTC plan
    js(page, INSTALL); page.wait_for_timeout(300)
    return b, page, ce, pe


def j_crawl(pw, w):
    J = "CRAWL"; b, page, ce, pe = crawl_seed(pw, w); page.set_default_timeout(5000)
    try:
        def go_today(): js(page, "()=>{ switchTab('today'); re2GrpAll={enter:true,check:true,manage:true}; todayRefresh(true); }")
        def go_plan(seg): return lambda: js(page, "(s)=>{ switchTab('plan'); bdSetSeg(s); bdRender(); }", seg)
        def go_watch(): js(page, "()=>{ switchTab('watch'); try{ wlSetView('wl'); }catch(e){} }")
        def go_watch_detail():
            js(page, "()=>{ switchTab('watch'); try{ wlSetView('wl'); }catch(e){} try{ wlOpen('AAPL'); }catch(e){} }")
        def go_manage_drawer(): js(page, "()=>{ switchTab('today'); todayRefresh(true); bdOpen('x1'); }")
        tot = 0
        for nm, fn, sc in (("Today", go_today, "body"), ("Plan · Planned", go_plan("plan"), "body"), ("Plan · Ordered", go_plan("ord"), "body"), ("Plan · Holding", go_plan("hold"), "body"), ("Watch", go_watch, "body"), ("Watch detail", go_watch_detail, "body"), ("Manage drawer", go_manage_drawer, "#bdDr")):
            n, sk, seen = crawl(page, nm, fn, sc)
            tot += n
            check(f"[CRAWL {w}] {nm}: {n} buttons clicked ({sk} send/delete/external skipped, {seen} distinct)", n > 0, n)
        step(J, w, "crawl: %d buttons clicked once, none dead" % tot, not [d for d in E.DEAD if d[0] == "crawl"], [d for d in E.DEAD if d[0] == "crawl"][:6])
        step(J, w, "no page errors", not pe, pe[:2])
        step(J, w, "CL2: no visible Thai text on any crawled screen or sheet (user-typed account names exempt)", not [t for t in E.THAI_SEEN if t[0].split(" · ")[0] in ("Today", "Plan", "Watch", "Watch detail", "Manage drawer")], [t for t in E.THAI_SEEN][:6])
    finally:
        b.close()


# CL2 — every other screen (Flow, Journal, Port, Weekend, Homework, Settings cards, drawers, static sheets forced open): nothing visible in Thai
THAI_SCREENS = [
  ("Today · Daily", "()=>{ switchTab('today'); td3SetMode('d'); todayRefresh(true); }"), ("Today · Weekend", "()=>{ switchTab('today'); td3SetMode('w'); todayRefresh(true); }"),
  ("Plan · Planned", "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); }"), ("Plan · Ordered", "()=>{ switchTab('plan'); bdSetSeg('ord'); bdRender(); }"), ("Plan · Holding", "()=>{ switchTab('plan'); bdSetSeg('hold'); bdRender(); }"),
  ("Plan · Stocks (Momentum)", "()=>{ switchTab('plan'); setPlanScope('stock'); }"), ("Plan · Stocks (Compounder)", "()=>{ switchTab('plan'); setPlanScope('ladder'); }"), ("Plan · Future", "()=>{ switchTab('plan'); setPlanScope('future'); }"),
  ("Flow", "()=>{ switchTab('flow'); }"), ("Watch · Ideas", "()=>{ switchTab('watch'); wlSetView('idea'); }"), ("Watch · list", "()=>{ switchTab('watch'); wlSetView('wl'); }"), ("Watch · Screen", "()=>{ switchTab('watch'); wlSetView('screen'); }"),
  ("Watch · detail", "()=>{ switchTab('watch'); wlSetView('wl'); wlOpen('AAPL'); }"), ("Watch · Homework", "()=>{ switchTab('watch'); wlSetView('wl'); hwOpen('AAPL'); }"),
  ("Journal", "()=>{ switchTab('journal'); }"), ("Port", "()=>{ switchTab('mix'); }"),
  ("Settings · Portfolio", "()=>{ switchTab('today'); openSettings(); }"), ("Settings · System", "()=>{ switchTab('today'); openSystemSettings(); }"), ("Settings · Industries", "()=>{ switchTab('today'); openIndustryManager(); }"),
  ("Core weekly-close price sheet", "()=>{ switchTab('plan'); setPlanScope('stock'); corePxOpen('xAAA'); }"), ("New Core plan sheet", "()=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen(); }"),
  ("Manage drawer", "()=>{ switchTab('today'); todayRefresh(true); bdOpen('x1'); }"), ("Plan drawer", "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); bdOpen('b1'); }"),
]
THAI_WATCH = [
  ("Watch (fixture) · Ideas", "()=>{ switchTab('watch'); wlSetView('idea'); }"), ("Watch (fixture) · Momentum list", "()=>{ switchTab('watch'); wl1Trk='winner'; wlSetView('wl'); }"),
  ("Watch (fixture) · Compounder list", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); }"), ("Watch (fixture) · Screen", "()=>{ switchTab('watch'); wlSetView('screen'); }"),
  ("Watch (fixture) · AAPL detail", "()=>{ switchTab('watch'); wlSetView('wl'); wlOpen('AAPL'); }"), ("Watch (fixture) · AAPL Homework", "()=>{ switchTab('watch'); wl1Trk='winner'; wlSetView('wl'); hwOpen('AAPL'); }"),
  ("Watch (fixture) · COST Homework", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); hwOpen('COST'); }"), ("Watch (fixture) · WHSE Homework", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); hwOpen('WHSE'); }"),
  ("Watch (fixture) · ZZ Homework", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); hwOpen('ZZ'); }"), ("Watch (fixture) · Add stocks sheet", "()=>{ switchTab('watch'); wlSetView('wl'); wl1ImpOpen(); }"),
]
THAI_OVERLAYS = ["teOverlay", "closePosOverlay", "glValOverlay", "wlAddOverlay", "ltOverlay", "sysOverlay", "reasonMgrOverlay", "scoreMgrOverlay", "cancelOverlay", "ffQeOverlay", "ffSetOverlay", "industryOverlay", "setOverlay"]


def j_thai(pw, w):
    J = "THAI"; b, page, ce, pe = crawl_seed(pw, w); page.set_default_timeout(5000)
    try:
        for nm, setup in THAI_SCREENS:
            js(page, RESET); 
            try: js(page, setup)
            except Exception: pass
            page.wait_for_timeout(250); E.thai_scan(page, "THAI · " + nm)
        for oid in THAI_OVERLAYS:
            js(page, RESET); js(page, "(id)=>{ const o=document.getElementById(id); if(o) o.classList.add('show'); }", oid); page.wait_for_timeout(120); E.thai_scan(page, "THAI · overlay " + oid)
        js(page, RESET); js(page, "()=>{ const b=document.getElementById('bkBanner'); if(b) b.classList.add('show'); }"); page.wait_for_timeout(120); E.thai_scan(page, "THAI · backup banner")
        bad = [t for t in E.THAI_SEEN if t[0].startswith("THAI") and "Watch (fixture)" not in t[0]]
        step(J, w, "CL2: no visible Thai text on any tab / segment / Settings card / sheet / forced-open overlay (%d screens)" % (len(THAI_SCREENS) + len(THAI_OVERLAYS) + 1), not bad, bad[:8])
        step(J, w, "no page errors", not pe, pe[:2])
    finally:
        b.close()
    # the Watch tab needs the Watch fixture (stocks with Fact Sheets / thesis / Screen source) — the crawl seed has no watchlist
    import hw1_common as HW
    b, page, pe = HW.open_hw(pw, w, 900 if w >= 900 else 844); page.set_default_timeout(5000)
    try:
        for nm, setup in THAI_WATCH:
            js(page, RESET)
            try: js(page, setup)
            except Exception: pass
            page.wait_for_timeout(300); E.thai_scan(page, "THAI · " + nm)
        bad = [t for t in E.THAI_SEEN if t[0].startswith("THAI") and "Watch (fixture)" in t[0]]
        step(J, w, "CL2: no visible Thai text on Watch (Ideas · lists · Screen · detail · Homework × 4 stocks · Add stocks) with the Watch fixture", not bad, bad[:8])
    finally:
        b.close()


def j_bar(pw, w):
    """HF6 'Not saved' bar: pushes the page down (never covers the header / tabs), reason in plain words, Retry clears it."""
    J = "BAR"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        top0 = js(page, "()=>({h:document.querySelector('header').getBoundingClientRect().top, t:document.getElementById('tabsMain').getBoundingClientRect().top})")
        js(page, "()=>{ window.__forceSaveFail = true; dirtyBooks.set(acctActive,(dirtyBooks.get(acctActive)||0)+1); pendingLocalWrite = true; doPersist(); }"); page.wait_for_timeout(900)
        r = js(page, "()=>{ const b=document.getElementById('hf6SaveBar'); if(!b) return null; const br=b.getBoundingClientRect(), h=document.querySelector('header').getBoundingClientRect(), t=document.getElementById('tabsMain').getBoundingClientRect(); return {txt:b.innerText.replace(/\\s+/g,' ').trim(), barBottom:br.bottom, barTop:br.top, headTop:h.top, tabsTop:t.top, ovf:document.documentElement.scrollWidth-innerWidth, wide:br.width, font:getComputedStyle(b).fontFamily, bodyFont:getComputedStyle(document.body).fontFamily}; }")
        step(J, w, "forced save failure → '⚠ Not saved · Server unreachable · Retry ›' (plain words)", r and r["txt"] == "⚠ Not saved · Server unreachable · Retry ›", r)
        step(J, w, "bar sits above the header (header + tabs pushed down, nothing overlapped)", r and r["barTop"] <= 1 and r["headTop"] >= r["barBottom"] - 1 and r["tabsTop"] >= r["barBottom"] - 1 and r["ovf"] <= 0, r)
        step(J, w, "bar uses the app font (not serif)", r and r["font"] == r["bodyFont"] and "serif" not in r["font"].split(",")[0].lower(), [r and r["font"], r and r["bodyFont"]])
        js(page, "()=>window.scrollTo(0, 400)"); page.wait_for_timeout(300)
        r2 = js(page, "()=>{ const b=document.getElementById('hf6SaveBar').getBoundingClientRect(), t=document.getElementById('tabsMain').getBoundingClientRect(); return {barTop:b.top, barBottom:b.bottom, tabsTop:t.top}; }")
        step(J, w, "scrolled: the bar stays on top and the sticky tabs sit under it", r2["barTop"] <= 1 and r2["tabsTop"] >= r2["barBottom"] - 1, r2)
        js(page, "()=>window.scrollTo(0, 0)")
        if SHOTS_ON: shot(page, "notsaved-%d" % w)
        js(page, "()=>{ window.__forceSaveFail = false; }")
        ok = click(page, "[data-hf6-retry]", "Retry ›", J)[0]; page.wait_for_timeout(900)
        gone = js(page, "()=>!document.getElementById('hf6SaveBar')")
        back = js(page, "()=>document.querySelector('header').getBoundingClientRect().top")
        step(J, w, "Retry after the fix → bar gone, header back to the top", ok and gone and abs(back - top0["h"]) <= 1, [gone, back, top0])
        step(J, w, "no console errors / page errors (besides the forced save failure)", not [x for x in (ce + pe) if 'forced failure' not in x], (ce + pe)[:2])
    finally:
        b.close()


def j_rrg(pw, w):
    """rrgCacheFresh: today's cached rows with neither tail nor tailF are NOT fresh (rebuilt from the job bars) — rows saved without tails never block tails for the rest of the day."""
    J = "RRG"; b, page, ce, pe = start(pw, w)
    try:
        r = js(page, """()=>{ const f = ffState(); const today = rrgToday(); const base = {day:today, model:RRG_MODEL, build:RRG_BUILD, bars:f.rrg && f.rrg.bars, barsAt:f.rrg && f.rrg.barsAt};
          const row = x=>Object.assign({sym:'XLK', quad:'lead', ratio:101, mom:100.5}, x);
          const mk = rows=>({rrg:Object.assign({}, f.rrg, {day:today, model:RRG_MODEL, rowsD:rows, rowsW:rows})});
          const keep = f.rrg; const out = {};
          const fresh = rows=>{ try{ const g = mk(rows); const orig = rrgBarsFresh; window.rrgBarsFresh = ()=>true; try{ return rrgCacheFresh(g); } finally { window.rrgBarsFresh = orig; } }catch(e){ return 'ERR ' + e.message; } };
          out.none = fresh([row({}), row({sym:'XLE'})]); out.tailF = fresh([row({tailF:[1,2,3,4]})]); out.tail = fresh([row({tail:[[1,2],[3,4]]})]); out.mixed = fresh([row({}), row({tailF:[1,2,3,4]})]); out.empty = fresh([]);
          return out; }""")
        step(J, w, "cached rows with neither tail nor tailF → not fresh (rebuild)", r["none"] is False, r)
        step(J, w, "rows with tailF / tail (or at least one) → still fresh; empty → not fresh", r["tailF"] is True and r["tail"] is True and r["mixed"] is True and r["empty"] is False, r)
        step(J, w, "no console errors / page errors · strict mock saw no nested-array / undefined write · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


def j5b(pw, w):
    """Compounder add-on rule (RE1-answers-A 16): thesis complete + existing tranches' risk at the current stop + new order ≤ 1.00%, order ≤ 0.50%; no +1.5R / breakeven condition; below the Pilot entry = a warning line only."""
    J = "J5b"; b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        import run_tests_phase374 as P4
        ok = click(page, "#hdrPlanBtn", "＋ New plan", J)[0]
        ok &= click(page, "#bdPop [onclick=\"lrNewAcct('fam')\"]", "Family", J)[0]
        ok &= click(page, "#bdPop [onclick=\"bdNewPick('D')\"]", "Compounder", J)[0]; page.wait_for_timeout(500)
        ok &= click(page, ".core-sheet button:has-text('TH · THB')", "TH market", J)[0]
        page.locator("#cnTicker").fill("CPALL"); page.locator("#cnEntry").fill("60"); page.locator("#cnStop").fill("55")
        page.select_option("#cnRiskSel", index=0); page.wait_for_timeout(500)   # Pilot risk 0.5%
        ok &= click(page, "[onclick*=coreNewSave]", "Save plan", J)[0]; page.wait_for_timeout(900)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        ok2, blk = place_from_today(page, "CPALL.BK", J); ok2 &= click(page, enter_btn(page, "CPALL.BK", "check"), "Pilot Filled", J)[0]; page.wait_for_timeout(400)
        ok2 &= click(page, "[onclick*=coreBuy1Save]", "Save buy", J)[0]; page.wait_for_timeout(700)
        step(J, w, "Pilot 0.5% (#10,000 @ 60, stop 55) filled", ok and ok2 and not blk, blk)
        P4.put_wl(page, {"CPALL.BK": P4.wl_doc("CPALL.BK", exit_="e", why="w", trigger="t", confirmed=True)})
        js(page, "()=>{ coreWrite(coreCardsList.find(x=>x.ticker==='CPALL.BK').id, {px:60, pxDate:thaiToday()}); re1Cache={}; }")
        click(page, "[onclick=\"acctSwitch('fam')\"]", "Family", J); js(page, "()=>{ switchTab('today'); re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(500)
        ROW = "()=>{ const r=document.querySelector('[data-re2-row=\"CPALL.BK\"][data-re2-grp=\"manage\"]'); return r ? {txt:r.innerText.replace(/\\s+/g,' '), btns:[...r.querySelectorAll('button')].map(b=>({t:b.innerText.trim(), dis:b.disabled}))} : null; }"
        r = js(page, ROW)
        step(J, w, "(a) thesis done · Pilot at ~0R (price 60 = entry) · total ≤ 1% → 'add-on allowed' + Add-on › (no +1.5R / breakeven needed)", r and "add-on allowed" in r["txt"] and any(x["t"] == "Add-on ›" and not x["dis"] for x in r["btns"]), r)
        ok = click(page, '[data-re2-row="CPALL.BK"][data-re2-grp="manage"] button:has-text("Add-on")', "Add-on ›", J)[0]; page.wait_for_timeout(400)
        sh = js(page, "()=>({txt:(document.querySelector('.core-sheet')||{innerText:''}).innerText.replace(/\\s+/g,' '), warn:!!document.querySelector('[data-ca-warn]'), qty:(coreEl('caQty')||{}).value, dis:(coreEl('caSave')||{}).disabled})")
        step(J, w, "(a) the add-on sheet opens: no warning line (price = entry), qty ≤ the 0.5% order, Save enabled", ok and "Record add-on buy" in sh["txt"] and not sh["warn"] and sh["dis"] is False and int(sh["qty"] or 0) > 0, sh)
        click(page, ".core-sheet button:has-text('Cancel')", "Cancel add-on", J)
        # (c) price below the Pilot entry → warning line, still allowed
        js(page, "()=>{ coreWrite(coreCardsList.find(x=>x.ticker==='CPALL.BK').id, {px:58, pxDate:thaiToday()}); re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(500)
        r = js(page, ROW)
        ok = click(page, '[data-re2-row="CPALL.BK"][data-re2-grp="manage"] button:has-text("Add-on")', "Add-on ›", J)[0]; page.wait_for_timeout(400)
        sh = js(page, "()=>({warn:(document.querySelector('[data-ca-warn]')||{innerText:''}).innerText.replace(/\\s+/g,' '), dis:(coreEl('caSave')||{}).disabled, qty:(coreEl('caQty')||{}).value})")
        step(J, w, "(c) add-on price 58 below the Pilot entry 60 → '⚠ Adding below entry — re-check ④ Wrong if' in the sheet, still allowed (Save enabled)", ok and r and any(x["t"] == "Add-on ›" and not x["dis"] for x in r["btns"]) and "Adding below entry" in sh["warn"] and sh["dis"] is False, [r, sh])
        ok = click(page, "[onclick*=coreBuyAddSave]", "Save add-on", J)[0]; page.wait_for_timeout(700)
        lots = js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='CPALL.BK'); return (c.lots||[]).length; }")
        step(J, w, "(c) Save → second lot recorded", ok and lots == 2, lots)
        # (b) ADDON_TOTAL_RISK (total would exceed 1.00%) is driven in J5 with a 1.0% Pilot
        step(J, w, "no console errors / page errors · strict mock · no Not-saved bar", not ce and not pe and not strict(page), [(ce + pe)[:2], strict(page)])
    finally:
        b.close()


JOURNEYS_FN = [("J1", j1), ("J2", j2), ("J3", j3), ("J6", j6), ("J7", j7), ("J4", j4), ("J5", j5), ("J5b", j5b), ("CRAWL", j_crawl), ("THAI", j_thai), ("BAR", j_bar), ("RRG", j_rrg)]

if __name__ == "__main__":
    with sync_playwright() as pw:
        for name, fn in JOURNEYS_FN:
            if not want(name): continue
            for w in (1440, 390):
                try: fn(pw, w)
                except Exception as e:
                    step(name, w, "journey crashed: %s" % str(e)[:200], False, str(e)[:500])
    check("no dead buttons / click-handler errors in the whole run", not E.DEAD, E.DEAD[:8])
    bad = [r for r in results if not r[1]]
    print("\nJOURNEY TABLE (journey · step · 1440 / 390)")
    seen = []
    for (j, n, w, ok) in E.JOURNEYS:
        if (j, n) not in seen: seen.append((j, n))
    for (j, n) in seen:
        r = {w: ok for (jj, nn, w, ok) in E.JOURNEYS if jj == j and nn == n}
        print("  %-3s %-70s %s / %s" % (j, n[:70], "pass" if r.get(1440) else ("FAIL" if 1440 in r else "-"), "pass" if r.get(390) else ("FAIL" if 390 in r else "-")))
    print(f"SUMMARY e2e1: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
