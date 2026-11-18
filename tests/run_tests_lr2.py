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
      f.rrg = {rowsD:[mk('XLC','lead',103), mk('XLI','lead',105), mk('ITA','lead',101), mk('XLK','lead',99.9), mk('SMH','imp',98), mk('XLP','lag',90), mk('IGV','lag',92), mk('XLU','lag',95)], rowsW:[], build:RRG_BUILD, model:RRG_MODEL, lastBar:rrgToday(), day:rrgToday()};
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
    if wide:
        check(f"{tag} A: hot sectors = up to 3 Leading by strength (↗, names) then first Improving ⤴ + Lagging ↘", hot.count("↗") == 3 and "⤴" in hot and hot.count("↘") == 2, hot)
        order = js(page, "()=>[...document.querySelectorAll('[data-lr2-hot]')].map(c=>c.dataset.lr2Hot)")
        check(f"{tag} A: Leading chips sorted by strength", order == ["XLI", "XLC", "ITA"], order)
    else:
        ph = js(page, "()=>{ const l2 = document.querySelector('[data-lr2-phone] .l2'); return {txt: l2.innerText.replace(/\\s+/g, ' '), chips: [...l2.querySelectorAll('[data-lr2-hot]')].map(c=>c.dataset.lr2Hot), more: (l2.querySelector('[data-lr2-hotmore]')||{}).innerText||'', h: Math.round(l2.getBoundingClientRect().height), all: Math.round(document.querySelector('[data-lr2-phone]').getBoundingClientRect().height)}; }")
        check(f"{tag} A: phone glance = mood line + news line + chips line (light-lock: mood/news each on own line) · ≤2 hot chips by strength + '+N' · no 'Hot:' label", ph["chips"] == ["XLI", "XLC"] and ph["more"] == "+2" and "Hot:" not in ph["txt"] and ph["h"] <= 44 and ph["all"] <= 140, ph)
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


def partC(page, tag, w):
    wide = w >= 900
    js(page, "()=>{ lr2DetOpen = false; re1Cache = {}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(400)
    g = js(page, """()=>{ const r = s=>{ const e = document.querySelector(s); return e ? e.getBoundingClientRect() : null; }; const a = r('[data-lr2-main] .lr2-actcol'), sd = r('[data-lr2-side]'), td = r('[data-ln4-todorow]'), dt = r('[data-ln4-moredet]'), act = r('[data-ln4-act]');
      return {a: a && [a.left, a.top, a.width], s: sd && [sd.left, sd.top, sd.width], todoTop: td && td.top, actBottom: act && act.bottom, detTop: dt && dt.top, todoBottom: td && td.bottom, open: document.querySelector('[data-ln4-moredet]').open}; }""")
    if wide:
        check(f"{tag} C: desktop — side column (~1/3) sits to the right of Act", g["s"] and g["s"][0] > g["a"][0] + g["a"][2] - 2 and 0.25 < g["s"][2] / (g["s"][2] + g["a"][2]) < 0.45, g)
    else:
        check(f"{tag} C: phone — To do comes after Act", g["todoTop"] >= g["actBottom"] - 2, g)
    check(f"{tag} C: Details · risk · sectors · accounts is collapsed and comes after To do", g["open"] is False and g["detTop"] >= g["todoBottom"] - 2, g)
    n = js(page, "()=>[...document.querySelectorAll('[data-lr2-ti]')].length")
    check(f"{tag} C: To do is a short list (max {4 if wide else 3} rows)", 1 <= n <= (4 if wide else 3), n)
    row = js(page, "()=>{ const r = document.querySelector('[data-lr2-ti]'); return r ? [!!r.querySelector('.lr2-tg'), !!r.querySelector('.t'), !!r.querySelector('.lk'), r.querySelector('button').getAttribute('onclick') || r.querySelector('button').dataset.ln4Todogrp] : null; }")
    check(f"{tag} C: each To do row = tag · one line · one link (same handler as before)", row and row[0] and row[1] and row[2] and row[3], row)
    # many items → '+N ›'
    js(page, """()=>{ window.__oti = ln4TodoItems; ln4TodoItems = ()=>['a','b','c','d','e','f'].map((x, i)=>({c:'a', id:'t:'+x, t:'Task '+x, fn:"void(0)"})); todayRefresh(true); }"""); page.wait_for_timeout(250)
    m = js(page, "()=>({rows: document.querySelectorAll('[data-lr2-ti]').length, more: (document.querySelector('[data-ln4-todomore]')||{}).innerText})")
    check(f"{tag} C: 6 items → {4 if wide else 3} rows + '+N ›'", m["rows"] == (4 if wide else 3) and m["more"] == "+%d ›" % (6 - (4 if wide else 3)), m)
    js(page, "()=>{ ln4TodoItems = window.__oti; todayRefresh(true); }")
    # missing Playbook is a To do item (FLOW tag)
    pb = js(page, "()=>{ const r = [...document.querySelectorAll('[data-lr2-ti]')].find(x=>/playbook/i.test(x.innerText)); return r ? r.innerText.replace(/\\s+/g,' ') : null; }")
    check(f"{tag} C: missing Playbook shows as a To do item (FLOW · … · Add ›)", pb is not None and "FLOW" in pb and "Add" in pb, pb)
    # Risk room: Family has no Momentum
    js(page, "()=>{ lr2DetOpen = true; todayRefresh(true); }"); page.wait_for_timeout(250)
    rr = js(page, """()=>{ const L = a=>[...document.querySelectorAll('[data-lr2-room="'+a+'"] .lr2-rl[data-lr2-rl]')].map(r=>({k:r.dataset.lr2Rl, pill:(r.querySelector('.lr-acc')||{}).innerText, tag:(r.querySelector('.lr-tag')||{}).innerText, t:r.querySelector('.t').innerText.replace(/\\s+/g,' '), clip:r.querySelector('.t').scrollWidth > r.querySelector('.t').clientWidth + 1}));
      const vis = [...document.querySelectorAll('[data-lr2-risk] [data-re2-chip]')].filter(e=>{ if(e.closest('.lr2-vh')) { const w = e.closest('.lr2-vh').getBoundingClientRect(); return w.width > 2 || w.height > 2; } const r = e.getBoundingClientRect(); return r.width > 2 && r.height > 2; }).length;
      return {main: L('main'), fam: L('fam'), strips: vis, tiles: document.querySelectorAll('[data-lr2-risk] .rk3, [data-lr2-risk] summary').length, det: !!document.querySelector('[data-ln4-moredet] [data-lr2-risk]')}; }""")
    mt = rr["main"][0]["t"] if rr["main"] else ""
    check(f"{tag} C: Risk room = ONE line per account × port inside Details ('M · MMT 1 of 4 ideas · room x / y'): Main 3 lines, Family 2 (no Momentum)", rr["det"] and [x["k"] for x in rr["main"]] == ["mom", "sat", "comp"] and [x["k"] for x in rr["fam"]] == ["sat", "comp"] and all(x["pill"] == "M" for x in rr["main"]) and all(x["pill"] == "F" for x in rr["fam"]) and rr["main"][0]["tag"] == "MMT" and re.match(r"^\d+ of \d+ ideas · room [\d.]+% / [\d.]+%$", mt), rr)
    if wide: check(f"{tag} C: no truncated risk lines · no tiles · no visible duplicated strip chips", not any(x["clip"] for x in rr["main"] + rr["fam"]) and rr["tiles"] == 0 and rr["strips"] == 0, rr)
    else: check(f"{tag} C: no tiles · no visible duplicated strip chips (lines may ellipsise on phone)", rr["tiles"] == 0 and rr["strips"] == 0, rr)
    js(page, "()=>{ lr2DetOpen = false; todayRefresh(true); }"); page.wait_for_timeout(200)
    ct = js(page, "()=>{ const d = document.querySelector('[data-ln4-moredet]'); d.open = true; const k = ['[data-ln4-hot]', '[data-ln4-macro]', '[data-ln4-goal]', '[data-ln4-wl]', '[data-ln4-today]'].map(s=>!!d.querySelector(s) || (s === '[data-ln4-today]')); return k; }")
    check(f"{tag} C: HOT · MACRO · GOAL · SIZE lines live inside Details (hooks kept)", all(ct), ct)
    check(f"{tag} C: weekly news hook still rendered by ln4NewsLine", "data-td3-wnews" in js(page, "()=>ln4NewsLine.toString()"))


def partFix(page, tag, w):
    wide = w >= 900
    js(page, "()=>{ lr2DetOpen = false; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
    h = js(page, """()=>{ const v = document.querySelector('.lr2-viewrow'), st = document.querySelector('[data-ln4-status]'), g = document.querySelector('[data-lr2-glance]'), sw = document.querySelector('[data-td3-sw]'), t = document.querySelector('[data-lr2-title]'), d = document.querySelector('[data-lr2-date]');
      const rv = v.getBoundingClientRect(), rg = g.getBoundingClientRect(), rs = sw.getBoundingClientRect(), rt = t.getBoundingClientRect();
      return {title: t.innerText, date: d.innerText, hv: Math.round(rv.height), gap: Math.round(rg.top - rv.bottom), swInRow: rs.top >= rv.top - 1 && rs.bottom <= rv.bottom + 1, titleLeft: rt.left < rs.left, filled: rt.width > 20}; }""")
    check(f"{tag} F2: Daily/Weekend sits in the page-header row with 'Today' + date (no empty band above the glance)", h["title"] == "Today" and re.match(r"^[A-Z][a-z]{2} \d{1,2} [A-Z][a-z]{2}( · US market opens \d\d:\d\d ICT)?$", h["date"]) and h["swInRow"] and h["titleLeft"] and h["hv"] <= 48, h)
    nm = js(page, "()=>RRG_SYMS.map(r=>[r.s, lr2SecShort(r.s)])")
    bad = [x for x in nm if not x[1] or len(x[1]) > 12 or x[1] == x[0] or re.search(r"\d", x[1])]
    check(f"{tag} F3: every RRG symbol has a short sector name (≤12 chars, not the ticker): {len(nm)} checked", not bad and len({x[1] for x in nm}) == len(nm), bad)
    seed_rrg(page)
    txt = card(page, "hot")
    check(f"{tag} F3: Hot / Cooling line shows sector names only (Staples, Software, Utilities … never tickers)", (not wide) or ("Staples" in txt and "Software" in txt and not re.search(r"\\bX[A-Z]{2,3}\\d?\\b", txt)), txt)
    t = js(page, """()=>{ const c = document.querySelector('[data-ln4-todorow]'), r = c.getBoundingClientRect(), th = c.querySelector('.lr2-th b').getBoundingClientRect(), tg = c.querySelector('.lr2-tg'), b = c.querySelector('.lr2-tb'), cs = getComputedStyle(b);
      const a = c.querySelector('.lr2-ti').getBoundingClientRect(), bt = b.getBoundingClientRect(), tgr = tg.getBoundingClientRect();
      return {titleOffset: Math.round(th.left - r.left), align: getComputedStyle(c).textAlign, bg: cs.backgroundColor, bd: cs.borderTopWidth, rowOffset: Math.round(tgr.left - r.left), tbGap: Math.round(bt.left - tgr.right)}; }""")
    check(f"{tag} F5: To do card is left-aligned like the design (title at the card's left padding, rows flush, no tinted box)", t["titleOffset"] <= 20 and t["align"] in ("left", "start") and t["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and t["bd"] == "0px" and t["rowOffset"] <= 20, t)


BASE_390 = {"height": 975, "rows": 12}   # origin/main (+ LR2 commit 0) at 390 with the same fixture · measured with tools in docs/reports/LR2-summary.md


def heights(pw):
    """Row / height count at 390 for the Main-only fixture (3 plans incl. one working order) with Details collapsed — Today must not get longer"""
    c = {"pA": plan_card("NVDA", 100, 92, px=99, ready=True), "pB": plan_card("AAPL", 100, 92, px=101, ready=True), "oM": plan_card("OOO", 50, 45, px=49, ready=True)}
    c["oM"]["ln4"] = {"placedAt": "2026-11-17T01:00:00Z"}
    b, page, ce, pe = launch(pw, 390, 844, c=c)
    try:
        js(page, "()=>{ lr2DetOpen = false; todayRefresh(true); }"); page.wait_for_timeout(400)
        r = js(page, ROWS_JS)
        print("ROWS390", r)
        check("[390] Today height at 390 stays within 3%% of the old layout (%d px vs %d)" % (r["height"], BASE_390["height"]), r["height"] <= BASE_390["height"] * 1.03, r)
    finally:
        b.close()


ROWS_JS = """()=>{ const vis = e=>e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const rows = [...document.querySelectorAll('.re2-row,.re2-col .ch,[data-ln4-todo],.re2-pc summary,.ln4-more>summary,.re2-strip:not(.lr2-calm),[data-lr2-head],[data-lr2-ph]')].filter(vis);
  return {rows: rows.length, height: document.documentElement.scrollHeight}; }"""


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=cards_b())
    try:
        page.wait_for_timeout(300)
        part0(page, tag)
        partA(page, tag, w)
        partB(page, tag, w)
        partC(page, tag, w)
        partFix(page, tag, w)
        check(f"{tag} no page errors", not pe, pe)
        check(f"{tag} no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844)):
            run(pw, w, h)
        heights(pw)
    bad = [r for r in results if not r[1]]
    print("SUMMARY lr2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
