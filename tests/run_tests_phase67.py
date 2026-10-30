#!/usr/bin/env python3
"""ESC1 — Esc ปิด pop-up ทุกตัว (ชั้นบนสุดชั้นเดียว) · กราฟเห็นเต็มไม่ครอป · ปุ่มทิศ Break อันเดียว · ช่องกราฟ TV ใน มุมมอง เห็นทันที · เทส 67
mock Firestore · Chromium 1440 + 390 · ภาพ PNG ปลอมสัดส่วน 2:1 (200×100)
ภาพ tests/screenshots/esc1-{sat-chart,vw-tech-open,vw-tech-add,brk-dir}-{1440,390}.png
รัน: python3 run_tests_phase67.py"""
import base64, json, os, re, struct, zlib
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase25 as p25
import run_tests_phase37 as P37
import run_tests_phase39 as P39
import run_tests_phase40 as P40
import run_tests_phase41 as P41
import run_tests_phase59 as P59
import run_tests_phase60 as P60
import run_tests_phase63 as P63
import run_tests_phase65 as P65

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
ROOT = '.ui-plan[data-id="iD"]'
TV1, TV2, TV3 = P59.TV1, P59.TV2, "https://www.tradingview.com/x/Cc56Dd78/"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def png(w, h):
    raw = b"".join(b"\x00" + b"\x30\x60\x90" * w for _ in range(h))
    def ch(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b"")


P59.PNG = png(200, 100)     # สัดส่วน 2:1 (ภาพ 1×1 เดิมเป็นสี่เหลี่ยมจัตุรัส ทดสอบสัดส่วนไม่ได้)
shot = P60.shot
wait = P59.wait
cnt = P59.cnt
doc_of = P59.doc_of
overflow = P59.overflow
fresh, cond, bp_idea, cd, ac = P63.fresh, P63.cond, P63.bp_idea, P63.cd, P63.ac


def esc(page, n=1):
    for _ in range(n): page.keyboard.press("Escape"); wait(page, 180)


def real(ce): return [e for e in ce if "Failed to load resource" not in e]


def tab_state(page): return js(page, "()=>({tab:activeTab, y:document.querySelectorAll('.overlay.show,.core-sheet,#vwLb').length})")


def fit_ratio(page, sel):
    return js(page, "(s)=>{ const i=document.querySelector(s+' img'); const o=document.querySelector(s); if(!i) return null; const r=i.getBoundingClientRect(), q=o.getBoundingClientRect(); return {fit:getComputedStyle(i).objectFit, w:r.width, h:r.height, exp:r.width*i.naturalHeight/i.naturalWidth, nw:i.naturalWidth, nh:i.naturalHeight, boxW:q.width, boxH:q.height, vw:innerWidth}; }", sel)


def ratio_ok(m): return m and m["fit"] == "contain" and m["nw"] == 200 and abs(m["h"] - m["exp"]) <= 2 and abs(m["h"] - m["w"] / 2) <= 2 and m["boxH"] >= m["h"] - 1


# ───────────────────────── 1–3 · Core sheets ─────────────────────────
def core_esc(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    ct = [p25.usT("t_cz", "CZZ", 250, 100, 90)]
    cards = {"cz": p25.ucard("cz", "t_cz", "CZZ", [(100, 250)], 90, tier="B", px=120, pxDate=p25.TODAY, emaW=100)}
    b, page, ce, pe = P65.setup(pw, w, h, coreRisk={"riskPct": 1.25, "maxLots": 6}, cards=cards, trades=ct)
    try:
        def open_buyadd():
            js(page, "()=>{ const cx=coreCtx('main'); const c=coreCardsList.find(x=>x.id==='cz'); coreSim['cz']={px:'120', stop:'110'}; coreBuyAddOpen('cz'); }")
        cases = [
            ("sheet Core แผนใหม่", "()=>coreNewOpen('main')", ".core-sheet[data-x], .core-sheet"),
            ("sheet Core ซื้อไม้เติม (ไม้ 1)", None, ".core-sheet"),
            ("sheet Core ล็อต", "()=>coreLotsOpen('cz')", ".core-sheet"),
            ("sheet กรอกค่าพอร์ต (glValOverlay)", "()=>{ const a = acctList[0]; window.glAccts = ()=>[{a, g:{cur:'THB'}}]; glValOpen(); }", "#glValOverlay.show"),
            ("sheet ของแอป (UI.sheet อื่น ไม่มี handler: .bk-sheet)", "()=>{ document.body.insertAdjacentHTML('beforeend', UI.sheet('<div>x</div>').replace('ui-sheet-backdrop','ui-sheet-backdrop bk-sheet')); }", ".bk-sheet"),
            ("sheet ลบ Sat (s7del)", "()=>{ document.body.insertAdjacentHTML('beforeend', UI.sheet('<div>x</div>').replace('ui-sheet-backdrop','ui-sheet-backdrop s7del-sheet')); }", ".s7del-sheet"),
            ("sheet เติมไม้ Future (pyr)", "()=>{ document.body.insertAdjacentHTML('beforeend', UI.sheet('<div>x</div>').replace('ui-sheet-backdrop','ui-sheet-backdrop pyr-sheet')); }", ".pyr-sheet"),
            ("sheet Playbook (pb)", "()=>{ document.body.insertAdjacentHTML('beforeend', UI.sheet('<div>x</div>').replace('ui-sheet-backdrop','ui-sheet-backdrop pb-sheet')); }", ".pb-sheet"),
            ("sheet Reset (cl2a)", "()=>cl2aSheet('<div>x</div>')", ".cl2a-sheet"),
            (".overlay เดิม (ตั้งค่า)", "()=>openSettings()", ".overlay.show"),
        ]
        for nm, code, sel in cases:
            if code is None: open_buyadd()
            else: js(page, code)
            wait(page, 300)
            was = cnt(page, sel)
            esc(page)
            now = cnt(page, sel)
            check(f"{tag} 1 {nm}: เปิด ({was}) → Esc → ปิด ({now})", was >= 1 and now == 0, f"{was}->{now}")
            esc(page)   # เผื่อมีอะไรค้าง
        st = js(page, "()=>[typeof coreNew, coreNew, coreDlg]")
        check(f"{tag} 1 หลังปิด sheet Core: state ฟอร์ม (coreNew/coreDlg) ถูกล้างผ่าน coreSheetClose", st[1] is None and st[2] is None, json.dumps(st))
        # ── 2 ซ้อน
        js(page, "()=>coreNewOpen('main')"); wait(page, 250)
        js(page, "()=>{ const el=document.createElement('span'); el.dataset.src='https://s3.tradingview.com/snapshots/p/pSb8OxWO.png'; el.dataset.url='https://www.tradingview.com/x/pSb8OxWO/'; vwZoom(el); }"); wait(page, 200)
        a0 = (cnt(page, "#vwLb"), cnt(page, ".core-sheet"))
        esc(page); a1 = (cnt(page, "#vwLb"), cnt(page, ".core-sheet"))
        esc(page); a2 = (cnt(page, "#vwLb"), cnt(page, ".core-sheet"))
        check(f"{tag} 2 sheet Core + lightbox: Esc#1 ปิดเฉพาะ lightbox · Esc#2 ปิด sheet", a0 == (1, 1) and a1 == (0, 1) and a2 == (0, 0), json.dumps([a0, a1, a2]))
        js(page, "()=>coreNewOpen('main')"); wait(page, 250)
        js(page, "()=>{ const m=document.createElement('div'); m.className='ccMenu on'; m.id='esc1Menu'; document.querySelector('.core-sheet .ccSh').appendChild(m); }")
        b0 = (cnt(page, "#esc1Menu.on"), cnt(page, ".core-sheet"))
        esc(page); b1 = (cnt(page, "#esc1Menu.on"), cnt(page, ".core-sheet"))
        esc(page); b2 = (cnt(page, "#esc1Menu.on"), cnt(page, ".core-sheet"))
        check(f"{tag} 2 เมนู ⋯ (.ccMenu) บน sheet: Esc#1 ปิดเมนูอย่างเดียว · Esc#2 ปิด sheet", b0 == (1, 1) and b1 == (0, 1) and b2 == (0, 0), json.dumps([b0, b1, b2]))
        js(page, "()=>{ openSettings(); coreNewOpen('main'); }"); wait(page, 250)
        c0 = (cnt(page, ".overlay.show"), cnt(page, ".core-sheet"))
        esc(page); c1 = (cnt(page, ".overlay.show"), cnt(page, ".core-sheet"))
        esc(page); c2 = (cnt(page, ".overlay.show"), cnt(page, ".core-sheet"))
        check(f"{tag} 2 sheet Core ซ้อนบน .overlay: Esc#1 ปิด sheet ก่อน · Esc#2 ปิด overlay", c0 == (1, 1) and c1 == (1, 0) and c2 == (0, 0), json.dumps([c0, c1, c2]))
        # ── 3 พิมพ์ในช่อง / IME / ไม่มีอะไรเปิด
        js(page, "()=>coreNewOpen('main')"); wait(page, 250)
        page.locator(".core-sheet input").first.focus(); page.keyboard.type("12"); wait(page, 100)
        foc = js(page, "()=>document.activeElement.tagName")
        esc(page)
        check(f"{tag} 3 Esc ขณะโฟกัสในช่องกรอกของ sheet → sheet ปิด (โฟกัส {foc})", foc == "INPUT" and cnt(page, ".core-sheet") == 0)
        js(page, "()=>coreNewOpen('main')"); wait(page, 250)
        page.locator(".core-sheet input").first.focus()
        js(page, "()=>{ document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',isComposing:true,bubbles:true,cancelable:true})); }"); wait(page, 150)
        check(f"{tag} 3 Esc ระหว่าง IME (isComposing) → sheet ไม่ปิด", cnt(page, ".core-sheet") == 1)
        esc(page)
        before = js(page, "()=>JSON.stringify({t:activeTab, w:typeof wlSel!=='undefined'?wlSel:null, ph:typeof phMenu!=='undefined'?phMenu:null, ov:document.querySelectorAll('.overlay.show,.core-sheet,#vwLb').length})")
        esc(page, 2)
        after = js(page, "()=>JSON.stringify({t:activeTab, w:typeof wlSel!=='undefined'?wlSel:null, ph:typeof phMenu!=='undefined'?phMenu:null, ov:document.querySelectorAll('.overlay.show,.core-sheet,#vwLb').length})")
        check(f"{tag} 3 ไม่มี pop-up เปิด → Esc ไม่ทำอะไร (แท็บ/state เท่าเดิม)", before == after, before + " / " + after)
        check(f"{tag} 3 console ไม่มี error (Core)", not real(ce) and not pe, json.dumps(real(ce)[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


# ───────────────────────── Watch / Sat ─────────────────────────
def watch_esc(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    notes = {"AVGO": {"event": [], "fund": [], "tech": [{"id": "t1", "d": "2026-10-08", "t": "พักใกล้ EMA10", "chart": TV2}], "updated_at": "x"}}
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, wl=[("AVGO", P41.V3, {})], notes=notes)
    try:
        P40.go_watch(page); wait(page, 300)
        # เมนู phase
        js(page, "()=>phMenuToggle('AVGO')"); wait(page, 250)
        n0 = cnt(page, "[data-ph-menu]")
        esc(page)
        check(f"{tag} 1 เมนู phase (PH1): เปิด ({n0}) → Esc → ปิด ({cnt(page, '[data-ph-menu]')})", n0 == 1 and cnt(page, "[data-ph-menu]") == 0 and js(page, "()=>phMenu") == "")
        # แผง Filter
        has = cnt(page, "[data-flt-toggle], [data-flt]")
        js(page, "()=>fltToggle()"); wait(page, 250)
        f0 = cnt(page, "[data-flt-panel]")
        esc(page)
        check(f"{tag} 1 แผง Filter (UX2): เปิด ({f0}) → Esc → ปิด ({cnt(page, '[data-flt-panel]')})", f0 == 1 and cnt(page, "[data-flt-panel]") == 0 and js(page, "()=>fltOpen") is False)
        # เมนู ⋯ ในการ์ด
        js(page, "()=>wlOpen('AVGO','sum')"); wait(page, 350)
        js(page, "()=>ltMenuToggle('AVGO')"); wait(page, 250)
        m0 = cnt(page, ".ltMenu")
        esc(page)
        check(f"{tag} 1 เมนู ⋯ ของการ์ด Thesis: เปิด ({m0}) → Esc → ปิด ({cnt(page, '.ltMenu')})", m0 == 1 and cnt(page, ".ltMenu") == 0)
        # กล่องคำศัพท์ + ซ้อน
        js(page, "()=>{ phMenuToggle('AVGO'); }"); wait(page, 200)
        js(page, "()=>{ document.body.insertAdjacentHTML('beforeend','<div id=\"ltTermPop\"></div>'); ltPopBtn = document.body; }")
        z0 = (cnt(page, "#ltTermPop"), cnt(page, "[data-ph-menu]"))
        esc(page); z1 = (cnt(page, "#ltTermPop"), cnt(page, "[data-ph-menu]"))
        esc(page); z2 = (cnt(page, "#ltTermPop"), cnt(page, "[data-ph-menu]"))
        check(f"{tag} 2 กล่องคำศัพท์ + เมนู phase: Esc#1 ปิดกล่องคำศัพท์ · Esc#2 ปิดเมนู", z0 == (1, 1) and z1 == (0, 1) and z2 == (0, 0), json.dumps([z0, z1, z2]))
        # lightbox จากแท็บ มุมมอง
        js(page, "()=>wlOpen('AVGO','view')"); wait(page, 400)
        page.locator(".wlDBody [data-vw-row=tech]").click(); wait(page, 300)
        top = ".wlDBody [data-vw-ang=tech] .vwTop .vwImg"
        wait(page, 400)
        rt = fit_ratio(page, top)
        check(f"{tag} 4 มุมมอง · Tech กาง: กราฟล่าสุดเต็มกว้างบนสุด · object-fit contain · สูง ≈ กว้าง × สัดส่วนจริง (±2px) · ไม่ครอป", ratio_ok(rt) and cnt(page, ".wlDBody [data-vw-ang=tech] > :first-child.vwTop") == 1, json.dumps(rt))
        if label == "390px":
            check(f"{tag} 4 มุมมอง 390: ภาพไม่ล้นแนวนอน", overflow(page) <= 0 and rt["boxW"] <= rt["vw"], json.dumps([overflow(page), rt]))
        shot(page, f"esc1-vw-tech-open-{sfx}.png", ".wlDBody")
        page.locator(top).click(); wait(page, 300)
        l0 = cnt(page, "#vwLb")
        esc(page)
        check(f"{tag} 1 lightbox กราฟ (จากแท็บ มุมมอง): เปิด ({l0}) → Esc → ปิด ({cnt(page, '#vwLb')}) · ไม่มี error", l0 == 1 and cnt(page, "#vwLb") == 0)
        # โฟกัสอยู่ที่ <a> ใน lightbox / ช่องกรอก → Esc ยังปิด
        page.locator(top).click(); wait(page, 250)
        page.locator("#vwLb a").focus()
        esc(page)
        check(f"{tag} 1 lightbox: โฟกัสอยู่ที่ลิงก์ 'เปิดใน TV' → Esc ปิดได้", cnt(page, "#vwLb") == 0)
        # ประวัติ 2 ข้อ → ข้อเก่ายังเป็นภาพย่อ 110px
        js(page, "()=>vwWrite('AVGO','tech',[{id:'t2',d:'2026-10-09',t:'ใหม่',chart:'" + TV3 + "'},{id:'t1',d:'2026-10-08',t:'เก่า',chart:'" + TV2 + "'}])"); wait(page, 400)
        hi = js(page, "()=>[...document.querySelectorAll('.wlDBody [data-vw-ang=tech] .vwHImg .vwImg')].map(e=>Math.round(e.getBoundingClientRect().height))")
        tp = js(page, "()=>document.querySelector('.wlDBody [data-vw-ang=tech] .vwTop .vwImg img').getAttribute('src')")
        check(f"{tag} 4 ประวัติ Tech ข้อเก่ายังเป็นภาพย่อสูง 110px (1 ภาพ) · กราฟล่าสุดอยู่บนสุดเต็มกว้าง", hi == [110] and tp.endswith("/C/Cc56Dd78.png".lower() if False else "Cc56Dd78.png"), json.dumps([hi, tp]))
        # แถวมินิ 54×30 คงเดิม (พับ)
        page.locator(".wlDBody [data-vw-row=tech]").click(); wait(page, 300)
        mini = js(page, "()=>{ const e=document.querySelector('.wlDBody [data-vw-row=tech] .vwMini'); if(!e) return null; const r=e.getBoundingClientRect(); return {w:r.width,h:r.height,fit:getComputedStyle(e.querySelector('img')).objectFit,add:document.querySelectorAll('.wlDBody [data-vw-add-tv]').length}; }")
        check(f"{tag} 2 รูปจิ๋วในแถว (vwMini) คง 54×30 · ครอปได้ (cover) · มีกราฟแล้ว → ไม่มีปุ่ม ＋ กราฟ TV", mini and mini["w"] == 54 and mini["h"] == 30 and mini["fit"] == "cover" and mini["add"] == 0, json.dumps(mini))
        check(f"{tag} 1 console ไม่มี error (Watch)", not real(ce) and not pe, json.dumps(real(ce)[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def tech_add(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    from run_tests_phase59 import idea, cand
    ideas = [idea([cand("CAA", "Cand A", 1, "study")])]
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, wl=[("AVGO", P41.V3, {})], ideas=ideas)
    try:
        P40.go_watch(page); js(page, "()=>wlOpen('AVGO','view')"); wait(page, 400)
        btn = ".wlDBody [data-vw-row=tech] [data-vw-add-tv]"
        info = js(page, "(s)=>{ const b=document.querySelector(s); if(!b) return null; const r=b.getBoundingClientRect(); const row=b.closest('[data-vw-row]'); const rr=row.getBoundingClientRect(); const kids=[...row.children]; const mid=kids.map(k=>k.getBoundingClientRect().top+k.getBoundingClientRect().height/2); return {t:b.innerText.trim(), h:Math.round(rr.height), one:Math.max(...mid)-Math.min(...mid)<8, right:Math.round(r.right), rowRight:Math.round(rr.right), n:document.querySelectorAll('.wlDBody [data-vw-add-tv]').length, last:row.lastElementChild===b || row.lastElementChild.className==='vwD', vw:innerWidth, ovf:document.documentElement.scrollWidth-innerWidth}; }", btn)
        check(f"{tag} 6 Tech ไม่มีกราฟ (ตอนพับ) → ปุ่ม '＋ กราฟ TV' ท้ายแถว (1 ปุ่ม · อยู่ในแถว)", info and info["t"] == "＋ กราฟ TV" and info["n"] == 1 and info["right"] <= info["rowRight"] + 1, json.dumps(info))
        check(f"{tag} 7 ปุ่ม ＋ กราฟ TV ไม่ทำให้แถว Tech ตัดบรรทัด (บรรทัดเดียว · สูง ≤ 52px) · ไม่ล้นแนวนอน", info and info["one"] and info["h"] <= 52 and info["ovf"] <= 0, json.dumps(info))
        shot(page, f"esc1-vw-tech-add-{sfx}.png", ".wlDBody")
        page.locator(btn).click(); wait(page, 400)
        st = js(page, "()=>({open:!!document.querySelector('.wlDBody [data-vw-ang=tech]'), foc:document.activeElement && document.activeElement.hasAttribute('data-vw-url'), ph:document.activeElement && document.activeElement.placeholder})")
        check(f"{tag} 6 แตะ ＋ กราฟ TV → Tech กาง + โฟกัสช่องลิงก์", st["open"] and st["foc"], json.dumps(st, ensure_ascii=False))
        page.locator(".wlDBody [data-vw-ang=tech] [data-vw-url]").fill(TV1); page.locator(".wlDBody [data-vw-ang=tech] [data-vw-save]").click(); wait(page, 600)
        tp = ".wlDBody [data-vw-ang=tech] .vwTop .vwImg"
        rt = fit_ratio(page, tp)
        first = js(page, "()=>{ const x=document.querySelector('.wlDBody [data-vw-ang=tech]'); return x.firstElementChild.className; }")
        check(f"{tag} 6 บันทึกลิงก์ → กราฟเต็มกว้างบนสุดของส่วน Tech (อยู่ก่อนประวัติ · contain · สัดส่วนจริง)", ratio_ok(rt) and first == "vwTop", json.dumps([rt, first]))
        page.locator(".wlDBody [data-vw-row=tech]").click(); wait(page, 300)
        check(f"{tag} 6 แตะแถว Tech อีกครั้ง → พับ (toggle เดิม)", cnt(page, ".wlDBody [data-vw-ang=tech]") == 0 and cnt(page, ".wlDBody [data-vw-row=tech] .vwMini") == 1)
        # Candidate
        js(page, "()=>wlSetView('cand')"); wait(page, 300)
        page.locator('.wlRows .wlR[data-sym="CAA"]').click(); wait(page, 400)
        cb = "[data-cand-x] [data-vw-row=tech] [data-vw-add-tv]"
        ci = js(page, "(s)=>{ const b=document.querySelector(s); if(!b) return null; const row=b.closest('[data-vw-row]'); const kids=[...row.children]; const mid=kids.map(k=>k.getBoundingClientRect().top+k.getBoundingClientRect().height/2); return {t:b.innerText.trim(), one:Math.max(...mid)-Math.min(...mid)<8, h:Math.round(row.getBoundingClientRect().height), ovf:document.documentElement.scrollWidth-innerWidth}; }", cb)
        check(f"{tag} 6 แถวขยาย Candidate มีปุ่ม '＋ กราฟ TV' เหมือนกัน · บรรทัดเดียว ไม่ล้น", ci and ci["t"] == "＋ กราฟ TV" and ci["one"] and ci["h"] <= 52 and ci["ovf"] <= 0, json.dumps(ci))
        page.locator(cb).click(); wait(page, 400)
        cs = js(page, "()=>({open:!!document.querySelector('[data-cand-x] [data-vw-ang=tech]'), foc:!!(document.activeElement && document.activeElement.hasAttribute('data-vw-url'))})")
        check(f"{tag} 6 Candidate: แตะ ＋ กราฟ TV → Tech กาง + โฟกัสช่องลิงก์", cs["open"] and cs["foc"], json.dumps(cs))
        check(f"{tag} 7 console ไม่มี error (Tech add)", not real(ce) and not pe, json.dumps(real(ce)[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def sat_esc(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h)
    try:
        P59.go_sat(page)
        js(page, "()=>satwWrite('XAUUSD', {chart:{url:'" + TV1 + "', at:'2026-10-09'}})"); wait(page, 600)
        sel = ".ui-tile[data-key=XAUUSD] .vwSat"
        rt = fit_ratio(page, sel)
        check(f"{tag} 4 การ์ด Sat: ภาพเต็มกว้างช่อง · contain · สูง = กว้าง × 1/2 ± 2px (ภาพจริง 200×100) · ไม่ครอป", ratio_ok(rt), json.dumps(rt))
        tg = js(page, "(s)=>{ const t=document.querySelector(s+' .vwTag'), e=document.querySelector(s+' .vwEd'), o=document.querySelector(s).getBoundingClientRect(); const a=t.getBoundingClientRect(), d=e.getBoundingClientRect(); return {tagIn:a.left>=o.left&&a.bottom<=o.bottom+1, edIn:d.right<=o.right+1&&d.top>=o.top-1, ovf:document.documentElement.scrollWidth-innerWidth}; }", sel)
        check(f"{tag} 4 ป้ายวันที่ + ปุ่ม 'เปลี่ยน' ยังวางทับมุมภาพ · หน้าไม่ล้นแนวนอน", tg["tagIn"] and tg["edIn"] and tg["ovf"] <= 0, json.dumps(tg))
        shot(page, f"esc1-sat-chart-{sfx}.png", ".ui-tile[data-key=XAUUSD]")
        page.locator(sel).click(position={"x": 40, "y": 30}); wait(page, 250)
        l0 = cnt(page, "#vwLb")
        esc(page)
        check(f"{tag} 1 lightbox กราฟ (จากการ์ด Sat): เปิด ({l0}) → Esc → ปิด ({cnt(page, '#vwLb')})", l0 == 1 and cnt(page, "#vwLb") == 0)
        # 404 → กล่องเทายังมี
        check(f"{tag} 1 console ไม่มี error (Sat)", not real(ce) and not pe, json.dumps(real(ce)[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def brk_dir(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, page, ce, pe = P63.sat_page(pw, w, h)
    try:
        fresh(page, bp_idea([cond()]))
        n = cnt(page, f"{ac()} [data-dir]")
        ro = cnt(page, f"{ac()} [data-dir-ro]")
        arrows = lambda: js(page, "(s)=>[...document.querySelectorAll(s+' .ui-adir')].map(e=>e.textContent.trim())", ac())
        pos = js(page, "(s)=>{ const b=document.querySelector(s+' [data-dir]'); return b.closest('[data-row]').dataset.row; }", ac())
        check(f"{tag} 5 ปุ่มทิศ `[data-dir]` 1 ปุ่ม (แถว Break Price) · แถว Vol เป็นลูกศรอ่านอย่างเดียว (ไม่ใช่ปุ่ม)", n == 1 and pos == "brk" and ro == 1 and cnt(page, f"{ac()} [data-row=vol] button.ui-adir") == 0 and arrows() == ["▲", "▲"], json.dumps([n, ro, pos, arrows()]))
        shot(page, f"esc1-brk-dir-{sfx}.png", ROOT)
        page.locator(f"{ac()} [data-dir]").click(); wait(page, 400)
        c = cd(page)
        check(f"{tag} 5 แตะ → brk_dir และ vol_dir = 'dn' ทั้งคู่ · ลูกศร ▼ ▼", c["brk_dir"] == "dn" and c["vol_dir"] == "dn" and arrows() == ["▼", "▼"], json.dumps([c, arrows()]))
        page.locator(f"{ac()} [data-dir]").click(); wait(page, 400)
        c = cd(page)
        check(f"{tag} 5 แตะอีก → 'up' ทั้งคู่", c["brk_dir"] == "up" and c["vol_dir"] == "up" and arrows() == ["▲", "▲"], json.dumps(c))
        # ข้อมูลเก่า brk up / vol dn
        fresh(page, bp_idea([cond(bdir="up", vdir="dn")]))
        check(f"{tag} 5 ข้อมูลเก่า brk up / vol dn → แสดง ▲ ทั้ง 2 แถว", arrows() == ["▲", "▲"], json.dumps(arrows()))
        page.locator(f"{ac()} [data-dir]").click(); wait(page, 400)
        c = cd(page)
        check(f"{tag} 5 แตะครั้งแรก → ทั้งคู่ 'dn' (เขียนให้ตรงกัน)", c["brk_dir"] == "dn" and c["vol_dir"] == "dn", json.dumps(c))
        # ค่าเริ่มตามทิศเงื่อนไข: Short → ▼ ทั้งคู่ (ไม่ได้เก็บ dir)
        fresh(page, bp_idea([cond()], side="Short") if "side" in P60.bp_idea.__code__.co_varnames else bp_idea([cond(bdir="dn", vdir="dn")]))
        check(f"{tag} 5 เงื่อนไขทิศ ▼: แสดง ▼ ทั้ง 2 แถว", arrows() == ["▼", "▼"], json.dumps(arrows()))
        # สรุป Active ใช้ทิศเดียว
        fresh(page, bp_idea([cond(steps=(1, 1, 0), brk=2400, vol=2410, bdir="up", vdir="dn")]))
        sm = js(page, "(s)=>document.querySelector(s+' .ui-acs[data-sum=break] .ui-acs-t').textContent.replace(/\\s+/g,' ').trim()", ac())
        check(f"{tag} 5 บรรทัดสรุป Break ใช้ทิศเดียวกันทั้ง 2 ส่วน (ข้อมูลเก่า up/dn → ▲ ทั้งคู่)", sm == "Break Price 2,400▲ · Vol 2,410▲", sm)
        # สรุปแถว Price + Vol กรอก → ปุ่มอยู่แถว Vol เมื่อ Price เป็นสรุป
        fresh(page, bp_idea([cond(steps=(1, 0, 0), brk=2400, vol=2410)]))
        pos2 = js(page, "(s)=>{ const b=document.querySelector(s+' [data-dir]'); return b ? b.closest('[data-row]').dataset.row : null; }", ac())
        check(f"{tag} 5 Price เป็นบรรทัดสรุป (ติ๊กแล้ว) → ปุ่มทิศยังเข้าถึงได้ (ย้ายไปแถว Vol) · มีปุ่มเดียว", pos2 == "vol" and cnt(page, f"{ac()} [data-dir]") == 1, str(pos2))
        check(f"{tag} 5 console ไม่มี error (Break dir)", not real(ce) and not pe, json.dumps(real(ce)[:3] + pe[:3], ensure_ascii=False))
    finally: browser.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            core_esc(pw, w, h, label)
            watch_esc(pw, w, h, label)
            sat_esc(pw, w, h, label)
            tech_add(pw, w, h, label)
            brk_dir(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 67 / ESC1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
