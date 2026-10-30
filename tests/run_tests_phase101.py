#!/usr/bin/env python3
"""WM1b — mapping สัปดาห์ · ตัวตน Asset (ID · ชื่อที่แสดง · ตลาดอ้างอิง) · alias · ปิดใช้งาน · import mapping · เทส 101
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1440 · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/wm1b-{assets-390,assets-1440,import-preview-390}.png
รัน: python3 run_tests_phase101.py"""
import copy, json, os
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase37 as P37
import run_tests_phase39 as P39
import run_tests_phase99 as P99
import run_tests_phase100 as P100

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
WEEK = "2026-09-28"
OV = "#sat7dBrokerOverlay"
DIALOGS = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


def launch(pw, w, h, picks=None, mut=None):
    def m(doc):
        P100.fixture(doc)
        if mut: mut(doc)
    b, page, ce, pe = P99.launch(pw, w, h, pb=True, picks=picks, mut=m)
    page.on("dialog", lambda d: DIALOGS.append(d.message))
    return b, page, ce, pe


def open_settings(page):
    js(page, "()=>sat7dBrokerOpen()"); settle(page, 500)


def save_settings(page):
    page.locator(f"{OV} [data-br-save]").click(); settle(page, 700)


def row(page, k, sel=""): return f'{OV} [data-as-row="{k}"] {sel}'.strip()


def warn_of(page, k): return js(page, "(k)=>{ const e = document.querySelector('#sat7dBrokerOverlay [data-as-warn=\"'+k+'\"]'); return e ? e.textContent : null; }", k)


def sdiff(a, b): return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


def ctx_settings(page):
    """settings ของบัญชีหลัก ยกเว้นก้อน satAssetCfg/satPbLink ที่ WM1b แก้ได้ (ไว้เทียบว่า Risk/Sizing/Broker ไม่ขยับ)"""
    return js(page, "()=>{ const s = JSON.parse(JSON.stringify(tdSettings())); delete s.satAssetCfg; delete s.satPbLink; delete s.ddState; delete s.satWeekPick; return s; }")


# ───────────────────────── 1 mapping สัปดาห์ + เขตเวลา ─────────────────────────
def mapping_tests(pw):
    exp = {"a": "2026-12-28", "b": "2026-11-30", "c": "2027-02-01", "d": "2027-01-31", "e": "2026-12-27", "ict": "2026-12-27", "hm": "20:00", "mon": "2026-09-28"}
    for tz in ("Asia/Bangkok", "UTC", "America/New_York"):
        P39.TZID = tz
        tag = f"[{ENGINE}/tz={tz}]"
        b, page, ce, pe = launch(pw, 390, 844)
        try:
            r = js(page, """()=>({tz: Intl.DateTimeFormat().resolvedOptions().timeZone, a: Calc.wiMondayOfStrategy('2026-12-27'), b: Calc.wiMondayOfStrategy('2026-11-29'), c: Calc.wiMondayOfStrategy('2027-01-31'),
              d: Calc.wiStrategyOfMonday('2027-02-01'), e: Calc.wiStrategyOfMonday('2026-12-28'), ict: Calc.wiIctDate(Date.parse('2026-12-27T20:00:00+07:00')), hm: Calc.wiIctHM(Date.parse('2026-12-27T20:00:00+07:00')),
              mon: Calc.wiMondayOfStrategy('2026-09-27'), dow: Calc.wiDow('2026-09-28')})""")
            ok = r["tz"] == tz and all(r[k] == v for k, v in exp.items()) and r["dow"] == 1
            check(f"{tag} 1 mapping Strategy อาทิตย์ → Weekly Impact จันทร์ ข้ามเดือน/ปี (27 ธ.ค.→28 ธ.ค. · 29 พ.ย.→30 พ.ย. · 31 ม.ค. 2027→1 ก.พ.) · ย้อนกลับ · ICT 20:00 · เครื่องตั้ง {tz} ได้ผลเดียวกัน", ok, r)
        finally: b.close()
    P39.TZID = "Asia/Bangkok"


# ───────────────────────── 2 Today: event วันอาทิตย์จากสแนปช็อตก่อนหน้า ─────────────────────────
def sunday_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844, picks=["XAUUSD"])
    try:
        prev = P100.sample(week="2026-09-21")
        prev["events"] = {"e_sun": {"title": "SAMPLE Sunday event", "kind": "decision", "scheduled_at": "2026-09-27T20:30:00+07:00", "time_status": "confirmed", "status": "scheduled"}}
        prev["assets"] = {"XAUUSD": {"impact": "HIGH", "note": "SAMPLE", "event_refs": ["e_sun"]}}   # TD3a: Today แสดงเฉพาะ HIGH
        cur = P100.sample(week=WEEK)
        cur["events"]["e_sun"] = copy.deepcopy(prev["events"]["e_sun"])   # event id เดียวกันอยู่ในสองสแนปช็อต
        cur["assets"]["XAUUSD"]["event_refs"].append("e_sun")
        P100.seed(page, prev); P100.seed(page, cur)
        P37.set_clock(page, "2026-09-27T13:00:00Z")   # อาทิตย์ 20:00 ICT (Strategy สัปดาห์ใหม่ 27 ก.ย.)
        js(page, "()=>{ wiResume(); }"); settle(page, 500)
        P100.go_today(page)
        s = P100.td_state(page)
        sun = [r for r in s["rows"] if r["id"] == "e_sun"]
        check(f"{tag} 2 อาทิตย์ 20:00 ICT: event 20:30 ของวันอาทิตย์ (อยู่สแนปช็อตสัปดาห์ก่อน + ซ้ำในสแนปช็อตปัจจุบัน) แสดงครั้งเดียว · ใกล้ประกาศ", len(sun) == 1 and sun[0]["st"] == "soon" and "20:30" in sun[0]["txt"], s["rows"])
        # สแนปช็อตก่อนหน้าอย่างเดียว (ไม่มีในปัจจุบัน)
        cur2 = P100.sample(week=WEEK); P100.seed(page, cur2)
        js(page, "()=>{ wiResume(); }"); settle(page, 500)
        P100.go_today(page)
        sun = [r for r in P100.td_state(page)["rows"] if r["id"] == "e_sun"]
        check(f"{tag} 2 event วันอาทิตย์ที่อยู่เฉพาะสแนปช็อตก่อนหน้า ยังเห็นใน Today (เลือกตามเวลาเหตุการณ์จริง ไม่ใช่ตามสัปดาห์)", len(sun) == 1, sun)
        check(f"{tag} 2 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 Asset settings + import mapping ─────────────────────────
def asset_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, picks=["XAUUSD"])
    try:
        before = ctx_settings(page)
        open_settings(page)
        ui = js(page, """()=>{ const r = k => document.querySelector('#sat7dBrokerOverlay [data-as-row="'+k+'"]'); const x = r('BTCUSD'); return {rows: [...document.querySelectorAll('#sat7dBrokerOverlay [data-as-row]')].map(e=>e.dataset.asRow),
          chip: !!x.querySelector('[data-as-setref]') && x.querySelector('[data-as-setref]').offsetParent !== null, act: x.querySelector('[data-as-active]').checked, ref: x.querySelector('[data-as-ref]').value,
          hint: x.querySelector('[data-as-ref] option').textContent, alias: x.querySelector('[data-as-alias]').value, builtin: x.querySelector('[data-as-alias]').parentElement.innerText, pb: !!x.querySelector('[data-as-pb]'),
          ow: document.documentElement.scrollWidth - innerWidth, ovow: (()=>{ const m = document.querySelector('#sat7dBrokerOverlay .modal'); return m.scrollWidth - m.clientWidth; })()}; }""")
        check(f"{tag} 3 ตั้งค่าสินค้า Sat: แถวรวมทุกตัว (built-in + custom) · ใช้งาน เปิดอยู่ · ตลาดอ้างอิง 'ยังไม่ตั้ง' + chip 'ตั้งตลาดอ้างอิง' + คำแนะนำสีจาง (Bitcoin) ไม่ตั้งให้เอง · alias ในตัว BTC · มีช่อง Playbook · ไม่ล้นแนวนอน",
              ui["rows"][:4] == ["XAUUSD", "BTCUSD", "S50", "BRENT"] and "XAG" in ui["rows"] and ui["chip"] and ui["act"] and ui["ref"] == "" and "Bitcoin" in ui["hint"] and "BTC" in ui["builtin"] and ui["pb"] and ui["ow"] <= 0, ui)
        if shots and label == "390px": C.shot(page, "wm1b-assets-390.png", OV + " .modal")
        if label == "1440px": C.shot(page, "wm1b-assets-1440.png", OV + " .modal")
        # alias ไม่ถูกต้อง
        for bad, why in (("xauusd", "ซ้ำรหัสสินค้า (XAUUSD)"), ("XAG", "ซ้ำรหัสสินค้า"), ("B", "ความยาว"), ("US", "US ต้องตั้งตลาดก่อน"), ("A1,B2,C3,D4,E5,F6", "เกิน 5")):
            page.locator(row(page, "S50", "[data-as-alias]")).fill(bad); save_settings(page)
            wv = warn_of(page, "S50")
            still = js(page, "()=>document.getElementById('sat7dBrokerOverlay').classList.contains('show')")
            check(f"{tag} 3 alias ไม่ถูกต้อง [{bad}] ({why}) → เตือนใต้แถว · ไม่บันทึก · overlay ยังเปิด", bool(wv) and still and not js(page, "()=>(satAssetCfg().S50||{}).aliases"), [wv, still])
        # alias ซ้ำระหว่างสินค้า (กับ alias ในตัวของ BTCUSD = BTC)
        page.locator(row(page, "S50", "[data-as-alias]")).fill("BTC"); save_settings(page)
        wv = warn_of(page, "S50")
        check(f"{tag} 3 alias ซ้ำกับ alias ของสินค้าอื่น (BTC ของ BTCUSD) → ปฏิเสธ", bool(wv) and "ซ้ำ" in wv, wv)
        page.locator(row(page, "S50", "[data-as-alias]")).fill("")
        # ตั้งตลาดอ้างอิง + alias US ที่ XAG... (custom แทน index) : ใช้ USDJPY เป็น "ดัชนี" ตัวอย่าง = SAMPLE
        page.locator(row(page, "USDJPY", "[data-as-alias]")).fill("US"); save_settings(page)
        wv = warn_of(page, "USDJPY")
        check(f"{tag} 3 alias 'US' ถูกปฏิเสธเมื่อยังไม่ตั้งตลาดอ้างอิง (ไม่เลือก S&P/Nasdaq ให้เอง)", bool(wv) and "ตลาดอ้างอิง" in wv and not js(page, "()=>(satAssetCfg().USDJPY||{}).aliases"), wv)
        n_assets = js(page, "()=>satAssets({all:true}).length")
        page.locator(row(page, "USDJPY", "[data-as-ref]")).select_option("Nasdaq-100"); settle(page, 200)
        chip_hidden = js(page, "()=>document.querySelector('#sat7dBrokerOverlay [data-as-row=\"USDJPY\"] [data-as-setref]').offsetParent === null")
        save_settings(page)
        cfg = js(page, "()=>satAssetCfg().USDJPY")
        check(f"{tag} 3 ตั้ง ตลาดอ้างอิง = Nasdaq-100 แล้ว alias US ได้ · chip หายเมื่อตั้งแล้ว · ID ไม่เปลี่ยน · จำนวนสินค้าเท่าเดิม", cfg == {"ref_market": "Nasdaq-100", "aliases": ["US"]} and chip_hidden and js(page, "()=>satAssets({all:true}).length") == n_assets and not warn_of(page, "USDJPY"), [cfg, chip_hidden])
        check(f"{tag} 3 Risk / ขนาดไม้ / โบรก / ตั้งค่าอื่นไม่ขยับ (settings ทั้งก้อนยกเว้น satAssetCfg/satPbLink เหมือนเดิมทุกตัวอักษร)", ctx_settings(page) == before, sdiff(ctx_settings(page), before))
        # ───── import mapping
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 600)
        def imp(d, key_extra=None):
            P100.paste(page, d)
            return js(page, "()=>({m: [...document.querySelectorAll('[data-wi-matched]')].map(e=>e.innerText.trim()), s: [...document.querySelectorAll('[data-wi-skipped]')].map(e=>e.innerText.trim()), err: (document.querySelector('[data-wi-errs]')||{}).innerText || null})")
        d = P100.sample(); d["assets"] = {
            "XAUUSD": {"impact": "HIGH", "note": "SAMPLE", "event_refs": ["e_pce"]},
            "BTC": {"impact": "MED", "note": "SAMPLE ไม่มี ref", "event_refs": []},
            "XAG": {"impact": "LOW", "note": "x", "event_refs": []},
            "US": {"impact": "HIGH", "note": "SAMPLE US ไม่ระบุตลาด", "event_refs": ["e_pce"]},
            "ZZZ": {"impact": "HIGH", "note": "ไม่มี Asset นี้", "event_refs": []}}
        r = imp(d)
        check(f"{tag} 3 import preview: BTC → BTCUSD (alias ที่ประกาศ · ไม่สร้างซ้ำ) · XAG ตรง (เพิ่มไว้แล้ว) · US ตรงกับ alias ของ USDJPY ที่ตั้ง Nasdaq-100 (ตั้งตลาดแล้ว = map ได้ ไม่ใช่ S&P) · ZZZ ไม่รู้จัก → ข้าม · ข้ามตัวหนึ่งไม่ทำให้ตัวอื่นหาย",
              any("BTC → BTCUSD" in m for m in r["m"]) and any("XAG" in m for m in r["m"]) and any("US → USDJPY" in m for m in r["m"]) and any(x.startswith("⊘ ZZZ") for x in r["s"]) and len(r["m"]) == 4 and not r["err"], r)
        if shots and label == "390px":
            js(page, "()=>{ const h = document.querySelector('.wi-sheet .ui-sheet'); h.scrollTop = 99999; }"); settle(page, 200)
            C.shot(page, "wm1b-import-preview-390.png", ".wi-sheet .ui-sheet")
        # ข้อมูลเฉพาะตลาด: ตลาดไม่ตรง / ยังไม่ตั้ง
        d2 = P100.sample(); d2["assets"] = {"XAUUSD": {"impact": "HIGH", "note": "x", "event_refs": [], "ref_market": "Gold spot"},
                                          "BTC": {"impact": "HIGH", "note": "x", "event_refs": [], "ref_market": "Bitcoin"},
                                          "US": {"impact": "HIGH", "note": "x", "event_refs": [], "ref_market": "S&P 500"},
                                          "USDJPY": {"impact": "MED", "note": "x", "event_refs": [], "ref_market": "Nasdaq-100"}}
        r = imp(d2)
        sk = " | ".join(r["s"])
        check(f"{tag} 3 งานวิจัยเฉพาะตลาด: ตลาดอ้างอิงของ Asset ยังไม่ตั้ง (XAUUSD/BTC) → ข้าม 'ตั้งตลาดอ้างอิงก่อน' · 'US' ที่ระบุ S&P 500 แต่ Asset ตั้ง Nasdaq-100 → ข้าม (ไม่ตรง) · ตรงกัน (USDJPY Nasdaq-100) → รับ",
              sk.count("ตั้งตลาดอ้างอิงก่อน") >= 2 and "ไม่ตรง" in sk and len(r["m"]) == 1 and "USDJPY" in r["m"][0], r)
        js(page, "()=>wiPasteClose()")
        # ตั้งตลาดอ้างอิง BTCUSD = Bitcoin แล้วรับ
        open_settings(page)
        page.locator(row(page, "BTCUSD", "[data-as-ref]")).select_option("Bitcoin"); save_settings(page)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); satV3Render({force:true}); }"); settle(page, 400)
        r = imp(d2)
        check(f"{tag} 3 ตั้ง BTCUSD = Bitcoin แล้ว งานวิจัย ref_market Bitcoin ของ BTC → รับ (map ผ่าน alias ไม่ซ้ำ Asset)", any("BTC → BTCUSD" in m for m in r["m"]), r)
        js(page, "()=>wiPasteClose()")
        # ───── ชื่อที่แสดง → ลิงก์เดิมไม่หลุด
        js(page, """()=>{ const B=getBook('main'); B.trades.push(makeTradeObject({id:'tx1', date:'2026-09-29', sym:'XAG', port:'satB', bias:'Long', entry:30, sl:29, tp:33, qty:1, mult:5000, cur:'USD', status:'open'}));
          B.trades.push(makeTradeObject({id:'tbr', date:'2026-09-20', sym:'BRENT', port:'satB', bias:'Long', entry:80, sl:78, tp:84, qty:1, mult:100, cur:'USD', status:'closed', exitPrice:82, exitDate:'2026-09-24'})); saveBook('main'); render(); }"""); settle(page, 500)
        iid = js(page, "()=>{ lfSatSet('XAUUSD'); return satV2NewPlan('XAUUSD'); }"); settle(page, 500)
        open_settings(page)
        page.locator(row(page, "XAG", "[data-as-label]")).fill("เงิน"); save_settings(page)
        lk = js(page, "(i)=>({label: sat7dLabel('XAG'), idea: !!satIdeasList.find(x=>x.id===i && x.asset==='XAUUSD'), open: getBook('main').trades.filter(t=>t.sym==='XAG' && t.status==='open').length, id: satAssets({all:true}).some(a=>a.key==='XAG')})", iid)
        check(f"{tag} 3 เปลี่ยนชื่อที่แสดง XAG → 'เงิน': รหัส/ไม้/แผนเดิมยังผูกกัน (ID ไม่เปลี่ยน)", lk == {"label": "เงิน", "idea": True, "open": 1, "id": True}, lk)
        # ───── ปิดใช้งานสินค้าที่มีประวัติ (BRENT: ไม้ปิดแล้ว) และที่ถูกใช้ (XAUUSD: เลือกสัปดาห์นี้ + แผน)
        DIALOGS.clear()
        open_settings(page)
        page.locator(row(page, "BRENT", "[data-as-active]")).uncheck()
        page.locator(row(page, "XAUUSD", "[data-as-active]")).uncheck()
        save_settings(page)
        check(f"{tag} 3 ปิดใช้งานสินค้าที่ถูกใช้ (XAUUSD เลือกอยู่ + มีแผน) → ถามยืนยันก่อน (BRENT ไม่ถูกใช้ ไม่ถาม) แล้วบันทึก", len(DIALOGS) == 1 and "XAUUSD" in DIALOGS[0] and js(page, "()=>[wiAssetActive('XAUUSD'), wiAssetActive('BRENT')]") == [False, False], DIALOGS)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); satV3Render({force:true}); }"); settle(page, 500)
        hid = js(page, """()=>{ waSheetOpen(); const rows = [...document.querySelectorAll('[data-wa-row]')].map(r=>r.dataset.waRow); waSheetClose(); const chips = [...document.querySelectorAll('[data-wi-chip]')].map(c=>c.dataset.wiChip); return {rows, chips}; }""")
        check(f"{tag} 3 ปิดใช้งานแล้วหายจาก ＋ Asset และจากชิป Weekly Impact (BRENT · XAUUSD)", "BRENT" not in hid["rows"] and "XAUUSD" not in hid["rows"] and "BRENT" not in hid["chips"] and "XAUUSD" not in hid["chips"], hid)
        keep = js(page, "(i)=>({idea: !!satIdeasList.find(x=>x.id===i), picked: satIsPicked('XAUUSD'), label: sat7dLabel('BRENT'), tile: !!document.querySelector('[data-ln1-tile=\"XAUUSD\"]'), closed: getBook('main').trades.filter(t=>t.sym==='BRENT' && t.status==='closed').length, sym: symDisp('BRENT')})", iid)
        check(f"{tag} 3 ของที่บันทึกแล้วยังทำงาน: แผน XAUUSD · XAUUSD ยังเลือกอยู่ในสัปดาห์นี้และการ์ดยังอยู่ · ไม้ปิดของ BRENT ยังอยู่ · ชื่อยังแสดงจากรายการเต็ม", keep["idea"] and keep["picked"] and keep["tile"] and keep["closed"] == 1 and keep["label"] == "Brent" and keep["sym"] == "BRENT", keep)
        js(page, "()=>{ switchTab('journal'); }"); settle(page, 800)
        jt = js(page, "()=>document.getElementById('tabJournal').innerText")
        check(f"{tag} 3 Journal ยังแสดงไม้ BRENT ที่ปิดแล้วพร้อมชื่อ (ไม่ผ่านรายการ active)", "Brent" in jt or "BRENT" in jt, jt[:200])
        js(page, "()=>{ switchTab('mix'); }"); settle(page, 600)
        check(f"{tag} 3 Port เปิดได้ ไม่ error", not ce and not pe, [ce[:2], pe[:2]])
        # ปิด/เปิดกลับ: ข้อมูลหนัก ๆ ไม่เปลี่ยน
        open_settings(page)
        page.locator(row(page, "BRENT", "[data-as-active]")).check(); page.locator(row(page, "XAUUSD", "[data-as-active]")).check(); save_settings(page)
        check(f"{tag} 3 เปิดใช้งานกลับ → กลับมาใน ＋ Asset/Weekly Impact · cfg สะอาด (ไม่เก็บ active:true)", js(page, "()=>[wiAssetActive('BRENT'), wiAssetActive('XAUUSD'), JSON.stringify(satAssetCfg().BRENT||null)]") == [True, True, "null"])
        # Playbook link ต่อสินค้า
        open_settings(page)
        page.locator(row(page, "XAG", "[data-as-pb]")).select_option("ETH"); save_settings(page)
        pbk = js(page, "()=>[satPbKeyOf('XAG'), (tdSettings().satPbLink||{}).XAG]")
        open_settings(page)
        page.locator(row(page, "XAG", "[data-as-pb]")).select_option(""); save_settings(page)
        pbk2 = js(page, "()=>[satPbKeyOf('XAG'), (tdSettings().satPbLink||{}).XAG||null]")
        check(f"{tag} 3 Playbook link ต่อสินค้า: XAG → ETH แล้วกลับอัตโนมัติ (XAG เดิม) · แผน/ไม้ไม่เปลี่ยน", pbk == ["ETH", "ETH"] and pbk2 == ["XAG", None], [pbk, pbk2])
        check(f"{tag} 3 Risk / ขนาดไม้ / โบรกไม่ขยับหลังทุกการแก้ (ยกเว้น satAssetCfg/satPbLink)", ctx_settings(page) == before, sdiff(ctx_settings(page), before))
        ow = js(page, "()=>document.documentElement.scrollWidth - innerWidth")
        check(f"{tag} 3 ไม่ล้นแนวนอน · ไม่มี console error", ow <= 0 and not ce and not pe, [ow, ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        mapping_tests(pw)
        sunday_tests(pw)
        asset_tests(pw, 390, 844, "390px", shots=True)
        asset_tests(pw, 300, 700, "300px")
        asset_tests(pw, 1440, 900, "1440px")
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
