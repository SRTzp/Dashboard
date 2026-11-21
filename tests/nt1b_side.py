#!/usr/bin/env python3
"""NT1b — side-by-side proof: mockup (left) | live app (right) → tests/screenshots/nt1b/*-side.png. Run: python3 tests/nt1b_side.py
 Today-1440 (TodayIdeasV5) · Ideas-card (IdeasFollowUp A) · New-idea-sheet (B) · My-ideas-list (C) · My-ideas-1440 (WatchIdeasFull) · Today-390 / My-ideas-390 (live only)"""
import os
from playwright.sync_api import sync_playwright
import net_stub
import nt1_side as NS, nt1_common as N, run_tests_nt1b as R, run_tests_nt1 as T
from re1d_common import js
import re1d_common as K

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "screenshots", "nt1b"); os.makedirs(OUT, exist_ok=True)
NS.OUT = OUT


def mock(pw, file, sel, idx, path, w=1500):
    NS.mock_shot(pw, file, sel, idx, path, w)


def watch_page(pw, w, h):
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    page.route("**://s3.tradingview.com/**", lambda r: r.fulfill(status=200, content_type="image/svg+xml", body=NS.SVG))
    if w <= 600: page.add_style_tag(content="#tabsMain{display:none!important}")
    t0 = R.td(page); R.quiet_fixture_ai(page)
    R.seed_my(page, {
        "avgo": R.mkmy(1, ("stock", "AVGO"), "Breakout over 190 with volume", R.add(t0, -1), R.add(t0, 5), next="Close above 190 on 1.5× volume → plan Momentum", level=102, view="bull", ang={"tech": "Tight base 172–190 for 5 weeks, volume drying up.", "fund": "AI networking revenue +70% y/y."}),
        "usm": R.mkmy(2, ("market", "US"), "Risk-off until CPI cools", R.add(t0, -2), t0, next="Read CPI tonight → still bear?", view="bear"),
        "xau": R.mkmy(3, ("sat", "XAU"), "Buy dips while real yields fall", R.add(t0, -4), R.add(t0, -2), next="Wait 2,612 zone", view="bull", planId="avgo"),
        "nv": R.mkmy(4, ("stock", "AAPL"), "Pullback to 140 = add zone", R.add(t0, -6), R.add(t0, 9), next="Wait ② 140", view="bull", planId="aapl"),
        "gold": R.mkmy(5, ("market", "TH"), "Range 2,580–2,700 into FOMC", R.add(t0, -40), R.add(t0, 30), view="neutral", updated_at=R.add(t0, -34) + "T05:00:00.000Z")})
    R.px(page, "AVGO", 100.0)
    return b, page


def today_page(pw, w, h):
    b, page, pe = R.lrf_page(pw, w, h, working=False)
    R.seed_today_ideas(page); R.seed_ai(page, "ai-2", "AI power: grid", "need_evidence", recheck=R.td(page))
    R.L2.set_regime(page, "red", "red", "fresh"); R.L2.seed_wi(page); R.L2.seed_rrg(page)
    js(page, """()=>{ const d = Calc.wiIctDate(Date.now()), doc = wiDocs[wiCurMon()], h0 = +Calc.wiIctHM(Date.now()).slice(0, 2); const at = h => new Date(d + 'T' + String(h).padStart(2, '0') + ':30:00+07:00').toISOString();
      doc.events.cpi.scheduled_at = at(Math.min(h0 + 6, 23)); todayRefresh(true); }""")
    R.to_today(page); page.mouse.move(2, 2); page.wait_for_timeout(300)
    return b, page


def main():
    with sync_playwright() as pw:
        m = os.path.join(OUT, "m.png"); l = os.path.join(OUT, "l.png")
        mock(pw, "TodayIdeasV5.html", "body", 0, m, 1440)
        b, page = today_page(pw, 1440, 900); page.screenshot(path=l); b.close()
        NS.compose(pw, m, l, os.path.join(OUT, "Today-1440-side.png"), 1000, 1000); print("Today-1440")
        mock(pw, "IdeasFollowUp.html", ".panel", 0, m, 1000)
        b, page = today_page(pw, 1440, 900); page.query_selector("[data-nt1b-ideas]").screenshot(path=l); b.close()
        NS.compose(pw, m, l, os.path.join(OUT, "Ideas-card-side.png"), 440, 440); print("Ideas-card")
        mock(pw, "IdeasFollowUp.html", ".sheet", 0, m, 1000)
        b, page = watch_page(pw, 1440, 900)
        T.to_my(page); js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(200)
        page.select_option("#nt1fSubj", "stock:AVGO"); page.fill("#nt1fTitle", "Breakout over 190 with volume"); page.fill("#nt1fNext", "Close above 190 on 1.5× volume → plan Momentum"); page.fill("#nt1fLevel", "190"); page.click('[data-nt1-fv="bull"]')
        page.query_selector("#ltModal").screenshot(path=l); b.close()
        NS.compose(pw, m, l, os.path.join(OUT, "New-idea-sheet-side.png"), 560, 560); print("sheet")
        mock(pw, "IdeasFollowUp.html", ".panel.list", 0, m, 1000)
        b, page = watch_page(pw, 1440, 900); N.goto_watch(page); T.to_my(page, "avgo"); page.query_selector("[data-nt1-list]").screenshot(path=l); b.close()
        NS.compose(pw, m, l, os.path.join(OUT, "My-ideas-list-side.png"), 560, 560); print("list")
        mock(pw, "WatchIdeasFull.html", "body", 0, m, 1440)
        b, page = watch_page(pw, 1440, 900); N.goto_watch(page); T.to_my(page, "avgo"); page.mouse.move(2, 2); page.screenshot(path=l); b.close()
        NS.compose(pw, m, l, os.path.join(OUT, "My-ideas-1440-side.png"), 1000, 1000); print("My-ideas-1440")
        b, page = today_page(pw, 390, 844); page.screenshot(path=os.path.join(OUT, "Today-390.png"), full_page=True); b.close()
        b, page = watch_page(pw, 390, 844); N.goto_watch(page); T.to_my(page); page.screenshot(path=os.path.join(OUT, "My-ideas-390.png")); b.close()
        for f in ("m.png", "l.png"): os.remove(os.path.join(OUT, f))
    print("ok")


if __name__ == "__main__":
    main()
