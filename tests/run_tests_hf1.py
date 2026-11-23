#!/usr/bin/env python3
"""HF1 — Today › Act rows on <=760: the action sits INSIDE the card on its own bottom line (hairline above, right-aligned); no overlap between cards / labels; To do + Ideas rows checked too. Desktop unchanged.
Run: python3 tests/run_tests_hf1.py   (HF1_SHOTS=1 writes docs/screenshots/hf1-today-act-390.png)"""
import sys, os
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, launch, check, results
from re1c_common import tr
import run_tests_lrf2 as L2, lrf_side as S
import nt1_common as N
import run_tests_nt1b as B
import run_tests_nt2 as P2
import run_tests_nt2c as C2

HERE = os.path.dirname(os.path.abspath(__file__))
HIDE_NAV = "@media (max-width:600px){#tabsMain{display:none!important}}"

# every visible item of `sel` must be boxed by its card, and consecutive boxes (cards + section labels) must not overlap vertically
BOX = """([sel, tol = 0.5])=>{ const bad = [], rows = [...document.querySelectorAll(sel)].filter(r=>r.getClientRects().length);
  rows.forEach(r=>{ const c = r.getBoundingClientRect(); r.querySelectorAll('*').forEach(e=>{ if(!e.getClientRects().length) return; const b = e.getBoundingClientRect(); if(!b.width || !b.height) return;
    if(b.bottom > c.bottom + tol || b.top < c.top - tol || b.right > c.right + tol || b.left < c.left - tol) bad.push((r.dataset.re2Row || r.className) + ' > ' + e.className); }); });
  const boxes = [...document.querySelectorAll(sel + ', .lr2-act .re2-col .ch')].filter(r=>r.getClientRects().length).map(r=>r.getBoundingClientRect()).sort((a,b)=>a.top-b.top);
  const ov = []; for(let i = 1; i < boxes.length; i++) if(boxes[i].top < boxes[i-1].bottom - 0.5 && boxes[i].left < boxes[i-1].right && boxes[i].right > boxes[i-1].left) ov.push([Math.round(boxes[i-1].bottom), Math.round(boxes[i].top)]);
  return {n: rows.length, bad: bad.slice(0, 6), ov, sw: document.documentElement.scrollWidth - innerWidth}; }"""


def act_fixture():
    d, cs = S.fixture()
    d["books"]["main"]["trades"].append(tr(id="h1", sym="NVDA", cur="USD", qty=40, entry=100, sl=90, posGroup="h1", sl0=90))
    cs["hN"] = {"acct": "main", "ticker": "NVDA", "market": "US", "strategy": "W", "status": "open", "trade_id": "h1", "stopHistory": [], "lots": [{"n": 1, "px": 100, "qty": 40}], "plan": {"entry": 100, "stop": 90}, "px": 116, "pxDate": "2026-10-02"}
    d["books"]["main"]["trades"].append(tr(id="h2", sym="KO", cur="USD", qty=60, entry=100, sl=90, posGroup="h2", sl0=90))
    cs["hK"] = {"acct": "main", "ticker": "KO", "market": "US", "strategy": "W", "status": "open", "trade_id": "h2", "stopHistory": [], "lots": [{"n": 1, "px": 100, "qty": 60}], "plan": {"entry": 100, "stop": 90}, "px": 116, "pxDate": "2026-10-02"}
    return d, cs


def act(pw, w, h, shot=False):
    tag = "[act %d]" % w
    d, cs = act_fixture()
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    try:
        L2.go(page); page.add_style_tag(content=HIDE_NAV)
        js(page, "()=>{ re2GrpAll = {enter:true, check:true, manage:true}; todayRefresh(true); }"); page.wait_for_timeout(400)
        g = js(page, "()=>[...document.querySelectorAll('.re2-row')].filter(r=>r.getClientRects().length).map(r=>r.dataset.re2Grp)")
        check(f"{tag} fixture shows Enter + Manage (Stop ›, Homework) rows", g.count("enter") >= 1 and g.count("manage") >= 2, g)
        o = js(page, BOX, [".lr2-act .re2-row"])
        check(f"{tag} every action / child box inside its card · no overlap between consecutive cards + section labels · no sideways scroll", o["n"] >= 4 and not o["bad"] and not o["ov"] and o["sw"] <= 0, o)
        a = js(page, """()=>[...document.querySelectorAll('.lr2-act .re2-row')].filter(r=>r.getClientRects().length).map(r=>{ const q = r.querySelector('.re2-btns'), m = r.querySelector('.re2-main'), cs = getComputedStyle(q), c = r.getBoundingClientRect(), qb = q.getBoundingClientRect(), mb = m.getBoundingClientRect();
          const vis = [...q.querySelectorAll('button')].filter(x=>x.getClientRects().length), nums = [...r.querySelectorAll('.num')].filter(x=>x.getClientRects().length);
          return {s:r.dataset.re2Row, has:vis.length > 0, below:qb.top >= mb.bottom - 0.5, right:vis.length ? Math.round(c.right - vis[vis.length-1].getBoundingClientRect().right) : null, hair:cs.borderTopWidth + ' ' + cs.borderTopStyle, pad:parseFloat(getComputedStyle(r).paddingBottom), gapBottom:vis.length ? Math.round(c.bottom - vis[0].getBoundingClientRect().bottom) : null,
            ell:nums.some(n=>getComputedStyle(n).textOverflow === 'ellipsis' && getComputedStyle(n).overflow !== 'visible'), clip:nums.some(n=>n.scrollWidth > n.clientWidth + 1 && getComputedStyle(n).overflow !== 'visible')}; })""")
        wb = [x for x in a if x["has"]]
        check(f"{tag} action on its own bottom line: below the text · hairline above · right-aligned (right inset = card padding) · bottom inset = card padding", wb and all(x["below"] and x["hair"] == "1px solid" and abs(x["right"] - x["pad"] - 1) <= 3 and abs(x["gapBottom"] - x["pad"] - 1) <= 3 for x in wb), wb)
        check(f"{tag} detail line wraps — no ellipsis, no clipping", a and not any(x["ell"] or x["clip"] for x in a), a)
        kinds = js(page, "()=>[...document.querySelectorAll('.lr2-act .re2-row [data-re2-btn]')].filter(b=>b.getClientRects().length).map(b=>({k:b.dataset.re2Btn, row:b.closest('.re2-row').dataset.re2Row, dis:b.disabled, html:b.outerHTML.slice(0,120), bg:getComputedStyle(b).backgroundColor, cls:b.className}))")
        pl = [k for k in kinds if k["k"] == "place" and "data-nt1b-sec" not in k["html"]]; hw = [k for k in kinds if k["k"] == "hw"]   # NT1b: only the first Place is dark, the rest are secondary
        dark = lambda bg: sum(map(int, bg[4:-1].split(","))) < 200
        check(f"{tag} primary Place stays the dark button · Homework stays the quiet link (no fill)", pl and all(dark(k["bg"]) for k in pl) and hw and all(k["bg"] == "rgba(0, 0, 0, 0)" and "mute" in k["cls"] for k in hw), kinds)
        # To do / Risk side column rows
        t = js(page, BOX, [".lr2-ti"])
        check(f"{tag} To do rows: nothing past the row · rows do not overlap · no sideways scroll", not t["bad"] and not t["ov"] and t["sw"] <= 0, t)
        if shot:
            page.query_selector(".lr2-act").screenshot(path=os.path.join(HERE, "..", "docs", "screenshots", "hf1-today-act-390.png"))
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def desktop(pw):
    tag = "[act 1440]"
    d, cs = act_fixture()
    b, page, ce, pe = launch(pw, 1440, 900, d=d, c=cs)
    try:
        L2.go(page)
        a = js(page, """()=>[...document.querySelectorAll('.lr2-act .re2-row')].filter(r=>r.getClientRects().length).map(r=>{ const q = r.querySelector('.re2-btns'), m = r.querySelector('.re2-main'), qb = q.getBoundingClientRect(), mb = m.getBoundingClientRect(), cs = getComputedStyle(q); return {s:r.dataset.re2Row, side:qb.left >= mb.right - 1, sameLine:qb.top < mb.bottom, hair:cs.borderTopWidth}; })""")
        check(f"{tag} desktop unchanged: action stays to the right of the text, no hairline", a and all(x["side"] and x["sameLine"] and x["hair"] == "0px" for x in a), a)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def ideas(pw, w):
    tag = "[ideas %d]" % w
    b, page, pe = N.open_nt1(pw, w, 844, my_docs=False, notes=False)
    try:
        page.add_style_tag(content=HIDE_NAV)
        t0 = B.td(page); now = P2.now_iso(page)
        B.quiet_fixture_ai(page)
        C2.seed_ai_rich(page, "ai-late", "US 30 Outperform", B.add(t0, -16))
        B.seed_my(page, {"x": P2.idea(1, ("sat", "XAU"), "Opportunity to Buy Gold", t0, B.add(t0, 9), scs=[P2.sc("pullback", 3290, 3340)], view="bull", lastPx={"v": 3650, "at": now}),
                         "y": P2.idea(2, ("sat", "BTC"), "Pullback to 82k", t0, B.add(t0, 9), scs=[P2.sc("pullback", 80000, 82000)], view="bull", lastPx={"v": 95000, "at": now})})
        B.to_today(page)
        o = js(page, BOX, ["[data-nt1b-it], [data-nt2c-watch]", 2])   # pills sit 1px low in the baseline too (not HF1)
        check(f"{tag} Ideas rows: every child inside its card · rows do not overlap · no sideways scroll", o["n"] >= 3 and not o["bad"] and not o["ov"] and o["sw"] <= 0, o)
        t = js(page, BOX, [".lr2-ti"])
        check(f"{tag} To do rows: nothing past the row · rows do not overlap", not t["bad"] and not t["ov"], t)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        act(pw, 390, 844, shot=bool(os.environ.get("HF1_SHOTS")))
        for w, h in ((360, 740), (700, 900)): act(pw, w, h)
        desktop(pw)
        for w in (390, 700): ideas(pw, w)
    bad = [r for r in results if not r[1]]
    print("SUMMARY hf1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
