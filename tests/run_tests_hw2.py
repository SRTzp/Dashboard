#!/usr/bin/env python3
"""HW2 — A: one way into Homework (hwGo) · B: your thesis fitted to holding time (Momentum / Compounder, chips) · C: Edit chips.
Run: python3 tests/run_tests_hw2.py   (HW2_SHOTS=1 writes docs/screenshots/hw2-*.png)"""
import sys, os, re, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results, launch
import hw1_common as H
import run_tests_pc2 as P

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
SHOTS_ON = bool(os.environ.get("HW2_SHOTS"))
ON_PAGE = "()=>{ const p = document.querySelector('[data-hw1-page]'); return p ? p.dataset.hw1Page : null; }"
FOCUS = "()=>{ const a = document.activeElement; const f = a && a.closest ? a.closest('[data-hw1-f]') : null; return f ? f.dataset.hw1F : null; }"
HL = "()=>{ const f = document.querySelector('[data-hw1-page] .hw2-hl'); return f ? f.dataset.hw1F : null; }"
FULLVIEW = "()=>!!(wl5FullSym && !hwSym)"


def shot(page, name):
    if not SHOTS_ON: return
    os.makedirs(SHOTS, exist_ok=True)
    vp = page.viewport_size
    if vp["width"] >= 1024: page.set_viewport_size({"width": vp["width"], "height": 1150}); page.wait_for_timeout(250)
    page.screenshot(path=os.path.join(SHOTS, name + ".png"))
    if vp["width"] >= 1024: page.set_viewport_size(vp)


def landed(page, sym, first, narrow):
    """On the Homework page for `sym`, the first missing required field is the one in focus / outlined; phone: My thesis active."""
    on = js(page, ON_PAGE) == sym
    f = js(page, HL) if narrow else (js(page, FOCUS) or js(page, HL))
    mine = js(page, "()=>{ const p = document.querySelector('[data-hw1-page]'); return p ? p.dataset.hw1Show : null; }") == "mine" if narrow else True
    return on and f == first and mine and not js(page, FULLVIEW), (on, f, mine)


def part_a(pw, w, h):
    tag = "[%s]" % w; narrow = w < 1024
    # ---- Watch row + Watch detail (Momentum AAPL, Compounder COST)
    b, page, pe = H.open_hw(pw, w, h)
    try:
        for sym in ("AAPL", "COST"):
            first = js(page, "(s)=>{ const it = wlItemOf(s); return hw1Prog(it, hw1Vals(it)).miss[0]; }", sym)
            js(page, "()=>{ wlSetView('wl'); wlBack && wlBack(); }"); page.wait_for_timeout(200)
            js(page, "(s)=>{ wl1SegGo(wl1TrkOf(wlItemOf(s))); wlOpen(s); }", sym); page.wait_for_timeout(300)
            # detail button (Do homework ›)
            btn = page.locator('[data-lr5-main]').first
            check(f"{tag} A {sym} detail main button is the homework entry", btn.count() == 1 and "omework" in btn.inner_text(), btn.inner_text() if btn.count() else None)
            btn.click(); page.wait_for_timeout(500)
            ok, d = landed(page, sym, first, narrow); check(f"{tag} A {sym} Watch detail › Homework page, first missing field ({first})", ok, d)
            js(page, "()=>hwBack()"); page.wait_for_timeout(300)
            # list row Homework › (desktop table only has it as a cell button)
            row = page.locator(f'[data-lr5-row][data-sym="{sym}"] [onclick*="wl5Hw"], [data-sym="{sym}"] [data-lr5-hw]').first
            if row.count() and row.is_visible():
                row.click(); page.wait_for_timeout(500)
                ok, d = landed(page, sym, first, narrow); check(f"{tag} A {sym} Watch row Homework › lands on {first}", ok, d)
                js(page, "()=>hwBack()"); page.wait_for_timeout(300)
        # no entry reaches wlOpen(sym, sub) / wl5Full: instrument and press the remaining entry functions
        js(page, "()=>{ window.__wo = []; const o = window.wlOpen; window.wlOpen = function(s, sub){ window.__wo.push([s, sub || '']); return o.apply(this, arguments); }; const f = window.wl5Full; window.wl5Full = function(){ window.__wo.push(['FULL']); return f.apply(this, arguments); }; }")
        for sym in ("AAPL", "COST"):
            for fn in ("hwGo('%s')", "wl5Hw('%s')", "wl1Fill('%s')", "td3HwGo('%s','W','why')", "td3HwGo('%s','C','')", "bdAddThesis('%s')", "ftGo('%s')"):
                js(page, "()=>{ window.__wo = []; }"); js(page, "(c)=>{ switchTab('today'); }", None); page.wait_for_timeout(100)
                js(page, "(c)=>eval(c)", fn % sym); page.wait_for_timeout(350)
                wo = js(page, "()=>window.__wo")
                check(f"{tag} A {fn % sym} → Homework page, no wlOpen(sym, sub) / wl5Full", js(page, ON_PAGE) == sym and all(x[0] != 'FULL' and not x[1] for x in wo), [js(page, ON_PAGE), wo])
        if SHOTS_ON and narrow:   # hw2-from-today (390): landed on the first missing field of My thesis
            js(page, "()=>{ switchTab('today'); hwGo('COST'); }"); page.wait_for_timeout(700); shot(page, "hw2-from-today-390")
            js(page, "()=>hwBack()"); page.wait_for_timeout(300)
        # old full-thesis view only from ⋯
        js(page, "()=>{ hwGo('COST'); hwBack(); wlOpen('COST'); wlMenu = 'COST'; renderWatchlist(); }"); page.wait_for_timeout(300)
        mi = js(page, "()=>[...document.querySelectorAll('[role=menuitem]')].map(x=>x.innerText.trim())") or []
        check(f"{tag} A ⋯ keeps Full thesis + News & catalysts", "Full thesis" in mi and "News & catalysts" in mi, mi)
        # Back from Today → Today, same scroll
        js(page, "()=>{ wlMenu=''; hwBack(); switchTab('today'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.body.style.minHeight='3000px'; window.scrollTo(0, 400); }"); page.wait_for_timeout(150)
        y0 = js(page, "()=>Math.round(window.scrollY)")
        js(page, "()=>hwGo('COST')"); page.wait_for_timeout(500)
        check(f"{tag} A hwGo from Today opens the Homework page on the Watch tab", js(page, ON_PAGE) == "COST" and js(page, "()=>activeTab") == "watch")
        js(page, "()=>hwBack()"); page.wait_for_timeout(700)
        y1 = js(page, "()=>Math.round(window.scrollY)")
        check(f"{tag} A Back → Today tab, same scroll ({y0})", js(page, "()=>activeTab") == "today" and abs(y1 - y0) <= 2, [js(page, "()=>activeTab"), y0, y1])
        js(page, "()=>{ switchTab('watch'); hwGo('COST'); }"); page.wait_for_timeout(400); js(page, "()=>hwBack()"); page.wait_for_timeout(300)
        check(f"{tag} A Back from Watch → Watch list", js(page, "()=>activeTab") == "watch" and js(page, ON_PAGE) is None)
    finally:
        b.close()
    # ---- Today Manage row · Plan card fix · Place-order ADDON_THESIS fix · drawer Open ›
    trades = [P.tr_held("MOMH", 40, 100, 90, "hm1"), P.tr_held("CMPH", 10, 100, 90, "hc1")]
    def cards(cs):
        cs["hMOMH"] = P.held_card("MOMH", 40, 100, 90, "hm1", [{"px": 100, "qty": 40}, {"px": 110, "qty": 12, "createdAt": "2026-11-18T00:00:00.000Z"}], price=102, lots_date="2026-09-01")
        cs["cmh"] = P.held_card("CMPH", 10, 100, 90, "hc1", [{"px": 100, "qty": 10}], track="ladder", price=101)
    b, page, ce, pe = P.run_with(pw, w, h, cards, trades, tab="today")
    try:
        for t in ("CMPH", "MOMH"): P.hw(page, t, False)
        js(page, "()=>{ switchTab('today'); re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(500)
        btn = page.locator('[data-re2-btn=hw]').first
        if btn.count():
            rs = js(page, "()=>document.querySelector('[data-re2-btn=hw]').closest('.re2-row').dataset.re2Row")
            btn.click(); page.wait_for_timeout(500)
            check(f"{tag} A Today Manage row `Homework → unlocks adds ›` → Homework page ({rs})", js(page, ON_PAGE) and js(page, ON_PAGE) in str(rs), [rs, js(page, ON_PAGE)])
        else: check(f"{tag} A Today Manage row button exists", False, "no [data-re2-btn=hw]")
        js(page, "()=>{ if(hwSym) hwBack(); switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        g = js(page, "()=>{ const x = pc2Gate(bdById('hMOMH')); return x && x.fix ? x.fix.fn : null; }")
        check(f"{tag} A Place order ADDON_THESIS fix is hwGo", bool(g) and g.startswith("hwGo("), g)
        if g:
            js(page, "(c)=>eval(c)", g); page.wait_for_timeout(500)
            check(f"{tag} A ADDON_THESIS fix → Homework page", js(page, ON_PAGE) == "MOMH", js(page, ON_PAGE))
        js(page, "()=>{ if(hwSym) hwBack(); switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        src = js(page, "()=>[pc2Hw.toString(), (typeof bdCardHtml!=='undefined'?bdCardHtml.toString():'')].join('\\n')") or ""
        check(f"{tag} A no td3HwGo left in the Plan board / drawer markup", "td3HwGo" not in src)
        js(page, "(k)=>bdOpen(k)", "hMOMH"); page.wait_for_timeout(400)
        ob = page.locator("[data-pc2-hwopen]").first
        if ob.count():
            ob.click(); page.wait_for_timeout(500)
            check(f"{tag} A Plan drawer HOMEWORK Open › → Homework page", js(page, ON_PAGE) == "MOMH", js(page, ON_PAGE))
        js(page, "()=>{ try{ bdClose(); }catch(e){} }")
    finally:
        b.close()


TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
PILLS = "()=>[...document.querySelectorAll('[data-hw2-pill]')].map(p=>({k:p.dataset.hw2Pill, t:p.innerText.replace(/\\s+/g,' ').trim(), cls:p.className}))"
SCR = """([rows])=>{ rs2.rows = rows; rs2.state = 'ok'; rs2.at = Date.now(); }"""


def plus_days(page, n):
    return js(page, "(n)=>{ const d = new Date(thaiToday() + 'T00:00:00Z'); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }", n)


def box(page, k): return js(page, "(k)=>document.querySelector('[data-hw1-ta=\"'+k+'\"]').value", k)
def chip(page, k, txt):
    return page.locator('[data-hw2-chip="%s"][data-txt="%s"]' % (k, txt)).first
def chip_on(page, k, txt):
    return js(page, "([k,t])=>{ const c = [...document.querySelectorAll('[data-hw2-chip=\"'+k+'\"]')].find(x=>x.dataset.txt===t); return c ? c.classList.contains('on') : null; }", [k, txt])


def part_b(pw, w, h):
    tag = "[%s]" % w; narrow = w < 1024
    b, page, pe = H.open_hw(pw, w, h)
    try:
        # ---- header + hold text + size cap per type
        H.go(page, "AAPL", "winner")
        top = js(page, TXT, ".hw1-top") or ""
        check(f"{tag} B Momentum header: ‹ · AAPL · MMT · 0 of 3", top.startswith("‹") and "AAPL" in top and "MMT" in top and "0 of 3" in top, top)
        line = js(page, TXT, "[data-hw2-line]") if narrow else top
        check(f"{tag} B Momentum: Hold 2 wk – 3 m · size 70% until done (engine hwFactor.mom)", "Hold 2 wk – 3 m" in line and "size 70% until done" in line and js(page, "()=>RiskEngine.POLICY.hwFactor.mom") == 0.7, line)
        check(f"{tag} B size text is amber", js(page, "()=>{ const e = [...document.querySelectorAll('[data-hw2-size]')].find(x=>x.offsetParent); return e ? getComputedStyle(e).color : null; }") not in (None, "rgb(95, 102, 114)"))
        H.go(page, "COST", "ladder")
        top = js(page, TXT, ".hw1-top") or ""
        line = js(page, TXT, "[data-hw2-line]") if narrow else top
        check(f"{tag} B Compounder: COMP · Hold 6 m – 3 y · size 50% until done", "COMP" in top and "Hold 6 m – 3 y" in line and "size 50% until done" in line, [top, line])
        # ---- Momentum: pills from a mocked Screen row
        d8, d40 = plus_days(page, 8), plus_days(page, 40)
        js(page, SCR, [[{"t": "AAPL", "r": 94, "s": "SMH", "o": -0.06, "nx": d8, "i": "Semis"}, {"t": "PLTR", "r": 70, "s": "IGV", "o": -0.2, "nx": d40}]])
        H.go(page, "AAPL", "winner")
        pl = js(page, PILLS)
        ks = [x["k"] for x in pl]
        check(f"{tag} B Momentum: 4 pills RS · sector · earnings · from high (Screen row)", ks == ["rs", "sector", "earn", "high"], pl)
        txt = {x["k"]: x["t"] for x in pl}
        check(f"{tag} B pill texts: `RS 94` · `… vs SPY` · `−6% from high`", txt.get("rs", "").startswith("RS 94") and txt.get("sector", "").endswith("vs SPY") and txt.get("high") == "−6% from high", txt)
        ea = [x for x in pl if x["k"] == "earn"]
        check(f"{tag} B earnings in 8 d (≤ 30): amber + `inside your hold`", ea and "in 8d" in ea[0]["t"] and ea[0]["t"].endswith("· inside your hold") and " pa" in " " + ea[0]["cls"], ea)
        check(f"{tag} B pills sit above the Fact Sheet tabs (left column)", js(page, "()=>{ const p = document.querySelector('[data-hw2-ctx]'), s = document.querySelector('.hw2-seg'); return !!p && !!s && !!p.closest('.hw1-facts') && p.compareDocumentPosition(s) & Node.DOCUMENT_POSITION_FOLLOWING; }"))
        check(f"{tag} B Fact Sheet opens on Results (Momentum)", js(page, "()=>document.querySelector('[data-hw1-page]').dataset.hw2Tab") == "results")
        H.go(page, "PLTR", "winner")
        ea = [x for x in js(page, PILLS) if x["k"] == "earn"]
        check(f"{tag} B earnings in 40 d: grey, no `inside your hold`", ea and "in 40d" in ea[0]["t"] and "inside" not in ea[0]["t"] and " pa" not in " " + ea[0]["cls"], ea)
        H.go(page, "SRC1", "winner")
        check(f"{tag} B stock not in Screen → no pills, no placeholder row", js(page, "()=>!document.querySelector('[data-hw2-ctx]') && !document.querySelector('[data-hw2-pill]')"))
        H.go(page, "COST", "ladder")
        check(f"{tag} B Compounder has no context pills", js(page, "()=>!document.querySelector('[data-hw2-ctx]')"))
        check(f"{tag} B Compounder Fact Sheet opens on Business", js(page, "()=>document.querySelector('[data-hw1-page]').dataset.hw2Tab") == "business")
        # ---- Momentum: fields + chips
        H.go(page, "AAPL", "winner")
        if narrow: js(page, "()=>hw1SegSet('AAPL','mine')")
        f = js(page, "()=>[...document.querySelectorAll('[data-hw1-mine] .hw2-f')].map(x=>[x.dataset.hw1F, x.querySelector('.hw1-fl').innerText.replace(/\\s+/g,' ').trim(), (x.querySelector('.hw1-hint')||{}).innerText])")
        check(f"{tag} B Momentum: 1 Catalyst & setup · 2 Trigger · 3 What would change my thesis?", [x[0] for x in f] == ["catalyst", "trigger", "exit"] and f[0][1].startswith("1 · Catalyst & setup") and f[1][1].startswith("2 · Trigger") and f[2][1].startswith("3 · What would change my thesis?"), f)
        check(f"{tag} B Momentum hints (incl. the corrected 'Not the stop' hint)", f[0][2] == "Why should it move in the next few weeks? Chart and/or news" and f[1][2] == "When do you buy? One line" and f[2][2] == "Not the stop (that's in the plan) — what makes the idea wrong", [x[2] for x in f])
        rows = js(page, "()=>[...document.querySelectorAll('[data-hw1-f=catalyst] .hw2-grp')].map(g=>[g.querySelector('.gl').innerText, [...g.querySelectorAll('.hw2-chip')].map(c=>c.dataset.txt)])")
        check(f"{tag} B Catalyst chip rows: CHART (4) · NEWS · BUSINESS (4)", rows == [["CHART", ["Base breakout", "Pullback to EMA50", "New high", "Sector leading"]], ["NEWS · BUSINESS", ["Earnings beat", "Guide raised", "New product / deal", "Analyst upgrade"]]], rows)
        check(f"{tag} B Trigger chips + Exit chips (defaults)", js(page, "()=>[...document.querySelectorAll('[data-hw1-f=trigger] .hw2-chip')].map(c=>c.dataset.txt)") == ["Close above base high", "+ volume ≥ 1.5×", "Bounce off EMA50"] and js(page, "()=>[...document.querySelectorAll('[data-hw1-f=exit] .hw2-chip')].map(c=>c.dataset.txt)") == ["RS below 70", "Close below EMA50", "Sector turns lagging", "Earnings miss", "No progress in 3 weeks"])
        if narrow:
            vis = js(page, "()=>[...document.querySelectorAll('[data-hw1-f=exit] .hw2-chip')].filter(c=>c.offsetParent).length")
            more = js(page, "()=>{ const m = document.querySelector('[data-hw1-f=exit] [data-hw2-more]'); return m && m.offsetParent ? m.innerText : null; }")
            check(f"{tag} B phone: first 2 chips + `+3`, wraps (no ellipsis)", vis == 2 and more == "+3", [vis, more])
            page.locator('[data-hw1-f=exit] [data-hw2-more]').first.click(); page.wait_for_timeout(120)
            check(f"{tag} B phone: `+3` opens the rest in place", js(page, "()=>[...document.querySelectorAll('[data-hw1-f=exit] .hw2-chip')].filter(c=>c.offsetParent).length") == 5)
        chip(page, "catalyst", "Base breakout").click(); page.wait_for_timeout(100)
        chip(page, "catalyst", "Earnings beat").click(); page.wait_for_timeout(100)
        check(f"{tag} B chip tap adds text joined with ' · ' and turns blue", box(page, "catalyst") == "Base breakout · Earnings beat" and chip_on(page, "catalyst", "Base breakout") and chip_on(page, "catalyst", "Earnings beat") and js(page, "()=>getComputedStyle(document.querySelector('[data-hw2-chip=catalyst].on')).color") == "rgb(59, 79, 196)", box(page, "catalyst"))
        page.fill('[data-hw1-ta="catalyst"]', box(page, "catalyst") + " · my own words"); page.wait_for_timeout(100)
        chip(page, "catalyst", "Base breakout").click(); page.wait_for_timeout(100)
        check(f"{tag} B tap again removes only that text · box stays free text", box(page, "catalyst") == "Earnings beat · my own words" and not chip_on(page, "catalyst", "Base breakout") and chip_on(page, "catalyst", "Earnings beat"), box(page, "catalyst"))
        page.fill('[data-hw1-ta="catalyst"]', ""); page.wait_for_timeout(100)
        check(f"{tag} B clearing the box un-selects the chips · field back to required", not chip_on(page, "catalyst", "Earnings beat") and js(page, TXT, '[data-hw1-chip="catalyst"]') == "required")
        # ---- done needs all 3 · Mark done grey until then
        dn = lambda: js(page, "()=>document.querySelector('[data-hw1-done]').disabled")
        grey = lambda: js(page, "()=>{ const b = document.querySelector('[data-hw1-done]'); return [getComputedStyle(b).backgroundColor, getComputedStyle(b).opacity]; }")
        chip(page, "catalyst", "Pullback to EMA50").click(); chip(page, "trigger", "Close above base high").click(); page.wait_for_timeout(100)
        check(f"{tag} B 2 of 3 → `Save · mark done` still disabled · header `2 of 3`", dn() is True and "2 of 3" in js(page, TXT, "[data-hw1-prog]"), [dn(), js(page, TXT, "[data-hw1-prog]")])
        check(f"{tag} B filled fields show green `done` · the empty one amber `required`", js(page, TXT, '[data-hw1-chip="catalyst"]') == "done" and js(page, TXT, '[data-hw1-chip="exit"]') == "required")
        chip(page, "exit", "RS below 70").click(); page.wait_for_timeout(100)
        check(f"{tag} B 3 of 3 → enabled", dn() is False)
        js(page, "()=>{ window.__t = null; }")
        page.click("[data-hw1-done]"); page.wait_for_timeout(600)
        st = js(page, "()=>{ const it = wlItemOf('AAPL'); return {done:wl1HwDone(it), cat:it.hw.catalyst, trig:it.hw.trigger, exit:it.my_thesis.exit, req:it.hw.catReq, cap:wl1CapPct(it)}; }")
        check(f"{tag} B Save · mark done → done, catalyst stored in the existing `hw.catalyst`, cap 100%", st["done"] and st["cat"] == "Pullback to EMA50" and st["trig"] == "Close above base high" and st["exit"] == "RS below 70" and st["cap"] == 100, st)
        check(f"{tag} B after done: header `✓ Done`, size line gone", js(page, TXT, "[data-hw1-prog]") == "✓ Done" and js(page, "()=>![...document.querySelectorAll('[data-hw2-size]')].some(x=>x.offsetParent)"))
        # ---- a Momentum stock marked done before HW2 stays done
        js(page, "()=>{ const it = wlItemOf('AVGO'); it.hw = {trigger:'Break of the 4-week base', confirmedAt:'2026-11-12T03:00:00Z', doneAt:'2026-11-12T03:00:00Z'}; it.my_thesis = {why:'x', exit:'Hyperscaler capex cut'}; }")
        st = js(page, "()=>{ const it = wlItemOf('AVGO'); return {done:wl1HwDone(it), cap:wl1CapPct(it), req:wl1HwReq(it).map(x=>x.k), pc:pc2Hw({ticker:'AVGO', track:'winner'})}; }")
        check(f"{tag} B old done Momentum without catalyst stays done · cap 100% · catalyst not asked", st["done"] and st["cap"] == 100 and "catalyst" not in st["req"], st)
        H.go(page, "AVGO", "winner")
        if narrow: js(page, "()=>hw1SegSet('AVGO','mine')")
        add = js(page, "()=>{ const c = document.querySelector('[data-hw1-chip=\"catalyst\"]'); return c ? [c.innerText, c.className, getComputedStyle(c).color] : null; }")
        check(f"{tag} B revisit: empty Catalyst shows a small amber `add` label only · header ✓ Done", add and add[0] == "add" and js(page, TXT, "[data-hw1-prog]") == "✓ Done" and add[2] != "rgb(14, 107, 76)", add)
        check(f"{tag} B legacy stock: Save · mark done enabled without catalyst", js(page, "()=>document.querySelector('[data-hw1-done]').disabled") is False)
        # ---- Compounder
        H.go(page, "COST", "ladder")
        if narrow: js(page, "()=>hw1SegSet('COST','mine')")
        f = js(page, "()=>[...document.querySelectorAll('[data-hw1-mine] .hw2-f')].map(x=>[x.dataset.hw1F, x.querySelector('.hw1-fl').innerText.replace(/\\s+/g,' ').trim(), (x.querySelector('.hw1-hint')||{}).innerText])")
        check(f"{tag} B Compounder: 1 I believe… · 2 My evidence is… · 3 What would change my thesis?", [x[0] for x in f] == ["why", "evidence", "exit"] and f[0][1].startswith("1 · I believe…") and f[1][1].startswith("2 · My evidence is…") and f[2][1].startswith("3 · What would change my thesis?"), f)
        check(f"{tag} B Compounder hints", f[0][2] == "What will happen in the business over the next 1–3 years?" and f[1][2] == "Facts from the left that support it — tap to add" and f[2][2] == "A business result, not a price · number + within how many quarters (checked each earnings)", [x[2] for x in f])
        check(f"{tag} B I believe… / change-my-thesis chips (defaults)", js(page, "()=>[...document.querySelectorAll('[data-hw1-f=why] .hw2-chip')].map(c=>c.dataset.txt)") == ["Pricing power", "Earnings growth speeding up", "New product / segment ramp", "Margin expansion", "Market share gains", "Recurring revenue"] and js(page, "()=>[...document.querySelectorAll('[data-hw1-f=exit] .hw2-chip')].map(c=>c.dataset.txt)") == ["Growth below X% for 2 qtrs", "Key milestone missed", "Margin falls 2 qtrs", "Lose key customer / renewal drops", "Management changes course", "Share count rises"])
        ev = js(page, "()=>[...document.querySelectorAll('[data-hw1-f=evidence] .hw2-chip')].map(c=>[c.dataset.txt, c.classList.contains('fact'), getComputedStyle(c).borderStyle])")
        want = ["Revenue +8% YoY", "EPS +14% vs revenue +8%", "Op margin 3.8%", "Shares −0.2% YoY"]
        check(f"{tag} B evidence chips = this Fact Sheet's numbers (max 4, dashed, FROM FACT SHEET)", [x[0] for x in ev] == want and all(x[1] and x[2] == "dashed" for x in ev) and js(page, TXT, "[data-hw1-f=evidence] .gl") == "FROM FACT SHEET", ev)
        fs = js(page, "()=>{ const f = ltFacts(wlItemOf('COST')); return f.q.rows.filter(r=>['rev_yoy','eps_yoy','op_margin','shares_yoy'].includes(r.k)).map(r=>[r.k, r.v[3]]); }")
        check(f"{tag} B …same values as the Fact Sheet rows (rev 8 · eps 14 · margin 3.8 · shares −0.2)", fs == [["rev_yoy", 8], ["eps_yoy", 14], ["op_margin", 3.8], ["shares_yoy", -0.2]], fs)
        chip(page, "evidence", "Revenue +8% YoY").click(); chip(page, "evidence", "EPS +14% vs revenue +8%").click(); page.wait_for_timeout(100)
        check(f"{tag} B evidence chip tap adds to the box (dashed chip turns blue)", box(page, "evidence") == "Revenue +8% YoY · EPS +14% vs revenue +8%" and chip_on(page, "evidence", "EPS +14% vs revenue +8%"), box(page, "evidence"))
        check(f"{tag} B Not proven yet stays, folded", js(page, "()=>{ const d = document.querySelector('[data-hw1-opt]'); return !d.open && d.innerText.includes('+ Not proven yet (optional)') && !!d.querySelector('[data-hw1-ta=unproven]'); }"))
        # no Fact Sheet
        H.go(page, "WHSE", "ladder")
        if narrow: js(page, "()=>hw1SegSet('WHSE','mine')")
        nf = js(page, "()=>{ const n = document.querySelector('[data-hw2-nofacts]'); return n ? [n.innerText.replace(/\\s+/g,' ').trim(), !!n.querySelector('button'), document.querySelectorAll('[data-hw1-f=evidence] .hw2-chip').length] : null; }")
        check(f"{tag} B no Fact Sheet → `No Fact Sheet yet · Import ›`, no evidence chips", nf and nf[0] == "No Fact Sheet yet · Import ›" and nf[1] and nf[2] == 0, nf)
        # ---- next check auto-filled from the earnings date
        nx = plus_days(page, 25)
        js(page, SCR, [[{"t": "ZZ", "r": 60, "s": "XLK", "o": -0.1, "nx": nx}]])
        js(page, "()=>{ const it = wlItemOf('ZZ'); it.next_check_date = ''; it.next_check_note = ''; }")
        H.go(page, "ZZ", "ladder"); page.wait_for_timeout(500)
        st = js(page, "()=>{ const it = wlItemOf('ZZ'); return [it.next_check_date, it.next_check_note]; }")
        fb = js(page, "()=>{ const d = wlCol().doc('ZZ'); return null; }")
        check(f"{tag} B Compounder: next check = next earnings date, filled automatically into the existing field", st[0] == nx and st[1] == "Q results", st)
        hd = js(page, TXT, "[data-hw2-next]") if not narrow else js(page, TXT, "[data-hw2-line]")
        check(f"{tag} B header shows `next check <date> (Q results)`", "next check" in (hd or "") and "(Q results)" in (hd or ""), hd)
        H.go(page, "WHSE", "ladder")
        check(f"{tag} B no earnings date known → no next-check text", js(page, "()=>{ const it = wlItemOf('WHSE'); return !it.next_check_date; }") and "next check" not in (js(page, TXT, ".hw1-top") or "") and "next check" not in (js(page, TXT, "[data-hw2-line]") or ""))
        check(f"{tag} B no console / page errors", not pe, pe[:2])
        if SHOTS_ON:
            H.go(page, "COST", "ladder")
            if narrow: js(page, "()=>hw1SegSet('COST','mine')")
            page.wait_for_timeout(300); shot(page, "hw2-comp-%d" % w)
            js(page, SCR, [[{"t": "AAPL", "r": 94, "s": "SMH", "o": -0.06, "nx": d8}]])
            js(page, "()=>{ const it = wlItemOf('AAPL'); it.hw = {}; it.my_thesis = {}; wlMtDraft['AAPL'] = {}; }")
            H.go(page, "AAPL", "winner")
            if narrow: js(page, "()=>hw1SegSet('AAPL','mine')")
            chip(page, "catalyst", "Base breakout").click(); chip(page, "catalyst", "Earnings beat").click(); page.wait_for_timeout(300); shot(page, "hw2-mmt-%d" % w)
            if narrow:
                H.go(page, "WHSE", "ladder"); js(page, "()=>hw1SegSet('WHSE','facts')"); page.wait_for_timeout(200); js(page, "()=>hw1SegSet('WHSE','mine')"); page.wait_for_timeout(300); shot(page, "hw2-nofacts-390")
    finally:
        b.close()


def main():
    only = os.environ.get("HW2_ONLY", "")
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            if not only or "A" in only: part_a(pw, w, h)
            if not only or "B" in only: part_b(pw, w, h)
    n = len(results); bad = [r for r in results if not r[1]]
    print(f"\nHW2: {n - len(bad)}/{n} passed"); sys.exit(1 if bad else 0)


if __name__ == "__main__": main()
