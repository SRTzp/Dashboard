#!/usr/bin/env python3
"""MS1 — SL tighter than the min stop: never blocks; size = budget ÷ min-stop distance; amber pill + 'Risk if SL hit · budget'.
Sat (XAUUSD min 0.5% = 10 pts @2000) + Core planSize (MMT 4% / COMP 7%) + SL ≥ min unchanged. Run: python3 run_tests_phaseMS1.py"""
import json
from playwright.sync_api import sync_playwright
import run_tests_phase121 as S
import run_tests_phase77 as P77

js, settle, check, results = S.js, S.settle, S.check, S.results


def tests(pw, w, h):
    tag = f"[ms1/{w}]"
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        S.ps_set(page)
        # Sat: SL 9 pts (<10) → sized on 10
        iid = S.sat_plan(page, "XAUUSD", 2000, 1991, 2040)
        c = S.calc(page, iid)
        ok_blk = not any("too tight" in x for x in c["blocks"])
        js(page, "([i])=>satV3PlanEdit(i,'sl','1990')", [iid]); settle(page, 300)
        cm = S.calc(page, iid)   # SL exactly at min (10 pts) = the reference sizing
        js(page, "([i])=>satV3PlanEdit(i,'sl','1991')", [iid]); settle(page, 300)
        check(f"{tag} Sat SL 9 < min 10: no 'too tight' block · raw size == size at SL=min (budget ÷ 10 pts) · Risk if SL hit < budget",
              ok_blk and abs(c["raw"] - cm["raw"]) < 1e-12 and c["dealTHB"] < c["riskTHB"], [c, cm["raw"]])
        pill = js(page, "()=>{ const e=document.querySelector('[data-ln4-cp=stop]'); return e ? e.textContent : ''; }")
        check(f"{tag} Sat amber pill text", "Sized on min stop 10" in pill and "your SL 9" in pill, pill)
        rk = js(page, "()=>{ const e=document.querySelector('[data-ln1-risk]'); return e ? e.textContent : ''; }")
        check(f"{tag} Sat row 'Risk if SL hit … · budget …'", "Risk if SL hit" in rk and "budget" in rk, rk)
        # SL ≥ min unchanged
        js(page, "([i])=>satV3PlanEdit(i,'sl','1985')", [iid]); settle(page, 300)
        c2 = S.calc(page, iid)
        pill2 = js(page, "()=>{ const e=document.querySelector('[data-ln4-cp=stop]'); return e ? e.textContent : ''; }")
        rk2 = js(page, "()=>{ const e=document.querySelector('[data-ln1-risk]'); return e ? e.textContent : ''; }")
        check(f"{tag} Sat SL 15 ≥ min: raw = budget ÷ 15 pts, no min-stop pill, plain 'Risk'", abs(c2["raw"] * 15 - cm["raw"] * 10) < 1e-9, [c2, pill2, rk2])
        check(f"{tag} Sat SL ≥ min: green 'Stop ≥ min' + no 'Risk if SL hit'", "Stop ≥ min" in pill2 and "Risk if SL hit" not in rk2, [pill2, rk2])
        # Core planSize
        r = js(page, """()=>{ const mk = (stopPct, mp)=>Ps1.planSize({E:1000000, market:'US', ideaRiskPct:0.5, entries:[{px:100}], stops:[{px:100*(1-stopPct/100)}], maxSizePct:100, minStopPct:mp});
          return {a:mk(2,4), b:mk(2,7), c:mk(5,4), d:mk(2,0)}; }""")
        # budget 5000 / (100*4%)=1250 sh
        check(f"{tag} Core MMT SL 2% < 4%: qty = 5000 ÷ 4 = 1250 · real risk 2500 < 5000 · minSized", r["a"]["qty"] == 1250 and abs(r["a"]["risk"] - 2500) < 1e-6 and r["a"]["minSized"], r["a"])
        check(f"{tag} Core COMP SL 2% < 7%: qty = 5000 ÷ 7 ≈ 714", r["b"]["qty"] == 714 and r["b"]["minSized"], r["b"])
        check(f"{tag} Core SL 5% ≥ 4%: qty = 5000 ÷ 5 = 1000 · not minSized", r["c"]["qty"] == 1000 and not r["c"]["minSized"], r["c"])
        check(f"{tag} Core no min given: unchanged (2% → 2500 sh)", r["d"]["qty"] == 2500 and not r["d"]["minSized"], r["d"])
        m = js(page, """()=>Ps1.planSize({E:1000000, market:'US', ideaRiskPct:1, entries:[{px:100,riskPct:0.5},{px:98,riskPct:0.5}], stops:[{px:97}], maxSizePct:100, minStopPct:4})""")
        # row1 d=3<4 → 5000/4=1250 ; row2 d=1<3.92 → 5000/3.92=1275
        check(f"{tag} Core multi-entry: each row sized on its own min distance", [x["qty"] for x in m["rows"]] == [1250, 1275] and all(x["minSized"] for x in m["rows"]), m["rows"])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 1000), (390, 844)):
            tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nMS1: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
