#!/usr/bin/env python3
"""LN4b — Mac text one step up (1280 · 1440, no new wraps/overflow) + iPhone 390 compact Today
(HOT one row 3+N · HOT = Leading + Fresh only · events ≤ 3 grouped lines · To do grouped chips · Exec hidden 0/0 · Act row never squeezes the ticker)
เทส 371 · Chromium · นาฬิกาปลอม · SAMPLE data only · รัน: python3 run_tests_phase371.py → tests/screenshots/ln4b-*.png"""
import json, sys
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase24 as P24
import run_tests_phase106 as T
import run_tests_phase120 as P120

ENGINE = base.BROWSER_ENGINE
results = []
js, settle = C.js, T.settle
cnt, txt = T.cnt, T.txt
NOW = T.NOW


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def ovf(page): return js(page, "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
def stub(page, code): js(page, "()=>{" + code + "}")
def refresh(page): js(page, "()=>todayRefresh(true)"); settle(page, 350)


def shot(page, name):
    page.wait_for_timeout(900)
    page.screenshot(path=f"screenshots/{name}")   # viewport only


# 23 sectors: 5 lead · 6 weak (fading) · 3 imp fast (Fresh) · 2 lead fast · 7 lag/imp slow
RRG = """window.rrgRowsNow = ()=>{
  const mk=(i,q,ratio,dm,days,prev)=>({sym:'S'+i,quad:q,ratio:ratio,mom:100,dMom:dm,days:days,prevDays:prev,model:RRG_MODEL});
  const R=[]; let i=0;
  for(let k=0;k<5;k++) R.push(mk(i++,'lead',104+k,0.1,30,0));
  for(let k=0;k<6;k++) R.push(mk(i++,'weak',101+k/10,-0.1,10,0));
  for(let k=0;k<3;k++) R.push(mk(i++,'imp',97,0.9,2,0));
  for(let k=0;k<2;k++) R.push(mk(i++,'lead',106+k,0.9,2,0));
  for(let k=0;k<7;k++) R.push(mk(i++,'lag',95,0.1,40,0));
  return R; };
window.tv1SecName = (e)=>'Sector '+e;
const _ss = window.sectorState; window.sectorState = (e)=>e === 'S20' ? {quad:'lag', followed:true} : {quad:null, followed:false};"""


EVS = """const n = Date.now(); wiDocs.D = wiDocs.D || {};
window.wiTier = (a, doc)=>(doc === wiDocs.D ? ({BTCUSD:'MED', USDJPY:'LOW'})[a] || 'HIGH' : null);
window.wiTodayModel = ()=>({todayL:[{id:'m1', doc:'D', ts:n+6*3600000, e:{title:'US PMI Flash'}, assets:['BTCUSD']},{id:'l1', doc:'D', ts:n+2*3600000, e:{title:'JP Low Thing'}, assets:['USDJPY']}], now:n, hasDocs:true});
window.td3NewsModel = ()=>({hasDocs:true, now:n, list:[{id:'e1', ts:n+3*3600000, e:{title:'US Core CPI (Oct)'}, assets:['XAUUSD']},{id:'e2', ts:n+3*3600000, e:{title:'US CPI (Oct)'}, assets:['XAUUSD','BTCUSD']},{id:'e3', ts:n+5*3600000, e:{title:'US PMI'}, assets:['XAUUSD']},{id:'e4', ts:n+7*3600000, e:{title:'FOMC Minutes'}, assets:['XAUUSD']},{id:'e5', ts:n+8*3600000, e:{title:'ECB Speech'}, assets:['XAUUSD']},{id:'e6', ts:null, e:{title:'Fed Chair Speech'}, assets:['XAUUSD']}]});"""


def mac(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h, iso=NOW, picks=(), weekly=False)
    try:
        import run_tests_phase13 as P13
        P24.set_ff(page, P24.ff_json(True, True))
        cards = {
            "ccAM": P24.card("ccAM", "main", "AMD", plan={"entry": 182.5, "stop": 170}, px=170, pxDate="2026-10-01"),
            "ccNV": P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=168, tier="A", lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 168}]),
        }
        js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("tNV", "core", "open", sym="NVDA", entry=171.4, sl=168, qty=10, cur="USD", date="2026-09-10")])
        for cid, c in cards.items():
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
        js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)
        P120.ps_on(page)
        stub(page, RRG)
        stub(page, EVS)
        T.go_today(page)
        js(page, "()=>{ ln4Sel = 'dd'; todayRefresh(true); }"); settle(page, 400)
        fs = js(page, """()=>{ const g = (s)=>{ const e = document.querySelector(s); return e ? parseFloat(getComputedStyle(e).fontSize) : null; };
          return {pill:g('[data-ln4-hotchip]'), go:g('[data-ln4-btn]'), m:g('[data-ln4-det]'), line:g('[data-ln4-hot]'), st:g('[data-ln4-status]') , sc:g('.ln4 .sc'), sw:g('[data-td3-tab="d"]'), ev:g('[data-ln4-ev] .as'), fr:g('[data-ln4-fr]'), tag:g('.ln4 .h small')}; }""")
        check(f"{tag} Mac: pills 12→13.5 · Act detail/button/line 12.5→13.5 · tags ≥ 13.5", fs["pill"] >= 13.5 and fs["go"] >= 13.5 and fs["m"] >= 13.5 and fs["line"] >= 13.5 and fs["sc"] >= 13.5 and fs["sw"] >= 13.5 and fs["tag"] >= 13.5, fs)
        check(f"{tag} Mac: Find row ≥ 14.5", (fs["fr"] or 15) >= 14.5, fs)
        # no new wraps: every Act/Find row keeps its main items on one line (grey detail may wrap)
        rows = js(page, """()=>[...document.querySelectorAll('[data-ln4-row],[data-ln4-fr]')].map(e=>{
          const kids=[...e.children].filter(k=>!k.matches('.m,[data-ln4-det]') && getComputedStyle(k).display!=='none' && k.getBoundingClientRect().height>0);
          const ys=kids.map(k=>{const r=k.getBoundingClientRect(); return r.top+r.height/2;}); const d = ys.length ? Math.max(...ys)-Math.min(...ys) : 0;
          return {s:e.dataset.ln4Row||e.dataset.ln4Fr, d:Math.round(d), w:Math.round(e.getBoundingClientRect().width)}; })""")
        check(f"{tag} Mac: Act/Find row items stay on one line", all(r["d"] <= 14 for r in rows), rows)
        pills = js(page, "()=>[...document.querySelectorAll('.ln4 .pill,.ln4 .sc,.ln4 .st,.ln4 .go,.ln4 .lad')].filter(e=>e.getBoundingClientRect().height>0).map(e=>[Math.round(e.getBoundingClientRect().height), (e.innerText||'').trim().slice(0,16)]).filter(x=>x[0]>40)")
        check(f"{tag} Mac: pills / tags / buttons keep one line", not pills, pills)
        hot = js(page, "()=>({n:+document.querySelector('[data-ln4-hot]').dataset.ln4Hotn, all:+document.querySelector('[data-ln4-hot]').dataset.ln4Hotall, names:[...document.querySelectorAll('[data-ln4-hotchip]')].filter(e=>e.getBoundingClientRect().height>0).map(e=>e.innerText.trim()), ys:new Set([...document.querySelectorAll('[data-ln4-hot] .pill')].filter(e=>e.getBoundingClientRect().height>0).map(e=>Math.round(e.getBoundingClientRect().top/10))).size})")
        check(f"{tag} Mac (LN4c): HOT = ★ + all HOT (≤5), no +N, no duplicates · ONE row", len(hot["names"]) == hot["all"] and hot["names"][0].startswith("★") and len(set(hot["names"])) == hot["all"] and hot["ys"] == 1 and txt(page, ".ln4-hm.md") == "", hot)
        mg = js(page, """()=>{ const c=s=>{const e=document.querySelector(s); return e?getComputedStyle(e).color:null;}; const p=document.createElement('span'); p.className='pill p-r'; document.querySelector('.ln4').appendChild(p); const red=getComputedStyle(p).color; p.className='pill p-g'; const teal=getComputedStyle(p).color; p.remove(); return {u:c('.glx.u'), d:c('.glx.d'), f:c('.glx.f'), red, teal}; }""")
        check(f"{tag} MACRO glyphs: ▲ teal · ▼ red · ▬ grey (per glyph)", mg["u"] == mg["teal"] and mg["d"] == mg["red"] and mg["f"] and mg["f"] not in (mg["u"], mg["d"]), mg)
        stub(page, EVS); refresh(page)
        ev1 = js(page, "()=>({dots:[...document.querySelectorAll('[data-ln4-ev] [data-ln4-impact]')].map(e=>e.dataset.ln4Impact), ys:new Set([...document.querySelectorAll('[data-ln4-ev]')].filter(e=>e.getBoundingClientRect().height>0).map(e=>Math.round(e.getBoundingClientRect().top/10))).size})")
        check(f"{tag} Mac: events carry impact dots (HIGH red / MED amber, LOW hidden) on ONE row", set(ev1["dots"]) == {"HIGH", "MED"} and ev1["ys"] == 1, ev1)
        check(f"{tag} Mac: no horizontal overflow", ovf(page) <= 0, ovf(page))
        # Watch / Core form / Sat form text
        js(page, "()=>{ switchTab('watch'); wlSetView('cand'); td3MetaWrite('AAA', {cand_at:'2026-09-29T03:00:00Z', source:'Volume spike'}); window.wlRowsAll = ()=>({wl:[], cand:['AAA'].map(s=>({sym:s, port:'cand', market:'US', item:null, w:null, d:null, cInfo:[]}))}); renderWatchlist(); }"); settle(page, 500)
        wr = js(page, """()=>[...document.querySelectorAll('[data-ln4w-row]')].map(e=>{ const k=[...e.children].filter(x=>!x.matches('[data-ln4w-acts],[data-tv1-sug],.m')&&x.getBoundingClientRect().height>0); const ys=k.map(x=>x.getBoundingClientRect().top+x.getBoundingClientRect().height/2); return Math.round(Math.max(...ys)-Math.min(...ys)); })""")
        wfs = js(page, "()=>{ const e=document.querySelector('[data-ln4w-row] .age'); return e ? parseFloat(getComputedStyle(e).fontSize) : null; }")
        check(f"{tag} Mac: Watch row single line · age ≥ 13.5", all(x <= 14 for x in wr) and (wfs or 14) >= 13.5, [wr, wfs])
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); settle(page, 400)
        js(page, "()=>coreNewOpen('main',{ticker:'AAA'})"); settle(page, 700)
        P120.fill(page, 100, 90)
        ff = js(page, "()=>{ const e=document.querySelector('.ln1-form label, .ps1Chip, .ps1Frm label'); return e ? parseFloat(getComputedStyle(e).fontSize) : null; }")
        check(f"{tag} Mac: Core form helper/labels ≥ 13.5", (ff or 14) >= 13.5, ff)
        check(f"{tag} Mac: Core form no horizontal overflow", ovf(page) <= 0, ovf(page))
        shot(page, f"ln4b-{w}-core-form.png")
        js(page, "()=>coreSheetClose()")
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid])
        for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)])
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); settle(page, 700)
        sf = js(page, "()=>{ const e=document.querySelector('.ln1-form label'); return e ? parseFloat(getComputedStyle(e).fontSize) : null; }")
        su = js(page, "()=>{ const su=document.querySelector('[data-pf-row=\"3\"]'); if(!su) return 1; return new Set([...su.querySelectorAll('.pf-chip,[data-ln4-all]')].map(e=>Math.round(e.getBoundingClientRect().top/6))).size; }")
        check(f"{tag} Mac: Sat form labels ≥ 13.5 · Setup chips + ✓ all on one row · no overflow", (sf or 14) >= 13.5 and su == 1 and ovf(page) <= 0, [sf, su, ovf(page)])
        shot(page, f"ln4b-{w}-sat-form.png")
        T.go_today(page)
        js(page, "()=>{ ln4Sel = ''; todayRefresh(true); }"); settle(page, 300)
        shot(page, f"ln4b-{w}-today.png")
        check(f"{tag} no console/page errors", not ce and not pe, [ce[:3], pe[:3]])
    finally:
        b.close()


def phone(pw):
    w, h = 390, 844
    tag = f"[{ENGINE}/390]"
    b, page, ce, pe = T.launch(pw, w, h, iso=NOW, picks=(), weekly=False)
    try:
        import run_tests_phase13 as P13
        P24.set_ff(page, P24.ff_json(True, True))
        cards = {
            "ccAM": P24.card("ccAM", "main", "AMD", plan={"entry": 182.5, "stop": 170}, px=170, pxDate="2026-10-01"),
            "ccNV": P24.open_card("ccNV", "tNV", ticker="NVDA", acct="main", qty=10, entry=171.4, sl=168, tier="A", lots=[{"n": 1, "date": "2026-09-10", "px": 171.4, "qty": 10, "f": 1, "stop": 168}]),
        }
        js(page, "(t)=>{ const B=getBook('main'); B.trades=t; saveBook('main'); render(); }", [P13.T("tNV", "core", "open", sym="NVDA", entry=171.4, sl=168, qty=10, cur="USD", date="2026-09-10")])
        for cid, c in cards.items():
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
        js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 700)
        P120.ps_on(page)
        # ── HOT definition ──
        stub(page, RRG)
        H = js(page, "()=>ln4HotSectors()")
        old = js(page, "()=>rrgRowsNow().filter(x=>x.quad==='lead'||x.quad==='weak'||((x.dMom||0)>=0.5)).length")
        hotN = len([x for x in H if x["hot"]])
        check(f"{tag} HOT count on this data = {hotN} of 23 (Leading + Fresh; old rule gave {old}); ★ S20 listed on top", hotN == 10 and old > hotN and H[0]["star"] and all(x["k"] in ("lead", "fresh") for x in H if x["hot"]), [hotN, old])
        order = [x["k"] for x in H]
        lead = [x["ratio"] for x in H if x["k"] == "lead"]
        check(f"{tag} HOT order: ★ first, then Fresh, then Leading by strength; no duplicates", order[0] == "star" and order[1:4] == ["fresh"] * 3 and lead == sorted(lead, reverse=True) and len({x["etf"] for x in H}) == len(H), order)
        stub(page, "window.ftList = ()=>[]; window.sk1Items = ()=>[]; window.ln4Crossed = ()=>false;")
        stub(page, EVS)
        T.go_today(page)
        # ── HOT one row ──
        hot = js(page, """()=>{ const cs=[...document.querySelectorAll('[data-ln4-hotchip]')].filter(e=>e.getBoundingClientRect().height>0);
          const mo=[...document.querySelectorAll('[data-ln4-hotmore]')].filter(e=>e.getBoundingClientRect().height>0);
          const all=[...cs,...mo]; return {chips:cs.length, names:cs.map(e=>e.innerText.trim()), more:mo.map(e=>e.innerText), rows:new Set(all.map(e=>Math.round(e.getBoundingClientRect().top/8))).size, fs:cs.length?parseFloat(getComputedStyle(cs[0]).fontSize):0, right:Math.max(...all.map(e=>e.getBoundingClientRect().right)), hotRight:document.querySelector('[data-ln4-hot]').getBoundingClientRect().right}; }""")
        allnames = js(page, "()=>[...document.querySelectorAll('[data-ln4-hotchip]')].map(e=>e.innerText.trim())")
        check(f"{tag} HOT: ONE row · as many chips as fit, same order (★ first) · +N = the rest · 11.5px", hot["chips"] >= 2 and hot["names"][0].startswith("★") and hot["names"] == allnames[:hot["chips"]] and hot["more"] == [f"+{len(H) - hot['chips']}"] and hot["rows"] == 1 and abs(hot["fs"] - 11.5) < 0.1 and hot["right"] <= hot["hotRight"] + 1, hot)
        page.locator("[data-ln4-hotmore]:visible").click(); settle(page, 300)
        full = js(page, "()=>[...document.querySelectorAll('[data-ln4-hotsheet] [data-ln4-hotchip]')].length")
        check(f"{tag} HOT: '+N' opens the full list (all {len(H)})", full == len(H), full)
        page.locator("[data-ln4-hotsheet] .rd").click(); settle(page, 300)
        # ── TODAY events ──
        ev = js(page, """()=>({lines:[...document.querySelectorAll('[data-ln4-evl]')].map(e=>e.innerText.replace(/\\s+/g,' ')), more:(document.querySelector('[data-ln4-evmore]')||{}).innerText||'', chips:[...document.querySelectorAll('[data-ln4-ev]')].filter(e=>e.getBoundingClientRect().height>0).length,
          cal:(()=>{const c=document.querySelector('[data-td3-cal]').getBoundingClientRect(), k=document.querySelector('[data-ln4-today] .k').getBoundingClientRect(); return Math.abs((c.top+c.height/2)-(k.top+k.height/2));})(),
          oneLine:[...document.querySelectorAll('[data-ln4-evl]')].every(e=>e.getBoundingClientRect().height<=34)})""")
        check(f"{tag} TODAY: ≤ 3 lines, grouped same-time, 'US CPI + Core CPI'-style", len(ev["lines"]) == 3 and ev["lines"][0].endswith("XAUUSD · BTCUSD") is False and "Core CPI (Oct) + CPI (Oct)" in ev["lines"][0] and ev["more"].startswith("+"), ev)
        dots = js(page, "()=>[...document.querySelectorAll('[data-ln4-evl] [data-ln4-impact]')].map(e=>e.dataset.ln4Impact)")
        check(f"{tag} TODAY: impact dots on lines (HIGH red / MED amber), LOW hidden", dots and set(dots) <= {"HIGH", "MED"}, dots)
        check(f"{tag} TODAY: old chips hidden · lines one-line · Calendar › link on the TODAY label line", ev["chips"] == 0 and ev["oneLine"] and ev["cal"] < 14, ev)
        page.locator("[data-ln4-evmore]").click(); settle(page, 300)
        ev2 = js(page, "()=>[...document.querySelectorAll('[data-ln4-evl]')].map(e=>e.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} TODAY: unknown time → 'time tbc' at the end", "time tbc" in ev2[-1], ev2)
        page.locator("[data-ln4-evmore]").click(); settle(page, 300)
        # ── To do grouped + Exec hidden ──
        stub(page, "window.ftList = ()=>[]; window.sk1Items = ()=>[{id:'lt:A',skill:'living-thesis',sym:'A',age:35,full:'living-thesis: A 35d'},{id:'lt:B',skill:'living-thesis',sym:'B',age:40,full:'living-thesis: B 40d'},{id:'lt+',more:true,full:'+5',short:'+5'},{id:'wi',skill:'weekly-impact',full:'weekly-impact (last day today)'}];")
        refresh(page)
        td = js(page, "()=>[...document.querySelectorAll('[data-ln4-todo]')].map(e=>e.innerText)")
        check(f"{tag} To do: 7 living-thesis → ONE chip 'living-thesis · 7 stocks ›'", any("living-thesis · 7 stocks" in t for t in td) and sum("living-thesis" in t for t in td) == 1, td)
        check(f"{tag} To do: Exec hidden at 0/0", cnt(page, "[data-ln4-exec]") == 0 or "0/0" not in txt(page, "[data-ln4-exec]"), cnt(page, "[data-ln4-exec]"))
        page.locator('[data-ln4-todogrp="lt"]').click(); settle(page, 300)
        check(f"{tag} To do: tapping the group opens its list", cnt(page, '[data-ln4-todolist="lt"] [data-ln4-todo]') >= 2, cnt(page, "[data-ln4-todolist]"))
        page.locator('[data-ln4-todogrp="lt"]').click(); settle(page, 300)
        # ── Act row: ticker never squeezed ──
        stub(page, """window.ln4SatRows = ()=>[{kind:'sat', sym:'Brent', key:'BRENT', id:'x1', state:'draft', status:'Draft', counter:true, macro:'Macro: Hawkish USD',
            bad:{why:'Entry is beyond the trigger — the plan is no longer valid, fix it', btn:'Fix ›', k:'plan'}, det:'Entry 82.4 · SL 80.9 · 4h', btn:{t:'Fix ›', fn:'void 0', fx:true}}];""")
        refresh(page)
        r = js(page, """()=>{ const e=document.querySelector('[data-ln4-row="Brent"]'); const b=e.querySelector('b').getBoundingClientRect(); const rg=document.createRange(); rg.selectNodeContents(e.querySelector('b'));
          const lines=new Set([...rg.getClientRects()].map(x=>Math.round(x.top))).size; const tag=e.querySelector('.sc.sat').getBoundingClientRect(); const why=e.querySelector('[data-ln4-why]').getBoundingClientRect(); const det=e.querySelector('[data-ln4-det]').getBoundingClientRect();
          return {lines, bh:Math.round(b.height), tagSame:Math.abs((tag.top+tag.height/2)-(b.top+b.height/2))<10, whyBelow:why.top>=b.bottom-2, detBelow:det.top>=why.bottom-2, bw:Math.round(b.width), ov:b.right<=e.getBoundingClientRect().right}; }""")
        check(f"{tag} Act: 'Brent' on ONE line with a long red reason + 3 tags; tag on line 1, reason on line 2, details on line 3", r["lines"] == 1 and r["tagSame"] and r["whyBelow"] and r["detBelow"] and r["bh"] < 26, r)
        stub(page, "window.ln4SatRows = ()=>[{kind:'sat', sym:'Brent', key:'BRENT', id:'x1', state:'draft', status:'Draft', det:'Entry 82.4', btn:{t:'Fix ›', fn:'void 0'}, bad:null}];")
        stub(page, "delete window.ln4SatRows;")
        refresh(page)
        # ── first viewport ──
        fv = js(page, "()=>{ const a=document.querySelector('[data-ln4-act] .h').getBoundingClientRect(); const s=document.querySelector('[data-ln4-status]').getBoundingClientRect(); const hot=document.querySelector('[data-ln4-hot]').getBoundingClientRect(); const sw=document.querySelector('[data-td3-sw]').getBoundingClientRect(); return {actBottom:Math.round(a.bottom), vh:innerHeight, statusTop:Math.round(s.top), hotTop:Math.round(hot.top), swTop:Math.round(sw.top), swBottom:Math.round(sw.bottom)}; }")
        check(f"{tag} first viewport (844) contains the Act header", fv["actBottom"] <= 844 - 70, fv)
        sr = js(page, "()=>{ const q=s=>document.querySelector(s).getBoundingClientRect(); const a=q('[data-ln4-risk]'), b=q('[data-td3-sw]'), h=q('[data-ln4-hot]'); return {riskSwSameRow:Math.abs((a.top+a.height/2)-(b.top+b.height/2))<12, swRight:b.right, hotGap:Math.round(h.top-Math.max(a.bottom,b.bottom))}; }")
        rg = js(page, "()=>{ const q=s=>document.querySelector(s).getBoundingClientRect(); const a=q('[data-ln4-risk]'), g=q('.ln4-status .td3-rg, .ln4-status .r > *'); return Math.abs((a.top+a.height/2)-(g.top+g.height/2)); }")
        check(f"{tag} status: Risk line sits beside the regime (line 1), switch right/under it, no empty row above HOT", rg < 14 and sr["hotGap"] < 24, [rg, sr])
        check(f"{tag} no horizontal overflow", ovf(page) <= 0, ovf(page))
        shot(page, "ln4b-390-today.png")
        check(f"{tag} no console/page errors", not ce and not pe, [ce[:3], pe[:3]])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for fn, a in ((mac, (1280, 800)), (mac, (1440, 900)), (phone, ())):
            try: fn(pw, *a)
            except Exception as e:
                import traceback; traceback.print_exc(); check("crashed", False, str(e)[:300])
    n = sum(1 for r in results if r[1])
    print(f"\n{n}/{len(results)} PASS")
    sys.exit(0 if n == len(results) else 1)
