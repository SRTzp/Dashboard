#!/usr/bin/env python3
"""BUGHUNT item 4 — idea@1 / living-thesis@1 importers reject wrong-typed fields with a clear error (pure parsers, fixtures only)."""
import os, sys, json
import re
from playwright.sync_api import sync_playwright
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
import run_tests_phase38 as P38, run_tests_phase39 as P39
fx = lambda n: json.load(open(os.path.join(H, "fixtures", n)))
idea, lt = fx("idea_semis.json"), fx("avgo_thesis.json")
CASES = [("ideaParse", idea, k, v, True) for k, v in [("id", 12345), ("name", {"a": 1}), ("name", [1, 2]), ("date", 5), ("mode", None), ("gaps", "x"), ("candidates", {}), ("candidates", [None]), ("kill", [5]), ("user_notes", []), ("chain", None)]]
CASES += [("ideaParse", {**idea, "candidates": [{"sym": 5}]}, None, None, False)]
CASES += [("ltParse", lt, k, v, True) for k, v in [("sym", 5), ("sym", {}), ("name", None), ("market", 1), ("kpi", "x"), ("log", ["x"]), ("summary", []), ("tier_inputs", "x")]]
CASES += [("ltParse", {**lt, "summary": {**lt["summary"], "status": None}}, None, None, False), ("ltParse", {**lt, "summary": {**lt["summary"], "thesis": "x"}}, None, None, False)]
fails = 0
with sync_playwright() as p:
    b, ctx, pg, ce, pe, dlg = P39.launch(p, 1024, 800, doc=P38.doc38(clean=False), clean=False, extra=None)
    pg.route(re.compile(r"^https?://"), lambda r: r.fallback() if re.search(r"gstatic\.com/firebasejs", r.request.url) else r.abort())
    for fn, base, k, v, swap in CASES:
        doc = {**base, k: v} if swap else base
        r = pg.evaluate("([f,t])=>{const r=window[f](t,null); return {err:r.err||null, ok:!r.err}}", [fn, json.dumps(doc)])
        ok = (not r["ok"]) and r["err"] and "ไม่บันทึก" in r["err"]
        fails += 0 if ok else 1; print(("PASS" if ok else "FAIL"), fn, k, json.dumps(v)[:30], "->", (r["err"] or "ACCEPTED")[:90])
    for fn, base in (("ideaParse", idea), ("ltParse", lt)):
        r = pg.evaluate("([f,t])=>{const r=window[f](t,null); return {err:r.err||null}}", [fn, json.dumps(base)])
        ok = r["err"] is None; fails += 0 if ok else 1; print(("PASS" if ok else "FAIL"), fn, "valid fixture still accepted", r["err"])
    b.close()
print("FAILS", fails); sys.exit(1 if fails else 0)
