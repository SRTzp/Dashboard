#!/usr/bin/env python3
"""UX2 — Filter รวมปุ่มเดียว (Watchlist/Candidates) + Card แผน Core อ่านง่าย (ตัดตัวเลขซ้ำ) + f → FF ทั้ง UI · เทส 64
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-09
ภาพ tests/screenshots/ux2-{filter-closed,filter-open,wl-filter,core-plan-us,core-plan-th,core-plan-howto}-{1440,390}.png
รัน: python3 run_tests_phase64.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase37 as P37
import run_tests_phase59 as VW
import run_tests_phase61 as P61

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-UX2.html"))
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
txt, cnt, wait = VW.txt, VW.cnt, VW.wait
TODAY = VW.TODAY


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


def syms(page): return js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>e.dataset.sym)")
def go(page, view): P61.go(page, view)
def flt_open(page):
    if page.locator("[data-flt-panel]").count() == 0:
        page.locator("[data-flt-btn]").click(); wait(page, 300)
def flt_close(page):
    if page.locator("[data-flt-panel]").count() == 1:
        page.locator("[data-flt-btn]").click(); wait(page, 300)
def n_of(page): return js(page, "()=>{ const i=document.querySelector('[data-flt-btn] i'); return i ? +i.textContent : 0; }")
def err_free(ce, pe): return not VW.real_errs(ce) and not pe


NOTES = {"AVGO": {"phase": {"v": "start", "at": TODAY}}, "NVDA": {"phase": {"v": "up", "at": TODAY}}, "MSFT": {"phase": {"v": "side", "at": TODAY}},
         "CAMT": {"phase": {"v": "up", "at": TODAY}, "tier": {"tier": "A", "tier_lens": "fortress", "tier_set_at": TODAY}}, "ONTO": {"phase": {"v": "weak", "at": TODAY}}}


def filter_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, c, page, ce, pe, dl = P61.launch(pw, w, h, notes=NOTES)
    try:
        # ── 1 Candidates พับอยู่
        go(page, "cand")
        check(f"{tag} 1 Candidates: ไม่มีแถว data-cand-filters/data-tq-filters/data-ph-filters (3 แถวเดิม) · มีปุ่ม Filter 1 ปุ่ม · ไม่เลือกอะไร = ไม่มีตัวเลข",
              cnt(page, "[data-cand-filters]") == 0 and cnt(page, "[data-tq-filters]") == 0 and cnt(page, "[data-ph-filters]") == 0 and cnt(page, "[data-flt-btn]") == 1 and n_of(page) == 0
              and txt(page, "[data-flt-btn]") == "Filter ▾", txt(page, "[data-flt-btn]"))
        shot(page, f"ux2-filter-closed-{sfx}.png", ".wlList")
        # ── 2 กาง
        flt_open(page)
        gl = js(page, "()=>[...document.querySelectorAll('[data-flt-panel] .fltGl')].map(e=>e.firstChild.textContent.trim())")
        check(f"{tag} 2 กางแผง → กลุ่ม Idea · Tier · Phase · เรียง · ปุ่มเป็น ▴", gl == ["Idea", "Tier", "Phase", "เรียง"] and txt(page, "[data-flt-btn]").endswith("▴"), json.dumps(gl, ensure_ascii=False))
        check(f"{tag} 2 ชิปในแผง: Idea [▲ ได้ ▼ เสีย] · Tier [ผ่าน ไม่ผ่าน ยังไม่ Check] · เรียง [ตาม Idea | Phase] (ตัดชิป 'ทั้งหมด')",
              js(page, "()=>[...document.querySelectorAll('[data-flt-panel] [data-cand-f]')].map(e=>e.textContent.trim())") == ["▲ ได้", "▼ เสีย"]
              and js(page, "()=>[...document.querySelectorAll('[data-flt-panel] [data-tq-f]')].map(e=>e.textContent.trim())") == ["ผ่าน", "ไม่ผ่าน", "ยังไม่ Check"]
              and js(page, "()=>[...document.querySelectorAll('[data-flt-panel] [data-ph-sort]')].map(e=>e.textContent.trim())") == ["ตาม Idea", "Phase"])
        shot(page, f"ux2-filter-open-{sfx}.png", ".wlList")
        page.locator('[data-cand-f="win"]').click(); wait(page, 300)
        flt_open(page)
        page.locator('[data-ph-f="up"]').click(); wait(page, 300)
        flt_open(page)
        got = syms(page)
        check(f"{tag} 2 เลือก ▲ ได้ + Up → ปุ่ม 'Filter 2'", n_of(page) == 2 and txt(page, "[data-flt-btn]").startswith("Filter 2"), txt(page, "[data-flt-btn]"))
        flt_close(page)
        check(f"{tag} 2 พับแล้วบรรทัดสรุป 'Idea ▲ · Up'", txt(page, "[data-flt-sum]") == "Idea ▲ · Up", txt(page, "[data-flt-sum]"))
        # เทียบกับการตั้งค่าตัวแปรเดิมตรง ๆ
        js(page, "()=>{ candFilter='all'; phFilter.clear(); renderWatchlist(); }"); wait(page, 200)
        all_rows = syms(page)
        js(page, "()=>{ candFilter='win'; phFilter.clear(); phFilter.add('up'); renderWatchlist(); }"); wait(page, 250)
        direct = syms(page)
        check(f"{tag} 2 รายการที่กรองด้วยแผง = ตั้งตัวแปรเดิม (candFilter='win' · phFilter={{up}}) ตรง ๆ", got == direct and len(direct) <= len(all_rows), json.dumps([got, direct, all_rows]))
        # ── 3 แตะซ้ำ + ล้างทั้งหมด
        flt_open(page)
        page.locator('[data-cand-f="win"]').click(); wait(page, 250)
        check(f"{tag} 3 แตะ ▲ ได้ ซ้ำ → กลับทั้งหมด (candFilter='all')", js(page, "()=>candFilter") == "all")
        flt_open(page)
        page.locator('[data-tq-f="pass"]').click(); wait(page, 250); flt_open(page)
        page.locator('[data-ph-sort="on"]').click(); wait(page, 250); flt_open(page)
        check(f"{tag} 3 Tier ผ่าน + Phase Up (n=2) · เรียง Phase ไม่นับ", n_of(page) == 2 and js(page, "()=>phSort") is True)
        check(f"{tag} 3 ปุ่มกางอยู่ → ลิงก์ 'ล้างทั้งหมด' (n>0)", cnt(page, "[data-flt-clear]") == 1)
        page.locator("[data-flt-clear]").click(); wait(page, 300)
        ls = js(page, "()=>({ph:localStorage.getItem('dash.phFilter'), tq:localStorage.getItem('dash.tqFilter')})")
        check(f"{tag} 3 ล้างทั้งหมด → n=0 · ตัวแปร/localStorage ล้าง (phFilter · tqFilter)", n_of(page) == 0 and ls == {"ph": "[]", "tq": "[]"} and js(page, "()=>[candFilter, phFilter.size, tqFilter.size]") == ["all", 0, 0], json.dumps(ls))
        # ── 5 คีย์ลัด
        flt_close(page)
        page.keyboard.press("BracketRight"); wait(page, 300)
        check(f"{tag} 5 คีย์ลัด ] → สลับ Idea filter เดิม (all → win)", js(page, "()=>candFilter") == "win")
        page.keyboard.press("BracketLeft"); wait(page, 300)
        check(f"{tag} 5 คีย์ลัด [ → กลับ all", js(page, "()=>candFilter") == "all")
        # ── 4 Watchlist
        go(page, "wl")
        check(f"{tag} 4 Watchlist: ปุ่ม Filter 1 ปุ่ม · ไม่มีแถวชิป Phase เดิม", cnt(page, "[data-flt-btn]") == 1 and cnt(page, "[data-ph-filters]") == 0)
        flt_open(page)
        gl = js(page, "()=>[...document.querySelectorAll('[data-flt-panel] .fltGl')].map(e=>e.firstChild.textContent.trim())")
        check(f"{tag} 4 แผงมีแค่ Phase + เรียง · เรียง = ปกติ | Phase", gl == ["Phase", "เรียง"] and js(page, "()=>[...document.querySelectorAll('[data-flt-panel] [data-ph-sort]')].map(e=>e.textContent.trim())") == ["ปกติ", "Phase"], json.dumps(gl, ensure_ascii=False))
        pills = js(page, "()=>{ const p=[...document.querySelectorAll('.wlPills')].map(e=>e.innerText.replace(/\\s+/g,' ')); return {pills:p, inFlt:!!document.querySelector('[data-flt] .wlPills')}; }")
        check(f"{tag} 4 ปุ่ม Port (All · Core.US · Core.TH) ยังอยู่เดิมนอกแผง", any("Core.US" in x and "Core.TH" in x for x in pills["pills"]) and not pills["inFlt"], json.dumps(pills, ensure_ascii=False))
        page.locator('[data-ph-f="up"]').click(); wait(page, 250); flt_open(page)
        page.locator('[data-ph-sort="on"]').click(); wait(page, 250)
        ph_up = js(page, "()=>[...document.querySelectorAll('.wlR')].every(e=>(e.querySelector('[data-ph-chip]')||{dataset:{}}).dataset.ph==='up')")
        check(f"{tag} 4 Watchlist: Up + เรียง Phase → ปุ่ม 'Filter 1' · แถวเป็น Up เท่านั้น", n_of(page) == 1 and ph_up and len(syms(page)) >= 1, txt(page, "[data-flt-btn]") + "|" + json.dumps(syms(page)))
        flt_close(page)
        check(f"{tag} 4 สรุป 'Up · เรียง Phase'", txt(page, "[data-flt-sum]") == "Up · เรียง Phase", txt(page, "[data-flt-sum]"))
        shot(page, f"ux2-wl-filter-{sfx}.png", ".wlList")
        if w < 600:
            m = js(page, "()=>{ const b=document.querySelector('.fltBar'); const r=b.getBoundingClientRect(); const ks=[...b.children].map(e=>e.getBoundingClientRect()); return {h:Math.round(r.height), one: Math.max(...ks.map(q=>q.top+q.height/2))-Math.min(...ks.map(q=>q.top+q.height/2)) < 6, over: b.scrollWidth>b.clientWidth+1, W: innerWidth, sw: document.documentElement.scrollWidth}; }")
            check(f"{tag} 12 390px: แถว Filter บรรทัดเดียว ไม่ล้น · หน้าไม่ล้นแนวนอน", m["one"] and not m["over"] and m["sw"] <= m["W"] + 1, json.dumps(m))
            flt_open(page)
            m2 = js(page, "()=>({sw:document.documentElement.scrollWidth, W:innerWidth, chip:Math.min(...[...document.querySelectorAll('[data-flt-panel] .chip')].map(e=>e.getBoundingClientRect().height)), pw:document.querySelector('[data-flt-panel]').scrollWidth<=document.querySelector('[data-flt-panel]').clientWidth+1})")
            check(f"{tag} 12 แผงกางไม่ล้นแนวนอน · ชิปสูง ≥ 32px", m2["sw"] <= m2["W"] + 1 and m2["pw"] and m2["chip"] >= 31.5, json.dumps(m2))
            check(f"{tag} 12 บนจอแคบไม่แสดง hint [ ]", js(page, "()=>{ const e=document.querySelector('.kbdhint'); return !e || getComputedStyle(e).display==='none'; }"))
        else:
            check(f"{tag} 12 ไม่มีขอบล้นแนวนอน (1440)", js(page, "()=>document.documentElement.scrollWidth <= innerWidth + 1"))
        check(f"{tag} 12 ไม่มี console error", err_free(ce, pe))
    finally:
        b.close()
    # snErr (ไม่มีสิทธิ์อ่าน stockNotes): Watchlist ไม่มี Filter · Candidates มีแต่ Idea
    b, c, page, ce, pe, dl = P61.launch(pw, w, h, deny=True)
    try:
        go(page, "wl")
        check(f"{tag} 4 ไม่มีสิทธิ์อ่าน stockNotes → Watchlist ไม่มี Filter (ไม่มี Phase ให้กรอง) · แถวยังครบ", cnt(page, "[data-flt]") == 0 and len(syms(page)) == 3)
        go(page, "cand"); flt_open(page)
        gl = js(page, "()=>[...document.querySelectorAll('[data-flt-panel] .fltGl')].map(e=>e.firstChild.textContent.trim())")
        check(f"{tag} 4 Candidates (ไม่มีสิทธิ์) → แผงมีเฉพาะ Idea", gl == ["Idea"], json.dumps(gl))
    finally:
        b.close()


def plan_card(pw, w, h, label, cards, notes=None, setup=None):
    b, c, page, ce, pe, dl = P61.launch(pw, w, h, cands=(), notes=notes or {}, cards=cards)
    js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); wait(page, 700)
    if setup: setup(page)
    for cid in cards:
        sel = f'[data-core-card="{cid}"] [data-c-row]'
        if page.locator(sel).count() and js(page, "(s)=>document.querySelector(s).getAttribute('aria-expanded')", sel) != "true": page.locator(sel).click(); wait(page, 250)
    return b, page, ce, pe


def core_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    S = lambda cid: f'[data-core-card="{cid}"]'
    # ── 6 US · Entry 100 Stop 90
    cards = {"cplan": p24.card("cplan", "main", "AVGO", plan={"entry": 100, "stop": 90}, tier="A")}
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "up", "at": TODAY}}})
    try:
        calc = js(page, "()=>{ const cx=coreCtx('main'); const r=coreFirstLotCalc(cx,'US','A',100,90,cx.F.f); return r ? {qty:r.qty, ok:r.ok, cost:r.cost, risk:r.risk} : null; }")
        sc = S("cplan")
        row = txt(page, sc + " [data-c-row]")
        check(f"{tag} 6 Card แผน (กางอยู่): แถวหัวไม่มี Entry/Stop/ไม้แรก", "Entry" not in row and "Stop" not in row and "ไม้แรก" not in row, row)
        check(f"{tag} 6 ไม่มีกล่อง ccGrid4 · ไม่มี 'f ตอนนี้' · ไม่มีป้าย 'f x%'", cnt(page, sc + " .ccGrid4") == 0 and "f ตอนนี้" not in txt(page, sc) and not re.search(r"(^|\s)f \d+%", txt(page, sc)), txt(page, sc)[:300])
        qty = txt(page, sc + " [data-c-qty]")
        check(f"{tag} 6 ตัวใหญ่ = จำนวนหุ้นเท่าเดิม (เทียบ coreFirstLotCalc)", calc and calc["ok"] and qty == f"{calc['qty']:,}" and js(page, "(s)=>parseFloat(getComputedStyle(document.querySelector(s+' .ccBig b')).fontSize)", sc) >= 24, f"{qty} vs {calc}")
        cost = txt(page, sc + " [data-c-cost]")
        check(f"{tag} 6 บรรทัดทุน/Risk เป็น $ อย่างเดียว ไม่มี ฿ · รูป 'ทุน $x (n%) · Risk $y (m%)'", re.match(r"^ทุน \$[\d.,]+[kM]? \([\d.]+%\) · Risk \$[\d.,]+[kM]? \([\d.]+%\)$", cost) is not None and "฿" not in cost and "≈" not in cost, cost)
        ff = txt(page, sc + " [data-c-ff]")
        check(f"{tag} 6 มี 'FF x% · เพดานไม้แรก y%'", re.match(r"^FF \d+% · เพดานไม้แรก [\d.]+%$", ff) is not None, ff)
        check(f"{tag} 6 Entry · Stop บรรทัดเดียว 'Entry 100 · Stop 90'", txt(page, sc + " [data-c-entry]") == "Entry 100 · Stop 90", txt(page, sc + " [data-c-entry]"))
        how = js(page, "(s)=>{ const d=document.querySelector(s+' [data-c-how]'); return d ? {open:d.open, cash:!!d.querySelector('[data-c-cash]'), round:!!d.querySelector('[data-c-round]'), src:!!d.querySelector('[data-c-ffsrc]'), ctl:!!d.querySelector('[data-c-ctl]')} : null; }", sc)
        check(f"{tag} 6 'วิธีคิด' พับอยู่ · ข้างในมี เงินสด/งบ · ปัด · ที่มาของ FF · คุมด้วยอะไร (อยู่ใน DOM)", how and how["open"] is False and how["cash"] and how["round"] and how["src"] and how["ctl"], json.dumps(how))
        shot(page, f"ux2-core-plan-us-{sfx}.png", sc)
        page.locator(sc + " [data-c-how] summary").click(); wait(page, 250)
        check(f"{tag} 6 กางวิธีคิด → เห็นบรรทัดเงินสด (× FF) และปัด", js(page, "(s)=>document.querySelector(s+' [data-c-how]').open", sc) is True and "× FF" in txt(page, sc + " [data-c-cash]") and "ปัด" in txt(page, sc + " [data-c-round]"), txt(page, sc + " [data-c-cash]"))
        shot(page, f"ux2-core-plan-howto-{sfx}.png", sc)
        check(f"{tag} 6 ปุ่มเดิมครบ (บันทึกซื้อไม้ 1 · ลบแผน · ⋯)", cnt(page, sc + " [data-c-buy1]") == 1 and cnt(page, sc + " [data-c-delplan]") == 1 and cnt(page, sc + " [data-c-more]") == 1)
        check(f"{tag} 8 phase Up → บรรทัดเตือนไม่มีส่วน Phase (เหลือเฉพาะ Tier badge ระดับ warn ถ้ามี)", cnt(page, sc + " [data-c-phase-warn]") == 0 and "Phase:" not in (txt(page, sc + " [data-c-warnline]") or ""), txt(page, sc)[:200])
        if w < 600:
            m = js(page, "(s)=>{ const e=document.querySelector(s+' .ccBig'); const q=document.querySelector(s+' [data-c-qty]'); const r=e.getBoundingClientRect(); return {oneLine: r.height < 70, sw: document.documentElement.scrollWidth, W: innerWidth, over: document.querySelector(s).scrollWidth>document.querySelector(s).clientWidth+1}; }", sc)
            check(f"{tag} 12 390px: Card แผน Core ไม่ล้น · ตัวใหญ่ไม่ตัดบรรทัด", m["oneLine"] and m["sw"] <= m["W"] + 1 and not m["over"], json.dumps(m))
        check(f"{tag} 12 ไม่มี console error (Card แผน)", err_free(ce, pe))
    finally:
        b.close()
    # ── 8 เตือนรวม: Side + Tier badge warn (ไม่อยู่ใน Watchlist)
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "side", "at": TODAY}}})
    try:
        sc = S("cplan"); wl = txt(page, sc + " [data-c-warnline]")
        badges = js(page, "(s)=>[...document.querySelectorAll(s+' .ccChip[data-c-tierbadge]')].map(e=>e.dataset.level)", sc)
        warn_tb = js(page, "()=>coreTierBadges({ticker:'AVGO'}, 'A').filter(b=>b.level==='warn').map(b=>b.text)")
        check(f"{tag} 8 phase Side + Tier badge ระดับ warn → บรรทัด ⚠ เดียวมีทั้ง 2 ข้อความ (คั่น ' · ')", cnt(page, sc + " [data-c-warnline]") == 1 and wl.startswith("⚠ Phase: Side — ยังไม่เข้า uptrend") and len(warn_tb) >= 1 and all(t in wl for t in warn_tb) and " · " in wl, wl + "|" + json.dumps(warn_tb, ensure_ascii=False))
        check(f"{tag} 8 badge ระดับ warn ไม่เป็นชิปแยกอีกแล้ว (เหลือเฉพาะ muted)", "warn" not in badges, json.dumps(badges))
        check(f"{tag} 8 ชิป Tier = 'Tier A · Fortress' (ไม่มี 'เพดานไม้แรก' ในชิป)", re.match(r"^Tier A", txt(page, sc + " [data-c-tier]")) and "เพดานไม้แรก" not in txt(page, sc + " [data-c-tier]"), txt(page, sc + " [data-c-tier]"))
        shot(page, f"ux2-core-plan-us-warn-{sfx}.png", sc)
    finally:
        b.close()
    cards = {"cb": p24.card("cb", "main", "AVGO", plan={"entry": 100, "stop": 90}, tier="B")}
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "up", "at": TODAY}}})
    try:
        check(f"{tag} 8 phase Up + Tier B (ไม่มี warn) → ไม่มีบรรทัดเตือนเลย", cnt(page, S("cb") + " [data-c-warnline]") == 0, txt(page, S("cb"))[:200])
    finally:
        b.close()
    # ── 7 TH
    cards = {"cth": p24.card("cth", "main", "PTT.BK", plan={"entry": 100, "stop": 90}, tier="A")}
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"PTT.BK": {"phase": {"v": "up", "at": TODAY}}})
    try:
        sc = S("cth"); cost = txt(page, sc + " [data-c-cost]")
        check(f"{tag} 7 Card แผน TH → สกุล ฿ อย่างเดียว (ไม่มี $)", re.match(r"^ทุน ฿[\d.,]+[kM]? \([\d.]+%\) · Risk ฿[\d.,]+[kM]? \([\d.]+%\)$", cost) is not None and "$" not in cost, cost)
        page.locator(sc + " [data-c-how] summary").click(); wait(page, 250)
        check(f"{tag} 7 วิธีคิด TH มี 'ปัดหลัก 100'", "ปัดหลัก 100" in txt(page, sc + " [data-c-round]"), txt(page, sc + " [data-c-round]"))
        shot(page, f"ux2-core-plan-th-{sfx}.png", sc)
        check(f"{tag} 7 ไม่มี console error", err_free(ce, pe))
    finally:
        b.close()
    # ── 9 zero-lot / เงินสดคุม / ชนเพดาน Tier
    cards = {"cz": p24.card("cz", "main", "AVGO", plan={"entry": 5000000, "stop": 4999999}, tier="B")}
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "up", "at": TODAY}}})
    try:
        sc = S("cz")
        z = js(page, "(s)=>({zero:!!document.querySelector(s+' [data-c-zero]'), inHow:!!document.querySelector(s+' [data-c-how] [data-c-zero]'), dis:document.querySelector(s+' [data-c-buy1]').disabled})", sc)
        check(f"{tag} 9 zero-lot → คำเตือนเห็นนอก วิธีคิด · ปุ่มซื้อไม้ 1 ปิดเหมือนเดิม", z["zero"] and not z["inHow"] and z["dis"], json.dumps(z))
    finally:
        b.close()
    cards = {"cc": p24.card("cc", "main", "AVGO", plan={"entry": 100, "stop": 99.9}, tier="B")}
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "up", "at": TODAY}}})
    try:
        sc = S("cc")
        tg = js(page, "(s)=>{ const t=document.querySelector(s+' [data-c-tag]'); return t ? {t:t.textContent.trim(), outside: !t.closest('[data-c-how]')} : null; }", sc)
        check(f"{tag} 9 ชนเพดาน Tier / เงินสดคุม → ป้ายเห็นนอก วิธีคิด (เมื่อเกิดเท่านั้น)", tg and tg["t"] in ("ชนเพดาน Tier", "เงินสดคุม") and tg["outside"], json.dumps(tg, ensure_ascii=False))
    finally:
        b.close()
    # DD พัก → ปุ่มปิด + title (ตั้ง ddState ของถัง core แบบเดียวกับ phase37)
    cards = {"cplan": p24.card("cplan", "main", "AVGO", plan={"entry": 100, "stop": 90}, tier="A")}
    def pause(pg):
        js(pg, "()=>{ window.ddCoreBlockNew = ()=>'DD พัก (ทดสอบ)'; renderCorePanel(); }")
        pg.wait_for_timeout(400)
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "up", "at": TODAY}}}, setup=pause)
    try:
        sc = S("cplan")
        d = js(page, "(s)=>{ const b=document.querySelector(s+' [data-c-buy1]'); return b ? {dis:b.disabled, t:b.title} : null; }", sc)
        check(f"{tag} 9 DD พัก → ปุ่มซื้อไม้ 1 ปิด + title เหตุผล", d and d["dis"] and d["t"], json.dumps(d, ensure_ascii=False))
    finally:
        b.close()


def ff_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    cards = {"cplan": p24.card("cplan", "main", "AVGO", plan={"entry": 100, "stop": 90}, tier="A"),
             "copen": p24.open_card("copen", "t1", "NVDA", qty=100, entry=100, sl=90)}
    b, page, ce, pe = plan_card(pw, w, h, label, cards, notes={"AVGO": {"phase": {"v": "up", "at": TODAY}}})
    try:
        bad = re.compile(r"f ตอนนี้|× f(?![A-Za-z])|ประตู f(?![A-Za-z])|f <b>|งบเสี่ยง[^<]{0,12}× f\b")
        pages = {}
        pages["core"] = js(page, "()=>document.body.innerText")
        js(page, "()=>{ switchTab('settings'); }"); wait(page, 400)
        pages["settings"] = js(page, "()=>document.body.innerText") + " " + js(page, "()=>[...document.querySelectorAll('#sCrGate, label')].map(e=>e.textContent).join(' ')")
        js(page, "()=>{ switchTab('today'); todayRefresh && todayRefresh(); }"); wait(page, 500)
        pages["today"] = js(page, "()=>document.body.innerText")
        for k, v in pages.items():
            check(f"{tag} 10 หน้า {k}: ไม่มี 'f ตอนนี้' · '× f' · 'ประตู f' ในข้อความที่มองเห็น", bad.search(v) is None, (bad.search(v).group(0) if bad.search(v) else ""))
        check(f"{tag} 10 มี 'FF' แทน (Core: FF x% · ตั้งค่า: ประตู FF)", "FF" in pages["core"] and "FF gate" not in pages["settings"], pages["core"][:100])   # RG2b — ถอดประตู FF
        check(f"{tag} 10 ไม่เปลี่ยนชื่อตัวแปร/ฟังก์ชัน (cx.F.f · coreFNow · ffBizDaysSince ยังอยู่)", js(page, "()=>typeof coreFNow==='function' && typeof ffBizDaysSince==='function' && typeof coreCtx('main').F.f==='number'"))
        check(f"{tag} 10 ไม่มี console error", err_free(ce, pe))
    finally:
        b.close()


def unchanged_tests(pw, w, h, label):
    """11 การ์ด open / closed (ไม่ใช่ plan) ไม่เปลี่ยน — เทียบ innerText กับ index.backup-pre-UX2.html บน fixture เดียวกัน (ยกเว้น f→FF)"""
    import run_tests_phase25 as p25
    tag = f"[{ENGINE}/{label}]"
    ids = ["aapl", "nvda", "msft", "amzn", "goog"]
    outs = []
    saved = p24.INDEX
    try:
        for index in (saved, BACKUP):
            p24.INDEX = index
            doc, cards = p25.data()
            browser, context, page, ce, pe, dialogs = p25.launch(pw, w, h, doc, cards)
            try:
                p25.go(page)
                o = {}
                for i in ids:
                    p25.expand(page, i)
                    o[i] = js(page, "(i)=>{ const e=document.querySelector('[data-core-card=\"'+i+'\"]'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : ''; }", i)
                outs.append(o)
            finally:
                browser.close()
    finally:
        p24.INDEX = saved
    new, old = outs
    norm = lambda t: re.sub(r"(^|[\s(])f($|[\s)<])", r"\1FF\2", t)
    diffs = {i: [new[i][:160], old[i][:160]] for i in ids if not (new[i] and (new[i] == old[i] or new[i] == norm(old[i])))}
    check(f"{tag} 11 การ์ด open (5 ใบ: ปกติ/แดง/เตือน/ไม่มีราคา/หลายไม้) innerText เหมือนก่อน UX2 (ยกเว้น f→FF) · ไม่ว่างเปล่า", not diffs, json.dumps(diffs, ensure_ascii=False))


def static_tests():
    s = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("S1 ฟังก์ชัน UX2: fltHtml · fltToggle · fltClear · coreFirstLotPlanHtml", all(f"function {n}(" in s for n in ("fltHtml", "fltToggle", "fltClear", "coreFirstLotPlanHtml")))
    check("S2 ไม่เปลี่ยนคีย์/ตัวแปร: localStorage 'dash.phFilter' · 'dash.tqFilter' ยังใช้", "dash.phFilter" in s and "dash.tqFilter" in s)
    check("S3 ปุ่ม Port ของ Watchlist ไม่ได้อยู่ใน fltHtml", "wlPills" not in s.split("function fltHtml()")[1].split("function fltToggle")[0])


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            filter_tests(pw, w, h, label)
            core_tests(pw, w, h, label)
            ff_tests(pw, w, h, label)
            unchanged_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 64 / UX2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
