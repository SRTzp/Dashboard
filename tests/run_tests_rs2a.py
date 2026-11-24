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
            check(f"{tag} C: NVDA row — ticker only (MV1: name moved to the tooltip) · RS 99 ↗ new high · $4.4T · $38.1B · in 6d · ✓ (no RS 4w column)", t and "NVIDIA" not in t and "99" in t and "new high" in t and "+3" not in t and "$4.4T" in t and "$38.1B" in t and "in 6d" in t and "✓" in t, t)
            check(f"{tag} C: ZETA −14% · $190M · 4 Feb · GE $1.1B", z and "−14%" in z and "$190M" in z and "4 Feb" in z and ge and "$1.1B" in ge, [z, ge])
            hdr = js(page, "()=>[...document.querySelectorAll('.rs2-th .lbl')].map(x=>x.innerText.trim().toLowerCase())")
            check(f"{tag} C: header — Ticker · Sector vs SPY · RS · from high · M.Cap · Avg $vol · Earnings (Leaders: no 3M · 1M, no RS 4w)", hdr == ["ticker", "sector vs spy", "rs · from high", "m.cap", "avg $vol", "earnings"], hdr)
            cols = js(page, "()=>{ const e = document.querySelector('[data-rs2-row][data-sym=ZETA] .rs2-rs'); const p = e.querySelector('.p'); return {g:getComputedStyle(e).gridTemplateColumns, ta:getComputedStyle(p).textAlign} }")
            check(f"{tag} C: RS cell is the 3-slot grid 24 · 16 · 64, % right-aligned", cols["g"] == "24px 16px 64px" and cols["ta"] == "right", cols)
            col = js(page, "()=>({amb:getComputedStyle(document.querySelector('[data-rs2-row][data-sym=NVDA] .c-e')).color, mut:getComputedStyle(document.querySelector('[data-rs2-row][data-sym=GE] [data-rs2-off]')).color})")
            check(f"{tag} C: earnings within 7 days amber · small % muted", col["amb"] == "rgb(154, 91, 0)" and col["mut"] == "rgb(95, 102, 114)", col)
            det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
            check(f"{tag} C: detail panel for the selected row (NVDA) — RS ← 4 wks ago · 3m/6m/9m/12m · TradingView link · On Watch", "RS 99" in det and "4 wks ago" not in det and "12M 99 · 3M 96 · 1M 90" in det and "3m +22%" in det and "12m +160%" in det and "TradingView" in det and "On Watch" in det, det)
            js(page, "()=>rs2Pick('PLTR')"); page.wait_for_timeout(200)
            det = js(page, "()=>document.querySelector('[data-rs2-det]').innerText.replace(/\\s+/g,' ')")
            check(f"{tag} C: clicking a row selects it · PLTR −8% from 52w high (182.6) · + Add to Watch", "PLTR" in det and "−8% from 52w high" in det and "182.6" in det and "12M 97 · 3M 94 · 1M 88" in det and "+ Add to Watch" in det, det)
            fall = js(page, "()=>[...document.querySelectorAll('[data-rs2-3m] b')].map(b=>getComputedStyle(b).color)")
            check(f"{tag} C: falling values amber — 12M 97 → 3M 94 → 1M 88 (3M and 1M amber, 12M ink)", fall[0] == "rgb(20, 22, 26)" and fall[1] == "rgb(154, 91, 0)" and fall[2] == "rgb(154, 91, 0)", fall)
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
        it = js(page, "()=>{ const i = wlItemOf('PLTR'); return i ? {t:i.ticker, m:i.market, lw:i.ladder_watch, ex:i.exch, ind:i.industry, trk:wl1TrkOf(i), st:wl1Status(i).label, src:i.src} : null }")
        check(f"{tag} D: + Watch on PLTR adds it to Momentum (No plan, exch NASDAQ, industry kept)", before == 0 and it and it["t"] == "PLTR" and it["trk"] == "winner" and it["lw"] is False and it["ex"] == "NASDAQ" and it["ind"] == "Software - Infrastructure" and "plan" in it["st"].lower(), it)
        src = it and it["src"] or {}
        check(f"{tag} D: it.src = {{from:'screen', preset:'leaders', r12:97, r3:94, r1:88, at}}", src.get("from") == "screen" and src.get("preset") == "leaders" and src.get("r12") == 97 and src.get("r3") == 94 and src.get("r1") == 88 and str(src.get("at", "")).startswith("20"), src)
        st = js(page, "()=>{ const b = document.querySelector('[data-rs2-row][data-sym=PLTR] [data-rs2-add]'); return {a:b.dataset.rs2Add, d:b.disabled, t:b.innerText} }")
        check(f"{tag} D: the button becomes 'Watching ✓' (a menu button since RS2a3, no longer disabled) at once", st["a"] == "done" and not st["d"] and ("Watching" in st["t"] or "✓" in st["t"]), st)
        js(page, "()=>{ wlSetView('wl'); wl1TrkSet('winner'); }"); page.wait_for_timeout(300)
        inm = js(page, "()=>[...document.querySelectorAll('[data-lr5-row]')].map(r=>r.dataset.sym)")
        check(f"{tag} D: PLTR is now on the Momentum list (and COST stays Compounder)", "PLTR" in inm and "NVDA" in inm, inm)
        js(page, "()=>wlSetView('screen')"); page.wait_for_timeout(400)
        # ---- Filter ▾ (RS min · % from high · new high only · sector · min $vol)
        js(page, "()=>rs2Set('rsMin', 90)"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: Filter RS min 90 → the 8 mockup rows + PB0", o[:8] == ["NVDA", "ZETA", "PLTR", "APP", "CRDO", "HOOD", "GE", "RKLB"] and len(o) == 9, o)
        js(page, "()=>{ rs2Set('rsMin', 0); rs2Set('near', 10); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: Filter within 10% drops ZETA (−14%) · APP (−11%) · HOOD (−12%)", "ZETA" not in o and "APP" not in o and "HOOD" not in o and "NVDA" in o and "GE" in o, o[:12])
        js(page, "()=>{ rs2Reset(); rs2Set('nh'); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: new high only → NVDA · CRDO", o == ["NVDA", "CRDO"], o)
        js(page, "()=>{ rs2Reset(); rs2Set('sector', 'Industrials'); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: sector filter → Industrials only (GE · RKLB · fillers)", o[:2] == ["GE", "RKLB"] and all(js(page, "(s)=>rs2.rows.find(r=>r.t===s).s", s) == "Industrials" for s in o), o[:6])
        js(page, "()=>{ rs2Reset(); rs2Set('vol', 250); }"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} E: min $vol ≥ $250M → names with ≥ $250M only", o == ["NVDA", "PLTR", "APP", "CRDO", "HOOD", "GE", "RKLB"], o)
        js(page, "()=>{ rs2Reset(); rs2Find('hood'); }"); page.wait_for_timeout(200)
        check(f"{tag} E: search 'hood' → HOOD", js(page, ROWS) == ["HOOD"], js(page, ROWS))
        js(page, "()=>{ rs2Find('zzzz'); }"); page.wait_for_timeout(200)
        check(f"{tag} E: no match → message + reset link", js(page, "()=>!!document.querySelector('[data-rs2-clear]')") and not js(page, ROWS))
        js(page, "()=>{ rs2Reset(); }"); page.wait_for_timeout(200)
        check(f"{tag} E: Reset returns to Leaders · no filters · 86", js(page, "()=>document.querySelector('[data-rs2-sum]').innerText").count("86") == 1 and js(page, "()=>rs2.preset") == "leaders")
        # ---- presets
        js(page, "()=>rs2Set('preset', 'emerging')"); page.wait_for_timeout(250)
        o = js(page, ROWS)
        check(f"{tag} P: Emerging (3M ≥ 90 · 1M ≥ 90 · 12M < 85) → the 10 EM rows, best RS first", len(o) == 10 and all(x.startswith("EM") for x in o) and o[0] == "EM9", o)
        sm = js(page, "()=>document.querySelector('[data-rs2-sum]').innerText.replace(/\\s+/g,' ').trim()")
        check(f"{tag} P: header count follows the preset (10 match)", "10" in sm, sm)
        note = js(page, "()=>document.querySelector('[data-rs2-note]').innerText")
        check(f"{tag} P: note names the preset rule", note.startswith("Emerging = 3M ≥ 90 and 1M ≥ 90 · 12M under 85"), note)
        if desk:
            hdr = js(page, "()=>[...document.querySelectorAll('.rs2-th .lbl')].map(x=>x.innerText.trim().toLowerCase())")
            check(f"{tag} P: Emerging adds the '3M · 1M' column after RS · from high", hdr == ["ticker", "sector vs spy", "rs · from high", "3m · 1m", "m.cap", "avg $vol", "earnings", ""][:len(hdr)] and "3m · 1m" in hdr, hdr)
            m = js(page, "()=>document.querySelector('[data-rs2-row][data-sym=EM9] [data-rs2-m]').innerText.trim()")
            check(f"{tag} P: EM9 3M · 1M cell = '90 · 92'", m == "90 · 92", m)
            e0 = js(page, TXT, "EM0")
            check(f"{tag} P: earnings from the weekly cache (nx) → 'in 3d' amber", e0 and "in 3d" in e0, e0)
            ov = js(page, "()=>{ const t = document.querySelector('.lr5-list'); return t.scrollWidth - t.clientWidth }")
            check(f"{tag} P: with the extra column the table still fits", ov <= 1, ov)
        else:
            t = js(page, TXT, "EM9")
            check(f"{tag} P: phone line 2 ends '3M 90 · 1M 92' in Emerging", t and t.endswith("3M 90 · 1M 92"), t)
        js(page, "()=>rs2Set('preset', 'pullback')"); page.wait_for_timeout(250)
        o = js(page, ROWS)
        check(f"{tag} P: Pullback (12M ≥ 85 · 3M ≥ 80 · 1M < 60 · within 15%) → PB0..PB5", sorted(o) == ["PB%d" % i for i in range(6)], o)
        if not desk:
            t = js(page, TXT, "PB0")
            check(f"{tag} P: phone line 2 ends '3M 82 · 1M 40' in Pullback", t and t.endswith("3M 82 · 1M 40"), t)
        js(page, "()=>rs2Set('preset', 'leaders')"); page.wait_for_timeout(250)
        t = js(page, TXT, "PLTR")
        check(f"{tag} P: back on Leaders — no 3M · 1M text on the row", t and "3M" not in t and "1M" not in t, t)
        js(page, "()=>localStorage.setItem('dash.rs2Presets', JSON.stringify({emerging:{m3Min:99, m1Min:99}}))")
        ov = js(page, "()=>{ const p = rs2Presets(); return [p.emerging.m3Min, p.emerging.rs12Max, p.leaders.rs12Min, rs2PresetText('emerging')] }")
        check(f"{tag} P: thresholds are settings — localStorage override changes Emerging only", ov[0] == 99 and ov[1] == 85 and ov[2] == 80 and ov[3].startswith("3M ≥ 99 and 1M ≥ 99"), ov)
        js(page, "()=>localStorage.removeItem('dash.rs2Presets')")
        # ---- Filter panel UI
        js(page, "()=>{ rs2.fOpen = false; renderWatchlist(); }")
        pre = js(page, "()=>[...document.querySelectorAll('[data-rs2-presets] button')].map(b=>b.innerText.trim() + ':' + b.getAttribute('aria-selected'))")
        check(f"{tag} H: segmented preset control Leaders (selected) · Emerging · Pullback", pre == ["Leaders:true", "Emerging:false", "Pullback:false"], pre)
        if desk:
            fb = js(page, "()=>({f:document.querySelector('[data-rs2-filter-btn]').innerText.trim(), r:document.querySelector('[data-rs2-reset]').innerText.trim(), chips:document.querySelectorAll('.rs2-chip').length})")
            check(f"{tag} H: 'Filter ▾' + 'Reset' next to the presets (no chip row)", fb["f"] == "Filter ▾" and fb["r"] == "Reset" and fb["chips"] == 0, fb)
            page.click("[data-rs2-filter-btn]"); page.wait_for_timeout(250)
        else:
            page.click("[data-rs2-more-filters]"); page.wait_for_timeout(250)
        fp = js(page, "()=>[...document.querySelectorAll('[data-rs2-filter-panel] [data-rs2-f]')].map(e=>e.dataset.rs2F)")
        check(f"{tag} H: the Filter panel holds RS min · % from high · new high only · sector · industry (RS2b) · min $vol", fp == ["rsMin", "near", "nh", "sector", "ind", "vol", "mcMin"], fp)
        page.select_option("[data-rs2-f=rsMin]", "90"); page.wait_for_timeout(250)
        check(f"{tag} H: changing a filter in the panel applies it (9 rows) and the button shows the count", len(js(page, ROWS)) == 9 and js(page, "()=>!!document.querySelector('[data-rs2-filter-panel]')"), js(page, ROWS))
        js(page, "()=>rs2Reset()"); js(page, "()=>{ rs2.fOpen = false; renderWatchlist(); }")
        # ---- sorts
        js(page, "()=>rs2Set('sort', 'high')"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} F: Closest to high — NVDA / CRDO (0%) first", o[:2] == ["NVDA", "CRDO"] or set(o[:2]) == {"NVDA", "CRDO"}, o[:5])
        js(page, "()=>rs2Set('sort', 'vol')"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} F: Avg $vol — NVDA ($38.1B) first, PLTR second", o[:2] == ["NVDA", "PLTR"], o[:4])
        js(page, "()=>rs2Set('sort', 'rs')"); page.wait_for_timeout(200)
        o = js(page, ROWS)
        check(f"{tag} F: RS high first — 99s first, then 97", o[:2] == ["NVDA", "ZETA"] and o[2] == "PLTR", o[:4])
        js(page, "()=>{ rs2Set('sort', 'nearhigh'); }")
        # ---- show more
        js(page, "()=>rs2More()"); page.wait_for_timeout(250)
        check(f"{tag} G: Show more → all 86 rows, no more button", len(js(page, ROWS)) == 86 and not js(page, "()=>!!document.querySelector('[data-rs2-more]')"))
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
        check(f"{tag} J: back to Momentum — only Momentum selected; Ideas tab still works", on == ["false", "true", "false", "false"], on)
        js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(250)
        on = js(page, "()=>[...document.querySelectorAll('[data-wl1-segs] [role=tab]')].map(t=>t.getAttribute('aria-selected'))")
        check(f"{tag} J: Ideas selected alone", on == ["true", "false", "false", "false"], on)
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
        r["o"] = None; r["p"] = None; r["l"] = ""; r["a3"] = None; r["m3"] = None; r["m1"] = None
    rows[6].pop("s"); rows[6].pop("i"); rows[7]["n"] = ""
    b, page, pe, ce = C.open_screen(pw, 1440, 900, data=rows)
    try:
        html = js(page, "()=>rs2.rows.filter(r=>r.t==='APP' || r.t==='CRDO').map(r=>rs2RowHtml(r)).join('') + rs2DetHtml(rs2.rows.find(r=>r.t==='APP'))")
        check(f"{tag} M: missing offHigh / line / 3M / 1M → no 'NaN' / 'undefined' in rows or detail", "NaN" not in html and "undefined" not in html and "null" not in html.replace("onclick", ""), html[:200])
        t2 = js(page, TXT, rows[6]["t"])
        check(f"{tag} M: missing sector / name → row still renders", t2 and "undefined" not in t2, t2)
        check(f"{tag} M: Leaders excludes rows without offHigh", "APP" not in js(page, ROWS))
        js(page, "()=>rs2Set('preset', 'emerging')"); page.wait_for_timeout(200)
        check(f"{tag} M: Emerging with rows lacking 3M/1M → empty list message, no crash", js(page, "()=>!!document.querySelector('[data-rs2-state=nomatch]')") and not pe, pe[:3])
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
