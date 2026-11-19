#!/usr/bin/env python3
"""LR5b — Journal tab: stats match the fixture by hand · R on the ORIGINAL stop (moved-stop case · no stop → "—") · Both = both accounts, THB total + trade currency rows ·
review save round-trip (persisted, additive `review`) · period / port filters · Not taken · no Thai in #tabJournal · one line per row at 360/390/1440 · no overflow.
Fixture: tests/lr5_common.py (Nov 2025, main + fam). Run: python3 tests/run_tests_lr5b.py"""
import re, sys, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import lr5_common as C
import lib_phase38 as P38

THAI = """()=>{ const out = []; const w = document.createTreeWalker(document.getElementById('tabJournal'), NodeFilter.SHOW_TEXT); let n; while(n = w.nextNode()){ if(/[\\u0E00-\\u0E3E\\u0E40-\\u0E7F]/.test(n.nodeValue)) out.push(n.nodeValue.trim().slice(0, 60)); }
  document.querySelectorAll('#tabJournal [title],#tabJournal [aria-label],#tabJournal [placeholder]').forEach(e=>['title', 'aria-label', 'placeholder'].forEach(a=>{ const v = e.getAttribute(a); if(v && /[\\u0E00-\\u0E3E\\u0E40-\\u0E7F]/.test(v)) out.push('@' + a + ' ' + v.slice(0, 60)); })); return out; }"""
KPI = """()=>{ const o = {}; document.querySelectorAll('[data-lr5-k]').forEach(k=>o[k.dataset.lr5K] = {big:k.querySelector('b').innerText.trim(), sub:k.querySelector('.lr5-ksub').innerText.trim()}); return o; }"""
ROWS = """()=>[...document.querySelectorAll('[data-lr5-row]')].map(r=>({k:r.dataset.lr5Row, t:r.innerText.replace(/\\s+/g,' ').trim(), h:Math.round(r.getBoundingClientRect().height)}))"""


def kpis(page): return js(page, KPI)
def rows(page): return js(page, ROWS)
def pick(page, tab, v): js(page, "([t,v])=>lrSwPick(t,v)", [tab, v]); page.wait_for_timeout(250)
def setp(page, k, v): js(page, "([k,v])=>lr5Set(k,v)", [k, v]); page.wait_for_timeout(250)


def run(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = C.open_journal(pw, w, h)
    ph = w <= 560
    try:
        # --- default = active account (main) · Month
        check(f"{tag} A: default = active account (Main) and Month; switch shows Main · Family · Both", js(page, "()=>lrSwCur('journal')") == "main" and js(page, "()=>LR5.per") == "month" and js(page, "()=>[...document.querySelectorAll('[data-lr-sw=\"journal\"] button')].map(b=>b.innerText.trim().replace(/\\s+/g,' '))") == ["M Main", "F Family", "Both"])
        k = kpis(page)
        # main Nov by hand: x1 −381.99 USD + n1 +200 USD + b1 −297 USD + a1 −20 USD (×33) + p1 +1,000 THB = −15,466.67 THB · R −1.29929+0.4−1.0−0.2 = −2.1 · 5 trades
        check(f"{tag} B: Main · Result = −฿15.5k · −2.1R · 5 trades", k["result"]["big"] == "−฿15.5k" and k["result"]["sub"] == "−2.1R · 5 trades", k["result"])
        if not ph:
            # wins NVDA + PTT = 2/5 = 40% · avg R win (+0.4, PTT has no stop) = +0.4 · loss (−1.299, −1.0, −0.2)/3 = −0.833 → −0.8
            check(f"{tag} B: Main · win rate 40% · win +0.4R · loss −0.8R", k["win"]["big"] == "40%" and k["win"]["sub"] == "win +0.4R · loss −0.8R", k["win"])
            check(f"{tag} B: Main · followed 4 / 5 · 1 discretionary exit", k["followed"]["big"] == "4 / 5" and "1 discretionary exit" in k["followed"]["sub"], k["followed"])
            check(f"{tag} B: Main · not taken 4 (2 hesitated · 1 missed · 1 other)", k["nottaken"]["big"] == "4" and k["nottaken"]["sub"] == "2 hesitated · 1 missed · 1 other", k["nottaken"])
        else:
            check(f"{tag} B: Main · phone cards Result / Followed / Not taken / To review", k["followed"]["big"] == "4 / 5" and k["nottaken"]["big"] == "4" and k["nottaken"]["sub"] == "2 hesitated" and "win rate 40%" in k["followed"]["sub"], k)
        check(f"{tag} B: Main · to review = 1 (XAU has no reason; the others have a review or an exit tag)", k["toreview"]["big"] == "1", k["toreview"])
        rs = rows(page)
        check(f"{tag} B: Main · 5 rows, newest first (XAU 17 · AMD 16 · PTT 14 · NVDA 13 · BTC 12), Oct / Aug trades excluded", [x["k"].split(":")[1] for x in rs] == ["x1", "a1", "p1", "n1", "b1"], [x["k"] for x in rs])
        rm = {x["k"].split(":")[1]: x["t"] for x in rs}
        check(f"{tag} B: R on the planned stop: XAU −1.3R · BTC −1.0R · NVDA +0.4R", "−1.3R" in rm["x1"] and "−1.0R" in rm["b1"] and "+0.4R" in rm["n1"], {k_: rm[k_][:60] for k_ in ("x1", "b1", "n1")})
        check(f"{tag} B: moved-stop trade (planned stop 90, moved to 98) reads −0.2R, not −1.0R", "−0.2R" in rm["a1"] and "−1.0R" not in rm["a1"], rm["a1"])
        check(f"{tag} B: no stored original stop → R '—' with a tooltip", "—" in rm["p1"] and js(page, "()=>{ const r = document.querySelector('[data-lr5-row$=\":p1\"] .lr5-r, [data-lr5-row$=\":p1\"] b.lr5-r'); return r ? r.title : ''; }").startswith("No original stop"), rm["p1"])
        check(f"{tag} B: P&L in the trade's currency (XAU −$382 · PTT +฿1.0k)", "−$382" in rm["x1"] and "+฿1.0k" in rm["p1"], [rm["x1"], rm["p1"]])
        check(f"{tag} B: plan marks: NVDA × Early exit · others ✓ Followed" if not ph else f"{tag} B: plan marks: NVDA ✗ early exit", ("× Early exit" in rm["n1"] if not ph else "✗ early exit" in rm["n1"]) and ("✓" in rm["b1"]), [rm["n1"], rm["b1"]])
        # --- Both
        pick(page, "journal", "both")
        k = kpis(page); rs = rows(page)
        # + s1 +19,200 THB · f1 −2,000 THB → 1,733.33 · R −0.69929 → −0.7R · 7 trades
        check(f"{tag} Both: Result = sum of both accounts in THB (+฿1.7k · −0.7R · 7 trades)", k["result"]["big"] == "+฿1.7k" and k["result"]["sub"] == "−0.7R · 7 trades", k["result"])
        check(f"{tag} Both: 7 rows, one per position, both accounts' pills (M and F)", len(rs) == 7 and js(page, "()=>[...new Set([...document.querySelectorAll('[data-lr5-row] .lr-acc')].map(e=>e.dataset.lrAcc))].sort().join()") == "F,M", len(rs))
        rm = {x["k"].split(":")[1]: x["t"] for x in rs}
        check(f"{tag} Both: each row keeps its own currency (S50 +฿19.2k · CPALL −฿2.0k · XAU −$382)", "+฿19.2k" in rm["s1"] and "−฿2.0k" in rm["f1"] and "−$382" in rm["x1"], [rm["s1"], rm["f1"]])
        if not ph:
            check(f"{tag} Both: win rate 43% (3 of 7) · avg R win +1.4R · loss −0.9R · followed 6 / 7", k["win"]["big"] == "43%" and k["win"]["sub"] == "win +1.4R · loss −0.9R" and k["followed"]["big"] == "6 / 7", [k["win"], k["followed"]])
            check(f"{tag} Both: not taken 6 = 3 hesitated · 1 missed · 1 invalidated · 1 other", k["nottaken"]["big"] == "6" and k["nottaken"]["sub"] == "3 hesitated · 1 missed · 1 invalidated · 1 other", k["nottaken"])
        # Both does not change the stored accounts
        check(f"{tag} Both: the switch never changed the active account or wrote anything", js(page, "()=>acctActive") == "main")
        pick(page, "journal", "fam"); k = kpis(page)
        check(f"{tag} Family: S50 +19,200 − CPALL 2,000 = +฿17.2k · +1.4R · 2 trades", k["result"]["big"] == "+฿17.2k" and k["result"]["sub"] == "+1.4R · 2 trades", k["result"])
        pick(page, "journal", "main")
        # --- period filters
        counts = {}
        for per in ("week", "month", "quarter", "all"):
            setp(page, "per", per); counts[per] = len(rows(page))
        check(f"{tag} C: period filters (Main): Week 1 (XAU) · Month 5 · Quarter 6 (+Oct) · All 9 (+Aug: GE · CAT scale-out = 1 row · UBER)", counts == {"week": 1, "month": 5, "quarter": 6, "all": 9}, counts)
        setp(page, "per", "week"); k = kpis(page)
        check(f"{tag} C: Week · not taken counts only 17–23 Nov (LLY 'thesis' → 1 other)", k["nottaken"]["big"] == "1", k["nottaken"])
        setp(page, "per", "all"); k = kpis(page)
        check(f"{tag} C: All · not taken includes September (5 = 3 hesitated … wait main only: GE · CAT · OLD hesitated · TSLA missed · LLY other)", k["nottaken"]["big"] == "5", k["nottaken"])
        setp(page, "per", "all"); rs9 = {x["k"].split(":")[1]: x for x in rows(page)}
        check(f"{tag} B: scale-out legs are ONE row on the blended R (+1.5R) · off-plan trade reads × Off plan", "+1.5R" in rs9["sg2"]["t"] and ("off plan" in rs9["u1"]["t"].lower()), [rs9["sg2"]["t"], rs9["u1"]["t"]])
        setp(page, "per", "month")
        # --- port filters
        pick(page, "journal", "both")
        pc = {}
        for p_ in ("MMT", "COMP", "SAT", "all"):
            setp(page, "port", p_); pc[p_] = len(rows(page))
        check(f"{tag} C: port filters (Both · Month): MMT 4 · COMP 0 · SAT 3 · All 7", pc == {"MMT": 4, "COMP": 0, "SAT": 3, "all": 7}, pc)
        setp(page, "port", "SAT"); k = kpis(page)
        # SAT: x1 −381.99 · b1 −297 (USD ×33) + s1 +19,200 THB = −12,605.67 − 9,801 + 19,200 = −3,206.67
        check(f"{tag} C: SAT stats = XAU + BTC + S50 → −฿3.2k · 3 trades", k["result"]["big"] == "−฿3.2k" and k["result"]["sub"].endswith("3 trades"), k["result"])
        setp(page, "port", "COMP"); check(f"{tag} C: empty state when nothing matches", js(page, "()=>!!document.querySelector('[data-lr5-empty]')"))
        setp(page, "port", "all"); pick(page, "journal", "main")
        # --- Not taken list
        if ph:
            js(page, "()=>document.querySelector('[data-lr5-ntl]').click()"); page.wait_for_timeout(250)
            nt = js(page, "()=>[...document.querySelectorAll('[data-lr5-nt-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
            js(page, "()=>lr5SheetClose()")
        else:
            js(page, "()=>{ document.querySelector('[data-lr5-nt]').open = true; }"); page.wait_for_timeout(150)
            nt = js(page, "()=>[...document.querySelectorAll('[data-lr5-nt-row]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} B: Not taken (4) opens the RE4 list: GE Hesitated · CAT Hesitated · TSLA Missed · LLY Thesis or news changed", len(nt) == 4 and any("GE" in x and "Hesitated" in x for x in nt) and any("TSLA" in x and "Missed" in x for x in nt), nt)
        # --- review round trip
        before = json.dumps(C.js(page, "()=>getBook('fam').trades.map(t=>t.review||null)"))
        js(page, "()=>lr5Pick('main:x1')"); page.wait_for_timeout(250)
        rv = js(page, "()=>(document.querySelector('[data-lr5-review]')||{innerText:''}).innerText.replace(/\\s+/g,' ')")
        check(f"{tag} C: review shows Planned vs Actual (stop 2,628 → 2,623.81 gap · −1.3R) and the planned-stop note (1R = 14)", "2,628" in rv and "(gap)" in rv and "−1.3R" in rv and "1R = 14" in rv and "never the moved one" in rv, rv[:300])
        check(f"{tag} C: review has the four reason chips + optional lesson + Save review", js(page, "()=>[...document.querySelectorAll('[data-lr5-why-btn]')].map(b=>b.innerText).join('|')") == "Planned exit|Stop|Gap / slippage|Discretionary" and js(page, "()=>!!document.querySelector('[data-lr5-lesson]') && !!document.querySelector('[data-lr5-save]')"))
        js(page, "()=>document.querySelector('[data-lr5-why-btn=\"gap\"]').click()"); page.wait_for_timeout(100)
        js(page, "()=>{ const t = document.querySelector('[data-lr5-lesson]'); t.value = 'Do not hold through the NFP gap'; t.dispatchEvent(new Event('input', {bubbles:true})); }")
        js(page, "()=>document.querySelector('[data-lr5-save]').click()"); page.wait_for_timeout(500)
        st = js(page, "()=>getBook('main').trades.find(t=>t.id==='x1').review")
        check(f"{tag} C: save writes review {{why, lesson, at}} on the trade", st and st["why"] == "gap" and st["lesson"] == "Do not hold through the NFP gap" and st["at"], st)
        db = P38.dump(page)["users/testuid"]["books"]["main"]["trades"]
        pst = [t for t in db if t["id"] == "x1"][0].get("review")
        check(f"{tag} C: …and it is persisted to the account book (round trip)", pst and pst["why"] == "gap" and pst["lesson"].startswith("Do not hold"), pst)
        check(f"{tag} C: other trades / the other account are untouched", json.dumps(C.js(page, "()=>getBook('fam').trades.map(t=>t.review||null)")) == before and js(page, "()=>getBook('main').trades.filter(t=>t.review).length") == 2)
        k = kpis(page); rm = {x["k"].split(":")[1]: x["t"] for x in rows(page)}
        check(f"{tag} C: after saving, To review = 0 and the row shows 'Gap / slippage'", k["toreview"]["big"] == "0" and "Gap / slippage" in rm["x1"], [k["toreview"], rm["x1"]])
        # Both: save goes to the trade's own account
        pick(page, "journal", "both"); js(page, "()=>lr5Pick('fam:f1')"); page.wait_for_timeout(200)
        js(page, "()=>document.querySelector('[data-lr5-why-btn=\"planned\"]').click()"); js(page, "()=>document.querySelector('[data-lr5-save]').click()"); page.wait_for_timeout(400)
        check(f"{tag} C: in Both, saving a Family row writes to the Family book only", js(page, "()=>getBook('fam').trades.find(t=>t.id==='f1').review.why") == "planned" and js(page, "()=>getBook('main').trades.filter(t=>t.review).length") == 2)
        pick(page, "journal", "main")
        # --- Thai · overflow · one line per row
        js(page, "()=>{ document.getElementById('lr5Det').open = true; }"); page.wait_for_timeout(250)
        th = js(page, THAI)
        check(f"{tag} D: no Thai characters in #tabJournal (Details open)", not th, th[:8])
        js(page, "()=>{ document.getElementById('lr5Det').open = false; }")
        ov = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} D: no horizontal page overflow", ov <= 1, ov)
        if ph:
            ls = js(page, "()=>[...document.querySelectorAll('.lr5-pr .lr5-l1,.lr5-pr .lr5-l2')].map(e=>Math.round(e.getBoundingClientRect().height))")
            hs = [x["h"] for x in rows(page)]
            check(f"{tag} D: phone rows are two single lines (each line ≤ 26px · row ≤ 72px)", ls and max(ls) <= 26 and max(hs) <= 72, [max(ls), max(hs)])
        else:
            hs = [x["h"] for x in rows(page)]
            check(f"{tag} D: desktop rows are one line (≤ 56px)", hs and max(hs) <= 56, hs)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 740)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY {len(results) - len(bad)}/{len(results)} pass · {len(bad)} fail")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
