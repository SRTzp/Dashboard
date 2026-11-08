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
import run_tests_phase44 as P44

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
        check("PL2·4 Satellite label kept (Today panel builder; WK1: Weekend list tags its Sat steps 'SAT')", js(page, "()=>tdBuild.toString().length>0 && document.documentElement.innerHTML.includes(\"tag, 'SAT'\") || document.documentElement.innerHTML.includes(\"'SAT', 'Weekly Impact'\")"))
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

# ── Item 5: trade summary ──
def item5(pw, w=390, h=844):
    tag = f"[{ENGINE}/summary/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        P111.ok_ev(page, "S3", stars=3)
        P111.open_form(page, "S3"); P111.setpx(page, 100, 90)
        S = """()=>({txt: document.getElementById('cnSum').innerText.replace(/\\s+/g,' ').trim(), n: document.querySelectorAll('#cnSum [data-cs-sum]').length,
            qty: (document.querySelector('[data-lf-qty]')||{}).innerText||'', risk: (document.querySelector('[data-lf-first] [data-lf-risk]')||{}).innerText||'',
            sEntry: (document.querySelector('[data-cs-sum=entry] b')||{}).innerText||'', sSl: (document.querySelector('[data-cs-sum=sl] b')||{}).innerText||'', sSize: (document.querySelector('[data-cs-sum=size] b')||{}).innerText||'',
            sRisk: (document.querySelector('[data-cs-sum=risk]')||{}).innerText||'', rs: (document.querySelector('[data-cs-rs]')||{}).innerText||'', miss: [...document.querySelectorAll('#cnSum [data-cs-miss]')].map(x=>x.innerText),
            fe: document.getElementById('cnEntry').value, fs: document.getElementById('cnStop').value})"""
        r = js(page, S)
        check(f"{tag} summary shows 6 parts (Entry · Size · SL · Risk · RS · reasons)", r["n"] == 6, r)
        check(f"{tag} summary == plan form: Entry/SL = inputs, Size = first-lot qty, Risk = first-lot risk", r["sEntry"].replace(",", "") == "100.00" and r["fe"] == "100" and r["sSl"] == "90.00" and r["fs"] == "90" and r["sSize"].replace(",", "") == r["qty"].replace(",", "") and r["qty"] != "" and r["risk"] in r["sRisk"], r)
        check(f"{tag} risk shows money + '% of pool'", "% of pool" in r["sRisk"], r["sRisk"])
        check(f"{tag} RS not rated → 'RS: Unrated' · no reasons → 'No reason tags'", r["rs"] == "RS: Unrated" and "No reason tags" in r["txt"], r)
        # watchlist item with RS stars + reasons
        js(page, "()=>{ wlItems.push({ticker:'S3', market:'US', rs_stars:2, reasons:['strong-rs','volume-spike'], port:'core'}); coreNewIn(); }"); settle(page, 300)
        r2 = js(page, S)
        tags = js(page, "()=>[...document.querySelectorAll('#cnSum [data-cs-reason]')].map(x=>x.innerText)")
        check(f"{tag} RS ★★ + reason labels from the candidate reasons (Strong RS, Volume Spike)", r2["rs"] == "RS ★★☆" and tags == ["Strong RS", "Volume Spike"], [r2["rs"], tags])
        # missing inputs
        js(page, "()=>{ document.getElementById('cnEntry').value = ''; coreNewIn(); }"); settle(page, 300)
        r3 = js(page, S)
        check(f"{tag} no Entry → 'Missing: Entry' for Entry; Size/Risk 'Missing: Entry' (no invented numbers)", "Missing: Entry" in r3["miss"] and r3["sSize"] == "" and r3["sEntry"] == "" and len([m for m in r3["miss"] if "Entry" in m]) >= 3, r3)
        js(page, "()=>{ document.getElementById('cnEntry').value = '100'; document.getElementById('cnStop').value = ''; coreNewIn(); }"); settle(page, 300)
        r4 = js(page, S)
        check(f"{tag} no SL → 'Missing: SL'", "Missing: SL" in r4["miss"] and r4["sSize"] == "", r4)
        js(page, "()=>{ document.getElementById('cnStop').value = '110'; coreNewIn(); }"); settle(page, 300)
        r5 = js(page, S)
        check(f"{tag} Entry below SL → size says 'Missing: Entry above SL' (not a number)", any("Entry above SL" in m for m in r5["miss"]) and r5["sSize"] == "", r5)
        # compounder track
        js(page, "()=>{ document.getElementById('cnEntry').value = '100'; document.getElementById('cnStop').value = '90'; coreNewIn(); }"); settle(page, 300)
        check(f"{tag} no overflow · no console errors", not C.overflow(page) and not ce and not pe, [C.overflow(page), ce[:2], pe[:2]])
        C.shot(page, "pl2-trade-summary-390.png")
    finally: b.close()

# ── Item 3: My Thesis ──
TV = "https://www.tradingview.com/x/AbCdEfGh/"
def item3(pw, w=1440, h=900):
    tag = f"[{ENGINE}/mythesis/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        js(page, "()=>{ window.__READY_REAL = true; }")
        ai = {"date": "2026-09-01", "mode": "full", "summary": {"status": "ok", "biz": "AI business summary text", "call": {"action": "hold", "why": "AI says wait"}}}
        js(page, "([a])=>wlCol().doc('MTA').set({ticker:'MTA', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', my_thesis:{why:'my why line one\\nsecond', exit:'my exit', updated_at:'2026-10-02T00:00:00Z'}, thesis:a, thesis_imported_at:'2026-10-20T00:00:00Z'})", [ai])
        js(page, "()=>wlCol().doc('MTB').set({ticker:'MTB', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'})")
        # legacy notes + image seeded in stockNotes (old Event/Fund./Tech)
        page.evaluate("""()=>window.firebase.__mockDb.__seedDoc(['users','testuid','stockNotes','MTA'], {event:[{id:'e1', d:'2026-09-10', t:'old event note'}], fund:[{id:'f1', d:'2026-09-11', t:'old fund note'}], tech:[{id:'t1', d:'2026-09-12', t:'old tech note', chart:'%s'}], updated_at:'2026-09-12'})""" % TV)
        P44.reload_keep(page)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 600)
        js(page, "()=>wlOpen('MTA')"); settle(page, 700)
        tabs = js(page, "()=>[...document.querySelectorAll('[data-lt-tab]')].map(t=>t.innerText.replace(/\\d+$/, '').trim())")
        check(f"{tag} tab 'มุมมอง' renamed to 'My Thesis'; AI tabs unchanged", "My Thesis" in tabs and "มุมมอง" not in tabs and all(x in tabs for x in ["สรุป", "ธุรกิจ", "ทำไมซื้อ", "ติดตาม", "ออกเมื่อ"]), tabs)
        sm = js(page, "()=>({sum: !!document.querySelector('[data-wl-mt-sum]'), editor: document.querySelectorAll('[data-wl-mt-why]').length})")
        check(f"{tag} Watchlist header has no duplicate My Thesis summary or editor", not sm["sum"] and sm["editor"] == 0, sm)
        js(page, "()=>wlSetSub('view')"); settle(page, 500)
        js(page, "()=>wlMtEditOpen('MTA')"); settle(page, 400)   # TX1 — Read → Edit
        st = js(page, """()=>({editor: document.querySelectorAll('[data-wl-mt-why]').length, legacyRows: document.querySelectorAll('[data-vw-row]').length, aiCard: (document.querySelector('[data-mt-ai]')||{}).dataset ? document.querySelector('[data-mt-ai]').dataset.mtAi : null,
          aiDate: (document.querySelector('[data-mt-ai-date]')||{}).innerText||'', aiSum: (document.querySelector('[data-mt-ai-sum]')||{}).innerText||'', gal: document.querySelectorAll('[data-mt-img]').length,
          notes: [...document.querySelectorAll('[data-mt-note]')].map(n=>n.dataset.mtNote+':'+n.innerText.replace(/\\s+/g,' ').trim()),
          sideBySide: (()=>{ const a = document.querySelector('.mtMain'), c = document.querySelector('.mtAi'); if(!a||!c) return false; const ra = a.getBoundingClientRect(), rc = c.getBoundingClientRect(); return rc.left >= ra.right - 2; })()})""")
        check(f"{tag} My Thesis tab: one editor, no legacy Event/Fund./Tech rows", st["editor"] == 1 and st["legacyRows"] == 0, st)
        check(f"{tag} legacy image shows in the My Thesis gallery", st["gal"] == 1, st)
        check(f"{tag} legacy notes listed with original tag + date (Event · Fund. · Tech)", len(st["notes"]) == 3 and any(n.startswith("event:") and "Event" in n and "old event note" in n for n in st["notes"]) and any(n.startswith("fund:") and "Fund." in n for n in st["notes"]) and any(n.startswith("tech:") and "Tech" in n for n in st["notes"]), st["notes"])
        check(f"{tag} wide screen: AI Thesis preview beside My Thesis with 'imported <date>' + summary", st["aiCard"] == "full" and st["aiDate"] == "imported 2026-10-20" and "AI says wait" in st["aiSum"] and st["sideBySide"], st)
        # edit text + add image -> persists after reload
        page.fill("[data-wl-mt-why]", "edited why"); page.dispatch_event("[data-wl-mt-why]", "input")
        js(page, "()=>wlMtSave('MTA')"); settle(page, 500)
        page.fill("[data-vw-ctx=mt] [data-vw-url]", "https://www.tradingview.com/x/ZzYyXxWw/"); page.dispatch_event("[data-vw-ctx=mt] [data-vw-url]", "input")
        page.locator("[data-vw-ctx=mt] [data-vw-save]").click(); settle(page, 600)
        P44.reload_keep(page)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 500)
        js(page, "()=>{ wlOpen('MTA'); wlSetSub('view'); }"); settle(page, 700)
        js(page, "()=>wlMtEditOpen('MTA')"); settle(page, 300)   # TX1
        after = js(page, "()=>({why: document.querySelector('[data-wl-mt-why]').value, gal: document.querySelectorAll('[data-mt-img]').length, stored: wlItemOf('MTA').my_thesis.why})")
        check(f"{tag} after reload: edited text and both images persist", after["why"] == "edited why" and after["stored"] == "edited why" and after["gal"] == 2, after)
        # import AI -> My Thesis untouched
        before = js(page, "()=>JSON.stringify([wlItemOf('MTA').my_thesis, wlItemOf('MTA').next_check_date||'', snMap['MTA'].tech.map(x=>x.id)])")
        js(page, "([a])=>wlCol().doc('MTA').update({thesis:Object.assign({}, a, {date:'2026-10-25'}), thesis_imported_at:'2026-10-26T00:00:00Z'})", [ai]); settle(page, 600)
        after2 = js(page, "()=>JSON.stringify([wlItemOf('MTA').my_thesis, wlItemOf('MTA').next_check_date||'', snMap['MTA'].tech.map(x=>x.id)])")
        check(f"{tag} AI import leaves My Thesis text/dates/images untouched", before == after2, [before[:120], after2[:120]])
        # saving My Thesis never touches AI data
        thb = js(page, "()=>JSON.stringify(wlItemOf('MTA').thesis)+wlItemOf('MTA').thesis_imported_at")
        page.fill("[data-wl-mt-why]", "edited again"); page.dispatch_event("[data-wl-mt-why]", "input"); js(page, "()=>wlMtSave('MTA')"); settle(page, 500)
        tha = js(page, "()=>JSON.stringify(wlItemOf('MTA').thesis)+wlItemOf('MTA').thesis_imported_at")
        check(f"{tag} saving My Thesis leaves AI Thesis data untouched", thb == tha, [thb[:60], tha[:60]])
        # remove one image -> note text kept
        js(page, "()=>{ window.confirm = ()=>true; }")
        n0 = js(page, "()=>document.querySelectorAll('[data-mt-img]').length")
        page.locator("[data-mt-imgdel]").first.click(); settle(page, 600)
        n1 = js(page, "()=>[document.querySelectorAll('[data-mt-img]').length, snMap['MTA'].tech.map(x=>x.t+'|'+(x.chart?'img':''))]")
        check(f"{tag} remove image works; the note text of that entry stays", n0 == 2 and n1[0] == 1 and any(x.startswith("old tech note") for x in n1[1]), [n0, n1])
        # View AI analysis -> same full AI view
        page.locator("[data-mt-ai-view]").click(); settle(page, 500)
        check(f"{tag} 'View AI analysis' opens the AI summary tab", js(page, "()=>wlSub") == "sum" and js(page, "()=>!!document.querySelector('[data-lt-decide]')"))
        # no AI thesis -> empty state with import action
        js(page, "()=>{ wlOpen('MTB'); wlSetSub('view'); }"); settle(page, 600)
        e = js(page, "()=>({state: (document.querySelector('[data-mt-ai]')||{dataset:{}}).dataset.mtAi, imp: !!document.querySelector('.mtAi [data-mt-import]'), tabs: document.querySelectorAll('[data-lt-tab]').length, editor: document.querySelectorAll('[data-wl-mt-why]').length, legacy: document.querySelectorAll('[data-vw-row]').length})")
        check(f"{tag} no AI thesis: empty state + existing Import action; My Thesis editor still there", e["state"] == "empty" and e["imp"] and e["editor"] == 1 and e["legacy"] == 0, e)
        # candidate card has no legacy block
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); }"); settle(page, 500)
        check(f"{tag} Candidate cards no longer show the Event/Fund./Tech block", js(page, "()=>document.querySelectorAll('[data-vw-row]').length") == 0)
        check(f"{tag} no overflow · no console errors", not C.overflow(page) and not ce and not pe, [C.overflow(page), ce[:2], pe[:2]])
    finally: b.close()

# ── Item 7: Candidate-first workflow ──
def item7(pw, w=1440, h=900):
    import run_tests_phase59 as P59
    tag = f"[{ENGINE}/candidate-first/{w}]"
    ideas = [P59.idea([P59.cand("MIGA", "A", 1, "study"), P59.cand("MIGB", "B", 2, "wait"), P59.cand("PARKX", "P", 3, "park"), P59.cand("BAD!!", "X", 4, "wait"),
                       P59.cand("INWL", "W", 5, "study"), P59.cand("EXIST", "E", 6, "study"), P59.cand("DELX", "D", 7, "study")], iid="i1"),
             P59.idea([], iid="i2"), dict(P59.idea([P59.cand("NOTCNT", "N", 1, "study")], iid="i3"), status="exploring")]
    def mut(doc):
        for bk in doc["books"].values():
            st = bk.setdefault("settings", {})
            st["candMeta"] = {"EXIST": {"manual": True, "sym": "EXIST", "market": "US", "cand_at": "2026-10-01T00:00:00Z"}, "DELX": {"manual": True, "sym": "DELX", "market": "US", "dismissed": True, "dismissed_at": "2026-10-02T00:00:00Z"}}
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, mut=mut, wl=[("INWL", None, {"tier": "A", "tier_set_at": "2026-01-01"})], ideas=ideas)
    try:
        settle(page, 1500)
        rep = js(page, "()=>tdSettings().candFromIdeasDone || null")
        cm = js(page, "()=>tdSettings().candMeta || {}")
        print("MIGRATION REPORT:", json.dumps(rep, ensure_ascii=False))
        check(f"{tag} migration ran once: migrated MIGA + MIGB only (source Event/Sector + idea_id, manual)", rep and rep["migrated"] == 2 and all(cm.get(k, {}).get("source") in ("Event", "Sector") and cm.get(k, {}).get("idea_id") and cm[k].get("manual") is True for k in ("MIGA", "MIGB")), [rep, list(cm)])
        rs = (rep or {}).get("reasons", {})
        check(f"{tag} skipped with reasons: parked, invalid ticker, in Watchlist, already Candidate, deleted, thematic-only, not-counted idea", all(any(k.startswith(p) for k in rs) for p in ("company parked", "no valid ticker", "already in Watchlist", "already in Candidates", "previously deleted", "thematic only", "idea status not counted")), rs)
        check(f"{tag} no skipped ticker was written (PARKX BAD INWL NOTCNT absent)", not any(k in cm for k in ("PARKX", "BAD!!", "INWL", "NOTCNT")) and cm["EXIST"].get("source") is None, list(cm))
        check(f"{tag} Ideas records untouched (3 docs, candidates intact)", js(page, "()=>[ideaList.length, ideaList.find(d=>d.id==='i1').idea.candidates.length]") == [3, 7])
        rows = js(page, "()=>wlRowsAll().cand.map(r=>r.sym).sort()")
        check(f"{tag} Candidates now = migrated + existing manual (no longer derived from Ideas)", rows == ["EXIST", "MIGA", "MIGB"], rows)
        again = js(page, "()=>{ const n0 = Object.keys(tdSettings().candMeta).length; const r = plIdeasMigrate(); return [r, n0, Object.keys(tdSettings().candMeta).length]; }")
        check(f"{tag} idempotent: second run does nothing", again[0] is None and again[1] == again[2], again)
        P44.reload_keep(page); settle(page, 1200)
        cm2 = js(page, "()=>Object.keys(tdSettings().candMeta).sort()")
        check(f"{tag} after reload: still 3 + DELX (no duplicates)", cm2 == ["DELX", "EXIST", "MIGA", "MIGB"], cm2)
        # gate gone: ticker that appears in an Idea can be added as a Candidate
        r = js(page, "()=>{ switchTab('today'); td4Mk='US'; td4AddIn('PARKX'); td4AddCands(); return candPop ? candPop.rows.map(x=>[x.sym, x.err||'']) : null; }")
        check(f"{tag} 'already in Ideas' gate removed (PARKX accepted in the Add Candidate popup)", r and r[0][0] == "PARKX" and r[0][1] == "", r)
        js(page, "()=>candPopClose()")
        # no Ideas stage artefacts
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); }"); settle(page, 500)
        st = js(page, """()=>({back: document.querySelectorAll('[data-td4-backchip],[data-td4-back]').length, pill: [...document.querySelectorAll('.wlPills *')].map(e=>e.innerText).join('|'),
           tqf: document.querySelectorAll('[data-tq-filters],[data-tq-f]').length, tierChip: document.querySelectorAll('[data-wl-tier]').length, tqrow: document.querySelectorAll('[data-tq-row]').length})""")
        check(f"{tag} no 'Back in Ideas', no Tier filter chips, no Tier badges; Ideas pill has no counter", st["back"] == 0 and st["tqf"] == 0 and st["tierChip"] == 0 and "Ideas" in st["pill"] and not any(ch.isdigit() for ch in st["pill"].split("Ideas")[1].split("|")[0]), st)
        js(page, "()=>{ wlSetView('wl'); wlOpen('INWL'); }"); settle(page, 500)
        js(page, "()=>wlOpenEdit('INWL')"); settle(page, 300)
        ed = js(page, "()=>({tierbox: document.querySelectorAll('#wlAddTierBox, [data-wl-tierbtn]').length, chips: document.querySelectorAll('[data-wl-tier]').length, stored: wlItemOf('INWL').tier})")
        check(f"{tag} Edit modal: no Tier selector/button; stored tier data kept; no tier badge on the card", ed["tierbox"] == 0 and ed["chips"] == 0 and ed["stored"] == "A", ed)
        js(page, "()=>wlAddClose()")
        tasks = js(page, "()=>JSON.stringify((tdLast&&tdLast.tasks)||[]).includes('idea-study') || JSON.stringify((tdLast&&tdLast.tasks)||[]).includes('idea-recheck')")
        check(f"{tag} Today has no 'idea-study' / 'idea-recheck' reminders", tasks is False)
        hw = js(page, "()=>[TD_HW_IDS.slice(), TD_HW_SHOW.map(x=>x.id)]")
        check(f"{tag} Deep dive checklist has 4 parts (Business · Why · Monitor · Exit) — no Tier part", hw == [["biz", "why", "next", "exit"], ["biz", "why", "next", "exit"]], hw)
        check(f"{tag} Satellite data untouched (satIdeasList is separate)", js(page, "()=>Array.isArray(satIdeasList)"))
        check(f"{tag} no console errors", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


if __name__ == "__main__":
    import sys
    with sync_playwright() as pw:
        item41(pw)
        item2(pw)
        item6(pw)
        item5(pw)
        item3(pw)
        item7(pw)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
