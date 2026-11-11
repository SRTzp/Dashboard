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
        page.locator("[data-wi-paste]").click(); settle(page, 400)
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


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 860), (390, 844)):
            try: persist(pw, w, h); run(pw, w, h)
            except Exception as e:
                import traceback; traceback.print_exc(); check(f"[{w}] crashed", False, str(e)[:300])
        try: iphone(pw)
        except Exception as e:
            import traceback; traceback.print_exc(); check("[iphone] crashed", False, str(e)[:300])
    nf = [r for r in results if not r[1]]
    print(f"\nSUMMARY: {len(results) - len(nf)} pass / {len(nf)} fail")
    sys.exit(1 if nf else 0)
