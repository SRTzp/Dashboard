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
    check(f"{tag} A: news empty = 'No key news this week'", "No key news" in card(page, "news"), card(page, "news"))
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


def cards_b():
    cs = {"pA": plan_card("NVDA", 100, 92, px=99, ready=True), "pF": plan_card("BBB.BK", 100, 92, px=99, ready=True)}
    cs["pF"]["acct"] = "fam"; cs["pF"]["market"] = "TH"
    cs["oF"] = plan_card("OOO", 50, 45, px=49, ready=True); cs["oF"]["acct"] = "fam"; cs["oF"]["ln4"] = {"placedAt": "2026-11-17T01:00:00Z"}   # a Family order that is already working
    return cs


def partB(page, tag, w):
    js(page, "()=>{ re1Cache = {}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
    rows = js(page, "()=>[...document.querySelectorAll('[data-re2-row]')].map(r=>({sym:r.dataset.re2Row, acct:r.dataset.lr2Acct, pill:(r.querySelector('[data-lr2-pill]')||{}).innerText, grp:r.dataset.re2Grp, dir:(r.querySelector('[data-lr2-dir]')||{}).innerText, btn:(r.querySelector('[data-re2-btn]')||{}).dataset?.re2Btn}))")
    by = {r["sym"]: r for r in rows}
    check(f"{tag} B: Act lists Main AND Family rows (active account stays Main)", "NVDA" in by and "BBB.BK" in by and js(page, "()=>acctActive") == "main", rows)
    check(f"{tag} B: rows carry the M / F account pill + direction", by.get("NVDA", {}).get("pill") == "M" and by.get("BBB.BK", {}).get("pill") == "F" and by.get("NVDA", {}).get("dir") == "Long", rows)
    check(f"{tag} B: Family order shows under Check orders with its Filled button", by.get("OOO", {}).get("grp") == "check" and by.get("OOO", {}).get("btn") == "fill", rows)
    head = sp(js(page, "()=>(document.querySelector('[data-lr2-head]')||{innerText:''}).innerText"))
    check(f"{tag} B: header = Act · Main + Family · state · Open risk with M/F pills / 3%", head.startswith("Act") and "Main + Family" in head and "Open risk" in head and "/ 3%" in head, head)
    check(f"{tag} B: no futures figure when there are no futures", js(page, "()=>!document.querySelector('[data-lr2-fut]')"))
    js(page, "()=>{ window.wl1PlaceGate = ()=>true; }")   # the homework cap is orthogonal to account routing (fixture plans are 40 sh with no homework)
    # Place on the Family row → Family band, records to Family, active stays Main
    js(page, "()=>{ document.querySelector('[data-re2-row=\"BBB.BK\"] [data-re2-btn=\"place\"]').click(); }"); page.wait_for_timeout(500)
    band = js(page, "()=>{ const b = document.querySelector('[data-lr-band]'); return b ? [b.dataset.lrBand, (b.querySelector('[data-lr-band-detail]')||{}).innerText] : null; }")
    check(f"{tag} B: Place on the F row opens the sheet with the Family band", band and band[0] == "F" and "records to Family only" in band[1], band)
    if w == 390: page.screenshot(path=os.path.join(SHOTS, "lr2-act-family-place-390.png"))
    js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(700)
    st = js(page, "()=>({active: acctActive, f: (coreCardsList.find(c=>c.id==='pF')||{}).ln4, m: (coreCardsList.find(c=>c.id==='pA')||{}).ln4})")
    check(f"{tag} B: …and records to the Family card only; active account is still Main", st["active"] == "main" and st["f"] and st["f"].get("placedAt") and not (st["m"] and st["m"].get("placedAt")), st)
    # Filled on the F order opens the Family sheet context
    js(page, "()=>{ re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(300)
    js(page, "()=>{ document.querySelector('[data-re2-row=\"OOO\"] [data-re2-btn=\"fill\"]').click(); }"); page.wait_for_timeout(500)
    ctx = js(page, "()=>({kind: (typeof coreDlg !== 'undefined' && coreDlg) ? coreDlg.kind : null, id: (typeof coreDlg !== 'undefined' && coreDlg) ? coreDlg.id : null, active: acctActive})")
    check(f"{tag} B: Filled on the F row acts on that Family card (Main stays active)", ctx["id"] == "oF" and ctx["active"] == "main", ctx)
    js(page, "()=>{ try{ coreSheetClose(); }catch(e){} }")
    js(page, "()=>{ const B = getBook('fam'); B.trades = (B.trades || []).concat([{id:'tfut', sym:'S50', port:'satB', status:'open', qty:2, entry:900, mult:1, date:'2026-11-17'}]); saveBook('fam'); re1Cache = {}; todayRefresh(true); }"); page.wait_for_timeout(300)
    fut = js(page, "()=>{ const e = document.querySelector('[data-lr2-fut]'); return e ? [e.innerText, lr2Futures('fam')] : null; }")
    check(f"{tag} B: Family futures leverage shown when S50 / GO are open (notional ÷ equity)", fut and fut[0].endswith("×") and fut[1] > 0, fut)
    js(page, "()=>{ const B = getBook('fam'); B.trades = B.trades.filter(t=>t.id !== 'tfut'); saveBook('fam'); re1Cache = {}; todayRefresh(true); }")
    # Enter cap across both accounts (3 closest Ready + '+N ›')
    cs = {}
    for i in range(5):
        c = plan_card("E%d" % i, 100, 92, px=99 - i * 0.2, ready=True); c["acct"] = "main" if i % 2 == 0 else "fam"
        if i % 2: c["market"] = "TH"
        cs["e%d" % i] = c
    K.seed(page, cs)
    n = js(page, "()=>({rows:[...document.querySelectorAll('[data-re2-grp=\"enter\"]')].filter(r=>/^E\\d/.test(r.dataset.re2Row)).length, more:(document.querySelector('[data-re2-more]')||{}).innerText||'', accts:[...new Set([...document.querySelectorAll('[data-re2-grp=\"enter\"]')].map(r=>r.dataset.lr2Acct))]})")
    check(f"{tag} B: Enter cap works across accounts (3 rows + '+N ›', both accounts present)", n["rows"] <= 4 and "+" in n["more"] and len(n["accts"]) == 2, n)


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=cards_b())
    try:
        page.wait_for_timeout(300)
        part0(page, tag)
        partA(page, tag, w)
        partB(page, tag, w)
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
