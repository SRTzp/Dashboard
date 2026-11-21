#!/usr/bin/env python3
"""RK1 — Risk per idea in Settings (new values) + hidden unused settings.
(1) Settings › Portfolio & Risk › 'Risk per idea': render · bounds (inline message, Save off) · Reset · save → shared settings + engine · derived box
(2) values flow to the plan sizing (Compounder first entry / total, Momentum, Sat) · saved plans and holdings keep their qty
(3) no 0.45 / 1.25 / 'step N' ladder labels in the rendered UI
(4) hidden (data kept): Daily routine · sub-port goals · Key news days · Sat Tactical TP1 / TP2
(5) Today without routine items · news window from a Weekly Impact CPI event, absent without one · 'No news calendar this week' · main goal still shown
(6) 360 / 390 / 1440 no overflow.   Run: python3 tests/run_tests_rk1.py"""
import os, sys, re, json
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results, NOANIM

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots", "rk1")
os.makedirs(SHOTS, exist_ok=True)
SHOT = os.environ.get("RK1_SHOTS") == "1"


def open_settings(page):
    js(page, "()=>{ serverConfirmed = true; stateFromServer = true; openSettings(); const s = document.getElementById('ps1Sec'); if(s) s.open = true; }"); page.wait_for_timeout(450)


def vals(page):
    return js(page, "()=>['rkComp','rkCompFirst','rkMom','rkSat'].map(i=>document.getElementById(i).value)")


def errs(page):
    return js(page, "()=>[...document.querySelectorAll('.rk1 .crErr')].map(e=>e.textContent.trim()).filter(Boolean)")


def save_off(page):
    return js(page, "()=>document.getElementById('setSaveBtn').disabled")


def fill(page, comp, first, mom, sat):
    for i, v in (("rkComp", comp), ("rkCompFirst", first), ("rkMom", mom), ("rkSat", sat)):
        page.fill("#" + i, v)
    page.wait_for_timeout(120)


SIZE = """()=>{ const L = re1L('main'), s = re1StockSpec(L, 'US'), rf = L.regime.factor;
  const mom = Re1Adapter.sizeMomentum(L, Object.assign({homeworkDone:true, isFirstEntry:true, side:'long', entry:180, stop:160}, s));
  const pil = Re1Adapter.sizeComp(L, Object.assign({kind:'pilot', thesisDone:false, side:'long', entry:100, stop:90}, s));
  const tot = Re1Adapter.sizeComp(L, Object.assign({kind:'pilot', thesisDone:true, side:'long', entry:100, stop:90, levels:[{price:100, splitPct:50}, {price:96, splitPct:50}]}, s));
  const sat = Re1Adapter.sizeSat(L, {entry:2642, stop:2628, tp:2684, side:'long', cond:{ema50:true, structure:true}, product:'XAUUSD', mult:100, fx:1, lotStep:0.01, minLot:0.01});
  return {rf, mom:mom.effPct, pil:pil.effPct, tot:tot.effPct, sat:sat.effPct, momF:mom.formula, satF:sat.formula, step:sat.step}; }"""


def near(a, b, e=1e-6):
    return a is not None and abs(a - b) < e


def over(page):
    return js(page, "()=>document.documentElement.scrollWidth - innerWidth")


def settings(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        open_settings(page)
        sec = js(page, "()=>{ const s = document.getElementById('ps1Sec'); const r = s.querySelector('[data-rk1]'); const hd = r.querySelector('.rk1-h'); return {first: s.querySelector('.secbody').firstElementChild === r, head: hd.innerText.replace(/\\s+/g,' ').trim(), rows: r.querySelectorAll('.rk1-r').length, oldNote: s.querySelector('summary').innerText.indexOf('come from the engine') >= 0}; }")
        check(f"{tag} 1 'Risk per idea' is the first block of Portfolio & Risk · header + Reset · old 'come from the engine' line gone", sec["first"] and sec["head"].startswith("Risk per idea") and sec["head"].endswith("Reset") and not sec["oldNote"], sec)
        check(f"{tag} 1 defaults 1.00 / 0.50 / 0.40 / 0.20 (2 decimals)", vals(page) == ["1.00", "0.50", "0.40", "0.20"], vals(page))
        der = js(page, "()=>document.querySelector('[data-rk1-der]').innerText")
        check(f"{tag} 1 derived box: weekly Momentum 1.60 · Sat 0.80 · applies to new plans · engine modifiers", "Momentum 1.60 %" in der and "Sat 0.80 %" in der and "Applies to new plans" in der and "regime 100 / 80 / 60" in der and "−10" in der and "−20" in der, der)
        if SHOT: page.screenshot(path=os.path.join(SHOTS, "settings-%d.png" % w), full_page=False)
        # bounds
        for (c, f, m, s, key, msg) in (("1.00", "0.50", "0.19", "0.20", "rkMom", "Use 0.20%–0.60%"), ("1.00", "0.50", "0.61", "0.20", "rkMom", "Use 0.20%–0.60%"), ("1.00", "0.50", "0.40", "0.09", "rkSat", "Use 0.10%–0.40%"),
                                       ("1.00", "0.50", "0.40", "0.41", "rkSat", "Use 0.10%–0.40%"), ("0.49", "0.40", "0.40", "0.20", "rkComp", "Use 0.50%–1.50%"), ("1.51", "0.50", "0.40", "0.20", "rkComp", "Use 0.50%–1.50%"),
                                       ("0.80", "0.90", "0.40", "0.20", "rkCompFirst", "First entry can’t be above the total")):
            fill(page, c, f, m, s)
            e = errs(page)
            check(f"{tag} 2 out of bounds ({c}/{f}/{m}/{s}) → '{msg}' · Save off", e == [msg] and save_off(page), [e, save_off(page)])
        fill(page, "1.00", "0.50", "0.40", "0.20"); check(f"{tag} 2 back to valid → no message · Save on", errs(page) == [] and not save_off(page))
        fill(page, "0.50", "0.50", "0.20", "0.10"); check(f"{tag} 2 lower bounds accepted", errs(page) == [] and not save_off(page))
        fill(page, "1.50", "1.50", "0.60", "0.40"); check(f"{tag} 2 upper bounds accepted", errs(page) == [] and not save_off(page))
        # out of bounds is never saved
        fill(page, "1.00", "0.50", "0.90", "0.20"); js(page, "()=>{ try{ saveSettings(); }catch(e){} }"); page.wait_for_timeout(200)
        check(f"{tag} 2 out-of-bounds value never reaches the shared settings / engine", js(page, "()=>[sh().riskPerIdea || null, RiskEngine.POLICY.mom.rptPct]") == [None, 0.4], js(page, "()=>[sh().riskPerIdea || null, RiskEngine.POLICY.mom.rptPct]"))
        # Reset
        fill(page, "1.20", "0.60", "0.50", "0.25"); page.click("[data-rk1-reset]"); page.wait_for_timeout(150)
        check(f"{tag} 3 Reset → 1.00 / 0.50 / 0.40 / 0.20", vals(page) == ["1.00", "0.50", "0.40", "0.20"] and errs(page) == [], vals(page))
        # derived follows the inputs
        fill(page, "1.20", "0.60", "0.50", "0.25")
        check(f"{tag} 3 derived box follows the inputs (Momentum 2.00 · Sat 1.00)", "Momentum 2.00 %" in js(page, "()=>document.querySelector('[data-rk1-der]').innerText") and "Sat 1.00 %" in js(page, "()=>document.querySelector('[data-rk1-der]').innerText"))
        # overflow
        check(f"{tag} 4 Settings no horizontal overflow", over(page) <= 0, over(page))
        row = js(page, "()=>{ const r = document.querySelector('[data-rk1] .rk1-r:not(.rk1-c)'); const x = [...r.children].map(e=>e.getBoundingClientRect()); return {h: r.getBoundingClientRect().height, inside: x.every(q=>q.right <= innerWidth + 0.5)}; }")
        check(f"{tag} 4 one line per row (inputs inside the viewport)", row["inside"] and row["h"] < 60, row)
        # save → shared + engine + reload-safe
        page.click("#setSaveBtn"); page.wait_for_timeout(500)
        st = js(page, "()=>({sh: sh().riskPerIdea, pol: [RiskEngine.POLICY.comp.totalCapPct, RiskEngine.POLICY.comp.pilotPct, RiskEngine.POLICY.mom.rptPct, RiskEngine.POLICY.sat.stepRpt, RiskEngine.POLICY.mom.weeklyPct, RiskEngine.POLICY.sat.weeklyPct], perAcct: Object.keys(state.settings).indexOf('riskPerIdea')})")
        check(f"{tag} 5 Save → shared settings {{compTotal, compFirst, mom, sat}} (one set, no per-account copy) + engine POLICY", st["sh"] == {"compTotal": 1.2, "compFirst": 0.6, "mom": 0.5, "sat": 0.25} and st["pol"][0] == 1.2 and st["pol"][1] == 0.6 and st["pol"][2] == 0.5 and st["pol"][3] == [0.25] * 4 and near(st["pol"][4], 2.0) and near(st["pol"][5], 1.0) and st["perAcct"] < 0, st)
        s = js(page, SIZE); rf = s["rf"]
        check(f"{tag} 6 plan sizing follows the settings: Momentum {0.5}×regime · Compounder first {0.6}×regime · total {1.2}×regime · Sat 0.25", near(s["mom"], 0.5 * rf) and near(s["pil"], 0.6 * rf, 1e-6) and near(s["tot"], 1.2 * rf) and near(s["sat"], 0.25), s)
        check(f"{tag} 6 Sat formula is just the value (no 'Step n')", not re.search(r"step", s["satF"] or "", re.I) and (s["satF"] or "").startswith("0.25%"), s["satF"])
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(300)
        open_settings(page)
        check(f"{tag} 5 reopening Settings shows the saved values", vals(page) == ["1.20", "0.60", "0.50", "0.25"], vals(page))
        page.click("[data-rk1-reset]"); page.click("#setSaveBtn"); page.wait_for_timeout(400)
        s = js(page, SIZE)
        check(f"{tag} 6 Reset + Save → defaults back (Momentum 0.40 · Compounder 0.50 / 1.00 · Sat 0.20)", near(s["mom"], 0.4 * s["rf"]) and near(s["pil"], 0.5 * s["rf"]) and near(s["tot"], 1.0 * s["rf"]) and near(s["sat"], 0.2), s)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def hidden(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        open_settings(page)
        vis = js(page, """()=>{ const v = id => { const e = typeof id === 'string' ? document.querySelector(id) : id; return !!(e && e.getClientRects().length); };
          document.querySelectorAll('details.setsec').forEach(d=>d.open = true);
          return {rt: v('#tdRtSet'), news: v('#newsSetSec'), tac: v('[data-rk1-hidden="tactical"]'), tp1: v('#sV2Tp1R'), satrow: v('[data-rk1-satrow]'), sec: v('#satV2Sec'), rem: v('#td4RemBtn'), ps1: v('#ps1Sec'),
            kept: !!(document.getElementById('tdRtSet') && document.getElementById('newsSet') && document.getElementById('sV2Tp1R'))}; }""")
        check(f"{tag} 7 Daily routine editor · Key news days · Sat Tactical TP1/TP2 are not visible (still in the page = data kept)", not vis["rt"] and not vis["news"] and not vis["tac"] and not vis["tp1"] and vis["kept"], vis)
        check(f"{tag} 7 Sat rules card keeps a 'Min stop per asset' row", vis["satrow"], vis)
        # stored data untouched by a save
        keep = js(page, """()=>{ const B = getBook(tdHome()); B.settings.routine = {slots:[{id:'z', start:'09:00', end:'10:00', name:'Z', link:'none'}], satDaily:['XAUUSD']}; B.settings.dailyExtra = [{id:'e1', name:'Extra'}]; B.settings.weekTasks = [{id:'w1', name:'W', auto:null, on:true}];
          B.settings.newsEvents = [{date:'2026-10-07', kind:'CPI', time:'19:30'}]; B.settings.subGoals = {main:{Winner:{cur:'USD', start:1, target:2, deadline:'2027-01-01', startDate:'2026-01-01'}}}; return JSON.stringify([B.settings.routine, B.settings.dailyExtra, B.settings.weekTasks, B.settings.newsEvents, B.settings.subGoals]); }""")
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(300); open_settings(page)
        page.fill("#rkMom", "0.45"); page.click("#setSaveBtn"); page.wait_for_timeout(400)
        after = js(page, "()=>{ const B = getBook(tdHome()); return JSON.stringify([B.settings.routine, B.settings.dailyExtra, B.settings.weekTasks, B.settings.newsEvents, B.settings.subGoals]); }")
        check(f"{tag} 8 saving Settings keeps the hidden settings' stored data byte for byte", keep == after, [keep, after])
        js(page, "()=>{ openSystemSettings(); document.querySelectorAll('details.setsec').forEach(d=>{ d.open = true; }); }"); page.wait_for_timeout(300)
        sys_txt = js(page, "()=>[...document.querySelectorAll('details.setsec')].filter(d=>d.getClientRects().length).map(d=>d.querySelector('summary').innerText.trim())")
        check(f"{tag} 7 system settings: no 'Daily routine' / 'Key news days (Sat)' sections", not any(re.match(r"^(Daily routine|Key news days)", t) for t in sys_txt), sys_txt)
        rem = js(page, "()=>{ const e = document.getElementById('td4RemBtn'); return !!(e && e.getClientRects().length); }")
        check(f"{tag} 7 reminders button still reachable (system settings)", rem)
        subs = js(page, "()=>({sub: document.querySelectorAll('[data-gl-subrow],[data-gl-subhead]').length, main: !!document.querySelector('#glSet [data-gl-startdate]')})")
        check(f"{tag} 7 sub-port goal fields gone · the main account goal form stays", subs["sub"] == 0 and subs["main"], subs)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


WI = """(dt)=>{ const mon = wiCurMon(), at = new Date(Date.now() + dt * 60000).toISOString();
  const doc = {events:{cpi:{title:'US CPI (Sep)', kind:'release', scheduled_at:at, time_status:'confirmed', status:'scheduled'}, pce:{title:'Core PCE', kind:'release', scheduled_at:at, time_status:'confirmed', status:'scheduled'}},
    assets:{XAUUSD:{impact:'HIGH', event_refs:['cpi','pce']}}};
  wiDocs = {}; wiDocs[mon] = doc; return mon; }"""


def today(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        # a stored routine exists but must not show
        js(page, "()=>{ const B = getBook(tdHome()); B.settings.routine = {slots:[{id:'z', start:'00:00', end:'23:59', name:'RoutineSlotZ', link:'none'}], satDaily:['XAUUSD','BTCUSD']}; B.settings.dailyExtra = [{id:'e1', name:'ExtraDailyQ'}]; todayRefresh(true); }"); page.wait_for_timeout(400)
        t = js(page, "()=>({txt: document.querySelector('[data-td-wrap]').innerText, rt: !!document.querySelector('[data-td-routine],[data-td-tl],[data-kind=\"sat-daily\"],[data-gl-xrow]'), tasks: tdBuild().tasks.map(x=>x.kind), rtObj: tdRoutine()})")
        check(f"{tag} 9 Today shows no routine slots / Sat daily check / other daily tasks / weekly-task or routine % items", not t["rt"] and "RoutineSlotZ" not in t["txt"] and "ExtraDailyQ" not in t["txt"] and "sat-daily" not in t["tasks"] and t["rtObj"] == {"slots": [], "satDaily": []} and not re.search(r"Daily · \d+%", t["txt"]), t)
        pct = js(page, "()=>tdBuild().tasks.some(x=>x.special==='satdaily')")
        check(f"{tag} 9 no 'Check Sat plan today' task", not pct)
        td = js(page, "()=>({own: typeof td5Write === 'function', plus: !!document.querySelector('[data-td5-plus]')})")
        check(f"{tag} 9 own to-dos (TD5) stay", td["own"] and td["plus"], td)
        goals = js(page, "()=>({goals: !!document.querySelector('[data-td3-goals]'), acct: document.querySelectorAll('[data-td3-acct]').length, sub: document.querySelectorAll('[data-td3-subgoals],[data-td3-sub]').length})")
        check(f"{tag} 10 Today goals: account rows stay · no sub-port goals", goals["goals"] and goals["acct"] >= 1 and goals["sub"] == 0, goals)
        # main goal still shown
        g = js(page, """()=>{ const B = getBook(tdHome()); B.settings.goals = {main:{cur:'THB', start:1000000, startDate:'2026-01-01', target:2000000, deadline:'2027-12-31'}}; B.settings.subGoals = {main:{Winner:{cur:'USD', start:1, target:2, deadline:'2027-01-01', startDate:'2026-01-01'}}};
          todayRefresh(true); return {pct: !!document.querySelector('[data-td3-acct="main"] [data-td3-pct]'), sub: document.querySelectorAll('[data-td3-sub]').length}; }""")
        check(f"{tag} 10 main account goal still shown (progress %) while a stored sub-port goal is not", g["pct"] and g["sub"] == 0, g)
        # news window from Weekly Impact
        js(page, WI, 10); js(page, "()=>{ re1Cache = {}; }")
        nw = js(page, "()=>({ev: newsEvents(), blk: newsSatBlock() && newsSatBlock().kind, warn: newsWarnLine(), pct: newsSizePctNow()})")
        check(f"{tag} 11 news window from a Weekly Impact HIGH CPI event: warn + size cut (Core PCE is not CPI)", len(nw["ev"]) == 1 and nw["ev"][0]["kind"] == "CPI" and nw["blk"] == "CPI" and "News window until" in nw["warn"] and nw["pct"] == 65, nw)
        js(page, WI, 300)
        nw = js(page, "()=>({blk: newsSatBlock(), n: newsEvents().length})")
        check(f"{tag} 11 CPI later today (outside −60 / +30 min): event listed, no window now", nw["n"] == 1 and nw["blk"] is None, nw)
        js(page, "()=>{ const d = wiDocs[wiCurMon()]; d.assets.XAUUSD.impact = 'MED'; }")
        check(f"{tag} 11 a non-HIGH CPI event gives no window", js(page, "()=>newsEvents().length") == 0)
        js(page, "()=>{ const B = getBook(tdHome()); B.settings.newsEvents = [{date: Calc.wiIctDate(Date.now()), kind:'CPI', time: Calc.wiIctHM(Date.now())}]; wiDocs = {}; }")
        nw = js(page, "()=>({n: newsEvents().length, blk: newsSatBlock(), warn: newsWarnLine()})")
        check(f"{tag} 12 no Weekly Impact → no news window (the hidden hand-entered list is not read)", nw["n"] == 0 and nw["blk"] is None and nw["warn"] == "", nw)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def planform(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; wiDocs = {}; wiLoaded = true; }")
        js(page, "()=>{ switchTab('plan'); pb2OpenAsset('XAUUSD'); }"); page.wait_for_timeout(500)
        st = js(page, "()=>pb2 ? pb2.step : null")
        if st != 2:
            check(f"{tag} 12 Sat plan form reachable", False, st)
            return
        has = js(page, "()=>!!document.querySelector('[data-rk1-nonews]') && document.querySelector('[data-rk1-nonews]').innerText.trim()")
        check(f"{tag} 12 Sat plan form without Weekly Impact: muted 'No news calendar this week'", has == "No news calendar this week", has)
        js(page, WI, 600); js(page, "()=>{ pb2Refresh(); }"); page.wait_for_timeout(200)
        check(f"{tag} 12 with a Weekly Impact doc the line is gone", not js(page, "()=>!!document.querySelector('[data-rk1-nonews]')"))
        check(f"{tag} 12 plan form no horizontal overflow", over(page) <= 0, over(page))
        if SHOT: page.screenshot(path=os.path.join(SHOTS, "planform-%d.png" % w), full_page=False)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


BAD = re.compile(r"(?<![\d.])0\.45\s?%|\b[Ss]tep [1-4] ·|\bSAT step\b|\bstep [1-4] ·")


def labels(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; }")
        seen = {}
        for name, fn in (("today", "switchTab('today'); todayRefresh(true)"), ("plan board", "switchTab('plan')"), ("port", "switchTab('mix')"), ("settings", "openSettings(); document.getElementById('ps1Sec').open = true; document.querySelectorAll('#setOverlay details').forEach(d=>d.open = true)")):
            js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); %s; }" % fn); page.wait_for_timeout(500)
            txt = js(page, "()=>document.body.innerText")
            seen[name] = sorted(set(m.group(0) for m in BAD.finditer(txt)))
        check(f"{tag} 13 no 0.45% / 'Step N ·' / 'SAT step' ladder labels in Today · Plan board · Port · Settings", all(not v for v in seen.values()), seen)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
        sat = js(page, "()=>[...document.querySelectorAll('[data-lr2-rl=\"sat\"] .rw, [data-lr2-rl=\"sat\"] .rp')].map(e=>e.textContent.trim())")
        check(f"{tag} 13 Today SAT line starts with the value (0.2%), not 'step n'", sat and all(re.match(r"^0\.2(0)?%", x) for x in sat), sat)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); }")
        # a changed value shows up everywhere without a hard-coded leftover
        js(page, "()=>{ sh().riskPerIdea = {compTotal:1.3, compFirst:0.7, mom:0.55, sat:0.35}; rk1Sync(); re1Cache = {}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        t = js(page, "()=>document.body.innerText")
        rl = js(page, "()=>document.querySelector('[data-lr2-rl=sat]').innerText + ' ' + document.querySelector('[data-lr2-rl=mom]').innerText")
        check(f"{tag} 13 Today follows a new value (SAT 0.35%) · weekly caps 4 × value (Momentum 2.2%, Sat 1.4%)", "0.35%" in t and (w <= 600 or ("1.4" in rl and "2.2%" in rl)), rl)
        nb = js(page, "()=>(typeof bdNew === 'function') ? bdNew().map(o=>o[3]) : null")
        check(f"{tag} 13 New plan popup subtitles read the values", nb and nb[0].startswith("0.55%") and nb[1].startswith("0.70–1.30%") and nb[2].endswith("0.35%"), nb)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def oldplan(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ serverConfirmed = true; stateFromServer = true; }")
        before = js(page, "()=>JSON.stringify(re1Src ? Object.keys(re1Src()).length : 0)")
        q0 = js(page, "()=>JSON.stringify(Object.keys(state.books ? state.books : {}).length ? 0 : [...(state.trades||[]), ...(coreCardsList||[])].map(t=>[t.id, t.qty, t.sl]))")
        js(page, "()=>{ sh().riskPerIdea = {compTotal:0.6, compFirst:0.5, mom:0.2, sat:0.1}; rk1Sync(); re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(400)
        q1 = js(page, "()=>JSON.stringify(Object.keys(state.books ? state.books : {}).length ? 0 : [...(state.trades||[]), ...(coreCardsList||[])].map(t=>[t.id, t.qty, t.sl]))")
        check(f"{tag} 14 changing the risk values never rewrites a saved trade / card (qty, stop unchanged)", q0 == q1, [q0[:80], q1[:80]])
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 800)):
            settings(pw, w, h); hidden(pw, w, h); today(pw, w, h); planform(pw, w, h); labels(pw, w, h); oldplan(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY rk1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
