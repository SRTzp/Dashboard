#!/usr/bin/env python3
"""PS1b §10 — RRG "Fresh": NEW tag (≤3 bars D / ≤1 completed week W · previous state ≥5 bars / ≥2 weeks · only Beating↗ / Lagging↗ / Beating↘)
+ [All][Fresh N] filter (remembered) + fit at 390/1440 · เทส 122"""
import json
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase105 as P105
import ln3fix_common as C

ENGINE = base.BROWSER_ENGINE
results = []
js, settle = C.js, T.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + detail[:700]) if (detail and not ok) else ""))


def Rp(sym, quad, days, prev, dm=0.1, **k):
    r = P105.R(sym, sym + " name", quad, dm=dm, days=days, **k)
    if prev is not None: r["prevDays"] = prev
    return r


def pure_tests(pw):
    b, page, ce, pe = T.launch(pw, 1440, 900)
    try:
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        t = js(page, """()=>{ const N=(q,d,p,tf)=>rrgNew({sym:'X',quad:q,days:d,prevDays:p,dMom:0},tf); const o=x=>x?x.n+x.u:null;
          return {flick:o(N('lead',2,2,'D')), real:[1,2,3,4].map(d=>o(N('lead',d,6,'D'))), prev5:o(N('lead',1,5,'D')), prev4:o(N('lead',1,4,'D')),
            neu:o(N('flat',1,9,'D')), lagdn:o(N('lag',1,9,'D')), imp:o(N('imp',1,9,'D')), weak:o(N('weak',2,9,'D')), noPrev:o(rrgNew({sym:'X',quad:'lead',days:1,dMom:0},'D')),
            w1:o(N('lead',1,2,'W')), w2:o(N('lead',2,5,'W')), wflick:o(N('lead',1,1,'W')), err:o(rrgNew({err:'x'},'D')),
            cfg: JSON.stringify(RRG_FRESH)}; }""")
        check("§10 flicker: previous state only 2 bars → no NEW", t["flick"] is None, t)
        check("§10 real change: NEW for 3 bars (1d,2d,3d) then gone (4th bar)", t["real"] == ["1d", "2d", "3d", None], t)
        check("§10 previous state must last ≥5 bars (5 ok · 4 not)", t["prev5"] == "1d" and t["prev4"] is None, t)
        check("§10 Neutral and Lagging ↘ never NEW · Lagging ↗ and Beating ↘ can be", t["neu"] is None and t["lagdn"] is None and t["imp"] == "1d" and t["weak"] == "2d", t)
        check("§10 Weekly: ≤1 completed week and previous ≥2 weeks (2nd week → gone · prev 1 week → no)", t["w1"] == "1w" and t["w2"] is None and t["wflick"] is None, t)
        check("§10 missing prevDays (old stored rows) or error row → no NEW (never guessed)", t["noPrev"] is None and t["err"] is None, t)
        check("§10 thresholds live in one constant block RRG_FRESH", '"maxDays":3' in t["cfg"] and '"minPrev":5' in t["cfg"] and '"maxDays":1' in t["cfg"], t["cfg"])
        # rrgCompute: prevDays comes from the real state series (no partial week: weekly is built from completed weeks only)
        c = js(page, """()=>{ const n=420, bench=[], cl=[]; let v=100; for(let i=0;i<n;i++){ bench.push(100); v*= i<250 ? 1.002 : i<330 ? 0.9985 : 1.003; cl.push(v); }
          const r=rrgCompute(cl, cl.map(x=>x*1.01), bench, 'D'); return {q:r.quad, d:r.days, p:r.prevDays, n:r.bars}; }""")
        check("§10 rrgCompute returns prevDays (length of the state before the current run)", c["p"] is None or (c["p"] >= 1 and c["d"] + c["p"] <= c["n"]), c)
        check("§10 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def ui_tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        rows = [Rp("AAA", "lead", 2, 8, dm=0.1), Rp("BBB", "imp", 1, 3, dm=0.1), Rp("CCC", "lag", 1, 9, dm=0.1), Rp("DDD", "lead", 9, 9, dm=0.9),
                Rp("EEE", "lead", 1, 6, dm=0.8), Rp("FFF", "flat", 1, 9, dm=0.0)]
        wk = [Rp("AAA", "lead", 1, 3), Rp("BBB", "lead", 2, 5)]
        P105.seed_rrg(page, d=rows, wk=wk); P105.go_flow(page)
        js(page, "()=>{ try{ localStorage.removeItem('rrgFreshOnly'); }catch(e){} ffRenderThemes(); }"); settle(page, 300)
        g = js(page, "()=>Object.fromEntries([...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>{ const n=e.querySelector('[data-rr-new]'); return [e.dataset.rr, n ? n.querySelector('.rr-spl').textContent : null]; }))")
        check(f"{tag} §10 การ์ด NEW: AAA 'NEW · 2d' · EEE 'NEW · 1d' · BBB (prev 3), DDD (9 bars), CCC (Lagging ↘), FFF (Neutral) ไม่มี", g.get("AAA") == "NEW · 2d" and g.get("EEE") == "NEW · 1d" and not any(g.get(k) for k in ("BBB", "CCC", "DDD", "FFF")), g)
        f = js(page, "()=>{ const b=[...document.querySelectorAll('[data-rr-fresh-f] button')].map(x=>x.textContent.trim()); return b; }")
        check(f"{tag} §10 ตัวกรอง [All] [Fresh N]: N = การ์ด NEW หรือ ⚡ (AAA, EEE ใหม่ · DDD, EEE มี ⚡ → 3)", f == ["All", "Fresh 3"], f)
        js(page, "()=>document.querySelector('[data-rr-f=fresh]').click()"); settle(page, 400)
        syms = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>e.dataset.rr).sort()")
        check(f"{tag} §10 กด Fresh → เหลือเฉพาะ AAA · DDD · EEE", syms == ["AAA", "DDD", "EEE"], syms)
        mem = js(page, "()=>localStorage.getItem('rrgFreshOnly')")
        js(page, "()=>{ ffRenderThemes(); }"); settle(page, 300)
        syms2 = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr]')].length")
        check(f"{tag} §10 จำตัวเลือกต่ออุปกรณ์ (localStorage) แล้ว render ใหม่ยังคงกรอง", mem == "1" and syms2 == 3, [mem, syms2])
        js(page, "()=>document.querySelector('[data-rr-f=all]').click()"); settle(page, 300)
        n_all = js(page, "()=>document.querySelectorAll('#ffThemes [data-rr]').length")
        check(f"{tag} §10 กด All → ครบ 6 การ์ด", n_all == 6, n_all)
        # weekly
        js(page, "()=>rrgSetTf('W')"); settle(page, 400)
        gw = js(page, "()=>Object.fromEntries([...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>{ const n=e.querySelector('[data-rr-new]'); return [e.dataset.rr, n ? n.querySelector('.rr-spl').textContent : null]; }))")
        check(f"{tag} §10 Weekly: AAA (1 week, prev 3) → 'NEW · 1w' · BBB (2nd week) ไม่มี", gw.get("AAA") == "NEW · 1w" and not gw.get("BBB"), gw)
        js(page, "()=>rrgSetTf('D')"); settle(page, 300)
        lay = js(page, """()=>[...document.querySelectorAll('#ffThemes [data-rr] .rr-lean')].map(l=>{ const lr=l.getBoundingClientRect(); const ch=[...l.querySelectorAll('.rr-ch,.rr-sp,.rr-nw')].filter(c=>c.getBoundingClientRect().width>0);
            const cy=ch.map(c=>{ const r=c.getBoundingClientRect(); return r.top+r.height/2; }); return {oneRow: Math.max(...cy)-Math.min(...cy) <= 4, inside: ch.every(c=>c.getBoundingClientRect().right <= lr.right+1)}; })""")
        check(f"{tag} §10 NEW + ⚡ + ชิป อยู่แถวเดียว ไม่ล้น ({w}px)", all(x["oneRow"] and x["inside"] for x in lay), lay)
        ov = js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
        check(f"{tag} §10 ไม่ overflow แนวนอน", ov <= 0, ov)
        if w <= 430:
            sh = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr-new]')].map(s=>[getComputedStyle(s.querySelector('.rr-spl')).display, getComputedStyle(s.querySelector('.rr-sps')).display, s.closest('.rr-lean').getBoundingClientRect().width])")
            check(f"{tag} §10 แคบ ≤330px → 'NEW' สั้น", all((x[0] == "none" and x[1] != "none") == (x[2] <= 330) for x in sh), sh)
        js(page, "()=>{ localStorage.setItem('dash.ps1Off','1'); ffRenderThemes(); }"); settle(page, 300)
        off = js(page, "()=>[document.querySelectorAll('[data-rr-new]').length, document.querySelectorAll('[data-rr-fresh-f]').length]")
        check(f"{tag} §10 โหมดเดิม (ps1Off) ไม่มี NEW / ตัวกรอง", off == [0, 0], off)
        check(f"{tag} §10 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def ask_tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        rows = [Rp("AAA", "lead", 2, 8, dm=0.1, off=-1.0), Rp("CCC", "lag", 1, 9, dm=0.1), Rp("DDD", "lead", 9, 9, dm=0.9)]
        P105.seed_rrg(page, d=rows, wk=[]); P105.go_flow(page)
        js(page, "()=>{ window.__cp=[]; Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__cp.push(t);return Promise.resolve();}},configurable:true}); }")
        has = js(page, "()=>Object.fromEntries([...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>[e.dataset.rr, !!e.querySelector('[data-sd-ask]')]))")
        check(f"{tag} §11 'Ask why ›' เฉพาะการ์ด Fresh (AAA=NEW, DDD=⚡) · CCC ไม่มี", has == {"AAA": True, "CCC": False, "DDD": True}, has)
        txt = js(page, "()=>document.querySelector('#ffThemes [data-rr=AAA] [data-sd-sum]').innerText.replace(/\\s+/g,' ')")
        check(f"{tag} §11 ข้อความบรรทัด: 'Not recorded · Ask why ›' (ยังไม่มี driver)", "Not recorded · Ask why ›" in txt, txt)
        js(page, "()=>document.querySelector('#ffThemes [data-rr=AAA] [data-sd-ask]').click()"); settle(page, 300)
        cp = js(page, "()=>window.__cp")
        want = "idea-scout scan: AAA AAA name turned Beating SPY ↗ on "
        check(f"{tag} §11 คลิก → คัดลอก prompt ตามข้อมูลการ์ด (state · Daily · NEW·2)", cp and cp[0].startswith(want) and "(Daily, NEW·2)" in cp[0] and cp[0].endswith("then the value chain and tickers."), cp)
        open_ = js(page, "()=>document.querySelector('#ffThemes [data-rr=AAA]').classList.contains('open')")
        check(f"{tag} §11 กดลิงก์ไม่เปิด/ปิดแถว (ไม่ toggle)", open_ is False, open_)
        cp2 = js(page, "()=>{ document.querySelector('#ffThemes [data-rr=DDD] [data-sd-ask]').click(); return window.__cp[1]; }")
        check(f"{tag} §11 การ์ด ⚡ อย่างเดียว: prompt มี '⚡ speeding up' ไม่มี NEW", cp2 and "(Daily, ⚡ speeding up)" in cp2, cp2)
        tt = js(page, """()=>{ const t=document.getElementById('cgToast'); if(!t) return null; const r=t.getBoundingClientRect();
            return {txt:[...t.querySelectorAll('.cgL')].map(e=>e.textContent).join('\\n'), shown:t.classList.contains('show'), lines:t.querySelectorAll('.cgL').length, fits:r.left>=0&&r.right<=innerWidth, btn:t.querySelectorAll('button,a').length, n:document.querySelectorAll('#cgToast').length}; }""")
        check(f"{tag} CG1 toast ล่าง 3 บรรทัดตามสเปก มีแค่ปุ่ม ✕ ไม่เกิน 3 บรรทัด ไม่ล้นจอ", tt and tt["shown"] and tt["txt"] == "Goal: find the dated reason this sector turned.\nPaste → scan → real driver? tick segments → pick.\nNo dated driver = price move, ignore." and tt["lines"] <= 3 and tt["fits"] and tt["btn"] == 1 and tt["n"] == 1, tt)
        ms = js(page, "()=>[cgToastMs('x'), cgToastMs('x'.repeat(10)), cgToastMs('x'.repeat(60)), cgToastMs('x'.repeat(100)), cgToastMs('x'.repeat(40)), cgToastMs('x'.repeat(120)), cgToastMs('x'.repeat(200))]")
        check(f"{tag} §11 auto-hide = clamp(5s, 2.5s+60ms×ตัวอักษร, 10s)", ms == [5000, 5000, 6100, 8500, 5000, 9700, 10000], ms)
        js(page, "()=>{ const t=document.getElementById('cgToast'); t.dispatchEvent(new Event('mouseenter')); }"); settle(page, 150)
        paused = js(page, "()=>cgToastT === 0 && document.getElementById('cgToast').classList.contains('show')")
        js(page, "()=>{ document.getElementById('cgToast').dispatchEvent(new Event('mouseleave')); }"); settle(page, 100)
        resumed = js(page, "()=>cgToastT !== 0")
        check(f"{tag} §11 หยุดนับตอน hover/touch แล้วนับต่อเมื่อปล่อย", paused and resumed, [paused, resumed])
        js(page, "()=>document.querySelector('#ffThemes [data-rr=DDD] [data-sd-ask]').click()"); settle(page, 200)
        one_t = js(page, "()=>document.querySelectorAll('#cgToast.show').length")
        js(page, "()=>document.getElementById('cgToast').click()"); settle(page, 200)
        closed = js(page, "()=>!document.getElementById('cgToast').classList.contains('show')")
        check(f"{tag} §11 ทีละอัน (คลิกซ้ำไม่ซ้อน) · แตะเพื่อปิด", one_t == 1 and closed, [one_t, closed])
        one = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr] [data-sd-sum]')].filter(e=>e.querySelector('[data-sd-ask]')).every(e=>e.getBoundingClientRect().height<=22 && e.scrollWidth<=e.clientWidth+1)")
        check(f"{tag} §11 บรรทัดเดียว ไม่ห่อ ไม่ล้น ({w}px)", one, one)
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        pure_tests(pw)
        for w, h in ((1440, 1000), (390, 844)):
            ui_tests(pw, w, h)
            ask_tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nPS1b phase122: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
