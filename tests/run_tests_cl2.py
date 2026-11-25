#!/usr/bin/env python3
"""CL2 — English everywhere the user looks · no browser pop-ups in the trade flows · accurate limit wording.
A  no visible Thai on any crawled screen / sheet (the permanent assertion lives in run_tests_e2e1.py: CRAWL + THAI journeys; this suite runs the THAI journey too)
B  Filled → entry-price sheet (prefilled · Enter saves · Esc cancels · invalid = ⚠) · confirm sheets (Enter = confirm · Esc = cancel) · spy: window.prompt/alert/confirm never called in the trade flows
C  limit wording (Add-on · plan · over-limit fill) · Add stocks sheet: one dark button, selected strategy = white segment on grey
Run: python3 tests/run_tests_cl2.py   (CL2_SHOTS=1 writes docs/screenshots/cl2-*.png · docs/briefs/CL2-brief.md)"""
import sys, os, re
from playwright.sync_api import sync_playwright
from e2e1_common import *
import e2e1_common as E
import run_tests_e2e1 as R
from re1d_common import check, results

SH = bool(os.environ.get("CL2_SHOTS"))
SPY = """()=>{ window.__dlg = []; window.prompt = ()=>{ window.__dlg.push('prompt'); return null; }; window.confirm = ()=>{ window.__dlg.push('confirm'); return false; }; window.alert = ()=>{ window.__dlg.push('alert'); }; }"""
DLG = "()=>window.__dlg.slice()"


def png(page, name):
    if SH: page.screenshot(path=os.path.join(E.SHOTS, name + ".png"))


def sheet_open(page): return js(page, "()=>!!document.querySelector('.core-sheet')")


def trade_state(page, id, acct="main"): return R.trade_of(page, id, acct)


def part_b(pw, w):
    b, page, ce, pe = start(pw, w); page.set_default_timeout(6000); tag = "[B %d]" % w
    try:
        js(page, SPY)
        # a full Sat loop with real clicks: plan → place → Filled (price sheet) → Move stop → partial exit → close
        ok = new_sat_plan(page, w, "CL2", 0, False, "main", 2643, 2660, 2600); ok &= R.save_plan(page, "CL2"); id = R.newest_idea(page, "XAUUSD")
        place_from_today(page, "XAU", "CL2")
        ok &= click(page, enter_btn(page, "XAU", "check"), "XAU Check row · Filled", "CL2")[0]; page.wait_for_timeout(300)
        px = js(page, "()=>(document.getElementById('cl2FillPx')||{}).value")
        check(f"{tag} Filled opens the entry-price sheet (not a browser prompt), prefilled with the planned entry", sheet_open(page) and px == "2643", px)
        if w == 390: png(page, "cl2-fill-price")
        page.keyboard.press("Escape"); page.wait_for_timeout(250)
        st = trade_state(page, id)
        check(f"{tag} Esc cancels: sheet closes, the order stays 'plan', nothing recorded", not sheet_open(page) and st and st["status"] == "plan", st)
        ok = click(page, enter_btn(page, "XAU", "check"), "XAU Check row · Filled again", "CL2")[0]; page.wait_for_timeout(300)
        page.locator("#cl2FillPx").fill("abc"); page.wait_for_timeout(150)
        er = js(page, "()=>{ const e=document.getElementById('csErr'); return e && e.style.display!=='none' ? e.textContent : ''; }"); dis = js(page, "()=>document.getElementById('csSave').disabled")
        check(f"{tag} a bad price shows a ⚠ line that says the fix, Save is off", er.startswith("⚠ Type the price you got") and dis is True, [er, dis])
        page.locator("#cl2FillPx").fill("2641.5"); page.wait_for_timeout(100); page.keyboard.press("Enter"); page.wait_for_timeout(500)
        st = trade_state(page, id)
        check(f"{tag} Enter saves: the trade is open at the typed price 2,641.5", st and st["status"] == "open" and abs(st["entry"] - 2641.5) < 1e-9 and not sheet_open(page), st)
        ok2, err = move_stop_ui(page, "XAU", 2650, "CL2")
        ok3 = close_ui(page, "XAU", 2621.5, "CL2", 0.5)
        st = trade_state(page, id)
        check(f"{tag} Move stop and partial exit worked by clicks only", ok2 and ok3 and st and st["sl"] == 2650 and st["status"] == "open", [err, st])
        ok4 = close_ui(page, "XAU", 2610, "CL2")
        # second plan: mouse path of the Filled sheet (Save button), default price kept
        ok = new_sat_plan(page, w, "CL2", 1, True, "main", 90000, 88500, 94000); ok &= R.save_plan(page, "CL2"); id2 = R.newest_idea(page, "BTCUSD")
        place_from_today(page, "BTC", "CL2")
        click(page, enter_btn(page, "BTC", "check"), "BTC Filled", "CL2"); page.wait_for_timeout(300)
        okc = click(page, "[data-cl2-fillsave]", "Filled · Save (mouse)", "CL2")[0]; page.wait_for_timeout(400)
        st = trade_state(page, id2)
        check(f"{tag} mouse: Save with the prefilled planned entry opens the trade at 90,000", okc and st and st["status"] == "open" and st["entry"] == 90000, st)
        # confirm sheets
        t1 = js(page, "()=>{ const i=sat7dIdea(arguments[0]); return 0; }") if False else None
        tid = js(page, "(id)=>{ const i=sat7dIdea(id); const s=(i.accts||{}).main; return s&&s.trade_id; }", id2)
        js(page, "([t])=>{ const B=getBook('main'); const x=B.trades.find(a=>a.id===t); x.status='cancelled'; }", [tid])
        js(page, "([t])=>restoreCancelled(t,'main')", [tid]); page.wait_for_timeout(250)
        body = js(page, "()=>(document.querySelector('.core-sheet h3')||{innerText:''}).innerText")
        check(f"{tag} Move back to Plan asks in an in-app sheet (no browser confirm)", sheet_open(page) and js(page, "()=>!!document.querySelector('[data-cl2-yes]')") and "back to Plan" in body, body)
        page.keyboard.press("Escape"); page.wait_for_timeout(200)
        check(f"{tag} Esc on the confirm sheet cancels (trade still cancelled)", not sheet_open(page) and js(page, "([t])=>getBook('main').trades.find(a=>a.id===t).status", [tid]) == "cancelled")
        js(page, "([t])=>restoreCancelled(t,'main')", [tid]); page.wait_for_timeout(250); page.keyboard.press("Enter"); page.wait_for_timeout(300)
        check(f"{tag} Enter confirms (trade back to plan)", js(page, "([t])=>getBook('main').trades.find(a=>a.id===t).status", [tid]) == "plan" and not sheet_open(page))
        js(page, "([t])=>delTrade(t,'main')", [tid]); page.wait_for_timeout(250)
        check(f"{tag} Delete trade asks in an in-app sheet", sheet_open(page) and js(page, "()=>!!document.querySelector('[data-cl2-yes]')"))
        click(page, "[data-cl2-yes]", "Delete · Confirm (mouse)", "CL2"); page.wait_for_timeout(300)
        check(f"{tag} mouse Confirm deletes the trade", js(page, "([t])=>!getBook('main').trades.some(a=>a.id===t)", [tid]))
        d = js(page, DLG)
        check(f"{tag} no window.prompt / alert / confirm was called in any of these flows", d == [], d)
        check(f"{tag} no console / page errors", not ce and not pe, (ce + pe)[:2])
    finally:
        b.close()


def part_hw(pw, w):
    import hw1_common as HW
    b, page, pe = HW.open_hw(pw, w, 900 if w >= 900 else 844); page.set_default_timeout(6000); tag = "[B-Homework %d]" % w
    try:
        js(page, E.INSTALL); js(page, SPY)
        HW.go(page, "AAPL", "winner")
        js(page, "()=>{ window.__wd = wlMtDirty; wlMtDirty = ()=>true; }")
        js(page, "()=>hwBack()"); page.wait_for_timeout(250)
        check(f"{tag} Homework leave with unsaved changes → in-app sheet (Leave / Stay), the page does not leave yet", sheet_open(page) and js(page, "()=>!!hwSym") and js(page, "()=>(document.querySelector('[data-cl2-yes]')||{innerText:''}).innerText") == "Leave", js(page, "()=>hwSym"))
        page.keyboard.press("Escape"); page.wait_for_timeout(200)
        check(f"{tag} Esc stays on Homework", not sheet_open(page) and js(page, "()=>!!hwSym"))
        js(page, "()=>hwBack()"); page.wait_for_timeout(250); page.keyboard.press("Enter"); page.wait_for_timeout(350)
        check(f"{tag} Enter leaves Homework", js(page, "()=>!hwSym"))
        HW.go(page, "AAPL", "winner"); js(page, "()=>{ wlMtDirty = ()=>true; }"); js(page, "()=>hwBack()"); page.wait_for_timeout(250)
        click(page, "[data-cl2-yes]", "Leave (mouse)", "CL2"); page.wait_for_timeout(300)
        check(f"{tag} mouse Leave works", js(page, "()=>!hwSym"))
        d = js(page, DLG)
        check(f"{tag} no window.prompt / alert / confirm called", d == [], d)
    finally:
        b.close()


def part_c(pw, w):
    tag = "[C %d]" % w
    if w == 1440:   # Add-on blocked wording (the real Core Family journey up to the block)
        b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
        try:
            import run_tests_phase374 as P4
            click(page, "#hdrPlanBtn", "＋ New plan", "CL2"); click(page, "#bdPop [onclick=\"lrNewAcct('fam')\"]", "Family", "CL2"); click(page, "#bdPop [onclick=\"bdNewPick('D')\"]", "Compounder", "CL2"); page.wait_for_timeout(500)
            click(page, ".core-sheet button:has-text('TH · THB')", "TH market", "CL2")
            page.locator("#cnTicker").fill("CPALL"); page.locator("#cnEntry").fill("60"); page.locator("#cnStop").fill("55"); page.wait_for_timeout(500)
            click(page, "[onclick*=coreNewSave]", "Save plan", "CL2"); page.wait_for_timeout(900)
            js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
            place_from_today(page, "CPALL.BK", "CL2")
            click(page, enter_btn(page, "CPALL.BK", "check"), "Pilot Filled", "CL2"); page.wait_for_timeout(500)
            click(page, "[onclick*=coreBuy1Save]", "Save buy", "CL2"); page.wait_for_timeout(700)
            P4.put_wl(page, {"CPALL.BK": P4.wl_doc("CPALL.BK", exit_="e", why="w", trigger="t", confirmed=True)})
            js(page, "()=>{ coreWrite(coreCardsList.find(x=>x.ticker==='CPALL.BK').id, {px:60, pxDate:thaiToday()}); re1Cache={}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)
            click(page, "[onclick=\"acctSwitch('fam')\"]", "Family", "CL2"); js(page, "()=>{ switchTab('today'); re1Cache={}; todayRefresh(true); }"); page.wait_for_timeout(500)
            row = sel_text(page, '[data-re2-row="CPALL.BK"][data-re2-grp="manage"]') or ""
            check(f"{tag} Add-on blocked row says 'Risk 1% is over the 1% limit for this stock (all lots at their current stop)'", re.search(r"Risk \d+(\.\d+)?% is over the 1% limit for this stock \(all lots at their current stop\)", row) is not None and "today's limit" not in row, row)
            png(page, "cl2-addon-blocked")
        finally:
            b.close()
    # the plan-total wording + over-limit fill wording live in the engine / Today code: assert the page really carries them
    b, page, ce, pe = start(pw, w)
    try:
        src = js(page, "()=>[document.documentElement.innerHTML.includes('is over the limit for this plan '), document.documentElement.innerHTML.includes('Over the limit for this plan: '), document.documentElement.innerHTML.includes(\"is over today's limit\"), document.documentElement.innerHTML.includes(\"Over today's limit\")]")
        check(f"{tag} PLAN_TOTAL_RISK says 'over the limit for this plan' (numbers kept) · over-limit fill says 'Over the limit for this plan:' · no 'today's limit' left in those texts", src == [True, True, False, False], src)
        # Add stocks sheet
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); wl1ImpOpen(); wl1ImpIn('NVDA, AAPL'); }"); page.wait_for_timeout(500)
        r = js(page, """()=>{ const box=document.querySelector('[data-wl1-imp]'); const lum=c=>{ const m=c.match(/[\\d.]+/g)||[0,0,0]; return (0.2126*m[0]+0.7152*m[1]+0.0722*m[2])/255; };
          const btns=[...box.querySelectorAll('button')].filter(x=>x.getClientRects().length); const dark=btns.filter(x=>{ const bg=getComputedStyle(x).backgroundColor; const a=(bg.match(/[\\d.]+/g)||[]); return (a.length<4||+a[3]>0.5) && lum(bg)<0.3; }).map(x=>x.innerText.trim());
          const sel=box.querySelector('.wl1-seg button.on'); return {dark, sel:sel?getComputedStyle(sel).backgroundColor:null, wrap:getComputedStyle(box.querySelector('.wl1-seg')).backgroundColor, add:(document.getElementById('wl1ImpAdd')||{}).disabled}; }""")
        check(f"{tag} Add stocks sheet: exactly one dark button (Add) · the selected strategy is a white segment on grey", len(r["dark"]) == 1 and r["dark"][0].startswith("Add") and r["sel"] == "rgb(255, 255, 255)" and r["wrap"] != "rgb(255, 255, 255)", r)
        if w == 390: png(page, "cl2-add-stocks")
    finally:
        b.close()
    if w == 390:   # the weekly close price sheet (Core) in English
        b, page, ce, pe = R.crawl_seed(pw, w)
        try:
            js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); corePxOpen('xAAA'); }"); page.wait_for_timeout(400)
            t = js(page, "()=>(document.querySelector('.core-sheet')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
            check(f"{tag} weekly close price sheet is English ('Weekly close price · AAA', Close price, Date (last Friday), Cancel, Save)", "Weekly close price · AAA" in t and "Close price" in t and "Date (last Friday)" in t and "Cancel" in t and "Save" in t and not re.search(r"[฀-฾เ-๿]", t), t[:200])
            png(page, "cl2-weekly-close")
        finally:
            b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w in (1440, 390):
            for fn in (part_b, part_hw, part_c):
                try: fn(pw, w)
                except Exception as e:
                    check(f"[{fn.__name__} {w}] crashed: {str(e)[:160]}", False, str(e)[:500])
            try: R.j_thai(pw, w)
            except Exception as e: check(f"[THAI {w}] crashed: {str(e)[:160]}", False, str(e)[:500])
    check("no dead buttons / click-handler errors in the CL2 clicks", not E.DEAD, E.DEAD[:8])
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY cl2: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
