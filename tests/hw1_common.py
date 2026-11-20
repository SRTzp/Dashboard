#!/usr/bin/env python3
"""HW1 — shared fixture: the LR5 Watch fixture + COST (Compounder, living thesis + compounder Fact Sheet), AAPL gets a momentum Fact Sheet,
WHSE (Compounder, no thesis, nothing written), SRC1 (Momentum, from Screen), ZZ (Compounder, 2 of 3 filled)."""
import os, json, copy
import lr5_common as C
from re1d_common import js

H = os.path.dirname(os.path.abspath(__file__))
fx = lambda n: json.load(open(os.path.join(H, "fixtures", "lt2", n + ".json")))
COMP, MOM = fx("compounder")["facts"], fx("momentum")["facts"]
for _r in COMP["q"]["rows"]:
    if _r["k"] == "kpi_renewal": _r["v"] = [93.0, 92.9, 92.7, 92.5]   # a full 4-quarter slide -> "slipping"


def tok(th):
    sm = th["thesis"]["summary"]; sm["thesis"] = ["ZQTHESIS0 AI networking share keeps growing", "ZQTHESIS1 second"]; sm["next"] = "ZQNEXT Q4 results vs guide"; sm["breaker"] = "ZQBREAKER Q4 AI revenue below guide"
    return th


def extra_items():
    th = tok(C.thesis_fields("AVGO"))
    cost = copy.deepcopy(th); cost["thesis"]["facts"] = COMP
    aapl = copy.deepcopy(th); aapl["thesis"]["facts"] = MOM
    return [
        ("COST", {"ladder_watch": True, "ladder_watch_set": True, "exch": "NASDAQ", "sector_etf": "XLK", **cost}),
        ("AAPL", {"exch": "NASDAQ", "sector_etf": "XLK", **aapl}),
        ("WHSE", {"ladder_watch": True, "ladder_watch_set": True, "exch": "NYSE"}),
        ("SRC1", {"exch": "NASDAQ", "src": {"from": "screen", "preset": "leaders", "r12": 95, "r3": 92, "r1": 88, "at": "2026-11-20T03:00:00Z"}}),
        ("ZZ", {"ladder_watch": True, "ladder_watch_set": True, "exch": "NYSE", "my_thesis": {"why": "They raise fees", "evidence": "Fee revenue is large"}}),
    ]


def open_hw(pw, w, h):
    b, page, pe = C.open_watch(pw, w, h, ideas=False)
    for t, x in extra_items():
        js(page, "([t,x])=>wlCol().doc(t).set(Object.assign({ticker:t, market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'}, x))", [t, x])
    page.wait_for_timeout(500)
    return b, page, pe


def go(page, sym, trk=None):
    js(page, "([s,t])=>{ if(t){ wl1Trk = t; } wlSetView('wl'); hwOpen(s); }", [sym, trk]); page.wait_for_timeout(350)


def fill(page, k, v):
    if not js(page, "(k)=>{ const e = document.querySelector('[data-hw1-ta=\"'+k+'\"]'); return !!e && e.getBoundingClientRect().width > 0; }", k): js(page, "()=>hw1SegSet(hwSym,'mine')")
    page.fill('[data-hw1-ta="%s"]' % k, v); page.wait_for_timeout(120)
