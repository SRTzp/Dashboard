#!/usr/bin/env python3
"""PL2c screenshots @390/1024/1440 -> docs/briefs/PL2c-screens/ (sample data)"""
import os, json
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase107 as T
import run_tests_phase111 as P111
import run_tests_phase44 as P44
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "briefs", "PL2c-screens"); os.makedirs(OUT, exist_ok=True)
js, settle = C.js, T.settle
LOG = []
def snap(page, name, w, sel=None):
    path = os.path.join(OUT, f"{name}-{w}.png"); page.wait_for_timeout(700)
    if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=path)
    else: page.screenshot(path=path)
    LOG.append(f"{name}-{w}: overflow={C.overflow(page)}")
def run(pw, w, h):
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        js(page, "()=>wlCol().doc('MTA').set({ticker:'MTA', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', ladder_watch:true, ladder_watch_set:true, my_thesis:{why:'SAMPLE why', updated_at:'2026-10-02T00:00:00Z'}, next_check_date:'2026-11-20', next_check_note:'Q3'})")
        js(page, "()=>wlCol().doc('MTB').set({ticker:'MTB', market:'TH', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'})")
        P44.reload_keep(page)
        js(page, "()=>switchTab('plan')"); settle(page, 900)
        snap(page, "plan-header", w)
        info = js(page, """()=>{const t=document.querySelector('.topbar'),tb=document.getElementById('tabsMain'),hb=t.querySelector('.hbtns'),sc=t.querySelector('.scopeTabs');
          const r=e=>e?e.getBoundingClientRect():null; const a=r(tb),b=r(sc),c=r(hb); return {tabs:a&&[a.left,a.right],scope:b&&[b.left,b.right,b.height],hb:c&&[c.left,c.right],topH:r(t).height}}""")
        LOG.append(f"plan-header-{w}: {json.dumps(info)}")
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 700); snap(page, "watchlist-rows", w)
        js(page, "()=>{ wlOpen('MTA'); wlSetSub('view'); }"); settle(page, 900); snap(page, "my-thesis", w)
    finally: b.close()
if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1024, 768), (1440, 900)): run(pw, w, h)
    print("\n".join(LOG)); open(os.path.join(OUT, "LOG.txt"), "w").write("\n".join(LOG))
