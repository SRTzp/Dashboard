#!/usr/bin/env python3
"""PL1 Step 6 (part 1) — A8: การ์ด Compounder = การ์ด Momentum (strategy 'W') + track:'ladder' · Base Risk 1% ของถัง Compounder · เพดาน 5% ของบัญชี · 40W EMA กรอกเอง · ถัง/DD แยก · เทส 118
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase118.py"""
import json, math
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle, cnt = T.settle, T.cnt
P13 = P111.P13


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def wl(page, t, **kw):
    doc = {"ticker": t, "market": "US", "port": "core", "note": "", "added_at": "2026-10-01T00:00:00Z", "my_thesis": {"why": "w", "exit": "x", "updated_at": "2026-10-01T00:00:00Z"}}
    doc.update(kw)
    js(page, "([t,d])=>wlCol().doc(t).set(d)", [t, doc]); settle(page, 300)


def card(**kw):
    c = {"acct": "main", "ticker": "AAA", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": None,
         "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z",
         "cs": {"eval": None, "date": "2026-10-20", "evalDate": "", "stars": None, "stars_src": "none", "baseRiskPct": 1, "riskAmt": 100, "equity": 1, "used": 0, "budget": 1, "adj": {"ff": 1, "dd": 1}, "capKey": "A"}}
    c.update(kw)
    return c


def plan_tests(pw, w, h):
    tag = f"[{ENGINE}/plan/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        wl(page, "CMPA", ladder_watch=True, ladder_watch_set=True); wl(page, "MOMA", ladder_watch=False)
        P = js(page, "()=>{ const cx = coreCtx('main'); return {tank:cx.tankTHB, lad:cx.ladderPoolTHB, acct:cx.acctTHB, lcash:cx.lCashTHB, cap:cx.cfg.ladderMaxAcctPct, fx:cx.fx}; }")
        P111.open_form(page, "CMPA"); P111.setpx(page, 100, 90)
        bn, fm = P111.banner(page), P111.form(page)
        risk_q = P["lad"] / P["fx"] * 0.01 / 10; cap_q = P["acct"] / P["fx"] * P["cap"] / 100 / 100; cash_q = P["lcash"] / P["fx"] / 100
        exp = math.floor(min(risk_q, cap_q, cash_q))
        check(f"{tag} A8: แผนใหม่ของหุ้น track Compounder → Base 1% ของ 'ถัง Compounder' + เพดาน 5% ของบัญชี ในแบนเนอร์", "Compounder pool" in bn["l1"] and "cap 5% of account" in bn["l1"].replace("5.00%", "5%"), bn)
        check(f"{tag} A8: ขนาดไม้แรก = min(1% ถัง Compounder ÷ (entry−stop), 5% บัญชี, เงินว่างถัง Compounder) = {exp} หุ้น · Risk 1%", fm["qty"].replace(",", "") == str(exp) and abs(float(fm["risk"]) - 1.0) < 1e-3 and fm["save"] is False, [fm, exp, risk_q, cap_q, cash_q])
        P111.open_form(page, "MOMA"); P111.setpx(page, 100, 90)
        bm = P111.banner(page); fq = P111.form(page)
        mexp = math.floor(min(P["tank"] / P["fx"] * 0.01 / 10, P["tank"] / P["fx"] * 0.15 / 100))
        check(f"{tag} A8: หุ้น track Momentum ยังใช้ถัง Momentum ('Momentum pool') ขนาดเดิม", "Momentum pool" in bm["l1"] and "Compounder" not in bm["l1"] and fq["qty"].replace(",", "") == str(mexp), [bm, fq, mexp])
        P111.open_form(page, "CMPA"); P111.setpx(page, 100, 90)
        js(page, "()=>coreNewSave()"); settle(page, 900)
        c = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='CMPA'); return c ? JSON.parse(JSON.stringify(c)) : null; }") or {}
        check(f"{tag} A8: บันทึก → การ์ด strategy 'W' + track 'ladder' · cs.baseRiskPct 1 · ไม่มีฟิลด์ ladder", c.get("strategy") == "W" and c.get("track") == "ladder" and c.get("cs", {}).get("baseRiskPct") == 1 and not c.get("ladder"), c)
        check(f"{tag} A8: บันทึกแล้วสลับไปหน้า Compounder (planScope = ladder) เพื่อให้เห็นการ์ดใหม่", js(page, "()=>planScope") == "ladder", js(page, "()=>planScope"))
        ls = js(page, "()=>{ const a = lfCoreAcc(); return [lfCoreCardsHtml(a, 'winner').includes('CMPA'), lfCoreCardsHtml(a, 'ladder').includes('CMPA')]; }")
        check(f"{tag} A8: การ์ด Compounder ไม่โผล่ในรายการ Momentum · โผล่ในรายการ Compounder", ls == [False, True], ls)
        check(f"{tag} A8: wlTrackOf(CMPA) = ladder · เปลี่ยน track ถูกบล็อกเมื่อมีแผนค้าง", js(page, "()=>wlTrackOf(wlItemOf('CMPA'))") == "ladder" and "still has an open Compounder" in js(page, "()=>wlTrackBlock('CMPA','winner')"), js(page, "()=>wlTrackBlock('CMPA','winner')"))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def pool_status_tests(pw, w, h):
    tag = f"[{ENGINE}/pool/{w}]"
    tr = [P13.T("tM", "core", "open", sym="MOMX", entry=100, sl=90, qty=50, cur="USD", date="2026-10-20"), P13.T("tC", "core", "open", sym="CMPX", entry=100, sl=90, qty=40, cur="USD", date="2026-10-20")]
    cards = {"ccM": card(ticker="MOMX", trade_id="tM", status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 50, "f": 1, "stop": 90}], px=100, emaW=95),
             "ccC": card(ticker="CMPX", track="ladder", trade_id="tC", status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 40, "f": 1, "stop": 90}], px=100, emaW40=98),
             "ccL": card(ticker="OLDL", strategy="L", plan=None, ladder={"levels": [{"px": 50, "status": "wait"}], "sl": 45, "budgetPct": 0.1, "budgetTHB": 1000, "split": [1]}, status="plan", trade_id=None)}
    b, page, ce, pe = P111.core(pw, w, h, tr, cards)
    try:
        r = js(page, """()=>{ const cx = coreCtx('main'), A = 'main'; return {w:cx.wCost, c:cx.cCost, wpool:ddPoolOfCard(coreCardsList.find(c=>c.id==='ccM')), cpool:ddPoolOfCard(coreCardsList.find(c=>c.id==='ccC')),
          ladTrades:[...ddLadderTradeIds(A)], trk:coreCardsList.map(c=>[c.id, coreTrackOfCard(c)]), split:cx.split ? [cx.split.w, cx.split.lHeld] : null}; }""")
        check(f"{tag} A8: ทุนที่ถือแยกถัง — Momentum ถือเฉพาะ MOMX (50×100×33) · Compounder ถือ CMPX (40×100×33) · DD bucket ของการ์ด Compounder = ladder", abs(r["w"] - 50 * 100 * 33) < 1 and abs(r["c"] - 40 * 100 * 33) < 1 and r["wpool"] == "winner" and r["cpool"] == "ladder" and r["ladTrades"] == ["tC"], r)
        check(f"{tag} A8: split.lHeld รวมทุนการ์ด Compounder (ถังเดียวกับบันได) · เงินว่าง Momentum ไม่ถูกหักด้วยทุน Compounder", r["split"] and abs(r["split"][1] - 40 * 100 * 33) < 1 and abs(r["split"][0] - 50 * 100 * 33) < 1, r["split"])
        st = js(page, """()=>{ const cx = coreCtx('main'); const m = coreView(coreCardsList.find(c=>c.id==='ccM'), cx), c = coreView(coreCardsList.find(c=>c.id==='ccC'), cx);
          return {m:[m.st.status, m.ema], c:[c.st.status, c.ema], cF:c.F.f, cTank:coreCxFor(coreCardsList.find(x=>x.id==='ccC'), cx).tankTHB === cx.ladderPoolTHB}; }""")
        check(f"{tag} A8: สถานะ — Momentum px 100 > EMA10 95 = green · Compounder px 100 > 40W EMA 98 = green (ema ใช้ emaW40)", st["m"] == ["green", 95] and st["c"] == ["green", 98] and st["cTank"], st)
        js(page, "()=>glWrite && 0"); 
        js(page, "()=>{ const c = coreCardsRaw.find(x=>x.id==='ccC'); c.px = 97; coreApplyPx(); }")
        y = js(page, "()=>{ const v = coreView(coreCardsList.find(c=>c.id==='ccC'), coreCtx('main')); return [v.st.status, coreCardHtml(v, coreCtx('main')).includes('40W EMA'), coreCardHtml(v, coreCtx('main')).includes('EMA10')]; }")
        check(f"{tag} A8: ปิด 97 < 40W EMA 98 → 🟡 'ปิดใต้ 40W EMA · งดเพิ่มไม้' (ไม่มีคำว่า EMA10 บนการ์ด Compounder)", y == ["yellow", True, False], y)
        js(page, "()=>{ const c = coreCardsRaw.find(x=>x.id==='ccC'); c.px = 85; coreApplyPx(); }")
        rd = js(page, "()=>coreView(coreCardsList.find(c=>c.id==='ccC'), coreCtx('main')).st.status")
        check(f"{tag} A8: ปิด 85 < Stop 90 → 🔴 (ต่ำกว่า Stop ชนะ 40W EMA)", rd == "red", rd)
        js(page, "()=>{ const c = coreCardsRaw.find(x=>x.id==='ccC'); c.px = 97; c.emaW40 = null; coreApplyPx(); }")
        e0 = js(page, "()=>{ const v = coreView(coreCardsList.find(c=>c.id==='ccC'), coreCtx('main')); return [v.st.status, v.ema, coreCardHtml(v, coreCtx('main')).includes('Stop อย่างเดียว')]; }")
        check(f"{tag} A8: ไม่กรอก 40W EMA → สถานะจาก Stop อย่างเดียว (px 97 > Stop 90 = green) · การ์ดบอก 'ใช้ Stop อย่างเดียว'", e0 == ["green", None, True], e0)
        capp = js(page, """()=>{ const pc = Object.assign({}, coreCardsList.find(c=>c.id==='ccC'), {id:'ccP', status:'plan', trade_id:null, lots:[], plan:{entry:100, stop:90}}); coreCardsList.push(pc);
          const cx = coreCtx('main'), v = coreView(pc, cx), h = coreCardHtml(v, cx); coreCardsList.pop(); return [/เพดาน 5% ของบัญชี/.test(h), /เพดานไม้แรก/.test(h)]; }""")
        check(f"{tag} A8: การ์ดแผน Compounder โชว์เพดาน '5% ของบัญชี' แทน 'เพดานไม้แรก x%' (เหมือน Momentum โชว์เพดานของมัน)", capp == [True, False], capp)
        # หน้าต่างราคา: ช่อง 40W EMA เก็บ emaW40
        js(page, "()=>corePxOpen('ccC')"); settle(page, 300)
        lab = js(page, "()=>(document.querySelector('[data-cpx-ema40]')||{}).value === undefined ? null : document.querySelector('[data-cpx-ema40]').closest('.ccF').querySelector('label').innerText")
        check(f"{tag} A8: sheet ราคาของการ์ด Compounder มีช่อง '40W EMA รายสัปดาห์ (ว่างได้)' (กรอกเอง) · การ์ด Momentum ยังเป็น EMA10", lab and "40W EMA" in lab, lab)
        js(page, "()=>{ document.getElementById('cpxPx').value = '101'; document.getElementById('cpxEma').value = '99.5'; corePxIn(); corePxSave(); }"); settle(page, 600)
        sv = js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccC'); return [c.emaW40, c.emaW, c.px]; }")
        check(f"{tag} A8: บันทึกราคา + 40W EMA → emaW40 = 99.5 (emaW เดิมไม่ถูกแตะ)", sv[0] == 99.5 and sv[1] in (None, 0) and sv[2] == 101, sv)
        leg = js(page, "()=>{ const a = lfCoreAcc(); return lfCoreCardsHtml(a, 'ladder').includes('OLDL'); }")
        check(f"{tag} A8: การ์ด strategy 'L' เดิมแสดงเป็นแถว legacy อ่านอย่างเดียวในรายการ Compounder", leg is True, leg)
        d0 = js(page, "()=>JSON.stringify(coreCardsList.find(c=>c.id==='ccL').ladder)")
        check(f"{tag} A8: ข้อมูล ladder เดิมไม่ถูกแตะ", '"sl":45' in d0 and '"budgetTHB":1000' in d0, d0)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def page_tests(pw, w, h):
    tag = f"[{ENGINE}/page/{w}]"
    tr = [P13.T("tM", "core", "open", sym="MOMX", entry=100, sl=90, qty=50, cur="USD", date="2026-10-20"), P13.T("tC", "core", "open", sym="CMPX", entry=100, sl=90, qty=40, cur="USD", date="2026-10-20")]
    cards = {"ccM": card(ticker="MOMX", trade_id="tM", status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 50, "f": 1, "stop": 90}], px=100, emaW=95),
             "ccC": card(ticker="CMPX", track="ladder", trade_id="tC", status="open", lots=[{"n": 1, "date": "2026-10-20", "px": 100, "qty": 40, "f": 1, "stop": 90}], px=100, emaW40=98),
             "ccL": card(ticker="OLDL", strategy="L", plan=None, ladder={"levels": [{"px": 50, "status": "wait"}], "sl": 45, "budgetPct": 0.1, "budgetTHB": 1000, "split": [1]}, status="plan")}
    b, page, ce, pe = P111.core(pw, w, h, tr, cards)
    try:
        js(page, "()=>{ ln1SetMode('lean'); switchTab('plan'); setPlanScope('ladder'); render(); }"); settle(page, 700)
        r = js(page, """()=>({head:(document.querySelector('[data-lf-box] .sumT')||{}).innerText, ch:(document.querySelector('[data-lf-cards] .lf-ch b')||{}).innerText, cards:[...document.querySelectorAll('#corePanel [data-core-card]')].map(e=>e.dataset.coreCard), legacy:[...document.querySelectorAll('[data-lf-legacy-row]')].map(e=>e.innerText.replace(/\\s+/g,' ')), ladderPanel:!!document.getElementById('ladderPanel'), btns:document.querySelectorAll('[data-lf-legacy] button').length, tag:(document.querySelector('[data-core-card=ccC] [data-lf-tag]')||{}).innerText||''})""")
        check(f"{tag} A8: หน้า Compounder (Lean) ใช้กล่องเดียวกับ Momentum: หัว 'Compounder' · 'การ์ด Compounder' · แสดงเฉพาะการ์ด track ladder (ccC) · ไม่มี #ladderPanel", r["head"] == "Compounder" and r["ch"] == "การ์ด Compounder" and r["cards"] == ["ccC"] and r["ladderPanel"] is False, r)
        check(f"{tag} A8: แถวบันไดเดิม (OLDL) = แถวอ่านอย่างเดียว 'plan · stop 45' ไม่มีปุ่ม", len(r["legacy"]) == 1 and "OLDL" in r["legacy"][0] and "stop 45" in r["legacy"][0] and r["btns"] == 0, r)
        check(f"{tag} A8: ป้ายการ์ด Compounder = '… · Compounder'", "Compounder" in r["tag"], r["tag"])
        js(page, "()=>{ setPlanScope('stock'); render(); }"); settle(page, 500)
        m = js(page, """()=>({head:(document.querySelector('[data-lf-box] .sumT')||{}).innerText, cards:[...document.querySelectorAll('#corePanel [data-core-card]')].map(e=>e.dataset.coreCard), legacy:document.querySelectorAll('[data-lf-legacy-row]').length})""")
        check(f"{tag} A8: หน้า Momentum แสดงเฉพาะการ์ด Momentum (ccM) · ไม่มีแถว legacy ladder", m["head"] == "Momentum" and m["cards"] == ["ccM"] and m["legacy"] == 0, m)
        js(page, "()=>{ setPlanScope('ladder'); render(); }"); settle(page, 500)
        js(page, "()=>document.querySelector('[data-lf-newplan]').click()"); settle(page, 600)
        t_ = js(page, "()=>(document.querySelector('.core-sheet h3')||{}).textContent||''")
        check(f"{tag} A8: ＋ แผน ในหน้า Compounder → ฟอร์มแผนใหม่ 'New Compounder plan' (ฟอร์มเดียวกับ Momentum)", t_ == "New Compounder plan", t_)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            plan_tests(pw, w, h); pool_status_tests(pw, w, h); page_tests(pw, w, h)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
