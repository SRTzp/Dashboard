#!/usr/bin/env python3
"""NT1d (v6) — A `.nt1-x` fix · B My idea detail 2 columns (+ Enlarge) · B2 price ruler / card / list / header · C Today “no next step” · D sheet + level hit / invalidated + D2 auto-copy + tvAlert reset · E Settings hints.
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

        # ───── B · 2 columns + B2 card / list / header
        dd = B.mkmy(1, ("sat", "XAU"), GOLD, B.add(t0, -1), B.add(t0, 4), view="bull", next="Watch H4 close above 3400", level=3350, ang={"tech": "Support 3290-3340", "sent": "Gold down 11%", "fund": "Central banks keep buying", "macro": "CPI Thursday"}, chart=tv, builtOn="en-idea-1", plan="My old plan text")
        dd.update({"levelDir": "down", "invLevel": 3250, "invDir": "down", "lastPx": {"v": 3410, "at": now_iso(page)}})
        B.seed_my(page, {"x1": dd, "x2": B.mkmy(2, ("market", "US"), "No chart idea", B.add(t0, -2), B.add(t0, 4), ang={"tech": "Breadth falling", "macro": "CPI"}, next="Read CPI", plan="Another old plan")})
        T.to_my(page, "x1"); page.wait_for_timeout(300)
        g = js(page, """()=>{ const q = s=>document.querySelector(s), r = e=>e.getBoundingClientRect(), c = r(q('[data-nt1-chartw]')), sd = r(q('[data-nt1-side]')), p = q('[data-nt1-detail]');
            return {cols:getComputedStyle(q('[data-nt1-r1]')).gridTemplateColumns.split(' ').length, left:c.right <= sd.left + 1, ch:Math.round(c.height), sh:Math.round(sd.height), cw:Math.round(c.width), sw:Math.round(sd.width),
              angs:[...document.querySelectorAll('[data-nt1-notes] [data-nt1-ang]')].map(x=>x.dataset.nt1Ang), cards:document.querySelectorAll('[data-nt1-notes]').length, plan:/old plan/i.test(p.innerText) || !!q('[data-nt1-ang="plan"]'), row2:!!q('.nt1-ang'),
              nx:!!q('[data-nt1-side] [data-nt1b-block]'), foot:!!q('[data-nt1-foot] [data-nt1-built]') && !!q('[data-nt1-foot] [data-nt1-review]'), checks:(p.innerText.match(/Check again/g) || []).length,
              noScroll:document.documentElement.scrollHeight <= innerHeight + 1, panel:p.scrollHeight <= p.clientHeight + 1 || (q('.nt1-det') && q('.nt1-det').scrollHeight <= q('.nt1-det').clientHeight + 1), fit:getComputedStyle(q('[data-nt1-chartw] img')).objectFit}; }""")
        check(f"{tag} B 2 columns: chart left (3fr) · Next step card + ONE white notes card right (2fr) · no row 2 · NO Plan anywhere in the detail", g["cols"] == 2 and g["left"] and g["cw"] > g["sw"] and g["angs"] == ["tech", "sent", "fund", "macro"] and g["cards"] == 1 and g["nx"] and not g["plan"] and not g["row2"], g)
        check(f"{tag} B chart ≥ 372 and stretches to the right column height · object-fit contain", g["ch"] >= 372 and g["ch"] >= g["sh"] - 1 and g["fit"] == "contain", g)
        check(f"{tag} B footer row: Built on left · review right · `Check again` appears once", g["foot"] and g["checks"] == 1, g)
        check(f"{tag} B fits 1440×900: no page scroll · detail does not need to scroll when filled", g["noScroll"] and g["panel"], g)
        shot(page, "watch-full")
        page.focus("[data-nt1-zoom]"); page.click("[data-nt1-zoom]"); page.wait_for_timeout(200)
        z = js(page, "()=>{ const m = document.querySelector('[data-nt1-zm]'); if(!m) return null; const i = m.querySelector('img'); return {tv:m.querySelector('[data-nt1-zm-tv]').innerText, maxw:getComputedStyle(i).maxWidth, maxh:getComputedStyle(i).maxHeight}; }")
        check(f"{tag} B ⤢ Enlarge opens the in-app large view: image ≤ 90vw/90vh · `↗ Open in TradingView` link", z and "Open in TradingView" in z["tv"] and z["maxw"] != "none" and z["maxh"] != "none", z)
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        check(f"{tag} B Esc closes it and focus returns to ⤢ Enlarge", not js(page, VIS, "[data-nt1-zm]") and js(page, "()=>document.activeElement.hasAttribute('data-nt1-zoom')"))
        page.click("[data-nt1-zoom]"); page.wait_for_timeout(150); page.mouse.click(5, 5); page.wait_for_timeout(150)
        check(f"{tag} B click outside closes it", js(page, "()=>!document.querySelector('[data-nt1-zm]')"))
        page.click("[data-nt1-zoom]"); page.wait_for_timeout(150); page.click("[data-nt1-zm-x]"); page.wait_for_timeout(150)
        check(f"{tag} B ✕ closes it", js(page, "()=>!document.querySelector('[data-nt1-zm]')") and js(page, "()=>document.activeElement.hasAttribute('data-nt1-zoom')"))
        T.to_my(page, "x2"); page.wait_for_timeout(250)
        n = js(page, """()=>{ const q = s=>document.querySelector(s); return {one:q('[data-nt1-r1]').classList.contains('one'), chart:!!q('[data-nt1-chartw]'), ang:[...document.querySelectorAll('[data-nt1-notes] [data-nt1-ang]')].map(x=>x.dataset.nt1Ang), plan:/another old plan/i.test(q('[data-nt1-detail]').innerText), cols:getComputedStyle(q('[data-nt1-r1]')).gridTemplateColumns.split(' ').length}; }""")
        check(f"{tag} B no chart → single column: Next step card on top, notes below · no Plan text", n["one"] and not n["chart"] and n["cols"] == 1 and n["ang"] == ["tech", "macro"] and not n["plan"], n)
        shot(page, "no-chart")
        js(page, "()=>{ document.querySelector('[data-nt1-my=\"x2\"] ~ *') }") if False else None
        page.click("[data-nt1-menu]"); page.click("[data-nt1-copy]"); page.wait_for_timeout(250)
        check(f"{tag} B stored `plan` text survives only in the Copy export", "Plan: Another old plan" in js(page, "()=>window.__nt1LastCopy"), js(page, "()=>window.__nt1LastCopy"))

        # ───── B2 · ruler
        T.to_my(page, "x1"); page.wait_for_timeout(200)
        rd = js(page, """()=>{ const B0 = '[data-nt1b-block] ', q = s=>document.querySelector(B0 + s), l = s=>{ const e = q(s); return e ? parseFloat(e.style.left) : null; };
            return {inv:l('[data-nt1r-tick="inv"]'), alert:l('[data-nt1r-tick="alert"]'), now:l('[data-nt1r-now]'), zone:q('[data-nt1r-zone]') ? [parseFloat(q('[data-nt1r-zone]').style.left), parseFloat(q('[data-nt1r-zone]').style.width)] : null,
              chip:q('[data-nt1r-chip]') && [q('[data-nt1r-chip]').innerText, q('[data-nt1r-chip]').className], top:q('[data-nt1-ruler] .top').innerText.replace(/\\s+/g,' '), lbl:[...document.querySelectorAll('[data-nt1b-block] [data-nt1r-lbl]')].map(x=>x.innerText.replace(/\\s+/g,' ').trim()), count:document.querySelectorAll('[data-nt1b-block] [data-nt1-ruler]').length,
              tvc:getComputedStyle(q('[data-nt1r-tick="inv"]')).backgroundColor, tac:getComputedStyle(q('[data-nt1r-tick="alert"]')).backgroundColor}; }""")
        check(f"{tag} B2 ruler (down/≤): Invalid tick < Alert tick < now dot, all inside 4–96 %, band between the two ticks · amber = Invalid, blue = Alert", rd["inv"] < rd["alert"] < rd["now"] <= 96 and rd["inv"] >= 4 and abs(rd["zone"][0] - rd["inv"]) < .1 and abs(rd["zone"][1] - (rd["alert"] - rd["inv"])) < .1 and rd["tvc"] == "rgb(217, 146, 26)" and rd["tac"] == "rgb(59, 79, 196)", rd)
        check(f"{tag} B2 ruler top line `Now 3,410 manual · …` + blue chip `1.8% to level` · labels `Invalid 3,250` / `Alert 3,350` on one line", rd["top"].startswith("Now 3,410 manual · ") and rd["chip"][0] == "1.8% to level" and "p-b" in rd["chip"][1] and rd["lbl"] == ["Invalid 3,250", "Alert 3,350"] and rd["count"] == 1, rd)
        T.to_my(page, "x1")
        up = dict(B.mkmy(3, ("stock", "MSFT"), "Up ruler", B.add(t0, -1), B.add(t0, 5), level=190, invLevel=182), levelDir="up", invDir="down")
        B.seed_my(page, {"up": up}); B.px(page, "MSFT", 191.4); T.to_my(page, "up"); page.wait_for_timeout(250)
        ru = js(page, """()=>{ const q = s=>document.querySelector('[data-nt1b-block] ' + s), l = s=>parseFloat(q(s).style.left); return {inv:l('[data-nt1r-tick="inv"]'), alert:l('[data-nt1r-tick="alert"]'), now:l('[data-nt1r-now]'), chip:q('[data-nt1r-chip]').innerText, cls:q('[data-nt1r-chip]').className, top:q('[data-nt1-ruler] .top').innerText.replace(/\\s+/g,' ')}; }""")
        check(f"{tag} B2 ruler (up/stock): Invalid < Alert < now · chip amber `above 190` · source `daily close`", ru["inv"] < ru["alert"] < ru["now"] <= 96 and ru["chip"] == "above 190" and "p-a" in ru["cls"] and "daily close" in ru["top"], ru)
        far = dict(B.mkmy(4, ("sat", "BTC"), "Close ticks", B.add(t0, -1), B.add(t0, 5), level=84000, invLevel=83500), levelDir="up", invDir="down", lastPx={"v": 120000, "at": now_iso(page)})
        B.seed_my(page, {"far": far}); T.to_my(page, "far"); page.wait_for_timeout(250)
        fd = js(page, "()=>({now:parseFloat(document.querySelector('[data-nt1b-block] [data-nt1r-now]').style.left), up:!!document.querySelector('[data-nt1b-block] .lbs.u [data-nt1r-lbl=\"alert\"]')})")
        check(f"{tag} B2 ticks closer than ~30 % → the Alert label moves above the track · `now` far away is clamped inside (≤ 96 %)", fd["up"] and fd["now"] <= 96, fd)
        # card: TV row + actions + Mark menu
        T.to_my(page, "x1"); page.wait_for_timeout(200)
        cd = js(page, """()=>{ const b = document.querySelector('[data-nt1b-block]'), tv = b.querySelector('[data-nt1d-tv]'), a = b.querySelector('.acts'); const t = tv.innerText.replace(/\\s+/g,' ');
            return {hdr:b.querySelector('[data-nt1d-hdr]').innerText, check:b.querySelector('[data-nt1d-check]').innerText, tv:t, acts:a.innerText.replace(/\\s+/g,' '), amb:b.classList.contains('amb'), border:getComputedStyle(a).borderTopWidth, nowrap:[...b.querySelectorAll('.nt1-lnk,.mk,.cp')].every(e=>getComputedStyle(e).whiteSpace === 'nowrap'), copyText:/Copy text/.test(b.innerText)}; }""")
        check(f"{tag} B2 card: `NEXT STEP` + `Check again` · ruler · ONE compact TV row `TV  Copy alert  Copy invalid  ✓ Set` · actions `Snooze 3 days  Done … Mark ▾` without a divider · `Copy text` renamed", cd["hdr"] == "NEXT STEP" and cd["check"].startswith("Check again") and cd["tv"] == "TV Copy alert Copy invalid ✓ Set" and cd["acts"].startswith("Snooze 3 days Done") and cd["acts"].endswith("Mark ▾") and cd["border"] == "0px" and cd["nowrap"] and not cd["copyText"] and not cd["amb"], cd)
        page.click("[data-nt1d-mark-btn]"); page.wait_for_timeout(120)
        mm = js(page, "()=>[...document.querySelectorAll('[data-nt1d-mark-menu] button')].map(b=>b.innerText)")
        page.keyboard.press("Escape"); page.wait_for_timeout(120)
        check(f"{tag} B2 Mark ▾ opens `Level hit · Invalidated` and Esc closes it", mm == ["Level hit", "Invalidated"] and js(page, "()=>!document.querySelector('[data-nt1d-mark-menu]')"), mm)
        # list rows
        T.to_my(page, "x1"); page.wait_for_timeout(200)
        lst = js(page, """()=>{ const rows = [...document.querySelectorAll('[data-nt1-my]')], bad = [];
            rows.forEach(r=>r.querySelectorAll('*').forEach(e=>{ if(e.getClientRects().length && getComputedStyle(e).textOverflow === 'ellipsis') bad.push(e.className || e.tagName); }));
            const r1 = document.querySelector('[data-nt1-my="x1"]'); const pills = rows.map(r=>r.querySelectorAll('[data-nt1b-pill]').length);
            return {bad, pills:Math.max(...pills), t2:r1.querySelector('.t2').innerText, hasAng:/Support 3290/.test(r1.innerText), l3:r1.querySelector('[data-nt1b-l3]').innerText.replace(/\\s+/g,' '), trail:!!r1.querySelector('.nt1b-trail')}; }""")
        check(f"{tag} B2 list rows: no ellipsis anywhere · Next step text is line 2 · line 3 = date + ONE status pill · the My-view summary is not in the row", lst["bad"] == [] and lst["pills"] <= 1 and lst["t2"] == "Watch H4 close above 3400" and not lst["hasAng"] and "1.8% to level" in lst["l3"] and not lst["trail"], lst)
        hd = js(page, """()=>{ const q = s=>document.querySelector(s), r = e=>e.getBoundingClientRect(), n = q('[data-nt1-new]'), f = q('[data-nt1-find]'), lt = q('[data-nt1-lt]'), h = q('[data-lr5-head]');
            return {newIn:!!n && r(n).right <= innerWidth && r(n).left >= 0 && r(n).width > 0, newInHead:h.contains(n), newInList:lt.contains(n), find:f && [f.innerText, Math.round(r(f).width), Math.round(r(f).height)], chips:[...lt.querySelectorAll('.nt1-chip')].map(c=>c.innerText.replace(/\\s+\\d+$/,'')), headRight:n && Math.round(innerWidth - r(n).right)}; }""")
        check(f"{tag} B2 header: `+ Idea` in the title row (dark, fully inside the viewport) · list top row = chips + 34px `⌕` icon button", hd["newIn"] and hd["newInHead"] and not hd["newInList"] and hd["find"] == ["⌕", 34, 34] and hd["chips"] == ["All", "Due", "Markets", "Stocks", "Sat", "Plan"], hd)

        # ───── D · sheet
        T.to_my(page); js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(250)
        s = js(page, """()=>{ const q = s=>document.querySelector(s), vis = e=>!!(e && e.checkVisibility() && e.getBoundingClientRect().width > 0), sh = q('[data-nt1-sheet]'), top = s=>Math.round(q(s).getBoundingClientRect().top);
            const fields = ['#nt1fSubj', '[data-nt1-fv="bull"]', '#nt1fTitle', '#nt1fChart', '#nt1fNext', '#nt1fCheck', '#nt1fLevel', '#nt1fInv', '#nt1fLast'].map(x=>vis(q(x)));
            return {fields, secs:[...sh.querySelectorAll('.nt1d-sec')].map(x=>x.innerText), order:top('#nt1fSubj') < top('#nt1fNext') && top('#nt1fNext') < top('[data-nt1d-pr]') && top('[data-nt1d-pr]') < top('[data-nt1d-more]'), plan:!!q('#nt1f-plan, [data-nt1-plan]') || /\\bPlan\\b/.test([...sh.querySelectorAll('label')].map(l=>l.innerText).join(' ')), tvcopy:/Copy level|I set the alert|Copy alert/.test(sh.innerText),
              foldOpen:q('[data-nt1d-more]').open, taVis:vis(q('#nt1f-tech')), alertSegs:[...sh.querySelectorAll('[data-nt1d-for="alert"]')].map(x=>[x.innerText, x.getAttribute('aria-pressed')]), invSegs:[...sh.querySelectorAll('[data-nt1d-for="inv"]')].map(x=>[x.innerText, x.getAttribute('aria-pressed')]), prev:q('[data-nt1d-prev]').innerText.trim()}; }""")
        check(f"{tag} D sheet = exactly 9 fields (About · My view · Title · Chart · Next step · Check again · Alert · Invalid · Last price) + `More notes` fold, order What → NEXT → PRICE ALERTS → More notes", all(s["fields"]) and s["secs"][:3] == ["NEXT", "PRICE ALERTS · optional", "MY NOTES · all optional"] and s["order"], s)
        check(f"{tag} D sheet: no Plan field · no Copy / `I set the alert` · `More notes` closed (fields hidden) · neither ≥ nor ≤ selected · no preview without numbers", not s["plan"] and not s["tvcopy"] and not s["foldOpen"] and not s["taVis"] and s["alertSegs"] == [["≥", "false"], ["≤", "false"]] and s["prev"] == "", s)
        page.select_option("#nt1fSubj", "stock:AVGO"); page.wait_for_timeout(80)
        check(f"{tag} D Last price hidden for a stock, shown for XAU", not js(page, VIS, "[data-nt1d-lastwrap]") and (page.select_option("#nt1fSubj", "sat:XAU") is not None) and js(page, VIS, "[data-nt1d-lastwrap]"))
        page.click('[data-nt1-fv="bull"]'); page.wait_for_timeout(60)
        ib = js(page, "()=>[...document.querySelectorAll('[data-nt1d-for=\"inv\"]')].map(x=>[x.innerText, x.getAttribute('aria-pressed')])")
        page.click('[data-nt1-fv="bull"]'); page.click('[data-nt1-fv="bear"]'); page.wait_for_timeout(60)
        ib2 = js(page, "()=>[...document.querySelectorAll('[data-nt1d-for=\"inv\"]')].map(x=>[x.innerText, x.getAttribute('aria-pressed')])")
        check(f"{tag} D Invalid direction defaults from My view: Bull → ≤ · Bear → ≥", ib == [["≥", "false"], ["≤", "true"]] and ib2 == [["≥", "true"], ["≤", "false"]], [ib, ib2])
        page.click('[data-nt1-fv="bear"]'); page.click('[data-nt1-fv="bull"]')
        page.fill("#nt1fLevel", "3350"); page.click('[data-nt1d-for="alert"][data-nt1d-dir="down"]'); page.fill("#nt1fInv", "3250"); page.fill("#nt1fLast", "3410"); page.wait_for_timeout(80)
        p1 = js(page, "()=>{ const q = s=>document.querySelector(s); return {has:!!q('[data-nt1d-prev] [data-nt1-ruler]'), top:q('[data-nt1d-prev] .top').innerText.replace(/\\s+/g,' '), inv:parseFloat(q('[data-nt1d-prev] [data-nt1r-tick=\"alert\"]').style.left), chip:!!q('[data-nt1d-prev] [data-nt1r-chip]')}; }")
        page.fill("#nt1fLevel", "3500"); page.wait_for_timeout(80)
        p2 = lr(page, '[data-nt1d-prev] [data-nt1r-tick="alert"]')
        page.fill("#nt1fLevel", ""); page.fill("#nt1fInv", ""); page.wait_for_timeout(80)
        check(f"{tag} D live ruler preview in the PRICE ALERTS block: redraws when a number changes (same nt1Ruler) · hides when Alert and Invalid are both empty", p1["has"] and p1["top"].startswith("Preview · 1.8% above the alert") and not p1["chip"] and p2 != p1["inv"] and js(page, "()=>document.querySelector('[data-nt1d-prev]').innerText.trim()") == "", [p1, p2])
        page.fill("#nt1fLevel", "3350"); page.fill("#nt1fInv", "3250")
        hl = js(page, TXT, "[data-nt1d-savehelp]")
        page.fill("#nt1fTitle", GOLD)
        hl = js(page, TXT, "[data-nt1d-savehelp]")
        check(f"{tag} D helper under Save shows the alert text that will be copied", hl == f"Save copies {LINE} for the TradingView alert", hl)
        page.fill("#nt1fNext", "Watch H4 close above 3400"); page.evaluate("()=>{ document.getElementById('nt1fCheck').value = ''; }")
        clip(page); sheet_save(page)
        nid = js(page, "()=>mySel"); d = js(page, DOC, nid)
        check(f"{tag} D Save needs only About + Title: saved with level · levelDir · invLevel · invDir (from My view) · lastPx · plan empty · check +3 trading days", d and d["level"] == 3350 and d["levelDir"] == "down" and d["invLevel"] == 3250 and d["invDir"] == "down" and d["lastPx"]["v"] == 3410 and d["plan"] == "" and d["checkOn"] == js(page, "()=>nt1bTD(thaiToday(), 3)") and d.get("hitAt") is None and not d.get("tvAlert"), d)
        cp = js(page, "()=>window.__clip"); tt = js(page, TXT, "#nt1Toast"); ln = js(page, "()=>[...document.querySelectorAll('#nt1Toast a, #nt1Toast button')].map(x=>[x.innerText, x.href || ''])")
        check(f"{tag} D2 new idea with a level → clipboard = `{LINE}` · toast `Saved · copied for TradingView: …` + Copy invalid + Open TradingView ↗ · Firestore write happened", cp == LINE and tt.startswith("Saved · copied for TradingView: " + LINE) and ["Open TradingView ↗", "https://www.tradingview.com/chart/"] in ln and any(x[0] == "Copy invalid" for x in ln), [cp, tt, ln])
        js(page, "()=>{ window.__clip = ''; }"); open_edit(page, nid); page.fill("#nt1fTitle", GOLD + " now"); sheet_save(page)
        check(f"{tag} D2 title-only edit → clipboard untouched", js(page, "()=>window.__clip") == "")
        open_edit(page, nid); page.fill("#nt1fTitle", GOLD); sheet_save(page)
        # tvAlert reset
        T.to_my(page, nid); page.wait_for_timeout(200)
        page.click("[data-nt1d-copyalert]"); page.wait_for_timeout(150); a1 = js(page, "()=>window.__clip")
        page.click("[data-nt1d-copyinv]"); page.wait_for_timeout(150); a2 = js(page, "()=>window.__clip")
        check(f"{tag} D `Copy alert` → `{LINE}` · `Copy invalid` → `{INVL}`", a1 == LINE and a2 == INVL, [a1, a2])
        page.click("[data-nt1d-tvset]"); page.wait_for_timeout(250)
        c2 = js(page, "()=>({tv:document.querySelector('[data-nt1d-tv]').innerText.replace(/\\s+/g,' '), chips:document.querySelectorAll('[data-nt1d-tv] .cp').length, doc:window.firebase.__mockDb.__getDoc(['users','testuid','ideas_my',mySel]).tvAlert})")
        check(f"{tag} D one tick covers both: green `TV alerts set ✓`, chips hidden, stored", c2["tv"] == "TV alerts set ✓" and c2["chips"] == 0 and c2["doc"] is True, c2)
        js(page, "()=>{ window.__clip = ''; }"); open_edit(page, nid); page.fill("#nt1fTitle", GOLD + "!"); sheet_save(page)
        check(f"{tag} D tvAlert stays true and the clipboard is untouched on a title-only edit", js(page, DOC, nid)["tvAlert"] is True and js(page, "()=>window.__clip") == "")
        open_edit(page, nid); page.fill("#nt1fTitle", GOLD); page.fill("#nt1fLevel", "3300"); sheet_save(page); T.to_my(page, nid); page.wait_for_timeout(200)
        d3 = js(page, DOC, nid)
        check(f"{tag} D level 3,350 → 3,300 with tvAlert=true → tvAlert false · clipboard = new alert line · TV chips are back", d3["tvAlert"] is False and js(page, "()=>window.__clip") == "XAU ≤ 3,300 · " + GOLD and js(page, "()=>document.querySelectorAll('[data-nt1d-tv] .cp').length") == 3, [d3["tvAlert"], js(page, "()=>window.__clip")])
        page.click("[data-nt1d-tvset]"); page.wait_for_timeout(200); js(page, "()=>{ window.__clip = ''; }")
        open_edit(page, nid); page.fill("#nt1fInv", "3200"); sheet_save(page); T.to_my(page, nid); page.wait_for_timeout(200)
        d4 = js(page, DOC, nid)
        check(f"{tag} D invLevel 3,250 → 3,200 with tvAlert=true → tvAlert false · clipboard = alert line · chips back", d4["tvAlert"] is False and d4["invLevel"] == 3200 and js(page, "()=>window.__clip") == "XAU ≤ 3,300 · " + GOLD and js(page, "()=>document.querySelectorAll('[data-nt1d-tv] .cp').length") == 3, [d4["tvAlert"], js(page, "()=>window.__clip")])
        clip(page, "deny"); open_edit(page, nid); page.fill("#nt1fLevel", "3250"); sheet_save(page)
        dn = js(page, "()=>({t:document.querySelector('#nt1Toast').innerText.replace(/\\s+/g,' '), copy:!!document.querySelector('[data-nt1-toast-copy]')})")
        check(f"{tag} D2 clipboard denied → toast shows the line with a Copy button (never silent)", dn["copy"] and "XAU ≤ 3,250 · " + GOLD in dn["t"], dn)
        clip(page); open_edit(page, nid); page.fill("#nt1fLevel", "3350"); page.fill("#nt1fInv", "3250"); page.fill("#nt1fLast", "3410"); sheet_save(page)
        # hit / invalid timestamps cleared on change, kept on a title-only edit
        B.seed_my(page, {"ts": dict(B.mkmy(11, ("sat", "XAU"), "Stamps", B.add(t0, -1), B.add(t0, 5), level=3350, invLevel=3250), levelDir="down", invDir="down", hitAt="2026-11-18T05:00:00.000Z", invHitAt="2026-11-18T06:00:00.000Z", invAckAt="2026-11-18T07:00:00.000Z", tvAlert=True)})
        js(page, "()=>mySel='ts'"); open_edit(page, "ts"); page.fill("#nt1fTitle", "Stamps edited"); sheet_save(page)
        k = js(page, DOC, "ts")
        check(f"{tag} D title-only edit keeps hitAt · invHitAt · invAckAt · tvAlert", k["hitAt"] and k["invHitAt"] and k["invAckAt"] and k["tvAlert"] is True, k)
        open_edit(page, "ts"); page.fill("#nt1fInv", "3200"); sheet_save(page); k = js(page, DOC, "ts")
        check(f"{tag} D invLevel changed → invHitAt + invAckAt cleared (hitAt kept) · tvAlert false", k["invHitAt"] is None and k["invAckAt"] is None and k["hitAt"] and k["tvAlert"] is False, k)
        open_edit(page, "ts"); page.fill("#nt1fLevel", "3400"); sheet_save(page); k = js(page, DOC, "ts")
        check(f"{tag} D level changed → hitAt cleared", k["hitAt"] is None, k)
        # ───── invalid · hit
        B.seed_my(page, {"iv": dict(B.mkmy(12, ("sat", "XAU"), "Gold invalid", B.add(t0, -1), B.add(t0, 5), level=3350, invLevel=3250, next="Check gold"), levelDir="down", invDir="down", lastPx={"v": 3300, "at": now_iso(page)}),
                         "lh": dict(B.mkmy(13, ("sat", "BTC"), "BTC level hit", B.add(t0, -1), B.add(t0, 5), level=90000, next="Check BTC"), levelDir="up", lastPx={"v": 91000, "at": now_iso(page)})})
        js(page, "()=>nt1Refresh()"); page.wait_for_timeout(300)
        before = js(page, DOC, "iv")
        check(f"{tag} D price 3,300 crosses the Alert (≤ 3,350) but not Invalid (3,250) → hitAt only", bool(before.get("hitAt")) and not before.get("invHitAt"), before)
        js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='iv'))")
        page.evaluate("()=>{ const m = myList.find(x=>x.id==='iv'); m.lastPx = {v:3231, at:new Date().toISOString()}; nt1Refresh(); }"); page.wait_for_timeout(300)
        iv1 = js(page, DOC, "iv")
        page.evaluate("()=>nt1Refresh()"); page.wait_for_timeout(200)
        iv2 = js(page, DOC, "iv")
        check(f"{tag} D price 3,231 ≤ 3,250 → `invHitAt` written once · both crossed → state invalid wins", bool(iv1.get("invHitAt")) and iv1["invHitAt"] == iv2["invHitAt"] and js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='iv')).state") == "invalid", [iv1.get("invHitAt"), iv2.get("invHitAt")])
        B.to_today(page)
        rows = js(page, "()=>nt1bDueAll().filter(x=>x.kind==='my').map(x=>[x.key, x.rank, x.pill, x.btn[0]])")
        check(f"{tag} C Today: `invalidated` (rank 0 · Review ›) ranks above `level hit` (rank 1)", rows[0][1:] == [0, "invalidated", "Review ›"] and ["my:lh", 1, "level hit", "Open ›"] in rows and [r[1] for r in rows] == sorted(r[1] for r in rows), rows)
        T.to_my(page, "iv"); N.goto_watch(page); T.to_my(page, "iv"); page.wait_for_timeout(250)
        iw = js(page, """()=>{ const b = document.querySelector('[data-nt1b-block]'); return {hdr:b.querySelector('[data-nt1d-hdr]').innerText, amb:b.classList.contains('amb'), txt:b.querySelector('[data-nt1b-next-t]').innerText, dark:[...b.querySelectorAll('.btn.pri')].map(x=>x.innerText), keep:!!b.querySelector('[data-nt1d-keep]'), keepTx:b.querySelector('[data-nt1d-keep]').innerText, chip:b.querySelector('[data-nt1r-chip]').innerText}; }""")
        check(f"{tag} D detail invalid: amber `INVALIDATED · …` · `Price broke 3,250` · the one dark button `Drop idea` · `Keep watching · snooze 3 days` · chip `below invalid`", iw["hdr"].startswith("INVALIDATED · ") and iw["amb"] and iw["txt"] == "Price broke 3,250" and iw["dark"] == ["Drop idea"] and iw["keepTx"] == "Keep watching · snooze 3 days" and iw["chip"] == "below invalid", iw)
        shot(page, "invalid-detail")
        page.click("[data-nt1d-keep]"); page.wait_for_timeout(300)
        kv = js(page, DOC, "iv")
        B.to_today(page)
        check(f"{tag} D Keep watching → invAckAt + snoozeTo written · the row leaves Today · stays quiet while the price stays beyond", bool(kv.get("invAckAt")) and bool(kv.get("snoozeTo")) and "my:iv" not in js(page, "()=>nt1bDueAll().map(x=>x.key)") and js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='iv')).state") != "invalid", kv)
        page.evaluate("()=>{ const m = myList.find(x=>x.id==='iv'); m.lastPx = {v:3400, at:new Date().toISOString()}; nt1Refresh(); m.lastPx = {v:3200, at:new Date().toISOString()}; nt1Refresh(); }"); page.wait_for_timeout(300)
        k2 = js(page, DOC, "iv")
        check(f"{tag} D after the snooze it fires again only if the price left and crossed again → new invHitAt newer than invAckAt", k2["invHitAt"] > k2["invAckAt"] and js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='iv')).state") == "invalid", k2)
        N.goto_watch(page); T.to_my(page, "iv"); page.wait_for_timeout(250); page.click("[data-nt1d-drop]"); page.wait_for_timeout(300)
        check(f"{tag} D Drop idea drops it with the Undo toast", js(page, DOC, "iv")["dropped"] is True and js(page, VIS, "[data-nt1b-undo]"))
        page.click("[data-nt1b-undo]"); page.wait_for_timeout(300)
        check(f"{tag} D Undo restores it", js(page, DOC, "iv")["dropped"] is False)
        # manual marks
        B.seed_my(page, {"fr": B.mkmy(14, ("sat", "S50"), "Fresh idea", B.add(t0, -1), B.add(t0, 5), level=900, next="Check S50")})
        N.goto_watch(page); T.to_my(page, "fr"); page.wait_for_timeout(250)
        page.click("[data-nt1d-mark-btn]"); page.click('[data-nt1d-mark="hit"]'); page.wait_for_timeout(300)
        check(f"{tag} D Mark ▾ › Level hit on a fresh idea → hitAt written · card turns amber `LEVEL HIT`", bool(js(page, DOC, "fr").get("hitAt")) and "LEVEL HIT" in js(page, TXT, "[data-nt1b-block]"))
        B.seed_my(page, {"fm": B.mkmy(15, ("sat", "OIL"), "Manual invalid", B.add(t0, -1), B.add(t0, 5), level=80, invLevel=60, next="Check oil")})
        N.goto_watch(page); T.to_my(page, "fm"); page.wait_for_timeout(250)
        page.click("[data-nt1d-mark-btn]"); page.click('[data-nt1d-mark="inv"]'); page.wait_for_timeout(300)
        check(f"{tag} D Mark ▾ › Invalidated → invHitAt written · `INVALIDATED` card", bool(js(page, DOC, "fm").get("invHitAt")) and "INVALIDATED" in js(page, TXT, "[data-nt1b-block]"))
        # level alert states
        B.seed_my(page, {"op": dict(B.mkmy(3, ("sat", "BTC"), "Old price idea", B.add(t0, -1), B.add(t0, 5), level=100, levelDir="up"), lastPx={"v": 90, "at": now_iso(page, -30)}),
                         "nd": dict(B.mkmy(4, ("sat", "OIL"), "No direction", B.add(t0, -1), B.add(t0, 5), level=80), lastPx={"v": 70, "at": now_iso(page)})})
        js(page, "()=>nt1Refresh()"); page.wait_for_timeout(300)
        N.goto_watch(page); T.to_my(page, "op")
        check(f"{tag} D manual price older than 24h → amber `old price`", js(page, "()=>!!document.querySelector('[data-nt1d-oldpx]')"))
        T.to_my(page, "nd")
        check(f"{tag} D level without a direction → no hit from the price", js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='nd')).state") == "none" and not js(page, DOC, "nd").get("hitAt") and "LEVEL HIT" not in js(page, TXT, "[data-nt1b-block]"))
        B.seed_my(page, {"st": dict(B.mkmy(6, ("stock", "AVGO"), "Breakout over 190", B.add(t0, -1), B.add(t0, 5), level=190, levelDir="up"))})
        B.px(page, "AVGO", 189.0); js(page, "()=>nt1Refresh()"); page.wait_for_timeout(250)
        s1 = js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='st')).state")
        B.px(page, "AVGO", 191.0); js(page, "()=>nt1Refresh()"); page.wait_for_timeout(300)
        check(f"{tag} D stock: 189 vs level 190 → near · daily close 191 crosses → hit (hitAt written)", s1 == "near" and bool(js(page, DOC, "st").get("hitAt")), [s1, js(page, DOC, "st")])
        gone = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], capture_output=True, text=True, cwd=os.path.join(HERE, "..")).stdout.split()
        check(f"{tag} D display + alerts only: no sizing / engine file changed · lastPx / invLevel not referenced in them", not any(f.endswith(("risk-engine.js", "core-size.js", "ps1-size.js", "pos-view.js", "re1-adapter.js")) for f in gone) and all("lastPx" not in open(os.path.join(HERE, "..", f), encoding="utf-8").read() and "invLevel" not in open(os.path.join(HERE, "..", f), encoding="utf-8").read() for f in ("risk-engine.js", "core-size.js", "ps1-size.js", "pos-view.js", "re1-adapter.js")), gone)

        # ───── C · Today
        B.seed_my(page, {"nn": dict(B.mkmy(7, ("stock", "AAPL"), "Brand new idea", t0, B.add(t0, 4), view="bull", next=None)),
                         "nr": B.mkmy(10, ("stock", "AMD"), "Near level", t0, B.add(t0, 4), level=100),
                         "lt": B.mkmy(8, ("market", "TH"), "Late one", B.add(t0, -6), B.add(t0, -2), next="Read the SET")})
        B.px(page, "AMD", 101.0); B.to_today(page)
        rk = js(page, "()=>nt1bDueAll().filter(x=>x.kind==='my').map(x=>[x.key, x.rank])")
        order = [r[1] for r in rk]
        check(f"{tag} C rank order: invalidated 0 → level hit 1 → near level 2 → no next step 3 → late 4 → check today 5 (→ AI 6)", order == sorted(order) and set(order) >= {0, 1, 2, 3, 4} and js(page, "()=>nt1bDueAll().filter(x=>x.kind==='ai').every(x=>x.rank===6)"), rk)
        row = js(page, "()=>{ const r = nt1bDueAll().find(x=>x.key==='my:nn'); return r && [r.pill, r.cls, r.btn[0], r.sub]; }")
        check(f"{tag} C new idea without Next step → amber `no next step` · `Set next step ›` · `New · <date> · Bull`", row and row[0] == "no next step" and "p-a" in row[1] and row[2] == "Set next step ›" and row[3].startswith("New · ") and row[3].endswith(" · Bull"), row)
        rows3 = js(page, B.ROWS); ranks3 = js(page, "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>+r.dataset.nt1bRank)")
        check(f"{tag} C max 3 rows unchanged · the first row is the invalidated one", len(rows3) == 3 and ranks3 == sorted(ranks3) and ranks3[0] == 0, [rows3, ranks3])
        tr = js(page, """()=>{ const r = document.querySelector('[data-nt1b-it]'); const n = r.querySelector('[data-nt1b-next]'), t = r.querySelector('.t'); return {sub:r.querySelector('[data-nt1b-sub]').innerText, pill:r.querySelector('[data-nt1b-pill]').innerText, pillInSub:n.contains(r.querySelector('[data-nt1b-pill]')), titleLines:Math.round(t.getBoundingClientRect().height / (parseFloat(getComputedStyle(t).lineHeight) || 18))}; }""")
        check(f"{tag} C Today row: `TAG title` / `Invalid … · invalidated` (status on line 2) / right button · title on one line", tr["sub"].startswith("Invalid") and tr["pill"] == "invalidated" and tr["pillInSub"] and tr["titleLines"] == 1, tr)
        js(page, "()=>nt1bSetNext('nn')"); page.wait_for_timeout(300)
        check(f"{tag} C Set next step › opens the sheet with Next step focused", js(page, "()=>document.activeElement && document.activeElement.id") == "nt1fNext")
        page.fill("#nt1fNext", "Close above 200"); sheet_save(page); B.to_today(page)
        check(f"{tag} C a saved Next step removes the row", "my:nn" not in js(page, "()=>nt1bDueAll().map(x=>x.key)"))
        B.seed_my(page, {"n2": dict(B.mkmy(9, ("market", "US"), "Another new", t0, B.add(t0, 4), next=None))}); B.to_today(page)
        before = "my:n2" in js(page, "()=>nt1bDueAll().map(x=>x.key)")
        js(page, "()=>nt1bAct('my:n2','snooze3')"); page.wait_for_timeout(200)
        check(f"{tag} C snooze hides the `no next step` row until the date", before and "my:n2" not in js(page, "()=>nt1bDueAll().map(x=>x.key)"))
        B.to_today(page); B.quiet_fixture_ai(page)
        js(page, "()=>{ const t = document.getElementById('nt1bToast'); if(t) t.style.display = 'none'; }")
        shot(page, "level-hit-today")
        N.goto_watch(page); T.to_my(page, nid); page.wait_for_timeout(300); shot(page, "level-hit-detail")

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
        T.to_my(page, "x1"); page.wait_for_timeout(300)
        y = js(page, """()=>{ const q = s=>document.querySelector(s), t = s=>Math.round(q(s).getBoundingClientRect().top); return {chart:t('[data-nt1-chartw]'), ch:Math.round(q('[data-nt1-chartw]').getBoundingClientRect().height), next:t('[data-nt1b-block]'), ang:t('[data-nt1-notes]'), foot:t('[data-nt1-foot]'), plan:/Old plan/.test(q('[data-nt1-detail]').innerText), over:document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1}; }""")
        check(f"{tag} B phone order: chart (230) → Next step card → notes → footer · no Plan · no sideways scroll", y["ch"] == 230 and y["chart"] < y["next"] < y["ang"] < y["foot"] and not y["plan"] and y["over"], y)
        shot(page, "phone")
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
