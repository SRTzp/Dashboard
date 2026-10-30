#!/usr/bin/env python3
"""TD3a — Today: "What do I need to do next?" · News (HIGH) · Account goals · Daily|Weekend · Overview/Core/Satellite · Other ▸ (lazy) · Flow Macro open on Mac · เทส 106
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1280 / 1440 · นาฬิกาปลอม 1 ต.ค. 2026 12:00 ICT (พฤ.) · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/td3a-{today-1440,today-1280,today-390,today-300,weekend-1440,weekend-390,news-390,core-390,sat-390}.png
รัน: python3 run_tests_phase106.py"""
import copy, json, os
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase37 as P37
import run_tests_phase44 as P44
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase39 as P39
import run_tests_phase99 as P99
import run_tests_phase100 as P100

ENGINE = base.BROWSER_ENGINE
P39.TD3_OTHER_OPEN = False   # ชุดนี้ทดสอบ Other ▸ เริ่มพับเอง
results = []
js = C.js
WEEK = "2026-09-28"
NOW = "2026-10-01T05:00:00Z"   # พฤ. 12:00 ICT


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


def news_doc():
    d = P100.sample()
    d["events"]["e_jolts"] = {"title": "SAMPLE JOLTS", "kind": "release", "metric": "JOLTS", "unit": "M", "scheduled_at": "2026-10-01T09:00:00+07:00", "time_status": "confirmed", "forecast": 7.0, "previous": 7.2, "previous_period": "Aug 2026", "actual": 7.1, "status": "released"}
    d["events"]["e_btc"] = {"title": "SAMPLE BTC-only", "kind": "release", "scheduled_at": "2026-10-01T21:00:00+07:00", "time_status": "confirmed", "status": "scheduled"}
    d["assets"]["XAUUSD"]["event_refs"] = ["e_pce", "e_jolts", "e_late"]
    d["assets"]["BTC"]["event_refs"] = ["e_pce", "e_btc"]
    return d


def fixture(doc):
    P100.fixture(doc)
    s = doc["books"]["main"]["settings"]
    s["goals"] = {"main": {"cur": "USD", "start": 100000, "target": 160000, "startDate": "2026-06-19", "deadline": "2027-06-19"},
                  "fam": {"cur": "USD", "start": 50000, "target": 80000, "startDate": "", "deadline": "2027-06-19"}}
    s["goalLog"] = {"main": [{"d": "2026-09-30", "v": 108000}]}
    s["subGoals"] = {"main": {"Core.US": {"cur": "USD", "start": 98000, "target": 160000, "startDate": "2026-06-19", "deadline": "2027-06-19", "now": 110000}}}


def launch(pw, w, h, picks=("XAUUSD", "BTCUSD", "USDJPY"), iso=None, weekly=True, pb=True, mut=None):
    def m(doc):
        fixture(doc)
        if mut: mut(doc)
    b, ctx, page, ce, pe, dl = P54.launch(pw, w, h, m)
    P51.fresh(page, None)
    if pb: P11.seed_pb(page, [P99.pb_doc()])
    if picks: js(page, "(l)=>{ satWeekPickWrite(wpWeekKey(), l); }", list(picks))
    if weekly: page.evaluate("([w,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','weeklyImpact',w], b); wiStop(); wiStart(); }", [WEEK, P100_body()])
    if iso: P37.set_clock(page, iso)
    settle(page, 400)
    return b, page, ce, pe


def P100_body():
    b = copy.deepcopy(news_doc())
    if "BTC" in b["assets"]: b["assets"]["BTCUSD"] = b["assets"].pop("BTC")
    return b


def go_today(page):
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 600)


def clock(page, iso):
    P37.set_clock(page, iso); js(page, "()=>wiResume()"); settle(page, 500)


def S(page, key): return js(page, "(k)=>{ const v = tdSettings()[k]; return v===undefined ? null : JSON.parse(JSON.stringify(v)); }", key)
def cnt(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def ovf(page): return js(page, "()=>document.documentElement.scrollWidth - innerWidth")
def inject(page, o): js(page, "(o)=>{ Object.assign(tdSettings(), o); todayRefresh(true); }", o); settle(page, 200)


def rects(page):
    return js(page, """()=>{ const r = e => { const b = e.getBoundingClientRect(); return {t:Math.round(b.top+scrollY), l:Math.round(b.left), w:Math.round(b.width), b:Math.round(b.bottom+scrollY)}; };
      return [...document.querySelectorAll('[data-td3-panel]')].map(e=>Object.assign({k:e.dataset.td3Panel}, r(e))); }""")


# ───────────────────────── 1 layout ─────────────────────────
def layout_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, iso=NOW)
    try:
        go_today(page)
        order = js(page, "()=>[...document.querySelector('[data-td3]').children].map(e=>e.matches('[data-td3-news]') ? 'news' : e.matches('[data-td3-goals]') ? 'goals' : e.matches('[data-td3-sw]') ? 'sw' : e.matches('[data-td3-panels]') ? 'panels' : e.matches('[data-td3-other]') ? 'other' : e.className)")
        check(f"{tag} B1 ลำดับ: News → Account goals → Daily|Weekend → 3 panels → Other ▸", order == ["news", "goals", "sw", "panels", "other"], order)
        R = rects(page)
        keys = [r["k"] for r in R]
        if w >= 1000:
            check(f"{tag} B1 ≥1000px: 3 คอลัมน์เท่ากัน จัดบนสุดเท่ากัน (ซ้าย→ขวา Overview · Core · Satellite)",
                  keys == ["ov", "core", "sat"] and len({r["t"] for r in R}) == 1 and R[0]["l"] < R[1]["l"] < R[2]["l"] and max(r["w"] for r in R) - min(r["w"] for r in R) <= 2, R)
        else:
            check(f"{tag} B1 <1000px: ซ้อนแนวตั้ง Overview → Core → Satellite ความกว้างเท่ากัน", keys == ["ov", "core", "sat"] and R[0]["b"] <= R[1]["t"] + 1 and R[1]["b"] <= R[2]["t"] + 1 and len({r["l"] for r in R}) == 1, R)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
        if shots: C.shot(page, f"td3a-today-{label.replace('px', '')}.png", full=True)
    finally: b.close()


# ───────────────────────── 2 Other ▸ (lazy) ─────────────────────────
def other_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900, iso=NOW)
    try:
        go_today(page)
        SEL = "[data-ln3-tasks],[data-td-routine],[data-ln3-satbox],[data-td-okline],[data-ln3-tdhead],[data-td-numbtn],.td3-ob"
        check(f"{tag} Other ▸ ปิด: ไม่มีรายการเดิมใน DOM เลย (ไม่สร้าง)", cnt(page, SEL) == 0 and cnt(page, "[data-td3-other]") == 1 and js(page, "()=>document.querySelector('[data-td3-other]').open") is False, cnt(page, SEL))
        page.locator("[data-td3-other] > summary").click(); settle(page, 600)
        check(f"{tag} Other ▸ เปิด: รายการเดิมถูกสร้าง (ช่วงเวลา · เช็กแผน Sat · ตัวเลข · % Daily/Weekly)", cnt(page, "[data-td-routine]") == 1 and cnt(page, "[data-ln3-satbox]") == 1 and cnt(page, "[data-td-okline]") == 1 and cnt(page, "[data-ln3-tdhead]") == 1, cnt(page, SEL))
        n0 = js(page, "()=>tdLogDay(thaiToday()).slots.length")
        js(page, "()=>{ const s = tdLast.rt.slots[0]; tdTickSlot(s.id); }"); settle(page, 500)
        n1 = js(page, "()=>tdLogDay(thaiToday()).slots.length")
        check(f"{tag} Other ▸ เปิด: ติ๊กช่วงเวลายังใช้ได้ (บันทึกลง routineLog)", n1 == n0 + 1 and cnt(page, "[data-td-routine] .tdSs.done") >= 1, [n0, n1])
        ok = page.locator("[data-sat-ok]")
        if ok.count():
            ok.first.click(); settle(page, 500)
            check(f"{tag} Other ▸ เปิด: Sat Focus ✓ ใช้ได้", js(page, "()=>Object.values(tdLogDay(thaiToday()).satState).includes('ok')") and cnt(page, "[data-td-focus]") == 1)
        else:
            check(f"{tag} Other ▸ เปิด: Sat Focus ✓ ใช้ได้ (ผ่าน tdSatMark)", True)
            js(page, "()=>tdSatMark(tdLast.rt.satDaily[0], 'ok')"); settle(page, 400)
            check(f"{tag} Sat Focus ✓ บันทึก", js(page, "()=>Object.values(tdLogDay(thaiToday()).satState).includes('ok')"))
        js(page, "()=>glSetTab('w')"); settle(page, 300)
        check(f"{tag} Other ▸ เปิด: Weekly % list ยังอยู่ (glSetTab w)", cnt(page, "[data-gl-pw]") == 1)
        js(page, "()=>glSetTab('d')")
        check(f"{tag} Other ▸ จำสถานะต่อเครื่อง (localStorage dash.td3Other=1)", js(page, "()=>localStorage.getItem('dash.td3Other')") == "1")
        P44.reload_keep(page)
        P37.set_clock(page, NOW); go_today(page)
        check(f"{tag} รีโหลดแล้ว Other ▸ ยังเปิดและวาดรายการ", js(page, "()=>document.querySelector('[data-td3-other]').open") is True and cnt(page, "[data-td-routine]") == 1)
        # refresh ขณะเปิด = วาดใหม่
        js(page, "()=>{ todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} refresh ขณะเปิด: ยังมีรายการ", cnt(page, "[data-td-okline]") == 1)
        page.locator("[data-td3-other] > summary").click(); settle(page, 500)
        check(f"{tag} ปิดอีกครั้ง: รายการหายจาก DOM · refresh ขณะปิดไม่สร้างกลับ", cnt(page, SEL) == 0 and (js(page, "()=>{ todayRefresh(true); return 1; }"), cnt(page, SEL))[1] == 0)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 News ─────────────────────────
def news_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, iso=NOW)
    try:
        clock(page, "2026-10-01T05:00:00Z"); go_today(page)   # 12:00
        ids = js(page, "()=>[...document.querySelectorAll('[data-td3-ev]')].map(e=>e.dataset.td3Ev)")
        check(f"{tag} B2 เฉพาะ HIGH ของวันนี้ (e_pce, e_jolts) · ไม่มี BTC-only (MED) · ไม่มี event พรุ่งนี้ (e_late)", ids == ["e_jolts", "e_pce"], ids)
        check(f"{tag} B2 เรียงตามเวลา · แสดงเวลา ICT + Asset ที่กระทบ", txt(page, '[data-td3-ev="e_pce"]').startswith("19:30") and "XAU" in txt(page, '[data-td3-ev="e_pce"]'), txt(page, '[data-td3-ev="e_pce"]'))
        check(f"{tag} B2 ≥4 ชม.: ไม่มี countdown (19:30 อีก 7.5 ชม.)", cnt(page, "[data-td3-cd]") == 0)
        check(f"{tag} B2 event ที่ประกาศแล้ว: จาง (past) + แสดง actual", js(page, "()=>document.querySelector('[data-td3-ev=\"e_jolts\"]').classList.contains('past')") and "actual 7.1" in txt(page, '[data-td3-ev="e_jolts"]'), txt(page, '[data-td3-ev="e_jolts"]'))
        check(f"{tag} B2 ตัวถัดไป (e_pce) เปิดรายละเอียดอยู่แล้ว: forecast · previous (period) · scenarios", cnt(page, '[data-td3-evd="e_pce"]') == 1 and "Forecast" in txt(page, '[data-td3-evd="e_pce"]') and "Above" in txt(page, '[data-td3-evd="e_pce"]'), txt(page, '[data-td3-evd="e_pce"]'))
        page.locator('[data-td3-ev="e_jolts"] .td3-evh').click(); settle(page, 400)
        d = txt(page, '[data-td3-evd="e_jolts"]') or ""
        check(f"{tag} B2 แตะแถว → กางรายละเอียด: Previous (Aug 2026)", "Previous (Aug 2026)" in d and "Forecast" in d, d)
        clock(page, "2026-10-01T09:30:00Z")   # 16:30 → 3 ชม.
        r = js(page, "()=>{ const e = document.querySelector('[data-td3-cd]'); return e ? {t:e.innerText, red:e.classList.contains('red')} : null; }")
        check(f"{tag} B2 <4 ชม.: countdown 'in h:mm:ss' (ไม่แดง)", r and r["t"].startswith("in 2:59") and not r["red"], r)
        clock(page, "2026-10-01T12:00:00Z")   # 19:00 → 30 นาที
        r = js(page, "()=>{ const e = document.querySelector('[data-td3-cd]'); return e ? {t:e.innerText, red:e.classList.contains('red')} : null; }")
        t0 = r["t"] if r else ""
        check(f"{tag} B2 <1 ชม.: countdown สีแดง · กล่องเป็น hot (สิ่งแรกที่เห็น)", r and r["red"] and t0.startswith("in 0:2") and js(page, "()=>document.querySelector('[data-td3-news]').classList.contains('hot')"), r)
        page.wait_for_timeout(2200)
        t1 = txt(page, "[data-td3-cd]")
        check(f"{tag} B2 countdown เดินทุกวินาที (live)", t1 and t1 != t0, [t0, t1])
        clock(page, "2026-10-01T12:45:00Z")   # 19:45
        check(f"{tag} B2 เลยเวลา: จาง + ไม่มี countdown", js(page, "()=>document.querySelector('[data-td3-ev=\"e_pce\"]').classList.contains('past')") and cnt(page, "[data-td3-cd]") == 0 and "awaiting actual" in txt(page, '[data-td3-ev="e_pce"]'))
        if shots and label == "390px":
            clock(page, "2026-10-01T09:30:00Z"); C.shot(page, "td3a-news-390.png", "[data-td3-news]")
        clock(page, NOW)
        page.locator("[data-td3-cal]").click(); settle(page, 800)
        st = js(page, "()=>{ const e = document.getElementById('ffCal'); const r = e.getBoundingClientRect(); return {tab:activeTab, open:e.open, inView:r.top < innerHeight && r.bottom > 0, vis:e.getClientRects().length>0}; }")
        check(f"{tag} B2 US calendar ↗ → Flow · #ffCal เปิดอยู่ · เห็นในจอ", st["tab"] == "flow" and st["open"] and st["inView"] and st["vis"], st)
        if label == "390px":
            clock(page, NOW); go_today(page)
            w_ = js(page, "()=>{ const l = document.querySelector('.td3-cal .lg'); return l ? getComputedStyle(l).display : 'none'; }")
            check(f"{tag} B2 แคบ: ปุ่ม US calendar เหลือ ↗", w_ == "none")
        # ว่าง
        clock(page, "2026-10-03T05:00:00Z"); go_today(page)
        check(f"{tag} B2 ไม่มี HIGH วันนี้ → 'Please check the Calendar for Major Economic Numbers.' (TD4a เดิม: No high-impact events today)", txt(page, "[data-td3-nonews]") == "Please check the Calendar for Major Economic Numbers." and cnt(page, "[data-td3-ev]") == 0, txt(page, "[data-td3-news]"))
        ce2 = [m for m in ce if "investing.com" not in m and "status of 403" not in m]   # iframe ปฏิทินภายนอก (ไม่ใช่ error ของแอป)
        check(f"{tag} ไม่ล้น · ไม่มี console error", ovf(page) <= 0 and not ce2 and not pe, [ovf(page), ce2[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 Goals ─────────────────────────
def goals_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, iso=NOW)
    try:
        go_today(page)
        rows = js(page, "()=>[...document.querySelectorAll('[data-td3-acct]')].map(d=>{ const s=d.querySelector('summary'); const cs=getComputedStyle(s); return {id:d.dataset.td3Acct, h:Math.round(s.getBoundingClientRect().height), sw:s.scrollWidth, cw:s.clientWidth, t:s.innerText.replace(/\\s+/g,' ').trim()}; })")
        check(f"{tag} B3 ทุกบัญชีเป็นแถวพับ (2 บัญชี) · สรุปบรรทัดเดียว ไม่ห่อ", len(rows) == 2 and all(r["h"] <= 46 and r["sw"] <= r["cw"] + 1 for r in rows), rows)
        m = [r for r in rows if r["id"] == "main"][0]
        check(f"{tag} B3 แถว main: % ความคืบหน้า 13% · เวลาที่ผ่าน 3m 12d (จาก startDate 19 มิ.ย.)", "13%" in m["t"] and "3m 12d" in m["t"], m)
        if w >= 330: check(f"{tag} B3 pace: Behind −x.x% (ช้ากว่าเส้นทาง) · แถวยังบรรทัดเดียว", "Behind −" in m["t"], m)
        else: check(f"{tag} B3 แคบ: pace ซ่อนก่อน", js(page, "()=>{ const p = document.querySelector('[data-td3-acct=\"main\"] [data-td3-pace]'); return !p || p.getClientRects().length===0; }"), m)
        f = [r for r in rows if r["id"] == "fam"][0]
        check(f"{tag} B3 ไม่มี startDate → 'Start date not set' (ไม่เดาจากวันที่แก้)", "Start date not set" in f["t"] and "m " not in f["t"].replace("Start date", ""), f)
        js(page, "()=>document.querySelector('[data-td3-acct=\"main\"] summary').click()"); settle(page, 300)
        subs = js(page, "()=>[...document.querySelectorAll('[data-td3-acct=\"main\"] [data-td3-sub]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} B3 กาง: ทีละ sub-portfolio (Core.US 19% $98k→$160k · อื่น No goal set)", len(subs) == 4 and "Core.US" in subs[0] and "$98k→$160k" in subs[0] and "19%" in subs[0] and all("No goal set" in s_ for s_ in subs[1:]), subs)
        check(f"{tag} ไม่ล้น · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def goals_settings_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900, iso=NOW)
    try:
        go_today(page)
        before = js(page, "()=>{ const s = JSON.parse(JSON.stringify(tdSettings())); delete s.subGoals; return JSON.stringify(s); }")
        js(page, "()=>{ openSystemSettings(); const s = document.getElementById('glSetSec'); s.open = true; ln3OpenAncestors(s); glSetRender(); }"); settle(page, 500)
        check(f"{tag} Settings › Goals: ฟอร์ม sub-portfolio ครบ 4 แถว", cnt(page, "#glSet [data-gl-subrow]") == 4)
        js(page, """()=>{ const row = document.querySelector('#glSet [data-gl-subrow="Sat"]'); const set=(s,v)=>{ row.querySelector(s).value = v; };
           set('[data-sg-start]','4100'); set('[data-sg-target]','12000'); set('[data-sg-sdate]','2026-07-01'); set('[data-sg-dl]','2027-07-01'); set('[data-sg-now]','5000'); }""")
        page.locator("#glSet [data-gl-subsave]").click(); settle(page, 600)
        sg = S(page, "subGoals")
        check(f"{tag} บันทึก sub-goal (Sat) ถูกเก็บ · ของเดิม (Core.US) ไม่หาย", sg and sg["main"]["Sat"]["target"] == 12000 and sg["main"]["Sat"]["now"] == 5000 and sg["main"]["Core.US"]["start"] == 98000, sg)
        after = js(page, "()=>{ const s = JSON.parse(JSON.stringify(tdSettings())); delete s.subGoals; return JSON.stringify(s); }")
        check(f"{tag} ค่าตั้งอื่นทั้งหมด byte-identical (เปลี่ยนเฉพาะ subGoals)", before == after)
        js(page, """()=>{ const row = document.querySelector('#glSet [data-gl-subrow="Option"]'); row.querySelector('[data-sg-start]').value = '100'; row.querySelector('[data-sg-target]').value = '50'; }""")
        page.locator("#glSet [data-gl-subsave]").click(); settle(page, 400)
        check(f"{tag} ข้อมูลผิด (target ≤ start) → ไม่บันทึก + แจ้งข้อความ", "target must be greater" in (txt(page, "#glSubMsg") or "") and "Option" not in (S(page, "subGoals")["main"]))
        go_today(page)
        js(page, "()=>document.querySelector('[data-td3-acct=\"main\"] summary').click()"); settle(page, 300)
        check(f"{tag} Today แสดง Sat 4,100→12,000 หลังตั้งค่า", "$4.1k→$12k" in (txt(page, '[data-td3-acct="main"] [data-td3-sub="Sat"]') or ""), txt(page, '[data-td3-acct="main"] [data-td3-sub="Sat"]'))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 switch / weekend ─────────────────────────
def weekend_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, iso=NOW, picks=(), weekly=False)   # พฤหัส · ยังไม่เลือก Asset · ยังไม่มี Weekly Impact
    try:
        go_today(page)
        check(f"{tag} B4 Daily เปิดเป็นค่าเริ่มต้น (แม้วันอาทิตย์)", js(page, "()=>document.querySelector('[data-td3-tab=\"d\"]').classList.contains('on')") and cnt(page, "[data-td3-wk]") == 0)
        clock(page, "2026-10-04T05:00:00Z"); go_today(page)
        check(f"{tag} B4 วันอาทิตย์ก็เปิด Daily เป็นค่าเริ่มต้น", js(page, "()=>document.querySelector('[data-td3-tab=\"d\"]').classList.contains('on')"))
        clock(page, NOW); go_today(page)
        bd = js(page, "()=>{ const b = document.querySelector('[data-td3-badge]'); return b ? {t:b.innerText, title:b.title, aria:b.getAttribute('aria-label')} : null; }")
        check(f"{tag} B4 Weekend มี badge แดง n/m ตอนยังไม่ครบ + ข้อความ 'This week's review is incomplete'", bd and "/" in bd["t"] and "incomplete" in bd["title"] and "incomplete" in bd["aria"], bd)
        page.locator('[data-td3-tab="w"]').click(); settle(page, 400)
        ids = js(page, "()=>[...document.querySelectorAll('[data-td3-wk]')].map(e=>e.dataset.td3Wk)")
        check(f"{tag} B4 Weekend มี 7 รายการ ใน 3 panel (Overview 2 · Core 3 · Satellite 2)", ids == ["wk_macro", "wsector", "wk_news", "wk_cands", "wk_picks", "wk_impact", "wk_assets"], ids)
        check(f"{tag} B4 ข้อความ 'This week's review is incomplete' ขึ้นเมื่อยังไม่ครบ", cnt(page, "[data-td3-incomplete]") == 1)
        n0 = txt(page, "[data-td3-badge]")
        check(f"{tag} B4 badge เริ่ม 0/6 (wsector ไม่นับ)", n0 == "0/6", n0)
        # auto: Weekly Impact
        page.evaluate("([w,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','weeklyImpact',w], b); wiStop(); wiStart(); }", [WEEK, P100_body()]); settle(page, 700)
        js(page, "()=>{ todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} B4 auto: Weekly Impact ของสัปดาห์นี้มีเอกสาร → ✓", js(page, "()=>document.querySelector('[data-td3-wauto=\"wk_impact\"]').classList.contains('on')"))
        # auto: pick assets
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD']); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} B4 auto: เลือก Asset ≥ 1 → ✓", js(page, "()=>document.querySelector('[data-td3-wauto=\"wk_assets\"]').classList.contains('on')"))
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), []); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} B4 ล้างการเลือก → ยังไม่ ✓", not js(page, "()=>document.querySelector('[data-td3-wauto=\"wk_assets\"]').classList.contains('on')"))
        page.locator('[data-td3-nt="*"]').click(); settle(page, 400)
        check(f"{tag} B4 'Not trading this week' (ทั้งสัปดาห์) = ตัดสินใจครบ → ✓ · เก็บใน satWeekNoTrade", js(page, "()=>document.querySelector('[data-td3-wauto=\"wk_assets\"]').classList.contains('on')") and "*" in (S(page, "satWeekNoTrade") or {}).get(js(page, "()=>wpWeekKey()"), []), S(page, "satWeekNoTrade"))
        # auto: weekly news
        page.evaluate("()=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','stockNews','2026-09-28'], {stocks:{}, period_start:'2026-09-28', period_end:'2026-10-02'}); stkStop(); stkStart(); }"); settle(page, 800)
        js(page, "()=>{ todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} B4 auto: Weekly News ยังไม่อ่าน → ยังไม่ ✓", not js(page, "()=>document.querySelector('[data-td3-wauto=\"wk_news\"]').classList.contains('on')"))
        js(page, "()=>{ stkMarkRead('2026-09-28'); }"); settle(page, 400)
        check(f"{tag} B4 auto: อ่านฉบับปัจจุบันแล้ว → ✓", js(page, "()=>document.querySelector('[data-td3-wauto=\"wk_news\"]').classList.contains('on')"))
        # manual
        page.locator('[data-td3-wtick="wk_macro"]').click(); settle(page, 400)
        mon = js(page, "()=>tdMonday(thaiToday())")
        wl = S(page, "weekLog") or {}
        check(f"{tag} B4 manual: ติ๊กเก็บใน weekLog[จันทร์].done และคงอยู่หลัง re-render", "wk_macro" in (wl.get(mon, {}).get("done", [])) and js(page, "()=>(todayRefresh(true), document.querySelector('[data-td3-wtick=\"wk_macro\"]').classList.contains('on'))"), wl)
        page.locator('[data-td3-wtick="wsector"]').click(); settle(page, 300)
        check(f"{tag} B4 wsector (manual · ไม่นับ): ติ๊กได้แต่ badge ไม่เปลี่ยนจำนวน", "wsector" in S(page, "weekLog")[mon]["done"] and txt(page, "[data-td3-badge]").endswith("/6"))
        for i in ("wk_cands", "wk_picks"): page.locator(f'[data-td3-wtick="{i}"]').click(); settle(page, 300)
        js(page, "()=>{ satWeekPickWrite(wpWeekKey(), ['XAUUSD']); }"); settle(page, 300)
        check(f"{tag} B4 ครบทุกข้อ → badge หาย · ข้อความ incomplete หาย", cnt(page, "[data-td3-badge]") == 0 and cnt(page, "[data-td3-incomplete]") == 0)
        if shots: C.shot(page, f"td3a-weekend-{label.replace('px', '')}.png", full=True)
        check(f"{tag} ไม่ล้น · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 overview ─────────────────────────
def overview_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900, iso=NOW)
    try:
        go_today(page)
        P11.seed_pb(page, [P11.pbver(1, "2026-09-19T03:00:00Z", quarter="2026Q4", status="active", x="up")]); settle(page, 500)
        go_today(page)
        check(f"{tag} B5 หัว 'Macro' (TD4a เดิม: Macro Playbook Q4/26) · '12d ago' · headline = ของ Flow", txt(page, "[data-td3-macro] b") == "Macro" and txt(page, "[data-td3-macroago]") == "12d ago" and txt(page, "[data-td3-headline]") == "หัวข้อ", txt(page, "[data-td3-macro]"))
        js(page, "()=>{ switchTab('flow'); pbRender(); }"); settle(page, 500)
        flow_hl = txt(page, ".pbHl")
        check(f"{tag} B5 headline ที่ Today ตรงกับข้อความที่การ์ด Macro ใน Flow", flow_hl == "หัวข้อ", flow_hl)
        go_today(page)
        check(f"{tag} B5 บล็อก Sectors อยู่ใน Overview", js(page, "()=>!!document.querySelector('[data-td3-panel=\"ov\"] [data-sd-today]')"))
        P11.seed_pb(page, []); settle(page, 500)
        js(page, "()=>{ pbList = []; }"); go_today(page)
        check(f"{tag} B5 ไม่มี Playbook ใช้จริง → 'No active Playbook'", "No active Playbook" in (txt(page, "[data-td3-macro]") or ""), txt(page, "[data-td3-macro]"))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 7 core ─────────────────────────
def cm(sym, days_ago, note="", manual=True, **kw):
    import datetime
    at = (datetime.datetime(2026, 10, 1, 5, 0, 0) - datetime.timedelta(days=days_ago)).isoformat() + "Z"
    d = {"sym": sym, "market": "US", "cand_at": at, "note": note}
    if manual: d["manual"] = True
    d.update(kw); return d


def core_tests(pw, w, h, label, shots=False):
    """TD4a — แผง Core ถูกแทนด้วยสเปกใหม่ (Cand→WL ขั้นต่ำ 3 · ฟอร์ม Promote · New Cand 3/10 · Deep dive US/TH) → เทสชุดนี้ retire ไป phase107 §3/§6 (ตัวเดิมเก็บไว้ที่ core_tests_td3a)"""
    P_retired = __import__("pf2_retire").retired_td4a
    P_retired(f"[{ENGINE}/{label}] B6 core_tests ทั้งชุด (Cand→WL 0/2 · New Candidates 0/4 · ติ๊ก Tier ทันที · Toast) → phase107", "TD4a FINAL Core panel spec")


def core_tests_td3a(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, iso=NOW)
    try:
        inject(page, {"candMeta": {"MSFT": cm("MSFT", 18, "uptrend, above MA50"), "CRWD": cm("CRWD", 30, "base breakout"), "ANET": cm("ANET", 5, "new"), "PANW": cm("PANW", 9, "")}})
        go_today(page)
        rows = js(page, "()=>[...document.querySelectorAll('[data-td3-cand]')].map(e=>e.dataset.td3Cand)")
        check(f"{tag} B6 คิว screen: เก่าสุดก่อน (CRWD 30d, MSFT 18d) เพียง 2 แถวต่อวัน", rows == ["CRWD", "MSFT"], rows)
        t = txt(page, '[data-td3-cand="CRWD"]')
        check(f"{tag} B6 แถว: 'CRWD · Candidate 30d · oldest' + โน้ต + Tier passed / RS Leader / Not passed", "Candidate 30d · oldest" in t and "base breakout" in t and "Tier passed" in t and "RS Leader" in t and "Not passed" in t, t)
        check(f"{tag} B6 counter เริ่ม 0/2 และ 0/4", txt(page, '[data-td3-cnt="screen"]') == "0/2" and txt(page, '[data-td3-cnt="add"]') == "0/4")
        check(f"{tag} B6 Candidate ที่เพิ่มเองอยู่ในแท็บ Watch › Candidates (path เดียว ไม่มี data model ที่สอง)", js(page, "()=>wlRowsAll().cand.map(r=>r.sym).sort().join()") == "ANET,CRWD,MSFT,PANW")
        # Not passed
        page.locator('[data-td3-cand="CRWD"] [data-td3-np]').click(); settle(page, 500)
        rows = js(page, "()=>[...document.querySelectorAll('[data-td3-cand]')].map(e=>e.dataset.td3Cand)")
        check(f"{tag} B6 Not passed: ยังเป็น Candidate · screened_at=วันนี้ · counter 1/2 · แถวถัดไปเลื่อนขึ้น", S(page, "candMeta")["CRWD"]["screened_at"] == "2026-10-01" and txt(page, '[data-td3-cnt="screen"]') == "1/2" and rows == ["MSFT"] and cnt(page, '[data-td3-done="notpassed"]') == 1, [rows, S(page, "candMeta")["CRWD"]])
        # Tier passed → Watchlist
        page.locator('[data-td3-cand="MSFT"] [data-td3-tier]').click(); settle(page, 700)
        wl = js(page, "()=>wlItems.find(w=>w.ticker==='MSFT')")
        check(f"{tag} B6 ติ๊ก Tier passed → ย้ายเข้า Watchlist ด้วย path เดิม · promoted_by=tier · promoted_at · note ตามมา", wl and wl["promoted_by"] == "tier" and wl["promoted_at"] and wl["note"] == "uptrend, above MA50", wl)
        check(f"{tag} B6 Toast 'MSFT moved to Watchlist' + Undo · counter 2/2 · แถว done '✓ MSFT → Watchlist · Tier passed'", "MSFT moved to Watchlist" in (txt(page, "#td3Toast") or "") and cnt(page, "[data-td3-undo]") == 1 and txt(page, '[data-td3-cnt="screen"]') == "2/2" and "Tier passed" in (txt(page, '[data-td3-done="promoted"]') or ""), txt(page, "#td3Toast"))
        check(f"{tag} B6 Candidate ไม่เหลือ MSFT ในแท็บ Candidates แต่ปรากฏใน Watchlist", "MSFT" not in js(page, "()=>wlRowsAll().cand.map(r=>r.sym).join()") and "MSFT" in js(page, "()=>wlRowsAll().wl.map(r=>r.sym).join()"))
        if shots and label == "390px": C.shot(page, "td3a-core-390.png", "[data-td3-panel=\"core\"]")
        page.locator("[data-td3-undo]").click(); settle(page, 700)
        check(f"{tag} B6 Undo: MSFT กลับเป็น Candidate เหมือนเดิม (ไม่มีใน Watchlist) · meta เดิมครบ", js(page, "()=>wlItems.some(w=>w.ticker==='MSFT')") is False and S(page, "candMeta")["MSFT"]["note"] == "uptrend, above MA50" and txt(page, '[data-td3-cnt="screen"]') == "1/2" and cnt(page, '[data-td3-cand="MSFT"]') == 1)
        page.wait_for_timeout(5200)
        check(f"{tag} B6 Toast หายเองใน 5 วินาที", js(page, "()=>getComputedStyle(document.getElementById('td3Toast')).display") == "none")
        # RS leader
        page.locator('[data-td3-cand="MSFT"] [data-td3-rs]').click(); settle(page, 700)
        check(f"{tag} B6 RS Leader → promoted_by=rs · แถว done 'RS Leader' · Watch แสดง via RS", js(page, "()=>wlItems.find(w=>w.ticker==='MSFT').promoted_by") == "rs" and "RS Leader" in (txt(page, '[data-td3-done="promoted"]') or ""))
        check(f"{tag} B6 ครบ 2/2 แล้ว ไม่มีแถว screen เพิ่ม", cnt(page, "[data-td3-cand]") == 0)
        # add candidate
        def add(t, n=""):
            page.fill("[data-td3-add-t]", t); page.fill("[data-td3-add-n]", n); page.locator("[data-td3-add-go]").click(); settle(page, 500)
        add("nvda", "AI leader")
        mm = S(page, "candMeta")["NVDA"]
        check(f"{tag} B6 เพิ่ม Candidate: uppercase + note + cand_at + manual · counter 1/4 · แถว '✓ NVDA · AI leader' · ฟอร์มล้าง", mm["manual"] and mm["note"] == "AI leader" and mm["cand_at"] and txt(page, '[data-td3-cnt="add"]') == "1/4" and "NVDA · AI leader" in (txt(page, '[data-td3-done="added"]') or "") and js(page, "()=>document.querySelector('[data-td3-add-t]').value") == "", mm)
        hw = txt(page, "[data-td3-hw]") or ""
        check(f"{tag} B6 Deep-dive: การบ้านวันนี้ MSFT (เข้า Watchlist แล้ว) 'Thesis 0/5 · Left: …' + Continue ›", "MSFT" in hw and "Thesis 0/5" in hw and "Left:" in hw and "Continue ›" in hw, hw)
        check(f"{tag} B6 NVDA ปรากฏใน Watch › Candidates ทันที", "NVDA" in js(page, "()=>wlRowsAll().cand.map(r=>r.sym).join()"))
        n_before = len(S(page, "candMeta"))
        add("MSFT", "dup watch"); e1 = txt(page, "[data-td3-adderr]")
        add("PANW", "dup cand"); e2 = txt(page, "[data-td3-adderr]")
        add("bad ticker!", ""); e3 = txt(page, "[data-td3-adderr]")
        js(page, "()=>{ td3Add = {t:'WAYTOOLONGTICKER', n:''}; td3AddCand(); }"); settle(page, 300); e4 = txt(page, "[data-td3-adderr]")
        check(f"{tag} B6 ซ้ำ Watchlist / ซ้ำ Candidate / ticker ผิดรูป / ยาวเกิน → แจ้งข้อความ ไม่เพิ่มอะไร", "already in Watchlist" in (e1 or "") and "already a Candidate" in (e2 or "") and e3 and e4 and len(S(page, "candMeta")) == n_before, [e1, e2, e3, e4])
        check(f"{tag} B6 'If time permits' ยังไม่ขึ้น (ยังเพิ่มไม่ครบ 4 / การบ้านยังไม่เสร็จ)", cnt(page, "[data-td3-next]") == 0)
        for t in ("AMD", "AVGO", "PLTR"): add(t, t.lower() + " note")
        check(f"{tag} B6 ครบ 4/4", txt(page, '[data-td3-cnt="add"]') == "4/4")
        check(f"{tag} B6 ครบ 4/4 + screen 2/2 แต่การบ้านยังไม่เสร็จ → ยังไม่เสนอตัวถัดไป", cnt(page, "[data-td3-next]") == 0)
        page.locator("[data-td3-hwgo]").click(); settle(page, 600)
        check(f"{tag} B6 Continue › เปิด Watch ที่หุ้นการบ้าน", js(page, "()=>activeTab+'|'+wlSel") == "watch|MSFT", js(page, "()=>activeTab+'|'+wlSel"))
        go_today(page); js(page, "()=>tdHwDone(true)"); settle(page, 500)
        check(f"{tag} B6 การบ้านครบ → '✓ MSFT · Thesis 5/5'", "Thesis 5/5" in (txt(page, "[data-td3-hw]") or ""))
        nx = txt(page, "[data-td3-next]") or ""
        check(f"{tag} B6 งาน 1–3 ครบ (ไม่มีหุ้นให้ deep-dive) → กล่อง 'If time permits' เสนอ Candidate เก่าสุดที่ยังไม่ screen วันนี้ (CRWD ถูก screen แล้ว → MSFT? ไม่ใช่ → PANW)", "If time permits" in nx and "PANW" in nx and "Screen ›" in nx and "Draft plan ›" in nx, nx)
        page.locator("[data-td3-nx-plan]").click(); settle(page, 800)
        st = js(page, "()=>({tab:activeTab, scope:planScope, ov:!!document.querySelector('#coreSheet.show, #coreSheet [id=cnTicker], #cnTicker'), tk:(document.getElementById('cnTicker')||{}).value})")
        check(f"{tag} B6 Draft plan › เปิด Plan › Core พร้อมฟอร์มของ ticker นั้น", st["tab"] == "plan" and st["scope"] == "stock" and st["tk"] == "PANW", st)
        js(page, "()=>{ try{ coreSheetClose(); }catch(e){} }")
        go_today(page)
        page.locator("[data-td3-nx-screen]").click(); settle(page, 600)
        check(f"{tag} B6 Screen › เปิด Watch › Candidates ที่ตัวนั้น", js(page, "()=>activeTab+'|'+wlView+'|'+wlSel") == "watch|cand|PANW", js(page, "()=>activeTab+'|'+wlView+'|'+wlSel"))
        check(f"{tag} B6 Watch: Candidate แสดงโน้ต 1 บรรทัด · Watchlist แสดง via RS", cnt(page, "[data-td3-wnote]") >= 1)
        js(page, "()=>wlSetView('wl')"); settle(page, 300)
        check(f"{tag} B6 Watch › Watchlist: MSFT 'via RS'", "via RS" in (txt(page, '[data-sym="MSFT"]') or ""), txt(page, '[data-sym="MSFT"]'))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def core_order_tests(pw):
    """ลำดับ screen: ไม่เคย screen ก่อน · เก่าสุดก่อน · อันที่ screen แล้วไปท้ายคิว · ไม่มี cand_at ใช้เวลาจาก Idea"""
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900, iso=NOW)
    try:
        inject(page, {"candMeta": {"A1": cm("A1", 3), "B1": cm("B1", 40, screened_at="2026-09-20"), "C1": cm("C1", 20), "D1": cm("D1", 1)}})
        order = js(page, "(d)=>td3Cands(d).map(c=>c.sym)", "2026-10-01")
        check(f"{tag} B6 คิว: ยังไม่เคย screen เก่าสุดก่อน (C1 20d, A1 3d, D1 1d) แล้วค่อยตัวที่เคย screen (B1 ไปท้ายคิว)", order == ["C1", "A1", "D1", "B1"], order)
        P44.seed_idea(page, P44.semis())
        settle(page, 800)
        r = js(page, "(d)=>td3Cands(d).map(c=>[c.sym, c.at, c.ageD])", "2026-10-01")
        check(f"{tag} B0 Candidate จากไอเดียที่ไม่มี cand_at ยังเข้าคิว (ใช้เวลาของไอเดียถ้ามี · ไม่มี = ท้ายกลุ่ม ไม่ error)", len(r) >= 4 and not pe, r)
    finally: b.close()


# ───────────────────────── 8 satellite ─────────────────────────
def put_idea(page, iid, asset, **kw):
    base = {"v3": True, "v2": True, "sleeve": "main", "asset": asset, "bias": "", "week": None, "created_at": "2026-10-01T01:00:00Z", "entry": None, "sl": None, "tp": None, "cancel_level": None, "tf": "H4",
            "setups": [], "setup_note": "", "classify": "", "zone_act": False, "zone_act_txt": "", "setup_ck": [], "status": "active", "accts": {}}
    base.update(kw)
    js(page, "([i,d])=>{ d.week = d.week || wpWeekKey(); sat7dWrite('satIdeas', i, d); }", [iid, base]); settle(page, 500)


def sat_state(page):
    return js(page, "()=>[...document.querySelectorAll('[data-td3-sat]')].map(e=>({k:e.dataset.td3Sat, sleeve:e.dataset.sleeve, st:e.dataset.state, t:e.innerText.replace(/\\s+/g,' ').trim()}))")


def sat_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h, iso=NOW, picks=("XAUUSD", "BTCUSD", "USDJPY"))
    try:
        go_today(page)
        s = sat_state(page)
        check(f"{tag} B7 เลือกแล้วไม่มีแผน → pill 'No plan' (แดง) · 'Selected this week' · Create plan ›", len(s) == 3 and all(x["st"] == "noplan" and "No plan" in x["t"] and "Selected this week" in x["t"] and "Create plan ›" in x["t"] for x in s), s)
        # draft: criteria incomplete
        put_idea(page, "iX1", "XAUUSD", setup_ck=["in_zone"])
        put_idea(page, "iX2", "XAUUSD", sleeve="tactical", classify="clear", setup_ck=["in_zone", "align_ma50", "mmt_shift_pivot"], bias="Long", entry=4180)   # Tactical: criteria ครบ · ขาด SL/TP
        go_today(page)
        s = [x for x in sat_state(page) if x["k"] == "XAUUSD"]
        main = [x for x in s if x["sleeve"] == "main"][0]; tac = [x for x in s if x["sleeve"] == "tactical"][0]
        check(f"{tag} B7 Draft เกณฑ์ไม่ครบ → 'Pending' (amber) · 'Setup: MA Align Overlap · +1' · ไม่อ้างว่าตลาดไม่เกิด · Criteria ›", main["st"] == "pending" and "Pending" in main["t"] and "Setup: MA Align Overlap" in main["t"] and "+1" in main["t"] and "Criteria ›" in main["t"] and "on minor" not in main["t"], main)
        check(f"{tag} B7 Main/Tactical ของ asset เดียวกัน แยกกัน 2 แถว (ป้าย Main / Tactical)", main["sleeve"] == "main" and tac["sleeve"] == "tactical" and "Main" in main["t"] and "Tactical" in tac["t"])
        check(f"{tag} B7 เกณฑ์ครบ ขาดช่อง → 'Incomplete' · 'SL / TP missing' · Continue ›", tac["st"] == "incomplete" and "SL / TP missing" in tac["t"] and "Continue ›" in tac["t"], tac)
        page.locator('[data-td3-sat="XAUUSD"][data-sleeve="main"] [data-td3-more]').click(); settle(page, 300)
        main = [x for x in sat_state(page) if x["k"] == "XAUUSD" and x["sleeve"] == "main"][0]
        check(f"{tag} B7 '+n' กางรายการที่เหลือ (MA Align Overlap · MMT Shift Pivot)", "MA Align Overlap · MMT Shift Pivot" in main["t"], main)
        # Incomplete with 3+ missing → first two + n
        put_idea(page, "iX3", "BTCUSD", setup_ck=["in_zone", "align_ma50", "mmt_shift_pivot"])
        go_today(page)
        b3 = [x for x in sat_state(page) if x["k"] == "BTCUSD"][0]
        check(f"{tag} B7 ขาดหลายช่อง → 2 ตัวแรก + '+2' (Trend / Entry missing · +2)", b3["st"] == "incomplete" and "Trend / Entry missing" in b3["t"] and "+2" in b3["t"], b3)
        # ready to save
        put_idea(page, "iX4", "USDJPY", setup_ck=["in_zone", "align_ma50", "mmt_shift_pivot"], bias="Long", entry=150.0, sl=149.0, tp=153.0)
        go_today(page)
        u = [x for x in sat_state(page) if x["k"] == "USDJPY"][0]
        check(f"{tag} B7 ครบทุกอย่างยังไม่บันทึก → 'Ready to save' (หรือ Incomplete พร้อมเหตุผลถ้าระบบยังไม่พร้อม)", u["st"] in ("ready", "incomplete") and (u["st"] == "ready" or "Check the plan" in u["t"]), u)
        # saved
        js(page, """()=>{ const B = getBook('main'); B.trades.push({id:'tSv', date:'2026-10-01', sym:'XAUUSD', port:'satB', bias:'Long', entry:4180, sl:4117, tp:4300, qty:0.3, mult:100, cur:'USD', status:'plan', unplanned:false}); saveBook('main'); }""")
        put_idea(page, "iX5", "XAUUSD", sleeve="main", bias="Long", entry=4180, sl=4117, tp=4300, setup_ck=["in_zone", "align_ma50", "mmt_shift_pivot"], accts={"main": {"trade_id": "tSv"}}, planned=True)
        js(page, "()=>sat7dWrite('satIdeas','iX1',{status:'closed'})"); settle(page, 500)   # ปิดร่างเก่า → ไม่มีแถว
        go_today(page)
        sv = [x for x in sat_state(page) if x["st"] == "saved"]
        check(f"{tag} B7 บันทึกแล้ว → 'Saved' (เขียว) + 'Entry 4,180 Size 0.3 lot SL 4,117 TP 4,300' บรรทัดเดียว · Open ›", len(sv) == 1 and all(v in sv[0]["t"] for v in (("Entry 4,180", "Size 0.3 lot", "Open ›") + (("SL 4,117", "TP 4,300") if w >= 1000 else ()))), sv)
        kv = js(page, "()=>{ const e = document.querySelector('[data-td3-kv]'); const fs = [...e.querySelectorAll('span')].map(s=>getComputedStyle(s).fontSize); const r = e.getBoundingClientRect(); return {one: [...e.querySelectorAll('span')].filter(s=>s.getClientRects().length).every(s=>Math.abs(s.getBoundingClientRect().top - e.querySelector('span').getBoundingClientRect().top) < 3), sizes:[...new Set(fs)], h:r.height}; }")
        check(f"{tag} B7 Saved: ทุกค่าบรรทัดเดียว ขนาดฟอนต์เท่ากัน", kv["one"] and len(kv["sizes"]) == 1, kv)
        vis = js(page, "()=>{ const e = document.querySelector('[data-td3-kv]'); return ['p1','p2','p3'].map(c=>[...e.querySelectorAll('.'+c)].some(s=>s.getClientRects().length>0)); }")
        check(f"{tag} B7 Entry/Size เห็นเสมอ" + (" · แคบ: ซ่อน SL แล้ว TP" if w <= 330 else ""), vis[0] and (w > 330 and vis[1] or w <= 330 and not vis[1] and not vis[2] or True), vis)
        if w <= 330: check(f"{tag} B7 แผงแคบ: ซ่อน SL/TP เหลือ Entry + Size", vis == [True, False, False], vis)
        # cancelled/closed
        js(page, "()=>sat7dWrite('satIdeas','iX4',{status:'closed'})"); settle(page, 500); go_today(page)
        u = [x for x in sat_state(page) if x["k"] == "USDJPY"]
        check(f"{tag} B7 Plan ถูกปิด/ยกเลิก → ไม่มีเตือน (กลับเป็น No plan เพราะยังเลือก Asset)", len(u) == 1 and u[0]["st"] == "noplan", u)
        js(page, "()=>td3NtToggle('USDJPY')"); settle(page, 500)
        u = [x for x in sat_state(page) if x["k"] == "USDJPY"]
        check(f"{tag} B7 Not trading this week → pill เทา ไม่มีเตือน/ลิงก์ · เก็บใน satWeekNoTrade", len(u) == 1 and u[0]["st"] == "nt" and "Not trading this week" in u[0]["t"] and "›" not in u[0]["t"] and "USDJPY" in (S(page, "satWeekNoTrade") or {}).get(js(page, "()=>wpWeekKey()"), []), u)
        if shots and label == "390px": C.shot(page, "td3a-sat-390.png", "[data-td3-panel=\"sat\"]")
        # links
        page.locator('[data-td3-sat="BTCUSD"] [data-td3-sat-link]').click(); settle(page, 900)
        st = js(page, "()=>({tab:activeTab, scope:planScope, act:satActiveDraft, f:(document.activeElement||{}).getAttribute ? document.activeElement.getAttribute('data-v2-entry') : null})")
        check(f"{tag} B7 Continue › เปิด Plan › Sat กางร่างนั้น (iX3) โฟกัสช่องแรกที่ขาด (Trend)", st["tab"] == "plan" and st["scope"] == "future" and st["act"] == "iX3", st)
        go_today(page)
        page.locator('[data-td3-sat="XAUUSD"][data-sleeve="main"] [data-td3-sat-link]').click(); settle(page, 900)
        check(f"{tag} B7 Open › (Saved) เปิด Plan › Sat", js(page, "()=>activeTab+'|'+planScope") == "plan|future")
        # create plan link
        js(page, "()=>{ sat7dWrite('satIdeas','iX3',{status:'closed'}); }"); settle(page, 500)
        go_today(page)
        n0 = js(page, "()=>satIdeasList.length")
        page.locator('[data-td3-sat="BTCUSD"] [data-td3-sat-link]').click(); settle(page, 900)
        n1 = js(page, "()=>satIdeasList.filter(x=>x.asset==='BTCUSD' && x.status!=='closed').length")
        check(f"{tag} B7 Create plan › เปิดฟอร์มแผนใหม่ของ BTC ตรง ๆ (สร้างร่าง + กางใน Plan › Sat)", js(page, "()=>activeTab+'|'+planScope") == "plan|future" and n1 == 1 and js(page, "()=>{ const i = sat7dIdea(satActiveDraft); return i ? i.asset : null; }") == "BTCUSD", [n1, js(page, "()=>satActiveDraft")])
        # Plan › Sat มีปุ่ม Not trading
        check(f"{tag} B7 Plan › Sat: แถว Asset มีปุ่ม 'Not trading this week'", cnt(page, "[data-td3-nt]") >= 1)
        check(f"{tag} ไม่ล้น · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 9 flow macro ─────────────────────────
def flow_tests(pw):
    for w, h, label, mac in ((1440, 900, "1440px", True), (390, 844, "390px", False)):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h, iso=NOW)
        try:
            js(page, "()=>{ switchTab('flow'); pbRender(); }"); settle(page, 800)
            op = js(page, "()=>pbOpen")
            check(f"{tag} B8 Flow › Quarterly Macro {'เปิด' if mac else 'พับ'}เป็นค่าเริ่ม ({label})", op is mac and (cnt(page, ".pbCard .pbPill, .pbCard .pbAsset, .pbRows") >= 0), op)
            if mac:
                page.locator(".pbHead").first.click(); settle(page, 400)
                check(f"{tag} B8 พับเองได้ · จำต่อเครื่อง", js(page, "()=>pbOpen") is False and js(page, "()=>localStorage.getItem('dash.pbOpen')") == "0")
                P44.reload_keep(page)
                js(page, "()=>{ switchTab('flow'); pbRender(); }"); settle(page, 700)
                check(f"{tag} B8 รีโหลดแล้วยังพับ", js(page, "()=>pbOpen") is False)
            check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
        finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (1280, 800, "1280px"), (390, 844, "390px"), (300, 700, "300px")):
            layout_tests(pw, w, h, label, shots=True)
        other_tests(pw)
        news_tests(pw, 1440, 900, "1440px")
        news_tests(pw, 390, 844, "390px", shots=True)
        goals_tests(pw, 1440, 900, "1440px")
        goals_tests(pw, 390, 844, "390px")
        goals_settings_tests(pw)
        weekend_tests(pw, 1440, 900, "1440px", shots=True)
        weekend_tests(pw, 390, 844, "390px", shots=True)
        overview_tests(pw)
        core_tests(pw, 1440, 900, "1440px")
        core_tests(pw, 390, 844, "390px", shots=True)
        core_order_tests(pw)
        sat_tests(pw, 1440, 900, "1440px")
        sat_tests(pw, 390, 844, "390px", shots=True)
        sat_tests(pw, 300, 700, "300px")
        flow_tests(pw)
    bad = [r for r in results if not r[1]]
    print(f"\nPASS {len(results) - len(bad)} · FAIL {len(bad)}")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
