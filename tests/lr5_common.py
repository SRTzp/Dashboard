#!/usr/bin/env python3
"""LR5a — shared Watch fixture: Momentum AAPL (Holding · hw not started · RS 87 ↗ new high) · AVGO (Plan ready · hw done · RS 64 ↗) · GE (No plan · hw done · RS 91 → ) · PLTR (No plan · hw not started · no RS data)
 · AMD (Setup ✓ · rating null 'history<252') + Compounder COST + archived ARX / ARY + two ideas. RRG rows for XLK (lagging 12d) / SMH (improving) / XLI (leading) / IGV (lagging)."""
import os, json
import net_stub
import re1d_common as K
from re1d_common import js, launch

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr")
CLK = "2026-11-19T12:00:00+07:00"

WL_JS = """([rows, px])=>{
  const col = wlCol();
  rows.forEach(x=>col.doc(x.t).set(Object.assign({ticker:x.t, market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'}, x.x || {})));
  window.__lr5px = px;
}"""

HW_DONE = lambda d: {"hw": {"trigger": "Break of the 4-week base", "confirmedAt": d + "T03:00:00Z", "doneAt": d + "T03:00:00Z"}, "my_thesis": {}}


_EN = {}


def en(o):
    """Same structure with every Thai string replaced by a consistent English token (references between strings stay valid)."""
    import re
    th = re.compile(r"[\u0E00-\u0E7F]")
    if isinstance(o, dict): return {k: en(v) for k, v in o.items()}
    if isinstance(o, list): return [en(v) for v in o]
    if isinstance(o, str) and th.search(o):
        if o not in _EN: _EN[o] = "Sample text %d" % (len(_EN) + 1)
        return _EN[o]
    return o


def thesis_fields(sym="AVGO"):
    """English-data living-thesis (from the WL2 fixture) as watchlist doc fields."""
    import lib_phase40 as P40
    th = en(P40.fx(sym)); t = {k: v for k, v in th.items() if k != "log"}
    return {"thesis": t, "thesis_log": th.get("log", []), "thesis_history": [], "thesis_hits": {}}


def idea_doc(iid="en-idea-1", name="Memory chips stay tight"):
    import lib_phase44 as P44, copy
    d = en(copy.deepcopy(P44.SEMIS)); d["id"] = iid; d["name"] = name; d["status"] = "need_evidence"; d["candidates"] = []; d["scope"] = ["US"]
    return d


def items():
    r = []
    r.append({"t": "AAPL", "x": {"exch": "NASDAQ", "sector_etf": "XLK"}})
    r.append({"t": "AVGO", "x": {"exch": "NASDAQ", "sector_etf": "SMH", "next_check_date": "2026-12-02", **HW_DONE("2026-11-12"), "my_thesis": {"why": "AI networking share", "exit": "Hyperscaler capex cut"}, **thesis_fields("AVGO")}})
    r.append({"t": "GE", "x": {"exch": "NYSE", "sector_etf": "XLI", "next_check_date": "2026-11-28", **HW_DONE("2026-11-08"), "my_thesis": {"why": "aero cycle", "exit": "Backlog falls"}}})
    r.append({"t": "PLTR", "x": {"exch": "NASDAQ", "sector_etf": "IGV"}})
    r.append({"t": "AMD", "x": {"exch": "NASDAQ", "sector_etf": "XLK"}})
    r.append({"t": "COST", "x": {"exch": "NASDAQ", "ladder_watch": True, "ladder_watch_set": True}})
    r.append({"t": "ARX", "x": {"archived": True, "archived_reason": "thesis broke after earnings", "archived_at": "2026-11-10T00:00:00Z"}})
    r.append({"t": "ARY", "x": {"archived": True, "archived_reason": "too slow", "archived_at": "2026-11-12T00:00:00Z"}})
    return r


RS = {
    "AAPL": {"rating": 87, "rating4wAgo": 72, "line": "up", "newHigh": True, "newHigh5d": True, "bench": "SPY", "asOf": "2026-11-18"},
    "AVGO": {"rating": 64, "rating4wAgo": 70, "line": "down", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18"},
    "GE": {"rating": 91, "rating4wAgo": 90, "line": "flat", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18"},
    "AMD": {"rating": None, "rating4wAgo": None, "line": "flat", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18", "reason": "history<252"},
}

SECT = {}   # WL2 — optional {ySym: {sector, industry}} on the price docs

FIX_JS = """([px])=>{
  const mk = (sym, quad, days)=>Object.assign({model:RRG_MODEL}, {sym, name:sym, quad, ratio:100, mom:100, dMom:0.1, days, prevDays:3, err:null, tailF:[100, 100]});
  const rows = [mk('XLK', 'lag', 12), mk('SMH', 'imp', 4), mk('XLI', 'lead', 11), mk('IGV', 'lag', 10)];
  const f = ffState(); f.rrg = {rowsD: rows, rowsW: rows, build:RRG_BUILD, model:RRG_MODEL, lastBar:rrgToday(), day:rrgToday()};
  try{ getBook('main').trades.push({id:'tAAPL', sym:'AAPL', port:'core', status:'open', dir:'long', entry:100, qty:10, sl:90, date:'2026-10-20', acct:'main'}); }catch(e){ console.warn(e); }
  serverConfirmed = true; stateFromServer = true;
  try{ glWrite(S=>{ S.tvSetup = Object.assign({}, S.tvSetup||{}, {AMD: thaiToday()}); }); }catch(e){ console.warn(e); }
  switchTab('watch'); wlSetView('wl'); renderWatchlist();
}"""


def seed(page, with_ideas=False):
    if with_ideas:
        for i, nm in enumerate(("Memory chips stay tight", "Grid power demand")):
            d = idea_doc("en-idea-%d" % (i + 1), nm)
            page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", [d["id"], {"idea": {k: v for k, v in d.items() if k != "log"}, "idea_log": d.get("log", []), "user": {}}])
        page.wait_for_timeout(500)
    rows = items()
    px = {k: {"rs": v, "close": 100.0, "closeDate": "2026-11-18", **SECT.get(k, {})} for k, v in RS.items()}
    js(page, WL_JS, [rows, px])
    px["PLTR"] = {"name": "watchlist-only ticker: no close, no rs"}   # a price doc without close (must not break the listener or show a 0 price)
    for k, v in px.items():
        page.evaluate("([k,v])=>window.firebase.__mockDb.__seedDoc(['users','testuid','prices',k], v)", [k, v])
    page.wait_for_timeout(500)
    js(page, FIX_JS, [px])
    page.wait_for_timeout(300)


def open_watch(pw, w, h, ideas=False, plan_cards=True, iso=CLK):
    import lib_phase39 as P39, re1c_common as R1
    cards = {}
    if plan_cards:
        cards = {"avgo": K.plan_card("AVGO", 100, 90, px=99, ready=True),
                 "aapl": K.plan_card("AAPL", 100, 90, px=105, status="open", trade_id="tAAPL", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 10, "f": 1, "stop": 90}])}
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=R1.doc_c(), cards=cards, clean=True, iso=iso)
    page.add_style_tag(content=K.NOANIM); page.wait_for_timeout(400)
    seed(page, ideas)
    return b, page, pe
