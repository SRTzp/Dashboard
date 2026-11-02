#!/usr/bin/env python3
"""PV2b — โครงพอร์ต v2 รอบ 2: กติกา Main/Tactical ตาม Bias · Hedge · เพดาน Open Risk · เบรก DD/Tactical · แถบงบ Risk · เทส 78
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย · Satellite $45,000 (พอร์ตรวม $150,000)
ภาพ tests/screenshots/pv2b-{header,asset-hedge,blocks,brake}-{1440,390}.png
รัน: python3 run_tests_phase78.py"""
import functools, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22
import run_tests_phase37 as P37
import run_tests_phase54 as P54
import run_tests_phase59 as P59
import run_tests_phase76 as P76
import run_tests_phase77 as P77

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, overflow = P54.txt, P54.overflow
launch, idea = functools.partial(P77.launch, pin_sat=True), P77.idea
T = p22.T


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(1100)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def view(page, name, sel):
    """ภาพส่วนที่ยาวกว่าจอ: เลื่อนให้ชิดบนแล้วถ่ายทั้งจอ (ถ่ายเฉพาะ element ที่สูงเกินจอได้ภาพมีแถบทึบทับ)"""
    page.evaluate("(s)=>{ const e=document.querySelector(s); if(e) e.scrollIntoView({block:'start'}); window.scrollBy(0,-70); }", sel)
    page.wait_for_timeout(900)
    page.screenshot(path=os.path.join(SHOTS, name), full_page=False)


def cnt(page, sel): return page.locator(sel).count()


def sat_t(id, status="open", sym="XAUUSD", bias="Long", entry=4180, sl=4117, qty=0.10, sleeve="main", **kw):
    kw.setdefault("date", "2026-09-29"); kw.setdefault("openedAt", kw["date"])
    return T(id, "satB", status, sym=sym, bias=bias, entry=entry, sl=sl, qty=qty, mult=100 if sym == "XAUUSD" else 1, cur="USD", sleeve=sleeve, **kw)


def put(page, trades, acct="main"):
    js(page, "([a,t])=>{ const B=getBook(a); B.trades=t; saveBook(a); render(); }", [acct, trades]); page.wait_for_timeout(450)


def setcfg(page, **kw):
    js(page, "(o)=>{ const s = getBook('main').settings; s.satV2 = Object.assign({}, satV2Cfg('main'), o); saveBook('main'); render(); }", kw); page.wait_for_timeout(400)


def bias(page, asset, b):
    js(page, "([a,b])=>satwWrite(a,{bias:b, flips:0})", [asset, b]); page.wait_for_timeout(350)


def note(page, iid):
    js(page, "([i])=>satV3MacroNoteSet(i,'ทดสอบ')", [iid]); page.wait_for_timeout(350)


def calc(page, iid, acct="main"):
    return js(page, """([i,a])=>{ const x = satIdeasList.find(y=>y.id===i); const c = satV3PlanAcctCalc(x, a);
        return {lot:c.lot, ready:c.ready, warns:c.warns, blocks:c.blocks, tacType:c.tacType, softWarn:c.softWarn, limit:c.v2.limit, deal:c.v2.lotDeal, riskUsd:c.v2.dealTHB/c.v2.k, offBias:c.offBias, dd:c.ddBlock, msg:c.lotMsg, rawHedge:c.v2.rawHedge}; }""", [iid, acct])


def trades(page, acct="main"): return js(page, "(a)=>getBook(a).trades.filter(t=>t.port==='satB').map(t=>JSON.parse(JSON.stringify(t)))", acct)
def save(page, iid): js(page, "([i])=>satV3SaveReadyAccounts(i)", [iid]); page.wait_for_timeout(700)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # 1 Bias Long/Short
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        iid = idea(page, sleeve="tactical", entry=4240, sl=4260)
        js(page, "([i])=>satV2SetDir(i,'Short')", [iid]); page.wait_for_timeout(500)
        c = calc(page, iid)
        note(page, iid); c = calc(page, iid)
        check(f"{tag} PF3 1 Strategy bias เก่า Long · Tactical Short (ไม่มี Main): ประเภท = accel (ไม่ใช่ hedge/range) · ไม่มีบล็อกใด ๆ", c["tacType"] == "accel" and c["blocks"] == [], c)
        check(f"{tag} 1 PF1 — Strategy bias เก่า Long · Tactical Short (ไม่มี Main) → ไม่บล็อก · ไม่มีเหตุผลสวน Bias", c["ready"] and not any("สวน Bias" in x for x in c["warns"]) and cnt(page, "[data-offbias-block]") == 0, c)
        shot(page, f"pv2b-blocks-{sfx}.png", ".ui-pcell")
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid]); page.wait_for_timeout(400)
        js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, "entry", "4180"]); js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, "sl", "4160"]); js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid, "tp", "4220"]); page.wait_for_timeout(500)
        note(page, iid)
        c = calc(page, iid)
        check(f"{tag} 1 Tactical Long (ทิศเดียวกับ Bias) → ได้ · ป้าย 'เร่งกำไร'", c["ready"] and c["tacType"] == "accel" and (txt(page, "[data-v2-type=accel]") or "").startswith("เร่งกำไร"), c)
        save(page, iid)
        ts = trades(page)
        check(f"{tag} 1 ไม้ที่บันทึกเก็บ tac_type = accel · แถวไม้ในการ์ด Asset มีป้ายเร่งกำไร", len(ts) == 1 and ts[0]["tac_type"] == "accel" and ts[0]["sleeve"] == "tactical" and cnt(page, "[data-pv2-pos=tactical] [data-pv2-type=accel]") >= 1, ts)
        # Main สวน Bias = กติกาเดิม (SR1)
        iid2 = idea(page, sleeve="main", entry=4180, sl=4117)
        js(page, "([i])=>satV2SetDir(i,'Short')", [iid2]); page.wait_for_timeout(450)
        js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid2, "entry", "4180"]); js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid2, "sl", "4240"]); js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid2, "tp", "4060"]); page.wait_for_timeout(450)
        c2 = calc(page, iid2)
        check(f"{tag} 1 PF1 — Main ทิศ Short ขณะ Strategy bias เก่า Long → ไม่บล็อก (ทิศ = Trend ของแผน)", c2["ready"] and not any("สวน Bias" in x for x in c2["warns"]), c2)
        check(f"{tag} 1 {label} ไม่มี console error · ไม่ล้นแนวนอน", not ce and not pe and overflow(page) <= 1, [ce[:2], pe[:2], overflow(page)])
    finally: b.close()

    # 2 Neutral + Main
    b, page, ce, pe = launch(pw, w, h, bias="Neutral")
    try:
        put(page, [sat_t("m1", qty=0.10)])
        check(f"{tag} PF3 2 ไม่มีปุ่ม Neutral / ป้าย Neutral ในหน้า Strategy (ถอดแล้ว)", cnt(page, "[data-bias-neutral]") == 0 and "Neutral" not in (js(page, "()=>document.querySelector('.ui-tile[data-key=XAUUSD]').innerText") or ""))
        check(f"{tag} 2 PF1 — ปุ่ม + แผน มีเสมอ", cnt(page, ".ui-tile[data-key=XAUUSD] .ui-btn-pri") == 1)
        iid = idea(page, sleeve="tactical", entry=4240, sl=4265, bias="Short")
        d = js(page, "(i)=>satIdeasList.find(x=>x.id===i).bias", iid)
        check(f"{tag} PF3 2 ทิศของแผนมาจาก Trend ที่ผู้ใช้ตั้งในแผน (d = Short) ไม่ได้เดาสวน Main ให้เอง: ค่าที่ตั้ง = Short และ Main ยัง Long", d == "Short" and len([t for t in trades(page) if t["sleeve"] == "main"]) == 1, json.dumps([d, trades(page)]))
        check(f"{tag} 2 PF1 — ทิศ Short ตั้งโดยผู้ใช้ (Trend ของแผน)", d == "Short", d)
        note(page, iid)
        c = calc(page, iid)
        check(f"{tag} 2 Neutral + Main ▲ 0.10 · Tactical ▼ → Hedge · ขนาด ≤ Main (0.10) · Risk จริง $250", c["tacType"] == "hedge" and c["limit"] == "hedge" and c["lot"] == 0.10 and abs(c["riskUsd"] - 250) < 1e-6 and c["ready"], c)
        check(f"{tag} 2 การ์ดแสดงป้าย Hedge (อัตโนมัติ) + แถวจำกัดโดย Main", (txt(page, "[data-v2-type=hedge]") or "").startswith("Hedge") and cnt(page, ".ui-plan [data-v2-size]") >= 1)
        save(page, iid)
        ts = [t for t in trades(page) if t["sleeve"] == "tactical"]
        check(f"{tag} 2 ไม้ Hedge ที่บันทึก: tac_type hedge · qty 0.10 · size_limit hedge", len(ts) == 1 and ts[0]["tac_type"] == "hedge" and ts[0]["qty"] == 0.10 and ts[0]["size_limit"] == "hedge", ts)
        put(page, [sat_t("m1", qty=0.05)])
        iid3 = idea(page, sleeve="tactical", entry=4240, sl=4265, bias="Short")
        page.wait_for_timeout(400)
        c = calc(page, iid3)
        check(f"{tag} 2 Main เล็กลงเป็น 0.05 → Hedge จำกัด ≤ 0.05 (สัญญา Hedge ไม่เกิน Main)", c["lot"] == 0.05 and c["limit"] == "hedge", c)
        js(page, "([i])=>satV2SetDir(i,'Long')", [iid3]); page.wait_for_timeout(500)
        js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid3, "entry", "4180"]); js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid3, "sl", "4160"]); js(page, "([i,f,v])=>satV3PlanEdit(i,f,v)", [iid3, "tp", "4220"]); page.wait_for_timeout(500)
        note(page, iid3)
        c = calc(page, iid3)
        check(f"{tag} PF3 2 Main ▲ + Tactical ▲: ไม่มีบล็อก 'รอ Bias เปลี่ยน' / เตือนสวน Bias ในรายการ blocks/warns", not any(("รอ Bias" in x or "สวน Bias" in x) for x in c["blocks"] + c["warns"]), c)
        check(f"{tag} 2 PF1 — Main ▲ + Tactical ▲ (ทิศเดียวกัน) → เร่งกำไร (accel) · ไม่บล็อก", c["ready"] and c["tacType"] == "accel" and c["blocks"] == [], c)
        # Main ตอน Neutral เข้าได้ตามเดิม
        put(page, [])
        iid4 = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iid4)
        c4 = calc(page, iid4)
        check(f"{tag} 2 Main ตอน Neutral เข้าได้ตามเดิม (ไม่บล็อก)", c4["ready"] and not c4["offBias"], c4)
    finally: b.close()

    # 3 Neutral ไม่มี Main → Range
    # PF3: Range/กรอบ 3× SL ถอดแล้ว — เช็กแทนอยู่หลังเช็ก PF1 ของ block 3 ด้านล่าง
    # PF3: (ต่อ) ป้าย Range ในการ์ด → เช็กไม่มีป้าย Range ด้านล่าง
    # PF3: (ต่อ) tac_type range → เช็ก tac_type ไม่ใช่ range ด้านล่าง
    b, page, ce, pe = launch(pw, w, h, bias="Neutral")
    try:
        iid = idea(page, sleeve="tactical", entry=4180, sl=4160); note(page, iid)
        c = calc(page, iid)
        check(f"{tag} 3 PF1 — Tactical ไม่มี Main → accel · ไม่มีเตือนกรอบ 3× · ไม่บล็อก · บันทึกได้ tac_type accel", c["tacType"] == "accel" and c["ready"] and not c["softWarn"] and c["blocks"] == [], c)
        save(page, iid)
        ts = trades(page)
        check(f"{tag} 3 PF1 — ไม้ Tactical ไม่มี Main บันทึก tac_type accel", len(ts) == 1 and ts[0]["tac_type"] == "accel", ts)
        card = js(page, "(i)=>{ const e=document.querySelector('.ui-plan[data-id=\"'+i+'\"]'); return e ? e.innerText : ''; }", iid)
        check(f"{tag} 3 PF3 Neutral ไม่มี Main: ไม่มีประเภท Range (tacType ≠ range) · การ์ดไม่มีป้าย Range/'กรอบควรกว้าง' · ไม้ที่บันทึก tac_type ≠ range", c["tacType"] != "range" and "Range" not in card and "กรอบควรกว้าง" not in card and ts[0]["tac_type"] != "range", [c["tacType"], card[:120], ts[0]["tac_type"]])
        iid_e = idea(page, sleeve="tactical", bias="")
        d_e = js(page, "(i)=>satIdeasList.find(x=>x.id===i).bias", iid_e)
        check(f"{tag} 3 PF3 แผนใหม่ (Strategy bias เก่า Neutral) ไม่มีทิศเริ่มต้นจาก Strategy: Trend ของแผนว่าง ('' ไม่ใช่ Long/Short)", d_e in ("", None), d_e)
    finally: b.close()

    # 4 เพดาน Open Risk
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        # 4a Satellite ≤ 1.2% ($1,800): BTC เสี่ยงค้าง $1,500 + Main ใหม่ ไม้ 1 = $315 → $1,815
        put(page, [sat_t("b1", sym="BTCUSD", entry=70000, sl=68500, qty=1)])
        iid = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iid)
        c = calc(page, iid)
        check(f"{tag} 4 Satellite จะเป็น $1,815 > $1,800 (1.2%) → บล็อก + บอกตัวเลข", (not c["ready"]) and any("Satellite Open Risk จะเป็น $1,815 > $1,800 (1.2%)" in m for m in c["blocks"]), c)
        shot(page, f"pv2b-blocks-{sfx}.png", ".ui-pcell")
        setcfg(page, orSat=1.5)
        c = calc(page, iid)
        check(f"{tag} 4 เปลี่ยนเพดาน Satellite 1.2 → 1.5 (= $2,250) → ผ่าน (บล็อกตามค่าใหม่)", c["ready"] and c["blocks"] == [], c)
        setcfg(page, orSat=1.2)
        # 4b ต่อสินค้า ≤ 0.6% ($900): XAUUSD Main ค้าง $700 + Tactical ใหม่ $240
        put(page, [sat_t("m1", qty=0.07, sl=4080)])
        iid2 = idea(page, sleeve="tactical", entry=4180, sl=4160); note(page, iid2)
        c = calc(page, iid2)
        check(f"{tag} 4 ต่อสินค้า: XAUUSD จะเป็น $940 > $900 (0.6%) → บล็อก (นับ Main + Tactical เต็ม ไม่หักกัน)", (not c["ready"]) and any("Risk XAUUSD จะเป็น $940 > $900 (0.6%)" in m for m in c["blocks"]), c)
        # 4c SL เลย Entry → Open Risk 0 → เปิดใหม่ได้
        put(page, [sat_t("m1", qty=0.09, sl=4090)])
        c = calc(page, iid2)
        check(f"{tag} 4 Main ค้าง $810 + Tactical $240 = $1,050 > $900 → บล็อก", not c["ready"] and any("$1,050" in m for m in c["blocks"]), c["blocks"])
        put(page, [sat_t("m1", qty=0.09, sl=4200)])
        c = calc(page, iid2)
        check(f"{tag} 4 เลื่อน SL ของ Main เลย Entry (ฝั่งกำไร) → Open Risk = 0 → เปิด Tactical ได้", c["ready"] and c["blocks"] == [], c)
        # 4d Core + Satellite ≤ 6% ($9,000): Core เสี่ยง $8,800 (฿352,000) + Main ใหม่ $315
        put(page, [T("c1", "core", "open", sym="CCC", entry=100, sl=80, qty=17600, cur="THB", date="2026-09-10", openedAt="2026-09-10")])
        iid3 = idea(page, sleeve="main", entry=4180, sl=4117, asset="BTCUSD") if False else None
        c = calc(page, iid)
        check(f"{tag} 4 Core $8,800 + Satellite ใหม่ $315 → $9,115 > $9,000 (6%) → บล็อก", (not c["ready"]) and any("Core + Satellite จะเป็น $9,115 > $9,000 (6%)" in m for m in c["blocks"]), c["blocks"])
        put(page, [T("c1", "core", "open", sym="CCC", entry=100, sl=120, qty=17600, cur="THB", date="2026-09-10", openedAt="2026-09-10")])
        c = calc(page, iid)
        check(f"{tag} 4 Core ที่ Stop เลยทุนแล้ว นับ 0 → ผ่าน", c["ready"] and c["blocks"] == [], c["blocks"])
        check(f"{tag} 4 {label} ไม่มี console error · ไม่ล้นแนวนอน", not ce and not pe and overflow(page) <= 1, [ce[:2], pe[:2], overflow(page)])
    finally: b.close()

    # 5 Max DD Satellite + เบรก Tactical
    b, page, ce, pe = launch(pw, w, h, bias="Long")
    try:
        iidM = idea(page, sleeve="main", entry=4180, sl=4117); note(page, iidM)
        iidT = idea(page, sleeve="tactical", entry=4180, sl=4160); note(page, iidT)
        loss = sat_t("x1", status="closed", entry=4180, sl=4000, qty=1, exitPrice=4099, exitDate="2026-09-28", sleeve="main")
        put(page, [loss])
        st = js(page, "()=>ddEval('main','sat').stage")
        cM, cT = calc(page, iidM), calc(page, iidT)
        check(f"{tag} 5 DD Satellite 18% · Max DD 20% → ยังไม่หยุด (stage {st}) · เปิดไม้ใหม่ได้ทั้งสองส่วน", st != "pause" and not cM["dd"] and not cT["dd"] and cM["ready"] and cT["ready"], [st, cM["dd"], cT["dd"]])
        setcfg(page, maxDd=15)
        st = js(page, "()=>ddEval('main','sat').stage")
        cM, cT = calc(page, iidM), calc(page, iidT)
        check(f"{tag} 5 ตั้ง Max DD 15% → DD 18% เกิน → หยุดเปิดไม้ใหม่ทั้ง Main + Tactical (stage {st})", st == "pause" and bool(cM["dd"]) and bool(cT["dd"]) and not cM["ready"] and not cT["ready"], [st, cM["dd"]])
        setcfg(page, maxDd=20)
        js(page, "()=>{ const s = getBook('main').settings; s.ddState.sat = %s; saveBook('main'); render(); }" % json.dumps(P37.ds0(45000))); page.wait_for_timeout(300)   # ล้างสถานะพักที่แอปจดไว้ (ระบบเดิม: พักจนครบกำหนด + รีวิว)
        # เบรก Tactical: เสียติด 5 ไม้
        def tl(i, d, pnl_usd, k="x"): return sat_t(f"{k}{i}", status="closed", sleeve="tactical", entry=4180, sl=4160, qty=0.10, exitPrice=4180 + pnl_usd / 10.0, exitDate=d, date="2026-09-%02d" % (int(d[-2:]) - 14), openedAt="2026-09-%02d" % (int(d[-2:]) - 14))   # RG2b: ไม้ปิดแล้วเปิดก่อนสัปดาห์นี้ — ไม่กินโควตาไม้ใหม่ 4/สัปดาห์
        losses = [tl(i, f"2026-09-{20 + i}", -50) for i in range(1, 6)]
        put(page, losses)
        cM, cT = calc(page, iidM), calc(page, iidT)
        br = js(page, "()=>{ const b = satV2Brake('main'); return [b.streak, b.stop, b.msg]; }")
        check(f"{tag} 5 เสียติด 5 ไม้ → เบรก Tactical หยุด + ข้อความบอกเงื่อนไขปลด · บล็อกเฉพาะ Tactical (Main เปิดได้)", br[0] == 5 and br[1] and "เสียติด 5/5" in br[2] and "ปลดเมื่อ" in br[2] and not cT["ready"] and any("เบรก Tactical" in m for m in cT["blocks"]) and cM["ready"] and cM["blocks"] == [], [br, cT["blocks"], cM["blocks"], cM["ready"], cM["warns"]])
        check(f"{tag} 5 หัว Strategy: เสียติด 5/5 · ป้าย 'หยุด'", "5" in (txt(page, "[data-pv2-brake=stop]") or "") and txt(page, "[data-pv2-brake-tag]") == "หยุด", txt(page, "[data-pv2-brake]"))
        view(page, f"pv2b-brake-{sfx}.png", "[data-pv2-hd=main]")
        put(page, losses + [tl(6, "2026-09-27", 300, "w")])
        cT = calc(page, iidT)
        check(f"{tag} 5 มีไม้ชนะ → เบรกปลด · Tactical เปิดได้ · ป้าย 'เปิดได้'", cT["ready"] and txt(page, "[data-pv2-brake-tag]") == "เปิดได้", [cT["blocks"], txt(page, "[data-pv2-brake-tag]")])
        # DD 10% ของ Tactical ($1,350): แพ้ 2 ไม้ ไม้ละ $700
        put(page, [tl(1, "2026-09-21", -700), tl(2, "2026-09-22", -700)])
        br = js(page, "()=>{ const b = satV2Brake('main'); return [b.streak, b.stop, Math.round(b.ddPct*10)/10, b.msg]; }")
        cT = calc(page, iidT)
        check(f"{tag} 5 DD Sat 3.1% ≥ 3% (เสียติดแค่ 2 · RG2b เบรก DD ฐานถัง Sat) → หยุด · ข้อความ DD", br[1] and br[0] == 2 and br[2] == 3.1 and "DD 3.1%/3%" in br[3] and not cT["ready"], br)
        put(page, [tl(1, "2026-09-21", -700), tl(2, "2026-09-22", -700), tl(3, "2026-09-23", 300, "w")])
        br = js(page, "()=>satV2Brake('main').stop")
        check(f"{tag} 5 ชนะ 1 ไม้ (DD เหลือ 2.4% < 3%) → ปลด", br is False)
        setcfg(page, brkN=2, brkDd=50)
        put(page, [tl(1, "2026-09-21", -100), tl(2, "2026-09-22", -100)])
        check(f"{tag} 5 เปลี่ยนเบรก 5 → 2 ไม้ → แพ้ 2 ติดก็หยุด (ตามค่าตั้งใหม่)", js(page, "()=>satV2Brake('main').stop") is True)
    finally: b.close()

    # 6 แถบหัว + การ์ด Asset ตรงกับข้อมูล
    b, page, ce, pe = launch(pw, w, h, bias="Neutral")
    try:
        put(page, [sat_t("m1", qty=0.10), sat_t("h1", sleeve="tactical", bias="Short", entry=4240, sl=4265, qty=0.10, tac_type="hedge")])
        hd = txt(page, "[data-pv2-meter=sat]") or ""
        check(f"{tag} 6 หัว Strategy: Satellite Open Risk $880 / $1,800 (1.2%) · Main $630 · Tactical $250", "$880 / $1,800 (1.2%)" in hd and "Main $630" in hd and "Tactical $250" in hd, hd)
        tt = txt(page, "[data-pv2-meter=total]") or ""
        check(f"{tag} 6 Core + Satellite $880 / $9,000 (6%)", "$880 / $9,000 (6%)" in tt, tt)
        ar = txt(page, ".ui-tile[data-key=XAUUSD] [data-pv2-asset-risk]") or ""
        rows = js(page, "()=>[...document.querySelectorAll('.ui-tile[data-key=XAUUSD] [data-pv2-pos]')].map(e=>e.dataset.pv2Pos)")
        check(f"{tag} 6 การ์ด Asset XAUUSD: แถว Main + Tactical แยก · Hedge · 'Risk รวม XAUUSD $880 / $900 (0.6%)'", rows == ["main", "tactical"] and "Risk รวม XAUUSD $880 / $900 (0.6%)" in ar and cnt(page, ".ui-tile[data-key=XAUUSD] [data-pv2-type=hedge]") == 1, [rows, ar])
        view(page, f"pv2b-header-{sfx}.png", "#satV3Sum")
        shot(page, f"pv2b-asset-hedge-{sfx}.png", ".ui-tile[data-key=XAUUSD]")
        setcfg(page, orSat=1.5, orAsset=0.8, orTot=7)
        hd = txt(page, "[data-pv2-meter=sat]") or ""; ar = txt(page, ".ui-tile[data-key=XAUUSD] [data-pv2-asset-risk]") or ""; tt = txt(page, "[data-pv2-meter=total]") or ""
        check(f"{tag} 6 เปลี่ยนค่าตั้ง (1.5 / 0.8 / 7) → แถบตามค่าใหม่ ($2,250 · $1,200 · $10,500)", "/ $2,250 (1.5%)" in hd and "/ $1,200 (0.8%)" in ar and "/ $10,500 (7%)" in tt, [hd, ar, tt])
        # 7 Main โดน SL → Hedge ยังเปิดอยู่
        js(page, "()=>{ const B = getBook('main'); const m = B.trades.find(t=>t.id==='m1'); m.status='closed'; m.exitPrice = m.sl; m.exitDate = '2026-10-01'; saveBook('main'); render(); }"); page.wait_for_timeout(450)
        ts = {t["id"]: t["status"] for t in trades(page)}
        check(f"{tag} 7 Main โดน SL (ปิด) → Hedge ยังเปิดอยู่ ไม่ปิดตาม · แถวยังอยู่ในการ์ด Asset", ts == {"m1": "closed", "h1": "open"} and cnt(page, ".ui-tile[data-key=XAUUSD] [data-pv2-pos=tactical]") == 1 and cnt(page, ".ui-tile[data-key=XAUUSD] [data-pv2-pos=main]") == 0, ts)
        check(f"{tag} 6 {label} ไม่มี console error · ไม่ล้นแนวนอน", not ce and not pe and overflow(page) <= 1, [ce[:2], pe[:2], overflow(page)])
    finally: b.close()

    # 8 RR2 ยังผ่าน: กดปุ่มในการ์ดแผน v2 แล้วภาพกราฟไม่โหลดซ้ำ
    kw = {"mut": P77.fixture(), "pick": ["XAUUSD", "BTCUSD"]}
    b, c_, page, ce, pe, dl, env = P59.launch(pw, w, h, **kw)
    try:
        js(page, "(c)=>{ satwWrite('XAUUSD', {bias:'Long', support:[3920], resistance:[4080], invalidation:3840, chart:c}); satwWrite('BTCUSD', {bias:'Long'}); }", P76.CHART); page.wait_for_timeout(400)
        P37.go_sat(page); page.wait_for_timeout(300)
        iid = js(page, "()=>satV2NewPlan('XAUUSD','main')"); page.wait_for_timeout(600)
        ok0 = js(page, P76.WATCH)
        for sel in ("[data-sleeve=tactical]", "[data-dir=Short]", "[data-dir=Long]", "[data-v2-setup]", "[data-sleeve=main]"):
            page.locator(sel).first.click(); page.wait_for_timeout(450)
        page.locator("[data-v2-entry]").first.fill("4180"); page.locator("[data-v2-entry]").first.press("Tab"); page.wait_for_timeout(450)
        st = js(page, P76.STATE)
        check(f"{tag} 8 กดปุ่มส่วน/ทิศ/Setup + กรอก Entry ในการ์ดแผน → ภาพกราฟไม่โหลดซ้ำ (load 0 · node เดิม · RR2 ผ่าน)", ok0 and st["loads"] == 0 and st["same"] and st["complete"], [ok0, st])
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
