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
    page.screenshot(path=os.path.join(SHOTS, name + ".png"))


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


def main():
    only = os.environ.get("HW2_ONLY", "")
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            if not only or "A" in only: part_a(pw, w, h)
    n = len(results); bad = [r for r in results if not r[1]]
    print(f"\nHW2: {n - len(bad)}/{n} passed"); sys.exit(1 if bad else 0)


if __name__ == "__main__": main()
