#!/usr/bin/env python3
"""LN3 — แท็บ Port แบบ Lean: กล่องสรุปเดียว · ปุ่ม รวม/บัญชี · บรรทัดบัญชี · โครงพอร์ต · การ์ด Core (วงกลมเดียวสลับ หุ้น/Industry · พับความเสี่ยง Core) · การ์ด Sat · เทส 83
mock Firestore · Chromium 1440 + 390 + 300 · นาฬิกาปลอม 2026-10-01 ไทย · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-port-{all,main}-{1440,390}.png
รัน: python3 run_tests_phase83.py"""
import json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase37 as P37
import run_tests_phase51 as P51
import run_tests_phase54 as P54
import run_tests_phase77 as P77
import run_tests_phase78 as P78

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P37.js
overflow = P54.overflow
cnt, sat_t, put = P78.cnt, P78.sat_t, P78.put


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(600)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def launch(pw, w, h, opt=50000):
    browser, context, page, ce, pe, dl = P54.launch(pw, w, h, P77.fixture(opt))
    P51.fresh(page, None)
    page.evaluate("()=>{ try{ localStorage.removeItem('ln3_port_acc'); }catch(e){} }")
    return browser, page, ce, pe


def core_t(id, sym, qty, price, acct="main"):
    return P13.T(id, "core", "open", sym=sym, entry=price, sl=price * 0.9, qty=qty)


def go(page):
    js(page, "()=>{ switchTab('mix'); }"); page.wait_for_timeout(500)


def body(page, sel="#mixBody"):
    return js(page, "(s)=>{ const e=document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe = launch(pw, w, h)
    try:
        page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "watchlist", "NVDA"], {"ticker": "NVDA", "market": "US", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"}]); page.wait_for_timeout(600)
        CORE = [core_t("c1", "NVDA", 100, 3500), core_t("c2", "AVGO", 50, 6000)]
        put(page, CORE + [sat_t("m1", "open", entry=4180, sl=4117, qty=0.10)], "main")
        put(page, [core_t("c3", "NVDA", 20, 3500)], "fam")
        go(page)
        # ── 1 กล่องสรุป
        sm = js(page, """()=>{ const s = document.getElementById('mixSummary'); return {boxes: s.querySelectorAll('[data-ln3-sum]').length, stats: s.querySelectorAll('.stat').length, t: s.innerText.replace(/\\s+/g,' '), eye: s.querySelectorAll('.privEye').length}; }""")
        check(f"{tag} 1 กล่องสรุปเดียว (ไม่ใช่การ์ด 4 ใบ): ทุนรวม · ถือครอง · Open Risk รวม · Realized · มีปุ่มซ่อนตัวเลข 👁", sm["boxes"] == 1 and sm["stats"] == 0 and all(k in sm["t"] for k in ("ทุนรวม 2 บัญชี", "ถือครอง", "Open Risk รวม", "Realized สะสม", "เงินสด")) and sm["eye"] >= 1, sm)
        exp = js(page, """()=>{ const st = acctAllStates().map(mixAcctStats); const sum = st.reduce((a,s)=>({cap:a.cap+s.cap, held:a.held+s.held, risk:a.risk+s.risk}), {cap:0,held:0,risk:0}); return {cap: '฿'+fmt0(sum.cap), held: fmt2(sum.held/sum.cap*100)+'%', risk: fmt2(sum.risk/sum.cap*100)+'%'}; }""")
        check(f"{tag} 1 ตัวเลขกล่องสรุป = ผลคำนวณเดิม (mixAcctStats รวมสองบัญชี)", exp["cap"] in sm["t"] and exp["held"] in sm["t"] and exp["risk"] in sm["t"], [exp, sm["t"]])
        js(page, "()=>{ document.querySelector('#mixSummary .privEye').click(); }"); page.wait_for_timeout(400)
        masked = js(page, "()=>document.getElementById('mixSummary').innerText")
        check(f"{tag} 1 กด 👁 → ตัวเงินในกล่องถูกซ่อน (฿X,XXX) · เปอร์เซ็นต์ยังเห็น", "฿X" in masked and "%" in masked, masked[:200])
        js(page, "()=>{ document.querySelector('#mixSummary .privEye').click(); }"); page.wait_for_timeout(300)
        # ── 2 ปุ่มบัญชี
        sw = js(page, "()=>[...document.querySelectorAll('[data-ln3-accsw] button')].map(b=>[b.innerText.trim(), b.classList.contains('on')])")
        check(f"{tag} 2 ปุ่ม รวม | บัญชีหลัก | Family · ค่าเริ่ม = รวม", sw and [x[0] for x in sw][0] == "รวม" and len(sw) == 3 and sw[0][1] is True, sw)
        all_ = js(page, "()=>({pies: document.querySelectorAll('#mixBody .piechart').length, structs: document.querySelectorAll('[data-pool-line]').length, line: !!document.querySelector('[data-ln3-accline]'), old: document.querySelectorAll('.mixAcctHead,.mixPort').length})")
        check(f"{tag} 2 โหมดรวม: วงกลมเดียวของ Core (+ Sat ถ้ามีหุ้น/ETF) · โครงพอร์ตทุกบัญชี · ไม่มีบัญชีเรียงซ้อนแบบเดิม", all_["pies"] == 1 and all_["structs"] == 1 and all_["old"] == 0 and not all_["line"], all_)
        shot(page, f"ln3-port-all-{sfx}.png", "#view-mix, #mixBody")
        page.locator('[data-ln3-acc="main"]').dispatch_event('click'); page.wait_for_timeout(500)
        line = body(page, "[data-ln3-accline]")
        e2 = js(page, "()=>{ const s = mixAcctStats(acctAllStates().find(e=>e.acct.id==='main')); const p=(x,b)=>b>0?x/b*100:0; return `ทุน ฿${fmt0(s.cap)} · ถือครอง ${fmt2(p(s.held,s.cap))}% · Open Risk ${fmt2(p(s.risk,s.cap))}%`; }")
        nm = js(page, "()=>acctList.find(a=>a.id==='main').name")
        check(f"{tag} 2 เลือกบัญชีหลัก → บรรทัด 'ทุน · ถือครอง · Open Risk' ตรงผลคำนวณ · ไม่ซ้ำชื่อบัญชี", line == e2 and nm not in line, [line, e2])
        check(f"{tag} 2 เลือกบัญชีหลัก → โครงพอร์ตเหลือบัญชีเดียว · จำค่าไว้ (localStorage) แม้วาดใหม่", cnt(page, "[data-pool-line]") == 1 and js(page, "()=>localStorage.getItem('ln3_port_acc')") == "main" and (js(page, "()=>{ renderPortfolioMix(); return document.querySelector('[data-ln3-acc=main]').classList.contains('on'); }")))
        # ── 3 โครงพอร์ต
        st = js(page, "()=>{ const e = document.querySelector('[data-pool-line]'); e.open = true; return {rows: [...e.querySelectorAll('[data-pool-bar]')].map(r=>r.dataset.poolBar)}; }")
        check(f"{tag} 3 โครงพอร์ต (RG2b: เส้นถัง): แถบ Winner/Ladder/Sat ในแถบพับ", st["rows"] == ["winner", "ladder", "sat"], st)
        page.locator('[data-ln3-acc="fam"]').dispatch_event('click'); page.wait_for_timeout(500)
        check(f"{tag} 3 Family (มีถัง Option) → แถว 'อื่น ๆ (เดิม) · ถัง Option' ยังอยู่ อ่านอย่างเดียว", cnt(page, "[data-pv2-row=legacy]") == 1 and "ถัง Option" in (js(page, "()=>document.querySelector('[data-pv2-row=legacy]').textContent") or ""))
        page.locator('[data-ln3-acc="main"]').dispatch_event('click'); page.wait_for_timeout(500)
        # ── 4 Core
        core = js(page, """()=>{ const c = document.querySelector('[data-ln3-core]'); const h = c.querySelector('.ln3-ph'); return {head: h.innerText.replace(/\\s+/g,' ').trim(), pies: c.querySelectorAll('.piechart').length, seg: [...c.querySelectorAll('[data-ln3-by]')].map(b=>[b.dataset.ln3By, b.classList.contains('on')]), leg: c.querySelector('.pielegend').innerText.replace(/\\s+/g,' '), fold: c.querySelector('[data-ln3-riskfold] summary').innerText}; }""")
        check(f"{tag} 4 การ์ด Core: หัว 'Core Port · DD x% · สถานะ' ไม่ซ้ำทุน (ไม่มีคำว่า ทุน/฿ ในหัว)", core["head"].startswith("Core Port") and "DD" in core["head"] and "ปกติ" in core["head"] and "ทุน" not in core["head"] and "฿" not in core["head"], core["head"])
        check(f"{tag} 4 วงกลมเดียว · ปุ่มสลับ หุ้น | Industry (ค่าเริ่ม หุ้น) · legend แสดงหุ้นที่ถือ + เงินสด", core["pies"] == 1 and core["seg"] == [["sym", True], ["ind", False]] and "NVDA" in core["leg"] and "AVGO" in core["leg"] and "เงินสด" in core["leg"], core)
        page.locator('[data-ln3-by="ind"]').click(); page.wait_for_timeout(400)
        leg2 = body(page, "[data-ln3-core] .pielegend")
        check(f"{tag} 4 สลับเป็น Industry → วงกลมเดิมเปลี่ยน legend เป็น Industry (ไม่มีชื่อหุ้น) · ยังมี 1 วง", cnt(page, "[data-ln3-core] .piechart") == 1 and "NVDA" not in leg2 and "เงินสด" in leg2 and ("ไม่ระบุ" in leg2 or "%" in leg2), leg2)
        page.locator('[data-ln3-by="sym"]').click(); page.wait_for_timeout(400)
        go_ = js(page, "()=>{ const e = document.querySelector('[data-ln3-lg-go=NVDA]'); return e ? e.getAttribute('onclick') : null; }")
        check(f"{tag} 4 ชื่อหุ้นใน legend กดแล้วไปหุ้นนั้น (wlOpen) เมื่อหุ้นอยู่ใน Watchlist", go_ and "wlOpen('NVDA'" in go_, go_)
        js(page, "()=>{ document.querySelector('[data-ln3-lg-go=NVDA]').click(); }"); page.wait_for_timeout(500)
        check(f"{tag} 4 กดแล้วไปแท็บ Watch · เลือก NVDA", js(page, "()=>activeTab==='watch' && wlSel==='NVDA'"), js(page, "()=>[activeTab, wlSel]"))
        go(page)
        js(page, "()=>{ const d = document.querySelector('[data-ln3-riskfold]'); d.open = true; }"); page.wait_for_timeout(200)
        rk = body(page, "[data-ln3-riskfold]")
        check(f"{tag} 4 พับ 'ความเสี่ยง Core (ชั้น 2 · W/L · บันได)': ถึง Stop ตอนนี้ · เต็ม · Ladder · เงินว่าง (RG2b: ไม่มีเพดานรวม/L รวม/บันไดใหม่)", all(k in rk for k in ("ถึง Stop ตอนนี้", "เต็ม", "Ladder", "เงินว่าง")) and "ความเสี่ยง Core (ชั้น 2 · W/L · บันได)" in rk, rk)
        # ── 5 Sat
        sat = js(page, "()=>{ const c = document.querySelector('[data-ln3-sat]'); return {head: c.querySelector('.ln3-ph').innerText.replace(/\\s+/g,' ').trim(), t: c.innerText.replace(/\\s+/g,' '), pies: c.querySelectorAll('.piechart').length}; }")
        check(f"{tag} 5 การ์ด Sat: หัว 'Sat · DD x%' ไม่ซ้ำทุน · มีไม้ฟิวเจอร์ค้าง = ไม่มีวงกลม · ชี้ไปดูที่แท็บแผน", sat["head"].startswith("Sat") and "DD" in sat["head"] and "ทุน" not in sat["head"] and "ไม้ค้าง 1 ไม้" in sat["t"] and "แท็บแผน" in sat["t"] and sat["pies"] == 0, sat)
        put(page, CORE, "main"); go(page)
        check(f"{tag} 5 ไม่มีไม้ → 'ไม่มีไม้ค้าง'", "ไม่มีไม้ค้าง" in (body(page, "[data-ln3-sat]") or ""))
        put(page, CORE + [P13.T("s1", "satB", "open", sym="NVDA", entry=100, sl=90, qty=10, cur="USD")], "main"); go(page)
        check(f"{tag} 5 Sat ถือหุ้น/ETF (NVDA) → โชว์วงกลมเหมือน Core", cnt(page, "[data-ln3-sat] .piechart") == 1 and "NVDA" in (body(page, "[data-ln3-sat] .pielegend") or ""))
        shot(page, f"ln3-port-main-{sfx}.png", "#view-mix, #mixBody")
        # ── 6 ล้น/console
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#mixSummary *, #mixBody *').forEach(e=>{ const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push(e.className || e.tagName); }); return bad.slice(0,5); }""")
        check(f"{tag} 6 {label} ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ov and not ce and not pe, [overflow(page), ov, ce[:2], pe[:2]])
    finally: b.close()

    # ── 7 บัญชีเดียว + legacy
    b, page, ce, pe = launch(pw, w, h, opt=0)
    try:
        js(page, "()=>{ acctList = acctList.filter(a=>a.id==='main'); }")
        go(page)
        check(f"{tag} 7 มีบัญชีเดียว → ไม่มีปุ่มเลือกบัญชี · ยังมีกล่องสรุป/การ์ด Core", cnt(page, "[data-ln3-accsw]") == 0 and cnt(page, "[data-ln3-sum]") == 1 and cnt(page, "[data-ln3-core]") == 1)
        js(page, "()=>ln1SetMode('legacy')"); go(page)
        lg = js(page, "()=>({stats: document.querySelectorAll('#mixSummary .stat').length, ln3: document.querySelectorAll('[data-ln3-sum],[data-ln3-core],[data-ln3-accsw]').length, mixPort: document.querySelectorAll('.mixPort').length})")
        check(f"{tag} 7 โหมดแบบเดิม: การ์ดสรุป 4 ใบ + พอร์ตเรียงซ้อนเดิม · ไม่มี LN3", lg["stats"] == 4 and lg["ln3"] == 0 and lg["mixPort"] >= 2, lg)
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
