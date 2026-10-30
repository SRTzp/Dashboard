#!/usr/bin/env python3
"""TR1fix — จำ Asset ที่เอาออกจากสัปดาห์ (satWeekDrop) · AI vs เรา ปุ่มเฉพาะแถวที่ต้องตัดสิน · ขัดเกลา (ฟอนต์/ฟอร์ม Product/ป้ายซ้ำ/การ์ด Strategy 390) · เทส 74
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย (สัปดาห์นี้ = 2026-09-27)
ภาพ tests/screenshots/tr1fix-{vs,drop-parked,product-form,strategy}-{1440,390}.png
รัน: python3 run_tests_phase74.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase54 as P54
import run_tests_phase72 as P72
import run_tests_phase73 as P73

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
WK = "2026-09-27"; NEXT = "2026-10-04"
settings, overflow, txt, cnt = P54.settings, P54.overflow, P73.txt, P73.cnt


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


def drop(page, wk=WK): return js(page, "(w)=>satWeekDropList(w)", wk)
def picks(page): return js(page, "()=>satWeekPickList()")
def resync(page): js(page, "()=>{ satCarrySig = ''; satCarrySync(); satV3Render(); }"); page.wait_for_timeout(250)


def vs_ai(**kw):
    return P73.trade_ai(id="t-vs", **kw)


def six_rows(page):
    pass


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # 1 เอา XAUUSD ออก → drop · ไม่กลับเข้า pick · อยู่แถบไม้ค้าง · เปิดไม้ใหม่/Activate บล็อก
    browser, page, ce, pe = P72.launch(pw, w, h)
    try:
        P72.hold_sync(page); P72.put_plan(page, "XAUUSD", "iX", planned=False); P72.release_sync(page)
        P72.go(page)
        check(f"{tag} 1 มีแผน XAUUSD สัปดาห์นี้ → อยู่ใน pick · drop ว่าง", picks(page) == ["XAUUSD"] and drop(page) == [], [picks(page), drop(page)])
        page.locator(".waChip .waMore").first.click(); page.wait_for_timeout(200)
        page.locator("[data-wa-remove]").click(); page.wait_for_timeout(400)
        check(f"{tag} 1 เอาออก → satWeekDrop[สัปดาห์นี้] มี XAUUSD (เก็บใน settings จริง) · pick ว่าง", drop(page) == ["XAUUSD"] and (settings(page, "satWeekDrop") or {}).get(WK) == ["XAUUSD"] and picks(page) == [], [drop(page), picks(page)])
        resync(page); js(page, "()=>{ render(); satV3Render(); }"); page.wait_for_timeout(300)
        check(f"{tag} 1 render/ซิงก์ซ้ำ → ไม่กลับเข้า pick", picks(page) == [] and "XAUUSD" not in P72.cards(page), [picks(page), P72.cards(page)])
        check(f"{tag} 1 อยู่แถบ 'ไม้ค้าง · ไม่ได้เลือกสัปดาห์นี้'", js(page, "()=>!!document.querySelector('[data-wa-park] [data-park=XAUUSD]')"))
        shot(page, f"tr1fix-drop-parked-{sfx}.png", "#satV3Panel")
        # จำลองเปิดแอปใหม่: ล้างสถานะ in-memory ของ sync + อ่านจาก settings ใหม่
        js(page, "()=>{ satCarrySig = ''; waParkOpen = false; switchTab('today'); }"); page.wait_for_timeout(300)
        P72.go(page)
        check(f"{tag} 1 กลับมาเปิดหน้า Strategy ใหม่ → ยังไม่ใน pick · ยังใน drop", picks(page) == [] and drop(page) == ["XAUUSD"], [picks(page), drop(page)])
        blocked = js(page, "()=>{ const i = satIdeasList.find(x=>x.asset==='XAUUSD'); return !!i; }")
        js(page, "()=>{ const i = satIdeasList.find(x=>x.asset==='XAUUSD'); satV3Sel = 'XAUUSD'; satV3Render(); }")
        act_blocked = js(page, "()=>{ const i = satIdeasList.find(x=>x.asset==='XAUUSD'); const c = (i.conditions||[])[0]; const before = JSON.stringify(i.conditions||[]); if(c) satV3CondActivate(i.id, c.id, true); return JSON.stringify(sat7dIdea(i.id).conditions||[]) === before; }")
        check(f"{tag} 1 ยังมีแผน XAUUSD อยู่ · Activate เงื่อนไขใหม่ถูกบล็อก (ไม่เปลี่ยนข้อมูล)", blocked and act_blocked)
        check(f"{tag} 1 {label} ไม่มี console error · ไม่ล้นแนวนอน", not ce and not pe and overflow(page) <= 1, [ce, pe, overflow(page)])
        # 2 ＋ Asset กลับ → ออกจาก drop
        js(page, "()=>waSheetOpen()"); page.wait_for_timeout(300)
        page.locator("[data-wa-pick='XAUUSD']").click(); page.wait_for_timeout(400)
        check(f"{tag} 2 ＋ Asset XAUUSD กลับ → อยู่ใน pick · ออกจาก drop", picks(page) == ["XAUUSD"] and drop(page) == [], [picks(page), drop(page)])
        resync(page)
        check(f"{tag} 2 หลังเพิ่มกลับ sync ซ้ำก็ยังอยู่ · แถบไม้ค้างหาย", picks(page) == ["XAUUSD"] and js(page, "()=>!document.querySelector('[data-wa-park]')"))
        # 2b ปุ่ม 'เพิ่มกลับ' ในแถบไม้ค้างก็เอาออกจาก drop
        page.locator(".waChip .waMore").first.click(); page.wait_for_timeout(200); page.locator("[data-wa-remove]").click(); page.wait_for_timeout(300)
        js(page, "()=>{ document.querySelector('[data-wa-park]').open = true; waParkOpen = true; }")
        page.locator("[data-park-add='XAUUSD']").click(); page.wait_for_timeout(400)
        check(f"{tag} 2 ปุ่ม เพิ่มกลับ (แถบไม้ค้าง) → ออกจาก drop เหมือนกัน", picks(page) == ["XAUUSD"] and drop(page) == [], [picks(page), drop(page)])
        # 3 สัปดาห์ถัดไป
        page.locator(".waChip .waMore").first.click(); page.wait_for_timeout(200); page.locator("[data-wa-remove]").click(); page.wait_for_timeout(300)
        js(page, """()=>{ const R = Date, off = 7*86400000; window.Date = class extends R { constructor(...a){ if(a.length===0) super(R.now()+off); else super(...a); } static now(){ return R.now()+off; } }; satCarrySig = ''; satCarrySync(); satV3Render(); }""")
        page.wait_for_timeout(400)
        check(f"{tag} 3 สัปดาห์ถัดไป ({NEXT}) → drop ของสัปดาห์นั้นว่าง", js(page, "()=>wpWeekKey()") == NEXT and drop(page, NEXT) == [], [js(page, "()=>wpWeekKey()"), drop(page, NEXT)])
        check(f"{tag} 3 สัปดาห์ถัดไป auto-pick ใส่ XAUUSD ตามปกติ (แผนยกมา/ไม้ค้างข้ามสัปดาห์ยังอยู่)", picks(page) == ["XAUUSD"], picks(page))
        check(f"{tag} 3 drop ของสัปดาห์เดิมยังอยู่ (ไม่ปนข้ามสัปดาห์)", drop(page, WK) == ["XAUUSD"], drop(page, WK))
    finally: browser.close()

    # 2c ＋ วางแผน จากไอเดียเทรด → เอาออกจาก drop
    browser, page, ce, pe = P73.launch(pw, w, h, trades=[(("t-p2",), {"ai": None, "me": {"title": "Fed ลดดอก → ทองขึ้น", "dir": "long", "date": "2026-09-30", "asset_hint": "XAUUSD", "wrong_if": ["Fed เซอร์ไพรส์เหยี่ยว"], "one_line": "ทองขึ้น"}, "user": {"expires": "2026-10-20"}})])
    try:
        js(page, "()=>satSettingsWrite(s=>{ s.satWeekDrop = {['%s']: ['XAUUSD']}; })" % WK)
        P73.go(page, "t-p2")
        check(f"{tag} 2 ตั้งต้น XAUUSD อยู่ใน drop", drop(page) == ["XAUUSD"], drop(page))
        page.click("[data-trade-plan]"); page.wait_for_timeout(600)
        check(f"{tag} 2 ＋ วางแผน จากไอเดียเทรด → เข้า pick · ออกจาก drop", picks(page) == ["XAUUSD"] and drop(page) == [], [picks(page), drop(page)])
    finally: browser.close()

    # 4 AI vs เรา
    me4 = {"title": "ไอเดียของฉัน", "date": "2026-09-30", "dir": "long", "tf": "D", "strength": "high", "horizon": "1 สัปดาห์", "wrong_if": ["แตกแนวรับ"]}
    browser, page, ce, pe = P73.launch(pw, w, h, trades=[(("t-vs",), {"ai": vs_ai(), "me": me4, "user": {"expires": "2026-10-20"}})])
    try:
        P73.go(page, "t-vs"); P73.tab(page, "vs")
        rows = js(page, "()=>[...document.querySelectorAll('[data-trade-row]')].map(r=>({k:r.dataset.tradeRow, flag:(r.querySelector('[data-trade-flag]')||{dataset:{}}).dataset.tradeFlag||'', btns:[...(r.nextElementSibling&&r.nextElementSibling.classList.contains('trdVsA') ? r.nextElementSibling.querySelectorAll('button') : [])].map(b=>b.innerText.trim())}))")
        m = {r["k"]: r for r in rows}
        check(f"{tag} 4 แถวตรงกัน (ระยะ · ผิดเมื่อ) ไม่มีป้าย ไม่มีปุ่ม", m["horizon"]["btns"] == [] and m["wrong_if"]["btns"] == [] and m["horizon"]["flag"] == "", rows)
        check(f"{tag} 4 แถว ต่าง/ขาด มี 2 ปุ่ม: '← ใช้ของ AI' · 'คงของเรา'", all(m[k]["btns"] == ["← ใช้ของ AI", "คงของเรา"] for k in ("dir", "strength", "counter", "alts")), rows)
        check(f"{tag} 4 ไม่มีปุ่ม 'เขียนของเรา' / 'รับทราบ' / 'ใช้ข้อของ AI'", js(page, "()=>!/เขียนของเรา|รับทราบ|ใช้ข้อของ AI/.test(document.querySelector('[data-trade-vs]').innerText) && !document.querySelector('[data-trade-write]')"))
        one = js(page, """()=>[...document.querySelectorAll('.trdVsA')].map(r=>{ const b = [...r.querySelectorAll('button')].map(x=>Math.round(x.getBoundingClientRect().top)); return b.length===2 && b[0]===b[1]; })""")
        check(f"{tag} 4 ปุ่ม 2 ปุ่มอยู่บรรทัดเดียว (top เท่ากัน) ทุกแถว", len(one) == 4 and all(one), one)
        check(f"{tag} 4 ช่อง 'เรา' มีไอคอน ✎ จาง · badge = 4", cnt(page, "[data-trade-me] .trdPen") == 6 and txt(page, "[data-trade-badge]") == "4", txt(page, "[data-trade-badge]"))
        shot(page, f"tr1fix-vs-{sfx}.png", ".wlm")
        if w <= 430:
            hh = js(page, "()=>{ const p = document.querySelector('[data-trade-vs]').closest('.panel'); return Math.round(p.getBoundingClientRect().height); }")
            check(f"{tag} 5 390: แท็บ AI vs เรา สูง ≤ 600 กับ 6 แถว (ได้ {hh})", hh <= 600, hh)
            check(f"{tag} 5 390: ไม่ล้นแนวนอน", overflow(page) <= 1 and js(page, "()=>{ const t = document.querySelector('[data-trade-vs]'); return t.scrollWidth <= t.parentElement.clientWidth + 1; }"), overflow(page))
        # ← ใช้ของ AI
        page.click("[data-trade-use=counter]"); page.wait_for_timeout(300)
        d = P73.idb(page, "t-vs")
        check(f"{tag} 4 ← ใช้ของ AI (ข้อโต้แย้ง) → me ได้ค่า AI · ปุ่มหาย · badge 3", d["me"]["counter"] == ["HBM ยังขาดตลาด"] and cnt(page, "[data-trade-use=counter]") == 0 and cnt(page, "[data-trade-ack=counter]") == 0 and txt(page, "[data-trade-badge]") == "3", [d["me"], txt(page, "[data-trade-badge]")])
        # คงของเรา
        page.click("[data-trade-ack=dir]"); page.wait_for_timeout(300)
        d = P73.idb(page, "t-vs")
        faded = js(page, "()=>{ const e = document.querySelector('[data-trade-row=dir] [data-trade-flag]'); return !!e && e.hasAttribute('data-trade-decided') && parseFloat(getComputedStyle(e).opacity) < 0.9; }")
        check(f"{tag} 4 คงของเรา → user.ack.dir=true · me ไม่เปลี่ยน · ป้ายจางลง · ปุ่มหาย · badge 2", d["user"]["ack"].get("dir") is True and d["me"]["dir"] == "long" and faded and cnt(page, "[data-trade-ack=dir]") == 0 and txt(page, "[data-trade-badge]") == "2", [d["user"], txt(page, "[data-trade-badge]")])
        # แก้ inline: แตะช่อง "เรา" → Enter
        page.click("[data-trade-me=alts]"); page.wait_for_timeout(200)
        check(f"{tag} 4 แตะช่อง 'เรา' → กลายเป็นช่องกรอก inline (ในแถวเดิม ไม่มีแถวฟอร์มแยก)", cnt(page, "[data-trade-row=alts] #trdEditIn") == 1 and cnt(page, ".trdEdit") == 0)
        page.fill("#trdEditIn", "ทางของฉัน 1"); page.keyboard.press("Enter"); page.wait_for_timeout(300)
        d = P73.idb(page, "t-vs")
        check(f"{tag} 4 Enter = บันทึก → me.alts · แถวหายป้าย/ปุ่ม (ตรงกับ AI? ไม่ → ยังมีป้ายตามผลเทียบ) ไม่แตะ ai", d["me"]["alts"] == ["ทางของฉัน 1"] and d["ai"]["alts"] == ["Short Samsung แทนดัชนี"] and cnt(page, "[data-trade-row=alts] #trdEditIn") == 0, d["me"])
        check(f"{tag} 4 แก้ alts ด้วยตัวเองแล้ว → ไม่ใช่ 'ขาด' อีก · ปุ่มของแถว alts หาย", cnt(page, "[data-trade-use=alts]") == 0 and cnt(page, "[data-trade-ack=alts]") == 0, txt(page, "[data-trade-vs]"))
        # Esc ยกเลิก
        page.click("[data-trade-me=horizon]"); page.wait_for_timeout(200)
        page.fill("#trdEditIn", "ค่าที่ไม่ควรบันทึก"); page.keyboard.press("Escape"); page.wait_for_timeout(300)
        d = P73.idb(page, "t-vs")
        check(f"{tag} 4 Esc = ยกเลิก (ไม่บันทึก · ช่องปิด)", d["me"]["horizon"] == "1 สัปดาห์" and cnt(page, "#trdEditIn") == 0, d["me"])
        # blur = บันทึก
        page.click("[data-trade-me=horizon]"); page.wait_for_timeout(200)
        page.fill("#trdEditIn", "2 สัปดาห์"); page.locator("[data-trade-vs] th").first.click(); page.wait_for_timeout(400)
        d = P73.idb(page, "t-vs")
        check(f"{tag} 4 blur = บันทึก", d["me"]["horizon"] == "2 สัปดาห์" and cnt(page, "#trdEditIn") == 0, d["me"])
        # แก้ช่องเราจนตรงกับ AI → ป้ายหาย badge ลด
        b0 = txt(page, "[data-trade-badge]")
        page.click("[data-trade-me=strength]"); page.wait_for_timeout(200)
        page.select_option("#trdEditIn", "mid"); page.keyboard.press("Enter"); page.wait_for_timeout(350)
        b1 = txt(page, "[data-trade-badge]")
        check(f"{tag} 4 แก้ช่องเราจนตรงกับ AI (ความแรง mid) → ปุ่มหาย · badge ลด ({b0}→{b1})", cnt(page, "[data-trade-use=strength]") == 0 and int(b1 or 0) < int(b0 or 0), [b0, b1])
        check(f"{tag} 4 {label} ไม่มี console error", not ce and not pe, [ce, pe])
    finally: browser.close()

    # 6 ฟอนต์ · 7 ฟอร์ม Product · 8 Strategy
    browser, page, ce, pe = P73.launch(pw, w, h, trades=[(("t-vs",), {"ai": vs_ai(products=[{"name": "Put option ETF", "type": "option", "lev": "Option"}, {"name": "KOSPI200 Futures", "type": "futures", "lev": "สูง"}]), "me": me4, "user": {"expires": "2026-10-20"}})])
    try:
        P73.go(page, "t-vs"); P73.tab(page, "vs")
        fam = js(page, "()=>getComputedStyle(document.querySelector('[data-trade-row=dir] td')).fontFamily")
        check(f"{tag} 6 เซลล์ตาราง AI vs เรา ไม่ใช่ monospace ({fam[:40]})", "mono" not in fam.lower(), fam)
        js(page, "()=>trdNewOpen()"); page.wait_for_timeout(300)
        fams = js(page, "()=>['trdNewNews','trdNewChain','trdNewAsset'].map(i=>getComputedStyle(document.getElementById(i)).fontFamily)")
        check(f"{tag} 6 ช่องฟอร์ม ＋ ไอเดีย (3 ช่อง) ไม่ใช่ monospace", all("mono" not in f.lower() for f in fams), fams)
        js(page, "()=>ideaSheetClose()"); page.wait_for_timeout(200)
        P73.tab(page, "prod")
        info = js(page, """()=>{ const g = i=>document.getElementById(i), cs = e=>getComputedStyle(e), n = g('trdProdName'), t = g('trdProdType'), l = g('trdProdLev');
          return {r:[n,t,l].map(e=>parseFloat(cs(e).borderTopLeftRadius)), h:[n,t,l].map(e=>Math.round(e.getBoundingClientRect().height)), bw:[n,t,l].map(e=>cs(e).borderTopWidth), fam:cs(n).fontFamily, bg:cs(n).backgroundColor}; }""")
        ref = js(page, "()=>{ const e = document.createElement('div'); e.className='f'; e.innerHTML='<input>'; document.body.appendChild(e); const c = getComputedStyle(e.firstChild); const r = [parseFloat(c.borderTopLeftRadius), c.backgroundColor]; e.remove(); return r; }")
        check(f"{tag} 7 ฟอร์ม Product: input/select มี border-radius > 0 · พื้นเดียวกับช่องกรอกของแอป · ความสูงเท่ากัน · ไม่ monospace", all(r > 0 for r in info["r"]) and info["bg"] == ref[1] and len(set(info["h"])) == 1 and "mono" not in info["fam"].lower(), [info, ref])
        shot(page, f"tr1fix-product-form-{sfx}.png", ".wlm")
        chips = js(page, "()=>[...document.querySelectorAll('[data-trade-prod]')].map(r=>[...r.querySelectorAll('.trdLev')].map(x=>x.innerText.trim()))")
        check(f"{tag} 7 แถว Product ไม่มีป้ายข้อความซ้ำ (Option/Option → Option 1 ป้าย · Futures+สูง = ประเภท 1 + Leverage 1)", chips == [["Option"], ["Futures", "สูง"]] and all(len(set(c)) == len(c) for c in chips), chips)
    finally: browser.close()

    browser, page, ce, pe = P72.launch(pw, w, h)
    try:
        P72.put_plan(page, "XAUUSD", "iX", planned=False)
        P72.go(page)
        info = js(page, """()=>{ const t = document.querySelector('.ui-tile[data-key=XAUUSD]'), sum = document.querySelector('#satV3Sum'), a = t.querySelector('.ui-tile-a'), b = t.querySelector('.ui-tile-b');
          return {tw:t.getBoundingClientRect().width, sw:sum.getBoundingClientRect().width, aFit:a.scrollWidth <= a.clientWidth+1, bFit:!b || b.scrollWidth <= b.clientWidth+1, name:a.innerText}; }""")
        check(f"{tag} 8 การ์ด Asset: ชื่อไม่ถูกตัด (scrollWidth ≤ clientWidth) · ป้ายทิศ/ขนาดไม้ไม่ถูกตัด", info["aFit"] and info["bFit"], info)
        check(f"{tag} 8 การ์ด Asset ที่เดียวในสัปดาห์: กว้าง ≥ 90% ของแผง ที่ {label} ({info['tw']:.0f}/{info['sw']:.0f})", (info["tw"] / info["sw"] >= 0.9) if w <= 700 else True, info)
        shot(page, f"tr1fix-strategy-{sfx}.png", "#satV3Panel")
        check(f"{tag} 8 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 1 and not ce and not pe, [overflow(page), ce, pe])
    finally: browser.close()


def static_checks():
    src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("9 static: ไม่เหลือปุ่ม data-trade-write / ข้อความ 'เขียนของเรา'", "data-trade-write" not in src and "เขียนของเรา" not in src)
    check("9 static: มี satWeekDrop ใช้ใน waRemove / auto-pick", "satWeekDropWrite" in src and "drop.includes(k)" in src)


if __name__ == "__main__":
    static_checks()
    with sync_playwright() as pw:
        for (w, h, label) in [(1440, 900, "1440px"), (390, 844, "390px")]:
            tests(pw, w, h, label)
    bad = [r for r in results if not r[1]]
    print(f"engine={ENGINE}  PASS: {len(results)-len(bad)}  FAIL: {len(bad)}  TOTAL: {len(results)}")
    if bad: print("FAILURES:"); [print(" -", r[0]) for r in bad]
