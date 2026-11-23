#!/usr/bin/env python3
"""LR-F — Today at 390: ≤ 2 rows per Act group then '+N more ›' · every Act row exactly 2 lines (same height ±2 px) · blocked row = chip + short reason, no Place button visible · glance hides empty items (one line when all empty) · no wrap in 'Risk-off' / 'Risk −$…'.
Run: python3 tests/run_tests_lrf.py"""
import sys, re
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, launch, check, results, plan_card
import run_tests_lr3 as L3


def cards_today():
    cs = L3.cards_board()
    for i, (sym, e, sl) in enumerate((("AAA", 50, 46), ("BBB", 60, 55), ("CCC", 70, 64))):
        c = plan_card(sym, e, sl, px=e + 0.5, ready=True); c["track"] = "ladder" if i == 2 else None
        if c["track"] is None: del c["track"]
        cs["x" + sym] = c
    return cs


def today(page):
    js(page, "()=>{ serverConfirmed = true; stateFromServer = true; if(acctActive !== 'main') acctSwitch('main'); re1Cache = {}; lr2DetOpen = false; re2GrpAll = {}; switchTab('today'); todayRefresh(true); }")
    page.wait_for_timeout(500)


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=cards_today())
    try:
        today(page)
        g = js(page, "()=>[...document.querySelectorAll('[data-re2-col]')].map(c=>({k:c.dataset.re2Col, rows:[...c.querySelectorAll('.re2-row')].filter(r=>r.getClientRects().length).length, more:(c.querySelector('[data-re2-more]')||{}).innerText||''}))")
        if w <= 600:
            check(f"{tag} C2: every Act group shows at most 2 rows, then '+N more ›'", all(x["rows"] <= 2 for x in g) and any(x["k"] == "enter" and re.match(r"^\+\d+ more ›$", x["more"].strip()) for x in g), g)
            hs = js(page, "()=>[...document.querySelectorAll('.re2-row')].filter(r=>r.getClientRects().length).map(r=>({s:r.dataset.re2Row, h:Math.round(r.getBoundingClientRect().height), grp:r.dataset.re2Grp, act:[...r.querySelectorAll('.re2-btns button')].some(b=>b.getClientRects().length)}))")
            # HF1: a row with an action = text (2 lines) + a bottom action line inside the card; a row without one stays 2 lines. Same kind = same height.
            same = all(max(x["h"] for x in g) - min(x["h"] for x in g) <= 2 for g in ([x for x in hs if x["act"]], [x for x in hs if not x["act"]]) if g)
            check(f"{tag} C2 (HF1): rows of the same kind are the same height (±2 px): text-only = 2 lines; with an action = 2 lines + the action line inside the card", len(hs) >= 3 and same, hs)
            ln = js(page, "()=>[...document.querySelectorAll('.re2-row .num')].filter(r=>r.getClientRects().length).map(n=>{ const cs = getComputedStyle(n); return {ws:cs.whiteSpace, ov:cs.textOverflow, one: n.getBoundingClientRect().height < 22}; })")
            check(f"{tag} C2 (NT2c phone): line 2 wraps (max 2 lines), never cut with an ellipsis", ln and all(x["ws"] == "normal" and x["ov"] != "ellipsis" for x in ln), ln)
            l2 = js(page, "()=>[...document.querySelectorAll('.re2-row:not(.x) [data-re2-cardline]')].filter(n=>n.getClientRects().length && !n.classList.contains('lrf-blkline')).map(n=>n.innerText.replace(/\\s+/g,' '))")
            check(f"{tag} C2: line 2 = first entry · SL · Risk only (no TP, no 2nd leg)", l2 and all(" TP " not in (" " + x + " ") and " + " not in x and "SL" in x and "Risk" in x for x in l2), l2)
            js(page, "()=>document.querySelector('[data-re2-col=\"enter\"] [data-re2-more]').click()"); page.wait_for_timeout(400)
            n2 = js(page, "()=>[...document.querySelectorAll('[data-re2-col=\"enter\"] .re2-row')].filter(r=>r.getClientRects().length).length")
            check(f"{tag} C2: '+N more ›' opens the rest of the group", n2 > 2, n2)
            # blocked row sits behind '+N more ›' on the phone — it stays open for the checks below
        blk = js(page, "()=>{ const r = document.querySelector('.re2-row[data-re2-row=\"NVDA\"]'); if(!r) return null; const b = r.querySelector('[data-re2-btn=\"place\"]'); return {chip:(r.querySelector('.lrf-blk')||{}).innerText||'', line:(r.querySelector('.lrf-blkline')||{}).innerText||'', btnShown: !!b && b.getClientRects().length > 0, hasBtn: !!b}; }")
        check(f"{tag} C2: blocked row = 'Blocked' chip + short reason (MMT weekly limit 4/4), no visible Place button", blk and blk["chip"] == "Blocked" and "MMT weekly limit 4/4" in blk["line"] and not blk["btnShown"], blk)
        if w > 600: check(f"{tag} C2: desktop blocked line reads 'Blocked · MMT weekly limit 4/4'", blk and blk["line"].replace("\n", " ").startswith("Blocked · MMT weekly limit 4/4"), blk)
        nw = js(page, "()=>[...document.querySelectorAll('.lr2-mood b, .lr2-c .big' + (innerWidth <= 600 ? ', .re2-main .num' : ''))].filter(e=>e.getClientRects().length).map(e=>({t:e.innerText.slice(0,20), ws:getComputedStyle(e).whiteSpace, h:Math.round(e.getBoundingClientRect().height)}))")
        nw = js(page, "()=>[...document.querySelectorAll('.nt1b-mood .pill')].filter(e=>e.getClientRects().length).map(e=>({t:e.innerText.slice(0,20), ws:getComputedStyle(e).whiteSpace, h:Math.round(e.getBoundingClientRect().height)}))")
        check(f"{tag} C2: the mood pill does not wrap (NT2c: Act line 2 may wrap on the phone)", nw and all(x["ws"] == "nowrap" for x in nw), nw)
        gl = js(page, "()=>({cards:[...document.querySelectorAll('[data-lr2-card]')].map(c=>c.dataset.lr2Card), txt:(document.querySelector('[data-lr2-glance]')||{innerText:''}).innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} C2: NT1b status card with no news / sector data = MOOD + MACRO rows only (no empty-state line, no hot / news cards)", gl["cards"] == ["mood"] and "Import ›" not in gl["txt"], gl)
        import run_tests_lr2 as L2
        L2.seed_wi(page); page.wait_for_timeout(300)
        gl = js(page, "()=>[...document.querySelectorAll('[data-lr2-card]')].map(c=>c.dataset.lr2Card)")
        check(f"{tag} C2: with Weekly Impact data (event not today) the empty sector item stays hidden (no 'No sector data')", "hot" not in gl and "none" not in gl, gl)
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} C2: no overflow · no page errors", ov <= 0 and not pe, [ov, pe])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (360, 740), (1440, 900)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY lrf: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
