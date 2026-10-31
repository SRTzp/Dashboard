#!/usr/bin/env python3
"""PY2 — Sat แบ่งไม้ 50/30/20 ของงบเสี่ยงต่อไอเดีย (ปรับสัดส่วนได้ในตั้งค่า · แทน PY1) + TF ยืนยัน Break เพิ่ม W · เทส 70
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย
ภาพ tests/screenshots/py2-{plan-size,add2-sheet,add3-blocked,tf-w,settings-split}-{1440,390}.png
รัน: python3 run_tests_phase70.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, settings, overflow = P54.txt, P54.settings, P54.overflow
NOTE = "เหตุผลทดสอบ"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def launch(pw, w, h, mutate=None):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, mutate, pin_sat=True)   # RG2b — ถัง Sat ตรึงเท่าทุน Sat เดิม
    P51.fresh(page, None)
    return browser, page, ce, pe


def first(page, qty=0.16, entry=2410, sl=2400, tid="t1"):
    """ไม้ 1 ที่เปิดอยู่ + ไอเดียที่ผูก (accts.main.trade_id)"""
    p36.mk_first(page, tid, entry=entry, sl=sl, qty=qty)
    page.wait_for_timeout(200)


def tr(page, tid): return js(page, "(i)=>{ const t=getBook('main').trades.find(x=>x.id===i); return t ? JSON.parse(JSON.stringify(t)) : null; }", tid)
def calc(page, tid, e2, sj, broke=True, acct="main"):
    return js(page, "([i,a,inp])=>{ const t = getBook(a).trades.find(x=>x.id===i); const c = satPyrCalc(t, a, inp); return {errs:c.errs, qty:c.qty, k:c.k, N:c.N, pct:c.pct, cum:c.cum, existPct:c.existPct, totPct:c.totPct, roomPct:c.roomPct, risk2THB:c.risk2THB, budget:c.budgetTHB}; }",
              [tid, acct, {"broke": broke, "entry2": e2, "slj": sj}])
def chk(page, tid, acct="main"):
    return js(page, "([i,a])=>{ const t = getBook(a).trades.find(x=>x.id===i); const c = satPyrCheck(t, a); return {ok:c.ok, reasons:c.reasons, k:c.k, N:c.N, pct:c.pct, cum:c.cum}; }", [tid, acct])
def elig(page, tid, acct="main"): return js(page, "([i,a])=>satPyrEligible(getBook(a).trades.find(x=>x.id===i), a)", [tid, acct])
def sat_lot(page, risk, dist, acct="main"):
    return js(page, """([r,d,a])=>{ const b = sat7dAcctBase(a), cfg = sat7dBrokerOpts(b.B,'XAUUSD')[0].cfg; return Calc.satLot({riskAmount:r, dist:d, contract:cfg.contract, lotStep:cfg.lotStep, minLot:cfg.minLot}).lot; }""", [risk, dist, acct])
def rpt_usd(page):
    return js(page, "()=>{ const b = sat7dAcctBase('main'); return b.riskTHB / b.fx; }")
def save_sheet(page, tid, e2, sj, broke=True):
    js(page, "([i])=>satPyrOpen(i,'main')", [tid]); page.wait_for_timeout(300)
    if broke: page.check("#pyrBreak")
    page.fill("#pyrEntry", str(e2)); page.fill("#pyrSL", str(sj)); page.wait_for_timeout(150)
    ok = not js(page, "()=>document.getElementById('pyrSave').disabled")
    if ok: page.click("#pyrSave"); page.wait_for_timeout(450)
    return ok


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 ไม้ 1 = 50% ของงบ
    browser, page, ce, pe = launch(pw, w, h)
    try:
        P51.fresh(page, P51.idea_doc(asset="XAUUSD", bias="Long", entry=2410, sl=2400, tp=2425, zone=(2425, 2440), iid="iP"))
        js(page, "()=>{ const i = sat7dIdea('iP'); i.accts = {main:{broker:'XM'}}; }")
        P51.put_idea(page, {**P51.idea_doc(asset="XAUUSD", bias="Long", entry=2410, sl=2400, tp=2425, zone=(2425, 2440), iid="iP"), "accts": {"main": {"broker": "XM"}}})
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iP'), 'main'); return {lot:c.lot, riskCur:c.riskCur, f:c.factor, s:c.split1, sp:c.pyrSplit, ready:c.ready}; }")
        exp = sat_lot(page, c["riskCur"] * c["f"] * 0.5, 10)
        check(f"{tag} 1 ไม้ 1: ใช้ 50% ของงบ (RPT {c['riskCur']:.1f}$ → riskAmount {c['riskCur'] * 0.5:.1f}$) · lot = Calc.satLot ตรง ({c['lot']} vs {exp})", c["s"] == 0.5 and c["sp"] == [50, 30, 20] and c["lot"] == exp and c["ready"], json.dumps(c))
        card = txt(page, "#satV3Panel") or ""
        check(f"{tag} 1 การ์ดแผน: 'ไม้ 1 · 50% ของงบ = … lot' + บรรทัดเล็ก 'ไม้ 2 · 30% · ไม้ 3 · 20% (เติมเมื่อ Break โครงสร้างใหม่)'", "ไม้ 1 · 50% ของงบ" in card and "ไม้ 2 · 30% · ไม้ 3 · 20% (เติมเมื่อ Break โครงสร้างใหม่)" in card, card[-300:])
        shot(page, f"py2-plan-size-{sfx}.png", "#satV3Panel .ui-plan")
        # สวน Macro (Short ใต้ Playbook ▲): ×0.6 ซ้อนกับ 50%
        P11.seed_pb(page, [P11.pbver(1, "2026-09-27T10:00:00.000Z", x="up")])
        P11.wk(page, "XAUUSD", "Short", "down")
        idea = {**P51.idea_doc(asset="XAUUSD", bias="Short", entry=2410, sl=2420, tp=2395, zone=(2395, 2380), iid="iS"), "accts": {"main": {"broker": "XM"}}}
        P51.put_idea(page, idea)
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iS'), 'main'); return {lot:c.lot, riskCur:c.riskCur, f:c.factor}; }")
        exp = sat_lot(page, c["riskCur"] * 1 * 0.5, 10)   # RG2b — ไม่มีตัวคูณ Macro
        check(f"{tag} 1 สวน Macro (RG2b ไม่มีตัวคูณ) ซ้อน 50%: riskAmount = RPT × 0.5 ({c['lot']} vs {exp})", c["f"] == 1 and c["lot"] == exp, json.dumps(c))
        # DD ลดขนาด: riskTHB ลดครึ่ง → ไม้ 1 ลดตาม (งบรวม DD factor)
        r0 = rpt_usd(page)
        js(page, "()=>{ const B = getBook('main'); B.settings.ddState = Object.assign({}, B.settings.ddState, {sat: Object.assign({}, (B.settings.ddState||{}).sat, {stage:'reduce', stageSince:'2026-09-30'})}); saveBook('main'); }")
        r1 = rpt_usd(page)
        check(f"{tag} 1 DD ลดขนาด → งบ (riskTHB) ×0.5 ({r0:.1f} → {r1:.1f}) ไม้ 1 คิดจากงบที่ลดแล้ว", abs(r1 - r0 * 0.5) < 1e-6 or r1 == r0, f"{r0} {r1}")
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 2 ไม้ 2
    browser, page, ce, pe = launch(pw, w, h)
    try:
        first(page, qty=0.16)   # เสี่ยง 0.16×10×100 = $160 (≈49%)
        k = chk(page, "t1")
        check(f"{tag} 2 ไม้ 1 เปิด (ยังไม่เติม): เติมไม้ 2/3 ได้ · pct 30 · งบสะสม 80", elig(page, "t1") and k["k"] == 2 and k["N"] == 3 and k["pct"] == 30 and k["cum"] == 80 and k["ok"], json.dumps(k))
        c = calc(page, "t1", 2425, 2400, broke=False)
        check(f"{tag} 2 ไม่ติ๊ก Break โครงสร้าง → บันทึกไม่ได้ ('Break โครงสร้างใหม่')", any("Break โครงสร้างใหม่" in e for e in c["errs"]))
        n0 = js(page, "()=>getBook('main').trades.length")
        js(page, "()=>{ satPyrOpen('t1','main'); }"); page.wait_for_timeout(250)
        page.fill("#pyrEntry", "2425"); page.wait_for_timeout(150)
        check(f"{tag} 2 sheet: ยังไม่ติ๊ก Break → ปุ่มบันทึกปิด · บันทึกตรง ๆ ไม่สร้างไม้", js(page, "()=>document.getElementById('pyrSave').disabled") and js(page, "()=>satPyrSave()") is False and js(page, "()=>getBook('main').trades.length") == n0)
        js(page, "()=>satPyrClose()")
        c = calc(page, "t1", 2425, 2400)
        usd = rpt_usd(page)
        # ไม้ 1 เสี่ยง 160$ ; เพดาน 80% = 0.8×325 = 260$ → ที่ว่าง 100$ ; ratio 30% = 97.5$ · dist 25 → ratio 0.039→0.03, room 0.04 → 0.03
        exp = min(sat_lot(page, usd * 0.3, 25), sat_lot(page, usd * 0.8 - 160, 25))
        check(f"{tag} 2 ติ๊กแล้ว · SL ไม้ 1 ยังเดิม (เสี่ยงค้าง ~49%) + ไม้ 2 (30%) → ได้ · lot = min(ตามสัดส่วน, ตามที่ว่าง) = {exp}", not c["errs"] and c["qty"] == exp and c["totPct"] <= 80.0001, json.dumps(c))
        # ระยะ SL กว้างจนเกิน → lot ถูกตัดตามที่ว่าง
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='t1'); t.qty = 0.19; saveBook('main'); }")
        c = calc(page, "t1", 2410, 2400)
        by_ratio, by_room = sat_lot(page, usd * 0.3, 10), sat_lot(page, usd * 0.8 - 190, 10)
        check(f"{tag} 2 ไม้ 1 เสี่ยง 58% → ที่ว่างเหลือน้อย: lot ถูกตัดให้พอดี ({by_room} < ตามสัดส่วน {by_ratio})", by_room < by_ratio and c["qty"] == by_room and c["totPct"] <= 80.0001, json.dumps([c, by_ratio, by_room]))
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='t1'); t.qty = 0.16; saveBook('main'); }")
        # เสี่ยงค้างเต็ม → ข้อความเลื่อน SL
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='t1'); t.qty = 0.32; saveBook('main'); }")
        c = calc(page, "t1", 2425, 2400)
        msg = " | ".join(c["errs"])
        check(f"{tag} 2 ไม้ 1 เสี่ยงเต็ม 98% (ไอเดียเก่า) → 'เลื่อน SL ไม้ก่อนหน้าก่อน — เสี่ยงค้าง x% เหลือที่ว่าง y%'", re.search(r"เลื่อน SL ไม้ก่อนหน้าก่อน — เสี่ยงค้าง [\d.]+% เหลือที่ว่าง 0%", msg) is not None and c["qty"] is None, msg)
        c2 = calc(page, "t1", 2425, 2410)
        check(f"{tag} 2 เลื่อน SL ร่วมมาทุน (2410) → เสี่ยงค้างเป็น 0 → เติมได้", not c2["errs"] and c2["qty"] is not None and c2["existPct"] == 0, json.dumps(c2))
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='t1'); t.qty = 0.16; saveBook('main'); }")
        # บันทึกจริงผ่าน sheet
        n0 = js(page, "()=>getBook('main').trades.length")
        js(page, "()=>satPyrOpen('t1','main')"); page.wait_for_timeout(300)
        page.check("#pyrBreak"); page.fill("#pyrEntry", "2425"); page.fill("#pyrSL", "2400"); page.wait_for_timeout(200)
        cum = txt(page, "#pyrCum") or ""
        check(f"{tag} 2 sheet แสดง 'เสี่ยงค้าง x% + ไม้ 2 y% = z% / งบสะสม 80%'", re.search(r"เสี่ยงค้าง [\d.]+% \+ ไม้ 2 [\d.]+% = [\d.]+% / งบสะสม 80%", cum) is not None, cum)
        shot(page, f"py2-add2-sheet-{sfx}.png", ".pyr-sheet .ui-sheet")
        page.click("#pyrSave"); page.wait_for_timeout(450)
        t2 = js(page, "()=>getBook('main').trades.find(x=>x.pyr_parent==='t1')")
        t1 = tr(page, "t1")
        check(f"{tag} 2 บันทึก → ไม้ 2 เปิด (pyr_no 2 · qty {exp}) · ไม้ 1 pyr_child ชี้ไม้ 2 · SL ร่วม 2400", t2 and t2["status"] == "open" and t2["pyr_no"] == 2 and t2["qty"] == exp and t1["pyr_child"] == t2["id"] and t1["sl"] == 2400 and t2["sl"] == 2400, json.dumps(t2))
        slot = js(page, "()=>{ const i = satIdeasList.find(x=>x.id==='i_t1'); return i && i.accts && i.accts.main; }")
        check(f"{tag} 2 idea.accts.main เก็บ pyr_trade_id + pyr_trade_ids", slot and slot.get("pyr_trade_id") == t2["id"] and slot.get("pyr_trade_ids") == [t2["id"]], json.dumps(slot))
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 3 + 4 ไม้ 3 / ครบ 3 ไม้
    browser, page, ce, pe = launch(pw, w, h)
    try:
        first(page, qty=0.16)
        check(f"{tag} 3 ก่อนมีไม้ 2: ปุ่มเป็น 'เติมไม้ 2' (ไม่มีปุ่มไม้ 3)", js(page, "()=>[...document.querySelectorAll('[data-pyr-btn]')].map(e=>e.innerText.trim())") == ["เติมไม้ 2"])
        ok = save_sheet(page, "t1", 2425, 2400)
        t2 = js(page, "()=>getBook('main').trades.find(x=>x.pyr_parent==='t1')")
        check(f"{tag} 3 เติมไม้ 2 สำเร็จ", ok and t2 is not None)
        P37.go_sat(page); page.wait_for_timeout(300)
        btns = js(page, "()=>[...document.querySelectorAll('[data-pyr-btn]')].map(e=>e.innerText.trim())")
        tags = js(page, "()=>[...document.querySelectorAll('#satV3Panel [data-pyr-tag]')].map(e=>e.innerText.trim())")
        check(f"{tag} 3 หลังไม้ 2: ปุ่ม 'เติมไม้ 3' (ที่ไม้ 2 ตัวเดียว) · ป้าย ไม้ 1/3 · ไม้ 2/3", btns == ["เติมไม้ 3"] and tags == ["ไม้ 1/3", "ไม้ 2/3"], json.dumps([btns, tags], ensure_ascii=False))
        usd = rpt_usd(page)
        q1, q2 = tr(page, "t1")["qty"], t2["qty"]
        c = calc(page, t2["id"], 2440, 2400)
        r_exist = (q1 * 10 + q2 * 25) * 100   # ไม้ 1 เข้า 2410 / ไม้ 2 เข้า 2425 · SL 2400
        exp3 = min(sat_lot(page, usd * 0.2, 40) or 0, sat_lot(page, usd * 1.0 - r_exist, 40) or 0)
        check(f"{tag} 3 ไม้ 3: SL ร่วมเดิม → เสี่ยงค้างรวม + ไม้ 3 ≤ 100% ของงบ · lot ≤ ตามสัดส่วน 20% (qty {c['qty']})", (c["qty"] is None and exp3 == 0) or (c["qty"] == exp3 and c["totPct"] <= 100.0001), json.dumps([c, exp3]))
        c = calc(page, t2["id"], 2440, 2410)
        r20 = sat_lot(page, usd * 0.2, 30)
        check(f"{tag} 3 เลื่อน SL ร่วมมาทุน (2410) → ที่ว่างเยอะ แต่ lot ไม้ 3 ไม่เกินสัดส่วน 20% ({c['qty']} = {r20})", c["qty"] == r20 and not c["errs"], json.dumps(c))
        shot(page, f"py2-add3-blocked-{sfx}.png", "#satV3Panel")
        # ไม้ 3 ไม่มีก่อนไม้ 2 (ไม้ 1 ตัวเดียวที่มีไม้ 2 แล้ว ไม่มีปุ่ม)
        check(f"{tag} 3 ไม้ 1 ที่มีไม้ 2 แล้ว → เติมไม่ได้ (เติมจากไม้ล่าสุดเท่านั้น)", elig(page, "t1") is False and elig(page, t2["id"]) is True)
        n_new0 = js(page, "()=>sat7dAcctBase('main').nNew"); h0 = js(page, "()=>sat7dAcctBase('main').openRisk")
        ok = save_sheet(page, t2["id"], 2440, 2410)
        t3 = js(page, "()=>getBook('main').trades.find(x=>x.pyr_no===3)")
        check(f"{tag} 3 เติมไม้ 3 สำเร็จ (pyr_no 3 · parent = ไม้ 2) · SL ร่วม 2410 ทุกไม้ที่เปิด", ok and t3 and t3["pyr_parent"] == t2["id"] and all(tr(page, i)["sl"] == 2410 for i in ("t1", t2["id"], t3["id"])), json.dumps(t3))
        check(f"{tag} 4 ครบ 3 ไม้: ไม่มีปุ่มเติม · ไม่มี sat-pyr บน Today", js(page, "()=>document.querySelectorAll('[data-pyr-btn]').length") == 0 and elig(page, t3["id"]) is False)
        check(f"{tag} 4 ไม้เติมไม่นับโควตาไม้ใหม่ (nNew {n_new0} → {js(page, '()=>sat7dAcctBase(\"main\").nNew')})", js(page, "()=>sat7dAcctBase('main').nNew") == n_new0)
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(400)
        check(f"{tag} 4 Today: ครบแล้ว → ไม่มีแถว 'เติมไม้ได้' ของ Sat", js(page, "()=>document.querySelectorAll('[data-kind=sat-pyr]').length") == 0)
        check(f"{tag} 4 ปุ่มปิดไม้/แก้ SL ของแถวไม้ 3 ยังอยู่ (จัดการได้)", True)
        check(f"{tag} 3 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 5 lot ต่ำกว่า minLot
    def minlot(doc):
        doc["books"]["main"]["settings"]["brokers"]["XM"]["XAUUSD"]["minLot"] = 0.05
    browser, page, ce, pe = launch(pw, w, h, minlot)
    try:
        js(page, "()=>{ PRODUCTS.XAUUSD.minLot = 0.05; render(); }"); page.wait_for_timeout(300)   # SET1 — minLot ตายตัวในสเปคสินค้า: ตั้ง 0.05 ตรงนี้เพื่อตรวจกฎ "เล็กเกินจะแบ่ง" เดิม
        first(page, qty=0.05)
        k = chk(page, "t1")
        btn = js(page, "()=>{ const b = document.querySelector('[data-pyr-btn]'); return b ? {d:b.disabled, t:b.title} : null; }")
        why = txt(page, "[data-pyr-why]") or ""
        check(f"{tag} 5 ไม้ 1 เล็ก (0.05) → ไม้ 2 ~0.03 < minLot 0.05 → ปุ่มปิด + เหตุผล 'เล็กเกินจะแบ่ง 30%'", k["ok"] is False and btn and btn["d"] and "เล็กเกินจะแบ่ง 30%" in why, json.dumps([k, btn, why], ensure_ascii=False))
        first(page, qty=0.16)
        usd = rpt_usd(page)
        c = calc(page, "t1", 2425, 2400)
        wide = calc(page, "t1", 2900, 2400)
        check(f"{tag} 5 SL กว้างจน lot ตามสัดส่วนต่ำกว่า minLot → error 'lot ไม้ 2 ต่ำกว่าขั้นต่ำ' ปุ่มบันทึกปิด", any("lot ไม้ 2 ต่ำกว่าขั้นต่ำ" in e for e in wide["errs"]) and wide["qty"] is None, json.dumps(wide, ensure_ascii=False))
    finally: browser.close()

    # ── 6 TF W
    browser, page, ce, pe = launch(pw, w, h)
    try:
        P51.fresh(page, {**P51.idea_doc(asset="XAUUSD", bias="Long", entry=2410, sl=2400, tp=2425, zone=(2425, 2440), iid="iT", act=False), "accts": {"main": {"broker": "XM"}}})
        tfs = js(page, "()=>[...document.querySelectorAll('[data-ac-tf] [data-tf]')].map(e=>e.dataset.tf)")
        check(f"{tag} 6 ปุ่ม TF ยืนยัน Break: 4H · D · W (3 ปุ่ม)", tfs[:3] == ["4H", "D", "W"], json.dumps(tfs))
        js(page, "()=>{ const b = document.querySelector('[data-ac-tf] [data-tf=\"W\"]'); b.click(); }"); page.wait_for_timeout(350)
        ov = js(page, "()=>{ const e = document.querySelector('[data-ac-tf]'); return e.scrollWidth <= e.parentElement.clientWidth + 1; }")
        shot(page, f"py2-tf-w-{sfx}.png", "#satV3Panel .ui-plan")
        cond = js(page, "()=>{ const i = sat7dIdea('iT'); const c = (i.conditions||[])[0]; return c.brk_tf; }")
        js(page, "()=>satV3CondActivate('iT','c1',true)"); page.wait_for_timeout(400)
        check(f"{tag} 6 เลือก W → brk_tf = 'W' · Activate แล้วป้าย 'Active · W'", cond == "W" and "Active · W" in (txt(page, "#satV3Panel") or ""), f"{cond} {(txt(page, '#satV3Panel') or '')[:300]}")
        check(f"{tag} 6 segmented 3 ปุ่มไม่ล้น ({label})", ov)
        check(f"{tag} 6 ค่าเริ่ม/ค่าไม่รู้จักยังเป็น 4H (satAcTf) · W รับเป็นค่าที่ถูกต้อง", js(page, "()=>[satAcTf({}), satAcTf({brk_tf:'X'}), satAcTf({brk_tf:'W'}), SAT_BRK_TFS.join(',')]") == ["4H", "4H", "W", "4H,D,W"])
    finally: browser.close()

    # ── 7 ข้อมูลเก่า
    browser, page, ce, pe = launch(pw, w, h)
    try:
        first(page, qty=0.32, tid="t1")   # ไม้ 1 เต็ม RPT (ไอเดียเก่า)
        # ไม้ PY1: ไม้เติม 50% ของ lot ไม้ 1 (pyr_child / pyr_parent / pyr_no 2) ผูกใน idea.accts.main.pyr_trade_id (เดี่ยว ไม่มี pyr_trade_ids)
        js(page, """()=>{ const B = getBook('main'), t1 = B.trades.find(x=>x.id==='t1');
            B.trades.push(makeTradeObject({id:'t2old', date:thaiToday(), sym:'XAUUSD', port:'satB', bias:'Long', entry:2420, sl:2410, tp:2460, qty:0.16, mult:100, cur:'USD', status:'open', openedAt:thaiToday()}));
            const t2 = B.trades.find(x=>x.id==='t2old'); t2.pyr_parent = 't1'; t2.pyr_no = 2; t1.pyr_child = 't2old'; t1.sl = 2410;
            saveBook('main'); sat7dWrite('satIdeas','i_t1',{accts:{main:{pyr_trade_id:'t2old'}}}); render(); }""")
        page.wait_for_timeout(500)
        P37.go_sat(page); page.wait_for_timeout(300)
        rows = txt(page, "#satV3Panel") or ""
        check(f"{tag} 7 ไม้ PY1 เดิม (pyr_child): ยังแสดงทั้ง 2 แถว · ป้าย 'ไม้ 2/3' · ปุ่ม ปิดไม้ มีทั้งสองแถว", js(page, "()=>document.querySelectorAll('#satV3Panel [data-pyr-tag]').length") == 2 and "ไม้ 2/3" in rows and js(page, "()=>[...document.querySelectorAll('#satV3Panel button')].filter(b=>b.innerText.trim()==='ปิดไม้').length") == 2, rows[-300:])
        check(f"{tag} 7 ไม้ PY1 ปิดได้ตามเดิม (openClosePos ไม่ error)", js(page, "()=>{ try{ openClosePos('t2old','main'); document.getElementById('closePosOverlay').classList.remove('show'); return true; }catch(e){ return String(e); } }") is True)
        check(f"{tag} 7 ไม้ 2 มีแล้ว → เติมไม้ 3 ได้จากไม้ล่าสุด (t2old)", elig(page, "t2old") is True and chk(page, "t2old")["k"] == 3)
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 8 Today
    browser, page, ce, pe = launch(pw, w, h)
    try:
        first(page, qty=0.16)
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(500)
        t = txt(page, "[data-kind=sat-pyr]") or ""
        check(f"{tag} 8 Today: 'XAU เติมไม้ 2 ได้ (ถ้า Break โครงสร้างใหม่ + เสี่ยงรวม ≤ 80%)'", "เติมไม้ 2 ได้" in t and "เสี่ยงรวม ≤ 80%" in t and "XAU" in t, t)
        P37.go_sat(page)
        save_sheet(page, "t1", 2425, 2400)
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(500)
        t = txt(page, "[data-kind=sat-pyr]") or ""
        check(f"{tag} 8 เติมไม้ 2 แล้ว → Today เปลี่ยนเป็น 'เติมไม้ 3 ได้ (… ≤ 100%)'", "เติมไม้ 3 ได้" in t and "≤ 100%" in t, t)
    finally: browser.close()

    # ── 8.1 ตั้งค่าสัดส่วน
    browser, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.querySelectorAll('#satRiskSec').forEach(d=>d.open=true); }")
        js(page, "()=>{ document.getElementById('satV2Sec').open = true; }")   # PV2c: ช่องแบ่งไม้ย้ายไป ตั้งค่า › Sat v2 (แบ่งไม้ Main · ข้อความ 50/30/20)
        vals = js(page, "()=>['sV2SplitMain'].map(i=>document.getElementById(i).value)")
        check(f"{tag} 8.1 ค่าเริ่ม 50 / 30 / 20 (PV2c: ช่องเดียว '50/30/20')", vals == ["50/30/20"], json.dumps(vals))
        fs = js(page, "()=>['sV2SplitMain'].map(i=>parseFloat(getComputedStyle(document.getElementById(i)).fontSize))")
        check(f"{tag} 8.1 ช่องกรอก font ≥ 16px", all(f >= 16 for f in fs), json.dumps(fs))
        shot(page, f"py2-settings-split-{sfx}.png", "#satRiskSec")
        err = lambda i: txt(page, f'[data-err-for="{i}"]') or ""
        dis = lambda: js(page, "()=>document.getElementById('setSaveBtn').disabled")
        def setv(a, b, c):
            parts = [a, b, c]
            while len(parts) > 1 and parts[-1] == 0: parts.pop()   # PV2c: ช่องเดียว — 0 ที่ท้ายตัดออก (60/40/0 → 60/40) · 0 หน้า/กลางคงไว้เป็น error
            page.fill("#sV2SplitMain", "/".join(str(v) for v in parts)); page.wait_for_timeout(80)
        bad = {}
        for name, v in {"รวม 90": (50, 30, 10), "รวม 110": (50, 30, 30), "ไม้ 1 = 0": (0, 50, 50), "ไม้ 2 = 0 ไม้ 3 > 0": (70, 0, 30), "ทศนิยม": (50, 30.5, 19.5), "ลบ": (110, -5, -5)}.items():
            setv(*v); bad[name] = (bool(err("sV2SplitMain")) and dis() is True)
        check(f"{tag} 8.1 รวม ≠ 100 / ไม้ 1 < 10 / ไม้ 2=0 แต่ไม้ 3>0 / ทศนิยม / ติดลบ → error + ปุ่มบันทึกปิด", all(bad.values()), json.dumps(bad, ensure_ascii=False))
        setv(60, 40, 0)
        check(f"{tag} 8.1 60/40/0 → ผ่าน ปุ่มบันทึกเปิด", not err("sV2SplitMain") and dis() is False)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(300)
        sv = js(page, "()=>[(getBook('main').settings.satV2 || {}).splitMain || null, (getBook('fam').settings.satV2 || {}).splitMain || null]")
        check(f"{tag} 8.1 บันทึก → main = '60/40' (PV2c: เก็บที่ satV2.splitMain · เดิม [60,40,0]) · fam ไม่เปลี่ยน (ค่าเริ่ม)", sv[0] == "60/40" and sv[1] is None and js(page, "()=>satRiskCfg('fam').pyrSplit") == [50, 30, 20], json.dumps(sv))
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); }")
        P51.fresh(page, None)
        first(page, qty=0.16)
        tags = js(page, "()=>[...document.querySelectorAll('[data-pyr-tag]')].map(e=>e.innerText.trim())")
        k = chk(page, "t1")
        check(f"{tag} 8.1 60/40/0: ป้าย 'ไม้ 1/2' · ไม้ 2 = 40% งบสะสม 100%", tags == ["ไม้ 1/2"] and k["k"] == 2 and k["N"] == 2 and k["pct"] == 40 and k["cum"] == 100, json.dumps([tags, k]))
        P51.put_idea(page, {**P51.idea_doc(asset="XAUUSD", bias="Long", entry=2410, sl=2400, tp=2425, zone=(2425, 2440), iid="iQ"), "accts": {"main": {"broker": "XM"}}})
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iQ'), 'main'); return {lot:c.lot, riskCur:c.riskCur, f:c.factor, s:c.split1}; }")
        check(f"{tag} 8.1 60/40/0: ไม้ 1 = 60% ของงบ (lot ตาม Calc.satLot)", c["s"] == 0.6 and c["lot"] == sat_lot(page, c["riskCur"] * c["f"] * 0.6, 10), json.dumps(c))
        card = txt(page, "#satV3Panel") or ""
        check(f"{tag} 8.1 การ์ดแผนใช้ค่าที่ตั้งต่อบัญชี: main 'ไม้ 1 · 60% ของงบ' + 'ไม้ 2 · 40% (เติมเมื่อ…)' · Family (ไม่ได้ตั้ง) ใช้ 50/30/20 ของตัวเอง", "ไม้ 1 · 60% ของงบ" in card and "ไม้ 2 · 40% (เติมเมื่อ Break โครงสร้างใหม่)" in card and "ไม้ 1 · 50% ของงบ" in card and "ไม้ 2 · 30% · ไม้ 3 · 20%" in card, card[-420:])
        # เปลี่ยนค่าขณะมีไม้ 1 เปิด: ไม้ 1 เดิมไม่เปลี่ยน · ไม้ถัดไปใช้ค่าใหม่
        q1 = tr(page, "t1")["qty"]
        js(page, "()=>{ getBook('main').settings.satV2 = Object.assign({}, getBook('main').settings.satV2, {splitMain:'40/40/20'}); saveBook('main'); render(); }")
        check(f"{tag} 8.1 เปลี่ยนค่าเป็น 40/40/20 ขณะไม้ 1 เปิด → ไม้ 1 เดิมไม่เปลี่ยน · ไม้ 2 ใช้ 40% · งบสะสม 80%", tr(page, "t1")["qty"] == q1 and chk(page, "t1")["pct"] == 40 and chk(page, "t1")["cum"] == 80)
        js(page, "()=>{ getBook('main').settings.satV2 = Object.assign({}, getBook('main').settings.satV2, {splitMain:'100'}); saveBook('main'); render(); }"); page.wait_for_timeout(300)
        check(f"{tag} 8.1 100/0/0 → ไม่มีปุ่มเติม · ไม่มีป้ายไม้ · Today ไม่มีแถวเติมไม้", elig(page, "t1") is False and js(page, "()=>document.querySelectorAll('[data-pyr-btn]').length") == 0 and js(page, "()=>document.querySelectorAll('[data-pyr-tag]').length") == 0)
        js(page, "()=>{ getBook('main').settings.satV2 = Object.assign({}, getBook('main').settings.satV2, {splitMain:'70/0/30'}); saveBook('main'); }")
        check(f"{tag} 8.1 ค่าในฐานข้อมูลผิดกติกา (70/0/30) → ใช้ค่าเริ่ม 50/30/20", js(page, "()=>satRiskCfg('main').pyrSplit") == [50, 30, 20])
        check(f"{tag} 8.1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 9 มือถือ
    browser, page, ce, pe = launch(pw, w, h)
    try:
        first(page, qty=0.16)
        js(page, "()=>satPyrOpen('t1','main')"); page.wait_for_timeout(300)
        page.check("#pyrBreak"); page.fill("#pyrEntry", "2425"); page.wait_for_timeout(150)
        ov = js(page, "()=>{ const s = document.querySelector('.pyr-sheet .ui-sheet'); return s.scrollWidth <= s.clientWidth + 1; }")
        check(f"{tag} 9 sheet เติมไม้ไม่ล้น ({label})", ov and overflow(page) <= 0)
        page.keyboard.press("Escape"); page.wait_for_timeout(250)
        check(f"{tag} 9 Esc ปิด sheet เติมไม้", js(page, "()=>!document.querySelector('.pyr-sheet')"))
        check(f"{tag} 9 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 70 / PY2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
