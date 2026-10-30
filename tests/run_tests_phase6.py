#!/usr/bin/env python3
"""7D.5 — ปรับการ์ดเงื่อนไข (แผน 2 ขั้น): แถวพับ "รอเงื่อนไข" 1 แถวต่อเงื่อนไข · ยกเลิก = ซ่อน ไม่ลบ ·
ขั้นหน้างานย่อเหลือบรรทัดสรุป · แก้คำได้ทุกที่ · รายการปุ่มลัดใช้ร่วมทุก asset (satConfig/conditionTemplates)

ไฟล์แยก (ไม่แตะเคสรอบก่อน) — รันที่ 1440px และ 430px · ทดสอบผ่าน DOM จริง (คลิก/พิมพ์) เป็นหลัก
ภาพเก็บที่ tests/screenshots/7d5-*.png

การใช้งาน: CHROMIUM_PATH=".../Google Chrome" python3 run_tests_phase6.py
"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base          # launch_page (login + mock Firebase)
import run_tests_phase5 as p5            # goto_sat / fill_blur / reload_keep_state / set_bias_dom

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots")
os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def text_of(page, sel):
    return norm(page.evaluate("(s)=>{ const e=document.querySelector(s); return e ? e.innerText : ''; }", sel))


def count(page, sel):
    return page.locator(sel).count()


def idea(page, iid):
    return page.evaluate("(i)=>sat7dIdea(i)", iid)


def cond(page, iid, cid):
    return next((c for c in (idea(page, iid) or {}).get("conditions", []) if c["id"] == cid), None)


def setup_strategy(page, asset, bias):
    v = "up" if bias == "L" else "down"
    page.evaluate("([a,v])=>satwWrite(a, {comps:{trend:{v:v},macro:{v:v}}, invalidation:100})", [asset, v])
    page.wait_for_timeout(120)
    p5.set_bias_dom(page, asset, bias)


def new_plan(page, asset):
    p5.ensure_pick(page, asset)
    before = set(page.evaluate("() => satIdeasList.map(x=>x.id)"))
    # PV2a: ปุ่ม [+ แผน] สร้างแผนฟอร์ม v2 แล้ว (ดู phase77) — เคสนี้ทดสอบการ์ดเดิม (kind bp) จึงสร้างผ่าน satV3NewPlan ตรง ๆ
    page.evaluate("(a) => satV3NewPlan(a)", asset)
    page.wait_for_timeout(250)
    return next(i for i in page.evaluate("() => satIdeasList.map(x=>x.id)") if i not in before)


def add_cond_typed(page, iid, sc_text, typed, tp_from=None, tp_to=None, inval=None):
    """AC2: ไม่มีปุ่มลัด/ช่องข้อความ — เงื่อนไขว่างที่มาตั้งแต่สร้างแผนถูกใช้ก่อน (ตั้ง text ด้วยฟังก์ชัน) · ข้อถัดไปเพิ่มด้วย satV3CondAdd
    ข้อความ = ข้อความปุ่มลัดเดิม + เว้นวรรค + ที่พิมพ์ (เทียบเท่าเดิม) · TP zone/Inval กรอกผ่านช่องจริง คืน id เงื่อนไข"""
    before = idea(page, iid)["conditions"]
    text = ((sc_text + " ") if sc_text else "") + typed
    empty = [c for c in before if c["id"] and not (c.get("text") or "").strip() and c.get("status") != "cancelled" and c.get("brk_px") is None]
    if empty and len(before) == 1:
        cid = empty[0]["id"]
        page.evaluate("([i,c,t])=>satV3CondEdit(i,c,'text',t)", [iid, cid, text])
    else:
        page.evaluate("([i,t])=>satV3CondAdd(i,t)", [iid, text])
        cid = next(c["id"] for c in idea(page, iid)["conditions"] if c["id"] not in [x["id"] for x in before])
    page.wait_for_timeout(250)
    for f, v in (("tp_from", tp_from), ("tp_to", tp_to), ("inval", inval)):
        if v is not None:
            p5.fill_blur(page, f'.ui-plan[data-id="{iid}"] .ui-cond[data-cond="{cid}"] input[onchange*="\'{f}\'"]', str(v))
    return cid


def run(pw, width, height, label):
    tag = f"[{ENGINE}/{label}]"
    px = label.replace("px", "")
    browser, context, page, console_errors, page_errors = base.launch_page(pw, width, height, base.DEFAULT_INDEX)
    p5.goto_sat(page)

    # ═════════ ปุ่มลัด: ไม่มีเอกสาร = ค่าเริ่มต้น ไม่ error ═════════
    tpl0 = page.evaluate("() => satV3CondTemplates().map(t=>t.text)")
    check(f"{tag} ปุ่มลัด: ไม่มีเอกสาร conditionTemplates → ใช้ค่าเริ่มต้น 2 รายการ (ไม่ error)",
          tpl0 == ["Break & Pullback @ ", "Swing back in demand zone @ "], json.dumps(tpl0))

    # ═════════ 1) แถวพับ "รอเงื่อนไข" ═════════
    setup_strategy(page, "XAUUSD", "S")
    X = new_plan(page, "XAUUSD")
    A = add_cond_typed(page, X, "Break & Pullback @", "4600", 4550, 4500, 4650)
    B = add_cond_typed(page, X, "Swing back in demand zone @", "4520", 4480, 4450)
    ca = cond(page, X, A)
    check(f"{tag} เงื่อนไขใหม่เก็บ saved:false จนกว่าจะบันทึกแผน", ca["saved"] is False and ca.get("status") is None, json.dumps(ca))
    page.click(f'.ui-plan[data-id="{X}"] .ui-plan-cta .ui-btn-pri:has-text("บันทึกแผน")')
    page.wait_for_timeout(250)
    ix = idea(page, X)
    check(f"{tag} [บันทึกแผน] → planned=true · ทุกข้อ saved:true · ไม่สร้างไม้",
          ix["planned"] is True and all(c["saved"] is True for c in ix["conditions"]) and not any((ix.get("accts") or {}).values()))
    head = text_of(page, f'.ui-wait[data-id="{X}"] .ui-wc-h')
    check(f"{tag} แถวพับ: หัว 'XAUUSD Short · รอเงื่อนไข'", head.startswith("XAUUSD Short · รอเงื่อนไข"), head)
    check(f"{tag} แถวพับ: 1 แถวต่อเงื่อนไข = 2 แถว", count(page, f'.ui-wait[data-id="{X}"] .ui-wc') == 2)
    rowA = text_of(page, f'.ui-wc[data-cond="{A}"]')
    rowB = text_of(page, f'.ui-wc[data-cond="{B}"]')
    check(f"{tag} แถว A: ข้อความ · TP 4550–4500 · Inval 4650 + [ยกเลิก] (AC1: ไม่มีปุ่ม Activate แล้ว)",
          "Break & Pullback @ 4600" in rowA and "TP 4550–4500" in rowA and "Inval 4650" in rowA and "Activate" not in rowA and "ยกเลิก" in rowA, rowA)
    check(f"{tag} แถว B: ไม่มี Inval → '—'", "TP 4480–4450" in rowB and "Inval —" in rowB, rowB)
    check(f"{tag} แถวพับไม่มีช่อง Entry/SL และไม่มีการ์ดกาง", count(page, ".ui-plan-nums") == 0 and count(page, ".ui-pgrid .ui-plan") == 0)

    # ข้อความยาว → ตัดด้วย … (CSS ellipsis) · title เก็บข้อความเต็ม
    long_txt = "Break & Pullback @ 4600 ยืนยันด้วยแท่งเทียน 1H ปิดใต้แนวรับเดิมพร้อมวอลุ่มสูงกว่าค่าเฉลี่ยสามเท่า และ retest ไม่ผ่านแนวต้านเดิม " * 4
    page.evaluate("([i,c,t])=>satV3CondEdit(i,c,'text',t)", [X, B, long_txt])
    page.evaluate("() => satV3Render()")
    page.wait_for_timeout(150)
    tr = page.evaluate(f"""() => {{ const e=document.querySelector('.ui-wc[data-cond="{B}"] .ui-wc-t'); const cs=getComputedStyle(e);
        return {{ov: cs.textOverflow, ws: cs.whiteSpace, trunc: e.scrollWidth > e.clientWidth, title: e.title}}; }}""")
    check(f"{tag} ข้อความยาวเกิน → ตัดด้วย … (text-overflow:ellipsis · ถูกตัดจริง) · title = ข้อความเต็ม",
          tr["ov"] == "ellipsis" and tr["ws"] == "nowrap" and tr["trunc"] and tr["title"] == long_txt, json.dumps(tr))
    lay = page.evaluate(f"""() => {{ const t=document.querySelector('.ui-wc[data-cond="{A}"] .ui-wc-t').getBoundingClientRect();
        const b=document.querySelector('.ui-wc[data-cond="{A}"] .ui-wc-b').getBoundingClientRect(); return {{tb:t.bottom, bt:b.top, tl:t.left, bl:b.left, bw:b.width}}; }}""")
    if width <= 480:
        check(f"{tag} ≤480px: ปุ่มลงแถวล่างของแถวนั้น", lay["bt"] >= lay["tb"] - 1, json.dumps(lay))
    else:
        check(f"{tag} >480px: ปุ่มอยู่แถวเดียวกับข้อความ (ขวา)", lay["bt"] < lay["tb"] and lay["bl"] > lay["tl"], json.dumps(lay))
    page.evaluate("([i,c,t])=>satV3CondEdit(i,c,'text',t)", [X, B, "Swing back in demand zone @ 4520"])
    page.evaluate("() => satV3Render()")
    page.wait_for_timeout(120)
    page.locator(f'.ui-wait[data-id="{X}"]').screenshot(path=os.path.join(SHOTS, f"7d5-wait-{px}.png"))

    # แตะข้อความ → กางการ์ดเพื่อแก้ข้อนั้น (โฟกัสช่องข้อความข้อนั้น)
    page.click(f'.ui-wc[data-cond="{B}"] .ui-wc-t')
    page.wait_for_timeout(200)
    foc = page.evaluate("() => { const a=document.activeElement; const c=a && a.closest ? a.closest('[data-cond]') : null; return a && c ? [c.dataset.cond, a.dataset.acPx] : null; }")
    check(f"{tag} แตะข้อความ → กางการ์ด + โฟกัสช่อง Break Price ของข้อนั้น (B) (AC2: ไม่มีช่องข้อความ)", count(page, ".ui-pgrid .ui-plan") == 1 and foc == [B, "brk"], str(foc))
    page.evaluate("() => document.activeElement.blur()")
    page.wait_for_timeout(100)
    page.click(f'.ui-plan[data-id="{X}"] .ui-plan-cta .ui-btn:has-text("พับกลับ")')
    page.wait_for_timeout(200)
    check(f"{tag} พับกลับ → แถวรอเงื่อนไขกลับมา", count(page, f'.ui-wait[data-id="{X}"]') == 1 and count(page, ".ui-pgrid .ui-plan") == 0)

    # ═════════ 2) Activate จากแถว → กางการ์ดที่ขั้นหน้างาน โดยเลือกข้อนั้นไว้แล้ว ═════════
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [X, A])   # AC1: เรียกตัวทำงานเดิมตรง ๆ
    page.wait_for_timeout(250)
    ix = idea(page, X)
    check(f"{tag} [Activate] จากแถว → การ์ดกางที่ขั้นหน้างาน · ข้อ A เป็นข้อ active ข้อเดียว",
          count(page, ".ui-pgrid .ui-plan") == 1 and [c["id"] for c in ix["conditions"] if c["active"]] == [A] and count(page, ".ui-plan-nums") == 1)
    check(f"{tag} Short: TP เริ่มต้น = ขอบใกล้ของ TP zone ข้อ A = max(4550,4500) = 4550", ix["tp"] == 4550, str(ix["tp"]))
    summ = text_of(page, "[data-ac-bar]")
    check(f"{tag} ขั้นหน้างาน: แถบ '● Active · 4H' + 'TP จาก–ถึง · Inval' (AC2: แทนบรรทัด ✅ ข้อความ · ✎ · [ยกเลิก Activate])",
          summ.startswith("● Active · 4H") and "TP 4,550–4,500" in summ and "Inval 4,650" in summ and "ยกเลิก Activate" not in summ and count(page, ".ui-cs-off") == 0, summ)
    others = text_of(page, ".ui-cond-oth")
    check(f"{tag} เงื่อนไขอื่นย่อเหลือ 1 บรรทัด '▸ เงื่อนไขอื่นรออยู่ 1 ข้อ' (ยังไม่กางแถว)",
          "เงื่อนไขอื่นรออยู่ 1 ข้อ" in others and others.startswith("▸") and count(page, ".ui-cond-oth .ui-wc") == 0, others)
    check(f"{tag} ขั้นหน้างาน: ซ่อนแถวปุ่มลัด + 'เพิ่มเอง' + ไม่มีรายการเงื่อนไขเต็ม",
          count(page, ".ui-plan .ui-cond-sc") == 0 and count(page, ".ui-plan .ui-chips .ui-cond-sc") == 0 and count(page, ".ui-plan .ui-cond-act") == 0
          and "+ เพิ่มเอง" not in text_of(page, ".ui-conds"))
    check(f"{tag} มี TP zone → ไม่ขึ้นคำเตือน 'ยังไม่ใส่ TP zone'", count(page, ".ui-cond-warn") == 0)
    page.locator(".ui-pcell").first.screenshot(path=os.path.join(SHOTS, f"7d5-active-{px}.png"))

    # แตะ ▸ → กางเป็นแถวสั้น [ใช้ข้อนี้] [ยกเลิก] → ใช้ข้อนี้ = สลับได้
    page.click(".ui-oth-t")
    page.wait_for_timeout(150)
    orow = text_of(page, f'.ui-cond-oth .ui-wc[data-cond="{B}"]')
    check(f"{tag} แตะ ▸ → แถวสั้นของข้อ B พร้อม [ยกเลิก] (AC1: ไม่มีปุ่ม [ใช้ข้อนี้] แล้ว)", "Swing back in demand zone @ 4520" in orow and "ใช้ข้อนี้" not in orow and "ยกเลิก" in orow, orow)
    page.locator(".ui-pcell").first.screenshot(path=os.path.join(SHOTS, f"7d5-active-others-{px}.png"))
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [X, B])   # AC1
    page.wait_for_timeout(250)
    ix = idea(page, X)
    check(f"{tag} [ใช้ข้อนี้] → สลับเป็น B (active มีข้อเดียว) · TP ตามข้อ B = max(4480,4450) = 4480",
          [c["id"] for c in ix["conditions"] if c["active"]] == [B] and ix["tp"] == 4480, json.dumps([ix["tp"], [c["active"] for c in ix["conditions"]]]))
    check(f"{tag} หลังสลับ: สรุปเป็นข้อ B · ข้อ A ย้ายไปอยู่ 'เงื่อนไขอื่น'",
          page.evaluate("() => document.querySelector('[data-ac-bar]').dataset.cond") == B and "TP 4,480–4,450" in text_of(page, "[data-ac-bar]") and "เงื่อนไขอื่นรออยู่ 1 ข้อ" in text_of(page, ".ui-cond-oth"))

    # ✎ แก้ในที่ (ข้อที่ Activate) → แก้ข้อความ/TP zone ได้ · TP ที่ยังเป็นค่าเริ่มต้นตาม
    page.click("[data-ac-bar]")   # AC2: แตะแถบ Active แทนปุ่ม ✎
    page.wait_for_timeout(150)
    page.evaluate("([i,c])=>satV3CondEdit(i,c,'text','Swing back in demand zone @ 4525')", [X, B])   # AC2: ไม่มีช่องข้อความ — แก้ผ่านฟังก์ชัน
    p5.fill_blur(page, f'.ui-cond-edit[data-cond-edit="{B}"] input[onchange*="\'tp_from\'"]', "4470")
    ix = idea(page, X)
    check(f"{tag} ✎ แก้ในที่: ข้อความ + TP zone แก้ได้ · TP เริ่มต้นตามขอบใกล้ใหม่ (max(4470,4450)=4470)",
          cond(page, X, B)["text"] == "Swing back in demand zone @ 4525" and ix["tp"] == 4470, json.dumps([cond(page, X, B), ix["tp"]]))
    page.click(f'.ui-cond-edit[data-cond-edit="{B}"] .ui-btn:has-text("เสร็จแล้ว")')
    page.wait_for_timeout(150)
    check(f"{tag} ✎ เสร็จแล้ว → กลับเป็นแถบ Active ที่ TP ใหม่ (AC2: ไม่แสดงข้อความ)", "TP 4,470–4,450" in text_of(page, "[data-ac-bar]") and count(page, ".ui-cond-edit") == 0)

    # [ยกเลิก Activate] → กลับไปรายการ (มีปุ่มลัด/เพิ่มเอง กลับมา)
    page.evaluate("([i,c])=>satV3CondActivate(i,c,false)", [X, B])   # AC2: ไม่มีปุ่ม [ยกเลิก Activate] — เรียกตัวทำงานเดิมตรง ๆ
    page.wait_for_timeout(200)
    ix = idea(page, X)
    check(f"{tag} ยกเลิก Activate → ไม่มีข้อ active · ไม่มีช่อง Entry/SL · กลับไปรายการ 2 ข้อ (AC2: ไม่มีชิปปุ่มลัด) · ไม่ลบเงื่อนไขใด",
          not any(c["active"] for c in ix["conditions"]) and count(page, ".ui-plan-nums") == 0 and count(page, ".ui-plan .ui-cond-sc") == 0 and count(page, ".ui-plan .ui-cond[data-cond]") == 2
          and len(ix["conditions"]) == 2, json.dumps([c["active"] for c in ix["conditions"]]))
    page.click(f'.ui-plan[data-id="{X}"] .ui-plan-cta .ui-btn:has-text("พับกลับ")')
    page.wait_for_timeout(200)

    # ═════════ 3) ยกเลิกเงื่อนไข = ซ่อน ไม่ลบ ═════════
    page.click(f'.ui-wc[data-cond="{B}"] .ui-wc-cancel')
    page.wait_for_timeout(250)
    cb = cond(page, X, B)
    check(f"{tag} [ยกเลิก] ข้อที่บันทึกแผนแล้ว → status:'cancelled' + cancelled_at · ข้อมูลยังอยู่ (ไม่ลบ)",
          cb and cb["status"] == "cancelled" and cb.get("cancelled_at") and cb["text"] == "Swing back in demand zone @ 4525" and cb["tp_from"] == 4470,
          json.dumps(cb))
    check(f"{tag} ข้อที่ยกเลิก → หายจากแถวพับ (เหลือ 1 แถว)", count(page, f'.ui-wait[data-id="{X}"] .ui-wc') == 1 and count(page, f'.ui-wc[data-cond="{B}"]') == 0)
    check(f"{tag} ลิงก์ 'ดูที่ยกเลิก (1)' ขึ้นบนแถว", "ดูที่ยกเลิก (1)" in text_of(page, f'.ui-wait[data-id="{X}"]'))
    p5.reload_keep_state(page)
    check(f"{tag} reload → ยังซ่อนอยู่ (แถวเหลือ 1) · ข้อมูลยังอยู่ · ลิงก์ 'ดูที่ยกเลิก (1)' ยังขึ้น",
          count(page, f'.ui-wait[data-id="{X}"] .ui-wc') == 1 and cond(page, X, B)["status"] == "cancelled" and "ดูที่ยกเลิก (1)" in text_of(page, f'.ui-wait[data-id="{X}"]'))
    page.click(f'.ui-wait[data-id="{X}"] .ui-link:has-text("ดูที่ยกเลิก")')
    page.wait_for_timeout(150)
    ci = page.evaluate(f"() => {{ const e=document.querySelector('.ui-cancd-i[data-cond=\"{B}\"]'); return e ? {{t:e.innerText, op:+getComputedStyle(e).opacity, btn:e.querySelectorAll('button,input').length}} : null; }}")
    check(f"{tag} 'ดูที่ยกเลิก' → แสดงแบบจาง (opacity<1) อ่านอย่างเดียว (ไม่มีปุ่ม/ช่องกรอก) พร้อมข้อความ + TP + วันที่ยกเลิก",
          ci and ci["op"] < 1 and ci["btn"] == 0 and "4525" in ci["t"] and "TP 4470–4450" in ci["t"] and __import__("re").search(r"ยกเลิก \d{1,2} \S+", ci["t"]) is not None and "ยกเลิก 20" not in ci["t"], json.dumps(ci))   # CL1: วันที่ยกเลิกเป็นวันที่ไทยสั้น (เช่น "29 ก.ย.") ไม่ใช่ ISO
    page.evaluate("(i)=>document.querySelector(`.ui-wait[data-id=\"${i}\"]`).scrollIntoView({block:'center'})", X)
    page.wait_for_timeout(150)
    page.locator(f'.ui-wait[data-id="{X}"]').screenshot(path=os.path.join(SHOTS, f"7d5-cancelled-{px}.png"))

    # ✕ ข้อที่ยังไม่เคยบันทึก = ลบจริง · ✕ ข้อที่บันทึกแล้ว (ในการ์ดที่กาง) = ซ่อน
    page.click(f'.ui-wait[data-id="{X}"] .ui-btn:text-is("เปิด")')
    page.wait_for_timeout(200)
    n_before = len(idea(page, X)["conditions"])
    T = add_cond_typed(page, X, None, "พิมพ์ผิด")
    check(f"{tag} เพิ่มข้อใหม่หลังบันทึกแผน → saved:false (ยังไม่เคยบันทึก)", cond(page, X, T)["saved"] is False)
    page.click(f'.ui-plan[data-id="{X}"] .ui-cond[data-cond="{T}"] .ui-cond-x')
    page.wait_for_timeout(200)
    ix = idea(page, X)
    check(f"{tag} ✕ ข้อที่ยังไม่เคยบันทึก → ลบจริง (ไม่อยู่ในข้อมูล ไม่อยู่ในรายการที่ยกเลิก)",
          len(ix["conditions"]) == n_before and all(c["id"] != T for c in ix["conditions"]) and len(ix["conditions"]) == 2, json.dumps([c["id"] for c in ix["conditions"]]))
    C = add_cond_typed(page, X, None, "C no tp @ 4580")
    page.click(f'.ui-plan[data-id="{X}"] .ui-plan-cta .ui-btn:has-text("พับกลับ")')
    page.wait_for_timeout(200)
    check(f"{tag} พับการ์ด = ยืนยันข้อที่เพิ่มระหว่างกาง → saved:true", cond(page, X, C)["saved"] is True)

    # ═════════ 4) ข้อที่ไม่มี TP zone → เตือนส้ม แต่ยังบันทึก order ได้ · แก้ข้อความหลังบันทึก order ไม่กระทบไม้ ═════════
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [X, C])   # AC1
    page.wait_for_timeout(250)
    warn = page.evaluate("() => { const e=document.querySelector('.ui-cond-warn'); return e ? {t:e.innerText, c:getComputedStyle(e).color} : null; }")
    check(f"{tag} Activate ข้อที่ไม่มี TP zone → เตือน 'ยังไม่ใส่ TP zone' (สีเตือน ไม่ใช่สีข้อความปกติ)",
          warn and "ยังไม่ใส่ TP zone" in warn["t"], json.dumps(warn))
    check(f"{tag} ไม่มี TP zone → สรุปแสดง 'TP —' และ 'Inval —' (ข้อมูลขาด = —)", "TP — · Inval —" in text_of(page, "[data-ac-bar]"), text_of(page, "[data-ac-bar]"))
    root = f'.ui-plan[data-id="{X}"]'
    p5.fill_blur(page, f'{root} input[onchange*="\'entry\'"]', "4600")
    p5.fill_blur(page, f'{root} input[onchange*="\'sl\'"]', "4650")
    dis = page.evaluate(f"() => document.querySelector('{root} .ui-plan-cta .ui-btn-pri').disabled")
    check(f"{tag} ไม่มี TP zone และไม่มี TP แรก → ปุ่ม [บันทึก order] ปิด (ST1: R:R ขั้นต่ำ 1.5 ต้องมี TP แรก · เดิม: ยังกดได้)", dis is True)
    p5.fill_blur(page, f'{root} input[onchange*="\'tp\'"]', "4500")   # ST1: กรอก TP แรกเอง (ไม่มี zone) R:R 2.0
    dis = page.evaluate(f"() => document.querySelector('{root} .ui-plan-cta .ui-btn-pri').disabled")
    check(f"{tag} ไม่มี TP zone แต่กรอก TP แรกเอง (R:R 2.0) → ปุ่ม [บันทึก order] กดได้ (เตือน ไม่บล็อก — เจตนาเดิมคงอยู่)", dis is False)
    page.click(f'{root} .ui-plan-cta .ui-btn-pri:has-text("บันทึก order")')
    page.wait_for_timeout(300)
    tr = page.evaluate(f"() => {{ const i=sat7dIdea('{X}'); return ['main','fam'].map(a=>getBook(a).trades.find(t=>t.id===((i.accts||{{}})[a]||{{}}).trade_id)||null); }}")
    check(f"{tag} บันทึก order ได้จริง (ไม่มี TP zone): ไม้ status=plan · condition_id=C · tp_zone=null · entry_condition = สำเนาข้อความ",
          all(t and t["status"] == "plan" and t["condition_id"] == C and t["tp_zone"] is None and t["entry_condition"] == "C no tp @ 4580" for t in tr[:1]), json.dumps(tr)[:300])
    snap = json.dumps(page.evaluate(f"() => getBook('main').trades.find(t=>t.id==='{tr[0]['id']}')"), sort_keys=True)
    page.evaluate("([i,c])=>satV3CondEdit(i,c,'text','C แก้คำหลังบันทึก order @ 4585')", [X, C])
    page.wait_for_timeout(200)
    snap2 = json.dumps(page.evaluate(f"() => getBook('main').trades.find(t=>t.id==='{tr[0]['id']}')"), sort_keys=True)
    check(f"{tag} แก้ข้อความเงื่อนไขหลังบันทึก order → ข้อความในไอเดียเปลี่ยน แต่ entry_condition ในไม้ไม่เปลี่ยน (สำเนา)",
          cond(page, X, C)["text"] == "C แก้คำหลังบันทึก order @ 4585" and snap == snap2 and tr[0]["entry_condition"] == "C no tp @ 4580")
    # ยกเลิกเงื่อนไขที่ผูกไม้แล้ว: ไม้ไม่กระทบ
    page.evaluate("([i,c])=>satV3CondCancel(i,c)", [X, C])
    page.wait_for_timeout(200)
    snap3 = json.dumps(page.evaluate(f"() => getBook('main').trades.find(t=>t.id==='{tr[0]['id']}')"), sort_keys=True)
    check(f"{tag} ยกเลิกเงื่อนไขที่ผูกกับไม้แล้ว → ซ่อนอย่างเดียว ไม้ไม่เปลี่ยนแม้แต่ field เดียว", cond(page, X, C)["status"] == "cancelled" and snap == snap3)

    # ═════════ 5) ไม่มีเงื่อนไขเหลือ + ไม่มีไม้ผูก → 'ไม่มีเงื่อนไขเหลือ' + [ปิดแผน] (ไม่ปิดเอง) ═════════
    setup_strategy(page, "S50", "S")
    S = new_plan(page, "S50")
    S1 = add_cond_typed(page, S, "Break & Pullback @", "1000", 950, 940)
    page.click(f'.ui-plan[data-id="{S}"] .ui-plan-cta .ui-btn-pri:has-text("บันทึกแผน")')
    page.wait_for_timeout(250)
    page.click(f'.ui-wc[data-cond="{S1}"] .ui-wc-cancel')
    page.wait_for_timeout(250)
    w = text_of(page, f'.ui-wait[data-id="{S}"]')
    check(f"{tag} ยกเลิกข้อสุดท้าย → แถวขึ้น 'ไม่มีเงื่อนไขเหลือ' + ปุ่ม [ปิดแผน] · ไม่ปิดเอง (status ยัง active)",
          "ไม่มีเงื่อนไขเหลือ" in w and "ปิดแผน" in w and idea(page, S)["status"] == "active", w)
    page.locator(f'.ui-wait[data-id="{S}"]').screenshot(path=os.path.join(SHOTS, f"7d5-empty-{px}.png"))
    page.click(f'.ui-wait[data-id="{S}"] .ui-wc-close')
    page.wait_for_timeout(250)
    isx = idea(page, S)
    check(f"{tag} [ปิดแผน] → status:'closed' · แถวหาย · เงื่อนไขที่ยกเลิกยังอยู่ในข้อมูล (ไม่ลบ)",
          isx["status"] == "closed" and count(page, f'.ui-wait[data-id="{S}"]') == 0 and isx["conditions"][0]["status"] == "cancelled", json.dumps(isx["conditions"]))

    # ═════════ 6) ข้อมูลเดิม: เงื่อนไข 7D.4 ที่ไม่มี status = รออยู่ · ไอเดียก่อน 7D.4 ยังแสดง ═════════
    page.evaluate("""() => satwWrite('BRENT', {comps:{trend:{v:'up'},macro:{v:'up'}}, invalidation:70}); """)
    page.wait_for_timeout(120)
    p5.set_bias_dom(page, "BRENT", "L")
    page.evaluate("""() => sat7dWrite('satIdeas','iOld74', {v3:true, asset:'BRENT', bias:'Long', week:wpWeekKey(), created_at:new Date().toISOString(),
        entry:null, sl:null, tp:null, cancel_level:null, setups:[], status:'active', accts:{}, planned:true,
        conditions:[{id:'co1', text:'เก่า 7D.4 ข้อ 1', tp_from:90, tp_to:95, inval:null, active:false}, {id:'co2', text:'เก่า 7D.4 ข้อ 2', tp_from:null, tp_to:null, inval:null, active:false}]}); """)
    page.evaluate("""() => sat7dWrite('satIdeas','iPre74', {v3:true, asset:'S50', bias:'Short', week:wpWeekKey(), created_at:new Date().toISOString(),
        entry:null, sl:null, tp:null, cancel_level:null, setups:[], status:'active', accts:{}}); """)
    page.wait_for_timeout(300)
    check(f"{tag} เงื่อนไข 7D.4 ที่ไม่มี status → รออยู่ (แถวพับโชว์ 2 ข้อ · TP ที่ไม่มี = —)",
          count(page, '.ui-wait[data-id="iOld74"] .ui-wc') == 2 and "TP — · Inval —" in text_of(page, '.ui-wc[data-cond="co2"]')
          and "TP 90–95" in text_of(page, '.ui-wc[data-cond="co1"]'))
    page.click('.ui-wc[data-cond="co1"] .ui-wc-cancel')
    page.wait_for_timeout(200)
    co1 = cond(page, "iOld74", "co1")
    check(f"{tag} ข้อ 7D.4 เดิม (ไม่มี field saved) ถือว่าบันทึกแล้ว → [ยกเลิก] = ซ่อน ไม่ลบ", co1 and co1["status"] == "cancelled" and co1["text"] == "เก่า 7D.4 ข้อ 1")
    leg = page.evaluate("() => { const c=document.querySelector('.ui-plan[data-id=\"iPre74\"]'); return c ? c.outerHTML : ''; }")
    check(f"{tag} ไอเดียก่อน 7D.4 (ไม่มี conditions) ยังแสดงการ์ดเดิม: มีช่อง Entry/SL/TP + ไม่มีรายการเงื่อนไข",
          "ui-plan-nums" in leg and "ui-conds" not in leg, leg[:160])

    # ═════════ 7) รายการปุ่มลัด — ใช้ร่วมทุก asset · เก็บที่ satConfig/conditionTemplates ═════════
    setup_strategy(page, "BTCUSD", "L")
    setup_strategy(page, "XAUUSD", "S")
    D1 = new_plan(page, "BTCUSD")           # ร่างใหม่ 2 asset พร้อมกัน
    D2 = new_plan(page, "XAUUSD")
    # AC2: ตัดชิปปุ่มลัด + ✎ แก้รายการ ออกจากการ์ด — รายการแม่แบบ (satConfig/conditionTemplates) + ฟังก์ชันยังอยู่ ทดสอบผ่านฟังก์ชันตรง
    check(f"{tag} ร่างของ BTC และ XAUUSD: ไม่มีชิปปุ่มลัด/✎ แก้รายการ (AC2) · แต่ละใบมีเงื่อนไข bp 1 ข้อ",
          count(page, f'.ui-plan[data-id="{D1}"] .ui-cond-sc[data-shortcut]') == 0 and count(page, f'.ui-plan[data-id="{D2}"] .ui-cond-sc[data-shortcut]') == 0
          and count(page, ".ui-cond-tpl-edit") == 0 and len(idea(page, D1)["conditions"]) == 1 and len(idea(page, D2)["conditions"]) == 1)
    page.evaluate("() => satV3CondTplEditorOpen('%s','list')" % D2)
    page.wait_for_timeout(200)
    check(f"{tag} ตัวแก้รายการ (ฟังก์ชันเดิม) ยังวาดได้เฉพาะการ์ดที่เปิด (รายการเดิม 2 ช่อง) — ไม่มีทางเปิดจาก UI แล้ว",
          page.evaluate("(i)=>satV3CondTplEditorHtml(i).includes('ui-ctpl-ed')", D2) and not page.evaluate("(i)=>satV3CondTplEditorHtml(i)", D1)
          and page.evaluate("(i)=>(satV3CondTplEditorHtml(i).match(/id=\"ctplEd_/g)||[]).length", D2) == 2)
    page.evaluate("() => satV3CondTplEditorClose()")
    page.evaluate("() => satV3CondTplAdd('Retest VWAP @ ')")
    page.wait_for_timeout(300)
    tpl = page.evaluate("() => satV3CondTemplates().map(t=>t.text)")
    check(f"{tag} เพิ่ม 'Retest VWAP @ ' → เป็น 3 รายการ (เว้นวรรคท้ายไม่หาย)", tpl[-1] == "Retest VWAP @ " and len(tpl) == 3, json.dumps(tpl))
    check(f"{tag} รายการแม่แบบใช้ร่วมทุก asset (อ่านจากที่เดียว) · การ์ด BTC ไม่แสดงปุ่มลัด (AC2)", count(page, f'.ui-plan[data-id="{D1}"] .ui-cond-sc[data-shortcut]') == 0 and page.evaluate("() => satV3CondTemplates().length") == 3)
    dumped = page.evaluate("() => window.firebase.__mockDb.__dump()")
    doc = dumped.get("users/testuid/satConfig/conditionTemplates")
    check(f"{tag} เก็บที่ users/{{uid}}/satConfig/conditionTemplates = {{items:[{{id,text}}]}}",
          doc and [i["text"] for i in doc["items"]] == tpl and all(set(i.keys()) == {"id", "text"} for i in doc["items"]), json.dumps(doc)[:300])
    check(f"{tag} satV3CondAdd ด้วยข้อความแม่แบบเพิ่มเงื่อนไขข้อความนั้นจริง (BTC · แทนปุ่มลัดที่ตัดแล้ว)",
          (lambda: (page.evaluate("(i)=>satV3CondAdd(i,'Retest VWAP @ 60000')", D1), page.wait_for_timeout(200), idea(page, D1)["conditions"][-1]["text"])[-1])() == "Retest VWAP @ 60000")
    p5.reload_keep_state(page)
    tpl_r = page.evaluate("() => satV3CondTemplates().map(t=>t.text)")
    check(f"{tag} reload → รายการแม่แบบ 3 รายการยังอยู่", tpl_r == tpl, json.dumps(tpl_r))
    first_id = page.evaluate("() => satV3CondTemplates()[0].id")
    page.evaluate("(i)=>satV3CondTplRename(i,'Break & Retest @ ')", first_id)
    page.wait_for_timeout(250)
    tpl2 = page.evaluate("() => satV3CondTemplates().map(t=>t.text)")
    check(f"{tag} แก้ชื่อค่าเริ่มต้นได้ (Break & Pullback → Break & Retest) และเขียนลง Firestore ทั้งรายการ",
          tpl2[0] == "Break & Retest @ " and len(tpl2) == 3 and
          [i["text"] for i in page.evaluate("() => window.firebase.__mockDb.__dump()")["users/testuid/satConfig/conditionTemplates"]["items"]] == tpl2, json.dumps(tpl2))
    check(f"{tag} ชื่อที่แก้อ่านได้ชุดเดียวกันทุกที่ (ไม่มีปุ่มลัดในการ์ด AC2)", count(page, ".ui-cond-sc[data-shortcut]") == 0)
    second_id = page.evaluate("() => satV3CondTemplates()[1].id")
    page.evaluate("(i)=>satV3CondTplRemove(i)", second_id)
    page.wait_for_timeout(250)
    tpl3 = page.evaluate("() => satV3CondTemplates().map(t=>t.text)")
    check(f"{tag} ลบรายการ → เหลือ 2 (ลบรายการที่ 2 'Swing back…')",
          tpl3 == ["Break & Retest @ ", "Retest VWAP @ "], json.dumps(tpl3))
    check(f"{tag} ตัวแก้รายการปิดอยู่ (ไม่มีทางเปิดจาก UI)", count(page, ".ui-ctpl-ed") == 0)

    # ═════════ ระบบ ═════════
    for t in ["home", "port", "watch", "journal", "plan"]:
        try: page.evaluate(f"() => switchTab('{t}')")
        except Exception: pass
    page.wait_for_timeout(200)
    p5.goto_sat(page)
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
    print("\n==== SUMMARY (Phase 6 / 7D.5) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
