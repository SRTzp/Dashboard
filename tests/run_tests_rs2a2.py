#!/usr/bin/env python3
"""RS2a2 — Watch › Screen polish: M.Cap replaces Price (format · missing · detail line · Min M.Cap filter) · sortable column headers (both directions · ▲/▼ · Sort ▾ sync · remembered · Reset)
· Tab / Shift+Tab cycle Momentum → Compounder → Ideas → Screen (guards) · phone swipe next/previous (ignored on buttons / inputs / with a sheet) · compact + → ✓ (no navigation)
· Add to [Momentum] [Compounder] in the detail (desktop panel / phone sheet) · 360/390/1440 no overflow.   Run: python3 tests/run_tests_rs2a2.py"""
import sys
from playwright.sync_api import sync_playwright
import rs2a_common as C
from re1d_common import js, check, results

ROWS = "()=>[...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym)"
TXT = "(s)=>{ const r = document.querySelector('[data-rs2-row][data-sym=\"'+s+'\"]'); return r ? r.innerText.replace(/\\s+/g,' ').trim() : null }"
SEG = "()=>wl1SegNow()"
SW = """([x,y,dx,dy,ms,sel])=>new Promise(res=>{
  const tgt = sel ? document.querySelector(sel) : document.elementFromPoint(x,y);
  if(!tgt) return res('notarget');
  if(sel){ const r = tgt.getBoundingClientRect(); x = r.left + r.width/2; y = r.top + r.height/2; }
  const mk = (px,py)=>new Touch({identifier:1, target:tgt, clientX:px, clientY:py});
  const fire = (type, px, py)=>tgt.dispatchEvent(new TouchEvent(type, {bubbles:true, cancelable:true, touches:type==='touchend'?[]:[mk(px,py)], changedTouches:[mk(px,py)]}));
  fire('touchstart', x, y); fire('touchmove', x+dx/2, y+dy/2);
  setTimeout(()=>{ fire('touchend', x+dx, y+dy); res('ok'); }, ms);
})"""


def swipe(page, dx, dy=0, x=195, y=None, sel=None):
    if y is None: y = 450 if js(page, SEG) == "screen" else 300     # inside the Screen list · inside the Ideas / Momentum / Compounder content
    r = page.evaluate(SW, [x, y, dx, dy, 120, sel]); page.wait_for_timeout(450); return r


def over(page):
    return js(page, "()=>({sw:document.documentElement.scrollWidth - innerWidth, bad:[...document.querySelectorAll('.lr5-screen *')].filter(e=>{const r=e.getBoundingClientRect(); return r.width>0 && r.right > innerWidth + 1 && !e.closest('.lr5-list') && !e.closest('.rs2-fl')}).length})")


def desk(pw, w, h):
    tag = "[%s]" % w
    b, page, pe, ce = C.open_screen(pw, w, h)
    try:
        # ---- 1 M.Cap
        check(f"{tag} 1 rs2Cap: $1.3T · $4.2B · $860M · missing → —", js(page, "()=>[rs2Cap(1.3e12), rs2Cap(4.2e9), rs2Cap(860e6), rs2Cap(null), rs2Cap(0), rs2Cap(undefined)]") == ["$1.3T", "$4.2B", "$860M", "—", "—", "—"])
        hdr = js(page, "()=>[...document.querySelectorAll('.rs2-th .lbl')].map(x=>x.innerText.trim().toLowerCase())")
        check(f"{tag} 1 desktop column M.Cap sits where Price was (no Price column)", hdr == ["stock", "sector vs spy", "rs · from high", "m.cap", "avg $vol", "earnings"], hdr)
        t = js(page, TXT, "NVDA"); z = js(page, TXT, "ZETA")
        check(f"{tag} 1 NVDA $4.4T · ZETA $860M · no price in the row", "$4.4T" in t and "$860M" in z and "182.40" not in t and "24.80" not in z, [t, z])
        js(page, "()=>rs2Find('F000')"); page.wait_for_timeout(200)
        f0 = js(page, TXT, "F000")
        check(f"{tag} 1 a name with no market cap shows — (and stays in the list)", f0 is not None and " — " in f0.replace("$", " ") or (f0 and "—" in f0), f0)
        js(page, "()=>{ rs2Find(''); rs2Pick('NVDA'); }"); page.wait_for_timeout(250)
        det = js(page, "()=>document.querySelector('[data-rs2-dm]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 1 detail line: Price 182.40 · M.Cap $4.4T · Avg $vol $38.1B · Earnings in 6d", det.startswith("Price 182.40 · M.Cap $4.4T · Avg $vol $38.1B · Earnings in 6d"), det)
        # ---- Min M.Cap
        check(f"{tag} 1 Min M.Cap is off by default (86 rows, no filter count)", js(page, "()=>rs2.mcMin") == 0 and js(page, "()=>document.querySelector('[data-rs2-sum]').innerText").count("86") == 1 and "·" not in js(page, "()=>document.querySelector('[data-rs2-filter-btn]').innerText"))
        js(page, "()=>{ rs2.fOpen = true; renderWatchlist(); }"); page.wait_for_timeout(200)
        page.select_option("[data-rs2-f=mcMin]", "10000000000"); page.wait_for_timeout(250)
        js(page, "()=>rs2More()"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        ok = js(page, "(o)=>o.every(s=>{ const r = rs2.rows.find(x=>x.t===s); return typeof r.mc === 'number' && r.mc >= 1e10 })", o)
        exp = js(page, "()=>rs2.rows.filter(rs2Match).length")
        check(f"{tag} 1 Min M.Cap $10B → only names with M.Cap ≥ $10B (missing ones drop out), button shows 1", ok and "NVDA" in o and "ZETA" not in o and "F000" not in o and len(o) == exp and 7 <= len(o) < 86 and js(page, "()=>document.querySelector('[data-rs2-filter-btn]').innerText").strip().startswith("Filter · 1"), o[:9])
        js(page, "()=>{ rs2Reset(); rs2.fOpen = false; renderWatchlist(); }"); page.wait_for_timeout(200)
        # ---- 2 header sorts
        th = lambda k: f"[data-rs2-th={k}]"
        check(f"{tag} 2 clickable headers: RS · from high · M.Cap · Avg $vol · Earnings; none active by default", js(page, "()=>[...document.querySelectorAll('[data-rs2-th]')].map(b=>b.dataset.rs2Th)") == ["rs", "high", "mc", "vol", "earn"] and js(page, "()=>!document.querySelector('[data-rs2-dir]')"))
        page.click(th("mc")); page.wait_for_timeout(250)
        o = js(page, ROWS)
        check(f"{tag} 2 M.Cap header → biggest first (NVDA $4.4T · PLTR · GE …), ▼ on the header, Sort ▾ shows M.Cap", o[:3] == ["NVDA", "PLTR", "GE"] and js(page, "()=>document.querySelector('[data-rs2-th=mc]').dataset.rs2Dir") == "desc" and "▼" in js(page, "()=>document.querySelector('[data-rs2-th=mc]').innerText") and js(page, "()=>document.querySelector('[data-rs2-sort]').value") == "mc" and "M.Cap" in js(page, "()=>document.querySelector('[data-rs2-sort-wrap] .t').innerText"), o[:4])
        page.click(th("mc")); page.wait_for_timeout(250)
        js(page, "()=>rs2More()"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        miss = js(page, "(o)=>o.map(s=>{ const r = rs2.rows.find(x=>x.t===s); return typeof r.mc === 'number' ? 1 : 0 })", o)
        check(f"{tag} 2 second click flips (smallest first, ▲) — names with no M.Cap stay last", o[0] == "F001" and js(page, "()=>document.querySelector('[data-rs2-th=mc]').dataset.rs2Dir") == "asc" and "▲" in js(page, "()=>document.querySelector('[data-rs2-th=mc]').innerText") and miss == sorted(miss, reverse=True) and miss[-1] == 0 and js(page, "()=>rs2.sort") == "mc" and "reversed" in js(page, "()=>document.querySelector('[data-rs2-sort-wrap] .t').innerText"), [o[:3], miss[-5:]])
        page.click(th("vol")); page.wait_for_timeout(250)
        o = js(page, ROWS)
        check(f"{tag} 2 Avg $vol header → NVDA ($38.1B) then PLTR; click again → smallest first", o[:2] == ["NVDA", "PLTR"] and js(page, "()=>document.querySelector('[data-rs2-sort]').value") == "vol", o[:3])
        page.click(th("vol")); page.wait_for_timeout(250)
        v = js(page, "()=>[...document.querySelectorAll('[data-rs2-row]')].slice(0, 12).map(r=>rs2.rows.find(x=>x.t===r.dataset.sym).v)")
        check(f"{tag} 2 Avg $vol flipped → ascending", v == sorted(v), v)
        page.click(th("earn")); page.wait_for_timeout(250)
        o = js(page, "()=>{ rs2.shown = 200; renderWatchlist(); return [...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym) }")
        nox = js(page, "(o)=>o.map(s=>rs2Earn(rs2.rows.find(x=>x.t===s)) ? 1 : 0)", o)
        check(f"{tag} 2 Earnings header → soonest first (NVDA in 6d · PLTR 2 Dec · GE · ZETA), ▲, no date last", o[:4] == ["NVDA", "PLTR", "GE", "ZETA"] and js(page, "()=>document.querySelector('[data-rs2-th=earn]').dataset.rs2Dir") == "asc" and nox == sorted(nox, reverse=True), o[:5])
        page.click(th("earn")); page.wait_for_timeout(250)
        o = js(page, ROWS)
        check(f"{tag} 2 Earnings flipped → latest first (ZETA 4 Feb), still no date last", o[:4] == ["ZETA", "GE", "PLTR", "NVDA"], o[:5])
        page.click(th("rs")); page.wait_for_timeout(250)
        o = js(page, ROWS); rr = js(page, "(o)=>o.map(s=>rs2.rows.find(x=>x.t===s).r)", o)
        check(f"{tag} 2 RS header → highest RS first (99s) · ▼", rr[:2] == [99, 99] and rr == sorted(rr, reverse=True) and js(page, "()=>document.querySelector('[data-rs2-th=rs]').dataset.rs2Dir") == "desc", rr[:6])
        page.click(th("rs")); page.wait_for_timeout(250)
        rr = js(page, "()=>[...document.querySelectorAll('[data-rs2-row]')].map(r=>rs2.rows.find(x=>x.t===r.dataset.sym).r)")
        check(f"{tag} 2 RS header again → lowest RS first", rr == sorted(rr) and rr[0] < 90, rr[:6])
        page.click(th("high")); page.wait_for_timeout(250)
        o = js(page, ROWS)
        check(f"{tag} 2 'from high' header → closest to the high first (NVDA / CRDO) · Sort ▾ = Closest to high", set(o[:2]) == {"NVDA", "CRDO"} and js(page, "()=>document.querySelector('[data-rs2-sort]').value") == "high", o[:4])
        page.select_option("[data-rs2-sort]", "mc"); page.wait_for_timeout(250)
        check(f"{tag} 2 choosing in the Sort ▾ dropdown → header ▼ on M.Cap (sync the other way)", js(page, "()=>document.querySelector('[data-rs2-th=mc]').dataset.rs2Dir") == "desc" and js(page, ROWS)[0] == "NVDA")
        st = js(page, "()=>JSON.parse(localStorage.getItem('dash.rs2b'))")
        check(f"{tag} 2 the choice is remembered (localStorage dash.rs2b sort + rev)", st.get("sort") == "mc" and st.get("rev") is False, st)
        page.click(th("mc")); page.wait_for_timeout(200)
        st = js(page, "()=>JSON.parse(localStorage.getItem('dash.rs2b'))")
        check(f"{tag} 2 reversed direction is remembered too", st.get("sort") == "mc" and st.get("rev") is True, st)
        page.click("[data-rs2-reset]"); page.wait_for_timeout(250)
        st = js(page, "()=>JSON.parse(localStorage.getItem('dash.rs2b'))")
        check(f"{tag} 2 Reset clears the sort → Near high + RS, no arrow, default order", st.get("sort") == "nearhigh" and not st.get("rev") and js(page, "()=>!document.querySelector('[data-rs2-dir]')") and js(page, ROWS)[:3] == ["NVDA", "ZETA", "PLTR"], st)
        # ---- 3 Tab cycle
        js(page, "()=>{ wlSetView('wl'); wl1TrkSet('winner'); document.activeElement.blur(); }"); page.wait_for_timeout(300)
        seq = []
        for _ in range(5):
            page.keyboard.press("Tab"); page.wait_for_timeout(250); seq.append(js(page, SEG))
        check(f"{tag} 3 Tab cycles (NT1 order) Momentum → Compounder → Screen → Ideas → Momentum → Compounder", seq == ["ladder", "screen", "idea", "winner", "ladder"], seq)
        seq = []
        for _ in range(3):
            page.keyboard.press("Shift+Tab"); page.wait_for_timeout(250); seq.append(js(page, SEG))
        check(f"{tag} 3 Shift+Tab goes back (Compounder → Momentum → Ideas → Screen)", seq == ["winner", "idea", "screen"], seq)
        check(f"{tag} 3 the segmented control follows (Screen selected)", js(page, "()=>[...document.querySelectorAll('[data-wl1-segs] [role=tab]')].map(t=>t.getAttribute('aria-selected'))") == ["false", "false", "false", "true"])
        js(page, "()=>{ wlSetView('screen'); }"); page.wait_for_timeout(300)
        page.focus("[data-rs2-q]"); page.keyboard.press("Tab"); page.wait_for_timeout(250)
        check(f"{tag} 3 Tab while typing in the search box does NOT switch segment", js(page, SEG) == "screen", js(page, SEG))
        js(page, "()=>{ document.activeElement.blur(); wlMenu = 'NVDA'; }"); page.keyboard.press("Tab"); page.wait_for_timeout(250)
        check(f"{tag} 3 Tab with a menu open is ignored (wl1Blocked)", js(page, SEG) == "screen", js(page, SEG))
        js(page, "()=>{ wlMenu = ''; }")
        # ---- 4 compact + → ✓
        js(page, "()=>{ wlSetView('screen'); }"); page.wait_for_timeout(300)
        bt = js(page, "()=>{ const b = document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]'); const r = b.getBoundingClientRect(); return {w:Math.round(r.width), h:Math.round(r.height), t:b.innerText.trim()} }")
        check(f"{tag} 4 desktop row button = small square '+' (≤ 32px)", bt["t"] == "+" and bt["w"] <= 32 and bt["h"] <= 32, bt)
        before = js(page, "()=>({v:wlView, trk:wl1Trk})")
        page.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"); page.wait_for_timeout(600)
        st = js(page, "()=>{ const b = document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]'); const i = wlItemOf('PLTR'); return {a:b.dataset.rs2Add, d:b.disabled, t:b.innerText.trim(), v:wlView, trk:i ? wl1TrkOf(i) : null, sel:rs2.sel} }")
        check(f"{tag} 4 + adds PLTR to Momentum and shows ✓ (now a menu button) in the same row — still on Screen, no navigation", st["a"] == "done" and not st["d"] and st["t"] == "✓" and st["trk"] == "winner" and st["v"] == "screen" and before["v"] == "screen", st)
        col = js(page, "()=>getComputedStyle(document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]')).color")
        check(f"{tag} 4 the ✓ is muted (grey, not a button)", col == "rgb(95, 102, 114)" or col.startswith("rgb(9") or col.startswith("rgb(1"), col)
        # ---- 5 Add to (detail)
        js(page, "()=>rs2Pick('APP')"); page.wait_for_timeout(250)
        pr = js(page, "()=>[...document.querySelectorAll('[data-rs2-addto]')].map(b=>[b.dataset.rs2Addto, b.getAttribute('aria-pressed'), b.innerText.trim()])")
        check(f"{tag} 5 detail: Add to [Momentum] [Compounder], Momentum preselected, above + Add to Watch", pr == [["winner", "true", "Momentum"], ["ladder", "false", "Compounder"]] and js(page, "()=>{ const a = document.querySelector('[data-rs2-addto-wrap]'), b = document.querySelector('[data-rs2-add-big]'); return !!(a.compareDocumentPosition(b) & 4) }"), pr)
        page.click("[data-rs2-addto=ladder]"); page.wait_for_timeout(250)
        check(f"{tag} 5 choosing Compounder updates the toggle + hint", js(page, "()=>document.querySelector('[data-rs2-addto=ladder]').getAttribute('aria-pressed')") == "true" and "Compounder as No plan" in js(page, "()=>document.querySelector('.rs2-dn').innerText"))
        page.click("[data-rs2-add-big]"); page.wait_for_timeout(600)
        it = js(page, "()=>{ const i = wlItemOf('APP'); return i ? {lw:i.ladder_watch, trk:wl1TrkOf(i), src:i.src, ex:i.exch, st:wl1Status(i).label} : null }")
        det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
        row = js(page, "()=>document.querySelector('[data-rs2-row][data-sym=APP] [data-rs2-add]').dataset.rs2Add")
        check(f"{tag} 5 + Add to Watch with Compounder → Compounder track (ladder_watch), No plan, it.src saved, row ✓, detail 'On Watch · Compounder ✓'", it and it["lw"] is True and it["trk"] == "ladder" and "plan" in it["st"].lower() and it["src"]["from"] == "screen" and it["src"]["r12"] == 96 and row == "done" and "On Watch · Compounder ✓" in det and js(page, "()=>wlView") == "screen", [it, det[-60:]])
        js(page, "()=>rs2Pick('NVDA')"); page.wait_for_timeout(250)
        det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 5 already watching (NVDA) → 'On Watch · Momentum ✓', no Add to toggle", "On Watch · Momentum ✓" in det and js(page, "()=>!document.querySelector('[data-rs2-addto]')"), det[-60:])
        js(page, "()=>rs2Pick('RKLB')"); page.wait_for_timeout(250)
        page.click("[data-rs2-add-big]"); page.wait_for_timeout(600)
        i2 = js(page, "()=>{ const i = wlItemOf('RKLB'); return i ? [i.ladder_watch, wl1TrkOf(i)] : null }")
        check(f"{tag} 5 default (Momentum) via the detail button → Momentum", i2 and i2[0] is False and i2[1] == "winner", i2)
        o = over(page)
        check(f"{tag} 6 no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)
        cl = js(page, "()=>{ const l = document.querySelector('.lr5-list'); return {sw:l.scrollWidth, cw:l.clientWidth} }")
        check(f"{tag} 6 table fits (headers + M.Cap + compact + visible)", cl["sw"] <= cl["cw"] + 1, cl)
        check(f"{tag} 6 page errors none", not pe, pe[:2])
    finally:
        b.close()


def phone(pw, w, h):
    tag = "[%s]" % w
    b, page, pe, ce = C.open_screen(pw, w, h)
    try:
        t = js(page, TXT, "NVDA")
        check(f"{tag} 7 phone row has no M.Cap column (line 2 unchanged: name · sector · earnings)", "$4.4T" not in t and t.startswith("NVDA RS 99") and "earnings in 6d" in t, t)
        check(f"{tag} 7 no sortable header row on phone (Sort ▾ is the only control)", js(page, "()=>getComputedStyle(document.querySelector('.rs2-th')).display") == "none" and js(page, "()=>!!document.querySelector('[data-rs2-sort]')"))
        bt = js(page, "()=>[...document.querySelectorAll('[data-rs2-add]')].slice(0, 6).map(b=>{ const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height), b.innerText.trim()] })")
        check(f"{tag} 7 + is a 44px tap target", all(x[0] >= 44 and x[1] >= 44 for x in bt), bt)
        page.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"); page.wait_for_timeout(600)
        st = js(page, "()=>({v:wlView, sheet:!!document.querySelector('[data-rs2-sheet]'), t:document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]').innerText.trim(), trk:wl1TrkOf(wlItemOf('PLTR'))})")
        check(f"{tag} 7 + → ✓ in the same row, no navigation, no sheet opened", st["t"] == "✓" and st["v"] == "screen" and not st["sheet"] and st["trk"] == "winner", st)
        page.click("[data-rs2-row][data-sym=APP]"); page.wait_for_timeout(400)
        sh = js(page, "()=>{ const s = document.querySelector('[data-rs2-sheet]'); return s ? s.innerText.replace(/\\s+/g,' ') : null }")
        check(f"{tag} 7 tapping a row opens the detail sheet with M.Cap + Add to", sh and "APP" in sh and "M.Cap $205.0B" in sh and "Price 612.30" in sh and "Add to" in sh and "Momentum" in sh and "Compounder" in sh and "+ Add to Watch" in sh, sh)
        check(f"{tag} 7 the sheet is not a duplicate of a hidden panel (one [data-rs2-det])", js(page, "()=>document.querySelectorAll('[data-rs2-det]').length") == 1)
        page.click("[data-rs2-addto=ladder]"); page.wait_for_timeout(250)
        page.click("[data-rs2-add-big]"); page.wait_for_timeout(600)
        it = js(page, "()=>{ const i = wlItemOf('APP'); return i ? [i.ladder_watch, wl1TrkOf(i)] : null }")
        check(f"{tag} 7 phone sheet: Compounder add works → 'On Watch · Compounder ✓'", it == [True, "ladder"] and "On Watch · Compounder ✓" in js(page, "()=>document.querySelector('[data-rs2-sheet]').innerText"), it)
        o = over(page)
        check(f"{tag} 7 sheet open: no horizontal overflow", o["sw"] <= 0, o)
        page.click("[data-rs2-sheet-close]"); page.wait_for_timeout(300)
        check(f"{tag} 7 ✕ closes the sheet", js(page, "()=>!document.querySelector('[data-rs2-sheet]')"))
        js(page, "()=>{ rs2.fOpen = true; renderWatchlist(); }"); page.wait_for_timeout(250)
        fp = js(page, "()=>[...document.querySelectorAll('[data-rs2-filter-panel] [data-rs2-f]')].map(e=>e.dataset.rs2F)")
        check(f"{tag} 7 Filter holds Min M.Cap (off by default)", fp[-1] == "mcMin" and js(page, "()=>document.querySelector('[data-rs2-f=mcMin]').value") == "0", fp)
        js(page, "()=>{ rs2.fOpen = false; renderWatchlist(); }"); page.wait_for_timeout(250)
        # ---- swipe
        seq = []
        for dx in (120, 120, 120, 120):
            swipe(page, dx, 5); seq.append(js(page, SEG))
        check(f"{tag} 8 swipe right ×4: Screen → Compounder → Momentum → Ideas → stays (no wrap)", seq == ["ladder", "winner", "idea", "idea"], seq)
        seq = []
        for dx in (-120, -120, -120, -120):
            swipe(page, dx, 5); seq.append(js(page, SEG))
        check(f"{tag} 8 swipe left ×4: Ideas → Momentum → Compounder → Screen → stays", seq == ["winner", "ladder", "screen", "screen"], seq)
        check(f"{tag} 8 the segmented control follows (Screen selected)", js(page, "()=>[...document.querySelectorAll('[data-wl1-segs] [role=tab]')].map(t=>t.getAttribute('aria-selected'))") == ["false", "false", "false", "true"])
        swipe(page, 40, 0); swipe(page, 120, 120)
        check(f"{tag} 8 short (< 60px) or mostly-vertical swipes do nothing", js(page, SEG) == "screen", js(page, SEG))
        swipe(page, 120, 5, sel="[data-rs2-row][data-sym=GE] [data-rs2-add]")
        swipe(page, 120, 5, sel="[data-rs2-preset=emerging]")
        swipe(page, 120, 5, sel="[data-rs2-q]")
        swipe(page, 120, 5, sel="[data-rs2-sort]")
        check(f"{tag} 8 swipe starting on a button / preset / input / select is ignored", js(page, SEG) == "screen", js(page, SEG))
        page.click("[data-rs2-row][data-sym=GE]"); page.wait_for_timeout(300)
        swipe(page, 120, 5, y=300)
        check(f"{tag} 8 swipe ignored while the detail sheet is open", js(page, SEG) == "screen" and js(page, "()=>!!document.querySelector('[data-rs2-sheet]')"), js(page, SEG))
        js(page, "()=>rs2Sheet(false)"); page.wait_for_timeout(250)
        o = over(page)
        check(f"{tag} 9 no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)
        check(f"{tag} 9 page errors none", not pe, pe[:2])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        desk(pw, 1440, 900)
        phone(pw, 390, 844)
        phone(pw, 360, 740)
    f = [r for r in results if not r[1]]
    print("\nSUMMARY RS2a2: %d/%d pass" % (len(results) - len(f), len(results)))
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
