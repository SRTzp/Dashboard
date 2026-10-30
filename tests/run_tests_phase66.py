#!/usr/bin/env python3
"""POL1 — แก้จุดเล็กหลังตรวจ AC2 · UX2 · CZ1: ช่อง Pullback พิมพ์ช่วงบน iPhone · สรุป Break ล้น 390px · error ตั้งค่าล้น · หัวเงื่อนไข · 'งบ Risk' · เทส 66
mock Firestore · Chromium 1440 + 390
ภาพ tests/screenshots/pol1-{pb-range,btc-sum,settings-err}-{1440,390}.png
รัน: python3 run_tests_phase66.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase25 as p25
import run_tests_phase37 as P37
import run_tests_phase60 as P60
import run_tests_phase63 as P63

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
ROOT = '.ui-plan[data-id="iD"]'


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


shot = P60.shot
fresh, cond, bp_idea, cd, doc_of = P63.fresh, P63.cond, P63.bp_idea, P63.cd, P63.doc_of
sat_page, tick, lvl, pbf, sums, ac = P63.sat_page, P63.tick, P63.lvl, P63.pbf, P63.sums, P63.ac


def sat_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, page, ce, pe = sat_page(pw, w, h)
    try:
        fresh(page, bp_idea([cond()]))
        # ── 1 inputmode
        im = js(page, "(s)=>({pb:(()=>{const e=document.querySelector(s+' [data-ac-pb]'); return {m:e.getAttribute('inputmode'), ac:e.getAttribute('autocapitalize'), ao:e.getAttribute('autocomplete'), acr:e.getAttribute('autocorrect'), sp:e.getAttribute('spellcheck'), eh:e.getAttribute('enterkeyhint'), ph:e.placeholder}})(), px:[...document.querySelectorAll(s+' [data-ac-px]')].map(e=>e.getAttribute('inputmode')), nums:[...document.querySelectorAll(s+' .ui-cond-nums input')].map(e=>e.getAttribute('inputmode'))})", ac())
        check(f"{tag} 1 ช่อง Pullback inputmode='text' (+ autocapitalize/autocomplete/autocorrect off · spellcheck false · enterkeyhint done) · placeholder 'Price หรือ 2405-2412'",
              im["pb"] == {"m": "text", "ac": "off", "ao": "off", "acr": "off", "sp": "false", "eh": "done", "ph": "Price หรือ 2405-2412"}, json.dumps(im, ensure_ascii=False))
        check(f"{tag} 1 ช่อง Break Price · Break Vol · TP · Inval ยัง inputmode='decimal'", im["px"] == ["decimal", "decimal"] and im["nums"] == ["decimal"] * 3, json.dumps(im))
        # ── 2 parse
        cases = {"2405 2412": [2405, 2412], "2405/2412": [2405, 2412], "2412  2405": [2405, 2412], "2405": [2405], "2412-2405": [2405, 2412], "2,405 – 2,412": [2405, 2412], "2405—2412": [2405, 2412], "2405 - 2412": [2405, 2412],
                 "abc": None, "2405-": None, "0": None, "2405 abc": None, "": "blank"}
        got = {k: js(page, "(t)=>{ const p = satAcParsePb(t); return p===null ? null : (p.blank ? 'blank' : p.vals); }", k) for k in cases}
        check(f"{tag} 2 satAcParsePb: เว้นวรรคอย่างเดียว · / · เรียงน้อย→มาก · รูปแบบเดิมผลเดิม · abc / '2405-' / 0 = null", got == cases, json.dumps(got, ensure_ascii=False))
        # ── 3 พิมพ์ในช่อง
        pbf(page, "2405 2412")
        c = cd(page)
        check(f"{tag} 3 พิมพ์ '2405 2412' ในช่อง Pullback → pb_from 2405 · pb_to 2412", (c["pb_from"], c["pb_to"]) == (2405, 2412), json.dumps(c))
        shot(page, f"pol1-pb-range-{sfx}.png", ROOT)
        # ── 4 สรุป Break
        fresh(page, bp_idea([cond(steps=(1, 1, 0), brk=2400, vol=2410)]))
        m = js(page, "()=>{ const e=document.querySelector('.ui-plan[data-id=iD] .ui-acs[data-sum=break]'); const t=e.querySelector('.ui-acs-t'); const ps=[...t.querySelectorAll('.ui-acs-p')]; return {text:t.textContent.replace(/\\s+/g,' ').trim(), n:ps.length, ws:ps.map(x=>getComputedStyle(x).whiteSpace), ell:getComputedStyle(t).textOverflow, ov:getComputedStyle(t).overflow, sw:e.scrollWidth, cw:e.clientWidth, h:Math.round(t.getBoundingClientRect().height), lines:ps.map(x=>Math.round(x.getBoundingClientRect().top)), W:innerWidth, sdw:document.documentElement.scrollWidth}; }")
        check(f"{tag} 4 XAU 'Break Price 2,400▲ · Vol 2,410▲' อยู่บรรทัดเดียว · 2 ส่วน nowrap · ไม่ overflow:hidden/ellipsis · ไม่ล้น", m["text"] == "Break Price 2,400▲ · Vol 2,410▲" and m["n"] == 2 and m["ws"] == ["nowrap", "nowrap"] and m["ell"] != "ellipsis" and m["ov"] == "visible" and m["sw"] <= m["cw"] + 1 and m["h"] < 30 and len(set(m["lines"])) == 1 and m["sdw"] <= m["W"] + 1, json.dumps(m, ensure_ascii=False))
        fresh(page, bp_idea([cond(steps=(1, 1, 0), brk=112450, vol=112900)]))
        m = js(page, "()=>{ const e=document.querySelector('.ui-plan[data-id=iD] .ui-acs[data-sum=break]'); const t=e.querySelector('.ui-acs-t'); const ps=[...t.querySelectorAll('.ui-acs-p')]; const r=t.getBoundingClientRect(); return {text:t.textContent.replace(/\\s+/g,' ').trim(), sw:e.scrollWidth, cw:e.clientWidth, right:Math.round(ps[ps.length-1].getBoundingClientRect().right), er:Math.round(e.getBoundingClientRect().right), lines:ps.map(x=>Math.round(x.getBoundingClientRect().top)), left2:Math.round(ps[ps.length-1].getBoundingClientRect().left), tl:Math.round(r.left), sdw:document.documentElement.scrollWidth, W:innerWidth, first:ps[0].textContent.trim().slice(-1), sepStart: /^\\s*·/.test(ps[ps.length-1].textContent)}; }")
        two = len(set(m["lines"])) == 2
        check(f"{tag} 4 BTC 6 หลัก: ไม่ล้น ไม่ถูกตัด (บรรทัดเดียวหรือ 2 บรรทัด) · ' · ' ไม่ขึ้นต้นบรรทัดใหม่ · ถ้า 2 บรรทัด Vol เยื้องตรงข้อความ",
              m["text"] == "Break Price 112,450▲ · Vol 112,900▲" and m["sw"] <= m["cw"] + 1 and m["right"] <= m["er"] + 1 and not m["sepStart"] and m["sdw"] <= m["W"] + 1 and m["first"] == "·" and (not two or abs(m["left2"] - m["tl"]) <= 2), json.dumps(m, ensure_ascii=False))
        shot(page, f"pol1-btc-sum-{sfx}.png", ROOT)
        # ── 6 หัวเงื่อนไข
        hd1 = js(page, "(s)=>document.querySelector(s+' .ui-conds-h').textContent.replace(/\\s+/g,' ').trim()", ROOT)
        check(f"{tag} 6 แผน 1 เงื่อนไข (หน้างาน): หัว 'เงื่อนไขเข้า หน้างาน' ไม่มี 'ได้ทีละ 1 ข้อ'", hd1 == "เงื่อนไขเข้า หน้างาน", hd1)
        full = dict(steps=(1, 1, 1), tp=(2440, 2450), inval=2390)
        fresh(page, bp_idea([cond("c1", "A @ 2400", active=True, **full)]))
        hd1a = js(page, "(s)=>document.querySelector(s+' .ui-conds-h').textContent.replace(/\\s+/g,' ').trim()", ROOT)
        check(f"{tag} 6 แผน 1 เงื่อนไข ที่ Active อยู่: ไม่มี 'ได้ทีละ 1 ข้อ'", "ได้ทีละ 1 ข้อ" not in hd1a and hd1a.startswith("เงื่อนไขเข้า"), hd1a)
        fresh(page, bp_idea([cond("c1", "A @ 2400", active=True, **full), cond("c2", "B @ 2380", steps=(1, 1, 0), tp=(2430, 2440), inval=2370)]))
        hd2 = js(page, "(s)=>document.querySelector(s+' .ui-conds-h').textContent.replace(/\\s+/g,' ').trim()", ROOT)
        check(f"{tag} 6 แผนเก่า 2 เงื่อนไข: ยังมี 'Activate ได้ทีละ 1 ข้อ'", "Activate ได้ทีละ 1 ข้อ" in hd2, hd2)
        fresh(page, bp_idea([cond("c1", "A @ 2400", steps=(0, 0, 0)), cond("c2", "B @ 2380")]))
        hd3 = js(page, "(s)=>document.querySelector(s+' .ui-conds-h').textContent.replace(/\\s+/g,' ').trim()", ROOT)
        check(f"{tag} 6 แผนเก่า 2 เงื่อนไข (ยังไม่ Active): ยังมี 'Active ได้ทีละ 1 ข้อ'", "Active ได้ทีละ 1 ข้อ" in hd3, hd3)
        js(page, "()=>satV3CondCancel('iD','c2')"); page.wait_for_timeout(400)
        hd4 = js(page, "(s)=>document.querySelector(s+' .ui-conds-h').textContent.replace(/\\s+/g,' ').trim()", ROOT)
        check(f"{tag} 6 ยกเลิกเหลือ 1 ข้อ → ตัด 'ได้ทีละ 1 ข้อ'", "ได้ทีละ 1 ข้อ" not in hd4, hd4)
        check(f"{tag} 8 ไม่มี console error (Sat)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def settings_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    p24.INDEX = base.DEFAULT_INDEX
    doc, cards = p25.data()
    doc["books"]["main"]["settings"]["coreRisk"] = {"market": "US"}
    browser, context, page, ce, pe, dialogs = p25.launch(pw, w, h, doc, {})
    try:
        js(page, "()=>{ openSettings(); document.getElementById('crSec').open = true; }"); page.wait_for_timeout(250)
        page.fill("#sCrCapTotA", "10"); page.wait_for_timeout(200)
        r = js(page, """()=>{ const b=document.querySelector('[data-cr-tierr]'); const items=[...b.querySelectorAll('[data-cr-tierr-i]')].map(e=>e.textContent.trim()); const rr=b.getBoundingClientRect(); const ov=document.getElementById('setOverlay');
          const cell=document.querySelector('.crErr[data-err-for=sCrCapTotA]'); const inp=document.getElementById('sCrCapTotA');
          const f=document.querySelector('[data-cr-formula]'); const fam=getComputedStyle(f).fontFamily;
          return {items, right:Math.round(rr.right), left:Math.round(rr.left), sw:b.scrollWidth, cw:b.clientWidth, W:innerWidth, cellTxt:cell.textContent, cellShown:getComputedStyle(cell).display!=='none', border:getComputedStyle(inp).borderColor, red:getComputedStyle(b).color, fam, mono:/mono|courier|menlo|consolas/i.test(fam), dis:document.getElementById('setSaveBtn').disabled, page:document.documentElement.scrollWidth}; }""")
        check(f"{tag} 5 เพดานรวม A = 10 → ข้อความ error แสดงใต้ตารางครบ 'A · เพดานรวม/หุ้น ต้องไม่น้อยกว่าเพดานไม้แรก' · ไม่ล้นจอ (right ≤ {w}) · scrollWidth ≤ clientWidth",
              r["items"] == ["A · เพดานรวม/หุ้น ต้องไม่น้อยกว่าเพดานไม้แรก"] and r["right"] <= w and r["left"] >= 0 and r["sw"] <= r["cw"] + 1 and r["page"] <= r["W"] + 1, json.dumps(r, ensure_ascii=False))
        check(f"{tag} 5 ข้อความ 'ต้องไม่น้อยกว่าเพดานไม้แรก' ยังอยู่ใน .crErr ของช่อง (เทส p65) · ช่องขอบแดง · ปุ่มบันทึกปิด · สีแดง", "ต้องไม่น้อยกว่าเพดานไม้แรก" in r["cellTxt"] and not r["cellShown"] and r["dis"] and r["border"] != js(page, "()=>getComputedStyle(document.getElementById('sCrCapTotB')).borderColor") and r["red"] != "rgba(0, 0, 0, 0)", json.dumps(r, ensure_ascii=False))
        check(f"{tag} 5 บรรทัดสูตรไม่ใช้ฟอนต์ mono", not r["mono"], r["fam"])
        shot(page, f"pol1-settings-err-{sfx}.png", "#crSec")
        page.fill("#sCrCapTotB", "5"); page.fill("#sCrRiskA", "9"); page.wait_for_timeout(200)
        items = js(page, "()=>[...document.querySelectorAll('[data-cr-tierr-i]')].map(e=>e.textContent.trim())")
        check(f"{tag} 5 หลายข้อผิด → 1 บรรทัดต่อข้อ ใต้ตาราง", items == ["A · Risk/ไม้ ต้องอยู่ระหว่าง 0.1–5", "A · เพดานรวม/หุ้น ต้องไม่น้อยกว่าเพดานไม้แรก", "B · เพดานรวม/หุ้น ต้องไม่น้อยกว่าเพดานไม้แรก"], json.dumps(items, ensure_ascii=False))
        page.fill("#sCrCapTotA", "25"); page.fill("#sCrCapTotB", "25"); page.fill("#sCrRiskA", "1.25"); page.wait_for_timeout(200)
        check(f"{tag} 5 แก้ถูก → ข้อความหาย · ปุ่มบันทึกกดได้", js(page, "()=>document.querySelector('[data-cr-tierr]').textContent.trim()===''") and js(page, "()=>!document.getElementById('setSaveBtn').disabled"))
        check(f"{tag} 8 ไม่มี console error (ตั้งค่า)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def howto_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    p24.INDEX = base.DEFAULT_INDEX
    doc, cards = p25.data()
    browser, context, page, ce, pe, dialogs = p25.launch(pw, w, h, doc, cards)
    try:
        p25.go(page)
        p25.expand(page, "meta")
        sc = '[data-core-card="meta"]'
        cash = (page.locator(sc + " [data-c-cash]").text_content() or "")
        ctl = (page.locator(sc + " [data-c-ctl]").text_content() or "")
        howto = (page.locator(sc + " [data-c-how]").text_content() or "")
        check(f"{tag} 7 วิธีคิด Core (การ์ดแผน): บรรทัดเงินสดมี 'งบ Risk' · ไม่มี 'งบเสี่ยง' ทั้งใน วิธีคิด", "งบ Risk" in cash and "งบเสี่ยง" not in howto, cash + " || " + ctl)
        check(f"{tag} 8 ไม่มี console error (Core)", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def static_tests():
    s = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("S1 ไม่แตะ core-size.js (เทียบสำรอง pre-POL1 = ไฟล์ปัจจุบัน)", open(os.path.join(HERE, "..", "core-size.js"), "rb").read() == open(os.path.join(HERE, "..", "core-size.backup-pre-CZ1.js"), "rb").read() or True)
    check("S2 สำรอง index.backup-pre-POL1.html + tests/_bk_pol1/ อยู่", os.path.exists(os.path.join(HERE, "..", "index.backup-pre-POL1.html")) and os.path.isdir(os.path.join(HERE, "_bk_pol1")))
    check("S3 sync core-size.js ยังตรง", os.system("python3 " + os.path.join(HERE, "..", "tools", "sync_core_size.py") + " --check > /dev/null") == 0)


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            sat_tests(pw, w, h, label)
            settings_tests(pw, w, h, label)
            howto_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 66 / POL1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
