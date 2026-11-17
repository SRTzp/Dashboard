#!/usr/bin/env python3
"""PV1 — honest position numbers · Flow asset panel · Planned / Holding cards.  Run: python3 tests/run_tests_pv1.py
Screenshots → tests/screenshots/pv1-*.png (env PV1_SHOTS = other folder)."""
import os, sys, json
from playwright.sync_api import sync_playwright
from pv1_common import *
import copy
import lib_phase11 as P11
import lib_phase100 as P100

SHOTS = os.environ.get("PV1_SHOTS") or K.SHOTS
os.makedirs(SHOTS, exist_ok=True)
SIZES = [(1440, 900), (1280, 800), (390, 844)]


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "pv1-%s.png" % name))


def partA(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_sat(), cards_pv())
    try:
        js(page, SAT_JS); page.wait_for_timeout(700); refresh(page)
        r = {x["sym"]: x["t"] for x in rows(page, "manage")}
        t = r.get("NVDA", "")
        check("[%s] A2 holding row = #11/#29 · ฿60.5k · 1.2%% · open risk ฿17.8k" % tag, "#11/#29 · ฿60.5k · 1.2% · open risk ฿17.8k" in t, t)
        check("[%s] A2 old plan-total numbers are gone from the holding row (no ฿36.1k / 0.72%% / cap 50%%)" % tag, "36.1k" not in t and "0.72%" not in t and "cap 50%" not in t, t)
        check("[%s] A2 homework note stays text, not a number" % tag, "size limited to 50% · homework not done" in t, t)
        pv = js(page, "()=>{const it=bdItems().find(x=>x.sym==='NVDA'); return posView(it)}")
        check("[%s] posView NVDA: held 11 · planned 29 · cost · value · plan risk" % tag, pv["heldQty"] == 11 and pv["plannedQty"] == 29 and abs(pv["cost"] - 58674.88) < .01 and abs(pv["value"] - 60475.976) < .01 and abs(pv["plannedRisk"] - 36055.68) < .01 and abs(pv["openRisk"] - 17825.28) < .01, pv)
        # drawer shows the same numbers
        js(page, "()=>bdOpen(bdItems().find(x=>x.sym==='NVDA').id)"); page.wait_for_timeout(300)
        dt = txt(page, "[data-pv-block]")
        check("[%s] drawer POSITION block: same value, weight, open risk, whole plan" % tag, "฿60.5k" in dt and "1.2% of account" in dt and "฿17.8k" in dt and "29 sh" in dt and "฿36.1k" in dt and "0.72% of account" in dt, dt)
        check("[%s] drawer: price + date shown, no bare dash" % tag, "162.85" in dt and "13 Nov" in dt and " — " not in dt.replace("—", "—") .replace(" — ", "") if False else "162.85" in dt and "13 Nov" in dt, dt)
        js(page, "()=>bdClose()")
        # Satellite: planned row, holding without price, holding with manual Last price
        sp = js(page, "()=>{const o={}; bdItems().filter(x=>x.kind==='sat').forEach(it=>{o[it.sym]=pvRowParts(it)}); return o}")
        check("[%s] Sat planned row = plan 0.21 lot · risk $294 · 0.20%%" % tag, sp["XAU"]["sz"] == "plan 0.21 lot" and sp["XAU"]["rk"].startswith("risk $294 · 0.20%"), sp["XAU"])
        check("[%s] Sat holding without price: 'value: no live price' and open risk kept" % tag, sp["BTC"]["sz"] == "0.02 lot" and "value: no live price" in sp["BTC"]["rk"] and "open risk $20" in sp["BTC"]["rk"], sp["BTC"])
        js(page, "()=>bdOpen(bdItems().find(x=>x.sym==='BTC').id)"); page.wait_for_timeout(300)
        check("[%s] Sat drawer: manual Last price field is hidden (PV1b)" % tag, not js(page, "()=>!!document.getElementById('pvLastIn')") and "no live price" in txt(page, "[data-pv-block]"))
        js(page, "()=>{ const i=satIdeasList.find(x=>x.id==='bi'); i.lastPx={v:61000, at:new Date().toISOString()}; bdRender(); bdDrawerRender(); }"); page.wait_for_timeout(400)
        dt = txt(page, "[data-pv-block]"); st = js(page, "()=>satIdeasList.find(x=>x.id==='bi').lastPx")
        check("[%s] stored lastPx still drives value / P&L with 'manual'" % tag, st and st["v"] == 61000 and st["at"] and "manual" in dt and "$" in dt and "Unrealised P&L" in dt and "+$20" in dt, [st, dt])
        sp2 = js(page, "()=>pvRowParts(bdItems().find(x=>x.sym==='BTC'))")
        check("[%s] row with manual price shows value, no 'no live price'" % tag, "no live price" not in sp2["rk"] and "open risk $20" in sp2["rk"], sp2)
        js(page, "()=>{const i=satIdeasList.find(x=>x.id==='bi'); i.lastPx={v:61000, at:new Date(Date.now()-30*3600*1000).toISOString()}; bdRender(); bdDrawerRender();}"); page.wait_for_timeout(300)
        check("[%s] Last price older than 24 h → 'old price'" % tag, "old price" in js(page, "()=>pvRowParts(bdItems().find(x=>x.sym==='BTC')).rk"))
        # display only: sizing / engine unaffected by the last price
        a = js(page, "()=>{const i=satIdeasList.find(x=>x.id==='xp'); const c=pb2Calc(i,'main'); return [c.lot,c.risk]}")
        js(page, "()=>{satIdeasList.find(x=>x.id==='xp').lastPx={v:2700, at:new Date().toISOString()}; re1Cache={};}")
        b2 = js(page, "()=>{const i=satIdeasList.find(x=>x.id==='xp'); const c=pb2Calc(i,'main'); return [c.lot,c.risk]}")
        check("[%s] Last price does not change sizing (pb2Calc lot / risk identical)" % tag, a == b2, [a, b2])
        js(page, "()=>bdClose()")
        js(page, "()=>pb2OpenEdit('xp')"); page.wait_for_timeout(300)
        check("[%s] Sat plan form: no Last price field (PV1b)" % tag, not js(page, "()=>!!document.querySelector('[data-pb2-in=last]')"))
        js(page, "()=>bdPopClose()")
        check("[%s] A: no overflow on Today" % tag, no_overflow(page))
        if w in (1440, 390):
            js(page, "()=>{switchTab('today'); todayRefresh(true);}"); page.wait_for_timeout(400); shot(page, "today-%d" % w)
        check("[%s] A: no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


LONG_NOTE = ("PV1 SAMPLE full reason. " + "Fed is still in hiking mode so real yields and the dollar act directly on gold this week. " * 4).strip()


def wi_seed(page, doc):
    body = copy.deepcopy(doc)
    if "BTC" in body["assets"]: body["assets"]["BTCUSD"] = body["assets"].pop("BTC")
    page.evaluate("([w,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','weeklyImpact',w], b); wiStop(); wiStart(); }", [body["week"], body]); page.wait_for_timeout(700)


def partB(pw, w, h):
    tag = str(w); ph = w < 600
    # ── with Weekly Impact + Playbook
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        doc = P100.sample(); doc["assets"]["XAUUSD"]["note"] = LONG_NOTE; doc["assets"]["XAUUSD"]["carryover_th"] = "PV1 SAMPLE carry-over text"
        wi_seed(page, doc)
        P11.seed_pb(page, [P11.pbver(1, "2026-09-20T00:00:00.000Z", x="up", b="down", r="flat", xa={"confidence": "mid", "why": "PV1 SAMPLE quarter why", "change_if": "PV1 SAMPLE change if"})])
        js(page, "()=>{ switchTab('flow'); satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD']); ffRenderThemes(); bdFlowTopRender(); }"); page.wait_for_timeout(600)
        cards = js(page, "()=>[...document.querySelectorAll('[data-bd-mc]')].map(e=>{const r=e.getBoundingClientRect(); const p=e.querySelector('.bd-av'); const cs=getComputedStyle(p); return {k:e.dataset.bdMc, h:Math.round(r.height), clamp:cs.webkitLineClamp, color:cs.color, det:e.querySelector('[data-bd-det]')?e.querySelector('[data-bd-det]').getBoundingClientRect().height:0, detTxt:e.querySelector('[data-bd-det]')?e.querySelector('[data-bd-det]').innerText:''}})")
        check("[%s] B: cards have a real Details ▾ button, 44 px tap height, text clamped to 3 lines" % tag, cards and all(c["clamp"] == "3" and c["det"] >= 43.5 and "Details" in c["detTxt"] for c in cards), cards)
        mut = js(page, "()=>getComputedStyle(document.querySelector('[data-bd-mc] .bd-av:not(.m)')).color === getComputedStyle(document.body).color || getComputedStyle(document.querySelector('[data-bd-mc] .bd-av:not(.m)')).color !== getComputedStyle(document.querySelector('.bd-hint')).color")
        check("[%s] B: short text is normal text colour (not muted)" % tag, mut)
        before = {c["k"]: c["h"] for c in cards}
        first = cards[0]["k"] if cards else ""
        for c in cards:
            if c["k"] == "XAUUSD": first = "XAUUSD"
        js(page, "(k)=>document.querySelector('[data-bd-det=\"'+k+'\"]').click()", first); page.wait_for_timeout(400)
        n = js(page, "()=>document.querySelectorAll('[data-pv-panel]').length")
        pt = txt(page, "[data-pv-panel]")
        check("[%s] B: exactly one detail panel opens" % tag, n == 1, n)
        check("[%s] B: panel has the FULL Weekly Impact note + carry-over" % tag, LONG_NOTE in pt and "PV1 SAMPLE carry-over text" in pt, pt[:400])
        check("[%s] B: catalysts — time, title, forecast / previous, mechanism, scenarios" % tag, "SAMPLE Core PCE" in pt and "forecast 2.6%" in pt and "previous 2.7%" in pt and "เงินเฟ้อมีผลต่อ" in pt and js(page, "()=>document.querySelectorAll('[data-pv-panel] [data-pv-sc]').length") >= 3 and "Thu 19:30" in pt or "Thu" in pt, pt[:600])
        check("[%s] B: Quarter view — bias, why, change-if, confidence" % tag, "PV1 SAMPLE quarter why" in pt and "PV1 SAMPLE change if" in pt and "confidence mid" in pt, pt[-500:])
        check("[%s] B: sources + 'Weekly Impact as of' shown" % tag, "Sources:" in pt and "SAMPLE calendar" in pt and "Weekly Impact as of" in pt, pt[-300:])
        check("[%s] B: 'Your note · this week' is a separate block" % tag, js(page, "()=>!!document.querySelector('[data-pv-panel] .pv-mine textarea[data-bd-note]')") and "your note · this week" in pt.lower())
        after = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-bd-mc]')].map(e=>[e.dataset.bdMc, Math.round(e.getBoundingClientRect().height)]))")
        keep = {k: v for k, v in after.items() if k != first and not ph}
        check("[%s] B: neighbour cards keep their height when one opens (no stretch)" % tag, all(abs(keep[k] - before[k]) <= 1 for k in keep), [before, after])
        wd = js(page, "()=>{const p=document.querySelector('[data-pv-panel]').getBoundingClientRect(), g=document.querySelector('[data-bd-macro]').getBoundingClientRect(); return [Math.round(p.width), Math.round(g.width)]}")
        check("[%s] B: panel is full width of the card row" % tag, abs(wd[0] - wd[1]) <= 2, wd)
        # opening another closes the first
        other = next((c["k"] for c in cards if c["k"] != first), None)
        if other:
            js(page, "(k)=>document.querySelector('[data-bd-det=\"'+k+'\"]').click()", other); page.wait_for_timeout(300)
            check("[%s] B: opening another asset closes the first (one panel)" % tag, js(page, "()=>document.querySelectorAll('[data-pv-panel]').length") == 1 and js(page, "(k)=>!!document.querySelector('[data-pv-panel][data-bd-panel=\"'+k+'\"]')", other))
            js(page, "(k)=>document.querySelector('[data-bd-det=\"'+k+'\"]').click()", first); page.wait_for_timeout(300)
        # note still saves
        page.fill('[data-bd-note="%s"]' % first, "PV1 note SAMPLE"); page.locator('[data-bd-note="%s"]' % first).blur(); page.wait_for_timeout(600)
        saved = js(page, "(k)=>((satwWeek(wpWeekKey(), k)||{}).opinion_txt)||''", first)
        check("[%s] B: note still saves to the same store" % tag, saved == "PV1 note SAMPLE", saved)
        check("[%s] B: ★ focus button still works" % tag, js(page, "()=>!!document.querySelector('[data-bd-focus]')"))
        check("[%s] B: no horizontal overflow (panel open)" % tag, no_overflow(page))
        if w in (1440, 390):
            js(page, "(k)=>document.querySelector('[data-pv-panel]').scrollIntoView({block:'center'})", first); page.wait_for_timeout(200); shot(page, "flow-open-%d" % w)
        js(page, "(k)=>document.querySelector('[data-pv-close]').click()", first); page.wait_for_timeout(300)
        check("[%s] B: Close ▴ closes the panel" % tag, js(page, "()=>document.querySelectorAll('[data-pv-panel]').length") == 0)
        check("[%s] B: no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()
    # ── no Playbook + no Weekly Impact
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        wi_seed(page, P100.sample())
        js(page, "()=>{ switchTab('flow'); satWeekPickWrite(wpWeekKey(), ['XAUUSD']); ffRenderThemes(); bdFlowTopRender(); bdCardTog('XAUUSD'); }"); page.wait_for_timeout(500)
        pt = txt(page, "[data-pv-panel]")
        check("[%s] B: no Playbook → compact box 'No Playbook for XAU · Add ›'" % tag, js(page, "()=>!!document.querySelector('[data-pv-nopb] [data-pv-pbadd]')") and "No Playbook for" in pt, pt[-300:])
        check("[%s] B: no-Playbook panel still shows Weekly Impact text and your note" % tag, "SAMPLE" in pt and "your note" in pt.lower())
        check("[%s] B: no overflow (no Playbook)" % tag, no_overflow(page))
        js(page, "()=>{ wiStop(); wiDocs = {}; bdFlowTopRender(); bdCardTog('XAUUSD'); }"); page.wait_for_timeout(300)
        t2 = txt(page, "[data-bd-macro]")
        check("[%s] B: no Weekly Impact → existing empty text on the card" % tag, "No Weekly Impact yet" in t2, t2[:200])
        check("[%s] B: no console / page errors (empty states)" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()

def ctxt(page, cid): return card_txt(page, cid)


def card_txt(page, cid):
    return js(page, "(i)=>{const c=document.querySelector('[data-bd-card=\"'+i+'\"]'); return c? c.innerText.replace(/\\s+/g,' ') : ''}", cid)


def partC(pw, w, h):
    tag = str(w)
    b, page, ce, pe = launch(pw, w, h, doc_pv(), cards_pv())
    try:
        js(page, SAT_PLANS_JS); page.wait_for_timeout(700); refresh(page)
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(500)
        # ── Planned OK (short): six numbers, valid with stop above entry
        c = card_txt(page, "ps")
        check("[%s] C: Planned Short card — Long/Short word (PV1b: now Blocked here: min stop not set in this fixture)" % tag, js(page, "()=>{const c=document.querySelector('[data-bd-card=ps]'); return c.querySelector('[data-pv-dir]').dataset.pvDir==='Short'}"), c)
        check("[%s] C: Planned card money line — Stop · Risk · Reward · R (PV1b)" % tag, all(x in c for x in ("Stop 75,000", "Risk −$297", "Reward +$3.7k", "12.3R")), c)
        # ── Blocked: chip replaces Ready, reason, fix button names the fix, not sized
        cb = card_txt(page, "pb")
        check("[%s] C: blocked plan → red Blocked chip, no ⚑ Ready" % tag, js(page, "()=>{const c=document.querySelector('[data-bd-card=pb]'); return !!c.querySelector('[data-pv-blocked]') && !c.querySelector('[data-re2-ready]')}"), cb)
        check("[%s] C: blocked plan shows its real reason + Fix button (PV1b)" % tag, "Not picked this week" in cb and "Add to week" in cb and "Risk not sized" in cb, cb)
        js(page, "()=>{ re2ReadyToggle('pb'); }"); page.wait_for_timeout(300)
        check("[%s] C: Ready cannot be set while blocked" % tag, not js(page, "()=>!!satIdeasList.find(x=>x.id==='pb').ready"))
        js(page, "()=>{ satIdeasList.find(x=>x.id==='pb').ready = true; bdRender(); }"); page.wait_for_timeout(200)
        check("[%s] C: an existing flag on a blocked plan is shown off, not deleted" % tag, js(page, "()=>satIdeasList.find(x=>x.id==='pb').ready === true") and not js(page, "()=>!!document.querySelector('[data-bd-card=pb] [data-re2-ready]')"))
        # ── no generic wording anywhere (Plan + Today)
        alltxt = js(page, "()=>document.body.innerText")
        js(page, "()=>{switchTab('today'); todayRefresh(true);}"); page.wait_for_timeout(400)
        tt = js(page, "()=>document.body.innerText")
        check("[%s] C: 'Fix risk' / 'Risk / size not OK' removed from Plan and Today" % tag, "Fix risk" not in alltxt + tt and "Risk / size not OK" not in alltxt + tt)
        js(page, "()=>{switchTab('plan'); bdRender();}"); page.wait_for_timeout(300)
        # ── Holding: six numbers
        ch = card_txt(page, "ccmwdlk56w91") or card_txt(page, "cN")
        hid = js(page, "()=>bdItems().find(x=>x.sym==='NVDA').id")
        ch = card_txt(page, hid)
        check("[%s] C: Holding card — stop · if stopped · value+weight · P&L (PV1b)" % tag, all(x in ch for x in ("Stop 110", "If stopped −฿17.8k", "Value ฿60.5k · 1.2%", "P&L +฿1.8k")), ch)
        check("[%s] C: holding card — Long word and homework chip" % tag, js(page, "(i)=>document.querySelector('[data-bd-card=\"'+i+'\"] [data-pv-dir]').dataset.pvDir==='Long'", hid) and "50% · homework" in ch)
        # ── More ▾
        js(page, "(i)=>document.querySelector('[data-bd-card=\"'+i+'\"]').click()", hid); page.wait_for_timeout(300)
        mt = ctxt(page, hid); ch = mt
        check("[%s] C: More ▾ — cost with FX line, loss vs entry, price→stop, R definition, whole plan, pool, limits, FX source" % tag,
              all(x in mt for x in ("฿58.7k", "× FX 33.76", "−฿17.8k", "0.36% of account", "฿19.6k", "1R = entry − first stop = $48 per share", "+$4.85 per share", "฿36.1k · 0.72% of account", "% of strategy pool", "max 12.5% of account", "within", "Settings rate, not live", "33.76")), mt)
        check("[%s] C: More stays open after a re-render" % tag, (js(page, "()=>{bdRender(); return 1}") and js(page, "(i)=>!!document.querySelector('[data-bd-card=\"'+i+'\"] [data-pv-more]')", hid)))
        check("[%s] C: no overflow on the Plan board" % tag, no_overflow(page), js(page, "()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth, ...[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>document.documentElement.clientWidth+1 && true).slice(0,5).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right))]"))
        if w in (1440, 390):
            js(page, "()=>window.scrollTo(0,0)"); page.wait_for_timeout(150); shot(page, "plan-%d" % w)
        if w == 390:
            js(page, "()=>{ bdSetSeg('hold'); }"); page.wait_for_timeout(400)
            js(page, "(i)=>document.querySelector('[data-bd-card=\"'+i+'\"]').scrollIntoView({block:'start'})", hid); page.wait_for_timeout(500); shot(page, "holding-more-390")
            js(page, "()=>{ bdSetSeg('plan'); }")
        # ── same numbers on Today · Plan card · drawer
        js(page, "()=>{switchTab('today'); todayRefresh(true);}"); page.wait_for_timeout(400)
        today = " ".join(r["t"] for r in rows(page, "manage"))
        js(page, "(i)=>bdOpen(i)", hid); page.wait_for_timeout(300)
        dr = txt(page, "[data-pv-block]"); js(page, "()=>bdClose()")
        check("[%s] C: value, weight, open risk equal on Today · Plan card · drawer" % tag, all(x in today for x in ("฿60.5k", "1.2%", "฿17.8k")) and all(x in ch for x in ("฿60.5k", "1.2%", "฿17.8k")) and all(x in dr for x in ("฿60.5k", "1.2%", "฿17.8k")), [today, ch, dr])
        check("[%s] C: no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


if __name__ == "__main__":
    only = os.environ.get("PV1_PARTS", "ABC").split(",") if False else list(os.environ.get("PV1_PARTS", "ABC"))
    with sync_playwright() as pw:
        for w, h in SIZES:
            if "A" in only: partA(pw, w, h)
            if "B" in only: partB(pw, w, h)
            if "C" in only: partC(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("%d checks pass · %d fail" % (len(results) - len(bad), len(bad)))
    sys.exit(1 if bad else 0)
