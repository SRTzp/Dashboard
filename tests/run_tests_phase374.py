#!/usr/bin/env python3
"""WL1 — Watch × TradingView workflow: split Watch (Momentum | Compounder), derived status, Import (WATCHLIST only), first-fill auto-add,
homework size cap (50% → 100%), Candidate list removed + export notice, TV1 export retired · เทส 374
Chromium · 390 (+360) + 1280 + 1440 · นาฬิกาปลอม พฤ. 1 ต.ค. 2026 12:00 ICT · SAMPLE data only
(เทส 368 = TV1 export/download — เลิกใช้: ฟีเจอร์ถูกถอดใน WL1 · Import ยังอยู่ และถูกแทนด้วยเคส Import ในไฟล์นี้)
รัน: python3 run_tests_phase374.py → tests/screenshots/wl1-*.png"""
import os, json, re, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import ln3fix_common as C   # ต้องมาก่อน
import lib_phase4 as base
import lib_phase13 as P13
import lib_phase24 as P24
import lib_phase38 as P38
import lib_phase120 as P120
import lib_phase106 as T

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle, cnt, txt = T.settle, T.cnt, T.txt
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots") + "/wl1-"


RETIRED_RE1C1 = ['Filled ✓ above the cap']   # RE-C1: only checks whose asserted behaviour the brief removes
def check(name, ok, detail=""):
    if any(p in name for p in RETIRED_RE1C1):
        print('RETIRED (RE-C1, not counted as PASS) - ' + name); return
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def wl_doc(t, trk=False, exch="NASDAQ", why="", exit_="", trigger="", confirmed=False, thesis=None):
    d = {"ticker": t, "market": "TH" if t.endswith(".BK") else "US", "port": "core", "note": "", "industry": "", "added_at": "2026-09-01T00:00:00Z",
         "ladder_watch": bool(trk), "ladder_state": "Base"}
    if exch: d["exch"] = exch
    if why or exit_: d["my_thesis"] = {"why": why, "exit": exit_, "updated_at": "2026-09-02T00:00:00Z"}
    hw = {}
    if trigger: hw["trigger"] = trigger
    if confirmed: hw["confirmedAt"] = "2026-09-03T00:00:00Z"; hw["doneAt"] = "2026-09-03T00:00:00Z"
    if hw: d["hw"] = hw
    if thesis is not None:
        d["thesis"] = {k: v for k, v in thesis.items() if k != "log"}; d["thesis_log"] = thesis.get("log", []); d["thesis_history"] = []; d["thesis_hits"] = {}
    return d


def put_wl(page, docs):
    for t, d in docs.items():
        page.evaluate("([t,d])=>window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist',t], d)", [t, d])
    js(page, "()=>{ wlStop(); wlStart(); }"); settle(page, 700)


def put_cards(page, cards):
    for cid, c in cards.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 800)


def put_trades(page, trades):
    js(page, "(t)=>{ const B=getBook('main'); B.trades=B.trades.concat(t); saveBook('main'); render(); }", trades)


def ps1(rows, stop, starter=None):
    return {"entry": rows[0][0], "stop": stop, "ps1": {"v": 1, "rows": [{"px": p, "qty": q, "riskPct": 0.4} for p, q in rows], "stops": [{"px": stop, "pct": 100}]}}


def wl_db(page): return page.evaluate("()=>{ const d = window.firebase.__mockDb.__dump(), o = {}; Object.keys(d).forEach(k=>{ const m = k.match(/^users\\/testuid\\/watchlist\\/(.+)$/); if(m) o[m[1]] = d[k]; }); return o; }")
def wl_ids(page): return sorted(wl_db(page).keys())
def card_db(page, cid): return page.evaluate("(id)=>window.firebase.__mockDb.__dump()['users/testuid/coreCards/'+id]", cid)
def ovf(page): return js(page, "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
def go_watch(page):
    js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 600)
def rows(page): return js(page, "()=>[...document.querySelectorAll('[data-wl1-row]')].map(e=>e.dataset.sym)")
def chip(page, sym): return js(page, "(s)=>{ const e=document.querySelector('[data-wl1-row][data-sym=\"'+s+'\"] [data-wl1-chip]'); return e ? e.innerText.trim() : null; }", sym)
def rowtxt(page, sym): return js(page, "(s)=>{ const e=document.querySelector('[data-wl1-row][data-sym=\"'+s+'\"]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sym)
def todo(page, pre): return js(page, "(p)=>ln4TodoItems(tdLast || {today:thaiToday(), weekday:true}).filter(x=>x.id.indexOf(p)===0).map(x=>x.t)", pre)
def refresh_today(page):
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)
def shot(page, name):
    settle(page, 700); page.screenshot(path=f"{SHOTS}{name}.png", animations="disabled")


def launch(pw, w, h):
    b, page, ce, pe = T.launch(pw, w, h, iso=T.NOW, picks=(), weekly=False)
    js(page, "()=>{ ln4Write(o=>{ delete o.starterFeatureOff; delete o.starterOff; o.re1StarterReset = true; }); }")   # RE-C1: Training (Starter ¼) ON for tests that exercise it
    page.route(re.compile(r"investing\.com"), lambda route: route.fulfill(status=200, content_type="text/html", body="<html><body></body></html>"))
    P24.set_ff(page, P24.ff_json(True, True))
    js(page, "()=>{ try{ ['dash.ps1Off','dash.wl1Trk','dash.wl1CandNote','dash.sw2Hint.watch','wlSubMap'].forEach(k=>localStorage.removeItem(k)); }catch(e){} }")
    return b, page, ce, pe


def fixtures_cards():
    return {
        "cAD": P24.open_card("cAD", "tAD", ticker="ADBE", acct="main", qty=10, entry=500, sl=470, px=505, pxDate="2026-10-01", plan=ps1([(500, 100)], 470)),            # Holding
        "cAM": P24.card("cAM", "main", "AMD", plan=ps1([(182.5, 200)], 170), px=180, pxDate="2026-10-01"),                                                            # Planned
        "cMS": P24.open_card("cMS", "tMS", ticker="MSFT", acct="main", qty=5, entry=400, sl=380, px=420, pxDate="2026-10-01", plan=ps1([(400, 5)], 380)),             # Holding · done
        "cNV": P24.open_card("cNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=160, px=180, pxDate="2026-10-01", track="ladder", plan=ps1([(171.4, 10)], 160)),
        "cNW": P24.card("cNW", "main", "NVDA", plan=ps1([(160, 10)], 150), px=180, pxDate="2026-10-01", track="ladder"),                                             # 2nd plan on NVDA → add-on planned
    }


def seed_main(page):
    put_wl(page, {
        "ADBE": wl_doc("ADBE", thesis=P38.th("ADBE")),                                                        # Holding · homework not started · has a thesis (tabs)
        "AMD": wl_doc("AMD", exit_="Breaks 165 on volume"),                                                    # Planned · trigger missing
        "MSFT": wl_doc("MSFT", exit_="Azure growth < 25%", trigger="Close above 430", confirmed=True),        # Holding · done
        "HANA.BK": wl_doc("HANA.BK", exch="SET"),                                                              # No plan
        "NVDA": wl_doc("NVDA", trk=True, why="AI capex cycle", exit_="Hyperscaler capex cut", confirmed=True),  # COMP · Holding · Add-on planned
        "AVGO": wl_doc("AVGO", trk=True),                                                                      # COMP · No plan
    })
    put_cards(page, fixtures_cards())
    put_trades(page, [P13.T("tAD", "core", "open", sym="ADBE", entry=500, sl=470, qty=10, cur="USD", date="2026-09-10"),
                      P13.T("tMS", "core", "open", sym="MSFT", entry=400, sl=380, qty=5, cur="USD", date="2026-09-10"),
                      P13.T("tNV", "core", "open", sym="NVDA", entry=171.4, sl=160, qty=10, cur="USD", date="2026-09-10")])
    settle(page, 400)


SW = """([x,y,dx,dy,ms,sel])=>new Promise(res=>{
  const tgt = sel ? document.querySelector(sel) : document.elementFromPoint(x,y);
  if(!tgt) return res('notarget');
  if(sel){ const r = tgt.getBoundingClientRect(); x = r.left + r.width/2; y = r.top + r.height/2; }
  const mk = (px,py)=>new Touch({identifier:1, target:tgt, clientX:px, clientY:py});
  const fire = (type, px, py)=>tgt.dispatchEvent(new TouchEvent(type, {bubbles:true, cancelable:true, touches:type==='touchend'?[]:[mk(px,py)], changedTouches:[mk(px,py)]}));
  fire('touchstart', x, y); fire('touchmove', x+dx/2, y+dy/2);
  setTimeout(()=>{ fire('touchend', x+dx, y+dy); res('ok'); }, ms);
})"""


def swipe(page, dx, dy=0, x=195, y=330, sel=None):
    r = page.evaluate(SW, [x, y, dx, dy, 120, sel]); settle(page, 350); return r


# ───────────────────────── 1 Watch list · status · split layout ─────────────────────────
def watch_list(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed_main(page); go_watch(page)
        r = rows(page)
        check(f"{tag} 1 Momentum list: ADBE (Holding, homework missing) → AMD (Planned) → HANA (No plan) → MSFT (done); no Compounder rows", r == ["ADBE", "AMD", "HANA.BK", "MSFT"], r)
        check(f"{tag} 1 status chips: Holding · Planned · No plan · Holding", [chip(page, s) for s in r] == ["Holding", "Planned", "No plan", "Holding"], [chip(page, s) for s in r])
        check(f"{tag} 1 cap tags: not done = 50% · done = 100%; homework text names what is missing", "50%" in rowtxt(page, "ADBE") and "100%" in rowtxt(page, "MSFT") and "trigger missing" in rowtxt(page, "AMD") and "homework done" in rowtxt(page, "MSFT"), [rowtxt(page, s) for s in r])
        check(f"{tag} 1 summary line: 4 stocks · 2 need homework", re.search(r"4 stocks.*2 need homework", txt(page, "[data-wl1-sum]") or "") is not None, txt(page, "[data-wl1-sum]"))
        check(f"{tag} 1 segmented control shows counts Momentum 4 | Compounder 2", "Momentum 4" in txt(page, "[data-wl1-segs]") and "Compounder 2" in txt(page, "[data-wl1-segs]"), txt(page, "[data-wl1-segs]"))
        js(page, "()=>wl1TrkSet('ladder')"); settle(page, 400)
        r2 = rows(page)
        check(f"{tag} 1 Compounder list: AVGO (No plan) before NVDA (done) · NVDA = 'Holding · Add-on planned' (2nd plan on the same key)", r2 == ["AVGO", "NVDA"] and chip(page, "NVDA") == "Holding · Add-on planned" and chip(page, "AVGO") == "No plan", [r2, chip(page, "NVDA")])
        check(f"{tag} 1 all 4 states reachable: No plan / Planned / Holding / Holding · Add-on planned", {chip(page, "NVDA"), chip(page, "AVGO")} == {"Holding · Add-on planned", "No plan"}, "")
        check(f"{tag} 1 key = exchange + symbol + strategy", js(page, "()=>wl1KeyOf(wlItemOf('NVDA'))") == "NASDAQ:NVDA|ladder" and js(page, "()=>wl1KeyOf(wlItemOf('HANA.BK'))") == "SET:HANA|winner", js(page, "()=>wl1KeyOf(wlItemOf('NVDA'))"))
        js(page, "()=>wl1TrkSet('winner')"); settle(page, 400)
        check(f"{tag} 1 the Candidates tab is gone (Ideas + Watch only)", cnt(page, "[data-wl-view='cand']") == 0 and js(page, "()=>{ wlSetView('cand'); return wlView; }") == "wl", "")
        hd = js(page, "()=>{ const c=document.querySelector('.wlList').getBoundingClientRect(); return [...document.querySelectorAll('[data-wl1-hd] *')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && (r.right>c.right-1 || r.left<c.left+1); }).map(e=>e.className||e.tagName); }")
        check(f"{tag} 1 list header (segmented · summary · ⇩/💡) stays inside the list card", hd == [], hd)
        check(f"{tag} 1 no leftover 'ตัวรอสร้าง Thesis' line / Candidate wording in the list header", "ตัวรอสร้าง" not in (txt(page, ".wlListHead") or "") and "Candidate" not in (txt(page, ".wlListHead") or ""), txt(page, ".wlListHead"))
        if w >= 1024:
            js(page, "()=>{ document.querySelector('.wlm.wl1').style.gridTemplateColumns='280px minmax(0,1fr)'; }"); settle(page, 200)
            hd = js(page, "()=>{ const c=document.querySelector('.wlList').getBoundingClientRect(); return [c.width, ...[...document.querySelectorAll('[data-wl1-hd] *')].filter(e=>{ const r=e.getBoundingClientRect(); return r.width>0 && (r.right>c.right-1 || r.left<c.left+1); }).map(e=>e.className||e.tagName)]; }")
            check(f"{tag} 1 list header fits at the 280px minimum too", len(hd) == 1 and hd[0] <= 281, hd)
            js(page, "()=>{ document.querySelector('.wlm.wl1').style.gridTemplateColumns=''; }")
        check(f"{tag} 1 no horizontal overflow", ovf(page) <= 0, ovf(page))
        rowsw = js(page, "()=>{ const l=document.querySelector('.wlm.wl1 .wlList'); return l ? Math.round(l.getBoundingClientRect().width) : null; }")
        if w >= 1024:
            check(f"{tag} 1 Mac: list column ≤ 320px (split)", rowsw is not None and 280 <= rowsw <= 320, rowsw)
            check(f"{tag} 1 Mac: 2-line rows with no buttons", js(page, "()=>{ const r=document.querySelector('[data-wl1-row]'); const a=r.querySelector('[data-wl1-act]'); return r.querySelectorAll('.l1,.l2').length===2 && getComputedStyle(a).display==='none'; }"), "")
            fs = js(page, "()=>{ const b=document.querySelector('.wlDBody'); const t=b.querySelector('.ltTab, textarea, .panel'); const q=getComputedStyle(t).fontSize; const root=document.querySelector('.wlm.wl1'); root.classList.remove('wl1'); const q2=getComputedStyle(t).fontSize; root.classList.add('wl1'); return [q,q2]; }")
            check(f"{tag} 1 Mac: panel font sizes unchanged", fs[0] == fs[1], fs)
            mw = js(page, "()=>{ const b=document.querySelector('.wlDBody'); return Math.max(...[...b.children].map(e=>Math.round(e.getBoundingClientRect().width))); }")
            check(f"{tag} 1 Mac: panel text column ≤ 760px", mw <= 762, mw)
            pw_ = js(page, "()=>{ const d=document.querySelector('.wlDet'); const l=document.querySelector('.wlList'); return Math.round(d.getBoundingClientRect().width) > Math.round(l.getBoundingClientRect().width)*2; }")
            check(f"{tag} 1 Mac: the panel takes the rest of the width", pw_, "")
        else:
            a = js(page, "()=>{ const r=document.querySelector('[data-wl1-row]'); const a=r.querySelector('[data-wl1-act]'); const b=a.getBoundingClientRect(), c=r.getBoundingClientRect(); return {disp:getComputedStyle(a).display, inside:b.right<=c.right+1&&b.left>=c.left-1, l1:r.querySelector('.l1').getBoundingClientRect().height, l2:r.querySelector('.l2').getBoundingClientRect().height}; }")
            check(f"{tag} 1 iPhone: 2-line rows, one action pill inside the row", a["disp"] != "none" and a["inside"] and a["l1"] < 48 and a["l2"] < 48, a)
            js(page, "()=>document.querySelectorAll('[data-wl1-row] > .l1, [data-wl1-row] > .l2').forEach(e=>{})")
            check(f"{tag} 1 iPhone: row action label: 'Do homework ›' / 'Open ›'", "Do homework" in rowtxt(page, "ADBE") and "Open" in rowtxt(page, "MSFT"), rowtxt(page, "MSFT"))
        # panel always opens on Summary (ignores remembered sub-tab)
        js(page, "()=>{ ltSubSave('ADBE','exit'); ltSubSave('AMD','trk'); }")
        js(page, "()=>wlOpen('ADBE')"); settle(page, 500)
        on = js(page, "()=>{ const t=document.querySelector('[data-lt-tabs] .ltTab.on'); return t ? t.dataset.ltTab : null; }")
        check(f"{tag} 1 panel ALWAYS opens on Summary (old per-ticker memory ignored)", on == "sum", on)
        check(f"{tag} 1 panel ends with the Homework block: ✗ ④ ✗ Trigger · Fill ④ › · 'I've reviewed this' disabled", js(page, "()=>{ const h=document.querySelector('[data-wl1-hw]'); return !!h && h.dataset.wl1HwState==='todo' && !!h.querySelector('[data-wl1-fill]') && h.querySelector('[data-wl1-confirm]').disabled; }"), txt(page, "[data-wl1-hw]"))
        if w >= 1024:
            shot(page, f"mac-split-{w}")
        else:
            js(page, "()=>wlBack()"); settle(page, 400); shot(page, "iphone-list-390" if w == 390 else f"iphone-list-{w}")
        check(f"{tag} 1 no overflow with the panel/sheet open", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


# ───────────────────────── 2 Tab key · ← → · swipe ─────────────────────────
def keys_swipe(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed_main(page); go_watch(page)
        trk = lambda: js(page, "()=>wl1Trk")
        if w >= 1024:
            js(page, "()=>{ document.activeElement && document.activeElement.blur(); }")
            page.keyboard.press("Tab"); settle(page, 300)
            check(f"{tag} 2 Tab → Compounder; first row selected (AVGO)", trk() == "ladder" and js(page, "()=>wlSel") == "AVGO", [trk(), js(page, "()=>wlSel")])
            page.keyboard.press("Tab"); settle(page, 300)
            check(f"{tag} 2 Tab again → Momentum", trk() == "winner", trk())
            page.keyboard.press("Shift+Tab"); settle(page, 300)
            check(f"{tag} 2 Shift+Tab is normal focus navigation (no list switch)", trk() == "winner", trk())
            js(page, "()=>wlOpen('ADBE')"); settle(page, 400)
            page.focus("[data-wl1-trigger]"); page.keyboard.press("Tab"); settle(page, 200)
            check(f"{tag} 2 Tab while typing in a field is ignored", trk() == "winner", trk())
            js(page, "()=>{ document.activeElement.blur(); wl1ImpOpen(); }"); settle(page, 300)
            page.keyboard.press("Tab"); settle(page, 200)
            check(f"{tag} 2 Tab with the Import sheet open is ignored", trk() == "winner" and cnt(page, ".wl1-sheet") == 1, trk())
            js(page, "()=>wl1ImpClose()")
            js(page, "()=>{ wlOpen('ADBE'); document.activeElement.blur(); }"); settle(page, 400)
            s0 = js(page, "()=>ltSub(wlSub) || 'sum'")
            page.keyboard.press("ArrowRight"); settle(page, 300)
            s1 = js(page, "()=>ltSub(wlSub)")
            page.keyboard.press("ArrowLeft"); settle(page, 300)
            s2 = js(page, "()=>ltSub(wlSub)")
            check(f"{tag} 2 ← / → still switch the thesis tabs (sum → view → sum)", s0 == "sum" and s1 == "view" and s2 == "sum" and trk() == "winner", [s0, s1, s2, trk()])
            js(page, "()=>wl1TrkSet('ladder')"); settle(page, 300)
            sel = js(page, "()=>wlSel")
            js(page, "()=>wl1TrkSet('winner')"); settle(page, 300)
            check(f"{tag} 2 switching list keeps nothing stale: selected stock not in the new list → first row", sel == "AVGO" and js(page, "()=>wlSel") == "ADBE", [sel, js(page, "()=>wlSel")])
            check(f"{tag} 2 choice remembered per device", js(page, "()=>localStorage.getItem('dash.wl1Trk')") == "winner", "")
        else:
            check(f"{tag} 2 iPhone: middle swipe left → Compounder (+ one-time hint)", swipe(page, -120, 5) == "ok" and trk() == "ladder" and js(page, "()=>!!localStorage.getItem('dash.sw2Hint.watch')"), trk())
            swipe(page, -120, 5)
            check(f"{tag} 2 iPhone: swipe left again stays (no wrap)", trk() == "ladder", trk())
            swipe(page, 120, -5)
            check(f"{tag} 2 iPhone: middle swipe right → Momentum", trk() == "winner", trk())
            check(f"{tag} 2 iPhone: choice remembered", js(page, "()=>localStorage.getItem('dash.wl1Trk')") == "winner", "")
            swipe(page, -120, 5, sel="#tabsMain")
            check(f"{tag} 2 iPhone: bottom-bar swipe unchanged (list stays; main tab changes only there)", trk() == "winner", [trk(), js(page, "()=>activeTab")])
            go_watch(page)
            js(page, "()=>wl1ImpOpen()"); settle(page, 300)
            swipe(page, -120, 5, y=120)
            check(f"{tag} 2 iPhone: swipe ignored with the Import sheet open", trk() == "winner", trk())
            js(page, "()=>wl1ImpClose()")
            js(page, "()=>wlOpen('ADBE')"); settle(page, 500)
            swipe(page, -120, 5, y=300)
            check(f"{tag} 2 iPhone: swipe ignored inside the full-screen sheet", trk() == "winner", trk())
    finally:
        b.close()


# ───────────────────────── 3 Import from TradingView ─────────────────────────
def imports(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        put_wl(page, {"NVDA": wl_doc("NVDA", trk=True, why="keep", exit_="me", trigger="t", confirmed=True), "HANA.BK": wl_doc("HANA.BK", exch="SET", exit_="Sentinel text")})
        go_watch(page)
        check(f"{tag} 3 Import button present; no TV1 export/download UI", cnt(page, "[data-wl1-import]") == 1 and cnt(page, "[data-tv1-btn], [data-tv1-dl], [data-tv1-bar]") == 0 and js(page, "()=>typeof tv1Build === 'undefined' && typeof tv1Download === 'undefined'"), "")
        page.locator("[data-wl1-import]").click(); settle(page, 400)
        check(f"{tag} 3 popup (Mac) / bottom sheet (iPhone) opens with strategy switch + paste box + upload", cnt(page, ".wl1-sheet [data-wl1-imp-seg]") == 2 and cnt(page, "[data-wl1-imp-text]") == 1 and cnt(page, "[data-wl1-imp-file]") == 1, "")
        sheet = js(page, "()=>{ const s=document.querySelector('.wl1-sheet .ui-sheet').getBoundingClientRect(); return {bottom:Math.round(innerHeight - s.bottom), w:Math.round(s.width), cx:Math.round(s.left + s.width/2)}; }")
        check(f"{tag} 3 layout: {'bottom sheet' if w < 600 else 'centred popup'}", (sheet["bottom"] <= 2) if w < 600 else (abs(sheet["cx"] - w / 2) < 4 and sheet["bottom"] > 8), sheet)
        ta = page.locator("[data-wl1-imp-text]")
        ta.fill("###WATCHLIST,SET:HANA,NASDAQ:NVDA,SPY/QQQ,###CANDIDATE,SET:BAFS,SET:EPG"); settle(page, 300)
        k = js(page, "()=>[document.querySelector('[data-wl1-n-new]').innerText, document.querySelector('[data-wl1-n-in]').innerText, document.querySelector('[data-wl1-n-skip]').innerText]")
        lst = txt(page, "[data-wl1-imp-list]") or ""
        check(f"{tag} 3 spec example: only the WATCHLIST section is read (HANA existing, NVDA existing, formula skipped, CANDIDATE ignored)", k == ["0", "2", "1"] and "BAFS" not in lst and "EPG" not in lst and "SPY/QQQ" in lst and "formula" in lst, [k, lst])
        ta.fill("###WATCHLIST,NASDAQ:NVDA"); settle(page, 300)
        check(f"{tag} 3 symbol already in the OTHER strategy (NVDA is Compounder, importing as Momentum) → 'already in Watch (Compounder)', not added", "already in Watch (Compounder)" in (txt(page, "[data-wl1-imp-list]") or "") and js(page, "()=>document.getElementById('wl1ImpAdd').disabled") and js(page, "()=>document.querySelector('[data-wl1-n-new]').innerText") == "0", txt(page, "[data-wl1-imp-list]"))
        ta.fill("###WATCHLIST,SET:HANA,NASDAQ:NVDA,SPY/QQQ,###CANDIDATE,SET:BAFS,SET:EPG"); settle(page, 300)
        check(f"{tag} 3 preview shows 3 equal tiles + 'Add' disabled when nothing is new", js(page, "()=>document.querySelectorAll('[data-wl1-imp-counts] > div').length") == 3 and js(page, "()=>document.getElementById('wl1ImpAdd').disabled"), "")
        r = js(page, "()=>wl1ParseTv('###WATCHLIST,SET:HANA,###CANDIDATE,SET:BAFS,SET:EPG', 'winner').items.map(x=>x.tok)")
        check(f"{tag} 3 '###WATCHLIST,SET:HANA,###CANDIDATE,SET:BAFS,SET:EPG' → only SET:HANA", r == ["SET:HANA"], r)
        r = js(page, "()=>wl1ParseTv('###watchlist,set:hana,nasdaq:nvda', 'winner').items.map(x=>x.tok)")
        check(f"{tag} 3 case-insensitive: ###watchlist + lower-case symbols", r == ["SET:HANA", "NASDAQ:NVDA"], r)
        r = js(page, "()=>wl1ParseTv('SET:AAA,NASDAQ:BBB,###WATCHLIST,SET:CCC', 'winner').items.map(x=>x.tok)")
        check(f"{tag} 3 tokens before the first section are ignored", r == ["SET:CCC"], r)
        r = js(page, "()=>wl1ParseTv('SET:AAA\\nNASDAQ:BBB,###CANDIDATE,SET:CCC', 'winner')")
        check(f"{tag} 3 no WATCHLIST section → found=false, nothing parsed (never falls back to the whole file)", r["found"] is False and r["items"] == [], r)
        r = js(page, "()=>wl1ParseTv('###WATCHLIST,SPY/QQQ,AAPL,NASDAQ:AAPL*2,BINANCE:BTCUSD,SET:ABC!,NYSE:BRK.B', 'winner')")
        check(f"{tag} 3 formulas / bare symbols / unsupported exchange / bad symbol → skipped with a reason; NYSE:BRK.B accepted", [x["tok"] for x in r["items"]] == ["NYSE:BRK.B"] and len(r["skipped"]) == 5 and all(x["reason"] for x in r["skipped"]), r)
        ta.fill("###WATCHLIST,SET:AAA,NASDAQ:BBB,SET:HANA,SPY/QQQ,###CANDIDATE,SET:ZZZ"); settle(page, 300)
        k = js(page, "()=>[document.querySelector('[data-wl1-n-new]').innerText, document.querySelector('[data-wl1-n-in]').innerText, document.querySelector('[data-wl1-n-skip]').innerText]")
        check(f"{tag} 3 preview counts new / already in / skipped = 2 / 1 / 1; button 'Add 2 to Momentum'", k == ["2", "1", "1"] and txt(page, "#wl1ImpAdd") == "Add 2 to Momentum", [k, txt(page, "#wl1ImpAdd")])
        page.locator("[data-wl1-imp-seg='ladder']").click(); settle(page, 200)
        check(f"{tag} 3 strategy switch → 'Add 2 to Compounder'", txt(page, "#wl1ImpAdd") == "Add 2 to Compounder", txt(page, "#wl1ImpAdd"))
        before = wl_db(page)
        page.locator("#wl1ImpAdd").click(); settle(page, 800)
        ids_ = wl_ids(page); db = wl_db(page)
        check(f"{tag} 3 apply: AAA.BK + BBB added as Compounder with exchange; existing HANA/NVDA untouched; no plan/order created", ids_ == sorted(["AAA.BK", "BBB", "HANA.BK", "NVDA"]) and db["AAA.BK"].get("ladder_watch") is True and db["AAA.BK"].get("exch") == "SET" and db["BBB"].get("exch") == "NASDAQ" and db["HANA.BK"] == before["HANA.BK"] and db["NVDA"] == before["NVDA"], [ids_, db.get("AAA.BK")])
        check(f"{tag} 3 no plan / card / size created by Import", js(page, "()=>coreCardsList.length") == 0, js(page, "()=>coreCardsList.length"))
        page.locator("[data-wl1-import]").click(); settle(page, 300)
        page.locator("[data-wl1-imp-text]").fill("###WATCHLIST,NASDAQ:NVDA"); settle(page, 300)
        page.locator("#wl1ImpAdd").evaluate("e=>e.disabled") ; page.locator("[data-wl1-imp-cancel]").click(); settle(page, 300)
        check(f"{tag} 3 re-import of a file without an item never removes it", sorted(wl_ids(page)) == ids_, wl_ids(page))
        page.locator("[data-wl1-import]").click(); settle(page, 300)
        page.locator("[data-wl1-imp-text]").fill("SET:AAA,NASDAQ:BBB"); settle(page, 300)
        check(f"{tag} 3 file without ###WATCHLIST → message 'No WATCHLIST section found', 0 added", "No WATCHLIST section found" in (txt(page, "[data-wl1-imp-err]") or "") and js(page, "()=>document.getElementById('wl1ImpAdd').disabled"), txt(page, "[data-wl1-imp-err]"))
        import tempfile, os
        fn = os.path.join(tempfile.mkdtemp(), "wl.txt"); open(fn, "w").write("###WATCHLIST,SET:UPL,NASDAQ:UPQ\n###CANDIDATE,SET:NOPE")
        page.locator("[data-wl1-imp-file]").set_input_files(fn); settle(page, 500)
        check(f"{tag} 3 .txt upload fills the box and previews (2 new)", js(page, "()=>document.querySelector('[data-wl1-n-new]').innerText") == "2" and "UPL" in js(page, "()=>document.getElementById('wl1ImpText').value"), txt(page, "[data-wl1-imp-list]"))
        if w == 390:
            js(page, "()=>wl1ImpClose()"); page.locator("[data-wl1-import]").click(); settle(page, 300)
            page.locator("[data-wl1-imp-text]").fill("###WATCHLIST,SET:HANA,NASDAQ:NVDA,SPY/QQQ,###CANDIDATE,SET:BAFS"); settle(page, 300)
            shot(page, "iphone-import-390")
        elif w >= 1024:
            shot(page, f"mac-import-{w}")
        check(f"{tag} 3 no overflow with the Import sheet", ovf(page) <= 0, ovf(page))
        js(page, "()=>wl1ImpClose()")
    finally:
        b.close()


# ───────────────────────── 4 entry workflow: first fill · homework · caps · Today ─────────────────────────
def workflow(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ window.confirm = ()=>true; }")
        put_wl(page, {"MSFT": wl_doc("MSFT", exit_="e", trigger="t", confirmed=True)})
        put_cards(page, {
            "cFF": P24.card("cFF", "main", "FFIL", plan=ps1([(100, 40)], 90), px=100, pxDate="2026-10-01"),
            "cCN": P24.card("cCN", "main", "CNCL", plan=ps1([(50, 20)], 45), px=50, pxDate="2026-10-01"),
        })
        check(f"{tag} 4 no Watch item yet for FFIL / CNCL", "FFIL" not in wl_ids(page) and "CNCL" not in wl_ids(page), wl_ids(page))
        # cancelled order with no fill → nothing
        js(page, "()=>ln4Place('core','cCN')"); settle(page, 400)
        js(page, "()=>bdCancelOrder('cCN')"); settle(page, 400)
        check(f"{tag} 4 placed then cancelled (never filled) → no auto-add to Watch / no Today task", "CNCL" not in wl_ids(page) and not [t for t in todo(page, "wl1hw:") if "CNCL" in t], wl_ids(page))
        # first partial fill
        js(page, "()=>ln4Place('core','cFF')"); settle(page, 400)
        js(page, "()=>coreBuy1Open('cFF')"); settle(page, 400)
        info = js(page, "()=>({qty:document.getElementById('cbQty').value, err:document.getElementById('cbErr').innerText, dis:document.getElementById('cbSave').disabled})")
        check(f"{tag} 4 Filled ✓ form: default qty clamped to the homework cap (40 → 20) and Save enabled", info["qty"] == "20" and info["dis"] is False, info)
        page.fill("#cbQty", "10"); page.dispatch_event("#cbQty", "input"); page.click("#cbSave"); settle(page, 900)
        check(f"{tag} 4 first (partial) fill → Watch item added once (Momentum, no duplicate)", wl_ids(page).count("FFIL") == 1 and js(page, "()=>wlTrackOf('FFIL')") == "winner", wl_ids(page))
        check(f"{tag} 4 …and Port has the position once", js(page, "()=>getBook('main').trades.filter(t=>t.sym==='FFIL').length") == 1, "")
        refresh_today(page)
        t1 = todo(page, "wl1hw:")
        check(f"{tag} 4 ONE Today task: '📚 FFIL · Holding · homework not done · cap 50%'", len([t for t in t1 if "FFIL" in t]) == 1 and any("homework not done · cap 50%" in t for t in t1), t1)
        if w == 390: shot(page, "iphone-today-homework-390")
        # second fill (written like the add-on save) → no duplicate item, no second task
        js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='cFF'); const B=getBook('main'), t=B.trades.find(x=>x.id===c.trade_id); t.qty+=5; saveBook('main'); coreWrite('cFF',{lots:c.lots.concat([{n:2,date:'2026-10-01',px:99,qty:5,f:1,stop:90}])}); }"); settle(page, 900)
        refresh_today(page)
        check(f"{tag} 4 second fill → still ONE Watch item and ONE Today task", wl_ids(page).count("FFIL") == 1 and len([t for t in todo(page, "wl1hw:") if "FFIL" in t]) == 1, [wl_ids(page), todo(page, "wl1hw:")])
        go_watch(page)
        check(f"{tag} 4 Watch row = Holding · 50%", chip(page, "FFIL") == "Holding" and "50%" in rowtxt(page, "FFIL"), rowtxt(page, "FFIL"))
        # homework: fields + confirm
        js(page, "()=>wlOpen('FFIL')"); settle(page, 500)
        check(f"{tag} 4 homework needs fields AND confirm: confirm disabled while ④ / trigger empty", js(page, "()=>document.querySelector('[data-wl1-confirm]').disabled"), "")
        page.evaluate("()=>wlCol().doc('FFIL').update({my_thesis:{why:'',exit:'Loses 90',updated_at:new Date().toISOString()}, hw:{trigger:'Close > 101'}})"); settle(page, 700)
        js(page, "()=>wlOpen('FFIL')"); settle(page, 400)
        check(f"{tag} 4 text alone is not 'done': fields filled but not reviewed → still 50% / task stays", js(page, "()=>wl1HwDone(wlItemOf('FFIL'))") is False and js(page, "()=>!document.querySelector('[data-wl1-confirm]').disabled") and js(page, "()=>wl1CapPct(wlItemOf('FFIL'))") == 50, "")
        page.locator("[data-wl1-confirm]").click(); settle(page, 900)
        db = wl_db(page)["FFIL"]
        check(f"{tag} 4 'I've reviewed this' stores time → done, cap 100%", js(page, "()=>wl1HwDone(wlItemOf('FFIL'))") is True and db["hw"].get("confirmedAt") and db["hw"].get("doneAt") and js(page, "()=>wl1CapPct(wlItemOf('FFIL'))") == 100, db.get("hw"))
        refresh_today(page)
        check(f"{tag} 4 Today homework task closes by itself", not [t for t in todo(page, "wl1hw:") if "FFIL" in t], todo(page, "wl1hw:"))
        page.evaluate("()=>wlCol().doc('FFIL').update({my_thesis:{why:'',exit:'Changed text',updated_at:new Date().toISOString()}})"); settle(page, 700)
        check(f"{tag} 4 editing ④ later keeps 'done' (no re-confirm)", js(page, "()=>wl1HwDone(wlItemOf('FFIL'))") is True, "")
        page.evaluate("()=>wlCol().doc('FFIL').update({my_thesis:{why:'',exit:'',updated_at:new Date().toISOString()}})"); settle(page, 700)
        check(f"{tag} 4 …unless a required field becomes empty → not done again", js(page, "()=>wl1HwDone(wlItemOf('FFIL'))") is False, "")
        # sold out → closed, Watch row stays as No plan
        js(page, "()=>{ const c=coreCardsList.find(x=>x.id==='cFF'); const B=getBook('main'), t=B.trades.find(x=>x.id===c.trade_id); t.status='closed'; t.exit=105; t.exitDate='2026-10-01'; saveBook('main'); coreWrite('cFF',{status:'closed'}); }"); settle(page, 900)
        go_watch(page)
        check(f"{tag} 4 sold out → position closed, Watch row stays and shows 'No plan'", "FFIL" in wl_ids(page) and chip(page, "FFIL") == "No plan", [wl_ids(page), chip(page, "FFIL")])
    finally:
        b.close()


def caps(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ window.confirm = ()=>true; }")
        put_wl(page, {"CAPX": wl_doc("CAPX"), "DONE": wl_doc("DONE", exit_="e", trigger="t", confirmed=True)})
        put_cards(page, {
            "pA": P24.card("pA", "main", "CAPX", plan=ps1([(100, 40), (98, 60)], 90), px=100, pxDate="2026-10-01"),     # full 100
            "pB": P24.card("pB", "main", "CAPX", plan=ps1([(97, 40)], 90), px=97, pxDate="2026-10-01"),
            "dA": P24.card("dA", "main", "DONE", plan=ps1([(100, 40), (98, 60)], 90), px=100, pxDate="2026-10-01"),
            "dB": P24.card("dB", "main", "DONE", plan=ps1([(97, 40)], 90), px=97, pxDate="2026-10-01"),
            "dC": P24.card("dC", "main", "DONE", plan=ps1([(96, 40)], 90), px=96, pxDate="2026-10-01"),
        })
        a = js(page, "()=>wl1Agg('CAPX','winner')")
        check(f"{tag} 5 homework not done → cap = 50% of full (full 100 → cap 50)", a["full"] == 100 and a["cap"] == 50 and a["pct"] == 50, a)
        js(page, "()=>ln4Place('core','pA')"); settle(page, 300)
        check(f"{tag} 5 plan A: first level 40 ≤ cap → order placed", js(page, "()=>!!(coreCardsList.find(x=>x.id==='pA').ln4||{}).placedAt"), "")
        js(page, "()=>{ window.__wl1Msg=''; ln4Place('core','pB'); }"); settle(page, 300)
        msg = js(page, "()=>window.__wl1Msg")
        check(f"{tag} 5 plan B (same stock) would make working 80 > 50 → BLOCKED across plans, reason shows allowed qty 10", not js(page, "()=>!!(coreCardsList.find(x=>x.id==='pB').ln4||{}).placedAt") and "homework not done" in msg and "allowed 10" in msg, msg)
        # fill form for plan A: hard error when above the cap, with allowed qty
        js(page, "()=>coreBuy1Open('pA')"); settle(page, 400)
        page.fill("#cbQty", "80"); page.dispatch_event("#cbQty", "input"); settle(page, 200)
        e = js(page, "()=>({err:document.getElementById('cbErr').innerText, dis:document.getElementById('cbSave').disabled})")
        check(f"{tag} 5 Filled ✓ above the cap → Save disabled with the reason + allowed qty (50)", e["dis"] is True and "allowed 50" in e["err"], e)
        js(page, "()=>coreSheetClose()")
        # done → ≤ 100% incl. held
        a = js(page, "()=>wl1Agg('DONE','winner')")
        check(f"{tag} 5 homework done → cap = 100% of full", a["done"] is True and a["cap"] == 100, a)
        js(page, "()=>{ ln4Place('core','dA'); ln4Place('core','dB'); }"); settle(page, 300)
        placed = js(page, "()=>['dA','dB'].map(i=>!!(coreCardsList.find(x=>x.id===i).ln4||{}).placedAt)")
        js(page, "()=>{ window.__wl1Msg=''; ln4Place('core','dC'); }"); settle(page, 300)
        m2 = js(page, "()=>window.__wl1Msg")
        check(f"{tag} 5 done: A (40) + B (40) fit, third plan (+40 = 120 > 100) blocked ('total would exceed full size')", placed == [True, True] and not js(page, "()=>!!(coreCardsList.find(x=>x.id==='dC').ln4||{}).placedAt") and "exceed full size" in m2, [placed, m2])
        # held counts: 'total ≤ 100% incl. held'
        c = js(page, """()=>{
          const mk = (held, work, full, done)=>{ const a = {full, held, working:work, done, lot:1}; a.cap = done ? full : Math.floor(full*0.5); return a; };
          const chk = (a, add)=>{ const allowed = Math.max(0, a.cap - a.held - a.working); return {ok: a.held + a.working + add <= a.cap, allowed}; };
          return {
            starterFirst: chk(mk(0,0,100,false), 25),
            addonNotDone: chk(mk(25,0,100,false), 50),
            addonDone: chk(mk(25,0,100,true), 50),
            doneHeld: chk(mk(60,0,100,true), 50),
            capOnlyOff: chk(mk(0,0,100,false), 50) };
        }""")
        check(f"{tag} 5 Starter ¼ ON: first entry ¼ (25) ok · add-on stops at 50 total when homework not done (allowed 25)", c["starterFirst"]["ok"] and (not c["addonNotDone"]["ok"]) and c["addonNotDone"]["allowed"] == 25, c)
        check(f"{tag} 5 homework done: add-on to 75 total ok; held 60 + 50 > 100 blocked (allowed 40)", c["addonDone"]["ok"] and (not c["doneHeld"]["ok"]) and c["doneHeld"]["allowed"] == 40, c)
        check(f"{tag} 5 Starter OFF: only the homework cap applies (50 = ok)", c["capOnlyOff"]["ok"], c)
        # real starter plan through the model: held 25 (starter filled) + add-on request
        put_cards(page, {"sS": P24.open_card("sS", "tSS", ticker="STAR", acct="main", qty=25, entry=100, sl=90, px=101, pxDate="2026-10-01",
                                              plan=dict(ps1([(100, 25)], 90), starter=True, addon={"riskPct": 0.3, "frac": 0.25, "cond": "stop>=be"}))})
        put_trades(page, [P13.T("tSS", "core", "open", sym="STAR", entry=100, sl=90, qty=25, cur="USD", date="2026-09-10")])
        put_wl(page, {"STAR": wl_doc("STAR")})
        r = js(page, "()=>{ const a = wl1Check('STAR','winner', 50, {extraFull: wl1FullQty(coreCardsList.find(x=>x.id==='sS'))}); return {full:a.full, cap:a.cap, held:a.held, ok:a.ok, allowed:a.allowed}; }")
        check(f"{tag} 5 real Starter ¼ plan: full = 100 (25 ÷ ¼), add-on of 50 on top of 25 held is blocked until homework is done (allowed 25)", r["full"] == 100 and r["cap"] == 50 and r["held"] == 25 and r["ok"] is False and r["allowed"] == 25, r)
        # plan form cap box
        P120.ps_on(page)
        js(page, "()=>{ switchTab('plan'); coreNewOpen(null, {ticker:'AMD'}); }"); settle(page, 500)
        P120.fill(page, 100, 95); settle(page, 400)
        box = js(page, "()=>{ const e=document.querySelector('[data-wl1-cap]'); return e ? {t:e.innerText.replace(/\\s+/g,' '), bar:!!e.querySelector('.bar u'), go:!!e.querySelector('[data-wl1-capgo]')} : null; }")
        check(f"{tag} 5 plan form cap box: headline · numbers line · bar with cap mark · Do homework ›", box is not None and "Homework not done" in box["t"] and "max 50%" in box["t"] and "full" in box["t"] and "cap" in box["t"] and "filled 0 + working 0" in box["t"] and box["bar"] and box["go"], box)
        if w == 390:
            shot(page, "iphone-capbox-390")
        check(f"{tag} 5 no overflow with the cap box", ovf(page) <= 0, ovf(page))
        js(page, "()=>coreSheetClose()")
    finally:
        b.close()


def today_addon(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        put_wl(page, {"NVDA": wl_doc("NVDA", exit_="e", trigger="t", confirmed=True)})
        put_cards(page, {"ccST": P24.open_card("ccST", "tST", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=171.4, px=180, pxDate="2026-10-01",
                                               plan={"entry": 171.4, "stop": 160, "starter": True, "addon": {"riskPct": 0.2, "frac": 0.25, "cond": "stop>=be"}},
                                               lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 171.4}])})
        put_trades(page, [P13.T("tST", "core", "open", sym="NVDA", entry=171.4, sl=171.4, qty=10, cur="USD", date="2026-09-10")])
        refresh_today(page); refresh_today(page)
        t = todo(page, "wl1ao:")
        check(f"{tag} 6 add-on condition met → ONE Today reminder '🛡️ NVDA add-on condition met · Review add-on ›' (no auto order)", len(t) == 1 and "add-on condition met" in t[0] and js(page, "()=>(coreCardsList.find(x=>x.id==='ccST').ln4||{}).placedAt") is None, t)
        check(f"{tag} 6 holding with homework done → no homework task", not todo(page, "wl1hw:"), todo(page, "wl1hw:"))
        if w == 390:
            shot(page, "iphone-today-390")
    finally:
        b.close()


# ───────────────────────── 7 Candidates removed · export notice · data kept ─────────────────────────
def candidates(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, {CANDA:{manual:true, sym:'CANDA', track:'winner', at:'2026-09-20'}, CANDB:{manual:true, sym:'CANDB', track:'ladder', at:'2026-09-21'}, CANDP:{manual:true, sym:'CANDP', track:'winner', at:'2026-09-22'}}); })"); settle(page, 500)
        put_wl(page, {"MSFT": wl_doc("MSFT")})
        put_cards(page, {"cP": P24.card("cP", "main", "CANDP", plan=ps1([(10, 100)], 9), px=10, pxDate="2026-10-01")})
        settle(page, 800)
        go_watch(page)
        check(f"{tag} 7 Candidate with a plan moved into Watch automatically (no duplicate); others stay out", wl_ids(page).count("CANDP") == 1 and "CANDA" not in wl_ids(page), wl_ids(page))
        check(f"{tag} 7 no Candidates tab / list / entry points (V key, pills, Today Find card)", cnt(page, "[data-wl-view='cand']") == 0 and cnt(page, "[data-ln4-find]") == 0 or js(page, "()=>{ switchTab('today'); todayRefresh(true); return document.querySelectorAll('[data-ln4-find]').length; }") == 0, "")
        go_watch(page)
        check(f"{tag} 7 one-time notice: 'Candidates moved to TradingView · Export 2 as .txt ›'", "Candidates moved to TradingView" in (txt(page, "[data-wl1-note]") or "") and "Export 2 as .txt" in (txt(page, "[data-wl1-note]") or ""), txt(page, "[data-wl1-note]"))
        page.locator("[data-wl1-export]").click(); settle(page, 400)
        ex = js(page, "()=>window.__wl1Exported")
        check(f"{tag} 7 export = ###CANDIDATE,… per strategy (Momentum / Compounder)", ex["winner"].startswith("###CANDIDATE,") and "CANDA" in ex["winner"] and "CANDB" in ex["ladder"] and "CANDB" not in ex["winner"] and "CANDP" not in ex["winner"], ex)
        check(f"{tag} 7 candidate docs are still in storage (nothing deleted)", js(page, "()=>Object.keys(tdSettings().candMeta||{}).sort().join(',')") == "CANDA,CANDB,CANDP", js(page, "()=>Object.keys(tdSettings().candMeta||{})"))
        page.locator("[data-wl1-note-x]").click(); settle(page, 300)
        check(f"{tag} 7 notice is dismissible and stays dismissed", cnt(page, "[data-wl1-note]") == 0 and js(page, "()=>{ renderWatchlist(); return document.querySelectorAll('[data-wl1-note]').length; }") == 0, "")
        check(f"{tag} 7 TV1 export retired: no HOLD/READY/SCREEN builder, no Download menu", js(page, "()=>[typeof tv1Build, typeof tv1Download, typeof tv1Changes, typeof tv1BarHtml].join()") == "undefined,undefined,undefined,undefined" and cnt(page, "[data-tv1-btn]") == 0, "")
        check(f"{tag} 7 Import kept (header ⇩)", cnt(page, "[data-wl1-import]") == 1, "")
        check(f"{tag} 7 no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


def watch360(pw):
    tag = f"[{ENGINE}/360]"
    b, page, ce, pe = launch(pw, 360, 780)
    try:
        seed_main(page); go_watch(page)
        check(f"{tag} 1 iPhone 360: list has no horizontal overflow", ovf(page) <= 0, ovf(page))
        bad = js(page, "()=>[...document.querySelectorAll('[data-wl1-row]')].filter(r=>r.scrollWidth > r.clientWidth + 1).map(r=>r.dataset.sym)")
        check(f"{tag} 1 rows fit (no clipped content)", bad == [], bad)
        js(page, "()=>wlOpen('MSFT')"); settle(page, 500)
        check(f"{tag} 1 sheet at 360: no overflow", ovf(page) <= 0, ovf(page))
        js(page, "()=>{ wlBack(); wl1ImpOpen(); }"); settle(page, 400)
        check(f"{tag} 3 Import sheet at 360: no overflow", ovf(page) <= 0, ovf(page))
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        import os; sel = [int(a) for a in os.environ.get('WL1W', '').split(',') if a]
        for w, h in [x for x in ((1440, 900), (1280, 860), (390, 844)) if not sel or x[0] in sel]:
            for fn in (watch_list, keys_swipe, imports, workflow, caps, today_addon, candidates):
                try: fn(pw, w, h)
                except Exception as e:
                    import traceback; traceback.print_exc(); check(f"[{w}] {fn.__name__} crashed", False, str(e)[:300])
        try: watch360(pw) if (not sel or 360 in sel) else None
        except Exception as e:
            import traceback; traceback.print_exc(); check("[360] crashed", False, str(e)[:300])
    nf = [r for r in results if not r[1]]
    print(f"\nSUMMARY: {len(results) - len(nf)} pass / {len(nf)} fail")
    sys.exit(1 if nf else 0)
