#!/usr/bin/env python3
"""CP1 — shared fixture: Compounder Watch stocks with daily-job numbers (rs.last / ma200 / vsMa / hi52 / offHi), a market doc (SPY / SET vs 52-week high) and a switchable regime (ffJson)."""
import os, json
import hf5_common as H
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
HWDONE = {"my_thesis": {"why": "Members renew and spend more", "evidence": "Renewal 92%", "exit": "Renewal below 90%"}, "hw": {"confirmedAt": "2026-10-01T03:00:00Z", "doneAt": "2026-10-01T03:00:00Z"}}

# sym: (market, last, ma200, hi52, extra doc fields)
STOCKS = {
    "COST": ("US", 905.0, 912.0, 1008.0, dict(HWDONE, buyZone={"lo": 880, "hi": 920})),                    # in zone · homework done
    "MSFT": ("US", 402.0, 398.0, 460.0, {"my_thesis": {"why": "Cloud keeps growing"}}),                     # near the 40-wk avg · no zone · homework 1 of 3
    "V": ("US", 285.0, 254.0, 300.0, dict(HWDONE, buyZone={"lo": 250, "hi": 265})),                         # above its zone · +12%
    "ADV": ("TH", 250.0, 255.0, 300.0, dict(HWDONE, buyZone={"lo": 200, "hi": 220})),                       # Thai: near the 40-wk avg (−2%), above its zone · uses SET
    "NODATA": ("US", None, None, None, {}),                                                                  # no daily numbers yet → "—"
}


def rs_for(last, ma, hi):
    if last is None: return {}
    return {"last": last, "lastDate": "2026-10-01", "ma200": ma, "vsMa": round(last / ma - 1, 4), "hi52": hi, "offHi": round(last / hi - 1, 4), "rating": 80}


def seed(page, stocks=None):
    """watch docs + price docs (app memory) · every Compounder"""
    st = stocks or STOCKS
    for t, (mk, last, ma, hi, x) in st.items():
        doc = dict({"ticker": t + (".BK" if mk == "TH" else ""), "market": mk, "port": "core", "note": "", "added_at": "2026-10-01T00:00:00Z", "ladder_watch": True, "ladder_watch_set": True, "exch": "SET" if mk == "TH" else "NASDAQ"}, **x)
        js(page, "(d)=>wlCol().doc(d.ticker).set(d)", doc)
    page.wait_for_timeout(500)
    js(page, "(m)=>Promise.all(Object.keys(m).map(k=>db.collection('users').doc(uid).collection('prices').doc(k).set({sym:k, ySym:k, rs:m[k]})))", {(t + (".BK" if v[0] == "TH" else "")): rs_for(v[1], v[2], v[3]) for t, v in st.items()})
    page.wait_for_timeout(400)


def market(page, spy=-0.02, st=-0.03):
    """the market doc the daily job writes (users/{uid}/market/index) — goes through the app's real listener"""
    js(page, "([a,b])=>db.collection('users').doc(uid).collection('market').doc('index').set({SPY:{close:500, hi52:510, offHi:a, asOf:'2026-10-01'}, SET:{close:1400, hi52:1450, offHi:b, asOf:'2026-10-01'}})", [spy, st])
    page.wait_for_timeout(250)


def regime(page, eq="green", cr="green"):
    """fund-flow ratios: state per signal (fresh dates for the harness clock)"""
    js(page, """([eq,cr])=>{ const it=(st,a,b)=>({tf:'D',sma:[20,50],adj:true,state:st,up:st==='green',days_in_state:20,flip_days:20,bar:'2026-10-01',inputs_asof:{[a]:'2026-10-01',[b]:'2026-10-01'},sma20:1.2,sma50:1.1,ratio:1.3,prev_week:{up:st==='green',bar:'2026-09-25'}});
      ffJson = Object.assign({}, ffJson || {}, {as_of:'2026-10-02', ver:3, ratios:Object.assign({}, (ffJson||{}).ratios||{}, {ACWI_BIL:it(eq,'ACWI','BIL'), HYG_IEI:it(cr,'HYG','IEI')})}); re1Cache = {}; }""", [eq, cr])


def today(page):
    js(page, "()=>{ re1Cache = {}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)


def png(page, name, full=False):
    os.makedirs(SHOTS, exist_ok=True)
    js(page, "()=>{ if(!document.getElementById('cpshot')){ const s=document.createElement('style'); s.id='cpshot'; s.textContent='@media (max-width:600px){#tabsMain{display:none!important}}'; document.head.appendChild(s); } }")
    page.wait_for_timeout(250); page.screenshot(path=os.path.join(SHOTS, name + ".png"), full_page=full)
