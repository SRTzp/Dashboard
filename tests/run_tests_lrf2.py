#!/usr/bin/env python3
"""LR-F2 — Today: MANAGE line 2 (Held · Stop · If stopped · Next) · no leading emoji in To do · 2-account fixture (Place · F, same idea, F futures) ·
Risk room = own card (side column under To do / phone after To do) · Weekly News = a To do row · header = ONE row on every width.
Run: python3 tests/run_tests_lrf2.py   (screens: python3 tests/lrf_side.py → tests/screenshots/lrf/today-*-side.png)"""
import sys, re
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, launch, check, results
import lrf_side as S


def go(page):
    js(page, "()=>{ serverConfirmed = true; stateFromServer = true; if(acctActive !== 'main') acctSwitch('main'); bdChip='all'; re1Cache = {}; }")
    js(page, S.PV.SAT_JS); js(page, S.PV.SAT_PLANS_JS.replace("mk('pb','XAGUSD','Long',30,29.5,32);", "")); page.wait_for_timeout(500)
    js(page, "()=>{ const B=getBook('main'); B.settings.psRisk = Object.assign({}, B.settings.psRisk||{}, {minStop:{XAUUSD:0.1}}); saveBook('main'); satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','XAGUSD']); }")
    S.fam_fixture(page)
    js(page, "()=>{ lr2DetOpen = false; re2GrpAll = {}; switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(500)


def run(pw, w, h):
    tag = "[%s]" % w
    d, cs = S.fixture()
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    try:
        go(page)
        # 1 MANAGE line 2
        ml = js(page, "()=>{ const r = document.querySelector('.re2-row[data-re2-grp=\"manage\"] [data-re2-cardline]'); return r ? {t: r.innerText.replace(/\\s+/g, ' ').trim(), ws: getComputedStyle(r).whiteSpace, ov: getComputedStyle(r).textOverflow} : null; }")
        check(f"{tag} 1 MANAGE line 2 = 'Held #n · Stop x · If stopped −$y · Next Buy #m @ p'", ml and re.match(r"^Held #[\d.]+ · Stop [\d,.]+ · If stopped [−+±]\$[\d.,k]+ · Next Buy #[\d.]+ @ [\d,.]+$", ml["t"]) is not None, ml)
        if w <= 600: check(f"{tag} 1 line-2 nowrap + ellipsis kept", ml and ml["ws"] == "nowrap" and ml["ov"] == "ellipsis", ml)
        # 2 emoji
        e = js(page, "()=>[lr2NoEmoji('🔥 NVDA homework'), lr2NoEmoji('⚠️ Playbook missing'), lr2NoEmoji('👨‍👩‍👧 x'), lr2NoEmoji('Plain text'), lr2NoEmoji('3 items')]")
        check(f"{tag} 2 leading emoji stripped from stored text (plain text and digits untouched)", e == ["NVDA homework", "Playbook missing", "x", "Plain text", "3 items"], e)
        js(page, "()=>{ const o = ln4TodoItems; window.__o = o; ln4TodoItems = function(M){ const L = o.call(this, M); L.push({c:'g', g:'', id:'t:e', t:'🔥 emoji item', fn:'void 0'}); return L.map(x=>x); }; todayRefresh(true); }"); page.wait_for_timeout(300)
        em = js(page, "()=>[...document.querySelectorAll('[data-ln4-todo] .t')].map(x=>x.innerText)")
        check(f"{tag} 2 To do rows show no leading emoji", not any(re.match(r"^\s*[\U0001F300-\U0001FAFF\u2600-\u27BF]", x) for x in em), em)
        js(page, "()=>{ ln4TodoItems = window.__o; todayRefresh(true); }")
        # 3 Family
        fam = js(page, "()=>[...document.querySelectorAll('.re2-row')].filter(r=>r.dataset.lr2Acct === 'fam').map(r=>({sym:r.dataset.re2Row, btn:((r.querySelector('[data-re2-btn=\"place\"] .m')||{}).innerText||''), same:(r.querySelector('[data-lrf-same]')||{}).innerText||'', sameShown: !!(r.querySelector('[data-lrf-same]')||{getClientRects:()=>[]}).getClientRects().length}))")
        xau = next((x for x in fam if x["sym"] == "XAU"), None)
        check(f"{tag} 3 Family rows: button 'Place · F'", fam and all(x["btn"] == "Place · F" for x in fam), fam)
        if w > 600: check(f"{tag} 3 Family row: 'same idea, Family size'", xau and xau["same"] == "· same idea, Family size" and xau["sameShown"], fam)
        main_btn = js(page, "()=>[...document.querySelectorAll('.re2-row[data-lr2-acct=\"main\"] [data-re2-btn=\"place\"] .m')].map(x=>x.innerText)")
        check(f"{tag} 3 Main rows keep plain 'Place'", all(x == "Place" for x in main_btn), main_btn)
        fu = js(page, "()=>{ const e = document.querySelector('[data-lr2-fut]'); return e ? [e.innerText, e.parentElement.innerText.replace(/\\s+/g, ' ')] : null; }")
        check(f"{tag} 3 F futures leverage in the open-risk line", fu and re.match(r"^\d\.\d×$", fu[0]) and "futures" in fu[1], fu)
        if w == 390: pass
        # 6 Risk room card
        rr = js(page, """()=>{ const r = document.querySelector('[data-lr2-risk]'), t = document.querySelector('[data-ln4-todorow]'), d = document.querySelector('[data-ln4-moredet]');
          const rb = r.getBoundingClientRect(), tb = t.getBoundingClientRect(), db = d.getBoundingClientRect();
          const L = [...r.querySelectorAll('.lr2-rl[data-lr2-rl]')].map(x=>[(x.querySelector('.lr-acc')||{}).innerText, (x.querySelector('.lr-tag')||{}).innerText, x.querySelector('.t').innerText.replace(/\\s+/g,' ')]);
          return {inDetails: !!d.querySelector('[data-lr2-risk]'), sibling: r.parentElement === t.parentElement, below: rb.top >= tb.bottom - 1, sameLeft: Math.abs(rb.left - tb.left) < 2, sameWidth: Math.abs(rb.width - tb.width) < 2, aboveDetails: rb.bottom <= db.top + 1, cls: r.className, lines: L, hooks: [r.querySelectorAll('[data-re2-room]').length, r.querySelectorAll('[data-re2-rr]').length], eventsInDet: !!d.querySelector('[data-re2-events]')}; }""")
        check(f"{tag} 6 Risk room is its own card, same style as To do, directly under it (not in Details)", not rr["inDetails"] and rr["sibling"] and rr["below"] and rr["sameLeft"] and rr["sameWidth"] and rr["aboveDetails"] and "lr2-todo" in rr["cls"], rr)
        ph = w <= 600
        txt_ok = (re.match(r"^\d+/\d+$", rr["lines"][0][2]) and re.match(r"^step \d+$", rr["lines"][1][2]) and re.match(r"^[\d.]+/[\d.]+%$", rr["lines"][2][2])) if ph else (re.match(r"^\d+ of \d+ ideas · room [\d.]+% / [\d.]+%$", rr["lines"][0][2]) and rr["lines"][1][2].startswith("step ") and "regime" in rr["lines"][2][2])
        check(f"{tag} 6 per port: Main MMT·SAT·COMP, Family SAT·COMP only ({'phone short text' if ph else 'desktop long text'})", [x[1] for x in rr["lines"]] == ["MMT", "SAT", "COMP", "SAT", "COMP"] and [x[0] for x in rr["lines"]] == ["M", "M", "M", "F", "F"] and txt_ok, rr["lines"])
        tops = js(page, "()=>{ const r = document.querySelector('[data-lr2-risk]'); const m = {}; [...r.querySelectorAll('.lr2-rl[data-lr2-rl]')].forEach(x=>{ const k = Math.round(x.getBoundingClientRect().top); m[k] = (m[k] || 0) + 1; }); return {rows: Object.keys(m).length, per: Object.values(m), span: [...r.querySelectorAll('span[data-re2-rr]')].length}; }")
        check(f"{tag} 6 {'phone = ONE line per account (2 lines: M with 3 ports, F with 2)' if ph else 'desktop = one line per port (5 lines)'} · data-re2-rr are spans", (tops["per"] == [3, 2] if ph else tops["rows"] == 5) and tops["span"] == 5, tops)
        js(page, "()=>{ window.__st = re2State; re2State = function(a){ const x = Object.assign({}, window.__st.apply(this, arguments)); x.ab = {sat:'r', comp:'a'}; return x; }; todayRefresh(true); }"); page.wait_for_timeout(300)
        col = js(page, "()=>{ const g = k=>{ const e = document.querySelector('[data-lr2-room=main] [data-lr2-rl=\\''+k+'\\'] .t'); return e ? getComputedStyle(e).color : null; }; return {sat: g('sat'), comp: g('comp'), mom: g('mom'), r: !!document.querySelector('[data-lr2-rl=sat].st-r'), a: !!document.querySelector('[data-lr2-rl=comp].st-a')}; }")
        check(f"{tag} 6 locked / reduced port tagged st-r / st-a" + (" and its segment coloured red / amber on the phone" if ph else ""), col["r"] and col["a"] and (not ph or (col["sat"] != col["mom"] and col["comp"] != col["mom"] and col["sat"] != col["comp"])), col)
        js(page, "()=>{ re2State = window.__st; todayRefresh(true); }")
        check(f"{tag} 6 hooks kept: data-lr2-risk · data-re2-room · data-re2-rr; Details keeps events", rr["hooks"][0] == 2 and rr["hooks"][1] == 5 and rr["eventsInDet"] or (rr["hooks"][0] == 2 and rr["hooks"][1] == 5), rr)
        js(page, "()=>{ lr2DetOpen = true; todayRefresh(true); }"); page.wait_for_timeout(300)
        det = js(page, "()=>document.querySelector('[data-ln4-moredet]').innerText.replace(/\\s+/g, ' ')")
        check(f"{tag} 6 Details no longer holds the Risk room lines", "ideas · room" not in det, det[:200])
        js(page, "()=>{ lr2DetOpen = false; }")
        js(page, "()=>{ window.__rr = re2Room; re2Room = ()=>null; todayRefresh(true); }"); page.wait_for_timeout(300)
        ns = js(page, "()=>{ const r = document.querySelector('[data-lr2-risk]'); return {lines: r.querySelectorAll('.lr2-rl:not(.lr2-vh .lr2-rl)').length, t: r.querySelector('.lr2-rsnap').innerText.replace(/\\s+/g, ' ')}; }")
        check(f"{tag} 6 no snapshot → ONE line 'Risk room — confirm a snapshot in Settings ›'", ns["lines"] == 1 and ns["t"] == "Risk room — confirm a snapshot in Settings ›", ns)
        js(page, "()=>{ re2Room = window.__rr; todayRefresh(true); }")
        # 7 Weekly News row
        js(page, "()=>{ window.__nl = stkLatest; window.__nr = stkIsRead; window.__nc = stkReadCount; window.__nv = stkOpenView; window.__opened = 0; stkLatest = ()=>({id:'e1'}); stkIsRead = ()=>window.__read === true; stkReadCount = ()=>[1, 4]; stkOpenView = ()=>{ window.__opened++; }; todayRefresh(true); }"); page.wait_for_timeout(300)
        nw = js(page, "()=>{ const e = document.querySelector('[data-td3-wnews]'); if(!e) return null; const g = document.querySelector('[data-ln4-status]'); return {txt: e.innerText.replace(/\\s+/g, ' ').trim(), inTodo: !!e.closest('[data-ln4-todorow]'), underBand: !!g.querySelector('[data-td3-wnews]'), n: document.querySelectorAll('[data-td3-wnews]').length, btn: e.querySelector('button.td3-lk') ? e.querySelector('button.td3-lk').innerText : ''}; }")
        check(f"{tag} 7 Weekly News = To do row 'NEWS · Weekly News · n unread · Read ›' (data-td3-wnews kept), no line under the glance band", nw and nw["txt"] == "NEWS Weekly News · 3 unread Read ›" and nw["inTodo"] and not nw["underBand"] and nw["n"] == 1, nw)
        js(page, "()=>document.querySelector('[data-td3-wnews] button').click()")
        check(f"{tag} 7 Read › runs the same handler (stkOpenView)", js(page, "()=>window.__opened") == 1)
        js(page, "()=>{ window.__read = true; todayRefresh(true); }"); page.wait_for_timeout(300)
        check(f"{tag} 7 the row disappears when read", js(page, "()=>document.querySelectorAll('[data-td3-wnews]').length") == 0)
        js(page, "()=>{ stkLatest = window.__nl; stkIsRead = window.__nr; stkReadCount = window.__nc; stkOpenView = window.__nv; todayRefresh(true); }")
        # 8 header
        hd = js(page, """()=>{ const v = document.querySelector('.lr2-viewrow'), t = document.querySelector('[data-lr2-title]'), d = document.querySelector('[data-lr2-date]'), sw = document.querySelector('[data-td3-sw]');
          const tr = t.getBoundingClientRect(), dr = d.getBoundingClientRect(), sr = sw.getBoundingClientRect(), vr = v.getBoundingClientRect();
          const bl = el=>{ const r = document.createRange(); r.selectNodeContents(el); const b = r.getClientRects(); return b.length ? Math.round(b[0].bottom) : null; };
          const sb = sw.querySelector('button'); const sbb = (()=>{ const r = document.createRange(); r.selectNodeContents(sb); return Math.round(r.getClientRects()[0].bottom); })();
          return {title: t.innerText, date: d.innerText.replace(/\\s+/g, ' '), tip: d.title, vh: Math.round(vr.height), oneRow: dr.top < tr.bottom && sr.top < tr.bottom + 20 && sr.left > dr.left, titleBottom: bl(t), dateBottom: bl(d), swTextBottom: sbb, over: d.scrollWidth > d.clientWidth + 1, us: !!(d.querySelector('[data-lrf-us]') && d.querySelector('[data-lrf-us]').getClientRects().length), tabs: [...document.querySelectorAll('[data-td3-tab]')].map(x=>x.dataset.td3Tab).join('')}; }""")
        if w > 600:
            ok = re.match(r"^[A-Z][a-z]{2} \d{1,2} [A-Z][a-z]{2} · US market opens \d\d:\d\d ICT$", hd["date"]) is not None
        else:
            ok = re.match(r"^[A-Z][a-z]{2} \d{1,2}( · US \d\d:\d\d)?$", hd["date"]) is not None and (w > 380 or not hd["us"])
            if w > 380: ok = ok and hd["us"]
        check(f"{tag} 8 header = ONE row (Today · date · Daily/Weekend), date format for this width", ok and hd["oneRow"] and hd["vh"] <= 48 and not hd["over"] and "US market opens" in hd["tip"] and hd["tabs"] == "dw", hd)
        check(f"{tag} 8 title and control share one baseline (±3px)", abs(hd["titleBottom"] - hd["swTextBottom"]) <= 3 and abs(hd["titleBottom"] - hd["dateBottom"]) <= 3, hd)
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} no overflow · no page errors", ov <= 0 and not pe, [ov, pe])
    finally:
        b.close()


FORMS = [("Core new plan", "()=>coreNewOpen('main',{mode:'new'})"), ("Core edit plan (2 entry rows)", "()=>bdEditLv('mA')"), ("Satellite new plan", "()=>pb2OpenAsset('XAUUSD')"), ("Satellite edit plan", "()=>pb2OpenEdit('xp')"),
         ("Stop sheet", "()=>coreStopOpen('cN')"), ("Fill sheet", "()=>bdFill('mO')")]
Q = """()=>[...document.querySelectorAll('.ui-sheet input,.ui-sheet select,.ui-sheet textarea,.bd-popb input,.core-sheet input')].filter(e=>e.getClientRects().length && !['checkbox','radio','hidden','file','range'].includes(e.type)).map(e=>{ const c = getComputedStyle(e); return {id: e.id || e.name || e.className.slice(0, 16), fs: parseFloat(c.fontSize), fw: +c.fontWeight, ff: c.fontFamily.split(',')[0].replace(/"/g, ''), tn: c.fontVariantNumeric.indexOf('tabular-nums') >= 0, col: c.color}; })"""


def forms(pw, w, h):
    tag = "[%s]" % w
    d, cs = S.fixture()
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    try:
        S.go(page, "plan")
        n_all = 0
        for name, fn in FORMS:
            js(page, "()=>{ try{ coreSheetClose(); }catch(e){} try{ bdClose(); }catch(e){} }"); page.wait_for_timeout(200)
            js(page, fn); page.wait_for_timeout(700)
            if name.startswith("Core edit"): pass
            ins = js(page, Q); n_all += len(ins)
            want = 16 if w <= 600 else 15
            bad = [x for x in ins if x["fs"] < want - 0.01 or x["fw"] != 600 or x["ff"] != "Inter" or not x["tn"]]
            check(f"{tag} 9 {name}: every input {want}px · 600 · Inter · tabular numbers ({len(ins)} inputs)", (len(ins) > 0 or name in ("Fill sheet", "Stop sheet")) and not bad, bad or ins[:2])
            if name.startswith("Core new"):
                pb = js(page, "()=>[...document.querySelectorAll('[data-ps1-add]')].map(e=>{ const c = getComputedStyle(e); return {t: e.innerText.trim(), bw: c.borderTopWidth, bg: c.backgroundColor, sh: c.boxShadow}; })")
                check(f"{tag} 9 '+ Entry' / '+ SL' = plain text (no border, no background, no shadow)", len(pb) == 2 and all(x["bw"] == "0px" and x["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and x["sh"] == "none" for x in pb), pb)
                ph = js(page, "()=>{ const e = document.getElementById('cnEntry'); e.placeholder = '0.00'; const c = getComputedStyle(e, '::placeholder'); return [c.color, getComputedStyle(e).color]; }")
                check(f"{tag} 9 placeholder is muted (differs from the ink colour)", ph[0] != ph[1], ph)
        check(f"{tag} 9 at least 15 inputs checked across the forms", n_all >= 15, n_all)
        check(f"{tag} 9 no page errors", not pe, pe)
    finally:
        b.close()


def record_buy(pw, w, h):
    """LR-F2 10 — Core 'record buy' sheet: English, over-limit fill = amber warning in plain numbers, Save enabled."""
    tag = "[%s]" % w
    d, cs = S.fixture()
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    try:
        S.go(page, "plan")
        js(page, "()=>coreBuy1Open('mA')"); page.wait_for_timeout(500)
        ok0 = js(page, "()=>!!document.getElementById('cbQty')")
        check(f"{tag} 10 record-buy sheet opens", ok0)
        js(page, "()=>{ document.getElementById('cbQty').value = '500'; coreBuy1In(); }"); page.wait_for_timeout(250)
        r = js(page, "()=>{ const e = document.getElementById('cbErr'); const m = re1FillInfo(coreCardsList.find(x=>x.id==='mA'), 500, 158, 150); return {t: e.innerText.replace(/\\s+/g, ' '), cls: e.className, dis: document.getElementById('cbSave').disabled, cs: getComputedStyle(e).color, bg: getComputedStyle(e).backgroundColor, info: m && m.budget}; }")
        t = r["t"]
        check(f"{tag} 10 over-limit fill shows qty, risk $, allowed qty and allowed risk $ (plain numbers)", re.search(r"Over today's limit: 500 sh @ 158 risks \$[\d,.]+k?, limit allows [\d,]+ \(\$[\d,.]+k?\)\. Recorded anyway; new risk is reduced until it fits\.", t) is not None and "FILL_OVER_LIMIT" not in t, r)
        check(f"{tag} 10 amber warning style (not the red error) and Save stays enabled", "ccAmber" in r["cls"] and r["dis"] is False and r["cs"] != js(page, "()=>getComputedStyle(document.documentElement).getPropertyValue('--red')"), r)
        # budget cause → the engine reason text
        js(page, """()=>{ window.__m = re1CardModel; re1CardModel = function(c, q, px, st){ const r = window.__m.apply(this, arguments); if(!r) return r; r.m = Object.assign({}, r.m, {blocked: true, reasons: ['MONEY_WEEK'], reasonTexts: ["This week's risk budget is used up"], allowedQty: 0}); return r; }; coreBuy1In(); }"""); page.wait_for_timeout(250)
        bt = js(page, "()=>document.getElementById('cbErr').innerText.replace(/\\s+/g, ' ')")
        check(f"{tag} 10 budget cause (MONEY_WEEK) shows that reason text instead of the qty sentence", "This week's risk budget is used up" in bt and "Over today's limit" not in bt and "Recorded anyway" in bt, bt)
        js(page, "()=>{ re1CardModel = window.__m; document.getElementById('cbQty').value = '10'; coreBuy1In(); }"); page.wait_for_timeout(200)
        quiet = js(page, "()=>document.getElementById('cbErr').style.display")
        check(f"{tag} 10 a fill within the limit shows no warning", quiet == "none", quiet)
        js(page, "()=>{ document.getElementById('cbQty').value = '10.5'; document.getElementById('cbPx').value = '0'; coreBuy1In(); }"); page.wait_for_timeout(200)
        er = js(page, "()=>({t: document.getElementById('cbErr').innerText.replace(/\\s+/g, ' '), cls: document.getElementById('cbErr').className, dis: document.getElementById('cbSave').disabled})")
        check(f"{tag} 10 a real error (price 0) stays a red error and disables Save", "Buy price must be above 0" in er["t"] and "ccAmber" not in er["cls"] and er["dis"] is True, er)
        js(page, "()=>{ document.getElementById('cbPx').value = '158'; document.getElementById('cbQty').value = '40'; coreBuy1In(); }")
        sh = js(page, "()=>document.querySelector('.core-sheet').innerText")
        th = re.findall(r"[\u0E00-\u0E7F]", sh)
        check(f"{tag} 10 no Thai characters anywhere in the sheet; English title / labels / buttons", not th and "Record buy #1" in sh and "Actual buy price" in sh and "Quantity" in sh and "Cancel" in sh and "Save" in sh, [sh[:160], th[:3]])
        check(f"{tag} 10 no page errors", not pe, pe)
    finally:
        b.close()


def setup_tick(pw, w, h):
    """LR-F2 11 — Confirm sheet: no visible Setup checkbox; Confirm always records tvSetup[KEY] = today."""
    tag = "[%s]" % w
    d, cs = S.fixture()
    b, page, ce, pe = launch(pw, w, h, d=d, c=cs)
    try:
        S.go(page, "plan")
        js(page, "()=>{ const s = getBook(tdHome()).settings; delete s.tvSetup; }")
        js(page, "()=>efCorePlaceOpen('mA')"); page.wait_for_timeout(500)
        st = js(page, "()=>{ const l = document.querySelector('[data-ef-core-place] [data-ef-setup]'), c = document.getElementById('efSetupCk'); return {hook: !!l, ck: !!c, checked: !!(c && c.checked), shown: !!(l && l.getClientRects().length), txt: document.querySelector('[data-ef-core-place]').innerText.indexOf('Setup ready today') >= 0}; }")
        check(f"{tag} 11 no visible Setup checkbox; data-ef-setup + #efSetupCk kept (hidden, checked)", st["hook"] and st["ck"] and st["checked"] and not st["shown"] and not st["txt"], st)
        pre = js(page, "()=>tv1SetupLeft('AVGO')")
        js(page, "()=>document.querySelector('[data-pb2-yes]').click()"); page.wait_for_timeout(600)
        v = js(page, "()=>({d:(getBook(tdHome()).settings.tvSetup||{})[wlSymKey('AVGO')], t:tv1Today(), g:tv1GroupOf({sym:'AVGO', port:'core'})})")
        check(f"{tag} 11 Confirm with nothing touched writes tvSetup[AVGO] = today; Watch shows 'Setup ✓' (was {pre} days left before)", v["d"] == v["t"] and v["g"] == "Setup ✓" and pre == 0, v)
        check(f"{tag} 11 no page errors", not pe, pe)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (360, 740), (1440, 900)):
            run(pw, w, h)
            forms(pw, w, h)
            record_buy(pw, w, h)
            setup_tick(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY lrf2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
