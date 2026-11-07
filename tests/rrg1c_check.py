#!/usr/bin/env python3
"""RRG1c — queue must not stall: hidden tab, reload mid-queue, credit error on batch 2, state rebuilt mid-run.
Fake timers in-page (Date.now virtual, rrgSleep advances it). รัน: python3 tests/rrg1c_check.py"""
import json, sys
import ln3fix_common as C
from rrg1b_check import HELPERS
from playwright.sync_api import sync_playwright

js = C.js
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:700]) if (d and not ok) else ""))


VIS = "(v)=>{ Object.defineProperty(document,'hidden',{value:!v,configurable:true}); document.dispatchEvent(new Event('visibilitychange')); }"
BAR = "()=>document.getElementById('ffRrgBar').innerText.replace(/\\s+/g,' ')"


def main():
    with sync_playwright() as pw:
        b, page, ce, pe = C.launch(pw, 1280, 900, cards=False)
        try:
            js(page, HELPERS)
            js(page, "()=>{ rrgAutoDone = true; switchTab('flow'); rrgReset(); rrgReset(); }")

            # ---------- 1. hidden tab: sleeping timer is lost, tab comes back ----------
            js(page, "()=>{ __mock({}); }")
            r = js(page, r"""async()=>{
              const f = ffState(); f.rrg = {rowsD:[], rowsW:[], loading:false, err:''};
              let hang = false, n = 0;
              const orig = window.rrgSleep;
              window.rrgSleep = (ms)=>{ if(hang) return new Promise(()=>{}); window.__sleeps.push(ms); window.__t += ms; return Promise.resolve(); };
              const fetchOrig = window.rrgFetchBatch;
              window.rrgFetchBatch = async (syms,k)=>{ const o = await fetchOrig(syms,k); n++; if(n === 1) hang = true; return o; };   // after batch 1 the timer is "lost"
              rrgRefresh(true);
              for(let i=0;i<20;i++) await new Promise(r=>setTimeout(r,0));
              const mid = {calls: __calls.length, pending: (f.rrg.pending||[]).length, busy: rrgBusy};
              const barStuck = document.getElementById('ffRrgBar').innerText.replace(/\s+/g,' ');
              __t += 3*60000; hang = false;      // 3 minutes pass while the tab is hidden
              document.dispatchEvent(new Event('visibilitychange'));   // (visible: document.hidden is false in headless)
              for(let i=0;i<60;i++) await new Promise(r=>setTimeout(r,0));
              const ff = ffState();
              return {mid, barStuck, calls: __calls.map(c=>c.syms.length+':'+c.syms[0]), model: ff.rrg.model, pending: ff.rrg.pending, err: ff.rrg.err, loading: ff.rrg.loading, newModel: ff.rrg.rowsD.filter(x=>x.model===RRG_MODEL).length, nsym: RRG_SYMS.length, busy: rrgBusy};
            }""")
            check("HIDDEN batch 1 done, timer lost: 7 symbols saved, 16 pending", r["mid"]["calls"] == 1 and r["mid"]["pending"] == 16 and r["mid"]["busy"], r["mid"])
            check("HIDDEN tab visible again after >2 min: watchdog resets and resumes ONLY the missing symbols (no SPY/batch-1 refetch)", r["calls"][0].startswith("8:") and len(r["calls"]) == 3 and r["calls"][1].startswith("8:") and r["calls"][2].startswith("8:") and r["model"] == 2 and r["pending"] is None and not r["err"] and not r["loading"] and not r["busy"] and r["newModel"] == r["nsym"], r)

            # ---------- 2. reload mid-queue: persisted loading:true + pending, nothing running ----------
            js(page, HELPERS); js(page, "()=>{ __mock({}); rrgAutoDone = true; switchTab('flow'); rrgReset(); }")
            r = js(page, r"""async()=>{
              const f = ffState(); const done = RRG_SYMS.slice(0,7).map(d=>d.s), pend = RRG_SYMS.slice(7).map(d=>d.s);
              const row = (s)=>({sym:s, name:s, quad:'lead', ratio:101, mom:101, dMom:0.1, dRatio:0.1, days:3, off52:-1, date:'2026-11-04', model:RRG_MODEL});
              f.rrg = {rowsD: done.map(row), rowsW: done.map(row), pending: pend.slice(), loading:true, err:'', build:RRG_BUILD};
              localStorage.setItem('rrgLastBatchAt', String(__t - 10000));      // last request 10 s ago -> next allowed in 51 s
              localStorage.setItem('rrgAutoAttemptAt', String(__t - 5000));
              rrgAutoDone = false; rrgBusy = false; rrgProg = null;
              const idle = ffState().rrg.loading;                               // stale loading flag must be dropped when nothing runs
              const t0 = __t; let waitBar = null;
              window.rrgSleep = async (ms)=>{ if(waitBar === null) waitBar = document.getElementById('ffRrgBar').innerText.replace(/\s+/g,' '); window.__sleeps.push(ms); window.__t += ms; };
              rrgAutoOnce();
              for(let i=0;i<5;i++) await new Promise(r=>setTimeout(r,0));
              const bar = waitBar;
              for(let i=0;i<60;i++) await new Promise(r=>setTimeout(r,0));
              const ff = ffState();
              return {idle, bar, first: __calls[0] && (__calls[0].t - t0), calls: __calls.map(c=>c.syms.length+':'+c.syms[0]), pend: pend.length, model: ff.rrg.model, pending: ff.rrg.pending};
            }""")
            check("RELOAD stale persisted loading:true is not trusted when nothing is running", r["idle"] is False, r)
            check("RELOAD resumes on load: only the 16 pending symbols (2 batches), honouring the saved next-allowed time (>= 51 s later)", len(r["calls"]) == 2 and r["first"] is not None and r["first"] >= 51000 and r["model"] == 2 and r["pending"] is None, r)
            check("RELOAD status line shows batch x/y + countdown while waiting", "batch" in r["bar"] and "/" in r["bar"] and "next in" in r["bar"], r["bar"])

            # ---------- 3. credit error on batch 2 ----------
            js(page, HELPERS); js(page, "()=>{ __mock({2:3}); rrgAutoDone = true; switchTab('flow'); rrgReset(); ffState().rrg = {rowsD:[], rowsW:[], loading:false, err:''}; }")
            r = js(page, r"""async()=>{
              await rrgRefresh(true);
              const f = ffState();
              const bar = document.getElementById('ffRrgBar').innerText.replace(/\s+/g,' ');
              const retry = !!document.querySelector('#ffRrgBar [data-rrg-retry]');
              const o = {calls: __calls.length, bar, retry, err: f.rrg.err, pending: (f.rrg.pending||[]).length, loading: f.rrg.loading, busy: rrgBusy, newModel: f.rrg.rowsD.filter(x=>x.model===RRG_MODEL).length};
              // not auto-looping: visibility / watchdog must NOT restart a queue that stopped on an error
              __t += 10*60000; document.dispatchEvent(new Event('visibilitychange')); rrgWatchdog();
              for(let i=0;i<20;i++) await new Promise(r=>setTimeout(r,0));
              o.callsAfterVisible = __calls.length;
              // Retry -> only the remaining symbols
              __calls.length = 0; __mock({});
              document.querySelector('#ffRrgBar [data-rrg-retry]').click();
              for(let i=0;i<60;i++) await new Promise(r=>setTimeout(r,0));
              const ff = ffState();
              o.retryCalls = __calls.map(c=>c.syms.length+':'+c.syms[0]); o.model = ff.rrg.model; o.pending2 = ff.rrg.pending;
              return o;
            }""")
            check("CREDIT batch 2 fails 3x: stops with clear error + Retry button; batch 1 kept (7 new), no endless loop", r["calls"] == 4 and "Price limit reached" in r["bar"] and r["retry"] and r["pending"] == 16 and not r["loading"] and not r["busy"] and r["newModel"] == 7 and r["callsAfterVisible"] == 4, r)
            check("CREDIT Retry resumes only the 16 missing symbols and finishes", len(r["retryCalls"]) == 2 and r["model"] == 2 and r["pending2"] is None, r)

            # ---------- 4. state rebuilt from a Firestore snapshot in the middle of a run ----------
            js(page, HELPERS); js(page, "()=>{ __mock({}); rrgAutoDone = true; switchTab('flow'); rrgReset(); ffState().rrg = {rowsD:[], rowsW:[], loading:false, err:''}; }")
            r = js(page, r"""async()=>{
              const fo = window.rrgFetchBatch; let n = 0;
              window.rrgFetchBatch = async (syms,k)=>{ const o = await fo(syms,k); n++;
                if(n === 2){ state.fundflow = JSON.parse(JSON.stringify(state.fundflow)); }   // what onSnapshot -> buildStateFromBook does: new object
                return o; };
              await rrgRefresh(true);
              const ff = ffState();
              return {model: ff.rrg.model, pending: ff.rrg.pending, newModel: ff.rrg.rowsD.filter(x=>x.model===RRG_MODEL).length, nsym: RRG_SYMS.length, loading: ff.rrg.loading, calls: __calls.length};
            }""")
            check("REBUILD state replaced mid-run: results land in the live state, run finishes, nothing stuck 'loading'", r["model"] == 2 and r["pending"] is None and r["newModel"] == r["nsym"] and not r["loading"] and r["calls"] == 3, r)

            check("no console errors", not [e for e in ce if "favicon" not in e.lower()] and not pe, {"ce": ce[:3], "pe": pe[:3]})
        finally:
            b.close()
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results)-len(bad)}/{len(results)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
