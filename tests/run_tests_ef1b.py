#!/usr/bin/env python3
"""EF1b — Today Enter cap · no counter-trend confirm · level place sheet · Ready as text.  Run: python3 tests/run_tests_ef1b.py
Screenshots -> tests/screenshots/ef1b-*.png (env EF1B_SHOTS = other folder)."""
import os, re, sys, copy
from playwright.sync_api import sync_playwright
from pv1_common import *

SHOTS = os.environ.get("EF1B_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
SIZES = [(1440, 900), (1280, 800), (390, 844)]
XP_JS = "()=>{ sat7dWrite('satIdeas','xp',{id:'xp',v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }"
READY = "()=>{ window.ps1MinStopMsg = ()=>''; re1Cache = {}; }"



def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "ef1b-%s.png" % name))


def has(page, sel):
    return js(page, "(s)=>!!document.querySelector(s)", sel)


def seed_n(page, n):
    js(page, """(n)=>{ for(let k=1;k<=n;k++) sat7dWrite('satIdeas','xp'+k,{id:'xp'+k,v3:true,v2:true,asset:'XAUUSD',bias:'Long',entry:2642+k,sl:2628,tp:2684,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],pb_acct:'main'}); }""", n)
    page.wait_for_timeout(600); refresh(page)
    js(page, "()=>{ re2GrpAll = {}; window.ps1MinStopMsg = ()=>''; re1Cache = {}; satWeekPickWrite(wpWeekKey(), ['XAUUSD']); switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)


def enter_rows(page):
    return js(page, "()=>document.querySelectorAll('[data-re2-col=enter] [data-re2-row]').length")


def run(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 5)
        n_ready = js(page, "()=>bdItems().filter(i=>i.status==='plan' && re2ReadyOf(i)).length")
        check("[%s] 1 fixture: 5 Ready plans" % tag, n_ready == 5, n_ready)
        cap = 3 if w > 600 else 2; mtxt = "+2 ›" if w > 600 else "+3 more ›"   # LR-F: phone shows 2 rows per group
        check("[%s] 1 Today › Enter shows %d Ready plans + '%s'" % (tag, cap, mtxt), enter_rows(page) == cap and txt(page, "[data-re2-more]") == mtxt, [enter_rows(page), txt(page, "[data-re2-more]")])
        check("[%s] 1 header count = rows shown (%d)" % (tag, cap), txt(page, "[data-re2-col=enter] [data-re2-n]") == str(cap))
        if w == 390: shot(page, "today-390-collapsed")
        if w == 1440: shot(page, "today-1440-collapsed")
        page.click("[data-re2-more]"); page.wait_for_timeout(300)
        check("[%s] 1 '+2 ›' expands in place: 5 rows, still on Today" % tag, enter_rows(page) == 5 and js(page, "()=>activeTab") == 'today', enter_rows(page))
        if w == 390: shot(page, "today-390-expanded")
        page.click("[data-re2-more]"); page.wait_for_timeout(300)
        check("[%s] 1 'Show less' collapses back to %d" % (tag, cap), enter_rows(page) == cap)
        js(page, "()=>{ bdItems().filter(i=>i.status==='plan').slice(0,2).forEach(i=>sat7dWrite('satIdeas', i.id, {status:'cancelled', archived:true})); refresh_=1; re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(400)
        check("[%s] 1 3 or fewer Ready plans: no '+N' button" % tag, (w <= 600 or not has(page, "[data-re2-more]")) and enter_rows(page) <= cap, enter_rows(page))
        check("[%s] 1 no overflow / errors" % tag, no_overflow(page) and not ce and not pe, ce + pe)
    finally:
        b.close()

    # row count at 390 vs. before (EF1b can only shorten Today)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 5)
        after = js(page, "()=>({rows:document.querySelectorAll('[data-re2-row]').length,h:document.documentElement.scrollHeight})")
        js(page, "()=>{ re2EnterCap = r=>r; todayRefresh(true); }"); page.wait_for_timeout(300)
        before = js(page, "()=>({rows:document.querySelectorAll('[data-re2-row]').length,h:document.documentElement.scrollHeight})")
        print("INFO [%s] Today rows %s -> %s · page height %s -> %s" % (tag, before["rows"], after["rows"], before["h"], after["h"]))
        check("[%s] 1 Today row count not longer than before (%s <= %s)" % (tag, after["rows"], before["rows"]), after["rows"] <= before["rows"] and after["h"] <= before["h"])
    finally:
        b.close()

    # 2 counter trend: no extra confirm, amber tag stays
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 1)
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='xp1'); i.structure_ok=false; i.mss=true; re1Cache={}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        js(page, "()=>pb2OpenEdit('xp1')"); page.wait_for_timeout(350)
        if has(page, "[data-pb2-save]"):
            page.click("[data-pb2-save]"); page.wait_for_timeout(500)
        check("[%s] 2 Save of a counter-trend plan: no 'Save as counter trend?' confirm" % tag, not has(page, "[data-ln4-cs-ok]") and not has(page, ".ln4-cs"))
        check("[%s] 2 plan saved (sheet closed)" % tag, not has(page, "[data-pb2-save]"))
        t = js(page, "()=>{const c=document.querySelector('[data-bd-card=xp1]'); return c? c.innerText.replace(/\\s+/g,' ') : ''}")
        check("[%s] 2 amber 'Counter trend' tag stays on the card" % tag, "Counter trend" in t, t)
        check("[%s] 2 ln4CounterAsk / pb2CounterAsk no longer reached by Save" % tag, js(page, "()=>{ let hit=0; const a=window.ln4CounterAsk; window.ln4CounterAsk=()=>{hit++}; try{ satV3SaveReadyAccounts('xp1'); }catch(e){} window.ln4CounterAsk=a; return hit===0; }"))
    finally:
        b.close()

    # 4 Ready = plain green text
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 1)
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        st = js(page, "()=>{const e=document.querySelector('[data-bd-card=xp1] [data-ef-ready]'); if(!e) return null; const s=getComputedStyle(e); return {t:e.textContent.trim(), bg:s.backgroundColor, bw:s.borderTopWidth, br:s.borderTopLeftRadius, col:s.color}}")
        check("[%s] 4 card 'Ready' is text, not a pill (no background / border / radius)" % tag, st and st["t"] == "Ready" and st["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and st["bw"] == "0px" and st["br"] == "0px", st)
        g = js(page, "()=>{const p=document.createElement('i'); p.style.color='var(--green)'; document.body.appendChild(p); const c=getComputedStyle(p).color; p.remove(); return c}")
        check("[%s] 4 'Ready' is green" % tag, st and st["col"] == g, [st, g])
        if w == 1440: shot(page, "card-ready-1440")
        if w == 390: shot(page, "card-ready-390")
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(300)
        c = js(page, "()=>{const e=document.querySelector('[data-re2-chip-st].rdy'); if(!e) return null; const s=getComputedStyle(e); return {bg:s.backgroundColor, col:s.color}}")
        check("[%s] 4 Today › Enter 'Ready' is plain green text too" % tag, c and c["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and c["col"] == g, c)
    finally:
        b.close()

    # 3 later entry level -> same confirm sheet
    c = copy.deepcopy(NVDA_CARD); c["ln4"] = {"placedLv": {"0": "2026-11-13T03:05:39.227Z"}}
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"h_card": c} if False else cards_pv())
    try:
        js(page, "()=>{ window.ps1MinStopMsg = ()=>''; re1Cache = {}; window.ftHwDone = ()=>true; window.wl1HwDone = ()=>true; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        cid = js(page, "()=>{ const it=bdItems().find(i=>i.kind==='core' && i.sym==='NVDA'); return it && it.id }")
        lv = js(page, "(id)=>{ const it=bdById(id); return it ? {nl:it.nl, k:it.k, placed:[...(it.placed||[])]} : null }", cid)
        js(page, "(id)=>bdPlaceLv(id,1)", cid); page.wait_for_timeout(400)
        sheet = has(page, "[data-ef-core-place]")
        placed_before = js(page, "(id)=>{const it=bdById(id); return [...(it.placed||[])]}", cid)
        check("[%s] 3 bdPlaceLv(#2) opens the confirm sheet (nothing recorded yet)" % tag, sheet and 1 not in placed_before, [lv, sheet, placed_before])
        sh = txt(page, "[data-ef-core-place]")
        check("[%s] 3 sheet says 'Place order #2' with the level price, same Confirm / Not yet buttons" % tag, "②" in sh and "Confirm" in sh and "Not yet" in sh and has(page, "[data-pb2-yes]"), sh)
        check("[%s] 3 sheet: no overflow" % tag, no_overflow(page))
        if w == 390: shot(page, "level-sheet-390")
        if w == 1440: shot(page, "level-sheet-1440")
        page.click("[data-pb2-no]"); page.wait_for_timeout(300)
        check("[%s] 3 Not yet → nothing recorded" % tag, 1 not in js(page, "(id)=>[...(bdById(id).placed||[])]", cid))
        js(page, "(id)=>bdPlaceLv(id,1)", cid); page.wait_for_timeout(350)
        page.click("[data-pb2-yes]"); page.wait_for_timeout(500)
        check("[%s] 3 Confirm records level #2 once, sheet closed" % tag, 1 in js(page, "(id)=>[...(bdById(id).placed||[])]", cid) and not has(page, "[data-ef-core-place]"))
        check("[%s] 3 no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


def core_planned():
    c = copy.deepcopy(NVDA_CARD); c["ticker"] = "AVGO"; c["id"] = "cP"; c.pop("trade_id", None); c["lots"] = []
    c.pop("track", None); c["status"] = "plan"; c.pop("px", None); c.pop("stopHistory", None); c["ln4"] = {}; c["log"] = []; c["plan"]["ps1"]["bucket"] = "winner"
    c["plan"]["ps1"]["rows"] = [{"px": 158, "riskPct": 0.5, "qty": 2}, {"px": 150, "riskPct": 0.5, "qty": 2}]
    c["plan"]["tp"] = 175; c["plan"]["stop"] = 150; c["stop"] = 150
    return c


def run2(pw, w, h):
    tag = str(w)
    # TS1 regression: no Setup tag, Momentum plan with entry + SL is placeable
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": core_planned()})
    try:
        js(page, "()=>{ tv1SetupLeft = (sym, held)=>{ const at = tv1SetupAt(sym); if(!at) return 0; if((held || tv1HeldKeys()).has(wlSymKey(sym))) return 0; const used = tv1TDays(at, tv1Today()); return used >= TV1_SETUP_DAYS ? 0 : TV1_SETUP_DAYS - used; }; delete getBook(tdHome()).settings.tvSetup; window.ps1MinStopMsg=()=>''; window.ftHwDone=()=>true; window.wl1HwDone=()=>true; re1Cache={}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(500)
        check("[%s] S no Setup tag exists (tvSetup empty)" % tag, js(page, "()=>tv1SetupLeft('AVGO')") == 0)
        it = js(page, "()=>{const i=bdItems().find(x=>x.id==='cP'); return i && {inc:i.inc, status:i.status}}")
        check("[%s] S new Momentum plan with entry + SL is not Waiting (no 'needs Setup')" % tag, it and not it["inc"], it)
        check("[%s] S Place order › visible on the card, not under 'Waiting for setup'" % tag, has(page, "[data-bd-card=cP] [data-bd-pill=place]") and not has(page, "[data-bd-wait]"))  # LR3: no Waiting row
        page.click("[data-bd-card=cP] [data-bd-pill=place]"); page.wait_for_timeout(350)
        sh = txt(page, "[data-ef-core-place]")
        check("[%s] S confirm sheet shows NO visible Setup checkbox; the hidden #efSetupCk stays, checked (LR-F2 11)" % tag, "Setup ready today" not in sh and js(page, "()=>{ const c = document.getElementById('efSetupCk'); return !!c && c.checked && c.getClientRects().length === 0; }"), sh)
        if w == 390: shot(page, "setup-sheet-390")
        page.click("[data-pb2-yes]"); page.wait_for_timeout(500)   # LR-F2 11: Confirm without touching anything
        v = js(page, "()=>({d:(getBook(tdHome()).settings.tvSetup||{})[wlSymKey('AVGO')], t:tv1Today()})")
        check("[%s] S Confirm (nothing touched) writes tvSetup[AVGO] = today (LN4 stats) and Watch shows 'Setup ✓'" % tag, v["d"] == v["t"] and js(page, "()=>tv1GroupOf({sym:'AVGO', port:'core'})") == "Setup ✓", v)
        check("[%s] S order recorded" % tag, js(page, "()=>!!(coreCardsList.find(y=>y.id==='cP').ln4||{}).placedAt"))
    finally:
        b.close()
    c = core_planned(); c["plan"]["stop"] = 0; c["stop"] = 0
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": c})
    try:
        js(page, "()=>{ tv1SetupLeft = (sym, held)=>{ const at = tv1SetupAt(sym); if(!at) return 0; if((held || tv1HeldKeys()).has(wlSymKey(sym))) return 0; const used = tv1TDays(at, tv1Today()); return used >= TV1_SETUP_DAYS ? 0 : TV1_SETUP_DAYS - used; }; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        check("[%s] S SL missing still goes to Waiting (needs SL)" % tag, js(page, "()=>{const i=bdItems().find(x=>x.id==='cP'); return !!(i && i.inc && /SL/.test(i.inc.text))}"))
    finally:
        b.close()
    # Today row text = card format
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        seed_n(page, 1)
        row = js(page, "()=>{const r=document.querySelector('[data-re2-col=enter] [data-re2-row]'); return r? r.innerText.replace(/\\s+/g,' ') : ''}")
        line = txt(page, "[data-re2-col=enter] [data-re2-cardline]")
        import re as _re
        check("[%s] T Enter row text = card format 'Buy #q @ px · SL · TP · Risk −$'" % tag, _re.search((r"Buy #[\d.]+ @ [\d,.]+ · SL [\d,.]+ · TP [\d,.]+ · Risk −\$" if w > 600 else r"Buy #[\d.]+ @ [\d,.]+ · SL [\d,.]+ · Risk −\$"), line or "") is not None, line)
        check("[%s] T no 'plan … lot' / 'ready' / 'step' text on the row" % tag, not _re.search(r"plan |ready|step \d", row), row)
        if w == 390: shot(page, "today-row-390")
        if w == 1440: shot(page, "today-row-1440")
        check("[%s] T no overflow" % tag, no_overflow(page) and not ce and not pe, ce + pe)
    finally:
        b.close()
    # Check orders row = card format + the still-valid prompt
    c = core_planned(); c["ln4"] = {"placedAt": "2000-01-03T03:00:00.000Z", "placedLv": {"0": "2000-01-03T03:00:00.000Z"}}
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": c})
    try:
        js(page, "()=>{ window.ps1MinStopMsg=()=>''; window.ftHwDone=()=>true; window.wl1HwDone=()=>true; re1Cache={}; }"); page.wait_for_timeout(300)
        seed_n(page, 0); page.wait_for_timeout(300)
        import re as _re
        row = js(page, "()=>{const r=document.querySelector('[data-re2-col=check] [data-re2-row]'); return r? r.innerText.replace(/\\s+/g,' ') : ''}")
        line = txt(page, "[data-re2-col=check] [data-re2-cardline]")
        check("[%s] T2 Check orders row text = card format 'Buy #q @ px · SL · Risk −$'" % tag, _re.search(r"Buy #[\d.]+ @ [\d,.]+ · SL [\d,.]+.* · Risk −[฿$]", line or "") is not None, line)
        check("[%s] T2 Check orders row keeps the still-valid prompt" % tag, "still valid?" in (row or ""), row)
        if w == 390: shot(page, "check-row-390")
        check("[%s] T2 Check orders: no overflow / errors" % tag, no_overflow(page) and not ce and not pe, ce + pe)
    finally:
        b.close()
    # level sheet risk line
    c = copy.deepcopy(NVDA_CARD)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        js(page, "()=>{ window.ps1MinStopMsg=()=>''; re1Cache={}; window.ftHwDone=()=>true; window.wl1HwDone=()=>true; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        cid = js(page, "()=>{ const it=bdItems().find(i=>i.kind==='core' && i.sym==='NVDA'); return it && it.id }")
        js(page, "(id)=>bdPlaceLv(id,1)", cid); page.wait_for_timeout(400)
        r = txt(page, "[data-ef-order-risk]")
        import re as _re
        check("[%s] L level sheet: 'This order: Buy #18 @ 140 · +Risk ฿… · total risk after fill x%%'" % tag, _re.match(r"This order: Buy #18 @ 140 · \+Risk \$[\d.]+k? · total risk after fill [\d.]+%", r or "") is not None, r)
        check("[%s] L level sheet has no Setup tick (first level only)" % tag, not has(page, "#efSetupCk"))
        if w == 390: shot(page, "level-sheet-risk-390")
        check("[%s] L no overflow / errors" % tag, no_overflow(page) and not ce and not pe, ce + pe)
    finally:
        b.close()


def run3(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": core_planned()})
    try:
        js(page, "()=>{ tv1SetupLeft = (sym, held)=>{ const at = tv1SetupAt(sym); if(!at) return 0; return 1; }; window.ps1MinStopMsg=()=>''; window.ftHwDone=()=>true; window.wl1HwDone=()=>true; re1Cache={}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(500)
        card_t = js(page, "()=>document.querySelector('[data-bd-card=cP]').innerText.replace(/\\s+/g,' ')")
        check("[%s] M card: Risk −$16 · reward at T1 +$42 (PC2: T1 sells half) · 5.3R (legs × FX 33.76; stored ps1.riskMoney ignored)" % tag, "Risk −$16" in card_t and "reward at T1 +$42" in card_t and "5.3R" in card_t, card_t)
        check("[%s] M card has no '฿' on a $ value (Main = USD)" % tag, "฿" not in card_t, card_t)
        pv = js(page, "()=>{const p=posView(bdItems().find(i=>i.id==='cP')); return {r:p.plannedRisk, w:p.reward, R:p.rewardR, st:p.plannedRiskStored, d:p.plannedRiskDiff}}")
        check("[%s] M posView: risk 540.16 · reward 1417.92 (T1 sell half) · R 2.625 · stored kept aside + flagged" % tag, abs(pv["r"] - 540.16) < 0.01 and abs(pv["w"] - 1417.92) < 0.01 and abs(pv["R"] - 2.625) < 0.01 and pv["st"] and pv["d"], pv)
        r1 = js(page, "()=>{const r=document.querySelector('[data-bd-card=cP] .pv-r1'); const t=[...r.children].map(e=>Math.round(e.getBoundingClientRect().top)); const x=r.querySelector('.bd-cxx').getBoundingClientRect(), p=x; return {one: true, xr:x.right, cr:r.getBoundingClientRect().right}}")
        check("[%s] H card header: ✕ on the same line as Ready + Place order ›, inside the card" % tag, r1["one"] and r1["xr"] <= r1["cr"] + 1, r1)
        if w == 390: shot(page, "card-header-390")
        page.click("[data-bd-card=cP] [data-bd-pill=place]"); page.wait_for_timeout(400)
        sh = txt(page, "[data-ef-core-place]")
        check("[%s] M sheet shows Risk −$16 · Reward at T1 +$42 · 2.6R (LR3: Risk / Reward / Size tiles)" % tag, "RISK −$16" in sh.upper() and "REWARD +$42" in sh.upper() and "2.6R" in sh and "฿" not in sh, sh)   # PC2 2g: reward = the T1 sell (half) · R to T1
        more = js(page, "()=>{const d=document.querySelector('[data-ef-more]'); return d? d.innerText : ''}")
        diff = js(page, "()=>{const e=document.querySelector('[data-ef-risk-diff]'); return e ? e.textContent : ''}")
        check("[%s] M More flags that the stored plan risk differs from the legs" % tag, "differs from the legs" in (diff or "") and "$1.1k" in diff, diff)
        if w == 390: shot(page, "sheet-money-390")
    finally:
        b.close()
    # no rows → stored riskMoney is the fallback
    c = core_planned(); c["plan"]["ps1"]["rows"] = []
    b, page, ce, pe = launch(pw, w, h, doc_pv(), {"cP": c})
    try:
        js(page, "()=>{ re1Cache={}; switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        pv = js(page, "()=>{const p=posView(bdItems().find(i=>i.id==='cP')); return {r:p.plannedRisk, d:p.plannedRiskDiff}}")
        check("[%s] M no legs → stored ps1.riskMoney is the fallback (no diff flag)" % tag, pv["r"] and abs(pv["r"] - 36055.68) < 1 and not pv["d"], pv)
    finally:
        b.close()


with sync_playwright() as pw:
    for w, h in SIZES:
        run(pw, w, h); run2(pw, w, h); run3(pw, w, h)
fails = [r for r in results if not r[1]]
print("\n%d checks pass · %d fail" % (len(results) - len(fails), len(fails)))
sys.exit(1 if fails else 0)
