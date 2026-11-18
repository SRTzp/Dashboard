#!/usr/bin/env python3
"""TW1 — small tweaks: Update levels loads ALL saved entry/SL levels · Today Act rows size + risk · Today status line → Flow Regime details ·
Plan filters on one row · RRG tile name tooltip (hover / long-press) · Candidate leftovers gone from Today · เทส 375
Chromium · 390 (+360) + 1280 + 1440 · นาฬิกาปลอม พฤ. 1 ต.ค. 2026 12:00 ICT · SAMPLE data only
รัน: python3 run_tests_phase375.py → tests/screenshots/tw1-*.png"""
import os, json, re, sys, copy
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase374 as W
import lib_phase24 as P24
import lib_phase13 as P13
import lib_phase106 as T
import lib_phase120 as P120
import rrg1_fixture as RF

ENGINE = W.base.BROWSER_ENGINE
results = []
js, settle, cnt, txt = W.js, T.settle, T.cnt, T.txt
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots") + "/tw1-"


RETIRED_RE1C2 = ['2 Act has plan/position rows', '2 stock row: size = shares', '2 multi-entry plan: size = total shares', '2 Sat row: size in lots', '2 every row has size + risk']   # RE-C2: Act rows are now the three groups (Enter / Check orders / Manage) — covered by run_tests_re1c2
def check(name, ok, detail=""):
    if any(q in name for q in RETIRED_RE1C2):
        print('RETIRED (RE-C2, not counted as PASS) - ' + name); return
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def launch(pw, w, h):
    b, page, ce, pe = W.launch(pw, w, h)
    P120.ps_on(page)   # per-account default risk (otherwise forms say 'Set default risk in Settings')
    return b, page, ce, pe


def shot(page, name, full=False):
    settle(page, 700); page.screenshot(path=f"{SHOTS}{name}.png", animations="disabled", full_page=full)


def ps1m(rows, stops, typed):
    """rows = [(px, qty, split%)] · stops = [(px, pct)] — a saved multi-level plan (plan.ps1)"""
    return {"entry": rows[0][0], "stop": stops[0][0], "risk": typed, "ps1": {
        "v": 1, "typed": typed, "qty": sum(r[1] for r in rows), "riskPct": typed, "riskMoney": round(typed * 10000), "sizePct": 4.0,
        "rows": [{"px": p, "qty": q, "riskPct": round(typed * s / 100, 6)} for p, q, s in rows],
        "stops": [{"px": p, "pct": c} for p, c in stops]}}


def levels(page):
    return js(page, "()=>({ne:coreNew.ne, ns:coreNew.ns, pxE:coreNew.pxE.slice(), pxS:coreNew.pxS.slice(), spE:coreNew.spE.slice(), pcS:coreNew.pcS.slice(), e0:coreEl('cnEntry').value, s0:coreEl('cnStop').value, rowsE:document.querySelectorAll('[data-ps1-row^=\"e\"]').length, rowsS:document.querySelectorAll('[data-ps1-row^=\"s\"]').length})")


def saved_levels(page, cid):
    c = W.card_db(page, cid); p = c["plan"]["ps1"]
    return {"e": [r["px"] for r in p["rows"]], "s": [(r["px"], r["pct"]) for r in p["stops"]], "split": [round(r["riskPct"] / p["typed"] * 100) for r in p["rows"]] if p.get("typed") else None}


CASES = [  # id, ticker, track, rows, stops, typed
    ("cM2", "AMD", None, [(100, 60, 60), (96, 50, 40)], [(90, 100)], 0.4),
    ("cM3", "ADBE", None, [(100, 40, 50), (97, 30, 30), (94, 20, 20)], [(88, 60), (85, 40)], 0.4),
    ("cC2", "NVDA", "ladder", [(100, 60, 60), (95, 50, 40)], [(88, 100)], 1.0),
    ("cC3", "MSFT", "ladder", [(100, 40, 50), (96, 30, 30), (92, 20, 20)], [(86, 70), (82, 30)], 1.0),
]


def update_levels(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        cards = {}
        for cid, t, trk, rows, stops, typed in CASES:
            kw = {"plan": ps1m(rows, stops, typed), "px": rows[0][0] + 5, "pxDate": "2026-10-01"}
            if trk: kw["track"] = trk
            cards[cid] = P24.card(cid, "main", t, **kw)
        cards["cM3"]["ln4"] = {"placedLv": {"1": "2026-09-30T10:00:00Z"}}
        W.put_cards(page, cards)
        for cid, t, trk, rows, stops, typed in CASES:
            nm = f"{'COMP' if trk else 'MMT'} {len(rows)}-entry/{len(stops)}-SL"
            before_card = copy.deepcopy(W.card_db(page, cid))
            js(page, "(id)=>{ switchTab('plan'); bdEditLv(id); }", cid); settle(page, 700)
            L = levels(page); L["rowsE"] = js(page, "()=>document.querySelectorAll('[data-ps1-row] input[id^=cnEn]').length"); L["rowsS"] = js(page, "()=>document.querySelectorAll('[data-ps1-row] input[id^=cnSt]').length")
            check(f"{tag} 1 {nm}: Update levels loads every saved entry (rows {L['rowsE']} / {len(rows)}) and SL level (rows {L['rowsS']} / {len(stops)})",
                  L["ne"] == len(rows) and L["ns"] == len(stops) and L["rowsE"] == len(rows) and L["rowsS"] == len(stops), L)
            check(f"{tag} 1 {nm}: prices + splits restored", float(L["e0"]) == rows[0][0] and [float(x) for x in L["pxE"][:len(rows) - 1]] == [r[0] for r in rows[1:]]
                  and float(L["s0"]) == stops[0][0] and [float(x) for x in L["pxS"][:len(stops) - 1]] == [s[0] for s in stops[1:]]
                  and [round(float(x)) for x in L["spE"][:len(rows)]] == [r[2] for r in rows] and (len(stops) == 1 or [round(float(x)) for x in L["pcS"][:len(stops)]] == [s[1] for s in stops]), L)
            if w == 390 and cid == "cM3":
                shot(page, "update-levels-2entry-390") if False else None
            ok_save = js(page, "()=>{ const b = coreEl('cnSave'); return !!b && !b.disabled; }")
            check(f"{tag} 1 {nm}: Save enabled with no edits", ok_save, "")
            if ok_save:
                js(page, "()=>coreNewSave()"); settle(page, 600)
                after = W.card_db(page, cid)
                sv = saved_levels(page, cid)
                check(f"{tag} 1 {nm}: save without edits keeps every level", sv["e"] == [r[0] for r in rows] and sv["s"] == [tuple(s) for s in stops] and sv["split"] == [r[2] for r in rows], sv)
                check(f"{tag} 1 {nm}: order flags (ln4.placedLv) untouched", (after.get("ln4") or {}) == (before_card.get("ln4") or {}), after.get("ln4"))
            else:
                js(page, "()=>coreSheetClose()")
        # screenshot: 2-entry Compounder form at 390
        if w == 390:
            js(page, "()=>{ switchTab('plan'); bdEditLv('cC2'); }"); settle(page, 800)
            shot(page, "update-levels-2entry-390")
            check(f"{tag} 1 form at 390: no horizontal overflow", W.ovf(page) <= 0, W.ovf(page))
            js(page, "()=>coreSheetClose()")
        # Sat: single Entry / SL / TP round trip
        js(page, """()=>{ const d = {v3:true, v2:true, sleeve:'main', week:wpWeekKey(), created_at:'2026-09-30T00:00:00Z', cancel_level:null, tf:'4H', setups:[], setup_note:'', classify:'', zone_act:false, zone_act_txt:'', setup_ck:[], status:'active', accts:{}, log:[],
            asset:'XAUUSD', bias:'Long', entry:2000, sl:1980, tp:2060, ema50_ok:true, structure_ok:true, mss:null, pb_acct:'main', pb2:true, ln4:{placedLv:{0:'2026-09-30T10:00:00Z'}}};
            sat7dWrite('satIdeas', 'iSAT', d); satIdeasList.push(Object.assign({id:'iSAT'}, d)); bdRender(); }""")
        settle(page, 500)
        js(page, "()=>{ switchTab('plan'); bdEditLv('iSAT'); }"); settle(page, 600)
        v = js(page, "()=>({e:pb2.entry, s:pb2.sl, t:pb2.tp, step:pb2.step})")
        check(f"{tag} 1 Sat: Update levels loads Entry / SL / TP", v["e"] == "2000" and v["s"] == "1980" and v["t"] == "2060", v)
        js(page, "()=>pb2Save(false)"); settle(page, 500)
        d = page.evaluate("()=>window.firebase.__mockDb.__dump()")
        sat = [x for k, x in d.items() if k.endswith("/satIdeas/iSAT")]
        check(f"{tag} 1 Sat: save without edits keeps Entry / SL / TP and the order flag", sat and sat[0]["entry"] == 2000 and sat[0]["sl"] == 1980 and sat[0]["tp"] == 2060 and (sat[0].get("ln4") or {}).get("placedLv", {}).get("0"), sat[:1])
    finally:
        b.close()


def act_fixture(page):
    t = js(page, "()=>tv1Today()")
    js(page, "(t)=>glWrite(S=>{ S.tvSetup = Object.assign({}, S.tvSetup||{}, {AMD:t, NVDA:t}); })", t)
    W.put_wl(page, {"AMD": W.wl_doc("AMD", exit_="x", trigger="y", confirmed=True), "NVDA": W.wl_doc("NVDA", trk=True, exit_="x", trigger="y", confirmed=True)})
    cards = {
        "cAM": P24.card("cAM", "main", "AMD", plan=ps1m([(182.5, 40, 100)], [(170, 100)], 0.4), px=181, pxDate="2026-10-01"),
        "cNV": P24.card("cNV", "main", "NVDA", track="ladder", plan=ps1m([(100, 30, 60), (96, 20, 40)], [(90, 100)], 1.0), px=100.5, pxDate="2026-10-01"),
    }
    W.put_cards(page, cards)
    js(page, """()=>{ const d = {v3:true, v2:true, sleeve:'main', week:wpWeekKey(), created_at:'2026-09-30T00:00:00Z', cancel_level:null, tf:'4H', setups:[], setup_note:'', classify:'', zone_act:false, zone_act_txt:'', setup_ck:[], status:'active', accts:{}, log:[],
        asset:'XAUUSD', bias:'Long', entry:2000, sl:1980, tp:2060, ema50_ok:true, structure_ok:true, mss:null, pb_acct:'main', pb2:true};
        sat7dWrite('satIdeas', 'iSAT', d); satIdeasList.push(Object.assign({id:'iSAT'}, d)); }""")
    W.refresh_today(page); W.refresh_today(page)


ROWJS = """()=>[...document.querySelectorAll('[data-tw1-row]')].map(r=>{
  const q = s=>r.querySelector(s), rc = r.getBoundingClientRect(), tops = new Set();
  [...r.querySelectorAll('b,.sc,.st,[data-tw1-lv],[data-tw1-size],[data-tw1-risk],[data-tw1-why],button')].filter(e=>e.offsetParent).forEach(e=>{ const q2 = e.getBoundingClientRect(); tops.add(Math.round((q2.top + q2.height/2)/14)); });
  const L = s=>{ const e = q(s); return e ? Math.round(e.getBoundingClientRect().left) : null; };
  return {sym:r.dataset.ln4Row, h:Math.round(rc.height), lines:tops.size, size:(q('[data-tw1-size]')||{}).innerText, risk:(q('[data-tw1-risk]')||{}).innerText, why:(q('[data-tw1-why]')||{}).innerText, lv:(q('[data-tw1-lv]')||{}).innerText, st:(q('[data-ln4-status]')||{}).innerText,
    xs:[L('b'),L('.sc'),L('[data-ln4-status]'),L('[data-tw1-lv]'),L('[data-tw1-size]'),L('[data-tw1-risk]'),L('[data-tw1-why]'),L('button')], clip:r.scrollWidth - r.clientWidth, btn:!!q('button[data-ln4-btn]')};
})"""


def act_rows(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        W.seed_main(page) if False else None
        act_fixture(page)
        R = js(page, ROWJS)
        syms = [r["sym"] for r in R]
        check(f"{tag} 2 Act has plan/position rows (AMD · NVDA · Gold)", len(R) >= 3, syms)
        by = {r["sym"]: r for r in R}
        # numbers = the saved plan numbers (same as plan board / form)
        amd = by.get("AMD") or {}
        check(f"{tag} 2 stock row: size = shares (#40) and risk = amount + % of portfolio", amd.get("size") == "#40" and re.search(r"%$", amd.get("risk") or "") is not None and "·" in (amd.get("risk") or ""), amd)
        nv = by.get("NVDA") or {}
        check(f"{tag} 2 multi-entry plan: size = total shares of the plan (#50)", nv.get("size") == "#50", nv)
        gold = [r for r in R if r["sym"] not in ("AMD", "NVDA")]
        check(f"{tag} 2 Sat row: size in lots + risk amount (·%)", bool(gold) and re.search(r"lot", gold[0]["size"] or "", re.I) is not None and (gold[0]["risk"] or "—") != "—", gold)
        check(f"{tag} 2 every row has size + risk (no empty cell)", all(r["size"] and r["risk"] for r in R), R)
        check(f"{tag} 2 every row keeps its action pill and no clipped content", all(r["btn"] and r["clip"] <= 1 for r in R), [(r["sym"], r["clip"]) for r in R])
        if w >= 1000:
            check(f"{tag} 2 Mac: ONE line per row (Entry / SL · size · risk · reason · pill)", all(r["lines"] == 1 for r in R), [(r["sym"], r["lines"], r["h"]) for r in R])
            check(f"{tag} 2 Mac: Entry/SL shown (Sat with TP)", all("Entry" in (r["lv"] or "") and "SL" in (r["lv"] or "") for r in R) and all("TP" in (r["lv"] or "") for r in gold), [r["lv"] for r in R])
            cols = list(zip(*[r["xs"] for r in R]))
            check(f"{tag} 2 Mac: columns aligned across rows", all(len(set(c)) == 1 for c in cols), cols)
        else:
            check(f"{tag} 2 iPhone: at most 2 lines per row (line 1 symbol+tag+status · line 2 size · risk · reason + pill)", all(r["lines"] <= 2 for r in R), [(r["sym"], r["lines"], r["h"]) for r in R])
            check(f"{tag} 2 iPhone: row height ≤ 2 lines (≤ 96 px)", all(r["h"] <= 96 for r in R), [(r["sym"], r["h"]) for r in R])
        check(f"{tag} 2 no horizontal overflow", W.ovf(page) <= 0, W.ovf(page))
        if w in (1440, 390):
            js(page, "()=>window.scrollTo(0,0)"); shot(page, f"today-{w}")
    finally:
        b.close()


def status_line(pw, w, h):
    if w <= 560:
        print('RETIRED (RE-C2, not counted as PASS) - [%d] 3 Today status line button: on the phone the COMP chip is hidden while Normal (brief §1); the Mac/tablet checks still run' % w); return
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        P24.set_ff(page, P24.ff_json(False, False)); settle(page, 300)
        W.refresh_today(page)
        n = cnt(page, "[data-tw1-status]")
        check(f"{tag} 3 Today status line is a button (focusable, pointer cursor)", n >= 1 and js(page, "()=>{ const e = document.querySelector('[data-tw1-status]'); return e.tagName === 'BUTTON' && e.tabIndex >= 0 && getComputedStyle(e).cursor === 'pointer'; }"), n)
        js(page, "()=>{ try{ localStorage.removeItem('dash.bdRows'); }catch(e){} }")
        page.locator("[data-tw1-status]").first.click(); settle(page, 900)
        r = js(page, "()=>{ const d = document.querySelector('[data-bd-more] [data-bd-row=\"regime\"]'); const dd = d && (d.tagName === 'DETAILS' ? d : d.querySelector('details')); const rc = dd ? dd.getBoundingClientRect() : null; return {tab:activeTab, open:!!(dd && dd.open), inview: !!rc && rc.top < innerHeight && rc.bottom > 0}; }")
        check(f"{tag} 3 click → Flow with 'Regime details' expanded and in view", r["tab"] == "flow" and r["open"] and r["inview"], r)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 400)
        page.locator("[data-tw1-status]").first.focus(); page.keyboard.press("Enter"); settle(page, 900)
        check(f"{tag} 3 keyboard (Enter) does the same", js(page, "()=>activeTab") == "flow", js(page, "()=>activeTab"))
    finally:
        b.close()


def plan_filters(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        W.seed_main(page)
        js(page, "()=>switchTab('plan')"); settle(page, 700)
        g = js(page, """()=>{ const c = document.querySelector('[data-bd-chips]'), s = document.querySelector('[data-bd-seg]'), f = document.querySelector('[data-bd-frow]');
          const a = c.getBoundingClientRect(), z = s.getBoundingClientRect(), fr = f.getBoundingClientRect();
          return {chipTop:a.top, segTop:z.top, chipsRight:a.right, segLeft:z.left, segRight:z.right, rowRight:fr.right, rowLeft:fr.left, chipsScroll:c.scrollWidth - c.clientWidth,
            btns:[...document.querySelectorAll('[data-bd-chip],[data-bd-segbtn]')].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.top + r.height/2), Math.round(r.left), Math.round(r.right)]; })}; }""")
        one = len({round(t[0] / 8) for t in g["btns"]}) == 1
        check(f"{tag} 4 type filters (All · MMT · COMP · Sat) and status chips (Planned · Ordered · Holding) = {len(g['btns'])} controls", len(g["btns"]) == 7, g["btns"])
        check(f"{tag} 4 all 7 on ONE row" + (" (iPhone: fits at this width)" if w < 600 else ""), one, g)
        check(f"{tag} 4 type filters left · status chips right", g["chipsRight"] <= g["segLeft"] + 1 and g["segRight"] <= g["rowRight"] + 1, g)
        check(f"{tag} 4 no clipped / scrolling chips and no page overflow", g["chipsScroll"] <= 0 and W.ovf(page) <= 0, (g["chipsScroll"], W.ovf(page)))
        # behaviour unchanged
        js(page, "()=>bdSetChip('COMP')"); settle(page, 300)
        syms = js(page, "()=>[...document.querySelectorAll('[data-bd-card]')].map(e=>e.querySelector('.bd-tk').innerText)")
        js(page, "()=>{ bdSetChip('all'); bdSetSeg('hold'); }"); settle(page, 300)
        on = js(page, "()=>document.querySelector('[data-bd-segbtn=\"hold\"]').classList.contains('on') && document.querySelector('[data-bd-chip=\"all\"]').classList.contains('on')")
        check(f"{tag} 4 behaviour unchanged: COMP filter shows only COMP · status chip switches column", set(syms) == {"NVDA"} and on, (syms, on))
        if w in (1440, 390):
            js(page, "()=>{ bdSetSeg('plan'); window.scrollTo(0,0); }"); shot(page, f"plan-filters-{w}")
    finally:
        b.close()


LP = """([sel, ms, up])=>new Promise(res=>{
  const t = document.querySelector(sel); if(!t) return res('notarget'); const r = t.getBoundingClientRect(), x = r.left + r.width/2, y = r.top + r.height/2;
  const mk = ()=>new Touch({identifier:7, target:t, clientX:x, clientY:y});
  t.dispatchEvent(new TouchEvent('touchstart', {bubbles:true, cancelable:true, touches:[mk()], changedTouches:[mk()]}));
  setTimeout(()=>{ res('held'); if(up) t.dispatchEvent(new TouchEvent('touchend', {bubbles:true, cancelable:true, touches:[], changedTouches:[mk()]})); }, ms);
})"""


def rrg_tip(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        RR = [("SMH", "lead", 4.2, 0.9), ("GRID", "lead", 3.1, 0.7), ("XLU", "lead", 2.4, -0.8), ("XLK", "lead", 1.0, 0.2), ("IGV", "imp", -1.0, 0.6), ("HACK", "imp", -0.7, 0.1),
              ("XLF", "weak", 0.6, -0.7), ("XLE", "lag", -2.1, -0.9), ("XLP", "lag", -1.4, 0.9)]   # GRID = not in RRG_SYMS → ticker only
        rows = [{"sym": s_, "name": s_ + " fund", "quad": q, "ratio": 100 + r, "mom": 100 + d, "dRatio": 0.1, "dMom": d, "rsTrend": r / 10, "days": 5, "prevDays": 6, "date": "2026-09-30", "off52": -3} for s_, q, r, d in RR]
        rows = page.evaluate("(" + RF.MODELIZE_JS + ")", rows)
        page.evaluate("(r)=>{ const f=ffState(); f.rrg.rowsD=r; f.rrg.rowsW=r; f.rrg.build=RRG_BUILD; f.rrg.day=rrgToday(); }", rows)
        js(page, "()=>{ switchTab('flow'); ffRenderThemes(); bdFlowTopRender(); }"); settle(page, 800)
        tiles = js(page, "()=>[...document.querySelectorAll('[data-bd-rrg] [data-bd-sec], [data-bd-rrg] .il')].map(e=>({sym:(e.dataset.bdSec||e.innerText.replace(/[^A-Z]/g,'')), name:e.getAttribute('data-tw1-name'), title:e.getAttribute('title'), vis:!!e.offsetParent}))")
        vis = [t for t in tiles if t["vis"]]
        check(f"{tag} 5 RRG tiles render ETF tickers ({len(vis)} visible)", len(vis) > 0, tiles[:4])
        nm = [t for t in vis if t["name"]]
        check(f"{tag} 5 every visible ticker with a known name carries it (data + title)", all(t["title"] == t["name"] for t in nm) and len(nm) > 0, nm[:4])
        miss = [t["sym"] for t in vis if not t["name"]]
        check(f"{tag} 5 tickers without a name show the ticker only (none invented): {miss}", all(t["title"] is None for t in vis if not t["name"]), miss)
        sel = "[data-bd-rrg] .bd-sr[data-tw1-name]" if w >= 700 else "[data-bd-rrg] .il[data-tw1-name]"
        first = js(page, "(s)=>{ const e = document.querySelector(s); return e ? e.getAttribute('data-tw1-name') : null; }", sel)
        if w >= 700:
            page.locator(sel).first.hover(); settle(page, 250)
            t = js(page, "()=>{ const e = document.querySelector('[data-tw1-tip]'); return e ? e.innerText : null; }")
            check(f"{tag} 5 Mac: hover shows the full name tooltip ('{first}')", t == first, t)
            if w == 1440: shot(page, "rrg-tooltip-1440")
            page.mouse.move(5, 5); settle(page, 200)
            check(f"{tag} 5 Mac: tooltip hides on leave", cnt(page, "[data-tw1-tip]") == 0, "")
        else:
            page.evaluate(LP, [sel, 250, True]); settle(page, 150)
            check(f"{tag} 5 iPhone: short tap (250 ms) shows nothing", cnt(page, "[data-tw1-tip]") == 0, "")
            page.evaluate(LP, [sel, 500, False]); settle(page, 120)
            t = js(page, "()=>{ const e = document.querySelector('[data-tw1-tip]'); return e ? e.innerText : null; }")
            check(f"{tag} 5 iPhone: long-press (~400 ms) shows the name tooltip ('{first}')", t == first, t)
            shot(page, "rrg-tooltip-390")
            js(page, f"()=>document.querySelector('{sel}').dispatchEvent(new TouchEvent('touchend', {{bubbles:true, cancelable:true}}))"); settle(page, 150)
            check(f"{tag} 5 iPhone: hides on release", cnt(page, "[data-tw1-tip]") == 0, "")
            page.evaluate(LP, [sel, 500, False]); settle(page, 2300)
            check(f"{tag} 5 iPhone: hides by itself after 2 s", cnt(page, "[data-tw1-tip]") == 0, "")
            check(f"{tag} 5 iPhone: no text-selection / callout (user-select none · touch-callout none)", js(page, "(s)=>{ const c = getComputedStyle(document.querySelector(s)); return c.userSelect === 'none' || c.webkitUserSelect === 'none'; }", sel), "")
        check(f"{tag} 5 no overflow", W.ovf(page) <= 0, W.ovf(page))
    finally:
        b.close()


def sweep(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, {CANDA:{manual:true, sym:'CANDA', track:'winner', at:'2026-09-20'}}); })")
        W.seed_main(page)
        P24.set_ff(page, P24.ff_json(True, True))
        js(page, "()=>{ try{ localStorage.removeItem('dash.td4RemDismiss'); }catch(e){} }")
        P24 and None
        from lib_phase37 import set_clock
        set_clock(page, "2026-10-01T21:30:00+07:00"); settle(page, 300)
        W.refresh_today(page); W.refresh_today(page)
        js(page, "()=>{ ln4MoreOpen = true; todayRefresh(true); document.querySelectorAll('#tabToday details').forEach(d=>d.open = true); }")
        t = js(page, "()=>document.getElementById('tabToday').innerText")
        bad = re.findall(r"(?i)cand→wl|new cand|candidate|triage|inbox", t)
        check(f"{tag} 6 Today (after 20:00, everything expanded) shows no Candidate / Cand→WL / Triage / Inbox text", not bad, bad)
        rem = js(page, "()=>td4RemList(tdBuild()).map(x=>x.t)")
        check(f"{tag} 6 'Unfinished today' no longer offers Cand→WL / New Cand", not any(re.search(r"(?i)cand", x) for x in rem), rem)
        links = js(page, "()=>[...document.querySelectorAll('#tabToday [onclick]')].map(e=>e.getAttribute('onclick')).filter(x=>/wlSetView\\('cand'\\)|td4Pro|td3NotPassed|td4Add|candExp/.test(x))")
        check(f"{tag} 6 no Today link goes to Candidates", not links, links)
    finally:
        b.close()


if __name__ == "__main__":
    import os
    sel = [int(a) for a in os.environ.get("TW1W", "").split(",") if a]
    with sync_playwright() as pw:
        for w, h in [x for x in ((1440, 900), (1280, 860), (390, 844), (360, 780)) if not sel or x[0] in sel]:
            fns = (update_levels, act_rows, status_line, plan_filters, rrg_tip) if w != 360 else (plan_filters, act_rows)
            if w == 1440: fns = fns + (sweep,)
            for fn in fns:
                try: fn(pw, w, h)
                except Exception as e:
                    import traceback; traceback.print_exc(); check(f"[{w}] {fn.__name__} crashed", False, str(e)[:300])
    nf = [r for r in results if not r[1]]
    print(f"\nSUMMARY: {len(results) - len(nf)} pass / {len(nf)} fail")
    sys.exit(1 if nf else 0)
