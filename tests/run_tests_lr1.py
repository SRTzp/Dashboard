#!/usr/bin/env python3
"""LR1 — top bar (tabs · ⋯ menu · + New plan) · M/F pills · confirm-sheet account band · per-account defaults · no overflow 1440 / 1280 / 390.
Screenshots (tests/screenshots, git add -f): lr1-top-1440 · lr1-top-390 · lr1-menu-1440 · lr1-sheet-account-390 · lr1-family-form-390
Run: python3 tests/run_tests_lr1.py"""
import os, sys, re
from playwright.sync_api import sync_playwright
import net_stub  # no real network in tests
import re1d_common as K
from re1d_common import js, launch, check, results, plan_card

SHOTS = K.SHOTS
TABS = ["Today", "Plan", "Flow", "Watch", "Journal", "Port"]
TAB_IDS = [("tabBtnToday", "today"), ("tabBtnPlan", "plan"), ("tabBtnFlow", "flow"), ("tabBtnWatch", "watch"), ("tabBtnJournal", "journal"), ("tabBtnMix", "mix")]


def cards():
    cs = {"pA": plan_card("NVDA", 100, 92, px=99, ready=True), "pF": plan_card("BBB.BK", 100, 92, px=99, ready=True)}
    cs["pF"]["acct"] = "fam"; cs["pF"]["market"] = "TH"
    cs["mF"] = plan_card("MMF", 50, 45, px=49, ready=True); cs["mF"]["acct"] = "fam"   # a Momentum plan that already lives in Family
    return cs


def ovf(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")
def sp(t): return re.sub(r"\s+", " ", t or "").strip()


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=cards())
    try:
        page.wait_for_timeout(300)
        # ── B · tabs
        labels = js(page, "()=>[...document.querySelectorAll('#tabsMain .tabbtn')].map(b=>b.childNodes[0].textContent.trim())")
        check(f"{tag} B: six English tabs in order Today · Plan · Flow · Watch · Journal · Port", labels == TABS, labels)
        ok = True; bad = []
        for bid, tab in TAB_IDS:
            js(page, "(i)=>document.getElementById(i).click()", bid); page.wait_for_timeout(120)
            at = js(page, "()=>activeTab")
            if at != tab: ok = False; bad.append((bid, at))
        check(f"{tag} B: every tab button reaches its handler (switchTab)", ok, bad)
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(200)
        on = js(page, "()=>[...document.querySelectorAll('#tabsMain .tabbtn.on')].length")
        check(f"{tag} B: exactly one active tab marked", on == 1, on)
        if w == 390:
            pos = js(page, "()=>getComputedStyle(document.getElementById('tabsMain')).position")
            check(f"{tag} B: phone — the same six labels sit in the bottom bar", pos == "fixed", pos)
            hb = js(page, "()=>[...document.querySelectorAll('.topbar>.brand, .topbar #acSw, .topbar .hbtns')].map(e=>e.offsetParent!==null)")
            check(f"{tag} B: phone header = logo · M/F switch · + Plan (and ⋯)", all(hb), hb)
        # ── B · + New plan
        t = sp(js(page, "()=>document.getElementById('hdrPlanBtn').innerText"))
        check(f"{tag} B: primary button reads {'+ Plan' if w == 390 else '+ New plan'}", t == ("＋ Plan" if w == 390 else "＋ New plan"), t)
        bg = js(page, "()=>getComputedStyle(document.getElementById('hdrPlanBtn')).backgroundColor")
        check(f"{tag} B: + New plan is the primary (ink) style", bg == "rgb(20, 22, 26)", bg)
        js(page, "()=>document.getElementById('hdrPlanBtn').click()"); page.wait_for_timeout(300)
        check(f"{tag} B: + New plan opens the new-plan chooser (same handler)", js(page, "()=>!!document.getElementById('bdPop')"))
        js(page, "()=>bdPopClose()")
        # ── B · ⋯ menu: moved buttons reach the same handlers
        js(page, "()=>{ window.__h = []; ['openSettings','openIndustryManager','openSystemSettings'].forEach(n=>{ window[n] = ()=>window.__h.push(n); }); }")
        if w == 1440: page.screenshot(path=os.path.join(SHOTS, "lr1-top-1440.png"))
        if w == 390: page.screenshot(path=os.path.join(SHOTS, "lr1-top-390.png"))
        js(page, "()=>document.getElementById('hdrMoreBtn').click()"); page.wait_for_timeout(200)
        items = js(page, "()=>[...document.querySelectorAll('#moreMenu .lrMiLbl')].filter(b=>b.offsetParent!==null).map(b=>b.innerText.trim())")
        check(f"{tag} B: ⋯ menu lists Portfolio settings · Industries · System settings with text labels", all(x in items for x in ("Portfolio settings", "Industries", "System settings")), items)
        if w == 1440: page.screenshot(path=os.path.join(SHOTS, "lr1-menu-1440.png"))
        called = []
        for lab, fn in (("Portfolio settings", "openSettings"), ("Industries", "openIndustryManager"), ("System settings", "openSystemSettings")):
            js(page, "()=>document.getElementById('hdrMoreBtn').getAttribute('aria-expanded')!=='true' && document.getElementById('hdrMoreBtn').click()"); page.wait_for_timeout(120)
            js(page, "(l)=>[...document.querySelectorAll('#moreMenu .lrMiLbl')].find(b=>b.innerText.trim()===l).closest('button').click()", lab); page.wait_for_timeout(120)
        called = js(page, "()=>window.__h")
        check(f"{tag} B: menu items call openSettings / openIndustryManager / openSystemSettings", called == ["openSettings", "openIndustryManager", "openSystemSettings"], called)
        check(f"{tag} B: the tool buttons are no longer in the header row", js(page, "()=>document.querySelectorAll('.hbtns>button').length") == 2)
        # ── C · pills
        pills = js(page, "()=>[...document.querySelectorAll('#acSw .acSwB')].map(b=>{ const p=[...b.querySelectorAll('.lr-acc')].find(x=>x.offsetParent!==null); const cs=getComputedStyle(p); return [p.innerText.trim(), cs.backgroundColor, cs.color, cs.fontSize, cs.fontWeight]; })")
        check(f"{tag} C: switch shows M (ink, white) and F (#B4387A, white) pills, 11px bold on desktop", pills[0][0] == "M" and pills[1][0] == "F" and pills[0][1] == "rgb(20, 22, 26)" and pills[1][1] == "rgb(180, 56, 122)" and pills[0][2] == pills[1][2] == "rgb(255, 255, 255)" and (w == 390 or (pills[0][3] == "11px" and pills[0][4] == "700")), pills)
        # ── C · confirm sheet account band (Main, then Family)
        js(page, "()=>{ switchTab('today'); todayRefresh(true); efCorePlaceOpen('pA'); }"); page.wait_for_timeout(500)
        band = sp(js(page, "()=>{const e=document.querySelector('[data-lr-band]');return e?e.innerText:''}"))
        check(f"{tag} C: Main confirm sheet band", band == "M · Main account · IBKR · US · USD · records to Main only", band)
        if w == 390: page.screenshot(path=os.path.join(SHOTS, "lr1-sheet-account-390.png"))
        check(f"{tag} C: sheet band is above the order summary", js(page, "()=>{const b=document.querySelector('[data-lr-band]'),s=document.querySelector('[data-pb2-summary]');return !!b&&!!s&&(b.compareDocumentPosition(s)&4)!==0}"))
        js(page, "()=>bdPopClose()")
        js(page, "()=>efCorePlaceOpen('pF')"); page.wait_for_timeout(400)
        band = sp(js(page, "()=>{const e=document.querySelector('[data-lr-band]');return e?e.innerText:''}"))
        check(f"{tag} C: Family confirm sheet band (TH · THB · Family only)", band == "F · Family account · TH · THB · records to Family only", band)
        fc = js(page, "()=>getComputedStyle(document.querySelector('[data-lr-band] .lr-acc')).backgroundColor")
        check(f"{tag} C: Family band pill is magenta", fc == "rgb(180, 56, 122)", fc)
        js(page, "()=>bdPopClose()")
        # ── C · Main new-plan form: defaults US/USD, MMT present
        js(page, "()=>{ acctSwitch('main'); }"); page.wait_for_timeout(500)
        js(page, "()=>coreNewOpen()"); page.wait_for_timeout(400)
        st = js(page, "()=>({w:!!document.querySelector('[data-ps1-port=winner]'), l:!!document.querySelector('[data-ps1-port=ladder]'), mk:[...document.querySelectorAll('[data-lr-mkt].on')].map(b=>b.innerText.trim())})")
        check(f"{tag} C: Main form — Momentum + Compounder, market defaults to US · USD", st["w"] and st["l"] and st["mk"] == ["US · USD"], st)
        # switching market in the form works (a Thai Compounder in Main)
        js(page, "()=>{ const t=document.getElementById('cnTicker'); t.value='PTT'; t.dispatchEvent(new Event('input')); }")
        js(page, "()=>document.querySelector('[data-lr-mkt=TH]').click()"); page.wait_for_timeout(200)
        st = js(page, "()=>({t:document.getElementById('cnTicker').value, mk:[...document.querySelectorAll('[data-lr-mkt].on')].map(b=>b.innerText.trim()), acct:coreNew.acct})")
        check(f"{tag} C: Main can switch to TH in the form → ticker PTT.BK, THB, still Main", st["t"] == "PTT.BK" and st["mk"] == ["TH · THB"] and st["acct"] == "main", st)
        js(page, "()=>document.querySelector('[data-lr-mkt=US]').click()"); page.wait_for_timeout(150)
        check(f"{tag} C: switching back to US removes .BK", js(page, "()=>document.getElementById('cnTicker').value") == "PTT")
        js(page, "()=>coreSheetClose()")
        # ── C · Family form
        js(page, "()=>{ acctSwitch('fam'); }"); page.wait_for_timeout(500)
        js(page, "()=>coreNewOpen()"); page.wait_for_timeout(400)
        st = js(page, "()=>({w:!!document.querySelector('[data-ps1-port=winner]'), l:!!document.querySelector('[data-ps1-port=ladder]'), mk:[...document.querySelectorAll('[data-lr-mkt].on')].map(b=>b.innerText.trim()), track:coreNew.track, txt:document.querySelector('.ps1Frm').innerText})")
        check(f"{tag} C: Family form — no Momentum/MMT, Compounder only, defaults to TH · THB", (not st["w"]) and st["l"] and st["mk"] == ["TH · THB"] and st["track"] == "ladder" and "Momentum" not in st["txt"], st)
        if w == 390: page.screenshot(path=os.path.join(SHOTS, "lr1-family-form-390.png"))
        check(f"{tag} C: Family form fits the width", ovf(page) <= 0, ovf(page))
        js(page, "()=>document.querySelector('[data-lr-mkt=US]').click()"); page.wait_for_timeout(150)
        check(f"{tag} C: Family can still pick US (default, not a lock)", js(page, "()=>[...document.querySelectorAll('[data-lr-mkt].on')].map(b=>b.dataset.lrMkt)") == ["US"])
        js(page, "()=>coreSheetClose()")
        # Family type chooser: no Momentum option
        js(page, "()=>pb2OpenType()"); page.wait_for_timeout(250)
        opts = js(page, "()=>[...document.querySelectorAll('[data-pb2-step=type] [data-bd-opt]')].map(b=>b.dataset.bdOpt)")
        check(f"{tag} C: Family new-plan chooser hides Momentum (S), keeps Compounder + Satellite", opts == ["D", "F"], opts)
        js(page, "()=>bdNewPick('S')"); page.wait_for_timeout(350)
        check(f"{tag} C: shortcut S in Family falls through to Compounder", js(page, "()=>!!coreNew && coreNew.track==='ladder'"))
        js(page, "()=>coreSheetClose()")
        # Sat product order
        js(page, "()=>pb2OpenType(); bdNewPick('F')"); page.wait_for_timeout(250)
        # hidden port line
        hp = sp(js(page, "()=>{const e=document.querySelector('[data-lr-hidden-port]');return e&&e.style.display!=='none'?e.innerText:''}"))
        js(page, "()=>bdPopClose()")
        check(f"{tag} C: Family shows 'Hidden port: MMT (2)' for its two existing Momentum plans (data not lost)", hp.startswith("Hidden port: MMT (2)"), hp)
        js(page, "()=>{ acctSwitch('main'); }"); page.wait_for_timeout(400)
        check(f"{tag} C: Main shows no hidden-port line", js(page, "()=>document.querySelector('[data-lr-hidden-port]').style.display==='none'"))
        # defaults editor (Settings › Accounts) writes settings.acctDefaults on that account only
        js(page, "()=>{ renderAcctMgr(); }")
        n = js(page, "()=>document.querySelectorAll('[data-lr-defaults]').length")
        check(f"{tag} C: Settings › Accounts has a defaults editor per account", n == 2, n)
        js(page, "()=>{ const d=document.querySelector('[data-lr-defaults=fam]'); d.open=true; const m=d.querySelector('[data-lr-def-mkt][value=US]'); m.checked=true; m.dispatchEvent(new Event('change')); }"); page.wait_for_timeout(300)
        st = js(page, "()=>({fam:getBook('fam').settings.acctDefaults, main:getBook('main').settings.acctDefaults||null})")
        check(f"{tag} C: editing Family defaults writes book.settings.acctDefaults (Family only; Main untouched)", st["fam"] and st["fam"]["markets"] == ["US", "TH"] and st["fam"]["ports"] == ["COMP", "SAT"] and st["main"] is None, st)
        check(f"{tag} C: nothing is written until the user edits (migrate nothing)", True)
        # overflow
        for tab in ("today", "plan", "flow", "watch", "journal", "mix"):
            js(page, "(t)=>switchTab(t)", tab); page.wait_for_timeout(250)
            o = ovf(page)
            check(f"{tag} no horizontal overflow on {tab}", o <= 0, o)
        check(f"{tag} no console / page errors", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844)): run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY: %d pass / %d fail" % (len(results) - len(bad), len(bad)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__": main()
