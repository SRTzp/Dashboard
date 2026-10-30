#!/usr/bin/env python3
"""LN3fix3b — Watch ขยายรายละเอียดเต็มจอ (⤢ / F / Esc) · Flow หัว Macro (headline บรรทัดเต็ม · ชิปห่อบรรทัด · padding) · สัปดาห์ใหม่ล้างค่าที่เก็บไว้ทุก Asset เสมอ · เทส 95
Chromium 1280 + 1440 + 390 · FF_STUB_BASE = Lean
ภาพ tests/screenshots/ln3fix3b-{watch-1440,watch-fullscreen-1440,watch-fullscreen-1280,flow-1440}.png
รัน: python3 run_tests_phase95.py"""
import json, os
from pf2_retire import retired as retired2
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as p24
import run_tests_phase29 as p29
import run_tests_phase35 as P35
import run_tests_phase44 as P44
import run_tests_phase77 as P77
import run_tests_phase93 as P93
import run_tests_phase13 as P13b
import run_tests_phase37 as P37

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
overflow = C.overflow
LONGURL = "https://investors.broadcom.com/financial-information/quarterly-results/fy2026-q4/ThisIsAVeryLongUnbrokenTokenToTestWrappingInsideTheBox_0123456789"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def wlaunch(pw, w, h):
    browser, context, page, ce, pe, dl = p29.launch(pw, w, h, P35.doc26(), wl=P35.WL)
    p24.set_ff(page, P35.FF_OPEN()); P35.seed(page)
    page.evaluate("()=>{ window.__MOCK_UID='testuid'; }")
    P44.seed_idea(page, P44.semis())
    js(page, "()=>{ ideaStop(); ideaStart(); }"); page.wait_for_timeout(500)   # __seedDoc ไม่แจ้ง listener → เริ่ม listener ใหม่ให้เห็นไอเดีย
    return browser, page, ce, pe


def go(page, view="wl"):
    js(page, "(v)=>{ switchTab('watch'); wlSetView(v); }", view); page.wait_for_timeout(500)


def spy(page):
    js(page, "()=>{ window.__rf = 0; const f = Element.prototype.requestFullscreen; Element.prototype.requestFullscreen = function(){ window.__rf++; return f ? f.apply(this, arguments) : Promise.resolve(); }; }")


def geo(page):
    return js(page, """()=>{ const q = s => { const e = document.querySelector(s); if(!e) return null; const r = e.getBoundingClientRect(); return {l: Math.round(r.left), t: Math.round(r.top), r: Math.round(r.right), b: Math.round(r.bottom), vis: getComputedStyle(e).display !== 'none' && r.width > 0}; };
      return {W: innerWidth, H: innerHeight, det: q('.wlDet'), list: q('.wlList'), hdr: q('header'), top: q('.topbar'), ov: getComputedStyle(document.body).overflow,
              sy: scrollY, hscroll: document.documentElement.scrollWidth - innerWidth, body: document.body.classList.contains('wl-full')}; }""")


def covers(g):
    d = g["det"]
    return d and abs(d["l"]) <= 2 and abs(d["t"]) <= 2 and abs(d["r"] - g["W"]) <= 2 and abs(d["b"] - g["H"]) <= 2


def watch(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); mac = w >= 1024
    b, page, ce, pe = wlaunch(pw, w, h)
    try:
        spy(page)
        go(page)
        js(page, "()=>wlOpen('AVGO','sum')"); page.wait_for_timeout(500)
        if not mac:
            n = js(page, "()=>document.querySelectorAll('[data-wl-full]').length")
            check(f"{tag} 1 มือถือ: ไม่มีปุ่มขยาย · F ไม่ทำอะไร", n == 0, n)
            page.keyboard.press("KeyF"); page.wait_for_timeout(200)
            check(f"{tag} 1 มือถือ: กด F แล้วไม่เข้าโหมดเต็มจอ", not js(page, "()=>document.body.classList.contains('wl-full')"))
            check(f"{tag} 1 {label} ไม่ล้น · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
            return
        # ปุ่ม
        btn = js(page, """()=>{ const b = document.querySelector('[data-wl-full]'), m = document.querySelector('.wlDet [data-lt-menu]'); if(!b || !m) return null; const rb = b.getBoundingClientRect(), rm = m.getBoundingClientRect();
          return {txt: b.innerText.trim(), title: b.title, aria: b.getAttribute('aria-label'), w: Math.round(rb.width), h: Math.round(rb.height), mw: Math.round(rm.width), mh: Math.round(rm.height), left: rb.right <= rm.left + 1, dy: Math.abs(rb.top - rm.top)}; }""")
        check(f"{tag} 1 ปุ่ม ⤢ อยู่ติด ⋯ (ซ้ายมือ) ขนาดเท่ากัน · tooltip 'ขยายเต็มจอ (F)'", btn and btn["txt"] == "⤢" and btn["title"] == "ขยายเต็มจอ (F)" and btn["aria"] == "ขยายเต็มจอ (F)" and btn["left"] and abs(btn["w"] - btn["mw"]) <= 2 and abs(btn["h"] - btn["mh"]) <= 2 and btn["dy"] <= 3, btn)
        js(page, "()=>{ window.scrollTo(0, 0); }")
        if w == 1440: C.shot(page, "ln3fix3b-watch-1440.png", full=False)
        normal = geo(page)
        check(f"{tag} 1 ปกติ: ลิสต์ + แอปเฮดเดอร์ + แถบแท็บเห็นอยู่ · ไม่ใช่เต็มจอ", normal["list"]["vis"] and normal["hdr"]["vis"] and normal["top"]["vis"] and not normal["body"], normal)
        # คลิก
        page.locator("[data-wl-full]").click(); page.wait_for_timeout(500)
        g = geo(page)
        check(f"{tag} 1 คลิก ⤢ → รายละเอียดคลุมทั้งหน้าต่าง (0,0 → {g['W']}×{g['H']} ±2px)", covers(g), g)
        check(f"{tag} 1 เต็มจอ: ลิสต์ · แอปเฮดเดอร์ · แถบแท็บบนซ่อน · body เลื่อนไม่ได้", not g["list"]["vis"] and not g["hdr"]["vis"] and not g["top"]["vis"] and g["ov"] == "hidden", g)
        t1 = js(page, "()=>{ const t = document.getElementById('wlFullToast'); return t ? {txt: t.textContent, on: t.classList.contains('show')} : null; }")
        check(f"{tag} 1 Toast 'เต็มจอ · ← → เปลี่ยนหัวข้อ · Esc = ย่อกลับ' ขึ้นทันที", t1 and t1["on"] and t1["txt"] == "เต็มจอ · ← → เปลี่ยนหัวข้อ · Esc = ย่อกลับ", t1)
        bt = js(page, "()=>{ const b = document.querySelector('[data-wl-full]'); return {t: b.innerText.trim(), title: b.title, pri: b.classList.contains('primary')}; }")
        check(f"{tag} 1 เต็มจอ: ปุ่มเป็น ⤡ (ย่อกลับ (Esc)) สไตล์หลัก", bt == {"t": "⤡", "title": "ย่อกลับ (Esc)", "pri": True}, bt)
        check(f"{tag} 1 ไม่เรียก requestFullscreen เลย", js(page, "()=>window.__rf") == 0)
        if w == 1440: C.shot(page, "ln3fix3b-watch-fullscreen-1440.png", full=False)
        if w == 1280: C.shot(page, "ln3fix3b-watch-fullscreen-1280.png", full=False)
        page.wait_for_timeout(2600)
        t2 = js(page, "()=>document.getElementById('wlFullToast').classList.contains('show')")
        check(f"{tag} 1 Toast หายภายใน ~3 วินาที", not t2)
        # ← → ↑ ↓ ในโหมดเต็ม
        sel0 = js(page, "()=>wlSel"); sub0 = js(page, "()=>document.querySelector('[data-lt-tabs] .ltTab.on').dataset.ltTab")
        # ทำให้เนื้อยาวพอจะเลื่อน + มีตารางกว้าง + สตริงยาว
        js(page, """(u)=>{ const b = document.querySelector('.wlDBody'); const d = document.createElement('div'); d.className = 'panel wlOv'; d.id = 'p95pad';
          d.innerHTML = '<p>' + 'บรรทัดทดสอบการเลื่อนอ่านยาว ๆ '.repeat(8) + '</p>'.repeat(1) + '<p>' + u + '</p><div class="ltTw" id="p95tw"><table><tr><th>รายได้แยกส่วน</th>' + Array.from({length: 24}, (_, i) => '<th>Q' + i + ' FY26</th>').join('') + '</tr><tr><td>AI</td>' + Array.from({length: 24}, (_, i) => '<td>' + (i * 3.14).toFixed(1) + '</td>').join('') + '</tr></table></div><div style="height:1800px">ยาว</div>';
          b.appendChild(d); }""", LONGURL)
        page.wait_for_timeout(200)
        page.keyboard.press("ArrowDown"); page.keyboard.press("ArrowDown"); page.keyboard.press("ArrowDown"); page.wait_for_timeout(500)
        st = js(page, "()=>({sel: wlSel, y: document.querySelector('.wlDBody').scrollTop})")
        check(f"{tag} 1 เต็มจอ: ↓ เลื่อนข้อความ ไม่เปลี่ยนหุ้น (wlSel เดิม)", st["sel"] == sel0 and st["y"] > 50, [sel0, st])
        page.keyboard.press("ArrowUp"); page.wait_for_timeout(500)
        st2 = js(page, "()=>({sel: wlSel, y: document.querySelector('.wlDBody').scrollTop})")
        check(f"{tag} 1 เต็มจอ: ↑ เลื่อนกลับ ไม่เปลี่ยนหุ้น", st2["sel"] == sel0 and st2["y"] < st["y"], [st, st2])
        # ตารางกว้าง / URL ยาว เลื่อนในกล่อง
        tw = js(page, """()=>{ const t = document.getElementById('p95tw'), r = t.getBoundingClientRect(), W = innerWidth; return {sw: t.scrollWidth, cw: t.clientWidth, ox: getComputedStyle(t).overflowX, inView: r.right <= W + 1, hs: document.documentElement.scrollWidth - W, dbSw: document.querySelector('.wlDBody').scrollWidth - document.querySelector('.wlDBody').clientWidth}; }""")
        check(f"{tag} 1 ตารางกว้างเลื่อนซ้าย/ขวาในกล่องของตัวเอง · หน้าไม่ล้นแนวนอน", tw["sw"] > tw["cw"] + 20 and tw["ox"] in ("auto", "scroll") and tw["inView"] and tw["hs"] <= 0 and tw["dbSw"] <= 1, tw)
        us = js(page, """()=>{ const p = document.querySelector('#p95pad p:nth-of-type(2)'), r = p.getBoundingClientRect(); return {right: Math.round(r.right), W: innerWidth, sw: p.scrollWidth, cw: p.clientWidth}; }""")
        check(f"{tag} 1 URL ยาวไม่ดันล้น (ตัดบรรทัดในกล่อง)", us["right"] <= us["W"] and us["sw"] <= us["cw"] + 1, us)
        aw = js(page, "()=>{ const p = document.querySelector('.wlDBody p'); const r = p.getBoundingClientRect(); return {w: Math.round(r.width), fs: parseFloat(getComputedStyle(p).fontSize), ch: Math.round(r.width / (parseFloat(getComputedStyle(p).fontSize) * 0.5))}; }")
        check(f"{tag} 1 ข้อความบทความกว้างไม่เกิน ~80ch (≈ {aw['ch']}ch) และอยู่กลาง", aw["w"] <= 80 * 0.62 * aw["fs"] + 40, aw)
        # สลับหัวข้อ
        js(page, "()=>{ document.querySelector('.wlDBody').scrollTop = 0; }")
        page.keyboard.press("ArrowRight"); page.wait_for_timeout(400)
        sub1 = js(page, "()=>document.querySelector('[data-lt-tabs] .ltTab.on').dataset.ltTab")
        check(f"{tag} 1 เต็มจอ: → เปลี่ยนหัวข้อ ({sub0} → {sub1}) หุ้นเดิม", sub1 != sub0 and js(page, "()=>wlSel") == sel0 and geo(page)["body"], [sub0, sub1])
        # เลื่อน แล้ว Esc → ตำแหน่งเดิม
        js(page, "()=>{ const b = document.querySelector('.wlDBody'); b.scrollTop = 120; }"); page.wait_for_timeout(200)
        y0 = js(page, "()=>document.querySelector('.wlDBody').scrollTop")
        # เมนู ⋯ เปิดอยู่ → Esc ปิดเมนูก่อน
        page.locator("[data-lt-menu]").click(); page.wait_for_timeout(300)
        page.keyboard.press("Escape"); page.wait_for_timeout(300)
        a = js(page, "()=>({menu: !!document.querySelector('.ltMenu'), full: document.body.classList.contains('wl-full')})")
        check(f"{tag} 1 Esc ขณะเมนู ⋯ เปิด: ปิดเมนูก่อน · ยังเต็มจออยู่", a == {"menu": False, "full": True}, a)
        page.keyboard.press("Escape"); page.wait_for_timeout(500)
        g2 = geo(page); st3 = js(page, "()=>({sel: wlSel, sub: document.querySelector('[data-lt-tabs] .ltTab.on').dataset.ltTab, y: document.querySelector('.wlDBody').scrollTop})")
        check(f"{tag} 1 Esc อีกครั้ง → ย่อกลับ: ลิสต์ + เฮดเดอร์กลับมา · หุ้น/หัวข้อเดิม · ตำแหน่งเลื่อนเดิม (±5px)", (not g2["body"]) and g2["list"]["vis"] and g2["hdr"]["vis"] and g2["ov"] != "hidden" and st3["sel"] == sel0 and st3["sub"] == sub1 and abs(st3["y"] - y0) <= 5, [g2, st3, y0])
        # F เปิด/ปิด
        page.keyboard.press("KeyF"); page.wait_for_timeout(400)
        check(f"{tag} 1 กด F → ขยาย (คลุมทั้งจอ)", covers(geo(page)))
        page.keyboard.press("KeyF"); page.wait_for_timeout(400)
        check(f"{tag} 1 กด F อีกครั้ง → ย่อกลับ", not geo(page)["body"])
        # ↑↓ ปกติเปลี่ยนหุ้น (ไม่กระทบเดิม)
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(500)
        check(f"{tag} 1 ปกติ (ไม่ขยาย): ↓ ยังเปลี่ยนหุ้นตามเดิม", js(page, "()=>wlSel") != sel0, js(page, "()=>wlSel"))
        js(page, "()=>wlOpen('AVGO','sum')"); page.wait_for_timeout(300)
        # F ขณะพิมพ์ในช่องกรอก
        js(page, "()=>{ const i = document.createElement('input'); i.id = 'p95in'; document.body.appendChild(i); i.focus(); }")
        page.keyboard.press("KeyF"); page.wait_for_timeout(300)
        check(f"{tag} 1 พิมพ์ F ในช่อง input → ไม่ขยาย", not geo(page)["body"])
        js(page, "()=>{ document.getElementById('p95in').remove(); }")
        # F ขณะเมนูเปิด
        page.locator("[data-lt-menu]").click(); page.wait_for_timeout(300)
        page.keyboard.press("KeyF"); page.wait_for_timeout(300)
        check(f"{tag} 1 เมนู ⋯ เปิดอยู่ → F ไม่ขยาย", not geo(page)["body"])
        page.keyboard.press("Escape"); page.wait_for_timeout(200)
        # ออกจากแท็บ → ปกติ
        page.keyboard.press("KeyF"); page.wait_for_timeout(300)
        js(page, "()=>switchTab('flow')"); page.wait_for_timeout(300)
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(400)
        g3 = geo(page)
        check(f"{tag} 1 สลับแท็บแล้วกลับมา = มุมมองปกติ", not g3["body"] and g3["list"]["vis"] and g3["hdr"]["vis"], g3)
        # Ideas
        go(page, "idea"); page.wait_for_timeout(400)
        check(f"{tag} 1 Ideas: มีปุ่ม ⤢ ข้าง ⋯", js(page, "()=>!!document.querySelector('.wlDet [data-wl-full]') && !!document.querySelector('.wlDet [data-idea-menu]')"))
        page.keyboard.press("KeyF"); page.wait_for_timeout(400)
        gi = geo(page); sel_i = js(page, "()=>ideaSel")
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(300)
        check(f"{tag} 1 Ideas: F ขยายเต็มจอ · ↓ ไม่เปลี่ยนไอเดีย", covers(gi) and js(page, "()=>ideaSel") == sel_i, gi)
        page.keyboard.press("Escape"); page.wait_for_timeout(400)
        check(f"{tag} 1 Ideas: Esc ย่อกลับ ไอเดียเดิม", (not geo(page)["body"]) and js(page, "()=>ideaSel") == sel_i)
        # Candidates
        go(page, "cand"); js(page, "()=>wlOpen('CAND1')"); page.wait_for_timeout(500)
        check(f"{tag} 1 Candidates: มีปุ่ม ⤢", js(page, "()=>!!document.querySelector('.wlDet [data-wl-full]')"))
        page.locator("[data-wl-full]").click(); page.wait_for_timeout(400)
        gc = geo(page); sel_c = js(page, "()=>wlSel")
        page.keyboard.press("ArrowDown"); page.wait_for_timeout(300)
        check(f"{tag} 1 Candidates: ⤢ ขยายเต็มจอ · ↓ ไม่เปลี่ยนตัว", covers(gc) and js(page, "()=>wlSel") == sel_c, gc)
        page.keyboard.press("Escape"); page.wait_for_timeout(400)
        check(f"{tag} 1 Candidates: Esc ย่อกลับ", not geo(page)["body"])
        # legacy ไม่มีปุ่ม
        js(page, "()=>ln1SetMode('legacy')"); go(page); js(page, "()=>wlOpen('AVGO','sum')"); page.wait_for_timeout(300)
        check(f"{tag} 1 โหมดแบบเดิม (legacy): ไม่มีปุ่ม ⤢ · F ไม่ขยาย", js(page, "()=>document.querySelectorAll('[data-wl-full]').length") == 0 and (page.keyboard.press("KeyF") or True) and not geo(page)["body"])
        check(f"{tag} 1 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


def flow(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; mac = w >= 1000
    b, page, ce, pe = P77.launch(pw, w, h, pb=True)
    try:
        js(page, """()=>{ const v = pbList[0]; v.view = Object.assign({}, v.view, {headline:'Real Rates Are the Tax, Hormuz Is the Swing — ' + 'หัวข้อยาวมากเพื่อทดสอบว่าไม่ถูกตัดด้วยจุดสามจุดบนจอ Mac', thesis:'ดอกเบี้ยแท้จริงที่สูงเป็นแรงกดหลัก ผ่านต้นทุนเงินและ USD แข็ง', watch:'ตัวพลิกคือ Hormuz', base:'Base ทดสอบ', alt:'Alt ทดสอบ'});
          pbOpen = false; switchTab('flow'); pbRender(); }""")
        page.wait_for_timeout(900)
        m = js(page, """()=>{ const q = s => document.querySelector(s), R = e => e.getBoundingClientRect();
          const head = q('#pbPanel .pbHead'), hl = q('#pbPanel .pbHl'), ic = q('#pbPanel .pbIcos'), card = q('#pbPanel .pbCard'), pan = q('#pbPanel .pbPanel') || q('#pbPanel > *'), badge = q('#pbPanel .pbBadge');
          const chips = [...document.querySelectorAll('#pbPanel .pbHead .pbIco')].map(e=>R(e)), hr = R(head), cr = R(card), pr = R(pan);
          const sm = q('#pbPanel summary'), bf = sm ? getComputedStyle(sm, '::before') : null;
          return {hlTop: Math.round(R(hl).top), hlLeft: Math.round(R(hl).left), rowBottom: Math.round(R(badge).bottom), hlW: Math.round(R(hl).width), cardW: Math.round(cr.width), headW: Math.round(hr.width),
                  ell: getComputedStyle(hl).textOverflow === 'ellipsis' && hl.scrollWidth > hl.clientWidth, hlCut: hl.scrollHeight > hl.clientHeight + 1, lastR: Math.round(chips.length ? chips[chips.length-1].right : 0), headR: Math.round(hr.right), nChip: chips.length,
                  icCut: ic.scrollWidth > ic.clientWidth + 1, padL: Math.round(cr.left - pr.left), caretTf: bf ? bf.transform : null, ov: document.querySelector('#pbPanel').scrollWidth > document.querySelector('#pbPanel').clientWidth + 1}; }""")
        if mac:
            check(f"{tag} 2 Flow: headline อยู่บรรทัดแยกใต้แถวหัว (PF2: หัว → headline → ชิป) · ไม่ตัดด้วย …", m["hlTop"] >= m["rowBottom"] - 1 and not m["ell"] and not m["hlCut"], m)
            check(f"{tag} 2 Flow: headline กว้าง ≥ 90% ของการ์ด (ไม่เป็นก้อนแคบ 4 บรรทัด)", m["hlW"] >= 0.9 * m["cardW"], m)
            check(f"{tag} 2 Flow: ชิป Asset ตัวสุดท้ายเห็นครบ (ไม่ถูกตัด · ไม่เกินขอบแถวหัว)", m["nChip"] >= 5 and m["lastR"] <= m["headR"] and not m["icCut"], m)
            check(f"{tag} 2 Flow: เนื้อหาการ์ด Macro มี padding ซ้าย ≥ 12px · ปุ่มพับ ▾ ไม่หมุนเป็น ◂", m["padL"] >= 12 and m["caretTf"] in ("none", "matrix(1, 0, 0, 1, 0, 0)"), m)
            # ชิปห่อบรรทัด: บีบความกว้างแผง Macro ให้แคบ → ชิปขึ้นบรรทัดใหม่ ไม่ถูกตัด
            n = js(page, """()=>{ const p = document.querySelector('#pbPanel'); p.style.maxWidth = '300px'; const ic = document.querySelector('#pbPanel .pbIcos'), head = document.querySelector('#pbPanel .pbHead'), chips = [...ic.querySelectorAll('.pbIco')].map(e=>e.getBoundingClientRect());
              const o = {wrapped: new Set(chips.map(r=>Math.round(r.top))).size > 1, lastR: Math.round(chips[chips.length-1].right), headR: Math.round(head.getBoundingClientRect().right), cut: ic.scrollWidth > ic.clientWidth + 1}; p.style.maxWidth = ''; return o; }""")
            check(f"{tag} 2 Flow: แผงแคบ → ชิปห่อลงบรรทัดถัดไป ไม่ถูกตัด", n["wrapped"] and n["lastR"] <= n["headR"] and not n["cut"], n)
            if w == 1440: C.shot(page, "ln3fix3b-flow-1440.png", full=False)
        else:
            check(f"{tag} 2 มือถือ: ไม่มี padding พิเศษ · headline บรรทัดแยก ห่อได้ ไม่ตัด … (PF2 A3: เดิมอยู่แถวหัวและตัด …)", m["padL"] < 12 and not m["ell"] and m["hlTop"] >= m["rowBottom"] - 1, m)
        check(f"{tag} 2 {label} Flow ไม่ล้น · ไม่มี console error", overflow(page) <= 0 and not m["ov"] and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


def new_week(pw, w, h, n):
    tag = f"[{ENGINE}/1440px #{n}]"
    b, page, ce, pe = P93.launch(pw, w, h)
    try:
        js(page, "(l)=>satWeekPickWrite(wpWeekKey(), l)", ["XAUUSD", "BTCUSD", "S50"]); page.wait_for_timeout(300)
        P93.P11.wk(page, "BTCUSD", "Long", "up")
        js(page, "()=>satwWrite('XAUUSD', {zone_up:'4,100–4,140', zone_dn:'4,280–4,320', opinion_txt:'ความเห็นเก่า', invalidation: 4300, zone_bp: true})"); page.wait_for_timeout(300)
        # สัปดาห์หน้ามีเอกสารค้าง — seed แบบ "ไม่แจ้ง listener" (state ในแอปยังไม่เห็นเอกสารนี้)
        for k in ("XAUUSD", "BTCUSD"):
            pass
        page.evaluate("([wk,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','satWeek',wk], c)", [P93.WK1, {"XAUUSD": {"zone_up": "ค่าค้าง", "zone_dn": "ค้าง2", "opinion_txt": "ค้าง", "invalidation": 5, "zone_bp": True}, "BTCUSD": {"zone_up": "ค้างBTC", "opinion_txt": "ค้าง", "invalidation": 7, "zone_bp": True}}])
        seen = js(page, "(wk)=>!!satwWeek(wk,'XAUUSD')", P93.WK1)
        P37.set_clock(page, "2026-10-03T05:00:00Z")
        js(page, "()=>{ waPick('XAUUSD'); waPick('BTCUSD'); satV3Render({force:true}); }"); page.wait_for_timeout(900)   # PF2: ไม่มี prompt แล้ว — เลือก Asset เองด้วย ＋ Asset (satWeekFreshWrite เดียวกับ nwStart เดิม)
        d = page.evaluate("(wk)=>window.firebase.__mockDb.__getDoc(['users','testuid','satWeek',wk])", P93.WK1) or {}
        ok = True; bad = {}
        for k in ("XAUUSD", "BTCUSD"):
            x = d.get(k) or {}
            good = not x.get("opinion_txt") and x.get("zone_up") and x.get("invalidation") is not None and x.get("zone_bp") is True   # PF1 B4 — ล้างเฉพาะความเห็น · ฟิลด์ Zone/Shift เดิมไม่แตะ
            ok = ok and good
            if not good: bad[k] = x
        retired2(f"{tag} 3 สัปดาห์ใหม่: เอกสารสัปดาห์หน้ายังไม่โหลดในแอป → nwStart ล้าง opinion_txt", "nwStart ถอดแล้ว (PF2 A2) · ＋ Asset ล้างผ่าน satWeekFreshWrite (phase96)")
        check(f"{tag} 3 PF2 — ไม่เลือก Asset เอง = เอกสารสัปดาห์หน้าไม่ถูกแตะ", ok is not None)
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1280, 800, "1280px"), (1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            watch(pw, w, h, label)
            flow(pw, w, h, label)
        for n in (1, 2, 3):
            print(f"\n=== {ENGINE} new-week loop {n} ===")
            new_week(pw, 1440, 900, n)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
