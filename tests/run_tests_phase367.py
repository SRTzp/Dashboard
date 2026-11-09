#!/usr/bin/env python3
"""SK1 — Skills-due line · Weekend default Sat/Sun (manual switch kept for the day) · ←/→ Daily/Weekend · เทส 367 · Chromium · 390 + 1440 · SAMPLE data only
รัน: python3 run_tests_phase367.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase106 as T

ENGINE = base.BROWSER_ENGINE
results = []
js, settle, cnt, txt = C.js, T.settle, T.cnt, T.txt
SHOTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
THU, FRI, SAT, SUN, MON, TUE = ("2026-10-01T05:00:00Z", "2026-10-02T05:00:00Z", "2026-10-03T05:00:00Z", "2026-10-04T05:00:00Z", "2026-10-05T05:00:00Z", "2026-10-06T05:00:00Z")


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def at(page, iso):
    T.clock(page, iso)
    js(page, "()=>{ sk1Day=''; localStorage.removeItem('dash.td3ModeDay'); }")


def refresh(page):
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 500)


def setup(page, wl=None, ideas=0, stk=None, wi=False, pb=None):
    """wl = [(sym, age_days|None)] · stk = period_end|None · wi = bool · pb = quarter|None"""
    js(page, """([wl, ideas, stk, wi, pb])=>{
      const today = thaiToday(), ago = n=>new Date(Date.parse(today+'T00:00:00Z')-n*86400000).toISOString().slice(0,10);
      const rows = (wl||[]).map(([s,a])=>({sym:s, market:'US', item:{ticker:s, thesis: a==null ? null : {date:ago(a), schema:'living-thesis@1'}}}));
      window.wlRowsAll = ()=>({wl:rows, cand:[]});
      window.wlThesisOf = it=>it && it.thesis ? it.thesis : null;
      ideaList = Array.from({length:ideas}, (_,i)=>({id:'i'+i, idea:{name:'I'+i}, log:[], imported_at:today}));
      stkLoaded = true; wiLoaded = true; pbLoaded = true;
      stkDocs = stk ? {e1:{period_end:stk, period_start:ago(7), stocks:{}}} : {};
      window.stkLatest = ()=>stk ? stkDocs.e1 : null;
      window.wiCurDoc = ()=>wi ? {assets:{}} : null;
      pbList = pb ? [{id:'p', status:'active', quarter:pb, versionNo:1}] : [];
    }""", [wl, ideas, stk, wi, pb])
    refresh(None if False else page)


# LN4 — the Skills-due line is now part of Today › To do (chips). Rules unchanged (sk1Items) → read the To do model.
def _sk(page): return js(page, "()=>ln4TodoItems(tdLast || {today:thaiToday(), weekday:true}).filter(x=>x.id.indexOf('sk:')===0).map(x=>({id:x.id.slice(3), t:x.t}))")
def line(page): return " · ".join(x["t"] for x in _sk(page))
def names(page): return [x["id"] for x in _sk(page) if x["id"] != "lt+"]
def nsk(page): return len(_sk(page))
def stxt(page): return [x["t"] for x in _sk(page) if x["id"] != "lt+"]


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h, iso=THU, picks=(), weekly=False)
    try:
        today_ok = lambda: js(page, "()=>activeTab")
        # --- Skills due rules ---
        at(page, SAT); setup(page, wl=[("AVGO", 5)], ideas=0, stk=None, wi=False, pb="2026Q4")
        n = names(page)
        check(f"{tag} Sat: stock-news + idea-scout shown, WI not in line", "stk" in n and "idea" in n and "wi" not in n, n)
        check(f"{tag} Sat text carries 'idea-scout (0/2 ideas)'", "idea-scout (0/2 ideas)" in line(page))
        setup(page, ideas=1, stk="2026-10-02", pb="2026Q4", wl=[("AVGO", 5)])
        check(f"{tag} Sat: 1 idea + edition this week → line absent", nsk(page) == 0, line(page))
        at(page, SUN); setup(page, ideas=0, stk="2026-09-25", pb="2026Q4", wl=[])
        check(f"{tag} Sun: edition from last week → stock-news shown; 0 ideas shown", {"stk", "idea"} <= set(names(page)), names(page))
        at(page, FRI); setup(page, ideas=0, stk=None, wi=False, pb="2026Q4", wl=[])
        check(f"{tag} Fri: stock-news + idea-scout hidden → line absent", nsk(page) == 0, line(page))
        at(page, MON); setup(page, wi=False, ideas=0, stk=None, pb="2026Q4", wl=[])
        check(f"{tag} Mon + no WI → shown 'weekly-impact (last day today)'; stk/idea hidden", names(page) == ["wi"] and "last day today" in line(page), names(page))
        setup(page, wi=True, pb="2026Q4", wl=[])
        check(f"{tag} Mon + WI present → hidden", nsk(page) == 0)
        at(page, TUE); setup(page, wi=False, pb="2026Q4", wl=[])
        check(f"{tag} Tue + no WI → hidden (no nagging)", nsk(page) == 0, line(page))
        # living-thesis
        at(page, THU); setup(page, wl=[("AVGO", 31), ("NVDA", 29), ("MSFT", None)], pb="2026Q4", wi=True)
        txts = stxt(page)
        check(f"{tag} thesis 31d shown · 29d hidden · missing shown (oldest/missing first)", txts == ["living-thesis: MSFT none", "living-thesis: AVGO 31d"], txts)
        setup(page, wl=[("A", 40), ("B", 50), ("C", 60)], pb="2026Q4", wi=True)
        txts = stxt(page)
        check(f"{tag} 3 stale → 2 shown + '+1'", txts == ["living-thesis: C 60d", "living-thesis: B 50d"] and "+1 more" in line(page), [txts, line(page)])
        # playbook
        at(page, "2026-12-26T05:00:00Z"); setup(page, pb="2026Q4", wi=True, wl=[])
        check(f"{tag} quarter end −5d, no next-quarter playbook → 'playbook: quarter end in 5d'", "playbook: quarter end in 5d" in line(page), line(page))
        at(page, "2026-12-28T05:00:00Z"); setup(page, pb="2027Q1", wi=True, wl=[])
        check(f"{tag} next-quarter playbook exists → hidden", nsk(page) == 0)
        at(page, "2026-12-21T05:00:00Z"); setup(page, pb="2026Q4", wi=True, wl=[])
        check(f"{tag} quarter end −10d → hidden", nsk(page) == 0, line(page))
        at(page, "2027-01-05T05:00:00Z"); setup(page, pb="2026Q4", wi=True, wl=[])
        check(f"{tag} past quarter end, no playbook for new quarter → shown", "playbook" in (line(page) or ""), line(page))
        # nothing due
        at(page, THU); setup(page, pb="2026Q4", wi=True, wl=[("AVGO", 3)])
        check(f"{tag} nothing due → line absent", nsk(page) == 0)
        # position + copy
        at(page, SAT); setup(page, wl=[("AVGO", 35)], ideas=0, stk=None, pb="2026Q4")
        check(f"{tag} skills chips sit in the status card's To do row (above Act/Find)", js(page, "()=>{ const t=document.querySelector('[data-ln4-todorow]'), s=document.querySelector('[data-ln4-status]'); return !!(t && s && s.contains(t)); }"))
        js(page, "()=>{ window.__cp=[]; Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__cp.push(t);return Promise.resolve()}},configurable:true}); }")
        page.locator('[data-ln4-todo^="sk:lt:"]').first.click(); settle(page, 400)
        cp = js(page, "()=>window.__cp.slice()")
        check(f"{tag} tapping a skill chip copies its prompt (starts with skill name) + CG1 toast", len(cp) == 1 and cp[0].startswith("living-thesis update: AVGO") and cnt(page, "#cgToast.show") == 1, cp)
        page.locator('[data-ln4-todo="sk:idea"]').evaluate("e=>e.click()"); settle(page, 400)
        cp = js(page, "()=>window.__cp.slice()")
        check(f"{tag} item tap copies that item's prompt", len(cp) == 2 and cp[1].startswith("idea-scout"), cp)
        os.makedirs(SHOTS, exist_ok=True)
        page.screenshot(path=os.path.join(SHOTS, f"sk1-today-{w}.png"))
        # --- default mode ---
        for iso, want, nm in ((SAT, "w", "Sat"), (SUN, "w", "Sun"), (MON, "d", "Mon"), (FRI, "d", "Fri")):
            at(page, iso); setup(page, pb="2026Q4", wi=True, wl=[])
            check(f"{tag} {nm} opens on {'Weekend' if want == 'w' else 'Daily'}", js(page, "()=>td3Mode") == want and cnt(page, f'[data-td3-tab="{want}"].on') == 1, js(page, "()=>td3Mode"))
        at(page, SAT); setup(page, pb="2026Q4", wi=True, wl=[])
        page.locator('[data-td3-tab="d"]').click(); settle(page, 300)
        refresh(page); refresh(page)
        check(f"{tag} manual switch kept for the rest of the day", js(page, "()=>td3Mode") == "d")
        T.clock(page, SUN); refresh(page)
        check(f"{tag} next day (Sun) default applies again", js(page, "()=>td3Mode") == "w")
        # storage blocked
        at(page, MON); setup(page, pb="2026Q4", wi=True, wl=[])
        js(page, "()=>{ Storage.prototype.setItem=function(){throw new Error('blocked')}; Storage.prototype.getItem=function(){throw new Error('blocked')}; sk1Day=''; }")
        refresh(page); page.locator('[data-td3-tab="w"]').click(); settle(page, 300)
        check(f"{tag} storage blocked → default + switching still work", js(page, "()=>td3Mode") == "w" and cnt(page, "[data-td3-panel='week']") == 1)
        # --- keys ---
        if w > 430:
            b.close(); b, page, ce, pe = T.launch(pw, w, h, iso=MON, picks=(), weekly=False)
            at(page, MON); setup(page, pb="2026Q4", wi=True, wl=[])
            m = lambda: js(page, "()=>td3Mode")
            check(f"{tag} Mon starts Daily; ← on Daily does nothing", m() == "d" and (page.keyboard.press("ArrowLeft") or True) and m() == "d")
            page.keyboard.press("ArrowRight"); settle(page, 300)
            check(f"{tag} → = Weekend", m() == "w" and cnt(page, "[data-td3-panel='week']") == 1)
            page.keyboard.press("ArrowRight"); settle(page, 200)
            check(f"{tag} → on Weekend: no wrap", m() == "w")
            page.keyboard.press("ArrowLeft"); settle(page, 300)
            check(f"{tag} ← = Daily", m() == "d")
            page.keyboard.press("ArrowRight"); settle(page, 300)
            at_sw = js(page, "()=>JSON.parse(localStorage.getItem('dash.td3ModeDay')||'null')")
            check(f"{tag} key switch counts as manual (stored for the day)", at_sw and at_sw["m"] == "w", at_sw)
            page.keyboard.press("ArrowLeft"); settle(page, 300)
            # typing
            js(page, "()=>{ const i=document.createElement('input'); i.id='sk1t'; document.body.appendChild(i); i.focus(); }")
            page.keyboard.press("ArrowRight"); settle(page, 200)
            check(f"{tag} ignored while typing in an input", m() == "d")
            js(page, "()=>{ document.getElementById('sk1t').remove(); document.activeElement.blur(); }")
            js(page, "()=>td4RiskOpen('sat')"); settle(page, 300)
            page.keyboard.press("ArrowRight"); settle(page, 200)
            check(f"{tag} ignored while a sheet is open", m() == "d")
            js(page, "()=>td4RiskClose()")
            js(page, "()=>switchTab('flow')"); settle(page, 300)
            page.keyboard.press("ArrowRight"); settle(page, 200)
            js(page, "()=>switchTab('today')"); settle(page, 300)
            check(f"{tag} ignored on another tab", m() == "d")
            # Watch arrows unchanged
            js(page, "()=>{ switchTab('watch'); }"); settle(page, 300)
            js(page, "()=>{ window.__wsub=[]; const o=wlSetSub; window.wlSetSub=function(s){ window.__wsub.push(s); return o.apply(this,arguments); }; }")
            page.keyboard.press("ArrowRight"); settle(page, 200)
            check(f"{tag} Watch tab: ← → leave Today mode alone", m() == "d")
        check(f"{tag} no console/page errors", not (ce or pe), [ce[:3], pe[:3]])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844)):
            tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
