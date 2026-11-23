#!/usr/bin/env python3
"""PH1 — iPhone pass (390): Watch swipe rules · Plan card header (⋯ only) + 'AT BROKER · NONE' · Flow catalyst 2 lines + ▾ after the date · Journal Details wraps · Today Act header has no stray '· —'. Desktop unchanged.
Run: python3 tests/run_tests_ph1.py   (PH1_SHOTS=1 writes docs/screenshots/ph1-{plan,flow,journal,today-act}.png)"""
import os, sys
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, launch, check, results
import lrf_side as S
import run_tests_lrf2 as L2
import lr4_common as F4
import lr5b_common as JC
import rs2a_common as RC

HERE = os.path.dirname(os.path.abspath(__file__))
HIDE_NAV = "@media (max-width:600px){#tabsMain{display:none!important}}"
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")


def shot(page, name, sel=None, full=True):
    if not os.environ.get("PH1_SHOTS"): return
    os.makedirs(SHOTS, exist_ok=True); p = os.path.join(SHOTS, "ph1-%s.png" % name)
    if sel: page.query_selector(sel).screenshot(path=p)
    else: page.screenshot(path=p, full_page=full)


SW = """([x,y,dx,dy,ms,sel])=>new Promise(res=>{
  const tgt = sel ? document.querySelector(sel) : document.elementFromPoint(x,y);
  if(!tgt) return res('notarget');
  if(sel){ const r = tgt.getBoundingClientRect(); x = r.left + r.width/2; y = r.top + r.height/2; }
  const mk = (px,py)=>new Touch({identifier:1, target:tgt, clientX:px, clientY:py});
  const fire = (type, px, py)=>tgt.dispatchEvent(new TouchEvent(type, {bubbles:true, cancelable:true, touches:type==='touchend'?[]:[mk(px,py)], changedTouches:[mk(px,py)]}));
  fire('touchstart', x, y); fire('touchmove', x+dx/2, y+dy/2);
  setTimeout(()=>{ fire('touchend', x+dx, y+dy); res('ok'); }, ms);
})"""


def swipe(page, dx, dy=0, x=195, y=300, sel=None, ms=120):
    r = page.evaluate(SW, [x, y, dx, dy, ms, sel]); page.wait_for_timeout(450); return r


def watch(pw):
    tag = "[watch swipe 390]"
    b, page, pe, ce = RC.open_screen(pw, 390, 844)
    try:
        seg = lambda: js(page, "()=>wl1SegNow()")
        check(f"{tag} the swipe area keeps vertical scroll only (touch-action pan-y)", "pan-y" in js(page, "()=>getComputedStyle(document.getElementById('tabWatch')).touchAction"), js(page, "()=>getComputedStyle(document.getElementById('tabWatch')).touchAction"))
        # a real sideways-scrolling chip row in the swipe area
        js(page, """()=>{ const r = document.createElement('div'); r.id = 'ph1chips'; r.style.cssText = 'overflow-x:auto;white-space:nowrap;width:100%;height:44px;position:relative';
          r.innerHTML = '<span style="display:inline-block;width:1200px;height:40px">chips chips chips</span>'; const t = document.getElementById('tabWatch'); t.insertBefore(r, t.firstChild); window.scrollTo(0, 0); }""")
        page.wait_for_timeout(200)
        check(f"{tag} fixture row really scrolls sideways", js(page, "()=>{ const r = document.getElementById('ph1chips'); return r.scrollWidth > r.clientWidth + 1 }"))
        s0 = seg()
        y = js(page, "()=>{ const r = document.getElementById('ph1chips').getBoundingClientRect(); return Math.round(r.top + r.height / 2) }")
        swipe(page, 120, 5, y=y); swipe(page, -120, 5, y=y)
        check(f"{tag} swipe that STARTS on the chip row → no segment change", seg() == s0, [s0, seg()])
        js(page, "()=>document.getElementById('ph1chips').remove()"); page.wait_for_timeout(150)
        swipe(page, 120, 120, y=450)
        check(f"{tag} diagonal (|dx| = |dy|) → none", seg() == s0, [s0, seg()])
        swipe(page, 120, 5, y=450, ms=700)
        check(f"{tag} slower than 600 ms → none", seg() == s0, [s0, seg()])
        swipe(page, 59, 0, y=450)
        check(f"{tag} under 60 px → none", seg() == s0, [s0, seg()])
        swipe(page, 120, 50, y=450)
        s1 = seg()
        check(f"{tag} |dx| = 2.4 × |dy| and ≥ 60px within 600ms on the list → segment changes", s1 != s0, [s0, s1])
        check(f"{tag} no page errors", not pe, pe[:2])
    finally:
        b.close()


def plan(pw):
    tag = "[plan 390]"
    d, cs = S.fixture()
    b, page, ce, pe = launch(pw, 390, 844, d=d, c=cs)
    try:
        S.go(page, "plan"); page.add_style_tag(content=HIDE_NAV)
        h = js(page, """()=>[...document.querySelectorAll('.pc2-card[data-bd-status=plan]')].filter(c=>c.getClientRects().length).map(c=>{ const r = c.querySelector('.pv-r1'); const vis = [...r.children].filter(e=>e.getClientRects().length && e.getBoundingClientRect().width > 0);
          return {id:c.dataset.bdCard, cx:vis.some(e=>e.matches('[data-re4-card]')), dash:vis.some(e=>e.matches('[data-bd-pct=na]')), menu:vis.some(e=>e.querySelector('[data-pc2-menu]'))}; })""")
        check(f"{tag} plan card header: ⋯ present, no ✕, no stray —", len(h) >= 3 and all(x["menu"] and not x["cx"] and not x["dash"] for x in h), h)
        first = h[0]["id"]
        js(page, "(id)=>pc2Menu(id)", first); page.wait_for_timeout(250)
        m = js(page, "()=>[...document.querySelectorAll('[data-pc2-menupop] button')].filter(b=>b.getClientRects().length).map(b=>b.innerText.trim())")
        check(f"{tag} ⋯ menu: Edit plan + Cancel plan (the ✕ action, same label as its title)", m == ["Edit plan", "Cancel plan"], m)
        page.click("[data-pc2-cancel]"); page.wait_for_timeout(400)
        check(f"{tag} Cancel plan opens the same cancel-with-reason sheet as ✕ did", js(page, "()=>!!document.querySelector('[data-re4-sheet], [data-re4-reasons], .re4-sheet, [data-re4-open], #re4Pop') || /cancel/i.test((document.querySelector('.ui-sheet-backdrop, .overlay.show')||{innerText:''}).innerText)"))
        js(page, "()=>{ try{ document.querySelectorAll('.ui-sheet-backdrop, .overlay.show').forEach(e=>e.remove()); document.querySelectorAll('.overlay').forEach(e=>e.classList.remove('show')); }catch(e){} }")
        js(page, "()=>{ pc2MenuId = null; bdSeg = 'ord'; bdSetSeg && 0; bdRender(); }")
        js(page, "()=>{ for(const c of document.querySelectorAll('.pc2-card[data-bd-status=ord]')) c.remove(); }"); page.wait_for_timeout(200)
        js(page, "()=>{ const col = document.querySelector('[data-bd-col=ord]'); const n = col.querySelector('[data-bd-n]'); }")
        shot(page, "plan")
        check(f"{tag} no page errors", not pe, pe[:2])
    finally:
        b.close()
    # empty orders
    b, page, ce, pe = launch(pw, 390, 844, d=d, c={})
    try:
        S.go(page, "plan"); page.add_style_tag(content=HIDE_NAV)
        js(page, "()=>{ bdSeg = 'ord'; bdRender(); }"); page.wait_for_timeout(300)
        e = js(page, """()=>{ const n = document.querySelector('[data-pc2-empty]'); if(!n) return null; const v = [...n.children].filter(c=>c.getClientRects().length); const k = document.querySelector('.bd-k');
          return {vis:v.map(c=>c.innerText.trim()), lines:Math.round(n.getBoundingClientRect().height / 15), cls:v.map(c=>c.className)}; }""")
        check(f"{tag} empty orders = ONE label line 'AT BROKER · NONE' (section-label style)", e and e["vis"] == ["AT BROKER · NONE"] and "bd-k" in e["cls"][0], e)
    finally:
        b.close()
    b, page, ce, pe = launch(pw, 1440, 900, d=d, c={})
    try:
        S.go(page, "plan"); js(page, "()=>{ bdRender(); }"); page.wait_for_timeout(300)
        e = js(page, "()=>{ const n = document.querySelector('[data-pc2-empty]'); return n ? [...n.children].filter(c=>c.getClientRects().length).map(c=>c.innerText.replace(/\\s+/g,' ').trim()) : null }")
        check("[plan 1440] desktop unchanged: the two-line note stays", e and e[0].startswith("Nothing waiting at the broker.") and "AT BROKER" not in " ".join(e), e)
    finally:
        b.close()


def flow(pw):
    tag = "[flow 390]"
    b, page, pe = F4.open_flow(pw, 390, 844)
    try:
        page.add_style_tag(content=HIDE_NAV)
        r = js(page, """()=>[...document.querySelectorAll('[data-lr4-tile] .r2')].map(e=>{ const cs = getComputedStyle(e), lh = parseFloat(cs.lineHeight) || 16; return {t:e.innerText, ws:cs.whiteSpace, to:cs.textOverflow, lines:Math.round(e.scrollHeight / lh), clipped:e.scrollHeight > e.clientHeight + 1}; })""")
        check(f"{tag} catalyst text wraps (normal white-space, no ellipsis), ≤ 2 lines, nothing cut", r and all(x["ws"] == "normal" and x["to"] != "ellipsis" and x["lines"] <= 2 and not x["clipped"] for x in r) and any(x["lines"] == 2 for x in r), r)
        js(page, "()=>document.querySelector('[data-lr4-tile]').click()"); page.wait_for_timeout(250)
        check(f"{tag} tapping the card opens the full text panel", js(page, "()=>!!document.querySelector('[data-lr4-tile].open') && !!document.querySelector('.pv-flowpanel, [data-pv-flow], [data-bd-mc-panel]') || document.querySelector('[data-lr4-tile]').getAttribute('aria-expanded') === 'true'"))
        js(page, "()=>document.querySelector('[data-lr4-tile]').click()"); page.wait_for_timeout(200)
        g = js(page, "()=>{ const s = document.querySelector('.lr4-wksel').getBoundingClientRect(), i = document.querySelector('.lr4-wk i').getBoundingClientRect(), g = document.querySelector('.lr4-wkg').getBoundingClientRect(); return {gap:Math.round(i.left - s.right), ghost:Math.round(s.width - g.width), txt:document.querySelector('.lr4-wkg').innerText}; }")
        check(f"{tag} ▾ sits right after the date (gap ≤ 4px, select as wide as the date text)", abs(g["gap"]) <= 4 and abs(g["ghost"]) <= 2, g)
        d = js(page, """()=>{ const s = document.querySelector('#lr4Det > summary small'); if(!s) return null; const cs = getComputedStyle(s); return {ws:cs.whiteSpace, to:cs.textOverflow, full:s.scrollWidth <= s.clientWidth + 1, sw:document.documentElement.scrollWidth - innerWidth}; }""")
        check(f"{tag} Flow Details summary line wraps (no ellipsis, fully visible)", d and d["ws"] == "normal" and d["to"] != "ellipsis" and d["full"] and d["sw"] <= 0, d)
        shot(page, "flow")
        check(f"{tag} no page errors", not pe, pe[:2])
    finally:
        b.close()
    b, page, pe = F4.open_flow(pw, 1440, 900)
    try:
        r = js(page, "()=>[...document.querySelectorAll('[data-lr4-tile] .r2')].every(e=>getComputedStyle(e).whiteSpace === 'nowrap' && getComputedStyle(e).textOverflow === 'ellipsis')")
        check("[flow 1440] desktop unchanged: catalyst stays one line with ellipsis", r)
        r = js(page, "()=>getComputedStyle(document.querySelector('#lr4Det > summary small')).textOverflow")
        check("[flow 1440] desktop unchanged: Details summary keeps its ellipsis", r == "ellipsis", r)
    finally:
        b.close()


def journal(pw):
    tag = "[journal 390]"
    b, page, pe = JC.open_journal(pw, 390, 844)
    try:
        page.add_style_tag(content=HIDE_NAV)
        js(page, "()=>lrSwPick('journal','both')"); page.wait_for_timeout(300)
        d = js(page, """()=>{ const s = document.querySelector('#lr5Det > summary small'); if(!s) return null; const cs = getComputedStyle(s), lh = parseFloat(cs.lineHeight) || 16; return {ws:cs.whiteSpace, to:cs.textOverflow, ov:cs.overflow, lines:Math.round(s.getBoundingClientRect().height / lh), full:s.scrollWidth <= s.clientWidth + 1, sw:document.documentElement.scrollWidth - innerWidth}; }""")
        check(f"{tag} Details summary line wraps (no ellipsis, fully visible, no sideways scroll)", d and d["ws"] == "normal" and d["to"] != "ellipsis" and d["full"] and d["sw"] <= 0, d)
        page.evaluate("()=>document.getElementById('lr5Det').scrollIntoView()"); page.wait_for_timeout(200)
        shot(page, "journal", full=False)
        check(f"{tag} no page errors", not pe, pe[:2])
    finally:
        b.close()


def today(pw):
    tag = "[today 390]"
    d, cs = S.fixture()
    b, page, ce, pe = launch(pw, 390, 844, d=d, c=cs)
    try:
        L2.go(page); page.add_style_tag(content=HIDE_NAV)
        js(page, "()=>{ todayRefresh(true); }"); page.wait_for_timeout(300)
        t = js(page, """()=>{ const h = document.querySelector('.lr2-act .lr2-head'); const o = h.querySelector('[data-lr2-orisk]'); const x = h.querySelector('[data-au2-exec]'); return {txt:o.innerText.replace(/\\s+/g,' ').trim(), au:x ? {vis:x.getClientRects().length > 0, y:x.dataset.au2Y, none:x.hasAttribute('data-au2-none')} : null}; }""")
        check(f"{tag} Act header: Open risk … with no stray '· —'", "—" not in t["txt"] and (t["au"] is None or t["au"]["y"] != "0" or not t["au"]["vis"]), t)
        shot(page, "today-act", sel=".lr2-act")
        check(f"{tag} no page errors", not pe, pe[:2])
    finally:
        b.close()
    b, page, ce, pe = launch(pw, 1440, 900, d=d, c=cs)
    try:
        L2.go(page)
        t = js(page, "()=>{ const x = document.querySelector('.lr2-act [data-au2-exec]'); return x ? [x.getClientRects().length > 0, x.innerText.replace(/\\s+/g,' ')] : null }")
        check("[today 1440] desktop unchanged: the Placed chip keeps its long text", t is None or (t[0] and "Placed" in t[1]), t)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        watch(pw); plan(pw); flow(pw); journal(pw); today(pw)
    bad = [r for r in results if not r[1]]
    print("SUMMARY ph1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
