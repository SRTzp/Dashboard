#!/usr/bin/env python3
"""RE-B — hidden read-only dry run page (?re1dry=1): renders with the mock store, performs ZERO writes (Firestore set/update/delete/add + localStorage),
no visible entry point without the flag, both accounts reported, downloads re1-dryrun-<date>.md/.json. Screenshot tests/screenshots/re1b-dryrun-1440.png
Run: python3 run_tests_re1b.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import ln3fix_common as C
import lib_phase4 as base
import lib_phase38 as P38
import lib_phase39 as P39

js = C.js
results = []
HERE = os.path.dirname(os.path.abspath(__file__))


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + ((" :: " + d[:600]) if (not ok and d) else ""))


def tr(**o):
    t = {"port": "core", "bias": "Long", "mult": 1, "cur": "THB", "status": "open", "date": "2026-09-29", "qty": 100, "entry": 100, "sl": 95, "tp": None}
    t.update(o); return t


def doc():
    d = P38.doc38(clean=True)
    for b in d["books"].values(): b["settings"].pop("satWeekPick", None)
    m = d["books"]["main"]; f = d["books"]["fam"]
    m["trades"] = [
        tr(id="m1", sym="AAPL", cur="USD", qty=6, entry=200, sl=195, posGroup="m1", sl0=190),
        tr(id="m1x", sym="AAPL", cur="USD", qty=4, entry=200, sl=190, status="closed", exitPrice=210, exitDate="2026-10-01", closedAt="2026-10-01T04:00:00.000Z", posGroup="m1", sl0=190),
        tr(id="m2", sym="PTT.BK", qty=1000, entry=36, sl=35, status="closed", exitPrice=35, exitDate="2026-09-30"),
        tr(id="b1", sym="ZZZ.BK", qty=3, entry=10, sl=9, status="closed", exitPrice=10.1, exitDate="2026-09-22", closedAt="2026-09-22T03:00:00.000Z"),
        tr(id="l1", sym="MSFT", cur="USD", qty=5, entry=400, sl=380, posGroup="l1", sl0=380),
        tr(id="l1a", sym="MSFT", cur="USD", qty=5, entry=390, sl=380, posGroup="l1", acc=True, accOf="l1", sl0=380),
        tr(id="l1b", sym="MSFT", cur="USD", qty=5, entry=380, sl=380, posGroup="l1", sl0=380),
    ]
    f["trades"] = [tr(id="f2", sym="PTT.BK", qty=200, entry=36, sl=35)]
    return d


def cards():
    return {
        "cA": {"acct": "main", "ticker": "AAPL", "market": "US", "strategy": "W", "status": "open", "trade_id": "m1", "stopHistory": [{"date": "2026-09-30", "from": 190, "to": 195}], "lots": [{"n": 1, "px": 200, "qty": 10}], "plan": {"entry": 200, "stop": 190}},
        "cL": {"acct": "main", "ticker": "MSFT", "market": "US", "strategy": "L", "status": "open", "trade_id": "l1", "acc_trade_id": "l1a", "stopHistory": [], "lots": [{"n": 1, "px": 400, "qty": 5}, {"n": 2, "px": 390, "qty": 5, "layer": "acc"}, {"n": 3, "px": 380, "qty": 5}]},
        "cP": {"acct": "main", "ticker": "NVDA", "market": "US", "strategy": "W", "status": "plan", "plan": {"entry": 120, "stop": 110, "ps1": {"rows": [{"px": 120, "qty": 50}]}}, "ln4": {"placedLv": {"0": "2026-10-01T02:00:00.000Z"}}},
    }


SPY = """()=>{
  window.__writes = []; window.__ls = [];
  const wrap = (obj, names, tag) => names.forEach(n => { const o = obj[n]; if(typeof o==='function') obj[n] = function(){ window.__writes.push(tag+'.'+n); return o.apply(this, arguments); }; });
  const deep = (x, tag) => { if(!x || typeof x!=='object') return x; wrap(x, ['set','update','delete','add'], tag); ['doc','collection'].forEach(k => { const o = x[k]; if(typeof o==='function') x[k] = function(){ return deep(o.apply(this, arguments), tag+'/'+k); }; }); return x; };
  const db = window.firebase.firestore(); const col = db.collection; db.collection = function(){ return deep(col.apply(this, arguments), 'db'); };
  ['setItem','removeItem','clear'].forEach(n => { const o = Storage.prototype[n]; Storage.prototype[n] = function(){ window.__ls.push(n+':'+(arguments[0]||'')); return o.apply(this, arguments); }; });
}"""


def run(pw):
    # ── A · without the flag: no entry point, no overlay, function inert
    b, ctx, page, ce, pe, dl = P39.launch(pw, 1440, 900, doc=doc(), cards=cards(), clean=True)
    try:
        js(page, "()=>{ openSettings() }"); page.wait_for_timeout(600)
        check("no flag: no dry-run row in Settings", js(page, "()=>document.querySelectorAll('[data-re1-dry-row],[data-re1-run],#re1DryOv').length") == 0)
        check("no flag: re1DryRun() is inert", js(page, "()=>re1DryRun()") is None and js(page, "()=>!document.getElementById('re1DryOv')"))
        check("no flag: no console / page errors", not ce and not pe, ce + pe)
    finally:
        b.close()
    # ── B · with ?re1dry=1
    P39.INDEX = P39.INDEX.split("?")[0] + "?re1dry=1"
    b, ctx, page, ce, pe, dl = P39.launch(pw, 1440, 900, doc=doc(), cards=cards(), clean=True)
    downloads = []
    page.on("download", lambda d: downloads.append(d))
    try:
        js(page, "()=>{ openSettings() }"); page.wait_for_timeout(600)
        check("flag: dry-run row appears in Settings", js(page, "()=>document.querySelectorAll('[data-re1-dry-row] [data-re1-run]').length") == 1)
        before_db = js(page, "()=>JSON.stringify(window.firebase.__mockDb.__dump())")
        before_ls = js(page, "()=>JSON.stringify(Object.assign({}, localStorage))")
        js(page, SPY)
        page.locator("[data-re1-run]").click(); page.wait_for_timeout(900)
        check("report overlay opened", js(page, "()=>!!document.getElementById('re1DryOv')"))
        txt = js(page, "()=>document.querySelector('[data-re1-md]').textContent")
        check("report shows Main and Family separately", "Account: " in txt and "(`main`)" in txt and "(`fam`)" in txt, txt[:200])
        check("report says read-only and Unknown (never 0)", "Read-only" in txt and "Unknown" in txt)
        check("report lists legacy-shape Compounder card", "legacy shape" in txt and "MSFT" in txt)
        check("report lists missing costs + equity proxy", "COSTS" in txt and "PROXY" in txt)
        check("report has strict-sign badge change", "Journal outcome badges" in txt and "be → win" in txt, txt[txt.find("Journal outcome"):][:300])
        check("report has no NaN / undefined / Infinity", not any(w in txt for w in ("NaN", "undefined", "Infinity")))
        check("two files downloaded (md + json)", len(downloads) == 2 and sorted(d.suggested_filename for d in downloads) == ["re1-dryrun-2026-10-02.json", "re1-dryrun-2026-10-02.md"], [d.suggested_filename for d in downloads])
        if downloads:
            p = [d for d in downloads if d.suggested_filename.endswith(".json")][0].path()
            j = json.load(open(p)); check("json report parses, 2 accounts, readOnly", len(j["accounts"]) == 2 and j["readOnly"] is True)
        writes = js(page, "()=>window.__writes"); ls = js(page, "()=>window.__ls")
        check("ZERO Firestore set/update/delete/add calls during the dry run", writes == [], writes)
        check("ZERO localStorage setItem/removeItem/clear calls", ls == [], ls)
        check("mock Firestore store unchanged", js(page, "()=>JSON.stringify(window.firebase.__mockDb.__dump())") == before_db)
        check("localStorage content unchanged", js(page, "()=>JSON.stringify(Object.assign({}, localStorage))") == before_ls)
        # no-write also when run twice + download buttons
        page.locator("[data-re1-dl=md]").click(); page.wait_for_timeout(300)
        check("still zero writes after extra download click", js(page, "()=>window.__writes.length + window.__ls.length") == 0)
        check("no console / page errors with the flag", not ce and not pe, ce + pe)
        page.screenshot(path=os.path.join(HERE, "screenshots", "re1b-dryrun-1440.png"))
    finally:
        b.close()


with sync_playwright() as pw:
    run(pw)
bad = [r for r in results if not r[1]]
print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
