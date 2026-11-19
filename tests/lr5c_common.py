#!/usr/bin/env python3
"""LR5c — shared fixture for the Port tab: main (Main) + fam (Family), fx 33, equity 5.0M / 10.0M, clock Wed 19 Nov 2025.
Open positions (hand-checkable) — see the run_tests_lr5c.py comments. NVDA is held in BOTH accounts; S50 is a futures position (Family); PTT.BK is a Thai stock."""
import os
import net_stub
import re1d_common as K
import re1c_common as R1
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
MOCK = os.path.join(HERE, "..", "docs", "briefs", "lr")
CLK = "2025-11-19T12:00:00+07:00"


def T(**o):
    return R1.tr(**o)


def main_trades():
    return [
        T(id="m_nvda", sym="NVDA", port="core", cur="USD", qty=11, entry=100, sl=95, posGroup="m_nvda", date="2025-11-10"),     # 11 × 100 × 33 = ฿36,300 · stop −55 × 33 = −฿1,815
        T(id="m_aapl", sym="AAPL", port="core", cur="USD", qty=30, entry=200, sl=190, posGroup="m_aapl", date="2025-11-10"),     # 30 × 200 × 33 = ฿198,000 · stop −300 × 33 = −฿9,900
        T(id="m_xau", sym="XAUUSD", port="satB", cur="USD", qty=0.05, mult=100, entry=2640, sl=2600, posGroup="m_xau", date="2025-11-12"),   # 0.05 × 2640 × 100 × 33 = ฿435,600
    ]


def fam_trades():
    return [
        T(id="f_nvda", sym="NVDA", port="core", cur="USD", qty=5, entry=100, sl=95, posGroup="f_nvda", date="2025-11-11"),      # 5 × 100 × 33 = ฿16,500 · stop −25 × 33 = −฿825
        T(id="f_ptt", sym="PTT.BK", port="core", cur="THB", qty=3000, entry=33, sl=30, posGroup="f_ptt", date="2025-11-11"),    # ฿99,000 · stop −฿9,000
        T(id="f_s50", sym="S50", port="satB", cur="THB", qty=4, mult=1, entry=900, sl=880, posGroup="f_s50", date="2025-11-17"),   # notional 4 × 900 × 200 = ฿720,000
    ]


def doc(with_fut=True):
    d = R1.doc_c()
    d["books"]["main"]["trades"] = main_trades()
    d["books"]["fam"]["trades"] = fam_trades() if with_fut else [t for t in fam_trades() if t["sym"] != "S50"]
    return d


def open_port(pw, w, h, doc_=None, view="both", iso=CLK):
    import lib_phase39 as P39
    b, ctx, page, ce, pe, dl = P39.launch(pw, w, h, doc=doc_ or doc(), cards={}, clean=True, iso=iso)
    page.add_style_tag(content=K.NOANIM); page.wait_for_timeout(300)
    js(page, "(v)=>{ lrSwReset && 0; LR_SW.port = v; switchTab('mix'); }", view); page.wait_for_timeout(600)
    return b, page, pe
