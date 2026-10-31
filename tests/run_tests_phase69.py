#!/usr/bin/env python3
"""WA1 — Strategy: เลือก Asset ต่อสัปดาห์ 1–3 ตัว + ป้าย Macro + ตัวคูณขนาดไม้ตาม Macro (Neutral / สวน) ปรับได้ · เทส 69
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย
ภาพ tests/screenshots/wa1-{week-empty,week-picks,add-asset,parked,settings-factor}-{1440,390}.png
รัน: python3 run_tests_phase69.py"""
from pf2_retire import retired as retired2
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase68 as P68

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, settings, overflow = P54.txt, P54.settings, P54.overflow
cell = P68.cell
SAVED = "2026-09-27T10:00:00.000Z"
NOTE = "เหตุผลทดสอบ"

CUSTOM = [{"key": "XAG", "label": "Silver", "unit": "lot"}, {"key": "USDJPY", "label": "USDJPY", "unit": "lot"}]
PB = P68.v2doc(assets={"XAUUSD": cell("up", focus=True), "XAG": cell("up", focus=True), "BTC": cell("up_flat", posture="ETF flow ดี"),
                       "USDJPY": cell("down"), "BRENT": cell("flat")})


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


def fixture(picks_other_week=True):
    def m(doc):
        s = doc["books"]["main"]["settings"]
        s["satCustomAssets"] = [dict(c) for c in CUSTOM]
        for c in CUSTOM: s["brokers"]["XM"][c["key"]] = {"contract": 5000, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}
        s["brokers"]["XM"]["BRENT"] = {"contract": 100, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}
        if picks_other_week: s["satWeekPick"] = {"2026-01-04": ["XAUUSD"]}   # เคยใช้การเลือกรายสัปดาห์แล้ว แต่สัปดาห์นี้ยังไม่เลือก
    return m


def launch(pw, w, h, picks=None, strict=True, pb=PB):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(strict))
    P51.fresh(page, None)
    P11.seed_pb(page, [pb])
    if picks is not None: js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", picks)
    go(page)
    return browser, page, ce, pe


def go(page): js(page, "()=>{ switchTab('plan'); setPlanScope('future'); render(); }"); page.wait_for_timeout(350)
def chips(page): return js(page, "()=>[...document.querySelectorAll('[data-wa-chip]')].map(e=>e.dataset.waChip)")
def tiles(page): return js(page, "()=>[...document.querySelectorAll('.ui-tile[data-key]')].map(e=>e.dataset.key)")
def picks(page): return js(page, "()=>satWeekPickList()")
def factor(page, asset, bias, acct="main", **extra):
    return js(page, """([a,b,x,c])=>{ const i = Object.assign({asset:a, bias:b, conditions:[], accts:{}, entry:100, sl:b==='Long'?99:101, tp:b==='Long'?103:97, week:wpWeekKey()}, x);
        const c1 = satV3PlanAcctCalc(i, c); return {f:c1.factor, rf:c1.ruleFactor, note:c1.noteBlock, ready:c1.ready, lot:c1.lot, risk:c1.riskCur, cfg:c1.chosen ? c1.chosen.cfg : null}; }""", [asset, bias, extra, acct])
def set_cfg(page, acct, **kw): js(page, "([a,o])=>{ const s = getBook(a).settings; s.satRisk = Object.assign({}, s.satRisk||{}, o); saveBook(a); }", [acct, kw])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 สัปดาห์ไม่มี pick → empty state + Today
    browser, page, ce, pe = launch(pw, w, h)
    try:
        check(f"{tag} 1 สัปดาห์ใหม่ไม่มี pick → empty state 'ยังไม่ได้เลือก Asset สัปดาห์นี้' + ปุ่มไปแท็บ Flow · ไม่มีการ์ด Asset", "ยังไม่ได้เลือก Asset สัปดาห์นี้" in (txt(page, "[data-wa-empty]") or "") and js(page, "()=>!!document.querySelector('[data-wa-flow]')") and tiles(page) == [], json.dumps(tiles(page)))
        shot(page, f"wa1-week-empty-{sfx}.png", "#satV3Sum")
        page.locator("[data-wa-flow]").click(); page.wait_for_timeout(300)
        check(f"{tag} 1 ปุ่มไป Flow ทำงาน", js(page, "()=>activeTab") == "flow")
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(500)
        check(f"{tag} 1 Today มีงาน 'เลือก Asset สัปดาห์นี้' (เริ่มจาก Macro) · ไม่มีงาน Bias", "Start by adding a Strategic Asset" in (txt(page, "[data-kind=sat-daily]") or "") and js(page, "()=>document.querySelectorAll('[data-kind=bias]').length") == 0)   # PF2: งานเลือก Asset ย้ายเป็นการ์ด Sat (state A)
        page.locator("[data-pf2-add]").first.click(); page.wait_for_timeout(500)
        check(f"{tag} 1 PF2 — แตะ Add Strategic Asset → ไปแท็บแผน และเปิด sheet ＋ Asset (เดิม: งาน sat-pick ไป Flow)", js(page, "()=>activeTab") == "plan" and js(page, "()=>!!document.querySelector('[data-wa-sheet]')"))
        js(page, "()=>{ waSheetClose(); switchTab('flow'); }")
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 2 ＋ Asset
    browser, page, ce, pe = launch(pw, w, h)
    try:
        page.locator("[data-wa-add]").click(); page.wait_for_timeout(300)
        lab = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-wa-row]')].map(e=>[e.dataset.waRow, e.querySelector('.waMac').innerText.trim()]))")
        exp = {"XAUUSD": "▲ Macro ★", "BTCUSD": "▲▬ Macro", "S50": "นอก Macro", "BRENT": "▬ Macro Neutral", "XAG": "▲ Macro ★", "USDJPY": "▼ Macro"}
        check(f"{tag} 2 ＋ Asset: รายการทั้งหมดพร้อมป้าย Macro (★ / ▲ / ▲▬ / ▬ Neutral / ▼ / นอก Macro)", lab == exp, json.dumps(lab, ensure_ascii=False))
        shot(page, f"wa1-add-asset-{sfx}.png")
        page.fill("[data-wa-search]", "xa"); page.wait_for_timeout(200)
        rows = js(page, "()=>[...document.querySelectorAll('[data-wa-row]')].map(e=>e.dataset.waRow)")
        check(f"{tag} 2 ค้นหา 'xa' → XAUUSD · XAG", rows == ["XAUUSD", "XAG"], json.dumps(rows))
        page.keyboard.press("Escape"); page.wait_for_timeout(250)
        check(f"{tag} 2 Esc ปิด sheet ＋ Asset (ESC1)", js(page, "()=>!document.querySelector('.wa-sheet')"))
        page.locator("[data-wa-add]").click(); page.wait_for_timeout(250)
        page.locator("[data-wa-pick='XAUUSD']").click(); page.wait_for_timeout(350)
        check(f"{tag} 2 เลือก XAUUSD → การ์ดขึ้น · satWeekPick[สัปดาห์นี้] = [XAUUSD] · sheet ปิด", tiles(page) == ["XAUUSD"] and picks(page) == ["XAUUSD"] and js(page, "()=>!document.querySelector('.wa-sheet')") and chips(page) == ["XAUUSD"])
        for k in ("XAG", "BTCUSD"):
            page.locator("[data-wa-add]").click(); page.wait_for_timeout(250)
            check(f"{tag} 2 รายการไม่มี {('XAUUSD')} ที่เลือกแล้ว", "XAUUSD" not in js(page, "()=>[...document.querySelectorAll('[data-wa-row]')].map(e=>e.dataset.waRow)"))
            page.locator(f"[data-wa-pick='{k}']").click(); page.wait_for_timeout(350)
        check(f"{tag} 2 ครบ 3 ตัว → ไม่มีปุ่ม ＋ Asset · มีการ์ด 3 ใบ · ป้าย Macro ในแถว pick", picks(page) == ["XAUUSD", "XAG", "BTCUSD"] and js(page, "()=>!document.querySelector('[data-wa-add]')") and len(tiles(page)) == 3 and js(page, "()=>document.querySelectorAll('[data-wa-chip] .waMac').length") == 3, json.dumps([picks(page), tiles(page)]))
        shot(page, f"wa1-week-picks-{sfx}.png", "#satV3Sum")
        r = js(page, "()=>satWeekPickAdd('USDJPY')")
        check(f"{tag} 2 เพิ่มตัวที่ 4 ผ่านฟังก์ชัน → ปฏิเสธ 'ครบ 3 ตัวแล้ว'", r["ok"] is False and "ครบ 3" in r["msg"] and len(picks(page)) == 3)
        page.locator("[data-wa-more='XAG']").click(); page.wait_for_timeout(200)
        page.locator("[data-wa-remove]").click(); page.wait_for_timeout(350)
        check(f"{tag} 2 ⋯ › เอาออกจากสัปดาห์นี้ → XAG หายจากการ์ด · ＋ Asset กลับมา", picks(page) == ["XAUUSD", "BTCUSD"] and "XAG" not in tiles(page) and js(page, "()=>!!document.querySelector('[data-wa-add]')"))
        page.locator("[data-wa-more='BTCUSD']").click(); page.wait_for_timeout(200)
        page.keyboard.press("Escape"); page.wait_for_timeout(200)
        check(f"{tag} 2 Esc ปิดเมนู ⋯", js(page, "()=>!document.querySelector('[data-wa-menu]')"))
        r = js(page, "()=>{ satWeekPickWrite('2026-01-04', ['XAG']); const w = Object.keys(tdSettings().satWeekPick); return w; }")
        check(f"{tag} 2 เขียน pick ของสัปดาห์อื่นไม่กระทบสัปดาห์นี้ · เก็บไม่เกิน 12 สัปดาห์", picks(page) == ["XAUUSD", "BTCUSD"] and js(page, """()=>{ for(let i=0;i<20;i++){ satWeekPickWrite('2025-'+String(10+i).padStart(2,'0')+'-01', ['XAUUSD']); } return Object.keys(tdSettings().satWeekPick).length; }""") <= 12)
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 2b ยังไม่เคยเลือก (ไม่มี satWeekPick) = empty state เสมอ (WA1fix: เลิกโหมด legacy)
    browser, page, ce, pe = launch(pw, w, h, strict=False)
    try:
        check(f"{tag} 2b ผู้ใช้ที่ยังไม่เคยเลือกรายสัปดาห์ (ไม่มี satWeekPick) → empty state · ไม่มีการ์ด · ไม่มี hint legacy (WA1fix)", len(tiles(page)) == 0 and js(page, "()=>!document.querySelector('[data-wa-legacy]')") and js(page, "()=>!!document.querySelector('[data-wa-empty]')"), json.dumps(tiles(page)))
        page.locator("[data-wa-add]").click(); page.wait_for_timeout(250)
        page.locator("[data-wa-pick='XAG']").click(); page.wait_for_timeout(350)
        check(f"{tag} 2b เลือก XAG ครั้งแรก → แสดงเฉพาะ XAG", tiles(page) == ["XAG"] and picks(page) == ["XAG"])
    finally: browser.close()

    # ── 3 เอาออกขณะมีไม้เปิด
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "BTCUSD"])
    try:
        p36.mk_first(page, "t1", entry=2400, sl=2390, qty=0.40)
        P51.put_idea(page, P54.idea(asset="XAUUSD", iid="iNew", act=False)); go(page); P37.open_plan(page)
        js(page, "()=>waRemove('XAUUSD')"); page.wait_for_timeout(350)
        js(page, "()=>{ document.querySelector('[data-wa-park]').open = true; waParkOpen = true; }")
        pk = txt(page, "[data-wa-park]") or ""
        check(f"{tag} 3 เอา XAUUSD ออกขณะมีไม้เปิด → แถบ 'ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้ (1)' มี XAUUSD · แผน/ไม้", "ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้ (1)" in pk and "XAUUSD" in pk and js(page, "()=>!!document.querySelector('[data-park=XAUUSD]')"), pk)
        shot(page, f"wa1-parked-{sfx}.png", "#satV3Panel")
        n0 = js(page, "()=>getBook('main').trades.length")
        r = js(page, """()=>{ const i = sat7dIdea('iNew'); const c = satV3PlanAcctCalc(i, 'main'); satV3SaveSlot('iNew','main'); satV3SaveOffplanAccount('iNew','main');
            return {block:c.unpickBlock, ready:c.ready, n:getBook('main').trades.length}; }""")
        check(f"{tag} 3 บันทึก order ใหม่ของตัวที่ไม่ได้เลือก → บล็อก 'ไม่ได้เลือกสัปดาห์นี้ — เพิ่มกลับก่อน'", r["block"] == "ไม่ได้เลือกสัปดาห์นี้ — เพิ่มกลับก่อน" and not r["ready"] and r["n"] == n0, json.dumps(r, ensure_ascii=False))
        check(f"{tag} 3 การ์ดแผนแสดงเหตุผลบล็อก", "ไม่ได้เลือกสัปดาห์นี้ — เพิ่มกลับก่อน" in (txt(page, "#satV3Panel") or ""))
        a = js(page, "()=>{ satV3CondActivate('iNew','c1',true); const i = sat7dIdea('iNew'); return !!(i.conditions||[]).find(c=>c.id==='c1' && c.active); }")
        check(f"{tag} 3 Activate เงื่อนไขใหม่ถูกบล็อก", a is False)
        js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='t1'); t.sl=2400; saveBook('main'); render(); }"); page.wait_for_timeout(250)
        check(f"{tag} 3 เลื่อน SL / จัดการไม้เดิมได้ · แถบยังอยู่", js(page, "()=>getBook('main').trades.find(x=>x.id==='t1').sl") == 2400 and js(page, "()=>!!document.querySelector('[data-wa-park]')"))
        page.locator("[data-park-add='XAUUSD']").click(); page.wait_for_timeout(350)
        check(f"{tag} 3 เพิ่มกลับ → แถบหาย · block หาย · Activate ได้", "XAUUSD" in picks(page) and js(page, "()=>!document.querySelector('[data-wa-park]')") and js(page, "()=>{ satV3CondActivate('iNew','c1',true); return !!(sat7dIdea('iNew').conditions||[]).find(c=>c.id==='c1' && c.active); }") is True)
        js(page, "()=>waRemove('XAUUSD')"); page.wait_for_timeout(300)
        js(page, "()=>{ const t=getBook('main').trades.find(x=>x.id==='t1'); t.status='closed'; t.exitPrice=2405; t.exitDate=thaiToday(); saveBook('main'); satV3IdeaDelete('iNew'); satV3IdeaDelete('i_t1'); render(); }"); page.wait_for_timeout(500)
        check(f"{tag} 3 ไม้ปิดหมด + แผนจบ → แถบไม้ค้างหายเอง", js(page, "()=>!document.querySelector('[data-wa-park]')"))
        check(f"{tag} 3 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 4 ตัวคูณขนาดไม้
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "BRENT", "S50"])
    try:
        for a in ("XAUUSD", "BRENT", "S50"): P11.wk(page, a, "Long", "up")
        L = factor(page, "XAUUSD", "Long"); S = factor(page, "XAUUSD", "Short", macro_note=NOTE)
        check(f"{tag} 4 Playbook XAU ▲ · แผน Long (ตาม) → ×1 · แผน Short (สวน) → ×1 (RG2b)", L["f"] == 1 and S["f"] == 1, json.dumps([L["f"], S["f"]]))   # RG2b — ไม่มีตัวคูณ Macro: สวน = ×1
        bn = factor(page, "BRENT", "Long")
        check(f"{tag} 4 Playbook ▬ (Neutral) → ×1.0 (ค่าเริ่ม) · ไม่ต้องกรอกเหตุผล", bn["f"] == 1 and bn["note"] == "")
        set_cfg(page, "main", macroNeutral=0.8)
        bn = factor(page, "BRENT", "Long"); out = factor(page, "S50", "Long", macro_note=NOTE)
        check(f"{tag} 4 ตั้ง Neutral 0.8 → BRENT ×0.8 · Asset นอก Macro (S50) ×0.8 (เท่า Neutral)", bn["f"] == 1 and out["f"] == 1, json.dumps([bn["f"], out["f"]]))   # RG2b — ค่า Neutral ที่ตั้งไม่มีผล
        set_cfg(page, "main", macroAgainst=0.5)
        S = factor(page, "XAUUSD", "Short", macro_note=NOTE)
        check(f"{tag} 4 ตั้ง สวน Macro 0.5 → ไม่มีผล ×1 (RG2b)", S["f"] == 1)
        full = factor(page, "XAUUSD", "Short", macro_note=NOTE, size_full_override=True)
        check(f"{tag} 4 ปุ่ม 'ใช้ไม้เต็ม (ไม่ตามกฎ)' ยังใช้ได้กับสวน Macro → ×1", full["f"] == 1 and full["rf"] == 1)   # RG2b
        exp = js(page, "([c,r,f])=>Calc.satLot({riskAmount:r*f, dist:1, contract:c.contract, lotStep:c.lotStep, minLot:c.minLot}).lot", [S["cfg"], S["risk"], 1 * 0.5])   # ตัวคูณ Macro 0.5 × ไม้ 1 = 50% ของงบ (PY2)
        check(f"{tag} 4 lot = Calc.satLot(riskAmount × ตัวคูณ) ({S['lot']} vs {exp})", S["lot"] == exp, json.dumps([S["lot"], exp]))
        # ร่วมกับ DD ×0.5 (ลดขนาด)
        ddf = js(page, "()=>{ const b = sat7dAcctBase('main'); return b.ddFactor; }")
        check(f"{tag} 4 DD ลดขนาดยังคูณใน riskTHB เดิม (ddFactor = {ddf}) · ตัวคูณ Macro แยกชั้น", ddf in (1, 0.5))
        # แยกบัญชี
        set_cfg(page, "fam", macroAgainst=0.7)
        fa = js(page, "()=>[satRiskCfg('main').macroAgainst, satRiskCfg('fam').macroAgainst, satRiskCfg('fam').macroNeutral]")
        check(f"{tag} 4 ตั้งต่อบัญชี: main สวน 0.5 · fam สวน 0.7 (Neutral fam ค่าเริ่ม 1)", fa == [1, 1, 1], json.dumps(fa))   # RG2b — ค่าที่ตั้งถูกเก็บไว้แต่ไม่อ่าน
        set_cfg(page, "main", macroAgainst=2)
        check(f"{tag} 4 ค่าผิดรูปใน settings (2) → ไม่อ่าน = 1 (RG2b)", js(page, "()=>satRiskCfg('main').macroAgainst") == 1)
        check(f"{tag} 4 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 5 Trend ไม่มีผล
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD"])
    try:
        P11.wk(page, "XAUUSD", "Long", "down")
        a = factor(page, "XAUUSD", "Long")
        P11.wk(page, "XAUUSD", "Short", "down")
        b = factor(page, "XAUUSD", "Short", macro_note=NOTE)
        check(f"{tag} 5 Macro ตาม + Trend สวน (Long, Trend ▼) → ×1", a["f"] == 1, json.dumps(a["f"]))
        check(f"{tag} 5 Macro สวน + Trend ตาม (Short, Trend ▼) → ×1 (RG2b ถอดตัวคูณ Macro)", b["f"] == 1, json.dumps(b["f"]))   # RG2b
    finally: browser.close()

    # ── 6 เหตุผลที่เข้าสวน/นอก Macro
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "S50"])
    try:
        P11.wk(page, "XAUUSD", "Short", "down")
        idea = P51.idea_doc(asset="XAUUSD", bias="Short", entry=2410, sl=2420, tp=2395, zone=(2395, 2380), iid="iAg"); idea["macro_note"] = ""
        P51.fresh(page, idea); P11.seed_pb(page, [PB]); P11.wk(page, "XAUUSD", "Short", "down"); js(page, "()=>satV3Render()"); page.wait_for_timeout(300)
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iAg'), 'main'); return {ready:c.ready, note:c.noteBlock, f:c.factor}; }")
        check(f"{tag} 6 สวน Macro ไม่กรอกเหตุผล → ไม่ ready · 'เขียนเหตุผลที่เข้าสวน/นอก Macro' · ปุ่มบันทึก order ปิด", c["ready"] is False and c["note"] == "เขียนเหตุผลที่เข้าสวน/นอก Macro" and js(page, "()=>!!document.querySelector('[data-macro-note]')") and "เขียนเหตุผลที่เข้าสวน/นอก Macro" in (txt(page, "#satV3Panel") or ""), json.dumps(c, ensure_ascii=False))
        btn = js(page, "()=>{ const b = [...document.querySelectorAll('#satV3Panel .ui-btn')].find(e=>/บันทึก order ทุกบัญชีที่พร้อม/.test(e.innerText)); return b ? b.disabled : null; }")
        n0 = js(page, "()=>getBook('main').trades.length")
        js(page, "()=>{ satV3SaveSlot('iAg','main'); satV3SaveOffplanAccount('iAg','main'); }"); page.wait_for_timeout(300)
        check(f"{tag} 6 ปุ่มปิด (disabled) · บันทึกตรง/รวมด้วย (นอกแผน) ก็ไม่ได้", btn is True and js(page, "()=>getBook('main').trades.length") == n0, str(btn))
        inp = page.locator("[data-macro-note]").first
        inp.fill("x" * 100); inp.dispatch_event("change"); page.wait_for_timeout(350)
        ln = len(js(page, "()=>sat7dIdea('iAg').macro_note") or "")
        check(f"{tag} 6 กรอกเหตุผล (ตัดที่ 80 ตัว) → บันทึกใน idea.macro_note", ln == 80, str(ln))
        inp = page.locator("[data-macro-note]").first
        inp.fill("เข้าสวนเพราะแนวรับแข็ง"); inp.dispatch_event("change"); page.wait_for_timeout(350)
        c = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iAg'), 'main'); return {ready:c.ready, note:c.noteBlock, warns:c.warns, lot:c.lot}; }")
        check(f"{tag} 6 กรอกเหตุผลแล้ว → ready · ไม่มีคำเตือน", c["ready"] is True and c["note"] == "", json.dumps(c, ensure_ascii=False))
        js(page, "()=>satV3SaveSlot('iAg','main')"); page.wait_for_timeout(350)
        t = js(page, "()=>{ const s = (sat7dIdea('iAg').accts||{}).main||{}; const t = getBook('main').trades.find(x=>x.id===s.trade_id); return t ? {note:t.macro_note, rule:t.size_rule, sf:t.sizeFactor, st:t.macro_state} : null; }")
        check(f"{tag} 6 บันทึก order → ไม้เก็บ macro_note + macro_state against + size_rule 1 + sizeFactor null", t and t["note"] == "เข้าสวนเพราะแนวรับแข็ง" and t["rule"] == 1 and t["sf"] is None and t["st"] == "against", json.dumps(t, ensure_ascii=False))
        # นอก Macro (S50)
        P51.fresh(page, None); P11.seed_pb(page, [PB])
        i2 = P51.idea_doc(asset="S50", bias="Long", entry=900, sl=890, tp=930, zone=(930, 940), iid="iOut"); i2["macro_note"] = ""
        i2["accts"] = {"main": {"broker": "Pi"}}
        P51.put_idea(page, i2)
        c2 = js(page, "()=>{ const c = satV3PlanAcctCalc(sat7dIdea('iOut'), 'main'); return {note:c.noteBlock, f:c.factor}; }")
        check(f"{tag} 6 นอก Macro (S50) ก็ต้องกรอกเหตุผลเหมือนกัน", c2["note"] == "เขียนเหตุผลที่เข้าสวน/นอก Macro", json.dumps(c2, ensure_ascii=False))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 7 ตั้งค่า
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD"])
    try:
        js(page, "()=>{ openSettings(); }"); page.wait_for_timeout(300)
        js(page, "()=>{ document.querySelectorAll('#satRiskSec').forEach(d=>d.open=true); }")
        shot(page, f"wa1-settings-factor-{sfx}.png", "#satRiskSec")
        err = lambda i: txt(page, f'[data-err-for="{i}"]') or ""
        dis = lambda: js(page, "()=>document.getElementById('setSaveBtn').disabled")
        bad = {}
        for fld in ("sSatMacroNeutral", "sSatMacroAgainst"):
            for v in ("0", "1.5", "", "0.05", "0.555"):
                page.fill("#" + fld, v); page.wait_for_timeout(60)
                bad[f"{fld}={v!r}"] = (err(fld) != "" and dis() is True)
            page.fill("#" + fld, "0.8"); page.wait_for_timeout(60)
        check(f"{tag} 7 ค่า 0 / 1.5 / ว่าง / 0.05 / 0.555 → error + ปุ่มบันทึกปิด ทั้ง 2 ช่อง", all(bad.values()), json.dumps(bad))
        check(f"{tag} 7 ค่าถูก (0.8) → ข้อความหาย · ปุ่มบันทึกเปิด", err("sSatMacroNeutral") == "" and err("sSatMacroAgainst") == "" and dis() is False)
        page.fill("#sSatMacroNeutral", "0.9"); page.fill("#sSatMacroAgainst", "0.4"); page.wait_for_timeout(60)
        js(page, "()=>saveSettings()"); page.wait_for_timeout(300)
        sv = js(page, "()=>[getBook('main').settings.satRisk, getBook('fam').settings.satRisk || null]")
        check(f"{tag} 7 บันทึก → main macroNeutral 0.9 · macroAgainst 0.4 · fam ไม่เปลี่ยน", sv[0]["macroNeutral"] == 0.9 and sv[0]["macroAgainst"] == 0.4 and "macroNeutral" not in (sv[1] or {}) and "macroAgainst" not in (sv[1] or {}), json.dumps(sv))
        set_cfg(page, "fam", macroNeutral=0.5)
        check(f"{tag} 7 บัญชี Family ตั้งต่างจาก main ได้", js(page, "()=>[satRiskCfg('main').macroNeutral, satRiskCfg('fam').macroNeutral]") == [0.9, 0.5])
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); }")
        P54.opensheet(page)
        check(f"{tag} 7 ตั้งค่าสินค้า Sat: ไม่มี checkbox ซ่อน · ลบสินค้าเพิ่มเอง (XAG ที่ไม่ได้ใช้) ได้ + เอาออกจาก pick", js(page, "()=>document.querySelectorAll('#sat7dBrokerOverlay [data-as-hide]').length") == 0 and js(page, "()=>document.querySelectorAll('#sat7dBrokerOverlay [data-as-del]').length") == 2)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD','XAG']); }")
        P54.opensheet(page)
        page.locator("#sat7dBrokerOverlay [data-as-del='XAG']").click(); page.wait_for_timeout(250)
        P54.save(page)
        check(f"{tag} 7 ลบ XAG ที่อยู่ใน pick → เอาออกจาก pick ด้วย", picks(page) == ["XAUUSD"], json.dumps(picks(page)))
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 8 Today Bias นับตาม pick
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "BRENT"])
    try:
        js(page, "()=>{ satWeekMap = {}; switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(500)
        t0 = txt(page, "[data-kind=bias]") or ""
        check(f"{tag} 8 PF3 Today: ไม่มีแถว Bias (งานถอด) · แถวเช็กแผน Sat นับตาม pick = XAU · Brent (ไม่มี BTC / S50)", t0 == "" and js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=\"sat-daily\"] .tdAs .nm')].map(e=>e.textContent)") == ["XAU", "Brent"], t0)
        for a in ("XAUUSD", "BRENT"): P11.wk(page, a, "Long", "up")
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(500)
        check(f"{tag} 8 ประเมินครบ 2/2 → ไม่มีงาน Bias", js(page, "()=>document.querySelectorAll('[data-kind=bias]').length") == 0)
        check(f"{tag} 8 เช็กแผน Sat รายวันนับเฉพาะที่เลือก", sorted(js(page, "()=>tdRoutine().satDaily")) == ["BRENT", "XAUUSD"], json.dumps(js(page, "()=>tdRoutine().satDaily")))
    finally: browser.close()

    # ── 9 มือถือ
    browser, page, ce, pe = launch(pw, w, h, picks=["XAUUSD", "XAG", "BTCUSD"])
    try:
        ok = js(page, """()=>{ const b = document.querySelector('[data-wa-bar]').getBoundingClientRect(); return {w:b.width, vw:window.innerWidth, over:[...document.querySelectorAll('[data-wa-chip]')].some(e=>e.getBoundingClientRect().right > window.innerWidth + 0.5)}; }""")
        check(f"{tag} 9 แถว pick 3 ตัวไม่ล้นจอ ({label})", ok["w"] <= ok["vw"] + 0.5 and not ok["over"] and overflow(page) <= 0, json.dumps([ok, overflow(page)]))
        js(page, "()=>waRemove('BTCUSD')"); page.wait_for_timeout(250)
        page.locator("[data-wa-add]").click(); page.wait_for_timeout(250)
        check(f"{tag} 9 sheet ＋ Asset ไม่ล้น", js(page, "()=>{ const s = document.querySelector('.wa-sheet .ui-sheet'); return s.scrollWidth <= s.clientWidth + 1; }"))
        page.keyboard.press("Escape"); page.wait_for_timeout(250)
        check(f"{tag} 9 Esc ปิด sheet (ESC1)", js(page, "()=>!document.querySelector('.wa-sheet')"))
        check(f"{tag} 9 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 69 / WA1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
