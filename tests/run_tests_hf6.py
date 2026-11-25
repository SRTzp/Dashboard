#!/usr/bin/env python3
"""HF6 — account saves never carry nested arrays (RRG tails flat) · fsSafe guard · "Not saved · Retry" bar · dangling Sat trade_id repaired.
Run: python3 tests/run_tests_hf6.py   (HF6_SHOTS=1 writes docs/screenshots/hf6-*.png · docs/briefs/HF6-brief.md)"""
import sys, os, json
from playwright.sync_api import sync_playwright
from re1d_common import js, launch, check, results
import run_tests_lrf as LF
import run_tests_ux3 as U
import run_tests_hf3 as H
import run_tests_hf5 as _h5   # noqa (suite import keeps the helpers loaded)
import hf5_common as C5
import lr5_common as C

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
NEST = "()=>(window.__nestedWrites || []).map(x=>x.path + ' :: ' + x.field)"
BAR = "()=>{ const b = document.getElementById('hf6SaveBar'); if(!b) return null; const r = b.getBoundingClientRect(); return {t: b.innerText.replace(/\\s+/g,' ').trim(), top: r.top, w: r.width, ovf: document.documentElement.scrollWidth - innerWidth}; }"


def flush(page):
    js(page, "()=>{ try{ dirtyBooks.set(acctActive, (dirtyBooks.get(acctActive)||0)+1); }catch(e){} pendingLocalWrite = true; return doPersist(); }"); page.wait_for_timeout(700)


def part_flow(pw):
    full = U.rr_bars(); full800 = {s_: r[-800:] for s_, r in full.items()}
    import re
    b, page, pe = C.open_watch(pw, 1440, 900, plan_cards=False)
    try:
        calls = []
        page.route(re.compile(r"api\.twelvedata\.com"), U.rr_td_handler(full800, calls))
        U.rr_prep(page, U.rr_doc(), key="")
        js(page, "()=>{ window.__nestedWrites = []; switchTab('flow'); const f = ffState(); f.themesCol = false; f.themesColUser = true; ffRenderThemes(); }"); page.wait_for_timeout(1500)
        n = js(page, "()=>{ const r = ffState().rrg; const nested = x=>Array.isArray(x) && x.some(v=>Array.isArray(v)); return {src:r.src, d:(r.rowsD||[]).length, flat:(r.rowsD||[]).every(x=>Array.isArray(x.tailF) && x.tailF.length === 10 && !('tail' in x)), nest:[...(r.rowsD||[]), ...(r.rowsW||[])].some(x=>nested(x.tail))}; }")
        check("[flow] job RRG rows have flat tailF (10 numbers), no nested tail", n["src"] == "job" and n["d"] == 23 and n["flat"] and not n["nest"], n)
        flush(page)
        check("[flow] persist with the job rows succeeds under the strict mock (no nested-array write)", js(page, NEST) == [] and (js(page, "()=>document.getElementById('hf6SaveBar')") is None), js(page, NEST))
        dr = js(page, "()=>{ const rows = (ffState().rrg.rowsD||[]); return rows.length && rows.every(x=>lr4Pts(x).length === 5); }")
        check("[flow] tails still draw (5 points per row)", dr)
        # reload → rebuilt
        cnt = js(page, "()=>document.querySelectorAll('[data-lr4-rrg] polyline').length")
        check("[flow] chart draws tail polylines", cnt > 0, cnt)
    finally:
        b.close()


def part_old(pw):
    b, page, pe = C.open_watch(pw, 1440, 900, plan_cards=False)
    try:
        js(page, """()=>{ const f = ffState(); const mk = s=>({sym:s, name:s, quad:'lead', ratio:101, mom:100.5, dMom:0.1, days:3, prevDays:2, err:null, tail:[[100,100],[100.4,100.1],[100.8,100.3],[101,100.5]]});
          f.rrg.rowsD = ['XLK','XLE'].map(mk); f.rrg.rowsW = ['XLK'].map(mk); f.rrg.model = RRG_MODEL; f.rrg.build = RRG_BUILD; window.__nestedWrites = []; }""")
        pre = js(page, "()=>{ const w = fsSafe({a:1, rows:ffState().rrg.rowsD}, 'probe'); return JSON.stringify(w).includes('[[') }")
        check("[old] fsSafe on a state still holding tail:[[…]] drops the nested field (no [[ left)", pre is False, pre)
        js(page, "()=>{ ffState(); }")
        r = js(page, "()=>({tail: [...ffState().rrg.rowsD, ...ffState().rrg.rowsW].some(x=>'tail' in x), F: ffState().rrg.rowsD[0].tailF})")
        check("[old] load cleans: no tail left, converted to flat tailF (8 numbers)", not r["tail"] and r["F"] and len(r["F"]) == 8, r)
        flush(page)
        check("[old] next save succeeds (no nested write, no bar)", js(page, NEST) == [] and js(page, "()=>document.getElementById('hf6SaveBar')") is None, js(page, NEST))
    finally:
        b.close()


def part_guard(pw):
    b, page, ce, pe = launch(pw, 1440, 900, c=LF.cards_today())
    try:
        errs = []
        page.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        r = js(page, """()=>{ const o = {a:1, ok:{x:2, u:undefined, n:NaN, inf:Infinity, nest:[[1,2],[3,4]], arr:[{p:1},{q:undefined}]}, keep:[1,2,3]}; const s = fsSafe(o, 'probe'); return {s, caught: hf6Caught.slice()}; }""")
        s = r["s"]
        check("[fsSafe] nested array / undefined / NaN / Infinity dropped, the rest kept", s["a"] == 1 and s["ok"]["x"] == 2 and "nest" not in s["ok"] and "u" not in s["ok"] and "n" not in s["ok"] and "inf" not in s["ok"] and s["keep"] == [1, 2, 3] and s["ok"]["arr"] == [{"p": 1}, {}], s)
        paths = [c["path"] for c in r["caught"]]
        check("[fsSafe] every drop is logged with its exact path (console.error)", all(any(x.startswith(p) for x in paths) for p in ("ok.nest", "ok.u", "ok.n", "ok.inf", "ok.arr[1].q")) and any("nested array at ok.nest" in e for e in errs), [paths, errs[:2]])
        # a write with a nested field through the real writers → the rest saves
        js(page, "()=>{ window.__nestedWrites = []; sat7dWrite('satIdeas','hf6g',{id:'hf6g', asset:'XAUUSD', bad:[[1,2]], ok:7}); }"); page.wait_for_timeout(300)
        d = js(page, "()=>{ const x = firebase.__mockDb && firebase.__mockDb.__getDoc ? firebase.__mockDb.__getDoc(['users','testuid','satIdeas','hf6g']) : null; return x; }")
        check("[fsSafe] sat7dWrite with a nested field: rest saved, no rejected write", js(page, NEST) == [] and (d is None or (d.get("ok") == 7 and "bad" not in d)), [js(page, NEST), d])
    finally:
        b.close()


def part_bar(pw):
    for w, h in ((1440, 900), (390, 844)):
        b, page, ce, pe = launch(pw, w, h, c=LF.cards_today())
        try:
            js(page, "()=>{ window.__forceSaveFail = true; }")
            flush(page)
            bar = js(page, BAR)
            check(f"[bar {w}] forced save failure → amber '⚠ Not saved · … · Retry ›' bar at the top", bar and bar["t"].startswith("⚠ Not saved ·") and bar["t"].endswith("Retry ›") and bar["top"] <= 1 and bar["ovf"] <= 0, bar)
            if os.environ.get("HF6_SHOTS"):
                os.makedirs(SHOTS, exist_ok=True); page.screenshot(path=os.path.join(SHOTS, "hf6-notsaved-%d.png" % w))
            js(page, "()=>{ window.__forceSaveFail = false; }")
            page.evaluate("()=>document.querySelector('[data-hf6-retry]').click()"); page.wait_for_timeout(900)
            check(f"[bar {w}] Retry after the fix → bar gone", js(page, BAR) is None, js(page, BAR))
        finally:
            b.close()


def part_dangling(pw):
    b, page, ce, pe = C5.start(pw)
    try:
        C5.mk(page, "hf6d", "XAUUSD", "Short")
        st = C5.place(page, "hf6d")
        check("[dangling] order placed", st.get("placed"), st)
        # dangle: trade_id points at a trade that is not in the book
        js(page, "()=>{ const i = sat7dIdea('hf6d'); const a = pb2AcctOf(i); i.accts = Object.assign({}, i.accts||{}, {[a]: Object.assign({}, (i.accts||{})[a]||{}, {lot:0.11, trade_id:'t_missing_main'})}); }")
        js(page, "()=>{ window.__nestedWrites = []; }")
        t = C5.fill(page, "hf6d")
        check("[dangling] Filled → trade created from the plan, status open", t and t["status"] == "open", t)
        r = js(page, "()=>{ const i = sat7dIdea('hf6d'); const a = pb2AcctOf(i); const tid = ((i.accts||{})[a]||{}).trade_id; return {tid, inBook: getBook(a).trades.some(x=>x.id===tid), row: !!document.querySelector('[data-hf3-block]')}; }")
        check("[dangling] slot now points at a real trade (not the missing id)", r["inBook"] and r["tid"] != "t_missing_main", r)
        check("[dangling] no nested/undefined write", js(page, NEST) == [])
    finally:
        b.close()
    b, page, ce, pe = C5.start(pw)
    try:
        # repair on load: a dangling slot with the book built
        C5.mk(page, "hf6e", "XAUUSD", "Short")
        js(page, "()=>{ const i = sat7dIdea('hf6e'); i.accts = {main:{lot:0.11, trade_id:'t_gone'}}; hf6RepairSlots(); }")
        r = js(page, "()=>(sat7dIdea('hf6e').accts.main||{})")
        check("[dangling] load repair clears trade_id, keeps lot", "trade_id" not in r and r.get("lot") == 0.11, r)
        # Filled never returns silently
        js(page, "()=>{ window.__toast = []; const o = sdToast; window.sdToast = m=>{ window.__toast.push(m); }; pb2Filled('nope'); }")
        tt = js(page, "()=>window.__toast")
        check("[dangling] Filled on an unknown setup shows a reason (no silent return)", tt and "Cannot record the fill" in tt[0], tt)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_flow(pw); part_old(pw); part_guard(pw); part_bar(pw); part_dangling(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY hf6: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
