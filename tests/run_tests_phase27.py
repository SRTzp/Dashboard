#!/usr/bin/env python3
"""7E-4 — Mean Reversion (MR · เทรดสวน Bias สั้น ๆ ที่แนว) · เทส 27
เงื่อนไข kind:'mr' ในแผน Sat เดิม · Calc.mrSide/mrCheck/mrHoldDays · ทิศที่ใช้จริง satV3SideOf · ขนาด 0.6 ตายตัว · ป้าย "MR · สวน Bias" · เตือนถือนาน
ข้อมูล: XAUUSD สัปดาห์นี้ Bias Short · Trend down · แนวรับ 2,400 · แนวต้าน 2,520 · Macro Bear (Playbook ▼) · บัญชี main โบรก XM (ข้อมูลทดสอบเดิม)
mock Firestore · Chromium 1440 + 430 · ภาพเก็บที่ tests/screenshots/7e4-*.png
รัน: python3 run_tests_phase27.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase11 as p11
from run_tests_phase11 import pbver, seed_pb, iso, txt, no_overflow, fresh, wk, reset_ideas, idea

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []



def f2c_line(page, t):
    return page.evaluate("(t)=>{ const d=document.createElement('div'); d.innerHTML=satV3F2cTradeLine(t); return d.innerText||d.textContent; }", t) or ""

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:600] + "...(truncated)") if (detail and len(detail) > 600) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(300)
    try:
        if sel and page.locator(sel).count():
            page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else:
            page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e:
        print("shot fail", name, e)


def js(page, code, arg=None):
    return page.evaluate(code, arg) if arg is not None else page.evaluate(code)


def mr_check(page, **kw):
    return js(page, "(a)=>Calc.mrCheck(a)", kw)


def setup_week(page, bias="Short", support=(2400,), resistance=(2520,)):
    seed_pb(page, [pbver(1, iso(-72), x="down", xa={"drivers": ["P1", "P2"]})])     # Macro Bear
    wk(page, "XAUUSD", bias, "down" if bias == "Short" else "up", inval=2600 if bias == "Short" else 2300)
    js(page, "(a)=>satwWrite('XAUUSD', {support:a[0], resistance:a[1]})", [list(support), list(resistance)])
    page.wait_for_timeout(200)


def mk(page, iid="iM", bias="Short", entry=None, sl=None, tp=None, active="c2", planned=True, lvl=2400, extra_conds=None, mr_tp=(2450, 2460)):
    """แผนที่มี 2 เงื่อนไข: c1 ปกติ (TP zone 2380–2350 → ขอบใกล้ Short = 2380) · c2 MR (TP zone 2450–2460 → ขอบใกล้ Long = 2450)"""
    conds = [
        {"id": "c1", "text": "Break & Pullback @ 2400", "tp_from": 2380, "tp_to": 2350, "inval": None, "active": active == "c1", "saved": True},
        {"id": "c2", "kind": "mr", "text": "MR ที่แนว 2400", "mr_level": lvl, "tp_from": mr_tp[0], "tp_to": mr_tp[1], "inval": None, "active": active == "c2", "saved": True},
    ]
    if extra_conds is not None: conds = extra_conds
    d = {"v3": True, "asset": "XAUUSD", "bias": bias, "created_at": iso(), "entry": entry, "sl": sl, "tp": tp, "cancel_level": None,
         "conditions": conds, "planned": planned, "setups": [], "status": "active", "accts": {}, "macro_note": "เหตุผลทดสอบ"}   # WA1: สวน/นอก Macro ต้องมีเหตุผลก่อนบันทึก order
    page.evaluate("([i,d])=>{ d.week = wpWeekKey(); sat7dWrite('satIdeas', i, d); }", [iid, d])
    page.wait_for_timeout(300)


def set_idea(page, iid, patch):
    page.evaluate("()=>{ if(document.activeElement && document.activeElement.blur) document.activeElement.blur(); }")
    page.evaluate("([i,p])=>satV3IdeaWrite(i,p)", [iid, patch]); page.wait_for_timeout(250)


def acct(page, iid="iM"):
    return js(page, """(i)=>{ const c = satV3PlanAcctCalc(sat7dIdea(i), 'main'); return {ready:c.ready, warns:c.warns, lot:c.lot, factor:c.factor, riskCur:c.riskCur,
        cfg: c.chosen ? c.chosen.cfg : null, mr:c.mr, mrOk:c.mrOk, heat:c.heatPct}; }""", iid)


def lot_exp(page, a, dist, factor):
    return js(page, "([cfg,r,d,f])=>Calc.satLot({riskAmount:r*f, dist:d, contract:cfg.contract, lotStep:cfg.lotStep, minLot:cfg.minLot}).lot", [a["cfg"], a["riskCur"], dist, factor])


def push_trade(page, **kw):
    base_t = {"id": "tx", "date": "2026-10-02", "sym": "XAUUSD", "port": "satB", "bias": "Long", "entry": 2410, "sl": 2390, "tp": 2450, "qty": 0.1, "mult": 100, "cur": "USD", "status": "open"}
    base_t.update(kw)
    js(page, """(o)=>{ const t = makeTradeObject(o); const B = getBook('main'); B.trades.push(t); saveBook('main'); render(); }""", base_t)
    page.wait_for_timeout(250)


def dates_with_biz_days(page, n, sym="XAUUSD"):
    """หาวันที่เริ่มที่ Calc.mrHoldDays ถึงวันนี้ (thaiToday) ได้ n พอดี"""
    return js(page, """([n, cal])=>{ const today = thaiToday(); const d = new Date(today+'T00:00:00Z');
        for(let i=0;i<30;i++){ const s = d.toISOString().slice(0,10); if(Calc.mrHoldDays({openedAt:s, today, calendar:cal})===n) return s; d.setUTCDate(d.getUTCDate()-1); } return null; }""", [n, sym == "BTCUSD"])


def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe = fresh(pw, w, h)
    page.evaluate("()=>{ ['main','fam'].forEach(a=>{ const B = getBook(a); if(B){ if(!B.settings) B.settings = {}; B.settings.satPyrSplit = [100,0,0]; saveBook(a); } }); }")   # PY2: สัดส่วนแบ่งไม้ 100/0/0 = ไม้ 1 เข้าเต็ม RPT เหมือนก่อน PY2 (เคสเดิมไม่ได้ทดสอบการแบ่งไม้)
    context.add_init_script("window.SAT_MR_ENABLED = true;"); page.evaluate("() => { window.SAT_MR_ENABLED = true; }")   # SR1 — MR ปิดเป็นค่าเริ่มต้น · เคส MR เดิมเปิดคืนเพื่อทดสอบโค้ด MR ครบ
    try:
        # ───────── 1–4 Calc ─────────
        page.evaluate("() => switchTab('flow')")
        check(f"{tag} 1 Calc.mrSide: Short→Long · Long→Short · None/ว่าง→null", js(page, "()=>[Calc.mrSide('Short'),Calc.mrSide('Long'),Calc.mrSide('None'),Calc.mrSide(null),Calc.mrSide('')]") == ["Long", "Short", None, None, None])
        L = dict(side="Long", level=2400, distPct=1)
        r = mr_check(page, entry=2410, sl=2390, tp=2450, **L)
        check(f"{tag} 2 mrCheck Long: 2410/2390/2450 → ok · ระยะ 0.42%", r["ok"] and round(r["distPct"], 2) == 0.42 and r["reasons"] == [], json.dumps(r))
        r = mr_check(page, entry=2430, sl=2390, tp=2450, **L)
        check(f"{tag} 2 mrCheck Long: Entry 2430 → 'Entry ห่างแนว 1.25% (เกิน 1%)'", (not r["ok"]) and r["reasons"] == ["Entry ห่างแนว 1.25% (เกิน 1%)"], json.dumps(r, ensure_ascii=False))
        r = mr_check(page, entry=2376, sl=2370, tp=2450, **L)
        check(f"{tag} 2 mrCheck Long: Entry 2376 = ขอบพอดี 1.00% → ok (epsilon 1e-9)", r["ok"] and abs(r["distPct"] - 1) < 1e-9, json.dumps(r))
        r = mr_check(page, entry=2410, sl=2405, tp=2450, **L)
        check(f"{tag} 2 mrCheck Long: SL 2405 → 'SL ต้องต่ำกว่าแนว 2,400'", (not r["ok"]) and r["reasons"] == ["SL ต้องต่ำกว่าแนว 2,400"], json.dumps(r, ensure_ascii=False))
        r = mr_check(page, entry=2410, sl=2390, tp=None, **L)
        check(f"{tag} 2 mrCheck Long: TP ว่าง → 'MR ต้องกรอก TP'", (not r["ok"]) and r["reasons"] == ["MR ต้องกรอก TP"], json.dumps(r, ensure_ascii=False))
        r = mr_check(page, entry=2410, sl=2390, tp=2400, **L)
        check(f"{tag} 2 mrCheck Long: TP 2400 (< Entry) → 'TP ผิดฝั่ง'", (not r["ok"]) and r["reasons"] == ["TP ผิดฝั่ง"], json.dumps(r, ensure_ascii=False))
        r = mr_check(page, side="Long", entry=2410, sl=2390, tp=2450, level=None, distPct=1)
        check(f"{tag} 2 mrCheck: ไม่มีแนว → 'ยังไม่เลือกแนว MR'", (not r["ok"]) and r["reasons"] == ["ยังไม่เลือกแนว MR"], json.dumps(r, ensure_ascii=False))
        S = dict(side="Short", level=2520, distPct=1)
        r = mr_check(page, entry=2510, sl=2530, tp=2470, **S)
        check(f"{tag} 3 mrCheck Short (แนวต้าน 2,520): 2510/2530/2470 → ok", r["ok"] and r["reasons"] == [], json.dumps(r))
        r = mr_check(page, entry=2510, sl=2515, tp=2470, **S)
        check(f"{tag} 3 mrCheck Short: SL 2515 → 'SL ต้องสูงกว่าแนว 2,520'", (not r["ok"]) and r["reasons"] == ["SL ต้องสูงกว่าแนว 2,520"], json.dumps(r, ensure_ascii=False))
        r = mr_check(page, entry=2510, sl=2530, tp=2520, **S)
        check(f"{tag} 3 mrCheck Short: TP 2520 (> Entry) → 'TP ผิดฝั่ง'", r["reasons"] == ["TP ผิดฝั่ง"], json.dumps(r, ensure_ascii=False))
        hd = lambda o, t, c=False: js(page, "(a)=>Calc.mrHoldDays(a)", {"openedAt": o, "today": t, "calendar": c})
        check(f"{tag} 4 mrHoldDays: ศุกร์→จันทร์ = 1 วันทำการ · ศุกร์→พุธ = 3 (เตือน) · ศุกร์→ศุกร์ถัดไป = 5", hd("2026-10-02", "2026-10-05") == 1 and hd("2026-10-02", "2026-10-07") == 3 and hd("2026-10-02", "2026-10-09") == 5 and hd("2026-10-02", "2026-10-02") == 0)
        check(f"{tag} 4 mrHoldDays: BTCUSD (ปฏิทิน) ศุกร์→จันทร์ = 3 วัน → เตือน · วันที่ผิดรูป = null", hd("2026-10-02", "2026-10-05", True) == 3 and hd("x", "2026-10-05") is None)

        # ───────── 5 ขั้นวางแผน: ปุ่ม ＋ MR · ชิปแนว ─────────
        p5.goto_sat(page); reset_ideas(page); setup_week(page)
        mk(page, "iP", planned=False, extra_conds=[{"id": "c1", "text": "Break & Pullback @ 2400", "tp_from": None, "tp_to": None, "inval": None, "active": False, "saved": False}])
        P = '.ui-plan[data-id="iP"]'
        check(f"{tag} 5 ขั้นวางแผน: มีปุ่ม '＋ MR สวน Bias' (แยกจากปุ่มลัดของผู้ใช้)", page.locator(f"{P} [data-mr-add]").count() == 1 and "＋ MR สวน Bias" in txt(page, f"{P} [data-mr-add]"))
        cfg_before = js(page, "()=>JSON.stringify(satConfigCondTpl)")
        page.click(f"{P} [data-mr-add]"); page.wait_for_timeout(300)
        conds = idea(page, "iP")["conditions"]
        mrc = [c for c in conds if c.get("kind") == "mr"]
        check(f"{tag} 5 กดปุ่ม → เพิ่มเงื่อนไข kind:'mr' text 'MR ที่แนว ' mr_level null · ไม่เขียน satConfig", len(conds) == 2 and len(mrc) == 1 and mrc[0]["text"] == "MR ที่แนว " and mrc[0]["mr_level"] is None and js(page, "()=>JSON.stringify(satConfigCondTpl)") == cfg_before, json.dumps(conds, ensure_ascii=False))
        MR = f'{P} [data-cond-kind="mr"]'
        check(f"{tag} 5 แถว MR: ป้าย 'MR · สวน Bias' + ชิปแนวรับ (Bias Short) = 2,400 เท่านั้น", "MR · สวน Bias" in txt(page, MR) and page.evaluate("(s)=>[...document.querySelectorAll(s+' [data-mr-level]')].map(e=>e.dataset.mrLevel)", MR) == ["2400"] and "แนวรับ" in txt(page, MR + " .ui-mr-lv"))
        shot(page, f"7e4-cond-mr-{label}.png", P)
        page.click(f'{MR} [data-mr-level="2400"]'); page.wait_for_timeout(300)
        mrc = [c for c in idea(page, "iP")["conditions"] if c.get("kind") == "mr"]
        check(f"{tag} 5 เลือกชิป 2,400 → mr_level = 2400", mrc[0]["mr_level"] == 2400 and page.locator(f'{MR} [data-mr-level="2400"].ui-on').count() == 1)
        js(page, "()=>satV3PlanSave('iP')"); page.wait_for_timeout(250)
        # Bias Long → ชิปแนวต้าน
        js(page, "()=>{ satIdeasList.map(x=>x.id).forEach(i=>satV3IdeaDelete(i)); }"); page.wait_for_timeout(250)
        wk(page, "XAUUSD", "Long", "up", inval=2300)
        mk(page, "iL", bias="Long", planned=False, extra_conds=[{"id": "c3", "kind": "mr", "text": "MR ที่แนว ", "mr_level": None, "tp_from": None, "tp_to": None, "inval": None, "active": False, "saved": False}])
        ML = '.ui-plan[data-id="iL"] [data-cond-kind="mr"]'
        check(f"{tag} 5 Bias Long → ชิปเป็นแนวต้าน 2,520", page.evaluate("(s)=>[...document.querySelectorAll(s+' [data-mr-level]')].map(e=>e.dataset.mrLevel)", ML) == ["2520"] and "แนวต้าน" in txt(page, ML + " .ui-mr-lv"))
        # ไม่มีแนว → ข้อความ + Activate กดไม่ได้
        reset_ideas(page); setup_week(page, "Short", support=(), resistance=())
        mk(page, "iN", lvl=None, active=None)
        js(page, "()=>{ satV3Open.add('iN'); satV3Render(); }"); page.wait_for_timeout(250)
        N = '.ui-plan[data-id="iN"] [data-cond-kind="mr"]'
        check(f"{tag} 5 ไม่มีแนวใน Strategy → 'ยังไม่มีแนวรับ/ต้านใน Strategy สัปดาห์นี้' + checkbox Activate ถูก disable", "ยังไม่มีแนวรับ/ต้านใน Strategy สัปดาห์นี้" in txt(page, N) and page.locator(f"{N} input[type=checkbox]").is_disabled())
        js(page, "()=>satV3CondActivate('iN','c2',true)"); page.wait_for_timeout(250)
        check(f"{tag} 5 Activate ข้อ MR ที่ไม่มีแนว (เรียกตรง) → ไม่ผ่าน", not any(c.get("active") for c in idea(page, "iN")["conditions"]))
        js(page, "()=>{ satV3Open.delete('iN'); satV3Render(); }"); page.wait_for_timeout(200)
        check(f"{tag} 5 แถวพับ 'รอเงื่อนไข': ปุ่ม Activate ของข้อ MR (ไม่มีแนว) ถูก disable · มีป้าย MR", page.locator('.ui-wait[data-id="iN"] [data-cond-kind="mr"] .ui-wc-act').is_disabled() and "MR · สวน Bias" in txt(page, '.ui-wait[data-id="iN"] [data-cond-kind="mr"]'))

        # ───────── 6–8 หน้างาน ─────────
        reset_ideas(page); setup_week(page)
        mk(page, "iM", active=None)                      # planned · ยังไม่ Activate
        week_before = js(page, "()=>JSON.stringify(satWeekMap)")
        js(page, "()=>satV3CondActivate('iM','c2',true)"); page.wait_for_timeout(350)
        C = '.ui-plan[data-id="iM"]'
        head = txt(page, f"{C} .ui-plan-h")
        check(f"{tag} 6 Activate MR → ป้ายทิศ Long + 'MR · สวน Bias' · idea.bias ยัง Short", head.startswith("XAUUSD Long") and "MR · สวน Bias" in head and idea(page, "iM")["bias"] == "Short", head)
        check(f"{tag} 6 satWeek ไม่ถูกเขียน (Bias สัปดาห์ยัง Short)", js(page, "()=>JSON.stringify(satWeekMap)") == week_before and js(page, "()=>satwWeek(wpWeekKey(),'XAUUSD').bias") == "Short")
        check(f"{tag} 6 บรรทัดกติกา: 'แนว 2,400 · Entry ต้องอยู่ 2,376–2,424 · SL ต่ำกว่า 2,400 · TP บังคับ'", "แนว 2,400 · Entry ต้องอยู่ 2,376–2,424 · SL ต่ำกว่า 2,400 · TP บังคับ" in txt(page, f"{C} [data-mr-line]"), txt(page, f"{C} [data-mr-line]"))
        check(f"{tag} 11 TP default = ขอบใกล้ตามทิศ Long (min 2450 ไม่ใช่ max 2460)", idea(page, "iM")["tp"] == 2450, str(idea(page, "iM").get("tp")))
        check(f"{tag} 6 PF3 การ์ดแผน MR (Short) ไม่มีป้าย Trend Shift ('>2,600') ของ Strategy แล้ว · ป้ายทิศของแผนยังเป็นของแผน (Long)", "Trend Shift" not in (txt(page, C) or "") and "2,600" not in (txt(page, C) or "") and idea(page, "iM")["bias"] == "Short", txt(page, C))
        check(f"{tag} 6 ไม่มีคำเตือน 'ผ่าน Trend Shift' ผิด ๆ (ใช้ทิศแผนเทียบ)", page.locator(f"{C} [data-trend-shift]").count() == 0)
        # 7 ขนาด
        page.fill(f'{C} .ui-plan-nums div:nth-child(1) input', "2410"); page.keyboard.press("Tab")
        page.fill(f'{C} .ui-plan-nums div:nth-child(2) input', "2390"); page.keyboard.press("Tab")
        page.evaluate("()=>{ if(document.activeElement && document.activeElement.blur) document.activeElement.blur(); }"); page.wait_for_timeout(350)
        a = acct(page)
        exp06 = lot_exp(page, a, 20, 0.6)
        check(f"{tag} 7 กรอก 2410/2390/(TP default 2450) → บัญชี ready · mrOk", a["ready"] and a["mr"] and a["mrOk"] and a["warns"] == [], json.dumps(a["warns"], ensure_ascii=False))
        check(f"{tag} 7 lot = Calc.satLot(riskAmount × 0.6) ตรงค่า ({a['lot']} = {exp06}) · factor 0.6 (ไม่ใช่ 0.36 แม้กฎ F2c ของ Long = 0.6 อยู่แล้ว)", a["factor"] == 0.6 and a["lot"] == exp06 and a["lot"] != lot_exp(page, a, 20, 0.36) , json.dumps({k: a[k] for k in ("lot", "factor")}))
        f2c = js(page, "()=>{ const f = satV3F2c(sat7dIdea('iM')); return {rule:f.rule.factor, factor:f.factor, off:f.off, mr:f.mr}; }")
        check(f"{tag} 7 RG2b: กฎ F2c ไม่มีตัวคูณ Macro (rule 1) แต่ MR ใช้ factor 0.6 ตายตัว · off=false", f2c == {"rule": 1, "factor": 0.6, "off": False, "mr": True}, json.dumps(f2c))
        size_row = txt(page, f'{C} [data-f2c-row="size"]')
        check(f"{tag} 7 บรรทัดขนาด: 'MR · ลด 40% (ตามค่า สวน Macro)' (WA1 แทน 'ตายตัว') · ไม่มีสวิตช์ขนาดเต็ม · ไม่มีบรรทัดกฎ F2c", "MR · ลด 40% (ตามค่า สวน Macro)" in size_row and "สวนทั้ง Macro" not in size_row and page.locator(f"{C} [data-size-switch]").count() == 0, size_row)
        # สวิตช์ override เก่าค้างอยู่ → ไม่มีผลกับ MR
        set_idea(page, "iM", {"size_full_override": True})
        a2 = acct(page)
        check(f"{tag} 7 size_full_override=true ค้างในแผน → MR ยัง 0.6", a2["factor"] == 0.6 and a2["lot"] == exp06 and page.locator(f"{C} [data-size-switch]").count() == 0)
        set_idea(page, "iM", {"size_full_override": False})
        shot(page, f"7e4-active-mr-ok-{label}.png", C)
        no_overflow(page, w, tag)
        # 8 ไม่ผ่าน
        set_idea(page, "iM", {"entry": 2430})
        a = acct(page)
        check(f"{tag} 8 Entry 2430 → ไม่ ready + 'Entry ห่างแนว 1.25% (เกิน 1%)' ต่อท้าย warns", (not a["ready"]) and a["warns"][-1] == "Entry ห่างแนว 1.25% (เกิน 1%)" and not a["mrOk"], json.dumps(a["warns"], ensure_ascii=False))
        check(f"{tag} 8 การ์ดแสดงเหตุผล · ไม่มีปุ่ม 'รวมด้วย (นอกแผน)' ของ MR ที่ไม่ผ่านกติกา", "Entry ห่างแนว 1.25% (เกิน 1%)" in txt(page, f"{C} .ui-plan-accts") and "รวมด้วย" not in txt(page, f"{C} .ui-plan-accts"), txt(page, f"{C} .ui-plan-accts"))
        js(page, "()=>satV3SaveSlot('iM','main')"); page.wait_for_timeout(300)
        check(f"{tag} 8 บันทึกตรง (satV3SaveSlot) ตอน MR ไม่ผ่าน → ไม่สร้างไม้", js(page, "()=>getBook('main').trades.filter(t=>t.mr).length") == 0)
        shot(page, f"7e4-active-mr-far-{label}.png", C)
        set_idea(page, "iM", {"entry": 2410, "tp": None})
        a = acct(page)
        check(f"{tag} 8 TP ว่าง → ไม่ ready + 'MR ต้องกรอก TP'", (not a["ready"]) and "MR ต้องกรอก TP" in a["warns"], json.dumps(a["warns"], ensure_ascii=False))
        set_idea(page, "iM", {"tp": 2450})

        # ───────── 9 บันทึก ─────────
        btn = page.locator(f'{C} .ui-btn:has-text("บันทึก order ทุกบัญชีที่พร้อม")')
        btn.scroll_into_view_if_needed(); btn.click(); page.wait_for_timeout(450)
        t = js(page, "()=>{ const a=((sat7dIdea('iM')||{}).accts||{}).main||{}; return a.trade_id ? getBook('main').trades.find(x=>x.id===a.trade_id) : null; }")
        got = {k: (t or {}).get(k) for k in ("bias", "mr", "mr_level", "plan_bias", "sizeFactor", "port", "status", "entry", "sl", "tp")}
        check(f"{tag} 9 บันทึก order: ไม้ bias Long · mr true · mr_level 2400 · plan_bias Short · sizeFactor 0.6", got == {"bias": "Long", "mr": True, "mr_level": 2400, "plan_bias": "Short", "sizeFactor": 0.6, "port": "satB", "status": "plan", "entry": 2410, "sl": 2390, "tp": 2450}, json.dumps(got))
        check(f"{tag} 9 PF3 trend_changed = null ด้วย (ไม่อ่าน Trend ของ Strategy เลย): ไม้ที่บันทึกไม่มี trend_state/trend_changed", (t or {}).get("trend_state") is None and (t or {}).get("trend_changed") is None, json.dumps({k: (t or {}).get(k) for k in ("trend_state", "trend_changed")}))
        check(f"{tag} 9 PF1 — field F2c บันทึกตามปกติ (side = Long): macro_state=against · size_rule=0.6 · off_rule=false · trend_state=null (ไม่อ่าน Strategy)", (t or {}).get("macro_state") == "against" and (t or {}).get("size_rule") == 1 and (t or {}).get("off_rule") is False and (t or {}).get("trend_state") is None, json.dumps({k: (t or {}).get(k) for k in ("macro_state","size_rule","off_rule","trend_state")}))
        check(f"{tag} 9 lot ที่บันทึก = lot ที่คำนวณ ({t and t.get('qty')})", t and t["qty"] == exp06)
        line = f2c_line(page, t)
        check(f"{tag} 9 บรรทัดรายละเอียดไม้: 'MR · ลด 40%' แทน 'ลด/เต็ม'", "MR · ลด 40%" in line and "· เต็ม" not in line, line)
        check(f"{tag} 9 แถวไม้ Sat มีป้าย 'MR · สวน Bias' · ทิศ Long", "MR · สวน Bias" in txt(page, '[data-mr-trade]') and "Long" in page.evaluate("()=>[...document.querySelectorAll('.ui-row .ui-tag')].map(e=>e.innerText).join(',')"))
        # โควตา: ไม้ใหม่ ≤ 2 / สัปดาห์ → เติมให้เต็มแล้ว MR แผนใหม่ไม่ ready
        reset_ideas(page)
        js(page, """()=>{ const B = getBook('main'); B.trades = B.trades.filter(t=>!t.mr); saveBook('main'); }""")
        for i in (1, 2, 3, 4): push_trade(page, id=f"tq{i}", date=js(page, "()=>thaiToday()"), entry=2650, sl=2620, tp=2700, bias="Short", port="satB")
        mk(page, "iQ", entry=2410, sl=2390, tp=2450)
        js(page, "()=>{ satV3Open.add('iQ'); satV3Render(); }"); page.wait_for_timeout(250)
        a = acct(page, "iQ")
        check(f"{tag} 9 โควตาไม้ใหม่เต็ม 4 → MR ก็ไม่ ready ('โควตาเต็ม')", (not a["ready"]) and "โควตาเต็ม" in a["warns"] and a["mrOk"], json.dumps(a["warns"], ensure_ascii=False))
        js(page, """()=>{ const B = getBook('main'); B.trades = B.trades.filter(t=>!/^tq/.test(t.id)); saveBook('main'); render(); }""")
        a = acct(page, "iQ")
        check(f"{tag} 9 โควตากลับว่าง → ready อีกครั้ง (heat นับเหมือนไม้ปกติ: {a['heat'] and round(a['heat'], 3)}%)", a["ready"] and a["heat"] is not None and a["heat"] > 0)

        # ───────── 10 สลับ MR ↔ ปกติ ─────────
        reset_ideas(page)
        mk(page, "iS", entry=2410, sl=2390, tp=None, active="c2")
        set_idea(page, "iS", {"act_side": "Long", "tp": 2450})
        js(page, "()=>satV3CondActivate('iS','c1',true)"); page.wait_for_timeout(350)
        i_s = idea(page, "iS")
        check(f"{tag} 10 สลับ MR → เงื่อนไขปกติ: entry/sl ถูกล้าง · ทิศกลับ Short · TP default ตามทิศ Short (max 2380)", i_s["entry"] is None and i_s["sl"] is None and i_s["tp"] == 2380 and js(page, "()=>satV3SideOf(sat7dIdea('iS'))") == "Short", json.dumps({k: i_s.get(k) for k in ("entry", "sl", "tp")}))
        CS = '.ui-plan[data-id="iS"]'
        check(f"{tag} 10 ป้ายทิศกลับเป็น Short · ไม่มีป้าย MR · ไม่มีบรรทัดกติกา MR", txt(page, f"{CS} .ui-plan-h").startswith("XAUUSD Short") and "MR · สวน Bias" not in txt(page, f"{CS} .ui-plan-h") and page.locator(f"{CS} [data-mr-line]").count() == 0, txt(page, f"{CS} .ui-plan-h"))
        check(f"{tag} 10 ขนาดกลับตามกฎ F2c (Short ตาม Macro+Trend ▼ → 'ขนาดไม้: เต็ม')", "ขนาดไม้: เต็ม" in txt(page, f'{CS} [data-f2c-row="size"]') and acct(page, "iS")["factor"] == 1)
        set_idea(page, "iS", {"entry": 2390, "sl": 2400})
        js(page, "()=>satV3CondActivate('iS','c2',true)"); page.wait_for_timeout(350)
        i_s = idea(page, "iS")
        check(f"{tag} 10 สลับปกติ → MR: entry/sl ถูกล้างอีกรอบ · TP = 2450", i_s["entry"] is None and i_s["sl"] is None and i_s["tp"] == 2450, json.dumps({k: i_s.get(k) for k in ("entry", "sl", "tp")}))
        # ยกเลิก Activate แล้ว Activate อีกฝั่ง ก็ล้าง (act_side)
        set_idea(page, "iS", {"entry": 2410, "sl": 2390})
        js(page, "()=>satV3CondActivate('iS','c2',false)"); page.wait_for_timeout(250)
        js(page, "()=>satV3CondActivate('iS','c1',true)"); page.wait_for_timeout(300)
        check(f"{tag} 10 ยกเลิก Activate แล้วเลือกข้อทิศตรงข้าม → ล้าง entry/sl", idea(page, "iS")["entry"] is None and idea(page, "iS")["sl"] is None)
        # สลับระหว่างข้อทิศเดียวกัน = ไม่ล้าง
        set_idea(page, "iS", {"entry": 2390, "sl": 2400})
        mk_extra = idea(page, "iS")["conditions"] + [{"id": "c4", "text": "อีกข้อ", "tp_from": None, "tp_to": None, "inval": None, "active": False, "saved": True}]
        set_idea(page, "iS", {"conditions": mk_extra})
        js(page, "()=>satV3CondActivate('iS','c4',true)"); page.wait_for_timeout(300)
        check(f"{tag} 10 ข้อปกติ → ข้อปกติ (ทิศเดียวกัน) ไม่ล้าง entry/sl", idea(page, "iS")["entry"] == 2390 and idea(page, "iS")["sl"] == 2400)

        # ───────── 12 Positions / Journal / ถือนาน ─────────
        reset_ideas(page)
        js(page, """()=>{ const B = getBook('main'); B.trades = []; saveBook('main'); }""")
        d3 = dates_with_biz_days(page, 3); d2 = dates_with_biz_days(page, 2)
        push_trade(page, id="m3", date=d3, mr=True, mr_level=2400, plan_bias="Short", sizeFactor=0.6)
        push_trade(page, id="m2", date=d2, mr=True, mr_level=2400, plan_bias="Short", sizeFactor=0.6, sym="XAUUSD")
        push_trade(page, id="n3", date=d3, bias="Short", entry=2650, sl=2680, tp=2600)
        js(page, "()=>{ switchTab('plan'); setPlanScope('future'); }"); page.wait_for_timeout(300)
        rows = page.evaluate("()=>{ const o={}; document.querySelectorAll('tr[data-pos]').forEach(r=>o[r.dataset.pos]=r.innerText.replace(/\\s+/g,' ')); return o; }")
        cards = page.evaluate("()=>{ const o={}; document.querySelectorAll('.tcard[data-pos]').forEach(r=>o[r.dataset.pos]=r.innerText.replace(/\\s+/g,' ')); return o; }")
        view = rows if w > 900 else cards
        check(f"{tag} 12 Positions ({'แถว' if w > 900 else 'การ์ดมือถือ'}): ไม้ MR มีป้าย 'MR · สวน Bias' ทั้ง 2 ไม้ · ไม้ปกติไม่มี", "MR · สวน Bias" in view.get("m3", "") and "MR · สวน Bias" in view.get("m2", "") and "MR · สวน Bias" not in view.get("n3", ""), json.dumps(view, ensure_ascii=False))
        check(f"{tag} 12 ไม้ MR เปิด 3 วันทำการ → '⚠ MR ถือ 3 วัน (เกิน 2)'", "⚠ MR ถือ 3 วัน (เกิน 2)" in view.get("m3", ""), view.get("m3", ""))
        check(f"{tag} 12 ไม้ MR เปิด 2 วัน → ไม่เตือน · ไม้ปกติ 3 วัน → ไม่เตือน", "⚠ MR" not in view.get("m2", "") and "⚠ MR" not in view.get("n3", ""))
        both = page.evaluate("()=>[document.querySelectorAll('tr[data-pos] [data-mr-tag]').length, document.querySelectorAll('.tcard[data-pos] [data-mr-tag]').length]")
        check(f"{tag} 12 ทั้งแถว (ตาราง) และการ์ดมือถือมีป้าย MR (DOM มีทั้งสองชุด)", both == [2, 2], str(both))
        shot(page, f"7e4-positions-mr-{label}.png")
        shot(page, f"7e4-hold-warn-{label}.png", "tr[data-pos='m3']" if w > 900 else ".tcard[data-pos='m3']")
        # BTCUSD: วันปฏิทิน · เปิดวันศุกร์ → จันทร์ = 3 → เตือน (ใช้ Calc ตรงกับ satMrHoldWarn)
        d_cal = dates_with_biz_days(page, 3, "BTCUSD")
        w_btc = js(page, "(d)=>satMrHoldWarn({mr:true,status:'open',port:'satB',sym:'BTCUSD',openedAt:d})", d_cal)
        w_xau = js(page, "(d)=>satMrHoldWarn({mr:true,status:'open',port:'satB',sym:'XAUUSD',openedAt:d})", d_cal)
        check(f"{tag} 12 BTCUSD นับวันปฏิทิน: เปิด 3 วันปฏิทิน → เตือน 3 · XAUUSD วันที่เดียวกัน (ทำการ ≤ 3) นับตามวันทำการ", w_btc == 3 and (w_xau is None or w_xau <= 3), f"{w_btc} {w_xau}")
        no_hold = js(page, "()=>[satMrHoldWarn({mr:true,status:'open',port:'satB',sym:'XAUUSD'}), satMrHoldWarn({mr:true,status:'closed',port:'satB',sym:'XAUUSD',openedAt:'2020-01-01'}), satMrHoldWarn({status:'open',port:'satB',sym:'XAUUSD',openedAt:'2020-01-01'})]")
        check(f"{tag} 12 ไม่มี openedAt/date → ไม่เตือน · ไม้ปิดแล้ว/ไม่ใช่ MR → ไม่เตือน", no_hold == [None, None, None], str(no_hold))
        no_overflow(page, w, tag)
        # Journal: ไม้ MR ที่ปิดแล้ว
        push_trade(page, id="mc", date=d2, status="closed", exitPrice=2450, exitDate=js(page, "()=>thaiToday()"), mr=True, mr_level=2400, plan_bias="Short", sizeFactor=0.6)
        js(page, "()=>switchTab('journal')"); page.wait_for_timeout(350)
        jt = page.evaluate("()=>document.querySelector('#jTbody') ? document.querySelector('#jTbody').innerText.replace(/\\s+/g,' ') : ''")
        jc = page.evaluate("()=>[...document.querySelectorAll('.tcard')].map(e=>e.innerText.replace(/\\s+/g,' ')).join(' | ')")
        check(f"{tag} 12 Journal (Closed Trades): ไม้ MR มีป้าย 'MR · สวน Bias'", "MR · สวน Bias" in (jt if w > 900 else jc), (jt if w > 900 else jc)[:200])
        check(f"{tag} 12 Journal: ตารางและการ์ดมือถือมีป้ายตรงกัน (DOM)", page.evaluate("()=>[document.querySelectorAll('#jTbody [data-mr-tag]').length>0, document.querySelectorAll('.tcard [data-mr-tag]').length>0]") == [True, True], page.evaluate("()=>[document.querySelectorAll('#jTbody [data-mr-tag]').length, document.querySelectorAll('.tcard [data-mr-tag]').length]"))
        no_overflow(page, w, tag)

        # ───────── 13 แผนปกติเท่าเดิม ─────────
        p5.goto_sat(page); reset_ideas(page)
        js(page, """()=>{ const B = getBook('main'); B.trades = []; saveBook('main'); }""")
        setup_week(page)
        mk(page, "iZ", entry=2650, sl=2680, tp=None, active="c1")
        set_idea(page, "iZ", {"tp": 2380})
        a = acct(page, "iZ")
        e = lot_exp(page, a, 30, 1)
        check(f"{tag} 13 แผนปกติ (Short ตาม Macro+Trend): factor 1 · lot = satLot(risk × 1) = {e} · ไม่มีป้าย/บรรทัด MR · ready", a["factor"] == 1 and a["lot"] == e and not a["mr"] and a["ready"] and page.locator('.ui-plan[data-id="iZ"] [data-mr-tag], .ui-plan[data-id="iZ"] [data-mr-line]').count() == 0, json.dumps({k: a[k] for k in ("factor", "lot", "mr", "ready")}))
        js(page, "()=>satV3SaveSlot('iZ','main')"); page.wait_for_timeout(350)
        t = js(page, "()=>{ const a=((sat7dIdea('iZ')||{}).accts||{}).main||{}; return a.trade_id ? getBook('main').trades.find(x=>x.id===a.trade_id) : null; }")
        check(f"{tag} 13 แผนปกติบันทึก: bias Short · sizeFactor null · ไม่มี field mr/mr_level/plan_bias เลย", t and t["bias"] == "Short" and t["sizeFactor"] is None and not any(k in t for k in ("mr", "mr_level", "plan_bias")), json.dumps({k: (t or {}).get(k) for k in ("bias", "sizeFactor", "mr")}))

        # ───────── 14 มือถือ ─────────
        p5.goto_sat(page); reset_ideas(page); setup_week(page)
        mk(page, "iF", entry=2410, sl=2390, tp=2450)
        js(page, "()=>{ satV3Open.add('iF'); satV3Render(); }"); page.wait_for_timeout(300)
        no_overflow(page, w, tag)
        ov = page.evaluate("()=>{ const e=document.querySelector('.ui-plan[data-id=\"iF\"]'); return e.scrollWidth <= e.clientWidth + 1; }")
        check(f"{tag} 14 การ์ด MR ไม่ล้นในกรอบการ์ดเอง", ov)
    finally:
        check(f"{tag} console: zero error-level messages", not ce, "; ".join(ce[:3]))
        check(f"{tag} console: zero uncaught page errors", not pe, "; ".join(pe[:3]))
        browser.close()


def main():
    with sync_playwright() as pw:
        ui_tests(pw, 1440, 900, "1440px")
        ui_tests(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 27 / 7E-4 MR) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
