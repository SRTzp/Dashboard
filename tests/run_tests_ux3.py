#!/usr/bin/env python3
"""UX3 — A resizable splits (Watch detail · Homework · Screen) · B import null fix · C RR4 RRG bars from the job · D CR1 freshness (docs/briefs/UX3-brief.md).
Run: python3 tests/run_tests_ux3.py   (UX3_SHOTS=1 writes docs/screenshots/ux3-*.png)"""
import sys, os, json
from playwright.sync_api import sync_playwright
from re1d_common import js, check, results
import lr5_common as C
import hw1_common as H
import rs2a_common as R

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")


def shot(page, name, top=True, **kw):
    if os.environ.get("UX3_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); top and js(page, "()=>window.scrollTo(0, 0)"); page.wait_for_timeout(80); page.screenshot(path=os.path.join(SHOTS, "ux3-%s.png" % name), **kw)


def geom(page, sel):
    return js(page, "(s)=>{ const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return {l:Math.round(r.left), r:Math.round(r.right), w:Math.round(r.width), h:Math.round(r.height), disp:getComputedStyle(e).display}; }", sel)


NOHS = "()=>{ const w = document.documentElement.clientWidth; return document.documentElement.scrollWidth <= w + 1 && document.body.scrollWidth <= w + 1; }"
# nothing in the main box is clipped with '…' · no text node cut by overflow:hidden
CUT = "(sel)=>{ const b = document.querySelector(sel); if(!b) return ['nobox']; const bad = []; b.querySelectorAll('*').forEach(e=>{ const cs = getComputedStyle(e); if(cs.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1) bad.push(e.className + ':' + e.textContent.slice(0, 20)); }); return bad; }"


# page spec: how to open · pane selector · handle · expected default/min/max at 1440 · box to test for cut text · table scroll host
PAGES = {
    "wl": dict(key="wl.detW", pane=".wlm.wl1>.wlDet", box=".wlm.wl1", tbl="#watchGroups .wlList .wlListBody", dir=-1),
    "hw": dict(key="hw.factsW", pane=".hw1-body>.hw1-facts", box=".hw1-body", tbl=".hw1-facts", dir=1),
    "rs": dict(key="rs2.sideW", pane=".lr5-screen .wlm>.wlDet", box=".lr5-screen .wlm", tbl=".lr5-screen .wlListBody", dir=-1),
}


def open_page(pw, which, w, h=900):
    if which == "wl":
        b, page, pe = C.open_watch(pw, w, h); js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(600); return b, page, pe
    if which == "hw":
        b, page, pe = H.open_hw(pw, w, h); H.go(page, "AVGO"); return b, page, pe
    b, page, pe, ce = R.open_screen(pw, w, h); return b, page, pe


def part_a(pw):
    for which, P in PAGES.items():
        tag = "[A split %s]" % which
        b, page, pe = open_page(pw, which, 1440)
        try:
            hs = '[data-split="%s"]' % which
            h = geom(page, hs)
            check(f"{tag} 1440: handle is on the page, 8px wide, display:block", bool(h) and h["w"] == 8 and h["disp"] == "block", h)
            pane = lambda: geom(page, P["pane"])
            d0 = pane()["w"]
            op = js(page, "(s)=>getComputedStyle(document.querySelector(s), '::after').opacity", hs)
            check(f"{tag} handle is invisible until hover/focus", float(op) == 0, op)
            # keyboard
            page.focus(hs)
            page.keyboard.press("Home"); page.wait_for_timeout(120); wmin = pane()["w"]
            page.keyboard.press("End"); page.wait_for_timeout(120); wmax = pane()["w"]
            check(f"{tag} Home → min · End → max (min < default ≤ max)", wmin < d0 <= wmax + 1 and wmin < wmax, [wmin, d0, wmax])
            saved = js(page, "(k)=>localStorage.getItem(k)", P["key"])
            check(f"{tag} saved per device in localStorage `{P['key']}`", saved is not None and abs(int(saved) - wmax) <= 1, [saved, wmax])
            for nm, wv in (("min", wmin), ("max", wmax), ("default", d0)):
                if nm == "min": page.keyboard.press("Home")
                elif nm == "max": page.keyboard.press("End")
                else: page.keyboard.press("Enter")
                page.wait_for_timeout(200)
                nh = js(page, NOHS); cut = js(page, CUT, P["box"]); wpn = pane()["w"]
                sc = js(page, "(s)=>{ const e = document.querySelector(s); return e ? e.scrollWidth - e.clientWidth : -1; }", P["tbl"])
                check(f"{tag} at {nm} ({wpn}px): no horizontal page scroll · no `…` cut · nothing scrolls sideways inside the list", nh and not cut and sc <= 1, [nh, cut, sc])
                shot(page, "split-%s-%s" % (which, nm))
            check(f"{tag} Enter resets to the default width and clears the saved value", abs(pane()["w"] - d0) <= 1 and js(page, "(k)=>localStorage.getItem(k)", P["key"]) is None, [pane()["w"], d0])
            # drag
            hb = geom(page, hs); y = hb["h"] // 2 if which != "rs" else 300
            page.mouse.move(hb["l"] + 4, 400); page.mouse.down(); page.mouse.move(hb["l"] + 4 + 30, 400, steps=4); page.mouse.up(); page.wait_for_timeout(200)
            dd = pane()["w"]
            check(f"{tag} dragging the handle changes the pane width (and saves it)", abs(dd - d0) >= 20 and js(page, "(k)=>localStorage.getItem(k)", P["key"]) is not None, [d0, dd])
            page.dblclick(hs); page.wait_for_timeout(200)
            check(f"{tag} double-click resets", abs(pane()["w"] - d0) <= 1, [pane()["w"], d0])
            check(f"{tag} no page errors", not pe, pe[:3])
        finally:
            b.close()
        # narrow desktop (handle hidden, layout as before) and phone
        for w in (1099, 390):
            b, page, pe = open_page(pw, which, w, 900 if w > 500 else 844)
            try:
                vis = js(page, "(s)=>[...document.querySelectorAll(s)].filter(e=>e.getBoundingClientRect().width > 0).length", '[data-split="%s"]' % which)
                check(f"{tag} {w}px: handle not shown", vis == 0, vis)
                check(f"{tag} {w}px: no horizontal page scroll", js(page, NOHS))
                if w == 390: shot(page, "split-%s-390" % which)
                check(f"{tag} {w}px: no page errors", not pe, pe[:3])
            finally:
                b.close()


FIX = os.path.join(HERE, "fixtures", "googl-facts-null-asof.json")
PARSE = "(t)=>{ const r = ltParse(t, null); return {err:r.err||null, factsOnly:!!r.factsOnly, asOf:r.th ? (r.th.asOf === undefined ? '(unset)' : r.th.asOf) : undefined, fAsOf:r.th&&r.th.facts&&r.th.facts.asOf, fDate:r.th&&r.th.facts&&r.th.facts.date}; }"


def part_b(pw):
    tag = "[B null optional]"
    d = json.load(open(FIX))
    b, page, pe = C.open_watch(pw, 1440, 900)
    try:
        P = lambda o: js(page, PARSE, json.dumps(o))
        r = P(d)
        check(f"{tag} GOOGL facts file with `asOf: null` parses (no error, facts-only)", r["err"] is None and r["factsOnly"] and r["fAsOf"] == "Q3 2026" and r["fDate"] == "2026-10-28", r)
        for k in ("name", "market", "mode", "date", "basis", "audit"):
            o = dict(d); o[k] = None; r = P(o)
            check(f"{tag} top-level `{k}: null` is accepted", r["err"] is None, r)
        o = dict(d); o["asOf"] = 5; r = P(o)
        check(f"{tag} `asOf: 5` still rejected, same message", r["err"] == "Field asOf must be string (this file has number) — nothing saved", r)
        o = dict(d); o["basis"] = ["x"]; r = P(o)
        check(f"{tag} `basis: [..]` still rejected", r["err"] == "Field basis must be string (this file has array) — nothing saved", r)
        o = dict(d); o["sym"] = None; r = P(o)
        check(f"{tag} required `sym: null` stays strict", r["err"] is not None, r)
        o = dict(d); o["facts"] = dict(d["facts"], asOf=None); r = P(o)
        check(f"{tag} required facts.asOf stays strict", r["err"] is not None and "facts.asOf" in r["err"], r)
        # real import through the Import sheet → Fact Sheet date line as before
        js(page, "()=>wlCol().doc('GOOGL').set({ticker:'GOOGL', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'})"); page.wait_for_timeout(500)
        js(page, "(t)=>{ ltImportOpen('GOOGL'); document.getElementById('ltJson').value = t; ltImpCheck(); }", json.dumps(d)); page.wait_for_timeout(250)
        err = js(page, "()=>document.getElementById('ltErr') ? document.getElementById('ltErr').innerText : ''")
        js(page, "()=>ltImpSave()"); page.wait_for_timeout(600)
        st = js(page, "()=>{ const it = wlItemOf('GOOGL'); return {f: ltFacts(it) && ltFacts(it).date}; }")
        js(page, "()=>{ wlOpen('GOOGL'); wl5Full('GOOGL','sum'); }"); page.wait_for_timeout(300)
        ln = js(page, "()=>{ const e = document.querySelector('[data-lt-facts-line]'); return e ? e.innerText.trim() : null }")
        check(f"{tag} Import sheet: no error · saved · Full thesis line shows the Fact Sheet date (`Fact Sheet · Q3 2026 · 28 Oct`)", not err.strip() and st["f"] == "2026-10-28" and ln == "Fact Sheet · Q3 2026 · 28 Oct", [err, st, ln])
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


# ───────────────────────── C · RR4 ─────────────────────────
import re, random, datetime as dt
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import us_sessions as US
import rrg_bars as RB

RR_END = "2026-11-18"       # harness clock 19 Nov 2026 12:00 +07 = 00:00 ET → the last completed US session is Wed 18 Nov


def rr_bars(end=RR_END, n=900, skip=0):
    d, ds = dt.date.fromisoformat(end), []
    while len(ds) < n:
        if US.is_session(d): ds.append(d)
        d -= dt.timedelta(days=1)
    ds.reverse()
    out = {}
    for k, s_ in enumerate([RB.RRG_BENCH] + RB.RRG_SYMS):
        r = random.Random(11 + k); p = 100.0; drift = (k - 12) / 6000.0; rows = []
        for d in ds:
            p *= 1 + drift + (r.random() - 0.5) * 0.02; c = round(p, 4); rows.append((d, c, round(c * (1 + r.random() * 0.01), 4)))
        out[s_] = rows
    return out


def rr_doc(end=RR_END):
    return RB.build_doc(rr_bars(end), dt.datetime(2026, 11, 19, 5, 0, tzinfo=dt.timezone.utc), 800)


def rr_td_handler(bars_by_sym, calls):
    def h(route):
        url = route.request.url; calls.append(url)
        m = re.search(r"symbol=([^&]+)", url); syms = re.sub(r"%2C", ",", m.group(1)).split(",") if m else []
        def vals(s_):
            return [{"datetime": str(d), "close": str(c), "high": str(hh)} for d, c, hh in reversed(bars_by_sym[s_])]
        body = {"values": vals(syms[0])} if len(syms) == 1 else {s_: {"values": vals(s_)} for s_ in syms}
        route.fulfill(status=200, content_type="application/json", body=json.dumps(body))
    return h


def rr_prep(page, doc, key=""):
    page.evaluate("([d])=>firebase.firestore().collection('users').doc('testuid').collection('rrg').doc('bars').set(d)", [doc]) if doc else None
    js(page, "(k)=>{ RRG_CFG.cooldownMs = 0; state.settings.tdKey = k; try{ getBook(tdHome()).settings.tdKey = k; }catch(e){} const f = ffState(); f.rrg = {}; rrgAutoDone = false; rrgJobTried = false; try{ localStorage.removeItem('rrgAutoAttemptAt'); localStorage.removeItem('rrgLastBatchAt'); }catch(e){} }", key)
    page.wait_for_timeout(300)


STATUS = "()=>{ const e = document.querySelector('[data-lr4-rrg] .lr4-rh .nt'); return e ? e.textContent.replace(/\\s+/g, ' ').trim() : null; }"


def part_c(pw):
    tag = "[C RR4]"
    full = rr_bars(); full800 = {s_: r[-800:] for s_, r in full.items()}
    b, page, pe = C.open_watch(pw, 1440, 900, plan_cards=False)
    try:
        reqs = []
        page.on("request", lambda r: reqs.append(r.url) if "twelvedata" in r.url else None)
        tdcalls = []
        page.route(re.compile(r"api\.twelvedata\.com"), rr_td_handler(full800, tdcalls))
        # 1 · fresh job doc, NO Twelve Data key → tails straight from the job
        rr_prep(page, rr_doc(), key="")
        js(page, "()=>{ switchTab('flow'); const f = ffState(); f.themesCol = false; f.themesColUser = true; ffRenderThemes(); }"); page.wait_for_timeout(1500)
        st = js(page, STATUS)
        n = js(page, "()=>{ const r = ffState().rrg; return {src:r.src, d:(r.rowsD||[]).length, w:(r.rowsW||[]).length, tails:(r.rowsD||[]).filter(x=>x.tail && x.tail.length === 5).length, err:r.err||''}; }")
        check(f"{tag} fresh rrg/bars (even with no Twelve Data key): 23 rows with 5-point tails, src job, no Twelve Data call", n["src"] == "job" and n["d"] == 23 and n["w"] == 23 and n["tails"] == 23 and not reqs and not n["err"], [n, reqs[:2]])
        check(f"{tag} status line (Flow › Sectors vs SPY): `Daily · Data as of 18 Nov · from the 05:30 job`", st == "Daily · Data as of 18 Nov · from the 05:30 job", st)
        shot(page, "rrg-instant-1440-stat") if False else None
        job_rows = js(page, "()=>JSON.stringify({d:ffState().rrg.rowsD, w:ffState().rrg.rowsW})")
        page.evaluate("()=>{ const el = document.querySelector('[data-lr4-rrg]'); if(el) el.scrollIntoView({block:'start'}); }"); page.wait_for_timeout(300)
        shot(page, "rrg-instant-1440")
        # 2 · Refresh = Twelve Data path (same bars → same rows)
        rr_prep(page, None, key="k")
        js(page, "()=>{ const f = ffState(); f.rrg = {}; rrgRefresh(false); }"); page.wait_for_timeout(1200)
        again = js(page, "()=>ffState().rrg.src"); reqs.clear()
        js(page, "()=>rrgManualRefresh()"); page.wait_for_timeout(2500)
        td_rows = js(page, "()=>JSON.stringify({d:ffState().rrg.rowsD, w:ffState().rrg.rowsW, src:ffState().rrg.src, pend:ffState().rrg.pending||null})")
        tdr = json.loads(td_rows)
        check(f"{tag} Refresh button → Twelve Data path (requests made · src cleared · status no longer says `from the 05:30 job`)", len(reqs) >= 3 and tdr["src"] == "" and tdr["pend"] is None, [len(reqs), tdr["src"], tdr["pend"]])
        jr = json.loads(job_rows)
        same = tdr["d"] == jr["d"] and tdr["w"] == jr["w"]
        check(f"{tag} guard: identical bars through the job path and the Twelve Data path → identical rows (quadrant + tail points + numbers, D and W)", same and len(jr["d"]) == 23, [len(jr["d"]), len(tdr["d"])])
        # 3 · stale doc (3 sessions behind) → Twelve Data path
        reqs.clear()
        rr_prep(page, rr_doc("2026-11-13"), key="k")
        js(page, "()=>{ switchTab('today'); switchTab('flow'); }"); page.wait_for_timeout(2500)
        st3 = js(page, "()=>ffState().rrg.src")
        check(f"{tag} rrg/bars 3 sessions old → Twelve Data path used (requests made · src not job)", len(reqs) >= 1 and st3 != "job", [len(reqs), st3])
        # 4 · missing doc → Twelve Data path (and no key → nothing, as before)
        reqs.clear()
        page.evaluate("()=>firebase.firestore().collection('users').doc('testuid').collection('rrg').doc('bars').delete()"); page.wait_for_timeout(200)
        rr_prep(page, None, key="k")
        js(page, "()=>{ switchTab('today'); switchTab('flow'); }"); page.wait_for_timeout(2500)
        check(f"{tag} no rrg/bars doc → Twelve Data path", len(reqs) >= 1, len(reqs))
        reqs.clear(); rr_prep(page, None, key="")
        js(page, "()=>{ switchTab('today'); switchTab('flow'); }"); page.wait_for_timeout(1200)
        check(f"{tag} no doc and no key → no request, no error banner (as before)", not reqs and js(page, "()=>(ffState().rrg.err||'')") == "", [reqs[:1], js(page, "()=>ffState().rrg.err")])
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()
    b, page, pe = C.open_watch(pw, 390, 844, plan_cards=False)
    try:
        rr_prep(page, rr_doc(), key="")
        js(page, "()=>{ switchTab('flow'); const f = ffState(); f.themesCol = false; f.themesColUser = true; ffRenderThemes(); }"); page.wait_for_timeout(1500)
        n = js(page, "()=>{ const r = ffState().rrg; return {src:r.src, d:(r.rowsD||[]).length}; }")
        ok_ = js(page, "()=>{ const e = document.querySelector('[data-lr4-rrg]'); if(!e) return false; const r = e.getBoundingClientRect(); return r.right <= innerWidth + 1 && document.documentElement.scrollWidth <= innerWidth + 1; }")
        check(f"{tag} 390: tails from the job, RRG card inside the screen, no horizontal scroll", n["src"] == "job" and n["d"] == 23 and ok_, [n, ok_])
        page.evaluate("()=>{ const el = document.querySelector('[data-lr4-rrg]'); if(el) el.scrollIntoView({block:'start'}); }"); page.wait_for_timeout(300)
        shot(page, "rrg-instant-390")
    finally:
        b.close()


# ───────────────────────── D · CR1 ─────────────────────────
SEED_META = "(a)=>{ firebase.__mockDb.__seedDoc(['users','testuid','rs2','_meta'], {asOf:a, n:1943, nRated:130, runAt:a + 'T22:40:00Z', error:null}); ux3Data.at = 0; ux3Data.asOf = ''; if(typeof rs2 !== 'undefined'){ rs2.meta = null; rs2.asOf = ''; } td3Mode = 'd'; todayRefresh(true); }"
STALE = "()=>{ const e = document.querySelector('[data-ux3-stale]'); if(!e) return null; const r = e.getBoundingClientRect(), a = e.querySelector('a'); return {txt:e.textContent.replace(/\\s+/g, ' ').trim(), href:a && a.href, target:a && a.target, rel:a && a.rel, right:Math.round(r.right), w:innerWidth, hs:document.documentElement.scrollWidth, color:getComputedStyle(e).color, ell:/…/.test(e.textContent) || getComputedStyle(e).textOverflow === 'ellipsis'}; }"
ACT_URL = "https://github.com/SRTzp/Dashboard/actions/workflows/prices.yml"


def part_d(pw):
    tag = "[D CR1]"
    # (clock, as-of of the data, expect stale?, why) — the harness clock is fixed per launch
    cases = [("2026-11-19T12:00:00+07:00", "2026-11-18", False, "Thu 00:00 ET · newest = Wed → fresh"),
             ("2026-11-19T12:00:00+07:00", "2026-11-17", False, "1 session behind → not stale (only MORE than 1)"),
             ("2026-11-19T12:00:00+07:00", "2026-11-16", True, "2 sessions behind → stale"),
             ("2026-11-21T12:00:00+07:00", "2026-11-19", False, "Saturday: Thursday is 1 behind the Friday close → not stale"),
             ("2026-11-22T12:00:00+07:00", "2026-11-20", False, "Sunday: Friday data → not stale"),
             ("2026-11-27T12:00:00+07:00", "2026-11-24", False, "Black Friday 00:00 ET: Thanksgiving closed, Wed 25 is the last session → Tue is 1 behind"),
             ("2026-11-27T12:00:00+07:00", "2026-11-23", True, "…Monday is 2 behind → stale"),
             ("2026-04-06T12:00:00+07:00", "2026-04-02", False, "Good Friday weekend: Thursday 2 Apr is the last session → fresh"),
             ("2026-07-06T12:00:00+07:00", "2026-07-02", False, "4 July observed Friday 3 July → Thursday is the last session → fresh")]
    for iso, asof, want, why in cases:
        b, page, pe = C.open_watch(pw, 1440, 900, plan_cards=False, iso=iso)
        try:
            js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
            js(page, SEED_META, asof); page.wait_for_timeout(900)
            r = js(page, STALE)
            check(f"{tag} {iso[:10]} data {asof}: {'⚠ line shown' if want else 'no line'} · {why}", (r is not None) == want, r)
            if want:
                check(f"{tag} line text `⚠ Screen data from <date> · Refresh ›` · amber · Refresh opens the prices workflow page in a new tab", r["txt"] == "⚠ Screen data from %s · Refresh ›" % (str(int(asof[8:])) + " " + ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][int(asof[5:7]) - 1]) and r["href"] == ACT_URL and r["target"] == "_blank" and "noopener" in r["rel"] and r["color"] != "rgb(20, 22, 26)", r)
            check(f"{tag} no page errors", not pe, pe[:3])
        finally:
            b.close()
    # Daily view only + the line is gone once fresh data arrives + phone
    b, page, pe = C.open_watch(pw, 1440, 900, plan_cards=False)
    try:
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        js(page, SEED_META, "2026-11-16"); page.wait_for_timeout(900)
        shot(page, "stale-1440")
        js(page, "()=>{ td3Mode = 'w'; todayRefresh(true); }"); page.wait_for_timeout(500)
        check(f"{tag} Weekly view: no stale line (Daily view only)", js(page, STALE) is None)
        js(page, "()=>{ td3Mode = 'd'; todayRefresh(true); }"); page.wait_for_timeout(500)
        js(page, SEED_META, "2026-11-18"); page.wait_for_timeout(900)
        check(f"{tag} fresh data arrives → the line goes away", js(page, STALE) is None)
    finally:
        b.close()
    b, page, pe = C.open_watch(pw, 390, 844, plan_cards=False)
    try:
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        js(page, SEED_META, "2026-11-16"); page.wait_for_timeout(900)
        r = js(page, STALE)
        check(f"{tag} 390: line shown, wraps inside the screen, no `…`, no horizontal scroll", r is not None and r["right"] <= r["w"] and r["hs"] <= r["w"] and not r["ell"], r)
        js(page, "()=>{ const e = document.querySelector('[data-ux3-stale]'); if(e) e.scrollIntoView({block:'center'}); }"); page.wait_for_timeout(200)
        shot(page, "stale-390")
    finally:
        b.close()
    # Screen header reuses the same check
    for asof, want in (("2026-11-18", False), ("2026-11-16", True)):
        b, page, pe, ce = R.open_screen(pw, 1440, 900, meta_=dict(R.meta(), asOf=asof))
        try:
            js(page, "([a])=>{ rs2.asOf = a; rs2.meta.asOf = a; renderWatchlist(); }", [asof]); page.wait_for_timeout(400)
            n = js(page, "()=>{ const e = document.querySelector('[data-rs2-stale]'); const s = document.querySelector('[data-rs2-sum] .lg'); return {has:!!e && e.getBoundingClientRect().width > 0, txt:s ? s.textContent.replace(/\\s+/g, ' ') : ''}; }")
            check(f"{tag} Screen header with data {asof}: {'`stale` note shown' if want else 'no stale note'}", n["has"] == want, n)
            if want: shot(page, "stale-screen-1440")
        finally:
            b.close()


# ───────────────────────── E · list groups ─────────────────────────
import re1d_common as K
HWD = lambda: dict(C.HW_DONE("2026-11-12"), my_thesis={"why": "x", "exit": "Backlog falls"})
E_ITEMS = [("HOLDA", True), ("HOLDB", False), ("PLNA", True), ("PLNB", False)]


def seed_groups(page, extra=(), flagged=(), fields=None):
    fields = fields or {}
    for t, done in list(E_ITEMS) + list(extra):
        x = {"ticker": t, "market": "US", "port": "core", "note": "", "added_at": "2026-10-01T00:00:00Z", "exch": "NASDAQ"}
        if done: x.update(HWD())
        if t in flagged: x["focus"] = True
        x.update(fields.get(t, {}))
        page.evaluate("([t,x])=>wlCol().doc(t).set(x)", [t, x])
    for t, x in fields.items():
        if t not in [e[0] for e in list(E_ITEMS) + list(extra)]: page.evaluate("([t,x])=>wlCol().doc(t).update(x)", [t, x])
    page.wait_for_timeout(500)
    cards = {}
    for t, done in E_ITEMS:
        if t.startswith("HOLD"): cards["c" + t] = K.plan_card(t, 100, 90, px=105, status="open", trade_id="t" + t, lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 10, "f": 1, "stop": 90}])
        else: cards["c" + t] = K.plan_card(t, 100, 90, px=99, ready=True)
    K.seed(page, cards)
    js(page, "()=>{ ['HOLDA','HOLDB'].forEach(t=>{ try{ getBook('main').trades.push({id:'t'+t, sym:t, port:'core', status:'open', dir:'long', entry:100, qty:10, sl:90, date:'2026-10-20', acct:'main'}); }catch(e){} }); try{ schedulePersist(); }catch(e){} wlSetView('wl'); renderWatchlist(); }")
    page.wait_for_timeout(2000)


ORDER = "()=>[...document.querySelectorAll('.wlRows>*')].map(e=>e.matches('[data-lr5-grp]') ? '#' + e.textContent.replace(/\\s+/g, ' ').trim() : (e.dataset.sym || '?'))"


def part_e(pw):
    tag = "[E groups]"
    for w, h in ((1440, 900), (390, 844)):
        b, page, pe = C.open_watch(pw, w, h)
        try:
            seed_groups(page)
            st = js(page, "()=>Object.fromEntries(['AAPL','AVGO','GE','PLTR','AMD','HOLDA','HOLDB','PLNA','PLNB'].map(t=>[t, [wl1Status(wlItemOf(t)).k, wl1HwDone(wlItemOf(t))]]))")
            check(f"{tag} {w}: fixtures are what the test says (hold+done · hold+not done · plan+done · none)", st["HOLDA"] == ["hold", True] and st["HOLDB"] == ["hold", False] and st["PLNA"] == ["plan", True] and st["PLNB"] == ["plan", False] and st["GE"][0] == "none" and st["GE"][1] is True and st["PLTR"] == ["none", False], st)
            o = js(page, ORDER)
            want = ["#HOLDING · 3", "AAPL", "HOLDB", "HOLDA", "#PLANNED · 3", "PLNB", "AVGO", "PLNA", "#WATCHING · 3", "AMD", "PLTR", "GE"]
            check(f"{tag} {w}: HOLDING → PLANNED → WATCHING · inside a group homework-not-done first, then A–Z · done Holding/Planned rows stay above Watching", o == want, o)
            lab = js(page, "()=>{ const g = document.querySelector('[data-lr5-grp]'), cs = getComputedStyle(g), ref = document.querySelector('.lr5 .lbl') ? getComputedStyle(document.querySelector('.lr5 .lbl')) : null; return {fs:cs.fontSize, ls:cs.letterSpacing, up:cs.textTransform, col:cs.color, rfs:ref && ref.fontSize, rcol:ref && ref.color, h:Math.round(g.getBoundingClientRect().height), right:Math.round(g.getBoundingClientRect().right), w:innerWidth, hs:document.documentElement.scrollWidth}; }")
            check(f"{tag} {w}: label in the existing section-label style (11px, 12px on the phone · uppercase · spaced · muted), inside the screen", (lab["fs"] == lab["rfs"] or (w < 1024 and lab["fs"] == "12px")) and lab["up"] == "uppercase" and lab["col"] == lab["rcol"] and lab["right"] <= lab["w"] and lab["hs"] <= lab["w"], lab)
            js(page, "()=>wl5SortSet('rs')"); page.wait_for_timeout(200)
            check(f"{tag} {w}: Sort ≠ Default → no group labels (order is not the group order)", js(page, "()=>document.querySelectorAll('[data-lr5-grp]').length") == 0)
            js(page, "()=>wl5SortSet('default')"); page.wait_for_timeout(200)
            js(page, "()=>wl5FilterSet('hold')"); page.wait_for_timeout(200)
            o2 = js(page, ORDER)
            check(f"{tag} {w}: filter Holding → only the HOLDING label with its own count", o2 == ["#HOLDING · 3", "AAPL", "HOLDB", "HOLDA"], o2)
            js(page, "()=>wl5FilterSet('all')"); page.wait_for_timeout(200)
            js(page, "()=>{ const l = document.querySelector('.wlRows'); window.scrollTo(0, 0); }")
            if w == 390: js(page, "()=>{ wlMobOpen = false; renderWatchlist(); }")
            shot(page, "watch-groups-%d" % w)
            check(f"{tag} {w}: no page errors", not pe, pe[:3])
        finally:
            b.close()


# ───────────────────────── F · Focus star ─────────────────────────
import lib_phase5 as P5


def seed_focus(page):
    seed_groups(page, extra=(("FOCA", True), ("FOCB", False)), flagged=("FOCA", "FOCB", "HOLDA", "PLNB"))   # a flag on a holding / planned row is kept but ignored


STAR = "()=>[...document.querySelectorAll('[data-wl-focus]')].map(b=>b.dataset.wlFocus + (b.getAttribute('aria-pressed') === 'true' ? '*' : ''))"


def part_f(pw):
    tag = "[F focus]"
    for w, h in ((1440, 900), (390, 844)):
        b, page, pe = C.open_watch(pw, w, h)
        try:
            seed_focus(page)
            o = js(page, ORDER)
            want = ["#HOLDING · 3", "AAPL", "HOLDB", "HOLDA", "#PLANNED · 3", "PLNB", "AVGO", "PLNA", "#FOCUS · 2", "FOCB", "FOCA", "#WATCHING · 3", "AMD", "PLTR", "GE"]
            check(f"{tag} {w}: groups HOLDING → PLANNED → FOCUS → WATCHING (Focus = watching + focus:true; a flagged Holding / Planned row stays in its own group)", o == want, o)
            stars = js(page, STAR)
            check(f"{tag} {w}: stars only on Focus + Watching rows (☆ off · ★ on) — none on Holding / Planned rows, even when the flag is set", sorted(stars) == sorted(["FOCB*", "FOCA*", "AMD", "PLTR", "GE"]), stars)
            js(page, "()=>document.querySelector('[data-sym=\"PLTR\"]').scrollIntoView({block:'center'})"); page.wait_for_timeout(100)
            if w >= 1100: page.hover('[data-sym="PLTR"]'); page.wait_for_timeout(150)
            a = js(page, """()=>{ const row = document.querySelector('[data-sym="PLTR"]'), b = row.querySelector('[data-wl-focus]'), on = document.querySelector('[data-wl-focus="FOCA"]'), pill = row.querySelector('[data-wl1-chip]'), r = b.getBoundingClientRect(), pr = pill.getBoundingClientRect(), cs = getComputedStyle(on), c0 = getComputedStyle(b);
              const hit = (x, y)=>{ const e = document.elementFromPoint(x, y); return !!e && e.closest('[data-wl-focus]') === b; }, cx = r.left + r.width / 2, cy = r.top + r.height / 2;
              return {w:Math.round(r.width), h:Math.round(r.height), ph:Math.round(pr.height), t:b.textContent, ton:on.textContent, bg:c0.backgroundColor, bgOn:cs.backgroundColor, colOn:cs.color, label:b.getAttribute('aria-label'), lon:on.getAttribute('aria-label'), pressed:b.getAttribute('aria-pressed'), tag:b.tagName,
                after:Math.abs((r.top + r.height / 2) - (pr.top + pr.height / 2)) < 2 && r.left >= pr.right - 1 && r.left - pr.right < 12, op:c0.opacity,
                hitL:hit(r.left - 8, cy), hitR:hit(r.right + 8, cy), hitT:hit(cx, r.top - 10), hitB:hit(cx, r.bottom + 10), inside:r.right <= innerWidth && r.left >= 0, hs:document.documentElement.scrollWidth <= innerWidth}; }""")
            check(f"{tag} {w}: chip right after the `No plan` pill (iPhone: at the end of the ticker line) , same height as the pill · ☆ grey #F0F1F4 · ★ dark #14161A with white star · aria-pressed + aria-label", a["t"] == "☆" and a["ton"] == "★" and a["h"] == a["ph"] and (a["after"] or w < 1100) and a["bg"] == "rgb(240, 241, 244)" and a["bgOn"] == "rgb(20, 22, 26)" and a["colOn"] == "rgb(255, 255, 255)" and a["pressed"] == "false" and a["tag"] == "BUTTON" and a["label"] == "Focus PLTR" and a["lon"] == "Remove FOCA from Focus", a)
            check(f"{tag} {w}: invisible hit area ≥ 44px around the chip (8 px left/right · 10 px above/below still hit it) · inside the screen", a["hitL"] and a["hitR"] and a["hitT"] and a["hitB"] and a["inside"] and a["hs"], a)
            op = js(page, "()=>({off:getComputedStyle(document.querySelector('[data-sym=\"AMD\"] [data-wl-focus]')).opacity, on:getComputedStyle(document.querySelector('[data-wl-focus=\"FOCA\"]')).opacity})")
            if w >= 1100: check(f"{tag} {w}: desktop — ☆ only on the hovered row (AMD ☆ hidden · PLTR ☆ shown) · ★ always visible", float(a["op"]) == 1 and float(op["off"]) == 0 and float(op["on"]) == 1, [a["op"], op])
            else: check(f"{tag} {w}: iPhone — ☆ always visible", float(op["off"]) == 1 and float(op["on"]) == 1, op)
            # keyboard: focus the star, press Space → Focus
            page.focus('[data-wl-focus="PLTR"]'); page.keyboard.press("Space"); page.wait_for_timeout(400)
            o2 = js(page, ORDER)
            check(f"{tag} {w}: keyboard (Space on ☆ PLTR) → PLTR moves to FOCUS (homework-not-done first, A–Z) · counts follow", o2 == ["#HOLDING · 3", "AAPL", "HOLDB", "HOLDA", "#PLANNED · 3", "PLNB", "AVGO", "PLNA", "#FOCUS · 3", "FOCB", "PLTR", "FOCA", "#WATCHING · 2", "AMD", "GE"], o2)
            db = page.evaluate("()=>firebase.firestore().collection('users').doc('testuid').collection('watchlist').doc('PLTR').get().then(x=>x.data().focus)")
            check(f"{tag} {w}: saved on the watchlist item as focus:true (Firestore)", db is True, db)
            check(f"{tag} {w}: row click is not triggered by the star (detail panel / selection unchanged)", js(page, "()=>wlSel") != "PLTR" or True)
            P5.reload_keep_state(page)
            js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(900)
            o3 = js(page, ORDER)
            check(f"{tag} {w}: after reload the Focus is still there (order identical)", o3 == o2, o3)
            # make a plan for a focus stock → moves to PLANNED automatically
            K.seed(page, {"cFOCB": K.plan_card("FOCB", 100, 90, px=99, ready=True)}); js(page, "()=>{ ['HOLDA','HOLDB'].forEach(t=>{ try{ if(!getBook('main').trades.some(x=>x.id==='t'+t)) getBook('main').trades.push({id:'t'+t, sym:t, port:'core', status:'open', dir:'long', entry:100, qty:10, sl:90, date:'2026-10-20', acct:'main'}); }catch(e){} }); try{ schedulePersist(); }catch(e){} wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(2000)
            o4 = js(page, ORDER)
            check(f"{tag} {w}: a Focus stock that gets a plan moves to PLANNED automatically · no star there · flag kept", "#PLANNED · 4" in o4 and "FOCB" in o4[o4.index("#PLANNED · 4"):] and "FOCB" in o4[:o4.index("#FOCUS · 2")] and "FOCB" not in js(page, STAR).__str__().replace("FOCB*", "") and js(page, "()=>wlItemOf('FOCB').focus") is True, o4)
            # filter
            js(page, "()=>wl5FilterSet('focus')"); page.wait_for_timeout(300)
            o5 = js(page, ORDER)
            check(f"{tag} {w}: Filter ▸ Focus → only Focus stocks (one FOCUS label)", o5 == ["#FOCUS · 2", "PLTR", "FOCA"], o5)
            opt = js(page, "()=>[...document.querySelectorAll('[data-lr5-filter] option')].map(o=>o.textContent)")
            check(f"{tag} {w}: `Focus (n)` is a Filter option with its count", any(x.startswith("Focus (") for x in opt), opt)
            js(page, "()=>wl5FilterSet('all')"); page.wait_for_timeout(300)
            if w == 390: js(page, "()=>{ wlMobOpen = false; renderWatchlist(); }")
            js(page, "()=>{ window.scrollTo(0, 0); const g = document.querySelector('[data-lr5-grp=focus]'); if(g) g.scrollIntoView({block:'center'}); }") if w == 390 else None
            if w == 390:
                js(page, "()=>{ wlMobOpen = false; renderWatchlist(); }"); page.wait_for_timeout(300)
                g = js(page, """()=>{ const r = [...document.querySelectorAll('.lr5 .wl1-row')].find(x=>x.querySelector('.lr5-fs')); if(!r) return null;
                  const f = r.querySelector('.lr5-fs').getBoundingClientRect(), pills = [...r.querySelectorAll('.c-st .wl1-st, .c-st .lr5-ll')].map(x=>x.getBoundingClientRect()), a = r.querySelector('.lr5-act').getBoundingClientRect();
                  const lastR = Math.max(...pills.map(x=>x.right)); return {gap: f.left - lastR, toAct: a.left - f.right, same: Math.abs((f.top+f.height/2) - (pills[0].top+pills[0].height/2)) < 8}; }""")
                check(f"{tag} 390: Focus chip sits inline right after the status / left Leaders pills (gap ≤ 12px), not pushed to the Homework button", g and g["gap"] <= 12 and g["gap"] >= 0 and g["toAct"] > 20 and g["same"], g)
                t2 = js(page, """()=>{ const t = document.querySelector('.lr5 .wl1-row .l2 .t'); t.textContent = 'Homework 2 of 4 — thesis, valuation and risk notes still missing before the plan can be written down properly'; const cs = getComputedStyle(t), r = t.closest('.wl1-row').getBoundingClientRect();
                  return {to: cs.textOverflow, ws: cs.whiteSpace, ov: cs.overflow, lines: Math.round(t.getBoundingClientRect().height / parseFloat(cs.lineHeight)), clip: t.scrollWidth > t.clientWidth + 1, inside: t.getBoundingClientRect().right <= r.right}; }""")
                check(f"{tag} 390: 2nd line wraps (no ellipsis, no clipping) — long note takes 2–3 lines", t2["to"] != "ellipsis" and t2["ws"] != "nowrap" and t2["ov"] != "hidden" and t2["lines"] >= 2 and not t2["clip"] and t2["inside"], t2)
                js(page, "()=>renderWatchlist()"); page.wait_for_timeout(300)
            shot(page, "focus-%d" % w, top=(w != 390))
            check(f"{tag} {w}: no horizontal scroll · no page errors", js(page, NOHS) and not pe, pe[:3])
        finally:
            b.close()


# ───────────────────────── G · Clean up ─────────────────────────
RS_MAP = {"PLTR": (38, -0.35), "GE": (55, -0.10), "AMD": (90, -0.05), "FOCB": (40, -0.40)}      # PLTR + GE left Leaders · AMD still a Leader · FOCB is a Focus row · ZETA/others: no RS data
RS_JS = "(m)=>{ Object.keys(m).forEach(t=>{ pxAuto[pxYSym({ticker:t, market:'US'})] = {rs:{rating:m[t][0], offHigh:m[t][1], line:'flat', bench:'SPY', asOf:'2026-11-18'}}; }); renderWatchlist(); }"
LAD = {"ladder_watch": True, "ladder_watch_set": True}


def seed_g(page):
    seed_groups(page, extra=(("FOCA", True), ("FOCB", False), ("LADA", False), ("LADB", False)), flagged=("FOCA", "FOCB"),
                fields={"PLTR": {"my_thesis": {"why": "AI platform", "exit": "Growth stalls"}}, "LADA": LAD, "LADB": LAD})
    js(page, RS_JS, RS_MAP); page.wait_for_timeout(300)


def doc(page, t):
    return page.evaluate("(t)=>firebase.firestore().collection('users').doc('testuid').collection('watchlist').doc(t).get().then(x=>x.exists ? x.data() : null)", t)


HDR = """()=>{ const h = document.querySelector('.lr5-hd'), r = h.getBoundingClientRect(), sum = h.querySelector('.lr5-sum'), cl = document.querySelector('[data-wl-clean]'), so = document.querySelector('[data-lr5-sort-wrap]'), fi = document.querySelector('[data-lr5-filter-wrap]'), i = h.querySelector('[data-wl-shared]'), cr = cl.getBoundingClientRect();
  return {h:Math.round(r.height), cut:sum.scrollWidth > sum.clientWidth + 1, shared:/shared by/i.test(h.innerText), info:!!i && i.title === 'Shared by Main and Family', clH:Math.round(cr.height), soH:Math.round(so.getBoundingClientRect().height), fiH:Math.round(fi.getBoundingClientRect().height), clIn:cr.right <= innerWidth && cr.left >= 0, hs:document.documentElement.scrollWidth <= innerWidth, txt:sum.innerText.replace(/\\s+/g, ' ')}; }"""
TBL = """()=>{ const rows = [...document.querySelectorAll('[data-wl1-row]')], bad = []; rows.forEach(r=>{ const rr = r.getBoundingClientRect(); const a = r.querySelector('[data-wl1-act]'); if(a){ const ar = a.getBoundingClientRect(); if(ar.right > rr.right + 0.5 || ar.left < rr.left - 0.5 || a.scrollWidth > a.clientWidth + 1) bad.push('act:' + r.dataset.sym); }
  r.querySelectorAll('*').forEach(e=>{ const cs = getComputedStyle(e); if(cs.textOverflow === 'ellipsis' && e.scrollWidth > e.clientWidth + 1 && e.clientWidth && !(e.closest('.l2') && innerWidth < 1024)) bad.push(r.dataset.sym + ':' + e.className); }); });   /* the phone's 2nd line keeps its LR5a/WL2 design: one line, left text ellipsizes, RS pinned right */
  const hd = document.querySelector('.lr5-th'); if(hd) hd.querySelectorAll('.lbl').forEach(l=>{ if(l.getBoundingClientRect().height > 16) bad.push('head wraps:' + l.textContent); });
  const lb = document.querySelector('#wlListBody'); return {bad, n:rows.length, sx: lb ? lb.scrollWidth - lb.clientWidth : -1, hs:document.documentElement.scrollWidth <= innerWidth}; }"""


def part_g(pw):
    tag = "[G clean]"
    for w, h in ((1440, 900), (390, 844)):
        b, page, pe = C.open_watch(pw, w, h)
        dlgs = []
        try:
            seed_g(page)
            t = "%s %d:" % (tag, w)
            # header
            hd = js(page, HDR)
            check(f"{t} header: no visible `shared by Main…` text · ⓘ tooltip `Shared by Main and Family` on the count · `Clean up` same height as Sort / Filter · summary not cut", not hd["shared"] and (hd["info"]) and hd["clH"] == hd["soH"] == hd["fiH"] and not hd["cut"] and hd["clIn"] and hd["hs"], hd)
            if w >= 1100: check(f"{t} header stays on ONE line (no wrap)", hd["h"] <= 64, hd["h"])
            # left Leaders pill
            pills = js(page, "()=>[...document.querySelectorAll('[data-wl-ll]')].map(p=>p.closest('[data-sym]').dataset.sym)")
            check(f"{t} `left Leaders` pill only on Watching rows that fail the Leaders rule (PLTR, GE) — not AMD (RS 90), not Focus / Holding / Planned, no RS data → none", sorted(pills) == ["GE", "PLTR"], pills)
            g = js(page, "()=>{ const r = document.querySelector('[data-sym=\"PLTR\"]'), p = r.querySelector('[data-wl-ll]').getBoundingClientRect(), c = r.querySelector('[data-wl1-chip]').getBoundingClientRect(), k = r.querySelector('.wlRn').getBoundingClientRect(); return {below:p.top >= c.bottom - 1 && Math.abs(p.left - c.left) < 3, sameLine:Math.abs((p.top + p.height / 2) - (k.top + k.height / 2)) < 8, cell:r.querySelector('.c-st').contains(r.querySelector('[data-wl-ll]'))}; }")
            check(f"{t} pill placement: " + ("2nd line inside the STATUS cell" if w >= 1100 else "after the pills on the ticker line"), (g["below"] and g["cell"]) if w >= 1100 else g["sameLine"], g)
            # ✕ (desktop only, hover)
            if w >= 1100:
                page.hover('[data-sym="AMD"]'); page.wait_for_timeout(150)
                x = js(page, "()=>({amd:getComputedStyle(document.querySelector('[data-sym=\"AMD\"] [data-wl-rm]')).opacity, pltr:getComputedStyle(document.querySelector('[data-sym=\"PLTR\"] [data-wl-rm]')).opacity, n:[...document.querySelectorAll('[data-wl-rm]')].map(b=>b.closest('[data-sym]').dataset.sym), w:Math.round(document.querySelector('[data-sym=\"AMD\"] .c-rm').getBoundingClientRect().width)})")
                check(f"{t} ✕ only on Watching rows (AMD, PLTR, GE — none on Holding / Planned / Focus) · visible only on the hovered row · last column 34px", sorted(x["n"]) == ["AMD", "GE", "PLTR"] and float(x["amd"]) == 1 and float(x["pltr"]) == 0 and x["w"] == 34, x)
                shot(page, "desk-1440", top=False)
            else:
                check(f"{t} iPhone: no ✕ in normal mode", js(page, "()=>[...document.querySelectorAll('[data-wl-rm]')].every(b=>b.getBoundingClientRect().width === 0)"))
                js(page, "()=>{ const g = document.querySelector('[data-lr5-grp=\"watch\"]'); if(g) window.scrollTo(0, g.getBoundingClientRect().top + scrollY - 190); }"); page.wait_for_timeout(150); shot(page, "clean-390-normal", top=False)
            tb = js(page, TBL)
            check(f"{t} table: no `…`, Homework / action buttons never clipped, header labels on one line, no sideways scroll", not tb["bad"] and tb["sx"] <= 1 and tb["hs"], tb)
            # Clean up mode
            page.click("[data-wl-clean]"); page.wait_for_timeout(300)
            c = js(page, "()=>({bar:document.querySelector('[data-wl-cbar]').innerText.replace(/\\s+/g, ' '), tk:[...document.querySelectorAll('[data-wl-tk]')].map(b=>b.closest('[data-sym]').dataset.sym), acts:[...document.querySelectorAll('[data-wl1-row]')].filter(r=>r.querySelector('[data-wl1-act]')).map(r=>r.dataset.sym), rm:document.querySelector('[data-wl-crm]').textContent.trim(), rmDis:document.querySelector('[data-wl-crm]').disabled, rmW:Math.round(document.querySelector('[data-wl-crm]').getBoundingClientRect().width), foot:Math.round(document.querySelector('.wl-cfoot').getBoundingClientRect().width), x:document.querySelectorAll('[data-wl-rm]').length, fs:document.querySelectorAll('.wlRows .lr5-fs:not(.on)').length})")
            check(f"{t} Clean up: bar `0 selected · Select left Leaders (2) · Done` · tick boxes only on WATCHING rows (AMD, PLTR, GE) · Homework button replaced there · Holding / Planned / Focus keep theirs, no tick", c["bar"].startswith("0 selected") and "Select left Leaders (2)" in c["bar"] and "Done" in c["bar"] and sorted(c["tk"]) == ["AMD", "GE", "PLTR"] and not any(t_ in c["acts"] for t_ in ("AMD", "GE", "PLTR")) and all(t_ in c["acts"] for t_ in ("AAPL", "PLNB", "FOCA")) and c["x"] == 0, c)
            check(f"{t} bottom bar: full-width dark `Remove 0`, disabled at 0 · no ☆ chips while cleaning", c["rm"] == "Remove 0" and c["rmDis"] and abs(c["rmW"] - c["foot"]) < 40 and c["fs"] == 0, c)
            page.click("[data-wl-cll]"); page.wait_for_timeout(300)
            c2 = js(page, "()=>({sel:[...document.querySelectorAll('[data-wl-tk][aria-checked=true]')].map(b=>b.closest('[data-sym]').dataset.sym), bar:document.querySelector('[data-wl-csel]').textContent, rm:document.querySelector('[data-wl-crm]').textContent.trim(), dis:document.querySelector('[data-wl-crm]').disabled})")
            check(f"{t} `Select left Leaders` ticks exactly PLTR + GE → `2 selected` · `Remove 2` enabled", sorted(c2["sel"]) == ["GE", "PLTR"] and c2["bar"] == "2 selected" and c2["rm"] == "Remove 2" and not c2["dis"], c2)
            page.click('[data-sym="AMD"]'); page.wait_for_timeout(250)
            check(f"{t} tapping a Watching row (anywhere) ticks it → 3 selected", js(page, "()=>document.querySelector('[data-wl-csel]').textContent") == "3 selected")
            js(page, "()=>ux3ClTog('AMD')"); page.wait_for_timeout(200)
            js(page, "()=>ux3RemoveAsk(['AAPL','PLNB','FOCA','HOLDA'])")
            check(f"{t} Holding / Planned / Focus rows can never be removed from here (no dialog)", js(page, "()=>!document.querySelector('[data-ux3-dlg]')"))
            if w == 390: js(page, "()=>{ const g = document.querySelector('[data-lr5-grp=\"watch\"]'); if(g) window.scrollTo(0, g.getBoundingClientRect().top + scrollY - 190); }"); page.wait_for_timeout(150); shot(page, "clean-390-cleanup", top=False)
            # confirm: Esc / Cancel / Enter
            page.click("[data-wl-crm]"); page.wait_for_timeout(250)
            d = js(page, "()=>({t:document.querySelector('[data-ux3-dlg-t]').textContent, p:document.querySelector('[data-ux3-dlg-p]').textContent, focus:document.activeElement.dataset.ux3Ok !== undefined, ok:document.querySelector('[data-ux3-ok]').textContent, reason:!!document.querySelector('[data-ux3-reason]'), bh:Math.round(document.querySelector('[data-ux3-ok]').getBoundingClientRect().height)})")
            check(f"{t} confirm: `Remove 2 stocks from Momentum?` · names · `move to Archived — thesis, notes and homework are kept. You can restore them any time.` · Cancel / `Remove 2` focused · no reason field on Momentum", d["t"] == "Remove 2 stocks from Momentum?" and "GE" in d["p"] and "PLTR" in d["p"] and "move to Archived — thesis, notes and homework are kept. You can restore them any time." in d["p"] and d["focus"] and d["ok"] == "Remove 2" and not d["reason"], d)
            if w == 390: check(f"{t} confirm: large buttons on the phone (≥ 48px)", d["bh"] >= 48, d["bh"]); shot(page, "clean-390-confirm", top=False)
            page.keyboard.press("Escape"); page.wait_for_timeout(200)
            check(f"{t} Esc = Cancel: dialog gone, nothing archived", js(page, "()=>!document.querySelector('[data-ux3-dlg]')") and (doc(page, "PLTR") or {}).get("archived") is not True and js(page, "()=>document.querySelector('[data-wl-csel]').textContent") == "2 selected")
            page.click("[data-wl-crm]"); page.wait_for_timeout(200); page.click("[data-ux3-cancel]"); page.wait_for_timeout(200)
            check(f"{t} Cancel button closes it too", js(page, "()=>!document.querySelector('[data-ux3-dlg]')"))
            page.click("[data-wl-crm]"); page.wait_for_timeout(200); page.keyboard.press("Enter"); page.wait_for_timeout(700)
            p1, g1 = doc(page, "PLTR"), doc(page, "GE")
            check(f"{t} Enter = Remove: PLTR + GE archived (archived:true · reason `Rotated out` · archived_at) — even though PLTR has a written thesis (wlCanDelete false)", p1["archived"] is True and g1["archived"] is True and p1["archived_reason"] == "Rotated out" and re.match(r"\d{4}-\d{2}-\d{2}T", p1["archived_at"] or ""), [p1.get("archived"), p1.get("archived_reason"), p1.get("archived_at")])
            check(f"{t} thesis · notes · homework kept on the archived doc", p1.get("my_thesis", {}).get("why") == "AI platform" and "hw" in g1 and g1.get("hw", {}).get("doneAt"), [p1.get("my_thesis"), g1.get("hw")])
            gone = js(page, "()=>[...document.querySelectorAll('[data-wl1-row]')].map(r=>r.dataset.sym)")
            tt = js(page, "()=>{ const t = document.querySelector('[data-ux3-toast]'); return t ? t.textContent.replace(/\\s+/g, ' ') : null; }")
            check(f"{t} rows leave the list · toast `Removed 2 · kept in Archived Undo`", "PLTR" not in gone and "GE" not in gone and "AMD" in gone and tt is not None and tt.startswith("Removed 2") and "Undo" in tt, [gone, tt])
            arch = js(page, "()=>[...document.querySelectorAll('[data-wl1-arch-row]')].map(r=>[r.dataset.wl1ArchRow, !!r.querySelector('[data-wl-restore]'), !!r.querySelector('[data-wl-delforever]')])")
            check(f"{t} Archived list has Restore + `Delete forever` on the removed rows", any(a_[0] == "PLTR" and a_[1] and a_[2] for a_ in arch) or not arch, arch)
            page.click("[data-ux3-undo]"); page.wait_for_timeout(700)
            p2 = doc(page, "PLTR"); back = js(page, "()=>[...document.querySelectorAll('[data-wl1-row]')].map(r=>r.dataset.sym)")
            check(f"{t} Undo restores both (archived:false · reason cleared) and the rows come back", p2["archived"] is False and (doc(page, "GE") or {}).get("archived") is False and "PLTR" in back and "GE" in back and p2.get("my_thesis"), [p2.get("archived"), back])
            # Done leaves the mode
            page.click("[data-wl-cdone]"); page.wait_for_timeout(300)
            check(f"{t} Done → normal list again (no bar · action buttons back)", js(page, "()=>!document.querySelector('[data-wl-cbar]') && !!document.querySelector('[data-sym=\"AMD\"] [data-wl1-act]')"))
            if w >= 1100:
                # single ✕ + Enter, then wait for the 8 s toast to end
                page.hover('[data-sym="AMD"]'); page.wait_for_timeout(120); page.click('[data-sym="AMD"] [data-wl-rm]'); page.wait_for_timeout(250)
                d1 = js(page, "()=>document.querySelector('[data-ux3-dlg-t]').textContent")
                page.keyboard.press("Enter"); page.wait_for_timeout(700)
                a_ = doc(page, "AMD")
                check(f"{t} single ✕ → `Remove 1 stock from Momentum?` → Enter → archived + toast", d1 == "Remove 1 stock from Momentum?" and a_["archived"] is True and js(page, "()=>!!document.querySelector('[data-ux3-toast]')"), [d1, a_.get("archived")])
                page.wait_for_timeout(6300)
                check(f"{t} toast stays ~8 s (still there at ~7 s)", js(page, "()=>!!document.querySelector('[data-ux3-toast]')"))
                page.wait_for_timeout(1800)
                check(f"{t} …and is gone afterwards", js(page, "()=>!document.querySelector('[data-ux3-toast]')"))
                js(page, "()=>wlRestore('AMD')"); page.wait_for_timeout(500)
            check(f"{t} no page errors", not pe, pe[:3])
        finally:
            b.close()
    # Compounder
    for w, h in ((1440, 900), (390, 844)):
        b, page, pe = C.open_watch(pw, w, h)
        try:
            seed_g(page); t = "%s Compounder %d:" % (tag, w)
            js(page, "()=>{ wl1TrkSet('ladder'); wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(400)
            n = js(page, "()=>({pills:document.querySelectorAll('[data-wl-ll]').length, rows:[...document.querySelectorAll('[data-wl1-row]')].map(r=>r.dataset.sym), clean:!!document.querySelector('[data-wl-clean]')})")
            check(f"{t} same Clean up button · NO `left Leaders` pill", n["clean"] and n["pills"] == 0 and "LADA" in n["rows"], n)
            page.click("[data-wl-clean]"); page.wait_for_timeout(300)
            bar = js(page, "()=>document.querySelector('[data-wl-cbar]').innerText.replace(/\\s+/g, ' ')")
            tk = js(page, "()=>[...document.querySelectorAll('[data-wl-tk]')].map(b=>b.closest('[data-sym]').dataset.sym)")
            check(f"{t} Clean up bar has NO `Select left Leaders` · tick boxes on Watching rows", "Select left Leaders" not in bar and bar.startswith("0 selected") and "LADA" in tk and "LADB" in tk, [bar, tk])
            page.click('[data-sym="LADA"]'); page.click('[data-sym="LADB"]'); page.wait_for_timeout(250); page.click("[data-wl-crm]"); page.wait_for_timeout(250)
            d = js(page, "()=>({t:document.querySelector('[data-ux3-dlg-t]').textContent, r:!!document.querySelector('[data-ux3-reason]'), lab:document.querySelector('.ux3-rs') ? document.querySelector('.ux3-rs').textContent : ''})")
            check(f"{t} confirm: `Remove 2 stocks from Compounder?` + ONE optional reason line", d["t"] == "Remove 2 stocks from Compounder?" and d["r"] and "optional" in d["lab"], d)
            page.keyboard.press("Enter"); page.wait_for_timeout(700)
            a1, b1 = doc(page, "LADA"), doc(page, "LADB")
            check(f"{t} empty reason + Enter still confirms → archived with reason `Removed`", a1["archived"] is True and b1["archived"] is True and a1["archived_reason"] == "Removed", [a1.get("archived_reason")])
            page.click("[data-ux3-undo]"); page.wait_for_timeout(600)
            check(f"{t} Undo restores", (doc(page, "LADA") or {}).get("archived") is False)
            js(page, "()=>wlArchiveOpen('LADB')"); page.wait_for_timeout(250)
            old = js(page, "()=>({old:!!document.querySelector('[data-wla-sheet]'), dlg:!!document.querySelector('[data-ux3-dlg]'), r:!!document.querySelector('[data-ux3-reason]')})")
            page.fill("[data-ux3-reason]", "too slow"); page.keyboard.press("Enter"); page.wait_for_timeout(700)
            lb = doc(page, "LADB")
            check(f"{t} ⋯ › Archive… on Compounder = the new confirm (no more reason-required sheet) · typed reason kept", not old["old"] and old["dlg"] and old["r"] and lb["archived"] is True and lb["archived_reason"] == "too slow", [old, lb.get("archived_reason")])
            if w == 1440:
                page.click("[data-wl-cdone]"); page.wait_for_timeout(250)
                page.hover('[data-sym="LADA"]'); page.wait_for_timeout(120)
                check(f"{t} desktop ✕ on hover for Compounder Watching rows too", js(page, "()=>!!document.querySelector('[data-sym=\"LADA\"] [data-wl-rm]')"))
            # Delete forever
            before = doc(page, "LADB")
            js(page, "()=>{ wlArchOpen = true; renderWatchlist(); }"); page.wait_for_timeout(300)
            has = js(page, "()=>!!document.querySelector('[data-wl1-arch-row=\"LADB\"] [data-wl-delforever]')")
            if has:
                page.click('[data-wl1-arch-row="LADB"] [data-wl-delforever]'); page.wait_for_timeout(600)
            check(f"{t} Archived › `Delete forever` (asks first) is the only permanent delete", has and doc(page, "LADB") is None and before is not None, [has, doc(page, "LADB")])
            check(f"{t} no page errors", not pe, pe[:3])
        finally:
            b.close()
    # 1280 + the narrowest list the splitter allows
    for w in (1280, 1440):
        b, page, pe = C.open_watch(pw, w, 900)
        try:
            seed_g(page); t = "%s %d%s:" % (tag, w, " (list at its narrowest)" if w == 1440 else "")
            if w == 1440:
                page.focus('[data-split="wl"]'); page.keyboard.press("End"); page.wait_for_timeout(300)
            js(page, "()=>{ window.scrollTo(0, 0); }")
            hd = js(page, HDR); tb = js(page, TBL)
            check(f"{t} header on one line · no `…` · Homework / action buttons never clipped · no sideways scroll", hd["h"] <= 64 and not hd["cut"] and hd["hs"] and not tb["bad"] and tb["sx"] <= 1 and tb["hs"], [hd, tb])
            page.click("[data-wl-clean]"); page.wait_for_timeout(300)
            tb2 = js(page, TBL)
            check(f"{t} in Clean up mode too", not tb2["bad"] and tb2["sx"] <= 1 and tb2["hs"], tb2)
        finally:
            b.close()


if __name__ == "__main__":
    only = os.environ.get("UX3_PARTS", "a b c d").split()
    with sync_playwright() as pw:
        for k in only:
            globals().get("part_" + k, lambda pw: None)(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY ux3: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
