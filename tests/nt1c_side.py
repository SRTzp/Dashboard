#!/usr/bin/env python3
"""NT1c — proof PNGs → tests/screenshots/nt1c/: Watch-My-ideas-1440 (WatchIdeasFull.html | live) · Watch-AI-1280 · Today-ideas-card-1280/1440/390 (live, long titles)."""
import os
from playwright.sync_api import sync_playwright
import net_stub
import nt1_side as NS, nt1_common as N, run_tests_nt1 as T, run_tests_nt1b as B, run_tests_nt1c as C
from re1d_common import js

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "screenshots", "nt1c"); os.makedirs(OUT, exist_ok=True); NS.OUT = OUT


def main():
    with sync_playwright() as pw:
        m = os.path.join(OUT, "m.png"); l = os.path.join(OUT, "l.png")
        NS.mock_shot(pw, "WatchIdeasFull.html", "body", 0, m, 1440)
        b, page, pe = N.open_nt1(pw, 1440, 900); N.goto_watch(page); T.to_my(page, "m1"); page.mouse.move(2, 2); page.screenshot(path=l); b.close()
        NS.compose(pw, m, l, os.path.join(OUT, "Watch-My-ideas-1440-side.png"), 1000, 1000)
        os.remove(m); os.remove(l)
        b, page, pe = N.open_nt1(pw, 1280, 800); T.extra_ai(page); N.goto_watch(page); T.to_ai(page); page.mouse.move(2, 2); page.screenshot(path=os.path.join(OUT, "Watch-AI-1280.png")); b.close()
        for w, h in ((1280, 800), (1440, 900), (390, 844)):
            b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
            if w <= 600: page.add_style_tag(content="#tabsMain{display:none!important}")
            t0 = B.td(page); B.quiet_fixture_ai(page)
            B.seed_my(page, {"a": B.mkmy(1, ("stock", "AVGO"), C.LONG, B.add(t0, -1), B.add(t0, 6), next="Close above 190 on volume and then write the plan", level=102),
                             "b": B.mkmy(2, ("market", "US"), "Risk-off until CPI", B.add(t0, -2), B.add(t0, -2), next="Read CPI → still bear?")})
            B.seed_ai(page, "ai-x", "AI power: grid equipment and the chain behind it", "need_evidence", recheck=t0); B.px(page, "AVGO", 100.0); B.to_today(page); page.mouse.move(2, 2)
            page.query_selector("[data-nt1b-ideas]").screenshot(path=os.path.join(OUT, f"Today-ideas-card-{w}.png")); b.close()
    print("ok")


if __name__ == "__main__":
    main()
