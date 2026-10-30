#!/usr/bin/env python3
"""TD4c — Today/Watch interaction polish · เทส 109
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1280 / 1440 · นาฬิกาปลอม 1 ต.ค. 2026 12:00 ICT (พฤ.) · ข้อมูล SAMPLE ล้วน
ภาพ tests/screenshots/td4c-{today-390,today-1440,sectors-390,watch-stars-390,deepdive-390,risk-390,risk-table-390}.png
รัน: SECT='sectors stars cand' python3 run_tests_phase109.py   (ส่วน = sectors stars cand sat deep scroll macro risk width)"""
import copy, json, os, sys
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase39 as P39
import run_tests_phase44 as P44
import run_tests_phase105 as P105
import run_tests_phase106 as P106
import run_tests_phase107 as T

ENGINE = base.BROWSER_ENGINE
results = []
js, settle, txt, cnt, ovf = T.js, T.settle, T.txt, T.cnt, T.ovf
go_today, go_watch, wl_seed, W, wl_doc, persist, launch = T.go_today, T.go_watch, T.wl_seed, T.W, T.wl_doc, T.persist, T.launch
NOW = T.NOW
P39.TD3_OTHER_DEV = False   # ชุดนี้ดู Today จริง (ไม่มี Other ▸)
LOG = {}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def scroll_y(page): return js(page, "()=>Math.round(window.pageYOffset)")


def scroll_to_sel(page, sel):
    js(page, "(s)=>{ const e = document.querySelector(s); if(e) e.scrollIntoView({block:'center'}); }", sel); settle(page, 250)


# ───────────────────────── 1 Sectors ─────────────────────────
def sector_rows(): return T.sec_rows()


def follow(page, *syms):
    js(page, "(l)=>{ l.forEach(s=>sdFollow(s)); }", list(syms)); settle(page, 300)


def sectors_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        P105.seed_rrg(page, d=sector_rows(), wk=P105.rows_w())
        follow(page, "XLU", "XLK")
        # Flow (อ้างอิง)
        P105.go_flow(page)
        flow = {s: (txt(page, f'#ffThemes [data-rr="{s}"] .l1') or "") for s in ("XLU", "XLK")}
        go_today(page)
        hdr = js(page, "()=>[...document.querySelectorAll('[data-td3-panel=\"ov\"] *')].filter(e=>e.children.length===0 && /^sectors?$/i.test(e.innerText.trim())).length")
        th = txt(page, "[data-sd-th]") or ""
        check(f"{tag} §1 หัวเดียว 'Sectors · Daily' (ไม่มีป้าย SECTORS ซ้อนบน)", hdr == 0 and cnt(page, ".td3-sh") == 0 and th.startswith("Sectors · Daily") and cnt(page, "[data-sd-th]") == 1, [hdr, th])
        t = txt(page, '[data-sd-trow="XLU"] .l1') or ""
        met = txt(page, '[data-sd-trow="XLU"] [data-sd-met]') or ""
        check(f"{tag} §1 แถวขวา = 'LEADING · 2 d · -1.2%' + '↗ strong + rising' (เหมือน Flow)", "LEADING" in t and "· 2 d · -1.2%" in met and "↗ strong + rising" in t, [t, met])
        same = all(("LEADING · 2 d · -1.2%" in flow[s].replace("  ", " ")) == ("LEADING · 2 d · -1.2%" in (txt(page, f'[data-sd-trow="{s}"] .l1') or "")) for s in flow)
        up_flow = "↗ strong + rising" in flow["XLU"]
        check(f"{tag} §1 ค่าตรง Flow ทั้ง 2 แถว (เฟส/วัน/OFF52W/↗)", same and up_flow, flow)
        side = js(page, "()=>{ const r = document.querySelector('[data-sd-trow=\"XLU\"]').getBoundingClientRect(), p = document.querySelector('[data-sd-trow=\"XLU\"] .sd-rt').getBoundingClientRect(); return {rowR:r.right, rtR:p.right, rtL:p.left, rowL:r.left, rowW:r.width, nmT:document.querySelector('[data-sd-trow=\"XLU\"] .sd-nm').getBoundingClientRect().top, rtT:p.top}; }")
        check(f"{tag} §1 กลุ่มสถานะชิดขวาของแถว", abs(side["rowR"] - side["rtR"]) <= 14, side)
        check(f"{tag} §1 ไม่ล้นแนวนอน", ovf(page) <= 0, ovf(page))
        if shots and label == "390px": C.shot(page, "td4c-sectors-390.png", sel='[data-sd-today]')
        # stale: แคชเมื่อวาน → ยังมีค่า + as of · ไม่มี Revisit
        js(page, """()=>{ const n = Object.assign({}, tdSettings().sectorNotes || {}); n.XLU = Object.assign(sdBlank(), n.XLU || {}, {follow:true, driver:'d', reviewed_at:'2026-09-20T00:00:00Z', reviewed_phase:'IMPROVING', reviewed_tf:'D'}); tdSettings().sectorNotes = n; todayRefresh(true); }"""); settle(page, 300)
        fresh_flag = cnt(page, '[data-sd-trow="XLU"] [data-sd-flag]')
        check(f"{tag} §1 ข้อมูลวันนี้ + เฟสต่างจากที่รีวิว → มี Revisit (กติกา TD3b ยังอยู่)", fresh_flag == 1, fresh_flag)
        P105.seed_rrg(page, d=sector_rows(), wk=P105.rows_w(), day="2026-09-29"); go_today(page)
        t2 = txt(page, '[data-sd-trow="XLU"] .l1') or ""
        asof = txt(page, "[data-sd-asof]") or ""
        check(f"{tag} §1 แคชเก่า → ยังโชว์ค่า (LEADING · 2 d · -1.2%) + 'as of 29 Sep' ที่หัว", "LEADING" in t2 and "-1.2%" in t2 and asof == "as of 29 Sep", [t2, asof])
        check(f"{tag} §1 แคชเก่า → ไม่มี Revisit (ธงเฉพาะข้อมูลวันนี้)", cnt(page, "[data-sd-flag]") == 0, cnt(page, "[data-sd-flag]"))
        # ไม่มีแคช
        js(page, "()=>{ const f = ffState(); f.rrg = {rowsD:[], rowsW:[], day:'', at:'', loading:false, err:''}; }"); go_today(page)
        t3 = txt(page, '[data-sd-trow="XLU"] .l1') or ""
        check(f"{tag} §1 ไม่มีแคช → '—' + 'Open Flow to refresh ›' (ไม่ดึงจาก Today)", "—" in t3 and "Open Flow to refresh ›" in t3 and cnt(page, "[data-sd-flag]") == 0 and cnt(page, "[data-sd-asof]") == 0, t3)
        n_fetch = js(page, "()=>!!(ffState().rrg && ffState().rrg.loading)")
        check(f"{tag} §1 Today ไม่สั่งดึงราคา (loading=false)", n_fetch is False, n_fetch)
        page.locator("[data-sd-openflow]").first.click(); settle(page, 500)
        check(f"{tag} §1 กด Open Flow to refresh › → ไปแท็บ Flow", js(page, "()=>activeTab") == "flow")
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 2 Watch stars ─────────────────────────
def stars_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        wl_seed(page, [W("AAPL"), W("MSFT", stars=1)])
        go_watch(page, "wl")
        page.locator('.wlR[data-sym="AAPL"]').click(); settle(page, 400)
        sel = lambda k: f'.wlDT [data-wl-star="AAPL"] [data-wl-star-n="{k}"]'
        bb = js(page, "()=>[...document.querySelectorAll('.wlDT [data-wl-star=\"AAPL\"] [data-wl-star-n]')].map(e=>{ const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })")
        check(f"{tag} §2 ดาว 3 ดวง แต่ละดวงกดได้ ≥ 32px", len(bb) == 3 and all(x[0] >= 32 and x[1] >= 32 for x in bb), bb)
        page.locator(sel(3)).click(); settle(page, 500)
        s1 = wl_doc(page, "AAPL")["stars"]
        check(f"{tag} §2 แตะดวงที่ 3 → ตั้งเป็น 3 ทันที (ไม่ใช่ +1)", s1 == 3, s1)
        if shots and label == "390px": C.shot(page, "td4c-watch-stars-390.png", sel=".wlDT")
        page.locator(sel(3)).click(); settle(page, 500)
        s2 = wl_doc(page, "AAPL")["stars"]
        check(f"{tag} §2 แตะดวงที่ 3 ซ้ำ → 0", s2 == 0, s2)
        page.locator(sel(3)).click(); settle(page, 500); page.locator(sel(1)).click(); settle(page, 500)
        s3 = wl_doc(page, "AAPL")["stars"]
        check(f"{tag} §2 จาก 3 แตะดวงที่ 1 → 1", s3 == 1, s3)
        page.locator(sel(2)).click(); settle(page, 500)
        check(f"{tag} §2 จาก 1 แตะดวงที่ 2 → 2 · ดาว aria-pressed ตรงค่า", wl_doc(page, "AAPL")["stars"] == 2 and js(page, "()=>document.querySelector('.wlDT [data-wl-star=\"AAPL\"] [data-wl-star-n=\"2\"]').getAttribute('aria-pressed')") == "true")
        P44.reload_keep(page); T.P106.P37.set_clock(page, NOW); T.hook_confirm(page); go_watch(page, "wl")
        check(f"{tag} §2 รีโหลดแล้วค่าคงอยู่ (AAPL=2 · MSFT=1)", wl_doc(page, "AAPL")["stars"] == 2 and wl_doc(page, "MSFT")["stars"] == 1)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 Cand → WL ─────────────────────────
def cand_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        T.hw_inject(page); go_today(page)
        rows = T.qrows(page); first = rows[0]
        row = f'[data-td3-cand="{first}"] [data-td4-row]'
        check(f"{tag} §3 แถวพับเป็นปุ่มทั้งแถว (role=button · aria-expanded=false) · ปุ่ม Screen › ยังเห็น", js(page, "(s)=>{ const e=document.querySelector(s); return e.getAttribute('role')+'|'+e.getAttribute('aria-expanded'); }", row) == "button|false" and "Screen ›" in (txt(page, row) or ""), txt(page, row))
        page.locator(row + " b").click(); settle(page, 300)
        check(f"{tag} §3 แตะตัวอักษรชื่อหุ้น (ไม่ใช่ปุ่ม) → ฟอร์มเปิด · aria-expanded=true · ปุ่มเป็น 'Close ‹'", cnt(page, f'[data-td4-pro="{first}"]') == 1 and js(page, "(s)=>document.querySelector(s).getAttribute('aria-expanded')", row) == "true" and "Close ‹" in (txt(page, row) or ""), txt(page, row))
        page.locator("[data-td4-pro-note]").click(); page.fill("[data-td4-pro-note]", "keep me"); T.ev_pass(page); page.locator('[data-td4-star="2"]').click(); settle(page, 200)
        check(f"{tag} §3 คลิกข้างในฟอร์ม (โน้ต/ติ๊ก/ดาว) → ฟอร์มไม่ปิด", cnt(page, f'[data-td4-pro="{first}"]') == 1)
        row2 = f'[data-td3-cand="{rows[1]}"] [data-td4-row]'
        page.locator(row2).click(position={"x": 12, "y": 10}); settle(page, 300)
        check(f"{tag} §3 แตะแถวอื่น → เปิดทีละใบ (ใบแรกพับ)", cnt(page, "[data-td4-pro]") == 1 and cnt(page, f'[data-td4-pro="{rows[1]}"]') == 1)
        page.locator(row2).click(position={"x": 12, "y": 10}); settle(page, 300)
        check(f"{tag} §3 แตะแถวที่เปิดอยู่ซ้ำ → พับ", cnt(page, "[data-td4-pro]") == 0)
        js(page, "(s)=>document.querySelector(s).focus()", row); page.keyboard.press("Enter"); settle(page, 300)
        o1 = cnt(page, f'[data-td4-pro="{first}"]')
        js(page, "(s)=>document.querySelector(s).focus()", row); page.keyboard.press(" "); settle(page, 300)
        check(f"{tag} §3 คีย์บอร์ด Enter เปิด · Space พับ", o1 == 1 and cnt(page, "[data-td4-pro]") == 0, o1)
        page.locator(f'[data-td3-cand="{first}"] [data-td4-promote]').click(); settle(page, 300)
        check(f"{tag} §3 ปุ่ม Screen › เดิมยังเปิดได้ (ไม่ซ้อน 2 ครั้ง)", cnt(page, f'[data-td4-pro="{first}"]') == 1)
        hv = js(page, "()=>{ const e = document.querySelector('[data-td4-row]'); const c = getComputedStyle(e); return [c.cursor]; }")
        check(f"{tag} §3 cursor:pointer ทั้งแถว", hv[0] == "pointer", hv)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 4 Satellite cards ─────────────────────────
SPY = """()=>{ window.__act = []; ['td3SatCreate', 'td3SatOpen', 'td3WeekGo'].forEach(n=>{ if(window['__orig_' + n]) return; window['__orig_' + n] = window[n]; window[n] = (...a)=>{ window.__act.push(n + ':' + a.join(',')); }; }); }"""


def sat_cards_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = P106.launch(pw, w, h, iso=NOW, picks=("XAUUSD", "BTCUSD", "USDJPY"))
    try:
        go_today(page)
        P106.put_idea(page, "iX1", "XAUUSD", setup_ck=["in_zone"])                                                                        # pending
        P106.put_idea(page, "iX2", "XAUUSD", sleeve="tactical", classify="clear", setup_ck=["in_zone", "align_ma50", "mmt_shift_pivot"], bias="Long", entry=4180)   # incomplete (ขาด SL/TP)
        js(page, "()=>td3NtToggle('USDJPY')"); settle(page, 500)                                                                          # BTCUSD = noplan
        go_today(page)
        js(page, SPY)
        st = P106.sat_state(page)
        check(f"{tag} §4 มีหลายสถานะ: noplan · pending · incomplete · nt", {x["st"] for x in st} >= {"noplan", "pending", "incomplete", "nt"}, [x["st"] for x in st])
        done = 0
        for x in st:
            k, sl, state = x["k"], x["sleeve"], x["st"]
            sel = f'[data-td3-sat="{k}"][data-sleeve="{sl}"]'
            if state == "nt":
                check(f"{tag} §4 Not trading this week ({k}) ไม่เป็นปุ่ม/ไม่กดทั้งการ์ด", js(page, "(s)=>{ const e=document.querySelector(s); return e.getAttribute('role') || ''; }", sel) == "" and cnt(page, sel + " [data-td3-sat-link]") == 0)
                js(page, "()=>{ window.__act = []; }"); page.locator(sel + " .l1 .nm").click(); settle(page, 250)
                check(f"{tag} §4 กดการ์ด Not trading ไม่เกิดการนำทาง", js(page, "()=>window.__act.slice()") == [] and js(page, "()=>activeTab") == "today")
                continue
            js(page, "()=>{ window.__act = []; }")
            page.locator(sel + " [data-td3-sat-link]").click(); settle(page, 250)
            a_link = js(page, "()=>window.__act.slice()")
            js(page, "()=>{ window.__act = []; }")
            page.locator(sel + " .l1 .nm").click(); settle(page, 250)
            a_card = js(page, "()=>window.__act.slice()")
            ok = len(a_link) == 1 and a_card == a_link
            check(f"{tag} §4 {k}/{state}: แตะตัวการ์ด = ลิงก์ของการ์ด {a_link} · ปุ่มลิงก์ยังอยู่ ({(txt(page, sel + ' [data-td3-sat-link]') or '')})", ok, [a_link, a_card])
            js(page, "()=>{ window.__act = []; }")
            page.locator(sel + " [data-td3-sat-link]").evaluate("e=>e.click()"); settle(page, 150)
            check(f"{tag} §4 {k}: กดปุ่มลิงก์ทำงานครั้งเดียว (ไม่ซ้ำจากการ์ด)", len(js(page, "()=>window.__act.slice()")) == 1)
            if state in ("pending", "incomplete") and cnt(page, sel + " [data-td3-more]"):
                js(page, "()=>{ window.__act = []; }"); page.locator(sel + " [data-td3-more]").click(); settle(page, 250)
                check(f"{tag} §4 {k}: ปุ่ม +n ในการ์ดกางรายการ ไม่ไปหน้าอื่น", js(page, "()=>window.__act.slice()") == [])
                go_today(page); js(page, SPY)
            done += 1
            js(page, "()=>{ window.__act = []; }")
        kb = js(page, "()=>{ const e = document.querySelector('[data-td3-sat-card]'); return e ? [e.getAttribute('role'), e.getAttribute('tabindex')] : null; }")
        check(f"{tag} §4 การ์ดมี role=button tabindex=0 (คีย์บอร์ด)", kb == ["button", "0"], kb)
        js(page, "()=>{ window.__act = []; document.querySelector('[data-td3-sat-card]').focus(); }"); page.keyboard.press("Enter"); settle(page, 200)
        check(f"{tag} §4 Enter บนการ์ด = ลิงก์ของการ์ด", len(js(page, "()=>window.__act.slice()")) == 1)
        check(f"{tag} §4 ทุกสถานะที่มีลิงก์ผ่านครบ ({done} การ์ด)", done >= 3, done)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 Deep dive ─────────────────────────
THESIS_FULL = {"date": "2026-09-20", "asOf": "2026-09-18", "summary": {}, "sections": {"s1": {"md": "biz"}, "s2": {"md": "why"}, "s3": {"md": "monitor"}, "s4": {"md": "exit"}},
               "kpi": [{"name": "k", "base": "b", "review_if": "r", "do": "d"}], "tripwires": [{"thesis": 1, "area": "a", "signal": "s", "now": "n", "level": "ok"}], "catalysts": [], "gaps": []}
THESIS_PART = {"date": "2026-09-20", "summary": {}, "sections": {"s1": {"md": "biz"}, "s2": {"md": "why"}}, "kpi": [], "tripwires": [], "catalysts": [], "gaps": []}


def deep_fixture(page):
    wl_seed(page, [W("AVGO", tier="A", tier_set_at="2026-09-01", tier_lens="fortress", thesis=THESIS_FULL),
                   W("PART", tier="A", tier_set_at="2026-09-01", tier_lens="fortress", thesis=THESIS_PART),
                   W("MSFT"), W("NVDA"), W("PTT.BK", "TH"), W("CPALL.BK", "TH")])


def deep_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        deep_fixture(page); go_today(page)
        comp = js(page, "()=>({avgo: tdHwComplete('AVGO', []), part: tdHwComplete('PART', []), parts: tdHwThesisParts('AVGO'), partP: tdHwThesisParts('PART'), msft: tdHwThesisParts('MSFT')})")
        check(f"{tag} §5 ครบ 5 ส่วนจาก Thesis นำเข้า + Tier: AVGO ครบ · PART ไม่ครบ (Monitor/Exit ว่าง) · MSFT ไม่มีอะไร", comp["avgo"] is True and comp["part"] is False and sorted(comp["partP"]) == ["biz", "tier", "why"] and comp["msft"] == [], comp)
        pk = js(page, "()=>[tdLast.hwm.US.t, tdLast.hwm.TH.t]")
        check(f"{tag} §5 AVGO ไม่ถูกเสนอเป็นตัวของวัน (ตัว US ≠ AVGO)", pk[0] != "AVGO" and "AVGO" not in (txt(page, "[data-td3-hw]") or ""), pk)
        cands = js(page, "()=>tdHomeworkCandidates().filter(x=>x.mk==='US').map(x=>[x.t, !!x.cmp])")
        check(f"{tag} §5 ตัวเลือกการบ้านติดธง cmp ให้ AVGO เท่านั้น", [c for c in cands if c[1]] == [["AVGO", True]], cands)
        # AVGO เป็นตัวที่เลือกไว้เดิม → ครบ = ถือว่าทำแล้ว · Next จาก Watchlist ไม่เสนอ AVGO
        js(page, "()=>tdLogWrite(d=>{ td4HwSet(d, 'US', 'AVGO', []); d.hw = {pick:'AVGO', done:false, parts:[]}; })"); settle(page, 500)
        r = txt(page, "[data-td3-hw]") or ""
        check(f"{tag} §5 pick เดิมเป็น AVGO (ครบแล้ว) → แถวเป็น ✓ 'Thesis 5/5' · วัน US นับว่าทำแล้ว · ไม่มี Missing", "AVGO" in r and "5/5" in r and "Missing" not in r and T.dd_head(page).startswith("US 1/1"), [r, T.dd_head(page)])
        check(f"{tag} §5 มีปุ่ม 'Next from Watchlist ›'", cnt(page, "[data-td4-hwnext-wl]") == 1)
        nx = js(page, "()=>{ const p = td4HwNextWlPick('US'); return p && p.t; }")
        check(f"{tag} §5 ตัวที่เสนอต่อไม่ใช่ AVGO / ไม่ใช่ตัวครบ", nx not in (None, "AVGO"), nx)
        page.locator("[data-td4-hwnext-wl]").click(); settle(page, 500)
        r2 = txt(page, "[data-td3-hw]") or ""
        check(f"{tag} §5 กด Next → ตัวถัดไป (ไม่ใช่ AVGO) พร้อม Missing: …", "AVGO" not in r2 and "Missing:" in r2, r2)
        # PART: ขาด Monitor · Exit
        js(page, "()=>tdLogWrite(d=>{ td4HwSet(d, 'US', 'PART', []); d.hw = {pick:'PART', done:false, parts:[]}; })"); settle(page, 500)
        r3 = txt(page, "[data-td3-hw]") or ""
        check(f"{tag} §5 หุ้นไม่ครบแสดงชื่อส่วนที่ว่างตรง ๆ: 'Missing: Monitor · Exit' + 'Thesis 3/5'", "Missing: Monitor · Exit" in r3 and "Thesis 3/5" in r3 and "Left:" not in r3 and "0/5" not in r3, r3)
        if shots and label == "390px": scroll_to_sel(page, '[data-td3-sec="hw"]'); C.shot(page, "td4c-deepdive-390.png", sel='[data-td3-sec="hw"]')
        # MSFT ไม่มีอะไร → Missing ครบ 5
        js(page, "()=>tdLogWrite(d=>{ td4HwSet(d, 'US', 'MSFT', []); d.hw = {pick:'MSFT', done:false, parts:[]}; })"); settle(page, 500)
        r4 = txt(page, "[data-td3-hw]") or ""
        check(f"{tag} §5 ว่างทั้งหมด → 'Missing: Tier · Business · Why · Monitor · Exit'", "Missing: Tier · Business · Why · Monitor · Exit" in r4, r4)
        # Change: ไม่วน AVGO
        seen = set()
        for _ in range(4):
            js(page, "()=>tdHwNext()"); settle(page, 250); seen.add(js(page, "()=>tdLast.hwm.US.t"))
        check(f"{tag} §5 Change วนเฉพาะตัวที่ยังไม่ครบ (ไม่มี AVGO)", "AVGO" not in seen and len(seen) >= 2, sorted(seen))
        # reminder
        js(page, "()=>tdLogWrite(d=>{ td4HwSet(d, 'US', 'AVGO', []); d.hw = {pick:'AVGO', done:false, parts:[]}; })"); settle(page, 400)
        T.clock(page, T.EVE); go_today(page)
        rem = [x["id"] for x in (js(page, "()=>td4RemList(tdLast)") or [])]
        check(f"{tag} §5 reminder 20:00 ไม่ค้าง 'Deep dive US' เมื่อ pick ครบแล้ว (ใช้กติกาเดียวกัน)", "hwUS" not in rem, rem)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5b ไม่เด้งขึ้นบน ─────────────────────────
def scroll_tests(pw):
    w, h, label = 390, 844, "390px"
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        deep_fixture(page); T.hw_inject(page); go_today(page)
        def probe(name, sel_scroll, action):
            scroll_to_sel(page, sel_scroll); y0 = scroll_y(page)
            action(); settle(page, 500)
            y1 = scroll_y(page)
            mx = js(page, "()=>Math.round(document.documentElement.scrollHeight - innerHeight)")   # หน้าสั้นลงจนชนก้นหน้า = ยอมให้ถูกบีบตามความยาวหน้า
            check(f"{tag} §5 {name}: scrollY ไม่ขยับ (±2px) {y0}→{y1}", y0 > 100 and abs(y1 - min(y0, mx)) <= 2, [y0, y1, mx])
        probe("Change", '[data-td3-hwnext]', lambda: page.locator("[data-td3-hwnext]").click())
        probe("สลับ TH", '[data-td4-hwmk="TH"]', lambda: page.locator('[data-td4-hwmk="TH"]').click())
        probe("สลับ US", '[data-td4-hwmk="US"]', lambda: page.locator('[data-td4-hwmk="US"]').click())
        probe("Cand→WL สลับตลาด", '[data-td4-scrmk]', lambda: page.locator('[data-td4-scrmk="TH"]').click())
        probe("Screen ›", '[data-td3-cand] [data-td4-promote]', lambda: page.locator('[data-td3-cand] [data-td4-promote]').first.click())
        # Next batch: ทำ 3 ตัวให้ครบขั้นต่ำก่อน
        js(page, "()=>{ td4SetScrMk('US'); }"); settle(page, 300)
        for s in js(page, "()=>td4Queue('US', thaiToday()).slice(0, 3).map(c=>c.sym)"): js(page, "(s)=>td3NotPassed(s)", s); settle(page, 300)
        if cnt(page, "[data-td4-nextbatch]"):
            probe("Next batch ›", '[data-td4-nextbatch]', lambda: page.locator("[data-td4-nextbatch]").click())
        else:
            check(f"{tag} §5 Next batch › ปรากฏหลังครบขั้นต่ำ", False, T.trk(page))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 Macro re-check ─────────────────────────
def set_pb_age(page, days):
    js(page, """(d)=>{ const ms = Date.now() - d*86400000; pbList.forEach(v=>{ v.savedAt = new Date(ms).toISOString(); }); try{ const s = tdSettings(); delete s.pbCheckedAt; }catch(e){} todayRefresh(true); }""", days); settle(page, 400)


def macro_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        go_today(page)
        set_pb_age(page, 29)
        a = txt(page, "[data-td3-macroago]") or ""
        cls = js(page, "()=>document.querySelector('[data-td3-macroago]').className")
        check(f"{tag} §B5b 29 วัน → '29d ago' muted (ไม่มี Re-check)", a == "29d ago" and "due" not in cls and cnt(page, "[data-td4-recheck]") == 0, [a, cls])
        set_pb_age(page, 34)
        a = txt(page, "[data-td3-macroago]") or ""
        col = js(page, "()=>getComputedStyle(document.querySelector('[data-td3-macroago]')).color")
        amb = js(page, "()=>{ const t = document.createElement('i'); t.style.color='var(--amber)'; document.body.appendChild(t); const c = getComputedStyle(t).color; t.remove(); return c; }")
        check(f"{tag} §B5b 34 วัน → amber '34d ago · Re-check ›' ในแถว Macro เดิม (ไม่มีแถวเพิ่ม)", a == "34d ago · Re-check ›" and col == amb and cnt(page, "[data-td3-macro]") == 1, [a, col, amb])
        page.locator("[data-td3-macro]").click(); settle(page, 600)
        st = js(page, "()=>({tab:activeTab, open:pbOpen, top:Math.round(document.getElementById('pbPanel').getBoundingClientRect().top), bar:!!document.querySelector('[data-pb-recheck]'), ok:!!document.querySelector('[data-pb-recheck-ok]')})")
        check(f"{tag} §B5b แตะ → Flow › Quarterly Macro เปิดและเลื่อนมาที่หัวแผง · มีปุ่มยืนยัน/วาง JSON", st["tab"] == "flow" and st["open"] is True and -5 <= st["top"] <= 200 and st["bar"] and st["ok"], st)
        js(page, "()=>pbConfirmOk()"); settle(page, 500); go_today(page)
        a2 = txt(page, "[data-td3-macroago]") or ""
        check(f"{tag} §B5b ยืนยันแล้ว → กลับเป็น muted (ไม่มี Re-check)", "Re-check" not in a2 and cnt(page, "[data-td4-recheck]") == 0, a2)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 7 Risk chip ─────────────────────────
def set_dd(page, sat_dd=None, core_dd=None):
    """ตั้ง ddState ของบัญชีแรก: dd = % ที่ต้องการ (peak = ทุน/(1-dd))"""
    js(page, """([sd, cd])=>{ const A = acctList[0].id, B = getBook(A), s = B.settings; s.fx = 40; s.capital = Object.assign({}, s.capital || {}, {core:700000, satB:26000});
      const mk = (tank, dd)=>({peak: dd ? tank/(1-dd/100) : tank, baseAt:'2026-09-01', tank, stage:'normal', stageSince:'2026-09-01', pauseUntil:null, review:null, recoverDd0:null, weekly:{}, rebasedAt:null});
      s.ddState = {core: mk(700000, cd), sat: mk(26000, sd)}; B.trades = []; saveBook(A); render(); todayRefresh(true); }""", [sat_dd, core_dd]); settle(page, 500)


def risk_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        set_dd(page); go_today(page)
        chip = txt(page, '[data-td4-risk="sat"]') or ""
        check(f"{tag} §B5b ปกติ → 'Risk ✓' ที่หัว Satellite · ไม่มีชิปที่ Core Port", chip == "Risk ✓" and cnt(page, '[data-td4-risk="core"]') == 0, chip)
        same = js(page, "()=>{ const h = document.querySelector('[data-td4-ph=\"sat\"] h3').getBoundingClientRect(), c = document.querySelector('[data-td4-risk=\"sat\"]').getBoundingClientRect(); return [Math.round(h.top), Math.round(c.top), Math.round(c.right), Math.round(document.querySelector('[data-td3-panel=\"sat\"]').getBoundingClientRect().right)]; }")
        check(f"{tag} §B5b ชิป Risk อยู่แถวเดียวกับหัว SATELLITE ชิดขวา", abs(same[0] - same[1]) <= 14 and same[3] - same[2] <= 22, same)
        page.locator('[data-td4-risk="sat"]').click(); settle(page, 400)
        sheet = js(page, "()=>{ const e = document.querySelector('[data-td4-rsheet]'); if(!e) return null; const t = e.querySelector('[data-td-nums]'); const r = e.querySelector('.bx').getBoundingClientRect(); return {rows:t ? t.rows.length : 0, vis:getComputedStyle(e.querySelector('[data-td-det]')).display, inView: r.bottom <= innerHeight + 1 && r.left >= -1 && r.right <= innerWidth + 1}; }")
        check(f"{tag} §B5b แตะ 'Risk ✓' → เปิดตารางตัวเลข (ชีต/ป๊อปโอเวอร์) ในหน้าจอ", sheet and sheet["rows"] >= 2 and sheet["vis"] != "none" and sheet["inView"], sheet)
        eq = js(page, """()=>{ const norm = e => e.outerHTML.replace(/ style="[^"]*"/g, ''); const t = document.createElement('template'); t.innerHTML = tdNumsHtml(tdLast); return norm(document.querySelector('#td4RiskSheet [data-td-det]')) === norm(t.content.firstElementChild); }""")
        check(f"{tag} §B5b ตารางในชีต = ผลของ tdNumsHtml เดิมทุกตัวอักษร (ตัวเลขเดียวกัน)", eq is True, eq)
        if shots and label == "390px": C.shot(page, "td4c-risk-table-390.png")
        page.keyboard.press("Escape"); settle(page, 200)
        check(f"{tag} §B5b Esc ปิดชีต", cnt(page, "#td4RiskSheet") == 0)
        # DD Sat
        set_dd(page, sat_dd=12.5); go_today(page)
        chip = txt(page, '[data-td4-risk="sat"]') or ""
        st = js(page, "()=>document.querySelector('[data-td4-risk=\"sat\"]').dataset.riskState")
        same = js(page, "()=>{ const h = document.querySelector('[data-td4-ph=\"sat\"] h3').getBoundingClientRect(), c = document.querySelector('[data-td4-risk=\"sat\"]').getBoundingClientRect(); return [Math.round(h.top), Math.round(c.top)]; }")
        check(f"{tag} §B5b DD Sat 12.5% (Reduce) → '⚠ DD Sat … 12.5% · Reduce ›' ที่หัว Satellite · amber", chip.startswith("⚠ DD Sat") and "12.5%" in chip and "Reduce" in chip and chip.endswith("›") and st == "amber", [chip, st])
        check(f"{tag} §B5b ชิป DD Sat อยู่แถวเดียวกับหัวแผง", abs(same[0] - same[1]) <= 14, same)
        wid = js(page, "()=>{ const c = document.querySelector('[data-td4-risk=\"sat\"]'), p = c.parentNode; return [c.scrollWidth <= c.clientWidth + 1 || getComputedStyle(c.querySelector('.t')).textOverflow === 'ellipsis', c.getBoundingClientRect().right <= document.querySelector('[data-td3-panel=\"sat\"]').getBoundingClientRect().right + 1, !!c.querySelector('.g')]; }")
        check(f"{tag} §B5b ชิปไม่ล้นแถว · › ยังเห็น", all(wid), wid)
        if shots and label == "390px": scroll_to_sel(page, '[data-td4-ph="sat"]'); C.shot(page, "td4c-risk-390.png", sel='[data-td4-ph="sat"]')
        page.locator('[data-td4-risk="sat"]').click(); settle(page, 300)
        has = js(page, "()=>[...document.querySelectorAll('#td4RiskSheet [data-td-nums] td[data-stage]')].map(e=>e.innerText.trim()+':'+e.dataset.stage)")
        check(f"{tag} §B5b ชีตแสดง DD Sat 12.5% stage reduce (สีตามขั้นเดิม)", any(x.startswith("12.5%") and x.endswith("reduce") for x in has), has)
        page.locator("[data-td4-rsheet-x]").click(); settle(page, 200)
        check(f"{tag} §B5b Core ยังไม่มีชิป (DD Core ปกติ)", cnt(page, '[data-td4-risk="core"]') == 0)
        set_dd(page, core_dd=12.5); go_today(page)
        cc = txt(page, '[data-td4-risk="core"]') or ""
        same = js(page, "()=>{ const h = document.querySelector('[data-td4-ph=\"core\"] h3').getBoundingClientRect(), c = document.querySelector('[data-td4-risk=\"core\"]').getBoundingClientRect(); return [Math.round(h.top), Math.round(c.top)]; }")
        check(f"{tag} §B5b DD Core ถึงขั้น → ชิป '⚠ DD Core … ›' ที่หัว Core Port เท่านั้น (Sat กลับเป็น Risk ✓)", cc.startswith("⚠ DD Core") and "12.5%" in cc and abs(same[0] - same[1]) <= 14 and (txt(page, '[data-td4-risk="sat"]') or "") == "Risk ✓", [cc, txt(page, '[data-td4-risk="sat"]')])
        if shots and label == "1440px": C.shot(page, "td4c-today-1440.png", full=True)
        if shots and label == "390px": C.shot(page, "td4c-today-390.png", full=True)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", ovf(page) <= 0 and not ce and not pe, [ovf(page), ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 8 กว้าง/แคบ รวม ─────────────────────────
def width_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        deep_fixture(page); T.hw_inject(page); P105.seed_rrg(page, d=sector_rows(), wk=P105.rows_w()); follow(page, "XLU", "XLK"); set_dd(page, sat_dd=12.5, core_dd=12.5)
        set_pb_age(page, 34); go_today(page)
        check(f"{tag} Today (ทุกบล็อกใหม่) ไม่ล้นแนวนอน", ovf(page) <= 0, ovf(page))
        el = js(page, "()=>[...document.querySelectorAll('[data-td4-ph],[data-sd-trow],[data-td3-macro]')].filter(e=>{ const r = e.getBoundingClientRect(); return r.right > innerWidth + 1 || r.left < -1; }).length")
        check(f"{tag} หัวแผง/แถว Sector/Macro อยู่ในจอ", el == 0, el)
        page.locator('[data-td4-risk="sat"]').click(); settle(page, 300)
        br = js(page, "()=>{ const r = document.querySelector('#td4RiskSheet .bx').getBoundingClientRect(); return r.left >= -1 && r.right <= innerWidth + 1 && r.top >= -1 && r.bottom <= innerHeight + 1; }")
        check(f"{tag} ชีตความเสี่ยงอยู่ในจอ", br is True, br)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def run_sectors(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: sectors_tests(pw, w, h, l, shots=True)
def run_stars(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: stars_tests(pw, w, h, l, shots=True)
def run_cand(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: cand_tests(pw, w, h, l)
def run_sat(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: sat_cards_tests(pw, w, h, l)
def run_deep(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: deep_tests(pw, w, h, l, shots=True)
def run_macro(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: macro_tests(pw, w, h, l)
def run_risk(pw):
    for w, h, l in [(390, 844, "390px"), (1440, 900, "1440px")]: risk_tests(pw, w, h, l, shots=True)
def run_width(pw):
    for w, h, l in [(300, 800, "300px"), (390, 844, "390px"), (1280, 800, "1280px"), (1440, 900, "1440px")]: width_tests(pw, w, h, l)


SECTIONS = {"sectors": run_sectors, "stars": run_stars, "cand": run_cand, "sat": run_sat, "deep": run_deep, "scroll": scroll_tests, "macro": run_macro, "risk": run_risk, "width": run_width}


def main():
    want = os.environ.get("SECT", " ".join(SECTIONS)).split()
    with sync_playwright() as pw:
        for k in want: SECTIONS[k](pw)
    print("LOG " + json.dumps(LOG, ensure_ascii=False))
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
