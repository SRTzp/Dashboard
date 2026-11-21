#!/usr/bin/env python3
"""LT2 — Fact Sheet (`facts`) in living-thesis@1: import + validate (never blocks the import) · store · ltFacts / ltTrend · Full-thesis muted line · Export JSON round-trip · no-facts thesis unchanged.
Run: python3 tests/run_tests_lt2.py"""
import sys, os, json, copy
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import lr5_common as C

H = os.path.dirname(os.path.abspath(__file__))
fx = lambda n: json.load(open(os.path.join(H, "fixtures", "lt2", n + ".json")))
BASE = json.load(open(os.path.join(H, "fixtures", "avgo_thesis_v3.json")))
PARSE = "(t)=>{ const r = ltParse(t, null); return {err:r.err||null, warn:r.warn||'', facts:r.th ? (r.th.facts||null) : undefined, sym:r.th&&r.th.sym, summ:r.th&&r.th.summary&&r.th.summary.status, nlog:r.log&&r.log.length}; }"


def mut(d, fn):
    d = copy.deepcopy(d); fn(d["facts"]); return d


def parse(page, d):
    return js(page, PARSE, json.dumps(d))


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = C.open_watch(pw, w, h, ideas=False)
    try:
        comp, mom = fx("compounder"), fx("momentum")
        # ---- valid imports, both tracks
        for nm, d in (("compounder", comp), ("momentum", mom)):
            r = parse(page, d)
            check(f"{tag} valid {nm}: imported with facts, no warning", r["err"] is None and r["warn"] == "" and r["facts"] == d["facts"], r)
        # ---- no facts → unchanged
        nf = parse(page, BASE)
        check(f"{tag} thesis without facts: imported as before (no facts key, no warning)", nf["err"] is None and nf["warn"] == "" and nf["facts"] is None, nf)
        # ---- each validation failure → rest imported + one warning, facts dropped
        bad = {
            "track enum": (comp, lambda f: f.update(track="swing")),
            "mix > 4": (comp, lambda f: f["mix"].append({"seg": "Other", "pct": 1})),
            "cols != 4": (comp, lambda f: f["q"].update(cols=["a", "b", "c"])),
            "row v != 4": (comp, lambda f: f["q"]["rows"][0].update(v=[1, 2, 3])),
            "row v not number": (comp, lambda f: f["q"]["rows"][0].update(v=[1, "x", 3, 4])),
            "calc row without formula": (comp, lambda f: f["q"]["rows"][0].pop("formula")),
            "calc line without formula": (comp, lambda f: f["lines"][1].pop("formula")),
            "line without src": (comp, lambda f: f["lines"][2].pop("src")),
            "kind enum": (comp, lambda f: f["lines"][2].update(kind="guess")),
            "group enum": (comp, lambda f: f["lines"][2].update(g="opinion")),
            "web without date": (comp, lambda f: f["lines"][3].pop("date")),
            "lines > 10": (comp, lambda f: f.update(lines=f["lines"] * 3)),
            "more > 14": (comp, lambda f: f.update(more=f["more"] * 15)),
            "mgmt > 2": (comp, lambda f: f.update(mgmt=f["mgmt"] * 3)),
            "missing > 3": (comp, lambda f: f.update(missing=["a", "b", "c", "d"])),
            "unknown row key": (comp, lambda f: f["q"]["rows"][0].update(k="foo")),
            "facts not an object": (comp, lambda f: None),
        }
        for nm, (base, fn) in bad.items():
            d = mut(base, fn)
            if nm == "facts not an object": d["facts"] = "oops"
            r = parse(page, d)
            ok = r["err"] is None and r["facts"] is None and r["warn"].startswith("Fact Sheet not imported — ") and r["sym"] == d["sym"] and r["summ"] == d["summary"]["status"]
            check(f"{tag} invalid ({nm}): rest imported, facts dropped, warning names the problem", ok, r)
        r = parse(page, mut(comp, lambda f: f.update(biz=91)))
        check(f"{tag} warning is ONE line naming the first problem", "\n" not in r["warn"] and "biz" in r["warn"], r["warn"])
        # HW1d — over-limit text is trimmed; a missing required group imports with a "missing" entry (no warning)
        r = parse(page, mut(comp, lambda f: f.update(biz="x" * 91)))
        check(f"{tag} biz > 90 is trimmed to 90, not an error", r["err"] is None and r["warn"] == "" and r["facts"] and len(r["facts"]["biz"]) == 90, r["warn"])
        r = parse(page, mut(mom, lambda f: f.update(lines=[x for x in f["lines"] if x["g"] != "lastq"])))
        check(f"{tag} momentum without lastq: imports, missing entry added", r["err"] is None and r["warn"] == "" and r["facts"] and any("Lastq" in m for m in r["facts"]["missing"]), r["warn"])
        # ---- ltTrend
        T = lambda k, v: js(page, "([k,v])=>ltTrend({k:k,v:v})", [k, v])
        cases = [("rev_yoy", [7, 8, 10, 13], "accel"), ("rev_yoy", [20, 18, 15, 11], "slow"), ("op_margin", [3.1, 3.3, 3.5, 3.7], "rising"), ("op_margin", [4, 3.9, 3.7, 3.4], "falling"),
                 ("kpi_renewal", [93, 92.9, 92.8, 92.7], "falling"), ("kpi_renewal", [91, 92, 93, 94], "rising"), ("rev_yoy", [7, 8, 8, 8], "steady"), ("rev_yoy", [9, 12, 10, 11], "steady"),
                 ("rev_yoy", [7, 8, 10, None], "steady"), ("rev_yoy", [None, 8, 9, 11], "accel"), ("eps_yoy", [None, None, 5, 9], "steady"), ("gm", [1, 2, None, 4], "steady"), ("rev_yoy", [], "steady")]
        for k, v, exp in cases:
            check(f"{tag} ltTrend {k} {v} -> {exp}", T(k, v) == exp, T(k, v))
        check(f"{tag} ltTrend(null / no v) -> steady", js(page, "()=>[ltTrend(null), ltTrend({}), ltTrend({k:'gm',v:'x'})]") == ["steady"] * 3)
        # ---- store via the real Import sheet (AVGO exists in the watchlist) + Full thesis line + export round trip
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); renderWatchlist(); }"); page.wait_for_timeout(300)
        old = js(page, "()=>{ const t = wlItemOf('AVGO').thesis; return {hasFacts: 'facts' in t, ltFacts: ltFacts(wlItemOf('AVGO'))}; }")
        check(f"{tag} before import: AVGO has no facts → ltFacts null, no Fact Sheet line", old == {"hasFacts": False, "ltFacts": None}, old)
        js(page, "()=>{ wlOpen('AVGO'); wl5Full('AVGO','sum'); }"); page.wait_for_timeout(300)
        check(f"{tag} no facts → no muted line", js(page, "()=>!document.querySelector('[data-lt-facts-line]')"))

        def do_import(d):
            js(page, "(t)=>{ ltImportOpen('AVGO'); document.getElementById('ltJson').value = t; ltImpCheck(); }", json.dumps(d)); page.wait_for_timeout(200)
            prev = js(page, "()=>document.getElementById('ltPrev') ? document.getElementById('ltPrev').innerText : ''")
            js(page, "()=>ltImpSave()"); page.wait_for_timeout(500)
            return prev
        prev = do_import(mom)
        check(f"{tag} preview shows Fact Sheet line, no warning", "Fact Sheet: momentum · Q3 FY26" in prev and "not imported" not in prev, prev)
        st = js(page, "()=>{ const it = wlItemOf('AVGO'); return {facts: it.thesis.facts, f: ltFacts(it), status: it.thesis.summary.status}; }")
        check(f"{tag} store: facts saved in the thesis doc, ltFacts returns it", st["facts"] == mom["facts"] and st["f"] == mom["facts"], st)
        js(page, "()=>{ wlOpen('AVGO'); wl5Full('AVGO','sum'); }"); page.wait_for_timeout(300)
        ln = js(page, "()=>{ const e = document.querySelector('[data-lt-facts-line]'); return e ? e.innerText.trim() : null }")
        check(f"{tag} Full thesis: muted line 'Fact Sheet · Q3 FY26 · 18 Nov'", ln == "Fact Sheet · Q3 FY26 · 18 Nov", ln)
        # export round trip
        js(page, "()=>{ window.__clip = ''; Object.defineProperty(navigator, 'clipboard', {value:{writeText:t=>{ window.__clip = t; return Promise.resolve(); }}, configurable:true}); ltExport('AVGO'); }"); page.wait_for_timeout(300)
        clip = js(page, "()=>window.__clip")
        ex = json.loads(clip) if clip else {}
        check(f"{tag} Export JSON includes facts (identical to imported)", ex.get("facts") == mom["facts"], list(ex.keys()))
        rt = parse(page, ex)
        check(f"{tag} export → import round trip: facts valid and identical", rt["err"] is None and rt["warn"] == "" and rt["facts"] == mom["facts"], rt)
        # update mode replaces facts whole
        comp2 = copy.deepcopy(mom); comp2["facts"] = copy.deepcopy(fx("compounder")["facts"])
        do_import(comp2)
        st = js(page, "()=>wlItemOf('AVGO').thesis.facts")
        check(f"{tag} update replaces facts whole (momentum → compounder, nothing left over)", st == comp2["facts"] and st["track"] == "compounder", st and st.get("track"))
        # invalid facts on import: rest stored, old facts replaced by nothing, warning in the preview
        badd = mut(mom, lambda f: f["lines"][0].pop("src"))
        prev = do_import(badd)
        st = js(page, "()=>{ const t = wlItemOf('AVGO').thesis; return {has:'facts' in t, status:t.summary.status, date:t.date}; }")
        check(f"{tag} invalid facts: preview warns, thesis stored without facts", "Fact Sheet not imported" in prev and st["has"] is False and st["date"] == badd["date"], [prev, st])
        # thesis without facts afterwards: log behaviour unchanged
        nlog = js(page, "()=>wlItemOf('AVGO').thesis_log.length")
        check(f"{tag} log merged as before", nlog >= len(BASE.get("log", [])), nlog)
        check(f"{tag} no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY LT2: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
