#!/usr/bin/env python3
"""MV1 — A Move to Compounder / Move to Momentum (⋯ menu) · B Screen desktop without the Company column + short-name tooltip · C one dark button per area (docs/briefs/MV1-brief.md).
Run: python3 tests/run_tests_mv1.py   (MV1_SHOTS=1 writes docs/screenshots/mv1-*.png)"""
import sys, os
from playwright.sync_api import sync_playwright
from re1d_common import js, check, results
import lr5_common as C
import rs2a_common as R

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")


def shot(page, name, **kw):
    if os.environ.get("MV1_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); page.wait_for_timeout(120); page.screenshot(path=os.path.join(SHOTS, "mv1-%s.png" % name), **kw)


def watch(pw, w, h=900):
    b, page, pe = C.open_watch(pw, w, h)
    js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(500)
    return b, page, pe


def trk(page, s): return js(page, "(s)=>wl1TrkOf(wlItemOf(s))", s)
def menu(page, s):
    js(page, "(s)=>{ wlOpen(s, ''); ltMenuToggle(s); }", s); page.wait_for_timeout(250)
def mv(page): return js(page, "()=>{ const e = document.querySelector('[data-lr5-det] [data-mv1-move]'); return e ? {t:e.innerText.replace(/\\s+/g,' ').trim(), off:e.getAttribute('aria-disabled') === 'true', why:e.dataset.mv1Off || '', to:e.dataset.mv1Move} : null; }")
def toast(page): return js(page, "()=>{ const e = document.querySelector('[data-ux3-toast]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : ''; }")
def doc(page, s): return js(page, "(s)=>wlCol().doc(s).get().then(d=>d.data())", s)


def part_a(pw, w):
    tag = "[A %d]" % w
    b, page, pe = watch(pw, w)
    try:
        # seed: GE gets Focus + a note; AVGO is Planned, AAPL Holding; BRK pair for the duplicate rule
        js(page, "()=>{ const col = wlCol(); col.doc('GE').update({focus:true, note:'keep me'}); col.doc('BRK-B').set({ticker:'BRK-B', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', exch:'NYSE'}); col.doc('BRK.B').set({ticker:'BRK.B', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', exch:'NYSE', ladder_watch:true, ladder_watch_set:true}); }"); page.wait_for_timeout(500)
        menu(page, "GE")
        m = mv(page)
        check(f"{tag} 1 Momentum No-plan stock: item 'Move to Compounder' + 'Keeps notes, homework and alerts'", m and m["t"] == "Move to Compounder Keeps notes, homework and alerts" and not m["off"], m)
        order = js(page, "()=>[...document.querySelectorAll('[data-lr5-det] .ltMenu > *')].map(e=>e.getAttribute('role') === 'separator' ? '|' : (e.innerText || '').split('\\n')[0].trim())")
        ie, im, ia = order.index("Edit"), order.index("Move to Compounder"), order.index("Archive…")
        check(f"{tag} 1 order: Edit → Move to … → … → divider → Archive (Remove)", ie < im < ia and order[ia - 1] == "|", order)
        if w <= 600:
            g = js(page, "()=>{ const e = document.querySelector('[data-lr5-det] .ltMenu'), r = e.getBoundingClientRect(); return {pos:getComputedStyle(e).position, bottom:Math.round(window.innerHeight - r.bottom), w:Math.round(r.width), rows:[...e.querySelectorAll('[role=menuitem]')].map(x=>Math.round(x.getBoundingClientRect().height))}; }")
            check(f"{tag} 1 phone: ⋯ is a bottom sheet, full width, every row >= 44px", g["pos"] == "fixed" and g["bottom"] <= 1 and g["w"] >= w - 2 and min(g["rows"]) >= 44, g)
            shot(page, "move-menu-390", full_page=False)
        else:
            shot(page, "move-menu", full_page=False)
        # blocked rows
        for s, why in (("AAPL", "Holding"), ("AVGO", "Planned")):
            menu(page, s); m = mv(page)
            check(f"{tag} 2 {why} ({s}): grey, not clickable, 'Has a plan · change it in Plan ›'", m and m["off"] and m["why"] == "plan" and m["t"] == "Move to Compounder Has a plan · change it in Plan ›", m)
            js(page, "()=>document.querySelector('[data-lr5-det] [data-mv1-move]').click()"); page.wait_for_timeout(200)
            check(f"{tag} 2 {s}: clicking the grey item changes nothing", trk(page, s) == "winner" and not toast(page))
            if s == "AVGO":
                if w <= 600: shot(page, "move-blocked-390", full_page=False)
                menu(page, s) if not js(page, "()=>!!document.querySelector('[data-lr5-det] [data-mv1-plan]')") else None
                js(page, "()=>document.querySelector('[data-lr5-det] [data-mv1-plan]').click()"); page.wait_for_timeout(500)
                check(f"{tag} 2 'Plan ›' opens that stock's plan (Plan tab)", js(page, "()=>activeTab") == "plan", js(page, "()=>activeTab"))
                js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(400)
        # duplicate
        menu(page, "BRK-B"); m = mv(page)
        check(f"{tag} 3 ticker already in Compounder → grey 'Already in Compounder'", m and m["off"] and m["why"] == "dup" and m["t"].endswith("Already in Compounder"), m)
        # move GE
        js(page, "()=>wlOpen('GE', '')"); page.wait_for_timeout(200)
        before = js(page, "()=>wlRowsView().rows.map(r=>r.sym)"); i = before.index("GE"); exp = before[i + 1] if i + 1 < len(before) else before[i - 1]
        menu(page, "GE")
        js(page, "()=>document.querySelector('[data-lr5-det] [data-mv1-move]').click()"); page.wait_for_timeout(500)
        d = doc(page, "GE")
        check(f"{tag} 4 one tap, no confirm: GE is Compounder now (one field + movedAt)", trk(page, "GE") == "ladder" and d.get("ladder_watch") is True and isinstance(d.get("movedAt"), str) and len(d["movedAt"]) > 10, d)
        check(f"{tag} 4 toast 'Moved GE to Compounder · Undo'", toast(page) == "Moved GE to Compounder Undo", toast(page))
        check(f"{tag} 4 no dialog opened", js(page, "()=>!document.querySelector('[data-ux3-dlg]')"))
        check(f"{tag} 4 stays on Momentum and selects the next row ({exp})", js(page, "()=>wl1Trk") == "winner" and js(page, "()=>wlSel") == exp, [js(page, "()=>wlSel"), exp])
        check(f"{tag} 4 GE left the Momentum list", "GE" not in js(page, "()=>wlRowsView().rows.map(r=>r.sym)"))
        check(f"{tag} 4 Focus + note + homework survive (same doc)", d.get("focus") is True and d.get("note") == "keep me" and bool((d.get("hw") or {}).get("doneAt")) and js(page, "()=>wlItemOf('GE').focus") is True)
        if w > 600: shot(page, "move-toast", full_page=False)
        js(page, "()=>document.querySelector('[data-ux3-undo]').click()"); page.wait_for_timeout(500)
        d = doc(page, "GE")
        check(f"{tag} 5 Undo: GE is back in Momentum with Focus + note, same doc", trk(page, "GE") == "winner" and d.get("ladder_watch") is False and d.get("focus") is True and d.get("note") == "keep me" and "GE" in js(page, "()=>wlRowsView().rows.map(r=>r.sym)"), d)
        # Compounder → Momentum
        js(page, "()=>wl1TrkSet('ladder')"); page.wait_for_timeout(300)
        menu(page, "COST"); m = mv(page)
        check(f"{tag} 6 Compounder: item reads 'Move to Momentum'", m and m["t"] == "Move to Momentum Keeps notes, homework and alerts" and not m["off"], m)
        js(page, "()=>document.querySelector('[data-lr5-det] [data-mv1-move]').click()"); page.wait_for_timeout(500)
        check(f"{tag} 6 COST moved to Momentum · toast · stays on Compounder", trk(page, "COST") == "winner" and toast(page) == "Moved COST to Momentum Undo" and js(page, "()=>wl1Trk") == "ladder", toast(page))
        js(page, "()=>document.querySelector('[data-ux3-undo]').click()"); page.wait_for_timeout(400)
        check(f"{tag} 6 Undo puts COST back in Compounder", trk(page, "COST") == "ladder")
        # toast closes by itself after 6 s
        js(page, "()=>{ wl1TrkSet('winner'); }"); page.wait_for_timeout(200)
        menu(page, "PLTR"); js(page, "()=>document.querySelector('[data-lr5-det] [data-mv1-move]').click()"); page.wait_for_timeout(400)
        page.wait_for_timeout(6300)
        check(f"{tag} 7 toast is gone after 6 s", toast(page) == "", toast(page))
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def long_rows():
    rows = R.rows()
    nm = {"APP": "AppLovin Corporation Class A Common Stock", "CRDO": "Credo Technology Group Holding Ltd Ordinary Shares", "HOOD": "Robinhood Markets, Inc. Class A Common Stock", "GE": "GE Aerospace Common Stock"}
    for r in rows:
        if r["t"] in nm: r["n"] = nm[r["t"]]
    rows.append(dict(rows[0], t="CLS", n="Celestica Inc. Common Shares", i="Electronic Components", s="Technology"))
    rows.append(dict(rows[0], t="TSM", n="Taiwan Semiconductor Manufacturing Company Ltd. American Depositary Shares", i="Semiconductors", s="Technology", e="NYSE"))
    return rows


def part_b(pw):
    tag = "[B 1440]"
    b, page, pe, ce = R.open_screen(pw, 1440, 900, data=long_rows())
    try:
        names = js(page, "()=>[['AppLovin Corporation Class A Common Stock'],['Celestica Inc. Common Shares'],['Robinhood Markets, Inc. Class A Common Stock'],['Taiwan Semiconductor Manufacturing Company Ltd. American Depositary Shares'],['Credo Technology Group Holding Ltd Ordinary Shares'],['GE Aerospace Common Stock'],['NVIDIA'],['']].map(a=>rs2ShortName(a[0]))")
        check(f"{tag} 1 short names: APP · CLS · HOOD · an ADR · an 'Ordinary Shares' name · 'Common Stock' · plain · empty",
              names == ["AppLovin Corporation", "Celestica Inc.", "Robinhood Markets", "Taiwan Semiconductor Manufacturing Company Ltd.", "Credo Technology Group Holding Ltd", "GE Aerospace", "NVIDIA", ""], names)
        js(page, "()=>{ rs2.q = ''; renderWatchlist(); }"); page.wait_for_timeout(300)
        cols = js(page, "()=>{ const r = document.querySelector('[data-rs2-row]'), h = document.querySelector('[data-rs2-th-row]'); const n = e=>getComputedStyle(e).gridTemplateColumns.split(' ').length; return {row:n(r), head:n(h), nm:getComputedStyle(r.querySelector('.c-stock .nm')).display, th:[...h.children].map(c=>c.innerText.trim())}; }")
        check(f"{tag} 2 no Company column: Ticker header, name hidden, columns match header", cols["nm"] == "none" and cols["th"][1].lower() == "ticker" and cols["row"] == cols["head"], cols)
        g = js(page, "()=>{ const r = document.querySelector('[data-rs2-row]'); return [...r.children].filter(c=>getComputedStyle(c).display !== 'none' && !c.classList.contains('l2')).map(c=>Math.round(c.getBoundingClientRect().width)); }")
        check(f"{tag} 2 Ticker column is narrow (<=90px), Sector column wider than before", g[1] <= 90 and g[2] >= 112, g)
        cut = js(page, "()=>[...document.querySelectorAll('[data-rs2-row] .c-sec .sec .nm')].filter(e=>e.scrollWidth > e.clientWidth + 1).length")
        check(f"{tag} 2 sector text is not cut with '…' in any row", cut == 0, cut)
        # tooltip on hover
        for sym, exp in (("HOOD", "Robinhood Markets"), ("CLS", "Celestica Inc."), ("APP", "AppLovin Corporation")):
            js(page, "(q)=>{ rs2.q = q; renderWatchlist(); }", sym); page.wait_for_timeout(250)
            row = page.locator('[data-rs2-row][data-sym="%s"]' % sym).first
            row.hover(); page.wait_for_timeout(150)
            tip = js(page, "(s)=>{ const e = document.querySelector('[data-rs2-row][data-sym=\"'+s+'\"] .c-stock'); const c = getComputedStyle(e, '::after'); return {content:c.content, bg:c.backgroundColor}; }", sym)
            check(f"{tag} 3 hover {sym}: dark tooltip '{exp}'", tip["content"] == '"%s"' % exp and tip["bg"] == "rgb(20, 22, 26)", tip)
            if sym == "HOOD": js(page, "()=>{ rs2.q = ''; renderWatchlist(); }"); page.wait_for_timeout(250); page.locator('[data-rs2-row][data-sym="HOOD"]').first.hover(); page.wait_for_timeout(150); shot(page, "screen", full_page=False)
        # keyboard focus shows it too
        js(page, "()=>{ rs2.q = ''; renderWatchlist(); }"); page.wait_for_timeout(250)
        page.locator('[data-rs2-row][data-sym="HOOD"] input[type=checkbox]').first.focus(); page.mouse.move(5, 5); page.wait_for_timeout(120)
        c = js(page, "()=>getComputedStyle(document.querySelector('[data-rs2-row][data-sym=\"HOOD\"] .c-stock'), '::after').content")
        check(f"{tag} 3 keyboard focus on the row shows the tooltip too", c == '"Robinhood Markets"', c)
        # not shown when not hovered
        c0 = js(page, "()=>getComputedStyle(document.querySelector('[data-rs2-row][data-sym=\"APP\"] .c-stock'), '::after').content")
        check(f"{tag} 3 no tooltip on rows that are not hovered", c0 in ("none", "normal"), c0)
        # search still matches company names
        js(page, "(q)=>{ rs2.q = q; renderWatchlist(); }", "ROBINHOOD"); page.wait_for_timeout(250)
        syms = js(page, "()=>[...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym)")
        check(f"{tag} 4 search 'robinhood' still finds HOOD by company name", syms == ["HOOD"], syms)
        js(page, "()=>{ rs2.q = ''; rs2Pick('HOOD'); }"); page.wait_for_timeout(300)
        dn = js(page, "()=>{ const e = document.querySelector('[data-rs2-dname]'); return e ? e.innerText : ''; }")
        check(f"{tag} 5 stock panel header uses the short name", dn.startswith("Robinhood Markets · ") and "Class A" not in dn, dn)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()
    tag = "[B 1099]"
    b, page, pe, ce = R.open_screen(pw, 1099, 900, data=long_rows())
    try:
        d = js(page, "()=>getComputedStyle(document.querySelector('[data-rs2-row] .c-stock .nm')).display")
        check(f"{tag} below 1100 nothing changes: the name column is still there", d != "none", d)
    finally:
        b.close()
    tag = "[B 390]"
    b, page, pe, ce = R.open_screen(pw, 390, 844, data=long_rows())
    try:
        r = js(page, "()=>{ const r = document.querySelector('[data-rs2-row][data-sym=\"HOOD\"]') || document.querySelector('[data-rs2-row]'); const l2 = r.querySelector('.l2 .t'); return {cols:getComputedStyle(r).gridTemplateColumns.split(' ').length, l2:l2.innerText, after:getComputedStyle(r.querySelector('.c-stock'), '::after').content, nm:getComputedStyle(r.querySelector('.c-stock .nm')).display, th:getComputedStyle(document.querySelector('[data-rs2-th-row]')).display}; }")
        check(f"{tag} phone unchanged: 2-column row, name + industry line kept, no tooltip, header hidden", r["cols"] == 2 and "Class A" in r["l2"] and r["after"] in ("none", "normal") and r["nm"] == "none" and r["th"] == "none", r)
        check(f"{tag} no horizontal scroll", js(page, "()=>document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"))
        shot(page, "screen-390", full_page=False)
    finally:
        b.close()


def pri_audit(pw, w):
    """C — visible dark buttons per area, on the main stock screens."""
    tag = "[C %d]" % w
    COUNT = "()=>{ const vis = e=>{ const r = e.getBoundingClientRect(), cs = getComputedStyle(e); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; }; return [...document.querySelectorAll('.pri, .ui-btn-pri')].filter(vis).map(e=>(e.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 28) + '|' + (e.closest('[data-lr5-det]') ? 'detail' : e.closest('.wlList, .wlListBody') ? 'list' : 'page')); }"
    out = {}
    b, page, pe = watch(pw, w)
    try:
        for s in ("GE", "PLTR", "AAPL", "AVGO"):
            js(page, "(s)=>{ wlOpen(s, ''); }", s); page.wait_for_timeout(350)
            out["Watch detail " + s] = js(page, COUNT)
            det = [x for x in out["Watch detail " + s] if x.endswith("|detail")]
            check(f"{tag} Watch detail {s}: dark button in the panel is only 'Make plan ›' (Homework ›, Open plan › are white)", all(x.startswith("Make plan") for x in det), det)
            if s == "PLTR": shot(page, "dark-watch" + ("-390" if w <= 600 else ""), full_page=False)
        js(page, "()=>wlOpen('PLTR','')"); page.wait_for_timeout(200)
        js(page, "()=>{ wl5Full('PLTR','sum'); }"); page.wait_for_timeout(300)
        out["Watch full thesis PLTR"] = js(page, COUNT)
    finally:
        b.close()
    for k, v in out.items(): print("  C%d %s: %s" % (w, k, v))
    return out


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_a(pw, 1440); part_a(pw, 390)
        part_b(pw)
        for w in (1440, 390): pri_audit(pw, w)
    bad = [r for r in results if not r[1]]
    print("\n%d checks, %d failed" % (len(results), len(bad)))
    sys.exit(1 if bad else 0)
