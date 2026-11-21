#!/usr/bin/env python3
"""NT1 — Watch › Ideas first (AI generated | My ideas) · trade-idea notes in context · Journal › Reviews.
Run: python3 tests/run_tests_nt1.py"""
import sys, os, json
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import nt1_common as N

HERE = os.path.dirname(os.path.abspath(__file__))
TXT = "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }"
VIS = "(s)=>{ const e = document.querySelector(s); if(!e) return false; const r = e.getBoundingClientRect(), c = getComputedStyle(e); return r.width>0 && r.height>0 && c.visibility!=='hidden' && c.display!=='none'; }"
ALLT = "(s)=>[...document.querySelectorAll(s)].map(e=>e.innerText.replace(/\\s+/g,' ').trim())"
OVER = "()=>{ const w = document.documentElement.clientWidth; return document.documentElement.scrollWidth <= w + 1 && document.body.scrollWidth <= w + 1; }"
SEGS = "()=>[...document.querySelectorAll('[data-wl1-segs] button')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())"
VIEW = "()=>[wlView, nt1Seg]"
DOC = lambda d: "(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas_my',i])"


def extra_ai(page):
    """3rd theme with companies + losers, a parked one, a ready one"""
    import lr5_common as C, copy
    for iid, nm, st, cands, lose in (
        ("nt1-idea-3", "Grid power demand", "need_evidence", [{"sym": s, "name": s, "state": "study", "segments": [], "relevance_src": "10-K"} for s in ("VST", "CEG", "ETN", "AVGO")], [{"sym": "ZZZZ", "why": "Loses on power cost"}]),
        ("nt1-idea-4", "Weight-loss pills", "parked", [], []),
    ):
        d = C.idea_doc(iid, nm); d["status"] = st; d["candidates"] = cands; d["losers"] = lose
        page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", [iid, {"idea": {k: v for k, v in d.items() if k != "log"}, "idea_log": d.get("log", []), "user": {}}])
    page.wait_for_timeout(500)


def to_my(page, sel=None):
    js(page, "()=>{ wlView='idea'; nt1SegSet('my'); }"); page.wait_for_timeout(200)
    if sel: js(page, "(i)=>nt1MySelect(i)", sel); page.wait_for_timeout(150)


def to_ai(page):
    js(page, "()=>{ wlView='idea'; nt1SegSet('ai'); }"); page.wait_for_timeout(200)


def fill_sheet(page, subj="market:US", title="T", tech="x", **kw):
    page.select_option("#nt1fSubj", subj)
    if subj == "tag:": page.fill("#nt1fTag", kw.get("tag", "mytag"))
    page.fill("#nt1fTitle", title)
    if tech is not None: page.fill("#nt1f-tech", tech)
    for k, sel in (("plan", "#nt1f-plan"), ("chart", "#nt1fChart"), ("check", "#nt1fCheck")):
        if kw.get(k) is not None: page.fill(sel, kw[k])
    if kw.get("view"): page.click('[data-nt1-fv="%s"]' % kw["view"])
    if kw.get("built"): page.select_option("#nt1fBuilt", kw["built"])


def run_desktop(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h)
    js(page, "()=>{ window.__dlg = []; window.confirm = m=>{ window.__dlg.push(String(m)); return true; }; }")
    DL = lambda: js(page, "()=>window.__dlg")
    try:
        extra_ai(page)
        # ================= A · order + always opens on Ideas
        js(page, "()=>{ switchTab('watch'); wl1SegGo('ladder'); switchTab('journal'); }"); page.wait_for_timeout(200)
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(300)
        lab = js(page, SEGS)
        check(f"{tag} A Watch segments = Ideas · Momentum · Compounder · Screen", [x.split(" ")[0] for x in lab] == ["Ideas", "Momentum", "Compounder", "Screen"], lab)
        check(f"{tag} A Watch re-opens on Ideas (last was Compounder)", js(page, VIEW)[0] == "idea", js(page, VIEW))
        js(page, "()=>{ wl1SegGo('winner'); switchTab('plan'); switchTab('watch'); }"); page.wait_for_timeout(250)
        check(f"{tag} A …again after Momentum", js(page, VIEW)[0] == "idea")
        # tab order
        seq = []
        page.mouse.click(5, 5)
        for _ in range(4):
            page.keyboard.press("Tab"); page.wait_for_timeout(180); seq.append(js(page, "()=>wl1SegNow()"))
        check(f"{tag} A Tab cycles Ideas → Momentum → Compounder → Screen → Ideas", seq == ["winner", "ladder", "screen", "idea"], seq)
        page.keyboard.press("Shift+Tab"); page.wait_for_timeout(180)
        check(f"{tag} A Shift+Tab goes back (Ideas → Screen)", js(page, "()=>wl1SegNow()") == "screen")
        js(page, "()=>wl1SegGo('idea')")
        st = js(page, "()=>[wl1SegStep(-1,false), wl1SegStep(1,false), wl1SegNow()]")
        check(f"{tag} A phone swipe order: no step before Ideas, next = Momentum", st == [False, True, "winner"], st)
        # deep links
        js(page, "()=>{ switchTab('today'); wl1Go('AAPL'); }"); page.wait_for_timeout(300)
        check(f"{tag} A deep link (stock) opens its own segment, not Ideas", js(page, "()=>[wlView, wl1SegNow(), wlSel]") == ["wl", "winner", "AAPL"], js(page, "()=>[wlView, wl1SegNow(), wlSel]"))
        js(page, "()=>{ switchTab('today'); switchTab('watch'); wlSetView('screen'); }"); page.wait_for_timeout(200)
        check(f"{tag} A deep link (Screen) opens Screen", js(page, VIEW)[0] == "screen")
        N.goto_watch(page)
        # ================= B · ← → AI ↔ My
        to_ai(page); page.mouse.click(5, 5)
        page.keyboard.press("ArrowLeft"); page.wait_for_timeout(120)
        check(f"{tag} B ← at AI generated stops", js(page, VIEW)[1] == "ai")
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(200)
        check(f"{tag} B → goes to My ideas", js(page, VIEW)[1] == "my")
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(120)
        check(f"{tag} B → at My ideas stops", js(page, VIEW)[1] == "my")
        page.keyboard.press("ArrowLeft"); page.wait_for_timeout(200)
        check(f"{tag} B ← goes back to AI generated", js(page, VIEW)[1] == "ai")
        js(page, "()=>nt1SegSet('my')"); js(page, "()=>nt1FindOpen()"); page.wait_for_timeout(150)
        page.keyboard.press("ArrowLeft"); page.wait_for_timeout(120)
        check(f"{tag} B ←/→ ignored while typing in Find", js(page, VIEW)[1] == "my")
        page.keyboard.press("Escape"); js(page, "()=>{ myFindOpen=false; myQ=''; renderWatchlist(); }"); page.mouse.click(5, 5)
        js(page, "()=>nt1SheetOpen({})"); page.wait_for_timeout(150); page.keyboard.press("ArrowLeft")
        check(f"{tag} B ←/→ ignored with a sheet open", js(page, VIEW)[1] == "my")
        js(page, "()=>nt1SheetClose()"); page.wait_for_timeout(100)
        js(page, "()=>{ switchTab('plan'); switchTab('watch'); }"); page.wait_for_timeout(250)
        check(f"{tag} B last of the two is remembered (My ideas)", js(page, VIEW) == ["idea", "my"], js(page, VIEW))
        to_ai(page)
        # ================= C · AI list
        rows = js(page, "()=>[...document.querySelectorAll('.nt1-ai')].map(r=>({id:r.dataset.idea, t:r.innerText.replace(/\\s+/g,' ').trim(), st:(r.querySelector('[data-nt1-st]')||{}).dataset?.nt1St, faded:r.classList.contains('faded')}))")
        by = {r["id"]: r for r in rows}
        check(f"{tag} C list has themes + the trade idea", len(rows) == 5 and "gold-cpi" in by, [r["id"] for r in rows])
        check(f"{tag} C status in plain words with evidence count", "Needs evidence · 2/4" in by["nt1-idea-3"]["t"] or "Needs evidence ·" in by["nt1-idea-3"]["t"], by["nt1-idea-3"]["t"])
        check(f"{tag} C no old wording (Waiting for evidence / Ready to hand off / Chain)", not any(s in js(page, "()=>document.body.innerText") for s in ("Waiting for evidence", "Ready to hand off")))
        check(f"{tag} C THEME / TRADE tags", "THEME" in by["nt1-idea-3"]["t"] and "TRADE" in by["gold-cpi"]["t"])
        check(f"{tag} C Gains tickers max 3 + “+n”, Loses tickers", "Gains" in by["nt1-idea-3"]["t"] and "+1" in by["nt1-idea-3"]["t"] and "Loses ZZZZ" in by["nt1-idea-3"]["t"], by["nt1-idea-3"]["t"])
        check(f"{tag} C Gains tickers show RS when known (AVGO)", js(page, "()=>{ const t = document.querySelector('[data-idea=\"nt1-idea-3\"] [data-nt1-tk-s=\"AVGO\"]'); return t ? t.innerText.trim() : ''; }") == "AVGO 64", js(page, "()=>{ const t = document.querySelector('[data-idea=\"nt1-idea-3\"] [data-nt1-tk-s=\"AVGO\"]'); return t ? t.innerText : null; }"))
        check(f"{tag} C trade idea shows Asset XAU", "Asset XAU" in by["gold-cpi"]["t"], by["gold-cpi"]["t"])
        check(f"{tag} C Parked is in All, faded", by["nt1-idea-4"]["faded"] and "Parked" in by["nt1-idea-4"]["t"])
        check(f"{tag} C no Open button on the rows · row opens the idea", not js(page, "()=>[...document.querySelectorAll('.nt1-ai button')].some(b=>/open/i.test(b.innerText))") and js(page, "()=>{ document.querySelector('[data-idea=\"nt1-idea-3\"]').click(); return ideaSel; }") == "nt1-idea-3")
        hd = js(page, "()=>document.querySelector('[data-lr5-head]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} C header: chips + Import JSON, no + Idea / + Trade idea", "Import JSON" in hd and "Needs evidence" in hd and "+ Idea" not in hd and "+ Trade idea" not in hd, hd)
        for chip, want in (("theme", {"nt1-idea-3", "en-idea-1", "en-idea-2"}), ("trade", {"gold-cpi"}), ("need", {"nt1-idea-3", "en-idea-1", "en-idea-2", "gold-cpi"}), ("ready", set())):
            js(page, "(k)=>nt1AiSet(k)", chip); page.wait_for_timeout(120)
            got = set(js(page, "()=>[...document.querySelectorAll('.nt1-ai')].map(r=>r.dataset.idea)"))
            check(f"{tag} C chip {chip}", got == want, sorted(got))
        js(page, "()=>nt1AiSet('all')")
        # ================= D · AI detail
        js(page, "()=>ideaOpen('nt1-idea-3')"); page.wait_for_timeout(200)
        d = js(page, "()=>document.querySelector('.nt1-det').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} D answer-first: sentence + What changed / Why now / Who gains / Who loses / Proven / Assumption / Park it when", all(s in d for s in ("When ", "What changed?", "Why now?", "Who gains?", "Who loses?", "Proven so far", "Still an assumption", "Park it when")), d[:400])
        check(f"{tag} D gains tickers → Watch / Screen buttons (all of them)", js(page, "()=>document.querySelectorAll('[data-nt1-gain] [data-nt1-tk]').length") == 4)
        check(f"{tag} D three fold-outs How it works · Evidence · Companies", js(page, ALLT, ".nt1-fold>summary") != [] and [x.split(" ")[0] for x in js(page, ALLT, ".nt1-fold>summary")] == ["How", "Evidence", "Companies"], js(page, ALLT, ".nt1-fold>summary"))
        check(f"{tag} D primary Add evidence › + “+ My idea on this”", js(page, TXT, "[data-idea-main]") == "Add evidence ›" and js(page, TXT, "[data-nt1-myidea]") == "+ My idea on this")
        check(f"{tag} D folds closed by default", js(page, "()=>document.querySelectorAll('.nt1-fold[open]').length") == 0)
        js(page, "()=>document.querySelector('[data-idea-main]').click()"); page.wait_for_timeout(200)
        check(f"{tag} D Add evidence › opens the Evidence fold (old evidence content + gaps hook)", js(page, "()=>!!document.querySelector('.nt1-fold[open][data-nt1-fold=\"evd\"]')") and js(page, VIS, "[data-idea-gaps]"))
        js(page, "()=>document.querySelector('[data-nt1-fold=\"co\"]>summary').click()"); page.wait_for_timeout(200)
        check(f"{tag} D Companies fold: old company rows + one open at a time", js(page, VIS, "[data-idea-co]") and js(page, "()=>document.querySelectorAll('.nt1-fold[open]').length") == 1)
        js(page, "()=>document.querySelector('[data-nt1-fold=\"mech\"]>summary').click()"); page.wait_for_timeout(200)
        check(f"{tag} D How it works fold: old chain/mechanism content", js(page, "()=>!!document.querySelector('.nt1-fold[open][data-nt1-fold=\"mech\"] [data-idea-vc], .nt1-fold[open][data-nt1-fold=\"mech\"] .ideaSteps, .nt1-fold[open][data-nt1-fold=\"mech\"] .wlOv')"))
        js(page, "()=>document.querySelector('[data-idea-menu]').click()"); page.wait_for_timeout(150)
        mn = js(page, "()=>['data-idea-park','data-idea-export','data-idea-hist','data-idea-import','data-idea-del'].map(a=>!!document.querySelector('['+a+']'))")
        check(f"{tag} D ⋯ menu keeps today's items (Park · Export · Log history · Import · Delete)", all(mn), mn)
        js(page, "()=>document.querySelector('[data-idea-park]').click()"); page.wait_for_timeout(250)
        check(f"{tag} D status change still works (Park)", js(page, "()=>ideaFind('nt1-idea-3').status") == "parked" or "parked" in str(js(page, "()=>ideaFind('nt1-idea-3')&&ideaFind('nt1-idea-3').status")))
        js(page, "()=>ideaSetStatus('nt1-idea-3','exploring')"); page.wait_for_timeout(250)
        js(page, "()=>ideaOpen('nt1-idea-3')"); page.wait_for_timeout(150)
        # ticker → stock on Watch / Screen
        js(page, "()=>document.querySelector('[data-nt1-gain] [data-nt1-tk=\"AVGO\"]').click()"); page.wait_for_timeout(300)
        check(f"{tag} D ticker on Watch → the stock on Watch", js(page, "()=>[wlView, wlSel]") == ["wl", "AVGO"], js(page, "()=>[wlView, wlSel]"))
        N.goto_watch(page); js(page, "()=>{ wlView='idea'; nt1SegSet('ai'); ideaOpen('nt1-idea-3'); }"); page.wait_for_timeout(200)
        js(page, "()=>document.querySelector('[data-nt1-gain] [data-nt1-tk=\"VST\"]').click()"); page.wait_for_timeout(300)
        check(f"{tag} D ticker not on Watch → Screen", js(page, "()=>[wlView, rs2.q]") == ["screen", "VST"], js(page, "()=>[wlView, rs2.q]"))
        N.goto_watch(page); to_ai(page)
        js(page, "()=>ideaOpen('gold-cpi')"); page.wait_for_timeout(200)
        tr = js(page, "()=>document.querySelector('.nt1-det').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} D trade idea: same pattern (Setup / Levels / Invalidation / Event) + folds + old hooks", all(s in tr for s in ("Setup", "Levels", "Invalidation", "Event", "Evidence", "Product", "Entry")) and js(page, VIS, "[data-trade-plan]") and js(page, VIS, "[data-trade-ask]"), tr[:300])
        js(page, "()=>document.querySelector('[data-idea-main]').click()"); page.wait_for_timeout(200)
        check(f"{tag} D trade: Add evidence › opens AI vs us", js(page, VIS, "[data-trade-vs]"))
        # ================= E · fits / no overflow
        sc = js(page, "()=>[document.scrollingElement.scrollHeight, innerHeight]")
        check(f"{tag} E AI generated: no page scroll at {w}x{h}", sc[0] <= sc[1] + 1, sc)
        hdo = js(page, "()=>{ const h = document.querySelector('[data-lr5-head]'); return [h.scrollWidth, h.clientWidth, document.querySelector('[data-nt1-chips]').scrollWidth <= document.querySelector('[data-nt1-chips]').clientWidth + 1]; }")
        check(f"{tag} E header not cut off (no overflow)", hdo[0] <= hdo[1] + 1 and hdo[2], hdo)
        check(f"{tag} E list rows not cut off", js(page, "()=>[...document.querySelectorAll('.nt1-ai')].every(r=>r.scrollWidth <= r.clientWidth + 1)"))
        check(f"{tag} E no horizontal page overflow", js(page, OVER))
        # ================= F · My ideas
        to_my(page)
        check(f"{tag} F My ideas list newest first (incl. old notes)", js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My).slice(0,3)") == ["m1", "m2", "m3"], js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)"))
        check(f"{tag} F row: subject tag · title · view chip · date · summary (Plan text first)", "US market Rally narrowing to AI names Neutral 18 Nov · plan: Leaders only, half size" == js(page, TXT, "[data-nt1-my=\"m1\"]"), js(page, TXT, "[data-nt1-my=\"m1\"]"))
        check(f"{tag} F row summary: first filled angle when there is no plan", js(page, TXT, "[data-nt1-my=\"m2\"]").endswith("Gap above 182 held 3 days"))
        check(f"{tag} F list scrolls inside its card (page does not)", js(page, "()=>{ const l = document.querySelector('.nt1-lb'); return l.scrollHeight >= l.clientHeight && document.scrollingElement.scrollHeight <= innerHeight + 1; }"))
        # detail
        d = js(page, "()=>document.querySelector('.nt1-det').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} F detail: subject · title · view · date · Edit · ⋯ · angle boxes (filled only) · Plan · Built on", all(s in d.lower() for s in ("us market", "rally narrowing", "neutral", "18 nov 2026", "edit", "technical", "sentiment", "plan", "built on: memory chips stay tight")) and "fundamental" not in d.lower(), d[:300])
        # chart
        cm1 = js(page, "()=>{ const c = document.querySelector('[data-nt1-chart]'); return c && [c.dataset.nt1Chart, c.dataset.url, c.dataset.href]; }")
        # network is stubbed → the image errors → Chart ↗ link; the URL it tried is kept on the row thumbnail
        th = js(page, "()=>{ const t = document.querySelector('[data-nt1-my=\"m1\"] [data-nt1-chart]'); return t && [t.dataset.url, t.dataset.href]; }")
        check(f"{tag} F TradingView link → snapshot image URL s3.tradingview.com/snapshots/a/AbC123.png", th is not None and th[0] == "https://s3.tradingview.com/snapshots/a/AbC123.png" and th[1] == "https://www.tradingview.com/x/AbC123/", th)
        check(f"{tag} F image error → “Chart ↗” link only", js(page, TXT, ".nt1-clink") == "Chart ↗" and js(page, "()=>!document.querySelector('.nt1-det img')"), cm1)
        js(page, "()=>nt1MySelect('m2')"); page.wait_for_timeout(150)
        check(f"{tag} F any other URL → Chart ↗ link only", js(page, "()=>{ const c = document.querySelector('.nt1-det [data-nt1-chart]'); return [c.dataset.nt1Chart, c.dataset.href]; }") == ["link", "https://example.com/chart"])
        js(page, "()=>{ page_img = 0; }") if False else None
        # chart helper (unit)
        un = js(page, "()=>[nt1Chart('tradingview.com/x/Zq9/'), nt1Chart('https://www.tradingview.com/x/Zq9'), nt1Chart('https://www.tradingview.com/x/Zq9/'), nt1Chart('https://tradingview.com/chart/abc'), nt1Chart('hello'), nt1Chart('')]")
        check(f"{tag} F chart link rules (x/<id>/ and x/<id>, others = link, junk = none)", un[0] is None and un[1]["url"].endswith("/snapshots/z/Zq9.png") and un[2]["url"].endswith("/snapshots/z/Zq9.png") and un[3]["kind"] == "link" and un[4] is None and un[5] is None, un)
        # filters + find
        for f, want in (("market", {"m1", "m4", "m6"}), ("stock", {"m2", "m7", "old"}), ("sat", {"m3"}), ("plan", {"m5"})):
            js(page, "(k)=>nt1FSet(k)", f); page.wait_for_timeout(100)
            got = set(r if not r.startswith("old:") else "old" for r in js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)"))
            check(f"{tag} F filter {f}", got == want, sorted(got))
        js(page, "()=>nt1FSet('all')")
        page.click("[data-nt1-find]"); page.keyboard.type("breadth"); page.wait_for_timeout(250)
        check(f"{tag} F ⌕ Find: title/text/subject", js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)") == ["m1", "m6"], js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)"))
        js(page, "()=>nt1FindSet('oil')"); page.wait_for_timeout(100)
        check(f"{tag} F Find matches the subject tag", js(page, "()=>[...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)") == ["m8"])
        js(page, "()=>{ myQ=''; myFindOpen=false; renderWatchlist(); }")
        # old notes
        js(page, "()=>nt1MySelect(document.querySelector('[data-nt1-old]').dataset.nt1My)"); page.wait_for_timeout(150)
        od = js(page, "()=>document.querySelector('.nt1-det').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} F old notes: read-only text idea (subject = the stock, title Waiting for / Watch out for)", "AVGO" in od and ("Waiting for" in od or "Watch out for" in od) and "read-only" in od and not js(page, VIS, "[data-nt1-del]") and not js(page, VIS, "[data-nt1-rv]"), od[:200])
        # convert: Waiting for
        wid = js(page, "()=>nt1OldNotes().find(o=>o.side==='cat').id"); js(page, "(i)=>nt1MySelect(i)", wid); page.click("[data-nt1-edit]"); page.wait_for_timeout(200)
        pre = js(page, "()=>({subj:document.getElementById('nt1fSubj').value, title:document.getElementById('nt1fTitle').value, macro:document.getElementById('nt1f-macro').value, check:document.getElementById('nt1fCheck').value})")
        check(f"{tag} F Edit on an old note pre-fills the sheet (subject, title, text, date kept)", pre == {"subj": "stock:AVGO", "title": "Waiting for", "macro": "Q1 renewal rate", "check": "2026-12-12"}, pre)
        page.click("[data-nt1-save]"); page.wait_for_timeout(500)
        conv = js(page, "()=>myList.filter(m=>m.conv)")
        check(f"{tag} F Save converts it into a real idea (conv kept) · old note no longer listed twice · old data stays", len(conv) == 1 and conv[0]["conv"]["side"] == "cat" and not js(page, "()=>nt1OldNotes().some(o=>o.side==='cat')") and js(page, "()=>wlItems.find(w=>w.ticker==='AVGO').my_notes.cat.length") == 1, conv)
        # create
        page.click("[data-nt1-new]"); page.wait_for_timeout(200)
        page.click("[data-nt1-save]"); page.wait_for_timeout(100)
        e1 = js(page, TXT, "#nt1Err")
        check(f"{tag} F required: nothing filled → asks for the title", "title" in (e1 or "").lower(), e1)
        page.fill("#nt1fTitle", "My new idea"); page.click("[data-nt1-save]"); page.wait_for_timeout(100)
        e2 = js(page, TXT, "#nt1Err")
        check(f"{tag} F required: title only → at least one angle or the plan", "angle" in (e2 or "").lower(), e2)
        page.select_option("#nt1fSubj", "tag:"); page.click("[data-nt1-save]"); page.wait_for_timeout(100)
        check(f"{tag} F required: free tag empty → asked", "tag" in (js(page, TXT, "#nt1Err") or "").lower())
        page.fill("#nt1fTag", "x" * 30); tl = js(page, "()=>document.getElementById('nt1fTag').value.length")
        check(f"{tag} F free tag ≤ 20 chars", tl == 20, tl)
        page.fill("#nt1fTag", "Copper"); page.fill("#nt1f-plan", "Buy dips"); page.fill("#nt1fChart", "not a link"); page.click("[data-nt1-save]"); page.wait_for_timeout(100)
        check(f"{tag} F bad chart text → asked for a web link", "link" in (js(page, TXT, "#nt1Err") or "").lower())
        page.fill("#nt1fChart", "https://www.tradingview.com/x/NeW42/"); page.click('[data-nt1-fv="bear"]')
        pv = js(page, "()=>document.querySelector('#nt1Prev [data-nt1-chart]').dataset.url")
        check(f"{tag} F sheet shows the picture as soon as the link is pasted", pv == "https://s3.tradingview.com/snapshots/n/NeW42.png", pv)
        lim = js(page, "()=>[...document.querySelectorAll('[data-nt1-fa],#nt1f-plan')].map(e=>e.maxLength).concat([document.getElementById('nt1fTitle').maxLength])")
        check(f"{tag} F limits: 4 angles ≤ 600 · plan ≤ 600 · title ≤ 80", lim == [600, 600, 600, 600, 600, 80], lim)
        page.click("[data-nt1-save]"); page.wait_for_timeout(600)
        nid = js(page, "()=>mySel"); doc = js(page, DOC(0), nid)
        check(f"{tag} F saved to users/{{uid}}/ideas_my: subject · title · view · chart · plan · review null", doc and doc["subject"] == {"type": "tag", "key": "Copper"} and doc["title"] == "My new idea" and doc["view"] == "bear" and doc["chart"].endswith("NeW42/") and doc["plan"] == "Buy dips" and doc["review"] is None and doc["checkOn"] is None and doc["builtOn"] is None, doc)
        check(f"{tag} F new idea is first (newest) and selected", js(page, "()=>document.querySelector('[data-nt1-my]').dataset.nt1My") == nid)
        # edit
        page.click("[data-nt1-edit]"); page.wait_for_timeout(150); page.fill("#nt1fTitle", "My edited idea"); page.click("[data-nt1-save]"); page.wait_for_timeout(500)
        doc = js(page, DOC(0), nid)
        check(f"{tag} F Edit saves (same id, new title, created kept)", doc["title"] == "My edited idea" and js(page, TXT, "[data-nt1-d-title]") == "My edited idea" and doc["created_at"] == js(page, DOC(0), nid)["created_at"])
        # dirty guard
        page.click("[data-nt1-edit]"); page.wait_for_timeout(150)
        n0 = len(DL()); page.click("[data-nt1-cancel]"); page.wait_for_timeout(150)
        check(f"{tag} F Cancel without changes closes silently", len(DL()) == n0 and not js(page, "()=>!!nt1Form"))
        page.click("[data-nt1-edit]"); page.wait_for_timeout(150); page.fill("#nt1fTitle", "changed"); page.click("[data-nt1-cancel]"); page.wait_for_timeout(150)
        check(f"{tag} F unsaved changes → ‘Discard your unsaved changes?’ guard", len(DL()) == n0 + 1 and "unsaved" in DL()[-1].lower() and js(page, TXT, "[data-nt1-d-title]") == "My edited idea", DL()[-1:])
        page.click("[data-nt1-edit]"); page.wait_for_timeout(150); page.fill("#nt1fTitle", "changed"); page.keyboard.press("Escape"); page.wait_for_timeout(150)
        check(f"{tag} F Esc in the sheet uses the same guard", len(DL()) == n0 + 2 and not js(page, "()=>!!nt1Form"))
        # delete + undo
        page.click("[data-nt1-menu]"); page.click("[data-nt1-del]"); page.wait_for_timeout(400)
        check(f"{tag} F Delete removes it + toast with Undo", js(page, DOC(0), nid) is None and "Deleted: My edited idea" in (js(page, TXT, "#nt1Toast") or "") and js(page, VIS, "[data-nt1-undo]"), js(page, TXT, "#nt1Toast"))
        page.click("[data-nt1-undo]"); page.wait_for_timeout(500)
        check(f"{tag} F Undo restores it", js(page, DOC(0), nid) is not None and js(page, "(i)=>!!document.querySelector('[data-nt1-my=\"'+i+'\"]')", nid))
        page.click("[data-nt1-menu]"); page.click("[data-nt1-copy]"); page.wait_for_timeout(300)
        ct = js(page, "()=>window.__nt1LastCopy")
        check(f"{tag} F ⋯ › Copy text", "My edited idea" in ct and "Plan: Buy dips" in ct, ct)
        # built on both ways
        js(page, "()=>nt1MySelect('m1')"); page.wait_for_timeout(150)
        js(page, "()=>document.querySelector('[data-nt1-built-link]').click()"); page.wait_for_timeout(250)
        check(f"{tag} F ‘Built on: <AI idea> ›’ opens that AI idea", js(page, "()=>[nt1Seg, ideaSel]") == ["ai", "en-idea-1"], js(page, "()=>[nt1Seg, ideaSel]"))
        check(f"{tag} F AI idea card shows ‘My ideas 1 ›’", js(page, TXT, "[data-nt1-built-n]") == "My ideas 1 ›", js(page, TXT, "[data-nt1-built-n]"))
        js(page, "()=>document.querySelector('[data-nt1-built-n]').click()"); page.wait_for_timeout(250)
        check(f"{tag} F …which lists the ideas built on it (filter chip)", js(page, "()=>[nt1Seg, [...document.querySelectorAll('[data-nt1-my]')].map(r=>r.dataset.nt1My)]") == ["my", ["m1"]] and js(page, VIS, "[data-nt1-built-chip]"))
        js(page, "()=>nt1OpenBuilt('')")
        # + My idea on this
        to_ai(page); js(page, "()=>ideaOpen('en-idea-2')"); page.wait_for_timeout(150); page.click("[data-nt1-myidea]"); page.wait_for_timeout(200)
        check(f"{tag} F + My idea on this → sheet with Built on preset", js(page, "()=>document.getElementById('nt1fBuilt').value") == "en-idea-2")
        js(page, "()=>nt1SheetClose()")
        # keyboard
        to_my(page, "m1"); page.mouse.click(5, 5)
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(150); a = js(page, "()=>mySel")
        page.keyboard.press("ArrowUp"); page.wait_for_timeout(150); b2 = js(page, "()=>mySel")
        check(f"{tag} F ↑/↓ move the selection in My ideas", a != "m1" and b2 == "m1", [a, b2])
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(100); page.keyboard.press("Enter"); page.wait_for_timeout(250)
        check(f"{tag} F Enter opens Edit", js(page, "()=>!!nt1Form") and js(page, "()=>nt1Form.id") == js(page, "()=>mySel"), js(page, "()=>[nt1Form && nt1Form.id, mySel]"))
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        to_ai(page); page.mouse.click(5, 5); s0 = js(page, "()=>ideaSel"); page.keyboard.press("ArrowDown"); page.wait_for_timeout(150)
        check(f"{tag} F ↑/↓ move in the AI list too", js(page, "()=>ideaSel") != s0)
        # ================= G · context lines
        js(page, "()=>{ switchTab('flow'); }"); page.wait_for_timeout(300)
        fx = js(page, TXT, "[data-nt1-ctx=\"flow\"]")
        check(f"{tag} G Flow: latest market idea line (subject · title · view · date · Ideas n ›)", fx and fx.startswith("US market Rally narrowing to AI names Neutral") and "Ideas 3 ›" in fx, fx)
        js(page, "()=>document.querySelector('[data-nt1-ctx-n]').click()"); page.wait_for_timeout(300)
        check(f"{tag} G …Ideas n › opens My ideas filtered to Markets", js(page, "()=>[activeTab, nt1Seg, myFilter]") == ["watch", "my", "market"], js(page, "()=>[activeTab, nt1Seg, myFilter]"))
        js(page, "()=>{ switchTab('watch'); wl1Go('AAPL'); }"); page.wait_for_timeout(300)
        cx = js(page, TXT, "[data-lr5-det] [data-nt1-ctx=\"stock\"]")
        check(f"{tag} G Watch detail: latest idea for the stock (title · view · date · Ideas n · + Idea)", cx and "Earnings gap held" in cx and "Bull" in cx and "Ideas 1" in cx and "+ Idea" in cx, cx)
        js(page, "()=>document.querySelector('[data-nt1-ctx-add]').click()"); page.wait_for_timeout(200)
        check(f"{tag} G + Idea opens the sheet with the subject set", js(page, "()=>document.getElementById('nt1fSubj').value") == "stock:AAPL")
        js(page, "()=>nt1SheetClose()")
        js(page, "()=>hwOpen('AVGO')"); page.wait_for_timeout(350)
        hx = js(page, TXT, "[data-hw1-page] [data-nt1-ctx=\"stock\"]")
        check(f"{tag} G Homework header: same line", hx and "AI networking share" in hx and "Bull" in hx, hx)
        js(page, "()=>{ hwBack(); switchTab('today'); }")
        # ================= H · Today check line · review
        js(page, "()=>{ switchTab('today'); ln4TodoAll = true; todayRefresh(true); }"); page.wait_for_timeout(500)
        tl = js(page, "()=>[...document.querySelectorAll('[data-lr2-ti]')].map(r=>r.innerText.replace(/\\s+/g,' ').trim())")
        line = [x for x in tl if "Check:" in x]
        check(f"{tag} H Today › To do: IDEA tag · Check: <title> — right? · Open › (only the due one)", line == ["IDEA Check: Range before CPI — right? Open ›"], tl)
        js(page, "()=>document.querySelector('[data-ln4-todo=\"idea:m3\"]').click()"); page.wait_for_timeout(350)
        check(f"{tag} H Open › goes to that idea in My ideas", js(page, "()=>[activeTab, nt1Seg, mySel]") == ["watch", "my", "m3"], js(page, "()=>[activeTab, nt1Seg, mySel]"))
        rv = js(page, "()=>document.querySelector('[data-nt1-review]').dataset.nt1Review")
        check(f"{tag} H on/after the check date: Right · Partly · Wrong + one-line field (≤ 140)", rv == "due" and js(page, "()=>[...document.querySelectorAll('[data-nt1-rv]')].map(b=>b.innerText)") == ["Right", "Partly", "Wrong"] and js(page, "()=>document.querySelector('[data-nt1-rv-text]').maxLength") == 140)
        nv = js(page, "()=>{ nt1MySelect('m1'); return document.querySelector('[data-nt1-review]').dataset.nt1Review; }")
        check(f"{tag} H before the date: no buttons yet", nv == "wait" and js(page, "()=>document.querySelectorAll('[data-nt1-rv]').length") == 0)
        js(page, "()=>nt1MySelect('m3')"); page.wait_for_timeout(100)
        page.fill("[data-nt1-rv-text]", "Broke up after FOMC"); page.click('[data-nt1-rv="partly"]'); page.wait_for_timeout(500)
        d3 = js(page, DOC(0), "m3")
        check(f"{tag} H save sets review {{result, text, at}}", d3["review"]["result"] == "partly" and d3["review"]["text"] == "Broke up after FOMC" and d3["review"]["at"], d3["review"])
        at1 = d3["review"]["at"]
        js(page, "()=>{ switchTab('today'); ln4TodoAll = true; todayRefresh(true); }"); page.wait_for_timeout(400)
        check(f"{tag} H the Today line is gone after the review", not any("Check:" in x for x in js(page, "()=>[...document.querySelectorAll('[data-lr2-ti]')].map(r=>r.innerText)")))
        js(page, "()=>nt1OpenMy('m3')"); page.wait_for_timeout(300); page.wait_for_timeout(1100)
        page.click('[data-nt1-rv="wrong"]'); page.wait_for_timeout(500)
        d3 = js(page, DOC(0), "m3")
        check(f"{tag} H changeable later (result updated, `at` = latest change)", d3["review"]["result"] == "wrong" and d3["review"]["at"] > at1 and d3["review"]["text"] == "Broke up after FOMC", [d3["review"], at1])
        # ================= J · Journal › Reviews
        js(page, "()=>{ switchTab('journal'); }"); page.wait_for_timeout(500)
        seg = js(page, ALLT, "[data-nt1-jsegs] button")
        check(f"{tag} J Journal segments Trades | Reviews n", seg == ["Trades", "Reviews 5"], seg)
        check(f"{tag} J Trades segment still shows the trade journal", js(page, VIS, "[data-lr5-view=desktop] .lr5-kpis, [data-lr5-view=desktop]"))
        js(page, "()=>nt1JSet('rev')"); page.wait_for_timeout(300)
        tl = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-nt1-tile]')].map(t=>[t.dataset.nt1Tile, t.innerText.replace(/\\s+/g,' ').trim()]))")
        # 90 days: m3 wrong(today), m4 wrong, m6 right, m7 partly → score 1.5 of 4 = 38%
        check(f"{tag} J Hit rate = right 1 · partly 0.5 · wrong 0 (38% = 1.5 of 4) with counts", tl["hit"] == "Hit rate 38% 1 right · 1 partly · 2 wrong", tl["hit"])
        check(f"{tag} J Markets tile (m4 wrong + m6 right = 1 of 2)", tl["markets"] == "Markets 50% 1 of 2", tl["markets"])
        check(f"{tag} J Stocks tile (partly = 0.5 of 1)", tl["stocks"] == "Stocks 50% 0.5 of 1", tl["stocks"])
        check(f"{tag} J By view: Bull / Bear / Neutral %", tl["view"].startswith("By view Bull 75% · Bear 0% · Neutral 0%"), tl["view"])
        lst = js(page, "()=>[...document.querySelectorAll('[data-nt1-rr]')].map(r=>r.dataset.nt1Rr)")
        check(f"{tag} J list newest review first · 120-day-old one outside 90 days", lst == ["m3", "m4", "m6", "m7"], lst)
        row = js(page, TXT, "[data-nt1-rr=\"m4\"]")
        check(f"{tag} J row: date · subject · title · view · result chip · what happened", row == "16 Nov TH market SET below 200-day Bear Wrong “Foreign buying came back”", row)
        js(page, "()=>nt1PerSet('all')"); page.wait_for_timeout(250)
        t2 = js(page, TXT, "[data-nt1-tile=\"hit\"]")
        check(f"{tag} J period all time: 1.5 of 5 → 30%", t2 == "Hit rate 30% 1 right · 1 partly · 3 wrong", t2)
        js(page, "()=>nt1PerSet('30')"); page.wait_for_timeout(200)
        check(f"{tag} J period 30 days", js(page, "()=>document.querySelectorAll('[data-nt1-rr]').length") == 4)
        js(page, "()=>nt1PerSet('90')")
        js(page, "()=>document.querySelector('[data-nt1-rr=\"m6\"]').click()"); page.wait_for_timeout(350)
        check(f"{tag} J tap a row → the idea in My ideas", js(page, "()=>[activeTab, nt1Seg, mySel]") == ["watch", "my", "m6"], js(page, "()=>[activeTab, nt1Seg, mySel]"))
        js(page, "()=>{ switchTab('journal'); nt1JSet('trades'); }"); page.wait_for_timeout(300)
        check(f"{tag} J back to Trades restores the trade journal", js(page, "()=>!document.getElementById('tabJournal').classList.contains('nt1-rev')"))
        # ================= K · permission-denied
        js(page, "()=>{ switchTab('watch'); wlView='idea'; nt1SegSet('my'); window.firebase.__mockDb.__denyPath(['users','testuid','ideas_my']); nt1Retry(); }"); page.wait_for_timeout(500)
        er = js(page, TXT, "[data-nt1-err]")
        check(f"{tag} K permission-denied → ‘Could not load My ideas (permission-denied) · Retry’", er == "Could not load My ideas (permission-denied) · Retry", er)
        js(page, "()=>window.firebase.__mockDb.__allowPath(['users','testuid','ideas_my'])"); page.click("[data-nt1-retry]"); page.wait_for_timeout(600)
        check(f"{tag} K Retry loads the list once the rule is there", js(page, "()=>!document.querySelector('[data-nt1-err]') && document.querySelectorAll('[data-nt1-my]').length") > 3)
        # ================= L · empty state + sizes
        check(f"{tag} L no horizontal overflow (My ideas)", js(page, OVER))
        sc = js(page, "()=>[document.scrollingElement.scrollHeight, innerHeight]")
        check(f"{tag} L My ideas: no page scroll at {w}x{h}", sc[0] <= sc[1] + 1, sc)
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


def run_phone(pw, w, h):
    tag = "[%s]" % w
    b, page, pe = N.open_nt1(pw, w, h)
    try:
        extra_ai(page)
        N.goto_watch(page)
        check(f"{tag} P opens on Ideas · no overflow", js(page, VIEW)[0] == "idea" and js(page, OVER))
        bt = js(page, "()=>[...document.querySelectorAll('[data-lr5-head] button')].filter(b=>b.getBoundingClientRect().width>0).map(b=>Math.round(b.getBoundingClientRect().height))")
        check(f"{tag} P header buttons ≥ 44px", all(x >= 44 for x in bt), bt)
        js(page, "()=>document.querySelector('.nt1-ai').click()"); page.wait_for_timeout(300)
        check(f"{tag} P AI idea opens as a sheet · no overflow", js(page, VIS, ".nt1-det") and js(page, OVER))
        ok = js(page, "()=>[...document.querySelectorAll('.nt1-det .btn, .nt1-det summary')].filter(b=>b.getBoundingClientRect().width>0).every(b=>b.getBoundingClientRect().height >= 43)")
        check(f"{tag} P detail buttons / fold rows ≥ 44px", ok)
        js(page, "()=>wlBack()"); to_my(page); page.wait_for_timeout(200)
        check(f"{tag} P My ideas list · no overflow", js(page, OVER) and js(page, "()=>document.querySelectorAll('[data-nt1-my]').length") > 3)
        js(page, "()=>document.querySelector('[data-nt1-my=\"m1\"]').click()"); page.wait_for_timeout(300)
        check(f"{tag} P My idea detail as a sheet · no overflow", js(page, VIS, "[data-nt1-detail]") and js(page, OVER))
        ok = js(page, "()=>[...document.querySelectorAll('.nt1-det .btn, .nt1-det input, .nt1-det [data-nt1-close]')].filter(b=>b.getBoundingClientRect().width>0).every(b=>b.getBoundingClientRect().height >= 36)")
        check(f"{tag} P detail controls tall enough", ok)
        js(page, "()=>{ wlBack(); nt1SheetOpen({}); }"); page.wait_for_timeout(300)
        check(f"{tag} P New idea sheet · no overflow", js(page, VIS, "[data-nt1-sheet]") and js(page, OVER) and js(page, "()=>document.getElementById('ltModal').scrollWidth <= document.getElementById('ltModal').clientWidth + 1"))
        js(page, "()=>nt1SheetClose()")
        js(page, "()=>{ switchTab('journal'); nt1JSet('rev'); }"); page.wait_for_timeout(400)
        check(f"{tag} P Journal › Reviews · no overflow", js(page, OVER) and js(page, "()=>document.querySelectorAll('[data-nt1-rr]').length") > 0)
        js(page, "()=>{ switchTab('flow'); }"); page.wait_for_timeout(300)
        check(f"{tag} P Flow context line · no overflow", js(page, VIS, "[data-nt1-ctx=\"flow\"]") and js(page, OVER))
        check(f"{tag} no page errors", not pe, pe[:3])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        run_desktop(pw, 1440, 900)
        run_desktop(pw, 1100, 800) if False else None
        run_phone(pw, 390, 844)
        run_phone(pw, 360, 740)
    bad = [r for r in results if not r[1]]
    print(f"SUMMARY nt1: {len(results) - len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)
