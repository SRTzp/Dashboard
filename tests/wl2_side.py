#!/usr/bin/env python3
"""WL2 — side-by-side proof: mockup (left) | live (right) at 1440 (MU selected) and 390 (list + MU sheet). Writes tests/screenshots/wl2/*.
Run: python3 tests/wl2_side.py"""
import os
from playwright.sync_api import sync_playwright
import wl2_common as W
import lr5a_side as S
from re1d_common import js

OUT = os.path.join(S.HERE, "screenshots", "wl2")
os.makedirs(OUT, exist_ok=True); S.OUT = OUT


def main():
    with sync_playwright() as pw:
        for w, h, mf in ((1440, 900, "WatchRS.dc.html"), (390, 844, "WatchRSPhone.dc.html")):
            m = S.mock(pw, w, h, mf, "wl2")
            def prep(page):
                if w >= 1024: js(page, "()=>{ wl5Sort = 'nearhigh'; renderWatchlist(); wlOpen('MU'); }")
                else: js(page, "()=>{ wl5Sort = 'nearhigh'; renderWatchlist(); wlOpen('MU'); }")
                page.wait_for_timeout(500)
            l, H = S.live(pw, w, h, "wl2", prep, full=(w >= 1024))
            S.side(pw, m, l, os.path.join(OUT, f"wl2-{w}-side.png"), w); print("wl2", w, "ok")
            if w < 600: import shutil; shutil.copy(l, os.path.join(OUT, "wl2-390-sheet.png"))
        for w, h in ((360, 780),):
            def prep(page): js(page, "()=>{ wl5Sort = 'nearhigh'; renderWatchlist(); }"); page.wait_for_timeout(300)
            S.live(pw, w, h, "wl2-list", prep, full=False)


if __name__ == "__main__":
    main()
