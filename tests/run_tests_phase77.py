#!/usr/bin/env python3
"""PV2a — โครงพอร์ต v2 รอบ 1: ตั้งค่า Sat (Main/Tactical) · Core 70 / Satellite 30 · ฟอร์มแผนใหม่ (Setup · ทิศ · Entry · SL) · คิดขนาด + เพดาน · เทส 77
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย
ภาพ tests/screenshots/pv2a-{settings,port,form-tactical,form-main,legacy-plan}-{1440,390}.png
รัน: python3 run_tests_phase77.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase63 as P63
import run_tests_phase69 as P69

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, overflow = P54.txt, P54.overflow
NOTE = "เหตุผลทดสอบ"



def fillx(page, sel, v):
    """SET1 — ช่องที่ไม่มี UI แล้ว (ซ่อน · ตายตัวในโค้ด): ตั้งค่าผ่าน JS เพื่อยังตรวจตรรกะ validation/อ่านกลับเดิม"""
    page.evaluate("([s,v])=>{ const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); }", [sel, v])

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


def fixture(opt=0):
    """Satellite $45,000 · fx 40 · Core ฿4.2M (= 70:30) · ทุกบัญชี"""
    def m(doc):
        for a in ("main", "fam"):
            s = doc["books"][a]["settings"]
            s["fx"] = 40; s["capital"]["core"] = 4200000; s["capital"]["satB"] = 45000
            s["ddState"]["sat"] = P37.ds0(45000)
            s["satRisk"] = {"newMax": 5}
            s["satWeekPick"] = {"2026-09-27": ["XAUUSD", "BTCUSD"]}
        doc["books"]["fam"]["settings"]["capital"]["option"] = opt
    return m


def launch(pw, w, h, pb=False, opt=0, bias="Long", pin_sat=None):
    if pin_sat is None: pin_sat = (__name__ == "__main__")   # RG2b — เมื่อรันชุดนี้เอง ตรึงถัง Sat = ทุน Sat เดิม (30%) · ชุดอื่นที่ใช้ launcher นี้ไม่ตรึงเว้นแต่ขอ
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(opt), pin_sat=pin_sat)
    P51.fresh(page, None)
    if pb: P11.seed_pb(page, [P69.PB])
    js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", ["XAUUSD", "BTCUSD"])
    P11.wk(page, "XAUUSD", bias, "up" if bias == "Long" else "down")
    P37.go_sat(page)
    return browser, page, ce, pe


def idea(page, **kw):
    """สร้างแผน v2 ผ่าน satV2NewPlan แล้วรอ snapshot → คืน id"""
    sv = kw.pop("sleeve", "main"); asset = kw.pop("asset", "XAUUSD")
    bias = kw.pop("bias", None)
    iid = js(page, "([a,s])=>satV2NewPlan(a,s)", [asset, sv]); page.wait_for_timeout(500)
    # PF1 — แผนใหม่เริ่มไม่มี Trend; เทสเก่าคาดว่าทิศ = Bias ที่ seed ไว้ใน Strategy → ตั้ง Trend ของแผนให้เท่ากัน (หรือ bias= ที่ระบุ)
    if bias != "":
        js(page, "([i,a,b])=>{ const w = satwWeek(wpWeekKey(), a); const d = b || (w && (w.bias==='Long' || w.bias==='Short') ? w.bias : 'Long'); satV2SetDir(i, d); }", [iid, asset, bias]); page.wait_for_timeout(300)
    # CS1 — Tactical ต้องเป็น Clear Trend ก่อนวางแผน: เทสเก่าที่สร้างแผน Tactical ตั้ง Classify = Clear Trend ให้ (เหมือน Trend ใน PF1)
    if sv == "tactical" and "classify" not in kw:
        js(page, "([i])=>satV3IdeaWrite(i,{classify:'clear'})", [iid]); page.wait_for_timeout(250)
    for k, v in kw.items():
        js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, k, str(v)]); page.wait_for_timeout(120)
    # PF1 A4 — TP บังคับ: ถ้ากรอก Entry/SL แล้วไม่ระบุ TP ให้ TP = 2R (เท่า tp1R เดิม จึงไม่เปลี่ยนตัวเลข Tactical)
    if "tp" not in kw and "entry" in kw and "sl" in kw:
        e, sl = float(kw["entry"]), float(kw["sl"])
        js(page, "([i,v])=>satV3PlanEdit(i,'tp',v)", [iid, str(round(e + 2 * (e - sl), 6))]); page.wait_for_timeout(120)
    page.wait_for_timeout(450)
    return iid


def calc(page, iid, acct="main"):
    return js(page, """([i,a])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x, a);
        return {lot:c.lot, ready:c.ready, warns:c.warns, deal:c.v2.lotDeal, rawRisk:c.v2.rawRisk, rawCap:c.v2.rawCap, limit:c.v2.limit, riskUsd:c.v2.dealTHB/c.v2.k, tp1:c.v2.tps.tp1, tp2:c.v2.tps.tp2, factor:c.factor, split1:c.split1, msg:c.lotMsg}; }""", [iid, acct])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # 1 ตั้งค่า
    browser, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ openSettings(); document.getElementById('satV2Sec').open = true; }"); page.wait_for_timeout(400)
        vals = js(page, "()=>Object.fromEntries(SAT_V2_FIELDS.map(([id,k])=>[k, document.getElementById(id).value]))")
        exp = {"rptMain": "1.5", "rptTac": "0.75", "maxDd": "20", "capMain": "1.4", "capTac": "1.2", "brkN": "5", "brkDd": "3", "tp1R": "2", "tp1Pct": "50", "tp2R": "3",
               "tfMain": "D", "tfTac": "4H", "setupsMain": "Break EMA20\nBreak PoC Week", "setupsTac": "Break EMA50\nPoC Support", "orSat": "1.2", "orAsset": "0.6", "orTot": "6", "splitMain": "50/30/20", "splitTac": "100"}   # PV2c: + แบ่งไม้ Main/Tactical
        check(f"{tag} 1 ตั้งค่า › Sat v2: ค่าเริ่มต้นครบ 19 ช่อง (RG2b: ถอด Main%/Tactical% · RPT 1.5/0.75 · cap 1.4×/1.2× · เบรก 3%)", vals == exp, vals)
        hint = lambda i: txt(page, f'[data-v2-hint="{i}"]')
        check(f"{tag} 1 ข้างช่องแสดง % ของพอร์ตรวม (RG2b ถัง Sat 30% ตรึง): RPT 0.45% / 0.23% · Max DD = 6% · เบรก DD = 0.9%",
              (hint("sV2RptMain"), hint("sV2RptTac"), hint("sV2MaxDd"), hint("sV2BrkDd")) ==
              ("= 0.45% ของพอร์ตรวม", "= 0.23% ของพอร์ตรวม", "= 6% ของพอร์ตรวม", "= 0.9% ของพอร์ตรวม"),
              [hint(i) for i in ("sV2RptMain", "sV2RptTac", "sV2MaxDd", "sV2BrkDd")])
        shot(page, f"pv2a-settings-{sfx}.png", "#satV2Sec")
        page.select_option("#sV2RptMain", "1.25"); page.wait_for_timeout(200)   # RG2b — ไม่มีสัดส่วน Main/Tactical แล้ว: เปลี่ยน RPT Main แทน
        check(f"{tag} 1 แก้ RPT Main 1.25 → 0.375% ของพอร์ตรวม · ปุ่มบันทึกใช้ได้", hint("sV2RptMain") == "= 0.38% ของพอร์ตรวม" and not js(page, "()=>document.getElementById('setSaveBtn').disabled"), hint("sV2RptMain"))
        check(f"{tag} 1 RPT เลือกได้: Main 0.5 · 0.75 · 1 · 1.25 · 1.5 · 2 / Tactical 0.25 · 0.5 · 0.75 · 1 (RG2b)", js(page, "()=>[...document.querySelectorAll('#sV2RptMain option')].map(o=>o.value)") == ["0.5", "0.75", "1", "1.25", "1.5", "2"] and js(page, "()=>[...document.querySelectorAll('#sV2RptTac option')].map(o=>o.value)") == ["0.25", "0.5", "0.75", "1"])
        pl_old = page.input_value("#sPoolS"); page.fill("#sPoolS", "25"); page.wait_for_timeout(200)
        err = txt(page, '[data-err-for="sPoolS"]') or ""
        check(f"{tag} 1 สัดส่วนถังรวม ≠ 100 → error + บันทึกไม่ได้ (RG2b: แทนสัดส่วน Main/Tactical)", "100" in err and js(page, "()=>document.getElementById('setSaveBtn').disabled"), err)
        page.fill("#sPoolS", pl_old)
        for fid, val, why in (("sV2Tp1Pct", "100", "TP1% นอก 1–99"), ("sV2Tp1Pct", "0", "TP1% = 0"), ("sV2MaxDd", "0", "Max DD ≤ 0"), ("sV2BrkN", "2.5", "เสียติดไม่ใช่จำนวนเต็ม"), ("sV2TfMain", "", "TF ว่าง"), ("sV2CapTac", "-1", "เพดาน < 0"), ("sV2Tp2R", "1", "TP2 ไม่ไกลกว่า TP1")):
            old = page.input_value("#" + fid); (fillx if fid in ("sV2TfMain",) else (lambda p,s_,v: p.fill(s_, v)))(page, "#" + fid, val); page.wait_for_timeout(120)
            check(f"{tag} 1 ค่าผิด ({why}) → error + ปุ่มบันทึกถูกล็อก", js(page, "()=>document.getElementById('setSaveBtn').disabled") and (txt(page, f'[data-err-for="{fid}"]') or "") != "", txt(page, f'[data-err-for="{fid}"]'))
            (fillx if fid in ("sV2TfMain",) else (lambda p,s_,v: p.fill(s_, v)))(page, "#" + fid, old); page.wait_for_timeout(100)
        fillx(page, "#sV2SetupsMain", ""); page.wait_for_timeout(100)
        check(f"{tag} 1 รายการ Setup ว่าง → error", js(page, "()=>document.getElementById('setSaveBtn').disabled"))
        fillx(page, "#sV2SetupsMain", "Break EMA20\nBreak EMA20"); page.wait_for_timeout(100)
        check(f"{tag} 1 ป้าย Setup ซ้ำ → error", js(page, "()=>document.getElementById('setSaveBtn').disabled"))
        fillx(page, "#sV2SetupsMain", "Break EMA20\nแนวรับ Day"); page.select_option("#sV2RptTac", "1"); fillx(page, "#sV2Tf" + "Tac", "15m"); page.wait_for_timeout(150)
        page.click("#setSaveBtn"); page.wait_for_timeout(500)
        cfg = js(page, "()=>satV2Cfg('main')")
        check(f"{tag} 1 บันทึกแล้วอ่านกลับได้ (RPT Main 1.25 · RPT Tactical 1 · TF 15m · Setup Main แก้ชื่อ/ลบ/เพิ่ม)", (cfg["rptMain"], cfg["rptTac"], cfg["tfTac"], cfg["setupsMain"]) == (1.25, 1, "15m", ["Break EMA20", "แนวรับ Day"]), cfg)
        check(f"{tag} 1 บัญชี Family ยังเป็นค่าเริ่มต้น (ตั้งต่างบัญชีได้)", js(page, "()=>{ const c = satV2Cfg('fam'); return [c.rptMain, c.rptTac, c.tfTac]; }") == [1.5, 0.75, "4H"])
        js(page, "()=>{ acctSwitch('fam'); }"); page.wait_for_timeout(500)
        js(page, "()=>{ openSettings(); document.getElementById('satV2Sec').open = true; }"); page.wait_for_timeout(300)
        check(f"{tag} 1 เปิดตั้งค่าบัญชี Family → เห็นค่าของ Family (RPT Main 1.5 · 4H)", page.input_value("#sV2RptMain") == "1.5" and page.input_value("#sV2TfTac") == "4H")
        page.select_option("#sV2RptMain", "2"); page.wait_for_timeout(150); page.click("#setSaveBtn"); page.wait_for_timeout(500)
        check(f"{tag} 1 Family ตั้ง RPT Main 2 ได้ แยกจากบัญชีหลัก (1.25)", js(page, "()=>[satV2Cfg('fam').rptMain, satV2Cfg('main').rptMain]") == [2, 1.25])
        check(f"{tag} 1 ไม่มี console error · ไม่ล้นแนวนอน", not P63.P60.real_errs(ce) if hasattr(P63.P60, "real_errs") else not ce, ce[:3] + pe[:3])
    finally: browser.close()

    # 2 Port
    browser, page, ce, pe = launch(pw, w, h, opt=50000)
    try:
        js(page, "()=>{ switchTab('mix'); ln3PortSet('main'); renderPortfolioMix(); }"); page.wait_for_timeout(500)
        line = txt(page, "[data-pool-txt]") or ""
        check(f"{tag} 2 Port (RG2b เส้นถัง แทนแถบ Core/Main/Tactical): เป้า Winner · Ladder · Sat 30 (ตรึงเท่าทุน Sat เดิม)", line.endswith("Sat 0/30") and "Winner 0/44" in line and "Ladder 0/26" in line, line)
        js(page, "()=>{ document.querySelector('[data-pool-line]').open = true; }")
        rows = js(page, "()=>[...document.querySelectorAll('[data-pool-line] [data-pool-bar]')].map(e=>e.dataset.poolBar)")
        t = txt(page, "[data-pool-line]") or ""
        check(f"{tag} 2 ไม่มี Option ในการแบ่งเงิน (บัญชีหลักไม่มีแถว อื่น ๆ) · มีเงินแต่ละถัง", rows[:3] == ["winner", "ladder", "sat"] and len(rows) % 3 == 0 and "Option" not in t and "฿1,800,000" in t, [rows, t])
        shot(page, f"pv2a-port-{sfx}.png", "[data-pool-line]")
        js(page, "()=>acctSwitch('fam')"); page.wait_for_timeout(500); js(page, "()=>{ switchTab('mix'); ln3PortSet('fam'); renderPortfolioMix(); document.querySelector('[data-pool-line]').open = true; }"); page.wait_for_timeout(400)
        lg = js(page, "()=>{ const e = document.querySelector('[data-pool-line] [data-pv2-row=legacy]'); return e ? e.textContent : ''; }")
        check(f"{tag} 2 ข้อมูล Option เดิม (Family ฿50,000) → 'อื่น ๆ (เดิม)' อ่านอย่างเดียว ไม่นับในแถบ", "อื่น ๆ (เดิม)" in lg and "50,000" in lg and js(page, "()=>document.querySelectorAll('[data-pool-line] [data-pool-bar]').length") % 3 == 0, lg)
        check(f"{tag} 2 ไม่มี console error · ไม่ล้นแนวนอน", not ce and not pe and overflow(page) <= 1, [ce[:2], pe[:2], overflow(page)])
    finally: browser.close()

    # 3 ฟอร์ม Tactical: ทอง 4,200 · Short 4240/4260
    browser, page, ce, pe = launch(pw, w, h, bias="Short")
    try:
        iid = idea(page, sleeve="tactical", entry=4240, sl=4260)
        c = calc(page, iid)
        check(f"{tag} 3 Tactical: lot ตาม Risk 0.169 · เพดาน 1.2× → ใช้ 0.12 (จำกัดโดยเพดานมูลค่า)", abs(c["rawRisk"] - 0.16875) < 1e-6 and c["limit"] == "cap" and c["lot"] == 0.12 and c["deal"] == 0.12, c)
        check(f"{tag} 3 TP1 4,200 / TP2 4,180 (2R 50% · 3R)", c["tp1"] == 4200 and c["tp2"] == 4180, c)
        sz = txt(page, "[data-v2-size=tactical]") or ""
        check(f"{tag} 3 ตารางขนาดไม้บอก RPT $338 → 0.169 · เพดาน 0.127 · ใช้ 0.12 · 'เพดานมูลค่า'", "$338" in sz and "0.1688" in sz and "0.12" in sz and "เพดานมูลค่า" in sz and cnt(page, "[data-v2-limit=cap]") >= 1, sz)
        check(f"{tag} 3 การ์ด: ปุ่ม Main|Tactical (Tactical เปิดอยู่) · TF 4H · Setup ค่าเริ่ม Tactical · TP แสดงราคา", js(page, "()=>document.querySelector('[data-sleeve=tactical]').getAttribute('aria-pressed')") == "true"
              and page.input_value("[data-v2-tf]") == "4H" and js(page, "()=>[...document.querySelectorAll('[data-v2-setup]')].map(e=>e.dataset.v2Setup)") == ["Break EMA50", "PoC Support"] and "4,200" in (txt(page, "[data-v2-tp]") or "") and "4,180" in (txt(page, "[data-v2-tp]") or ""), txt(page, "[data-v2-tp]"))
        check(f"{tag} 3 ไม่มีช่อง Break Price / Break Vol / Pullback / ปุ่ม TF 4H·D·W ในแผนใหม่", cnt(page, ".ui-plan [data-ac-px]") == 0 and cnt(page, ".ui-plan [data-ac-pb]") == 0 and cnt(page, ".ui-plan [data-ac-tf]") == 0 and cnt(page, "[data-v2-card] .ui-acr") == 0)
        shot(page, f"pv2a-form-tactical-{sfx}.png", ".ui-pcell")
        check(f"{tag} 3 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()

    # 4 ฟอร์ม Main: Long 4180/4117
    browser, page, ce, pe = launch(pw, w, h)
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117)
        c = calc(page, iid)
        check(f"{tag} 4 Main: Entry 4,180 SL 4,117 → ดีล 0.10 lot (Risk $630) · เพดาน 2× ไม่จำกัด", c["deal"] == 0.10 and abs(c["riskUsd"] - 630) < 1e-6 and c["limit"] == "risk" and c["rawCap"] > 0.10, c)
        check(f"{tag} 4 Main: ไม้ 1 = 50% ของดีล (PY2 ใช้ต่อ) = 0.05 · ไม่มีกล่อง 'จำกัดโดยเพดาน'", c["lot"] == 0.05 and c["split1"] == 0.5 and cnt(page, "[data-v2-limit]") == 0, c)
        check(f"{tag} 4 Main: TF ค่าเริ่ม D · Setup ค่าเริ่ม Main · TP กรอกเองได้ไม่บังคับ", page.input_value("[data-v2-tf]") == "D" and js(page, "()=>[...document.querySelectorAll('[data-v2-setup]')].map(e=>e.dataset.v2Setup)") == ["Break EMA20", "Break PoC Week"] and cnt(page, "input[data-v2-tp=main]") == 1)
        sz = txt(page, "[data-v2-size=main]") or ""
        check(f"{tag} 4 ตารางขนาดไม้: RPT Main 1.5% $675 → 0.107 · ใช้ 0.1 lot · Risk $630", "$630" in sz and "0.1071" in sz and "RPT Main 1.5%" in sz, sz)
        shot(page, f"pv2a-form-main-{sfx}.png", ".ui-pcell")
        js(page, "([i])=>satV2SetSleeve(i,'tactical')", [iid]); page.wait_for_timeout(600)
        check(f"{tag} 4 สลับ Tactical → TF เปลี่ยนเป็น 4H · Setup ของ Tactical", page.input_value("[data-v2-tf]") == "4H" and js(page, "()=>[...document.querySelectorAll('[data-v2-setup]')].map(e=>e.dataset.v2Setup)")[0] == "Break EMA50")
        js(page, "([i])=>satV2Edit(i,'tf','15m')", [iid]); page.wait_for_timeout(500)
        js(page, "([i])=>satV2SetSleeve(i,'main')", [iid]); page.wait_for_timeout(600)
        check(f"{tag} 4 TF ที่พิมพ์เอง (15m) ไม่ถูกทับตอนสลับส่วน", page.input_value("[data-v2-tf]") == "15m")
        check(f"{tag} 4 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()

    # 4b ปุ่ม [+ แผน] บน tile → แผนใหม่ใช้ฟอร์ม v2 เท่านั้น (ไม่มี conditions/Break/Pullback)
    browser, page, ce, pe = launch(pw, w, h)
    try:
        page.click('.ui-tile[data-key="XAUUSD"] .ui-btn-pri:has-text("+ แผน")'); page.wait_for_timeout(700)
        d = js(page, "()=>{ const l = satIdeasList.filter(x=>x.v3 && x.asset==='XAUUSD'); return l.map(x=>({v2:x.v2, sleeve:x.sleeve, cond:Array.isArray(x.conditions), bias:x.bias, tf:x.tf})); }")
        check(f"{tag} 4b กดปุ่ม [+ แผน] → แผนฟอร์ม v2 (sleeve main · PF1: Trend ว่าง · TF D · ไม่มี conditions) · การ์ด v2 ขึ้น", d == [{"v2": True, "sleeve": "main", "cond": False, "bias": "", "tf": "D"}] and cnt(page, "[data-v2-card=main]") == 1, d)
        page.click('.ui-tile[data-key="XAUUSD"] .ui-btn-pri:has-text("+ แผน")'); page.wait_for_timeout(500)
        check(f"{tag} 4b กด [+ แผน] ซ้ำ → ไม่สร้างร่างซ้ำ", js(page, "()=>satIdeasList.filter(x=>x.v3 && x.asset==='XAUUSD').length") == 1)
    finally: browser.close()

    # 5 Tactical ที่ Asset ไม่ได้เลือก
    browser, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['BTCUSD']); }"); page.wait_for_timeout(700)
        r = js(page, "()=>satV2NewPlan('XAUUSD','tactical')")
        page.wait_for_timeout(500)
        d = js(page, "(i)=>{ const x = satIdeasList.find(y=>y.id===i); return x ? x.sleeve : null; }", r)
        check(f"{tag} 5 Asset ไม่ได้เลือกสัปดาห์นี้ → สร้าง Tactical ไม่ได้ (ได้ Main)", d == "main", d)
        # แผน Main ที่สร้างแล้ว asset ถูก auto-pick (WA1fix) → จำลอง "ไม่ได้เลือก" ที่ชั้น satIsPicked เพื่อเช็กการ์ด
        info = js(page, """([i])=>{ const x = satIdeasList.find(y=>y.id===i); const keep = window.satIsPicked; window.satIsPicked = ()=>false;
            const h = document.createElement('div'); h.innerHTML = satV2CardHtml(x); const b = h.querySelector('[data-sleeve=tactical]'); const w = h.querySelector('[data-v2-sleeve-why]');
            satV2SetSleeve(i, 'tactical'); const out = {dis: b && b.disabled, why: w ? w.innerText : '', sleeve: x.sleeve}; window.satIsPicked = keep; return out; }""", [r])
        page.wait_for_timeout(400)
        check(f"{tag} 5 ปุ่ม Tactical ปิด + เหตุผล 'เฉพาะ Asset ที่เลือกสัปดาห์นี้'", info["dis"] is True and "เฉพาะ Asset ที่เลือกสัปดาห์นี้" in info["why"], info)
        check(f"{tag} 5 บังคับสลับผ่านโค้ดก็ไม่เปลี่ยน (ยังเป็น Main)", js(page, "(i)=>satIdeasList.find(y=>y.id===i).sleeve", r) == "main")
    finally: browser.close()

    # 6 ตัวคูณ Macro กับ Tactical
    browser, page, ce, pe = launch(pw, w, h, pb=True, bias="Short")
    try:
        iid = idea(page, sleeve="tactical", entry=4240, sl=4260)
        c = calc(page, iid)
        check(f"{tag} 6 สวน Macro (Short vs Playbook ▲) → RG2b ไม่มีตัวคูณ Macro (×1): Risk $338 → 0.169 (ติดเพดาน 0.12)", c["factor"] == 1 and abs(c["rawRisk"] - 0.16875) < 1e-6 and c["lot"] == 0.12, c)
        check(f"{tag} 6 สวน Macro ต้องเขียนเหตุผลก่อน (ไม่ ready) · ไม่มีข้อความ 'ลด 40%' (RG2b)", not c["ready"] and "ลด 40%" not in (txt(page, "[data-f2c-row=size]") or ""), [c["ready"], txt(page, "[data-f2c-row=size]")])
    finally: browser.close()

    # 7 บันทึกไม้ → field ใหม่ครบ
    for sv, bias, entry, sl_ in (("tactical", "Short", 4240, 4260), ("main", "Long", 4180, 4117)):
        browser, page, ce, pe = launch(pw, w, h, bias=bias)
        try:
            iid = idea(page, sleeve=sv, entry=entry, sl=sl_)
            js(page, "([i])=>satV3MacroNoteSet(i, 'ทดสอบ')", [iid]); page.wait_for_timeout(400)
            page.locator("[data-v2-setup]").first.click(); page.wait_for_timeout(400)
            page.fill("[data-v2-note]", "Break Point 4,245"); page.locator("[data-v2-note]").press("Tab"); page.wait_for_timeout(500)
            js(page, "([i])=>satV3SaveReadyAccounts(i)", [iid]); page.wait_for_timeout(700)
            t = js(page, "()=>{ const l = getBook('main').trades.filter(t=>t.port==='satB'); return l.length ? JSON.parse(JSON.stringify(l[l.length-1])) : null; }")
            ok = t and t["sleeve"] == sv and t["setups"] and t["setup_note"] == "Break Point 4,245" and t["tf"] == ("4H" if sv == "tactical" else "D")
            if sv == "tactical": ok = ok and t["size_limit"] == "cap" and t["qty"] == 0.12 and t["tp"] == 4200 and t["tp2"] == 4180 and t["tp1_pct"] == 50 and t["status"] == "plan"
            else: ok = ok and t["size_limit"] == "risk" and t["qty"] == 0.05 and t["deal_lot"] == 0.10
            check(f"{tag} 8 ไม้ {sv} ที่บันทึก: sleeve · setups · setup_note · tf · size_limit · qty{' · TP1/TP2/tp1_pct' if sv == 'tactical' else ' (ไม้ 1 = 50%) · deal_lot'}", bool(ok), t)
            if sv == "main":
                check(f"{tag} 8 หลังบันทึก แถว plan โผล่ในรายการ · ร่างหายไป (ไม่มีการ์ดฟอร์ม)", cnt(page, "[data-v2-card]") == 0 and cnt(page, ".ui-row") >= 1)
        finally: browser.close()

    # 8 แผนเดิม (bp)
    browser, page, ce, pe = P63.sat_page(pw, w, h)
    try:
        P63.fresh(page, P63.bp_idea([P63.cond()]))
        check(f"{tag} 7 แผนเดิม (kind bp) ยังแสดงแบบเดิม: TF 4H·D·W + Break/Vol/Pullback · ไม่มีฟอร์ม v2", cnt(page, ".ui-plan [data-ac-tf] button") == 3 and cnt(page, "[data-v2-card]") == 0 and cnt(page, ".ui-plan [data-ac-px]") >= 2, cnt(page, ".ui-plan [data-ac-px]"))
        shot(page, f"pv2a-legacy-plan-{sfx}.png", ".ui-pcell")
        P63.full_ready(page)
        check(f"{tag} 7 แผนเดิม Activate ได้แบบเดิม (ติ๊กครบ → Active)", cnt(page, ".ui-plan [data-ac-on]") == 1, cnt(page, ".ui-plan [data-ac-on]"))
        check(f"{tag} 7 แผน/ไม้เดิมไม่มี sleeve = Main อัตโนมัติ", js(page, "()=>[satV2Sleeve({}), satV2Sleeve({sleeve:'tactical'}), satV2Sleeve(null)]") == ["main", "tactical", "main"])
    finally: browser.close()


def cnt(page, sel): return page.locator(sel).count()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
