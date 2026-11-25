#!/usr/bin/env python3
"""HF5 D — risk audit: Today and Plan agree after every order step (docs/briefs/HF5-brief.md).
Walks one Sat (XAU lot) and one Momentum (US stock) plan through plan → Place order (working) → Filled → Move stop → Close and, at each step, compares the SAME number in:
  expected (hand-computed from the plan numbers) · Today › Risk room chips (Sat / MMT used %) · Today open risk (Act header) · Plan board summary · Plan card (posView) · engine budget check
  (max(0, −weekly net) + open + reserved + candidate 0). Also: cancel before fill releases reserved risk · Family and Main kept apart.
Run: python3 tests/run_tests_hf5_risk.py   (prints the step × place table)"""
import sys, os
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results, plan_card
import run_tests_lrf as LF
import hf5_common as H

MEASURE = """(a)=>{ re1Cache = {}; const L = re1L(a), eq = L.basis.weekEquity, R = re2Room(a), RE = RiskEngine, now = Date.now();
  const sb = RE.satBudgetCheck({basis:L.basis, now, account:a, ideas:L.ideas, costsFor:L.costsFor, candidateRisk:0});
  const mc = RE.momentumCheck({now, account:a, basis:L.basis, ideas:L.ideas, costsFor:L.costsFor, candidate:{ideaId:'__none', isAddition:false, riskMoney:0}});
  const p = v=>v == null ? null : Math.round(v / eq * 1e6) / 1e4;   // % of week equity, 2 dp
  const o = {eq, sat_room:R.sat.used, mom_room:R.mom.used, open_today:lr2OpenRisk(a), eng_sat:p(sb.usageWeek), eng_mom:p(mc.usageWeek), mom_left:R.mom.left, fx:L.fx};
  o.sat_room = Math.round(o.sat_room * 100) / 100; o.mom_room = Math.round(o.mom_room * 100) / 100; o.open_today = Math.round(o.open_today * 100) / 100;
  return o; }"""
CARD = """(id)=>{ const it = bdById(id); if(!it) return null; const pv = posView(it); const eq = re1L(it.acct || tdHome()).basis.weekEquity;
  const v = it.status === 'hold' ? pv.openRisk : pv.plannedRisk; return {st: it.status, pct: v == null ? 0 : Math.round(v / eq * 1e6) / 1e4}; }"""
BOARD = "()=>{ bdRender(); const e = document.querySelector('[data-bd-orisk]'); return e ? parseFloat(e.innerText) : null; }"
ROOM_TXT = "(a)=>{ const e = document.querySelector('[data-lr2-room=\"' + a + '\"]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
TABLE = []


BASE = {}


def snap(page, step, acct, card_id, exp_pct, which, card_exp=None):
    m = js(page, MEASURE, acct); js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(250)
    js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(250)
    board = js(page, BOARD); card = js(page, CARD, card_id) if card_id else {"pct": 0}
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(200)
    room = (m["sat_room"] if which == "sat" else m["mom_room"]) - BASE.get(which, 0); eng = (m["eng_sat"] if which == "sat" else m["eng_mom"]) - BASE.get(which + "_e", 0)   # the fixture already holds other Momentum ideas: compare what THIS plan adds
    row = {"step": step, "expected": round(exp_pct, 2), "room": room, "open_today": m["open_today"], "board": board, "card": card["pct"], "engine": round(eng, 2)}
    TABLE.append(row)
    tol = 0.011
    cexp = (card_exp if card_exp is not None else exp_pct) if card_id else 0
    ok = abs(room - exp_pct) < tol and abs(eng - exp_pct) < tol and abs(card["pct"] - cexp) < tol
    # Today's open-risk chip + the board summary are the ACTIVE total (Momentum + Satellite): they must match each other, and equal the sum of both rooms
    both = round(m["sat_room"] + m["mom_room"], 2)
    ok2 = abs(m["open_today"] - both) < tol and (board is None or abs(board - m["open_today"]) < 0.011)
    check("[%s] %s · expected %.2f%% = Risk room %.2f%% = engine %.2f%% = card %.2f%%" % (which, step, exp_pct, room, eng, card["pct"]), ok, row)
    check("[%s] %s · Today open risk %.2f%% = board %s%% = Sat + MMT rooms %.2f%%" % (which, step, m["open_today"], board, both), ok2, row)
    return m


def sat_walk(pw):
    b, page, ce, pe = H.start(pw)
    try:
        m0 = js(page, MEASURE, "main"); eq, fx = m0["eq"], m0["fx"]
        pc = lambda money: money * fx / eq * 100   # USD money → % of week equity
        H.mk(page, "x1", "XAUUSD", "Short")
        snap(page, "plan", "main", "x1", 0.0, "sat", card_exp=pc(17 * 100 * js(page, "()=>pb2Calc(sat7dIdea('x1'), 'main').lot")))
        H.place(page, "x1")
        lot = js(page, "()=>sat7dIdea('x1').ln4.snap['0'].lot"); risk0 = lot * 17 * 100   # 17 points × $100 / lot-point
        snap(page, "Place order (working)", "main", "x1", pc(risk0), "sat")
        H.fill(page, "x1")
        snap(page, "Filled", "main", "x1", pc(risk0), "sat")
        H.move_stop(page, "x1", 2650)
        snap(page, "Move stop 2,660 → 2,650", "main", "x1", pc(lot * 7 * 100), "sat")
        # Close at the (moved) stop = a realized loss of 7 points; it stays in this week's budget as realized loss, open risk goes to 0
        js(page, "()=>{ const i=sat7dIdea('x1'), a=pb2AcctOf(i), B=getBook(a), t=B.trades.filter(x=>x.id===i.accts[a].trade_id)[0]; t.status='closed'; t.exitPrice=2650; t.exitDate=thaiToday(); t.exitTime=new Date().toISOString(); saveBook(a); sat7dWrite('satIdeas','x1',{status:'closed'}); re1Cache={}; render(); }"); page.wait_for_timeout(400)
        m = snap(page, "Close (loss 7 pts)", "main", None, pc(lot * 7 * 100), "sat")
        # cancel before fill releases the reservation (new BTC plan, Place order, then cancel)
        H.mk(page, "b1", "BTCUSD", "Long")
        H.place(page, "b1")
        blot = js(page, "()=>sat7dIdea('b1').ln4.snap['0'].lot"); br = blot * 1500 * 1
        before = js(page, MEASURE, "main")
        check("[sat] cancel-before-fill: Place order reserves risk (Risk room rises)", before["sat_room"] > m["sat_room"] + 0.001, [m["sat_room"], before["sat_room"]])
        js(page, "()=>bdCancelLvDo('b1', 0, {})"); page.wait_for_timeout(500)
        after = js(page, MEASURE, "main")
        check("[sat] cancel-before-fill releases it (back to %.2f%%)" % m["sat_room"], abs(after["sat_room"] - m["sat_room"]) < 0.011 and abs(after["eng_sat"] - m["eng_sat"]) < 0.011, [m["sat_room"], before["sat_room"], after["sat_room"]])
        TABLE.append({"step": "Cancel before fill (BTC)", "expected": round(m["sat_room"], 2), "room": after["sat_room"], "open_today": after["open_today"], "board": "-", "card": 0, "engine": round(after["eng_sat"], 2)})
        # Family vs Main apart: a plan placed on Family changes Family only
        js(page, "()=>{ re1Cache={}; }")
        H.mk(page, "f1", "S50", "Short", pb_acct="fam")
        fam0 = js(page, MEASURE, "fam"); main0 = js(page, MEASURE, "main")
        H.place(page, "f1")
        fam1 = js(page, MEASURE, "fam"); main1 = js(page, MEASURE, "main")
        check("[sat] Family order: Family Risk room rises, Main stays %.2f%%" % main0["sat_room"], fam1["sat_room"] > fam0["sat_room"] + 0.001 and abs(main1["sat_room"] - main0["sat_room"]) < 0.001, [fam0["sat_room"], fam1["sat_room"], main0["sat_room"], main1["sat_room"]])
        check("[sat] Family order: Family engine budget == Family room", abs(fam1["eng_sat"] - fam1["sat_room"]) < 0.011, fam1)
        TABLE.append({"step": "Family S50 order (Main unchanged)", "expected": round(main0["sat_room"], 2), "room": main1["sat_room"], "open_today": main1["open_today"], "board": "-", "card": 0, "engine": round(main1["eng_sat"], 2)})
        check("[sat] no console errors", not ce and not pe, (ce + pe)[:2])
    finally:
        b.close()


def mom_walk(pw):
    cs = LF.L3.cards_board() if hasattr(LF.L3, "cards_board") else {}
    cs = dict(cs)
    cs["mA"] = plan_card("AAA", 100, 92, px=100.5, ready=True)
    b, page, ce, pe = launch(pw, 1440, 900, c=cs)
    try:
        LF.today(page)
        js(page, "()=>{ window.prompt = (m, d)=>String(d); window.wl1PlaceGate = ()=>true; }")
        m0 = js(page, MEASURE, "main"); eq, fx = m0["eq"], m0["fx"]
        pc = lambda money: money * fx / eq * 100
        BASE["mom"] = m0["mom_room"]; BASE["mom_e"] = m0["eng_mom"]
        # plan: not reserved (engine) — the card shows its planned risk, rooms show 0
        m = js(page, MEASURE, "main"); card = js(page, CARD, "mA")
        TABLE.append({"step": "MMT plan", "expected": 0.0, "room": round(m["mom_room"] - BASE["mom"], 2), "open_today": m["open_today"], "board": "-", "card": card["pct"], "engine": round(m["eng_mom"] - BASE["mom_e"], 2)})
        check("[mom] plan: nothing reserved (Risk room +%.2f%% = engine +%.2f%% = 0) · card shows planned risk %.2f%%" % (m["mom_room"] - BASE["mom"], m["eng_mom"] - BASE["mom_e"], card["pct"]), abs(m["mom_room"] - BASE["mom"]) < 0.011 and abs(m["eng_mom"] - BASE["mom_e"]) < 0.011 and abs(card["pct"] - pc(36 * 8)) < 0.011, [m, card])
        js(page, "()=>{ efCorePlaceOpen('mA'); }"); page.wait_for_timeout(300); js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(600)
        snap(page, "Place order (working)", "main", "mA", pc(36 * 8), "mom")
        js(page, "()=>{ window.__q0 = null; }")
        js(page, "()=>coreBuy1Open('mA')"); page.wait_for_timeout(300); js(page, "()=>coreBuy1Save()"); page.wait_for_timeout(600)
        q = js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='mA'); return getBook(c.acct).trades.filter(x=>x.id===c.trade_id)[0].qty; }")
        snap(page, "Filled (qty %s)" % q, "main", "mA", pc(q * 8), "mom")
        js(page, "()=>coreStopOpen('mA')"); page.wait_for_timeout(250)
        js(page, "()=>{ const el=document.getElementById('csStop'); el.value='96'; coreStopIn(); }"); js(page, "()=>coreStopSave()"); page.wait_for_timeout(600)
        snap(page, "Move stop 92 → 96", "main", "mA", pc(q * 4), "mom")
        js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='mA'), A=c.acct, B=getBook(A), t=B.trades.filter(x=>x.id===c.trade_id)[0]; t.status='closed'; t.exitPrice=96; t.exitDate=thaiToday(); t.exitTime=new Date().toISOString(); saveBook(A); coreCloseCardOfTrade(t, A, 'manual'); re1Cache={}; render(); }"); page.wait_for_timeout(500)
        snap(page, "Close (loss 4 / share)", "main", None, pc(q * 4), "mom")
        check("[mom] no console errors", not ce and not pe, (ce + pe)[:2])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        sat_walk(pw)
        mom_walk(pw)
    print("\nSTEP × PLACE (% of week equity)")
    print("%-38s %9s %9s %9s %9s %9s %9s" % ("step", "expected", "RiskRoom", "OpenToday", "Board", "Card", "Engine"))
    for r in TABLE:
        print("%-38s %9s %9s %9s %9s %9s %9s" % (r["step"], r["expected"], r["room"], r.get("open_today", "-"), r["board"], r["card"], r["engine"]))
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY hf5_risk: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
