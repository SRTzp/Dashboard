#!/usr/bin/env python3
"""LN3fix §1 — แผน Core แบบ Lean: ปุ่ม Core|Sat · กล่องมืดกล่องเดียว · การ์ดแถว 2 บรรทัด · ⋯ (ปิด/แก้/ยกเลิก/ลบ) · ฟอร์มแผนใหม่ (บัญชีบอกตลาด · ใช่|ไม่ · ยังไม่ตอบ n · Winners|Ladder · ยกเลิก) · เทส 89
mock Firestore · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3fix-core-{1440,390}.png · ln3fix-core-form-{1440,390}.png
รัน: python3 run_tests_phase89.py"""
import json, os, re
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as P24
import run_tests_phase26 as P26

ENGINE = base.BROWSER_ENGINE
CS1_RETIRED = True   # CS1 — ส่วนที่ทดสอบ UI ประเมิน Tier/Risk % แก้ได้ในฟอร์มแผน (ถูกถอดตามบรีฟ) · ดู tests/CS1_retired.md
results = []
js = C.js
overflow = C.overflow


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def txt(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def vis(page, sel):
    return js(page, "(s)=>{ const e=document.querySelector(s); if(!e) return false; const r=e.getBoundingClientRect(); return getComputedStyle(e).display!=='none' && r.width>0 && r.height>0; }", sel)


def mut_both(doc):
    doc["books"]["main"]["settings"].setdefault("coreRisk", {})["market"] = "both"
    doc["books"]["fam"]["settings"].setdefault("coreRisk", {})["market"] = "TH"


def fill_tier(page, strong=True):
    """Fortress ผ่านครบ · Growth ไม่ผ่าน (ยังไม่ตอบ netcash)"""
    for i, v in (("tiRoic", "18"), ("tiNd", "0.8"), ("tiFcf", "92"), ("tiRev", "12"), ("tiCagr", "16"), ("tiOpm", "34"), ("tiOpmPrev", "31")):
        page.fill("#" + i, v)
    js(page, "()=>{ coreTiTk('fcf3y',true); coreTiTk('capret',true); coreTiTk('ocf',true); coreTiG5('substitute',false); coreTiG5('customerMigrating',false); coreTiG5('singleProduct',false); }")
    page.wait_for_timeout(200)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ───────── 1 หน้า Core: ปุ่ม · ตัดส่วนเดิมออก · กล่องเดียว
    b, page, ce, pe = C.launch(pw, w, h, mut=mut_both)
    try:
        C.go_core(page)
        sw = js(page, "()=>({a: document.getElementById('scopeStock').innerText.trim(), b: document.getElementById('scopeFuture').innerText.trim(), onA: document.getElementById('scopeStock').classList.contains('on')})")
        check(f"{tag} 1 บนสุดปุ่ม 'Core | Sat' (ไม่มี 'Port หุ้น / Port Future') · Core ติดอยู่", sw["a"] == "Winner" and sw["b"] == "Sat" and sw["onA"], sw)   # RG2b — ปุ่มสามตัว Winner | Ladder | Sat
        gone = js(page, """()=>({strip: !!document.querySelector('#strip') && document.querySelector('#strip').offsetParent!==null, ports: document.getElementById('ports').children.length,
          pos: !!document.getElementById('posPanel') && document.getElementById('posPanel').offsetParent!==null, foot: document.getElementById('foot').offsetParent!==null,
          sum: document.querySelectorAll('#tabPlan [data-sum]').length, bar4: document.querySelectorAll('#tabPlan .sumBar4').length,
          hold: /Hold\\s/.test(document.getElementById('tabPlan').innerText), heat: /heat:/.test(document.getElementById('tabPlan').innerText),
          legacyHead: document.querySelectorAll('#corePanel [data-core-head]').length})""")
        check(f"{tag} 1 ตัดออก: การ์ดบัญชี Hold/Plan · กล่อง 4 ช่อง · ชิปต่อบัญชี · Positions · บรรทัด heat ท้ายหน้า", not gone["strip"] and gone["ports"] == 0 and not gone["pos"] and not gone["foot"] and gone["sum"] == 0 and gone["bar4"] == 0 and not gone["hold"] and not gone["heat"] and gone["legacyHead"] == 0, gone)
        box = js(page, "()=>({n: document.querySelectorAll('[data-lf-box]').length, cap: document.querySelector('[data-lf-cap]').innerText.trim()})")
        check(f"{tag} 1 กล่องมืดกล่องเดียว: 'Core' + 'ทุน ฿4.2M'", box["n"] == 1 and box["cap"] == "ทุน ฿9.6M", box)   # LN3fix3c §4: หัว Core = ทุนรวมทุกบัญชี (2 × ฿4.2M)   # LN3fix2 §2: ตัด '% ของพอร์ต'
        sh = vis(page, "[data-lf-sidehint]")
        check(f"{tag} 1 ไม่มีฟอร์มเปิด: " + ("Mac คอลัมน์ขวามีการ์ดเล็ก 'ยังไม่ได้เปิดฟอร์มแผน Core' + ปุ่ม ＋ แผน Core" if w >= 1000 else "มือถือไม่มีการ์ดว่าง"), sh == (w >= 1000), sh)
        # ตัวเลข = ค่าเดิม
        ref = js(page, """()=>{ const A='main', rk = coreAcctRisk(A), cx = coreCtx(A), cfg = cx.cfg, sp = cx.split, tank = cx.tankTHB;
          return {now: fmt2(rk.layer2Pct)+'%', lim: fmt2(cfg.l2Cap)+'%', full: fmt2(rk.layer2FullPct)+'%', wPct: fmt2(cx.wCost/tank*100), lPct: fmt2(sp.lPct*100), lcap: fmt2(cfg.ladderShare),
            free: '฿'+fmt0(sp ? tank-cx.wCost-sp.lUsed : tank-cx.held), ff: Math.round(cx.F.f*100)+'%', dd: fmt2(Math.round(ddEval(A,'core').ddPct*100)/100)+'%'}; }""")
        got = js(page, "()=>({now: document.querySelector('[data-lf-row=main] [data-lf-now]').innerText.trim(), lim: document.querySelector('[data-lf-row=main] [data-lf-lim]').innerText.trim(), full: document.querySelector('[data-lf-full]').textContent.trim(), wp: document.querySelector('[data-lf-wpct]').textContent.trim(), lp: document.querySelector('[data-lf-lpct]').textContent.trim(), more: document.querySelector('[data-lf-more]').textContent.replace(/\\s+/g,' '), line: document.querySelector('[data-lf-row=main] [data-lf-line]').innerText.replace(/\\s+/g,' ').trim(), free: +document.querySelector('[data-lf-row=main] [data-lf-free]').dataset.lfFree})")
        ok = got["now"] == ref["now"] and got["lim"] == ref["lim"] and got["full"] == ref["full"] and got["wp"] == ref["wPct"] + "%" and got["lp"] == ref["lPct"] and f"Ladder {ref['lPct']}/{ref['lcap']}%" in got["more"] and abs(got["free"] - float(ref["free"].replace("฿", "").replace(",", ""))) <= 1 and f"DD {ref['dd']}" in got["line"] and f"FF" in got["line"] and ref["ff"] in got["line"]
        check(f"{tag} 1 ตัวเลขเดียวกับของเดิม: Risk ชั้น 2 ตอนนี้/เต็ม/เพดาน · เงินว่าง · DD · FF (Winners/Ladder/เต็ม อยู่ในพับ · LN3fix2 §2)", ok, [ref, got])
        # ขาดราคา
        al = js(page, "()=>[...document.querySelectorAll('[data-lf-alert]')].map(e=>({k:e.dataset.lfAlert, t:e.innerText.replace(/\\s+/g,' ').trim()}))")
        miss = [a for a in al if a["k"] == "missing"]
        check(f"{tag} 1 แถบเตือน 'ขาดราคา 1 ตัว (NVDA) — ไม่นับใน Risk · อัปเดตราคา ›' เฉพาะเมื่อมี", len(miss) == 1 and "ขาดราคา 1 ตัว (NVDA)" in miss[0]["t"] and "ไม่นับใน Risk" in miss[0]["t"] and "อัปเดตราคา" in miss[0]["t"], al)
        js(page, "()=>{ const t = posThaiToday(); coreWrite('ccNV', {px: 130, pxDate: t, emaW: 120}); }"); page.wait_for_timeout(700)
        al2 = js(page, "()=>[...document.querySelectorAll('[data-lf-alert=missing]')].length")
        now2 = js(page, "()=>+document.querySelector('[data-lf-row=main] [data-lf-now]').innerText.replace('%','')")
        check(f"{tag} 1 มีราคาแล้ว → แถบขาดราคาหาย · Risk ชั้น 2 นับ NVDA (ตอนนี้ > 0)", al2 == 0 and now2 > 0, [al2, now2])
        # พับรายละเอียด
        js(page, "()=>document.querySelector('[data-lf-det]').open = true"); page.wait_for_timeout(200)
        det = txt(page, "[data-lf-det]")
        check(f"{tag} 1 พับ 'รายละเอียดและกฎ': ตำแหน่ง · Ladder ใหม่/ประตู · เพดานต่อตัว · Stop ฉุกเฉิน · ถ้าทุกไม้โดน Stop บัญชีลด", all(k in det for k in ("ตำแหน่ง 1 ตัว", "Ladder ใหม่:", "เพดานต่อตัว", "Stop ฉุกเฉิน", "ถ้าทุกไม้โดน Stop บัญชีลด", "ล็อกกำไร")), det[:400])
        js(page, "()=>document.querySelector('[data-lf-det]').open = false")
        # สลับบัญชี + จำค่า
        js(page, "()=>document.querySelector('[data-lf-acc=fam]').click()"); page.wait_for_timeout(500)
        st = js(page, "()=>({box: document.querySelector('[data-lf-box]').dataset.lfBox, ls: localStorage.getItem('lf_core_acc'), tk: [...document.querySelectorAll('#corePanel [data-c-ticker]')].map(e=>e.innerText), on: document.querySelector('[data-lf-acc].on').dataset.lfAcc})")
        check(f"{tag} 1 ปุ่มเลือกบัญชี (สีบัญชี): Family → กล่อง+การ์ดเปลี่ยน · จำค่าใน localStorage", st["box"] == "fam" and st["ls"] == "fam" and st["tk"] == [] and st["on"] == "fam", st)
        js(page, "()=>document.querySelector('[data-lf-acc=main]').click()"); page.wait_for_timeout(500)
        # การ์ดแถว 2 บรรทัด
        rows = js(page, "()=>[...document.querySelectorAll('#corePanel .ccRow')].map(r=>({t: r.querySelector('[data-c-ticker]').innerText, tag: (r.querySelector('[data-lf-tag]')||{innerText:''}).innerText, l2: (r.querySelector('[data-lf-l2]')||{innerText:''}).innerText}))")
        nv = next((r for r in rows if r["t"] == "NVDA"), {}); av = next((r for r in rows if r["t"] == "AVGO"), {})
        check(f"{tag} 1 การ์ด 2 บรรทัด: NVDA 'A · Winners' + 'ไม้ 1 · SL 115' · AVGO 'B · Winners' + 'แผน · 300 / 270 · ไม้แรก 17 หุ้น'",
              nv.get("tag") == "A · Winners" and nv.get("l2") == "ไม้ 1 · SL 115" and av.get("tag") == "B · Winners" and av.get("l2") == "แผน · 300 / 270 · ไม้แรก 17 หุ้น", rows)
        hdr = txt(page, "[data-lf-ch]")
        check(f"{tag} 1 หัว 'การ์ด Core · 2 ตัว · ＋ แผน Core' · ขยาย/ยุบทั้งหมดคงไว้", hdr is not None and "การ์ด Core" in hdr and "2 ตัว" in hdr and "＋ แผน Core" in hdr and vis(page, "[data-c-expandall]") and vis(page, "[data-c-collapseall]"), hdr)
        # กางการ์ด
        js(page, "()=>coreAll('main', 1)"); page.wait_for_timeout(300)
        body = js(page, "()=>document.querySelector('[data-core-card=ccNV]').innerText.replace(/\\s+/g,' ')")
        keys = ("ราคา · EMA10", "ขนาด · เสี่ยง", "Base 10 @128 SL 115", "อัปเดตราคา", "เติมไม้", "เลื่อน Stop")   # LN3fix2 §2: การ์ดกางตัวเลขน้อย
        check(f"{tag} 1 กางการ์ด: ราคา·EMA10 · ขนาด·เสี่ยง · Base n @ทุน SL · ปุ่ม (ตัวเลขน้อย)", all(k in body for k in keys), [k for k in keys if k not in body])
        btn = js(page, "()=>({px: document.querySelector('[data-core-card=ccNV] [data-c-px-btn]').className, order: [...document.querySelectorAll('[data-core-card=ccNV] .ccBtns > button')].map(b=>b.innerText.trim())})")
        check(f"{tag} 1 ปุ่มหลัก 'อัปเดตราคา' (primary) · 'เติมไม้' · 'เลื่อน Stop' · ⋯", "pri" in btn["px"] and btn["order"][:3] == ["อัปเดตราคา", "เติมไม้", "เลื่อน Stop"] and btn["order"][-1] == "⋯", btn)
        C.shot(page, f"ln3fix-core-{sfx}.png", full=False) if w in (1440, 390) else None
        js(page, "()=>coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null)"); page.wait_for_timeout(200)
        menu = js(page, "()=>[...document.querySelectorAll('[data-core-card=ccNV] .ccMenu button')].map(b=>b.innerText.trim())")
        need = ["ปิด/ขาย", "แก้ Entry/SL", "ยกเลิก", "ลบ"]
        js(page, "()=>{ const c = coreCardsList.find(x=>x.id==='ccNV'); coreWrite('ccNV', {stopHistory: [{date: '2026-09-20', from: 110, to: 115}], stop: 115}); }"); page.wait_for_timeout(600)
        js(page, "()=>{ coreAll('main',1); coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null); }"); page.wait_for_timeout(300)
        menu = js(page, "()=>[...document.querySelectorAll('[data-core-card=ccNV] .ccMenu button')].map(b=>b.innerText.trim())")
        check(f"{tag} 1 ⋯ มี 'ประวัติ Stop (n)' · กดแล้วเห็นตาราง วันที่/จาก/เป็น", "ประวัติ Stop (1)" in menu, menu)
        js(page, "()=>document.querySelector('[data-core-card=ccNV] [data-c-stophist]').click()"); page.wait_for_timeout(400)
        sh2 = txt(page, "[data-c-stophist-tbl]")
        check(f"{tag} 1 ประวัติ Stop แสดง '2026-09-20 110 115'", sh2 is not None and "2026-09-20" in sh2 and "110" in sh2 and "115" in sh2, sh2)
        js(page, "()=>coreSheetClose()")
        js(page, "()=>{ coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null); }"); page.wait_for_timeout(200)
        check(f"{tag} 1 ⋯ ของการ์ด: ปิด/ขาย · แก้ · ยกเลิก · ลบ (+ ดูไม้ที่ซื้อ · Tier… · เปลี่ยนกลยุทธ์)", all(n in menu for n in need) and any(m.startswith("ดูไม้ที่ซื้อ") for m in menu) and "Tier…" in menu, menu)
        # ปิดไม้ผ่าน ⋯ = ผลเดียวกับ Positions เดิม
        js(page, "()=>document.querySelector('[data-core-card=ccNV] [data-c-close-btn]').click()"); page.wait_for_timeout(500)
        cp = js(page, "()=>({open: document.getElementById('closePosOverlay').classList.contains('show'), info: (document.getElementById('cpInfo')||{innerText:''}).innerText})")
        check(f"{tag} 1 ⋯ › ปิด/ขาย เปิดหน้าต่างปิดไม้เดิมของ NVDA (openClosePos)", cp["open"] and "NVDA" in cp["info"], cp)
        js(page, "()=>{ document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show')); }")
        def closed_result(mode):
            b2, p2, ce2, pe2 = C.launch(pw, w, h, mut=mut_both)
            try:
                js(p2, "(m)=>{ ln1SetMode(m); switchTab('plan'); setPlanScope('stock'); render(); }", mode); p2.wait_for_timeout(500)
                js(p2, "()=>{ const t = getBook('main').trades.find(x=>x.sym==='NVDA'); openClosePos(t.id,'main'); }"); p2.wait_for_timeout(400)
                p2.fill("#cpExitPrice", "140"); p2.wait_for_timeout(150)
                js(p2, "()=>confirmClosePos()"); p2.wait_for_timeout(700)
                return js(p2, "()=>{ const t = getBook('main').trades.find(x=>x.sym==='NVDA'); const c = coreCardsList.find(x=>x.id==='ccNV'); return {st: t.status, exit: t.exitPrice, card: c.status}; }")
            finally: b2.close()
        # (ผ่านปุ่มเมนู = เรียก openClosePos เดียวกัน → ผลปิดเท่ากับแบบเดิม)
        rl, rg = closed_result("lean"), closed_result("legacy")
        check(f"{tag} 1 ปิดไม้ Core ผ่าน ⋯ (Lean) = ผลเดียวกับ Positions เดิม: ไม้ closed @140 · การ์ด closed", rl == rg and rl["st"] == "closed" and rl["exit"] == 140, [rl, rg])
        js(page, "()=>{ coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null); document.querySelector('[data-core-card=ccNV] [data-c-lcancel-pos]').click(); }"); page.wait_for_timeout(400)
        lk = txt(page, "[data-c-link-msg]")
        check(f"{tag} 1 ⋯ › ยกเลิก → sheet ยืนยัน 'ยกเลิกไม้ NVDA จะปิดการ์ด Core NVDA ด้วย' (เหมือน Positions เดิม)", lk is not None and "ยกเลิกไม้ NVDA" in lk and "ปิดการ์ด Core NVDA" in lk, lk)
        js(page, "()=>coreSheetClose()")
        js(page, "()=>{ coreMenuToggle(document.querySelector('[data-core-card=ccNV] [data-c-more]'), null); document.querySelector('[data-core-card=ccNV] [data-c-del-pos]').click(); }"); page.wait_for_timeout(400)
        lk2 = txt(page, "[data-c-link-msg]")
        check(f"{tag} 1 ⋯ › ลบ → sheet ยืนยัน 'ลบไม้ NVDA จะปิดการ์ด Core NVDA ด้วย'", lk2 is not None and "ลบไม้ NVDA" in lk2, lk2)
        js(page, "()=>coreSheetClose()")
        # คำ
        ct = js(page, "()=>document.getElementById('corePanel').innerText")
        bad = re.findall(r"(?:(?<=[\s(·/])|^)[WL](?=[\s·/)]|$)|บันได|ทั้งคู่", ct)
        check(f"{tag} 1 โหมด Lean ไม่มีคำ 'W' / 'L' / 'บันได' / 'ทั้งคู่' ในหน้าแผน Core", not bad, bad)
        ov = js(page, "()=>{ const W = innerWidth, bad = []; document.querySelectorAll('#corePanel *').forEach(e=>{ if(e.closest('table, .tablewrap, pre, .ccMenu')) return; const r = e.getBoundingClientRect(); if(r.width>0 && r.right > W + 1) bad.push(e.className||e.tagName); }); return bad.slice(0,5); }")
        check(f"{tag} 1 {label} หน้าแผน Core ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
    finally: b.close()

    # ───────── 2 ฟอร์มแผน Core ใหม่
    b, page, ce, pe = C.launch(pw, w, h, mut=mut_both)
    try:
        C.go_core(page)
        js(page, "()=>document.querySelector('[data-lf-newplan]').click()"); page.wait_for_timeout(500)
        mac = w >= 1000
        loc = js(page, "()=>{ const s = document.querySelector('.core-sheet [data-core-sheet=new]'); if(!s) return null; const side = !!s.closest('#lfCoreSide'); const r = s.getBoundingClientRect(), bx = document.querySelector('[data-lf-box]').getBoundingClientRect(); return {side, backdrop: !!s.closest('.ui-sheet-backdrop'), left: r.left, boxRight: bx.right}; }")
        check(f"{tag} 2 ฟอร์ม: Mac = คอลัมน์ขวา (ไม่เด้งทับ) · มือถือ = sheet เดิม", loc is not None and ((loc["side"] and not loc["backdrop"] and loc["left"] >= loc["boxRight"] - 1) if mac else (loc["backdrop"] and not loc["side"])), loc)
        if CS1_RETIRED:   # CS1 — Tier block / Risk % ในฟอร์มแผน Core ถูกแทนที่ด้วยแบนเนอร์ ★ (ครอบคลุมใน phase111)
            print("RETIRED (CS1) — Tier block / Risk % ในฟอร์มแผน Core ถูกแทนที่ด้วยแบนเนอร์ ★ (ครอบคลุมใน phase111)")
        else:
            opts = js(page, "()=>[...document.querySelectorAll('#cnAcct option')].map(o=>o.innerText.trim())")
            check(f"{tag} 2 ตัวเลือกบัญชีบอกตลาด 'บัญชีหลัก · US+TH' (ไม่มี 'ทั้งคู่')", any(o == "บัญชีหลัก · US+TH" for o in opts) and not any("ทั้งคู่" in o for o in opts), opts)
            row = js(page, "()=>{ const a = document.querySelector('#cnAcctBox').getBoundingClientRect(), t = document.getElementById('cnTicker').getBoundingClientRect(); return {sameRow: Math.abs(a.top - t.top) < 30, wa: a.width, wt: t.width}; }")
            check(f"{tag} 2 แถวเดียว 'บัญชี' (3 ส่วน) + 'Ticker' (2 ส่วน)", row["sameRow"] and row["wa"] > row["wt"], row)
            tl = txt(page, "[data-lf-tierline]")
            open0 = js(page, "()=>document.querySelector('[data-lf-tdet]').open")
            check(f"{tag} 2 กล่อง Tier: 'Tier B · เพดาน …%' (บรรทัดเดียว) · พับตัวเลข Tier เปิดอยู่เมื่อยังไม่มี Tier · ปุ่มเติมจาก Thesis ซ่อนเมื่อไม่มี Thesis", tl is not None and tl.startswith("Tier B") and "คำนวณ" not in tl and open0 and not vis(page, "#tiFillRow"), [tl, open0])
            # ปุ่ม ใช่ | ไม่ ทุกข้อ
            yn = js(page, "()=>({tk: document.querySelectorAll('[data-tk] button').length, g5: document.querySelectorAll('[data-g5] button').length, rows: [...document.querySelectorAll('.lf-yn')].map(r=>{ const s = r.querySelector('.ccSeg').getBoundingClientRect(), p = r.getBoundingClientRect(); return {right: Math.abs(p.right - s.right) < 16, txt: [...r.querySelectorAll('button')].map(b=>b.innerText.trim()).join('|')}; })})")
            check(f"{tag} 2 ใช่/ไม่ทุกข้อ = ปุ่มเล็ก 'ใช่ | ไม่' ชิดขวาแถวเดียวกับคำถาม (Fortress 2 · Growth 2 · Gate 5 3 ข้อ)", yn["tk"] == 8 and yn["g5"] == 6 and all(r["right"] and r["txt"] == "ใช่|ไม่" for r in yn["rows"]) and len(yn["rows"]) == 7, yn)
            # ยังไม่ตอบ ≠ ไม่ · ผลต่อมุม
            res0 = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-lf-res]')].map(e=>[e.dataset.lfRes, e.innerText.trim()]))")
            check(f"{tag} 2 ยังไม่กรอกอะไร: หัวกลุ่ม Gate 5 'ยังไม่ตอบ 3' (สีแดง) · Fortress/Growth ✗ + 'ยังไม่ตอบ 2'", res0["gate5"] == "ยังไม่ตอบ 3" and res0["fortress"].startswith("✗") and res0["fortress"].endswith("ยังไม่ตอบ 2") and res0["growth"].startswith("✗") and res0["growth"].endswith("ยังไม่ตอบ 2"), res0)
            js(page, "()=>coreTiG5('substitute', false)"); page.wait_for_timeout(100)
            one = js(page, "()=>({on: [...document.querySelectorAll('[data-g5=substitute] button')].map(b=>b.classList.contains('on')), tx: document.querySelector('[data-lf-res=gate5]').innerText.trim()})")
            js(page, "()=>coreTiG5('substitute', false)"); page.wait_for_timeout(100)
            again = js(page, "()=>[...document.querySelectorAll('[data-g5=substitute] button')].map(b=>b.classList.contains('on'))")
            check(f"{tag} 2 กด 'ไม่' → ปุ่มไม่ติด + 'ยังไม่ตอบ 2' · กดซ้ำ = กลับเป็นยังไม่ตอบ (ไม่ใช่ 'ไม่')", one["on"] == [False, True] and one["tx"] == "ยังไม่ตอบ 2" and again == [False, False], [one, again])
            # Tier คำนวณเท่าเดิมทุกกรณีตัวอย่าง
            cases = []
            def classify(page, inp):
                return js(page, """(i)=>{ const crit = coreSizeOpts(coreTiAcct()).tierCrit; const r = Calc.coreSize.classifyTier(Object.assign({}, i, crit)); return {computed: r.computed, lens: r.computedLens || null}; }""", inp)
            def ui_eval(page): return js(page, "()=>{ const t = coreTiEval(); return {computed: t.computed, lens: t.computedLens || null, tier: t.tier, pick: t.pick}; }")
            samples = [
                ("Fortress ผ่านครบ", dict(roic=.18, ndEbitda=.8, fcfConv=.92, fcfPositive3y=True, capitalReturn=True, gate5=dict(substitute=False, customerMigrating=False, singleProduct=False))),
                ("Fortress แต่ Gate 5 ยังไม่ตอบ 1 ข้อ", dict(roic=.18, ndEbitda=.8, fcfConv=.92, fcfPositive3y=True, capitalReturn=True, gate5=dict(substitute=False, customerMigrating=False, singleProduct=None))),
                ("Growth ผ่านครบ", dict(revGrowth=.25, revCagr3=.2, opMargin=.34, opMarginPrev=.31, ocf=True, netCash=True, gate5=dict(substitute=False, customerMigrating=False, singleProduct=False))),
                ("ทั้งสองมุม", dict(roic=.18, ndEbitda=.8, fcfConv=.92, fcfPositive3y=True, capitalReturn=True, revGrowth=.25, revCagr3=.2, opMargin=.34, opMarginPrev=.31, ocf=True, netCash=True, gate5=dict(substitute=False, customerMigrating=False, singleProduct=False))),
                ("Gate 5 ข้อ 2 = ใช่", dict(roic=.18, ndEbitda=.8, fcfConv=.92, fcfPositive3y=True, capitalReturn=True, gate5=dict(substitute=False, customerMigrating=True, singleProduct=False))),
            ]
            def apply(page, inp):
                js(page, "()=>{ coreTi.g5 = {substitute:null, customerMigrating:null, singleProduct:null}; coreTi.tk = {fcf3y:null, capret:null, ocf:null, netcash:null}; coreTi.pick = null; }")
                m = {"tiRoic": ("roic", 100), "tiNd": ("ndEbitda", 1), "tiFcf": ("fcfConv", 100), "tiRev": ("revGrowth", 100), "tiCagr": ("revCagr3", 100), "tiOpm": ("opMargin", 100), "tiOpmPrev": ("opMarginPrev", 100)}
                for el, (k, mul) in m.items():
                    v = inp.get(k); page.fill("#" + el, "" if v is None else str(round(v * mul, 6)))
                for tk, k in (("fcf3y", "fcfPositive3y"), ("capret", "capitalReturn"), ("ocf", "ocf"), ("netcash", "netCash")):
                    if inp.get(k) is not None: js(page, "([a,b])=>coreTiTk(a,b)", [tk, inp[k]])
                for g, v in (inp.get("gate5") or {}).items():
                    if v is not None: js(page, "([a,b])=>coreTiG5(a,b)", [g, v])
                page.wait_for_timeout(120)
            allok = True; det = []
            for nm, inp in samples:
                apply(page, inp)
                full = {"roic": None, "ndEbitda": None, "fcfConv": None, "revGrowth": None, "revCagr3": None, "opMargin": None, "opMarginPrev": None, "fcfPositive3y": None, "capitalReturn": None, "ocf": None, "netCash": None}
                full.update(inp); full["gate5"] = dict({"substitute": None, "customerMigrating": None, "singleProduct": None}, **(inp.get("gate5") or {}))
                ui, ref = ui_eval(page), classify(page, full)
                ok1 = ui["computed"] == ref["computed"] and ui["lens"] == ref["lens"]
                allok = allok and ok1; det.append([nm, ui, ref])
            check(f"{tag} 2 Tier คำนวณเท่าเดิมทุกกรณีตัวอย่าง (Fortress · Gate5 ยังไม่ตอบ=ไม่ผ่าน · Growth · ทั้งสองมุม · Gate5 ใช่)", allok, det)
            apply(page, samples[0][1])
            tl2 = txt(page, "[data-lf-tierline]"); sel = js(page, "()=>document.getElementById('cnTierSel').value")
            res1 = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-lf-res]')].map(e=>[e.dataset.lfRes, e.innerText.trim()]))")
            check(f"{tag} 2 Fortress ผ่านครบ → 'Tier A · Fortress · เพดาน …' · 'Tier ที่ใช้' = A Fortress · หัวกลุ่ม Fortress ✓ · Gate 5 ✓", tl2.startswith("Tier A · Fortress · เพดาน") and "คำนวณ" not in tl2 and sel == "fortress" and res1["fortress"] == "✓" and res1["gate5"] == "✓", [tl2, sel, res1])
            # เลือก Tier เอง
            js(page, "()=>coreTiPick('B')"); page.wait_for_timeout(150)
            tl3 = txt(page, "[data-lf-tierline]")
            check(f"{tag} 2 เลือก Tier ที่ใช้ = B → บรรทัด Tier บอก 'เลือกเอง' · เพดาน B", tl3.startswith("Tier B") and "เลือกเอง" in tl3, tl3)
            js(page, "()=>coreTiPick('fortress')"); page.wait_for_timeout(150)
            # กลยุทธ์ Winners|Ladder
            page.fill("#cnTicker", "TSM"); page.fill("#cnEntry", "300"); page.fill("#cnStop", "270"); page.wait_for_timeout(250)
            sg = js(page, "()=>({w: document.getElementById('cnStratW').innerText.trim(), l: document.getElementById('cnStratL').innerText.trim(), ld: document.getElementById('cnStratL').disabled, note: document.querySelector('[data-lf-stratnote]').innerText.trim()})")
            check(f"{tag} 2 กลยุทธ์ 'Winners | Ladder' + บรรทัด 'Ladder (ถัวตามแนวรับ) ใช้ได้เฉพาะ A Fortress' · A Fortress → Ladder กดได้", sg["w"] == "Winners" and sg["l"] == "Ladder" and not sg["ld"] and sg["note"] == "Ladder (ถัวตามแนวรับ) ใช้ได้เฉพาะ A Fortress", sg)
            js(page, "()=>coreTiPick('growth')"); page.wait_for_timeout(200)
            sg2 = js(page, "()=>({ld: document.getElementById('cnStratL').disabled, strat: coreNew.strat})")
            check(f"{tag} 2 Tier ไม่ใช่ A Fortress → Ladder กดไม่ได้ (ปิด) · กลับเป็น Winners", sg2["ld"] and sg2["strat"] == "W", sg2)
            js(page, "()=>coreTiPick('fortress')"); page.wait_for_timeout(200)
            # แถว Entry · Stop · Risk % (LN3fix2: แทนช่อง FF) + บรรทัดผล
            g3 = js(page, "()=>{ const r = ['cnEntry','cnStop','cnRisk'].map(i=>document.getElementById(i).getBoundingClientRect()); return {sameRow: r.every(x=>Math.abs(x.top - r[0].top) < 12), ff: document.getElementById('cnRisk').tagName}; }")
            ref2 = js(page, "()=>{ const cx = coreCtx('main'), r = coreFirstLotCalc(cx, 'US', 'A', 300, 270, cx.F.f, Math.min(cx.opts.riskFirst, cx.opts.tierRisk.A*cx.F.f)); return {qty: r.qty, risk: coreMoneyK(r.risk, 'US')}; }")
            got2 = js(page, "()=>({qty: +document.querySelector('[data-lf-qty]').innerText.replace(/,/g,''), line: document.querySelector('[data-lf-first]').innerText.replace(/\\s+/g,' ').trim(), ok: document.querySelector('[data-lf-first]').innerText.includes('✅')})")
            check(f"{tag} 2 แถวเดียว Entry · Stop · Risk % · บรรทัดผล '● บัญชีหลัก ไม้แรก n หุ้น · เสี่ยง $x ✅' = ค่าของ coreFirstLotCalc (Risk ไม้แรก)", g3["sameRow"] and g3["ff"] == "INPUT" and got2["qty"] == ref2["qty"] and ref2["risk"] in got2["line"] and got2["ok"] and "●" in got2["line"], [g3, ref2, got2])
            # ปุ่ม
            bt = js(page, "()=>({tier: document.getElementById('cnTierOnly').innerText.trim(), cancel: document.querySelector('[data-lf-cancel]').innerText.trim(), save: document.getElementById('cnSave').innerText.trim(), dis: document.getElementById('cnSave').disabled, tdis: document.getElementById('cnTierOnly').disabled})")
            check(f"{tag} 2 ปุ่ม 'บันทึกเฉพาะ Tier' · 'ยกเลิก' + 'บันทึกแผน' (กรอกครบ = กดได้)", bt["cancel"] == "ยกเลิก" and bt["save"] == "บันทึกแผน" and bt["tier"].startswith("บันทึกเฉพาะ Tier") and not bt["dis"] and not bt["tdis"], bt)
            words = js(page, "()=>document.querySelector('.core-sheet').innerText")
            bad = re.findall(r"(?:(?<=[\s(·/])|^)[WL](?=[\s·/)]|$)|บันได", words)
            check(f"{tag} 2 ฟอร์ม Lean ไม่มีคำ 'W' / 'L' / 'บันได'", not bad, bad)
            if w in (1440, 390):
                js(page, "()=>{ window.scrollTo(0, 0); document.querySelectorAll('.ui-sheet').forEach(e=>{ e.scrollTop = 0; }); }")
                C.shot(page, f"ln3fix-core-form-{sfx}.png", full=(w >= 1000))
            ovf = js(page, "()=>{ const W = innerWidth, bad = []; document.querySelectorAll('.core-sheet *').forEach(e=>{ if(e.closest('table, pre')) return; const r = e.getBoundingClientRect(); if(r.width>0 && r.right > W + 1) bad.push(e.className||e.tagName); }); return bad.slice(0,5); }")
            check(f"{tag} 2 {label} ฟอร์มไม่ล้นแนวนอน", overflow(page) <= 0 and not ovf, [overflow(page), ovf])
            # ยกเลิก = ปิดไม่บันทึก
            n0 = js(page, "()=>coreCardsList.length")
            js(page, "()=>document.querySelector('[data-lf-cancel]').click()"); page.wait_for_timeout(400)
            closed = js(page, "()=>({sheet: document.querySelectorAll('.core-sheet').length, side: document.getElementById('lfCoreSide').classList.contains('on'), n: coreCardsList.length})")
            check(f"{tag} 2 'ยกเลิก' = ปิดฟอร์มไม่บันทึก (จำนวนการ์ดเท่าเดิม)", closed["sheet"] == 0 and not closed["side"] and closed["n"] == n0, closed)
            # บันทึก = ไม้แรก/เสี่ยงเท่าเดิม
            js(page, "()=>document.querySelector('[data-lf-newplan]').click()"); page.wait_for_timeout(400)
            page.fill("#cnTicker", "TSM"); fill_tier(page); page.fill("#cnEntry", "300"); page.fill("#cnStop", "270"); page.wait_for_timeout(250)
            qty_ui = js(page, "()=>+document.querySelector('[data-lf-qty]').innerText.replace(/,/g,'')")
            js(page, "()=>document.getElementById('cnSave').click()"); page.wait_for_timeout(800)
            card = js(page, "()=>{ const c = coreCardsList.find(x=>x.ticker==='TSM'); return c ? {tier: c.tier, lens: c.tierLens, plan: c.plan, strat: c.strategy, acct: c.acct} : null; }")
            row2 = js(page, "()=>{ const r = document.querySelector('[data-core-card] [data-c-ticker]'); const e = [...document.querySelectorAll('#corePanel .ccRow')].find(x=>x.querySelector('[data-c-ticker]').innerText==='TSM'); return e ? e.querySelector('[data-lf-l2]').innerText : null; }")
            check(f"{tag} 2 'บันทึกแผน' → การ์ด TSM (Tier A Fortress · Winners · 300/270) · แถวการ์ดบอกไม้แรกเท่าที่ฟอร์มคำนวณ", card and card["tier"] == "A" and card["lens"] == "fortress" and card["strat"] == "W" and card["plan"] == {"entry": 300, "stop": 270, "risk": 0.6} and row2 == f"แผน · 300 / 270 · ไม้แรก {qty_ui} หุ้น", [card, row2, qty_ui])
    finally: b.close()

    # ───────── 3 Ladder (Lean ใช้คำ Ladder) + legacy เหมือนเดิม
    b, page, ce, pe = C.launch(pw, w, h, cards={"ccNV": C.core_cards()["ccNV"], "ccLd": P26.lcard("ccLd", ticker="ZZZ")}, mut=mut_both)
    try:
        C.go_core(page)
        r = js(page, "()=>{ const e = [...document.querySelectorAll('#corePanel .ccRow')].find(x=>x.querySelector('[data-c-ticker]').innerText==='ZZZ'); return e ? {tag: e.querySelector('[data-lf-tag]').innerText, l2: e.querySelector('[data-lf-l2]').innerText} : null; }")
        check(f"{tag} 3 การ์ดแผน Ladder: ป้าย 'A · Ladder' · บรรทัด 2 'แผน · L1 … · SL …' (ไม่มีคำ 'บันได')", r is not None and r["tag"] == "A · Ladder" and r["l2"].startswith("แผน · L1 ") and "SL" in r["l2"], r)
        js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(300)
        t = js(page, "()=>document.getElementById('corePanel').innerText")
        check(f"{tag} 3 เนื้อการ์ด Ladder ไม่มีคำ 'บันได' / 'L' เดี่ยว", not re.findall(r"(?:(?<=[\s(·/])|^)[WL](?=[\s·/)]|$)|บันได", t), re.findall(r"(?:(?<=[\s(·/])|^)[WL](?=[\s·/)]|$)|บันได", t))
    finally: b.close()

    b, page, ce, pe = C.launch(pw, w, h, mut=mut_both)
    try:
        js(page, "()=>{ ln1SetMode('legacy'); switchTab('plan'); setPlanScope('stock'); render(); }"); page.wait_for_timeout(600)
        lg = js(page, """()=>({a: document.getElementById('scopeStock').innerText.replace(/\\s+/g,' ').trim(), strip: document.getElementById('strip').offsetParent!==null, ports: !!document.querySelector('#portsSum'), pos: document.getElementById('posPanel').offsetParent!==null,
          head: document.querySelectorAll('#corePanel [data-core-head]').length, lf: document.querySelectorAll('[data-lf-box]').length, hasW: /ระบบ Week|·W|W /.test(document.getElementById('corePanel').innerText)})""")
        check(f"{tag} 3 โหมดเดิม (legacy) แผน Core เหมือนเดิม: ปุ่ม 'Port หุ้น' · การ์ดบัญชี Hold/Plan · กล่อง 4 ช่อง · Positions · หัวบัญชี Core · ไม่มีกล่อง Lean", lg["a"].startswith("Port หุ้น") and lg["strip"] and lg["ports"] and lg["pos"] and lg["head"] >= 1 and lg["lf"] == 0, lg)
        js(page, "()=>coreNewOpen('main')"); page.wait_for_timeout(400)
        lf = js(page, "()=>({w: !!document.getElementById('cnStratW'), txt: document.getElementById('cnStratW').innerText, tierbtn: !!document.getElementById('cnTierB'), lean: !!document.querySelector('[data-lf-tier]'), opt: [...document.querySelectorAll('#cnAcct option')].map(o=>o.innerText.trim())})")
        check(f"{tag} 3 ฟอร์ม legacy เหมือนเดิม: 'ระบบ Week' · ปุ่ม Tier 4 ตัวเลือก · บัญชี 'ทั้งคู่'", lf["txt"] == "ระบบ Week" and lf["tierbtn"] and not lf["lean"] and any("ทั้งคู่" in o for o in lf["opt"]), lf)
        js(page, "()=>{ coreSheetClose(); ln1SetMode('lean'); }"); page.wait_for_timeout(500)
        back = js(page, "()=>({a: document.getElementById('scopeStock').innerText.trim(), lf: document.querySelectorAll('[data-lf-box]').length})")
        check(f"{tag} 3 สลับกลับ Lean → ปุ่ม 'Core' + กล่อง Lean กลับมา", back["a"] == "Core" and back["lf"] == 1, back)
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px"), (300, 700, "300px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
