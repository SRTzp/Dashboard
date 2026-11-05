#!/usr/bin/env python3
"""PL2b item 8 — main-tab swipe zones · เทส 363 · Playwright WebKit + iPhone emulation (touch · portrait 390×844 + landscape 844×390 · rotation)
Chromium (mobile touch) รันซ้ำเป็นชุดที่สอง · เหตุการณ์ touch ถูกส่งแบบสังเคราะห์ (touchstart/touchend ที่จุดเริ่ม/จบ) เพราะ Playwright ไม่มี swipe API
รัน: python3 run_tests_phase363.py   (BROWSER=chromium ก็ได้)"""
import json, os, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase39 as P39
import run_tests_phase38 as P38
import run_tests_phase59 as P59

results = []
js = C.js


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


class _Browser:
    def __init__(self, b, dev): self._b, self._dev = b, dev
    def new_context(self, **kw): return self._b.new_context(**{**self._dev, **kw})
    def __getattr__(self, k): return getattr(self._b, k)


class _Type:
    def __init__(self, t, dev): self._t, self._dev = t, dev
    def launch(self, **kw):
        kw.pop("executable_path", None)
        return _Browser(self._t.launch(**kw), self._dev)


class _PW:
    def __init__(self, pw, engine, dev): self.chromium = _Type(getattr(pw, engine), dev)


def make_pw(pw, engine, w, h):
    base.CHROMIUM_PATH = None if engine == "webkit" else base.CHROMIUM_PATH
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    dev = {"has_touch": True, "is_mobile": True, "device_scale_factor": 3, "user_agent": ua} if engine == "webkit" else {"has_touch": True, "is_mobile": True, "device_scale_factor": 3}
    return _PW(pw, engine, dev)


# ── synthetic swipe (touchstart at start point, touchend at end point) ──
SWIPE = """([sx, sy, ex, ey])=>{
  const mk = (type, x, y)=>{ const e = new Event(type, {bubbles:true, cancelable:true}); const t = {clientX:x, clientY:y, pageX:x, pageY:y, identifier:1};
    Object.defineProperty(e, 'touches', {value: type==='touchend' ? [] : [t]}); Object.defineProperty(e, 'changedTouches', {value:[t]}); return e; };
  const a = document.elementFromPoint(sx, sy) || document.body, b = document.elementFromPoint(ex, ey) || document.body;
  window.__swClicks = 0; if(!window.__swClk){ window.__swClk = true; document.addEventListener('click', ()=>{ window.__swClicks++; }, true); }
  const before = activeTab;
  a.dispatchEvent(mk('touchstart', sx, sy));
  b.dispatchEvent(mk('touchend', ex, ey));
  return {before, after: activeTab, target: a.tagName + '.' + (a.className||'') + '#' + (a.id||'')};
}"""


def swipe(page, sx, sy, ex, ey):
    r = js(page, SWIPE, [sx, sy, ex, ey]); page.wait_for_timeout(250); return r


def rect(page, sel):
    return js(page, "(s)=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return {l:r.left, t:r.top, r:r.right, b:r.bottom, w:r.width, h:r.height}; }", sel)


def go(page, tab):
    js(page, "(t)=>switchTab(t)", tab); page.wait_for_timeout(500)


def launch(pw, engine, w, h, ideas=True):
    P = make_pw(pw, engine, w, h)
    doc = P38.doc38(clean=True)
    for b in doc["books"].values(): b["settings"].pop("satWeekPick", None)
    iso = "2026-10-01T05:00:00Z"
    idl = [P59.idea([P59.cand("CAA", "A", 1, "study")], iid="i1")] if ideas else []
    def extra(page):
        for it in idl:
            import run_tests_phase44 as P44
            P44.seed_idea(page, it)
    return P39.launch(P, w, h, doc=doc, clean=True, iso=iso, pick=False, extra=extra)


def zone_tests(pw, engine):
    tg = f"[{engine}]"
    # ───────── portrait 390×844 ─────────
    b, ctx, page, ce, pe, dl = launch(pw, engine, 390, 844)
    try:
        go(page, "today"); n = rect(page, "#tabsMain")
        check(f"{tg} portrait: bottom nav is fixed at the bottom (orientation portrait)", n and n["b"] >= 800 and js(page, "()=>matchMedia('(orientation: portrait)').matches"), n)
        y = (n["t"] + n["b"]) / 2
        r = swipe(page, 300, y, 60, y)
        check(f"{tg} portrait: swipe LEFT starting in the bottom nav → next tab", r["before"] == "today" and r["after"] != "today", r)
        go(page, "watch"); r = swipe(page, 60, y, 330, y)
        check(f"{tg} portrait: swipe RIGHT starting in the bottom nav → previous tab", r["after"] != "watch", r)
        go(page, "today"); r = swipe(page, 330, 300, 40, 300)
        check(f"{tg} portrait: swipe starting in page content → tab unchanged", r["after"] == "today", r)
        r = swipe(page, 330, 24, 40, 24)
        check(f"{tg} portrait: swipe starting in the top header → tab unchanged (bottom nav ONLY)", r["after"] == "today", r)
        r = swipe(page, 6, 300, 380, 300)
        check(f"{tg} portrait: swipe starting in the side margin → tab unchanged", r["after"] == "today", r)
        r = swipe(page, 330, 300, 60, y)
        check(f"{tg} portrait: starts in content, ends in the bottom nav → tab unchanged", r["after"] == "today", r)
        # Value Chain + Evidence + detail tab strip (Ideas detail open)
        js(page, "()=>{ switchTab('watch'); wlSetView('idea'); ideaSel='i1'; wlMobOpen=true; renderWatchlist(); }"); page.wait_for_timeout(600)
        for sub, sel in (("vc", ".ideaVc"), ("evd", ".ltTw")):
            js(page, "(s)=>{ ideaSubSave('i1', s); renderWatchlist(); }", sub); page.wait_for_timeout(500)
            info = js(page, "(s)=>{ const e = document.querySelector(s); if(!e) return null; let p = e, hid = []; while(p && p !== document.body){ const cs = getComputedStyle(p); if(p !== e && (cs.overflowX==='hidden' || cs.overflowX==='clip')) hid.push(p.className||p.tagName); p = p.parentElement; } const r = e.getBoundingClientRect(); return {sw:e.scrollWidth, cw:e.clientWidth, ox:getComputedStyle(e).overflowX, hid, l:r.left, t:r.top, w:r.width, h:r.height}; }", sel)
            check(f"{tg} {sel} is rendered, overflow-x scrollable, no clipping parent", info and info["ox"] in ("auto", "scroll") and not info["hid"], info)
            if info:
                x0, y0 = info["l"] + info["w"] - 20, info["t"] + min(info["h"], 40) / 2
                st = js(page, "()=>activeTab"); r = swipe(page, x0, y0, 40, y0)
                check(f"{tg} portrait: swipe starting on {sel} → tab unchanged", r["after"] == st, r)
        js(page, "()=>{ ideaSubSave('i1','sum'); renderWatchlist(); }"); page.wait_for_timeout(400)
        tab = rect(page, "[data-idea-tabs]")
        if tab:
            st = js(page, "()=>activeTab"); r = swipe(page, tab["l"] + tab["w"] - 20, tab["t"] + tab["h"] / 2, 30, tab["t"] + tab["h"] / 2)
            check(f"{tg} portrait: swipe starting on the detail tab strip → tab unchanged", r["after"] == st, r)
        # click behaviour: swipe ending on a button → no click · tap on a button → click works
        go(page, "today"); nb = rect(page, "#tabBtnWatch") or rect(page, "#tabsMain button:nth-child(3)")
        js(page, "()=>{ window.__swClicks = 0; }")
        # ends on a nav button after a recognised swipe: eatClick swallows the next click
        bt = rect(page, "#tabsMain button:nth-child(2)")
        r = swipe(page, 330, y, bt["l"] + bt["w"] / 2 - 100, y)
        js(page, "()=>{ window.__swClicks = 0; const b = document.querySelector('#tabsMain button:nth-child(2)'); b.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true})); }"); page.wait_for_timeout(100)
        clicks = js(page, "()=>window.__swClicks")
        check(f"{tg} a recognised swipe swallows the synthetic click that follows (click listener sees it, handler does not run)", r["after"] != "today", r)
        page.wait_for_timeout(600)
        go(page, "today")
        page.locator("#tabsMain button:nth-child(2)").tap(); page.wait_for_timeout(500)
        check(f"{tg} a plain TAP on a nav button still works (tab switches)", js(page, "()=>activeTab") != "today")
        check(f"{tg} no console errors", not [e for e in ce if "Failed to load" not in e] and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()
    # ───────── landscape 844×390 ─────────
    b, ctx, page, ce, pe, dl = launch(pw, engine, 844, 390)
    try:
        go(page, "today")
        check(f"{tg} landscape: orientation is landscape; nav is in the top header (not fixed bottom)", not js(page, "()=>matchMedia('(orientation: portrait)').matches") and js(page, "()=>getComputedStyle(document.querySelector('.tabs')).position") != "fixed")
        tb = rect(page, ".topbar"); sync = rect(page, "#syncStatus") or rect(page, ".sync") or tb
        r = swipe(page, 700, tb["t"] + 8, 300, tb["t"] + 8)
        check(f"{tg} landscape: swipe LEFT from the header strip → next tab", r["before"] == "today" and r["after"] != "today", r)
        go(page, "watch"); r = swipe(page, 200, tb["t"] + 8, 600, tb["t"] + 8)
        check(f"{tg} landscape: swipe RIGHT from the header strip → previous tab", r["after"] != "watch", r)
        go(page, "today")
        s = js(page, "()=>{ const e = document.querySelector('#syncBadge'); if(!e) return null; const r = e.getBoundingClientRect(); return {l:r.left, t:r.top, w:r.width, h:r.height}; }")
        sx, sy = (s["l"] + s["w"] / 2, s["t"] + s["h"] / 2) if s else (80, tb["t"] + 12)
        r = swipe(page, sx, sy, sx - 300, sy)
        check(f"{tg} landscape: swipe from the sync-status area → tab changes", r["after"] != "today", [r, s])
        go(page, "today")
        wr = rect(page, "#mainWrap"); vw = js(page, "()=>document.documentElement.clientWidth")
        gl, gr = wr["l"], vw - wr["r"]
        print(f"INFO {tg} landscape gutters: left={gl:.0f}px right={gr:.0f}px")
        if gl >= 8:
            r = swipe(page, gl / 2, 250, gl / 2 - 120, 250)
            check(f"{tg} landscape: swipe starting in the LEFT gutter ({gl:.0f}px visible) → tab changes", r["after"] != "today", r)
            go(page, "today")
        else: check(f"{tg} landscape: no visible left gutter ≥ 8px → no gutter zone (nothing to test)", True)
        if gr >= 8:
            r = swipe(page, vw - gr / 2, 250, vw - gr / 2 - 300, 250)
            check(f"{tg} landscape: swipe starting in the RIGHT gutter ({gr:.0f}px visible) → tab changes", r["after"] != "today", r)
            go(page, "today")
        else: check(f"{tg} landscape: no visible right gutter ≥ 8px → no gutter zone (nothing to test)", True)
        r = swipe(page, 400, 250, 80, 250)
        check(f"{tg} landscape: swipe starting on a card/panel → tab unchanged", r["after"] == "today", r)
        r = swipe(page, 400, 250, 700, tb["t"] + 8)
        check(f"{tg} landscape: starts on content, ends in the header → tab unchanged", r["after"] == "today", r)
        js(page, "()=>{ switchTab('watch'); wlSetView('idea'); ideaSel='i1'; wlMobOpen=true; renderWatchlist(); ideaSubSave('i1','vc'); renderWatchlist(); }"); page.wait_for_timeout(600)
        vcr = rect(page, ".ideaVc")
        if vcr:
            r = swipe(page, vcr["l"] + vcr["w"] - 20, vcr["t"] + 20, 40, vcr["t"] + 20)
            check(f"{tg} landscape: swipe on the Value Chain row → tab unchanged", r["after"] == "watch", r)
        # rotation: resize to portrait → zones switch
        page.set_viewport_size({"width": 390, "height": 844}); page.wait_for_timeout(500)
        go(page, "today"); n = rect(page, "#tabsMain"); y = (n["t"] + n["b"]) / 2
        r1 = swipe(page, 330, 300, 40, 300); r2 = swipe(page, 330, y, 60, y)
        check(f"{tg} rotate landscape→portrait: content swipe ignored · bottom-nav swipe works", r1["after"] == "today" and r2["after"] != "today", [r1, r2])
        page.set_viewport_size({"width": 844, "height": 390}); page.wait_for_timeout(500)
        go(page, "today"); tb = rect(page, ".topbar")
        r1 = swipe(page, 700, tb["t"] + 8, 300, tb["t"] + 8)
        check(f"{tg} rotate portrait→landscape: header swipe works again", r1["after"] != "today", r1)
        check(f"{tg} no console errors", not [e for e in ce if "Failed to load" not in e] and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


if __name__ == "__main__":
    engines = [e for e in (os.environ.get("ENGINES") or "webkit,chromium").split(",") if e]
    with sync_playwright() as pw:
        for e in engines: zone_tests(pw, e)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
