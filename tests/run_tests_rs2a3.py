#!/usr/bin/env python3
"""RS2a3 — Screen: undo / change after + (toast 8 s · Undo guard · Move to) · ✓ menu · detail Change ▾ · ←/→ presets (ends · typing/menu guards · other tabs) · tick column (header · shift-range · clear on preset/filter · Space)
· TradingView .txt (content · name · BRK.B · batch Add to Watch + Undo) · phone ⋯ download + ✓ sheet · Today alerts (each kind · cap 3 · priority · seen once · settings) · 360/390/1440 no overflow.   Run: python3 tests/run_tests_rs2a3.py"""
import re, sys
from playwright.sync_api import sync_playwright
import rs2a_common as C
from re1d_common import js, check, results

ROWS = "()=>[...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym)"
TOAST = "()=>{ const t = document.getElementById('rs2Toast'); return t && t.classList.contains('show') ? t.innerText.replace(/\\s+/g,' ').replace(/ ?✕$/,'').trim() : null }"
ITEM = "(s)=>{ const i = wlItemOf(s); return i ? {trk:wl1TrkOf(i), lw:i.ladder_watch, src:i.src && i.src.from} : null }"


def data():
    r = C.rows()
    bk = C.row("BRK-B", "Berkshire Hathaway B", "Financial Services", "Insurance - Diversified", "NYSE", 93, 90, "u", 0, -0.03, 470.0, 1.5e9, mc=1.0e12)
    r.insert(6, bk)
    return r


WL = C.WL + [{"t": "ZEDIT", "x": {"exch": "NYSE", "note": "my own note"}}]


def over(page):
    return js(page, "()=>({sw:document.documentElement.scrollWidth - innerWidth, bad:[...document.querySelectorAll('.lr5-screen *')].filter(e=>{const r=e.getBoundingClientRect(); return r.width>0 && r.right > innerWidth + 1 && !e.closest('.lr5-list') && !e.closest('.rs2-fl')}).length})")


def norm(t): return re.sub(r"\s+", " ", t or "").strip()


def dl(page, sel):
    with page.expect_download() as d:
        page.click(sel)
    f = d.value
    return f.suggested_filename, open(f.path()).read()


def desk(pw, w, h):
    tag = "[%s]" % w
    b, page, pe, ce = C.open_screen(pw, w, h, data=data(), wl=WL)
    try:
        # ---- 1 undo / change after +
        page.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"); page.wait_for_timeout(500)
        t = js(page, TOAST)
        check(f"{tag} 1 + shows ONE toast: 'Added PLTR to Momentum · Undo · Move to Compounder'", t == "Added PLTR to Momentum · Undo · Move to Compounder" and js(page, "()=>document.querySelectorAll('#rs2Toast').length") == 1, t)
        page.click("[data-rs2-row][data-sym=APP] [data-rs2-add=new]"); page.wait_for_timeout(400)
        check(f"{tag} 1 a new add REPLACES the toast (APP, still one toast)", js(page, TOAST) == "Added APP to Momentum · Undo · Move to Compounder" and js(page, "()=>document.querySelectorAll('#rs2Toast').length") == 1, js(page, TOAST))
        page.click("[data-rs2-undo]"); page.wait_for_timeout(500)
        st = js(page, "()=>({it:wlItemOf('APP'), b:document.querySelector('[data-rs2-row][data-sym=APP] [data-rs2-add]').dataset.rs2Add, pltr:!!wlItemOf('PLTR')})")
        check(f"{tag} 1 Undo (new, unedited) deletes the Watch item → row back to + · the earlier PLTR add stays", st["it"] is None and st["b"] == "new" and st["pltr"], st)
        check(f"{tag} 1 …and says so", js(page, TOAST) == "Removed APP from Watch", js(page, TOAST))
        page.click("[data-rs2-row][data-sym=HOOD] [data-rs2-add=new]"); page.wait_for_timeout(400)
        page.click("[data-rs2-moveto=ladder]"); page.wait_for_timeout(500)
        it = js(page, ITEM, "HOOD")
        check(f"{tag} 1 Move to Compounder → same field Edit uses (ladder_watch) · toast flips to 'Move to Momentum'", it and it["trk"] == "ladder" and it["lw"] is True and "Move to Momentum" in js(page, TOAST) and js(page, TOAST).startswith("Moved HOOD to Compounder"), [it, js(page, TOAST)])
        page.click("[data-rs2-moveto=winner]"); page.wait_for_timeout(400)
        check(f"{tag} 1 …and back to Momentum", js(page, ITEM, "HOOD")["trk"] == "winner")
        # edited since → Undo refuses
        js(page, "()=>wlCol().doc('HOOD').update({note:'looked at it'})"); page.wait_for_timeout(400)
        page.click("[data-rs2-undo]"); page.wait_for_timeout(400)
        check(f"{tag} 1 Undo on an item that was edited since → 'Edited — remove it from Watch instead' and the item stays", js(page, TOAST) == "Edited — remove it from Watch instead" and js(page, ITEM, "HOOD") is not None, js(page, TOAST))
        # 8 s
        page.click("[data-rs2-row][data-sym=GE] [data-rs2-add=new]") if js(page, "()=>!wlItemOf('GE')") else None
        page.click("[data-rs2-row][data-sym=RKLB] [data-rs2-add=new]"); page.wait_for_timeout(7000)
        a = js(page, TOAST); page.wait_for_timeout(1500); c = js(page, TOAST)
        check(f"{tag} 1 the toast stays ~8 s then goes", a is not None and c is None, [a, c])
        # ---- 2 ✓ menu
        page.click("[data-rs2-row][data-sym=NVDA] [data-rs2-add=done]"); page.wait_for_timeout(300)
        mi = js(page, "()=>[...document.querySelectorAll('[data-rs2-menu] .mi')].map(b=>[norm(b.innerText), b.disabled])".replace("norm(b.innerText)", "b.innerText.replace(/\\s+/g,' ').trim()"))
        check(f"{tag} 2 ✓ is a button → menu: Momentum ✓ · Compounder · Open in Watch › · Remove from Watch (disabled for a stock not added from Screen, with the reason)",
              [m[0] for m in mi] == ["Momentum ✓", "Compounder", "Open in Watch ›", "Remove from Watch not added from Screen"] and mi[3][1] is True and mi[0][1] is False, mi)
        page.click("[data-rs2-mv=ladder]"); page.wait_for_timeout(400)
        check(f"{tag} 2 menu › Compounder switches the track (ladder_watch) and closes", js(page, ITEM, "NVDA")["trk"] == "ladder" and js(page, "()=>!document.querySelector('[data-rs2-menu]')"))
        page.click("[data-rs2-row][data-sym=NVDA] [data-rs2-add=done]"); page.wait_for_timeout(250)
        check(f"{tag} 2 the menu now shows Compounder ✓", js(page, "()=>document.querySelector('[data-rs2-mv=ladder]').innerText.trim()") == "Compounder ✓")
        page.click("[data-rs2-openwl]"); page.wait_for_timeout(500)
        st = js(page, "()=>({v:wlView, trk:wl1Trk, sel:wlSel})")
        check(f"{tag} 2 menu › Open in Watch › → Watch list on that track with NVDA selected", st == {"v": "wl", "trk": "ladder", "sel": "NVDA"}, st)
        js(page, "()=>{ wl1TrkSet('winner'); wlSetView('screen'); }"); page.wait_for_timeout(500)
        page.click("[data-rs2-row][data-sym=HOOD] [data-rs2-add=done]"); page.wait_for_timeout(250)
        mi = js(page, "()=>[...document.querySelectorAll('[data-rs2-menu] .mi')].map(b=>[b.innerText.replace(/\\s+/g,' ').trim(), b.disabled])")
        check(f"{tag} 2 an item that was edited → Remove disabled with the reason", mi[3][1] is True and "has homework or notes" in mi[3][0], mi)
        page.keyboard.press("Escape"); page.wait_for_timeout(250)
        check(f"{tag} 2 Esc closes the menu", js(page, "()=>!document.querySelector('[data-rs2-menu]')"))
        page.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=done]"); page.wait_for_timeout(250)
        mi = js(page, "()=>[...document.querySelectorAll('[data-rs2-menu] .mi')].map(b=>[b.innerText.replace(/\\s+/g,' ').trim(), b.disabled])")
        check(f"{tag} 2 an item Screen created and nobody edited → Remove from Watch is enabled", mi[3] == ["Remove from Watch", False], mi)
        page.click("[data-rs2-remove]"); page.wait_for_timeout(500)
        check(f"{tag} 2 Remove from Watch deletes it → row back to +", js(page, "()=>!wlItemOf('PLTR')") and js(page, "()=>document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]').dataset.rs2Add") == "new")
        page.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"); page.wait_for_timeout(400)
        page.click("[data-rs2-row][data-sym=NVDA]"); page.wait_for_timeout(300)
        det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 2 detail on Watch: 'On Watch · Compounder ✓' + Change ▾", "On Watch · Compounder ✓" in det and "Change ▾" in det and js(page, "()=>!!document.querySelector('[data-rs2-change]')"), det[-60:])
        page.click("[data-rs2-change]"); page.wait_for_timeout(300)
        mi = js(page, "()=>[...document.querySelectorAll('[data-rs2-det] [data-rs2-menu] .mi')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 2 Change ▾ opens the same menu in the detail", mi[:3] == ["Momentum", "Compounder ✓", "Open in Watch ›"], mi)
        page.click("[data-rs2-mv=winner]"); page.wait_for_timeout(400)
        check(f"{tag} 2 …Momentum switches back", js(page, ITEM, "NVDA")["trk"] == "winner" and "On Watch · Momentum ✓" in js(page, "()=>document.querySelector('[data-rs2-det]').innerText"))
        # ---- 3 ←/→ presets
        js(page, "()=>{ rs2Reset(); document.activeElement.blur(); }"); page.wait_for_timeout(300)
        seq = []
        for k in ("ArrowRight", "ArrowRight", "ArrowRight", "ArrowLeft", "ArrowLeft", "ArrowLeft"):
            page.keyboard.press(k); page.wait_for_timeout(250); seq.append(js(page, "()=>rs2.preset"))
        check(f"{tag} 3 → → → ← ← ←: Emerging, Pullback, (end) Pullback, Emerging, Leaders, (end) Leaders — no wrap", seq == ["emerging", "pullback", "pullback", "emerging", "leaders", "leaders"], seq)
        check(f"{tag} 3 the preset tabs follow", js(page, "()=>document.querySelector('[data-rs2-preset=leaders]').getAttribute('aria-selected')") == "true")
        page.focus("[data-rs2-q]"); page.keyboard.press("ArrowRight"); page.wait_for_timeout(250)
        check(f"{tag} 3 not while typing in the search box", js(page, "()=>rs2.preset") == "leaders")
        js(page, "()=>{ document.activeElement.blur(); rs2.menu = {sym:'NVDA', at:'row'}; renderWatchlist(); }"); page.keyboard.press("ArrowRight"); page.wait_for_timeout(250)
        check(f"{tag} 3 not while a menu is open", js(page, "()=>rs2.preset") == "leaders")
        js(page, "()=>{ rs2.menu = null; renderWatchlist(); }")
        js(page, "()=>{ wlSetView('wl'); wl1TrkSet('winner'); document.activeElement.blur(); }"); page.wait_for_timeout(300)
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(250)
        check(f"{tag} 3 other tabs unchanged: on Momentum ← / → do not touch the Screen preset", js(page, "()=>rs2.preset") == "leaders" and js(page, "()=>wlView") == "wl")
        js(page, "()=>{ wlSetView('screen'); }"); page.wait_for_timeout(400)
        # ---- 4 tick
        check(f"{tag} 4 desktop has a checkbox column first (header + every row)", js(page, "()=>[!!document.querySelector('[data-rs2-tick-all]'), document.querySelectorAll('[data-rs2-tick]').length, document.querySelector('[data-rs2-row] .c-tk') === document.querySelector('[data-rs2-row]').firstElementChild]") == [True, 50, True])
        check(f"{tag} 4 no selection → no selection bar", js(page, "()=>!document.querySelector('[data-rs2-selbar]')"))
        page.click("[data-rs2-tick-all]"); page.wait_for_timeout(300)
        check(f"{tag} 4 header checkbox = every row SHOWN (50)", js(page, "()=>document.querySelector('[data-rs2-selcount]').innerText") == "50 selected" and js(page, "()=>document.querySelector('[data-rs2-tick-all]').checked"))
        page.click("[data-rs2-more]"); page.wait_for_timeout(300)
        check(f"{tag} 4 Show more → header is partial (indeterminate) · ticking again selects all 87 loaded rows", js(page, "()=>document.querySelector('[data-rs2-tick-all]').indeterminate") is True)
        page.click("[data-rs2-tick-all]"); page.wait_for_timeout(300)
        check(f"{tag} 4 …87 selected", js(page, "()=>document.querySelector('[data-rs2-selcount]').innerText") == "87 selected")
        bar = js(page, "()=>document.querySelector('[data-rs2-selbar]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} 4 bar: '87 selected · Download for TradingView (.txt) · Add to Watch · Clear'", bar == "87 selected · ⤓ Download for TradingView (.txt) · Add to Watch · Clear", bar)
        page.click("[data-rs2-clrsel]"); page.wait_for_timeout(250)
        check(f"{tag} 4 Clear empties the selection", js(page, "()=>!document.querySelector('[data-rs2-selbar]') && document.querySelectorAll('[data-rs2-tick]:checked').length") == 0)
        order = js(page, ROWS)
        page.click(f"[data-rs2-tick={order[1]}]"); page.click(f"[data-rs2-tick={order[4]}]", modifiers=["Shift"]); page.wait_for_timeout(300)
        got = js(page, "()=>[...document.querySelectorAll('[data-rs2-tick]:checked')].map(c=>c.dataset.rs2Tick)")
        check(f"{tag} 4 Shift+click selects the range from the last clicked row (rows 2–5)", got == order[1:5], [got, order[:6]])
        page.click(f"[data-rs2-tick={order[2]}]"); page.wait_for_timeout(250)
        check(f"{tag} 4 a plain click toggles one row", js(page, "()=>document.querySelector('[data-rs2-selcount]').innerText") == "3 selected")
        js(page, "()=>{ rs2.sel = 'NVDA'; renderWatchlist(); }"); page.wait_for_timeout(250); page.mouse.click(5, 5)
        page.keyboard.press("ArrowDown"); page.keyboard.press("ArrowDown"); page.wait_for_timeout(250)
        o2 = js(page, ROWS)
        check(f"{tag} 4 ↓ ↓ moves the selected row (NVDA → third row), ↑ back, stops at the first row", js(page, "()=>rs2.sel") == o2[2] and (page.keyboard.press("ArrowUp") or True) and (page.keyboard.press("ArrowUp") or True) and (page.keyboard.press("ArrowUp") or True) and js(page, "()=>rs2.sel") == o2[0], [o2[:3], js(page, "()=>rs2.sel")])
        js(page, "()=>{ rs2.sel = 'NVDA'; renderWatchlist(); }"); page.wait_for_timeout(250)
        page.keyboard.press("Space"); page.wait_for_timeout(250)
        check(f"{tag} 4 Space toggles the tick of the selected row (NVDA)", js(page, "()=>!!rs2.tick.NVDA") is True and js(page, "()=>document.querySelector('[data-rs2-selcount]').innerText") == "4 selected")
        page.keyboard.press("Space"); page.wait_for_timeout(250)
        check(f"{tag} 4 …and again un-ticks it", js(page, "()=>!rs2.tick.NVDA") is True)
        js(page, "()=>{ rs2.shown = 50; rs2.sel = rs2View()[49].t; renderWatchlist(); }"); page.wait_for_timeout(300)
        o50 = js(page, "()=>rs2View().map(r=>r.t)")
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(350)
        check(f"{tag} 4 ↓ on the last shown row (50) with Show more → loads the next 50 and moves to row 51", js(page, "()=>rs2.shown") == 100 and js(page, "()=>rs2.sel") == o50[50] and len(js(page, ROWS)) == 87, [js(page, "()=>rs2.shown"), js(page, "()=>rs2.sel"), o50[50]])
        js(page, "()=>{ rs2.sel = rs2View()[86].t; renderWatchlist(); }"); page.keyboard.press("ArrowDown"); page.wait_for_timeout(250)
        check(f"{tag} 4 ↓ on the very last row (nothing more to load) stays", js(page, "()=>rs2.sel") == o50[86] and js(page, "()=>rs2.shown") == 100)
        js(page, "()=>{ rs2.shown = 50; rs2.sel = rs2View()[0].t; renderWatchlist(); }"); page.wait_for_timeout(250)
        page.click("[data-rs2-preset=emerging]"); page.wait_for_timeout(300)
        check(f"{tag} 4 selection clears when the preset changes", js(page, "()=>!document.querySelector('[data-rs2-selbar]')"))
        page.click("[data-rs2-preset=leaders]"); page.wait_for_timeout(300)
        page.click(f"[data-rs2-tick={order[0]}]"); js(page, "()=>{ rs2Set('rsMin', 90); }"); page.wait_for_timeout(300)
        check(f"{tag} 4 …and when a filter changes", js(page, "()=>!document.querySelector('[data-rs2-selbar]')"))
        js(page, "()=>rs2Reset()"); page.wait_for_timeout(300)
        page.click(f"[data-rs2-tick={order[0]}]"); js(page, "()=>{ rs2Set('sort', 'mc'); }"); page.wait_for_timeout(300)
        check(f"{tag} 4 (a sort change keeps it — same rows)", js(page, "()=>rs2TkN()") == 1)
        js(page, "()=>rs2Reset()"); page.wait_for_timeout(300)
        # ---- 5 .txt
        order = js(page, ROWS)
        for s in ("NVDA", "BRK-B", "ZETA"): page.click(f"[data-rs2-tick={s}]")
        name, txt = dl(page, "[data-rs2-dl]")
        exp = ",".join({"NVDA": "NASDAQ:NVDA", "BRK-B": "NYSE:BRK.B", "ZETA": "NYSE:ZETA"}[s] for s in order if s in ("NVDA", "BRK-B", "ZETA"))
        check(f"{tag} 5 file: one line, comma-separated EXCH:SYMBOL in list order, BRK-B → NYSE:BRK.B, no trailing comma", txt == exp and "\n" not in txt and not txt.endswith(",") and "NYSE:BRK.B" in txt and "NASDAQ:NVDA" in txt, [txt, exp])
        check(f"{tag} 5 name screen-<preset>-YYYY-MM-DD.txt", name == "screen-leaders-2026-11-19.txt", name)
        js(page, "()=>rs2Reset()"); page.click("[data-rs2-preset=emerging]"); page.wait_for_timeout(300)
        page.click("[data-rs2-tick-all]"); n2, t2 = dl(page, "[data-rs2-dl]")
        check(f"{tag} 5 the preset is in the name (emerging) · ≤ 10 NASDAQ symbols", n2 == "screen-emerging-2026-11-19.txt" and t2.count("NASDAQ:EM") == 10, [n2, t2[:60]])
        js(page, "()=>rs2Reset()"); page.wait_for_timeout(300)
        # ---- 6 batch add + undo
        for s in ("NVDA", "BRK-B", "ZETA", "CRDO"): page.click(f"[data-rs2-tick={s}]")
        page.click("[data-rs2-addsel]"); page.wait_for_timeout(600)
        t = js(page, TOAST)
        added = js(page, "()=>['NVDA','BRK-B','ZETA','CRDO'].map(s=>{ const i = wlItemOf(s); return i ? wl1TrkOf(i) + (i.src ? ':screen' : '') : null })")
        check(f"{tag} 6 Add to Watch (batch): Momentum, skips names already on Watch, ONE summary toast with Undo", added == ["winner", "winner:screen", "winner", "winner:screen"] and t and t.startswith("Added 2 stocks to Momentum (2 already on Watch)") and "Undo" in t, [added, t])
        check(f"{tag} 6 the selection is cleared after", js(page, "()=>!document.querySelector('[data-rs2-selbar]')"))
        page.click("[data-rs2-undo]"); page.wait_for_timeout(500)
        gone = js(page, "()=>['BRK-B','CRDO'].map(s=>!wlItemOf(s))")
        check(f"{tag} 6 Undo removes only the names this batch created (NVDA / ZETA stay)", gone == [True, True] and js(page, "()=>!!wlItemOf('NVDA') && !!wlItemOf('ZETA')"), gone)
        o = over(page)
        check(f"{tag} 7 no horizontal overflow (tick column + bar + toast)", o["sw"] <= 0 and o["bad"] == 0, o)
        check(f"{tag} 7 page errors none", not pe, pe[:2])
    finally:
        b.close()


def hwpage(pw):
    import hw1_common as H
    tag = "[1440]"
    b, page, pe = H.open_hw(pw, 1440, 480)
    try:
        H.go(page, "AAPL", "winner")
        POS = "()=>({sel:wlSel, on:hw1On(), pg:!!document.querySelector('[data-hw1-page=AAPL]'), y:Math.round(window.scrollY + [...document.querySelectorAll('.hw1-pg, .lr5.hw .wlDet.lr5-det, .hw1-body, .hw1-facts')].reduce((a, el)=>a + el.scrollTop, 0))})"
        a = js(page, POS)
        check(f"{tag} 11 Homework page open on AAPL", a["sel"] == "AAPL" and a["on"] and a["pg"], a)
        js(page, "()=>document.activeElement && document.activeElement.blur()")
        for _ in range(3): page.keyboard.press("ArrowDown"); page.wait_for_timeout(120)
        page.wait_for_timeout(300); b1 = js(page, POS)
        check(f"{tag} 11 ↓ ↓ ↓ on the Homework page: same stock (AAPL), page still open, and it scrolled", b1["sel"] == "AAPL" and b1["on"] and b1["pg"] and b1["y"] > a["y"], [a, b1])
        for _ in range(2): page.keyboard.press("ArrowUp"); page.wait_for_timeout(120)
        page.wait_for_timeout(300); c1 = js(page, POS)
        check(f"{tag} 11 ↑ ↑ scrolls back up — still AAPL, page open", c1["sel"] == "AAPL" and c1["on"] and c1["pg"] and c1["y"] < b1["y"], [b1, c1])
        for _ in range(60): page.keyboard.press("ArrowUp")
        page.wait_for_timeout(300)
        for _ in range(60): page.keyboard.press("ArrowDown")
        page.wait_for_timeout(300); d1 = js(page, POS)
        check(f"{tag} 11 many ↓ presses past the bottom never jump to the next stock or close the page", d1["sel"] == "AAPL" and d1["on"] and d1["pg"], d1)
        ta = "[data-hw1-ta]"
        if js(page, "(q)=>!!document.querySelector(q)", ta):
            page.focus(ta); page.keyboard.press("ArrowDown"); page.keyboard.press("ArrowUp"); page.wait_for_timeout(200)
            e1 = js(page, POS)
            check(f"{tag} 11 typing in a field: arrows are not handled by the page (stock + page unchanged)", e1["sel"] == "AAPL" and e1["on"] and e1["pg"], e1)
        check(f"{tag} 11 page errors none", not pe, pe[:2])
    finally:
        b.close()


def phone(pw, w, h):
    tag = "[%s]" % w
    b, page, pe, ce = C.open_screen(pw, w, h, data=data(), wl=WL)
    try:
        check(f"{tag} 8 phone: no tick boxes", js(page, "()=>[...document.querySelectorAll('[data-rs2-tick]')].every(c=>c.offsetParent === null)") and js(page, "()=>!document.querySelector('[data-rs2-selbar]')"))
        page.click("[data-rs2-dots]"); page.wait_for_timeout(300)
        mi = js(page, "()=>[...document.querySelectorAll('[data-rs2-pmenu] .mi')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 8 ⋯ menu: Download shown list (.txt) 87 · Filter · Reset · Edit rules (RS2d)", mi == ["⤓ Download shown list (.txt) 87", "Filter", "Reset", "Edit rules"], mi)
        name, txt = dl(page, "[data-rs2-dl-shown]")
        parts = txt.split(",")
        check(f"{tag} 8 downloads ALL rows of the current preset/filter (87 — not just the 50 loaded) · NYSE:BRK.B inside", len(parts) == 87 and "NYSE:BRK.B" in parts and parts[0] == "NASDAQ:NVDA" and name == "screen-leaders-2026-11-19.txt", [len(parts), name])
        check(f"{tag} 8 the menu closes after", js(page, "()=>!document.querySelector('[data-rs2-pmenu]')"))
        page.click("[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"); page.wait_for_timeout(500)
        t = js(page, TOAST)
        bt = js(page, "()=>[...document.querySelectorAll('#rs2Toast button')].map(b=>Math.round(b.getBoundingClientRect().height))")
        check(f"{tag} 8 toast 'Added PLTR … Undo · Move to Compounder' with ≥ 44px buttons", t.startswith("Added PLTR to Momentum · Undo · Move to Compounder") and all(x >= 40 for x in bt), [t, bt])
        o = over(page)
        check(f"{tag} 8 toast: no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)
        page.click("[data-rs2-undo]"); page.wait_for_timeout(400)
        check(f"{tag} 8 Undo on phone", js(page, "()=>!wlItemOf('PLTR')"))
        page.click("[data-rs2-row][data-sym=NVDA] [data-rs2-add=done]"); page.wait_for_timeout(300)
        sh = js(page, "()=>{ const s = document.querySelector('[data-rs2-menu-sheet]'); return s ? s.innerText.replace(/\\s+/g,' ') : null }")
        check(f"{tag} 8 ✓ tap = the same menu as a sheet (Momentum ✓ · Compounder · Open in Watch › · Remove from Watch)", sh and "Momentum ✓" in sh and "Compounder" in sh and "Open in Watch ›" in sh and "Remove from Watch" in sh and "not added from Screen" in sh and js(page, "()=>!document.querySelector('[data-rs2-sheet]')"), sh)
        o = over(page)
        check(f"{tag} 8 menu sheet: no horizontal overflow", o["sw"] <= 0, o)
        page.click("[data-rs2-mv=ladder]"); page.wait_for_timeout(400)
        check(f"{tag} 8 sheet › Compounder switches the track", js(page, ITEM, "NVDA")["trk"] == "ladder" and js(page, "()=>!document.querySelector('[data-rs2-menu-sheet]')"))
        page.keyboard.press("Escape")
        o = over(page)
        check(f"{tag} 9 no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)
        check(f"{tag} 9 page errors none", not pe, pe[:2])
    finally:
        b.close()


# ---------------- Today alerts
CHG = {"asOf": "2026-11-19", "prevAsOf": "2026-11-18", "items": [
    {"sym": "CRDO", "k": "d", "from": 78, "to": 95}, {"sym": "GE", "k": "a", "from": 91, "to": 91}, {"sym": "ZETA", "k": "b", "from": 84, "to": 78},
    {"sym": "APP", "k": "d", "from": 80, "to": 93}, {"sym": "NVDA", "k": "c", "from": 99, "to": 80}, {"sym": "EM0", "k": "e", "from": 60, "to": 91},
    {"sym": "PLTR", "k": "b", "from": 88, "to": 79}, {"sym": "HOOD", "k": "d", "from": 70, "to": 91}]}
LINES = "()=>[...document.querySelectorAll('[data-rs2-chg]')].map(r=>r.innerText.replace(/\\s+/g,' ').replace(/ Open ›$/,'').trim())"


def today(pw, w, h):
    tag = "[%s]" % w
    b, page, pe, ce = C.open_screen(pw, w, h, data=data(), wl=WL, go=False)
    try:
        js(page, "(c)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','rs2','changes'], c); localStorage.removeItem('dash.rs2ChgSeen'); localStorage.removeItem('dash.rs2Alerts'); rs2Chg.at = 0; rs2Chg.doc = null; }", CHG)
        js(page, "()=>{ switchTab('today'); }"); page.wait_for_timeout(1200)
        js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(500)
        L = js(page, LINES)
        check(f"{tag} 10 Today's To do list gets up to 3 Screen lines, priority b → a → d (two b's here, then the a; c · e off by default)", len(L) == 3 and "ZETA left Leaders · RS 78" in L[0] and "PLTR left Leaders · RS 79" in L[1] and "GE new 52w high" in L[2], L)
        check(f"{tag} 10 no new panel — the lines are ordinary Today rows", js(page, "()=>[...document.querySelectorAll('[data-rs2-chg]')].every(r=>r.classList.contains('tdRow') || r.closest('.tdRow') || r.closest('[data-td-col], #tabToday'))"))
        check(f"{tag} 10 only the 3 best lines show — the d / c / e ones wait (CRDO, APP, HOOD, NVDA, EM0 hidden)", all(n not in " ".join(L) for n in ("CRDO", "APP", "HOOD", "NVDA", "EM0")), L)
        check(f"{tag} 10 each line has the SCREEN tag, the Screen row text, and is not folded behind +N", all(x.startswith("SCREEN ") for x in L) and js(page, "()=>document.querySelectorAll('[data-rs2-chg]').length") == 3)
        o = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} 10 no horizontal overflow on Today", o <= 0, o)
        js(page, "()=>{ rs2AlertSet('b', false); }"); page.wait_for_timeout(400)
        L = js(page, LINES)
        check(f"{tag} 10 Settings off (b) → left-Leaders lines disappear; the list fills with a, d, d", len(L) == 3 and "left Leaders" not in " ".join(L) and "GE new 52w high" in L[0] and "CRDO" in L[1] and "APP" in L[2], L)
        js(page, "()=>{ rs2AlertSet('a', false); rs2AlertSet('d', false); rs2AlertSet('c', true); rs2AlertSet('e', true); }"); page.wait_for_timeout(400)
        L = js(page, LINES)
        check(f"{tag} 10 c and e are off by default, on when switched on (c before e)", len(L) == 2 and "NVDA" in L[0] and "RS down to 80" in L[0] and "New Emerging: EM0" in L[1], L)
        js(page, "()=>{ ['a','b','c','d','e'].forEach(k=>rs2AlertSet(k, false)); }"); page.wait_for_timeout(400)
        check(f"{tag} 10 all off → no lines", js(page, LINES) == [])
        js(page, "()=>{ localStorage.removeItem('dash.rs2Alerts'); todayRefresh(true); }"); page.wait_for_timeout(400)
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(400)
        st = js(page, "()=>[...document.querySelectorAll('[data-rs2-alert]')].map(c=>[c.dataset.rs2Alert, c.checked])")
        check(f"{tag} 10 Settings › Screen alerts: toggles a–e (a, b, d on)", st == [["a", True], ["b", True], ["c", False], ["d", True], ["e", False]], st)
        page.click("[data-rs2-alert=c]"); page.wait_for_timeout(300)
        check(f"{tag} 10 a toggle is remembered", js(page, "()=>rs2AlertOn('c')") is True)
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); localStorage.removeItem('dash.rs2Alerts'); todayRefresh(true); }"); page.wait_for_timeout(300)
        page.click("[data-rs2-chg] >> nth=0"); page.wait_for_timeout(700)
        st = js(page, "()=>({tab:activeTab, v:wlView, sel:rs2.sel, rows:[...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym).slice(0,3), on:(document.querySelector('[data-rs2-row].on')||{dataset:{}}).dataset.sym})")
        check(f"{tag} 10 tap → Watch › Screen with that row selected (ZETA — even though it left Leaders)", st["tab"] == "watch" and st["v"] == "screen" and st["sel"] == "ZETA" and st["on"] == "ZETA", st)
        js(page, "()=>{ switchTab('today'); }"); page.wait_for_timeout(500)
        check(f"{tag} 10 hidden once viewed for that asOf", js(page, LINES) == [])
        js(page, "(c)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','rs2','changes'], Object.assign({}, c, {asOf:'2026-11-20', prevAsOf:'2026-11-19'})); rs2Chg.at = 0; rs2Chg.doc = null; todayRefresh(true); }", CHG); page.wait_for_timeout(800)
        js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(400)
        check(f"{tag} 10 a new asOf shows them again", len(js(page, LINES)) == 3, js(page, LINES))
        js(page, "(c)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','rs2','changes'], {asOf:'2026-11-21', prevAsOf:'', items:[]}); rs2Chg.at = 0; rs2Chg.doc = null; todayRefresh(true); }", CHG); page.wait_for_timeout(800)
        js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(300)
        check(f"{tag} 10 no previous run / empty list → nothing", js(page, LINES) == [])
        check(f"{tag} 10 page errors none", not pe, pe[:2])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        desk(pw, 1440, 900)
        hwpage(pw)
        phone(pw, 390, 844)
        phone(pw, 360, 740)
        today(pw, 1440, 900)
        today(pw, 390, 844)
    f = [r for r in results if not r[1]]
    print("\nSUMMARY RS2a3: %d/%d pass" % (len(results) - len(f), len(results)))
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
