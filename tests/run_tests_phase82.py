#!/usr/bin/env python3
"""LN3 — แท็บแผน (Sat) แบบ Lean รอบเดียว: หัวกล่อง · Zone ▲/▼ (+ย้ายค่าเดิม) · สลับ Trend ต้องมีเหตุผล · แถวแผน 2 บรรทัด · ฟอร์ม (Zone check · สวน Macro · สถานะ) · ลูกศรมีสี · เทส 82
mock Firestore · Chromium 1440 + 390 + 300 · นาฬิกาปลอม 2026-10-01 ไทย · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-plan-{tile,rows,form-main,form-tactical}-{1440,390}.png
รัน: python3 run_tests_phase82.py"""
from pf2_retire import retired_wm1 as retired3
import json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase69 as P69
import run_tests_phase76 as P76
import run_tests_phase77 as P77
import run_tests_phase78 as P78

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, overflow = P54.txt, P54.overflow
idea, put, note, trades, save, cnt, setcfg, sat_t = P77.idea, P78.put, P78.note, P78.trades, P78.save, P78.cnt, P78.setcfg, P78.sat_t


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(500)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def fixture(against=1.0):
    def m(doc):
        P77.fixture()(doc)
        for a in ("main", "fam"):
            doc["books"][a]["settings"]["satRisk"] = {"newMax": 5, "macroAgainst": against}
        doc["books"]["fam"]["settings"]["capital"]["satB"] = 30000
        doc["books"]["fam"]["settings"]["ddState"]["sat"] = P37.ds0(30000)
    return m


def launch(pw, w, h, bias="Long", pb=False, against=1.0):
    browser, context, page, ce, pe, dl = P54.launch(pw, w, h, fixture(against))
    P51.fresh(page, None)
    if pb: P11.seed_pb(page, [P69.PB])
    js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", ["XAUUSD", "BTCUSD"])
    P11.wk(page, "XAUUSD", bias, "up" if bias == "Long" else "down")
    P37.go_sat(page)
    page.evaluate("()=>{ try{ localStorage.removeItem('ln2_acc'); }catch(e){} }")
    return browser, page, ce, pe, dl


def wkdoc(page, asset="XAUUSD"):
    return js(page, "(a)=>JSON.parse(JSON.stringify(satwWeek(wpWeekKey(),a)||{}))", asset)


def color(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? getComputedStyle(e).color : null; }", sel)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    T = '.ln1-tile[data-key="XAUUSD"]'

    # ── 1 หัวกล่อง
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        put(page, [sat_t("m1", "open", entry=4180, sl=4117, qty=0.10)], "main")
        t = js(page, """()=>{ const s = document.getElementById('satV3Sum'); const bx = s.querySelector('[data-ln2-box]');
          return {title: s.querySelector('.sumT').innerText.trim(), wk: s.querySelector('#satV3WeekSel').selectedOptions[0].innerText, box: bx.innerText.replace(/\\s+/g,' ').trim(), heat: /heat|RPT/.test(bx.innerText)}; }""")
        check(f"{tag} 1 หัวกล่อง: ชื่อ 'Strategy' (ไม่มีคำว่า 'สัปดาห์นี้') · ช่วงสัปดาห์ในตัวเลือก", t["title"] == "Strategy" and "สัปดาห์นี้" not in t["wk"] and "ต.ค." in t["wk"], t)
        import re
        check(f"{tag} 1 'Risk Sat (ถ้าโดน SL ทุกไม้)' · $ใช้/$เพดาน · เหลือ · 'Main $x · Tactical $y · DD a/b%'",
              ("Risk Sat (ถ้าโดน SL ทุกไม้)" in t["box"] or w >= 1000) and re.search(r"Main \$[\d,]+ · Tac(?:tical)? \$[\d,]+\s+DD [\d.]+/\d+%", t["box"]) and not t["heat"], t["box"])   # LN3fix3c: แถวต่อบัญชี · Mac ไม่มีหัวรวม (ชื่อ "● OUN · Risk Sat" อยู่ในแต่ละกล่อง)
        check(f"{tag} 1 Core+Sat ย้ายเข้าพับ 'รายละเอียดและกฎบัญชี' ยังอยู่ครบ", js(page, "()=>{ const d = document.querySelector('[data-ln2-det]'); d.open = true; const t = d.innerText; return t.includes('Core+Sat') && t.includes('เพดาน') && t.includes('Stop เลยทุน = 0'); }"))
    finally: b.close()

    # ── 2-4 Zone ▲/▼ · Shift · สลับ Trend ต้องมีเหตุผล — PF1 ถอดทั้งชุด: PF3 ตรวจว่าของเดิมหายจริง + ข้อมูลเก่าใน DB ไม่ถูกแตะ (ตรวจฟอร์มใหม่ใน phase98)
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        TI = js(page, "(T)=>{ const t=document.querySelector(T); return {txt: t.innerText.replace(/\\s+/g,' '), inputs: t.querySelectorAll('input').length, ta: t.querySelectorAll('textarea').length}; }", T)
        wk2 = wkdoc(page)
        fn2 = js(page, "()=>({zone: typeof satwSetZone, zbp: typeof satwSetZoneBp, trend: typeof ln1Trend, ask: typeof ln3Ask, log: typeof ln3fLogToggle, zset: typeof ln3ZoneSet})")
        check(f"{tag} 3 PF3 ค่าเดิม support/resistance ไม่ถูกย้ายเป็น Zone ▲/▼ (ไม่มี zone_up / zone_dn ในเอกสาร)", "zone_up" not in wk2 and "zone_dn" not in wk2 and "Zone" not in TI["txt"], wk2)
        check(f"{tag} 3 PF3 ไม่มีช่อง Zone ในการ์ด (ไม่มี input ในการ์ดเลย)", TI["inputs"] == 0, TI)
        check(f"{tag} 2 PF3 ฟังก์ชันเขียน Zone (satwSetZone / satwSetZoneBp / ln3ZoneSet) ถอดแล้ว — แก้ช่องไม่ได้จึงไม่มี zone_up/zone_dn ถูกเขียน", fn2["zone"] == "undefined" and fn2["zbp"] == "undefined" and fn2["zset"] == "undefined", fn2)
        check(f"{tag} 3 PF3 support / resistance เดิมยังอยู่ครบในเอกสาร (เก็บข้อมูลเก่า ไม่ลบ)", wk2.get("support") == [2400] and wk2.get("resistance") == [2520], wk2)
        check(f"{tag} 2 PF3 ไม่มีช่อง Trend Shift ในแถว · invalidation เดิม (2300) ไม่ถูกแตะ", "Trend Shift" not in TI["txt"] and TI["inputs"] == 0 and wk2.get("invalidation") == 2300, wk2)
        check(f"{tag} 4 PF3 ไม่มีปุ่ม Down/Up ให้กด → ไม่มีกล่อง 'สลับเป็น … เพราะ?' (ln1Trend / ln3Ask ถอดแล้ว)", fn2["trend"] == "undefined" and fn2["ask"] == "undefined" and "เพราะ" not in TI["txt"], fn2)
        check(f"{tag} 4 PF3 ไม่มีช่องเหตุผลสลับ: การ์ดมี textarea เดียว = ความเห็นเรา", TI["ta"] == 1 and cnt(page, T + " textarea[data-ln3-opinion]") == 1, TI)
        check(f"{tag} 4 PF3 ปุ่มในการ์ดมีแค่ + แผน · Clear Note · เอาออกจากสัปดาห์นี้ (ไม่มีปุ่มสลับ)", sorted(js(page, "(T)=>[...document.querySelectorAll(T+' button')].map(b=>b.innerText.trim())", T)) == sorted(["☆", "+ แผน", "Clear Note", "เอาออกจากสัปดาห์นี้", "Not trading this week"]))
        check(f"{tag} 4 PF3 ไม่มี trend_log ในเอกสาร Strategy (ไม่มีการสลับให้บันทึก)", "trend_log" not in wk2, wk2)
        check(f"{tag} 4 PF3 flips ยัง 0 (ไม่มีทางกดสลับ/ยกเลิก)", (wk2.get("flips") or 0) == 0, wk2)
        check(f"{tag} 4 PF3 ไม่มี confirm/dialog ใด ๆ (ไม่มีการสลับให้ถามยืนยัน) · ไม่มี trend_log", dl == [] and "trend_log" not in wk2, dl)
        check(f"{tag} 4 PF3 ไม่มี Flat ในการ์ด (ไม่ถามเหตุผล ไม่นับ log)", cnt(page, T + " [data-ln1-flat]") == 0 and "Flat" not in TI["txt"], TI["txt"][:160])
        check(f"{tag} 4 PF3 ไม่มีลิงก์ 'ประวัติสลับ Trend' (ln3fLogToggle ถอดแล้ว · ไม่มีข้อความประวัติในการ์ด)", fn2["log"] == "undefined" and "ประวัติสลับ" not in TI["txt"], fn2)
    finally: b.close()

    # ── 5 การ์ดสินทรัพย์ + แถวแผน 2 บรรทัด
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        js(page, "(c)=>satwWrite('XAUUSD',{chart:c})", P76.CHART); page.wait_for_timeout(500)
        iid = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iid)
        row = js(page, "(i)=>{ const r = document.querySelector('[data-ln3-row=\"'+i+'\"]'); return r ? {t: r.innerText.replace(/\\s+/g,' ').trim(), st: r.dataset.ln3State} : null; }", iid)
        check(f"{tag} 5 ร่าง = แถวบรรทัดเดียว 'XAUUSD Main ▲ 4,180 / 4,117 ร่าง ›' (ฟอร์มกางหลังกด + แผน)", row and row["st"] == "draft" and row["t"].startswith("XAUUSD Main ▲ Up Entry 4,180 · SL 4,117") and "ร่าง" in row["t"], row)   # LN3fix §2.1 — แถวแผนกำกับ Entry / SL
        tile = js(page, "()=>{ const t = document.querySelector('%s'); return {tv: !!t.querySelector('[data-ln1-tv]'), tvTxt: (t.querySelector('[data-ln1-tv]')||{}).innerText, img: !!t.querySelector('.vwImg img'), pos: t.querySelectorAll('.pv2tile,[data-pv2-pos],[data-pv2-asset-risk]').length, macro: !!t.querySelector('[data-ln1-row=macro]'), flat: !!t.querySelector('[data-ln1-flat]'), nt: !!t.querySelector('[data-ln1-notrade]'), det: !!t.querySelector('[data-ln3-hist]')}; }" % T)
        check(f"{tag} 5 PF3 การ์ดสินทรัพย์: ไม่มี Flat/งดเทรด/ลิงก์ประวัติสลับ Trend (ถอดแล้ว) · ไม่มีไม้ที่ถือ/Risk · ยังมีแถว Macro (WM1: ไม่มีรูป/ลิงก์ chart ใน Strategy)", not tile["flat"] and not tile["nt"] and not tile["det"] and tile["pos"] == 0 and tile["macro"] and not tile["img"] and not tile["tv"], tile)
        retired3(f"{tag} 5 PF1 — การ์ดสินทรัพย์: กราฟเต็ม + เปิด TradingView ↗ · Macro · ไม่มี Flat/งดเทรด/ประวัติ", "WM1 §7 — ไม่มีรูป/ลิงก์ chart ใน Strategy")
        fit = js(page, "()=>{ const i = document.querySelector('%s .vwImg.vwFull img'); return i ? getComputedStyle(i).objectFit : null; }" % T)
        retired3(f"{tag} 5 รูปกราฟเต็มไม่ตัดขอบ (object-fit: contain)", "WM1 §7 — ไม่มีรูปใน Strategy แล้ว")
        # บันทึก 2 บัญชี
        js(page, "([i])=>satV3PlanEdit(i,'tp','4300')", [iid]); page.wait_for_timeout(300)
        save(page, iid)
        put_ = js(page, "()=>{ const r = document.querySelector('[data-ln3-row]'); return r ? {t: r.innerText.replace(/\\s+/g,' ').trim(), p2: (r.querySelector('[data-ln3-p2]')||{}).innerText, st: r.dataset.ln3State, dots: r.querySelectorAll('[data-ln3-p2] b').length, status: r.querySelector('[data-ln3-status]').innerText} : null; }")
        check(f"{tag} 5 บันทึกแล้ว → สถานะ 'รอเข้า' · บรรทัด 2 '● 0.05 $315 · ● 0.05 $… · รวม $…/$…' (จุด 2 สี = 2 บัญชี)", put_ and put_["status"] == "รอเข้า" and put_["dots"] == 2 and "รวม $" in put_["p2"] and "/$" in put_["p2"], put_)
        tot = js(page, "()=>{ const r = document.querySelector('[data-ln3-row]'); return [r.querySelector('[data-ln3-ptot]').innerText, r.querySelector('[data-ln3-pcap]').innerText, ['main','fam'].map(a=>{ const R = satV2Risk(a), CP = satV2Caps(a), fx = satV2Money(a).fx; return [(R.byAsset['XAUUSD']||{tot:0}).tot/fx, CP.asset/fx]; })]; }")
        e_r = round(sum(x[0] for x in tot[2])); e_c = round(sum(x[1] for x in tot[2]))
        check(f"{tag} 5 'รวม' = Risk สินทรัพย์นั้น / เพดานต่อสินค้า (รวมบัญชีที่มีไม้) ตรง satV2Risk/satV2Caps", tot[0] == f"${e_r:,}" and tot[1] == f"${e_c:,}", [tot, e_r, e_c])
        js(page, "()=>{ const B=getBook('main'); const t=B.trades.find(x=>x.sym==='XAUUSD'); t.status='open'; t.openedAt='2026-10-01'; saveBook('main'); render(); }"); page.wait_for_timeout(600)
        st = js(page, "()=>document.querySelector('[data-ln3-status]').innerText")
        check(f"{tag} 5 มีไม้เปิด → สถานะ 'เข้าแล้ว n' · การ์ดสินทรัพย์ยังไม่มีไม้ที่ถือ/Risk", st.startswith("เข้าแล้ว") and js(page, "()=>document.querySelectorAll('%s .pv2tile,%s [data-pv2-pos]').length" % (T, T)) == 0, st)
        mg = js(page, "()=>{ const d = document.querySelector('[data-ln3-manage]'); return d ? d.textContent.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} 5 ปุ่มจัดการไม้เดิม (ปิดไม้ · แก้ SL) ยังอยู่ในพับ 'จัดการไม้'", mg and "ปิดไม้" in mg and "แก้ SL" in mg, mg)
        shot(page, f"ln3-plan-rows-{sfx}.png", "#satV3Panel")
    finally: b.close()

    # ── 6-7 ฟอร์ม Main: Zone จาก Strategy / ติ๊ก อยู่ใน Zone / Idea — PF1 ถอด: PF3 ตรวจว่าของเดิมหายจริง + Zone Activation ใหม่แทน (ตรวจเต็มใน phase98)
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        iz = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iz)
        frm = lambda: js(page, "()=>{ const f = document.querySelector('.ln1-card'); return f ? f.innerText.replace(/\\s+/g,' ') : ''; }")
        f0 = frm()
        check(f"{tag} 6 PF3 Long: ไม่มี 'อยู่ใน Zone ▲' ที่ดึงจาก Strategy · มีแถว Zone Activation ของแผน (ติ๊กเอง) ทดแทน", "อยู่ใน Zone ▲" not in f0 and cnt(page, "[data-pf-zact]") == 0 and cnt(page, "[data-pf-ztxt]") == 1, f0[:200])
        js(page, "([i])=>satV2SetDir(i,'Short')", [iz]); page.wait_for_timeout(400)
        f1 = frm()
        check(f"{tag} 6 PF3 เปลี่ยนเป็น Short: ไม่มี 'อยู่ใน Zone ▼' · ป้ายทิศเปลี่ยนตาม Trend ของแผน (▼ Down)", "อยู่ใน Zone ▼" not in f1 and "▼ Down" in js(page, "()=>(document.querySelector('[data-ln2-form=main]')||{innerText:''}).innerText"), f1[:200])
        check(f"{tag} 6 PF3 ไม่มีคำเตือน '⚠ ไม่อยู่ใน Zone' (ไม่ติ๊กก็ไม่เตือน)", "ไม่อยู่ใน Zone" not in f0 and "ไม่อยู่ใน Zone" not in f1)
        js(page, "([i])=>satV3PlanEdit(i,'entry','4180')", [iz]); js(page, "([i])=>satV3PlanEdit(i,'sl','4243')", [iz]); js(page, "([i])=>satV3PlanEdit(i,'tp','4000')", [iz]); page.wait_for_timeout(400)
        zdoc = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); return {zone_ok: x.zone_ok, zone_act: x.zone_act}; }", [iz])
        check(f"{tag} 6 PF3 ไม่มีฟิลด์ zone_ok บนแผน (zone_ok ไม่ถูกเขียนจากการติ๊ก/ไม่ติ๊ก) · มี zone_act ของ Zone Activation ใหม่ (เริ่ม false)", zdoc["zone_ok"] in (None,) and zdoc["zone_act"] is False, zdoc)
        save(page, iz)
        ztr = js(page, "()=>getBook('main').trades.map(t=>({zone_ok: t.zone_ok, idea_txt: t.idea_txt}))")
        check(f"{tag} 6 PF3 บันทึกแล้ว ไม้ไม่มี zone_ok / idea_txt (ไม่ auto-เขียน zone_ok=false · ไม่มีช่อง Idea)", len(ztr) >= 1 and all(t["zone_ok"] in (None,) and t["idea_txt"] in (None, "") for t in ztr), ztr)
    finally: b.close()

    # ── Tactical form
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        iid = idea(page, sleeve="tactical", entry=4180, sl=4160)
        check(f"{tag} 6 PF3 Tactical: ไม่มีช่อง Idea / ช่อง Zone กรอกเอง + ติ๊ก (ถอด) · มี Zone Activation (แถวติ๊ก + ข้อความ) ของแผนแทน · zone_txt ไม่ถูกเขียน", cnt(page, "[data-ln3-idea]") == 0 and cnt(page, "[data-pf-zact]") == 0 and cnt(page, "[data-pf-ztxt]") == 1 and cnt(page, "[data-pf-ztxt]") >= 0 and js(page, "([i])=>satIdeasList.find(y=>y.id===i).zone_txt", [iid]) in (None, ""), cnt(page, "[data-pf-zact]"))
        leg = txt(page, "[data-ln3-leg=tactical]")
        check(f"{tag} 6 Tactical: บรรทัด 'TP1 4,306 (2R·50%) · TP2 4,369 (3R)'", leg is not None and leg.startswith("TP1 ") and "(2R·50%)" in leg and "TP2 " in leg and "(3R)" in leg, leg)
        st = txt(page, "[data-ln2-form=tactical]")
        check(f"{tag} 7 สถานะ Tactical: '▲ · 2% · <บัญชี> $270 · <บัญชี> $180 · ● Loss 0/5 · DD 0/10%' (LN3fix3c: ทุกบัญชี · ≤340px แสดงจุดสีแทนชื่อ)", re.fullmatch(r"▲ Up · 2% · (?:\S+ )?\$270 · (?:\S+ )?\$180 · ● Loss 0/5 · DD 0/10%", st) is not None, st)
        shot(page, f"ln3-plan-form-tactical-{sfx}.png", ".ui-plan")
        def tl(i, d, pnl, k="x"): return sat_t(f"{k}{i}", status="closed", sleeve="tactical", entry=4180, sl=4160, qty=0.10, exitPrice=4180 + pnl / 10.0, exitDate=d)
        put(page, [tl(i, f"2026-09-{20 + i}", -50) for i in range(1, 6)], "main")
        stp = txt(page, "[data-ln2-form=tactical]")
        check(f"{tag} 7 ติดเกณฑ์ → '⛔ พัก Tactical' (สีแดง แทน ●) · ไม่มีคำว่า 'เบรก'", stp is not None and "⛔ พัก Tactical" in stp and "●" not in stp and "เบรก" not in stp and js(page, "()=>getComputedStyle(document.querySelector('[data-ln2-pause]')).color") == "rgb(192, 57, 43)", stp)
    finally: b.close()

    # ── Main status (ทิศตาม Macro)
    b, page, ce, pe, dl = launch(pw, w, h, pb=True)
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117)
        st = txt(page, "[data-ln2-form=main]")
        check(f"{tag} 7 สถานะ Main: '▲ · Macro ▲ · 2% · <บัญชี> $630 · <บัญชี> $420 · ไม้ใหม่ 0/5' (LN3fix3c: ทุกบัญชี)", re.fullmatch(r"▲ Up · Macro ▲ · 2% · (?:\S+ )?\$630 · (?:\S+ )?\$420 · (?:ไม้)?ใหม่ 0/5", st) is not None, st)
        check(f"{tag} 6 ทิศตาม Macro → ไม่มีกล่อง 'สวน Macro'", cnt(page, "[data-ln3-macro-box]") == 0)
    finally: b.close()
    # ── สวน Macro (สัปดาห์ Short · Playbook ▲ → Short สวน Macro)
    b, page, ce, pe, dl = launch(pw, w, h, bias="Short", pb=True, against=1.0)
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4243)
        box = txt(page, "[data-ln3-macro-box]")
        c0 = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); return {note: c.noteBlock, ready: c.ready, factor: c.factor, lot: c.lot}; }", [iid])
        check(f"{tag} 6 สวน Macro → โผล่กล่อง '⚠ สวน Macro ▲ · ใส่เหตุผล' · เหตุผลว่าง = บล็อก (noteBlock) · บันทึกไม่ได้", box and box.startswith("⚠ สวน Macro ▲") and bool(c0["note"]) and not c0["ready"], [box, c0])
        save(page, iid); n0 = len(trades(page, "main"))
        check(f"{tag} 6 เหตุผลว่างสั่งบันทึก → ไม่เกิดไม้", n0 == 0, n0)
        page.locator("[data-ln3-macro-box] input").fill("Fed เปลี่ยนท่าที"); page.locator("[data-ln3-macro-box] input").blur(); page.wait_for_timeout(700)
        x = js(page, "([i])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x,'main'); return {mn: x.macro_note, mw: x.macro_why, ready: c.ready, factor: c.factor, lot: c.lot, rule: c.ruleFactor, warns: c.warns, blocks: c.blocks}; }", [iid])
        check(f"{tag} 6 มีเหตุผล → เก็บ macro_why (+ macro_note) · พร้อมบันทึก · ขนาดไม้เต็ม (factor 1 ตามตั้งค่า)", x["mw"] == "Fed เปลี่ยนท่าที" and x["mn"] == "Fed เปลี่ยนท่าที" and x["ready"] and x["factor"] == 1, x)
        save(page, iid)
        check(f"{tag} 6 บันทึกสำเร็จหลังมีเหตุผล (ได้ไม้ plan)", len(trades(page, "main")) >= 1)
        lot_against = x["lot"]
    finally: b.close()
    b, page, ce, pe, dl = launch(pw, w, h, bias="Short", pb=False)
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4243); note(page, iid)
        lot_plain = js(page, "([i])=>satV3PlanAcctCalc(satIdeasList.find(y=>y.id===i),'main').lot", [iid])
        check(f"{tag} 6 lot ตอนสวน Macro (factor 1) = lot ตอนไม่สวน", lot_against == lot_plain and lot_plain, [lot_against, lot_plain])
    finally: b.close()

    # ── ลูกศรมีสี
    b, page, ce, pe, dl = launch(pw, w, h, pb=True)
    try:
        iid = idea(page, sleeve="main", entry=4180, sl=4117)
        c_dark_u = color(page, f"{T} .ln3-zr .ln3u"); c_form_u = color(page, "[data-ln2-form=main] .pf-up")
        check(f"{tag} 11 PF3 ไม่มีปุ่ม Trend (Up/Down) ของ Strategy ให้ลูกศรไปสีตามปุ่มที่เลือก: ในการ์ดไม่มี [data-ln1-trend] · ลูกศรสีมาจาก Macro (มืด) กับ Trend ของแผน (สว่าง) เท่านั้น", cnt(page, T + " [data-ln1-trend]") == 0 and c_dark_u is not None and c_form_u is not None, [c_dark_u, c_form_u])
        check(f"{tag} 11 PF1 — ลูกศร ▲ Macro บนพื้นมืด #4fd39a · ▲ Up ของแผนในฟอร์มสว่าง #1F9D6B (มีข้อความ Up)", c_dark_u == "rgb(79, 211, 154)" and c_form_u == "rgb(31, 157, 107)", [c_dark_u, c_form_u])
        shot(page, f"ln3-plan-form-main-{sfx}.png", ".ui-plan")
    finally: b.close()

    # ── lot/บล็อกเท่า LN2 (Lean = เดิม) + โหมดเดิม
    res = {}
    for m in ("lean", "legacy"):
        b, page, ce, pe, dl = launch(pw, w, h, bias="Neutral")
        try:
            js(page, "(m)=>ln1SetMode(m)", m); page.wait_for_timeout(400)
            setcfg(page, orSat=10, orAsset=10, orTot=20)
            i1 = idea(page, sleeve="main", entry=4180, sl=4117); note(page, i1)
            put(page, [sat_t("h1", "open", entry=4180, sl=4117, qty=0.50)], "main")
            res[m] = js(page, """(i)=>{ const x = satIdeasList.find(y=>y.id===i); return ['main','fam'].map(a=>{ const c = satV3PlanAcctCalc(x, a); return {lot:c.lot, ready:c.ready, blocks:c.blocks, limit:c.v2.limit}; }); }""", i1)
            if m == "legacy":
                pv = js(page, "()=>({hd: document.querySelectorAll('[data-pv2-header] [data-pv2-hd]').length, ln3rows: document.querySelectorAll('[data-ln3-row]').length, zone: document.querySelectorAll('[data-ln3-zone]').length, ask: document.querySelectorAll('[data-ln3-ask]').length})")
                check(f"{tag} 12 โหมดแบบเดิม: หัวกล่องเดิม (การ์ด Risk ต่อบัญชี) · ไม่มีแถวแผน/Zone ของ LN3", pv["hd"] == 2 and pv["ln3rows"] == 0 and pv["zone"] == 0, pv)
        finally: b.close()
    check(f"{tag} 11 lot / ตัวจำกัด / บล็อก / ready ของแผน Lean = แบบเดิม ทุกตัว", res["lean"] == res["legacy"], [res["lean"][0], res["legacy"][0]])

    # ── ล้น + console
    b, page, ce, pe, dl = launch(pw, w, h, pb=True)
    try:
        js(page, "()=>satwWrite('XAUUSD',{support:[4100,4140], resistance:[4300,4350], chart: %s})" % json.dumps(P76.CHART)); page.wait_for_timeout(400)
        iid = idea(page, sleeve="tactical", entry=4180, sl=4160)
        js(page, "()=>{ document.querySelector('[data-ln2-det]').open = true; const f = document.querySelector('%s .ln1-fold'); if(f) f.open = true; }" % T); page.wait_for_timeout(300)
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#satV3Panel *').forEach(e=>{ if(e.closest('.waBar.lf')) return; const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push(e.className || e.tagName); }); return bad.slice(0,5); }""")   # LN3fix §2.2 — แถบปุ่ม Asset เลื่อนแนวนอนได้ในตัวเอง
        check(f"{tag} 13 {label} ไม่ล้นแนวนอน (scrollWidth = innerWidth · ไม่มี element เกินขวา)", overflow(page) <= 0 and not ov, [overflow(page), ov])
        check(f"{tag} 13 {label} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
