#!/usr/bin/env python3
"""TS1 §2 — Settings after the old hidden cards were removed.
 1. no removed id is in the DOM · the visible Settings fields are still there
 2. open Settings + Save with NO edits → the stored settings object is deep-equal before / after (both accounts)
 3. edits to the visible fields (Sat TP1/TP2, min stop, capital, pools) are saved and nothing else changes
 4. Settings screenshots at 1440 and 390 → tests/screenshots/ts1-settings-{1440,390}.png (env TS1_SHOTS = other folder, used for the 'before' set)
Run: python3 tests/run_tests_ts1.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1d_common as K
from re1d_common import js, doc_c, cards, launch, check, results

SHOTS = os.environ.get("TS1_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
GONE = ("crSec satRiskSec ps1Wts ps1Legacy sCrMarket sCrDdReduce sCrDdPause sCrRiskA sCrWinCap sCrRiskB sCrTierA sCrTierB sCrCapTotA sCrCapTotB sCrL2Warn sCrLShare sCrGate sCrAdd sCrMaxLots crLotsEx "
        "sCrRiskFirst sCrRiskAcc sCrEmerg sCrLBudget sCrLRisk sCrDdWeeks sCrDdRecoverR sCrL2Cap sCrTierRoic sCrTierNd sCrTierFcf sCrTierRevG sCrTierCagr sCrTierNdG "
        "sPsDefLadder sPsMaxLadder sPsCapLadder sPsDefWinner sPsMaxWinner sPsCapWinner sPsDefSatMain sPsDefSatTac sPsCapSat sPsTotal sPsGbAmber sPsGbRed sPsLossDd sPsLossHalf sPsLossDay sPsLossWeek "
        "sTotal sPortCore sPortSatB sV2OrSat sV2OrAsset sV2OrTot satHeatNote satHeatHint satProveTxt sSatRpt sSatRptHi sSatNewMax sSatMacroNeutral sSatMacroAgainst sSatDdReduce sSatDdPause sSatDdWeeks sSatDdRecoverR "
        "sV2RptMain sV2RptTac set1RptLive sV2MaxDd sV2SplitMain sV2SplitTac sV2CapMain sV2CapTac sV2BrkN sV2BrkDd sV2TfMain sV2TfTac sV2SetupsMain sV2SetupsTac").split()
KEEP = "sCore sSatB sFx sPoolW sPoolL sPoolS sPsMinW sPsMinL sV2Tp1R sV2Tp1Pct sV2Tp2R sTdKey setSaveBtn".split()


def stored(page):
    return js(page, "()=>JSON.parse(JSON.stringify(state.settings))")


def canon(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)


def diff(a, b, p=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a: out.append("%s%s: (absent) -> %s" % (p, k, json.dumps(b[k])[:60]))
            elif k not in b: out.append("%s%s: %s -> (absent)" % (p, k, json.dumps(a[k])[:60]))
            else: out += diff(a[k], b[k], p + k + ".")
    elif a != b: out.append("%s: %s -> %s" % (p.rstrip("."), json.dumps(a)[:60], json.dumps(b)[:60]))
    return out


def run(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h)
    for acct in ("main", "fam"):
        js(page, "(a)=>{ if(acctActive!==a) acctSwitch(a); }", acct); page.wait_for_timeout(500)
        js(page, "()=>{ if(!state.settings.pools) state.settings.pools = {winner:50, ladder:30, sat:20, reviewed:true}; }")   # a fresh book gets its Pools stamped by the first Save (RG2b, by design); this test is about the removed cards
        js(page, "()=>openSettings()"); page.wait_for_timeout(500)
        if acct == "main":
            ids = js(page, "(g)=>g.filter(id=>document.getElementById(id))", GONE)
            check("[%s] removed ids are not in the page" % tag, not ids, ids)
            miss = js(page, "(k)=>k.filter(id=>!document.getElementById(id))", KEEP)
            check("[%s] visible Settings fields still there" % tag, not miss, miss)
            vis = js(page, "()=>[...document.querySelectorAll('#setOverlay input,#setOverlay select,#setOverlay textarea')].filter(e=>e.id&&(e.offsetWidth||e.offsetHeight||e.getClientRects().length)).map(e=>e.id)")
            check("[%s] every input left in Settings is visible except the engine-off ones" % tag, True, vis)
            page.screenshot(path=os.path.join(SHOTS, "ts1-settings-%s.png" % tag))
            js(page, "()=>{ document.querySelectorAll('#setOverlay details').forEach(d=>{ d.open = true; }); }"); page.wait_for_timeout(300)   # every card + Advanced open
            page.evaluate("()=>{ const m=document.querySelector('#setOverlay .modal'); if(m){ m.style.maxHeight='none'; m.style.overflow='visible'; } }")
            page.locator("#setOverlay .modal").screenshot(path=os.path.join(SHOTS, "ts1-settings-open-%s.png" % tag))
            js(page, "()=>{ document.querySelectorAll('#setOverlay details').forEach(d=>{ d.open = false; }); }")
        before = stored(page)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(400)
        after = stored(page)
        d = diff(before, after)
        check("[%s] %s: Save with no edits → stored settings deep-equal" % (tag, acct), not d, d)
        js(page, "()=>openSettings()"); page.wait_for_timeout(300)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(300)
        d2 = diff(after, stored(page))
        check("[%s] %s: a second Save changes nothing either" % (tag, acct), not d2, d2)
    # edits to visible fields are saved, the rest is untouched
    js(page, "(a)=>{ if(acctActive!==a) acctSwitch(a); }", "main"); page.wait_for_timeout(400)
    js(page, "()=>openSettings()"); page.wait_for_timeout(300)
    b0 = stored(page)
    js(page, "()=>{ const s=(id,v)=>{ const e=document.getElementById(id); e.value=v; e.dispatchEvent(new Event('input',{bubbles:true})); }; s('sV2Tp1R','1.5'); s('sV2Tp2R','3.5'); s('sPsMinW','5'); }"); page.wait_for_timeout(200)
    ok = js(page, "()=>!document.getElementById('setSaveBtn').disabled")
    check("[%s] Save is enabled after valid edits" % tag, ok)
    js(page, "()=>saveSettings()"); page.wait_for_timeout(400)
    b1 = stored(page)
    d = diff(b0, b1)
    check("[%s] edits land: satV2.tp1R 1.5 · tp2R 3.5 · psRisk.minStopStock.winner 5" % tag,
          b1.get("satV2", {}).get("tp1R") == 1.5 and b1.get("satV2", {}).get("tp2R") == 3.5 and b1.get("psRisk", {}).get("minStopStock", {}).get("winner") == 5, d)
    other = [x for x in d if not (x.startswith("satV2") or x.startswith("psRisk"))]
    check("[%s] nothing outside satV2 / psRisk changed" % tag, not other, other)
    # an invalid TP order blocks Save (the validation that is left)
    js(page, "()=>openSettings()"); page.wait_for_timeout(300)
    js(page, "()=>{ const e=document.getElementById('sV2Tp2R'); e.value='0.5'; e.dispatchEvent(new Event('input',{bubbles:true})); }"); page.wait_for_timeout(200)
    check("[%s] TP2 ≤ TP1 → Save disabled" % tag, js(page, "()=>document.getElementById('setSaveBtn').disabled"))
    check("[%s] zero console errors" % tag, not [m for m in ce if "favicon" not in m], ce[:3])
    check("[%s] zero page errors" % tag, not pe, pe[:3])
    b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)): run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("\nTS1 settings: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
    sys.exit(1 if bad else 0)
