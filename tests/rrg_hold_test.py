#!/usr/bin/env python3
"""RRG-HOLD — etfHoldingsUrl for every RRG_SYMS ETF · speed-list ticker links · chart popover open/close · sector rows link new tab.
Run: python3 tests/rrg_hold_test.py"""
import sys, re
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import lr4_common as C

def run(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = C.open_flow(pw, w, h)
    try:
        u = js(page, "()=>RRG_SYMS.map(x=>[x.s, etfHoldingsUrl(x.s)])")
        check(f"{tag} URL: every RRG_SYMS ETF ({len(u)}) gives stockanalysis.com/etf/<lower>/holdings/", len(u) == 23 and all(v == f"https://stockanalysis.com/etf/{s.lower()}/holdings/" for s, v in u), u[:2])
        bad = js(page, "()=>[etfHoldingsUrl(''), etfHoldingsUrl(null), etfHoldingsUrl('TH'), etfHoldingsUrl('a b')]")
        check(f"{tag} URL: junk input → '' (TH has none)", bad[0] == "" and bad[1] == "" and bad[3] == "", bad)
        if w > 600:
            tk = js(page, "()=>[...document.querySelectorAll('[data-lr4-speed] a.rh-tk')].map(a=>[a.textContent, a.getAttribute('href'), a.target, a.rel])")
            check(f"{tag} speed list: tickers are links (new tab, noopener)", len(tk) > 0 and all(t[2] == "_blank" and "noopener" in t[3] and t[1] == f"https://stockanalysis.com/etf/{t[0].lower()}/holdings/" for t in tk), tk[:2])
        # chart popover
        sym = js(page, "()=>document.querySelector('[data-lr4-sec]').dataset.lr4Sec")
        page.evaluate("(s)=>document.querySelector('[data-lr4-sec=\"'+s+'\"] .rh-hit').dispatchEvent(new MouseEvent('click',{bubbles:true}))", sym)
        pop = js(page, "()=>{ const p = document.getElementById('rhPop'); if(!p) return null; const a = p.querySelector('a'); return {sym:p.dataset.rhPop, txt:p.innerText, href:a && a.href, t:a && a.target, rel:a && a.rel, inView:p.getBoundingClientRect().right <= innerWidth && p.getBoundingClientRect().left >= 0}; }")
        check(f"{tag} popover opens on dot with full name + Holdings ↗ (new tab)", bool(pop) and "Holdings" in pop["txt"] and pop["t"] == "_blank" and "noopener" in pop["rel"] and pop["href"].endswith(f"/{sym.lower()}/holdings/") and pop["inView"], pop)
        page.keyboard.press("Escape")
        check(f"{tag} popover closes on Esc", js(page, "()=>!document.getElementById('rhPop')"))
        page.evaluate("(s)=>document.querySelector('[data-lr4-lbl=\"'+s+'\"]')&&document.querySelector('[data-lr4-lbl=\"'+s+'\"]').dispatchEvent(new MouseEvent('click',{bubbles:true}))", sym)
        page.evaluate("()=>document.body.click()")
        check(f"{tag} popover closes on outside tap", js(page, "()=>!document.getElementById('rhPop')"))
        # sector rows
        n = js(page, """()=>{ const f = ffState(); const rows = f.rrg.rowsD; const x = rows[0]; const h = sdRowHtml(x, 'D', SD_QLBL), d = sdBodyHtml(x);
          return {row:/data-rh-link="/.test(h) && /target="_blank"/.test(h), det:/data-rh-link="/.test(d), all:rows.every(r=>/data-rh-link=/.test(sdRowHtml(r,'D',SD_QLBL)))}; }""")
        check(f"{tag} sector row + detail carry Holdings ↗", n["row"] and n["det"] and n["all"], n)
        check(f"{tag} no page errors", not pe, pe[:2] if pe else None)
    finally:
        b.close()

def main():
    with sync_playwright() as pw:
        run(pw, 1440, 900); run(pw, 390, 844)
    bad = [r for r in results if not r[1]]
    print(f"PASS {len(results)-len(bad)} FAIL {len(bad)}")
    for r in bad: print(" -", r[0], "::", r[2])
    sys.exit(1 if bad else 0)
main()
