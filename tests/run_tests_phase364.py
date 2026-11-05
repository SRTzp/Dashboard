#!/usr/bin/env python3
"""PL2b item 9 — "เลือกศึกษา" (Value Chain pick): ticked-first display order · user choice kept separate from the AI pick · export = user choice only · เทส 364
Chromium · 390 + 1440 · รัน: python3 run_tests_phase364.py"""
import copy, json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase44 as P44
import run_tests_phase59 as P59

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def make_idea():
    d = P59.idea([P59.cand("CAA", "A", 1, "study")], iid="i1")
    segs = d["chain"]["segments"]
    segs[2]["pick"] = True     # AI pick (user has not chosen)
    segs[4]["pick"] = True
    return d


ORDER = "()=>[...document.querySelectorAll('.ideaVc [data-idea-seg]')].map(b=>+b.dataset.ideaSeg)"
TICKED = "()=>[...document.querySelectorAll('.ideaVc [data-idea-pick]')].filter(c=>c.checked).map(c=>+c.dataset.ideaPick)"
VISIBLE = """(i)=>{ const row = document.querySelector('.ideaVc'), b = row.querySelector('[data-idea-seg="'+i+'"]'); const r = row.getBoundingClientRect(), q = b.getBoundingClientRect(); return {vis: q.left >= r.left - 1 && q.right <= r.right + 1, left: Math.round(q.left - r.left), sl: row.scrollLeft, rw: Math.round(r.width), bw: Math.round(q.width)}; }"""


def open_vc(page):
    js(page, "()=>{ switchTab('watch'); wlSetView('idea'); ideaSel='i1'; wlMobOpen=true; ideaSubSave('i1','vc'); renderWatchlist(); }"); page.wait_for_timeout(600)


def tests(pw, w, h):
    tg = f"[{ENGINE}/{w}]"
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, ideas=[make_idea()])
    try:
        open_vc(page)
        src_order = js(page, "()=>ideaList.find(d=>d.id==='i1').idea.chain.segments.map(s=>s.name)")
        o0 = js(page, ORDER)
        check(f"{tg} initial: original order 0..5; nothing ticked even though the AI set pick:true on #2 and #4", o0 == [0, 1, 2, 3, 4, 5] and js(page, TICKED) == [], [o0, js(page, TICKED)])
        chips = js(page, "()=>[...document.querySelectorAll('[data-idea-aipick]')].map(e=>+e.closest('[data-idea-seg]').dataset.ideaSeg)")
        sug = js(page, "()=>[...document.querySelectorAll('[data-idea-suggest]')].map(e=>+e.closest('[data-idea-seg]').dataset.ideaSeg)")
        check(f"{tg} the AI values show as separate chips: 'AI pick' on #2 and #4 · 'AI เสนอ' (suggest) unchanged on #0 and #3", chips == [2, 4] and sug == [0, 3], [chips, sug])
        st = js(page, "()=>plAiPickStats()")
        check(f"{tg} stats helper: 6 segments · 2 with AI pick:true · 2 without a user choice", st == {"segments": 6, "aiPickTrue": 2, "aiPickTrueNoUserChoice": 2}, st)
        # tick #4 (5th card, off-screen on a phone)
        y0 = js(page, "()=>{ window.scrollTo(0, 120); return window.scrollY; }"); page.wait_for_timeout(150)
        page.locator('[data-idea-pick="4"]').scroll_into_view_if_needed(); y1 = js(page, "()=>window.scrollY")
        page.locator('[data-idea-pick="4"]').check(); page.wait_for_timeout(400)
        o1 = js(page, ORDER); vis = js(page, VISIBLE, 4); y2 = js(page, "()=>window.scrollY")
        check(f"{tg} tick #4 → its card moves to the left group (first)", o1 == [4, 0, 1, 2, 3, 5] and js(page, TICKED) == [4], o1)
        check(f"{tg} tick #4 → the card is visible in the row (row scrolled horizontally)", vis["vis"], vis)
        check(f"{tg} tick #4 → the PAGE did not move vertically (scrollY {y1} → {y2})", y1 == y2, [y1, y2])
        page.locator('[data-idea-pick="2"]').check(); page.wait_for_timeout(400)
        o2 = js(page, ORDER)
        check(f"{tg} tick #2 too → ticked group keeps original relative order (2, 4) then the unticked ones (0, 1, 3, 5)", o2 == [2, 4, 0, 1, 3, 5], o2)
        page.locator('[data-idea-pick="4"]').uncheck(); page.wait_for_timeout(400)
        o3 = js(page, ORDER)
        check(f"{tg} untick #4 → back to its original relative place among the unticked (2, then 0, 1, 3, 4, 5)", o3 == [2, 0, 1, 3, 4, 5], o3)
        # storage separation
        u = (P59.doc_of(page, "ideas", "i1") or {}).get("user", {}).get("pick", {})
        idea_doc = (P59.doc_of(page, "ideas", "i1") or {}).get("idea", {})
        names = src_order
        check(f"{tg} user.pick holds only the user's choices (#2 true · #4 false) — untouched AI picks not copied", u == {names[2]: True, names[4]: False}, u)
        check(f"{tg} the AI's own segments[].pick is never overwritten (still true on #2 and #4) and the stored segment order is unchanged", [s["name"] for s in idea_doc["chain"]["segments"]] == names and [bool(s.get("pick")) for s in idea_doc["chain"]["segments"]] == [False, False, True, False, True, False], idea_doc.get("chain", {}).get("segments", [])[:1])
        # export
        ex = js(page, "()=>{ const o = ideaExportObj(ideaList.find(x=>x.id==='i1')); return o.chain.segments.map(s=>[s.name, s.pick]); }")
        check(f"{tg} export: segment ORDER unchanged and pick = user choice only (#2 true; AI-ticked #4 → false; untouched AI picks not exported as true)", [x[0] for x in ex] == names and [x[1] for x in ex] == [False, False, True, False, False, False], ex)
        # reload → order rebuilt from user.pick
        P44.reload_keep(page); open_vc(page)
        o4 = js(page, ORDER)
        check(f"{tg} reload → order rebuilt from the saved user.pick (2 first) and the box is still ticked", o4 == [2, 0, 1, 3, 4, 5] and js(page, TICKED) == [2], [o4, js(page, TICKED)])
        check(f"{tg} no console errors · no horizontal page overflow", not [e for e in ce if "Failed to load" not in e] and not pe and C.overflow(page) <= 0, [ce[:2], pe[:2], C.overflow(page)])
        C.shot(page, f"pl2b-value-chain-{w}.png")
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)): tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
