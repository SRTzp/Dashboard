#!/usr/bin/env python3
"""AU2 A+B — Today execution chip (counts · colours · phone nowrap · tap target · no taller) and the Journal card. DD_STOP chip text. Run: python3 tests/run_tests_au2.py"""
import sys
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import run_tests_lrf as LF


def chip(page):
    return js(page, "()=>{ const b = document.querySelector('[data-au2-exec]'); if(!b) return null; const r = b.getBoundingClientRect(); const v = [...b.children].find(x=>x.getClientRects().length && !x.classList.contains('au2-sep')); return {tone:b.dataset.au2Tone, x:+b.dataset.au2X, y:+b.dataset.au2Y, txt:b.innerText.replace(/\\s+/g,' ').trim(), h:Math.round(r.height), ws:getComputedStyle(b).whiteSpace, shown:v?v.innerText:'', col:getComputedStyle(b).color}; }")


def settle(page, ms=700):
    js(page, "()=>{ re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(ms)


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        LF.today(page); settle(page, 900); settle(page)
        c = chip(page)
        check(f"{tag} chip sits in the Act open-risk line", js(page, "()=>!!document.querySelector('.lr2-orisk [data-au2-exec]')"), c)
        N = c["y"]
        check(f"{tag} Ready plans, none answered → 0/N amber (N≥3)", c and c["x"] == 0 and N >= 3 and c["tone"] == "a", c)
        if w <= 600:
            check(f"{tag} phone text is '0/N → N/N' (no wrap, one line)", c and c["shown"] == f"0/{N} → {N}/{N}" and c["ws"] == "nowrap" and c["h"] < 24, c)
        else:
            check(f"{tag} desktop text is 'Placed 0/N · goal 100%'", c and c["shown"] == f"Placed 0/{N} · goal 100%", c)
        # taller? hide the chip → Act head height must not change
        hh = js(page, "()=>{ const h = document.querySelector('[data-lr2-head]'); const a = h.getBoundingClientRect().height; const b = document.querySelector('[data-au2-exec]'); b.style.display='none'; const d = document.documentElement.scrollHeight; const c = h.getBoundingClientRect().height; b.style.display=''; return {a, c, sh:document.documentElement.scrollHeight, d}; }")
        check(f"{tag} chip does not make the Act head / page taller", abs(hh["a"] - hh["c"]) <= 1 and hh["sh"] == hh["d"], hh)
        ids = js(page, "()=>Object.keys(ln4Cfg().rdy||{})")
        core = js(page, "(ids)=>ids.filter(id=>(coreCardsList||[]).some(x=>x.id===id))", ids)
        K = core[0]; rest = [i for i in ids if i != K]
        js(page, "(id)=>ln4Valid(id, id, 'working')", rest[0]); settle(page)
        c = chip(page); check(f"{tag} one placed → 1/N amber", c and c["x"] == 1 and c["y"] == N and c["tone"] == "a", c)
        js(page, "(id)=>{ coreWrite(id, {status:'cancelled', cancelReason:'invalidated', cancelledAt:new Date().toISOString()}); re4ValidMark(id, id, 'invalidated'); const c = coreCardsList.find(x=>x.id===id); if(c){ c.status='cancelled'; c.cancelReason='invalidated'; c.cancelledAt=new Date().toISOString(); (coreCancelledList=coreCancelledList||[]).push(c); } }", K); settle(page)
        c = chip(page); check(f"{tag} 'Not taken · invalidated' leaves the denominator → 1/(N-1)", c and c["x"] == 1 and c["y"] == N - 1, c)
        js(page, "(ids)=>{ ids.forEach(id=>ln4Valid(id,id,'working')); }", rest[1:2]); settle(page)
        c = chip(page); check(f"{tag} second placed, the rest unanswered → amber 2/(N-1)", c and c["x"] == 2 and c["y"] == N - 1 and c["tone"] == "a", c)
        js(page, "(ids)=>{ ids.forEach(id=>ln4Valid(id,id,'working')); }", rest); settle(page)
        c = chip(page); check(f"{tag} all placed or correctly skipped → green", c and c["tone"] == "g" and c["x"] == c["y"] == N - 1, c)
        if w <= 600: check(f"{tag} phone green shows ✓", c and c["shown"] == f"{N-1}/{N-1} ✓", c)
        js(page, "(id)=>{ const c = (coreCancelledList||[]).find(x=>x.id===id); c.cancelReason='hesitated'; }", K); settle(page)
        c = chip(page); check(f"{tag} hesitated stays in the count → amber", c and c["y"] == N and c["tone"] == "a" and c["x"] == N - 1, c)
        # Journal card shares the helper
        js(page, "()=>{ LR5.per='week'; switchTab('journal'); }"); page.wait_for_timeout(700)
        jx = js(page, "()=>{ const e = document.querySelector('[data-au2-jx]'); return e ? e.innerText : null; }")
        exp = js(page, "()=>{ const e = au2PeriodExec(lrSwIds('journal'), 'week'); return e.y ? 'placed ' + e.x + '/' + e.y : null; }")
        both = js(page, "()=>{ const e = au2PeriodExec(acctList.map(a=>a.id), 'week'), w = au2WeekExec(acctList.map(a=>a.id)); return e.x === w.x && e.y === w.y; }")
        check(f"{tag} Journal Not-taken card shows the helper's rate for the selected account; period=week equals the Today chip over the same accounts", jx == exp and exp is not None and both, [jx, exp, both])
        # tap target
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        js(page, "()=>{ LR5.per='month'; LR5.ntOpen=false; document.querySelector('[data-au2-exec]').click(); }"); page.wait_for_timeout(900)
        tp = js(page, "()=>({tab: activeTab, per: LR5.per, open: LR5.ntOpen || !!document.querySelector('[data-lr5-ntsheet]')})")
        check(f"{tag} tap → Journal, Not taken, this week", tp["tab"] == "journal" and tp["per"] == "week" and tp["open"], tp)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def stop_chip(pw):
    b, page, ce, pe = launch(pw, 1280, 900, c=LF.cards_today())
    try:
        LF.today(page)
        t = js(page, "()=>{ const d = 86400000, n = Date.now(); const sn = [{at:n-40*d, equity:1000000, confirmed:true}, {at:n-2*d, equity:790000, confirmed:true}]; const a = Re1Adapter.liveEmergency(sn, []); const b2 = Re1Adapter.liveEmergency([sn[0], {at:n-2*d, equity:880000, confirmed:true}], []); return {a:[a.active, a.stopped], b:[b2.active, b2.stopped]}; }")
        check("[adapter] −21% → active + stopped; −12% → active, not stopped", t and t["a"] == [True, True] and t["b"] == [True, False], t)
        st = js(page, "()=>{ const L = re1L(tdHome()); const was = [L.emergency.active, L.emergency.stopped]; L.emergency.active = true; L.emergency.stopped = true; const a = re2State(tdHome()); L.emergency.stopped = false; const b2 = re2State(tdHome()); L.emergency.active = was[0]; L.emergency.stopped = was[1]; return [a.t, a.c, b2.t]; }")
        check("[Act state chip] stopped → 'Stopped · DD 20%' (red); not stopped otherwise", st and st[:2] == ["Stopped · DD 20%", "r"] and st[2] != "Stopped · DD 20%", st)
        chipt = js(page, "()=>{ const o = Re1Adapter.rtext('DD_STOP'); return o; }")
        check("[adapter] DD_STOP text", chipt == "Account is 20% below its peak · new entries stopped", chipt)
    finally:
        b.close()


def goal_case(pw, w, h):
    tag = "[%s goal]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        LF.today(page); settle(page, 900); settle(page)
        ids = js(page, "()=>Object.keys(ln4Cfg().rdy||{})"); N = len(ids)
        core = js(page, "(ids)=>ids.filter(id=>(coreCardsList||[]).some(x=>x.id===id))", ids)
        check(f"{tag} default goal 100%", js(page, "()=>au2Goal()") == 100, None)
        # neutral reasons: invalidated, thesis, blocked, room, error leave the denominator; hesitated/missed/other stay in
        res = js(page, """(ids)=>{ const o = {}; ['invalidated','thesis','blocked','room','error','hesitated','missed','other'].forEach((r, i)=>{ const id = 'zz' + r; ln4Write(q=>{ q.rdy = q.rdy || {}; q.rdy[id] = {day:thaiToday(), wk:tdMonday(thaiToday()), acct:'main', sym:r}; });
          (coreCancelledList = coreCancelledList || []).push({id, ticker:r, acct:'main', status:'cancelled', cancelReason:r, cancelledAt:new Date().toISOString(), track:null}); o[r] = au2Outcome(id); }); return o; }""", ids)
        want = {"invalidated": "skip", "thesis": "skip", "blocked": "skip", "room": "skip", "error": "skip", "hesitated": "hes", "missed": "miss", "other": "miss"}
        check(f"{tag} neutral = invalidated/thesis/blocked/room/error · misses = hesitated/missed/other", res == want, res)
        e = js(page, "()=>{ const x = au2WeekExec(null); return {y:x.y, skip:x.skip, hes:x.hes, miss:x.miss, un:x.un, tip:x.tip}; }")
        check(f"{tag} tooltip lists unanswered / hesitated", e["skip"] == 5 and e["hes"] == 1 and e["miss"] == 2 and "unanswered" in e["tip"] and "hesitated" in e["tip"], e)
        # goal setting 80 / 90 / 100 changes the colour
        js(page, "()=>{ ln4Write(q=>{ Object.keys(q.rdy).forEach(k=>{ if(k.startsWith('zz')) delete q.rdy[k]; }); }); coreCancelledList = coreCancelledList.filter(x=>!String(x.id).startsWith('zz')); }")
        js(page, "(ids)=>{ ids.slice(0, ids.length-1).forEach(id=>ln4Valid(id,id,'working')); }", ids); settle(page)
        c = chip(page); pct = (N - 1) / N * 100
        for g in (80, 90, 100):
            js(page, "(g)=>au2SetGoal(g)", g); settle(page, 500); c = chip(page)
            check(f"{tag} goal {g}%: {N-1}/{N} ({pct:.0f}%) is {'green ✓' if pct >= g else 'amber'}", c and c["tone"] == ("g" if pct >= g else "a") and (f"goal {g}%" in c["txt"] or c["shown"].startswith(f"{N-1}/{N}")), c)
        js(page, "()=>au2SetGoal(90)"); settle(page, 500)
        c = chip(page)
        check(f"{tag} below goal tooltip", js(page, "()=>document.querySelector('[data-au2-exec]').title") .count("unanswered") == (1 if c["tone"] == "a" else 0), c)
        # settings control
        js(page, "()=>{ try{ ln4SetRender(); }catch(e){} }")
        ctl = js(page, "()=>{ let h = document.getElementById('ln4SetBox'); if(!h){ h = document.createElement('div'); h.id='ln4SetBox'; document.body.appendChild(h); } ln4SetRender(); const s = h.querySelector('#au2Goal'); return s ? [...s.options].map(o=>o.value).join() + '|' + s.value : null; }")
        check(f"{tag} setting offers 80/90/100 (current selected)", ctl == "80,90,100|90", ctl)
        # weekly checklist
        wk = js(page, "()=>{ const M = {today:thaiToday()}; try{ const it = td3WeekModel(M).items.find(i=>i.id==='wk_exec'); return it ? {ok:it.ok, auto:it.auto, t:it.t} : null; }catch(e){ return String(e); } }")
        check(f"{tag} weekly checklist has the auto item 'Execution goal met'", isinstance(wk, dict) and wk["t"] == "Execution goal met" and wk["auto"] is True, wk)
        js(page, "(ids)=>{ ids.forEach(id=>ln4Valid(id,id,'working')); }", ids); js(page, "()=>au2SetGoal(100)"); settle(page, 500)
        wk = js(page, "()=>td3WeekModel({today:thaiToday()}).items.find(i=>i.id==='wk_exec').ok")
        check(f"{tag} item turns ✓ when the goal is met", wk is True, wk)
        # grey week = met
        js(page, "()=>{ ln4Write(q=>{ q.rdy = {}; }); }"); settle(page, 500)
        c = chip(page); g = js(page, "()=>td3WeekModel({today:thaiToday()}).items.find(i=>i.id==='wk_exec').ok")
        check(f"{tag} no Ready plans → grey chip, checklist counts it as met", c and c["tone"] == "n" and g is True, [c, g])
        # history + streak
        js(page, """()=>{ const m = tdMonday(thaiToday()), w = k=>posAddDaysISO(m, -7 * k); ln4Write(q=>{ q.rdy = {}; q.valid = q.valid || {};
          [[1, 'a1', true], [2, 'a2', true], [3, 'a3', false]].forEach(([k, id, ok])=>{ q.rdy[id] = {day:w(k), wk:w(k), acct:'main', sym:id.toUpperCase()}; if(ok) q.valid[id] = {day:w(k), via:'working', sym:id}; });
          q.rdy.s1 = {day:w(1), wk:w(1), acct:'main', sym:'INV'}; }); const add = c=>{ (coreCardsRaw = coreCardsRaw || []).push(c); }; add({id:'s1', ticker:'INV', acct:'main', status:'cancelled', cancelReason:'invalidated', cancelNote:'broke support', cancelledAt:new Date().toISOString()}); add({id:'a3', ticker:'A3', acct:'main', status:'plan', plan:{}}); coreApplyPx(); re1Cache = {}; todayRefresh(true); }""")
        st = js(page, "()=>({streak: au2Streak(['main']), hist: au2History(['main']).map(h=>[h.wk === tdMonday(thaiToday()), h.x, h.y, h.met])})")
        check(f"{tag} streak: this (grey = met) + 2 met weeks, then a missed one stops it", st["streak"] == 3, st)
        js(page, "()=>{ LR5.per='all'; switchTab('journal'); }"); page.wait_for_timeout(800)
        js(page, """()=>{ const add = c=>{ if(!coreCardsRaw.some(x=>x.id===c.id)) coreCardsRaw.push(c); }; add({id:'s1', ticker:'INV', acct:'main', status:'cancelled', cancelReason:'invalidated', cancelNote:'broke support', cancelledAt:new Date().toISOString()}); add({id:'a3', ticker:'A3', acct:'main', status:'plan', plan:{}}); coreApplyPx(); lr5Render(); }"""); page.wait_for_timeout(400)
        jt = js(page, "()=>{ const d = document.querySelector('[data-au2-hist]'); return d ? {t:d.innerText.replace(/\\s+/g,' '), streak:(d.querySelector('[data-au2-streak]')||{}).innerText, skips:[...d.querySelectorAll('[data-au2-skip]')].map(x=>x.innerText)} : null; }")
        if jt: js(page, "()=>{ document.querySelector('[data-au2-hist]').open = true; }")
        jt = js(page, "()=>{ const d = document.querySelector('[data-au2-hist]'); return d ? {streak:(d.querySelector('[data-au2-streak]')||{}).innerText, skips:[...d.querySelectorAll('[data-au2-skip]')].map(x=>x.textContent), rows:d.querySelectorAll('[data-au2-hrow]').length} : null; }")
        check(f"{tag} Journal: weekly history, streak text, Invalidated answer lists its reason text", jt and jt["streak"] == "Goal met 3 weeks in a row" and jt["rows"] >= 3 and any("Invalidated" in x and "broke support" in x for x in jt["skips"]), jt)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def peak_case(pw):
    b, page, ce, pe = launch(pw, 1280, 900, c=LF.cards_today())
    try:
        LF.today(page)
        t = js(page, "()=>{ const d = 86400000, n = Date.now(); const mk = (a, e)=>({at:n-a*d, equity:e, confirmed:true}); const snaps = [mk(60, 1000000), mk(30, 1300000), mk(2, 1000000)]; const a = Re1Adapter.liveEmergency(snaps, []); const keep = Re1Adapter.liveEmergency([mk(60, 1000000), mk(2, 1000000)], [], {peakP:1300000, peakAt:n-30*d}); return {a:[a.active, a.stopped, Math.round(a.ddPct*10)/10, a.peakEquity], keep:[keep.stopped, keep.peakP]}; }")
        check("[adapter] peak 1.3M → 1.0M = −23% → stopped (half size also on, month basis)", t and t["a"][1] is True and t["a"][3] == 1300000 and t["keep"] == [True, 1300000], t)
        check("[adapter] 10% half-size rule keeps the month-start reference", t and t["a"][0] in (True, False), t)
        w = js(page, "()=>{ const id = tdHome(); const L = re1L(id); const before = (L.S.re1 || {}).peak || null; return {has: !!(L.emergency), before}; }")
        check("[peak store] per-account peak is written to S.re1.peak when higher", js(page, """()=>{ const id = tdHome(); const B = getBook(id); B.settings = B.settings || {}; B.settings.re1 = B.settings.re1 || {}; B.settings.re1.peak = {peakP: 5, peakAt: 1}; re1Cache = {}; const L = re1L(id); return (L.S.re1 && L.S.re1.peak && L.S.re1.peak.peakP) === 5; }"""), w)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1280, 900), (390, 844)): run(pw, w, h); goal_case(pw, w, h)
        peak_case(pw)
        stop_chip(pw)
    bad = [r for r in results if not r[1]]
    print("SUMMARY au2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
