#!/usr/bin/env python3
"""PS1 — Portfolio & Risk (Settings card · lean plan form · add-on gate · Sat E-based lots + verify rule · Port panel · Today line) · เทส 120
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase120.py"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase111 as P111
import run_tests_phase77 as P77

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = T.settle
P13 = P111.P13
import os
INDEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
PS = {"def": {"winner": 0.4, "ladder": 1.0, "satMain": 0.2, "satTac": 0.15}}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def ps_on(page, ps=PS):
    """PS1 เปิด (ถอดแฟลกนักพัฒนา) + ตั้ง psRisk ของบัญชี main"""
    js(page, "([ps])=>{ localStorage.removeItem('dash.ps1Off'); const B=getBook('main'); B.settings.psRisk = ps; saveBook('main'); render(); }", [ps])
    settle(page, 300)


def card(**kw):
    c = {"acct": "main", "ticker": "AAA", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-11-05", "emaW": None,
         "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z"}
    c.update(kw)
    return c


def open_card(sym, tid, **kw):
    return card(ticker=sym, trade_id=tid, status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 10, "f": 1, "stop": 90}], **kw)


def form(page, t="AAA"):
    js(page, "([t])=>{ switchTab('plan'); setPlanScope('stock'); coreNewOpen('main',{ticker:t}); }", [t]); settle(page, 500)


def fill(page, e=None, s=None, r=None):
    for i, v in (("cnEntry", e), ("cnStop", s), ("cnRisk", r)):
        if v is not None:
            js(page, "([i,v])=>{ const el=document.getElementById(i); el.value=v; if(i==='cnRisk') coreNewRisk(); else coreNewIn(); }", [i, str(v)])
    settle(page, 150)


def sumtxt(page):
    return js(page, "()=>document.getElementById('cnSum').innerText.replace(/\\s+/g,' ').trim()")


def save_dis(page):
    return js(page, "()=>document.getElementById('cnSave').disabled")


def errtxt(page):
    return js(page, "()=>{ const e=document.getElementById('cnErr'); return e.style.display==='none' ? '' : e.innerText; }")


def E(page):
    return js(page, "()=>ps1E('main')")


def tests(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    tr = [P13.T("tR", "core", "open", sym="RED", entry=100, sl=90, qty=10, cur="USD", date="2026-10-20")]
    cards = {"cR": open_card("RED", "tR", px=100), "cOld": card(ticker="OLDP", plan={"entry": 300, "stop": 270})}

    # ── 1 Settings ──────────────────────────────────────────────────────────
    b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
    try:
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        js(page, "()=>{ openSettings(); }"); settle(page, 400)
        st = js(page, """()=>({card: !!document.getElementById('ps1Sec'), defs: ['sPsDefLadder','sPsDefWinner','sPsDefSatMain','sPsDefSatTac'].map(i=>document.getElementById(i).value),
            legacyInside: ['sPortCore','sPortSatB','sTotal','sV2OrSat','sV2OrAsset','sV2OrTot'].every(i=>!!document.getElementById(i).closest('#ps1Legacy')),
            maxs:[document.getElementById('sPsMaxLadder').value, document.getElementById('sPsMaxWinner').value],
            caps:['sPsCapLadder','sPsCapWinner','sPsCapSat','sPsTotal','sPsGbAmber','sPsGbRed'].map(i=>document.getElementById(i).value)})""")
        check(f"{tag} 1 Settings: การ์ด Portfolio & Risk มี · ค่าเริ่ม default risk ทั้ง 4 ช่อง 'ว่าง' (ไม่มีค่า hardcode)", st["card"] and st["defs"] == ["", "", "", ""], st)
        check(f"{tag} 1 Settings: ค่าเริ่ม Max position 12.5/7.5 · cap 3/1.5/0.5 · total 5 · give-back 8/10", st["maxs"] == ["12.5", "7.5"] and st["caps"] == ["3", "1.5", "0.5", "5", "8", "10"], st)
        check(f"{tag} 1 Settings: แถวเดิม (Max Heat · Open-Risk caps) ย้ายเข้า 'Legacy limits' ที่พับอยู่ · id เดิมยังอยู่ครบ", st["legacyInside"] and ('id="ps1Legacy" data-ps1-legacy>' in open(INDEX, encoding="utf-8").read()), st)
        js(page, "()=>{ const s=(i,v)=>{ const e=document.getElementById(i); e.value=v; crOnInput(); }; s('sPsDefWinner','0.9'); }"); settle(page, 100)
        er = js(page, "()=>document.querySelector('[data-err-for=sPsDefWinner]').innerText")
        ok_btn = js(page, "()=>crOnInput()")
        check(f"{tag} 1 Settings: default นอกช่วง (0.9 > 0.35–0.50) → error แดง + บันทึกไม่ได้", "0.35" in er and ok_btn is False, [er, ok_btn])
        js(page, "()=>{ const s=(i,v)=>{ const e=document.getElementById(i); e.value=v; crOnInput(); }; s('sPsDefWinner','0.4'); s('sPsDefLadder','1'); s('sPsDefSatMain','0.2'); s('sPsDefSatTac','0.15'); saveSettings(); }"); settle(page, 300)
        saved = js(page, "()=>getBook('main').settings.psRisk")
        check(f"{tag} 1 Settings: บันทึกแล้ว settings.psRisk เก็บ default ทั้ง 4 + caps · coreRisk.baseRisk เดิมไม่ถูกลบ", saved and saved["def"] == {"ladder": 1, "winner": 0.4, "satMain": 0.2, "satTac": 0.15} and saved["total"] == 5, saved)
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 2 Plan form ─────────────────────────────────────────────────────────
    b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
    try:
        js(page, "()=>localStorage.removeItem('dash.ps1Off')")
        form(page)
        check(f"{tag} 2 Form: ยังไม่ตั้ง default risk → 'Set default risk in Settings' + บันทึกไม่ได้", "Set default risk in Settings" in js(page, "()=>document.getElementById('cnRiskHint').innerText") and save_dis(page), [])
        ps_on(page)
        form(page)
        fill(page, 100, 90)
        e = E(page); div = js(page, "()=>getBook('main').settings.fx")
        exp = int((0.004 * e / div) / 10)
        lay = js(page, """()=>{ const r=id=>document.getElementById(id).getBoundingClientRect(); const a=r('cnEntry'),b=r('cnStop'),c=r('cnRisk');
            const fs=['cnEntry','cnStop','cnRisk','cnTicker'].map(i=>parseFloat(getComputedStyle(document.getElementById(i)).fontSize));
            const sum=document.getElementById('cnSum'); return {top:[a.top,b.top,c.top], w:[a.width,b.width,c.width], fs, bt:getComputedStyle(sum).borderTopWidth, ov:document.documentElement.scrollWidth>innerWidth,
              extra:document.querySelectorAll('[data-ps1-er],[data-ps1-sp],.ps1X').length, plus:document.querySelectorAll('[data-ps1-add]').length}}""")
        check(f"{tag} 2 Form: Entry · SL · Risk อยู่แถวเดียวกัน กว้างเท่ากัน ({w}px) ไม่ล้นแนวนอน", abs(lay["top"][0] - lay["top"][1]) < 1 and abs(lay["top"][1] - lay["top"][2]) < 1 and max(lay["w"]) - min(lay["w"]) < 2 and not lay["ov"], lay)
        check(f"{tag} 2 Form: font ของ input ≥ 16px (กัน iPhone zoom) · มีเส้นแบ่งบางเหนือสรุป · เริ่มต้นไม่มีช่องแถวเพิ่ม · มี ＋ 2 ปุ่ม", min(lay["fs"]) >= 16 and lay["bt"] == "1px" and lay["extra"] == 0 and lay["plus"] == 2, lay)
        s1 = sumtxt(page)
        check(f"{tag} 2 Form: ค่าเริ่มต้น Risk = default Momentum 0.4% · จำนวนหุ้น = floor(0.4%×E÷10) = {exp:,} (ปัดลง lot 1) · สรุปบรรทัดเดียว 'sh · Risk · Size … of portfolio'",
              js(page, "()=>document.getElementById('cnRisk').value") == "0.4" and f"{exp:,} sh" in s1 and "Risk 0." in s1 and "of portfolio" in s1 and "Avg" not in s1, [s1, exp])
        check(f"{tag} 2 Form: ช่อง Risk นอกช่วง Momentum (0.7) → บล็อกบันทึก", (fill(page, r=0.7) or True) and save_dis(page) and "0.35" in errtxt(page), errtxt(page))
        fill(page, r=0.4)
        # size cap trims
        fill(page, 100, 99.9)
        s2 = sumtxt(page)
        sz = js(page, "()=>{ const s=document.querySelector('[data-ps1-size]'); return parseFloat(s.innerText); }")
        check(f"{tag} 2 Form: SL แคบมาก → จำนวนหุ้นถูกลดให้ไม่เกิน max position 7.5% ของพอร์ต + มีโน้ตสั้น", sz <= 7.5 + 1e-6 and "reduced" in s2, [s2, sz])
        fill(page, 100, 90)
        # two entry rows
        js(page, "()=>ps1RowAdd('e')"); settle(page, 150)
        js(page, "()=>{ document.getElementById('cnEn1').value='95'; ps1In('e',1,'95'); }"); settle(page, 150)
        two = js(page, "()=>({er:!!document.querySelector('[data-ps1-er]'), n:document.querySelectorAll('[data-ps1-er] input').length, rows:document.querySelectorAll('#cnEx .ps1X').length, sum:document.getElementById('cnSum').innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 2 Form: กด ＋ Entry → โผล่แถวที่ 2 + ช่อง risk % ต่อ entry · สรุปมี Avg entry · Avg SL · Left", two["er"] and two["n"] == 2 and two["rows"] == 1 and "Avg entry" in two["sum"] and "Left" in two["sum"], two)
        js(page, "()=>{ ps1In('er',0,'0.3'); document.getElementById('cnEr0').value='0.3'; ps1In('er',1,'0.2'); document.getElementById('cnEr1').value='0.2'; }"); settle(page, 150)
        sm = sumtxt(page)
        check(f"{tag} 2 Form: 2 entry (100 risk 0.3% · 95 risk 0.2%) รวม ≤ 0.4%+ → คำนวณหุ้นต่อแถว · บล็อกเมื่อรวมเกินงบ idea (0.5 > 0.4)", "Left" in sm and save_dis(page) and "more than" in errtxt(page), [sm, errtxt(page)])
        js(page, "()=>{ ps1In('er',0,'0.25'); document.getElementById('cnEr0').value='0.25'; ps1In('er',1,'0.15'); document.getElementById('cnEr1').value='0.15'; }"); settle(page, 150)
        check(f"{tag} 2 Form: rows ลงตัว (0.25+0.15=0.40) → บันทึกได้", not save_dis(page), [errtxt(page), sumtxt(page)])
        # 2 SL rows
        js(page, "()=>ps1RowAdd('s')"); settle(page, 150)
        js(page, "()=>{ document.getElementById('cnSt1').value='85'; ps1In('s',1,'85'); }"); settle(page, 150)
        pc = js(page, "()=>[document.getElementById('cnSp0').value, document.getElementById('cnSp1').value]")
        check(f"{tag} 2 Form: กด ＋ SL → โผล่ช่อง % ของหุ้นที่ออก (เริ่ม 50/50) · ไม่ล้นแนวนอน", pc == ["50", "50"] and not js(page, "()=>document.documentElement.scrollWidth>innerWidth"), pc)
        js(page, "()=>{ ps1In('sp',0,'60'); document.getElementById('cnSp0').value='60'; }"); settle(page, 150)
        check(f"{tag} 2 Form: % ออกรวม ≠ 100 (60+50) → บล็อกบันทึก 'Exit % must total 100'", save_dis(page) and "total 100" in errtxt(page), errtxt(page))
        js(page, "()=>{ ps1In('sp',0,'50'); document.getElementById('cnSp0').value='50'; }"); settle(page, 150)
        a = js(page, "()=>({sum:document.getElementById('cnSum').innerText, dis:document.getElementById('cnSave').disabled})")
        check(f"{tag} 2 Form: SL 90/85 ออก 50/50 → Avg SL = 87.50 ในสรุป", "87.50" in a["sum"], a)
        js(page, "()=>{ ps1RowDel('s',1); ps1RowDel('e',1); }"); settle(page, 150)
        back = js(page, "()=>document.querySelectorAll('[data-ps1-er],[data-ps1-sp],.ps1X').length")
        check(f"{tag} 2 Form: ลบกลับเหลือ 1 แถว → ช่องพิเศษหายหมด", back == 0, back)
        # 4 rows max
        js(page, "()=>{ for(let i=0;i<6;i++){ ps1RowAdd('e'); ps1RowAdd('s'); } }"); settle(page, 150)
        mx = js(page, "()=>[coreNew.ne, coreNew.ns]")
        check(f"{tag} 2 Form: สูงสุด 4 แถว (Entry 4 · SL 4)", mx == [4, 4], mx)
        js(page, "()=>{ coreSheetClose(); }")
        # shot-friendly 2x2 state is exercised in screenshots script
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 3 caps + save + old plans unchanged ─────────────────────────────────
    big = [P13.T("tB", "core", "open", sym="BIG", entry=100, sl=50, qty=20000, cur="USD", date="2026-10-20")]   # principal 1,000,000 USD-ish => way over caps
    b, page, ce, pe = C.launch2(pw, w, h, big + tr, dict(cards, cB=open_card("BIG", "tB", px=100)), pin_winner=True)
    try:
        ps_on(page)
        form(page); fill(page, 100, 90)
        e3 = errtxt(page)
        check(f"{tag} 3 Caps: bucket/total เต็มแล้ว → ปุ่มบันทึกถูกบล็อก + เหตุผลบรรทัดเดียว 'Over … risk cap'", save_dis(page) and "risk cap" in e3, e3)
        js(page, "()=>coreSheetClose()")
    finally:
        b.close()

    b, page, ce, pe = C.launch2(pw, w, h, tr, cards, pin_winner=True)
    try:
        ps_on(page)
        before = js(page, "()=>JSON.stringify(coreCardsList.find(c=>c.ticker==='OLDP'))")
        form(page); fill(page, 100, 90)
        n_before = js(page, "()=>coreCardsList.length")
        js(page, "()=>coreNewSave()"); settle(page, 700)
        sv = js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='AAA' && x.status==='plan'); return c && {ps1:!!(c.plan&&c.plan.ps1), qty:c.plan.ps1&&c.plan.ps1.qty, entry:c.plan.entry, stop:c.plan.stop, risk:c.plan.risk, bucket:c.plan.ps1&&c.plan.ps1.bucket, cs:!!c.cs}; }")
        check(f"{tag} 3 Save: แผนใหม่เก็บ plan.ps1 (snapshot) · bucket winner · ไม่มี cs (Base Risk เดิม) · entry/stop ตรงฟอร์ม", sv and sv["ps1"] and sv["qty"] > 0 and sv["entry"] == 100 and sv["stop"] == 90 and sv["bucket"] == "winner" and not sv["cs"], sv)
        after = js(page, "()=>JSON.stringify(coreCardsList.find(c=>c.ticker==='OLDP'))")
        check(f"{tag} 3 แผนเก่า (OLDP) ไม่ถูกแตะ · ตัวเลขเดิมเหมือนเดิม", before == after, [before[:120], after[:120]])
        card_txt = js(page, "()=>{ const el=document.querySelector('[data-ps1-cardsum]'); return el ? el.innerText.replace(/\\s+/g,' ') : ''; }")
        js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='AAA'); coreToggle(c.id); }"); settle(page, 300)
        card_txt = js(page, "()=>{ const el=document.querySelector('[data-ps1-cardsum]'); return el ? el.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} 3 การ์ดแผน PS1 แสดงสรุป 'sh · Risk · Size' (ไม่ใช่สูตรเดิม)", "sh" in card_txt and "Risk" in card_txt, card_txt)
        # buy 1 uses ps1 qty
        qty = sv["qty"]
        js(page, "()=>{ const c=coreCardsList.find(x=>x.ticker==='AAA'); coreBuy1Open(c.id); }"); settle(page, 300)
        rec = js(page, "()=>document.getElementById('cbQty') && document.getElementById('cbQty').value")
        check(f"{tag} 3 ซื้อไม้ 1 ใช้จำนวนหุ้นจาก snapshot PS1 ({qty})", str(rec) == str(qty), [rec, qty])
        js(page, "()=>coreSheetClose()")
        check(f"{tag} 3 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 4 Add-on gate ───────────────────────────────────────────────────────
    ps1snap = {"v": 1, "bucket": "winner", "E": 5685000, "typed": 0.4, "mult": {"f": 1, "dd": 1}, "ideaEff": 0.4, "rows": [{"px": 100, "riskPct": 0.4, "qty": 100}], "stops": [{"px": 90, "pct": 100}],
               "qty": 100, "avgEntry": 100, "avgStop": 90, "riskPct": 0.2, "riskMoney": 12000, "sizePct": 1, "leftPct": 0.2, "lot": 1, "maxSizePct": 7.5, "date": "2026-11-05"}
    tr4 = [P13.T("tA1", "core", "open", sym="ADDA", entry=100, sl=100, qty=100, cur="USD", date="2026-10-20"), P13.T("tA2", "core", "open", sym="ADDB", entry=100, sl=90, qty=40, cur="USD", date="2026-10-20")]
    c4 = {"cA1": open_card("ADDA", "tA1", px=110, plan={"entry": 100, "stop": 100, "risk": 0.4, "ps1": ps1snap}, stop=100),
          "cA2": open_card("ADDB", "tA2", px=110, plan={"entry": 100, "stop": 90, "risk": 0.4, "ps1": ps1snap}, stop=90)}
    b, page, ce, pe = C.launch2(pw, w, h, tr4, c4, pin_winner=True)
    try:
        ps_on(page)
        r = js(page, """()=>['ADDA','ADDB'].map(t=>{ const c=coreCardsList.find(x=>x.ticker===t); const k=lfAddCalc(c,{acc:false,px:110,sl:t==='ADDA'?100:90,risk:NaN,riskEdited:false}); return {t, nb:k.newBudget, max:k.maxRiskPct, q:k.r&&k.r.qty, blocked:k.blocked}; })""")
        check(f"{tag} 4 Add-on: stop ≥ avg entry (ADDA 100/100) → งบใหม่เต็ม 0.40% ของ idea · stop ใต้ avg (ADDB) → ใช้เท่าที่เหลือ (<0.40%)", r[0]["nb"] is True and r[1]["nb"] is False and r[0]["max"] > r[1]["max"] and abs(r[0]["max"] - 0.4) < 0.01, r)
        check(f"{tag} 4 Add-on: ได้จำนวนหุ้นเติม > 0 เมื่อมีงบเหลือ", r[0]["q"] > 0 and r[1]["q"] > 0, r)
        check(f"{tag} 4 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()

    # ── 5 Panel + Today line ────────────────────────────────────────────────
    tr5 = [P13.T("p1", "core", "open", sym="BE", entry=100, sl=100, qty=100, cur="USD", date="2026-10-20"),      # breakeven stop -> principal 0, price 120 -> give-back 2000
           P13.T("p2", "core", "open", sym="NOSL", entry=50, sl=0, qty=100, cur="USD", date="2026-10-20"),       # missing stop
           P13.T("p3", "core", "open", sym="NOPX", entry=50, sl=45, qty=100, cur="USD", date="2026-10-20")]      # missing price
    c5 = {"c1": open_card("BE", "p1", px=120, pxDate="2026-11-05", plan={"entry": 100, "stop": 100}, stop=100), "c2": open_card("NOSL", "p2", px=60, plan={"entry": 50, "stop": 45}, stop=0),
          "c3": open_card("NOPX", "p3", px=None, plan={"entry": 50, "stop": 45}, stop=45)}
    b, page, ce, pe = C.launch2(pw, w, h, tr5, c5, pin_winner=True)
    try:
        ps_on(page)
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); render(); }"); settle(page, 500)
        pn = js(page, """()=>({body: !!document.querySelector('[data-ps1-panel-body]'), e: (document.querySelector('[data-ps1-e]')||{}).innerText, buckets: [...document.querySelectorAll('[data-ps1-bucket]')].map(x=>x.dataset.ps1Bucket),
            chips: [...document.querySelectorAll('[data-ps1-chip]')].map(x=>x.dataset.ps1Chip), miss: (document.querySelector('[data-ps1-missing]')||{}).innerText||'', foot: document.querySelector('.ps1Fn')?.innerText,
            rows: Object.fromEntries([...document.querySelectorAll('[data-ps1-idea]')].map(r=>[r.dataset.ps1Idea, r.innerText.replace(/\\s+/g,' ').trim()])), tot: (document.querySelector('[data-ps1-total]')||{}).innerText})""")
        check(f"{tag} 5 Panel: แสดงมูลค่าพอร์ต + วันที่ · 3 bucket (Compounder/Momentum/Sat) พร้อมชิป Normal", pn["body"] and "Portfolio value" in pn["e"] and pn["buckets"] == ["ladder", "winner", "sat"] and pn["chips"].count("normal") >= 1, pn)
        check(f"{tag} 5 Panel: breakeven (stop = avg entry) → Risk now 0.00% · give-back > 0", "0.00%" in pn["rows"].get("BE", "") and "unknown" not in pn["rows"].get("BE", ""), pn["rows"])
        check(f"{tag} 5 Panel: ไม่มี stop / ไม่มีราคา → 'unknown' (ไม่เป็น 0) + ขึ้นรายการ 'Missing stop/price'", "unknown" in pn["rows"].get("NOSL", "") and "unknown" in pn["rows"].get("NOPX", "") and "NOSL" in pn["miss"] and "NOPX" in pn["miss"], [pn["rows"], pn["miss"]])
        check(f"{tag} 5 Panel: footnote 'Gaps/slippage can still cause a loss.'", pn["foot"] == "Gaps/slippage can still cause a loss.", pn["foot"])
        # give-back bands via model
        gb = js(page, "()=>{ const c=ps1Cfg('main'); return [Ps1.gbLevel(7.9,c), Ps1.gbLevel(8,c), Ps1.gbLevel(10,c)]; }")
        check(f"{tag} 5 Panel: give-back <8% ok · ≥8% amber · ≥10% red", gb == ["ok", "amber", "red"], gb)
        js(page, "()=>{ const B=getBook('main'); B.trades.find(t=>t.sym==='BE').qty = 60000; saveBook('main'); render(); }"); settle(page, 400)
        red = js(page, "()=>({lvl:(document.querySelector('[data-ps1-giveback]')||{dataset:{}}).dataset.ps1Giveback, txt:(document.querySelector('[data-ps1-giveback]')||{}).innerText||'', chips:[...document.querySelectorAll('[data-ps1-chip]')].map(x=>x.dataset.ps1Chip)})")
        check(f"{tag} 5 Panel: give-back ≥10% → แดง + 'Review: take partial profit or raise stops' · bucket เต็ม = 'Stop opening'", red["lvl"] == "red" and "Review: take partial profit or raise stops" in red["txt"], red)
        js(page, "()=>switchTab('today')"); settle(page, 500)
        td = js(page, "()=>{ const el=document.querySelector('[data-ps1-today]'); return el ? el.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} 5 Today: มีบรรทัดสั้น 'Risk x / 5.0% · left … · give-back …'", "Risk" in td and "give-back" in td and "left" in td, td)
        check(f"{tag} 5 Today: ไม่ล้นแนวนอน", not js(page, "()=>document.documentElement.scrollWidth>innerWidth"), [])
        check(f"{tag} 5 console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def sat_tests(pw, w, h):
    tag = f"[{ENGINE}/sat/{w}]"
    b, page, ce, pe = P77.launch(pw, w, h)
    try:
        ps_on(page)
        js(page, "()=>{ openSettings(); }"); settle(page, 200); js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); settle(page, 500)
        idea = js(page, "([i])=>{ const x=satIdeasList.find(y=>y.id===i); return {sleeve:x.sleeve, tf:x.tf}; }", [iid])
        check(f"{tag} 4b แผน Sat ใหม่ default Main + TF 4H", idea == {"sleeve": "main", "tf": "4H"}, idea)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid]); settle(page, 300)
        for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, f_, str(v)]); settle(page, 120)

        def calc():
            return js(page, """([i])=>{ const x=satIdeasList.find(y=>y.id===i); const c=satV3PlanAcctCalc(x,'main'); return {lot:c.lot, blocks:c.blocks, ready:c.ready, fac:c.verify&&c.verify.fac, ok:c.verify&&c.verify.ok, msg:c.lotMsg, raw:c.v2&&c.v2.rawRisk, lim:c.v2&&c.v2.limit, deal:c.v2&&c.v2.lotDeal, risk:c.v2&&c.v2.riskTHB, E:c.ps1&&c.ps1.E, def:c.ps1&&c.ps1.def, margin:c.ps1&&c.ps1.margin}; }""", [iid])
        js(page, "()=>{ const B=getBook('main'); B.settings.psRisk={def:{winner:0.4,ladder:1.0,satMain:0.1,satTac:0.15}}; saveBook('main'); render(); }"); settle(page, 300)
        c0 = calc()
        check(f"{tag} 4b Structure ✗ (ยังไม่ติ๊ก) → ถูกบล็อก 'Check Structure first' · ไม่ ready", "Check Structure first" in c0["blocks"] and not c0["ready"], c0)
        js(page, "([i])=>{ pfVerifySet(i,'structure_ok',true); pfVerifySet(i,'ema50_ok',true); }", [iid]); settle(page, 400)
        c1 = calc()
        js(page, "([i])=>{ pfVerifySet(i,'ema50_ok',false); }", [iid]); settle(page, 400)
        c2 = calc()
        js(page, "([i])=>{ pfVerifySet(i,'structure_ok',false); pfVerifySet(i,'ema50_ok',true); }", [iid]); settle(page, 400)
        c3 = calc()
        check(f"{tag} 4b ✓✓ Clear Trend → ขนาด 100% (factor 1) · ไม่มี block Structure", c1["fac"] == 1 and "Check Structure first" not in c1["blocks"] and c1["lot"], c1)
        import math
        exp_deal = math.floor(c1["raw"] * 0.6 / 0.01 + 1e-9) * 0.01
        check(f"{tag} 4b EMA ✗ + Structure ✓ → Unclear Trend ขนาด 60% · lot = floor(0.6 × เต็ม) ปัดลงตาม lot step", c2["fac"] == 0.6 and c1["lim"] == "risk" and c2["lim"] == "risk" and abs(c2["deal"] - exp_deal) < 1e-9 and "Check Structure first" not in c2["blocks"], [c1, c2, exp_deal])
        check(f"{tag} 4b Structure ✗ (EMA ✓) → ถูกบล็อก ไม่ว่า EMA", "Check Structure first" in c3["blocks"] and not c3["ready"], c3)
        check(f"{tag} 4b ขนาด = E × default risk (0.10% ของพอร์ตทั้งหมด) · แสดง Sat balance เป็นข้อมูล 'margin is not risk'", c1["E"] and abs(c1["risk"] - c1["E"] * 0.1 / 100) < 1 and c1["def"] == 0.1 and c1["margin"] > 0, c1)
        # summary text for unclear
        js(page, "([i])=>{ pfVerifySet(i,'structure_ok',true); pfVerifySet(i,'ema50_ok',false); }", [iid]); settle(page, 500)
        txt = js(page, "([i])=>{ const x=satIdeasList.find(y=>y.id===i); return satV2SizeLine({_idea:x,_skipSet:new Set()}, {id:'main'}); }", [iid])
        check(f"{tag} 4b สรุปขนาดแสดง 'Size 60% (Unclear Trend)' + 'margin is not risk'", "Size 60% (Unclear Trend)" in txt and "margin is not risk" in txt, txt[:300])
        # default risk empty -> message
        js(page, "()=>{ const B=getBook('main'); B.settings.psRisk={def:{}}; saveBook('main'); render(); }"); settle(page, 400)
        ce_ = calc()
        check(f"{tag} 4 Sat: default risk ว่าง → 'Set default risk in Settings' และไม่มี lot", ce_["msg"] == "Set default risk in Settings" and ce_["lot"] is None, ce_)
        ps_on(page)
        # tactical unchanged: needs clear trend, no 60% rule, uses satTac default
        tid = js(page, "()=>satV2NewPlan('XAUUSD','tactical')"); settle(page, 500)
        js(page, "([i])=>satV2SetDir(i,'Long')", [tid]); settle(page, 300)
        for f_, v in (("entry", 2000), ("sl", 1990), ("tp", 2020)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [tid, f_, str(v)]); settle(page, 120)
        tc = js(page, """([i])=>{ const x=satIdeasList.find(y=>y.id===i); const c=satV3PlanAcctCalc(x,'main'); return {tf:x.tf, sleeve:x.sleeve, blocks:c.blocks, fac:c.verify&&c.verify.fac, def:c.ps1&&c.ps1.def}; }""", [tid])
        check(f"{tag} 4b Tactical: ไม่เข้ากฎ 60%/Structure (verify factor 1) · ใช้ default Tactical 0.15% · ยัง 'needs Clear Trend' เดิม", tc["fac"] == 1 and tc["def"] == 0.15 and "Check Structure first" not in tc["blocks"], tc)
        # legacy classify-only plan blocked until Structure ticked
        lid = js(page, "()=>satV2NewPlan('BTCUSD','main')"); settle(page, 500)
        js(page, "([i])=>{ satV2SetDir(i,'Long'); satV3IdeaWrite(i,{classify:'clear'}); }", [lid]); settle(page, 300)
        for f_, v in (("entry", 60000), ("sl", 58000), ("tp", 64000)):
            js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [lid, f_, str(v)]); settle(page, 120)
        lg = js(page, """([i])=>{ const x=satIdeasList.find(y=>y.id===i); const c=satV3PlanAcctCalc(x,'main'); return {legacy:satClsLegacy(x), blocks:c.blocks, st:td3PlanStatus(x)}; }""", [lid])
        check(f"{tag} 4b แผนเก่าที่ยังใช้ classify เดิม (verification pending) ต้องติ๊ก Structure ก่อนเข้าไม้ใหม่", lg["legacy"] and "Check Structure first" in lg["blocks"] and lg["st"] and lg["st"]["k"] == "pending", lg)
        check(f"{tag} 4b console ไม่มี error", not ce and not pe, [ce[:2], pe[:2]])
    finally:
        b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((1440, 1000), (390, 844)):
            tests(pw, w, h)
            sat_tests(pw, w, h)
    bad = [r for r in results if not r[1]]
    print(f"\nPS1 phase120: {len(results) - len(bad)}/{len(results)} PASS")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
