#!/usr/bin/env python3
"""light-lock hotfix — the app is light only. With colorScheme 'dark' emulated at 390, Today · Plan · confirm sheet
must equal the light render (computed colours of every element + screenshot diff ~ 0). Also: glance band mood / next news on separate lines.
Screenshots (tests/screenshots, git add -f): light-today-390 · dark-today-390"""
import os, sys, io
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import run_tests_lr3 as L3

SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
COLORS = """()=>[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().width>0).map((e,i)=>{const c=getComputedStyle(e);return i+':'+e.tagName+'|'+c.color+'|'+c.backgroundColor+'|'+c.borderTopColor+'|'+c.fill})"""

def snap(page, name):
    return page.screenshot()

def view(page, which):
    if which == "today":
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }")
    elif which == "plan":
        L3.goto_plan(page, "main")
    else:
        L3.goto_plan(page, "main"); js(page, "()=>efCorePlaceOpen('mN')")
    page.wait_for_timeout(500)

def main():
    with sync_playwright() as pw:
        b, page, ce, pe = launch(pw, 390, 844, c=L3.cards_board())
        out = {}
        for scheme in ("light", "dark"):
            page.emulate_media(color_scheme=scheme); page.wait_for_timeout(200)
            for v in ("today", "plan", "sheet"):
                view(page, v)
                out[(scheme, v)] = (js(page, COLORS), snap(page, v))
                if v == "today": page.screenshot(path=os.path.join(SHOTS, scheme + "-today-390.png"))
                if v == "sheet": js(page, "()=>{ try{ if(bdPopOpen()) bdPopClose(); }catch(e){} }")
        for v in ("today", "plan", "sheet"):
            cl, il = out[("light", v)]; cd, idk = out[("dark", v)]
            check(f"{v}: computed colours identical light vs dark-emulated ({len(cl)} elements)", cl == cd, [x for x in zip(cl, cd) if x[0] != x[1]][:3])
            check(f"{v}: screenshot diff = 0 (pixel-identical PNG)", il == idk, (len(il), len(idk)))
        check("html data-theme=light · color-scheme meta light", js(page, "()=>document.documentElement.dataset.theme==='light' && document.querySelector('meta[name=color-scheme]').content==='light'"))
        check("page color-scheme is light under dark emulation", js(page, "()=>getComputedStyle(document.documentElement).colorScheme") in ("light", "only light"))
        view(page, "today")
        g = js(page, "()=>{const m=document.querySelector('[data-lr2-phone] .lr2-mood'), n=document.querySelector('[data-lr2-phone] .lr2-nx'); if(!m||!n) return {m:!!m,n:!!n}; const a=m.getBoundingClientRect(), c=n.getBoundingClientRect(); return {mb:a.bottom, nt:c.top, ml:a.left, nl:c.left, over: !(a.bottom<=c.top+0.5)}}")
        check("Today 390: mood and next-news on separate lines (no overlap)", g and g.get("over") is False, g)
        check("no console/page errors", not ce and not pe, (ce[:2], pe[:2]))
        b.close()
    f = [r for r in results if not r[1]]
    print(f"{len(results)-len(f)}/{len(results)} PASS"); sys.exit(1 if f else 0)

if __name__ == "__main__": main()
