#!/usr/bin/env python3
"""7E-2b-2 — ไม้จากการ์ดไม่นับนอกแผน · Watchlist Tier + ป้ายเทียบบนการ์ด Core · ทางเข้าเดิม (Watch → แผน Core · บันทึกไม้ย้อนหลัง)
            · ผูกการ์ด ↔ Positions · ป้าย BE · เทส 29
mock Firestore · Chromium 1440 + 430 · นาฬิกาปลอม = 2026-10-01 12:00 เวลาไทย (วันนี้ = 2026-10-01 ทุกเคส)
ภาพเก็บที่ tests/screenshots/7e2b2-*.png
รัน: python3 run_tests_phase29.py [/path/to/index.html]"""
import json, os, re, subprocess, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase22 as p22
import run_tests_phase24 as p24
import run_tests_phase26 as p26

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
results = []
T = p22.T
txt = p24.txt; ex = p24.ex; go = p24.go_stock
TODAY = "2026-10-01"
ISO = "2026-10-01T05:00:00Z"   # 12:00 เวลาไทย


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    page.wait_for_timeout(600)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=not page.locator(".core-sheet, .overlay.show").count())
    except Exception as e: print("shot fail", name, e)


CLOCK_JS = """(iso) => { const R = Date, base = R.parse(iso), start = R.now();
  class FD extends R { constructor(...a){ if(a.length===0) super(base + (R.now()-start)); else super(...a); } static now(){ return base + (R.now()-start); } }
  window.Date = FD; }"""


def launch(pw, w, h, doc, cards=None, wl=None, deny_wl=False):
    lk = {"headless": True}
    if base.CHROMIUM_PATH: lk["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    context = browser.new_context(viewport={"width": w, "height": h}, timezone_id="Asia/Bangkok")
    from ff_stub import FF_STUB; context.add_init_script(FF_STUB)
    context.add_init_script("(" + CLOCK_JS + ")(" + json.dumps(ISO) + ")")
    page = context.new_page()
    ce, pe, dialogs = [], [], []
    page.on("console", lambda m: ce.append(m.text) if m.type == "error" and "watchlist" not in m.text.lower() else None)
    page.on("pageerror", lambda e: pe.append(str(e)))
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))
    page.route(re.compile(r"gstatic\.com/firebasejs"), lambda r: r.fulfill(status=200, content_type="application/javascript", body=base.MOCK_FB))
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), lambda r: r.fulfill(status=200, content_type="text/css", body=""))
    page.route(re.compile(r"fundflow\.json|open\.er-api\.com|api\.twelvedata\.com"), lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto("file://" + INDEX, wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("() => localStorage.setItem('bkLastBackupAt', String(Date.now()))")
    page.evaluate("(d)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], d); }", doc)
    for cid, c in (cards or {}).items():
        page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, c])
    for tk, x in (wl or {}).items():
        d = {"ticker": tk, "market": "TH" if tk.endswith(".BK") else "US", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"}
        d.update(x)
        page.evaluate("([t,d])=>window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist',t], d)", [tk, d])
    if deny_wl:
        page.evaluate("()=>window.firebase.__mockDb.__denyPath(['users','testuid','watchlist'])")
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(1000)
    return browser, context, page, ce, pe, dialogs


def dump(page): return page.evaluate("()=>window.firebase.__mockDb.__dump()")
def wl_doc(page, t): return dump(page).get("users/testuid/watchlist/" + t)
def card_sel(id): return f'[data-core-card="{id}"]'
def trade_of(page, id, acct="main"): return next((t for t in p24.book_trades(page, acct) if t["id"] == id), None)


def pos_text(page, tid):
    return page.evaluate("(id)=>[...document.querySelectorAll('[data-pos=\"'+id+'\"]')].map(e=>e.textContent.replace(/\\s+/g,' ')).join(' | ')", tid)


def jtext(page, sym):
    """ข้อความของแถว/การ์ด Journal Closed ที่มี sym (ตาราง + การ์ดมือถือ)"""
    return page.evaluate("""(s)=>[...document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard')].filter(e=>e.textContent.indexOf(s)>=0).map(e=>e.textContent.replace(/\\s+/g,' ')).join(' | ')""", sym)


def jrows_syms(page, syms):
    return [s for s in syms if jtext(page, s)]


def go_journal(page):
    page.evaluate("()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(300)


def go_plan(page):
    page.evaluate("()=>{ switchTab('plan'); setPlanAcct('all'); }"); page.wait_for_timeout(300)


def badges(page, id):
    return page.evaluate("""(id)=>[...document.querySelectorAll('[data-core-card="'+id+'"] [data-c-tierbadge]')].map(e=>({level:e.dataset.level, code:e.dataset.code, text:e.textContent.trim()}))""", id)


def row_warn(page, id):
    return page.evaluate("""(id)=>{ const e = document.querySelector('[data-core-card="'+id+'"] .ccRow [data-c-wlwarn]'); return e ? e.getAttribute('title') : null; }""", id)


def nums(page):
    return page.evaluate("""()=>{ const cx = coreCtx('main'), rk = coreAcctRisk('main');
      return {cash: Math.round(cx.cashTHB*1e4)/1e4, l2: Math.round(rk.layer2Pct*1e6)/1e6, l2f: Math.round(rk.layer2FullPct*1e6)/1e6,
              lp: cx.split ? Math.round(cx.split.lPct*1e8)/1e8 : null, wc: Math.round(cx.wCost*1e4)/1e4}; }""")


def no_h_overflow(page): return page.evaluate("()=>document.documentElement.scrollWidth <= window.innerWidth + 1")


def in_view(page, sel):
    b = page.locator(sel).first.bounding_box(); vp = page.viewport_size
    return bool(b) and b["x"] >= -1 and b["x"] + b["width"] <= vp["width"] + 1 and b["y"] >= -1 and b["y"] + b["height"] <= vp["height"] + 1


# ───────────────────────── A · นอกแผน ─────────────────────────
def section_A(pw, w, h, tag):
    # A1 ซื้อไม้ 1 ผ่านการ์ด W ของ ticker ที่ไม่อยู่ใน Watchlist
    doc = p24.doc_with(main_trades=[T("nc", "core", "open", sym="NOCARD", unplanned=True, cur="USD")], main_market="both")
    cards = {"cb": p24.card("cb", "main", "BUYW", tier="B", plan={"entry": 100, "stop": 90}, stop=90)}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go(page); ex(page, "cb")
        page.click(card_sel("cb") + " [data-c-buy1]"); page.wait_for_timeout(200); page.click("#cbSave"); page.wait_for_timeout(700)
        tr = next((t for t in p24.book_trades(page) if t["sym"] == "BUYW"), None)
        check(f"{tag} A1 ซื้อไม้ 1 ผ่านการ์ด W (BUYW ไม่อยู่ใน Watchlist) → trade unplanned:false", tr is not None and tr["unplanned"] is False, json.dumps(tr))
        go_plan(page)
        check(f"{tag} A1 Positions: ไม้จากการ์ดไม่มีป้าย 'นอกแผน' · ไม้ที่ไม่มีการ์ด (NOCARD) ยังมีป้าย",
              "นอกแผน" not in pos_text(page, tr["id"]) and "BUYW" in pos_text(page, tr["id"]) and "นอกแผน" in pos_text(page, "nc"), pos_text(page, tr["id"]) + " || " + pos_text(page, "nc"))
        check(f"{tag} A1 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()

    # A2 ไม้เก่า unplanned:true + มีการ์ดผูก → ไม่มีป้ายทุกจุด · ไม่มีการ์ด → ยังมีป้าย
    def cl(id, sym, **kw): return T(id, "core", "closed", sym=sym, entry=100, sl=90, qty=1, exitPrice=110, exitDate="2026-09-20", date="2026-09-10", cur="USD", **kw)
    trades = [T("ol1", "core", "open", sym="OLDX", unplanned=True, cur="USD"), T("ol2", "core", "open", sym="NOCARDX", unplanned=True, cur="USD"),
              cl("olc", "OLDC", unplanned=True), cl("olc2", "NOCARD2", unplanned=True),
              cl("og1", "GRPX", unplanned=True, posGroup="gx"), cl("og2", "GRPX", posGroup="gx"),
              cl("gh1", "GRPY", unplanned=True, posGroup="gy"), cl("gh2", "GRPY", posGroup="gy")]
    cards = {"c_old": p24.open_card("c_old", "ol1", ticker="OLDX", qty=1, entry=100, sl=90), "c_oldc": p24.open_card("c_oldc", "olc", ticker="OLDC", qty=1, entry=100, sl=90),
             "c_og": p24.open_card("c_og", "og1", ticker="GRPX", qty=1, entry=100, sl=90)}
    doc = p24.doc_with(main_trades=trades, main_market="both")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go_plan(page)
        check(f"{tag} A2 Positions: ไม้เก่า unplanned:true + มีการ์ด (OLDX) → ไม่มีป้าย · ไม่มีการ์ด (NOCARDX) → มีป้าย",
              "นอกแผน" not in pos_text(page, "ol1") and "OLDX" in pos_text(page, "ol1") and "นอกแผน" in pos_text(page, "ol2"), pos_text(page, "ol1") + " || " + pos_text(page, "ol2"))
        go_journal(page)
        check(f"{tag} A2 Journal แถว/การ์ดมือถือ: OLDC (มีการ์ด) ไม่มีป้าย · NOCARD2 (ไม่มีการ์ด) มีป้าย",
              "นอกแผน" not in jtext(page, "OLDC") and "นอกแผน" in jtext(page, "NOCARD2"), jtext(page, "OLDC") + " || " + jtext(page, "NOCARD2"))
        check(f"{tag} A2 Journal หัวกลุ่ม: GRPX (ขาแรกมีการ์ด) ไม่มีป้าย · GRPY (ไม่มีการ์ด) มีป้าย",
              "นอกแผน" not in page.evaluate("()=>[...document.querySelectorAll('#jTbody .ghead')].filter(e=>e.textContent.indexOf('GRPX')>=0).map(e=>e.textContent).join('')")
              and "นอกแผน" in page.evaluate("()=>[...document.querySelectorAll('#jTbody .ghead')].filter(e=>e.textContent.indexOf('GRPY')>=0).map(e=>e.textContent).join('')"),
              jtext(page, "GRPX") + " || " + jtext(page, "GRPY"))
        page.evaluate("()=>setJFilter('offplan')"); page.wait_for_timeout(200)
        shown = jrows_syms(page, ["OLDC", "NOCARD2", "GRPX", "GRPY"])
        check(f"{tag} A2 ตัวกรอง 'นอกแผน': เหลือเฉพาะ NOCARD2 + GRPY (ไม้ที่ผูกการ์ดหลุดจากตัวกรอง)", shown == ["NOCARD2", "GRPY"], json.dumps(shown))
        n = page.evaluate("()=>journalStats().overall.nOffPlan")
        check(f"{tag} A2 สถิติ nOffPlan = 2 (NOCARD2 + gh1) · ไม่นับ olc/og1 ที่ผูกการ์ด", n == 2, str(n))
        check(f"{tag} A2 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()

    # A3 การ์ด L ซื้อระดับแรก
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, p26.doc26(), cards={"l1": p26.lcard("l1")})
    try:
        go(page); page.evaluate("()=>{ setPlanScope('ladder'); render(); }"); page.wait_for_timeout(400); ex(page, "l1")   # RG2b: การ์ด L อยู่หน้า Ladder
        page.click('[data-ldr-card="l1"] [data-ldr-buy], ' + card_sel("l1") + " [data-c-lbuy]"); page.wait_for_selector('.core-sheet [data-core-sheet="lbuy"]'); page.click("#clSave"); page.wait_for_timeout(700)
        t = next((x for x in p24.book_trades(page) if x["sym"] == "ZZZ"), None)
        check(f"{tag} A3 การ์ด L ซื้อระดับแรก (coreLBuySave) → trade unplanned:false", t is not None and t["unplanned"] is False, json.dumps(t))
    finally:
        browser.close()


# ───────────────────────── B · Watchlist Tier ─────────────────────────
def section_B_watch(pw, w, h, tag):
    wl = {"WLA": {"tier": "A", "tier_set_at": "2026-01-05", "note": "เดิม"},
          "WLOLD": {"tier": "A", "tier_set_at": "2025-09-30"}, "WLNEW": {"tier": "A", "tier_set_at": "2025-10-01"},
          "WLB": {"tier": "B", "tier_set_at": "2026-09-01"}, "WLNO": {}}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, p24.doc_with(main_trades=[], main_market="both"), wl=wl)
    try:
        page.evaluate("()=>switchTab('watch')"); page.wait_for_timeout(400)
        # ชิปในรายการ
        r = lambda s, sel: page.locator(f'.wlR[data-sym="{s}"] {sel}').count()
        check(f"{tag} B2 รายการ Watchlist: ชิป A/B แสดง · ยังไม่ตั้ง = ไม่แสดง · Tier A เกิน 12 เดือน (2025-09-30) = ชิปเทา 'ทบทวน' · 2025-10-01 = ไม่มี",
              r("WLA", '[data-wl-tier="A"]') == 1 and r("WLB", '[data-wl-tier="B"]') == 1 and r("WLNO", "[data-wl-tier]") == 0
              and r("WLOLD", "[data-wl-tier-review]") == 1 and r("WLNEW", "[data-wl-tier-review]") == 0 and r("WLA", "[data-wl-tier-review]") == 0, "")
        page.evaluate("()=>wlOpen('WLOLD')"); page.wait_for_timeout(300)
        check(f"{tag} B2 หัวรายละเอียด: ชิป Tier A + 'ทบทวน' ข้าง CORE tag", page.locator('.wlDT [data-wl-tier="A"]').count() == 1 and page.locator(".wlDT [data-wl-tier-review]").count() == 1)
        # (a) WT1: โมดัลเพิ่มไม่มีส่วน Tier · เพิ่มใหม่ไม่เขียนฟิลด์ tier (ตั้งผ่านปุ่ม "บันทึกเฉพาะ Tier" ในฟอร์มแผน Core)
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','NEWT'], {ticker:'NEWT', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(500)   # TD4b: Candidate ก็เพิ่มตรงไม่ได้แล้ว → seed เป็นตัวที่อยู่ใน Watchlist ก่อน
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','NEWU'], {ticker:'NEWU', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(500)   # TD4b: Candidate ก็เพิ่มตรงไม่ได้แล้ว → seed เป็นตัวที่อยู่ใน Watchlist ก่อน
        page.evaluate("()=>wlOpenAdd('NEWT')"); page.wait_for_timeout(150)
        check(f"{tag} B2 [WT1] โมดัลเพิ่ม: ไม่มี dropdown Tier · ไม่มีส่วน Tier (ซ่อน)", page.locator("#wlAddTier").count() == 0 and not page.locator("#wlAddTierBox").is_visible())
        page.click("#wlAddBtn"); page.wait_for_timeout(400)
        d = wl_doc(page, "NEWT")
        check(f"{tag} B2 [WT1] เพิ่มใหม่ → doc ไม่มีฟิลด์ tier/tier_set_at (เดิม: ตั้ง A ได้ในโมดัล)", d and "tier" not in d and "tier_set_at" not in d, json.dumps(d))
        page.evaluate("()=>wlOpenAdd('NEWU')"); page.click("#wlAddBtn"); page.wait_for_timeout(300)
        d = wl_doc(page, "NEWU")
        check(f"{tag} B2 เพิ่มใหม่ ไม่ตั้ง Tier → ไม่มีฟิลด์ tier/tier_set_at", d and "tier" not in d and "tier_set_at" not in d, json.dumps(d))
        # (b) แก้ Note อย่างเดียว
        page.evaluate("()=>wlOpenEdit('WLA')"); page.wait_for_timeout(150)
        st = page.inner_text("#wlAddTierSt")
        check(f"{tag} B2 [WT1] โมดัลแก้ไข: บรรทัดสถานะ 'Tier A · Fortress (เดิม) · ตั้งเมื่อ 2026-01-05' (เดิม: dropdown = A)", "Tier A" in st and "2026-01-05" in st and page.locator("#wlAddTier").count() == 0, st)
        shot(page, f"7e2b2-wl-tier-modal-{w}.png")
        page.fill("#wlAddNote", "แก้โน้ต"); page.click("#wlAddBtn"); page.wait_for_timeout(400)
        d = wl_doc(page, "WLA")
        check(f"{tag} B2 แก้ Note อย่างเดียว → tier 'A' · tier_set_at ไม่เปลี่ยน (2026-01-05)", d["note"] == "แก้โน้ต" and d["tier"] == "A" and d["tier_set_at"] == "2026-01-05", json.dumps(d))
        # (c) WT1: เปลี่ยนเป็น B = seed ฟิลด์ใน doc ตรง ๆ (เดิม: เลือก B ใน dropdown) → โมดัลแก้ไขแสดง 'Tier B'
        page.evaluate("([t])=>window.firebase.__mockDb.collection('users').doc('testuid').collection('watchlist').doc('WLA').update({tier:'B', tier_set_at:t})", [TODAY]); page.wait_for_timeout(300)
        page.evaluate("()=>wlOpenEdit('WLA')"); page.wait_for_timeout(150)
        d = wl_doc(page, "WLA"); st = page.inner_text("#wlAddTierSt")
        check(f"{tag} B2 [WT1] doc tier 'B' · tier_set_at = วันนี้ → โมดัลแก้ไขแสดง 'Tier B'", d["tier"] == "B" and d["tier_set_at"] == TODAY and st.startswith("Tier B"), json.dumps(d) + st)
        # (d) WT1: ล้าง Tier (เดิม: เลือก 'ยังไม่ตั้ง')
        page.click("#wlAddTierClr"); page.wait_for_timeout(400)
        d = wl_doc(page, "WLA")
        check(f"{tag} B2 [WT1] กด 'ล้าง Tier' → ลบฟิลด์ tier/tier_set_at (mock รองรับ FieldValue.delete)", d and d.get("tier") is None and d.get("tier_set_at") is None, json.dumps(d))
        check(f"{tag} B2 ไม่มี console error / alert", not ce and not pe and not dialogs, json.dumps([ce[:2], pe[:2], dialogs[:2]]))
    finally:
        browser.close()


def section_B_cards(pw, w, h, tag):
    A = lambda id, tk, tier="A", **kw: p24.card(id, "main", tk, tier=tier, tierReason="เหตุผล" if tier == "A" else None, plan={"entry": 100, "stop": 90}, stop=90, **kw)
    cards = {"k1": A("k1", "CA1"), "k2": A("k2", "CA2"), "k3": A("k3", "CA3"), "k4": A("k4", "CA4"), "k5": A("k5", "CA5"),
             "k6": A("k6", "CB1", "B"), "k7": A("k7", "CB2", "B"), "k8": A("k8", "PTT.BK"), "k10": A("k10", "CB3", "B"),
             "k9": p26.lcard("k9", ticker="LAA", tier="A")}
    wl = {"CA1": {"tier": "B", "tier_set_at": "2026-09-01"}, "CA2": {}, "CA4": {"tier": "A", "tier_set_at": "2025-09-30"}, "CA5": {"tier": "A", "tier_set_at": "2025-10-01"},
          "CB1": {"tier": "A", "tier_set_at": "2026-09-01"}, "PTT": {"tier": "B", "tier_set_at": "2026-09-01"}, "LAA": {"tier": "B", "tier_set_at": "2026-09-01"},
          "CB3": {"tier": "B", "tier_set_at": "2026-09-01"}}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, p24.doc_with(main_trades=[], main_market="both"), cards, wl)
    try:
        go(page)
        b = lambda id: badges(page, id)
        one = lambda id, lvl, code, text=None: (lambda x: len(x) == 1 and x[0]["level"] == lvl and x[0]["code"] == code and (text is None or x[0]["text"] == text))(b(id))
        check(f"{tag} B5 การ์ด A + Watchlist = B → เหลือง 'Watchlist = B · การ์ดยังเป็น A'", one("k1", "warn", "WL_B", "Watchlist = B · การ์ดยังเป็น A"), json.dumps(b("k1"), ensure_ascii=False))
        check(f"{tag} B5 การ์ด A + Watchlist ไม่ตั้ง Tier → เหลือง", one("k2", "warn", "NO_WL_TIER"), json.dumps(b("k2"), ensure_ascii=False))
        check(f"{tag} B5 การ์ด A + ไม่อยู่ Watchlist → เหลือง 'ไม่อยู่ใน Watchlist · ยังไม่ได้ทำการบ้าน'", one("k3", "warn", "NOT_IN_WATCHLIST", "ไม่อยู่ใน Watchlist · ยังไม่ได้ทำการบ้าน"), json.dumps(b("k3"), ensure_ascii=False))
        check(f"{tag} B5 การ์ด A + WL A ตั้ง 2025-09-30 (วันนี้ 2026-10-01) → เทา 'ทบทวน Tier'", one("k4", "muted", "REVIEW") and b("k4")[0]["text"].startswith("ทบทวน Tier"), json.dumps(b("k4"), ensure_ascii=False))
        check(f"{tag} B5 การ์ด A + WL A ตั้ง 2025-10-01 → ไม่มีป้าย", b("k5") == [], json.dumps(b("k5")))
        check(f"{tag} B5 การ์ด B + WL A → เทา · การ์ด B + ไม่อยู่ WL → เทา · การ์ด B + WL B → ไม่มี",
              one("k6", "muted", "WL_A") and one("k7", "muted", "NOT_IN_WATCHLIST") and b("k10") == [], json.dumps([b("k6"), b("k7"), b("k10")], ensure_ascii=False))
        check(f"{tag} B6 PTT.BK บนการ์ด จับคู่ PTT ใน Watchlist (WL = B → เหลือง)", one("k8", "warn", "WL_B"), json.dumps(b("k8"), ensure_ascii=False))
        check(f"{tag} B3 การ์ด L อยู่หน้า Ladder (RG2b) → ไม่มีป้าย Tier บนหน้า Winner", b("k9") == [], json.dumps(b("k9"), ensure_ascii=False))
        w_ids = ["k1", "k2", "k3", "k8"]; m_ids = ["k4", "k5", "k6", "k7", "k10", "k9"]   # RG2b: k9 (การ์ด L) ย้ายไปหน้า Ladder
        check(f"{tag} B7 แถวยุบ: ⚠ เมื่อมี warn (k1 k2 k3 k8 k9) · title = ข้อความ · ไม่มีเมื่อมีแค่ muted/ไม่มีป้าย",
              all(row_warn(page, i) for i in w_ids) and not any(row_warn(page, i) for i in m_ids) and row_warn(page, "k1") == "Watchlist = B · การ์ดยังเป็น A",
              json.dumps({i: row_warn(page, i) for i in w_ids + m_ids}, ensure_ascii=False))
        check(f"{tag} B7 ป้ายในตัวการ์ด: ระดับ muted อยู่ใน .ccChips ต่อท้ายชิป Tier · ระดับ warn (UX2) รวมอยู่ในบรรทัด ⚠ เดียวใต้ชิป", page.evaluate("()=>{ const m = document.querySelector('[data-core-card=\"k4\"] .ccChips [data-c-tierbadge]'); const w = document.querySelector('[data-core-card=\"k1\"] [data-c-warnline] [data-c-tierbadge]'); return !!m && !!m.previousElementSibling && m.previousElementSibling.hasAttribute('data-c-tier') && !!w && !document.querySelector('[data-core-card=\"k1\"] .ccChips [data-level=warn]'); }"))
        ex(page, "k1"); ex(page, "k4"); ex(page, "k9"); ex(page, "k3"); ex(page, "k2")
        page.evaluate("()=>document.querySelector('[data-core-card=\"k1\"]').scrollIntoView({block:'center'})"); page.wait_for_timeout(300)
        shot(page, f"7e2b2-card-tier-badges-{w}.png")
        # B8 ปุ่มกดได้
        dis = page.evaluate("()=>[...document.querySelectorAll('[data-core-card=\"k1\"] .ccBtns button')].filter(b=>b.disabled).length")
        page.click(card_sel("k1") + " [data-c-buy1]"); page.wait_for_timeout(250)
        check(f"{tag} B8 การ์ดที่มีป้ายเตือน: ปุ่มไม่ถูกล็อก · กดซื้อไม้ 1 แล้วเปิด sheet ได้", dis == 0 and p24.sheet_open(page, "buy1"), f"disabled={dis}")
        page.evaluate("()=>coreSheetClose()")
        page.click(card_sel("k1") + " [data-c-more]"); page.wait_for_timeout(100); page.click(card_sel("k1") + " .ccMenu [data-c-tierbtn]"); page.wait_for_timeout(250)
        info = txt(page, "[data-c-wlinfo]")
        check(f"{tag} B3 บล็อก Tier (sheet 'Tier…') แสดง 'Watchlist: Tier B (ตั้งเมื่อ 2026-09-01)' · ข้อมูลอย่างเดียว", info == "Watchlist: Tier B (ตั้งเมื่อ 2026-09-01)", str(info))
        page.evaluate("()=>coreSheetClose()")
        infos = {}
        for i in ("k2", "k3"):
            page.evaluate("(i)=>coreTierOpen(i)", i); page.wait_for_timeout(150); infos[i] = txt(page, "[data-c-wlinfo]"); page.evaluate("()=>coreSheetClose()")
        check(f"{tag} B3 บล็อก Tier: 'Watchlist: ยังไม่ตั้ง Tier' / 'ไม่อยู่ใน Watchlist'", infos == {"k2": "Watchlist: ยังไม่ตั้ง Tier", "k3": "ไม่อยู่ใน Watchlist"}, json.dumps(infos, ensure_ascii=False))
        page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]'); page.fill("#cnTicker", "CA1"); page.wait_for_timeout(150)
        i1 = txt(page, "[data-c-wlinfo]"); page.fill("#cnTicker", "NOTHERE"); page.wait_for_timeout(150); i2 = txt(page, "[data-c-wlinfo]")
        check(f"{tag} B3 ฟอร์มแผนใหม่: พิมพ์ ticker แล้วบรรทัด Watchlist อัปเดตตามทันที", i1 == "Watchlist: Tier B (ตั้งเมื่อ 2026-09-01)" and i2 == "ไม่อยู่ใน Watchlist", f"{i1} / {i2}")
        page.evaluate("()=>coreSheetClose()")
        tiers = {k: c["tier"] for k, c in p24.cards_db(page).items()}
        check(f"{tag} B3 ป้ายไม่เปลี่ยน Tier ของการ์ด (k1 ยัง A · k6 ยัง B)", tiers["k1"] == "A" and tiers["k6"] == "B", json.dumps(tiers))
        check(f"{tag} B ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
        if w <= 500: check(f"{tag} 16 แผง Core + ป้าย ไม่ล้นแนวนอน", no_h_overflow(page))
    finally:
        browser.close()
    # Watchlist error → ไม่มีป้ายเลย
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, p24.doc_with(main_trades=[], main_market="both"), {"k1": A("k1", "CA1"), "k3": A("k3", "CA3")}, wl, deny_wl=True)
    try:
        go(page); ex(page, "k1")
        n = page.evaluate("()=>[document.querySelectorAll('[data-c-tierbadge]').length, document.querySelectorAll('[data-c-wlwarn]').length, !!coreWatchInfo('CA1').loaded]")
        page.evaluate("()=>coreTierOpen('k1')"); page.wait_for_timeout(150)
        check(f"{tag} B5 Watchlist โหลดไม่ได้ (permission-denied) → ไม่มีป้าย/⚠ เลย · บรรทัด Watchlist ในฟอร์ม Tier ว่าง",
              n == [0, 0, False] and not (txt(page, "[data-c-wlinfo]") or ""), json.dumps(n))
        page.evaluate("()=>coreSheetClose()")
        check(f"{tag} B5 (Watchlist error) ปุ่มซื้อไม้ 1 ยังกดได้", not page.is_disabled(card_sel("k1") + " [data-c-buy1]"))
    finally:
        browser.close()


# ───────────────────────── C · ทางเข้า ─────────────────────────
def section_C(pw, w, h, tag):
    doc = p26.doc26()   # main = US · fam = TH
    wl = {"NVDA": {}, "PTT.BK": {}, "DUP": {}}
    cards = {"cdup": p24.card("cdup", "main", "DUP", tier="B", plan={"entry": 100, "stop": 90}, stop=90)}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards, wl)
    try:
        def via_watch(sym):
            page.evaluate("()=>{ coreSheetClose(); switchTab('watch'); }"); page.wait_for_timeout(250)
            page.evaluate("(s)=>wlOpen(s)", sym); page.wait_for_timeout(300)
            check(f"{tag} C1 หน้ารายละเอียด {sym}: มีปุ่ม 'เปิดแผน Core →'", page.locator("[data-c-open-plan]").count() == 1)
            page.click("[data-c-open-plan]"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]', timeout=3000); page.wait_for_timeout(200)
            return page.evaluate("()=>({tab: activeTab, scope: planScope, ticker: document.getElementById('cnTicker').value, acct: (document.getElementById('cnAcct')||{}).value})")
        s = via_watch("NVDA")
        check(f"{tag} C1 Watch → 'เปิดแผน Core →': แท็บแผน · scope หุ้น · sheet แผนใหม่ · ticker เติม NVDA · บัญชีตลาด US = main", s == {"tab": "plan", "scope": "stock", "ticker": "NVDA", "acct": "main"}, json.dumps(s))
        s = via_watch("PTT.BK")
        check(f"{tag} C1 PTT.BK → บัญชีตลาด TH = fam (family)", s == {"tab": "plan", "scope": "stock", "ticker": "PTT.BK", "acct": "fam"}, json.dumps(s))
        s = via_watch("DUP")
        msg = txt(page, "#cnErr") or ""
        check(f"{tag} C1 มีการ์ดเปิดของ ticker นั้นอยู่แล้ว → ข้อความเดิม 'มีการ์ด DUP อยู่แล้ว' + ปุ่ม 'ไปที่การ์ด'", "มีการ์ด DUP อยู่แล้ว" in msg and page.locator("#cnGoto").count() == 1, msg)
        page.evaluate("()=>coreSheetClose()"); page.evaluate("()=>coreNewOpen('main')"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
        check(f"{tag} C1 เปิดจากปุ่ม ＋ เดิม (ไม่ส่ง ticker) → ช่อง Ticker ว่างเหมือนเดิม", page.input_value("#cnTicker") == "")
        page.evaluate("()=>coreSheetClose()")
        src = open(INDEX, encoding="utf-8").read()
        check(f"{tag} C1 ลบคอมเมนต์ '7E-2: เปิดใหม่' ทั้งสองจุดแล้ว", "7E-2: เปิดใหม่" not in src)
        check(f"{tag} C1 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def section_C2(pw, w, h, tag):
    doc = p24.doc_with(main_trades=[], main_market="both")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, {})
    try:
        go_journal(page)
        check(f"{tag} C2 หัวแผง Closed Trades มีปุ่ม 'บันทึกไม้ย้อนหลัง'", page.locator("#jBackfillBtn").is_visible())
        page.click("#jBackfillBtn"); page.wait_for_selector('.core-sheet [data-core-sheet="backfill"]'); page.wait_for_timeout(300)
        check(f"{tag} 16 sheet ย้อนหลัง: ปุ่มบันทึก/ยกเลิกเห็นครบในจอ", in_view(page, "[data-bf-save]") and in_view(page, "[data-bf-cancel]") or w > 500, "")
        check(f"{tag} C2 ปุ่มบันทึกปิดอยู่จนกรอกครบ", page.is_disabled("#bfSave"))
        ncards0 = len(p24.cards_db(page))
        fill = lambda **k: [page.fill("#" + i, str(v)) for i, v in k.items()]
        # Core US
        page.select_option("#bfPort", "core"); fill(bfSym="BFUS", bfEntry=100, bfSl=90, bfQty=10, bfExit=110)
        page.fill("#bfDate", "2026-09-01"); page.fill("#bfExitDate", "2026-09-15"); page.wait_for_timeout(100)
        rs = page.evaluate("()=>[...document.querySelectorAll('#bfReason option')].map(o=>o.value)")
        if len(rs) > 1: page.select_option("#bfReason", rs[1])
        check(f"{tag} C2 กรอกถูกต้อง (Core US) → ปุ่มบันทึกเปิด", not page.is_disabled("#bfSave"), txt(page, "#bfErr") or "")
        shot(page, f"7e2b2-backfill-form-{w}.png")
        # ตรวจกติกา
        page.fill("#bfExitDate", "2026-10-02"); a = page.is_disabled("#bfSave"); ea = txt(page, "#bfErr") or ""
        page.fill("#bfExitDate", "2026-08-31"); b = page.is_disabled("#bfSave")
        page.fill("#bfExitDate", "2026-09-15"); page.fill("#bfSl", "100"); c_ = page.is_disabled("#bfSave")
        page.fill("#bfSl", "90"); page.select_option("#bfBias", "Short"); d_ = page.is_disabled("#bfSave")
        page.fill("#bfSl", "110"); e_ = not page.is_disabled("#bfSave")
        page.select_option("#bfBias", "Long"); page.fill("#bfSl", "90"); page.fill("#bfQty", "0"); f_ = page.is_disabled("#bfSave"); page.fill("#bfQty", "10")
        check(f"{tag} C2 ตรวจ: วันปิดอนาคต (2026-10-02) ✗ · วันปิด < วันเข้า ✗ · Long SL ≥ Entry ✗ · Short SL < Entry ✗ · Short SL 110 ✓ · Qty 0 ✗",
              a and b and c_ and d_ and e_ and f_ and "วันนี้" in ea, json.dumps([a, b, c_, d_, e_, f_, ea], ensure_ascii=False))
        page.click("#bfSave"); page.wait_for_timeout(500)
        t = next((x for x in p24.book_trades(page) if x["sym"] == "BFUS"), None)
        check(f"{tag} C2 บันทึกไม้ Core US → status closed · unplanned true · port core · mult 1 · cur USD · exit 110 / 2026-09-15 · เหตุผลปิดตามที่เลือก",
              t and t["status"] == "closed" and t["unplanned"] is True and t["port"] == "core" and t["mult"] == 1 and t["cur"] == "USD" and t["exitPrice"] == 110 and t["exitDate"] == "2026-09-15"
              and t["date"] == "2026-09-01" and (len(rs) < 2 or t.get("exitReason") == rs[1]), json.dumps(t, ensure_ascii=False))
        check(f"{tag} C2 ไม่สร้างการ์ดใหม่ · sheet ปิดแล้ว · แถวใน Journal ติดป้าย 'นอกแผน'", len(p24.cards_db(page)) == ncards0 and not page.locator(".core-sheet").count() and "นอกแผน" in jtext(page, "BFUS"), jtext(page, "BFUS"))
        # Core TH
        page.click("#jBackfillBtn"); page.wait_for_selector('.core-sheet [data-core-sheet="backfill"]')
        fill(bfSym="BFTH.BK", bfEntry=50, bfSl=45, bfQty=100, bfExit=40); page.fill("#bfDate", "2026-09-01"); page.fill("#bfExitDate", "2026-09-10"); page.click("#bfSave"); page.wait_for_timeout(400)
        t = next((x for x in p24.book_trades(page) if x["sym"] == "BFTH.BK"), None)
        check(f"{tag} C2 Core TH (.BK) → cur THB · mult 1 · ขาดทุนบันทึกได้", t and t["cur"] == "THB" and t["mult"] == 1 and t["unplanned"] is True and t["status"] == "closed", json.dumps(t))
        # Sat
        page.click("#jBackfillBtn"); page.wait_for_selector('.core-sheet [data-core-sheet="backfill"]')
        page.select_option("#bfPort", "satB"); fill(bfSym="XAUUSD"); page.wait_for_timeout(150)
        bx = page.is_visible("#bfBrokerBox"); opts = page.evaluate("()=>[...document.querySelectorAll('#bfBroker option')].map(o=>o.value)")
        fill(bfEntry=2650, bfSl=2620, bfQty=0.19, bfExit=2700); page.fill("#bfDate", "2026-09-02"); page.fill("#bfExitDate", "2026-09-12"); page.wait_for_timeout(100)
        check(f"{tag} C2 Sat: เห็นช่องสินค้า (SET1: ไม่มีโบรกแล้ว · สเปค XAUUSD ×100 USD มาจากสินค้า)", bx and opts == [""] and "XAUUSD" in page.evaluate("()=>document.querySelector('#bfBroker option').textContent") and "×100" in page.evaluate("()=>document.querySelector('#bfBroker option').textContent"), json.dumps(opts))
        page.click("#bfSave"); page.wait_for_timeout(400)
        t = next((x for x in p24.book_trades(page) if x["sym"] == "XAUUSD"), None)
        check(f"{tag} C2 บันทึกไม้ Sat → port satB · mult 100 · cur USD (จากโบรก XM) · closed · unplanned true", t and t["port"] == "satB" and t["mult"] == 100 and t["cur"] == "USD" and t["status"] == "closed" and t["unplanned"] is True, json.dumps(t))
        check(f"{tag} C2 ยังไม่มีการ์ดใหม่หลังบันทึกทั้ง 3 ไม้", len(p24.cards_db(page)) == ncards0)
        check(f"{tag} C2 ไม่มี console error / alert", not ce and not pe and not dialogs, json.dumps([ce[:2], pe[:2], dialogs[:2]]))
        if w <= 500: check(f"{tag} 16 หน้า Journal ไม่ล้นแนวนอน", no_h_overflow(page))
    finally:
        browser.close()


# ───────────────────────── D · ผูกการ์ด ↔ Positions ─────────────────────────
def fixture_D(full=True):
    def ut(id, sym): return T(id, "core", "open", sym=sym, entry=100, sl=90, qty=10, cur="USD", date="2026-09-25", openedAt="2026-09-25")
    trades = [ut("lk3", "LNK3"), ut("nl1", "NOLINK")]
    cards = {"ck3": p24.open_card("ck3", "lk3", ticker="LNK3", qty=10, entry=100, sl=90, px=105, pxDate=TODAY), "cpl": p26.lcard("cpl", ticker="PLN")}
    if full:
        trades += [ut("lk1", "LNK1"), ut("lk2", "LNK2"), p26.ltrade("lo", sym="ZZZ")]
        cards.update({"ck1": p24.open_card("ck1", "lk1", ticker="LNK1", qty=10, entry=100, sl=90, px=105, pxDate=TODAY),
                      "ck2": p24.open_card("ck2", "lk2", ticker="LNK2", qty=10, entry=100, sl=90, px=105, pxDate=TODAY),
                      "lo": p26.lopen("lo", ticker="ZZZ", pxDate=TODAY)})
        trades[-1]["id"] = "t_lo"; cards["lo"]["trade_id"] = "t_lo"
    return p26.doc26(main_trades=trades), cards


def pos_btn(page, tid, label):
    return page.locator(f'[data-pos="{tid}"] button:has-text("{label}")').locator("visible=true").first


def section_D(pw, w, h, tag):
    doc, cards = fixture_D(True)
    doc["books"]["main"]["trades"].append(T("jc1", "core", "closed", sym="JCL", entry=100, sl=90, qty=1, exitPrice=110, exitDate="2026-09-20", date="2026-09-10", cur="USD"))
    cards["cjc"] = p24.open_card("cjc", "jc1", ticker="JCL", qty=1, entry=100, sl=90)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, doc, cards)
    try:
        go_plan(page)
        # 11 [แก้]
        lk = pos_btn(page, "lk3", "แก้")
        check(f"{tag} D11 ปุ่ม [แก้] ของไม้ผูกการ์ด: title 'แก้ผ่านการ์ด Core' · ไม้ไม่ผูก = ไม่มี title นี้", lk.get_attribute("title") == "แก้ผ่านการ์ด Core" and pos_btn(page, "nl1", "แก้").get_attribute("title") is None)
        lk.click(); page.wait_for_timeout(1200)
        st = page.evaluate("""()=>{ const c = document.querySelector('[data-core-card="ck3"]'), r = c.getBoundingClientRect(), el = document.elementFromPoint(r.left + r.width/2, Math.min(Math.max(r.top + r.height/2, 1), innerHeight - 1));
          return {modal: document.getElementById('teOverlay').classList.contains('show'), open: c.classList.contains('open'), hit: el && el.closest('[data-core-card]') ? el.closest('[data-core-card]').dataset.coreCard : null, scope: planScope}; }""")
        check(f"{tag} D11 [แก้] ไม้ผูกการ์ด → ไม่มีโมดัลแก้ไม้ · การ์ดขยาย · อยู่ในจอ (elementFromPoint กลางการ์ด = การ์ด LNK3) · scope หุ้น", st == {"modal": False, "open": True, "hit": "ck3", "scope": "stock"}, json.dumps(st))
        go_plan(page); pos_btn(page, "nl1", "แก้").click(); page.wait_for_timeout(250)
        check(f"{tag} D11 ไม้ไม่ผูกการ์ด → [แก้] เปิดโมดัลเดิม", page.evaluate("()=>document.getElementById('teOverlay').classList.contains('show')"))
        page.evaluate("()=>closeTradeEdit()")
        r1 = page.evaluate("()=>{ openTradeEdit('lk3','main'); return document.getElementById('teOverlay').classList.contains('show'); }")
        r2 = page.evaluate("()=>{ openTradeEdit('lk3','main',{fromCard:true}); const s = document.getElementById('teOverlay').classList.contains('show'); closeTradeEdit(); return s; }")
        check(f"{tag} D8 openTradeEdit ตรง ๆ กับไม้ที่ผูกการ์ดและยังเปิด → เปิดการ์ดแทน (ไม่มีโมดัล) · เมนู 'แก้ Entry/SL' ของการ์ด (fromCard) ยังเปิดโมดัลได้", r1 is False and r2 is True, f"{r1} {r2}")
        page.evaluate("()=>openTradeEdit('jc1','main')"); page.wait_for_timeout(200)
        check(f"{tag} D5 Journal ✎ ของไม้ปิดที่มีการ์ด → เปิดโมดัลแก้ไม้ตามเดิม", page.evaluate("()=>document.getElementById('teOverlay').classList.contains('show')"))
        page.evaluate("()=>closeTradeEdit()")

        # 12 [ยกเลิก]
        go_plan(page); pos_btn(page, "lk1", "ยกเลิก").click(); page.wait_for_selector('.core-sheet [data-core-sheet="link"]')
        msg = txt(page, "[data-c-link-msg]") or ""
        check(f"{tag} D12 [ยกเลิก] ไม้ผูกการ์ด → sheet ยืนยัน 'ยกเลิกไม้ LNK1 จะปิดการ์ด Core LNK1 ด้วย (ประวัติไม้ในการ์ดยังอยู่)'", msg == "ยกเลิกไม้ LNK1 จะปิดการ์ด Core LNK1 ด้วย (ประวัติไม้ในการ์ดยังอยู่)", msg)
        check(f"{tag} 16 sheet ยืนยัน: ปุ่มครบในจอ", in_view(page, "[data-c-link-ok]") and in_view(page, "[data-c-link-no]"))
        shot(page, f"7e2b2-pos-link-confirm-{w}.png")
        before = (trade_of(page, "lk1")["status"], p24.cards_db(page)["ck1"]["status"])
        page.click("[data-c-link-no]"); page.wait_for_timeout(300)
        after = (trade_of(page, "lk1")["status"], p24.cards_db(page)["ck1"]["status"])
        check(f"{tag} D12 กดยกเลิกใน sheet ยืนยัน → ไม่มีอะไรเปลี่ยน (ไม้ยัง open · การ์ดยัง open · ไม่เปิดโมดัล Cancel)", before == after == ("open", "open") and not page.locator(".core-sheet").count()
              and not page.evaluate("()=>document.getElementById('cancelOverlay').classList.contains('show')"), f"{before} {after}")
        pos_btn(page, "lk1", "ยกเลิก").click(); page.wait_for_selector('.core-sheet [data-core-sheet="link"]'); page.click("[data-c-link-ok]"); page.wait_for_timeout(300)
        check(f"{tag} D12 ยืนยัน → เปิดโมดัล Cancel เดิม · ยังไม่ปิดการ์ดจนกว่าจะบันทึก", page.evaluate("()=>document.getElementById('cancelOverlay').classList.contains('show')") and p24.cards_db(page)["ck1"]["status"] == "open")
        page.fill("#cancelNote", "ไม่เข้าแล้ว"); page.evaluate("()=>confirmCancel()"); page.wait_for_timeout(600)
        c1 = p24.cards_db(page)["ck1"]
        check(f"{tag} D12 บันทึก Cancel → ไม้ cancelled · การ์ด status closed · closedBy 'cancel' · มี closed_at", trade_of(page, "lk1")["status"] == "cancelled" and c1["status"] == "closed" and c1.get("closedBy") == "cancel" and c1.get("closed_at"), json.dumps(c1)[:300])
        go(page)
        page.evaluate("()=>document.querySelectorAll('[data-c-closedgroup]').forEach(d=>d.open=true)")   # PX2: กลุ่มปิดแล้วพับไว้ — กางก่อนอ่านข้อความแถว
        ctxt = txt(page, '[data-core-card="ck1"][data-kind="closed"]') or ""
        check(f"{tag} D6 การ์ดที่ปิดไปอยู่กลุ่มปิดแล้ว (ไม่ใช่แผน) · แสดงเหตุผล 'ยกเลิกไม้' · ไม่มีการ์ดแผน/เปิดของ LNK1", "ปิดแล้ว" in (txt(page, '[data-c-closedgroup] > summary') or "") and "ยกเลิกไม้" in ctxt and page.locator('[data-core-card="ck1"][data-kind="plan"], [data-core-card="ck1"][data-kind="open"]').count() == 0, ctxt)

        # 13 [ลบ]
        go_plan(page); nd0 = len(dialogs)
        pos_btn(page, "lk2", "ลบ").click(); page.wait_for_selector('.core-sheet [data-core-sheet="link"]')
        msg = txt(page, "[data-c-link-msg]") or ""
        check(f"{tag} D13 [ลบ] ไม้ผูกการ์ด → sheet 'ลบไม้ LNK2 จะปิดการ์ด Core LNK2 ด้วย' · ไม่มี confirm() ของเบราว์เซอร์", msg == "ลบไม้ LNK2 จะปิดการ์ด Core LNK2 ด้วย" and len(dialogs) == nd0, f"{msg} {dialogs}")
        page.click("[data-c-link-ok]"); page.wait_for_timeout(600)
        c2 = p24.cards_db(page)["ck2"]
        check(f"{tag} D13 ยืนยัน → ไม้ถูกลบ · การ์ด closed · closedBy 'delete' · ไม่มี confirm()", trade_of(page, "lk2") is None and c2["status"] == "closed" and c2.get("closedBy") == "delete" and len(dialogs) == nd0, json.dumps(c2)[:300])
        go(page)
        page.evaluate("()=>document.querySelectorAll('[data-c-closedgroup]').forEach(d=>d.open=true)")   # PX2: กลุ่มปิดแล้วพับไว้ — กางก่อนอ่านข้อความแถว
        ctxt = txt(page, '[data-core-card="ck2"][data-kind="closed"]') or ""
        check(f"{tag} D6 กลุ่มปิดแล้วแสดง 'ลบไม้' (การ์ดที่ไม้ถูกลบไม่กลับไปเป็นแผน)", "ลบไม้" in ctxt, ctxt)
        # ไม้ไม่ผูกการ์ด ยังใช้ confirm() เดิม
        go_plan(page); pos_btn(page, "nl1", "ลบ").click(); page.wait_for_timeout(400)
        check(f"{tag} D3 ไม้ไม่ผูกการ์ด → [ลบ] ยังใช้ confirm() เดิม ('ลบรายการนี้?') · ลบได้", len(dialogs) == nd0 + 1 and dialogs[-1] == "ลบรายการนี้?" and trade_of(page, "nl1") is None, json.dumps(dialogs))
        # Journal ✕ ของไม้ปิดที่ผูกการ์ด
        nd1 = len(dialogs)
        page.evaluate("()=>delTrade('jc1','main')"); page.wait_for_selector('.core-sheet [data-core-sheet="link"]')
        page.click("[data-c-link-ok]"); page.wait_for_timeout(500)
        cj = p24.cards_db(page)["cjc"]
        check(f"{tag} D5 Journal ✕ ของไม้ปิดที่มีการ์ด → sheet ยืนยันแบบข้อ 3 · ลบไม้ + การ์ด closed/delete · ไม่มี confirm()", trade_of(page, "jc1") is None and cj["status"] == "closed" and cj.get("closedBy") == "delete" and len(dialogs) == nd1, json.dumps(cj)[:200])
        # 14 ตัวเลข: ยกเลิกการ์ด L ที่เปิดอยู่ด้วย แล้วเทียบกับ fixture ที่ไม่เคยมีการ์ด/ไม้ของ lk1 lk2 lo
        go_plan(page); pos_btn(page, "t_lo", "ยกเลิก").click(); page.wait_for_selector('.core-sheet [data-core-sheet="link"]'); page.click("[data-c-link-ok]"); page.wait_for_timeout(300)
        page.fill("#cancelNote", "x"); page.evaluate("()=>confirmCancel()"); page.wait_for_timeout(600)
        cl = p24.cards_db(page)["lo"]
        check(f"{tag} D12 การ์ด L ที่เปิดอยู่ก็ปิดตามเมื่อยกเลิกไม้ (closedBy cancel)", cl["status"] == "closed" and cl.get("closedBy") == "cancel", json.dumps(cl)[:200])
        nx = nums(page)
    finally:
        browser.close()
    # Y = fixture ที่ไม่เคยมี lk1/lk2/lo (แต่มีของอื่นเหมือนกัน)
    docY, cardsY = fixture_D(False)
    docY["books"]["main"]["trades"] = [t for t in docY["books"]["main"]["trades"] if t["id"] != "nl1"]
    browserY, _c, pageY, ceY, peY, _d = launch(pw, w, h, docY, cardsY)
    try:
        ny = nums(pageY)
    finally:
        browserY.close()
    check(f"{tag} D14 หลังยกเลิก/ลบ: เงินสดว่าง · ชั้น 2 (ตอนนี้/เต็ม) · สัดส่วน L · ทุน W เท่ากับตอนไม่มีการ์ดเหล่านั้น", nx == ny and ny["cash"] > 0, json.dumps([nx, ny]))
    check(f"{tag} D ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))


# ───────────────────────── E · BE ─────────────────────────
def section_E(pw, w, h, tag):
    def cl(id, sym, ex_): return T(id, "core", "closed", sym=sym, entry=100, sl=90, qty=1, exitPrice=ex_, exitDate="2026-09-20", date="2026-09-10", cur="THB")
    trades = [cl("e0", "PBE0", 100), cl("e4", "PBE4", 99.6), cl("ew", "PWIN", 101), cl("el", "PLOSS", 99)]
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, p24.doc_with(main_trades=trades, main_market="both"), {})
    try:
        go_journal(page)
        tg = lambda s: page.evaluate("""(s)=>[...document.querySelectorAll('#jContent_closed tr, #jContent_closed .tcard')].filter(e=>e.textContent.indexOf(s)>=0).map(e=>[...e.querySelectorAll('.tag.win,.tag.loss,.tag.be')].map(x=>x.textContent.trim()+':'+x.className.replace(/\\s+/g,' ')).join(',')).filter(Boolean)""", s)
        got = {s: tg(s) for s in ("PBE0", "PBE4", "PWIN", "PLOSS")}
        check(f"{tag} E15 P&L 0 และ −0.4 (ปัดเป็น 0) → 'BE' (คลาส tag be) · +1 → WIN · −1 → LOSS (ทั้งตารางและการ์ดมือถือ)",
              all(x.startswith("BE:tag be") for x in got["PBE0"] + got["PBE4"]) and got["PBE0"] and got["PBE4"]
              and all(x.startswith("WIN:") for x in got["PWIN"]) and got["PWIN"] and all(x.startswith("LOSS:") for x in got["PLOSS"]) and got["PLOSS"], json.dumps(got))
        shot(page, f"7e2b2-journal-be-{w}.png")
        page.evaluate("()=>setJFilter('loss')"); page.wait_for_timeout(200)
        sh = jrows_syms(page, ["PBE0", "PBE4", "PWIN", "PLOSS"])
        check(f"{tag} E15 ตัวกรอง Loss: มีแค่ PLOSS (BE ไม่อยู่ใน Loss)", sh == ["PLOSS"], json.dumps(sh))
        page.evaluate("()=>setJFilter('win')"); page.wait_for_timeout(200)
        sh = jrows_syms(page, ["PBE0", "PBE4", "PWIN", "PLOSS"])
        check(f"{tag} E15 ตัวกรอง Win: มีแค่ PWIN", sh == ["PWIN"], json.dumps(sh))
        page.evaluate("()=>setJFilter('all')"); page.wait_for_timeout(200)
        sh = jrows_syms(page, ["PBE0", "PBE4", "PWIN", "PLOSS"])
        check(f"{tag} E15 'ทั้งหมด' เห็น BE ด้วย (ครบ 4 ไม้)", len(sh) == 4, json.dumps(sh))
        wr = page.evaluate("()=>{ const o = journalStats().overall; return [o.n, o.wins, o.winRate]; }")
        check(f"{tag} E15 Win Rate ไม่เปลี่ยน: 4 ไม้ · ชนะ 1 (BE ไม่นับเป็น win) → 25%", wr == [4, 1, 25], json.dumps(wr))
        check(f"{tag} E ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def grep_tests():
    src = open(INDEX, encoding="utf-8").read()
    check("grep: tradeOffPlan / coreCardOfTrade มีอยู่ · makeTradeObject รับ fromCard · coreBuy1Save + coreLBuySave ส่ง fromCard:true (2 จุด)",
          "function tradeOffPlan(" in src and "function coreCardOfTrade(" in src and src.count("status:'open', fromCard:true") == 2 and "o.fromCard" in src)
    check("grep: ไม่เหลือการอ่าน t.unplanned เพื่อแสดงผล/นับ (เหลือเฉพาะ tradeOffPlan · makeTradeObject · plannedEntry)",
          len(re.findall(r"\b(?:t|legs\[0\]|x)\.unplanned", src)) == 2 and "!!t.unplanned && !coreCardOfTrade(t)" in src, str(re.findall(r".{30}\bt\.unplanned.{10}", src)))
    check("grep: coreEff เช็ก status==='closed' ก่อน (ไม่คืน plan ให้การ์ดที่ปิดแล้ว)", re.search(r"function coreEff\(c\)\{\s*if\(c\.status==='closed'\)", src) is not None)
    check("grep: ไม่เหลือ confirm('ลบรายการนี้?') ใน delTrade แบบเดิมที่ไม่ผ่านไม้ผูกการ์ด · มี delTradeDo / coreLinkAsk", "function delTradeDo(" in src and "function coreLinkAsk(" in src)
    cs = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "sync_core_size.py"), "--check", INDEX], capture_output=True, text=True)
    check("sync_core_size --check: สำเนาใน index.html ตรง core-size.js (ไม่ได้แตะ core-size.js)", cs.returncode == 0, cs.stdout + cs.stderr)


def main():
    with sync_playwright() as pw:
        for (w, h) in ((1440, 900), (430, 900)):
            tag = f"[chromium/{w}]"
            for fn in (section_A, section_B_watch, section_B_cards, section_C, section_C2, section_D, section_E):
                try: fn(pw, w, h, tag)
                except Exception as e:
                    import traceback; traceback.print_exc()
                    check(f"{tag} {fn.__name__} ไม่ throw", False, repr(e))
    grep_tests()
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nengine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    sys.exit(1 if f else 0)


if __name__ == "__main__":
    main()
