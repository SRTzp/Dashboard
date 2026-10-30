#!/usr/bin/env python3
"""LN3fix3 §1–4 — กล่อง Macro แบบ Lean (ไม่มีพับ "รายละเอียด Macro" · เปลี่ยนเมื่อ · My opinion · แถวลิงก์) · Zone เรียงตาม Trend + B&P · สัปดาห์ใหม่ถามเก็บ Asset · Trend ว่าง · เตือน Re-check Macro · เทส 93
mock Firestore · Chromium 1440 + 390 + 320 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean · นาฬิกาปลอม
ภาพ tests/screenshots/ln3fix3-{strategy-300,strategy-390,strategy-1440,newweek-1440}.png
รัน: python3 run_tests_phase93.py"""
from pf2_retire import retired_wm1 as retired3
import copy, json, os
from pf2_retire import retired as retired2
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase13 as P13
import run_tests_phase37 as P37
import run_tests_phase77 as P77

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
overflow = C.overflow
WK0, WK1 = "2026-09-27", "2026-10-04"
LONG = "100,000–102,000"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=500): page.wait_for_timeout(ms)


def launch(pw, w, h, bias="Short", pb=True):
    """XAUUSD Trend = bias · BTC ไม่มีเอกสารสัปดาห์ (Trend ว่าง) · Playbook 2026Q4 บันทึก 27 ก.ย. · นาฬิกา 1 ต.ค."""
    b, page, ce, pe = P77.launch(pw, w, h, pb=pb, bias=bias)
    js(page, "()=>{ switchTab('plan'); setPlanScope('future'); lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 600)
    return b, page, ce, pe


def sel(a, s=""): return f'[data-ln1-tile="{a}"] {s}'.strip()


def show(page, asset):
    js(page, "(a)=>{ lfSatSet(a); satV3Render({force:true}); }", asset); settle(page, 400)


def zone_order(page, asset):
    return js(page, "(a)=>[...document.querySelectorAll('[data-ln1-tile=\"'+a+'\"] [data-ln3-zone]')].map(e=>e.dataset.ln3Zone)", asset)


def geo(page, asset, k):
    """ช่อง Zone k + ป้าย B&P: ตำแหน่ง/ความกว้างจริง"""
    return js(page, """([a,k])=>{ const t = document.querySelector('[data-ln1-tile="'+a+'"]'); const inp = t.querySelector('[data-ln3-zone="'+k+'"]'); const ck = t.querySelector('[data-ln3-bp]');
      const r = inp.getBoundingClientRect(), c = ck ? ck.closest('label').getBoundingClientRect() : null, tr = t.getBoundingClientRect();
      return {inp: [Math.round(r.left), Math.round(r.right), Math.round(r.top + r.height/2)], ck: c ? [Math.round(c.left), Math.round(c.right), Math.round(c.top + c.height/2), Math.round(c.height)] : null,
              clip: inp.scrollWidth > inp.clientWidth + 1, tile: [Math.round(tr.left), Math.round(tr.right)], fs: getComputedStyle(inp).fontSize, pad: getComputedStyle(inp).paddingLeft}; }""", [asset, k])


def sat_dump(page): return js(page, "()=>JSON.parse(JSON.stringify(satWeekMap))")


def strategy(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe = launch(pw, w, h)
    try:
        # ───── §1 กล่อง Macro Lean
        t = js(page, """()=>{ const e = document.querySelector('[data-ln1-tile="XAUUSD"]'); const T = e.innerText.replace(/\\s+/g,' ');
          return {fold: !!e.querySelector('details.ln1-fold, .ln1-fold'), txt: /รายละเอียด Macro/.test(T), editor: !!e.querySelector('.ui-editor'), tally: /รวม ▲/.test(T) || !!e.querySelector('.ui-tally'),
                  why1: /เหตุผล 1 ประโยค/.test(T), sr: /แนวรับ|แนวต้าน/.test(T), warn: /ยังไม่มี Trend Shift/.test(T), trendEd: /Trend ✎|Macro ▼/.test(T), macroRows: e.querySelectorAll('[data-ln1-row=macro]').length}; }""")
        check(f"{tag} 1 Lean: ไม่มีพับ 'รายละเอียด Macro' และของในนั้น (ตัวแก้ · รวม ▲▬▼ · เหตุผล 1 ประโยค · แนวรับ/ต้าน · ⚠ ไม่มี Trend Shift) · Macro แถวเดียว", t == {"fold": False, "txt": False, "editor": False, "tally": False, "why1": False, "sr": False, "warn": False, "trendEd": False, "macroRows": 1}, t)
        chg = js(page, "()=>({ui: (document.querySelector('[data-ln1-tile=\"XAUUSD\"] [data-ln3-chg]')||{}).innerText || null, pb: satMacroOf('XAUUSD').change_if})")
        check(f"{tag} 1 'เปลี่ยนเมื่อ …' บรรทัดเดียวอ่านอย่างเดียว ตรงกับ Playbook ของ Asset นั้น", chg["ui"] and chg["ui"].startswith("Change if · Quarterly") and chg["pb"] in chg["ui"] and js(page, "()=>document.querySelectorAll('[data-ln1-tile=\"XAUUSD\"] [data-ln3-chg] input, [data-ln1-tile=\"XAUUSD\"] [data-ln3-chg] textarea').length") == 0, chg)
        show(page, "BTCUSD")
        chg2 = js(page, "()=>(document.querySelector('[data-ln1-tile=\"BTCUSD\"] [data-ln3-chg]')||{}).innerText || null")
        check(f"{tag} 1 'เปลี่ยนเมื่อ' ของ BTC มาจาก Playbook ของ BTC (คนละบรรทัดกับ XAU)", chg2 and "up_flat" in chg2, chg2)
        show(page, "XAUUSD")
        # My opinion
        ta = page.locator(sel("XAUUSD", "[data-ln3-opinion]"))
        check(f"{tag} 1 มีช่อง 'ความคิดเห็นเรา' เป็น textarea (PF1: เดิม My opinion (Trend + Macro))", ta.count() == 1 and "Note · This week" in js(page, "()=>document.querySelector('[data-ln1-tile=\"XAUUSD\"] .ln3-op').innerText"))
        ta.fill("Trend ลงตาม real yield แต่แรงซื้อธนาคารกลางยังรับ"); ta.blur(); settle(page, 600)
        sv = js(page, "()=>satwWeek(wpWeekKey(),'XAUUSD').opinion_txt")
        js(page, "()=>satV3Render({force:true})"); settle(page, 400)
        back = js(page, "()=>document.querySelector('[data-ln1-tile=\"XAUUSD\"] [data-ln3-opinion]').value")
        check(f"{tag} 1 opinion_txt บันทึกเมื่อ change (ฟิลด์ opinion_txt บนเอกสาร satWeek) และโหลดกลับมาแสดง", sv == "Trend ลงตาม real yield แต่แรงซื้อธนาคารกลางยังรับ" and back == sv, [sv, back])
        # แถวลิงก์
        links = js(page, "()=>[...document.querySelectorAll('[data-ln1-tile=\"XAUUSD\"] [data-ln3-links] button')].map(b=>b.innerText.trim())")
        check(f"{tag} 1 PF1 — แถวลิงก์ล่าง: คัดลอกจากสัปดาห์ก่อน · เอาออกจากสัปดาห์นี้ (ไม่มี ประวัติสลับ Trend / งดเทรด)", links == ["Clear Note", "เอาออกจากสัปดาห์นี้"], links)   # WM1: Copy last week ซ่อนเมื่อสัปดาห์ก่อนไม่มี Note · Clear Note มีเสมอ   # PF2: ลิงก์นำเข้าโผล่เฉพาะกล่องว่าง + สัปดาห์ก่อนมีความเห็น
        # PF3 — PF1 ถอด Zone ▲/▼ · B&P · Shift · Trend · ประวัติสลับ ออกจากการ์ด Strategy: ตรวจว่าของเดิมหายจริง (ฟอร์มแผนตรวจใน phase98)
        X = js(page, "()=>{ const t = document.querySelector('[data-ln1-tile=\"XAUUSD\"]'); return {txt: t.innerText.replace(/\\s+/g,' '), ta: t.querySelectorAll('textarea').length, hist: t.querySelectorAll('[data-ln3-hist]').length, zone: t.querySelectorAll('[data-ln3-zone]').length, bp: t.querySelectorAll('[data-ln3-bp]').length, ask: t.querySelectorAll('[data-ln3-ask]').length, fn: [typeof satwSetZoneBp, typeof ln3ZoneSideSet, typeof ln3ZoneSide, typeof ln3ZoneBp]}; }")
        check(f"{tag} 1 PF3 แถวลิงก์ล่างไม่มี 'ประวัติสลับ Trend (n)' / 'งดเทรด' (เหลือ Clear Note · เอาออก)", "ประวัติสลับ" not in X["txt"] and "งดเทรด" not in X["txt"] and X["hist"] == 0, X["txt"][:160])
        check(f"{tag} 1 PF3 ไม่มีกล่องเหตุผลสลับ Trend: การ์ดมี textarea เดียว (ความเห็นเรา) · ไม่มีข้อความ 'เพราะ'", X["ta"] == 1 and X["ask"] == 0 and "เพราะ" not in X["txt"], X)
        check(f"{tag} 1 PF3 ไม่มีลิงก์ประวัติ → ไม่มีรายการสลับ Trend ให้เปิด", X["hist"] == 0)
        check(f"{tag} 2 PF3 ไม่มีช่อง Zone ▲/▼ ในการ์ด (ไม่มีเรียงตาม Trend)", X["zone"] == 0 and "Zone" not in X["txt"], X["txt"][:160])
        check(f"{tag} 2 PF3 ไม่มีช่อง B&P ในการ์ด", X["bp"] == 0 and "B&P" not in X["txt"])
        check(f"{tag} 2 PF3 ไม่มีทางติ๊ก B&P → ฟังก์ชันเขียน zone_bp ถอดแล้ว", X["fn"][0] == "undefined" and X["bp"] == 0, X["fn"])
        check(f"{tag} 2 PF3 ไม่มีป้าย B&P แถวเดียวกับช่อง Zone (ไม่มีทั้งคู่ → ไม่มีอะไรถูกตัด)", X["bp"] == 0 and X["zone"] == 0)
        check(f"{tag} 2 PF3 ฟอร์ม Main ไม่มีตัวเลือก Zone 2 ฝั่ง (ln3ZoneSideSet ถอดแล้ว) · มี Zone Activation แทน (ตรวจใน phase98)", X["fn"][1] == "undefined")
        check(f"{tag} 2 PF3 ไม่มีตัวเลือก zone_side (ln3ZoneSide ถอดแล้ว)", X["fn"][2] == "undefined")
        check(f"{tag} 2 PF3 ไม่มีทางเอา B&P ออก/ใส่ → ไม่มีการเขียน zone_bp (ln3ZoneBp ถอดแล้ว)", X["fn"][3] == "undefined")
        if w in (300, 390, 1440): C.shot(page, f"ln3fix3-strategy-{sfx}.png", full=True)
        check(f"{tag} 1-2 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


def trend_empty(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ satwWrite('BTCUSD', {bias: null, flips: 0}); }"); settle(page, 500)
        show(page, "BTCUSD")
        e = js(page, """()=>{ const t = document.querySelector('[data-ln1-tile="BTCUSD"]'); const hint = t.querySelector('[data-ln3-trend-empty]'), plan = t.querySelector('[data-ln1-plan]'); return {hint: !!hint, plan: plan ? plan.disabled : null}; }""")
        check(f"{tag} 3 PF1 — Asset ที่ไม่มี Trend ใน Strategy: ไม่มีแถบเหลือง · + แผน กดได้", e == {"hint": False, "plan": False}, e)
        te = js(page, "()=>{ const t = document.querySelector('[data-ln1-tile=\"BTCUSD\"]'); const w = satwWeek(wpWeekKey(),'BTCUSD') || {}; return {trend: t.querySelectorAll('[data-ln1-trend]').length, ta: t.querySelectorAll('textarea').length, ask: t.querySelectorAll('[data-ln3-ask]').length, log: (w.trend_log||[]).length}; }")
        check(f"{tag} 3 PF3 Trend ว่าง: ไม่มีปุ่ม Up/Down · ไม่มีแถบเหลือง 'ยังไม่เลือก Trend' · + แผน กดได้", te["trend"] == 0 and e["hint"] is False and e["plan"] is False, [te, e])
        check(f"{tag} 3 PF3 ไม่มีการเลือก Trend ครั้งแรก/สอง → ไม่มี trend_log เกิดใหม่ · ไม่มีกล่องถามเหตุผล (textarea เดียว = ความเห็นเรา)", te["log"] == 0 and te["ask"] == 0 and te["ta"] == 1, te)
        check(f"{tag} 3 PF3 Asset ที่เพิ่มกลางสัปดาห์ก็เหมือนกัน: ไม่มี Trend/แถบเหลือง · แผนกดได้ (เหมือนกรณี Trend ว่าง)", te["trend"] == 0 and e["plan"] is False, [te, e])
        check(f"{tag} 3 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


def new_week(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        # สัปดาห์ก่อน (27 ก.ย.): XAU ▼ ถือ 1 ไม้ · BTC ▲ · S50 งดเทรด · เอกสารเก่าห้ามถูกแตะ
        js(page, "(l)=>satWeekPickWrite(wpWeekKey(), l)", ["XAUUSD", "BTCUSD", "S50"]); settle(page, 300)
        P11.wk(page, "BTCUSD", "Long", "up"); js(page, "()=>satwWrite('S50', {bias:'None', flips:0})"); settle(page, 300)
        js(page, "()=>satwWrite('XAUUSD', {zone_up:'4,100–4,140', zone_dn:'4,280–4,320', opinion_txt:'ความเห็นเก่า', invalidation: 4300, zone_bp: true})"); settle(page, 300)
        js(page, "(t)=>{ const B = getBook('main'); B.trades = B.trades.concat([t]); saveBook('main'); render(); }", P13.T("tNW", "satB", "open", sym="XAUUSD", entry=4180, sl=4117, qty=0.05, bias="Short", date="2026-09-28"))
        settle(page, 300)
        # สัปดาห์หน้า (4 ต.ค.) มีเอกสาร XAUUSD ค้างไว้ (ไม่มี Trend) → ต้องถูกล้างตอนเริ่ม
        page.evaluate("([wk,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','satWeek',wk], c)", [WK1, {"XAUUSD": {"zone_up": "ค่าค้าง", "opinion_txt": "ค้าง", "invalidation": 5, "zone_bp": True}}]); settle(page, 500)
        macro0 = js(page, "()=>ln1MacroTxt('XAUUSD', wpWeekKey())")
        before = sat_dump(page)[WK0]
        # ───── วันพฤหัส ไม่ใช่สัปดาห์ใหม่ (มี Strategy แล้ว) → ไม่มีกล่อง
        none = js(page, "()=>!!document.querySelector('[data-nw-box]')")
        check(f"{tag} 4 กลางสัปดาห์ที่มี Strategy แล้ว (พฤ. 1 ต.ค.) → ไม่มีกล่องสัปดาห์ใหม่", none is False)
        # PF2 — เอา prompt สัปดาห์ใหม่ออกแล้ว: เคสเสาร์/ทีหลัง/เริ่มสัปดาห์ถูกถอด (PF2_retired.md) → ตรวจใหม่ใน phase99
        P37.set_clock(page, "2026-10-03T05:00:00Z")
        js(page, "()=>{ satV3Render({force:true}); }"); settle(page, 600)
        for n in ("4 เสาร์ ที่สัปดาห์หน้ายังไม่มี Strategy → กล่องเริ่มสัปดาห์ใหม่", "4 Asset ที่ยังถือไม้อยู่ = ติ๊กไว้ในกล่องสัปดาห์ใหม่", "4 กล่องสัปดาห์ใหม่ไม่ล้นแนวนอน", "4 ติ๊ก BTC ออก → ปุ่ม เริ่มสัปดาห์ (เก็บ 2)", "4 ทีหลัง ซ่อนกล่อง", "4 เริ่มสัปดาห์: pick/drop/done", "4 Asset ที่เก็บไว้: ความเห็นเรา เริ่มว่าง (nwStart)", "4 ข้อมูลสัปดาห์เก่าไม่ถูกลบหลัง nwStart"):
            retired2(f"{tag} {n}", "prompt เริ่มสัปดาห์ใหม่ (nwHtml/nwStart) ถอดแล้ว (PF2 A2)")
        check(f"{tag} 4 PF2 — เสาร์ที่สัปดาห์หน้ายังไม่มี Strategy → ไม่มีกล่องเริ่มสัปดาห์ใหม่ · ข้อมูลสัปดาห์เก่าไม่ถูกแตะ", not js(page, "()=>!!document.querySelector('[data-nw-box]')") and json.dumps(before, sort_keys=True) == json.dumps(sat_dump(page)[WK0], sort_keys=True))

        # ───── ตอบแล้ว = ไม่ถามอีก (เสาร์ → อาทิตย์)
        P37.set_clock(page, "2026-10-04T05:00:00Z")
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); waPick('XAUUSD'); lfSatSet('XAUUSD'); satV3Render({force:true}); }"); settle(page, 800)   # PF2: สัปดาห์ใหม่เริ่มว่าง → เลือก XAU เองด้วย ＋ Asset
        s = js(page, """()=>{ const t = document.querySelector('[data-ln1-tile="XAUUSD"]'); return {box: !!document.querySelector('[data-nw-box]'), wk: wpWeekKey(), op: t.querySelector('[data-ln3-opinion]').value, plan: t.querySelector('[data-ln1-plan]').disabled,
          old: t.querySelectorAll('[data-ln1-trend],[data-ln3-zone],[data-ln3-shift],[data-ln3-bp],[data-ln3-trend-empty]').length, macro: ln1MacroTxt('XAUUSD', wpWeekKey())}; }""")
        check(f"{tag} 4 อาทิตย์ (สัปดาห์ใหม่ 4 ต.ค.): ไม่ถามซ้ำ · ความเห็นเรา ว่าง · ไม่มี Trend/Zone/Shift/B&P/แถบเหลือง · + แผน กดได้ · Macro ใช้ตัวเดิมจาก Playbook",
              not s["box"] and s["wk"] == WK1 and s["op"] == "" and s["plan"] is False and s["old"] == 0 and s["macro"] == macro0, [s, macro0])
        # 'คัดลอกจากสัปดาห์ก่อน' คัดลอกเฉพาะความเห็น
        js(page, "()=>satV3CopyPrev('XAUUSD')"); settle(page, 700)
        cp = js(page, "()=>{ const w = satwWeek(wpWeekKey(),'XAUUSD'); return {op: w.opinion_txt, bias: w.bias || null}; }")
        check(f"{tag} 4 'คัดลอกจากสัปดาห์ก่อน' คัดลอกเฉพาะความเห็นเรา (PF1 B4) · ไม่คัดลอก Trend", cp == {"op": "ความเห็นเก่า", "bias": None}, cp)
        check(f"{tag} 4 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()
    # ───── สัปดาห์ใหม่กลางสัปดาห์ (จ.–ศ.) ที่ยังไม่เคยตั้ง Strategy → ถามเมื่อเปิดครั้งแรก
    b, page, ce, pe = launch(pw, w, h)
    try:
        P37.set_clock(page, "2026-10-06T05:00:00Z")
        js(page, "()=>{ satV3Render({force:true}); }"); settle(page, 700)
        retired2(f"{tag} 4 เปิดครั้งแรกของสัปดาห์ใหม่ (อังคาร 6 ต.ค.) → กล่องโผล่ด้วย", "prompt เริ่มสัปดาห์ใหม่ถอดแล้ว (PF2 A2)")
        check(f"{tag} 4 PF2 — อังคาร 6 ต.ค. ยังไม่ตั้ง Strategy → ไม่มีกล่องสัปดาห์ใหม่", not js(page, "()=>!!document.querySelector('[data-nw-box]')"))
    finally: b.close()


def recheck(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        def at(iso):
            P37.set_clock(page, iso)
            js(page, "()=>{ pbRender(); todayRefresh(true); }"); settle(page, 500)
        def state():
            return js(page, """()=>({bar: (document.querySelector('[data-pb-recheck]')||{}).innerText || null, task: (document.querySelector('[data-kind="macro-recheck"]')||{}).textContent || null,
                                      days: (pbStaleInfo()||{}).days})""")
        at("2026-10-26T10:00:00Z")   # 29 วันหลัง 27 ก.ย. 10:00Z
        s = state()
        check(f"{tag} 5 29 วันหลังอัปเดต Playbook → ไม่มีเตือนทั้งที่ Flow และ Today", s["days"] == 29 and s["bar"] is None and s["task"] is None, s)
        at("2026-10-28T10:00:00Z")   # 31 วัน
        js(page, "()=>switchTab('flow')"); settle(page, 800)
        s = state()
        check(f"{tag} 5 31 วัน → Flow การ์ด Macro ไตรมาส: แถบเหลือง '⚠ Macro ไม่ได้อัปเดต 31 วัน (ล่าสุด 27 ก.ย.) — Re-check เดือนละครั้ง · วาง JSON ใหม่ · ยืนยันว่ายังใช้ได้'",
              s["bar"] and s["bar"].replace("\n", " ").startswith("⚠ Macro ไม่ได้อัปเดต 31 วัน (ล่าสุด 27 ก.ย.) — Re-check เดือนละครั้ง · วาง JSON ใหม่ · ยืนยันว่ายังใช้ได้"), s)
        if w == 1440: C.shot(page, "ln3fix3-recheck-flow-1440.png", full=False)
        js(page, "()=>switchTab('today'); todayRefresh(true)"); settle(page, 800)
        s = state()
        check(f"{tag} 5 31 วัน → Today มีงาน '⚠ Re-check Macro · ไม่ได้อัปเดต 31 วัน' + ปุ่ม 'ไป Flow ›'", s["task"] and "Re-check Macro" in s["task"] and "ไม่ได้อัปเดต 31 วัน" in s["task"] and "ไป Flow ›" in s["task"], s)
        js(page, "()=>document.querySelector('[data-kind=\"macro-recheck\"]').click()"); settle(page, 600)
        check(f"{tag} 5 กดงานนี้ → ไปแท็บ Flow", js(page, "()=>activeTab") == "flow", js(page, "()=>activeTab"))
        before = js(page, "()=>JSON.stringify(pbList.map(v=>[v.id, v.status, v.savedAt]))")
        page.locator("[data-pb-recheck-ok]").click(); settle(page, 700)
        s = state(); chk = js(page, "()=>tdSettings().pbCheckedAt")
        after = js(page, "()=>JSON.stringify(pbList.map(v=>[v.id, v.status, v.savedAt]))")
        check(f"{tag} 5 'ยืนยันว่ายังใช้ได้' → เก็บ pbCheckedAt (ต่อผู้ใช้) · จำนวนวันนับใหม่ (0) · แถบ/งานหาย · เนื้อหา Playbook ไม่เปลี่ยน", isinstance(chk, (int, float)) and s["days"] == 0 and s["bar"] is None and s["task"] is None and before == after, [chk, s])
        at("2026-11-27T10:30:00Z")   # ยืนยันเมื่อ 28 ต.ค. 10:00Z → +30 วัน = ยังไม่เตือน
        s = state()
        at("2026-11-29T10:30:00Z")   # +32 วัน
        s2 = state()
        check(f"{tag} 5 หลังยืนยัน นับจากวันที่ยืนยัน: +30 วันยังไม่เตือน · +32 วันเตือนอีก", s["days"] == 30 and s["bar"] is None and s2["days"] == 32 and s2["task"] is not None, [s, s2])
        # วางเวอร์ชันใหม่ = รีเซ็ตด้วย
        v1 = js(page, "()=>JSON.parse(JSON.stringify(pbList[0]))")
        P11.seed_pb(page, [v1, dict(v1, id="2026Q4-v002", savedAt="2026-11-28T10:00:00.000Z", versionNo=2, prevId="2026Q4-v001")]); settle(page, 800)
        at("2026-11-29T10:30:00Z")
        s = state()
        check(f"{tag} 5 วาง JSON ใหม่ (เวอร์ชันใหม่ 28 พ.ย.) → นับใหม่ ไม่เตือน", s["days"] == 1 and s["bar"] is None and s["task"] is None, s)
        check(f"{tag} 5 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def legacy(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ ln1SetMode('legacy'); }"); settle(page, 700)
        tiles = js(page, "()=>document.querySelectorAll('#satV3Panel .ui-tile').length")
        P37.set_clock(page, "2026-10-28T10:00:00Z"); js(page, "()=>{ pbRender(); todayRefresh(true); satV3Render({force:true}); }"); settle(page, 600)
        l = js(page, """()=>({op: document.querySelectorAll('.ln3-op, [data-ln3-links], [data-nw-box], [data-ln3-chg]').length, tiles: document.querySelectorAll('#satV3Panel .ui-tile').length, bar: document.querySelectorAll('[data-pb-recheck]').length, task: document.querySelectorAll('[data-kind="macro-recheck"]').length,
                              lean: document.body.classList.contains('lf-lean')})""")
        check(f"{tag} 6 โหมดเดิม (legacy): ไม่มีกล่อง Lean ใหม่ · ไม่มีกล่องสัปดาห์ใหม่ · ไม่มีเตือน Re-check Macro (Flow/Today) — หน้าเดิมไม่เปลี่ยน", l["op"] == 0 and tiles >= 1 and l["bar"] == 0 and l["task"] == 0 and not l["lean"], l)
        check(f"{tag} 6 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (320, 700, "320px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            strategy(pw, w, h, label)
            if w in (1440, 390):
                trend_empty(pw, w, h, label); new_week(pw, w, h, label); recheck(pw, w, h, label); legacy(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
