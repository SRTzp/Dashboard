#!/usr/bin/env python3
"""HF4 — Place order write never sends `undefined` (Firestore rejects it): Sat Short/Long place · re-entry stored · Core place · the strict mock behaves like the real SDK.
Run: python3 tests/run_tests_hf4.py   (docs/briefs/HF4-brief.md)"""
import sys, os
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import run_tests_lrf as LF
import run_tests_lr3 as L3
import run_tests_hf3 as H

UNDEF = "()=>(window.__undefWrites || []).map(x=>x.path + ' :: ' + x.field)"
SNAP = "()=>{ const i = sat7dIdea('hfX'); const l = (i && i.ln4) || (bdById('hfX') && bdById('hfX').ln4) || {}; return l.snap ? l.snap['0'] : null; }"
RES = "()=>({st: bdById('hfX') ? bdById('hfX').status : null, open: !!document.getElementById('bdPop'), line: (document.querySelector('[data-hf3-block]')||{}).innerText || null})"


def part_sat(pw):
    # the mock itself: undefined throws unless ignoreUndefinedProperties is set
    b, page, ce, pe = launch(pw, 1440, 900, c=LF.cards_today())
    try:
        r = js(page, """()=>{ const d = firebase.firestore(), out = {}; const ref = d.collection('users').doc('hf4probe');
          try{ ref.set({a:1, n:{x:undefined}}); out.set = 'no throw'; }catch(e){ out.set = e.message; }
          try{ ref.set({a:1}); ref.update({b:undefined}); out.upd = 'no throw'; }catch(e){ out.upd = e.message; }
          return out; }""")
        # the app already called db.settings({ignoreUndefinedProperties:true}) at start-up → the same writes pass (and the offenders are listed)
        check("[mock] after the app's db.settings({ignoreUndefinedProperties:true}) an undefined field is dropped, not thrown", r["set"] == "no throw" and r["upd"] == "no throw", r)
        s = js(page, "()=>{ const d = firebase.firestore(); const x = d.collection('users').doc('hf4probe2'); x.set({a:1, n:{x:undefined}}); return JSON.stringify(firebase.__mockDb ? firebase.__mockDb.__getDoc(['users','hf4probe2']) : null); }")
        check("[mock] …and the stored doc has no undefined key", s is not None and "undefined" not in s and '"x"' not in s, s)
        st = js(page, "()=>typeof db.settings")
        check("[app] db.settings exists", st == "function")
    finally:
        b.close()
    for w, h in ((1440, 900), (390, 844)):
        for bias, sl, tp in (("Short", 2660, 2600), ("Long", 2620, 2700)):
            tag = "[%d %s]" % (w, bias)
            b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
            try:
                H.sat_open(page, {"bias": bias, "sl": sl, "tp": tp})
                js(page, "()=>{ window.__undefWrites = []; pb2PlaceYes(); }"); page.wait_for_timeout(600)
                r = js(page, RES); sn = js(page, SNAP)
                check(f"{tag} place (no re-entry, no model) → recorded, sheet closed, no ⚠ line", r["st"] == "ord" and not r["open"] and not r["line"], r)
                check(f"{tag} snapshot has no `reentry` key (and none with undefined)", sn is not None and "reentry" not in sn and all(v is not None or k in ("mss", "riskPct", "riskAmt", "lot", "macro", "label", "mult", "ema", "structure") for k, v in sn.items()), sn)
                check(f"{tag} no write carried an undefined field", js(page, UNDEF) == [], js(page, UNDEF))
                check(f"{tag} no page errors", not pe, pe)
            finally:
                b.close()
    # re-entry confirmed → reentry:true stored
    b, page, ce, pe = launch(pw, 1440, 900, c=LF.cards_today())
    try:
        H.sat_open(page, {"bias": "Short", "sl": 2660, "tp": 2600})
        js(page, "()=>{ window.__pc0 = pb2Calc; window.pb2Calc = (i, a)=>{ const c = window.__pc0(i, a); c.c = Object.assign({}, c.c, {re1NeedsReentry:true, re1:Object.assign({}, c.c && c.c.re1, {reentry:true})}); return c; }; pb2Render(); re1ReentryTap('hfX', true); window.__undefWrites = []; pb2PlaceYes(); }"); page.wait_for_timeout(600)
        r = js(page, RES); sn = js(page, SNAP)
        ln = js(page, "()=>{ const i = sat7dIdea('hfX'); return (i && i.ln4) || (bdById('hfX') && bdById('hfX').ln4) || {}; }")
        check("[re-entry] confirmed → recorded and `reentry:true` stored", r["st"] == "ord" and not r["line"] and (ln.get("reentry") is True or (sn or {}).get("reentry") is True), [r, ln, sn])
        check("[re-entry] no undefined field in any write", js(page, UNDEF) == [], js(page, UNDEF))
    finally:
        b.close()
    # Core place
    b, page, ce, pe = launch(pw, 1440, 900, c=L3.cards_board())
    try:
        L3.goto_plan(page, "main")
        js(page, "()=>{ window.wl1PlaceGate = ()=>true; efCorePlaceOpen('mA'); window.__undefWrites = []; }"); page.wait_for_timeout(300)
        js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(600)
        r = js(page, "()=>({open: !!document.getElementById('bdPop'), line: !!document.querySelector('[data-hf3-block]'), placed: (()=>{ const c = (coreCardsList||[]).find(x=>x.id==='mA'); return !!(c && c.ln4 && (c.ln4.placedAt || c.ln4.placedLv)); })()})")
        check("[core] place → recorded, sheet closed, no ⚠ line", r["placed"] and not r["open"] and not r["line"], r)
        check("[core] no write carried an undefined field", js(page, UNDEF) == [], js(page, UNDEF))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_sat(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY hf4: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
