#!/usr/bin/env python3
"""WL2 — Watch: RS · from high column (3-slot grid · colours · new-high chip · phone line 2) · detail RS block (+ Holdings ↗) · From living thesis + "Use this thesis ✓"
· sector auto-fill from prices industry/sector · sort "Near high + RS" · Exch? chip · old price docs (no new fields) → rating only, no errors · 360/390/1440.
Run: python3 tests/run_tests_wl2.py"""
import sys
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import wl2_common as W

RGB = {"mut": "rgb(95, 102, 114)", "ink": "rgb(20, 22, 26)", "amb": "rgb(154, 91, 0)"}
ROWS = "()=>[...document.querySelectorAll('[data-lr5-row]')].map(r=>r.dataset.sym)"


def row(page, sym, sel=""):
    return js(page, "([s,q])=>{ const r = document.querySelector('[data-lr5-row][data-sym=\"'+s+'\"]'); const e = q ? r && r.querySelector(q) : r; return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", [sym, sel])


def run(pw, w, h):
    tag = "[%s]" % w
    desk = w >= 1024
    b, page, pe = W.open_watch(pw, w, h, ideas=False)
    try:
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(500)
        o = js(page, ROWS)
        check(f"{tag} A: all Momentum rows listed", sorted(o) == sorted(["AAPL", "AMD", "AVGO", "GE", "PLTR", "MU", "GLBE", "RELY", "TEAM", "NVDA"]), o)
        # ---- D: RS cell
        cell = lambda s: row(page, s, ".c-rs") if desk else row(page, s, ".l2")
        if desk:
            exp = {"MU": "98 ↘ −42%", "AAPL": "87 ↗ new high", "GE": "91 → −6%", "RELY": "63 ↘ −21%", "AVGO": "64 ↘ −28%", "TEAM": "76 ↘", "PLTR": "—", "AMD": "—"}
            got = {s: cell(s) for s in exp}
            check(f"{tag} D: RS · from high — rating · arrow · % (new high takes the % slot; old doc → rating only; no data → —)", got == exp, got)
            cols = js(page, "()=>{ const e = document.querySelector('[data-lr5-row][data-sym=MU] .lr5-rs'); const p = e.querySelector('.p'); return {g:getComputedStyle(e).gridTemplateColumns, ta:getComputedStyle(p).textAlign, tn:getComputedStyle(e).fontVariantNumeric, w:e.getBoundingClientRect().width} }")
            check(f"{tag} D: 3-slot grid 24px · 16px · 64px, % right-aligned, tabular numbers", cols["g"] == "24px 16px 64px" and cols["ta"] == "right" and "tabular" in cols["tn"], cols)
            col = {s: js(page, "(s)=>{ const p = document.querySelector('[data-lr5-row][data-sym=\"'+s+'\"] .lr5-rs .p'); return p ? getComputedStyle(p).color : null }", s) for s in ("GE", "RELY", "MU", "GLBE")}
            check(f"{tag} D: colours — −6% muted · −21% ink · −42% / −31% amber", col["GE"] == RGB["mut"] and col["RELY"] == RGB["ink"] and col["MU"] == RGB["amb"] and col["GLBE"] == RGB["amb"], col)
            nh = js(page, "()=>{ const r = document.querySelector('[data-lr5-row][data-sym=AAPL] .lr5-rs'); const c = r.querySelector('[data-lr5-newhigh]'); const rr = r.getBoundingClientRect(), cr = c.getBoundingClientRect(); return {inside:cr.left >= rr.left - 1 && cr.right <= rr.right + 1, right:Math.abs(cr.right - rr.right) <= 1, off:!!r.querySelector('[data-lr5-off]')} }")
            check(f"{tag} D: new-high chip sits in the % slot (right-aligned, no % beside it)", nh["inside"] and nh["right"] and not nh["off"], nh)
            hdr = js(page, "()=>[...document.querySelectorAll('.lr5-th .lbl')].map(x=>x.innerText.toLowerCase())")
            check(f"{tag} D: column header 'RS · from high'", "rs · from high" in hdr, hdr)
            tw = js(page, "()=>{ const t = document.querySelector('.lr5-tbl'); const l = document.querySelector('.lr5-list'); return {sw:t.scrollWidth, cw:t.clientWidth, lw:l.clientWidth, rs:[...document.querySelectorAll('.c-rs')].every(c=>c.scrollWidth <= c.clientWidth + 1)} }")
            check(f"{tag} D: the column does not widen the table (min-width 900 unchanged · no cell clipped · nothing scrolls at 1440)", tw["sw"] <= max(tw["cw"], 900) and tw["rs"] and tw["sw"] <= tw["lw"], tw)
            lg = js(page, "()=>{ const l = document.querySelector('[data-wl2-legend]'); return l ? l.innerText.replace(/\\s+/g,' ') : null }")
            check(f"{tag} D: legend under the table (0 to −10% · −10 to −25% · beyond −25% · new high)", lg and "0 to −10%" in lg and "beyond −25%" in lg and "new high" in lg, lg)
        else:
            exp = {"MU": "RS 98 ↘ −42%", "AAPL": "RS 87 ↗ new high", "GE": "RS 91 → −6%", "TEAM": "RS 76 ↘"}
            got = {s: cell(s) for s in exp}
            check(f"{tag} D: phone line 2 ends with 'RS 98 ↘ −42%' (new high chip · old doc → rating only)", all(got[s].endswith(exp[s]) for s in exp), got)
            pos = js(page, "()=>[...document.querySelectorAll('[data-lr5-row]')].filter(r=>r.querySelector('[data-lr5-rs-phone]')).map(r=>{ const l = r.querySelector('.l2').getBoundingClientRect(), p = r.querySelector('[data-lr5-rs-phone]').getBoundingClientRect(), t = r.querySelector('.l2 .t').getBoundingClientRect(); return {s:r.dataset.sym, pin:Math.abs(l.right - p.right) <= 1, noOverlap:t.right <= p.left + 1, h:Math.round(l.height)} })")
            check(f"{tag} D: RS pinned right on line 2, left text ellipsizes, never overlaps, one line", all(x["pin"] and x["noOverlap"] and x["h"] <= 22 for x in pos), pos)
        # ---- G: Exch? chip
        ex = js(page, "()=>{ const r = document.querySelector('[data-lr5-row][data-sym=GLBE]'); const q = r.querySelector('[data-wl1-exq]'), c = r.querySelector('[data-wl1-chip]'); if(!q) return null; const a = q.getBoundingClientRect(), s = c.getBoundingClientRect(), n = r.querySelector('.wlRn').getBoundingClientRect(); return {ws:getComputedStyle(q).whiteSpace, apart:a.right <= s.left + 0.5 || a.bottom <= s.top || s.bottom <= a.top, after:a.left >= n.right - 0.5, h:Math.round(a.height), txt:q.options[0].text} }")
        check(f"{tag} G: GLBE 'Exch?' chip — nowrap, one line, after the ticker, does not overlap the status chip", ex and ex["ws"] == "nowrap" and ex["apart"] and ex["after"] and ex["txt"] == "Exch?" and ex["h"] <= 44, ex)
        # ---- F: sort
        sel = "[data-lr5-sort]"
        opts = js(page, "()=>[...document.querySelectorAll('[data-lr5-sort] option')].map(o=>o.textContent)")
        check(f"{tag} F: Sort options — Default · RS high first · Near high + RS · Next check soonest · Homework first", opts == ["Default", "RS high first", "Near high + RS", "Next check soonest", "Homework first"], opts)
        page.select_option(sel, "nearhigh"); page.wait_for_timeout(300)
        o = js(page, ROWS)
        near = ["GE", "AAPL", "TEAM", "RELY"]; nodata = [x for x in ("AMD", "PLTR", "NVDA") if x in o]; far = ["MU", "AVGO", "GLBE"]
        check(f"{tag} F: Near high + RS — by rating (GE 91 · AAPL 87 · TEAM 76 · RELY 63), unrated next, rows beyond −25% below (MU 98 · AVGO 64 · GLBE 54)", o[:4] == near and o[-3:] == far and sorted(o[4:-3]) == sorted(nodata), o)
        page.select_option(sel, "rs"); page.wait_for_timeout(250)
        o2 = js(page, ROWS)
        check(f"{tag} F: RS high first is unchanged (MU 98 first)", o2[0] == "MU", o2)
        page.select_option(sel, "default"); page.wait_for_timeout(250)
        # ---- E + B: detail
        if desk:
            js(page, "()=>wlOpen('MU')"); page.wait_for_timeout(350)
            d = js(page, "()=>{ const r = document.querySelector('[data-lr5-rsb]'); const g = q=>{ const e = r.querySelector(q); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null }; return {l1:r.firstChild.textContent + ' ' + r.querySelector('b').innerText, all:r.innerText.replace(/\\s+/g,' ').trim(), off:g('[data-lr5-off-line]'), offc:getComputedStyle(r.querySelector('[data-lr5-off-line]')).color, rets:g('[data-lr5-rets]'), sec:document.querySelector('[data-lr5-f=sector]').innerText.replace(/\\s+/g,' ').trim(), hold:(document.querySelector('[data-wl2-holdings]')||{}).href, from:(document.querySelector('[data-wl2-from]')||{innerText:''}).innerText} }")
            check(f"{tag} E: MU RS block 'RS 98 ← 99 (4 wks ago) · line ↘'", d["all"].startswith("RS 98 ← 99 (4 wks ago) · line ↘"), d["all"])
            check(f"{tag} E: '−42% from 52w high (1,255 · 18 Jun)' in amber", d["off"] == "−42% from 52w high (1,255 · 18 Jun)" and d["offc"] == RGB["amb"], d)
            check(f"{tag} E: returns '3m −7% · 6m +50% · 9m +85% · 12m +200%'", d["rets"] == "3m −7% · 6m +50% · 9m +85% · 12m +200%", d["rets"])
            check(f"{tag} E: Holdings ↗ link next to the sector (SMH holdings page)", "Holdings ↗" in d["sec"] and d["hold"] and "/smh/" in d["hold"].lower(), d)
            check(f"{tag} B: block labelled 'From living thesis'", d["from"].lower() == "from living thesis", d["from"])
        else:
            page.locator("[data-lr5-row][data-sym=MU]").click(position={"x": 20, "y": 14}); page.wait_for_timeout(400)
            t = js(page, "()=>document.querySelector('.lr5-det').innerText.replace(/\\s+/g,' ')")
            check(f"{tag} E: sheet shows RS 98 ← 99 · −42% from 52w high (1,255 · 18 Jun) · 3m … 12m · From living thesis", all(x in t for x in ("RS 98 ← 99 (4 wks ago)", "−42% from 52w high (1,255 · 18 Jun)", "3m −7% · 6m +50% · 9m +85% · 12m +200%")) and "from living thesis" in t.lower(), t)
        # Use this thesis — MU (all blank)
        use = js(page, "()=>{ const u = document.querySelector('[data-wl2-use]'); const m = document.querySelector('[data-lr5-main]'); return u ? {t:u.innerText.trim(), above:!!(u.compareDocumentPosition(m) & Node.DOCUMENT_POSITION_FOLLOWING), h:Math.round(u.getBoundingClientRect().height)} : null }")
        check(f"{tag} B: 'Use this thesis ✓' shows above the main action (44px)", use and use["t"] == "Use this thesis ✓" and use["above"] and use["h"] >= 44, use)
        pre = js(page, "()=>{ const it = wlItemOf('MU'); return {done:wl1HwDone(it), cap:wl1CapPct(it), my:wlMyThesis(it).exit, trg:(it.hw||{}).trigger||''} }")
        check(f"{tag} B: before — homework not done, cap 50%, exit/trigger blank", pre == {"done": False, "cap": 50, "my": "", "trg": ""}, pre)
        page.click("[data-wl2-use]"); page.wait_for_timeout(500)
        post = js(page, "()=>{ const it = wlItemOf('MU'), lt = wl2Lt(it); return {done:wl1HwDone(it), cap:wl1CapPct(it), exitOk:wlMyThesis(it).exit === lt.exit && !!lt.exit, trgOk:it.hw.trigger === lt.trigger && !!lt.trigger, conf:!!it.hw.confirmedAt, d:!!it.hw.doneAt, btn:!!document.querySelector('[data-wl2-use]')} }")
        check(f"{tag} B: after — wl1HwDone true · cap 100% · lt exit → my exit · lt trigger → hw.trigger · confirmedAt + doneAt · button gone", post == {"done": True, "cap": 100, "exitOk": True, "trgOk": True, "conf": True, "d": True, "btn": False}, post)
        if desk:
            hw = row(page, "MU", "[data-wl1-hwt]")
            check(f"{tag} B: MU row shows 'Done <date>'", hw.startswith("Done ") and "Not started" not in hw, hw)
        else:
            check(f"{tag} B: MU phone line 2 says 'thesis done'", "thesis done" in row(page, "MU", ".l2"), row(page, "MU", ".l2"))
        # blanks only — NVDA has its own exit
        if desk:
            js(page, "()=>wlOpen('NVDA')"); page.wait_for_timeout(300)
        else:
            js(page, "()=>{ wlBack(); }"); page.wait_for_timeout(200); js(page, "()=>wlOpen('NVDA')"); page.wait_for_timeout(350)
        page.click("[data-wl2-use]"); page.wait_for_timeout(500)
        nv = js(page, "()=>{ const it = wlItemOf('NVDA'), lt = wl2Lt(it); return {done:wl1HwDone(it), exit:wlMyThesis(it).exit, trgOk:it.hw.trigger === lt.trigger} }")
        check(f"{tag} B: never overwrites — NVDA keeps 'My own exit', trigger filled, homework done", nv == {"done": True, "exit": "My own exit", "trgOk": True}, nv)
        nb = js(page, "()=>{ wlOpen('AVGO'); return !!document.querySelector('[data-wl2-use]') }")
        check(f"{tag} B: no button when homework is already done (AVGO) or there is no living thesis (AAPL)", nb is False and js(page, "()=>{ wlOpen('AAPL'); return !!document.querySelector('[data-wl2-use]') }") is False)
        # ---- C: sector auto-fill
        sc = js(page, "()=>({glbe:tv1EtfOf('GLBE', wlItemOf('GLBE')), mu:tv1EtfOf('MU', wlItemOf('MU')), plain:tv1EtfOf('ZZZZ', null)})")
        check(f"{tag} C: sector from the price doc — GLBE (Software) → IGV · MU keeps manual SMH · unknown → ''", sc == {"glbe": "IGV", "mu": "SMH", "plain": ""}, sc)
        if desk:
            js(page, "()=>{ wlBack(); }"); page.wait_for_timeout(200)
            check(f"{tag} C: GLBE row shows its sector (Software) in the Sector column", row(page, "GLBE", "[data-lr5-sec]").startswith("Software"), row(page, "GLBE", "[data-lr5-sec]"))
        # ---- missing fields
        miss = js(page, "()=>{ const r = wl5RsOf(wlItemOf('TEAM')); return {ok:r.ok, off:r.off, hi:r.hi, r3m:r.r3m} }")
        check(f"{tag} G: old price doc (TEAM, no new fields) → rating only, no errors", miss == {"ok": True, "off": None, "hi": None, "r3m": None}, miss)
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} G: no horizontal page overflow", ov <= 0, ov)
        check(f"{tag} G: no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 780)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY WL2: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
