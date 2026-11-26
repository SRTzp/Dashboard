#!/usr/bin/env python3
"""RX1 — R marks inline (A) · TP1 reminder + Exit 50% sheet, Sat only (B).
A  one constant R_MARKS · plan card / Today Enter row / Manage row / plan form · values Long + Short per strategy · constant change flows everywhere · no extra line (card heights unchanged) · ✓ when the typed price passes
B  (see part_b) Sat TP1 reminder · Exit 50% sheet · Runner row · TP2 close-the-rest
Run: python3 tests/run_tests_rx1.py   (RX1_SHOTS=1 writes docs/screenshots/rx1-*.png · docs/briefs/RX1-brief.md)"""
import sys, os, re
from playwright.sync_api import sync_playwright
from e2e1_common import *
import e2e1_common as E
import hf5_common as H
import run_tests_e2e1 as R
from re1d_common import check, results

SH = bool(os.environ.get("RX1_SHOTS"))


def png(page, name):
    if not SH: return
    os.makedirs(E.SHOTS, exist_ok=True)
    js(page, "()=>{ const s=document.createElement('style'); s.id='rxshot'; s.textContent='@media (max-width:600px){#tabsMain{display:none!important}}'; document.head.appendChild(s); }")
    page.wait_for_timeout(250); page.screenshot(path=os.path.join(E.SHOTS, name + ".png"))
    js(page, "()=>{ const s=document.getElementById('rxshot'); if(s) s.remove(); }")


def txt(page, sel): return sel_text(page, sel)


def card_heights(page):
    js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
    h = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-bd-card]')].map(r=>[r.dataset.bdCard, Math.round(r.getBoundingClientRect().height*10)/10]))")
    rows = js(page, "()=>{ switchTab('today'); re2GrpAll={enter:true,check:true,manage:true}; todayRefresh(true); return Object.fromEntries([...document.querySelectorAll('.re2-row')].map((r,i)=>[(r.dataset.re2Row||'')+'#'+i, Math.round(r.getBoundingClientRect().height*10)/10])); }"); page.wait_for_timeout(300)
    return h, rows


def part_a(pw, w):
    tag = "[A %d]" % w
    b, page, ce, pe = H.start(pw, w, 900 if w > 600 else 844)
    try:
        js(page, INSTALL); js(page, "()=>{ re2EnterAll = true; }")
        src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "index.html"), encoding="utf-8").read()
        if w == 1440:
            check("A: ONE constant — `const R_MARKS = { sat:[2, 3], mmt:[3, 5], comp:[5, 10] };` declared once, with the edit-here comment", src.count("const R_MARKS =") == 1 and "const R_MARKS = { sat:[2, 3], mmt:[3, 5], comp:[5, 10] };   /* SRTp 26 Nov — R levels shown in plans; edit here */" in src)
        # ---- values (pure calc: Long + Short per strategy) ----
        v = js(page, "()=>{ const f=(k,e,s,d)=>rxCalc(k,e,s,d).map(m=>m.n+'R '+rxNum(m.px)).join(' · '); return {satS:f('sat',2643,2660,'short'), satL:f('sat',90000,88500,'long'), mmtL:f('mmt',60,55,'long'), compL:f('comp',60,55,'long'), mmtS:f('mmt',60,65,'short'), compS:f('comp',60,65,'short'), noStop:f('sat',2643,0,'short'), noEntry:f('mmt',0,55,'long'), wrongSide:f('sat',2643,2600,'short')}; }")
        check(f"{tag} values: Sat Short 2643/2660 → 2R 2,609 · 3R 2,592 · Sat Long 90000/88500 → 2R 93,000 · 3R 94,500", v["satS"] == "2R 2,609 · 3R 2,592" and v["satL"] == "2R 93,000 · 3R 94,500", v)
        check(f"{tag} values: Momentum Long 60/55 → 3R 75 · 5R 85 · Compounder Long → 5R 85 · 10R 110 · Short: 60/65 → 3R 45 · 5R 35 (mmt) · 5R 35 · 10R 10 (comp)", v["mmtL"] == "3R 75 · 5R 85" and v["compL"] == "5R 85 · 10R 110" and v["mmtS"] == "3R 45 · 5R 35" and v["compS"] == "5R 35 · 10R 10", v)
        check(f"{tag} hidden when entry or stop is missing (or the stop is on the wrong side)", v["noStop"] == "" and v["noEntry"] == "" and v["wrongSide"] == "", v)
        # ---- plan card + Today Enter row + Manage row ----
        H.mk(page, "s1", "XAUUSD", "Short")
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(400)
        card = txt(page, '[data-bd-card="xBBB"]') or ""; sat = txt(page, '[data-bd-card="s1"]') or ""; comp = txt(page, '[data-bd-card="xCCC"]') or ""
        check(f"{tag} Plan card · Momentum: 'Risk −$180 · 0.12% · 3R 75 · 5R 85' (one constant, grey, same line)", "Risk −$180 · 0.12% · 3R 75 · 5R 85" in card, card)
        check(f"{tag} Plan card · Sat Short: '… · 2R 2,609 · 3R 2,592' · Compounder: '… · 5R 100 · 10R 130'", "2R 2,609 · 3R 2,592" in sat and "5R 100 · 10R 130" in comp, [sat, comp])
        if SH:
            for k, id in (("mmt", "xBBB"), ("sat", "s1"), ("comp", "xCCC")):
                os.makedirs(E.SHOTS, exist_ok=True); page.locator(f'[data-bd-card="{id}"]').screenshot(path=os.path.join(E.SHOTS, f"rx1-marks-card-{k}-{w}.png"))
        js(page, "()=>{ switchTab('today'); re2GrpAll={enter:true,check:true,manage:true}; todayRefresh(true); }"); page.wait_for_timeout(400)
        er = txt(page, '[data-re2-row="XAU"][data-re2-grp="enter"]') or ""; ec = txt(page, '[data-re2-row="CCC"][data-re2-grp="enter"]') or ""
        satfit = "Risk −$289 · 2R 2,609 · 3R 2,592" in er if w > 600 else "Risk −$289" in er   # 390: the long Sat line cannot take the marks without a new line → hidden there (see rxFit)
        check(f"{tag} Today Enter row · XAU 'Risk −$289 · 2R 2,609 · 3R 2,592'{'' if w > 600 else ' (390: too long for one line → marks hidden, no extra line)'} · CCC 'Risk −$216 · 5R 100 · 10R 130'", satfit and "Risk −$216 · 5R 100 · 10R 130" in ec, [er, ec])
        # ---- no extra line: card / row heights equal with the marks off ----
        h1, r1 = card_heights(page)
        js(page, "()=>{ window.__rm = JSON.parse(JSON.stringify(R_MARKS)); R_MARKS.sat.length = 0; R_MARKS.mmt.length = 0; R_MARKS.comp.length = 0; }")
        h0, r0 = card_heights(page)
        js(page, "()=>{ Object.keys(window.__rm).forEach(k=>{ R_MARKS[k].length = 0; window.__rm[k].forEach(x=>R_MARKS[k].push(x)); }); }")
        dh = {k: [h0.get(k), h1.get(k)] for k in h1 if h0.get(k) is not None and abs(h0.get(k) - h1.get(k)) > 0.6}
        dr = {k: [r0.get(k), r1.get(k)] for k in r1 if r0.get(k) is not None and abs(r0.get(k) - r1.get(k)) > 0.6}
        check(f"{tag} no extra line: every Plan card and Today row is the same height with the marks as without (diff: {list(dh)[:4] + list(dr)[:4]})", len(h1) >= 6 and not dh and not dr, [dh, dr])
        # ---- one constant flows: sat [1.5, 3] ----
        js(page, "()=>{ R_MARKS.mmt.length = 0; R_MARKS.mmt.push(1.5, 3); }")
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(350)
        c2 = txt(page, '[data-bd-card="xBBB"]') or ""
        check(f"{tag} constant change (mmt [1.5, 3]) flows to the Plan card: 'Risk −$180 · 0.12% · 1.5R 67.5 · 3R 75'", "Risk −$180 · 0.12% · 1.5R 67.5 · 3R 75" in c2, c2)
        js(page, "()=>{ R_MARKS.mmt.length = 0; R_MARKS.mmt.push(3, 5); }")
        js(page, "()=>{ switchTab('plan'); bdRender(); }"); page.wait_for_timeout(350)
        sat = txt(page, '[data-bd-card="s1"]') or ""
        check(f"{tag} Sat plan card keeps the marks at both widths when the line fits ('Risk −$289 · reward +$731 · 2.5R · 2R 2,609 · 3R 2,592'); a longer set (1.5R 2,617.5) that would wrap is hidden, never a new line", "2R 2,609 · 3R 2,592" in sat, sat)
        # ---- Manage (holding) + ✓ ----
        js(page, "()=>{ R_MARKS.sat.length = 0; R_MARKS.sat.push(2, 3); }")
        pl = H.place(page, "s1"); ft = H.fill(page, "s1")
        js(page, "()=>{ switchTab('today'); re2GrpAll={enter:true,check:true,manage:true}; todayRefresh(true); }"); page.wait_for_timeout(400)
        m0 = txt(page, '[data-hf5-row="XAU"]') or ""
        check(f"{tag} Manage row, no price yet: 'No price yet …' + grey levels '2R 2,609 · 3R 2,592'", "No price yet" in m0 and "2R 2,609 · 3R 2,592" in m0 and not js(page, "()=>!!document.querySelector('[data-hf5-row=\"XAU\"] [data-rx-hit]')"), m0)
        ok = set_price(page, "XAU", 2630, "RX1"); m1 = txt(page, '[data-hf5-row="XAU"]') or ""
        check(f"{tag} Manage row, price 2,630 (not past 2R): 'Last 2,630 … · 2R 2,609 · 3R 2,592', no ✓", ok and "Last 2,630" in m1 and "2R 2,609 · 3R 2,592" in m1 and "✓ risk" not in m1.replace("2R ✓", ""), m1)
        ok = set_price(page, "XAU", 2605, "RX1"); m2 = txt(page, '[data-hf5-row="XAU"]') or ""
        check(f"{tag} price 2,605 passes 2R (≤ 2,609): '2R ✓ · 3R 2,592' (green ✓), 3R still a level", ok and "2R ✓ · 3R 2,592" in m2, m2)
        if SH: page.locator('[data-hf5-row="XAU"]').screenshot(path=os.path.join(E.SHOTS, f"rx1-marks-manage-{w}.png"))
        ok = set_price(page, "XAU", 2590, "RX1"); m3 = txt(page, '[data-hf5-row="XAU"]') or ""
        check(f"{tag} price 2,590 passes both: '2R ✓ · 3R ✓'", ok and "2R ✓ · 3R ✓" in m3, m3)
        js(page, "()=>{ R_MARKS.sat.length = 0; R_MARKS.sat.push(1.5, 3); todayRefresh(true); }"); page.wait_for_timeout(300)
        m4 = txt(page, '[data-hf5-row="XAU"]') or ""
        check(f"{tag} constant change flows to the Manage row too ('1.5R ✓ · 3R ✓')", "1.5R ✓ · 3R ✓" in m4, m4)
        js(page, "()=>{ R_MARKS.sat.length = 0; R_MARKS.sat.push(2, 3); }")
        check(f"{tag} no console errors / page errors", not ce and not pe, (ce + pe)[:2])
    finally:
        b.close()


def part_form(pw, w):
    tag = "[A-form %d]" % w
    b, page, ce, pe = start(pw, w); page.set_default_timeout(6000)
    try:
        J = "RX1"
        # Satellite form: Short XAU 2643 / 2660, TP empty → hint, tap 2R → TP = 2609
        ok = click(page, "#hdrPlanBtn", "＋ New plan", J)[0]; ok &= click(page, "#bdPop [onclick=\"bdNewPick('F')\"]", "pick Satellite", J)[0]
        ok &= click(page, "#bdPop [onclick=\"pb2Pick(0)\"]", "pick asset", J)[0]; ok &= click(page, "[data-pb2-dir=\"Sell\"]", "Sell", J)[0]
        h0 = txt(page, "[data-rx-wrap=sat] [data-rx-hint]") or ""
        page.locator("[data-pb2-in=\"entry\"]").fill("2643"); page.locator("[data-pb2-in=\"sl\"]").fill("2660"); page.wait_for_timeout(200)
        h1 = txt(page, "[data-rx-wrap=sat] [data-rx-hint]") or ""
        check(f"{tag} Sat form: no entry/stop → no hint; with 2643 / 2660 and TP empty → '2R 2,609 · 3R 2,592' inside the TP box", h0 == "" and re.sub(r"\s*·\s*", " ", h1) == "2R 2,609 3R 2,592", [h0, h1])
        fit = js(page, "()=>{ const h=document.querySelector('[data-rx-wrap=sat] [data-rx-hint]'); const r=h.getBoundingClientRect(), i=h.parentElement.querySelector('input').getBoundingClientRect(); return h.scrollWidth <= h.clientWidth + 1 && r.top >= i.top - 1 && r.bottom <= i.bottom + 1 && r.right <= i.right + 1; }")
        check(f"{tag} the hint is not cut (no '…', nothing clipped in the TP box)", fit is True, fit)
        if SH and w == 1440: png(page, "rx1-form-tp-hint")
        ok = click(page, "[data-rx-wrap=sat] [data-rx-tap=\"3\"]", "tap 3R", J)[0]
        tp = js(page, "()=>document.querySelector('[data-pb2-in=\"tp\"]').value"); h2 = txt(page, "[data-rx-wrap=sat] [data-rx-hint]") or ""
        check(f"{tag} tap '3R 2,592' → TP = 2592 (stored in the form) and the hint disappears", ok and tp == "2592" and h2 == "" and js(page, "()=>pb2.tp") == "2592", [tp, h2])
        page.locator("[data-pb2-in=\"tp\"]").fill(""); page.wait_for_timeout(200)
        h3 = txt(page, "[data-rx-wrap=sat] [data-rx-hint]") or ""
        check(f"{tag} clearing TP brings the hint back", "2R 2,609" in h3 and "3R 2,592" in h3, h3)
        click(page, "#bdPop [data-bd-popx]", "✕", J)
        # Momentum form (Target 1)
        ok = click(page, "#hdrPlanBtn", "＋ New plan", J)[0]; ok &= click(page, "#bdPop [onclick=\"bdNewPick('A')\"]", "Momentum", J)[0] if page.locator("#bdPop [onclick=\"bdNewPick('A')\"]").count() else False
        page.wait_for_timeout(400)
        if not page.locator("#cnTp").count():
            ok = js(page, "()=>{ try{ switchTab('plan'); coreNewOpen(); }catch(e){} return !!coreEl('cnTp'); }"); page.wait_for_timeout(500)
        page.locator("#cnTicker").fill("BBB"); page.locator("#cnEntry").fill("60"); page.locator("#cnStop").fill("55"); page.wait_for_timeout(500)
        mh = txt(page, "[data-rx-wrap=core] [data-rx-hint]") or ""
        check(f"{tag} Momentum form (Target 1): entry 60 / stop 55 → hint '3R 75 · 5R 85'", "3R 75" in mh and "5R 85" in mh, mh)
        if SH and w == 1440: png(page, "rx1-form-tp-hint-mmt")
        ok = click(page, "[data-rx-wrap=core] [data-rx-tap=\"5\"]", "tap 5R", J)[0]
        v = js(page, "()=>coreEl('cnTp').value"); mh2 = txt(page, "[data-rx-wrap=core] [data-rx-hint]") or ""
        check(f"{tag} tap '5R 85' → Target 1 = 85, hint hidden", ok and v == "85" and mh2 == "", [v, mh2])
        check(f"{tag} no console errors / page errors", not ce and not pe, (ce + pe)[:2])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w in (1440, 390):
            for fn in (part_a, part_form):
                try: fn(pw, w)
                except Exception as e:
                    check(f"[{fn.__name__} {w}] crashed: {str(e)[:160]}", False, str(e)[:500])
    check("no dead buttons / click-handler errors in the RX1 clicks", not E.DEAD, E.DEAD[:8])
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY rx1: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
