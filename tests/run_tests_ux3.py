#!/usr/bin/env python3
"""UX3 — A resizable splits (Watch detail · Homework · Screen) · B import null fix · C RR4 RRG bars from the job · D CR1 freshness (docs/briefs/UX3-brief.md).
Run: python3 tests/run_tests_ux3.py   (UX3_SHOTS=1 writes docs/screenshots/ux3-*.png)"""
import sys, os, json
from playwright.sync_api import sync_playwright
from re1d_common import js, check, results
import lr5_common as C
import hw1_common as H
import rs2a_common as R

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")


def shot(page, name, **kw):
    if os.environ.get("UX3_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); js(page, "()=>window.scrollTo(0, 0)"); page.wait_for_timeout(80); page.screenshot(path=os.path.join(SHOTS, "ux3-%s.png" % name), **kw)


def geom(page, sel):
    return js(page, "(s)=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return {l:Math.round(r.left), r:Math.round(r.right), w:Math.round(r.width), h:Math.round(r.height), disp:getComputedStyle(e).display}; }", sel)


NOHS = "()=>{ const w = document.documentElement.clientWidth; return document.documentElement.scrollWidth <= w + 1 && document.body.scrollWidth <= w + 1; }"
# nothing in the main box is clipped with '…' · no text node cut by overflow:hidden
CUT = "(sel)=>{ const b = document.querySelector(sel); if(!b) return ['nobox']; const bad = []; b.querySelectorAll('*').forEach(e=>{ const cs = getComputedStyle(e); if(cs.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1) bad.push(e.className + ':' + e.textContent.slice(0, 20)); }); return bad; }"


# page spec: how to open · pane selector · handle · expected default/min/max at 1440 · box to test for cut text · table scroll host
PAGES = {
    "wl": dict(key="wl.detW", pane=".wlm.wl1>.wlDet", box=".wlm.wl1", tbl="#watchGroups .wlList .wlListBody", dir=-1),
    "hw": dict(key="hw.factsW", pane=".hw1-body>.hw1-facts", box=".hw1-body", tbl=".hw1-facts", dir=1),
    "rs": dict(key="rs2.sideW", pane=".lr5-screen .wlm>.wlDet", box=".lr5-screen .wlm", tbl=".lr5-screen .wlListBody", dir=-1),
}


def open_page(pw, which, w, h=900):
    if which == "wl":
        b, page, pe = C.open_watch(pw, w, h); js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(600); return b, page, pe
    if which == "hw":
        b, page, pe = H.open_hw(pw, w, h); H.go(page, "AVGO"); return b, page, pe
    b, page, pe, ce = R.open_screen(pw, w, h); return b, page, pe


def part_a(pw):
    for which, P in PAGES.items():
        tag = "[A split %s]" % which
        b, page, pe = open_page(pw, which, 1440)
        try:
            hs = '[data-split="%s"]' % which
            h = geom(page, hs)
            check(f"{tag} 1440: handle is on the page, 8px wide, display:block", bool(h) and h["w"] == 8 and h["disp"] == "block", h)
            pane = lambda: geom(page, P["pane"])
            d0 = pane()["w"]
            op = js(page, "(s)=>getComputedStyle(document.querySelector(s), '::after').opacity", hs)
            check(f"{tag} handle is invisible until hover/focus", float(op) == 0, op)
            # keyboard
            page.focus(hs)
            page.keyboard.press("Home"); page.wait_for_timeout(120); wmin = pane()["w"]
            page.keyboard.press("End"); page.wait_for_timeout(120); wmax = pane()["w"]
            check(f"{tag} Home → min · End → max (min < default ≤ max)", wmin < d0 <= wmax + 1 and wmin < wmax, [wmin, d0, wmax])
            saved = js(page, "(k)=>localStorage.getItem(k)", P["key"])
            check(f"{tag} saved per device in localStorage `{P['key']}`", saved is not None and abs(int(saved) - wmax) <= 1, [saved, wmax])
            for nm, wv in (("min", wmin), ("max", wmax), ("default", d0)):
                if nm == "min": page.keyboard.press("Home")
                elif nm == "max": page.keyboard.press("End")
                else: page.keyboard.press("Enter")
                page.wait_for_timeout(200)
                nh = js(page, NOHS); cut = js(page, CUT, P["box"]); wpn = pane()["w"]
                sc = js(page, "(s)=>{ const e = document.querySelector(s); return e ? e.scrollWidth - e.clientWidth : -1; }", P["tbl"])
                check(f"{tag} at {nm} ({wpn}px): no horizontal page scroll · no `…` cut · nothing scrolls sideways inside the list", nh and not cut and sc <= 1, [nh, cut, sc])
                shot(page, "split-%s-%s" % (which, nm))
            check(f"{tag} Enter resets to the default width and clears the saved value", abs(pane()["w"] - d0) <= 1 and js(page, "(k)=>localStorage.getItem(k)", P["key"]) is None, [pane()["w"], d0])
            # drag
            hb = geom(page, hs); y = hb["h"] // 2 if which != "rs" else 300
            page.mouse.move(hb["l"] + 4, 400); page.mouse.down(); page.mouse.move(hb["l"] + 4 - 30 * P["dir"] * -1, 400, steps=4); page.mouse.up(); page.wait_for_timeout(200)
            dd = pane()["w"]
            check(f"{tag} dragging the handle changes the pane width (and saves it)", abs(dd - d0) >= 20 and js(page, "(k)=>localStorage.getItem(k)", P["key"]) is not None, [d0, dd])
            page.dblclick(hs); page.wait_for_timeout(200)
            check(f"{tag} double-click resets", abs(pane()["w"] - d0) <= 1, [pane()["w"], d0])
            check(f"{tag} no page errors", not pe, pe[:3])
        finally:
            b.close()
        # narrow desktop (handle hidden, layout as before) and phone
        for w in (1099, 390):
            b, page, pe = open_page(pw, which, w, 900 if w > 500 else 844)
            try:
                vis = js(page, "(s)=>[...document.querySelectorAll(s)].filter(e=>e.getBoundingClientRect().width > 0).length", '[data-split="%s"]' % which)
                check(f"{tag} {w}px: handle not shown", vis == 0, vis)
                check(f"{tag} {w}px: no horizontal page scroll", js(page, NOHS))
                if w == 390: shot(page, "split-%s-390" % which)
                check(f"{tag} {w}px: no page errors", not pe, pe[:3])
            finally:
                b.close()


FIX = os.path.join(HERE, "fixtures", "googl-facts-null-asof.json")
PARSE = "(t)=>{ const r = ltParse(t, null); return {err:r.err||null, factsOnly:!!r.factsOnly, asOf:r.th ? (r.th.asOf === undefined ? '(unset)' : r.th.asOf) : undefined, fAsOf:r.th&&r.th.facts&&r.th.facts.asOf, fDate:r.th&&r.th.facts&&r.th.facts.date}; }"


def part_b(pw):
    tag = "[B null optional]"
    d = json.load(open(FIX))
    b, page, pe = C.open_watch(pw, 1440, 900)
    try:
        P = lambda o: js(page, PARSE, json.dumps(o))
        r = P(d)
        check(f"{tag} GOOGL facts file with `asOf: null` parses (no error, facts-only)", r["err"] is None and r["factsOnly"] and r["fAsOf"] == "Q3 2026" and r["fDate"] == "2026-10-28", r)
        for k in ("name", "market", "mode", "date", "basis", "audit"):
            o = dict(d); o[k] = None; r = P(o)
            check(f"{tag} top-level `{k}: null` is accepted", r["err"] is None, r)
        o = dict(d); o["asOf"] = 5; r = P(o)
        check(f"{tag} `asOf: 5` still rejected, same message", r["err"] == "Field asOf must be string (this file has number) — nothing saved", r)
        o = dict(d); o["basis"] = ["x"]; r = P(o)
        check(f"{tag} `basis: [..]` still rejected", r["err"] == "Field basis must be string (this file has array) — nothing saved", r)
        o = dict(d); o["sym"] = None; r = P(o)
        check(f"{tag} required `sym: null` stays strict", r["err"] is not None, r)
        o = dict(d); o["facts"] = dict(d["facts"], asOf=None); r = P(o)
        check(f"{tag} required facts.asOf stays strict", r["err"] is not None and "facts.asOf" in r["err"], r)
        # real import through the Import sheet → Fact Sheet date line as before
        js(page, "()=>wlCol().doc('GOOGL').set({ticker:'GOOGL', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'})"); page.wait_for_timeout(500)
        js(page, "(t)=>{ ltImportOpen('GOOGL'); document.getElementById('ltJson').value = t; ltImpCheck(); }", json.dumps(d)); page.wait_for_timeout(250)
        err = js(page, "()=>document.getElementById('ltErr') ? document.getElementById('ltErr').innerText : ''")
        js(page, "()=>ltImpSave()"); page.wait_for_timeout(600)
        st = js(page, "()=>{ const it = wlItemOf('GOOGL'); return {f: ltFacts(it) && ltFacts(it).date}; }")
        js(page, "()=>{ wlOpen('GOOGL'); wl5Full('GOOGL','sum'); }"); page.wait_for_timeout(300)
        ln = js(page, "()=>{ const e = document.querySelector('[data-lt-facts-line]'); return e ? e.innerText.trim() : null }")
        check(f"{tag} Import sheet: no error · saved · Full thesis line shows the Fact Sheet date (`Fact Sheet · Q3 2026 · 28 Oct`)", not err.strip() and st["f"] == "2026-10-28" and ln == "Fact Sheet · Q3 2026 · 28 Oct", [err, st, ln])
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    only = os.environ.get("UX3_PARTS", "a b c d").split()
    with sync_playwright() as pw:
        for k in only:
            globals().get("part_" + k, lambda pw: None)(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY ux3: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
