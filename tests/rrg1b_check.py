#!/usr/bin/env python3
"""RRG1b — fetch queue / rate limit, old-model 'waiting' state, collapsible legend, lean 2-line card.
Fake timers are in-page: Date.now is virtual and rrgSleep advances it (no real waiting). รัน: python3 tests/rrg1b_check.py"""
import json, sys
import ln3fix_common as C
from playwright.sync_api import sync_playwright

js = C.js
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:700]) if (d and not ok) else ""))


HELPERS = r"""()=>{
  window.__t = 1000000; window.__sleeps = []; window.__calls = [];
  Date.now = ()=>window.__t;
  window.rrgSleep = async (ms)=>{ window.__sleeps.push(ms); window.__t += ms; };
  window.rrgToday = ()=>'2026-11-04'; window.thaiToday = ()=>'2026-11-04';
  try{ localStorage.removeItem('rrgLastBatchAt'); }catch(e){}
  window.rrgMemBatchAt = 0;
  window.__days = (end, n)=>{ const a=[]; let d=new Date(end+'T00:00:00Z'); while(a.length<n){ const w=d.getUTCDay(); if(w!==0&&w!==6) a.push(d.toISOString().slice(0,10)); d=new Date(d.getTime()-86400000); } return a; };
  window.__series = (s)=> window.__days('2026-11-04',420).map((dt,i)=>{ const k=419-i; const c = s==='SPY' ? 100+0.02*k : 100*(1+0.0005*k+0.01*Math.sin(k/9)); return {datetime:dt, close:String(c), high:String(c*1.01)}; });
  window.__mock = (failPlan)=>{   // failPlan: {batchNo: remainingFailures}
    let n = 0;
    window.rrgFetchBatch = async (syms)=>{
      n++; window.__calls.push({n, t: window.__t, syms: syms.slice()});
      const k = window.__calls.filter(c=>c.syms[0]===syms[0]).length;   // attempt number for this batch
      const idx = [...new Set(window.__calls.map(c=>c.syms[0]))].indexOf(syms[0]) + 1;
      if(failPlan[idx] && k <= failPlan[idx]){ const e = new Error('You have run out of API credits for the current minute. 16 API credits were used, the current limit being 8'); e.rate = true; throw e; }
      const o = {}; syms.forEach(s=>{ o[s] = window.__series(s); }); return o;
    };
  };
  tdSettings().tdKey = 'x';
  return true;
}"""

OLD_ROWS = r"""()=>{
  const f = ffState();
  const old = (s,q)=>({sym:s, name:s+' name', quad:q, dMom:0.3, dRatio:0.1, ratio:102, mom:101, days:4, off52:-3, date:'2026-11-03', rsTrend:0.01});
  f.rrg = {rowsD:[old('SMH','lead'), old('XLE','imp')], rowsW:[old('SMH','lead'), old('XLE','imp')], build:RRG_BUILD, day:'', at:'', err:'', loading:false};   // no model => old
  return true;
}"""


def main():
    with sync_playwright() as pw:
        b, page, ce, pe = C.launch(pw, 1280, 900, cards=False)
        try:
            js(page, HELPERS)

            # ---------- 1. rate limit ----------
            js(page, OLD_ROWS)
            js(page, "()=>{ __mock({2:1}); }")   # batch 2 fails once with the credit error
            r = js(page, r"""async()=>{
              const f = ffState();
              const p1 = rrgRefresh(true);
              const p2 = rrgRefresh(true), p3 = rrgManualRefresh();   // clicks while running -> join the queue
              const same = (p1 === p2) && (p1 === p3);
              let midSaved = null;
              const watch = setInterval(()=>{ if(__calls.length === 2 && midSaved === null) midSaved = {rows: f.rrg.rowsD.length, model: f.rrg.model, pending: (f.rrg.pending||[]).length}; }, 0);
              await p1; clearInterval(watch);
              const gaps = __calls.slice(1).map((c,i)=>c.t - __calls[i].t);
              return {same, calls: __calls.map(c=>c.syms.length + ':' + c.syms[0]), gaps, sleeps: __sleeps.slice(), model: f.rrg.model, pending: f.rrg.pending, err: f.rrg.err, rows: f.rrg.rowsD.length, newModel: f.rrg.rowsD.filter(x=>x.model===RRG_MODEL).length, nsym: RRG_SYMS.length};
            }""")
            check("RL refresh clicks while the queue runs join it (same promise, no second fetch)", r["same"], r)
            check("RL batch 2 credit error -> retried automatically (4 requests for 3 batches), 3rd batch follows", len(r["calls"]) == 4 and r["calls"][1] == r["calls"][2], r["calls"])
            check("RL every request >= 61 s after the previous one (incl. the retry)", all(g >= 61000 for g in r["gaps"]) and len(r["gaps"]) == 3, r["gaps"])
            check("RL all rows new-model after the retry; migrated flag only now; pending cleared", r["model"] == 2 and r["pending"] is None and r["newModel"] == r["nsym"] and not r["err"], r)

            # batch 1 kept when batch 2 exhausts all tries; resume uses only the remaining symbols
            js(page, OLD_ROWS); js(page, HELPERS); js(page, OLD_ROWS)
            js(page, "()=>{ __mock({2:3}); }")
            r2 = js(page, r"""async()=>{
              const f = ffState();
              await rrgRefresh(true);
              const o = {calls: __calls.length, model: f.rrg.model, err: f.rrg.err, raw: f.rrg.errRaw, newModel: f.rrg.rowsD.filter(x=>x.model===RRG_MODEL).length, old: f.rrg.rowsD.filter(x=>x.model!==RRG_MODEL).length, pending: (f.rrg.pending||[]).length, outdated: rrgOutdated(f.rrg)};
              __calls.length = 0; __mock({});
              await rrgRefresh(true);
              o.resumeCalls = __calls.map(c=>c.syms.length + ':' + c.syms[0]); o.model2 = f.rrg.model; o.pending2 = f.rrg.pending;
              o.gap = __calls.length ? __calls[0].t - __lastT : null;
              return o;
            }""".replace("o.gap = __calls.length ? __calls[0].t - __lastT : null;", ""))
            check("RL 3 failures on batch 2: max 3 tries, batch 1 results kept (8 symbols new-model), NOT migrated", r2["calls"] == 1 + 3 and r2["newModel"] == 7 and r2["model"] is None and r2["outdated"], r2)
            check("RL short status line (no raw API text); raw error kept in errRaw", "credits" not in (r2["err"] or "") and "Price limit" in r2["err"] and "credits" in r2["raw"], r2)
            check("RL next refresh resumes ONLY the remaining symbols, then migrates", r2["resumeCalls"] == ["8:" + r2["resumeCalls"][0].split(":")[1], "8:" + r2["resumeCalls"][1].split(":")[1]] and r2["model2"] == 2 and r2["pending2"] is None, r2)
            gap = js(page, "()=>{ const f = ffState(); return {model: f.rrg.model}; }")
            # cross-run cooldown: a new run starting right after a finished one must still wait 61 s
            js(page, "()=>{ __calls.length = 0; __sleeps.length = 0; __mock({}); }")
            g = js(page, r"""async()=>{ const t0 = __t; await rrgRefresh(true); return {first: __calls[0].t - t0, sleeps: __sleeps.slice(0,1)}; }""")
            check("RL a fresh run right after a finished one waits out the 61 s window first (no 8+8 inside a minute)", g["first"] >= 60000 or (g["sleeps"] and g["sleeps"][0] >= 59000), g)
            bar = js(page, r"""()=>{ const f = ffState(); f.rrg.loading = true; rrgProg = {batch:2, nb:3, waitUntil: Date.now()+45000, limit:false}; ffRenderThemes();
               const a = document.getElementById('ffRrgBar').innerText;
               rrgProg = {batch:2, nb:3, waitUntil: Date.now()+60000, limit:true}; ffRenderThemes();
               const b2 = document.getElementById('ffRrgBar').innerText; f.rrg.loading = false; rrgProg = null; ffRenderThemes(); return [a,b2]; }""")
            check("RL status lines: 'Updating prices · batch 2/3 · next in 45 s' / 'Price limit reached — retrying in 60 s'", "Updating prices · batch 2/3 · next in 45 s" in bar[0] and "Price limit reached — retrying in 60 s" in bar[1], bar)

            # ---------- 2. old-model results ----------
            js(page, HELPERS)
            w = js(page, r"""()=>{
              const f = ffState(); f.rrgTf = 'D';
              const mk = (s,q)=>Object.assign({sym:s, name:s+' name', date:'2026-11-04', lastObsBench:'2026-11-04', model:RRG_MODEL, eps:0.02, delta:0.01, rsTrend:q==='lead'?0.4:-0.4, rawChg:0.1, rel:q==='lead'?'pos':'neg', momUp:true, lag:5, bars:300, close:101.2, benchClose:100, pt:'up', ptEma:100, ptEmaPrev:99, ptN:50, ptLag:5, lastObs:'2026-11-04'}, {quad:q, ratio:101, mom:101, dMom:0.1, dRatio:0.1, days:5, off52:-5.9});
              const old = {sym:'SMH', name:'Semiconductors', quad:'lead', ratio:103, mom:102, dMom:0.3, dRatio:0.1, days:4, off52:-3, date:'2026-11-03', rsTrend:0.01};
              const rows = [mk('PAVE','lead'), mk('XLU','imp'), old];
              f.rrg = {rowsD: rows, rowsW: rows, build:RRG_BUILD, model:RRG_MODEL, lastBar:'2026-11-04', day:'2026-11-04', at:'', loading:false, err:''};
              switchTab('flow'); f.themesCol = false; f.themesColUser = true; ffRenderThemes();
              const box = id=>[...document.querySelectorAll('#'+id+' .ffChip')].map(e=>e.innerText.trim());
              const card = document.querySelector('#ffThemes [data-rr="SMH"]');
              return {boxes: {lead: box('ffQlead'), imp: box('ffQimp'), lag: box('ffQlag'), weak: box('ffQweak'), flat: box('ffQflat')}, wait: box('ffQwait'), waitVisible: document.getElementById('ffQwaitBox').style.display !== 'none',
                      card: card.innerText.replace(/\s+/g,' '), gauges: card.querySelectorAll('.rrgGauge').length, chips: card.querySelectorAll('.rr-ch').length, details: !!card.querySelector('details'),
                      breadth: document.getElementById('ffBreadth').innerText, copy: rrgCopyText(), badge: sectorState('SMH').quad, cur: sdCurShow('SMH','D').why};
            }""")
            allbox = sum(w["boxes"].values(), [])
            check("OLD old-model symbol is in the grey waiting strip (ticker only), in none of the new boxes", w["wait"] == ["SMH"] and w["waitVisible"] and "SMH" not in allbox and "PAVE" in w["boxes"]["lead"] and "XLU" in w["boxes"]["imp"], w)
            check("OLD card says 'Old model — refreshing…' with no state label, no chips, no gauges", "Old model — refreshing…" in w["card"] and "Outperforming" not in w["card"] and "Underperforming" not in w["card"] and "Beating" not in w["card"] and w["gauges"] == 0 and w["chips"] == 0 and not w["details"], w["card"])
            check("OLD breadth counts only new-model results and shows (n waiting)", w["breadth"].startswith("1/2") and "(1 waiting)" in w["breadth"], w["breadth"])
            check("OLD not used elsewhere: copy-by-phase lists it as waiting, watchlist badge has no state, Today has no phase", "Waiting for refresh (old model): SMH" in w["copy"] and "Outperforming · strengthening: PAVE" in w["copy"] and "SMH" not in w["copy"].split("Waiting")[0] and w["badge"] is None and w["cur"] == "waiting", w)

            # ---------- 3. legend ----------
            lg = js(page, r"""()=>{ try{ localStorage.removeItem('rrgLegendOpen'); }catch(e){} rrgLegSynced = false; ffRenderThemes();
               const el = document.getElementById('rrLegend'); const o = {closedByDefault: !el.open, summary: el.querySelector('summary').innerText.trim(), lines: el.querySelector('.hint').innerHTML.split('<br>').length, txt: el.querySelector('.hint').textContent};
               el.open = true; el.dispatchEvent(new Event('toggle')); o.stored = localStorage.getItem('rrgLegendOpen');
               rrgLegSynced = false; el.open = false; ffRenderThemes(); o.restored = document.getElementById('rrLegend').open;
               document.getElementById('rrLegend').open = false; document.getElementById('rrLegend').dispatchEvent(new Event('toggle')); o.stored2 = localStorage.getItem('rrgLegendOpen');
               rrgLegSynced = false; ffRenderThemes(); o.restored2 = document.getElementById('rrLegend').open; return o; }""")
            check("LEG closed by default, label 'How to read ›', 4 short lines of plain English", lg["closedByDefault"] and lg["summary"] == "How to read ›" and lg["lines"] == 4 and "Custom model, not JdK RRG" in lg["txt"], lg)
            check("LEG open/closed is remembered per device (localStorage)", lg["stored"] == "1" and lg["restored"] is True and lg["stored2"] == "0" and lg["restored2"] is False, lg)

            # ---------- 4. lean card ----------
            for tag, wdt in (("390", 390), ("1440", 1440)):
                page.set_viewport_size({"width": wdt, "height": 900})
                c = js(page, r"""()=>{
                  const f = ffState(); const rows = f.rrg.rowsD;
                  const set = (s, o)=>Object.assign(rows.find(x=>x.sym===s), o);
                  set('PAVE', {quad:'lead', pt:'up', close:103.2, ptEma:100, ptEmaPrev:99, off52:-5.9});
                  set('XLU', {quad:'imp', pt:'down', close:95.9, ptEma:100, ptEmaPrev:101, off52:-12.4});
                  rows.push(Object.assign({}, rows[0], {sym:'XLE', name:'Energy', quad:'lag', pt:'mixed', close:100.8, ptEma:100, ptEmaPrev:99, off52:0}));
                  rows.push(Object.assign({}, rows[0], {sym:'XLF', name:'Financials', quad:'weak', pt:null, off52:-1.2}));
                  rows.push(Object.assign({}, rows[0], {sym:'XLK', name:'Technology', quad:'flat', pt:'up', close:100.04, ptEma:100, ptEmaPrev:99.9, off52:-30.2}));
                  ffRenderThemes();
                  const out = {};
                  ['PAVE','XLU','XLE','XLF','XLK'].forEach(s=>{
                    const card = document.querySelector('#ffThemes [data-rr="'+s+'"]'), hd = card.querySelector('.sd-hd'), lean = card.querySelector('.rr-lean');
                    const chips = [...lean.querySelectorAll('.rr-ch')], gap = lean.querySelector('.rr-gap');
                    const r = lean.getBoundingClientRect();
                    out[s] = {chips: chips.map(e=>e.innerText.trim()), tips: chips.map(e=>e.title), gap: gap.innerText.trim(), gapVisible: gap.getBoundingClientRect().bottom <= r.bottom + 0.5 && gap.getBoundingClientRect().right <= r.right + 0.5,
                              chipsInside: chips.every(e=>{ const q=e.getBoundingClientRect(); return q.right <= r.right + 0.5 && q.bottom <= r.bottom + 0.5 && q.top >= r.top - 0.5; }),
                              noHScroll: lean.scrollWidth <= lean.clientWidth + 1, oneRow: new Set(chips.map(e=>Math.round(e.getBoundingClientRect().top))).size === 1,
                              l1: hd.querySelector('.l1').innerText.replace(/\s+/g,' ').trim(), gauges: card.querySelectorAll('summary + .rr-dg .rrgGauge').length, gaugesOutsideDetails: [...card.querySelectorAll('.rrgGauge')].filter(g=>!g.closest('details')).length,
                              text: hd.innerText.replace(/\s+/g,' '), mono: getComputedStyle(lean).fontFamily, docW: document.documentElement.scrollWidth <= window.innerWidth + 1};
                  });
                  const dt = document.querySelector('#ffThemes [data-rr="PAVE"] details'); dt.open = true; out.det = dt.innerText.replace(/\s+/g,' ');
                  return out; }""")
                p = c["PAVE"]
                check(f"CARD[{tag}] chip texts: Beating SPY ↗ + ▲ Up +3.2%, gap '−5.9% from 52W high'", p["chips"] == ["Beating SPY ↗", "▲ Up +3.2%"] and p["gap"] == "−5.9% from 52W high", p)
                check(f"CARD[{tag}] other states: Lagging SPY ↗ / ▼ Down −4.1% · Lagging SPY ↘ / ◆ Mixed +0.8% · Beating SPY ↘ / Price n/a · ≈ SPY", c["XLU"]["chips"] == ["Lagging SPY ↗", "▼ Down −4.1%"] and c["XLE"]["chips"] == ["Lagging SPY ↘", "◆ Mixed +0.8%"] and c["XLF"]["chips"] == ["Beating SPY ↘", "Price n/a"] and c["XLK"]["chips"][0] == "≈ SPY" and c["XLE"]["gap"] == "at 52W high", {k: c[k]["chips"] for k in ("XLU", "XLE", "XLF", "XLK")})
                check(f"CARD[{tag}] tooltips: full state + 'not absolute price'; price: 'Own price vs 50-day EMA (rising) — not compared with SPY'", "Outperforming · strengthening — relative to SPY, not absolute price" == p["tips"][0] and p["tips"][1] == "Own price vs 50-day EMA (rising) — not compared with SPY" and "(falling)" in c["XLU"]["tips"][1], p["tips"])
                check(f"CARD[{tag}] 2 lines: 'SYM Name' then one chip row; no state label / bars / gauges / momentum chip on the card", p["l1"] == "☆PAVE PAVE name" and "bars in state" not in p["text"] and "vs 1y norm" not in c["PAVE"]["text"].split("Details")[0] and p["gaugesOutsideDetails"] == 0 and len(p["chips"]) == 2, p)
                check(f"CARD[{tag}] line 2 never wraps/overflows; chips fully inside; page has no horizontal scroll", all(c[s]["chipsInside"] and c[s]["noHScroll"] and c[s]["oneRow"] and c[s]["docW"] for s in ("PAVE", "XLU", "XLE", "XLF", "XLK")), {s: [c[s]["chipsInside"], c[s]["noHScroll"], c[s]["oneRow"], c[s]["docW"]] for s in ("PAVE", "XLU", "XLE", "XLF", "XLK")})
                if wdt == 390:
                    print("INFO 390: 52W gap visible per card:", {s: c[s]["gapVisible"] for s in ("PAVE", "XLU", "XLE", "XLF", "XLK")})
                else:
                    check("CARD[1440] 52W gap shown when there is room", all(c[s]["gapVisible"] for s in ("PAVE", "XLU", "XLE", "XLF", "XLK")), {s: c[s]["gapVisible"] for s in c if s != "det"})
                check(f"CARD[{tag}] Details holds bars in state, 52W gap, both 1y-norm gauges + words, raw values, freshness", all(k in c["det"] for k in ("Bars in state", "52W gap", "RS level vs 1y norm", "RS momentum vs 1y norm", "Raw RS trend", "Freshness", "Flat = barely moving")), c["det"][:300])
            # fit rule: when the row is too narrow the 52W text is what disappears; chips stay
            nar = js(page, r"""()=>{ const lean = document.querySelector('#ffThemes [data-rr="PAVE"] .rr-lean'); lean.style.width = '200px';
               const chips = [...lean.querySelectorAll('.rr-ch')], gap = lean.querySelector('.rr-gap'), r = lean.getBoundingClientRect();
               const o = {chipsInside: chips.every(e=>e.getBoundingClientRect().right <= r.right + 0.5 && e.getBoundingClientRect().bottom <= r.bottom + 0.5), gapHidden: gap.getBoundingClientRect().top >= r.bottom - 0.5}; lean.style.width = ''; return o; }""")
            check("CARD fit rule: too narrow -> 52W-gap text is hidden first, both chips stay fully visible", nar["chipsInside"] and nar["gapHidden"], nar)

            # Today › Sectors uses the same lean line
            td = js(page, r"""()=>{ ['PAVE','SMH'].forEach(s=>sdWrite(s, n=>{ n.follow = true; return n; })); const h = document.createElement('div'); h.innerHTML = tdSectorsHtml(); document.body.appendChild(h);
               const rows = [...h.querySelectorAll('.sd-tr')].map(r=>({sym: r.getAttribute('data-sd-trow'), chips: [...r.querySelectorAll('.rr-ch')].map(e=>e.innerText.trim()), gap: (r.querySelector('.rr-gap')||{}).innerText, wait: !!r.querySelector('[data-rr-wait]'), txt: r.innerText.replace(/\s+/g,' ')})); h.remove(); return rows; }""")
            pave = [r for r in td if r["sym"] == "PAVE"][0]; smh = [r for r in td if r["sym"] == "SMH"][0]
            check("TODAY Sectors row = same lean line (chips + gap); old-model sector shows 'Old model — refreshing…' only", pave["chips"] == ["Beating SPY ↗", "▲ Up +3.2%"] and pave["gap"] == "−5.9% from 52W high" and "bars in state" not in pave["txt"] and smh["wait"] and not smh["chips"], td)
            check("no console errors", not [e for e in ce if "favicon" not in e.lower()] and not pe, {"ce": ce[:3], "pe": pe[:3]})
        finally:
            b.close()
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results)-len(bad)}/{len(results)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
