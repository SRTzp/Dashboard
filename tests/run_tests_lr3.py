#!/usr/bin/env python3
"""LR3 — Plan board (A) · confirm sheet (B) · plan forms (C).
Screenshots (tests/screenshots, git add -f): lr3-plan-1440 · lr3-plan-390 · lr3-sheet-390 · lr3-sheet-1440 · lr3-form-core-390 · lr3-form-sat-1440
Run: python3 tests/run_tests_lr3.py   (env LR3_PARTS=AB runs only those parts)"""
import os, sys, re, json
from playwright.sync_api import sync_playwright
import net_stub  # no real network in tests
import re1d_common as K
from re1d_common import js, launch, check, results, plan_card

SHOTS = K.SHOTS
def sp(t): return re.sub(r"\s+", " ", t or "").strip()
def ovf(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")
def txt(page, sel): return js(page, "(s)=>{const e=document.querySelector(s);return e?e.innerText.replace(/\\s+/g,' ').trim():''}", sel)
def shot(page, name): page.screenshot(path=os.path.join(SHOTS, name + ".png"))
THAI = re.compile(r"[฀-๿]")


def cards_board():
    cs = {}
    cs["mN"] = plan_card("NVDA", 100, 92, px=99, ready=True)                                   # Main · MMT · also in Family
    cs["mA"] = plan_card("AVGO", 158, 150, px=160, ready=True)
    cs["mA"]["plan"]["ps1"]["rows"] = [{"px": 158, "qty": 20}, {"px": 150, "qty": 20}]          # two entry levels
    cs["mA"]["plan"]["tp"] = 175
    cs["mW"] = plan_card("PLTR", 0, 0, px=30)                                                   # Waiting: needs Entry · SL
    cs["mW"]["plan"] = {"entry": 0, "stop": 0}
    cs["mO"] = plan_card("MSFT", 50, 45, px=49, ready=True); cs["mO"]["ln4"] = {"placedAt": "2026-11-17T01:00:00Z"}   # working order
    cs["mC"] = plan_card("KO", 60, 55, px=61, ready=True); cs["mC"]["track"] = "ladder"         # Main · COMP
    cs["fN"] = plan_card("NVDA", 100, 92, px=99, ready=True); cs["fN"]["acct"] = "fam"; cs["fN"]["market"] = "TH"
    cs["fM"] = plan_card("ZZZ", 40, 36, px=41, ready=True); cs["fM"]["acct"] = "fam"; cs["fM"]["market"] = "TH"   # Family MMT plan (port hidden for Family)
    cs["fC"] = plan_card("BBB.BK", 100, 92, px=99, ready=True); cs["fC"]["acct"] = "fam"; cs["fC"]["market"] = "TH"; cs["fC"]["track"] = "ladder"
    return cs


def goto_plan(page, acct="main"):
    js(page, "(a)=>{ serverConfirmed = true; stateFromServer = true; if(acctActive !== a) acctSwitch(a); bdChip = 'all'; bdSeg = 'plan'; re1Cache = {}; switchTab('plan'); bdRender(); }", acct)
    page.wait_for_timeout(500)


def board(page): return js(page, "()=>({sum: (document.querySelector('[data-bd-sum]')||{}).innerText||'', chips:[...document.querySelectorAll('[data-bd-chip]')].map(b=>b.dataset.bdChip), hidden:[...document.querySelectorAll('[data-bd-hidden]')].map(d=>d.dataset.bdHidden+':'+d.innerText.split('\\n')[0]), cards:[...document.querySelectorAll('[data-bd-card]')].map(c=>c.dataset.bdCard)})")


def partA(page, tag, w):
    goto_plan(page, "main")
    b = board(page)
    check(f"{tag} A: header = N planned · N ordered · N holding · open risk X% / 3% (phone, LR-F: 'Open risk X% / 3% · closest to entry first')", re.search(r"^\d+ planned · \d+ ordered · \d+ holding · open risk [\d.]+% / 3%$", b["sum"]) is not None or (w <= 600 and re.search(r"^Open risk [\d.]+% / 3% · closest to entry first$", b["sum"]) is not None), b["sum"])
    check(f"{tag} A: chips All · MMT · COMP · SAT with port dots", b["chips"] == ["all", "MMT", "COMP", "SAT"] and js(page, "()=>document.querySelectorAll('.bd-chip .bd-dot').length") == 3, b["chips"])
    # open risk = Today's per-account value
    mine = js(page, "()=>re1Pct(lr2OpenRisk('main'))"); today = js(page, "()=>{ switchTab('today'); todayRefresh(true); const e=document.querySelector('[data-lr2-orisk]'); return e ? e.innerText.replace(/\\s+/g,' ') : ''; }")
    page.wait_for_timeout(300); goto_plan(page, "main")
    check(f"{tag} A: open risk on the board ({mine}) equals Today's Act header value", mine in b["sum"] and mine in today, [mine, b["sum"], today])
    js(page, "()=>{ lr2OpenRisk = a=>0.5; bdRender(); }"); page.wait_for_timeout(150)
    check(f"{tag} A: header reads lr2OpenRisk (single source)", "isk 0.50% / 3%" in txt(page, "[data-bd-sum]") or "isk 0.5% / 3%" in txt(page, "[data-bd-sum]"), txt(page, "[data-bd-sum]"))
    # active account only
    check(f"{tag} A: Main board shows Main plans only (no Family-only ZZZ / BBB.BK)", "mN" in b["cards"] and "fM" not in b["cards"] and "fC" not in b["cards"], b["cards"])
    # columns 5:3:4
    if w >= 1280:
        cw = js(page, "()=>[...document.querySelectorAll('.bd-col')].map(c=>Math.round(c.getBoundingClientRect().width))")
        check(f"{tag} A: PC2 columns with cards share the width equally, the empty Ordered one is a slim 240px strip → {cw}", abs(cw[0] - cw[1]) <= 2 and cw[2] <= 241 and cw[0] > cw[2], cw)
    # Waiting row
    wt = js(page, "()=>{ const d = document.querySelector('[data-bd-wait]'); return d ? {open:d.open, t:d.querySelector('summary').innerText.replace(/\\s+/g,' '), n:d.querySelectorAll('[data-bd-card]').length} : null; }")
    check(f"{tag} A: Waiting row collapsed: 'Waiting · 1 need entry or stop ▸'", wt and not wt["open"] and (wt["t"].startswith("Waiting · 1 need entry or stop") or wt["t"].startswith("+1 waiting · need entry or stop")), wt)
    vis = js(page, "()=>{ const c = document.querySelector('[data-bd-card=\"mW\"]'); return !!c && c.checkVisibility(); }")
    check(f"{tag} A: collapsed Waiting hides its card", not vis)
    js(page, "()=>document.querySelector('[data-bd-wait] summary').click()"); page.wait_for_timeout(200)
    js(page, "()=>bdRender()"); page.wait_for_timeout(150)
    vis = js(page, "()=>{ const c = document.querySelector('[data-bd-card=\"mW\"]'); return !!c && c.checkVisibility(); }")
    check(f"{tag} A: Waiting expands in place and stays open after a re-render", vis and js(page, "()=>document.querySelector('[data-bd-wait]').open"))
    js(page, "()=>document.querySelector('[data-bd-wait] summary').click()"); page.wait_for_timeout(150)
    # also in
    al = js(page, "()=>[...document.querySelectorAll('[data-bd-card]')].map(c=>({id:c.dataset.bdCard, also:(c.querySelector('[data-bd-also]')||{}).innerText||null}))")
    by = {x["id"]: x["also"] for x in al}
    check(f"{tag} A: 'also in F ›' only on the ticker both accounts hold (NVDA)", sp(by.get("mN")) == "also in F ›" and by.get("mA") is None and by.get("mO") is None, by)
    # phone segmented tabs
    if w <= 600:
        sg = js(page, "()=>{ const s = document.querySelector('[data-bd-seg]'), c = document.querySelector('[data-bd-chips]'); return {t:[...s.querySelectorAll('button')].map(b=>b.innerText.replace(/\\s+/g,' ')), above: s.getBoundingClientRect().bottom <= c.getBoundingClientRect().top + 1, vis:[...document.querySelectorAll('.bd-col')].filter(c=>c.getClientRects().length).length}; }")
        check(f"{tag} A: phone segmented Planned · Ordered · Holding with counts, above the chips, one column visible", sg["t"][0].startswith("Planned") and sg["t"][1].startswith("Ordered") and sg["t"][2].startswith("Holding") and sg["above"] and sg["vis"] == 3, sg)   # PC2: phone = one column, all three sections stacked
    else:
        check(f"{tag} A: desktop shows all three columns and NO segment control", js(page, "()=>[...document.querySelectorAll('.bd-col')].filter(c=>c.getClientRects().length).length") == 3 and js(page, "()=>getComputedStyle(document.querySelector('[data-bd-seg]')).display") == "none")
    js(page, "()=>{ bdSeg = 'plan'; bdRender(); }")
    if w == 1440: shot(page, "lr3-plan-1440")
    if w == 390: shot(page, "lr3-plan-390")
    check(f"{tag} A: no overflow", ovf(page) <= 0, ovf(page))
    # also in → switches account and scrolls to it
    js(page, "()=>document.querySelector('[data-bd-card=\"mN\"] [data-bd-also]').click()"); page.wait_for_timeout(500)
    st = js(page, "()=>({a:acctActive, tab:activeTab, card: !!document.querySelector('[data-bd-card=\"fN\"]'), vis:(()=>{const c=document.querySelector('[data-bd-card=\"fN\"]'); if(!c) return false; const r=c.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0;})()})")
    check(f"{tag} A: tap switches to Family and shows the Family NVDA card", st["a"] == "fam" and st["card"] and st["vis"], st)
    b2 = board(page)
    check(f"{tag} A: Family hides the MMT chip", b2["chips"] == ["all", "COMP", "SAT"], b2["chips"])
    check(f"{tag} A: Family MMT plan shows under 'Hidden port: MMT (1)'", len(b2["hidden"]) == 1 and b2["hidden"][0].startswith("MMT:Hidden port: MMT (") and "fM" in b2["cards"] and "mN" not in b2["cards"], b2)
    back = js(page, "()=>(document.querySelector('[data-bd-card=\"fN\"] [data-bd-also]')||{}).textContent||null")
    check(f"{tag} A: Family NVDA shows 'also in M ›'", sp(back) == "also in M ›", back)
    # empty column shrinks (Family has no orders)
    ec = js(page, "()=>{ const c = document.querySelector('[data-bd-col=\"ord\"]'); return {empty:c.classList.contains('bd-empty'), h:Math.round(c.getBoundingClientRect().height), t:c.innerText.replace(/\\s+/g,' ')}; }")
    if w > 600:
        check(f"{tag} A: empty Ordered column = slim strip with 'Nothing waiting at the broker.' ({ec['h']} px)", ec["empty"] and ec["h"] <= 140 and "Nothing waiting at the broker." in ec["t"], ec)
    else:
        check(f"{tag} A: empty column carries bd-empty", ec["empty"], ec)
    js(page, "()=>document.querySelector('[data-bd-card=\"fN\"] [data-bd-also]').click()"); page.wait_for_timeout(400)
    check(f"{tag} A: …and back to Main", js(page, "()=>acctActive") == "main")


def partA2(page, tag, w):
    goto_plan(page, "main")
    js(page, "()=>{ const s = getBook('main').settings; s.fx = 33.5; bdRender(); }"); page.wait_for_timeout(300)
    card = txt(page, '[data-bd-card="mN"] [data-pc2-l3]')
    check(f"{tag} F1: Main (USD) plan card shows $ not ฿", "$" in card and "฿" not in card, card)
    # tiles + % of account on the same base as Size %
    js(page, "()=>efCorePlaceOpen('mA')"); page.wait_for_timeout(400)
    t = js(page, "()=>{ const m = document.querySelector('[data-lr3-risk]'), z = document.querySelector('[data-lr3-size]'); const pv = posView(bdById('mA')); const B = lr3Base('main'); return {risk: m.innerText.replace(/\\s+/g,' '), size: z.innerText.replace(/\\s+/g,' '), pct: pv.plannedRisk / B * 100, base: B, weq: re1L('main').basis.weekEquity, cur: (pv.dcur)}; }")
    check(f"{tag} F1: sheet tiles in $ and 'x% of account' uses the engine week equity (same base as Size %)", "$" in t["risk"] and "฿" not in t["risk"] and t["base"] == t["weq"] and (("%.2g" % t["pct"]) in t["risk"] or ("%.1f" % t["pct"]) in t["risk"] or ("%.2f" % t["pct"]) in t["risk"]), t)
    ro = js(page, "()=>{ const e=document.querySelector('[data-ef-order-risk]'); return e ? e.innerText : ''; }")
    check(f"{tag} F1: no ฿ left in the sheet text", "฿" not in txt(page, "[data-ef-core-place]"), txt(page, "[data-ef-core-place]"))
    js(page, "()=>{ bdPopClose(); }")
    # blocked reason = one short line, full text under More
    goto_plan(page, "main")
    bl = js(page, "()=>{ const c=document.querySelector('[data-bd-card=\"mN\"]'); const w=c.querySelector('[data-pc2-warn]'); if(!w) return null; const r=w.getBoundingClientRect(); return {t:w.innerText, title:w.title, h:Math.round(r.height), lh:parseFloat(getComputedStyle(w).lineHeight)||16}; }")
    check(f"{tag} F3: Blocked reason is one short line ('Blocked · MMT weekly limit 4/4')", bl and bl["t"].startswith("⚠ ") and "MMT weekly limit 4/4" in bl["t"] and len(bl["t"]) <= 60 and bl["h"] <= bl["lh"] * 1.6, bl)
    full = bl["title"] if bl else ""   # PC2: the full engine text is the tooltip (and the drawer's amber box)
    check(f"{tag} F3: full engine text is in the tooltip / drawer", len(full) > len(bl["t"]) if bl else False, full)


def heights(pw):
    b, page, ce, pe = launch(pw, 390, 844, c=cards_board())
    try:
        goto_plan(page, "main")
        r = js(page, "()=>({height: document.documentElement.scrollHeight, cards: document.querySelectorAll('[data-bd-card]').length, vis: [...document.querySelectorAll('[data-bd-card]')].filter(c=>c.getClientRects().length).length})")
        print("PLAN390", r)
    finally:
        b.close()


def run(pw, w, h, parts):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h, c=cards_board())
    try:
        page.wait_for_timeout(300)
        if "A" in parts: partA(page, tag, w); partA2(page, tag, w)
        if "B" in parts:
            import lr3_sheet; lr3_sheet.partB(page, tag, w)
        if "C" in parts:
            import lr3_forms; lr3_forms.partC(page, tag, w)
        check(f"{tag} no page errors", not pe, pe)
        check(f"{tag} no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    parts = list(os.environ.get("LR3_PARTS", "ABC"))
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844), (360, 740)):
            run(pw, w, h, parts)
            if "B" in parts:
                import lr3_sheet; lr3_sheet.run_sat(pw, w, h, "[%s]" % w)
            if "C" in parts:
                import lr3_forms; lr3_forms.run_sat(pw, w, h, "[%s]" % w)
        if "A" in parts: heights(pw)
    bad = [r for r in results if not r[1]]
    print("SUMMARY lr3: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
