#!/usr/bin/env python3
"""RS2a — shared Screen fixture: 130 ranked rows (the 8 mockup rows first: NVDA ZETA PLTR APP CRDO HOOD GE RKLB) + fillers so the default view
(RS ≥ 80 · within 15% of the high) matches 86 stocks. Watch holds NVDA (next check in 6 days), ZETA, GE → 'Watching ✓'."""
import json
import net_stub
import re1d_common as K
from re1d_common import js

CLK = "2026-11-19T12:00:00+07:00"
ASOF = "2026-11-18"


def row(t, n, s, i, e, r, p, l, h, o, c, v, hi=None):
    return {"t": t, "n": n, "e": e, "s": s, "i": i, "r": r, "p": p, "l": l, "h": h, "o": o, "x": hi or round(c / (1 + o), 2), "xd": "2026-11-03", "c": c, "v": v,
            "a3": 0.22, "a6": 0.48, "a9": 0.71, "a12": 1.6}


MOCK = [
    row("NVDA", "NVIDIA", "Technology", "Semiconductors", "NASDAQ", 99, 96, "u", 2, 0.0, 182.40, 38.1e9),
    row("ZETA", "Zeta Global", "Technology", "Software - Application", "NYSE", 99, 93, "u", 0, -0.14, 24.80, 190e6),
    row("PLTR", "Palantir", "Technology", "Software - Infrastructure", "NASDAQ", 97, 95, "u", 0, -0.08, 168.10, 5.2e9, 182.6),
    row("APP", "AppLovin", "Technology", "Software - Application", "NASDAQ", 96, 97, "u", 0, -0.11, 612.30, 3.1e9),
    row("CRDO", "Credo Technology", "Technology", "Semiconductors", "NASDAQ", 95, 86, "u", 2, 0.0, 141.20, 620e6),
    row("HOOD", "Robinhood", "Financial Services", "Capital Markets", "NASDAQ", 94, 97, "f", 0, -0.12, 128.50, 2.4e9),
    row("GE", "GE Aerospace", "Industrials", "Aerospace & Defense", "NYSE", 91, 91, "f", 0, -0.06, 296.70, 1.1e9),
    row("RKLB", "Rocket Lab", "Industrials", "Aerospace & Defense", "NASDAQ", 90, 79, "u", 0, -0.09, 56.40, 980e6),
]


def rows():
    out = [dict(m) for m in MOCK]
    sect = [("Technology", "Software - Application"), ("Healthcare", "Biotechnology"), ("Industrials", "Engineering & Construction"), ("Financial Services", "Banks - Regional"), ("Energy", "Oil & Gas E&P")]
    for k in range(78):    # fillers that match the default view: RS 80-89, 0..−14% from the high
        s, i = sect[k % 5]
        out.append(row("F%03d" % k, "Filler Co %d" % k, s, i, "NYSE", 89 - k % 10, 80 + k % 5, "u" if k % 3 else "f", 0, -(k % 15) / 100.0, 20 + k, (20 + k % 50) * 1e6))
    for k in range(20):    # RS ≥ 80 but beyond −15% (hidden by default)
        out.append(row("W%03d" % k, "Wide Co %d" % k, "Technology", "Software - Application", "NASDAQ", 85 - k % 5, 80, "d", 0, -0.2 - k / 100.0, 40 + k, 90e6))
    for k in range(24):    # RS < 80
        out.append(row("L%03d" % k, "Low Co %d" % k, "Utilities", "Utilities - Regulated Electric", "NYSE", 60 - k, 55, "d", 0, -0.05, 30 + k, 60e6))
    return out


def meta(n=1943):
    return {"asOf": ASOF, "n": n, "nRated": 130, "runAt": ASOF + "T22:40:00Z", "error": None}


SEED_JS = """([rows, meta, wl, parts])=>{
  const db = window.firebase.__mockDb;
  if(parts){ const hdr = {asOf:meta.asOf, n:rows.length, parts:parts.length}; db.__seedDoc(['users','testuid','rs2','latest'], hdr); parts.forEach((p, i)=>db.__seedDoc(['users','testuid','rs2','latest_'+i], {asOf:meta.asOf, i, rows:p})); }
  else db.__seedDoc(['users','testuid','rs2','latest'], {asOf:meta.asOf, n:rows.length, rows});
  if(meta) db.__seedDoc(['users','testuid','rs2','_meta'], meta);
  const col = wlCol();
  wl.forEach(x=>col.doc(x.t).set(Object.assign({ticker:x.t, market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'}, x.x || {})));
}"""

WL = [{"t": "NVDA", "x": {"exch": "NASDAQ", "next_check_date": "2026-11-25"}}, {"t": "ZETA", "x": {"exch": "NYSE", "next_check_date": "2026-02-04"}},
      {"t": "GE", "x": {"exch": "NYSE", "next_check_date": "2026-01-21"}}, {"t": "COST", "x": {"exch": "NASDAQ", "ladder_watch": True, "ladder_watch_set": True}}]


def open_screen(pw, w, h, data=None, meta_=None, wl=None, parts=None, seed=True, go=True):
    import lib_phase39 as P39, re1c_common as R1
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=R1.doc_c(), cards={}, clean=True, iso=CLK)
    page.add_style_tag(content=K.NOANIM); page.wait_for_timeout(400)
    if seed:
        js(page, SEED_JS, [data if data is not None else rows(), meta_ if meta_ is not None else meta(), wl if wl is not None else WL, parts])
        page.wait_for_timeout(400)
    if go:
        js(page, "()=>{ switchTab('watch'); wlSetView('screen'); }"); page.wait_for_timeout(700)
    return b, page, pe, ce
