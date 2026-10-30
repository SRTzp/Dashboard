#!/usr/bin/env python3
"""CL2-b — ลบโค้ด 4 ก้อน: Checklist · Ideas · Missed · Fund Checklist + Import JSON + ฟอร์ม Watchlist เดิม + ฟอร์ม Growth Gate
mock Firestore (ไม่ต่อเน็ต) · 1440px + 430px · seed.json ปัจจุบัน · ภาพเก็บที่ tests/screenshots/cl2b-*.png
รัน: python3 run_tests_phase20.py [/path/to/index.html]
เทียบขนาด/ไอคอนปุ่ม ＋ กับ index.backup-pre-CL2b.html (อยู่โฟลเดอร์แม่ของ index.html) — ถ้าไม่มีไฟล์นั้นจะข้ามเฉพาะเคสเทียบ (พิมพ์ SKIP)"""
import copy, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
UID = "testuid"
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:600] + "...(truncated)") if (detail and len(detail) > 600) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def retired(name, reason):
    """CL2-c — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)


def shot(page, name, sel=None):
    try:
        if sel and page.locator(sel).count():
            page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else:
            page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e:
        print("shot fail", name, e)


def T(id, port, status, **kw):
    d = {"id": id, "date": "2026-09-10", "sym": id.upper(), "port": port, "bias": "Long", "entry": 100, "sl": 95, "tp": None, "qty": 10,
         "mult": 1, "cur": "THB", "status": status, "unplanned": False}
    d.update(kw); return d


MISSED_TAGS = [{"id": "keepme", "label": "แท็ก missed เดิมของผู้ใช้", "offPlan": True}]


def make_doc():
    doc = copy.deepcopy(SEED)
    doc["books"]["main"]["trades"] = [
        T("cl1", "core", "closed", sym="CLOSA", exitPrice=110, exitDate="2026-09-20", discScore="3", setupScore="2"),
        T("cn1", "core", "cancelled", sym="CANCA", cancelDate="2026-09-12", cancelNote="เปลี่ยนใจ"),
        T("pl1", "core", "plan", sym="PLANA"),
    ]
    doc["books"]["main"]["reasonTags"] = {"missed": copy.deepcopy(MISSED_TAGS)}
    return doc


def launch(pw, w, h, doc, path=None):
    lk = {"headless": True}
    if base.CHROMIUM_PATH: lk["executable_path"] = base.CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    context = browser.new_context(viewport={"width": w, "height": h})
    from ff_stub import FF_STUB; context.add_init_script(FF_STUB)
    page = context.new_page()
    ce, pe, dialogs = [], [], []
    page.on("console", lambda m: ce.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: pe.append(str(e)))
    page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))
    page.route(re.compile(r"gstatic\.com/firebasejs"), lambda r: r.fulfill(status=200, content_type="application/javascript", body=base.MOCK_FB))
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), lambda r: r.fulfill(status=200, content_type="text/css", body=""))
    page.route(re.compile(r"fundflow\.json|open\.er-api\.com|api\.twelvedata\.com"), lambda r: r.fulfill(status=200, content_type="application/json", body="{}"))
    page.goto("file://" + (path or INDEX), wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("() => localStorage.setItem('bkLastBackupAt', String(Date.now()))")   # กัน backup อัตโนมัติ
    page.evaluate("(d)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], d); }", doc)
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(500)
    return browser, context, page, ce, pe, dialogs


def dump_book(page, acct="main"):
    return page.evaluate("(a)=>{ const d = window.firebase.__mockDb.__dump()['users/testuid']; return d && d.books && d.books[a]; }", acct)


def present(page, sel): return page.evaluate("(s)=>!!document.querySelector(s)", sel)


def btn_info(page):
    return page.evaluate("""() => { const b = document.querySelector('.hbtns>button.primary'); if(!b) return null;
        const r = b.getBoundingClientRect(), ic = b.querySelector('.btnIcon'), cs = getComputedStyle(b);
        return {w: Math.round(r.width*10)/10, h: Math.round(r.height*10)/10, icon: ic ? ic.textContent : null, iconFs: ic ? getComputedStyle(ic).fontSize : null,
                fs: cs.fontSize, title: b.title, txt: b.innerText.replace(/\\s+/g,' ').trim()}; }""")


def run(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, make_doc())
    try:
        # ───── §1 ปุ่ม ＋ / ปุ่มลัด T — CL2-c ลบฟอร์ม Add Trade + ปุ่ม ＋ + ปุ่มลัด T (7E-2 จะเปิดใหม่ที่การ์ด Core) ─────
        R_ADD = "CL2-c ลบฟอร์ม Add Trade + ปุ่ม ＋ + ปุ่มลัด T"
        retired(f"{tag} ปุ่ม ＋ แถบบน: onclick=openTrade() · ไอคอน ＋", R_ADD)
        retired(f"{tag} ปุ่ม ＋: ขนาด/ไอคอน/ฟอนต์/ข้อความ เท่าไฟล์ก่อนแก้ (กว้าง×สูง · font · ไอคอน)", R_ADD)
        shot(page, f"cl2b-topbar-{w}.png", ".topbar")
        retired(f"{tag} กดปุ่ม ＋ → #tradeOverlay เปิด · ไม่มี #checklistOverlay ใน DOM", R_ADD)
        retired(f"{tag} กด T → #tradeOverlay เปิด · ไม่มี #checklistOverlay ใน DOM", R_ADD)

        # ───── DOM: ของที่ต้องหายไป ─────
        gone = ["#checklistOverlay", "#ideasPanel", "#ideaOverlay", "#missedOverlay", "#fcDetailOverlay", "#impOverlay", "#watchOverlay",
                "#checklistDraftsPanel", "#missedPanel", "#jColBtn_missed", "#tStatus option[value=missed]"]
        found = [s for s in gone if present(page, s)]
        check(f"{tag} DOM: ไม่มี #checklistOverlay · #ideasPanel · #ideaOverlay · #missedOverlay · #fcDetailOverlay · #impOverlay · #watchOverlay · jColBtn_missed · option[value=missed]", not found, json.dumps(found))
        check(f"{tag} ปุ่ม 📥 Import / ปุ่ม Missed ในตารางแผนไม่อยู่ใน DOM", not page.evaluate("() => !!document.querySelector('[onclick*=\"openImportCL\"],[onclick*=\"openMissedModal\"],[onclick*=\"openIdeaModal\"]')"))

        # ───── Journal ─────
        page.evaluate("() => switchTab('journal')"); page.wait_for_timeout(300)
        kinds = page.evaluate("() => [JV_KINDS, JINC_STATUS]")
        check(f"{tag} Journal: JV_KINDS = closed+cancel · JINC_STATUS = closed+cancelled", kinds == [["closed", "cancel"], ["closed", "cancelled"]], json.dumps(kinds))
        heads = page.evaluate("() => [...document.querySelectorAll('#tabJournal .panel-head h2')].map(e=>e.innerText.replace(/\\s+/g,' ').trim()).filter(Boolean)")
        check(f"{tag} Journal: หัวพาเนลไม่มี Missed · มี Cancelled Trades", not any("Missed" in x for x in heads) and any("Cancelled" in x for x in heads), json.dumps(heads, ensure_ascii=False))
        shot(page, f"cl2b-journal-{w}.png")
        cn = page.evaluate("() => (document.getElementById('cancelTbody').innerText + document.getElementById('cancelCards').innerText)")
        check(f"{tag} Journal: ไม้ cancelled ยังแสดง (CANCA)", "CANCA" in cn, cn[:200])
        page.evaluate("() => openCancelModal('cn1','main')"); page.wait_for_timeout(200)
        check(f"{tag} Journal: ไม้ cancelled ยังแก้ได้ (openCancelModal เปิด #cancelOverlay)", page.evaluate("() => document.getElementById('cancelOverlay').classList.contains('show')"))
        page.evaluate("() => document.getElementById('cancelOverlay').classList.remove('show')")
        page.evaluate("() => openTradeEdit('cl1','main')"); page.wait_for_timeout(250)
        sc = page.evaluate("() => ({d: document.getElementById('tDiscScore').value, s: document.getElementById('tSetupScore').value, show: document.getElementById('teOverlay').classList.contains('show')})")
        check(f"{tag} Journal: คะแนนวินัย/Setup ยังแสดงในหน้าต่างแก้ไม้ (3 / 2) (CL2-c: openTradeEdit)", sc["show"] and sc["d"] == "3" and sc["s"] == "2", json.dumps(sc))
        page.evaluate("() => { document.getElementById('tSetupScore').value = '1'; }")
        page.evaluate("() => saveTradeEdit()"); page.wait_for_timeout(300)
        tr = page.evaluate("() => getBook('main').trades.find(t=>t.id==='cl1')")
        check(f"{tag} Journal: แก้คะแนน Setup แล้วบันทึกได้ (setupScore 1 · discScore 3) (CL2-c: saveTradeEdit)", tr and tr.get("setupScore") == 1 and tr.get("discScore") == 3, json.dumps(tr))
        lab = page.evaluate("() => [scoreLabelText('disc','3'), scoreLabelText('setup','2'), typeof scoreUsedCount, typeof cloneScoreLabels]")
        check(f"{tag} คะแนนรีวิว: scoreLabelText/scoreUsedCount/cloneScoreLabels ยังอยู่ (jReviewCell เช็กในกลุ่ม grep)", lab[2:] == ["function"] * 2 and all(lab[:2]), json.dumps(lab, ensure_ascii=False))

        # ───── Reason tag manager ─────
        page.evaluate("() => switchTab('plan')"); page.wait_for_timeout(200)
        rk = page.evaluate("() => Object.keys(REASON_KINDS)")
        check(f"{tag} ตัวจัดการแท็ก: หมวดเหลือ exit + cancel (ไม่มี missed)", rk == ["exit", "cancel"], json.dumps(rk))
        for kind in ("exit", "cancel"):
            page.evaluate("(k)=>openReasonManager(k)", kind); page.wait_for_timeout(150)
            r = page.evaluate("() => ({show: document.getElementById('reasonMgrOverlay').classList.contains('show'), title: document.getElementById('reasonMgrTitle').textContent, n: document.querySelectorAll('#reasonMgrList input[type=text]').length})")
            check(f"{tag} ตัวจัดการแท็ก: เปิดหมวด {kind} ได้ (มีรายการแท็ก)", r["show"] and r["n"] > 0 and "พลาด" not in r["title"], json.dumps(r, ensure_ascii=False))
            if kind == "cancel": shot(page, f"cl2b-reasontags-{w}.png", "#reasonMgrOverlay .modal")
            if kind == "exit":
                page.fill("#newReasonTag", "แท็กทดสอบ CL2b"); page.evaluate("() => addReasonTag()"); page.wait_for_timeout(200)
            page.evaluate("() => document.getElementById('reasonMgrOverlay').classList.remove('show')")
        page.wait_for_timeout(1800)   # รอ debounce persist
        bk = dump_book(page)
        check(f"{tag} ตัวจัดการแท็ก: เซฟแล้ว reasonTags.missed ใน mock ยังอยู่ (ไม่ถูกลบ/ไม่ถูกทับ) และ exit ได้แท็กใหม่",
              bk and bk.get("reasonTags", {}).get("missed") == MISSED_TAGS and any(x["label"] == "แท็กทดสอบ CL2b" for x in bk["reasonTags"].get("exit", [])), json.dumps((bk or {}).get("reasonTags"), ensure_ascii=False)[:500])
        check(f"{tag} DEFAULT_REASON_TAGS.missed ยังอยู่ในโค้ด", page.evaluate("() => Array.isArray(DEFAULT_REASON_TAGS.missed) && DEFAULT_REASON_TAGS.missed.length > 0"))
        lbl = page.evaluate("() => [...document.querySelectorAll('.setsec label')].map(e=>e.textContent.trim()).filter(x=>/Closed Trade/.test(x))")
        check(f"{tag} ตั้งค่า: ป้ายขนาดฟอนต์ 'Closed Trade' ไม่อ้าง Missed", lbl == [], json.dumps(lbl, ensure_ascii=False))

        # ───── Watch: เพิ่มหุ้น · R/GG ─────
        page.evaluate("() => switchTab('watch')"); page.wait_for_timeout(300)
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist','ZZTEST'], {ticker:'ZZTEST', market:'US', port:'core', note:'', industry:'', added_at:new Date().toISOString()}); wlStop(); wlStart(); }"); page.wait_for_timeout(500)   # TD4b: Candidate ก็เพิ่มตรงไม่ได้แล้ว → seed เป็นตัวที่อยู่ใน Watchlist ก่อน
        page.evaluate("() => wlOpenAdd('ZZTEST')"); page.wait_for_timeout(200)
        check(f"{tag} Watch: wlOpenAdd เปิดฟอร์มเพิ่มหุ้น (#wlAddOverlay)", page.evaluate("() => document.getElementById('wlAddOverlay').classList.contains('show')"))
        page.fill("#wlAddSym", "ZZTEST"); page.evaluate("() => wlAddOnSym()"); page.wait_for_timeout(100)
        shot(page, f"cl2b-watch-add-{w}.png", "#wlAddOverlay .modal")
        page.evaluate("() => wlAddSave()"); page.wait_for_timeout(500)
        rows = page.evaluate("() => wlRowsAll().wl.map(r=>r.sym)")
        check(f"{tag} Watch: เพิ่มหุ้น ZZTEST ผ่าน wlOpenAdd → wlAddSave ได้ (อยู่ในรายการ)", "ZZTEST" in rows, json.dumps(rows))
        retired(f"{tag} Watch: ป้าย R/GG ไม่พัง (wlGG · ggRow · GG_MAX · ggScoreOfSym · setupFactor เรียกได้)", "CL2-d ลบ wlGG/ggRow/GG_*/ggScoreOfSym/setupFactor ทั้งบล็อก (phase22 ตรวจแทนว่า Watch ไม่มีป้าย R/GG · เพิ่มหุ้นได้)")
        shot(page, f"cl2b-watch-{w}.png")
        # Industry manager
        page.evaluate("() => openIndustryManager()"); page.wait_for_timeout(150)
        page.fill("#newIndustryName", "CL2bIndustry"); page.evaluate("() => addIndustry()"); page.wait_for_timeout(150)
        has = page.evaluate("() => state.industries.includes('CL2bIndustry')")
        page.evaluate("() => deleteIndustry('CL2bIndustry')"); page.wait_for_timeout(150)
        gone2 = page.evaluate("() => !state.industries.includes('CL2bIndustry')")
        check(f"{tag} Industry manager: เพิ่ม/ลบ ได้", has and gone2, json.dumps([has, gone2]))
        page.evaluate("() => document.getElementById('industryOverlay').classList.remove('show')")

        # ───── Add Trade: ไม้ core ใหม่ — CL2-c ลบฟอร์ม (7E-2 จะเปิดใหม่ที่การ์ด Core) ─────
        page.evaluate("() => switchTab('plan')"); page.wait_for_timeout(200)
        retired(f"{tag} Add Trade: บันทึกไม้ core ใหม่ได้ (plan:core) · Calc/SZ ทำงาน (มี hint ขนาดไม้)", "CL2-c ลบฟอร์ม Add Trade (saveTrade/calcHint) — สร้างไม้ผ่านฟอร์มเลิกใช้")
        retired(f"{tag} SZ: szRenderCard ไม่ error", "CL2-c ลบ szRenderCard (ฟังก์ชัน sz* ที่ฟอร์มเรียกอย่างเดียว) — SZ/szHeat/szMaxPos/szCfg ยังอยู่ให้ CL2-d")
        shot(page, f"cl2b-plan-{w}.png")

        # ───── เซฟแล้ว ไม่มี key เก่า ─────
        page.wait_for_timeout(1800)
        bk = dump_book(page)
        bad = [k for k in ("checklistDrafts", "ideas", "failLog") if bk and k in bk]
        check(f"{tag} เซฟแล้ว books.main ไม่มี key checklistDrafts / ideas / failLog ใหม่", bk is not None and not bad, json.dumps([bad, list((bk or {}).keys())]))
        bk2 = dump_book(page, "fam")
        check(f"{tag} books.fam ไม่มี key checklistDrafts / ideas / failLog", not [k for k in ("checklistDrafts", "ideas", "failLog") if bk2 and k in bk2], json.dumps(list((bk2 or {}).keys())))

        # ───── ทุกแท็บ + ตั้งค่า ─────
        for t in ("flow", "mix", "watch", "plan", "journal"):
            page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(250)
            page.evaluate("() => { if(typeof render==='function') render(); }")
        for fn in ("openSystemSettings()", "openSettings()"):
            try:
                page.evaluate("() => " + fn); page.wait_for_timeout(200)
                page.keyboard.press("Escape"); page.wait_for_timeout(100)
            except Exception as e:
                check(f"{tag} เปิด {fn} ได้", False, str(e))
        check(f"{tag} เปิดทุกแท็บ + ตั้งค่า: ไม่มี console error", not ce, json.dumps(ce[:5], ensure_ascii=False))
        check(f"{tag} เปิดทุกแท็บ + ตั้งค่า: ไม่มี uncaught page error", not pe, json.dumps(pe[:5], ensure_ascii=False))
        if w <= 700:
            for t in ("flow", "mix", "watch", "plan", "journal"):
                page.evaluate("(t)=>switchTab(t)", t); page.wait_for_timeout(200)
                sw = page.evaluate("() => document.documentElement.scrollWidth")
                check(f"{tag} แท็บ {t}: ไม่ล้นแนวนอน (scrollWidth={sw} ≤ {w})", sw <= w)
    finally:
        browser.close()


def grep_tests():
    src = open(INDEX, encoding="utf-8").read()
    lines = src.split("\n")
    def cnt(pat, allow=None):
        n = [i for i, t in enumerate(lines) if pat in t and not (allow and allow in t)]
        return n
    must_not = ["openChecklist", "clState", "checklistDrafts", "renderIdeas", "ideaOverlay", "openMissedModal", "confirmMissed", "fcState", "FUND_CRITERIA",
                "importChecklistJSON", "openImportCL", "watchOverlay", "saveWatch", "renderGGForm", "ggState", "failLog"]
    for n in must_not:
        left = cnt(n, allow="CL2A_DROP_KEYS")   # ยกเว้นรายการ key เดิมของ cl2aStripLegacy
        check(f"grep index.html: ไม่เจอ {n} (ยกเว้นรายการ key ใน cl2aStripLegacy)", not left, json.dumps([i + 1 for i in left][:5]))
    must = ["jReviewCell", "discScore", "setupScore", "cloneScoreLabels", "escHtml", "openIndustryManager", "scoreLabelText", "makeTradeObject", "closePosOverlay", "Calc.newCount", "cl2aStripLegacy"]
    for n in must:
        check(f"grep index.html: ยังเจอ {n}", any(n in t for t in lines))
    for n in ["ggRow", "ggScoreOfSym", "SETUPS", "setupFactor"]:
        retired(f"grep index.html: ยังเจอ {n}", "CL2-d ลบบล็อก CL3 (gg*/GG_*/SETUPS/setupCfg/setupFactor) — phase22 ตรวจว่าไม่เจอแทน")
    retired("grep index.html: บล็อก 'CL3: ลบพร้อม SZ' มีหัว+ท้าย และ GG_ITEMS/GG_R/GG_MAX/ggClampTot/ggTotal/ggDone/setupCfg ยังอยู่", "CL2-d ลบบล็อก CL3 ทั้งก้อน")


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440x900"), (430, 900, "430x900")):
            run(pw, w, h, label)
    grep_tests()
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"engine=chromium  PASS: {p}  FAIL: {f}  TOTAL: {len(results)}")
    if f:
        print("\nFAILED:")
        for n, ok, d in results:
            if not ok: print(" -", n, "::", d[:300])
        sys.exit(1)


if __name__ == "__main__":
    main()
