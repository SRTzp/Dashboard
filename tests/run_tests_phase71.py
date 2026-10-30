#!/usr/bin/env python3
"""CO1 — Sat แผนข้ามสัปดาห์: แผนที่ยังไม่เข้ายกไปสัปดาห์ถัดไป + ต้องกดยืนยัน · ไม้ที่ถือข้ามสัปดาห์แสดงต่อ · เทส 71
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย (สัปดาห์นี้ = 2026-09-27) · สัปดาห์ก่อน = 2026-09-20
ภาพ tests/screenshots/co1-{carried,carried-nobias,held-cross-week}-{1440,390}.png
รัน: python3 run_tests_phase71.py"""
import json, os
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
WK = "2026-09-27"; PREV = "2026-09-20"; PREV2 = "2026-09-13"


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


def fixture(strict=False, picks=None):
    def m(doc):
        s = doc["books"]["main"]["settings"]
        for k in ("BTCUSD", "S50", "BRENT"):
            s["brokers"]["XM"][k] = {"contract": 100, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}
        if strict: s["satWeekPick"] = {"2026-01-04": ["XAUUSD"], **({WK: picks} if picks is not None else {})}
    return m


def launch(pw, w, h, strict=False, picks=None):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(strict, picks))
    P51.fresh(page, None)
    return browser, page, ce, pe


def put_prev(page, asset="XAUUSD", week=PREV, iid="iC", bias="Long", act=True, created="2026-09-21T01:00:00.000Z", extra=None):
    entry, sl, tp = (2410, 2400, 2425) if bias == "Long" else (2410, 2420, 2395)
    zone = (2425, 2440) if bias == "Long" else (2395, 2380)
    d = {**P51.idea_doc(asset=asset, bias=bias, entry=entry, sl=sl, tp=tp, zone=zone, iid=iid, act=act), "accts": {"main": {"broker": "XM"}}}
    d.update(extra or {})
    js(page, "([i,w,c])=>{ sat7dWrite('satIdeas', i.id, Object.assign({}, i, {week:w, created_at:c, planned:true, setups:[], status:'active'})); }", [d, week, created])
    page.wait_for_timeout(450)


def go(page): P37.go_sat(page); page.wait_for_timeout(250); P37.open_plan(page)
def idea(page, iid): return js(page, "(i)=>{ const x = sat7dIdea(i); return x ? JSON.parse(JSON.stringify(x)) : null; }", iid)
def ok_btn(page, iid):
    return js(page, "(i)=>{ const b = document.querySelector('[data-carry-ok=\"'+i+'\"]'); return b ? {d:b.disabled} : null; }", iid)
def msg(page): return txt(page, "[data-carry-msg]") or ""
def set_bias(page, bias, asset="XAUUSD"): P11.wk(page, asset, bias, "up")
def clear_bias(page): js(page, "()=>{ satWeekMap = {}; satV3Render(); }"); page.wait_for_timeout(250)
def banner(page, iid="iC"): return txt(page, f"[data-carry-banner='{iid}']") or ""


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 แผน planned สัปดาห์ก่อน → สัปดาห์นี้แสดงพร้อมป้ายยกมา · บันทึก order / Activate ไม่ได้
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", act=True)
        put_prev(page, iid="iN", act=False, asset="XAUUSD", extra={"conditions": [{"id": "c1", "text": "Break & Pullback @ 2400", "tp_from": 2425, "tp_to": 2440, "inval": None, "active": False, "saved": True}]})
        go(page)
        b = banner(page)
        check(f"{tag} 1 แผน planned สัปดาห์ก่อน (ไม่มีไม้) → ขึ้นในสัปดาห์นี้พร้อมแถบ 'ยกมาจาก …' (PF1: ไม่มี 'เช็ก Bias ใหม่') + ปุ่ม ใช้ต่อสัปดาห์นี้ · ไม่ใช้", "ยกมาจาก" in b and "Bias" not in b and "ใช้ต่อสัปดาห์นี้" in b and "ไม่ใช้" in b, b)
        check(f"{tag} 1 ไม่อยู่ในประวัติ 'ร่างไม่ได้ใช้' อีกแล้ว (ยังไม่ปิด)", js(page, "()=>!document.querySelector('[data-closed-idea=iC]')"))
        shot(page, f"co1-carried-{sfx}.png", "#satV3Panel")
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iC'), 'main'); return {ready:c.ready, blk:c.carryBlock, act: !!satV3ActiveCond(sat7dIdea('iC'))}; }")
        n0 = js(page, "()=>getBook('main').trades.length")
        js(page, "()=>{ satV3SaveSlot('iC','main'); satV3SaveOffplanAccount('iC','main'); }"); page.wait_for_timeout(300)
        check(f"{tag} 1 ก่อนยืนยัน: บันทึก order ไม่ได้ (carryBlock) · ไม่มีไม้ใหม่ · เงื่อนไขที่เคย active แสดงเป็นรอ (ไม่มีข้อ Active) แต่ค่า active เดิมไม่ลบ", c["ready"] is False and "ยืนยัน" not in (c["blk"] or "x") and "ยกมาจากสัปดาห์ก่อน" in (c["blk"] or "") and c["act"] is False and js(page, "()=>getBook('main').trades.length") == n0 and idea(page, "iC")["conditions"][0]["active"] is True, json.dumps(c, ensure_ascii=False))
        a = js(page, "()=>{ satV3CondActivate('iN','c1',true); return !!(sat7dIdea('iN').conditions||[]).find(c=>c.id==='c1' && c.active); }")
        dis = js(page, "()=>[...document.querySelectorAll('.ui-plan[data-id=iN] .ui-cond-act input, [data-id=iN] .ui-wc-act')].filter(e=>!e.checked).every(e=>e.disabled)")
        check(f"{tag} 1 Activate เงื่อนไขของแผนยกมาไม่ได้ (แม้เงื่อนไขครบ) · ช่อง Activate disabled", a is False and dis is True)
        js(page, "()=>satV3PlanEdit('iC','sl',2401)"); page.wait_for_timeout(250)
        check(f"{tag} 1 แก้ค่าในแผนยกมาได้ (SL → 2401)", idea(page, "iC")["sl"] == 2401)
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 2 ยังไม่ทำ Bias → ใช้ต่อปิด · ทำ Bias → ใช้ต่อ
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", act=True)
        clear_bias(page); go(page)
        o = ok_btn(page, "iC")
        check(f"{tag} 2 PF1 — ไม่ต้องทำ Bias สัปดาห์นี้ → ปุ่ม 'ใช้ต่อ' เปิดได้ · ไม่มีข้อความ 'ทำ Bias สัปดาห์นี้ก่อน'", o and o["d"] is False and "Bias" not in msg(page), f"{o} {msg(page)}")
        shot(page, f"co1-carried-nobias-{sfx}.png", "#satV3Panel")
        set_bias(page, "Long"); go(page)   # PF1 — ตั้ง Bias เก่าของ Strategy ไม่มีผล (พิสูจน์ว่าไม่อ่าน)
        o = ok_btn(page, "iC")
        check(f"{tag} 2 ตั้ง Bias เก่า (Long) ไม่เปลี่ยนอะไร → ปุ่ม 'ใช้ต่อ' เปิด · ไม่มีป้ายสวน Bias", o and o["d"] is False and js(page, "()=>!document.querySelector('[data-carry-offbias]')"))
        page.locator("[data-carry-ok='iC']").click(); page.wait_for_timeout(500)
        d = idea(page, "iC")
        check(f"{tag} 2 กด ใช้ต่อ → week = สัปดาห์นี้ · carried_from = [สัปดาห์เดิม]", d["week"] == WK and d["carried_from"] == [PREV], json.dumps([d["week"], d.get("carried_from")]))
        check(f"{tag} 2 แถบยกมาหาย · เงื่อนไขครบที่เคย active → Active อีกครั้ง (เข้าขั้นหน้างาน)", js(page, "()=>!document.querySelector('[data-carry-banner]')") and js(page, "()=>!!satV3ActiveCond(sat7dIdea('iC'))"))
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iC'), 'main'); return {ready:c.ready, blk:c.carryBlock}; }")
        js(page, "()=>satV3SaveSlot('iC','main')"); page.wait_for_timeout(350)
        check(f"{tag} 2 หลังยืนยัน: ready · บันทึก order ได้", c["ready"] is True and not c["blk"] and js(page, "()=>getBook('main').trades.some(t=>t.sym==='XAUUSD' && t.status==='plan')"))
    finally: browser.close()

    # ── 3 Bias ใหม่สวนทิศ → ยืนยันได้ แต่ถูกบล็อก SR1
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", bias="Long", act=True)
        set_bias(page, "Short"); go(page)
        red = js(page, "()=>!!document.querySelector('[data-carry-banner] [data-carry-offbias]')")
        o = ok_btn(page, "iC")
        check(f"{tag} 3 PF1 — Bias เก่า Short สวนแผน Long → แถบไม่มีป้ายสวน Bias · ปุ่ม ใช้ต่อ กดได้", not red and o and o["d"] is False and "สวน Bias" not in banner(page))
        page.locator("[data-carry-ok='iC']").click(); page.wait_for_timeout(450)
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iC'), 'main'); return {ready:c.ready, off:c.offBias}; }")
        n0 = js(page, "()=>getBook('main').trades.length")
        js(page, "()=>{ satV3SaveSlot('iC','main'); satV3SaveOffplanAccount('iC','main'); }"); page.wait_for_timeout(300)
        check(f"{tag} 3 PF1 — ยืนยันแล้ว (week = สัปดาห์นี้) → ไม่ถูกบล็อกด้วยสวน Bias (ไม่มีป้าย/เหตุผลสวน Bias)", idea(page, "iC")["week"] == WK and not c["off"] and "สวน Bias" not in (txt(page, "#satV3Panel") or ""))
    finally: browser.close()

    # ── 4 ไม่ใช้
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", act=True); set_bias(page, "Long"); go(page)
        page.locator("[data-carry-drop='iC']").click(); page.wait_for_timeout(450)
        d = idea(page, "iC")
        check(f"{tag} 4 ไม่ใช้ → แผนปิด (status closed · carry_unused) · ไม่ถูกลบ · week เดิม", d and d["status"] == "closed" and d.get("carry_unused") is True and d["week"] == PREV)
        js(page, "()=>{ satV3ClosedOpen = true; satV3Render(); }"); page.wait_for_timeout(250)
        row = txt(page, "[data-closed-idea=iC]") or ""
        check(f"{tag} 4 อยู่ในประวัติ 'แผนที่ปิดแล้ว' เป็น 'ร่างไม่ได้ใช้' · แถบยกมาหาย", "ร่างไม่ได้ใช้" in row and js(page, "()=>!document.querySelector('[data-carry-banner]')"), row)
    finally: browser.close()

    # ── 5 มีไม้เปิดจากสัปดาห์ก่อน (ไม้ 1 + ไม้ 2 ของ PY2) → แสดงทันที ไม่มีแถบยืนยัน
    browser, page, ce, pe = launch(pw, w, h)
    try:
        p36.mk_first(page, "t1", entry=2410, sl=2400, qty=0.16)
        js(page, """()=>{ sat7dWrite('satIdeas','i_t1',{week:'2026-09-20'}); }"""); page.wait_for_timeout(300)
        js(page, "()=>{ const t = getBook('main').trades.find(x=>x.id==='t1'); t.date='2026-09-21'; t.openedAt='2026-09-21'; saveBook('main'); }")
        # เติมไม้ 2 ผ่านฟังก์ชันเดียวกับ sheet
        go(page)
        P37.go_sat(page)
        js(page, "()=>satPyrOpen('t1','main')"); page.wait_for_timeout(300)
        page.check("#pyrBreak"); page.fill("#pyrEntry", "2425"); page.fill("#pyrSL", "2400"); page.wait_for_timeout(200)
        page.click("#pyrSave"); page.wait_for_timeout(450)
        iw = idea(page, "i_t1")
        check(f"{tag} 5 ไอเดียมีไม้ 1 + ไม้ 2 และ week = สัปดาห์ก่อน", iw["week"] == PREV and js(page, "()=>getBook('main').trades.filter(x=>x.pyr_parent).length") == 1)
        go(page)
        rows = js(page, "()=>document.querySelectorAll('#satV3Panel .ui-row').length")
        check(f"{tag} 5 สัปดาห์นี้ยังแสดงแถวไม้ทั้ง 2 ไม้ (ไม่ต้องยืนยัน) · ไม่มีแถบยกมา · ไม่มีในประวัติ", rows == 2 and js(page, "()=>!document.querySelector('[data-carry-banner]')") and js(page, "()=>!document.querySelector('[data-closed-idea=i_t1]')"), str(rows))
        shot(page, f"co1-held-cross-week-{sfx}.png", "#satV3Panel")
        btns = js(page, "()=>[...document.querySelectorAll('#satV3Panel [data-pyr-btn]')].map(b=>b.innerText.trim())")
        check(f"{tag} 5 เติมไม้ 3 ได้จากแถวข้ามสัปดาห์ (ปุ่ม 'เติมไม้ 3')", btns == ["เติมไม้ 3"], json.dumps(btns, ensure_ascii=False))
        t2 = js(page, "()=>getBook('main').trades.find(x=>x.pyr_parent)")
        js(page, "([i])=>{ openTradeEdit(i,'main'); }", [t2["id"]]); page.wait_for_timeout(250)
        page.fill("#tSL", "2405"); page.click("#teSaveBtn"); page.wait_for_timeout(300)
        check(f"{tag} 5 เลื่อน SL ไม้ข้ามสัปดาห์ได้ (ใช้กับทั้ง 2 ไม้)", js(page, "()=>getBook('main').trades.filter(t=>t.status==='open').every(t=>t.sl===2405)"))
        js(page, "()=>{ const B = getBook('main'); B.trades.forEach(t=>{ t.status='closed'; t.exitPrice=2420; t.exitDate=thaiToday(); }); saveBook('main'); satV3IdeaWrite('i_t1',{status:'closed'}); render(); }"); page.wait_for_timeout(450)
        check(f"{tag} 5 ปิดไม้หมดได้ → แถวหาย · อยู่ในประวัติ", js(page, "()=>document.querySelectorAll('#satV3Panel .ui-row').length") == 0)
        check(f"{tag} 5 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 6 ยกต่อ 2 สัปดาห์ติด → ต้องยืนยันทุกครั้ง · carried_from 2 ค่า
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", week=PREV2, act=True); set_bias(page, "Long"); go(page)
        check(f"{tag} 6 แผนอายุ 2 สัปดาห์ → ขึ้นแถบยกมา ('ยกมาจาก' สัปดาห์เก่ากว่า)", "ยกมาจาก" in banner(page))
        page.locator("[data-carry-ok='iC']").click(); page.wait_for_timeout(400)
        # จำลองสัปดาห์ถัดไป: ยืนยันไว้เมื่อสัปดาห์ก่อน (week = PREV · carried_from [PREV2]) แล้วยังไม่เข้า → ต้องยืนยันอีก
        js(page, "([i,w,f])=>{ sat7dWrite('satIdeas', i, {week:w, carried_from:f}); }", ["iC", PREV, [PREV2]]); page.wait_for_timeout(400)
        go(page)
        check(f"{tag} 6 สัปดาห์ถัดไป ยังไม่เข้า → ขึ้นแถบยืนยันอีก (ไม่จำกัดจำนวนครั้ง)", js(page, "()=>!!document.querySelector('[data-carry-banner=iC]')"))
        page.locator("[data-carry-ok='iC']").click(); page.wait_for_timeout(450)
        d = idea(page, "iC")
        check(f"{tag} 6 ยืนยันครั้งที่ 2 → carried_from = [สัปดาห์เก่า, สัปดาห์ก่อน] (2 ค่า) · week = สัปดาห์นี้", d["week"] == WK and d["carried_from"] == [PREV2, PREV], json.dumps([d["week"], d["carried_from"]]))
        put_prev(page, iid="iOld", week="2026-06-14", act=True)
        go(page)
        check(f"{tag} 6 แผนเก่ากว่า 8 สัปดาห์ → ไม่ยกมา (ร่างที่ไม่ได้ใช้ในประวัติ)", js(page, "()=>!document.querySelector('[data-carry-banner=iOld]')") and js(page, "()=>satV3ClosedKind(sat7dIdea('iOld'))") == "unused")
    finally: browser.close()

    # ── 7 ยกมา 4 Asset (เกิน 3)
    browser, page, ce, pe = launch(pw, w, h, strict=True, picks=[])
    try:
        for i, a in enumerate(("XAUUSD", "BTCUSD", "S50", "BRENT")):
            put_prev(page, asset=a, iid=f"i{a}", created=f"2026-09-2{i}T01:00:00.000Z")
            set_bias(page, "Long", a)
        go(page)
        pk = js(page, "()=>satWeekPickList()")
        check(f"{tag} 7 ยกมา 4 Asset → 3 ตัวแรกอยู่ใน pick สัปดาห์ใหม่โดยอัตโนมัติ", pk == ["XAUUSD", "BTCUSD", "S50"], json.dumps(pk))
        js(page, "()=>{ const e = document.querySelector('[data-wa-park]'); if(e) e.open = true; waParkOpen = true; }")
        park = txt(page, "[data-wa-park]") or ""
        o = ok_btn(page, "iBRENT")
        check(f"{tag} 7 ตัวที่ 4 (BRENT) อยู่แถบ 'ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้' · ปุ่ม ใช้ต่อ ปิด + 'ครบ 3 ตัวแล้ว'", "BRENT" in park.upper() and o and o["d"] is True and "ครบ 3" in (txt(page, "[data-carry-banner=iBRENT] [data-carry-msg]") or ""), f"{park} {o}")
        js(page, "()=>waRemove('S50')"); page.wait_for_timeout(350)
        o = ok_btn(page, "iBRENT")
        check(f"{tag} 7 เอา S50 ออกจาก pick → ใช้ต่อ BRENT เปิด · กดแล้ว BRENT เข้า pick + week สัปดาห์นี้", o and o["d"] is False, str(o))
        page.locator("[data-carry-ok='iBRENT']").click(); page.wait_for_timeout(450)
        check(f"{tag} 7 BRENT ใน pick แล้ว · แผนยืนยันแล้ว", "BRENT" in js(page, "()=>satWeekPickList()") and idea(page, "iBRENT")["week"] == WK)
        page.locator("[data-carry-drop='iBTCUSD']").click(); page.wait_for_timeout(450)
        check(f"{tag} 7 ไม่ใช้ (BTCUSD ไม่มีแผน/ไม้อื่น) → เอา Asset ออกจาก pick", "BTCUSD" not in js(page, "()=>satWeekPickList()") and idea(page, "iBTCUSD")["status"] == "closed", json.dumps(js(page, "()=>satWeekPickList()")))
    finally: browser.close()

    # ── 8 Today
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", act=True); put_prev(page, iid="iD2", act=False, created="2026-09-22T01:00:00.000Z"); set_bias(page, "Long")
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(500)
        t = js(page, "()=>[...document.querySelectorAll('[data-kind=sat-carry]')].map(e=>e.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} 8 Today: 'XAU แผนยกมา · รอยืนยัน' ≤ 1 แถวต่อ Asset (มี 2 แผน XAUUSD → 1 แถว)", len(t) == 1 and "XAU" in t[0] and "แผนยกมา · รอยืนยัน" in t[0], json.dumps(t, ensure_ascii=False))
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        js(page, "()=>satV3CarryConfirm('iC')"); page.wait_for_timeout(300)
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(400)
        t = js(page, "()=>document.querySelectorAll('[data-kind=sat-carry]').length")
        check(f"{tag} 8 ยืนยัน iC แล้วยังเหลือ iD2 → ยัง 1 แถว", t == 1)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        js(page, "()=>satV3CarryDrop('iD2')"); page.wait_for_timeout(300)
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(400)
        check(f"{tag} 8 ไม่ใช้ iD2 → แถวรอยืนยันหาย (ปกติ = เงียบ)", js(page, "()=>document.querySelectorAll('[data-kind=sat-carry]').length") == 0)
        check(f"{tag} 8 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 9 มือถือ
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_prev(page, iid="iC", act=True); clear_bias(page); go(page)
        r = js(page, """()=>{ const b = document.querySelector('[data-carry-banner]'); const r = b.getBoundingClientRect();
            return {over:[...b.querySelectorAll('*')].some(e=>e.getBoundingClientRect().right > window.innerWidth + 0.5), w:r.width, vw:window.innerWidth, btn:[...b.querySelectorAll('button')].map(e=>e.getBoundingClientRect().height)}; }""")
        check(f"{tag} 9 แถบยกมา + ปุ่มไม่ล้น ({label}) · ปุ่มสูง ≥ 34px", not r["over"] and r["w"] <= r["vw"] and all(x >= 34 for x in r["btn"]) and overflow(page) <= 0, json.dumps([r, overflow(page)]))
        check(f"{tag} 9 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 71 / CO1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
