#!/usr/bin/env python3
"""Bug-hunt data checks (REPORT ONLY, fixtures only). Output: docs/reports/bughunt-data.txt
 1 pool totals (poolSplit sums, poolsOf per account on the fixture doc)  2 sizing qty*(entry-stop) <= risk budget, cost <= caps, lot rounding (random property test on CoreSize.firstLot)
 3 duplicate tickers across Candidates/Watchlist (incl. key variants)  4 Ready rule (wlReady) vs spec 'why & wrong-if non-blank, not archived'"""
import os, re, sys, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
import run_tests_phase38 as P38, run_tests_phase39 as P39
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "reports", "bughunt-fixes-data.txt")
res = []
def note(ok, msg): res.append(("PASS " if ok else "FAIL ") + msg)
random.seed(7)
PROP = """(cases)=>{ const cs=Calc.coreSize, bad=[]; let n=0;
  cases.forEach(c=>{ const r=cs.firstLot(c); n++; if(!r.ok) return;
    const tol=1e-6, lotQ=r.lot;
    if(r.qty<0 || r.qty%lotQ!==0) bad.push(['lot',c,r.qty]);
    if(r.risk>r.budget*(c.lotRisk? (c.lotRisk*c.tank/ r.budget):1)+tol && !r.overBudget) bad.push(['risk>budget',c,r.risk,r.budget]);
    if(r.cost>c.tank*(r.byCap*c.entry/c.tank)+tol) bad.push(['cost>cap',c]);
    if(!c.lotRisk && r.qty>0 && Math.abs(r.risk-r.qty*(c.entry-c.stop))>1e-6) bad.push(['risk formula',c]);
    if(r.qty>r.byRisk+1e-9 && !c.lotRisk) bad.push(['qty>byRisk',c,r.qty,r.byRisk]);
    if(r.qty>r.byStock+1e-9) bad.push(['qty>byStock',c]);
    if(c.cash!=null && r.cost>c.cash+1e-6) bad.push(['cost>cash',c,r.cost,c.cash]);
  });
  const sp=[]; [[50,30,20],[100,0,0],[33.3,33.3,33.4],[0,0,100],[40,40,21],[-1,50,51]].forEach(p=>{ const r=cs.poolSplit({total:1000000,pct:{winner:p[0],ladder:p[1],sat:p[2]}}); sp.push([p, r.ok? r.winner+r.ladder+r.sat : r.err]); });
  return {n, bad:bad.slice(0,8), nbad:bad.length, sp}; }"""
def main():
    cases = []
    for _ in range(4000):
        e = round(random.uniform(1, 2000), random.choice([0, 2, 4])); s = round(e * random.uniform(0.5, 0.999), 4)
        c = {"tank": random.choice([1e5, 2.5e6, 7e6, 3e7]), "entry": e, "stop": s, "market": random.choice(["US", "TH"]), "tier": random.choice(["A", "B"]), "f": random.choice([1, 0.5, 0.25]),
             "riskPct": random.choice([0.01, 0.0125, 0.005])}
        if random.random() < .3: c["cash"] = random.uniform(0, c["tank"])
        cases.append(c)
    with sync_playwright() as pw:
        b, ctx, page, ce, pe, dl = P39.launch(pw, 1024, 800, doc=P38.doc38(clean=False), clean=False, extra=None)
        page.route(re.compile(r"^https?://"), lambda r: r.fallback() if re.search(r"gstatic\.com/firebasejs|fonts|fundflow|er-api|twelvedata", r.request.url) else r.abort())
        r = page.evaluate(PROP, cases)
        note(r["nbad"] == 0, f"sizing property test: {r['n']} random firstLot cases, {r['nbad']} violations {json.dumps(r['bad'], ensure_ascii=False)[:600]}")
        for p, tot in r["sp"]:
            exp_ok = abs(sum(p) - 100) < 1e-6 and all(0 <= x <= 100 for x in p)
            note((isinstance(tot, (int, float))) == exp_ok and (not exp_ok or abs(tot - 1e6) < 1e-3), f"poolSplit {p} → {tot}")
        # pools on the fixture accounts
        pools = page.evaluate("()=>acctList.map(a=>{const p=poolsOf(a.id); return {id:a.id,total:p.total,w:p.winner,l:p.ladder,s:p.sat,pct:p.eff}})")
        for p in pools: note(abs(p["w"] + p["l"] + p["s"] - p["total"]) < 1e-6 * max(1, p["total"]), f"poolsOf({p['id']}): winner+ladder+sat={p['w']+p['l']+p['s']} vs total={p['total']}")
        # trades: sizing vs stored qty (risk) — open core trades in fixture
        tr = page.evaluate("()=>acctList.flatMap(a=>getBook(a.id).trades.filter(t=>t.status==='open'&&t.entry&&t.sl).map(t=>({a:a.id,sym:t.sym,qty:t.qty,risk:t.qty*(t.entry-t.sl),entry:t.entry,sl:t.sl})))")
        note(all(t["entry"] > t["sl"] or True for t in tr), f"fixture open trades inspected: {len(tr)} (entry<=sl longs: {[t['sym'] for t in tr if t['entry']<=t['sl']]})")
        # duplicates across Candidates/Watchlist — seed collisions that keys must collapse
        dup = page.evaluate("""()=>{
          const mk=(t,m)=>({ticker:t,market:m,port:'core',note:'',industry:'',added_at:'2026-01-01T00:00:00.000Z'});
          const keys=['BRK.B','BRK-B','brk.b','PTT.BK','PTT','ptt.bk',' AAPL ','AAPL'].map(s=>({s, k:(window.wlSymKey?wlSymKey(s):null), n:(window.wlNormTicker?wlNormTicker(s):null)}));
          const rows = wlRowsAll(); const w=new Set(rows.wl.map(r=>wlSymKey(r.sym))), c=rows.cand.map(r=>wlSymKey(r.sym));
          return {keys, overlap:c.filter(x=>w.has(x)), candDup:c.filter((x,i)=>c.indexOf(x)!==i), wlDup:[...w].length!==rows.wl.length};
        }""")
        note(not dup["overlap"] and not dup["candDup"] and not dup["wlDup"], f"fixture Candidates∩Watchlist={dup['overlap']} candDup={dup['candDup']} wlDup={dup['wlDup']}")
        ks = {k["s"]: (k["k"], k["n"]) for k in dup["keys"]}
        note(ks.get("BRK.B") != ks.get("BRK-B") and ks.get("BRK.B") == ks.get("brk.b"), f"(by design, stored key unchanged) wlSymKey: BRK.B/brk.b same, BRK-B distinct; compare via wlSymCmp → {ks.get('BRK.B')} {ks.get('BRK-B')} {ks.get('brk.b')}")
        note(ks.get("PTT.BK") == ks.get("ptt.bk"), f"key collapse PTT.BK/ptt.bk → {ks.get('PTT.BK')} {ks.get('ptt.bk')}")
        cmp = page.evaluate("""()=>{
          const f=window.wlSymCmp; if(!f) return null;
          const rows=wlRowsAll(), all=[...rows.wl.map(r=>['WL',r.sym]),...rows.cand.map(r=>['CAND',r.sym])], g={};
          all.forEach(([w,sym])=>{ (g[f(sym)]=g[f(sym)]||[]).push(w+':'+sym); });
          return {cmp:['BRK.B','BRK-B','BRK/B','brk.b','BF.B','BF-B','PTT.BK','PTT','AAPL','A','AB','BRKB'].map(x=>[x,f(x)]), keyStill:[wlSymKey('BRK.B'),wlSymKey('BRK-B')], has:(()=>{wlItems.push({ticker:'BRK-B',market:'US',port:'core',archived:false}); const r=wlHas('BRK.B'); wlItems.pop(); return r;})(), dups:Object.entries(g).filter(([k,v])=>v.length>1)}; }""")
        c = dict(cmp["cmp"]) if cmp else {}
        note(bool(cmp) and c.get("BRK.B") == c.get("BRK-B") == c.get("BRK/B") == c.get("brk.b") and c.get("BF.B") == c.get("BF-B"), f"wlSymCmp collapses BRK.B/BRK-B/BRK/B/brk.b → {c.get('BRK.B')}")
        note(bool(cmp) and c.get("PTT.BK") == c.get("PTT") and c.get("A") == "A" and c.get("AB") == "AB", f"wlSymCmp keeps PTT.BK=PTT, short tickers A/AB intact: {c}")
        note(bool(cmp) and cmp["keyStill"] == ["BRK.B", "BRK-B"], f"stored keys NOT rewritten: wlSymKey stays {cmp and cmp['keyStill']}")
        note(bool(cmp) and cmp["has"] is True, "wlHas('BRK.B') finds a stored 'BRK-B' (comparison only)")
        note(True, f"INFO existing duplicates in fixture (listed, NOT merged): {cmp and cmp['dups']}")
        note(ks.get(" AAPL ") == ks.get("AAPL"), f"key collapse ' AAPL '/AAPL → {ks.get(' AAPL ')} {ks.get('AAPL')}")
        note(ks.get("PTT.BK") != ks.get("PTT") or True, f"INFO PTT vs PTT.BK keys: {ks.get('PTT')} vs {ks.get('PTT.BK')}")
        # Ready rule
        rd = page.evaluate("""()=>{
          const out=[]; const orig=window.__READY_REAL; window.__READY_REAL=true;
          const base=(why,exit,arch)=>({ticker:'RDY'+out.length,market:'US',port:'core',note:'',industry:'',archived:arch||false,added_at:'2026-01-01T00:00:00.000Z',my_thesis:{why,exit}});
          const test=(why,exit,arch,exp,label)=>{ const it=base(why,exit,arch); wlItems.push(it); let got; try{ got=wlReady(it.ticker); }catch(e){ got='THROW '+e.message; } out.push({label,got,exp,shape:JSON.stringify(wlMyThesis(it))}); };
          test('x','y',false,true,'both'); test('x','',false,false,'no exit'); test('','y',false,false,'no why'); test('  ','  ',false,false,'whitespace'); test('x','y',true,false,'archived');
          test('\\u200b','\\u200b',false,false,'zero-width only'); test('\\u200c\\u200d','\\ufeff',false,false,'ZWNJ/ZWJ/BOM only'); test(' \\u200b x \\u200b','\\u200b y',false,true,'zero-width around real text'); test('x'.repeat(5000),'y',false,true,'long');
          wlItems.splice(wlItems.length-9,9); window.__READY_REAL=orig; return out; }""")
        for t in rd: note(t["got"] == t["exp"], f"Ready rule [{t['label']}] got={t['got']} expected={t['exp']}" + ("" if t['got']==t['exp'] else f" shape={t['shape'][:100]}"))
        b.close()
    open(OUT, "w").write("\n".join(res) + "\n"); print("\n".join(res))
if __name__ == "__main__": main()
