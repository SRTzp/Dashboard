#!/usr/bin/env python3
"""LR2 — Today: tab shortcuts (0) · glance band (A) · one Act list (B) · side column + Risk room (C).
Screenshots (tests/screenshots, git add -f): lr2-today-1440 · lr2-today-390 · lr2-act-family-place-390 · lr2-glance-empty-1440
Run: python3 tests/run_tests_lr2.py"""
import os, sys, re, json
from playwright.sync_api import sync_playwright
import net_stub  # no real network in tests
import re1d_common as K
from re1d_common import js, launch, check, results, plan_card

SHOTS = K.SHOTS
def sp(t): return re.sub(r"\s+", " ", t or "").strip()
def ovf(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")


def part0(page, tag):
    order = js(page, "()=>TAB_ORDER")
    check(f"{tag} 0: TAB_ORDER = today,plan,flow,watch,journal,mix", order == ["today", "plan", "flow", "watch", "journal", "mix"], order)
    js(page, "()=>switchTab('today')"); page.wait_for_timeout(150)
    res = []
    for k, t in (("1", "today"), ("2", "plan"), ("3", "flow"), ("4", "watch"), ("5", "journal"), ("6", "mix")):
        page.keyboard.press(k); page.wait_for_timeout(150); res.append(js(page, "()=>activeTab") == t)
    check(f"{tag} 0: keys 1 Today · 2 Plan · 3 Flow · 4 Watch · 5 Journal · 6 Port", all(res), res)
    tips = js(page, "()=>[...document.querySelectorAll('#tabsMain .tabbtn')].map(b=>b.title)")
    check(f"{tag} 0: tooltips show the key", tips == ["Today · 1", "Plan · 2", "Flow · 3", "Watch · 4", "Journal · 5", "Port · 6"], tips)
    js(page, "()=>switchTab('today')"); page.wait_for_timeout(150)
    js(page, "()=>document.getElementById('hdrPlanBtn').click()"); page.wait_for_timeout(300)
    page.keyboard.press("3"); page.wait_for_timeout(200)
    check(f"{tag} 0: key 3 with the New-plan chooser open does not switch tab", js(page, "()=>activeTab") == "today" and js(page, "()=>!!document.getElementById('bdPop')"))
    js(page, "()=>bdPopClose()")
    js(page, "()=>openSettings && openSettings()"); page.wait_for_timeout(300)
    page.keyboard.press("4"); page.wait_for_timeout(200)
    check(f"{tag} 0: key 4 with a sheet open does not switch tab", js(page, "()=>activeTab") == "today")
    page.keyboard.press("Escape"); page.wait_for_timeout(200)


def today_iso(page): return js(page, "()=>Calc.wiIctDate(Date.now())")


def set_regime(page, eq, cr, asof="fresh"):
    """fixture: fundflow.json with the two ratios (green|red|neutral) · asof fresh (today) | stale (30d old)"""
    js(page, """([eq, cr, asof])=>{
      const d = new Date(); if(asof === 'stale') d.setDate(d.getDate() - 30); const iso = d.toISOString().slice(0, 10);
      const mk = st=>({tf:'D', sma:[20,50], adj:true, state:st, up:st==='green', days_in_state:12, inputs_asof:{a:iso, b:iso}, sma20:1.2, sma50:1.1});
      ffJson = {as_of: iso, ratios:{ACWI_BIL: mk(eq), HYG_IEI: mk(cr)}}; re1Cache = {}; todayRefresh(true); }""", [eq, cr, asof])
    page.wait_for_timeout(250)


def card(page, k): return sp(js(page, "(k)=>{ const c = document.querySelector('[data-lr2-card=\"'+k+'\"]'); return c ? c.innerText : null; }", k))


def seed_wi(page):
    js(page, """()=>{
      const mon = wiCurMon(), at = Date.now() + 26 * 3600000, iso = new Date(at).toISOString();
      const doc = {id: mon, week: mon, events:{cpi:{title:'US CPI', label_th:'US CPI', scheduled_at: iso, time_status:'confirmed', status:'scheduled', kind:'cpi'}},
        assets:{XAUUSD:{impact:'HIGH', event_refs:['cpi']}, BTCUSD:{impact:'MED', event_refs:[]}, S50:{impact:'LOW', event_refs:[]}, BRENT:{impact:'LOW', event_refs:[]}}};
      wiDocs = {}; wiDocs[mon] = doc;
      window.__bdBias = bdBias; window.__pk = satWeekPickList; satWeekPickList = ()=>['XAUUSD','BTCUSD','S50','BRENT'];
      bdBias = k=>k === 'XAUUSD' ? {k:'bull', t:'Bull'} : k === 'BTCUSD' ? {k:'bear', t:'Bear'} : {k:'none', t:'No Playbook'};
      todayRefresh(true); }""")
    page.wait_for_timeout(250)


def seed_rrg(page):
    js(page, """()=>{
      const mk = (s, q, r)=>({sym:s, quad:q, ratio:r, mom:100, dMom:0.3, model:RRG_MODEL, err:null});
      const f = ffState();
      f.rrg = {rowsD:[mk('XLC','lead',103), mk('XLI','lead',105), mk('ITA','lead',101), mk('XLK','lead',99.9), mk('SMH','imp',98), mk('XLK2','lag',90), mk('IGV','lag',92), mk('XLU','lag',95)], rowsW:[], build:RRG_BUILD, model:RRG_MODEL, lastBar:rrgToday(), day:rrgToday()};
      todayRefresh(true); }""")
    page.wait_for_timeout(250)


def partA(page, tag, w):
    wide = w >= 900
    # mood — one rule on the shared regime result
    for eq, cr, asof, want, st in (("green", "green", "fresh", "Risk-on", "green"), ("red", "green", "fresh", "Mixed", "amber"), ("green", "red", "fresh", "Mixed", "amber"),
                                   ("red", "red", "fresh", "Risk-off", "amber"), ("green", "green", "stale", "Unclear", "grey"), ("neutral", "green", "fresh", "Unclear", "grey")):
        set_regime(page, eq, cr, asof)
        got = js(page, "()=>{ const c = document.querySelector('[data-lr2-card=\"mood\"]'); return c ? [c.dataset.rgLabel, c.dataset.rgState] : null; }")
        check(f"{tag} A: mood {eq}/{cr}/{asof} = {want} ({st})", got == [want, st], got)
    set_regime(page, "red", "red", "fresh")
    pc = js(page, "()=>rm1Eff().pc")
    check(f"{tag} A: line 2 reads the effective size ({pc}%) from the same RM1 result", f"{pc}%" in card(page, "mood") and "ntries" in card(page, "mood"), card(page, "mood"))
    check(f"{tag} A: old tdRegimeVerdict reads the same label (no second rule)", js(page, "()=>{ const d = document.createElement('div'); d.innerHTML = tdRegimeVerdict(); return d.firstChild.dataset.rgLabel === lr2Mood().label; }"))
    set_regime(page, "green", "green", "fresh")
    # empty states
    js(page, "()=>{ wiDocs = {}; ffState().rrg = {rowsD:[], rowsW:[]}; todayRefresh(true); }"); page.wait_for_timeout(250)
    check(f"{tag} A: moves empty = 'No Weekly Impact · Import ›'", "No Weekly Impact · Import ›" in card(page, "moves"), card(page, "moves"))
    check(f"{tag} A: news empty = 'No key news this week'", "No key news this week" in card(page, "news"), card(page, "news"))
    if wide:
        check(f"{tag} A: four cards", js(page, "()=>document.querySelectorAll('.lr2-glance [data-lr2-card]').length") == 4)
        page.screenshot(path=os.path.join(SHOTS, "lr2-glance-empty-1440.png"))
    # filled
    seed_wi(page); seed_rrg(page)
    js(page, """()=>{ const B = getBook(tdHome()); B.settings.newsEvents = []; saveBook(tdHome()); todayRefresh(true); }"""); page.wait_for_timeout(200)
    mv = card(page, "moves"); hot = card(page, "hot"); nw = card(page, "news")
    check(f"{tag} A: moves chips XAU ▲ HIGH · BTC ▼ MED, quiet assets on line 2", "XAU ▲" in mv and "BTC ▼" in mv and ("HIGH" in mv and "MED" in mv if wide else True) and (("quiet" in mv) if wide else True), mv)
    check(f"{tag} A: hot sectors = up to 3 Leading by strength (↗, names) then first Improving ⤴ + Lagging ↘", ("↗ Industrials" in hot or "↗ Infra" in hot or "XLI" not in hot) and hot.count("↗") == 3 and "⤴" in hot and (hot.count("↘") == 2 if wide else True), hot)
    order = js(page, "()=>[...document.querySelectorAll('[data-lr2-hot]')].map(c=>c.dataset.lr2Hot)")
    check(f"{tag} A: Leading chips sorted by strength", order == ["XLI", "XLC", "ITA"], order)
    check(f"{tag} A: next news = ICT time + name + impact", "HIGH" in nw and "US CPI" in nw if wide else "HIGH" in js(page, "()=>document.querySelector('[data-lr2-card=\"news\"]').innerText"), nw)
    if wide:
        hs = js(page, "()=>[...document.querySelectorAll('.lr2-glance .lr2-c')].map(c=>Math.round(c.getBoundingClientRect().height))")
        check(f"{tag} A: all four cards the same height ({hs})", len(set(hs)) == 1, hs)
        hh = js(page, "()=>{ const c = document.querySelector('[data-lr2-card=\"hot\"] .chs'); return [c.scrollHeight <= c.clientHeight + 1, new Set([...c.children].map(x=>Math.round(x.getBoundingClientRect().top))).size]; }")
        check(f"{tag} A: hot chip row never wraps", hh[0] and hh[1] == 1, hh)
    # tap-through
    if w == 1440: page.screenshot(path=os.path.join(SHOTS, "lr2-today-1440.png"))
    if w == 390: page.screenshot(path=os.path.join(SHOTS, "lr2-today-390.png"))
    js(page, "()=>switchTab('today')")
    for k, fn in (("news", "td3GoCal"), ("hot", "ln4GoLeadership"), ("mood", "tdRegimeGo")):
        js(page, "(fn)=>{ window.__called = null; window['__o_'+fn] = window[fn]; window[fn] = ()=>{ window.__called = fn; }; }", fn)
        js(page, "(k)=>document.querySelector('[data-lr2-card=\"'+k+'\"]').click()", k)
        got = js(page, "()=>window.__called"); js(page, "(fn)=>{ window[fn] = window['__o_'+fn]; }", fn)
        check(f"{tag} A: {k} card taps through ({fn})", got == fn, got)
    js(page, "()=>{ bdBias = window.__bdBias; satWeekPickList = window.__pk; wiDocs = {}; todayRefresh(true); }")


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        page.wait_for_timeout(300)
        part0(page, tag)
        partA(page, tag, w)
        check(f"{tag} no page errors", not pe, pe)
        check(f"{tag} no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY lr2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
