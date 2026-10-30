#!/usr/bin/env python3
"""7D.3 Phase 2 — Strategy tile bar (ส่วนที่ 1 ช่อง B, namespace satV3).
รันแยกจาก run_tests.py/run_tests_phase1.py — ไม่ลบ/แก้เคสเดิม เพิ่มเคสใหม่ของรอบนี้เท่านั้น
satV3* ยังไม่ถูก mount เข้าหน้าไหนจริง (SAT_V3_ON=false) — เทสรอบนี้เรียกฟังก์ชันตรง ๆ (ทดสอบแยกได้)
ตาม README ของงาน: full end-to-end (tiles -> plan cards -> save) รอ Phase 4 ที่ประกอบหน้าเสร็จ

รันได้ทั้ง Chromium และ WebKit:
  python3 run_tests_phase2.py
  BROWSER=webkit python3 run_tests_phase2.py
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

results = []

def check(name, ok, detail=""):
    results.append((name, ok, detail))
    d = (detail[:400] + "...(truncated)") if (detail and len(detail) > 400) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def seed_pb(page, xau="up"):
    """F2c — Macro อ่านจาก Playbook (ไม่ใช่ comps.macro.v เดิม) → seed เวอร์ชัน active ที่ท่าที XAUUSD = xau"""
    doc = {"schema": "macroPlaybook/v1", "quarter": "2026Q4", "status": "active", "view": {"headline": "h", "thesis": "t", "pillars": [{"id": "P1", "title": "เสาหลัก 1"}]},
           "assets": {"XAUUSD": {"stance": xau, "why": "w", "change_if": "c", "drivers": ["P1"]}, "BTC": {"stance": "none"}, "BRENT": {"stance": "none"}, "US": {"stance": "none"}},
           "savedAt": "2026-09-01T00:00:00.000Z", "versionNo": 1, "prevId": None, "reason": None, "stanceChanges": {}}
    page.evaluate("""(d)=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','macroPlaybook','2026Q4-v001'], d); pbStop(); pbStart(); }""", doc)
    page.wait_for_timeout(150)

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
        # ratios includes an asset the macro key maps to ('XAU') so satwMacroFF(XAUUSD) has real data to show
        route.fulfill(status=200, content_type="application/json", body=json.dumps({
            "as_of": "2026-09-20",
            "ratios": {},
            "assets": {"XAU": {"label": "Gold", "view": "Risk-off bid", "mechanism": "real yields down", "flip_when": "DXY > 105"}}
        }))
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

    # sat7dStart() populates satWeekMap/satIdeasList from the mock Firestore listeners; give it a tick.
    page.evaluate("() => { try{ sat7dStart(); }catch(e){} }")
    page.wait_for_timeout(200)

    # === tile: no assessment at all yet -> 'ยังไม่ประเมิน' + n/2 + '?' icon + no dots colored + no [+ แผน] button ===
    page.evaluate("() => { satWeekPickWrite(wpWeekKey(), ['S50']); }")   # WA1fix — ไม่มีโหมด legacy: แถบ Strategy แสดงเฉพาะที่เลือก (≤ 3) → ตรวจ S50 แยก แล้วเลือก XAU/BTC/Brent
    bar_s50 = page.evaluate("() => satV3StrategyBarHtml()")
    page.evaluate("() => { satWeekPickWrite(wpWeekKey(), ['XAUUSD', 'BTCUSD', 'BRENT']); }")
    bar0 = page.evaluate("() => satV3StrategyBarHtml()")
    check(f"[{BROWSER_ENGINE}/{label}] แถบ Strategy มีครบ 4 ช่อง (data-key ของ SAT_ASSETS ทุกตัว · WA1fix: ตามที่เลือก 3 + S50 ที่เลือกแยก)",
          all(f'data-key="{k}"' in bar0 for k in ["XAUUSD", "BTCUSD", "BRENT"]) and 'data-key="S50"' in bar_s50 and 'data-key="S50"' not in bar0, bar0[:200])
    check(f"[{BROWSER_ENGINE}/{label}] PF3 ช่องที่ยังไม่มีข้อมูลเลย: ไม่มีป้าย 'ยังไม่ประเมิน' · ไม่จาง (ui-dim) · มีปุ่ม [+ แผน] กดได้เสมอ (PF1)", "ยังไม่ประเมิน" not in bar0 and "ui-dim" not in bar0 and bar0.count("+ แผน") >= 3, bar0[:300])

    # === factor cycle: null -> up -> flat -> down -> null, exactly matching SAT_V3_CYCLE ===
    page.evaluate("() => { satV3Pick('XAUUSD'); }")
    editor0 = page.evaluate("() => satV3EditorHtml('XAUUSD', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] satV3Pick เลือก asset แล้ว editor เปิด (ui-editor แสดง XAUUSD)",
          'data-asset="XAUUSD"' in editor0, editor0[:200])

    seq = []
    for _ in range(5):
        page.evaluate("() => { satV3CycleFactor('XAUUSD','trend'); }")
        page.wait_for_timeout(30)  # let the mock Firestore onSnapshot round-trip land in satWeekMap before reading back
        v = page.evaluate("""
          () => { const w = satwWeek(wpWeekKey(),'XAUUSD');
                  return (w && w.comps && w.comps.trend) ? w.comps.trend.v : null; }
        """)
        seq.append(v)
    check(f"[{BROWSER_ENGINE}/{label}] แตะวนองค์ประกอบ: null→up→flat→down→null (วนครบรอบพอดี 4 แตะ ตัวที่ 5 กลับมา up)",
          seq == ["up", "flat", "down", None, "up"], str(seq))

    # === tally + bias-locked colored dots reflected in tile after assessing both scored factors (Trend, Macro) as 'up' — 7D.4: เหลือ 2 องค์ประกอบ ===
    # [F2c แก้เคสเดิม] Macro ▲ มาจาก Playbook (seed_pb) ไม่ใช่การเขียน comps.macro.v · Trend ▲ ยังเขียนที่ satWeek เหมือนเดิม
    seed_pb(page, "up")
    page.evaluate("""
      () => { satwWrite('XAUUSD', {comps:{trend:{v:'up'}}}); }
    """)
    page.wait_for_timeout(50)
    tally_txt = page.evaluate("() => satV3EditorHtml('XAUUSD', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] รวมองค์ประกอบถูกต้อง: ▲2 ▬0 ▼0 (ครบ 2/2 ไม่มีข้อความ 'ประเมินแล้ว')",
          "รวม ▲2 ▬0 ▼0" in tally_txt and "ประเมินแล้ว" not in tally_txt, tally_txt[:300])

    # === Bias -> Long, auto-collapses (satV3Sel resets to null) ===
    page.evaluate("() => satV3SetBias('XAUUSD','Long')")
    sel_after_bias = page.evaluate("() => satV3Sel")
    check(f"[{BROWSER_ENGINE}/{label}] PF3 ตั้ง Bias=Long ผ่านตัวช่วยเทส → ไม่มี auto-fold ตาม Bias แล้ว (ตัวแก้ XAUUSD ที่เปิดอยู่ยังเปิด)", sel_after_bias == "XAUUSD", str(sel_after_bias))

    bar1 = page.evaluate("() => satV3StrategyBarHtml()")
    # [F2c แก้เคสเดิม] ป้าย 'Long · 2/2' → 'Long · ขนาดไม้ เต็ม'
    check(f"[{BROWSER_ENGINE}/{label}] PF3 หลังตั้ง Bias=Long (ข้อมูลเก่า): tile ไม่โชว์ 'Long ·' / 'ขนาดไม้ เต็ม/ลด' · ปุ่ม [+ แผน] ยังอยู่ (PF1)", "Long ·" not in bar1 and "ขนาดไม้ เต็ม" not in bar1 and "ขนาดไม้ ลด" not in bar1 and bar1.count("+ แผน") >= 3, bar1[:200])
    check(f"[{BROWSER_ENGINE}/{label}] หลังตั้ง Bias=Long: จุด 2 จุดเขียวครบ (ui-dot-up ปรากฏ 2 ครั้งในช่อง XAUUSD)",
          bar1.count("ui-dot-up") == 2, str(bar1.count("ui-dot-up")))

    # === warnings: against-factors majority ===
    page.evaluate("""
      () => { satwWrite('XAUUSD',{comps:{trend:{v:'down'}}}); }
    """)
    seed_pb(page, "down")   # [F2c แก้เคสเดิม] Macro ▼ จาก Playbook (เดิมเขียน comps.macro.v='down')
    page.wait_for_timeout(30)
    editor_warn = page.evaluate("() => satV3EditorHtml('XAUUSD', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] PF3 ไม่มีเตือน 'Bias สวนองค์ประกอบ' แล้ว แม้ Long แต่ down มากกว่า up (satV3Warnings ถอด)", "สวนองค์ประกอบ" not in editor_warn, editor_warn[:200])
    check(f"[{BROWSER_ENGINE}/{label}] PF3 ไม่มีเตือน 'สวน Trend' แม้ Long แต่ Trend factor = down", "สวน Trend" not in editor_warn, editor_warn[:200])

    # === no-invalidation warning, cleared once set ===
    check(f"[{BROWSER_ENGINE}/{label}] PF3 ตัวแก้ไม่มีช่อง/คำเตือน Trend Shift เลย (ถอดจาก Strategy) แม้ยังไม่ตั้ง invalidation", "Trend Shift" not in editor_warn and "จุดผิด" not in editor_warn, editor_warn[:200])
    page.evaluate("() => satwSetInvalidation('XAUUSD', '2580')")
    page.wait_for_timeout(30)
    editor_inv = page.evaluate("() => satV3EditorHtml('XAUUSD', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] ตั้ง invalidation แล้วคำเตือน 'ยังไม่มี Trend Shift' หายไป",
          "ยังไม่มี Trend Shift" not in editor_inv, editor_inv[:100])

    # === แนวรับ/แนวต้าน + why fields: legacy fallback ===
    page.evaluate("""
      () => { satwWrite('BTCUSD', {comps:{zone:{v:'up', levels:[60000, 61000]}}, inv_note:'legacy note เดิม'}); }
    """)
    page.wait_for_timeout(30)
    editor_btc = page.evaluate("() => satV3EditorHtml('BTCUSD', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] แนวรับ: ยังไม่เคยตั้ง support -> fallback แสดง comps.zone.levels เดิม (60000, 61000) — 7D.4: ตัดเงื่อนไข 'readonly' ออก (7D.3 รอบ 3 เปลี่ยนเป็นช่องแก้ได้ + ชิป ✕ แล้ว แต่เคสนี้ค้างไว้จนแดงมาตั้งแต่ก่อน 7D.4)",
          "60000, 61000" in editor_btc and "disabled" not in editor_btc.split("แนวรับ")[1][:250], editor_btc[:600])
    check(f"[{BROWSER_ENGINE}/{label}] why: ยังไม่มี why -> ใช้ inv_note เดิมเป็นค่าเริ่มต้น ('legacy note เดิม')",
          "legacy note เดิม" in editor_btc, editor_btc[:600])

    # editing support writes the 'support' field for real (even if user clears it) and it stops being readonly
    page.evaluate("() => satwSetSupport('BTCUSD', '59500, 59800')")
    page.wait_for_timeout(30)
    btc_after = page.evaluate("() => ({w: satwWeek(wpWeekKey(),'BTCUSD'), editor: satV3EditorHtml('BTCUSD', wpWeekKey())})")
    check(f"[{BROWSER_ENGINE}/{label}] แก้แนวรับแล้ว support ถูกเขียนจริง เป็น [59500,59800] และ comps.zone.levels เดิมไม่ถูกลบ",
          btc_after["w"]["support"] == [59500, 59800] and btc_after["w"]["comps"]["zone"]["levels"] == [60000, 61000],
          json.dumps(btc_after["w"]))
    check(f"[{BROWSER_ENGINE}/{label}] หลังแก้แนวรับแล้ว ช่องไม่ readonly อีกต่อไป",
          "disabled" not in btc_after["editor"].split("แนวรับ")[1][:200], "n/a")

    # explicit why write does not clobber inv_note (old field preserved)
    page.evaluate("() => satwSetWhy('BTCUSD', 'เหตุผลใหม่ที่พิมพ์เอง')")
    page.wait_for_timeout(30)
    btc_why = page.evaluate("() => satwWeek(wpWeekKey(),'BTCUSD')")
    check(f"[{BROWSER_ENGINE}/{label}] เขียน why ใหม่แล้ว ไม่ลบ inv_note เดิม (ยังอยู่ครบ)",
          btc_why["why"] == "เหตุผลใหม่ที่พิมพ์เอง" and btc_why["inv_note"] == "legacy note เดิม", json.dumps(btc_why))

    # === Bias งดเทรด (None): tile dim + shows why as sub, no [+ แผน] button ===
    page.evaluate("() => satV3SetBias('BRENT','None')")
    page.wait_for_timeout(30)
    tile_dim_check = page.evaluate("""
      () => { const el = document.createElement('div'); el.innerHTML = satV3StrategyBarHtml();
        const t = el.querySelector('.ui-tile[data-key="BRENT"]');
        return {dim: t ? t.classList.contains('ui-dim') : null, html: t ? t.outerHTML : null}; }
    """)
    check(f"[{BROWSER_ENGINE}/{label}] PF3 Bias=งดเทรด (ข้อมูลเก่า): tile BRENT ไม่จาง (ไม่มี ui-dim · ไม่มีสถานะงดเทรดแล้ว)", tile_dim_check["dim"] is False, str(tile_dim_check["dim"]))
    brent_tile = tile_dim_check["html"] or ""
    check(f"[{BROWSER_ENGINE}/{label}] PF3 Bias=งดเทรด (ข้อมูลเก่า): ช่อง BRENT ไม่มีป้าย 'งดเทรด' · ยังมีปุ่ม [+ แผน]", "งดเทรด" not in brent_tile and "+ แผน" in brent_tile, brent_tile[:300])

    # === [F2c แก้เคสเดิม] เดิม: seed collection 'macro' แล้วเช็คป้าย 'ใส่เอง' + satwMacroFF() คืน null → ตอนนี้ Macro = บล็อกอ่านอย่างเดียวจาก Playbook · satwMacroFF ถูกลบ ===
    page.evaluate("""
      () => { window.firebase.__mockDb.__seedDoc(['macro','wk1'], {week:'2026-09-20',
              assets:{XAU:{label:'Gold', view:'Risk-off bid', mechanism:'real yields down', flip_when:'DXY > 105'}}}); }
    """)
    page.evaluate("() => rsLoad(true)")
    page.wait_for_timeout(150)
    editor_macro = page.evaluate("() => satV3EditorHtml('XAUUSD', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] F2c Macro ไม่แสดง Fund-flow ('macro' เดิมไม่ถูกอ่าน) · ไม่มีป้าย 'ใส่เอง' · มีบล็อก Macro อ่านอย่างเดียวจาก Playbook",
          "Fund-flow" not in editor_macro and "Gold" not in editor_macro and "ใส่เอง" not in editor_macro and 'data-macro-block="1"' in editor_macro, editor_macro[:300])
    check(f"[{BROWSER_ENGINE}/{label}] F2c satwMacroFF ถูกลบแล้ว · rsMacroDoc ก็ไม่มี",
          page.evaluate("() => typeof satwMacroFF==='undefined' && typeof rsMacroDoc==='undefined'"))

    # S50 has no fund-flow mapping (SATW_MACRO_KEY.S50 === null) -> must degrade to '— ไม่มีข้อมูล...' not throw
    editor_s50 = page.evaluate("() => satV3EditorHtml('S50', wpWeekKey())")
    check(f"[{BROWSER_ENGINE}/{label}] 7D.4 S50 (ไม่มี mapping) เรนเดอร์ตัวแก้ปกติ ไม่ throw ไม่มีข้อความ Fund-flow",
          "Fund-flow" not in editor_s50 and 'data-asset="S50"' in editor_s50, editor_s50[:200])

    # === copy-from-previous-week: write a previous week doc through the real sat7dWrite() path
    #     (NOT __seedDoc — __seedDoc writes the mock store directly without calling notify(), so it never
    #     reaches satWeekMap once the onSnapshot listener is already attached; sat7dWrite() uses the real
    #     doc.set({merge:true}) path which does notify the listener, same as production) ===
    page.evaluate("""
      () => {
        const wk = wpWeekKey();
        const d = new Date(wk+'T00:00:00'); d.setDate(d.getDate()-7);
        const pk = wpWeekKey(d);
        sat7dWrite('satWeek', pk, {
          S50: {comps:{trend:{v:'up'},momentum:{v:'up'},zone:{v:'flat',levels:[900]},sentiment:{v:'up'},macro:{v:'flat'}},
                invalidation: 888, inv_note: 'สัปดาห์ก่อน', opinion_txt: 'ความเห็นสัปดาห์ก่อน'}
        });
      }
    """)
    page.wait_for_timeout(250)  # let onSnapshot deliver into satWeekMap
    page.evaluate("() => satV3CopyPrev('S50')")
    page.wait_for_timeout(100)
    s50_after_copy = page.evaluate("() => satwWeek(wpWeekKey(),'S50')")
    check(f"[{BROWSER_ENGINE}/{label}] PF3 คัดลอกจากสัปดาห์ก่อน (S50): คัดลอก comps + ความเห็น (opinion_txt) · ไม่คัดลอก Bias/invalidation/inv_note (PF1)", bool(s50_after_copy) and bool(s50_after_copy.get("comps")) and s50_after_copy.get("opinion_txt") == "ความเห็นสัปดาห์ก่อน" and not s50_after_copy.get("bias") and not s50_after_copy.get("invalidation") and not s50_after_copy.get("inv_note"), json.dumps(s50_after_copy, ensure_ascii=False)[:300])

    # === UI.tiles backward compatibility: round-1 caller shape (no head/dotsHtml) still renders exactly as before ===
    legacy_tiles = page.evaluate("""
      () => UI.tiles([{key:'x', title:'XAUUSD', value:'Long', sub:'test', cls:'ok'}], 'x')
    """)
    check(f"[{BROWSER_ENGINE}/{label}] UI.tiles: caller เดิม (ไม่ส่ง head) ยังเรนเดอร์ title/value/sub/cls แบบเดิมทุกประการ",
          "ui-tile-k" in legacy_tiles and "XAUUSD" in legacy_tiles and "ui-tile-v ok" in legacy_tiles
          and "Long" in legacy_tiles and "test" in legacy_tiles and "ui-tile ui-sel" in legacy_tiles,
          legacy_tiles)

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
    print("\n==== SUMMARY (Phase 2) ====")
    print(f"engine={BROWSER_ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok:
                print(f" - {name} :: {detail}")
    sys.exit(1 if n_fail else 0)

if __name__ == "__main__":
    main()
