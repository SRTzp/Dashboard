#!/usr/bin/env python3
"""PL1 end-of-Phase-A — screenshots @390 / @1440 → docs/briefs/PL1-screens/ (ไม่แก้สไตล์ · ใช้ข้อมูล SAMPLE ล้วน)
Add popup · Screening modal · Watchlist row + card · Compounder page · Today Plans block · พร้อมตรวจ overflow แนวนอน"""
import json, os
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase107 as T
import run_tests_phase111 as P111

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "briefs", "PL1-screens")
os.makedirs(OUT, exist_ok=True)
js, settle = C.js, T.settle
P13 = P111.P13
LOG = []


def snap(page, name, w, sel=None, full=False):
    path = os.path.join(OUT, f"{name}-{w}.png")
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=path)
        else: page.screenshot(path=path, full_page=full)
    except Exception as e:
        page.screenshot(path=path)
        LOG.append(f"{name}-{w}: element shot failed ({e}); viewport used")
    ov = C.overflow(page)
    LOG.append(f"{name}-{w}: overflow={ov}")


def put(page, t, **kw):
    doc = {"ticker": t, "market": "US", "port": "core", "note": "", "added_at": "2026-10-01T00:00:00Z"}; doc.update(kw)
    js(page, "([t,d])=>wlCol().doc(t).set(d)", [t, doc])


def card(**kw):
    c = {"acct": "main", "ticker": "AAA", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": None, "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z",
         "cs": {"eval": None, "date": "2026-10-20", "evalDate": "", "stars": None, "stars_src": "none", "baseRiskPct": 1, "riskAmt": 100, "equity": 1, "used": 0, "budget": 1, "adj": {"ff": 1, "dd": 1}, "capKey": "A"}}
    c.update(kw); return c


def open_card(sym, tid, **kw):
    return card(ticker=sym, trade_id=tid, status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 10, "f": 1, "stop": 90}], **kw)


def run(pw, w, h):
    # 1+2 Add popup, screening modal
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_today(page)
        js(page, "(v)=>td4AddIn(v)", "NVDA AMD PLTR"); js(page, "()=>td4AddCands()"); settle(page, 500)
        js(page, "()=>{ candPopAllTrack('winner'); candPopAllReason('strong-rs'); candPopIn(1,'note','breakout watch'); }"); settle(page, 300)
        js(page, "()=>{ candPop.rows[2].track = 'ladder'; candPopRender(); }"); settle(page, 300)
        snap(page, "add-popup", w, ".cpSh")
        js(page, "()=>candPopClose()"); settle(page, 200)
        js(page, "(d)=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, d); })", {"NVDA": {"manual": True, "sym": "NVDA", "market": "US", "cand_at": "2026-10-20T03:00:00.000Z", "track": "winner", "reasons": ["strong-rs"], "note": "from ideas", "link": "https://example.com/nvda"}}); settle(page, 300)
        js(page, "()=>scrOpen('NVDA')"); settle(page, 400)
        js(page, "()=>{ scrSet('proven','passed'); scrSet('trend','passed'); }"); settle(page, 200)
        page.fill("[data-scr-why]", "Margin expansion not yet priced in"); settle(page, 200)
        snap(page, "screening-modal", w, ".scrSh")
    finally: b.close()
    # 3 Watchlist row + card, 4 Compounder page, 5 Today Plans
    tr = [P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"), P13.T("tG", "core", "open", sym="GRN", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"),
          P13.T("tY", "core", "open", sym="YEL", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20"), P13.T("tC", "core", "open", sym="CMPO", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
    cards = {"cR": open_card("RED", "tR", px=85, emaW=95), "cG": open_card("GRN", "tG", px=110, emaW=95), "cY": open_card("YEL", "tY", px=94, emaW=95),
             "cD1": card(ticker="DRFA", plan={}, created_at="2026-10-21T00:00:00Z"), "cD2": card(ticker="DRFB", plan={"entry": 50, "stop": 45}, created_at="2026-10-22T00:00:00Z"),
             "cC": open_card("CMPO", "tC", track="ladder", px=100, emaW40=98), "cC2": card(ticker="CMPD", track="ladder", plan={"entry": 80, "stop": 72})}
    b, page, ce, pe = P111.core(pw, w, h, tr, cards)
    try:
        MT = lambda w_, x: {"why": w_, "exit": x, "updated_at": "2026-10-25T00:00:00Z"}
        put(page, "RED", reasons=["strong-rs"], rs_stars=3, my_thesis=MT("w", "x"), next_check_date="2026-11-20", next_check_note="Q3 earnings", ladder_watch=False)
        put(page, "GRN", reasons=["volume-spike", "strong-rs"], rs_stars=1, my_thesis=MT("w", ""), ladder_watch=False)
        put(page, "CMPO", reasons=["earnings-spike"], rs_stars=None, ladder_watch=True, ladder_watch_set=True, thesis={"date": "2026-09-01", "mode": "full", "summary": {"status": "ok"}}, thesis_imported_at="2026-10-20T00:00:00Z")
        put(page, "DRFB", reasons=["strong-rs"], rs_stars=0, my_thesis=MT("w", "x"), onboarding={"at": "2026-10-10T00:00:00Z", "fortress": "passed", "proven": "untested", "emerging": "untested", "trend40": "passed", "trend_basis": "weekly", "why_watch": "Steady compounder", "concerns": "valuation", "exception": "", "track": "winner"})
        put(page, "OLDARC", archived=True, archived_reason="thesis broke", archived_at="2026-10-30T00:00:00Z"); settle(page, 700)
        js(page, "()=>{ coreSheetClose(); switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); settle(page, 600)
        snap(page, "watchlist-rows", w)
        js(page, "()=>wlOpen('RED')"); settle(page, 600)
        snap(page, "watchlist-card", w, "#tabWatch", full=False)
        js(page, "()=>{ switchTab('plan'); setPlanScope('ladder'); render(); }"); settle(page, 800)
        snap(page, "compounder-page", w, "#tabPlan")
        js(page, "()=>{ ln1SetMode('lean'); switchTab('plan'); setPlanScope('ladder'); render(); }"); settle(page, 800)
        snap(page, "compounder-page-lean", w, "#tabPlan")
        T.go_today(page); settle(page, 600)
        js(page, "()=>{ window.scrollTo(0, document.documentElement.scrollHeight); }"); settle(page, 500)   # PL1 polish — เลื่อนสุดหน้าเพื่อโชว์ว่าปุ่ม ↑ ไม่ทับ Create plan ›
        snap(page, "today-plans", w, None if w < 600 else '[data-td3-panel="plans"]')
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            run(pw, w, h)
    print("\n".join(LOG))
    open(os.path.join(OUT, "overflow-log.txt"), "w", encoding="utf-8").write("\n".join(LOG) + "\n")


if __name__ == "__main__": main()
