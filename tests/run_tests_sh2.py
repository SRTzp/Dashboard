#!/usr/bin/env python3
"""SH2 — shared labels / industries / FX across accounts (settings.shared on home); font sizes per device.  Run: python3 tests/run_tests_sh2.py"""
import sys, json
from playwright.sync_api import sync_playwright
from re1d_common import *

def doc_sh2():
    d = doc_c(); b = d["books"]
    m, f = b["main"], b["fam"]
    m["industries"] = ["Semis", "Banks"]; f["industries"] = ["banks", "Energy"]
    m["industryLinks"] = {"Semis": "https://main.example/semis"}; f["industryLinks"] = {"Semis": "https://fam.example/semis", "Energy": "https://fam.example/energy"}
    m["scoreLabels"] = {"disc": {"3": "MAIN-3", "2": "m2", "1": "m1", "0": "m0"}}; f["scoreLabels"] = {"disc": {"3": "FAM-3", "2": "f2", "1": "f1", "0": "f0"}}
    m["scoreCriteria"] = "MAIN-CRIT"; f["scoreCriteria"] = "FAM-CRIT"
    m["reasonTags"] = {"exit": [{"id": "t1", "label": "TP", "offPlan": False}]}
    f["reasonTags"] = {"exit": [{"id": "t1", "label": "FAM-TP", "offPlan": False}, {"id": "t2", "label": "Fam only", "offPlan": True}]}
    f["exitReasons"] = [{"id": "t9", "label": "legacy", "offPlan": False}]
    m["settings"]["fx"] = 33.5; f["settings"]["fx"] = 30.1
    m["fontSizes"] = {"wl": 0.9, "plan": 0.9, "closed": 0.9}; m["tabsOffset"] = 4
    f["watchSortMode"] = {"core": "name"}
    return d

SNAP = """()=>{ const S=sh(); return JSON.stringify({ind:S.industries, links:S.industryLinks, crit:ensureScoreLabels('disc')['3'], criteria:S.scoreCriteria, exit:ensureReasonTags('exit').map(x=>x.id+':'+x.label), fx:state.settings.fx, fxShared:S.fx, fxB:{main:getBook('main').settings.fx, fam:getBook('fam').settings.fx}}); }"""

def run(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_sh2(), {})
    try:
        v = json.loads(js(page, SNAP))
        check("[%s] industries = union (Main first, case-insens.)" % tag, v["ind"] == ["Semis", "Banks", "Energy"], v["ind"])
        check("[%s] links union, Main wins on clash" % tag, v["links"].get("Semis") == "https://main.example/semis" and "Energy" in v["links"], v["links"])
        check("[%s] score label / criteria: Main wins" % tag, v["crit"] == "MAIN-3" and v["criteria"] == "MAIN-CRIT", v)
        check("[%s] reason tags union by id, Main label wins, legacy exitReasons not read when tags exist" % tag, v["exit"] == ["t1:TP", "t2:Fam only"], v["exit"])
        check("[%s] FX: Main wins, both accounts show it" % tag, v["fx"] == 33.5 and v["fxShared"] == 33.5 and v["fxB"] == {"main": 33.5, "fam": 33.5}, v)
        js(page, "()=>{ sh().industries.push('NewInd'); ensureScoreLabels('disc')['2']='EDITED'; schedulePersist(); }"); page.wait_for_timeout(800)
        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(600)
        v2 = json.loads(js(page, SNAP))
        check("[%s] switch to Family: same industries (incl. edit), labels, FX" % tag, v2["ind"] == ["Semis", "Banks", "Energy", "NewInd"] and v2["crit"] == "MAIN-3" and v2["fx"] == 33.5 and js(page, "()=>ensureScoreLabels('disc')['2']") == "EDITED", v2)
        js(page, "()=>{ ensureScoreLabels('disc')['1']='FAM-EDIT'; state.settings.fx=34.2; state.settings.fxUpdatedAt='2026-11-18T00:00:00Z'; shFxPush(); schedulePersist(); }"); page.wait_for_timeout(800)
        js(page, "()=>acctSwitch('main')"); page.wait_for_timeout(600)
        check("[%s] edits made in Family (label, FX) show on Main" % tag, js(page, "()=>ensureScoreLabels('disc')['1']") == "FAM-EDIT" and js(page, "()=>state.settings.fx") == 34.2)
        doc = js(page, "()=>window.firebase.__mockDb.__getDoc(['users','testuid'])")
        bm, bf = doc["books"]["main"], doc["books"]["fam"]
        check("[%s] stored on home settings.shared" % tag, bm["settings"]["shared"]["fx"] == 34.2 and "NewInd" in bm["settings"]["shared"]["industries"] and "shared" not in bf["settings"], [bm["settings"]["shared"].get("fx"), "NewInd" in bm["settings"]["shared"]["industries"], "shared" in bf["settings"]])
        check("[%s] old fields untouched (industries / scoreCriteria / reasonTags / exitReasons / watchSortMode / fontSizes)" % tag,
              bm["industries"] == ["Semis", "Banks"] and bf["industries"] == ["banks", "Energy"] and bf["scoreCriteria"] == "FAM-CRIT" and len(bf["reasonTags"]["exit"]) == 2 and bf["exitReasons"][0]["id"] == "t9" and bf["watchSortMode"] == {"core": "name"} and bm["fontSizes"]["wl"] == 0.9, "")
        # per device
        d1 = json.loads(js(page, "()=>localStorage.getItem('dash.devUi.v1')"))
        check("[%s] font size seeded once from Main (0.9 / offset 4)" % tag, d1["fontSizes"]["wl"] == 0.9 and d1["tabsOffset"] == 4, d1)
        js(page, "()=>{ openSystemSettings(); document.getElementById('sizeWl').value='1.3'; saveSystemSettings(); }")
        css = js(page, "()=>getComputedStyle(document.documentElement).getPropertyValue('--wlnote-size').trim()")
        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(400)
        css2 = js(page, "()=>getComputedStyle(document.documentElement).getPropertyValue('--wlnote-size').trim()")
        check("[%s] font size: this device 1.3rem, same after account switch" % tag, css == "1.3rem" and css2 == "1.3rem", [css, css2])
        saved = js(page, "()=>window.firebase.__mockDb.__getDoc(['users','testuid']).books.main.fontSizes.wl")
        check("[%s] font size not written to Firestore (still Main's old 0.9)" % tag, saved == 0.9, saved)
        check("[%s] no errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()
    # second device: its own localStorage, seeded from Main, unaffected by first device's 1.3
    b, page, ce, pe = launch(pw, w, h, doc_sh2(), {})
    try:
        wl = js(page, "()=>{ openSystemSettings(); return document.getElementById('sizeWl').value; }")
        check("[%s] other device keeps its own font size (seed 0.9, not 1.3)" % tag, wl == "0.9", wl)
    finally:
        b.close()

with sync_playwright() as pw:
    for w, h in [(1440, 900), (390, 844)]: run(pw, w, h)
bad = [r for r in results if not r[1]]
print("\nFAILED:", len(bad)) if bad else print("\nALL PASS")
sys.exit(1 if bad else 0)
