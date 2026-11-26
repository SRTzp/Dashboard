#!/usr/bin/env python3
"""CP1 — Compounder first when the market pulls back · buy zone · 40-week average.
C  Today: Mood MARKET line + 'Pullback' wording · Act group 'Compounder first' (zone → near 40-wk avg → add-on) · normal-market summary line · To do nudge
D  Homework page buy zone (+ helper line + 'use 40-wk avg ±3%') · Watch › Compounder columns (vs 40-wk · Buy zone)
E  iPhone 390 · wording check · screenshots (CP1_SHOTS=1 → docs/screenshots/cp1-*.png)
Engine (pullback + 100/100/75) → tests/cp1_engine_test.js · data job → tests/rs2_selftest.py · J9 journey → tests/run_tests_e2e1.py
Run: python3 tests/run_tests_cp1.py"""
import sys, os, re
from playwright.sync_api import sync_playwright
import hf5_common as H
import cp1_common as C
from re1d_common import js, check, results

SH = bool(os.environ.get("CP1_SHOTS"))
BAD = re.compile(r"downtrend|risk-off|danger", re.I)
ROWS = "()=>[...document.querySelectorAll('[data-cp1-group] [data-cp1-row]')].map(r=>({sym:r.dataset.cp1Row, k:r.dataset.cp1K, t:r.innerText.replace(/\\s+/g,' ').trim(), btn:(r.querySelector('button')||{}).innerText, dark:!!r.querySelector('button:not(.o):not([data-nt1b-sec])')}))"
MOOD = "()=>{ const r=[...document.querySelectorAll('[data-nt1b-row=\"mood\"],[data-nt1b-row=\"market\"]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim()); return r; }"
GRP = "()=>{ const g=document.querySelector('[data-cp1-group]'); return g ? g.innerText.replace(/\\s+/g,' ').trim() : ''; }"


def shot(page, name, w):
    if SH: C.png(page, "cp1-%s-%d" % (name, w))


def set_state(page, spy=-0.02, st=-0.03, eq="green", cr="green"):
    C.market(page, spy, st); C.regime(page, eq, cr); C.today(page)


def run(pw, w):
    tag = "[%d]" % w
    ph = w < 600
    b, page, ce, pe = H.start(pw, w, 900 if w > 600 else 844)
    try:
        C.seed(page)
        page.wait_for_timeout(300)
        # ───── C · Mood card: normal market
        set_state(page, -0.02, -0.03)
        m = js(page, MOOD)
        check(f"{tag} C normal: MARKET line 'SPY −2% … SET −3% … normal' (grey, no Pullback)", any("MARKET" in x and "−2%" in x and "−3%" in x and "normal" in x for x in m) and not any("Pullback" in x for x in m), m)
        check(f"{tag} C normal: no Compounder group", js(page, "()=>document.querySelectorAll('[data-cp1-group]').length") == 0)
        sm = js(page, "()=>{ const e=document.querySelector('[data-cp1-sum]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }")
        check(f"{tag} C normal: ONE summary line at the bottom of Act — 'COMPOUNDER · 1 in buy zone · show ›'", sm == "COMPOUNDER · 1 in buy zone · show ›", sm)
        check(f"{tag} C normal: the summary is the last thing inside Act", js(page, "()=>{ const a=document.querySelector('[data-ln4-act]'); return !!a && a.lastElementChild.hasAttribute('data-cp1-sum'); }"))
        check(f"{tag} C normal: To do has no pullback nudge", js(page, "()=>!document.body.innerText.includes('Market pullback')"))
        shot(page, "today-normal", w) if w == 1440 else None
        page.click("[data-cp1-show]"); page.wait_for_timeout(300)
        op = js(page, "()=>[...document.querySelectorAll('[data-cp1-open] [data-cp1-row]')].map(r=>r.dataset.cp1Row)")
        check(f"{tag} C normal: show › expands the same rows in place (COST)", op == ["COST"], op)
        page.click("[data-cp1-show]"); page.wait_for_timeout(200)
        check(f"{tag} C normal: hide › folds it back", js(page, "()=>document.querySelectorAll('[data-cp1-open]').length") == 0)
        # ───── C · pullback threshold 6.9% vs 7.0%
        set_state(page, -0.069, -0.01)
        check(f"{tag} C SPY −6.9% → no pullback", js(page, "()=>document.querySelectorAll('[data-cp1-group]').length") == 0 and not any("Pullback" in x for x in js(page, MOOD)))
        set_state(page, -0.07, -0.01)
        m = js(page, MOOD)
        check(f"{tag} C SPY −7.0% → pullback: Mood 'Pullback' + 'Compounder size 100%'", any("Pullback" in x and "Compounder size 100%" in x for x in m), m)
        check(f"{tag} C pullback: MARKET line names SPY −7% · SET −1%" + ("" if ph else " · HYG/IEI green"), any(x.startswith("MARKET") and "SPY" in x and "−7%" in x and "SET −1%" in x and (ph or "HYG/IEI green" in x) for x in m), m)
        # SET only → Thai stocks only
        set_state(page, -0.01, -0.08)
        r = js(page, ROWS)
        check(f"{tag} C SET −8% only → pullback for Thai stocks only (ADV, no US rows)", [x["sym"] for x in r] == ["ADV.BK"] and any("Pullback" in x for x in js(page, MOOD)), r)
        # ───── C · regime signals
        set_state(page, -0.01, -0.01, "green", "red")
        m = js(page, MOOD)
        check(f"{tag} C exactly one red signal → pullback, Compounder size stays 100%", any("Pullback" in x and "Compounder size 100%" in x for x in m) and js(page, "()=>document.querySelectorAll('[data-cp1-group]').length") == 1, m)
        set_state(page, -0.01, -0.01, "red", "red")
        check(f"{tag} C both red alone (indexes flat) → not 'one red' → no Pullback pill", not any("Pullback" in x for x in js(page, MOOD)))
        set_state(page, -0.09, -0.06, "red", "red")
        m = js(page, MOOD)
        check(f"{tag} C both red + SPY −9% → 'Compounder size 75% · buy in steps'", any("Compounder size 75%" in x and "buy in steps" in x for x in m) or (ph and any("Compounder size 75%" in x for x in m)), m)
        # ───── C · Act group order + buttons
        set_state(page, -0.09, -0.06)
        r = js(page, ROWS); g = js(page, GRP)
        check(f"{tag} C group header 'COMPOUNDER FIRST · market pullback · 2 to look at', above Enter", g.upper().startswith("COMPOUNDER FIRST MARKET PULLBACK · 2 TO LOOK AT") and js(page, "()=>{ const a=document.querySelector('[data-cp1-group]'), e=document.querySelector('[data-re2-col=\"enter\"]'); return !e || !!(a.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING); }"), g)
        check(f"{tag} C rows: 1 in buy zone (COST) → 2 near the 40-wk avg (MSFT)", [x["sym"] for x in r] == ["COST", "MSFT"] and [x["k"] for x in r] == ["zone", "near"], r)
        check(f"{tag} C row 1 'Now 905 · zone 880–920 · 40-wk avg 912 (−1%) · homework ✓' + dark 'Make plan ›'", "Now 905 · zone 880–920" in r[0]["t"] and "40-wk avg 912 (−1%)" in r[0]["t"] and "homework ✓" in r[0]["t"] and r[0]["btn"] == "Make plan ›" and r[0]["dark"], r[0])
        check(f"{tag} C row 2 near the avg: 'Now 402 · 40-wk avg 398 (+1%) · no zone set · homework 1 of 3' + white 'Homework ›'", "Now 402" in r[1]["t"] and "398 (+1%)" in r[1]["t"] and "no zone set" in r[1]["t"] and "homework 1 of 3" in r[1]["t"] and r[1]["btn"] == "Homework ›" and not r[1]["dark"], r[1])
        check(f"{tag} C above-zone (V +12%) and no-data stocks are not listed", not any(x["sym"] in ("V", "NODATA") for x in r))
        dk = js(page, "()=>[...document.querySelectorAll('[data-ln4-act] .re2-row .btn')].filter(b=>b.getClientRects().length && getComputedStyle(b).backgroundColor==='rgb(20, 21, 24)').length")
        check(f"{tag} C exactly one dark button in Act (the top Compounder row); Place buttons below are plain", dk == 1, dk)
        # buttons act
        page.click("[data-cp1-row=\"COST\"] [data-cp1-btn=\"plan\"]"); page.wait_for_timeout(600)
        check(f"{tag} C Make plan › opens the plan form for COST", js(page, "()=>{ const t=document.getElementById('cnTicker'); return !!t && /COST/i.test(t.value); }"), js(page, "()=>document.body.innerText.slice(0,200)"))
        js(page, "()=>{ try{ coreSheetClose(); }catch(e){} }"); C.today(page)
        page.click("[data-cp1-row=\"MSFT\"] [data-cp1-btn=\"hw\"]"); page.wait_for_timeout(600)
        check(f"{tag} C Homework › opens the Homework page", js(page, "()=>!!document.querySelector('[data-hw1-page=\"MSFT\"]')"))
        C.today(page)
        js(page, "()=>{ switchTab('watch'); wl1SegGo('ladder'); renderWatchlist(); }"); page.wait_for_timeout(500)
        st = js(page, "()=>({hw:document.querySelectorAll('[data-hw1-page]').length, list:document.querySelectorAll('[data-wl1-row]').length, hwSym:hwSym, vis:[...document.querySelectorAll('[data-hw1-page]')].filter(e=>e.getClientRects().length).length})")
        check(f"{tag} E leaving a Homework page for Today and coming back to Watch shows the list only (no Homework header under / instead of the list)", st["hw"] == 0 and st["vis"] == 0 and st["list"] >= 4 and st["hwSym"] == "", st)
        C.today(page)
        # planned stock → its plan row, not a second row
        js(page, "()=>coreWrite('cp1plan', {acct:'main', ticker:'COST', market:'US', strategy:'L', status:'plan', plan:{entry:905, stop:860, ready:true, ps1:{rows:[{px:905, qty:20}]}}})"); page.wait_for_timeout(500); C.today(page)
        r = js(page, ROWS)
        check(f"{tag} C a planned stock shows its plan row (it leaves the Compounder group; no duplicate row)", [x["sym"] for x in r] == ["MSFT"] and js(page, "()=>wl1Status(wlItemOf('COST')).k") == "plan", r)
        js(page, "()=>coreWrite('cp1plan', {status:'cancelled'})"); page.wait_for_timeout(300)
        # cap 5 + "+n ›"
        extra = {("Z%d" % i): ("US", 100.0, 100.0, 120.0, dict(C.HWDONE, buyZone={"lo": 95, "hi": 105})) for i in range(5)}
        C.seed(page, extra); C.market(page, -0.09, -0.06); C.today(page)
        r = js(page, ROWS); more = js(page, "()=>{ const e=document.querySelector('[data-cp1-more]'); return e ? e.innerText.trim() : null; }")
        check(f"{tag} C at most 5 rows + '+n ›'", len(r) == 5 and more and re.fullmatch(r"\+\d+ ›", more), [len(r), more])
        n0 = len(r); page.click("[data-cp1-more]"); page.wait_for_timeout(300)
        check(f"{tag} C '+n ›' shows the rest in place", len(js(page, ROWS)) > n0)
        for i in range(5): js(page, "(t)=>wlCol().doc(t).delete()", "Z%d" % i)
        page.wait_for_timeout(400); js(page, "()=>Promise.all([0,1,2,3,4].map(i=>db.collection('users').doc(uid).collection('prices').doc('Z'+i).delete()))"); js(page, "()=>{ cp1All=false; }")
        # add-on row (synthetic engine row → same builder): zone → near → add-on, never two rows for one stock
        ao = js(page, """()=>{ const S = cp1State(); const w = wlItemOf('COST'); const fake = [{it:{tag:'COMP', kind:'core', sym:'V', id:'x1', acct:'main'}, o:{k:'addon', fn:'void 0'}},{it:{tag:'MMT', kind:'core', sym:'AAPL', id:'x2'}, o:{k:'addon', fn:'void 0'}}];
          const B = cp1Build(fake); return B.rows.map(r=>r.k + ':' + r.it.ticker); }""")
        check(f"{tag} C order zone → near → add-on (V holding); a Momentum add-on is not here", ao == ["zone:COST", "near:MSFT", "addon:V"], ao)
        # ───── C · To do nudge
        set_state(page, -0.09, -0.06)
        td = js(page, "()=>[...document.querySelectorAll('[data-ln4-todo=\"cp1:hw\"]')].map(e=>({t:e.innerText.replace(/\\s+/g,' ').trim(), c:e.dataset.ln4C}))")
        check(f"{tag} C pullback → To do 'Market pullback · finish homework on 2 Compounder stocks ›' (amber)", len(td) == 1 and td[0]["t"].startswith("Market pullback · finish homework on 2 Compounder stocks") and td[0]["c"] == "a", td)
        shot(page, "today-pullback", w)
        js(page, "()=>cp1HwGo()"); page.wait_for_timeout(500)
        st = js(page, "()=>({tab:activeTab, trk:wl1Trk, f:wl5Filter})")
        check(f"{tag} C the nudge opens Watch › Compounder · filter 'Needs homework'", st["tab"] == "watch" and st["trk"] == "ladder" and st["f"] == "need", st)
        js(page, "()=>wl5FilterSet('all')")
        set_state(page, -0.02, -0.03)
        check(f"{tag} C normal market → the nudge is gone", js(page, "()=>document.querySelectorAll('[data-ln4-todo=\"cp1:hw\"]').length") == 0)
        # ───── wording
        set_state(page, -0.09, -0.06)
        txt = " | ".join(js(page, MOOD) + [js(page, GRP)])
        check(f"{tag} E wording: no 'downtrend / risk-off / danger' in the Mood pullback lines or the Compounder group", not BAD.search(txt), txt)
        # ───── D · Watch columns
        js(page, "()=>{ switchTab('watch'); wl1SegGo('ladder'); renderWatchlist(); }"); page.wait_for_timeout(600)
        hd = js(page, "()=>[...document.querySelectorAll('.wl5-th .lbl')].map(e=>e.innerText.trim().toUpperCase())")
        check(f"{tag} D Watch › Compounder header has 'VS 40-WK' + 'BUY ZONE'" if not ph else f"{tag} D phone: header hidden (line 2 carries the numbers)", ph or ("VS 40-WK" in hd and "BUY ZONE" in hd), hd)
        rows = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-wl1-row]')].map(r=>[r.dataset.sym, {vs:(r.querySelector('[data-cp1-vs]')||{}).innerText||'', bz:(r.querySelector('[data-cp1-bz]')||{}).innerText||'', z:(r.querySelector('[data-cp1-bz]')||{}).dataset?.cp1Bz||'', l2:(r.querySelector('.l2')||{}).innerText||''}]))")
        if not ph:
            check(f"{tag} D COST: vs 40-wk −1% · 'in 880–920' (green pill)", rows["COST"]["vs"] == "−1%" and rows["COST"]["bz"] == "in 880–920" and rows["COST"]["z"] == "in" and rows["ADV.BK"]["bz"] == "above 200–220", rows["COST"])
            check(f"{tag} D V: +12% · 'above 250–265' (grey) · MSFT '—' · NODATA '—' '—'", rows["V"]["bz"] == "above 250–265" and rows["V"]["vs"] == "+12%" and rows["MSFT"]["bz"] == "—" and rows["NODATA"]["vs"] == "—" and rows["NODATA"]["bz"] == "—", rows)
            col = js(page, "()=>{ const g=document.querySelector('[data-sym=\"COST\"] .cp1-bz'), a=document.querySelector('[data-sym=\"V\"] .cp1-bz'); return [getComputedStyle(g).backgroundColor, getComputedStyle(a).backgroundColor]; }")
            check(f"{tag} D zone pill: green when inside · grey otherwise", col[0] == "rgb(230, 244, 238)" and col[1] == "rgb(240, 241, 244)", col)
            check(f"{tag} D Momentum list has no new columns", (js(page, "()=>{ wl1SegGo('winner'); renderWatchlist(); return document.querySelectorAll('.wl5-th.cp1c, [data-cp1-vs]').length; }") == 0))
            js(page, "()=>{ wl1SegGo('ladder'); renderWatchlist(); }")
        else:
            check(f"{tag} D phone line 2: 'vs 40-wk −1% · in zone' (COST) · 'vs 40-wk +12% · above zone' (V)", "vs 40-wk −1% · in zone" in rows["COST"]["l2"].replace("\n", " ") and "vs 40-wk +12% · above zone" in rows["V"]["l2"].replace("\n", " "), rows)
        page.wait_for_timeout(300); shot(page, "watch-comp", w)
        # ───── D · Homework page: buy zone
        js(page, "()=>hwGo('MSFT')"); page.wait_for_timeout(700)
        prog0 = js(page, "()=>(document.querySelector('[data-hw1-prog]')||{}).innerText")
        zb = js(page, "()=>{ const z=document.querySelector('[data-cp1-zonebox]'); return z ? {t:z.innerText.replace(/\\s+/g,' '), fs:[...z.querySelectorAll('input')].map(i=>getComputedStyle(i).fontSize), after:!!document.querySelector('[data-hw1-f=\"exit\"]') && !!(document.querySelector('[data-hw1-f=\"exit\"]').compareDocumentPosition(z) & Node.DOCUMENT_POSITION_FOLLOWING)} : null; }")
        check(f"{tag} D Homework page: optional 'Buy zone' under field 3, inputs 16px", zb and "Buy zone" in zb["t"] and "optional" in zb["t"] and zb["after"] and zb["fs"] == ["16px", "16px"], zb)
        check(f"{tag} D helper line 'Now 402 · 40-wk avg 398 · 52-wk high 460 (−13%) · use 40-wk avg ±3%'", zb and "Now 402 · 40-wk avg 398 · 52-wk high 460 (−13%) · use 40-wk avg ±3%" in zb["t"], zb)
        page.click("[data-cp1-use]"); page.wait_for_timeout(500)
        v = js(page, "()=>[...document.querySelectorAll('[data-cp1-zone]')].map(i=>i.value)")
        bz = js(page, "()=>wlItemOf('MSFT').buyZone")
        check(f"{tag} D tap fills 40-wk avg ±3% (386.06 – 409.94) and saves it on the Watch item", v == ["386.06", "409.94"] and bz == {"lo": 386.06, "hi": 409.94}, [v, bz])
        stored = js(page, "async ()=>{ const d = await wlCol().doc('MSFT').get(); return d.data().buyZone; }")
        check(f"{tag} D stored as buyZone:{{lo,hi}} in the database", stored == {"lo": 386.06, "hi": 409.94}, stored)
        check(f"{tag} D the zone is not one of the 3 required answers (progress unchanged)", js(page, "()=>(document.querySelector('[data-hw1-prog]')||{}).innerText") == prog0, prog0)
        page.fill("[data-cp1-zone=\"lo\"]", "420"); page.fill("[data-cp1-zone=\"hi\"]", "410"); page.locator("[data-cp1-zone=\"hi\"]").blur(); page.wait_for_timeout(300)
        check(f"{tag} D To smaller than From → message, nothing saved", "To must be at least From" in (js(page, "()=>document.querySelector('[data-cp1-zmsg]').innerText")) and js(page, "()=>wlItemOf('MSFT').buyZone") == {"lo": 386.06, "hi": 409.94})
        page.fill("[data-cp1-zone=\"lo\"]", "395"); page.fill("[data-cp1-zone=\"hi\"]", "405"); page.locator("[data-cp1-zone=\"hi\"]").blur(); page.wait_for_timeout(300)
        shot_zone = True
        if SH:
            js(page, "()=>{ const z=document.querySelector('[data-cp1-zonebox]'); z.scrollIntoView({block:'center'}); }"); page.wait_for_timeout(300)
            shot(page, "buyzone", w)
        mk = js(page, "()=>document.querySelector('[data-hw1-page=\"MSFT\"]') ? 1 : 0")
        # Today alert: MSFT is now inside its zone → first row group 'In buy zone'
        js(page, "()=>{ hwBack(true); }"); page.wait_for_timeout(300)
        set_state(page, -0.09, -0.06)
        r = js(page, ROWS)
        check(f"{tag} D buy zone saved → Today shows MSFT 'In buy zone' (zone 395–405)", any(x["sym"] == "MSFT" and x["k"] == "zone" and "zone 395–405" in x["t"] for x in r), r)
        check(f"{tag} D zone rows come before near-average rows", [x["k"] for x in r] == sorted([x["k"] for x in r], key=lambda k: {"zone": 0, "near": 1, "addon": 2}[k]), r)
        # clear → removed
        js(page, "()=>hwGo('MSFT')"); page.wait_for_timeout(500)
        page.fill("[data-cp1-zone=\"lo\"]", ""); page.fill("[data-cp1-zone=\"hi\"]", ""); page.locator("[data-cp1-zone=\"hi\"]").blur(); page.wait_for_timeout(300)
        check(f"{tag} D both fields empty → zone removed", js(page, "()=>wlItemOf('MSFT').buyZone") is None)
        js(page, "()=>{ hwBack(true); }")
        # Momentum stock: no buy zone box
        js(page, "()=>wlCol().doc('AAPL').set({ticker:'AAPL', market:'US', port:'core', added_at:'2026-10-01T00:00:00Z', ladder_watch:false, ladder_watch_set:true})"); page.wait_for_timeout(400)
        js(page, "()=>hwGo('AAPL')"); page.wait_for_timeout(500)
        check(f"{tag} D Momentum homework page has no Buy zone box", js(page, "()=>document.querySelectorAll('[data-cp1-zonebox]').length") == 0)
        js(page, "()=>{ hwBack(true); }")
        # ───── E · iPhone
        set_state(page, -0.09, -0.06)
        shot(page, "today-pullback-final", w) if False else None
        if ph:
            ov = js(page, "()=>document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
            check(f"{tag} E no horizontal overflow", ov)
            lay = js(page, """()=>{ const rows=[...document.querySelectorAll('[data-cp1-group] [data-cp1-row]')]; return rows.map(r=>{ const b=r.querySelector('.re2-btns .btn').getBoundingClientRect(), c=r.getBoundingClientRect(); return {w:Math.round(b.width), h:Math.round(b.height), full:b.width >= c.width - 30, inside:c.right <= innerWidth + 1, chip:!!(r.querySelector('.chip') && r.querySelector('.chip').getClientRects().length)}; }); }""")
            check(f"{tag} E Compounder rows stack: full-width button ≥ 44px, chip visible, inside the card", lay and all(x["full"] and x["h"] >= 44 and x["inside"] and x["chip"] for x in lay), lay)
            cut = js(page, "()=>[...document.querySelectorAll('[data-cp1-group] *, [data-nt1b-row=\"mood\"] *, [data-nt1b-row=\"market\"] *')].filter(e=>e.getClientRects().length && /…|\\.\\.\\./.test(e.childNodes.length===1 && e.firstChild.nodeType===3 ? e.firstChild.nodeValue : '')).map(e=>e.innerText)")
            check(f"{tag} E no '…' in the Compounder group or the Mood lines", not cut, cut)
            m = js(page, MOOD)
            check(f"{tag} E Mood is two short lines: 'Pullback · Compounder size 100%' + 'SPY −9% · SET −6%'", any("Pullback" in x and "Compounder size 100%" in x and "good time" not in x for x in m) and any(x == "MARKET SPY −9% · SET −6%" for x in m), m)
            clip = js(page, "()=>[...document.querySelectorAll('[data-cp1-group] .num, [data-cp1-group] .l1')].filter(e=>e.scrollWidth > e.clientWidth + 1).map(e=>e.innerText)")
            check(f"{tag} E nothing runs past the card edge", not clip, clip)
            shot(page, "today-pullback", w)
        else:
            shot(page, "today-pullback", w)
        check(f"{tag} no page errors / console errors", not pe and not [x for x in ce if "favicon" not in x], (pe + ce)[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w in (1440, 390):
            try: run(pw, w)
            except Exception as e:
                import traceback; traceback.print_exc(); check("[%d] suite crashed: %s" % (w, str(e)[:160]), False, str(e)[:400])
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY cp1: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
