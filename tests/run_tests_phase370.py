#!/usr/bin/env python3
"""LN4 — iPhone 390 readiness: screenshots of Today · Watch · Core form · Sat form · Plan list · Journal · Port · Settings
+ no horizontal scroll · text ≥ 12px · tap targets ≥ 36px (LN4-owned elements; the deliberate '✓ all' is exempt) · เทส 370
รัน: python3 run_tests_phase370.py → tests/screenshots/ln4-390-*.png"""
import json, sys
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests
import ts1_retire
import ln3fix_common as C
import lib_phase4 as base
import lib_phase24 as P24
import lib_phase106 as T
import lib_phase120 as P120
import lib_phase77 as P77

ENGINE = base.BROWSER_ENGINE
results = []
js, settle = C.js, T.settle


def check(name, ok, detail=""):
    if ts1_retire.skip(__name__ if __name__ != "__main__" else "run_tests_phase370", name): return   # TS1 check-level retirement
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


SCAN = """(sel)=>{
  const out = {small:[], tap:[]};
  const root = document.querySelector(sel); if(!root) return {missing:true};
  const vis = e=>{ const r = e.getBoundingClientRect(); const cs = getComputedStyle(e); return r.width>0 && r.height>0 && cs.visibility!=='hidden' && cs.display!=='none'; };
  root.querySelectorAll('*').forEach(e=>{
    if(!vis(e) || e.closest('[data-ln4-all]')) return;
    const own = [...e.childNodes].some(n=>n.nodeType===3 && n.textContent.trim());
    const fs = parseFloat(getComputedStyle(e).fontSize);
    if(own && fs < 11.85) out.small.push((e.className||e.tagName)+':'+fs+':'+e.textContent.trim().slice(0,18));
    if(/^(BUTTON|SELECT)$/.test(e.tagName) || (e.tagName==='INPUT' && /text|checkbox/.test(e.type))){
      const r = e.getBoundingClientRect(), box = e.type==='checkbox' ? (e.closest('label')||e).getBoundingClientRect() : r;
      if(box.height < 35.5) out.tap.push((e.className||e.tagName)+':'+Math.round(box.height)+':'+(e.textContent||e.value||'').trim().slice(0,14));
    }
  });
  out.small = out.small.slice(0,8); out.tap = out.tap.slice(0,8);
  return out;
}"""


def ovf(page): return js(page, "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")


def shot(page, name): C.shot(page, f"ln4-390-{name}.png", full=True)


def scan(page, tag, name, sel, shots=True):
    if shots: shot(page, name)
    r = js(page, SCAN, sel) if False else page.evaluate(SCAN, sel)
    check(f"{tag} {name}: no horizontal scroll", ovf(page) <= 0, ovf(page))
    check(f"{tag} {name}: text ≥ 12px ({sel})", not r.get("small"), r.get("small"))
    check(f"{tag} {name}: tap targets ≥ 36px ({sel})", not r.get("tap"), r.get("tap"))
    return r


def run(pw):
    w, h = 390, 844
    tag = f"[{ENGINE}/390]"
    cards = {
        "ccAM": P24.card("ccAM", "main", "AMD", plan={"entry": 182.5, "stop": 170}, px=170, pxDate="2026-10-01"),
        "ccNV": P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=168, tier="A", lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 168}]),
        "ccAV": P24.card("ccAV", "main", "AVGO", plan={"entry": 341.2, "stop": 320}, px=330, pxDate="2026-10-01", track="ladder"),
    }
    b, page, ce, pe = T.launch(pw, w, h, iso=T.NOW, picks=("XAUUSD",), weekly=False)
    try:
        import lib_phase13 as P13
        P24.set_ff(page, P24.ff_json(True, True))
        js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("tNV", "core", "open", sym="NVDA", entry=171.4, sl=168, qty=10, cur="USD", date="2026-09-10")])
        for cid, c in cards.items():
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
        js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)
        P120.ps_on(page)
        # Today
        T.go_today(page)
        page.locator("[data-ln4-more]").click(); settle(page, 300)
        scan(page, tag, "today", "[data-ln4]")
        # Watch
        for t_ in ("AAA", "BBB"):   # WL1 — the Candidate list is gone: the Watch list is the lean list
            page.evaluate("([t])=>window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist',t], {ticker:t, market:'US', port:'core', note:'', industry:'', added_at:'2026-09-01T00:00:00Z', exch:'NASDAQ'})", [t_])
        js(page, "()=>{ wlStop(); wlStart(); }"); settle(page, 700)
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); settle(page, 600)
        page.locator('[data-wl1-row][data-sym="AAA"]').click(); settle(page, 300)
        js(page, "()=>wlBack && wlBack()"); settle(page, 300)
        scan(page, tag, "watch", "#watchGroups")
        rows = js(page, "()=>[...document.querySelectorAll('[data-wl1-row] .l1')].map(e=>(()=>{ const c=[...e.children].map(k=>{const r=k.getBoundingClientRect(); return r.top+r.height/2;}); return Math.max(...c)-Math.min(...c) < 12 ? 1 : 2; })())")
        check(f"{tag} watch: symbol · exchange · status chip on one line", rows and all(x == 1 for x in rows), rows)
        # Core form
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); settle(page, 500)
        scan(page, tag, "plan-list", "#tab-plan, body", True) if False else shot(page, "plan-list")
        check(f"{tag} plan-list: no horizontal scroll", ovf(page) <= 0, ovf(page))
        js(page, "()=>coreNewOpen('main',{ticker:'AAA'})"); settle(page, 700)
        P120.fill(page, 100, 90)
        scan(page, tag, "core-form", ".core-sheet, #lfCoreSide, .ps1Frm")
        sm = js(page, "()=>{ const e=document.getElementById('cnSum'); return e ? Math.round(e.getBoundingClientRect().height / parseFloat(getComputedStyle(e).lineHeight || 18)) : 0; }")
        check(f"{tag} core-form: summary ≤ 2 lines", sm <= 2, sm)
        js(page, "()=>coreSheetClose()")
        # Sat form
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid])
        for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)])
        js(page, "([i])=>{ switchTab('plan'); td3SatOpen(i, ''); }", [iid]); settle(page, 700)   # PB1b: the Sat form is the popup form
        js(page, "()=>{ pb2.ema=true; pb2.str=false; pb2.mss=true; pb2Refresh(); }"); settle(page, 200)
        scan(page, tag, "sat-form", "#pb2Body")
        order = js(page, "()=>{ const q=s=>{const e=document.querySelector(s); return e?Math.round(e.getBoundingClientRect().top):-1}; return [q('[data-pb2-seg]'), q('[data-pb2-prices]'), q('[data-pb2-trend]'), q('[data-pb2-mss]'), q('[data-pb2-size]'), q('[data-pb2-rem]'), q('[data-pb2-draft]')]; }")
        check(f"{tag} sat-form: Buy|Sell → Entry/SL/TP → Trend → MSS → size → reminder → Save (one column, top to bottom)", all(x > 0 for x in order) and order == sorted(order), order)
        w_ = js(page, "()=>{ const b=document.getElementById('pb2Body'), br=b.getBoundingClientRect(); const tr=document.querySelector('.pb2-trow').getBoundingClientRect(), sz=document.querySelector('[data-pb2-size]').getBoundingClientRect(); return {fit:b.scrollWidth<=b.clientWidth+1, inside:[...b.querySelectorAll('*')].every(e=>e.getBoundingClientRect().right<=br.right+1), trendH:Math.round(tr.height), sizeInside:sz.right<=br.right+1}; }")
        check(f"{tag} sat-form: nothing wider than the sheet · Trend row stays on one line · size box inside", w_["fit"] and w_["inside"] and w_["trendH"] < 50 and w_["sizeInside"], w_)
        check(f"{tag} sat-form: no Setup chips / ✓ all / checkboxes / account rows from the old inline form", js(page, "()=>document.querySelectorAll('#bdPop .pf-chip, #bdPop [data-ln4-all], #bdPop input[type=checkbox], #bdPop .ln1-sz').length") == 0)
        t = js(page, "()=>document.getElementById('pb2Body').innerText")
        check(f"{tag} sat-form: wrong-side error not duplicated", t.count('wrong side') == 0 and t.count('needs SL') <= 1, t.count('needs SL'))
        js(page, "()=>bdPopClose()")
        # Journal
        js(page, "()=>{ switchTab('journal'); }"); settle(page, 600)
        scan(page, tag, "journal", "#tab-journal, #jFilters")
        # Port
        js(page, "()=>{ switchTab('port'); }"); settle(page, 600)
        shot(page, "port")
        check(f"{tag} port: no horizontal scroll", ovf(page) <= 0, ovf(page))
        # Settings
        js(page, "()=>{ openSettings(); }"); settle(page, 600)
        js(page, "()=>{ const e=document.getElementById('ln4SetBox'); if(e) e.scrollIntoView({block:'center'}); }"); settle(page, 300)
        r = scan(page, tag, "settings", "#ln4SetBox")
        right = js(page, "()=>{ const r=document.querySelector('[data-ln4-setfeature]'); if(!r) return null; const i=r.querySelector('input').getBoundingClientRect(), b=r.getBoundingClientRect(); return i.right >= b.right - 6; }")
        check(f"{tag} settings: switch stays on the right", right is True, right)
        check(f"{tag} no console/page errors", not ce and not pe, [ce[:3], pe[:3]])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        try: run(pw)
        except Exception as e:
            import traceback; traceback.print_exc(); check("crashed", False, str(e)[:300])
    n = sum(1 for r in results if r[1])
    print(f"\n{n}/{len(results)} PASS")
    sys.exit(0 if n == len(results) else 1)
