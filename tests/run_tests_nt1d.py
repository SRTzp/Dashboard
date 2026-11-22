#!/usr/bin/env python3
"""NT1d (v6, trimmed by NT2) — A `.nt1-x` fix · B My idea detail 2 columns (+ Enlarge) · B2 price ruler / card / list / header · C Today “no next step” · D sheet + level hit / invalidated + D2 auto-copy + tvAlert reset · E Settings hints.
Run: python3 tests/run_tests_nt1d.py   (set NT1D_SHOTS=1 to write docs/screenshots/nt1d-*.png)"""
import sys, os, base64, subprocess, zlib, struct
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import nt1_common as N
import run_tests_nt1 as T
import run_tests_nt1b as B

TXT, VIS, OVER, DOC = B.TXT, B.VIS, B.OVER, B.DOC
HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "..", "docs", "screenshots")
GOLD = "Gold buy zone"
LINE = "XAU ≤ 3,350 · " + GOLD
INVL = "XAU ≤ 3,250 INVALID · " + GOLD


def png(w, h):
    raw = b"".join(b"\x00" + b"\xff" * (w * 3) for _ in range(h))
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b"")


def shot(page, name):
    if os.environ.get("NT1D_SHOTS"):
        os.makedirs(SHOTS, exist_ok=True); page.screenshot(path=os.path.join(SHOTS, "nt1d-%s.png" % name))


def stub(page):
    page.route("https://s3.tradingview.com/**", lambda r: r.fulfill(status=200, content_type="image/png", body=png(470, 372)))


def clip(page, mode="ok"):
    page.evaluate("""(mode)=>{ window.__clip = ''; window.__exec = 0;
      Object.defineProperty(navigator, 'clipboard', {configurable:true, value:{writeText:t=>{ if(mode==='deny') return Promise.reject(new Error('denied')); window.__clip = t; return Promise.resolve(); }}});
      if(mode==='deny') document.execCommand = ()=>false; }""", mode)


def now_iso(page, delta_h=0):
    return js(page, "(d)=>new Date(Date.now() + d * 3600000).toISOString()", delta_h)


def sheet_save(page):
    page.click("[data-nt1-save]"); page.wait_for_timeout(350)


def open_edit(page, i):
    js(page, "(i)=>nt1SheetOpen({id:i})", i); page.wait_for_timeout(200)


def lr(page, sel):   # left % of a ruler part
    return js(page, "(s)=>{ const e = document.querySelector(s); return e ? parseFloat(e.style.left) : null; }", sel)


def sheet_fill(page, subj="sat:XAU", title=GOLD, view="bull", next_="Watch H4 close above 3400", level="3350", adir="down", inv="3250", last="3410"):
    page.select_option("#nt1fSubj", subj)
    if view: page.click('[data-nt1-fv="%s"]' % view)
    page.fill("#nt1fTitle", title); page.fill("#nt1fNext", next_)
    if level: page.fill("#nt1fLevel", level)
    if adir: page.click('[data-nt1d-for="alert"][data-nt1d-dir="%s"]' % adir)
    if inv: page.fill("#nt1fInv", inv)
    if last: page.fill("#nt1fLast", last)


def part_desktop(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        stub(page); t0 = B.td(page); B.quiet_fixture_ai(page); clip(page)
        tv = "https://www.tradingview.com/x/AbC123/"
        # ───── A · the text rows are no longer squeezed into the 44px close button
        B.seed_ai(page, "ai-rc", "Recheck theme with a long name", "need_evidence", recheck=B.add(t0, 5))
        T.to_ai(page); js(page, "()=>ideaOpen('ai-rc')"); page.wait_for_timeout(250)
        js(page, "()=>document.querySelector('[data-nt1-fold=\"evd\"]>summary').click()"); page.wait_for_timeout(250)
        a = js(page, """()=>{ const n = document.querySelector('.nt1-note'); if(!n) return null; const r = n.getBoundingClientRect(), s = document.querySelector('[data-nt1-fold="evd"]>summary').getBoundingClientRect();
            return {w:Math.round(r.width), cw:getComputedStyle(n).width, overlap:!(r.bottom <= s.top + 1 || r.top >= s.bottom - 1 || r.right <= s.left || r.left >= s.right), txt:n.innerText}; }""")
        check(f"{tag} A Recheck row is > 300px wide, computed width ≠ 44px, does not overlap the fold header", a and a["w"] > 300 and a["cw"] != "44px" and not a["overlap"], a)
        shot(page, "evidence-fold")
        B.seed_my(page, {"x0": B.mkmy(1, ("sat", "XAU"), GOLD, B.add(t0, -1), B.add(t0, 4), next="Watch H4 close above 3400", level=3340)})
        T.to_my(page, "x0"); js(page, "()=>nt1SheetOpen({id:'x0'})"); page.wait_for_timeout(200)
        xb = js(page, "()=>{ const r = document.querySelector('.nt1-sh .nt1-x').getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; }")
        check(f"{tag} A the sheet ✕ stays 44×44", xb == [44, 44], xb)
        page.click("[data-nt1-cancel]"); page.wait_for_timeout(150)

        # ───── NT2: the B / B2 / D / invalid / C blocks of NT1d (Next step card · Alert + Invalid rows · NEXT sheet · rank 3 · 440px list) assert UI that NT2 replaced — they now live, rewritten for Scenarios, in run_tests_nt2.py
        t0 = B.td(page)
        gone = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], capture_output=True, text=True, cwd=os.path.join(HERE, "..")).stdout.split()
        check(f"{tag} D display + alerts only: no sizing / engine file changed · lastPx / invLevel not referenced in them", not any(f.endswith(("risk-engine.js", "core-size.js", "ps1-size.js", "pos-view.js", "re1-adapter.js")) for f in gone) and all("lastPx" not in open(os.path.join(HERE, "..", f), encoding="utf-8").read() and "invLevel" not in open(os.path.join(HERE, "..", f), encoding="utf-8").read() for f in ("risk-engine.js", "core-size.js", "ps1-size.js", "pos-view.js", "re1-adapter.js")), gone)

        # ───── E · Settings hints
        e1 = js(page, """()=>[...document.querySelectorAll('.ps1Rg')].map(e=>{ const s = getComputedStyle(e); return [s.fontFamily.split(',')[0].replace(/["']/g, ''), s.fontSize, s.textOverflow, s.fontFamily.includes('mono')]; })""")
        check(f"{tag} E `.ps1Rg` hints: Inter · 12px · no ellipsis · no mono", e1 and all(x[0] == "Inter" and x[1] == "12px" and x[2] != "ellipsis" and not x[3] for x in e1), e1)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def part_phone(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h, my_docs=False, notes=False)
    try:
        stub(page); t0 = B.td(page); B.quiet_fixture_ai(page)
        dd = dict(B.mkmy(1, ("sat", "XAU"), GOLD, B.add(t0, -1), B.add(t0, 4), view="bull", next="Watch H4", level=3350, invLevel=3250, ang={"tech": "Support", "sent": "Down 11%"}, chart="https://www.tradingview.com/x/AbC123/", plan="Old plan"), levelDir="down", invDir="down", lastPx={"v": 3410, "at": now_iso(page)})
        B.seed_my(page, {"x1": dd})
        T.to_my(page); page.wait_for_timeout(250)
        nb = js(page, "()=>{ const r = document.querySelector('[data-nt1-new]').getBoundingClientRect(); return [r.left >= 0, r.right <= innerWidth, r.width > 0]; }")
        check(f"{tag} B2 `+ Idea` is fully inside the viewport", all(nb), nb)
        e1 = js(page, "()=>[...document.querySelectorAll('.ps1Rg')].map(e=>{ const s = getComputedStyle(e); return [s.fontFamily.split(',')[0].replace(/[\"']/g, ''), s.textOverflow]; })")
        check(f"{tag} E `.ps1Rg` hints: Inter · no ellipsis", e1 and all(x[0] == "Inter" and x[1] != "ellipsis" for x in e1), e1)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        part_desktop(pw, 1440, 900)
        part_phone(pw, 390, 844)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY nt1d: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
