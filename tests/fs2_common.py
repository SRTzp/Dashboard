#!/usr/bin/env python3
"""FS2 — shared: the HW1 fixture with COST (Compounder) / AAPL (Momentum) carrying the FS2 facts (q.ends · ask · business[])."""
import os, json, copy
import hw1_common as H
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
fx = lambda n: json.load(open(os.path.join(HERE, "fixtures", "fs2", n + ".json")))
COMP, MOM = fx("compounder")["facts"], fx("momentum")["facts"]
OLD_COMP, OLD_MOM = H.COMP, H.MOM          # LT2 facts: no business / ends / ask (must still render)
for _r in COMP["q"]["rows"]:
    if _r["k"] == "kpi_renewal": _r["v"] = [93.0, 92.9, 92.7, 92.5]


def open_fs2(pw, w, h):
    b, page, pe = H.open_hw(pw, w, h)
    setf(page, "COST", COMP); setf(page, "AAPL", MOM)
    return b, page, pe


def setf(page, sym, facts, mode=None, track=None):
    """Replace the Fact Sheet of one stock (and optionally its thesis mode) in the live item; the caller re-opens the page."""
    js(page, "([s,f,m])=>{ const it = wlItemOf(s); it.thesis.facts = f; if(m) it.thesis.mode = m; }", [sym, copy.deepcopy(facts), mode])


def go(page, sym, trk=None, tab=None):
    H.go(page, sym, trk)
    if tab: js(page, "(t)=>hw1SegSet(hwSym,t)", tab); page.wait_for_timeout(150)
