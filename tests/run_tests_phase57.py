#!/usr/bin/env python3
"""GL2 — เตือนตอนกรอกค่าพอร์ตเมื่อต่างจากทุนในตั้งค่าเกิน 10% · เทส 57
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-08
ภาพ tests/screenshots/gl2-sheet-{1440,390}.png
รัน: python3 run_tests_phase57.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase56 as G
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = base.BROWSER_ENGINE
results = G.results
check, js, txt, count, wait = G.check, G.js, G.txt, G.count, G.wait


def cap_doc(main_core=4320000, fam_core=2000000, main_fx=36):
    def m(doc):
        for a, core in (("main", main_core), ("fam", fam_core)):
            s = doc["books"][a]["settings"]
            s["capital"]["core"] = core; s["capital"]["satB"] = 0; s["strategicCash"] = 0
            s["fx"] = main_fx if a == "main" else 36
    return m


def line(page, a): return txt(page, f'[data-gl-valcmp="{a}"]')
def warn(page, a): return js(page, "(a)=>document.querySelector(`[data-gl-valcmp=\"${a}\"]`).getAttribute('data-warn')", a)
def typ(page, a, v):
    page.locator(f'[data-gl-valin="{a}"]').fill(v); wait(page, 120)


def open_sheet(page):
    G.go_today(page); page.locator("[data-gl-valopen]").click(); wait(page, 300)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); narrow = w < 500
    # ── 1-2 main USD
    browser, context, page, ce, pe, dialogs = G.launch(pw, w, h, G.with_goals(log=False), cap_doc())
    try:
        open_sheet(page)
        check(f"{tag} 1 ช่องว่าง = ไม่มีบรรทัดเทียบ", line(page, "main") == "" and line(page, "fam") == "")
        typ(page, "main", "145000")
        l = line(page, "main")
        check(f"{tag} 1 main ทุนแอป $120.0k · กรอก 145,000 → 'ต่าง +20.8%' amber + ลิงก์ ตั้งค่า", l == "ทุนในตั้งค่า $120.0k · ต่าง +20.8% → พิจารณาปรับทุนใน ตั้งค่า" and warn(page, "main") == "1" and count(page, "[data-gl-capgo]") == 1, l)
        color_w = js(page, "()=>getComputedStyle(document.querySelector('[data-gl-valcmp=main]')).color")
        typ(page, "main", "124000")
        l = line(page, "main"); color_n = js(page, "()=>getComputedStyle(document.querySelector('[data-gl-valcmp=main]')).color")
        check(f"{tag} 2 กรอก 124,000 → 'ทุนในตั้งค่า $120.0k (ต่าง +3.3%)' สีจาง ไม่มีลิงก์", l == "ทุนในตั้งค่า $120.0k (ต่าง +3.3%)" and warn(page, "main") == "0" and count(page, "[data-gl-capgo]") == 0 and color_n != color_w, json.dumps([l, color_n, color_w]))
        typ(page, "main", "108000")
        check(f"{tag} 2 กรอก 108,000 → 'ต่าง −10.0%' สีจาง (= 10% ไม่เตือน)", line(page, "main") == "ทุนในตั้งค่า $120.0k (ต่าง −10.0%)" and warn(page, "main") == "0", line(page, "main"))
        typ(page, "main", "107000")
        check(f"{tag} 2 กรอก 107,000 → amber 'ต่าง −10.8%'", "ต่าง −10.8%" in line(page, "main") and warn(page, "main") == "1", line(page, "main"))
        typ(page, "main", "")
        check(f"{tag} 2 ลบค่า → บรรทัดหาย", line(page, "main") == "")
        # ── 3 Family THB
        typ(page, "fam", "2380000")
        check(f"{tag} 3 Family ทุนแอป ฿2.00M · กรอก 2,380,000 → 'ต่าง +19.0%' amber", line(page, "fam") == "ทุนในตั้งค่า ฿2.00M · ต่าง +19.0% → พิจารณาปรับทุนใน ตั้งค่า" and warn(page, "fam") == "1", line(page, "fam"))
        typ(page, "fam", "")
        check(f"{tag} 3 ช่องว่าง → ไม่มีบรรทัด", line(page, "fam") == "")
        # ── 6 layout
        typ(page, "main", "145000"); typ(page, "fam", "2380000")
        info = js(page, """()=>{ const r=[...document.querySelectorAll('.glCmp')].map(e=>{const cs=getComputedStyle(e); return {h:e.getBoundingClientRect().height, ws:cs.whiteSpace, fs:parseFloat(cs.fontSize), sw:e.scrollWidth, cw:e.clientWidth, ff:cs.fontFamily}});
          const i=document.querySelector('[data-gl-valin]'); const ph=getComputedStyle(i,'::placeholder').fontFamily, inf=getComputedStyle(i).fontFamily;
          const mono=getComputedStyle(document.documentElement).getPropertyValue('--mono'); return {r,ph,inf,mono}; }""")
        one = all(x["h"] < x["fs"] * 2 and x["ws"] == "nowrap" for x in info["r"])
        check(f"{tag} 6 บรรทัดเทียบ 2 บัญชีไม่ตัดบรรทัด (nowrap · สูง < 2 บรรทัด)", one and len(info["r"]) == 2, json.dumps(info, ensure_ascii=False))
        mono_first = info["mono"].split(",")[0].strip().strip("'\"")
        check(f"{tag} 6 placeholder + ช่อง + บรรทัดเทียบไม่ใช้ฟอนต์ mono", mono_first and mono_first not in info["ph"] and mono_first not in info["inf"] and all(mono_first not in x["ff"] for x in info["r"]), json.dumps(info, ensure_ascii=False))
        check(f"{tag} 6 ไม่ล้นแนวนอน", G.overflow(page) <= 0, G.overflow(page))
        G.shot(page, f"gl2-sheet-{sfx}.png", "#glValOverlay .modal")
        # ── 5 ลิงก์ ตั้งค่า มีค่าค้าง → ถามก่อน (กดยกเลิก)
        js(page, "()=>{ window.__cc=0; window.confirm=()=>{ window.__cc++; return false; }; }")
        page.locator('[data-gl-valcmp="main"] [data-gl-capgo]').click(); wait(page, 300)
        st = js(page, "()=>({cc:window.__cc, sheet:document.getElementById('glValOverlay').classList.contains('show'), set:document.getElementById('setOverlay').classList.contains('show'), v:document.querySelector('[data-gl-valin=main]').value})")
        check(f"{tag} 5 มีค่าค้าง → ถามก่อน · ตอบไม่ → ค้างใน sheet ค่ายังอยู่ · ไม่เปิดตั้งค่า", st == {"cc": 1, "sheet": True, "set": False, "v": "145000"}, json.dumps(st))
        # ตอบใช่ → เปิดตั้งค่าส่วนทุน
        js(page, "()=>{ window.confirm=()=>{ window.__cc++; return true; }; }")
        page.locator('[data-gl-valcmp="main"] [data-gl-capgo]').click(); wait(page, 400)
        st = js(page, "()=>({cc:window.__cc, sheet:document.getElementById('glValOverlay').classList.contains('show'), set:document.getElementById('setOverlay').classList.contains('show'), core:document.getElementById('sCore').value, open:document.querySelector('#setOverlay .setsec').open, act:acctActive})")
        check(f"{tag} 5 ตอบใช่ → ปิด sheet · เปิดตั้งค่าส่วนทุน (เงินต้น Core 4320000) · ถามรวม 2 ครั้ง", st["cc"] == 2 and not st["sheet"] and st["set"] and st["core"] == "4320000" and st["open"], json.dumps(st))
        check(f"{tag} 5 ไม่บันทึกค่าที่ค้าง: goalLog ว่าง", G.settings(page, "goalLog") in (None, {}), json.dumps(G.settings(page, "goalLog")))
        js(page, "()=>document.getElementById('setOverlay').classList.remove('show')")
        # ลิงก์ของบัญชีที่ไม่ใช่ active → สลับบัญชีแล้วเปิดตั้งค่าของบัญชีนั้น
        G.go_today(page); page.locator("[data-gl-valopen]").click(); wait(page, 300)
        typ(page, "fam", "2380000")
        page.locator('[data-gl-valcmp="fam"] [data-gl-capgo]').click(); wait(page, 600)
        st = js(page, "()=>({act:acctActive, set:document.getElementById('setOverlay').classList.contains('show'), core:document.getElementById('sCore').value})")
        check(f"{tag} 5 ลิงก์ของ Family → สลับเป็นบัญชี Family แล้วเปิดตั้งค่า (เงินต้น 2000000)", st == {"act": "fam", "set": True, "core": "2000000"}, json.dumps(st))
        # ไม่มีค่าค้าง → เปิดทันที
        js(page, "()=>{ document.getElementById('setOverlay').classList.remove('show'); acctSwitch('main'); }"); wait(page, 400)
        G.go_today(page); page.locator("[data-gl-valopen]").click(); wait(page, 300)
        typ(page, "main", "145000"); l0 = warn(page, "main")
        # ลบค่าก่อน = ไม่มีลิงก์ → จำลองเรียก glCapGo ตรง ๆ ตอนช่องว่าง
        typ(page, "main", "")
        js(page, "()=>{ window.__cc=0; window.confirm=()=>{ window.__cc++; return true; }; glCapGo('main'); }"); wait(page, 400)
        st = js(page, "()=>({cc:window.__cc, set:document.getElementById('setOverlay').classList.contains('show')})")
        check(f"{tag} 5 ไม่มีค่าค้าง → ไม่ถาม · เปิดตั้งค่าทันที", st == {"cc": 0, "set": True}, json.dumps(st))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 4 ทุนแอป = 0 → ไม่มีบรรทัด · บันทึกได้ · goalLog เหมือน GL1
    browser, context, page, ce, pe, dialogs = G.launch(pw, w, h, G.with_goals(log=False), cap_doc(fam_core=0))
    try:
        open_sheet(page)
        typ(page, "fam", "2380000"); typ(page, "main", "145000")
        check(f"{tag} 4 Family ทุนแอป 0 → ไม่มีบรรทัดเทียบ (main ยังมี)", line(page, "fam") == "" and line(page, "main") != "", json.dumps([line(page, "fam"), line(page, "main")], ensure_ascii=False))
        page.locator("[data-gl-valsave]").click(); wait(page, 450)
        gl = G.settings(page, "goalLog")
        check(f"{tag} 4 amber ไม่บล็อกการบันทึก · goalLog รูปเดิมของ GL1 {{acct:[{{d,v}}]}}", not G.sheet_open(page) and gl == {"main": [{"d": G.TODAY, "v": 145000}], "fam": [{"d": G.TODAY, "v": 2380000}]}, json.dumps(gl))
        check(f"{tag} 4 หลังบันทึก การ์ดเป้าไม่มีเตือนทุน", count(page, "[data-gl-goal] [data-gl-valcmp]") == 0)
        check(f"{tag} 4 ไม่แก้ทุนในตั้งค่า (main core 4320000)", js(page, "()=>getBook('main').settings.capital.core") == 4320000)
        check(f"{tag} 4 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
