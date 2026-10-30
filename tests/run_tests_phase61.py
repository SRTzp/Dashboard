#!/usr/bin/env python3
"""PH1 — Trend Phase ต่อหุ้น (Side · Start▲ · Up · Weak▼) ใน Watchlist / Candidates + ตัวกรอง/เรียง + แสดงในแผน Core · เทส 61
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-09 (ศ.) เวลาไทย
ภาพ tests/screenshots/ph1-{wl,cand,menu,filter,core-card}-{1440,390}.png
รัน: python3 run_tests_phase61.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase40 as P40
import run_tests_phase59 as VW

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
TODAY = VW.TODAY
txt, cnt, rect, wait, doc_of = VW.txt, VW.cnt, VW.rect, VW.wait, VW.doc_of
PHV = {"start": "Start▲", "up": "Up", "side": "Side", "weak": "Weak▼"}


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


def days_ago(n): return js_days(n)


def js_days(n):
    import datetime
    d = datetime.date.fromisoformat(TODAY) - datetime.timedelta(days=n)
    return d.isoformat()


def launch(pw, w, h, wl=("AVGO", "NVDA", "MSFT"), cands=(("CAMT", "Camtek", 1), ("ONTO", "Onto", 2)), notes=None, cards=None, deny=False):
    ideas = [VW.idea([VW.cand(s, n, r) for s, n, r in cands])] if cands else []
    b, c, page, ce, pe, dl, env = VW.launch(pw, w, h, wl=list(wl), ideas=ideas, notes=notes, deny=deny)
    if cards:
        for cid, card in cards.items():
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [cid, card])
        js(page, "()=>{ coreStop(); coreStart(); }"); page.wait_for_timeout(600)
    return b, c, page, ce, pe, dl


def go(page, view="wl"):
    js(page, "(v)=>{ switchTab('watch'); wlSetView(v); }", view); wait(page, 450)


def chips(page): return js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>({s:e.dataset.sym, ph:(e.querySelector('[data-ph-chip]')||{dataset:{}}).dataset.ph||null, t:(e.querySelector('[data-ph-chip]')||{innerText:null}).innerText}))")
def fopen(page):
    """UX2: ตัวกรอง Phase อยู่ในแผง Filter — กางแผงก่อนแตะชิป (idempotent)"""
    if page.locator("[data-flt-panel]").count() == 0 and page.locator("[data-flt-btn]").count():
        page.locator("[data-flt-btn]").click(); wait(page, 250)
def syms(page): return js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>e.dataset.sym)")
def chip_click(page, sym): page.locator(f'.wlR[data-sym="{sym}"] [data-ph-chip]').click(); wait(page, 350)
def pick(page, sym, v):
    chip_click(page, sym)
    page.locator(f'[data-ph-menu][data-sym="{sym}"] [data-ph-set="{v}"]').click(); wait(page, 450)
def note_phase(page, sym): return (doc_of(page, "stockNotes", sym) or {}).get("phase")
def err_free(ce, pe): return not VW.real_errs(ce) and not pe


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ── 1 ไม่มี phase
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        go(page, "wl")
        cs = chips(page)
        check(f"{tag} 1 Watchlist ไม่มี phase → ชิป '—' ทุกแถว (3 แถว)", len(cs) == 3 and all(x["ph"] == "none" and x["t"] == "—" for x in cs), json.dumps(cs, ensure_ascii=False))
        fopen(page)
        phx = js(page, "()=>({ph:[...document.querySelectorAll('[data-flt-panel] [data-ph-f]')].map(e=>e.textContent.trim()).join(''), sort:[...document.querySelectorAll('[data-flt-panel] [data-ph-sort]')].map(e=>e.textContent.trim()).join('|')})")
        check(f"{tag} 1 ตัวกรองไม่กรองอะไร (ไม่เลือก = ทั้งหมด) · แผง Filter มีชิป Start▲ Up Side Weak▼ — เรียง ปกติ|Phase (UX2: ย้ายเข้าแผง)", phx == {"ph": "Start▲UpSideWeak▼—", "sort": "ปกติ|Phase"} and len(syms(page)) == 3, json.dumps(phx, ensure_ascii=False))
        rh = js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>({h:e.getBoundingClientRect().height, one:(()=>{const r=e.getBoundingClientRect(); return [...e.querySelectorAll('.wlRn,.wlMkt,[data-ph-chip]')].every(x=>{const q=x.getBoundingClientRect(); return q.top>=r.top-1 && q.bottom<=r.bottom+1;});})()}))")
        check(f"{tag} 1 แถว Watchlist ยังบรรทัดเดียว (ชื่อ·market·ชิป อยู่ในกรอบแถว · สูง ≤ 56px)", all(x["h"] <= 56 and x["one"] for x in rh), json.dumps(rh))
        shot(page, f"ph1-wl-{sfx}.png", ".wlList")
        go(page, "cand")
        cs = chips(page)
        check(f"{tag} 1 Candidates ไม่มี phase → ชิป '—' ทุกแถว (2 แถว) · แถวบรรทัดเดียว", len(cs) == 2 and all(x["ph"] == "none" for x in cs) and all(x["h"] <= 56 for x in js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>({h:e.getBoundingClientRect().height}))")), json.dumps(cs, ensure_ascii=False))
        shot(page, f"ph1-cand-{sfx}.png", ".wlList")

        # ── 2 ตั้ง AVGO = Start▲
        go(page, "wl")
        sel0 = js(page, "()=>wlSel"); open0 = js(page, "()=>wlMobOpen")
        chip_click(page, "AVGO")
        check(f"{tag} 2 แตะชิป → เมนู 4 ค่า + ล้าง · ไม่เปิดการ์ด/ไม่เลือกแถว", cnt(page, '[data-ph-menu] [data-ph-set]') == 4 and cnt(page, "[data-ph-menu] [data-ph-clear]") == 1 and js(page, "()=>wlSel") == sel0 and js(page, "()=>wlMobOpen") == open0,
              json.dumps([js(page, "()=>wlSel"), sel0, js(page, "()=>wlMobOpen")]))
        shot(page, f"ph1-menu-{sfx}.png", ".wlList")
        page.locator('[data-ph-menu][data-sym="AVGO"] [data-ph-set="start"]').click(); wait(page, 450)
        check(f"{tag} 2 AVGO = Start▲ → stockNotes/AVGO.phase = {{v:'start', at:วันนี้}}", note_phase(page, "AVGO") == {"v": "start", "at": TODAY}, json.dumps(note_phase(page, "AVGO")))
        col = js(page, "()=>{ const e=document.querySelector('.wlR[data-sym=AVGO] [data-ph-chip]'); const s=getComputedStyle(e); const t=document.createElement('i'); t.style.color='var(--teal)'; document.body.appendChild(t); const tc=getComputedStyle(t).color; t.remove(); return {ph:e.dataset.ph, text:e.innerText, color:s.color, teal:tc}; }")
        check(f"{tag} 2 ชิป AVGO = 'Start▲' สี teal", col["ph"] == "start" and col["text"].strip() == "Start▲" and col["color"] == col["teal"], json.dumps(col, ensure_ascii=False))
        check(f"{tag} 2 เมนูปิดหลังเลือก", cnt(page, "[data-ph-menu]") == 0, "")
        pick(page, "NVDA", "up"); pick(page, "MSFT", "side")
        cs = {x["s"]: x["ph"] for x in chips(page)}
        check(f"{tag} 2 ตั้ง NVDA=Up · MSFT=Side แล้วชิปตามค่า (สีต่างกัน 4 ค่า: start teal · up green · side เทา · weak amber)", cs == {"AVGO": "start", "NVDA": "up", "MSFT": "side"}, json.dumps(cs))
        pick(page, "MSFT", "weak")
        colors = js(page, "()=>{ const o={}; ['start','up','side','weak'].forEach(k=>{ const e=document.createElement('span'); e.className='phChip ph-'+k; document.body.appendChild(e); o[k]=getComputedStyle(e).color+'|'+getComputedStyle(e).backgroundColor; e.remove(); }); return o; }")
        check(f"{tag} 2 สีชิป 4 ค่าไม่ซ้ำกัน", len(set(colors.values())) == 4, json.dumps(colors))
        pick(page, "MSFT", "side")
        # ล้าง
        chip_click(page, "MSFT"); page.locator('[data-ph-menu][data-sym="MSFT"] [data-ph-clear]').click(); wait(page, 450)
        check(f"{tag} 2 ล้าง → phase เป็น null · ชิปกลับเป็น '—'", note_phase(page, "MSFT") is None and {x["s"]: x["ph"] for x in chips(page)}["MSFT"] == "none", json.dumps(note_phase(page, "MSFT")))
        pick(page, "MSFT", "side")

        # ── 3 Candidate → Watchlist ค่าตามไปเอง
        go(page, "cand")
        pick(page, "CAMT", "up")
        check(f"{tag} 3 Candidate CAMT = Up → stockNotes/CAMT.phase = up", note_phase(page, "CAMT") == {"v": "up", "at": TODAY}, json.dumps(note_phase(page, "CAMT")))
        page.locator('.wlR[data-sym="CAMT"] .wlRn').click(); wait(page, 400)
        page.locator('[data-cand-x] [data-c-add]').click(); wait(page, 400)
        js(page, "(s)=>{ ltSheetClose(); const c = td3Cands(thaiToday()).find(x=>x.key===wlSymKey(s)); csEvalWrite(c.sym, Calc.evalNorm({rs:{sustained:'passed'}, gate5:['passed','passed','passed'], stars:1})); td4Pro = {sym:c.sym, key:c.key, note:'x', tier:true, rs:false, stars:1}; td4ProSave(); }", "CAMT")   # TD4b: ＋ ของ Candidate ไม่เพิ่มตรงแล้ว → ย้ายด้วยฟอร์ม Move (td4ProSave · ค่า Tier/Phase ตามไปเหมือนเดิม); wait(page, 700)
        go(page, "wl")
        cs = {x["s"]: x["ph"] for x in chips(page)}
        check(f"{tag} 3 ＋ เพิ่มเข้า Watchlist → แถว Watchlist CAMT แสดง Up", cs.get("CAMT") == "up", json.dumps(cs))
        check(f"{tag} 3 ย้ายแล้ว phase ไม่หาย (เอกสารเดียวกัน)", note_phase(page, "CAMT") == {"v": "up", "at": TODAY})

        # ── 4 ตัวกรอง + เรียง
        # สถานะตอนนี้ WL: AVGO start · NVDA up · MSFT side · CAMT up
        fopen(page)
        page.locator('[data-ph-f="start"]').click(); wait(page, 300)
        page.locator('[data-ph-f="up"]').click(); wait(page, 300)
        check(f"{tag} 4 ตัวกรอง Start▲ + Up → เฉพาะ 2 ค่านี้ (AVGO · NVDA · CAMT)", sorted(syms(page)) == ["AVGO", "CAMT", "NVDA"], json.dumps(syms(page)))
        shot(page, f"ph1-filter-{sfx}.png", ".wlList")
        page.locator('[data-ph-f="start"]').click(); page.locator('[data-ph-f="up"]').click(); wait(page, 300)
        check(f"{tag} 4 เอาติ๊กออกหมด → แสดงทั้งหมด", len(syms(page)) == 4, json.dumps(syms(page)))
        js(page, "()=>{ wlSetView('wl'); }"); pick(page, "MSFT", "weak"); fopen(page); page.locator('[data-ph-sort="on"]').click(); wait(page, 350)
        check(f"{tag} 4 เรียง Phase: start → up → side → weak → ว่าง (AVGO · NVDA · CAMT · MSFT)", syms(page) == ["AVGO", "CAMT", "NVDA", "MSFT"] or syms(page) == ["AVGO", "NVDA", "CAMT", "MSFT"], json.dumps(syms(page)))
        first_two = [x["ph"] for x in chips(page)]
        check(f"{tag} 4 ลำดับชิปตามเรียง = start, up, up, weak", first_two == ["start", "up", "up", "weak"], json.dumps(first_two))
        fopen(page); page.locator('[data-ph-sort="off"]').click(); wait(page, 300)
        js(page, "()=>{ phMenu=''; }")
        # ไม่มี phase ทั้งแถว: '—' กรอง
        fopen(page); page.locator('[data-ph-f="none"]').click(); wait(page, 300)
        check(f"{tag} 4 ตัวกรอง '—' → เฉพาะที่ยังไม่ตั้ง (ตอนนี้ไม่มี)", syms(page) == [], json.dumps(syms(page)))
        fopen(page); page.locator('[data-ph-f="none"]').click(); wait(page, 300)
        go(page, "cand")
        check(f"{tag} 4 ตัวกรอง/เรียงใช้กับ Candidates ด้วย (ONTO ยังไม่ตั้ง = '—')", js(page, "()=>phFilter.size") == 0, "")
        fopen(page); page.locator('[data-ph-f="none"]').click(); wait(page, 300)
        check(f"{tag} 4 Candidates + ตัวกรอง '—' → ONTO", syms(page) == ["ONTO"], json.dumps(syms(page)))
        mem = js(page, "()=>localStorage.getItem('dash.phFilter')")
        check(f"{tag} 4 จำค่าต่อเครื่อง (localStorage dash.phFilter = [\"none\"])", mem == '["none"]', str(mem))
        fopen(page); page.locator('[data-ph-f="none"]').click(); wait(page, 300)
        if w < 600:
            fopen(page); js(page, "()=>{ if(document.querySelector('[data-flt-panel]')) document.querySelector('[data-flt-btn]').click(); }"); wait(page, 250)
            m = js(page, "()=>{ const f=document.querySelector('.fltBar'); return {sw:f.scrollWidth, cw:f.clientWidth, page:document.documentElement.scrollWidth-innerWidth}; }")
            check(f"{tag} 4 390px: แถว Filter ไม่ล้นหน้า (UX2: แถวเดียว ตัด … เอง)", m["page"] <= 1 and m["sw"] <= m["cw"] + 1, json.dumps(m))
        check(f"{tag} 4 ไม่มี console error", err_free(ce, pe), json.dumps(VW.real_errs(ce)[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()

    # ── 5 ข้อมูลช่วย
    b, c, page, ce, pe, dl = launch(pw, w, h, wl=("AVGO", "NVDA", "MSFT"), cands=())
    try:
        P39.seed(page, ["users", "testuid", "prices", "AVGO"], {"close": 200, "ema10w": 190, "closeDate": "2026-10-09", "suspect": False})
        P39.seed(page, ["users", "testuid", "prices", "NVDA"], {"close": 100, "ema10w": 110, "closeDate": "2026-10-09", "suspect": False})
        js(page, "()=>{ pxStop(); pxStart(); }"); wait(page, 700)
        go(page, "wl")
        chip_click(page, "AVGO")
        t = txt(page, "[data-ph-menu] [data-ph-help]")
        check(f"{tag} 5 มี prices close > ema10w → เมนูมี 'ปิด W เหนือ EMA10'", t == "ปิด W เหนือ EMA10", str(t))
        page.keyboard.press("Escape"); js(page, "()=>{ phMenu=''; renderWatchlist(); }"); wait(page, 200)
        chip_click(page, "NVDA")
        check(f"{tag} 5 close < ema10w → 'ปิด W ใต้ EMA10'", txt(page, "[data-ph-menu] [data-ph-help]") == "ปิด W ใต้ EMA10", str(txt(page, "[data-ph-menu] [data-ph-help]")))
        js(page, "()=>{ phMenu=''; renderWatchlist(); }"); wait(page, 200)
        chip_click(page, "MSFT")
        check(f"{tag} 5 ไม่มี prices → ไม่มีบรรทัดข้อมูลช่วย", cnt(page, "[data-ph-help]") == 0)
        cs = {x["s"]: x["ph"] for x in chips(page)}
        check(f"{tag} 5 ข้อมูลช่วยไม่เปลี่ยนค่า phase เอง (ยัง '—' ทุกแถว · ไม่มีเอกสาร stockNotes ถูกเขียน)", set(cs.values()) == {"none"} and doc_of(page, "stockNotes", "AVGO") is None, json.dumps(cs))
        check(f"{tag} 5 ไม่มี console error", err_free(ce, pe))
    finally:
        b.close()

    # ── 6 อายุ phase
    notes = {"AVGO": {"phase": {"v": "up", "at": days_ago(15)}}, "NVDA": {"phase": {"v": "up", "at": days_ago(13)}}, "MSFT": {"phase": {"v": "up", "at": days_ago(14)}}}
    b, c, page, ce, pe, dl = launch(pw, w, h, cands=(), notes=notes)
    try:
        go(page, "wl")
        d = js(page, "()=>Object.fromEntries([...document.querySelectorAll('.wlR')].map(e=>[e.dataset.sym, {dot:!!e.querySelector('[data-ph-dot]'), t:(e.querySelector('[data-ph-chip]')||{}).title}]))")
        check(f"{tag} 6 phase.at เก่า 15 วัน → มีจุดทบทวน · 13 วัน → ไม่มี · 14 วัน → ไม่มี", d["AVGO"]["dot"] and not d["NVDA"]["dot"] and not d["MSFT"]["dot"], json.dumps(d, ensure_ascii=False))
        check(f"{tag} 6 title บอกวันที่ตั้ง", days_ago(15) in d["AVGO"]["t"] and days_ago(13) in d["NVDA"]["t"], json.dumps(d, ensure_ascii=False))
        pick(page, "AVGO", "up")
        check(f"{tag} 6 ตั้งใหม่ → วันที่เป็นวันนี้ · จุดหาย", note_phase(page, "AVGO") == {"v": "up", "at": TODAY} and cnt(page, ".wlR[data-sym=AVGO] [data-ph-dot]") == 0, json.dumps(note_phase(page, "AVGO")))
        check(f"{tag} 6 ไม่มี console error", err_free(ce, pe))
    finally:
        b.close()

    # ── 7 การ์ดแผน Core
    cards = {"cplan": p24.card("cplan", "main", "AVGO", plan={"entry": 100, "stop": 90}, tier="A"), "cplan2": p24.card("cplan2", "main", "NVDA", plan={"entry": 100, "stop": 90}, tier="A")}
    notes = {"AVGO": {"phase": {"v": "side", "at": TODAY}}, "NVDA": {"phase": {"v": "up", "at": TODAY}}}
    b, c, page, ce, pe, dl = launch(pw, w, h, cands=(), notes=notes, cards=cards)
    try:
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); wait(page, 600)
        sel = lambda cid: f'[data-core-card="{cid}"]'
        if page.locator(sel("cplan") + " [data-c-row]").count():
            for cid in ("cplan", "cplan2"):
                if js(page, "(s)=>document.querySelector(s+' [data-c-row]').getAttribute('aria-expanded')", sel(cid)) != "true": page.locator(sel(cid) + " [data-c-row]").click(); wait(page, 250)
        warn = txt(page, sel("cplan") + " [data-c-phase-warn]")
        check(f"{tag} 7 การ์ดแผน Core: Side → ชิป phase + เตือน '⚠ Phase: Side — ยังไม่เข้า uptrend' (UX2: รวมกับเตือน Tier บรรทัดเดียว)", warn.startswith("⚠ Phase: Side — ยังไม่เข้า uptrend") and cnt(page, sel("cplan") + " [data-c-phase]") == 1, str(warn))
        check(f"{tag} 7 Up → มีชิป ไม่มีคำเตือน", cnt(page, sel("cplan2") + " [data-c-phase]") == 1 and cnt(page, sel("cplan2") + " [data-c-phase-warn]") == 0)
        shot(page, f"ph1-core-card-{sfx}.png", sel("cplan"))
        check(f"{tag} 7 บันทึกแผนได้ทั้ง Side และ Up (ปุ่มบันทึกซื้อไม้ 1 ไม่ถูกปิดเพราะ phase)", js(page, "(s)=>{ const b=document.querySelector(s+' [data-c-buy1]'); return b ? b.disabled : null; }", sel("cplan")) == js(page, "(s)=>{ const b=document.querySelector(s+' [data-c-buy1]'); return b ? b.disabled : null; }", sel("cplan2")), "")
        page.locator(sel("cplan") + " [data-c-phase]").click(); wait(page, 600)
        check(f"{tag} 7 แตะชิปบนการ์ด = ไปแถว Watchlist (แท็บ watch · เลือก AVGO)", js(page, "()=>activeTab") == "watch" and js(page, "()=>wlSel") == "AVGO", json.dumps([js(page, "()=>activeTab"), js(page, "()=>wlSel")]))
        check(f"{tag} 7 ไม่มี console error", err_free(ce, pe))
    finally:
        b.close()

    # ── 7b ไม่ตั้ง phase → เตือนด้วย
    b, c, page, ce, pe, dl = launch(pw, w, h, cands=(), cards={"cplan": p24.card("cplan", "main", "AVGO", plan={"entry": 100, "stop": 90}, tier="A")})
    try:
        js(page, "()=>{ switchTab('plan'); setPlanScope('stock'); }"); wait(page, 600)
        if js(page, "()=>document.querySelector('[data-core-card=cplan] [data-c-row]').getAttribute('aria-expanded')") != "true": page.locator("[data-core-card=cplan] [data-c-row]").click(); wait(page, 250)
        check(f"{tag} 7 phase ว่าง → ชิป 'Phase —' + เตือน (ยังไม่ตั้ง)", txt(page, "[data-core-card=cplan] [data-c-phase-warn]").startswith("⚠ Phase: ยังไม่ตั้ง") and "Phase —" in txt(page, "[data-core-card=cplan] [data-c-phase]"), str(txt(page, "[data-core-card=cplan] [data-c-phase-warn]")))
    finally:
        b.close()

    # ── 8 ไม่มีสิทธิ์อ่าน stockNotes
    b, c, page, ce, pe, dl = launch(pw, w, h, deny=True)
    try:
        go(page, "wl")
        check(f"{tag} 8 ไม่มีสิทธิ์อ่าน stockNotes → ไม่มีชิป phase · ไม่มีแถบตัวกรอง phase · แถวยังครบ", cnt(page, "[data-ph-chip]") == 0 and cnt(page, "[data-ph-filters]") == 0 and len(syms(page)) == 3, json.dumps(syms(page)))
        go(page, "cand")
        check(f"{tag} 8 Candidates ทำงานปกติ (แถว 2 · ไม่มีชิป)", len(syms(page)) == 2 and cnt(page, "[data-ph-chip]") == 0)
        check(f"{tag} 8 ไม่มี pageerror", not pe, json.dumps(pe[:3]))
    finally:
        b.close()

    # ── 9 390px
    if w < 600:
        notes = {"AVGO": {"phase": {"v": "start", "at": TODAY}}}
        b, c, page, ce, pe, dl = launch(pw, w, h, notes=notes)
        try:
            go(page, "wl")
            m = js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>{ const r=e.getBoundingClientRect(); const ks=[...e.children].filter(x=>x.getBoundingClientRect().width>0).map(x=>x.getBoundingClientRect()); const tops=ks.map(q=>Math.round(q.top+q.height/2)); return {h:r.height, spread:Math.max(...tops)-Math.min(...tops), over:e.scrollWidth>e.clientWidth+1}; })")
            check(f"{tag} 9 แถว Watchlist บรรทัดเดียว (กึ่งกลางทุกชิ้นอยู่ระดับเดียวกัน) · ไม่ล้น", all(x["spread"] <= 14 and not x["over"] for x in m), json.dumps(m))
            check(f"{tag} 9 หน้าไม่ล้นแนวนอน", VW.overflow(page) <= 1, str(VW.overflow(page)))
            go(page, "cand")
            m = js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>{ const r=e.getBoundingClientRect(); return {h:r.height, over:e.scrollWidth>e.clientWidth+1}; })")
            check(f"{tag} 9 แถว Candidate ไม่ล้น · ไม่สูงผิดปกติ", all(x["h"] <= 56 and not x["over"] for x in m), json.dumps(m))
            check(f"{tag} 9 ไม่มี console error", err_free(ce, pe))
        finally:
            b.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 61 / PH1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
