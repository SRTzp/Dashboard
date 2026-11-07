#!/usr/bin/env python3
"""RR3 — Flow › Leadership: list never empty while refreshing + header layout (1440 / 390, light + dark). รัน: python3 tests/rr3_check.py"""
import json, sys, os
import ln3fix_common as C
from rrg1b_check import HELPERS
from playwright.sync_api import sync_playwright

js = C.js
results = []
SHOTS = os.path.join(os.path.dirname(__file__), "..", "docs", "shots", "rr3")


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:700]) if (d and not ok) else ""))


SEED = r"""()=>{
  const f = ffState();
  const mk = (s,i)=>({sym:s,name:s+' n',quad:['lead','imp','weak','lag'][i%4],ratio:101,mom:101,dMom:(i%3?0.6:0.05),dRatio:0.1,days:(i%5)+1,prevDays:8,off52:-3,date:'2026-11-04',model:RRG_MODEL,eps:0.02,delta:0.01,rsTrend:i%2?-0.4:0.4,rawChg:0.1,rel:i%2?'neg':'pos',momUp:true,lag:5,bars:300,close:101,benchClose:100,pt:'up',ptEma:100,ptEmaPrev:99,ptN:50,ptLag:5,lastObs:'2026-11-04'});
  const syms = RRG_SYMS.map(d=>d.s);
  f.rrgTf = 'D'; localStorage.removeItem('dash.ps1Off'); localStorage.setItem('rrgFreshOnly','0');
  f.rrg = {rowsD:syms.map(mk), rowsW:syms.map(mk), day:'2026-11-03', lastBar:'2026-11-04', model:RRG_MODEL, loading:false, err:''};
  ffRenderThemes(); return syms.length;
}"""
COUNT = "()=>document.querySelectorAll('#ffThemes .sd-row').length"
GEOM = r"""()=>{
  const q = s=>document.querySelector(s), r = e=>{ const b = e.getBoundingClientRect(); return {t:Math.round(b.top), b:Math.round(b.bottom), l:Math.round(b.left), r:Math.round(b.right), h:Math.round(b.height)}; };
  const head = r(q('#ffThemesHead')), ctl = r(q('.rrgCtl')), st = r(q('.rrgStatus')), panel = r(q('#ffThemesPanel'));
  const kids = [...q('.rrgCtl').children].map(r);
  const rowsOf = [...new Set(kids.map(k=>k.t))];
  return {head, ctl, st, panel, kids, sameRow: Math.abs((ctl.t+ctl.b)/2 - (head.t+head.b)/2) < 14, ctlLines: rowsOf.length,
    hOverflow: document.documentElement.scrollWidth > innerWidth + 1, ctlOverflow: q('.rrgCtl').scrollWidth > q('.rrgCtl').clientWidth + 1, statusText: q('.rrgStatus').innerText,
    vtxt: document.getElementById('ffRrgBar').innerText};
}"""


def main():
    with sync_playwright() as pw:
        b, page, ce, pe = C.launch(pw, 1440, 900, cards=False)
        try:
            js(page, HELPERS)
            js(page, "()=>{ rrgAutoDone = true; switchTab('flow'); rrgReset(); }")
            n = js(page, SEED)

            # ---- data stays through loading (batch 1-3) ----
            r = js(page, r"""async(COUNT)=>{
              const cnt = ()=>document.querySelectorAll('#ffThemes .sd-row').length, snaps = [];
              const fo = window.rrgFetchBatch; __mock({});
              const fo2 = window.rrgFetchBatch;
              window.rrgFetchBatch = async (s,k)=>{ snaps.push({at:'fetch', n:cnt(), dim: !!document.querySelector('#ffThemes .rrgDim'), spin: !!document.querySelector('[data-rrg-refresh].spin'), dis: document.querySelector('[data-rrg-refresh]').disabled}); return fo2(s,k); };
              const sl = window.rrgSleep; window.rrgSleep = async(ms)=>{ snaps.push({at:'sleep', n:cnt()}); window.__t += ms; };
              // switch controls mid-run
              const p = rrgRefresh(true);
              await new Promise(r=>setTimeout(r,0));
              rrgSetTf('W'); const w1 = cnt(); rrgSetFresh(true); const fr1 = cnt() + '|' + !!document.querySelector('[data-rr-fresh-none]'); rrgSetFresh(false); rrgSetTf('D'); const d1 = cnt();
              await p;
              return {snaps, w1, fr1, d1, after: cnt()};
            }""")
            n_all = n
            check("LOAD list keeps all 23 rows (dimmed) at every batch", all(s["n"] == n_all for s in r["snaps"]) and len(r["snaps"]) >= 5 and r["after"] == n_all, r)
            check("LOAD dim + spinning disabled ↻ while loading", r["snaps"][0]["dim"] and r["snaps"][0]["spin"] and r["snaps"][0]["dis"], r["snaps"][0])
            check("LOAD switching Daily/Weekly and All/Fresh during loading keeps data", r["w1"] == n_all and r["d1"] == n_all and not r["fr1"].endswith("true") or r["fr1"].split("|")[0] != "0", r)

            # ---- fallback: live rows vanish mid-run -> last good shown ----
            r = js(page, r"""()=>{
              ffRenderThemes();
              const f = ffState(); f.rrg.rowsD = []; f.rrg.rowsW = []; f.rrg.loading = true; rrgProg = {batch:1,nb:3,waitUntil:0,limit:false}; ffRenderThemes();
              const inLoad = document.querySelectorAll('#ffThemes .sd-row').length;
              f.rrg.loading = false; rrgProg = null; ffRenderThemes();
              return {inLoad, idle: document.querySelectorAll('#ffThemes .sd-row').length};
            }""")
            check("LAST-GOOD rows emptied mid-refresh -> last good list still shown; idle+empty -> empty (honest)", r["inLoad"] == n_all and r["idle"] == 0, r)

            # ---- Fresh with nothing fresh -> message + Show all ----
            js(page, SEED)
            r = js(page, r"""()=>{ ffState().rrg.rowsD.forEach(x=>{ x.dMom = 0.01; x.days = 30; }); rrgSetFresh(true); window.__dbg = {ps1: ps1Off(), fo: rrgFreshOnly(), ln1: ln1On(), html: document.getElementById('ffThemes').innerHTML.slice(0,200)}; const m = !!document.querySelector('[data-rr-fresh-none] [data-rr-showall]'); const sa = document.querySelector('[data-rr-showall]'); if(sa) sa.click(); return {dbg: window.__dbg, m, n: document.querySelectorAll('#ffThemes .sd-row').length}; }""")
            check("FRESH empty -> 'Nothing fresh' with Show all button that restores the list", r["m"] and r["n"] == n_all, r)

            # ---- layout 1440 ----
            js(page, SEED)
            g = js(page, GEOM)
            check("L1440 controls on the same row as title+score, on the right", g["sameRow"] and g["ctl"]["l"] > g["head"]["l"] + 200, g)
            check("L1440 controls never wrap / overflow; no horizontal scroll", g["ctlLines"] == 1 and not g["ctlOverflow"] and not g["hOverflow"], g)
            check("L1440 status is a single line under the title row, full width", g["st"]["t"] >= g["head"]["b"] - 2 and g["st"]["h"] < 26 and abs((g["st"]["r"] - g["st"]["l"]) - (g["panel"]["r"] - g["panel"]["l"])) < 50, g)
            check("L1440 'rrg v7' not on screen (tooltip only), no 'กำลังดึง'", "rrg v" not in g["vtxt"] and js(page, "()=>document.querySelector('[data-rrg-copy]').title.includes('rrg v')"), g["vtxt"])
            check("L1440 ↻ same size as ⧉, tooltip 'Refresh prices'", js(page, "()=>{ const a=document.querySelector('[data-rrg-copy]').getBoundingClientRect(), b=document.querySelector('[data-rrg-refresh]').getBoundingClientRect(); return Math.abs(a.width-b.width)<1 && Math.abs(a.height-b.height)<1 && document.querySelector('[data-rrg-refresh]').title.startsWith('Refresh prices'); }"))
            # loading state layout (long status line)
            js(page, "()=>{ const f=ffState(); f.rrg.loading=true; rrgProg={batch:2,nb:3,waitUntil:Date.now()+44000,limit:false}; ffRenderThemes(); }")
            g = js(page, GEOM)
            check("L1440 loading status 'Updating prices · batch 2/3 · next in 44 s' one line, controls one row", "Updating prices · batch 2/3 · next in 44 s" in g["statusText"] and g["ctlLines"] == 1 and g["sameRow"], g)
            page.screenshot(path=os.path.join(SHOTS, "mac-light-loading.png"), clip={"x": 0, "y": g["panel"]["t"] - 10, "width": 1440, "height": 420})
            js(page, "()=>{ const f=ffState(); f.rrg.loading=false; rrgSetProg(null); ffRenderThemes(); }")
            page.screenshot(path=os.path.join(SHOTS, "mac-light.png"), clip={"x": 0, "y": g["panel"]["t"] - 10, "width": 1440, "height": 420})
            page.emulate_media(color_scheme="dark")
            js(page, "()=>{ document.documentElement.setAttribute('data-theme','dark'); ffRenderThemes(); }")
            page.screenshot(path=os.path.join(SHOTS, "mac-dark.png"), clip={"x": 0, "y": g["panel"]["t"] - 10, "width": 1440, "height": 420})

            # ---- layout 390 ----
            for theme in ("light", "dark"):
                page.emulate_media(color_scheme=theme)
                js(page, "(t)=>{ document.documentElement.setAttribute('data-theme', t); }", theme)
                page.set_viewport_size({"width": 390, "height": 844})
                page.wait_for_timeout(250)
                for loading in (False, True):
                    js(page, "(l)=>{ const f=ffState(); f.rrg.loading=l; if(l) rrgProg={batch:2,nb:3,waitUntil:Date.now()+44000,limit:false}; else rrgSetProg(null); ffRenderThemes(); window.scrollTo(0,0); document.getElementById('ffThemesPanel').scrollIntoView(); }", loading)
                    g = js(page, GEOM)
                    tag = f"L390 {theme}{' loading' if loading else ''}"
                    check(tag + ": title row, controls row, status row in that order; no element alone on a row", g["head"]["b"] <= g["ctl"]["t"] + 1 and g["ctl"]["b"] <= g["st"]["t"] + 1 and g["ctlLines"] == 1 and len(g["kids"]) == 4, g)
                    check(tag + ": controls fit one line, no overflow, no horizontal scroll", not g["ctlOverflow"] and not g["hOverflow"] and g["ctl"]["r"] <= 390 and g["ctl"]["l"] >= 0, g)
                    page.screenshot(path=os.path.join(SHOTS, f"m390-{theme}{'-loading' if loading else ''}.png"), clip={"x": 0, "y": max(0, g["panel"]["t"] - 10), "width": 390, "height": 460})
            check("no console errors", not [e for e in ce if "favicon" not in e.lower()] and not pe, {"ce": ce[:3], "pe": pe[:3]})
        finally:
            b.close()
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results)-len(bad)}/{len(results)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
