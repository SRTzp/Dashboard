#!/usr/bin/env python3
"""AC1 — เงื่อนไขเข้า Sat: ติ๊ก Break ราคา · Break Vol · Pullback + Pullback zone · ครบ = Activate เอง (ตัดปุ่ม Activate) · เทส 60
mock Firestore · Chromium 1440 + 390
ภาพ tests/screenshots/ac1-{cond-empty,cond-missing,cond-active,today-wait}-{1440,390}.png
รัน: python3 run_tests_phase60.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase51 as P51
import run_tests_phase55 as P55

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
CLK = "2026-10-01T05:00:00Z"
MISS_ALL = "ขาด: Break Price · Break Vol · Pullback · TP · Invalidation"   # AC2: ไม่มี Pullback zone แยกแล้ว


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def cond(cid="c1", text="Break & Pullback @ 2400", tp=None, inval=None, steps=(0, 0, 0), pb=None, active=False, tf="4H", legacy=False, lv=True, brk=2400, vol=2410):
    """AC2: เงื่อนไขมีตัวเลข Break Price/Vol (ค่าเริ่ม 2400/2410) เว้นแต่ lv=False (ว่าง) หรือ legacy (ข้อเก่าไม่มี steps)"""
    c = {"id": cid, "text": text, "tp_from": tp[0] if tp else None, "tp_to": tp[1] if tp else None, "inval": inval, "active": active, "saved": True}
    if not legacy:
        c.update({"kind": "bp", "steps": {"brk": bool(steps[0]), "vol": bool(steps[1]), "pb": bool(steps[2])}, "brk_tf": tf,
                  "pb_from": pb[0] if pb else None, "pb_to": pb[1] if pb else None,
                  "brk_px": brk if lv else None, "vol_px": vol if lv else None, "brk_dir": None, "vol_dir": None})
    return c


def bp_idea(conds, asset="XAUUSD", bias="Long", iid="iD", entry=None, sl=None, tp=None, broker=None):
    d = {"id": iid, "v3": True, "asset": asset, "bias": bias, "entry": entry, "sl": sl, "tp": tp, "accts": {}, "conditions": conds}
    if broker: d["accts"] = {"main": {"broker": broker}}
    return d


def fresh(page, idea):
    P51.fresh(page, idea)
    page.wait_for_timeout(300)


def doc_of(page, iid="iD"): return js(page, "(i)=>JSON.parse(JSON.stringify(sat7dIdea(i)))", iid)


def cd(page, cid="c1", iid="iD"): return [c for c in doc_of(page, iid)["conditions"] if c["id"] == cid][0]


def active_ids(page, iid="iD"): return [c["id"] for c in doc_of(page, iid)["conditions"] if c.get("active")]


def ac(page, cid="c1", iid="iD"): return f'.ui-plan[data-id="{iid}"] .ui-ac[data-ac="{cid}"]'


def chip(page, k, cid="c1", iid="iD"): return page.locator(f'{ac(page, cid, iid)} [data-step="{k}"]')


def txt(page, sel):
    return re.sub(r"\s+", " ", page.locator(sel).first.text_content() or "").strip() if page.locator(sel).count() else ""


def fill(page, sel, val):
    page.locator(sel).first.fill(str(val)); page.locator(sel).first.press("Tab"); page.wait_for_timeout(450)


def zone(page, a, b, cid="c1", iid="iD"):
    if a is not None: fill(page, f'{ac(page, cid, iid)} [data-ac-z="from"]', a)
    if b is not None: fill(page, f'{ac(page, cid, iid)} [data-ac-z="to"]', b)


def num(page, field, val, cid="c1", iid="iD"):
    sel = f'.ui-plan[data-id="{iid}"] :is([data-cond="{cid}"],[data-cond-edit="{cid}"]) .ui-cond-nums input[onchange*="\'{field}\'"]'
    if not page.locator(sel).count() and page.locator(f'.ui-plan[data-id="{iid}"] .ui-cs-edit').count():
        page.locator(f'.ui-plan[data-id="{iid}"] .ui-cs-edit').click(); page.wait_for_timeout(250)   # ข้อที่ Active อยู่แก้ TP/Inval ผ่าน ✎
    fill(page, sel, val)


def lvl(page, k, val, cid="c1", iid="iD"): fill(page, f'{ac(page, cid, iid)} [data-ac-px="{k}"]', val)


def pbf(page, val, cid="c1", iid="iD"): fill(page, f'{ac(page, cid, iid)} [data-ac-pb]', val)


def sums(page, cid="c1", iid="iD"):
    return page.evaluate("(s)=>[...document.querySelectorAll(s+' .ui-acs')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())", ac(page, cid, iid))


def edit_open(page, grp, cid="c1", iid="iD"):
    """แตะบรรทัดสรุป (break | brk | vol | pb) กลับเป็นแถวกรอก"""
    sel = f'{ac(page, cid, iid)} [data-sum="{grp}"]'
    if page.locator(sel).count(): page.locator(sel).click(); page.wait_for_timeout(300)


def tpnum(page, field, val, cid="c1", iid="iD"):
    sel = f'.ui-plan[data-id="{iid}"] :is([data-cond="{cid}"],[data-cond-edit="{cid}"]) .ui-cond-nums input[onchange*="\'{field}\'"]'
    if not page.locator(sel).count() and page.locator(f'.ui-plan[data-id="{iid}"] [data-ac-bar]').count():
        page.locator(f'.ui-plan[data-id="{iid}"] [data-ac-bar]').click(); page.wait_for_timeout(250)   # ข้อที่ Active อยู่แก้ TP/Inval ผ่านแถบ Active
    fill(page, sel, val)


def tick(page, k, cid="c1", iid="iD"):
    chip(page, k, cid, iid).click(); page.wait_for_timeout(450)


def pressed(page, cid="c1", iid="iD"):
    return page.evaluate("(sel)=>[...document.querySelectorAll(sel+' [data-step]')].map(e=>e.getAttribute('aria-pressed')==='true')", ac(page, cid, iid))


def overflow(page, sels): return P37.overflow(page, sels)


def sat_page(pw, w, h):
    browser, context, page, ce, pe, dialogs = P37.launch(pw, w, h)
    p5.goto_sat(page); p36.clean(page, "Long"); P37.go_sat(page)
    return browser, page, ce, pe


# ───────────────────────── 1-5 · 10 ─────────────────────────
# AC2: ชิป 3 ขั้น + ช่อง zone เปลี่ยนเป็นแถวกรอกตัวเลข (TF → Break Price → Break Vol → Pullback) · ความคาดหวังเดิม (ติ๊กครบ → Activate เอง · ถอน → ยกเลิกเอง · TP เริ่มต้น) ตรวจเท่าเดิม — ดู tests/AC2_retired.md
def ui_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, page, ce, pe = sat_page(pw, w, h)
    try:
        # ── 1 เงื่อนไขใหม่
        fresh(page, bp_idea([cond(lv=False)]))
        root = '.ui-plan[data-id="iD"]'
        check(f"{tag} 1 ไม่มีปุ่ม Activate (ไม่มี checkbox/ปุ่ม ใน UI) · มีช่องติ๊ก 3 ช่อง", page.locator(f"{root} .ui-cond-act").count() == 0 and page.locator(f"{root} .ui-wc-act").count() == 0 and page.evaluate("(r)=>[...document.querySelectorAll(r+' button, '+r+' label')].filter(e=>/^\\s*Activate\\s*$/.test(e.textContent)).length", root) == 0
              and page.locator(f'{ac(page)} [data-step]').count() == 3, txt(page, root))
        labs = page.evaluate("(s)=>[...document.querySelectorAll(s+' .ui-ac-nm')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())", ac(page))
        check(f"{tag} 1 แถว: Break Price · Break Vol · Pullback (ว่างทั้งหมด · ไม่ติ๊ก)", labs == ["Break Price", "Break Vol", "Pullback"] and pressed(page) == [False, False, False], json.dumps(labs, ensure_ascii=False))
        check(f"{tag} 1 TF ปิดแท่งเริ่มต้น 4H · มีตัวเลือก 4H | D | W (PY2 เพิ่ม W)", page.locator(f'{ac(page)} [data-ac-tf] [aria-pressed="true"]').inner_text() == "4H" and page.locator(f'{ac(page)} [data-ac-tf] button').all_inner_texts() == ["4H", "D", "W"])
        check(f"{tag} 1 บรรทัด '{MISS_ALL}'", txt(page, f'{ac(page)} [data-ac-miss]') == MISS_ALL, txt(page, f'{ac(page)} [data-ac-miss]'))
        shot(page, f"ac1-cond-empty-{sfx}.png", root)
        page.locator(f'{ac(page)} [data-ac-tf] [data-tf="D"]').click(); page.wait_for_timeout(400)
        check(f"{tag} 1 เลือก TF = D → เก็บ brk_tf:'D' · ไม่ Activate", cd(page)["brk_tf"] == "D" and active_ids(page) == [], json.dumps(cd(page)))
        page.locator(f'{ac(page)} [data-ac-tf] [data-tf="4H"]').click(); page.wait_for_timeout(300)

        # ── 2 Pullback ติ๊กได้เมื่อ Break ครบ + มีค่า Pullback
        dis = page.evaluate("(s)=>{const e=document.querySelector(s+' [data-step=pb]'); return {d:e.getAttribute('aria-disabled'), t:e.title, bg:getComputedStyle(e).backgroundColor};}", ac(page))
        check(f"{tag} 2 Pullback ก่อน Break → ช่องติ๊กเทา (aria-disabled) + title บอกเหตุ", dis["d"] == "true" and "Break" in dis["t"], json.dumps(dis, ensure_ascii=False))
        js(page, "()=>satAcStep('iD','c1','pb',true)"); page.wait_for_timeout(300)
        check(f"{tag} 2 เรียกติ๊ก Pullback ตรง ๆ ก่อน Break → ไม่ได้ (steps.pb ยัง false)", cd(page)["steps"]["pb"] is False, json.dumps(cd(page)))
        lvl(page, "brk", 2400); lvl(page, "vol", 2410)
        tick(page, "brk"); tick(page, "vol")
        check(f"{tag} 2 ติ๊ก Break Price + Break Vol (ลำดับใดก็ได้ · ต้องกรอกตัวเลขก่อน) → steps.brk/vol true", cd(page)["steps"] == {"brk": True, "vol": True, "pb": False}, json.dumps(cd(page)["steps"]))
        blk = js(page, "()=>satAcPbBlock({kind:'bp', steps:{brk:true, vol:true, pb:false}})")
        check(f"{tag} 2 Break ครบแต่ไม่มีค่า Pullback เลย → ติ๊กไม่ได้ + เหตุ 'กรอก Pullback ก่อน' (ข้อมูลไม่มีตัวเลข Break · ตรวจที่ฟังก์ชัน)", blk == "กรอก Pullback ก่อน", blk)
        js(page, "()=>satAcStep('iD','c1','pb',true)"); page.wait_for_timeout(300)
        check(f"{tag} 2 Break ครบ + ค่าเริ่ม (กรอบ Break) → ติ๊ก Pullback ได้ แต่ pb_from/pb_to ยัง null", cd(page)["steps"]["pb"] is True and cd(page)["pb_from"] is None, json.dumps(cd(page)))
        js(page, "()=>satAcStep('iD','c1','pb',false)"); page.wait_for_timeout(300)
        page.locator(f'{ac(page)} [data-ac-pb]').count()
        pbf(page, "2412-2405")
        c = cd(page)
        check(f"{tag} 2 กรอก Pullback 2412-2405 → เรียงน้อย→มากให้เอง (2405–2412)", (c["pb_from"], c["pb_to"]) == (2405, 2412), json.dumps(c))
        check(f"{tag} 2 มีค่า Pullback → ช่องติ๊กไม่เทา", "ui-dis" not in (page.locator(f'{ac(page)} [data-step=pb]').get_attribute("class") or ""))
        pbf(page, "0")
        check(f"{tag} 2 ตัวเลข Pullback ต้อง > 0 (0 → ไม่เขียน ค่าเดิม 2405–2412 คงอยู่ · AC2 ตัดการล้างด้วย 0)", (cd(page)["pb_from"], cd(page)["pb_to"]) == (2405, 2412), json.dumps(cd(page)))
        page.wait_for_timeout(1700)
        pbf(page, 2405)
        tick(page, "pb")
        check(f"{tag} 2 ติ๊ก Pullback ได้ → steps.pb true (ครบ 3 ขั้น) แต่ยังไม่ครบ TP/Inval → ไม่ Activate", cd(page)["steps"]["pb"] is True and active_ids(page) == [], json.dumps(cd(page)))
        miss = txt(page, f'{ac(page)} [data-ac-miss]')
        check(f"{tag} 2 บรรทัดขาด เหลือ 'TP · Invalidation' (เรียงตามลำดับ)", miss == "ขาด: TP · Invalidation", miss)
        shot(page, f"ac1-cond-missing-{sfx}.png", root)

        # ── 3 ครบ → Activate เอง
        tpnum(page, "tp_from", 2440)
        check(f"{tag} 3 TP 1 ช่อง ยังขาด Invalidation → ไม่ Activate", active_ids(page) == [] and txt(page, f'{ac(page)} [data-ac-miss]') == "ขาด: Invalidation", txt(page, f'{ac(page)} [data-ac-miss]'))
        tpnum(page, "inval", 2390)
        c = cd(page); d = doc_of(page)
        check(f"{tag} 3 ติ๊กครบ + TP 1 ช่อง + Invalidation → active:true อัตโนมัติ", active_ids(page) == ["c1"] and c["saved"] is True, json.dumps(c))
        auto = {k: d.get(k) for k in ("act_side", "tp", "entry", "sl")}
        check(f"{tag} 3 ป้าย '● Active' ขึ้น · ไม่มีปุ่ม Activate · ช่อง Entry/SL เปิด", page.locator(f'{root} [data-ac-on]').count() == 1 and page.locator(f"{root} .ui-plan-nums").count() == 1 and page.locator(f"{root} .ui-cond-act").count() == 0, txt(page, root)[:200])
        shot(page, f"ac1-cond-active-{sfx}.png", root)
        js(page, "()=>satV3CondActivate('iD','c1',false)"); page.wait_for_timeout(350)
        js(page, "()=>satV3CondActivate('iD','c1',true)"); page.wait_for_timeout(350)
        d2 = doc_of(page); manual = {k: d2.get(k) for k in ("act_side", "tp", "entry", "sl")}
        check(f"{tag} 3 ทิศ/TP เริ่มต้น เหมือนกด Activate เดิม (act_side · tp = ขอบใกล้ TP zone · entry/sl)", auto == manual and auto["act_side"] == "Long" and auto["tp"] == 2440, json.dumps([auto, manual]))

        # ── 4 ถอนเงื่อนไข → ยกเลิกเอง
        tpnum(page, "inval", "")
        check(f"{tag} 4 ลบ Invalidation หลัง active → active:false", active_ids(page) == [] and page.locator(f'{root} [data-ac-on]').count() == 0, json.dumps(cd(page)))
        check(f"{tag} 4 ยกเลิกเอง ไม่ลบค่าอื่น (steps/Pullback/TP ยังอยู่)", cd(page)["steps"] == {"brk": True, "vol": True, "pb": True} and cd(page)["tp_from"] == 2440 and cd(page)["pb_from"] == 2405, json.dumps(cd(page)))
        tpnum(page, "inval", 2390)
        check(f"{tag} 4 กรอก Invalidation กลับ → Activate อีกครั้ง", active_ids(page) == ["c1"])
        tpnum(page, "tp_from", "")
        check(f"{tag} 4 ลบ TP (ทั้ง 2 ช่องว่าง) → active:false", active_ids(page) == [], json.dumps(cd(page)))
        tpnum(page, "tp_to", 2441)
        check(f"{tag} 4 TP ช่อง 'ถึง' ช่องเดียวก็พอ → Activate", active_ids(page) == ["c1"])
        edit_open(page, "pb")
        pbf(page, "")
        check(f"{tag} 4 ลบช่อง Pullback ที่พิมพ์เอง → pb_from/pb_to null · กลับไปตามกรอบ Break (ยัง active · ติ๊กยังอยู่ · AC2: ไม่หลุดเพราะมีค่าเริ่ม)", cd(page)["pb_from"] is None and cd(page)["steps"]["pb"] is True and active_ids(page) == ["c1"], json.dumps(cd(page)))
        edit_open(page, "break")
        lvl(page, "vol", "")
        check(f"{tag} 4 ลบตัวเลข Break Vol → ติ๊ก Vol หลุด · active:false (ไม่มีค่า Pullback เริ่มแล้วด้วย)", active_ids(page) == [] and cd(page)["steps"]["vol"] is False and cd(page)["steps"]["pb"] is False, json.dumps(cd(page)))
        lvl(page, "vol", 2410)
        check(f"{tag} 4 กรอก Break Vol กลับ → ยังไม่ Activate (ต้องติ๊กใหม่)", active_ids(page) == [], json.dumps(cd(page)))
        tick(page, "vol"); tick(page, "pb")
        check(f"{tag} 4 ติ๊กกลับครบ → Activate", active_ids(page) == ["c1"], json.dumps(cd(page)))
        edit_open(page, "pb"); tick(page, "pb")
        check(f"{tag} 4 เอาติ๊ก Pullback ออก → active:false · บรรทัด 'ขาด: ติ๊ก Pullback'", active_ids(page) == [] and txt(page, f'{ac(page)} [data-ac-miss]') == "ขาด: ติ๊ก Pullback", txt(page, f'{ac(page)} [data-ac-miss]'))

        # ── 10 เลย์เอาต์
        fresh(page, bp_idea([cond(steps=(1, 1, 0), pb=(2405, 2412), tp=(2440, 2450), inval=2390)]))
        js(page, "()=>satAcEditOpen('iD','c1','break')"); page.wait_for_timeout(300)   # เปิดแถวกรอก Break ทั้งสอง (ไม่พึ่งสถานะ UI ค้างจากเคสก่อน)
        m = page.evaluate("""(s)=>{ const cs=[...document.querySelectorAll(s+' [data-step]')].map(e=>e.getBoundingClientRect()), seg=[...document.querySelectorAll(s+' [data-ac-tf] button')].map(e=>e.getBoundingClientRect().height);
            const tops = cs.map(r=>Math.round(r.top)), hs = cs.map(r=>r.height);
            return {stacked: tops.every((t,i)=>i===0 || t>tops[i-1]), minH: Math.min(...hs, ...seg),
              fonts: [...document.querySelectorAll(s+' input')].map(e=>parseFloat(getComputedStyle(e).fontSize)), W: innerWidth}; }""", ac(page))
        check(f"{tag} 10 ช่องติ๊ก 3 ช่องอยู่คนละแถว เรียงจากบนลงล่าง (Break Price → Break Vol → Pullback)", m["stacked"], json.dumps(m))
        check(f"{tag} 10 ช่องติ๊ก/ปุ่ม TF สูง ≥ 30px · ช่องกรอกทุกช่อง font ≥ 16px", m["minH"] >= 29.5 and all(f >= 16 for f in m["fonts"]) and len(m["fonts"]) == 6, json.dumps(m))
        bad = overflow(page, [root, "#satV3Panel", ac(page)])
        check(f"{tag} 10 ไม่ล้นแนวนอน", not bad, json.dumps(bad))
        check(f"{tag} 10 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


# ───────────────────────── 5-7 · 9 ─────────────────────────
def logic_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, page, ce, pe = sat_page(pw, w, h)
    try:
        # ── 5 สองเงื่อนไข · สลับ
        full = dict(steps=(1, 1, 1), pb=(2405, 2412), tp=(2440, 2450), inval=2390)
        fresh(page, bp_idea([cond("c1", "A @ 2400", active=True, **full), cond("c2", "B @ 2380", steps=(1, 1, 0), pb=(2380, 2385), tp=(2430, 2440), inval=2370)]))
        check(f"{tag} 5 เริ่ม: ข้อ 1 active ข้อเดียว", active_ids(page) == ["c1"])
        page.locator('.ui-plan[data-id="iD"] .ui-oth-t').click(); page.wait_for_timeout(250)
        check(f"{tag} 5 กางเงื่อนไขอื่น → แก้ติ๊ก/Pullback/TP ของข้อ 2 ได้ในที่ (ไม่ต้องยกเลิกข้อ 1)", page.locator(f'{ac(page, "c2")} [data-step=pb]').count() == 1)
        tick(page, "pb", "c2")
        check(f"{tag} 5 ข้อ 2 ครบ → active ย้ายไปข้อ 2 · ข้อ 1 active:false", active_ids(page) == ["c2"] and cd(page, "c1")["active"] is False, json.dumps(doc_of(page)["conditions"], ensure_ascii=False))
        check(f"{tag} 5 ข้อความเล็ก 'สลับไปเงื่อนไข #2'", "สลับไปเงื่อนไข #2" in txt(page, '.ui-plan[data-id="iD"]'), txt(page, '.ui-plan[data-id="iD"]'))
        check(f"{tag} 5 สลับแล้ว ข้อ 1 ไม่ถูกแก้ข้อมูล (steps/Pullback/TP/Inval ครบเดิม)", cd(page, "c1")["steps"] == {"brk": True, "vol": True, "pb": True} and cd(page, "c1")["inval"] == 2390 and cd(page, "c1")["pb_from"] == 2405, json.dumps(cd(page, "c1")))
        check(f"{tag} 5 TP เริ่มต้นตามข้อ 2 = min(2430,2440)=2430", doc_of(page)["tp"] == 2430, str(doc_of(page)["tp"]))

        # ── 6 แผนเก่า
        old = P51.idea_doc(iid="iD", act=True)
        old["entry"], old["sl"], old["tp"] = 2410, 2400, 2425
        old["accts"] = {"main": {"broker": "XM"}}
        fresh(page, old)
        check(f"{tag} 6 แผนเก่า (ไม่มี kind/steps · active:true) → ติ๊กครบ 3 (บรรทัดสรุป 2 บรรทัด) · ยัง active · ไม่ migrate (ไม่มี steps ใน DB)",
              len(sums(page)) == 2 and active_ids(page) == ["c1"] and "steps" not in cd(page) and "kind" not in cd(page), json.dumps([sums(page), cd(page)]))
        c1 = P51.calc(page, old)
        js(page, "()=>{ render(); satV3Render(); }"); page.wait_for_timeout(300)
        c2 = P51.calc(page, old)
        check(f"{tag} 6 คำนวณ lot / R:R เท่าเดิม (ready · lot มีค่า · R:R ผ่าน)", c1 == c2 and c1["ready"] is True and c1["lot"] and not c1["rr"], json.dumps([c1, c2]))
        tpnum(page, "tp_to", 2441)
        check(f"{tag} 6 แก้ค่าบนข้อเก่า → ยัง active", active_ids(page) == ["c1"], json.dumps(cd(page)))
        edit_open(page, "pb")
        pbf(page, "2400-2410")
        check(f"{tag} 6 กรอก Pullback ในข้อเก่า → แปลงเป็นรูปใหม่ (kind:'bp' · steps ครบ · legacy_ok) · AC2: ยัง active (เดิม AC1: ขาด Inval → หลุด · ตอนนี้ข้อเก่าไม่หลุดเมื่อแก้ตัวเลข)",
              cd(page).get("kind") == "bp" and cd(page)["steps"] == {"brk": True, "vol": True, "pb": True} and cd(page)["pb_from"] == 2400 and cd(page).get("legacy_ok") is True and active_ids(page) == ["c1"], json.dumps(cd(page)))

        # ── 7 กติกาเดิมยังบล็อก
        def done(**kw):
            return bp_idea([cond("c1", active=True, steps=(1, 1, 1), pb=(2405, 2412), tp=kw.get("tpz", (2425, 2440)), inval=2390)],
                           entry=kw.get("entry", 2410), sl=kw.get("sl", 2400), tp=kw.get("tp", 2425), broker="XM")
        P51.set_news(page, [])
        P51.set_clock(page, CLK)
        c = P51.calc(page, done())
        check(f"{tag} 7 ครบ + R:R 1.5 → ready", c["ready"] is True and not c["rr"], json.dumps(c, ensure_ascii=False))
        c = P51.calc(page, done(tp=2420))
        check(f"{tag} 7 R:R 1.0 (< 1.5) → ยังบล็อก", c["ready"] is False and c["rr"] and "ต่ำกว่า 1.5" in c["rr"], json.dumps(c, ensure_ascii=False))
        i = done(tp=2420); fresh(page, i)
        n0 = P51.n_trades(page)
        js(page, "()=>{ satV3SaveSlot('iD','main'); satV3SaveReadyAccounts('iD'); }"); page.wait_for_timeout(400)
        check(f"{tag} 7 R:R ต่ำ → บันทึก order ไม่ได้ (ไม่มีไม้ใหม่)", P51.n_trades(page) == n0, f"{n0}→{P51.n_trades(page)}")
        P51.set_news(page, [{"date": "2026-10-01", "kind": "CPI", "time": "19:30"}])
        P51.set_clock(page, "2026-10-01T11:40:00Z")
        c = P51.calc(page, done())
        check(f"{tag} 7 ช่วงงดข่าว CPI → ยังบล็อก", c["ready"] is False and c["news"] and "งดเปิดไม้ใหม่" in c["news"], json.dumps(c, ensure_ascii=False))
        P51.set_news(page, []); P51.set_clock(page, CLK)
        js(page, "()=>satwWrite('XAUUSD', {bias:'Short', support:[2300], resistance:[2500], invalidation:2550})"); page.wait_for_timeout(300)
        c = P51.calc(page, done())
        check(f"{tag} 7 PF1 — Strategy bias เก่า Short · แผน Long → ไม่บล็อก (ready) · ไม่มีเหตุผลสวน Bias", c["ready"] is True and not any("สวน Bias" in x for x in c["warns"]), json.dumps(c, ensure_ascii=False))
        check(f"{tag} 7 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


# ───────────────────────── 8 Today ─────────────────────────
def today_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, context, page, ce, pe, dialogs = P39.launch(pw, w, h, doc=P38.doc38(clean=True), clean=True, iso="2026-10-14T03:00:00Z")
    try:
        def state(conds, **kw):
            js(page, "()=>{ switchTab('today'); }")
            if conds is not None:
                P51.put_idea(page, bp_idea(conds, **kw))
            js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(450)
            return {"b": P38.kinds(page, "b"), "a": P38.kinds(page, "a"), "r": P38.kinds(page, "r")}
        P51.set_clock(page, "2026-10-14T03:00:00Z")
        s = state(None)
        check(f"{tag} 8 ไม่มีแผน → ไม่มีแถวรอ Pullback (ปกติ = เงียบ)", "sat-pbwait" not in s["a"] + s["b"] + s["r"], json.dumps(s))
        s = state([cond(steps=(1, 0, 0), pb=(2410, 2420))])
        check(f"{tag} 8 Break ไม่ครบ 2 ติ๊ก → ไม่มีแถว", "sat-pbwait" not in s["a"] + s["b"] + s["r"], json.dumps(s))
        s = state([cond(steps=(1, 1, 0), pb=(2410, 2420))])
        t = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="sat-pbwait"]').first.text_content()) if page.locator('.tdRow[data-kind="sat-pbwait"]').count() else ""
        check(f"{tag} 8 Break ครบ 2 ติ๊ก ไม่มี Pullback → แถว 'XAU รอ Pullback เข้า zone 2,410–2,420' (1 แถว)", s["b"].count("sat-pbwait") == 1 and "XAU" in t and "รอ Pullback เข้า zone" in t and "2410" in t.replace(",", "") and "2420" in t.replace(",", ""), json.dumps(s) + t)
        shot(page, f"ac1-today-wait-{sfx}.png")
        if w < 600:
            bad = overflow(page, [".tdRow[data-kind='sat-pbwait']", "#todayPanel"])
            check(f"{tag} 8 390px แถวไม่ล้นแนวนอน", not bad, json.dumps(bad))
        s = state([cond(steps=(1, 1, 0), pb=(2410, 2420)), cond("c2", "B", steps=(1, 1, 0), pb=(2380, 2390))])
        check(f"{tag} 8 สองเงื่อนไขรอ Pullback ในสินค้าเดียว → ยัง 1 แถว", s["b"].count("sat-pbwait") == 1, json.dumps(s))
        js(page, "()=>satAcStep('iD','c1','pb',true)"); js(page, "()=>satAcStep('iD','c2','pb',true)"); page.wait_for_timeout(350)
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(400)
        s = {"b": P38.kinds(page, "b"), "a": P38.kinds(page, "a"), "r": P38.kinds(page, "r")}
        check(f"{tag} 8 ติ๊ก Pullback แล้ว → แถวหาย", "sat-pbwait" not in s["a"] + s["b"] + s["r"], json.dumps(s) + json.dumps(doc_of(page)["conditions"], ensure_ascii=False)[:300])
        check(f"{tag} 8 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


# ───────────────────────── 9 สินค้าเพิ่มเอง ─────────────────────────
def custom_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    doc = P38.doc38(clean=True); P55.with_custom(P55.XAG)(doc)
    browser, context, page, ce, pe, dialogs = P39.launch(pw, w, h, doc=doc, clean=True, iso=CLK, pick=['XAUUSD', 'BTCUSD', 'XAG'])   # WA1fix: XAG ต้องอยู่ใน pick สัปดาห์นี้
    try:
        p5.goto_sat(page); p36.clean(page, "Long"); P37.go_sat(page)
        js(page, "()=>satwWrite('XAG', {bias:'Long', support:[28], resistance:[33], invalidation:27})"); page.wait_for_timeout(300)
        i = bp_idea([cond("c1", "Break & Pullback @ 30", steps=(1, 1, 0), pb=(29.5, 30))], asset="XAG", entry=30, sl=29, tp=None, broker="XM", iid="iX")
        P51.fresh(page, i); page.wait_for_timeout(300)
        check(f"{tag} 9 XAG (สินค้าเพิ่มเอง): ครบ 3 ขั้น (Break Price+Vol ติ๊กแล้ว = 1 บรรทัดสรุป · Pullback รอติ๊ก) ไม่มีปุ่ม Activate", page.locator(f'{ac(page, "c1", "iX")} .ui-acs[data-sum="break"]').count() == 1 and page.locator(f'{ac(page, "c1", "iX")} [data-step="pb"]').count() == 1 and page.locator('.ui-plan[data-id="iX"] .ui-cond-act').count() == 0)
        fill(page, f'.ui-plan[data-id="iX"] [data-cond="c1"] .ui-cond-nums input[onchange*="\'tp_from\'"]', 31.5)
        fill(page, f'.ui-plan[data-id="iX"] [data-cond="c1"] .ui-cond-nums input[onchange*="\'inval\'"]', 28.5)
        tick(page, "pb", "c1", "iX")
        check(f"{tag} 9 XAG ครบ → Activate เอง · TP เริ่มต้น 31.5 · act_side Long", active_ids(page, "iX") == ["c1"] and doc_of(page, "iX")["act_side"] == "Long", json.dumps(doc_of(page, "iX"), ensure_ascii=False)[:400])
        js(page, "()=>satV3IdeaWrite('iX',{macro_note:'เหตุผลทดสอบ'})"); page.wait_for_timeout(250)   # WA1: Asset นอก Macro ต้องมีเหตุผลก่อนบันทึก order
        c = P55.calc(page, doc_of(page, "iX"))
        check(f"{tag} 9 XAG คำนวณ lot ได้ · ready (R:R 1.5)", c["lot"] and c["ready"] is True, json.dumps(c, ensure_ascii=False))
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def static_tests():
    s = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("S1 SAT_COND_STEPS เป็นค่าคงที่ที่เดียว (3 ขั้น: brk · vol · pb)", len(re.findall(r"const SAT_COND_STEPS\s*=", s)) == 1 and "{k:'brk'" in s and "{k:'vol'" in s and "{k:'pb'" in s)


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            ui_tests(pw, w, h, label)
            logic_tests(pw, w, h, label)
            today_tests(pw, w, h, label)
            custom_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 60 / AC1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
