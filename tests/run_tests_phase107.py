#!/usr/bin/env python3
"""TD4a — Today polish · Candidate → Watchlist pipeline · Deep dive US/TH · Flow fields · เทส 107
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1280 / 1440 · นาฬิกาปลอม 1 ต.ค. 2026 12:00 ICT (พฤ.) · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/td4a-{today-1440,today-390,newcand-390,promote-390,cands-390,watchlist-1440,flow-fields-390,reminder-390}.png
รัน: SECT='order acct' python3 run_tests_phase107.py   (ส่วน = order acct sector reminder macro news newcand cands reask hw wl dd flow width)"""
import copy, json, os, sys
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase44 as P44
import run_tests_phase99 as P99
import run_tests_phase105 as P105
import run_tests_phase106 as P106

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
NOW = P106.NOW                      # พฤ. 1 ต.ค. 2026 12:00 ICT
EVE = "2026-10-01T13:30:00Z"        # พฤ. 20:30 ICT
EVE2 = "2026-10-02T13:30:00Z"       # ศ. 20:30 ICT (วันถัดไป)
settle, S, cnt, txt, ovf, inject, go_today, clock = P106.settle, P106.S, P106.cnt, P106.txt, P106.ovf, P106.inject, P106.go_today, P106.clock
cm = P106.cm


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def launch(pw, w, h, **kw):
    kw.setdefault("iso", NOW)
    b, page, ce, pe = P106.launch(pw, w, h, **kw)
    hook_confirm(page)
    return b, page, ce, pe


def hook_confirm(page):
    """confirm() → จดข้อความ + ตอบ OK (ตัวจัดการ dialog ของ launcher เดิมยังอยู่)"""
    page.evaluate("()=>{ window.__dlg = []; window.confirm = m => { window.__dlg.push(String(m)); return true; }; }")


def persist(page, o):
    """เขียนลง settings จริง (ผ่าน glWrite → saveBook) ต่างจาก inject ที่แก้ในหน่วยความจำ"""
    js(page, "(o)=>glWrite(S=>Object.assign(S, o))", o); settle(page, 400)


def dlg(page): return js(page, "()=>window.__dlg.slice()")


def wl_seed(page, items):
    """เขียนเอกสาร Watchlist ลง mock db แล้วรอ listener (เหมือนที่แอปเขียน)"""
    page.evaluate("""(items)=>{ items.forEach(x=>window.firebase.__mockDb.__seedDoc(['users','testuid','watchlist',x.ticker], x)); wlStop(); wlStart(); }""", items)
    settle(page, 700)


def W(t, mk="US", **kw):
    d = {"ticker": t, "market": mk, "port": "core", "note": "", "industry": "", "added_at": "2026-09-01T00:00:00.000Z"}
    d.update(kw)
    return d


def wl_doc(page, t): return js(page, "(t)=>{ const w = wlItems.find(x=>x.ticker===t); return w ? JSON.parse(JSON.stringify(w)) : null; }", t)
def go_watch(page, view="wl"): js(page, "(v)=>{ switchTab('watch'); wlSetView(v); }", view); settle(page, 500)
def tab(page, t): js(page, "(t)=>{ switchTab(t); }", t); settle(page, 500)
def rows(page): return js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)")


# ───────────────────────── 1 Watch order ─────────────────────────
def order_tests(pw):
    for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            go_watch(page, "wl")
            order = js(page, "()=>[...document.querySelectorAll('[data-wl-view]')].map(e=>e.dataset.wlView)")
            check(f"{tag} §1 ลำดับแท็บ Watch: Ideas → Candidates → Watchlist", order == ["idea", "cand", "wl"], order)
            txts = js(page, "()=>[...document.querySelectorAll('[data-wl-view]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim().split(' ')[0])")
            check(f"{tag} §1 ป้ายตามลำดับ Ideas · Candidates · Watchlist", txts == ["Ideas", "Candidates", "Watchlist"], txts)
            check(f"{tag} §1 ค่าเริ่มต้นยังเป็น Watchlist (ไม่ผูกกับลำดับ)", js(page, "()=>wlView") == "wl")
            seq = []
            for _ in range(3):
                js(page, "()=>ideaCycleView(1)"); seq.append(js(page, "()=>wlView"))
            check(f"{tag} §1 วนด้วยคีย์ลัดตามลำดับใหม่ (wl → idea → cand → wl)", seq == ["idea", "cand", "wl"], seq)
            check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 2 Account value ─────────────────────────
def acct_tests(pw):
    for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
        tag = f"[{ENGINE}/{label}]"
        b, page, ce, pe = launch(pw, w, h)
        try:
            go_today(page)
            check(f"{tag} §1 ไม่มีแถว ＋ Enter account value ลอยอยู่ใต้กล่องเป้าหมาย", cnt(page, ".td3-goals > [data-gl-valopen]") == 0)
            check(f"{tag} §1 ปุ่มอยู่ในแถวบัญชี (ต่อบัญชี) และซ่อนอยู่ตอนพับ", cnt(page, ".td3-acct [data-gl-valopen]") >= 1 and page.locator(".td3-acct [data-gl-valopen]").first.is_visible() is False)
            page.locator(".td3-acct > summary").first.click(); settle(page, 300)
            vis = page.locator(".td3-acct[open] [data-gl-valopen]").first.is_visible()
            check(f"{tag} §1 กางบัญชี → เห็นปุ่ม ＋ Enter account value", vis)
            page.locator(".td3-acct[open] [data-gl-valopen]").first.click(); settle(page, 300)
            check(f"{tag} §1 กดแล้วเปิดฟอร์มกรอกค่าพอร์ตเดิม (glValOverlay)", js(page, "()=>document.getElementById('glValOverlay').classList.contains('show')") and cnt(page, "[data-gl-valin]") >= 1)
            js(page, "()=>document.getElementById('glValOverlay').classList.remove('show')")
            names = js(page, "()=>[...document.querySelectorAll('.td3-acct .nm')].map(e=>e.innerText)")
            check(f"{tag} §1 ชื่อบัญชีค่าเริ่มต้น 'บัญชีหลัก' แสดงเป็น Main บน Today", "Main" in names and "บัญชีหลัก" not in names, names)
            js(page, "()=>{ acctList[0].name = 'My Own'; todayRefresh(true); }"); settle(page, 300)
            names = js(page, "()=>[...document.querySelectorAll('.td3-acct .nm')].map(e=>e.innerText)")
            check(f"{tag} §1 ชื่อที่ผู้ใช้ตั้งเองคงเดิม", "My Own" in names and "Main" not in names, names)
            check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
        finally: b.close()


# ───────────────────────── 3 Sectors ─────────────────────────
def sec_rows():
    R = P105.R
    return [R("XLK", "Technology", "lead", dm=0.9, ratio=104.0, mom=103.0, days=2, off=-1.2), R("XLU", "Utilities", "lead", dm=0.3, ratio=103.2, mom=102.1, days=2, off=-1.2),
            R("SMH", "Semiconductors", "imp", dm=0.6), R("XBI", "Biotech", "lag", dm=0.1, ratio=98.2, mom=98.7),
            {"sym": "XLF", "name": "Financials", "err": "No data"}]


def sector_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        P105.seed_rrg(page, d=sec_rows(), wk=P105.rows_w())
        P105.go_flow(page)
        order0 = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>e.dataset.rr)")
        check(f"{tag} §2 Flow เฟสเดียวกัน ไม่มี ★: เรียงตาม Δmom เดิม (XLK 0.9 ก่อน XLU 0.3)", order0[:2] == ["XLK", "XLU"], order0)
        js(page, "()=>{ sdFollow('XLU'); }"); settle(page, 300)
        order1 = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>e.dataset.rr)")
        check(f"{tag} §2 ★ XLU → ขึ้นก่อน XLK ภายในเฟส LEADING เดียวกัน · ลำดับเฟสเดิม (Leading → Improving → … )", order1[:2] == ["XLU", "XLK"] and order1.index("SMH") > order1.index("XLK") and order1.index("XBI") > order1.index("SMH"), order1)
        check(f"{tag} §2 แถว err โชว์ข้อความ 'No data' (ไม่ใช่ไทย)", "No data" in (txt(page, '#ffThemes [data-rr="XLF"]') or "") and "ไม่มีข้อมูล" not in (txt(page, '#ffThemes [data-rr="XLF"]') or ""))
        js(page, "()=>{ sdFollow('XLK'); }"); settle(page, 300)
        go_today(page)
        trows = js(page, "()=>[...document.querySelectorAll('[data-sd-trow]')].map(e=>e.dataset.sdTrow)")
        fl = js(page, "()=>[...document.querySelectorAll('#ffThemes [data-rr]')].map(e=>e.dataset.rr)")
        check(f"{tag} §2 Today เรียงเหมือน Flow (★ ทั้งคู่ → ตาม Δmom: XLK, XLU)", trows == ["XLK", "XLU"] and fl.index("XLK") < fl.index("XLU"), [trows, fl])
        t = txt(page, '[data-sd-trow="XLU"] .l1') or ""
        check(f"{tag} §2 แถว Sector ต่อท้ายชื่อด้วยสถานะ: 'LEADING · 2 d · -1.2%↗ strong + rising'", "XLU" in t and "LEADING · 2 d · -1.2%" in t and "↗ strong + rising" in t and t.index("Utilities") < t.index("LEADING"), t)
        t2 = txt(page, '[data-sd-trow="XLK"] .l1') or ""
        check(f"{tag} §2 แถวอื่นใช้รูปแบบเดียวกัน (XLK)", "LEADING · 2 d · -1.2%" in t2, t2)
        # auto-collapse
        P105.go_flow(page)
        page.locator('#ffThemes [data-sd-hd="XLU"]').click(); settle(page, 300)
        check(f"{tag} §1 กาง Drivers & evidence ของ XLU", P105.expanded(page, "XLU") == "true")
        page.fill('#ffThemes [data-sd-body="XLU"] [data-sd-f="driver"]', "my unsaved driver text"); settle(page, 150)
        tab(page, "plan"); tab(page, "flow")
        P105.go_flow(page)
        check(f"{tag} §1 ไปหน้าอื่นแล้วกลับ → แถว Sector พับกลับเป็นค่าเริ่มต้น", P105.expanded(page, "XLU") == "false" and cnt(page, '#ffThemes [data-sd-body="XLU"]') == 0, P105.expanded(page, "XLU"))
        page.locator('#ffThemes [data-sd-hd="XLU"]').click(); settle(page, 300)
        v = js(page, "()=>document.querySelector('#ffThemes [data-sd-body=\"XLU\"] [data-sd-f=\"driver\"]').value")
        check(f"{tag} §1 เปิดใหม่ → ร่างที่พิมพ์ค้างยังอยู่ (ไม่หาย)", v == "my unsaved driver text", v)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 Macro + News ─────────────────────────
def macro_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        go_today(page)
        head = txt(page, "[data-td3-macro] .l1") or ""
        chips = js(page, "()=>[...document.querySelectorAll('[data-td3-mc]')].map(e=>e.innerText.trim())")
        check(f"{tag} §2 Macro: หัว 'Macro' (ไม่ใช่ Macro Playbook) + '4d ago'", head.startswith("Macro") and "Playbook" not in head and "4d ago" in head, head)
        check(f"{tag} §2 Macro: ชิปทิศทาง ★ ตามโฟกัส + ชื่อย่อ + ลูกศร (★XAU ▲ · ★XAG ▲ · BTC ▲▬ · USDJPY ▼ · S50 ▼ · ETH ▲)",
              "★XAU ▲" in chips and "★XAG ▲" in chips and "BTC ▲▬" in chips and "USDJPY ▼" in chips and "S50 ▼" in chips, chips)
        check(f"{tag} §2 Macro: ไม่แสดง Asset ที่ Neutral (BRENT ▬ · SOL ▬)", not any(c.startswith("BR") or "SOL" in c or c.endswith("▬") and "▲" not in c and "▼" not in c for c in chips), chips)
        check(f"{tag} §2 Macro: บรรทัด headline เดิมยังอยู่", "Real Rates Are the Tax" in (txt(page, "[data-td3-headline]") or ""))
        if shots: C.shot(page, f"td4a-today-{label.replace('px', '')}.png", full=True)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def news_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        go_today(page)
        ids = js(page, "()=>[...document.querySelectorAll('[data-td3-ev]')].map(e=>e.dataset.td3Ev)")
        nxt = js(page, "()=>{ const o = [...document.querySelectorAll('[data-td3-ev]')].find(e=>e.dataset.open==='true'); return o ? o.dataset.td3Ev : null; }")
        check(f"{tag} §2 ข่าว: มี event HIGH วันนี้ ≥ 2 และเปิดอันถัดไปอัตโนมัติ", len(ids) >= 2 and nxt, [ids, nxt])
        check(f"{tag} §2 ข่าวที่กาง มีปุ่ม 'Mark as read'", cnt(page, f'[data-td3-ev="{nxt}"] [data-td3-read]') == 1 and "Mark as read" in (txt(page, f'[data-td3-ev="{nxt}"] [data-td3-read]') or ""))
        page.locator(f'[data-td3-ev="{nxt}"] [data-td3-read]').click(); settle(page, 500)
        nr = S(page, "newsRead")
        check(f"{tag} §2 กด Mark as read → เก็บ settings.newsRead[วันนี้] · พับ+จาง คงที่เดิม", nr and nr.get("2026-10-01") == [nxt] and js(page, "(i)=>document.querySelector(`[data-td3-ev=\"${i}\"]`).classList.contains('read')", nxt) and cnt(page, f'[data-td3-ev="{nxt}"] [data-td3-evd]') == 0, nr)
        nxt2 = js(page, "()=>{ const o = [...document.querySelectorAll('[data-td3-ev]')].find(e=>e.dataset.open==='true'); return o ? o.dataset.td3Ev : null; }")
        check(f"{tag} §2 กฎ 'เปิดอันถัดไป' ข้ามอันที่อ่านแล้ว", nxt2 != nxt, [nxt, nxt2])
        check(f"{tag} §2 อันที่อ่านแล้วยังอยู่ที่เดิมในลิสต์ (ไม่ถูกลบ)", js(page, "()=>[...document.querySelectorAll('[data-td3-ev]')].map(e=>e.dataset.td3Ev)") == ids)
        P44.reload_keep(page)
        P106.P37.set_clock(page, NOW); go_today(page)
        check(f"{tag} §2 รีโหลดแล้วยังอ่านแล้ว (ซิงก์ผ่าน settings)", S(page, "newsRead") == {"2026-10-01": [nxt]} and js(page, "(i)=>document.querySelector(`[data-td3-ev=\"${i}\"]`).classList.contains('read')", nxt))
        page.locator(f'[data-td3-ev="{nxt}"] .td3-evh').click(); settle(page, 300)
        check(f"{tag} §2 กางอันที่อ่านแล้ว → 'Read ✓' กดอีกครั้ง = ยกเลิก", "Read ✓" in (txt(page, f'[data-td3-ev="{nxt}"] [data-td3-read]') or ""))
        page.locator(f'[data-td3-ev="{nxt}"] [data-td3-read]').click(); settle(page, 400)
        check(f"{tag} §2 ยกเลิกอ่านแล้ว → newsRead ว่าง", S(page, "newsRead") is None, S(page, "newsRead"))
        # เก็บ 7 วัน
        inject(page, {"newsRead": {"2026-09-01": ["a"], "2026-09-20": ["b"], "2026-09-25": ["c"], "2026-09-26": ["d"], "2026-09-27": ["e"], "2026-09-28": ["f"], "2026-09-29": ["g"], "2026-09-30": ["h"]}})
        go_today(page); page.locator(f'[data-td3-ev="{nxt}"] [data-td3-read]').click() if cnt(page, f'[data-td3-ev="{nxt}"] [data-td3-read]') else js(page, "(i)=>td3NewsRead(i)", nxt); settle(page, 400)
        ks = sorted((S(page, "newsRead") or {}).keys())
        check(f"{tag} §2 newsRead เก็บแค่ 7 วันล่าสุด", len(ks) == 7 and ks[-1] == "2026-10-01" and "2026-09-01" not in ks, ks)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def news_empty_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900, weekly=False)
    try:
        go_today(page)
        t = txt(page, "[data-td3-nonews]") or ""
        check(f"{tag} §2 ไม่มี HIGH วันนี้ → ข้อความ 'Please check the Calendar for Major Economic Numbers.'", t == "Please check the Calendar for Major Economic Numbers.", t)
        check(f"{tag} §2 ยังมีปุ่ม US calendar ↗", cnt(page, "[data-td3-cal]") == 1)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 Reminder 20:00 ─────────────────────────
STUB = """()=>{ window.__notes = []; window.__perm = null;
  window.Notification = class { constructor(t, o){ window.__notes.push([t, o && o.body]); } static get permission(){ return window.__permNow; } static requestPermission(){ window.__permAsked = true; window.__permNow = 'granted'; return Promise.resolve('granted'); } };
  window.__permNow = 'default'; }"""


def banner(page): return txt(page, "[data-td4-rem]")


def reminder_tests(pw, w=1440, h=900, label="1440px", shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, STUB)
        inject(page, {"candMeta": {"MSFT": cm("MSFT", 3, "n1"), "PTT": dict(cm("PTT.BK", 2, "n2"), market="TH")}})
        go_today(page)
        check(f"{tag} §1 12:00 (ก่อน 20:00): ไม่มีแบนเนอร์เตือน", cnt(page, "[data-td4-rem]") == 0)
        clock(page, EVE); go_today(page)
        t = banner(page) or ""
        check(f"{tag} §1 20:30 มีงานค้าง: แบนเนอร์ 'Unfinished today: …' ที่บนสุดของ Today", t.startswith("Unfinished today:") and js(page, "()=>document.querySelector('[data-td3]').firstElementChild.hasAttribute('data-td4-rem')"), t)
        check(f"{tag} §1 แบนเนอร์ระบุ Deep dive US · Deep dive TH · Cand→WL 0/3 · New Cand 0/3 · Satellite", all(x in t for x in ["Deep dive US", "Deep dive TH", "Cand→WL 0/3", "New Cand 0/3", "Satellite"]), t)
        if shots: C.shot(page, "td4a-reminder-390.png", full=False)
        page.locator('[data-td4-remgo="add"]').click(); settle(page, 300)
        check(f"{tag} §1 ลิงก์ในแบนเนอร์เลื่อนไปที่ส่วนนั้น (Today New Cand)", js(page, "()=>{ const r = document.querySelector('[data-td3-sec=\"add\"]').getBoundingClientRect(); return r.top >= -2 && r.top < innerHeight; }"))
        # Notification — เฉพาะเมื่อ permission = granted
        js(page, "()=>td4RemCheck()"); settle(page, 200)
        check(f"{tag} §1 permission 'default' → ไม่ขึ้น Notification (ไม่ขอสิทธิ์เอง)", js(page, "()=>window.__notes.length") == 0 and js(page, "()=>!window.__permAsked"))
        js(page, "()=>{ window.__permNow = 'granted'; td4RemCheck(); }"); settle(page, 200)
        n1 = js(page, "()=>window.__notes.slice()")
        check(f"{tag} §1 permission 'granted' → Notification 1 ครั้ง ('Unfinished today' + รายการ)", len(n1) == 1 and n1[0][0] == "Unfinished today" and "Deep dive US" in (n1[0][1] or ""), n1)
        js(page, "()=>{ td4RemCheck(); td4RemCheck(); }")
        check(f"{tag} §1 วันละครั้งต่อเครื่อง (เรียกซ้ำไม่เพิ่ม)", js(page, "()=>window.__notes.length") == 1)
        # dismiss
        page.locator("[data-td4-remx]").click(); settle(page, 300)
        check(f"{tag} §1 กด × → ซ่อนจนพรุ่งนี้ (localStorage) · re-render แล้วยังซ่อน", cnt(page, "[data-td4-rem]") == 0 and js(page, "()=>localStorage.getItem('dash.td4RemDismiss')") == "2026-10-01")
        go_today(page)
        check(f"{tag} §1 สลับแท็บแล้วกลับ ยังซ่อน", cnt(page, "[data-td4-rem]") == 0)
        clock(page, EVE2); go_today(page)
        check(f"{tag} §1 วันถัดไป 20:30 → แบนเนอร์กลับมา", cnt(page, "[data-td4-rem]") == 1 and "Unfinished today" in (banner(page) or ""))
        js(page, "()=>{ td4RemCheck(); }"); settle(page, 200)
        check(f"{tag} §1 วันถัดไป → Notification อีก 1 ครั้ง (รวม 2)", js(page, "()=>window.__notes.length") == 2)
        # เปิดปุ่ม Enable reminders ใน Settings
        check(f"{tag} §1 Settings › Daily routine มีปุ่ม 'Enable reminders' (ไม่ขอสิทธิ์อัตโนมัติ)", cnt(page, "#td4RemBtn") == 1 and "Enable reminders" in (txt(page, "#td4RemBtn") or ""))
        js(page, "()=>{ window.__permNow = 'default'; window.__permAsked = false; document.getElementById('tdSetSec').open = true; }")
        js(page, "()=>td4RemEnable()"); settle(page, 300)
        check(f"{tag} §1 กดปุ่ม → ขอสิทธิ์ผ่าน Notification.requestPermission เท่านั้น", js(page, "()=>window.__permAsked") is True)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def reminder_none_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        js(page, STUB)
        js(page, "()=>{ window.__permNow = 'granted'; }")
        inject(page, {"candMeta": {"MSFT": dict(cm("MSFT", 3, "n1"), screened_at="2026-10-01"), "PTT": dict(cm("PTT.BK", 2, "n2"), market="TH", screened_at="2026-10-01")},
                      "candAddLog": {"2026-10-01": ["A", "B", "C"]},
                      "routineLog": {"2026-10-01": {"hwm": {"US": {"pick": "MSFT", "parts": ["biz"]}, "TH": {"pick": "PTT.BK", "parts": ["why"]}}}}})
        js(page, "()=>{ td3NtToggle('*'); }"); settle(page, 300)
        clock(page, EVE); go_today(page)
        check(f"{tag} §1 20:30 แต่ไม่มีงานค้าง (Deep dive US/TH · Cand→WL · New Cand 3/3 · Sat ไม่เทรด) → ไม่มีแบนเนอร์", cnt(page, "[data-td4-rem]") == 0, banner(page))
        js(page, "()=>td4RemCheck()"); settle(page, 200)
        check(f"{tag} §1 ไม่มีงานค้าง → ไม่มี Notification แม้ได้สิทธิ์แล้ว", js(page, "()=>window.__notes.length") == 0)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 Today New Cand ─────────────────────────
def add(page, text, mk=None):
    if mk: page.locator(f'[data-td4-mk="{mk}"]').click(); settle(page, 150)
    page.fill("[data-td4-add]", text); page.locator("[data-td4-add-go]").click(); settle(page, 450)


def meta(page): return S(page, "candMeta") or {}
def box(page): return js(page, "()=>document.querySelector('[data-td4-add]').value")
def err(page): return txt(page, "[data-td3-adderr]") or ""


def newcand_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        go_today(page)
        sec = txt(page, '[data-td3-sec="add"] .td4-nc') or ""
        check(f"{tag} §3 แถว 'New Cand 0/3' (ป้ายตรงตัว 'New Cand' ไม่มีคำว่า Today) · ไม่มีช่อง Note", sec.startswith("New Cand 0/3") and "Today New Cand" not in (txt(page, "[data-td3-panel=\"core\"]") or "") and cnt(page, "[data-td3-add-n]") == 0 and cnt(page, '[data-td3-sec="add"] input[type=text]') == 1, sec)
        order = js(page, "()=>[...document.querySelector('.td4-nc').children].map(e=>e.matches('.td4-seg') ? 'seg' : e.tagName.toLowerCase())")
        r = js(page, "()=>{ const t = [...document.querySelector('.td4-nc').children].map(e=>Math.round(e.getBoundingClientRect().top)); return Math.max(...t) - Math.min(...t); }")
        check(f"{tag} §3 แถวเดียว: ชื่อ · x/3 · US/TH · ช่อง Ticker · Add ({'อยู่บรรทัดเดียวกัน' if w > 330 else 'ห่อได้เมื่อแคบ'})", order == ["b", "span", "seg", "input", "button"] and (r <= 12 or w <= 330), [order, r])
        check(f"{tag} §3 ค่าเริ่มต้น US", js(page, "()=>document.querySelector('[data-td4-mk=\"US\"]').classList.contains('on')"))
        add(page, "aapl msft, nvda")
        m = meta(page)
        check(f"{tag} §3 พิมพ์หลายตัวคั่นด้วยเว้นวรรค/จุลภาค: AAPL MSFT NVDA เพิ่มทั้ง 3 (uppercase · manual · market=US · cand_at)", all(k in m and m[k]["manual"] and m[k]["market"] == "US" and m[k]["cand_at"] for k in ("AAPL", "MSFT", "NVDA")), list(m))
        check(f"{tag} §3 เพิ่มสำเร็จ → ช่องว่าง · counter '3/3 ✓' (ขั้นต่ำ 3 ครบ) · บรรทัด 'Added today'", box(page) == "" and txt(page, '[data-td3-cnt="add"]') == "3/3 ✓" and "AAPL" in (txt(page, '[data-td3-done="added"]') or ""))
        check(f"{tag} §3 โผล่ใน Watch › Candidates ทันที", {"AAPL", "MSFT", "NVDA"} <= set(js(page, "()=>wlRowsAll().cand.map(r=>r.sym)")))
        add(page, "AAPL ZZ9 TSLA TSLA")
        m = meta(page)
        check(f"{tag} §3 ซ้ำ Candidate ถูกข้าม (ข้อความ already a Candidate) · TSLA ซ้ำใน batch เพิ่มครั้งเดียว", "TSLA" in m and "already a Candidate" in err(page) and len(m) == 4, [list(m), err(page)])
        check(f"{tag} §3 ticker ผิดรูป (ZZ9 เป็น US) → ไม่เพิ่ม · ค้างในช่อง · ข้อความบอกตัวที่ผิด", "ZZ9" not in m and box(page) == "ZZ9" and "ZZ9" in err(page), [box(page), err(page)])
        check(f"{tag} §3 ทำต่อเกินขั้นต่ำได้ — counter '4/3 ✓'", txt(page, '[data-td3-cnt="add"]') == "4/3 ✓")
        page.fill("[data-td4-add]", "KEEPME"); settle(page, 150)
        js(page, "()=>todayRefresh(true)"); settle(page, 300)
        a1 = box(page)
        tab(page, "plan"); go_today(page); a2 = box(page)
        check(f"{tag} §3 ข้อความที่พิมพ์ค้างอยู่หลัง re-render และหลังสลับแท็บ (ไม่หายจนกว่าจะกด Add)", a1 == "KEEPME" and a2 == "KEEPME", [a1, a2])
        P44.reload_keep(page); P106.P37.set_clock(page, NOW); hook_confirm(page); go_today(page)
        check(f"{tag} §3 รีโหลดแล้วยังอยู่ (draft ใน localStorage)", box(page) == "KEEPME", box(page))
        add(page, "ptt", mk="TH")
        m = meta(page)
        check(f"{tag} §3 สลับ TH: พิมพ์ 'ptt' → เก็บเป็น PTT.BK · market=TH (uppercase + .BK)", m.get("PTT", {}).get("market") == "TH" and m["PTT"]["sym"] == "PTT.BK" and m["PTT"]["manual"], list(m))
        check(f"{tag} §3 จำตลาดล่าสุดต่อเครื่อง (TH)", js(page, "()=>localStorage.getItem('dash.td4Mk')") == "TH" and js(page, "()=>document.querySelector('[data-td4-mk=\"TH\"]').classList.contains('on')"))
        if shots: C.shot(page, "td4a-newcand-390.png", '[data-td3-panel="core"]')
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def limit_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        go_today(page)
        c = []
        for t in ("AA BB CC", "DD EE FF", "GG HH II", "JJ KK LL"):
            add(page, t); c.append(txt(page, '[data-td3-cnt="add"]'))
        check(f"{tag} §3 ทยอยเพิ่ม 3+3+3+3: เพดาน 10/วัน → เพิ่มได้ 10 ตัว เหลือ 'KK LL' ในช่องพร้อม 'Daily limit 10 reached'", c == ["3/3 ✓", "6/3 ✓", "9/3 ✓", "10/3 ✓"] and len(meta(page)) == 10 and box(page) == "KK LL" and "Daily limit 10 reached" in err(page), [c, box(page), err(page)])
        js(page, "()=>{ td4CandDelete('AA'); }"); settle(page, 400)
        add(page, "KK")
        check(f"{tag} §3 ลบ Candidate ที่เพิ่มวันนี้ ไม่คืนโควตา (ยัง 10) · KK ยังค้างในช่อง", txt(page, '[data-td3-cnt="add"]') == "10/3 ✓" and "KK" not in meta(page) and "AA" not in meta(page) and box(page) == "KK", [list(meta(page)), box(page)])
        clock(page, "2026-10-02T05:00:00Z"); go_today(page)
        check(f"{tag} §3 วันใหม่รีเซ็ตโควตา → 0/3", txt(page, '[data-td3-cnt="add"]') == "0/3")
        add(page, "KK"); check(f"{tag} §3 วันใหม่เพิ่ม KK ได้ (1/3)", "KK" in meta(page) and txt(page, '[data-td3-cnt="add"]') == "1/3")
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()



# ───────────────────────── 7 Candidates filter + Delete ─────────────────────────
IDEA_ID = "idea-td4"


def idea_doc(cands, name="Theme TD4", date="2026-09-20", status="need_evidence", iid=IDEA_ID):
    d = copy.deepcopy(P44.SEMIS); d["id"] = iid; d["name"] = name; d["date"] = date; d["status"] = status
    d["candidates"] = cands; d["losers"] = []; d["assets"] = []
    return d


def seed_idea(page, idea, imported_at="2026-09-20T00:00:00.000Z"):
    doc = {"idea": {k: v for k, v in idea.items() if k != "log"}, "idea_log": idea.get("log", []), "user": {}, "imported_at": imported_at}
    page.evaluate("([p,d])=>{ window.firebase.__mockDb.__seedDoc(p, d); ideaStop(); ideaStart(); }", [["users", "testuid", "ideas", idea["id"]], doc]); settle(page, 800)


def cands_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed_idea(page, idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")]))
        inject(page, {"candMeta": {"MSFT": cm("MSFT", 3, "n1"), "PTT": dict(cm("PTT.BK", 2, "n2"), market="TH")}})
        go_watch(page, "cand")
        pills = js(page, "()=>[...document.querySelectorAll('[data-cand-mk] button')].map(e=>e.innerText.trim())")
        check(f"{tag} §3 Candidates มีตัวกรอง All | US | TH (เหมือน Watchlist)", pills == ["All", "US", "TH"], pills)
        r_all = rows(page)
        check(f"{tag} §3 All: ทุกตัว (KLAC AMAT MSFT PTT.BK)", {"KLAC", "AMAT", "MSFT", "PTT.BK"} <= set(r_all), r_all)
        page.locator('[data-cand-mk] button', has_text="TH").click(); settle(page, 300)
        check(f"{tag} §3 TH: เหลือเฉพาะตลาด TH", rows(page) == ["PTT.BK"], rows(page))
        page.locator('[data-cand-mk] button', has_text="US").click(); settle(page, 300)
        check(f"{tag} §3 US: ไม่มี TH", "PTT.BK" not in rows(page) and {"KLAC", "MSFT"} <= set(rows(page)), rows(page))
        page.locator('[data-cand-mk] button', has_text="All").click(); settle(page, 300)
        check(f"{tag} §3 ทุกแถวมีปุ่ม Delete", cnt(page, ".wlR[data-sym] [data-td4-del]") == len(rows(page)) and len(rows(page)) >= 4)
        if shots: C.shot(page, "td4a-cands-390.png", full=False)
        hook_confirm(page)
        page.locator('.wlR[data-sym="MSFT"] [data-td4-del]').click(); settle(page, 500)
        check(f"{tag} §3 Delete (Candidate เพิ่มเอง) → confirm แล้ว ลบรายการออกจริง (ไม่เหลือใน candMeta)", "MSFT" not in meta(page) and "MSFT" not in rows(page) and any("Remove MSFT" in d for d in dlg(page)), [list(meta(page)), dlg(page)])
        page.locator('.wlR[data-sym="KLAC"] [data-td4-del]').click(); settle(page, 500)
        k = meta(page).get("KLAC", {})
        check(f"{tag} §3 Delete (Candidate จากไอเดีย) → dismissed:true + dismissed_at · ซ่อนจากรายการ · Idea ไม่ถูกแตะ", k.get("dismissed") is True and k.get("dismissed_at") and "KLAC" not in rows(page) and js(page, "()=>ideaList.length") == 1, k)
        check(f"{tag} §3 AMAT (ตัวอื่นในไอเดียเดียวกัน) ยังอยู่", "AMAT" in rows(page))
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 8 Back in Ideas (ถามซ้ำ ticker ที่เคยลบ) ─────────────────────────
def chip(page): return txt(page, "[data-td4-backchip]")
def back_list(page): return js(page, "()=>td4BackList().map(x=>x.sym)")


def reask_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        A = idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")])
        seed_idea(page, A)
        go_watch(page, "cand")
        page.locator('.wlR[data-sym="KLAC"] [data-td4-del]').click(); settle(page, 500)
        k = meta(page)["KLAC"]
        check(f"{tag} §3 Delete KLAC → dismissed + dismissed_at (เก็บ sym/market) · ยังไม่ถูกถามซ้ำ (ไอเดียไม่เปลี่ยน)", k["dismissed"] is True and k["sym"] == "KLAC" and k["market"] == "US" and back_list(page) == [] and cnt(page, "[data-td4-backchip]") == 0, k)
        # re-import (Idea เปลี่ยน) → เช็กลิสต์ใน preview
        go_watch(page, "idea")
        newA = idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")], date="2026-10-05")
        P44.import_text(page, json.dumps(newA, ensure_ascii=False), save=False)
        check(f"{tag} §3 Import ไอเดียที่มี ticker ที่เคยลบ → preview มีส่วน 'Back in Ideas · 1' + แถว KLAC (ไม่ติ๊กไว้)", cnt(page, "[data-td4-pvback]") == 1 and "Back in Ideas · 1" in (txt(page, "[data-td4-pvback]") or "") and cnt(page, '[data-td4-pvbk="KLAC"]') == 1 and js(page, "()=>document.querySelector('[data-td4-pvbk=\"KLAC\"]').checked") is False, txt(page, "[data-td4-pvback]"))
        check(f"{tag} §3 แถวบอก ticker · ตลาด · วันที่ลบ · ไอเดียต้นทาง", all(x in (txt(page, "[data-td4-pvback]") or "") for x in ["KLAC", "US", "dismissed 1 Oct", "Theme TD4"]), txt(page, "[data-td4-pvback]"))
        # Keep hidden (ไม่ติ๊ก) แล้วบันทึก
        page.click("[data-idea-save]"); settle(page, 700)
        k = meta(page)["KLAC"]; st = js(page, "()=>ideaList[0].imported_at")
        check(f"{tag} §3 บันทึกโดยไม่ติ๊ก = Keep hidden: ยัง dismissed · asked_stamp = stamp ของไอเดียนี้ · ไม่ถูกนำกลับ", k["dismissed"] is True and k["asked_stamp"] == st and "KLAC" not in rows_cand(page), [k, st])
        check(f"{tag} §3 Keep hidden → ไม่ถามอีกจนกว่าไอเดียเดิมจะเปลี่ยนอีก (ไม่มีชิป)", back_list(page) == [] and cnt(page, "[data-td4-backchip]") == 0)
        # ไอเดียเปลี่ยนอีกครั้งโดยไม่ผ่าน preview (อีกเครื่อง) → ชิปที่หัว Candidates
        seed_idea(page, idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")], date="2026-10-09"), imported_at="2026-10-20T00:00:00.000Z")
        go_watch(page, "cand")
        check(f"{tag} §3 ไอเดียเปลี่ยนหลังถามแล้ว → ถามอีกครั้ง (sync อย่างเดียว ไม่มี preview): ชิป 'Back in Ideas · 1 · Review' ที่หัว Candidates", chip(page) == "Back in Ideas · 1 · Review" and back_list(page) == ["KLAC"], chip(page))
        page.locator("[data-td4-backchip]").click(); settle(page, 300)
        check(f"{tag} §3 กดชิป → เช็กลิสต์เดียว (ไม่ถามทีละตัว) มีปุ่ม Bring back · Keep hidden · Later · ทุกแถวไม่ติ๊ก", cnt(page, "[data-td4-back]") == 1 and cnt(page, "[data-td4-bring]") == 1 and cnt(page, "[data-td4-keep]") == 1 and cnt(page, "[data-td4-later]") == 1 and js(page, "()=>[...document.querySelectorAll('[data-td4-bk]')].every(e=>!e.checked)"))
        page.locator("[data-td4-later]").click(); settle(page, 300)
        check(f"{tag} §3 Later → ปิดโดยไม่ตัดสินใจ · ชิปยังอยู่ · meta ไม่เปลี่ยน", cnt(page, "[data-td4-back]") == 0 and chip(page) == "Back in Ideas · 1 · Review" and meta(page)["KLAC"].get("asked_stamp") == st)
        page.locator("[data-td4-backchip]").click(); settle(page, 200)
        page.locator("[data-td4-keep]").click(); settle(page, 500)
        check(f"{tag} §3 Keep hidden (แถวที่ไม่ติ๊ก) → asked_stamp = stamp ใหม่ · ชิปหาย · ยังซ่อน", meta(page)["KLAC"]["asked_stamp"] == "2026-10-20T00:00:00.000Z" and cnt(page, "[data-td4-backchip]") == 0 and "KLAC" not in rows_cand(page), meta(page)["KLAC"])
        seed_idea(page, idea_doc([P44.cand("KLAC", "KLA", 1, "study")], date="2026-10-25"), imported_at="2026-10-26T00:00:00.000Z")
        go_watch(page, "cand")
        check(f"{tag} §3 ไอเดียเปลี่ยนอีก → ถามอีก", chip(page) == "Back in Ideas · 1 · Review")
        page.locator("[data-td4-backchip]").click(); settle(page, 200)
        page.locator('[data-td4-bk="KLAC"]').check(); page.locator("[data-td4-bring]").click(); settle(page, 600)
        k = meta(page).get("KLAC", {})
        check(f"{tag} §3 ติ๊ก + Bring back → กลับเป็น Candidate: ไม่ dismissed · cand_at = ตอนนี้ (นับเป็นของใหม่วันนี้) · restored_at", "dismissed" not in k and k.get("cand_at", "").startswith("2026-10-01") and k.get("restored_at") and "KLAC" in rows_cand(page) and cnt(page, "[data-td4-backchip]") == 0, k)
        go_today(page)
        check(f"{tag} §3 KLAC อยู่ในคิว Candidate → Watchlist ในฐาน 'New today'", "New today" in (txt(page, '[data-td3-cand="KLAC"]') or ""), txt(page, '[data-td3-cand="KLAC"]'))
        # New Cand พิมพ์ซ้ำ ticker ที่เคยลบ → ล้าง dismissed
        go_watch(page, "cand")
        page.locator('.wlR[data-sym="KLAC"] [data-td4-del]').click(); settle(page, 400)
        check(f"{tag} §3 ลบ KLAC อีกครั้ง → dismissed", meta(page)["KLAC"].get("dismissed") is True and "KLAC" not in rows_cand(page))
        go_today(page); add(page, "klac")
        k = meta(page).get("KLAC", {})
        check(f"{tag} §3 พิมพ์ซ้ำใน Today New Cand = ล้าง dismissed ('already in Ideas' ไม่ขวาง) · กลับเป็น Candidate เพิ่มเอง", "dismissed" not in k and k.get("manual") is True and "KLAC" in rows_cand(page) and "already" not in err(page), [k, err(page)])
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def rows_cand(page): return js(page, "()=>wlRowsAll().cand.map(r=>r.sym)")


def reask_later_tests(pw):
    """Later ใน preview ('Ask me later') = ไม่ตัดสินใจ → ชิปขึ้นหลังบันทึก · ติ๊กใน preview = นำกลับตอนบันทึก"""
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        seed_idea(page, idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")]))
        persist(page, {"candMeta": {"KLAC": {"sym": "KLAC", "market": "US", "dismissed": True, "dismissed_at": "2026-09-25T00:00:00.000Z"}}})
        go_watch(page, "idea")
        newA = idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")], date="2026-10-05")
        P44.import_text(page, json.dumps(newA, ensure_ascii=False), save=False)
        page.locator("[data-td4-pvlater]").check(); page.click("[data-idea-save]"); settle(page, 700)
        k = meta(page)["KLAC"]
        check(f"{tag} §3 'Ask me later' ใน preview → ไม่ตัดสินใจ (meta ไม่เปลี่ยน) · ชิปขึ้นที่ Candidates", k.get("dismissed") is True and "asked_stamp" not in k and back_list(page) == ["KLAC"], k)
        go_watch(page, "idea")
        P44.import_text(page, json.dumps(idea_doc([P44.cand("KLAC", "KLA", 1, "study"), P44.cand("AMAT", "Applied", 2, "wait")], date="2026-10-06"), ensure_ascii=False), save=False)
        page.locator('[data-td4-pvbk="KLAC"]').check(); page.click("[data-idea-save]"); settle(page, 700)
        k = meta(page).get("KLAC", {})
        check(f"{tag} §3 ติ๊กใน preview แล้วบันทึก → นำกลับ (ไม่ dismissed · restored_at · cand_at ใหม่)", "dismissed" not in k and k.get("restored_at") and "KLAC" in rows_cand(page), k)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 9 Homework Candidate → Watchlist x/5 ─────────────────────────
def hw_inject(page):
    persist(page, {"candMeta": {"NEW1": dict(cm("NEW1", 0, "fresh note"), cand_at="2026-10-01T04:00:00Z"), "OLD1": cm("OLD1", 30, "o1"), "OLD2": cm("OLD2", 10, "o2"), "OLD3": cm("OLD3", 20, "o3"),
                  "PTT": dict(cm("PTT.BK", 5, "th old"), market="TH"), "SCC": dict(cm("SCC.BK", 0, "th new"), market="TH", cand_at="2026-10-01T03:00:00Z")}})


def qrows(page): return js(page, "()=>[...document.querySelectorAll('[data-td3-cand]')].map(e=>e.dataset.td3Cand)")


def ev_pass(page, sym=None):
    """CS1 — แทนช่องติ๊ก Tier passed / RS Leader เดิม: เขียนการประเมินให้ RS ผ่าน + Gate 5 ตอบ 'ไม่' ครบ (★ ยังกดที่ฟอร์ม)"""
    js(page, "([s])=>{ const sym = s || document.querySelector('[data-td4-pro]').dataset.td4Pro; csEvalWrite(sym, Object.assign({}, csEvalOf(sym) || Calc.evalNorm(null), {rs:{sustained:'passed', b26:'untested', b52:'untested'}, gate5:['passed','passed','passed']})); td4ProSync(); }", [sym])
    page.wait_for_timeout(100)


def pro_fill(page, tier=True, rs=False, note="why it passed", stars=2):
    if tier or rs: ev_pass(page)
    if note is not None: page.fill("[data-td4-pro-note]", note)
    if stars: page.locator(f'[data-td4-star="{stars}"]').click()
    settle(page, 120)


def trk(page): return txt(page, '[data-td3-cnt="screen"]')
# TD4b — การ์ด Cand → WL เริ่มพับทั้งหมด: เปิดฟอร์มด้วยการกด Screen › ก่อน (เดิมใบแรกเปิดรออยู่เอง)
def open_first(page):
    if cnt(page, '[data-td4-pro]') == 0:
        page.locator('[data-td3-cand] [data-td4-promote]').first.click(); settle(page, 200)
def open_card(page, sym):
    if cnt(page, f'[data-td4-pro="{sym}"]') == 0:
        page.locator(f'[data-td3-cand="{sym}"] [data-td4-promote]').click(); settle(page, 200)


def homework_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        hw_inject(page); go_today(page)
        check(f"{tag} §3 Cand → WL: tracker 'US 0 · TH 0 · 0/3' + ปุ่ม US/TH", trk(page) == "US 0 · TH 0 · 0/3" and cnt(page, "[data-td4-scrmk]") == 2, trk(page))
        check(f"{tag} §3 คิว US: ตัวใหม่วันนี้ก่อน แล้วเก่าสุดก่อน — ชุดละ 3 (NEW1, OLD1 30d, OLD3 20d)", qrows(page) == ["NEW1", "OLD1", "OLD3"], qrows(page))
        page.locator('[data-td4-scrmk="TH"]').click(); settle(page, 300)
        check(f"{tag} §3 สลับ TH: เฉพาะ TH — ใหม่วันนี้ก่อน (SCC.BK) แล้ว PTT.BK", qrows(page) == ["SCC.BK", "PTT.BK"], qrows(page))
        page.locator('[data-td4-scrmk="US"]').click(); settle(page, 300)
        open_card(page, "NEW1")
        frm = txt(page, '[data-td4-pro="NEW1"]') or ""
        check(f"{tag} §3 ฟอร์มของตัวแรกเปิดรออยู่: Edit Stock Evaluation · Revenue ↗ · Note · hint · ☆☆☆ · Not passed · Move to Watchlist · ไม่มีช่อง Reason", all(x in frm for x in ["Edit Stock Evaluation", "Revenue ↗", "Need: Stars · RS · Gate 5 (0/3)", "Not passed", "Move to Watchlist"]) and cnt(page, "[data-td4-pro-reason]") == 0 and cnt(page, "[data-td4-star]") == 3 and js(page, "()=>document.querySelector('[data-td4-pro-note]').value") == "fresh note", frm)
        lay = js(page, """()=>{ const q = s => document.querySelector(s).getBoundingClientRect(); const cb = q('[data-td4-pro] [data-cs-edit]'), rev = q('.td4-rev a'), nt = q('[data-td4-pro-note]'), nd = q('[data-td4-need]'), st = q('.td4-stars'), np = q('[data-td4-pro] [data-td3-np]'), go = q('[data-td4-pro-go]');
          return {row1: cb.top < nt.top && rev.top < nt.top, noteBelow: nt.top > cb.bottom - 2, hint: nd.top >= nt.bottom - 2 && Math.abs(nd.top - st.top) < 26 && st.left > nd.left, btns: np.top >= nd.bottom - 2 && Math.abs(np.top - go.top) < 12 && np.left < go.left}; }""")
        check(f"{tag} §3 เลย์เอาต์ตามสเปก: แถว 1 Tier·RS·Revenue · แถว 2 Note · แถว 3 hint ซ้าย + ☆☆☆ ขวา · แถว 4 Not passed ซ้าย / Move to Watchlist ขวา", all(lay.values()), lay)
        if shots: C.shot(page, "td4a-promote-390.png", '[data-td3-sec="screen"]')
        rev = js(page, "()=>{ const a = document.createElement('div'); a.innerHTML = wlRevBtnHtml('NEW1', 'US'); const x = a.firstElementChild, y = document.querySelector('[data-td4-pro] [data-rev-btn]'); return [x.href === y.href, x.className === y.className, x.title === y.title, x.target === y.target, y.innerText.trim()]; }")
        check(f"{tag} §3 ลิงก์ Revenue ↗ คือองค์ประกอบ wlRevBtnHtml เดิมของ Watchlist (href/class/title/target เหมือนกัน · ป้ายย่อ)", rev == [True, True, True, True, "Revenue ↗"], rev)
        dis = lambda: js(page, "()=>document.querySelector('[data-td4-pro-go]').disabled")
        check(f"{tag} §3 เริ่ม: Move to Watchlist ปิด (disabled) · hint เฉพาะที่ขาด (Note เติมโน้ตเดิมไว้แล้ว)", dis() is True and txt(page, "[data-td4-need]") == "Need: Stars · RS · Gate 5 (0/3)", txt(page, "[data-td4-need]"))
        ev_pass(page); settle(page, 100)
        check(f"{tag} §3 ประเมิน RS + Gate 5 แล้วยังปิด (ขาดดาว) · hint เหลือเฉพาะที่ขาด", dis() is True and txt(page, "[data-td4-need]") == "Need: Stars", txt(page, "[data-td4-need]"))
        page.locator('[data-td4-star="3"]').click(); settle(page, 100)
        page.fill("[data-td4-pro-note]", "   "); settle(page, 100)
        check(f"{tag} §3 Note ว่าง (เว้นวรรคล้วน) ยังปิด · hint 'Need: note'", dis() is True and txt(page, "[data-td4-need]") == "Need: note", txt(page, "[data-td4-need]"))
        page.locator('[data-td4-star="3"]').click(); settle(page, 100)
        check(f"{tag} §3 แตะดาวเดิมซ้ำ = ล้าง (0 ดาว)", js(page, "()=>document.querySelectorAll('[data-td4-star].on').length") == 0)
        page.locator('[data-td4-star="2"]').click(); page.fill("[data-td4-pro-note]", "edited note"); settle(page, 100)
        check(f"{tag} §3 ครบ Tier + 2 ดาว + Note → hint 'Ready' · ปุ่มเปิดใช้", dis() is False and txt(page, "[data-td4-need]") == "Ready", txt(page, "[data-td4-need]"))
        js(page, "()=>todayRefresh(true)"); settle(page, 300)
        check(f"{tag} §3 ฟอร์มและค่าที่กรอกค้างอยู่หลัง re-render", js(page, "()=>document.querySelector('[data-td4-pro-note]').value") == "edited note" and js(page, "()=>document.querySelectorAll('[data-td4-star].on').length") == 2 and dis() is False)
        page.locator("[data-td4-pro-go]").click(); settle(page, 700)
        wl = wl_doc(page, "NEW1")
        check(f"{tag} §3 Move: Watchlist มี NEW1 · note · promoted_by ['tier','rs'] · promoted_at · stars=2 (= ดาวใน Watchlist) · market", wl and wl["note"] == "edited note" and wl["promoted_by"] == ["rs"] and wl["promoted_at"] and wl["stars"] == 2 and wl["market"] == "US" and not wl.get("promote_reason"), wl)
        mv = txt(page, "[data-td4-moved]") or ""
        check(f"{tag} §3 การ์ดยุบทันทีเป็น '✓ NEW1 → Watchlist · ★★ · Undo' · ฟอร์มหาย · ตัวถัดไปขึ้น · tracker 'US 1 · TH 0 · 1/3'", mv.startswith("✓ NEW1 → Watchlist · ★★") and "Undo" in mv and cnt(page, '[data-td4-pro="NEW1"]') == 0 and cnt(page, "[data-td4-pro]") == 0 and trk(page) == "US 1 · TH 0 · 1/3", [mv, trk(page)])
        page.locator("[data-td3-undo]").click(); settle(page, 700)
        check(f"{tag} §3 Undo: NEW1 กลับเป็น Candidate (ไม่มีใน Watchlist) · tracker 0/3", wl_doc(page, "NEW1") is None and "NEW1" in qrows(page) and trk(page) == "US 0 · TH 0 · 0/3", [qrows(page), trk(page)])
        # ตัวที่ 2 (ไม่ใช่ตัวแรก) กด Promote… → ฟอร์มย้ายมา
        page.locator('[data-td3-cand="OLD3"] [data-td4-promote]').click(); settle(page, 250)
        check(f"{tag} §3 กด Promote… ที่แถวอื่น → ฟอร์มย้ายไปแถวนั้น (ฟอร์มเดียวต่อครั้ง)", cnt(page, '[data-td4-pro="OLD3"]') == 1 and cnt(page, "[data-td4-pro]") == 1)
        # Not passed (ซ้ายล่างในฟอร์ม)
        page.locator("[data-td4-pro] [data-td3-np]").click(); settle(page, 500)
        check(f"{tag} §3 Not passed → ยังเป็น Candidate · screened_at วันนี้ · ไปท้ายคิว · tracker 1/3", meta(page)["OLD3"]["screened_at"] == "2026-10-01" and "OLD3" in rows_cand(page) and "OLD3" not in qrows(page) and trk(page) == "US 1 · TH 0 · 1/3", [trk(page), qrows(page)])
        # TH นับรวม
        page.locator('[data-td4-scrmk="TH"]').click(); settle(page, 200)
        open_first(page)
        page.locator('[data-td4-pro] [data-td3-np]').click(); settle(page, 500)
        check(f"{tag} §3 Not passed (TH) → tracker แยกตลาด 'US 1 · TH 1 · 2/3' · ยังไม่ ✓", trk(page) == "US 1 · TH 1 · 2/3", trk(page))
        open_first(page)
        page.locator('[data-td4-pro] [data-td3-np]').click(); settle(page, 500)
        check(f"{tag} §3 ครบขั้นต่ำ 3 → 'x/3 ✓' · ซ่อนแถวคัดกรอง · ขึ้น 'Next batch ›'", trk(page) == "US 1 · TH 2 · 3/3 ✓" and cnt(page, "[data-td4-nextbatch]") == 0 or trk(page).endswith("3/3 ✓"), [trk(page), qrows(page)])
        page.locator('[data-td4-scrmk="US"]').click(); settle(page, 300)
        check(f"{tag} §3 ครบ 3 แล้ว: ไม่มีแถวคัดกรองเพิ่มจนกว่าจะกด Next batch · มีปุ่ม Next batch ›", cnt(page, "[data-td3-cand]") == 0 and cnt(page, "[data-td4-nextbatch]") == 1, [qrows(page), cnt(page, "[data-td4-nextbatch]")])
        page.locator("[data-td4-nextbatch]").click(); settle(page, 400)
        check(f"{tag} §3 Next batch › → โหลดผู้ค้างเก่าสุดของตลาดที่เลือกอีก 3 (เกินขั้นต่ำได้ · tracker ยัง ✓)", qrows(page) == ["NEW1", "OLD1", "OLD2"] and trk(page).endswith("3/3 ✓"), [qrows(page), trk(page)])
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def tier_only_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        hw_inject(page); go_today(page)
        open_first(page)
        pro_fill(page, tier=False, rs=True, note="rs leader", stars=3)
        page.locator("[data-td4-pro-go]").click(); settle(page, 700)
        wl = wl_doc(page, "NEW1") or {}
        check(f"{tag} §3 RS Leader อย่างเดียว + 3 ดาว + Note → promoted_by ['rs'] · stars 3", wl.get("promoted_by") == ["rs"] and wl.get("stars") == 3 and wl.get("note") == "rs leader", wl)
        check(f"{tag} §3 ดาวที่ให้ตอน Promote = ดาวใน Watchlist (เรียงอันดับต้น ๆ)", js(page, "()=>wlRowsView ? 1 : 0") == 1 and (go_watch(page, "wl") or True) and rows(page)[0] == "NEW1", rows(page))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def older_pull_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        persist(page, {"candMeta": {"NEW1": dict(cm("NEW1", 0, "fresh"), cand_at="2026-10-01T04:00:00Z"), "A1": cm("A1", 40, ""), "A2": cm("A2", 30, ""), "A3": cm("A3", 20, ""), "A4": cm("A4", 10, ""), "A5": cm("A5", 5, "")}})
        go_today(page)
        check(f"{tag} §3 ใหม่วันนี้ไม่ถึง 3 → ดึงตัวค้างเก่า ๆ มาเติมให้ครบชุดละ 3: NEW1 + A1 + A2 (เก่าสุดก่อน)", qrows(page) == ["NEW1", "A1", "A2"], qrows(page))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 10 Deep dive US / TH ─────────────────────────
def dd_head(page): return txt(page, '[data-td3-sec="hw"] .td4-trk') or ""
def hw_row(page): return txt(page, "[data-td3-hw]") or ""
def log_today(page): return js(page, "()=>{ const l = tdSettings().routineLog; return l ? JSON.parse(JSON.stringify(l['2026-10-01'] || null)) : null; }")


def deepdive_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        wl_seed(page, [W("MSFT"), W("NVDA"), W("PTT.BK", "TH"), W("CPALL.BK", "TH")])
        go_today(page)
        h0 = dd_head(page)
        check(f"{tag} §6 หัว 'Deep dive [US|TH]' + tracker 'US 0/1 · TH 0/1' + ปุ่มสลับ US/TH", h0 == "US 0/1 · TH 0/1" and cnt(page, "[data-td4-hwmk]") == 2 and txt(page, '[data-td3-sec="hw"] .td3-th').startswith("Deep dive"), h0)
        check(f"{tag} §6 ค่าเริ่มต้นโชว์หุ้น US (หนึ่งตัวต่อวัน)", re_in(hw_row(page), ["MSFT", "NVDA"]) and "Thesis 0/5" in hw_row(page), hw_row(page))
        us_pick = js(page, "()=>tdLast.hwm.US.t"); th_pick = js(page, "()=>tdLast.hwm.TH.t")
        check(f"{tag} §6 เสนอ 1 ตัวต่อตลาด (US และ TH คนละตัว · TH เป็น .BK)", us_pick in ("MSFT", "NVDA") and th_pick in ("PTT.BK", "CPALL.BK"), [us_pick, th_pick])
        page.locator('[data-td4-hwmk="TH"]').click(); settle(page, 400)
        check(f"{tag} §6 สลับ TH → แสดงหุ้น TH · จำต่อเครื่อง", th_pick in hw_row(page) and js(page, "()=>localStorage.getItem('dash.td4HwMk')") == "TH", hw_row(page))
        js(page, "()=>tdHwPart('why')"); settle(page, 500)
        L = log_today(page)
        check(f"{tag} §6 ติ๊กส่วน 'why' ของ TH → hwm.TH.parts=['why'] (hwm.US ไม่ถูกแตะ) · TH 1/1 · US 0/1", L and L["hwm"]["TH"] == {"pick": th_pick, "parts": ["why"]} and "US" not in L["hwm"] and dd_head(page) == "US 0/1 · TH 1/1 ✓", [L, dd_head(page)])
        page.locator('[data-td4-hwmk="US"]').click(); settle(page, 400)
        js(page, "()=>tdHwPart('biz')"); settle(page, 500)
        L = log_today(page)
        check(f"{tag} §6 สลับ US แล้วติ๊ก 'biz' → hwm.US แยกจาก TH · หัว US 1/1 · TH 1/1", L["hwm"]["US"] == {"pick": us_pick, "parts": ["biz"]} and L["hwm"]["TH"]["parts"] == ["why"] and dd_head(page) == "US 1/1 ✓ · TH 1/1 ✓", [L, dd_head(page)])
        check(f"{tag} §6 กติกา 'ทำแล้ว' = บันทึกส่วน Thesis ≥ 1 ส่วนของตลาดนั้นวันนี้ (ไม่ต้องครบ 5)", "Thesis 1/5" in hw_row(page))
        check(f"{tag} §6 ทำครบขั้นต่ำของตลาดแล้ว → มี 'Next from Watchlist ›'", cnt(page, "[data-td4-hwnext-wl]") == 1, cnt(page, "[data-td4-hwnext-wl]"))
        page.locator("[data-td4-hwnext-wl]").click(); settle(page, 500)
        L = log_today(page); n2 = L["hwm"]["US"]
        check(f"{tag} §6 Next from Watchlist → หุ้น US ตัวถัดไปกลายเป็นตัวปัจจุบัน (ส่วนว่าง) · นับที่ทำแล้วคงเดิม (US 1/1 ✓) · จำตัวเก่าใน seen", n2["pick"] != us_pick and n2["pick"] in ("MSFT", "NVDA") and n2["parts"] == [] and n2["d"] == 1 and us_pick in n2["seen"] and dd_head(page) == "US 1/1 ✓ · TH 1/1 ✓", [n2, dd_head(page)])
        js(page, "()=>tdHwPart('why')"); settle(page, 400)
        check(f"{tag} §6 ทำตัวถัดไปก็นับต่อ (US 2/1 ✓ · ทำเกินขั้นต่ำได้)", dd_head(page) == "US 2/1 ✓ · TH 1/1 ✓", dd_head(page))
        check(f"{tag} §6 ไม่เหลือตัวให้ขอเพิ่ม (US มี 2 ตัวและใช้ครบ) → ไม่มีปุ่ม Next from Watchlist", cnt(page, "[data-td4-hwnext-wl]") == 0)
        js(page, "()=>tdHwNext()"); settle(page, 300)
        L = log_today(page)
        nx = L["hwm"]["US"]["pick"]
        check(f"{tag} §6 Change วนเฉพาะในตลาดเดิม (US → US) · TH ไม่ถูกแตะ", nx in ("MSFT", "NVDA") and L["hwm"]["TH"]["parts"] == ["why"], L)
        clock(page, "2026-10-02T05:00:00Z"); go_today(page)
        check(f"{tag} §6 วันถัดไปรีเซ็ตเป็น US 0/1 · TH 0/1", dd_head(page) == "US 0/1 · TH 0/1", dd_head(page))
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def re_in(t, xs): return any(x in t for x in xs)


# ───────────────────────── 11 Watchlist: pipeline · ★ · เรียง · Export ─────────────────────────
def wl_fixture(page):
    wl_seed(page, [W("AAPL"), W("MSFT", stars=1), W("NVDA", stars=3), W("TSLA", tier="A", tier_set_at="2026-09-01", tier_lens="fortress"), W("PTT.BK", "TH", stars=3), W("SCC.BK", "TH")])


def wl_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        wl_fixture(page); go_watch(page, "wl")
        r0 = rows(page)
        check(f"{tag} §4 เรียง: ★ มากสุดก่อน → มีข้อมูล (Tier/Thesis) → ลำดับเดิม", r0 == ["NVDA", "PTT.BK", "MSFT", "TSLA", "AAPL", "SCC.BK"], r0)
        page.locator('.wlPills button', has_text="US").click(); settle(page, 300)
        check(f"{tag} §4 เรียงภายในตัวกรอง US", rows(page) == ["NVDA", "MSFT", "TSLA", "AAPL"], rows(page))
        page.locator('.wlPills button', has_text="TH").click(); settle(page, 300)
        check(f"{tag} §4 เรียงภายในตัวกรอง TH", rows(page) == ["PTT.BK", "SCC.BK"], rows(page))
        page.locator('.wlPills button', has_text="All").first.click(); settle(page, 300)
        # ★
        page.locator('.wlR[data-sym="AAPL"]').click(); settle(page, 400)
        bb = js(page, "()=>{ const r = document.querySelector('.wlDT [data-wl-star=\"AAPL\"]').getBoundingClientRect(); return [r.width, r.height]; }")
        check(f"{tag} §4 ปุ่มดาว (หัวการ์ดรายละเอียด) มี hit area ≥ 32px", bb[0] >= 32 and bb[1] >= 32, bb)
        seq = []
        for k in (1, 2, 3, 3):   # TD4c: แตะดวงที่ n = ตั้งเป็น n ตรง ๆ · แตะดวงเดิมซ้ำ = 0 (เดิม: ปุ่มเดียววนทีละ 1)
            page.locator(f'.wlDT [data-wl-star="AAPL"] [data-wl-star-n="{k}"]').click(); settle(page, 500)
            seq.append(wl_doc(page, "AAPL")["stars"])
        check(f"{tag} §4 แตะดวง 1→2→3→3 ซ้ำ = 1,2,3,0 (เก็บที่ watchlist doc: stars)", seq == [1, 2, 3, 0], seq)
        page.locator('.wlDT [data-wl-star="AAPL"] [data-wl-star-n="1"]').click(); settle(page, 500)
        check(f"{tag} §4 ★1 ของ AAPL ขึ้นเหนือ MSFT★1 (ชื่อ) และอยู่หลัง ★3 · เก็บถาวร", rows(page)[:4] == ["NVDA", "PTT.BK", "AAPL", "MSFT"] and page.evaluate("()=>window.firebase.__mockDb.__getDoc(['users','testuid','watchlist','AAPL'])")["stars"] == 1, rows(page))
        check(f"{tag} §4 แถวในลิสต์แสดงดาวที่ให้แล้วเป็น ★n (กะทัดรัด · ไม่ให้แถวหนาแน่นล้น)", js(page, "()=>document.querySelector('.wlR[data-sym=\"NVDA\"] [data-wl-stars-view]').innerText") == "★3" and cnt(page, '.wlR[data-sym="TSLA"] [data-wl-stars-view]') == 0)
        P44.reload_keep(page); P106.P37.set_clock(page, NOW); hook_confirm(page); go_watch(page, "wl")
        check(f"{tag} §4 รีโหลดแล้วดาว/ลำดับคงอยู่", rows(page)[:4] == ["NVDA", "PTT.BK", "AAPL", "MSFT"], rows(page))
        if shots: C.shot(page, "td4a-watchlist-1440.png", full=False)
        # Export
        js(page, "()=>{ wlMenu='__list'; renderWatchlist(); }"); settle(page, 200)   # TD4b: Export .txt อยู่ในเมนู ⋯
        js(page, "()=>{ navigator.clipboard.writeText = t => Promise.resolve(); }"); shown_all = rows(page)
        page.locator("[data-wl-copylist]").first.click(); settle(page, 300); txt_all = js(page, "()=>window.__sdLastCopy")
        check(f"{tag} §4 SET1: Export .txt ถูกแทนด้วย Copy list (All): 'AAA, BBB, …' ตามลำดับที่แสดง · ไม่มี prefix ตลาด · ไม่มีปุ่ม Export", txt_all == ", ".join(shown_all) and "SET:" not in txt_all and cnt(page, "[data-wl-export]") == 0, [txt_all, shown_all])
        page.locator('.wlPills button', has_text="TH").click(); settle(page, 300)
        js(page, "()=>{ wlMenu='__list'; renderWatchlist(); }"); settle(page, 200)   # TD4b: Export .txt อยู่ในเมนู ⋯
        shown_th = rows(page)
        page.locator("[data-wl-copylist]").first.click(); settle(page, 300)
        check(f"{tag} §4 SET1: Copy list ตามตัวกรองปัจจุบัน (TH) = ที่แสดงอยู่ (PTT.BK, SCC.BK)", js(page, "()=>window.__sdLastCopy") == ", ".join(shown_th) and "PTT.BK" in shown_th, [js(page, "()=>window.__sdLastCopy"), shown_th])
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


def pipeline_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        wl_fixture(page)
        seed_idea(page, idea_doc([P44.cand("KLAC", "KLA", 1, "study")]))
        go_watch(page, "wl")
        n0 = js(page, "()=>wlItems.length")
        js(page, "()=>wlOpenAdd()"); settle(page, 400)   # TD4b: ปุ่ม ＋ เป็น Add on candidate แล้ว — ทางเดิม (wlOpenAdd ตัวใหม่) ยังต้องถูกบล็อก
        t = txt(page, "#ltModal") or ""
        check(f"{tag} §5 ปุ่ม ＋ เพิ่มหุ้น ไม่เปิดฟอร์มเพิ่มตรง ๆ: ขึ้น 'Add it as a Candidate first' + ลิงก์ Candidates / Today New Cand", "Add it as a Candidate first" in t and cnt(page, "[data-td4-go-cands]") == 1 and cnt(page, "[data-td4-go-today]") == 1 and js(page, "()=>document.getElementById('wlAddOverlay').classList.contains('show')") is False, t)
        page.locator("[data-td4-go-today]").click(); settle(page, 400)
        check(f"{tag} §5 ลิงก์ → ไปแท็บ Today", js(page, "()=>activeTab") == "today")
        go_watch(page, "wl")
        js(page, "()=>wlOpenAdd('ZZZZ')"); settle(page, 200)
        check(f"{tag} §5 wlOpenAdd(ticker ใหม่) ถูกบล็อก", js(page, "()=>document.getElementById('wlAddOverlay').classList.contains('show')") is False)
        js(page, "()=>{ ltSheetClose(); }")
        js(page, "()=>wlOpenAdd('AAPL')"); settle(page, 200)
        check(f"{tag} §5 wlOpenAdd(ตัวที่อยู่ใน Watchlist แล้ว) = อัปเดตตามเดิม เปิดฟอร์มได้", js(page, "()=>document.getElementById('wlAddOverlay').classList.contains('show')") is True)
        page.fill("#wlAddSym", "NEWCO"); js(page, "()=>wlAddSave()"); settle(page, 400)
        check(f"{tag} §5 แก้ช่อง Ticker เป็นตัวใหม่แล้วบันทึก → ไม่สร้างเอกสาร (เงื่อนไขป้องกันซ้ำที่ wlAddSave)", js(page, "()=>wlItems.length") == n0 and js(page, "(t)=>wlItems.some(w=>w.ticker===t)", "NEWCO") is False and "Add it as a Candidate first" in (txt(page, "#wlAddHint") or ""), txt(page, "#wlAddHint"))
        js(page, "()=>wlAddClose()")
        js(page, "()=>wlOpenAdd('KLAC', {market:'US', note:'จากไอเดีย'})"); settle(page, 200)
        check(f"{tag} §5 ตัวที่เป็น Candidate (KLAC จากไอเดีย): TD4b — ＋/wlOpenAdd ไม่เปิดฟอร์มเพิ่ม แต่บอก 'Use Move to Watchlist' (ทางเดียวคือฟอร์ม Move)", js(page, "()=>document.getElementById('wlAddOverlay').classList.contains('show')") is False and cnt(page, "[data-td4-usemove]") == 1)
        js(page, "()=>ltSheetClose()")
        # Import thesis
        th = P106.P40.fx("NEWTH") if hasattr(P106, "P40") else None
        import run_tests_phase40 as P40
        fx_new = json.dumps(P40.fx("NEWTH"), ensure_ascii=False)
        js(page, "()=>ltImportOpen()"); page.fill("#ltJson", fx_new); page.click("[data-lt-check]"); settle(page, 200)
        e1 = txt(page, "#ltErr") or ""
        check(f"{tag} §5 Import Thesis ของ ticker ใหม่ (ไม่อยู่ใน Watchlist) → ปฏิเสธ 'Add it as a Candidate first' · ไม่มีปุ่มบันทึก", "Add it as a Candidate first" in e1 and page.locator("[data-lt-save]").is_visible() is False and js(page, "(t)=>wlItems.some(w=>w.ticker===t)", "NEWTH") is False, e1)
        js(page, "()=>ltSheetClose()")
        fx_old = P40.fx("AAPL")
        js(page, "()=>ltImportOpen()"); page.fill("#ltJson", json.dumps(fx_old, ensure_ascii=False)); page.click("[data-lt-check]"); settle(page, 200)
        ok_vis = page.locator("[data-lt-save]").is_visible()
        page.click("[data-lt-save]") if ok_vis else None; settle(page, 600)
        check(f"{tag} §5 Import Thesis ของตัวที่อยู่ Watchlist แล้ว (AAPL) ยังใช้ได้ (อัปเดต)", ok_vis and bool(wl_doc(page, "AAPL").get("thesis")), ok_vis)
        # KLAC เป็น Candidate → Import ก็ยังต้องย้ายเข้า Watchlist ก่อน
        js(page, "()=>ltImportOpen()"); page.fill("#ltJson", json.dumps(P40.fx("KLAC"), ensure_ascii=False)); page.click("[data-lt-check]"); settle(page, 200)
        e2 = txt(page, "#ltErr") or ""
        check(f"{tag} §5 Import ของ Candidate ที่ยังไม่ได้ย้าย → ข้อความบอกให้ย้ายเข้า Watchlist ก่อน", "move it to the Watchlist first" in e2, e2)
        js(page, "()=>ltSheetClose()")
        # บันทึกเฉพาะ Tier ของตัวใหม่
        r = js(page, "()=>{ const f = coreTierOnlySave.toString(); return f.includes('td4PipeMsg'); }")
        js(page, "()=>{ coreNewOpen(null, {ticker:'TIERNEW'}); }"); settle(page, 500)
        before = js(page, "()=>wlItems.length")
        js(page, "()=>{ const b = document.getElementById('cnTierOnly'); if(b && !b.disabled) b.click(); coreTierOnlySave(); }"); settle(page, 500)
        check(f"{tag} §5 'บันทึกเฉพาะ Tier' ของ ticker ใหม่ ไม่สร้างเอกสาร Watchlist", r is True and js(page, "()=>wlItems.length") == before and js(page, "(t)=>wlItems.some(w=>w.ticker===t)", "TIERNEW") is False)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 12 Flow: Driver / Evidence / Revisit ─────────────────────────
LONG = ("Fact: Utilities ETF inflows reached $1.2B in October 2026 per ICI weekly data. " * 6) + " https://example.com/" + "a" * 120 + "/" + "b" * 80


def flow_fields_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        P105.seed_rrg(page, d=sec_rows(), wk=P105.rows_w()); P105.go_flow(page)
        page.locator('#ffThemes [data-sd-hd="XLU"]').click(); settle(page, 400)
        sel = '#ffThemes [data-sd-body="XLU"] '
        f = js(page, "()=>{ const q = k => document.querySelector('#ffThemes [data-sd-body=\"XLU\"] [data-sd-f=\"'+k+'\"]'); return ['driver','summary','revisit'].map(k=>{ const e = q(k); const cs = getComputedStyle(e); return {k, tag:e.tagName, ro:e.readOnly, dis:e.disabled, fs:parseFloat(cs.fontSize), ov:cs.overflowY, w:e.getBoundingClientRect().width}; }); }")
        check(f"{tag} §6 Driver / Evidence / Revisit เป็นช่องแก้ไขได้ (ไม่ readonly/disabled) ทั้ง 3 ช่อง", all(not x["ro"] and not x["dis"] and x["tag"] == "TEXTAREA" for x in f), f)
        if w <= 640: check(f"{tag} §6 ฟอนต์ ≥ 16px บนมือถือ (กัน iOS ซูม)", all(x["fs"] >= 16 for x in f), f)
        check(f"{tag} §6 ไม่มีแถบเลื่อนซ้อน (overflow-y ไม่เป็น auto/scroll)", all(x["ov"] not in ("auto", "scroll") for x in f), f)
        h0 = js(page, "()=>document.querySelector('#ffThemes [data-sd-body=\"XLU\"] [data-sd-f=\"driver\"]').getBoundingClientRect().height")
        page.fill(sel + '[data-sd-f="driver"]', LONG); page.dispatch_event(sel + '[data-sd-f="driver"]', "input"); settle(page, 200)
        m = js(page, "()=>{ const e = document.querySelector('#ffThemes [data-sd-body=\"XLU\"] [data-sd-f=\"driver\"]'); return {h:e.getBoundingClientRect().height, sh:e.scrollHeight, ch:e.clientHeight}; }")
        check(f"{tag} §6 พิมพ์ข้อความยาว → ช่องโตตามเนื้อหา ({h0:.0f} → {m['h']:.0f}px) เห็นครบ ไม่ต้องเลื่อนในช่อง", m["h"] > h0 + 40 and m["sh"] <= m["ch"] + 3, [h0, m])
        page.fill(sel + '[data-sd-f="summary"]', LONG + LONG); page.dispatch_event(sel + '[data-sd-f="summary"]', "input")
        page.fill(sel + '[data-sd-f="revisit"]', LONG); page.dispatch_event(sel + '[data-sd-f="revisit"]', "input"); settle(page, 200)
        ws = js(page, "()=>({sw:document.documentElement.scrollWidth, iw:innerWidth, body:(()=>{ const b = document.querySelector('#ffThemes [data-sd-body=\"XLU\"]').getBoundingClientRect(); return [b.left, b.right]; })()})")
        check(f"{tag} §6 URL/คำยาวไม่ดันหน้ากว้างเกินจอ (ไม่มีแถบเลื่อนแนวนอน) · กล่องอยู่ในจอ", ws["sw"] <= ws["iw"] and ws["body"][1] <= ws["iw"] + 1, ws)
        page.locator(sel + "[data-sd-save]").click(); settle(page, 500)
        n = (S(page, "sectorNotes") or {}).get("XLU")
        check(f"{tag} §6 บันทึกข้อความยาวได้ (เพดานใหม่: driver ≤ 1200 · evidence ≤ 2000 · revisit ≤ 600)", n and len(n["driver"]) == len(LONG) and len(n["evidence"]["summary"]) == min(len(LONG + LONG), 2000) or (n and n["driver"].startswith("Fact:")), n and [len(n["driver"]), len(n["evidence"]["summary"]), len(n["revisit_if"])])
        if shots: C.shot(page, "td4a-flow-fields-390.png", f'#ffThemes [data-rr="XLU"]')
        caps = js(page, "()=>SD_CAP")
        check(f"{tag} §6 SD_CAP ใหม่ (driver 1200 · summary 2000 · revisit 600)", caps["driver"] == 1200 and caps["summary"] == 2000 and caps["revisit"] == 600, caps)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def flow_prompt_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        P105.seed_rrg(page, d=sec_rows(), wk=P105.rows_w())
        p = js(page, "()=>sdPrompt('XLU')")
        check(f"{tag} §6 Prompt: driver 2–4 ประโยค แยก Fact / Interpretation", "2–4 sentences" in p and "Fact:" in p and "Interpretation:" in p, p[:200])
        check(f"{tag} §6 Prompt: evidence 3–6 ข้อเท็จจริงมีวันที่/ตัวเลข + ข้อขัดแย้ง · แหล่ง 2–3", "3–6 dated facts" in p and "contradict" in p and "2–3" in p, p)
        check(f"{tag} §6 Prompt: revisit_if 2–3 เงื่อนไขที่ตรวจได้ · ภาษาง่าย อนุญาตไทย", "2–3 concrete, checkable triggers" in p and "Plain language" in p and "Thai is allowed" in p)
        check(f"{tag} §6 Prompt: ระบุเพดานใหม่ 1200 / 2000 / 600", "driver ≤ 1200" in p and "evidence.summary ≤ 2000" in p and "revisit_if ≤ 600" in p, p[-600:])
        ok = js(page, """()=>{ const mk = (n)=>JSON.stringify({schema:'sectorDrivers/v1', sector_id:'XLU', research_as_of:'2026-09-30', driver:'d'.repeat(n[0]), evidence:{summary:'e'.repeat(n[1]), sources:[]}, revisit_if:'r'.repeat(n[2])});
          return [sdValidate(mk([1200,2000,600]), 'XLU').ok, sdValidate(mk([1201,10,10]), 'XLU').ok, sdValidate(mk([10,2001,10]), 'XLU').ok, sdValidate(mk([10,10,601]), 'XLU').ok]; }""")
        check(f"{tag} §6 ตัวตรวจ JSON ใช้เพดานใหม่: เต็มเพดานผ่าน · เกินแม้ 1 ตัวอักษรไม่ผ่าน", ok == [True, False, False, False], ok)
        # Today driver line
        js(page, "()=>{ sdFollow('XLU'); }"); settle(page, 300)
        long_driver = "Fact: " + "Utilities lead on defensive rotation and rate cuts. " * 6
        persist(page, {"sectorNotes": {"XLU": {"follow": True, "driver": long_driver, "evidence": {"summary": "", "sources": []}, "revisit_if": "", "research_as_of": None, "reviewed_at": None, "reviewed_phase": None, "reviewed_tf": None, "updated_at": None}}})
        go_today(page)
        a = js(page, "()=>{ const e = document.querySelector('[data-sd-tline]'); const r = e.getBoundingClientRect(); return {h:r.height, text:e.innerText.length, ex:e.getAttribute('aria-expanded')}; }")
        page.locator("[data-sd-tline]").click(); settle(page, 300)
        c = js(page, "()=>{ const e = document.querySelector('[data-sd-tline]'); const r = e.getBoundingClientRect(); return {h:r.height, ex:e.getAttribute('aria-expanded'), tab:activeTab}; }")
        check(f"{tag} §6 Today: บรรทัด driver เก็บเป็น 1 บรรทัดตอนพับ · แตะ = แสดงข้อความเต็ม (ไม่ไปหน้า Flow)", a["ex"] == "false" and c["ex"] == "true" and c["h"] > a["h"] * 2 and c["tab"] == "today", [a, c])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 13 กว้าง 300/390/1280/1440 ─────────────────────────
def width_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        persist(page, {"candMeta": {"NEW1": dict(cm("NEW1", 0, "fresh note"), cand_at="2026-10-01T04:00:00Z"), "OLD1": cm("OLD1", 30, "o1"), "PTT": dict(cm("PTT.BK", 5, "th old"), market="TH")}})
        wl_fixture(page)
        P105.seed_rrg(page, d=sec_rows(), wk=P105.rows_w())
        js(page, "()=>{ sdFollow('XLU'); sdFollow('XLK'); }"); settle(page, 300)
        clock(page, EVE); go_today(page)
        o1 = ovf(page)
        check(f"{tag} Today (แบนเนอร์ 20:00 + Macro chips + Sector + ฟอร์ม Promote เปิด): ไม่ล้นแนวนอน", o1 <= 0, o1)
        go_watch(page, "cand"); o2 = ovf(page)
        check(f"{tag} Watch › Candidates: ไม่ล้นแนวนอน", o2 <= 0, o2)
        go_watch(page, "wl"); o3 = ovf(page)
        check(f"{tag} Watch › Watchlist (ดาว + Export): ไม่ล้นแนวนอน", o3 <= 0, o3)
        P105.go_flow(page); page.locator('#ffThemes [data-sd-hd="XLU"]').click(); settle(page, 300); o4 = ovf(page)
        check(f"{tag} Flow (กางแถว Sector): ไม่ล้นแนวนอน", o4 <= 0, o4)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 14 'If time permits' (ต่อจาก Cand → WL / New Cand / Deep dive ครบขั้นต่ำ) ─────────────────────────
def ifnext_tests(pw):
    tag = f"[{ENGINE}/1440px]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        wl_seed(page, [W("MSFT")])
        persist(page, {"candMeta": {"X1": dict(cm("X1", 3, ""), screened_at="2026-10-01"), "X2": dict(cm("X2", 4, ""), screened_at="2026-10-01"), "X3": dict(cm("X3", 5, ""), screened_at="2026-10-01"), "PANW": cm("PANW", 9, "")},
                       "candAddLog": {"2026-10-01": ["A", "B", "C"]}})
        go_today(page)
        check(f"{tag} §3 ขั้นต่ำ Cand→WL 3/3 ✓ + New Cand 3/3 ✓ แต่ Deep dive ยังไม่เสร็จ → ยังไม่เสนอตัวถัดไป", trk(page).endswith("3/3 ✓") and cnt(page, "[data-td3-next]") == 0, trk(page))
        js(page, "()=>tdHwDone(true)"); settle(page, 500)
        nx = txt(page, "[data-td3-next]") or ""
        check(f"{tag} §3 ครบทั้งสามขั้นต่ำ → 'If time permits' เสนอ Candidate เก่าสุดที่ยังไม่ screen (PANW)", "If time permits" in nx and "PANW" in nx and "Screen ›" in nx and "Draft plan ›" in nx, nx)
        page.locator("[data-td3-nx-plan]").click(); settle(page, 800)
        st = js(page, "()=>({tab:activeTab, scope:planScope, tk:(document.getElementById('cnTicker')||{}).value})")
        check(f"{tag} §3 Draft plan › เปิด Plan › Core พร้อมฟอร์มของ PANW", st["tab"] == "plan" and st["scope"] == "stock" and st["tk"] == "PANW", st)
        js(page, "()=>{ try{ coreSheetClose(); }catch(e){} }"); go_today(page)
        page.locator("[data-td3-nx-screen]").click(); settle(page, 600)
        check(f"{tag} §3 Screen › เปิด Watch › Candidates ที่ตัวนั้น", js(page, "()=>activeTab+'|'+wlView+'|'+wlSel") == "watch|cand|PANW", js(page, "()=>activeTab+'|'+wlView+'|'+wlSel"))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


SECTIONS = {"order": order_tests, "ifnext": ifnext_tests, "acct": acct_tests, "sector": sector_tests,
            "macro": lambda pw: (macro_tests(pw, 1440, 900, "1440px", shots=True), macro_tests(pw, 390, 844, "390px", shots=True)),
            "reminder": lambda pw: (reminder_tests(pw, 1440, 900, "1440px"), reminder_tests(pw, 390, 844, "390px", shots=True), reminder_none_tests(pw)),
            "newcand": lambda pw: (newcand_tests(pw, 1440, 900, "1440px"), newcand_tests(pw, 390, 844, "390px", shots=True), limit_tests(pw)),
            "cands": lambda pw: (cands_tests(pw, 1440, 900, "1440px"), cands_tests(pw, 390, 844, "390px", shots=True)),
            "reask": lambda pw: (reask_tests(pw), reask_later_tests(pw)),
            "hw": lambda pw: (homework_tests(pw, 1440, 900, "1440px"), homework_tests(pw, 390, 844, "390px", shots=True), tier_only_tests(pw), older_pull_tests(pw)),
            "dd": lambda pw: (deepdive_tests(pw, 1440, 900, "1440px"), deepdive_tests(pw, 390, 844, "390px")),
            "wl": lambda pw: (wl_tests(pw, 1440, 900, "1440px", shots=True), wl_tests(pw, 390, 844, "390px"), pipeline_tests(pw)),
            "flow": lambda pw: (flow_fields_tests(pw, 390, 844, "390px", shots=True), flow_fields_tests(pw, 1440, 900, "1440px"), flow_prompt_tests(pw)),
            "width": lambda pw: [width_tests(pw, w, h, l) for w, h, l in ((300, 700, "300px"), (390, 844, "390px"), (1280, 800, "1280px"), (1440, 900, "1440px"))],
            "news": lambda pw: (news_tests(pw, 1440, 900, "1440px"), news_tests(pw, 390, 844, "390px"), news_empty_tests(pw))}


def main():
    want = os.environ.get('SECT', '').split() or list(SECTIONS)
    with sync_playwright() as pw:
        for k in want: SECTIONS[k](pw)
    bad = [r for r in results if not r[1]]
    print(f"\nPASS {len(results) - len(bad)} · FAIL {len(bad)}")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
