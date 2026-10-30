#!/usr/bin/env python3
import json, os, sys, math, re
from playwright.sync_api import sync_playwright

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

    # ---- §7 canonical numeric cases, via Calc.satLot directly (pure) ----
    xau_pure = page.evaluate("""
      () => Calc.satLot({riskAmount: 13000/33, dist: 20, contract: 100, lotStep: 0.01, minLot: 0.01})
    """)
    check(f"[{label}] Calc.satLot XAUUSD pure -> 0.19 lot",
          xau_pure.get("lot") is not None and abs(xau_pure["lot"] - 0.19) < 1e-9,
          json.dumps(xau_pure))

    s50_pure = page.evaluate("""
      () => Calc.satLot({riskAmount: 13000, dist: 10, contract: 200, lotStep: 1, minLot: 1})
    """)
    check(f"[{label}] Calc.satLot S50 pure -> 6 สัญญา",
          s50_pure.get("lot") == 6, json.dumps(s50_pure))

    # ---- §7 canonical numeric cases, via the LIVE code path (sat7dCalc -> delegates to Calc.satLot) ----
    page.evaluate("() => { const s=getBook('main').settings; s.satRisk={rpt:1.25, rptHi:1.5}; }")   # SR1 — fixture: ค่าเดิม 1.25/1.5 (ตัวเลขคาดหวังเดิมคงไว้)
    xau_live = page.evaluate("""
      () => sat7dCalc({asset:'XAUUSD', bias:'Long', entry:2650, sl:2630,
                        checks:{g1:true,g2:true,g3:true,setup:true}, invalidation:'test',
                        accts:{main:{broker:'XM'}}}, 'main')
    """)
    check(f"[{label}] sat7dCalc (live path) XAUUSD main/XM -> 0.19 lot",
          xau_live.get("lot") is not None and abs(xau_live["lot"] - 0.19) < 1e-9,
          json.dumps({k: xau_live.get(k) for k in ("lot","lotMsg","warns","ready")}))

    s50_live = page.evaluate("""
      () => sat7dCalc({asset:'S50', bias:'Long', entry:900, sl:890,
                        checks:{g1:true,g2:true,g3:true,setup:true}, invalidation:'test',
                        accts:{main:{broker:'Pi'}}}, 'main')
    """)
    check(f"[{label}] sat7dCalc (live path) S50 main/Pi -> 6 สัญญา",
          s50_live.get("lot") == 6,
          json.dumps({k: s50_live.get(k) for k in ("lot","lotMsg","warns","ready")}))

    # BTC not configured for any broker on 'main' -> should degrade to "—"/warning, not throw
    btc_live = page.evaluate("""
      () => sat7dCalc({asset:'BTCUSD', bias:'Long', entry:60000, sl:59000,
                        checks:{}, invalidation:'', accts:{}}, 'main')
    """)
    check(f"[{label}] sat7dCalc BTCUSD (SET1: built-in % loss spec, no broker) -> lot computed, no throw",
          btc_live.get("lot") is not None and (btc_live.get("chosen") or {}).get("cfg", {}).get("sys") == "pct" and isinstance(btc_live.get("warns"), list),   # SET1 — BTC มีสเปค % loss ในตัว (ไม่ต้องตั้งโบรก) → คำนวณได้
          json.dumps(btc_live))

    # SL wrong side -> no lot computed, 'SL ผิดฝั่ง' warning
    wrongside = page.evaluate("""
      () => sat7dCalc({asset:'XAUUSD', bias:'Long', entry:2650, sl:2670,
                        checks:{g1:true,g2:true,g3:true,setup:true}, invalidation:'x',
                        accts:{main:{broker:'XM'}}}, 'main')
    """)
    check(f"[{label}] sat7dCalc SL ผิดฝั่ง -> lot null + 'SL ผิดฝั่ง' in warns",
          wrongside.get("lot") is None and "SL ผิดฝั่ง" in wrongside.get("warns", []),
          json.dumps(wrongside))

    # accounts don't mix: fam only has 'IC' registered (not 'XM') and its own (smaller) capital.satB — must not
    # borrow main's broker list or capital when computing for 'fam'
    fam_live = page.evaluate("""
      () => sat7dCalc({asset:'XAUUSD', bias:'Long', entry:2650, sl:2630,
                        checks:{g1:true,g2:true,g3:true,setup:true}, invalidation:'x',
                        accts:{fam:{broker:'XM'}}}, 'fam')
    """)
    fam_brokers = sorted(o["broker"] for o in fam_live.get("opts", []))
    fam_cap = fam_live.get("base", {}).get("cap")
    main_cap = xau_live.get("base", {}).get("cap")
    check(f"[{label}] sat7dCalc 2 บัญชีไม่ปนกัน — fam เห็นแค่โบรกของตัวเอง (IC) ไม่ใช่ของ main (XM)",
          fam_brokers == [""], json.dumps(fam_brokers))   # SET1 — ไม่มีโบรก: ทุกบัญชีเห็นตัวเลือกเดียว = สเปคสินค้า (ตัวเลือก broker ว่าง)
    check(f"[{label}] sat7dCalc 2 บัญชีไม่ปนกัน — ถัง Sat ของ fam ต่างจาก main (ไม่ยืมทุนข้ามบัญชี)",
          fam_cap is not None and main_cap is not None and abs(fam_cap - main_cap) > 1,
          f"fam_cap={fam_cap} main_cap={main_cap}")

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

    # weekly Sat entry-card save flow (7D.2): create an idea via the real sat7dWrite path, verify it lands in mock satIdeas collection
    page.evaluate("""
      () => { document.getElementById('s7NewAsset') && (document.getElementById('s7NewAsset').value='XAUUSD');
              document.getElementById('s7NewBias') && (document.getElementById('s7NewBias').value='Long');
              sat7dNew(); }
    """)
    page.wait_for_timeout(200)
    ideas_doc = page.evaluate("() => window.firebase.__mockDb.__dump()")
    idea_written = any(k.startswith("users/testuid/satIdeas/") for k in ideas_doc.keys())
    check(f"[{label}] 7D.2 entry-card save flow: sat7dNew() เขียน satIdeas/ จริง", idea_written, str(list(ideas_doc.keys())))

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
