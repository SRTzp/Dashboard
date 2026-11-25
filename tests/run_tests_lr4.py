#!/usr/bin/env python3
"""LR4 — Flow tab: RRG tail end-point = current ratio/mom (same rrgCompute path) · Daily/Weekly toggle · empty states (no Weekly Impact / no RRG / no events) · calendar + macro tabs · no Thai in #tabFlow · no overflow at 360/390/1440.
Run: python3 tests/run_tests_lr4.py"""
import re, sys
from playwright.sync_api import sync_playwright
import net_stub
from re1d_common import js, check, results
import lr4_common as C

TAIL_JS = """()=>{
  const mk = (n, f)=>{ const c = [], b = []; let x = 100, y = 100; for(let i = 0; i < n; i++){ y *= 1 + 0.002 * Math.sin(i / 7); x *= 1 + f(i); c.push(x); b.push(y); } return {c, b}; };
  const out = {};
  [['up', i=>0.004 * Math.sin(i / 9) + 0.0015], ['wavy', i=>0.012 * Math.sin(i / 5)], ['down', i=>-0.002 + 0.003 * Math.cos(i / 11)]].forEach(([k, f])=>{
    const s = mk(1500, f), d = rrgCompute(s.c, s.c, s.b, 'D'), w = rrgCompute(s.c.filter((_, i)=>i % 5 === 4), s.c.filter((_, i)=>i % 5 === 4), s.b.filter((_, i)=>i % 5 === 4), 'W');
    const T = r=>{ const F = r.tailF; return {n:F && F.length / 2, ok: !!F && F[F.length - 2] === r.ratio && F[F.length - 1] === r.mom, err:r.err}; };   /* HF6: flat tailF */
    out[k] = {d:T(d), w:T(w)};
  });
  return out; }"""

THAI = """()=>{ const out = []; const w = document.createTreeWalker(document.getElementById('tabFlow'), NodeFilter.SHOW_TEXT); let n; while(n = w.nextNode()){ if(/[\\u0E00-\\u0E7F]/.test(n.nodeValue)) out.push(n.nodeValue.trim().slice(0, 60)); }
  document.querySelectorAll('#tabFlow [title],#tabFlow [aria-label],#tabFlow [placeholder]').forEach(e=>['title', 'aria-label', 'placeholder'].forEach(a=>{ const v = e.getAttribute(a); if(v && /[\\u0E00-\\u0E7F]/.test(v)) out.push('@' + a + ' ' + v.slice(0, 60)); })); return out; }"""


def run(pw, w, h):
    tag = "[%s]" % w
    rows = C.mock_sectors()
    b, page, pe = C.open_flow(pw, w, h)
    try:
        ov = lambda: js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        # --- tail = same formula
        t = js(page, TAIL_JS)
        check(f"{tag} B: rrgCompute adds a 5-point tail whose last pair equals ratio / mom exactly (D + W, 3 series)", all(v[k]["n"] == 5 and v[k]["ok"] for v in t.values() for k in ("d", "w")), t)
        ends = js(page, "()=>[...document.querySelectorAll('[data-lr4-sec]')].map(g=>({s:g.dataset.lr4Sec, e:g.dataset.lr4End, n:+g.dataset.lr4N}))")
        want = {r["sym"]: f'{r["ratio"]},{r["mom"]}' for r in rows}
        check(f"{tag} B: chart draws one tail per sector, end-point = row ratio / mom (16 sectors, 5 points)", len(ends) == 16 and all(want[x["s"]] == x["e"] and x["n"] == 5 for x in ends), ends[:3])
        # --- tail fix: build 9, IRBO gone, every dot labelled
        lb = js(page, "()=>({b:RRG_BUILD, irbo:document.getElementById('tabFlow').innerHTML.includes('IRBO'), dots:[...document.querySelectorAll('[data-lr4-sec]')].map(g=>({s:g.dataset.lr4Sec, lbl:!!document.querySelector('[data-lr4-lbl=\"'+g.dataset.lr4Sec+'\"]'), title:!!g.querySelector('title')}))})")
        check(f"{tag} tail: RRG_BUILD is 9 · nothing draws IRBO", lb["b"] == 9 and not lb["irbo"], [lb["b"], lb["irbo"]])
        check(f"{tag} tail: every dot has a visible label or a hover title", len(lb["dots"]) == 16 and all(d["lbl"] or d["title"] for d in lb["dots"]), [d for d in lb["dots"] if not (d["lbl"] or d["title"])])
        mg = js(page, "()=>{ const f = ffState(); f.rrg.build = 8; f.rrg.day = 'x'; f.rrg.rowsD = [{sym:'IRBO'}, {sym:'ROBO'}, {sym:'SMH'}].concat(f.rrg.rowsD.slice(0,0)); f.rrg.rowsW = [{sym:'IRBO'}]; ffMigrateRrg && 0; return null; }") if False else None
        # --- glance / header
        hd = js(page, "()=>({wk:(document.querySelector('[data-lr4-week]')||{}).innerText, same:(document.querySelector('[data-lr4-same]')||{}).innerText, imp:!!document.querySelector('[data-lr4-import]')})")
        check(f"{tag} A: header = 'Flow' + week range; desktop says 'Same in Main and Family'; Import JSON exists", hd["imp"] and ("17–21 Nov" in hd["wk"]) and (w <= 600 or hd["same"] == "Same in Main and Family"), hd)
        g = js(page, "()=>({mood:(document.querySelector('[data-lr4-mood]')||{}).innerText||'', why:(document.querySelector('[data-lr4-card=\"why\"]')||{}).innerText||'', news:[...document.querySelectorAll('[data-lr4-next]')].length, nl:(document.querySelector('[data-lr4-nextline]')||{}).innerText||''})")
        check(f"{tag} A: mood = Risk-off + 60%; why shows Equity / Credit red + days (desktop); next news lists the coming events", "Risk-off" in g["mood"] and "60%" in g["mood"] and (w <= 600 or ("32d" in g["why"] and "24d" in g["why"])) and (g["news"] >= 2 if w > 600 else "CPI" in g["nl"]), g)
        tl = js(page, "()=>[...document.querySelectorAll('[data-lr4-tile]')].map(t=>({k:t.dataset.lr4Tile, t:t.innerText.replace(/\\s+/g,' ').slice(0,60), h:Math.round(t.getBoundingClientRect().height)}))")
        check(f"{tag} A: one tile per Weekly Impact asset, impact order (XAU HIGH first)", len(tl) >= 4 and tl[0]["k"] == "XAUUSD" and "HIGH" in tl[0]["t"] and "Bull" in tl[0]["t"], tl)
        nw = js(page, "()=>[...document.querySelectorAll('[data-lr4-tile] .r2')].every(e=>innerWidth <= 760 ? getComputedStyle(e).whiteSpace === 'normal' : getComputedStyle(e).whiteSpace === 'nowrap' && getComputedStyle(e).textOverflow === 'ellipsis')")   # PH1: phone wraps to 2 lines
        check(f"{tag} A: tile reason = one line (nowrap + ellipsis); phone ≤760 wraps (PH1)", nw)
        js(page, "()=>document.querySelector('[data-lr4-tile=\"XAUUSD\"]').click()"); page.wait_for_timeout(250)
        check(f"{tag} A: tapping a tile opens the existing Weekly Impact detail panel", js(page, "()=>!!document.querySelector('[data-pv-panel]')"))
        js(page, "()=>document.querySelector('[data-lr4-tile=\"XAUUSD\"]').click()"); page.wait_for_timeout(150)
        # --- Daily / Weekly toggle
        w2 = [dict(r, tailF=[v + (0.5 if i % 2 == 0 else 0) for i, v in enumerate(r["tailF"])], ratio=r["ratio"] + 0.5) for r in rows[:6]]
        js(page, "(r)=>{ const f = ffState(); f.rrg.rowsW = r.map(x=>Object.assign({model:RRG_MODEL}, x)); bdFlowTopRender(); }", w2)
        cap_d = js(page, "()=>(document.querySelector('.lr4-fig figcaption')||{innerText:''}).innerText")
        n_d = js(page, "()=>document.querySelectorAll('[data-lr4-sec]').length")
        js(page, "()=>[...document.querySelectorAll('[data-bd-rrgtf] button')].find(b=>/^(W|Weekly)$/.test(b.innerText.trim())).click()"); page.wait_for_timeout(300)
        n_w = js(page, "()=>document.querySelectorAll('[data-lr4-sec]').length"); tf = js(page, "()=>rrgTf()")
        cap_w = js(page, "()=>(document.querySelector('.lr4-fig figcaption')||{innerText:''}).innerText")
        check(f"{tag} B: Weekly toggle switches the rows (16 → 6) and the tail note ('last 5 days' → 'last 5 weeks')", tf == "W" and n_d == 16 and n_w == 6 and (w <= 600 or ("5 days" in cap_d and "5 weeks" in cap_w)), [tf, n_d, n_w, cap_d, cap_w])
        js(page, "()=>rrgSetTf('D')"); page.wait_for_timeout(200)
        # --- row without a tail = dot only
        js(page, "()=>{ const f = ffState(); delete f.rrg.rowsD[0].tail; delete f.rrg.rowsD[0].tailF; bdFlowTopRender(); }")
        dot = js(page, "(s)=>{ const g = document.querySelector('[data-lr4-sec=\"'+s+'\"]'); return g ? [g.querySelectorAll('polyline').length, g.querySelectorAll('circle').length] : null; }", rows[0]["sym"])
        check(f"{tag} B: a cached row without a tail draws the dot only", dot == [0, 1], dot)
        # --- speed list (desktop) + phone arrows
        if w > 600:
            sp = js(page, "()=>({g:[...document.querySelectorAll('[data-lr4-grp]')].map(x=>x.dataset.lr4Grp), rest:(document.querySelector('[data-lr4-rest] summary')||{}).innerText||'', chips:[...document.querySelectorAll('.lr4-speed .sp2')].map(x=>x.innerText)})")
            check(f"{tag} B: speed list = Leading / Improving / Lagging + collapsed 'Weakening (n)'", sp["g"] == ["lead", "imp", "lag"] and sp["rest"].startswith("Weakening (6)") and any("speeding up" in c for c in sp["chips"]) and any("1d · new" in c for c in sp["chips"]), sp)
        else:
            ar = js(page, "()=>(document.querySelector('.lr4-arrows')||{innerText:''}).innerText")
            check(f"{tag} B: phone RRG card has the arrow lines (↗ leaders · ⤴ improving · ↘ laggards)", "↗" in ar and "⤴" in ar and "↘" in ar, ar)
        js(page, "()=>document.querySelector('[data-lr4-allsec]').click()"); page.wait_for_timeout(300)
        op = js(page, "()=>({det:document.getElementById('lr4Det').open, row:document.querySelector('[data-bd-row=\"rrg\"]').open})")
        check(f"{tag} C: 'All 23 sectors ›' opens Details › RRG details (current list)", op["det"] and op["row"], op)
        js(page, "()=>{ document.getElementById('lr4Det').open = false; }")
        # --- LR4 last pass: header = ONE row, ONE week picker · tooltip clear · every tile has a reason line
        hr = js(page, "()=>{ const h=document.querySelector('[data-lr4-head]'), k=[...h.children].filter(e=>e.getClientRects().length).map(e=>e.getBoundingClientRect()); const sel=document.querySelectorAll('#tabFlow [data-bd-wk]'); const o=sel[0]?sel[0].selectedOptions[0].textContent:''; return {n:sel.length, inHead:!!(sel[0]&&h.contains(sel[0])), tops:k.map(r=>Math.round(r.top+r.height/2)), hh:Math.round(h.getBoundingClientRect().height), opt:o, add:document.querySelectorAll('#tabFlow [data-bd-addasset]').length, tip:document.querySelectorAll('[data-tw1-tip]').length, miss:[...document.querySelectorAll('[data-bd-mc]')].filter(e=>!(e.querySelector('[data-bd-reason]')||{innerText:''}).innerText.trim()).length}; }")
        check(f"{tag} 6: Flow header is ONE row (all items share a centre line, height < 64)", max(hr["tops"]) - min(hr["tops"]) <= 12 and hr["hh"] < 64, hr)
        check(f"{tag} 6: exactly one week picker in #tabFlow, inside the header; text '{'' if w <= 600 else 'Week '}17–21 Nov'", hr["n"] == 1 and hr["inHead"] and hr["opt"] == (("" if w <= 600 else "Week ") + "17–21 Nov"), hr)
        check(f"{tag} 2/4: no name tooltip on load · every asset tile has a reason line (No catalyst when empty)", hr["tip"] == 0 and hr["miss"] == 0, hr)
        # --- calendar + macro
        mq = js(page, "()=>({chip:[...document.querySelectorAll('[data-lr4-qmiss]')].map(c=>c.innerText.trim()), det:document.getElementById('lr4Det').open})")
        check(f"{tag} C: 'Q4 missing' chip when there is no playbook · Details closed by default", any("Q4 missing" in c for c in mq["chip"]) and not mq["det"], mq)
        if w > 600:
            gr = js(page, "()=>({days:[...document.querySelectorAll('[data-lr4-day]')].map(d=>d.innerText.replace(/\\s+/g,' ')), n:+document.querySelector('[data-lr4-wkgrid]').dataset.lr4Evn})")
            check(f"{tag} C: calendar = Mon–Fri grid with chips (time · name · tier)", len(gr["days"]) == 5 and gr["n"] == 5 and "20:30 US CPI · HIGH" in gr["days"][3] and "21:30 EIA crude · MED" in gr["days"][2], gr)
            js(page, "()=>lr4CalTab('macro')"); page.wait_for_timeout(200)
            mv = js(page, "()=>({pb:document.getElementById('pbPanel').getClientRects().length > 0, grid:document.getElementById('lr4CalGrid').getClientRects().length > 0})")
            check(f"{tag} C: Macro quarter tab shows #pbPanel and hides the grid", mv["pb"] and not mv["grid"], mv)
            mt = js(page, "()=>{ const p=document.getElementById('pbPanel'); return {t:p.innerText.replace(/\\s+/g,' ').trim(), nb:p.querySelectorAll('.bd-nb').length, ttl:p.querySelectorAll('.bd-sh b').length}; }")
            check(f"{tag} 1: Macro tab English only ('No playbook yet · Paste JSON'), no numbered '5' header, no inner card title", "No playbook yet" in mt["t"] and "Paste JSON" in mt["t"] and mt["nb"] == 0 and mt["ttl"] == 0 and not re.search("[\u0E00-\u0E7F]", mt["t"]), mt)
            js(page, "()=>lr4CalTab('cal')")
            js(page, "()=>{ switchTab('today'); td3GoCal(); }"); page.wait_for_timeout(400)
            check(f"{tag} C: Today's 'US calendar ↗' (td3GoCal) lands on the Flow calendar card", js(page, "()=>activeTab === 'flow' && (()=>{ const r = document.getElementById('lr4Cal').getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0; })()"))
        else:
            js(page, "()=>document.querySelector('[data-lr4-calrow]').click()"); page.wait_for_timeout(300)
            sh = js(page, "()=>({sheet:!!document.querySelector('[data-lr4-sheet]'), days:document.querySelectorAll('.lr4-sheet [data-lr4-day]').length, txt:(document.querySelector('[data-lr4-sheet]')||{innerText:''}).innerText})")
            check(f"{tag} C: phone 'Economic calendar · 5 this week ›' opens the calendar as a sheet", sh["sheet"] and sh["days"] == 5 and "CPI" in sh["txt"], sh)
            sx = js(page, "()=>{ const x=document.querySelector('[data-lr4-sheetx]').getBoundingClientRect(), h=document.querySelector('.lr4-sheet .hd').getBoundingClientRect(), l=document.querySelector('.lr4-sheet .lr4-inv-s'); return {w:Math.round(x.width), h:Math.round(x.height), right:Math.round(h.right-x.right), link:!!l && l.getBoundingClientRect().top < h.bottom, fs:l?parseFloat(getComputedStyle(l).fontSize):0}; }")
            check(f"{tag} 3: phone sheet has a 44px x close at top right and a small 'Investing.com ↗' link in the header line", sx["w"] >= 44 and sx["h"] >= 44 and sx["right"] <= 16 and sx["link"] and sx["fs"] <= 12, sx)
            js(page, "()=>document.querySelector('[data-lr4-sheetx]').click()"); page.wait_for_timeout(200)
            js(page, "()=>document.querySelector('[data-lr4-macrow]').click()"); page.wait_for_timeout(200)
            check(f"{tag} C: phone 'Macro quarter ›' row reveals the playbook panel", js(page, "()=>document.getElementById('pbPanel').getClientRects().length > 0"))
        # --- no Thai
        js(page, "()=>{ switchTab('flow'); document.querySelectorAll('#tabFlow details').forEach(d=>d.open = true); try{ ffRenderRegime(); ffRenderThemes(); }catch(e){} }"); page.wait_for_timeout(300)
        th = js(page, THAI)
        check(f"{tag} C: no Thai characters in #tabFlow (Details open)", not th, th[:8])
        check(f"{tag} no horizontal overflow", ov() <= 0, ov())
        # --- empty states
        js(page, "()=>{ wiDocs = {}; const f = ffState(); f.rrg = {rowsD:[], rowsW:[]}; rrgLastGood = {D:null, W:null}; newsEvents = ()=>[]; bdFlowTopRender(); }"); page.wait_for_timeout(300)
        es = js(page, "()=>({tiles:[...document.querySelectorAll('[data-lr4-tile]')].map(t=>t.innerText.replace(/\\s+/g,' ')), rrg:(document.querySelector('[data-lr4-rrgempty]')||{innerText:''}).innerText, evn:+document.querySelector('[data-lr4-wkgrid]').dataset.lr4Evn, news:(document.querySelector('[data-lr4-card=\"news\"]')||{innerText:''}).innerText})")
        check(f"{tag} E: no Weekly Impact → tiles say 'No Weekly Impact · Add ›'", es["tiles"] and all("No Weekly Impact · Add ›" in x for x in es["tiles"]), es["tiles"][:2])
        check(f"{tag} E: no RRG → 'No RRG data yet' + 'All 23 sectors ›'", "No RRG data yet" in es["rrg"] and "All 23 sectors" in es["rrg"], es["rrg"])
        check(f"{tag} E: no events → empty calendar grid (0) and the news card says so (phone: no Next line)", es["evn"] == 0 and (w <= 600 or "No HIGH / MED news" in es["news"]), es)
        check(f"{tag} no overflow in the empty state · no page errors", ov() <= 0 and not pe, [ov(), pe])
    finally:
        b.close()


if __name__ == "__main__":
    with sync_playwright() as pw:
        for w, h in ((1440, 900), (390, 844), (360, 780)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nSUMMARY LR4: {len(results) - len(bad)}/{len(results)} pass")
    sys.exit(1 if bad else 0)
