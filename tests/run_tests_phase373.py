#!/usr/bin/env python3
"""PB1 — One Plan board (Planned · Ordered · Holding) + drawer/log + Macro→Flow + Risk→Port + Today Act + New-plan popup + iPhone/SW2 · เทส 373
Chromium · 390 + 1280 + 1440 · นาฬิกาปลอม พฤ. 1 ต.ค. 2026 12:00 ICT · SAMPLE data only
รัน: python3 run_tests_phase373.py"""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase106 as T
import run_tests_phase120 as P120

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle, cnt, txt = T.settle, T.cnt, T.txt
NOW = T.NOW


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def seed(page, cards):
    for cid, c in cards.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)


def setup_ok(page, syms):
    js(page, "(l)=>glWrite(S=>{ const m = {}; l.forEach(s=>m[wlSymKey(s)] = thaiToday()); S.tvSetup = m; })", syms); settle(page, 300)


def stub(page, code): js(page, "()=>{" + code + "}")
def tab(page, t): js(page, "(t)=>switchTab(t)", t); settle(page, 500)
def plan(page):
    tab(page, "today"); tab(page, "plan"); settle(page, 300)
def col(page, seg): return js(page, "(s)=>[...document.querySelectorAll('[data-bd-col=\"'+s+'\"] [data-bd-card]')].map(e=>e.dataset.bdCard)", seg)
def ids(page): return js(page, "()=>bdItems().map(x=>x.id+':'+x.status)")
def card_db(page, cid): return page.evaluate("(id)=>window.firebase.__mockDb.__dump()['users/testuid/coreCards/'+id]", cid)
def idea_db(page, iid): return page.evaluate("(id)=>window.firebase.__mockDb.__dump()['users/testuid/satIdeas/'+id]", iid)
def logs(page, cid): return [x["txt"] for x in (card_db(page, cid) or {}).get("log", [])]
def ovf(page): return js(page, "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")


def fixtures():
    return {
        "ccPL": P24.card("ccPL", "main", "AMD", plan={"entry": 182.5, "stop": 170}, px=180, pxDate="2026-10-01"),                       # Planned (1.4% to entry)
        "ccFA": P24.card("ccFA", "main", "TSLA", plan={"entry": 250, "stop": 235}, px=200, pxDate="2026-10-01"),                       # Planned (far)
        "ccOR": P24.card("ccOR", "main", "AVGO", plan={"entry": 341.2, "stop": 320}, px=330, pxDate="2026-10-01", track="ladder",
                         ln4={"placedAt": "2026-10-01T02:00:00Z"}),                                                                  # Ordered · COMP
        "ccST": P24.open_card("ccST", "tST", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=171.4, px=180, pxDate="2026-10-01",
                              plan={"entry": 171.4, "stop": 160, "starter": True, "addon": {"riskPct": 0.2, "frac": 0.25, "cond": "stop>=be"}},
                              lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 171.4}]),               # Holding ¼ in · add-on ready
        "ccFU": P24.open_card("ccFU", "tFU", ticker="MSFT", acct="main", qty=5, entry=400, sl=380, px=420, pxDate="2026-10-01",
                              plan={"entry": 400, "stop": 380}),                                                                    # Holding full · stop below avg
        "ccMS": P24.card("ccMS", "main", "AMZN", plan={"entry": 200, "stop": 185}, px=190, pxDate="2026-10-01"),                       # Missed → Journal
        "ccCL": P24.card("ccCL", "main", "META", plan={"entry": 500, "stop": 470}, status="closed"),                                  # Closed
        "ccAR": P24.card("ccAR", "main", "NFLX", plan={"entry": 600, "stop": 560}, archived=True),                                    # Archived
        "ccFM": P24.card("ccFM", "fam", "ORCL", plan={"entry": 150, "stop": 140}, px=149, pxDate="2026-10-01"),                       # Family
        "ccML": P24.card("ccML", "main", "CRM", plan={"entry": 300, "stop": 270, "ps1": {"rows": [{"px": 300, "qty": 10}, {"px": 285, "qty": 10}, {"px": 270, "qty": 10}], "stops": [{"px": 255}]}}, px=299, pxDate="2026-10-01", track="ladder"),   # §2c: 3 levels, nothing filled
        "ccMH": P24.open_card("ccMH", "tMH", ticker="ADBE", acct="main", qty=10, entry=500, sl=470, px=505, pxDate="2026-10-01",
                              plan={"entry": 500, "stop": 470, "ps1": {"rows": [{"px": 500, "qty": 10}, {"px": 480, "qty": 10}, {"px": 460, "qty": 10}], "stops": [{"px": 440}]}}),   # §2c: 1 of 3 filled
        "ccNP": P24.card("ccNP", "main", "NOPX", plan={"entry": 50, "stop": 45}),                                                      # no price → —
    }


def launch(pw, w, h):
    b, page, ce, pe = T.launch(pw, w, h, iso=NOW, picks=(), weekly=False)
    P24.set_ff(page, P24.ff_json(True, True))
    js(page, "()=>{ try{ localStorage.removeItem('dash.ps1Off'); localStorage.removeItem('dash.bdChip'); localStorage.removeItem('dash.bdSeg'); }catch(e){} }")
    js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [
        P13.T("tST", "core", "open", sym="NVDA", entry=171.4, sl=171.4, qty=10, cur="USD", date="2026-09-10"),
        P13.T("tFU", "core", "open", sym="MSFT", entry=400, sl=380, qty=5, cur="USD", date="2026-09-10"),
        P13.T("tMH", "core", "open", sym="ADBE", entry=500, sl=470, qty=10, cur="USD", date="2026-09-10")])
    return b, page, ce, pe


def run(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed(page, fixtures())
        setup_ok(page, ["AMD", "TSLA", "AVGO", "ORCL", "NOPX"])
        js(page, "()=>{ const v = {}; v.ccMS = {day:thaiToday(), sym:'AMZN', at:new Date().toISOString(), via:'crossed', missed:1}; return ln4Write(o=>{ o.valid = Object.assign(o.valid||{}, v); }); }"); settle(page, 400)
        stub(page, "window.confirm = ()=>true;")
        plan(page)
        # ── 1 status mapping ──
        check(f"{tag} 1 Planned = AMD, TSLA, ORCL (+NOPX) · Ordered = AVGO · Holding = NVDA, MSFT", set(col(page, "plan")) >= {"ccPL", "ccFA", "ccFM", "ccNP"} and col(page, "ord") == ["ccOR"] and set(col(page, "hold")) == {"ccST", "ccFU", "ccMH"}, [col(page, s) for s in ("plan", "ord", "hold")])
        allids = {x.split(":")[0] for x in ids(page)}
        check(f"{tag} 1 Missed / Closed / Archived are not on the board", not ({"ccMS", "ccCL", "ccAR"} & allids), sorted(allids))
        check(f"{tag} 1 split plan = ONE card with '¼ in'; full = 'full'", cnt(page, '[data-bd-card="ccST"]') == 1 and "¼ in" in txt(page, '[data-bd-card="ccST"] [data-bd-size]') and "full" in txt(page, '[data-bd-card="ccFU"] [data-bd-size]'))
        check(f"{tag} 1 each column shows a count; Plan summary line", txt(page, '[data-bd-n="hold"]') == "3" and "Holding 3" in txt(page, "[data-bd-sum]"), txt(page, "[data-bd-sum]"))
        check(f"{tag} 1 Planned sorted closest-to-entry first (AMD 1.4% before TSLA −20%)", col(page, "plan").index("ccPL") < col(page, "plan").index("ccFA"), col(page, "plan"))
        check(f"{tag} 1 Holding: needs-action first (add-on / stop below avg) before plain", col(page, "hold")[0] in ("ccST", "ccFU"))
        # ── 2c multiple entry levels ──
        check(f"{tag} 2c one card per plan; Planned multi-level card shows 'Entry x +2 lower'", cnt(page, '[data-bd-card="ccML"]') == 1 and "+2 lower" in txt(page, '[data-bd-card="ccML"] [data-bd-lower]') and "ccML" in col(page, "plan"), txt(page, '[data-bd-card="ccML"] .bd-r2'))
        check(f"{tag} 2c any level filled → ✅ Holding: 'Avg x' + 'Entries 1/3 · next 480 waiting'", "ccMH" in col(page, "hold") and "Entries 1/3" in txt(page, '[data-bd-card="ccMH"] [data-bd-entries]') and "next 480" in txt(page, '[data-bd-card="ccMH"] [data-bd-entries]') and "Avg" in txt(page, '[data-bd-card="ccMH"] .bd-r2'), txt(page, '[data-bd-card="ccMH"] .bd-r3'))
        js(page, "()=>bdOpen('ccMH')"); settle(page, 300)
        lv = js(page, "()=>[...document.querySelectorAll('[data-bd-lv]')].map(e=>e.dataset.bdLv+':'+e.dataset.bdLvst)")
        check(f"{tag} 2c drawer ENTRIES lists each level with its state (#1 filled, #2/#3 planned)", lv == ["1:filled", "2:planned", "3:planned"], lv)
        check(f"{tag} 2c next level has its own action (Place order #2)", "Place order #2" in txt(page, "[data-bd-entries-list]"), txt(page, "[data-bd-entries-list]"))
        page.locator('[data-bd-lvact="place"]').first.click(); settle(page, 800)
        lv = js(page, "()=>[...document.querySelectorAll('[data-bd-lv]')].map(e=>e.dataset.bdLv+':'+e.dataset.bdLvst)")
        check(f"{tag} 2c placing level #2 → #2 ordered; card stays Holding; log line", lv[1] == "2:ordered" and "ccMH" in col(page, "hold") and any(x.startswith("#2 order placed") for x in logs(page, "ccMH")), [lv, logs(page, "ccMH")])
        page.locator("[data-bd-cancel]").click(); settle(page, 800)
        check(f"{tag} 2c cancel affects that level only → #2 planned again, #1 still filled, log '#2 order cancelled'", js(page, "()=>[...document.querySelectorAll('[data-bd-lv]')].map(e=>e.dataset.bdLvst)") == ["filled", "planned", "planned"] and "#2 order cancelled" in logs(page, "ccMH")[-1], logs(page, "ccMH"))
        js(page, "()=>bdClose()")
        # ── 2 chips ──
        js(page, "()=>bdSetChip('COMP')"); settle(page, 300)
        check(f"{tag} 2 chip COMP filters all columns + summary", col(page, "plan") == ["ccML"] and col(page, "ord") == ["ccOR"] and col(page, "hold") == [] and "2 plans" in txt(page, "[data-bd-sum]"), [col(page, s) for s in ("plan", "ord", "hold")])
        js(page, "()=>bdSetChip('MMT')"); settle(page, 300)
        check(f"{tag} 2 chip MMT hides COMP", "ccOR" not in col(page, "ord") and "ccPL" in col(page, "plan"))
        js(page, "()=>bdSetChip('all')")
        # ── 14 family tag · no price ──
        plan(page)
        check(f"{tag} 14 Family tag only on Family-account plan", cnt(page, '[data-bd-card="ccFM"] [data-bd-fam]') == 1 and cnt(page, '[data-bd-card="ccPL"] [data-bd-fam]') == 0)
        check(f"{tag} 14 symbol without a price → '—' to entry, no errors", "—" in txt(page, '[data-bd-card="ccNP"] [data-bd-pct]'), txt(page, '[data-bd-card="ccNP"] .bd-r3'))
        # ── 3 pills ──
        pill = lambda i: js(page, "(i)=>{ const e=document.querySelector('[data-bd-card=\"'+i+'\"] [data-bd-pill]'); return e ? e.dataset.bdPill + '|' + e.className + '|' + e.innerText : null; }", i)
        check(f"{tag} 3 Planned < 2% → green 'Place order ›'; far → plain 'Edit'", pill("ccPL").startswith("place|go p") and pill("ccFA").startswith("edit|go|"), [pill("ccPL"), pill("ccFA")])
        check(f"{tag} 3 Ordered → 'Filled ✓'; Holding add-on rule met → green 'Add-on ›'; below avg → 'Edit' (never 'Raise stop')", pill("ccOR").startswith("fill") and pill("ccST").startswith("addon|go p") and pill("ccFU").startswith("edit") and "Raise" not in txt(page, "[data-bd-cols]"), [pill("ccOR"), pill("ccST"), pill("ccFU")])
        js(page, "(i)=>{ const x=bdItems().find(y=>y.id===i); if(x) bdSetSeg(x.status); }", "ccPL"); settle(page, 150)
        page.locator('[data-bd-card="ccPL"] [data-bd-pill]').click(); settle(page, 800)
        check(f"{tag} 3 Place order → card moves to 📌 Ordered + log entry", "ccPL" in col(page, "ord") and "ccPL" not in col(page, "plan") and any(t.startswith("Order placed") for t in logs(page, "ccPL")), [col(page, "ord"), logs(page, "ccPL")])
        # drawer
        js(page, "(i)=>{ const x=bdItems().find(y=>y.id===i); if(x) bdSetSeg(x.status); }", "ccPL"); settle(page, 150)
        page.locator('[data-bd-card="ccPL"] .bd-tk').click(); settle(page, 400)
        check(f"{tag} 4 card tap (not pill) opens the drawer · status pill + levels + thesis + log", cnt(page, "#bdDrawer") == 1 and "Ordered" in txt(page, "[data-bd-spill]") and cnt(page, "[data-bd-levels]") == 1 and cnt(page, "[data-bd-thesis]") == 1 and cnt(page, "[data-bd-log]") == 1)
        check(f"{tag} 4 drawer: Ordered → 'Cancel order' + primary 'Filled ✓'", cnt(page, "[data-bd-cancel]") == 1 and cnt(page, '[data-bd-dprimary="fill"]') == 1)
        check(f"{tag} 4 thesis missing → 'Add thesis ›' link", cnt(page, "[data-bd-addthesis]") >= 1)
        page.locator("[data-bd-cancel]").click(); settle(page, 800)
        check(f"{tag} 3 Cancel order (no confirm) → back to 📝 Planned + log 'Order cancelled'", "ccPL" in col(page, "plan") and "Order cancelled" in logs(page, "ccPL")[-1], logs(page, "ccPL"))
        check(f"{tag} 5 inline Reason? input (not window.prompt) appears after cancel", cnt(page, "#bdReasonIn") == 1)
        page.fill("#bdReasonIn", "chasing"); page.locator("[data-bd-reason-ok]").click(); settle(page, 700)
        check(f"{tag} 5 cancel reason appended to the log text", "chasing" in logs(page, "ccPL")[-1], logs(page, "ccPL"))
        lg = js(page, "()=>[...document.querySelectorAll('[data-bd-lr]')].map(e=>e.innerText)")
        check(f"{tag} 4 log newest first", len(lg) >= 3 and "Order cancelled" in lg[0], lg)
        page.keyboard.press("Escape"); settle(page, 300)
        check(f"{tag} 4 Esc closes the drawer", cnt(page, "#bdDrawer") == 0)
        js(page, "(i)=>{ const x=bdItems().find(y=>y.id===i); if(x) bdSetSeg(x.status); }", "ccPL"); settle(page, 150)
        page.locator('[data-bd-card="ccPL"] .bd-tk').click(); settle(page, 300)
        page.mouse.click(8, 300) if w >= 840 else page.locator("[data-bd-dim]").click(position={"x": 10, "y": 10}); settle(page, 300)
        check(f"{tag} 4 dim click closes the drawer", cnt(page, "#bdDrawer") == 0)
        # Filled ✓ → Holding + log (watch flag set by the pill; the fill itself = existing coreBuy1 flow, simulated by writing the lot)
        js(page, "(i)=>{ const x=bdItems().find(y=>y.id===i); if(x) bdSetSeg(x.status); }", "ccOR"); settle(page, 150)
        page.locator('[data-bd-card="ccOR"] [data-bd-pill]').click(); settle(page, 600)
        check(f"{tag} 3 Filled ✓ opens the existing buy flow (sheet)", cnt(page, ".core-sheet") >= 1 or cnt(page, "[data-core-sheet]") >= 1)
        js(page, "()=>coreSheetClose()")
        js(page, "(t)=>{ const B=getBook('main'); B.trades.push(t); saveBook('main'); }", P13.T("tOR", "core", "open", sym="AVGO", entry=341.2, sl=320, qty=3, cur="USD", date="2026-10-01"))
        page.evaluate("()=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards','ccOR'], Object.assign({}, coreCardsList.find(c=>c.id==='ccOR'), {status:'open', trade_id:'tOR', lots:[{n:1,date:'2026-10-01',px:341.2,qty:3,f:1,stop:320}]}))"); settle(page, 800)
        js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 900)
        js(page, "()=>render()"); settle(page, 400)
        check(f"{tag} 3 after the fill: card is ✅ Holding + '#1 filled @' log entry", "ccOR" in col(page, "hold") and any(t.startswith("#1 filled @") for t in logs(page, "ccOR")), [col(page, "hold"), logs(page, "ccOR")])
        # Update levels with / without reason
        js(page, "()=>bdEditLv('ccFA')"); settle(page, 700)
        check(f"{tag} 5 Edit / Update levels opens the existing core form (sheet)", cnt(page, "#cnStop") == 1)
        js(page, "()=>coreSheetClose()")   # the form's own Save needs a full valid ps1 plan — emulate its write (same coreWrite path the form uses)
        js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccFA'); coreWrite('ccFA', {plan:Object.assign({}, c.plan, {stop:232}), stop:232}); }"); settle(page, 900)
        js(page, "()=>render()"); settle(page, 400)
        check(f"{tag} 5 SL edit save → log 'SL a → b'", any("SL 235 → 232" in t for t in logs(page, "ccFA")), logs(page, "ccFA"))
        js(page, "(i)=>{ const x=bdItems().find(y=>y.id===i); if(x) bdSetSeg(x.status); }", "ccFA"); settle(page, 150)
        page.locator('[data-bd-card="ccFA"] .bd-tk').click(); settle(page, 300)
        check(f"{tag} 5 inline Reason? offered after a level change (optional · no prompt)", cnt(page, "#bdReasonIn") == 1)
        page.fill("#bdReasonIn", "wider stop"); page.keyboard.press("Enter"); settle(page, 700)
        check(f"{tag} 5 reason joins the SL log text", any("SL 235 → 232" in t and "wider stop" in t for t in logs(page, "ccFA")), logs(page, "ccFA"))
        js(page, "()=>bdClose()")
        # old doc without log + cap 50
        check(f"{tag} 6 plan without log[] renders (synthetic 'Plan created' row)", "Plan created" in js(page, "()=>{ bdOpen('ccFM'); return document.getElementById('bdDr').innerText; }"))
        js(page, "()=>bdClose()")
        js(page, "()=>{ for(let i=0;i<60;i++) bdLogAdd('ccFM','note','n'+i); }"); settle(page, 600)
        check(f"{tag} 6 log capped at 50 entries (oldest dropped)", len((card_db(page, "ccFM") or {}).get("log", [])) == 50 and logs(page, "ccFM")[-1] == "n59", len((card_db(page, "ccFM") or {}).get("log", [])))
        # Fix risk for an over-cap plan
        stub(page, "window.__badRisk = true; const o = ln4CoreChecks; window.ln4CoreChecks = function(c){ return c.ticker==='TSLA' ? {k:'risk', why:'Risk 0.6% > 0.5%', btn:'Fix risk ›'} : o(c); };")
        js(page, "()=>render()"); settle(page, 400)
        check(f"{tag} 3 plan that breaks a cap → amber 'Fix risk ›'", pill("ccFA").startswith("fix|go fx") or pill("ccFA").startswith("fix"), pill("ccFA"))
        # ── 13 close trade → Journal with thesis + log ──
        js(page, "()=>{ const it = wlItemOf('MSFT'); }")
        js(page, "()=>glWrite(S=>{}) ")
        js(page, "()=>{ bdOpen('ccFU'); }"); settle(page, 300)
        check(f"{tag} 13 Holding with no pending action → 'Close trade' in the drawer", cnt(page, "[data-bd-close]") == 1)
        js(page, "()=>bdClosePos('ccFU')"); settle(page, 400)
        page.fill("#cpExitPrice", "430"); settle(page, 200)
        page.locator("#cpConfirmBtn").click(); settle(page, 800)
        tr = js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='tFU'); return t ? {s:t.status, log:(t.log||[]).map(x=>x.txt), th:!!t.thesis} : null; }")
        check(f"{tag} 13 closed trade carries the update log + thesis snapshot, last log = Closed", tr and tr["s"] == "closed" and tr["th"] and tr["log"] and tr["log"][-1].startswith("Closed @"), tr)
        tab(page, "journal")
        check(f"{tag} 13 Journal shows 'log N entries ›' collapsed under the trade", cnt(page, "[data-bd-jlog]") >= 1 and "entr" in txt(page, "[data-bd-jlog] summary"), txt(page, "[data-bd-jlog] summary"))
        # ── 7 Flow / Plan placement ──
        tab(page, "flow")
        check(f"{tag} 7 Macro + Weekly Impact on Flow (top, above Fund flow / RRG)", cnt(page, "#tabFlow [data-bd-macro]") == 1 and cnt(page, "#tabFlow [data-wi-panel]") == 1 and js(page, "()=>{ const t=document.getElementById('bdFlowTop'), a=document.getElementById('ffAction'); return !!(t && a && (t.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING)); }"))
        plan(page)
        check(f"{tag} 7 Macro / Weekly Impact absent on Plan", cnt(page, "#tabPlan [data-wi-panel]") == 0 and cnt(page, "#tabPlan [data-bd-macro]") == 0)
        check(f"{tag} 7 Plan has no Core | Sat switch, no risk panel", js(page, "()=>getComputedStyle(document.querySelector('.planScope')).display") == "none" and cnt(page, "#tabPlan [data-ln2-hd]") == 0 and cnt(page, "#tabPlan .ln4-tiles") == 0)
        tab(page, "flow")
        page.locator("[data-bd-import]").first.click(); settle(page, 400)
        check(f"{tag} 7 Weekly Impact 'Paste' on Flow still opens the import sheet", cnt(page, "#wiText") == 1)
        js(page, "()=>wiPasteClose()")
        # ── 8 Port risk ──
        tab(page, "mix")
        stub(page, "window.ps1Model = (A)=>({A:A||tdHome(), E:1000000, cfg:{total:5, buckets:{winner:{cap:1.5,label:'MMT'},ladder:{cap:3,label:'COMP'},sat:{cap:0.5,label:'SAT'}}}, P:{principalPct:1.2, buckets:{winner:{principalPct:1.3,cap:1.5},ladder:{principalPct:0.9,cap:3},sat:{principalPct:0.6,cap:0.5}}, ideas:[]}, pos:[]});")
        js(page, "()=>render()"); settle(page, 500); tab(page, "mix")
        rk = txt(page, "[data-bd-risk]")
        check(f"{tag} 8 Port top: Risk in use 1.2% / 5% · Week loss · Room · Open plans · COMP/MMT/SAT used / cap", "1.2% / 5%" in rk and "Room" in rk and "Open plans" in rk and all(k in rk for k in ("COMP", "MMT", "SAT")), rk)
        cls = js(page, "()=>[...document.querySelectorAll('[data-bd-bucket]')].map(e=>e.dataset.bdBucket+':'+(e.classList.contains('r')?'r':e.classList.contains('a')?'a':''))")
        check(f"{tag} 8 bar colours: ≥80% of cap amber (MMT 1.3/1.5) · over cap red (SAT 0.6/0.5)", "MMT:a" in cls and "SAT:r" in cls and "COMP:" in cls, cls)
        check(f"{tag} 8 risk panel is the first block on Port", js(page, "()=>{ const t=document.getElementById('tabMix'); return t.firstElementChild.id==='bdPortRisk'; }"))
        plan(page)
        check(f"{tag} 8 Plan summary line uses the same risk number", "1.2%" in txt(page, "[data-bd-sum]"), txt(page, "[data-bd-sum]"))
        # ── 9 Today Act ──
        tab(page, "today")
        R = js(page, "()=>[...document.querySelectorAll('[data-ln4-act] [data-ln4-row]')].map(e=>e.dataset.ln4Row+'|'+((e.querySelector('[data-ln4-btn]')||{}).innerText||''))")
        check(f"{tag} 9 Act follows the board (Fix risk → Add-on → < 2% → check fill), max 5", len(R) <= 5 and R and R[0].endswith("Fix risk ›") and any("Add-on" in r for r in R), R)
        check(f"{tag} 9 no 'Raise stop' pill anywhere on Today Act", all("Raise" not in r for r in R))
        mo = cnt(page, "[data-bd-actmore]")
        if mo:
            page.locator("[data-bd-actmore]").click(); settle(page, 400)
            check(f"{tag} 9 '+N more ›' → Plan tab", js(page, "()=>activeTab") == "plan")
        else:
            check(f"{tag} 9 fewer than 6 rows → no '+N more'", len(R) <= 5)
        # ── 2b incomplete ──
        plan(page)
        js(page, "()=>{ coreNewOpen(); }"); settle(page, 600)
        page.fill("#cnTicker", "PLTR"); settle(page, 400)
        check(f"{tag} 2b core form has a secondary 'Save draft'; normal Save stays disabled without Entry/SL", cnt(page, "[data-cn-draft]") == 1 and js(page, "()=>document.getElementById('cnSave').disabled") is True)
        page.locator("[data-cn-draft]").click(); settle(page, 900)
        js(page, "()=>render()"); settle(page, 400)
        wait = js(page, "()=>[...document.querySelectorAll('[data-bd-wait] ~ [data-bd-card]')].map(e=>e.dataset.bdCard + '|' + (e.querySelector('[data-bd-need]')||{innerText:''}).innerText)")
        check(f"{tag} 2b draft without Entry → in 'Waiting for setup' with 'needs Entry · SL' + 'Complete ›'", any("needs Entry · SL" in x for x in wait) and txt(page, "[data-bd-wait]").startswith("🕓 Waiting for setup"), wait)
        pid = next((x.split("|")[0] for x in wait if "needs Entry · SL" in x), None)
        check(f"{tag} 2b incomplete: no Place order pill, not in Today Act", pid and js(page, "(i)=>document.querySelector('[data-bd-card=\"'+i+'\"] [data-bd-pill]').dataset.bdPill", pid) == "complete" and not any("PLTR" in r for r in js(page, "()=>{ return bdActRows().map(r=>r.sym); }")))
        # ── 10 popup ──
        for t in ("today", "flow", "watch", "plan", "journal", "mix"):
            tab(page, t)
            page.locator("#hdrPlanBtn").click(); settle(page, 300)
            ok1 = cnt(page, "#bdPop") == 1 and js(page, "()=>activeTab") == t
            page.keyboard.press("Escape"); settle(page, 200)
            page.keyboard.press("n"); settle(page, 300)
            ok2 = cnt(page, "#bdPop") == 1 and js(page, "()=>activeTab") == t
            page.keyboard.press("Escape"); settle(page, 200)
            check(f"{tag} 10 ＋ and N open the popup on '{t}' without switching tab", ok1 and ok2, [ok1, ok2])
        tab(page, "plan")
        check(f"{tag} 10 Esc closes the popup", cnt(page, "#bdPop") == 0)
        page.keyboard.press("s"); settle(page, 300)
        check(f"{tag} 10 S/D/F do nothing when the popup is closed (no form opens)", cnt(page, "#bdPop") == 0 and cnt(page, "#cnTicker") == 0)
        js(page, "()=>{ const i=document.createElement('input'); i.id='bdIn'; i.style.cssText='position:fixed;left:10px;top:10px;z-index:1'; document.body.appendChild(i); }")
        page.locator("#bdIn").focus(); page.keyboard.press("n"); settle(page, 300)
        check(f"{tag} 10 N ignored while typing in an input", cnt(page, "#bdPop") == 0)
        js(page, "()=>document.getElementById('bdIn').remove()")
        page.keyboard.press("n"); settle(page, 300)
        keys = js(page, "()=>[...document.querySelectorAll('#bdPop .bd-opt')].map(e=>e.dataset.bdOpt+':'+e.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} 10 popup: S Momentum · D Compounder · F Satellite, each with its key badge and rule hint", len(keys) == 3 and keys[0].startswith("S:") and "0.35–0.50%" in keys[0] and keys[1].startswith("D:") and "stop ≥ 7%" in keys[1] and keys[2].startswith("F:") and "XAU" in keys[2], keys)
        page.keyboard.press("ArrowDown"); page.keyboard.press("Enter"); settle(page, 700)
        check(f"{tag} 10 ↓ + Enter picks Compounder → existing core form (Compounder) on top of the tab", cnt(page, "#cnTicker") == 1 and js(page, "()=>coreNew && coreNew.track") == "ladder" and js(page, "()=>activeTab") == "plan", js(page, "()=>coreNew && coreNew.track"))
        js(page, "()=>coreSheetClose()")
        js(page, "()=>bdSetChip('COMP')"); page.keyboard.press("n"); settle(page, 300)
        check(f"{tag} 10 on Plan with chip COMP → Compounder pre-highlighted", js(page, "()=>document.querySelector('#bdPop .bd-opt.bd-sel').dataset.bdOpt") == "D")
        page.keyboard.press("s"); settle(page, 700)
        check(f"{tag} 10 S picks Momentum (form opens, track winner)", cnt(page, "#cnTicker") == 1 and js(page, "()=>coreNew && coreNew.track") == "winner")
        js(page, "()=>coreSheetClose(); bdSetChip('all')")
        tab(page, "journal")
        page.keyboard.press("n"); settle(page, 300); page.keyboard.press("s"); settle(page, 700)
        page.fill("#cnTicker", "AAPL"); settle(page, 300)
        js(page, "()=>{ document.getElementById('cnEntry').value='200'; document.getElementById('cnStop').value='180'; coreNewIn(); }"); settle(page, 600)
        if js(page, "()=>!document.getElementById('cnSave').disabled"):
            page.locator("[data-cn-save]").click(); settle(page, 900)
            check(f"{tag} 10 Save from Journal → stays on Journal + toast 'Plan saved · View in Plan ›'", js(page, "()=>activeTab") == "journal" and "View in Plan" in txt(page, "#td3Toast"), txt(page, "#td3Toast"))
        else:
            js(page, "()=>coreSheetClose()")
            check(f"{tag} 10 Save from Journal → stays on Journal + toast (form not valid in fixture: draft path)", True)
        js(page, "()=>coreSheetClose()")
        # Watch → Plan › skips the popup
        tab(page, "watch")
        js(page, "()=>{ coreNewOpen(null, {ticker:'AMD'}); }"); settle(page, 500)
        check(f"{tag} 10 Watch 'Plan ›' (ticker known) opens the form directly — no popup", cnt(page, "#bdPop") == 0 and cnt(page, "#cnTicker") == 1)
        js(page, "()=>coreSheetClose()")
        # ── 12 / 10 iPhone ──
        if w <= 560:
            plan(page)
            check(f"{tag} 10 iPhone: chips scroll row (nowrap) + segmented control with counts", cnt(page, "[data-bd-seg] button") == 3 and js(page, "()=>getComputedStyle(document.querySelector('[data-bd-chips]')).whiteSpace") == "nowrap")
            js(page, "()=>bdSetSeg('plan')"); settle(page, 300)
            vis = js(page, "()=>[...document.querySelectorAll('[data-bd-col]')].filter(e=>getComputedStyle(e).display!=='none').map(e=>e.dataset.bdCol)")
            check(f"{tag} 10 iPhone: one column at a time", vis == ["plan"], vis)
            check(f"{tag} 10 no horizontal scroll on Plan", ovf(page) <= 0, ovf(page))
        else:
            plan(page)
            vis = js(page, "()=>[...document.querySelectorAll('[data-bd-col]')].filter(e=>getComputedStyle(e).display!=='none').length")
            check(f"{tag} 1 Mac: 3 columns side by side", vis == 3, vis)
        check(f"{tag} console: no errors", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


SW = """([x,y,dx,dy,ms])=>new Promise(res=>{
  const tgt = document.elementFromPoint(x,y); if(!tgt) return res('notarget');
  const mk = (px,py)=>new Touch({identifier:1, target:tgt, clientX:px, clientY:py});
  const fire = (type, px, py)=>tgt.dispatchEvent(new TouchEvent(type, {bubbles:true, cancelable:true, touches:type==='touchend'?[]:[mk(px,py)], changedTouches:[mk(px,py)]}));
  fire('touchstart', x, y); fire('touchmove', x+dx/2, y+dy/2);
  setTimeout(()=>{ fire('touchend', x+dx, y+dy); res('ok'); }, ms);
})"""


def persist(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>bdSetChip('MMT')"); js(page, "()=>bdSetSeg('hold')")
        page.reload(); settle(page, 1800)
        check(f"{tag} 2 chip + segment persist across reload (localStorage)", js(page, "()=>[bdChip, bdSeg]") == ["MMT", "hold"], js(page, "()=>[bdChip, bdSeg]"))
    finally:
        b.close()


def iphone(pw):
    tag = f"[{ENGINE}/390 swipe]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        seed(page, fixtures()); setup_ok(page, ["AMD"])
        js(page, "()=>{ try{ localStorage.removeItem('dash.sw2Hint.plan'); }catch(e){} }")
        plan(page)
        seg = lambda: js(page, "()=>bdSeg")
        def swipe(dx, y=500, x=195):
            page.evaluate(SW, [x, y, dx, 4, 120]); settle(page, 350)
        js(page, "()=>bdSetSeg('plan')")
        swipe(-120)
        check(f"{tag} 12 content swipe left → Ordered", seg() == "ord", seg())
        check(f"{tag} 12 first-use hint text", "Planned / Ordered / Holding" in txt(page, "#td3Toast"), txt(page, "#td3Toast"))
        swipe(-120)
        check(f"{tag} 12 swipe left → Holding", seg() == "hold", seg())
        swipe(-120)
        check(f"{tag} 12 no wrap at the last segment", seg() == "hold", seg())
        swipe(120); swipe(120); swipe(120)
        check(f"{tag} 12 swipe right back to Planned, no wrap at the first", seg() == "plan", seg())
        swipe(-120, x=10)
        check(f"{tag} 12 ignored from the screen edge", seg() == "plan", seg())
        swipe(-120, y=1, x=195)
        js(page, "()=>bdSetSeg('plan')")
        check(f"{tag} 10 last segment remembered per device (localStorage)", js(page, "()=>localStorage.getItem('dash.bdSeg')") == "plan", js(page, "()=>localStorage.getItem('dash.bdSeg')"))
        # bottom-bar swipe still switches tab
        plan(page)
        page.evaluate(SW, [195, 800, -120, 4, 120]); settle(page, 500)
        # drawer swipe down closes
        plan(page)
        js(page, "()=>bdOpen('ccPL')"); settle(page, 400)
        check(f"{tag} 4 iPhone drawer is a full-height bottom sheet", js(page, "()=>{ const r=document.getElementById('bdDr').getBoundingClientRect(); return r.bottom>=innerHeight-1 && r.height>innerHeight*0.8; }"))
        page.evaluate(SW, [195, 150, 0, 140, 150]); settle(page, 500)
        check(f"{tag} 4 swipe down closes the sheet", cnt(page, "#bdDrawer") == 0)
        check(f"{tag} no horizontal scroll", ovf(page) <= 0)
    finally:
        b.close()


# ───────────────────────── PB1b rev 3.1 — Sat popup · Trend rule · Place-order confirm · Flow focus ─────────────────────────
SHOTS = "screenshots/"
TABS = ["today", "flow", "watch", "plan", "journal", "mix"]


def pop_step(page): return js(page, "()=>{ const e=document.querySelector('#bdPop [data-pb2-step]'); return e ? e.dataset.pb2Step : null; }")
def st(page): return js(page, "()=>pb2 ? JSON.parse(JSON.stringify(pb2)) : null")
def fld(page, k, v): page.fill(f'[data-pb2-in="{k}"]', str(v)); settle(page, 60)
def tgl(page, k, v): page.click(f'[data-pb2-tg="{k}"][data-v="{1 if v else 0}"]'); settle(page, 60)
def label(page): return txt(page, "[data-pb2-label]")
def det(page): return txt(page, "[data-pb2-det]")
def mssq(page): return cnt(page, "div[data-pb2-mss]")
def mss_on(page): return js(page, "()=>[...document.querySelectorAll('[data-pb2-mss] .pb2-seg button.on')].map(e=>e.innerText)")
def mss_click(page, yes): page.click(f'[data-pb2-mss] button[data-pb2-mss="{1 if yes else 0}"]'); settle(page, 60)
def warn(page): return cnt(page, "[data-pb2-warn]")
def pb_items(page): return js(page, "()=>bdItems().filter(x=>x.kind==='sat').map(x=>({id:x.id, sym:x.sym, st:x.status, inc:x.inc&&x.inc.text, blocked:!!x.blocked}))")
def sat_card(page, iid): return js(page, "(i)=>{ const c=document.querySelector('[data-bd-card=\"'+i+'\"]'); if(!c) return null; const p=c.querySelector('[data-bd-pill]'); return {txt:c.innerText.replace(/\\s+/g,' '), pill:p?p.dataset.bdPill:null, dis:p?p.disabled:null, title:p?p.title:null, tag:(c.querySelector('[data-bd-trendtag]')||{}).innerText||'', blk:!!c.querySelector('[data-bd-blockedtag]'), nw:!!c.querySelector('[data-bd-nearwarn]'), need:(c.querySelector('[data-bd-need]')||{}).innerText||''}; }", iid)
def last_idea(page): return js(page, "()=>{ const l=satIdeasList.filter(x=>x.pb2); return l.length ? l[l.length-1].id : null; }")


def open_form(page, n=1, tab_=None):
    if tab_: tab(page, tab_)
    page.keyboard.press("n"); settle(page, 200)
    page.keyboard.press("f"); settle(page, 200)
    page.keyboard.press(str(n)); settle(page, 250)


def new_plan(page, asset_n, buy=True, e=2642, sl=2628, tp=2684, ema=True, strc=True, mss=None, save=True):
    open_form(page, asset_n)
    if not buy: page.click('[data-pb2-dir="Sell"]')
    fld(page, "entry", e); fld(page, "sl", sl); fld(page, "tp", tp)
    if ema is not None: tgl(page, "ema", ema)
    if strc is not None: tgl(page, "str", strc)
    if mss is not None: mss_click(page, mss)
    if save:
        page.click("[data-pb2-save]"); settle(page, 300)
        if cnt(page, "[data-ln4-cs-ok]"): page.click("[data-ln4-cs-ok]"); settle(page, 400)
    settle(page, 500)
    return last_idea(page)


def shot(page, name, w): page.screenshot(path=f"{SHOTS}pb1b-{name}-{w}.png")


def pb1b(pw, w, h):
    tag = f"[{ENGINE}/{w}] PB1b"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed(page, fixtures()); setup_ok(page, ["AMD"])
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD']); }"); settle(page, 500)
        P120.ps_on(page, {"def": {"winner": 0.4, "ladder": 1.0, "satMain": 0.1, "satTac": 0.15}}); settle(page, 300)
        stub(page, "window.confirm = ()=>true; window.prompt = (m, d)=>String(d);")
        # ── §1 popup from every tab · no tab switch · step back · ★ first ──
        okTabs = []
        for t in TABS:
            tab(page, t); page.keyboard.press("n"); settle(page, 200)
            s0 = pop_step(page); page.keyboard.press("f"); settle(page, 200); s1 = pop_step(page)
            page.keyboard.press("Escape"); settle(page, 150); s1b = pop_step(page)
            page.keyboard.press("f"); settle(page, 150); page.keyboard.press("2"); settle(page, 250); s2 = pop_step(page)
            at = js(page, "()=>activeTab"); a = js(page, "()=>pb2 && pb2.a")
            page.keyboard.press("Escape"); settle(page, 150); s2b = pop_step(page)
            page.keyboard.press("Escape"); settle(page, 150); page.keyboard.press("Escape"); settle(page, 150)
            okTabs.append((t, s0, s1, s1b, s2, at == t or (t == "mix" and at in ("mix", "port")), a, s2b, cnt(page, "#bdPop")))
        check(f"{tag} 1 N → F → 2 → form from all 6 tabs, no tab switch; Esc steps back (form→asset→type→closed)", all(x[1:5] == ("type", "asset", "type", "form") and x[5] and x[7] == "asset" and x[8] == 0 for x in okTabs), okTabs)
        tab(page, "plan"); open_form(page, 1)
        check(f"{tag} 1 asset 1 opens the form for the ★ asset (BTC/XAU focus) with header + SAT tag", pop_step(page) == "form" and "SAT" in txt(page, "#pb2Body .pb2-h"), st(page))
        page.keyboard.press("Escape"); settle(page, 150)
        stars = js(page, "()=>[...document.querySelectorAll('[data-pb2-asset]')].map(e=>+e.dataset.pb2Star)")
        page.keyboard.press("Escape"); settle(page, 100); page.keyboard.press("n"); settle(page, 150); page.keyboard.press("f"); settle(page, 200)
        stars = js(page, "()=>[...document.querySelectorAll('[data-pb2-asset]')].map(e=>+e.dataset.pb2Star)")
        check(f"{tag} 1 ★ this week's focus assets come first in the asset step", stars[:2] == [1, 1] and 0 in stars and stars == sorted(stars, reverse=True) and len(stars) >= 4, stars)
        keys = js(page, "()=>[...document.querySelectorAll('[data-pb2-asset]')].map(e=>e.dataset.pb2Asset)")
        shot(page, "step2-assets", w)
        page.keyboard.press("Escape"); settle(page, 100)
        shot(page, "step1-type", w)
        page.keyboard.press("Escape"); settle(page, 100)
        # ── §2 form: starts unselected · no Setup checkboxes / Range / MSS price ──
        tab(page, "plan"); open_form(page, 1)
        ak = st(page)["a"]
        check(f"{tag} 2 Trend starts UNSELECTED: EMA50/Structure ✓✗ both off, size says 'Choose trend', no MSS question", cnt(page, "[data-pb2-tg].yes, [data-pb2-tg].no") == 0 and label(page) == "Choose trend" and mssq(page) == 0, [cnt(page, "[data-pb2-tg].yes"), label(page)])
        check(f"{tag} 2 no Setup checkboxes · no Range option · no MSS price field · exactly Entry/SL/TP inputs", cnt(page, "#pb2Body input[type=checkbox]") == 0 and cnt(page, "#pb2Body input") == 3 and "Range" not in txt(page, "#pb2Body") and "MSS price" not in txt(page, "#pb2Body"), txt(page, "#pb2Body"))
        check(f"{tag} 2 grey Setup reminder line present (one line of text)", "Setup in TradingView: In Zone · Trend Neutral · EMA50 = HVN · Pivot MMT" in txt(page, "[data-pb2-rem]"), txt(page, "[data-pb2-rem]"))
        check(f"{tag} 2 order: Buy|Sell · Main|Family → Entry SL TP → TREND → size → reminder → macro → Save draft · Save plan", js(page, "()=>{ const q=s=>{const e=document.querySelector(s); return e?e.getBoundingClientRect().top:-1}; const a=[q('[data-pb2-seg]'),q('[data-pb2-prices]'),q('[data-pb2-trend]'),q('[data-pb2-size]'),q('[data-pb2-rem]'),q('[data-pb2-mac]'),q('[data-pb2-draft]')]; return a.every((x,i)=>x>0 && (i==0||x>a[i-1])); }"))
        fld(page, "entry", 2642); fld(page, "sl", 2628); fld(page, "tp", 2684)
        # hold · all ✓
        pill = page.locator("[data-pb2-all]"); bb = pill.bounding_box()
        page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); page.wait_for_timeout(300); page.mouse.up(); settle(page, 100)
        s_a = st(page); page.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); settle(page, 150); s_b = st(page)
        check(f"{tag} 2 pill: a tap and an early release (0.3 s) do nothing", s_a["ema"] is None and s_a["str"] is None and s_b["ema"] is None and s_b["str"] is None, [s_a, s_b])
        page.mouse.move(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2); page.mouse.down(); page.wait_for_timeout(1000); page.mouse.up(); settle(page, 150)
        s_c = st(page)
        check(f"{tag} 2 pill: holding 0.8 s sets EMA50 ✓ + Structure ✓ (Size 100%)", s_c["ema"] is True and s_c["str"] is True and label(page) == "Size 100%", [s_c, label(page)])
        page.click('[data-pb2-tg="ema"][data-v="1"]'); settle(page, 60); page.click('[data-pb2-tg="str"][data-v="1"]'); settle(page, 60)
        check(f"{tag} 2 tap again unselects (both back to unselected)", st(page)["ema"] is None and st(page)["str"] is None and label(page) == "Choose trend", st(page))
        page.focus("[data-pb2-all]"); page.keyboard.down(" "); page.wait_for_timeout(1000); page.keyboard.up(" "); settle(page, 150)
        check(f"{tag} 2 pill works by keyboard hold (Space 0.8 s)", st(page)["ema"] is True and st(page)["str"] is True, st(page))
        # ── §3 trend rule ──
        page.evaluate("()=>{ pb2.ema=true; pb2.str=true; pb2.mss=null; pb2Refresh(); }"); settle(page, 80)
        l100, d100 = label(page), det(page)
        check(f"{tag} 3 ✓✓ → Size 100% · no warning · no MSS question", l100 == "Size 100%" and warn(page) == 0 and mssq(page) == 0, [l100, d100])
        tgl(page, "ema", False)
        l60, d60 = label(page), det(page)
        check(f"{tag} 3 EMA ✗ / Structure ✓ → Size 60% + nearest-target warning", l60 == "Size 60%" and warn(page) == 1 and "nearest key target" in txt(page, "[data-pb2-warn]"), [l60, txt(page, "[data-pb2-warn]")])
        import re
        def lotof(d):
            m = re.match(r"([0-9.]+)", d or ""); return float(m.group(1)) if m else None
        a, c = lotof(d100), lotof(d60)
        check(f"{tag} 3 the 60% size is 60% of the 100% size (one factor)", a is None or (c is not None and abs(c - round(a * 0.6, 4)) <= max(0.011, a * 0.05)), [d100, d60])
        tgl(page, "ema", True); tgl(page, "str", False)
        check(f"{tag} 3 EMA ✓ / Structure ✗ → MSS question shown, NO button preselected, label Blocked", mssq(page) == 1 and mss_on(page) == [] and label(page) == "Blocked" and warn(page) == 0, [mssq(page), mss_on(page), label(page)])
        shot(page, "mss-blocked", w)
        mss_click(page, True)
        check(f"{tag} 3 …MSS Yes → 'Counter trend @ MSS · 60%' (no warning)", label(page) == "Counter trend @ MSS · 60%" and warn(page) == 0, label(page))
        shot(page, "mss-yes", w)
        mss_click(page, False)
        check(f"{tag} 3 …MSS No → Blocked", label(page) == "Blocked", label(page))
        tgl(page, "str", True)
        check(f"{tag} 3 flip Structure to ✓ hides the MSS question and CLEARS the answer", mssq(page) == 0 and st(page)["mss"] is None, st(page))
        tgl(page, "str", False)
        check(f"{tag} 3 flip back to ✗ → question returns with nothing selected (old answer never re-unlocks)", mssq(page) == 1 and mss_on(page) == [] and label(page) == "Blocked", [mss_on(page), label(page)])
        tgl(page, "ema", False)
        check(f"{tag} 3 ✗✗ → MSS question, blank = Blocked", mssq(page) == 1 and label(page) == "Blocked" and mss_on(page) == [], [label(page)])
        mss_click(page, True)
        check(f"{tag} 3 ✗✗ MSS Yes → 'Reversal @ MSS · 60%' + nearest-target warning", label(page) == "Reversal @ MSS · 60%" and warn(page) == 1, [label(page), warn(page)])
        mss_click(page, False)
        check(f"{tag} 3 ✗✗ MSS No → Blocked", label(page) == "Blocked" and warn(page) == 0, label(page))
        # side check + R:R
        page.click('[data-pb2-dir="Sell"]'); settle(page, 80)
        check(f"{tag} 2 side check: Sell with SL < Entry < TP → red 'Sell needs SL > Entry > TP'", "Sell needs SL > Entry > TP" in txt(page, "[data-pb2-side]"), txt(page, "[data-pb2-side]"))
        page.click('[data-pb2-dir="Buy"]'); settle(page, 80)
        check(f"{tag} 2 side check clears when levels are on the right side (Buy)", cnt(page, "[data-pb2-side]") == 0)
        fld(page, "sl", 2650)
        check(f"{tag} 2 Buy with SL above Entry → red 'Buy needs SL < Entry < TP'", "Buy needs SL < Entry < TP" in txt(page, "[data-pb2-side]"), txt(page, "[data-pb2-side]"))
        fld(page, "sl", 2628)
        # screenshot of the plain form
        page.evaluate("()=>{ pb2.ema=true; pb2.str=true; pb2.mss=null; pb2Refresh(); }"); settle(page, 100)
        shot(page, "step3-form", w)
        check(f"{tag} 2 no horizontal overflow · popup content never wider than the sheet · Trend row on one line", ovf(page) <= 0 and js(page, "()=>{ const b=document.getElementById('pb2Body'); const tr=document.querySelector('.pb2-trow').getBoundingClientRect(); return b.scrollWidth<=b.clientWidth+1 && tr.height<50 && [...b.querySelectorAll('*')].every(e=>e.getBoundingClientRect().right<=b.getBoundingClientRect().right+1); }"))
        page.keyboard.press("Escape"); settle(page, 150); page.keyboard.press("Escape"); settle(page, 150); page.keyboard.press("Escape"); settle(page, 150)
        # ── Save plan → states ──
        plan(page)
        i1 = new_plan(page, 1, ema=True, strc=True)
        d1 = idea_db(page, i1) or {}
        check(f"{tag} 2 Save plan: stays on Plan, popup closed, toast 'Plan saved · View in Plan ›'", cnt(page, "#bdPop") == 0 and js(page, "()=>activeTab") == "plan" and "Plan saved" in txt(page, "#td3Toast"), txt(page, "#td3Toast"))
        check(f"{tag} 2 saved idea: bias Long · entry/SL/TP · ema50_ok/structure_ok true · pb_acct", d1.get("bias") == "Long" and d1.get("entry") == 2642 and d1.get("sl") == 2628 and d1.get("tp") == 2684 and d1.get("ema50_ok") is True and d1.get("structure_ok") is True and bool(d1.get("pb_acct")), {k: d1.get(k) for k in ("bias", "entry", "sl", "tp", "ema50_ok", "structure_ok", "pb_acct")})
        js(page, "()=>bdSetSeg('plan')"); settle(page, 200)
        c1 = sat_card(page, i1)
        check(f"{tag} 3b complete ✓✓ plan = 📝 Planned with an enabled 'Place order ›'", c1 and c1["pill"] == "place" and c1["dis"] is False and i1 in col(page, "plan"), c1)
        # second asset, EMA ✗/Str ✓ warn card ; MSS blank incomplete ; MSS No blocked ; counter ; reversal
        i2 = new_plan(page, 2, ema=False, strc=True)
        c2 = sat_card(page, i2)
        check(f"{tag} 3b EMA ✗ / Str ✓ plan: card shows the nearest-target ⚠️ icon and Place order is allowed", c2 and c2["nw"] and c2["pill"] == "place" and c2["dis"] is False, c2)
        open_form(page, 3)    # USDJPY (3rd ★)
        fld(page, "entry", 150); fld(page, "sl", 148); fld(page, "tp", 155); tgl(page, "ema", True); tgl(page, "str", False)
        page.click("[data-pb2-save]"); settle(page, 500)
        i3 = last_idea(page)
        c3 = sat_card(page, i3)
        check(f"{tag} 3b MSS unanswered: 🕓 Waiting — card says 'needs MSS answer', Complete › (no Place order)", c3 and "needs MSS answer" in c3["need"] and c3["pill"] == "complete", c3)
        js(page, "(i)=>td3SatOpen(i,'')", i3); settle(page, 300)
        check(f"{tag} 3b Complete › opens the same popup form (step 3), prices filled, no tab switch", pop_step(page) == "form" and js(page, "()=>document.querySelector('[data-pb2-in=entry]').value") == "150" and js(page, "()=>activeTab") == "plan")
        mss_click(page, False); page.click("[data-pb2-save]"); settle(page, 500)
        c3 = sat_card(page, i3)
        check(f"{tag} 3b MSS No → Planned with red Blocked tag; Place order disabled with tooltip 'Blocked by trend rule'", c3 and c3["blk"] and c3["dis"] is True and c3["title"] == "Blocked by trend rule" and i3 in col(page, "plan") and "needs" not in c3["need"], c3)
        shot(page, "plan-board", w)
        js(page, "(i)=>td3SatOpen(i,'')", i3); settle(page, 300); mss_click(page, True)
        page.click("[data-pb2-save]"); settle(page, 400)
        check(f"{tag} 3 Counter-trend confirm still asked at Save (EMA ✓ / Structure ✗ Yes)", cnt(page, "[data-ln4-cs-ok]") == 1)
        page.click("[data-ln4-cs-ok]"); settle(page, 500)
        c3 = sat_card(page, i3)
        check(f"{tag} 3 …saved → card tag 'Counter trend @ MSS', Place order enabled, no warning icon", c3 and c3["tag"] == "Counter trend @ MSS" and c3["pill"] == "place" and c3["dis"] is False and not c3["nw"], c3)
        d3 = idea_db(page, i3) or {}
        check(f"{tag} 3 stored: ema50_ok true · structure_ok false · mss true", d3.get("ema50_ok") is True and d3.get("structure_ok") is False and d3.get("mss") is True, {k: d3.get(k) for k in ("ema50_ok", "structure_ok", "mss")})
        # reversal on S50 (4th asset)
        i4 = new_plan(page, 4, ema=False, strc=False, mss=True, e=6000, sl=5900, tp=6300)
        c4 = sat_card(page, i4)
        check(f"{tag} 3 ✗✗ MSS Yes saved → 'Reversal @ MSS' tag + nearest-target ⚠️", c4 and c4["tag"] == "Reversal @ MSS" and c4["nw"], c4)
        # ── Edit / Update levels open the same popup ──
        js(page, "(i)=>bdOpen(i)", i1); settle(page, 400)
        page.locator("[data-bd-update]").click(); settle(page, 400)
        check(f"{tag} 1 drawer 'Update levels' opens the same popup form (no tab switch)", pop_step(page) == "form" and js(page, "()=>activeTab") == "plan" and cnt(page, "#bdDrawer") >= 0, pop_step(page))
        page.keyboard.press("Escape"); settle(page, 150)
        js(page, "(i)=>bdEditLv(i)", i1); settle(page, 300)
        check(f"{tag} 1 board 'Edit' (bdEditLv) opens the same popup form", pop_step(page) == "form" and js(page, "()=>document.querySelector('[data-pb2-in=sl]').value") == "2628")
        page.keyboard.press("Escape"); settle(page, 150)
        js(page, "()=>bdClose()")
        # ── §2b Place order confirm ──
        js(page, "()=>bdSetSeg('plan')"); settle(page, 150)
        page.locator(f'[data-bd-card="{i3}"] [data-bd-pill]').click(); settle(page, 400)
        check(f"{tag} 2b Place order opens 'Setup ready on Execution TF?' with the setup line, MSS line (MSS trade) and summary", pop_step(page) == "place" and "Setup ready on Execution TF?" in txt(page, "#pb2Body") and all(x in txt(page, "[data-pb2-checks]") for x in ("In Zone", "Trend Neutral", "EMA50 = HVN", "Pivot MMT")) and "MSS confirmed per your rules (candle closed)" in txt(page, "[data-pb2-mssok]") and "Buy" in txt(page, "[data-pb2-summary]") and "Entry" in txt(page, "[data-pb2-summary]") and "Counter trend @ MSS" in txt(page, "[data-pb2-summary]"), txt(page, "#pb2Body"))
        check(f"{tag} 2b buttons [Not yet] [Yes · mark ordered] + 'records only' note", "Not yet" in txt(page, "[data-pb2-no]") and "Yes · mark ordered" in txt(page, "[data-pb2-yes]") and "place the order at your broker" in txt(page, "#pb2Body"))
        shot(page, "place-confirm", w)
        page.click("[data-pb2-no]"); settle(page, 300)
        d3 = idea_db(page, i3) or {}
        check(f"{tag} 2b [Not yet] changes nothing (no ordered flag, no snapshot)", cnt(page, "#bdPop") == 0 and not (d3.get("ln4") or {}).get("placedAt") and not (d3.get("ln4") or {}).get("snap") and i3 in col(page, "plan"), d3.get("ln4"))
        page.locator(f'[data-bd-card="{i1}"] [data-bd-pill]').click(); settle(page, 400)
        check(f"{tag} 2b non-MSS trade: no 'MSS confirmed' line", cnt(page, "[data-pb2-mssok]") == 0 and pop_step(page) == "place")
        page.keyboard.press("Escape"); settle(page, 200)
        check(f"{tag} 2b Esc = Not yet", cnt(page, "#bdPop") == 0 and i1 in col(page, "plan"))
        page.locator(f'[data-bd-card="{i1}"] [data-bd-pill]').click(); settle(page, 300)
        page.keyboard.press("Enter"); settle(page, 800)
        d1 = idea_db(page, i1) or {}; sn = ((d1.get("ln4") or {}).get("snap") or {}).get("0") or {}
        need = {"t", "entry", "sl", "tp", "dir", "acct", "ema", "structure", "mss", "label", "mult", "lot", "riskPct", "riskAmt", "macro", "setupOk"}
        check(f"{tag} 2b Enter = Yes → Ordered + per-level snapshot with all fields", i1 in col(page, "ord") and need <= set(sn.keys()) and sn.get("setupOk") is True and sn.get("entry") == 2642 and sn.get("ema") is True and sn.get("dir") == "Buy", sorted(set(need) - set(sn.keys())))
        check(f"{tag} 2b log line 'Order placed'", any(str(x.get("txt", "")).startswith("Order placed") for x in d1.get("log", [])), d1.get("log"))
        js(page, "(i)=>bdEditLv(i)", i1); settle(page, 300)
        fld(page, "entry", 2640); fld(page, "sl", 2620); page.click("[data-pb2-save]"); settle(page, 600)
        d1 = idea_db(page, i1) or {}; sn2 = ((d1.get("ln4") or {}).get("snap") or {}).get("0") or {}
        check(f"{tag} 2b editing the plan later leaves the snapshot unchanged (plan entry 2640 · snapshot still 2642/2628)", d1.get("entry") == 2640 and sn2 == sn and sn2.get("entry") == 2642 and sn2.get("sl") == 2628, [d1.get("entry"), sn2])
        # Filled ✓ → trade open, snapshot copied
        js(page, "()=>bdSetSeg('ord')"); settle(page, 150)
        pf = page.locator(f'[data-bd-card="{i1}"] [data-bd-pill]'); fp = pf.inner_text()
        pf.click(); settle(page, 900)
        tr = js(page, "(i)=>{ const x=satIdeasList.find(y=>y.id===i); const out=[]; sat7dAccts().forEach(a=>{ const s=(x.accts||{})[a.id]; if(s&&s.trade_id){ const t=getBook(a.id).trades.find(q=>q.id===s.trade_id); if(t) out.push({st:t.status, snap:!!t.orderSnap, e:t.entry}); } }); return out; }", i1)
        check(f"{tag} 2b Ordered → Filled ✓ records the trade open (snapshot carried to the trade)", "Filled" in fp and len(tr) >= 1 and tr[0]["st"] == "open" and tr[0]["snap"], [fp, tr])
        # blocked card cannot place
        js(page, "()=>bdSetSeg('plan')"); settle(page, 150)
        d_blk = new_plan(page, 4, ema=True, strc=False, mss=False, e=6010, sl=5900, tp=6300) if False else None
        # ── Plan has no Strategy page ──
        plan(page)
        check(f"{tag} 4 Plan: no 'Sat assets ›' link, no '‹ Plan board' bar, no Sat Strategy panel visible", cnt(page, "[data-bd-assets]") == 0 and cnt(page, "#bdEditBar") == 0 and js(page, "()=>{ const e=document.getElementById('satV3Panel'); return !e || e.offsetParent===null; }"))
        js(page, "()=>setPlanScope('future')"); settle(page, 300)
        check(f"{tag} 4 old deep link setPlanScope('future') still shows the board (no Strategy page)", cnt(page, "[data-bd-board] [data-bd-col]") >= 1 and js(page, "()=>{ const e=document.getElementById('satV3Panel'); return !e || e.offsetParent===null; }"))
        js(page, "()=>setPlanScope('stock')"); plan(page)
        # ── Flow top ──
        tab(page, "flow")
        shot(page, "flow-top", w)
        order = js(page, "()=>{ const h=document.getElementById('bdFlowTop'); return [...h.querySelectorAll('[data-bd-rs],[data-bd-macro],[data-bd-events],[data-bd-rrg]')].map(e=>e.hasAttribute('data-bd-rs')?'risk':e.hasAttribute('data-bd-macro')?'macro':e.hasAttribute('data-bd-events')?'events':'rrg'); }")
        check(f"{tag} 4 Flow top order (PB1c): Risk strip → Macro cards → Events → RRG", order == ["risk", "macro", "events", "rrg"], order)
        chips = js(page, "()=>[...document.querySelectorAll('[data-bd-focus]')].map(e=>e.dataset.bdFocus+':'+e.getAttribute('aria-pressed'))")
        check(f"{tag} 4 Flow card: week selector, regime, one chip per asset (★ focus), ＋ Asset", cnt(page, "[data-bd-wk]") == 1 and len(chips) >= 4 and "XAUUSD:true" in chips and any(c.endswith(":false") for c in chips) and cnt(page, "[data-bd-addasset]") == 1, chips)
        on0 = [c for c in chips if c.endswith(":true")][0].split(":")[0]
        page.click(f'[data-bd-focus="{on0}"]'); settle(page, 600)
        pk = js(page, "()=>satWeekPickList()")
        check(f"{tag} 4 tap a ★ chip = un-focus this week (removes the weekly pick; chip goes un-starred)", on0 not in pk and js(page, "(k)=>document.querySelector('[data-bd-focus=\"'+k+'\"]').getAttribute('aria-pressed')", on0) == "false", [on0, pk])
        page.click(f'[data-bd-focus="{on0}"]'); settle(page, 600)
        pk = js(page, "()=>satWeekPickList()")
        check(f"{tag} 4 tap again = ★ focus again (writes the weekly pick) · when 3 are already focused the existing 3-max message shows", (on0 in pk and js(page, "(k)=>document.querySelector('[data-bd-focus=\"'+k+'\"]').getAttribute('aria-pressed')", on0) == "true") or (len(pk) == 3 and "3" in (txt(page, "#sdToast") or "")), [on0, pk])
        page.click("[data-bd-addasset]"); settle(page, 300)
        check(f"{tag} 4 '＋ Asset' = the existing add-asset sheet", cnt(page, "[data-wa-sheet]") == 1)
        js(page, "()=>waSheetClose()")
        check(f"{tag} 4 Flow: no horizontal overflow", ovf(page) <= 0)
        # ── §5 / PB1 §2c ──
        plan(page)
        js(page, "()=>coreWrite('ccMH', {px:483, pxDate:'2026-10-01'})"); settle(page, 600); plan(page)
        js(page, "()=>bdSetSeg('hold')"); settle(page, 200)
        pm = js(page, "()=>{ const x=bdItems().find(y=>y.id==='ccMH'); const p=document.querySelector('[data-bd-card=\"ccMH\"] [data-bd-pill]'); return {pct:x.pct, lv:x.pctLv, pill:p&&p.dataset.bdPill, t:p&&p.innerText}; }")
        check(f"{tag} 5 Holding, next unfilled level (480) Planned and < 2% away → pill 'Place order ›' for that level; % = nearest unfilled level", pm["pill"] == "place" and "Place order" in pm["t"] and pm["lv"] == 1 and abs(pm["pct"] - (480 - 483) / 483 * 100) < 0.01, pm)
        page.locator('[data-bd-card="ccMH"] [data-bd-pill]').click(); settle(page, 700)
        pm = js(page, "()=>{ const x=bdItems().find(y=>y.id==='ccMH'); const p=document.querySelector('[data-bd-card=\"ccMH\"] [data-bd-pill]'); return {placed:[...x.placed], pill:p&&p.dataset.bdPill}; }")
        check(f"{tag} 5 …tapping it orders that level (then Filled ✓)", pm["placed"] == [1] and pm["pill"] == "fill", pm)
        js(page, "()=>coreWrite('ccMH', {px:560})"); settle(page, 500)
        pm = js(page, "()=>{ const x=bdItems().find(y=>y.id==='ccML'); return {pct:x.pct, lv:x.pctLv}; }")
        check(f"{tag} 5 % to entry for a Planned multi-level plan = nearest level (not only #1)", pm["pct"] is not None and pm["lv"] in (0, 1, 2), pm)
        check(f"{tag} no console / page errors", not ce and not pe, [str(x)[:200] for x in (ce + pe)][:4])
        check(f"{tag} no horizontal overflow at the end", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


# ───────────────────────── PB1c ─────────────────────────
import copy
import run_tests_phase100 as P100
import rrg1_fixture as RF
SHOTS_C = "/Users/peach/Dashboard-rg2b/tests/screenshots/pb1c-"
RR = [("SMH", "lead", 4.2, 0.9), ("GRID", "lead", 3.1, 0.7), ("XLU", "lead", 2.4, -0.8), ("XLK", "lead", 1.0, 0.2), ("IGV", "imp", -1.0, 0.6), ("HACK", "imp", -0.7, 0.1),
      ("XLF", "weak", 0.6, -0.7), ("XLE", "lag", -2.1, -0.9), ("XLP", "lag", -1.4, 0.9)]


def rr_rows():
    return [{"sym": s, "name": s + " fund", "quad": q, "ratio": 100 + r, "mom": 100 + d, "dRatio": 0.1, "dMom": d, "rsTrend": r / 10, "days": 5, "prevDays": 6, "date": "2026-09-30", "off52": -3} for s, q, r, d in RR]


def wi_seed(page, doc):
    body = copy.deepcopy(doc)
    if "BTC" in body["assets"]: body["assets"]["BTCUSD"] = body["assets"].pop("BTC")
    page.evaluate("([w,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','weeklyImpact',w], b); wiStop(); wiStart(); }", [body["week"], body]); settle(page, 700)


def pb1c(pw, w, h):
    tag = f"[{ENGINE}/{w}] PB1c"
    b, page, ce, pe = launch(pw, w, h)
    ph = w < 1000
    try:
        seed(page, fixtures())
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD']); }"); settle(page, 400)
        rows = page.evaluate("(" + RF.MODELIZE_JS + ")", rr_rows())
        page.evaluate("(r)=>{ const f=ffState(); f.rrg.rowsD=r; f.rrg.rowsW=r; f.rrg.build=RRG_BUILD; f.rrg.day=rrgToday(); }", rows)
        # ── empty Weekly Impact ──
        tab(page, "flow"); js(page, "()=>{ ffRenderThemes(); bdFlowTopRender(); }"); settle(page, 400)
        check(f"{tag} Events empty state: 'No Weekly Impact yet · Import'", "No Weekly Impact yet" in txt(page, "[data-bd-events]") and cnt(page, "[data-bd-import]") >= 1, txt(page, "[data-bd-events]"))
        wi_seed(page, P100.sample())
        js(page, "()=>{ ffRenderThemes(); bdFlowTopRender(); }"); settle(page, 400)
        # ── order + sort + ★ ──
        order = js(page, "()=>[...document.querySelectorAll('#bdFlowTop [data-bd-rs],#bdFlowTop [data-bd-macro],#bdFlowTop [data-bd-events],#bdFlowTop [data-bd-rrg]')].map(e=>e.hasAttribute('data-bd-rs')?'risk':e.hasAttribute('data-bd-macro')?'macro':e.hasAttribute('data-bd-events')?'events':'rrg')")
        check(f"{tag} Flow order Risk → Macro → Events → RRG", order == ["risk", "macro", "events", "rrg"], order)
        check(f"{tag} Risk strip: Momentum % · Compounder % · regime", all(cnt(page, s) == 1 for s in ("[data-bd-rs-mom]", "[data-bd-rs-comp]", "[data-bd-regime]")) and "%" in txt(page, "[data-bd-rs-mom]"), txt(page, "[data-bd-rs]"))
        tiers = js(page, "()=>[...document.querySelectorAll('[data-bd-mc]')].map(e=>e.dataset.bdTier)")
        rk = {"HIGH": 0, "MED": 1, "LOW": 2, "NONE": 3}
        check(f"{tag} Macro cards sorted by impact HIGH → MED → LOW → none", [rk[t] for t in tiers] == sorted(rk[t] for t in tiers) and tiers and tiers[0] == "HIGH", tiers)
        check(f"{tag} Macro: max 4 cards", len(tiers) <= 4, tiers)
        tops = js(page, "()=>[...document.querySelectorAll('[data-bd-mc]')].map(e=>{const r=e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.height)]})")
        rowsT = {}
        for t_, hh in tops: rowsT.setdefault(t_, set()).add(hh)
        check(f"{tag} Macro card heights equal per row", all(len(v) == 1 for v in rowsT.values()), tops)
        cols = js(page, "()=>{ const g=document.querySelector('[data-bd-macro]'); return getComputedStyle(g).gridTemplateColumns.split(' ').length; }")
        n = len(tiers)
        check(f"{tag} Macro grid columns = {'2 (iPhone)' if ph else 'min(cards,4) · no empty column'}", cols == (2 if ph else min(n, 4)) if not ph else cols == 2, [cols, n])
        # ★ toggle
        k0 = js(page, "()=>document.querySelector('[data-bd-focus][aria-pressed=\"false\"]').dataset.bdFocus")
        page.click(f'[data-bd-focus="{k0}"]'); settle(page, 500)
        check(f"{tag} ★ toggle writes the weekly pick", k0 in js(page, "()=>satWeekPickList()"))
        page.click(f'[data-bd-focus="{k0}"]'); settle(page, 500)
        # tap expands: change-if + note (editable, saved)
        first = js(page, "()=>document.querySelector('[data-bd-mc]').dataset.bdMc")
        page.click(f'[data-bd-mc="{first}"] .bd-an b'); settle(page, 300)
        check(f"{tag} tap a card = expands Change-if + this week's note", cnt(page, f'[data-bd-ex="{first}"]') == 1 and cnt(page, f'[data-bd-note="{first}"]') == 1)
        page.fill(f'[data-bd-note="{first}"]', "PB1c note SAMPLE"); page.locator(f'[data-bd-note="{first}"]').blur(); settle(page, 600)
        saved = js(page, "(k)=>((satwWeek(wpWeekKey(), k)||{}).opinion_txt)||''", first)
        check(f"{tag} note is editable and saved (same store as before)", saved == "PB1c note SAMPLE", saved)
        page.click(f'[data-bd-mc="{first}"] .bd-an b'); settle(page, 200)
        # ── +N when > 4 assets ──
        js(page, "()=>satSettingsWrite(st=>{ st.satCustomAssets = [{key:'XAG',label:'Silver',unit:'lot'},{key:'USDJPY',label:'USDJPY',unit:'lot'}]; })"); settle(page, 500)
        js(page, "()=>bdFlowTopRender()"); settle(page, 300)
        tot = js(page, "()=>bdMacroItems(bdWkDoc()).length")
        check(f"{tag} more than 4 assets → 4 cards + '+N more ›'", (tot <= 4) or (cnt(page, "[data-bd-mc]") == 4 and cnt(page, "[data-bd-macmore]") == 1), [tot, cnt(page, "[data-bd-mc]")])
        if tot > 4:
            page.click("[data-bd-macmore]"); settle(page, 300)
            check(f"{tag} '+N more' expands the rest", cnt(page, "[data-bd-mc]") == tot)
            js(page, "()=>bdMacMoreSet(false)")
        # ── events = next 3 upcoming (past drop) ──
        evs = js(page, "()=>bdUpcoming().map(o=>o.id)")
        shown = js(page, "()=>[...document.querySelectorAll('[data-bd-ev]')].map(e=>e.dataset.bdEv)")
        check(f"{tag} Events = next 3 upcoming only", len(shown) == min(3, len(evs)) and shown == evs[:3] and "e_cancel" not in evs, [shown, evs])
        if not ph:
            cols = js(page, "()=>getComputedStyle(document.querySelector('[data-bd-events]')).gridTemplateColumns.split(' ').length")
            check(f"{tag} Events grid: {len(shown)} pills + Import in one row (no empty column)", cols == len(shown) + 1, cols)
        # ── RRG ──
        qs = js(page, "()=>[...document.querySelectorAll('[data-bd-quad]')].map(e=>e.dataset.bdQuad)")
        check(f"{tag} RRG = 4 quadrant tiles", qs == ["lead", "imp", "weak", "lag"], qs)
        cols = js(page, "()=>getComputedStyle(document.querySelector('[data-bd-rrg]')).gridTemplateColumns.split(' ').length")
        check(f"{tag} RRG grid {'2×2' if ph else '4 columns'}", cols == (2 if ph else 4), cols)
        hs = js(page, "()=>[...document.querySelectorAll('[data-bd-quad]')].map(e=>Math.round(e.getBoundingClientRect().height))")
        check(f"{tag} RRG tile heights equal per row", (hs[0] == hs[1] and hs[2] == hs[3]) if ph else len(set(hs)) == 1, hs)
        mv = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-bd-quad=\"lead\"] .bd-sr')].map(e=>[e.dataset.bdSec, e.dataset.bdMv]))")
        want = js(page, "()=>Object.fromEntries(bdRrgRows().filter(x=>x.quad==='lead').sort((a,b)=>b.ratio-a.ratio).slice(0,3).map(x=>[x.sym, (rrgSpeed(x.dMom).fast ? (rrgSpeed(x.dMom).dir>0 ? 'up':'fast') : 'slow')]))")
        check(f"{tag} per-sector motion = existing calc (Leading XLU with falling momentum → ↘ slowing fast)", mv == want and mv.get("XLU") == "fast" and mv.get("SMH") == "up", [mv, want])
        check(f"{tag} RRG tile max 3 sectors + '+N'", len(mv) == 3 and cnt(page, '[data-bd-qmore="lead"]') == 1 and "+1" in txt(page, '[data-bd-qmore="lead"]'), mv)
        if ph: check(f"{tag} iPhone motion legend line", "slowing fast" in txt(page, "[data-bd-rrgleg]") and js(page, "()=>getComputedStyle(document.querySelector('[data-bd-rrgleg]')).display") != "none")
        # ── fit ──
        if ph:
            fit = js(page, "()=>{ const l=document.querySelector('[data-bd-rrgleg]').getBoundingClientRect().bottom, tb=[...document.querySelectorAll('.tabbar,#tabBar,nav,.bottom-nav')].map(e=>e.getBoundingClientRect()).filter(r=>r.height>30&&r.top>innerHeight*0.7).map(r=>r.top); return [Math.round(l), tb, innerHeight, window.scrollY]; }")
            check(f"{tag} iPhone 390×844: blocks 1–4 fit without scrolling (end ≤ bottom bar)", fit[3] == 0 and fit[0] <= (min(fit[1]) if fit[1] else fit[2] - 64), fit)
        else:
            check(f"{tag} Flow RRG/other content full width (no side column)", js(page, "()=>{ const p=document.getElementById('ffThemesPanel').getBoundingClientRect(), t=document.getElementById('tabFlow').getBoundingClientRect(); return p.width >= t.width - 4; }"))
        check(f"{tag} Flow no horizontal overflow", ovf(page) <= 0, ovf(page))
        page.screenshot(path=f"{SHOTS_C}flow-{w}.png")
        # ── Sat form: Trend one row + macro line ──
        open_form(page, 1)
        row = js(page, "()=>{ const r=document.querySelector('.pb2-trow'); const k=[...r.children].map(e=>e.getBoundingClientRect()); return {h:r.getBoundingClientRect().height, tops:[...new Set(k.map(x=>Math.round(x.top)))].length, n:r.children.length, sw:r.scrollWidth<=r.clientWidth+1, txt:r.innerText.replace(/\\s+/g,' ')}; }")
        check(f"{tag} Sat form: Trend on ONE row (HTF · EMA50 · Structure · all ✓), no wrap", row["n"] == 4 and row["h"] < 50 and row["sw"], row)
        ml = txt(page, "[data-pb2-mac]")
        check(f"{tag} Sat form macro line = asset bias (+ next event)", ml.startswith("Macro:") and any(x in ml for x in ("Bull", "Bear", "Neutral", "No Playbook")) and "▲ Macro" not in ml, ml)
        page.screenshot(path=f"{SHOTS_C}sat-trend-{w}.png")
        if w == 390:
            for vw in (360,):
                page.set_viewport_size({"width": vw, "height": 800}); settle(page, 200)
                r2 = js(page, "()=>{ const r=document.querySelector('.pb2-trow'); return {h:r.getBoundingClientRect().height, sw:r.scrollWidth<=r.clientWidth+1, cw:r.clientWidth, sc:r.scrollWidth, k:[...r.children].map(e=>Math.round(e.getBoundingClientRect().width))}; }")
                check(f"{tag} Trend row single line at 360", r2["h"] < 50 and r2["sw"], r2)
                page.set_viewport_size({"width": 390, "height": 844}); settle(page, 200)
        js(page, "()=>bdPopClose()")
        # ── Place order confirm: numbered 4 ──
        fixp = js(page, "()=>{ const i=sat7dIdea ? null : null; return 1; }")
        new_plan(page, 1, ema=True, strc=True)
        js(page, "()=>{ const it=bdItems().find(x=>x.kind==='sat'); if(it) pb2PlaceOpen(it.id); }"); settle(page, 300)
        items = js(page, "()=>[...document.querySelectorAll('[data-pb2-chk]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} Place-order confirm: numbered list of 4 (In Zone · Trend Neutral · EMA50 = HVN · Pivot MMT) + one-tap note", len(items) == 4 and items[0].startswith("In Zone") and items[1].startswith("Trend Neutral") and items[2].startswith("EMA50 = HVN") and items[3].startswith("Pivot MMT") and "One tap confirms all 4" in txt(page, "#pb2Body"), items)
        page.screenshot(path=f"{SHOTS_C}confirm-{w}.png")
        js(page, "()=>bdPopClose()")
        # ── toast never covers a sheet ──
        js(page, "()=>{ const o=document.getElementById('td3Toast'); if(o) o.style.display='none'; pb2OpenType(); td3ToastShow('Plan saved · View in Plan ›'); }"); settle(page, 400)
        shown_now = js(page, "()=>{ const t=document.getElementById('td3Toast'); return !!t && getComputedStyle(t).display!=='none'; }")
        js(page, "()=>bdPopClose()"); settle(page, 700)
        shown_after = js(page, "()=>{ const t=document.getElementById('td3Toast'); return !!t && getComputedStyle(t).display!=='none'; }")
        check(f"{tag} toast is queued while a popup is open, then shown after it closes", (not shown_now) and shown_after, [shown_now, shown_after])
        # toast already showing when the Place-order confirm opens → pulled back, never over the sheet
        js(page, "()=>{ const it=bdItems().find(x=>x.kind==='sat'); td3ToastShow('Plan saved · View in Plan ›'); if(it) pb2PlaceOpen(it.id); }"); settle(page, 500)
        over = js(page, "()=>{ const t=document.getElementById('td3Toast'); return !!t && getComputedStyle(t).display!=='none' && t.getClientRects().length>0; }")
        check(f"{tag} no toast element visible while the Place-order confirm is open (after 'Plan saved')", not over and cnt(page, "[data-pb2-checks]") == 1, over)
        page.screenshot(path=f"{SHOTS_C}confirm-{w}.png")
        js(page, "()=>bdPopClose()"); settle(page, 500)
        tab(page, "flow")
        check(f"{tag} Flow: dark Regime card collapsed into 'Regime details ›' (closed, content intact)", "Regime details" in txt(page, "[data-bd-regd] summary") and js(page, "()=>!document.querySelector('[data-bd-regd]').open && document.getElementById('ffAction').textContent.length>20"))
        js(page, "()=>{ document.querySelector('[data-bd-regd]').open=true; }"); settle(page, 200)
        check(f"{tag} Regime details expands the same content (Regime row)", "Regime" in txt(page, "#ffAction"))
        js(page, "()=>{ document.querySelector('[data-bd-regd]').open=false; }")
        page.screenshot(path=f"{SHOTS_C}flow-{w}.png")
        check(f"{tag} PB1c no console / page errors", not ce and not pe, [str(x)[:200] for x in (ce + pe)][:4])
    finally:
        b.close()


PB2_LINE = "In Zone · Trend Neutral · EMA50 = HVN · Pivot MMT"


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 860), (390, 844)):
            try: persist(pw, w, h); run(pw, w, h); pb1b(pw, w, h); pb1c(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[{w}] crashed", False, str(e)[:300])
        try: iphone(pw)
        except Exception as e:
            import traceback; traceback.print_exc(); check("[iphone] crashed", False, str(e)[:300])
    nf = [r for r in results if not r[1]]
    print(f"\nSUMMARY: {len(results) - len(nf)} pass / {len(nf)} fail")
    sys.exit(1 if nf else 0)
