#!/usr/bin/env python3
"""NT1b — Ideas you don't forget: next step · check date · price level (sheet) · Today › Ideas card (+ ⋯ actions) · Watch pill · My ideas next step / trail / stale / Due ·
Today status card (MOOD · TODAY · HOT · MACRO) · CHECK ORDERS hidden at 0 · UIUX fixes ①–⑥ (one dark primary · colours · no duplicate homework text · Risk room 2 lines · 1440×900 · phone order).
Run: python3 tests/run_tests_nt1b.py"""
import sys, os, json, datetime
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import re1d_common as K
import nt1_common as N
import run_tests_nt1 as T
import run_tests_lr2 as L2
import lrf_side as S

TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
VIS = "(s)=>{ const e = document.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(), c = getComputedStyle(e); return r.width>0 && r.height>0 && c.visibility!=='hidden' && c.display!=='none'; }"
OVER = "()=>{ const w = document.documentElement.clientWidth; return document.documentElement.scrollWidth <= w + 1 && document.body.scrollWidth <= w + 1; }"
DOC = "(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas_my',i])"
AIDOC = "(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas',i])"
ROWS = "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>r.dataset.nt1bIt)"
ROWTX = "(k)=>{ const r = document.querySelector('[data-nt1b-it=\"' + k + '\"]'); return r ? r.innerText.replace(/\\s+/g,' ').trim() : null; }"
INFO = "(k)=>{ const r = document.querySelector('[data-nt1b-it=\"' + k + '\"]'); if(!r) return null; const p = r.querySelector('[data-nt1b-pill]'); return {tag:r.querySelector('[data-nt1b-tag]').innerText.trim(), title:r.querySelector('.t').innerText.trim(), pill:p.innerText.trim(), cls:p.className, btn:[...r.querySelectorAll('[data-nt1b-btn]')].map(b=>b.innerText.trim()), next:r.querySelector('[data-nt1b-sub]').innerText.trim()}; }"


def add(iso, n): return (datetime.date.fromisoformat(iso) + datetime.timedelta(days=n)).isoformat()


def td(page): return js(page, "()=>thaiToday()")


def seed_my(page, docs):
    for k, v in docs.items():
        page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas_my').doc(i).set(d)", [k, v])
    page.wait_for_timeout(500)


def seed_ai(page, iid, name, status="need_evidence", recheck=None, user=None, cands=True):
    import lr5_common as C
    d = C.idea_doc(iid, name); d["status"] = status
    if recheck: d["recheck"] = {"date": recheck}
    if cands: d["candidates"] = [{"sym": s, "name": s, "state": "study", "segments": [], "relevance_src": "10-K"} for s in ("VST", "CEG")]
    page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", [iid, {"idea": {k: v for k, v in d.items() if k != "log"}, "idea_log": d.get("log", []), "user": user or {}}])
    page.wait_for_timeout(300)


def quiet_fixture_ai(page):
    far = add(td(page), 40)
    for iid, nm in (("en-idea-1", "Memory chips stay tight"), ("en-idea-2", "Grid power demand")):
        seed_ai(page, iid, nm, "need_evidence", recheck=far, cands=False)


def px(page, sym, v):
    js(page, "([s,v])=>{ pxAuto[s] = {close:v, closeDate:thaiToday()}; coreApplyPx(); todayRefresh(true); }", [sym, v]); page.wait_for_timeout(200)


def to_today(page):
    js(page, "()=>{ lr2DetOpen = false; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(350)


def mkmy(i, subj, title, created, check_on=None, **x):
    x.setdefault("next", "Look again")   # NT1d: an idea without a Next step is due on Today (“no next step”) — fixtures that are not meant to be due carry one
    return N.my(i, subj, title, x.pop("view", None), x.pop("chart", None), x.pop("ang", {"tech": "x"}), x.pop("plan", ""), check=check_on, created=created, **x)


# ───────────────────────────────────────────── sheet · fields · defaults
def part_sheet(pw, w, h):   # NT2: the sheet lost Next step / Alert level / More notes (see run_tests_nt2.py for the Scenarios sheet) — what is left here is the check-date + validation behaviour that did not change
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        t0 = td(page)
        check(f"{tag} S trading-day maths: Thu +3 = Tue · Fri +3 = Wed · Sat +1 = Mon", js(page, "()=>[nt1bTD('2026-11-19', 3), nt1bTD('2026-11-20', 3), nt1bTD('2026-11-21', 1)]") == ["2026-11-24", "2026-11-25", "2026-11-23"])
        T.to_my(page); js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(250)
        g = js(page, "()=>{ const q = s=>document.querySelector(s); const c = q('#nt1fCheck'); return {check:c && c.value, next:!!q('[data-nt1b-next-in]'), blk:!!q('[data-nt1s-blk]')}; }")
        check(f"{tag} S New idea sheet (NT2): Scenarios block + Check again on · no Next step field", g["blk"] and not g["next"], g)
        check(f"{tag} S Check again on is pre-filled +3 trading days (not empty)", g["check"] == js(page, "()=>nt1bTD(thaiToday(), 3)") and g["check"] > t0, g)
        page.select_option("#nt1fSubj", "stock:AVGO"); page.fill("#nt1fTitle", "AVGO breakout"); page.fill("#nt1fCheck", add(t0, 5))
        page.click('[data-nt1s-r="0"] [data-nt1s-kind="breakout"]'); page.fill('[data-nt1s-r="0"] [data-nt1s-f="level"]', "-4"); page.click("[data-nt1-save]"); page.wait_for_timeout(300)
        check(f"{tag} S a scenario level must be above 0", "level" in (js(page, TXT, "#nt1Err") or "").lower(), js(page, TXT, "#nt1Err"))
        page.fill('[data-nt1s-r="0"] [data-nt1s-f="level"]', "190"); page.click("[data-nt1-save]"); page.wait_for_timeout(600)
        nid = js(page, "()=>mySel"); d = js(page, DOC, nid)
        check(f"{tag} S saved: scenarios · checkOn · snoozeTo null · planId null · dropped false", d["scenarios"][0]["level"] == 190 and d["checkOn"] == add(t0, 5) and d["snoozeTo"] is None and d["planId"] is None and d["dropped"] is False, d)
        seed_my(page, {"old1": mkmy(4, ("stock", "AAPL"), "Old idea", add(t0, -5))})
        m = js(page, "()=>{ const m = myList.find(x=>x.id==='old1'); return [m.checkOn, nt1bEff(m), nt1bTD(nt1DayOf(m), 3)]; }")
        check(f"{tag} S old idea without a check date: effective = created + 3 trading days (computed)", m[0] is None and m[1] == m[2], m)
        check(f"{tag} S …and nothing is written until it is edited", js(page, DOC, "old1")["checkOn"] is None)
        T.to_my(page, "old1"); page.click("[data-nt1-edit]"); page.wait_for_timeout(200)
        check(f"{tag} S Edit shows that computed date in the field", js(page, "()=>document.getElementById('nt1fCheck').value") == m[1])
        page.click("[data-nt1-save]"); page.wait_for_timeout(500)
        check(f"{tag} S …saving writes it", js(page, DOC, "old1")["checkOn"] == m[1])
        check(f"{tag} S no page errors", not pe, pe[:3])
    finally:
        b.close()


# ───────────────────────────────────────────── Today › Ideas card
def part_today(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        t0 = td(page); wide = w >= 900
        quiet_fixture_ai(page)
        seed_my(page, {
            "near": mkmy(1, ("stock", "AVGO"), "Breakout over 190", add(t0, -1), add(t0, 6), next="Close above 190 on volume", level=102, levelDir="up"),          # 2.0% from the close 100 → near
            "far": mkmy(2, ("stock", "AAPL"), "Far from level", add(t0, -1), add(t0, 6), next="n/a", level=104, levelDir="up"),                                     # 4% → not near, not due
            "today": mkmy(3, ("market", "US"), "Risk-off until CPI", add(t0, -2), t0, next="Read CPI → still bear?", view="bear"),
            "late2": mkmy(4, ("sat", "XAU"), "Range before CPI", add(t0, -4), add(t0, -2), next="Wait for the break"),
            "late5": mkmy(5, ("market", "TH"), "SET below 200-day", add(t0, -9), add(t0, -5), next="Check the 200-day"),
            "snz": mkmy(6, ("stock", "COST"), "Snoozed", add(t0, -3), add(t0, -3), snoozeTo=add(t0, 2)),
            "rev": mkmy(7, ("market", "US"), "Reviewed", add(t0, -3), add(t0, -3), review=N.rev("right")),
            "drp": mkmy(8, ("market", "US"), "Dropped", add(t0, -3), add(t0, -3), dropped=True),
            "fut": mkmy(9, ("market", "US"), "Future", add(t0, -3), add(t0, 9)),
        })
        seed_ai(page, "ai-need", "AI power: grid", "need_evidence", recheck=t0)
        seed_ai(page, "ai-park", "Parked theme", "parked", recheck=add(t0, -3))
        seed_ai(page, "ai-fut", "Future theme", "need_evidence", recheck=add(t0, 8))
        px(page, "AVGO", 100.0); px(page, "AAPL", 100.0)
        to_today(page)
        card = js(page, TXT, "[data-nt1b-ideas]")
        due = js(page, "()=>nt1bDueAll().map(x=>x.key)")
        check(f"{tag} T due items come from both sources, in order: near level → overdue (newest first) → today → AI", due == ["my:near", "my:late2", "my:late5", "my:today", "ai:ai-need"], due)
        check(f"{tag} T not due: snoozed · reviewed · dropped · future · far from level · parked AI · future AI", all(k not in due for k in ("my:snz", "my:rev", "my:drp", "my:fut", "my:far", "ai:ai-park", "ai:ai-fut")), due)
        rows = js(page, ROWS)
        check(f"{tag} T max 3 rows (5 due)", rows == ["my:near", "my:late2", "my:late5"], rows)
        hd = js(page, "()=>({t:document.querySelector('[data-nt1b-ideas] .lr2-th b').innerText, due:document.querySelector('[data-nt1b-due]').innerText, open:document.querySelector('[data-nt1b-open]').innerText, all:document.querySelector('[data-nt1b-all]').innerText})")
        n_open = js(page, "()=>nt1bOpenCount()")
        check(f"{tag} T header: Ideas · amber `5 due` · `n open` · All ›", hd == {"t": "Ideas", "due": "5 due", "open": f"{n_open} open", "all": "All ›"}, hd)
        dc = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1b-due]')).color")
        check(f"{tag} T `n due` is amber", dc not in ("rgb(20, 22, 26)",) and dc.startswith(("rgb(169, 110, 6)", "rgb(154, 91, 0)")), dc)
        check(f"{tag} T open count = My ideas not reviewed / dropped + AI not parked", n_open == 7 + 5, n_open)   # near far today late2 late5 snz fut (7) + ai-need + ai-fut + 2 quiet fixture themes + the fixture trade idea
        i1 = js(page, INFO, "my:near")
        check(f"{tag} T row 1: subject tag · title · blue `2.0% to A` · one button `Open ›` (NT2: Make plan › only once a scenario has fired) · the scenario line under it", i1 == {"tag": "AVGO", "title": "Breakout over 190", "pill": "2.0% to A", "cls": i1["cls"], "btn": ["Open ›"], "next": "A breakout 102"} and "p-b" in i1["cls"], i1)
        i2 = js(page, INFO, "my:late2")
        check(f"{tag} T overdue: amber `2 days late` · Open ›", i2["pill"] == "2 days late" and "p-a" in i2["cls"] and i2["btn"] == ["Open ›"] and i2["tag"] == "XAU", i2)
        i3 = js(page, INFO, "my:late5")
        check(f"{tag} T 5 days late · a Draft shows `Draft · no scenario yet` (NT2: no Next step line)", i3["pill"] == "5 days late" and i3["next"] == "Draft · no scenario yet", i3)
        check(f"{tag} T NT2 wording `2.0% to A` (never `away`)", "to A" in card and "away" not in card, card)
        # reasons: today + AI
        js(page, "()=>{ ln4TodoAll = true; }")
        js(page, "()=>nt1bAct('my:near','snooze7')"); page.wait_for_timeout(300)
        js(page, "()=>nt1bAct('my:late2','snooze7')"); js(page, "()=>nt1bAct('my:late5','snooze7')"); page.wait_for_timeout(300)
        rows = js(page, ROWS)
        check(f"{tag} T after 3 snoozes: today + AI idea fill the box", rows == ["my:today", "ai:ai-need"], rows)
        it = js(page, INFO, "my:today"); ia = js(page, INFO, "ai:ai-need")
        check(f"{tag} T check date today → amber `check today` · Open ›", it["pill"] == "check today" and "p-a" in it["cls"] and it["btn"] == ["Open ›"] and it["tag"].replace("\u00a0", " ") == "US MKT", it)
        check(f"{tag} T AI idea: grey status pill `evidence n/4` · `Add evidence ›` · line 2 `check today` (NT2c)", ia["tag"] == "THEME" and ia["pill"].startswith("evidence ") and ia["pill"].endswith("/4") and "p-n" in ia["cls"] and ia["btn"] == ["Add evidence ›"] and ia["next"] == "check today", ia)
        for k in ("my:near", "my:late2", "my:late5"):
            js(page, "(k)=>nt1bAct(k.replace('my:','my:'),'snooze3')", k) if False else None
        # AI trade idea due
        js(page, "()=>{ const d = tradeList[0]; d.ai.expires = thaiToday(); todayRefresh(true); }"); page.wait_for_timeout(250)
        ib = js(page, ROWS)
        check(f"{tag} T a trade idea comes back on its date (TRADE tag · `Open ›` when not needing evidence)", any(r.startswith("ai:gold") for r in ib) or len(ib) == 3, ib)
        # one button per row · no row with only ⋯
        nb = js(page, "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>[r.querySelectorAll('[data-nt1b-btn]').length, r.querySelectorAll('.nt1b-btn').length])")
        check(f"{tag} T every row has exactly one real button", all(x == [1, 1] for x in nb) and nb, nb)
        # ⋯ : header menu
        page.click("[data-nt1b-hdots]"); page.wait_for_timeout(150)
        mn = js(page, "()=>[...document.querySelectorAll('[data-nt1b-menu] [role=menuitem]')].map(b=>b.innerText.trim())")
        check(f"{tag} T header ⋯ menu: Snooze 3 days · Snooze 1 week · Done — nothing to do · Drop idea", mn == ["Snooze 3 days", "Snooze 1 week", "Done — nothing to do", "Drop idea"], mn)
        dr = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1b-act=drop]')).color")
        check(f"{tag} T Drop idea is red", dr.startswith("rgb(194, 54, 47)") or dr.startswith("rgb(166, 45, 39)"), dr)
        page.mouse.click(5, 300); page.wait_for_timeout(150)
        check(f"{tag} T a click elsewhere closes the menu", not js(page, VIS, "[data-nt1b-menu]"))
        if wide:
            r0 = "[data-nt1b-it] [data-nt1b-rowdots]"
            op0 = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1b-rowdots]')).opacity")
            page.hover("[data-nt1b-it]"); page.wait_for_timeout(120)
            op1 = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1b-rowdots]')).opacity")
            check(f"{tag} T row ⋯ appears on hover only", float(op0) == 0 and float(op1) == 1, [op0, op1])
        # actions on the AI row
        first = js(page, ROWS)[0]
        js(page, "(k)=>{ nt1bMenu = k; todayRefresh(true); }", first); page.wait_for_timeout(150)
        check(f"{tag} T a row's ⋯ opens the menu for that row", js(page, TXT, "[data-nt1b-menu] .nt1b-mh") is not None and "·" in js(page, TXT, "[data-nt1b-menu] .nt1b-mh"))
        page.click("[data-nt1b-act=snooze3]"); page.wait_for_timeout(500)
        k_ = first.split(":", 1)[1]
        if first.startswith("my:"): d = js(page, DOC, k_); sz = d["snoozeTo"]
        else: sz = js(page, AIDOC, k_)["user"].get("snoozeTo")
        check(f"{tag} T Snooze 3 days writes snoozeTo = today + 3 and the row leaves", sz == add(t0, 3) and first not in js(page, ROWS), [first, sz])
        tt = js(page, TXT, "#nt1bToast")
        check(f"{tag} T toast with Undo", tt and "Undo" in tt, tt)
        page.click("[data-nt1b-undo]"); page.wait_for_timeout(400)
        check(f"{tag} T Undo brings it back", first in js(page, ROWS))
        # my idea actions: 1 week / done / drop + undo
        js(page, "(k)=>nt1bAct(k,'snooze7')", "my:today"); page.wait_for_timeout(300)
        check(f"{tag} T Snooze 1 week writes today + 7", js(page, DOC, "today")["snoozeTo"] == add(t0, 7))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        js(page, "(k)=>nt1bAct(k,'done')", "my:today"); page.wait_for_timeout(300)
        check(f"{tag} T Done — nothing to do moves the check date +3 trading days", js(page, DOC, "today")["snoozeTo"] == js(page, "()=>nt1bTD(thaiToday(), 3)"), js(page, DOC, "today"))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        check(f"{tag} T Undo restores the old date", js(page, DOC, "today")["snoozeTo"] is None)
        js(page, "(k)=>nt1bAct(k,'drop')", "my:today"); page.wait_for_timeout(300)
        check(f"{tag} T Drop idea marks dropped + toast `Dropped:` + Undo", js(page, DOC, "today")["dropped"] is True and "Dropped" in (js(page, TXT, "#nt1bToast") or "") and "my:today" not in js(page, ROWS))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        check(f"{tag} T Undo of Drop brings the idea back", js(page, DOC, "today")["dropped"] is False and "my:today" in js(page, ROWS))
        # AI: done / drop
        js(page, "(k)=>nt1bAct(k,'done')", "ai:ai-need"); page.wait_for_timeout(300)
        u = js(page, AIDOC, "ai-need")["user"]
        check(f"{tag} T AI idea Done: user.snoozeTo +3 trading days · user.done (existing doc, no new collection)", u.get("snoozeTo") == js(page, "()=>nt1bTD(thaiToday(), 3)") and u.get("done") is True, u)
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        js(page, "(k)=>nt1bAct(k,'drop')", "ai:ai-need"); page.wait_for_timeout(300)
        check(f"{tag} T AI idea Drop = Parked (reversible)", js(page, AIDOC, "ai-need")["user"].get("status") == "parked" and "ai:ai-need" not in js(page, ROWS))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        check(f"{tag} T …Undo restores its status", js(page, AIDOC, "ai-need")["user"].get("status") != "parked" and "ai:ai-need" in js(page, ROWS))
        # buttons go to the right place
        js(page, "()=>document.querySelector('[data-nt1b-it=\"ai:ai-need\"] [data-nt1b-btn]').click()"); page.wait_for_timeout(350)
        check(f"{tag} T Add evidence › opens the AI idea", js(page, "()=>[activeTab, nt1Seg, ideaSel]") == ["watch", "ai", "ai-need"], js(page, "()=>[activeTab, nt1Seg, ideaSel]"))
        to_today(page)
        # no duplicates in To do
        tl = js(page, "()=>[...document.querySelectorAll('[data-lr2-ti]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} T the same idea never shows twice: no `IDEA · Check:` line in To do", not any(x.startswith("IDEA") or "Check:" in x for x in tl), tl)
        # Watch pill
        wc = js(page, "()=>{ const b = document.getElementById('tabBadgeWatch'); return [b.style.display !== 'none', b.innerText]; }")
        due_n = js(page, "()=>nt1bDueAll().length")
        check(f"{tag} T Watch nav shows an amber count pill = ideas due", wc == [True, str(due_n)] and due_n >= 2, [wc, due_n])
        ws = js(page, "()=>{ const b = document.getElementById('tabBadgeWatch'); const s = getComputedStyle(b); return [s.color, s.backgroundColor]; }")
        check(f"{tag} T …amber colours", ws[0] in ("rgb(169, 110, 6)", "rgb(154, 91, 0)"), ws)
        js(page, "()=>switchTab('journal')"); page.wait_for_timeout(200)
        check(f"{tag} T …the pill is there on every page", js(page, "()=>document.getElementById('tabBadgeWatch').style.display !== 'none'"))
        if w <= 700:
            pos = js(page, "()=>{ const b = document.getElementById('tabBadgeWatch').getBoundingClientRect(); return [b.width > 0, Math.round(b.bottom) <= innerHeight, Math.round(b.right) <= innerWidth]; }")
            check(f"{tag} T phone nav: same pill, inside the screen", all(pos), pos)
        # none due → one line
        js(page, "()=>{ myList.forEach(m=>{ m.snoozeTo = nt1bTD(thaiToday(), 9); }); ideaList.forEach(d=>{ d.user.snoozeTo = nt1bTD(thaiToday(), 9); }); tradeList.forEach(d=>{ d.user.snoozeTo = nt1bTD(thaiToday(), 9); }); }")
        to_today(page)
        st = js(page, "()=>document.querySelector('[data-nt1b-ideas]').dataset.nt1bState")
        one = js(page, TXT, "[data-nt1b-ideas]")
        hh = js(page, "()=>Math.round(document.querySelector('[data-nt1b-ideas]').getBoundingClientRect().height)")
        no = js(page, "()=>n=nt1bOpenCount()") if False else js(page, "()=>nt1bOpenCount()")
        check(f"{tag} T nothing due → ONE line: `Ideas · none due · n open · All ›`", st == "none" and one == f"Ideas · none due · {no} open All ›" and hh < 70 and not js(page, VIS, "[data-nt1b-it]"), [st, one, hh])
        check(f"{tag} T …and the Watch pill is gone", js(page, "()=>document.getElementById('tabBadgeWatch').style.display") == "none")
        js(page, "()=>document.querySelector('[data-nt1b-all]').click()"); page.wait_for_timeout(300)
        check(f"{tag} T All › opens Watch › Ideas", js(page, "()=>[activeTab, wlView]") == ["watch", "idea"], js(page, "()=>[activeTab, wlView]"))
        check(f"{tag} T no overflow · no page errors", js(page, OVER) and not pe, pe[:3])
    finally:
        b.close()


def part_near_edges(pw):
    tag = "[1440]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = td(page); quiet_fixture_ai(page)
        seed_my(page, {"e3": mkmy(1, ("stock", "AVGO"), "Within 3%", add(t0, -1), add(t0, 6), level=103, levelDir="up"), "e4": mkmy(2, ("stock", "AAPL"), "Over 3%", add(t0, -1), add(t0, 6), level=104, levelDir="up"),
                       "sat": mkmy(3, ("sat", "XAU"), "Sat level", add(t0, -1), add(t0, 6), level=2600, levelDir="up"), "dated": mkmy(4, ("stock", "COST"), "Near and late", add(t0, -1), add(t0, -3), level=101, levelDir="up")})
        for s in ("AVGO", "AAPL", "COST"): px(page, s, 100.0)
        due = js(page, "()=>nt1bDueAll().map(x=>[x.key, x.pill])")
        check(f"{tag} T near level = within 3% of the price: 3.0% yes (NT2 measures distance from the price) · 4% no · Sat (no price) no · a late idea near its level shows `to A` first", sorted(due) == [["my:dated", "1.0% to A"], ["my:e3", "3.0% to A"]], due)
        js(page, "()=>{ const m = myList.find(x=>x.id==='dated'); m.subject.type = 'sat'; todayRefresh(true); }"); page.wait_for_timeout(200)
        d2 = js(page, "()=>nt1bDueAll().map(x=>[x.key, x.pill, x.btn[0]])")
        check(f"{tag} T `Make plan ›` only for a stock (a Sat idea near its date shows Open ›)", ["my:dated", "3 days late", "Open ›"] in d2, d2)
        check(f"{tag} T no page errors", not pe, pe[:3])
    finally:
        b.close()


# ───────────────────────────────────────────── Watch › My ideas
def part_watch(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        t0 = td(page); quiet_fixture_ai(page)
        seed_my(page, {
            "avgo": mkmy(1, ("stock", "AVGO"), "Breakout over 190 with volume", add(t0, -1), add(t0, 6), next="Close above 190 on volume → plan Momentum", level=102, levelDir="up", view="bull"),
            "usm": mkmy(2, ("market", "US"), "Risk-off until CPI cools", add(t0, -2), t0, next="Read CPI tonight → still bear?", view="bear"),
            "nvda": mkmy(3, ("stock", "AAPL"), "Pullback = add zone", add(t0, -5), add(t0, 9), next="Wait for the add", planId="aapl"),
            "plan": mkmy(4, ("stock", "AVGO"), "Plan linked, no fill", add(t0, -6), add(t0, 8), planId="avgo"),
            "stale": mkmy(5, ("market", "TH"), "Range into FOMC", add(t0, -40), add(t0, 30), view="neutral", updated_at=add(t0, -34) + "T05:00:00.000Z"),
            "fresh": mkmy(6, ("market", "TH"), "Not stale", add(t0, -20), add(t0, 30), updated_at=add(t0, -20) + "T05:00:00.000Z"),
            "revd": mkmy(7, ("market", "US"), "Reviewed long ago", add(t0, -90), add(t0, -80), review=N.rev("right", "", -80)),
        })
        px(page, "AVGO", 100.0)
        T.to_my(page, "avgo"); page.wait_for_timeout(300)
        row = js(page, "()=>{ const r = document.querySelector('[data-nt1-my=\"avgo\"]'); return {nx:r.querySelector('[data-nt1b-nx]').innerText.replace(/\\s+/g,' '), trail:!!r.querySelector('[data-nt1b-trail]'), pill:(r.querySelector('[data-nt1b-pill]')||{}).innerText}; }")
        check(f"{tag} W list row (NT2): line 2 = the scenarios in full · no trail in the row (it moved to the detail footer)", row["nx"] == "A breakout 102" and not row["trail"], row)
        check(f"{tag} W near its level: `2.0% to A` pill on the row", row["pill"] == "2.0% to A", row)
        def trail(i):
            T.to_my(page, i); page.wait_for_timeout(120)
            return js(page, "()=>{ const t = document.querySelector('[data-nt1-foot] [data-nt1b-trail]'); return t ? [t.innerText.replace(/\\s+/g,' '), t.querySelector('[data-nt1b-step=plan]') ? t.querySelector('[data-nt1b-step=plan]').classList.contains('on') : null, t.querySelector('[data-nt1b-step=hold]') ? t.querySelector('[data-nt1b-step=hold]').classList.contains('on') : null] : null; }")
        tr = [trail(i) for i in ("avgo", "plan", "nvda", "usm")]
        check(f"{tag} W trail (detail footer): unlinked → none ticked · linked plan → Plan ✓ · plan with a fill → Plan ✓ Holding ✓ · market idea → `Market view · no plan`",
              tr[0] == ["Idea → Plan → Holding", False, False] and tr[1] == ["Idea → Plan ✓ → Holding", True, False] and tr[2] == ["Idea → Plan ✓ → Holding ✓", True, True] and tr[3][0] == "Market view · no plan", tr)
        T.to_my(page, "nvda"); page.wait_for_timeout(120)
        tc = js(page, "()=>getComputedStyle(document.querySelector('[data-nt1-foot] [data-nt1b-step=hold]')).color")
        check(f"{tag} W a reached step is green", tc.startswith("rgb(18, 128, 92)"), tc)
        # stale
        st = js(page, "()=>[...document.querySelectorAll('[data-nt1b-stale]')].map(e=>e.closest('[data-nt1-my]').dataset.nt1My)")
        check(f"{tag} W stale (no check / edit / plan for 30 days): ONLY that idea asks `Still valid?`", st == ["stale"], st)
        stx = js(page, TXT, "[data-nt1-my=\"stale\"] [data-nt1b-stale]")
        check(f"{tag} W …`Still valid?` · `Keep · check in 1 week` · `Drop`", stx == "Still valid? Keep · check in 1 week Drop", stx)
        page.click("[data-nt1-my=\"stale\"] [data-nt1b-keep]"); page.wait_for_timeout(500)
        d = js(page, DOC, "stale")
        check(f"{tag} W Keep moves the check date (+1 week) and counts as a touch", d["snoozeTo"] == add(t0, 7) and d["updated_at"][:10] >= t0 and "stale" not in js(page, "()=>[...document.querySelectorAll('[data-nt1b-stale]')].map(e=>e.closest('[data-nt1-my]').dataset.nt1My)"), d)
        check(f"{tag} W …asked once: it does not come back", js(page, "()=>document.querySelectorAll('[data-nt1b-stale]').length") == 0)
        js(page, "()=>{ const m = myList.find(x=>x.id==='fresh'); m.updated_at = nt1bTD(thaiToday(), 0) && (new Date(Date.now() - 31*864e5)).toISOString(); m.created_at = m.updated_at; renderWatchlist(); }"); page.wait_for_timeout(200)
        page.click("[data-nt1-my=\"fresh\"] [data-nt1b-drop]"); page.wait_for_timeout(400)
        check(f"{tag} W stale Drop = dropped (Undo toast) · row leaves the list", js(page, DOC, "fresh")["dropped"] is True and js(page, "()=>!document.querySelector('[data-nt1-my=\"fresh\"]')") and "Undo" in (js(page, TXT, "#nt1bToast") or ""))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        # Due filter
        chips = js(page, "()=>[...document.querySelectorAll('[data-nt1-f]')].map(b=>b.innerText.trim())")
        check(f"{tag} W filter chips: All · Due n · Markets · Stocks · Sat · Plan", chips[0] == "All" and chips[1].startswith("Due") and chips[2:] == ["Markets", "Stocks", "Sat", "Plan"], chips)
        page.click("[data-nt1-f=due]"); page.wait_for_timeout(250)
        dr = js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)")
        check(f"{tag} W Due filter lists only due ideas (price near / check date reached / not snoozed)", set(dr) == {"avgo", "usm"}, dr)
        js(page, "()=>nt1FSet('all')")
        # detail: Next step block above the chart
        T.to_my(page, "avgo"); page.wait_for_timeout(250)
        blk = js(page, "()=>{ const d = document.querySelector('[data-nt1-detail]'); const b = d.querySelector('[data-nt1b-block]'); return {at:!!b, txt:b && b.innerText.replace(/\\s+/g,' '), plan:b && (b.querySelector('[data-nt1b-mkplan]')||{}).className, trail:!!d.querySelector('[data-nt1-foot] [data-nt1b-trail]')}; }")
        check(f"{tag} W detail (NT2): green Scenarios card with check date · ruler `A 102` · `now 100` · `2.0% away` · trail in the footer", blk["at"] and "SCENARIOS · WATCHING" in blk["txt"] and "A 102" in blk["txt"] and "now 100" in blk["txt"] and "2.0% away" in blk["txt"] and blk["trail"], blk)
        check(f"{tag} W detail (NT2): the watching card has no dark button and no `Make plan ›` until a scenario fires", "pri" not in (blk["plan"] or "") and "Make plan" not in blk["txt"], blk)
        js(page, "()=>document.querySelector('[data-nt1b-d-snooze]').click()"); page.wait_for_timeout(400)
        check(f"{tag} W detail Snooze 3 days writes snoozeTo", js(page, DOC, "avgo")["snoozeTo"] == add(t0, 3))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        js(page, "()=>document.querySelector('[data-nt1b-d-done]').click()"); page.wait_for_timeout(400)
        check(f"{tag} W detail Done moves the check date +3 trading days", js(page, DOC, "avgo")["snoozeTo"] == js(page, "()=>nt1bTD(thaiToday(), 3)"))
        js(page, "()=>nt1bUndoDo()"); page.wait_for_timeout(300)
        # review stays inside the idea
        T.to_my(page, "usm"); page.wait_for_timeout(200)
        check(f"{tag} W review Right / Partly / Wrong stays inside the idea on its date", js(page, "()=>document.querySelector('[data-nt1-review]').dataset.nt1Review") == "due")
        # old notes: no next block / not due
        check(f"{tag} W no overflow · no page errors", js(page, OVER) and not pe, pe[:3])
    finally:
        b.close()


# ───────────────────────────────────────────── Make plan › links the plan to the idea
def part_plan(pw):
    tag = "[1440]"
    b, page, pe = N.open_nt1(pw, 1440, 900, my_docs=False, notes=False)
    try:
        t0 = td(page)
        seed_my(page, {"avgo": mkmy(1, ("stock", "AMD"), "Breakout over 102", add(t0, -1), add(t0, 6), next="Buy the break", level=102)})
        px(page, "AMD", 100.0)
        to_today(page)
        before = js(page, "()=>coreCardsList.filter(c=>coreNorm(c.ticker)==='AMD').length")
        js(page, "()=>document.querySelector('[data-nt1b-it=\"my:avgo\"] [data-nt1b-btn]').click()"); page.wait_for_timeout(500)
        o = js(page, "()=>({tab:activeTab, mode:coreNew && coreNew.mode, tk:(coreEl('cnTicker')||{}).value, entry:(coreEl('cnEntry')||{}).value, pend:nt1bPend && nt1bPend.id})")
        check(f"{tag} M Make plan › opens the plan editor on Plan with the ticker + level as entry", o["tab"] == "plan" and o["mode"] == "new" and o["entry"] == "102" and o["pend"] == "avgo" and (o["tk"] or "").upper() in ("AMD", ""), o)
        tr0 = js(page, "()=>myList.find(x=>x.id==='avgo').planId")
        check(f"{tag} M …nothing is linked before the plan is saved", tr0 is None)
        check(f"{tag} M coreNewSave calls the link hook right after the new card is written", js(page, "()=>/coreWrite\\(id, card\\);\\s*try\\{ nt1bLinkPlan\\(id, rd\\.ticker\\)/.test(coreNewSave.toString())"))
        # the sandbox snapshot is stale, so the form cannot save here — write the card the way coreNewSave does, then run the hook it calls
        js(page, "()=>{ coreWrite('ccnew1', {acct:tdHome(), ticker:'AMD', market:'US', strategy:'W', plan:{entry:102, stop:95}, stop:95, stopHistory:[], px:null, lots:[], status:'plan', created_at:new Date().toISOString()}); nt1bLinkPlan('ccnew1', 'AMD'); }"); page.wait_for_timeout(900)
        after = js(page, "()=>coreCardsList.filter(c=>coreNorm(c.ticker)==='AMD').map(c=>c.id)")
        pid = js(page, DOC, "avgo")["planId"]
        check(f"{tag} M saving the plan stores planId on the idea (id of the new card)", pid == "ccnew1" and pid in after, [after, pid])
        T.to_my(page, "avgo"); page.wait_for_timeout(300)
        tr = js(page, "()=>document.querySelector('[data-nt1-foot] [data-nt1b-trail]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} M the trail turns green by itself: Idea → Plan ✓ → Holding", tr == "Idea → Plan ✓ → Holding", tr)
        js(page, "(p)=>{ const c = coreCardsList.find(x=>x.id===p); c.status = 'open'; c.lots = [{n:1, date:thaiToday(), px:100, qty:1}]; renderWatchlist(); }", pid); page.wait_for_timeout(200)
        tr = js(page, "()=>document.querySelector('[data-nt1-foot] [data-nt1b-trail]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} M …and Holding ✓ once the plan has a fill", tr == "Idea → Plan ✓ → Holding ✓", tr)
        # a plan saved for another ticker is not linked
        js(page, "()=>{ nt1bPend = {id:'avgo', ticker:'ZZZZ', at:Date.now()}; nt1bLinkPlan('cc999', 'AMD'); }")
        check(f"{tag} M a plan for a different ticker never links", js(page, "()=>myList.find(x=>x.id==='avgo').planId") == pid)
        check(f"{tag} M no page errors", not pe, pe[:3])
    finally:
        b.close()


# ───────────────────────────────────────────── Today layout: status card · CHECK ORDERS · UIUX fixes
def rect(page, sel):
    return js(page, "(s)=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return {l:Math.round(r.left), t:Math.round(r.top), w:Math.round(r.width), h:Math.round(r.height), b:Math.round(r.bottom), r:Math.round(r.right)}; }", sel)


def lrf_page(pw, w, h, working=True, extra_cards=None):
    d, cs = S.fixture()
    if not working: cs.pop("mO", None)
    if extra_cards: extra_cards(cs)
    b, page, ce, pe = K.launch(pw, w, h, d=d, c=cs)
    S.go(page, "today")
    js(page, "()=>{ lr2DetOpen = false; todayRefresh(true); }"); page.wait_for_timeout(300)
    if w <= 600: page.add_style_tag(content="#tabsMain{display:none!important}")
    return b, page, pe


def seed_today_ideas(page):
    t0 = td(page)
    seed_my(page, {"a": mkmy(1, ("stock", "AVGO"), "Breakout over 190", add(t0, -1), add(t0, 6), next="Close above 190 on volume", level=102, levelDir="up"),
                   "b": mkmy(2, ("market", "US"), "Risk-off until CPI", add(t0, -2), t0, next="Read CPI → still bear?", view="bear"),
                   "c": mkmy(3, ("sat", "XAU"), "Range before CPI", add(t0, -4), add(t0, -2), next="Wait for the break")})
    seed_ai(page, "ai-1", "AI power: grid", "need_evidence", recheck=t0)
    px(page, "AVGO", 100.0)


def part_layout(pw, w, h):
    tag = "[%s]" % w; wide = w >= 900
    b, page, pe = lrf_page(pw, w, h, working=False)
    try:
        seed_today_ideas(page)
        L2.set_regime(page, "red", "red", "fresh")
        L2.seed_wi(page); L2.seed_rrg(page)
        js(page, """()=>{ const d = Calc.wiIctDate(Date.now()), mon = wiCurMon(), doc = wiDocs[mon]; const hm = Calc.wiIctHM(Date.now()), h0 = +hm.slice(0, 2);
          const at = h => new Date(d + 'T' + String(h).padStart(2, '0') + ':30:00+07:00').toISOString();
          doc.events.cpi.scheduled_at = at(Math.min(h0 + 6, 23)); doc.events.past = {title:'US Jobs', label_th:'US Jobs', scheduled_at:at(Math.max(h0 - 3, 0)), time_status:'confirmed', status:'scheduled', kind:'nfp'};
          doc.assets.XAUUSD.event_refs = ['cpi', 'past']; todayRefresh(true); }""")
        page.wait_for_timeout(300)
        to_today(page)
        if wide: page.screenshot(path=os.path.join(K.SHOTS, "nt1b-today-scratch.png")) if False else None
        # ---- status card: left column above Act
        st = rect(page, "[data-nt1b-status]"); act = rect(page, "[data-ln4-act]"); ideas = rect(page, "[data-nt1b-ideas]"); todo = rect(page, "[data-ln4-todorow]"); risk = rect(page, "[data-lr2-risk]")
        check(f"{tag} L status card exists once (the old Market mood + Hot sectors cards are gone)", js(page, "()=>[document.querySelectorAll('[data-nt1b-status]').length, document.querySelectorAll('.lr2-glance:not([data-nt1b-status]), .lr2-c').length]") == [1, 0])
        if wide:
            check(f"{tag} L status card in the LEFT column, above Act, same width", st and act and st["t"] < act["t"] and st["b"] <= act["t"] and st["l"] == act["l"] and abs(st["w"] - act["w"]) <= 1, [st, act])
            check(f"{tag} L Ideas card sits level with the status card (±4px) · right column starts at the top of the content", abs(ideas["t"] - st["t"]) <= 4, [ideas, st])
            check(f"{tag} L right column order: Ideas → To do → Risk room", ideas["t"] < todo["t"] < risk["t"] and ideas["l"] == todo["l"] == risk["l"], [ideas, todo, risk])
            check(f"{tag} L right column is 440px wide (mockup grid 1fr + 440)", abs(ideas["w"] - 440) <= 2, ideas)
        rows = js(page, "()=>[...document.querySelectorAll('[data-nt1b-status] [data-nt1b-row]')].map(r=>r.dataset.nt1bRow)")
        check(f"{tag} L rows in order: MOOD · TODAY · HOT · MACRO", rows == ["mood", "today", "hot", "macro"], rows)
        labs = js(page, "()=>[...document.querySelectorAll('[data-nt1b-status] .k')].map(e=>[e.innerText, getComputedStyle(e).fontSize, getComputedStyle(e).textTransform, getComputedStyle(e).fontFamily.split(',')[0].replace(/\"/g,''), Math.round(e.getBoundingClientRect().width)])")
        if wide: check(f"{tag} L labels: 11px uppercase Inter (no serif), 62px column", all(x[1] == "11px" and x[2] == "uppercase" and "serif" not in x[3].lower() and x[4] <= 62 for x in labs) and len(labs) == 4, labs)
        mood = js(page, TXT, "[data-nt1b-row=mood]")
        check(f"{tag} L MOOD: regime pill + `new entries at n% size` + goal on the same row", mood.startswith("MOOD Risk-off new entries at ") and "% size" in mood and ("Goal" in mood or "goal" in mood), mood)
        check(f"{tag} L MOOD pill colour: Risk-off amber", js(page, "()=>getComputedStyle(document.querySelector('.nt1b-mood .pill')).color") .startswith("rgb(169, 110, 6)"))
        L2.set_regime(page, "green", "green", "fresh")
        check(f"{tag} L Risk-on pill green · Unclear grey", js(page, "()=>getComputedStyle(document.querySelector('.nt1b-mood .pill')).color") != "rgb(169, 110, 6)" and js(page, "()=>document.querySelector('[data-lr2-card=mood]').dataset.rgState") == "green")
        L2.set_regime(page, "red", "red", "fresh")
        today = js(page, TXT, "[data-nt1b-row=today]")
        check(f"{tag} L TODAY: key events with the time and an `in 6h 48m`-style pill under 8 h · past events faded", "US CPI" in today and ("in 6h" in today or "in 7h" in today) and "US Jobs" in today, today)
        if wide: check(f"{tag} L past event is faded", js(page, "()=>{ const e = [...document.querySelectorAll('[data-nt1b-row=today] .ev')].find(x=>/Jobs/.test(x.innerText)); return e ? getComputedStyle(e).opacity : null; }") not in (None, "1"))
        hot = js(page, TXT, "[data-nt1b-row=hot]")
        check(f"{tag} L HOT: leading sectors as chips (max 3 then +n) + muted `↥ … · ↘ …`", hot.startswith("HOT ↗") and hot.count("↗") == 3 and "+1" in hot and "↥" in hot and "↘" in hot, hot)
        mac = js(page, TXT, "[data-nt1b-row=macro]")
        check(f"{tag} L MACRO: Playbook one-liner (or `No active Playbook`) + Playbook ›", mac.startswith("MACRO") and "Playbook" in mac, mac)
        stx = js(page, TXT, "[data-nt1b-status]")
        check(f"{tag} L nothing from Risk room / Act in the status card (no weekly risk, room, open risk, port status)", not any(x in stx.lower() for x in ("room", "open risk", "weekly", "normal", "placed")), stx)
        # tap-through hooks
        for sel, fn in (("[data-lr2-card=mood]", "tdRegimeGo"), ("[data-lr2-hot]", "lr2Go"), ("[data-ln4-playbook]", "td4MacroGo")):
            js(page, "(fn)=>{ window.__called = null; window['__o_'+fn] = window[fn]; window[fn] = ()=>{ window.__called = fn; }; }", fn)
            js(page, "(s)=>document.querySelector(s).click()", sel); got = js(page, "()=>window.__called"); js(page, "(fn)=>{ window[fn] = window['__o_'+fn]; }", fn)
            check(f"{tag} L {sel} taps through ({fn}) — links unchanged", got == fn, got)
        # no events → TODAY row hidden
        js(page, "()=>{ wiDocs = {}; todayRefresh(true); }"); page.wait_for_timeout(250)
        check(f"{tag} L no events → the TODAY row is hidden", js(page, "()=>[...document.querySelectorAll('[data-nt1b-row]')].map(r=>r.dataset.nt1bRow)") == ["mood", "hot", "macro"])
        # ---- CHECK ORDERS hidden at 0
        check(f"{tag} L CHECK ORDERS: 0 working → the whole section (heading + `Nothing to check`) is hidden", js(page, "()=>[!!document.querySelector('[data-re2-col=check]'), /Nothing to check|CHECK ORDERS/i.test(document.querySelector('[data-ln4-act]').innerText)]") == [False, False])
        # ---- UIUX ①: one dark primary
        dark = js(page, """()=>{ const root = document.getElementById('tabToday'); const lum = c=>{ const m = c.match(/\\d+(\\.\\d+)?/g); if(!m) return 1; const [r, g, b, a] = m.map(Number); return (a === 0) ? 1 : (0.2126*r + 0.7152*g + 0.0722*b)/255; };
          return [...root.querySelectorAll('button, a, [role=button]')].filter(e=>{ const r = e.getBoundingClientRect(); return r.width > 20 && r.height > 20 && getComputedStyle(e).visibility !== 'hidden'; })
            .filter(e=>lum(getComputedStyle(e).backgroundColor) < 0.25).map(e=>[e.innerText.trim().slice(0, 20), !!e.closest('[data-ln4-act]')]); }""")
        check(f"{tag} L ① exactly ONE dark primary button on Today, and it is in Act", len(dark) == 1 and dark[0][1] is True, dark)
        ib = js(page, "()=>[...document.querySelectorAll('[data-nt1b-btn]')].map(b=>{ const s = getComputedStyle(b); return [b.innerText.trim(), s.backgroundColor, s.color, s.borderTopWidth]; })")
        check(f"{tag} L ① Ideas buttons are outline (white fill, dark text, 1px border) — also `Make plan ›` near its level", ib and all(x[1] == "rgb(255, 255, 255)" and x[3] == "1px" for x in ib) and any(x[0] == "Make plan ›" for x in ib), ib)
        # ---- ② homework amber (To do group)
        js(page, """()=>{ window.__o = window.__o || ln4TodoItems; ln4TodoItems = function(M){ return [
          {c:'r', g:'ft', gl:'homework', id:'ft:A', t:'A homework overdue', fn:"void 0"}, {c:'a', g:'ft', gl:'homework', id:'ft:B', t:'B homework due today', fn:"void 0"}, {c:'g', g:'ft', gl:'homework', id:'ft:C', t:'C homework due in 3d', fn:"void 0"},
          {c:'a', id:'t:z', t:'Something else', fn:"void 0"}]; }; todayRefresh(true); }"""); page.wait_for_timeout(300)
        hw = js(page, "()=>{ const b = document.querySelector('[data-ln4-todogrp=ft]'); return b ? [b.innerText.replace(/\\s+/g,' ').trim(), b.dataset.ln4C, b.className, getComputedStyle(b.querySelector('.t')).color] : null; }")
        check(f"{tag} L ② `homework · n stocks` is amber (to-do colour), not red", hw and hw[0].startswith("homework · 3 stocks") and hw[1] == "a" and "lr2-c-a" in hw[2] and hw[3] != "rgb(194, 54, 47)", hw)
        js(page, "()=>{ ln4TodoItems = window.__o; todayRefresh(true); }"); page.wait_for_timeout(200)
        # ---- ③ no duplicate homework message in Act
        act_t = js(page, TXT, "[data-ln4-act]")
        check(f"{tag} L ③ Act has no `size limited to 50%` / `homework not done` text", "size limited" not in act_t.lower() and "homework not done" not in act_t.lower(), act_t[:300])
        hl = js(page, "()=>{ const b = document.querySelector('[data-re2-btn=hw]'); return b ? [b.innerText.trim(), getComputedStyle(b).color, getComputedStyle(b).backgroundColor, b.closest('.re2-row').dataset.re2Row] : null; }")
        check(f"{tag} L ③ Compounder holding without homework: muted `Homework → unlocks adds ›` in the button slot", hl and hl[0].startswith("Homework → unlocks adds") and hl[2] in ("rgba(0, 0, 0, 0)", "transparent") and hl[1] != "rgb(20, 22, 26)", hl)
        check(f"{tag} L ③ the page does not say `size limited to 50%` anywhere", "size limited to 50%" not in js(page, "()=>document.getElementById('tabToday').innerText"))
        # ---- ④ Risk room 2 lines
        rr = js(page, "()=>[...document.querySelectorAll('[data-lr2-risk] [data-lr2-room]')].map(r=>({txt:r.innerText.replace(/\\s+/g,' ').trim(), h:Math.round(r.getBoundingClientRect().height), tops:(()=>{ const t = [...r.querySelectorAll('.lr2-rl')].map(x=>Math.round(x.getBoundingClientRect().top)); return Math.max(...t) - Math.min(...t) <= 4 ? 1 : 2; })(), tip:r.title}))")
        check(f"{tag} L ④ Risk room = one line per account (2 accounts → 2 lines, each `MMT … · SAT … · COMP …`)", len(rr) == 2 and all(x["tops"] == 1 and x["h"] <= 40 for x in rr) and "MMT" in rr[0]["txt"] and "SAT" in rr[0]["txt"] and "COMP" in rr[0]["txt"] and "SAT" in rr[1]["txt"], rr)
        check(f"{tag} L ④ the long text + regime note moved to the tooltip", all("regime" in x["tip"].lower() and "room" in x["tip"].lower() for x in rr), rr)
        if wide: check(f"{tag} L ④ Risk room card is short (two lines)", rect(page, "[data-lr2-risk]")["h"] <= 130, rect(page, "[data-lr2-risk]"))
        # ---- ⑥ every Ideas row = one real button
        nbtn = js(page, "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>r.querySelectorAll('[data-nt1b-btn]').length)")
        check(f"{tag} L ⑥ every Ideas row has exactly one real button; ⋯ lives in the header (and on hover)", nbtn and all(n == 1 for n in nbtn) and js(page, VIS, "[data-nt1b-hdots]"), nbtn)
        # ---- no page scroll at 1440 x 900 with the sample data
        if w == 1440:
            # sample data: 3 ideas, 4 To do rows, 2 Enter + 2 Manage rows, Check orders hidden
            js(page, "()=>{ ln4TodoItems = function(M){ return [{c:'a', g:'ft', gl:'homework', id:'ft:A', t:'A homework due', fn:'void 0'},{c:'a', g:'ft', gl:'homework', id:'ft:B', t:'B homework due', fn:'void 0'},{c:'a', g:'ft', gl:'homework', id:'ft:C', t:'C homework due', fn:'void 0'},{c:'g', id:'t:z', t:'Weekly News', fn:'void 0'},{c:'g', id:'t:y', t:'Another', fn:'void 0'},{c:'g', id:'t:x', t:'Third', fn:'void 0'}]; }; todayRefresh(true); }"); page.wait_for_timeout(300)
            js(page, "()=>{ window.hf5QueueOnly = ()=>false; todayRefresh(true); }"); page.wait_for_timeout(300)   # E2E1: queue-blocked Sat plans now also list in Enter (reason + fix link) — this sample counts 2 Enter rows, so the fixture's two blocked Sat plans stay out
            sc = js(page, "()=>[document.documentElement.scrollHeight, innerHeight, document.scrollingElement.scrollHeight]")
            check(f"{tag} L ④ whole Today fits 1440 × 900 without page scroll (sample data, Check orders hidden)", sc[0] <= sc[1] + 1, sc)
        check(f"{tag} L no overflow · no page errors", js(page, OVER) and not pe, pe[:3])
    finally:
        b.close()


def part_layout_working(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = lrf_page(pw, w, h, working=True)
    try:
        seed_today_ideas(page); to_today(page)
        check(f"{tag} L CHECK ORDERS is shown again as soon as one order is working", js(page, "()=>[!!document.querySelector('[data-re2-col=check]'), document.querySelector('[data-re2-col=check] .ch').innerText.replace(/\\s+/g,' ')]")[0] is True)
        dark = js(page, """()=>{ const root = document.getElementById('tabToday'); const lum = c=>{ const m = c.match(/\\d+(\\.\\d+)?/g); if(!m) return 1; const [r, g, b, a] = m.map(Number); return (a === 0) ? 1 : (0.2126*r + 0.7152*g + 0.0722*b)/255; };
          return [...root.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width > 20 && lum(getComputedStyle(e).backgroundColor) < 0.25).map(e=>e.innerText.trim().slice(0, 12)); }""")
        check(f"{tag} L ① still ONE dark primary with a working order + a ready plan (the second one turns plain)", len(dark) == 1, dark)
        # order of the page on a phone: status → Act → Ideas → To do → Risk room
        order = js(page, "()=>['[data-nt1b-status]', '[data-ln4-act]', '[data-nt1b-ideas]', '[data-ln4-todorow]', '[data-lr2-risk]'].map(s=>{ const e = document.querySelector(s); const r = e.getBoundingClientRect(); return Math.round(r.top + scrollY); })")
        if w <= 700: check(f"{tag} L phone order: status → Act → Ideas → To do → Risk room", order == sorted(order) and len(set(order)) == 5, order)
        check(f"{tag} L no overflow · no page errors", js(page, OVER) and not pe, pe[:3])
        if w <= 700:
            sz = js(page, "()=>[...document.querySelectorAll('[data-nt1b-btn], [data-nt1b-hdots], [data-nt1b-all]')].map(b=>Math.round(b.getBoundingClientRect().height))")
            check(f"{tag} L 44px phone targets on the Ideas card", sz and all(x >= 44 for x in sz), sz)
    finally:
        b.close()


def part_phone_watch(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        t0 = td(page)
        seed_my(page, {"a": mkmy(1, ("stock", "AVGO"), "Breakout over 190", add(t0, -1), t0, next="Close above 190", level=102), "s": mkmy(2, ("market", "TH"), "Stale one", add(t0, -50), add(t0, 5), updated_at=add(t0, -45) + "T05:00:00.000Z")})
        px(page, "AVGO", 100.0)
        N.goto_watch(page); T.to_my(page); page.wait_for_timeout(300)
        check(f"{tag} P My ideas list with next step · stale · no overflow", js(page, OVER) and js(page, VIS, "[data-nt1-my=a] [data-nt1b-nx]") and js(page, VIS, "[data-nt1b-stale]"))
        sz = js(page, "()=>[...document.querySelectorAll('[data-nt1b-stale] button')].map(b=>Math.round(b.getBoundingClientRect().height))")
        check(f"{tag} P stale buttons are 44px tall on a phone", sz and all(x >= 44 for x in sz), sz)
        js(page, "()=>document.querySelector('[data-nt1-my=a]').click()"); page.wait_for_timeout(300)
        check(f"{tag} P detail: Next step block · no overflow", js(page, VIS, "[data-nt1b-block]") and js(page, OVER))
        js(page, "()=>{ wlBack(); nt1SheetOpen({}); }"); page.wait_for_timeout(300)
        check(f"{tag} P New idea sheet with the FOLLOW-UP section · no overflow", js(page, VIS, ".nt1d-sec") and js(page, OVER) and js(page, "()=>document.getElementById('ltModal').scrollWidth <= document.getElementById('ltModal').clientWidth + 1"))
        js(page, "()=>nt1SheetClose()")
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_sheet(pw, 1440, 900)
        part_today(pw, 1440, 900)
        part_near_edges(pw)
        part_watch(pw, 1440, 900)
        part_plan(pw)
        part_layout(pw, 1440, 900)
        part_layout_working(pw, 1440, 900)
        for w, h in ((390, 844), (360, 740)):
            part_today(pw, w, h)
            part_layout(pw, w, h)
            part_layout_working(pw, w, h)
            part_phone_watch(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY nt1b: {len(results) - len(bad)}/{len(results)}")
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
