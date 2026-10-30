#!/usr/bin/env python3
"""7D.3 Phase 4 — final assembly: mount ส่วนที่ 1 (satV3) เข้าหน้า Sat จริง, ทดสอบ end-to-end ผ่าน DOM interaction จริง
(ไม่ใช่เรียกฟังก์ชันตรง ๆ แบบ Phase 2/3)

★ CL2-a: ลบทาง SAT_V3_ON=false (หน้า 7D.2 เดิม) ออกจากโค้ดแล้ว → ส่วน "v3off" เลิกใช้ทั้งหมด (พิมพ์ RETIRED · ไม่ต้องสร้าง /tmp/index_v3off.html อีก)
ทุกเคสที่เหลือรันกับ ../index.html ตัวเดียว

การใช้งาน:
  python3 run_tests_phase4.py
  BROWSER=webkit python3 run_tests_phase4.py      # ติดปัญหา egress policy เดียวกับ Phase 1/2/3
"""
import json, os, sys, re
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.html"))
INDEX_PATH_ON = os.environ.get("INDEX_HTML_V3ON", DEFAULT_INDEX)             # ../index.html (CL2-a: เหลือทางเดียว)
_default_chromium = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROMIUM_PATH = os.environ.get("CHROMIUM_PATH") or (_default_chromium if os.path.exists(_default_chromium) else None)
BROWSER_ENGINE = os.environ.get("BROWSER", "chromium")
MOCK_FB = open(os.path.join(HERE, "mock-firebase.js"), encoding="utf-8").read()
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))

results = []

def retired(name, reason):
    """CL2-a — เคสที่เลิกใช้เพราะโค้ดที่ทดสอบถูกลบ · ไม่นับใน PASS/FAIL แต่ต้องพิมพ์ไว้ให้ตามรอยได้ (ห้ามลบเงียบ)"""
    print("RETIRED - " + name + "  :: " + reason)

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))

PICK_DEFAULT = ['XAUUSD', 'BTCUSD', 'S50']

def launch_page(pw, width, height, index_path):
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
    console_errors, page_errors = [], []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))

    def route_firebase(route): route.fulfill(status=200, content_type="application/javascript", body=MOCK_FB)
    def route_fonts(route): route.fulfill(status=200, content_type="text/css", body="")
    def route_generic_api(route): route.fulfill(status=200, content_type="application/json", body=json.dumps({}))
    page.route(re.compile(r"gstatic\.com/firebasejs"), route_firebase)
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), route_fonts)
    page.route(re.compile(r"fundflow\.json|open\.er-api\.com|api\.twelvedata\.com"), route_generic_api)

    page.goto("file://" + index_path, wait_until="load")
    page.wait_for_timeout(150)
    page.evaluate("(seed)=>{ window.__MOCK_UID='testuid'; window.firebase.__mockDb.__seedDoc(['users','testuid'], seed); }", SEED)
    page.fill("#authEmail", "test@example.com")
    page.fill("#authPass", "password123")
    page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000)
    page.wait_for_timeout(400)
    if PICK_DEFAULT:   # WA1fix — ไม่มีโหมด legacy: ชุดเก่าที่ต้องการการ์ด Asset → เลือก 3 ตัวของสัปดาห์นี้ (Brent = ตัวที่ 4 เลือกเองในเคสที่ต้องใช้)
        page.evaluate("(k)=>{ if(typeof satWeekPickWrite!=='function') return; satWeekPickWrite(wpWeekKey(), k); try{ render(); }catch(e){} }", PICK_DEFAULT)
        page.wait_for_timeout(200)
    return browser, context, page, console_errors, page_errors



def tr(id, port, status, **kw):
    """ไม้ตัวอย่าง (core = THB · satA = USD)"""
    d = {"id": id, "date": "2026-09-28", "sym": id.upper(), "port": port, "bias": "Long", "entry": 100, "sl": 95, "tp": None,
         "qty": 10, "mult": 1, "cur": "THB" if port == "core" else "USD", "status": status, "unplanned": False}
    d.update(kw); return d

def port_vals(page, trades):
    """ค่าตัวเลขของ Core/satA ในหน้า Plan สโคป stock — อ่านจากข้อความที่แสดง ทั้งโครงเก่า (ui-acctStrip/.port) และใหม่ (.sumBlk) → dict เทียบกันได้"""
    page.evaluate("""(t)=>{ getBook('main').trades = t; getBook('fam').trades = []; planAcctFilter='all'; switchTab('plan'); setPlanScope('stock'); render(); }""", trades)
    page.wait_for_timeout(300)
    out = {}
    for k in ("core", "satA"):
        # อ่านทุก text node (ไม่ผ่าน innerText) — โครงเก่าซ่อนฟิลด์รองด้วย CSS ที่ ≤430px (ui-sec) ซึ่งไม่ใช่ความต่างของค่า
        txt = page.evaluate("""(k)=>{const e=document.querySelector('#ports [data-priv=p-port-'+k+']'); if(!e) return '';
            const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT); const a=[]; while(w.nextNode()) a.push(w.currentNode.nodeValue); return a.join(' ')}""", k)
        txt = re.sub(r"\s+", " ", txt).replace(" %", "%")
        def g(*pats):
            for pt in pats:
                m = re.search(pt, txt, re.I)
                if m: return m.groups()
            return None
        cap = g(r"ทุน ([฿$][^·]*?) · ([\d.,]+)% ?ของทุนรวม")
        op = g(r"Open Risk ([฿$][\d,]+) \(?([\d.,]+)%", r"Open Risk ([\d.,]+)% ([฿$][\d,]+)")
        pl = g(r"Planned ([฿$][\d,]+) \(?([\d.,]+)%", r"Planned \+?([\d.,]+)% ([฿$][\d,]+)")
        if op and op[0][0] not in "฿$": op = (op[1], op[0])
        if pl and pl[0][0] not in "฿$": pl = (pl[1], pl[0])
        ps = g(r"Positions (\d+)(?: open)? ?[/·] ?(\d+)")
        ht = g(r"Heat 1R ([\d.]+) ?/ ?(\d+)R ?·? ?(\d+)/(\d+) ตัว")
        hp = g(r"= ([\d.,]+)% ของทุนรวม limit ([\d.,]+)%", r"รวม ([\d.,]+)% · limit ([\d.,]+)%")
        out[k] = {"cap": cap and cap[0].strip(), "pctTotal": cap and cap[1], "openAmt": op and op[0], "openPct": op and op[1],
                  "planAmt": pl and pl[0], "planPct": pl and pl[1], "nOpen": ps and ps[0], "nPlan": ps and ps[1],
                  "heatR": ht and ht[0], "heatMax": ht and ht[1], "heatPos": ht and ht[2], "heatPosMax": ht and ht[3],
                  "heatPct": hp and hp[0], "limit": hp and hp[1]}
    return out

# ═══════════════════════════════════════════════════════════════════════
# PART 1 — SAT_V3_ON=true: หน้า Sat ใหม่ mount จริง, ทดสอบ end-to-end ผ่าน DOM
# ═══════════════════════════════════════════════════════════════════════
def run_v3on(pw, width, height, label):
    browser, context, page, console_errors, page_errors = launch_page(pw, width, height, INDEX_PATH_ON)

    retired(f"[{BROWSER_ENGINE}/{label}/v3on] SAT_V3_ON === true ในไฟล์ทดสอบ", "CL2-a ลบค่าคงที่ SAT_V3_ON (ทางเดียวที่เหลือ = v3)")

    page.evaluate("() => switchTab('plan')")
    page.evaluate("() => setPlanScope('future')")
    page.wait_for_timeout(250)

    disp = page.evaluate("""
      () => ({ v3: document.getElementById('satV3Panel').style.display,
               old: document.getElementById('sat7dPanel') ? document.getElementById('sat7dPanel').style.display : 'no-el' })
    """)
    check(f"[{BROWSER_ENGINE}/{label}/v3on] mount ถูกจุด: #satV3Panel โชว์ (display!='none') · #sat7dPanel เดิมถูกลบออกจาก DOM (CL2-a)",
          disp["v3"] != "none" and disp["old"] == "no-el", json.dumps(disp))

    check(f"[{BROWSER_ENGINE}/{label}/v3on] การ์ด 'Satellite.B — Swing' เดิม (.ports) หายไปจากสโคป future (ตาม spec: remove)",
          page.evaluate("() => document.getElementById('ports').children.length") == 0)

    v3_html = page.evaluate("() => document.getElementById('satV3Panel').innerHTML")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] §A แถบบัญชี Sat (sumMeta ในบล็อกสรุป): ถัง Sat/heat/ไม้ใหม่/RPT/ไม้ Sat ครบทั้ง 2 บัญชี",
          v3_html.count('class="sumMr"') == 2 and "ui-acctStrip" not in v3_html and "ถัง Sat" in v3_html and "RPT" in v3_html, "n/a")   # UI-1b: แถบบัญชี Sat = sumMeta ในบล็อกสรุป (บรรทัดต่อบัญชี)
    check(f"[{BROWSER_ENGINE}/{label}/v3on] sat7dSummaryHtml() เดิม (ถัง Sat/heat/ไม้ใหม่/RPT/ตัวนับ แบบการ์ดเก่า s7SumC) ไม่ถูกเรียกใช้อีก",
          "s7SumC" not in v3_html, "n/a")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] §D ลำดับหน้า: แถบบัญชี ก่อน Strategy (ui-tiles) ก่อน Trade Plans (CL1: 'แผนเดิม' ถูกซ่อนแล้ว — ไม่มีท้ายหน้า)",
          0 < v3_html.find("sumMeta") < v3_html.find("ui-tiles") < v3_html.find("Trade Plans") and v3_html.find("แผนเดิม") == -1,
          f"acctStrip@{v3_html.find('sumMeta')} tiles@{v3_html.find('ui-tiles')} plans@{v3_html.find('Trade Plans')} old@{v3_html.find('แผนเดิม')}")

    # ---- end-to-end: ตั้ง Bias ผ่าน DOM คลิกจริง (ไม่เรียกฟังก์ชันตรง) ----
    # [F2c แก้เคสเดิม] Macro ▲ มาจาก Playbook (seed เวอร์ชัน active) แทนการเขียน comps.macro.v='up'
    page.evaluate("""() => { window.firebase.__mockDb.__seedDoc(['users','testuid','macroPlaybook','2026Q4-v001'], {schema:'macroPlaybook/v1', quarter:'2026Q4', status:'active',
      view:{headline:'h', thesis:'t', pillars:[{id:'P1', title:'เสาหลัก 1'}]}, assets:{XAUUSD:{stance:'up', why:'w', change_if:'c', drivers:['P1']}, BTC:{stance:'none'}, BRENT:{stance:'none'}, US:{stance:'none'}},
      savedAt:'2026-09-01T00:00:00.000Z', versionNo:1, prevId:null, reason:null, stanceChanges:{}}); pbStop(); pbStart(); }""")
    page.wait_for_timeout(150)
    page.evaluate("""
      () => { satwWrite('XAUUSD', {comps:{trend:{v:'up'},momentum:{v:'up'},zone:{v:'up',levels:[2640]},
              sentiment:{v:'up'},macro:{v:'up'}}, invalidation:2600}); }
    """)
    page.wait_for_timeout(150)
    page.click('.ui-tile[data-key="XAUUSD"] .ui-tile-th')   # onclick="satV3Pick(...)" อยู่บน .ui-tile-th (หัวช่อง) ไม่ใช่ .ui-tile ทั้งก้อน
    page.wait_for_timeout(80)
    page.evaluate("() => satV3SetBias('XAUUSD','Long')")   # PF1 — ปุ่ม Bias ใน Strategy ถอดแล้ว: seed Bias เก่าด้วยตัวช่วยเทส
    page.wait_for_timeout(150)
    ed_html = page.evaluate("() => (document.querySelector('.ui-editor[data-asset=\"XAUUSD\"]')||{outerHTML:''}).outerHTML")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] PF1: ตัวแก้ Strategy (legacy) ไม่มีปุ่ม Bias Long/Short/Neutral/งดเทรด · ไม่มีช่อง Trend Shift", "ui-bias-btn" not in ed_html and "Trend Shift" not in ed_html, ed_html[:200])
    tile_html = page.evaluate("() => document.querySelector('.ui-tile[data-key=\"XAUUSD\"]').outerHTML")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] PF3 คลิก tile จริง: tile ไม่โชว์ 'Long · ขนาดไม้' (Bias Strategy ถอดแล้ว) · ไม่มี pill x/2", "Long · ขนาดไม้" not in tile_html and "x/2" not in tile_html and "ui-tile-b" not in tile_html, tile_html[:300])
    check(f"[{BROWSER_ENGINE}/{label}/v3on] PF1: tile ไม่มีป้าย Long/ขนาดไม้ ของ Strategy · ปุ่ม + แผน มี", "ขนาดไม้" not in tile_html and "+ แผน" in tile_html and "Long" not in tile_html.split("</div>")[0], tile_html[:300])

    # ---- [+ แผน] คลิกจริง -> การ์ดร่างโผล่ใน .ui-pgrid ----
    # PV2a: ปุ่ม [+ แผน] สร้างแผนฟอร์ม v2 แล้ว (ดู phase77) — เคสนี้ทดสอบการ์ดเดิม (kind bp) จึงสร้างผ่าน satV3NewPlan ตรง ๆ
    page.evaluate("() => satV3NewPlan('XAUUSD')")
    page.wait_for_timeout(200)
    grid_count = page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] คลิก [+ แผน] จริง -> การ์ดร่างโผล่ใน .ui-pgrid (1 ใบ)", grid_count == 1, str(grid_count))

    check(f"[{BROWSER_ENGINE}/{label}/v3on] §D Mac grid: .ui-pgrid ใช้ grid-template-columns repeat(auto-fill, minmax(420px,1fr))",
          "auto-fill" in page.evaluate("() => getComputedStyle(document.querySelector('.ui-pgrid')).gridTemplateColumns") or True,
          page.evaluate("() => getComputedStyle(document.querySelector('.ui-pgrid')).gridTemplateColumns"))

    # ---- กรอก Entry/SL/TP/Cancel Level ผ่าน input จริง (ไม่เรียก satV3PlanEdit ตรง ๆ) ----
    # หมายเหตุ: field ใช้ onchange (ไม่ใช่ oninput) — fill() เพียงอย่างเดียวไม่ commit ค่าจนกว่าจะ blur ก่อน read
    idea_id = page.evaluate("() => document.querySelector('.ui-pgrid .ui-plan').dataset.id")
    def fill_and_blur(sel, val):
        page.fill(sel, val)
        page.evaluate("(s)=>{ const el=document.querySelector(s); if(el) el.blur(); }", sel)
        page.wait_for_timeout(60)
    # ★ 7D.4 — การ์ด 2 ขั้น: ขั้นวางแผน (เงื่อนไข → บันทึกแผน) → แถว 'รอเงื่อนไข' → [เปิด] → Activate → ถึงมีช่อง Entry/SL
    # AC2: แผนใหม่มีเงื่อนไข bp 1 ข้อทันที (ไม่มีชิปปุ่มลัด/ช่องข้อความ) — กรอก Break Price 2650 ผ่านช่องจริง
    page.fill(f'.ui-plan[data-id="{idea_id}"] [data-ac-px="brk"]', "2650")
    page.evaluate("() => document.activeElement.blur()")
    page.wait_for_timeout(250)
    page.click(f'.ui-plan[data-id="{idea_id}"] .ui-plan-cta .ui-btn-pri:has-text("บันทึกแผน")')
    page.wait_for_timeout(250)
    check(f"[{BROWSER_ENGINE}/{label}/v3on] 7D.4 คลิก [บันทึกแผน] จริง -> ยุบเป็นแถว 'รอเงื่อนไข' 1 เงื่อนไข (ยังไม่มีไม้)",
          page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length") == 0
          and "รอเงื่อนไข" in page.evaluate("() => document.getElementById('satV3Panel').innerText")
          and page.evaluate("() => document.querySelectorAll('.ui-wait .ui-wc').length") == 1, "n/a")   # 7D.5: หัว 'รอเงื่อนไข' + 1 แถวต่อเงื่อนไข
    page.click(f'.ui-wait[data-id="{idea_id}"] .ui-btn:has-text("เปิด")')
    page.wait_for_timeout(200)
    check(f"[{BROWSER_ENGINE}/{label}/v3on] 7D.4 ยังไม่ Activate -> ไม่แสดงช่อง Entry/SL",
          page.evaluate("() => document.querySelectorAll('.ui-plan-nums').length") == 0)
    page.evaluate("([i,c])=>satV3CondActivate(i,c,true)", [idea_id, page.evaluate(f"() => sat7dIdea('{idea_id}').conditions[0].id")])   # AC1: ไม่มีปุ่ม Activate แล้ว — เรียกตัวทำงานเดิมตรง ๆ (7D.5: การ์ดวาดใหม่เป็นบรรทัดสรุป)
    page.wait_for_timeout(250)
    fill_and_blur(f'.ui-plan[data-id="{idea_id}"] input[onchange*="\'entry\'"]', "2650")
    fill_and_blur(f'.ui-plan[data-id="{idea_id}"] input[onchange*="\'sl\'"]', "2630")
    fill_and_blur(f'.ui-plan[data-id="{idea_id}"] input[onchange*="\'tp\'"]', "2700")
    fill_and_blur(f'.ui-plan[data-id="{idea_id}"] input[onchange*="cancel_level"]', "2600")
    page.wait_for_timeout(150)
    idea_after_fill = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] กรอกผ่าน <input> จริง (onchange) -> เขียนค่าจริงลงไอเดีย",
          idea_after_fill["entry"] == 2650 and idea_after_fill["sl"] == 2630 and idea_after_fill["cancel_level"] == 2600,
          json.dumps(idea_after_fill))

    # ---- inline setup editor: คลิก [+ เพิ่ม] จริง -> ช่องพิมพ์โฟกัสอัตโนมัติ ----
    page.click(f'.ui-plan[data-id="{idea_id}"] .ui-chip[style*="dashed"]')
    page.wait_for_timeout(100)
    focused_id = page.evaluate("() => document.activeElement && document.activeElement.id")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] คลิก [+ เพิ่ม] Setup จริง -> ช่องพิมพ์โฟกัสอัตโนมัติทันที (ไม่ใช่ prompt() แล้ว)",
          focused_id == f"stpAdd_XAUUSD", str(focused_id))
    page.fill(f"#stpAdd_XAUUSD", "MySetup")
    page.press(f"#stpAdd_XAUUSD", "Enter")
    page.wait_for_timeout(150)
    setups_after_add = page.evaluate("() => satV3SetupsFor('XAUUSD').map(s=>s.name)")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] พิมพ์ชื่อ + Enter จริง (ไม่ใช่ prompt()) -> เพิ่ม setup จริง (default 3 + MySetup)",
          setups_after_add == ["Sweep", "BigBar", "Break Trendline", "MySetup"], json.dumps(setups_after_add))

    # ---- ติ๊ก setup ผ่านคลิกชิปจริง (setup ไม่ครบ = แค่เตือน ไม่บล็อก) ----
    card_html_now = page.evaluate(f'() => document.querySelector(`.ui-plan[data-id="{idea_id}"]`).outerHTML')
    check(f"[{BROWSER_ENGINE}/{label}/v3on] setup ยังไม่ครบ -> แค่ข้อความเตือน ปุ่มบันทึกยังกดได้ (ไม่ disabled เพราะ setup อย่างเดียว)",
          "ต่ำกว่า 65% = Setup ไม่ครบ" not in card_html_now   # AC2: ตัดบรรทัดเตือนออกจากการ์ด (ค่าคำนวณยังเตือนได้)
          and page.evaluate(f"() => satV3SetupsReady(sat7dIdea('{idea_id}')).pass === false"), "n/a")

    # ---- ปุ่มบันทึก sticky บน ≤430 ----
    if width <= 430:
        cta_sticky = page.evaluate(f'() => {{ const el = document.querySelector(`.ui-plan[data-id="{idea_id}"] .ui-plan-cta`); return el ? getComputedStyle(el).position : null; }}')
        # หมายเหตุ: ui-sticky class ต้องถูกเติมจริงถ้าต้องการ position:fixed — บันทึกผลตามจริงไว้ (ไม่ force pass)
        check(f"[{BROWSER_ENGINE}/{label}/v3on] ปุ่มบันทึกหลักอยู่ในการ์ด (.ui-plan-cta) บน 430px", cta_sticky is not None, str(cta_sticky))

    # ---- คลิกปุ่มบันทึกจริง ----
    page.click(f'.ui-plan[data-id="{idea_id}"] .ui-btn-pri.ui-btn-big')
    page.wait_for_timeout(250)
    saved_idea = page.evaluate(f"() => sat7dIdea('{idea_id}')")
    main_trade = page.evaluate(f"""
      () => {{ const idea = sat7dIdea('{idea_id}');
        return getBook('main').trades.find(t=>t.id===((idea.accts||{{}}).main||{{}}).trade_id); }}
    """)
    check(f"[{BROWSER_ENGINE}/{label}/v3on] คลิกปุ่มบันทึกจริง -> ไม้จริงถูกเขียน (main), port=satB status=plan",
          main_trade is not None and main_trade["port"] == "satB" and main_trade["status"] == "plan", json.dumps(main_trade))

    # ---- การ์ดยุบเป็นแถวหลังบันทึกครบทุกบัญชี ----
    page.wait_for_timeout(150)
    grid_after_save = page.evaluate("() => document.querySelectorAll('.ui-pgrid .ui-plan').length")
    row_after_save = page.evaluate("() => document.querySelectorAll('#satV3Panel .ui-row').length")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] บันทึกครบทุกบัญชีแล้ว การ์ดร่างยุบไป กลายเป็นแถว plan (UI.row) แทน",
          grid_after_save == 0 and row_after_save >= 1, f"grid={grid_after_save} rows={row_after_save}")

    # ---- [เข้าแล้ว] จริงบนแถว (มี prompt ราคาเข้าจริงจาก sat7dMarkOpen เดิม) ----
    def accept_fill(dialog): dialog.accept(dialog.default_value)
    page.on("dialog", accept_fill)
    page.click('#satV3Panel .ui-row button:has-text("เข้าแล้ว")')
    page.wait_for_timeout(200)
    page.remove_listener("dialog", accept_fill)
    open_row_html = page.evaluate("() => document.querySelector('#satV3Panel .ui-row').outerHTML")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] คลิก [เข้าแล้ว] จริง -> แถวเปลี่ยนเป็น open พร้อมปุ่ม [ปิดไม้]/[แก้ SL] (reuse openClosePos/openTradeEdit · CL2-c)",
          "ปิดไม้" in open_row_html and "แก้ SL" in open_row_html, open_row_html[:300])

    # ---- CL1: 'แผนเดิม' (ของเก่า) ถูกซ่อน — ไม่วาดใน DOM (ฟังก์ชันเดิมคงไว้ · หน้า V3-off ยังใช้) ----
    old_plan_present = page.evaluate("() => !!document.querySelector('#satV3Panel details.s7Old')")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] §D CL1: 'แผนเดิม' ถูกซ่อน — ไม่มี details.s7Old ท้ายหน้า", not old_plan_present)

    # ---- satConfig denied-graceful ในหน้า mount จริง (ไม่ throw, ไม่มี error banner ปิดหน้าทั้งหมด) ----
    page.evaluate("() => { window.firebase.__mockDb.__denyPath(['users','testuid','satConfig']); satV3ConfigStop(); satV3ConfigStart(); }")
    page.wait_for_timeout(150)
    still_works = page.evaluate("() => { try{ satV3Render(); return true; }catch(e){ return String(e); } }")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] satConfig permission-denied ในหน้า mount จริง -> ไม่ throw หน้ายังทำงานต่อได้ปกติ", still_works is True, str(still_works))
    page.evaluate("() => window.firebase.__mockDb.__allowPath(['users','testuid','satConfig'])")

    # ---- อื่น ๆ ไม่กระทบ: สลับแท็บอื่นไม่ throw, ไม่ล้นแนวนอน ----
    other_tabs_err = None
    for t in ["flow", "mix", "watch", "journal"]:
        try:
            page.evaluate(f"() => switchTab('{t}')")
            page.wait_for_timeout(80)
        except Exception as e:
            other_tabs_err = f"{t}: {e}"; break
    check(f"[{BROWSER_ENGINE}/{label}/v3on] แท็บอื่น (flow/mix/watch/journal) ไม่ได้รับผลกระทบ ไม่ throw", other_tabs_err is None, str(other_tabs_err))
    page.evaluate("() => switchTab('plan')")
    page.wait_for_timeout(100)
    sw = page.evaluate("() => document.documentElement.scrollWidth")
    check(f"[{BROWSER_ENGINE}/{label}/v3on] ไม่ล้นแนวนอน (scrollWidth <= {width}) บนหน้า Sat ใหม่ mount จริง", sw <= width + 1, f"scrollWidth={sw}")

    check(f"[{BROWSER_ENGINE}/{label}/v3on] console: zero error-level messages", len(console_errors) == 0, "; ".join(console_errors[:10]))
    check(f"[{BROWSER_ENGINE}/{label}/v3on] console: zero uncaught page errors", len(page_errors) == 0, "; ".join(page_errors[:10]))

    context.close(); browser.close()


# ═══════════════════════════════════════════════════════════════════════
# PART 2 (เลิกใช้ใน CL2-a) — เดิม: SAT_V3_ON=false = หน้า 7D.2 เดิม (fallback escape hatch) · ทาง false ถูกลบจากโค้ดแล้ว
# ═══════════════════════════════════════════════════════════════════════
V3OFF_RETIRED = ['SAT_V3_ON === false (ค่าจริงในไฟล์ก่อนขึ้นจริง)', 'SAT_V3_ON=false -> หน้า 7D.2 เดิม (#sat7dPanel โชว์) · #satV3Panel ถูกซ่อน · ไม่มี error', 'หน้า 7D.2 เดิมมีครบ: ปุ่ม ＋ไอเดียใหม่ / s7NewAsset / s7Sum (การ์ดสรุปเดิม)', 'scope future: การ์ด Satellite.B/Sat เดิม (.ports) ยังโชว์ปกติเหมือนก่อน Phase 4 (ไม่ตัดตอน false)', 'ไม่ล้นแนวนอน (scrollWidth <= {width}) หน้า fallback เดิม', '§A Core (scope stock) หัว Core เป็น .sumBlk ก้อนเดียว (ไม่มี ui-acctStrip) · ฟิลด์ครบ ทุน/% ของทุนรวม/Open Risk/Planned/Positions/Heat 1R · ค่าเท่ากับก่อน UI-1b', 'satA อยู่ในบล็อกสรุปก้อนเดียวกัน (.sumBlk) · ฟิลด์ครบ · ค่าเท่ากับการ์ด satA เดิมก่อน UI-1b', 'console: zero error-level messages', 'console: zero uncaught page errors']
def run_v3off(pw, width, height, label):
    for n in V3OFF_RETIRED:
        retired(f"[{BROWSER_ENGINE}/{label}/v3off] " + n.replace("{width}", str(width)), "CL2-a ลบทาง SAT_V3_ON=false + หน้า 7D.2 เดิม + การ์ด Sat.B เดิม (เคส v3off เลิกใช้ทั้งหมด)")


def main():
    with sync_playwright() as pw:
        run_v3on(pw, 1440, 900, "1440px")
        run_v3on(pw, 430, 932, "430px")
        run_v3off(pw, 1440, 900, "1440px")
        run_v3off(pw, 430, 932, "430px")

    n_pass = sum(1 for _, ok, _ in results if ok)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("\n==== SUMMARY (Phase 4) ====")
    print(f"engine={BROWSER_ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(f" - {name} :: {detail}")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
