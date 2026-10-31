#!/usr/bin/env python3
"""LN1 — หน้าแผน Sat แบบ Lean (สวิตช์ Lean/เดิม) · Trend แทน Bias · ฟอร์มหน้าเดียว · Setup ชิป · ปุ่ม TradingView · แผน bp พับ · เทส 80
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย · Satellite $45,000
ภาพ tests/screenshots/ln1-{weekly,form-main,form-tactical,legacy-row,old-mode}-{1440,390}.png
รัน: python3 run_tests_phase80.py   (วันอาทิตย์เวลาไทย: p3/p2 ล้มหลอก — ไม่เกี่ยวกับชุดนี้)"""
from pf2_retire import retired_wm1 as retired3
import functools, json, os, re
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE   # ชุดนี้ต้องการค่าเริ่มจริง (Lean) — ชุดเก่า seed "แบบเดิม" เอง · SET1: แฟลกนักพัฒนา dash.ln1Legacy ให้ตรวจโหมดเดิมได้
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase54 as P54
import run_tests_phase59 as P59
import run_tests_phase76 as P76
import run_tests_phase77 as P77
import run_tests_phase78 as P78

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, overflow = P54.txt, P54.overflow
launch, idea, calc = functools.partial(P77.launch, pin_sat=True), P77.idea, P77.calc
put, note, trades, save, cnt = P78.put, P78.note, P78.trades, P78.save, P78.cnt


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(900)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def mode(page, m):
    js(page, "(m)=>ln1SetMode(m)", m); page.wait_for_timeout(500)


def week(page, asset):
    return js(page, "(a)=>JSON.parse(JSON.stringify(satwWeek(wpWeekKey(), a)||{}))", asset)


def click(page, sel, n=0):
    page.locator(sel).nth(n).click(); page.wait_for_timeout(450)


def tile(asset): return f'.ln1-tile[data-key="{asset}"]'


def norm(ts):
    out = []
    for t in ts:
        o = {k: v for k, v in t.items() if k not in ("id", "date", "openedAt", "createdAt", "created_at", "at", "ts")}
        out.append(o)
    return out


def calc_all(page, iid):
    return js(page, """(i)=>{ const x = satIdeasList.find(y=>y.id===i); return sat7dAccts().map(a=>{ const c = satV3PlanAcctCalc(x, a.id);
      return {a:a.id, lot:c.lot, ready:c.ready, blocks:c.blocks, warns:c.warns, limit:c.v2.limit, deal:c.v2.lotDeal, risk:c.v2.actualTHB}; }); }""", iid)


def flip(page, T, d):
    """LN3 — สลับทิศ Trend ต้องใส่เหตุผลทุกครั้ง"""
    page.locator(f"{T} [data-ln1-trend={d}]").first.click(); page.wait_for_timeout(450)
    page.locator(f"{T} [data-ln3-why]").fill("ทดสอบ"); page.wait_for_timeout(150)
    page.locator(f"{T} [data-ln3-ok]").click(); page.wait_for_timeout(500)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 สวิตช์
    b, page, ce, pe = launch(pw, w, h)
    try:
        P11.wk(page, "XAUUSD", "Long", "up", inval=4000)
        js(page, "()=>{ satwWrite('XAUUSD',{support:[4120,4060],resistance:[4250],invalidation:4300}); }"); page.wait_for_timeout(300)
        iid = idea(page, sleeve="main", entry=4180, sl=4117)
        check(f"{tag} 1 ค่าเริ่ม = Lean (กล่อง Strategy + ฟอร์ม Lean · ไม่มีแถบ Bias เดิม)", js(page, "()=>ln1Mode()") == "lean" and cnt(page, ".ln1-tile") >= 1 and cnt(page, "[data-ln1-form]") == 1 and cnt(page, ".ui-bias-btn") == 0)
        js(page, "()=>{ openSettings(); document.getElementById('satV2Sec').open = true; document.querySelectorAll('#ln3SetHost > .ln3-g').forEach(d=>d.open = true); }"); page.wait_for_timeout(300)
        r = js(page, "()=>document.querySelectorAll('#ln1ModeLean, #ln1ModeLegacy').length")
        check(f"{tag} 1 SET1: ตั้งค่า › Sat ไม่มีสวิตช์ 'หน้าแผน: Lean / แบบเดิม' แล้ว (Lean ตายตัว)", r == 0, r)
        before = js(page, "()=>JSON.stringify({w: satWeekMap, i: satIdeasList, b: getBook('main').trades})")
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(500)   # SET1 — สวิตช์ใน Settings ถูกเอาออก · สลับผ่านโค้ดด้วยแฟลกนักพัฒนา
        st = js(page, "()=>({m: ln1Mode(), ls: localStorage.getItem('ln1_plan_view')})")
        js(page, "()=>{ closeSettings && closeSettings(); }") if js(page, "()=>typeof closeSettings==='function'") else None
        page.wait_for_timeout(300)
        after = js(page, "()=>JSON.stringify({w: satWeekMap, i: satIdeasList, b: getBook('main').trades})")
        check(f"{tag} 1 สลับเป็น 'แบบเดิม' → เก็บใน localStorage · ข้อมูล (Bias/แผน/ไม้) เท่าเดิมทุกตัว", st == {"m": "legacy", "ls": "legacy"} and before == after, st)
        pv = js(page, """()=>({tf: !!document.querySelector('[data-v2-card] [data-v2-tf]'), plan: !!document.querySelector('.ui-plan [data-v2-entry]'), sum: !!document.querySelector('#satV3Sum .ui-tiles'), hd: !!document.querySelector('[data-pv2-header]'),
          lean: document.querySelectorAll('.ln1-tile,[data-ln1-form]').length, tp: !!document.querySelector('.ui-tile[data-key=XAUUSD] .ui-tile-th .ui-btn-pri')})""")
        js(page, "()=>satV3Pick('XAUUSD')"); page.wait_for_timeout(400)
        pv["bias"] = cnt(page, ".ui-bias-btn") == 0   # PF1 — ปุ่ม Bias ถอดแล้ว
        check(f"{tag} 1 หน้าแบบเดิม = PV2c: ฟอร์มมี TF · ตารางเดิม · ช่องสรุป Strategy · แถบ Risk · ไม่มีปุ่ม Bias (PF1) · ไม่มีของ Lean", pv["tf"] and pv["plan"] and pv["sum"] and pv["hd"] and pv["tp"] and pv["bias"] and pv["lean"] == 0, pv)
        shot(page, f"ln1-old-mode-{sfx}.png", "#satV3Panel")
        mode(page, "lean")
        check(f"{tag} 1 สลับกลับ Lean ได้ทันที · ข้อมูลยังเท่าเดิม", cnt(page, ".ln1-tile") >= 1 and js(page, "()=>JSON.stringify({w: satWeekMap, i: satIdeasList, b: getBook('main').trades})") == before)
    finally: b.close()

    # ── 2 ผลคำนวณเท่ากันทั้งสองโหมด
    res = {}
    for m in ("lean", "legacy"):
        b, page, ce, pe = launch(pw, w, h, bias="Neutral")
        try:
            mode(page, m)
            i1 = idea(page, sleeve="main", entry=4180, sl=4117); note(page, i1)
            i2 = idea(page, sleeve="tactical", entry=4240, sl=4260, bias="Short"); page.wait_for_timeout(400); note(page, i2)
            c1, c2 = calc_all(page, i1), calc_all(page, i2)
            if m == "lean": js(page, "(i)=>{ ln3ToggleDraft(i); }", i1); page.wait_for_timeout(400)   # PF3b — แผนร่างเปิดทีละอัน: แตะหัว i1 ให้ฟอร์มขึ้นก่อนอ่านหน้าจอ
            dom = js(page, """()=>[...document.querySelectorAll('.ui-plan')].map(p=>({id:p.dataset.id, t:p.innerText.replace(/\\s+/g,' ')}))""")
            save(page, i1); save(page, i2)
            res[m] = {"c1": c1, "c2": c2, "dom": dom, "tr": {a: norm(trades(page, a)) for a in ("main", "fam")}, "i1": i1, "i2": i2}
        finally: b.close()
    L, O = res["lean"], res["legacy"]
    check(f"{tag} 2 Main (4,180 / 4,117) · Tactical (4,240 / 4,260) × 2 บัญชี: lot · Risk · บล็อก ตรงกันทั้งสองโหมด", L["c1"] == O["c1"] and L["c2"] == O["c2"] and all(x["lot"] for x in L["c1"] + L["c2"]), [L["c1"], O["c1"]])
    d1 = next(x["t"] for x in L["dom"] if x["id"] == L["i1"]) if any(x["id"] == L["i1"] for x in L["dom"]) else ""
    lots = [str(round(x["lot"], 3)).rstrip("0").rstrip(".") for x in L["c1"]]
    check(f"{tag} 2 ตัวเลขที่แสดงบนหน้าจอ Lean = ผลคำนวณ (lot ของทั้งสองบัญชีอยู่ในแถวขนาดไม้)", all(l in d1 for l in lots) and "ไม้ 1/3 · 50/30/20" in d1, [lots, d1[:300]])
    check(f"{tag} 2 บันทึก order แล้วไม้ที่ได้เหมือนกันทั้งสองโหมด (ยกเว้น id/เวลา) · 2 ไม้/บัญชี", L["tr"] == O["tr"] and all(len(v) == 2 for v in L["tr"].values()), [len(L["tr"]["main"]), len(O["tr"]["main"])])

    # ── 3-5 Trend / ทิศค่าเริ่ม / Setup ชิปเดิม — ถอดโดย PF1: PF3 ตรวจว่าของเดิมหายจริง + ทางใหม่ทำงาน (ดู phase98 ด้วย)
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        t_ = js(page, "()=>{ const t = document.querySelector('.ln1-tile[data-key=XAUUSD]'); return {tr: t.querySelectorAll('[data-ln1-trend],[data-ln1-flat],[data-ln3-zone],[data-ln3-shift],[data-ln1-notrade]').length, op: !!t.querySelector('textarea[data-ln3-opinion]'), plan: !!t.querySelector('[data-ln1-plan]')}; }")
        check(f"{tag} 3 PF1 — tile Lean ไม่มี Trend/Flat/Zone/Shift/งดเทรด · มีความคิดเห็นเรา · มี + แผน", t_ == {"tr": 0, "op": True, "plan": True}, t_)
        tile = js(page, "()=>document.querySelector('.ln1-tile[data-key=XAUUSD]').innerText.replace(/\\s+/g,' ')")
        wkd = js(page, "()=>{ const w = satwWeek(wpWeekKey(), 'XAUUSD') || {}; return {bias: w.bias || null}; }")
        q = lambda sel: cnt(page, ".ln1-tile[data-key=XAUUSD] " + sel)
        check(f"{tag} 3 PF3 เริ่ม Bias Long (ข้อมูลเก่า): tile ไม่มีปุ่ม Up/Down และ Flat ไม่มีช่องติ๊ก", q("[data-ln1-trend]") == 0 and q("[data-ln1-flat]") == 0, [q("[data-ln1-trend]"), q("[data-ln1-flat]")])
        check(f"{tag} 3 PF3 ไม่มีปุ่มกด Down/Up ที่เขียน bias/trend_dir · Bias เก่าใน DB ไม่ถูกแตะ (ยัง Long)", q("[data-ln1-trend]") == 0 and wkd["bias"] == "Long", wkd)
        check(f"{tag} 3 PF3 ไม่มีช่องติ๊ก Flat / เอา Flat ออก", q("[data-ln1-flat]") == 0 and "Flat" not in tile, tile[:160])
        check(f"{tag} 3 PF3 ไม่มีปุ่ม 'งดเทรดสัปดาห์นี้' (bias None เขียนจาก UI ไม่ได้)", q("[data-ln1-notrade]") == 0 and "งดเทรด" not in tile, tile[:160])
        check(f"{tag} 3 PF3 tile ไม่แสดง Neutral/trend_dir ของข้อมูลเก่า (ไม่มี Trend ในหน้า Strategy)", "Neutral" not in tile and "trend" not in tile.lower(), tile[:160])
        check(f"{tag} 3 PF3 tile ไม่มีแถว Zone ▲/▼ · Shift · เหลือ Macro/ความเห็น/+ แผน", q("[data-ln3-zone]") == 0 and q("[data-ln3-shift]") == 0 and "Zone" not in tile and "Shift" not in tile and "Macro" in tile, tile[:200])
        i_new = idea(page, sleeve="main", bias="")
        d_new = js(page, "(i)=>satIdeasList.find(x=>x.id===i).bias", i_new)
        check(f"{tag} 4 PF3 แผนใหม่ไม่ได้ทิศเริ่มต้นจาก Strategy (Bias เก่า Long): Trend ของแผนว่าง ('' ไม่ใช่ Long)", d_new in ("", None), d_new)
        js(page, "([i])=>satV3IdeaDelete(i)", [i_new]); page.wait_for_timeout(400)
        i_sh = idea(page, sleeve="main", entry=4180, sl=4240, bias="Short"); note(page, i_sh)
        c_sh = P78.calc(page, i_sh)
        check(f"{tag} 4 PF3 Strategy bias เก่า Long แต่แผนเลือก Short → ไม่ถูกบล็อก (ไม่มี SR1 สวน Trend/Bias) · พร้อมบันทึก", c_sh["ready"] and not any(("สวน" in x) for x in c_sh["blocks"] + c_sh["warns"]), c_sh)
        form = txt(page, ".ln1-card") or ""
        check(f"{tag} 5 PF3 ฟอร์มไม่มี Setup ชิปเดิม (Break EMA20 · Break PoC Week · Break EMA50 · PoC Support) · มีชิป Setup on minor ใหม่ (In the zone · MA Align Overlap)", not any(x in form for x in ("Break EMA20", "Break PoC Week", "Break EMA50", "PoC Support")) and "In the zone" in form and "MA Align Overlap" in form, form[:240])
        js(page, "([i])=>satV3IdeaDelete(i)", [i_sh]); page.wait_for_timeout(400)
    finally: b.close()

    # ── 6 รูปแบบฟอร์ม + 9 ภาพ/แผน bp  (ใช้ launch เดียวกัน)
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iid)
        rect = lambda sel: js(page, "(s)=>[...document.querySelectorAll(s)].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.top), Math.round(r.left), Math.round(r.width)]; })", sel)
        pr = rect(".ln1-g3 input")
        check(f"{tag} 6 Entry · SL · TP อยู่แถวเดียว 3 ช่อง (บรรทัดเดียวกัน · กว้างพอพิมพ์)", len(pr) == 3 and len({x[0] for x in pr}) == 1 and pr[0][1] < pr[1][1] < pr[2][1] and all(x[2] >= 60 for x in pr), pr)
        rows = rect("[data-ln1-acct]")
        check(f"{tag} 6 ขนาดไม้ 2 บัญชีเรียงต่อกัน (บัญชีหลัก → Family) · ไม่มีแท็บ", len(rows) == 2 and rows[0][0] < rows[1][0] and cnt(page, ".ln1-card [role=tab], .ln1-card .ui-tabs, .ln1-card .tabs") == 0, rows)
        row_txt = txt(page, "[data-ln1-acct]")
        check(f"{tag} 6 แถวบัญชี: ชื่อ+โบรก · lot · Risk$ · ✓ · 'ไม้ 1 จาก 3 (50/30/20)' · รายละเอียดพับไว้", "บัญชีหลัก" in row_txt and "lot" in row_txt and "pts" in row_txt and "Risk $" in row_txt and cnt(page, "[data-ln3-leg=main]") == 1 and js(page, "()=>document.querySelector('[data-ln1-more]').open") is False and "ตารางเพดาน" not in row_txt, row_txt)
        js(page, "()=>{ document.querySelector('[data-ln1-more]').open = true; }")
        check(f"{tag} 6 PF1 — กาง รายละเอียด ▸ → ตารางเพดาน/ตัวจำกัดเดิมครบ · ไม่มี TF ซ้ำ (TF อยู่แถว Trade Overview)", cnt(page, "[data-ln1-more] [data-v2-tf]") == 0 and cnt(page, "[data-pf-tf]") == 1)
        check(f"{tag} 6 PF1 — ปุ่มบันทึกอยู่ท้ายฟอร์ม", "บันทึก" in (txt(page, ".ln1-card .ui-plan-cta") or ""))
        js(page, "()=>{ document.querySelector('[data-ln1-more]').open = false; }")
        shot(page, f"ln1-form-main-{sfx}.png", ".ln1-card")
        js(page, "([i])=>satV3IdeaDelete(i)", [iid]); page.wait_for_timeout(400)
        it = idea(page, sleeve="tactical", entry=4240, sl=4260); js(page, "([i])=>satV2SetDir(i,'Short')", [it]); page.wait_for_timeout(400); note(page, it)
        check(f"{tag} 6 PF1 — Tactical: มีช่อง TP (บังคับ · A4) · ไม้ 1 จาก 1 ไม่แสดงบรรทัดแบ่งไม้", cnt(page, "input[data-v2-tp=tac]") == 1)
        shot(page, f"ln1-form-tactical-{sfx}.png", ".ln1-card")
        js(page, "([i])=>satV3IdeaDelete(i)", [it]); page.wait_for_timeout(400)
        # แผน bp เดิม
        js(page, "()=>{ satV3NewPlan('XAUUSD'); }"); page.wait_for_timeout(600)
        lg = js(page, "()=>{ const d = document.querySelector('[data-ln1-legacy]'); return d ? {open: d.open, t: d.querySelector('summary').textContent.trim(), inner: d.querySelectorAll('.ui-plan, .ui-wait').length} : null; }")
        check(f"{tag} 8 แผน bp เดิมในโหมด Lean = แถวพับ 'รูปแบบเดิม · 1 แผน' (ปิดอยู่) · ไม่โผล่เป็นการ์ดนอกพับ", lg and lg["t"] == "รูปแบบเดิม · 1 แผน ▸" and lg["open"] is False and cnt(page, ".ui-pgrid > .ui-pcell .ui-plan[data-id]:not([data-ln1-x])") >= 0 and js(page, "()=>document.querySelectorAll('.ln1-card').length") == 0, lg)
        page.locator("[data-ln1-legacy] summary").click(); page.wait_for_timeout(500)
        lg2 = js(page, "()=>{ const d = document.querySelector('[data-ln1-legacy]'); return {open: d.open, n: d.querySelectorAll('.ui-plan, .ui-wait').length, vis: d.querySelector('.ui-plan, .ui-wait').getBoundingClientRect().height > 0}; }")
        check(f"{tag} 8 กดกาง → เป็นการ์ดเดิม (ไม่ถูกวาดทับตอนข้อมูลเปลี่ยน)", lg2["open"] and lg2["n"] >= 1 and lg2["vis"], lg2)
        shot(page, f"ln1-legacy-row-{sfx}.png", "#satV3Panel")
        mode(page, "legacy")
        check(f"{tag} 8 โหมดแบบเดิม: แผน bp เป็นการ์ดตามเดิม (ไม่มีแถว 'รูปแบบเดิม')", cnt(page, "[data-ln1-legacy]") == 0 and cnt(page, ".ui-pgrid .ui-plan, .ui-pgrid .ui-wait") >= 1)
    finally: b.close()

    # ── 7 TradingView + ภาพไม่โหลดซ้ำ
    b, c_, page, ce2, pe2, dl, env = P59.launch(pw, w, h, mut=P77.fixture(), pick=["XAUUSD", "BTCUSD"])
    try:
        js(page, "()=>satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD'])"); page.wait_for_timeout(200)
        js(page, "(c)=>{ satwWrite('XAUUSD', {bias:'Long', trend_dir:'up', support:[3920], resistance:[4080], invalidation:3840, chart:c}); satwWrite('BTCUSD', {bias:'Long'}); }", P76.CHART); page.wait_for_timeout(500)
        P37.go_sat(page); page.wait_for_timeout(400)
        tv = js(page, "()=>[...document.querySelectorAll('[data-ln1-tv]')].map(a=>[a.dataset.ln1Tv, a.getAttribute('href'), a.textContent.trim(), a.target, a.closest('.vwImg')!==null])")
        retired3(f"{tag} 7 มีลิงก์กราฟ = ปุ่ม 'เปิด TradingView ↗' มุมบนขวาของรูป (ลิงก์ที่ตั้งไว้ · แท็บใหม่) · ไม่มีลิงก์ (BTC) = ไม่แสดง", "WM1 §7 — ไม่มีรูป/ลิงก์ chart ใน Strategy")
        js(page, "()=>satV2NewPlan('XAUUSD','main')"); page.wait_for_timeout(600)
        ok0 = js(page, P76.WATCH)
        for sel in ("[data-sleeve=tactical]", "[data-pf-setup=in_zone]", "[data-sleeve=main]", "[data-pf-setup=align_ma50]"):
            page.locator(sel).first.click(force=True); page.wait_for_timeout(450)
        st = js(page, P76.STATE)
        retired3(f"{tag} 7 กด ส่วน/Setup/Zone Activation หลายรอบ (PF1) → รูปกราฟไม่โหลดซ้ำ (RR2)", "WM1 §7 — ไม่มีรูปใน Strategy แล้ว")
        click(page, f"{tile('XAUUSD')} [data-ln1-tv]") if False else None
        shot(page, f"ln1-weekly-{sfx}.png", "#satV3Sum")
        # ไม่มีลิงก์หลังลบกราฟ
        js(page, "()=>{ if(document.activeElement) document.activeElement.blur(); satwWrite('XAUUSD',{chart:null}); }"); page.wait_for_timeout(500)
        check(f"{tag} 7 ลบกราฟ → ปุ่ม TradingView หาย", cnt(page, "[data-ln1-tv]") == 0, js(page, "()=>[JSON.stringify((satwWeek(wpWeekKey(),'XAUUSD')||{}).chart), document.querySelectorAll('[data-ln1-tv]').length, (document.querySelector('[data-ln1-tv]')||{outerHTML:''}).outerHTML.slice(0,120)]"))
    finally: b.close()

    # ── 9 ล้น + console
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iid)
        js(page, "()=>{ document.querySelector('[data-ln1-more]').open = true; const f = document.querySelector('.ln1-tile .ln1-fold'); if(f) f.open = true; }"); page.wait_for_timeout(300)
        check(f"{tag} 9 {label} ไม่ล้นแนวนอน (กางทุกพับ) · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
