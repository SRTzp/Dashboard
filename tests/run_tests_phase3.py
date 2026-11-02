#!/usr/bin/env python3
"""7D.3 Phase 3 — Trade Plan card (UI.planCard + adapter Sat, ส่วนที่ 1 ช่อง C, namespace satV3 ต่อ).
รันแยกจาก run_tests.py/run_tests_phase1.py/run_tests_phase2.py — ไม่ลบ/แก้เคสเดิม เพิ่มเคสใหม่ของรอบนี้เท่านั้น
satV3* ยังไม่ถูก mount เข้าหน้าไหนจริง (SAT_V3_ON=false) — เทสรอบนี้เรียกฟังก์ชันตรง ๆ (ทดสอบแยกได้)
ครอบคลุม: satConfig graceful degradation, setup add/rename/remove แยกตามสินค้า, satV3NewPlan (สร้าง/ไม่ซ้ำ),
คำนวณต่อบัญชี (lot/R-multiple), setup ไม่ครบ = เตือนอย่างเดียว (นอกแผน), บันทึก order (makeTradeObject จริง,
cancel_level/setups ติดไปด้วย), ปุ่มเดียว "บันทึกทุกบัญชีที่พร้อม", "รวมด้วย (นอกแผน)", ✕ ลบร่างไม่แตะสมุด,
และ ★ CRITICAL FIX: plan/open row ต้องอ่านจากไม้ในสมุดจริง ไม่ใช่ idea.status — ไอเดียปิดเองเฉพาะเมื่อข้ามหมด/ปิดหมด

รันได้ทั้ง Chromium และ WebKit:
  python3 run_tests_phase3.py
  BROWSER=webkit python3 run_tests_phase3.py
"""
import json, os, sys, re
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INDEX = os.path.abspath(os.path.join(HERE, "..", "index.html"))
INDEX_PATH = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("INDEX_HTML", DEFAULT_INDEX)
APP_URL = "file://" + INDEX_PATH
_default_chromium = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROMIUM_PATH = os.environ.get("CHROMIUM_PATH") or (_default_chromium if os.path.exists(_default_chromium) else None)
BROWSER_ENGINE = os.environ.get("BROWSER", "chromium")
MOCK_FB = open(os.path.join(HERE, "mock-firebase.js"), encoding="utf-8").read()
SEED = json.load(open(os.path.join(HERE, "seed.json"), encoding="utf-8"))

# 7D.4 — ไอเดียแบบเก่า (v3:true แต่ไม่มี conditions) เหมือน satV3NewPlan ก่อน 7D.4 ทุกประการ (เติม Entry ถ้ามีแนวรับ 1 ค่า)
LEGACY_JS = """(asset)=>{ const wk = satwWeek(wpWeekKey(), asset); const bias = wk.bias;
  const sup = satV3SupportDisplay(wk), res = satV3ResistanceDisplay(wk); const zones = bias==='Long' ? sup.values : res.values;
  const id = 'iL' + Date.now() + Math.floor(Math.random()*1000);
  sat7dWrite('satIdeas', id, {v3:true, asset, bias, week:wpWeekKey(), created_at:new Date().toISOString(),
    entry: zones.length===1 ? zones[0] : null, sl:null, tp:null, cancel_level:null, setups:[], status:'active', accts:{}});
  return id; }"""

results = []

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))

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
    def route_generic_api(route):
        route.fulfill(status=200, content_type="application/json", body=json.dumps({}))

    page.route(re.compile(r"gstatic\.com/firebasejs"), route_firebase)
    page.route(re.compile(r"fonts\.(googleapis|gstatic)\.com"), route_fonts)
    page.route(re.compile(r"fundflow\.json"), route_generic_api)
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

    page.evaluate("() => { try{ sat7dStart(); }catch(e){} }")
    page.wait_for_timeout(200)
    page.evaluate("() => { satWeekPickWrite(wpWeekKey(), ['XAUUSD','BTCUSD','S50']); }")   # WA1fix — ไม่มีโหมด legacy: เลือก Asset สัปดาห์นี้ก่อนมีแผน/คำนวณ

    # ═══════════ satConfig: graceful degradation ═══════════

    # 1) no satConfig doc at all (never written) -> satV3ConfigStart() must not throw, falls back to 3 defaults
    page.evaluate("() => { try{ satV3ConfigStart(); }catch(e){ window.__cfgThrew = String(e); } }")
    page.wait_for_timeout(80)
    cfg0 = page.evaluate("() => ({threw: window.__cfgThrew || null, setups: satV3SetupsFor('XAUUSD'), err: satConfigErr})")
    check(f"[{BROWSER_ENGINE}/{label}] satConfig: ไม่มีเอกสารเลย -> ไม่ throw ใช้ default 3 รายการ (Sweep/BigBar/Break Trendline)",
          cfg0["threw"] is None and [s["name"] for s in cfg0["setups"]] == ["Sweep", "BigBar", "Break Trendline"] and cfg0["err"] is None,
          json.dumps(cfg0))

    # 2) deny the satConfig path entirely (simulates rules-not-deployed permission-denied) -> still no throw, still defaults
    page.evaluate("() => satV3ConfigStop()")
    page.evaluate("() => { window.firebase.__mockDb.__denyPath(['users','testuid','satConfig']); }")
    page.evaluate("() => { try{ satV3ConfigStart(); }catch(e){ window.__cfgThrew2 = String(e); } }")
    page.wait_for_timeout(80)
    cfg_denied = page.evaluate("() => ({threw: window.__cfgThrew2 || null, setups: satV3SetupsFor('S50'), err: satConfigErr})")
    check(f"[{BROWSER_ENGINE}/{label}] satConfig: permission-denied (rules ยังไม่ deploy) -> ไม่ throw ใช้ default ต่อได้ทันที + ตั้ง satConfigErr ไว้เตือน",
          cfg_denied["threw"] is None and [s["name"] for s in cfg_denied["setups"]] == ["Sweep", "BigBar", "Break Trendline"]
          and cfg_denied["err"], json.dumps(cfg_denied))
    check(f"[{BROWSER_ENGINE}/{label}] console: satConfig denial ไม่ทำให้เกิด uncaught error (แค่ console.warn)",
          not any("permission-denied" in e and "Uncaught" in e for e in page_errors), "n/a")

    page.evaluate("() => { satV3ConfigStop(); window.firebase.__mockDb.__allowPath(['users','testuid','satConfig']); }")
    page.evaluate("() => { try{ satV3ConfigStart(); }catch(e){} }")
    page.wait_for_timeout(80)

    # 3) custom setups written for one asset -> satV3SetupsFor reads them back correctly, per-asset isolated
    page.evaluate("() => satV3SetupAdd('XAUUSD', 'Custom A')")
    page.wait_for_timeout(60)
    after_add = page.evaluate("() => ({xau: satV3SetupsFor('XAUUSD'), s50: satV3SetupsFor('S50')})")
    check(f"[{BROWSER_ENGINE}/{label}] satV3SetupAdd: XAUUSD ได้ setup ใหม่ 4 รายการ (default 3 + Custom A)",
          len(after_add["xau"]) == 4 and after_add["xau"][-1]["name"] == "Custom A", json.dumps(after_add["xau"]))
    check(f"[{BROWSER_ENGINE}/{label}] satV3SetupAdd: S50 ไม่ถูกแตะต้อง ยังเป็น default 3 รายการเหมือนเดิม (แยกตามสินค้า)",
          [s["name"] for s in after_add["s50"]] == ["Sweep", "BigBar", "Break Trendline"], json.dumps(after_add["s50"]))

    custom_id = after_add["xau"][-1]["id"]
    page.evaluate(f"() => satV3SetupRename('XAUUSD', '{custom_id}', 'Custom A แก้ชื่อ')")
    page.wait_for_timeout(60)
    after_rename = page.evaluate("() => satV3SetupsFor('XAUUSD')")
    check(f"[{BROWSER_ENGINE}/{label}] satV3SetupRename: ชื่อถูกแก้ (id เดิม)",
          any(s["id"] == custom_id and s["name"] == "Custom A แก้ชื่อ" for s in after_rename), json.dumps(after_rename))

    page.evaluate(f"() => satV3SetupRemove('XAUUSD', '{custom_id}')")
    page.wait_for_timeout(60)
    after_remove = page.evaluate("() => satV3SetupsFor('XAUUSD')")
    check(f"[{BROWSER_ENGINE}/{label}] satV3SetupRemove: กลับไปเหลือ default 3 รายการ",
          [s["name"] for s in after_remove] == ["Sweep", "BigBar", "Break Trendline"], json.dumps(after_remove))

    # ═══════════ satV3NewPlan: create + no-duplicate ═══════════

    # need a Long bias on XAUUSD this week with entry-fillable support zone, matching Phase 2's satV3SetBias flow
    page.evaluate("""
      () => {
        satwWrite('XAUUSD', {comps:{trend:{v:'up'},momentum:{v:'up'},zone:{v:'up',levels:[2640]},sentiment:{v:'up'},macro:{v:'up'}}, invalidation:2600});
        satV3SetBias('XAUUSD','Long');
      }
    """)
    page.wait_for_timeout(60)

    page.evaluate("() => satV3NewPlan('XAUUSD')")
    page.wait_for_timeout(200)
    plan1 = page.evaluate("""
      () => { const d = satIdeasList.find(x=>x.v3 && x.asset==='XAUUSD' && x.status!=='closed'); return d || null; }
    """)
    check(f"[{BROWSER_ENGINE}/{label}] satV3NewPlan: สร้างไอเดียใหม่ v3:true asset=XAUUSD bias=Long จาก Bias ของ Strategy สัปดาห์นี้",
          plan1 is not None and plan1.get("bias") == "Long" and plan1.get("v3") is True, json.dumps(plan1))

    page.evaluate("() => satV3NewPlan('XAUUSD')")  # click [+ แผน] again while a draft still exists
    page.wait_for_timeout(150)
    plans_after_2nd_click = page.evaluate("""
      () => satIdeasList.filter(x=>x.v3 && x.asset==='XAUUSD' && x.status!=='closed').length
    """)
    check(f"[{BROWSER_ENGINE}/{label}] satV3NewPlan: กดซ้ำขณะยังมีร่างของ XAUUSD อยู่ -> ไม่สร้างซ้ำ (ยังมีแค่ 1 ไอเดีย)",
          plans_after_2nd_click == 1, str(plans_after_2nd_click))

    # ★ 7D.4: [+ แผน] สร้างไอเดียแบบการ์ด 2 ขั้น (conditions) แล้ว — เคสด้านล่างนี้ทดสอบการ์ด 'แบบเดิม' (ไอเดียเก่าที่ไม่มี conditions
    #   ต้องแสดงแบบเดิมและใช้งานต่อได้ตามสเปก 7D.4 ข้อ B6) จึงลบร่างใหม่แล้วสร้างไอเดียแบบเก่า (ไม่มี conditions) แทน
    #   ส่วนเคสการ์ด 2 ขั้นดู run_tests_phase5.py
    page.evaluate(f"() => satV3IdeaDelete('{plan1['id']}')")
    page.wait_for_timeout(120)
    plan_id = page.evaluate(LEGACY_JS, "XAUUSD")
    page.wait_for_timeout(200)

    # ═══════════ draft card: price chips / entry / R-multiple / incomplete-setup warning ═══════════

    page.evaluate(f"() => satV3PlanEdit('{plan_id}','entry','2650')")
    page.evaluate(f"() => satV3PlanEdit('{plan_id}','sl','2630')")
    page.evaluate(f"() => satV3PlanEdit('{plan_id}','tp','2700')")
    page.evaluate(f"() => satV3PlanEdit('{plan_id}','cancel_level','2600')")
    page.wait_for_timeout(80)
    idea1 = page.evaluate(f"() => sat7dIdea('{plan_id}')")
    check(f"[{BROWSER_ENGINE}/{label}] satV3PlanEdit: entry/sl/tp/cancel_level เขียนเป็นตัวเลขจริง",
          idea1["entry"] == 2650 and idea1["sl"] == 2630 and idea1["tp"] == 2700 and idea1["cancel_level"] == 2600, json.dumps(idea1))

    card_html = page.evaluate(f"() => satV3DraftCardHtml(sat7dIdea('{plan_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] การ์ดร่าง: มี priceChips จากแนวรับ (2640) ให้แตะเติม Entry",
          '2640' in card_html and f"satV3PlanEdit('{plan_id}','entry','2640')" in card_html, card_html[:300])
    check(f"[{BROWSER_ENGINE}/{label}] การ์ดร่าง: R-multiple คำนวณถูก (TP2700-Entry2650)/(Entry2650-SL2630) = 2.5R",
          "2.5R" in card_html, card_html[card_html.find("ui-rr"):card_html.find("ui-rr")+60])
    check(f"[{BROWSER_ENGINE}/{label}] การ์ดร่าง: setup 0/3 ต่ำกว่า 65% -> ไม่แสดงบรรทัดเตือนในการ์ด (AC2) · ค่าคำนวณ satV3SetupsReady ยัง pass:false",
          "Setup 0/3" not in card_html and "ต่ำกว่า 65% = Setup ไม่ครบ" not in card_html   # AC2: ตัดบรรทัดนี้ออกจากการ์ด
          and page.evaluate(f"() => {{ const su = satV3SetupsReady(sat7dIdea('{plan_id}')); return su.n === 0 && su.total === 3 && su.pass === false && satV3SetupLabel(su).includes('Setup 0/3'); }}"), card_html[:400])   # ค่าคำนวณยังคงเดิม

    # ═══════════ per-account calc: lot / R-multiple via satV3PlanAcctCalc, same numbers as §7 canonical case ═══════════

    page.evaluate("() => { const s=getBook('main').settings; s.satRisk={rpt:1.25, rptHi:1.5}; s.satPyrSplit=[100,0,0]; }")   # SR1 — fixture: ค่าเดิม 1.25/1.5 (ตัวเลขคาดหวังเดิมคงไว้) · PY2 — 100/0/0 = ไม้ 1 เข้าเต็ม RPT
    calc_main = page.evaluate(f"() => satV3PlanAcctCalc(sat7dIdea('{plan_id}'), 'main')")
    check(f"[{BROWSER_ENGINE}/{label}] satV3PlanAcctCalc main/XM เท่ากับ sat7dCalc เดิมทุกจุด -> lot 0.15",
          calc_main.get("lot") is not None and abs(calc_main["lot"] - 0.15) < 1e-9, json.dumps(calc_main))

    # ═══════════ save flow: single button, primary account only first, cancel_level/setups carried, port satB ═══════════

    ready_count_before = page.evaluate(f"() => satV3ReadyCount(sat7dIdea('{plan_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] satV3ReadyCount: 2 บัญชี (main/fam) มีโบรกตั้งไว้ครบ -> พร้อมทั้งคู่ (2)",
          ready_count_before == 2, str(ready_count_before))

    page.evaluate(f"() => satV3SaveReadyAccounts('{plan_id}')")
    page.wait_for_timeout(150)
    after_save = page.evaluate(f"""
      () => {{
        const idea = sat7dIdea('{plan_id}');
        const mainTrade = getBook('main').trades.find(t=>t.id===((idea.accts||{{}}).main||{{}}).trade_id);
        const famTrade = getBook('fam').trades.find(t=>t.id===((idea.accts||{{}}).fam||{{}}).trade_id);
        return {{idea, mainTrade, famTrade}};
      }}
    """)
    check(f"[{BROWSER_ENGINE}/{label}] บันทึก order: เขียนไม้จริงทั้ง main และ fam ผ่าน makeTradeObject() (ปุ่มเดียว บันทึกทุกบัญชีที่พร้อม)",
          after_save["mainTrade"] is not None and after_save["famTrade"] is not None, json.dumps(after_save)[:600])
    check(f"[{BROWSER_ENGINE}/{label}] บันทึก order: ไม้ port=satB, status=plan, cancel_level ติดไปด้วย",
          after_save["mainTrade"]["port"] == "satB" and after_save["mainTrade"]["status"] == "plan"
          and after_save["mainTrade"]["cancel_level"] == 2600, json.dumps(after_save["mainTrade"]))
    check(f"[{BROWSER_ENGINE}/{label}] บันทึก order: setups ที่เลือกไว้ (ว่างเพราะยังไม่ติ๊ก) ติดไปกับไม้ด้วย field ใหม่",
          after_save["mainTrade"].get("setups") == [], json.dumps(after_save["mainTrade"]))

    # ★ CRITICAL FIX check #1: right after save (0 setups checked => setup ไม่ครบ = นอกแผน), row must show as 'plan'
    #   immediately — must NOT be hidden/closed just because idea has old-style incomplete-checklist semantics
    row_state_after_save = page.evaluate(f"() => satV3PlanRowState(sat7dIdea('{plan_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] ★ CRITICAL: หลังบันทึก order แล้ว plan row ต้องขึ้นทันที (ไม่ถูกซ่อน/ปิดเอง) แม้ setup ยังไม่ครบ",
          row_state_after_save == "plan", str(row_state_after_save))
    check(f"[{BROWSER_ENGINE}/{label}] บันทึก order: setup ไม่ครบ -> ไม้ Setup ไม่ครบ (setup_incomplete:true · unplanned:false) ตามสเปก SU",
          after_save["mainTrade"].get("setup_incomplete") is True and after_save["mainTrade"].get("unplanned") is False,
          json.dumps(after_save["mainTrade"]))

    # card should have collapsed out of the "draft" section now that both accounts have a trade_id
    plans_html_after_save = page.evaluate("() => satV3PlansSectionHtml()")
    check(f"[{BROWSER_ENGINE}/{label}] การ์ดร่างยุบไปแล้วหลังบันทึกครบทุกบัญชี (ไม่อยู่ในโซนร่างอีกต่อไป), ไปโผล่เป็นแถว plan แทน",
          "เข้าแล้ว" in plans_html_after_save and "ยกเลิก" in plans_html_after_save
          and f'data-id="{plan_id}"' not in plans_html_after_save, plans_html_after_save[:500])

    # ═══════════ mark-open / cancel wired to existing UI.row buttons -> existing openClosePos/editTrade/sat7dMarkOpen/sat7dCancelSlot ═══════════

    row_html = page.evaluate(f"() => satV3PlanRowsHtml(sat7dIdea('{plan_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] แถว plan: ปุ่ม [เข้าแล้ว]/[ยกเลิก] ผูกกับ satV3RowMarkOpenAll/satV3RowCancelAll (ทำทุกบัญชีที่ยัง plan พร้อมกัน)",
          f"satV3RowMarkOpenAll('{plan_id}')" in row_html and f"satV3RowCancelAll('{plan_id}')" in row_html, row_html[:300])

    # cancel fam's plan slot first (still 'plan' at this point, right after save) — leaves only main still 'plan',
    # so satV3RowMarkOpenAll below triggers exactly 1 fill-price prompt (main) and we get a clean open+cancelled mix to test with
    page.evaluate(f"() => sat7dCancelSlot('{plan_id}','fam')")
    page.wait_for_timeout(100)

    # sat7dMarkOpen() (reused as-is) prompts for the real fill price — accept the suggested default so headless run doesn't hang
    def accept_fill_prompt(dialog):
        # dialog.accept() alone submits an EMPTY string for a prompt() (not the browser-shown default value) —
        # must pass default_value explicitly to actually confirm the suggested fill price
        dialog.accept(dialog.default_value)
    page.on("dialog", accept_fill_prompt)
    page.evaluate(f"() => satV3RowMarkOpenAll('{plan_id}')")
    page.wait_for_timeout(150)
    page.remove_listener("dialog", accept_fill_prompt)
    after_open = page.evaluate(f"""
      () => {{
        const idea = sat7dIdea('{plan_id}');
        const mainTrade = getBook('main').trades.find(t=>t.id===((idea.accts||{{}}).main||{{}}).trade_id);
        return {{status: mainTrade.status, rowState: satV3PlanRowState(idea)}};
      }}
    """)
    check(f"[{BROWSER_ENGINE}/{label}] [เข้าแล้ว]: ไม้ในสมุดเปลี่ยนเป็น status=open ผ่าน sat7dMarkOpen เดิม, plan row state -> 'open'",
          after_open["status"] == "open" and after_open["rowState"] == "open", json.dumps(after_open))

    open_row_html = page.evaluate(f"() => satV3PlanRowsHtml(sat7dIdea('{plan_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] แถว open: ปุ่ม [ปิดไม้]/[แก้ SL] ผูกกับ openClosePos/openTradeEdit ตรง ๆ (reuse ไม่สร้างใหม่ · CL2-c: editTrade → openTradeEdit)",
          "openClosePos(" in open_row_html and "openTradeEdit(" in open_row_html, open_row_html[:400])

    # ═══════════ ★ CRITICAL FIX check #2: idea must NOT auto-close just because one account is 'open'
    #   — it only auto-closes when ALL accounts are skipped, or every bound trade is closed/cancelled ═══════════
    idea_after_open = page.evaluate(f"() => sat7dIdea('{plan_id}')")
    check(f"[{BROWSER_ENGINE}/{label}] ★ CRITICAL: idea.status ยังไม่ใช่ 'closed' แค่เพราะไม้เปิดอยู่ 1 บัญชี (ปุ่มปิด/แก้ต้องยังใช้ได้)",
          idea_after_open.get("status") != "closed", json.dumps(idea_after_open))

    # fam is already 'cancelled' (done above, before mark-open) -> now close the main 'open' trade for real -> idea should auto-close
    page.evaluate(f"""
      () => {{
        const idea = sat7dIdea('{plan_id}');
        const mainTrade = getBook('main').trades.find(t=>t.id===((idea.accts||{{}}).main||{{}}).trade_id);
        mainTrade.status = 'closed';
        saveBook('main');
        satV3MaybeAutoClose('{plan_id}');
      }}
    """)
    page.wait_for_timeout(80)
    idea_final = page.evaluate(f"() => sat7dIdea('{plan_id}')")
    row_state_final = page.evaluate(f"() => satV3PlanRowState(sat7dIdea('{plan_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] ★ CRITICAL: main ไม้ closed + fam ไม้ cancelled (ทุกบัญชีปิด/ยกเลิกแล้ว) -> idea ปิดเอง (status=closed)",
          idea_final.get("status") == "closed" and row_state_final == "closed", json.dumps({"idea": idea_final, "rowState": row_state_final}))
    check(f"[{BROWSER_ENGINE}/{label}] ตัวกรอง 'ปิดแล้ว': satV3ClosedIdeas() เจอไอเดียนี้แล้ว",
          any(x["id"] == plan_id for x in page.evaluate("() => satV3ClosedIdeas()")), "n/a")

    # ═══════════ "รวมด้วย (นอกแผน)" opt-in path — fam CAN compute a lot (has IC/XAUUSD broker) but is not
    #   ready because its weekly new-trade quota is already full (SAT7D_NEW_MAX=2) — the case the feature is
    #   actually for (lot!=null but ready=false), distinct from "no broker at all" (lot=null, nothing to save) ═══════════

    page.evaluate("""
      () => {
        satwWrite('XAUUSD', {comps:{trend:{v:'up'},momentum:{v:'up'},zone:{v:'up',levels:[2640]},sentiment:{v:'up'},macro:{v:'up'}}, invalidation:2600});
        // fill fam's weekly Sat quota (SAT7D_NEW_MAX=2) so satV3PlanAcctCalc(...,'fam') is lot!=null but ready=false ('โควตาเต็ม')
        const B = getBook('fam');
        const wk = wpWeekKey();
        B.trades.push({id:'quota1', date:wk+'-01'.slice(0,10), port:'satB', sym:'XAUUSD', bias:'Long', entry:2600, sl:2590, tp:null, qty:0.01, mult:100, cur:'USD', status:'closed', openedAt: new Date().toISOString().slice(0,10)});
        B.trades.push({id:'quota2', date:wk+'-01'.slice(0,10), port:'satB', sym:'XAUUSD', bias:'Long', entry:2600, sl:2590, tp:null, qty:0.01, mult:100, cur:'USD', status:'open', openedAt: new Date().toISOString().slice(0,10)});
        B.trades.push({id:'quota3', date:wk+'-01'.slice(0,10), port:'satB', sym:'XAUUSD', bias:'Long', entry:2600, sl:2590, tp:null, qty:0.01, mult:100, cur:'USD', status:'open', openedAt: new Date().toISOString().slice(0,10)});
        B.trades.push({id:'quota4', date:wk+'-01'.slice(0,10), port:'satB', sym:'XAUUSD', bias:'Long', entry:2600, sl:2590, tp:null, qty:0.01, mult:100, cur:'USD', status:'open', openedAt: new Date().toISOString().slice(0,10)});
        saveBook('fam');
      }
    """)
    page.wait_for_timeout(60)
    plan2_id = page.evaluate(LEGACY_JS, "XAUUSD")   # previous XAUUSD idea is already closed, so this is a fresh draft (แบบเดิม ไม่มี conditions — ดูหมายเหตุด้านบน)
    page.wait_for_timeout(150)
    page.evaluate(f"() => {{ satV3PlanEdit('{plan2_id}','entry','2650'); satV3PlanEdit('{plan2_id}','sl','2630'); satV3PlanEdit('{plan2_id}','tp','2700'); }}")   # ST1: ใส่ TP แรก (R:R 2.5) — เดิมไม่มี TP
    page.wait_for_timeout(80)
    calc_fam_full = page.evaluate(f"() => satV3PlanAcctCalc(sat7dIdea('{plan2_id}'), 'fam')")
    check(f"[{BROWSER_ENGINE}/{label}] เตรียมเคส 'รวมด้วย (นอกแผน)': fam คำนวณ lot ได้จริง แต่โควตาไม้ใหม่สัปดาห์นี้เต็ม (4/4) -> ไม่ ready",
          calc_fam_full.get("ready") is False and calc_fam_full.get("lot") is not None
          and "โควตาเต็ม" in (calc_fam_full.get("warns") or []), json.dumps(calc_fam_full))

    draft2_html = page.evaluate(f"() => satV3DraftCardHtml(sat7dIdea('{plan2_id}'))")
    check(f"[{BROWSER_ENGINE}/{label}] adapter.rowExtra: บัญชีคำนวณ lot ได้แต่ไม่ ready -> โชว์ ⚠️ + ลิงก์ 'รวมด้วย (นอกแผน)'",
          "รวมด้วย (นอกแผน)" in draft2_html and f"satV3SaveOffplanAccount('{plan2_id}','fam')" in draft2_html, draft2_html[:800])

    page.evaluate(f"() => satV3SaveReadyAccounts('{plan2_id}')")  # only saves the ready one (main) — fam is skipped (not ready)
    page.wait_for_timeout(120)
    after_ready_only = page.evaluate(f"() => sat7dIdea('{plan2_id}')")
    check(f"[{BROWSER_ENGINE}/{label}] 'บันทึกทุกบัญชีที่พร้อม' ไม่แตะ fam (โควตาเต็ม ไม่ ready แม้คำนวณ lot ได้)",
          "fam" not in (after_ready_only.get("accts") or {}) or not (after_ready_only["accts"].get("fam") or {}).get("trade_id"),
          json.dumps(after_ready_only))

    # now confirm the opt-in link actually saves fam despite not being 'ready'
    page.evaluate(f"() => satV3SaveOffplanAccount('{plan2_id}','fam')")
    page.wait_for_timeout(120)
    fam_offplan = page.evaluate(f"""
      () => {{ const idea = sat7dIdea('{plan2_id}');
        const t = getBook('fam').trades.find(x=>x.id===((idea.accts||{{}}).fam||{{}}).trade_id);
        return {{idea, t}}; }}
    """)
    check(f"[{BROWSER_ENGINE}/{label}] satV3SaveOffplanAccount: กด 'รวมด้วย (นอกแผน)' แล้ว fam ได้ไม้จริงแม้ไม่ ready",
          fam_offplan["t"] is not None and fam_offplan["t"]["port"] == "satB", json.dumps(fam_offplan)[:400])

    # ═══════════ ✕ delete draft: only removes the idea doc, never touches any account's trade book ═══════════

    page.evaluate("""
      () => {
        satwWrite('BRENT', {comps:{trend:{v:'up'},momentum:{v:'up'},zone:{v:'up',levels:[85]},sentiment:{v:'up'},macro:{v:'up'}}, invalidation:80});
        satV3SetBias('BRENT','Long');
      }
    """)
    page.wait_for_timeout(60)
    page.evaluate("() => satV3NewPlan('BRENT')")
    page.wait_for_timeout(150)
    plan3 = page.evaluate("() => satIdeasList.find(x=>x.v3 && x.asset==='BRENT' && x.status!=='closed')")
    plan3_id = plan3["id"]
    trades_before_delete = page.evaluate("() => getBook('main').trades.length + getBook('fam').trades.length")
    page.evaluate(f"() => satV3IdeaDelete('{plan3_id}')")
    page.wait_for_timeout(150)
    trades_after_delete = page.evaluate("() => getBook('main').trades.length + getBook('fam').trades.length")
    idea_still_present = page.evaluate(f"() => satIdeasList.some(x=>x.id==='{plan3_id}')")
    check(f"[{BROWSER_ENGINE}/{label}] ✕ ลบร่าง: เอกสารไอเดียหายไปจริง แต่จำนวนไม้ในสมุดทั้งสองบัญชีไม่เปลี่ยนเลย (ลบร่างเท่านั้น ไม่แตะสมุด)",
          idea_still_present is False and trades_before_delete == trades_after_delete,
          f"still_present={idea_still_present} before={trades_before_delete} after={trades_after_delete}")

    # ═══════════ satV3SkipToggle: skipping every account auto-closes a still-draft idea ═══════════

    page.evaluate("""
      () => {
        satwWrite('BRENT', {comps:{trend:{v:'up'},momentum:{v:'up'},zone:{v:'up',levels:[85]},sentiment:{v:'up'},macro:{v:'up'}}, invalidation:80});
      }
    """)
    page.wait_for_timeout(60)
    page.evaluate("() => satV3NewPlan('BRENT')")
    page.wait_for_timeout(150)
    plan4 = page.evaluate("() => satIdeasList.find(x=>x.v3 && x.asset==='BRENT' && x.status!=='closed')")
    plan4_id = plan4["id"]
    page.evaluate(f"() => satV3SkipToggle('{plan4_id}','main',true)")
    page.wait_for_timeout(150)   # let the mock Firestore onSnapshot round-trip land in satIdeasList before the 2nd skip
    page.evaluate(f"() => satV3SkipToggle('{plan4_id}','fam',true)")
    page.wait_for_timeout(150)
    idea4_after_skip = page.evaluate(f"() => sat7dIdea('{plan4_id}')")
    check(f"[{BROWSER_ENGINE}/{label}] ข้ามทุกบัญชี -> idea ปิดเอง (status=closed) โดยไม่ต้องบันทึก order สักบัญชีเดียว",
          idea4_after_skip.get("status") == "closed", json.dumps(idea4_after_skip))

    # ═══════════ UI.planCard / UI.row / UI.chips backward compatibility — round-1 payload shapes still identical ═══════════
    # (round-1's own assertions in run_tests.py already re-run and pass each time; this re-confirms the exact
    #  same payload/assertions from inside this phase3 file too, since UI.planCard/UI.row/UI.chips were touched here)
    legacy = page.evaluate("""
      () => ({
        planCard: UI.planCard({sym:'XAUUSD', dir:'L', entry:2650, sl:2630, tp:2700, cancel:2660, rr:'2.0R',
          setups:[{label:'Sweep', on:true}], accts:[{name:'บัญชีหลัก', color:'#3F6FD8', line:'XM 0.19 lot'}]}, null),
        row: UI.row({color:'#3F6FD8', name:'บัญชีหลัก', tag:'Long', detail:'2650 / SL 2630', btns:[{label:'เข้าแล้ว'}]}),
        chips: UI.chips([{label:'Sweep', on:true},{label:'BigBar', on:false}])
      })
    """)
    check(f"[{BROWSER_ENGINE}/{label}] UI.planCard: payload เดิม (ไม่ส่ง id/editPrefix/priceChips ฯลฯ) ยังเรนเดอร์ 2650 / XM 0.19 lot เหมือนเดิม",
          "2650" in legacy["planCard"] and "XM 0.19 lot" in legacy["planCard"] and 'data-id' not in legacy["planCard"], legacy["planCard"][:300])
    check(f"[{BROWSER_ENGINE}/{label}] UI.row: payload เดิม (ไม่ส่ง onClick) ยัง render ปุ่ม 'เข้าแล้ว' เหมือนเดิม (เป็น <button> ตอนนี้ แต่ยังไม่มี onclick attr)",
          "เข้าแล้ว" in legacy["row"] and "ui-row" in legacy["row"], legacy["row"][:300])
    check(f"[{BROWSER_ENGINE}/{label}] UI.chips: payload เดิมยัง render ui-on/Sweep เหมือนเดิม",
          "ui-on" in legacy["chips"] and "Sweep" in legacy["chips"], legacy["chips"][:300])

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
    print("\n==== SUMMARY (Phase 3) ====")
    print(f"engine={BROWSER_ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(f" - {name} :: {detail}")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
