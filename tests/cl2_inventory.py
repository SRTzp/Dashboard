#!/usr/bin/env python3
"""CL2 A — Thai inventory: visit every screen/segment/sheet reachable by one click on seeded data, collect every VISIBLE text node / placeholder / title / aria-label with Thai, plus Thai browser-dialog messages.
Run: python3 tests/cl2_inventory.py [--write]   → prints count; --write writes docs/reports/CL2-thai-inventory.md"""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from e2e1_common import *
import e2e1_common as E
import run_tests_e2e1 as R

HERE = os.path.dirname(os.path.abspath(__file__))
TH = r"[฀-๿]"
COLLECT = """()=>{ const TH=/[\\u0E00-\\u0E3E\\u0E40-\\u0E7F]/; const out=[]; document.querySelectorAll('details').forEach(d=>{ if(!d.closest('#bdPop,.moreMenu')) d.open=true; });
 const vis=e=>{ if(!e||!e.getClientRects().length) return false; const cs=getComputedStyle(e); return cs.visibility!=='hidden'&&cs.display!=='none'&&+cs.opacity>0; };
 const desc=e=>{ let s=e.tagName.toLowerCase(); if(e.id) s+='#'+e.id; else if(e.className&&typeof e.className==='string') s+='.'+e.className.trim().split(/\\s+/).slice(0,2).join('.'); return s; };
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT); let n; while(n=w.nextNode()){ const t=n.nodeValue.replace(/\\s+/g,' ').trim(); if(!t||!TH.test(t)) continue; const p=n.parentElement; if(!p||/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE)$/.test(p.tagName)) continue; if(!vis(p)) continue; out.push({k:'text',t,el:desc(p),ctx:(p.outerHTML||'').slice(0,240)}); }
 document.querySelectorAll('[placeholder],[title],[aria-label]').forEach(e=>{ if(!vis(e)) return; ['placeholder','title','aria-label'].forEach(a=>{ const v=e.getAttribute(a); if(v&&TH.test(v)) out.push({k:a,t:v.replace(/\\s+/g,' ').trim(),el:desc(e)}); }); });
 document.querySelectorAll('input,textarea,select').forEach(e=>{ if(!vis(e)||e.type==='password') return; const v=e.tagName==='SELECT'?(e.selectedOptions[0]||{}).text:e.value; if(v&&TH.test(v)&&e.tagName==='SELECT') out.push({k:'option',t:v,el:desc(e)}); });
 (window.__dlg||[]).filter(d=>TH.test(String(d.m))).forEach(d=>out.push({k:d.k,t:String(d.m).replace(/\\s+/g,' ').trim(),el:'window.'+d.k})); window.__dlg=[];
 return out; }"""
SPY = """()=>{ window.__dlg=window.__dlg||[]; window.prompt=(m,d)=>{ window.__dlg.push({k:'prompt',m}); return String(d==null?'':d); }; window.confirm=m=>{ window.__dlg.push({k:'confirm',m}); return true; }; window.alert=m=>{ window.__dlg.push({k:'alert',m}); }; window.open=()=>null; }"""
CLOSE = R.RESET.replace("window.prompt = (m, d)=>String(d); window.confirm = ()=>true; window.alert = ()=>{}; window.open = ()=>null;", "") + "; ()=>0"
RESET = R.RESET.split("window.prompt")[0] + "}"
RESET = RESET.replace("; }", "}", 0)


def screens(page):
    S = lambda s: (lambda: js(page, s))
    sets = [
      ("Today · Daily", "()=>{ switchTab('today'); td3SetMode('d'); re2GrpAll={enter:true,check:true,manage:true}; todayRefresh(true); }"),
      ("Today · Weekend", "()=>{ switchTab('today'); td3SetMode('w'); todayRefresh(true); }"),
      ("Plan · Planned", "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); }"),
      ("Plan · Ordered", "()=>{ switchTab('plan'); bdSetSeg('ord'); bdRender(); }"),
      ("Plan · Holding", "()=>{ switchTab('plan'); bdSetSeg('hold'); bdRender(); }"),
      ("Flow", "()=>{ switchTab('flow'); }"),
      ("Watch · Ideas", "()=>{ switchTab('watch'); wlSetView('idea'); }"),
      ("Watch · Momentum/Compounder list", "()=>{ switchTab('watch'); wlSetView('wl'); }"),
      ("Watch · Screen", "()=>{ switchTab('watch'); wlSetView('screen'); }"),
      ("Watch · stock detail", "()=>{ switchTab('watch'); wlSetView('wl'); wlOpen('AAPL'); }"),
      ("Watch · Homework page", "()=>{ switchTab('watch'); wlSetView('wl'); hwOpen('AAPL'); }"),
      ("Journal", "()=>{ switchTab('journal'); }"),
      ("Port", "()=>{ switchTab('mix'); }"),
      ("Settings · Portfolio", "()=>{ switchTab('today'); openSettings(); }"),
      ("Settings · System", "()=>{ switchTab('today'); openSystemSettings(); }"),
      ("Settings · Industries", "()=>{ switchTab('today'); openIndustryManager(); }"),
      ("Plan · Stocks (Momentum) · Planned", "()=>{ switchTab('plan'); setPlanScope('stock'); }"),
      ("Plan · Stocks (Compounder)", "()=>{ switchTab('plan'); setPlanScope('ladder'); }"),
      ("Plan · Future", "()=>{ switchTab('plan'); setPlanScope('future'); }"),
      ("Sheet · Core weekly-close price", "()=>{ switchTab('plan'); setPlanScope('stock'); corePxOpen('xAAA'); }"),
      ("Sheet · New Core plan", "()=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen(); }"),
      ("Manage drawer", "()=>{ switchTab('today'); todayRefresh(true); bdOpen('x1'); }"),
      ("Plan drawer", "()=>{ switchTab('plan'); bdSetSeg('plan'); bdRender(); bdOpen('b1'); }"),
    ]
    return sets

LISTB = """()=>{ const l=[...document.querySelectorAll('button,[role=button],summary,[onclick]')].filter(b=>b.getClientRects().length&&!b.disabled&&b.getAttribute('aria-disabled')!=='true'&&!b.closest('#tabsMain,#sdToast')&&getComputedStyle(b).visibility!=='hidden'); return l.map((b,i)=>({i,sig:(b.innerText||b.getAttribute('aria-label')||b.title||'').replace(/\\s+/g,' ').trim().slice(0,30)+'|'+(b.getAttribute('onclick')||'').slice(0,90)})); }"""
CLICKN = """(i)=>{ const l=[...document.querySelectorAll('button,[role=button],summary,[onclick]')].filter(b=>b.getClientRects().length&&!b.disabled&&b.getAttribute('aria-disabled')!=='true'&&!b.closest('#tabsMain,#sdToast')&&getComputedStyle(b).visibility!=='hidden'); const b=l[i]; if(!b) return false; try{ b.click(); }catch(e){ return false; } return true; }"""
NAVSKIP = r"switchTab|moreMenuGo|openSettings|openSystem|openIndustry|wlSetView|bdSetSeg|td3SetMode|toggleMore|openMore"


WATCH_SCREENS = [
  ("Watch (fixture) · Ideas", "()=>{ switchTab('watch'); wlSetView('idea'); }"), ("Watch (fixture) · Momentum list", "()=>{ switchTab('watch'); wl1Trk='winner'; wlSetView('wl'); }"),
  ("Watch (fixture) · Compounder list", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); }"), ("Watch (fixture) · Screen", "()=>{ switchTab('watch'); wlSetView('screen'); }"),
  ("Watch (fixture) · AAPL detail", "()=>{ switchTab('watch'); wlSetView('wl'); wlOpen('AAPL'); }"), ("Watch (fixture) · AAPL Homework", "()=>{ switchTab('watch'); wl1Trk='winner'; wlSetView('wl'); hwOpen('AAPL'); }"),
  ("Watch (fixture) · COST Homework", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); hwOpen('COST'); }"), ("Watch (fixture) · WHSE Homework", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); hwOpen('WHSE'); }"),
  ("Watch (fixture) · ZZ Homework", "()=>{ switchTab('watch'); wl1Trk='ladder'; wlSetView('wl'); hwOpen('ZZ'); }"),
  ("Watch (fixture) · Add stocks sheet", "()=>{ switchTab('watch'); wlSetView('wl'); wl1ImpOpen(); }"),
]


def inventory(pw, w, mode="main"):
    if mode == "watch":
        import hw1_common as HW
        b, page, pe = HW.open_hw(pw, w, 900 if w >= 900 else 844); page.set_default_timeout(5000)
    else:
        b, page, ce, pe = R.crawl_seed(pw, w); page.set_default_timeout(5000)
    rows = []; seen = set()
    def add(screen, via, items):
        for x in items:
            key = (screen, x["k"], x["t"])
            if key in seen: continue
            seen.add(key); rows.append({"w": w, "screen": screen, "via": via, "k": x["k"], "t": x["t"], "el": x["el"], "ctx": x.get("ctx","")})
    try:
        js(page, SPY)
        for name, setup in (WATCH_SCREENS if mode == 'watch' else screens(page)):
            def go():
                js(page, R.RESET.split("window.prompt")[0] + "}"); js(page, SPY)
                try: js(page, setup)
                except Exception as e: pass
                page.wait_for_timeout(250)
            go(); add(name, "", js(page, COLLECT))
            lst = js(page, LISTB); done = set(); n = 0
            for x in lst:
                if x["sig"] in done: continue
                done.add(x["sig"])
                if re.search(R.SKIP, x["sig"], re.I) or re.search(NAVSKIP, x["sig"]): continue
                if n >= 60: break
                go()
                cur = js(page, LISTB)
                tgt = next((y for y in cur if y["sig"] == x["sig"]), None)
                if not tgt: continue
                if not js(page, CLICKN, tgt["i"]): continue
                n += 1; page.wait_for_timeout(200)
                try: items = js(page, COLLECT)
                except Exception: continue
                add(name, "click: " + x["sig"].split("|")[0][:28].strip(), items)
        if mode == "watch": return rows
        # static overlays / banners that only open from a data state or a hidden path: force each one open once (this is what the user sees when it does open)
        for oid in ("teOverlay", "closePosOverlay", "glValOverlay", "wlAddOverlay", "ltOverlay", "sysOverlay", "reasonMgrOverlay", "scoreMgrOverlay", "cancelOverlay", "ffQeOverlay", "ffSetOverlay", "industryOverlay", "setOverlay"):
            js(page, "(id)=>{ document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show')); const o=document.getElementById(id); if(o) o.classList.add('show'); }", oid); page.wait_for_timeout(120)
            add("Sheet (forced open) · " + oid, "", js(page, COLLECT))
            js(page, "(id)=>{ const o=document.getElementById(id); if(o) o.classList.remove('show'); }", oid)
        js(page, "()=>{ const b=document.getElementById('bkBanner'); if(b) b.classList.add('show'); }"); page.wait_for_timeout(120)
        add("Weekly backup banner (forced open)", "", js(page, COLLECT)); js(page, "()=>{ const b=document.getElementById('bkBanner'); if(b) b.classList.remove('show'); }")
        # the More menu
        js(page, "()=>{ switchTab('today'); }"); js(page, "()=>{ const m=document.getElementById('moreMenu'); if(m) m.classList.add('show'); try{ toggleMore(); }catch(e){} }"); page.wait_for_timeout(250)
        add("More menu", "", js(page, COLLECT))
    finally:
        b.close()
    return rows


def src_lines():
    L = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read().split("\n")
    return L


def find_line(L, t):
    runs = re.findall(r"[฀-๿][฀-๿\s\.\,\-\(\)/%0-9a-zA-Z·›]{3,}", t)
    for r in sorted(runs, key=len, reverse=True)[:2]:
        key = r.strip()[:24]
        for i, l in enumerate(L):
            if key in l: return i + 1
    return 0


if __name__ == "__main__":
    allrows = []
    with sync_playwright() as pw:
        for w in (1440, 390):
            if os.environ.get("INV_MODE") != "watch": allrows += inventory(pw, w)
            if os.environ.get("INV_MODE") != "main": allrows += inventory(pw, w, 'watch')
    L = src_lines()
    uniq = {}
    for r in allrows:
        k = (r["screen"], r["t"])
        if k not in uniq: uniq[k] = dict(r, ws={r["w"]})
        else: uniq[k]["ws"].add(r["w"])
    out = sorted(uniq.values(), key=lambda r: (r["screen"], r["t"]))
    for r in out: r["line"] = find_line(L, r["t"])
    json.dump(out, open(os.environ.get("INV_JSON", "/tmp/cl2_inv.json"), "w"), ensure_ascii=False, indent=1, default=list)
    print("INVENTORY", len(out), "items;", len({r['t'] for r in out}), "distinct texts")
    if "--write" in sys.argv:
        P = os.path.join(HERE, "..", "docs", "reports", "CL2-thai-inventory.md")
        with open(P, "w", encoding="utf-8") as f:
            f.write("# CL2 · Thai text the user sees (inventory)\n\nCrawl: seeded data, 1440 + 390; every tab/segment/Homework page/Settings/drawers + every sheet/menu reachable by one click (delete/external skipped). Count **%d** items (%d distinct texts).\n\n| Screen | Kind | Text | Source line |\n|---|---|---|---|\n" % (len(out), len({r['t'] for r in out})))
            for r in out: f.write("| %s | %s | %s | %s |\n" % (r["screen"], r["k"], r["t"].replace("|", "\\|"), r["line"] or "?"))
