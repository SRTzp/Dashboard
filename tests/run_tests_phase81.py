#!/usr/bin/env python3
"""LN2 — หัวกล่อง Strategy แบบ Lean (เลือกบัญชี · กล่องความเสี่ยงเดียว) · ฟอร์ม Main/Tactical · Flat ไม่นับสลับ Bias · เทส 81
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย · fixture 2 บัญชีตัวเลขต่างกัน (main Sat $45,000 · fam Sat $30,000)
ภาพ tests/screenshots/ln2-{header-main,header-family,header-alert,form-tactical}-{1440,390}.png
รัน: python3 run_tests_phase81.py"""
import json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE   # ชุดนี้ต้องการค่าเริ่มจริง (Lean)
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase77 as P77
import run_tests_phase78 as P78

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, overflow = P54.txt, P54.overflow
idea, put, note, trades, save, cnt, setcfg = P77.idea, P78.put, P78.note, P78.trades, P78.save, P78.cnt, P78.setcfg
sat_t = P78.sat_t


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(700)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def fixture(mode="diff"):
    def m(doc):
        base_ = P77.fixture()
        base_(doc)
        doc["books"]["fam"]["settings"]["capital"]["satB"] = 30000
        doc["books"]["fam"]["settings"]["ddState"]["sat"] = P37.ds0(30000)
    return m


def launch(pw, w, h, bias="Long"):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture())
    dl = dialogs   # รายการข้อความ dialog ที่แอปเด้ง (launch ของ P54 กด OK ให้)
    P51.fresh(page, None)
    js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", ["XAUUSD", "BTCUSD"])
    P11.wk(page, "XAUUSD", bias, "up" if bias == "Long" else "down")
    P37.go_sat(page)
    page.evaluate("()=>{ try{ localStorage.removeItem('ln2_acc'); }catch(e){} }")
    return browser, page, ce, pe, dl


def hd(page, acc=None):
    """LN3fix3c — หัวกล่องมีแถวต่อบัญชี (ไม่มีสวิตช์) · acc = แถวของบัญชีนั้น (ไม่ระบุ = แถวแรก) · alerts/btns อ่านจากทั้งกล่อง"""
    return js(page, """(acc)=>{ const H = document.querySelector('[data-ln2-hd]'); if(!H) return null; const h = acc ? H.querySelector('[data-ln2-row="'+acc+'"]') : H.querySelector('[data-ln2-row]'); if(!h) return null; const g = s => { const e = h.querySelector(s); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; }; const gd = s => { const e = H.querySelector('[data-ln2-detacc="'+h.dataset.ln2Row+'"] '+s); return e ? e.textContent.replace(/\\s+/g,' ').trim() : null; };
      return {acc: h.dataset.ln2Row, rows: H.querySelectorAll('[data-ln2-row]').length, btns: [...H.querySelectorAll('[data-ln2-acc]')].map(b=>[b.dataset.ln2Acc, b.classList.contains('on')]), boxes: H.querySelectorAll('[data-ln2-box]').length,
        used: g('[data-ln2-used]'), cap: g('[data-ln2-cap]'), left: g('[data-ln2-left]'), main: g('[data-ln2-main]'), tac: g('[data-ln2-tac]'), cs: gd('[data-ln2-cs]'), cst: gd('[data-ln2-cst]'),
        ddl: g('[data-ln2-ddl]'), alerts: [...H.querySelectorAll('[data-ln2-alert]')].map(a=>a.innerText.trim()), text: H.innerText}; }""", acc)


def expect(page, acct):
    return js(page, """(a)=>{ const fx = satV2Money(a).fx, R = satV2Risk(a), CP = satV2Caps(a), u = x=>satV2Usd(x, fx);
      return {used: u(R.sat), cap: u(CP.sat), left: u(Math.max(0, CP.sat - R.sat)), main: u(R.main), tac: u(R.tac), cs: u(R.core + R.sat), cst: u(CP.total)}; }""", acct)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 + 2 หัวกล่อง Lean + ตัวเลข
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        put(page, [sat_t("m1", "open", entry=4180, sl=4117, qty=0.10), sat_t("t1", "open", entry=4180, sl=4160, qty=0.10, sleeve="tactical")], "main")
        put(page, [sat_t("f1", "open", entry=4180, sl=4117, qty=0.05)], "fam")
        h0 = hd(page)
        check(f"{tag} 1 (LN3fix3c) ไม่มีสวิตช์เลือกบัญชี · กล่องเดียว · 2 แถว (บัญชีหลัก · Family) เห็นพร้อมกัน", h0 and h0["btns"] == [] and h0["rows"] == 2 and h0["boxes"] == 1 and cnt(page, "[data-ln2-accsw]") == 0, h0 and [h0["btns"], h0["rows"]])
        bad = js(page, """()=>{ const s = document.getElementById('satV3Sum'); const t = document.querySelector('[data-ln2-hd]').innerText; return {pv2: s.querySelectorAll('[data-pv2-header],[data-pv2-hd],[data-sat-meta],.sumMeta,[data-pv2-brake]').length, heat: /heat/i.test(t), rpt: /RPT/.test(t), nnew: t.includes('ไม้ใหม่'), brake: t.includes('เบรก'), acc: s.querySelectorAll('[data-ln1-acc]').length}; }""")
        check(f"{tag} 1 ไม่มี heat / RPT / ไม้ใหม่ / บรรทัดเบรก / การ์ด Risk ซ้ำ ในหัวกล่อง", bad == {"pv2": 0, "heat": False, "rpt": False, "nnew": False, "brake": False, "acc": 0}, bad)
        check(f"{tag} 1 หัวเล็ก 'Risk Sat (ถ้าโดน SL ทุกไม้)' · ตัวใหญ่ $ใช้ / $เพดาน · เหลือ", ("Risk Sat (ถ้าโดน SL ทุกไม้)" in h0["text"] or (w >= 1000 and h0["text"].count("Risk Sat") == 2)) and h0["used"] and h0["cap"] and h0["left"], h0["text"][:200])
        e0 = expect(page, "main")
        check(f"{tag} 2 ตัวเลข บัญชีหลัก = satV2Risk/satV2Caps เดิม (ใช้ · เพดาน · เหลือ · Main · Tactical · Core+Sat)", all(h0[k] == e0[k] for k in ("used", "cap", "left", "main", "tac", "cs", "cst")) and h0["used"] != "$0", [h0, e0])
        check(f"{tag} 2 บรรทัดเล็ก 'DD x/20%' (LN3) · 'Core+Sat $a / $b' อยู่ในพับรายละเอียด", h0["ddl"].startswith("DD") and "/20%" in h0["ddl"] and h0["cs"] and h0["cst"], [h0["ddl"], h0["cs"]])
        shot(page, f"ln2-header-main-{sfx}.png", "#satV3Sum")
        h1 = hd(page, "fam"); e1 = expect(page, "fam")
        check(f"{tag} 1 (LN3fix3c) แถว Family แสดงพร้อมแถวบัญชีหลัก (เพดานต่างกัน) · กล่องเดียวเสมอ", h1["acc"] == "fam" and h1["rows"] == 2 and h1["boxes"] == 1 and h1["cap"] != h0["cap"] and h1["used"] != h0["used"], [h1["cap"], h0["cap"], h1["used"], h0["used"]])
        check(f"{tag} 2 ตัวเลข Family = satV2Risk/satV2Caps เดิม", all(h1[k] == e1[k] for k in ("used", "cap", "left", "main", "tac", "cs", "cst")), [h1, e1])
        shot(page, f"ln2-header-family-{sfx}.png", "#satV3Sum")
        js(page, "()=>{ ln2Mem = null; try{ localStorage.removeItem('ln2_acc'); }catch(e){} satV3Render({force:true}); }"); page.wait_for_timeout(400)
        ls = js(page, "()=>localStorage.getItem('ln2_acc')")
        check(f"{tag} 1 (LN3fix3c) ไม่มีการจำบัญชีอีกแล้ว: วาดใหม่ยังเห็นทั้ง 2 แถว · localStorage ไม่ถูกเขียน", ls is None and hd(page)["rows"] == 2, ls)
        js(page, "()=>{ ln2Mem = null; localStorage.setItem('ln2_acc','ghost'); satV3Render({force:true}); }"); page.wait_for_timeout(300)
        check(f"{tag} 1 ค่าเก่าที่จำไว้ไม่มีอยู่จริง → ไม่มีผล · ยัง 2 แถว แถวแรก = บัญชีแรก", hd(page)["acc"] == "main" and hd(page)["rows"] == 2)
        # พับรายละเอียด
        det = js(page, "()=>{ const d = document.querySelector('[data-ln2-det]'); d.open = true; return d.innerText.replace(/\\s+/g,' '); }")
        check(f"{tag} 1 พับ 'รายละเอียดและกฎบัญชี': เงิน Sat · Main/Tactical · เพดาน Sat/ต่อสินค้า/Core+Sat · วิธีนับ", all(k in det for k in ("เงิน Sat", "Main 70%", "Tactical 30%", "เพดาน", "ต่อสินค้า", "Core+Sat", "Entry ถึง Stop ปัจจุบัน", "รวมแผนรอเข้า", "Stop เลยทุน = 0")), det[:300])
        # บัญชีเดียว
        js(page, "()=>{ acctList.find(a=>a.id==='fam').ports = ['core']; ln2Mem = null; satV3Render({force:true}); }"); page.wait_for_timeout(400)
        h2 = hd(page)
        check(f"{tag} 1 มีบัญชี Sat เดียว → 1 แถว ไม่มีสวิตช์ · ยังมีกล่องความเสี่ยง", h2 and h2["btns"] == [] and h2["boxes"] == 1 and h2["rows"] == 1 and cnt(page, "[data-ln2-accsw]") == 0, h2 and h2["btns"])
    finally: b.close()

    # ── 3 แถบเตือน
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        h0 = hd(page)
        check(f"{tag} 3 ไม่มีเงื่อนไข → ไม่แสดงแถบเตือน", h0["alerts"] == [] and cnt(page, "[data-ln2-alert]") == 0, h0["alerts"])
        def tl(i, d, pnl, k="x"): return sat_t(f"{k}{i}", status="closed", sleeve="tactical", entry=4180, sl=4160, qty=0.10, exitPrice=4180 + pnl / 10.0, exitDate=d)
        put(page, [tl(i, f"2026-09-{20 + i}", -50) for i in range(1, 6)], "main")
        h1 = hd(page)
        check(f"{tag} 3 แพ้ติด 5 ไม้ → '⚠ พัก Tactical: แพ้ติด 5 ไม้ · Main ยังเปิดได้'", h1["alerts"] == ["⚠ พัก Tactical: แพ้ติด 5 ไม้ · Main ยังเปิดได้"], h1["alerts"])
        shot(page, f"ln2-header-alert-{sfx}.png", "#satV3Sum")
        loss = sat_t("y1", status="closed", entry=4180, sl=4000, qty=1, exitPrice=4099, exitDate="2026-09-28", sleeve="main")
        put(page, [loss], "main"); setcfg(page, maxDd=15)
        h2 = hd(page)
        check(f"{tag} 3 DD Sat ถึงเกณฑ์ (18% ≥ 15%) → '⚠ หยุดเปิดไม้ใหม่: DD Sat …%' · ไม่มีแถบ Tactical", len(h2["alerts"]) == 1 and h2["alerts"][0].startswith("⚠ หยุดเปิดไม้ใหม่: DD Sat 18") and "/15%" in h2["ddl"], [h2["alerts"], h2["ddl"]])
        setcfg(page, maxDd=20, orSat=1.0)
        js(page, "()=>{ const s = getBook('main').settings; s.ddState.sat = %s; saveBook('main'); render(); }" % json.dumps(P37.ds0(45000))); page.wait_for_timeout(300)
        put(page, [sat_t("o1", "open", entry=4180, sl=4117, qty=0.30)], "main")
        h3 = hd(page)
        check(f"{tag} 3 ใกล้เพดาน (ใช้ ≥ 80% ของเพดาน Sat) → '⚠ ใกล้เพดาน: เหลือ $x' (x = ช่อง 'เหลือ')", len(h3["alerts"]) == 1 and h3["alerts"][0] == "⚠ ใกล้เพดาน: เหลือ " + h3["left"], [h3["alerts"], h3["left"], h3["used"], h3["cap"]])
    finally: b.close()

    # ── 4 ฟอร์ม
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iid)
        fm = js(page, """()=>{ const e = document.querySelector('[data-ln2-form]'); return e ? {k: e.dataset.ln2Form, t: e.innerText.replace(/\\s+/g,' ').trim()} : null; }""")
        exp = js(page, "()=>{ const M = satV2Money('main'); return [M.cfg.rptMain, satV2Usd(M.mainTHB*M.cfg.rptMain/100, M.fx), sat7dAcctBase('main').nNew, sat7dAcctBase('main').newMax]; }")
        expf = js(page, "()=>{ const M = satV2Money('fam'); return satV2Usd(M.mainTHB*M.cfg.rptMain/100, M.fx); }")
        nmM, nmF = js(page, "()=>[acctList.find(a=>a.id==='main').name, acctList.find(a=>a.id==='fam').name]")
        want = (f"▲ Up · Macro — · {exp[0]}% · {nmM} {exp[1]} · {nmF} {expf} · ไม้ใหม่ {exp[2]}/{exp[3]}" if w > 480 else f"▲ Up · Macro — · {exp[0]}% · {exp[1]} · {expf} · ใหม่ {exp[2]}/{exp[3]}")   # PF1 — ทิศ = Trend ของแผน · มือถือซ่อนชื่อบัญชี (A4)   # LN3 + LN3fix3c (ทุกบัญชี)
        check(f"{tag} 4 Main: '{want}' (LN3fix3c: $ ต่อไม้ของทุกบัญชี) · ไม่แสดงส่วน Tactical", fm and fm["k"] == "main" and fm["t"] == want and cnt(page, '[data-ln2-form="tactical"]') == 0, [fm, want])
        fm2 = js(page, "()=>document.querySelector('[data-ln2-form] [data-ln2-deal-acc=\"fam\"]').innerText")
        check(f"{tag} 4 (LN3fix3c) เสี่ยงต่อดีลของ Family อยู่ในบรรทัดเดียวกับบัญชีหลัก (เปลี่ยนตามบัญชี)", fm2 == expf and fm2 != exp[1], [fm2, expf, exp[1]])
        page.locator("[data-sleeve=tactical]").click(); page.wait_for_timeout(500)
        ft = js(page, """()=>{ const e = document.querySelector('[data-ln2-form]'); return e ? {k: e.dataset.ln2Form, t: e.innerText.replace(/\\s+/g,' ').trim()} : null; }""")
        te = js(page, "()=>{ const M = satV2Money('main'); return satV2Usd(M.tacTHB*M.cfg.rptTac/100, M.fx); }")
        tf = js(page, "()=>{ const M = satV2Money('fam'); return satV2Usd(M.tacTHB*M.cfg.rptTac/100, M.fx); }")
        check(f"{tag} 4 Tactical: '▲ · 2% · OUN $x · FAM $y · ● Loss 0/5 · DD 0/10%' (LN3 + LN3fix3c) · ไม่แสดงไม้ใหม่", ft and ft["k"] == "tactical" and ft["t"] == (f"▲ Up · 2% · {nmM} {te} · {nmF} {tf} · ● Loss 0/5 · DD 0/10%" if w > 480 else f"▲ Up · 2% · {te} · {tf} · ● Loss 0/5 · DD 0/10%") and "ไม้ใหม่" not in ft["t"], ft)
        shot(page, f"ln2-form-tactical-{sfx}.png", ".ui-plan")
        def tl(i, d, pnl, k="x"): return sat_t(f"{k}{i}", status="closed", sleeve="tactical", entry=4180, sl=4160, qty=0.10, exitPrice=4180 + pnl / 10.0, exitDate=d)
        put(page, [tl(i, f"2026-09-{20 + i}", -50) for i in range(1, 6)], "main")
        ft2 = js(page, "()=>{ const e = document.querySelector('[data-ln2-pause]'); return e ? e.innerText.trim() : null; }")
        why2 = js(page, "()=>document.querySelector('[data-ln3-pause-why]').innerText.trim()")
        check(f"{tag} 4 ถึงเกณฑ์ → '⛔ พัก Tactical' (สีแดง) + 'พัก Tactical · แพ้ติด 5 ไม้ → ชนะ 1 ไม้ หรือขาดทุนลดต่ำกว่า 10% แล้วเทรดได้เอง' (LN3)", ft2 == f"⛔ พัก Tactical · {nmM}" and why2 == "พัก Tactical · แพ้ติด 5 ไม้ → ชนะ 1 ไม้ หรือขาดทุนลดต่ำกว่า 10% แล้วเทรดได้เอง" and js(page, "()=>document.querySelector('[data-ln2-pause]').classList.contains('stop')"), [ft2, why2])
        # ข้อความบล็อกตอนบันทึก ใช้คำใหม่
        blk = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); return satV3PlanAcctCalc(x,'main').blocks; }", [iid])
        body = js(page, "()=>document.querySelector('.ui-plan').innerText")
        check(f"{tag} 4 ข้อความบล็อกตอนบันทึกใช้คำใหม่ 'พัก Tactical …' · ไม่มีคำว่า 'เบรก' ทั้งในฟอร์มและหัวกล่อง", any(m.startswith("พัก Tactical") for m in blk) and "เบรก" not in body and "เบรก" not in js(page, "()=>document.getElementById('satV3Sum').innerText"), [blk, "เบรก" in body])
        # DD Sat พักในโหมด Lean ก็ไม่ใช้คำว่าเบรก
        put(page, [sat_t("y1", status="closed", entry=4180, sl=4000, qty=1, exitPrice=4099, exitDate="2026-09-28", sleeve="main")], "main"); setcfg(page, maxDd=15)
        body2 = js(page, "()=>document.querySelector('.ui-plan').innerText + ' ' + document.getElementById('satV3Sum').innerText")
        check(f"{tag} 4 DD Sat พัก → ข้อความในฟอร์ม 'หยุดเปิดไม้ใหม่: DD Sat …' ไม่มีคำว่า 'เบรก'", "หยุดเปิดไม้ใหม่: DD Sat" in body2 and "เบรก" not in body2, body2[:300])
        # โหมดเดิมไม่เปลี่ยนคำ
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(500)
        old = js(page, "()=>{ const x = satIdeasList.find(y=>y.id===%s); return satV3PlanAcctCalc(x,'main').blocks; }" % json.dumps(iid))
        check(f"{tag} 4 โหมดแบบเดิม: ข้อความบล็อกยังเป็น 'เบรก Tactical: …' เหมือนเดิม", any(m.startswith("เบรก Tactical:") for m in old) or cnt(page, "[data-pv2-header]") == 1, old)
    finally: b.close()

    # ── 5 heat ยังบล็อก + ผลคำนวณเท่า LN1 (Lean = เดิม)
    res = {}
    for m in ("lean", "legacy"):
        b, page, ce, pe, dl = launch(pw, w, h, bias="Neutral")
        try:
            js(page, "(m)=>ln1SetMode(m)", m); page.wait_for_timeout(400)
            setcfg(page, orSat=10, orAsset=10, orTot=20)
            i1 = idea(page, sleeve="main", entry=4180, sl=4117); note(page, i1)
            i2 = idea(page, sleeve="tactical", entry=4240, sl=4260); js(page, "([i])=>satV2SetDir(i,'Short')", [i2]); page.wait_for_timeout(400); note(page, i2)
            calc = lambda i: js(page, """(i)=>{ const x = satIdeasList.find(y=>y.id===i); return ['main','fam'].map(a=>{ const c = satV3PlanAcctCalc(x, a); return {lot:c.lot, ready:c.ready, blocks:c.blocks, limit:c.v2.limit, risk:c.v2.actualTHB}; }); }""", i)
            before = [calc(i1), calc(i2)]
            put(page, [sat_t("h1", "open", entry=4180, sl=4117, qty=0.50)], "main")   # Open Risk $3,150 > heat 6% ($2,700) แต่ < เพดาน Sat 10% ($15,000)
            st = js(page, "()=>{ const b = sat7dAcctBase('main'); const R = satV2Risk('main'), CP = satV2Caps('main'); return {heat: b.heatPct, heatMax: b.heatMax, under: R.sat < CP.sat}; }")
            after = [calc(i1), calc(i2)]
            res[m] = {"before": before, "after": after, "st": st}
        finally: b.close()
    L, O = res["lean"], res["legacy"]
    check(f"{tag} 5 heat เกิน (Open Risk ไม่เกินเพดาน) → ยังบล็อกบัญชีหลัก (ready=false) · Family ที่ heat ปกติยัง ready", L["st"]["heat"] > L["st"]["heatMax"] and L["st"]["under"] and not L["after"][0][0]["ready"] and L["after"][0][1]["ready"], [L["st"], L["after"][0]])
    check(f"{tag} 5 lot / ตัวจำกัด / บล็อก / ready ของแผน (ก่อน-หลังมีไม้ค้าง) Lean = แบบเดิม ทุกตัว", L["before"] == O["before"] and L["after"] == O["after"], [L["after"][0], O["after"][0]])

    # ── 6 Flat ไม่นับสลับ Bias — PF1 ถอดทั้งชุดควบคุม Trend/Flat/สลับ: PF3 ตรวจว่าของเดิมหายจริง · ไม่มีอะไรถูกเขียน/ถามยืนยัน
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        wk6 = js(page, "()=>JSON.parse(JSON.stringify(satwWeek(wpWeekKey(),'XAUUSD')||{}))")
        q6 = lambda sel: cnt(page, '.ln1-tile[data-key=XAUUSD] ' + sel)
        ta6 = q6("textarea")
        flips0 = (wk6.get("flips") or 0) == 0 and "trend_log" not in wk6
        check(f"{tag} 6 PF3 ไม่มีช่องติ๊ก Flat · ไม่มีปุ่ม Up/Down ให้สลับ → flips ยัง 0 · ไม่มี trend_log", q6("[data-ln1-flat]") == 0 and q6("[data-ln1-trend]") == 0 and flips0, wk6)
        check(f"{tag} 6 PF3 ไม่มีกล่องเหตุผลสลับ Trend (มี textarea เดียว = ความเห็นเรา)", ta6 == 1 and q6("textarea[data-ln3-opinion]") == 1, ta6)
        check(f"{tag} 6 PF3 ไม่มีสถานะ Flat ที่ติ๊กอยู่ให้ 'กดทิศเดิมซ้ำ' · flips ไม่ขยับ", q6("[data-ln1-flat]") == 0 and (wk6.get("flips") or 0) == 0, wk6)
        check(f"{tag} 6 PF3 ไม่มี confirm/dialog ใด ๆ ตอนเปิดหน้า Strategy (ไม่มีการสลับให้ถาม) · ไม่มี trend_log", dl == [] and "trend_log" not in wk6, dl)
        check(f"{tag} 6 PF3 ไม่มีทางเปลี่ยนทิศตอน Flat จึงไม่มี confirm · tile มีแค่ + แผน / Clear Note / เอาออก", dl == [] and sorted(js(page, "()=>[...document.querySelectorAll('.ln1-tile[data-key=XAUUSD] button')].map(b=>b.innerText.trim())")) == sorted(["☆", "+ แผน", "Clear Note", "เอาออกจากสัปดาห์นี้", "Not trading this week"]), js(page, "()=>[...document.querySelectorAll('.ln1-tile[data-key=XAUUSD] button')].map(b=>b.innerText.trim())"))
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(500)
        check(f"{tag} 6 PF3 โหมดเดิม: ไม่มีปุ่ม Neutral/Bias (ไม่มีอะไรให้นับเป็นสลับ)", cnt(page, "[data-bias-neutral]") == 0 and cnt(page, ".ui-bias-btn") == 0)
    finally: b.close()

    # ── 7 โหมดเดิม: หัวกล่องเหมือน LN1/PV2c
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(500)
        pv = js(page, """()=>({hd: document.querySelectorAll('[data-pv2-header] [data-pv2-hd]').length, meter: document.querySelectorAll('[data-pv2-meter]').length, brake: document.querySelectorAll('[data-pv2-brake]').length,
          meta: document.querySelectorAll('[data-sat-meta] .sumMr').length, heat: /heat/.test(document.querySelector('[data-sat-meta]').innerText), rpt: document.querySelector('[data-sat-meta]').innerText.includes('RPT'), ln2: document.querySelectorAll('[data-ln2-hd]').length, fl: document.querySelectorAll('[data-ln2-form]').length})""")
        check(f"{tag} 7 โหมดแบบเดิม: แถบบัญชี 2 บรรทัด (heat · RPT) + การ์ด Risk 2 บัญชี + บรรทัดเบรก · ไม่มีหัวกล่อง LN2", pv == {"hd": 2, "meter": 4, "brake": 2, "meta": 2, "heat": True, "rpt": True, "ln2": 0, "fl": 0}, pv)
        iid = idea(page, sleeve="tactical", entry=4180, sl=4160)
        check(f"{tag} 7 ฟอร์มโหมดเดิมไม่มีบรรทัด LN2", cnt(page, "[data-ln2-form]") == 0)
    finally: b.close()

    # ── 8 ความสูง 390 + ล้น + console
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        put(page, [sat_t("m1", "open", entry=4180, sl=4117, qty=0.10)], "main")
        hh = js(page, """()=>{ const top = document.querySelector('#satV3Sum').getBoundingClientRect().top; const c = document.querySelector('#satV3Sum .ln1-tile, #satV3Sum .waBar'); const sel = document.querySelector('.ln1-tiles, [data-wa-bar]'); const t = sel ? sel.getBoundingClientRect().top : null;
          return {h: t == null ? null : Math.round(t - top)}; }""")
        if w <= 430: check(f"{tag} 8 หัวกล่อง (ถึงก่อนการ์ดสินทรัพย์แรก) สูงไม่เกิน 360px", hh["h"] is not None and hh["h"] <= 560, hh)   # WM1: แผง Weekly Impact เพิ่มเหนือการ์ด (360 → 560)
        else: check(f"{tag} 8 หัวกล่อง (ถึงก่อนการ์ดสินทรัพย์แรก) สูงไม่เกิน 360px", hh["h"] is not None and hh["h"] <= 560, hh)   # WM1: แผง Weekly Impact เพิ่มเหนือการ์ด (360 → 560)
        js(page, "()=>{ document.querySelector('[data-ln2-det]').open = true; }"); page.wait_for_timeout(200)
        iid = idea(page, sleeve="tactical", entry=4180, sl=4160)
        check(f"{tag} 8 {label} ไม่ล้นแนวนอน (กางรายละเอียด) · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
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
