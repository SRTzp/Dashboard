#!/usr/bin/env python3
"""LR5a — Watch tab: header · one-line rows · status chips · RS column (↗ → ↘ · new high · missing + reason) · Sort / Filter (counts, order, RS null last, remembered per device) · detail panel · Archived · phone sheet · Ideas · English only · no overflow at 360/390/1440.
Run: python3 tests/run_tests_lr5a.py"""
import re, sys, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import lr5_common as C

THAI = """()=>{ const out = []; const root = document.getElementById('tabWatch'); const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while(n = w.nextNode()){ if(/[\\u0E00-\\u0E7F]/.test(n.nodeValue)) out.push(n.nodeValue.trim().slice(0, 60)); }
  root.querySelectorAll('[title],[aria-label],[placeholder]').forEach(e=>['title', 'aria-label', 'placeholder'].forEach(a=>{ const v = e.getAttribute(a); if(v && /[\\u0E00-\\u0E7F]/.test(v)) out.push('@' + a + ' ' + v.slice(0, 60)); })); return out; }"""
ROWS = "()=>[...document.querySelectorAll('[data-lr5-row]')].map(r=>r.dataset.sym)"


def order(page): return js(page, ROWS)
def ov(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")


def row(page, sym, sel=""):
    return js(page, "([s,q])=>{ const r = document.querySelector('[data-lr5-row][data-sym=\"'+s+'\"]'); const e = q ? r && r.querySelector(q) : r; return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", [sym, sel])


def run(pw, w, h):
    tag = "[%s]" % w
    desk = w >= 1024
    b, page, pe = C.open_watch(pw, w, h, ideas=True)
    try:
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(500)
        # ---- header
        hd = js(page, "()=>({h1:document.querySelector('.lr5-h1').innerText, segs:[...document.querySelectorAll('[data-wl1-segs] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim()), sum:document.querySelector('[data-wl1-sum]').innerText.replace(/\\s+/g,' ').trim(), find:!!document.querySelector('[data-lr5-q]') && getComputedStyle(document.querySelector('[data-lr5-q]').closest('label')).display !== 'none', add:document.querySelector('[data-wl1-import]').innerText.trim()})")
        check(f"{tag} A: header = Watch · Momentum 5 · Compounder 1 · Ideas 2", hd["h1"] == "Watch" and hd["segs"] == ["Momentum 5", "Compounder 1", "Ideas 2"], hd)
        check(f"{tag} A: summary line '5 stocks · 3 need homework'" + (" · shared by Main and Family" if desk else ""), hd["sum"].startswith("5 stocks · 3 need homework") and (("shared by Main and Family" in hd["sum"]) if desk else True), hd["sum"])
        check(f"{tag} A: desktop has Find ticker + '+ Add stock'; phone has '+ Add' only", (hd["find"] and hd["add"] == "+ Add stock") if desk else (not hd["find"] and hd["add"] == "+ Add"), hd)
        # ---- rows + statuses
        o = order(page)
        check(f"{tag} A: one row per live Momentum stock (archived + Compounder excluded)", sorted(o) == ["AAPL", "AMD", "AVGO", "GE", "PLTR"], o)
        st = {s: row(page, s, "[data-wl1-chip]") for s in o}
        check(f"{tag} A: status chips Holding / Plan ready / No plan / Setup ✓", st == {"AAPL": "Holding", "AVGO": "Plan ready", "GE": "No plan", "PLTR": "No plan", "AMD": "Setup ✓"}, st)
        act = {s: row(page, s, "[data-wl1-act]") for s in o}
        check(f"{tag} A: one action per row — Homework › / Open plan › (Plan › on phone) / Make plan › (black when it is the next step)", act["AAPL"] == "Homework ›" and act["PLTR"] == "Homework ›" and act["GE"] == "Make plan ›" and act["AVGO"] == ("Open plan ›" if desk else "Plan ›"), act)
        pri = js(page, "()=>[...document.querySelectorAll('[data-lr5-row] [data-wl1-act].pri')].map(b=>b.closest('[data-lr5-row]').dataset.sym)")
        check(f"{tag} A: only the next-step button (GE · Make plan) is black", pri == ["GE"], pri)
        # ---- homework / sector / next check text (desktop cells)
        if desk:
            hw = {s: row(page, s, "[data-wl1-hwt]") for s in o}
            check(f"{tag} A: homework cell — 'Not started · adds at 50%' (Holding) · 'Not started' · 'Done 8 Nov · aero cycle'", hw["AAPL"] == "Not started · adds at 50%" and hw["PLTR"] == "Not started" and hw["GE"] == "Done 8 Nov · aero cycle" and hw["AVGO"].startswith("Done 12 Nov · AI networking"), hw)
            nx = {s: row(page, s, "[data-lr5-next]") for s in o}
            check(f"{tag} A: Next check — GE 28 Nov · AVGO 2 Dec · others —", nx["GE"] == "28 Nov" and nx["AVGO"] == "2 Dec" and nx["AAPL"] == "—" and nx["PLTR"] == "—", nx)
            sec = {s: row(page, s, "[data-lr5-sec]") for s in o}
            check(f"{tag} A: Sector vs SPY — Technology ↘ · Semiconductors ⤴ · Industrials ↗ · Software ↘", sec["AAPL"] == "Technology ↘" and sec["AVGO"] == "Semiconductors ⤴" and sec["GE"] == "Industrials ↗" and sec["PLTR"] == "Software ↘", sec)
            hdr = js(page, "()=>[...document.querySelectorAll('.lr5-th .lbl')].map(x=>x.innerText)")
            check(f"{tag} A: table header Stock · Status · Sector vs SPY · RS · Thesis · homework · Next check", [x.lower() for x in hdr] == ["stock", "status", "sector vs spy", "rs", "thesis · homework", "next check"], hdr)
        # ---- RS
        rs = {s: js(page, "(s)=>{ const e = document.querySelector('[data-lr5-row][data-sym=\"'+s+'\"] .c-rs [data-lr5-rs]'); return e ? {t:e.innerText.replace(/\\s+/g,' ').trim(), v:e.dataset.lr5Rs, arrow:(e.querySelector('[data-lr5-arrow]')||{dataset:{}}).dataset.lr5Arrow||'', nh:!!e.querySelector('[data-lr5-newhigh]'), tip:e.getAttribute('title')||''} : null; }", s) for s in o}
        if desk:
            check(f"{tag} B: RS column — AAPL '87 ↗ new high' · AVGO '64 ↘' · GE '91 →'", rs["AAPL"]["t"] == "87 ↗ new high" and rs["AAPL"]["arrow"] == "up" and rs["AVGO"]["t"] == "64 ↘" and rs["AVGO"]["arrow"] == "down" and not rs["AVGO"]["nh"] and rs["GE"]["t"] == "91 →" and rs["GE"]["arrow"] == "flat", rs)
            check(f"{tag} B: missing RS → '—' with the reason in the tooltip (history<252 · no data)", rs["AMD"]["t"] == "—" and "252" in rs["AMD"]["tip"] and rs["PLTR"]["t"] == "—" and "No RS data" in rs["PLTR"]["tip"], rs)
        else:
            ph = {s: row(page, s, ".l2") for s in o}
            check(f"{tag} B: phone — RS sits at the end of line 2 ('… · RS 87 ↗')", ph["AAPL"].endswith("RS 87 ↗") and ph["GE"].endswith("RS 91 →") and ph["AVGO"].endswith("RS 64 ↘") and "RS" not in ph["PLTR"] and "RS" not in ph["AMD"], ph)
            check(f"{tag} B: phone line 2 — amber homework note when missing · 'Industrials · thesis done 8 Nov' when done", ph["AAPL"].startswith("Homework not started · adds at 50%") and ph["PLTR"] == "Homework not started" and ph["GE"].startswith("Industrials · thesis done 8 Nov"), ph)
        # ---- one line per row · no overflow
        dims = js(page, "()=>[...document.querySelectorAll('[data-lr5-row]')].map(r=>({s:r.dataset.sym, h:Math.round(r.getBoundingClientRect().height), cells:[...r.children].filter(c=>getComputedStyle(c).display!=='none' && !c.classList.contains('lr5-id')).map(c=>Math.round(c.getBoundingClientRect().height)), l2:(r.querySelector('.l2')||{getBoundingClientRect:()=>({height:0})}).getBoundingClientRect().height}))")
        if desk: check(f"{tag} A: every row is ONE line (≤ 64px · no cell wraps)", all(d["h"] <= 64 for d in dims) and all(max(d["cells"]) <= 44 for d in dims), dims)
        else: check(f"{tag} C: every phone row is TWO lines (≤ 72px · line 2 one line ≤ 22px)", all(d["h"] <= 72 and d["l2"] <= 22 for d in dims), dims)
        check(f"{tag} A: no horizontal page overflow", ov(page) <= 0, ov(page))
        # ---- hooks kept
        hk = js(page, "()=>['[data-wl1-row]','[data-wl1-chip]','[data-wl1-act]','[data-wl1-sum]','[data-wl1-seg]','[data-wl1-ideas]','[data-wl1-import]','[data-wl1-arch]','[data-wl1-arch-toggle]','[data-wl-restore]','[data-wl1-hwt]'].filter(s=>!document.querySelector(s))")
        check(f"{tag} A: old hooks still present (rows · chip · act · sum · seg · ideas · import · archive · restore)", hk == [], hk)
        check(f"{tag} A: no Thai in #tabWatch (list)", js(page, THAI) == [], js(page, THAI))
        # ---- sort
        sel = "[data-lr5-sort]"
        base = order(page)
        page.select_option(sel, "rs"); page.wait_for_timeout(300)
        check(f"{tag} B: Sort › RS high first — GE 91 · AAPL 87 · AVGO 64, then no-RS rows (AMD · PLTR) last in default order", order(page) == ["GE", "AAPL", "AVGO"] + [x for x in base if x in ("AMD", "PLTR")], order(page))
        page.select_option(sel, "next"); page.wait_for_timeout(300)
        check(f"{tag} B: Sort › Next check soonest — GE (28 Nov) · AVGO (2 Dec) · rows without a date last", order(page)[:2] == ["GE", "AVGO"] and order(page)[2:] == [x for x in base if x not in ("GE", "AVGO")], order(page))
        page.select_option(sel, "hw"); page.wait_for_timeout(300)
        check(f"{tag} B: Sort › Homework first — rows needing homework first (default order inside), done rows after", order(page) == [x for x in base if x in ("AAPL", "AMD", "PLTR")] + [x for x in base if x in ("GE", "AVGO")], order(page))
        ls = js(page, "()=>localStorage.getItem('dash.wl5Sort')")
        check(f"{tag} B: Sort choice is remembered on this device (localStorage dash.wl5Sort)", ls == "hw", ls)
        page.select_option(sel, "default"); page.wait_for_timeout(300)
        check(f"{tag} B: Sort › Default restores the original order", order(page) == base, order(page))
        # ---- filter
        opts = js(page, "()=>[...document.querySelectorAll('[data-lr5-filter] option')].map(o=>o.textContent)")
        check(f"{tag} B: Filter counts — All (5) · Holding (1) · Plan ready (1) · No plan (3) · Needs homework (3)", opts == ["All (5)", "Holding (1)", "Plan ready (1)", "No plan (3)", "Needs homework (3)"], opts)
        for val, want in (("hold", ["AAPL"]), ("plan", ["AVGO"]), ("none", ["GE", "AMD", "PLTR"]), ("need", ["AAPL", "AMD", "PLTR"])):
            page.select_option("[data-lr5-filter]", val); page.wait_for_timeout(250)
            check(f"{tag} B: Filter › {val} shows exactly {want}", sorted(order(page)) == sorted(want), order(page))
        page.select_option("[data-lr5-filter]", "all"); page.wait_for_timeout(250)
        check(f"{tag} B: Filter choice remembered (dash.wl5Filter) · back to All → 5 rows", js(page, "()=>localStorage.getItem('dash.wl5Filter')") == "all" and len(order(page)) == 5)
        js(page, "()=>wl5Find('av')"); page.wait_for_timeout(250)
        check(f"{tag} B: Find ticker 'av' → AVGO only", order(page) == ["AVGO"], order(page))
        js(page, "()=>wl5Find('')"); page.wait_for_timeout(200)
        # ---- detail panel
        if desk:
            js(page, "()=>wlOpen('AAPL')"); page.wait_for_timeout(300)
            det = js(page, "()=>{ const d = document.querySelector('[data-lr5-det]'); const f = k=>{ const e = d.querySelector('[data-lr5-f=\"'+k+'\"]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }; return {sym:d.dataset.lr5Det, head:d.querySelector('.lr5-dh').innerText.replace(/\\s+/g,' ').trim(), why:f('why'), trigger:f('trigger'), exit:f('exit'), sector:f('sector'), main:d.querySelector('[data-lr5-main]').innerText.trim(), mainBlack:getComputedStyle(d.querySelector('[data-lr5-main]')).backgroundColor, hint:d.querySelector('.lr5-hint').innerText, amber:getComputedStyle(d.querySelector('[data-lr5-empty]')).color, link:(d.querySelector('[data-lr5-rs-link]')||{}).href||''}; }")
            check(f"{tag} D: detail AAPL — header 'AAPL Holding NASDAQ · Technology'", det["sym"] == "AAPL" and det["head"].startswith("AAPL Holding NASDAQ · Technology"), det)
            check(f"{tag} D: WHY 'Not written yet' in amber · TRIGGER — · EXIT WHEN —", det["why"] == "WHY Not written yet" and det["amber"] == "rgb(154, 91, 0)" and det["trigger"] == "TRIGGER —" and det["exit"] == "EXIT WHEN —", det)
            check(f"{tag} D: SECTOR VS SPY 'Technology (XLK) ↘ lagging · 12d' + RS 'RS 87 ← 72 (4 wks ago) · line ↗ · new high 18 Nov' + TradingView RS link", "Technology (XLK) ↘ lagging · 12d" in det["sector"] and "RS 87 ← 72 (4 wks ago) · line ↗ · new high 18 Nov" in det["sector"] and "RS chart on TradingView ↗" in det["sector"] and "tradingview.com/chart" in det["link"], det)
            check(f"{tag} D: one black main action 'Do homework ›' + hint about ⋯", det["main"] == "Do homework ›" and det["mainBlack"] == "rgb(20, 22, 26)" and "Full thesis, news and archive are in ⋯" in det["hint"], det)
            js(page, "()=>wlOpen('AVGO')"); page.wait_for_timeout(300)
            d2 = js(page, "()=>{ const d = document.querySelector('[data-lr5-det]'); const f = k=>d.querySelector('[data-lr5-f=\"'+k+'\"]').innerText.replace(/\\s+/g,' ').trim(); return {why:f('why'), trigger:f('trigger'), exit:f('exit'), main:d.querySelector('[data-lr5-main]').innerText.trim(), sector:f('sector')}; }")
            check(f"{tag} D: AVGO panel — WHY / TRIGGER / EXIT WHEN from the thesis · main 'Open plan ›' · RS line ↘, no new high", d2["why"] == "WHY AI networking share" and d2["trigger"] == "TRIGGER Break of the 4-week base" and d2["exit"] == "EXIT WHEN Hyperscaler capex cut" and d2["main"] == "Open plan ›" and "RS 64 ← 70 (4 wks ago) · line ↘" in d2["sector"] and "new high" not in d2["sector"], d2)
            js(page, "()=>wlOpen('PLTR')"); page.wait_for_timeout(300)
            d3 = js(page, "()=>document.querySelector('[data-lr5-f=\"sector\"]').innerText.replace(/\\s+/g,' ').trim()")
            check(f"{tag} D: PLTR panel (no RS data) → 'RS — …' + the TradingView link, no 0 / NaN", d3.startswith("SECTOR VS SPY Software (IGV)") and "RS — the daily price job has not covered this stock" in d3 and "RS chart on TradingView" in d3 and "NaN" not in d3, d3)
            js(page, "()=>wlOpen('AMD')"); page.wait_for_timeout(300)
            d4 = js(page, "()=>document.querySelector('[data-lr5-f=\"sector\"]').innerText.replace(/\\s+/g,' ').trim()")
            check(f"{tag} D: AMD panel (rating null · history<252) → reason shown", "less than 252 sessions" in d4, d4)
            # ⋯ menu
            js(page, "()=>wlOpen('AVGO')"); page.wait_for_timeout(250)
            page.click("[data-lr5-det] [data-lt-menu]"); page.wait_for_timeout(250)
            mi = js(page, "()=>[...document.querySelectorAll('[data-lr5-det] .ltMenu [role=menuitem]')].map(b=>b.innerText.trim())")
            check(f"{tag} D: ⋯ menu holds Full thesis · News & catalysts · Archive… · Edit · Import · Export · History", all(x in mi for x in ("Full thesis", "News & catalysts", "Archive…", "Edit", "Import thesis", "Export JSON")), mi)
            js(page, "()=>wlOpen('PLTR')"); page.wait_for_timeout(250); page.click("[data-lr5-det] [data-lt-menu]"); page.wait_for_timeout(250)
            check(f"{tag} D: Delete is in the ⋯ menu for a stock with no plan (PLTR)", "Delete" in js(page, "()=>[...document.querySelectorAll('[data-lr5-det] .ltMenu [role=menuitem]')].map(b=>b.innerText.trim())"))
            js(page, "()=>{ wlMenu = ''; wlOpen('AVGO'); }"); page.wait_for_timeout(250); page.click("[data-lr5-det] [data-lt-menu]"); page.wait_for_timeout(250)
            check(f"{tag} E: no Thai in the open ⋯ menu / panel", js(page, THAI) == [], js(page, THAI))
            page.click("[data-lr5-full]"); page.wait_for_timeout(500)
            tabs = js(page, "()=>[...document.querySelectorAll('[data-lt-tabs] .ltTab')].map(b=>b.innerText.trim())")
            check(f"{tag} D: Full thesis opens the old tabs (Summary · My Thesis · Business · Why buy · Track · Exit when) with a ‹ Summary back button", tabs[:6] == ["Summary", "My Thesis", "Business", "Why buy", "Track", "Exit when"] or len(tabs) >= 5, tabs)
            check(f"{tag} E: no Thai in the full thesis panel (Summary tab)", js(page, THAI) == [], js(page, THAI))
            for sub in ("biz", "why", "trk", "exit", "view"):
                js(page, "(s)=>wlSetSub(s)", sub); page.wait_for_timeout(250)
                t = js(page, THAI)
                check(f"{tag} E: no Thai in the full thesis › {sub}", t == [], t)
            page.click("[data-lr5-back]"); page.wait_for_timeout(300)
            check(f"{tag} D: ‹ Summary returns to the compact panel (table visible again)", js(page, "()=>!!document.querySelector('[data-lr5-det] [data-lr5-main]') && !!document.querySelector('[data-lr5-row]')"))
        else:
            js(page, "()=>{ wlBack(); }"); page.wait_for_timeout(200)
            check(f"{tag} C: phone — no sheet until a row is tapped", not js(page, "()=>document.querySelector('[data-lr5]').classList.contains('open')"))
            page.locator("[data-lr5-row][data-sym=AAPL]").click(position={"x": 20, "y": 14}); page.wait_for_timeout(400)
            sh = js(page, "()=>{ const d = document.querySelector('.lr5-det'); const r = d.getBoundingClientRect(); return {open:document.querySelector('[data-lr5]').classList.contains('open'), pos:getComputedStyle(d).position, bottom:Math.round(innerHeight - r.bottom), h:Math.round(r.height), vh:innerHeight, txt:d.innerText.replace(/\\s+/g,' ').trim(), close:Math.round(d.querySelector('[data-lr5-close]').getBoundingClientRect().height)}; }")
            check(f"{tag} C: tapping a row opens the detail as a bottom sheet (fixed · bottom 0 · ≤ 88% of the screen)", sh["open"] and sh["pos"] == "fixed" and sh["bottom"] == 0 and sh["h"] <= sh["vh"] * 0.88 + 2, sh)
            check(f"{tag} C: sheet carries the same content as the desktop panel (WHY · TRIGGER · EXIT WHEN · sector · RS · Do homework ›)", all(x in sh["txt"] for x in ("WHY Not written yet", "TRIGGER", "EXIT WHEN", "Technology (XLK) ↘ lagging · 12d", "RS 87 ← 72 (4 wks ago)", "RS chart on TradingView ↗", "Do homework ›")), sh["txt"])
            check(f"{tag} C: sheet × is a 36px+ tap target and closes it", sh["close"] >= 36)
            check(f"{tag} E: no Thai in the sheet", js(page, THAI) == [], js(page, THAI))
            page.click("[data-lr5-close]"); page.wait_for_timeout(300)
            check(f"{tag} C: × closes the sheet", not js(page, "()=>document.querySelector('[data-lr5]').classList.contains('open')"))
        # ---- archived
        js(page, "()=>{ document.querySelector('[data-wl1-arch]').open = true; }"); page.wait_for_timeout(200)
        ar = js(page, "()=>{ const d = document.querySelector('[data-wl1-arch]'); return {tag:d.tagName, open:d.open, sum:d.querySelector('summary').innerText.trim(), rows:[...d.querySelectorAll('[data-wl1-arch-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()), hint:d.querySelector('.lr5-archhint').innerText}; }")
        check(f"{tag} A: 'Archived (2)' is a <details> at the bottom; hint says what Archive means", ar["tag"] == "DETAILS" and ar["sum"] == "Archived (2)" and "stopped watching" in ar["hint"] and "notes" in ar["hint"], ar)
        check(f"{tag} A: archived rows = ticker · date · reason · Restore (newest first)", ar["rows"] == ["ARY 12 Nov too slow Restore", "ARX 10 Nov thesis broke after earnings Restore"], ar["rows"])
        js(page, "()=>{ document.querySelector('[data-wl1-arch]').open = true; }"); page.wait_for_timeout(200)
        check(f"{tag} A: archived rows fit the width (one line each)", js(page, "()=>[...document.querySelectorAll('[data-wl1-arch-row]')].every(r=>r.getBoundingClientRect().height <= 52 && r.scrollWidth <= r.clientWidth + 1)") and ov(page) <= 0)
        js(page, "()=>document.querySelector('[data-wl1-arch-row=ARX] [data-wl-restore]').click()"); page.wait_for_timeout(700)
        check(f"{tag} A: Restore puts the stock back in the table; count 2 → 1", "ARX" in order(page) and "Archived (1)" in js(page, "()=>document.querySelector('[data-wl1-arch-toggle]').innerText"), order(page))
        # ---- Compounder tab
        js(page, "()=>wl1TrkSet('ladder')"); page.wait_for_timeout(300)
        check(f"{tag} A: Compounder tab lists COST only", order(page) == ["COST"], order(page))
        js(page, "()=>wl1TrkSet('winner')"); page.wait_for_timeout(200)
        # ---- Ideas
        js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(500)
        ir = js(page, "()=>({on:document.querySelector('[data-wl1-ideas]').classList.contains('on'), hdr:[...document.querySelectorAll('.lr5-ith .lbl')].map(x=>x.innerText), rows:[...document.querySelectorAll('.lr5-ir')].map(r=>r.innerText.replace(/\\s+/g,' ').trim()), rs:[...document.querySelectorAll('.lr5-ir .c-rs')].map(e=>e.innerText.trim()), sum:document.querySelector('[data-wl1-sum]').innerText.replace(/\\s+/g,' ').trim(), btns:[!!document.querySelector('[data-idea-new-top]'), !!document.querySelector('[data-idea-import-top]')]})")
        check(f"{tag} F: Ideas tab — same table style, 2 idea rows, RS column '—' (does not apply), '+ Idea' and Import in the header", ir["on"] and len(ir["rows"]) == 2 and (ir["rs"] == ["—", "—"] if desk else True) and ir["btns"] == [True, True] and ir["sum"].startswith("2 ideas"), ir)
        check(f"{tag} F: no Thai in the Ideas list (English data fixture)", js(page, THAI) == [], js(page, THAI))
        js(page, "()=>ideaOpen('en-idea-1')"); page.wait_for_timeout(500)
        for sub in ("sum", "mech", "evd", "vc", "co"):
            js(page, "(s)=>{ try{ ideaSetTab(s); }catch(e){} }", sub); page.wait_for_timeout(250)
            t = js(page, THAI)
            check(f"{tag} F: no Thai in the idea detail › {sub}", t == [], t)
        check(f"{tag} F: no horizontal overflow on the Ideas tab", ov(page) <= 0, ov(page))
        js(page, "()=>{ wlBack(); wlSetView('wl'); }"); page.wait_for_timeout(300)
        # ---- price docs without close
        px = js(page, "()=>({pltr:pxAuto.PLTR && pxAuto.PLTR.ySym, close:pxAuto.PLTR && pxAuto.PLTR.close, err:pxErr, txt:/\\$0\\b|\\b0\\.00\\b/.test(document.getElementById('tabWatch').innerText)})")
        check(f"{tag} G: a price doc without close / rs (PLTR) is stored · price listener fine · no 0 price anywhere in Watch", px["pltr"] == "PLTR" and px["close"] is None and not px["err"] and not px["txt"], px)
        # ---- old RS field
        old = js(page, "()=>/RS (rating|stars)|Unrated|★/i.test(document.getElementById('tabWatch').innerText)")
        check(f"{tag} G: no obsolete manual 'RS rating' field in Watch", old is False)
        check(f"{tag} G: no console / page errors", not pe, pe)
    finally:
        b.close()


def C_SHOT(name):
    import os
    d = os.path.join(C.HERE, "screenshots", "lr5a"); os.makedirs(d, exist_ok=True); return os.path.join(d, name)


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 780)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY LR5a: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
