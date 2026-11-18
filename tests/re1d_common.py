#!/usr/bin/env python3
"""RE-D shared helpers (copied from run_tests_re1c2 so importing does not run that suite). Output goes inside the running worktree (HERE)."""
import json, os, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1c_common as K
from re1c_common import js, doc_c, cards, tr
import lib_phase39 as P39

HERE = os.path.dirname(os.path.abspath(__file__)); SHOTS = os.path.join(HERE, "screenshots")
results = []
PREFIX = 're1d'
NOANIM = "*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:600]) if (not ok and d) else ""))


def launch(pw, w, h, d=None, c=None):
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=d or doc_c(), cards=c if c is not None else cards(), clean=True)
    page.add_style_tag(content=NOANIM); page.wait_for_timeout(500)
    js(page, "()=>{ if(typeof lr2DetOpen !== 'undefined') lr2DetOpen = true; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)   # LR2: phone keeps Details (risk room) open in tests · Setup ✓ present (board treats plans without it as Waiting)
    return b, page, ce, pe


def refresh(page):
    js(page, "()=>{ re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(350)


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "re1d-%s.png" % name))


def no_overflow(page):
    return js(page, "()=>{ const w=document.documentElement.clientWidth; return document.documentElement.scrollWidth<=w+1 && document.body.scrollWidth<=w+1; }")


def rows(page, grp):
    return js(page, "(g)=>[...document.querySelectorAll('[data-re2-grp=\"'+g+'\"]')].map(r=>({sym:r.dataset.re2Row, t:r.innerText.replace(/\\s+/g,' '), btn:(r.querySelector('button')||{}).dataset?.re2Btn||'', dis:!!(r.querySelector('button')||{}).disabled}))", grp)


def txt(page, sel):
    return js(page, "(s)=>{const e=document.querySelector(s);return e?e.innerText.replace(/\\s+/g,' '):''}", sel)


def override(page, body):
    """display-layer test hook: tweak the engine result the strip reads (shallow copy)"""
    js(page, "(b)=>{ if(!window.__re1L) window.__re1L = re1L; const o = window.__re1L; re1L = a=>{ const L = o(a); if(!L) return L; const C = Object.assign({}, L); (new Function('L','C', b))(L, C); return C; }; re1Cache = {}; todayRefresh(true); }", body)
    page.wait_for_timeout(350)


def plan_card(sym, entry, stop, px=None, ready=False, **kw):
    c = {"acct": "main", "ticker": sym, "market": "US", "strategy": "W", "status": "plan", "plan": {"entry": entry, "stop": stop, "ps1": {"rows": [{"px": entry, "qty": 40}]}}}
    if px is not None: c["px"] = px; c["pxDate"] = "2026-10-02"
    if ready: c["plan"]["ready"] = True
    c.update(kw); return c


def seed(page, cs):
    for cid, c in cs.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    js(page, "()=>{ coreStop(); coreStart(); }"); page.wait_for_timeout(700); refresh(page)


