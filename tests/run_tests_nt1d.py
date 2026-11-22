#!/usr/bin/env python3
"""NT1d — A `.nt1-x` fix · B My idea detail 2 columns (+ Enlarge) · C Today “no next step” · D sheet + level hit + D2 auto-copy · E Settings hints.
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
GOLD = "Opportunity to Buy Gold"
LINE = "XAU ≤ 3,340 · " + GOLD


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

        # ───── B · 2 columns
        dd = B.mkmy(1, ("sat", "XAU"), GOLD, B.add(t0, -1), B.add(t0, 4), view="bull", next="Watch H4 close above 3400", level=3340, ang={"tech": "Support 3290-3340", "sent": "Gold down 11%", "fund": "Central banks keep buying", "macro": "CPI Thursday"}, chart=tv, builtOn="en-idea-1")
        dd.update({"levelDir": "down", "lastPx": {"v": 3410, "at": now_iso(page)}})
        B.seed_my(page, {"x1": dd, "x2": B.mkmy(2, ("market", "US"), "No chart idea", B.add(t0, -2), B.add(t0, 4), ang={"tech": "Breadth falling", "macro": "CPI"}, next="Read CPI", plan="My old plan text")})
        T.to_my(page, "x1"); page.wait_for_timeout(300)
        g = js(page, """()=>{ const q = s=>document.querySelector(s), r = e=>e.getBoundingClientRect(), c = r(q('[data-nt1-chartw]')), sd = r(q('[data-nt1-side]')), det = q('.nt1-det') || q('[data-nt1-detail]'), p = q('[data-nt1-detail]');
            return {cols:getComputedStyle(q('[data-nt1-r1]')).gridTemplateColumns.split(' ').length, left:c.right <= sd.left + 1, ch:Math.round(c.height), sh:Math.round(sd.height), cw:Math.round(c.width), sw:Math.round(sd.width),
              angs:[...document.querySelectorAll('[data-nt1-side] [data-nt1-ang]')].map(x=>x.dataset.nt1Ang), plan:!!q('[data-nt1-ang="plan"]'), row2:!!q('.nt1-ang'), nx:!!q('[data-nt1-side] [data-nt1b-block]'),
              foot:!!q('[data-nt1-foot] [data-nt1-built]') && !!q('[data-nt1-foot] [data-nt1-review]'), checks:(p.innerText.match(/Check again/g) || []).length,
              noScroll:document.documentElement.scrollHeight <= innerHeight + 1, panel:p.scrollHeight <= p.clientHeight + 1 || (q('.nt1-det') && q('.nt1-det').scrollHeight <= q('.nt1-det').clientHeight + 1),
              fit:getComputedStyle(q('[data-nt1-chartw] img')).objectFit}; }""")
        check(f"{tag} B 2 columns: chart left (3fr) · Next step + angle cards right (2fr) · no row 2 · no Plan card without an old plan", g["cols"] == 2 and g["left"] and g["cw"] > g["sw"] and g["angs"] == ["tech", "sent", "fund", "macro"] and g["nx"] and not g["plan"] and not g["row2"], g)
        check(f"{tag} B chart ≥ 372 and stretches to the right column height · object-fit contain", g["ch"] >= 372 and g["ch"] >= g["sh"] - 1 and g["fit"] == "contain", g)
        check(f"{tag} B footer row: Built on left · review right · `Check again` appears once", g["foot"] and g["checks"] == 1, g)
        check(f"{tag} B fits 1440×900: no page scroll · detail does not need to scroll when filled", g["noScroll"] and g["panel"], g)
        shot(page, "watch-full")
        # Enlarge
        page.focus("[data-nt1-zoom]"); page.click("[data-nt1-zoom]"); page.wait_for_timeout(200)
        z = js(page, "()=>{ const m = document.querySelector('[data-nt1-zm]'); if(!m) return null; const i = m.querySelector('img'); return {tv:m.querySelector('[data-nt1-zm-tv]').innerText, maxw:getComputedStyle(i).maxWidth, maxh:getComputedStyle(i).maxHeight, focus:document.activeElement.hasAttribute('data-nt1-zm-x')}; }")
        check(f"{tag} B ⤢ Enlarge opens the in-app large view: image ≤ 90vw/90vh · `↗ Open in TradingView` link", z and "Open in TradingView" in z["tv"] and z["maxw"] != "none" and z["maxh"] != "none", z)
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        check(f"{tag} B Esc closes it and focus returns to ⤢ Enlarge", not js(page, VIS, "[data-nt1-zm]") and js(page, "()=>document.activeElement.hasAttribute('data-nt1-zoom')"))
        page.click("[data-nt1-zoom]"); page.wait_for_timeout(150); page.mouse.click(5, 5); page.wait_for_timeout(150)
        check(f"{tag} B click outside closes it", js(page, "()=>!document.querySelector('[data-nt1-zm]')"))
        page.click("[data-nt1-zoom]"); page.wait_for_timeout(150); page.click("[data-nt1-zm-x]"); page.wait_for_timeout(150)
        check(f"{tag} B ✕ closes it", js(page, "()=>!document.querySelector('[data-nt1-zm]')") and js(page, "()=>document.activeElement.hasAttribute('data-nt1-zoom')"))
        # no chart → single column, old plan shown read-only
        T.to_my(page, "x2"); page.wait_for_timeout(250)
        n = js(page, """()=>{ const q = s=>document.querySelector(s); return {one:q('[data-nt1-r1]').classList.contains('one'), chart:!!q('[data-nt1-chartw]'), ang:[...document.querySelectorAll('.nt1-ang [data-nt1-ang]')].map(x=>x.dataset.nt1Ang), plan:q('[data-nt1-ang="plan"]') && q('[data-nt1-ang="plan"]').innerText.replace(/\\s+/g,' '), planInSide:!!q('[data-nt1-side] [data-nt1-ang="plan"]'), cols:getComputedStyle(q('[data-nt1-r1]')).gridTemplateColumns.split(' ').length}; }""")
        check(f"{tag} B no chart → single column: Next step + `Plan (old)` on top, angles below", n["one"] and not n["chart"] and n["cols"] == 1 and n["ang"] == ["tech", "macro"] and n["planInSide"] and n["plan"].lower().startswith("plan (old)"), n)
        shot(page, "no-chart")

        # ───── D · sheet
        T.to_my(page); js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(250)
        s = js(page, """()=>{ const q = s=>document.querySelector(s), vis = e=>!!(e && e.checkVisibility() && e.getBoundingClientRect().width > 0), sh = q('[data-nt1-sheet]');
            const labels = [...sh.querySelectorAll('label')].filter(l=>vis(l)).map(l=>l.innerText.split('\\n')[0].trim());
            return {labels, plan:!!q('#nt1f-plan, [data-nt1-plan]'), tvcopy:/Copy level|I set the alert/.test(sh.innerText), foldOpen:q('[data-nt1d-more]').open, taVis:vis(q('#nt1f-tech')), segs:[...sh.querySelectorAll('[data-nt1d-dir]')].map(x=>[x.innerText, x.getAttribute('aria-pressed')]), last:vis(q('[data-nt1d-lastwrap]'))}; }""")
        check(f"{tag} D sheet: About · My view · Title · Chart · Next step · Check again on · Alert level (+ ≥ ≤) · Last price · More notes fold", s["labels"][:7] == ["About", "My view optional", "Title", "Chart TradingView snapshot link", "Next step one line — what you will look at next", "Check again on", "Alert level optional"] and s["last"], s)
        check(f"{tag} D sheet: no Plan field · no Copy level / `I set the alert` · `More notes` closed (its fields hidden) · neither ≥ nor ≤ selected", not s["plan"] and not s["tvcopy"] and not s["foldOpen"] and not s["taVis"] and s["segs"] == [["≥", "false"], ["≤", "false"]], s)
        page.select_option("#nt1fSubj", "stock:AVGO"); page.wait_for_timeout(80)
        check(f"{tag} D Last price hidden for a stock, shown for XAU", not js(page, VIS, "[data-nt1d-lastwrap]") and (page.select_option("#nt1fSubj", "sat:XAU") is not None) and js(page, VIS, "[data-nt1d-lastwrap]"))
        page.fill("#nt1fLevel", "3340"); page.click('[data-nt1d-dir="down"]')
        hl = js(page, TXT, "[data-nt1d-lvhelp]")
        check(f"{tag} D helper: `Reached when price goes ≤ 3,340`", hl == "Reached when price goes ≤ 3,340", hl)
        page.fill("#nt1fTitle", GOLD); page.fill("#nt1fLast", "3410"); page.fill("#nt1fNext", "Watch H4 close above 3400")
        page.evaluate("()=>{ document.getElementById('nt1fCheck').value = ''; }")
        clip(page); sheet_save(page)
        nid = js(page, "()=>mySel"); d = js(page, DOC, nid)
        check(f"{tag} D Save needs only About + Title (+ the rest optional): saved with level · dir · lastPx · plan kept empty", d and d["level"] == 3340 and d["levelDir"] == "down" and d["lastPx"]["v"] == 3410 and d["plan"] == "" and d["checkOn"] == js(page, "()=>nt1bTD(thaiToday(), 3)") and d.get("hitAt") is None and not d.get("tvAlert"), d)
        # D2
        cp = js(page, "()=>window.__clip"); tt = js(page, TXT, "#nt1Toast"); ln = js(page, "()=>document.querySelector('#nt1Toast a') && [document.querySelector('#nt1Toast a').innerText, document.querySelector('#nt1Toast a').href]")
        check(f"{tag} D2 new idea with a level → clipboard = `{LINE}` · toast `Saved · copied for TradingView: …` + Open TradingView ↗ · Firestore write happened", cp == LINE and tt.startswith("Saved · copied for TradingView: " + LINE) and ln[0] == "Open TradingView ↗" and ln[1] == "https://www.tradingview.com/chart/", [cp, tt, ln])
        js(page, "()=>{ window.__clip = ''; }"); open_edit(page, nid); page.fill("#nt1fTitle", GOLD + " now"); sheet_save(page)
        check(f"{tag} D2 title-only edit → clipboard untouched", js(page, "()=>window.__clip") == "")
        open_edit(page, nid); page.fill("#nt1fLevel", "3300"); page.fill("#nt1fTitle", GOLD); sheet_save(page)
        check(f"{tag} D2 level 3,340 → 3,300 → copied again", js(page, "()=>window.__clip") == "XAU ≤ 3,300 · " + GOLD, js(page, "()=>window.__clip"))
        clip(page, "deny"); open_edit(page, nid); page.fill("#nt1fLevel", "3250"); sheet_save(page)
        dn = js(page, "()=>({t:document.querySelector('#nt1Toast').innerText.replace(/\\s+/g,' '), copy:!!document.querySelector('[data-nt1-toast-copy]')})")
        check(f"{tag} D2 clipboard denied → toast shows the line with a Copy button (never silent)", dn["copy"] and "XAU ≤ 3,250 · " + GOLD in dn["t"], dn)
        clip(page)
        # detail card · not hit
        open_edit(page, nid); page.fill("#nt1fLevel", "3340"); page.fill("#nt1fLast", "3410"); page.fill("#nt1fTitle", GOLD); sheet_save(page)
        T.to_my(page, nid); page.wait_for_timeout(200)
        c = js(page, """()=>{ const b = document.querySelector('[data-nt1b-block]'); return {txt:b.innerText.replace(/\\s+/g,' '), bg:getComputedStyle(b).backgroundColor, amb:b.classList.contains('amb'), tv:getComputedStyle(b.querySelector('.w')).color, dark:[...b.querySelectorAll('.btn.pri')].length}; }""")
        check(f"{tag} D detail: `Level ≤ 3,340 · now 3,410 (manual · …) · 2.1% to level` · `TV alert: not set` amber · Copy text · Copy level · I set it · Level hit", all(x in c["txt"] for x in ("Level ≤ 3,340", "now 3,410 (manual", "2.1% to level", "TV alert: not set", "Copy text", "Copy level", "I set it", "Level hit", "TradingView sends the push")) and not c["amb"] and c["tv"] == "rgb(154, 91, 0)", c)
        page.click("[data-nt1d-copylevel]"); page.wait_for_timeout(200)
        check(f"{tag} D Copy level puts the plain number `3340` on the clipboard", js(page, "()=>window.__clip") == "3340", js(page, "()=>window.__clip"))
        page.click("[data-nt1d-copytext]"); page.wait_for_timeout(200)
        check(f"{tag} D Copy text puts the alert line on the clipboard", js(page, "()=>window.__clip") == LINE, js(page, "()=>window.__clip"))
        # price crosses → hit (written once)
        open_edit(page, nid); page.fill("#nt1fLast", "3300"); sheet_save(page)
        d = js(page, DOC, nid); h1 = d.get("hitAt")
        T.to_my(page, nid); page.wait_for_timeout(200)
        hc = js(page, "()=>{ const b = document.querySelector('[data-nt1b-block]'); return {hdr:b.querySelector('[data-nt1d-hdr]').innerText, amb:b.classList.contains('amb'), notyet:!!b.querySelector('[data-nt1d-notyet]'), notyetTx:b.querySelector('[data-nt1d-notyet]') && b.querySelector('[data-nt1d-notyet]').innerText, tvrow:!!b.querySelector('[data-nt1d-tv]')}; }")
        check(f"{tag} D price 3,300 ≤ 3,340 → `hitAt` written · detail turns amber `LEVEL HIT · …` · `Not yet · snooze 3 days`", bool(h1) and hc["hdr"].startswith("LEVEL HIT · ") and hc["amb"] and hc["notyetTx"] == "Not yet · snooze 3 days" and not hc["tvrow"], [h1, hc])
        open_edit(page, nid); page.fill("#nt1fLast", "3500"); sheet_save(page); page.wait_for_timeout(300)
        d2 = js(page, DOC, nid)
        check(f"{tag} D price back to 3,500 → still hit (hitAt unchanged)", d2.get("hitAt") == h1 and js(page, "()=>nt1bLevelState(myList.find(m=>m.id===mySel)).state") == "hit", [h1, d2.get("hitAt")])
        # old price · no direction · fresh idea → Level hit button
        B.seed_my(page, {"op": dict(B.mkmy(3, ("sat", "BTC"), "Old price idea", B.add(t0, -1), B.add(t0, 5), level=100, levelDir="up"), lastPx={"v": 90, "at": now_iso(page, -30)}),
                         "nd": dict(B.mkmy(4, ("sat", "OIL"), "No direction", B.add(t0, -1), B.add(t0, 5), level=80), lastPx={"v": 70, "at": now_iso(page)}),
                         "fr": B.mkmy(5, ("sat", "S50"), "Fresh idea", B.add(t0, -1), B.add(t0, 5), level=900)})
        js(page, "()=>nt1Refresh()"); page.wait_for_timeout(300)
        T.to_my(page, "op")
        check(f"{tag} D manual price older than 24h → amber `old price`", "old price" in js(page, TXT, "[data-nt1b-block]") and js(page, "()=>!!document.querySelector('[data-nt1d-oldpx]')"))
        T.to_my(page, "nd")
        check(f"{tag} D level without a direction → no hit from the price", js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='nd')).state") == "none" and not js(page, DOC, "nd").get("hitAt") and "LEVEL HIT" not in js(page, TXT, "[data-nt1b-block]"))
        T.to_my(page, "fr"); page.click("[data-nt1d-levelhit]"); page.wait_for_timeout(300)
        check(f"{tag} D `Level hit` button on a fresh idea → hit", bool(js(page, DOC, "fr").get("hitAt")) and "LEVEL HIT" in js(page, TXT, "[data-nt1b-block]"))
        # I set it
        T.to_my(page, "op"); page.click("[data-nt1d-tvset]"); page.wait_for_timeout(250)
        check(f"{tag} D `I set it` → TV alert: set ✓ (stored on the idea)", js(page, DOC, "op").get("tvAlert") is True and "TV alert: set ✓" in js(page, TXT, "[data-nt1b-block]"))
        clip(page); open_edit(page, "op"); page.fill("#nt1fLevel", "120"); sheet_save(page)
        check(f"{tag} D2 `tvAlert` ticked → no copy even when the level changes", js(page, "()=>window.__clip") == "")
        # stock close crosses
        B.seed_my(page, {"st": dict(B.mkmy(6, ("stock", "AVGO"), "Breakout over 190", B.add(t0, -1), B.add(t0, 5), level=190, levelDir="up"))})
        B.px(page, "AVGO", 189.0); js(page, "()=>nt1Refresh()"); page.wait_for_timeout(250)
        s1 = js(page, "()=>nt1bLevelState(myList.find(m=>m.id==='st')).state")
        B.px(page, "AVGO", 191.0); js(page, "()=>nt1Refresh()"); page.wait_for_timeout(300)
        check(f"{tag} D stock: 189 vs level 190 → near · daily close 191 crosses → hit (hitAt written)", s1 == "near" and bool(js(page, DOC, "st").get("hitAt")), [s1, js(page, DOC, "st")])
        gone = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], capture_output=True, text=True, cwd=os.path.join(HERE, "..")).stdout.split()
        src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
        check(f"{tag} D display + this alert only: no sizing / engine file changed · lastPx / nt1bLevelPx not referenced in them", not any(f.endswith(("risk-engine.js", "core-size.js", "ps1-size.js", "pos-view.js", "re1-adapter.js")) for f in gone) and all("lastPx" not in open(os.path.join(HERE, "..", f), encoding="utf-8").read() for f in ("risk-engine.js", "core-size.js", "ps1-size.js", "pos-view.js", "re1-adapter.js")), gone)

        # ───── C · Today
        B.seed_my(page, {"nn": dict(B.mkmy(7, ("stock", "AAPL"), "Brand new idea", t0, B.add(t0, 4), view="bull", next=None)),
                         "nr": B.mkmy(10, ("stock", "AMD"), "Near level", t0, B.add(t0, 4), level=100),
                         "lt": B.mkmy(8, ("market", "TH"), "Late one", B.add(t0, -6), B.add(t0, -2), next="Read the SET")})
        B.px(page, "AMD", 101.0); B.to_today(page)
        rk = js(page, "()=>nt1bDueAll().filter(x=>x.kind==='my').map(x=>[x.key, x.rank])")
        order = [r[1] for r in rk]
        check(f"{tag} C rank order: level hit 0 → near level 1 → no next step 2 → late 3 → check today 4 (→ AI 5)", order == sorted(order) and set(order) >= {0, 1, 2, 3}, rk)
        row = js(page, "()=>{ const r = nt1bDueAll().find(x=>x.key==='my:nn'); return r && [r.pill, r.cls, r.btn[0], r.sub]; }")
        check(f"{tag} C new idea without Next step → Today row: amber `no next step` · `Set next step ›` · `New · <date> · Bull`", row and row[0] == "no next step" and "p-a" in row[1] and row[2] == "Set next step ›" and row[3].startswith("New · ") and row[3].endswith(" · Bull"), row)
        rows3 = js(page, B.ROWS)
        check(f"{tag} C max 3 rows unchanged", len(rows3) == 3 and js(page, "()=>[...document.querySelectorAll('[data-nt1b-it]')].map(r=>+r.dataset.nt1bRank)") == [0, 0, 0], rows3)
        js(page, "()=>nt1bMaxRows = 99") if False else None
        hit = js(page, "()=>{ const r = nt1bDueAll().find(x=>x.key==='my:st'); return r && [r.rank, r.pill, r.btn[0], r.sub]; }")
        check(f"{tag} C level-hit row: rank 0 · amber `level hit` · `Make plan ›` (stock) · sub `Level ≥ 190`", hit == [0, "level hit", "Make plan ›", "Level ≥ 190"], hit)
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
        dd = B.mkmy(1, ("sat", "XAU"), GOLD, B.add(t0, -1), B.add(t0, 4), view="bull", next="Watch H4", level=3340, ang={"tech": "Support", "sent": "Down 11%"}, chart="https://www.tradingview.com/x/AbC123/", plan="Old plan")
        B.seed_my(page, {"x1": dd})
        T.to_my(page, "x1"); page.wait_for_timeout(300)
        y = js(page, """()=>{ const q = s=>document.querySelector(s), t = s=>Math.round(q(s).getBoundingClientRect().top); return {chart:t('[data-nt1-chartw]'), ch:Math.round(q('[data-nt1-chartw]').getBoundingClientRect().height), next:t('[data-nt1b-block]'), plan:t('[data-nt1-ang="plan"]'), ang:t('[data-nt1-ang="tech"]'), foot:t('[data-nt1-foot]'), over:document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1}; }""")
        check(f"{tag} B phone order: chart (230) → Next step → Plan → angles → footer · no sideways scroll", y["ch"] == 230 and y["chart"] < y["next"] < y["plan"] < y["ang"] < y["foot"] and y["over"], y)
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
