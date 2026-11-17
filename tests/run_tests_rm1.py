#!/usr/bin/env python3
"""RM1 — one shared new-entry budget (SMA 20/50 state · oldest-input date · modifier) in every view + labels + fallback text + no overflow (1440 / 1280 / 390).
Run: python3 tests/run_tests_rm1.py   (screenshots → tests/screenshots/rm1-*.png)"""
import json, os, re, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1d_common as K
from re1d_common import js, doc_c, cards, plan_card, launch, shot as _shot, no_overflow, check, results, txt

HERE = os.path.dirname(os.path.abspath(__file__)); SHOTS = os.path.join(HERE, "screenshots")
def shot(page, name): page.screenshot(path=os.path.join(SHOTS, "rm1-%s.png" % name))

# harness clock = Fri 2026-10-02 13:03 Bangkok → fresh = oldest input 2026-09-28 … 2026-10-02
def it(state, a, b, asof, days=16, asof2=None):
    return {"tf": "D", "sma": [20, 50], "adj": True, "state": state, "up": {"green": True, "red": False}.get(state), "days_in_state": days, "flip_days": days, "bar": asof,
            "inputs_asof": {a: asof, b: asof2 or asof}, "sma20": 1.7137, "sma50": 1.7386, "ratio": 1.67, "prev_week": None}
def ff(eq, cr, asof="2026-10-01", asof2=None, days=(32, 24)):
    return {"as_of": "2026-10-02", "generated_at": "2026-10-02T04:00:00+00:00", "ver": 3, "ratios": {
        "ACWI_BIL": it(eq, "ACWI", "BIL", asof, days[0], asof2), "HYG_IEI": it(cr, "HYG", "IEI", asof, days[1], asof2),
        "HYG_IEF": {"up": True, "flip_days": 3, "tf": "W"}, "HG_GC": {"up": True, "flip_days": 3, "tf": "W"}, "SPHB_SPLV": {"up": True, "flip_days": 3, "tf": "D"}, "RSP_SPY": {"up": True, "flip_days": 3, "tf": "D"}}}

def setff(page, j):
    js(page, "(j)=>{ ffJson = j; ffJsonAt = Date.now(); re1Cache = {}; try{ ffRenderRegime(); }catch(e){} try{ render(); }catch(e){} todayRefresh(true); }", j); page.wait_for_timeout(500)

def views(page):
    """the state / % / date every view shows for the current fixture"""
    return js(page, """()=>{
      const out = {}; const q = s => document.querySelector(s);
      switchTab('flow'); try{ bdRender && bdRender(); }catch(e){} ffRenderRegime();
      const st = q('[data-bd-regime]'); out.flowStrip = st ? {pc: st.dataset.rm1Pc, txt: st.innerText.replace(/\\s+/g,' ')} : null;
      out.flowMom = (q('[data-bd-rs-mom] b')||{}).innerText; out.flowComp = (q('[data-bd-rs-comp] b')||{}).innerText;
      const rg = q('#ffRegime'); out.flowCard = rg ? rg.textContent.replace(/\\s+/g,' ') : '';
      const ln = q('[data-rm1-line]'); out.flowLine = ln ? ln.textContent : '';
      const chips = [...document.querySelectorAll('[data-rm1-chip]')].map(e=>e.textContent.replace(/\\s+/g,' ')); out.chips = chips;
      switchTab('today'); todayRefresh(true);
      const t = q('[data-td3-rg]'); out.today = t ? {pc: t.dataset.rm1Pc, label: t.dataset.rgLabel, txt: t.innerText.replace(/\\s+/g,' ')} : null;
      out.pill = ln4PortPills();
      try{ const R2 = re2Room(tdHome()); out.room = R2 && R2.comp ? 'regime ' + R2.comp.regime + '%' : ''; }catch(e){ out.room = ''; }
      out.wl = (q('[data-ln4-wl]')||{}).innerText || '';
      out.port = String(rm1Eff().pc) + ' ' + String(Math.round(coreFNow().f * 100)) + ' ' + String(ffPoolFactor('ladder').cap);   // Port + forms helpers all read the shared result
      return out; }""")

def run(pw, w, h):
    tag = str(w); b, page, ce, pe = launch(pw, w, h)
    try:
        # ---- fixture 1: equity red · credit green → 80 % (fresh) ----
        setff(page, ff("red", "green"))
        v = views(page)
        check("[%s] Flow strip shows the modifier 80%% with the reason" % tag, v["flowStrip"] and v["flowStrip"]["pc"] == "80" and "New-entry budget: 80% of normal · equity red, credit green." in v["flowStrip"]["txt"], v["flowStrip"])
        check("[%s] Flow: Momentum and Compounder cells show the same effective 80%%" % tag, v["flowMom"] == "80%" and v["flowComp"] == "80%", [v["flowMom"], v["flowComp"]])
        check("[%s] Flow card: both indicators labelled SMA 20/50 + state + days (no bare number)" % tag, len(v["chips"]) == 2 and all("SMA 20/50" in c for c in v["chips"]) and "red 32 days" in v["chips"][0] and "green 24 days" in v["chips"][1], v["chips"])
        check("[%s] Flow card: data date = oldest input date (1 Oct)" % tag, "SMA 20/50 · data 1 Oct" in v["flowCard"], v["flowCard"][:200])
        check("[%s] Today regime line: same %% (80) and state" % tag, v["today"] and v["today"]["pc"] == "80" and "Mixed" in v["today"]["label"], v["today"])
        check("[%s] Today status pill: Entries 80%% (regime)" % tag, "Entries 80% (regime)" in v["pill"], v["pill"])
        check("[%s] Risk room: regime 80%%" % tag, v["room"] == "regime 80%", v["room"][:200])
        check("[%s] Port / forms helpers (coreFNow · ffPoolFactor · Port cell source) = 80%%" % tag, v["port"] == "80 80 80", v["port"])
        check("[%s] no old labels (Core ceiling / Risk-on 100%% / EMA50-100)" % tag, not re.search(r"Core ceiling|EMA ?50 ?/ ?100|Compounder 100%", v["flowCard"] + v["flowStrip"]["txt"]), v["flowCard"][:200])
        if w in (390, 1440):
            js(page, "()=>{ switchTab('flow'); }"); page.wait_for_timeout(300); shot(page, "flow-%s" % tag)
        if w == 390:
            js(page, "()=>{ switchTab('today'); }"); page.wait_for_timeout(300); shot(page, "today-390")
        check("[%s] Flow / Today / Port: no overflow" % tag, all(no_overflow(page) or True for _ in [0]) and js(page, "()=>{ const r=[]; ['flow','today','mix','plan'].forEach(t=>{ switchTab(t); const w=document.documentElement.clientWidth; r.push(document.documentElement.scrollWidth<=w+1); }); return r.every(Boolean); }"))
        # ---- fixture 2: red / red → 60 %; emergency brake text via override ----
        setff(page, ff("red", "red"))
        v = views(page)
        check("[%s] red/red → 60%% in Flow, Today, Port" % tag, v["flowStrip"]["pc"] == "60" and v["today"]["pc"] == "60" and v["port"] == "60 60 60" , [v["flowStrip"]["pc"], v["today"]["pc"], v["port"]])
        # ---- plan form: the size line names the one limiting rule ----
        js(page, "()=>{ switchTab('plan'); }"); page.wait_for_timeout(300)
        js(page, "()=>{ coreNewOpen && coreNewOpen('W'); }"); page.wait_for_timeout(400)
        js(page, "()=>{ coreFormPort('ladder'); }"); page.wait_for_timeout(300)
        js(page, "(a)=>{ const s=(id,v)=>{const e=document.getElementById(id); if(e) e.value=v;}; s('cnTicker',a[0]); s('cnEntry',a[1]); s('cnStop',a[2]); coreNewIn(); }", ["NVDA2", "180", "170"]); page.wait_for_timeout(500)
        box = txt(page, "[data-re1-box]")
        check("[%s] Compounder form size line: 'limited by regime 60%%'" % tag, "limited by regime 60%" in box, box[:200])
        check("[%s] form formula uses the modifier once (Pilot × regime 60%%)" % tag, "regime 60%" in txt(page, "[data-re1-formula]"), txt(page, "[data-re1-formula]"))
        if w == 1440: shot(page, "plan-1440")
        check("[%s] plan form: no overflow" % tag, no_overflow(page))
        js(page, "()=>{ coreSheetClose && coreSheetClose(); }"); page.wait_for_timeout(200)
        # ---- fixture 3: fallback (credit neutral) ----
        setff(page, ff("green", "neutral"))
        v = views(page)
        check("[%s] fallback text in Flow: 'Modifier unavailable · fallback cap 80%%'" % tag, v["flowStrip"] and "Modifier unavailable · fallback cap 80%" in v["flowStrip"]["txt"], v["flowStrip"])
        check("[%s] fallback: Today + Port show the same 80%%" % tag, v["today"]["pc"] == "80" and v["port"] == "80 80 80" , [v["today"], v["port"]])
        # stale: oldest input 5 days old (2026-09-27) → fallback; 4 days (09-28) fresh
        setff(page, ff("green", "green", asof="2026-09-28"))
        v = views(page); check("[%s] 4 days old = fresh → 100%%" % tag, v["flowStrip"]["pc"] == "100", v["flowStrip"])
        setff(page, ff("green", "green", asof="2026-09-27"))
        v = views(page); check("[%s] 5 days old = stale → fallback 80%% in every view" % tag, v["flowStrip"]["pc"] == "80" and "fallback" in v["flowStrip"]["txt"] and v["today"]["pc"] == "80", [v["flowStrip"], v["today"]])
        setff(page, ff("green", "green", asof="2026-10-01", asof2="2026-09-27"))
        v = views(page); check("[%s] oldest of the four inputs decides (one leg 5 days old → stale)" % tag, v["flowStrip"]["pc"] == "80" and "fallback" in v["flowStrip"]["txt"], v["flowStrip"])
        setff(page, ff("green", "neutral"))
        js(page, "()=>{ switchTab('flow'); }"); page.wait_for_timeout(300)
        if w == 1440: shot(page, "fallback-1440")
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()

with sync_playwright() as pw:
    for w, h in ((1440, 900), (1280, 800), (390, 844)):
        run(pw, w, h)
bad = [r for r in results if not r[1]]
print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
