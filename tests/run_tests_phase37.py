#!/usr/bin/env python3
"""DD1 — (0) แก้ R/heat + เบรกชั้น 3 (DD ของถัง) Core + Sat · ปกติ → ลดขนาด → พัก → ฟื้นตัว · เทส 37
mock Firestore · Chromium 1440 + 430 · นาฬิกาปลอม = 2026-10-01 12:00 ไทย (พฤหัส · สัปดาห์เริ่ม 2026-09-27) · timezone Asia/Bangkok
ตัวเลขหลัก (ผู้ใช้ยืนยัน): ถัง Core ฿700,000 · RPT 1.25% (1R = ฿8,750) · ถัง Sat ฿1,040,000 (USD 26,000 × fx 40) · RPT 1.25% (1R = ฿13,000)
ภาพเก็บที่ tests/screenshots/dd1-*.png (strip-reduce · strip-pause · sheet-pause-review · core-weakest · sat-blocked)
รัน: python3 run_tests_phase37.py"""
import json, os, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase24 as p24
import run_tests_phase26 as p26
import run_tests_phase29 as p29
import run_tests_phase33 as p33
import run_tests_phase36 as p36
from run_tests_phase11 import iso
from run_tests_phase27 import js, setup_week, push_trade

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
TODAY = "2026-10-01"
WK = "2026-09-27"          # วันอาทิตย์ต้นสัปดาห์ปัจจุบัน
P14, P7 = "2026-10-15", "2026-10-08"
T = p29.T
txt = p24.txt


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def near(a, b, tol=0.01): return a is not None and abs(a - b) <= tol


# ───────────────────────── เอกสารตั้งต้น ─────────────────────────
def ds0(tank, peak=None, **kw):
    d = {"peak": peak if peak is not None else tank, "baseAt": "2026-09-01", "tank": tank, "stage": "normal", "stageSince": "2026-09-01",
         "pauseUntil": None, "review": None, "recoverDd0": None, "weekly": {}, "rebasedAt": None}
    d.update(kw); return d


def doc37(with_dd=True):
    doc = p24.doc_with(main_trades=[], core_cap=700000, main_market="both")
    for acct in ("main", "fam"):
        b = doc["books"][acct]; s = b["settings"]
        s["fx"] = 40; s["capital"]["core"] = 700000; s["capital"]["satB"] = 26000
        s.setdefault("coreRisk", {}).update({"riskPct": 1.25, "tierA": 10, "tierB": 5, "market": "both"}); s["coreRisk"]["maxLots"] = 6   # CZ1: seed เพดานไม้แรกเดิม 10/5
        s["satRisk"] = {"rpt": 1.25, "rptHi": 2, "newMax": 2}
        if with_dd: s["ddState"] = {"core": ds0(700000), "sat": ds0(26000)}
        b["trades"] = []
    return doc


def launch(pw, w, h, doc=None, cards=None):
    r = p29.launch(pw, w, h, doc if doc is not None else doc37(), cards=cards)
    r[2].evaluate("()=>localStorage.setItem('bkLastBackupAt', String(Date.now()))")
    return r


def fx_core(page):
    p24.set_ff(page, p26.FF_OPEN())


def go_core(page): p24.go_stock(page)


def open_plan(page):
    b = page.locator("#satV3Panel button:has-text('เปิด')")
    if b.count() and page.locator(".ui-plan [data-dd-block], .ui-plan .ui-row").count() == 0: b.first.click()
    page.wait_for_timeout(400)


def go_sat(page): js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(300)


def put_trades(page, acct, trades):
    js(page, "([a,t])=>{ const B=getBook(a); B.trades=t; saveBook(a); render(); }", [acct, trades]); page.wait_for_timeout(350)


def set_dd(page, acct, bucket, st):
    js(page, "([a,b,s])=>{ const B=getBook(a); B.settings.ddState=Object.assign({}, B.settings.ddState||{}, {[b]:s}); saveBook(a); render(); }", [acct, bucket, st]); page.wait_for_timeout(350)


def dd(page, acct, bucket):
    return js(page, """([a,b])=>{ const e=ddEval(a,b); if(!e) return null;
        return {stage:e.stage, ddPct:e.ddPct, sizeFactor:e.sizeFactor, allowNew:e.allowNew, allowLadder:e.allowLadder, pauseUntil:e.pauseUntil, equity:e.equity, peak:e.peak,
                missing:e.missing, recoverR:e.recoverRNow, oneR:e.oneR, reviewDone:e.reviewDone, rebased:e.rebased, rebasedAt:e.rebasedAt, weekly:e.weekly, since:e.next.stageSince, left:e.info.pauseLeftDays}; }""", [acct, bucket])


def persisted(page, acct, bucket):
    return js(page, "([a,b])=>{ const s=getBook(a).settings.ddState; return s && s[b] ? JSON.parse(JSON.stringify(s[b])) : null; }", [acct, bucket])


def db_dd(page, acct, bucket):
    return page.evaluate("([a,b])=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; const s = d.books[a].settings.ddState; return s ? s[b] : null; }", [acct, bucket])


def clear_cards(page):
    page.evaluate("""async ()=>{ const d = window.firebase.__mockDb.__dump(); const col = window.firebase.firestore().collection('users').doc('testuid').collection('coreCards');
        for(const k of Object.keys(d)){ const m = k.match(/^users\\/testuid\\/coreCards\\/(.+)$/); if(m) await col.doc(m[1]).delete(); } }""")
    page.wait_for_timeout(250)


def seed_cards(page, cards):
    for cid, c in cards.items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    page.wait_for_timeout(400)


def closed(id, port="core", pnl=-87500, exit_date="2026-09-25", **kw):
    """ไม้ปิดแล้วที่ได้ P&L = pnl (฿) · core: qty 1000 entry 100 · sat: USD ผ่าน fx 40 (qty 1 × mult 100)"""
    if port == "core":
        q = max(1000, int(abs(pnl) / 50)); ex = 100 + pnl / q
        d = dict(entry=100, sl=90, qty=q, exitPrice=ex, exitDate=exit_date, cur="THB")
    else:
        ex = 2400 + (pnl / 40) / 100
        d = dict(entry=2400, sl=2390, qty=1, mult=100, exitPrice=ex, exitDate=exit_date, cur="USD", sym="XAUUSD")
    d.update(kw)
    return T(id, port, "closed", date="2026-09-10", openedAt="2026-09-10", **d)


def card_ids(page): return list(p24.cards_db(page).keys())


def n_cards(page): return len(p24.cards_db(page))


def n_trades(page, acct="main"): return js(page, "(a)=>getBook(a).trades.length", acct)


def chip(page, bucket, acct=None):
    sel = (f'[data-core-acct="{acct}"] ' if (acct and bucket == "core") else (f'[data-sat-meta] [data-acct="{acct}"] ' if acct else "")) + f'[data-dd-chip="{bucket}"]'
    return txt(page, sel) or ""


def open_sheet(page, acct, bucket):
    js(page, "([a,b])=>ddSheetOpen(a,b)", [acct, bucket]); page.wait_for_selector('.core-sheet [data-core-sheet="dd"]', timeout=3000)


def overflow(page, sels):
    return page.evaluate("""(sels)=>{ const W = window.innerWidth, bad = [];
      sels.forEach(s=>{ const e = document.querySelector(s); if(!e) return; const r = e.getBoundingClientRect();
        if(r.right > W + 1 || r.left < -1 || e.scrollWidth > e.clientWidth + 1) bad.push(s+':'+Math.round(r.left)+'-'+Math.round(r.right)+'/'+e.scrollWidth+'>'+e.clientWidth); });
      if(document.documentElement.scrollWidth > W + 1) bad.push('page:'+document.documentElement.scrollWidth+'>'+W); return bad; }""", sels)


def set_clock(page, iso_s):
    page.evaluate("(iso)=>{ const R = Date, base = R.parse(iso), start = R.now();"
                  " class FD extends R { constructor(...a){ if(a.length===0) super(base + (R.now()-start)); else super(...a); } static now(){ return base + (R.now()-start); } } window.Date = FD; }", iso_s)


# ───────────────────────── (0) แก้ R / heat / ข้อความ PY1 ─────────────────────────
def section0(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        # 0.1 ไม้ใหม่เก็บ sl0 ตอนเข้า
        t = js(page, """()=>makeTradeObject({id:'z1', date:thaiToday(), sym:'XAUUSD', port:'satB', bias:'Long', entry:100, sl:90, qty:1, mult:1, cur:'USD', status:'open'})""")
        check(f"{tag} 0.1 makeTradeObject ไม้ใหม่ (Long entry 100 SL 90) เก็บ sl0 = 90", t.get("sl0") == 90, json.dumps(t.get("sl0")))
        tc = js(page, """()=>makeTradeObject({id:'z2', date:thaiToday(), sym:'AAA', port:'core', bias:'Long', entry:100, sl:92, qty:10, mult:1, cur:'THB', status:'open', fromCard:true})""")
        check(f"{tag} 0.1 ไม้ Core ใหม่เก็บ sl0 ด้วย", tc.get("sl0") == 92, json.dumps(tc.get("sl0")))
        # เลื่อน SL ผ่านฟอร์มแก้ไม้ (Sat open) → sl0 ไม่แตะ → ปิด 120 → R = 2.0
        put_trades(page, "main", [T("s1", "satB", "open", sym="XAUUSD", entry=100, sl=90, qty=1, mult=1, cur="USD", sl0=90, date=TODAY, openedAt=TODAY, bias="Long")])
        js(page, "()=>openTradeEdit('s1','main')"); page.wait_for_timeout(250)
        page.fill("#tSL", "105"); page.wait_for_timeout(100); page.click("#teSaveBtn"); page.wait_for_timeout(300)
        s1 = js(page, "()=>JSON.parse(JSON.stringify(getBook('main').trades.find(x=>x.id==='s1')))")
        check(f"{tag} 0.1 เลื่อน SL 90 → 105 (ฟอร์มแก้ไม้) · sl = 105 · sl0 ยัง 90", s1["sl"] == 105 and s1["sl0"] == 90, json.dumps([s1["sl"], s1.get("sl0")]))
        js(page, "()=>openClosePos('s1','main')"); page.wait_for_timeout(200)
        page.fill("#cpExitPrice", "120"); page.wait_for_timeout(100); js(page, "()=>confirmClosePos()"); page.wait_for_timeout(300)
        r = js(page, "()=>realizedROf(getBook('main').trades.find(x=>x.id==='s1'))")
        check(f"{tag} 0.1 ปิด 120 → R = 2.0 (ไม่ใช่ 4.0 / —)", near(r, 2.0, 1e-9), str(r))
        # ไม้เก่าไม่มี sl0 → พฤติกรรมเดิม (R จาก SL ปัจจุบัน)
        old = js(page, """()=>({a: realizedROf({status:'closed', bias:'Long', entry:100, sl:90, qty:1, mult:1, exitPrice:120, port:'satB', cur:'USD'}),
            b: realizedROf({status:'closed', bias:'Long', entry:100, sl:105, qty:1, mult:1, exitPrice:120, port:'satB', cur:'USD'})})""")
        check(f"{tag} 0.1 ไม้เก่าไม่มี sl0: SL 90 → R 2.0 · SL 105 → R 4.0 (พฤติกรรมเดิม)", near(old["a"], 2.0, 1e-9) and near(old["b"], 4.0, 1e-9), json.dumps(old))
        # Core เก่า: ใช้ Stop แรกใน stopHistory
        seed_cards(page, {"ch": p24.open_card("ch", "tch", ticker="HIST.BK", sl=105, stopHistory=[{"date": "2026-09-15", "from": 90, "to": 105}], px=120, pxDate="2026-09-25", emaW=100)})
        rh = js(page, """()=>realizedROf({id:'tch', port:'core', status:'closed', bias:'Long', entry:100, sl:105, qty:10, mult:1, exitPrice:120, cur:'THB'})""")
        check(f"{tag} 0.1 Core เก่าไม่มี sl0 → ใช้ Stop แรกใน stopHistory (90) → R 2.0", near(rh, 2.0, 1e-9), str(rh))
        # แก้ไม้ plan = อัปเดต sl0 ตาม · เลื่อน SL ของไม้ Core ผ่านการ์ด ไม่แตะ sl0
        put_trades(page, "main", [T("pl", "satB", "plan", sym="XAUUSD", entry=100, sl=90, qty=1, mult=1, cur="USD", sl0=90, date=TODAY, bias="Long")])
        js(page, "()=>openTradeEdit('pl','main')"); page.wait_for_timeout(250)
        page.fill("#tSL", "92"); page.wait_for_timeout(100); page.click("#teSaveBtn"); page.wait_for_timeout(300)
        pl = js(page, "()=>JSON.parse(JSON.stringify(getBook('main').trades.find(x=>x.id==='pl')))")
        check(f"{tag} 0.1 แก้ไม้ plan (SL 90 → 92) → sl0 ตาม = 92", pl["sl"] == 92 and pl["sl0"] == 92, json.dumps([pl["sl"], pl.get("sl0")]))
        clear_cards(page)
        seed_cards(page, {"cm": p24.open_card("cm", "tcm", ticker="MOVE.BK", sl=95, px=120, pxDate="2026-09-25", emaW=100)})
        put_trades(page, "main", [T("tcm", "core", "open", sym="MOVE.BK", entry=100, sl=95, qty=10, sl0=95, date="2026-09-10", openedAt="2026-09-10")])
        js(page, "()=>coreStopOpen('cm')"); page.wait_for_timeout(250)
        page.fill("#csStop", "108"); page.wait_for_timeout(100); js(page, "()=>coreStopSave()"); page.wait_for_timeout(350)
        tm = js(page, "()=>JSON.parse(JSON.stringify(getBook('main').trades.find(x=>x.id==='tcm')))")
        check(f"{tag} 0.1 การ์ด Core เลื่อน Stop 95 → 108 · sl0 ยัง 95", tm["sl"] == 108 and tm["sl0"] == 95, json.dumps([tm["sl"], tm.get("sl0")]))
        # 0.2 heat แถบ Sat: SL เลยทุน = 0
        put_trades(page, "main", [T("h1", "satB", "open", sym="XAUUSD", entry=2400, sl=2410, qty=0.4, mult=100, cur="USD", sl0=2390, date=TODAY, openedAt=TODAY, bias="Short" if False else "Long"),
                                  T("h2", "satB", "open", sym="XAUUSD", entry=2400, sl=2390, qty=0.1, mult=100, cur="USD", sl0=2390, date=TODAY, openedAt=TODAY, bias="Long")])
        hb = js(page, "()=>{ const b=sat7dAcctBase('main'); return {open:b.openRisk, heat:b.heatPct, cap:b.cap, thb: getBook('main').trades.filter(t=>t.status==='open').reduce((a,t)=>a+posOpenRisk(t,40).thb,0)}; }")
        check(f"{tag} 0.2 heat แถบ: ไม้ SL เลยทุน (2410 ≥ 2400) = 0 · รวมเหลือไม้ที่ 2 = ฿4,000 (0.1×10×100×40)", near(hb["open"], 4000, 1e-6) and near(hb["open"], hb["thb"], 1e-6), json.dumps(hb))
        # heat แถบ = heat ใน sheet เติมไม้ (PY1)
        push = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='h2'); t.sl = 2400; saveBook('main'); render(); return true; }"); page.wait_for_timeout(200)
        base_open = js(page, "()=>sat7dAcctBase('main').openRisk")
        check(f"{tag} 0.2 SL ทั้งคู่ถึงทุน/เลยทุน → heat แถบ = 0", near(base_open, 0, 1e-6), str(base_open))
        # 0.3 ข้อความ PY1
        p36.clean(page, "Long"); p36.mk_first(page, sl=2400)
        js(page, "()=>{ const B=getBook('main'); }")
        p36.open_sheet(page); p36.fill(page, e2=2412, sj=2400)
        s = p36.sheet(page)
        check(f"{tag} 0.3 sheet เติมไม้: 'ความเสี่ยงไม้ 1 หลังย้าย SL ร่วม' เป็น ฿ (฿0 · ล็อกกำไร) ไม่มี USD", "฿0" in (s["r1"] or "") and "USD" not in (s["r1"] or ""), json.dumps(s, ensure_ascii=False))
        heat_sheet = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='t1'); return satPyrCalc(t,'main',{broke:true, entry2:2412, slj:2400}).base.openRisk; }")
        check(f"{tag} 0.3 heat ฐานใน sheet = แถบ (ไม้ 1 SL = ทุน → 0)", near(heat_sheet, 0, 1e-6) and near(js(page, "()=>sat7dAcctBase('main').openRisk"), 0, 1e-6), str(heat_sheet))
        js(page, "()=>satPyrClose()")
        # เหตุผลสวน Bias
        js(page, "()=>{ satwWrite('XAUUSD', {bias:'Short'}); }") if False else None
        p36.clean(page, "Long"); p36.mk_first(page, sl=2400)
        page.evaluate("()=>{ const t=getBook('main').trades.find(x=>x.id==='t1'); t.bias='Short'; saveBook('main'); render(); }"); page.wait_for_timeout(250)
        ck = js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='t1'); return satPyrCheck(t,'main'); }")
        want = "สวน Bias สัปดาห์ (ตอนนี้ Long) — เติมไม้ไม่ได้"
        check(f"{tag} 0.3 PF1 — ปุ่มเติมไม้: ไม่มีเหตุผล สวน Bias แล้ว", not any("สวน Bias" in x for x in ck["reasons"]), json.dumps(ck["reasons"], ensure_ascii=False))
        b = p36.btn(page)
        check(f"{tag} 0.3 PF1 — ปุ่มเติมไม้ไม่ถูกบล็อกด้วยสวน Bias", b and "สวน Bias" not in (b["title"] or "") and "สวน Bias" not in (b["why"] or ""), json.dumps(b, ensure_ascii=False))
        check(f"{tag} 0 console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} 0 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── (1–5, 9–11, 13) Core ─────────────────────────
def core_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        fx_core(page); go_core(page)
        # ── 1 Core: ปิดไม้ขาดทุนรวม ฿87,500 (12.5%) → ลดขนาด ×0.5
        put_trades(page, "main", [closed("c1", pnl=-87500)])
        e = dd(page, "main", "core")
        check(f"{tag} 1 Core ปิดขาดทุน ฿87,500 → DD 12.5% · stage reduce · ×0.5", e["stage"] == "reduce" and near(e["ddPct"], 12.5, 1e-6) and e["sizeFactor"] == 0.5 and e["allowNew"] and not e["allowLadder"], json.dumps(e))
        check(f"{tag} 1 บันทึก state ลง settings.ddState.core (ddSync) · stage reduce", (db_dd(page, "main", "core") or {}).get("stage") == "reduce", json.dumps(db_dd(page, "main", "core")))
        c = chip(page, "core", "main")
        check(f"{tag} 1 ชิป 'DD 12.5% · ลดขนาด ×0.5' บนแถบบัญชี Core", "DD 12.5%" in c and "ลดขนาด ×0.5" in c, c)
        bar = txt(page, '[data-dd-bar="core"]') or ""
        check(f"{tag} 1 แถบแจ้ง 1 บรรทัด + ลิงก์ 'รายละเอียด'", "ลดขนาด" in bar and "รายละเอียด" in bar and "งดเปิดบันได L ใหม่" in bar, bar)
        shot(page, f"dd1-strip-reduce-{label}.png", '[data-core-acct="main"]')
        bud = js(page, "()=>{ const cx=coreCtx('main'); const r=coreFirstLotCalc(cx,'TH','A',100,90,1); return {budget:r.budget, full:r.budgetFull, rp:cx.opts.riskPct, base:cx.opts.riskPctBase, ddf:cx.opts.ddFactor}; }")
        check(f"{tag} 1 ไม้ W ใหม่งบเสี่ยง = ฿4,375 (riskPct × 0.5 ส่งเข้า Calc.coreSize)", near(bud["budget"], 4375, 1e-6) and near(bud["rp"], 0.00625, 1e-12) and near(bud["base"], 0.0125, 1e-12) and bud["ddf"] == 0.5, json.dumps(bud))
        lad = js(page, "()=>{ const r=coreCanPlace('main',{tier:'A',fortress:true,thb:{ok:false}},null,false); return {allowed:r.allowed, dd:r.ddBlock, rows:r.rows.filter(x=>x.k==='dd').length}; }")
        check(f"{tag} 1 coreCanPlace: บันไดใหม่ไม่ได้ + เหตุผล 'งดเปิดบันได L ใหม่'", lad["allowed"] is False and "งดเปิดบันได L ใหม่" in lad["dd"] and lad["rows"] == 1, json.dumps(lad, ensure_ascii=False))
        ladE = js(page, "()=>{ const r=coreCanPlace('main',{tier:'A',fortress:true,thb:{ok:false}},null,true); return {dd:r.ddBlock}; }")
        check(f"{tag} 1 แก้แผนบันไดเดิม (isEdit) ไม่โดนเบรก", not ladE["dd"], json.dumps(ladE))
        p33.new_form(page, "LTEST"); p33.fill_fortress(page); page.click("#cnStratL"); page.wait_for_timeout(200)
        er = txt(page, "#cnErr") or ""
        check(f"{tag} 1 ฟอร์มแผน L: ปุ่มบันทึกปิด + เหตุผล DD ในกล่องข้อผิดพลาด", page.locator("#cnSave").first.is_disabled() and "งดเปิดบันได L ใหม่" in er and page.locator('#cnLgates [data-gate="dd"]').count() == 1, er)
        page.click("#cnStratW"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.wait_for_timeout(200)
        er = txt(page, "#cnErr") or ""
        check(f"{tag} 1 ฟอร์มแผน W ใน reduce: ไม่ถูกบล็อกด้วย DD (ลดขนาดเท่านั้น)", "เบรก DD" not in er and not page.locator("#cnSave").first.is_disabled(), er)
        js(page, "()=>coreSheetClose()")

        # ── 2 Core: เพิ่ม unrealized จน DD 20% → พัก 14 วัน
        clear_cards(page)
        seed_cards(page, {
            "cA": p24.open_card("cA", "tA", ticker="AAA.BK", qty=1000, entry=100, sl=105, px=110, pxDate="2026-09-25", emaW=100, tier="A"),
            "cB": p24.open_card("cB", "tB", ticker="BBB.BK", qty=3125, entry=100, sl=75, px=80, pxDate="2026-09-25", emaW=70, tier="A"),
            "cP": p24.card("cP", "main", "PLAN.BK", tier="A", plan={"entry": 100, "stop": 90}, stop=90)})
        set_dd(page, "main", "core", ds0(700000))
        put_trades(page, "main", [closed("c1", pnl=-87500),
                                  T("tA", "core", "open", sym="AAA.BK", entry=100, sl=105, qty=1000, sl0=90, date="2026-09-10", openedAt="2026-09-10"),
                                  T("tB", "core", "open", sym="BBB.BK", entry=100, sl=75, qty=3125, sl0=75, date="2026-09-10", openedAt="2026-09-10")])
        e = dd(page, "main", "core")
        check(f"{tag} 2 เพิ่ม unrealized → equity ฿560,000 · DD 20% · stage pause", e["stage"] == "pause" and near(e["equity"], 560000, 1e-6) and near(e["ddPct"], 20, 1e-6) and e["sizeFactor"] == 0 and not e["allowNew"], json.dumps(e))
        check(f"{tag} 2 พักถึง {P14} (วันนี้ + 14)", e["pauseUntil"] == P14 and e["left"] == 14, json.dumps([e["pauseUntil"], e["left"]]))
        c = chip(page, "core", "main")
        check(f"{tag} 2 ชิป 'พักถึง 15 ต.ค.' (สีแดง)", "พักถึง 15 ต.ค." in c and page.locator('[data-dd-chip="core"].dd-pause').count() >= 1, c)
        check(f"{tag} 2 แถบแจ้ง: พักถึง 15 ต.ค. · ห้ามเปิดไม้ใหม่ · ต้องเขียนทบทวน", all(x in (txt(page, '[data-dd-bar="core"]') or "") for x in ("พักถึง 15 ต.ค.", "ห้ามเปิดไม้ใหม่", "ต้องเขียนทบทวน")), txt(page, '[data-dd-bar="core"]'))
        shot(page, f"dd1-strip-pause-{label}.png", '[data-core-acct="main"]')
        # ไม้แรกใหม่บันทึกไม่ได้
        n0 = n_cards(page)
        p33.new_form(page, "NEWW"); page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.wait_for_timeout(250)
        er = txt(page, "#cnErr") or ""
        want = "เบรก DD: พักถึง 15 ต.ค. — เลื่อน Stop/ขาย/เติมตัวที่กำไรได้"
        check(f"{tag} 2 แผน W ใหม่: ปุ่มบันทึกแผนปิด + เหตุผล '{want}'", page.locator("#cnSave").first.is_disabled() and want in er, er)
        js(page, "()=>coreNewSave()"); page.wait_for_timeout(300)
        check(f"{tag} 2 เรียก coreNewSave() ตรง ๆ ก็ไม่สร้างการ์ด", n_cards(page) == n0, str(n_cards(page)))
        js(page, "()=>coreSheetClose()")
        # การ์ดแผนที่มีอยู่: ปุ่มซื้อไม้ 1 ปิด + เรียกตรง ๆ ไม่เปิด
        bb = js(page, "()=>{ const b=document.querySelector('[data-core-card=\"cP\"] [data-c-buy1]'); return b ? {dis:b.disabled, title:b.title} : null; }")
        check(f"{tag} 2 การ์ดแผน: [บันทึกซื้อไม้ 1] ปิด + เหตุผล", bb and bb["dis"] and want in bb["title"], json.dumps(bb, ensure_ascii=False))
        js(page, "()=>coreBuy1Open('cP')"); page.wait_for_timeout(200)
        check(f"{tag} 2 coreBuy1Open() ตรง ๆ ไม่เปิด sheet ซื้อ", page.locator('.core-sheet [data-core-sheet="buy1"]').count() == 0)
        # เลื่อน Stop ได้
        js(page, "()=>coreStopOpen('cA')"); page.wait_for_timeout(250)
        page.fill("#csStop", "106"); page.wait_for_timeout(100)
        ok_stop = not page.locator("#csSave").first.is_disabled()
        js(page, "()=>coreStopSave()"); page.wait_for_timeout(350)
        check(f"{tag} 2 เลื่อน Stop ทำได้ (105 → 106)", ok_stop and js(page, "()=>getBook('main').trades.find(x=>x.id==='tA').sl") == 106)
        # ขาย/ปิดไม้ได้
        js(page, "()=>openClosePos('tB','main')"); page.wait_for_timeout(200)
        page.fill("#cpExitPrice", "80"); page.fill("#cpQty", "125"); page.wait_for_timeout(100)
        nt = n_trades(page); js(page, "()=>confirmClosePos()"); page.wait_for_timeout(350)
        check(f"{tag} 2 ขาย (ปิดบางส่วน) ทำได้", n_trades(page) == nt + 1 and js(page, "()=>getBook('main').trades.find(x=>x.id==='tB').qty") == 3000)
        # เติม: ตัวที่ Stop ≥ ทุน ได้ · Stop < ทุน ไม่ได้
        ra = js(page, "()=>{ const cx=coreCtx('main'), c=coreCardsList.find(x=>x.id==='cA'); return coreAddBlockReason(coreView(c,cx),cx); }")
        rb = js(page, "()=>{ const cx=coreCtx('main'), c=coreCardsList.find(x=>x.id==='cB'); return coreAddBlockReason(coreView(c,cx),cx); }")
        check(f"{tag} 2 เติมตัวที่ Stop ≥ ทุน (AAA Stop 106 ≥ 100) ทำได้ — ไม่มีเหตุผลบล็อก", ra == "", ra)
        check(f"{tag} 2 ตัวที่ Stop < ทุน (BBB Stop 75 < 100) เติมไม่ได้ + 'เบรก DD: เติมได้เฉพาะตัวที่ Stop ≥ ทุน'", rb == "เบรก DD: เติมได้เฉพาะตัวที่ Stop ≥ ทุน", rb)
        btnB = js(page, "()=>{ const b=document.querySelector('[data-core-card=\"cB\"] [data-c-addbtn]'); return b ? {dis:b.disabled, title:b.title} : null; }")
        btnA = js(page, "()=>{ const b=document.querySelector('[data-core-card=\"cA\"] [data-c-addbtn]'); return b ? {dis:b.disabled} : null; }")
        check(f"{tag} 2 ปุ่ม [เติมไม้] ตัว A เปิด · ตัว B ปิด", btnA and not btnA["dis"] and btnB and btnB["dis"] and "Stop ≥ ทุน" in btnB["title"], json.dumps([btnA, btnB], ensure_ascii=False))
        js(page, "()=>coreSimToggle('cA')"); js(page, "()=>{ coreSimIn('cA','px','112'); coreSimIn('cA','stop','106'); }")
        sim = js(page, "()=>{ const cx=coreCtx('main'), c=coreCardsList.find(x=>x.id==='cA'); const s=coreSimCalc(coreView(c,cx),cx); return {ok:s.ok, blocked:s.blocked||[], qty:s.r&&s.r.qty}; }")
        check(f"{tag} 2 ไม้เติมตัว A คิดขนาดตามกติกาเดิม (ไม่คูณ 0.5 ของ DD) · ไม่ติดบล็อก DD", sim["ok"] and not any("เบรก DD" in x for x in sim["blocked"]), json.dumps(sim, ensure_ascii=False))
        js(page, "()=>coreBuyAddOpen('cB')"); page.wait_for_timeout(200)
        check(f"{tag} 2 coreBuyAddOpen(B) ตรง ๆ ไม่เปิด sheet", page.locator('.core-sheet [data-core-sheet="buyadd"]').count() == 0)
        # บันทึกไม้ย้อนหลังไม่ถูกบล็อก
        js(page, "()=>jBackfillOpen()"); page.wait_for_timeout(250)
        page.select_option("#bfPort", "core"); page.fill("#bfSym", "OLDX"); page.fill("#bfEntry", "100"); page.fill("#bfSl", "90"); page.fill("#bfQty", "10"); page.fill("#bfExit", "110")
        page.fill("#bfDate", "2026-09-20"); page.fill("#bfExitDate", "2026-09-25"); page.wait_for_timeout(200)
        nt = n_trades(page); can = not page.locator("#bfSave").first.is_disabled()
        if can: page.click("#bfSave")
        page.wait_for_timeout(350)
        check(f"{tag} 2 บันทึกไม้ย้อนหลัง (ระหว่างพัก) บันทึกได้ — ไม่ใช่เปิดความเสี่ยงใหม่", can and n_trades(page) == nt + 1, str(n_trades(page)))

        # ── 3 ครบ 14 วันแต่ยังไม่เขียนทบทวน → ยัง pause · เขียน 25 ตัวอักษร → recover
        e0 = dd(page, "main", "core")
        pst = persisted(page, "main", "core")
        pst.update({"stageSince": "2026-09-17", "pauseUntil": TODAY, "review": None})
        set_dd(page, "main", "core", pst)
        e = dd(page, "main", "core")
        check(f"{tag} 3 ครบเวลาพัก (วันนี้ = pauseUntil) แต่ยังไม่เขียนทบทวน → ยัง pause", e["stage"] == "pause" and e["left"] == 0 and not e["reviewDone"], json.dumps(e))
        open_sheet(page, "main", "core")
        sv = page.locator("#ddReviewSave").first
        check(f"{tag} 3 sheet: ปุ่ม 'เขียนทบทวน' ปิดเมื่อยังไม่พิมพ์ · มีช่องข้อความ", sv.is_disabled() and page.locator("#ddReview").count() == 1 and "ครบเวลาพักแล้ว" in (txt(page, "[data-dd-left]") or ""), txt(page, "[data-dd-left]"))
        page.fill("#ddReview", "สั้นไป"); page.wait_for_timeout(100)
        check(f"{tag} 3 พิมพ์ < 20 ตัวอักษร → ปุ่มปิด + ข้อความแจ้ง", sv.is_disabled() and "อย่างน้อย 20" in (txt(page, "#ddReviewErr") or ""))
        shot(page, f"dd1-sheet-pause-review-{label}.png", ".core-sheet .ui-sheet")
        text25 = "ขายตัวอ่อนช้า ไม่ตัดตาม Stop"
        page.fill("#ddReview", text25); page.wait_for_timeout(100)
        check(f"{tag} 3 พิมพ์ ≥ 20 ตัวอักษร ({len(text25)}) → ปุ่มกดได้", not sv.is_disabled())
        page.click("#ddReviewSave"); page.wait_for_timeout(500)
        p = persisted(page, "main", "core"); e = dd(page, "main", "core")
        check(f"{tag} 3 เก็บ review{{text, at}} · ครบเวลา + มีบันทึก → recover อัตโนมัติ · ไม้ใหม่ ×0.5", p["stage"] == "recover" and e["stage"] == "recover" and e["sizeFactor"] == 0.5 and e["allowNew"] and not e["allowLadder"], json.dumps([p, e])[:500])
        check(f"{tag} 3 ชิป 'ฟื้นตัว …R / 2R' · ไม้ W ใหม่ ×0.5", "ฟื้นตัว" in chip(page, "core", "main") and "R / 2R" in chip(page, "core", "main") and near(js(page, "()=>coreSizeOpts('main').riskPct"), 0.00625, 1e-12), chip(page, "core", "main"))
        # ใน recover แผน W ใหม่ไม่ถูกบล็อก (ลดขนาดเท่านั้น) · บันไดใหม่ยังงด
        lad = js(page, "()=>coreCanPlace('main',{tier:'A',fortress:true,thb:{ok:false}},null,false).ddBlock")
        check(f"{tag} 3 recover: งดบันได L ใหม่ ('ฟื้นตัว')", "ฟื้นตัว" in lad, lad)
        # ── 4 recover: ปิดไม้กำไร ฿17,500 (2R) → normal
        st = ds0(700000, stage="recover", stageSince="2026-09-28", recoverDd0=15)
        set_dd(page, "main", "core", st)
        put_trades(page, "main", [closed("c1", pnl=-70000, exit_date="2026-09-20"), closed("c2", pnl=17000, exit_date="2026-09-30")])
        e = dd(page, "main", "core")
        check(f"{tag} 4 recover: กำไรที่ปิด ฿17,000 (1.94R) → ยัง recover", e["stage"] == "recover" and near(e["recoverR"], 17000 / 8750, 1e-9), json.dumps(e))
        put_trades(page, "main", [closed("c1", pnl=-70000, exit_date="2026-09-20"), closed("c2", pnl=17500, exit_date="2026-09-30")])
        e = dd(page, "main", "core")
        check(f"{tag} 4 recover: กำไรที่ปิด ฿17,500 (2R) → normal (DD เหลือ {e['ddPct']:.1f}% · ออกด้วยกฎ +2R เพราะยังไม่มี snapshot 2 สัปดาห์)", e["stage"] == "normal" and e["sizeFactor"] == 1, json.dumps(e))
        check(f"{tag} 4 ชิป 'ปกติ' หลังออกจาก recover", "ปกติ" in chip(page, "core", "main") and page.locator('[data-dd-bar="core"]').count() == 0, chip(page, "core", "main"))
        # ── 5 reduce: snapshot 2 สัปดาห์ที่จบแล้ว < 12.5 → normal · สัปดาห์เดียว → ยัง reduce
        put_trades(page, "main", [closed("c1", pnl=-35000)])
        set_dd(page, "main", "core", ds0(700000, stage="reduce", stageSince="2026-09-01", weekly={"2026-09-20": 10, "2026-09-13": 11}))
        e = dd(page, "main", "core")
        check(f"{tag} 5 reduce: 2 สัปดาห์ที่จบแล้ว DD < 12.5 (10 · 11) → normal", e["stage"] == "normal" and near(e["ddPct"], 5, 1e-6), json.dumps(e))
        set_dd(page, "main", "core", ds0(700000, stage="reduce", stageSince="2026-09-01", weekly={"2026-09-20": 10}))
        e = dd(page, "main", "core")
        check(f"{tag} 5 reduce: สัปดาห์เดียว → ยัง reduce", e["stage"] == "reduce", json.dumps(e))
        set_dd(page, "main", "core", ds0(700000, stage="reduce", stageSince="2026-09-01", weekly={"2026-09-27": 8, "2026-09-20": 10}))
        e = dd(page, "main", "core")
        check(f"{tag} 5 reduce: ไม่นับสัปดาห์ปัจจุบัน (ปัจจุบัน + 1 สัปดาห์) → ยัง reduce", e["stage"] == "reduce", json.dumps(e))
        p = persisted(page, "main", "core")
        check(f"{tag} 5 snapshot สัปดาห์ปัจจุบัน {WK} เก็บค่าล่าสุด (5%) · weekly ≤ 12 สัปดาห์", near(p["weekly"].get(WK), 5, 1e-6) and len(p["weekly"]) <= 12, json.dumps(p["weekly"]))
        # ── 9 แก้ทุนถัง Core → rebase
        put_trades(page, "main", [closed("c1", pnl=-87500)])
        set_dd(page, "main", "core", ds0(700000))
        check(f"{tag} 9 (ก่อนแก้ทุน) reduce", dd(page, "main", "core")["stage"] == "reduce")
        js(page, "()=>openSettings()"); page.wait_for_timeout(250)
        page.fill("#sCore", "800000"); page.wait_for_timeout(100); js(page, "()=>saveSettings()"); page.wait_for_timeout(500)
        e = dd(page, "main", "core"); p = persisted(page, "main", "core")
        check(f"{tag} 9 แก้ทุนถัง Core 700,000 → 800,000 = rebase: DD 0 · stage normal · peak = equity ฿800,000 · baseAt วันนี้", e["stage"] == "normal" and near(e["ddPct"], 0, 1e-9) and near(p["peak"], 800000, 1e-6) and p["baseAt"] == TODAY and p["tank"] == 800000, json.dumps([e, p])[:500])
        check(f"{tag} 9 แจ้งบรรทัดเล็ก 'เริ่มนับ DD ใหม่ (แก้ทุนถัง)'", "เริ่มนับ DD ใหม่ (แก้ทุนถัง)" in (txt(page, '[data-dd-rebase="core"]') or ""), txt(page, '[data-dd-rebase="core"]'))
        js(page, "()=>{ const B=getBook('main'); B.settings.capital.core=700000; saveBook('main'); render(); }")
        # ── 10 ขาดราคาปิด 1 ตัว → นับเป็น 0 + 'ขาดราคา 1 ตัว'
        clear_cards(page)
        seed_cards(page, {"cX": p24.open_card("cX", "tX", ticker="NOPX.BK", qty=500, entry=100, sl=90, tier="A"),
                          "cY": p24.open_card("cY", "tY", ticker="HASPX.BK", qty=500, entry=100, sl=90, px=90, pxDate="2026-09-25", emaW=80, tier="A")})
        put_trades(page, "main", [T("tX", "core", "open", sym="NOPX.BK", entry=100, sl=90, qty=500, sl0=90, date="2026-09-10", openedAt="2026-09-10"),
                                  T("tY", "core", "open", sym="HASPX.BK", entry=100, sl=90, qty=500, sl0=90, date="2026-09-10", openedAt="2026-09-10")])
        set_dd(page, "main", "core", ds0(700000))
        e = dd(page, "main", "core")
        check(f"{tag} 10 ตัวที่ไม่มีราคานับเป็น 0 (equity = 700,000 − 5,000 จากตัวที่มีราคา) + ขาดราคา 1 ตัว", e["missing"] == 1 and near(e["equity"], 695000, 1e-6), json.dumps(e))
        open_sheet(page, "main", "core")
        check(f"{tag} 10 sheet แสดง 'ขาดราคา 1 ตัว'", "ขาดราคา 1 ตัว" in (txt(page, "[data-dd-missing]") or ""), txt(page, "[data-dd-missing]"))
        js(page, "()=>coreSheetClose()")
        # ── 11 Core DD ≥ 20% → sheet แสดงตัวอ่อนสุด 3 ตัวตามลำดับ
        clear_cards(page)
        mk = lambda cid, tk, px, sl, **kw: p24.open_card(cid, "t" + cid, ticker=tk, qty=100, entry=100, sl=sl, px=px, pxDate="2026-09-25", emaW=50, tier="A", **kw)
        seed_cards(page, {"w1": mk("w1", "W1.BK", 80, 70), "w2": mk("w2", "W2.BK", 85, 70), "w3": mk("w3", "W3.BK", 92, 70), "w4": mk("w4", "W4.BK", 95, 70),
                          "w5": mk("w5", "W5.BK", 85, 84), "w6": mk("w6", "W6.BK", 85, 80, stopHistory=[{"date": "2026-09-15", "from": 90, "to": 80}])})
        tr = lambda tid, sym, sl, **kw: T(tid, "core", "open", sym=sym, entry=100, sl=sl, qty=100, date="2026-09-10", openedAt="2026-09-10", **kw)
        put_trades(page, "main", [closed("c1", pnl=-150000), tr("tw1", "W1.BK", 70, sl0=90), tr("tw2", "W2.BK", 70, sl0=90), tr("tw3", "W3.BK", 70, sl0=90), tr("tw4", "W4.BK", 70, sl0=90),
                                  tr("tw5", "W5.BK", 84, sl0=90), tr("tw6", "W6.BK", 80)])
        set_dd(page, "main", "core", ds0(700000))
        e = dd(page, "main", "core")
        check(f"{tag} 11 DD ≥ 20% (ปิดขาดทุน ฿150,000 + ตัวที่ถืออยู่) → pause", e["stage"] == "pause" and e["ddPct"] >= 20, json.dumps(e))
        open_sheet(page, "main", "core")
        rows = page.evaluate("()=>[...document.querySelectorAll('[data-dd-weakrow]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        order = [r.split(" ·")[0] for r in rows]
        check(f"{tag} 11 sheet แสดงตัวอ่อนสุด 3 ตัว: W1 (−2.00R) → ถัดมา R −1.50 เรียงห่าง Stop น้อยสุด W5 (1.2%) → W2/W6", len(rows) == 3 and order[0] == "W1.BK" and order[1] == "W5.BK" and order[2] in ("W2.BK", "W6.BK"), json.dumps(rows, ensure_ascii=False))
        check(f"{tag} 11 ข้อความ 'ทบทวน ลดตัวอ่อนสุด — คุณตัดสินใจเอง' · ไม่ขายให้ (ไม้ยังครบ)", "ทบทวน ลดตัวอ่อนสุด — คุณตัดสินใจเอง" in (txt(page, "[data-dd-weak]") or "") and js(page, "()=>getBook('main').trades.filter(t=>t.status==='open').length") == 6)
        shot(page, f"dd1-core-weakest-{label}.png", ".core-sheet .ui-sheet")
        # ตัวอ่อนสุดอาศัย sl0 / stopHistory: W6 ไม่มี sl0 ใช้ stopHistory[0].from = 90 → R −1.5 เท่ากับ W2
        wk = js(page, "()=>ddWeakest(ddEval('main','core')).map(x=>[x.ticker, Math.round(x.r*100)/100])")
        check(f"{tag} 11 W6 (ไม่มี sl0) ใช้ Stop แรกใน stopHistory → R −1.5", ["W6.BK", -1.5] in wk or any(x[0] == "W6.BK" for x in js(page, "()=>ddWeakest(ddEval('main','core')).map(x=>[x.ticker,x.r])")), json.dumps(wk))
        js(page, "()=>coreSheetClose()")
        # ── 14 (Core) 430: ชิป/แถบ/sheet ไม่ล้น
        bad = overflow(page, ['[data-core-head="main"]', '[data-dd-bar="core"]'])
        open_sheet(page, "main", "core")
        bad += overflow(page, [".core-sheet .ui-sheet"])
        check(f"{tag} 14 ชิป/แถบ/sheet (Core) ไม่ล้นแนวนอน", not bad, json.dumps(bad))
        js(page, "()=>coreSheetClose()")
        check(f"{tag} core console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} core console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── (13) ไม่มี ddState (บัญชีเก่า) ─────────────────────────
def legacy_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    doc = doc37(with_dd=False)
    doc["books"]["main"]["trades"] = [closed("old1", pnl=-200000, exit_date="2026-08-15"),
                                      closed("old2", port="satB", pnl=-100000, exit_date="2026-08-15")]
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=doc)
    try:
        fx_core(page); go_core(page); page.wait_for_timeout(600)
        pc, ps = persisted(page, "main", "core"), persisted(page, "main", "sat")
        check(f"{tag} 13 ไม่มี ddState: เริ่ม peak = equity ปัจจุบัน (Core ฿700,000 · Sat $26,000) · stage normal", pc and ps and pc["stage"] == "normal" and near(pc["peak"], 700000, 1e-6) and ps["stage"] == "normal" and near(ps["peak"], 26000, 1e-6), json.dumps([pc, ps])[:400])
        check(f"{tag} 13 ไม้ที่ปิดก่อนเริ่มนับ (baseAt = วันนี้) ไม่ดึง DD ลง · ชิปเป็น 'ปกติ' · ไม่พัง",
              "ปกติ" in chip(page, "core", "main") and dd(page, "main", "core")["ddPct"] == 0 and pc["baseAt"] == TODAY and pc["tank"] == 700000, chip(page, "core", "main"))
        check(f"{tag} 13 เขียนลง Firestore (mock) แล้ว และไม่เขียนซ้ำเมื่อค่าไม่เปลี่ยน", (db_dd(page, "main", "core") or {}).get("stage") == "normal" and js(page, "()=>ddSync()") is False, "")
        check(f"{tag} 13 console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} 13 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── (6–8, 14) Sat ─────────────────────────
def sat_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        page.evaluate("() => { satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50']); }")   # WA1fix — ไม่มีโหมด legacy: เลือก Asset สัปดาห์นี้ก่อนคำนวณแผน
        p5.goto_sat(page); p36.clean(page, "Long"); go_sat(page)
        # ── 7 Sat reduce: ปิดขาดทุน ฿130,000 (12.5%) → lot = ครึ่งหนึ่ง
        put_trades(page, "main", [closed("s1", port="satB", pnl=-130000)])
        e = dd(page, "main", "sat")
        check(f"{tag} 7 Sat ปิดขาดทุน ฿130,000 → DD 12.5% · stage reduce · ×0.5 · 1R = ฿13,000", e["stage"] == "reduce" and near(e["ddPct"], 12.5, 1e-6) and e["sizeFactor"] == 0.5 and near(e["oneR"], 13000, 1e-6), json.dumps(e))
        idea = {"id": "iD", "v3": True, "asset": "XAUUSD", "bias": "Long", "entry": 2410, "sl": 2400, "tp": 2460, "accts": {},   # ST1: fixture ใส่ TP แรก (R:R 5.0 ≥ 1.5) — เดิม tp None
            "conditions": [{"id": "c1", "text": "Break & Pullback @ 2400", "tp_from": 2460, "tp_to": 2480, "inval": None, "active": True, "saved": True}]}
        r = js(page, """(idea)=>{ idea.week = wpWeekKey(); const c = satV3PlanAcctCalc(idea,'main'); const b = sat7dAcctBase('main'); const cfg = c.chosen.cfg;
            const rc = (b.cap*1.25/100/b.fx)*c.factor*c.split1, dist = 10;   /* PY2: ไม้ 1 = n1% ของงบ */
            const full = Calc.satLot({riskAmount: rc, dist, contract: cfg.contract, lotStep: cfg.lotStep, minLot: cfg.minLot}).lot;
            const half = Calc.satLot({riskAmount: rc*0.5, dist, contract: cfg.contract, lotStep: cfg.lotStep, minLot: cfg.minLot}).lot;
            return {lot:c.lot, full, half, cap:b.cap, riskTHB:b.riskTHB, factor:c.factor, ready:c.ready}; }""", idea)
        check(f"{tag} 7 lot ใหม่ = Calc.satLot ที่ riskAmount × 0.5 ตรง ๆ (ปัดลงตาม lotStep) · ต่างจาก lot ปกติ", r["lot"] == r["half"] and r["half"] < r["full"] and r["cap"] == 1040000 and near(r["riskTHB"], 6500, 1e-6), json.dumps(r))
        check(f"{tag} 7 reduce ยัง ready ได้ (ลดขนาดเท่านั้น ไม่บล็อก)", r["ready"] is True, json.dumps(r))
        c = chip(page, "sat", "main")
        check(f"{tag} 7 ชิป Sat 'DD 12.5% · ลดขนาด ×0.5' ในแถบบัญชี Sat", "DD 12.5%" in c and "ลดขนาด ×0.5" in c, c)
        # ── 6 Sat: ปิดไม้ขาดทุนรวม ฿208,000 (20%) → พัก 7 วัน (ทั้งสองบัญชี)
        put_trades(page, "fam", [closed("f1", port="satB", pnl=-208000)])
        put_trades(page, "main", [closed("s1", port="satB", pnl=-208000)])
        e = dd(page, "main", "sat")
        check(f"{tag} 6 Sat ปิดขาดทุน ฿208,000 (20%) → pause · พักถึง {P7} (วันนี้ + 7)", e["stage"] == "pause" and near(e["ddPct"], 20, 1e-6) and e["pauseUntil"] == P7 and not e["allowNew"], json.dumps(e))
        check(f"{tag} 6 ชิป Sat 'พักถึง 8 ต.ค.' · แถบแจ้ง", "พักถึง 8 ต.ค." in chip(page, "sat", "main") and "พักถึง 8 ต.ค." in (txt(page, '[data-sat-meta] [data-dd-bar="sat"]') or ""), chip(page, "sat", "main"))
        js(page, "(i)=>{ i.week = wpWeekKey(); sat7dWrite('satIdeas','iD', Object.assign({}, i, {created_at:new Date().toISOString(), planned:true, setups:[], status:'active'})); }", idea); page.wait_for_timeout(500)
        go_sat(page); open_plan(page)
        rd = js(page, """()=>['main','fam'].map(a=>{ const i=sat7dIdea('iD'); const c=satV3PlanAcctCalc(i,a); return {a, ready:c.ready, dd:c.ddBlock, w:c.warns[0]||''}; })""")
        check(f"{tag} 6 การ์ดแผน: ทุกบัญชีที่พักไม่ ready + เหตุผล 'เบรก DD: พักถึง 8 ต.ค.…'", all((not x["ready"]) and "เบรก DD: พักถึง 8 ต.ค." in x["dd"] for x in rd), json.dumps(rd, ensure_ascii=False))
        panel = txt(page, "#satV3Panel") or ""
        check(f"{tag} 6 หน้า Sat ไม่มีปุ่ม 'รวมด้วย (นอกแผน)' · มีข้อความเบรก DD ต่อบัญชี", "รวมด้วย (นอกแผน)" not in panel and page.locator("#satV3Panel [data-dd-block]").count() >= 1, panel[:200] + " | blocks=" + str(page.locator("#satV3Panel [data-dd-block]").count()) + " offplan=" + str("รวมด้วย (นอกแผน)" in panel))
        shot(page, f"dd1-sat-blocked-{label}.png", "#satV3Panel")
        n0, f0 = n_trades(page, "main"), n_trades(page, "fam")
        js(page, "()=>{ satV3SaveSlot('iD','main'); satV3SaveSlot('iD','fam'); satV3SaveOffplanAccount('iD','main'); satV3SaveReadyAccounts('iD'); try{ sat7dSaveOrder('iD','main'); }catch(e){} }"); page.wait_for_timeout(400)
        check(f"{tag} 6 เรียกฟังก์ชันบันทึก order ตรง ๆ (SaveSlot · SaveOffplan · SaveReady · sat7dSaveOrder) → ไม่สร้างไม้", n_trades(page, "main") == n0 and n_trades(page, "fam") == f0, f"{n_trades(page,'main')} {n_trades(page,'fam')}")
        # PY1 เติมไม้ (Stop ≥ ทุน) ยังทำได้ระหว่างพัก
        p36.clean(page, "Long")
        put_trades(page, "main", [closed("s1", port="satB", pnl=-208000)])
        p36.mk_first(page, sl=2400)
        b = p36.btn(page)
        check(f"{tag} 6 PY1: เติมไม้ตัวที่ Stop ≥ ทุน ยังกดได้ระหว่างพัก (ปุ่มเปิด · ไม่มีเหตุผลบล็อก)", b and b["disabled"] is False and b["why"] == "", json.dumps(b, ensure_ascii=False))
        n0 = n_trades(page, "main")
        p36.open_sheet(page); p36.fill(page, e2=2412, sj=2400)
        s = p36.sheet(page)
        js(page, "()=>satPyrSave()"); page.wait_for_timeout(350)
        check(f"{tag} 6 PY2: เติมไม้สำเร็จระหว่างพัก (ไม้ 2 = 30% ของงบ · ไม่คูณ DD ซ้ำ) · lot {s['lot']}", n_trades(page, "main") == n0 + 1 and s["lot"] is not None and abs(float(s["lot"]) - js(page, "()=>{ const b = sat7dAcctBase('main'); const cfg = sat7dBrokerOpts(b.B,'XAUUSD')[0].cfg; return Calc.satLot({riskAmount: b.riskTHB / b.fx * 0.3, dist: 12, contract: cfg.contract, lotStep: cfg.lotStep, minLot: cfg.minLot}).lot; }")) < 1e-9, json.dumps(s, ensure_ascii=False))
        # ── 8 แยกบัญชี: main พัก · fam ปกติ
        put_trades(page, "fam", []); set_dd(page, "fam", "sat", ds0(26000)); p36.clean(page, "Long"); put_trades(page, "main", [closed("s1", port="satB", pnl=-208000)])
        js(page, "(i)=>{ i.week = wpWeekKey(); sat7dWrite('satIdeas','iD', Object.assign({}, i, {created_at:new Date().toISOString(), planned:true, setups:[], status:'active'})); }", idea); page.wait_for_timeout(500)
        go_sat(page); open_plan(page)
        em, ef = dd(page, "main", "sat"), dd(page, "fam", "sat")
        rd = js(page, """()=>['main','fam'].map(a=>{ const c=satV3PlanAcctCalc(sat7dIdea('iD'),a); return {a, ready:c.ready, dd:c.ddBlock}; })""")
        check(f"{tag} 8 แยกบัญชี: main = pause · fam = normal", em["stage"] == "pause" and ef["stage"] == "normal" and ef["sizeFactor"] == 1, json.dumps([em, ef]))
        check(f"{tag} 8 การ์ดแผน: main ไม่ ready (เบรก DD) · fam ready ปกติ", rd[0]["ready"] is False and rd[0]["dd"] and rd[1]["ready"] is True and not rd[1]["dd"], json.dumps(rd, ensure_ascii=False))
        check(f"{tag} 8 ชิป: main 'พักถึง' · fam 'ปกติ' · Core ของ main ไม่โดน (normal)", "พักถึง" in chip(page, "sat", "main") and "ปกติ" in chip(page, "sat", "fam") and dd(page, "main", "core")["stage"] == "normal", chip(page, "sat", "main") + " | " + chip(page, "sat", "fam"))
        # ── 14 (Sat) ไม่ล้น
        bad = overflow(page, ["[data-sat-meta]", '[data-sat-meta] [data-dd-bar="sat"]'])
        open_sheet(page, "main", "sat")
        bad += overflow(page, [".core-sheet .ui-sheet"])
        check(f"{tag} 14 ชิป/แถบ/sheet (Sat) ไม่ล้นแนวนอน", not bad, json.dumps(bad))
        check(f"{tag} 14 sheet Sat: ตารางสัปดาห์ · เกณฑ์ · เวลาที่เหลือ", all(x in (txt(page, ".core-sheet") or "") for x in ("สัปดาห์", "เกณฑ์", "เหลือเวลาพัก")) and page.locator("[data-dd-weekly]").count() == 1, (txt(page, ".core-sheet") or "")[:200])
        js(page, "()=>coreSheetClose()")
        check(f"{tag} sat console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} sat console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── (12) ค่าตั้ง ─────────────────────────
def settings_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    doc = doc37()
    for a in ("main", "fam"):                    # ค่าเริ่มต้น: ไม่มี dd* ใน coreRisk/satRisk
        for k in ("coreRisk", "satRisk"): doc["books"][a]["settings"][k] = {kk: vv for kk, vv in doc["books"][a]["settings"][k].items() if not kk.startswith("dd")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc=doc)
    try:
        page.evaluate("()=>{ openSettings(); document.querySelectorAll('#crSec,#satRiskSec').forEach(d=>d.open=true); }"); page.wait_for_timeout(300)
        vals = page.evaluate("()=>Object.fromEntries(['sCrDdReduce','sCrDdPause','sCrDdWeeks','sCrDdRecoverR','sSatDdReduce','sSatDdPause','sSatDdWeeks','sSatDdRecoverR'].map(i=>[i, document.getElementById(i).value]))")
        want = {"sCrDdReduce": "12.5", "sCrDdPause": "20", "sCrDdWeeks": "2", "sCrDdRecoverR": "2", "sSatDdReduce": "12.5", "sSatDdPause": "20", "sSatDdWeeks": "1", "sSatDdRecoverR": "2"}
        check(f"{tag} 12 ค่าเริ่มต้นครบ: Core 12.5 · 20 · 2 สัปดาห์ · 2R | Sat 12.5 · 20 · 1 สัปดาห์ · 2R", vals == want, json.dumps(vals))
        units = page.evaluate("()=>Object.fromEntries(['sCrDdReduce','sCrDdPause','sCrDdWeeks','sCrDdRecoverR','sSatDdReduce','sSatDdPause','sSatDdWeeks','sSatDdRecoverR'].map(i=>{ const l=document.getElementById(i).closest('.f').querySelector('label'); const u=l.querySelector('.crUnit'); return [i, u ? u.innerText : '']; }))")
        check(f"{tag} 12 ป้ายหน่วยครบทุกช่อง (% ของถัง · สัปดาห์ · R)", all(units[k] for k in units) and "%" in units["sCrDdReduce"] and "%" in units["sSatDdPause"] and "weeks" in units["sCrDdWeeks"] and "R" in units["sSatDdRecoverR"], json.dumps(units, ensure_ascii=False))
        er = lambda i: txt(page, f'[data-err-for="{i}"]') or ""
        sd = lambda: page.evaluate("()=>document.getElementById('setSaveBtn').disabled")
        check(f"{tag} 12 ค่าเริ่มต้น: ไม่มี error · ปุ่มบันทึกเปิด", not sd() and not er("sCrDdReduce") and not er("sCrDdPause") and not er("sSatDdWeeks"))
        page.fill("#sCrDdReduce", "25"); page.wait_for_timeout(100)
        check(f"{tag} 12 reduce ≥ pause (25 ≥ 20) → ข้อความแดง + บันทึกปิด", bool(er("sCrDdReduce")) and sd(), er("sCrDdReduce"))
        page.fill("#sCrDdReduce", "20"); page.wait_for_timeout(100)
        check(f"{tag} 12 reduce = pause (20 = 20) → แดง + บันทึกปิด", bool(er("sCrDdReduce")) and sd())
        page.fill("#sCrDdReduce", "12.5"); page.fill("#sCrDdPause", "60"); page.wait_for_timeout(100)
        check(f"{tag} 12 pause 60 > 50 → แดง + บันทึกปิด", bool(er("sCrDdPause")) and sd(), er("sCrDdPause"))
        page.fill("#sCrDdPause", "20")
        for v in ("0", "1.5", "9"):
            page.fill("#sCrDdWeeks", v); page.wait_for_timeout(100)
            check(f"{tag} 12 pauseWeeks {v} → แดง + บันทึกปิด", bool(er("sCrDdWeeks")) and sd(), er("sCrDdWeeks"))
        page.fill("#sCrDdWeeks", "2")
        for v in ("0.4", "11"):
            page.fill("#sCrDdRecoverR", v); page.wait_for_timeout(100)
            check(f"{tag} 12 recoverR {v} → แดง + บันทึกปิด", bool(er("sCrDdRecoverR")) and sd(), er("sCrDdRecoverR"))
        page.fill("#sCrDdRecoverR", "2")
        page.fill("#sSatDdReduce", "30"); page.wait_for_timeout(100)
        check(f"{tag} 12 Sat: reduce 30 ≥ pause 20 → แดง + บันทึกปิด", bool(er("sSatDdReduce")) and sd(), er("sSatDdReduce"))
        page.fill("#sSatDdReduce", "10"); page.fill("#sSatDdPause", "18"); page.fill("#sSatDdWeeks", "2"); page.fill("#sSatDdRecoverR", "1.5")
        page.fill("#sCrDdReduce", "10"); page.fill("#sCrDdPause", "25"); page.fill("#sCrDdWeeks", "3"); page.fill("#sCrDdRecoverR", "3"); page.wait_for_timeout(100)
        check(f"{tag} 12 ค่าถูกต้อง → ไม่มี error · บันทึกเปิด", not sd())
        js(page, "()=>saveSettings()"); page.wait_for_timeout(400)
        cr, sr = js(page, "()=>coreRiskCfg('main')"), js(page, "()=>satRiskCfg('main')")
        check(f"{tag} 12 บันทึกแล้วอ่านกลับ: Core 10 · 25 · 3 · 3R | Sat 10 · 18 · 2 · 1.5R", (cr["ddReduce"], cr["ddPause"], cr["ddPauseWeeks"], cr["ddRecoverR"]) == (10, 25, 3, 3) and (sr["ddReduce"], sr["ddPause"], sr["ddPauseWeeks"], sr["ddRecoverR"]) == (10, 18, 2, 1.5), json.dumps([cr, sr])[:300])
        d = db_dd(page, "main", "core")
        check(f"{tag} 12 บันทึกค่าตั้งแล้ว ddState เดิมไม่หาย", d is not None and d["stage"] == "normal")
        # ค่าที่ผิดใน Firestore → ใช้ค่าเริ่มต้น (ไม่พัง)
        js(page, "()=>{ const B=getBook('main'); B.settings.coreRisk.ddReduce=30; B.settings.coreRisk.ddPause=20; saveBook('main'); }")
        cr = js(page, "()=>coreRiskCfg('main')")
        check(f"{tag} 12 reduce ≥ pause ใน settings → coreRiskCfg ใช้ 12.5 / 20", cr["ddReduce"] == 12.5 and cr["ddPause"] == 20, json.dumps([cr["ddReduce"], cr["ddPause"]]))
        bad = overflow(page, ["#crSec", "#satRiskSec"])
        check(f"{tag} 12 ช่องค่าตั้ง DD ไม่ล้นแนวนอน", not bad, json.dumps(bad))
        check(f"{tag} 12 console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} 12 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


# ───────────────────────── DD1fix (10–11) recover ได้ +2R ตอน DD ยังลึก → reduce ───────────────────────── 
def fix_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        fx_core(page); go_core(page)
        # 10 Core: recover dd0 25 · ปิดกำไร 2R · DD ยัง ≥ 20
        # peak 700,000 · ปิดขาดทุน 140,000 (−20%) + กำไร 17,500 (2R) = DD 17.5% … ต้องยัง ≥ 20: ขาดทุน 175,000 → DD 22.5%
        set_dd(page, "main", "core", ds0(700000, stage="recover", stageSince="2026-09-28", recoverDd0=25))
        put_trades(page, "main", [closed("c1", pnl=-192500, exit_date="2026-09-20"), closed("c2", pnl=17500, exit_date="2026-09-30")])
        e = dd(page, "main", "core"); p = persisted(page, "main", "core")
        check(f"{tag} 10 Core recover dd0 25 + กำไร 2R แต่ DD {e['ddPct']:.1f}% ≥ 20 → reduce (ไม่ใช่ normal/pause)", e["stage"] == "reduce" and e["ddPct"] >= 20 and p["stage"] == "reduce" and p["recoverDd0"] == 25 and p["stageSince"] == TODAY, json.dumps([e, p])[:400])
        c = chip(page, "core", "main")
        check(f"{tag} 10 ชิป 'ลดขนาด ×0.5' (ไม่ใช่ 'พักถึง')", "ลดขนาด ×0.5" in c and "พักถึง" not in c, c)
        lad = js(page, "()=>coreCanPlace('main',{tier:'A',fortress:true,thb:{ok:false}},null,false)")
        check(f"{tag} 10 ไม้ W ใหม่ ×0.5 · บันไดใหม่ปิด", near(js(page, "()=>coreSizeOpts('main').riskPct"), 0.00625, 1e-12) and lad["allowed"] is False, json.dumps(lad.get("ddBlock")))
        open_sheet(page, "main", "core")
        t = txt(page, "[data-dd-repause]") or ""
        check(f"{tag} 10 sheet: 'พักใหม่เมื่อ DD ≥ 26.25%' (max(20, 25 + 1.25))", "พักใหม่เมื่อ DD ≥ 26.25%" in t, t)
        shot(page, f"dd1fix-recover-to-reduce-{label}.png", ".core-sheet .ui-sheet")
        js(page, "()=>coreSheetClose()")
        check(f"{tag} 10 core console: zero error-level messages", not ce, "; ".join(ce[:3]))
        # 11 Sat เดียวกัน (gap = rpt 1.25)
        set_dd(page, "main", "sat", ds0(26000, stage="recover", stageSince="2026-09-28", recoverDd0=25))
        put_trades(page, "main", [closed("s1", port="satB", pnl=-292500, exit_date="2026-09-20"), closed("s2", port="satB", pnl=26000, exit_date="2026-09-30")])
        e = dd(page, "main", "sat"); p = persisted(page, "main", "sat")
        check(f"{tag} 11 Sat recover dd0 25 + กำไร 2R (฿26,000) แต่ DD {e['ddPct']:.1f}% ≥ 20 → reduce", e["stage"] == "reduce" and e["ddPct"] >= 20 and p["recoverDd0"] == 25 and e["sizeFactor"] == 0.5, json.dumps([e, p])[:400])
        go_sat(page)
        c = chip(page, "sat", "main")
        check(f"{tag} 11 ชิป Sat 'ลดขนาด ×0.5'", "ลดขนาด ×0.5" in c and "พักถึง" not in c, c)
        open_sheet(page, "main", "sat")
        t = txt(page, "[data-dd-repause]") or ""
        check(f"{tag} 11 sheet Sat: 'พักใหม่เมื่อ DD ≥ 26.25%'", "พักใหม่เมื่อ DD ≥ 26.25%" in t, t)
        js(page, "()=>coreSheetClose()")
        bad = overflow(page, ["[data-sat-meta]"])
        check(f"{tag} 11 ไม่ล้นแนวนอน", not bad, json.dumps(bad))
        check(f"{tag} 10-11 console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (430, 932, "430px")):
            section0(pw, w, h, label)
            core_tests(pw, w, h, label)
            legacy_tests(pw, w, h, label)
            sat_tests(pw, w, h, label)
            settings_tests(pw, w, h, label)
            fix_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 37 / DD1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
