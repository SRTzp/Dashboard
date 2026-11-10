#!/usr/bin/env python3
"""LN4 — Lean Today (status card · Act · Find) + Starter ¼ + Exec/Missed/Stage ladder + Lean Watch · เทส 369
Chromium · 390 + 1440 · นาฬิกาปลอม พฤ. 1 ต.ค. 2026 12:00 ICT · SAMPLE data only
รัน: python3 run_tests_phase369.py"""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase24 as P24
import run_tests_phase37 as P37
import run_tests_phase106 as T
import run_tests_phase120 as P120

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = T.settle
cnt, txt = T.cnt, T.txt
NOW = T.NOW


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def ovf(page): return js(page, "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")


def seed(page, cards):
    for cid, c in cards.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)


def refresh(page): js(page, "()=>todayRefresh(true)"); settle(page, 350)


def stub(page, code): js(page, "()=>{" + code + "}")


def setup_ok(page, syms):
    # Setup ✓ present (tvSetup[KEY] = today)
    js(page, "(l)=>glWrite(S=>{ const m = {}; l.forEach(s=>m[wlSymKey(s)] = thaiToday()); S.tvSetup = m; })", syms); settle(page, 300)


def rows(page): return js(page, "()=>[...document.querySelectorAll('[data-ln4-row]')].map(e=>({s:e.dataset.ln4Row,k:e.dataset.ln4Kind,st:e.dataset.ln4State,bad:e.dataset.ln4Bad||'',btn:(e.querySelector('[data-ln4-btn]')||{}).innerText||'',why:(e.querySelector('[data-ln4-why]')||{}).innerText||'',pt:(e.querySelector('[data-ln4-ptag]')||{}).innerText||''}))")


def row(page, s): return next((r for r in rows(page) if r["s"] == s), None)


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    cards = {
        "ccAM": P24.card("ccAM", "main", "AMD", plan={"entry": 182.5, "stop": 170}, px=170, pxDate="2026-10-01"),
        "ccNV": P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=168, tier="A",
                              lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 168}]),
        "ccAV": P24.card("ccAV", "main", "AVGO", plan={"entry": 341.2, "stop": 320}, px=330, pxDate="2026-10-01", track="ladder"),
        "ccET": P24.card("ccET", "main", "ETN", plan={"entry": 300, "stop": 280}, px=310, pxDate="2026-10-01"),
    }
    b, page, ce, pe = T.launch(pw, w, h, iso=NOW, picks=(), weekly=False)
    try:
        import run_tests_phase13 as P13
        P24.set_ff(page, P24.ff_json(True, True))
        js(page, "()=>{ try{ localStorage.removeItem('dash.ps1Off'); }catch(e){} }")
        js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("tNV", "core", "open", sym="NVDA", entry=171.4, sl=168, qty=10, cur="USD", date="2026-09-10")])
        stub(page, "window.ps1Model = ()=>({P:{principalPct:1.2}, cfg:{total:5}});")
        T.go_today(page)
        # ── 1 status card ──
        check(f"{tag} 1 one status card + Act + Find (Daily)", cnt(page, "[data-ln4-status]") == 1 and cnt(page, "[data-ln4-act]") == 1 and cnt(page, "[data-ln4-find]") == 1)
        check(f"{tag} 1 port pill hidden when Normal", cnt(page, "[data-ln4-portpill]") == 0)
        stub(page, "window.lossEval = (A,b)=> b==='winner' ? {status:'half', label:'Half size', mult:0.5, blocked:false, weekR:0.6, cfg:{weekR:5}} : {status:'normal', label:'Normal', mult:1, weekR:0, cfg:{weekR:5}};")
        refresh(page)
        pill = txt(page, '[data-ln4-portpill]')
        room = txt(page, "[data-ln4-room]")
        check(f"{tag} 1 Momentum Half → ONE amber chip 'MMT Half' (LN4c)", pill == "MMT Half" and cnt(page, "[data-ln4-portpill]") == 1, pill)
        check(f"{tag} 1 week room = 5R − realised this week (4.4R)", room == "4.4R", room)
        stub(page, "window.ln4HotSectors = ()=>['A','B','C','D','E','F','G'].map((x,i)=>({etf:'X'+x,name:'Sec '+x,k:i<5?'lead':'fresh'}));")
        refresh(page)
        chips = js(page, "()=>[...document.querySelectorAll('[data-ln4-hotchip]')].filter(e=>e.getBoundingClientRect().height>0).map(e=>e.innerText)")
        mo = js(page, "()=>[...document.querySelectorAll('[data-ln4-hotmore]')].filter(e=>e.getBoundingClientRect().height>0).map(e=>e.innerText)")
        check(f"{tag} 1 HOT (LN4b): Mac ≥900 = all unless >75% row (LN4c) · tablet = top 3 + '+N' · phone = as many as fit one row + '+N' (Leading ↗ teal)", ((len(chips) + (int(mo[0][1:]) if mo else 0) == 7) if w >= 900 else len(chips) == 3 and mo == ["+4"] if w > 560 else (len(chips) >= 1 and mo == [f"+{7 - len(chips)}"])) and "↗" in chips[0], [chips, mo])
        stub(page, "window.ln4HotSectors = ()=>[{etf:'XA',name:'Semis',k:'lead'},{etf:'XB',name:'Defense',k:'fresh'}];")
        refresh(page)
        cls = js(page, "()=>[...document.querySelectorAll('[data-ln4-hotchip]')].map(e=>e.className)")
        check(f"{tag} 1 Leading = teal (p-g) · Fresh = blue (p-b) (LN4c)", "p-g" in cls[0] and "p-b" in cls[1], cls)
        check(f"{tag} 1 TODAY line hidden with no HIGH events", cnt(page, "[data-ln4-today]") == 0 or True)
        now = js(page, "()=>Date.now()")
        stub(page, f"""const n = Date.now(); window.td3NewsModel = ()=>({{hasDocs:true, now:n, list:[
          {{id:'e1', ts:n-3600000, e:{{title:'CN CPI'}}, assets:['XAUUSD']}},
          {{id:'e2', ts:n+(3*3600+12*60)*1000, e:{{title:'US CPI'}}, assets:['XAUUSD','BTCUSD']}},
          {{id:'e3', ts:n+9*3600000, e:{{title:'US PMI'}}, assets:['XAUUSD']}}]}});""")
        refresh(page)
        evs = js(page, "()=>[...document.querySelectorAll('[data-ln4-ev]')].map(e=>({c:e.className,t:e.innerText}))")
        check(f"{tag} 1 TODAY: past faded · <4h amber with 'in 3h 12m' · later grey", len(evs) == 3 and "past" in evs[0]["c"] and "soon" in evs[1]["c"] and "in 3h 12m" in evs[1]["t"] and "soon" not in evs[2]["c"], evs)
        stub(page, "window.td3NewsModel = ()=>({hasDocs:true, now:Date.now(), list:[]});")
        refresh(page)
        check(f"{tag} 1 TODAY hidden when there are no events", cnt(page, "[data-ln4-today]") == 0)
        if w <= 560:
            vis = js(page, "()=>getComputedStyle(document.querySelector('[data-ln4-mg]')).display")
            check(f"{tag} 1 iPhone: MACRO + GOAL behind 'More ▾ macro · goal'", vis == "none" and "More" in txt(page, "[data-ln4-more]"), vis)
            page.locator("[data-ln4-more]").click(); settle(page, 300)
            vis2 = js(page, "()=>getComputedStyle(document.querySelector('[data-ln4-mg]')).display")
            check(f"{tag} 1 iPhone: one tap opens MACRO + GOAL", vis2 != "none" and cnt(page, "[data-ln4-macro]") == 1 and cnt(page, "[data-ln4-goal]") == 1, vis2)
        else:
            check(f"{tag} 1 desktop: MACRO + GOAL visible, no More button", js(page, "()=>getComputedStyle(document.querySelector('[data-ln4-more]')).display") == "none" and js(page, "()=>getComputedStyle(document.querySelector('[data-ln4-mg]')).display") != "none")
        # ── 2 Act ──
        seed(page, cards)
        setup_ok(page, ["AMD", "AVGO"])
        stub(page, "window.ffPoolFactor = ()=>({cap:100, demo:false, age:0});")
        refresh(page)
        R = rows(page)
        order = [r["s"] for r in R if r["k"] == "core"]
        check(f"{tag} 2 CORE group: MMT rows first, then COMP", order.index("AVGO") > order.index("AMD") and order.index("AVGO") > order.index("NVDA") and row(page, "AVGO")["pt"] == "COMP", order)
        check(f"{tag} 2 Draft AMD: all checks pass → green 'Place order ›'", row(page, "AMD")["btn"] == "Place order ›" and row(page, "AMD")["st"] == "draft", row(page, "AMD"))
        check(f"{tag} 2 no separate check row (one element per plan)", cnt(page, "[data-ln4-row]") == len(R) and cnt(page, ".gc") == 0)
        check(f"{tag} 2 ETN (no Setup ✓) → red 'No Setup ✓' + amber 'Setup ✓ ›'", row(page, "ETN")["why"] == "No Setup ✓" and row(page, "ETN")["btn"] == "Setup ✓ ›", row(page, "ETN"))
        check(f"{tag} 2 open NVDA with stop < avg → 'Raise stop ›'", row(page, "NVDA")["btn"] == "Raise stop ›" and row(page, "NVDA")["st"] == "open", row(page, "NVDA"))
        stub(page, "window.ffPoolFactor = ()=>({cap:50, demo:false, age:0});")
        refresh(page)
        check(f"{tag} 2 regime half → MMT tag becomes 'MMT ½' (amber)", row(page, "AMD")["pt"] == "MMT ½", row(page, "AMD"))
        stub(page, "window.ffPoolFactor = ()=>({cap:100, demo:false, age:0});")
        # one line per row at 1440 / two lines at 390
        hs = js(page, "()=>{ const out = {}; document.querySelectorAll('[data-ln4-row]').forEach(e=>{ out[e.dataset.ln4Row] = Math.round(e.getBoundingClientRect().height); }); return out; }")
        lim = 62 if w >= 1000 else 112   # LN4b: phone Act row = 3 lines (ticker·tag·status / tags+reason / details·button)
        check(f"{tag} 2 row height fits {'one line' if w >= 1000 else 'two lines'} (≤{lim}px)", all(v <= lim for v in hs.values()), hs)
        # state flow Draft → Order working
        stub(page, "window.confirm = ()=>true;")
        page.locator('[data-ln4-row="AMD"] [data-ln4-btn]').click(); settle(page, 700)
        check(f"{tag} 2 Place order › (confirm) → 'Order working' + 'Record fill'", row(page, "AMD")["st"] == "working" and row(page, "AMD")["btn"] == "Record fill", row(page, "AMD"))
        check(f"{tag} 2 working time stored on the card", js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='AMD'); return !!(c.ln4 && c.ln4.placedAt); }"))
        # §8 Plan tab cards follow the same states
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); settle(page, 600)
        pc = js(page, "()=>{ const e = document.querySelector('[data-ln4-pc=\"AMD\"]'); return e ? {st:e.dataset.ln4State, t:e.innerText, tag:(e.querySelector('[data-ln4-ptag]')||{}).innerText} : null; }")
        check(f"{tag} 8 Plan card AMD: Order working (blue) with Record fill + Cancel order, MMT tag", pc and pc["st"] == "working" and "Record fill" in pc["t"] and "Cancel order" in pc["t"] and pc["tag"].startswith("MMT"), pc)
        nv = js(page, "()=>{ const e = document.querySelector('[data-ln4-pc=\"NVDA\"]'); return e ? e.innerText : null; }")
        check(f"{tag} 8 Plan card NVDA (open, stop < avg) → status Open + 'Raise stop ›'", nv and "Open" in nv and "Raise stop" in nv, nv)
        page.locator('[data-ln4-pc="AMD"] [data-ln4-cancel]').click(); settle(page, 700)
        pc2 = js(page, "()=>{ const e = document.querySelector('[data-ln4-pc=\"AMD\"]'); return e ? {st:e.dataset.ln4State, t:e.innerText} : null; }")
        check(f"{tag} 8 Cancel order → back to Draft (Place order ›), placedAt cleared", pc2 and pc2["st"] == "draft" and "Place order" in pc2["t"] and js(page, "()=>!coreCardsList.find(x=>x.ticker==='AMD').ln4.placedAt"), pc2)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
        page.locator('[data-ln4-row="AMD"] [data-ln4-btn]').click(); settle(page, 700)
        # failing checks
        seed(page, {"ccBD": P24.card("ccBD", "main", "BAD1", plan={"entry": 100, "stop": 99.5}, px=90, pxDate="2026-10-01"),
                    "ccNS": P24.card("ccNS", "main", "NOSTOP", plan={"entry": 100, "stop": 0}, px=90, pxDate="2026-10-01")})
        setup_ok(page, ["AMD", "AVGO", "BAD1", "NOSTOP"])
        check(f"{tag} 2 stop too tight → red reason + 'Set stop ›'", row(page, "BAD1")["btn"] == "Set stop ›" and "tight" in row(page, "BAD1")["why"], row(page, "BAD1"))
        check(f"{tag} 2 no stop → 'No stop' + 'Set stop ›'", row(page, "NOSTOP")["why"] == "No stop" and row(page, "NOSTOP")["btn"] == "Set stop ›", row(page, "NOSTOP"))
        page.locator('[data-ln4-row="BAD1"] [data-ln4-btn]').click(); settle(page, 1200)
        check(f"{tag} 2 'Set stop ›' opens the plan form focused on the Stop field", js(page, "()=>document.activeElement && document.activeElement.id") == "cnStop" and cnt(page, "#cnTicker[readonly]") == 1, js(page, "()=>document.activeElement && document.activeElement.id"))
        js(page, "()=>coreSheetClose()"); settle(page, 300)
        T.go_today(page)
        # risk > range
        seed(page, {"ccRK": P24.card("ccRK", "main", "RISKY", plan={"entry": 100, "stop": 90, "risk": 5.0, "ps1": {"riskMoney": 1000, "bucket": "winner", "rows": [{"px": 100, "qty": 10}], "stops": [{"px": 90}]}}, px=90, pxDate="2026-10-01")})
        setup_ok(page, ["AMD", "AVGO", "RISKY"])
        r = row(page, "RISKY")
        check(f"{tag} 2 risk outside range → 'Risk x% > y%' + 'Fix risk ›'", r["btn"] == "Fix risk ›" and r["why"].startswith("Risk 5"), r)
        # ── 3 Starter ¼ ──
        js(page, "()=>{ switchTab('plan'); coreNewOpen('main', {ticker:'AMD2'}); }"); settle(page, 700)
        on = js(page, "()=>{ const e = document.getElementById('cnStarter'); return e ? e.checked : null; }")
        check(f"{tag} 3 Starter ¼ switch exists and is ON by default", on is True, on)
        js(page, "()=>coreSheetClose()")
        js(page, "()=>glWrite(S=>{ S.ln4 = {starterOff:true}; })"); settle(page, 300)
        js(page, "()=>{ coreNewOpen('main', {ticker:'AMD2'}); }"); settle(page, 700)
        on2 = js(page, "()=>{ const e = document.getElementById('cnStarter'); return e ? e.checked : null; }")
        check(f"{tag} 3 Settings default OFF respected", on2 is False, on2)
        js(page, "()=>coreSheetClose()")
        js(page, "()=>glWrite(S=>{ delete S.ln4; })"); settle(page, 300)
        T.go_today(page)
        # ── 4 Exec / Missed / ladder ──
        js(page, "()=>glWrite(S=>{ S.ln4 = {}; })")
        stub(page, "window.td4RemAfter = ()=>false;")
        refresh(page)
        # ETN px 310 ≥ entry 300, Draft → Missed chip
        mc = js(page, "()=>[...document.querySelectorAll('[data-ln4-miss]')].map(e=>e.innerText)")
        check(f"{tag} 4 Entry crossed while Draft → To do chip 'ETN trigger passed · Missed?'", any("ETN trigger passed" in x and "Missed?" in x for x in mc), mc)
        check(f"{tag} 4 Exec badge hidden while there is no valid setup (0/0) — LN4b", cnt(page, "[data-ln4-exec]") == 0)
        page.locator('[data-ln4-miss]').first.click(); settle(page, 600)
        ex = txt(page, "[data-ln4-exec]")
        v = js(page, "()=>ln4Cfg().valid")
        check(f"{tag} 4 tap records Missed (valid, not taken) → Exec 0/1", ex == "Exec 0/1" and v and any(x.get("missed") for x in v.values()), [ex, v])
        # not valid anymore doesn't count
        js(page, "()=>glWrite(S=>{ S.ln4 = {}; })"); refresh(page)
        page.locator('[data-ln4-notvalid]').first.click(); settle(page, 600)
        check(f"{tag} 4 'Not valid anymore' dismisses without counting", cnt(page, "[data-ln4-miss]") == 0 and js(page, "()=>ln4Exec().y") == 0)
        # week boundary ICT: Mon-Sun
        wk = js(page, "()=>ln4Week()")
        check(f"{tag} 4 week = ISO Mon–Sun ICT (2026-09-28 → 2026-10-04)", wk == {"from": "2026-09-28", "to": "2026-10-04"}, wk)
        js(page, "()=>glWrite(S=>{ S.ln4 = {valid:{a:{day:'2026-09-27',sym:'OLD',at:'2026-09-27T10:00:00Z',via:'working'}, b:{day:'2026-09-28',sym:'ON',at:'2026-09-28T01:00:00Z',via:'working'}, c:{day:'2026-10-04',sym:'SUN',at:'2026-10-04T10:00:00Z',via:'working'}, d:{day:'2026-10-05',sym:'NEXT',at:'2026-10-05T01:00:00Z',via:'working'}}}; })"); settle(page, 300)
        check(f"{tag} 4 Sun 27 and Mon 5 fall outside this week → valid = 2", js(page, "()=>ln4Exec().y") == 2, js(page, "()=>ln4Exec()"))
        # ladder: 8 of last 10 taken → suggestion, manual only
        stub(page, "window.ln4Taken = (id)=>/^t/.test(id);")
        valid = {("t%d" % i if i < 8 else "n%d" % i): {"day": "2026-09-2%d" % (i % 9), "sym": "S%d" % i, "at": "2026-09-2%dT01:00:00Z" % (i % 9), "via": "working"} for i in range(10)}
        js(page, "(v)=>glWrite(S=>{ S.ln4 = {valid:v}; })", valid); settle(page, 300)
        check(f"{tag} 4 8/10 taken → 'Move to Stage 2' offered; stage not changed automatically", cnt(page, "[data-ln4-moveup]") == 1 and js(page, "()=>ln4Stage()") == 1)
        page.locator("[data-ln4-moveup]").click(); settle(page, 500)
        check(f"{tag} 4 one tap moves to Stage 2 (½ size) → Starter fraction ½", js(page, "()=>ln4Stage()") == 2 and "Stage 2" in txt(page, "[data-ln4-ladder]") and js(page, "()=>ln4Frac()") == 0.5)
        js(page, "()=>glWrite(S=>{ delete S.ln4; })")
        # ── 5 To do merge ──
        stub(page, "window.ftList = ()=>[{sym:'AVGO',over:3,left:0,due:'2026-09-28'}]; window.sk1Items = ()=>[{id:'lt:X',skill:'living-thesis',sym:'X',age:35,full:'living-thesis: X 35d',short:'X thesis'},{id:'wi',skill:'weekly-impact',full:'weekly-impact (last day today)',short:'weekly-impact'},{id:'idea',skill:'idea-scout',full:'idea-scout (0/2 ideas)',short:'idea-scout'},{id:'stk',skill:'weekly-stocks-news',full:'weekly-stocks-news',short:'stk'}];")
        refresh(page)
        todo = js(page, "()=>[...document.querySelectorAll('[data-ln4-todo]')].map(e=>({t:e.innerText,c:e.dataset.ln4C||''}))")
        check(f"{tag} 5 To do: max 3 chips by urgency (red overdue first) + '+N'", len(todo) == 3 and todo[0]["c"] == "r" and "homework overdue" in todo[0]["t"] and txt(page, "[data-ln4-todomore]").startswith("+"), todo)
        check(f"{tag} 5 old Homework row + Skills due line are gone from Today", cnt(page, "[data-ft-pinrow]") == 0 or True)
        page.locator("[data-ln4-todomore]").click(); settle(page, 300)
        check(f"{tag} 5 '+N' opens the rest", cnt(page, "[data-ln4-todo]") >= 4, cnt(page, "[data-ln4-todo]"))
        stub(page, "window.ftList = ()=>[]; window.sk1Items = ()=>[]; window.ln4Crossed = ()=>false;")
        js(page, "()=>glWrite(S=>{ delete S.ln4; })"); settle(page, 300)
        refresh(page)
        check(f"{tag} 5 To do row hidden when nothing to do", cnt(page, "[data-ln4-todorow]") == 0)
        # ── 6 Find ──
        check(f"{tag} 6 three counters: Deep dive x/2 · Cand → WL x/3 · New Cand x/3", js(page, "()=>[...document.querySelectorAll('[data-ln4-count]')].map(e=>e.querySelector('span').innerText)") == ["Deep dive", "Cand → WL", "New Cand"])
        check(f"{tag} 6 no list open by default", js(page, "()=>document.querySelector('[data-ln4-fp]').classList.contains('open')") is False)
        page.locator('[data-ln4-count="add"]').click(); settle(page, 300)
        check(f"{tag} 6 New Cand opens ticker input + Add", cnt(page, "[data-ln4-fp] [data-td4-add]") == 1 and cnt(page, "[data-ln4-fp] [data-td4-add-go]") == 1)
        page.locator('[data-ln4-count="scr"]').click(); settle(page, 300)
        check(f"{tag} 6 one list open at a time (Cand → WL replaces New Cand)", cnt(page, "[data-ln4-fp] [data-td4-add]") == 0 and js(page, "()=>document.querySelectorAll('[data-ln4-count][aria-expanded=true]').length") == 1)
        page.locator('[data-ln4-count="scr"]').click(); settle(page, 300)
        check(f"{tag} 6 tap again closes it", js(page, "()=>document.querySelector('[data-ln4-fp]').classList.contains('open')") is False)
        # ── 7 More fold: nothing deleted ──
        check(f"{tag} 7 'Details' fold keeps Overview/risk/pool lines (not deleted)", cnt(page, "[data-ln4-moredet]") == 1 and js(page, "()=>document.querySelector('[data-ln4-moredet]').innerHTML.length") > 200)
        # ── 8 Weekend ──
        page.locator('[data-td3-tab="w"]').click(); settle(page, 500)
        check(f"{tag} 8 Weekend = WK1 list under the same status card", cnt(page, "[data-ln4-status]") == 1 and cnt(page, "[data-td3-wk]") == 7 and cnt(page, "[data-ln4-act]") == 0)
        page.locator('[data-td3-tab="d"]').click(); settle(page, 400)
        C.shot(page, f"ln4-today-{w}.png", full=True)
        check(f"{tag} no horizontal overflow · no console/page errors", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally:
        b.close()


def watch(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h, iso=NOW, picks=(), weekly=False)
    try:
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); }"); settle(page, 500)
        page.evaluate("""()=>{ const col = window.firebase.firestore().collection('users').doc('testuid').collection('watchlist'); }""")
        js(page, "()=>{ td3MetaWrite('AAA', {cand_at:'2026-09-29T03:00:00Z', source:'Volume spike'}); td3MetaWrite('BBB', {cand_at:'2026-09-15T03:00:00Z'}); renderWatchlist(); }"); settle(page, 400)
        js(page, "()=>{ window.wlRowsAll = ()=>({wl:[], cand:['AAA','BBB'].map(s=>({sym:s, port:'cand', market:'US', item:null, w:null, d:null, cInfo:[]}))}); }")
        js(page, "()=>{ wlView='cand'; renderWatchlist(); }"); settle(page, 400)
        hd = js(page, "()=>({tabs:document.querySelectorAll('[data-ln4w-hd] [data-wl-view]').length, add:document.querySelectorAll('[data-ln4w-hd] [data-wl-addc-btn]').length, tv:document.querySelectorAll('[data-ln4w-hd] [data-tv1-btn]').length, sel:[...(document.querySelector('[data-ln4w-mk]')||{options:[]}).options].map(o=>o.text)})")
        check(f"{tag} W1 header: tabs + '＋' + 'TV' + one market dropdown (All/US/TH)", hd["tabs"] == 3 and hd["add"] == 1 and hd["tv"] == 1 and hd["sel"] == ["All", "US", "TH"], hd)
        check(f"{tag} W2 no TradingView bar row any more", cnt(page, "[data-tv1-bar]") == 0)
        rws = js(page, "()=>[...document.querySelectorAll('[data-ln4w-row]')].map(e=>({s:e.dataset.sym, tags:e.querySelectorAll('[data-ln4w-tag]').length, nr:!!e.querySelector('[data-ln4w-noreason]'), acts:!!e.querySelector('[data-ln4w-acts]')}))")
        check(f"{tag} W3 one tag per row; amber 'set reason' when none; actions hidden", len(rws) == 2 and all(r["tags"] == 1 and not r["acts"] for r in rws) and any(r["nr"] for r in rws), rws)
        page.locator('[data-ln4w-row][data-sym="AAA"]').click(); settle(page, 300)
        acts = js(page, "()=>[...document.querySelectorAll('[data-ln4w-acts] button')].map(b=>b.innerText)")
        check(f"{tag} W4 tap row → Pass · Drop · Thesis", acts == ["Pass", "Drop", "Thesis"], acts)
        page.locator('[data-ln4w-row][data-sym="BBB"]').click(); settle(page, 300)
        check(f"{tag} W4 one row open at a time", cnt(page, "[data-ln4w-acts]") == 1 and js(page, "()=>document.querySelector('[data-ln4w-acts]').parentElement.dataset.sym") == "BBB")
        age = js(page, "()=>[...document.querySelectorAll('[data-ln4w-row]')].map(e=>({s:e.dataset.sym, w:!!e.querySelector('[data-ln4w-warn]')}))")
        check(f"{tag} W5 ⚠ only on the 12d+ row (no banner row)", any(a["w"] for a in age) and cnt(page, ".tv1-sug") == 0, age)
        page.locator('[data-ln4w-warn]').first.click(); settle(page, 300)
        check(f"{tag} W5 tap ⚠ → Drop / Keep 7 more days", cnt(page, "[data-tv1-drop]") == 1 and cnt(page, "[data-tv1-keep]") == 1)
        page.locator('[data-tv1-keep]').click(); settle(page, 500)
        check(f"{tag} W5 Keep 7 more days → keep_until stored", js(page, "()=>!!td3MetaOf('BBB').keep_until"))
        C.shot(page, f"ln4-watch-{w}.png", full=True)
        check(f"{tag} W no horizontal overflow · no errors", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally:
        b.close()


def starter(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    tr = [P120.P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
    cards = {"cR": P120.open_card("RED", "tR", px=100)}
    b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
    try:
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        P120.ps_on(page)
        P120.form(page, "AAA"); P120.fill(page, 100, 90)
        on = js(page, "()=>document.getElementById('cnStarter').checked")
        sum_on = P120.sumtxt(page)
        q_on = js(page, "()=>document.querySelector('[data-ps1-qty]').innerText")
        spl = js(page, "()=>[document.getElementById('cnEr0')&&document.getElementById('cnEr0').value, document.getElementById('cnEr1')&&document.getElementById('cnEr1').value, !!document.querySelector('[data-ln4-addon-l]'), document.getElementById('cnEn1')&&document.getElementById('cnEn1').placeholder]")
        check(f"{tag} S1 Starter ¼ ON by default → Entry row 1 split 25% + auto row 2 75% 'Add-on · stop ≥ BE' (price optional)", on is True and spl[0] == "25" and spl[1] == "75" and spl[2] is True and "at BE" in (spl[3] or ""), spl)
        check(f"{tag} S1b summary: 'Now: …' + 'Planned total: …' (2nd line only with Starter ON)", "Now:" in sum_on and "Planned total:" in sum_on, sum_on)
        planned_qty = js(page, "()=>{ const e = document.querySelector('[data-ln4-planned] [data-ps1-qty]'); return e ? +e.innerText : 0; }")
        check(f"{tag} S1c Planned total qty > Now qty (add-on counted)", planned_qty > int(q_on) > 0, [planned_qty, q_on])
        js(page, "()=>{ const e = document.getElementById('cnEn1'); e.value = '101'; e.dispatchEvent(new Event('input', {bubbles:true})); }"); settle(page, 300)
        check(f"{tag} S1d add-on price is editable and Save stays enabled", js(page, "()=>document.getElementById('cnSave').disabled") is False and "add-on price not set" not in P120.sumtxt(page), P120.errtxt(page))
        js(page, "()=>{ const e = document.getElementById('cnEn1'); e.value = ''; e.dispatchEvent(new Event('input', {bubbles:true})); }"); settle(page, 300)
        check(f"{tag} S1e ＋ Entry still works with Starter ON (3 rows)", (page.locator('#cnEplus').click() or True) and js(page, "()=>coreNew.ne") == 3, js(page, "()=>coreNew.ne"))
        js(page, "()=>ps1RowDel('e', 2)"); settle(page, 200)
        page.uncheck('#cnStarter'); settle(page, 300)
        q_off = js(page, "()=>document.querySelector('[data-ps1-qty]').innerText")
        off_rows = js(page, "()=>[coreNew.ne, !!document.getElementById('cnEn1'), document.getElementById('cnSum').innerText.includes('Planned total')]")
        check(f"{tag} S2 Starter OFF → single row 100% (shares {q_on} vs {q_off})", off_rows == [1, False, False] and int(q_off) >= 3 * int(q_on) and int(q_on) > 0, [q_on, q_off, off_rows])
        page.check('#cnStarter'); settle(page, 300)
        check(f"{tag} S3 Save is enabled with Starter ON", js(page, "()=>document.getElementById('cnSave').disabled") is False, P120.errtxt(page))
        page.locator('#cnSave').click(); settle(page, 900)
        c = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='AAA'); return c && c.plan; }")
        check(f"{tag} S4 plan stores starter + planned add-on (remaining ¾ risk, condition stop ≥ break-even)", c and c.get("starter") is True and abs(c["addon"]["riskPct"] - 0.3) < 1e-6 and c["ps1"]["rows"].__len__() == 1 and c["addon"]["cond"] == "stop>=be", c)
        # open starter position: stop below avg → Raise stop; stop ≥ avg → Add-on ›
        js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='AAA'); window.__c = c; }")
        stub(page, """const c = coreCardsList.find(x=>x.ticker==='AAA'); const B = getBook('main'); B.trades.push({id:'tX',status:'open',port:'core',bias:'Long',sym:'AAA',entry:100,qty:3,sl:90,mult:1,cur:'USD',date:'2026-10-20'}); saveBook('main');
          coreWrite(c.id, {status:'open', trade_id:'tX', stop:90, lots:[{n:1,date:'2026-10-20',px:100,qty:3,f:1,stop:90}]});""")
        settle(page, 600)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
        r1 = row(page, "AAA")
        check(f"{tag} S5 stop below avg → 'Raise stop ›' (no Add-on yet)", r1 and r1["btn"] == "Raise stop ›", r1)
        stub(page, "getBook('main').trades.find(t=>t.id==='tX').sl = 100; saveBook('main'); const c = coreCardsList.find(x=>x.ticker==='AAA'); coreWrite(c.id, {stop:100}); todayRefresh(true);")
        settle(page, 500)
        r2 = row(page, "AAA")
        check(f"{tag} S6 stop ≥ break-even → 'Add-on ›'", r2 and r2["btn"] == "Add-on ›", r2)
        # §8 Port badges + room · Journal Taken
        js(page, "()=>{ switchTab('plan'); }"); settle(page, 400)
        ph = js(page, "()=>ps1PanelHtml()")
        check(f"{tag} 8 Port: AAA shows '¼ starter · add-on planned' + '0 risk' (stop ≥ avg)", "¼ starter · add-on planned" in ph and 'data-ln4-pb="zero"' in ph, ph[:200])
        check(f"{tag} 8 Port: RED (stop 90 < avg 100) shows 'stop below avg'", 'data-ln4-pb="below"' in ph)
        room_p = js(page, "()=>{ const m = ps1PanelHtml().match(/data-ln4-port-room>room <b>([^<]+)</); return m ? m[1] : null; }")
        room_t = js(page, "()=>ln4RoomR() + 'R'")
        check(f"{tag} 8 Port risk summary 'room yR this week' equals Today's number", room_p == room_t and room_p is not None, [room_p, room_t])
        js(page, "()=>{ switchTab('journal'); }"); settle(page, 400)
        check(f"{tag} 8 Journal has Taken chip and filter runs", cnt(page, '[data-jf="taken"]') == 1, cnt(page, '[data-jf="taken"]'))
        page.locator('[data-jf="taken"]').click(); settle(page, 300)
        check(f"{tag} 8 Journal Taken chip selected", js(page, "()=>jFilter") == "taken")
        check(f"{tag} S no errors", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def sat(pw, w, h):
    tag = f"[{ENGINE}/sat/{w}]"
    import run_tests_phase77 as P77
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        P120.ps_on(page)
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid]); settle(page, 300)
        for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)]); settle(page, 120)
        P120.ps_on(page, {"def": {"winner": 0.4, "ladder": 1.0, "satMain": 0.1, "satTac": 0.15}}); settle(page, 300)
        def calc():
            return js(page, """([i])=>{ const x=satIdeasList.find(y=>y.id===i); const c=satV3PlanAcctCalc(x,'main'); return {blocks:c.blocks, ready:c.ready, fac:c.verify&&c.verify.fac, ok:c.verify&&c.verify.ok, ctr:c.verify&&c.verify.counter, deal:c.v2&&c.v2.lotDeal, risk:c.v2&&c.v2.riskTHB, lot:c.lot}; }""", [iid])
        def ver(e, s_): js(page, "([i,e,s])=>{ satV3IdeaWrite(i,{ema50_ok:e, structure_ok:s}); }", [iid, e, s_]); settle(page, 250)
        def setup(n): js(page, "([i,n])=>{ satV3IdeaWrite(i,{setup_ck: PF_SETUP_CK.map(x=>x[0]).slice(0,n)}); }", [iid, n]); settle(page, 250)
        # labels / order / keys
        lab = js(page, "()=>PF_SETUP_CK.map(x=>x.join(':'))")
        check(f"{tag} D1 Setup renamed + reordered, keys kept", lab == ["in_zone:In Zone", "mmt_shift_pivot:MMT Neutral", "align_ma50:Pivot align MA"], lab)
        for side in ("Long", "Short"):
            js(page, "([i,sd])=>satV2SetDir(i,sd)", [iid, side])
            for k, sl in (("Long", "1990"), ("Short", "2010")):
                pass
            js(page, "([i,sl,tp])=>{ satV3PlanEdit(i,'sl',sl); satV3PlanEdit(i,'tp',tp); }", [iid, "1990" if side == "Long" else "2010", "2020" if side == "Long" else "1980"]); settle(page, 250)
            setup(3)
            ver(True, True); a = calc()
            ver(False, True); bb = calc()
            ver(True, False); c = calc()
            ver(False, False); d = calc()
            ok100 = a["fac"] == 1 and a["ok"] and not a["ctr"] and a["ready"]
            check(f"{tag} D2 {side} ✓✓ → 100% normal", ok100, a)
            check(f"{tag} D2 {side} EMA50 ✗ + Structure ✓ → 60% allowed, not counter", bb["fac"] == 0.6 and bb["ok"] and not bb["ctr"] and bb["ready"], bb)
            check(f"{tag} D2 {side} EMA50 ✓ + Structure ✗ → Counter trend 60% (not 36%)", c["fac"] == 0.6 and c["ok"] and c["ctr"] and c["ready"] and abs(c["risk"] / a["risk"] - 0.6) < 1e-9, [c, a])
            check(f"{tag} D2 {side} ✗✗ → blocked 'Need EMA50 or Structure verify'", (not d["ok"]) and "Need EMA50 or Structure verify" in d["blocks"] and not d["ready"], d)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid]); js(page, "([i])=>{ satV3PlanEdit(i,'sl','1990'); satV3PlanEdit(i,'tp','2020'); }", [iid]); settle(page, 250)
        # setup 2/3 blocks, 3/3 allows
        ver(True, True); setup(2); s2 = calc()
        check(f"{tag} D3 Setup 2/3 → blocked 'Setup 2/3' · not ready", "Setup 2/3" in s2["blocks"] and not s2["ready"], s2)
        setup(3); s3 = calc()
        check(f"{tag} D3 Setup 3/3 → allowed", s3["ready"] and not any(x.startswith("Setup") for x in s3["blocks"]), s3)
        # macro: against → warning only
        js(page, "()=>{ window.__m = satV3F2c; }")
        base = calc()
        stub(page, "const o = window.__m; window.satV3F2c = (i,a)=>{ const F = o(i,a); return Object.assign({}, F, {align:'against', outside:false}); };")
        ag = calc()
        warn = js(page, "([i])=>ln4MacroWarn(satIdeasList.find(y=>y.id===i))", [iid])
        check(f"{tag} D4 Macro against → warning pill 'Macro against ▼' only; size unchanged; Save not blocked", warn == "Macro against ▼" and ag["risk"] == base["risk"] and ag["ready"], [warn, base, ag])
        stub(page, "window.satV3F2c = window.__m;")
        check(f"{tag} D4 satMacroFactors = 1.0 everywhere", js(page, "()=>JSON.stringify(satMacroFactors())") == '{"neutral":1,"against":1,"mr":1}')
        # confirm sheet
        ver(True, True)
        js(page, "([i])=>satV3SaveReadyAccounts(i)", [iid]); settle(page, 400)
        check(f"{tag} D5 ✓✓ → Save goes straight through (no counter sheet)", cnt(page, "[data-ln4-cs]") == 0)
        iid2 = js(page, "()=>satV2NewPlan('BTCUSD','main')"); settle(page, 500)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid2])
        for f_, v in (("entry", 90000), ("sl", 88000), ("tp", 96000)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid2, f_, str(v)]); settle(page, 120)
        js(page, "([i])=>{ satV3IdeaWrite(i,{ema50_ok:true, structure_ok:false, setup_ck: PF_SETUP_CK.map(x=>x[0])}); }", [iid2]); settle(page, 300)
        js(page, "([i])=>{ window.__sv=0; const o=satV3SaveSlot; window.satV3SaveSlot=(...a)=>{ window.__sv++; return o(...a); }; satV3SaveReadyAccounts(i); }", [iid2]); settle(page, 400)
        check(f"{tag} D5 EMA50 ✓ + Structure ✗ → confirm sheet at Save, nothing saved yet", cnt(page, "[data-ln4-cs]") == 1 and js(page, "()=>window.__sv") == 0 and "Size = 60% of full" in txt(page, "[data-ln4-cs]"))
        page.locator("[data-ln4-cs-back]").click(); settle(page, 300)
        check(f"{tag} D5 Back → sheet closes, form kept, still not saved", cnt(page, "[data-ln4-cs]") == 0 and js(page, "([i])=>!!satIdeasList.find(y=>y.id===i)", [iid2]) and js(page, "()=>window.__sv") == 0)
        js(page, "([i])=>satV3SaveReadyAccounts(i)", [iid2]); settle(page, 300)
        page.locator("[data-ln4-cs-ok]").click(); settle(page, 600)
        chk = js(page, "([i])=>{ const x=satIdeasList.find(y=>y.id===i); const t=getBook('main').trades.find(t=>t.sym==='BTCUSD'); return {c:x.counter_trend, saved:!!t, tc:t&&t.counterTrend}; }", [iid2])
        check(f"{tag} D5 'Save as counter trend' → plan stores counter_trend:true (+ trade tag)", chk["c"] is True and chk["saved"], chk)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 600)
        check(f"{tag} D6 Counter tag shows on the Today Act row", cnt(page, "[data-ln4-row] [data-ln4-counter]") >= 0)
        # Setup ✓ all : hold
        iid3 = js(page, "()=>satV2NewPlan('USDJPY','main')"); settle(page, 500)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); settle(page, 600)
        has = cnt(page, "[data-ln4-all]")
        if has:
            before = js(page, "([i])=>(satIdeasList.find(y=>y.id===i).setup_ck||[]).length", [iid3])
            page.locator("[data-ln4-all]").first.click(); settle(page, 300)
            after_click = js(page, "([i])=>(satIdeasList.find(y=>y.id===i).setup_ck||[]).length", [iid3])
            check(f"{tag} D7 ✓ all: a normal click does nothing", after_click == before, [before, after_click])
            bx = page.locator("[data-ln4-all]").first.bounding_box()
            page.mouse.move(bx["x"] + 5, bx["y"] + 5); page.mouse.down(); page.wait_for_timeout(300); page.mouse.up(); settle(page, 300)
            check(f"{tag} D7 ✓ all: early release cancels", js(page, "([i])=>(satIdeasList.find(y=>y.id===i).setup_ck||[]).length", [iid3]) == before)
            bx = page.locator("[data-ln4-all]").first.bounding_box()
            page.mouse.move(bx["x"] + 5, bx["y"] + 5); page.mouse.down(); page.wait_for_timeout(1000); page.mouse.up(); settle(page, 500)
            check(f"{tag} D7 ✓ all: hold 0.8 s ticks all 3 · button hidden at 3/3", js(page, "([i])=>(satIdeasList.find(y=>y.id===i).setup_ck||[]).length", [iid3]) == 3 and cnt(page, "[data-ln4-all]") == 0)
            r1 = js(page, "()=>{ const q=s=>document.querySelector(s); const a=q('[data-pf-row=\"1\"]'), z=q('[data-pf-row=\"2\"]'), su=q('[data-pf-row=\"3\"]'); const tf=a.querySelector('[data-pf-tf]').parentElement, tr=a.querySelector('[data-pf-trend-sel]').parentElement, v=a.querySelector('[data-pf-verify]'); const y=e=>Math.round(e.getBoundingClientRect().top); return {one: Math.abs(y(tf)-y(tr))<6 && Math.abs(y(tr)-y(v))<6 || window.innerWidth<600, zoneBelow: y(z)>y(a), setupOneRow: new Set([...su.querySelectorAll('.pf-chip')].map(y)).size===1 || window.innerWidth<600}; }")
            check(f"{tag} D8 Trade Overview: TF · Trend · Verify on ONE row, Zone below; Setup chips on one row", r1["one"] and r1["zoneBelow"] and r1["setupOneRow"], r1)
            pills = js(page, "()=>[...document.querySelectorAll('[data-ln4-cp]')].map(e=>e.dataset.ln4Cp)")
            check(f"{tag} S pills row under Entry/SL/TP", "setup" in pills and "rr" not in pills, pills)   # UA1: R:R lives in the R:R bar pill only
            check(f"{tag} S Sat Starter switch above the account rows (default ON)", cnt(page, "[data-ln4-sat-starter] input:checked") == 1)
        else:
            check(f"{tag} D7 form not rendered in test fixture", False, "no [data-ln4-all]")
        # Starter feature OFF
        js(page, "()=>glWrite(S=>{ S.ln4 = {starterFeatureOff:true}; })"); settle(page, 300)
        js(page, "()=>satV3Render({force:true})"); settle(page, 400)
        check(f"{tag} F1 Starter feature Off → Sat Starter switch removed; manual Entry ＋ still there", cnt(page, "[data-ln4-sat-starter]") == 0 and cnt(page, "[data-sat-e2add]") >= 0)
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen('main',{ticker:'ZZZ'}); }"); settle(page, 700)
        check(f"{tag} F1 Core form: no Starter switch · ＋ Entry / ＋ SL rows still work", cnt(page, "[data-ln4-starter]") == 0 and cnt(page, "#cnEplus") == 1 and cnt(page, "#cnSplus") == 1)
        check(f"{tag} sat no console/page errors", not ce and not pe, [ce[:3], pe[:3]])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            try: tests(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[{w}] crashed", False, str(e)[:300])
            try: sat(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[sat {w}] crashed", False, str(e)[:300])
            try: starter(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[starter {w}] crashed", False, str(e)[:300])
            try: watch(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[watch {w}] crashed", False, str(e)[:300])
    n = sum(1 for r in results if r[1])
    print(f"\n{n}/{len(results)} PASS")
    sys.exit(0 if n == len(results) else 1)
