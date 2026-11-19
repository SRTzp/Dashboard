#!/usr/bin/env python3
"""ID1 — before | after shots -> tests/screenshots/id1/ (ideas-1440 · ideas-1440-expand · ideas-390-sheet).
'after' = this checkout; 'before' = ID1_BEFORE=<dir of a checkout of the previous main>.  Run: python3 tests/id1_side.py"""
import os, sys, subprocess, json
from playwright.sync_api import sync_playwright
import id1_common as C
from lr5b_side import side
from re1d_common import js, NOANIM

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "screenshots", "id1"); os.makedirs(OUT, exist_ok=True)


def shots(tag):
    with sync_playwright() as pw:
        for w, h, tab in ((1440, 900, "sum"), (390, 844, "sum")):
            b, page, r = C.open_ideas(pw, w, h, tab=tab)
            try:
                page.add_style_tag(content=NOANIM); page.mouse.move(2, 2); page.wait_for_timeout(300)
                if w == 1440:
                    page.screenshot(path=os.path.join(OUT, f"_{tag}-ideas-1440.png"))
                    js(page, "()=>wlFullSet(true)"); page.wait_for_timeout(500)
                    page.screenshot(path=os.path.join(OUT, f"_{tag}-ideas-1440-expand.png"))
                else:
                    page.screenshot(path=os.path.join(OUT, f"_{tag}-ideas-390-sheet.png"))
            finally:
                b.close()


def main():
    if os.environ.get("ID1_SHOTS"):
        shots(os.environ["ID1_SHOTS"]); return
    before = os.environ.get("ID1_BEFORE")
    if before:
        subprocess.check_call([sys.executable, os.path.join(before, "tests", "id1_side.py")], cwd=os.path.join(before, "tests"), env=dict(os.environ, ID1_SHOTS="before", ID1_BEFORE=""))
        import shutil
        for n in os.listdir(os.path.join(before, "tests", "screenshots", "id1")):
            if n.startswith("_before"): shutil.copy(os.path.join(before, "tests", "screenshots", "id1", n), os.path.join(OUT, n))
    shots("after")
    with sync_playwright() as pw:
        for n, w in (("ideas-1440", 1440), ("ideas-1440-expand", 1440), ("ideas-390-sheet", 390)):
            a, b_ = os.path.join(OUT, f"_before-{n}.png"), os.path.join(OUT, f"_after-{n}.png")
            if os.path.exists(a): side(pw, a, b_, os.path.join(OUT, f"{n}.png"), w)
    for n in os.listdir(OUT):
        if n.startswith("_"): os.remove(os.path.join(OUT, n))


if __name__ == "__main__":
    main()
