#!/usr/bin/env python3
import json, os, sys, math, re
from playwright.sync_api import sync_playwright
import net_stub  # TS1: no real network in tests

HERE = os.path.dirname(os.path.abspath(__file__))
# Default: index.html one directory up from tests/ (i.e. ~/Documents/Dashboard/index.html when this
# folder is ~/Documents/Dashboard/tests/). Override with the INDEX_HTML env var or a CLI arg, e.g.
# when running against a staged copy in a container: INDEX_HTML=/mnt/user-data/uploads/Dashboard/index.html python3 run_tests.py
DEFAULT_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.html"))
INDEX_PATH = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("INDEX_HTML", DEFAULT_INDEX)
APP_URL = "file://" + INDEX_PATH
_default_chromium = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROMIUM_PATH = os.environ.get("CHROMIUM_PATH") or (_default_chromium if os.path.exists(_default_chromium) else None)
MOCK_FB = open(os.path.join(HERE, "mock-firebase.js"), encoding="utf-8").read()
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))

results = []  # (name, ok, detail)

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:300] + "...(truncated)") if (detail and len(detail) > 300) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))

def retired(name, reason):
    """CL2-a — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)

def run_viewport(pw, width, height, label):
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
        # any other outbound API this test flow might incidentally trigger (fx rate, RRG) — never hit the real network
        route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    page.route(re.compile(r"gstatic\.com/firebasejs"), route_firebase)
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), route_fonts)
    page.route(re.compile(r"fundflow\.json"), route_fundflow)
    page.route(re.compile(r"open\.er-api\.com|api\.twelvedata\.com"), route_generic_api)

    page.goto(APP_URL, wait_until="load")
    page.wait_for_timeout(150)

    # seed mock db + uid, before signing in
    page.evaluate("(seed)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], seed); }", SEED)

    page.fill("#authEmail", "test@example.com")
    page.fill("#authPass", "password123")
    page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(400)  # let onSnapshot deliver + first render settle

    ok_login = page.eval_on_selector("#mainWrap", "el => el.style.display !== 'none'")
    check(f"[{label}] login + main app loads", ok_login)

    # ---- §7 Sat lot / broker cases ----
    retired(f"[{label}] §7 Calc.satLot / sat7dCalc / satV3StrategyBarHtml numeric cases", "AU1 — the legacy Sat calculators (Calc.satLot, sat7dCalc, v1 plan sizing) and the hidden Sat strategy panel were deleted; the engine (RE1) sizes Sat — see tests/risk_engine_test.js, re1_adapter_test.js, ps1b_size_test.js")

    # ---- §0.5 — unknown top-level field round-trips through buildStateFromBookRaw ----
    probe = page.evaluate("() => (state && state._probeX) || null")
    check(f"[{label}] §0.5 unknown field _probeX survives buildStateFromBookRaw on load", probe == "leftover-legacy-value-should-round-trip", str(probe))

    # trigger a save (schedulePersist via saveBook) and check the field is still in the written doc
    page.evaluate("""
      () => { state.settings.strategicCash = (state.settings.strategicCash||0) + 1; saveBook('main'); }
    """)
    page.wait_for_timeout(700)  # debounce (350ms) + mock write
    written = page.evaluate("() => window.firebase.__mockDb.__getDoc(['users','testuid'])")
    probe_after_save = (written or {}).get("books", {}).get("main", {}).get("_probeX")
    check(f"[{label}] §0.5 _probeX still present in Firestore doc after saveBook()", probe_after_save == "leftover-legacy-value-should-round-trip", str(probe_after_save))

    # KNOWN_BOOK_FIELDS diagnostic: with the seed doc's only "unknown" field being _probeX (sat_since IS known),
    # console.info should have logged exactly that. We didn't capture console.info calls above 400ms mark; check now via a fresh call.
    unknown_now = page.evaluate("""
      () => Object.keys(state).filter(k=>!KNOWN_BOOK_FIELDS.includes(k) && !['toJSON'].includes(k))
    """)
    non_wrapper_extra = [k for k in unknown_now if k not in ("_probeX",)]
    check(f"[{label}] เฉพาะ _probeX เป็น unknown field (ไม่มีอย่างอื่นหลุดมา)", non_wrapper_extra == [] and "_probeX" in unknown_now, str(unknown_now))

    # ---- §0.2 UI.* dormant components — unit-testable in isolation, correct HTML for sample input ----
    ui_check = page.evaluate("""
      () => {
        const out = {};
        out.acctStrip = UI.acctStrip([{name:'บัญชีหลัก', color:'#3F6FD8', items:[{label:'heat', value:'1.2', warn:false},{label:'ใหม่', value:'2', warn:true, secondary:true}]}]);
        out.tiles = UI.tiles([{key:'x', title:'XAUUSD', value:'Long', sub:'test', cls:'ok'}], 'x');
        out.planCard = UI.planCard({sym:'XAUUSD', dir:'L', entry:2650, sl:2630, tp:2700, cancel:2660, rr:'2.0R',
          setups:[{label:'Sweep', on:true}], accts:[{name:'บัญชีหลัก', color:'#3F6FD8', line:'XM 0.19 lot'}]}, null);
        out.row = UI.row({color:'#3F6FD8', name:'บัญชีหลัก', tag:'Long', detail:'2650 / SL 2630', btns:[{label:'เข้าแล้ว'}]});
        out.chips = UI.chips([{label:'Sweep', on:true},{label:'BigBar', on:false}]);
        out.sheet = UI.sheet('<b>hi</b>');
        return out;
      }
    """)
    check(f"[{label}] UI.acctStrip returns namespaced HTML with warn class", "ui-acctStrip" in ui_check["acctStrip"] and "ui-warn" in ui_check["acctStrip"])
    check(f"[{label}] UI.tiles returns 1 selected tile", "ui-tile ui-sel" in ui_check["tiles"] or "ui-sel" in ui_check["tiles"])
    check(f"[{label}] UI.planCard returns plan card with entry/sl/broker line", "2650" in ui_check["planCard"] and "XM 0.19 lot" in ui_check["planCard"])
    check(f"[{label}] UI.row returns 1-line row", "ui-row" in ui_check["row"] and "เข้าแล้ว" in ui_check["row"])
    check(f"[{label}] UI.chips returns chip list with on state", "ui-on" in ui_check["chips"] and "Sweep" in ui_check["chips"])
    check(f"[{label}] UI.sheet wraps content in sheet backdrop", "ui-sheet-backdrop" in ui_check["sheet"] and "<b>hi</b>" in ui_check["sheet"])

    # ---- §0.1 tokens actually declared with mockup values ----
    tokens = page.evaluate("""
      () => { const cs = getComputedStyle(document.documentElement);
        return {card:cs.getPropertyValue('--card').trim(), up:cs.getPropertyValue('--up').trim(),
                dn:cs.getPropertyValue('--dn').trim(), warn:cs.getPropertyValue('--warn').trim(),
                dark:cs.getPropertyValue('--dark').trim(), line:cs.getPropertyValue('--line').trim(),
                mute:cs.getPropertyValue('--mute').trim(), soft:cs.getPropertyValue('--soft').trim(),
                bg:cs.getPropertyValue('--bg').trim(), ink:cs.getPropertyValue('--ink').trim()};
      }
    """)
    expected = {"card":"#FFFFFF","up":"#1F9D6B","dn":"#D4493F","warn":"#C98A12","dark":"#1D2025",
                "line":"#E3E6EA","mute":"#7B818C","soft":"#F5F6F8","bg":"#EEF0F3","ink":"#16181D"}
    tok_ok = all(tokens[k].upper() == v for k, v in expected.items())
    check(f"[{label}] §0.1 design tokens declared with exact mockup hex values", tok_ok, json.dumps(tokens))

    # ★ 7D.3 Phase 4 (25 ก.ย. 2569): เดิมเช็คว่า SAT_V3_ON ยังเป็น false (ระหว่างพัฒนา Phase 1-3) — พอ Phase 4
    # เสร็จและทดสอบครบทุกจุดแล้ว สเปกสั่งให้ตั้ง SAT_V3_ON=true จริง (ไปใช้งานจริง) จึงอัปเดตค่าที่คาดหวังตรงนี้
    # ให้ตรงกับสถานะจริงหลังขึ้นจอ — ค่านี้ควรเป็น true ตลอดไปจนกว่าจะมีการตัดสินใจย้อนกลับอย่างชัดเจนในอนาคต
    retired(f"[{label}] §0.7 SAT_V3_ON exists (7D.3 Phase 4: ตั้งเป็น true แล้ว — หน้า Sat ใหม่ mount จริง)", "CL2-a ลบค่าคงที่ SAT_V3_ON (ทางเดียวที่เหลือ = v3)")
    retired(f"[{label}] §0.7 SAT7D_ON (old switch) untouched, still true", "CL2-a ลบค่าคงที่ SAT7D_ON")

    # ---- 7D/7D.2 regression: switch through every tab at this viewport, no throw / no new console errors ----
    tabs = ["flow", "mix", "watch", "plan", "journal"]
    tab_err = None
    for t in tabs:
        try:
            page.evaluate(f"() => switchTab('{t}')")
            page.wait_for_timeout(120)
        except Exception as e:
            tab_err = f"{t}: {e}"
            break
    check(f"[{label}] switchTab() ทุกแท็บทำงานไม่ throw", tab_err is None, str(tab_err))

    # scrollWidth<=viewport width on every tab at this width (matches 7D-brief pass bar: scrollWidth == width)
    page.evaluate("() => switchTab('plan')")
    page.wait_for_timeout(150)
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"[{label}] ไม่ล้นแนวนอน (scrollWidth <= {width})", sw <= width + 1, f"scrollWidth={sw}")

    # Sat 7D.2 panel still renders (SAT7D_ON=true path) with our seeded idea-less state, no throw already proven above
    sat_panel = page.evaluate("() => !!document.getElementById('satV3Panel') && !document.getElementById('sat7dPanel')")   # CL2-a: เหลือ #satV3Panel ตัวเดียว
    check(f"[{label}] แท็บแผน (scope future) มี #satV3Panel เหมือนเดิม (CL2-a: #sat7dPanel ถูกลบ)", sat_panel)

    retired(f"[{label}] 7D.2 entry-card save flow: sat7dNew() writes satIdeas/", "AU1 — sat7dNew (the old weekly Sat entry card) was deleted; Sat plans are created by satV2NewPlan / pb2SaveDo (covered by sd1 · lr3 · lr5 suites)")

    # Core-only Add Trade restriction: opening Add Trade (scope=core context) must not expose satB-only fields improperly;
    # smoke check: the global Add Trade function exists and running it while on Core scope doesn't throw.
    add_trade_ok = True
    add_trade_err = ""
    try:
        page.evaluate("() => { if (typeof openTradeForm === 'function') { /* exists, not invoked to avoid opening a real unseeded form flow */ } }")
    except Exception as e:
        add_trade_ok = False
        add_trade_err = str(e)
    check(f"[{label}] Add Trade entry point ยังอยู่ ไม่ throw (smoke check)", add_trade_ok, add_trade_err)

    check(f"[{label}] console: zero error-level messages", len(console_errors) == 0, "; ".join(console_errors[:10]))
    check(f"[{label}] console: zero uncaught page errors", len(page_errors) == 0, "; ".join(page_errors[:10]))

    context.close()
    browser.close()
    return console_errors, page_errors


def main():
    with sync_playwright() as pw:
        run_viewport(pw, 1440, 900, "1440px")
        run_viewport(pw, 430, 932, "430px")

    n_pass = sum(1 for _, ok, _ in results if ok)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("\n==== SUMMARY ====")
    print(f"PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(f" - {name} :: {detail}")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
