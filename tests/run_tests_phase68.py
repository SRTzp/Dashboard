#!/usr/bin/env python3
"""MF1 — Macro Playbook v2: Asset ไม่จำกัด 4 ตัว + ★ + ＋ วางแผน + Link Asset · เทส 68
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-01 ไทย
ภาพ tests/screenshots/mf1-{flow-v2,row-open,link,add-new-asset}-{1440,390}.png
รัน: python3 run_tests_phase68.py"""
import copy, json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, settings, overflow = P54.txt, P54.settings, P54.overflow
SAVED = "2026-09-27T10:00:00.000Z"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def cell(stance, **kw):
    if stance == "none": return {"stance": "none"}
    d = {"stance": stance, "why": f"เหตุผลของท่าที {stance} ที่ค่อนข้างยาวเพื่อทดสอบการตัดข้อความเป็นบรรทัดเดียวด้วยจุดสามจุด", "change_if": f"เปลี่ยนเมื่อ {stance}", "drivers": ["P1"]}
    d.update(kw); return d


def v2obj(assets=None, schema="macroPlaybook/v2", status="active", **view):
    a = assets if assets is not None else {
        "XAUUSD": cell("up", focus=True), "XAG": cell("up", focus=True), "BTC": cell("up_flat", posture="ETF flow ดี"),
        "USDJPY": cell("down"), "BRENT": cell("flat"), "US": cell("up_flat", posture="valuation สูง")}
    v = {"headline": "หัวข้อ", "thesis": "ข้อความ", "pillars": [{"id": "P1", "title": "เสาหลัก 1"}, {"id": "P2", "title": "เสาหลัก 2"}]}
    v.update(view)
    return {"schema": schema, "quarter": "2026Q4", "status": status, "doc_url": "https://example.com/x", "view": v, "assets": a}


def v2doc(no=1, **kw):
    o = v2obj(**kw); o.update({"id": f"2026Q4-v{no:03d}", "savedAt": SAVED, "versionNo": no, "prevId": None, "reason": None, "stanceChanges": {}})
    return o


def v1obj(**kw):
    o = P11.pbver(1, SAVED, x="up", b="down_flat", r="flat", u="none", ba={"posture": "ระยะสั้นยังผันผวน"}); o["schema"] = "macroPlaybook/v1"
    for k in ("id", "savedAt", "versionNo", "prevId", "reason", "stanceChanges"): o.pop(k, None)
    return o


CUSTOM = [{"key": "XAG", "label": "Silver", "unit": "lot"}, {"key": "GOLD2", "label": "Gold2", "unit": "lot"}]


def fixture(doc):
    s = doc["books"]["main"]["settings"]
    s["satCustomAssets"] = [dict(c) for c in CUSTOM]
    for k in ("XAG", "GOLD2"): s["brokers"]["XM"][k] = {"contract": 5000, "lotStep": 0.01, "minLot": 0.01, "cur": "USD"}


def launch(pw, w, h, pb=None):
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture)
    P51.fresh(page, None)
    P11.seed_pb(page, [pb if pb is not None else v2doc()])
    return browser, page, ce, pe


def flow(page, open_=True):
    js(page, "(o)=>{ switchTab('flow'); pbOpen = o; pbRender(); }", open_); page.wait_for_timeout(300)


def rows(page): return js(page, "()=>[...document.querySelectorAll('#pbPanel [data-pb-row]')].map(e=>e.dataset.pbRow)")
def val(page, o): return js(page, "(o)=>Calc.pbValidate(o, new Date('2026-10-01T05:00:00Z'))", o)
def pbk(page, k, lst=None): return js(page, "([k,l])=>satPbKeyOf(k, l===null ? undefined : l)", [k, lst])


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # ── 1 วาง JSON v2 (6 Asset) → ตรวจ → บันทึก → แสดง 6 แถวเรียง ★ ก่อน
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture)
    try:
        P51.fresh(page, None)
        old = P11.pbver(1, "2026-09-01T00:00:00.000Z", x="up", b="down_flat", r="flat", u="none"); old["schema"] = "macroPlaybook/v1"
        P11.seed_pb(page, [old])   # เวอร์ชันเดิมเก่ากว่านาฬิกาปลอม → ที่บันทึกใหม่เป็นตัวล่าสุด
        flow(page, True)
        obj = v2obj(watch="ข้อควรติดตามที่ยาวเกิน 140 ตัวอักษรแต่ไม่เกิน 200 " + "ก" * 100)
        page.locator("#pbPanel button:has-text('วาง JSON')").click()
        page.fill("#pbText", json.dumps(obj, ensure_ascii=False))
        page.locator(".pb-sheet button:has-text('ตรวจ')").click(); page.wait_for_timeout(250)
        errs = page.locator(".pb-sheet .pbErrs").count()
        warn = txt(page, ".pb-sheet .pbWarns") or ""
        check(f"{tag} 1 JSON v2 6 Asset: ตรวจผ่าน ไม่มี error · watch 150 ตัวไม่เตือน", errs == 0 and "view.watch" not in warn, warn)
        check(f"{tag} 1 พรีวิวมี 6 แถว", page.locator(".pb-sheet .pbRowW").count() == 6)
        page.locator(".pb-sheet .ui-chip:has-text('ทบทวนตามรอบ'), .pb-sheet [onclick*=\"pbSetReason('review')\"]").first.click(); page.wait_for_timeout(150)
        page.fill("#pbReasonText", "เพิ่ม Asset ตาม v2"); page.wait_for_timeout(150)
        page.locator("#pbSaveBtn").click(); page.wait_for_timeout(700)
        ids = js(page, "()=>pbList.map(v=>v.id).sort()")
        check(f"{tag} 1 บันทึกได้ → v002 schema v2 (6 Asset)", ids[-1] == "2026Q4-v002" and js(page, "()=>pbList.find(v=>v.id==='2026Q4-v002').schema") == "macroPlaybook/v2" and js(page, "()=>Object.keys(pbList.find(v=>v.id==='2026Q4-v002').assets).length") == 6, json.dumps(ids))
        flow(page, True)
        check(f"{tag} 1 การ์ดแสดง 6 แถว เรียง ★ ก่อน → ▲▼ เต็ม → ▲▬ → ▬", rows(page) == ["XAUUSD", "XAG", "USDJPY", "BTC", "US", "BRENT"], json.dumps(rows(page)))
        cls = js(page, "()=>Object.fromEntries([...document.querySelectorAll('#pbPanel [data-pb-row]')].map(e=>[e.dataset.pbRow, e.querySelector('.pbIco').className.replace('pbIco ','')]))")
        check(f"{tag} 1 สีท่าที: ▲ เขียว · ▼ แดง · ▬ เทา", cls["XAUUSD"] == "pb-up" and cls["USDJPY"] == "pb-dn" and cls["BTC"] == "pb-up" and cls["BRENT"] == "pb-flat", json.dumps(cls))
        check(f"{tag} 1 ★ นำหน้าชื่อเฉพาะ focus", js(page, "()=>[...document.querySelectorAll('#pbPanel [data-pb-row]')].filter(e=>e.querySelector('.pbStar')).map(e=>e.dataset.pbRow)") == ["XAUUSD", "XAG"])
        shot(page, f"mf1-flow-v2-{sfx}.png", "#pbPanel")
        page.locator("#pbPanel [data-pb-row='BTC'] .pbAsset").click(); page.wait_for_timeout(250)
        check(f"{tag} 1 แตะแถว → กางรายละเอียดเดิม (why เต็ม · change_if)", "change_if" in (txt(page, ".pb-sheet") or ""))
        shot(page, f"mf1-row-open-{sfx}.png")
        page.keyboard.press("Escape"); page.wait_for_timeout(150)
        check(f"{tag} 1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 2 ตรวจ JSON
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture)
    try:
        P51.fresh(page, None)
        r1 = val(page, v1obj())
        check(f"{tag} 2 v1 เดิม (4 Asset) ยังผ่าน", r1["errors"] == [], json.dumps(r1, ensure_ascii=False))
        a = v2obj({"XAG": cell("up", focus=True), "EURUSD": cell("none")})
        check(f"{tag} 2 v2 ไม่มี XAUUSD (ไม่บังคับ 4 ตัว) → ผ่าน", val(page, a)["errors"] == [], json.dumps(val(page, a), ensure_ascii=False))
        e = lambda o: " | ".join(val(page, o)["errors"])
        check(f"{tag} 2 key ผิดรูป (xau / ยาวเกิน 12) → error", "key" in e(v2obj({"xau": cell("up")})) and "key" in e(v2obj({"ABCDEFGHIJKLM": cell("up")})))
        check(f"{tag} 2 stance ผิด → error", "stance" in e(v2obj({"XAG": {"stance": "bull", "why": "x", "change_if": "y"}})))
        check(f"{tag} 2 ไม่มี why → error", "why" in e(v2obj({"XAG": {"stance": "up", "change_if": "y"}})))
        check(f"{tag} 2 focus ไม่ใช่ true/false → error · label ไม่ใช่ข้อความ → error", "focus" in e(v2obj({"XAG": cell("up", focus="yes")})) and "label" in e(v2obj({"XAG": cell("up", label=5)})))
        check(f"{tag} 2 v2 assets ว่าง → error · schema ผิด → error", e(v2obj({})) != "" and "schema" in e(v2obj(schema="macroPlaybook/v3")))
        check(f"{tag} 2 v1 ที่ขาด asset ใน 4 ตัว → ยัง error เดิม", "ขาด" in e({**v1obj(), "assets": {"XAUUSD": cell("up")}}))
        w200 = val(page, v2obj(watch="ก" * 200)); w201 = val(page, v2obj(watch="ก" * 201))
        check(f"{tag} 2 view.watch 200 ไม่เตือน · 201 เตือน", not any("watch" in x for x in w200["warnings"]) and any("watch" in x for x in w201["warnings"]))
    finally: browser.close()

    # ── 3 stanceChanges
    browser, context, page, ce, pe, dialogs = P54.launch(pw, w, h, fixture)
    try:
        P51.fresh(page, None)
        d = js(page, "([a,b])=>Calc.pbDiff(a,b)", [v1obj(), v2obj({"XAUUSD": cell("up"), "BTC": cell("down_flat"), "XAG": cell("up"), "US": cell("none")})])
        check(f"{tag} 3 v1 → v2: เพิ่ม XAG → {{from:none,to:up}} · ตัด BRENT → {{to:none}}", d.get("XAG") == {"from": "none", "to": "up"} and d.get("BRENT") == {"from": "flat", "to": "none"} and "XAUUSD" not in d and "BTC" not in d, json.dumps(d))
        d2 = js(page, "([a,b])=>Calc.pbDiff(a,b)", [None, v2obj({"XAG": cell("up")})])
        check(f"{tag} 3 เวอร์ชันแรก: เทียบกับ none", d2 == {"XAG": {"from": "none", "to": "up"}}, json.dumps(d2))
    finally: browser.close()

    # ── 4 satPbKeyOf
    browser, page, ce, pe = launch(pw, w, h)
    try:
        check(f"{tag} 4 BTCUSD→BTC · BTCUSDT→BTC · XAUUSD→XAUUSD · BRENT→BRENT", [pbk(page, "BTCUSD"), pbk(page, "BTCUSDT"), pbk(page, "XAUUSD"), pbk(page, "BRENT")] == ["BTC", "BTC", "XAUUSD", "BRENT"])
        check(f"{tag} 4 XAG (เพิ่มเองใน Sat · มีใน Playbook v2) → XAG · S50 (ไม่มีใน Playbook) → null", pbk(page, "XAG") == "XAG" and pbk(page, "S50") is None)
        check(f"{tag} 4 Playbook ที่ส่งเอง (list) ที่ไม่มี XAG → null", pbk(page, "XAG", [v2doc(assets={"XAUUSD": cell("up")})]) is None)
        js(page, "()=>satSettingsWrite(st=>{ st.satPbLink = {NVDA:'US', S50:'none', XAG:'none'}; })")
        check(f"{tag} 4 ตั้ง link NVDA→US → US · 'none' → null (แม้ key ตรง)", pbk(page, "NVDA") == "US" and pbk(page, "XAG") is None and pbk(page, "S50") is None)
        src = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
        i = src.index("function satPbKeyOf("); j = src.index("\n}\n", i) + 3
        left = re.findall(r"(SAT_PB_ASSET\[|IDEA_ASSET_PB\[)", src[:i] + src[j:])
        check(f"{tag} 4 [static] ไม่เหลือการอ่าน SAT_PB_ASSET[ / IDEA_ASSET_PB[ ตรงนอก satPbKeyOf", not left, json.dumps(left))
    finally: browser.close()

    # ── 5 การ์ด Sat XAG ใช้ Macro ของ XAG
    browser, page, ce, pe = launch(pw, w, h, v2doc(assets={"XAUUSD": cell("up"), "XAG": cell("down", focus=True)}))
    try:
        m = js(page, "()=>{ const x = satMacroOf('XAG'); return {state:x.state, v:x.versionId}; }")
        check(f"{tag} 5 satMacroOf(XAG) = ท่าที XAG ใน Playbook v2 (▼)", m["state"] == "down" and m["v"] == "2026Q4-v001", json.dumps(m))
        f = js(page, "()=>{ const mk = (b)=>({asset:'XAG', bias:b, conditions:[], accts:{}, entry:30, sl:29}); const f1 = satV3F2c(mk('Long')); return {lf:f1.factor, align:f1.align, mac:f1.mac.state}; }")
        check(f"{tag} 5 F2c ใช้ท่าที XAG: Long สวน Macro ▼ → align=against · ขนาด ×0.6 (WA1: ตัวคูณตาม Macro อย่างเดียว)", f["mac"] == "down" and f["align"] == "against" and f["lf"] == 0.6, json.dumps(f))
        js(page, "()=>satwWrite('XAG', {bias:'Long', comps:{trend:{v:'down'}}, support:[28], resistance:[33], invalidation:27})"); page.wait_for_timeout(300)
        f = js(page, "()=>satV3F2c({asset:'XAG', bias:'Long', conditions:[], accts:{}, entry:30, sl:29}).factor")
        check(f"{tag} 5 สวน Macro + Trend สวน → ×0.6 (Trend ไม่มีผลเพิ่ม)", f == 0.6, str(f))
        P51.fresh(page, P51.idea_doc(asset="XAG", entry=30, sl=29, tp=31.5, zone=(31.5, 33), iid="iX"))
        P11.seed_pb(page, [v2doc(assets={"XAUUSD": cell("up"), "XAG": cell("down", focus=True)})]); js(page, "()=>satV3Render()"); page.wait_for_timeout(250)
        card = txt(page, "#satV3Panel") or ""
        check(f"{tag} 5 การ์ดแผน XAG แสดง 'Macro: ▼ ลง'", "Macro: ▼ ลง" in card or "Macro" in card and "▼ ลง" in card, card[:200])
    finally: browser.close()

    # ── 6 ＋ วางแผน
    browser, page, ce, pe = launch(pw, w, h)
    try:
        flow(page, True)
        btns = js(page, "()=>Object.fromEntries([...document.querySelectorAll('#pbPanel [data-pb-row]')].map(e=>[e.dataset.pbRow, e.querySelector('[data-pb-plan]') ? e.querySelector('[data-pb-plan]').innerText.trim() : (e.querySelector('[data-pb-core]') ? 'CORE:'+e.querySelector('[data-pb-core]').innerText.trim() : null)]))")
        check(f"{tag} 6 ปุ่มขวา: ＋ วางแผน ทุกแถว · US = ป้าย 'หุ้น Core' ไม่มีปุ่ม", btns["XAG"] == "＋ วางแผน" and btns["US"] == "CORE:หุ้น Core" and btns["XAUUSD"] == "＋ วางแผน", json.dumps(btns, ensure_ascii=False))
        page.locator("#pbPanel [data-pb-plan='XAG']").click(); page.wait_for_timeout(400)
        wk = js(page, "()=>satWeekPickList(wpWeekKey())")
        check(f"{tag} 6 ＋ วางแผน XAG (มีใน Sat) → satWeekPick[สัปดาห์นี้] มี XAG · ไปแท็บ แผน", wk == ["XAG"] and js(page, "()=>activeTab") == "plan" and js(page, "()=>Object.keys(tdSettings().satWeekPick)") == [js(page, "()=>wpWeekKey()")], json.dumps([wk, js(page, "()=>activeTab")]))
        flow(page, True)
        t = txt(page, "#pbPanel [data-pb-row='XAG'] [data-pb-plan]")
        check(f"{tag} 6 ปุ่มเป็น '✓ สัปดาห์นี้'", t == "✓ สัปดาห์นี้", t)
        page.locator("#pbPanel [data-pb-row='XAG'] [data-pb-in]").click(); page.wait_for_timeout(300)
        check(f"{tag} 6 แตะ ✓ → ไปการ์ดใน Strategy (แท็บ แผน · ตัวแก้ XAG กาง)", js(page, "()=>activeTab") == "plan" and js(page, "()=>satV3Sel") == "XAG")
        js(page, "()=>{ satWeekPickAdd('XAUUSD'); satWeekPickAdd('BTCUSD'); }")
        flow(page, True)
        page.locator("#pbPanel [data-pb-plan='BRENT']").click(); page.wait_for_timeout(300)
        msg = txt(page, "#pbPanel [data-pb-msg]") or ""
        check(f"{tag} 6 ครบ 3 แล้ว → 'สัปดาห์นี้ครบ 3 ตัวแล้ว — เอาตัวอื่นออกก่อน' · ไม่เพิ่ม", msg == "สัปดาห์นี้ครบ 3 ตัวแล้ว — เอาตัวอื่นออกก่อน" and js(page, "()=>satWeekPickList()") == ["XAG", "XAUUSD", "BTCUSD"], msg)
        js(page, "()=>satWeekPickRemove('BTCUSD')")
        check(f"{tag} 6 satWeekPickRemove เอาออกได้", js(page, "()=>satWeekPickList()") == ["XAG", "XAUUSD"])
        flow(page, True)
        page.locator("#pbPanel [data-pb-plan='USDJPY']").click(); page.wait_for_timeout(500)
        check(f"{tag} 6 USDJPY (ไม่มีใน Sat) → เปิด sheet เพิ่มสินค้า เติม key ให้", js(page, "()=>document.getElementById('sat7dBrokerOverlay').classList.contains('show')") and js(page, "()=>!!document.querySelector('#sat7dBrokerOverlay [data-as-row=USDJPY]')"))
        shot(page, f"mf1-add-new-asset-{sfx}.png")
        page.locator("#sat7dBrokerOverlay [data-br-save]").click(); page.wait_for_timeout(600)
        check(f"{tag} 6 บันทึก → USDJPY อยู่ในสินค้า Sat + อยู่ในสัปดาห์นี้ + ไปแท็บ แผน", js(page, "()=>satCustomList().some(c=>c.key==='USDJPY')") and "USDJPY" in js(page, "()=>satWeekPickList()") and js(page, "()=>activeTab") == "plan", json.dumps(js(page, "()=>satWeekPickList()")))
        flow(page, True)
        check(f"{tag} 6 แถว USDJPY ตอนนี้ ✓ สัปดาห์นี้", (txt(page, "#pbPanel [data-pb-row='USDJPY'] [data-pb-plan]") or "") == "✓ สัปดาห์นี้")
        # key ที่ใช้เป็นสินค้า Sat ไม่ได้ → ข้อความ
        P11.seed_pb(page, [v2doc(assets={"XAUUSD": cell("up"), "OIL": cell("up")})]); flow(page, True)
        page.locator("#pbPanel [data-pb-plan='OIL']").click(); page.wait_for_timeout(250)
        check(f"{tag} 6 key สงวน (OIL) → ข้อความให้กด ⋯ ผูกเอง · ไม่เปิด sheet", "สงวน" in (txt(page, "#pbPanel [data-pb-msg]") or ""))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 7 Link ที่แถว
    browser, page, ce, pe = launch(pw, w, h, v2doc(assets={"XAUUSD": cell("up", focus=True), "XAG": cell("down")}))
    try:
        flow(page, True)
        page.locator("#pbPanel [data-pb-more='XAUUSD']").click(); page.wait_for_timeout(250)
        check(f"{tag} 7 ⋯ → 'ใช้กับ Sat: [เลือก ▾]' มี GOLD2 ให้เลือก", "GOLD2" in js(page, "()=>[...document.querySelectorAll('[data-pb-link-sel=XAUUSD] option')].map(o=>o.value).join(',')"))
        page.locator("[data-pb-link-sel='XAUUSD']").select_option("GOLD2"); page.wait_for_timeout(300)
        check(f"{tag} 7 ผูก GOLD2→XAUUSD: เก็บ satPbLink · การ์ด GOLD2 ใช้ท่าที XAUUSD", settings(page, "satPbLink") == {"GOLD2": "XAUUSD"} and js(page, "()=>satMacroOf('GOLD2').state") == "up" and js(page, "()=>satV3F2c({asset:'GOLD2', bias:'Long', conditions:[], accts:{}, entry:30, sl:29}).mac.state") == "up", json.dumps(settings(page, "satPbLink")))
        shot(page, f"mf1-link-{sfx}.png", "#pbPanel")
        page.locator("#pbPanel [data-pb-more='XAG']").click(); page.wait_for_timeout(250)
        page.locator("[data-pb-link-sel='XAG']").select_option("GOLD2"); page.wait_for_timeout(300)
        msg = txt(page, "#pbPanel [data-pb-msg]") or ""
        check(f"{tag} 7 ผูกซ้ำที่อื่น (GOLD2→XAG) → ย้าย + ข้อความ 'ย้าย Gold2 จาก XAUUSD'", settings(page, "satPbLink") == {"GOLD2": "XAG"} and "ย้าย" in msg and "XAUUSD" in msg and js(page, "()=>satMacroOf('GOLD2').state") == "down", msg)
        page.locator("[data-pb-linked='GOLD2'] .pbX").first.click(); page.wait_for_timeout(300)
        check(f"{tag} 7 ✕ เลิกผูก → GOLD2 ไม่มี Macro", js(page, "()=>satPbKeyOf('GOLD2')") is None)
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 8 แถบดำ
    browser, page, ce, pe = launch(pw, w, h)
    try:
        flow(page, True)
        bar = js(page, "()=>[...document.querySelectorAll('.ffActMac .as')].map(e=>e.innerText.trim())")
        check(f"{tag} 8 แถบดำแสดงเฉพาะ Asset ★ (XAU ▲ · XAG ▲)", bar == ["XAU ▲", "XAG ▲"], json.dumps(bar, ensure_ascii=False))
        P11.seed_pb(page, [v2doc(assets={"A1": cell("up"), "A2": cell("down"), "A3": cell("flat"), "A4": cell("up"), "A5": cell("up")})]); flow(page, True)
        bar = js(page, "()=>[...document.querySelectorAll('.ffActMac .as')].map(e=>e.innerText.trim())")
        check(f"{tag} 8 ไม่มี ★ → 4 ตัวแรกตามลำดับ", len(bar) == 4 and bar[0].startswith("A1"), json.dumps(bar))
        P11.seed_pb(page, [v2doc(assets={f"K{i}": cell("up", focus=True) for i in range(1, 7)})]); flow(page, True)
        check(f"{tag} 8 ★ มากกว่า 4 → แสดงสูงสุด 4", js(page, "()=>document.querySelectorAll('.ffActMac .as').length") == 4)
    finally: browser.close()

    # ── 9 บรรทัดเดียว / ไม่ล้น
    browser, page, ce, pe = launch(pw, w, h)
    try:
        flow(page, True)
        m = js(page, """()=>{ const r=[...document.querySelectorAll('#pbPanel [data-pb-row="XAG"]')][0]; const why=r.querySelector('.pbWhy'), c=getComputedStyle(why);
            const a=r.querySelector('.pbAsset').getBoundingClientRect(), b=r.querySelector('.pbPlan').getBoundingClientRect();
            return {ws:c.whiteSpace, to:c.textOverflow, clipped:why.scrollWidth>why.clientWidth, sameLine:Math.abs((a.top+a.height/2)-(b.top+b.height/2))<4, h:r.getBoundingClientRect().height,
                    right:b.right, panelRight:document.querySelector('#pbPanel .pbCard').getBoundingClientRect().right}; }""")
        check(f"{tag} 9 แถว Asset บรรทัดเดียว: why ตัด … · ปุ่มอยู่บรรทัดเดียวกันและไม่ล้นกรอบ", m["ws"] == "nowrap" and m["to"] == "ellipsis" and m["clipped"] and m["sameLine"] and m["right"] <= m["panelRight"] + 1 and m["h"] < 60, json.dumps(m))
        check(f"{tag} 9 หน้าไม่ล้นแนวนอน ({label})", overflow(page) <= 0, str(overflow(page)))
        check(f"{tag} 9 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 68 / MF1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
