#!/usr/bin/env python3
"""7E-2a-fix — การ์ด Core ยุบเป็นแถว (ตรงม็อกอัป docs/mockups/core-card-compact.html โหมด B · ตารางอยู่ใน ⋯) + ป้ายนับไม้ #n/N + ค่าตั้ง maxLots + ข้อความ 0 หุ้นชนเพดาน Tier
mock Firestore · 1440px + 430px (บางข้อ 932px) · ข้อมูล: บัญชีหลัก US ถัง ฿3,500,000 · AAPL 52@100 + 26@110 → 78 @ 103.33 · Stop 90 · ปิด 101 · EMA10 90
รัน: python3 run_tests_phase25.py [/path/to/index.html] · ภาพเก็บที่ tests/screenshots/7e2afix-*.png"""
import copy, json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22
import run_tests_phase23 as p23
import run_tests_phase24 as p24

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
results = []
T = p22.T; bk = p22.bkk_today_minus; TODAY = bk(0)
txt = p24.txt
FX = 33.37


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:600] + "...(truncated)") if (detail and len(detail) > 600) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    try:
        if sel and page.locator(sel).count():
            page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else:
            page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e:
        print("shot fail", name, e)


def usT(id, sym, qty, avg, sl):
    return T(id, "core", "open", sym=sym, entry=avg, sl=sl, qty=qty, cur="USD", date="2026-09-10")


def ucard(id, tid, ticker, lots, sl, **kw):
    return p24.card(id, "main", ticker, market="US", status="open", trade_id=tid, stop=sl, tier=kw.pop("tier", "B"),
                    lots=[{"n": i + 1, "date": "2026-09-30", "px": l[0], "qty": l[1], "f": 1, "stop": sl} for i, l in enumerate(lots)], **kw)


def data(extra_trades=None, extra_cards=None, max_lots=None, main_market="US"):
    trades = [usT("t_aapl", "AAPL", 78, (52 * 100 + 26 * 110) / 78, 90), usT("t_nvda", "NVDA", 40, 125, 120), usT("t_msft", "MSFT", 20, 395, 380),
              usT("t_amzn", "AMZN", 50, 180, 170), usT("t_goog", "GOOG", 30, 140, 130)]
    cards = {
        "aapl": ucard("aapl", "t_aapl", "AAPL", [(100, 52), (110, 26)], 90, px=101, pxDate=TODAY, emaW=90),
        "nvda": ucard("nvda", "t_nvda", "NVDA", [(125, 40)], 120, tier="A", tierReason="moat", px=118, pxDate=bk(5) if False else TODAY, emaW=124),
        "msft": ucard("msft", "t_msft", "MSFT", [(395, 20)], 380, px=412, pxDate=TODAY, emaW=418),
        "amzn": ucard("amzn", "t_amzn", "AMZN", [(180, 50)], 170, px=180, pxDate=bk(12), emaW=170),
        "goog": ucard("goog", "t_goog", "GOOG", [(140, 16), (140, 8), (140, 6)], 130, px=150, pxDate=TODAY, emaW=140),
        "meta": p24.card("meta", "main", "META", market="US", tier="B", plan={"entry": 600, "stop": 560}, stop=560),
    }
    trades += (extra_trades or []); cards.update(extra_cards or {})
    doc = p22.make_doc(main_trades=trades, with_legacy=False)
    st = doc["books"]["main"]["settings"]
    st["capital"]["core"] = 3500000; st["fx"] = FX
    cr = st.setdefault("coreRisk", {}); cr.update({"riskPct": 1, "tierA": 10, "tierB": 5}); cr["market"] = main_market   # CZ1: ค่าเริ่มต้นใหม่ (1.25/15/10) → seed ค่าเดิม ให้ตัวเลขที่คาดเท่าเดิม
    if max_lots is not None: cr["maxLots"] = max_lots
    return doc, cards


def launch(pw, w, h, doc, cards):
    return p24.launch(pw, w, h, doc, cards=cards)


def go(page): p24.go_stock(page)
def row(page, id): return f'[data-core-card="{id}"] [data-c-row]'
def card(page, id): return f'[data-core-card="{id}"]'
def expanded(page, id): return page.get_attribute(row(page, id), "aria-expanded")


def expand(page, id):
    if expanded(page, id) != "true": page.click(row(page, id)); page.wait_for_timeout(80)


def list_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page)
        ex = {k: expanded(page, k) for k in cards}
        check(f"{tag} 1 เริ่มต้นทุกใบยุบ ยกเว้น 🔴 · aria-expanded ถูก", ex == {"aapl": "false", "nvda": "true", "msft": "false", "amzn": "false", "goog": "false", "meta": "false"}, json.dumps(ex))
        check(f"{tag} 1 การ์ดเรียงต่อกันในกรอบเดียว (.ccList) คั่นด้วยเส้น · ทุกใบเป็น <button> แถว", page.locator("#corePanel .ccList").count() == 1 and page.locator("#corePanel .ccList > .ccCard").count() == 6 and page.locator("#corePanel .ccList button.ccRow").count() == 6)
        r = txt(page, row(page, "aapl")) or ""
        need = ["101", "90", "$858", "0.82%", "#2/3"]
        check(f"{tag} 2 แถว AAPL: {' · '.join(need)}", all(x in r for x in need), r)
        if w > 700:
            check(f"{tag} 2 แถว AAPL (1440): มี '78 @ 103.33'", "78 @ 103.33" in r, r)
        else:
            check(f"{tag} 2 แถว AAPL (430): ไม่มี '78 @' แต่มี '#2/3'", "78 @" not in r and "#2/3" in r, r)
        rp = txt(page, row(page, "meta")) or ""
        check(f"{tag} 2 แถวแผน META: 'แผน · Entry 600 · Stop 560 · ไม้แรก 8 หุ้น'", "แผน" in rp and "Entry 600" in rp and "Stop 560" in rp and "ไม้แรก 8 หุ้น" in rp, rp)
        check(f"{tag} 2 แถว 🔴 NVDA: 'ปิดใต้ Stop — ขายหมด' · ⚪ AMZN: 'ขาดราคา (เก่า 12 วัน)'", "ปิดใต้ Stop — ขายหมด" in txt(page, row(page, "nvda")) and "ขาดราคา (เก่า 12 วัน)" in txt(page, row(page, "amzn")))
        check(f"{tag} 2 ป้ายสั้น B·W + title ข้อความเต็ม (US · Tier B · เพดานไม้แรก 5% · ระบบ Week)", txt(page, card(page, "aapl") + " .ccTag") == "B·W" and page.get_attribute(card(page, "aapl") + " .ccTag", "title") == "US · Tier B · เพดานไม้แรก 5% · ระบบ Week")
        order = page.evaluate("()=>[...document.querySelectorAll('#corePanel .ccList > .ccCard')].map(e=>e.dataset.coreCard)")
        check(f"{tag} 3 ลำดับ 🔴 → 🟡 → ⚪ → 🟢 (เสี่ยงมาก→น้อย) → แผน", order == ["nvda", "msft", "amzn", "aapl", "goog", "meta"], str(order))
        shot(page, f"7e2afix-list-collapsed-{w}.png", "#corePanel")
        shot(page, f"7e2afix-red-{w}.png", card(page, "nvda"))
        # 4 กดแถว
        page.click(row(page, "aapl")); page.wait_for_timeout(80)
        a1 = expanded(page, "aapl") == "true" and page.locator(card(page, "aapl") + " .ccBody").is_visible()
        page.click(row(page, "aapl")); page.wait_for_timeout(80)
        a2 = expanded(page, "aapl") == "false" and not page.locator(card(page, "aapl") + " .ccBody").is_visible()
        check(f"{tag} 4 กดแถว = ขยาย · กดซ้ำ = ยุบ", a1 and a2)
        page.focus(row(page, "aapl")); page.keyboard.press("Enter"); page.wait_for_timeout(80)
        e1 = expanded(page, "aapl") == "true"
        page.keyboard.press("Enter"); page.wait_for_timeout(80)
        check(f"{tag} 4 Enter บนแถว = ขยาย/ยุบ", e1 and expanded(page, "aapl") == "false")
        page.click('[data-c-expandall]'); page.wait_for_timeout(150)
        allo = page.evaluate("()=>[...document.querySelectorAll('[data-c-row]')].every(b=>b.getAttribute('aria-expanded')==='true')")
        page.click('[data-c-collapseall]'); page.wait_for_timeout(150)
        allc = page.evaluate("()=>[...document.querySelectorAll('[data-c-row]')].every(b=>b.getAttribute('aria-expanded')==='false')")
        check(f"{tag} 4 ขยายทั้งหมด / ยุบทั้งหมด ทำงาน (ยุบทั้งหมดรวม 🔴)", allo and allc)
        # 🔴 กดยุบเอง → คงยุบหลังวาดใหม่
        expand(page, "nvda"); page.click(row(page, "nvda")); page.evaluate("()=>render()"); page.wait_for_timeout(150)
        check(f"{tag} 1 🔴 ที่ผู้ใช้กดยุบเอง → ไม่ขยายซ้ำหลังวาดใหม่", expanded(page, "nvda") == "false")
        # 11 ความสูง
        hrow = page.evaluate("()=>document.querySelector('[data-core-card=\"aapl\"] [data-c-row]').getBoundingClientRect().height")
        lim_r = 56 if w > 700 else 76
        maxrow = page.evaluate("()=>Math.max(...[...document.querySelectorAll('#corePanel [data-c-row]')].map(b=>b.getBoundingClientRect().height))")
        check(f"{tag} 11 แถวยุบสูง ≤ {lim_r}px (สูงสุดจริง {maxrow:.0f}px)", maxrow <= lim_r, f"{maxrow}")
        expand(page, "aapl")
        hc = page.evaluate("()=>document.querySelector('[data-core-card=\"aapl\"]').getBoundingClientRect().height")
        lim_c = 230 if w > 700 else 420
        check(f"{tag} 11 การ์ดขยาย (กล่องเติมไม้ปิด) สูง ≤ {lim_c}px (จริง {hc:.0f}px)", hc <= lim_c, f"{hc}")
        print(f"   วัดจริง {label}: แถวยุบ AAPL {hrow:.0f}px · สูงสุด {maxrow:.0f}px · การ์ดขยาย {hc:.0f}px")
        check(f"{tag} 11 ไม่ล้นแนวนอน: #corePanel scrollWidth ≤ clientWidth", page.evaluate("()=>{const e=document.getElementById('corePanel');return e.scrollWidth<=e.clientWidth+1 && document.documentElement.scrollWidth<=innerWidth+1}"))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def expand_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page); expand(page, "aapl")
        c = card(page, "aapl")
        check(f"{tag} 5 ส่วนขยาย 4 ช่อง · ไม่มีแถบ Week/Tier · ไม่มีตาราง pyramid ในการ์ด · ไม่มี ccNote ในการ์ด (มี 1 ที่หัวแผง)",
              page.locator(c + " .ccGrid4 .ccFld").count() == 4 and page.locator(c + " .ccSeg").count() == 0 and page.locator(c + " [data-c-pyr]").count() == 0 and page.locator(c + " .ccNote").count() == 0 and page.locator("#corePanel .ccNote").count() == 1)
        vals = {k: txt(page, f"{c} [data-c-{k}]") for k in ("px", "ema", "stop", "emg", "hold", "riskpx", "riskcost")}
        check(f"{tag} 5 ค่า data-c-*: px 101 · ema 90 · stop 90 · emg 83.7 · hold '78 @ 103.33' + small 'ไม้ 2/3' · riskpx $858 · riskcost 'จากทุน $1,040'",
              vals["px"] == "101" and vals["ema"] == "90" and vals["stop"] == "90" and vals["emg"] == "83.7" and vals["hold"] == "78 @ 103.33" and txt(page, f"{c} [data-c-lotsub]") == "ไม้ 2/3" and vals["riskpx"] == "$858" and vals["riskcost"] == "จากทุน $1,040", json.dumps(vals, ensure_ascii=False))
        body = txt(page, c + " .ccBody") or ""
        check(f"{tag} 5 ช่อง 4: '0.82% ของถัง ≈฿28,631 · จากทุน $1,040' · ช่อง 1: วันที่ · อายุ 0 วัน", "0.82% ของถัง ≈฿28,631 · จากทุน $1,040" in body and "อายุ 0 วัน" in body, body)
        # ปุ่มแถวเดียว
        bt = page.evaluate("(c)=>[...document.querySelectorAll(c+' .ccBtns > .ccBtn')].map(b=>b.textContent.trim())", c)
        ys = page.evaluate("(c)=>[...new Set([...document.querySelectorAll(c+' .ccBtns > .ccBtn')].map(b=>Math.round(b.getBoundingClientRect().top)))]", c)
        check(f"{tag} 3 ปุ่ม: [เติมไม้] [อัปเดตราคา] [เลื่อน Stop] [⋯] อยู่แถวเดียว (ไม่ขึ้นบรรทัดใหม่)", bt == ["เติมไม้", "อัปเดตราคา", "เลื่อน Stop", "⋯"] and len(ys) == 1, f"{bt} {ys}")
        # 6 กล่องเติมไม้
        check(f"{tag} 6 กล่องจำลองไม้เติมซ่อนก่อน", not page.locator(c + " [data-c-simbox]").is_visible())
        page.click(c + " [data-c-addbtn]"); page.wait_for_timeout(100)
        check(f"{tag} 6 กด [เติมไม้] → เห็นกล่อง", page.locator(c + " [data-c-simbox]").is_visible())
        page.fill(c + " [data-c-simpx]", "115"); page.fill(c + " [data-c-simstop]", "100"); page.wait_for_timeout(150)
        ref = page.evaluate("()=>{ const c = coreCardsList.find(x=>x.id==='aapl'), cx = coreCtx('main'); const s = coreSimCalc(coreView(c,cx),cx); return {qty:s.r.qty, tag:s.r.tag, carry:s.r.carry, newRisk:s.r.newRisk}; }")
        shown = txt(page, c + " [data-c-addqty]")
        check(f"{tag} 6 กรอก 115 / 100 → ผลเท่า coreSimCalc ({ref['qty']} หุ้น · {ref['tag']})", shown == str(ref["qty"]) and ref["qty"] > 0, f"{shown} {ref}")
        shot(page, f"7e2afix-addlot-open-{w}.png", c)
        page.click(c + " [data-c-simcancel]"); page.wait_for_timeout(100)
        check(f"{tag} 6 [ยกเลิก] ปิดกล่อง", not page.locator(c + " [data-c-simbox]").is_visible())
        shot(page, f"7e2afix-card-expanded-{w}.png", c)
        # 7 ปุ่มตามสถานะ
        expand(page, "msft"); expand(page, "nvda"); expand(page, "amzn")
        ms = page.locator(card(page, "msft") + " [data-c-addbtn]")
        check(f"{tag} 7 🟡: [เติมไม้] disabled + title 'ปิดใต้ EMA10 — งดเพิ่มไม้'", ms.is_disabled() and ms.get_attribute("title") == "ปิดใต้ EMA10 — งดเพิ่มไม้")
        first_n = page.evaluate("(c)=>{ const b=document.querySelector(c+' .ccBtns > .ccBtn'); return {t:b.textContent.trim(), dn:b.classList.contains('dn'), pri:b.classList.contains('pri'), cs:getComputedStyle(b).backgroundColor}; }", card(page, "nvda"))
        check(f"{tag} 7 🔴: ปุ่มแรก = [ปิดตำแหน่ง] สีแดง (ไม่มีปุ่มเติมไม้)", first_n["t"] == "ปิดตำแหน่ง" and first_n["dn"] and page.locator(card(page, "nvda") + " [data-c-addbtn]").count() == 0, json.dumps(first_n))
        first_a = page.evaluate("(c)=>{ const b=document.querySelector(c+' .ccBtns > .ccBtn'); return {t:b.textContent.trim(), pri:b.classList.contains('pri')}; }", card(page, "amzn"))
        check(f"{tag} 7 ⚪: ปุ่มแรก = [อัปเดตราคา] สีหลัก · เติมไม้ disabled", first_a["t"] == "อัปเดตราคา" and first_a["pri"] and page.locator(card(page, "amzn") + " [data-c-addbtn]").is_disabled())
        check(f"{tag} 3 🔴 พื้นการ์ดแดงอ่อน", page.evaluate("(c)=>getComputedStyle(document.querySelector(c)).backgroundColor", card(page, "nvda")) != "rgb(255, 255, 255)")
        # plan
        expand(page, "meta")
        pl = txt(page, card(page, "meta") + " .ccBody") or ""
        check(f"{tag} 3 plan ขยาย: UX2 แทนกล่อง 4 ช่อง → Entry · Stop บรรทัดเดียว · FF · ไม้แรก 8 หุ้น (ตัวใหญ่) + ตัวคุมใน วิธีคิด + [บันทึกซื้อไม้ 1] [ลบแผน]", page.locator(card(page, "meta") + " .ccGrid4").count() == 0 and page.locator(card(page, "meta") + " [data-c-entry]").count() == 1 and page.locator(card(page, "meta") + " [data-c-ff]").count() == 1 and "ไม้แรก" in pl and "8 หุ้น" in pl and "คุมด้วยเพดาน Tier B (5%)" in (page.locator(card(page, "meta") + " [data-c-ctl]").text_content() or "") and page.locator(card(page, "meta") + " [data-c-buy1]").count() == 1 and page.locator(card(page, "meta") + " [data-c-delplan]").count() == 1, pl)
        check(f"{tag} 1b plan ไม่มีป้าย #n/N", page.locator(card(page, "meta") + " [data-c-lotbadge]").count() == 0)
        shot(page, f"7e2afix-plan-{w}.png", card(page, "meta"))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def menu_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page); expand(page, "aapl"); c = card(page, "aapl")
        page.click(c + " [data-c-more]"); page.wait_for_timeout(100)
        g = page.evaluate("(c)=>{ const m=document.querySelector(c+' .ccMenu'), r=m.getBoundingClientRect(), b=document.querySelector(c+' [data-c-more]').getBoundingClientRect(); return {on:m.classList.contains('on'), l:r.left, r:r.right, t:r.top, b:r.bottom, btop:b.top, bt:b.bottom, iw:innerWidth, txt:m.innerText.replace(/\\s+/g,' ')}; }", c)
        check(f"{tag} 8 ⋯ เปิดเมนูใต้ปุ่ม (หรือพลิกขึ้นบนถ้าที่ไม่พอ · fix2) · กรอบเมนูอยู่ในจอ (ไม่ถูกตัด)", g["on"] and g["l"] >= 0 and g["r"] <= g["iw"] and (g["t"] >= g["bt"] - 1 or g["b"] <= g["btop"] + 1) and g["t"] >= 0, json.dumps(g, ensure_ascii=False))
        check(f"{tag} 8 เมนู: 'ดูไม้ที่ซื้อ (2)' · แก้ Entry/SL · ปิดตำแหน่ง · Tier… · ซื้อแล้ว — ล็อกกลยุทธ์ (disabled) (7E-2b-1)",
              all(x in g["txt"] for x in ("ดูไม้ที่ซื้อ (2)", "แก้ Entry/SL", "ปิดตำแหน่ง", "Tier…", "ซื้อแล้ว — ล็อกกลยุทธ์")) and page.locator(c + " .ccMenu [data-c-strat=L]").is_disabled(), g["txt"])
        shot(page, f"7e2afix-menu-{w}.png", c)
        page.click(c + " .ccMenu [data-c-edit-btn]"); page.wait_for_timeout(200)
        check(f"{tag} 8 แก้ Entry/SL → openTradeEdit (#teOverlay)", page.locator("#teOverlay.show").count() == 1)
        page.evaluate("closeTradeEdit()")
        page.click(c + " [data-c-more]"); page.click(c + ' .ccMenu [data-c-tierbtn]'); page.wait_for_timeout(200)
        check(f"{tag} 8 Tier… → coreTierOpen (sheet Tier)", p24.sheet_open(page, "tier"))
        page.evaluate("coreSheetClose()")
        page.click(c + " [data-c-more]"); page.wait_for_timeout(80)
        page.mouse.click(5, 5); page.wait_for_timeout(80)
        o1 = page.locator(c + " .ccMenu.on").count() == 0
        page.click(c + " [data-c-more]"); page.wait_for_timeout(80); page.keyboard.press("Escape"); page.wait_for_timeout(80)
        check(f"{tag} 8 คลิกนอกเมนู / Esc = ปิด", o1 and page.locator(c + " .ccMenu.on").count() == 0)
        # 9 ดูไม้ที่ซื้อ
        page.click(c + " [data-c-more]"); page.click(c + " .ccMenu [data-c-lots-btn]"); page.wait_for_timeout(200)
        sh = txt(page, ".core-sheet [data-core-sheet=lots]") or ""
        rows = page.evaluate("()=>[...document.querySelectorAll('.core-sheet [data-c-pyr] tbody tr')].map(r=>[...r.cells].map(c=>c.textContent.trim()))")
        check(f"{tag} 9 'ดูไม้ที่ซื้อ (2)' → sheet 'AAPL · ไม้ที่ซื้อ' · ตาราง 2 แถว (100/52 · 110/26) · 'ถือ 78 @ 103.33' · หัว Stop", "AAPL · ไม้ที่ซื้อ" in sh and len(rows) == 2 and rows[0][2] == "100" and rows[0][3] == "52" and rows[1][2] == "110" and rows[1][3] == "26" and "ถือ 78 @ 103.33" in sh and "Stop ปัจจุบัน 90" in sh, json.dumps(rows) + sh)
        ov = page.evaluate("()=>{ const s=document.querySelector('.core-sheet .ui-sheet'); return {sw:s.scrollWidth, cw:s.clientWidth}; }")
        check(f"{tag} 9 sheet ไม่ล้นแนวนอน", ov["sw"] <= ov["cw"] + 1, json.dumps(ov))
        shot(page, f"7e2afix-pyramid-sheet-{w}.png", ".core-sheet .ui-sheet")
        page.click("[data-c-lots-close]"); page.wait_for_timeout(100)
        check(f"{tag} 9 ปิด sheet ได้", not p24.sheet_open(page, "lots"))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def text_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data(main_market="both")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page)
        page.evaluate("coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        page.fill("#cnTicker", "XXX.BK"); page.click("#cnTierB"); page.fill("#cnEntry", "2000"); page.fill("#cnStop", "1999"); page.click('#cnF button[data-f="1"]'); page.wait_for_timeout(100)
        z = txt(page, "#cnRes [data-c-zero]") or ""
        check(f"{tag} 10 0 หุ้นเพราะชนเพดาน Tier (Tier B 2000/1999 TH) → 'ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿175,000) → ใช้ Tier A หรือข้ามตัวนี้'", z == "ราคาต่อ 1 หลัก (100) เกินเพดาน Tier B (฿175,000) → ใช้ Tier A หรือข้ามตัวนี้", z)
        page.click("#cnTierA"); page.fill("#cnReason", "x"); page.fill("#cnEntry", "1000"); page.fill("#cnStop", "100"); page.wait_for_timeout(100)
        z = txt(page, "#cnRes [data-c-zero]") or ""
        check(f"{tag} 10 0 หุ้นเพราะงบเสี่ยงคุม (Tier A 1000/100) → ข้อความเดิม 'ต่ำกว่า 1 หลัก (100) — ขยายงบหรือเลื่อน Stop'", z == "ต่ำกว่า 1 หลัก (100) — ขยายงบหรือเลื่อน Stop", z)
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def persist_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page); expand(page, "aapl"); expand(page, "goog")
        ls = page.evaluate("()=>JSON.parse(localStorage.getItem('coreCardsOpen'))")
        check(f"{tag} 12 สถานะขยายเก็บใน localStorage (ไม่เขียน Firestore)", sorted(ls) == ["aapl", "goog"], str(ls))
        sets0 = page.evaluate("()=>(window.__setLog||[]).length")
        page.evaluate("()=>{ coreOpen.clear(); coreLoadOpen(); render(); }"); page.wait_for_timeout(150)
        check(f"{tag} 12 รีเฟรช (โหลดใหม่จาก localStorage) → AAPL/GOOG ยังขยาย · ใบอื่นยุบ", expanded(page, "aapl") == "true" and expanded(page, "goog") == "true" and expanded(page, "msft") == "false")
        page.evaluate("()=>{ setPlanAcct('fam'); }"); page.wait_for_timeout(100)
        page.evaluate("()=>{ setPlanAcct('all'); }"); page.wait_for_timeout(100)
        check(f"{tag} 12 สลับตัวกรองบัญชีแล้วกลับ → สถานะขยายคงอยู่", expanded(page, "aapl") == "true")
        page.evaluate("()=>{ window.__gi = Storage.prototype.getItem; window.__si = Storage.prototype.setItem; Storage.prototype.getItem = ()=>{ throw new Error('boom'); }; Storage.prototype.setItem = ()=>{ throw new Error('boom'); }; coreLoadOpen(); render(); }"); page.wait_for_timeout(150)
        check(f"{tag} 12 localStorage.getItem โยน error → ยุบทั้งหมด (🔴 ยังขยาย) ไม่พัง", expanded(page, "aapl") == "false" and expanded(page, "goog") == "false" and expanded(page, "nvda") == "true")
        page.click(row(page, "aapl")); page.wait_for_timeout(100)
        check(f"{tag} 12 localStorage.setItem โยน error → กดขยายยังทำงาน ไม่พัง", expanded(page, "aapl") == "true")
        page.evaluate("()=>{ Storage.prototype.getItem = window.__gi; Storage.prototype.setItem = window.__si; }")
        check(f"{tag} 12 ไม่มีการเขียน Firestore จากการขยาย/ยุบ", page.evaluate("()=>(window.__setLog||[]).length") == sets0)
        check(f"{tag} ไม่มี pageerror", not pe, str(pe[:3]))
    finally:
        browser.close()


def lots_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page); expand(page, "aapl"); expand(page, "goog")
        check(f"{tag} 13 AAPL ช่องถือ = '78 @ 103.33 · ไม้ 2/3' · แถว #2/3", txt(page, card(page, "aapl") + " [data-c-lotsub]") == "ไม้ 2/3" and txt(page, card(page, "aapl") + " [data-c-hold]") == "78 @ 103.33" and "#2/3" in txt(page, row(page, "aapl")))
        gb = txt(page, row(page, "goog")) or ""
        add = page.locator(card(page, "goog") + " [data-c-addbtn]")
        check(f"{tag} 13 การ์ด 3 ไม้ = '#3/3 ครบ' (เทา) · เติมไม้ disabled title 'ครบ 3 ไม้แล้ว'", "#3/3 ครบ" in gb and add.is_disabled() and add.get_attribute("title") == "ครบ 3 ไม้แล้ว" and page.locator(card(page, "goog") + " .ccLot.nt").count() == 1, gb)
        bl = page.evaluate("()=>{ coreSim['goog'] = {px:'150', stop:'140'}; const c = coreCardsList.find(x=>x.id==='goog'), cx = coreCtx('main'); const s = coreSimCalc(coreView(c,cx),cx); return {ok:s.ok, blocked:s.blocked, qty:s.r&&s.r.qty}; }")
        check(f"{tag} 13 coreSimCalc(3 ไม้) blocked มี 'ครบ 3 ไม้แล้ว' (ตัวเลขอื่นไม่เปลี่ยน)", bl["ok"] and "ครบ 3 ไม้แล้ว" in bl["blocked"], json.dumps(bl, ensure_ascii=False))
        shot(page, f"7e2afix-full-lots-{w}.png", card(page, "goog"))
        # ตั้งค่า
        def setmax(v):
            page.evaluate("openSettings()"); page.wait_for_timeout(150)
            page.evaluate("()=>document.querySelectorAll('#setOverlay details').forEach(d=>d.open=true)")
            page.fill("#sCrMaxLots", str(v)); page.wait_for_timeout(80)
        setmax(4)
        ex = txt(page, "#crLotsEx") or ""
        page.click("#setSaveBtn"); page.wait_for_timeout(700)
        gb = txt(page, row(page, "goog")) or ""
        check(f"{tag} 13 ตั้ง maxLots 4 → '#3/4' + เติมไม้กดได้", "#3/4" in gb and not page.locator(card(page, "goog") + " [data-c-addbtn]").is_disabled(), gb)
        setmax(2)
        page.click("#setSaveBtn"); page.wait_for_timeout(700)
        gb = txt(page, row(page, "goog")) or ""
        check(f"{tag} 13 ตั้ง maxLots 2 → การ์ด 3 ไม้ = '#3/2' สีเหลือง", "#3/2" in gb and page.locator(card(page, "goog") + " .ccLot.warn").count() == 1 and "ครบ" not in gb, gb)
        cfgm = page.evaluate("()=>coreRiskCfg('main').maxLots")
        for bad in ("0", "7", "2.5", ""):
            setmax(bad)
            st = page.evaluate("()=>({dis:document.getElementById('setSaveBtn').disabled, err:(document.querySelector('.crErr[data-err-for=sCrMaxLots]')||{}).textContent||''})")
            check(f"{tag} 13 ค่าผิด maxLots={bad!r} → ข้อความแดง + ปุ่มบันทึกล็อก (ไม่บันทึก)", st["dis"] and "1–6" in st["err"], json.dumps(st, ensure_ascii=False))
            page.evaluate("()=>document.querySelectorAll('.overlay.show').forEach(e=>e.classList.remove('show'))")
        check(f"{tag} 13 ค่าผิดไม่ถูกบันทึก: ค่ายังเป็น 2", page.evaluate("()=>coreRiskCfg('main').maxLots") == 2 == cfgm)
        bad = page.evaluate("()=>{ const out = {}; [0,7,2.5,null,'3'].forEach(v=>{ const s = state.settings; const old = s.coreRisk.maxLots; s.coreRisk.maxLots = v; out[String(v)] = coreRiskCfg('main').maxLots; s.coreRisk.maxLots = old; }); return out; }")
        check(f"{tag} 13 coreRiskCfg: ค่าผิด (0 · 7 · 2.5 · ว่าง) → ใช้ 3", all(v == 3 for v in bad.values()), json.dumps(bad))
        check(f"{tag} 13 ค่าตั้งแยกต่อบัญชี: main = 2 · fam ยังเป็น 3", page.evaluate("()=>[coreRiskCfg('main').maxLots, coreRiskCfg('fam').maxLots]") == [2, 3])
        setmax(3)
        page.evaluate("()=>{ document.getElementById('sCrAdd').value = 50; crOnInput(); }")
        ex = txt(page, "#crLotsEx") or ""
        check(f"{tag} 13 บรรทัดตัวอย่าง 50% × 3 = 'ไม้แรก 100 → 50 → 25 (รวม 175% ของไม้แรก)'", "ไม้แรก 100 → 50 → 25 (รวม 175% ของไม้แรก)" in ex, ex)
        page.evaluate("()=>{ const m=document.querySelector('#setOverlay .modal'); m.style.maxHeight='none'; m.style.overflow='visible'; }")
        shot(page, f"7e2afix-settings-maxlots-{w}.png", "#crSec")
        page.evaluate("()=>document.querySelectorAll('.overlay.show').forEach(e=>e.classList.remove('show'))")
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def menu_fix2_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page)
        for k in ("aapl", "goog", "meta", "nvda", "msft", "amzn"): expand(page, k)
        order = page.evaluate("()=>[...document.querySelectorAll('#corePanel .ccList > .ccCard')].map(e=>e.dataset.coreCard)")
        def open_menu(id, place):
            page.evaluate("(id)=>document.querySelectorAll('.ccMenu.on').forEach(x=>x.classList.remove('on'))", id)
            c = card(page, id); b = c + " [data-c-more]"
            page.evaluate("([b,place])=>{ const e=document.querySelector(b); e.scrollIntoView({block:'center'}); if(place==='bottom'){ const r=e.getBoundingClientRect(); window.scrollBy(0, r.top - (innerHeight - 60)); } }", [b, place])
            page.wait_for_timeout(120)
            if place == "bottom":   # หน้าจอเตี้ยลงให้ปุ่ม ⋯ ชิดล่างจอจริง (ที่ใต้ปุ่มไม่พอ)
                page.set_viewport_size({"width": w, "height": 700}); page.wait_for_timeout(150)
                page.evaluate("(b)=>{ const e=document.querySelector(b); e.scrollIntoView({block:'end'}); window.scrollBy(0, 30); }", b); page.wait_for_timeout(150)
            if place == "bottom": page.evaluate("(b)=>document.querySelector(b).click()", b)   # ไม่ให้ Playwright เลื่อนหน้าเอง
            else: page.click(b)
            page.wait_for_timeout(100)
            return page.evaluate("""(c)=>{ const m=document.querySelector(c+' .ccMenu'), r=m.getBoundingClientRect(), br=document.querySelector(c+' [data-c-more]').getBoundingClientRect();
              const items=[...m.querySelectorAll('button')]; const bad=[];
              items.forEach(i=>{ const q=i.getBoundingClientRect(), e=document.elementFromPoint(q.left+q.width/2, q.top+q.height/2); if(!(e && m.contains(e))) bad.push(i.textContent.trim().slice(0,20)); });
              return {on:m.classList.contains('on'), n:items.length, bad, l:r.left, r:r.right, t:r.top, b:r.bottom, bt:br.top, bb:br.bottom, iw:innerWidth, ih:innerHeight}; }""", c)
        for id in ("aapl", "goog", "meta", order[-1]):
            g = open_menu(id, "center")
            ok = g["on"] and not g["bad"] and g["l"] >= 0 and g["r"] <= g["iw"] and g["t"] >= 0 and g["b"] <= g["ih"]
            check(f"{tag} fix2 ⋯ ของ {id} (กลางจอ): ทุกรายการ ({g['n']}) มองเห็นจริง (elementFromPoint อยู่ในเมนู) · ขอบเมนูอยู่ในจอทั้ง 4 ด้าน", ok, json.dumps(g, ensure_ascii=False))
        last = order[-1]
        g = open_menu(last, "center")
        shot(page, f"7e2afix2-menu-last-{w}.png")
        page.evaluate("()=>{ const d=document.createElement('div'); d.id='fix2Spacer'; d.style.height='1500px'; document.body.appendChild(d); }")   # ให้เลื่อนปุ่ม ⋯ ไปชิดล่างจอได้
        g2 = open_menu("aapl", "bottom")
        up = g2["on"] and g2["b"] <= g2["bt"] + 1 and not g2["bad"] and g2["t"] >= 0
        check(f"{tag} fix2 ⋯ ชิดล่างจอ → เมนูเปิดขึ้นบน (menu.bottom ≤ btn.top + 1) และเห็นครบ", up, json.dumps(g2, ensure_ascii=False))
        shot(page, f"7e2afix2-menu-up-{w}.png")
        page.set_viewport_size({"width": w, "height": h})
        rad = page.evaluate("()=>{ const cs=[...document.querySelectorAll('#corePanel .ccList > .ccCard')]; const f=getComputedStyle(cs[0]), l=getComputedStyle(cs[cs.length-1]); return {ft:f.borderTopLeftRadius, fb:f.borderBottomLeftRadius, lt:l.borderTopLeftRadius, lb:l.borderBottomLeftRadius, ov:getComputedStyle(document.querySelector('#corePanel .ccList')).overflow}; }")
        check(f"{tag} fix2 มุมโค้งใบแรก (บน) / ใบสุดท้าย (ล่าง) ยังโค้ง · .ccList ไม่มี overflow:hidden", rad["ft"] != "0px" and rad["lb"] != "0px" and rad["fb"] == "0px" and rad["lt"] == "0px" and rad["ov"] == "visible", json.dumps(rad))
        red = page.evaluate("()=>{ const e=document.querySelector('#corePanel .ccList > .ccCard'); const s=getComputedStyle(e); return {id:e.dataset.coreCard, red:e.classList.contains('isRed'), bg:s.backgroundColor, r:s.borderTopLeftRadius}; }")
        check(f"{tag} fix2 🔴 ใบแรกพื้นแดงอ่อนโค้งตามมุม (ไม่ล้นมุม)", red["id"] == "nvda" and red["red"] and red["bg"] != "rgb(255, 255, 255)" and red["r"] != "0px", json.dumps(red))
        one = page.evaluate("()=>{ const e=document.querySelector('[data-core-card=aapl] [data-c-lotsub]'), h=document.querySelector('[data-core-card=aapl] [data-c-hold]'); return {tag:e.tagName, t:e.textContent.trim(), rects:e.getClientRects().length, sep:!h.textContent.includes('ไม้'), below:e.getBoundingClientRect().top >= h.getBoundingClientRect().bottom - 1}; }")
        check(f"{tag} fix2 ช่องถือ: 'ไม้ 2/3' อยู่ใน <small> บรรทัดแยกใต้ '78 @ 103.33' · ไม่ถูกตัดกลางคำ (getClientRects = 1)", one["tag"] == "SMALL" and one["t"] == "ไม้ 2/3" and one["rects"] == 1 and one["sep"] and one["below"], json.dumps(one, ensure_ascii=False))
        check(f"{tag} fix2 ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def height10_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    trades, cards = [], {}
    for i in range(10):
        tid, cid = f"tt{i}", f"cc{i}"
        trades.append(usT(tid, f"S{i}", 20, 100, 90))
        cards[cid] = ucard(cid, tid, f"S{i}", [(100, 20)], 90, px=105 + i, pxDate=TODAY, emaW=95)
    doc, _ = data()
    doc["books"]["main"]["trades"] = trades
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page)
        m = page.evaluate("()=>{ const h=document.querySelector('[data-core-head=main]').getBoundingClientRect(), l=document.querySelector('#corePanel .ccList').getBoundingClientRect(); return {head:h.height, list:l.height, need:h.height+l.height, vh:innerHeight}; }")
        check(f"{tag} 6 การ์ดยุบ 10 ใบ ที่ {w}×{h}: หัวบัญชี + รายการ ({m['need']:.0f}px) ใส่จอเดียว ({m['vh']}px)", m["need"] <= m["vh"] if w > 700 else True, json.dumps(m))
        check(f"{tag} 6 ทุกใบยุบ (10 แถว)", page.locator("#corePanel [data-c-row][aria-expanded=false]").count() == 10)
    finally:
        browser.close()


def w932_checks(pw):
    tag = "[chromium/932x430]"
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, 932, 430, doc, cards)
    try:
        go(page); expand(page, "aapl"); expand(page, "meta")
        check(f"{tag} 6 แผงไม่ล้นแนวนอนที่ 932", page.evaluate("()=>{const e=document.getElementById('corePanel');return e.scrollWidth<=e.clientWidth+1 && document.documentElement.scrollWidth<=innerWidth+1}"))
        check(f"{tag} ไม่มี console error / pageerror", not ce and not pe, str(ce[:3] + pe[:3]))
    finally:
        browser.close()


def core_size_checks(pw):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), "--check"], capture_output=True, text=True)
    check("14 tools/sync_core_size.py --check ผ่าน (สำเนา = ต้นฉบับ · ไม่ถูกแก้)", r.returncode == 0, r.stdout + r.stderr)
    doc, cards = data()
    browser, context, page, ce, pe, dialogs = launch(pw, 1440, 900, doc, cards)
    try:
        src = open(os.path.join(ROOT, "tests", "core_size_test.js"), encoding="utf-8").read()
        rr = page.evaluate(p23.NODE_SHIM, src)
        m = re.search(r"(\d+) ผ่าน · (\d+) ไม่ผ่าน", " ".join(rr["last"]))
        check("14 tests/core_size_test.js (รันบนสำเนาใน index.html ผ่านเบราว์เซอร์) = 471/471 (CZ1: +22 เคส · LN3fix2: +29 เคส · เดิม 420 ผ่านครบ) · exit 0", bool(m) and m.group(1) == "471" and m.group(2) == "0" and rr["code"] == 0, json.dumps(rr, ensure_ascii=False))
    finally:
        browser.close()
    check("14 core-size.js ต่างจากต้นฉบับก่อน 7E-2b-1 เฉพาะ 2 จุดตามข้อ 0 (roicMin 0.12 · canPlaceLadder shareCap/l2Cap · +TIER2 +DD1 รวม 13 hunk · CZ1 +12 = 25 · LN3fix2 +8 = 33 hunk)", core_size_only_two_spots())


def core_size_only_two_spots():
    """7E-2b-1: core-size.js ต่างจาก core-size.backup-pre-7E2b1.js เฉพาะ 2 จุดตามข้อ 0 (roicMin · canPlaceLadder shareCap/l2Cap) = 3 hunk เดิม · TIER2 เพิ่มรวมเป็น 11 hunk · DD1 +2 = 13"""
    import difflib
    a = open(os.path.join(ROOT, "core-size.backup-pre-7E2b1.js"), encoding="utf-8").read().splitlines()
    b = open(os.path.join(ROOT, "core-size.js"), encoding="utf-8").read().splitlines()
    d = list(difflib.unified_diff(a, b, lineterm="", n=0))
    ch = [l for l in d if (l.startswith("+") or l.startswith("-")) and not l.startswith("+++") and not l.startswith("---")]
    return sum(1 for l in d if l.startswith("@@")) == 33 and any("roicMin: 0.12" in l for l in ch) and any("shareCap" in l for l in ch) and any("l2Cap" in l for l in ch)

def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            list_checks(pw, w, h, label)
            expand_checks(pw, w, h, label)
            menu_checks(pw, w, h, label)
            text_checks(pw, w, h, label)
            persist_checks(pw, w, h, label)
            lots_checks(pw, w, h, label)
            height10_checks(pw, w, h, label)
            menu_fix2_checks(pw, w, h, label)
        w932_checks(pw)
        core_size_checks(pw)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:300])
        sys.exit(1)


if __name__ == "__main__":
    main()
