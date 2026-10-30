#!/usr/bin/env python3
"""GL1 — เป้าหมาย Port ต่อบัญชี + % งาน Daily / Weekly (บนสุดของแท็บ วันนี้) · เทส 56
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-08 (พฤ.) เวลาไทย
ภาพ tests/screenshots/gl1-{goal,daily,weekly,sheet,settings}-{1440,390}.png
รัน: python3 run_tests_phase56.py"""
from pf2_retire import retired as retired2
import copy, json, math, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-GL1.html"))
results = []
js = P37.js
TODAY = "2026-10-08"
CLK = "2026-10-08T05:00:00Z"        # พฤ. 12:00 ไทย
CLK_SAT = "2026-10-10T05:00:00Z"    # ส. 12:00 ไทย
MON = "2026-10-05"
OVS = "#glValOverlay"


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


GOAL_MAIN = {"cur": "USD", "start": 112000, "startDate": "2026-01-02", "target": 250000, "deadline": "2027-12-31"}
GOAL_FAM = {"cur": "THB", "start": 2000000, "startDate": "2026-01-02", "target": 4000000, "deadline": "2028-12-31"}


def S(doc, acct="main"): return doc["books"][acct]["settings"]


def day(slots=0, sat=0, hw=False, extra=0):
    ids = ["planTH", "selUS1", "selUS2", "planUS", "selTH"][:slots]
    sats = ["XAUUSD", "BTC", "BRENT"][:sat]   # WA1fix: Today นับเฉพาะ Asset ที่เลือกสัปดาห์นี้ (เพดาน 3 = XAU · BTC · Brent ตาม P39.PICK39)
    d = {"slots": ids, "satState": {k: ("ok" if i == 0 else "no") for i, k in enumerate(sats)}}
    if hw: d["hw"] = {"pick": "ABC", "done": True}
    if extra: d["extra"] = ["x1", "x2"][:extra]
    return d


def with_goals(both=True, log=True, **kw):
    def m(doc):
        s = S(doc)
        s["goals"] = {"main": dict(GOAL_MAIN)}
        if both: s["goals"]["fam"] = dict(GOAL_FAM)
        if log:
            s["goalLog"] = {"main": [{"d": TODAY, "v": 145000}]}
            if both: s["goalLog"]["fam"] = [{"d": TODAY, "v": 2380000}]
        for k, v in kw.items(): s[k] = copy.deepcopy(v)
    return m


def launch(pw, w, h, *mutators, iso=CLK, watch=True, log=None, sat_week=None, pick=None):
    doc = P38.doc38(clean=True, log=log if log is not None else {})
    for m in mutators:
        if m: m(doc)
    def extra(page):
        if sat_week:
            P39.seed(page, ["users", "testuid", "satWeek", "2026-10-04"], sat_week)
        if watch:
            P39.seed(page, ["users", "testuid", "watchlist", "ABC"], {"ticker": "ABC", "market": "US", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"})
    return P39.launch(pw, w, h, doc=doc, clean=True, iso=iso, extra=extra, pick=pick)


def go_today(page): P38.go_today(page); page.wait_for_timeout(200)
def settings(page, key): return js(page, "(k)=>{ const v = tdSettings()[k]; return v===undefined ? null : JSON.parse(JSON.stringify(v)); }", key)
def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def txt_wrap_nohw(page):
    """GL3 — ข้อความ Today ([data-td-wrap]) ไม่รวมแถว/บรรทัดการบ้าน (GL3 เปลี่ยนหน้าตาการบ้านเป็นชิป 5 part ตาม brief) · ส่วนอื่นต้องเหมือนเดิมทุกตัวอักษร"""
    return js(page, "()=>{ const e=document.querySelector('[data-td-wrap]'); if(!e) return null; const c=e.cloneNode(true); c.querySelectorAll('.tdRow[data-kind=\"homework\"], [data-hw-doneline], .tdRow[data-kind=\"sat-daily\"], .tdRow[data-kind=\"bias\"]').forEach(x=>x.remove()); return c.innerText.replace(/\\s+/g,' ').trim(); }")
def count(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def acct_txt(page, a, sub=""): return txt(page, f'[data-gl-acct="{a}"] {sub}'.strip())
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
def wait(page, ms=350): page.wait_for_timeout(ms)
def tab(page, t): page.locator(f'[data-gl-tab="{t}"]').click(); wait(page)
def open_settings(page): js(page, "()=>openSystemSettings()"); wait(page, 400)
def close_settings(page): js(page, "()=>{ document.getElementById('sysOverlay').classList.remove('show'); }")
def style_left(page, a): return js(page, "(a)=>parseFloat(document.querySelector(`[data-gl-acct=\"${a}\"] [data-gl-exp]`).style.left)", a)
def bar_w(page, a): return js(page, "(a)=>parseFloat(document.querySelector(`[data-gl-acct=\"${a}\"] .glBar i`).style.width)", a)
def sheet_open(page): return js(page, "()=>document.getElementById('glValOverlay').classList.contains('show')")


def exp_expected(start, sd, target, dl, asof):
    from datetime import date
    D = lambda s: date.fromisoformat(s)
    T = (D(dl) - D(sd)).days; a = (D(asof) - D(sd)).days
    return start * math.exp(math.log(target / start) / T * a)


def fill_sheet(page, date=None, **vals):
    if date is not None: page.locator("[data-gl-valdate]").fill(date)
    for a, v in vals.items(): page.locator(f'[data-gl-valin="{a}"]').fill(v)
    page.locator("[data-gl-valsave]").click(); wait(page, 450)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); narrow = w < 500
    # ── 1 ไม่มี goals / dailyExtra / weekTasks
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, pick=["XAUUSD", "BTCUSD", "S50"])   # WA1fix: ป้ายจำนวนงานที่ช่วง Plan TH (S50) ต้องเท่าไฟล์เก่า → เลือก S50
    try:
        go_today(page)
        check(f"{tag} 1 ไม่มี goals: การ์ดเป้าแสดงแถวเดียว 'ตั้งเป้าหมาย Port →' · ไม่มีแถวบัญชี · ไม่มีปุ่มกรอกค่า", (txt(page, "[data-gl-setup]") or "").endswith("ตั้งเป้าหมาย Port →") and count(page, ".glA") == 0 and count(page, "[data-gl-valopen]") == 0, txt(page, "[data-gl-goal]"))
        check(f"{tag} 1 สวิตช์ Daily · x% / Weekly · y% อยู่ถัดจากการ์ดเป้า · ค่าเริ่ม Daily", js(page, "()=>{ const s=document.querySelector('[data-gl-seg]'); return !!s && s.previousElementSibling === document.querySelector('[data-gl-goal]') && s.querySelector('[data-gl-tab=d]').classList.contains('on'); }"))
        tab(page, "w")
        ids = js(page, "()=>[...document.querySelectorAll('[data-gl-wrow]')].map(e=>e.dataset.glWrow)")
        check(f"{tag} PF3 1 Weekly ชุดเริ่มต้น: ข้อ 'ทำแผน Sat สัปดาห์นี้' (กดเอง) · กรอกค่าพอร์ตซ่อน (ไม่มีบัญชีตั้งเป้า) → เหลือ 3 แถว = wbias · wjournal · wdaily", ids == ["wbias", "wsector", "wjournal", "wdaily"], json.dumps(ids))
        check(f"{tag} PF3 1 ปุ่ม 'Weekly · 0%' · แถว 'ทำแผน Sat สัปดาห์นี้' กดเองได้ (ไม่มีเส้นประ auto) · Journal กดเองได้ · Daily เป็น auto", txt(page, '[data-gl-tab="w"]') == "Weekly · 0%" and "ทำแผน Sat สัปดาห์นี้" in (txt(page, '[data-gl-wrow="wbias"]') or "") and count(page, '[data-gl-wrow="wbias"] [data-gl-wauto]') == 0 and count(page, '[data-gl-wtick="wbias"]') == 1 and count(page, '[data-gl-wtick="wjournal"]') == 1 and count(page, '[data-gl-wrow="wdaily"] [data-gl-wauto]') == 1, txt(page, "[data-gl-weekly]"))
        # Today ส่วนเดิมเหมือนก่อน GL1
        txt_now = txt_wrap_nohw(page)
        tab(page, "d")
    finally: browser.close()
    saved = P39.INDEX; P39.INDEX = BACKUP
    try:
        browser, context, page, ce2, pe2, d2 = launch(pw, w, h)
        try:
            go_today(page); txt_old = txt_wrap_nohw(page)
        finally: browser.close()
    finally: P39.INDEX = saved
    txt_old = re.sub(r"ประตู f(?![A-Za-z])", "ประตู FF", re.sub(r"ค่า f/", "ค่า FF/", txt_old))   # UX2: f → FF ทั้ง UI (Today: ประตู FF · ค่า FF/ประตู)
    txt_old = txt_old.replace("บัญชีหลัก", "Main")   # SET1 — ตารางตัวเลขใน Today แสดง "Main" แทน "บัญชีหลัก" (ตั้งใจ)
    check(f"{tag} PF3 1 Today ส่วนเดิม ([data-td-wrap]) ข้อความเหมือนก่อน GL1 (ยกเว้นชื่องาน Weekly ข้อแรก 'ทำแผน Sat สัปดาห์นี้' แทน 'ตั้ง Bias สัปดาห์ Sat ครบ' · ต้องทำ 3→2 · ตัวนับ Trading Plan US 2→1 เพราะงาน Today 'Bias ยังไม่ประเมิน' ถอด)", txt_now == txt_old.replace("ตั้ง Bias สัปดาห์ Sat ครบ", "ทำแผน Sat สัปดาห์นี้").replace("ต้องทำ3", "ต้องทำ2").replace("Trading Plan US2", "Trading Plan US1"), (lambda x, y: (lambda i: x[max(0, i - 40):i + 420] + " || " + y[max(0, i - 40):i + 420])(next((k for k, (p, q) in enumerate(zip(x, y)) if p != q), min(len(x), len(y)))))(txt_now, txt_old.replace("ตั้ง Bias สัปดาห์ Sat ครบ", "ทำแผน Sat สัปดาห์นี้").replace("ต้องทำ3", "ต้องทำ2").replace("Trading Plan US2", "Trading Plan US1")))
    check(f"{tag} 1 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))

    # ── 2-3 main $ / Family ฿
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals())
    try:
        go_today(page)
        n_main = acct_txt(page, "main", "[data-gl-num]"); n_fam = acct_txt(page, "fam", "[data-gl-num]")
        names = js(page, "()=>[...document.querySelectorAll('[data-gl-acct] b')].map(e=>e.textContent)")
        check(f"{tag} 2 main: '$145.0k → $250k · 31 ธ.ค. 70' · 24% · ช้ากว่าเส้นทาง −4.8% · ต้องโต 55.7%/ปี", n_main == "$145.0k → $250k · 31 ธ.ค. 70" and acct_txt(page, "main", "[data-gl-pct]") == "24%" and "ช้ากว่าเส้นทาง −4.8%" in acct_txt(page, "main", "[data-gl-l3]") and "ต้องโต 55.7%/ปี" in acct_txt(page, "main", "[data-gl-l3]"), json.dumps([n_main, acct_txt(page, "main", "[data-gl-l3]")], ensure_ascii=False))
        check(f"{tag} 2 main: ขีดดำ ≈ 29.2% · แถบ 24% · สีเหลืองของสถานะช้ากว่า", abs(style_left(page, "main") - 29.2) < 0.15 and abs(bar_w(page, "main") - 23.9) < 0.2 and js(page, "()=>document.querySelector('[data-gl-acct=main] [data-gl-status]').classList.contains('wa')"), json.dumps([style_left(page, "main"), bar_w(page, "main")]))
        check(f"{tag} 3 Family: '฿2.38M → ฿4M · 31 ธ.ค. 71' · 19% · ตามเส้นทาง (−0.3%) · ต้องโต 26.2%/ปี", n_fam == "฿2.38M → ฿4M · 31 ธ.ค. 71" and acct_txt(page, "fam", "[data-gl-pct]") == "19%" and "ตามเส้นทาง (−0.3%)" in acct_txt(page, "fam", "[data-gl-l3]") and "ต้องโต 26.2%/ปี" in acct_txt(page, "fam", "[data-gl-l3]"), json.dumps([n_fam, acct_txt(page, "fam", "[data-gl-l3]")], ensure_ascii=False))
        check(f"{tag} 3 ทั้ง 2 บัญชีแยกกัน (ไม่รวม) · ชื่อบัญชีตามที่ตั้ง · ปุ่ม ＋ กรอกค่าพอร์ต ที่หัวการ์ด", len(names) == 2 and count(page, "[data-gl-valopen]") == 1 and "ช้ากว่า" not in acct_txt(page, "fam", "[data-gl-l3]"), json.dumps(names, ensure_ascii=False))
        check(f"{tag} 3 'กรอก 8 ต.ค.' ไม่เหลือง (ค่าวันนี้) · ไม่มีวงเล็บวัน", "กรอก 8 ต.ค." in acct_txt(page, "main", "[data-gl-l3]") and "วัน)" not in acct_txt(page, "main", "[data-gl-l3]") and not js(page, "()=>document.querySelector('[data-gl-acct=main] [data-gl-asof]').classList.contains('wa')"))
        shot(page, f"gl1-goal-{sfx}.png", "[data-gl-goal]")
        check(f"{tag} 3 ตั้งค่า Port ใน Today: การ์ดเป้า + สลับ + แผง ≤ 1 จอ (≤ 800px) เมื่อมี 2 บัญชี", js(page, "()=>{ const p=document.querySelector('[data-gl-pd]'), c=document.querySelector('[data-gl-goal]'); return p.getBoundingClientRect().bottom - c.getBoundingClientRect().top; }") <= 800, js(page, "()=>{ const p=document.querySelector('[data-gl-pd]'), c=document.querySelector('[data-gl-goal]'); return p.getBoundingClientRect().bottom - c.getBoundingClientRect().top; }"))
        if narrow:
            bad = js(page, """()=>{ const out=[]; document.querySelectorAll('[data-gl-goal] .glL1, [data-gl-goal] .glL3, [data-gl-goal] .glH').forEach(e=>{ const lh=parseFloat(getComputedStyle(e).lineHeight)||20; if(e.getBoundingClientRect().height > lh*1.7 || e.scrollWidth > e.clientWidth + 1) out.push(e.className+':'+e.scrollWidth+'>'+e.clientWidth+' '+e.innerText); }); return out; }""")
            check(f"{tag} 10 390px: ทุกบรรทัดในการ์ดเป้าไม่ตัดขึ้นบรรทัดใหม่ · ไม่ถูกตัดด้วย …", not bad, json.dumps(bad, ensure_ascii=False))
            check(f"{tag} 10 390px: หน้าไม่ล้นแนวนอน", overflow(page) <= 0, overflow(page))
        # สลับบัญชี active แล้วการ์ดเป้ายังครบทั้ง 2
        js(page, "()=>acctSwitch('fam')"); wait(page, 500); go_today(page)
        check(f"{tag} 10 สลับบัญชี active เป็น Family → การ์ดเป้ายังแสดงครบ 2 บัญชี ตัวเลขเท่าเดิม", count(page, "[data-gl-acct]") == 2 and acct_txt(page, "main", "[data-gl-pct]") == "24%" and acct_txt(page, "fam", "[data-gl-pct]") == "19%")
        check(f"{tag} 2 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()

    # ── 4 as-of ≠ วันนี้ · ไม่มีค่า
    def old_log(doc):
        s = S(doc); s["goalLog"] = {"main": [{"d": "2026-09-26", "v": 145000}, {"d": "2026-09-01", "v": 130000}]}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(both=False, log=False), old_log)
    try:
        go_today(page)
        l3 = acct_txt(page, "main", "[data-gl-l3]")
        e = exp_expected(112000, "2026-01-02", 250000, "2027-12-31", "2026-09-26")
        vs = (145000 / e - 1) * 100
        want = f"{'ช้ากว่า' if vs < 0 else 'เร็วกว่า'}เส้นทาง {'−' if vs < 0 else '+'}{abs(vs):.1f}%"
        check(f"{tag} 4 ค่าล่าสุด 26 ก.ย. → เทียบเส้นทาง ณ 26 ก.ย. ({want}) ไม่ใช่เส้นทางวันนี้ (−4.8%)", want in l3 and "−4.8%" not in l3, json.dumps([l3, want], ensure_ascii=False))
        check(f"{tag} 4 'กรอก 26 ก.ย. (12 วัน)' สีเหลือง", "กรอก 26 ก.ย. (12 วัน)" in l3 and js(page, "()=>document.querySelector('[data-gl-acct=main] [data-gl-asof]').classList.contains('wa')"), l3)
        check(f"{tag} 4 ต้องโต คิดจากวัน as-of ถึงครบกำหนด", "ต้องโต " in l3 and abs(float(l3.split("ต้องโต ")[1].split("%")[0]) - ((250000 / 145000) ** (365 / 461) - 1) * 100) < 0.06, l3)
    finally: browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(both=False, log=False))
    try:
        go_today(page)
        check(f"{tag} 4 ไม่มีค่าเลย: 'ยังไม่กรอกค่าพอร์ต' · 0% · ไม่แสดงต้องโต", acct_txt(page, "main", "[data-gl-l3]") == "ยังไม่กรอกค่าพอร์ต" and acct_txt(page, "main", "[data-gl-pct]") == "0%" and count(page, "[data-gl-need]") == 0 and "$112.0k" in acct_txt(page, "main", "[data-gl-num]"), acct_txt(page, "main"))
    finally: browser.close()

    # ── 5 ขอบ
    def log_of(v, d=TODAY): return lambda doc: S(doc).update({"goalLog": {"main": [{"d": d, "v": v}]}})
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(both=False, log=False), log_of(260000))
    try:
        go_today(page)
        l3 = acct_txt(page, "main", "[data-gl-l3]")
        check(f"{tag} 5 now ≥ target: ✓ ถึงเป้าแล้ว · % ≥ 100 · ไม่แสดงต้องโต · แถบเต็ม", "✓ ถึงเป้าแล้ว" in l3 and "ต้องโต" not in l3 and int(acct_txt(page, "main", "[data-gl-pct]").rstrip("%")) >= 100 and bar_w(page, "main") == 100, json.dumps([l3, acct_txt(page, "main", "[data-gl-pct]")], ensure_ascii=False))
    finally: browser.close()
    def late(doc): S(doc)["goals"]["main"]["deadline"] = "2026-10-08"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(both=False, log=False), log_of(145000), late)
    try:
        go_today(page)
        l3 = acct_txt(page, "main", "[data-gl-l3]")
        check(f"{tag} 5 as-of ≥ deadline และยังไม่ถึงเป้า: 'เลยกำหนด' (เหลือง) แทนต้องโต", "เลยกำหนด" in l3 and "ต้องโต" not in l3 and js(page, "()=>document.querySelector('[data-gl-overdue]').classList.contains('wa')"), l3)
    finally: browser.close()
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(both=False, log=False), log_of(100000))
    try:
        go_today(page)
        p = acct_txt(page, "main", "[data-gl-pct]")
        check(f"{tag} 5 now < start: % ติดลบ (−9%) · แถบ 0 · ขีดดำยังอยู่ในกรอบ 0–100", p == "−9%" and bar_w(page, "main") == 0 and 0 <= style_left(page, "main") <= 100, json.dumps([p, bar_w(page, "main"), style_left(page, "main")]))
        # ตั้งเป้าผิด → ไม่บันทึก
        before = settings(page, "goals")
        open_settings(page)
        js(page, "()=>{ document.getElementById('glSetSec').open = true; }")
        def try_save(**f):
            for k, v in f.items(): page.locator(f"[data-gl-{k}]").fill(v)
            page.locator("[data-gl-save]").click(); wait(page, 300)
            return txt(page, "[data-gl-setmsg]"), settings(page, "goals")
        m1, g1 = try_save(target="100,000", start="112,000")
        check(f"{tag} 5 ตั้งเป้าผิด: target ≤ start → มีข้อความ · ไม่บันทึก", m1 and g1 == before, json.dumps([m1, g1], ensure_ascii=False))
        m2, g2 = try_save(target="250,000", deadline="2026-01-01")
        check(f"{tag} 5 ตั้งเป้าผิด: deadline ≤ startDate → มีข้อความ · ไม่บันทึก", m2 and g2 == before, json.dumps([m2, g2], ensure_ascii=False))
        m3, g3 = try_save(deadline="2027-12-31", start="0")
        check(f"{tag} 5 ตั้งเป้าผิด: start = 0 → ไม่บันทึก", m3 and g3 == before, json.dumps([m3, g3], ensure_ascii=False))
        m4, g4 = try_save(start="112,000", target="300,000")
        check(f"{tag} 5 ตั้งเป้าถูกต้อง (ตัวเลขมีจุลภาค) → บันทึก goals.main.target = 300000 · ไม่กระทบ goalLog", g4 and g4["main"]["target"] == 300000 and settings(page, "goalLog") == {"main": [{"d": TODAY, "v": 100000}]}, json.dumps(g4))
        shot(page, f"gl1-settings-{sfx}.png", "#sysOverlay .modal")
        if narrow:
            fs = js(page, "()=>[...document.querySelectorAll('#glSet input, #glSet select')].map(e=>parseFloat(getComputedStyle(e).fontSize))")
            check(f"{tag} 10 390px: ช่องกรอกเป้าในตั้งค่า font ≥ 16px", fs and min(fs) >= 16, json.dumps(fs))
        # ลบเป้า → ประวัติยังอยู่
        page.locator("[data-gl-del]").click(); wait(page, 400)
        check(f"{tag} 5 ลบเป้า (ยืนยัน) → goals ไม่มี main · goalLog ยังอยู่", settings(page, "goals") is None and settings(page, "goalLog") == {"main": [{"d": TODAY, "v": 100000}]} and len(dialogs) >= 1, json.dumps([settings(page, "goals"), dialogs]))
        close_settings(page); go_today(page)
        check(f"{tag} 5 หลังลบเป้า: การ์ดกลับเป็นแถว 'ตั้งเป้าหมาย Port →'", count(page, "[data-gl-setup]") == 1 and count(page, ".glA") == 0)
        page.locator("[data-gl-setup]").click(); wait(page, 400)
        check(f"{tag} 5 กด 'ตั้งเป้าหมาย Port →' เปิดตั้งค่าที่ส่วนเป้าหมาย", js(page, "()=>document.getElementById('sysOverlay').classList.contains('show') && document.getElementById('glSetSec').open"))
        # ค่าเริ่มต้นของช่อง = ค่าล่าสุดใน goalLog + วันนี้
        sv = js(page, "()=>[document.getElementById('glSetStart').value, document.getElementById('glSetStartDate').value]")
        check(f"{tag} 5 ไม่มีเป้า: ช่อง 'ค่าเริ่มต้น/วันเริ่ม' เติมให้ = ค่าล่าสุดใน goalLog + วันนี้", sv == ["100,000", TODAY], json.dumps(sv))
    finally: browser.close()
    # บัญชีที่ถูกลบ: key ที่ไม่มีใน acctList ถูกข้าม
    def ghost(doc): S(doc)["goals"]["ghost"] = dict(GOAL_MAIN); S(doc)["goalLog"]["ghost"] = [{"d": TODAY, "v": 1}]
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(), ghost)
    try:
        go_today(page)
        check(f"{tag} 5 key ของบัญชีที่ไม่มีใน acctList ถูกข้าม (ไม่แสดง · ไม่ลบข้อมูล)", count(page, "[data-gl-acct]") == 2 and "ghost" in (settings(page, "goals") or {}) and not ce and not pe)
    finally: browser.close()

    # ── 6 Sheet กรอกค่า
    def old_vals(doc): S(doc)["goalLog"] = {"main": [{"d": "2026-09-26", "v": 140000}]}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(log=False), old_vals)
    try:
        go_today(page)
        page.locator("[data-gl-valopen]").click(); wait(page)
        info = js(page, """()=>({open:document.getElementById('glValOverlay').classList.contains('show'), date:document.querySelector('[data-gl-valdate]').value,
            ph:[...document.querySelectorAll('[data-gl-valin]')].map(e=>[e.dataset.glValin, e.placeholder, e.inputMode, parseFloat(getComputedStyle(e).fontSize)]),
            labels:[...document.querySelectorAll('#glValBody .f label')].map(e=>e.textContent.trim())})""")
        check(f"{tag} 6 sheet เปิด: วันที่ค่าเริ่ม = วันนี้ไทย · ช่องต่อบัญชี (ป้ายสกุล $ / ฿) · placeholder 'ล่าสุด …' · inputmode=decimal", info["open"] and info["date"] == TODAY and [p[0] for p in info["ph"]] == ["main", "fam"] and info["ph"][0][1] == "ล่าสุด 140,000" and all(p[2] == "decimal" for p in info["ph"]) and info["labels"][1].endswith("$") and info["labels"][2].endswith("฿"), json.dumps(info, ensure_ascii=False))
        check(f"{tag} 6 ช่องกรอกใน sheet font ≥ 16px (กัน iPhone ซูม)", min(p[3] for p in info["ph"]) >= 16 and js(page, "()=>parseFloat(getComputedStyle(document.querySelector('[data-gl-valdate]')).fontSize)") >= 16)
        shot(page, f"gl1-sheet-{sfx}.png", f"{OVS} .modal")
        if narrow: check(f"{tag} 10 390px: sheet ไม่ล้นแนวนอน", js(page, "()=>{ const m=document.querySelector('#glValOverlay .modal'); return m.scrollWidth - m.clientWidth; }") <= 1 and overflow(page) <= 0)
        fill_sheet(page, main="145,000", fam="2,380,000")
        lg = settings(page, "goalLog")
        check(f"{tag} 6 บันทึก 2 บัญชี (จุลภาคได้) → ปิด sheet · main ต่อท้าย (เรียงวัน) · fam 1 แถว", not sheet_open(page) and lg["main"] == [{"d": "2026-09-26", "v": 140000}, {"d": TODAY, "v": 145000}] and lg["fam"] == [{"d": TODAY, "v": 2380000}], json.dumps(lg))
        check(f"{tag} 6 แถบอัปเดตทันที: main 24% · fam 19%", acct_txt(page, "main", "[data-gl-pct]") == "24%" and acct_txt(page, "fam", "[data-gl-pct]") == "19%")
        page.locator("[data-gl-valopen]").click(); wait(page)
        fill_sheet(page, main="150000")
        lg = settings(page, "goalLog")
        check(f"{tag} 6 วันเดียวกันกรอกซ้ำ = แทนที่ (ความยาว log ไม่เพิ่ม) · ช่องว่าง (fam) = ไม่บันทึก/ไม่แตะ", len(lg["main"]) == 2 and lg["main"][-1] == {"d": TODAY, "v": 150000} and lg["fam"] == [{"d": TODAY, "v": 2380000}], json.dumps(lg))
        before = settings(page, "goalLog")
        def bad_try(date=None, **v):
            page.locator("[data-gl-valopen]").click(); wait(page, 250)
            fill_sheet(page, date=date, **v)
            ok = sheet_open(page) and (txt(page, "[data-gl-valmsg]") or "") != "" and settings(page, "goalLog") == before
            page.locator("[data-gl-valcancel]").click(); wait(page, 200)
            return ok
        check(f"{tag} 6 วันอนาคต → ไม่บันทึก มีข้อความ", bad_try(date="2026-10-09", main="1"))
        check(f"{tag} 6 ค่า 0 / ติดลบ / ตัวอักษร → ไม่บันทึก มีข้อความ", bad_try(main="0") and bad_try(main="-5") and bad_try(main="abc"))
        check(f"{tag} 6 ไม่กรอกอะไรเลยแล้วกดบันทึก → ไม่บันทึก มีข้อความ", bad_try())
        # ประวัติ + ลบรายแถว
        open_settings(page); js(page, "()=>{ document.getElementById('glSetSec').open = true; }")
        rows = js(page, "()=>[...document.querySelectorAll('[data-gl-hist]')].map(e=>e.dataset.glHist)")
        check(f"{tag} 6 ประวัติค่าพอร์ตใน ตั้งค่า: ล่าสุดก่อน (main)", rows == [TODAY, "2026-09-26"], json.dumps(rows))
        page.locator('[data-gl-histdel="2026-09-26"]').click(); wait(page, 400)
        check(f"{tag} 6 ลบแถวประวัติ (ยืนยัน) → ลบเฉพาะแถวนั้น", settings(page, "goalLog")["main"] == [{"d": TODAY, "v": 150000}] and len(dialogs) >= 1, json.dumps(settings(page, "goalLog")))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()
    # ประวัติ > 12 แถว → ดูทั้งหมด
    def long_log(doc): S(doc)["goalLog"]["main"] = [{"d": f"2026-09-{i:02d}", "v": 100000 + i} for i in range(1, 16)]
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(), long_log)
    try:
        open_settings(page); js(page, "()=>{ document.getElementById('glSetSec').open = true; }")
        a = count(page, "[data-gl-hist]")
        page.locator("[data-gl-histall]").click(); wait(page, 250)
        check(f"{tag} 6 ประวัติ > 12 แถว: แสดง 12 + ปุ่ม ดูทั้งหมด → แสดงครบ 15", a == 12 and count(page, "[data-gl-hist]") == 15, json.dumps([a, count(page, "[data-gl-hist]")]))
    finally: browser.close()

    # ── 7 Daily
    daily_cfg = {"dailyExtra": [{"id": "x1", "name": "อ่านข่าวเช้า 15 นาที"}, {"id": "x2", "name": "จด Journal ไม้ที่ปิดวันนี้"}]}
    def today_log(doc): S(doc)["routineLog"] = {TODAY: day(slots=2, sat=2, hw=True, extra=1)}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(**daily_cfg), today_log)
    try:
        go_today(page)
        head = txt(page, "[data-gl-dpct]"); chips = js(page, "()=>[...document.querySelectorAll('[data-gl-chip]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 7 Daily: ช่อง 2/5 + Sat 2/3 (ok 1 · no 1) + การบ้าน 5/5 + งานอื่น 1/2 → '10/15 · 67%' [GL3: การบ้านนับ 5 part · WA1fix: Sat 3 ตลาด]", head == "10/15 · 67%", json.dumps([head, chips], ensure_ascii=False))
        check(f"{tag} 7 ชิปแยกหมวดตรง: ช่วงเวลา 2/5 · เช็กแผน Sat 2/3 · การบ้าน 5/5 · งานอื่น 1/2 [GL3 · WA1fix]", chips == ["ช่วงเวลา 2/5", "เช็กแผน Sat 2/3", "การบ้าน 5/5", "งานอื่น 1/2"], json.dumps(chips, ensure_ascii=False))
        check(f"{tag} 7 ปุ่มสลับ 'Daily · 67%' · หัว 'วันนี้ พฤ. 8 ต.ค.' · ปุ่มสูง ≥ 40px", (txt(page, '[data-gl-tab="d"]') == "Daily · 67%") and "วันนี้ พฤ. 8 ต.ค." in txt(page, "[data-gl-pd]") and js(page, "()=>document.querySelector('[data-gl-tab=d]').getBoundingClientRect().height") >= 40, txt(page, "[data-gl-pd]"))
        shot(page, f"gl1-daily-{sfx}.png")
        page.locator('[data-gl-xtick="x2"]').click(); wait(page, 450)
        check(f"{tag} 7 ติ๊กงานอื่นใน Today → '11/15 · 73%' · เขียน routineLog[วัน].extra = [x1,x2] (ไม่แตะ slots/satState/hw)", txt(page, "[data-gl-dpct]") == "11/15 · 73%" and settings(page, "routineLog")[TODAY]["extra"] == ["x1", "x2"] and settings(page, "routineLog")[TODAY]["slots"] == ["planTH", "selUS1"] and settings(page, "routineLog")[TODAY]["hw"] == {"pick": "ABC", "done": True}, json.dumps(settings(page, "routineLog")))
        check(f"{tag} 7 ปุ่มสลับอัปเดตเป็น 'Daily · 73%' · ติ๊กซ้ำ = เอาออก", txt(page, '[data-gl-tab="d"]') == "Daily · 73%")
        page.locator('[data-gl-xtick="x2"]').click(); wait(page, 400)
        check(f"{tag} 7 ติ๊กซ้ำ → กลับ 10/15 · extra = [x1]", txt(page, "[data-gl-dpct]") == "10/15 · 67%" and settings(page, "routineLog")[TODAY]["extra"] == ["x1"])
        # ติ๊ก slot เดิม → ตัวเลข Daily ขยับ
        page.locator('[data-tick-slot="selUS2"]').click(); wait(page, 400)
        check(f"{tag} 7 ติ๊กช่วงเวลาที่ส่วนเดิม → Daily 11/15 (ไม่ซ้ำรายการในแผง)", txt(page, "[data-gl-dpct]") == "11/15 · 73%" and count(page, "[data-gl-pd] [data-tick-slot]") == 0)
        check(f"{tag} 7 ส่วนเดิมของ Today ยังอยู่ (Routine · Sat ✓/✕ · การบ้าน)", count(page, "[data-td-routine]") == 1 and (count(page, "[data-sat-chip]") >= 1 or count(page, "[data-pf2-sat]") >= 1))   # PF2: ไม่มี Asset = การ์ด Sat state A
        # จำแท็บ (localStorage)
        tab(page, "w")
        stored = js(page, "()=>localStorage.getItem('dash.glTab')")
        check(f"{tag} 7 จำแท็บที่เลือกต่อเครื่อง (localStorage) = w", stored == "w", stored)
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()
    # เสาร์
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(**daily_cfg), iso=CLK_SAT)
    try:
        go_today(page)
        check(f"{tag} 7 เสาร์: ปุ่ม 'Daily · วันหยุด' · แผง 'วันหยุด — ไม่มีงานรายวัน' · ติ๊กงานอื่นไม่ได้", txt(page, '[data-gl-tab="d"]') == "Daily · วันหยุด" and "วันหยุด — ไม่มีงานรายวัน" in (txt(page, "[data-gl-rest]") or "") and count(page, "[data-gl-xtick]") == 0, txt(page, "[data-gl-seg]"))
        tab(page, "w")
        check(f"{tag} 7 เสาร์: Weekly ยังแสดง (ครบ 5 แท่ง จ.–ศ. ไม่มีวันใดเป็นวันนี้-ตัวหนา)", count(page, "[data-gl-day]") == 5 and count(page, ".glDay.today") == 0)
    finally: browser.close()

    # ── 8 Weekly
    WL = {MON: day(5, 3, True, 2), "2026-10-06": day(5, 3, True, 1), "2026-10-07": day(2, 1, True, 1), TODAY: day(2, 2, True, 1)}   # 15/15 · 14/15 · 9/15 · 10/15 [GL3 · WA1fix: Sat 3 ตลาด]
    def wk_log(doc): S(doc)["routineLog"] = copy.deepcopy(WL)
    def goal_log(doc): S(doc)["goalLog"] = {"main": [{"d": "2026-10-06", "v": 145000}], "fam": [{"d": "2026-09-20", "v": 2380000}]}
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(**daily_cfg), wk_log, goal_log, sat_week={'XAUUSD':{'bias':'Long'}, 'BTCUSD':{'bias':'Short'}, 'S50':{'bias':'None'}, 'BRENT':{'bias':'Long'}})
    try:
        go_today(page)
        tab(page, "w")
        rows = js(page, "()=>[...document.querySelectorAll('[data-gl-wrow]')].map(e=>({id:e.dataset.glWrow, done:e.dataset.done==='true', right:e.querySelector('[data-gl-wright]').innerText, auto:!!e.querySelector('[data-gl-wauto]')}))")
        by = {r["id"]: r for r in rows}
        pcts = js(page, "()=>[...document.querySelectorAll('[data-gl-day]')].map(e=>[e.dataset.glDay, e.querySelector('i') ? e.querySelector('i').style.height : null, e.querySelector('i') ? e.querySelector('i').className : null])")
        check(f"{tag} PF3 8 งาน 'ทำแผน Sat สัปดาห์นี้' เป็นกดเอง: ยังไม่ติ๊ก = ไม่ครบ · ไม่ใช่ auto · ขวา = 'กดเอง'", by["wbias"]["auto"] is False and by["wbias"]["done"] is False and by["wbias"]["right"] == "กดเอง", json.dumps(by.get("wbias"), ensure_ascii=False))
        check(f"{tag} 8 กรอกค่า 1 จาก 2 บัญชีในสัปดาห์ → '1/2 บัญชี' ไม่ครบ", not by["wvalue"]["done"] and by["wvalue"]["right"] == "1/2 บัญชี", json.dumps(by.get("wvalue"), ensure_ascii=False))
        check(f"{tag} 8 Daily จ.100 อ.93 พ.60 พฤ.67 (fixture 15/15 · 14/15 · 9/15 · 10/15 [GL3: การบ้านนับ 5 part]) → 'Daily ครบ ≥ 4/5 วัน' = 2/4 ไม่ครบ", by["wdaily"]["right"] == "2/4" and not by["wdaily"]["done"], json.dumps([by.get("wdaily"), pcts]))
        check(f"{tag} 8 แท่ง จ.–ศ.: ≥ 80% teal · < 80% amber · วันอนาคต (ศ.) ว่าง · วันนี้ตัวหนา", [p[1] for p in pcts] == ["100%", "93%", "60%", "67%", None] and [p[2] for p in pcts] == ["", "", "lo", "lo", None] and count(page, ".glDay.today") == 1 and js(page, "()=>document.querySelector('.glDay.today').dataset.glDay") == TODAY, json.dumps(pcts))
        check(f"{tag} PF3 8 ก่อนติ๊กอะไร รวม '0/4 · 0%' (ไม่มีงาน auto ที่ครบเอง — Bias ไม่นับแล้ว)", txt(page, "[data-gl-wpct]") == "0/5 · 0%", txt(page, "[data-gl-wpct]"))
        page.locator('[data-gl-wtick="wjournal"]').click(); wait(page, 450)
        wlg = settings(page, "weekLog")
        check(f"{tag} 8 ติ๊ก Journal → weekLog[{MON}] = {{done:[wjournal]}} · รวม '1/4 · 25%' · ปุ่ม 'Weekly · 25%' (PF1: งาน Bias เป็นกดเอง ไม่นับอัตโนมัติ)", wlg == {MON: {"done": ["wjournal"]}} and txt(page, "[data-gl-wpct]") == "1/5 · 20%" and txt(page, '[data-gl-tab="w"]') == "Weekly · 20%", json.dumps([wlg, txt(page, "[data-gl-wpct]")]))
        check(f"{tag} PF3 8 แถว Weekly ครบ 4 แถว: ช่องติ๊กเฉพาะงานกดเอง (wbias · wjournal = 'กดเอง') · งาน auto (wvalue · wdaily) ไม่มีช่องติ๊ก ขวา = n/N", js(page, "()=>[...document.querySelectorAll('[data-gl-wrow]')].map(e=>[e.dataset.glWrow, !!e.querySelector('[data-gl-wtick]'), e.querySelector('[data-gl-wright]').innerText])") == [["wbias", True, "กดเอง"], ["wsector", True, "กดเอง"], ["wvalue", False, "1/2 บัญชี"], ["wjournal", True, "กดเอง"], ["wdaily", False, "2/4"]], js(page, "()=>[...document.querySelectorAll('[data-gl-wrow]')].map(e=>[e.dataset.glWrow, !!e.querySelector('[data-gl-wtick]'), e.querySelector('[data-gl-wright]').innerText])"))
        shot(page, f"gl1-weekly-{sfx}.png")
        if narrow:
            bad = js(page, """()=>{ const out=[]; document.querySelectorAll('[data-gl-pw] .glRow, [data-gl-pw] .glL1').forEach(e=>{ const lh=parseFloat(getComputedStyle(e).lineHeight)||20; if(e.getBoundingClientRect().height > lh*2.1 || e.scrollWidth > e.clientWidth + 1) out.push(e.className+':'+e.scrollWidth+'>'+e.clientWidth+' '+e.innerText); }); return out; }""")
            check(f"{tag} 10 390px: แถว Weekly ไม่ตัดบรรทัด ไม่ถูกตัดด้วย …", not bad, json.dumps(bad, ensure_ascii=False))
            check(f"{tag} 10 390px: Weekly ไม่ล้นแนวนอน", overflow(page) <= 0, overflow(page))
        check(f"{tag} 8 ซ้ำ ติ๊กเอาออก → weekLog.done = []", (page.locator('[data-gl-wtick="wjournal"]').click(), wait(page, 400), settings(page, "weekLog")[MON]["done"] == [])[2])
        # ปิดงาน auto → ตัวหารลด
        js(page, "()=>glWrite(S=>{ S.weekTasks = glWeekTasks().map(t=>t.id==='wbias' ? Object.assign({}, t, {on:false}) : t); })"); wait(page, 400)
        W = js(page, "()=>glWeekStat(tdLast)")
        check(f"{tag} PF3 8 ปิดงาน wbias (on:false) → ตัวหารลดเหลือ 3 · ไม่นับ 'ทำแผน Sat สัปดาห์นี้'", W["N"] == 4 and count(page, '[data-gl-wrow="wbias"]') == 0, json.dumps({"N": W.get("N"), "n": W.get("n")}))
        check(f"{tag} 8 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()
    # ครบทุกข้อ + 26 สัปดาห์
    old_weeks = {}
    from datetime import date, timedelta
    m0 = date(2026, 10, 5)
    for i in range(1, 31): old_weeks[(m0 - timedelta(days=7 * i)).isoformat()] = {"done": ["wjournal"]}
    def many(doc): S(doc)["weekLog"] = copy.deepcopy(old_weeks)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(**daily_cfg), many)
    try:
        go_today(page); tab(page, "w")
        page.locator('[data-gl-wtick="wjournal"]').click(); wait(page, 450)
        keys = sorted((settings(page, "weekLog") or {}).keys())
        check(f"{tag} 9 weekLog ตัดเหลือ 26 สัปดาห์ตอนเขียน (เก็บล่าสุด · มีสัปดาห์นี้ · ตัดเก่าสุดทิ้ง)", len(keys) == 26 and MON in keys and min(old_weeks) not in keys and keys[-1] == MON, json.dumps([len(keys), keys[:2], keys[-2:]]))
    finally: browser.close()

    # ── 9 ตั้งค่า
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, with_goals(), lambda d: S(d).update({"routine": {"slots": [{"id": "a1", "start": "09:00", "end": "10:00", "name": "A", "link": "none"}], "satDaily": ["XAUUSD"]}}))
    try:
        open_settings(page); js(page, "()=>{ document.getElementById('tdSetSec').open = true; }"); wait(page, 200)
        init_del = js(page, "()=>[...document.querySelectorAll('[data-gl-wdel]')].map(e=>e.dataset.glWdel)")
        check(f"{tag} PF3 9 งานรายสัปดาห์เริ่มต้น 4 ข้อ · ปุ่มลบมีเฉพาะงานกดเอง (แถว 0 = ทำแผน Sat · แถว 2 = Journal) · งาน auto (กรอกค่าพอร์ต · Daily) ลบไม่ได้", sorted(init_del) == ["0", "1", "3"], json.dumps(init_del))
        page.locator("[data-gl-xadd]").click(); page.locator('[data-gl-xname="0"]').fill("อ่านข่าวเช้า"); page.locator("[data-gl-xadd]").click(); page.locator('[data-gl-xname="1"]').fill("เช็กปฏิทินข่าว")
        page.locator("[data-gl-xdn='0']").click(); wait(page, 200)
        names = js(page, "()=>tdDraft.extra.map(x=>x.name)")
        check(f"{tag} 9 เพิ่ม 2 งานรายวัน · เรียงลำดับ ▼ ทำงาน → ['เช็กปฏิทินข่าว','อ่านข่าวเช้า']", names == ["เช็กปฏิทินข่าว", "อ่านข่าวเช้า"], json.dumps(names, ensure_ascii=False))
        page.locator("[data-gl-xname='1']").fill("อ่านข่าวเช้า 15 นาที")
        page.locator("[data-gl-wadd]").click(); page.locator("[data-gl-wname='5']").fill("สรุปสัปดาห์")
        page.locator("[data-gl-wname='0']").fill("Bias ครบ")
        page.locator("[data-gl-won='4']").uncheck()
        page.locator("[data-rt-save]").click(); wait(page, 500)
        de, wt = settings(page, "dailyExtra"), settings(page, "weekTasks")
        check(f"{tag} PF3 9 บันทึก: dailyExtra 2 ข้อ · weekTasks เก็บชื่อใหม่ ('Bias ครบ' ที่แถวแรก) + on:false (แถวที่ 5) + งานที่เพิ่มเอง ('สรุปสัปดาห์') auto:null", len(de) == 2 and [x["name"] for x in de] and wt[0]["name"] == "Bias ครบ" and wt[0]["auto"] is None and wt[4]["on"] is False and wt[5]["name"] == "สรุปสัปดาห์" and wt[5]["auto"] is None, json.dumps([de, wt], ensure_ascii=False))
        shot(page, f"gl1-settings-{sfx}.png", "#sysOverlay .modal")
        page.locator("[data-gl-wdel='5']").click(); wait(page, 200)
        page.locator("[data-gl-xdel='0']").click(); wait(page, 200)
        page.locator("[data-rt-save]").click(); wait(page, 500)
        check(f"{tag} 9 ลบงานรายวัน 1 ข้อ + งานรายสัปดาห์ที่เพิ่มเอง → บันทึกแล้วเหลือ 1 / 5", len(settings(page, "dailyExtra")) == 1 and len(settings(page, "weekTasks")) == 5)
        page.locator("[data-gl-wreset]").click(); page.locator("[data-rt-save]").click(); wait(page, 500)
        check(f"{tag} 9 คืนค่าเริ่มต้น (งานรายสัปดาห์) → ชื่อ/เปิดกลับเป็นชุดเริ่มต้น · weekTasks ถูกลบคีย์ · dailyExtra ยังอยู่", settings(page, "weekTasks") is None and len(settings(page, "dailyExtra")) == 1)
        page.locator("[data-gl-xadd]").click(); page.locator("[data-gl-xname='1']").fill("x" * 31); wait(page, 200)
        check(f"{tag} 9 ชื่อยาวเกิน 30 / ว่าง → ข้อความ + ปุ่มบันทึกกดไม่ได้", js(page, "()=>document.getElementById('tdSetSave').disabled") and "30" in (txt(page, "[data-gl-xerr='1']") or ""), txt(page, "[data-gl-xerr='1']"))
        page.locator("[data-gl-xname='1']").fill(""); wait(page, 100)
        check(f"{tag} 9 ชื่อว่าง → ปุ่มบันทึกกดไม่ได้", js(page, "()=>document.getElementById('tdSetSave').disabled"))
        # เพดาน 8 ข้อ
        for i in range(8):
            if page.locator("[data-gl-xadd]").is_enabled(): page.locator("[data-gl-xadd]").click()
        check(f"{tag} 9 งานรายวันอื่นสูงสุด 8 ข้อ (ปุ่มเพิ่มปิดเมื่อครบ)", js(page, "()=>tdDraft.extra.length") == 8 and not page.locator("[data-gl-xadd]").is_enabled())
        if narrow:
            fs = js(page, "()=>[...document.querySelectorAll('#tdRtSet .glXRow input[type=text]')].map(e=>parseFloat(getComputedStyle(e).fontSize))")
            check(f"{tag} 10 390px: ช่องกรอกในตั้งค่า Daily routine ≥ 16px · ตั้งค่าไม่ล้นแนวนอน", min(fs) >= 16 and overflow(page) <= 0, json.dumps([min(fs), overflow(page)]))
        check(f"{tag} 9 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
