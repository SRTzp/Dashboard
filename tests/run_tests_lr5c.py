#!/usr/bin/env python3
"""LR5c — Port tab: household total = sum of the accounts (฿) · holdings by hand (shared NVDA = both accounts, S50 = notional, Thai stock) · open risk per account = Today's ·
futures leverage = Today's (hidden with no futures) · % of household: stock rows + cash = 100 ±0.5 · Main / Family views · More keeps the old sections · no Thai in the new block · no overflow 360/390/1440.
Fixture: tests/lr5c_common.py. Run: python3 tests/run_tests_lr5c.py"""
import sys
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import lr5c_common as C

THAI = """()=>{ const out = []; const w = document.createTreeWalker(document.getElementById('lr5cHost'), NodeFilter.SHOW_TEXT); let n; while(n = w.nextNode()){ if(/[\\u0E00-\\u0E3E\\u0E40-\\u0E7F]/.test(n.nodeValue)) out.push(n.nodeValue.trim().slice(0, 60)); }
  document.querySelectorAll('#lr5cHost [title],#lr5cHost [aria-label]').forEach(e=>['title', 'aria-label'].forEach(a=>{ const v = e.getAttribute(a); if(v && /[\\u0E00-\\u0E3E\\u0E40-\\u0E7F]/.test(v)) out.push('@' + a + ' ' + v.slice(0, 60)); })); return out; }"""
# by hand (fx 33): AAPL 30×200×33 = 198,000 · XAU 0.05×2640×100×33 = 435,600 · NVDA (11+5)×100×33 = 52,800 · PTT 3,000×33 = 99,000 · S50 notional 4×900×200 = 720,000
HAND = {"AAPL": 198000, "XAUUSD": 435600, "NVDA": 52800, "PTT.BK": 99000, "S50": 720000}
# stops: AAPL 10×30×33 = 9,900 · XAU 40×0.05×100×33 = 6,600 · NVDA 5×11×33 + 5×5×33 = 2,640 · PTT 3×3,000 = 9,000 · S50 20×4×200 = 16,000
STOP = {"AAPL": 9900, "XAUUSD": 6600, "NVDA": 2640, "PTT.BK": 9000, "S50": 16000}


def run(pw, w, h):
    tag = "[%s]" % w
    ph = w <= 560
    b, page, pe = C.open_port(pw, w, h)
    try:
        sw = js(page, "()=>[...document.querySelectorAll('[data-lr-sw=\"port\"] button')].map(b=>b.innerText.trim().replace(/\\s+/g,' '))")
        check(f"{tag} A: switch Main · Family · Both from the shared LR5b switch, default Both", sw == ["M Main", "F Family", "Both"] and js(page, "()=>lrSwCur('port')") == "both", sw)
        D = js(page, "()=>{ const D = lr5cData(); return {total:D.total, rows:D.rows.map(r=>({sym:r.sym, thb:r.thb, risk:r.risk, fut:r.fut})), E:D.sel.map(x=>x.E)}; }")
        check(f"{tag} B: household total = sum of the accounts' equity in ฿ (card shows it, bar M / F)", D["total"] == sum(D["E"]) and js(page, "()=>document.querySelector('[data-lr5c-total]').innerText") == js(page, "(t)=>lr5cFmt(t, '฿')", D["total"]) and js(page, "()=>document.querySelectorAll('[data-lr5c-bar]>div').length") == 2, D["total"])
        got = {r["sym"]: round(r["thb"]) for r in D["rows"]}
        check(f"{tag} B: holdings in ฿ by hand — shared NVDA = Main + Family, S50 = notional, XAU / AAPL in USD × fx, PTT in ฿", got == HAND, got)
        check(f"{tag} B: sorted by total value (S50 · XAU · AAPL · PTT · NVDA)", [r["sym"] for r in D["rows"]] == ["S50", "XAUUSD", "AAPL", "PTT.BK", "NVDA"], [r["sym"] for r in D["rows"]])
        check(f"{tag} B: if stopped by hand (NVDA ฿2,640 · S50 ฿16,000 on the per-point basis)", {r["sym"]: round(r["risk"]) for r in D["rows"]} == STOP, {r["sym"]: round(r["risk"]) for r in D["rows"]})
        rows = js(page, "()=>[...document.querySelectorAll('[data-lr5c-row]')].map(r=>({k:r.dataset.lr5cRow, t:r.innerText.replace(/\\s+/g,' ').trim(), h:Math.round(r.getBoundingClientRect().height), lines:r.children.length}))")
        rm = {r["k"]: r["t"] for r in rows}
        check(f"{tag} B: shared NVDA shows #11 (Main) and #5 (Family); S50 labelled notional; PTT is a Thai ticker row", "#11" in rm["NVDA"] and "#5" in rm["NVDA"] and "notional" in rm["S50"] and "#3,000" in rm["PTT.BK"], rm)
        check(f"{tag} B: stop shown in red with a minus (−฿16.0k · −฿2.6k)", "−฿16.0k" in rm["S50"] and "−฿2.6k" in rm["NVDA"], [rm["S50"], rm["NVDA"]])
        if ph:
            check(f"{tag} B: phone rows are 2 lines (ticker·tag·total / qty·stop) and ≤ 76px", all(r["lines"] == 2 and r["h"] <= 76 for r in rows), [(r["k"], r["lines"], r["h"]) for r in rows])
        else:
            pcts = js(page, "()=>{ const o = {}; document.querySelectorAll('tbody [data-lr5c-row]').forEach(r=>o[r.dataset.lr5cRow] = parseFloat(r.querySelector('[data-lr5c-p]').innerText)); o.__cash = parseFloat(document.querySelector('[data-lr5c-cashrow] [data-lr5c-p]').innerText); return o; }")
            cash = pcts.pop("__cash"); s = sum(v for k, v in pcts.items() if k != "S50") + cash
            check(f"{tag} B: % of household — stock rows + cash = 100 ±0.5 (S50 is notional, listed apart)", abs(s - 100) <= 0.5, (s, pcts, cash))
        # open risk = Today's (same function) and the card shows each account's own value
        risk = js(page, "()=>({m:re1Pct(lr2OpenRisk('main')), f:re1Pct(lr2OpenRisk('fam')), card:document.querySelector('[data-lr5c-riskleg]').innerText.replace(/\\s+/g,' '), cap:RiskEngine.POLICY.active.weeklyPct})")
        check(f"{tag} B: open risk — each account's own % of {risk['cap']}% (never combined)", risk["m"] in risk["card"] and risk["f"] in risk["card"] and risk["card"].count("of 3%") == 2, risk)
        # futures = Today's
        lev = js(page, "()=>document.querySelector('[data-lr5c-lev=\"fam\"]').innerText.trim()")
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(600)
        today = js(page, "()=>({fut:[...document.querySelectorAll('[data-lr2-fut]')].map(e=>e.innerText.trim()), risk:[...document.querySelectorAll('[data-lr2-orisk]')].map(e=>e.innerText.replace(/\\s+/g,' '))})")
        check(f"{tag} B: futures leverage equals Today's ({lev})", lev in today["fut"], [lev, today])
        check(f"{tag} B: open risk % equals the Today header's", all(v in " ".join(today["risk"]) for v in (risk["m"], risk["f"])), [risk, today["risk"]])
        js(page, "()=>switchTab('mix')"); page.wait_for_timeout(500)
        # views
        js(page, "()=>lrSwPick('port','main')"); page.wait_for_timeout(300)
        r1 = js(page, "()=>[...document.querySelectorAll('[data-lr5c-row]')].map(r=>r.dataset.lr5cRow)")
        t1 = js(page, "()=>document.querySelector('[data-lr5c-total]').innerText")
        check(f"{tag} C: Main view — only Main's positions, total in Main's currency ($), no futures card, no household note", r1 == ["XAUUSD", "AAPL", "NVDA"] and t1.startswith("$") and js(page, "()=>!document.querySelector('[data-lr5c-card=\"fut\"]') && !document.querySelector('[data-lr5c-note]')"), [r1, t1])
        js(page, "()=>lrSwPick('port','fam')"); page.wait_for_timeout(300)
        r2 = js(page, "()=>[...document.querySelectorAll('[data-lr5c-row]')].map(r=>r.dataset.lr5cRow)")
        check(f"{tag} C: Family view — Family's positions + the futures card", r2 == ["S50", "PTT.BK", "NVDA"] and js(page, "()=>!!document.querySelector('[data-lr5c-card=\"fut\"]')"), r2)
        js(page, "()=>lrSwPick('port','both')"); page.wait_for_timeout(300)
        # More keeps the old sections
        more = js(page, "()=>{ const d = document.querySelector('[data-lr5c-more]'); d.open = true; return {sum:!!d.querySelector('#mixSummary'), body:!!d.querySelector('#mixBody'), risk:!!d.querySelector('#bdPortRisk'), txt:d.querySelector('#mixBody').innerText.length > 20}; }")
        check(f"{tag} C: More ▾ keeps the existing summary, risk blocks and per-account sections", more["sum"] and more["body"] and more["risk"] and more["txt"], more)
        js(page, "()=>{ document.querySelector('[data-lr5c-more]').open = false; }")
        th = js(page, THAI)
        check(f"{tag} D: no Thai in the new Port block", th == [], th)
        ov = js(page, "()=>({doc:document.documentElement.scrollWidth - document.documentElement.clientWidth, host:(()=>{ const h = document.getElementById('lr5cHost'); return [...h.querySelectorAll('.lr5c-card,.lr5c-list,.lr5-hd')].filter(e=>e.scrollWidth > e.clientWidth + 1).length; })()})")
        check(f"{tag} D: no horizontal overflow", ov["doc"] <= 0 and ov["host"] == 0, ov)
        if w <= 390:
            pb = js(page, "()=>{ const e = [...document.querySelectorAll('button')].find(x=>x.offsetParent && /Plan/.test(x.innerText) && x.getBoundingClientRect().top < 80 && x.getBoundingClientRect().left > 150); if(!e) return null; const r = e.getBoundingClientRect(); return {l:r.left, r:r.right, w:innerWidth}; }")
            check(f"{tag} D: Port ＋ Plan button fits inside the viewport", pb is not None and 0 <= pb["l"] and pb["r"] <= pb["w"], pb)
        check(f"{tag} no page errors", not pe, pe)
    finally:
        b.close()


def run_nofut(pw):
    b, page, pe = C.open_port(pw, 1440, 900, doc_=C.doc(with_fut=False))
    try:
        check("[nofut] futures card hidden when no futures are open (2 cards)", js(page, "()=>!document.querySelector('[data-lr5c-card=\"fut\"]') && document.querySelectorAll('.lr5c-cards>.lr5c-card').length") == 2)
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 780)):
            run(pw, w, h)
        run_nofut(pw)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY {len(results) - len(bad)}/{len(results)} pass · {len(bad)} fail")
    sys.exit(1 if bad else 0)
