#!/usr/bin/env python3
"""LR5b — shared fixture for the Journal tab: two accounts (main = Main · fam = Family), clock Wed 19 Nov 2025.
Closed trades (hand-checkable) — see EXPECT. Not-taken: 3 hesitated · 1 missed · 1 invalidated (+ 1 'thesis' = other) in November."""
import os, json
import net_stub
import re1d_common as K
import re1c_common as R1
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr")
CLK25 = "2025-11-19T12:00:00+07:00"


def T(**o):
    return R1.tr(**o)


def closed_main():
    return [
        # XAU · Sat · USD · gap through the stop: planned stop 2628 (1R = 14 × 0.21 × 100 = 294) · exit 2623.81 → −381.99 = −1.30R · no reason yet
        T(id="x1", sym="XAUUSD", port="satB", cur="USD", qty=0.21, mult=100, entry=2642, sl=2628, sl0=2628, tp=2684, status="closed", exitPrice=2623.81, date="2025-11-14", exitDate="2025-11-17", posGroup="x1"),
        # NVDA · Momentum · USD · early exit (+200 / risk 500 = +0.4R) · reviewed Discretionary
        T(id="n1", sym="NVDA", port="core", cur="USD", qty=100, entry=100, sl=95, sl0=95, tp=115, status="closed", exitPrice=102, date="2025-11-05", exitDate="2025-11-13", exitReason="early", posGroup="n1",
          review={"why": "disc", "lesson": "Sold on fear before CPI", "at": "2025-11-13T10:00:00Z"}),
        # BTC · Sat · USD · stop: −297 / risk 297 = −1.0R · reason from the existing exit tag 'sl'
        T(id="b1", sym="BTCUSD", port="satB", cur="USD", qty=3, mult=1, entry=1000, sl=901, sl0=901, status="closed", exitPrice=901, date="2025-11-10", exitDate="2025-11-12", exitReason="sl", posGroup="b1"),
        # moved-stop case: planned stop 90 (risk 100), stop later moved to 98, exit 98 → −20 = −0.2R (on the moved stop it would read −1.0R)
        T(id="a1", sym="AMD", port="core", cur="USD", qty=10, entry=100, sl=98, sl0=90, status="closed", exitPrice=98, date="2025-11-06", exitDate="2025-11-16", exitReason="sl", posGroup="a1"),
        # no original stop stored → R "—"
        T(id="p1", sym="PTT.BK", port="core", cur="THB", qty=1000, entry=36, sl=35, status="closed", exitPrice=37, date="2025-11-04", exitDate="2025-11-14", exitReason="tp", posGroup="p1"),
        # October (quarter / all only)
        T(id="o1", sym="AVGO", port="core", cur="USD", qty=10, entry=100, sl=90, sl0=90, status="closed", exitPrice=120, date="2025-10-01", exitDate="2025-10-20", exitReason="tp", posGroup="o1"),
        # August (all only)
        T(id="g1", sym="GE", port="core", cur="USD", qty=10, entry=100, sl=90, sl0=90, status="closed", exitPrice=90, date="2025-08-01", exitDate="2025-08-10", exitReason="sl", posGroup="g1"),
        # August scale-out (2 legs = ONE row: +100 and +200 on risk 100 + 100 = +1.5R) · an off-plan trade · a cancelled trade (Details only)
        T(id="sg1", sym="CAT", port="core", cur="USD", qty=10, entry=100, sl=90, sl0=90, status="closed", exitPrice=110, date="2025-08-02", exitDate="2025-08-12", exitReason="partial", posGroup="sg"),
        T(id="sg2", sym="CAT", port="core", cur="USD", qty=10, entry=100, sl=90, sl0=90, status="closed", exitPrice=120, date="2025-08-02", exitDate="2025-08-14", exitReason="tp", posGroup="sg"),
        T(id="u1", sym="UBER", port="core", cur="USD", qty=10, entry=100, sl=90, sl0=90, status="closed", exitPrice=95, date="2025-08-03", exitDate="2025-08-15", unplanned=True, posGroup="u1"),
        T(id="cx1", sym="SHOP", port="core", cur="USD", qty=10, entry=100, sl=90, status="cancelled", date="2025-11-08", cancelDate="2025-11-09", cancelTag="fear", posGroup="cx1"),
    ]


def closed_fam():
    return [
        # S50 · Sat · THB · +19,200 / risk 8,000 = +2.4R · planned exit with a lesson
        T(id="s1", sym="S50", port="satB", cur="THB", qty=2, mult=200, entry=900, sl=880, sl0=880, tp=960, status="closed", exitPrice=948, date="2025-11-10", exitDate="2025-11-15", posGroup="s1",
          review={"why": "planned", "lesson": "Let TP2 run, it worked", "at": "2025-11-15T10:00:00Z"}),
        # Family loss in THB: −2,000 / risk 2,000 = −1.0R · exit tag 'sl'
        T(id="f1", sym="CPALL.BK", port="core", cur="THB", qty=1000, entry=60, sl=58, sl0=58, status="closed", exitPrice=58, date="2025-11-03", exitDate="2025-11-11", exitReason="sl", posGroup="f1"),
    ]


def doc():
    d = R1.doc_c()
    d["books"]["main"]["trades"] = closed_main()
    d["books"]["fam"]["trades"] = closed_fam()
    return d


def nt_card(cid, acct, tk, reason, at, note="", strat="W"):
    return {"acct": acct, "ticker": tk, "market": "US", "strategy": strat, "status": "cancelled", "cancelReason": reason, "cancelNote": note, "cancelledAt": at, "plan": {"entry": 100, "stop": 95}}


def cards():
    return {
        "n1": nt_card("n1", "main", "GE", "hesitated", "2025-11-12T03:00:00.000Z", "Plan ready 2 days · ran +6% without me"),
        "n2": nt_card("n2", "main", "CAT", "hesitated", "2025-11-13T03:00:00.000Z"),
        "n3": nt_card("n3", "fam", "KO", "hesitated", "2025-11-14T03:00:00.000Z"),
        "n4": nt_card("n4", "main", "TSLA", "missed", "2025-11-15T03:00:00.000Z"),
        "n5": nt_card("n5", "fam", "PEP", "invalidated", "2025-11-16T03:00:00.000Z"),
        "n6": nt_card("n6", "main", "LLY", "thesis", "2025-11-17T03:00:00.000Z"),
        "n0": nt_card("n0", "main", "OLD", "hesitated", "2025-09-03T03:00:00.000Z", "", "L"),
    }


EXPECT = {   # by hand — November 2025, both accounts, All ports
    "n": 7, "thb_both": None,
}


def open_journal(pw, w, h, doc_=None, cards_=None, iso=CLK25, tab=True):
    import lib_phase39 as P39
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=doc_ or doc(), cards=cards_ if cards_ is not None else cards(), clean=True, iso=iso)
    page.add_style_tag(content=K.NOANIM); page.wait_for_timeout(300)
    if tab:
        js(page, "()=>{ switchTab('journal'); }"); page.wait_for_timeout(500)
    return b, page, pe
