#!/usr/bin/env python3
"""CLEAN1 — (1) Journal review: Planned entry shows size like Actual ('#0.21 @ 2,642') · (2) Today Blocked row line 2 = 'Blocked · <short reason> · allowed #n' (n = engine allowedQty, omitted when null/0)
· (3) desktop Risk room SAT line not truncated · (4) screenshot scripts hide #tabsMain only at <=600px.
Run: python3 tests/run_tests_clean1.py"""
import sys, os, re
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import lrf_side as S
import run_tests_lrf as LF
import lr5b_common as JC

HERE = os.path.dirname(os.path.abspath(__file__))


def journal(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = JC.open_journal(pw, w, h)
    try:
        js(page, "()=>lrSwPick('journal','both')"); page.wait_for_timeout(300)
        js(page, "()=>lr5Pick('main:x1')"); page.wait_for_timeout(400)
        t = js(page, "()=>{ const c = [...document.querySelectorAll('[data-lr5-review] .lr5-pv > span')].map(s=>s.innerText.trim()); const i = c.indexOf('Entry'); return c.slice(i, i + 3); }")
        check(f"{tag} 1 review panel Entry: Planned '#0.21 @ 2,642' = same format as Actual", t and t[1] == "#0.21 @ 2,642" and t[2] == t[1], t)
        check(f"{tag} 1 no page errors", not pe, pe)
    finally:
        b.close()


def today(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        LF.today(page); js(page, "()=>{ re2GrpAll = {enter:true, check:true, manage:true}; todayRefresh(true); }"); page.wait_for_timeout(400)
        ln = lambda: js(page, "()=>{ const r = document.querySelector('.re2-row[data-re2-row=\"NVDA\"] .lrf-blkline'); return r ? {t: r.innerText.replace(/\\s+/g, ' ').trim(), shown: r.getClientRects().length > 0, ws: getComputedStyle(r).whiteSpace} : null; }")
        l = ln()
        check(f"{tag} 2 Blocked line 2 = 'Blocked · MMT weekly limit 4/4' (visible, also on the phone); no 'allowed' when allowedQty is 0/null", l and l["shown"] and l["t"] == "Blocked · MMT weekly limit 4/4", l)
        js(page, "()=>{ window.__g = re1PlanGate; re1PlanGate = function(c, lv){ const g = window.__g(c, lv); return Object.assign({}, g, {model: Object.assign({}, g.model || {}, {allowedQty: 12})}); }; todayRefresh(true); }"); page.wait_for_timeout(400)
        l = ln()
        check(f"{tag} 2 with engine allowedQty 12 -> 'Blocked · MMT weekly limit 4/4 · allowed #12'", l and l["t"] == "Blocked · MMT weekly limit 4/4 · allowed #12", l)
        if w <= 600: check(f"{tag} 2 phone: still ONE line (nowrap)", l and l["ws"] == "nowrap", l)
        check(f"{tag} 2 no page errors", not pe, pe)
    finally:
        b.close()
    if w > 600:
        d, cs = S.fixture()
        b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
        try:
            js(page, "()=>{ serverConfirmed = true; stateFromServer = true; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
            s = js(page, "()=>{ const t = document.querySelector('[data-lr2-risk] [data-lr2-rl=\"sat\"] .rw'); return t ? {txt: t.innerText, sw: t.scrollWidth, cw: t.clientWidth, shown: t.getClientRects().length > 0} : null; }")
            check(f"{tag} 3 desktop SAT line '0.2% · x/y%' (RK1: value, no step label) not truncated", s and s["shown"] and re.match(r"^[\d.]+% · [\d.]+/[\d.]+%", s["txt"]) is not None and s["sw"] <= s["cw"], s)
        finally:
            b.close()


def scripts():
    names = ["lr4_side", "lrf_side", "lr5b_side", "lr5c_side", "lib_phase38", "lib_phase39", "lib_phase40", "run_tests_phase373", "ln4_match", "ui_audit"]
    bad = [n for n in names if "@media (max-width:600px){#tabsMain{display:none!important}}" not in open(os.path.join(HERE, n + ".py")).read()]
    check("4 whole-page screenshot scripts hide #tabsMain via a <=600px media rule", not bad, bad)
    check("4 lr5a_side keeps its w<=600 guard", "if w <= 600: page.add_style_tag(content=HIDE_NAV)" in open(os.path.join(HERE, "lr5a_side.py")).read())


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            journal(pw, w, h); today(pw, w, h)
    scripts()
    bad = [r for r in results if not r[1]]
    print("SUMMARY clean1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
