#!/usr/bin/env python3
"""WT1 — ปุ่ม "บันทึกเฉพาะ Tier" ในฟอร์มแผน Core (ไม่ต้องมี Entry/SL) → เก็บที่ Watchlist → แผนใหม่ดึงไปใช้ · เทส 33
mock Firestore · 1440px + 430px · นาฬิกาปลอม = 2026-10-01 (เวลาไทย) · บัญชี US (main) + TH (fam)
seed Watchlist: AVGO (US · ไม่มี tier) · OLDA (tier 'A' เก่า) · PTT.BK (TH · research doc PTT) · GROW/BOTH/BEE (ชิปมุม) · TWO (ใช้เคส 2)
ภาพเก็บที่ tests/screenshots/wt1-*.png
รัน: python3 run_tests_phase33.py [/path/to/index.html]"""
import copy, json, os, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase26 as p26
import run_tests_phase29 as p29

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
p29.INDEX = INDEX
results = []
txt = p24.txt; go = p24.go_stock
doc26 = p26.doc26; FF_OPEN = p26.FF_OPEN
TODAY = "2026-10-01"
AS_OF = "2026-09-20"
BASE = json.load(open(os.path.join(HERE, "..", "avgo-research-card-th.json"), encoding="utf-8"))
TH_FX = json.load(open(os.path.join(HERE, "fixtures", "avgo_thesis.json"), encoding="utf-8"))   # WL2


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot_el(page, sel, name, tall=False):
    vp = page.viewport_size
    try:
        if tall: page.set_viewport_size({"width": vp["width"], "height": 2600})
        page.wait_for_timeout(500)
        page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e: print("shot fail", name, e)
    finally:
        if tall: page.set_viewport_size(vp); page.wait_for_timeout(200)


def m(name, value, unit="%", period="TTM"):
    return {"name": name, "value": value, "unit": unit, "period": period, "source_url": "https://www.sec.gov/Archives/edgar/data/1/x.htm"}


TIER7 = [m("ROIC = NOPAT ÷ IC [T:roic]", "24.5"), m("ND/EBITDA [T:nd]", "-0.3", "x"), m("FCF conversion [T:fcf]", "92"), m("รายได้โต TTM [T:rev]", "25.3"),
         m("CAGR รายได้ 3 ปี [T:cagr]", "18.0"), m("Op margin [T:opm]", "12.0 / 10.0", "%", "FY2026 / FY2025"), m("เช็ก 3 ข้อ [T:chk]", "yes/yes/yes", "-", "FY2026")]


def seed_research(page):
    """WL2 — Tier metrics มาจาก thesis.tier_inputs ของ watchlist/PTT.BK (เดิมจาก research_card ของ research/PTT)"""
    def ti(v, tag="C", period="FY25"): return {"v": v, "tag": tag, "period": period, "src": "ทดสอบ"}
    th = copy.deepcopy(TH_FX); th["sym"] = "PTT"; th.pop("log", None); th["date"] = AS_OF; th["asOf"] = AS_OF
    th["tier_inputs"] = {"roic": ti(24.5), "ndEbitda": ti(-0.3), "fcfConv": ti(92), "revGrowth": ti(25.3), "revCagr3": ti(18.0), "opMargin": ti(12.0), "opMarginPrev": ti(10.0),
                         "fcfPositive3y": ti(True, "F"), "capitalReturn": ti(True, "F"), "ocfPositive": ti(True, "F"), "netCash": ti(True)}
    page.evaluate("([k,d])=>window.firebase.__mockDb.__seedDoc(['research',k], d)", ["PTT", {"ticker": "PTT", "name": "PTT"}])
    page.evaluate("(t)=>wlCol().doc('PTT.BK').update({thesis:t, thesis_log:[], thesis_history:[], thesis_hits:{}})", th)
    page.evaluate("() => rsLoad(true)"); page.wait_for_timeout(400)


def tick(page, key, v, attr="data-tk"):
    cur = tkv(page, key, attr)
    if cur == v: return
    page.click(f'[{attr}="{key}"] button[data-v="{1 if v else 0}"]')


def tkv(page, key, attr="data-tk"):
    return page.evaluate("([a,k])=>{ const on=[...document.querySelectorAll('['+a+'=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; }", [attr, key])


def val(page, sel): return page.input_value(sel)
def vis(page, sel): return page.locator(sel).count() > 0 and page.locator(sel).first.is_visible()
def dis(page, sel): return page.locator(sel).first.is_disabled()
def wl_doc(page, t): return p29.wl_doc(page, t)
def wl_keys(page): return sorted(k.split("/")[-1] for k in p29.dump(page) if k.startswith("users/testuid/watchlist/"))


def new_form(page, ticker, acct="main"):
    page.evaluate("(a)=>coreNewOpen(a)", acct)
    page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
    if ticker: page.fill("#cnTicker", ticker)
    page.wait_for_timeout(80)


def fill_fortress(page):
    for sel, v in {"#tiRoic": "24.5", "#tiNd": "-0.3", "#tiFcf": "92"}.items(): page.fill(sel, v)
    tick(page, "fcf3y", True); tick(page, "capret", True)
    for k in ("substitute", "customerMigrating", "singleProduct"): tick(page, k, False, "data-g5")
    page.wait_for_timeout(100)


def lens_label(page, key): return txt(page, f'[data-c-lensline="{key}"]') or ""
def cards_n(page): return len(p24.cards_db(page))
def overflow(page, ids):
    return page.evaluate("""(ids)=>{ const W = window.innerWidth, bad = [];
      ids.forEach(id=>{ const e = typeof id==='string' && id[0]==='#' ? document.querySelector(id) : document.querySelector(id); if(!e) { bad.push(id+':missing'); return; }
        const r = e.getBoundingClientRect(); if(r.right > W + 1 || r.left < -1 || e.scrollWidth > e.clientWidth + 1) bad.push(id + ':' + Math.round(r.left) + '-' + Math.round(r.right) + '/' + e.scrollWidth + '>' + e.clientWidth); });
      const sh = document.querySelector('.core-sheet'); if(sh && sh.scrollWidth > sh.clientWidth + 1) bad.push('sheet'); return bad; }""", ids)


WL = {"AVGO": {}, "OLDA": {"tier": "A", "tier_set_at": "2026-01-05"}, "PTT.BK": {}, "TWO": {},
      "GROW": {"tier": "A", "tier_lens": "growth", "tier_set_at": "2026-09-01"},
      "BOTH": {"tier": "A", "tier_lens": "both", "tier_set_at": "2026-09-01"},
      "BEE": {"tier": "B", "tier_set_at": "2026-09-01"}}


def checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    cards = {"c1": p24.card("c1", "main", "CARD1", tier="A", tierLens="fortress", tierReason="ok"),
             "l1": p26.lcard("l1", ticker="LCARD", tier="A", tierLens="fortress")}
    browser, context, page, ce, pe, dialogs = p29.launch(pw, w, h, doc26(), cards=cards, wl=WL)
    try:
        p24.set_ff(page, FF_OPEN()); go(page); seed_research(page)
        # 1 ─ AVGO: บันทึกเฉพาะ Tier โดยไม่ใส่ Entry/Stop
        n0 = cards_n(page)
        new_form(page, "")
        check(f"{tag} 1 เปิดฟอร์มแผนใหม่ → มีปุ่ม 'บันทึกเฉพาะ Tier' + บรรทัดเล็ก · ticker ว่าง = กดไม่ได้",
              vis(page, "#cnTierOnly") and "บันทึกเฉพาะ Tier" in (txt(page, "#cnTierOnly") or "") and "ยังไม่สร้างแผน · ไม่ต้องใส่ Entry/Stop" in (txt(page, "[data-c-tieronlybox]") or "") and dis(page, "#cnTierOnly"))
        page.fill("#cnTicker", "AVGO"); fill_fortress(page)
        check(f"{tag} 1 AVGO กรอกชุด Fortress + Gate 5 ไม่ ×3 → ปุ่มบันทึกเฉพาะ Tier กดได้ · ปุ่ม 'บันทึกแผน' ยังปิด",
              not dis(page, "#cnTierOnly") and dis(page, "#cnSave") and (txt(page, "#cnTierOnly") or "") == "บันทึกเฉพาะ Tier", txt(page, "#cnTierOnly") or "")
        shot_el(page, '[data-core-sheet="new"]', f"wt1-tieronly-btn-{w}.png", tall=True)
        page.click("#cnTierOnly"); page.wait_for_timeout(500)
        d = wl_doc(page, "AVGO") or {}
        ti = d.get("tier_inputs") or {}
        check(f"{tag} 1 กด → ฟอร์มปิด · ไม่มีการ์ดใหม่", page.locator(".core-sheet").count() == 0 and cards_n(page) == n0, str(cards_n(page)))
        check(f"{tag} 1 doc AVGO: tier 'A' · tier_lens 'fortress' · tier_computed 'A' · tier_set_at = วันนี้ไทย",
              d.get("tier") == "A" and d.get("tier_lens") == "fortress" and d.get("tier_computed") == "A" and d.get("tier_set_at") == TODAY and d.get("tier_reason") is None, json.dumps(d, ensure_ascii=False))
        check(f"{tag} 1 tier_inputs ครบ (roic 0.245 · nd -0.3 · fcfConv 0.92 · ติ๊ก · gate5 ไม่ ×3)",
              ti.get("roic") == 0.245 and ti.get("ndEbitda") == -0.3 and ti.get("fcfConv") == 0.92 and ti.get("fcfPositive3y") is True and ti.get("capitalReturn") is True
              and ti.get("gate5") == {"substitute": False, "customerMigrating": False, "singleProduct": False}, json.dumps(ti))
        nt = txt(page, "#wtNote") or ""
        check(f"{tag} 1 มีข้อความแจ้ง 'บันทึก Tier AVGO = A · Fortress แล้ว (Watchlist)' · ไม่มี alert", nt == "บันทึก Tier AVGO = A · Fortress แล้ว (Watchlist)" and not dialogs, nt + json.dumps(dialogs))
        # 2 ─ เลือก A · Growth ที่คำนวณไม่ผ่าน
        new_form(page, "TWO"); fill_fortress(page)
        page.click("#cnTierG"); page.wait_for_timeout(80)
        a = dis(page, "#cnTierOnly")
        page.fill("#cnReason", "เชื่อว่าโตเร็วกว่าตัวเลข"); page.wait_for_timeout(80)
        b = dis(page, "#cnTierOnly")
        check(f"{tag} 2 เลือก A · Growth ที่ไม่ผ่านโดยไม่ใส่เหตุผล → ปุ่มปิด · ใส่เหตุผล → กดได้", a and not b, json.dumps([a, b]))
        page.click("#cnTierOnly"); page.wait_for_timeout(400)
        d = wl_doc(page, "TWO") or {}
        check(f"{tag} 2 tier_reason ถูกเก็บ · tier_lens 'growth' · tier_computed 'A'", d.get("tier_reason") == "เชื่อว่าโตเร็วกว่าตัวเลข" and d.get("tier_lens") == "growth" and d.get("tier") == "A" and d.get("tier_computed") == "A", json.dumps(d, ensure_ascii=False))
        # 3 ─ NEWX ไม่อยู่ใน Watchlist
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','NEWX'], {ticker:'NEWX', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(600)   # TD4a: สร้างเอกสารใหม่ผ่านฟอร์ม Tier ไม่ได้แล้ว → NEWX เป็นตัวที่ย้ายเข้า Watchlist มาก่อน
        new_form(page, "NEWX"); fill_fortress(page)
        lbl = txt(page, "#cnTierOnly") or ""
        check(f"{tag} 3 [TD4a] ticker NEWX (ย้ายเข้า Watchlist มาก่อน) → ป้ายปุ่ม 'บันทึกเฉพาะ Tier' (ไม่มี '(เพิ่มเข้า Watchlist)' แล้ว)", lbl.startswith("บันทึกเฉพาะ Tier"), lbl)
        page.click("#cnTierOnly"); page.wait_for_timeout(400)
        d = wl_doc(page, "NEWX") or {}
        check(f"{tag} 3 สร้าง doc NEWX: market US · port core · note/industry ว่าง · มีฟิลด์ Tier",
              d.get("ticker") == "NEWX" and d.get("market") == "US" and d.get("port") == "core" and d.get("note") == "" and d.get("industry") == "" and bool(d.get("added_at")) and d.get("tier") == "A" and d.get("tier_lens") == "fortress" and bool(d.get("tier_inputs")), json.dumps(d, ensure_ascii=False))
        # 4 ─ Overview AVGO: ชิป → ฟอร์มแผนใหม่ + กล่อง Tier มีค่า
        page.evaluate("()=>{ switchTab('watch'); wlOpen('AVGO'); }"); page.wait_for_timeout(400)
        chip = txt(page, ".wlDT [data-wl-tier]") or ""
        check(f"{tag} 4 Overview AVGO: ชิป 'A · Fortress'", chip == "A · Fortress", chip)
        shot_el(page, ".wlDT", f"wt1-wl-chip-{w}.png")
        page.click(".wlDT [data-wl-tier]"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]'); page.wait_for_timeout(200)
        pk = page.evaluate("()=>[...document.querySelectorAll('.ccSegTier button.on')].map(b=>b.dataset.pick)")
        info = txt(page, "#tiWlInfo") or ""
        check(f"{tag} 4 กดชิป → ฟอร์มแผนใหม่ ticker AVGO · กล่อง Tier มีค่าครบ (24.5 · -0.3 · 92 · ติ๊ก · Gate 5 ไม่ ×3)",
              val(page, "#cnTicker") == "AVGO" and (val(page, "#tiRoic"), val(page, "#tiNd"), val(page, "#tiFcf")) == ("24.5", "-0.3", "92")
              and tkv(page, "fcf3y") is True and tkv(page, "capret") is True and [tkv(page, k, "data-g5") for k in ("substitute", "customerMigrating", "singleProduct")] == [False, False, False], json.dumps([val(page, "#cnTicker"), val(page, "#tiRoic")]))
        check(f"{tag} 4 ปุ่ม A · Fortress ติด · #tiWlInfo = 'Tier จาก Watchlist (ตั้งเมื่อ {TODAY})'", pk == ["fortress"] and info == f"Tier จาก Watchlist (ตั้งเมื่อ {TODAY})", json.dumps(pk) + info)
        shot_el(page, '[data-core-sheet="new"]', f"wt1-plan-prefill-{w}.png", tall=True)
        # 5 ─ ต่อ: Entry/Stop → บันทึกแผน
        page.fill("#cnEntry", "100"); page.fill("#cnStop", "90"); page.wait_for_timeout(150)
        check(f"{tag} 5 กรอก Entry/Stop → ปุ่ม 'บันทึกแผน' เปิด", not dis(page, "#cnSave"), txt(page, "#cnErr") or "")
        page.click("#cnSave"); page.wait_for_timeout(600)
        k, c = p24.one_card(page, "AVGO")
        check(f"{tag} 5 การ์ดได้ Tier A · Fortress · tierInputs.roic 0.245", c is not None and c["tier"] == "A" and c.get("tierLens") == "fortress" and (c.get("tierInputs") or {}).get("roic") == 0.245, json.dumps(c)[:300] if c else "no card")
        bad = page.evaluate("(id)=>[...document.querySelectorAll('[data-core-card=\"'+id+'\"] [data-c-tierbadge]')].map(e=>e.textContent.trim())", k) if k else []
        check(f"{tag} 5 การ์ดไม่มีป้าย 'ยังไม่ได้ตั้ง Tier ใน Watchlist'", all("ยังไม่ได้ตั้ง Tier" not in x for x in bad), json.dumps(bad, ensure_ascii=False))
        # 6 ─ แผนใหม่ที่ดึง Tier มาแล้วแก้ ROIC → บันทึกแผน = ไม่เขียนกลับ Watchlist
        before = json.dumps(wl_doc(page, "NEWX"), sort_keys=True)
        new_form(page, "NEWX")
        check(f"{tag} 6 NEWX ดึง Tier จาก Watchlist มาเติม (ROIC 24.5)", val(page, "#tiRoic") == "24.5")
        page.fill("#tiRoic", "20"); page.fill("#cnEntry", "50"); page.fill("#cnStop", "45"); page.wait_for_timeout(150)
        page.click("#cnSave"); page.wait_for_timeout(600)
        k, c = p24.one_card(page, "NEWX")
        after = json.dumps(wl_doc(page, "NEWX"), sort_keys=True)
        check(f"{tag} 6 บันทึกแผน → การ์ดได้ ROIC ใหม่ (0.2) · Watchlist doc ไม่เปลี่ยน", c is not None and (c.get("tierInputs") or {}).get("roic") == 0.2 and before == after, before + " || " + after)
        # 7 ─ เปลี่ยน ticker ในฟอร์ม
        new_form(page, "AVGO")
        a = val(page, "#tiRoic")
        page.fill("#cnTicker", "ZZZZ"); page.wait_for_timeout(100)
        b = val(page, "#tiRoic"); pk2 = page.evaluate("()=>[...document.querySelectorAll('.ccSegTier button.on')].map(b=>b.dataset.pick)")
        g5 = [tkv(page, k, "data-g5") for k in ("substitute", "customerMigrating", "singleProduct")]
        check(f"{tag} 7 ticker AVGO → ตัวที่ไม่มี tier (ยังไม่แตะกล่อง) → กล่องเคลียร์ (ตัวเลข · Gate 5 · ปุ่ม Tier)", a == "24.5" and b == "" and g5 == [None, None, None] and pk2 != ["fortress"], json.dumps([a, b, g5, pk2]))
        page.fill("#cnTicker", "AVGO"); page.wait_for_timeout(100)
        check(f"{tag} 7 กลับเป็น AVGO (ยังไม่แตะ) → ดึงค่ากลับมา", val(page, "#tiRoic") == "24.5")
        new_form(page, "ZZZZ"); page.fill("#tiRoic", "7"); page.wait_for_timeout(80)
        page.fill("#cnTicker", "AVGO"); page.wait_for_timeout(100)
        check(f"{tag} 7 แตะกล่อง Tier แล้วเปลี่ยน ticker → ค่าที่กรอกไม่หาย (ROIC 7)", val(page, "#tiRoic") == "7" and (txt(page, "#tiWlInfo") or "").startswith("Watchlist:"), val(page, "#tiRoic") + (txt(page, "#tiWlInfo") or ""))
        # 8 ─ โมดัลแก้ไข AVGO
        page.evaluate("()=>coreSheetClose()")
        page.evaluate("()=>{ switchTab('watch'); wlOpen('AVGO'); wlOpenEdit('AVGO'); }"); page.wait_for_timeout(300)
        st = txt(page, "#wlAddTierSt") or ""
        check(f"{tag} 8 โมดัลแก้ไข AVGO: ไม่มี dropdown A/B · สถานะ 'Tier A · Fortress · ตั้งเมื่อ {TODAY}' · มีปุ่ม 'ตั้ง Tier…' + ลิงก์ 'ล้าง Tier'",
              page.locator("#wlAddTier").count() == 0 and st == f"Tier A · Fortress · ตั้งเมื่อ {TODAY}" and not vis(page, "#wlAddTierBtn") and vis(page, "#wlAddEvalBox [data-cs-edit]") and vis(page, "#wlAddTierClr"), st)   # CS1 — ปุ่ม ตั้ง Tier… ถูกแทนที่ด้วย Edit Stock Evaluation
        shot_el(page, "#wlAddOverlay .modal", f"wt1-wl-edit-{w}.png")
        page.click("#wlAddEvalBox [data-cs-edit]"); page.wait_for_selector("[data-cs-sheet]"); page.wait_for_timeout(200)
        check(f"{tag} 8 'ตั้ง Tier…' → โมดัลปิด · เปิดฟอร์มแผนใหม่ ticker AVGO", not page.locator("#wlAddOverlay.show").count() and page.evaluate("()=>document.querySelector('[data-cs-sheet]').dataset.sym") == "AVGO")   # CS1
        page.evaluate("()=>{ coreSheetClose(); csEvalClose(); }")
        page.evaluate("()=>{ switchTab('watch'); wlOpen('AVGO'); wlOpenEdit('AVGO'); }"); page.wait_for_timeout(200)
        page.click("#wlAddTierClr"); page.wait_for_timeout(400)
        d = wl_doc(page, "AVGO") or {}
        gone = all(d.get(f) is None for f in ("tier", "tier_set_at", "tier_lens", "tier_inputs", "tier_computed", "tier_reason"))
        check(f"{tag} 8 'ล้าง Tier' → 6 ฟิลด์หาย/null · บรรทัดสถานะ 'ยังไม่ตั้ง Tier'", gone and (txt(page, "#wlAddTierSt") or "") == "ยังไม่ตั้ง Tier" and not vis(page, "#wlAddTierClr"), json.dumps(d, ensure_ascii=False))
        page.click("#wlAddBtn"); page.wait_for_timeout(400)
        page.evaluate("()=>wlOpen('AVGO')"); page.wait_for_timeout(300)
        chip = txt(page, ".wlDT [data-wl-tier-set]") or ""
        check(f"{tag} 8 หลังล้าง ชิปกลับเป็น 'ตั้ง Tier' (จาง) · รายการซ้ายไม่มีชิป Tier", chip == "ตั้ง Tier" and page.locator('.wlR[data-sym="AVGO"] [data-wl-tier]').count() == 0, chip)
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','NEWY'], {ticker:'NEWY', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(500)   # TD4a: ต้องอยู่ใน Watchlist ก่อน
        page.evaluate("()=>wlOpenAdd('NEWY')"); page.wait_for_timeout(150)
        hid = not vis(page, "#wlAddTierBox") and page.locator("#wlAddTier").count() == 0
        page.click("#wlAddBtn"); page.wait_for_timeout(400)
        d = wl_doc(page, "NEWY") or {}
        check(f"{tag} 8 โมดัลเพิ่มหุ้นใหม่ไม่มีส่วน Tier · บันทึกแล้ว doc ไม่มีฟิลด์ tier", hid and d.get("ticker") == "NEWY" and not any(f in d for f in ("tier", "tier_set_at", "tier_lens", "tier_inputs", "tier_computed", "tier_reason")), json.dumps(d))
        # ชิปมุม
        page.evaluate("()=>switchTab('watch')")
        out = {}
        for s in ("GROW", "BOTH", "BEE"):
            page.evaluate("(s)=>wlOpen(s)", s); page.wait_for_timeout(200)
            out[s] = [txt(page, ".wlDT [data-wl-tier]"), txt(page, f'.wlR[data-sym="{s}"] [data-wl-tier]')]
        check(f"{tag} 4 ชิปแบบ long: A · Growth / A · ทั้งคู่ / B · แบบสั้นในรายการ = A / A / B", out == {"GROW": ["A · Growth", "A"], "BOTH": ["A · ทั้งคู่", "A"], "BEE": ["B", "B"]}, json.dumps(out, ensure_ascii=False))
        # 9 ─ OLDA
        page.evaluate("()=>wlOpen('OLDA')"); page.wait_for_timeout(250)
        chip = txt(page, ".wlDT [data-wl-tier]") or ""
        new_form(page, "OLDA")
        info = txt(page, "#tiWlInfo") or ""
        check(f"{tag} 9 OLDA → ชิป 'A · Fortress (เดิม)' · แผนใหม่ OLDA กล่อง Tier ว่าง · ข้อความเดิม 'Watchlist: Tier A …'",
              chip == "A · Fortress (เดิม)" and val(page, "#tiRoic") == "" and tkv(page, "fcf3y") is None and info.startswith("Watchlist: Tier A"), chip + " | " + info)
        # 10 ─ PTT.BK
        page.evaluate("()=>coreSheetClose()")
        new_form(page, "PTT.BK", acct="fam")
        check(f"{tag} 10 PTT.BK แผนใหม่บัญชี TH → เห็นปุ่ม 'เติมจาก Thesis' (thesis ใน watchlist/PTT.BK · WL2)", vis(page, "#tiFillTh"))
        page.click("#tiFillTh"); page.wait_for_timeout(100)
        for k in ("substitute", "customerMigrating", "singleProduct"): tick(page, k, False, "data-g5")
        lbl = txt(page, "#cnTierOnly") or ""
        keys0 = wl_keys(page)
        page.click("#cnTierOnly"); page.wait_for_timeout(400)
        d = wl_doc(page, "PTT.BK") or {}
        check(f"{tag} 10 บันทึกเฉพาะ Tier → เขียนลง doc PTT.BK เดิม (ไม่สร้าง PTT ซ้ำ) · ป้ายปุ่มไม่มี '(เพิ่มเข้า Watchlist)'",
              d.get("tier") == "A" and bool(d.get("tier_inputs")) and "PTT" not in wl_keys(page) and wl_keys(page) == keys0 and "เพิ่มเข้า" not in lbl, json.dumps([lbl, wl_keys(page)]))
        new_form(page, "PTT", acct="fam")
        check(f"{tag} 10 พิมพ์ PTT (ไม่มี .BK) → จับคู่ Watchlist PTT.BK ได้ · ดึง Tier มาเติม · ปุ่มไม่ขึ้น '(เพิ่มเข้า Watchlist)'", val(page, "#tiRoic") != "" and "เพิ่มเข้า" not in (txt(page, "#cnTierOnly") or ""), val(page, "#tiRoic") + (txt(page, "#cnTierOnly") or ""))
        page.evaluate("()=>coreSheetClose()")
        # 11 ─ edit / convert / sheet Tier…
        go(page)
        page.evaluate("()=>coreNewOpen(null,{mode:'convert', id:'c1'})"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        c_ = page.locator("#cnTierOnly").count(); page.evaluate("()=>coreSheetClose()")
        page.evaluate("()=>coreNewOpen(null,{mode:'edit', id:'l1'})"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        e_ = page.locator("#cnTierOnly").count(); page.evaluate("()=>coreSheetClose()")
        go(page); p24.menu_click(page, "c1", "[data-c-tierbtn]"); page.wait_for_selector('.core-sheet [data-core-sheet="tier"]')
        t_ = page.locator("#cnTierOnly").count(); has_blk = page.locator("[data-c-tierblock]").count()
        check(f"{tag} 11 โหมด convert / edit และ sheet 'Tier…' ของการ์ด → ไม่มีปุ่ม 'บันทึกเฉพาะ Tier' (sheet Tier ยังมีกล่อง Tier)", (c_, e_, t_) == (0, 0, 0) and has_blk == 1, json.dumps([c_, e_, t_, has_blk]))
        page.evaluate("()=>coreSheetClose()")
        # 12 ─ layout + console
        new_form(page, "NEWQ"); fill_fortress(page)
        if w <= 700:
            ov = overflow(page, ["[data-c-tieronlybox]", "#cnTierOnly", "[data-c-tieronlybox] .ccSub"])
            check(f"{tag} 12 430px: ปุ่ม + บรรทัดเล็กไม่ล้นแนวนอน (เช็กราย element)", ov == [], json.dumps(ov))
            page.evaluate("()=>coreSheetClose()")
            page.evaluate("()=>{ switchTab('watch'); wlOpen('BEE'); wlOpenEdit('BEE'); }"); page.wait_for_timeout(250)
            ov2 = overflow(page, ["#wlAddTierBox", "#wlAddTierSt", "#wlAddTierBtn"])
            check(f"{tag} 12 430px: โมดัลแก้ไข ส่วน Tier ไม่ล้นแนวนอน", ov2 == [], json.dumps(ov2))
        else:
            ok = page.evaluate("""()=>{ const s = document.querySelector('.core-sheet').getBoundingClientRect(), r = document.querySelector('[data-c-tieronlybox]').getBoundingClientRect(); return r.left >= s.left - 1 && r.right <= s.right + 1; }""")
            check(f"{tag} 12 1440px: ปุ่ม + บรรทัดเล็กอยู่ในกรอบ sheet", ok)
        check(f"{tag} 12 ไม่มี console error / page error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            checks(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:400])
        sys.exit(1)


if __name__ == "__main__":
    main()
