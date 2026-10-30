#!/usr/bin/env python3
"""BR1 — แก้รายชื่อโบรก (เพิ่ม/ลบ/เปลี่ยนชื่อ) · ชื่อที่แสดงของสินค้า Sat · ซ่อนสินค้าที่ไม่เทรด · เทส 54
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย
ภาพ tests/screenshots/br1-{broker-sheet,broker-renamed-plan,asset-hidden-strategy}-{1440,390}.png
รัน: python3 run_tests_phase54.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase51 as P51

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-BR1.html"))
results = []
js, T = P37.js, P38.T
CLK = "2026-10-01T05:00:00Z"
OV = "#sat7dBrokerOverlay"


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
    doc = P38.doc38(clean=True)
    for b in doc["books"].values(): b["settings"].pop("satWeekPick", None)   # WA1fix — doc38 ใส่ pick ให้ชุดเก่า · ชุด WA1+ เริ่มจากว่าง
    if mutate: mutate(doc)
    return P39.launch(pw, w, h, doc=doc, clean=True, iso=CLK, pick=False)


def settings(page, key): return js(page, "(k)=>{ const v = tdSettings()[k]; return v===undefined ? null : v; }", key)
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
def opensheet(page):
    js(page, "()=>sat7dBrokerOpen()"); page.wait_for_timeout(350)
def save(page):
    page.locator(f"{OV} [data-br-save]").click(); page.wait_for_timeout(450)
def txt(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def cnt_ov(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def sheet_open(page): return js(page, "()=>document.getElementById('sat7dBrokerOverlay') && document.getElementById('sat7dBrokerOverlay').classList.contains('show')")
def labels(page): return js(page, "()=>SAT_ASSETS.map(a=>sat7dLabel(a.key))")
def tiles(page): return js(page, "()=>[...document.querySelectorAll('.ui-tile[data-key]')].map(e=>e.dataset.key)")


def idea(asset="XAUUSD", broker="XM", iid="iD", act=True, **kw):
    d = P51.idea_doc(asset=asset, iid=iid, act=act, **kw)
    d["accts"] = {"main": {"broker": broker}}
    return d


def lot_of(page, i, acct="main"):
    return js(page, """([i,a])=>{ i.week = wpWeekKey(); const c = satV3PlanAcctCalc(i, a); return {lot:c.lot, broker:c.chosen ? c.chosen.broker : null}; }""", [i, acct])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ── 1 ไม่มี brokerList / satAssetCfg → เหมือนเดิม (เทียบกับไฟล์ก่อน BR1)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        P51.fresh(page, idea())
        js(page, "()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: เทียบ lot กับไฟล์ก่อนแก้ → ไม้ 1 เข้าเต็ม RPT (100/0/0)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50']); satV3Render(); }")   # WA1fix: ไม่มีโหมด legacy → เลือก 3 ตัวของสัปดาห์นี้ (ตัวที่ 4 = Brent ตรวจที่รายชื่อสินค้าทั้งหมด)
        now_lot = lot_of(page, idea())
        check(f"{tag} 1 ไม่มีฟิลด์ใหม่: brokerList/satAssetCfg ไม่มี · รายชื่อโบรก = XM/IC/Pi · ชื่อสินค้า = XAUUSD/BTC/S50/Brent", settings(page, "brokerList") is None and settings(page, "satAssetCfg") is None
              and js(page, "()=>sat7dBrokers()") == ["XM", "IC", "Pi"] and js(page, "()=>brokerList().map(b=>b.name)") == ["XM", "IC", "Pi"] and labels(page) == ["XAUUSD", "BTC", "S50", "Brent"], json.dumps(labels(page)))
        check(f"{tag} 1 Strategy มีช่องตาม pick ของสัปดาห์ (3 · เพดาน WA1fix) · สินค้าทั้งหมดยัง 4 · lot XAUUSD (XM) คำนวณได้", len(tiles(page)) == 3 and js(page, "()=>satAssets({all:true}).length") == 4 and (now_lot["lot"] or 0) > 0 and now_lot["broker"] in ("", None), json.dumps([tiles(page), now_lot]))
        opensheet(page)
        sec = js(page, f"""()=>({{bk:[...document.querySelectorAll('{OV} [data-bk-name]')].map(e=>e.value), as:[...document.querySelectorAll('{OV} [data-as-label]')].map(e=>e.placeholder),
              rows:[...document.querySelectorAll('{OV} .s7BAcct[data-acct=main] .s7BRow')].map(e=>e.dataset.broker), assetRows:[...document.querySelectorAll('{OV} .s7BAcct[data-acct=main] .s7BRow[data-broker=XM] .s7BA')].map(e=>e.dataset.asset)}})""")
        check(f"{tag} 1 หน้าตั้งโบรก: ส่วน โบรก = XM/IC/Pi · ส่วน สินค้า = 4 ตัว · รายบัญชีวนตามรายชื่อ · แถวสินค้า 4 ตัว", sec == {"bk": [], "as": ["XAUUSD", "BTC", "S50", "Brent"], "rows": [], "assetRows": []}, json.dumps(sec))
        shot(page, f"br1-broker-sheet-{sfx}.png", f"{OV} .modal")
        # 8 ยกเลิก = ไม่มีอะไรเปลี่ยน
        page.locator(f"{OV} [data-as-label=XAUUSD]").fill("ZZ")
        page.locator(f"{OV} [data-br-cancel]").click(); page.wait_for_timeout(300)
        check(f"{tag} 8 ยกเลิก = ไม่มีอะไรเปลี่ยน (brokerList / satAssetCfg ยังไม่มี · ชื่อเดิม)", not sheet_open(page) and settings(page, "brokerList") is None and settings(page, "satAssetCfg") is None and js(page, "()=>brokerName('XM')") == "XM")
        if w < 500:
            opensheet(page)
            m = js(page, f"""()=>{{ const fs=[...document.querySelectorAll('{OV} input[type=number],{OV} input[type=text],{OV} select')].map(e=>parseFloat(getComputedStyle(e).fontSize)); return {{min:Math.min(...fs), n:fs.length, over:document.documentElement.scrollWidth-innerWidth, ovr:document.querySelector('{OV} .modal').scrollWidth - document.querySelector('{OV} .modal').clientWidth}}; }}""")
            check(f"{tag} 8 390px: หน้าตั้งโบรกไม่ล้นแนวนอน · ช่องกรอก font ≥ 16", m["over"] <= 0 and m["ovr"] <= 1 and m["min"] >= 16, json.dumps(m))
            page.locator(f"{OV} [data-br-cancel]").click()
        check(f"{tag} 1 console ไม่มี error (ค่าเริ่มต้น)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()
    # เทียบ lot ก่อน/หลัง BR1 (fixture เดียวกัน)
    saved = P39.INDEX; P39.INDEX = BACKUP
    try:
        browser, context, page, ce, pe, dialogs = launch(pw, w, h)
        try:
            P51.fresh(page, idea()); old_lot = js(page, """(i)=>{ i.week = wpWeekKey(); const c = satV3PlanAcctCalc(i, 'main'); return {lot:c.lot, broker:c.chosen ? c.chosen.broker : null}; }""", idea())
        finally: browser.close()
    finally: P39.INDEX = saved
    check(f"{tag} 1 lot + โบรกที่เลือก เท่าก่อน BR1 (fixture เดียวกัน)", old_lot["lot"] == now_lot["lot"] and old_lot["lot"], json.dumps([old_lot, now_lot]))

    print("RETIRED - [p54] §2 เปลี่ยนชื่อโบรก · §3 เพิ่มโบรก · §4 ลบโบรก (≈25 เช็ก): UI โบรกถูกเอาออก (SET1) — ดู tests/SET1_retired.md")

    # ── 5 ชื่อที่แสดงของสินค้า
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        P51.fresh(page, idea())
        js(page, "()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'told', date:'2026-09-20', sym:'XAUUSD', port:'satB', bias:'Long', entry:2400, sl:2390, tp:2420, qty:0.1, mult:100, cur:'USD', status:'closed', exitPrice:2410, exitDate:'2026-09-25'})); saveBook('main'); render(); }")
        opensheet(page)
        for bad, key, why in (("Brent", "S50", "ซ้ำสินค้าอื่น"), ("x" * 13, "S50", "ยาวเกิน 12")):
            page.locator(f"{OV} [data-as-label={key}]").fill(bad); save(page)
            wm = txt(page, f"{OV} [data-as-warn={key}]") or ""
            check(f"{tag} 5 ชื่อที่แสดง {why} → เตือนใต้ช่อง ไม่บันทึก", wm != "" and sheet_open(page) and settings(page, "satAssetCfg") is None, wm)
            page.locator(f"{OV} [data-as-label={key}]").fill("")
        page.locator(f"{OV} [data-as-label=XAUUSD]").fill("XAU"); save(page)
        check(f"{tag} 5 เปลี่ยน XAUUSD → 'XAU': satAssetCfg = {{XAUUSD:{{label:'XAU'}}}} · key ไม่เปลี่ยน", settings(page, "satAssetCfg") == {"XAUUSD": {"label": "XAU"}} and "XAU" in labels(page), json.dumps(settings(page, "satAssetCfg")))
        P51.fresh(page, idea())
        tile = txt(page, ".ui-tile[data-key=XAUUSD] .ui-tile-a")
        check(f"{tag} 5 Strategy: ช่องแสดง 'XAU' (data-key ยัง XAUUSD)", tile == "XAU", tile)
        plan = txt(page, "#satV3Panel") or ""
        check(f"{tag} 5 การ์ดแผน: ชื่อสินค้า 'XAU'", "XAU" in plan and "XAUUSD" not in plan, plan[:200])
        js(page, "()=>{ const B=getBook('main'); B.trades = B.trades.filter(t=>t.id==='told'); saveBook('main'); reset_ideas_stub && 0; }") if False else None
        js(page, "()=>{ satWeekMap = {}; switchTab('today'); }"); page.wait_for_timeout(600)
        bias_row = js(page, "()=>{ const e=document.querySelector('[data-kind=bias]'); return e ? e.innerText : ''; }")
        check(f"{tag} 5 PF3 Today: ไม่มีแถว เช็ก Bias (งานถอดแล้ว) · แถวเช็กแผน Sat รายวันยังแสดงชื่อสินค้า 'XAU'", bias_row == "" and "XAU" in (js(page, "()=>{ const e=document.querySelector('[data-kind=sat-daily]'); return e ? e.innerText : ''; }") or ""), bias_row)
        js(page, "()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'told', date:'2026-09-20', sym:'XAUUSD', port:'satB', bias:'Long', entry:2400, sl:2390, tp:2420, qty:0.1, mult:100, cur:'USD', status:'closed', exitPrice:2410, exitDate:'2026-09-25'})); saveBook('main'); render(); }")
        js(page, "()=>{ switchTab('journal'); }"); page.wait_for_timeout(500)
        jt = js(page, "()=>document.body.innerText")
        check(f"{tag} 5 Journal/ไม้เดิม: sym XAUUSD แสดงเป็น 'XAU' (ไม้ที่เก็บ sym เดิมไม่ถูกแก้)", re.search(r"\bXAU\s+Long", jt) is not None and "XAUUSD" not in jt and js(page, "()=>getBook('main').trades.find(t=>t.id==='told').sym") == "XAUUSD")
        opensheet(page)
        check(f"{tag} 5 หน้า Sat assets (SET1): แถวสินค้าแสดงชื่อ XAUUSD · ไม่มีแถวโบรกรายบัญชี", cnt_ov(page, f"{OV} [data-as-row=XAUUSD]") == 1 and cnt_ov(page, f"{OV} .s7BRow") == 0)
        page.locator(f"{OV} [data-as-label=XAUUSD]").fill("   "); save(page)
        check(f"{tag} 5 ว่าง → กลับเป็นชื่อเดิม 'XAUUSD' · satAssetCfg ถูกลบ", labels(page)[0] == "XAUUSD" and settings(page, "satAssetCfg") is None, json.dumps(settings(page, "satAssetCfg")))
        week_key_ok = js(page, "()=>Object.keys(satWeekMap||{}).every(k=>/^\\d{4}-\\d{2}-\\d{2}$/.test(k))")
        check(f"{tag} 5 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 6 (WA1: แทน "ซ่อน" ด้วย "ไม่ได้เลือกสัปดาห์นี้") เอา BRENT ออกจากสัปดาห์นี้
    def with_brent(doc):
        doc["books"]["main"]["settings"]["brokers"]["XM"]["BRENT"] = {"contract": 100, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}
    def pickw(page, lst):
        js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); render(); }", lst); page.wait_for_timeout(300)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_brent)
    try:
        P51.fresh(page, None)
        js(page, "()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tbr', date:'2026-09-20', sym:'BRENT', port:'satB', bias:'Long', entry:80, sl:78, tp:84, qty:1, mult:100, cur:'USD', status:'closed', exitPrice:82, exitDate:'2026-09-24'})); saveBook('main'); }")
        js(page, "()=>{ const B=getBook('main'); B.settings.routine = Object.assign({}, B.settings.routine||{}, {satDaily:['XAUUSD','BTC','S50','BRENT']}); saveBook('main'); render(); }")
        pickw(page, ["XAUUSD", "BTCUSD", "S50"])
        P51.fresh(page, None)
        check(f"{tag} 6 เลือกสัปดาห์นี้ 3 ตัว (ไม่มี BRENT): บันทึก satWeekPick ได้ ไม่มีคำเตือน · ไม่มีข้อมูล hidden ใหม่", js(page, "()=>satWeekPickList()") == ["XAUUSD", "BTCUSD", "S50"] and settings(page, "satAssetCfg") is None)
        opensheet(page)
        check(f"{tag} 6 หน้าตั้งโบรก: ไม่มี checkbox ซ่อน · แถวสินค้า BRENT ยังตั้งสัญญาได้ (WA1 ไม่มีซ่อนแล้ว)", js(page, f"()=>document.querySelectorAll('{OV} [data-as-hide]').length") == 0 and js(page, f"()=>document.querySelectorAll('{OV} [data-as-row=BRENT]').length") == 1)
        page.locator(f"{OV} [data-br-cancel]").click()
        check(f"{tag} 6 ค่าตั้งโบรกของ Brent (XM) ยังอยู่ (ไม่ลบ · SET1 ไม่แตะข้อมูลโบรกเดิม)", js(page, "()=>getBook('main').settings.brokers.XM.BRENT.contract") == 100)
        check(f"{tag} 6 Strategy ไม่มีช่อง Brent (3 ช่อง)", tiles(page) == ["XAUUSD", "BTCUSD", "S50"], json.dumps(tiles(page)))
        shot(page, f"br1-asset-hidden-strategy-{sfx}.png", "#satV3Panel")
        js(page, "()=>{ switchTab('today'); }"); page.wait_for_timeout(500)
        bias_row = js(page, "()=>{ const e=document.querySelector('[data-kind=bias]'); return e ? e.innerText : ''; }")
        check(f"{tag} 6 Today: เตือน Bias ไม่มี Brent · เช็กแผน Sat รายวันไม่มี Brent", "Brent" not in bias_row and js(page, "()=>tdRoutine().satDaily") == ["XAUUSD", "BTC", "S50"], json.dumps([bias_row, js(page, '()=>tdRoutine().satDaily')]))
        js(page, "()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tbr', date:'2026-09-20', sym:'BRENT', port:'satB', bias:'Long', entry:80, sl:78, tp:84, qty:1, mult:100, cur:'USD', status:'closed', exitPrice:82, exitDate:'2026-09-24'})); saveBook('main'); render(); }")
        js(page, "()=>{ switchTab('journal'); }"); page.wait_for_timeout(500)
        check(f"{tag} 6 ไม้ Brent ที่ปิดแล้วยังอยู่ใน Journal", "BRENT" in js(page, "()=>document.body.innerText"))
        pickw(page, ["XAUUSD", "BTCUSD", "BRENT"])
        P51.fresh(page, None)
        check(f"{tag} 6 เลือก BRENT กลับ (สลับกับ S50 — ครบ 3) → Strategy มี Brent · ค่าตั้ง Brent ยังอยู่", tiles(page) == ["XAUUSD", "BTCUSD", "BRENT"] and settings(page, "satAssetCfg") is None and js(page, "()=>getBook('main').settings.brokers.XM.BRENT.contract") == 100, json.dumps(tiles(page)))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 7 เอาออกจากสัปดาห์นี้ขณะมีไม้เปิด / แผน Activate / เอาออกหมด (WA1: ไม่บล็อกการเอาออก → ไม้ค้าง + ห้ามเปิดไม้ใหม่)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        P51.fresh(page, idea(asset="XAUUSD", broker="XM"))
        js(page, "()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tbo', date:'2026-09-30', sym:'BRENT', port:'satB', bias:'Long', entry:80, sl:78, tp:84, qty:1, mult:100, cur:'USD', status:'open', openedAt:'2026-09-30'})); saveBook('main'); render(); }")
        pickw(page, ["XAUUSD", "BTCUSD", "BRENT"])
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(300)
        js(page, "()=>waRemove('BRENT')"); page.wait_for_timeout(300)
        pk = js(page, "()=>{ const e = document.querySelector('[data-wa-park]'); if(e) e.open = true; return e ? e.innerText.replace(/\\s+/g,' ') : ''; }")
        check(f"{tag} 7 เอา BRENT ที่มีไม้เปิดออก → ทำได้ ไม้ไปแถบ 'ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้' (เหตุผลเดิม 'ซ่อนไม่ได้' ไม่มีแล้ว)", js(page, "()=>!satIsPicked('BRENT')") and "brent" in pk.lower() and "ไม้ค้าง" in pk, pk)
        js(page, "()=>waRemove('XAUUSD')"); page.wait_for_timeout(300)
        blocked = js(page, "()=>{ const i = sat7dIdea('iD'); const c = satV3PlanAcctCalc(i, 'main'); return {ready:c.ready, block:c.unpickBlock}; }")
        check(f"{tag} 7 เอา XAUUSD ที่มีแผน Activate ออก → ทำได้ · บันทึก order ใหม่ถูกบล็อก 'ไม่ได้เลือกสัปดาห์นี้ — เพิ่มกลับก่อน'", blocked["ready"] is False and blocked["block"] == "ไม่ได้เลือกสัปดาห์นี้ — เพิ่มกลับก่อน", json.dumps(blocked, ensure_ascii=False))
    finally: browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        P51.fresh(page, None)
        pickw(page, ["XAUUSD"])
        js(page, "()=>waRemove('XAUUSD')"); page.wait_for_timeout(300)
        check(f"{tag} 7 เอาออกจนเหลือ 0 → ทำได้ (WA1 ไม่บังคับเหลือ ≥ 1) · ขึ้น empty state", js(page, "()=>satAssets().length") == 0 and js(page, "()=>!!document.querySelector('[data-wa-empty]')"))
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def static_tests():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("[static] ไม่มี const SAT7D_BROKERS / SAT7D_LABEL เหลือ (เป็นฟังก์ชันอ่านค่าปัจจุบัน)", "const SAT7D_BROKERS" not in src and "const SAT7D_LABEL" not in src and "SAT7D_LABEL[" not in src and "SAT7D_BROKERS." not in src)
    check("[static] SAT7D_DEFAULT_BROKERS ยังอยู่ (ค่าเริ่มต้น XM/IC/Pi)", "const SAT7D_DEFAULT_BROKERS" in src)
    check("[static] ฟังก์ชันใหม่ครบ: brokerList · brokerName · satAssetCfg · satAssets · sat7dLabel · symDisp", all(("function " + f + "(") in src for f in ("brokerList", "brokerName", "satAssetCfg", "satAssets", "sat7dLabel", "symDisp")))


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    static_tests()
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 54 / BR1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
