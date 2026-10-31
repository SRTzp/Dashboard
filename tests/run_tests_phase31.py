#!/usr/bin/env python3
"""TIER2 — Tier 2 มุมมอง (A-Fortress / A-Growth) บนฟอร์ม/การ์ด/เมนู/ค่าตั้ง · เทส 31 (brief ข้อ 10–16)
mock Firestore · 1440px + 430px · บัญชี US (main) ถัง Core 700,000 fx = 1 · Fund-flow เปิดประตู L (FF_OPEN)
ภาพเก็บที่ tests/screenshots/tier2-*.png
รัน: python3 run_tests_phase31.py [/path/to/index.html]"""
import json, os, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase26 as p26

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
results = []
txt = p24.txt; go = p24.go_stock; ex = p24.ex; card_sel = p26.card_sel
launch = p26.launch; doc26 = p26.doc26; FF_OPEN = p26.FF_OPEN; db_card = p26.db_card


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    page.wait_for_timeout(500)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=not page.locator(".core-sheet").count())
    except Exception as e: print("shot fail", name, e)


def shot_el(page, sel, name):
    page.wait_for_timeout(500)
    try: page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e: print("shot fail", name, e)


def tick(page, key, v, attr="data-tk"):
    """ช่องติ๊ก 3 สถานะ (toggle) · v True/False/None · คลิกเฉพาะเมื่อสถานะต่างจากที่ต้องการ"""
    cur = page.evaluate("([a,k])=>{ const on=[...document.querySelectorAll('['+a+'=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; }", [attr, key])
    if cur == v: return
    page.click(f'[{attr}="{key}"] button[data-v="{(1 if cur else 0) if v is None else (1 if v else 0)}"]')


def put(page, sel, v): page.fill(sel, "" if v is None else str(v))


def fortress(page, roic=15, nd=1.5, fcf=90, f3=True, cap=True, g5=(False, False, False)):
    for key, v in zip(("substitute", "customerMigrating", "singleProduct"), g5): tick(page, key, v, "data-g5")
    put(page, "#tiRoic", roic); put(page, "#tiNd", nd); put(page, "#tiFcf", fcf)
    tick(page, "fcf3y", f3); tick(page, "capret", cap)
    page.wait_for_timeout(80)


def growth(page, rev=25, cagr=18, opm=12, prev=10, ocf=True, nd=2.5, netcash=None, g5=(False, False, False)):
    for key, v in zip(("substitute", "customerMigrating", "singleProduct"), g5): tick(page, key, v, "data-g5")
    put(page, "#tiRev", rev); put(page, "#tiCagr", cagr); put(page, "#tiOpm", opm); put(page, "#tiOpmPrev", prev)
    put(page, "#tiNd", nd)
    tick(page, "ocf", ocf); tick(page, "netcash", netcash)
    page.wait_for_timeout(80)


def clear_fortress(page):
    put(page, "#tiRoic", None); put(page, "#tiFcf", None); tick(page, "fcf3y", None); tick(page, "capret", None)


def clear_growth(page):
    for s in ("#tiRev", "#tiCagr", "#tiOpm", "#tiOpmPrev"): put(page, s, None)
    tick(page, "ocf", None); tick(page, "netcash", None)


def summ(page): return txt(page, "[data-c-lenssum]") or ""
def line(page, k): return txt(page, f'[data-c-lensline="{k}"]') or ""
def new_form(page, ticker="TIERX", acct="main"):
    page.evaluate("(a)=>coreNewOpen(a)", acct)
    page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
    page.fill("#cnTicker", ticker)


# ───────── 10 · ฟอร์มแผนใหม่ ─────────
def form_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        new_form(page)
        fortress(page)
        check(f"{tag} 10 ชุด Fortress (ROIC 15 · ND 1.5 · FCF 90 · FCF3y ✓ · ปันผล ✓ · Gate 5 ไม่×3) → 'คำนวณได้ A · Fortress' · บรรทัด Fortress ✓ ผ่าน · ปุ่ม L เปิด",
              "คำนวณได้ A · Fortress" in summ(page) and line(page, "fortress") == "Fortress: ✓ ผ่าน" and line(page, "growth").startswith("Growth: ✗")
              and page.locator("#cnStratL").count() == 0, summ(page) + "|" + line(page, "growth"))   # RG2b: ไม่มีปุ่ม L ในฟอร์ม Winner
        check(f"{tag} 10 ปุ่ม Tier เริ่ม = ผลคำนวณ (A · Fortress ติด) · ปุ่มมี 4 ตัว", "on" in (page.get_attribute("#cnTierA", "class") or "") and page.locator(".ccSegTier button").count() == 4)
        shot_el(page, "[data-c-tierblock]", f"tier2-block-fortress-{w}.png")
        clear_fortress(page)
        growth(page)
        check(f"{tag} 10 ชุด Growth (rev 25 · CAGR 18 · opm 12 vs 10 · OCF ✓ · ND 2.5) → 'คำนวณได้ A · Growth' (RG2b: ไม่มีปุ่ม L ในฟอร์ม)",
              "คำนวณได้ A · Growth" in summ(page) and line(page, "growth") == "Growth: ✓ ผ่าน" and line(page, "fortress").startswith("Fortress: ✗")
              and page.locator("#cnStratL").count() == 0, summ(page))   # RG2b: ไม่มีตัวเลือก W/L ในฟอร์ม
        shot_el(page, "[data-c-tierblock]", f"tier2-block-growth-{w}.png")
        shot(page, f"tier2-L-disabled-{w}.png")
        fortress(page, nd=1.5)   # ND ใช้ร่วม → 1.5 ผ่านทั้ง 2 มุม
        check(f"{tag} 10 ผ่านทั้งคู่ → 'คำนวณได้ A · ทั้งสองมุม' + L เปิด", "คำนวณได้ A · ทั้งสองมุม" in summ(page) and page.locator("#cnStratL").count() == 0 and "on" in (page.get_attribute("#cnTierAB", "class") or ""), summ(page))
        shot_el(page, "[data-c-tierblock]", f"tier2-block-both-{w}.png")
        clear_fortress(page); put(page, "#tiNd", 2.5); page.wait_for_timeout(100)   # RG2b: ถอดตัวเลือก W/L ออกจากฟอร์ม — ตัดเคส "เลือก L แล้วมุม Fortress หลุด → กลับเป็น W" (ไม่มีให้เลือก L)
        # ไม่มีข้อมูล growth → B · บอกเหตุผล
        clear_growth(page); put(page, "#tiNd", None); page.wait_for_timeout(80)
        check(f"{tag} 10 ไม่มีข้อมูลเลย → 'คำนวณได้ B' · ปุ่ม B ติด", summ(page) == "คำนวณได้ B" and "on" in (page.get_attribute("#cnTierB", "class") or ""), summ(page))
        # เลือกมุมที่ไม่ผ่าน → ต้องมีเหตุผล
        page.click("#cnTierG"); page.wait_for_timeout(80)
        check(f"{tag} 10 เลือก A · Growth ที่คำนวณไม่ผ่าน → ช่องเหตุผลโผล่ · บันทึกไม่ได้ (REASON)", page.locator("#cnReasonBox").is_visible() and page.is_disabled("#cnSave"))
        check(f"{tag} 10 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────── 11 · บันทึกแผน A-Growth ─────────
def save_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        qtys = {}
        for tk, mode in (("TGRO", "g"), ("TFOR", "f"), ("TBEE", "b")):
            new_form(page, tk)
            if mode == "g": growth(page)
            elif mode == "f": fortress(page)
            page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.click('#cnF button[data-f="1"]'); page.wait_for_timeout(150)
            qtys[tk] = (txt(page, "#cnRes [data-c-qty]") or "").replace(",", "")
            page.click("#cnSave"); page.wait_for_timeout(500)
        k, c = p24.one_card(page, "TGRO")
        check(f"{tag} 11 บันทึกแผน A-Growth → การ์ดเก็บ tier 'A' · tierLens 'growth' · tierComputed 'A'", c and c["tier"] == "A" and c["tierLens"] == "growth" and c["tierComputed"] == "A", json.dumps(c, ensure_ascii=False))
        check(f"{tag} 11 tierInputs เก็บช่องใหม่ (revGrowth 0.25 · revCagr3 0.18 · opMargin 0.12 · opMarginPrev 0.10 · ocf true)",
              c and abs(c["tierInputs"]["revGrowth"] - 0.25) < 1e-12 and abs(c["tierInputs"]["revCagr3"] - 0.18) < 1e-12 and abs(c["tierInputs"]["opMargin"] - 0.12) < 1e-12
              and abs(c["tierInputs"]["opMarginPrev"] - 0.10) < 1e-12 and c["tierInputs"]["ocf"] is True, json.dumps(c and c["tierInputs"], ensure_ascii=False))
        kf, cf = p24.one_card(page, "TFOR")
        check(f"{tag} 11 A-Fortress เก็บ tierLens 'fortress' · tierInputs.fcfPositive3y/capitalReturn true", cf and cf["tierLens"] == "fortress" and cf["tierInputs"]["fcfPositive3y"] is True and cf["tierInputs"]["capitalReturn"] is True)
        kb, cb = p24.one_card(page, "TBEE")
        check(f"{tag} 11 B เก็บ tier 'B' · tierLens null", cb and cb["tier"] == "B" and cb["tierLens"] is None)
        check(f"{tag} 11 ไม้แรกเพดานเดียว 25% ของถัง Winner (RG2b ไม่แยก Tier): A-Growth = A-Fortress = B = 365 หุ้น", qtys["TGRO"] == "365" and qtys["TFOR"] == "365" and qtys["TBEE"] == "365", json.dumps(qtys))
        ex(page, k)
        chip_g = txt(page, f'{card_sel(k)} [data-c-tier]') or ""
        check(f"{tag} 11 ชิปการ์ด A-Growth = 'Tier A · Growth' + บรรทัด FF 'เพดานไม้แรก 25%' (UX2: เพดานย้ายจากชิป)", chip_g == "Tier A · Growth" and "เพดานไม้แรก 25%" in (txt(page, f'{card_sel(k)} [data-c-ff]') or ""), chip_g)
        ex(page, kf); chip_f = txt(page, f'{card_sel(kf)} [data-c-tier]') or ""
        check(f"{tag} 11 ชิป A-Fortress = 'Tier A · Fortress' + บรรทัด FF 'เพดานไม้แรก 25%' (UX2)", chip_f == "Tier A · Fortress" and "เพดานไม้แรก 25%" in (txt(page, f'{card_sel(kf)} [data-c-ff]') or ""), chip_f)
        check(f"{tag} 11 ป้ายแถวยุบยังเป็น A·W และ title บอกมุม", txt(page, f'{card_sel(k)} .ccTag') == "A·W" and "Tier A · Growth" in (page.get_attribute(f'{card_sel(k)} .ccTag', "title") or ""),
              page.get_attribute(f'{card_sel(k)} .ccTag', "title") or "")
        check(f"{tag} 11 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()
    # ภาพชิป: การ์ดทุกมุมเปิดพร้อมกัน
    cards = {"cg": p24.card("cg", "main", "GROW", tier="A", tierLens="growth", tierReason="r"),
             "cf": p24.card("cf", "main", "FORT", tier="A", tierLens="fortress", tierReason="r"),
             "cb": p24.card("cb", "main", "BOTH", tier="A", tierLens="both", tierReason="r"),
             "cl": p24.card("cl", "main", "OLDA", tier="A", tierReason="r"),
             "cw": p24.card("cw", "main", "BEEE", tier="B")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        for id in cards: ex(page, id)
        chips = {id: txt(page, f'{card_sel(id)} [data-c-tier]') for id in cards}
        check(f"{tag} 11 ชิปครบ 4 แบบ + การ์ดเก่า",
              chips == {"cg": "Tier A · Growth", "cf": "Tier A · Fortress", "cb": "Tier A · Fortress + Growth", "cl": "Tier A · Fortress (เดิม)", "cw": "Tier B"}
              and {id: ("เพดานไม้แรก 25%") in (txt(page, f'{card_sel(id)} [data-c-ff]') or "") for id in cards} == {id: True for id in cards}, json.dumps(chips, ensure_ascii=False))   # UX2: เพดานไม้แรกย้ายไปบรรทัด FF
        shot(page, f"tier2-card-chip-{w}.png")
    finally:
        browser.close()


# ───────── 12 · เมนู ⋯ ─────────
def menu_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    cards = {"cg": p24.card("cg", "main", "GROW", tier="A", tierLens="growth", tierReason="r"),
             "cf": p24.card("cf", "main", "FORT", tier="A", tierLens="fortress", tierReason="r"),
             "cb": p24.card("cb", "main", "BOTH", tier="A", tierLens="both", tierReason="r")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        res = {}
        for id in cards:
            ex(page, id); page.click(card_sel(id) + " [data-c-more]")
            res[id] = page.locator(card_sel(id) + ' .ccMenu [data-c-strat]').count()
            page.keyboard.press("Escape")
        check(f"{tag} 12 ⋯ (RG2b) เมนูการ์ด Winner ไม่มี 'เปลี่ยนเป็น L' ทั้ง A-Growth · A-Fortress · A-ทั้งคู่ (ถอดโหมดแปลง W→L)", res == {"cg": 0, "cf": 0, "cb": 0}, json.dumps(res))
        check(f"{tag} 12 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────── 13 · การ์ดเก่า tier A ไม่มี tierLens ─────────
def legacy_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    old = p24.card("old", "main", "OLDX", tier="A", tierReason="moat เดิม", plan={"entry": 100, "stop": 90}, stop=90)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), cards={"old": old}, ff=FF_OPEN())
    try:
        go(page)
        ex(page, "old")
        chip = txt(page, card_sel("old") + " [data-c-tier]") or ""
        check(f"{tag} 13 การ์ดเก่า tier A ไม่มี tierLens → ชิป 'Tier A · Fortress (เดิม)'", chip.startswith("Tier A · Fortress (เดิม)"), chip)
        before = json.dumps(db_card(page, "old"), sort_keys=True)
        p24.menu_click(page, "old", "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
        check(f"{tag} 13 Tier… การ์ดเก่า: ปุ่ม A · Fortress ติด · เหตุผลเดิมถูกเติม", "on" in (page.get_attribute("#cnTierA", "class") or "") and page.input_value("#cnReason") == "moat เดิม")
        page.click('.core-sheet .ccFoot button:has-text("ยกเลิก")'); page.wait_for_timeout(300)
        check(f"{tag} 13 เปิด Tier… แล้วปิดไม่บันทึก = ไม่มีอะไรเปลี่ยน (ไม่ migrate · ไม่เติม tierLens)", before == json.dumps(db_card(page, "old"), sort_keys=True) and "tierLens" not in db_card(page, "old"))
        # RG2b — ถอดโหมดแปลง W→L (การ์ดเก่าไม่มีเมนู 'เปลี่ยนเป็น L' · วาง Ladder ที่หน้า Ladder)
        page.click(card_sel("old") + " [data-c-more]")
        check(f"{tag} 13 การ์ดเก่าไม่มีเมนูเปลี่ยนเป็น L (RG2b)", page.locator(card_sel("old") + ' .ccMenu [data-c-tierbtn]').count() == 1 and page.locator(card_sel("old") + ' .ccMenu [data-c-strat]').count() == 0)
        page.keyboard.press("Escape")
        check(f"{tag} 13 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────── 14 · บันได L เดิมของการ์ดที่เปลี่ยนเป็น A-Growth ─────────
def ladder_keep_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    cards = {"lp": p26.lcard("lp", ticker="LPP", tierLens="fortress"), "lo": p26.lopen("lo", ticker="LOO", tierLens="fortress")}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(main_trades=[p26.ltrade("lo", "LOO")]), cards=cards, ff=FF_OPEN())
    try:
        go(page)
        # RG2b — การ์ด L อยู่หน้า Ladder (ไม่มีเมนู Tier…/แก้แผนบันไดในหน้า Winner) : ตัดเคสเปลี่ยนมุม Tier ของการ์ด L ออก
        onwin = page.locator(card_sel("lp")).count() + page.locator(card_sel("lo")).count()
        page.evaluate("()=>{ setPlanScope('ladder'); render(); }"); page.wait_for_timeout(400)
        check(f"{tag} 14 (RG2b) การ์ด L ไม่อยู่หน้า Winner · อยู่หน้า Ladder ทั้ง 2 ใบ (ไม่มี Tier…)", onwin == 0 and page.locator('[data-ldr-card="lp"]').count() == 1 and page.locator('[data-ldr-card="lo"]').count() == 1, onwin)
        check(f"{tag} 14 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────── 15 · ค่าตั้ง ─────────
def settings_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        new_form(page, "SETX")
        growth(page, rev=19.9)
        r0 = line(page, "growth")
        check(f"{tag} 15 ค่าเริ่มต้น (รายได้โต 20%) · rev 19.9% → Growth ไม่ผ่าน (รายได้โต < 20%)", r0.startswith("Growth: ✗") and "รายได้โต < 20%" in r0, r0)
        page.evaluate("()=>coreSheetClose()"); page.wait_for_timeout(300)
        page.evaluate("()=>openSettings()"); page.wait_for_timeout(250)
        page.evaluate("()=>document.querySelectorAll('#setOverlay details').forEach(d=>d.open=true)")
        vals = page.evaluate("()=>({r:sCrTierRoic.value, n:sCrTierNd.value, f:sCrTierFcf.value, g:sCrTierRevG.value, c:sCrTierCagr.value, ng:sCrTierNdG.value})")
        check(f"{tag} 15 ค่าตั้ง 'เกณฑ์ Tier' ค่าเริ่มต้นตามตาราง (12 · 2 · 80 · 20 · 15 · 3) — ค่าเก่าไม่มีคีย์ = ใช้ค่าเริ่มต้น", vals == {"r": "12", "n": "2", "f": "80", "g": "20", "c": "15", "ng": "3"}, json.dumps(vals))
        check(f"{tag} 15 หัวข้อ 'เกณฑ์ Tier' มีในส่วนความเสี่ยง Core", page.locator("[data-c-tiercrit-h]").count() == 1 and "tier criteria" in (txt(page, "[data-c-tiercrit-h]") or "").lower())
        shot(page, f"tier2-settings-{w}.png")
        page.fill("#sCrTierRevG", "15"); page.wait_for_timeout(60)
        page.click("#setSaveBtn"); page.wait_for_timeout(1200)
        saved = page.evaluate("()=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return d.books.main.settings.coreRisk; }")
        check(f"{tag} 15 บันทึก → coreRisk.tierRevG = 15 (+ คีย์ใหม่ครบ)", saved and saved["tierRevG"] == 15 and saved["tierRoic"] == 12 and saved["tierNdG"] == 3, json.dumps(saved))
        check(f"{tag} 15 coreSizeOpts.tierCrit.growth.revGrowthMin = 0.15", abs(page.evaluate("()=>coreSizeOpts('main').tierCrit.growth.revGrowthMin") - 0.15) < 1e-12)
        new_form(page, "SETX")
        growth(page, rev=19.9)
        r1 = line(page, "growth")
        check(f"{tag} 15 กลับฟอร์ม → rev 19.9% กลายเป็นผ่าน (Growth: ✓) · 'คำนวณได้ A · Growth'", r1 == "Growth: ✓ ผ่าน" and "คำนวณได้ A · Growth" in summ(page), r1)
        page.evaluate("()=>coreSheetClose()"); page.wait_for_timeout(300)
        page.evaluate("()=>openSettings()"); page.wait_for_timeout(250)
        page.evaluate("()=>document.querySelectorAll('#setOverlay details').forEach(d=>d.open=true)")
        page.fill("#sCrTierRoic", "0"); page.wait_for_timeout(60)
        check(f"{tag} 15 เกณฑ์ Tier ต้องมากกว่า 0 · ผิด = ปุ่มบันทึกปิด + ข้อความแดง", page.is_disabled("#setSaveBtn") and bool(txt(page, '[data-err-for="sCrTierRoic"]')))
        check(f"{tag} 15 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────── 16 · เลย์เอาต์ ─────────
def layout_checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc26(), ff=FF_OPEN())
    try:
        go(page)
        new_form(page, "LAYX")
        fortress(page); growth(page, nd=1.5)
        m = page.evaluate("""()=>{ const b = document.querySelector('[data-c-tierblock]'), sh = document.querySelector('.core-sheet [data-core-sheet=\"new\"]') || document.querySelector('.core-sheet');
          const bw = b.getBoundingClientRect(), sw = sh.getBoundingClientRect();
          return {blockScroll: b.scrollWidth, blockClient: b.clientWidth, docScroll: document.documentElement.scrollWidth, docClient: document.documentElement.clientWidth,
                  right: bw.right, vw: window.innerWidth, shScroll: sh.scrollWidth, shClient: sh.clientWidth}; }""")
        check(f"{tag} 16 บล็อก Tier ไม่ล้นแนวนอน (บล็อก/sheet/หน้า)", m["blockScroll"] <= m["blockClient"] + 1 and m["shScroll"] <= m["shClient"] + 1 and m["docScroll"] <= m["docClient"] + 1 and m["right"] <= m["vw"] + 1, json.dumps(m))
        if w <= 700:
            order = page.evaluate("()=>{ const f = document.querySelector('[data-c-tiersec=\"fortress\"]').getBoundingClientRect(), g = document.querySelector('[data-c-tiersec=\"growth\"]').getBoundingClientRect(); return {fb: f.bottom, gt: g.top, fl: f.left, gl: g.left}; }")
            check(f"{tag} 16 ≤ 700px: สองส่วนเรียงบน-ล่าง (Growth อยู่ใต้ Fortress · ซ้ายตรงกัน)", order["gt"] >= order["fb"] - 1 and abs(order["fl"] - order["gl"]) < 2, json.dumps(order))
        hs = page.evaluate("()=>[...document.querySelectorAll('.ccSegTier button')].map(b=>Math.round(b.getBoundingClientRect().height))")
        check(f"{tag} 16 ปุ่ม Tier 4 ตัวสูง ≥ 36px", len(hs) == 4 and min(hs) >= 36, json.dumps(hs))
        okpt = page.evaluate("""()=>{ const bad = []; document.querySelectorAll('.ccSegTier button, [data-tk] button, [data-g5] button').forEach(b=>{
              b.scrollIntoView({block:'center'}); const r = b.getBoundingClientRect(), e = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2);
              if(!(e === b || b.contains(e))) bad.push(b.id || (b.parentElement.dataset.tk || b.parentElement.dataset.g5) + ':' + b.dataset.v); }); return bad; }""")
        check(f"{tag} 16 elementFromPoint ของปุ่ม Tier/ช่องติ๊ก/Gate 5 = ตัวมันเอง (ไม่ถูกบัง)", okpt == [], json.dumps(okpt))
        page.click("#cnTierB"); page.wait_for_timeout(60)
        a = "on" in (page.get_attribute("#cnTierB", "class") or "")
        page.click("#cnTierAB"); page.wait_for_timeout(60)
        check(f"{tag} 16 ปุ่ม Tier กดได้จริง (B → ทั้งคู่)", a and "on" in (page.get_attribute("#cnTierAB", "class") or ""))
        if w <= 700:
            rows = page.evaluate("()=>new Set([...document.querySelectorAll('.ccSegTier button')].map(b=>Math.round(b.getBoundingClientRect().top))).size")
            check(f"{tag} 16 ปุ่ม Tier 4 ตัวขึ้น 2 แถวได้", rows == 2, str(rows))
        check(f"{tag} 16 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            form_checks(pw, w, h, label)
            save_checks(pw, w, h, label)
            menu_checks(pw, w, h, label)
            legacy_checks(pw, w, h, label)
            ladder_keep_checks(pw, w, h, label)
            settings_checks(pw, w, h, label)
            layout_checks(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:400])
        sys.exit(1)


if __name__ == "__main__":
    main()
