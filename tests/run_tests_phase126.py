#!/usr/bin/env python3
"""PS1c — plan form redesign (own port switch · per-port drafts · split % · 2-column rows · summary/port line) · Core|Sat top bar
· Sat form alignment · Today homework (one row, Plans badge) · เทส 126 · Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน"""
import json, re
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase111 as P111
import run_tests_phase120 as P
import run_tests_phase121 as X

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = T.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def run(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    # ── 1 Port switch: only source of the port · per-port drafts · title/chip/regime follow ──
    b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
    try:
        P.ps_on(page)
        # a Watchlist item that says Momentum: typing must never reset the port
        T.wl_seed(page, [T.W("AVGO", ladder_watch=False)])
        P.form(page, "AVGO")
        st = lambda: js(page, """()=>({track:coreNew.track, on:[...document.querySelectorAll('[data-ps1-seg] button.on')].map(x=>x.dataset.ps1Port), title:document.querySelector('[data-ps1-title]').firstChild.textContent,
            risk:document.getElementById('cnRisk').value, scope:planScope, note:document.getElementById('cnWlNote').textContent, coreOn:document.getElementById('scopeCore').classList.contains('on')})""")
        s0 = st()
        check(f"{tag} 1 starts as the Watchlist port (Momentum) · title 'New plan' · switch shows Momentum", s0["track"] == "winner" and s0["on"] == ["winner"] and s0["title"] == "New plan", s0)
        # type a draft for Momentum
        P.fill(page, 100, 90)
        js(page, "()=>coreFormPort('ladder')"); settle(page, 200)
        s1 = st()
        e1 = js(page, "()=>[document.getElementById('cnEntry').value, document.getElementById('cnStop').value]")
        check(f"{tag} 1 switch → Compounder: port, switch, top scope, risk default (1) follow · typed Momentum values are NOT carried over", s1["track"] == "ladder" and s1["on"] == ["ladder"] and s1["scope"] == "ladder" and s1["risk"] == "1" and e1 == ["", ""], [s1, e1])
        check(f"{tag} 1 muted note: Watchlist track Momentum (unchanged)", s1["note"] == "Watchlist track: Momentum (unchanged)", s1["note"])
        P.fill(page, 50, 40)
        js(page, "()=>{ document.getElementById('cnTicker').value='AVGO'; coreNewIn(); }"); settle(page, 150)   # keystrokes never reset the port
        check(f"{tag} 1 typing in the form does not reset the port", st()["track"] == "ladder", st())
        ok = True; seen = []
        for i in range(5):
            p = "winner" if i % 2 == 0 else "ladder"
            js(page, "([p])=>coreFormPort(p)", [p]); settle(page, 120)
            s = st(); chip = js(page, "()=>document.getElementById('cnRiskHint').innerText")
            seen.append([p, s["track"], s["on"], s["risk"], js(page, "()=>[document.getElementById('cnEntry').value,document.getElementById('cnStop').value]")])
            ok = ok and s["track"] == p and s["on"] == [p] and s["scope"] == ("stock" if p == "winner" else "ladder")
        check(f"{tag} 1 switch 5 times: port, switch, scope always agree", ok, seen)
        # drafts restore: last switch was winner (i=4) → Momentum draft 100/90, Compounder draft 50/40
        e_w = seen[-1][4]; e_l = seen[-2][4]
        check(f"{tag} 1 each port keeps its OWN draft (Momentum 100/90 · Compounder 50/40)", e_w == ["100", "90"] and e_l == ["50", "40"], seen)
        # top scope switch drives the form too
        js(page, "()=>setPlanScope('ladder')"); settle(page, 200)
        check(f"{tag} 1 top switch (Core port) → form follows", st()["track"] == "ladder" and st()["on"] == ["ladder"], st())
        # rules follow the port: Momentum range 0.35–0.50 vs Compounder 0.80–1.25
        P.fill(page, 100, 90, 0.4)
        er = js(page, "()=>{ const e=document.getElementById('cnErr'); return e.style.display==='none' ? '' : e.innerText; }")
        check(f"{tag} 1 Compounder form rejects Momentum risk 0.4 (range 0.8–1.25)", "0.8" in er, er)
        js(page, "()=>coreFormPort('winner')"); settle(page, 150)
        check(f"{tag} 1 Momentum: its own draft is back (risk default 0.4)", js(page, "()=>document.getElementById('cnRisk').value") == "0.4", "")
        # save: card has the plan's port · Watchlist unchanged
        js(page, "()=>coreFormPort('ladder')"); settle(page, 150); P.fill(page, 100, 85, 1)
        js(page, "()=>coreNewSave()"); settle(page, 700)
        c = js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='AVGO'); const w=wlItems.find(x=>x.ticker==='AVGO'); return c && {track:c.track, wl:w.ladder_watch}; }")
        check(f"{tag} 1 save: card track = Compounder · Watchlist track unchanged", c and c["track"] == "ladder" and c["wl"] is False, c)
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 2 Layout: single row · 2 columns after ＋ · equal row width · split % ──
    b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
    try:
        P.ps_on(page); P.form(page, "NVDA"); P.fill(page, 100, 95)
        lay = lambda: js(page, """()=>{ const r=id=>document.getElementById(id).getBoundingClientRect(); const a=r('cnEntry'),s=r('cnStop'),k=r('cnRisk');
          return {top:[a.top,s.top,k.top], left:[a.left,s.left,k.left], ov:document.documentElement.scrollWidth>innerWidth}}""")
        l0 = lay()
        check(f"{tag} 2 single trade: Entry · SL · Risk on ONE row", abs(l0["top"][0] - l0["top"][1]) < 1 and abs(l0["top"][1] - l0["top"][2]) < 1 and l0["left"][0] < l0["left"][1] < l0["left"][2] and not l0["ov"], l0)
        sm0 = P.sumtxt(page)
        check(f"{tag} 2 summary '#N · x% · Risk ฿k (y%)'", sm0.startswith("#") and "Risk ฿" in sm0 and "% of" not in sm0.split("Risk")[0], sm0)
        ln = js(page, "()=>{ const p=document.getElementById('cnPortLn'); const s=document.getElementById('cnSum'); return {vis:p.style.display!=='none', t:p.innerText.replace(/\\s+/g,' '), below:p.getBoundingClientRect().top >= s.getBoundingClientRect().bottom - 1, fs:parseFloat(getComputedStyle(p).fontSize), col:getComputedStyle(p).color}}")
        check(f"{tag} 2 port line always visible under the summary: 'x% of MMT · cap 7.5% (y% of MMT) · Details ›' · ~11.5px light grey", ln["vis"] and ln["below"] and re.search(r"^[\d.]+% of MMT · cap 7\.5% \([\d.]+% of MMT\) Details ›$", ln["t"]) and "Details" in ln["t"] and 11 <= ln["fs"] <= 12 and ln["col"] == "rgb(163, 168, 176)", ln)
        js(page, "()=>{ ps1RowAdd('e'); ps1RowAdd('s'); }"); settle(page, 200)
        js(page, "()=>{ document.getElementById('cnEn1').value='98'; ps1In('e',1,'98'); document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); }"); settle(page, 200)
        wd = js(page, """()=>{ const w=sel=>[...document.querySelectorAll(sel)].map(i=>Math.round(i.closest('.ps1R').getBoundingClientRect().width*10)/10);
          const px=sel=>[...document.querySelectorAll(sel)].map(i=>Math.round(i.getBoundingClientRect().width));
          const g=document.getElementById('cnGrid'); const e=document.getElementById('cnEBox').getBoundingClientRect(), s=document.getElementById('cnSBox').getBoundingClientRect(), r=document.getElementById('cnRisk').getBoundingClientRect();
          return {e:w('#cnEntry,#cnEn1'), s:w('#cnStop,#cnSt1'), epx:px('#cnEntry,#cnEn1'), spx:px('#cnStop,#cnSt1'), multi:g.classList.contains('multi'), sideBySide:Math.abs(e.top-s.top)<1 && e.left<s.left, riskAbove:r.bottom<=e.top+1, ov:document.documentElement.scrollWidth>innerWidth,
            splits:[document.getElementById('cnEr0').value,document.getElementById('cnEr1').value], outs:[document.getElementById('cnSp0').value,document.getElementById('cnSp1').value],
            lbl:[document.getElementById('cnEh').innerText,document.getElementById('cnSh').innerText,document.getElementById('cnRiskLbl').innerText], metas:[...document.querySelectorAll('[data-ps1-meta]')].map(m=>m.innerText.trim())}}""")
        check(f"{tag} 2 after ＋: Entry·split | SL·out side by side under 'Risk per idea' · no overflow", wd["multi"] and wd["sideBySide"] and wd["riskAbove"] and not wd["ov"] and wd["lbl"] == ["Entry · split", "SL · out", "Risk per idea"], wd)
        check(f"{tag} 2 row 1 is exactly as wide as row 2 (Entry & SL) · price box ≥ 70px", len(set(wd["e"])) == 1 and len(set(wd["s"])) == 1 and min(wd["epx"] + wd["spx"]) >= 70, wd)
        check(f"{tag} 2 splits default 50/50 · each row's result under its own box (entries '#N · x%', SL '−x%')", wd["splits"] == ["50", "50"] and wd["outs"] == ["50", "50"] and wd["metas"][0].startswith("#") and wd["metas"][1].startswith("#") and wd["metas"][2].startswith("−") and "%" in wd["metas"][1], wd)
        # split total
        js(page, "()=>{ document.getElementById('cnEr0').value='60'; ps1In('er',0,'60'); }"); settle(page, 150)
        check(f"{tag} 2 split 60+50 → one-line error · Save blocked", P.save_dis(page) and "Entry split must total 100%" in P.errtxt(page), P.errtxt(page))
        js(page, "()=>{ document.getElementById('cnEr0').value='60'; ps1In('er',0,'60'); document.getElementById('cnEr1').value='40'; ps1In('er',1,'40'); }"); settle(page, 150)
        s_a = js(page, "()=>[...document.querySelectorAll('[data-ps1-meta]')].slice(0,2).map(m=>parseInt(m.innerText.replace('#','')))")
        # same maths as PS1b: shares = floor(idea risk × reg × split ÷ per-share risk to blended SL)
        e = P.E(page); fx = js(page, "()=>getBook('main').settings.fx")
        F = js(page, "()=>coreCtx('main').F.f"); idea = 0.4 * F
        bl = 0.5 * 95 + 0.5 * 85
        exp = [int(e / fx * idea / 100 * sp / (px - bl)) for sp, px in ((0.6, 100), (0.4, 98))]
        check(f"{tag} 2 shares match the PS1b maths for the same inputs (split 60/40) {exp}", s_a == exp and not P.save_dis(page), [s_a, exp, P.errtxt(page)])
        # risk change updates the rows automatically (no row stores absolute risk)
        P.fill(page, r=0.5); s_b = js(page, "()=>[...document.querySelectorAll('[data-ps1-meta]')].slice(0,2).map(m=>parseInt(m.innerText.replace('#','')))")
        check(f"{tag} 2 changing 'Risk per idea' updates all rows automatically", s_b[0] > s_a[0], [s_a, s_b])
        # pill beside risk per idea
        js(page, "()=>{ const o=coreCtxTrack; window.coreCtxTrack=(cx,t)=>{ const r=o(cx,t); r.F=Object.assign({}, r.F, {f:0.5}); return r; }; coreNewIn(); }"); settle(page, 200)
        pill = js(page, "()=>{ const p=document.getElementById('cnRegPill'); return {vis:p.style.display!=='none', t:p.innerText}}")
        check(f"{tag} 2 regime pill beside 'Risk per idea' ('× regime 50% → 0.25%')", pill["vis"] and "× regime" in pill["t"] and "→" in pill["t"], pill)
        # row count change resets splits to even 34/33/33
        js(page, "()=>ps1RowAdd('e')"); settle(page, 150)
        sp3 = js(page, "()=>[...document.querySelectorAll('input[id^=cnEr]')].map(i=>i.value)")
        check(f"{tag} 2 3 rows → 34/33/33 (adding a row resets to even)", sp3 == ["34", "33", "33"], sp3)
        js(page, "()=>ps1RowDel('e',2)"); settle(page, 150)
        sp2 = js(page, "()=>[...document.querySelectorAll('input[id^=cnEr]')].map(i=>i.value)")
        check(f"{tag} 2 removing a row → 50/50", sp2 == ["50", "50"], sp2)
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 3 Core | Sat top bar · keys · header position ──
    b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
    try:
        P.ps_on(page)
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 500)
        top = js(page, """()=>({btns:[...document.querySelectorAll('.scopeTabs button')].map(b=>b.id+':'+b.innerText.replace(/\\s+/g,' ').trim()), old:!!document.getElementById('scopeLadder')||!!document.getElementById('scopeStock'),
            inHdr:!!document.getElementById('scopeCore').closest('#hdrSub'), hdPlan:document.querySelector('.topbar').classList.contains('hd-plan'), ov:document.documentElement.scrollWidth>innerWidth,
            seg:!!document.querySelector('[data-lf-seg]'), coreTitle:(document.querySelector('[data-lf-core-title]')||{}).innerText})""")
        check(f"{tag} 3 plan scope = 2 buttons Core | Sat (no Momentum/Compounder/Sat trio)", len(top["btns"]) == 2 and top["btns"][0].startswith("scopeCore:Core") and top["btns"][1].startswith("scopeFuture:Sat") and not top["old"] and not top["hdPlan"] and not top["ov"], top)
        check(f"{tag} 3 dark Core header has a Momentum | Compounder switch", top["seg"] and "Core" in (top["coreTitle"] or ""), top)
        js(page, "()=>lfPortSet('ladder')"); settle(page, 200)
        check(f"{tag} 3 Core header switch → Compounder (scope=ladder · Core stays on)", js(page, "()=>[planScope, document.getElementById('scopeCore').classList.contains('on')]") == ["ladder", True], "")
        js(page, "()=>setPlanScope('future')"); settle(page, 200)
        js(page, "()=>document.getElementById('scopeCore').click()"); settle(page, 200)
        check(f"{tag} 3 Sat → Core restores the last Core port (Compounder)", js(page, "()=>planScope") == "ladder", "")
        # keys S / D / F
        ks = []
        for key, exp in (("KeyS", "stock"), ("KeyD", "ladder"), ("KeyF", "future")):
            page.keyboard.press(key[-1].lower()); settle(page, 200); ks.append([key, js(page, "()=>planScope"), exp])
        check(f"{tag} 3 keys S (Momentum) · D (Compounder) · F (Sat) still work", all(k[1] == k[2] for k in ks), ks)
        if w >= 900:
            tabs = js(page, "()=>{ const t=document.getElementById('tabsMain').getBoundingClientRect(), v=document.documentElement.clientWidth; return {centerOff:Math.abs((t.left+t.right)/2 - v/2)}; }")
            js(page, "()=>switchTab('today')"); settle(page, 300)
            t2 = js(page, "()=>{ const t=document.getElementById('tabsMain').getBoundingClientRect(); return {l:t.left}; }")
            js(page, "()=>{ switchTab('plan'); }"); settle(page, 300)
            t3 = js(page, "()=>{ const t=document.getElementById('tabsMain').getBoundingClientRect(); return {l:t.left}; }")
            check(f"{tag} 3 main tabs identical position on Plan and on Today (centred, no left shift)", abs(t2["l"] - t3["l"]) < 1 and tabs["centerOff"] < 4, [tabs, t2, t3])
        check(f"{tag} 3 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 4 Sat form alignment ──
    b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
    try:
        X.ps_set(page)
        iid = X.sat_plan(page, "XAUUSD", 2000, 1985, 2040)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); settle(page, 600)
        def sat():
            return js(page, """()=>{ const q=s=>document.querySelector(s); const r=e=>e&&e.getBoundingClientRect(); const e1=r(q('[data-v2-entry]')), sl=r(q('[data-v2-sl]')), tp=r(q('[data-v2-tp]')), plus=r(q('[data-sat-e2add]')),
              lab=q('[data-v2-entry]').closest('div').querySelector('label'), e2=r(q('[data-v2-entry2]')), sh=r(q('[data-v2-e2share]')), rm=r(q('[data-sat-e2rm]'));
              return {tops:[e1.top,sl.top,tp.top], w:[e1.width,sl.width,tp.width], plusTop:plus&&plus.top, plusH:plus&&plus.height, labTop:r(lab).top, e2:e2&&{left:e2.left,w:e2.width,top:e2.top}, e1l:e1.left, sl_l:sl.left, tp_l:tp.left,
                sh:sh&&{left:sh.left,top:sh.top}, rm:rm&&{left:rm.left}, ov:document.documentElement.scrollWidth>innerWidth}}""")
        a = sat()
        check(f"{tag} 4 Sat: Entry / SL / TP boxes on one baseline · ＋ is small (≤22px) and on the label line", abs(a["tops"][0] - a["tops"][1]) < 1 and abs(a["tops"][1] - a["tops"][2]) < 1 and a["plusH"] <= 22 and a["plusTop"] < a["tops"][0], a)
        js(page, "()=>document.querySelector('[data-sat-e2add]').click()"); settle(page, 500)
        b2 = sat()
        check(f"{tag} 4 Sat: Entry 2 is the SAME size/column as Entry 1; its % + ✕ sit in the SL column; TP column empty; boxes did not move", b2["e2"] and abs(b2["e2"]["w"] - b2["w"][0]) < 1 and abs(b2["e2"]["left"] - b2["e1l"]) < 1 and abs(b2["sh"]["left"] - b2["sl_l"]) < 2 and abs(b2["sh"]["top"] - b2["e2"]["top"]) < 8 and b2["rm"]["left"] > b2["sh"]["left"] and abs(b2["tops"][0] - a["tops"][0]) < 1 and not b2["ov"], [a, b2])
        check(f"{tag} 4 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 5 Today: homework row + Plans badge ──
    tr = []
    for n, syms in (("one", ["AVGO"]), ("three", ["AVGO", "GLBE", "NVDA"]), ("five", ["AVGO", "GLBE", "NVDA", "MSFT", "AMZN"])):
        cards = {f"hw{i}": P.card(ticker=s_, plan={"entry": 100, "stop": 90, "ft": {"at": "2026-11-07", "due": "2026-11-08" if i == 2 else "2026-11-13"}}) for i, s_ in enumerate(syms)}
        b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
        try:
            P.ps_on(page)
            js(page, "()=>{ ftToday = ()=>'2026-11-10'; switchTab('today'); render(); }"); settle(page, 600)
            r = js(page, """()=>{ const rows=[...document.querySelectorAll('[data-ft-pinrow]')]; const row=rows[0]; if(!row) return {n:0};
              const vis=[...row.querySelectorAll('.ftc:not(.ftmore)')].filter(c=>c.offsetParent!==null).map(c=>c.innerText.trim());
              const more=row.querySelector('[data-ft-more]'); return {n:rows.length, vis, more:more&&more.innerText.trim(), od:row.classList.contains('od'), odChip:[...row.querySelectorAll('.ftc.od')].length,
               border:getComputedStyle(row).borderTopColor, goes:!!row.querySelector('[data-ft-go]'), ov:document.documentElement.scrollWidth>innerWidth, old:document.querySelectorAll('[data-ft-pin] ~ .tx').length}}""")
            if n == "one":
                check(f"{tag} 5 homework: ONE row with 1 chip (AVGO) · no '+N'", r["n"] == 1 and r["vis"] == ["AVGO 3d"] and r["more"] is None and r["goes"] and not r["ov"], r)
            elif n == "three":
                check(f"{tag} 5 homework: 3 chips in ONE row · overdue chip red (NVDA) · row border red", r["n"] == 1 and len(r["vis"]) == 3 and "NVDA overdue" in r["vis"] and r["od"] and r["odChip"] == 1 and r["more"] is None and not r["ov"], r)
            else:
                check(f"{tag} 5 homework: 5 items → 3 chips + '+2'", r["n"] == 1 and len(r["vis"]) == 3 and r["more"] == "+2", r)
                js(page, "()=>document.querySelector('[data-ft-more]').click()"); settle(page, 150)
                v2 = js(page, "()=>[[...document.querySelectorAll('[data-ft-pinrow] .ftc:not(.ftmore)')].filter(c=>c.offsetParent!==null).length, document.querySelector('[data-ft-more]').innerText.trim()]")
                js(page, "()=>document.querySelector('[data-ft-more]').click()"); settle(page, 150)
                v3 = js(page, "()=>[[...document.querySelectorAll('[data-ft-pinrow] .ftc:not(.ftmore)')].filter(c=>c.offsetParent!==null).length, document.querySelector('[data-ft-more]').innerText.trim()]")
                check(f"{tag} 5 '+2' expands in place (5 chips) and collapses again (3 chips)", v2[0] == 5 and v3 == [3, "+2"], [v2, v3])
                goto = js(page, "()=>{ let hit=null; const o=ftGo; window.ftGo=s=>{hit=s;}; document.querySelector('[data-ft-go]').click(); window.ftGo=o; return hit; }")
                check(f"{tag} 5 'Do it ›' goes to the most urgent (NVDA, overdue)", goto == "NVDA", goto)
                badge = js(page, "()=>{ switchTab('today'); render(); return [...document.querySelectorAll('.td3-pr')].map(x=>x.innerText.replace(/\\s+/g,' ')).slice(0,3); }")
                check(f"{tag} 5 Today › Plans rows carry the homework badge next to Draft", all("Homework" in t or "Overdue" in t for t in badge) and len(badge) > 0, badge)
            check(f"{tag} 5 console ไม่มี error ({n})", not ce and not pe, [ce[:2], pe[:2]])
        finally:
            b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 1000)):
            run(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
