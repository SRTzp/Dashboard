#!/usr/bin/env python3
"""HW1d — lenient Fact Sheet import: missing groups -> warning, track from Watch, command chip includes the track.
Run: python3 tests/run_tests_hw1d.py"""
import sys, json, copy
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import hw1_common as H

TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"


def fj(sym, base, fn=None):
    f = copy.deepcopy(base)
    if fn: fn(f)
    return json.dumps({"schema": "living-thesis@1", "sym": sym, "mode": "facts", "date": "2026-11-20", "summary": {"biz": "x"}, "facts": f, "catalysts": []})


def imp(page, sym, text):
    js(page, "([s,t])=>{ ltImportOpen(s); document.getElementById('ltJson').value = t; ltImpCheck(); }", [sym, text]); page.wait_for_timeout(200)
    err = js(page, TXT, "#ltErr") or ""
    toast = None
    if not err:
        js(page, "()=>{ window.__t = null; const o = window.sdToast; window.sdToast = (m)=>{ window.__t = m; try{ o(m); }catch(e){} }; ltImpSave(); }"); page.wait_for_timeout(400)
        toast = js(page, "()=>window.__t")
    return err, toast


def drop(g): return lambda f: f.update(lines=[x for x in f["lines"] if x["g"] != g])


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = H.open_hw(pw, w, h)
    try:
        # 1 · Compounder stock, momentum Fact Sheet missing `expected`
        err, toast = imp(page, "ZZ", fj("ZZ", H.MOM, drop("expected")))
        check(f"{tag} Compounder + momentum sheet missing expected: no error", err == "", err)
        mi = js(page, "()=>(ltFacts(wlItemOf('ZZ')) || {}).missing") or []
        check(f"{tag} missing entry added for expected", "Expected — not in this Fact Sheet" in mi, mi)
        check(f"{tag} stored as given (track momentum)", js(page, "()=>wlItemOf('ZZ').thesis.facts.track") == "momentum")
        check(f"{tag} toast: missing + made-for text", (toast or "").startswith("Fact Sheet updated (Q3 FY26) · missing: ") and "expected" in toast and "· made for momentum, shown as Compounder" in toast, toast)
        H.go(page, "ZZ", "ladder")
        if w < 1024: js(page, "()=>hw1SegSet('ZZ','mine')"); page.wait_for_timeout(150)
        check(f"{tag} page shows the Compounder layout", js(page, "()=>!!document.querySelector('[data-hw1-f=\"evidence\"]') && !document.querySelector('[data-hw1-f=\"trigger\"]')"))
        # 2 · matching track, group missing -> warning only
        err, toast = imp(page, "AAPL", fj("AAPL", H.MOM, drop("expected")))
        check(f"{tag} matching track missing group: imports", err == "" and (toast or "").startswith("Fact Sheet updated (Q3 FY26) · missing: expected") and "made for" not in (toast or ""), (err, toast))
        # 3 · structure still errors
        for nm, fn in (("q cols != 4", lambda f: f["q"].update(cols=["a", "b", "c"])), ("calc without formula", lambda f: f["q"]["rows"][0].pop("formula")),
                       ("line without src", lambda f: f["lines"][0].pop("src")), ("wrong type", lambda f: f.update(biz=5))):
            err, _ = imp(page, "AAPL", fj("AAPL", H.MOM, fn))
            check(f"{tag} structure error blocks: {nm}", err.startswith("Fact Sheet not valid"), err)
        # 4 · over-limit text trimmed
        def longs(f): f["biz"] = "b" * 120; f["lines"][0]["text"] = "t" * 100
        err, toast = imp(page, "AAPL", fj("AAPL", H.MOM, longs))
        f = js(page, "()=>ltFacts(wlItemOf('AAPL'))") or {}
        check(f"{tag} long text trimmed, not rejected", err == "" and len(f.get("biz", "")) == 90 and len(f["lines"][0]["text"]) == 80, err)
        # 5 · command chip per track
        for sym, trk, want in (("WHSE", "ladder", "compounder"), ("SRC1", "winner", "momentum")):
            H.go(page, sym, trk)
            if w < 1024: js(page, "(s)=>hw1SegSet(s,'facts')", sym); page.wait_for_timeout(150)
            c = js(page, "()=>document.querySelector('[data-hw1-copycmd]').dataset.cmd")
            check(f"{tag} chip for {sym}: living-thesis facts {sym} {want}", c == f"living-thesis facts {sym} {want}", c)
        H.go(page, "COST", "ladder")
        check(f"{tag} Copy for AI header has the track", js(page, "()=>hw1CopyText(wlItemOf('COST')).split('\\n')[0]") == "living-thesis challenge · COST · compounder")
        check(f"{tag} no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY HW1d: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
