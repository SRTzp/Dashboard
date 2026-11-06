#!/usr/bin/env python3
"""RRG1b — screenshots 390 / 1440: lean cards (fixture, new model) + one waiting symbol + legend closed/open + Today Sectors. ภาพ → tests/screenshots/rrg1b-*.png"""
import ln3fix_common as C
from playwright.sync_api import sync_playwright
js = C.js

SEED = r"""()=>{
  const N = 400, mk = (f, bf)=>{ const c=[], b=[]; for(let i=0;i<N;i++){ const bb = bf ? bf(i) : 100; b.push(bb); c.push(bb*f(i)); } return {c, b}; };
  const run = (s, tf)=> rrgCompute(s.c, s.c, s.b, tf||'D', {lastObs:'2026-11-04'});
  const dn = (()=>{ const b=[], c=[]; for(let i=0;i<N;i++){ const t=Math.max(0,i-(N-60))/60; b.push(100*(1-0.08*t)); c.push(100*(1-0.03*t)); } return {c, b}; })();
  const defs = [
    ['PAVE','Infrastructure', dn],
    ['SMH','Semiconductors', mk(i=>Math.exp(0.0004*i + 0.0000030*i*i))],
    ['XLE','Energy', mk(i=> i<N-8 ? Math.exp(-0.003*i) : Math.exp(-0.003*(N-8) + 0.004*(i-(N-8))))],
    ['IGV','Software', mk(i=> i<N-20 ? Math.exp(0.003*i) : Math.exp(0.003*(N-20)))],
    ['XLU','Utilities', mk(i=>Math.exp(-0.0004*i - 0.0000025*i*i))],
    ['XLRE','Real Estate', mk(i=>1+0.0030*Math.sin(i/5)+0.0012*Math.sin(i/2.3))]
  ];
  const rows = defs.map(d=>Object.assign({sym:d[0], name:d[1], date:'2026-11-04', lastObsBench:'2026-11-04'}, run(d[2])));
  rows.push({sym:'XLK', name:'Technology', quad:'lead', ratio:103, mom:102, dMom:0.3, dRatio:0.1, days:4, off52:-3, date:'2026-11-03', rsTrend:0.01});   // old model => waiting
  window.rrgToday = ()=>'2026-11-04'; window.thaiToday = ()=>'2026-11-04';
  const f = ffState(); f.rrgTf = 'D';
  f.rrg = {rowsD: rows, rowsW: rows, build:RRG_BUILD, model:RRG_MODEL, lastBar:'2026-11-04', day:'2026-11-04', at:'', loading:false, err:''};
  sdWrite('SMH', n=>{ n.follow = true; return n; }); sdWrite('XLK', n=>{ n.follow = true; return n; });
  try{ localStorage.removeItem('rrgLegendOpen'); }catch(e){} rrgLegSynced = false;
  switchTab('flow'); f.themesCol = false; f.themesColUser = true; ffRenderThemes();
  return rows.map(r=>[r.sym, r.quad, r.pt, r.model]);
}"""

with sync_playwright() as pw:
    for w, h, tag in ((1440, 1000, "1440"), (390, 844, "390")):
        b, page, ce, pe = C.launch(pw, w, h, cards=False)
        try:
            print(tag, js(page, SEED))
            page.wait_for_timeout(500)
            C.shot(page, f"rrg1b-flow-{tag}.png", sel='#ffThemesPanel')
            js(page, "()=>{ document.getElementById('rrLegend').open = true; rrgDetOpen['SMH'] = true; ffRenderThemes(); }")
            page.wait_for_timeout(200)
            C.shot(page, f"rrg1b-legend-details-{tag}.png", sel='#ffThemesPanel')
            js(page, "()=>{ switchTab('today'); }")
            page.wait_for_timeout(500)
            try: C.shot(page, f"rrg1b-today-sectors-{tag}.png", sel='[data-sd-today]')
            except Exception as e: print("today shot:", e)
            print(tag, "console errors:", ce[:2], pe[:2])
        finally:
            b.close()
