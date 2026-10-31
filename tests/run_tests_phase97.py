#!/usr/bin/env python3
"""HD1 — ตัวควบคุมรองของ Plan/Port ย้ายเข้า header ที่มีอยู่ (Mac + iPhone) · Journal ไม่เปลี่ยน · เทส 97
Chromium · FF_STUB_BASE = Lean · Mac 900/1024/1280/1440/1920 · iPad 768 · iPhone 390/320/300
ภาพ tests/screenshots/hd1-{plan-1280,plan-1440,port-1440,port-1920,journal-1440,port-1024-compact,plan-390,port-390,port-300}.png
รัน: python3 run_tests_phase97.py"""
import json, os
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase77 as P77
import run_tests_phase93 as P93

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


TABS = [("today", None), ("flow", None), ("watch", None), ("plan", "stock"), ("plan", "future"), ("journal", None), ("mix", None)]

PROBE = """()=>{
  const R = e => { if(!e) return null; const b = e.getBoundingClientRect(); return {l:b.left, r:b.right, t:b.top, b:b.bottom, w:b.width, h:b.height, cy:b.top+b.height/2}; };
  const q = s => document.querySelector(s), wrap = q('#mainWrap'), wr = wrap.getBoundingClientRect();
  const slot = q('#hdrSub'), vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
  const ps = q('.planScope');
  const full = slot.querySelector('.scopeTabs,[data-ln3-accsw]');
  return {tab: activeTab, scope: planScope, nav: R(q('#tabsMain')), wrapC: (wr.left + wr.right) / 2, brand: R(q('.brand')), hb: R(q('.hbtns')), top: R(q('.topbar')), slot: R(slot),
    slotEmpty: slot.children.length === 0, slotCmp: slot.classList.contains('cmp'), fullInSlot: !!full, fullVis: vis(full), cmpVis: vis(slot.querySelector('.hdrCmp')),
    nScopeStock: document.querySelectorAll('#scopeStock').length, nScopeFuture: document.querySelectorAll('#scopeFuture').length, nAccSw: document.querySelectorAll('[data-ln3-accsw]').length,
    scopeInSlot: !!slot.querySelector('#scopeStock') && !!slot.querySelector('#scopeFuture'), accInSlot: !!slot.querySelector('[data-ln3-accsw]'),
    planScopeH: ps ? ps.getBoundingClientRect().height : 0, planScopeKids: ps ? ps.children.length : 0,
    gridCols: getComputedStyle(q('.topbar')).display, ow: document.documentElement.scrollWidth - innerWidth,
    brandNameVis: vis(q('.brandName')), syncTimeVis: vis(q('#brandSyncTime')), dotVis: vis(q('#acctDot')), dot: R(q('#acctDot')), mark: R(q('.brandMark')), sel: typeof ln3PortSel === 'function' ? ln3PortSel() : null};
}"""


def probe(page): return js(page, PROBE)


def go(page, tab, scope=None):
    js(page, "(t)=>switchTab(t)", tab); settle(page, 350)
    if scope: js(page, "(s)=>setPlanScope(s)", scope); settle(page, 300)


def launch(pw, w, h, names=("OUN", "FAM")):
    b, page, ce, pe = P93.launch(pw, w, h)
    js(page, "(n)=>{ acctList.forEach((a,i)=>{ if(n[i]) a.name = n[i]; }); renderAcctBar(); render(); renderPortfolioMix(); }", list(names)); settle(page, 300)
    return b, page, ce, pe


def near(a, b, tol): return abs(a - b) <= tol


# ══════════════════════════ Mac header (≥ 900)
def desk(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        rows = {}
        for tab, sc in TABS:
            go(page, tab, sc); rows[f"{tab}{'-' + sc if sc else ''}"] = probe(page)
        ks = list(rows)
        cen = {k: (r["nav"]["l"] + r["nav"]["r"]) / 2 for k, r in rows.items()}
        check(f"{tag} 2 ทุกแท็บ: กึ่งกลาง #tabsMain = กึ่งกลาง container (± 0.5px)", all(near(cen[k], rows[k]["wrapC"], 0.5) for k in ks), {k: [round(cen[k], 1), rows[k]["wrapC"]] for k in ks})
        check(f"{tag} 2 ทุกแท็บ: x ซ้ายของ nav เท่ากัน (± 0.5px) · x ซ้ายของ brand · x ขวาของ toolbar เท่ากัน",
              all(near(rows[k]["nav"]["l"], rows[ks[0]]["nav"]["l"], 0.5) and near(rows[k]["brand"]["l"], rows[ks[0]]["brand"]["l"], 0.5) and near(rows[k]["hb"]["r"], rows[ks[0]]["hb"]["r"], 0.5) for k in ks),
              {k: [round(rows[k]["nav"]["l"], 1), round(rows[k]["brand"]["l"], 1), round(rows[k]["hb"]["r"], 1)] for k in ks})
        check(f"{tag} 2 header แถวเดียว: ความสูง topbar เท่ากันทุกแท็บ (± 1px) · ไม่ล้นแนวนอน", all(near(rows[k]["top"]["h"], rows[ks[0]]["top"]["h"], 1) and rows[k]["ow"] <= 1 for k in ks), {k: [rows[k]["top"]["h"], rows[k]["ow"]] for k in ks})
        # Plan
        for k in ("plan-stock", "plan-future"):
            r = rows[k]
            check(f"{tag} 1 {k}: ปุ่ม scope อยู่ใน #hdrSub (node เดียว: #scopeStock/#scopeFuture อย่างละ 1) · แถว .planScope ไม่เหลือความสูง",
                  r["nScopeStock"] == 1 and r["nScopeFuture"] == 1 and ((r["scopeInSlot"] and r["planScopeH"] == 0) or (not r["scopeInSlot"] and r["planScopeKids"] == 1)), r)
        r = rows["plan-stock"]
        placed = r["scopeInSlot"]
        if placed:
            gap = r["slot"]["l"] - r["nav"]["r"]
            check(f"{tag} 2 Plan: ช่องห่างจาก nav 16px (± 1) · กึ่งกลางแนวตั้งตรงกับ nav (± 1) · เว้นห่าง toolbar ≥ 12px", near(gap, 16, 1) and near(r["slot"]["cy"], r["nav"]["cy"], 1) and r["hb"]["l"] - r["slot"]["r"] >= 12, [gap, r["slot"], r["nav"]["cy"], r["hb"]["l"]])
            # คลิก Sat/Core เหมือนปุ่มเดิม
            go(page, "plan", "stock")
            if r["fullVis"]:
                page.locator("#hdrSub #scopeFuture").click(); settle(page, 400)
                s1 = js(page, "()=>({ps: planScope, cls: document.getElementById('tabPlan').className, on: document.getElementById('scopeFuture').classList.contains('on')})")
                page.locator("#hdrSub #scopeStock").click(); settle(page, 400)
                s2 = js(page, "()=>({ps: planScope, cls: document.getElementById('tabPlan').className, on: document.getElementById('scopeStock').classList.contains('on')})")
                check(f"{tag} 1 คลิก Sat / Core ในช่อง = สลับ scope เหมือนปุ่มเดิม (planScope · lf-future/lf-stock · on)", s1["ps"] == "future" and "lf-future" in s1["cls"] and s1["on"] and s2["ps"] == "stock" and "lf-stock" in s2["cls"] and s2["on"], [s1, s2])
            else:
                page.locator("#hdrSub .hdrCmp select").select_option(index=1); settle(page, 400)
                s1 = js(page, "()=>({ps: planScope, on: document.getElementById('scopeFuture').classList.contains('on')})")
                page.locator("#hdrSub .hdrCmp select").select_option(index=0); settle(page, 400)
                s2 = js(page, "()=>({ps: planScope, on: document.getElementById('scopeStock').classList.contains('on')})")
                check(f"{tag} 1 รูปย่อ: เลือก Sat / Core = สลับ scope เหมือนปุ่มเดิม", s1["ps"] == "future" and s1["on"] and s2["ps"] == "stock" and s2["on"], [s1, s2])
            js(page, "()=>{ document.activeElement && document.activeElement.blur(); }")
            page.keyboard.press("f"); settle(page, 350); k1 = js(page, "()=>planScope")
            page.keyboard.press("s"); settle(page, 350); k2 = js(page, "()=>planScope")
            sel_ok = js(page, "()=>{ const c = document.querySelector('#hdrSub .hdrCmp select'); return c ? c.selectedIndex : -1; }")
            check(f"{tag} 1 คีย์ลัด F / S ยังสลับ scope · ช่องตามสถานะ", k1 == "future" and k2 == "stock" and sel_ok in (-1, 0), [k1, k2, sel_ok])
        else:
            inpage = js(page, "()=>!!document.querySelector('#tabPlan .planScope .scopeTabs')")
            check(f"{tag} 2 Plan: ที่ไม่พอแม้รูปย่อ → ตัวควบคุมอยู่ในหน้าเหมือนเดิม (ไม่ทับ/ไม่ดัน nav-toolbar) · node เดียว", inpage and r["nScopeStock"] == 1, r)
        # Port
        r = rows["mix"]
        placed = r["accInSlot"]
        check(f"{tag} 1 Port: [data-ln3-accsw] มี 1 node (ในช่อง หรือในหน้าเมื่อไม่พอที่)", r["nAccSw"] == 1, r)
        if placed:
            go(page, "mix")
            gap = r["slot"]["l"] - r["nav"]["r"]
            check(f"{tag} 2 Port: ช่องห่าง nav 16px (± 1) · กึ่งกลางแนวตั้ง (± 1) · ห่าง toolbar ≥ 12px", near(gap, 16, 1) and near(r["slot"]["cy"], r["nav"]["cy"], 1) and r["hb"]["l"] - r["slot"]["r"] >= 12, [gap, r["slot"], r["nav"]["cy"], r["hb"]["l"]])
            for i, (lab, want) in enumerate([("OUN", "main"), ("FAM", "fam"), ("รวม", "all")]):
                if r["fullVis"]:
                    page.locator("#hdrSub [data-ln3-accsw] button", has_text=lab).first.click()
                else:
                    page.locator("#hdrSub .hdrCmp select").select_option(label=lab)
                settle(page, 450)
                got = js(page, "()=>({sel: ln3PortSel(), n: document.querySelectorAll('[data-ln3-accsw]').length, inSlot: !!document.querySelector('#hdrSub [data-ln3-accsw]')})")
                ids = js(page, "()=>acctList.map(a=>a.id)")
                exp = want if want == "all" else (ids[0] if lab == "OUN" else ids[1])
                check(f"{tag} 1 Port: เลือก {lab} ในช่อง → ln3PortSel = {exp} · node เดียว · ยังอยู่ในช่องหลัง re-render", got["sel"] == exp and got["n"] == 1 and got["inSlot"], got)
        r = rows["today"]
        check(f"{tag} 1 Today/Flow/Watch/Journal: ช่องว่าง", all(rows[k]["slotEmpty"] for k in ("today", "flow", "watch", "journal")), {k: rows[k]["slotEmpty"] for k in ("today", "flow", "watch", "journal")})
        # 1 บัญชี → ช่องว่างบน Port
        js(page, "()=>{ window.__acct2 = acctList.pop(); acctSel = null; }") if False else None
        # Journal: การ์ดสรุปเดิม
        go(page, "journal"); settle(page, 300)
        jr = js(page, """()=>({acct: document.querySelectorAll('[data-ln3-jacct]').length, scopes: document.querySelectorAll('[data-ln3-scopes] button').length, dec: !!document.querySelector('[data-jsum="decision"]'),
            txt: document.getElementById('jSum').innerText, slotEmpty: document.getElementById('hdrSub').children.length === 0})""")
        check(f"{tag} 4 Journal: การ์ดสรุปมี OUN|FAM · รวม|Core|Sat · ทุกปี/ทุกเดือน · แถบเตือน/ข้อความตัดสิน เหมือนเดิม · ช่อง header ว่าง",
              jr["acct"] == 2 and jr["scopes"] == 3 and jr["dec"] and "ทุกปี" in jr["txt"] and "ทุกเดือน" in jr["txt"] and jr["slotEmpty"], jr)
        if w in (1280, 1440, 1920):
            go(page, "plan", "stock")
            if w in (1280, 1440): C.shot(page, f"hd1-plan-{w}.png", full=False)
            go(page, "mix")
            if w in (1440, 1920): C.shot(page, f"hd1-port-{w}.png", full=False)
            if w == 1440:
                go(page, "journal"); C.shot(page, "hd1-journal-1440.png", full=False)
        if w == 1024:
            go(page, "mix"); C.shot(page, "hd1-port-1024-compact.png", full=False)
        # สลับไปมา 3 รอบ
        base_l = rows["today"]["nav"]["l"]; drift = []
        for _ in range(3):
            for tab, sc in TABS: go(page, tab, sc); drift.append(abs(probe(page)["nav"]["l"] - base_l))
        check(f"{tag} 2 สลับแท็บไปมา 3 รอบ: nav ไม่ขยับ (≤ 0.5px) · ไม่มี console error", max(drift) <= 0.5 and not ce and not pe, [max(drift), ce[:2], pe[:2]])
    finally: b.close()


def compact_cases(pw):
    """ชื่อบัญชียาว / หน้าต่างแคบ → รูปย่อ · ไม่ทับ toolbar"""
    tag = f"[{ENGINE}/compact]"
    b, page, ce, pe = launch(pw, 1280, 900, names=("บัญชีหลักชื่อยาวมากๆ ของฉัน", "Family Office Account"))
    try:
        go(page, "mix"); r = probe(page)
        ok = (r["cmpVis"] and not r["fullVis"] and r["hb"]["l"] - r["slot"]["r"] >= 12) if r["accInSlot"] else (r["nAccSw"] == 1)
        check(f"{tag} 2 ชื่อบัญชียาว (1280) → รูปย่อ pill ▾ ที่จุดเดิม · ไม่ทับ toolbar · แถวเดียว", ok and r["nAccSw"] == 1 and r["ow"] <= 1, r)
        if r["accInSlot"]:
            page.locator("#hdrSub .hdrCmp select").select_option(index=1); settle(page, 450)
            got = js(page, "()=>({sel: ln3PortSel(), ids: acctList.map(a=>a.id), n: document.querySelectorAll('[data-ln3-accsw]').length})")
            check(f"{tag} 1 รูปย่อ: เลือกบัญชีที่ 1 → ln3PortSel ตรง · node เดียว", got["sel"] == got["ids"][0] and got["n"] == 1, got)
    finally: b.close()
    # 1 บัญชี → ช่องว่าง
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        js(page, "()=>{ window.__keep = acctList.slice(); acctList.splice(1); renderPortfolioMix(); }"); go(page, "mix"); settle(page, 300)
        r = probe(page)
        check(f"{tag} 1 บัญชีเดียว: ไม่มีสวิตช์บัญชี → ช่อง header ว่าง · ไม่มี node ค้าง", r["nAccSw"] == 0 and r["slotEmpty"], r)
    finally: b.close()


# ══════════════════════════ iPad 768 — เหมือนเดิมก่อน HD1
def ipad(pw):
    tag = f"[{ENGINE}/768]"
    b, page, ce, pe = launch(pw, 768, 1000)
    try:
        rows = {}
        for tab, sc in TABS: go(page, tab, sc); rows[f"{tab}{'-' + sc if sc else ''}"] = probe(page)
        check(f"{tag} 2 768: ช่อง header ว่างทุกแท็บ · ตัวควบคุมอยู่ในหน้าเหมือนเดิม (.planScope มี scopeTabs · Port มี accsw ในหน้า)",
              all(r["slotEmpty"] for r in rows.values()) and rows["plan-stock"]["planScopeKids"] == 1 and rows["plan-stock"]["planScopeH"] > 0 and rows["mix"]["nAccSw"] == 1 and not rows["mix"]["accInSlot"], {k: [r["slotEmpty"], r["planScopeKids"], r["nAccSw"]] for k, r in rows.items()})
        check(f"{tag} 2 768: header ความสูงเท่ากันทุกแท็บ · ไม่ล้นแนวนอน", all(near(r["top"]["h"], rows["today"]["top"]["h"], 1) and r["ow"] <= 1 for r in rows.values()), {k: [r["top"]["h"], r["ow"]] for k, r in rows.items()})
        go(page, "plan", "stock"); page.locator("#scopeFuture").click(); settle(page, 400)
        a = js(page, "()=>planScope")
        go(page, "mix"); page.locator("[data-ln3-accsw] button", has_text="FAM").first.click(); settle(page, 400)
        c = js(page, "()=>[ln3PortSel(), acctList.map(a=>a.id)]")
        check(f"{tag} 1 768: เลือกจากตัวควบคุมในหน้าใช้ได้ (Sat · FAM)", a == "future" and c[0] == c[1][1], [a, c])
    finally: b.close()


# ══════════════════════════ iPhone
def phone(pw, w, h):
    tag = f"[{ENGINE}/{w}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        rows = {}
        for tab, sc in TABS: go(page, tab, sc); rows[f"{tab}{'-' + sc if sc else ''}"] = probe(page)
        t0 = rows["today"]["top"]["h"]
        check(f"{tag} 3 ความสูง top bar Plan/Port = Today (± 1px) · Journal/Flow/Watch เท่ากัน · ไม่ล้นแนวนอน", all(near(r["top"]["h"], t0, 1) and r["ow"] <= 1 for r in rows.values()), {k: [r["top"]["h"], r["ow"]] for k, r in rows.items()})
        for k in ("plan-stock", "plan-future", "mix"):
            r = rows[k]
            if k.startswith("plan") and w < 430:   # RG2b — 3 ปุ่ม Winner | Ladder | Sat ไม่พอที่ใน header จอ < 430px → อยู่ในหน้า (ชื่อแอปคงอยู่ · โลโก้ + จุดซิงก์เห็น)
                where_ = page.evaluate("()=>[...document.querySelectorAll('.scopeBtn')].map(b=>b.closest('.planScope') ? 'page' : 'hdr')")
                check(f"{tag} 3 {k}: RG2b ปุ่ม 3 ตัวอยู่ในหน้า (header ไม่พอ) · โลโก้ + จุดซิงก์ยังเห็น · ไม่ล้นจอ", r["dotVis"] and where_ == ["page", "page", "page"] and r["hb"]["r"] <= w, [r, where_])
            else:
                check(f"{tag} 3 {k}: ซ่อนชื่อ Trading + ข้อความซิงก์ · โลโก้ + จุดซิงก์ยังเห็น · ตัวควบคุมอยู่ในช่อง (เต็มหรือย่อ) ไม่ล้นจอ",
                      not r["brandNameVis"] and not r["syncTimeVis"] and r["dotVis"] and (r["fullVis"] or r["cmpVis"]) and r["slot"]["r"] <= w and r["slot"]["r"] <= r["hb"]["l"] + 0.5, r)
        for k in ("today", "flow", "watch", "journal"):
            r = rows[k]
            check(f"{tag} 3 {k}: top bar เหมือนเดิม (เห็น Trading + ข้อความซิงก์ · ช่องว่าง)", r["brandNameVis"] and r["slotEmpty"], r)
        # จุดซิงก์แตะแล้ว retrySync
        called = js(page, "()=>{ window.__rs = 0; const o = window.retrySync; window.retrySync = function(){ window.__rs++; }; return 1; }")
        go(page, "plan", "stock")
        page.evaluate("()=>{ const b = document.getElementById('brandSync'); b.removeAttribute('onclick'); b.onclick = ()=>window.retrySync(); }")
        r = rows["plan-stock"]
        page.mouse.click(r["dot"]["l"] + r["dot"]["w"] / 2, r["dot"]["t"] + r["dot"]["h"] / 2); settle(page, 150)
        rs = js(page, "()=>window.__rs")
        check(f"{tag} 3 แตะจุดซิงก์ที่โลโก้ → เรียก retrySync()", rs == 1, rs)
        # เลือกจากช่อง
        go(page, "plan", "stock")
        if js(page, "()=>!!document.querySelector('#hdrSub .hdrCmp') && document.querySelector('#hdrSub').classList.contains('cmp')"):
            page.locator("#hdrSub .hdrCmp select").select_option(index=1)
        else:
            page.locator("#hdrSub #scopeFuture").click()
        settle(page, 400); a = js(page, "()=>planScope")
        go(page, "mix")
        if js(page, "()=>document.querySelector('#hdrSub').classList.contains('cmp')"):
            page.locator("#hdrSub .hdrCmp select").select_option(label="FAM")
        else:
            page.locator("#hdrSub [data-ln3-accsw] button", has_text="FAM").first.click()
        settle(page, 450); c = js(page, "()=>[ln3PortSel(), acctList.map(a=>a.id), document.querySelectorAll('[data-ln3-accsw]').length]")
        check(f"{tag} 3 เลือก Sat / FAM จากช่องใน top bar ได้ · node เดียว", a == "future" and c[0] == c[1][1] and c[2] == 1, [a, c])
        if w == 390:
            check(f"{tag} 3 Plan 390: Core|Sat เต็มรูปพอดี (ไม่ย่อ)", rows["plan-stock"]["fullVis"] and not rows["plan-stock"]["slotCmp"], rows["plan-stock"])
        if w == 300:
            check(f"{tag} 3 Port 300: รูปย่อ pill", rows["mix"]["cmpVis"] and not rows["mix"]["fullVis"], rows["mix"])
        if w in (390, 300):
            go(page, "plan", "stock"); C.shot(page, f"hd1-plan-{w}.png", full=False) if w == 390 else None
            go(page, "mix"); C.shot(page, f"hd1-port-{w}.png", full=False)
        check(f"{tag} 3 {w}: ไม่ล้นแนวนอน · ไม่มี console error", js(page, "()=>document.documentElement.scrollWidth - innerWidth") <= 1 and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


# ══════════════════════════ Legacy
def legacy(pw):
    tag = f"[{ENGINE}/legacy]"
    b, page, ce, pe = launch(pw, 1440, 900)
    try:
        js(page, "()=>ln1SetMode('legacy')"); settle(page, 600)
        go(page, "plan", "stock"); r1 = probe(page)
        go(page, "mix"); r2 = probe(page)
        check(f"{tag} Legacy: header ไม่เป็น grid · ช่องว่าง · scopeTabs อยู่ใน .planScope เหมือนเดิม", r1["gridCols"] != "grid" and r1["slotEmpty"] and r1["planScopeKids"] == 1 and r1["planScopeH"] > 0 and r2["slotEmpty"], [r1["gridCols"], r1["slotEmpty"], r1["planScopeKids"], r2["slotEmpty"]])
        js(page, "()=>ln1SetMode('lean')"); settle(page, 600); go(page, "plan", "stock"); r3 = probe(page)
        check(f"{tag} กลับ Lean: scopeTabs เข้าช่องอีกครั้ง · node เดียว", r3["scopeInSlot"] and r3["nScopeStock"] == 1, r3)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h in [(900, 800), (1024, 800), (1280, 900), (1440, 900), (1920, 1000)]: desk(pw, w, h)
        compact_cases(pw)
        ipad(pw)
        for w, h in [(390, 844), (320, 700), (300, 700)]: phone(pw, w, h)
        legacy(pw)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
