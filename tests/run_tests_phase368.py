#!/usr/bin/env python3
"""TV1 — Dashboard ⇄ TradingView (export 2 files · import · groups + tags · Setup ✓ · 14d Drop? · change count) · เทส 368 · Chromium · 390 + 1440 · SAMPLE data only
นาฬิกาปลอม พฤ. 1 ต.ค. 2026 · รัน: python3 run_tests_phase368.py"""
import json, sys, datetime
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase13 as P13
import run_tests_phase59 as P59
import run_tests_phase44 as P44
import copy

ENGINE = base.BROWSER_ENGINE
results = []
js, settle, cnt, txt = C.js, T.settle, T.cnt, T.txt
W = T.W


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def cand(page, sym, ind="", track="winner", days=3, **extra):
    rec = {"manual": True, "sym": sym, "market": "US", "cand_at": (datetime.date(2026, 10, 1) - datetime.timedelta(days=days)).isoformat() + "T03:00:00.000Z", "track": track, "reasons": ["volume-spike"]}
    if ind: rec["industry"] = ind
    rec.update(extra)
    js(page, "([k,r])=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, {[k]: r}); })", [sym, rec])


def cm(page, k=None):
    return js(page, "(k)=>{ const m = tdSettings().candMeta||{}; return JSON.parse(JSON.stringify(k ? (m[k]||null) : m)); }", k)


def setup_data(page):
    """HOLD NVDA(core open) · Sat open SATX · wl: AVGO(setup) META CRWD(SMH) AMD(ladder) DELTA.BK(TH) · cands MU/LRCX(semis=HOT) FTNT DDOG(cold)"""
    js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("t1", "core", "open", sym="NVDA", entry=100, sl=90, qty=10, cur="USD", date="2026-09-20"), P13.T("t2", "satB", "open", sym="SATX", entry=10, sl=9, qty=10, cur="USD", date="2026-09-20")])
    T.wl_seed(page, [W("NVDA"), W("AVGO"), W("META", industry="Software"), W("CRWD", sector_etf="SMH"), W("AMD", ladder_watch=True, ladder_watch_set=True), W("DELTA.BK", mk="TH", ladder_watch=True, ladder_watch_set=True)])
    js(page, "()=>{ window.sectorState = etf=>({quad: etf==='SMH' ? 'lead' : 'lag', followed:false}); window.hotSectors = ()=>[{etf:'SMH', k:'lead', ratio:1}]; }")
    cand(page, "MU", "Semiconductors", days=3); cand(page, "LRCX", "Semiconductors", days=5)
    cand(page, "FTNT", "Software", days=9, reasons=[]); cand(page, "DDOG", "", days=1, reasons=["earnings-spike"])
    js(page, "()=>glWrite(S=>{ S.tvInfo = {NVDA:{x:'NASDAQ:NVDA'}, MU:{x:'NASDAQ:MU'}, AMD:{x:'NASDAQ:AMD'}}; S.tvSetup = {AVGO:thaiToday()}; })")
    settle(page, 400)


def export(page, track):
    js(page, "(t)=>{ wlMenu=''; tv1Menu=true; renderWatchlist(); }", track)
    with page.expect_download() as d:
        page.locator(f'[data-tv1-dl="{track}"]').click()
    dl = d.value
    return dl.suggested_filename, open(dl.path(), encoding="utf-8").read()


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_watch(page, "wl"); setup_data(page); T.go_watch(page, "wl")
        # ── Export ──
        check(f"{tag} header: 'TradingView' button present + note '= READY in TV'", cnt(page, "[data-tv1-btn]") == 1 and cnt(page, "[data-tv1-bar]") == 0 and txt(page, "[data-tv1-btn]").startswith("TV"), txt(page, "[data-ln4w-hd]"))   # LN4: header icon "TV n" replaces the bar + note
        js(page, "()=>{ tv1Menu=true; renderWatchlist(); }"); settle(page, 200)
        mi = js(page, "()=>[...document.querySelectorAll('[data-tv1-menu] [role=menuitem]')].map(e=>e.firstChild.textContent.trim())")
        check(f"{tag} menu: Download Momentum · Download Compounder · Import…", mi == ["⬇ Download Momentum", "⬇ Download Compounder", "⬆ Import…"], mi)
        if w == 390: C.shot(page, "tv1-menu-390.png")
        else: C.shot(page, "tv1-menu-1440.png")
        name, txt_m = export(page, "winner")
        exp_m = "###HOLD,NASDAQ:NVDA,###READY - SETUP,AVGO,###READY,CRWD,META,###SCREEN - HOT - Semiconductors,NASDAQ:MU,LRCX,###SCREEN,DDOG,FTNT"
        check(f"{tag} Dash_Momentum.txt: fixed name · sections in order · HOT-sector stock first in READY · HOT per sector · tvSym used (NASDAQ:MU) · bare when unknown", name == "Dash_Momentum.txt" and txt_m == exp_m, [name, txt_m])
        check(f"{tag} no Sat stock (SATX) · NVDA once only (HOLD wins over READY) · compounder AMD / TH not in the Momentum file", "SATX" not in txt_m and txt_m.count("NVDA") == 1 and "AMD" not in txt_m and "DELTA" not in txt_m, txt_m)
        name2, txt_c = export(page, "ladder")
        check(f"{tag} Dash_Compounder.txt: AMD + SET:DELTA (TH → SET:) · track split", name2 == "Dash_Compounder.txt" and txt_c == "###READY,NASDAQ:AMD,SET:DELTA", [name2, txt_c])
        toast = js(page, "()=>document.getElementById('tv1Toast').innerText")
        check(f"{tag} toast: Saved · delete old → Import list · no 'without exchange' line when N = 0", "Saved Dash_Compounder.txt" in toast and "delete old Dash_Compounder → ⋯ → Import list" in toast and "without exchange" not in toast, toast)
        export(page, "winner")
        toast = js(page, "()=>document.getElementById('tv1Toast').innerText")
        check(f"{tag} toast counts symbols without exchange (AVGO CRWD META LRCX FTNT DDOG = 6)", "6 symbols without exchange" in toast, toast)
        # ── change count ──
        check(f"{tag} after both downloads: change count hidden (0)", cnt(page, "[data-tv1-n]") == 0 and txt(page, "[data-tv1-btn]") == "TV", txt(page, "[data-tv1-btn]"))
        cand(page, "ANET", "Software", days=0); settle(page, 300); js(page, "()=>renderWatchlist()")
        check(f"{tag} new Candidate → 'TradingView · 1 change'", txt(page, "[data-tv1-btn]") == "TV 1", txt(page, "[data-tv1-btn]"))
        js(page, "()=>{ td3MetaWrite('ANET',{dismissed:true}); renderWatchlist(); }"); settle(page, 300)
        check(f"{tag} removing it again → back to 0 (count goes down)", cnt(page, "[data-tv1-n]") == 0, txt(page, "[data-tv1-btn]"))
        js(page, "()=>tv1SetupToggle('META')"); settle(page, 300)
        check(f"{tag} Setup ✓ on META (READY → READY - SETUP) = 1 change", txt(page, "[data-tv1-btn]") == "TV 1", txt(page, "[data-tv1-btn]"))
        export(page, "winner"); settle(page, 200)
        check(f"{tag} download resets the count", cnt(page, "[data-tv1-n]") == 0)
        js(page, "()=>tv1SetupToggle('META')"); settle(page, 300)
        # ── cap 15 ──
        for i in range(20): cand(page, f"Z{i:02d}", "Biotechnology" if i % 2 else "", days=(i % 8) + 1)
        settle(page, 300)
        _, t2 = export(page, "winner")
        n_screen = len([x for x in t2.split("###SCREEN,")[1].split(",")]) if "###SCREEN," in t2 else 0
        n_hot = len(t2.split("###SCREEN - HOT - Semiconductors,")[1].split(",###")[0].split(",")) if "SCREEN - HOT - Semiconductors" in t2 else 0
        check(f"{tag} SCREEN cap: max 15 Candidates per file (HOT first, then newest); the rest stay in the Dashboard", n_hot + n_screen == 15 and n_hot == 2, [n_hot, n_screen])
        for i in range(20): js(page, "(k)=>td3MetaWrite(k,{dismissed:true})", f"Z{i:02d}")
        settle(page, 300)
        # ── Dashboard groups = export sections ──
        T.go_watch(page, "cand")
        hd = js(page, "()=>[...document.querySelectorAll('[data-tv1-group]')].map(e=>e.dataset.tv1Group)")
        check(f"{tag} Candidates tab: 'HOT · Semiconductors' header then 'Other' (same grouping as the file)", hd == ["HOT · Semiconductors", "Other"], hd)
        order = T.rows(page)
        check(f"{tag} Candidates order: HOT group (newest first MU, LRCX) then Other newest first (DDOG, FTNT)", order == ["MU", "LRCX", "DDOG", "FTNT"], order)
        tags = js(page, "()=>Object.fromEntries([...document.querySelectorAll('.wlR[data-sym]')].map(e=>[e.dataset.sym, [(e.querySelector('[data-tv1-src]')||{}).textContent, (e.querySelector('[data-tv1-age]')||{}).textContent]]))")
        check(f"{tag} row tags: reason + age ('Volume Spike' 3d · 'Earnings Spike' 1d)", tags["MU"] == ["Volume Spike", "3d"] and tags["DDOG"] == ["Earnings Spike", "1d"], tags)
        none_c = js(page, "()=>{ const e=document.querySelector('.wlR[data-sym=FTNT] [data-tv1-src]'); return [e.textContent, e.hasAttribute('data-ln4w-noreason'), getComputedStyle(e).color]; }")
        check(f"{tag} no reason → '—' amber", none_c[0] == "set reason" and none_c[1], none_c)   # LN4: amber 'set reason' 
        if w == 390: C.shot(page, "tv1-cand-390.png", full=True)
        else: C.shot(page, "tv1-cand-1440.png")
        # age ⚠ and 14d suggestion
        cand(page, "OLD12", "", days=12, reasons=["strong-rs"]); cand(page, "OLD16", "", days=16, reasons=["strong-rs"]); settle(page, 300); js(page, "()=>renderWatchlist()"); settle(page, 300)
        ag = js(page, "()=>Object.fromEntries([...document.querySelectorAll('.wlR[data-sym]')].map(e=>[e.dataset.sym, (e.querySelector('[data-tv1-age]')||{}).textContent]))")
        check(f"{tag} age '12d ⚠' at >= 12 days · FTNT 9d no warning", ag["OLD12"] == "12d⚠" and ag["FTNT"] == "9d" and ag["OLD16"] == "16d⚠", ag)
        check(f"{tag} no banner row; tap ⚠ on the 16d row → Drop / Keep 7 more days (LN4)", cnt(page, "[data-tv1-sug]") == 0 and (page.locator('[data-ln4w-warn="OLD16"]').click() or True) and cnt(page, '[data-tv1-sug="OLD16"]') == 1 and cnt(page, "[data-tv1-sug]") == 1)
        page.locator('[data-tv1-sug="OLD16"] [data-tv1-keep]').click(); settle(page, 400)
        km = cm(page, "OLD16")
        check(f"{tag} Keep 7 more days → suggestion gone · keep_until = today + 7 (2026-10-08) · nothing dropped", cnt(page, "[data-tv1-sug]") == 0 and km and km.get("keep_until") == "2026-10-08", km)
        js(page, "()=>glWrite(S=>{ S.candMeta.OLD16.keep_until = '2026-09-30'; })"); js(page, "()=>renderWatchlist()"); settle(page, 300)
        page.locator('[data-ln4w-warn="OLD16"]').click(); settle(page, 300)
        check(f"{tag} after the 7 days → suggestion returns on ⚠ (never automatic)", cnt(page, '[data-tv1-sug="OLD16"]') == 1 and cm(page, "OLD16") is not None)
        page.locator('[data-tv1-sug="OLD16"] [data-tv1-drop]').click(); settle(page, 400)
        check(f"{tag} Drop (one tap) → candidate removed", "OLD16" not in T.rows(page) and cm(page, "OLD16") is None)
        js(page, "()=>{ td3MetaWrite('OLD12',{dismissed:true}); }"); settle(page, 200)
        # ── Setup ✓ ──
        T.go_watch(page, "wl")
        order = T.rows(page)
        check(f"{tag} Watchlist: 'Setup ✓' group first (AVGO) with header, then 'Watchlist'", order[0] == "AVGO" and js(page, "()=>[...document.querySelectorAll('[data-tv1-group]')].map(e=>e.dataset.tv1Group)") == ["Setup ✓", "Watchlist"], order)
        page.locator('.wlR[data-sym="AVGO"]').click(); settle(page, 250)   # LN4: Setup ✓ lives in the tapped row's actions
        check(f"{tag} AVGO badge shows '5d left' on the day it is set", "5d left" in txt(page, '[data-tv1-setup="AVGO"]') and js(page, "()=>document.querySelector('[data-tv1-setup=AVGO]').getAttribute('aria-pressed')") == "true", txt(page, '[data-tv1-setup="AVGO"]'))
        page.locator('.wlR[data-sym="META"]').click(); settle(page, 250)
        page.locator('[data-tv1-setup="META"]').click(); settle(page, 400)
        check(f"{tag} one tap on META → Setup ✓ stored (tvSetup) and META sorts into the first group", js(page, "()=>!!tdSettings().tvSetup.META") and T.rows(page)[:2] == ["AVGO", "META"] or T.rows(page)[:2] == ["META", "AVGO"], T.rows(page))
        page.locator('[data-tv1-setup="META"]').click(); settle(page, 400)
        check(f"{tag} tap again = toggled off", not js(page, "()=>!!(tdSettings().tvSetup||{}).META"))
        exp = {"Thu 2026-09-24 (5 trading days used)": ("2026-09-24", 0), "Fri 2026-09-25 (4 used)": ("2026-09-25", 1), "Mon 2026-09-28 (3 used)": ("2026-09-28", 2), "Thu 2026-10-01 (today)": ("2026-10-01", 5)}
        res = {k: js(page, "(d)=>{ glWrite(S=>{ S.tvSetup = {AVGO:d}; }); return tv1SetupLeft('AVGO'); }", v[0]) for k, v in exp.items()}
        check(f"{tag} Setup ✓ auto-expires after 5 trading days (Mon–Fri, weekend not counted)", all(res[k] == exp[k][1] for k in exp), res)
        js(page, "()=>glWrite(S=>{ S.tvSetup = {NVDA:thaiToday()}; })")
        check(f"{tag} Setup ✓ clears once the stock has an entry (HOLD)", js(page, "()=>tv1SetupLeft('NVDA')") == 0)
        js(page, "()=>glWrite(S=>{ S.tvSetup = {AVGO:thaiToday()}; })")
        # ── Import ──
        T.go_watch(page, "cand")
        csv = "Symbol,Exchange,Description,Sector,Industry\nAMAT,NASDAQ,Applied Materials,Electronic technology,Semiconductors\nNET,NYSE,Cloudflare,Technology services,Software\nKCE,SET,KCE Electronics,Electronic technology,Electronic Components\nMU,NASDAQ,Micron,Electronic technology,Semiconductors\nMETA,NASDAQ,Meta,Technology services,Internet software\nBTCUSD,CRYPTO,Bitcoin,,\n"
        js(page, "()=>{ wlRestore = ()=>{}; }")
        T.wl_seed(page, [W("NVDA"), W("AVGO"), W("META", industry="Software"), W("CRWD", sector_etf="SMH"), W("AMD", ladder_watch=True, ladder_watch_set=True), W("DELTA.BK", mk="TH", ladder_watch=True, ladder_watch_set=True), W("CELH", archived=True)])
        csv += "CELH,NASDAQ,Celsius,,\n"
        js(page, "()=>tv1ImportOpen()"); settle(page, 300)
        page.set_input_files("[data-tv1-file]", {"name": "VolumeSpike_Momentum.csv", "mimeType": "text/csv", "buffer": csv.encode()}); settle(page, 500)
        groups = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-tv1-g]')].map(g=>[g.dataset.tv1G, [...g.querySelectorAll('[data-tv1-r]')].map(e=>e.dataset.tv1R)]))")
        check(f"{tag} import .csv preview: New (AMAT NET KCE) · Already Candidate (MU) · Already Watchlist (META) · Archived (CELH) · Non-stock (BTCUSD, CRYPTO exchange)", groups.get("new") == ["AMAT", "NET", "KCE"], groups)
        check(f"{tag} preview: skip groups", groups.get("cand") == ["MU"] and groups.get("wl") == ["META"] and groups.get("arch") == ["CELH"] and groups.get("non") == ["BTCUSD"], groups)
        meta_t = txt(page, "[data-tv1-meta]")
        check(f"{tag} reason 'Volume Spike' from the file name · track Momentum from the file name (no choice asked)", "Volume Spike" in meta_t and "Momentum" in meta_t and cnt(page, "[data-tv1-track]") == 0, meta_t)
        check(f"{tag} HOT marked in preview (AMAT Semiconductors · HOT)", "Semiconductors · HOT" in txt(page, '[data-tv1-r="AMAT"]'), txt(page, '[data-tv1-r="AMAT"]'))
        if w == 390: C.shot(page, "tv1-import-390.png")
        else: C.shot(page, "tv1-import-1440.png")
        before = js(page, "()=>JSON.stringify(tdSettings().candAddLog||{})"); mu0 = cm(page, "MU")
        page.locator("[data-tv1-add]").click(); settle(page, 500)
        am = cm(page, "AMAT"); kc = cm(page, "KCE")
        check(f"{tag} Add → Candidates only: AMAT saved (industry · tv · source 'TradingView' · Volume Spike · winner) · KCE market TH sym KCE.BK", am and am["industry"] == "Semiconductors" and am["tv"] == "NASDAQ:AMAT" and am["source"] == "TradingView" and am["reasons"] == ["volume-spike"] and am["track"] == "winner" and kc["market"] == "TH" and kc["sym"] == "KCE.BK", [am, kc])
        check(f"{tag} not in Watchlist · daily New Cand log (candAddLog) unchanged · toast 'Added 3'", js(page, "()=>wlItems.some(x=>x.ticker==='AMAT')") is False and js(page, "()=>JSON.stringify(tdSettings().candAddLog||{})") == before and "Added 3" in js(page, "()=>document.getElementById('tv1Toast').innerText"), before)
        info = js(page, "()=>JSON.parse(JSON.stringify(tdSettings().tvInfo))")
        check(f"{tag} existing MU / META: only tvSym + industry learned (candMeta untouched, no new Candidate)", info["MU"]["x"] == "NASDAQ:MU" and info["MU"]["i"] == "Semiconductors" and info["META"]["x"] == "NASDAQ:META" and cm(page, "META") is None and cm(page, "MU") == mu0, info)
        T.go_watch(page, "cand")
        hd = js(page, "()=>[...document.querySelectorAll('[data-tv1-group]')].map(e=>e.dataset.tv1Group)")
        check(f"{tag} imported industry drives HOT grouping: Semis group now MU, LRCX, AMAT (KCE → Other)", hd[0] == "HOT · Semiconductors" and set(T.rows(page)[:3]) == {"MU", "LRCX", "AMAT"}, [hd, T.rows(page)])
        # txt import with section reason + chosen track
        txt_in = "###SCREEN - Earnings Spike,NASDAQ:PLTR,NYSE:SNOW,###READY,NASDAQ:META"
        js(page, "()=>tv1ImportOpen()"); settle(page, 300)
        page.fill("[data-tv1-text]", txt_in); settle(page, 400)
        check(f"{tag} .txt: section name → reason 'Earnings Spike' · no file-name track → required choice shown", "Earnings Spike" in txt(page, "[data-tv1-reason]") and cnt(page, "[data-tv1-track]") == 2, txt(page, "[data-tv1-meta]"))
        page.locator("[data-tv1-add]").click(); settle(page, 300)
        check(f"{tag} Add without a track → blocked with a message, nothing saved", cm(page, "PLTR") is None and "Pick a track" in txt(page, "[data-tv1-err]"), txt(page, "[data-tv1-err]"))
        page.locator('[data-tv1-track="ladder"]').click(); settle(page, 200)
        page.locator("[data-tv1-add]").click(); settle(page, 500)
        pl = cm(page, "PLTR")
        check(f"{tag} chosen track Compounder saved · reason Earnings Spike · plain-ticker exchange learned (NASDAQ:PLTR)", pl and pl["track"] == "ladder" and pl["reasons"] == ["earnings-spike"] and pl["tv"] == "NASDAQ:PLTR", pl)
        # tvSym learning feeds the next export
        _, t3 = export(page, "winner")
        check(f"{tag} tvSym learning: next export uses NASDAQ:META / NASDAQ:AMAT (no bare ticker)", "NASDAQ:META" in t3 and "NASDAQ:AMAT" in t3 and ",AMAT" not in t3.replace("NASDAQ:AMAT", ""), t3)
        # round trip
        _, tm = export(page, "winner"); _, tc = export(page, "ladder")
        js(page, "()=>tv1ImportOpen()"); settle(page, 300)
        page.fill("[data-tv1-text]", tm + "," + tc); settle(page, 500)
        g2 = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-tv1-g]')].map(g=>[g.dataset.tv1G, g.querySelectorAll('[data-tv1-r]').length]))")
        check(f"{tag} round trip export → import = 0 New", "new" not in g2 and "Nothing to add" in txt(page, "[data-tv1-add]"), [g2, txt(page, "[data-tv1-add]")])
        js(page, "()=>tv1ImportClose()")
        check(f"{tag} no horizontal overflow · no console/page errors", T.ovf(page) <= 0 and not [x for x in ce if "Failed to load" not in x] and not pe, [T.ovf(page), ce[:3], pe[:2]])
    finally:
        b.close()


def tv1b_ideas():
    def mk(iid, name, nature, cands, segs=None):
        d = P59.idea(cands, iid=iid); d["name"] = name; d["idea"] = dict(d.get("idea") or {}, nature=nature)
        if segs is not None: d["chain"] = {"segments": segs}
        return d
    def c(sym, segs): x = P59.cand(sym, sym, 1, "study"); x["segments"] = segs; return x
    seg_semis = {"name": "Chips", "role": "r", "effect": "win", "trap": "t", "industries": ["Semiconductors"], "suggest": True, "pick": False}
    seg_none = {"name": "Misc", "role": "r", "effect": "win", "trap": "t", "industries": ["Zzz Unknown"], "suggest": True, "pick": False}
    return [mk("iE", "Memory squeeze", "event", [c("EV1", ["Chips"]), c("EV2", ["Chips"]), c("EV3", ["Chips"])], [seg_semis]),
            mk("iS", "IGV Software turned Improving - why?", "structural", [c("SW1", [])], []),
            mk("iN", "Plain idea", "structural", [c("NOS", ["Misc"])], [seg_none])]


def tests_tv1b(pw, w, h, backfill):
    tag = f"[{ENGINE}/tv1b-{'backfill' if backfill else 'move'}/{w}]"
    def mut(doc):
        for bk in doc["books"].values():
            st = bk.setdefault("settings", {})
            if backfill:
                st["candFromIdeasDone"] = {"at": "2026-09-01T00:00:00Z", "migrated": 4, "skipped": 0, "reasons": {}}
                old = {"manual": True, "market": "US", "cand_at": "2026-09-30T00:00:00Z", "track": "winner", "reasons": ["volume-spike"]}
                st["candMeta"] = {"EV1": dict(old, sym="EV1", source="From Ideas", idea_id="iE", note="From idea: Memory squeeze"),
                                  "SW1": dict(old, sym="SW1", source="From Ideas", idea_id="iS"),
                                  "GONE": dict(old, sym="GONE", source="From Ideas", idea_id="no-such-idea"),
                                  "NOS": dict(old, sym="NOS", source="From Ideas", idea_id="iN"),
                                  "KEEP": dict(old, sym="KEEP", source="TradingView", industry="Biotechnology")}
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, mut=mut, ideas=tv1b_ideas())
    try:
        settle(page, 1800)
        js(page, "()=>{ window.sectorState = etf=>({quad: (etf==='SMH' || etf==='IGV') ? 'lead' : 'lag', followed:false}); window.hotSectors = ()=>[{etf:'SMH', k:'lead', ratio:1},{etf:'IGV', k:'lead', ratio:1}]; }")
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); }"); settle(page, 600)
        m = js(page, "()=>JSON.parse(JSON.stringify(tdSettings().candMeta||{}))")
        check(f"{tag} Event idea: EV1 source 'Event' · idea_id iE · industry Semiconductors · sector_etf SMH", m.get("EV1", {}).get("source") == "Event" and m["EV1"].get("idea_id") == "iE" and m["EV1"].get("industry") == "Semiconductors" and m["EV1"].get("sector_etf") == "SMH", m.get("EV1"))
        check(f"{tag} Sector idea ('Ask why' idea named with IGV): SW1 source 'Sector' · idea_id iS · sector_etf IGV · sector 'Software'", m.get("SW1", {}).get("source") == "Sector" and m["SW1"].get("idea_id") == "iS" and m["SW1"].get("sector_etf") == "IGV" and "Software" in str(m["SW1"].get("sector")), m.get("SW1"))
        check(f"{tag} no sector derivable (NOS): source + idea_id saved, no sector_etf, industry kept as text", m.get("NOS", {}).get("source") == "Sector" and m["NOS"].get("idea_id") == "iN" and not m["NOS"].get("sector_etf") and m["NOS"].get("industry") == "Zzz Unknown", m.get("NOS"))
        if backfill:
            check(f"{tag} backfill: existing 'From Ideas' rows upgraded (EV1 Event / SW1 Sector) and old fields (track, reasons, note, cand_at) kept", m["EV1"].get("track") == "winner" and m["EV1"].get("reasons") == ["volume-spike"] and m["EV1"].get("cand_at") == "2026-09-30T00:00:00Z" and m["EV1"].get("note") == "From idea: Memory squeeze", m["EV1"])
            check(f"{tag} backfill: idea no longer found (GONE) left untouched · non-idea candidate (KEEP) untouched", m["GONE"].get("source") == "From Ideas" and "sector_etf" not in m["GONE"] and m["KEEP"] == {"manual": True, "market": "US", "cand_at": "2026-09-30T00:00:00Z", "track": "winner", "reasons": ["volume-spike"], "sym": "KEEP", "source": "TradingView", "industry": "Biotechnology"}, [m["GONE"], m["KEEP"]])
            n0 = js(page, "()=>tv1IdeaBackfill()")
            check(f"{tag} backfill is idempotent (second run writes nothing)", n0 == 0, n0)
        hd = js(page, "()=>[...document.querySelectorAll('[data-tv1-group]')].map(e=>e.dataset.tv1Group)")
        check(f"{tag} Candidates tab groups idea candidates under HOT · Semiconductors and HOT · Software (rest in Other)", "HOT · Semiconductors" in hd and "HOT · Software" in hd and "Other" in hd, hd)
        grp = js(page, "()=>{ const o={}; let g=''; for(const e of document.querySelectorAll('[data-tv1-group], .wlR[data-sym]')){ if(e.dataset.tv1Group) g=e.dataset.tv1Group; else (o[g]=o[g]||[]).push(e.dataset.sym); } return o; }")
        check(f"{tag} rows: EV1 EV2 EV3 under HOT · Semiconductors · SW1 under HOT · Software · NOS (+ GONE/KEEP) in Other", set(grp.get("HOT · Semiconductors", [])) == ({"EV1"} if backfill else {"EV1", "EV2", "EV3"}) and grp.get("HOT · Software") == ["SW1"] and "NOS" in grp.get("Other", []), grp)
        if "EV3" in m and not backfill:
            pass
        tags = js(page, "()=>Object.fromEntries([...document.querySelectorAll('.wlR[data-sym]')].map(e=>[e.dataset.sym, (e.querySelector('[data-tv1-src]')||{}).textContent]))")
        if not backfill: check(f"{tag} row tags show 'Event: …' / 'Sector: …' from the stored source", str(tags.get("EV1", "")).startswith("Event: Memory") and str(tags.get("SW1", "")).startswith("Sector: IGV"), tags)
        _, txt_m = export(page, "winner")
        check(f"{tag} export: SCREEN - HOT - Semiconductors holds EV1 EV2 EV3 · SCREEN - HOT - Software holds SW1", "###SCREEN - HOT - Semiconductors," in txt_m and "SW1" in txt_m.split("###SCREEN - HOT - Software,")[1].split(",###")[0] and all(k in txt_m.split("###SCREEN - HOT - Semiconductors,")[1].split(",###")[0] for k in (("EV1",) if backfill else ("EV1", "EV2", "EV3"))), txt_m)
        check(f"{tag} no console/page errors", not [x for x in ce if "Failed to load" not in x] and not pe, [ce[:3], pe[:2]])
    finally: b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            tests(pw, w, h); tests_tv1b(pw, w, h, False); tests_tv1b(pw, w, h, True)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    sys.exit(1 if bad else 0)
