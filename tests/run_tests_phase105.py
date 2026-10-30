#!/usr/bin/env python3
"""TD3b — Sector Drivers & Evidence (Flow › RRG → Today): ☆/★ Follow · Drivers & evidence (collapsed) · Copy AI prompt · Import answer (sectorDrivers/v1) ·
Save vs Save & mark reviewed · ธง "Revisit · phase changed" · Today block Sectors · งาน Weekly · ป้ายอังกฤษ + ↗ chip + หัว Leadership · เทส 105
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1280 / 1440 · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/td3b-{flow-1440,flow-390,import-390,today-1440,today-390}.png
รัน: python3 run_tests_phase105.py"""
import copy, json, re
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
THAI = re.compile(r"[฀-๿]")


def settle(page, ms=450): page.wait_for_timeout(ms)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def R(sym, name, quad, dm=0.6, dr=0.2, ratio=102.0, mom=101.5, days=4, off=-3.0, date="2026-09-30"):
    return {"sym": sym, "name": name, "quad": quad, "prevQuad": quad, "dMom": dm, "dRatio": dr, "ratio": ratio, "mom": mom, "days": days, "off52": off, "date": date, "rsTrend": 0.01}


def rows_d():
    return [R("SMH", "Semiconductors", "imp", dm=0.6), R("XLU", "Utilities", "lead", dm=0.3, ratio=103.2, mom=102.1), R("IGV", "Software", "weak", dm=-0.5, ratio=100.4, mom=99.1),
            R("XBI", "Biotech", "lag", dm=0.1, ratio=98.2, mom=98.7), {"sym": "XLF", "name": "Financials", "err": "ไม่มีข้อมูล"}]


def rows_w():
    return [R("SMH", "Semiconductors", "lead", dm=0.2, date="2026-09-28"), R("XLU", "Utilities", "lag", dm=-0.2, date="2026-09-28"), R("IGV", "Software", "imp", dm=0.5, date="2026-09-28"),
            R("XBI", "Biotech", "weak", dm=0.1, date="2026-09-28"), R("XLF", "Financials", "lead", dm=0.4, date="2026-09-28")]


SEED_RRG = """([d, w, day])=>{ const f = ffState(); f.rrg = {rowsD: d, rowsW: w, build: RRG_BUILD, day: day || rrgToday(), at: new Date().toISOString(), loading:false, err:''}; f.rrgTf = 'D'; }"""


def launch(pw, w, h, mut=None, rrg=True):
    b, page, ce, pe = C.launch(pw, w, h, cards=False, mut=mut)
    if rrg: seed_rrg(page)
    return b, page, ce, pe


def seed_rrg(page, d=None, wk=None, day=None):
    js(page, SEED_RRG, [d if d is not None else rows_d(), wk if wk is not None else rows_w(), day])


def go_flow(page):
    js(page, "()=>{ switchTab('flow'); const f = ffState(); f.themesCol = false; f.themesColUser = true; ffRenderThemes(); }"); settle(page, 500)


def go_today(page):
    js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 600)


def notes(page): return js(page, "()=>JSON.parse(JSON.stringify(tdSettings().sectorNotes || null))")
def note(page, s): return (notes(page) or {}).get(s)
def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def cnt(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
def other_settings(page): return js(page, "()=>{ const s = JSON.parse(JSON.stringify(tdSettings())); delete s.sectorNotes; return s; }")
def stored_doc(page): return page.evaluate("()=>window.firebase.__mockDb.__getDoc(['users','testuid'])")
def sdsel(sym): return f'#ffThemes [data-rr="{sym}"]'
def expanded(page, sym): return js(page, "(s)=>{ const e=document.querySelector('#ffThemes [data-sd-hd=\"'+s+'\"]'); return e ? e.getAttribute('aria-expanded') : null; }", sym)


def fill_form(page, sym, driver="D", summary="E", revisit="R"):
    b = f'{sdsel(sym)} .sd-body'
    page.locator(f'{b} [data-sd-f="driver"]').fill(driver)
    page.locator(f'{b} [data-sd-f="summary"]').fill(summary)
    page.locator(f'{b} [data-sd-f="revisit"]').fill(revisit)


def open_row(page, sym):
    if expanded(page, sym) != "true": page.locator(f'{sdsel(sym)} .sd-hd .l2').first.click() if cnt(page, f'{sdsel(sym)} .l2') else page.locator(f'{sdsel(sym)} .sd-hd .sd-sum').click()
    settle(page, 250)


def save_btn(page, sym, mark=False):
    page.locator(f'{sdsel(sym)} [data-sd-{"mark" if mark else "save"}]').click(); settle(page, 900)


GOOD = {"schema": "sectorDrivers/v1", "sector_id": "SMH", "research_as_of": "2026-09-30", "driver": "Interpretation: AI capex lifted orders.",
        "evidence": {"summary": "Two firms raised guidance; one flagged slower China demand.", "sources": [{"title": "Company A call", "url": "https://example.com/a"}, {"title": "Company B 8-K", "url": "http://example.org/b"}]},
        "revisit_if": "Orders slow or guidance is cut.", "extra_key": 1}


def paste_check(page, obj_or_text):
    t = obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text, ensure_ascii=False)
    js(page, "(t)=>{ const e = document.getElementById('sdJson'); e.value = t; e.dispatchEvent(new Event('input')); }", t)
    page.locator("[data-sd-check]").click(); settle(page, 200)
    return {"err": txt(page, "[data-sd-err]") or "", "apply": js(page, "()=>{ const b=document.querySelector('[data-sd-apply]'); return !!b && b.style.display !== 'none'; }"), "prev": txt(page, "[data-sd-pv]")}


# ───────────────────────── 1 · Flow โครงสร้าง / ป้ายอังกฤษ / chip / เรียงลำดับ ─────────────────────────
def flow_structure(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        before = js(page, "()=>JSON.parse(JSON.stringify(ffState().rrg))")
        go_flow(page)
        check(f"{tag} 1 หัวมุมมอง lean = 'Leadership' (ไม่ใช่ เงินไหลเข้าธีมไหน)", txt(page, "#ffThemesTitle") == "Leadership", txt(page, "#ffThemesTitle"))
        order = js(page, "()=>[...document.querySelectorAll('#ffThemes .ln3-rr')].map(e=>e.dataset.rr)")
        check(f"{tag} 1 ลำดับแถวเดิม (ควอดแรนต์ lead→imp→weak→lag→err · Δmom) ไม่เปลี่ยน", order == ["XLU", "SMH", "IGV", "XBI", "XLF"], order)
        oracle = js(page, """()=>{ const O={lead:0,imp:1,weak:2,lag:3}; const rows = ffState().rrg.rowsD.slice().sort((a,b)=>{ if(a.err&&!b.err) return 1; if(!a.err&&b.err) return -1; if(a.err&&b.err) return a.sym.localeCompare(b.sym);
          if(O[a.quad]!==O[b.quad]) return O[a.quad]-O[b.quad]; const da=a.dMom==null?-Infinity:a.dMom, db=b.dMom==null?-Infinity:b.dMom; return (db-da)||(b.ratio-a.ratio); }).map(x=>x.sym);
          return JSON.stringify(rows)===JSON.stringify(rrgSortRows(ffState().rrg.rowsD).map(x=>x.sym)); }""")
        check(f"{tag} 1 rrgSortRows = ตัวเรียงเดิมทุกประการ (เทียบ oracle)", oracle is True)
        after = js(page, "()=>JSON.parse(JSON.stringify(ffState().rrg))")
        check(f"{tag} 1 ผลคำนวณ RRG (แถวในแคช) ไม่ถูกแก้โดยการวาด", before == after)
        check(f"{tag} 1 ทุกแถวมี ☆ (5 แถว) · ยังไม่ follow → ☆ · aria-pressed=false", cnt(page, "#ffThemes [data-sd-star]") == 5 and cnt(page, '#ffThemes [data-sd-star][aria-pressed="false"]') == 5 and txt(page, '[data-sd-star="SMH"]') == "☆")
        bx = page.locator('[data-sd-star="SMH"]').bounding_box()
        check(f"{tag} 1 ปุ่มดาว hit area ≥ 32px (กว้าง {bx['width']:.0f} × สูง {bx['height']:.0f})", bx["width"] >= 31.5 and bx["height"] >= 31.5, bx)
        check(f"{tag} 1 ค่าเริ่มต้นพับ: ไม่มี .sd-body · aria-expanded=false ทุกแถว", cnt(page, "#ffThemes .sd-body") == 0 and cnt(page, '#ffThemes [data-sd-hd][aria-expanded="false"]') == 5)
        check(f"{tag} 1 สรุปบรรทัดพับ = 'Drivers not yet recorded' (ไม่มีโน้ต)", "Drivers not yet recorded" in (txt(page, f'{sdsel("SMH")} [data-sd-sum]') or ""), txt(page, f'{sdsel("SMH")} [data-sd-sum]'))
        smh = txt(page, sdsel("SMH")) or ""
        check(f"{tag} 1 องค์ประกอบเดิมคงอยู่: IMPROVING · '4 d' · OFF52W -3.0% · Strength/Momentum · 2 เกจ", "IMPROVING" in smh and "4 d" in smh and "-3.0%" in smh and "Strength" in smh and "Momentum" in smh and cnt(page, f'{sdsel("SMH")} .rrgGaugeWrap') == 2, smh)
        ok_text = " ".join(js(page, "()=>[...document.querySelectorAll('#ffThemes .ln3-rr:not(.dim)')].map(e=>e.innerText)"))
        check(f"{tag} 1 ป้ายแถวที่คำนวณได้เป็นอังกฤษล้วน (ไม่มีอักษรไทย) · ไม่มีคำไทยของเกจ/Δ", not THAI.search(ok_text), THAI.findall(ok_text)[:5])
        lv = js(page, "()=>[...document.querySelectorAll('#ffThemes .rrgGaugeLbl')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")
        allowed = {"Very strong", "Strong", "Neutral", "Weak", "Very weak"}
        check(f"{tag} 1 ระดับ = Very strong/Strong/Neutral/Weak/Very weak · Δ = Flat/Moving/Fast/Very fast", all(any(s.startswith(a) for a in allowed) for s in lv) and all(re.search(r"(Flat|Moving|Fast|Very fast)", s) for s in lv), lv)
        check(f"{tag} 1 Δ ▲/▼ + สีเดิม (▲ teal / ▼ red)", js(page, "()=>{ const up=[...document.querySelectorAll('#ffThemes .rrgGaugeDelta')].filter(e=>e.innerText.startsWith('▲')); const dn=[...document.querySelectorAll('#ffThemes .rrgGaugeDelta')].filter(e=>e.innerText.startsWith('▼')); return up.length>0 && dn.length>0 && up.every(e=>e.style.color.includes('teal')) && dn.every(e=>e.style.color.includes('red')); }"))
        hint = txt(page, "#ffThemes .hint") or ""
        check(f"{tag} 1 legend/hint เป็นอังกฤษ (Flat/Moving/Fast · d · OFF52W)", not THAI.search(hint) and "Flat" in hint and "Moving" in hint and "OFF52W" in hint, hint)
        check(f"{tag} 1 footer บรรทัดเดียว: 'RRG shows relative price strength and momentum, not proof of fund inflows.'", txt(page, "[data-sd-foot]") == "RRG shows relative price strength and momentum, not proof of fund inflows." and cnt(page, "[data-sd-foot]") == 1, txt(page, "[data-sd-foot]"))
        chips = js(page, "()=>Object.fromEntries([...document.querySelectorAll('#ffThemes .ln3-rr')].map(e=>[e.dataset.rr, (e.querySelector('.sd-up')||{}).innerText||'']))")
        check(f"{tag} 1 ↗ chip: IMPROVING+Δ▲≥0.15 → 'momentum rising' · LEADING+Δ▲ → 'strong + rising' · WEAKENING/LAGGING/err ไม่มี", chips == {"XLU": "↗ strong + rising", "SMH": "↗ momentum rising", "IGV": "", "XBI": "", "XLF": ""}, chips)
        e = js(page, """()=>[sdChip({quad:'imp',dMom:0.15}), sdChip({quad:'imp',dMom:0.1499}), sdChip({quad:'lead',dMom:0.14}), sdChip({quad:'imp',dMom:-0.6}), sdChip({quad:'weak',dMom:0.9}), sdChip({quad:'lag',dMom:0.9}), sdChip({quad:'lead',dMom:null}), sdChip({err:'x',quad:'lead',dMom:1})].map(s=>s.replace(/<[^>]+>/g,''))""")
        check(f"{tag} 1 ↗ chip ขอบเขต |Δ| ≥ 0.15 (0.15 มี · 0.1499 ไม่มี · Δ▼ ไม่มี · err ไม่มี)", e == ["↗ momentum rising", "", "", "", "", "", "", ""], e)
        check(f"{tag} 1 แถว err: ยังโชว์ข้อความ error เดิม + ☆ + Drivers & evidence", "ไม่มีข้อมูล" in (txt(page, sdsel("XLF")) or "") and cnt(page, f'{sdsel("XLF")} [data-sd-star]') == 1 and cnt(page, f'{sdsel("XLF")} [data-sd-sum]') == 1)
        check(f"{tag} 1 ไม่ล้นแนวนอน ({overflow(page)})", overflow(page) <= 0)
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def flow_shots(pw, w, h, name):
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, """()=>{ const ago = n => new Date(Date.now() - n*864e5).toISOString();
          sdWrite('SMH', n=>{ n.follow=true; n.driver='Interpretation: AI capex lifted data-center orders; guidance raised by two large firms.'; n.evidence={summary:'Company A and B raised Q4 guidance; one supplier flagged slower China demand (contradiction).', sources:[{title:'Company A Q3 call', url:'https://example.com/a'},{title:'Company B 8-K', url:'https://example.com/b'}]}; n.revisit_if='Orders slow or companies cut guidance'; n.research_as_of='2026-09-29'; n.reviewed_at=ago(2); n.reviewed_phase='LEADING'; n.reviewed_tf='D'; return n; });
          sdWrite('XLU', n=>{ n.follow=true; return n; }); sdOpen['SMH']=true; }""")
        go_flow(page); C.shot(page, name, full=True)
    finally: b.close()


# ───────────────────────── 2 · Follow / unfollow ↔ Today ─────────────────────────
def follow_tests(pw):
    tag = f"[{ENGINE}/1280px]"
    b, page, ce, pe = launch(pw, 1280, 900)
    try:
        go_today(page)
        check(f"{tag} 2 ไม่มีใคร follow → Today มีบล็อก Sectors + 'No sectors followed — pick 1–3 in Flow ›'", txt(page, "[data-sd-tempty]") == "No sectors followed — pick 1–3 in Flow ›" and cnt(page, "[data-sd-trow]") == 0, txt(page, "[data-sd-today]"))
        check(f"{tag} 2 ยังไม่มี sectorNotes ในเอกสาร", notes(page) is None)
        base_other = other_settings(page)
        go_flow(page)
        page.locator('[data-sd-star="SMH"]').click(); settle(page, 700)
        n = note(page, "SMH")
        check(f"{tag} 2 กด ☆ → ★ (aria-pressed=true) · ไม่กางแถว (aria-expanded ยัง false)", txt(page, '[data-sd-star="SMH"]') == "★" and js(page, "()=>document.querySelector('[data-sd-star=\"SMH\"]').getAttribute('aria-pressed')") == "true" and expanded(page, "SMH") == "false")
        check(f"{tag} 2 สร้างโน้ตว่าง: follow=true · ฟิลด์อื่นว่าง · reviewed_* = null", n and n["follow"] is True and n["driver"] == "" and n["evidence"] == {"summary": "", "sources": []} and n["revisit_if"] == "" and n["reviewed_at"] is None and n["reviewed_phase"] is None and n["reviewed_tf"] is None and n["research_as_of"] is None, n)
        go_today(page)
        check(f"{tag} 2 Today แสดง SMH ทันทีโดยไม่มีโน้ต: 'Drivers not yet recorded.' · ไม่มี empty state", cnt(page, '[data-sd-trow="SMH"]') == 1 and "Drivers not yet recorded." in (txt(page, '[data-sd-trow="SMH"]') or "") and cnt(page, "[data-sd-tempty]") == 0, txt(page, "[data-sd-today]"))
        go_flow(page)
        open_row(page, "SMH"); fill_form(page, "SMH", "driver text", "evidence text", "revisit text"); save_btn(page, "SMH")
        page.locator('[data-sd-star="SMH"]').click(); settle(page, 600)   # unfollow
        n2 = note(page, "SMH")
        check(f"{tag} 2 Unfollow: follow=false · โน้ตยังอยู่ครบ (driver/evidence/revisit)", n2 and n2["follow"] is False and n2["driver"] == "driver text" and n2["evidence"]["summary"] == "evidence text" and n2["revisit_if"] == "revisit text", n2)
        go_today(page)
        check(f"{tag} 2 Unfollow → หายจาก Today ทันที + กลับเป็น empty state", cnt(page, '[data-sd-trow="SMH"]') == 0 and cnt(page, "[data-sd-tempty]") == 1)
        go_flow(page)
        page.locator('[data-sd-star="SMH"]').click(); settle(page, 600)
        n3 = note(page, "SMH")
        check(f"{tag} 2 Re-follow: โน้ตเดิมกลับมา (ไม่ถูกล้าง) · updated_at ไม่เปลี่ยนเพราะกดดาว", n3["follow"] is True and n3["driver"] == "driver text" and n3["updated_at"] == n2["updated_at"], [n3, n2["updated_at"]])
        check(f"{tag} 2 ค่าตั้งอื่นใน settings ไม่เปลี่ยนหลัง follow/save/unfollow (deep-compare ยกเว้น sectorNotes)", other_settings(page) == base_other, "differs")
        # กดดาวไม่แตะ reviewed baseline
        js(page, "()=>{ sdWrite('SMH', n=>{ n.reviewed_at = '2026-09-29T03:00:00.000Z'; n.reviewed_phase = 'LEADING'; n.reviewed_tf = 'D'; return n; }); }")
        before = note(page, "SMH")
        page.locator('[data-sd-star="SMH"]').click(); settle(page, 300); page.locator('[data-sd-star="SMH"]').click(); settle(page, 500)
        after = note(page, "SMH")
        check(f"{tag} 2 Follow/Unfollow ไม่รีเซ็ต review baseline (reviewed_* เดิม)", all(after[k] == before[k] for k in ("reviewed_at", "reviewed_phase", "reviewed_tf", "driver", "research_as_of")), [before, after])
        check(f"{tag} 2 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 3 · Save vs Save & mark reviewed · persistence ─────────────────────────
def save_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    saved = None
    try:
        go_flow(page)
        base_other = other_settings(page)
        open_row(page, "SMH")
        check(f"{tag} 3 แตะแถวกาง: aria-expanded=true · ฟอร์ม Driver/Evidence/Revisit if + 4 ปุ่ม", expanded(page, "SMH") == "true" and cnt(page, f'{sdsel("SMH")} .sd-body textarea') == 3 and cnt(page, f'{sdsel("SMH")} .sd-body [data-sd-f="revisit"]') == 1
              and all(cnt(page, f'{sdsel("SMH")} [data-sd-{k}]') == 1 for k in ("copy", "import", "save", "mark")))
        fill_form(page, "SMH", "AI capex lifted orders (ตีความ)", "Two firms raised guidance", "Orders slow")
        page.locator(f'{sdsel("SMH")} [data-sd-addsrc]').click(); settle(page, 200)
        page.locator(f'{sdsel("SMH")} [data-sd-f="stitle"]').fill("Company A call"); page.locator(f'{sdsel("SMH")} [data-sd-f="surl"]').fill("https://example.com/a")
        page.locator(f'{sdsel("SMH")} [data-sd-addok]').click(); settle(page, 250)
        check(f"{tag} 3 เพิ่มลิงก์ → chip (target=_blank rel=noopener) · ยังไม่บันทึกลงเอกสาร (แสดง unsaved)", js(page, "()=>{ const a=document.querySelector('#ffThemes [data-rr=\"SMH\"] .sd-lk a'); return !!a && a.target==='_blank' && /noopener/.test(a.rel) && a.getAttribute('href')==='https://example.com/a'; }") and note(page, "SMH") is None and "unsaved" in (txt(page, f'{sdsel("SMH")} [data-sd-meta]') or ""))
        page.locator(f'{sdsel("SMH")} [data-sd-addsrc]').click(); settle(page, 150)
        page.locator(f'{sdsel("SMH")} [data-sd-f="surl"]').fill("javascript:alert(1)"); page.locator(f'{sdsel("SMH")} [data-sd-addok]').click(); settle(page, 200)
        check(f"{tag} 3 เพิ่มลิงก์ javascript: → ปฏิเสธ + ข้อความ · ยัง 1 ลิงก์", cnt(page, f'{sdsel("SMH")} .sd-lk') == 1 and "http" in (txt(page, f'{sdsel("SMH")} [data-sd-msg]') or ""), txt(page, f'{sdsel("SMH")} [data-sd-msg]'))
        save_btn(page, "SMH")
        n = note(page, "SMH")
        check(f"{tag} 3 Save: บันทึกข้อความ + ลิงก์ · reviewed_* ยัง null · follow ไม่เปลี่ยน (false) · updated_at มี", n["driver"] == "AI capex lifted orders (ตีความ)" and n["evidence"]["summary"] == "Two firms raised guidance" and n["evidence"]["sources"] == [{"title": "Company A call", "url": "https://example.com/a"}] and n["revisit_if"] == "Orders slow"
              and n["reviewed_at"] is None and n["reviewed_phase"] is None and n["reviewed_tf"] is None and n["follow"] is False and n["updated_at"], n)
        check(f"{tag} 3 สรุปพับหลัง Save (ยังไม่รีวิว): 'Not yet reviewed' · ไม่มีแท็ก", "Not yet reviewed" in (txt(page, f'{sdsel("SMH")} [data-sd-sum]') or "") and cnt(page, f'{sdsel("SMH")} [data-sd-flag]') == 0, txt(page, f'{sdsel("SMH")} [data-sd-sum]'))
        save_btn(page, "SMH", mark=True)
        n = note(page, "SMH")
        check(f"{tag} 3 Save & mark reviewed: reviewed_at (ISO) + reviewed_phase=IMPROVING + reviewed_tf=D", n["reviewed_phase"] == "IMPROVING" and n["reviewed_tf"] == "D" and re.match(r"^\d{4}-\d\d-\d\dT", n["reviewed_at"] or ""), n)
        meta = txt(page, f'{sdsel("SMH")} [data-sd-meta]') or ""
        check(f"{tag} 3 meta แยกวัน AI กับวันรีวิว: 'AI research as of — · reviewed by you <d MMM>'", "AI research as of —" in meta and "reviewed by you" in meta and "not yet" not in meta, meta)
        base = dict(n)
        fill_form(page, "SMH", "edited later", "edited evidence", "edited revisit"); save_btn(page, "SMH")
        n2 = note(page, "SMH")
        check(f"{tag} 3 แก้ข้อความ + Save ธรรมดา: reviewed_at/phase/tf เดิมเป๊ะ (ไม่รีเซ็ต baseline) · ข้อความใหม่", n2["driver"] == "edited later" and all(n2[k] == base[k] for k in ("reviewed_at", "reviewed_phase", "reviewed_tf")), [base, n2])
        js(page, "()=>{ const f = ffState(); f.rrg.rowsD.find(x=>x.sym==='SMH').quad = 'weak'; ffRenderThemes(); }"); settle(page, 300)
        fill_form(page, "SMH", "edited again", "e2", "r2"); save_btn(page, "SMH", mark=True)
        n3 = note(page, "SMH")
        check(f"{tag} 3 Save & mark อีกครั้ง (เฟสตอนนี้ WEAKENING): baseline ใหม่ = WEAKENING / D · reviewed_at ใหม่กว่า", n3["reviewed_phase"] == "WEAKENING" and n3["reviewed_tf"] == "D" and n3["reviewed_at"] >= n2["reviewed_at"], n3)
        check(f"{tag} 3 ค่าตั้งอื่นใน settings ไม่เปลี่ยน (deep-compare ยกเว้น sectorNotes)", other_settings(page) == base_other)
        doc = stored_doc(page); sv = doc["books"]["main"]["settings"]
        check(f"{tag} 3 เขียนลงเอกสาร users/{{uid}} จริง: books.main.settings.sectorNotes.SMH (ไม่มี collection ใหม่)", sv.get("sectorNotes", {}).get("SMH", {}).get("driver") == "edited again" and "sectorNotes" not in doc and "sectorNotes" not in doc["books"]["main"], list(sv.keys())[:12])
        saved = doc
        # ข้อความไทย + ปกติเว้นช่อง
        fill_form(page, "SMH", "ไทย " * 90, "หลักฐานภาษาไทย", "เงื่อนไขภาษาไทย"); save_btn(page, "SMH")
        check(f"{tag} 3 ข้อความไทยได้ (นับตัวอักษร ไม่ใช่ไบต์: ไทย 360 ตัวผ่านเพดาน 400)", "ไทย" in (note(page, "SMH")["driver"]) and len(note(page, "SMH")["driver"]) == 360)
        over = "x" * 1201
        js(page, "(s)=>{ sdIn('SMH','driver', s); }", over); before_over = json.dumps(note(page, "SMH"), sort_keys=True)
        page.locator(f'{sdsel("SMH")} [data-sd-save]').click(); settle(page, 500)
        check(f"{tag} 3 Driver เกิน 400 ตัว → ไม่บันทึก + ข้อความ · โน้ตเดิมไม่เปลี่ยน", json.dumps(note(page, "SMH"), sort_keys=True) == before_over and "1200" in (txt(page, f'{sdsel("SMH")} [data-sd-msg]') or ""), txt(page, f'{sdsel("SMH")} [data-sd-msg]'))   # TD4a: เพดาน 400 → 1200
        check(f"{tag} 3 ไม่ล้นแนวนอนตอนฟอร์มกาง ({overflow(page)})", overflow(page) <= 0)
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()
    # reload: เอกสารที่เขียนไว้ → หน้าใหม่ → ยังอยู่
    if saved:
        sn = saved["books"]["main"]["settings"]["sectorNotes"]

        def mut(doc): doc["books"]["main"]["settings"]["sectorNotes"] = copy.deepcopy(sn)
        b2, page2, ce2, pe2 = launch(pw, 390, 844, mut=mut)
        try:
            go_flow(page2)
            check(f"{tag} 3 Reload: โน้ต SMH ยังอยู่ (driver · reviewed_phase) · เปิดแถวเห็นข้อความ", (note(page2, "SMH") or {}).get("reviewed_phase") == "WEAKENING" and (note(page2, "SMH") or {}).get("driver") == sn["SMH"]["driver"])
            open_row(page2, "SMH")
            check(f"{tag} 3 Reload: ฟอร์มโหลดข้อความที่บันทึกไว้", js(page2, "()=>document.querySelector('#ffThemes [data-rr=\"SMH\"] [data-sd-f=\"revisit\"]').value") == sn["SMH"]["revisit_if"])
        finally: b2.close()


# ───────────────────────── 4 · ธง Revisit · phase changed ─────────────────────────
def flag_tests(pw):
    tag = f"[{ENGINE}/1280px]"
    b, page, ce, pe = launch(pw, 1280, 900)
    try:
        def setn(phase, tf, at="2026-09-29T03:00:00.000Z"):
            js(page, "([p,t,a])=>{ sdWrite('SMH', n=>{ n.follow = true; n.driver = 'drv'; n.reviewed_at = a; n.reviewed_phase = p; n.reviewed_tf = t; return n; }); ffRenderThemes(); todayRefresh(true); }", [phase, tf, at])
            settle(page, 300)
        def flag(): return js(page, "()=>({flow: document.querySelectorAll('#ffThemes [data-rr=\"SMH\"] [data-sd-flag]').length, today: document.querySelectorAll('[data-sd-trow=\"SMH\"] [data-sd-flag]').length})")
        go_flow(page)
        setn("LEADING", "D")
        check(f"{tag} 4 reviewed LEADING (D) → ตอนนี้ IMPROVING (D) → แท็ก 'Revisit · phase changed' ทั้ง Flow และ Today", flag() == {"flow": 1, "today": 1} and "Revisit · phase changed" in (txt(page, f'{sdsel("SMH")} [data-sd-sum]') or ""), flag())
        setn("IMPROVING", "D")
        check(f"{tag} 4 เฟสเดิม (IMPROVING = IMPROVING) → ไม่มีแท็ก", flag() == {"flow": 0, "today": 0}, flag())
        setn("LEADING", "W")
        check(f"{tag} 4 reviewed LEADING (W) ตอนนี้ W = LEADING (SMH ในแคช W) → ไม่มีแท็ก", flag() == {"flow": 0, "today": 0}, flag())
        setn("IMPROVING", "W")
        check(f"{tag} 4 reviewed IMPROVING (W) ตอนนี้ W = LEADING → แท็ก (เทียบข้อมูล W)", flag()["flow"] == 1, flag())
        js(page, "()=>{ rrgSetTf('W'); }"); settle(page, 300)
        setn("LEADING", "D")   # reviewed D · หน้ากำลังดู W (W: LEADING เท่าเดิมแต่ D: IMPROVING)
        check(f"{tag} 4 หน้ากำลังดู W แต่ reviewed tf = D → เทียบข้อมูล D เท่านั้น (D ปัจจุบัน IMPROVING ≠ LEADING → แท็ก) ไม่ใช้ W มาเทียบ", flag()["flow"] == 1 and flag()["today"] == 1, flag())
        setn("IMPROVING", "D")
        check(f"{tag} 4 reviewed IMPROVING (D) · หน้าดู W (W ต่างเฟส) → ไม่มีแท็ก (ไม่เทียบข้าม tf)", flag() == {"flow": 0, "today": 0}, flag())
        js(page, "()=>{ ffState().rrgTf = 'D'; ffRenderThemes(); }")
        setn("LEADING", "D")
        # แถว err
        seed_rrg(page, d=[R("SMH", "Semiconductors", "imp")] and [{"sym": "SMH", "name": "Semiconductors", "err": "ไม่มีข้อมูล"}] + rows_d()[1:], wk=rows_w()); js(page, "()=>{ ffRenderThemes(); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} 4 แถว SMH เป็น err (ข้อมูลหาย) → ไม่มีแท็ก · Today เฟส '—'", flag() == {"flow": 0, "today": 0} and "—" in (txt(page, '[data-sd-trow="SMH"] [data-sd-phase]') or ""), [flag(), txt(page, '[data-sd-trow="SMH"] [data-sd-phase]')])
        # ข้อมูล tf ของที่รีวิวไม่มี
        seed_rrg(page, d=rows_d(), wk=[]); js(page, "()=>{ ffRenderThemes(); todayRefresh(true); }"); settle(page, 300)
        setn("LEADING", "W")
        check(f"{tag} 4 reviewed W แต่แคช W ว่าง → ไม่มีแท็ก", flag() == {"flow": 0, "today": 0}, flag())
        # แคชเก่า
        seed_rrg(page, day="2026-09-20"); setn("LEADING", "D"); js(page, "()=>{ ffRenderThemes(); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} 4 แคช RRG เก่า (คนละวัน) → ไม่มีแท็ก · Today ยังโชว์เฟสล่าสุด + 'as of' (TD4c)", flag() == {"flow": 0, "today": 0} and "IMPROVING" in (txt(page, '[data-sd-trow="SMH"] [data-sd-phase]') or "") and "as of" in (txt(page, "[data-sd-asof]") or ""), flag())
        # ไม่มีแคช/ไม่มี key
        js(page, "()=>{ ffState().rrg = {err:'nokey', at:''}; ffRenderThemes(); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} 4 ไม่มีแคช RRG เลย (nokey) → ไม่มีแท็ก ไม่ error", flag() == {"flow": 0, "today": 0})
        # รีวิวตอนไม่มีข้อมูลสด (แคชเก่า — แถวยังโชว์) → reviewed_phase null และไม่เคยแท็ก
        seed_rrg(page, day="2026-09-20"); js(page, "()=>{ sdWrite('SMH', n=>{ n.reviewed_at=null; n.reviewed_phase=null; n.reviewed_tf=null; return n; }); ffRenderThemes(); }"); settle(page, 200)
        open_row(page, "SMH"); save_btn(page, "SMH", mark=True)
        n = note(page, "SMH")
        check(f"{tag} 4 Save & mark reviewed ตอนแคช RRG เก่า → reviewed_phase/tf = null (ไม่แต่งเฟส) · reviewed_at มี", n["reviewed_phase"] is None and n["reviewed_tf"] is None and n["reviewed_at"], n)
        check(f"{tag} 4 สรุป: 'Reviewed <d> · phase not recorded'", "phase not recorded" in (txt(page, f'{sdsel("SMH")} [data-sd-sum]') or ""), txt(page, f'{sdsel("SMH")} [data-sd-sum]'))
        js(page, "()=>{ sdWrite('SMH', n=>{ n.reviewed_at=null; n.reviewed_phase=null; n.reviewed_tf=null; return n; }); ffState().rrg = {err:'nokey', at:''}; sdDraftOf('SMH'); }")
        js(page, "()=>sdSave('SMH', true)"); settle(page, 500)
        n = note(page, "SMH")
        check(f"{tag} 4 Save & mark reviewed ตอนไม่มีแคช RRG เลย → reviewed_phase/tf = null", n["reviewed_phase"] is None and n["reviewed_tf"] is None and n["reviewed_at"], n)
        seed_rrg(page); js(page, "()=>{ ffRenderThemes(); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} 4 พอข้อมูลกลับมา ก็ไม่เคยแท็ก (ไม่มีเฟสอ้างอิง)", flag() == {"flow": 0, "today": 0}, flag())
        # follow ใหม่ ไม่เคยรีวิว → ไม่แท็ก
        js(page, "()=>{ sdWrite('XLU', n=>{ n.follow = true; return n; }); ffRenderThemes(); todayRefresh(true); }"); settle(page, 300)
        check(f"{tag} 4 follow ใหม่ที่ยังไม่เคยรีวิว (XLU) → ไม่มีแท็ก", js(page, "()=>document.querySelectorAll('[data-sd-trow=\"XLU\"] [data-sd-flag], #ffThemes [data-rr=\"XLU\"] [data-sd-flag]').length") == 0)
        check(f"{tag} 4 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 5 · Copy AI prompt ─────────────────────────
def prompt_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        go_flow(page); open_row(page, "SMH")
        page.locator(f'{sdsel("SMH")} [data-sd-copy]').click(); settle(page, 300)
        p = js(page, "()=>window.__sdLastPrompt || ''")
        for k, v in (("sector id", "Sector ID: SMH"), ("ชื่อ", "Semiconductors"), ("ETF/benchmark", "against SPY"), ("เฟส+tf+วันข้อมูล", "IMPROVING (Daily RRG, data as of 2026-09-30)"),
                     ("คำถามตรงตัว", "What supports this sector's relative strength, what evidence supports or contradicts that explanation, and what would invalidate it?"),
                     ("research current sources", "Research current sources"), ("facts vs interpretation", "Distinguish facts from interpretation"), ("price ≠ inflows", "Do not assume price strength proves fund inflows"),
                     ("Evidence insufficient", "Evidence insufficient"), ("JSON schema", '"schema": "sectorDrivers/v1"'), ("sector_id ใน template", '"sector_id": "SMH"'), ("Return only", "Return only the JSON")):
            check(f"{tag} 5 prompt มี {k}", v in p, p[:200])
        m = re.search(r"\{\n\s+\"schema\".*\}$", p, re.S)
        tpl = json.loads(m.group(0)) if m else None
        check(f"{tag} 5 template JSON ใน prompt ถูกต้อง (parse ได้ · ครบฟิลด์ · ≤ 3 sources)", tpl and set(tpl) >= {"schema", "sector_id", "research_as_of", "driver", "evidence", "revisit_if"} and set(tpl["evidence"]) == {"summary", "sources"}, tpl)
        check(f"{tag} 5 toast 'Prompt copied'", (txt(page, "#sdToast") or "") == "Prompt copied" and js(page, "()=>document.getElementById('sdToast').classList.contains('show')"), txt(page, "#sdToast"))
        js(page, "()=>{ ffState().rrgTf='W'; }"); page.locator(f'{sdsel("SMH")} [data-sd-copy]').click(); settle(page, 200)
        p2 = js(page, "()=>window.__sdLastPrompt")
        check(f"{tag} 5 tf Weekly → 'LEADING (Weekly RRG, data as of 2026-09-28)'", "LEADING (Weekly RRG, data as of 2026-09-28)" in p2, p2[:300])
        js(page, "()=>{ ffState().rrg = {err:'nokey', at:''}; }"); page.locator(f'{sdsel("SMH")} [data-sd-copy]').click() if cnt(page, f'{sdsel("SMH")} [data-sd-copy]') else js(page, "()=>sdCopyPrompt('SMH')"); settle(page, 200)
        p3 = js(page, "()=>window.__sdLastPrompt")
        check(f"{tag} 5 ไม่มีข้อมูล RRG → 'RRG data unavailable' (ไม่แต่งเฟส)", "RRG data unavailable" in p3 and "LEADING" not in p3.split("Question:")[0] and "IMPROVING" not in p3.split("Question:")[0], p3[:300])
        check(f"{tag} 5 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 6 · Import answer ─────────────────────────
def import_tests(pw, shot=None):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        go_flow(page); open_row(page, "SMH")
        fill_form(page, "SMH", "keep driver", "keep evidence", "keep revisit"); save_btn(page, "SMH")
        base_note = json.dumps(note(page, "SMH"), sort_keys=True); base_doc = json.dumps(stored_doc(page)["books"]["main"]["settings"], sort_keys=True)
        page.locator(f'{sdsel("SMH")} [data-sd-import]').click(); settle(page, 300)
        check(f"{tag} 6 Import answer เปิด dialog (ใช้ overlay เดิม) หัว 'Import answer · SMH'", js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')") and "Import answer · SMH" in (txt(page, "[data-sd-imp-h]") or ""))
        bad = [("JSON เสีย", "{not json"), ("schema ผิด", {**GOOD, "schema": "sectorDrivers/v2"}), ("sector_id ผิด", {**GOOD, "sector_id": "KBE"}), ("sector_id ไม่ใช่ string", {**GOOD, "sector_id": 5}),
               ("4 sources", {**GOOD, "evidence": {"summary": "s", "sources": [{"title": "t", "url": f"https://e.com/{i}"} for i in range(4)]}}),
               ("url javascript:", {**GOOD, "evidence": {"summary": "s", "sources": [{"title": "t", "url": "javascript:alert(1)"}]}}),
               ("url ftp:", {**GOOD, "evidence": {"summary": "s", "sources": [{"title": "t", "url": "ftp://e.com/x"}]}}),
               ("url ไม่ใช่ URL", {**GOOD, "evidence": {"summary": "s", "sources": [{"title": "t", "url": "not a url"}]}}),
               ("url เกิน 500", {**GOOD, "evidence": {"summary": "s", "sources": [{"title": "t", "url": "https://e.com/" + "a" * 500}]}}),
               ("title เกิน 120", {**GOOD, "evidence": {"summary": "s", "sources": [{"title": "t" * 121, "url": "https://e.com/x"}]}}),
               ("source ไม่ใช่ object", {**GOOD, "evidence": {"summary": "s", "sources": ["https://e.com/x"]}}),
               ("sources ไม่ใช่ array", {**GOOD, "evidence": {"summary": "s", "sources": "x"}}),
               ("วันอนาคต", {**GOOD, "research_as_of": "2026-10-02"}), ("วันที่ผิดรูป", {**GOOD, "research_as_of": "26/09/2026"}), ("วันที่ไม่มีจริง", {**GOOD, "research_as_of": "2026-02-30"}),
               ("driver เกิน 1200", {**GOOD, "driver": "d" * 1201}), ("summary เกิน 2000", {**GOOD, "evidence": {"summary": "s" * 2001, "sources": []}}), ("revisit เกิน 600", {**GOOD, "revisit_if": "r" * 601}),   # TD4a: เพดานใหม่
               ("driver ไม่ใช่ string", {**GOOD, "driver": ["x"]}), ("ไม่มี evidence", {k: v for k, v in GOOD.items() if k != "evidence"}), ("revisit_if หาย", {k: v for k, v in GOOD.items() if k != "revisit_if"}), ("array", [GOOD])]
        for nm, o in bad:
            r = paste_check(page, o)
            same = json.dumps(note(page, "SMH"), sort_keys=True) == base_note
            check(f"{tag} 6 import ไม่ถูกต้อง ({nm}) → error + ไม่มีปุ่ม Apply + โน้ตเดิมเป๊ะ", bool(r["err"]) and not r["apply"] and same and r["prev"] is None, r)
        check(f"{tag} 6 หลังพยายาม import ผิดทั้งหมด เอกสารที่เก็บ (settings) เหมือนเดิมทุกไบต์", json.dumps(stored_doc(page)["books"]["main"]["settings"], sort_keys=True) == base_doc)
        r = paste_check(page, {**GOOD, "sector_id": "KBE"})
        check(f"{tag} 6 ข้อความ error ชี้ชัด: 'sector_id is KBE, this row is SMH — nothing changed'", "sector_id is KBE, this row is SMH" in r["err"] and "nothing changed" in r["err"], r)
        r = paste_check(page, "```json\n" + json.dumps(GOOD) + "\n```")
        check(f"{tag} 6 import ถูกต้อง (ล้อม ```json ได้ · มี key เกินถูกข้าม) → preview 3 ฟิลด์ + ปุ่ม Apply", not r["err"] and r["apply"] and "Driver" in r["prev"] and "Evidence" in r["prev"] and "Revisit if" in r["prev"] and "2 sources" in r["prev"], r)
        check(f"{tag} 6 ยังไม่ Apply → โน้ตที่เก็บไม่เปลี่ยน", json.dumps(note(page, "SMH"), sort_keys=True) == base_note)
        if shot: C.shot(page, shot)
        r = paste_check(page, {**GOOD, "sector_id": "smh", "driver": "ไทย" * 100})
        check(f"{tag} 6 sector_id ตัวพิมพ์เล็ก (smh) ผ่าน · driver ภาษาไทย 300 ตัวผ่าน", not r["err"] and r["apply"], r)
        r = paste_check(page, GOOD)
        page.locator("[data-sd-apply]").click(); settle(page, 400)
        check(f"{tag} 6 Apply to form: dialog ปิด · ฟอร์มถูกเติม (driver/evidence/revisit/2 ลิงก์) · meta 'AI research as of 30 Sep' · แสดง unsaved", not js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')")
              and js(page, "()=>document.querySelector('#ffThemes [data-rr=\"SMH\"] [data-sd-f=\"driver\"]').value") == GOOD["driver"] and cnt(page, f'{sdsel("SMH")} .sd-lk') == 2
              and "AI research as of 30 Sep" in (txt(page, f'{sdsel("SMH")} [data-sd-meta]') or "") and "unsaved" in (txt(page, f'{sdsel("SMH")} [data-sd-meta]') or ""), txt(page, f'{sdsel("SMH")} [data-sd-meta]'))
        check(f"{tag} 6 Apply ไม่บันทึกเอง: โน้ตที่เก็บยังเดิม", json.dumps(note(page, "SMH"), sort_keys=True) == base_note)
        page.locator(f'{sdsel("SMH")} [data-sd-f="revisit"]').fill("manual edit after import")   # แก้เองหลัง import ได้
        save_btn(page, "SMH")
        n = note(page, "SMH")
        check(f"{tag} 6 แก้เองหลัง import แล้ว Save: เก็บ research_as_of แยกจากวันรีวิว · reviewed_at ยัง null (ไม่ใช่ mark) · sources 2", n["research_as_of"] == "2026-09-30" and n["revisit_if"] == "manual edit after import" and n["driver"] == GOOD["driver"] and len(n["evidence"]["sources"]) == 2 and n["reviewed_at"] is None, n)
        check(f"{tag} 6 ไม่ล้นแนวนอน ({overflow(page)}) · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 7 · Today block ─────────────────────────
def today_tests(pw, w, h, label, shot=None):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        long_drv = "ก" * 100
        js(page, """(drv)=>{ const ago = n => new Date(Date.now() - n*864e5).toISOString();
          sdWrite('SMH', n=>{ n.follow=true; n.driver='Guidance up on data-center orders and a very long explanation that continues beyond eighty characters for sure'; n.evidence={summary:'ev', sources:[]}; n.reviewed_at=ago(3); n.reviewed_phase='LEADING'; n.reviewed_tf='D'; return n; });
          sdWrite('XLU', n=>{ n.follow=true; n.driver='Utility driver'; return n; });
          sdWrite('IGV', n=>{ n.follow=true; return n; });
          sdWrite('ZZZ', n=>{ n.follow=true; n.driver='gone sector'; return n; });
          sdWrite('XBI', n=>{ n.driver='not followed'; return n; }); }""", long_drv)
        go_today(page)
        rows = js(page, "()=>[...document.querySelectorAll('[data-sd-trow]')].map(e=>e.dataset.sdTrow)")
        check(f"{tag} 7 Today แสดงเฉพาะ sector ที่ follow (XLU, SMH, IGV) ตามลำดับ Flow · XBI (ไม่ follow) และ ZZZ (ไม่อยู่ในรายการ RRG) ไม่แสดง", rows == ["XLU", "SMH", "IGV"], rows)
        check(f"{tag} 7 ZZZ ถูกซ่อนแต่โน้ตยังอยู่ในเอกสาร (ไม่ลบ)", (note(page, "ZZZ") or {}).get("driver") == "gone sector")
        t = txt(page, '[data-sd-trow="SMH"]') or ""
        check(f"{tag} 7 แถว SMH: ชื่อ · เฟส Improving · Δ (▲) · ↗ chip · แท็ก 'Revisit · phase changed' · driver ตัด ~80 ตัว (…) · 'Reviewed 3d ago'", "SMH" in t and "Semiconductors" in t and "IMPROVING · 4 d" in t and "↗ momentum rising" in t and "Revisit · phase changed" in t and "Reviewed 3d ago" in t, t)   # TD4a: เฟสตัวพิมพ์ใหญ่ + วัน + OFF52W ต่อท้ายชื่อ · driver เต็ม (พับ 1 บรรทัดด้วย CSS)
        dl = js(page, "()=>document.querySelector('[data-sd-trow=\"SMH\"] [data-sd-tline]').innerText")
        check(f"{tag} 7 driver บนแถว Today ≤ 80 ตัว + …", len(dl.split(" · ")[0]) > 80 and js(page, "()=>getComputedStyle(document.querySelector('[data-sd-trow=\"SMH\"] [data-sd-tline]')).whiteSpace") == "nowrap", dl)   # TD4a: แสดงข้อความเต็ม พับเป็น 1 บรรทัด (ellipsis) แตะ = ขยาย
        ph = js(page, "()=>getComputedStyle(document.querySelector('[data-sd-trow=\"SMH\"] [data-sd-phase]')).color")
        check(f"{tag} 7 สีเฟสตามควอดแรนต์ (IMPROVING = blue) ไม่ใช่สี muted", ph != js(page, "()=>getComputedStyle(document.querySelector('[data-sd-trow=\"IGV\"] [data-sd-phase]')).color"), ph)
        check(f"{tag} 7 ไม่มีโน้ต (IGV) → 'Drivers not yet recorded.' · XLU ไม่เคยรีวิว → 'Not yet reviewed' ไม่โชว์ · ไม่มีแท็ก", "Drivers not yet recorded." in (txt(page, '[data-sd-trow="IGV"]') or "") and cnt(page, '[data-sd-trow="IGV"] [data-sd-flag], [data-sd-trow="XLU"] [data-sd-flag]') == 0)
        check(f"{tag} 7 มี driver แต่ไม่มี evidence (XLU) → 'Supporting evidence not yet recorded.' · SMH มี evidence → ไม่มีบรรทัดนี้", cnt(page, '[data-sd-trow="XLU"] [data-sd-tev]') == 1 and cnt(page, '[data-sd-trow="SMH"] [data-sd-tev]') == 0)
        blk = js(page, """()=>{ const b=document.querySelector('[data-sd-today]'); const c2=document.querySelector('[data-td-col="2"]'); const g=document.querySelector('[data-gl-goal]'); const top=document.querySelector('[data-td-goaltop]');
          return {inCol2: !!c2 && c2.contains(b), afterGoal: !!g && g.nextElementSibling===b, afterGoalTop: !!top && top.nextElementSibling===b, idx: [...b.parentNode.children].indexOf(b), mac: ln3Mac()}; }""")
        if w >= 1000:
            check(f"{tag} 7 Mac: บล็อก Sectors อยู่ใน panel Overview (TD3a)", js(page, "()=>{ const b=document.querySelector('[data-sd-today]'); const p=document.querySelector('.td3-pn'); return !!p && p.firstElementChild.contains(b); }"), blk)   # TD3a: Sectors อยู่ใน panel Overview (ซ้ายสุด)
        else:
            check(f"{tag} 7 iPhone: บล็อก Sectors ต่อจากบรรทัดเป้าหมาย Port (หรือบนสุดถ้าไม่มีเป้า)", blk["afterGoalTop"] or blk["idx"] <= 3, blk)
        check(f"{tag} 7 tdSectorsHtml() เป็นฟังก์ชันเดียว (TD3a ย้ายได้) คืน HTML บล็อกเดียว", js(page, "()=>(tdSectorsHtml().match(/data-sd-today/g)||[]).length") == 1)
        ow = overflow(page)
        check(f"{tag} 7 ไม่ล้นแนวนอน ({ow})", ow <= 0)
        if shot: C.shot(page, shot, full=True)
        # แตะแถว → Flow, RRG เปิด, แถวนั้นกาง และอยู่ในจอ
        page.locator('[data-sd-trow="SMH"]').click(); settle(page, 800)
        st = js(page, """()=>{ const e=document.querySelector('#ffThemes [data-rr="SMH"]'); const r=e?e.getBoundingClientRect():null; return {tab: activeTab, exp: expanded_(), body: !!(e && e.querySelector('.sd-body')), vis: !!r && r.top < innerHeight && r.bottom > 0, rrgOpen: document.getElementById('ffThemesBody').style.display !== 'none'}; function expanded_(){ const h=document.querySelector('#ffThemes [data-sd-hd="SMH"]'); return h && h.getAttribute('aria-expanded'); } }""")
        check(f"{tag} 7 แตะแถว Today → ไปแท็บ Flow · RRG เปิด · แถว SMH กางและอยู่ในจอ", st["tab"] == "flow" and st["exp"] == "true" and st["body"] and st["vis"] and st["rrgOpen"], st)
        # empty-state แตะ → Flow
        js(page, "()=>{ ['SMH','XLU','IGV','ZZZ'].forEach(s=>sdWrite(s, n=>{ n.follow=false; return n; })); }"); go_today(page)
        page.locator("[data-sd-tempty]").click(); settle(page, 500)
        check(f"{tag} 7 แตะ empty state → ไปแท็บ Flow", js(page, "()=>activeTab") == "flow")
        check(f"{tag} 7 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 8 · Weekend task ─────────────────────────
def weekend_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        t = js(page, "()=>glWeekTasks().find(x=>x.id==='wsector')")
        check(f"{tag} 8 งาน Weekly 'Review drivers for selected sectors' อยู่ในรายการเริ่มต้น (กดเอง · auto=null)", t and t["name"] == "Review drivers for selected sectors" and t["auto"] is None and t["on"] is True, t)
        js(page, "()=>{ sdWrite('SMH', n=>{ n.follow=true; n.driver='drv'; n.reviewed_at=new Date().toISOString(); n.reviewed_phase='IMPROVING'; n.reviewed_tf='D'; return n; }); glSetTab('w'); }"); go_today(page)
        row = js(page, "()=>{ const r=document.querySelector('[data-gl-wrow=\"wsector\"]'); return r ? {done: r.dataset.done, txt: r.innerText.replace(/\\s+/g,' ').trim(), tick: !!r.querySelector('[data-gl-wtick]'), auto: !!r.querySelector('[data-gl-wauto]')} : null; }")
        check(f"{tag} 8 แถวมีช่องติ๊กกดเอง · ไม่ auto · ยังไม่ติ๊กแม้มีโน้ต+รีวิวแล้ว (ไม่ auto-complete)", row and row["tick"] and not row["auto"] and row["done"] == "false", row)
        check(f"{tag} 8 ไม่มีตัวนับ (ไม่มี n/N ในแถว) — มีแค่ 'กดเอง' + ปุ่ม Flow ›", row and not re.search(r"\d+\s*/\s*\d+", row["txt"]) and "Flow ›" in row["txt"] and "กดเอง" in row["txt"], row)
        page.locator('[data-gl-wtick="wsector"]').click(); settle(page, 500)
        check(f"{tag} 8 ติ๊กเองได้ → done", js(page, "()=>document.querySelector('[data-gl-wrow=\"wsector\"]').dataset.done") == "true")
        page.locator('[data-sd-wlink]').click(); settle(page, 600)
        check(f"{tag} 8 ลิงก์ Flow › → แท็บ Flow · RRG panel เปิด", js(page, "()=>activeTab") == "flow" and js(page, "()=>document.getElementById('ffThemesBody').style.display !== 'none'"))
        # ความยาวชื่อ: ชื่อเริ่มต้น 35 ตัวไม่ถูกตัด แม้เก็บเป็นรายการที่กำหนดเอง · ชื่ออื่นเกิน 30 ยังตัด
        r = js(page, """()=>{ const def = GL_WEEK_DEF.map(x=>({...x})); const long = 'x'.repeat(40);
          glWrite(S=>{ S.weekTasks = def.concat([{id:'wlong', name:long, auto:null, on:true}]); }); const w = glWeekTasks(); return {sector: w.find(x=>x.id==='wsector').name, long: w.find(x=>x.id==='wlong').name.length}; }""")
        check(f"{tag} 8 ชื่อเริ่มต้น 35 ตัวไม่ถูกตัดเมื่อเก็บในรายการ · ชื่อกำหนดเองยาว 40 ถูกตัดเหลือ 30 (กติกาเดิม)", r["sector"] == "Review drivers for selected sectors" and r["long"] == 30, r)
        check(f"{tag} 8 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 9 · คีย์บอร์ด / ทั้งแถวแตะได้ / stopPropagation ─────────────────────────
def interact_tests(pw):
    tag = f"[{ENGINE}/1280px]"
    b, page, ce, pe = launch(pw, 1280, 900)
    try:
        go_flow(page)
        hd = page.locator('[data-sd-hd="IGV"]')
        check(f"{tag} 9 แถวโฟกัสได้ (tabindex=0) · role=button · cursor pointer", js(page, "()=>{ const e=document.querySelector('[data-sd-hd=\"IGV\"]'); return e.tabIndex===0 && e.getAttribute('role')==='button' && getComputedStyle(e).cursor==='pointer'; }"))
        hd.focus(); page.keyboard.press("Enter"); settle(page, 250)
        check(f"{tag} 9 Enter บนแถว → กาง (aria-expanded=true) · โฟกัสยังอยู่ที่แถว", expanded(page, "IGV") == "true" and js(page, "()=>document.activeElement.getAttribute('data-sd-hd')") == "IGV")
        page.keyboard.press("Space"); settle(page, 250)
        check(f"{tag} 9 Space → พับ", expanded(page, "IGV") == "false")
        page.locator('[data-sd-hd="IGV"] .l2 .g').first.click(); settle(page, 250)
        check(f"{tag} 9 แตะตรงเกจ (ส่วนไหนของแถวก็ได้) → กาง", expanded(page, "IGV") == "true")
        page.locator('[data-sd-hd="IGV"] .l1 .sub').first.click(); settle(page, 250)
        check(f"{tag} 9 แตะชื่อ sector → พับ", expanded(page, "IGV") == "false")
        page.locator('[data-sd-hd="IGV"]').click(); settle(page, 250)
        page.locator(f'{sdsel("IGV")} [data-sd-f="driver"]').click(); page.locator(f'{sdsel("IGV")} [data-sd-f="driver"]').fill("typing"); page.locator(f'{sdsel("IGV")} .sd-fl').first.click(); page.locator(f'{sdsel("IGV")} .sd-meta').click(); settle(page, 250)
        check(f"{tag} 9 คลิก textarea/ป้าย/meta ในฟอร์ม → ไม่พับ · ข้อความที่พิมพ์ยังอยู่", expanded(page, "IGV") == "true" and js(page, "()=>document.querySelector('#ffThemes [data-rr=\"IGV\"] [data-sd-f=\"driver\"]').value") == "typing")
        js(page, "()=>{ ffRenderThemes(); }"); settle(page, 200)
        check(f"{tag} 9 วาด RRG ใหม่ (เช่นหลังรีเฟรชราคา) → แถวยังกาง + ข้อความที่ยังไม่บันทึกไม่หาย", expanded(page, "IGV") == "true" and js(page, "()=>document.querySelector('#ffThemes [data-rr=\"IGV\"] [data-sd-f=\"driver\"]').value") == "typing")
        page.locator('[data-sd-star="XBI"]').focus(); page.keyboard.press("Enter"); settle(page, 500)
        check(f"{tag} 9 ดาวกด Enter ได้ (follow) · ไม่กางแถว", (note(page, "XBI") or {}).get("follow") is True and expanded(page, "XBI") == "false")
        # hover ไม่ขยับ layout
        page.locator('[data-sd-hd="SMH"]').scroll_into_view_if_needed(); settle(page, 150); h0 = page.locator('[data-sd-hd="SMH"]').bounding_box(); page.locator('[data-sd-hd="SMH"]').hover();   # TD4a: ★ เปลี่ยนลำดับแถว → เลื่อนให้เห็นก่อนวัด
        h1 = page.locator('[data-sd-hd="SMH"]').bounding_box()
        check(f"{tag} 9 hover ไม่ทำให้ layout ขยับ (ขนาดแถวเท่าเดิม)", abs(h0["height"] - h1["height"]) < 0.5 and abs(h0["y"] - h1["y"]) < 0.5, [h0, h1])
        # ไม่ดึง RRG จาก Today
        js(page, "()=>{ window.__rrCalls = 0; const o = window.rrgRefresh; window.rrgRefresh = function(){ window.__rrCalls++; return o.apply(this, arguments); }; state.settings.tdKey = 'k'; getBook(tdHome()).settings.tdKey = 'k'; ffState().rrg.day = '2000-01-01'; }")
        go_today(page); js(page, "()=>{ todayRefresh(true); }"); settle(page, 400)
        check(f"{tag} 9 เปิด/วาด Today ด้วยแคช RRG เก่า → ไม่เรียก rrgRefresh (ไม่ดึงราคาจาก Today)", js(page, "()=>window.__rrCalls") == 0)
        check(f"{tag} 9 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ───────────────────────── 10 · legacy view + ความกว้างต่ำสุด ─────────────────────────
def legacy_tests(pw):
    tag = f"[{ENGINE}/1280px]"
    b, page, ce, pe = launch(pw, 1280, 900)
    try:
        js(page, "()=>{ ln1SetMode('legacy'); switchTab('flow'); const f=ffState(); f.themesCol=false; f.themesColUser=true; ffRenderThemes(); }"); settle(page, 500)
        t = txt(page, "#ffThemes") or ""
        check(f"{tag} 10 มุมมอง legacy ไม่เปลี่ยน: หัว 'เงินไหลเข้าธีมไหน' · ตาราง rrgTbl · ป้ายไทย (ความแข็ง/โมเมนตัม · แข็ง…) · ไม่มี ☆ / Drivers", txt(page, "#ffThemesTitle") == "เงินไหลเข้าธีมไหน" and cnt(page, "#ffThemes table.rrgTbl") == 1 and "ความแข็ง" in t and "โมเมนตัม" in t
              and cnt(page, "#ffThemes [data-sd-star]") == 0 and cnt(page, "#ffThemes [data-sd-sum]") == 0 and ("แข็ง" in t or "กลาง" in t or "อ่อน" in t), t[:200])
        js(page, "()=>{ ln1SetMode('lean'); switchTab('flow'); ffRenderThemes(); }"); settle(page, 400)
        check(f"{tag} 10 กลับ lean → หัว 'Leadership' + ☆", txt(page, "#ffThemesTitle") == "Leadership" and cnt(page, "#ffThemes [data-sd-star]") == 5)
    finally: b.close()


def width_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        js(page, "()=>{ sdWrite('SMH', n=>{ n.follow=true; n.driver='ก'.repeat(300); n.evidence={summary:'ข'.repeat(700), sources:[{title:'Very long source title '.repeat(4), url:'https://example.com/'+'a'.repeat(300)}]}; n.revisit_if='ค'.repeat(250); n.reviewed_at=new Date(Date.now()-3*864e5).toISOString(); n.reviewed_phase='LEADING'; n.reviewed_tf='D'; return n; }); sdOpen['SMH']=true; sdOpen['XBI']=true; }")
        go_flow(page); ow1 = overflow(page)
        page.locator(f'{sdsel("SMH")} [data-sd-import]').click(); settle(page, 300); ow2 = overflow(page)
        js(page, "()=>sdImpClose()")
        go_today(page); ow3 = overflow(page)
        check(f"{tag} 10 ไม่ล้นแนวนอน: Flow กางยาว ({ow1}) · dialog import ({ow2}) · Today ({ow3})", ow1 <= 0 and ow2 <= 0 and ow3 <= 0)
        check(f"{tag} 10 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        flow_structure(pw, 1440, 900, "1440px")
        flow_structure(pw, 390, 844, "390px")
        flow_shots(pw, 1440, 900, "td3b-flow-1440.png")
        flow_shots(pw, 390, 844, "td3b-flow-390.png")
        flow_structure(pw, 300, 700, "300px")
        follow_tests(pw)
        save_tests(pw)
        flag_tests(pw)
        prompt_tests(pw)
        import_tests(pw, shot="td3b-import-390.png")
        today_tests(pw, 1440, 900, "1440px", shot="td3b-today-1440.png")
        today_tests(pw, 390, 844, "390px", shot="td3b-today-390.png")
        weekend_tests(pw)
        interact_tests(pw)
        legacy_tests(pw)
        for w, h, lab in ((300, 700, "300px"), (390, 844, "390px"), (1280, 800, "1280px"), (1440, 900, "1440px")):
            width_tests(pw, w, h, lab)
    bad = [r for r in results if not r[1]]
    print(f"\nTD3b phase105: {len(results) - len(bad)}/{len(results)} PASS")
    if bad:
        print("FAILURES:")
        for n, _, d in bad: print("FAIL -", n, d if isinstance(d, str) else json.dumps(d, ensure_ascii=False)[:300])
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
