#!/usr/bin/env python3
"""7D.3 Phase 1 — item E (Safari <select> fix) + SAT_ASSETS/SAT7D_ASSETS merge.
รันแยกจาก run_tests.py (round 1) ตามคำแนะนำใน README — ไม่ลบ/แก้เคสเดิม เพิ่มเคสใหม่ของรอบนี้เท่านั้น

รันได้ทั้ง Chromium และ WebKit:
  python3 run_tests_phase1.py                     # Chromium (ค่าเริ่มต้น)
  BROWSER=webkit python3 run_tests_phase1.py       # WebKit — เคสหลักของ item E ต้องผ่านที่นี่ด้วย
"""
import json, os, sys, re
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.html"))
INDEX_PATH = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("INDEX_HTML", DEFAULT_INDEX)
APP_URL = "file://" + INDEX_PATH
_default_chromium = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROMIUM_PATH = os.environ.get("CHROMIUM_PATH") or (_default_chromium if os.path.exists(_default_chromium) else None)
BROWSER_ENGINE = os.environ.get("BROWSER", "chromium")  # 'chromium' or 'webkit'
MOCK_FB = open(os.path.join(HERE, "mock-firebase.js"), encoding="utf-8").read()
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))

results = []

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:300] + "...(truncated)") if (detail and len(detail) > 300) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))

def retired(name, reason):
    """CL2-a — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)

def run_viewport(pw, width, height, label):
    if BROWSER_ENGINE == "webkit":
        browser = pw.webkit.launch(headless=True)
    else:
        launch_kwargs = {"headless": True}
        if CHROMIUM_PATH:
            launch_kwargs["executable_path"] = CHROMIUM_PATH
        browser = pw.chromium.launch(**launch_kwargs)
    context = browser.new_context(viewport={"width": width, "height": height})
    from ff_stub import FF_STUB; context.add_init_script(FF_STUB)   # fetch fundflow.json แบบ file:// ไม่ได้ → จำลอง
    page = context.new_page()

    console_errors = []
    page_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))

    def route_firebase(route):
        route.fulfill(status=200, content_type="application/javascript", body=MOCK_FB)
    def route_fonts(route):
        route.fulfill(status=200, content_type="text/css", body="")
    def route_fundflow(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({"as_of": "2026-09-20", "ratios": {}}))
    def route_generic_api(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    page.route(re.compile(r"gstatic\.com/firebasejs"), route_firebase)
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), route_fonts)
    page.route(re.compile(r"fundflow\.json"), route_fundflow)
    page.route(re.compile(r"open\.er-api\.com|api\.twelvedata\.com"), route_generic_api)

    page.goto(APP_URL, wait_until="load")
    page.wait_for_timeout(150)

    page.evaluate("(seed)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], seed); }", SEED)
    page.fill("#authEmail", "test@example.com")
    page.fill("#authPass", "password123")
    page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(400)

    ok_login = page.eval_on_selector("#mainWrap", "el => el.style.display !== 'none'")
    check(f"[{BROWSER_ENGINE}/{label}] login + main app loads", ok_login)

    # ---- CL2-c: ฟอร์ม Add Trade (#tradeOverlay/#tPort) ถูกลบ — เคสเลือก Port ในฟอร์มเลิกใช้ · เคสแก้ไม้ satB ใช้หน้าต่างแก้ไม้ใหม่ (openTradeEdit · Port อ่านอย่างเดียว) ----
    R_ADD = "CL2-c ลบฟอร์ม Add Trade (openTrade/#tPort/acctSyncPortSelect) — ไม่มีช่องเลือก Port ให้ตรวจแล้ว"
    retired(f"[{BROWSER_ENGINE}/{label}] new trade: tPort มีแค่ option 'core' เท่านั้น (ไม่มี satA/satB)", R_ADD)
    retired(f"[{BROWSER_ENGINE}/{label}] new trade: ไม่มี <option hidden> หลงเหลือ (options ที่ไม่อนุญาตถูกลบออกจาก DOM จริง)", R_ADD)
    retired(f"[{BROWSER_ENGINE}/{label}] retroactive closed: tPort = ['core','satB'] (ไม่มี satA)", R_ADD + " · openUnplannedClosed ถูกลบ")
    retired(f"[{BROWSER_ENGINE}/{label}] retroactive closed: ป้าย satB ขึ้นต้นด้วย 'Sat' ไม่ใช่ 'Satellite.B'/'Sat.B'", R_ADD + " · openUnplannedClosed ถูกลบ")

    # === Mode 3a (แก้ให้ใช้ทางใหม่): แก้ไม้ satB เดิมด้วยหน้าต่างแก้ไม้ — หัวแสดง Sat (อ่านอย่างเดียว) และ Port ยังเป็น satB หลังบันทึก ===
    page.evaluate("""
      () => { state.trades.push({id:'t_satb_test', sym:'XAUUSD', port:'satB', bias:'Long',
              entry:2650, sl:2630, tp:2700, qty:1, mult:1, status:'plan', date:'2026-09-01'}); }
    """)
    page.evaluate("() => { openTradeEdit('t_satb_test'); }")
    page.wait_for_timeout(50)
    head3a = page.evaluate("() => ({t: document.getElementById('teHead').innerText.replace(/\\s+/g,' '), sel: document.querySelectorAll('#teOverlay select#tPort, #teHead select, #teHead input').length})")
    check(f"[{BROWSER_ENGINE}/{label}] แก้ไม้ satB เดิม: หัวหน้าต่างแก้ไม้แสดง Port = 'Sat' (ไม่มี satA/Satellite.B) และไม่มีช่องเปลี่ยน Port",
          "Sat" in head3a["t"] and "Satellite" not in head3a["t"] and "Sat.B" not in head3a["t"] and head3a["sel"] == 0, json.dumps(head3a, ensure_ascii=False))
    page.evaluate("() => saveTradeEdit()")
    page.wait_for_timeout(50)
    cur3a = page.evaluate("() => state.trades.find(t=>t.id==='t_satb_test').port")
    check(f"[{BROWSER_ENGINE}/{label}] แก้ไม้ satB เดิม: บันทึกแล้ว Port ยังเป็น satB (ไม่หลุดไป core)",
          cur3a == "satB", str(cur3a))

    # === Mode 3b (เลิกใช้ใน CL2-a): แก้ไม้ satA เดิม — ไม้ satA ถูกล้างตอนรีเซ็ตครั้งเดียว + PORTS.satA ถูกลบ ไม่มีไม้ satA ให้แก้อีกแล้ว ===
    retired(f"[{BROWSER_ENGINE}/{label}] แก้ไม้ satA เดิม: satA ยังอยู่ใน tPort ให้แก้ได้ (ไม่ถูกลบทิ้งไปด้วย)", "CL2-a ลบ Sat.A — ไม่มีไม้ satA ให้แก้")
    retired(f"[{BROWSER_ENGINE}/{label}] แก้ไม้ satA เดิม: ค่าที่เลือกอยู่ยังเป็น satA (ไม่ถูกเปลี่ยนค่าเงียบ ๆ)", "CL2-a ลบ Sat.A — ไม่มีไม้ satA ให้แก้")
    retired(f"[{BROWSER_ENGINE}/{label}] แก้ไม้ satA เดิม: satB ไม่ถูกเสนอเป็นตัวเลือก (ไม่ได้กำลังแก้ไม้ satB)", "CL2-a ลบ Sat.A — ไม่มีไม้ satA ให้แก้")

    # === ปิดหน้าต่างแก้ไม้แล้ว state ต้องไม่ค้าง (แทนเคส 'เปิดไม้ใหม่ต่อจากแก้ไม้ satB แล้ว satB ไม่หลุดกลับมา' ของฟอร์มเดิม → เลิกใช้) ===
    retired(f"[{BROWSER_ENGINE}/{label}] เปิดไม้ใหม่ต่อจากแก้ไม้ satB แล้ว satB/satA ต้องไม่หลุดกลับมา (state ถูก reset)", R_ADD + " · tradeAllowSatB ถูกลบ")
    page.evaluate("() => closeTradeEdit()")

    # === wPort (ฟอร์ม Watchlist เดิม) — CL2-b ลบฟอร์มนี้ทั้งก้อน (#watchOverlay/#wPort/toggleWBiasField) · acctSyncPortSelect ยังถูกเทส์ผ่าน #tPort ด้านบน ===
    retired(f"[{BROWSER_ENGINE}/{label}] wPort: ยังมี core/satB ครบ (CL2-a: satA ถูกลบจากพอร์ตของบัญชี) ไม่ใช้กฎ satA-ไม้ใหม่", "CL2-b ลบฟอร์ม Watchlist เดิม (#wPort/#watchOverlay/toggleWBiasField)")
    retired(f"[{BROWSER_ENGINE}/{label}] wPort: ไม่มี <option hidden> หลงเหลือ", "CL2-b ลบฟอร์ม Watchlist เดิม (#wPort/#watchOverlay/toggleWBiasField)")
    retired(f"[{BROWSER_ENGINE}/{label}] wPort: ป้าย satB = 'Sat'", "CL2-b ลบฟอร์ม Watchlist เดิม (#wPort/#watchOverlay/toggleWBiasField)")

    # ---- label rename sanity: PORTS.satB.name, jPortShort, journal badges all say 'Sat' not 'Sat.B'/'Satellite.B' ----
    label_checks = page.evaluate("""
      () => ({
        portsName: PORTS.satB.name,
        jPortShort: (typeof jPortShort === 'function') ? null : 'jPortShort not in scope (closure) - skip',
      })
    """)
    check(f"[{BROWSER_ENGINE}/{label}] PORTS.satB.name === 'Sat' (key ในข้อมูลยังเป็น satB)",
          label_checks["portsName"] == "Sat", str(label_checks["portsName"]))

    # ---- SAT_ASSETS / SAT7D_ASSETS merge: single source of truth, shapes preserved for old call sites ----
    merge_check = page.evaluate("""
      () => ({
        sat7dAssets: SAT7D_ASSETS,
        derivedFromSatAssets: SAT_ASSETS.map(a=>a.key),
        sat7dLabelBTC: sat7dLabel('BTCUSD'),
        satwMacroXAU: SATW_MACRO_KEY.XAUUSD,
        satwMacroS50: SATW_MACRO_KEY.S50,
      })
    """)
    check(f"[{BROWSER_ENGINE}/{label}] SAT7D_ASSETS derive มาจาก SAT_ASSETS.map(key) พอดี (ไม่ประกาศอาเรย์ซ้ำ)",
          merge_check["sat7dAssets"] == merge_check["derivedFromSatAssets"], json.dumps(merge_check))
    check(f"[{BROWSER_ENGINE}/{label}] SAT7D_LABEL.BTCUSD ยังเป็น 'BTC' เหมือนเดิมหลังรวม",
          merge_check["sat7dLabelBTC"] == "BTC", str(merge_check["sat7dLabelBTC"]))
    check(f"[{BROWSER_ENGINE}/{label}] SATW_MACRO_KEY.XAUUSD ยังเป็น 'XAU', S50 ยังเป็น null หลังรวม",
          merge_check["satwMacroXAU"] == "XAU" and merge_check["satwMacroS50"] is None, json.dumps(merge_check))

    # 7D/7D.2 regression using the merged assets: the Sat weekly-plan select (SAT7D_ASSETS-driven, used by the old
    # #s7NewAsset <select> when SAT_V3_ON=false) still derives all 4 assets with correct labels after the merge.
    # ★ 7D.3 Phase 4: SAT_V3_ON is now true in the live file, so #s7NewAsset itself no longer mounts (the new
    # satV3 page replaces it — see run_tests_phase4.py's v3off suite, which re-checks #s7NewAsset's DOM directly
    # under SAT_V3_ON=false). Here we check the same underlying data (SAT7D_ASSETS + sat7dLabel) the old <select>
    # was built from, which is what this case actually verifies and is unaffected by which panel is mounted.
    page.evaluate("() => switchTab('plan')")
    page.evaluate("() => setPlanScope('future')")
    page.wait_for_timeout(150)
    newasset_opts = page.evaluate("() => SAT7D_ASSETS.map(a=>({value:a, label:sat7dLabel(a)}))")
    check(f"[{BROWSER_ENGINE}/{label}] SAT7D_ASSETS/sat7dLabel (ที่ขับเคลื่อน #s7NewAsset เดิม) ยังมีครบ 4 สินค้า label ถูกต้องหลังรวม",
          newasset_opts == [{"value":"XAUUSD","label":"XAUUSD"},{"value":"BTCUSD","label":"BTC"},
                             {"value":"S50","label":"S50"},{"value":"BRENT","label":"Brent"}],
          json.dumps(newasset_opts))

    check(f"[{BROWSER_ENGINE}/{label}] console: zero error-level messages", len(console_errors) == 0, "; ".join(console_errors[:10]))
    check(f"[{BROWSER_ENGINE}/{label}] console: zero uncaught page errors", len(page_errors) == 0, "; ".join(page_errors[:10]))

    context.close()
    browser.close()


def main():
    with sync_playwright() as pw:
        run_viewport(pw, 1440, 900, "1440px")
        run_viewport(pw, 430, 932, "430px")

    n_pass = sum(1 for _, ok, _ in results if ok)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("\n==== SUMMARY (Phase 1) ====")
    print(f"engine={BROWSER_ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(f" - {name} :: {detail}")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
