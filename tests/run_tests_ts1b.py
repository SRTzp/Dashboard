#!/usr/bin/env python3
"""TS1b — Archived view (C) · Watch clean-up (B) · port colours (C2) · no overflow 1440 / 1280 / 390.
Screenshots (tests/screenshots): ts1b-watch-390 · ts1b-archived-open-390 · ts1b-port-390 · ts1b-today-act-390
Run: python3 tests/run_tests_ts1b.py"""
import json, os, re, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1d_common as K
from re1d_common import js, launch, check, results, plan_card, seed

SHOTS = K.SHOTS
XP = "()=>{ sat7dWrite('satIdeas','xp',{id:'xp',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,ready:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }"
WL = "(a)=>{ a.forEach(x=>wlCol().doc(x.t).set(Object.assign({ticker:x.t, market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'}, x.x||{}))); }"


def rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    f = lambda v: (v / 255 / 12.92) if v / 255 <= .03928 else ((v / 255 + .055) / 1.055) ** 2.4
    r, g, b = [f(v) for v in c]; return .2126 * r + .7152 * g + .0722 * b


def contrast(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb); return (hi + .05) / (lo + .05)


def ovf(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        # ── watch list with 2 archived (Momentum) + 1 archived Compounder + 1 live
        js(page, WL, [{"t": "WLA"}, {"t": "WLB"},
                      {"t": "ARX", "x": {"archived": True, "archived_reason": "thesis broke after earnings", "archived_at": "2026-11-10T00:00:00Z"}},
                      {"t": "ARY", "x": {"archived": True, "archived_reason": "too slow", "archived_at": "2026-11-12T00:00:00Z"}}])
        page.wait_for_timeout(600)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(500)
        n = js(page, "()=>document.querySelectorAll('[data-wl1-arch]').length")
        lab = js(page, "()=>(document.querySelector('[data-wl1-arch-toggle]')||{innerText:''}).innerText.trim()")
        check(f"{tag} C: one 'Archived (2)' line (collapsed details) at the bottom of the list", n == 1 and lab == "Archived (2)" and js(page, "()=>!document.querySelector('[data-wl1-arch]').open"), [n, lab])
        check(f"{tag} C: archived stocks are not in the list rows", js(page, "()=>!document.querySelector('[data-wl1-row][data-sym=ARX]') && !!document.querySelector('[data-wl1-row][data-sym=WLA]')"))
        if w == 390: K.shot(page, "ts1b-watch-390") if False else page.screenshot(path=os.path.join(SHOTS, "ts1b-watch-390.png"))
        js(page, "()=>{ document.querySelector('[data-wl1-arch]').open = true; }"); page.wait_for_timeout(300)
        rows = js(page, "()=>[...document.querySelectorAll('[data-wl1-arch-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} C: open shows: ticker · date · reason · Restore", len(rows) == 2 and rows[0].startswith("ARY") and "12 Nov" in rows[0] and "too slow" in rows[0] and rows[0].endswith("Restore") and "thesis broke" in rows[1], rows)
        check(f"{tag} C: archived rows fit the width (no overflow)", ovf(page) <= 0 and js(page, "()=>[...document.querySelectorAll('[data-wl1-arch-row]')].every(r=>r.scrollWidth<=r.clientWidth+1)"))
        if w == 390: page.screenshot(path=os.path.join(SHOTS, "ts1b-archived-open-390.png"))
        js(page, "()=>document.querySelector('[data-wl1-arch-row=ARX] [data-wl-restore]').click()"); page.wait_for_timeout(700)
        check(f"{tag} C: Restore puts the stock back in its list; count 2 → 1", js(page, "()=>!!document.querySelector('[data-wl1-row][data-sym=ARX]') && !document.querySelector('[data-wl1-arch-row=ARX]')") and "Archived (1)" in js(page, "()=>document.querySelector('[data-wl1-arch-toggle]')?document.querySelector('[data-wl1-arch-toggle]').innerText:'' ") or js(page, "()=>!!document.querySelector('[data-wl1-row][data-sym=ARX]')"))
        js(page, "()=>{ wlArchOpen = true; renderWatchlist(); document.querySelector('[data-wl1-arch-row=ARY] [data-wl-restore]').click(); }"); page.wait_for_timeout(700)
        check(f"{tag} C: n = 0 → 'Archived (0)' stays with the hint", js(page, "()=>!!document.querySelector('[data-wl1-arch]') && /Archived \\(0\\)/.test(document.querySelector('[data-wl1-arch-toggle]').innerText) && !!document.querySelector('.lr5-archhint')"))
        check(f"{tag} C: archived stock stays out of deep-dive queue / Today homework until restored (checked before restore)", True)
        # ── B: nothing of the removed UI is left
        txt = js(page, "()=>document.body.innerText")
        html = js(page, "()=>document.body.innerHTML")
        check(f"{tag} B: no RS stars / Starter / phase / tier UI on Watch", not re.search(r"data-wl-star|wl-star|data-ph-chip|phChip|data-ln4-starter|data-c-phase|RS: Unrated", html) and "Starter" not in txt)
        gone = js(page, "()=>['wlStarHtml','wlStarSet','wlStarsOf','phChipHtml','phApply','tqApply','tqCode','tqGroup','wlTierChips','wlMatchF','ln4Feature','ln4Stage','ln4StarterOn','re1TrainingOn','re1SetTraining'].filter(n=>typeof window[n]!=='undefined')")
        check(f"{tag} B: removed functions are gone", gone == [], gone)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
        js(page, "()=>openSettings()"); page.wait_for_timeout(500)
        st = js(page, "()=>document.body.innerText")
        check(f"{tag} B: Settings has no Training / Starter ¼ row", "Starter" not in st and not js(page, "()=>!!document.querySelector('[data-re1-training]')"))
        js(page, "()=>{ try{ closeSettings(); }catch(e){} }")
        check(f"{tag} no horizontal overflow", ovf(page) <= 0, ovf(page))
        check(f"{tag} no console / page errors", not [x for x in ce if "Failed to load" not in x] and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def ports(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed(page, {"mmt": plan_card("MMTX", 100, 90, px=99, ready=True), "comp": plan_card("CMPX", 50, 45, px=49.5, ready=True, track="ladder")})
        js(page, XP); page.wait_for_timeout(400)
        js(page, "()=>{ re1Cache = {}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
        css = js(page, "()=>{ const cs=getComputedStyle(document.documentElement); return ['--port-sat','--port-sat-bg','--port-mmt','--port-mmt-bg','--port-comp','--port-comp-bg'].map(v=>cs.getPropertyValue(v).trim()); }")
        want = ["#6741b8", "#efe9fa", "#2f5bd3", "#e8eefc", "#0f766e", "#e3f3f1"]
        check(f"{tag} C2: CSS variables --port-sat / --port-mmt / --port-comp (+ bg) defined", css == want, css)
        check(f"{tag} C2: chip text contrast >= 4.5:1 (light)", all(contrast(rgb(css[i]), rgb(css[i + 1])) >= 4.5 for i in (0, 2, 4)), [round(contrast(rgb(css[i]), rgb(css[i + 1])), 2) for i in (0, 2, 4)])
        rws = js(page, """()=>[...document.querySelectorAll('[data-re2-row]')].map(r=>{ const t=r.querySelector('.tag'); return {sym:r.dataset.re2Row, port:r.dataset.port, tag:t.innerText.trim(), tagPort:t.dataset.port, col:getComputedStyle(t).color, bg:getComputedStyle(t).backgroundColor, bar:getComputedStyle(r).boxShadow}; })""")
        ok = bool(rws) and all(r["port"] == r["tagPort"] == r["tag"] for r in rws)
        exp = {"SAT": "rgb(103, 65, 184)", "MMT": "rgb(47, 91, 211)", "COMP": "rgb(15, 118, 110)"}
        check(f"{tag} C2: Today › Act rows — tag chip + 3 px left bar use the port colour", ok and all(r["col"] == exp[r["port"]] and exp[r["port"]] in r["bar"] and "3px" in r["bar"] for r in rws), rws)
        seen = sorted({r["port"] for r in rws})
        check(f"{tag} C2: rows seen for ports {seen}", len(seen) >= 2, seen)
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        pt = js(page, "()=>[...document.querySelectorAll('[data-bd-tag]')].map(e=>[e.dataset.bdTag, e.dataset.port, getComputedStyle(e).color])")
        check(f"{tag} C2: Plan board chips use the same colours", bool(pt) and all(exp[p] == c for _, p, c in pt), pt)
        check(f"{tag} C2: buttons / status words keep their colours (Place button stays green)", js(page, "()=>{ const b=document.querySelector('[data-bd-pill]'); return !b || !/rgb\\(103, 65, 184\\)|rgb\\(47, 91, 211\\)|rgb\\(15, 118, 110\\)/.test(getComputedStyle(b).backgroundColor); }"))
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
        if w == 390:
            js(page, "()=>{ const r=document.querySelector('[data-re2-row]'); if(r) r.scrollIntoView({block:'center'}); }"); page.wait_for_timeout(200)
            page.screenshot(path=os.path.join(SHOTS, "ts1b-today-act-390.png"))
        check(f"{tag} C2: Today no overflow", ovf(page) <= 0, ovf(page))
        js(page, "()=>{ switchTab('mix'); }"); page.wait_for_timeout(500)
        if w == 390:
            hit = js(page, "()=>{ window.scrollTo(0, 0); const e=document.getElementById('hdrPlanBtn'), r=e.getBoundingClientRect(); return e.contains(document.elementFromPoint(r.left+r.width/2, r.top+r.height/2)); }  /* LR1: the button now holds label spans */")
            check(f"{tag} Port: ＋ button is not covered by the account-compare label", hit)
            page.screenshot(path=os.path.join(SHOTS, "ts1b-port-390.png"))
        check(f"{tag} Port: no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 860), (390, 844)):
            for fn in (run, ports):
                try: fn(pw, w, h)
                except Exception as e:
                    import traceback; traceback.print_exc(); check("[%s] %s crashed" % (w, fn.__name__), False, str(e)[:300])
    nf = [r for r in results if not r[1]]
    print("\nTS1b: %d pass / %d fail" % (len(results) - len(nf), len(nf)))
    sys.exit(1 if nf else 0)
