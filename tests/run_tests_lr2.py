#!/usr/bin/env python3
"""LR2 — Today: tab shortcuts (0) · glance band (A) · one Act list (B) · side column + Risk room (C).
Screenshots (tests/screenshots, git add -f): lr2-today-1440 · lr2-today-390 · lr2-act-family-place-390 · lr2-glance-empty-1440
Run: python3 tests/run_tests_lr2.py"""
import os, sys, re, json
from playwright.sync_api import sync_playwright
import net_stub  # no real network in tests
import re1d_common as K
from re1d_common import js, launch, check, results, plan_card

SHOTS = K.SHOTS
def sp(t): return re.sub(r"\s+", " ", t or "").strip()
def ovf(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")


def part0(page, tag):
    order = js(page, "()=>TAB_ORDER")
    check(f"{tag} 0: TAB_ORDER = today,plan,flow,watch,journal,mix", order == ["today", "plan", "flow", "watch", "journal", "mix"], order)
    js(page, "()=>switchTab('today')"); page.wait_for_timeout(150)
    res = []
    for k, t in (("1", "today"), ("2", "plan"), ("3", "flow"), ("4", "watch"), ("5", "journal"), ("6", "mix")):
        page.keyboard.press(k); page.wait_for_timeout(150); res.append(js(page, "()=>activeTab") == t)
    check(f"{tag} 0: keys 1 Today · 2 Plan · 3 Flow · 4 Watch · 5 Journal · 6 Port", all(res), res)
    tips = js(page, "()=>[...document.querySelectorAll('#tabsMain .tabbtn')].map(b=>b.title)")
    check(f"{tag} 0: tooltips show the key", tips == ["Today · 1", "Plan · 2", "Flow · 3", "Watch · 4", "Journal · 5", "Port · 6"], tips)
    js(page, "()=>switchTab('today')"); page.wait_for_timeout(150)
    js(page, "()=>document.getElementById('hdrPlanBtn').click()"); page.wait_for_timeout(300)
    page.keyboard.press("3"); page.wait_for_timeout(200)
    check(f"{tag} 0: key 3 with the New-plan chooser open does not switch tab", js(page, "()=>activeTab") == "today" and js(page, "()=>!!document.getElementById('bdPop')"))
    js(page, "()=>bdPopClose()")
    js(page, "()=>openSettings && openSettings()"); page.wait_for_timeout(300)
    page.keyboard.press("4"); page.wait_for_timeout(200)
    check(f"{tag} 0: key 4 with a sheet open does not switch tab", js(page, "()=>activeTab") == "today")
    page.keyboard.press("Escape"); page.wait_for_timeout(200)


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, ce, pe = launch(pw, w, h)
    try:
        page.wait_for_timeout(300)
        part0(page, tag)
        check(f"{tag} no page errors", not pe, pe)
        check(f"{tag} no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print("SUMMARY lr2: %d checks, %d failing" % (len(results), len(bad)))
    for r in bad: print("FAIL", r[0])
    sys.exit(1 if bad else 0)
