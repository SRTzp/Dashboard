#!/usr/bin/env python3
"""WL2 — Watch fixture with the new RS fields (hi52 · offHigh · r3m..r12m) on top of the LR5a one.
AAPL 87 ↗ new high · AVGO 64 ↘ −28% (amber) · GE 91 → −6% (muted) · RELY 63 ↘ −21% (ink) · MU 98 ↘ −42% (amber, living thesis, homework not done)
· GLBE 54 ↘ −31% (no exchange → 'Exch?') · TEAM 76 (OLD price doc: no new fields) · PLTR no RS doc · AMD rating null."""
import lr5_common as C

C.RS.update({
    "AAPL": {**C.RS["AAPL"], "hi52": 270.5, "hi52Date": "2026-11-18", "offHigh": 0.0, "r3m": 0.12, "r6m": 0.2, "r9m": 0.3, "r12m": 0.4},
    "AVGO": {**C.RS["AVGO"], "hi52": 400.0, "hi52Date": "2026-07-02", "offHigh": -0.28, "r3m": -0.1, "r6m": 0.05, "r9m": 0.2, "r12m": 0.3},
    "GE": {**C.RS["GE"], "hi52": 330.0, "hi52Date": "2026-10-01", "offHigh": -0.06, "r3m": 0.02, "r6m": 0.1, "r9m": 0.2, "r12m": 0.25},
    "RELY": {"rating": 63, "rating4wAgo": 60, "line": "down", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18", "hi52": 100.0, "hi52Date": "2026-03-02", "offHigh": -0.21, "r3m": -0.05, "r6m": -0.1, "r9m": 0.0, "r12m": 0.1},
    "MU": {"rating": 98, "rating4wAgo": 99, "line": "down", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18", "hi52": 1255.0, "hi52Date": "2026-06-18", "offHigh": -0.42, "r3m": -0.07, "r6m": 0.5, "r9m": 0.85, "r12m": 2.0},
    "GLBE": {"rating": 54, "rating4wAgo": 58, "line": "down", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18", "hi52": 60.0, "hi52Date": "2026-05-01", "offHigh": -0.31, "r3m": -0.2, "r6m": -0.1, "r9m": 0.0, "r12m": 0.1},
    "TEAM": {"rating": 76, "rating4wAgo": 70, "line": "down", "newHigh": False, "newHigh5d": False, "bench": "SPY", "asOf": "2026-11-18"},
})
C.SECT.update({"GLBE": {"sector": "Technology", "industry": "Software - Infrastructure"}, "MU": {"sector": "Consumer Cyclical", "industry": "Auto Parts"}})
_items = C.items


def items():
    r = _items()
    r.append({"t": "MU", "x": {"exch": "NASDAQ", "sector_etf": "SMH", **C.thesis_fields("AVGO")}})
    r.append({"t": "GLBE", "x": {}})
    r.append({"t": "RELY", "x": {"exch": "NYSE", "sector_etf": "XLF"}})
    r.append({"t": "NVDA", "x": {"exch": "NASDAQ", "sector_etf": "SMH", "my_thesis": {"why": "", "exit": "My own exit"}, **C.thesis_fields("AVGO")}})
    r.append({"t": "TEAM", "x": {"exch": "NASDAQ", "sector_etf": "IGV"}})
    return r


C.items = items
open_watch = C.open_watch
