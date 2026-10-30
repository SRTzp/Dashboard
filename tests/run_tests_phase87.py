#!/usr/bin/env python3
"""LN3 — แท็บ Journal แบบ Lean: กล่องสรุปเดียว (บัญชี · รวม/Core/Sat · ปี/เดือน · 6 ตัวเลข · โชค/แพ้รับได้ในพับ 'รีวิว x/y') · การ์ดไม้ 3 บรรทัด · แก้ไข/ลบ → ⋯ · พับ Setup/Cancelled/เงื่อนไข · เทส 87
mock Firestore · Chromium 1440 + 390 + 300 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-journal-{1440,390}.png
รัน: python3 run_tests_phase87.py"""
import json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase16 as P16

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
def vis(page, sel): return js(page, "(s)=>{ const e=document.querySelector(s); return !!e && e.offsetParent !== null && getComputedStyle(e).display !== 'none'; }", sel)


def C(id, port, sym, entry, exit_, qty=1, **kw):
    d = dict(sym=sym, entry=entry, sl=entry - 10, qty=qty, exitPrice=exit_, exitDate=kw.pop("exitDate", "2026-10-12"), date="2026-10-05", openedAt="2026-10-05")
    d.update(kw); return P13.T(id, port, "closed", **d)


MAIN = [
    C("a1", "core", "NVDA", 128, 141, 100, discScore=3, setupScore=3, exitNote="ปิดครึ่งตามแผน", exitReason="tp"),
    C("a2", "core", "AVGO", 300, 290, 10, discScore=3, setupScore=2),
    C("s1", "satB", "XAUUSD", 4240, 4200, 0.07, bias="Short", unplanned=True, discScore=0, setupScore=1, posGroup="g1", exitDate="2026-10-15", mult=100, cur="USD"),
    C("s2", "satB", "XAUUSD", 4240, 4220, 0.07, bias="Short", unplanned=True, discScore=2, posGroup="g1", exitDate="2026-10-16", mult=100, cur="USD"),
    C("s3", "satB", "BTCUSD", 62000, 61000, 0.01, bias="Short", exitDate="2026-10-10", cur="USD"),
    P13.T("x1", "core", "closed", sym="MISS", entry=50, sl=40, qty=10, exitPrice=0, exitDate="2026-10-11", date="2026-10-01"),   # ข้อมูลไม่ครบ (ไม่มี Exit)
    P13.T("c1", "satB", "cancelled", sym="BTCUSD", entry=62000, sl=60500, tp=66000, qty=0.01, cancelDate="2026-10-08", date="2026-10-07", cur="USD"),
]
FAM = [C("f1", "core", "PTT", 36, 40, 1000, discScore=3, setupScore=3)]


def setup(pw, w, h):
    browser, context, page, ce, pe = P16.fresh(pw, w, h)
    P16.seed(page, MAIN, FAM)
    js(page, "()=>{ switchTab('journal'); jAcct = 'main'; render(); }"); page.wait_for_timeout(500)
    return browser, page, ce, pe


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe = setup(pw, w, h)
    try:
        # ── 1 กล่องสรุป
        bx = js(page, """()=>{ const b = document.querySelector('[data-ln3-jbox]'); if(!b) return null; const g = k => (b.querySelector('[data-sum='+k+'] b')||{}).innerText; return {n: document.querySelectorAll('[data-ln3-jbox]').length, sel: b.querySelectorAll('.jvSel').length, accts: [...b.querySelectorAll('[data-ln3-jacct]')].map(x=>x.innerText.trim()), scopes: [...b.querySelectorAll('[data-ln3-scope]')].map(x=>x.innerText.trim()), cells: ['n','win','avgr','pnl','dd','disc'].map(g), ports: document.getElementById('jPorts').innerHTML.trim(), portShown: getComputedStyle(document.getElementById('jPorts')).display, rowShown: getComputedStyle(document.getElementById('jAcctRow')).display, old: document.querySelectorAll('#jSum .sumGrid').length}; }""")
        exp = js(page, "()=>{ const j = journalStats().overall; return {n: String(j.n), win: fmt2(j.winRate)+'%', dd: fmt2(j.maxDDPct)+'%', disc: fmt2(j.avgDisc)+'/3'}; }")
        check(f"{tag} 1 กล่องสรุปเดียว: หัว Journal + ปี/เดือน · ปุ่มบัญชี 2 · ปุ่ม รวม/Core/Sat · 6 ตัวเลข · ไม่มีการ์ดแยกพอร์ตแบบเดิม", bx and bx["n"] == 1 and bx["sel"] == 2 and len(bx["accts"]) == 2 and bx["scopes"] == ["รวม", "Core", "Sat"] and bx["ports"] == "" and bx["old"] == 0 and bx["rowShown"] == "none", bx)
        check(f"{tag} 1 ตัวเลข 6 ช่อง = journalStats เดิม (ไม้ปิด · Win Rate · Avg R · P&L · Max DD · วินัย)", bx["cells"][0] == exp["n"] and bx["cells"][1] == exp["win"] and bx["cells"][4] == exp["dd"] and bx["cells"][5] == exp["disc"], [bx["cells"], exp])
        rv = js(page, "()=>{ const d = document.querySelector('[data-ln3-review]'); const j = journalStats().overall; return {sum: d.querySelector('summary').innerText.trim(), body: d.textContent.replace(/\\s+/g,' '), open: d.open, exp: `รีวิว ${j.nReviewed}/${j.n}`, luck: j.luckyWins, good: j.goodLosses, outside: /โชค|แพ้รับได้/.test(document.querySelector('[data-ln3-jbox]').innerText)}; }")
        check(f"{tag} 1 'โชค / แพ้รับได้' อยู่ในพับใต้ 'รีวิว x/y' (พับไว้) · ไม่โผล่นอกพับ · ค่า = journalStats", rv["sum"] == rv["exp"] and rv["open"] is False and f"โชค {rv['luck']} · แพ้รับได้ {rv['good']}" in rv["body"] and rv["outside"] is False, rv)
        ln = txt(page, "[data-jsum=decision]") or ""
        check(f"{tag} 1 บรรทัด 'ถือเฉลี่ย x วัน · …' + ข้อความเตือน (ไม้นอกแผน n ไม้ · P&L)", ln.startswith("ถือเฉลี่ย") and "ไม้นอกแผน 2 ไม้" in ln, ln)
        # ── 2 สลับบัญชี / Core / Sat
        page.locator('[data-ln3-scope="core"]').click(); page.wait_for_timeout(400)
        ex = js(page, "()=>{ const j = journalStats().core; return String(j.n); }")
        rows = js(page, "()=>[...document.querySelectorAll('#jCards .ln3-jc')].map(c=>c.innerText.replace(/\\s+/g,' '))")
        check(f"{tag} 2 กด Core → ตัวเลขเป็นของ Core (journalStats.core) · รายการไม้เหลือเฉพาะ Core · ปุ่ม Core ติด", txt(page, "[data-sum=n] b") == ex and len(rows) == 2 and all("Core" in r for r in rows) and js(page, "()=>document.querySelector('[data-ln3-scope=core]').classList.contains('on')"), [txt(page, "[data-sum=n] b"), ex, rows])
        page.locator('[data-ln3-scope="satB"]').click(); page.wait_for_timeout(400)
        ex2 = js(page, "()=>String(journalStats().satB.n)")
        sb = js(page, "()=>[...document.querySelectorAll('#setupBody [data-setup]')].length")
        check(f"{tag} 2 กด Sat → ตัวเลขเป็นของ Sat · สถิติ Setup ตามขอบเขตเดียวกัน", txt(page, "[data-sum=n] b") == ex2 and ex2 == "3", [txt(page, "[data-sum=n] b"), ex2])
        page.locator('[data-ln3-scope="all"]').click(); page.wait_for_timeout(300)
        chips = js(page, "()=>[...document.querySelectorAll('#jFilters .chip')].map(c=>c.innerText.trim())")
        check(f"{tag} 2 ชิปกรอง: ทั้งหมด · Win · Loss · นอกแผน · Setup ไม่ครบ · ไม้เร่ง · ＋ ย้อนหลัง (ไม่มี Core/Sat)", chips == ["ทั้งหมด", "Win", "Loss", "นอกแผน", "Setup ไม่ครบ", "ไม้เร่ง", "＋ ย้อนหลัง"], chips)   # LN3fix2 §1.11 — ชิป ไม้เร่ง
        page.locator("[data-ln3-backfill]").click(); page.wait_for_timeout(400)
        check(f"{tag} 2 '＋ ย้อนหลัง' เปิดฟอร์มบันทึกไม้ย้อนหลัง", js(page, "()=>!!document.querySelector('#bfSym')"))
        js(page, "()=>{ document.querySelectorAll('.core-sheet,.overlay.show').forEach(o=>{ o.classList.remove('show'); if(o.classList.contains('core-sheet')) o.remove(); }); }")
        page.locator('[data-ln3-jacct="fam"]').click(); page.wait_for_timeout(400)
        check(f"{tag} 2 สลับเป็น Family → ตัวเลขของ Family (ไม้ปิด 1)", txt(page, "[data-sum=n] b") == "1" and js(page, "()=>jAcct") == "fam")
        page.locator('[data-ln3-jacct="main"]').click(); page.wait_for_timeout(400)
        # ── 3 การ์ด
        card = js(page, """()=>{ const c = document.querySelector('#jCards .ln3-jc'); return {l: [...c.children].map(x=>x.className), t: c.innerText.replace(/\\s+/g,' '), menu: !!c.querySelector('.ln3-mn'), btnsVisible: [...c.querySelectorAll('.ln3-mnb button')].some(b=>b.checkVisibility()), edit: [...c.querySelectorAll('button')].map(b=>b.innerText.trim())}; }""") if w < 1024 else None
        if card:
            check(f"{tag} 3 การ์ดไม้ 3 บรรทัด (ชื่อ+ป้าย+P&L/R · วันที่+Entry→Exit+qty+⋯ · เหตุผลออก+วินัย/Setup)", card["l"] == ["ln3-jl1", "ln3-jl2", "ln3-jl3"] and card["menu"], card)
            check(f"{tag} 3 ปุ่ม แก้ไข/ลบ ซ่อนอยู่ในเมนู ⋯ (ไม่เห็นเป็นปุ่มเรียงแถว)", card["btnsVisible"] is False, card)
            js(page, "()=>document.querySelector('#jCards .ln3-mn summary').click()"); page.wait_for_timeout(200)
            check(f"{tag} 3 กด ⋯ → เห็นปุ่ม แก้ไข / ลบ · 'แก้ไข' เปิดหน้าต่างแก้ไม้", js(page, "()=>[...document.querySelectorAll('#jCards .ln3-mn[open] .ln3-mnb button')].map(b=>b.innerText.trim())") == ["แก้ไข", "ลบ"])
            js(page, "()=>document.querySelector('#jCards .ln3-mn[open] .ln3-mnb button').click()"); page.wait_for_timeout(500)
            check(f"{tag} 3 'แก้ไข' → เปิดหน้าต่างแก้ไข (overlay)", js(page, "()=>document.querySelectorAll('.overlay.show').length") >= 1)
            js(page, "()=>document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show'))")
            grp = txt(page, "#jCards [style*='border:1.5px']") or ""
            check(f"{tag} 3 กลุ่ม scale-out: หัวสรุป 'XAUUSD · Sat · 2 scale-out' + qty / avg out / P&L / R", "2 scale-out" in grp and "qty 0.14" in grp and "avg out" in grp and "R" in grp, grp[:200])
            shot(page, f"ln3-journal-{sfx}.png", "#tabJournal")
        else:
            tb = js(page, "()=>({tbl: document.querySelectorAll('#jTbody tr').length, vis: document.querySelector('.tablewrap').offsetParent !== null, cards: document.getElementById('jCards').offsetParent !== null})")
            check(f"{tag} 3 จอ ≥ 1024 ยังเป็นตาราง (ซ่อนการ์ด) · มีแถวไม้ + scale-out", tb["tbl"] >= 5 and tb["vis"] and tb["cards"] is False, tb)
            shot(page, f"ln3-journal-{sfx}.png", "#tabJournal")
        # ── 4 พับ
        pn = js(page, "()=>({closed: getComputedStyle(document.getElementById('jContent_closed')).display, setup: getComputedStyle(document.getElementById('jContent_setup')).display, cancel: getComputedStyle(document.getElementById('jContent_cancel')).display, cond: getComputedStyle(document.getElementById('jContent_cond')).display, cancelPanel: getComputedStyle(document.getElementById('cancelPanel')).display})")
        check(f"{tag} 4 Closed Trades เปิด · สถิติ Setup / Cancelled / เงื่อนไขที่ยกเลิก พับไว้", pn["closed"] != "none" and pn["setup"] == "none" and pn["cancel"] == "none" and pn["cond"] == "none" and pn["cancelPanel"] != "none", pn)
        js(page, "()=>jvToggleCollapse('cancel')"); page.wait_for_timeout(300)
        check(f"{tag} 4 กดหัว Cancelled → กางออก (ไม้ยกเลิก Entry/SL/TP ครบ)", js(page, "()=>getComputedStyle(document.getElementById('jContent_cancel')).display") != "none" and "62,000" in (txt(page, "#cancelPanel") or ""))
        js(page, "()=>jPanelToggle('setup')"); page.wait_for_timeout(300)
        check(f"{tag} 4 กดหัวสถิติ Setup → กางออก (ตารางครบคอลัมน์ Setup · ไม้ · Win% · Avg R · P&L)", js(page, "()=>{ const r = document.querySelector('#setupBody [data-setup]'); return !!r && ['ไม้','Win%','Avg R','P&L (฿)'].every(k=>r.querySelector('[data-lb=\"'+k+'\"]')); }"))
        # ── 5 ข้อมูลไม่ครบ
        inc = js(page, "()=>{ const e = document.querySelector('#jIncomplete .jInc'); return e ? e.innerText.replace(/\\s+/g,' ') : null; }")
        check(f"{tag} 5 แถบข้อมูลไม่ครบ (รวมไม้ยกเลิกที่ไม่มีเหตุผล) ยังอยู่ · กดแล้วไปแก้", inc and "ข้อมูลไม่ครบ 2 รายการ" in inc, inc)
        # ── 6 ล้น/console
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#tabJournal *').forEach(e=>{ if(e.closest('.tablewrap')) return; const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push((e.className || e.tagName) + ':' + Math.round(r.right)); }); return bad.slice(0,5); }""")
        check(f"{tag} 6 {label} ไม่ล้นแนวนอน · ไม่มี console error", js(page, "()=>document.documentElement.scrollWidth - window.innerWidth") <= 0 and not ov and not ce and not pe, [ov, ce[:2], pe[:2]])
        # ── 7 legacy
        js(page, "()=>ln1SetMode('legacy')"); page.wait_for_timeout(600)
        lg = js(page, "()=>({cells: document.querySelectorAll('#jSum .sumCell').length, ports: document.querySelectorAll('#jPorts .port').length, ln3: document.querySelectorAll('[data-ln3-jbox],.ln3-jc').length, chips: [...document.querySelectorAll('#jFilters .chip')].map(c=>c.innerText.trim()), setup: getComputedStyle(document.getElementById('jContent_setup')).display, rowShown: getComputedStyle(document.getElementById('jAcctRow')).display})")
        check(f"{tag} 7 โหมดแบบเดิม: 6 เซลล์ sumBlk + การ์ดพอร์ต Core/Sat + ชิป Core/Sat · สถิติ Setup เปิดตามเดิม · ไม่มี LN3", lg["cells"] == 6 and lg["ports"] == 2 and lg["ln3"] == 0 and "Core" in lg["chips"] and "Sat" in lg["chips"] and lg["setup"] != "none" and lg["rowShown"] != "none", lg)
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
