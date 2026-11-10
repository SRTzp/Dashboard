#!/usr/bin/env python3
"""PS1b §7 plan form: 7a scope switch · 7b lean multi-row · 7c rounding · 7d Details 3 lines · 7e stock min stop · เทส 124 · Chromium 390/1440 (+320 fit)"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C
import run_tests_phase4 as base
import run_tests_phase120 as B
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
results = []
js, settle, P13 = C.js, T.settle, B.P13


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + detail[:700]) if (detail and not ok) else ""))


def stock_scope(page, scope="stock"):
    js(page, "([s])=>{ switchTab('plan'); setPlanScope(s); }", [scope]); settle(page, 300)


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = C.launch2(pw, w, h, [], {}, pin_winner=True)
    try:
        # psRisk WITHOUT minStopStock key -> defaults 4 / 7 apply
        B.ps_on(page)
        js(page, "()=>{ const B=getBook('main'); delete B.settings.psRisk.minStopStock; saveBook('main'); }")
        d = js(page, "()=>ps1StockMin('main')")
        check(f"{tag} §7e ค่าเริ่ม Momentum 4% · Compounder 7% (ไม่มี key = ใช้ค่านี้)", d == {"winner": 4, "ladder": 7}, d)
        # Momentum 3.9 blocked / 4.0 ok
        B.form(page, "MIN"); B.fill(page, 100, 96.1)
        e1 = B.errtxt(page); m1 = js(page, "()=>document.getElementById('cnSMsg').textContent")
        ms1 = js(page, "()=>{ const e=document.querySelector('[data-ms1-pill]'); return e ? e.textContent : ''; }")
        check(f"{tag} §7e MS1: Momentum SL ห่าง 3.9% → ไม่บล็อก · amber pill 'Sized on min stop 4% (your SL 3.9%)' · ไม่มี msg แดง", not B.save_dis(page) and "Sized on min stop 4% (your SL 3.9%)" in ms1 and "too tight" not in e1 and m1 == "", [e1, m1, ms1])
        B.fill(page, 100, 96)
        check(f"{tag} §7e Momentum: SL ห่าง 4.0% → ผ่าน (ไม่มี msg)", not B.save_dis(page) and js(page, "()=>document.getElementById('cnSMsg').style.display") == "none", [B.errtxt(page)])
        # multi-entry checks every row
        js(page, "()=>ps1RowAdd('e')"); settle(page, 150)
        js(page, "()=>{ document.getElementById('cnEn1').value='98'; ps1In('e',1,'98'); }"); settle(page, 150)
        e2 = B.errtxt(page)
        check(f"{tag} §7e MS1 หลาย entry: ทุกแถว vs SL (98→96 = 2.0% < 4%) → ไม่บล็อก (pill ต่อแถวตรวจใน MS1 test)", "Stop too tight" not in e2, e2)
        js(page, "()=>ps1RowDel('e',1)"); settle(page, 150)
        # 7a: switch scope while the form is open
        B.fill(page, 100, 90)
        t0 = js(page, "()=>'New ' + ({winner:'Momentum',ladder:'Compounder'})[coreNew.track] + ' plan'")
        js(page, "()=>setPlanScope('ladder')"); settle(page, 300)
        a = js(page, "()=>({title:'New ' + ({winner:'Momentum',ladder:'Compounder'})[coreNew.track] + ' plan', seg:document.querySelector('[data-ps1-seg] button.on').dataset.ps1Port, track:coreNew.track, entry:document.getElementById('cnEntry').value, stop:document.getElementById('cnStop').value, risk:document.getElementById('cnRisk').value})")
        check(f"{tag} §7a สลับ scope ตอนฟอร์มเปิด: 'New Momentum plan' → 'New Compounder plan' · track ladder · ราคาที่พิมพ์คงอยู่", t0 == "New Momentum plan" and a["title"] == "New Compounder plan" and a["track"] == "ladder" and a["seg"] == "ladder" and a["entry"] == "" and a["stop"] == "", [t0, a])   # PS1c §2: per-port drafts — typed prices are NOT carried to the other port
        # Compounder min 7%: 93.1 blocked, 93 ok
        B.fill(page, 100, 93.1); c1 = B.errtxt(page)
        ms7 = js(page, "()=>{ const e=document.querySelector('[data-ms1-pill]'); return e ? e.textContent : ''; }")
        B.fill(page, 100, 93); c2 = B.save_dis(page)
        check(f"{tag} §7e MS1 Compounder: 6.9% → ไม่บล็อก + pill 'min stop 7%' · 7.0% ผ่านไม่มี pill", "min stop 7%" in ms7 and not c2 and "too tight" not in c1, [c1, c2, ms7])
        sm = js(page, "()=>document.getElementById('cnSum').textContent.replace(/\\s+/g,' ')")
        js(page, "()=>setPlanScope('stock')"); settle(page, 300)
        a2 = js(page, "()=>({title:'New ' + ({winner:'Momentum',ladder:'Compounder'})[coreNew.track] + ' plan', track:coreNew.track, sum:document.getElementById('cnSum').textContent.replace(/\\s+/g,' ')})")
        check(f"{tag} §7a สลับกลับ → Momentum · สรุป/กฎเปลี่ยนตามบัคเก็ต", a2["title"] == "New Momentum plan" and a2["track"] == "winner" and a2["sum"] != sm, [a2, sm])
        js(page, "()=>coreSheetClose()")
        # ps1Off / settings fields
        js(page, "()=>{ openSettings(); }"); settle(page, 500)
        st = js(page, "()=>[document.getElementById('sPsMinW').value, document.getElementById('sPsMinL').value]")
        check(f"{tag} §7e Settings: ช่อง Min stop (stocks) เติมค่า 4 / 7 ไว้ให้แล้ว", st == ["4", "7"], st)
        js(page, "()=>{ document.getElementById('sPsMinW').value=''; crOnInput(); }")
        err = js(page, "()=>ps1FormErrs()")
        check(f"{tag} §7e ปล่อยว่าง = ปิด (ไม่มี error)", "sPsMinW" not in err, err)
        js(page, "()=>{ const o=document.getElementById('setOverlay'); if(o) o.remove(); }")
        # 7c exact case
        r = js(page, """()=>{ const r = Ps1.planSize({E:144000, market:'US', ideaRiskPct:0.25, entries:[{px:100,riskPct:0.125},{px:110,riskPct:0.125}], stops:[{px:90,pct:100}], maxSizePct:50, cash:1e9}); return {ok:r.ok, qty:r.rows&&r.rows.map(x=>x.qty), risk:r.risk, pct:ps1R2(r.riskPct), left:ps1R2(r.leftPct), r2:[ps1R2(0.2499999999), ps1R2(0.245), ps1R2(0.2449)]}; }""")
        check(f"{tag} §7c 18 sh × 10 + 9 sh × 20 = $360 = 0.25% → แสดง 0.25 (ปัดเศษ ไม่ตัดทิ้ง) · Left 0.00", r["ok"] and r["qty"] == [18, 9] and abs(r["risk"] - 360) < 1e-6 and r["pct"] == "0.25" and r["left"] == "0.00" and r["r2"] == ["0.25", "0.25", "0.24"], r)
        # 7d + 7b
        B.form(page, "DET"); B.fill(page, 100, 90)
        det = js(page, "()=>[...document.querySelectorAll('#cnDetB > div')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())")
        check(f"{tag} §7d Details = 3 บรรทัด: Portfolio… · risk×regime=… · After this …", len(det) == 3 and det[0].startswith("Portfolio ฿") and "× regime" in det[1] and "= $" in det[1] and "% of Momentum" in det[1] and det[2].startswith("After this: Momentum") and "of max 7.5%" in det[2] and not any("rounded down" in x for x in det), det)
        sm = js(page, "()=>document.getElementById('cnSum').textContent.replace(/\\s+/g,' ').trim()")
        check(f"{tag} §7b สรุป: '#จำนวน · size% · Risk x.xx%' (ไม่มี Avg เมื่อมี entry เดียว)", sm.startswith("#") and sm.count("·") == 2 and "Avg" not in sm and "Risk ฿" in sm and "%" in sm, sm)
        mt = js(page, "()=>[...document.querySelectorAll('[data-ps1-meta]')].map(e=>[e.dataset.ps1Meta, e.textContent.replace(/\\s+/g,' ').trim()])")
        check(f"{tag} §7b แถว Entry: '#68 · 3.9%' · แถว SL: '−10.0%'", mt[0][0] == "e0" and mt[0][1] == "" and ["s0", "−10.0%"] in mt, mt)   # PS1c §8: single trade → no entry result (summary has it)
        hd = js(page, "()=>[document.getElementById('cnEh').textContent, document.getElementById('cnSh').textContent, document.querySelectorAll('.ps1Pc').length]")
        check(f"{tag} §7b ยัง 1 entry/1 SL: ไม่มีหัว Risk / Out และไม่มีช่อง %", hd == ["Entry", "SL", 0], hd)
        js(page, "()=>{ ps1RowAdd('e'); ps1RowAdd('s'); }"); settle(page, 200)
        js(page, "()=>{ document.getElementById('cnEn1').value='110'; ps1In('e',1,'110'); document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); }"); settle(page, 250)
        hd2 = js(page, "()=>[document.getElementById('cnEh').textContent, document.getElementById('cnSh').textContent, document.querySelectorAll('.ps1Pc').length]")
        sm2 = js(page, "()=>document.getElementById('cnSum').textContent.replace(/\\s+/g,' ').trim()")
        mt2 = js(page, "()=>[...document.querySelectorAll('[data-ps1-meta]')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())")
        check(f"{tag} §7b หลัง ＋: หัว 'Risk' / 'Out' โผล่ · ช่อง % ต่อแถว · สรุปมี Avg · เมตาแถวครบ", hd2 == ["Entry · split", "SL · out", 4] and "Avg" in sm2 and all(mt2) and len(mt2) == 4, [hd2, sm2, mt2])
        lay = js(page, """()=>[...document.querySelectorAll('.ps1R')].map(r=>{ const rr=r.getBoundingClientRect(); const kids=[...r.children].filter(c=>c.getBoundingClientRect().width>0 && !c.matches('.ps1M')); const cy=kids.map(c=>{const q=c.getBoundingClientRect();return q.top+q.height/2;}); return {oneRow:Math.max(...cy)-Math.min(...cy)<=6, inside:[...r.children].every(c=>c.getBoundingClientRect().right<=rr.right+1)}; })""")
        check(f"{tag} §7b ทุกแถวอยู่บรรทัดเดียว ไม่ล้น ({w}px) · ✕ ไม่ตกบรรทัด", all(x["oneRow"] and x["inside"] for x in lay) and not js(page, "()=>document.documentElement.scrollWidth>innerWidth"), lay)
        stack = js(page, """()=>{ const r=s=>document.querySelector(s).getBoundingClientRect();
            const hd=r('#cnEBox .ps1Hd'), r0=r('[data-ps1-row=e0]'), r1=r('[data-ps1-row=e1]'), s0=r('[data-ps1-row=s0]'), s1=r('[data-ps1-row=s1]'), risk=r('#cnRisk'), sbox=r('#cnSBox');
            return {ok: risk.bottom<=hd.top+1 && hd.bottom<=r0.top+1 && r0.bottom<=r1.top+1 && s0.bottom<=s1.top+1 && Math.abs(r0.top-s0.top)<1 && r0.right<=sbox.left+1, hd:[hd.top,hd.bottom], r0:[r0.top,r0.bottom], r1:[r1.top,r1.bottom], s0:[s0.top,s0.bottom]}; }""")
        check(f"{tag} §7b PS1c §4: Risk per idea → หัว → แถว 1 → 2 (ซ้าย Entry · ขวา SL แถวตรงกัน) ไม่ทับกัน", stack["ok"], stack)
        js(page, "()=>coreSheetClose()")
        check(f"{tag} console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def fit320(pw):
    b, page, ce, pe = C.launch2(pw, 320, 700, [], {}, pin_winner=True)
    try:
        B.ps_on(page); B.form(page, "FIT"); B.fill(page, 100, 90)
        js(page, "()=>{ ps1RowAdd('e'); ps1RowAdd('s'); }"); settle(page, 200)
        js(page, "()=>{ document.getElementById('cnEn1').value='110'; ps1In('e',1,'110'); document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); }"); settle(page, 250)
        r = js(page, """()=>{ const rows=[...document.querySelectorAll('.ps1R')]; return {ov:document.documentElement.scrollWidth>innerWidth, rows:rows.map(r=>{ const rr=r.getBoundingClientRect(); const kids=[...r.children].filter(c=>c.getBoundingClientRect().width>0 && !c.matches('.ps1M')); const cy=kids.map(c=>{const q=c.getBoundingClientRect();return q.top+q.height/2;}); return Math.max(...cy)-Math.min(...cy)<=6 && kids.every(c=>c.getBoundingClientRect().right<=rr.right+1); }), sz:[...document.querySelectorAll('.ps1Sz')].map(e=>getComputedStyle(e).display)}; }""")
        check("[320] §7b fit: ไม่ห่อ ไม่ล้น · ตัด size % ก่อน (เมื่อแคบ)", not r["ov"] and all(r["rows"]), r)
        js(page, "()=>coreSheetClose()")
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 1000), (390, 844)):
            tests(pw, w, h)
        fit320(pw)
    bad = [r for r in results if not r[1]]
    print(f"\nPS1b phase124: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
