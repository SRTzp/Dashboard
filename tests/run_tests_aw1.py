#!/usr/bin/env python3
"""AW1 — account switch in the top bar · [ ] shortcuts · badge · Equity snapshot sheet · Cancel plan ✕ · Risk room chip (390 / 1280 / 1440).
Run: node tests/aw1_test.js   (wrapper)  or  python3 tests/run_tests_aw1.py   Screenshots → tests/screenshots/aw1-*.png"""
import json, os, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import re1d_common as K
from re1d_common import js, doc_c, cards, plan_card, launch, refresh, no_overflow, check, results, txt


def cancelled_card(cid, sym, reason, acct="main", at="2026-10-01T05:00:00.000Z"):
    c = plan_card(sym, 100, 92)
    c.update({"acct": acct, "status": "cancelled", "cancelReason": reason, "cancelledAt": at, "cancelNote": None})
    return c

SHOTS = K.SHOTS


def shot(page, name):
    page.screenshot(path=os.path.join(SHOTS, "aw1-%s.png" % name))


def make(extra=None, old_fam_snap=False):
    cs = cards()
    cs["pA"] = plan_card("AAA", 100, 92, px=99, ready=True)                       # main · Enter row (ready)
    cs["pB"] = plan_card("BBB", 100, 92, px=99, ready=True); cs["pB"]["acct"] = "fam"   # family · Enter row (ready)
    cs["pC"] = plan_card("CCC", 100, 92)
    cs.update(extra or {})
    d = doc_c()
    if old_fam_snap: d["books"]["fam"]["settings"]["equitySnapshots"][0]["bkkDate"] = "2026-09-21"
    return d, cs


def badge(page):
    return js(page, "()=>{const b=[...document.querySelectorAll('[data-acsw]')].map(x=>({id:x.dataset.acsw,n:(x.querySelector('[data-acsw-n]')||{}).innerText||''}));return b}")


def run(pw, w, h):
    tag = str(w)
    mobile = w <= 600
    d, cs = make(old_fam_snap=True)
    b, page, ce, pe = launch(pw, w, h, d, cs)
    try:
        # ── §1 switch
        ids = js(page, "()=>acctList.map(a=>a.id)")
        check("[%s] pill #acSw sits in the top bar, one button per account, aria-pressed on the active one" % tag, js(page, "()=>{const p=document.querySelector('.topbar #acSw');const bs=[...p.querySelectorAll('button')];return bs.length===acctList.length && bs[0].getAttribute('aria-pressed')==='true' && bs[1].getAttribute('aria-pressed')==='false' && getComputedStyle(p).display!=='none'}"))
        lab = js(page, "()=>[...document.querySelectorAll('#acSw button')].map(x=>x.title)")
        check("[%s] title = full name + '. previous · / next'" % tag, all(". previous · / next" in t for t in lab), lab)
        check("[%s] ⋯ menu has no account select (#acctSel / #mmAcct gone)" % tag, js(page, "()=>!document.getElementById('acctSel') && !document.getElementById('mmAcct')"))
        if mobile:
            vis = js(page, "()=>[...document.querySelectorAll('#acSw .acSwL')].filter(e=>e.offsetParent).map(e=>e.innerText)")
            check("[%s] iPhone: labels shortened to a letter" % tag, all(len(x) <= 2 for x in vis) and len(vis) == 2, vis)
            check("[%s] iPhone: no 'Trading' word / sync text, logo + sync dot stay" % tag, js(page, "()=>{const v=id=>{const e=document.getElementById(id)||document.querySelector(id);return e&&e.offsetParent!==null};return !document.querySelector('.brandName').offsetParent && !document.getElementById('brandSyncTime').offsetParent && !!document.querySelector('.brandMark').offsetParent && !!document.getElementById('acctDot').offsetParent && document.querySelectorAll('.hbtns>button').length>=2}"))
            tap = js(page, "()=>[...document.querySelectorAll('#acSw button')].map(b=>{const r=b.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]})")
            check("[%s] iPhone: tap targets ≥ 44 px" % tag, all(x[0] >= 44 and x[1] >= 44 for x in tap), tap)
            js(page, "()=>document.getElementById('brandSync').click()"); page.wait_for_timeout(200)
            check("[%s] iPhone: tapping the sync dot opens the ⋯ menu" % tag, js(page, "()=>document.getElementById('moreMenu').classList.contains('show')"))
            js(page, "()=>closeMoreMenu()")
        # tabs: stays on the same tab
        for tab in ("today", "plan", "journal", "mix"):
            js(page, "(t)=>switchTab(t)", tab); page.wait_for_timeout(250)
            js(page, "()=>document.querySelector('#acSw button:not(.on)').click()"); page.wait_for_timeout(300)
            now = js(page, "()=>[acctActive, activeTab, document.querySelector('#acSw .on').dataset.acsw]")
            check("[%s] click switches account and stays on %s" % (tag, tab), now[0] == ids[1] and now[1] == tab and now[2] == ids[1], now)
            js(page, "(a)=>acctSwitch(a)", ids[0]); page.wait_for_timeout(250)
        # ── §2 shortcuts
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(200)
        page.keyboard.press("/"); page.wait_for_timeout(250)
        check("[%s] / = next account" % tag, js(page, "()=>acctActive") == ids[1])
        page.keyboard.press("/"); page.wait_for_timeout(250)
        check("[%s] / wraps to the first" % tag, js(page, "()=>acctActive") == ids[0])
        page.keyboard.press("."); page.wait_for_timeout(250)
        check("[%s] . = previous (wraps)" % tag, js(page, "()=>acctActive") == ids[1])
        js(page, "(a)=>acctSwitch(a)", ids[0]); page.wait_for_timeout(250)
        js(page, "()=>{ const i=document.createElement('input'); i.id='aw1In'; document.body.appendChild(i); i.focus(); }")
        page.keyboard.press("/"); page.keyboard.press("."); page.wait_for_timeout(200)
        check("[%s] shortcut ignored while typing in an input" % tag, js(page, "()=>acctActive") == ids[0] and js(page, "()=>document.getElementById('aw1In').value") == "/.")
        js(page, "()=>{ document.getElementById('aw1In').remove(); document.activeElement.blur(); }")
        page.keyboard.press("Control+/"); page.wait_for_timeout(200)
        check("[%s] shortcut ignored with a modifier key" % tag, js(page, "()=>acctActive") == ids[0])
        js(page, "()=>coreSheet('snap','<h3>x</h3>')"); page.wait_for_timeout(150)
        page.keyboard.press("/"); page.wait_for_timeout(200)
        check("[%s] shortcut ignored while a sheet is open" % tag, js(page, "()=>acctActive") == ids[0])
        js(page, "()=>coreSheetClose()")
        page.keyboard.press("Shift+/"); page.wait_for_timeout(250)
        check("[%s] Shift+/ still opens the help overlay (account unchanged), help lists '. /' and '[ ]'" % tag, js(page, "()=>acctActive") == ids[0] and js(page, "()=>{const o=document.getElementById('kbHelpOverlay');return !!o && o.classList.contains('show') && /\\. \\//.test(o.innerText) && o.innerText.indexOf('[ ]')>=0}"))
        js(page, "()=>document.getElementById('kbHelpOverlay').classList.remove('show')")
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(300)
        c0 = js(page, "()=>bdChip"); page.keyboard.press("]"); page.wait_for_timeout(250)
        check("[%s] [ ] cycle the Plan filter again with 2 accounts (account unchanged)" % tag, js(page, "()=>bdChip") != c0 and js(page, "()=>acctActive") == ids[0], [c0, js(page, "()=>bdChip")])
        page.keyboard.press("["); page.wait_for_timeout(250)
        check("[%s] [ steps the filter back" % tag, js(page, "()=>bdChip") == c0)
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(200)
        # ── §3 badge
        bd = badge(page)
        check("[%s] badge only on the inactive account: Family = 1 Enter row + snapshot due = 2" % tag, bd[0]["n"] == "" and bd[1]["n"] == "2", bd)
        check("[%s] badge number = Act rows + snapshot due (+ review due) from the same functions" % tag, js(page, "(a)=>{const M=re2Model(a);return M.enter.length+M.check.length+M.manage.length+(aw1SnapDue(a)?1:0)+(re4Due(a)?1:0)}", ids[1]) == 2)
        # ── §4 snapshot sheet
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(200)
        js(page, "()=>document.querySelector('[data-aw1-snap]') ? 1 : 0")
        js(page, "()=>aw1SnapOpen()"); page.wait_for_timeout(250)
        info = js(page, "()=>({rows:document.querySelectorAll('[data-aw1-snap-row]').length, due:[...document.querySelectorAll('[data-aw1-snap-row]')].map(r=>r.dataset.due), foot:[...document.querySelectorAll('.ccFoot button')].map(b=>b.innerText.trim()), t:document.querySelector('.ccSh h3').innerText})")
        check("[%s] Equity snapshot sheet: one row per account, Later + 'Confirm' (only Family due)" % tag, info["rows"] == 2 and info["due"] == ["0", "1"] and info["foot"] == ["Later", "Confirm"], info)
        js(page, "()=>{ coreSheetClose(); }")
        d2, cs2 = make(old_fam_snap=False)
        d2["books"]["main"]["settings"]["equitySnapshots"][0]["bkkDate"] = "2026-09-21"; d2["books"]["fam"]["settings"]["equitySnapshots"][0]["bkkDate"] = "2026-09-21"
        b2, p2, ce2, pe2 = launch(pw, w, h, d2, cs2)
        try:
            js(p2, "()=>aw1SnapOpen()"); p2.wait_for_timeout(300)
            f = js(p2, "()=>[...document.querySelectorAll('.ccFoot button')].map(b=>b.innerText.trim())")
            check("[%s] both due → footer 'Later' · 'Confirm both'" % tag, f == ["Later", "Confirm both"], f)
            if w == 390: shot(p2, "snapshot-sheet-390")
            js(p2, "()=>{ document.getElementById('aw1SnA_' + acctList[0].id).value='5,100,000'; }")
            js(p2, "()=>document.getElementById('aw1SnAll').click()"); p2.wait_for_timeout(500)
            r = js(p2, "()=>({due:acctList.map(a=>aw1SnapDue(a.id)), chips:[...document.querySelectorAll('[data-aw1-done]')].map(x=>x.innerText), snaps:acctList.map(a=>(getBook(a.id).settings.equitySnapshots||[]).length), last:getBook(acctList[0].id).settings.equitySnapshots.slice(-1)[0].equity})")
            check("[%s] Confirm both → both confirmed (✓), snapshots written through re1SnapConfirm, edited value kept" % tag, r["due"] == [False, False] and len(r["chips"]) == 2 and r["snaps"] == [2, 2] and r["last"] == 5100000, r)
            js(p2, "()=>coreSheetClose()"); p2.wait_for_timeout(200)
            check("[%s] after confirming, the snapshot part leaves the badge (Family keeps 1 Enter row)" % tag, [x["n"] for x in badge(p2)] == ["", "1"], badge(p2))
            js(p2, "()=>{ acctList.length = 1; render(); }"); p2.wait_for_timeout(200)
            check("[%s] pill hidden with one account" % tag, js(p2, "()=>getComputedStyle(document.getElementById('acSw')).display==='none'"))
            check("[%s] no console / page errors (sheet run)" % tag, not ce2 and not pe2, ce2 + pe2)
        finally:
            b2.close()
        # ── §5 ✕ on the Planned card
        js(page, "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); }"); page.wait_for_timeout(350)
        x = js(page, "()=>{const c=document.querySelector('[data-bd-status=plan] [data-re4-card]');if(!c)return null;const r=c.getBoundingClientRect(),cs=getComputedStyle(c);return {t:c.innerText.trim(),w:Math.round(r.width),h:Math.round(r.height),label:c.getAttribute('aria-label'),title:c.title,br:cs.borderRadius,hit:getComputedStyle(c,'::after').content}}")
        check("[%s] Planned card: round ✕ (28 px), aria-label + title 'Cancel plan'" % tag, x and x["t"] == "✕" and x["w"] == 28 and x["h"] == 28 and x["label"] == "Cancel plan" and x["title"] == "Cancel plan", x)
        if mobile: check("[%s] iPhone: ✕ has a 44 px hit area (::after)" % tag, x and x["hit"] != "none" and x["hit"] != "normal", x)
        before = js(page, "()=>JSON.stringify(coreCardsList.map(c=>[c.id,c.status]))")
        js(page, "()=>document.querySelector('[data-bd-status=plan] [data-re4-card]').click()"); page.wait_for_timeout(300)
        check("[%s] ✕ opens the Cancel plan reason sheet" % tag, js(page, "()=>!!document.querySelector('[data-core-sheet=cxplan] #cxReason')"))
        js(page, "()=>document.querySelector('[data-re4-keep]').click()"); page.wait_for_timeout(300)
        check("[%s] Keep closes the sheet and changes nothing" % tag, js(page, "()=>!document.querySelector('[data-core-sheet=cxplan]')") and js(page, "()=>JSON.stringify(coreCardsList.map(c=>[c.id,c.status]))") == before)
        js(page, "()=>{ const id=document.querySelector('[data-bd-status=plan]').dataset.bdId||''; }")
        js(page, "()=>bdOpen(document.querySelector('[data-bd-status=plan]').dataset.bdCard)"); page.wait_for_timeout(400)   # PV1b: tapping the card toggles More; the drawer opens from Edit
        dr = js(page, "()=>{const b=document.querySelector('#bdDrawer [data-re4-cancel]');return b?b.innerText.replace(/\\s+/g,' ').trim():null}")
        check("[%s] drawer foot keeps the words 'Cancel plan ›'" % tag, dr == "Cancel plan ›", dr)
        js(page, "()=>{ try{ bdClose(); }catch(e){} }"); page.wait_for_timeout(200)
        if w in (390, 1440): js(page, "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); window.scrollTo(0,0); }"); page.wait_for_timeout(300); shot(page, "plan-%d" % w) if w in (390, 1440) else None
        # ── §6 Risk room chip never 'Review due'
        d3, cs3 = make()
        cs3["x1"] = cancelled_card("x1", "X1", "missed"); cs3["x2"] = cancelled_card("x2", "X2", "hesitated"); cs3["x3"] = cancelled_card("x3", "X3", "missed")
        b3, p3, ce3, pe3 = launch(pw, w, h, d3, cs3)
        try:
            due = js(p3, "()=>re4Due('main')")
            room = js(p3, "()=>{const c=document.querySelector('[data-re2-room] summary .chip');return c?c.innerText.trim():''}")
            st = js(p3, "()=>document.querySelector('[data-re2-state]').innerText.trim()")
            ex = js(p3, "()=>{const c=document.querySelector('[data-re4-chip]');return c?c.innerText.trim():''}")
            check("[%s] execution review due: Risk room chip + Act state never say 'Review due'" % tag, due and "Review due" not in room and "Review due" not in st and room == "Normal", [due, room, st])
            check("[%s] execution-review signal still visible on Today: red '3 not taken' chip + To do item" % tag, ex == "3 not taken" and js(p3, "()=>re1TodoItems().some(i=>i.id==='re4rev:main')"), ex)
            check("[%s] no console / page errors (review run)" % tag, not ce3 and not pe3, ce3 + pe3)
        finally:
            b3.close()
        # screenshots
        if w in (390, 1440):
            js(page, "()=>{ acctSwitch(acctList[0].id); switchTab('today'); todayRefresh(true); window.scrollTo(0,0); }"); page.wait_for_timeout(500)
            shot(page, "today-%d" % w)
        if w == 1440:
            js(page, "()=>{ acctSwitch(acctList[1].id); switchTab('today'); todayRefresh(true); window.scrollTo(0,0); }"); page.wait_for_timeout(500)
            shot(page, "family-active-1440")
            js(page, "()=>acctSwitch(acctList[0].id)"); page.wait_for_timeout(300)
        # ── overflow
        for tab in ("today", "plan", "journal", "mix"):
            js(page, "(t)=>{ switchTab(t); }", tab); page.wait_for_timeout(450)
            check("[%s] no horizontal overflow on %s" % (tag, tab), no_overflow(page), js(page, "()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth]"))
        check("[%s] no console / page errors" % tag, not ce and not pe, ce + pe)
    finally:
        b.close()


with sync_playwright() as pw:
    for w, h in ((390, 844), (1280, 800), (1440, 900)):
        run(pw, w, h)
bad = [r for r in results if not r[1]]
print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
sys.exit(1 if bad else 0)
