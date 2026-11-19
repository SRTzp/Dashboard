#!/usr/bin/env python3
"""ID1 — shared launcher for the Watch > Ideas detail: 3 ideas (Waiting for evidence / Exploring / Draft), clock Mon 5 Oct 2026."""
import copy
import net_stub
import lib_phase44 as P44
import lib_phase47 as P47
from re1d_common import js, NOANIM

HIDE_NAV = "@media (max-width:600px){#tabsMain{display:none!important}}"


def ideas():
    a = P44.semis(); a.update(id="semis-ai-memory-2026", name="Semis AI memory", status="need_evidence")
    b = copy.deepcopy(a); b.update(id="grid-power", name="Grid power equipment", status="exploring", date="2026-09-20")
    c = copy.deepcopy(a); c.update(id="idea-draft", name="Draft idea", status="draft", mode="draft", date="2026-10-03")
    d = copy.deepcopy(a); d.update(id="ready-idea", name="Ready idea", status="ready", mode="pick", date="2026-11-05", gaps=[])
    e = copy.deepcopy(a); e.update(id="no-cands", name="No companies idea", status="exploring", candidates=[], losers=[])
    return [a, b, c, d, e]


def open_ideas(pw, w, h, sel="semis-ai-memory-2026", tab=None):
    r = P47.launcher(pw, w, h, ideas=ideas())
    b, page = r[0], r[2]
    js(page, "()=>{ localStorage.removeItem('dash.ln1Legacy'); localStorage.removeItem('ln1_plan_view'); }")   # the stub forces the pre-Lean mode; the real app is Lean
    page.add_style_tag(content=NOANIM); page.wait_for_timeout(200)
    P47.go_ideas(page)
    if sel:
        js(page, "(s)=>ideaOpen(s)", sel); page.wait_for_timeout(300)
        if tab: js(page, "(t)=>ideaSetTab(t)", tab); page.wait_for_timeout(250)
    return b, page, r
