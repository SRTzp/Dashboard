#!/usr/bin/env python3
"""LN3fix2 §4–5 — แผน Sat "แผน & ไม้ที่ถือ" (แทน Positions + บรรทัด heat) · ไม้นอกแผน · Port โหมดรวมมีชื่อบัญชี · Today ชิป XAU ไม่ตกบรรทัด · เทส 92
mock Firestore · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3fix2-{plan,port,today}-{1440,390}.png
รัน: python3 run_tests_phase92.py"""
import json, os, re
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase13 as P13
import run_tests_phase77 as P77
import run_tests_phase78 as P78

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
overflow = C.overflow


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def txt(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def launch(pw, w, h):
    """XAUUSD Main: 2 บัญชีเข้าแล้ว · BTC นอกแผนถืออยู่ (main) · BTC Tactical ร่าง"""
    browser, page, ce, pe = P77.launch(pw, w, h)
    js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", ["XAUUSD", "BTCUSD"])
    P11.wk(page, "BTCUSD", "Short", "down"); page.wait_for_timeout(300)
    iid = P77.idea(page, asset="XAUUSD", sleeve="main", entry=4180, sl=4117)
    P78.note(page, iid)
    js(page, "([i])=>satV3PlanEdit(i,'tp','4300')", [iid]); page.wait_for_timeout(300)
    P78.save(page, iid)
    js(page, """()=>{ ['main','fam'].forEach((a,i)=>{ const B = getBook(a); B.trades.filter(t=>t.sym==='XAUUSD' && t.port==='satB').forEach(t=>{ t.status='open'; t.openedAt='2026-09-28'; t.date='2026-09-28'; t.entry = 4182 + i*3; t.sl = 4150; t.tp = null; }); saveBook(a); }); render(); }""")
    page.wait_for_timeout(500)
    bt = P13.T("tBT", "satB", "open", sym="BTCUSD", bias="Long", entry=61200, sl=60400, qty=0.02, tp=64000, unplanned=True, cur="USD", mult=1, date="2026-09-30")
    js(page, "(t)=>{ const B = getBook('main'); B.trades.push(t); saveBook('main'); render(); }", bt); page.wait_for_timeout(300)
    P77.idea(page, asset="BTCUSD", sleeve="tactical", entry=63500, sl=64200)
    js(page, "()=>{ switchTab('plan'); setPlanScope('future'); ln3Open.clear(); lfHeldClosed.clear(); satV3Render({force:true}); }"); page.wait_for_timeout(600)
    return browser, page, ce, pe, iid


def shot(page, name, full=True): C.shot(page, name, full=full)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe, iid = launch(pw, w, h)
    try:
        g = js(page, "()=>({pos: document.getElementById('posPanel').offsetParent!==null, foot: document.getElementById('foot').offsetParent!==null, txt: /Positions|heat:/.test(document.getElementById('tabPlan').innerText)})")
        check(f"{tag} 1 แผน Sat (Lean): ไม่มีส่วน Positions และไม่มีบรรทัด heat ท้ายหน้า", not g["pos"] and not g["foot"] and not g["txt"], g)
        head = txt(page, "#satV3Panel .h"); cnt = txt(page, "[data-lf-hcount]")
        check(f"{tag} 1 หัวการ์ด 'แผน & ไม้ที่ถือ' · 'ถือ 2 · แผน 1' (XAU ที่เข้าแล้ว + BTC นอกแผน · BTC ร่าง)", head and head.startswith("แผน & ไม้ที่ถือ") and cnt == "ถือ 2 · แผน 1", [head, cnt])
        order = js(page, "()=>[...document.querySelectorAll('#satV3Panel .ln3-prow[data-ln3-row]')].map(r=>r.dataset.ln3Row.startsWith('off-') ? 'off:' + r.dataset.lfAsset : r.dataset.lfAsset + ':' + r.dataset.ln3State)")
        check(f"{tag} 1 เรียง: ถืออยู่ (XAU) → นอกแผน (BTC ถือ) → ร่าง (BTC Tactical)", order == ["XAUUSD:open", "off:BTCUSD", "BTCUSD:draft"], order)
        # กางเป็นค่าเริ่ม
        det = js(page, """()=>{ const d = document.querySelector('[data-lf-held=open][data-lf-asset=XAUUSD] + [data-lf-detail]'); if(!d) return null; return {n: d.querySelectorAll('[data-lf-trade]').length, lines: [...d.querySelectorAll('[data-lf-trade]')].map(l=>l.innerText.replace(/\\s+/g,' ').trim()), total: (document.querySelector('[data-lf-total]')||{innerText:''}).innerText.replace(/\\s+/g,' ')}; }""")
        check(f"{tag} 2 แถวที่เข้าแล้ว กางเป็นค่าเริ่ม: 'รวม $/$cap' + ต่อบัญชี 2 บรรทัด ('● บัญชี lot · n วัน  $เสี่ยง ⋯' / 'ทุน · SL · TP')", det and det["n"] == 2 and det["total"].startswith("รวม $") and "/$" in det["total"] and all("lot" in l and "วัน" in l and "ทุน" in l and "SL" in l and "TP" in l for l in det["lines"]), det)
        calc = js(page, """()=>{ const r = document.querySelector('[data-lf-held=open]'); const tot = ['main','fam'].map(a=>{ const R = satV2Risk(a), CP = satV2Caps(a), fx = satV2Money(a).fx || 1; const ar = R.byAsset['XAUUSD']; return [ar ? ar.tot / fx : 0, CP.asset / fx]; });
          return {ptot: r.querySelector('[data-lf-total] [data-ln3-ptot]').innerText, pcap: r.querySelector('[data-lf-total] [data-ln3-pcap]').innerText, e: [Math.round(tot[0][0] + tot[1][0]), Math.round(tot[0][1] + tot[1][1])]}; }""")
        check(f"{tag} 2 'รวม' = Risk สินทรัพย์นั้น / เพดานต่อสินค้า ตรง satV2Risk/satV2Caps", calc["ptot"] == f"${calc['e'][0]:,}" and calc["pcap"] == f"${calc['e'][1]:,}", calc)
        risk_ok = js(page, """()=>[...document.querySelectorAll('[data-lf-held=open][data-lf-asset=XAUUSD] + [data-lf-detail] [data-lf-trade]')].map(l=>{ const id = l.dataset.lfTrade; const a = ['main','fam'].find(x=>getBook(x).trades.some(t=>t.id===id)); const t = getBook(a).trades.find(x=>x.id===id); const fx = satV2Money(a).fx||1; return l.querySelector('.r').innerText.includes(satV2Usd(ln3TradeRiskTHB(t, fx), fx)) && l.innerText.includes(fmt2(t.entry)); })""")
        check(f"{tag} 2 ตัวเลขต่อบัญชีตรงสูตรเดิม (เสี่ยง $ = ln3TradeRiskTHB · ทุน = Entry ของไม้)", len(risk_ok) == 2 and all(risk_ok), risk_ok)
        # พับ/กาง
        js(page, "()=>document.querySelector('[data-lf-held=open]').click()"); page.wait_for_timeout(400)
        col = js(page, """()=>{ const r = [...document.querySelectorAll('[data-lf-held]')].find(x=>x.dataset.lfAsset==='XAUUSD'); return {st: r.dataset.lfHeld, p2: (r.querySelector('[data-ln3-p2]')||{innerText:''}).innerText.replace(/\\s+/g,' '), detail: !!document.querySelector('[data-lf-detail]'), sel: localStorage.getItem('lf_sat_asset')}; }""")
        check(f"{tag} 2 แตะหัวแถว → พับ: บรรทัดสรุป '● lot $ · ● lot $ · รวม $/$cap' · Strategy ตาม Asset (XAU)", col["st"] == "closed" and col["p2"].count("●") == 2 and "· รวม $" in col["p2"] and col["sel"] == "XAUUSD", col)
        js(page, "()=>[...document.querySelectorAll('[data-lf-held]')].find(x=>x.dataset.lfAsset==='XAUUSD').click()"); page.wait_for_timeout(400)
        back = js(page, "()=>[...document.querySelectorAll('[data-lf-held]')].find(x=>x.dataset.lfAsset==='XAUUSD').dataset.lfHeld")
        check(f"{tag} 2 แตะอีกครั้ง → กางกลับ", back == "open", back)
        # ⋯
        js(page, "()=>document.querySelector('[data-lf-detail] [data-lf-tmenu]').click()"); page.wait_for_timeout(250)
        menu = js(page, "()=>{ const m = [...document.querySelectorAll('[data-lf-detail] .lf-mn')].find(x=>x.style.display==='block'); return m ? [...m.querySelectorAll('button')].map(b=>b.innerText.trim()) : null; }")
        check(f"{tag} 2 ⋯ ของแต่ละไม้: ปิด · แก้ · ยกเลิก · ลบ", menu == ["ปิด", "แก้", "ยกเลิก", "ลบ"], menu)
        tid = js(page, "()=>document.querySelector('[data-lf-detail] [data-lf-trade]').dataset.lfTrade")
        acct = js(page, "(i)=>['main','fam'].find(x=>getBook(x).trades.some(t=>t.id===i))", tid)
        js(page, "()=>document.querySelector('[data-lf-detail] [data-lf-act=close]').click()"); page.wait_for_timeout(500)
        o1 = js(page, "()=>({show: document.getElementById('closePosOverlay').classList.contains('show'), info: document.getElementById('cpInfo').innerText.replace(/\\s+/g,' ')})")
        js(page, "()=>document.getElementById('closePosOverlay').classList.remove('show')")
        js(page, "([i,a])=>openClosePos(i,a)", [tid, acct]); page.wait_for_timeout(400)
        o2 = js(page, "()=>({show: document.getElementById('closePosOverlay').classList.contains('show'), info: document.getElementById('cpInfo').innerText.replace(/\\s+/g,' ')})")
        js(page, "()=>document.getElementById('closePosOverlay').classList.remove('show')")
        check(f"{tag} 2 ⋯ › ปิด = เปิดหน้าต่างปิดไม้เดิม (openClosePos) ผลเดียวกับ Positions เดิม", o1["show"] and o1 == o2 and "XAUUSD" in o1["info"], [o1, o2])
        js(page, "()=>{ document.querySelector('[data-lf-detail] [data-lf-tmenu]').click(); document.querySelector('[data-lf-detail] [data-lf-act=edit]').click(); }"); page.wait_for_timeout(400)
        e1 = js(page, "()=>document.getElementById('teOverlay').classList.contains('show')")
        js(page, "()=>document.getElementById('teOverlay').classList.remove('show')")
        check(f"{tag} 2 ⋯ › แก้ = หน้าต่างแก้ไม้เดิม (openTradeEdit)", e1, e1)
        js(page, "()=>{ document.querySelector('[data-lf-detail] [data-lf-tmenu]').click(); document.querySelector('[data-lf-detail] [data-lf-act=cancel]').click(); }"); page.wait_for_timeout(400)
        c1 = js(page, "()=>[...document.querySelectorAll('.overlay.show')].map(o=>o.id)")
        js(page, "()=>document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'))")
        check(f"{tag} 2 ⋯ › ยกเลิก = หน้าต่างยกเลิกไม้เดิม (openCancelModal)", len(c1) == 1 and "ancel" in c1[0], c1)
        n0 = js(page, "()=>getBook('main').trades.length + getBook('fam').trades.length")
        js(page, "()=>{ document.querySelector('[data-lf-detail] [data-lf-tmenu]').click(); document.querySelector('[data-lf-detail] [data-lf-act=del]').click(); }"); page.wait_for_timeout(600)
        n1 = js(page, "()=>getBook('main').trades.length + getBook('fam').trades.length")
        gone = js(page, "(i)=>!['main','fam'].some(x=>getBook(x).trades.some(t=>t.id===i))", tid)
        check(f"{tag} 2 ⋯ › ลบ = ลบไม้เดิม (delTrade) · ไม้นั้นหายไป", gone and n1 == n0 - 1, [n0, n1, gone])
        # ไม้นอกแผน
        off = js(page, """()=>{ const r = document.querySelector('[data-lf-held][data-ln3-row^="off-"]'); if(!r) return null; const tg = r.querySelector('[data-lf-offplan]'); const d = r.nextElementSibling; return {tag: tg.innerText, bg: getComputedStyle(tg).backgroundColor, open: r.dataset.lfHeld, line: d ? d.innerText.replace(/\\s+/g,' ') : '', status: r.querySelector('[data-ln3-status]').innerText.replace(/\\s+/g,' ')}; }""")
        redbg = bool(off) and [int(x) for x in re.findall(r"\d+", off["bg"])[:3]][0] > 230
        check(f"{tag} 3 ไม้นอกแผน = แถวของตัวเองป้ายแดง 'นอกแผน' · กางได้เหมือนกัน (ทุน 61,200 · SL 60,400 · TP 64,000)", off and off["tag"] == "นอกแผน" and redbg and off["open"] == "open" and "61,200" in off["line"] and "60,400" in off["line"] and "64,000" in off["line"] and off["status"].startswith("ถือ 1"), off)
        js(page, "()=>document.querySelector('[data-ln3-row^=\"off-\"]').click()"); page.wait_for_timeout(400)
        offc = js(page, "()=>({st: document.querySelector('[data-ln3-row^=\"off-\"]').dataset.lfHeld, p2: (document.querySelector('[data-ln3-row^=\"off-\"] [data-ln3-p2]')||{innerText:''}).innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 3 ไม้นอกแผนพับ = บรรทัดสรุป '● lot $ · รวม $/$cap'", offc["st"] == "closed" and "●" in offc["p2"] and "รวม $" in offc["p2"], offc)
        # ร่าง + Strategy ตาม
        js(page, "()=>document.querySelector('.ln3-prow[data-ln3-state=draft]').click()"); page.wait_for_timeout(500)
        sel = js(page, "()=>({s: localStorage.getItem('lf_sat_asset'), form: document.querySelectorAll('#satV3Panel .ui-plan').length})")
        check(f"{tag} 4 แตะแถวร่าง BTC → Strategy ตาม Asset (BTC) · ฟอร์มกาง (LN3fix ยังทำงาน)", sel["s"] == "BTCUSD" and sel["form"] == 1, sel)
        ov = js(page, "()=>{ const W = innerWidth, bad = []; document.querySelectorAll('#satV3Panel *').forEach(e=>{ if(e.closest('.waBar, table, pre')) return; const r = e.getBoundingClientRect(); if(r.width>0 && r.right > W + 1) bad.push(e.className||e.tagName); }); return bad.slice(0,5); }")
        check(f"{tag} 4 {label} แผน Sat (มีแถวถือ/นอกแผน) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
        js(page, "()=>{ ln3Open.clear(); lfHeldClosed.clear(); satV3Render({force:true}); window.scrollTo(0,0); }"); page.wait_for_timeout(300)
        if w in (1440, 390): shot(page, f"ln3fix2-plan-{sfx}.png")
        # legacy เหมือนเดิม
        js(page, "()=>{ ln1SetMode('legacy'); switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(700)
        lg = js(page, "()=>({pos: document.getElementById('posPanel').offsetParent!==null, foot: document.getElementById('foot').offsetParent!==null, held: document.querySelectorAll('[data-lf-held]').length, h: (document.querySelector('#satV3Panel .h')||{innerText:''}).innerText})")
        check(f"{tag} 5 legacy เหมือนเดิม: มี Positions + บรรทัด heat · ไม่มีแถวถือแบบ Lean", lg["pos"] and lg["foot"] and lg["held"] == 0 and "แผน & ไม้ที่ถือ" not in lg["h"], lg)
    finally: b.close()

    # ───────── Port โหมดรวม
    b, page, ce, pe, iid = launch(pw, w, h)
    try:
        js(page, "()=>{ try{ localStorage.removeItem('ln3_port_acc'); }catch(e){} switchTab('mix'); }"); page.wait_for_timeout(800)
        # RG2b — การ์ดโครงพอร์ต (Core/Main/Tactical) ถูกแทนด้วยเส้นถังเส้นเดียว + แถบพับต่อบัญชี (data-pool-line)
        names = js(page, "()=>{ const l = document.querySelector('[data-pool-line]'); if(l) l.open = true; return [...document.querySelectorAll('[data-pool-line] [data-pool-acct]')].map(c=>({id: c.dataset.poolAcct, name: (c.querySelector('.poolAcctN')||{innerText:null}).innerText, dot: !!c.querySelector('.acctDotC')})); }")
        check(f"{tag} 6 Port โหมดรวม: เส้นถังเส้นเดียว · แถบพับแยกต่อบัญชีมีชื่อ+จุดสี (ไม่ซ้ำไม่มีชื่อ)", js(page, "()=>document.querySelectorAll('[data-pool-line]').length") == 1 and len(names) == 2 and [n["id"] for n in names] == ["main", "fam"] and all(n["dot"] and n["name"] for n in names) and len({n["name"] for n in names}) == 2, names)
        ref = js(page, "()=>['main','fam'].map(a=>Math.round(satV2Money(a).totalTHB))")
        cards = js(page, "()=>[...document.querySelectorAll('[data-pool-line] [data-pool-acct]')].map(c=>c.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} 6 ยอดบัญชีต่อบัญชีในเส้นถัง = ยอดรวมเดิม (฿ ของแต่ละบัญชีเท่าเดิม)", len(cards) == 2 and all(f"฿{r:,}" in n for r, n in zip(ref, cards)), [ref, cards])
        js(page, "()=>ln3PortSet('main')"); page.wait_for_timeout(500)
        one = js(page, "()=>({n: document.querySelectorAll('[data-pool-line] [data-pool-acct]').length, names: document.querySelectorAll('[data-pool-line] .poolAcctN').length})")
        check(f"{tag} 6 เลือกบัญชีเดียว → บล็อกเดียว · ไม่มีหัวชื่อซ้ำ", one["n"] == 1 and one["names"] == 0, one)
        js(page, "()=>ln3PortSet('all')"); page.wait_for_timeout(400)
        if w in (1440, 390): shot(page, f"ln3fix2-port-{sfx}.png")
        ovf = overflow(page)
        check(f"{tag} 6 {label} Port ไม่ล้นแนวนอน", ovf <= 0, ovf)
    finally: b.close()

    # ───────── Today: ชิป XAU ไม่ตกบรรทัด
    b, page, ce, pe, iid = launch(pw, w, h)
    try:
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(1200)
        ch = js(page, "()=>[...document.querySelectorAll('.tdAs')].map(c=>{ const n = c.querySelector('.nm'); const r = n.getBoundingClientRect(); const cs = getComputedStyle(n); return {t: n.innerText, h: Math.round(r.height), ws: cs.whiteSpace, ch: Math.round(c.getBoundingClientRect().height)}; })")
        check(f"{tag} 7 Today เช็กแผน Sat: ชื่อ Asset บรรทัดเดียว ไม่ตกบรรทัด · ชิปกว้างพอ", len(ch) >= 2 and all(c["ws"] == "nowrap" and c["h"] <= 26 and c["ch"] <= 60 for c in ch), ch)
        ov = js(page, "()=>{ const W = innerWidth, bad = []; document.querySelectorAll('.tdAs, .tdSatGrid').forEach(e=>{ const r = e.getBoundingClientRect(); if(r.width>0 && r.right > W + 1) bad.push(e.className); }); return bad; }")
        check(f"{tag} 7 {label} ชิปเช็กแผน Sat ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
        if w in (1440, 390): shot(page, f"ln3fix2-today-{sfx}.png")
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
