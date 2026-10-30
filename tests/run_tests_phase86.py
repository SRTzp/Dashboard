#!/usr/bin/env python3
"""LN3 — แท็บ Flow แบบ Lean: การ์ดสรุปเดียว · ทุกหัวข้อพับได้ (Macro เปิดเป็นค่าเริ่ม) · RRG แถว 2 บรรทัดครบคอลัมน์ · เตือน QT เป็นบรรทัดใน Regime · เทส 86
mock Firestore + fundflow stub · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-flow-{1440,390}.png
รัน: python3 run_tests_phase86.py"""
import json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase11 as P11
import run_tests_phase12 as P12

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []


def js(page, f, arg=None):
    return page.evaluate(f, arg) if arg is not None else page.evaluate(f)


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(500)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def cnt(page, sel): return page.locator(sel).count()
def txt(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


ROWS = [
    {"sym": "SMH", "name": "Semis", "quad": "lead", "prevQuad": "lead", "dMom": 1.2, "dRatio": 0.5, "ratio": 106, "mom": 104, "rsTrend": 1.5, "days": 6, "off52": -3.2},
    {"sym": "XLU", "name": "Utilities/Power", "quad": "imp", "prevQuad": "lag", "dMom": 0.8, "dRatio": 0.2, "ratio": 98, "mom": 101, "rsTrend": 0.4, "days": 3, "off52": -1.0},
    {"sym": "IGV", "name": "Software", "quad": "weak", "prevQuad": "lead", "dMom": -1.1, "dRatio": -0.4, "ratio": 102, "mom": 97, "rsTrend": -0.5, "days": 9, "off52": -12.4},
    {"sym": "XLRE", "name": "Real estate", "quad": "lag", "prevQuad": "lag", "dMom": -0.3, "dRatio": -0.1, "ratio": 95, "mom": 96, "rsTrend": -1.0, "days": 12, "off52": -18.0},
]


def setup(pw, w, h):
    browser, context, page, ce, pe = P11.fresh(pw, w, h)
    P12.set_ff(page, {"ACWI_BIL": False, "HYG_IEI": True, "HG_GC": True}, prev={"ACWI_BIL": False, "HYG_IEI": True}, age=1)
    P11.seed_pb(page, [P12.pbver(1, P12.iso(), x="down", b="none", r="none", u="none")])
    P12.rrg_rows(page, ROWS)
    js(page, "()=>{ switchTab('flow'); renderFundflow(); }"); page.wait_for_timeout(500)
    return browser, page, ce, pe


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe = setup(pw, w, h)
    try:
        # ── 1 การ์ดสรุป
        hero = js(page, """()=>{ const h = document.querySelector('[data-ln3-fhero]'); if(!h) return null; return {t: h.innerText.replace(/\\s+/g,' ').trim(), rows: [...h.querySelectorAll('[data-ff-row]')].map(r=>r.dataset.ffRow), grid: document.querySelectorAll('#ffAction .ffActGrid,#ffAction .ffActCell').length, big: h.querySelector('[data-ff-cap=hero]').innerText.replace(/\\s+/g,' ').trim()}; }""")
        check(f"{tag} 1 การ์ดสรุปเดียว (แทนกล่อง 4 ช่อง): 'Core ลงเงินได้' · 75% · 'ลด 25% จาก Regime' · แถว Regime / ธีมนำ / Macro", hero and hero["grid"] == 0 and hero["rows"] == ["regime", "lead", "macro"] and hero["t"].startswith("Core ลงเงินได้") and hero["big"].startswith("75%") and "ลด 25% จาก Regime" in hero["big"], hero)
        check(f"{tag} 1 Regime: 'ACWI/BIL ▼ แดง · HYG/IEI ▲ เขียว' · ธีมนำ: Semis (RRG Leading) · Macro: XAU ▼ + ไตรมาส/เวอร์ชัน", all(k in hero["t"] for k in ("ACWI/BIL ▼ แดง", "HYG/IEI ▲ เขียว", "Semis", "(RRG Leading)", "XAU ▼", "2026Q4 v001")), hero["t"])
        ccol = js(page, "()=>{ const u = document.querySelector('[data-ff-row=regime] .ln3u'), d = document.querySelector('[data-ff-row=regime] .ln3d'); return [getComputedStyle(u).color, getComputedStyle(d).color]; }")
        check(f"{tag} 1 ลูกศรมีสี (พื้นมืด): ▲ #4fd39a · ▼ #ff7b6e", ccol == ["rgb(79, 211, 154)", "rgb(255, 123, 110)"], ccol)
        js(page, "()=>document.querySelector('[data-ff-row=regime]').click()"); page.wait_for_timeout(300)
        # ── 2 หัวข้อพับได้
        sec = js(page, "()=>({macro: document.querySelector('[data-ln3-sec=macro]').open, regime: document.querySelector('[data-ln3-sec=regime]').open, cal: document.getElementById('ffCal').open, msum: document.querySelector('[data-ln3-sec=macro] summary').innerText.replace(/\\s+/g,' '), rsum: document.querySelector('[data-ln3-sec=regime] summary').innerText.replace(/\\s+/g,' ')})")
        check(f"{tag} 2 Macro เปิดเป็นค่าเริ่ม · Regime / ปฏิทินข่าว พับไว้ · หัวข้อสรุปค่า ('Macro ไตรมาส 2026Q4 · ใช้จริง' · 'Regime … 75%')", sec["macro"] is True and sec["regime"] is False and sec["cal"] is False and "2026Q4" in sec["msum"] and "ใช้จริง" in sec["msum"] and "75%" in sec["rsum"], sec)
        js(page, "()=>{ document.querySelector('[data-ln3-sec=macro]').open = false; document.querySelector('[data-ln3-sec=macro]').dispatchEvent(new Event('toggle')); renderFundflow(); }"); page.wait_for_timeout(300)
        check(f"{tag} 2 พับ Macro แล้ววาดใหม่ (ข้อมูลเปลี่ยน) → ยังพับอยู่ (จำสถานะ)", js(page, "()=>document.querySelector('[data-ln3-sec=macro]').open") is False)
        js(page, "()=>{ const d = document.querySelector('[data-ln3-sec=macro]'); d.open = true; d.dispatchEvent(new Event('toggle')); }")
        body = txt(page, "[data-ln3-sec=macro]") or ""
        check(f"{tag} 2 กาง Macro → เนื้อหาเดิมครบ (ปุ่ม วาง JSON · ประวัติ)", "วาง JSON" in body and "ประวัติ" in body, body[:200])
        # ── 3 Regime + QT
        js(page, "()=>{ const d = document.querySelector('[data-ln3-sec=regime]'); d.open = true; d.dispatchEvent(new Event('toggle')); }"); page.wait_for_timeout(200)
        rg = js(page, """()=>{ const d = document.querySelector('[data-ln3-sec=regime]'); return {t: d.innerText.replace(/\\s+/g,' '), chips: d.querySelectorAll('.ffRegChip').length, qt: !!d.querySelector('[data-ln3-qt]'), warn: (d.querySelector('[data-ln3-qt-warn]')||{}).innerText, bar: getComputedStyle(document.getElementById('ffQeBar')).display}; }""")
        check(f"{tag} 3 Regime: Core 2 ตัว + บริบท 3 ตัว · บรรทัด 'QE/QT: QT … แก้ ✎' · แถบ QT ใหญ่ซ่อน", all(k in rg["t"] for k in ("ACWI/BIL", "HYG/IEI", "Cu/Au", "SPHB/SPLV", "RSP/SPY")) and rg["qt"] and "QE/QT:" in rg["t"] and rg["bar"] == "none", rg)
        check(f"{tag} 3 ยังไม่ตั้ง QT → บรรทัดเตือน 'QT ยังไม่ได้ตั้งค่า — แตะเพื่อกรอก' (ในหัวข้อ Regime)", rg["warn"] == "QT ยังไม่ได้ตั้งค่า — แตะเพื่อกรอก", rg["warn"])
        js(page, "()=>document.querySelector('[data-ln3-qt-warn]').click()"); page.wait_for_timeout(300)
        check(f"{tag} 3 แตะบรรทัดเตือน → เปิดฟอร์ม QE/QT", js(page, "()=>document.getElementById('ffQeOverlay').classList.contains('show')"))
        js(page, "()=>{ document.getElementById('ffQeDate').value = '2026-10-01'; ffSaveQe(); }"); page.wait_for_timeout(400)
        qt = txt(page, "[data-ln3-qt]") or ""
        check(f"{tag} 3 ตั้งแล้ว → 'QE/QT: QT ตั้งเมื่อ 2026-10-01' · ไม่มีบรรทัดเตือน · ปุ่ม 'แก้ ✎' เปิดฟอร์มได้", "ตั้งเมื่อ 2026-10-01" in qt and cnt(page, "[data-ln3-qt-warn]") == 0, qt)
        page.locator("[data-ln3-qt-edit]").click(); page.wait_for_timeout(300)
        check(f"{tag} 3 'แก้ ✎' เปิดฟอร์ม", js(page, "()=>document.getElementById('ffQeOverlay').classList.contains('show')"))
        js(page, "()=>document.getElementById('ffQeOverlay').classList.remove('show')")
        # ── 4 ปฏิทิน / บอร์ด / ตั้งค่า
        check(f"{tag} 4 ปฏิทินข่าว (พับ) · บอร์ดจดเอง ชั้น 1–2 (พับ) · ปุ่ม 🛠 ตั้งค่า proxy / น้ำหนัก ยังอยู่", cnt(page, "details#ffCal") == 1 and cnt(page, "details#ffManualBoards") == 1 and js(page, "()=>document.getElementById('ffManualBoards').open") is False and "ตั้งค่า proxy" in (txt(page, ".ffFoot") or ""))
        # ── 5 RRG
        js(page, "()=>{ ffState().themesCol = false; ffApplyThemesCol(); ffRenderThemes(); }"); page.wait_for_timeout(300)
        rr = js(page, """()=>{ const g = document.querySelector('[data-ln3-rrg]'); if(!g) return null; const rows = [...g.querySelectorAll('.ln3-rr')]; return {n: rows.length, tbl: document.querySelectorAll('#ffThemes table').length, t0: rows[0].innerText.replace(/\\s+/g,' '), l1: rows.every(r=>r.querySelector('.l1')), l2: rows.every(r=>r.querySelectorAll('.l2 .rrgGaugeWrap').length === 2), order: rows.map(r=>r.dataset.rr), bar: document.getElementById('ffRrgBar').innerText.replace(/\\s+/g,' '), br: document.getElementById('ffBreadth').innerText}; }""")
        check(f"{tag} 5 RRG เป็นแถว 2 บรรทัด (ไม่ใช่ตาราง): บรรทัด 1 ชื่อ+ควอดแรนต์+วันอยู่มา+ห่างจาก high · บรรทัด 2 ความแข็ง + โมเมนตัม (เกจ+Δ)", rr and rr["n"] == 4 and rr["tbl"] == 0 and rr["l1"] and rr["l2"], rr)
        check(f"{tag} 5 ครบคอลัมน์เดิม: ควอดแรนต์ LEADING · อยู่มา 6 · OFF52W −3.2% · เรียง Leading → Improving → Weakening → Lagging", "LEADING" in rr["t0"] and "6" in rr["t0"] and "-3.2%" in rr["t0"] and rr["order"] == ["SMH", "XLU", "IGV", "XLRE"], [rr["t0"], rr["order"]])
        check(f"{tag} 5 แถบสถานะ (Daily/Weekly · รีเฟรช · rrg v) + Breadth + 4 ช่องควอดแรนต์ ยังอยู่", "Daily" in rr["bar"] and "รีเฟรชราคา" in rr["bar"] and "ชนะ SPY" in rr["br"] and cnt(page, ".ffQuad .ffQ") == 4, [rr["bar"], rr["br"]])
        shot(page, f"ln3-flow-{sfx}.png", "#tabFlow")
        # ── 6 ล้น + console
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#tabFlow *').forEach(e=>{ if(e.closest('.ffMiniScroll,table')) return; const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push((e.className || e.tagName) + ':' + Math.round(r.right)); }); return bad.slice(0,5); }""")
        check(f"{tag} 6 {label} ไม่ล้นแนวนอน · ไม่มี console error", js(page, "()=>document.documentElement.scrollWidth - window.innerWidth") <= 0 and not ov and not ce and not pe, [ov, ce[:2], pe[:2]])
        # ── 7 legacy
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(500)
        lg = js(page, "()=>({grid: document.querySelectorAll('#ffAction .ffActCell').length, tbl: document.querySelectorAll('#ffThemes table.rrgTbl').length, ln3: document.querySelectorAll('[data-ln3-fhero],[data-ln3-sec],[data-ln3-rrg]').length, bar: getComputedStyle(document.getElementById('ffQeBar')).display})")
        check(f"{tag} 7 โหมดแบบเดิม: กล่อง 4 ช่อง · ตาราง RRG · แถบ QT ใหญ่ ตามเดิม · ไม่มี LN3", lg["grid"] == 4 and lg["tbl"] == 1 and lg["ln3"] == 0 and lg["bar"] != "none", lg)
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
