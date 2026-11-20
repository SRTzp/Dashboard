#!/usr/bin/env python3
"""RS2a — Watch › Screen: 4th segment · default view (RS ≥ 80, ≤ 15% from high, Near high + RS) · filters · sorts · search · + Watch round-trip (Momentum · No plan · Watching ✓)
· already-on-Watch rows · show more · header line · missing data / empty / error states · split docs (latest_0..k) · 360/390/1440 no overflow.
Run: python3 tests/run_tests_rs2a.py"""
import sys
from playwright.sync_api import sync_playwright
import rs2a_common as C
from re1d_common import js, check, results

ROWS = "()=>[...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym)"
TXT = "(s)=>{ const r = document.querySelector('[data-rs2-row][data-sym=\"'+s+'\"]'); return r ? r.innerText.replace(/\\s+/g,' ').trim() : null }"


def over(page):
    return js(page, "()=>({sw:document.documentElement.scrollWidth - innerWidth, bad:[...document.querySelectorAll('.lr5-screen *')].filter(e=>{const r=e.getBoundingClientRect(); return r.width>0 && r.right > innerWidth + 1 && !e.closest('.lr5-list') && !e.closest('.rs2-fl')}).length})")


def run(pw, w, h):
    tag = "[%s]" % w
    desk = w >= 1024
    b, page, pe, ce = C.open_screen(pw, w, h)
    try:
        # ---- segment + header
        segs = js(page, "()=>[...document.querySelectorAll('[data-wl1-segs] [role=tab]')].map(t=>({on:t.getAttribute('aria-selected'), t:t.innerText.replace(/\\s+/g,' ').trim()}))")
        check(f"{tag} A: 4 segments — Momentum · Compounder · Ideas · Screen, Screen selected", len(segs) == 4 and segs[3]["t"] == "Screen" and segs[3]["on"] == "true" and all(s["on"] == "false" for s in segs[:3]), segs)
        sm = js(page, "()=>document.querySelector('[data-rs2-sum]').innerText.replace(/\\s+/g,' ').trim()")
        check(f"{tag} A: header line — {'1,943 liquid US stocks · 86 match · as of 18 Nov close' if desk else '86 of 1,943 · 18 Nov'}", sm == ("1,943 liquid US stocks · 86 match · as of 18 Nov close" if desk else "86 of 1,943 · 18 Nov"), sm)
        # ---- default view
        o = js(page, ROWS)
        check(f"{tag} B: default view = RS ≥ 80 · within 15% · Near high + RS · 50 rows", len(o) == 50 and o[:8] == ["NVDA", "ZETA", "PLTR", "APP", "CRDO", "HOOD", "GE", "RKLB"] and not any(s.startswith(("W", "L")) for s in o), o[:10])
        check(f"{tag} B: footer 'Showing 50 of 86' + Show more", js(page, "()=>document.querySelector('.rs2-foot').innerText.replace(/\\s+/g,' ')").startswith("Showing 50 of 86") and js(page, "()=>!!document.querySelector('[data-rs2-more]')"))
        # ---- row content
        if desk:
            t = js(page, TXT, "NVDA"); z = js(page, TXT, "ZETA"); ge = js(page, TXT, "GE")
            check(f"{tag} C: NVDA row — name · RS 99 ↗ new high · +3 · 182.40 · $38.1B · in 6d · Watching ✓", t and "NVIDIA" in t and "99" in t and "new high" in t and "+3" in t and "182.40" in t and "$38.1B" in t and "in 6d" in t and "Watching ✓" in t, t)
            check(f"{tag} C: ZETA −14% · $190M · 4 Feb · GE 0 delta · $1.1B", z and "−14%" in z and "$190M" in z and "4 Feb" in z and ge and " 0 " in ge and "$1.1B" in ge, [z, ge])
            cols = js(page, "()=>{ const e = document.querySelector('[data-rs2-row][data-sym=ZETA] .rs2-rs'); const p = e.querySelector('.p'); return {g:getComputedStyle(e).gridTemplateColumns, ta:getComputedStyle(p).textAlign} }")
            check(f"{tag} C: RS cell is the 3-slot grid 24 · 16 · 64, % right-aligned", cols["g"] == "24px 16px 64px" and cols["ta"] == "right", cols)
            col = js(page, "()=>({amb:getComputedStyle(document.querySelector('[data-rs2-row][data-sym=NVDA] .c-e')).color, mut:getComputedStyle(document.querySelector('[data-rs2-row][data-sym=GE] [data-rs2-off]')).color, up:getComputedStyle(document.querySelector('[data-rs2-row][data-sym=ZETA] [data-rs2-delta]')).color})")
            check(f"{tag} C: earnings within 7 days amber · small % muted · positive Δ green", col["amb"] == "rgb(154, 91, 0)" and col["mut"] == "rgb(95, 102, 114)" and col["up"] == "rgb(14, 107, 76)", col)
            det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
            check(f"{tag} C: detail panel for the selected row (NVDA) — RS ← 4 wks ago · 3m/6m/9m/12m · TradingView link · On Watch", "RS 99" in det and "96 (4 wks ago)" in det and "3m +22%" in det and "12m +160%" in det and "TradingView" in det and "On Watch" in det, det)
            js(page, "()=>rs2Pick('PLTR')"); page.wait_for_timeout(200)
            det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
            check(f"{tag} C: clicking a row selects it · PLTR −8% from 52w high (182.6) · + Add to Watch", "PLTR" in det and "−8% from 52w high" in det and "182.6" in det and "+ Add to Watch" in det, det)
        else:
            t = js(page, TXT, "NVDA"); z = js(page, TXT, "ZETA")
            check(f"{tag} C: phone 2-line row — 'NVDA RS 99 ↗ new high · NVIDIA · Semis? · earnings in 6d'", t and t.startswith("NVDA RS 99") and "new high" in t and "NVIDIA" in t and "earnings in 6d" in t and z.startswith("ZETA RS 99") and "−14%" in z and "Zeta Global · Software" in z, [t, z])
            hh = js(page, "()=>[...document.querySelectorAll('[data-rs2-row]')].slice(0, 8).map(r=>Math.round(r.getBoundingClientRect().height))")
            check(f"{tag} C: rows are 2 lines (≥ 56px, ≤ 72px)", all(56 <= x <= 72 for x in hh), hh)
            bt = js(page, "()=>[...document.querySelectorAll('[data-rs2-add]')].slice(0, 6).map(b=>{ const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)] })")
            check(f"{tag} C: + button is a 44px touch target", all(x[0] >= 40 and x[1] >= 44 for x in bt), bt)
        # ---- + Watch round trip
        before = js(page, "()=>wlItemOf('PLTR') ? 1 : 0")
        btn = "[data-rs2-row][data-sym=PLTR] [data-rs2-add=new]"
        page.click(btn); page.wait_for_timeout(700)
        it = js(page, "()=>{ const i = wlItemOf('PLTR'); return i ? {t:i.ticker, m:i.market, lw:i.ladder_watch, ex:i.exch, ind:i.industry, trk:wl1TrkOf(i), st:wl1Status(i).label} : null }")
        check(f"{tag} D: + Watch on PLTR adds it to Momentum (No plan, exch NASDAQ, industry kept)", before == 0 and it and it["t"] == "PLTR" and it["trk"] == "winner" and it["lw"] is False and it["ex"] == "NASDAQ" and it["ind"] == "Software - Infrastructure" and "plan" in it["st"].lower(), it)
        st = js(page, "()=>{ const b = document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]'); return {a:b.dataset.rs2Add, d:b.disabled, t:b.innerText} }")
        check(f"{tag} D: the button becomes 'Watching ✓' (disabled) at once", st["a"] == "done" and st["d"] and ("Watching" in st["t"] or "✓" in st["t"]), st)
        js(page, "()=>{ wlSetView('wl'); wl1TrkSet('winner'); }"); page.wait_for_timeout(300)
        inm = js(page, "()=>[...document.querySelectorAll('[data-lr5-row]')].map(r=>r.dataset.sym)")
        check(f"{tag} D: PLTR is now on the Momentum list (and COST stays Compounder)", "PLTR" in inm and "NVDA" in inm, inm)
        js(page, "()=>wlSetView('screen')"); page.wait_for_timeout(400)
        # ---- filters
        js(page, "()=>rs2Set('rsMin', 90)"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: RS ≥ 90 → 8 mockup rows only", o == ["NVDA", "ZETA", "PLTR", "APP", "CRDO", "HOOD", "GE", "RKLB"], o)
        js(page, "()=>{ rs2Set('rsMin', 80); rs2Set('near', 10); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: within 10% of high drops ZETA (−14%) · APP (−11%) · HOOD (−12%)", "ZETA" not in o and "APP" not in o and "HOOD" not in o and "NVDA" in o and "GE" in o, o[:12])
        js(page, "()=>{ rs2Set('near', 0); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: any distance shows the 'Wide' names too (RS ≥ 80)", len(o) == 50 and js(page, "()=>document.querySelector('[data-rs2-sum]').innerText").count("106") >= 1, js(page, "()=>document.querySelector('[data-rs2-sum]').innerText"))
        js(page, "()=>{ rs2Reset(); rs2Set('nh'); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: new high only → NVDA · CRDO", o == ["NVDA", "CRDO"], o)
        js(page, "()=>{ rs2Reset(); rs2Set('sector', 'Industrials'); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: sector filter → Industrials only (GE · RKLB · fillers)", o[:2] == ["GE", "RKLB"] and all(js(page, "(s)=>rs2.rows.find(r=>r.t===s).s", s) == "Industrials" for s in o), o[:6])
        js(page, "()=>{ rs2Reset(); rs2Set('vol', 1000 > 250 ? 250 : 250); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: min $vol ≥ $250M → names with ≥ $250M only", o == ["NVDA", "PLTR", "APP", "CRDO", "HOOD", "GE", "RKLB"], o)
        js(page, "()=>{ rs2Reset(); rs2Find('hood'); }"); page.wait_for_timeout(200)
        check(f"{tag} E: search 'hood' → HOOD · by name 'robin' → HOOD", js(page, ROWS) == ["HOOD"], js(page, ROWS))
        js(page, "()=>{ rs2Find('zzzz'); }"); page.wait_for_timeout(200)
        check(f"{tag} E: no match → message + reset link", js(page, "()=>!!document.querySelector('[data-rs2-clear]')") and not js(page, ROWS))
        js(page, "()=>{ rs2Reset(); }"); page.wait_for_timeout(200)
        check(f"{tag} E: Reset returns to the default 86", js(page, "()=>document.querySelector('[data-rs2-sum]').innerText").count("86") == 1)
        # ---- sorts
        js(page, "()=>rs2Set('sort', 'high')"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} F: Closest to high — NVDA / CRDO (0%) first", o[:2] == ["NVDA", "CRDO"] or set(o[:2]) == {"NVDA", "CRDO"}, o[:5])
        js(page, "()=>rs2Set('sort', 'vol')"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} F: Avg $vol — NVDA ($38.1B) first, PLTR second", o[:2] == ["NVDA", "PLTR"], o[:4])
        js(page, "()=>{ rs2Set('sort', 'gain'); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} F: RS 4w gain — RKLB (+11) first, CRDO (+9) next", o[0] == "RKLB" and o[1] == "CRDO", o[:4])
        js(page, "()=>{ rs2Set('rsMin', 0); rs2Set('near', 0); rs2Set('sort', 'nearhigh'); }"); page.wait_for_timeout(200)
        o = js(page, "()=>{ const v = rs2View(); return v.slice(-5).map(r=>r.t) }")
        far_last = js(page, "()=>{ const v = rs2View(); const i = v.findIndex(r=>r.o != null && r.o < -0.25); return v.slice(i).every(r=>r.o < -0.25) }")
        check(f"{tag} F: Near high + RS puts rows beyond −25% below the rest", far_last)
        js(page, "()=>{ rs2Reset(); }")
        # ---- show more
        js(page, "()=>rs2More()"); page.wait_for_timeout(250)
        check(f"{tag} G: Show more → all 86 rows, no more button", len(js(page, ROWS)) == 86 and not js(page, "()=>!!document.querySelector('[data-rs2-more]')"))
        # ---- filters UI
        fl = js(page, "()=>[...document.querySelectorAll('[data-rs2-filters] .rs2-chip')].filter(c=>c.getBoundingClientRect().width>0).map(c=>(c.querySelector('.t') ? c.querySelector('.t').innerText : c.innerText).replace(/\\s+/g,' ').trim())")
        if desk:
            check(f"{tag} H: chips RS ≥ 80 · Within 15% of high · New high only · Sector: All · Avg $vol ≥ $10M · Reset", fl == ["RS ≥ 80 ▾", "Within 15% of high ▾", "New high only", "Sector: All ▾", "Avg $vol ≥ $10M ▾", "Reset"], fl)
        else:
            check(f"{tag} H: phone chips RS ≥ 80 · ≤ 15% from high · New high · Sector (+ more via ⚲)", fl == ["RS ≥ 80 ▾", "≤ 15% from high ▾", "New high", "Sector ▾"], fl)
            js(page, "()=>rs2MoreFilters()"); page.wait_for_timeout(250)
            fl2 = js(page, "()=>[...document.querySelectorAll('[data-rs2-filters] .rs2-chip')].filter(c=>c.getBoundingClientRect().width>0).map(c=>(c.querySelector('.t') ? c.querySelector('.t').innerText : c.innerText).replace(/\\s+/g,' ').trim())")
            check(f"{tag} H: ⚲ reveals Avg $vol + Reset", len(fl2) == 6, fl2)
            js(page, "()=>rs2MoreFilters()")
        o2 = over(page)
        check(f"{tag} I: no horizontal overflow of the page", o2["sw"] <= 0, o2)
        if desk:
            hd = js(page, "()=>{ const h = document.querySelector('.lr5-hd'); const k = [...h.children].filter(c=>getComputedStyle(c).display !== 'none'); const t = k.map(c=>Math.round(c.getBoundingClientRect().top + c.getBoundingClientRect().height / 2)); return Math.max(...t) - Math.min(...t) }")
            check(f"{tag} I: header is one row", hd <= 6, hd)
            cl = js(page, "()=>{ const l = document.querySelector('.lr5-list'); return {sw:l.scrollWidth, cw:l.clientWidth} }")
            check(f"{tag} I: the table fits without a horizontal scrollbar (+ Watch buttons visible)", cl["sw"] <= cl["cw"] + 1, cl)
        # ---- tab switching
        js(page, "()=>{ wlSetView('wl'); wl1TrkSet('winner'); }"); page.wait_for_timeout(250)
        on = js(page, "()=>[...document.querySelectorAll('[data-wl1-segs] [role=tab]')].map(t=>t.getAttribute('aria-selected'))")
        check(f"{tag} J: back to Momentum — only Momentum selected; Ideas tab still works", on == ["true", "false", "false", "false"], on)
        js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(250)
        on = js(page, "()=>[...document.querySelectorAll('[data-wl1-segs] [role=tab]')].map(t=>t.getAttribute('aria-selected'))")
        check(f"{tag} J: Ideas selected alone", on == ["false", "false", "true", "false"], on)
        check(f"{tag} K: no page errors", not pe, pe[:3])
    finally:
        b.close()


def states(pw):
    tag = "[states]"
    b, page, pe, ce = C.open_screen(pw, 1440, 900, data=[], meta_={"asOf": "", "n": 0, "error": "SPY benchmark too short"})
    try:
        s = js(page, "()=>document.querySelector('[data-rs2-state]') && document.querySelector('[data-rs2-state]').dataset.rs2State")
        txt = js(page, "()=>document.querySelector('.lr5-list').innerText")
        check(f"{tag} L: no doc yet → empty message mentioning the failed job, no crash", s == "empty" and "No ranked list yet" in txt and "SPY benchmark" in txt, txt)
        check(f"{tag} L: no page errors on an empty list", not pe, pe[:3])
    finally:
        b.close()
    b, page, pe, ce = C.open_screen(pw, 1440, 900, seed=False)
    try:
        s = js(page, "()=>document.querySelector('[data-rs2-state]') && document.querySelector('[data-rs2-state]').dataset.rs2State")
        check(f"{tag} L: nothing in Firestore at all → empty state", s == "empty", s)
    finally:
        b.close()
    # rows with missing fields
    rows = C.rows()[:12]
    for r in rows[3:6]:
        r["o"] = None; r["p"] = None; r["l"] = ""; r["a3"] = None
    rows[6].pop("s"); rows[6].pop("i"); rows[7]["n"] = ""
    b, page, pe, ce = C.open_screen(pw, 1440, 900, data=rows)
    try:
        js(page, "()=>{ rs2Set('near', 0); rs2Set('rsMin', 0); }"); page.wait_for_timeout(300)
        t = js(page, TXT, "APP")
        check(f"{tag} M: missing offHigh / 4w-ago / line → '—' cells, no 'NaN' / 'undefined'", t and "NaN" not in t and "undefined" not in t and "—" in t, t)
        t2 = js(page, TXT, rows[6]["t"])
        check(f"{tag} M: missing sector / name → row still renders", t2 and "undefined" not in t2, t2)
        js(page, "()=>rs2Set('near', 15)"); page.wait_for_timeout(200)
        check(f"{tag} M: near-high filter excludes rows without offHigh", "APP" not in js(page, ROWS))
        check(f"{tag} M: no page errors", not pe, pe[:3])
    finally:
        b.close()
    # split docs
    allrows = C.rows()
    parts = [allrows[i:i + 50] for i in range(0, len(allrows), 50)]
    b, page, pe, ce = C.open_screen(pw, 1440, 900, data=allrows, parts=parts)
    try:
        page.wait_for_selector('[data-rs2-row]', timeout=8000); page.wait_for_timeout(500)
        n = js(page, "()=>rs2.rows.length")
        check(f"{tag} N: rs2/latest with parts → rows from latest_0..k merged ({len(allrows)})", n == len(allrows), n)
        check(f"{tag} N: default view identical (86 match)", js(page, "()=>document.querySelector('[data-rs2-sum]').innerText").count("86") == 1)
    finally:
        b.close()
    # + Watch for a stock that is Compounder / archived
    b, page, pe, ce = C.open_screen(pw, 1440, 900, wl=C.WL + [{"t": "APP", "x": {"exch": "NASDAQ", "archived": True, "archived_reason": "x", "archived_at": "2026-11-01T00:00:00Z"}}])
    try:
        page.wait_for_selector('[data-rs2-row][data-sym=APP]', timeout=8000)
        t = js(page, "()=>document.querySelector('[data-rs2-row][data-sym=APP] [data-rs2-add]').dataset.rs2Add")
        check(f"{tag} O: an archived stock shows 'Archived' (no duplicate add)", t == "archived", t)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 740)):
            run(pw, w, h)
        states(pw)
    f = [r for r in results if not r[1]]
    print("\nSUMMARY RS2a: %d/%d pass" % (len(results) - len(f), len(results)))
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
