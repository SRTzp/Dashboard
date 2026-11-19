#!/usr/bin/env python3
"""SD1 — wrong-side guard: Sat form (inline 'Switch to X ›', Save off) · Blocked rows (Today Act, Plan board, drawer, Place sheet) with a one-tap fix ·
stored plans never change without the tap · Core form still blocks Entry <= SL.  Run: python3 tests/run_tests_sd1.py"""
import sys
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import run_tests_lrf as LF

IDEA = """(o)=>{ sat7dWrite('satIdeas','sdX',Object.assign({id:'sdX',v3:true,v2:true,asset:'XAUUSD',entry:2643,ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],ready:true,readyAt:new Date().toISOString()}, o));
  (satIdeasList||[]).forEach(i=>{ if(i && i.id==='sdX') Object.assign(i,o); }); re1Cache = {}; re2GrpAll = {enter:true, check:true, manage:true}; todayRefresh(true); try{ bdRender(); }catch(e){} }"""


def rowinfo(page):
    return js(page, "()=>{ const r = document.querySelector('.re2-row[data-re2-row=\"XAU\"]'); if(!r) return null; const b = r.querySelector('[data-sd-fix]'); const l = r.querySelector('.lrf-blkline'); return {chip: (r.querySelector('[data-re2-chip-st]')||{}).innerText, line: l ? l.innerText.replace(/\\s+/g,' ').trim() : '', btn: b ? b.innerText.trim() : null}; }")


def sat_case(pw, w, h, bias, sl, tp, want_to, want_line):
    tag = "[%s %s]" % (w, bias)
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        LF.today(page)
        js(page, IDEA, {"bias": bias, "sl": sl, "tp": tp}); page.wait_for_timeout(500)
        before = js(page, "()=>sat7dIdea('sdX').bias")
        r = rowinfo(page)
        check(f"{tag} Today row Blocked: '{want_line}' + 'Switch to {want_to} ›'", r and r["chip"] == "Blocked" and r["line"].startswith("Blocked · " + want_line) and r["btn"] == f"Switch to {want_to} ›", r)
        check(f"{tag} stored plan unchanged before the tap", before == bias, before)
        card = js(page, "()=>{ switchTab('plan'); bdRender(); const c = document.querySelector('[data-bd-card=\"sdX\"]'); return c ? {t: c.innerText.replace(/\\s+/g,' '), f: !!c.querySelector('[data-pv-fixbtn=\"side\"]')} : null; }")
        check(f"{tag} Plan board card: Blocked + fix button", card and want_line in card["t"] and "Blocked" in card["t"] and card["f"], card)
        dr = js(page, "()=>{ bdOpen('sdX'); const d = document.querySelector('.bd-df [data-sd-fix]'); return {btn: d ? d.innerText.trim() : null, dis: d ? d.disabled : null, txt: document.body.innerText.includes('" + want_line + "')}; }")
        check(f"{tag} drawer: enabled fix button + reason", dr and dr["btn"] == f"Switch to {want_to} ›" and dr["dis"] is False and dr["txt"], dr)
        js(page, "()=>{ bdClose(); pb2PlaceOpen('sdX'); }"); page.wait_for_timeout(300)
        sh = js(page, "()=>{ const s = document.querySelector('[data-sd-banner]'); const y = document.querySelector('[data-pb2-yes]'); return {b: s ? s.innerText.replace(/\\s+/g,' ') : null, yes: y ? y.disabled : null}; }")
        check(f"{tag} Place order sheet: Blocked banner + Confirm disabled", sh and sh["b"] and want_line in sh["b"] and sh["yes"] is True, sh)
        js(page, "()=>document.querySelector('[data-sd-banner] [data-sd-fix]').click()"); page.wait_for_timeout(500)
        after = js(page, "()=>({bias: sat7dIdea('sdX').bias, banner: !!document.querySelector('[data-sd-banner]'), yes: (document.querySelector('[data-pb2-yes]')||{}).disabled})")
        check(f"{tag} tap flips to {want_to}, levels kept, banner gone, Place now enabled", after["bias"] == want_to and not after["banner"] and after["yes"] is False, after)
        keep = js(page, "()=>{ const i = sat7dIdea('sdX'); return [i.entry, i.sl, i.tp]; }")
        check(f"{tag} numbers kept", keep == [2643, sl, tp], keep)
        js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(500)
        pl = js(page, "()=>{ const i = bdById('sdX'); return i ? i.status : null; }")
        check(f"{tag} Place works after the switch (plan is now Ordered)", pl == "ord", pl)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def form(pw, w, h):
    tag = "[%s form]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        js(page, "()=>{ pb2OpenAsset('XAUUSD', {direct:true}); }"); page.wait_for_timeout(400)
        def fill(e, s, t):
            for k, v in (("entry", e), ("sl", s), ("tp", t)):
                js(page, "([k,v])=>{ const i = document.querySelector('[data-pb2-in=\"'+k+'\"]'); i.value = v; pb2In(k, v); }", [k, v])
        js(page, "()=>pb2Set_dir('Buy')")   # manual pick wins over auto
        fill("2643", "2660", "2600")   # Buy with SL above entry
        st = js(page, "()=>({m: (document.querySelector('[data-pb2-side]')||{}).innerText, s: document.querySelector('[data-pb2-save]').disabled, d: document.querySelector('[data-pb2-draft]').disabled})")
        check(f"{tag} Buy + SL above entry: red line 'look like a Short' + Save off", st["m"] and "These levels look like a Short · Switch to Short ›" in st["m"] and st["s"] and not st["d"], st)
        js(page, "()=>document.querySelector('[data-sd-switch]').click()"); page.wait_for_timeout(300)
        st = js(page, "()=>({dir: pb2.dir, line: !!document.querySelector('[data-pb2-side]'), s: document.querySelector('[data-pb2-save]').disabled, v: [pb2.entry, pb2.sl, pb2.tp]})")
        check(f"{tag} switch -> Sell, numbers kept, line gone, Save on", st["dir"] == "Sell" and not st["line"] and not st["s"] and st["v"] == ["2643", "2660", "2600"], st)
        js(page, "()=>pb2Set_dir('Buy')"); page.wait_for_timeout(200)
        fill("2643", "2620", "2700"); js(page, "()=>pb2Set_dir('Sell')"); page.wait_for_timeout(200)
        st = js(page, "()=>({m: (document.querySelector('[data-pb2-side]')||{}).innerText, s: document.querySelector('[data-pb2-save]').disabled})")
        check(f"{tag} Sell + SL below entry: line says 'look like a Long' + Save off", st["m"] and "These levels look like a Long · Switch to Long ›" in st["m"] and st["s"], st)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def auto(pw, w, h):
    tag = "[%s auto]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        js(page, "()=>{ pb2OpenAsset('XAUUSD', {direct:true}); }"); page.wait_for_timeout(400)
        def fill(k, v): js(page, "([k,v])=>{ const i = document.querySelector('[data-pb2-in=\"'+k+'\"]'); i.value = v; pb2In(k, v); }", [k, v])
        fill("entry", "2643"); st = js(page, "()=>({d: pb2.dir, a: !!document.querySelector('[data-pb2-auto]')})")
        check(f"{tag} entry only: no auto yet", st["d"] == "Buy" and not st["a"], st)
        fill("sl", "2660"); st = js(page, "()=>({d: pb2.dir, a: !!document.querySelector('[data-pb2-auto]'), w: !!document.querySelector('[data-pb2-side]')})")
        check(f"{tag} SL > entry -> Sell + 'auto' tag, no wrong-side line", st["d"] == "Sell" and st["a"] and not st["w"], st)
        fill("sl", "2620"); st = js(page, "()=>({d: pb2.dir, a: !!document.querySelector('[data-pb2-auto]')})")
        check(f"{tag} SL < entry -> Buy (auto follows the numbers)", st["d"] == "Buy" and st["a"], st)
        js(page, "()=>pb2Set_dir('Sell')"); fill("tp", "2700"); st = js(page, "()=>({d: pb2.dir, a: !!document.querySelector('[data-pb2-auto]'), m: (document.querySelector('[data-pb2-side]')||{}).innerText, s: document.querySelector('[data-pb2-save]').disabled})")
        check(f"{tag} manual Sell wins: auto tag gone, contradiction -> switch line, Save plan off", st["d"] == "Sell" and not st["a"] and "Switch to Long" in (st["m"] or "") and st["s"], st)
        fill("sl", "2600"); st = js(page, "()=>pb2.dir")
        check(f"{tag} manual pick is not overridden by later edits", st == "Sell", st)
        js(page, "()=>pb2Save(true)"); page.wait_for_timeout(500)
        r = js(page, "()=>{ const i = (satIdeasList||[]).find(x=>x && x.asset === 'XAUUSD' && x.pb2); return i ? {w: i.wrongSide, bias: i.bias} : null; }")
        check(f"{tag} draft saves with the wrong side, flagged wrongSide:true", r and r["w"] is True and r["bias"] == "Short", r)
        LF.today(page); js(page, "()=>{ re2GrpAll = {enter:true, check:true, manage:true}; todayRefresh(true); }"); page.wait_for_timeout(400)
        rows = js(page, "()=>!!document.querySelector('.re2-row[data-re2-row=\"XAU\"]')")
        check(f"{tag} flagged draft is not on Today", rows is False, rows)
        pl = js(page, "()=>{ const i = (satIdeasList||[]).find(x=>x && x.asset === 'XAUUSD' && x.pb2); pb2PlaceOpen(i.id); return !!document.querySelector('[data-pb2-step=\"place\"]'); }")
        check(f"{tag} flagged draft cannot open Place", pl is False, pl)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def core(pw, w, h):
    tag = "[%s core]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        js(page, "()=>{ planScope='stock'; coreNewOpen('main'); }"); page.wait_for_timeout(500)
        js(page, "()=>{ const t=document.getElementById('cnTicker'); t.value='AAPL'; document.getElementById('cnEntry').value='80'; document.getElementById('cnStop').value='90'; coreNewIn(); }"); page.wait_for_timeout(300)
        t = js(page, "()=>{ const f = document.getElementById('cnFerr_stop'); return f ? f.innerText : ''; }")
        check(f"{tag} Core form still blocks Entry <= SL ('Entry must be above SL')", "Entry must be above" in t, t)
    finally:
        b.close()


def stored(pw, w, h):
    tag = "[%s stored]" % w
    b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
    try:
        LF.today(page)
        js(page, IDEA, {"bias": "Long", "sl": 2660, "tp": 2600}); page.wait_for_timeout(300)
        js(page, "()=>location.reload && 0"); 
        r = js(page, "()=>[sat7dIdea('sdX').bias, sat7dIdea('sdX').sl]")
        check(f"{tag} existing wrong-side plan shows Blocked on load and nothing auto-changed", rowinfo(page)["chip"] == "Blocked" and r == ["Long", 2660], r)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            sat_case(pw, w, h, "Long", 2660, 2600, "Short", "Wrong side: SL above entry for Long")
            sat_case(pw, w, h, "Short", 2620, 2700, "Long", "Wrong side: SL below entry for Short")
            form(pw, w, h); auto(pw, w, h); stored(pw, w, h)
        core(pw, 1440, 900)
    bad = [r for r in results if not r[1]]
    print("SUMMARY sd1: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
