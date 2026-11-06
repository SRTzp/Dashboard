#!/usr/bin/env python3
"""RRG1 — Relative Trend vs SPY: synthetic deterministic tests F1–F8 (+G migration, +H9–H11 when present).
Chromium · functions evaluated in-page on synthetic series · prints hysteresis flip counts for the PR.
รัน: python3 tests/rrg1_check.py"""
import json, sys
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

js = C.js
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:700]) if (d and not ok) else ""))


# ---- synthetic series (built in page; bench constant 100 unless stated) ----
SCEN = r"""()=>{
  const N = 400, out = {};
  const mk = (f, benchF)=>{ const c=[], b=[]; for(let i=0;i<N;i++){ b.push(benchF?benchF(i):100); c.push((benchF?benchF(i):100)*f(i)); } return {c, b}; };
  const run = (s, tf, mode)=> rrgCompute(s.c, s.c, s.b, tf||'D', {mode});
  // F1 persistent underperformance (accelerating decline -> raw < 0 and change < 0)
  out.f1 = mk(i=>Math.exp(-0.0004*i - 0.0000025*i*i));
  // F2 recovering underperformance: long decline then 8 bars of recovery (still below SPY)
  out.f2 = mk(i=> i<N-8 ? Math.exp(-0.003*i) : Math.exp(-0.003*(N-8) + 0.004*(i-(N-8))));
  // F3 asset -3% while bench -8% over the last 60 bars (outperforming, price down)
  out.f3 = (()=>{ const b=[], c=[]; for(let i=0;i<N;i++){ const t=Math.max(0,i-(N-60))/60; b.push(100*(1-0.08*t)); c.push(100*(1-0.03*t)); } return {c, b}; })();
  // F4 weakening leadership: rise then flat
  out.f4 = mk(i=> i<N-20 ? Math.exp(0.003*i) : Math.exp(0.003*(N-20)));
  // F5 near-zero oscillation (two incommensurate sines)
  out.f5 = mk(i=>1+0.0030*Math.sin(i/5)+0.0012*Math.sin(i/2.3));
  const sum = (r)=>({quad:r.quad, rel:r.rel, momUp:r.momUp, raw:r.rsTrend, chg:r.rawChg, eps:r.eps, delta:r.delta, ratio:r.ratio, mom:r.mom, err:r.err});
  out.res = {}; ['f1','f2','f3','f4','f5'].forEach(k=>{ out.res[k] = sum(run(out[k])); });
  out.flips = {}; out.flat = {}; ['none','opp','zero'].forEach(m=>{ const r5 = run(out.f5,'D',m); out.flips[m] = r5.flips; out.flat[m] = r5.flatBars; });
  out.flipsAll = {}; ['f1','f2','f3','f4','f5'].forEach(k=>{ out.flipsAll[k] = {}; ['none','opp','zero'].forEach(m=>{ out.flipsAll[k][m] = run(out[k],'D',m).flips; }); });
  // old-model classification of F2's last bar (z only), to prove the counter-example
  out.f2old = (out.res.f2.ratio >= 100) ? ((out.res.f2.mom >= 100) ? 'lead' : 'weak') : ((out.res.f2.mom >= 100) ? 'imp' : 'lag');
  out.f3price = out.f3.c[N-1]/out.f3.c[N-60]-1; out.f3bench = out.f3.b[N-1]/out.f3.b[N-60]-1;
  return out;
}"""


def main():
    with sync_playwright() as pw:
        b, page, ce, pe = C.launch(pw, 1280, 900, cards=False)
        try:
            o = js(page, SCEN)
            r = o["res"]
            check("F1 persistent underperformance -> Underperforming · worsening (lag)", r["f1"]["quad"] == "lag" and r["f1"]["raw"] < -r["f1"]["eps"], r["f1"])
            check("F2 recovering underperformance -> imp (recovering), NOT lead", r["f2"]["quad"] == "imp" and r["f2"]["raw"] < 0 and r["f2"]["chg"] > r["f2"]["delta"], r["f2"])
            check("F2 counter-example reproduced: old z-only rule would say 'lead' on the same data", o["f2old"] == "lead", o["f2old"])
            check("F3 outperforming in a market decline: rel=pos while asset price falls", r["f3"]["rel"] == "pos" and o["f3price"] < 0 and o["f3bench"] < o["f3price"], {"r": r["f3"], "px": o["f3price"], "bm": o["f3bench"]})
            check("F4 weakening leadership (raw>0, falling) -> Outperforming · fading (weak)", r["f4"]["quad"] == "weak" and r["f4"]["raw"] > r["f4"]["eps"] and r["f4"]["chg"] < 0, r["f4"])
            fl = o["flips"]
            print(f"INFO F5 flips over last 252 bars  none={fl['none']}  opp={fl['opp']}  zero={fl['zero']}  | Neutral bars none={o['flat']['none']} opp={o['flat']['opp']} zero={o['flat']['zero']}  (RRG_HYST chosen in app: {js(page, '()=>RRG_HYST')})")
            print("INFO flips per scenario (none/opp/zero):", json.dumps(o["flipsAll"]))
            check("F5 near-zero oscillation: hysteresis reduces flips vs none", fl["zero"] < fl["none"] and fl["opp"] <= fl["none"], fl)
            ch = js(page, "()=>RRG_HYST")
            check("F5 chosen hysteresis flips fewer than none AND keeps Neutral reachable (opp makes Neutral nearly unreachable)", fl[ch] < fl["none"] and o["flat"][ch] > 0, {"fl": fl, "flat": o["flat"], "chosen": ch})

            # F6 stale + mismatched dates through the real refresh pipeline (mock fetch)
            res6 = js(page, r"""async()=>{
              const today = '2026-11-04';   // Wed
              window.rrgToday = ()=>today; window.thaiToday = ()=>today;
              const days = (end, n)=>{ const a=[]; let d=new Date(end+'T00:00:00Z'); while(a.length<n){ const w=d.getUTCDay(); if(w!==0&&w!==6) a.push(d.toISOString().slice(0,10)); d=new Date(d.getTime()-86400000); } return a; };
              const vals = (ds, f)=> ds.map((dt,i)=>{ const c = f(ds.length-1-i); return {datetime:dt, close:String(c), high:String(c*1.01)}; });   // newest first
              const mkData = (end, f)=> vals(days(end, 420), f);
              window.__fx = {};
              window.rrgFetchBatch = async (syms)=>{ const o={}; syms.forEach(s=>{ o[s] = (window.__fx[s] || (()=>[]))(); }); return o; };
              RRG_CFG.cooldownMs = 0;
              const key = ffState; tdSettings().tdKey = 'x';
              const SPY = ()=> mkData('2026-11-04', i=>100+0.02*i);
              RRG_SYMS.forEach(d=>{ window.__fx[d.s] = ()=> mkData('2026-11-04', i=>100*(1+0.0005*i+0.01*Math.sin(i/9))); });
              window.__fx.SPY = SPY;
              window.__fx.XLU = ()=> mkData('2026-11-03', i=>100*(1+0.0005*i+0.01*Math.sin(i/9)));   // ends a day earlier than SPY
              await rrgRefresh(true);
              const f = ffState();
              const xlu = f.rrg.rowsD.find(x=>x.sym==='XLU'), pave = f.rrg.rowsD.find(x=>x.sym==='PAVE'), paveW = f.rrg.rowsW.find(x=>x.sym==='PAVE');
              const stale7 = rrgBarsFresh({lastBar:'2026-10-28'}, today), fresh2 = rrgBarsFresh({lastBar:'2026-11-02'}, today);
              return {err: f.rrg.err, model: f.rrg.model, lastBar: f.rrg.lastBar, xlu, pave: {quad:pave.quad, err:pave.err, lastObs:pave.lastObs}, paveW: {date:paveW.date, lastObs:paveW.lastObs, prev:paveW.preview, err:paveW.err, quad:paveW.quad}, stale7, fresh2,
                      cacheFresh: rrgCacheFresh(f), cacheFresh7: (()=>{ const g={rrg:Object.assign({}, f.rrg, {lastBar:'2026-10-28'})}; return rrgCacheFresh(g); })(), n: f.rrg.rowsD.length, nsym: RRG_SYMS.length + 1 };
            }""")
            check("F6 stale: last bar 7 days old -> not fresh; 2 days old -> fresh", res6["stale7"] is False and res6["fresh2"] is True, res6)
            check("F6 cacheFresh requires fresh bars (7d-old lastBar -> refetch)", res6["cacheFresh"] is True and res6["cacheFresh7"] is False, res6)
            check("F6 mismatched asset/benchmark end dates -> not classified (err, no quad)", bool(res6["xlu"].get("err")) and "Mismatched" in res6["xlu"]["err"] and not res6["xlu"].get("quad"), res6["xlu"])
            check("F6 matching symbols classified; model stamp 2 and lastBar stored", res6["pave"]["quad"] in ("lead", "weak", "imp", "lag", "flat") and res6["model"] == 2 and res6["lastBar"] == "2026-11-04", res6)
            # F7 partial week: today Wed 2026-11-04 -> classify on week ending Fri 2026-10-30, preview to Wed
            check("F7 partial week: W row dated by last COMPLETED week's last session; preview carries this week", res6["paveW"]["date"] == "2026-10-30" and res6["paveW"]["prev"] and res6["paveW"]["prev"]["asOf"] == "2026-11-04", res6["paveW"])
            wk = js(page, r"""()=>{ const a = rrgToWeekly(['2026-10-29','2026-10-30','2026-11-02','2026-11-03'], [1,2,3,4], [1,2,3,4], '2026-11-04');
                                  const b = rrgToWeekly(['2026-10-29','2026-10-30'], [1,2], [1,2], '2026-11-04');
                                  const c = rrgToWeekly(['2026-11-02','2026-11-03'], [1,2], [1,2], '2026-11-07');   // Sat: holiday-shortened week counts as complete
                                  return [a.partial, a.lastObs, b.partial, c.partial]; }""")
            check("F7 rrgToWeekly: partial flag + lastObs per bar (Friday-complete, Sat after holiday week complete)", wk[0] is True and wk[1][-1] == "2026-11-03" and wk[2] is False and wk[3] is False, wk)

            # F8 breadth == state: rel==='pos' <=> lead/weak ; raw>eps => pos ; raw<-eps => not pos ; DOM breadth equals count
            f8 = js(page, r"""()=>{
              const rows = ffState().rrg.rowsD.filter(x=>!x.err);
              const bad = rows.filter(x=> ((x.quad==='lead'||x.quad==='weak') !== (x.rel==='pos')) || (x.rsTrend > x.eps && x.rel!=='pos') || (x.rsTrend < -x.eps && x.rel==='pos'));
              ffState().rrgTf = 'D'; ffRenderThemes();
              const up = rows.filter(x=>x.quad==='lead'||x.quad==='weak').length;
              return {bad: bad.length, up, total: rows.length, dom: document.getElementById('ffBreadth').textContent}; }""")
            check("F8 breadth and state agree on every row (and DOM breadth = count of outperforming)", f8["bad"] == 0 and f8["dom"].startswith(f"{f8['up']}/{f8['total']}"), f8)

            # G migration: old-model cache -> outdated & retained; failed refetch keeps outdated; success re-baselines notes without Revisit
            g = js(page, r"""async()=>{
              const f = ffState();
              const oldRows = [{sym:'SMH', name:'Semiconductors', quad:'lead', prevQuad:'imp', dMom:0.3, dRatio:0.1, ratio:102, mom:101, days:4, off52:-3, date:'2026-11-03', rsTrend:0.01}];
              f.rrg = {rowsD: oldRows, rowsW: oldRows.map(x=>Object.assign({}, x)), build: 6, day: '2026-11-04', at:'', err:'', loading:false};
              f.rrg.build = RRG_BUILD; f.rrg.day = '';   // what ffState() migration does for build != RRG_BUILD
              const o1 = {outdated: rrgOutdated(f.rrg), fresh: rrgCacheFresh(f), keeps: f.rrg.rowsD.length};
              // seed a note reviewed under the old model
              sdWrite('SMH', n=>{ n.reviewed_at = new Date().toISOString(); n.reviewed_phase = 'IMPROVING'; n.reviewed_tf = 'D'; return n; });
              // failed refetch
              window.rrgFetchBatch = async ()=>{ throw new Error('boom'); };
              await rrgRefresh(true);
              const o2 = {err: f.rrg.err, model: f.rrg.model, outdated: rrgOutdated(f.rrg), rows: f.rrg.rowsD.length, noteModel: sdNote('SMH').reviewed_model, flag: sdFlag('SMH', sdNote('SMH'))};
              // successful refetch
              const days = (end, n)=>{ const a=[]; let d=new Date(end+'T00:00:00Z'); while(a.length<n){ const w=d.getUTCDay(); if(w!==0&&w!==6) a.push(d.toISOString().slice(0,10)); d=new Date(d.getTime()-86400000); } return a; };
              window.rrgFetchBatch = async (syms)=>{ const o={}; syms.forEach(s=>{ o[s] = days('2026-11-04',420).map((dt,i)=>{ const k=419-i; const c = s==='SPY' ? 100+0.02*k : 100*(1+0.0005*k+0.01*Math.sin(k/9)); return {datetime:dt, close:String(c), high:String(c*1.01)}; }); }); return o; };
              await rrgRefresh(true);
              await new Promise(r=>setTimeout(r,300));
              const n = sdNote('SMH');
              const cur = sdCur('SMH','D');
              const o3 = {model: f.rrg.model, outdated: rrgOutdated(f.rrg), noteModel: n.reviewed_model, updated: n.model_updated, phase: n.reviewed_phase, curPhase: cur.ok ? cur.phase : null, flag: sdFlag('SMH', n)};
              return {o1, o2, o3}; }""")
            check("G old-model cache is flagged outdated, not fresh, rows retained", g["o1"]["outdated"] and not g["o1"]["fresh"] and g["o1"]["keeps"] == 1, g["o1"])
            check("G failed refetch: old results retained, still outdated, NOT stamped migrated", g["o2"]["err"] and g["o2"]["outdated"] and g["o2"]["model"] is None and g["o2"]["rows"] == 1 and g["o2"]["noteModel"] is None, g["o2"])
            check("G no 'Revisit · phase changed' from the model change (flag off on old-model note)", g["o2"]["flag"] is False and g["o3"]["flag"] is False, g)
            check("G successful refetch: model=2, note re-baselined once (phase = current, model stamp, model_updated date)", g["o3"]["model"] == 2 and not g["o3"]["outdated"] and g["o3"]["noteModel"] == 2 and g["o3"]["updated"] == "2026-11-04" and g["o3"]["phase"] == g["o3"]["curPhase"], g["o3"])
            check("no console errors", not [e for e in ce if "favicon" not in e.lower()] and not pe, {"ce": ce[:3], "pe": pe[:3]})
        finally:
            b.close()
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results)-len(bad)}/{len(results)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
