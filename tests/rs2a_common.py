#!/usr/bin/env python3
"""RS2a — shared Screen fixture: 130 ranked rows (the 8 mockup rows first: NVDA ZETA PLTR APP CRDO HOOD GE RKLB) + fillers so the default view
(RS ≥ 80 · within 15% of the high) matches 86 stocks. Watch holds NVDA (next check in 6 days), ZETA, GE → 'Watching ✓'."""
import json
import net_stub
import re1d_common as K
from re1d_common import js

CLK = "2026-11-19T12:00:00+07:00"
ASOF = "2026-11-18"


def row(t, n, s, i, e, r, p, l, h, o, c, v, hi=None, m3=None, m1=None, nx=None, mc=None):
    d = {"t": t, "n": n, "e": e, "s": s, "i": i, "r": r, "p": p, "l": l, "h": h, "o": o, "x": hi or round(c / (1 + o), 2), "xd": "2026-11-03", "c": c, "v": v,
            "a3": 0.22, "a6": 0.48, "a9": 0.71, "a12": 1.6, "m3": r - 3 if m3 is None else m3, "m1": r - 9 if m1 is None else m1}
    if nx: d["nx"] = nx
    if mc: d["mc"] = mc
    return d


MOCK = [
    row("NVDA", "NVIDIA", "Technology", "Semiconductors", "NASDAQ", 99, 96, "u", 2, 0.0, 182.40, 38.1e9, nx="2026-11-25", mc=4.4e12),
    row("ZETA", "Zeta Global", "Technology", "Software - Application", "NYSE", 99, 93, "u", 0, -0.14, 24.80, 190e6, mc=860e6),
    row("PLTR", "Palantir", "Technology", "Software - Infrastructure", "NASDAQ", 97, 95, "u", 0, -0.08, 168.10, 5.2e9, 182.6, m3=94, m1=88, nx="2026-12-02", mc=390e9),
    row("APP", "AppLovin", "Technology", "Software - Application", "NASDAQ", 96, 97, "u", 0, -0.11, 612.30, 3.1e9, mc=205e9),
    row("CRDO", "Credo Technology", "Technology", "Semiconductors", "NASDAQ", 95, 86, "u", 2, 0.0, 141.20, 620e6, mc=25.3e9),
    row("HOOD", "Robinhood", "Financial Services", "Capital Markets", "NASDAQ", 94, 97, "f", 0, -0.12, 128.50, 2.4e9, mc=110e9),
    row("GE", "GE Aerospace", "Industrials", "Aerospace & Defense", "NYSE", 91, 91, "f", 0, -0.06, 296.70, 1.1e9, mc=315e9),
    row("RKLB", "Rocket Lab", "Industrials", "Aerospace & Defense", "NASDAQ", 90, 79, "u", 0, -0.09, 56.40, 980e6, mc=28.6e9),
]


def rows():
    out = [dict(m) for m in MOCK]
    sect = [("Technology", "Software - Application"), ("Healthcare", "Biotechnology"), ("Industrials", "Engineering & Construction"), ("Financial Services", "Banks - Regional"), ("Energy", "Oil & Gas E&P")]
    for k in range(72):    # fillers that match the default view: RS 80-89, 0..−14% from the high
        s, i = sect[k % 5]
        out.append(row("F%03d" % k, "Filler Co %d" % k, s, i, "NYSE", 89 - k % 10, 80 + k % 5, "u" if k % 3 else "f", 0, -(k % 15) / 100.0, 20 + k, (20 + k % 50) * 1e6, mc=None if k % 4 == 0 else (1 + k) * 25e7))
    for k in range(6):     # Pullback: 12M ≥ 85 · 3M ≥ 80 · 1M < 60 · within 15% (and Leaders too — RS ≥ 80 and near) — kept out of Leaders by the 72 fillers above (86 in total)
        out.append(row("PB%d" % k, "Pullback Co %d" % k, "Technology", "Software - Application", "NASDAQ", 90 - k, 85, "u", 0, -0.1, 50 + k, 80e6, m3=82 + k, m1=40 + k))
    for k in range(10):    # Emerging: 3M ≥ 90 · 1M ≥ 90 · 12M < 85 (far from the high so they are not Leaders)
        out.append(row("EM%d" % k, "Emerging Co %d" % k, "Healthcare", "Biotechnology", "NASDAQ", 60 + k * 2, 40, "u", 0, -0.3, 15 + k, 40e6, m3=90 + k % 9, m1=91 + k % 8, nx="2026-11-22" if k == 0 else None))
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

WL = [{"t": "NVDA", "x": {"exch": "NASDAQ", "next_check_date": "2026-11-25"}}, {"t": "ZETA", "x": {"exch": "NYSE", "next_check_date": "2027-02-04"}},
      {"t": "GE", "x": {"exch": "NYSE", "next_check_date": "2027-01-21"}}, {"t": "COST", "x": {"exch": "NASDAQ", "ladder_watch": True, "ladder_watch_set": True}}]


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
