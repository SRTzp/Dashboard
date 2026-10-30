#!/usr/bin/env python3
"""RR2 — กดปุ่มในการ์ดแผน (TF · ทิศ · Price) แล้วรูป Chart ไม่กระพริบ (event load ของ <img> = 0 · node เดิม) · เทส 76
Chromium 1440 + 390 · mock Firestore · ภาพ tests/screenshots/rr2-*.png
รัน: python3 run_tests_phase76.py   (INDEX_OVERRIDE=path ใช้ทดสอบกับไฟล์สำรอง)"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase59 as P59

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
wait, cnt, overflow = P59.wait, P59.cnt, P59.overflow
PICK = ["XAUUSD", "BTCUSD"]
CHART = {"url": P59.TV1, "at": "2026-10-09"}
IDX = os.environ.get("INDEX_OVERRIDE")


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:500] + "...") if (detail and len(detail) > 500) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    wait(page, 300)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def launch(pw, w, h):
    kw = {"pick": PICK}
    if IDX: kw["index"] = IDX
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, **kw)
    return b, page, ce, pe


def seed(page):
    js(page, "(c)=>{ satwWrite('XAUUSD', {bias:'Long', support:[3920,3860], resistance:[4080], invalidation:3840, chart:c}); satwWrite('BTCUSD', {bias:'Long', support:[60000], resistance:[70000], invalidation:58000}); }", CHART)
    wait(page, 400)
    P37.go_sat(page); wait(page, 400)
    js(page, "()=>satV3NewPlan('XAUUSD')"); wait(page, 600)


WATCH = """()=>{ window.__loads = 0; window.__bad = 0; window.__img = document.querySelector('.ui-tile[data-key=XAUUSD] img');
  if(!window.__ld){ window.__ld = true;
    document.addEventListener('load', e=>{ const t = e.target; if(t && t.tagName==='IMG' && t.closest && t.closest('.ui-tile[data-key=XAUUSD]')) window.__loads++; }, true); }
  return !!window.__img && window.__img.complete; }"""
STATE = "()=>{ const n = document.querySelector('.ui-tile[data-key=XAUUSD] img'); return {same: !!n && n === window.__img && n.isConnected, complete: !!n && n.complete, loads: window.__loads}; }"
MUT = """()=>{ const t = document.querySelector('.ui-tile[data-key=XAUUSD]'); window.__tm = 0; if(window.__tmo) window.__tmo.disconnect();
  window.__tmo = new MutationObserver(r=>{ window.__tm += r.length; }); window.__tmo.observe(t, {childList:true, subtree:true, attributes:true, characterData:true}); }"""


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed(page)
        check(f"{tag} 0 เตรียม: ภาพ XAUUSD โหลดแล้ว · แผนร่าง 1 ใบมีปุ่ม TF", js(page, WATCH) and cnt(page, ".ui-plan [data-ac-tf] button") == 3)
        # 1 TF 4H → D → W
        js(page, MUT)
        for tf in ("D", "W", "4H"):
            page.locator(f'.ui-plan [data-ac-tf] [data-tf="{tf}"]').first.click(); wait(page, 500)
            check(f"{tag} 1 กด TF {tf} (snapshot สะท้อนกลับ) → ปุ่มเปลี่ยนจริง", page.locator(f'.ui-plan [data-ac-tf] [data-tf="{tf}"]').first.get_attribute("aria-pressed") == "true")
        st = js(page, STATE)
        check(f"{tag} 1 กด TF 3 ครั้ง → load เพิ่ม 0 · img node เดิม · complete", st["loads"] == 0 and st["same"] and st["complete"], st)
        # 2 force 5 ครั้ง
        for _ in range(5): js(page, "()=>satV3Render({force:true})"); wait(page, 120)
        st = js(page, STATE)
        check(f"{tag} 2 satV3Render({{force:true}}) 5 ครั้ง → load 0 · node เดิม", st["loads"] == 0 and st["same"] and st["complete"], st)
        # 4 ปุ่มอื่นในการ์ดแผน
        for sel in ('.ui-plan .ui-adir[data-dir]',):
            for _ in range(2):
                if page.locator(sel).count(): page.locator(sel).first.click(); wait(page, 450)
        px = page.locator('.ui-plan [data-ac-px="brk"]')
        if px.count(): px.first.fill("4100"); px.first.press("Tab"); wait(page, 500)
        st = js(page, STATE)
        check(f"{tag} 4 สลับทิศ ▲▼ + กรอก Price → load 0 · node เดิม", st["loads"] == 0 and st["same"], [st, page.locator('.ui-plan .ui-adir[data-dir]').count(), px.count()])
        shot(page, f"rr2-plan-{sfx}.png")
        # 3 เปลี่ยน URL กราฟจริง → โหลดภาพใหม่ 1 ครั้ง
        js(page, "()=>{ window.__loads = 0; }")
        js(page, "(u)=>satwWrite('XAUUSD', {chart:{url:u, at:'2026-10-10'}})", P59.TV2); wait(page, 900)
        st = js(page, STATE)
        check(f"{tag} 3 เปลี่ยน URL กราฟ → โหลดภาพใหม่ (ยังทำงาน) · img เปลี่ยน node", st["loads"] >= 1 and not st["same"], st)
        check(f"{tag} 6 {label} ไม่มี console error · ไม่ล้นแนวนอน", not P59.real_errs(ce) and not pe and overflow(page) <= 1, [ce, pe])
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
