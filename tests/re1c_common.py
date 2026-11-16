"""RE-C1 shared fixtures: two accounts (main / fam), confirmed snapshots, costs. Clock of the harness = 2026-10-02 (Friday)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import ln3fix_common as C
import lib_phase38 as P38
import lib_phase39 as P39
js = C.js
def tr(**o):
    t = {"port": "core", "bias": "Long", "mult": 1, "cur": "THB", "status": "open", "date": "2026-09-29", "qty": 100, "entry": 100, "sl": 95, "tp": None}
    t.update(o); return t


def doc():
    d = P38.doc38(clean=True)
    for b in d["books"].values(): b["settings"].pop("satWeekPick", None)
    m = d["books"]["main"]; f = d["books"]["fam"]
    m["trades"] = [
        tr(id="m1", sym="AAPL", cur="USD", qty=6, entry=200, sl=195, posGroup="m1", sl0=190),
        tr(id="m1x", sym="AAPL", cur="USD", qty=4, entry=200, sl=190, status="closed", exitPrice=210, exitDate="2026-10-01", closedAt="2026-10-01T04:00:00.000Z", posGroup="m1", sl0=190),
        tr(id="m2", sym="PTT.BK", qty=1000, entry=36, sl=35, status="closed", exitPrice=35, exitDate="2026-09-30"),
        tr(id="b1", sym="ZZZ.BK", qty=3, entry=10, sl=9, status="closed", exitPrice=10.1, exitDate="2026-09-22", closedAt="2026-09-22T03:00:00.000Z"),
        tr(id="l1", sym="MSFT", cur="USD", qty=5, entry=400, sl=380, posGroup="l1", sl0=380),
        tr(id="l1a", sym="MSFT", cur="USD", qty=5, entry=390, sl=380, posGroup="l1", acc=True, accOf="l1", sl0=380),
        tr(id="l1b", sym="MSFT", cur="USD", qty=5, entry=380, sl=380, posGroup="l1", sl0=380),
    ]
    f["trades"] = [tr(id="f2", sym="PTT.BK", qty=200, entry=36, sl=35)]
    return d


def cards():
    return {
        "cA": {"acct": "main", "ticker": "AAPL", "market": "US", "strategy": "W", "status": "open", "trade_id": "m1", "stopHistory": [{"date": "2026-09-30", "from": 190, "to": 195}], "lots": [{"n": 1, "px": 200, "qty": 10}], "plan": {"entry": 200, "stop": 190}},
        "cL": {"acct": "main", "ticker": "MSFT", "market": "US", "strategy": "L", "status": "open", "trade_id": "l1", "acc_trade_id": "l1a", "stopHistory": [], "lots": [{"n": 1, "px": 400, "qty": 5}, {"n": 2, "px": 390, "qty": 5, "layer": "acc"}, {"n": 3, "px": 380, "qty": 5}]},
        "cP": {"acct": "main", "ticker": "NVDA", "market": "US", "strategy": "W", "status": "plan", "plan": {"entry": 120, "stop": 110, "ps1": {"rows": [{"px": 120, "qty": 50}]}}, "ln4": {"placedLv": {"0": "2026-10-01T02:00:00.000Z"}}},
    }



def doc_c(snap=True, costs=True, equity=5000000, fam_equity=10000000):
    d = doc()
    for k, a in d["books"].items():
        st = a["settings"]
        if snap: st["equitySnapshots"] = [{"id": "s1", "bkkDate": "2026-09-28", "equity": equity if k == "main" else fam_equity, "confirmed": True, "kind": "weekly", "fx": 33}]
        if costs: st["costSettings"] = {"winner": {"perUnit": 0.005, "min": 1}, "ladder": {"perUnit": 0.005, "min": 1}, "sat": {"perUnit": 7, "swapDay": 3}}
        st["fx"] = 33
    return d
