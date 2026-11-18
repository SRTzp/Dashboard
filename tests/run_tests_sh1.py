#!/usr/bin/env python3
"""SH1 — Flow data shared across accounts (settings.flowShared on the home account).  Run: python3 tests/run_tests_sh1.py"""
import os, sys, json, copy
from playwright.sync_api import sync_playwright
from re1d_common import *
import re1d_common as K

def rows_(sym, tag): return [{"sym": sym, "tag": tag, "model": "x"}]

def doc_sh1():
    d = doc_c(); b = d["books"]
    b["main"]["fundflow"] = {"ver": 5, "qe": {"mode": "QE", "date": "", "note": "MAIN-NOTE", "history": []},
        "ctx": {"rsp": -1}, "log": [{"d": "1 พ.ย.", "m": "main-log"}],
        "rrg": {"rowsD": rows_("AAA", "main-old"), "rowsW": [], "day": "2026-11-10", "at": "2026-11-10T01:00:00.000Z", "err": "", "loading": False}}
    b["fam"]["fundflow"] = {"ver": 5, "qe": {"mode": "QT", "date": "", "note": "FAM-NOTE", "history": []},
        "rrg": {"rowsD": rows_("BBB", "fam-new"), "rowsW": rows_("BBB", "fam-new-w"), "day": "2026-11-12", "at": "2026-11-12T01:00:00.000Z", "err": "", "loading": False}}
    return d

SNAP = """()=>{ const f=ffState(); return JSON.stringify({qe:f.qe.note, mode:f.qe.mode, rsp:f.ctx.rsp, log:(f.log||[]).map(x=>x.m), rrgD:(f.rrg.rowsD||[]).map(x=>x.sym), rrgW:(f.rrg.rowsW||[]).map(x=>x.sym), at:f.rrg.at, l1:f.l1.map(x=>x.r).join('|')}); }"""

def run(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_sh1(), {})
    try:
        a_main = js(page, "()=>acctActive"); 
        s1 = js(page, SNAP)
        v = json.loads(s1)
        check("[%s] migrate: Flow note/ctx/log = Main's" % tag, v["qe"] == "MAIN-NOTE" and v["rsp"] == -1 and v["log"] == ["main-log"], v)
        check("[%s] migrate: rrg = newer account's (Family BBB, 12 Nov)" % tag, v["rrgD"] == ["BBB"] and v["rrgW"] == ["BBB"] and v["at"].startswith("2026-11-12"), v)
        # manual item edit while on Main
        js(page, "()=>{ ffState().l1[0].r='MANUAL-X'; ffPersist(); }"); page.wait_for_timeout(700)
        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(600)
        check("[%s] switched to Family" % tag, js(page, "()=>acctActive") == "fam")
        s2 = js(page, SNAP)
        check("[%s] Family sees identical Flow data (strip, RRG rows, manual items)" % tag, json.loads(s2) == json.loads(js(page, SNAP)) and json.loads(s2)["l1"].startswith("MANUAL-X") and json.loads(s2)["qe"] == "MAIN-NOTE" and json.loads(s2)["rrgD"] == ["BBB"], s2)
        # edit on Family -> visible on Main
        js(page, "()=>{ ffState().qe.note='EDIT-IN-FAM'; ffTouch(); }"); page.wait_for_timeout(700)
        js(page, "()=>acctSwitch('main')"); page.wait_for_timeout(600)
        s3 = json.loads(js(page, SNAP))
        check("[%s] edit made in Family shows on Main" % tag, s3["qe"] == "EDIT-IN-FAM", s3)
        saved = js(page, "()=>{ const doc=window.firebase.__mockDb.__getDoc? window.firebase.__mockDb.__getDoc(['users','testuid']) : null; return doc ? JSON.stringify({m:doc.books.main.settings.flowShared && doc.books.main.settings.flowShared.qe.note, oldM:doc.books.main.fundflow.qe.note, oldF:doc.books.fam.fundflow.qe.note, famShared: !!(doc.books.fam.settings||{}).flowShared}) : null; }")
        print("INFO saved:", saved)
        if saved:
            sv = json.loads(saved)
            check("[%s] stored once on home; old state.fundflow untouched (MAIN-NOTE / FAM-NOTE)" % tag, sv["m"] == "EDIT-IN-FAM" and sv["oldM"] == "MAIN-NOTE" and sv["oldF"] == "FAM-NOTE" and not sv["famShared"], sv)
        check("[%s] no errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()

with sync_playwright() as pw:
    for w, h in [(1440, 900), (390, 844)]: run(pw, w, h)
bad = [r for r in results if not r[0]] if results and isinstance(results[0], tuple) else []
print("\nFAILED:", len(bad)) if bad else print("\nALL PASS")
sys.exit(1 if bad else 0)
