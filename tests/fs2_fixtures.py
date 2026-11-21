#!/usr/bin/env python3
"""FS2 — regenerates tests/fixtures/fs2/{compounder,momentum}.json = the LT2 fixtures + the optional FS2 fields (q.ends · ask · business[])."""
import json, os, copy
H = os.path.dirname(os.path.abspath(__file__))
B = lambda k, **x: dict(k=k, **x)


def build():
    out = {}
    d = json.load(open(os.path.join(H, "fixtures", "lt2", "compounder.json"))); f = d["facts"]
    f["q"]["ends"] = ["2025-11", "2026-02", "2026-05", "2026-08"]
    for r in f["q"]["rows"]:
        if r["k"] == "kpi_renewal": r["ask"] = "Are members staying?"
    f["lines"][1]["ask"] = "How much do fees matter?"
    f["lines"][3]["ask"] = "What does the market expect next?"
    f["business"] = [
        B("product", answer="Bulk groceries & goods in warehouse stores · 98% one-time sales, 2% yearly membership fees", line="Food 40% · Non-food 38% · Services 20% · Fees 2%", flag="info", flagText="info", kind="rpt", src="10-K note 11 · revenue by category", period="FY2026"),
        B("customers", answer="76M paid members — households and small businesses", line="No single customer ≥ 10% of revenue · own stores = 94% of sales", flag="ok", flagText="no customer ≥10%", kind="rpt", src="10-K Item 1 · note 11", period="FY2026"),
        B("economics", answer="Gross margin 12.6% · main cost = the goods it buys (87% of revenue)", line="Last 3 yrs: revenue +7%/yr · operating profit +12%/yr → profit grew faster", flag="ok", flagText="yes", kind="calc", src="calc · 10-K FY24–26", period="FY24–FY26", formula="Operating profit CAGR vs revenue CAGR, 3 years"),
        B("retention", answer="Renewal rate 92.5% in US/Canada · 90.0% worldwide", line="Down from 93.0% a year ago · membership is 1 year, no long contract", flag="watch", flagText="slipping", kind="rpt", src="Q1 FY27 earnings release", period="Q1 FY27", note="Renewal rate counts only members who were due to renew"),
        B("cash", missing=True, line="Debt due in 12 months is not split out in the filing"),
        B("outside", answer="Membership fee level vs competitors · tariffs on imported goods", line="Company names these in risk factors; no single supplier > 10% of purchases", flag="watch", flagText="2 named", kind="rpt", src="10-K Item 1A p.14–16", period="FY2026"),
    ]
    out["compounder"] = d
    d = json.load(open(os.path.join(H, "fixtures", "lt2", "momentum.json"))); f = d["facts"]
    f["q"]["ends"] = ["2025-11", "2026-02", "2026-05", "2026-08"]
    f["q"]["rows"][0]["ask"] = "Is revenue growing?"
    f["lines"][0]["ask"] = "Did it beat expectations?"
    f["business"] = [
        B("product", answer="AI custom chips and networking for cloud giants; VMware software", line="AI semis 55% · Non-AI semis 15% · Software 30%", flag="info", flagText="info", kind="rpt", src="10-Q segment note", period="Q3 FY26"),
        B("customers", answer="2 customers = 36% of revenue", line="Cloud giants buy in large multi-quarter orders", flag="watch", flagText="2 ≥10%", kind="rpt", src="10-Q p.18", period="Q3 FY26"),
        B("economics", answer="Gross margin 76% · operating margin 54%", line="Operating profit growing faster than revenue", flag="ok", flagText="yes", kind="calc", src="calc · 10-Q", period="Q3 FY26", formula="Operating income ÷ revenue"),
        B("outside", answer="Export limits on China · supply from one foundry", line="Named in risk factors", flag="watch", flagText="2 named", kind="rpt", src="10-K Item 1A", period="FY2025"),
    ]
    out["momentum"] = d
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(H, "fixtures", "fs2"), exist_ok=True)
    for k, v in build().items():
        json.dump(v, open(os.path.join(H, "fixtures", "fs2", k + ".json"), "w"), ensure_ascii=False, indent=1)
        print("wrote", k)
