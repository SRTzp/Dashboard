#!/usr/bin/env python3
"""PL2 — Today/Watch/Sat fixes · เทส 362 (เพิ่มทีละ item) · Chromium · ข้อมูล SAMPLE ล้วน
รัน: python3 run_tests_phase362.py"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase39 as P39
import run_tests_phase54 as P54
import run_tests_phase38 as P38
import run_tests_phase100 as P100
import run_tests_phase107 as P107
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=500): page.wait_for_timeout(ms)


def at(pw, iso, w=390, h=844):
    doc = P38.doc38(clean=True)
    for b in doc["books"].values(): b["settings"].pop("satWeekPick", None)
    return P39.launch(pw, w, h, doc=doc, clean=True, iso=iso, pick=False)


def wi_doc(week):
    return {"schema": "weeklyImpact/v2", "week": week, "asof": week + "T09:00:00+07:00", "sources": {}, "events": {}, "assets": {}}


# ── Item 4 + 1 ──
def item41(pw):
    # Item 4: Today panel label
    b, ctx, page, ce, pe, dl = at(pw, "2026-11-04T05:00:00Z", 1440, 900)
    try:
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 1800)
        lbl = js(page, "()=>[...document.querySelectorAll('[data-td3-panel] .ph, [data-td3-panel] h3, [data-td3-panel] .ttl, [data-td3-panel] b')].map(e=>e.innerText.trim()).join('|')")
        html = js(page, "()=>document.querySelector('[data-td3]') ? document.querySelector('[data-td3]').innerText : ''")
        check("PL2·4 Today panel shows 'Selection' (not 'Core Port')", "selection" in html.lower() and "core port" not in html.lower(), html[:300])
        check("PL2·4 Satellite label kept (Today panel builder)", js(page, "()=>tdBuild.toString().length>0 && document.documentElement.innerHTML.includes(\"P('sat', 'Satellite'\")"))
        check("PL2·4 other 'Core Port' (port definition name) not renamed", js(page, "()=>document.documentElement.innerHTML.includes(\"name:'Core Port'\")"))
    finally:
        b.close()
    # Item 1: Weekly Impact week mapping — Mon 2026-11-02, Sat 2026-11-07, Sun 2026-11-08 (Asia/Bangkok-safe times 05:00Z)
    cases = [("Monday", "2026-11-02T05:00:00Z", "2026-11-02"), ("Saturday", "2026-11-07T05:00:00Z", "2026-11-09"), ("Sunday", "2026-11-08T05:00:00Z", "2026-11-09"),
             ("Wednesday", "2026-11-04T05:00:00Z", "2026-11-02")]
    for nm, iso, mon in cases:
        b, ctx, page, ce, pe, dl = at(pw, iso)
        try:
            r = js(page, """(m)=>{ wiDocs[m] = {id:m, week:m, asof:m+'T02:00:00.000Z', assets:{}, events:{}, sources:{}}; wiLoaded = true; wiErr = null;
              return {cur: wiCurMon(), hasDoc: !!wiCurDoc(), html: wiPanelHtml()}; }""", mon)
            check(f"PL2·1 {nm}: wiCurMon = {mon}, doc for that Monday is CURRENT", r["cur"] == mon and r["hasDoc"], r)
            check(f"PL2·1 {nm}: no 'ต่างสัปดาห์' wrong-week warning", "data-wi-diffweek" not in r["html"], r["html"][:200])
            d = P100.sample(); d["week"] = mon; d["asof"] = mon + "T09:00:00+07:00"
            v = js(page, "(t)=>{ const x = Calc.wiValidate(t, wiAssetCtx()); return {errors:x.errors, warnings:x.warnings, ok: !!x.doc && x.doc.week}; }", json.dumps(d))
            check(f"PL2·1 {nm}: import validation accepts week={mon} (no error/warning about week)", not v["errors"] and v["ok"] == mon and not [x for x in v["warnings"] if "week" in x.lower() or "สัปดาห์" in x], v)
        finally:
            b.close()
    # other-week doc still flagged (regression guard)
    b, ctx, page, ce, pe, dl = at(pw, "2026-11-04T05:00:00Z")
    try:
        r = js(page, "()=>{ wiDocs['2026-10-26'] = {id:'2026-10-26', week:'2026-10-26', asof:'2026-10-26T02:00:00.000Z', assets:{}, events:{}, sources:{}}; wiLoaded = true; wiErr = null; return wiPanelHtml(); }")
        check("PL2·1 a genuinely older week doc is still shown as other-week (guard)", "data-wi-diffweek" in r)
    finally:
        b.close()


# ── Item 2: Unfinished-today banner → real navigation ──
def item2(pw, w=1440, h=900):
    T = P107
    tag = f"[{ENGINE}/{w}/item2]"
    def fresh():
        b, page, ce, pe = T.launch(pw, w, h)
        js(page, "()=>{ window.__toasts = []; const o = window.sdToast; window.sdToast = m=>{ window.__toasts.push(m); o && o(m); }; }")
        T.inject(page, {"candMeta": {"MSFT": T.cm("MSFT", 3, "n1"), "PTT": dict(T.cm("PTT.BK", 2, "n2"), market="TH")}})
        T.clock(page, T.EVE); T.go_today(page)
        return b, page, ce, pe
    state = "()=>({tab: activeTab, wl: (typeof wlView!=='undefined'?wlView:null), scr: typeof scr!=='undefined' && scr ? scr.sym : null, ae: document.activeElement ? (document.activeElement.getAttribute('data-td4-add')!==null) : false, toasts: window.__toasts.slice()})"
    # Deep dive US → Watch workspace of the pick
    b, page, ce, pe = fresh()
    try:
        pick = js(page, "()=>tdLast.hwm.US ? tdLast.hwm.US.t : null")
        page.locator('[data-td4-remgo="hwUS"]').click(); settle(page, 500)
        st = js(page, state)
        check(f"{tag} Deep dive US → opens the Watch workspace for {pick}", pick and st["tab"] == "watch" and js(page, "(t)=>typeof wlOpenSym!=='undefined' ? wlOpenSym===t : true", pick), [pick, st])
        check(f"{tag} Deep dive US → market stays US", js(page, "()=>td4HwMk") == "US")
    finally: b.close()
    b, page, ce, pe = fresh()
    try:
        page.locator('[data-td4-remgo="hwTH"]').click(); settle(page, 500)
        st = js(page, state)
        check(f"{tag} Deep dive TH → switches market to TH and navigates (or toast if no pick)", js(page, "()=>td4HwMk") == "TH" and (st["tab"] == "watch" or st["toasts"]), st)
    finally: b.close()
    # Cand→WL → screening modal for first unscreened candidate
    b, page, ce, pe = fresh()
    try:
        page.locator('[data-td4-remgo="scr"]').click(); settle(page, 600)
        st = js(page, state)
        check(f"{tag} Cand→WL → Watch (Candidates) + screening modal open for a candidate", st["tab"] == "watch" and st["scr"] in ("MSFT", "PTT.BK", "PTT"), st)
    finally: b.close()
    # New Cand → focus the add input
    b, page, ce, pe = fresh()
    try:
        js(page, "()=>switchTab('watch')"); settle(page, 300)
        js(page, "()=>td4RemGo('add', '')")
        settle(page, 400)
        st = js(page, state)
        check(f"{tag} New Cand → navigates to Today and focuses the add input", st["tab"] == "today" and st["ae"], st)
    finally: b.close()
    # Satellite → Plan (Sat) or the Sat/Plans panel
    b, page, ce, pe = fresh()
    try:
        page.locator('[data-td4-remgo="sat"]').click(); settle(page, 600)
        st = js(page, state)
        check(f"{tag} Satellite → opens the outstanding Sat planning task (Plan tab) or the Sat panel on Today", st["tab"] in ("plan", "today") and not st["toasts"], st)
    finally: b.close()
    # Missing target → toast, never silent
    b, page, ce, pe = fresh()
    try:
        js(page, "()=>{ const o = tdBuild; window.tdBuild = ()=>{ const m = o(); m.hwm = {}; return m; }; td4RemGo('hw', 'US'); }"); settle(page, 300)
        st = js(page, state)
        check(f"{tag} Deep dive with no pick → toast 'Couldn't open …' (not silent)", any("Couldn't open" in t for t in st["toasts"]), st)
        js(page, "()=>{ document.querySelectorAll('[data-td4-add]').forEach(e=>e.remove()); td4RemGo('add', ''); }"); settle(page, 200)
    finally: b.close()

# ── Item 6: Sat Verify checkboxes ──
def item6(pw, w=390, h=844):
    tag = f"[{ENGINE}/sat-verify/{w}]"
    b, page, ce, pe = P111.sat_launch(pw, w, h)
    try:
        tid = js(page, "()=>satV2NewPlan('XAUUSD','tactical')"); settle(page, 500)
        js(page, "([i])=>{ satV2SetDir(i,'Long'); }", [tid]); settle(page, 300)
        info = """([i])=>{ const x = satIdeasList.find(y=>y.id===i); const f = document.querySelector('[data-v2-card="tactical"]');
          return {cls: satClsKey(x), legacy: satClsLegacy(x), lock: satTacLock(x, true), ema: x.ema50_ok, st: x.structure_ok, classify: x.classify,
                  ckE: !!(f && f.querySelector('[data-pf-ema50]') && f.querySelector('[data-pf-ema50]').checked), ckS: !!(f && f.querySelector('[data-pf-structure]') && f.querySelector('[data-pf-structure]').checked),
                  hint: (f && f.querySelector('[data-cs-tac-hint]')) ? f.querySelector('[data-cs-tac-hint]').innerText : null, dropdown: document.querySelectorAll('[data-pf-classify-sel]').length,
                  stat: (td3PlanStatus(x)||{}).list}; }"""
        r = js(page, info, [tid])
        check(f"{tag} new Tactical plan: both boxes empty → locked, no dropdown, hint 'Tactical needs EMA50 + Structure verify'", r["lock"] and r["dropdown"] == 0 and r["hint"] == "Tactical needs EMA50 + Structure verify" and r["stat"] == ["Needs EMA50 + Structure verify"], r)
        page.locator("[data-pf-ema50]").first.check(); settle(page, 400)
        r = js(page, info, [tid])
        check(f"{tag} EMA50 only → saved as own boolean, still Unclear + locked", r["ema"] is True and r["st"] is False and r["cls"] == "unclear" and r["lock"] and r["ckE"] and not r["ckS"], r)
        doc = js(page, "([i])=>{ const d = window.firebase.__mockDb; return null; }", [tid])
        page.locator("[data-pf-structure]").first.check(); settle(page, 400)
        r = js(page, info, [tid])
        check(f"{tag} both boxes → Clear Trend, Tactical unlocked, both persisted on the idea", r["ema"] is True and r["st"] is True and r["cls"] == "clear" and not r["lock"] and r["ckE"] and r["ckS"] and r["hint"] is None, r)
        page.locator("[data-pf-ema50]").first.uncheck(); settle(page, 400)
        r = js(page, info, [tid])
        check(f"{tag} un-ticking one box → Unclear again + locked (structure box keeps its value)", r["cls"] == "unclear" and r["lock"] and r["st"] is True and r["ema"] is False and not r["ckE"] and r["ckS"], r)
        saved = js(page, "([i])=>sat7dIdea(i) && {e: sat7dIdea(i).ema50_ok, s: sat7dIdea(i).structure_ok}", [tid])
        check(f"{tag} booleans survive a re-render from the stored idea", saved == {"e": False, "s": True}, saved)
        # legacy plan: stored classify=clear, no verification saved → keeps working + shows legacy note; not auto-ticked
        lid = js(page, "()=>satV2NewPlan('BTCUSD','tactical')"); settle(page, 500)
        js(page, "([i])=>{ satV2SetDir(i,'Long'); satV3IdeaWrite(i,{classify:'clear'}); satV3Render({force:true}); }", [lid]); settle(page, 400)
        r = js(page, info, [lid])
        note = js(page, "()=>document.querySelector('[data-pf-legacy-note]') ? document.querySelector('[data-pf-legacy-note]').innerText : null")
        check(f"{tag} legacy classify=clear: still Clear Trend/unlocked · boxes NOT auto-ticked · 'Legacy classification — verification pending' shown", r["cls"] == "clear" and not r["lock"] and r["legacy"] and not r["ckE"] and not r["ckS"] and r["ema"] is None and note == "Legacy classification — verification pending", [r, note])
        page.locator("[data-pf-ema50]").last.check(); settle(page, 400)
        r = js(page, info, [lid])
        check(f"{tag} legacy: once saved via the new controls the boxes are the source of truth (EMA50 only → Unclear, locked); old classify value left stored", r["cls"] == "unclear" and r["lock"] and not r["legacy"] and r["classify"] == "clear", r)
        # recorded trades untouched
        P78 = __import__("run_tests_phase78")
        P78.put(page, [P78.sat_t("tr1", "open", sleeve="tactical", qty=0.05)])
        t0 = js(page, "()=>JSON.stringify(getBook('main').trades.filter(t=>t.id==='tr1'))")
        js(page, "([i])=>{ pfVerifySet(i,'ema50_ok',false); pfVerifySet(i,'structure_ok',false); }", [lid]); settle(page, 300)
        t1 = js(page, "()=>JSON.stringify(getBook('main').trades.filter(t=>t.id==='tr1'))")
        check(f"{tag} changing verification never alters a recorded trade", t0 == t1 and t0 != "[]", [t0[:80], t1[:80]])
        check(f"{tag} no overflow · no console errors", not C.overflow(page) and not ce and not pe, [C.overflow(page), ce[:2], pe[:2]])
        C.shot(page, "pl2-sat-verify-390.png")
    finally: b.close()


if __name__ == "__main__":
    import sys
    with sync_playwright() as pw:
        item41(pw)
        item2(pw)
        item6(pw)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
