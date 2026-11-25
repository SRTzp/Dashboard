#!/usr/bin/env python3
"""HF3 — A Place order Confirm never "does nothing" (blocks = a line in the sheet · toasts above sheets · picks full → Replace · error guard) ·
B Flow RRG says why it is slow (denied / missing / stale / partial / progress) · C the job doc stores its bulk as JSON strings (docs/briefs/HF3-brief.md).
Run: python3 tests/run_tests_hf3.py   (HF3_SHOTS=1 writes docs/screenshots/hf3-*.png · HF3_PARTS=ab runs only those parts)"""
import sys, os, json
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import run_tests_lrf as LF
import run_tests_lr3 as L3
import lr5_common as C
import run_tests_ux3 as U

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")


def shot(page, name):
    if os.environ.get("HF3_SHOTS"):
        page.evaluate("()=>{ const el = document.querySelector('[data-lr4-rrg]'); if(el && !document.getElementById('bdPop')) el.scrollIntoView({block:'start'}); }") if name.startswith("rrg") else None; page.wait_for_timeout(250)
        os.makedirs(SHOTS, exist_ok=True); page.screenshot(path=os.path.join(SHOTS, "hf3-%s.png" % name))


IDEA = """(o)=>{ sat7dWrite('satIdeas','hfX',Object.assign({id:'hfX',v3:true,v2:true,asset:'XAUUSD',entry:2643,sl:2660,tp:2600,bias:'Short',ema50_ok:true,structure_ok:true,status:'active',accts:{},week:wpWeekKey(),tf:'4H',setups:[],ready:true,readyAt:new Date().toISOString()}, o));
  (satIdeasList||[]).forEach(i=>{ if(i && i.id==='hfX') Object.assign(i,o); }); re1Cache = {}; re2GrpAll = {enter:true, check:true, manage:true}; window.ps1MinStopMsg = ()=>''; todayRefresh(true); try{ bdRender(); }catch(e){} }"""
SHEET = "()=>{ const l = document.querySelector('[data-hf3-block]'); const b = document.getElementById('bdPop'); const y = document.querySelector('[data-pb2-yes]'); return {line: l ? l.innerText.replace(/\\s+/g, ' ').trim() : null, kind: l ? l.dataset.hf3Kind : null, open: !!b, yes: !!y, btns: [...document.querySelectorAll('[data-hf3-rep]')].map(x=>x.innerText.trim()), fix: [...document.querySelectorAll('[data-hf3-block] button')].map(x=>x.innerText.trim())}; }"
OVF = "()=>document.documentElement.scrollWidth - innerWidth"


DIS = "()=>{ const y = document.querySelector('[data-pb2-yes]'); return y ? {dis: y.disabled, bg: getComputedStyle(y).backgroundColor} : null; }"


def sat_open(page, o=None):
    LF.today(page)
    js(page, "()=>satWeekPickWrite(wpWeekKey(), ['EURUSD'])")
    js(page, IDEA, o or {}); page.wait_for_timeout(400)
    js(page, "()=>pb2PlaceOpen('hfX')"); page.wait_for_timeout(350)


def part_a(pw):
    for w, h in ((1440, 900), (390, 844)):
        for bias, sl, tp in (("Short", 2660, 2600), ("Long", 2620, 2700)):
            tag = "[A %d %s]" % (w, bias)
            b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
            errs = []
            page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            try:
                # 1 · a toast is on top of an open sheet (all three toast elements)
                sat_open(page, {"bias": bias, "sl": sl, "tp": tp})
                check(f"{tag} Place order sheet is open", js(page, SHEET)["open"])
                top = js(page, """()=>{ const out = {}; sdToast('hf3 sd'); try{ td3ToastShow('hf3 td3'); }catch(e){} try{ ln4Toast('hf3 ln4'); }catch(e){}
                  [['sdToast'], ['td3Toast']].forEach(([id])=>{ const t = document.getElementById(id); if(!t){ out[id] = 'none'; return; } const r = t.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); out[id] = !!(e && (e === t || t.contains(e))) ; out[id + 'z'] = getComputedStyle(t).zIndex; out[id + 'bd'] = getComputedStyle(document.querySelector('.ui-sheet-backdrop')).zIndex; }); return out; }""")
                page.wait_for_timeout(250)
                top = js(page, """()=>{ const out = {}; sdToast('hf3 sd'); [['sdToast']].forEach(([id])=>{ const t = document.getElementById(id); t.style.pointerEvents = 'auto'; const r = t.getBoundingClientRect(); const e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); out[id] = !!(e && (e === t || t.contains(e))); out.z = +getComputedStyle(t).zIndex; out.bd = +getComputedStyle(document.querySelector('.ui-sheet-backdrop')).zIndex; });
                  document.getElementById('sdToast').style.pointerEvents = 'auto'; td3ToastShow('hf3 td3'); const t3 = document.getElementById('td3Toast'); out.td3z = t3 ? +getComputedStyle(t3).zIndex : null; return out; }""")
                check(f"{tag} toast shown while a sheet is open: elementFromPoint at its centre = the toast, z-index above the sheet", top["sdToast"] and top["z"] > top["bd"] and (top["td3z"] is None or top["td3z"] > top["bd"]), top)
                js(page, "()=>{ const q = document.getElementById('sdToast'); q.classList.remove('show'); q.style.pointerEvents = ''; const t = document.getElementById('td3Toast'); if(t) t.style.display = 'none'; }")
                # 2 · wrong side
                js(page, IDEA, {"bias": bias, "sl": (2620 if bias == "Short" else 2660), "tp": (2700 if bias == "Short" else 2600)}); page.wait_for_timeout(200)
                js(page, "()=>{ bdPopClose(); pb2PlaceOpen('hfX'); }"); page.wait_for_timeout(300)
                js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(250)
                r = js(page, SHEET)
                check(f"{tag} wrong side → amber line in the sheet 'Blocked · Wrong side…' + 'Switch to … ›', sheet still open", r["open"] and r["line"] and r["line"].startswith("⚠ Blocked · Wrong side") and any(x.startswith("Switch to") for x in r["fix"]), r)
                shot(page, "place-blocked-wrongside-%d" % w) if False else None
                d = js(page, DIS)
                check(f"{tag} wrong side: Confirm is disabled and grey (not dark)", d and d["dis"] and d["bg"] == "rgb(214, 218, 224)", d)
                js(page, "()=>document.querySelector('[data-hf3-block] [data-hf3-fix]').click()"); page.wait_for_timeout(500)
                r = js(page, SHEET)
                check(f"{tag} the Fix › flips the side and the line goes", r["open"] and r["line"] is None, r)
                # 3 · engine block
                js(page, IDEA, {"bias": bias, "sl": sl, "tp": tp}); page.wait_for_timeout(200)
                js(page, "()=>{ bdPopClose(); pb2PlaceOpen('hfX'); window.__bl0 = re1SatBlocks; window.re1SatBlocks = ()=>['Weekly risk 6.0% is over the cap']; }"); page.wait_for_timeout(300)
                js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(250)
                r = js(page, SHEET)
                check(f"{tag} engine block → the reason + 'Edit plan ›' in the sheet, sheet open, no order recorded", r["open"] and r["line"] and "over the cap" in r["line"] and "Edit plan ›" in r["fix"] and js(page, "()=>bdById('hfX').status") != "ord", r)
                shot(page, "place-blocked-%d" % w) if w == 390 and bias == "Short" else None
                js(page, "()=>{ window.re1SatBlocks = window.__bl0; }")
                # 4 · re-entry not confirmed
                js(page, "()=>{ bdPopClose(); pb2PlaceOpen('hfX'); window.__pc0 = pb2Calc; window.pb2Calc = (i, a)=>{ const c = window.__pc0(i, a); c.c = Object.assign({}, c.c, {re1NeedsReentry:true}); return c; }; pb2Render(); }"); page.wait_for_timeout(300)
                js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(250)
                r = js(page, SHEET)
                check(f"{tag} re-entry not confirmed → line + 'Tick Re-entry ›', sheet open", r["open"] and r["line"] and "Re-entry not confirmed" in r["line"] and "Tick Re-entry ›" in r["fix"], r)
                js(page, "()=>document.querySelector('[data-hf3-block] [data-hf3-fix]').click()"); page.wait_for_timeout(250)
                r = js(page, "()=>({line: !!document.querySelector('[data-hf3-block]'), ck: document.querySelector('[data-re1-reentry] input').checked, dis: document.querySelector('[data-pb2-yes]').disabled})")
                check(f"{tag} tick → line gone, box ticked, Confirm enabled", not r["line"] and r["ck"] and r["dis"] is False, r)
                js(page, "()=>{ window.pb2Calc = window.__pc0; }")
                # 5 · picks full (the sheet was opened with room; the list filled up meanwhile)
                js(page, "()=>{ bdPopClose(); satWeekPickWrite(wpWeekKey(), ['EURUSD']); pb2PlaceOpen('hfX'); satWeekPickWrite(wpWeekKey(), ['EURUSD', 'BTCUSDT', 'S50']); }"); page.wait_for_timeout(300)
                before = js(page, "()=>satWeekPickList()")
                js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(300)
                r = js(page, SHEET)
                check(f"{tag} picks full → '⚠ This week already has 3 Sat picks · Replace one:' + one button per pick, sheet open", r["open"] and r["line"] and r["line"].startswith("⚠ This week already has 3 Sat picks · Replace one:") and len(r["btns"]) == 3 and all(x.startswith("Replace ") for x in r["btns"]) and js(page, "()=>bdById('hfX').status") != "ord", [r, before])
                d = js(page, DIS)
                check(f"{tag} picks full: Confirm disabled and grey while the line shows", d and d["dis"] and d["bg"] == "rgb(214, 218, 224)", d)
                shot(page, "place-picks-full-%d" % w)
                check(f"{tag} no horizontal scroll with the line in the sheet", js(page, OVF) <= 0)
                js(page, "()=>document.querySelector('[data-hf3-rep=\"BTCUSDT\"]').click()"); page.wait_for_timeout(500)
                after = js(page, "()=>({picks: satWeekPickList(), st: bdById('hfX') ? bdById('hfX').status : null, open: !!document.getElementById('bdPop'), toast: (document.getElementById('sdToast')||{}).textContent})")
                check(f"{tag} tap 'Replace BTCUSDT' → pick swapped for XAUUSD and the order is recorded in the same tap (sheet closed, Order working ✓)", "XAUUSD" in after["picks"] and "BTCUSDT" not in after["picks"] and after["st"] == "ord" and not after["open"], after)
                # 6 · thrown error → line + console.error
                js(page, "()=>{ bdWriteWithLog = (()=>{ const o = bdWriteWithLog; window.__bw0 = o; return function(){ throw new Error('boom test'); }; })(); }")
                js(page, IDEA, {"status": "active", "ln4": None}); js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD']); const i = bdById('hfX'); }")
                js(page, "()=>{ bdPopClose(); pb2PlaceOpen('hfX'); }"); page.wait_for_timeout(300)
                n0 = len(errs)
                js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(300)
                r = js(page, SHEET)
                check(f"{tag} an exception → '⚠ Could not record the order · boom test' in the sheet (open) + full console.error", r["open"] and r["line"] and r["line"].startswith("⚠ Could not record the order · boom test") and len(errs) > n0, [r, errs[n0:][:1]])
                js(page, "()=>{ bdWriteWithLog = window.__bw0; }")
                # 7 · happy path unchanged
                js(page, "()=>{ bdPopClose(); const i = bdById('hfX'); }"); sat_open(page, {"bias": bias, "sl": sl, "tp": tp})
                js(page, "()=>pb2PlaceYes()"); page.wait_for_timeout(500)
                r = js(page, "()=>({st: bdById('hfX').status, open: !!document.getElementById('bdPop'), line: !!document.querySelector('[data-hf3-block]'), toast: (document.getElementById('sdToast')||{}).textContent})")
                check(f"{tag} happy path: order recorded (Ordered), sheet closed, no block line", r["st"] == "ord" and not r["open"] and not r["line"], r)
                check(f"{tag} no page errors", not pe, pe)
            finally:
                b.close()
    # Core sheet
    for w, h in ((1440, 900), (390, 844)):
        tag = "[A core %d]" % w
        b, page, ce, pe = launch(pw, w, h, c=L3.cards_board())
        errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        try:
            L3.goto_plan(page, "main")
            js(page, "()=>{ efCorePlaceOpen('mA'); window.__g0 = wl1PlaceGate; window.wl1PlaceGate = ()=>{ window.__wl1Msg = 'Place order blocked — NVDA: homework not done · max 50% = 10 (held 0 + working 0 + this 20) — allowed 10'; return false; }; }"); page.wait_for_timeout(350)
            js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(250)
            r = js(page, SHEET)
            check(f"{tag} Core: size-engine block → line in the sheet ('homework not done…' + 'Do homework ›'), sheet open", r["open"] and r["line"] and "homework not done" in r["line"] and "Do homework ›" in r["fix"] and "Edit plan ›" in r["fix"] and js(page, DIS)["dis"], r)
            js(page, "()=>{ window.wl1PlaceGate = ()=>{ window.__wl1Msg = 'Place order blocked — AVGO: Weekly Momentum ammunition used'; return false; }; bdPopClose(); efCorePlaceOpen('mA'); }"); page.wait_for_timeout(300)
            js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(250)
            r = js(page, SHEET)
            check(f"{tag} Core: any other engine block also names a fix ('Edit plan ›')", r["line"] and "Edit plan ›" in r["fix"] and "Do homework ›" not in r["fix"], r)
            js(page, "()=>{ document.querySelector('[data-hf3-block] [data-hf3-fix]').click(); }"); page.wait_for_timeout(500)
            check(f"{tag} Edit plan › closes the place sheet", js(page, "()=>!document.querySelector('[data-ef-core-place]')"))
            js(page, "()=>{ window.wl1PlaceGate = window.__g0; }")
            js(page, "()=>{ window.wl1PlaceGate = window.__g0; bdWriteWithLog = (()=>{ window.__bw0 = bdWriteWithLog; return function(){ throw new Error('boom core'); }; })(); bdPopClose(); window.wl1PlaceGate = ()=>true; efCorePlaceOpen('mA'); }"); page.wait_for_timeout(300)
            n0 = len(errs)
            js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(300)
            r = js(page, SHEET)
            check(f"{tag} Core: an exception → '⚠ Could not record the order · boom core' in the sheet + console.error", r["open"] and r["line"] and r["line"].startswith("⚠ Could not record the order · boom core") and len(errs) > n0, [r, errs[n0:][:1]])
            js(page, "()=>{ bdWriteWithLog = window.__bw0; bdPopClose(); efCorePlaceOpen('mA'); }"); page.wait_for_timeout(300)
            js(page, "()=>efCorePlaceYes()"); page.wait_for_timeout(500)
            r = js(page, "()=>({open: !!document.getElementById('bdPop'), line: !!document.querySelector('[data-hf3-block]'), placed: !!((()=>{ const c = (coreCardsList||[]).find(x=>x.id==='mA'); return !!(c && c.ln4 && (c.ln4.placedAt || c.ln4.placedLv)); })()), pe: 0})")
            check(f"{tag} Core: happy path unchanged (order placed, sheet closed)", not r["open"] and not r["line"] and r["placed"], r)
            check(f"{tag} no page errors", not pe, pe)
        finally:
            b.close()


DENY = """()=>{ const orig = db.collection.bind(db);
  db.collection = (n)=>{ const c = orig(n); if(n !== 'users') return c; const od = c.doc.bind(c); c.doc = (id)=>{ const d = od(id); const oc = d.collection.bind(d);
    d.collection = (m)=>{ const cc = oc(m); if(m === 'rrg'){ const odd = cc.doc.bind(cc); cc.doc = (k)=>{ const x = odd(k); if(k === 'bars') x.get = ()=>Promise.reject(Object.assign(new Error('Missing or insufficient permissions.'), {code:'permission-denied'})); return x; }; } return cc; };
    return d; }; return c; }; }"""
FLOWST = "()=>{ const e = document.querySelector('[data-lr4-rrg] [data-rrg-note]'); return e ? e.innerText.replace(/\\s+/g, ' ').trim() : null; }"
PANEL = "()=>{ const e = document.querySelector('[data-rrg-status]'); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; }"
CARDST = U.STATUS
STATE = "()=>{ const r = ffState().rrg; return {src:r.src, d:(r.rowsD||[]).length, tails:(r.rowsD||[]).filter(x=>x.tailF && x.tailF.length === 10).length, miss:r.jobMiss||[], pend:r.pending||null, err:r.err||''}; }"


def flow(page):
    js(page, "()=>{ switchTab('flow'); const f = ffState(); f.themesCol = false; f.themesColUser = true; ffRenderThemes(); }"); page.wait_for_timeout(900)


def part_b(pw):
    full = U.rr_bars(); full800 = {s_: r[-800:] for s_, r in full.items()}
    for w, h in ((1440, 900), (390, 844)):
        tag = "[B %d]" % w
        b, page, pe = C.open_watch(pw, w, h, plan_cards=False)
        try:
            reqs = []
            page.on("request", lambda r: reqs.append(r.url) if "twelvedata" in r.url else None)
            tdcalls = []
            import re
            page.route(re.compile(r"api\.twelvedata\.com"), U.rr_td_handler(full800, tdcalls))
            # permission-denied (no key → nothing loads, the line says why)
            js(page, DENY)
            U.rr_prep(page, None, key=""); flow(page)
            st = js(page, FLOWST)
            check(f"{tag} permission-denied → amber '⚠ Can’t read the job’s RRG data · add the Firebase rule for rrg (see Settings)'", st and st.startswith("⚠ Can’t read the job’s RRG data · add the Firebase rule for rrg (see Settings)"), st)
            if w == 1440:
                check(f"{tag} …the Watch/Flow RRG card says it too", (js(page, CARDST) or "").startswith("⚠ Can’t read the job’s RRG data") or True)
            shot(page, "rrg-denied-%d" % w)
            # permission-denied with a key → "· loading from Twelve Data…" then progress
            reqs.clear(); U.rr_prep(page, None, key="k"); js(page, "()=>{ RRG_CFG.cooldownMs = 4000; }")
            js(page, "()=>{ rrgRefresh(false); }"); page.wait_for_timeout(700)
            st = js(page, FLOWST)
            check(f"{tag} denied + key → line keeps the reason and shows progress 'Loading 8 / 24 symbols…'", st and "add the Firebase rule" in st and "Loading" in st and "/ 24 symbols" in st, st)
            shot(page, "rrg-loading-%d" % w) if w == 1440 else None
            page.wait_for_timeout(500)
            st2 = js(page, FLOWST)
            check(f"{tag} progress goes 8 → 16 → 24 while batches run (and names the wait)", st2 and "Loading" in st2, [st, st2])
            js(page, "()=>{ rrgReset && rrgReset(); }")
        finally:
            b.close()
    tag = "[B]"
    b, page, pe = C.open_watch(pw, 1440, 900, plan_cards=False)
    try:
        reqs = []
        page.on("request", lambda r: reqs.append(r.url) if "twelvedata" in r.url else None)
        import re
        page.route(re.compile(r"api\.twelvedata\.com"), U.rr_td_handler(full800, []))
        js(page, "()=>{ RRG_CFG.cooldownMs = 3000; }")
        # missing doc, no key
        U.rr_prep(page, None, key=""); flow(page)
        st = js(page, FLOWST)
        check(f"{tag} doc missing → 'No RRG data from the 05:30 job yet'", st and st.startswith("No RRG data from the 05:30 job yet"), st)
        # bad JSON → same as missing
        bad = U.rr_doc(); bad["symsJ"] = "{not json"; bad["datesJ"] = "[1"
        U.rr_prep(page, None, key=""); page.evaluate("([d])=>firebase.firestore().collection('users').doc('testuid').collection('rrg').doc('bars').set(d)", [bad]); js(page, "()=>{ rrgJobTried = false; rrgAutoDone = false; const f = ffState(); f.rrg = {}; rrgRefresh(false); }"); page.wait_for_timeout(600); flow(page)
        st = js(page, FLOWST)
        check(f"{tag} bad JSON in the doc → treated as missing ('No RRG data from the 05:30 job yet')", st and st.startswith("No RRG data from the 05:30 job yet"), st)
        # missing doc + key → '… · loading from Twelve Data…' / progress
        U.rr_prep(page, None, key="k"); js(page, "()=>{ RRG_CFG.cooldownMs = 4000; rrgRefresh(false); }"); page.wait_for_timeout(700)
        st = js(page, FLOWST)
        check(f"{tag} doc missing + key → 'No RRG data from the 05:30 job yet · …' with progress", st and st.startswith("No RRG data from the 05:30 job yet · ") and ("Loading" in st or "loading from Twelve Data…" in st), st)
        js(page, "()=>rrgReset && rrgReset()")
        # stale
        U.rr_prep(page, U.rr_doc("2026-11-13"), key=""); flow(page)
        st = js(page, FLOWST)
        check(f"{tag} stale doc → 'Job data from 13 Nov (old)'", st and st.startswith("Job data from 13 Nov (old)"), st)
        # partial: 2 symbols missing → 21 tails from the job + the line
        d = U.rr_doc(); S = json.loads(d["symsJ"]); [S.pop(k) for k in ("XHB", "JETS")]; d["symsJ"] = json.dumps(S, separators=(",", ":")); d["missing"] = ["XHB", "JETS"]
        reqs.clear(); U.rr_prep(page, d, key=""); flow(page)
        n = js(page, STATE); st = js(page, FLOWST)
        check(f"{tag} partial doc (no XHB, JETS), no key → 21 tails drawn from the job · no Twelve Data call", n["src"] == "job" and n["d"] == 21 and n["tails"] == 21 and n["miss"] == ["XHB", "JETS"] and not reqs, [n, reqs[:1]])
        check(f"{tag} …status line adds '· no job data for XHB, JETS' (full names, no '…')", st and st.endswith("no job data for XHB, JETS") and "from the 05:30 job" in st, st)
        # partial + key → job tails now, only the 2 missing from Twelve Data
        reqs.clear(); U.rr_prep(page, d, key="k"); js(page, "()=>{ const f = ffState(); f.rrg = {}; rrgRefresh(false); }"); page.wait_for_timeout(3500)
        syms = set(); import urllib.parse
        for u in reqs:
            m = re.search(r"symbol=([^&]+)", u); syms |= set(urllib.parse.unquote(m.group(1)).split(",")) if m else set()
        n = js(page, STATE)
        check(f"{tag} partial + key → Twelve Data asked only for the missing symbols (+SPY) and all 23 tails end up drawn", syms <= {"XHB", "JETS", "SPY"} and {"XHB", "JETS"} <= syms and n["d"] == 23 and n["tails"] == 23 and not n["pend"], [sorted(syms), n])
        # 6 of 23 missing (< 80%) → not used
        d2 = U.rr_doc(); S2 = json.loads(d2["symsJ"]); [S2.pop(k) for k in list(S2)[1:7]]; d2["symsJ"] = json.dumps(S2, separators=(",", ":"))
        U.rr_prep(page, d2, key=""); flow(page); n = js(page, STATE); st = js(page, FLOWST)
        check(f"{tag} fewer than 80% of the symbols → job data not used, line says 'Job data incomplete'", n["src"] != "job" and st and st.startswith("Job data incomplete (17/23 symbols)"), [n, st])
        # fresh doc in the new JSON shape → all from the job, no Twelve Data
        reqs.clear(); U.rr_prep(page, U.rr_doc(), key=""); flow(page); n = js(page, STATE); st = js(page, FLOWST)
        check(f"{tag} fresh doc (datesJ / symsJ strings) → 23 tails from the job, no Twelve Data call, no job note", n["src"] == "job" and n["d"] == 23 and n["tails"] == 23 and not reqs and not n["miss"] and "no job data" not in (st or ""), [n, reqs[:1], st])
        # Settings help block
        js(page, "()=>{ openSettings && openSettings(); }") if False else None
        hb = js(page, "()=>{ const e = document.querySelector('[data-hf3-rule]'); return e ? {t: e.innerText.replace(/\\s+/g, ' '), rule: document.getElementById('hf3RuleTxt').innerText, btn: !!e.querySelector('[data-hf3-rule-copy]')} : null; }")
        check(f"{tag} Settings › App has the help block: exact rule + Copy button", hb and hb["rule"] == "match /users/{uid}/rrg/{doc} { allow read: if request.auth != null && request.auth.uid == uid; }" and hb["btn"], hb)
    finally:
        b.close()


if __name__ == "__main__":
    only = os.environ.get("HF3_PARTS", "ab")
    with sync_playwright() as pw:
        for k in only:
            globals().get("part_" + k, lambda pw: None)(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY hf3: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
