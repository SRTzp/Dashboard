#!/usr/bin/env python3
"""WK1 — Weekend = one list in routine order (SAT · CORE · OVERVIEW) · ⑤ New ideas · ⑥ Raise stops · ⑦ change_if · Copy prompt/Paste JSON when data missing
· news read per item (✓ toggle · Unread|All · Mark all read) · Today Daily news line = one button · เทส 366 · Chromium · 390 + 1440 · SAMPLE data only
นาฬิกาปลอม พฤ. 1 ต.ค. 2026 12:00 ICT (สัปดาห์ 28 ก.ย. – 4 ต.ค.) · รัน: python3 run_tests_phase366.py"""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase44 as P44
import run_tests_phase106 as T

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = T.settle
cnt, txt, S = T.cnt, T.txt, T.S
NOW, WEEK = T.NOW, T.WEEK
ED = "2026-09-28"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def trade(i, sl, bias="Long", entry=100):
    return {"id": f"t{i}", "status": "open", "port": "core", "bias": bias, "sym": f"S{i}", "entry": entry, "qty": 10, "sl": sl, "mult": 1, "date": "2026-09-20", "openedAt": "2026-09-20"}


def set_trades(page, main, fam=()):
    js(page, "([m,f])=>{ const A=getBook('main'); A.trades=m; saveBook('main'); const B=getBook('fam'); B.trades=f; saveBook('fam'); render(); todayRefresh(true); }", [list(main), list(fam)])
    settle(page, 400)


def set_ideas(page, stamps):
    js(page, "(L)=>{ ideaList = L.map((s,i)=>({id:'i'+i, idea:{name:'I'+i}, log:[], imported_at:s})); todayRefresh(true); }", list(stamps)); settle(page, 300)


def seed_news(page, tickers=("AAA", "BBB", "CCC")):
    stocks = {t: {"coverage": "ok", "status": "review" if i == 0 else "info", "headline_th": f"{t} headline", "happened_th": f"{t} fact", "groups": ["watchlist"]} for i, t in enumerate(tickers)}
    js(page, "(L)=>{ window.stkLists = ()=>({wl:L, cand:[]}); }", list(tickers))
    page.evaluate("([id,st])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','stockNews',id], {stocks:st, period_start:'2026-09-28', period_end:'2026-10-02', asof:'2026-10-02T10:00:00+07:00', sources:{}}); stkStop(); stkStart(); }", [ED, stocks])
    settle(page, 800); js(page, "()=>todayRefresh(true)"); settle(page, 300)


def weekend(page):
    page.locator('[data-td3-tab="w"]').click(); settle(page, 400)


def ids(page): return js(page, "()=>[...document.querySelectorAll('[data-td3-wk]')].map(e=>e.dataset.td3Wk)")
def done(page, i): return js(page, "(i)=>document.querySelector('[data-td3-wk=\"'+i+'\"]').dataset.done", i)
def sub(page, i): return txt(page, f'[data-td3-wk="{i}"] [data-td3-wsub]')
def mon(page): return js(page, "()=>tdMonday(thaiToday())")


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h, iso=NOW, picks=(), weekly=False)
    try:
        set_trades(page, [], [])
        T.go_today(page); weekend(page)
        # ── 1 order · tags · header · bar ──
        check(f"{tag} 1 Weekend = ONE list of 7 in routine order", ids(page) == ["wk_impact", "wk_assets", "wk_news", "wk_cands", "wk_ideas", "wk_stops", "wk_chg"], ids(page))
        check(f"{tag} 1 one panel only (no Overview/Core/Satellite panels)", cnt(page, "[data-td3-panels] > [data-td3-panel]") == 1 and cnt(page, '[data-td3-panel="week"]') == 1 and cnt(page, '[data-td3-panel="ov"],[data-td3-panel="core"],[data-td3-panel="sat"]') == 0)
        tags = js(page, "()=>[...document.querySelectorAll('[data-td3-wk]')].map(e=>e.querySelector('[data-td3-gt]').innerText)")
        check(f"{tag} 1 group tags SAT · SAT · CORE · CORE · OVERVIEW · CORE · OVERVIEW", tags == ["SAT", "SAT", "CORE", "CORE", "OVERVIEW", "CORE", "OVERVIEW"], tags)
        nums = js(page, "()=>[...document.querySelectorAll('[data-td3-wk]')].map(e=>e.querySelector('.td3-ck').innerText)")
        # stops auto-ticked (no positions) → ⑥ shows ✓
        check(f"{tag} 1 rows numbered 1..7 (✓ when done)", nums == ["1", "2", "3", "4", "5", "✓", "7"], nums)
        hd = txt(page, "[data-td3-panel=week] .td3-wkh")
        check(f"{tag} 1 header 'Weekend review · n/N done · ~45 min' (n/N = counted items: 1/7 — Raise stops auto-ticks with no positions)", hd == "Weekend review · 1/7 done · ~45 min", hd)
        bar = js(page, "()=>{ const b=document.querySelector('[data-td3-bar]'); return [b.getAttribute('aria-valuenow'), b.getAttribute('aria-valuemax'), b.firstElementChild.style.width]; }")
        check(f"{tag} 1 progress bar matches n/N (1/7 = 14%)", bar == ["1", "7", "14%"], bar)
        sw = txt(page, "[data-td3-badge]")
        check(f"{tag} 1 Weekend tab badge uses the same n/N", sw == "1/7", sw)
        # ── 2 ⑤ ideas ──
        set_ideas(page, ["2026-09-20T03:00:00Z", "2026-10-05T03:00:00Z"])   # last week · next week
        check(f"{tag} 5 ideas of other weeks are not counted → 'New ideas 0/2' · not ticked · button 'Flow ›'", "New ideas 0/2" in txt(page, '[data-td3-wk="wk_ideas"] .nm') and done(page, "wk_ideas") == "false" and txt(page, '[data-td3-wk="wk_ideas"] [data-td3-wgo]') == "Flow ›" and "Flow › Fresh → Ask why › → idea-scout" in sub(page, "wk_ideas"), [txt(page, '[data-td3-wk="wk_ideas"]')])
        set_ideas(page, ["2026-09-20T03:00:00Z", "2026-09-29T03:00:00Z", "2026-10-04T16:00:00Z", "2026-10-04T17:30:00Z"])   # Mon · Sun 23:00 ICT in · Sun 00:30 ICT next-Mon out
        check(f"{tag} 5 counts Mon–Sun (ICT) only: Mon + Sun 23:00 in, last week + Mon 00:30 ICT out → 2/2 · auto ✓", "New ideas 2/2" in txt(page, '[data-td3-wk="wk_ideas"] .nm') and done(page, "wk_ideas") == "true" and cnt(page, '[data-td3-wauto="wk_ideas"]') == 1, txt(page, '[data-td3-wk="wk_ideas"]'))
        set_ideas(page, ["2026-09-30T03:00:00Z"])
        check(f"{tag} 5 ≥ 1 this week → ticks itself", done(page, "wk_ideas") == "true" and "New ideas 1/2" in txt(page, '[data-td3-wk="wk_ideas"] .nm'))
        set_ideas(page, [])
        page.locator('[data-td3-wtick="wk_ideas"]').click(); settle(page, 400)
        check(f"{tag} 5 0 ideas → manual tick works and is stored in weekLog[Mon].done", done(page, "wk_ideas") == "true" and "wk_ideas" in S(page, "weekLog")[mon(page)]["done"])
        page.locator('[data-td3-wtick="wk_ideas"]').click(); settle(page, 300)
        # ── 3 ⑥ stops ──
        set_trades(page, [trade(1, 90), trade(2, 100), trade(3, 110)])   # stop < avg · = avg · > avg
        s6 = sub(page, "wk_stops")
        check(f"{tag} 6 3 positions (stop<avg, =avg, >avg) → N=1: '1 position with stop below avg entry' · not ticked · Port ›", s6 == "1 position with stop below avg entry" and done(page, "wk_stops") == "false" and cnt(page, '[data-td3-wtick="wk_stops"]') == 1 and txt(page, '[data-td3-wk="wk_stops"] [data-td3-wgo]') == "Port ›", [s6, done(page, "wk_stops")])
        set_trades(page, [trade(1, 90), trade(2, 80), trade(3, 0)], [trade(4, 95)])   # 3 counted (2 main + 1 fam) · 1 without stop
        s6b = sub(page, "wk_stops")
        check(f"{tag} 6 counts every account · trades without a stop are not counted and the sub-text says so", s6b == "3 positions with stop below avg entry · 1 without a stop not counted", s6b)
        page.locator('[data-td3-wtick="wk_stops"]').click(); settle(page, 300)
        check(f"{tag} 6 N>0 → manual tick works", done(page, "wk_stops") == "true")
        page.locator('[data-td3-wtick="wk_stops"]').click(); settle(page, 300)
        set_trades(page, [trade(1, 100), trade(2, 105)])
        check(f"{tag} 6 N=0 → auto ✓ (no tick button)", done(page, "wk_stops") == "true" and cnt(page, '[data-td3-wauto="wk_stops"]') == 1 and cnt(page, '[data-td3-wtick="wk_stops"]') == 0)
        sh = trade(5, 110, "Short"); sh2 = trade(6, 90, "Short")
        set_trades(page, [sh, sh2])
        check(f"{tag} 6 Short mirrors it (stop above entry counts · at/below entry is locked)", "1 position with stop" in sub(page, "wk_stops") and done(page, "wk_stops") == "false", sub(page, "wk_stops"))
        set_trades(page, [])
        # ── 4 ⑦ change_if ──
        check(f"{tag} 7 change_if: hit status is not stored anywhere → manual tick (fallback) · Flow ›", cnt(page, '[data-td3-wtick="wk_chg"]') == 1 and txt(page, '[data-td3-wk="wk_chg"] [data-td3-wgo]') == "Flow ›" and done(page, "wk_chg") == "false")
        page.locator('[data-td3-wtick="wk_chg"]').click(); settle(page, 300)
        check(f"{tag} 7 manual tick stored", done(page, "wk_chg") == "true" and "wk_chg" in S(page, "weekLog")[mon(page)]["done"])
        page.locator('[data-td3-wtick="wk_chg"]').click(); settle(page, 300)
        # ── 5 missing data: Copy prompt / Paste JSON ──
        miss = js(page, "()=>[...document.querySelectorAll('[data-td3-wk]')].filter(e=>e.querySelector('[data-td3-wprompt]')).map(e=>e.dataset.td3Wk)")
        check(f"{tag} 1/3 no Weekly Impact + no news edition → 'Copy prompt ›' + 'Paste JSON ›' on ① and ③ only", miss == ["wk_impact", "wk_news"] and cnt(page, "[data-td3-wpaste]") == 2, miss)
        page.locator('[data-td3-wprompt="wi"]').click(); settle(page, 300)
        lp = js(page, "()=>window.__td3LastPrompt||''")
        check(f"{tag} ① Copy prompt → text starts with the skill name 'weekly-impact:' + manifest JSON", lp.startswith("weekly-impact:\n\n{") and '"assets"' in lp, lp[:80])
        page.locator('[data-td3-wpaste="wi"]').click(); settle(page, 400)
        check(f"{tag} ① Paste JSON ✓ opens the existing Weekly Impact paste sheet", cnt(page, ".wi-sheet") == 1)
        js(page, "()=>wiPasteClose()")
        page.evaluate("([w,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','weeklyImpact',w], b); wiStop(); wiStart(); }", [WEEK, T.P100_body()]); settle(page, 700)
        js(page, "()=>todayRefresh(true)"); settle(page, 300)
        check(f"{tag} ① data exists → Copy prompt / Paste JSON hidden · row auto ✓", cnt(page, '[data-td3-wk="wk_impact"] [data-td3-wprompt]') == 0 and done(page, "wk_impact") == "true")
        # ── 6 news per item ──
        seed_news(page)
        check(f"{tag} ③ edition present → no Copy prompt/Paste on ③ · sub '0/3 read'", cnt(page, '[data-td3-wk="wk_news"] [data-td3-wprompt]') == 0 and sub(page, "wk_news") == "0/3 read" and done(page, "wk_news") == "false", [sub(page, "wk_news")])
        weekend(page) if cnt(page, "[data-td3-wk]") == 0 else None
        page.locator('[data-td3-wgo="wk_news"]').click(); settle(page, 500)
        rows = js(page, "()=>[...document.querySelectorAll('[data-stk-row]')].map(e=>e.dataset.stkRow)")
        check(f"{tag} 6 news sheet: 3 items, each with its own ✓ toggle · filter Unread|All (default Unread) · 'Mark all read' · header '0/3 read'", len(rows) == 3 and cnt(page, "[data-stk-ck]") == 3 and js(page, "()=>document.querySelector('[data-stk-f=unread]').classList.contains('on')") and txt(page, "[data-stk-read]") == "Mark all read" and txt(page, "[data-stk-rc]") == "0/3 read", [rows, txt(page, "[data-stk-rc]")])
        check(f"{tag} 6 header 'Mark all read' stays on the title row (no wrap)", js(page, "()=>{ const h=document.querySelector('.stkBody .pbShH'), b=h.querySelector('[data-stk-read]'), t=h.querySelector('b'); return Math.abs(b.getBoundingClientRect().top - t.getBoundingClientRect().top) < 20 && h.scrollWidth <= h.clientWidth + 1; }"))
        page.locator('[data-stk-ck="AAA"]').click(); settle(page, 500)
        check(f"{tag} 6 tick one → sheet 1/3 · row hidden by the Unread filter", txt(page, "[data-stk-rc]") == "1/3 read" and cnt(page, '[data-stk-row="AAA"]') == 0 and cnt(page, "[data-stk-row]") == 2, txt(page, "[data-stk-rc]"))
        store = S(page, "stockNewsRead")
        check(f"{tag} 6 stored per item: stockNewsRead[edition] = {{readIds:[AAA]}}", store == {ED: {"readIds": ["AAA"]}}, store)
        check(f"{tag} 6 Weekend ③ shows 1/3 read · not ticked yet", sub(page, "wk_news") == "1/3 read" and done(page, "wk_news") == "false", sub(page, "wk_news"))
        page.locator('[data-stk-f="all"]').click(); settle(page, 300)
        faded = js(page, "()=>[...document.querySelectorAll('[data-stk-row]')].map(e=>[e.dataset.stkRow, e.classList.contains('rd'), getComputedStyle(e).opacity])")
        check(f"{tag} 6 filter All → 3 rows · the read one fades (opacity .5)", len(faded) == 3 and [f for f in faded if f[1]] == [["AAA", True, "0.5"]], faded)
        page.locator('[data-stk-ck="AAA"]').click(); settle(page, 400)
        check(f"{tag} 6 tap again = unread → 0/3 · store has no AAA", txt(page, "[data-stk-rc]") == "0/3 read" and S(page, "stockNewsRead")[ED]["readIds"] == [], S(page, "stockNewsRead"))
        page.locator('[data-stk-ck="BBB"]').click(); page.locator('[data-stk-ck="CCC"]').click(); settle(page, 400)
        page.locator('[data-stk-f="unread"]').click(); settle(page, 300)
        check(f"{tag} 6 2/3 read; Unread shows just the remaining one", txt(page, "[data-stk-rc]") == "2/3 read" and js(page, "()=>[...document.querySelectorAll('[data-stk-row]')].map(e=>e.dataset.stkRow)") == ["AAA"])
        page.locator("[data-stk-read]").click(); settle(page, 500)
        check(f"{tag} 6 Mark all read → 3/3 · 'All read ✓ · Show all' under Unread · button disabled", txt(page, "[data-stk-rc]") == "3/3 read" and cnt(page, "[data-stk-allread]") == 1 and "All read ✓ · Show all" in txt(page, "[data-stk-allread]") and js(page, "()=>document.querySelector('[data-stk-read]').disabled"), txt(page, "[data-stk-allread]"))
        page.locator("[data-stk-showall]").click(); settle(page, 300)
        check(f"{tag} 6 'Show all' → All filter, 3 rows", cnt(page, "[data-stk-row]") == 3 and js(page, "()=>document.querySelector('[data-stk-f=all]').classList.contains('on')"))
        check(f"{tag} 6 all read → Weekend ③ auto-ticks", done(page, "wk_news") == "true" and sub(page, "wk_news") == "3/3 read", sub(page, "wk_news"))
        js(page, "()=>stkCloseView()")
        # reload keeps state
        P44.reload_keep(page); js(page, "()=>{ window.stkLists = ()=>({wl:['AAA','BBB','CCC'], cand:[]}); }"); T.go_today(page); weekend(page)
        check(f"{tag} 6 reload keeps the read state (③ still done · 3/3)", done(page, "wk_news") == "true" and sub(page, "wk_news") == "3/3 read", [sub(page, "wk_news"), S(page, "stockNewsRead")])
        # legacy flag = all items read
        js(page, "()=>{ satSettingsWrite(stg=>{ stg.stockNewsRead = {'%s': true}; }); todayRefresh(true); }" % ED); settle(page, 500)
        check(f"{tag} 6 old edition-level read flag (true) → all items read (3/3) without rewriting", sub(page, "wk_news") == "3/3 read" and done(page, "wk_news") == "true" and S(page, "stockNewsRead") == {ED: True}, S(page, "stockNewsRead"))
        js(page, "()=>{ stkOpenView(); }"); settle(page, 400)
        page.locator('[data-stk-f="all"]').click(); settle(page, 300)
        page.locator('[data-stk-ck="BBB"]').click(); settle(page, 500)
        check(f"{tag} 6 un-tick from a legacy flag → expands to per-item (AAA, CCC stay read)", sorted(S(page, "stockNewsRead")[ED]["readIds"]) == ["AAA", "CCC"] and txt(page, "[data-stk-rc]") == "2/3 read", S(page, "stockNewsRead"))
        js(page, "()=>stkCloseView()")
        # ── 7 Daily line ──
        weekend(page) if False else None
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 400)
        page.locator('[data-td3-tab="d"]').click(); settle(page, 400)
        ln = js(page, "()=>{ const e=document.querySelector('[data-td3-wnews]'); if(!e) return null; const cs=getComputedStyle(e), b=e.querySelector('button'); return {tag:e.tagName, txt:e.innerText.replace(/\\s+/g,' ').trim(), inCore:!!e.closest('[data-td3-panel=core]'), nb:e.querySelectorAll('button').length, bt:b?b.innerText.trim():'', bw:b?getComputedStyle(b).borderTopStyle:'', border:cs.borderTopWidth, bg:cs.backgroundColor, dot:!!e.querySelector('.dot'), fs:cs.fontSize, tab:e.tabIndex, onclick:e.hasAttribute('onclick')}; }")
        check(f"{tag} 7 Daily line (Core panel): plain muted div 'Weekly News · 1/3 unread · Read ›' · no dot · no border · only the dashed Read › pill is a button", ln and ln["tag"] == "DIV" and ln["txt"] == "Weekly News · 1/3 unread · Read ›" and ln["inCore"] and ln["nb"] == 1 and ln["bt"] == "Read ›" and ln["bw"] == "dashed" and ln["border"] == "0px" and not ln["dot"] and not ln["onclick"], ln)
        page.locator("[data-td3-wnews] b, [data-td3-wnews]").first.click(position={"x": 8, "y": 6}); settle(page, 400)
        check(f"{tag} 7 tapping the text does nothing (sheet stays closed)", cnt(page, ".stk-sheet, .stk-panel") == 0)
        page.locator("[data-td3-wnews] button").click(); settle(page, 500)
        check(f"{tag} 7 the Read › pill opens the news sheet", cnt(page, ".stk-sheet, .stk-panel") == 1)
        js(page, "()=>stkCloseView()")
        page.focus("[data-td3-wnews] button"); page.keyboard.press("Enter"); settle(page, 400)
        check(f"{tag} 7 keyboard: Enter on the pill opens the sheet", cnt(page, ".stk-sheet, .stk-panel") == 1)
        check(f"{tag} 7 same small size as before (≤ 14.6px)", float(ln["fs"][:-2]) <= 14.6, ln["fs"])
        js(page, "()=>stkCloseView()")
        js(page, "()=>{ stkMarkRead('%s'); }" % ED); settle(page, 500)
        check(f"{tag} 7 all read → the line is hidden · no Watchlist-card/Plan-form news added", cnt(page, "[data-td3-wnews]") == 0 and cnt(page, "[data-wl-news],[data-plan-news]") == 0)
        # ── shots ──
        js(page, "()=>{ satSettingsWrite(stg=>{ stg.stockNewsRead = {'%s': {readIds:['AAA']}}; }); todayRefresh(true); }" % ED); settle(page, 400)
        weekend(page); js(page, "()=>document.querySelector('[data-td3-panel=week]').scrollIntoView({block:'start'})")
        C.shot(page, f"wk1-weekend-{w}.png", full=True)
        page.emulate_media(color_scheme="dark"); settle(page, 300)
        C.shot(page, f"wk1-weekend-dark-{w}.png", full=True)
        page.emulate_media(color_scheme="light")
        js(page, "()=>{ stkOpenView(); }"); settle(page, 400)
        C.shot(page, f"wk1-news-{w}.png")
        page.emulate_media(color_scheme="dark"); settle(page, 300)
        C.shot(page, f"wk1-news-dark-{w}.png")
        page.emulate_media(color_scheme="light")
        sx = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} no horizontal overflow (sheet open) · no console/page errors", sx <= 0 and not [x for x in ce if "Failed to load" not in x] and not pe, [sx, ce[:2], pe[:2]])
        js(page, "()=>stkCloseView()")
        T.go_today(page); weekend(page)
        check(f"{tag} no overflow on the Weekend list", T.ovf(page) <= 0, T.ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)): tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
