#!/usr/bin/env python3
"""SW2 — iPhone 390 content-area swipe: Today Daily|Weekend · Plan Core|Sat. synthetic touch events."""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase106 as T

results = []
js, settle = C.js, T.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + json.dumps(detail, ensure_ascii=False)[:500]) if not ok else ""))


SW = """([x,y,dx,dy,ms,sel])=>new Promise(res=>{
  const tgt = sel ? document.querySelector(sel) : document.elementFromPoint(x,y);
  if(!tgt) return res('notarget');
  if(sel){ const r = tgt.getBoundingClientRect(); x = r.left + r.width/2; y = r.top + r.height/2; }
  const mk = (px,py)=>new Touch({identifier:1, target:tgt, clientX:px, clientY:py});
  const fire = (type, px, py, list)=>tgt.dispatchEvent(new TouchEvent(type, {bubbles:true, cancelable:true, touches:type==='touchend'?[]:[mk(px,py)], changedTouches:[mk(px,py)]}));
  fire('touchstart', x, y);
  fire('touchmove', x+dx/2, y+dy/2);
  setTimeout(()=>{ fire('touchend', x+dx, y+dy); res('ok'); }, ms);
})"""


def swipe(page, dx, dy=0, x=195, y=300, ms=120, sel=None):
    r = page.evaluate(SW, [x, y, dx, dy, ms, sel]); settle(page, 350); return r


def mode(page): return js(page, "()=>td3Mode")
def scope(page): return js(page, "()=>planScope")
def tab(page): return js(page, "()=>activeTab")


def run(pw):
    b, page, ce, pe = T.launch(pw, 390, 844, iso=T.NOW, picks=("XAUUSD",), weekly=False)
    import re; page.route(re.compile(r"investing\.com"), lambda route: route.fulfill(status=200, content_type="text/html", body="<html><body></body></html>"))   # PB1d: calendar iframe = no real network
    try:
        js(page, "()=>{ try{localStorage.removeItem('dash.sw2Hint.today');localStorage.removeItem('dash.sw2Hint.plan');}catch(e){} }")
        T.go_today(page)
        js(page, "()=>sk1ModeSet('d')"); js(page, "()=>todayRefresh(true)"); settle(page, 400)
        # a probe button to detect trailing clicks
        js(page, "()=>{ window.__clicks=0; const b=document.createElement('button'); b.id='swProbe'; b.textContent='probe'; b.style.cssText='position:fixed;left:150px;top:200px;width:90px;height:40px;z-index:1'; b.onclick=()=>window.__clicks++; document.body.appendChild(b); }")
        # Today
        swipe(page, -120, 5, y=500)
        check("today: swipe left → Weekend", mode(page) == 'w', mode(page))
        check("today: hint toast shown once", js(page, "()=>document.getElementById('td3Toast') && document.getElementById('td3Toast').style.display==='flex' && /Daily \\/ Weekend/.test(document.getElementById('td3Toast').innerText)"))
        swipe(page, -120, 5, y=500)
        check("today: swipe left again → stays Weekend (no wrap)", mode(page) == 'w', mode(page))
        swipe(page, 120, -5, y=500)
        check("today: swipe right → Daily", mode(page) == 'd', mode(page))
        swipe(page, 120, -5, y=500)
        check("today: swipe right on Daily → stays", mode(page) == 'd', mode(page))
        check("today: stays on Today (never changes main tab)", tab(page) == 'today', tab(page))
        check("today: manual switch persisted for the day (SK1)", js(page, "()=>{ const o=JSON.parse(localStorage.getItem('dash.td3ModeDay')||'null'); return o && o.m==='d'; }"))
        js(page, "()=>{ document.getElementById('td3Toast').style.display='none'; }")
        swipe(page, -120, 5, y=500)
        check("today: hint not shown a second time", js(page, "()=>document.getElementById('td3Toast').style.display!=='flex'"))
        swipe(page, 120, 0, y=500)
        # ignores
        swipe(page, -120, 0, y=500, x=10)
        check("ignored: starts within 20px of the edge", mode(page) == 'd', mode(page))
        swipe(page, -120, 0, y=500, x=382)
        check("ignored: starts within 20px of the right edge", mode(page) == 'd', mode(page))
        swipe(page, -100, 80, y=500)
        check("ignored: mostly-vertical drag", mode(page) == 'd', mode(page))
        swipe(page, -50, 0, y=500)
        check("ignored: < 60px", mode(page) == 'd', mode(page))
        swipe(page, -120, 0, y=500, ms=700)
        check("ignored: slower than 600 ms", mode(page) == 'd', mode(page))
        swipe(page, -120, 0, sel='[data-td3-sw]')
        check("ignored: starts on the Daily|Weekend switch", mode(page) == 'd', mode(page))
        js(page, "()=>{ const i=document.createElement('input'); i.id='swIn'; i.style.cssText='position:fixed;left:20px;top:300px;width:200px;height:36px;z-index:1'; document.body.appendChild(i); }")
        swipe(page, -120, 0, sel='#swIn')
        check("ignored: starts on an input", mode(page) == 'd', mode(page))
        js(page, "()=>document.getElementById('swIn').focus()")
        swipe(page, -120, 0, y=600)
        check("ignored: an input is focused", mode(page) == 'd', mode(page))
        js(page, "()=>{ document.getElementById('swIn').blur(); document.getElementById('swIn').remove(); }")
        js(page, "()=>{ const t=document.createElement('div'); t.id='swTw'; t.className='tablewrap'; t.style.cssText='position:fixed;left:20px;top:300px;width:300px;height:60px;z-index:1;background:#eee'; document.body.appendChild(t); const s=document.createElement('div'); s.id='swSc'; s.style.cssText='position:fixed;left:20px;top:400px;width:300px;height:60px;z-index:1;overflow-x:auto;background:#ddd'; s.innerHTML='<div style=\"width:900px;height:40px\">x</div>'; document.body.appendChild(s); }")
        swipe(page, -120, 0, sel='#swTw')
        check("ignored: starts on a table", mode(page) == 'd', mode(page))
        swipe(page, -120, 0, sel='#swSc')
        check("ignored: starts on a horizontally scrollable row", mode(page) == 'd', mode(page))
        js(page, "()=>{ document.getElementById('swTw').remove(); document.getElementById('swSc').remove(); }")
        js(page, "()=>{ const o=document.querySelector('.overlay'); if(o) o.classList.add('show'); window.__ov=!!o; }")
        if js(page, "()=>window.__ov"):
            swipe(page, -120, 0, y=500)
            check("ignored: a sheet/overlay is open", mode(page) == 'd', mode(page))
            js(page, "()=>document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'))")
        # click swallowing
        swipe(page, -120, 0, sel='#swProbe')
        # (probe is a start target; do swipe from elsewhere ending on probe, then click it)
        js(page, "()=>sk1ModeSet('d')"); js(page, "()=>todayRefresh(true)"); settle(page, 300)
        page.evaluate(SW, [195, 500, -120, 0, 100, None]); js(page, "()=>document.getElementById('swProbe').click()")
        page.evaluate("()=>document.getElementById('swProbe').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))")
        settle(page, 200)
        check("swipe: trailing click is swallowed", js(page, "()=>window.__clicks") == 0, js(page, "()=>window.__clicks"))
        settle(page, 500)
        before = js(page, "()=>window.__clicks")
        page.evaluate("()=>document.getElementById('swProbe').dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}))")
        check("click works again after the swipe window", js(page, "()=>window.__clicks") == before + 1)
        js(page, "()=>document.getElementById('swProbe').remove()")
        # Bottom bar still switches main tabs; content never does
        t0 = tab(page)
        swipe(page, -120, 0, sel='#tabsMain button')
        check("bottom bar: swipe still changes main tab", tab(page) != t0, [t0, tab(page)])
        # Plan (PB1: content swipe switches the status segment Planned | Ordered | Holding)
        js(page, "()=>{ switchTab('today'); switchTab('plan'); bdSetSeg('plan'); }"); settle(page, 600)
        seg = lambda: js(page, "()=>bdSeg")
        swipe(page, -120, 0, y=500)
        check("plan: swipe left → Ordered", seg() == 'ord', seg())
        check("plan: hint toast shown", js(page, "()=>/Planned \\/ Ordered \\/ Holding/.test((document.getElementById('td3Toast')||{innerText:''}).innerText)"))
        swipe(page, -120, 0, y=500)
        check("plan: swipe left → Holding", seg() == 'hold', seg())
        swipe(page, -120, 0, y=500)
        check("plan: swipe left on Holding → stays (no wrap)", seg() == 'hold', seg())
        swipe(page, 120, 0, y=500); swipe(page, 120, 0, y=500)
        check("plan: swipe right ×2 → Planned", seg() == 'plan', seg())
        swipe(page, 120, 0, y=500)
        check("plan: swipe right on Planned → stays", seg() == 'plan', seg())
        check("plan: never changes main tab", tab(page) == 'plan', tab(page))
        # other tabs: nothing
        js(page, "()=>switchTab('journal')"); settle(page, 400)
        swipe(page, -120, 0, y=500)
        check("other tabs: content swipe does nothing", tab(page) == 'journal', tab(page))
        # reduced motion: no animation
        ctxrm = js(page, "()=>{ let n=0; const o=Element.prototype.animate; Element.prototype.animate=function(){ n++; return o.apply(this, arguments); }; window.__an=()=>n; return 1; }")
        js(page, "()=>switchTab('today')"); settle(page, 400)
        js(page, "()=>sk1ModeSet('d')"); js(page, "()=>todayRefresh(true)"); settle(page, 300)
        swipe(page, -120, 0, y=500)
        check("slide animation runs (motion allowed)", js(page, "()=>window.__an()") >= 1, js(page, "()=>window.__an()"))
        page.emulate_media(reduced_motion="reduce")
        n0 = js(page, "()=>window.__an()")
        swipe(page, 120, 0, y=500)
        check("reduced motion: no animation", js(page, "()=>window.__an()") == n0 and mode(page) == 'd', [n0, mode(page)])
        check("no console/page errors", not ce and not pe, [ce[:3], pe[:3]])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        try: run(pw)
        except Exception:
            import traceback; traceback.print_exc(); check("crashed", False, "see trace")
    n = sum(1 for r in results if r[1])
    print(f"\n{n}/{len(results)} PASS")
    sys.exit(0 if n == len(results) else 1)
