"""LR3 part B — confirm sheet (Core + Satellite + later level) · order: band · legs · stop · tiles · … · Confirm · footnote."""
import os, re
from re1d_common import js, check, launch
import pv1_common as PV

SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
def sp(t): return re.sub(r"\s+", " ", t or "").strip()

ORDER_JS = """()=>{
  const q = s=>document.querySelector(s), top = e=>e ? e.getBoundingClientRect().top + window.scrollY : null;
  const sheet = q('[data-pb2-step="place"]'); if(!sheet) return null;
  const pos = s=>{ const e = sheet.querySelector(s); return e ? [...sheet.querySelectorAll('*')].indexOf(e) : -1; };
  const legs = [...sheet.querySelectorAll('[data-lr3-leg]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim());
  const stop = (sheet.querySelector('[data-lr3-stop]')||{}).innerText;
  const y = e=>e ? e.getBoundingClientRect().top : null;
  return {band: pos('[data-lr-band]'), orders: pos('[data-lr3-orders]'), leg: pos('[data-lr3-leg]'), stop: pos('[data-lr3-stop]'), tiles: pos('[data-lr3-tiles]'), more: pos('[data-ef-more]'), yes: pos('[data-pb2-yes]'), note: pos('.pb2-note'),
    legs, stop_t: (stop||'').replace(/\\s+/g,' ').trim(), tilesT: (sheet.querySelector('[data-lr3-tiles]')||{innerText:''}).innerText.replace(/\\s+/g,' '),
    nTiles: sheet.querySelectorAll('.lr3-tile').length, setup: pos('[data-ef-setup],[data-pb2-checks]')};
}"""

STICKY_JS = """()=>{
  const f = document.querySelector('.lr3-foot'), y = document.querySelector('[data-pb2-yes]'); if(!f || !y) return null;
  const r = y.getBoundingClientRect();
  return {pos: getComputedStyle(f).position, h: Math.round(r.height), bottomOk: r.bottom <= innerHeight + 1 && r.top >= 0, vh: innerHeight, bot: Math.round(r.bottom)};
}"""


def order_ok(o, sat=False):
    return o and 0 <= o["band"] < o["orders"] < o["leg"] < o["stop"] < o["tiles"] < o["yes"] < o["note"] and (o["more"] < 0 or o["tiles"] < o["more"] < o["yes"]) and o["nTiles"] == 3


def close(page): js(page, "()=>{ try{ if(bdPopOpen()) bdPopClose(); }catch(e){} }"); page.wait_for_timeout(150)


def partB(page, tag, w):
    js(page, "()=>{ serverConfirmed = true; stateFromServer = true; if(acctActive !== 'main') acctSwitch('main'); bdChip='all'; re1Cache = {}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
    js(page, "()=>efCorePlaceOpen('mN')"); page.wait_for_timeout(450)
    o = js(page, ORDER_JS)
    check(f"{tag} B core: order = account band · Orders to place (legs) · STOP row · Risk/Reward/Size tiles · Confirm · footnote", order_ok(o), o)
    check(f"{tag} B core: leg = 'BUY #40 @ 100 Limit · entry', stop row = 'Stop 92 …'", o and len(o["legs"]) == 1 and re.match(r"^BUY #\d+ @ 100 (Limit|Stop) · entry", o["legs"][0]) and o["stop_t"].startswith("STOP 92"), o and [o["legs"], o["stop_t"]])
    check(f"{tag} B core: tiles read Risk · Reward · Size", o and all(k in o["tilesT"].lower() for k in ("risk", "reward", "size")), o and o["tilesT"])
    check(f"{tag} B core: Setup line (EF1b) still there, after the tiles", js(page, "()=>!!document.querySelector('[data-ef-core-place] [data-ef-setup]')") and o["tiles"] < o["setup"], o)
    check(f"{tag} B core: Not yet / Confirm / records-only footnote", js(page, "()=>!!document.querySelector('[data-pb2-no]') && !!document.querySelector('[data-pb2-yes]') && /Records only/.test(document.querySelector('.pb2-note').innerText)"))
    check(f"{tag} B core: More ▾ holds size working", js(page, "()=>{ const d=document.querySelector('[data-ef-core-place] [data-ef-more]'); return !!d && /More/.test(d.querySelector('summary').innerText) && !d.open; }"))
    if w < 600:
        s = js(page, STICKY_JS)
        check(f"{tag} B core 390: sticky footer · Confirm visible and ≥ 44 px", s and s["pos"] == "sticky" and s["h"] >= 44 and s["bottomOk"], s)
        page.screenshot(path=os.path.join(SHOTS, "lr3-sheet-390.png"))
    if w == 1440: page.screenshot(path=os.path.join(SHOTS, "lr3-sheet-1440.png"))
    ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
    check(f"{tag} B core: no overflow", ov <= 0, ov)
    close(page)
    # later level (AVGO entry 2/2)
    js(page, "()=>efCorePlaceOpen('mA', 1)"); page.wait_for_timeout(450)
    o2 = js(page, ORDER_JS)
    check(f"{tag} B later level: same order · one leg 'entry 2/2' @ 150", order_ok(o2) and len(o2["legs"]) == 1 and "entry 2/2" in o2["legs"][0] and "@ 150" in o2["legs"][0], o2)
    check(f"{tag} B later level: 'This order' risk line (EF1b) still shown", js(page, "()=>!!document.querySelector('[data-ef-order-risk]')"))
    close(page)
    # two-level plan opened normally: both legs
    js(page, "()=>efCorePlaceOpen('mA')"); page.wait_for_timeout(400)
    o3 = js(page, ORDER_JS)
    check(f"{tag} B two entries: two legs entry 1/2 · 2/2, one stop row with the target", o3 and len(o3["legs"]) == 2 and "entry 1/2" in o3["legs"][0] and "entry 2/2" in o3["legs"][1] and "target" in o3["stop_t"], o3 and [o3["legs"], o3["stop_t"]])
    close(page)


def run_sat(pw, w, h, tag):
    b, page, ce, pe = launch(pw, w, h, d=PV.doc_sat(), c=PV.cards_pv())
    try:
        js(page, PV.SAT_JS); js(page, PV.SAT_PLANS_JS); page.wait_for_timeout(700)
        js(page, "()=>{ re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(300)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','XAGUSD']); switchTab('plan'); bdRender(); if(bdPopOpen()) bdPopClose(); pb2 = {step:'place', id:'xp', a:'XAUUSD'}; pb2Render(); }"); page.wait_for_timeout(450)
        o = js(page, ORDER_JS)
        check(f"{tag} B sat: order = band · legs · STOP row · tiles · checks · Confirm · footnote", order_ok(o, True) and o["tiles"] < o["setup"], o)
        check(f"{tag} B sat: leg 'BUY #0.21 @ 2,642', STOP row with target and sell", o and o["legs"] and re.match(r"^BUY #0\.21 @ 2,642", o["legs"][0]) and o["stop_t"].startswith("STOP 2,628") and "target" in o["stop_t"], o and [o["legs"], o["stop_t"]])
        check(f"{tag} B sat: data-pb2-order kept on the first leg", js(page, "()=>!!document.querySelector('[data-pb2-order]')"))
        if w < 600:
            s = js(page, STICKY_JS)
            check(f"{tag} B sat 390: sticky footer · Confirm visible and ≥ 44 px", s and s["pos"] == "sticky" and s["h"] >= 44 and s["bottomOk"], s)
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} B sat: no overflow", ov <= 0, ov)
        check(f"{tag} B sat: Not yet / Confirm still wired", js(page, "()=>/pb2PlaceNo/.test(document.querySelector('[data-pb2-no]').getAttribute('onclick')) && /pb2PlaceYes/.test(document.querySelector('[data-pb2-yes]').getAttribute('onclick'))"))
    finally:
        b.close()
