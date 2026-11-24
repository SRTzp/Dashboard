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


def shot(page, name, **kw):
    if os.environ.get("UX3_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); js(page, "()=>window.scrollTo(0, 0)"); page.wait_for_timeout(80); page.screenshot(path=os.path.join(SHOTS, "ux3-%s.png" % name), **kw)


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


if __name__ == "__main__":
    only = os.environ.get("UX3_PARTS", "a b c d").split()
    with sync_playwright() as pw:
        for k in only:
            globals().get("part_" + k, lambda pw: None)(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY ux3: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
