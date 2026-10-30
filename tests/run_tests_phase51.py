#!/usr/bin/env python3
"""ST1 — กติกา Sat: ออกกำไร 2 ขั้น (TP1/TP2) · R:R ≥ 1.5 · งดเปิดไม้ช่วง CPI/NFP · เช็กลิสต์ก่อนข่าว · เทส 51
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอมเลื่อนได้ (timezone Asia/Bangkok)
ภาพ tests/screenshots/st1-{settings-news,plan-block-news,plan-rr,today-news}-{1440,390}.png
รัน: python3 run_tests_phase51.py"""
import json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase5 as p5
import run_tests_phase24 as p24
import run_tests_phase36 as p36
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
T = P38.T


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def set_clock(page, iso): P37.set_clock(page, iso)


def set_news(page, events):
    js(page, "(ev)=>{ const B=getBook('main'); B.settings.newsEvents = ev; saveBook('main'); render(); }", events); page.wait_for_timeout(300)


def idea_doc(asset="XAUUSD", bias="Long", entry=2410, sl=2400, tp=2425, zone=(2425, 2440), iid="iD", act=True):
    return {"id": iid, "v3": True, "asset": asset, "bias": bias, "entry": entry, "sl": sl, "tp": tp, "accts": {}, "macro_note": "เหตุผลทดสอบ",   # WA1: สวน/นอก Macro ต้องมีเหตุผลก่อนบันทึก order
           
            "conditions": [{"id": "c1", "text": "Break & Pullback @ 2400", "tp_from": zone[0] if zone else None, "tp_to": zone[1] if zone else None,
                            "inval": None, "active": act, "saved": True}]}


def put_idea(page, idea):
    js(page, "(i)=>{ i.week = wpWeekKey(); sat7dWrite('satIdeas', i.id, Object.assign({}, i, {created_at:new Date().toISOString(), planned:true, setups:[], status:'active'})); }", idea)
    page.wait_for_timeout(450)


def fresh(page, idea=None):
    p36.clean(page, "Long")
    if idea: put_idea(page, idea)
    P37.go_sat(page); P37.open_plan(page)


def calc(page, idea, acct="main"):
    return js(page, """([i,a])=>{ i.week = wpWeekKey(); const c = satV3PlanAcctCalc(i, a); return {ready:c.ready, news:c.newsBlock, rr:c.rrBlock, lot:c.lot, warns:c.warns}; }""", [idea, acct])


def n_trades(page, acct="main"): return js(page, "(a)=>getBook(a).trades.length", acct)


def overflow(page, sels): return P37.overflow(page, sels)


# ───────────────────────── 1 ตั้งค่า วันข่าว ─────────────────────────
def settings_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = P39.launch(pw, w, h, doc=P38.doc38(clean=True), clean=True, iso="2026-10-01T05:00:00Z")
    try:
        js(page, "()=>{ openSystemSettings(); document.getElementById('newsSetSec').open = true; }"); page.wait_for_timeout(300)
        check(f"{tag} 1 ไม่มีวันข่าว → บรรทัดเตือน 'ยังไม่ได้กรอกวันข่าวช่วง 2 สัปดาห์ข้างหน้า'", "ยังไม่ได้กรอกวันข่าวช่วง 2 สัปดาห์ข้างหน้า" in (page.locator("[data-news-warn]").text_content() if page.locator("[data-news-warn]").count() else ""))

        def add(date, kind, time=None):
            page.locator("[data-news-new-date]").fill(date)
            page.locator("[data-news-new-kind]").select_option(kind)
            page.wait_for_timeout(100)
            auto = page.locator("[data-news-new-time]").input_value()
            if time: page.locator("[data-news-new-time]").fill(time)
            page.locator("[data-news-add]").click(); page.wait_for_timeout(900)
            return auto

        a1 = add("2026-10-14", "CPI")
        check(f"{tag} 1 CPI 2026-10-14 (ช่วง DST) → เวลาเติมให้ 19:30", a1 == "19:30", a1)
        a2 = add("2026-11-06", "NFP")
        check(f"{tag} 1 NFP 2026-11-06 (หลังออมแสงสิ้นสุด 1 พ.ย.) → เวลาเติมให้ 20:30", a2 == "20:30", a2)
        a3 = add("2026-10-29", "FOMC")
        check(f"{tag} 1 FOMC 2026-10-29 (DST) → เวลาเติมให้ 01:00", a3 == "01:00", a3)
        auto = js(page, "()=>[newsDefTime('FOMC','2026-11-20'), newsDefTime('CPI','2026-03-07'), newsDefTime('CPI','2026-03-08'), newsDefTime('CPI','2026-10-31'), newsDefTime('CPI','2026-11-01')]")
        check(f"{tag} 1 ขอบออมแสง: อาทิตย์ที่ 2 มี.ค. (8 มี.ค. 2026) เริ่ม DST (7 มี.ค. ยังไม่) · อาทิตย์ที่ 1 พ.ย. (1 พ.ย.) จบ · FOMC นอก DST = 02:00", auto == ["02:00", "20:30", "19:30", "19:30", "20:30"], json.dumps(auto))
        a4 = add("2026-10-15", "NFP", time="19:35")
        saved = P38.settings_db(page)["newsEvents"]
        check(f"{tag} 1 แก้เวลาเองก่อนเพิ่มได้ (19:35) · เก็บที่ settings ของ acctList[0] (main) เรียงตามวัน", [(e["date"], e["kind"], e["time"]) for e in saved] == [("2026-10-14", "CPI", "19:30"), ("2026-10-15", "NFP", "19:35"), ("2026-10-29", "FOMC", "01:00"), ("2026-11-06", "NFP", "20:30")], json.dumps(saved))
        check(f"{tag} 1 ไม่ได้เขียนลงบัญชีอื่น (fam ไม่มี newsEvents)", "newsEvents" not in P38.settings_db(page, "fam"))
        check(f"{tag} 1 มี CPI ใน 14 วันข้างหน้าแล้ว → บรรทัดเตือนหาย", page.locator("[data-news-warn]").count() == 0)
        n0 = len(saved)
        add("2026-10-14", "CPI")
        saved2 = P38.settings_db(page)["newsEvents"]
        check(f"{tag} 1 วัน+ประเภทซ้ำ → เตือน ไม่บันทึกซ้ำ", len(saved2) == n0 and "อยู่แล้ว" in page.locator("[data-news-msg]").text_content(), page.locator("[data-news-msg]").text_content())
        add("2026-10-20", "CPI", time="25:99")
        check(f"{tag} 1 เวลาผิดรูปแบบ → ไม่บันทึก + เตือน", len(P38.settings_db(page)["newsEvents"]) == n0 and "HH:MM" in page.locator("[data-news-msg]").text_content())
        page.locator('[data-news-row="2026-10-15|NFP"] [data-news-time]').fill("19:40"); page.locator('[data-news-row="2026-10-15|NFP"] [data-news-time]').press("Tab"); page.wait_for_timeout(900)
        ev = [e for e in P38.settings_db(page)["newsEvents"] if e["date"] == "2026-10-15"][0]
        check(f"{tag} 1 แก้เวลาแถวเดิมได้ (19:40) บันทึกทันที", ev["time"] == "19:40", json.dumps(ev))
        page.wait_for_timeout(600)
        shot(page, f"st1-settings-news-{label.replace('px','')}.png", "#newsSetSec")
        # เก่าเกิน 30 วัน ซ่อน (ไม่ลบ)
        js(page, "()=>{ const B=getBook('main'); B.settings.newsEvents.push({date:'2026-08-01', kind:'CPI', time:'19:30'}); saveBook('main'); newsSetRender(); }"); page.wait_for_timeout(900)
        check(f"{tag} 1 วันที่ผ่านไปเกิน 30 วัน ซ่อนจากรายการ แต่ยังอยู่ใน settings", page.locator('[data-news-row="2026-08-01|CPI"]').count() == 0 and any(e["date"] == "2026-08-01" for e in P38.settings_db(page)["newsEvents"]))
        page.locator('[data-news-row="2026-10-15|NFP"] [data-news-del]').click(); page.wait_for_timeout(900)
        check(f"{tag} 1 ลบแถวได้", page.locator('[data-news-row="2026-10-15|NFP"]').count() == 0 and not any(e["date"] == "2026-10-15" for e in P38.settings_db(page)["newsEvents"]))
        if w < 600:
            bad = overflow(page, ["#newsSetSec", "#newsSet"])
            check(f"{tag} 1 390px ส่วนวันข่าวไม่ล้นแนวนอน", not bad, json.dumps(bad))
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


# ───────────────────────── 2-4 Sat: ช่วงงด · R:R · TP2 ─────────────────────────
def sat_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = P37.launch(pw, w, h)
    try:
        p5.goto_sat(page); p36.clean(page, "Long"); P37.go_sat(page)
        # ── 2 ช่วงงด CPI 19:30 (1 ต.ค.) → 18:30–20:00
        set_news(page, [{"date": "2026-10-01", "kind": "CPI", "time": "19:30"}])
        idea = idea_doc()
        fresh(page, idea)
        set_clock(page, "2026-10-01T11:29:00Z")   # 18:29
        c = calc(page, idea)
        check(f"{tag} 2 18:29 (ก่อนช่วงงด) → ready · ไม่มีเหตุผลบล็อก", c["ready"] is True and not c["news"] and not c["rr"], json.dumps(c, ensure_ascii=False))
        n0 = n_trades(page)
        js(page, "()=>satV3SaveReadyAccounts('iD')"); page.wait_for_timeout(500)
        check(f"{tag} 2 18:29 บันทึก order ได้", n_trades(page) == n0 + 1, f"{n0} → {n_trades(page)}")
        # ที่ 18:30 (เริ่มช่วงงด)
        fresh(page, idea)
        set_clock(page, "2026-10-01T11:30:00Z")
        c = calc(page, idea)
        want = "ช่วงข่าว CPI 18:30–20:00 — งดเปิดไม้ใหม่ (เปิดได้หลัง 20:00)"
        check(f"{tag} 2 18:30 → บล็อก + เหตุผลมีช่วงเวลา · ไม่ ready", c["ready"] is False and c["news"] == want, json.dumps(c, ensure_ascii=False))
        P37.go_sat(page); P37.open_plan(page)
        panel = page.locator("#satV3Panel").text_content()
        check(f"{tag} 2 การ์ดแผนแสดงข้อความช่วงข่าวต่อบัญชี · ไม่มีปุ่ม 'รวมด้วย (นอกแผน)'", want in re.sub(r"\s+", " ", panel) and "รวมด้วย (นอกแผน)" not in panel and page.locator("#satV3Panel [data-news-block]").count() >= 1,
              f"blocks={page.locator('#satV3Panel [data-news-block]').count()}")
        shot(page, f"st1-plan-block-news-{label.replace('px','')}.png", "#satV3Panel")
        n0, f0 = n_trades(page, "main"), n_trades(page, "fam")
        js(page, "()=>{ satV3SaveSlot('iD','main'); satV3SaveSlot('iD','fam'); satV3SaveOffplanAccount('iD','main'); satV3SaveReadyAccounts('iD'); try{ sat7dSaveOrder('iD','main'); }catch(e){} }"); page.wait_for_timeout(400)
        check(f"{tag} 2 เรียก satV3SaveSlot / SaveOffplan / SaveReady / sat7dSaveOrder ตรง ๆ ในช่วงงด → ไม่สร้างไม้", n_trades(page, "main") == n0 and n_trades(page, "fam") == f0, f"{n_trades(page,'main')} {n_trades(page,'fam')}")
        set_clock(page, "2026-10-01T12:59:00Z")   # 19:59
        c = calc(page, idea)
        check(f"{tag} 2 19:59 → ยังบล็อก", c["ready"] is False and c["news"] == want, json.dumps(c, ensure_ascii=False))
        set_clock(page, "2026-10-01T13:00:00Z")   # 20:00
        c = calc(page, idea)
        check(f"{tag} 2 20:00 (แท่งข่าวปิด) → ผ่าน · ready", c["ready"] is True and not c["news"], json.dumps(c, ensure_ascii=False))
        n0 = n_trades(page)
        js(page, "()=>satV3SaveReadyAccounts('iD')"); page.wait_for_timeout(500)
        check(f"{tag} 2 20:00 บันทึก order ได้", n_trades(page) == n0 + 1, f"{n0} → {n_trades(page)}")
        # ทุก asset
        set_clock(page, "2026-10-01T12:00:00Z")   # 19:00
        r = js(page, """()=>['XAUUSD','BTCUSD','S50','BRENT'].map(a=>{ const i={id:'z'+a, v3:true, asset:a, bias:'Long', entry:100, sl:98, tp:103, accts:{}, week:wpWeekKey(), conditions:[{id:'c', text:'x', tp_from:103, tp_to:106, active:true, saved:true}]};
            const c = satV3PlanAcctCalc(i,'main'); return {a, news:c.newsBlock, ready:c.ready}; })""")
        check(f"{tag} 2 ทุก asset ของ Sat (XAU · BTC · S50 · Brent) ติดช่วงงดเหมือนกัน · ไม่ ready", all(x["news"] == want and x["ready"] is False for x in r), json.dumps(r))
        # FOMC ไม่บล็อก
        set_news(page, [{"date": "2026-10-01", "kind": "FOMC", "time": "19:30"}])
        c = calc(page, idea)
        check(f"{tag} 2 FOMC ไม่งดเปิดไม้ (ข้อ 4 เช็กลิสต์อย่างเดียว) → ready", c["ready"] is True and not c["news"], json.dumps(c, ensure_ascii=False))
        # NFP 20:30 → 19:30–21:00
        set_news(page, [{"date": "2026-10-01", "kind": "NFP", "time": "20:30"}])
        set_clock(page, "2026-10-01T12:30:00Z")   # 19:30
        c = calc(page, idea)
        check(f"{tag} 2 NFP 20:30 → ช่วงงด 19:30–21:00", c["news"] == "ช่วงข่าว NFP 19:30–21:00 — งดเปิดไม้ใหม่ (เปิดได้หลัง 21:00)", json.dumps(c, ensure_ascii=False))
        set_news(page, [])
        # ── 3 R:R
        set_clock(page, "2026-10-01T05:00:00Z")
        def rr(bias, e, s, t, zone=(103, 106)):
            i = idea_doc(bias=bias, entry=e, sl=s, tp=t, zone=zone); i["conditions"][0].pop("kind", None)
            return calc(page, i)
        c = rr("Long", 100, 98, 103)
        check(f"{tag} 3 Long entry 100 / SL 98 / TP 103 → R:R 1.5 ผ่าน (ready)", c["ready"] is True and not c["rr"], json.dumps(c, ensure_ascii=False))
        c = rr("Long", 100, 98, 102.9)
        check(f"{tag} 3 TP 102.9 → R:R 1.45 บล็อก · ข้อความ 'R:R 1.4 ต่ำกว่า 1.5 — ปรับ Entry / Stop / TP' (ไม่ปัดขึ้นเป็น 1.5)", c["ready"] is False and c["rr"] == "R:R 1.4 ต่ำกว่า 1.5 — ปรับ Entry / Stop / TP", json.dumps(c, ensure_ascii=False))
        c = rr("Short", 100, 102, 97)
        check(f"{tag} 3 Short entry 100 / SL 102 / TP 97 ถูกฝั่ง → R:R 1.5 ผ่าน (ไม่มีเหตุผล R:R)", not c["rr"], json.dumps(c, ensure_ascii=False))
        c = rr("Short", 100, 102, 97.1)
        check(f"{tag} 3 Short TP 97.1 → 1.45 บล็อก", c["rr"].startswith("R:R 1.4 ต่ำกว่า 1.5"), json.dumps(c, ensure_ascii=False))
        c = rr("Long", 100, 98, 99)
        check(f"{tag} 3 Long แต่ TP ต่ำกว่า Entry (ผิดฝั่ง) → บล็อก", c["ready"] is False and "ผิดฝั่ง" in c["rr"], json.dumps(c, ensure_ascii=False))
        c = rr("Short", 100, 102, 101)
        check(f"{tag} 3 Short แต่ TP สูงกว่า Entry (ผิดฝั่ง) → บล็อก", c["ready"] is False and "ผิดฝั่ง" in c["rr"], json.dumps(c, ensure_ascii=False))
        c = rr("Long", 100, 98, None)
        check(f"{tag} 3 ไม่มี TP แรก → บล็อก 'ต้องมี TP แรกก่อน — R:R ขั้นต่ำ 1.5'", c["ready"] is False and c["rr"] == "ต้องมี TP แรกก่อน — R:R ขั้นต่ำ 1.5", json.dumps(c, ensure_ascii=False))
        # บันทึกจริง: R:R ต่ำ → SaveSlot ไม่สร้างไม้ · ปุ่มบันทึกปิด · ไม่มี 'รวมด้วย'
        low = idea_doc(entry=2410, sl=2400, tp=2424.9)
        fresh(page, low)
        panel = page.locator("#satV3Panel").text_content()
        n0 = n_trades(page)
        js(page, "()=>{ satV3SaveSlot('iD','main'); satV3SaveOffplanAccount('iD','main'); satV3SaveReadyAccounts('iD'); }"); page.wait_for_timeout(400)
        check(f"{tag} 3 R:R 1.49 → เรียกบันทึกตรง ๆ ไม่สร้างไม้ · ไม่มีปุ่ม 'รวมด้วย (นอกแผน)' · มีข้อความ R:R ต่อบัญชี", n_trades(page) == n0 and "รวมด้วย (นอกแผน)" not in panel and page.locator("#satV3Panel [data-rr-block]").count() >= 1, f"{n_trades(page)} {page.locator('#satV3Panel [data-rr-block]').count()}")
        bad_el = page.locator("#satV3Panel [data-rr-row] [data-rr]").first
        check(f"{tag} 3 ตัวเลข R:R แสดงแดง (R:R 1.4) เมื่อ < 1.5", bad_el.get_attribute("data-rr") == "bad" and "R:R 1.4" in bad_el.text_content(), bad_el.text_content())
        col_bad = bad_el.evaluate("e=>getComputedStyle(e).color")
        shot(page, f"st1-plan-rr-bad-{label.replace('px','')}.png", "#satV3Panel")
        ok = idea_doc(entry=2410, sl=2400, tp=2425)
        fresh(page, ok)
        good_el = page.locator("#satV3Panel [data-rr-row] [data-rr]").first
        col_good = good_el.evaluate("e=>getComputedStyle(e).color")
        check(f"{tag} 3 R:R 1.5 แสดงเขียว (data-rr=ok · สีต่างจากแดง)", good_el.get_attribute("data-rr") == "ok" and "R:R 1.5" in good_el.text_content() and col_good != col_bad, f"{good_el.text_content()} {col_good} vs {col_bad}")
        # ── 4 TP2
        tp = js(page, """()=>({ L:[satV3TpNear({tp_from:103,tp_to:106},'Long'), satV3TpFar({tp_from:103,tp_to:106},'Long')], Lr:[satV3TpNear({tp_from:106,tp_to:103},'Long'), satV3TpFar({tp_from:106,tp_to:103},'Long')],
            S:[satV3TpNear({tp_from:97,tp_to:94},'Short'), satV3TpFar({tp_from:97,tp_to:94},'Short')], one:satV3TpFar({tp_from:103,tp_to:null},'Long'), same:satV3TpFar({tp_from:103,tp_to:103},'Long'), none:satV3TpFar({tp_from:null,tp_to:null},'Long'), nocond:satV3TpFar(null,'Long') })""")
        check(f"{tag} 4 Long zone 103–106 → TP1 103 · TP2 106 (กรอกกลับด้านก็เหมือนเดิม) · Short zone 97–94 → TP1 97 · TP2 94", tp["L"] == [103, 106] and tp["Lr"] == [103, 106] and tp["S"] == [97, 94], json.dumps(tp))
        check(f"{tag} 4 zone จุดเดียว / ไม่มี zone / ไม่มีข้อ → TP2 ว่าง", tp["one"] is None and tp["same"] is None and tp["none"] is None and tp["nocond"] is None, json.dumps(tp))
        line = re.sub(r"[\s,]+", " ", page.locator("#satV3Panel [data-tp-plan]").first.text_content())
        check(f"{tag} 4 บรรทัดสั่งงาน: 'TP1 2425 ออก 50% → เลื่อน Stop มา 2410 · TP2 2440 ส่วนที่เหลือ'", re.sub(r"(\d) (\d{3})", r"\1\2", line).strip() == "TP1 2425 ออก 50% → เลื่อน Stop มา 2410 · TP2 2440 ส่วนที่เหลือ", line)
        nz = idea_doc(entry=2410, sl=2400, tp=2425, zone=(2425, None))
        fresh(page, nz)
        line = re.sub(r"\s+", " ", page.locator("#satV3Panel [data-tp-plan]").first.text_content())
        check(f"{tag} 4 ไม่มี TP2 → 'ส่วนที่เหลือ: ตามแผน'", line.endswith("ส่วนที่เหลือ: ตามแผน") and "TP2" not in line, line)
        shot(page, f"st1-plan-rr-{label.replace('px','')}.png", "#satV3Panel")
        fresh(page, ok)
        js(page, "()=>satV3SaveReadyAccounts('iD')"); page.wait_for_timeout(500)
        t = js(page, "()=>getBook('main').trades.filter(t=>t.port==='satB').slice(-1)[0]")
        check(f"{tag} 4 ไม้ที่บันทึกมี tp = 2425 · tp2 = 2440 (ขอบไกลของ zone)", t and t["tp"] == 2425 and t.get("tp2") == 2440, json.dumps(t))
        P37.go_sat(page); P37.open_plan(page)
        row = re.sub(r"[\s,]+", " ", page.locator("#satV3Panel").text_content())
        check(f"{tag} 4 แถวไม้ Sat แสดง 'TP1 … · TP2 …'", "TP1 2425 · TP2 2440" in re.sub(r"(\d) (\d{3})", r"\1\2", row), row[:300])
        js(page, "()=>{ const t = getBook('main').trades.filter(t=>t.port==='satB').slice(-1)[0]; t.status='open'; saveBook('main'); render(); }"); page.wait_for_timeout(300)
        row = re.sub(r"[\s,]+", " ", page.locator("#satV3Panel").text_content())
        check(f"{tag} 4 ไม้เปิดอยู่ก็แสดง 'TP1 · TP2' เหมือนกัน", "TP1 2425 · TP2 2440" in re.sub(r"(\d) (\d{3})", r"\1\2", row), row[:300])
        # ไม้เก่าไม่มี tp2
        p36.clean(page, "Long")
        p36.mk_first(page, tid="told", sl=2390)
        P37.go_sat(page); P37.open_plan(page)
        row = re.sub(r"\s+", " ", page.locator("#satV3Panel").text_content())
        old = js(page, "()=>getBook('main').trades.find(t=>t.id==='told')")
        check(f"{tag} 4 ไม้เก่าไม่มี tp2 → แสดง 'TP 2460' เดิม ไม่ error", "tp2" not in old and "TP 2,460" in row.replace("2460", "2,460") and not pe, row[:200] + json.dumps(pe))
        # makeTradeObject: แก้ไม้เดิมไม่ทำ tp2 หาย
        t2 = js(page, "()=>makeTradeObject({id:'z', date:thaiToday(), sym:'XAUUSD', port:'satB', bias:'Long', entry:100, sl:98, tp:103, qty:1, mult:1, cur:'USD', status:'plan', prevTrade:{tp2:106, port:'satB'}})")
        check(f"{tag} 4 แก้ไม้ที่มี tp2 (prevTrade) → tp2 ยังอยู่", t2.get("tp2") == 106, json.dumps(t2.get("tp2")))
        if w < 600:
            bad = overflow(page, ["#satV3Panel"])
            check(f"{tag} 4 390px หน้า Sat ไม่ล้นแนวนอน", not bad, json.dumps(bad))
        check(f"{tag} 2-4 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


# ───────────────────────── 5 Today ─────────────────────────
def today_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = P39.launch(pw, w, h, doc=P38.doc38(clean=True), clean=True, iso="2026-10-14T03:00:00Z")
    try:
        held = T("tx", "satB", "open", sym="XAUUSD", entry=2400, sl=2390, qty=0.1, cur="USD", date="2026-10-13", openedAt="2026-10-13")
        def state(iso, events, trades):
            js(page, "([ev,tr])=>{ const B=getBook('main'); B.settings.newsEvents = ev; B.trades = tr; saveBook('main'); }", [events, trades])
            set_clock(page, iso)
            js(page, "()=>{ switchTab('today'); todayRefresh(); }"); page.wait_for_timeout(350)
            return {"r": P38.kinds(page, "r"), "a": P38.kinds(page, "a"), "b": P38.kinds(page, "b")}
        CPI = [{"date": "2026-10-14", "kind": "CPI", "time": "19:30"}]
        s = state("2026-10-14T03:00:00Z", CPI, [held])
        txt = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="news"]').first.text_content()) if page.locator('.tdRow[data-kind="news"]').count() else ""
        check(f"{tag} 5 วัน CPI + มีไม้ Sat เปิด → แถวด่วน 📰 พร้อมเช็กลิสต์ (ยกเลิก limit · Stop มาจุดเข้า · ถือตามกฎ · เช็ก Stop ที่ broker)",
              s["r"].count("news") == 1 and "CPI" in txt and "19:30" in txt and "ยกเลิก limit ที่ค้าง" in txt and "Stop มาจุดเข้า" in txt and "ถือตามกฎ" in txt and "Stop ที่ broker" in txt and "XAU" in txt, json.dumps(s) + txt)
        shot(page, f"st1-today-news-{label.replace('px','')}.png")
        if w < 600:
            bad = overflow(page, [".tdRow[data-kind='news']", "#todayPanel"]) if page.locator("#todayPanel").count() else overflow(page, [".tdRow[data-kind='news']"])
            check(f"{tag} 5 390px แถวข่าวไม่ล้นแนวนอน", not bad, json.dumps(bad))
        page.locator('.tdRow[data-kind="news"]').first.click(); page.wait_for_timeout(500)
        check(f"{tag} 5 แตะแถว = ไปหน้า Sat (แผงไม้)", js(page, "()=>activeTab") == "plan", js(page, "()=>activeTab"))
        s = state("2026-10-14T03:00:00Z", CPI, [])
        txt = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="news"]').first.text_content()) if page.locator('.tdRow[data-kind="news"]').count() else ""
        check(f"{tag} 5 วัน CPI ไม่มีไม้ → แถวกลุ่มภายในสัปดาห์ 1 บรรทัด 'งดเปิดไม้ใหม่ 18:30–20:00' (ไม่ด่วน)", s["a"].count("news") == 1 and s["r"].count("news") == 0 and "งดเปิดไม้ใหม่ 18:30–20:00" in txt, json.dumps(s) + txt)
        s = state("2026-10-14T12:59:00Z", CPI, [held])
        check(f"{tag} 5 19:59 ยังมีแถว (ข่าว + 30 นาที = 20:00)", s["r"].count("news") == 1, json.dumps(s))
        s = state("2026-10-14T13:00:00Z", CPI, [held])
        check(f"{tag} 5 20:00 → แถวหาย (มีไม้)", "news" not in s["r"] + s["a"] + s["b"], json.dumps(s))
        s = state("2026-10-14T13:00:00Z", CPI, [])
        check(f"{tag} 5 20:00 → แถวหาย (ไม่มีไม้)", "news" not in s["r"] + s["a"] + s["b"], json.dumps(s))
        s = state("2026-10-13T03:00:00Z", CPI, [held])
        check(f"{tag} 5 วันก่อน CPI (13 ต.ค.) → ยังไม่มีแถว (CPI ขึ้นเฉพาะวันข่าว)", "news" not in s["r"] + s["a"] + s["b"], json.dumps(s))
        FO = [{"date": "2026-10-29", "kind": "FOMC", "time": "01:00"}]
        s = state("2026-10-28T03:00:00Z", FO, [held])
        txt = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="news"]').first.text_content()) if page.locator('.tdRow[data-kind="news"]').count() else ""
        check(f"{tag} 5 FOMC วันที่ 29 01:00 → แถวขึ้นตั้งแต่วันที่ 28 (มีไม้) พร้อมเช็กลิสต์", s["r"].count("news") == 1 and "FOMC" in txt and "01:00" in txt, json.dumps(s) + txt)
        s = state("2026-10-28T03:00:00Z", FO, [])
        check(f"{tag} 5 FOMC ไม่มีไม้ → ไม่มีแถว (FOMC ไม่งดเปิดไม้)", "news" not in s["r"] + s["a"] + s["b"], json.dumps(s))
        s = state("2026-10-28T18:30:00Z", FO, [held])   # 29 ต.ค. 01:30
        check(f"{tag} 5 หลัง 01:30 (ข่าว + 30 นาที) → แถวหาย", "news" not in s["r"] + s["a"] + s["b"], json.dumps(s))
        s = state("2026-10-14T03:00:00Z", [], [held])
        check(f"{tag} 5 ไม่มีวันข่าว → ไม่มีแถว (ปกติ = เงียบ)", "news" not in s["r"] + s["a"] + s["b"], json.dumps(s))
        s = state("2026-10-14T03:00:00Z", [{"date": "2026-10-14", "kind": "NFP", "time": "20:30"}], [held])
        txt = re.sub(r"\s+", " ", page.locator('.tdRow[data-kind="news"]').first.text_content()) if page.locator('.tdRow[data-kind="news"]').count() else ""
        check(f"{tag} 5 NFP 20:30 (นอก DST) → แถวด่วนแสดงเวลา 20:30", s["r"].count("news") == 1 and "NFP" in txt and "20:30" in txt, json.dumps(s) + txt)
        pend = js(page, "()=>getBook('main').trades.filter(t=>t.port==='satB').length")
        check(f"{tag} 5 ไม้ที่ order รอเข้า (status plan) ก็นับ → แถวด่วน", state("2026-10-14T03:00:00Z", CPI, [dict(held, status="plan")])["r"].count("news") == 1)
        # ไม่นับในเพดานแถว Ideas (ID4) — แถวข่าวไม่ใช่ kind idea-*
        check(f"{tag} 5 แถวข่าวไม่ใช่แถว Ideas (kind=news · ไม่นับเพดาน 2 แถว)", not any(k.startswith("idea-") for k in ["news"]))
        check(f"{tag} 5 ไม่มี console error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            settings_tests(pw, w, h, label)
            sat_tests(pw, w, h, label)
            today_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 51 / ST1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
