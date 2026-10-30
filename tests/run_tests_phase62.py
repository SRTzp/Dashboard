#!/usr/bin/env python3
"""TQ1 — ด่าน Tier เร็วที่แถว Candidate (A-Fortress · A-Growth · B · ไม่ผ่าน · ยังไม่เช็ก) + การบ้านเริ่มที่ Tier · เทส 62
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-09 (ศ.) เวลาไทย
ภาพ tests/screenshots/tq1-{cand-tier,cand-row,hw}-{1440,390}.png
รัน: python3 run_tests_phase62.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase39 as P39
import run_tests_phase59 as VW

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
TODAY = VW.TODAY
txt, cnt, rect, wait, doc_of = VW.txt, VW.cnt, VW.rect, VW.wait, VW.doc_of


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


def launch(pw, w, h, wl=(), cands=(("CAMT", "Camtek", 1), ("ONTO", "Onto", 2), ("NVMI", "Nova", 3)), notes=None, wl_kw=None):
    ideas = [VW.idea([VW.cand(s, n, r) for s, n, r in cands])] if cands else []
    wls = [((s, None, (wl_kw or {}).get(s, {})) if isinstance(s, str) else s) for s in wl]
    b, c, page, ce, pe, dl, env = VW.launch(pw, w, h, wl=wls, ideas=ideas, notes=notes)
    return b, c, page, ce, pe, dl


def fopen(page):
    """UX2: ตัวกรอง Tier อยู่ในแผง Filter — กางแผงก่อนแตะชิป (idempotent)"""
    if page.locator("[data-flt-panel]").count() == 0 and page.locator("[data-flt-btn]").count():
        page.locator("[data-flt-btn]").click(); VW.wait(page, 250)
def go(page, view="cand"):
    js(page, "(v)=>{ switchTab('watch'); wlSetView(v); }", view); wait(page, 450)


def syms(page): return js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>e.dataset.sym)")
def expand(page, sym):
    if not cnt(page, f'[data-cand-x][data-sym="{sym}"]'):
        page.locator(f'.wlR[data-sym="{sym}"] .wlRn').click(); wait(page, 400)
def set_tier(page, sym, code):
    expand(page, sym)
    page.locator(f'[data-cand-x][data-sym="{sym}"] [data-tq-set="{code}"]').click(); wait(page, 450)
def note_tier(page, sym): return (doc_of(page, "stockNotes", sym) or {}).get("tier")
def wl_doc(page, sym): return doc_of(page, "watchlist", sym)
def badge(page, sym): return js(page, "(s)=>{ const e=document.querySelector('.wlR[data-sym=\"'+s+'\"] [data-tq-badge]'); return e ? e.innerText.trim() : null; }", sym)
def errs(ce, pe): return not VW.real_errs(ce) and not pe


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ── 1 Candidate ใหม่ · เกณฑ์อ่านจากค่าตั้ง
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        go(page, "cand")
        check(f"{tag} 1 Candidate ใหม่ → ยังไม่เช็ก · ไม่มีป้าย Tier ทุกแถว", len(syms(page)) == 3 and cnt(page, "[data-tq-badge]") == 0, json.dumps(syms(page)))
        expand(page, "CAMT")
        first = js(page, "()=>{ const x=document.querySelector('[data-cand-x]'); return x && x.children[0] ? x.children[0].hasAttribute('data-tq') : null; }")
        check(f"{tag} 1 แถวขยายมีแถว Tier บนสุด (ก่อน Event/Fund./Tech) · 4 ชิป A-F A-G B ไม่ผ่าน · 'ยังไม่เช็ก'", first is True and [x.strip() for x in js(page, "()=>[...document.querySelectorAll('[data-cand-x] [data-tq-set]')].map(e=>e.innerText)")] == ["A-F", "A-G", "B", "ไม่ผ่าน"] and cnt(page, "[data-tq-none]") == 1, str(first))
        f0 = txt(page, "[data-tq-crit-f]"); g0 = txt(page, "[data-tq-crit-g]")
        check(f"{tag} 1 เกณฑ์ A ทั้ง 2 มุมตามค่าตั้ง (ROIC > 12% · ND/EBITDA < 2 · FCF > 80% · รายได้โต ≥ 20% · CAGR ≥ 15% · ND < 3)", "ROIC > 12%" in f0 and "ND/EBITDA < 2" in f0 and "FCF conv > 80%" in f0 and "รายได้โต ≥ 20%" in g0 and "CAGR 3 ปี ≥ 15%" in g0 and "ND/EBITDA < 3" in g0, f0 + " | " + g0)
        js(page, "()=>{ const a=acctList.find(x=>(x.ports||ACCT_PORT_KEYS).includes('core'))||acctList[0]; const st=a.id===acctActive?state:acctBooks[a.id]; st.settings.coreRisk=Object.assign({}, st.settings.coreRisk, {tierRoic:15}); renderWatchlist(); }"); wait(page, 400)
        check(f"{tag} 1 แก้ค่าตั้ง ROIC 12→15 → ข้อความเกณฑ์เปลี่ยนเป็น ROIC > 15%", "ROIC > 15%" in txt(page, "[data-tq-crit-f]"), txt(page, "[data-tq-crit-f]"))
        shot(page, f"tq1-cand-tier-{sfx}.png", ".wlList")

        # ── 2 เลือก A-G → เก็บ · ป้าย · แตะซ้ำล้าง
        set_tier(page, "CAMT", "AG")
        check(f"{tag} 2 A-G → stockNotes/CAMT.tier = {{tier:'A', tier_lens:'growth', tier_set_at:วันนี้}}", note_tier(page, "CAMT") == {"tier": "A", "tier_lens": "growth", "tier_set_at": TODAY}, json.dumps(note_tier(page, "CAMT")))
        check(f"{tag} 2 ป้ายหลังชื่อ = 'A'", badge(page, "CAMT") == "A", str(badge(page, "CAMT")))
        check(f"{tag} 2 ชิป A-G ถูกเลือก (aria-pressed) · 'ยังไม่เช็ก' หาย", js(page, "()=>document.querySelector('[data-cand-x] [data-tq-set=AG]').getAttribute('aria-pressed')") == "true" and cnt(page, "[data-tq-none]") == 0)
        set_tier(page, "CAMT", "AG")
        check(f"{tag} 2 แตะซ้ำ → กลับเป็นยังไม่เช็ก (tier = null · ไม่มีป้าย)", note_tier(page, "CAMT") is None and badge(page, "CAMT") is None, json.dumps(note_tier(page, "CAMT")))
        set_tier(page, "CAMT", "B")
        check(f"{tag} 2 B → tier B · ไม่มี lens · ป้าย 'B'", note_tier(page, "CAMT") == {"tier": "B", "tier_lens": None, "tier_set_at": TODAY} and badge(page, "CAMT") == "B", json.dumps(note_tier(page, "CAMT")))

        # ── 3 A-F → เพิ่มเข้า Watchlist
        set_tier(page, "CAMT", "AF")
        check(f"{tag} 3 A-F → tier A / fortress", note_tier(page, "CAMT") == {"tier": "A", "tier_lens": "fortress", "tier_set_at": TODAY}, json.dumps(note_tier(page, "CAMT")))
        page.locator('[data-cand-x] [data-c-add]').click(); wait(page, 400)
        js(page, "(s)=>{ ltSheetClose(); const c = td3Cands(thaiToday()).find(x=>x.key===wlSymKey(s)); csEvalWrite(c.sym, Calc.evalNorm({rs:{sustained:'passed'}, gate5:['passed','passed','passed'], stars:1})); td4Pro = {sym:c.sym, key:c.key, note:'x', tier:true, rs:false, stars:1}; td4ProSave(); }", "CAMT")   # TD4b: ＋ ของ Candidate ไม่เพิ่มตรงแล้ว → ย้ายด้วยฟอร์ม Move (td4ProSave · ค่า Tier/Phase ตามไปเหมือนเดิม); wait(page, 800)
        d = wl_doc(page, "CAMT") or {}
        check(f"{tag} 3 ＋ เพิ่มเข้า Watchlist → watchlist doc มี tier A / fortress / tier_set_at", d.get("tier") == "A" and d.get("tier_lens") == "fortress" and d.get("tier_set_at") == TODAY, json.dumps(d, ensure_ascii=False)[:300])
        go(page, "wl")
        lab = js(page, "()=>{ const it=wlItems.find(x=>x.ticker==='CAMT'); return it ? wlTierLabel(it) : null; }")
        check(f"{tag} 3 ป้าย Tier ใน Watchlist = 'A · Fortress'", lab == "A · Fortress", str(lab))
        check(f"{tag} 3 ไม่มีป้าย Candidate (✕/A/B ของ TQ1) ในแถว Watchlist", cnt(page, '.wlR[data-sym="CAMT"] [data-tq-badge]') == 0)
        check(f"{tag} 3 ไม่มี console error", errs(ce, pe), json.dumps(VW.real_errs(ce)[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()

    # ── 3b Watchlist ที่มี tier อยู่แล้ว → ไม่ทับ
    b, c, page, ce, pe, dl = launch(pw, w, h, wl=("AVGO",), cands=(("CAMT", "Camtek", 1),), wl_kw={"AVGO": {"tier": "B", "tier_set_at": "2026-09-01"}}, notes={"AVGO": {"tier": {"tier": "A", "tier_lens": "growth", "tier_set_at": TODAY}}})
    try:
        js(page, "()=>wlOpenAdd('AVGO')"); wait(page, 300)
        page.click("#wlAddOverlay [onclick='wlAddSave()']"); wait(page, 700)
        d = wl_doc(page, "AVGO") or {}
        check(f"{tag} 3 Watchlist ที่มี tier อยู่แล้ว (B) → ไม่ทับด้วยค่าจาก stockNotes", d.get("tier") == "B" and d.get("tier_set_at") == "2026-09-01" and "tier_lens" not in d, json.dumps(d, ensure_ascii=False)[:300])
    finally:
        b.close()

    # ── 4 ไม่ผ่าน → confirm
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        go(page, "cand")
        set_tier(page, "ONTO", "fail")
        check(f"{tag} 4 ไม่ผ่าน → ป้าย '✕' · tier fail", badge(page, "ONTO") == "✕" and (note_tier(page, "ONTO") or {}).get("tier") == "fail", json.dumps(note_tier(page, "ONTO")))
        shot(page, f"tq1-cand-row-{sfx}.png", ".wlList")
        # ยกเลิก = ไม่เพิ่ม: สลับคำตอบ confirm ผ่านตัวแปรหน้าเว็บ
        js(page, "()=>{ window.__cf=[]; window.__cfAns=false; window.confirm=(m)=>{ window.__cf.push(m); return window.__cfAns; }; }")
        page.locator('[data-cand-x] [data-c-add]').click(); wait(page, 400)
        cf = js(page, "()=>window.__cf")
        check(f"{tag} 4 เพิ่มเข้า Watchlist ตัวที่ไม่ผ่าน → confirm 'ONTO ไม่ผ่าน Tier — เพิ่มเข้า Watchlist ต่อไหม'", cf == ["ONTO ไม่ผ่าน Tier — เพิ่มเข้า Watchlist ต่อไหม"], json.dumps(cf, ensure_ascii=False))
        check(f"{tag} 4 ยกเลิก → ไม่เปิดฟอร์มเพิ่ม · ไม่เพิ่ม", not js(page, "()=>document.getElementById('wlAddOverlay').classList.contains('show')") and wl_doc(page, "ONTO") is None)
        js(page, "()=>{ window.__cfAns=true; }")
        page.locator('[data-cand-x] [data-c-add]').click(); wait(page, 400)
        js(page, "(s)=>{ ltSheetClose(); const c = td3Cands(thaiToday()).find(x=>x.key===wlSymKey(s)); csEvalWrite(c.sym, Calc.evalNorm({rs:{sustained:'passed'}, gate5:['passed','passed','passed'], stars:1})); td4Pro = {sym:c.sym, key:c.key, note:'x', tier:true, rs:false, stars:1}; td4ProSave(); }", "ONTO")   # TD4b: ＋ ของ Candidate ไม่เพิ่มตรงแล้ว → ย้ายด้วยฟอร์ม Move (td4ProSave · ค่า Tier/Phase ตามไปเหมือนเดิม); wait(page, 800)
        d = wl_doc(page, "ONTO") or {}
        check(f"{tag} 4 ตกลง = เพิ่ม · watchlist doc ไม่มี tier (ไม่คัดลอก fail)", d.get("ticker") == "ONTO" and "tier" not in d and "tier_set_at" not in d, json.dumps(d, ensure_ascii=False)[:300])
        check(f"{tag} 4 stockNotes ยังเก็บ fail ไว้ (ไม่ลบ)", (note_tier(page, "ONTO") or {}).get("tier") == "fail")

        # ── 5 ตัวกรอง (ONTO ย้ายไป Watchlist แล้ว: เหลือ CAMT · NVMI)
        go(page, "cand")
        set_tier(page, "CAMT", "AF"); set_tier(page, "NVMI", "fail")
        fopen(page)
        tqt = js(page, "()=>[...document.querySelectorAll('[data-flt-panel] [data-tq-f]')].map(e=>e.textContent.trim()).join('|')")
        check(f"{tag} 5 มีชิปตัวกรอง ผ่าน · ไม่ผ่าน · ยังไม่ Check (UX2: อยู่ในแผง Filter · ตัดคำ 'Tier' ท้ายชิป · เช็ก→Check)", tqt == "ผ่าน|ไม่ผ่าน|ยังไม่ Check", tqt)
        fopen(page); page.locator('[data-tq-f="pass"]').click(); wait(page, 300)
        check(f"{tag} 5 ผ่าน Tier (A+B) → เฉพาะ CAMT", syms(page) == ["CAMT"], json.dumps(syms(page)))
        page.locator('[data-tq-f="pass"]').click(); page.locator('[data-tq-f="fail"]').click(); wait(page, 300)
        check(f"{tag} 5 ไม่ผ่าน → เฉพาะ NVMI", syms(page) == ["NVMI"], json.dumps(syms(page)))
        page.locator('[data-tq-f="fail"]').click(); page.locator('[data-tq-f="none"]').click(); wait(page, 300)
        check(f"{tag} 5 ยังไม่เช็ก → ไม่มี (ทุกตัวเช็กแล้ว)", syms(page) == [], json.dumps(syms(page)))
        page.locator('[data-tq-f="none"]').click(); wait(page, 300)
        check(f"{tag} 5 ไม่เลือก = ทั้งหมด", sorted(syms(page)) == ["CAMT", "NVMI"], json.dumps(syms(page)))
        if w < 600:
            m = js(page, "()=>{ const f=document.querySelector('[data-flt-panel]'); return {page:document.documentElement.scrollWidth-innerWidth, pw:f ? f.scrollWidth-f.clientWidth : -1}; }")
            check(f"{tag} 5 390px แผงตัวกรองไม่ล้นหน้า (UX2)", m["page"] <= 1 and m["pw"] <= 1, json.dumps(m))
        check(f"{tag} 5 ไม่มี console error", errs(ce, pe), json.dumps(VW.real_errs(ce)[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()

    # ── 6 การบ้าน
    notes = {"NVMI": {"tier": {"tier": "fail", "tier_lens": None, "tier_set_at": TODAY}}, "ONTO": {"tier": {"tier": "B", "tier_lens": None, "tier_set_at": TODAY}}}
    b, c, page, ce, pe, dl = launch(pw, w, h, wl=(), notes=notes)
    try:
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); wait(page, 500)
        order = js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=homework] [data-hw-part]')].map(e=>e.dataset.hwPart)")
        check(f"{tag} 6 ชิปการบ้านลำดับ Tier → ธุรกิจ · ทำไม · ติดตาม · ออก (id เดิม)", order == ["tier", "biz", "why", "next", "exit"], json.dumps(order))
        lab = js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=homework] [data-hw-part]')].map(e=>e.innerText.trim())")
        check(f"{tag} 6 ป้ายชิป = Tier · ธุรกิจ · ทำไม · ติดตาม · ออก", lab == ["Tier", "ธุรกิจ", "ทำไม", "ติดตาม", "ออก"], json.dumps(lab, ensure_ascii=False))
        cs = js(page, "()=>tdHomeworkCandidates().map(x=>x.t)")
        check(f"{tag} 6 Watchlist ว่าง → Candidate ที่ยังไม่เช็ก (CAMT) มาก่อนที่ผ่านแล้ว (ONTO) · NVMI (ไม่ผ่าน) ไม่ถูกเสนอ", cs == ["CAMT", "ONTO"], json.dumps(cs))
        check(f"{tag} 6 ตัวเสนอวันนี้ = CAMT (ยังไม่เช็ก)", txt(page, ".tdRow[data-kind=homework] .tdWhat b") == "CAMT", str(txt(page, ".tdRow[data-kind=homework] .tdWhat b")))
        shot(page, f"tq1-hw-{sfx}.png", ".tdRow[data-kind=homework]")
        # Watchlist ก่อน Candidate เสมอ (ไม่เปลี่ยน)
        # ติ๊ก part Tier ของ Candidate → เปิดแถว Candidate ที่ขยายไว้ · ไม่ตั้งแทน
        page.locator('.tdRow[data-kind=homework] [data-hw-part="tier"]').click(); wait(page, 700)
        st = js(page, "()=>({tab:activeTab, view:wlView, exp:candExp, sel:wlSel})")
        check(f"{tag} 6 ติ๊ก Tier ของ Candidate → ไปแท็บ Watch · Candidates · แถว CAMT ขยายไว้", st == {"tab": "watch", "view": "cand", "exp": "CAMT", "sel": "CAMT"} and cnt(page, '[data-cand-x][data-sym="CAMT"] [data-tq]') == 1, json.dumps(st))
        check(f"{tag} 6 ไม่ตั้ง Tier แทนผู้ใช้ (stockNotes/CAMT ไม่มี tier)", note_tier(page, "CAMT") is None, json.dumps(note_tier(page, "CAMT")))
        parts = js(page, "()=>{ const d = tdLogDay(thaiToday()); return d.hw ? d.hw.parts : null; }")
        check(f"{tag} 6 log การบ้านเก็บ parts ลำดับเดิม ['tier']", parts == ["tier"], json.dumps(parts))
        check(f"{tag} 6 ไม่มี console error", errs(ce, pe), json.dumps(VW.real_errs(ce)[:3] + pe[:3], ensure_ascii=False))
    finally:
        b.close()

    # ── 7 log การบ้านเก่า
    b, c, page, ce, pe, dl = launch(pw, w, h, wl=("AVGO",), cands=())
    try:
        js(page, """()=>{ const id = tdHome(); const B = getBook(id); B.settings.routineLog = B.settings.routineLog || {};
            B.settings.routineLog['2026-10-08'] = {satState:{}, slots:{}, hw:{pick:'OLDX', done:true, parts:['biz','why','next','exit','tier']}};
            B.settings.routineLog['2026-10-07'] = {satState:{}, slots:{}, hw:{pick:'OLDY', done:true}};
            B.settings.routineLog['2026-10-06'] = {satState:{}, slots:{}, hw:{pick:'OLDZ', done:false}};
            saveBook(id); }""")
        n = js(page, "()=>['2026-10-08','2026-10-07','2026-10-06'].map(d=>tdHwPartsOf(tdSettings().routineLog[d].hw).length)")
        check(f"{tag} 7 log เก่า (parts ลำดับเดิม · done:true ไม่มี parts · done:false) → นับ n/5 = 5 · 5 · 0 เท่าเดิม", n == [5, 5, 0], json.dumps(n))
        js(page, "()=>{ switchTab('today'); todayRefresh(); }"); wait(page, 400)
        check(f"{tag} 7 ไม่มี console error", errs(ce, pe))
    finally:
        b.close()

    # ── 8 390px
    if w < 600:
        notes = {"CAMT": {"phase": {"v": "start", "at": TODAY}, "tier": {"tier": "A", "tier_lens": "growth", "tier_set_at": TODAY}}}
        b, c, page, ce, pe, dl = launch(pw, w, h, notes=notes)
        try:
            go(page, "cand")
            m = js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>{ const r=e.getBoundingClientRect(); const ks=[...e.children].filter(x=>x.getBoundingClientRect().width>0).map(x=>x.getBoundingClientRect()); const mids=ks.map(q=>Math.round(q.top+q.height/2)); return {s:e.dataset.sym, h:r.height, spread:Math.max(...mids)-Math.min(...mids), over:e.scrollWidth>e.clientWidth+1}; })")
            check(f"{tag} 8 แถว Candidate (ชื่อ + phase + ป้าย Tier) บรรทัดเดียว · ไม่ล้น", all(x["spread"] <= 14 and not x["over"] and x["h"] <= 56 for x in m) and cnt(page, '.wlR[data-sym="CAMT"] [data-ph-chip]') == 1 and badge(page, "CAMT") == "A", json.dumps(m))
            expand(page, "CAMT")
            hs = js(page, "()=>[...document.querySelectorAll('[data-cand-x] [data-tq-set]')].map(e=>e.getBoundingClientRect().height)")
            check(f"{tag} 8 ชิป Tier สูง ≥ 32px (4 ตัว)", len(hs) == 4 and min(hs) >= 31.5, json.dumps(hs))
            check(f"{tag} 8 หน้าไม่ล้นแนวนอน (แถวขยาย)", VW.overflow(page) <= 1, str(VW.overflow(page)))
            check(f"{tag} 8 ไม่มี console error", errs(ce, pe), json.dumps(VW.real_errs(ce)[:3] + pe[:3], ensure_ascii=False))
        finally:
            b.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 62 / TQ1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
