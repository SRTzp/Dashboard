#!/usr/bin/env python3
"""LN3fix3 §5 — จอ Mac ≥1000px: Today 2 คอลัมน์ (ซ้าย เป้าหมาย Port→งาน→เช็กแผน Sat · ขวา ช่วงเวลา→Re-check Macro→อื่น ๆ ปกติ) · Flow (ตัวอักษร Macro ≥15px · หัวข้อไม่ตัด … · Macro กว้างกว่า RRG · ข้อควรติดตามพับ) · Watch (ลิสต์ 355px · แถว BRK.B บรรทัดเดียว · ข้อความยาวตัดบรรทัด) · งาน XAU เติมไม้บอกบัญชี · เทส 94
Chromium 1280 + 1440 + 390 (มือถือไม่เปลี่ยน) · FF_STUB_BASE = Lean
ภาพ tests/screenshots/ln3fix3-{today-1440,flow-1440,watch-1440,watch-1280}.png
รัน: python3 run_tests_phase94.py"""
from pf2_retire import retired_sn1 as retired4
import json, os
import pf2_retire as RT
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase56 as P56
import run_tests_phase77 as P77
import run_tests_phase85 as P85
import run_tests_phase35 as P35

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
overflow = C.overflow
LONGTOK = "ThisIsAVeryLongUnbrokenTokenToTestWrapping_https://investors.broadcom.com/financial-information/quarterly-results/fy2026-q4"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def today(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); mac = w >= 1000
    browser, context, page, ce, pe, dl = P56.launch(pw, w, h, P56.with_goals(), None, log={})
    try:
        js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); page.wait_for_timeout(900)
        if mac: RT.retired_td3a(f"{tag} 1 ก้นสองคอลัมน์ต่างกันไม่เกิน ~35% — ดู TD3a_retired.md (แทนด้วย 3 panels ชิดบนเท่ากัน ด้านล่าง)")
        js(page, """()=>{ const mk = id => ({id, date:'2026-09-28', sym:'XAUUSD', port:'satB', bias:'Long', entry:4180, sl:4117, qty:0.05, mult:1, cur:'USD', status:'open', unplanned:false});
          getBook('main').trades = [mk('px1')]; getBook('fam').trades = [mk('px2')]; saveBook('main'); saveBook('fam');
          window.satPyrCheck = ()=>({ok:true, k:2, cum:3}); window.satPyrEligible = ()=>true; }""")
        js(page, "()=>todayRefresh(true)"); page.wait_for_timeout(500)
        pyr = js(page, "()=>[...document.querySelectorAll('[data-kind=sat-pyr]')].map(e=>e.textContent.replace(/\\s+/g,' '))")
        check(f"{tag} 1 งาน 'XAU เติมไม้ … ได้' ของ 2 บัญชีบอกชื่อบัญชี (จุดสี + ชื่อ) ไม่ซ้ำคลุมเครือ", len(pyr) >= 2 and len(set(pyr)) == len(pyr) and all(("หลัก" in t or "Family" in t) for t in pyr), pyr)
        RT.retired_td3a(f"{tag} 1 Today 2 คอลัมน์ Mac (ลำดับซ้าย/ขวา · Re-check ระหว่างช่วงเวลากับ อื่น ๆ ปกติ) / มือถือ: เป้าหมายบรรทัดบนสุด — ดู TD3a_retired.md")
        pn = js(page, RT.PANELS_JS)
        check(f"{tag} 1 TD3a: 3 panels (Overview · Core Port · Satellite) ชิดบนเท่ากันบน Mac · ไม่ล้นแนวนอน", RT.panels_ok(pn), pn)
        if mac and w == 1440: C.shot(page, "ln3fix3-today-1440.png", full=True)
        check(f"{tag} 1 {label} Today ไม่ล้น · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: browser.close()


def flow(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); mac = w >= 1000
    b, page, ce, pe = P77.launch(pw, w, h, pb=True)
    try:
        js(page, """()=>{ const v = pbList[0]; v.view = Object.assign({}, v.view, {headline:'Real Rates Are the Tax, Hormuz Is the Swing — ' + 'หัวข้อยาวมากเพื่อทดสอบว่าไม่ถูกตัดด้วยจุดสามจุดบนจอ Mac', thesis:'ดอกเบี้ยแท้จริงที่สูงเป็นแรงกดหลัก ผ่านต้นทุนเงินและ USD แข็ง', watch:'ตัวพลิกคือ Hormuz', base:'Base ทดสอบ', alt:'Alt ทดสอบ'});
          pbOpen = true; switchTab('flow'); pbRender(); }""")
        page.wait_for_timeout(1000)
        m = js(page, """()=>{ const q = s => document.querySelector(s); const fs = s => { const e = q(s); return e ? parseFloat(getComputedStyle(e).fontSize) : null; };
          const hl = q('#pbPanel .pbHl'), why = q('#pbPanel .pbWhy'), ico = q('#pbPanel .pbRow .pbIco'), pb = q('#pbPanel').getBoundingClientRect(), rr = q('#ffThemesPanel') ? q('#ffThemesPanel').getBoundingClientRect() : null, fold = q('[data-pb-fold]');
          return {thesis: fs('#pbPanel .pbThesis'), why: fs('#pbPanel .pbWhy'), hlTrunc: hl ? (getComputedStyle(hl).textOverflow==='ellipsis' && hl.scrollWidth > hl.clientWidth) : null, hlWs: hl ? getComputedStyle(hl).whiteSpace : null,
                  whyClamp: why ? getComputedStyle(why).webkitLineClamp : null, whyCut: why ? why.scrollHeight > why.clientHeight + 1 : null, ico: ico ? Math.round(ico.getBoundingClientRect().width) : null, pbW: Math.round(pb.width), rrgW: rr ? Math.round(rr.width) : null,
                  fold: fold ? {open: fold.open, txt: fold.querySelector('summary').innerText.trim(), hasWatch: !!fold.querySelector('.pbWatch'), hasScn: fold.querySelectorAll('.pbScn').length} : null, bodyOv: document.querySelector('#pbPanel').scrollWidth > document.querySelector('#pbPanel').clientWidth + 1}; }""")
        if mac:
            check(f"{tag} 2 Flow: ตัวอักษรบทสรุป Macro ≥ 15px และ headline Asset ≥ 15px", m["thesis"] >= 15 and m["why"] >= 15, m)
            check(f"{tag} 2 Flow: หัวข้อไม่ตัดด้วย '…' (ขึ้นบรรทัดใหม่) · เหตุผล Asset ไม่ถูกตัด 2 บรรทัด", not m["hlTrunc"] and m["hlWs"] == "normal" and m["whyClamp"] in ("none", None) and not m["whyCut"], m)
            check(f"{tag} 2 Flow: คอลัมน์ไอคอนแคบ ~36px · คอลัมน์ Macro กว้างกว่า RRG (≈1.15 : 1)", 30 <= m["ico"] <= 44 and m["pbW"] > m["rrgW"] and 1.05 <= m["pbW"] / m["rrgW"] <= 1.3, m)
            check(f"{tag} 2 Flow: 'ข้อควรติดตาม · Base / Alt · P1–P4' พับเป็นค่าเริ่ม (มีข้อควรติดตาม + Base + Alt ข้างใน)", m["fold"] and m["fold"]["open"] is False and m["fold"]["hasWatch"] and m["fold"]["hasScn"] == 2 and m["fold"]["txt"].startswith("ข้อควรติดตาม · Base / Alt"), m)
            if w == 1440: C.shot(page, "ln3fix3-flow-1440.png", full=False)
        else:
            check(f"{tag} 2 มือถือไม่เปลี่ยน: ไม่มีพับข้อควรติดตาม (แสดงตรง) · ฟอนต์ 16px (PF2 A3)", m["fold"] is None and m["thesis"] == 16, m)   # PF2 A3: มือถือเนื้อหา Macro 16px
        check(f"{tag} 2 {label} Flow ไม่ล้น · ไม่มี console error", overflow(page) <= 0 and not m["bodyOv"] and not ce and not pe, [overflow(page), ce[:2], pe[:2]])
    finally: b.close()


def watch(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); mac = w >= 1000
    b, page, ce, pe, dl = P85.launch(pw, w, h)
    try:
        for a in ("main", "fam"):
            js(page, "([a,t])=>{ const B = getBook(a); B.trades = [t]; saveBook(a); render(); }", [a, P13.T("h" + a, "core", "open", sym="AVGO", entry=300, sl=270, qty=100)])
        import copy
        d = copy.deepcopy(P35.dump(page)["users/testuid/watchlist/AVGO"]["thesis"])
        d["tripwires"][0]["level"] = "broken"
        d["catalysts"] = [{"event": "งบ Q3 FY26 — ประชุมผู้ถือหุ้นประจำปี + ประกาศแผนซื้อหุ้นคืนรอบใหม่ " + LONGTOK, "date": "2026-12-10", "date_status": "estimated", "thesis": 1}, {"event": "ประกาศเก่าที่ผ่านแล้ว", "date": "2026-09-01", "date_status": "confirmed", "thesis": 1}]
        for k in ("thesis", "theses"):
            if isinstance(d.get(k), list) and d[k] and isinstance(d[k][0], dict):
                for f in ("claim", "text", "title", "why"):
                    if isinstance(d[k][0].get(f), str): d[k][0][f] = d[k][0][f] + " " + LONGTOK; break
        P35.put_thesis(page, "AVGO", d)
        js(page, "()=>{ phSet('AVGO','start'); }"); page.wait_for_timeout(300)
        P85.go(page); page.wait_for_timeout(600)
        g = js(page, """()=>{ const l = document.querySelector('.wlList').getBoundingClientRect(); const r = document.querySelector('.wlR[data-sym="AVGO"]'); const kids = [...r.children].filter(e=>!e.classList.contains('ln3-cat'));
          const tops = kids.map(e=>{ const q = e.getBoundingClientRect(); return Math.round(q.top + q.height/2); }); return {w: Math.round(l.width), txt: r.innerText.replace(/\\s+/g,' ').trim(), spread: Math.max(...tops) - Math.min(...tops), dots: r.querySelectorAll('.wlDotH, .wlDotR').length, rowOv: r.scrollWidth > r.clientWidth + 1}; }""")
        if mac:
            check(f"{tag} 3 Watch: ลิสต์กว้าง 355px (±1)", abs(g["w"] - 355) <= 1, g)
            check(f"{tag} 3 Watch: แถวแบบ BRK.B (Tier A · Phase · ⛔ Tripwire · ควร update · 3 จุด) อยู่บรรทัดเดียว ไม่ล้น", "⛔ Tripwire" in g["txt"] and "ควร update" in g["txt"] and g["dots"] == 3 and g["spread"] <= 6 and not g["rowOv"], g)
        else:
            check(f"{tag} 3 มือถือไม่เปลี่ยน: ลิสต์ไม่ใช่ 355px แบบ Mac · ไม่ล้น", not g["rowOv"] and overflow(page) <= 0, g)
        det = js(page, """()=>{ const body = document.querySelector('.wlDBody'); const probe = document.createElement('div'); probe.style.cssText = 'position:absolute;visibility:hidden;width:72ch;font:inherit'; body.appendChild(probe); const max = probe.getBoundingClientRect().width; probe.remove();
          const items = [...body.querySelectorAll('li, dd')]; const wide = items.filter(e=>e.getBoundingClientRect().width > max + 2).length;
          return {bodyOv: body.scrollWidth > body.clientWidth + 1, max: Math.round(max), wide, n: items.length, docOv: document.documentElement.scrollWidth - innerWidth}; }""")
        check(f"{tag} 3 Watch รายละเอียด: สตริง/Catalyst ยาวไม่มีช่องว่างตัดบรรทัด ไม่ดันจอ{' · ข้อความบทความกว้างไม่เกิน ~72ch' if mac else ''}", not det["bodyOv"] and det["docOv"] <= 0 and (not mac or det["wide"] == 0), det)
        if w == 1440: C.shot(page, "ln3fix3-watch-1440.png", full=False)
        if w == 1280: C.shot(page, "ln3fix3-watch-1280.png", full=False)
        check(f"{tag} 3 {label} Watch ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (1280, 800, "1280px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            today(pw, w, h, label); flow(pw, w, h, label); watch(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
