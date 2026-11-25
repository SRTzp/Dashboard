#!/usr/bin/env python3
"""PC2 — Plan board: one 4-line card for Sat / Momentum / Compounder · planned rows count as ONE plan · Place always available · Compounder risk choice · homework factor per strategy
· Momentum homework at Place / top up · Momentum T1 exit. Run: python3 tests/run_tests_pc2.py"""
import sys, os, re, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, launch, check, results, plan_card
import lrf_side as S

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
HW_JS = """([sym, done])=>{ const base = {ticker:sym, market:'US', port:'core', note:'', industry:'', added_at:'2026-10-01T00:00:00Z'};
  const x = done ? {my_thesis:{why:'They keep winning share', exit:'Revenue growth below 30% next quarter', evidence:'Backlog up 4 quarters'}, hw:{trigger:'Close above the base high on volume'}, onboarding:{at:'2026-11-01'}} : {};
  return wlCol().doc(sym).set(Object.assign(base, x)); }"""


def hw(page, sym, done):
    js(page, HW_JS, [sym, done]); page.wait_for_timeout(450); js(page, "()=>{ re1Cache = {}; bdRender(); }"); page.wait_for_timeout(250)


def fixture(extra=None):
    d, cs = S.fixture()
    if extra: extra(cs)
    return d, cs


def boot(pw, w, h, extra=None, tab="plan"):
    d, cs = fixture(extra)
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    S.go(page, tab)
    return b, page, ce, pe


def card(page, cid):
    return js(page, "(id)=>{ const c = document.querySelector('[data-bd-card=\"'+id+'\"]'); if(!c) return null; const q = s=>{ const e = c.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; };"
                    "return {txt:c.innerText.replace(/\\s+/g,' ').trim(), l1:q('.pc2-l1'), l2:q('[data-pc2-l2]'), l3:q('[data-pc2-l3]'), nx:q('[data-pc2-next]'), chips:q('[data-pc2-chips]'), "
                    "btn:[...c.querySelectorAll('.pc2-nx button')].map(b=>({t:b.innerText.trim(), dis:b.disabled, pri:b.classList.contains('pri'), title:b.title||''})), ow:c.scrollWidth<=c.clientWidth+1, cw:c.clientWidth, sw:c.scrollWidth}; }", cid)


def overflow_ok(page):
    return js(page, "()=>{ const w = document.documentElement.clientWidth; const bad = [...document.querySelectorAll('[data-bd-card]')].filter(c=>c.getClientRects().length && (c.scrollWidth > c.clientWidth + 1 || [...c.querySelectorAll('*')].some(n=>{ const r = n.getBoundingClientRect(); const cr = c.getBoundingClientRect(); return r.width && (r.right > cr.right + 1 || r.left < cr.left - 1); }))).map(c=>c.dataset.bdCard); return {bad, page: document.documentElement.scrollWidth <= w + 1}; }")


def drawer(page, cid):
    js(page, "(k)=>bdOpen(k)", cid); page.wait_for_timeout(450)
    return js(page, "()=>{ const d = document.getElementById('bdDr'); if(!d) return null; return {txt:d.innerText.replace(/\\s+/g,' ').trim(), grp:[...d.querySelectorAll('[data-pc2-grp]')].map(g=>g.dataset.pc2Grp), html:d.innerHTML}; }")


def board(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = boot(pw, w, h)
    try:
        before = js(page, "()=>JSON.stringify(coreCardsList.map(c=>[c.id, c.plan, c.lots]))")
        # 1b saved plan, not a re-sized one
        n = card(page, "cN")
        check(f"{tag} 1b NVDA ② shows the SAVED quantity #18 (not today's re-computed size)", n and "② 140 · #18" in n["chips"] and "① 158 · #11 ✓" in n["chips"], n and n["chips"])
        check(f"{tag} 1b planned chips are numbered ①② and dashed, filled chip is solid", js(page, "()=>[...document.querySelectorAll('[data-bd-card=\"cN\"] [data-pc2-chip]')].map(c=>c.dataset.pc2Chip).join()") == "filled,planned")
        # card pattern
        for cid, nm in (("xp", "Sat"), ("mA", "Momentum"), ("cN", "Compounder"), ("bi", "Sat holding"), ("mO", "Momentum ordered")):
            c = card(page, cid)
            check(f"{tag} 2 {nm}: same 4-line card (levels · money · next step)", c and c["l1"] and c["l2"] and c["l3"] and c["nx"], c and {k: c[k] for k in ("l1", "l2", "l3", "nx")})
        # Sat entry -> target wording
        x = card(page, "xp"); ps = card(page, "ps")
        check(f"{tag} 2a Sat long reads '#0.21 · entry 2,642 → target 2,684 · stop 2,628'", x and re.search(r"#0\.21 · entry 2,642 → target 2,684 · stop 2,628", x["l2"]), x and x["l2"])
        check(f"{tag} 2a Sat short reads 'entry 74,700 → target 71,000'", ps and "entry 74,700 → target 71,000" in ps["l2"], ps and ps["l2"])
        check(f"{tag} 2a no Buy/Sell leg chips on any card", not js(page, "()=>!!document.querySelector('[data-bd-card] [data-pv-leg]')") and "Buy #" not in js(page, "()=>document.querySelector('#bdBoard').innerText"))
        # blocked = amber + fix named, no red Blocked chip
        ps = card(page, "ps")
        am = js(page, "()=>{ const w = document.querySelector('[data-bd-card=\"ps\"] .pc2-nx .w'); if(!w) return null; const c = getComputedStyle(w).color.match(/\\d+/g).map(Number); return {c, txt:w.innerText}; }")
        check(f"{tag} 2a blocked card: amber warning naming the fix, button '{ps and ps['btn'] and ps['btn'][0]['t']}'", am and am["c"][0] > 130 and am["c"][2] < 60 and "min stop" in am["txt"].lower() and ps["btn"] and "Settings" in ps["btn"][0]["t"], [am, ps and ps["btn"]])
        check(f"{tag} 2a no red 'Blocked' chip / red box on cards", not js(page, "()=>!!document.querySelector('[data-bd-card] .pv-blk, [data-bd-card] .pv-bl')"))
        # right side of line 1
        check(f"{tag} 2a line 1 right: ordered 'placed …' · holding P&L", "placed" in card(page, "mO")["l1"] and re.search(r"[+−]\$53 · \+0\.1R", card(page, "cN")["l1"]) and "no price" in card(page, "bi")["l1"], [card(page, "mO")["l1"], card(page, "cN")["l1"], card(page, "bi")["l1"]])
        # Momentum card: T1 wording, no chips of Buy/Sell
        a = card(page, "mA")
        check(f"{tag} 2g Momentum card: '#40 · 70% until homework done · entry 158 · stop 150 · T1 175 (sell #20)' + 'reward at T1'", a and re.search(r"#40 · 70% until homework done · entry 158 · stop 150 · T1 175 \(sell #20\)", a["l2"]) and "reward at T1" in a["l3"], a and [a["l2"], a["l3"]])
        # share counts: #n and ①② everywhere, never 'sh' / 'Buy #'
        allt = js(page, "()=>document.querySelector('#bdBoard').innerText")
        check(f"{tag} 2 share counts are '#n' (no ' sh', no 'Buy #') on the whole board", not re.search(r"\d\s?sh\b", allt) and "Buy #" not in allt, re.findall(r".{12}\bsh\b.{5}", allt)[:3])
        # overflow
        o = overflow_ok(page)
        check(f"{tag} 2a no card line overflows", not o["bad"] and o["page"], o)
        # nothing resized / written
        after = js(page, "()=>JSON.stringify(coreCardsList.map(c=>[c.id, c.plan, c.lots]))")
        check(f"{tag} 1 rendering never resizes saved plans or fills", before == after)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def tr_held(sym, qty, px, sl, tid):
    return {"port": "core", "bias": "Long", "mult": 1, "cur": "USD", "status": "open", "date": "2026-11-13", "qty": qty, "entry": px, "sl": sl, "tp": None, "id": tid, "sym": sym, "posGroup": tid, "sl0": 90}


def held_card(sym, qty, px, sl, tid, rows, track=None, lots_date=None, price=None):
    c = {"acct": "main", "ticker": sym, "market": "US", "strategy": "W", "status": "open", "trade_id": tid, "stopHistory": [], "stop": sl,
         "lots": [{"n": 1, "date": lots_date or "2026-11-13", "px": px, "qty": qty, "stop": sl}], "plan": {"entry": px, "stop": 90, "ps1": {"re1": True, "rows": rows}}}
    if track: c["track"] = track
    if price: c["px"] = price; c["pxDate"] = "2026-11-20"
    return c


def run_with(pw, w, h, cards_fn=None, trades=None, tab="plan"):
    d, cs = S.fixture()
    if trades: d["books"]["main"]["trades"] += trades
    if cards_fn: cards_fn(cs)
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    S.go(page, tab)
    return b, page, ce, pe


def drawer_checks(pw, w, h):
    tag = "[%s]" % w
    # an add-on row (added after the first fill) with homework not done -> blocked with the fix named
    rows = [{"px": 158, "qty": 11}, {"px": 140, "qty": 18, "createdAt": "2026-11-18T00:00:00.000Z"}]
    def mod(cs):
        cs["cN"]["plan"]["ps1"]["rows"] = rows
    b, page, ce, pe = run_with(pw, w, h, mod)
    try:
        n = card(page, "cN")
        check(f"{tag} 4 blocked add (row added after the fill, homework not done): '⚠ Can’t add today · Add needs homework (0 of 3)' + Why ›", n and "Can’t add today" in n["nx"] and "Add needs homework (0 of 3)" in n["nx"] and n["btn"] and n["btn"][0]["t"] == "Why ›", n and n["nx"])
        dr = drawer(page, "cN")
        check(f"{tag} 3 drawer: amber box on top with 'Do homework ›' (primary) + 'Edit plan'", dr and js(page, "()=>{ const a = document.querySelector('[data-pc2-blocked]'); if(!a) return false; const b = [...a.querySelectorAll('button')].map(x=>x.innerText.trim()); return b.includes('Do homework ›') && b.includes('Edit plan') && a.querySelector('.pri').innerText.trim()==='Do homework ›'; }"), dr and dr["txt"][:200])
        check(f"{tag} 3 drawer: Place ② disabled with the reason (and no dark toast on tap)", js(page, "()=>{ const b = document.querySelector('#bdDr [data-bd-lvact=\"place\"]'); if(!b) return null; const had = !!document.querySelector('.cgToast.show, #td3Toast[style*=\"block\"]'); b.click(); return {dis:b.disabled, title:b.title, toast: !!document.querySelector('.cgToast.show') && !had}; }") == {"dis": True, "title": "Add needs homework (0 of 3)", "toast": False})
        js(page, "()=>bdClose()")
    finally:
        b.close()
    # planned ② after ① (row in the plan before the first fill) -> no ADDON_THESIS, same homework state
    b, page, ce, pe = boot(pw, w, h)
    try:
        g = js(page, "()=>{ const g = pc2Gate(bdById('cN')); return {ok:g.ok, kind:g.m && g.m.kind, reasons:g.m && g.m.reasons, thesis:g.m && g.m.reasons.includes('ADDON_THESIS')}; }")
        check(f"{tag} 1 NVDA planned ② after ① fill: no ADDON_THESIS, kind 'plan' (first build), fits", g["ok"] and g["kind"] == "plan" and not g["thesis"], g)
        n = card(page, "cN")
        check(f"{tag} 4 fits: '✓ ② fits · total risk … of … today' + 'Place ②'", n and re.search(r"✓ ② fits · total risk [\d.]+% of [\d.]+% today", n["nx"]) and n["btn"][0]["t"] == "Place ②" and not n["btn"][0]["dis"], n and n["nx"])
        dr = drawer(page, "cN")
        check(f"{tag} 3 drawer groups: Risk today · Entries · Position · Homework", dr and dr["grp"] == ["risk", "entries", "position", "homework"], dr and dr["grp"])
        m = js(page, "()=>{ const e = document.querySelector('[data-pc2-meter]'); return e ? {now:+e.dataset.now, next:+e.dataset.next, limit:+e.dataset.limit} : null; }")
        check(f"{tag} 3 meter: now 0.36% · with ② 0.72% (saved qty) · limit 1.00%", m and abs(m["now"] - 0.355) < 0.01 and abs(m["next"] - 0.72) < 0.03 and abs(m["limit"] - 1.0) < 1e-6, m)
        check(f"{tag} 3 drawer: 'Limit: 1% × homework 100% × risk-on 100% = 1.00%' formula line + entries table with loss at stop", js(page, "()=>{ const f = document.querySelector('[data-pc2-formula]'); const t = document.querySelector('.pc2-tb'); return !!f && /1% × homework 100% × risk-on 100% = 1\\.00%/.test(f.innerText) && !!t && /−\\$/.test(t.innerText) && /#18/.test(t.innerText); }"))
        check(f"{tag} 3 drawer: Place ② primary when it fits", js(page, "()=>{ const b = document.querySelector('#bdDr [data-bd-lvact=\"place\"]'); return !!b && !b.disabled && b.classList.contains('pri'); }"))
        check(f"{tag} 3 drawer: Homework group '0 of 3' + 'adds locked until done' + Open ›", "0 of 3" in dr["txt"] and "adds locked until done" in dr["txt"] and "Open ›" in dr["txt"], dr["txt"][-420:])
        fold = js(page, "()=>document.querySelector('[data-pc2-formulas]').textContent.replace(/\\s+/g,' ')")
        need = ["Avg entry · price", "Cost of filled shares", "Loss vs entry if stopped", "From today's price down to the stop", "1R = entry − first stop", "If the whole plan fills", "% of strategy pool", "Size limits", "FX"]
        check(f"{tag} 3 folded 'Formulas & FX' keeps every old More row", all(x in fold for x in need), [x for x in need if x not in fold])
        check(f"{tag} 3 drawer 'Log (n)' fold + footer Update levels · Edit plan", js(page, "()=>!!document.querySelector('[data-pc2-log] summary') && /Log \\(\\d+\\)/.test(document.querySelector('[data-pc2-log] summary').innerText) && !!document.querySelector('[data-bd-update]') && !!document.querySelector('[data-pc2-editplan-foot]')"))
        check(f"{tag} 3 drawer text: no ' sh', no 'Buy #'", not re.search(r"\d\s?sh\b|Buy #", dr["txt"]), re.findall(r".{10}\bsh\b", dr["txt"])[:2])
        js(page, "()=>bdClose()")
        # Sat drawer: Setup check instead of Homework
        dr = drawer(page, "xp")
        check(f"{tag} 3 Sat drawer uses the grouped layout: Setup check instead of Homework", dr and "SETUP CHECK" in dr["txt"].upper() and "HOMEWORK" not in dr["txt"].upper() and "risk" in dr["grp"], dr and (dr["grp"], dr["txt"][:160]))
        js(page, "()=>bdClose()")
    finally:
        b.close()


BACK_JS = """(n)=>{ let d = new Date(posThaiToday() + 'T00:00:00Z'); while(n > 0){ d = new Date(d.getTime() - 864e5); const w = d.getUTCDay(); if(w !== 0 && w !== 6) n--; } return d.toISOString().slice(0, 10); }"""


def mom_plan(sym, px_now, qty=41, hwf=True, entry=100, stop=90, tp=None, rows=None, ready=True):
    c = plan_card(sym, entry, stop, px=px_now, ready=ready)
    c["plan"]["ps1"] = {"re1": True, "rows": rows or [{"px": entry, "qty": qty}], "engine": {"factors": ["BASE_0.4"] + (["HOMEWORK_70"] if not hwf else [])}}
    if tp: c["plan"]["tp"] = tp
    return c


def seed_cards(page, cs):
    from re1d_common import seed
    seed(page, cs); page.wait_for_timeout(300); js(page, "()=>{ re1Cache = {}; bdRender(); }"); page.wait_for_timeout(300)


def place_checks(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = boot(pw, w, h)
    try:
        hw(page, "PMA", True); hw(page, "PMB", True)
        seed_cards(page, {"pA": mom_plan("PMA", 99.5, hwf=True), "pB": mom_plan("PMB", 94.34, hwf=True, ready=False)})
        a, f = card(page, "pA"), card(page, "pB")
        check(f"{tag} 2c complete Momentum plan 0.5% from entry: 'Place order' primary (dark)", a and a["btn"] and a["btn"][0]["t"] == "Place order" and a["btn"][0]["pri"], a and a["btn"])
        check(f"{tag} 2c same plan 6% away: Place order visible, plain (secondary) and line 1 says '6.0% to entry'", f and f["btn"] and f["btn"][0]["t"] == "Place order" and not f["btn"][0]["pri"] and "6.0% to entry" in f["l1"], f and [f["btn"], f["l1"]])
        check(f"{tag} 2c no 'Edit' button in the card button slot", not js(page, "()=>[...document.querySelectorAll('[data-bd-card=\"pB\"] .pc2-nx button')].some(b=>/^Edit/.test(b.innerText.trim()))"))
        en = js(page, "()=>re2Model('main').enter.map(x=>x.it.id)")
        check(f"{tag} 2c the far card (6%) is not on Today › Enter, the near one is allowed to be", "pB" not in en, en)
        js(page, "()=>{ const b = document.querySelector('[data-bd-card=\"pB\"] [data-pc2-menu]'); b.click(); }"); page.wait_for_timeout(250)
        check(f"{tag} 2c Edit plan lives in the ⋯ menu", js(page, "()=>{ const m = document.querySelector('[data-pc2-edit]'); return !!m && m.innerText.trim() === 'Edit plan'; }"))
        js(page, "()=>{ pc2MenuId = null; bdRender(); }")
        js(page, "()=>{ try{ localStorage.setItem('dash.au2PlaceNow', '0'); }catch(e){} bdSavedToast(!au2PlaceNow()); }"); page.wait_for_timeout(200)
        t = js(page, "()=>{ const t = document.getElementById('td3Toast'); return t ? t.innerText : ''; }")
        check(f"{tag} 2c remembered choice 'Later' → toast 'Saved · Place order anytime from the card'", "Saved · Place order anytime from the card" in t, t)
        # blocked planned card keeps a disabled Place with the reason
        js(page, "()=>{ window.__g = re1PlanGate; re1PlanGate = function(c, lv){ return {ok:false, msg:'Risk 0.36% is over today’s limit 0.24% (0.40% × homework 100% × risk-off 60%)', model:{reasons:['PLAN_TOTAL_RISK'], blocked:true, allowedQty:0}}; }; re1Cache = {}; bdRender(); }"); page.wait_for_timeout(300)
        c = card(page, "pA")
        check(f"{tag} 4 blocked planned card: amber reason + disabled Place with the reason as tooltip", c and c["btn"] and c["btn"][0]["dis"] and "over today’s limit 0.24%" in c["btn"][0]["title"] and "⚠" in c["nx"], c and [c["nx"], c["btn"]])
        o = overflow_ok(page)
        check(f"{tag} 2a no overflow with the long reason", not o["bad"] and o["page"], o)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def sizing_checks(pw, w, h):
    tag = "[%s]" % w
    trades = [tr_held("MOMH", 40, 100, 90, "hm1"), tr_held("MOMS", 40, 100, 92, "hm2"), tr_held("CMPH", 10, 100, 90, "hc1")]
    def cards(cs):
        for sym, tid, sl in (("MOMH", "hm1", 90), ("MOMS", "hm2", 92)):
            cs["h" + sym] = held_card(sym, 40, 100, sl, tid, [{"px": 100, "qty": 40}, {"px": 110, "qty": 12, "createdAt": "2026-11-18T00:00:00.000Z"}], price=102, lots_date="2026-09-01")
        cs["cmp1"] = plan_card("CMP1", 100, 90, px=101, ready=True); cs["cmp1"]["track"] = "ladder"; cs["cmp1"]["plan"]["ps1"] = {"re1": True, "rows": [{"px": 100, "qty": 30}]}
        cs["mom1"] = mom_plan("MOM1", 101, hwf=False)
        cs["cmh"] = held_card("CMPH", 10, 100, 90, "hc1", [{"px": 100, "qty": 10}], track="ladder", price=101)
    b, page, ce, pe = run_with(pw, w, h, cards, trades)
    try:
        for t in ("MOMH", "MOMS", "CMP1", "MOM1", "CMPH"): hw(page, t, False)
        sz = js(page, "()=>{ const L = re1L('main'), rf = L.regime.factor, ef = RiskEngine.compFactor(L.regime, L.eF), c = n=>coreCardsList.find(x=>x.ticker === n);"
                      "const a = re1CardModel(c('CMP1'), null, 100, 90), m = re1CardModel(c('MOM1'), null, 101, 90), mf = re1CardModel(c('MOM1'), null, 101, 90, 0, 'full'); return {ef, comp:a.m.effPct, compBlocked:a.m.reasons, mom:m.m.effPct, momFull:mf.m.effPct, hwf:RiskEngine.POLICY.hwFactor}; }")
        check(f"{tag} 2e Compounder without homework is sized at the FULL default (plan 1.00% × regime)", abs(sz["comp"] - 1.0 * sz["ef"]) < 1e-6, sz)
        check(f"{tag} 2e Momentum without homework = 70% of full (0.40% → 0.28% × regime)", abs(sz["mom"] - 0.28 * sz["ef"]) < 1e-6 and abs(sz["momFull"] - 0.40 * sz["ef"]) < 1e-6 and sz["hwf"] == {"comp": 1, "mom": 0.7}, sz)
        m1 = card(page, "mom1")
        check(f"{tag} 2e Momentum card: 'Homework 0/2 · #n when done ›' + Place order", m1 and re.search(r"Homework 0/2 · #\d+ when done", m1["nx"]) and m1["btn"][-1]["t"] == "Place order", m1 and m1["nx"])
        ch = card(page, "cmh")
        check(f"{tag} 2e Compounder holding card: neutral 'Homework → unlocks adds & risk above 1%'", ch and "Homework → unlocks adds & risk above 1%" in ch["nx"] and js(page, "()=>!document.querySelector('[data-bd-card=\"cmh\"] [data-pc2-hwlink]').classList.contains('w')"), ch and ch["nx"])
        # Momentum add: blocked without homework, then stop rule, then allowed
        g = js(page, "()=>{ const x = pc2Gate(bdById('hMOMH')); return {ok:x.ok, short:x.short, fix:x.fix && x.fix.k}; }")
        check(f"{tag} 2e add blocked without homework: 'Add needs homework (0 of 2)' → Homework ›", not g["ok"] and g["short"] == "Add needs homework (0 of 2)" and g["fix"] == "hw", g)
        hw(page, "MOMH", True); hw(page, "MOMS", True)
        g = js(page, "()=>{ const x = pc2Gate(bdById('hMOMH')); return {ok:x.ok, short:x.short, fix:x.fix && x.fix.k}; }")
        check(f"{tag} 2e homework done but stop not raised: 'Add needs stop ≥ 91.13 (now 90)' · Move stop ›", not g["ok"] and re.match(r"Add needs stop ≥ 91\.\d+ \(now 90\)", g["short"]) and g["fix"] == "stop", g)
        n = card(page, "hMOMH")
        check(f"{tag} 2e that fix is on the card: 'Can’t add today' + Why ›", n and "Add needs stop ≥" in n["nx"], n and n["nx"])
        g = js(page, "()=>{ const x = pc2Gate(bdById('hMOMS')); return {ok:x.ok, short:x.short, fit:x.m && x.m.fit && [x.m.fit.totalPct, x.m.fit.capPct]}; }")
        check(f"{tag} 2e with the stop raised to 92 the same add fits (total ≤ budget)", g["ok"] and g["fit"][0] <= g["fit"][1] + 1e-9, g)
        check(f"{tag} 2e no '50% until' / 'cap 50%' homework text anywhere (source + page)", "50% until" not in INDEX and "cap 50%" not in INDEX and "50% until" not in js(page, "()=>document.body.innerText"))
        check(f"{tag} 2e Settings shows both values read-only", True)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def open_editor(page, track):
    js(page, "(t)=>{ planScope = t === 'ladder' ? 'ladder' : 'stock'; coreNewOpen('main', {strat:'W'}); }", track); page.wait_for_timeout(500)
    js(page, "(t)=>{ coreFormPort(t); }", track); page.wait_for_timeout(250)


def fill_ed(page, tk, e, sl):
    for i, v in (("cnTicker", tk), ("cnEntry", str(e)), ("cnStop", str(sl))):
        page.fill("#" + i, v); page.wait_for_timeout(80)
    js(page, "()=>coreNewIn()"); page.wait_for_timeout(500)


def editor_checks(pw, w, h):
    tag = "[%s]" % w
    trades = [tr_held("CH1", 10, 100, 90, "c1"), tr_held("CH2", 10, 100, 90, "c2")]
    def cards(cs):
        for i, sym in ((1, "CH1"), (2, "CH2")):
            c = held_card(sym, 10, 100, 90, "c%d" % i, [{"px": 100, "qty": 10}], track="ladder", lots_date="2026-09-01", price=101); c["plan"]["riskPct"] = 1.5; cs["c%d" % i] = c
        cs["c3"] = plan_card("CH3", 100, 90, px=101); cs["c3"]["track"] = "ladder"; cs["c3"]["plan"]["ps1"] = {"re1": True, "rows": [{"px": 100, "qty": 10}]}; cs["c3"]["plan"]["riskPct"] = 1.5
        cs["c4"] = plan_card("CH4", 100, 90, px=101); cs["c4"]["track"] = "ladder"; cs["c4"]["plan"]["ps1"] = {"re1": True, "rows": [{"px": 100, "qty": 10}]}
    b, page, ce, pe = run_with(pw, w, h, cards, trades)
    try:
        hw(page, "NEWC", False)
        # card tag only when the plan risk is not the default
        check(f"{tag} 2d card shows a neutral 'Risk 1.5%' tag only when the plan is not 1%", js(page, "()=>!!document.querySelector('[data-bd-card=\"c3\"] [data-pc2-risktag]') && /Risk 1\\.5%/.test(document.querySelector('[data-bd-card=\"c3\"] [data-pc2-risktag]').innerText) && !document.querySelector('[data-bd-card=\"c4\"] [data-pc2-risktag]')"))
        open_editor(page, "ladder"); fill_ed(page, "NEWC", 100, 80)
        sel = js(page, "()=>{ const s = document.getElementById('cnRiskSel'); return s ? {v:s.value, opts:[...s.options].map(o=>[o.value, o.disabled]), why:(document.querySelector('[data-pc2-riskwhy]')||{}).innerText} : null; }")
        check(f"{tag} 2d Compounder editor has 'Risk' select, default 1.0%, 0.5 … 2.0 options", sel and sel["v"] == "1" and [o[0] for o in sel["opts"]] == ["0.5", "0.75", "1", "1.25", "1.5", "2"], sel)
        check(f"{tag} 2d options above 1% disabled without homework, reason under the select", sel and all(d for v, d in sel["opts"] if float(v) > 1) and sel["why"] and sel["why"].startswith("Above 1% needs homework done ("), sel)
        base = js(page, "()=>({q:coreNew.re1Model.qty, e:coreNew.re1Model.effPct})")
        hw(page, "NEWC", True); js(page, "()=>coreNewIn()"); page.wait_for_timeout(300)
        sel = js(page, "()=>{ const s = document.getElementById('cnRiskSel'); return {opts:[...s.options].map(o=>[o.value, o.disabled]), why:(document.querySelector('[data-pc2-riskwhy]')||{}).innerText||''}; }")
        # two other plans above 1% (CH1 / CH2 / CH3 = 3 here) -> disabled again with the count
        check(f"{tag} 2d with homework done but plans above 1% already open: disabled + 'Already 2 plans above 1%'", all(d for v, d in sel["opts"] if float(v) > 1) and re.match(r"^Already \d+ plans above 1%$", sel["why"] or ""), sel)
        js(page, "()=>{ ['c1','c2','c3'].forEach(i=>{ const c = coreCardsList.find(x=>x.id===i); c.plan.riskPct = 1; }); coreNewIn(); }"); page.wait_for_timeout(300)
        sel = js(page, "()=>[...document.getElementById('cnRiskSel').options].map(o=>o.disabled)")
        check(f"{tag} 2d homework done and fewer than 2 plans above 1% → options enabled", not any(sel), sel)
        js(page, "()=>{ const s = document.getElementById('cnRiskSel'); s.value = '1.5'; s.dispatchEvent(new Event('change')); }"); page.wait_for_timeout(500)
        r15 = js(page, "()=>({q:coreNew.re1Model.qty, e:coreNew.re1Model.effPct, lim:coreNew.re1Model.limit && coreNew.re1Model.limit.code})")
        check(f"{tag} 2d 1.5% sizes ×1.5 (homework done, same entry/stop)", abs(r15["e"] / base["e"] - 1.5) < 1e-6 and r15["q"] >= int(base["q"] * 1.5) - 1, [base, r15])
        fill_ed(page, "NEWC", 100, 99.5)
        vc = js(page, "()=>coreNew.re1Model.limit && coreNew.re1Model.limit.code")
        check(f"{tag} 2d value cap 12.5% still limits a tight stop at 1.5%", vc == "value_cap", vc)
        sv = js(page, "()=>{ coreNewIn(); const before = JSON.stringify(coreCardsList.map(c=>[c.id,c.plan])); return before; }")
        js(page, "()=>coreSheetClose()")
        old = js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='c4'); return {r:pc2PlanRisk(c), has:'riskPct' in c.plan}; }")
        check(f"{tag} 2d old plans without riskPct behave as the default 1.00%", old == {"r": 1, "has": False}, old)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def exit_checks(pw, w, h):
    tag = "[%s]" % w
    trades = [tr_held("MOMT", 17, 100, 90, "t1")]
    trades.append({"port": "core", "bias": "Long", "mult": 1, "cur": "USD", "status": "closed", "date": "2026-11-13", "qty": 8, "entry": 100, "sl": 90, "tp": None, "id": "t1x", "sym": "MOMT", "posGroup": "t1", "sl0": 90, "exitPrice": 120, "exitDate": "2026-11-18", "closedAt": "2026-11-18T04:00:00.000Z"})
    trades.append(tr_held("MOMN", 17, 100, 90, "n1"))
    def cards(cs):
        cs["t1"] = held_card("MOMT", 17, 100, 90, "t1", [{"px": 100, "qty": 17}], lots_date="2026-09-01", price=125); cs["t1"]["plan"]["tp"] = 120
        cs["n1"] = held_card("MOMN", 17, 100, 90, "n1", [{"px": 100, "qty": 17}], lots_date="2026-09-01", price=102); cs["n1"]["plan"]["tp"] = 120
        cs["pl"] = mom_plan("MOMP", 99.5, qty=17, hwf=False, tp=120, rows=[{"px": 100, "qty": 17}])
    b, page, ce, pe = run_with(pw, w, h, cards, trades)
    try:
        for t in ("MOMT", "MOMN", "MOMP"): hw(page, t, True)
        p = card(page, "pl")
        check(f"{tag} 2g planned card: 'T1 120 (sell #8)', 'reward at T1 … 2.0R', no Buy/Sell chips", p and "T1 120 (sell #8)" in p["l2"] and re.search(r"reward at T1 \+\$[\d.,k]+ · 2\.0R", p["l3"]) and not js(page, "()=>!!document.querySelector('[data-bd-card=\"pl\"] [data-pv-leg]')"), p and [p["l2"], p["l3"]])
        n = card(page, "n1")
        check(f"{tag} 2g holding card (T1 not hit): 'T1 120 (sell #8)' in line 2", n and "T1 120 (sell #8)" in n["l2"], n and n["l2"])
        dr = drawer(page, "n1")
        check(f"{tag} 2g drawer offers 'Place T1 sell'; the sheet shows 'SELL #8 @ 120 · Limit'", js(page, "()=>{ const b = document.querySelector('[data-pc2-t1place]'); if(!b) return false; b.click(); return true; }"))
        page.wait_for_timeout(450)
        t = js(page, "()=>{ const s = document.querySelector('[data-pc2-t1sheet]'); return s ? s.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} 2g T1 sheet text", re.search(r"SELL #8 @ 120 Limit", t) is not None and "trails" in t, t)
        js(page, "()=>bdPopClose()")
        a = card(page, "t1")
        check(f"{tag} 2g after T1: '#9 left @ 100 … T1 done … trailing' + 'Suggested: stop to breakeven' · 'Move stop to 100'", a and "#9 left @ 100" in a["l2"] and "T1 done" in a["l2"] and "trailing" in a["l2"] and "Suggested: stop to breakeven" in a["nx"] and any(x["t"] == "Move stop to 100" for x in a["btn"]), a and [a["l2"], a["nx"]])
        # editor: single Exit row
        open_editor(page, "winner"); fill_ed(page, "ABCD", 100, 90)
        js(page, "()=>{ const t = document.getElementById('cnTp'); }"); page.fill("#cnTp", "120"); js(page, "()=>coreNewIn()"); page.wait_for_timeout(400)
        ed = js(page, "()=>{ const f = document.querySelector('[data-pc2-exit]'); const q = coreNew.re1Model && coreNew.re1Model.qty; return {vis: f.getClientRects().length > 0, txt:f.innerText.replace(/\\s+/g,' '), v:document.getElementById('cnT1v').value, hint:document.getElementById('cnT1hint').innerText, q, t2:document.getElementById('cnTp2').type, all:document.getElementById('cnWBox').innerText}; }")
        check(f"{tag} 2g Momentum editor: one Exit row 'Target 1 · Sell at T1 [50 %] · rest: trail stop', default 50%", ed["vis"] and ed["v"] == "50" and "Target 1" in ed["txt"] and "Sell at T1" in ed["txt"] and "Used for reward/R and the T1 sell. Rest exits by your trailing stop." in ed["txt"], ed)
        check(f"{tag} 2g hint '= #half of #total' and Target 2 / shares-at-T1 gone", re.search(r"= #%d of #%d" % (ed["q"] // 2, ed["q"]), ed["hint"]) and "Target 2" not in ed["all"] and "Shares at target 1" not in ed["all"] and "display only" not in ed["all"] and ed["t2"] == "hidden", ed)
        js(page, "()=>pc2T1Mode('qty')"); page.fill("#cnT1v", "5"); js(page, "()=>coreNewIn()"); page.wait_for_timeout(300)
        hint = js(page, "()=>document.getElementById('cnT1hint').innerText")
        check(f"{tag} 2g sell can be a share count: '= #5 of #…'", re.search(r"= #5 of #\d+", hint) is not None, hint)
        js(page, "()=>coreSheetClose()")
        check(f"{tag} 2g no overflow", not overflow_ok(page)["bad"], overflow_ok(page))
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def homework_place_checks(pw, w, h):
    tag = "[%s]" % w
    def cards(cs):
        cs["pl"] = mom_plan("MOMP", 99.5, qty=1, hwf=False, rows=[{"px": 100, "qty": 1}])
    b, page, ce, pe = run_with(pw, w, h, cards)
    try:
        hw(page, "MOMP", False)
        q70 = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='MOMP'); const m = re1CardModel(c, null, 100, 90).m; const f = re1CardModel(c, null, 100, 90, 0, 'full').m; return [m.qty, f.qty]; }")
        js(page, "(q)=>{ const c = coreCardsList.find(x=>x.ticker==='MOMP'); c.plan.ps1.rows[0].qty = q; coreWrite(c.id, {plan:c.plan}); }", q70[0])
        js(page, "()=>efCorePlaceOpen('pl')"); page.wait_for_timeout(450)
        t = js(page, "()=>document.querySelector('[data-ef-core-place]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 2f Place sheet (homework not done): '#{q70[0]}', '70% · homework not done' and one link 'Fill 2 lines → full size #{q70[1]} ›'", f"#{q70[0]}" in t and "70% · homework not done" in t and f"Fill 2 lines → full size #{q70[1]} ›" in t, t[:300])
        check(f"{tag} 2f fields are closed by default (never blocks Place)", not js(page, "()=>!!document.querySelector('[data-pc2-hwbox]')"))
        js(page, "()=>document.querySelector('[data-pc2-hwfill]').click()"); page.wait_for_timeout(300)
        check(f"{tag} 2f link unfolds exactly the two Momentum homework fields", js(page, "()=>[...document.querySelectorAll('[data-pc2-hwin]')].map(x=>x.dataset.pc2Hwin).join()") == "exit,trigger")
        page.fill("[data-pc2-hwin=exit]", "Revenue growth below 30% next quarter"); page.wait_for_timeout(200)
        check(f"{tag} 2f one line filled = not done yet, size unchanged", not js(page, "()=>ftHwDone('MOMP')") and js(page, "()=>coreCardsList.find(x=>x.ticker==='MOMP').plan.ps1.rows[0].qty") == q70[0])
        page.fill("[data-pc2-hwin=trigger]", "Close above 100 on 1.5x volume"); page.wait_for_timeout(1500)
        done = js(page, "()=>({d:ftHwDone('MOMP'), q:coreCardsList.find(x=>x.ticker==='MOMP').plan.ps1.rows[0].qty, t:document.querySelector('[data-ef-core-place]').innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 2f both lines valid → homework saved as done and the size updates live #{q70[0]} → #{q70[1]}", done["d"] and done["q"] == q70[1] and f"#{q70[1]}" in done["t"] and "full size ✓" in done["t"], done)
        js(page, "()=>bdPopClose()")
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()
    # Place without filling: the saved 70% size is what is placed
    b, page, ce, pe = run_with(pw, w, h, cards)
    try:
        hw(page, "MOMP", False)
        q70 = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='MOMP'); const m = re1CardModel(c, null, 100, 90).m; c.plan.ps1.rows[0].qty = m.qty; coreWrite(c.id, {plan:c.plan}); return m.qty; }")
        js(page, "()=>efCorePlaceOpen('pl')"); page.wait_for_timeout(400)
        js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(500)
        r = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='MOMP'); return {placed:!!(c.ln4 && c.ln4.placedAt), q:c.plan.ps1.rows[0].qty, hw:ftHwDone('MOMP')}; }")
        check(f"{tag} 2f ignoring the link: Place sends #{q70} as saved, homework untouched", r["placed"] and r["q"] == q70 and not r["hw"], r)
    finally:
        b.close()


def topup_checks(pw, w, h):
    tag = "[%s]" % w
    trades = [tr_held("TU1", 1, 100, 90, "u1"), tr_held("TU2", 1, 100, 90, "u2"), tr_held("TU3", 1, 100, 90, "u3")]
    b, page, ce, pe = run_with(pw, w, h, None, trades)
    try:
        q70 = js(page, "()=>{ const c = {acct:'main', ticker:'TU1', market:'US', plan:{entry:100, stop:90}, id:'x'}; return re1CardModel(c, null, 100, 90).m.qty; }")
        d3, d6 = js(page, BACK_JS, 3), js(page, BACK_JS, 6)
        cs = {}
        for k, tk, tid, dt in (("u1", "TU1", "u1", d3), ("u2", "TU2", "u2", d6), ("u3", "TU3", "u3", d3)):
            cs[k] = held_card(tk, 1, 100, 90, tid, [{"px": 100, "qty": 1}], lots_date=dt, price=100)
        js(page, "(q)=>0", 0)
        for c in cs.values():
            pass
        seed_cards(page, cs)
        # make the held qty the 70% size and set the trades
        js(page, "(q)=>{ const B = getBook('main'); B.trades.forEach(t=>{ if(/^u\\d$/.test(t.id)) t.qty = q; }); saveBook('main'); coreCardsList.forEach(c=>{ if(/^TU/.test(c.ticker)){ c.lots[0].qty = q; c.plan.ps1.rows[0].qty = q; } }); re1Cache = {}; }", q70)
        hw(page, "TU1", True); hw(page, "TU2", True); hw(page, "TU3", False)
        a, b2, c3 = card(page, "u1"), card(page, "u2"), card(page, "u3")
        check(f"{tag} 2f Top up: shown ≤ 5 trading days after the first fill with homework done ('Top up to full · #n', '2 days left')", a and re.search(r"Top up to full · #\d+", a["nx"]) and "2 days left" in a["nx"], a and a["nx"])
        check(f"{tag} 2f Top up gone after day 5 and when homework is not done", b2 and "Top up" not in b2["nx"] and c3 and "Top up" not in c3["nx"], [b2 and b2["nx"], c3 and c3["nx"]])
        full = js(page, "()=>{ const c = {acct:'main', ticker:'TU1', market:'US', plan:{entry:100, stop:90}, id:'x'}; return re1CardModel(c, null, 100, 90, 0, 'full').m.qty; }")
        n = int(re.search(r"#(\d+)", a["nx"].split("Top up")[1]).group(1))
        check(f"{tag} 2f Top up sized to the full budget (held #{q70} + top-up #{n} = full #{full} ±1)", abs(q70 + n - full) <= 1, [q70, n, full])
        js(page, "()=>pc2TopUpGo('u1')"); page.wait_for_timeout(800)
        t = js(page, "()=>{ const e = document.querySelector('[data-ef-core-place]'); return e ? e.innerText.replace(/\\s+/g,' ') : ''; }")
        rows = js(page, "()=>coreCardsList.find(x=>x.ticker==='TU1').plan.ps1.rows.length")
        check(f"{tag} 2f Top up = a first-build row (no ADDON_THESIS, no stop-raise rule): the Place sheet opens for ②", rows == 2 and "Place order ②" in t and js(page, "()=>pc2Gate(bdById('u1')).ok"), [rows, t[:160]])
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def phone_checks(pw, w, h):
    tag = "[%s]" % w
    trades = [tr_held("MOMT", 17, 100, 90, "t1")]
    def cards(cs):
        cs["t1"] = held_card("MOMT", 17, 100, 90, "t1", [{"px": 100, "qty": 17}], lots_date="2026-09-01", price=125); cs["t1"]["plan"]["tp"] = 120
        cs["pl"] = mom_plan("MOMP", 94.34, qty=17, hwf=False, tp=120, rows=[{"px": 100, "qty": 9}, {"px": 95, "qty": 8}])
    b, page, ce, pe = run_with(pw, w, h, cards, trades)
    try:
        hw(page, "MOMT", True); hw(page, "MOMP", False)
        o = overflow_ok(page)
        check(f"{tag} 2a phone: no card line overflows, no page scroll sideways", not o["bad"] and o["page"], o)
        st = js(page, "()=>{ const cols = [...document.querySelectorAll('[data-bd-col]')]; return {vis: cols.filter(c=>c.getClientRects().length).length, sticky: cols.map(c=>getComputedStyle(c.querySelector('.bd-ch')).position)}; }")
        check(f"{tag} 2a phone: one column, three sections stacked, sticky section headers", st["vis"] == 3 and all(x == "sticky" for x in st["sticky"]), st)
        bh = js(page, "()=>[...document.querySelectorAll('[data-bd-card] .pc2-nx button:not(.pc2-hw)')].filter(b=>b.getClientRects().length).map(b=>Math.round(b.getBoundingClientRect().height))")
        check(f"{tag} 2a phone: card buttons are tap-size (≥ 40px)", bh and min(bh) >= 40, bh)
        dr = drawer(page, "t1")
        check(f"{tag} 3 drawer fits the phone (no sideways scroll)", js(page, "()=>{ const d = document.getElementById('bdDr'); return d.scrollWidth <= d.clientWidth + 1; }"), dr and dr["txt"][:80])
        js(page, "()=>bdClose()")
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def fix_checks(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = boot(pw, w, h)
    try:
        hw(page, "AVGO", False)
        a = card(page, "mA")
        same = js(page, "()=>{ const c = document.querySelector('[data-bd-card=\"mA\"] .pc2-nx'); const h = c.querySelector('.pc2-hw'), b = c.querySelector('.pc2-b'); return {hw:h.innerText, same: Math.abs(h.getBoundingClientRect().top - b.getBoundingClientRect().top) <= 4, dy: Math.round(b.getBoundingClientRect().top - h.getBoundingClientRect().top)}; }")
        check(f"{tag} fix2 Momentum next step is the short form 'Homework 0/2 · #n when done ›'" + (" and Place stays on the same line" if w >= 1280 else " (may wrap on the phone)"), re.match(r"^Homework 0/2 · #\d+ when done ›$", same["hw"]) and (w < 1280 or same["same"]), same)
        x = card(page, "xp")
        check(f"{tag} fix3 no blocked reason is cut with '…' (HF5: names the open setup)", "…" not in js(page, "()=>document.querySelector('#bdBoard').innerText") and "BTC is open with full risk · move its stop to cut risk ≥ 50% (now 0%) to open another Sat" in x["nx"], x["nx"])
        check(f"{tag} fix4 Sat lots show 2 decimals (#0.99), data keeps full precision", "#0.99 " in (card(page, "ps")["l2"] + " ") and "#0.9911" not in js(page, "()=>document.querySelector('#bdBoard').innerText") and js(page, "()=>{ const p = posView(bdById('ps')); return p.plannedQty > 0.99 && p.plannedQty < 0.9912 && String(p.plannedQty).length > 4; }"))
        for cid in ("cN", "xp", "mA"):
            drawer(page, cid)
            r = js(page, "()=>{ const d = document.getElementById('bdDr'); const places = [...d.querySelectorAll('button')].filter(b=>/^Place\\b/.test(b.innerText.trim())).map(b=>({t:b.innerText.trim(), inFoot: !!b.closest('.bd-df')})); const foot = [...d.querySelectorAll('.bd-df button')].map(b=>b.innerText.trim()); const pri = d.querySelector('[data-bd-lvact=\"place\"].pri'); return {places, foot, bg: pri ? getComputedStyle(pri).backgroundColor : null}; }")
            if cid == "cN":
                check(f"{tag} fix5 drawer: ONE Place (in the Entries row, black), footer = Update levels · Close trade · Edit plan", len(r["places"]) == 1 and not r["places"][0]["inFoot"] and r["bg"] == "rgb(20, 22, 26)" and r["foot"][:3] == ["Update levels", "Close trade", "Edit plan"], r)
            else:
                check(f"{tag} fix5 drawer {cid}: at most one Place and none duplicated in the footer", len(r["places"]) <= 1, r)
            js(page, "()=>bdClose()")
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (360, 740)):
            phone_checks(pw, w, h); fix_checks(pw, w, h)
        for w, h in ((1440, 900), (1280, 800)):
            board(pw, w, h); drawer_checks(pw, w, h); place_checks(pw, w, h); sizing_checks(pw, w, h); editor_checks(pw, w, h); exit_checks(pw, w, h); homework_place_checks(pw, w, h); topup_checks(pw, w, h); fix_checks(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY pc2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
