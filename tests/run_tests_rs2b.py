#!/usr/bin/env python3
"""RS2b — Screen › Industries: Stocks | Industries toggle (+ memory, Reset) · rows per preset · Matches / Breadth / Group RS values · header sorts + tie-break · 1-match fold · ≥ 5 rule · Unknown
· Top 5 (best first, one line, ellipsis at 1280) · row click / Stocks › → Stocks + chip (× clears) · Filter ▾ Industry · coverage line · ↑/↓/Enter/←/→ · no tick / download in Industries · no detail panel
· phone 2-line rows · 360/390/1280/1440 no overflow.   Run: python3 tests/run_tests_rs2b.py"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from playwright.sync_api import sync_playwright
import build_rs2 as J
import rs2a_common as C
from re1d_common import js, check, results

PRESETS = {"leaders": lambda r: r["r"] >= 80 and r["o"] >= -0.15,
           "emerging": lambda r: r["m3"] >= 90 and r["m1"] >= 90 and r["r"] < 85 and True,
           "pullback": lambda r: r["r"] >= 85 and r["m3"] >= 80 and r["m1"] < 60 and r["o"] >= -0.15}


def mk(t, ind, sec, r, o=-0.05, m3=None, m1=None):
    return C.row(t, t + " Inc", sec, ind, "NASDAQ", r, r - 3, "u", 0, o, 50.0, 80e6, m3=m3, m1=m1)


def build(unknown=8):
    R = []
    far = dict(o=-0.4)
    # Semiconductors: 12 liquid · Leaders 7 (long tickers so the Top 5 line is cut at 1280)
    for t, r in zip(["NVDAXX", "CREDOXX", "ALABXXX", "AVGOXXX", "MRVLXXX", "MUXXXXX", "TSMXXXX"], [99, 97, 95, 93, 92, 91, 90]):
        R.append(mk(t, "Semiconductors", "Technology", r, m3=95, m1=40 if t in ("NVDAXX", "CREDOXX", "ALABXXX") else 95))
    for k in range(5):
        R.append(mk("SEMI%d" % k, "Semiconductors", "Technology", 50 + k, m3=50, m1=50, **far))
    # Software - Infrastructure 10 · Leaders 5
    for k, r in enumerate([97, 90, 88, 86, 84]):
        R.append(mk("PLTRX%d" % k, "Software - Infrastructure", "Technology", r, m3=82, m1=45 if k < 2 else 85))
    for k in range(5):
        R.append(mk("SOFT%d" % k, "Software - Infrastructure", "Technology", 40 + k, m3=50, m1=50, **far))
    # Aerospace & Defense 6 · Leaders 4
    for k, r in enumerate([91, 90, 89, 85]):
        R.append(mk("GEAX%d" % k, "Aerospace & Defense", "Industrials", r, m3=70, m1=70))
    for k in range(2):
        R.append(mk("AERO%d" % k, "Aerospace & Defense", "Industrials", 55 + k, m3=50, m1=50, **far))
    # Capital Markets 8 · Leaders 2  (same count as nothing else → plain)
    for k, r in enumerate([94, 81]):
        R.append(mk("HOODX%d" % k, "Capital Markets", "Financial Services", r, m3=70, m1=70))
    for k in range(6):
        R.append(mk("CAPM%d" % k, "Capital Markets", "Financial Services", 30 + k, m3=50, m1=50, **far))
    # Utilities - Independent Power 5 · 1 match · Banks - Regional 9 · 1 match   (→ folded)
    R.append(mk("VSTX", "Utilities - Independent Power", "Utilities", 96, m3=70, m1=70))
    for k in range(4):
        R.append(mk("UTIL%d" % k, "Utilities - Independent Power", "Utilities", 45 + k, m3=50, m1=50, **far))
    R.append(mk("BANKA", "Banks - Regional", "Financial Services", 83, m3=70, m1=70))
    for k in range(8):
        R.append(mk("BANK%d" % k, "Banks - Regional", "Financial Services", 35 + k, m3=50, m1=50, **far))
    # Tiny Industry: 4 liquid, all match → < 5, never a row
    for k in range(4):
        R.append(mk("TINY%d" % k, "Tiny Industry", "Technology", 99 - k, m3=70, m1=70))
    # Unknown industry: matches, never a row
    for k in range(unknown):
        R.append(mk("UNK%d" % k, "", "Technology", 92 - k, m3=70, m1=70))
    return R


def expect(R, preset):
    """independent of the app: per industry (≥ 5 liquid) → matches / n / avg / rank (equal averages share a rank)"""
    by = {}
    for r in R:
        if r["i"]: by.setdefault(r["i"], []).append(r)
    G = {i: round(sum(x["r"] for x in L) / len(L), 1) for i, L in by.items() if len(L) >= 5}
    order = sorted(G, key=lambda i: (-G[i], -len(by[i]), i))
    rank = {}
    for k, i in enumerate(order):
        rank[i] = rank[order[k - 1]] if k and G[order[k - 1]] == G[i] else k + 1
    out = []
    for i in G:
        m = sorted([x for x in by[i] if PRESETS[preset](x)], key=lambda x: -x["r"])
        if m: out.append({"ind": i, "m": len(m), "n": len(by[i]), "avg": G[i], "rank": rank[i], "top": [x["t"] for x in m[:5]], "pct": round(100.0 * len(m) / len(by[i]))})
    out.sort(key=lambda e: (-e["m"], e["rank"], e["ind"]))
    return out


def meta_for(R, **kw):
    rows = [dict(r) for r in R]
    gs = J.group_stats(rows)
    n_, c_ = J.ind_coverage(rows)
    m = C.meta(); m.update({"groups": gs, "indN": n_, "indCov": c_}); m.update(kw)
    return m


def opened(pw, w, h, R, view="ind", preset=None):
    b, page, pe, ce = C.open_screen(pw, w, h, data=R, meta_=meta_for(R), wl=C.WL)
    if preset: js(page, "(p)=>rs2Set('preset', p)", preset)
    if view == "ind": page.click("[data-rs2-view=ind]")
    page.wait_for_timeout(400)
    return b, page, pe, ce


ROWS = """()=>[...document.querySelectorAll('[data-rs2-ind-row]')].map(r=>({ind:r.dataset.ind, m:r.querySelector('[data-rs2-ind-m]').innerText.replace(/\\s+/g,' ').trim(),
  b:r.querySelector('[data-rs2-ind-b]').innerText.trim(), g:r.querySelector('[data-rs2-ind-g]').innerText.replace(/\\s+/g,' ').trim(),
  top:[...r.querySelectorAll('.tn')].map(x=>x.innerText.replace(/\\s+/g,' ').trim()), h:Math.round(r.getBoundingClientRect().height), on:r.classList.contains('on'),
  sec:(r.querySelector('.c-sec')||{}).innerText||''}))"""
SRC = "()=>[...document.querySelectorAll('[data-rs2-row]')].map(r=>r.dataset.sym)"
SUM = "()=>{ const e = document.querySelector('[data-rs2-sum] .lg'); return e ? e.innerText.replace(/\\s+/g,' ') : '' }"
FOLD = "()=>{ const e = document.querySelector('[data-rs2-fold]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null }"
CHIP = "()=>{ const e = document.querySelector('[data-rs2-indchip]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null }"
STATE = "()=>({view:rs2.view, ind:rs2.ind, preset:rs2.preset, ls:JSON.parse(localStorage.getItem('dash.rs2b')||'{}')})"


def over(page):
    return js(page, "()=>({sw:document.documentElement.scrollWidth - innerWidth, bad:[...document.querySelectorAll('.lr5-screen *')].filter(e=>{const r=e.getBoundingClientRect(); return r.width>0 && r.right > innerWidth + 1 && !e.closest('.lr5-list') && !e.closest('.rs2-fl')}).length})")


def desk(pw, w, h):
    tag = "[%s]" % w
    R = build()
    b, page, pe, ce = opened(pw, w, h, R, view="stocks")
    try:
        # ---- 1 toggle + memory + Reset
        pos = js(page, "()=>{ const s = document.querySelector('[data-rs2-presets]'), v = document.querySelector('[data-rs2-views]'); return {after:!!(s.compareDocumentPosition(v) & Node.DOCUMENT_POSITION_FOLLOWING), same:s.parentElement === v.parentElement, labels:[...v.querySelectorAll('button')].map(x=>x.innerText), on:v.querySelector('.on').innerText} }")
        check(f"{tag} 1 Stocks | Industries toggle sits in the preset row, after the preset segments · Stocks is the default", pos["after"] and pos["same"] and pos["labels"] == ["Stocks", "Industries"] and pos["on"] == "Stocks", pos)
        check(f"{tag} 1 Stocks view unchanged: rows + detail panel", len(js(page, SRC)) > 0 and js(page, "()=>!!document.querySelector('[data-rs2-det]')") and not js(page, "()=>!!document.querySelector('[data-rs2-ind-row]')"))
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(300)
        st = js(page, STATE)
        check(f"{tag} 1 Industries view on · remembered (dash.rs2b.view)", st["view"] == "ind" and st["ls"].get("view") == "ind" and len(js(page, ROWS)) > 0, st)
        js(page, "()=>{ wlSetView('wl'); wlSetView('screen'); }"); page.wait_for_timeout(500)
        check(f"{tag} 1 …and kept when leaving Screen and coming back", js(page, "()=>rs2.view") == "ind" and len(js(page, ROWS)) > 0)
        page.click("[data-rs2-reset]"); page.wait_for_timeout(300)
        st = js(page, STATE)
        check(f"{tag} 1 Reset → Stocks (and forgets it)", st["view"] == "stocks" and st["ls"].get("view") == "stocks" and len(js(page, SRC)) > 0, st)

        # ---- 2/3 rows per preset + values
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(300)
        for p in ("leaders", "emerging", "pullback"):
            page.click(f"[data-rs2-preset={p}]"); page.wait_for_timeout(300)
            E = expect(R, p)
            got = js(page, ROWS)
            fold_n = sum(1 for e in E if e["m"] == 1)
            main = [e for e in E if e["m"] != 1]
            if fold_n and main:
                page.click("[data-rs2-fold]"); page.wait_for_timeout(250); got = js(page, ROWS)
            ok = [g["ind"] for g in got] == [e["ind"] for e in E]
            check(f"{tag} 2 {p}: one row per industry with ≥ 5 liquid stocks and ≥ 1 match ({len(E)} expected)", ok, [[g["ind"] for g in got], [e["ind"] for e in E]])
            bad = [(g["ind"], g["m"], e["m"], e["n"]) for g, e in zip(got, E) if g["m"] != "%d of %d" % (e["m"], e["n"])]
            check(f"{tag} 3 {p}: Matches column = 'k of n' for every row", not bad, bad)
            bad = [(g["ind"], g["b"], e["pct"]) for g, e in zip(got, E) if g["b"] != "%d%%" % e["pct"]]
            check(f"{tag} 3 {p}: Breadth % = matches ÷ liquid stocks in the industry", not bad, bad)
            bad = [(g["ind"], g["g"], e["avg"], e["rank"]) for g, e in zip(got, E) if g["g"] != "%d #%d" % (round(e["avg"]), e["rank"])]
            check(f"{tag} 3 {p}: Group RS = '88 #3' (average 12M of ALL liquid stocks in the industry, rank)", not bad, bad)
            if fold_n and main:
                page.click("[data-rs2-fold]"); page.wait_for_timeout(200)
        page.click("[data-rs2-preset=leaders]"); page.wait_for_timeout(300)
        E = expect(R, "leaders")
        check(f"{tag} 3 leaders: expected numbers (Semis 7 of 12 · Software 5 of 10 · A&D 4 of 6 · Capital Markets 2 of 8 · folded: Utilities, Banks)", [(e["ind"], e["m"], e["n"]) for e in E][:4] == [("Semiconductors", 7, 12), ("Software - Infrastructure", 5, 10), ("Aerospace & Defense", 4, 6), ("Capital Markets", 2, 8)] and sorted(e["ind"] for e in E if e["m"] == 1) == ["Banks - Regional", "Utilities - Independent Power"], [(e["ind"], e["m"], e["n"]) for e in E])

        # ---- 4 default sort + header sorts
        got = js(page, ROWS)
        check(f"{tag} 4 default sort = Matches ▼ (desc) · header shows ▼", [g["ind"] for g in got] == [e["ind"] for e in E if e["m"] != 1] and js(page, "()=>document.querySelector('[data-rs2-ith=m]').dataset.rs2Dir") == "desc", [g["ind"] for g in got])
        page.click("[data-rs2-ith=b]"); page.wait_for_timeout(250)
        exp = sorted([e for e in E if e["m"] != 1], key=lambda e: (-e["m"] / float(e["n"]), -e["m"], e["rank"]))
        check(f"{tag} 4 Breadth header sorts by breadth ▼ (matches ÷ liquid)", [g["ind"] for g in js(page, ROWS)] == [e["ind"] for e in exp], [g["ind"] for g in js(page, ROWS)])
        page.click("[data-rs2-ith=b]"); page.wait_for_timeout(250)
        check(f"{tag} 4 second click flips (▲)", [g["ind"] for g in js(page, ROWS)] == [e["ind"] for e in reversed(exp)] and js(page, "()=>document.querySelector('[data-rs2-ith=b]').dataset.rs2Dir") == "asc", [g["ind"] for g in js(page, ROWS)])
        page.click("[data-rs2-ith=g]"); page.wait_for_timeout(250)
        exp = sorted([e for e in E if e["m"] != 1], key=lambda e: (e["rank"], e["ind"]))
        check(f"{tag} 4 Group RS header sorts strongest group first (rank 1 …)", [g["ind"] for g in js(page, ROWS)] == [e["ind"] for e in exp], [g["ind"] for g in js(page, ROWS)])
        check(f"{tag} 4 sort choice remembered", js(page, STATE)["ls"].get("isort") == "g")
        page.click("[data-rs2-ith=m]"); page.wait_for_timeout(250)
        check(f"{tag} 4 back to Matches ▼", [g["ind"] for g in js(page, ROWS)] == [e["ind"] for e in E if e["m"] != 1])

        # ---- 5 fold + header line
        n_m = sum(e["m"] for e in E)
        check(f"{tag} 5 header line '{n_m} match in {len(E)} industries'", f"{n_m} match in {len(E)} industries" in js(page, SUM), js(page, SUM))
        check(f"{tag} 5 exactly-1-match industries folded under '+ 2 industries with 1 match'", js(page, FOLD) == "+ 2 industries with 1 match" and len(js(page, ROWS)) == 4, [js(page, FOLD), len(js(page, ROWS))])
        page.click("[data-rs2-fold]"); page.wait_for_timeout(250)
        names = [g["ind"] for g in js(page, ROWS)]
        check(f"{tag} 5 click expands them (sorted in) · link turns into Hide", len(names) == 6 and "Banks - Regional" in names and js(page, FOLD).startswith("Hide 2 industries"), [names, js(page, FOLD)])
        page.click("[data-rs2-fold]"); page.wait_for_timeout(200)

        # ---- 6 ≥ 5 rule + Unknown
        allnames = set(g["ind"] for g in js(page, ROWS)) | {"Banks - Regional", "Utilities - Independent Power"}
        check(f"{tag} 6 an industry with 4 liquid stocks is never a row (even with 4 matches) · Unknown is never a row", "Tiny Industry" not in allnames and "Unknown" not in allnames and "" not in allnames, sorted(allnames))
        page.click("[data-rs2-view=stocks]"); page.wait_for_timeout(250)
        page.fill("[data-rs2-q]", "TINY"); page.wait_for_timeout(250)
        check(f"{tag} 6 …but its stocks are still in the Stocks list", len(js(page, SRC)) == 4, js(page, SRC))
        page.fill("[data-rs2-q]", ""); page.wait_for_timeout(250)
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(250)

        # ---- 7 Top 5
        got = js(page, ROWS)
        semi = got[0]
        check(f"{tag} 7 Top 5 = ticker + RS, best first, at most 5", semi["top"] == ["NVDAXX 99", "CREDOXX 97", "ALABXXX 95", "AVGOXXX 93", "MRVLXXX 92"], semi["top"])
        check(f"{tag} 7 one line per row on desktop (≤ 46px)", all(g["h"] <= 46 for g in got), [g["h"] for g in got])
        cut = js(page, "()=>{ const c = document.querySelector('[data-rs2-ind-row] [data-rs2-ind-top]'), s = getComputedStyle(c); return {ov:c.scrollWidth > c.clientWidth, ws:s.whiteSpace, to:s.textOverflow, o:s.overflow, w:Math.round(c.clientWidth)} }")
        check(f"{tag} 7 ellipsis style: nowrap + overflow hidden + text-overflow ellipsis", cut["ws"] == "nowrap" and cut["to"] == "ellipsis" and cut["o"] == "hidden", cut)
        if w <= 1280:
            check(f"{tag} 7 at {w}px the Top 5 of the biggest row is cut with … (scrollWidth > width)", cut["ov"], cut)
        # ---- 13 no detail, full width, no tick / dl
        lay = js(page, "()=>{ const l = document.querySelector('.lr5-list'), m = document.querySelector('.lr5m'); return {det:!!document.querySelector('.wlDet, [data-rs2-det]'), lw:Math.round(l.getBoundingClientRect().width), mw:Math.round(m.getBoundingClientRect().width)} }")
        check(f"{tag} 13 no detail panel · the table uses the full width", not lay["det"] and lay["lw"] >= lay["mw"] - 4, lay)
        check(f"{tag} 12 no tick column, no select-all, no selection bar, no download link in Industries", js(page, "()=>!document.querySelector('[data-rs2-tick], [data-rs2-tick-all], [data-rs2-selbar], [data-rs2-dl], [data-rs2-dl-shown], [data-rs2-add], [data-rs2-dots]')"))
        o = over(page)
        check(f"{tag} 15 Industries: no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)

        # ---- 12 ticked rows vanish when switching view
        page.click("[data-rs2-view=stocks]"); page.wait_for_timeout(300)
        page.click("[data-rs2-tick=NVDAXX]"); page.wait_for_timeout(200)
        check(f"{tag} 12 Stocks: ticking still works (selection bar)", js(page, "()=>!!document.querySelector('[data-rs2-selbar]')"))
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(300)
        check(f"{tag} 12 → Industries: bar gone, selection cleared", js(page, "()=>!document.querySelector('[data-rs2-selbar]') && Object.keys(rs2.tick).length === 0"))
        js(page, "()=>{ document.body.focus(); }")
        page.keyboard.press("Space"); page.wait_for_timeout(200)
        check(f"{tag} 12 Space does not tick in Industries", js(page, "()=>Object.keys(rs2.tick).length === 0"))

        # ---- 8 Stocks › and row click, chip, ×
        page.click("[data-rs2-ind-row][data-ind=Semiconductors] [data-rs2-ind-go]"); page.wait_for_timeout(400)
        syms = js(page, SRC)
        check(f"{tag} 8 'Stocks ›' → Stocks view filtered to the industry, chip 'Industry: Semiconductors ×'", js(page, "()=>rs2.view") == "stocks" and js(page, CHIP) == "Industry: Semiconductors ×" and len(syms) == 7 and all(s in ("NVDAXX", "CREDOXX", "ALABXXX", "AVGOXXX", "MRVLXXX", "MUXXXXX", "TSMXXXX") for s in syms), [js(page, CHIP), syms])
        check(f"{tag} 8 chip is neutral (no port colours) and the preset stays", js(page, "()=>{ const c = document.querySelector('[data-rs2-indchip]'); return getComputedStyle(c).backgroundColor }") == "rgb(238, 240, 243)" and js(page, "()=>rs2.preset") == "leaders")
        page.click("[data-rs2-indchip-x]"); page.wait_for_timeout(300)
        check(f"{tag} 8 × clears the chip and the filter", js(page, CHIP) is None and js(page, "()=>rs2.ind") == "" and len(js(page, SRC)) > 7)
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(300)
        page.click("[data-rs2-ind-row][data-ind='Aerospace & Defense']"); page.wait_for_timeout(400)
        check(f"{tag} 8 a click anywhere on the row does the same", js(page, CHIP) == "Industry: Aerospace & Defense ×" and len(js(page, SRC)) == 4 and js(page, "()=>rs2.view") == "stocks", [js(page, CHIP), js(page, SRC)])
        check(f"{tag} 8 Filter shows the count (Industry set → Filter · 1)", "Filter · 1" in js(page, "()=>document.querySelector('[data-rs2-filter-btn]').innerText"))
        page.click("[data-rs2-reset]"); page.wait_for_timeout(300)
        check(f"{tag} 8 Reset also clears the industry chip", js(page, CHIP) is None and js(page, "()=>rs2.ind") == "")

        # ---- 9 Filter ▾ Industry
        page.click("[data-rs2-filter-btn]"); page.wait_for_timeout(250)
        opts = js(page, "()=>[...document.querySelectorAll('[data-rs2-f=ind] option')].map(o=>o.value)")
        check(f"{tag} 9 Filter ▾ has an Industry select (all industries · every industry · Unknown)", opts[0] == "" and "Semiconductors" in opts and "Tiny Industry" in opts and opts[-1] == "Unknown", opts)
        page.select_option("[data-rs2-f=ind]", "Capital Markets"); page.wait_for_timeout(300)
        check(f"{tag} 9 setting it there shows the same chip + filters Stocks", js(page, CHIP) == "Industry: Capital Markets ×" and sorted(js(page, SRC)) == ["HOODX0", "HOODX1"], [js(page, CHIP), js(page, SRC)])
        page.select_option("[data-rs2-f=ind]", "Unknown"); page.wait_for_timeout(300)
        check(f"{tag} 9 Unknown = stocks without an industry", js(page, CHIP) == "Industry: Unknown ×" and len(js(page, SRC)) == 8 and all(s.startswith("UNK") for s in js(page, SRC)), js(page, SRC))
        page.select_option("[data-rs2-f=ind]", ""); page.wait_for_timeout(200)
        check(f"{tag} 9 'All industries' clears it", js(page, CHIP) is None)

        # ---- 10 coverage line
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(300)
        cov = js(page, "()=>{ const e = document.querySelector('[data-rs2-indcov]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null }")
        n_i = sum(1 for r in R if r["i"]); pct = int(100.0 * n_i / len(R))
        check(f"{tag} 10 coverage < 90% → muted line 'Industry data {pct}% complete'", cov == f"Industry data {pct}% complete", cov)
        page.click("[data-rs2-view=stocks]")
        check(f"{tag} 10 …only in the Industries view", js(page, "()=>!document.querySelector('[data-rs2-indcov]')"))

        # ---- 11 keyboard
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(300)
        js(page, "()=>{ if(document.activeElement) document.activeElement.blur(); }")
        sel = lambda: js(page, "()=>{ const e = document.querySelector('[data-rs2-ind-row].on'); return e ? e.dataset.ind : null }")
        first = sel()
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(200)
        s1 = sel()
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(200)
        s2 = sel()
        page.keyboard.press("ArrowUp"); page.wait_for_timeout(200)
        check(f"{tag} 11 ↓ ↓ ↑ moves the selected industry row", first == "Semiconductors" and s1 == "Software - Infrastructure" and s2 == "Aerospace & Defense" and sel() == s1, [first, s1, s2, sel()])
        for _ in range(8): page.keyboard.press("ArrowDown")
        page.wait_for_timeout(200)
        check(f"{tag} 11 stops at the last row", sel() == "Capital Markets", sel())
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(300)
        check(f"{tag} 11 → still switches the preset (Emerging) · stays in Industries", js(page, "()=>rs2.preset") == "emerging" and js(page, "()=>rs2.view") == "ind")
        page.keyboard.press("ArrowLeft"); page.wait_for_timeout(300)
        check(f"{tag} 11 ← back to Leaders", js(page, "()=>rs2.preset") == "leaders")
        page.keyboard.press("ArrowUp"); page.keyboard.press("ArrowUp"); page.wait_for_timeout(200)
        want = sel()
        page.keyboard.press("Enter"); page.wait_for_timeout(400)
        check(f"{tag} 11 Enter opens the selected industry's Stocks (chip + filtered rows)", js(page, "()=>rs2.view") == "stocks" and js(page, CHIP) == f"Industry: {want} ×" and len(js(page, SRC)) > 0, [want, js(page, CHIP)])
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(200)
        check(f"{tag} 11 ↓ in Stocks still moves stocks (not industries)", js(page, "()=>rs2.view") == "stocks")
        check(f"{tag} page errors none", not pe, pe[:2])
    finally:
        b.close()
    # full coverage → no coverage line
    b, page, pe, ce = opened(pw, w, h, build(unknown=0), view="ind")
    try:
        check(f"{tag} 10 coverage ≥ 90% → no line", js(page, "()=>!document.querySelector('[data-rs2-indcov]')") and len(js(page, ROWS)) > 0)
    finally:
        b.close()


def phone(pw, w, h):
    tag = "[%s]" % w
    R = build()
    b, page, pe, ce = opened(pw, w, h, R, view="stocks")
    try:
        bt = js(page, "()=>[...document.querySelectorAll('[data-rs2-view]')].map(b=>Math.round(b.getBoundingClientRect().height))")
        check(f"{tag} 14 phone: same toggle · 44px targets", len(bt) == 2 and all(x >= 44 for x in bt), bt)
        page.click("[data-rs2-view=ind]"); page.wait_for_timeout(400)
        E = [e for e in expect(R, "leaders") if e["m"] != 1]
        rows = js(page, "()=>[...document.querySelectorAll('[data-rs2-ind-row]')].map(r=>({ind:r.dataset.ind, l1:r.querySelector('.pl1').innerText.replace(/\\s+/g,' ').trim(), l2:r.querySelector('.pl2').innerText.replace(/\\s+/g,' ').trim(), h:Math.round(r.getBoundingClientRect().height), vis:r.querySelector('.c-top').offsetParent !== null}))")
        check(f"{tag} 14 2-line rows: 'Semiconductors 7 of 12' / 'Group RS 88 (#3) · top 3 names'", rows and rows[0]["l1"] == "Semiconductors 7 of 12" and rows[0]["l2"].startswith("Group RS ") and rows[0]["l2"].endswith("NVDAXX 99 · CREDOXX 97 · ALABXXX 95") and "(#" in rows[0]["l2"], rows[:1])
        check(f"{tag} 14 rows are ≥ 44px tall (tap targets) and the desktop cells are hidden", all(r["h"] >= 44 and not r["vis"] for r in rows), [(r["ind"], r["h"], r["vis"]) for r in rows])
        check(f"{tag} 14 same industries / order as desktop", [r["ind"] for r in rows] == [e["ind"] for e in E], [r["ind"] for r in rows])
        check(f"{tag} 14 no tick / Sort ▾ / ⋯ / detail sheet in Industries", js(page, "()=>!document.querySelector('[data-rs2-tick], [data-rs2-dots], [data-rs2-sort-wrap], [data-rs2-sheet], [data-rs2-selbar]')"))
        fb = js(page, "()=>{ const e = document.querySelector('[data-rs2-fold]'); return e ? Math.round(e.getBoundingClientRect().height) : 0 }")
        check(f"{tag} 14 the '+ 2 industries with 1 match' line is a ≥ 44px target", fb >= 44, fb)
        o = over(page)
        check(f"{tag} 15 Industries: no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)
        page.click("[data-rs2-ind-row][data-ind=Semiconductors]"); page.wait_for_timeout(400)
        check(f"{tag} 14 tap → filtered Stocks with the chip (no detail sheet)", js(page, CHIP) == "Industry: Semiconductors ×" and js(page, "()=>rs2.view") == "stocks" and len(js(page, SRC)) == 7 and js(page, "()=>!document.querySelector('[data-rs2-sheet]')"), [js(page, CHIP), len(js(page, SRC))])
        cb = js(page, "()=>Math.round(document.querySelector('[data-rs2-indchip-x]').getBoundingClientRect().height)")
        check(f"{tag} 14 chip × is a ≥ 44px target", cb >= 44, cb)
        o = over(page)
        check(f"{tag} 15 filtered Stocks: no horizontal overflow", o["sw"] <= 0 and o["bad"] == 0, o)
        page.click("[data-rs2-indchip-x]"); page.wait_for_timeout(300)
        check(f"{tag} 14 × clears it", js(page, CHIP) is None)
        check(f"{tag} page errors none", not pe, pe[:2])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        desk(pw, 1440, 900)
        desk(pw, 1280, 800)
        phone(pw, 390, 844)
        phone(pw, 360, 740)
    f = [r for r in results if not r[1]]
    print("\nSUMMARY RS2b: %d/%d pass" % (len(results) - len(f), len(results)))
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
