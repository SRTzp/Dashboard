#!/usr/bin/env python3
"""LN4c — Today status card (iPhone/Mac) + screenshots (390 viewport · 1280)"""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase24 as P24
import run_tests_phase106 as T
import run_tests_phase120 as P120
js, settle = C.js, T.settle
results = []
def check(n, ok, d=""):
    results.append((n, bool(ok)));
    print(("PASS" if ok else "FAIL") + " - " + n + ((" :: " + json.dumps(d, ensure_ascii=False)[:500]) if not ok else ""))

def run(pw, w, h):
    tag = f"[{w}]"
    b, page, ce, pe = T.launch(pw, w, h, iso=T.NOW, picks=("XAUUSD",), weekly=False)
    try:
        P24.set_ff(page, P24.ff_json(False, False))
        P120.ps_on(page)
        T.go_today(page); settle(page, 500)
        info = js(page, """()=>{ const q=s=>document.querySelector(s); const st=q('[data-ln4-status]'); const sw=q('[data-td3-sw]').getBoundingClientRect(), rg=q('[data-td3-rg]').getBoundingClientRect(), hot=q('[data-ln4-hot]'), ch=[...document.querySelectorAll('[data-ln4-portpill]')];
          return {chips:ch.map(e=>e.innerText), swSameRowAsRegime:Math.abs((sw.top+sw.height/2)-(rg.top+rg.height/2))<10, rgTxt:q('[data-td3-rg]').innerText, room:!!q('[data-ln4-room]'), wl:!!q('[data-ln4-wl]'), top:st.getBoundingClientRect().top, hotTop: hot?hot.getBoundingClientRect().top:null, swTop:sw.top, swBottom:sw.bottom}; }""")
        check(f"{tag} single merged port chip", len(info["chips"]) == 1 and "MMT" in info["chips"][0] and "COMP" in info["chips"][0] and "(regime)" in info["chips"][0], info)
        check(f"{tag} room present once", info["room"], info)
        if w <= 560:
            check(f"{tag} switch on regime line (right), no lone switch row", info["swSameRowAsRegime"], info)
            check(f"{tag} regime shows label only (no W/L)", "W " not in info["rgTxt"] and "L " not in info["rgTxt"], info)
            if info["hotTop"]: check(f"{tag} ≤3 lines before HOT", info["hotTop"] - info["top"] <= 120, info)
        js(page, "()=>{ window.ln4HotSectors = ()=>[...['A','B','C','D','E'].map((x,i)=>({etf:'X'+x,name:'Sector '+x,k:i<3?'lead':'fresh',star:false,hot:true,ratio:5-i})), {etf:'XS',name:'Starred',k:'star',star:true,hot:false,ratio:0}]; todayRefresh(true); }"); settle(page, 400)
        hot = js(page, "()=>({vis:[...document.querySelectorAll('[data-ln4-hotchip]')].filter(e=>e.getBoundingClientRect().height>0).length, more:[...document.querySelectorAll('[data-ln4-hotmore]')].filter(e=>e.getBoundingClientRect().height>0).map(e=>e.innerText), cls:[...document.querySelectorAll('[data-ln4-hotchip]')].map(e=>e.className)})")
        if w >= 900:
            check(f"{tag} 5 HOT + 1 ★ all visible, no +N", hot["vis"] == 6 and not hot["more"], hot)
        check(f"{tag} Leading teal (p-g) · Fresh blue (p-b) · never amber", any("p-g" in c for c in hot["cls"]) and any("p-b" in c for c in hot["cls"]) and not any("p-a" in c for c in hot["cls"]), hot)
        C.shot(page, f"ln4c-today-{w}.png")
        check(f"{tag} no errors", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

if __name__ == "__main__":
    with sync_playwright() as pw:
        run(pw, 390, 844); run(pw, 1280, 800); run(pw, 1440, 900)
    n = sum(1 for r in results if r[1]); print(f"\n{n}/{len(results)} PASS"); sys.exit(0 if n == len(results) else 1)
