#!/usr/bin/env python3
"""PL2 — screenshots @390 / @1440 → docs/briefs/PL2-screens/ (SAMPLE data only; no style changes)
Today banner + Selection · My Thesis tab (images + AI preview) · Sat plan row · trade summary · Candidate flow."""
import json, os
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # must come first
import run_tests_phase107 as T
import run_tests_phase111 as P111
import run_tests_phase59 as P59
import run_tests_phase44 as P44
import run_tests_phase362 as X

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "briefs", "PL2-screens"); os.makedirs(OUT, exist_ok=True)
js, settle = C.js, T.settle
LOG = []

def snap(page, name, w, sel=None, full=False):
    path = os.path.join(OUT, f"{name}-{w}.png"); page.wait_for_timeout(900)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=path)
        else: page.screenshot(path=path, full_page=full)
    except Exception as e:
        page.screenshot(path=path); LOG.append(f"{name}-{w}: element shot failed ({e}); viewport used")
    LOG.append(f"{name}-{w}: overflow={C.overflow(page)} bytes={os.path.getsize(path)}")

def run(pw, w, h):
    # 1 Today: banner + Selection
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.inject(page, {"candMeta": {"MSFT": T.cm("MSFT", 3, "n1"), "PTT": dict(T.cm("PTT.BK", 2, "n2"), market="TH")}})
        T.clock(page, T.EVE); T.go_today(page); settle(page, 800); snap(page, "today-banner-selection", w)
    finally: b.close()
    # 2 My Thesis tab with images + AI preview
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        js(page, "()=>{ window.__READY_REAL = true; }")
        ai = {"date": "2026-09-01", "mode": "full", "summary": {"status": "ok", "biz": "SAMPLE AI summary", "call": {"action": "hold", "why": "SAMPLE: wait for the next quarter before adding"}}}
        js(page, "([a])=>wlCol().doc('MTA').set({ticker:'MTA', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', my_thesis:{why:'SAMPLE why buy', exit:'SAMPLE wrong if', updated_at:'2026-10-02T00:00:00Z'}, thesis:a, thesis_imported_at:'2026-10-20T00:00:00Z', next_check_date:'2026-11-20', next_check_note:'Q3 earnings'})", [ai])
        page.evaluate("""()=>window.firebase.__mockDb.__seedDoc(['users','testuid','stockNotes','MTA'], {event:[{id:'e1', d:'2026-09-10', t:'SAMPLE event note'}], fund:[{id:'f1', d:'2026-09-11', t:'SAMPLE fund note'}], tech:[{id:'t1', d:'2026-09-12', t:'SAMPLE tech note', chart:'%s'}], updated_at:'2026-09-12'})""" % X.TV)
        P44.reload_keep(page)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 500)
        js(page, "()=>{ wlOpen('MTA'); wlSetSub('view'); }"); settle(page, 900); snap(page, "my-thesis", w)
    finally: b.close()
    # 3 Sat plan row (verify checkboxes) + 4 trade summary
    b, page, ce, pe = P111.sat_launch(pw, w, h)
    try:
        tid = js(page, "()=>satV2NewPlan('XAUUSD','tactical')"); settle(page, 500)
        js(page, "([i])=>{ satV2SetDir(i,'Long'); }", [tid]); settle(page, 300)
        page.locator("[data-pf-ema50]").first.check(); settle(page, 400)
        snap(page, "sat-plan-row", w, "[data-pf-assess]")
    finally: b.close()
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        P111.ok_ev(page, "S3", stars=3); js(page, "()=>wlCol().doc('S3').set({ticker:'S3', market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z', rs_stars:2, reasons:['strong-rs','volume-spike']})"); settle(page, 500)
        P111.open_form(page, "S3"); P111.setpx(page, 100, 90); snap(page, "trade-summary", w, "#cnWBox")
    finally: b.close()
    # 5 Candidate flow: Candidates list + screening modal
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.inject(page, {"candMeta": {"MSFT": T.cm("MSFT", 3, "n1"), "PTT": dict(T.cm("PTT.BK", 2, "n2"), market="TH")}})
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); }"); settle(page, 700); snap(page, "candidates-list", w)
        js(page, "()=>scrOpen('MSFT')"); settle(page, 600); snap(page, "candidate-screening", w)
    finally: b.close()

if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)): run(pw, w, h)
    print("\n".join(LOG)); open(os.path.join(OUT, "LOG.txt"), "w").write("\n".join(LOG))
