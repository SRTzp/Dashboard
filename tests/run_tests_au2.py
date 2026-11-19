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
            check(f"{tag} phone text is '0/N' (no wrap, one line)", c and c["shown"] == f"0/{N}" and c["ws"] == "nowrap" and c["h"] < 24, c)
        else:
            check(f"{tag} desktop text is 'Placed 0/N this week'", c and c["shown"] == f"Placed 0/{N} this week", c)
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


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1280, 900), (390, 844)): run(pw, w, h)
        stop_chip(pw)
    bad = [r for r in results if not r[1]]
    print("SUMMARY au2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
