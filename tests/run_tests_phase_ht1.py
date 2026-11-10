#!/usr/bin/env python3
"""HT1 — one tight HOT rule (Today · Watch groups · TV export). Fixture = live distribution:
lead 5 · lead+fresh 10 · imp+fresh 1 · lag 1 · lag+fresh 5 · flat+fresh 1."""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase106 as T
js = C.js
results = []
def check(n, ok, d=""):
    results.append((n, bool(ok))); print(("PASS" if ok else "FAIL") + " - " + n + ((" :: " + str(d)[:500]) if not ok else ""))

FIX = """()=>{
  const rows = []; let i = 0;
  const add = (q, n, fresh, base)=>{ for(let k=0;k<n;k++){ i++; rows.push({sym:'S'+String(i).padStart(2,'0'), quad:q, ratio:base-k*0.1, dMom: fresh ? 1.5 : 0.1, days: fresh ? 1 : 30, prevDays: 20}); } };
  add('lead',5,false,104); add('lead',10,true,106); add('imp',1,true,99); add('lag',1,false,95); add('lag',5,true,94); add('flat',1,true,100);
  return rows; }"""

def tests(pw, w, h):
    tag = f"[{w}]"
    b, page, ce, pe = T.launch(pw, w, h, iso=T.NOW, picks=(), weekly=False)
    try:
        rows = js(page, FIX)
        res = page.evaluate("""(rows)=>{ window.rrgIsFresh = x=>x.days<=3; window.rrgWaiting = ()=>false; window.rrgSortRows = r=>r.slice().sort((a,b)=>({lead:0,imp:1,weak:2,lag:3,flat:4}[a.quad]-{lead:0,imp:1,weak:2,lag:3,flat:4}[b.quad])||(b.dMom-a.dMom)||(b.ratio-a.ratio));
          const all = rows.filter(x=>x.quad==='lead'||(x.quad==='imp'&&rrgIsFresh(x))).length;
          const hot = hotSectorsFrom(rows,'D'); return {all, hot:hot.map(h=>h.etf+':'+h.k), quads:hot.map(h=>h.row.quad)}; }""", rows)
        check(f"{tag} live distribution (23 sectors): HOT <= 5 (was 22)", len(res["hot"]) <= 5 and len(res["hot"]) == 5, res)
        check(f"{tag} no lag/flat/weak in HOT", all(q in ("lead", "imp") for q in res["quads"]), res)
        # imp+fresh included when it ranks in top 5
        r2 = page.evaluate("""(rows)=>{ const few = rows.filter(x=>x.quad==='imp'||x.quad==='lag'||x.quad==='flat'||x.sym<='S03'); return hotSectorsFrom(few,'D').map(h=>h.etf+':'+h.k); }""", rows)
        check(f"{tag} imp+fresh included when in top 5 (blue Fresh)", any(x.endswith(":fresh") for x in r2), r2)
        # star lagging: Today shows with star, Watch/TV not HOT
        r3 = page.evaluate("""(rows)=>{
          const lag = rows.find(x=>x.quad==='lag'); const sy = lag.sym;
          window.rrgRowsNow = ()=>rows; window.rrgTf = ()=>'D'; window.tv1SecName = e=>e;
          window.sectorState = e=>({quad:(rows.find(x=>x.sym===e)||{}).quad, followed:e===sy});
          const td = ln4HotSectors(); const chip = td.find(h=>h.etf===sy);
          return {sy, chip, hotCount: td.filter(h=>h.hot).length, tv: tv1HotOf(sy), sh: sectorHot({sector_etf:sy}), leadTv: tv1HotOf(hotSectors()[0].etf)}; }""", rows)
        check(f"{tag} ★ lagging: on Today with ★, not HOT; not in Watch/TV HOT", r3["chip"] and r3["chip"]["star"] and not r3["chip"]["hot"] and not r3["tv"] and not r3["sh"] and r3["leadTv"] and r3["hotCount"] == 5, r3)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()

if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            try: tests(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[{w}] crashed", False, str(e))
    n = sum(1 for r in results if r[1]); print(f"\n{n}/{len(results)} PASS"); sys.exit(0 if n == len(results) else 1)
