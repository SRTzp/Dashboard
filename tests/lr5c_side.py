#!/usr/bin/env python3
"""LR5c — side-by-side proof: mockup (left) | live (right). Writes tests/screenshots/lr5c/*  Run: python3 tests/lr5c_side.py"""
import os
from playwright.sync_api import sync_playwright
import lr5c_common as C
from lr5b_side import mock, side
import lr5b_side as S
from re1d_common import js

OUT = os.path.join(S.HERE, "screenshots", "lr5c"); os.makedirs(OUT, exist_ok=True)
S.OUT = OUT


def live(pw, w, h, name, view="both"):
    b, page, pe = C.open_port(pw, w, h, view=view)
    try:
        page.mouse.move(2, 2); p = os.path.join(OUT, f"{name}-{w}-live.png"); page.screenshot(path=p, full_page=True); return p
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h, mf, nm in ((1440, 900, "PortBoth.dc.html", "port-1440-side.png"), (390, 844, "PortPhone.dc.html", "port-390-side.png")):
            m = mock(pw, w, h, mf, "port"); l = live(pw, w, h, "port")
            side(pw, m, l, os.path.join(OUT, nm), w)
        for v in ("main", "family"):
            p = live(pw, 1440, 900, "port-" + v, "main" if v == "main" else "fam"); os.replace(p, os.path.join(OUT, f"port-1440-{v}-live.png"))


if __name__ == "__main__":
    main()
