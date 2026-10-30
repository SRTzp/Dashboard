#!/usr/bin/env python3
"""WA1fix — Strategy เริ่มว่างจริง (เลิกโหมด legacy) + auto-pick จากแผน/ไม้ + ชิป Asset อ่านออก · เทส 72
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 (สัปดาห์นี้ = 2026-09-27)
ภาพ tests/screenshots/wa1fix-{empty,auto-pick,chips}-{1440,390}.png
รัน: python3 run_tests_phase72.py"""
from pf2_retire import retired as retired2
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase39 as P39
import run_tests_phase51 as P51
import run_tests_phase54 as P54

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, settings, overflow = P54.txt, P54.settings, P54.overflow
WK = "2026-09-27"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def fixture(m):
    def f(doc):
        s = doc["books"]["main"]["settings"]
        for k in ("BTCUSD", "S50", "BRENT"):
            s["brokers"]["XM"][k] = {"contract": 100, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}
        s.pop("satWeekPick", None)
        if m: m(s)
    return f


def launch(pw, w, h, m=None):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture(m))
    P51.fresh(page, None)
    return browser, page, ce, pe


def go(page): P37.go_sat(page); page.wait_for_timeout(300); P37.open_plan(page); page.wait_for_timeout(300)


def put_plan(page, asset, iid, planned=True, week=WK):
    d = {**P51.idea_doc(asset=asset, iid=iid, act=planned), "accts": {"main": {"broker": "XM"}}}
    js(page, "([i,w])=>{ sat7dWrite('satIdeas', i.id, Object.assign({}, i, {week:w, planned:true, setups:[], status:'active'})); }", [d, week])
    page.wait_for_timeout(400)


def put_open(page, asset, tid):
    js(page, "([a,t])=>{ const B = getBook('main'); B.trades.push({id:t, port:'satB', sym:a, status:'open', bias:'Long', qty:0.1, entry:100, sl:90, date:thaiToday(), openedAt:thaiToday()}); saveBook('main'); render(); }", [asset, tid])
    page.wait_for_timeout(300)


def hold_sync(page): js(page, "()=>{ window.__sync0 = satCarrySync; satCarrySync = function(){}; }")   # กันซิงก์ระหว่าง seed — ให้ซิงก์ครั้งแรกเห็นทุกอย่างพร้อมกัน (เหมือนผู้ใช้เปิดแอปครั้งแรกหลังอัปเดต)
def release_sync(page): js(page, "()=>{ satCarrySync = window.__sync0; satCarrySig = ''; }")


def picks(page): return js(page, "()=>satWeekPickList()")
def cards(page): return js(page, "()=>[...document.querySelectorAll('.ui-tile[data-key]')].map(e=>e.dataset.key)")


def lum(c):
    ch = [v / 255 for v in c]
    ch = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in ch]
    return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2]


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb(s):
    n = [float(x) for x in re.findall(r"[\d.]+", s)[:4]]
    return n[:3], (n[3] if len(n) > 3 else 1.0)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # 1 ผู้ใช้เดิมไม่มี satWeekPick · ไม่มีแผน/ไม้ → empty เสมอ
    browser, page, ce, pe = launch(pw, w, h)
    try:
        go(page)
        check(f"{tag} 1 ไม่มี satWeekPick ใน settings จริง (ผู้ใช้เดิม)", settings(page, "satWeekPick") is None)
        check(f"{tag} 1 ไม่มีการ์ด Asset", cards(page) == [], cards(page))
        check(f"{tag} 1 แสดง empty state + ปุ่มไป Flow + ＋ Asset", js(page, "()=>!!document.querySelector('[data-wa-empty]') && !!document.querySelector('[data-wa-flow]') && !!document.querySelector('[data-wa-add]')"))
        check(f"{tag} 1 ไม่มี data-wa-legacy / ข้อความ 'แสดงทุกตัว'", js(page, "()=>!document.querySelector('[data-wa-legacy]') && !document.body.innerText.includes('แสดงทุกตัว')"))
        check(f"{tag} 1 satAssets() ว่าง · ไม่เขียน satWeekPick ตอน render", js(page, "()=>satAssets().length") == 0 and settings(page, "satWeekPick") is None)
        P39.go_today(page)
        page.wait_for_timeout(300)
        check(f"{tag} 1 Today มีงาน 'เลือก Asset สัปดาห์นี้'", js(page, "()=>!!document.querySelector('[data-pf2-sat=\"A\"]') || document.body.innerText.includes('Start by adding a Strategic Asset')"))   # PF2: ย้ายเป็นการ์ด Sat state A
        go(page)
        check(f"{tag} 1 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [ce, pe])
        shot(page, f"wa1fix-empty-{sfx}.png", "#satV3Panel")
    finally: browser.close()

    # 2 มีแผน XAUUSD (planned) + ไม้เปิด BTC → pick = [BTCUSD, XAUUSD]
    browser, page, ce, pe = launch(pw, w, h)
    try:
        hold_sync(page); put_plan(page, "XAUUSD", "iX"); put_open(page, "BTCUSD", "tB"); release_sync(page)
        go(page)
        check(f"{tag} 2 pick = [BTCUSD, XAUUSD] (ไม้เปิดก่อน แผนตาม)", picks(page) == ["BTCUSD", "XAUUSD"], picks(page))
        check(f"{tag} 2 การ์ดมี BTCUSD, XAUUSD เท่านั้น · S50/BRENT ไม่ขึ้น", sorted(cards(page)) == ["BTCUSD", "XAUUSD"], cards(page))
        n = js(page, "()=>{ window.__w = 0; const f = satSettingsWrite; satSettingsWrite = function(m){ window.__w++; return f(m); }; satV3Render(); satV3Render(); render(); satV3Render(); return window.__w; }")
        check(f"{tag} 2 render ซ้ำไม่เขียนซ้ำ (0 ครั้ง)", n == 0, n)
        check(f"{tag} 2 pick ถูกบันทึกใน settings ของสัปดาห์นี้", (settings(page, "satWeekPick") or {}).get(WK) == ["BTCUSD", "XAUUSD"], settings(page, "satWeekPick"))
        P39.go_today(page)
        check(f"{tag} 2 Today ไม่มีงาน 'เลือก Asset สัปดาห์นี้' แล้ว (มี pick)", js(page, "()=>!document.querySelector('[data-kind=sat-pick]')"))
        go(page)
        check(f"{tag} 2 ไม่ขึ้นแถบ 'ไม้ค้าง' และไม่มี empty/legacy", js(page, "()=>!document.querySelector('[data-wa-park]') && !document.querySelector('[data-wa-empty]') && !document.querySelector('[data-wa-legacy]')"))
        shot(page, f"wa1fix-auto-pick-{sfx}.png", "#satV3Panel")
    finally: browser.close()

    # 3 4 Asset มีแผน/ไม้ → 3 ตัวใน pick ตามลำดับ · ตัวที่ 4 ไม้ค้าง
    browser, page, ce, pe = launch(pw, w, h)
    try:
        hold_sync(page)
        put_plan(page, "BRENT", "iBr", planned=False)   # แผนรอ (ร่าง)
        put_plan(page, "S50", "iS", planned=True)
        put_plan(page, "XAUUSD", "iX", planned=False)
        put_open(page, "BTCUSD", "tB"); release_sync(page)
        go(page)
        p = picks(page)
        check(f"{tag} 3 pick 3 ตัวตามลำดับ: ไม้เปิด BTC → แผนที่มีไม้รอ S50 → แผนร่าง XAUUSD (BRENT ร่างเหมือนกันแต่เรียงหลัง)", p == ["BTCUSD", "S50", "XAUUSD"], p)
        rest = [k for k in ("BTCUSD", "S50", "BRENT", "XAUUSD") if k not in p]
        check(f"{tag} 3 ตัวที่ 4 ไม่อยู่ในการ์ด", len(rest) == 1 and rest[0] not in cards(page), [p, cards(page)])
        check(f"{tag} 3 ตัวที่ 4 อยู่แถบ 'ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้'", js(page, "(k)=>{ const e = document.querySelector('[data-wa-park] [data-park=\"'+k+'\"]'); return !!e && document.querySelector('[data-wa-park] summary').innerText.includes('ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้'); }", rest[0]), rest)
        check(f"{tag} 3 ไม่เกิน 3 ใน settings", len((settings(page, "satWeekPick") or {}).get(WK, [])) == 3)
    finally: browser.close()

    # 4 ชิป contrast
    browser, page, ce, pe = launch(pw, w, h)
    try:
        put_plan(page, "XAUUSD", "iX"); put_open(page, "BTCUSD", "tB")
        go(page)
        info = js(page, """()=>{ const n = document.querySelector('.waChip .waName'), c = document.querySelector('.waChip'), m = document.querySelector('.waChip .waMore'), mac = document.querySelector('.waChip .waMac');
          const cs = e=>e ? getComputedStyle(e) : null;
          return {name: cs(n).color, chip: cs(c).backgroundColor, more: m ? cs(m).color : null, moreTxt: m ? m.innerText : null, mac: mac ? [cs(mac).color, cs(mac).backgroundColor] : null, nameTxt: n.innerText, vis: n.getBoundingClientRect().width > 8}; }""")
        nc, _ = rgb(info["name"]); bg, _ = rgb(info["chip"])
        r = contrast(nc, bg)
        check(f"{tag} 4 contrast ชื่อ Asset (.waName) กับพื้นชิป ≥ 4.5 (ได้ {r:.2f})", r >= 4.5, info)
        check(f"{tag} 4 ชื่อมองเห็น (กว้าง>8px · มีข้อความ)", info["vis"] and len(info["nameTxt"]) > 0, info)
        mc, _ = rgb(info["more"]); check(f"{tag} 4 ปุ่ม ⋯ ยังเห็นและ contrast ≥ 4.5", info["moreTxt"] == "⋯" and contrast(mc, bg) >= 4.5, info)
        if info["mac"]:
            a, _ = rgb(info["mac"][0]); b, _ = rgb(info["mac"][1])
            check(f"{tag} 4 ป้าย Macro ในชิปอ่านได้ (contrast ≥ 3)", contrast(a, b) >= 3, info["mac"])
        else: check(f"{tag} 4 ป้าย Macro ในชิป", False, "ไม่พบ")
        check(f"{tag} 4 ปุ่ม ＋ Asset (ถ้ามี) อ่านได้บนพื้นดำ", True if not js(page, "()=>!!document.querySelector('[data-wa-add]')") else contrast(rgb(js(page, "()=>getComputedStyle(document.querySelector('[data-wa-add]')).color"))[0], rgb(js(page, "()=>getComputedStyle(document.getElementById('satV3Sum')).backgroundColor"))[0]) >= 4.5)
        shot(page, f"wa1fix-chips-{sfx}.png", ".waBar")
        check(f"{tag} 6 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [ce, pe])
    finally: browser.close()


def static_checks():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("5 static: ไม่เหลือ data-wa-legacy", "data-wa-legacy" not in src)
    check("5 static: ไม่เหลือข้อความ 'แสดงทุกตัว'", "แสดงทุกตัว" not in src)
    check("5 static: ไม่เหลือ satWeekPickOn", "satWeekPickOn" not in src)


if __name__ == "__main__":
    static_checks()
    with sync_playwright() as pw:
        for (w, h, label) in [(1440, 900, "1440px"), (390, 844, "390px")]:
            tests(pw, w, h, label)
    bad = [r for r in results if not r[1]]
    print(f"engine={ENGINE}  PASS: {len(results)-len(bad)}  FAIL: {len(bad)}  TOTAL: {len(results)}")
    if bad: print("FAILURES:"); [print(" -", r[0]) for r in bad]
