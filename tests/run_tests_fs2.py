#!/usr/bin/env python3
"""FS2 — Fact Sheet "answer-first": left tabs Business | Results | AI thesis · Business boxes · Results tiles · AI thesis tab · no page scroll at 1440x900 · phone 4-way switch.
Run: python3 tests/run_tests_fs2.py"""
import sys, os, json, copy
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import hw1_common as H
import fs2_common as F

VIS = "(s)=>{ const e = document.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(), c = getComputedStyle(e); return r.width>0 && r.height>0 && c.visibility!=='hidden' && c.display!=='none'; }"
TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
OVER = "()=>{ const w = document.documentElement.clientWidth; return document.documentElement.scrollWidth <= w + 1 && document.body.scrollWidth <= w + 1; }"
DOC = "()=>{ const d = document.scrollingElement; return [d.scrollHeight, innerHeight]; }"
CARD = "()=>{ const c = document.querySelector('.hw1-facts'), m = document.querySelector('.hw1-mscroll'); return {facts:[c.scrollHeight, c.clientHeight], mine:[m.scrollHeight, m.clientHeight]}; }"
TAB = "()=>document.querySelector('[data-hw1-page]').dataset.hw2Tab"
COL = lambda page, sel, prop="color": js(page, "([s,p])=>{ const e = document.querySelector(s); return e ? getComputedStyle(e)[p] : null; }", [sel, prop])
GREEN, AMBER, RED = "rgb(14, 107, 76)", "rgb(154, 91, 0)", None


def rows_of(k, vals, **x):
    return dict({"k": k, "label": k, "unit": "%", "v": vals, "kind": "rpt", "src": "8-K"}, **x)


def facts_with(rows, base=None):
    f = copy.deepcopy(base or F.COMP); f["q"]["rows"] = rows; return f


def strings_of(f):
    """every text LT2 field that must stay reachable on the page"""
    s = [f["biz"], f["asOf"]]
    s += [m["seg"] for m in f["mix"]]
    if f.get("mixMeta"): s += [f["mixMeta"]["src"], f["mixMeta"]["period"], f["mixMeta"]["basis"]]
    s += f["q"]["cols"]
    for r in f["q"]["rows"]:
        s += [r["label"], r["src"]] + ([r["formula"]] if r.get("formula") else [])
    for x in (f.get("lines") or []) + (f.get("more") or []):
        s += [x["label"], x["text"], x["src"]] + [x[k] for k in ("formula", "period", "note") if x.get(k)]
    for x in f.get("mgmt") or []: s += [x["text"], x["src"]]
    s += f.get("missing") or []
    return s


def run(pw, w, h):
    tag = "[%s]" % w
    phone = w < 1024
    b, page, pe = F.open_fs2(pw, w, h)
    try:
        js(page, "()=>{ try{ Object.keys(localStorage).filter(k=>k.startsWith('dash.hw2Tab')).forEach(k=>localStorage.removeItem(k)); }catch(e){} }")
        # ================= A · tabs, defaults, remember
        F.go(page, "COST", "ladder")
        check(f"{tag} Compounder default tab = Business", js(page, TAB) == "business", js(page, TAB))
        F.go(page, "AAPL", "winner")
        check(f"{tag} Momentum default tab = Results", js(page, TAB) == "results", js(page, TAB))
        F.go(page, "COST", "ladder")
        if not phone:
            lbl = js(page, "()=>[...document.querySelectorAll('[data-hw2-tabbtn]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
            check(f"{tag} switch = Business | Results | AI thesis (+ badge Lite)", lbl == ["Business", "Results", "AI thesis Lite"], lbl)
        else:
            lbl = js(page, "()=>[...document.querySelectorAll('[data-hw1-seg]')].map(b=>b.innerText.trim())")
            hh = js(page, "()=>[...document.querySelectorAll('[data-hw1-seg]')].map(b=>Math.round(b.getBoundingClientRect().height))")
            check(f"{tag} phone switch = Business | Results | AI | Mine, 44px", lbl == ["Business", "Results", "AI", "Mine"] and all(x >= 44 for x in hh), [lbl, hh])
            check(f"{tag} phone: the in-card desktop switch is hidden", not js(page, VIS, "[data-hw2-seg]"))
        js(page, "()=>hw1SegSet(hwSym,'ai')"); page.wait_for_timeout(120)
        ls = js(page, "()=>localStorage.getItem('dash.hw2Tab.COST')")
        check(f"{tag} tab remembered per stock (localStorage)", ls == "ai" and js(page, TAB) == "ai", ls)
        F.go(page, "AAPL", "winner"); a = js(page, TAB)
        F.go(page, "COST", "ladder")
        check(f"{tag} re-open: COST keeps AI thesis, AAPL keeps Results", js(page, TAB) == "ai" and a == "results", [js(page, TAB), a])
        js(page, "()=>{ hw1SegSet(hwSym,'business'); }")
        # ----- keys (desktop)
        if not phone:
            page.mouse.click(5, 5); page.keyboard.press("ArrowLeft"); page.wait_for_timeout(80)
            check(f"{tag} <- at the first tab stops", js(page, TAB) == "business")
            page.keyboard.press("ArrowRight"); page.wait_for_timeout(80); t1 = js(page, TAB)
            page.keyboard.press("ArrowRight"); page.wait_for_timeout(80); t2 = js(page, TAB)
            page.keyboard.press("ArrowRight"); page.wait_for_timeout(80); t3 = js(page, TAB)
            check(f"{tag} -> moves Business > Results > AI thesis and stops at the end", [t1, t2, t3] == ["results", "ai", "ai"], [t1, t2, t3])
            page.keyboard.press("ArrowLeft"); page.wait_for_timeout(80)
            check(f"{tag} <- moves back", js(page, TAB) == "results")
            page.focus("[data-hw1-ta=why]"); page.keyboard.press("ArrowLeft"); page.keyboard.press("ArrowRight"); page.wait_for_timeout(80)
            check(f"{tag} arrows do nothing while typing", js(page, TAB) == "results")
            js(page, "()=>document.activeElement.blur()")
            js(page, "()=>hw1SegSet(hwSym,'business')")
        # ================= B · Business tab
        F.go(page, "COST", "ladder", "business")
        order = js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>e.dataset.hw2Box)")
        check(f"{tag} Compounder: 6 boxes in the fixed order", order == ["product", "customers", "economics", "retention", "cash", "outside"], order)
        nums = js(page, "()=>[...document.querySelectorAll('[data-hw2-grid] .qh .n')].map(e=>e.innerText)")
        check(f"{tag} boxes carry the numbers 1-6", nums == ["1", "2", "3", "4", "5", "6"], nums)
        if not phone:
            lefts = js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>Math.round(e.getBoundingClientRect().left))")
            check(f"{tag} 2-column grid", len(set(lefts)) == 2 and lefts[0] == lefts[2] == lefts[4] and lefts[1] == lefts[3] == lefts[5], lefts)
        flags = js(page, "()=>[...document.querySelectorAll('[data-hw2-lv]')].map(e=>[e.closest('[data-hw2-box]').dataset.hw2Box, e.innerText.trim(), getComputedStyle(e).color])")
        fd = {x[0]: x for x in flags}
        check(f"{tag} flag label text comes from the data", fd["retention"][1] == "slipping" and fd["customers"][1] == "no customer ≥10%" and fd["economics"][1] == "yes", flags)
        check(f"{tag} flag colours: ok green · watch amber · info grey", fd["customers"][2] == GREEN and fd["retention"][2] == AMBER and fd["product"][2] not in (GREEN, AMBER), flags)
        tint = js(page, "()=>['retention','outside','customers'].map(k=>getComputedStyle(document.querySelector('[data-hw2-box=\"'+k+'\"]')).backgroundColor)")
        check(f"{tag} watch boxes get the amber tint, ok box does not", tint[0] == tint[1] == "rgb(255, 251, 244)" and tint[2] != tint[0], tint)
        mt = js(page, TXT, "[data-hw2-box=cash]")
        check(f"{tag} missing box: 'Not disclosed' in amber (+ the reason)", mt and mt.startswith("5 Cash cycle") and "Not disclosed" in mt and "not split out" in mt and js(page, "()=>getComputedStyle(document.querySelector('[data-hw2-box=cash] .a')).color") == AMBER, mt)
        check(f"{tag} box 1: answer + mix bar + legend (Segment pct% · +yoy%) + source", js(page, "()=>!!document.querySelector('[data-hw2-box=product] [data-hw2-mix]')") and "Food 40% · +7%" in (js(page, TXT, "[data-hw2-box=product] [data-hw2-mixl]") or "") and "10-K note 11" in (js(page, TXT, "[data-hw2-box=product]") or ""))
        check(f"{tag} box anatomy: question · flag · answer · one line · source", all(x in (js(page, TXT, "[data-hw2-box=retention]") or "") for x in ["Do customers stay?", "slipping", "Renewal rate 92.5%", "Down from 93.0%", "Q1 FY27 earnings release"]))
        check(f"{tag} a business note stays inline (amber)", js(page, "()=>{ const n = document.querySelector('[data-hw2-box=retention] [data-hw2-note]'); return !!n && n.getBoundingClientRect().height > 0 && getComputedStyle(n).color === 'rgb(154, 91, 0)' && n.innerText.includes('only members who were due'); }"))
        check(f"{tag} 'Not disclosed:' line under the boxes", "Not disclosed: Timing of next fee increase" in (js(page, TXT, "[data-hw2-nd]") or ""))
        st = js(page, TXT, "[data-hw2-latest]") or ""
        check(f"{tag} Latest results strip: revenue · EPS · KPI with trend words + Results ›", all(x in st for x in ["Latest results", "Revenue +8%", "steady", "EPS +14%", "accelerating", "Are members staying?".split()[0] and "Renewal rate", "slipping", "Results ›"]), st)
        js(page, "()=>document.querySelector('[data-hw2-latest-go]').click()"); page.wait_for_timeout(120)
        check(f"{tag} Results › switches to the Results tab", js(page, TAB) == "results" and js(page, VIS, "[data-hw2-tiles]"))
        F.go(page, "AAPL", "winner", "business")
        mo = js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>e.dataset.hw2Box)")
        check(f"{tag} Momentum: 4 boxes (1, 2, 3, 6)", mo == ["product", "customers", "economics", "outside"], mo)
        nums = js(page, "()=>[...document.querySelectorAll('[data-hw2-grid] .qh .n')].map(e=>e.innerText)")
        check(f"{tag} Momentum boxes keep their numbers 1 2 3 6", nums == ["1", "2", "3", "6"], nums)
        if not phone:
            lefts = js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>Math.round(e.getBoundingClientRect().left))")
            check(f"{tag} Momentum boxes 2 x 2", lefts[0] == lefts[2] and lefts[1] == lefts[3] and lefts[0] != lefts[1], lefts)
        # ================= C · Results tab
        F.go(page, "COST", "ladder", "results")
        tl = js(page, "()=>[...document.querySelectorAll('[data-hw2-tiles] .hw2-t')].map(e=>e.dataset.hw1Q || e.dataset.hw2G)")
        check(f"{tag} Compounder tiles: revenue, EPS, KPI, margin", tl == ["rev_yoy", "eps_yoy", "kpi_renewal", "op_margin"], tl)
        bars = js(page, "()=>[...document.querySelectorAll('[data-hw2-tiles] .hw2-t')].map(e=>[e.querySelectorAll('.hw2-sp .s').length, e.querySelectorAll('.hw2-sv span').length, e.querySelectorAll('.hw2-sp i.last').length])")
        check(f"{tag} each tile: 4 bars (last dark) with 4 values", all(x == [4, 4, 1] for x in bars), bars)
        t0 = js(page, TXT, "[data-hw1-q=eps_yoy]") or ""
        check(f"{tag} tile = question · answer + trend word · reason", all(x in t0 for x in ["Is profit per share growing?", "+14%", "accelerating", "+11% → +13% → +14%"]), t0)
        t2 = js(page, TXT, "[data-hw1-q=kpi_renewal]") or ""
        check(f"{tag} level row: reason = 4-quarter range, uses the row's ask", all(x in t2 for x in ["Are members staying?", "92.5%", "slipping", "92.5 – 93% in 4 quarters"]), t2)
        rg = js(page, "()=>[...document.querySelectorAll('[data-hw2-rows] [data-hw2-b]')].map(e=>e.dataset.hw2G || e.dataset.hw1Q || e.dataset.hw2B)")
        check(f"{tag} Compounder rows in order: profit > cash > exposure > shares > expected > mgmt > not disclosed", rg == ["profit", "cash", "exposure", "shares_yoy", "expected", "mgmt", "nd"], rg)
        gt = js(page, TXT, "[data-hw1-q=rev_yoy]") or ""
        check(f"{tag} the growth line is merged into the revenue block (no separate row)", "growth" not in rg and "+8%" in gt)
        check(f"{tag} rows: question · answer · source (web source + date visible)", "What does the market expect next?" in (js(page, TXT, "[data-hw2-g=expected]") or "") and "consensus site · 18 Nov" in (js(page, TXT, "[data-hw2-g=expected]") or ""), js(page, TXT, "[data-hw2-g=expected]"))
        check(f"{tag} a line's note is inline, amber, visible (not only in the popover)", js(page, "()=>{ const n = document.querySelector('[data-hw2-g=profit] [data-hw2-note]'); return !!n && n.getBoundingClientRect().height > 0 && getComputedStyle(n).color === 'rgb(154, 91, 0)' && n.innerText.includes('Shows size only'); }"))
        check(f"{tag} line asks: 'How much do fees matter?' (ask) · default 'Is it turning profit into cash?'", "How much do fees matter?" in (js(page, TXT, "[data-hw2-g=profit]") or "") and "Is it turning profit into cash?" in (js(page, TXT, "[data-hw2-g=cash]") or ""))
        check(f"{tag} management: question + quote + — source", "What does management say?" in (js(page, TXT, "[data-hw2-g=mgmt]") or "") and "— Q3 call" in (js(page, TXT, "[data-hw2-g=mgmt]") or ""))
        check(f"{tag} not disclosed row in amber", js(page, "()=>getComputedStyle(document.querySelector('[data-hw2-b=nd] .a')).color") == AMBER)
        check(f"{tag} More facts folded; opens in place with the items", js(page, "()=>{ const d = document.querySelector('[data-hw1-more]'); return !!d && !d.open && d.innerText.includes('More facts'); }"))
        js(page, "()=>{ document.querySelector('[data-hw1-more]').open = true; }"); page.wait_for_timeout(80)
        check(f"{tag} More facts open: Peer op. margin + its ask/label reachable", "2.9% / 3.1%" in (js(page, TXT, "[data-hw1-more]") or ""))
        js(page, "()=>{ document.querySelector('[data-hw1-more]').open = false; }")
        F.go(page, "AAPL", "winner", "results")
        tl = js(page, "()=>[...document.querySelectorAll('[data-hw2-tiles] .hw2-t')].map(e=>e.dataset.hw1Q || e.dataset.hw2G)")
        check(f"{tag} Momentum tiles: revenue, EPS, margin, last quarter", tl == ["rev_yoy", "eps_yoy", "gm", "lastq"], tl)
        rg = js(page, "()=>[...document.querySelectorAll('[data-hw2-rows] [data-hw2-b]')].map(e=>e.dataset.hw2G || e.dataset.hw1Q || e.dataset.hw2B)")
        check(f"{tag} Momentum rows: lastq > expected > mgmt > not disclosed", rg == ["lastq", "expected", "mgmt", "nd"], rg)
        check(f"{tag} the beat tile shows the answer line + source", "Did it beat expectations?" in (js(page, TXT, "[data-hw2-tiles] [data-hw2-g=lastq]") or "") and "$18.0B vs $17.4B est." in (js(page, TXT, "[data-hw2-tiles] [data-hw2-g=lastq]") or ""))
        # ================= D · trend words + colours
        cases = [("accel", [10, 20, 35, 55], "accelerating", "g", "accel"), ("slow", [60, 50, 40, 35], "slowing", "a", "slow"), ("negative", [5, -2, -4, -6], "slowing", "r", "slow"),
                 ("steady", [10, 12, 11, 12], "steady", "n", "steady"), ("rise", [3.5, 3.6, 3.7, 3.8], "rising", "g", "rising"), ("fall", [93.0, 92.9, 92.7, 92.5], "slipping", "a", "falling")]
        rws = [rows_of("rev_yoy", [5, -2, -4, -6]), rows_of("eps_yoy", [10, 20, 35, 55]), rows_of("kpi_a", [60, 50, 40, 35]), rows_of("kpi_b", [10, 12, 11, 12])]
        F.setf(page, "COST", facts_with(rws)); F.go(page, "COST", "ladder", "results")
        got = js(page, "()=>[...document.querySelectorAll('.hw2-t .hw2-tw')].map(e=>[e.dataset.hw1Trend, e.innerText, e.className.replace('hw2-tw ','')])")
        check(f"{tag} trend: accelerating green · slowing amber · slowing + negative value red · steady grey", got == [["slow", "slowing", "r"], ["accel", "accelerating", "g"], ["slow", "slowing", "a"], ["steady", "steady", "n"]], got)
        cl = js(page, "()=>[...document.querySelectorAll('.hw2-t .hw2-tw')].map(e=>getComputedStyle(e).color)")
        check(f"{tag} trend colours are red / green / amber / grey", cl[1] == GREEN and cl[2] == AMBER and cl[0] not in (GREEN, AMBER) and cl[3] not in (GREEN, AMBER, cl[0]), cl)
        rws = [rows_of("op_margin", [3.5, 3.6, 3.7, 3.8]), rows_of("kpi_renewal", [93.0, 92.9, 92.7, 92.5]), rows_of("gm", [40, 41, 40, 41])]
        F.setf(page, "COST", facts_with(rws)); F.go(page, "COST", "ladder", "results")
        got = js(page, "()=>[...document.querySelectorAll('.hw2-t .hw2-tw')].map(e=>[e.dataset.hw1Trend, e.innerText, e.className.replace('hw2-tw ','')])")
        check(f"{tag} level rows: rising green · slipping amber · steady grey", sorted(x[0] for x in got) == ["falling", "rising", "steady"] and {x[0]: x[2] for x in got} == {"rising": "g", "falling": "a", "steady": "n"}, got)
        neg = [rows_of("shares_yoy", [-0.1, -0.2, -0.2, -0.3])]
        F.setf(page, "COST", facts_with([rows_of("rev_yoy", [5, 4, 2, -3])] + neg)); F.go(page, "COST", "ladder", "results")
        got = js(page, "()=>[document.querySelector('[data-hw1-q=rev_yoy] .hw2-tw').className, document.querySelector('[data-hw1-q=shares_yoy] .hw2-tw').className]")
        check(f"{tag} negative growth value = red; a shrinking share count is not red", got[0].endswith(" r") and not got[1].endswith(" r"), got)
        bars = js(page, "()=>[...document.querySelectorAll('[data-hw1-q=rev_yoy] .hw2-sp .s i')].map(e=>[e.classList.contains('neg'), Math.round(e.getBoundingClientRect().height)])")
        check(f"{tag} negative values draw below the baseline", [x[0] for x in bars] == [False, False, False, True], bars)
        # ================= E · header dates with / without ends · old JSON
        F.setf(page, "COST", F.COMP); F.go(page, "COST", "ladder", "business")
        hd = js(page, TXT, "[data-hw2-period]")
        check(f"{tag} header with ends: calendar months + fiscal quarter + reported date", hd == "latest quarter Jun–Aug 2026 (Q3 FY26) · reported 18 Nov", hd)
        F.setf(page, "COST", F.OLD_COMP); F.go(page, "COST", "ladder", "business")
        hd = js(page, TXT, "[data-hw2-period]")
        check(f"{tag} header without ends: latest quarter Q3 FY26", hd == "latest quarter Q3 FY26 · reported 18 Nov", hd)
        old = js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>e.dataset.hw2Box)")
        check(f"{tag} old JSON (no business): box 1 from biz + mix, a hint instead of 5 empty boxes", old == ["product"] and js(page, "()=>!!document.querySelector('[data-hw2-nobiz]')") and js(page, TXT, "[data-hw2-biz]") == F.OLD_COMP["biz"], old)
        bz = js(page, "()=>{ const e = document.querySelector('[data-hw2-biz]'); const c = getComputedStyle(e); return [e.scrollWidth <= e.clientWidth + 1, c.textOverflow, c.whiteSpace]; }")
        check(f"{tag} biz is never truncated (wraps)", bz[0] and bz[1] != "ellipsis" and bz[2] != "nowrap", bz)
        F.go(page, "COST", "ladder", "results")
        check(f"{tag} old JSON still renders the Results tiles and rows", js(page, "()=>document.querySelectorAll('[data-hw2-tiles] .hw2-t').length") == 4 and js(page, "()=>document.querySelectorAll('[data-hw2-rows] [data-hw2-b]').length") >= 5)
        F.setf(page, "AAPL", F.OLD_MOM); F.go(page, "AAPL", "winner", "results")
        check(f"{tag} old Momentum JSON renders (no ask, no ends)", js(page, "()=>document.querySelectorAll('[data-hw2-tiles] .hw2-t').length") == 4 and "Is revenue growing?" in (js(page, TXT, "[data-hw2-tiles]") or ""))
        # ================= F · reachability of every LT2 field + popover
        for nm, f in (("Compounder", F.COMP), ("Momentum", F.MOM), ("Compounder (old)", F.OLD_COMP), ("Momentum (old)", F.OLD_MOM)):
            sym, trk = ("COST", "ladder") if nm.startswith("Comp") else ("AAPL", "winner")
            F.setf(page, sym, f); F.go(page, sym, trk)
            txt = js(page, "()=>document.querySelector('.hw1-facts').textContent.replace(/\\s+/g,' ')")
            miss = [x for x in strings_of(f) if " ".join(x.split()) not in txt]
            check(f"{tag} {nm}: every LT2 field is reachable (block / reason / popover)", not miss, miss)
        F.setf(page, "COST", F.COMP); F.go(page, "COST", "ladder", "results")
        js(page, "()=>document.querySelector('[data-hw1-q=rev_yoy]').click()"); page.wait_for_timeout(120)
        pop = js(page, "()=>{ const p = [...document.querySelectorAll('.hw1-pop')].find(x=>x.offsetParent); return p ? p.innerText.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} tap a tile: popover = Formula · Period (months + quarters) · Source · Type", pop and all(x in pop for x in ["Formula", "Revenue ÷ same quarter last year − 1", "Period Sep 2025–Aug 2026 (Q4'25 – Q3'26)", "Source 8-K EX-99.1 ×4", "Type Calculated"]), pop)
        check(f"{tag} tapped block has aria-expanded + selected look", js(page, "()=>{ const e = document.querySelector('[data-hw1-q=rev_yoy]'); return e.getAttribute('aria-expanded') === 'true' && e.classList.contains('sel'); }"))
        js(page, "()=>document.querySelector('[data-hw1-q=rev_yoy]').click()"); page.wait_for_timeout(80)
        js(page, "()=>document.querySelector('[data-hw2-g=expected]').click()"); page.wait_for_timeout(100)
        pop = js(page, "()=>{ const p = [...document.querySelectorAll('.hw1-pop')].find(x=>x.offsetParent); return p ? p.innerText.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} web line popover: Date + Type Quote site", pop and "Date 18 Nov" in pop and "Type Quote site" in pop, pop)
        js(page, "()=>document.querySelector('[data-hw2-g=expected]').click()")
        js(page, "()=>document.querySelector('[data-hw2-g=profit]').click()"); page.wait_for_timeout(100)
        pop = js(page, "()=>{ const p = [...document.querySelectorAll('.hw1-pop')].find(x=>x.offsetParent); return p ? p.innerText.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} profit line popover: formula + period + note", pop and "Fee revenue $1.3B ÷ Operating income $2.6B" in pop and "Period Jun–Aug 2026 (Q3 FY26)" in pop and "Shows size only" in pop, pop)
        js(page, "()=>document.querySelector('[data-hw2-g=profit]').click()")
        js(page, "()=>{ hw1SegSet(hwSym,'business'); document.querySelector('[data-hw2-box=retention]').click(); }"); page.wait_for_timeout(100)
        pop = js(page, "()=>{ const p = [...document.querySelectorAll('.hw1-pop')].find(x=>x.offsetParent); return p ? p.innerText.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} business box popover: Period · Source · Type", pop and "Period Q1 FY27" in pop and "Source Q1 FY27 earnings release" in pop and "Type Reported" in pop, pop)
        js(page, "()=>document.querySelector('[data-hw2-box=retention]').click()")
        # ================= G · AI thesis tab
        F.go(page, "COST", "ladder", "ai")
        check(f"{tag} badge = Lite when thesis.mode is lite", (js(page, TXT, "[data-hw2-badge]") or "") == "Lite")
        ah = js(page, TXT, "[data-hw2-ai-h]") or ""
        check(f"{tag} AI header: Lite · date · based on <basis> + Update ›", ah.startswith("Lite · 2 Oct · based on 10-Q Q3 FY26") and "Update ›" in ah, ah)
        sm = js(page, TXT, "[data-hw2-sum]") or ""
        check(f"{tag} summary rows: Thesis · Risk · Next · Breaks if (+ Price / Status)", all(x in sm for x in ["Thesis ZQTHESIS0", "Risk", "Next ZQNEXT", "Breaks if ZQBREAKER", "Price", "Status"]), sm)
        secs = js(page, "()=>[...document.querySelectorAll('[data-hw2-sec]')].map(e=>[e.dataset.hw2Sec, e.open, e.querySelector('summary').innerText.trim()])")
        check(f"{tag} 4 fold-out sections, first open, no tabs inside tabs", [s[0] for s in secs] == ["s1", "s2", "s3", "s4"] and [s[1] for s in secs] == [True, False, False, False] and not js(page, "()=>!!document.querySelector('[data-hw2-pane=ai] [data-lt-tab], [data-hw2-pane=ai] .ltTab')"), secs)
        js(page, "()=>document.querySelector('[data-hw2-sec=s2] summary').click()"); page.wait_for_timeout(80)
        check(f"{tag} a section opens in place", js(page, "()=>document.querySelector('[data-hw2-sec=s2]').open"))
        up = js(page, TXT, "[data-hw2-upsell]") or ""
        check(f"{tag} Lite: 'Want more depth' line with living-thesis deep COST compounder", "Want more depth before buying?" in up and "living-thesis deep COST compounder" in up and js(page, "()=>document.querySelector('[data-hw2-upsell] [data-cmd]').dataset.cmd") == "living-thesis deep COST compounder", up)
        check(f"{tag} the AI tab header has its own Update ›; the Facts header one is hidden here", js(page, VIS, "[data-hw2-ai-update]") and not js(page, VIS, "[data-hw2-period]"))
        check(f"{tag} thesis [[terms]] stay tappable (.ltTerm in the sections)", js(page, "()=>{ const t = document.querySelector('[data-hw2-pane=ai] .ltTerm'); return !t || !!t.dataset.term; }"))
        # never fills fields
        js(page, "()=>{ const t = document.querySelector('[data-hw2-pane=ai] .ltTerm'); if(t) t.click(); }"); page.wait_for_timeout(80)
        check(f"{tag} the AI thesis tab never fills your fields", js(page, "()=>[...document.querySelectorAll('[data-hw1-ta]')].every(e=>e.value === '')"))
        js(page, "()=>{ if(typeof ltTermClose==='function') ltTermClose(); }")
        js(page, "()=>{ const it = wlItemOf('COST'); it.thesis.mode = 'deep'; renderWatchlist(); }"); page.wait_for_timeout(200)
        check(f"{tag} badge = Deep when mode is deep, no upsell", (js(page, TXT, "[data-hw2-badge]") or "") == "Deep" and not js(page, "()=>!!document.querySelector('[data-hw2-upsell]')") and (js(page, TXT, "[data-hw2-ai-h]") or "").startswith("Deep"))
        js(page, "()=>{ const it = wlItemOf('COST'); it.thesis.mode = 'facts'; delete it.thesis.sections; renderWatchlist(); }"); page.wait_for_timeout(200)
        check(f"{tag} facts-only thesis = badge none + empty state", (js(page, TXT, "[data-hw2-badge]") or "") == "none" and js(page, "()=>!!document.querySelector('[data-hw2-ai-empty]')"))
        F.go(page, "WHSE", "ladder", "ai")
        em = js(page, TXT, "[data-hw2-ai-empty]") or ""
        cmds = js(page, "()=>[...document.querySelectorAll('[data-hw2-ai-empty] [data-cmd]')].map(e=>e.dataset.cmd)")
        check(f"{tag} empty state: No AI thesis yet · lite/deep chips for this track · token cost · Import JSON · tip", "No AI thesis yet" in em and cmds == ["living-thesis lite WHSE compounder", "living-thesis deep WHSE compounder"] and "≈ 55k tokens" in em and "≈ 110k tokens" in em and "Import JSON ›" in em and "Write your own thesis first" in em, [em, cmds])
        check(f"{tag} empty state: badge none", (js(page, TXT, "[data-hw2-badge]") or "") == "none")
        F.go(page, "SRC1", "winner", "ai")
        cmds = js(page, "()=>[...document.querySelectorAll('[data-hw2-ai-empty] [data-cmd]')].map(e=>e.dataset.cmd)")
        check(f"{tag} empty state for a Momentum stock uses 'momentum'", cmds == ["living-thesis lite SRC1 momentum", "living-thesis deep SRC1 momentum"], cmds)
        js(page, "()=>document.querySelector('[data-hw2-ai-import]').click()"); page.wait_for_timeout(250)
        check(f"{tag} Import JSON › opens the import", js(page, "()=>!!document.querySelector('#ltImp, [data-lt-imp], .ltImpBox, textarea[data-lt-imp-ta], [data-lt-imp-text]') || (typeof ltImp !== 'undefined' && !!ltImp)"))
        js(page, "()=>{ if(typeof ltImportClose==='function') ltImportClose(); }")
        # ================= H · fallback (no facts)
        F.go(page, "WHSE", "ladder", "business")
        check(f"{tag} no facts: HW1c fallback unchanged (steps + import link) inside the Business tab", js(page, "()=>document.querySelector('[data-hw1-facts]').dataset.hw1Facts") == "fallback" and js(page, VIS, "[data-hw1-nofacts]") and js(page, VIS, "[data-hw1-import-link]") and "No Fact Sheet yet" in (js(page, TXT, "[data-hw1-nofacts]") or ""))
        # ================= I · layout
        F.setf(page, "COST", F.COMP); F.setf(page, "AAPL", F.MOM)
        for sym, trk in (("COST", "ladder"), ("AAPL", "winner")):
            for tab in ("business", "results", "ai"):
                F.go(page, sym, trk, tab)
                if phone:
                    check(f"{tag} {sym}/{tab}: no horizontal overflow", js(page, OVER))
                    continue
                d = js(page, DOC); c = js(page, CARD)
                if h >= 900:
                    check(f"{tag} {sym}/{tab}: the page does not scroll at 1440x900", d[0] <= d[1] + 1, d)
                    check(f"{tag} {sym}/{tab}: left card content fits (no inner scroll)", c["facts"][0] <= c["facts"][1] + 1, c)
                    check(f"{tag} {sym}/{tab}: right card — footer buttons stay visible (HW2: the 3 answers + chips scroll inside the card)", js(page, "()=>{ const m = document.querySelector('[data-hw1-mine]').getBoundingClientRect(), b = document.querySelector('.hw1-btns').getBoundingClientRect(); return b.bottom <= m.bottom + 1 && b.top >= m.top; }"), c)
                else:
                    check(f"{tag} {sym}/{tab}: page still does not scroll at {w}x{h}", d[0] <= d[1] + 1, d)
        if not phone:
            F.go(page, "COST", "ladder", "business")
            bt = js(page, "()=>{ const f = document.querySelector('.hw1-mfoot').getBoundingClientRect(), v = innerHeight; return [Math.round(f.bottom), v, [...document.querySelectorAll('.hw1-btns .btn')].every(b=>b.getBoundingClientRect().bottom <= v)]; }")
            check(f"{tag} right card footer (Save draft · Save · mark done · Copy for AI challenge) stays visible", bt[2], bt)
            if h < 900:
                c = js(page, CARD)
                check(f"{tag} smaller laptop: the left card scrolls inside itself (Compounder Business)", c["facts"][0] > c["facts"][1], c)
            ov = js(page, "()=>{ const ta = document.querySelector('[data-hw1-ta=why]'); const a = ta.getBoundingClientRect().height; ta.focus(); return [a, ta.getBoundingClientRect().height]; }")
            page.wait_for_timeout(100)
            ov[1] = js(page, "()=>document.querySelector('[data-hw1-ta=why]').getBoundingClientRect().height")
            check(f"{tag} textareas ~2 lines tall and do not jump on focus (HW2: chips below must not move)", 40 <= ov[0] <= 70 and ov[1] == ov[0], ov)
        else:
            F.go(page, "COST", "ladder", "results")
            ch = js(page, "()=>{ const t = document.querySelector('[data-hw1-q=rev_yoy]'), a = t.querySelector('.ans').getBoundingClientRect(), c = t.querySelector('.ch').getBoundingClientRect(); return [Math.round(a.bottom), Math.round(c.top)]; }")
            check(f"{tag} phone: the mini chart sits under the answer", ch[1] >= ch[0] - 1, ch)
            hh = js(page, "()=>[...document.querySelectorAll('[data-hw2-tiles] .hw2-t, [data-hw2-rows] [data-hw1-row]')].map(e=>Math.round(e.getBoundingClientRect().height))")
            check(f"{tag} phone: every tap block is >= 44px", all(x >= 44 for x in hh), hh)
            F.go(page, "COST", "ladder", "business")
            hh = js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>Math.round(e.getBoundingClientRect().height))")
            check(f"{tag} phone: Business boxes >= 44px, one column", all(x >= 44 for x in hh) and len(set(js(page, "()=>[...document.querySelectorAll('[data-hw2-box]')].map(e=>Math.round(e.getBoundingClientRect().left))"))) == 1, hh)
            F.go(page, "COST", "ladder", "ai")
            check(f"{tag} phone: AI tab no overflow", js(page, OVER))
            js(page, "()=>hw1SegSet(hwSym,'mine')"); page.wait_for_timeout(100)
            check(f"{tag} phone: Mine shows the fields + sticky buttons, no overflow", js(page, VIS, "[data-hw1-ta=why]") and js(page, VIS, "[data-hw1-done]") and js(page, OVER))
        check(f"{tag} no console / page errors", not pe, pe)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (1280, 800), (390, 844), (360, 800)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY FS2: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
