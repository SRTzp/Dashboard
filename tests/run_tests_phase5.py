#!/usr/bin/env python3
"""7D.4 — ปรับหน้าแผน Future: (A) Strategy เหลือ 2 องค์ประกอบ (Trend · Macro) · ตัด Fund-flow · Trend Shift
(B) การ์ดแผน 2 ขั้น (conditions → บันทึกแผน → Activate → Entry/SL → บันทึก order) · Setup ผ่านที่ 65%
+ เคสที่ค้างจาก 7D.3 (แนวรับ 3 ค่า reload / ลบทีละค่า / ลบหมดแล้วไม่ดึง comps.zone.levels กลับ)

ไฟล์แยก (ไม่แตะเคสรอบก่อน) — รันที่ 1440px และ 430px · ทดสอบผ่าน DOM จริง (คลิก/พิมพ์) เป็นหลัก
ภาพการ์ด 2 ขั้นเก็บที่ tests/screenshots/7d4-*.png

การใช้งาน: CHROMIUM_PATH=".../Google Chrome" python3 run_tests_phase5.py
"""
import json, os, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base   # ใช้ launch_page (login + mock Firebase) ร่วมกัน

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def seed_playbook(page, stances=("up", "up", "up", "none")):
    """F2c — Macro อ่านจาก Playbook (ไม่ใช่ comps.macro.v) → seed เวอร์ชัน active 1 ตัวให้ XAUUSD/BTC/BRENT (ค่าเริ่มต้น ▲ ทั้งหมด = ตรงกับที่เคสเดิมตั้ง macro ▲ ด้วยมือ)"""
    assets = {}
    for a, st in zip(["XAUUSD", "BTC", "BRENT", "US"], stances):
        assets[a] = {"stance": "none"} if st == "none" else {"stance": st, "why": "ตัวอย่าง why", "change_if": "ตัวอย่าง change_if", "drivers": ["P1"]}
    doc = {"schema": "macroPlaybook/v1", "quarter": "2026Q4", "status": "active", "view": {"headline": "h", "thesis": "t",
           "pillars": [{"id": "P1", "title": "เสาหลัก 1"}]}, "assets": assets,
           "savedAt": "2026-09-01T00:00:00.000Z", "versionNo": 1, "prevId": None, "reason": None, "stanceChanges": {}}
    page.evaluate("""(d)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','macroPlaybook','2026Q4-v001'], d); pbStop(); pbStart(); }""", doc)
    page.wait_for_timeout(150)


def goto_sat(page):
    page.evaluate("() => switchTab('plan')")
    page.evaluate("() => setPlanScope('future')")
    page.wait_for_timeout(250)


def fill_blur(page, sel, val):
    page.fill(sel, val)
    page.evaluate("(s)=>{ const el=document.querySelector(s); if(el) el.blur(); }", sel)
    page.wait_for_timeout(80)


def reload_keep_state(page):
    """จำลอง reload จริง: mock Firestore อยู่ในหน่วยความจำของหน้า → dump ก่อน แล้ว seed กลับหลัง reload แล้ว login ใหม่"""
    page.wait_for_timeout(1500)   # ให้ schedulePersist (debounce) เขียนก้อน users/{uid} ให้เสร็จก่อน dump
    dump = page.evaluate("() => window.firebase.__mockDb.__dump()")
    page.reload(wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("""(dump)=>{ window.__MOCK_UID='testuid';
        Object.keys(dump).forEach(k=>window.firebase.__mockDb.__seedDoc(k.split('/'), dump[k])); }""", dump)
    page.fill("#authEmail", "test@example.com")
    page.fill("#authPass", "password123")
    page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(400)
    goto_sat(page)


def ensure_pick(page, asset):
    """WA1fix — ไม่มีโหมด legacy: asset ต้องอยู่ใน pick สัปดาห์นี้ (เพดาน 3) ก่อนมีการ์ด · ไม่อยู่ → ใส่เป็นตัวแรก ตัดตัวท้ายออกถ้าเกิน"""
    page.evaluate("(a)=>{ if(satIsPicked(a)) return; const l = satWeekPickList().filter(k=>k!==a); satWeekPickWrite(wpWeekKey(), [a].concat(l).slice(0,3)); satV3Render(); }", asset)
    page.wait_for_timeout(120)


def open_editor(page, asset):
    """เปิดตัวแก้ของ asset (idempotent — แตะซ้ำที่ช่องเดิมจะพับ จึงเช็คก่อน)"""
    ensure_pick(page, asset)
    if page.evaluate(f"() => !!document.querySelector('.ui-editor[data-asset=\"{asset}\"] .ui-factors')"):
        return
    # คลิกที่ชื่อสินค้า (.ui-tile-a) ไม่ใช่กึ่งกลาง .ui-tile-th — จอ 430 กึ่งกลางแถวหัวไปตกบนปุ่ม [+ แผน] ที่ขึ้นบรรทัดล่างเต็มความกว้าง
    page.click(f'.ui-tile[data-key="{asset}"] .ui-tile-th .ui-tile-a')
    page.wait_for_timeout(100)


def set_bias_dom(page, asset, letter):
    open_editor(page, asset)
    # PF1 — ปุ่ม Bias ใน Strategy ถอดแล้ว: seed Bias เก่าด้วยตัวช่วยเทส (mock-firebase.js)
    page.evaluate("([a,b])=>satV3SetBias(a,b)", [asset, {"L": "Long", "S": "Short", "N": "Neutral"}[letter]])
    page.wait_for_timeout(150)


def run(pw, width, height, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, console_errors, page_errors = base.launch_page(pw, width, height, base.DEFAULT_INDEX)
    goto_sat(page)
    page.evaluate("()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: สัดส่วนแบ่งไม้ 100/0/0 = ไม้ 1 เข้าเต็ม RPT เหมือนก่อน PY2 (เคสเดิมไม่ได้ทดสอบการแบ่งไม้)
    seed_playbook(page)

    # ═════════════ A1 — SAT_FACTORS เหลือ 2 องค์ประกอบ · ทุกจุดนับจาก SATW_COMPS_SCORED ═════════════
    f = page.evaluate("() => ({scored: SATW_COMPS_SCORED, keys: SAT_FACTORS.map(x=>x.k), zone: SAT_FACTORS.find(x=>x.k==='zone')})")
    check(f"{tag} SAT_FACTORS: องค์ประกอบให้คะแนน = Trend · Macro เท่านั้น (SATW_COMPS_SCORED)", f["scored"] == ["trend", "macro"], json.dumps(f))
    check(f"{tag} SAT_FACTORS: zone คง kind:'levels' · ไม่มี momentum/sentiment ใน SAT_FACTORS",
          f["zone"] and f["zone"].get("kind") == "levels" and "momentum" not in f["keys"] and "sentiment" not in f["keys"], json.dumps(f))

    bar0 = page.evaluate("() => satV3StrategyBarHtml()")
    check(f"{tag} PF3 ช่องที่ยังไม่ประเมิน: ไม่มีป้าย 'ยังไม่ประเมิน' (ป้ายประเมิน Bias ถอด) · ไม่จาง · มีปุ่ม [+ แผน] ทุกช่อง", "ยังไม่ประเมิน" not in bar0 and "ui-dim" not in bar0 and bar0.count("+ แผน") >= 3, bar0[:200])

    # momentum/sentiment ที่เคยบันทึกไว้ (ข้อมูลเดิม) ต้องไม่ถูกนับ และไม่ถูกลบ
    page.evaluate("""() => satwWrite('XAUUSD', {comps:{momentum:{v:'up',note:'เก่า'},sentiment:{v:'up'},zone:{v:'up',levels:[1900]}}}); """)
    page.wait_for_timeout(150)
    t0 = page.evaluate("() => satwTally(satwWeek(wpWeekKey(),'XAUUSD'))")
    check(f"{tag} ข้อมูลเดิม momentum/sentiment ไม่ถูกนับ (tally n=0) แต่ยังอยู่ในเอกสาร (ไม่ลบ)",
          t0["n"] == 0 and page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').comps.momentum.note") == "เก่า", json.dumps(t0))

    open_editor(page, "XAUUSD")
    ed = page.evaluate("() => document.querySelector('.ui-editor[data-asset=\"XAUUSD\"]').outerHTML")
    n_factor = page.evaluate("() => document.querySelectorAll('.ui-editor[data-asset=\"XAUUSD\"] .ui-factor').length")
    check(f"{tag} ตัวแก้ Strategy: มีช่อง ▲▬▼ แค่ 2 (Trend · Macro) ไม่มี Momentum/Sentiment",
          n_factor == 2 and "Trend" in ed and "Macro" in ed and "Momentum" not in ed and "Sentiment" not in ed, f"n={n_factor}")

    # ═════════════ A2 — Macro: ไม่มี Fund-flow · ยังมี ▲▬▼ + โน้ต · ป้ายจางใต้ Macro ═════════════
    check(f"{tag} Macro: ตัดมุมมอง Fund-flow ออกจาก Strategy (ไม่มีข้อความ Fund-flow ในตัวแก้)", "Fund-flow" not in ed)
    # [F2c แก้เคสเดิม] เดิม: ป้าย 'ใส่เอง · จะเชื่อม Playbook…' + satwMacroFF ต้องยังอยู่ + แตะ ▲▬▼ ของ Macro ได้ → Macro ไม่ใช่ช่องกรอกเองอีกแล้ว
    check(f"{tag} Macro (F2c): ป้าย 'ใส่เอง · จะเชื่อม Playbook…' ถูกลบแล้ว", "ใส่เอง" not in ed and "จะเชื่อม Playbook" not in ed)
    check(f"{tag} satwMacroFF (F2c) ถูกลบแล้ว", page.evaluate("() => typeof satwMacroFF === 'undefined'"))
    page.click('.ui-editor[data-asset="XAUUSD"] .ui-factor:has(.ui-f-n:text-is("Macro"))', force=True)
    page.wait_for_timeout(120)
    check(f"{tag} Macro (F2c): แตะช่อง Macro ไม่เขียน comps.macro.v (อ่านจาก Playbook)",
          page.evaluate("() => { const c = (satwWeek(wpWeekKey(),'XAUUSD')||{}).comps||{}; return !(c.macro && c.macro.v); }"))
    fill_blur(page, '.ui-editor[data-asset="XAUUSD"] input[data-my-opinion]', "Fed dovish")
    mc = page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').comps.macro")
    check(f"{tag} Macro (F2c): My opinion เก็บที่ comps.macro.note เดิม", mc.get("note") == "Fed dovish" and mc.get("v") is None, json.dumps(mc))

    # ═════════════ A3 — ผิดเมื่อ → Trend Shift ═════════════
    ed = page.evaluate("() => document.querySelector('.ui-editor[data-asset=\"XAUUSD\"]').outerHTML")
    check(f"{tag} PF3 ตัวแก้ไม่มีช่อง Trend Shift และไม่มีป้าย 'ผิดเมื่อ' (ถอดทั้งช่อง)", "Trend Shift" not in ed and "ผิดเมื่อ" not in ed, ed[:200])
    page.evaluate("()=>satwSetInvalidation('XAUUSD','2600')")   # PF1 — ช่อง Trend Shift ถอดแล้ว: seed ข้อมูลเดิมด้วยตัวช่วยเทส
    check(f"{tag} Trend Shift ใช้ field เดิม (invalidation)", page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD').invalidation") == 2600)
    page.click('.ui-editor[data-asset="XAUUSD"] .ui-factor:has(.ui-f-n:has-text("Trend"))')   # Trend → ▲
    page.wait_for_timeout(100)
    set_bias_dom(page, "XAUUSD", "L")
    tile = page.evaluate("() => document.querySelector('.ui-tile[data-key=\"XAUUSD\"]').innerText")
    # [F2c แก้เคสเดิม] ป้าย 'Long · 2/2' → 'Long · ขนาดไม้ เต็ม' (Macro ▲ จาก Playbook + Trend ▲ ตาม Long = ไม่สวน)
    check(f"{tag} PF3 ช่องพับ: ไม่โชว์ 'Long · ขนาดไม้' และไม่โชว์ 'Trend Shift <2,600' (ข้อมูลเก่ายังอยู่ใน DB แต่ UI ไม่แสดง)", "Long" not in tile and "ขนาดไม้" not in tile and "Trend Shift" not in tile and "2,600" not in tile, tile)
    dots = page.evaluate("() => document.querySelectorAll('.ui-tile[data-key=\"XAUUSD\"] .ui-tile-dot').length")
    check(f"{tag} จุดสถานะ = 2 จุด", dots == 2, str(dots))
    check(f"{tag} PF3 Bias=Long (ข้อมูลเก่า) กับ trend/macro ▲: ตัวแก้ไม่มีเตือนสวนองค์ประกอบ/สวน Trend/Bias ใด ๆ (satV3Warnings ถอด)", not any(w in page.evaluate("() => satV3EditorHtml('XAUUSD', wpWeekKey())") for w in ("สวนองค์ประกอบ", "สวน Trend", "ui-warn")))

    # ═════════════ B (ค้างจาก 7D.3) — แนวรับ 3 ค่า / ลบ 1 / ลบหมด ═════════════
    open_editor(page, "XAUUSD")
    fill_blur(page, '.ui-editor[data-asset="XAUUSD"] input[onchange*="satwSetSupport"]', "2600, 2610, 2620")
    reload_keep_state(page)
    sup = page.evaluate("() => satV3SupportDisplay(satwWeek(wpWeekKey(),'XAUUSD')).values")
    check(f"{tag} 7D.3 ค้าง: แนวรับ 3 ค่า → reload อยู่ครบ", sup == [2600, 2610, 2620], json.dumps(sup))
    open_editor(page, "XAUUSD")
    chips = page.evaluate("() => document.querySelectorAll('.ui-editor[data-asset=\"XAUUSD\"] .ui-fl:has(input[onchange*=\"satwSetSupport\"]) .ui-chip').length")
    check(f"{tag} 7D.3 ค้าง: ชิปแนวรับหลัง reload = 3", chips == 3, str(chips))
    page.click('.ui-editor[data-asset="XAUUSD"] .ui-fl:has(input[onchange*="satwSetSupport"]) .ui-chip:nth-child(2) .ui-chip-x')
    page.wait_for_timeout(200)
    sup = page.evaluate("() => satV3SupportDisplay(satwWeek(wpWeekKey(),'XAUUSD')).values")
    check(f"{tag} 7D.3 ค้าง: ลบ 1 ค่า (คลิก ✕ จริง) → เหลือ 2600, 2620", sup == [2600, 2620], json.dumps(sup))
    for _ in range(2):
        page.click('.ui-editor[data-asset="XAUUSD"] .ui-fl:has(input[onchange*="satwSetSupport"]) .ui-chip:nth-child(1) .ui-chip-x')
        page.wait_for_timeout(200)
    reload_keep_state(page)
    raw = page.evaluate("() => satwWeek(wpWeekKey(),'XAUUSD')")
    sup = page.evaluate("() => satV3SupportDisplay(satwWeek(wpWeekKey(),'XAUUSD')).values")
    check(f"{tag} 7D.3 ค้าง: ลบหมด → reload แล้วไม่ดึง comps.zone.levels (1900) กลับ · comps.zone.levels เดิมไม่ถูกลบ",
          sup == [] and raw["support"] == [] and raw["comps"]["zone"]["levels"] == [1900], json.dumps({"sup": sup, "support": raw.get("support"), "zone": raw["comps"]["zone"]}))

    # ═════════════ Setup ผ่านที่ 65% (Calc) ═════════════
    sp = page.evaluate("() => [Calc.setupPass(2,3), Calc.setupPass(3,4), Calc.setupPass(2,4), Calc.setupPass(1,3), Calc.setupPass(3,3), Calc.setupPass(0,0), Calc.setupPass(2,4,0.5), Calc.setupPass(2,3,'x')]")
    check(f"{tag} Calc.setupPass: 2/3 ผ่าน · 3/4 ผ่าน · 2/4 ไม่ผ่าน · 1/3 ไม่ผ่าน · 3/3 ผ่าน · 0/0 ไม่ผ่าน · ปรับเกณฑ์ได้ · ค่าเพี้ยน→0.65",
          sp == [True, True, False, False, True, False, True, True], json.dumps(sp))
    check(f"{tag} เกณฑ์เริ่มต้น 0.65 (settings.satSetupPassRatio ไม่ตั้ง)", page.evaluate("() => satV3SetupPassRatio()") == 0.65)
    ok_keep = page.evaluate("""() => { state.settings.satSetupPassRatio = 0.5; openSettings(); saveSettings();
        const kept = state.settings.satSetupPassRatio; const ratio = satV3SetupPassRatio();
        const p24 = Calc.setupPass(2, 4, ratio); delete state.settings.satSetupPassRatio;
        return {kept, ratio, p24}; }""")
    check(f"{tag} เกณฑ์อ่านจาก settings (0.5 → 2/4 ผ่าน) และ saveSettings() ไม่ทำค่าหาย",
          ok_keep["kept"] == 0.5 and ok_keep["ratio"] == 0.5 and ok_keep["p24"] is True, json.dumps(ok_keep))

    # ═════════════ B — การ์ด 2 ขั้น (DOM จริง) ═════════════
    # PV2a: ปุ่ม [+ แผน] สร้างแผนฟอร์ม v2 แล้ว (ดู phase77) — เคสนี้ทดสอบการ์ดเดิม (kind bp) จึงสร้างผ่าน satV3NewPlan ตรง ๆ
    page.evaluate("() => satV3NewPlan('XAUUSD')")
    page.wait_for_timeout(250)
    card = page.evaluate("() => { const c=document.querySelector('.ui-pgrid .ui-plan'); return c ? c.outerHTML : ''; }")
    idea_id = page.evaluate("() => document.querySelector('.ui-pgrid .ui-plan').dataset.id")
    check(f"{tag} [+ แผน] → การ์ดขั้นวางแผนขึ้น 1 ใบ", card != "" and page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length") == 1)
    check(f"{tag} ขั้นวางแผน: ไม่มีชิปราคาแนวรับ/แนวต้าน (ตัดแล้ว) และไม่มีช่อง Entry/SL/TP/Cancel Level",
          "ui-plan-nums" not in card and ">Entry<" not in card and "satV3PlanEdit(" not in card and page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan > .ui-chips .ui-chip').length") == 0, card[:200])
    idea = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    check(f"{tag} ไอเดียใหม่: conditions=[bp 1 ข้อ] (AC2) planned=false ไม่เติม Entry จากแนวรับ", len(idea["conditions"]) == 1 and idea["conditions"][0]["kind"] == "bp" and idea["planned"] is False and idea["entry"] is None, json.dumps(idea))
    dis = page.evaluate("() => document.querySelector('.ui-plan-cta .ui-btn-pri').disabled")
    check(f"{tag} เงื่อนไขยังว่าง (ยังไม่กรอกอะไร) → ปุ่ม [บันทึกแผน] ปิดอยู่", dis is True)

    # AC2: ไม่มีชิปปุ่มลัด/ช่องข้อความ — กรอก Break Price 2650 ในเงื่อนไข A (ที่มีมาตั้งแต่สร้างแผน)
    check(f"{tag} แผนใหม่: ไม่มีปุ่มลัด/ช่องข้อความ (AC2 · แทนเคส 'ปุ่มลัด → โฟกัสช่องข้อความ')", page.locator(".ui-plan .ui-cond-sc, .ui-plan .ui-cond-text").count() == 0)
    page.fill('.ui-plan .ui-ac [data-ac-px="brk"]', "2650")
    page.evaluate("() => document.activeElement.blur()")
    page.wait_for_timeout(250)
    ca = page.evaluate(f"() => sat7dIdea('{idea_id}').conditions")
    check(f"{tag} Break Price = 2650 (แทนข้อความ 'Break & Pullback @ 2650' · AC2)", len(ca) == 1 and ca[0]["brk_px"] == 2650 and ca[0]["text"] == "", json.dumps(ca))
    check(f"{tag} เงื่อนไขใหม่: active=false · tp_from/tp_to/inval ว่าง (null)",
          ca[0]["active"] is False and ca[0]["tp_from"] is None and ca[0]["tp_to"] is None and ca[0]["inval"] is None, json.dumps(ca[0]))
    condA = ca[0]["id"]
    sel = lambda cid, f: f'.ui-cond[data-cond="{cid}"] input[onchange*="\'{f}\'"]'
    fill_blur(page, sel(condA, "tp_from"), "2700")
    fill_blur(page, sel(condA, "tp_to"), "2720")
    fill_blur(page, sel(condA, "inval"), "2600")

    page.evaluate(f"() => satV3CondAdd('{idea_id}', 'Swing back in demand zone @ 2620')")   # AC2: ไม่มีปุ่มลัด — เรียกฟังก์ชันตรง (ข้อเก่าแบบมี text · หลายเงื่อนไข)
    page.wait_for_timeout(250)
    ca = page.evaluate(f"() => sat7dIdea('{idea_id}').conditions")
    condB = ca[1]["id"]
    check(f"{tag} ปุ่มลัด 'Swing back in demand zone @' → ข้อ B = 'Swing back in demand zone @ 2620'", len(ca) == 2 and ca[1]["text"] == "Swing back in demand zone @ 2620", json.dumps(ca))
    fill_blur(page, sel(condB, "tp_from"), "2690")   # คนละ TP zone กับ A — กรอกกลับด้านตั้งใจ (2690 > 2680)
    fill_blur(page, sel(condB, "tp_to"), "2680")

    # เพิ่มเอง (ข้อ C ว่าง)
    page.evaluate(f"() => satV3CondAdd('{idea_id}', 'พิมพ์เอง 2630')")   # AC2: ไม่มี '+ เพิ่มเอง' — เรียกฟังก์ชันตรง
    page.wait_for_timeout(250)
    ca = page.evaluate(f"() => sat7dIdea('{idea_id}').conditions")
    check(f"{tag} '+ เพิ่มเอง' + พิมพ์เองได้ (ข้อ C) → มี 3 ข้อ", len(ca) == 3 and ca[2]["text"] == "พิมพ์เอง 2630", json.dumps(ca))
    condC = ca[2]["id"]

    # ภาพขั้นวางแผน
    page.locator(".ui-pcell").first.screenshot(path=os.path.join(SHOTS, f"7d4-step1-plan-{label.replace('px','')}.png"))

    # ✕ ลบเงื่อนไขข้อ C (ผู้ใช้กดเอง)
    page.click(f'.ui-cond[data-cond="{condC}"] .ui-cond-x')
    page.wait_for_timeout(200)
    ca = page.evaluate(f"() => sat7dIdea('{idea_id}').conditions")
    check(f"{tag} ✕ ลบเงื่อนไขข้อ C → เหลือ A, B (ไม่ลบข้ออื่น)", [c["id"] for c in ca] == [condA, condB], json.dumps(ca))

    # ขั้นวางแผนไม่มีช่อง Activate
    check(f"{tag} ขั้นวางแผน: ยังไม่มีช่อง Activate", page.evaluate("() => document.querySelectorAll('.ui-cond-act').length") == 0)

    # บันทึกแผน → satIdeas เท่านั้น ไม่สร้างไม้ → แถว 'รอเงื่อนไข · 2 ข้อ'
    trades_before = page.evaluate("() => ['main','fam'].map(a=>getBook(a).trades.length)")
    page.click('.ui-plan-cta .ui-btn-pri:has-text("บันทึกแผน")')
    page.wait_for_timeout(300)
    trades_after = page.evaluate("() => ['main','fam'].map(a=>getBook(a).trades.length)")
    idea = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    wait_html = page.evaluate("() => { const r=document.querySelector('.ui-wait'); return r ? r.innerText : ''; }")
    check(f"{tag} [บันทึกแผน]: เขียน satIdeas เท่านั้น (planned=true) ไม่สร้างไม้ในสมุดใดเลย",
          idea["planned"] is True and trades_before == trades_after and not any((idea.get("accts") or {}).values()), json.dumps([trades_before, trades_after]))
    check(f"{tag} [บันทึกแผน]: ยุบเป็นแถว 'รอเงื่อนไข' 2 เงื่อนไข (การ์ดหาย) — 7D.5",
          "รอเงื่อนไข" in wait_html and page.evaluate("() => document.querySelectorAll('.ui-wait .ui-wc').length") == 2
          and page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length") == 0, wait_html)

    # reload → แผนอยู่ครบ
    reload_keep_state(page)
    ideaR = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    waitR = page.evaluate("() => { const r=document.querySelector('.ui-wait'); return r ? r.innerText : ''; }")
    check(f"{tag} reload: เงื่อนไข 2 ข้อ (พร้อม TP zone ของแต่ละข้อ) + แถว 'รอเงื่อนไข' (2 เงื่อนไข) อยู่ครบ",
          ideaR and [c["text"] for c in ideaR["conditions"]] == ["", "Swing back in demand zone @ 2620"] and ideaR["conditions"][0]["brk_px"] == 2650
          and ideaR["conditions"][0]["tp_from"] == 2700 and ideaR["conditions"][1]["tp_from"] == 2690 and "รอเงื่อนไข" in waitR, json.dumps(ideaR)[:400])
    check(f"{tag} reload: [+ แผน] ซ้ำขณะมีแผนรออยู่ → ไม่สร้างใบซ้ำ",
          (page.evaluate("() => { satV3NewPlan('XAUUSD'); return satIdeasList.filter(x=>x.v3 && x.asset==='XAUUSD' && x.status!=='closed').length; }")) == 1)

    # กางการ์ด (ขั้นหน้างาน) — กด [เปิด] จริง
    page.click('.ui-wait .ui-btn:has-text("เปิด")') if page.evaluate("() => !!document.querySelector('.ui-wait')") else None
    page.wait_for_timeout(200)
    check(f"{tag} ขั้นหน้างาน: กด [เปิด] → การ์ดกาง มี 2 เงื่อนไข (AC1: ชิปติ๊กแทนช่อง Activate) แต่ยังไม่แสดง Entry/SL (ยังไม่ Activate)",
          page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length") == 1
          and page.evaluate("() => document.querySelectorAll('.ui-cond[data-cond] .ui-ac').length") == 2 and page.evaluate("() => document.querySelectorAll('.ui-cond-act').length") == 0
          and page.evaluate("() => document.querySelectorAll('.ui-plan-nums').length") == 0)
    page.locator(".ui-pcell").first.screenshot(path=os.path.join(SHOTS, f"7d4-step2-noactive-{label.replace('px','')}.png"))

    # Activate A → ช่องขึ้น · TP = ขอบใกล้ A (Long = min(2700,2720)=2700)
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [idea_id, condA])   # AC1: เรียกตัวทำงานเดิมตรง ๆ (7D.5: การ์ดวาดใหม่)
    page.wait_for_timeout(250)
    ideaA = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    check(f"{tag} Activate A → ช่อง Entry/SL/TP/Cancel Level ขึ้น · TP เริ่มต้น = 2700 (ขอบใกล้ของ A · Long)",
          page.evaluate("() => document.querySelectorAll('.ui-plan-nums').length") == 1 and ideaA["tp"] == 2700, json.dumps(ideaA["conditions"]) + str(ideaA["tp"]))
    # Activate B → ย้าย · TP = min(2690,2680)=2680 (กรอกกลับด้านก็ได้ขอบใกล้)
    # 7D.5: มีข้อ Activate แล้ว ข้ออื่นย่อเป็น '▸ เงื่อนไขอื่นรออยู่ n ข้อ' → กางแล้วกด [ใช้ข้อนี้]
    page.click(f'.ui-plan[data-id="{idea_id}"] .ui-oth-t')
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [idea_id, condB])   # AC1: แถวสั้นไม่มีปุ่ม [ใช้ข้อนี้] แล้ว
    page.wait_for_timeout(250)
    ideaB = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    act = [c["id"] for c in ideaB["conditions"] if c["active"]]
    check(f"{tag} Activate B → ย้ายจาก A (active มีข้อเดียว = B) · TP = 2680 (ขอบใกล้ของ B ที่กรอกกลับด้าน 2690–2680 · Long)",
          act == [condB] and ideaB["tp"] == 2680, json.dumps({"act": act, "tp": ideaB["tp"]}))
    tp_val = page.evaluate("() => document.querySelector('.ui-plan-nums input[onchange*=\"\\'tp\\'\"]').value")
    check(f"{tag} ช่อง TP แสดง 2680 และแก้ได้ (พิมพ์ทับ)", tp_val == "2680")

    # กรอก Entry/SL/Cancel → lot ต่อบัญชี (§7 เดิม: main/XM 0.19 lot)
    root = f'.ui-plan[data-id="{idea_id}"]'
    fill_blur(page, f'{root} input[onchange*="\'entry\'"]', "2650")
    fill_blur(page, f'{root} input[onchange*="\'sl\'"]', "2630")
    fill_blur(page, f'{root} input[onchange*="cancel_level"]', "2600")
    page.evaluate("() => { const s=getBook('main').settings; s.satRisk={rpt:1.25, rptHi:1.5}; }")   # SR1 — fixture: ค่าเดิม 1.25/1.5 (ตัวเลขคาดหวังเดิมคงไว้)
    lot = page.evaluate(f"() => satV3PlanAcctCalc(sat7dIdea('{idea_id}'), 'main').lot")
    check(f"{tag} §7 lot เดิมยังได้ค่าเท่าเดิม: XAUUSD main/XM = 0.15 lot", lot is not None and abs(lot - 0.15) < 1e-9, str(lot))
    check(f"{tag} คำนวณ lot ต่อบัญชี + ปุ่ม 'บันทึก order ทุกบัญชีที่พร้อม (2)' ตามเดิม",
          "บันทึก order ทุกบัญชีที่พร้อม (2)" in page.evaluate(f"() => document.querySelector('{root} .ui-plan-cta .ui-btn-pri').innerText"))
    su_txt = page.evaluate(f"() => document.querySelector('{root} .ui-hint:not(.ui-cond-hint)') ? [...document.querySelectorAll('{root} .ui-hint')].map(e=>e.innerText).join('|') : ''")
    check(f"{tag} Setup 0/3 → ไม่แสดงบรรทัดเตือนในการ์ดแล้ว (AC2) · ค่าคำนวณยัง pass:false (ไม่บล็อก)", "ต่ำกว่า 65%" not in su_txt and page.evaluate(f"() => satV3SetupsReady(sat7dIdea('{idea_id}')).pass") is False, su_txt)
    page.locator(".ui-pcell").first.screenshot(path=os.path.join(SHOTS, f"7d4-step2-active-{label.replace('px','')}.png"))

    # Setup 2/3 → ผ่าน
    chips = page.locator(f'{root} .ui-chips .ui-chip', has_text="Sweep")
    page.click(f'{root} .ui-chip:has-text("Sweep")')
    page.wait_for_timeout(150)
    page.click(f'{root} .ui-chip:has-text("BigBar")')
    page.wait_for_timeout(150)
    su_txt = page.evaluate(f"() => [...document.querySelectorAll('{root} .ui-hint')].map(e=>e.innerText).join('|')")
    su_calc = page.evaluate(f"() => {{ const su = satV3SetupsReady(sat7dIdea('{idea_id}')); return {{n: su.n, pass: su.pass, label: satV3SetupLabel(su)}}; }}")
    check(f"{tag} Setup 2/3 → ผ่าน (AC2: ไม่แสดงบรรทัดในการ์ด · ค่าคำนวณ 2/3 pass:true ไม่มีคำเตือน)", "Setup 2/3" not in su_txt and su_calc == {"n": 2, "pass": True, "label": "Setup 2/3"} and "นอกแผน" not in su_txt, json.dumps([su_txt, su_calc]))
    page.click(f'{root} .ui-chip:has-text("BigBar")')
    page.wait_for_timeout(150)
    su_txt = page.evaluate(f"() => [...document.querySelectorAll('{root} .ui-hint')].map(e=>e.innerText).join('|')")
    su_calc = page.evaluate(f"() => {{ const su = satV3SetupsReady(sat7dIdea('{idea_id}')); return {{n: su.n, pass: su.pass, label: satV3SetupLabel(su)}}; }}")
    check(f"{tag} Setup 1/3 → ไม่ผ่าน (AC2: ไม่แสดงบรรทัดในการ์ด · ค่าคำนวณ 1/3 pass:false · ข้อความเตือน 'ต่ำกว่า 65% = Setup ไม่ครบ' ยังสร้างได้)", "ต่ำกว่า 65%" not in su_txt and su_calc == {"n": 1, "pass": False, "label": "Setup 1/3 · ต่ำกว่า 65% = Setup ไม่ครบ"}, json.dumps([su_txt, su_calc]))
    page.click(f'{root} .ui-chip:has-text("BigBar")')   # กลับเป็น 2/3
    page.wait_for_timeout(150)

    # บันทึก order (DOM จริง)
    page.click(f'{root} .ui-plan-cta .ui-btn-pri:has-text("บันทึก order")')
    page.wait_for_timeout(300)
    tr = page.evaluate(f"""() => {{ const i = sat7dIdea('{idea_id}'); return ['main','fam'].map(a=>getBook(a).trades.find(t=>t.id===((i.accts||{{}})[a]||{{}}).trade_id)||null); }}""")
    check(f"{tag} บันทึก order: ไม้ทั้ง 2 บัญชีถูกเขียน port=satB status=plan", all(t and t["port"] == "satB" and t["status"] == "plan" for t in tr), json.dumps(tr)[:300])
    t0 = tr[0]
    check(f"{tag} ไม้มี condition_id + entry_condition (สำเนาข้อความ) + tp_zone ของข้อ B · TP=2680",
          t0["condition_id"] == condB and t0["entry_condition"] == "Swing back in demand zone @ 2620"
          and t0["tp_zone"] == {"from": 2690, "to": 2680} and t0["tp"] == 2680, json.dumps(t0))
    check(f"{tag} Setup 2/3 ผ่าน → ไม้ไม่ติดธงนอกแผน (unplanned=false)", t0.get("unplanned") is False, str(t0.get("unplanned")))
    check(f"{tag} บันทึก order → การ์ดยุบ กลายเป็นแถว plan (อ่านจากไม้ในสมุด)",
          page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length") == 0
          and page.evaluate("() => document.querySelectorAll('#satV3Panel .ui-row button').length") > 0
          and "เข้าแล้ว" in page.evaluate("() => document.getElementById('satV3Panel').innerText"))

    # ลบข้อ A ได้ ไม้ไม่กระทบ
    snap = json.dumps(page.evaluate(f"() => getBook('main').trades.find(t=>t.id==='{t0['id']}')"), sort_keys=True)
    page.evaluate(f"() => satV3CondRemove('{idea_id}','{condA}')")
    page.wait_for_timeout(200)
    snap2 = json.dumps(page.evaluate(f"() => getBook('main').trades.find(t=>t.id==='{t0['id']}')"), sort_keys=True)
    left = page.evaluate(f"() => sat7dIdea('{idea_id}').conditions.map(c=>c.id)")
    check(f"{tag} ลบเงื่อนไขข้อ A ได้ · ไม้ที่บันทึกแล้วไม่กระทบ (ไม่เปลี่ยนแม้แต่ field เดียว)", left == [condB] and snap == snap2, f"{left}")
    check(f"{tag} ลบข้อ B (ข้อที่ผูกกับไม้) → ไม้ยังเก็บ entry_condition/condition_id/tp_zone ครบ",
          (lambda: (page.evaluate(f"() => satV3CondRemove('{idea_id}','{condB}')"), page.wait_for_timeout(150),
                    page.evaluate(f"() => getBook('main').trades.find(t=>t.id==='{t0['id']}')"))[2])()["entry_condition"] == "Swing back in demand zone @ 2620")

    # ═════════════ TP zone กรอกกลับด้าน 4600–4580: Long → 4580 · Short → 4600 (ผ่าน UI) ═════════════
    page.evaluate("""() => { satwWrite('S50', {comps:{trend:{v:'down'},macro:{v:'down'}}, invalidation:1000}); }""")
    page.wait_for_timeout(120)
    set_bias_dom(page, "S50", "S")
    # PV2a: ปุ่ม [+ แผน] สร้างแผนฟอร์ม v2 แล้ว (ดู phase77) — เคสนี้ทดสอบการ์ดเดิม (kind bp) จึงสร้างผ่าน satV3NewPlan ตรง ๆ
    page.evaluate("() => satV3NewPlan('S50')")
    page.wait_for_timeout(250)
    sid = page.evaluate("() => satIdeasList.find(x=>x.v3 && x.asset==='S50' && x.status!=='closed').id")
    cs = page.evaluate(f"() => sat7dIdea('{sid}').conditions[0].id")   # AC2: แผนใหม่มีเงื่อนไข bp 1 ข้อให้เลย (ไม่มี '+ เพิ่มเอง')
    page.evaluate(f"() => satV3CondEdit('{sid}', '{cs}', 'text', 'Short zone')")
    fill_blur(page, f'.ui-cond[data-cond="{cs}"] input[onchange*="\'tp_from\'"]', "4600")
    fill_blur(page, f'.ui-cond[data-cond="{cs}"] input[onchange*="\'tp_to\'"]', "4580")
    page.click(f'.ui-plan[data-id="{sid}"] .ui-plan-cta .ui-btn-pri:has-text("บันทึกแผน")')
    page.wait_for_timeout(200)
    page.click('.ui-wait[data-id="' + sid + '"] .ui-btn:has-text("เปิด")')
    page.wait_for_timeout(200)
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [sid, cs])   # AC1
    page.wait_for_timeout(250)
    check(f"{tag} TP zone กรอกกลับด้าน 4600–4580 → Short ได้ TP = 4600 (ขอบใกล้ = max)", page.evaluate(f"() => sat7dIdea('{sid}').tp") == 4600)
    check(f"{tag} satV3TpNear ล้วน: 4600–4580 → Long 4580 · Short 4600 · ค่าเดียว/ไม่มีค่า",
          page.evaluate("() => [satV3TpNear({tp_from:4600,tp_to:4580},'Long'), satV3TpNear({tp_from:4600,tp_to:4580},'Short'), satV3TpNear({tp_from:4580,tp_to:4600},'Long'), satV3TpNear({tp_from:4580,tp_to:4600},'Short'), satV3TpNear({tp_from:4600,tp_to:null},'Long'), satV3TpNear({tp_from:null,tp_to:null},'Long')]")
          == [4580, 4600, 4580, 4600, 4600, None])
    # TP ที่ผู้ใช้แก้เองแล้ว ไม่ถูกทับเมื่อแก้ TP zone ของข้อที่ active
    fill_blur(page, f'.ui-plan[data-id="{sid}"] input[onchange*="\'tp\'"]', "4500")
    page.click(f'.ui-plan[data-id="{sid}"] [data-ac-bar]')   # AC2: แตะแถบ Active แทนปุ่ม ✎
    page.wait_for_timeout(150)
    fill_blur(page, f'.ui-cond-edit[data-cond-edit="{cs}"] input[onchange*="\'tp_to\'"]', "4590")
    check(f"{tag} TP ที่แก้เองแล้ว (4500) ไม่ถูกทับเมื่อแก้ TP zone", page.evaluate(f"() => sat7dIdea('{sid}').tp") == 4500)

    # ═════════════ ไอเดียเก่า (ไม่มี conditions) แสดงแบบเดิม · ใช้งานต่อได้ ═════════════
    page.evaluate("""() => { satwWrite('BRENT', {comps:{trend:{v:'up'},macro:{v:'up'}}, invalidation:80, support:[84,85]}); }""")
    page.wait_for_timeout(120)
    set_bias_dom(page, "BRENT", "L")
    page.evaluate("""() => sat7dWrite('satIdeas','iLegacy1', {v3:true, asset:'BRENT', bias:'Long', week:wpWeekKey(), created_at:new Date().toISOString(),
        entry:null, sl:null, tp:null, cancel_level:null, setups:[], status:'active', accts:{}}); """)
    page.wait_for_timeout(250)
    leg = page.evaluate("() => { const c=document.querySelector('.ui-plan[data-id=\"iLegacy1\"]'); return c ? c.outerHTML : ''; }")
    check(f"{tag} ไอเดียเก่า (ไม่มี conditions): การ์ดแบบเดิม — มีช่อง Entry/SL/TP/Cancel + ชิปราคาแนวรับ + บัญชี ไม่มีรายการเงื่อนไข",
          "ui-plan-nums" in leg and "ui-conds" not in leg and "84" in leg and "ui-plan-accts" in leg, leg[:200])
    fill_blur(page, '.ui-plan[data-id="iLegacy1"] input[onchange*="\'entry\'"]', "85")
    check(f"{tag} ไอเดียเก่า: กรอก Entry ได้ตามเดิม", page.evaluate("() => sat7dIdea('iLegacy1').entry") == 85)

    # ═════════════ พิมพ์ค้างในช่อง แล้วกดปุ่ม [บันทึกแผน] (กดค้าง 300ms) → click ต้องไม่หาย (กัน re-render ทับปุ่มระหว่าง mousedown→mouseup) ═════════════
    page.evaluate("""() => { satwWrite('BTCUSD', {comps:{trend:{v:'up'},macro:{v:'up'}}, invalidation:60000}); }""")
    page.wait_for_timeout(120)
    set_bias_dom(page, "BTCUSD", "L")
    # PV2a: ปุ่ม [+ แผน] สร้างแผนฟอร์ม v2 แล้ว (ดู phase77) — เคสนี้ทดสอบการ์ดเดิม (kind bp) จึงสร้างผ่าน satV3NewPlan ตรง ๆ
    page.evaluate("() => satV3NewPlan('BTCUSD')")
    page.wait_for_timeout(250)
    page.click('.ui-plan:has(.ui-plan-h b:text-is("BTC")) .ui-ac [data-ac-px="brk"]')   # AC2: ช่อง Break Price ของเงื่อนไขที่มีมาแล้ว
    page.wait_for_timeout(250)
    page.keyboard.type("65000")   # ยังโฟกัสอยู่ในช่อง ไม่ได้ blur เอง
    btn = page.locator('.ui-plan:has(.ui-plan-h b:text-is("BTC")) .ui-plan-cta .ui-btn-pri')
    btn.scroll_into_view_if_needed()
    box = btn.bounding_box()
    page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.mouse.down(); page.wait_for_timeout(300); page.mouse.up(); page.wait_for_timeout(300)
    bt = page.evaluate("() => satIdeasList.find(x=>x.v3 && x.asset==='BTCUSD')")
    check(f"{tag} พิมพ์ในช่อง Break Price แล้วกด [บันทึกแผน] ค้าง 300ms → คลิกไม่หาย (planned=true) และตัวเลขที่เพิ่งพิมพ์ถูกเก็บ (brk_px 65000)",
          bt["planned"] is True and bt["conditions"][0]["brk_px"] == 65000, json.dumps(bt)[:300])

    # ═════════════ ขนาดช่อง Entry/SL/TP/Cancel ═════════════
    m = page.evaluate("""() => { const i = document.querySelector('.ui-plan-nums input'); const r = i.getBoundingClientRect(); const cs = getComputedStyle(i);
        return {h: r.height, fs: parseFloat(cs.fontSize)}; }""")
    check(f"{tag} ช่อง Entry/SL/TP/Cancel สูงขึ้น ~6px (19→≈25) ตัวเลขใหญ่ขึ้น 1–2px (13.3→15)",
          m["h"] >= 24 and m["h"] <= 27 and 14.3 <= m["fs"] <= 15.5, json.dumps(m))

    # ═════════════ ระบบ ═════════════
    for tab in ["home", "port", "watch", "journal", "plan"]:
        try: page.evaluate(f"() => switchTab('{tab}')")
        except Exception: pass
    page.wait_for_timeout(200)
    goto_sat(page)
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"{tag} ไม่ล้นแนวนอน (scrollWidth = {width})", sw <= width, str(sw))
    check(f"{tag} console: zero error-level messages", len(console_errors) == 0, "; ".join(console_errors[:8]))
    check(f"{tag} console: zero uncaught page errors", len(page_errors) == 0, "; ".join(page_errors[:8]))
    context.close(); browser.close()


def main():
    with sync_playwright() as pw:
        run(pw, 1440, 900, "1440px")
        run(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok)
    n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 5 / 7D.4) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(f" - {name} :: {detail}")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
