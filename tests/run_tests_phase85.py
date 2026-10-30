#!/usr/bin/env python3
"""LN3 — แท็บ Watch แบบ Lean: ลิสต์แถวเดียว (Tier · Phase · เตือน · จุดบัญชี · เรียงด่วนก่อน) · ＋ / ⋯ มุมขวา · รายละเอียด: ปุ่มรองรวมในเมนู ⋯ · ปุ่มหลัก 'เปิดแผน Core →' · 6 แท็บเดิม · Candidate · เทส 85
mock Firestore · Chromium 1440 + 390 + 300 · นาฬิกาปลอม = 2026-10-01 · FF_STUB_BASE = ค่าเริ่ม Lean
ภาพ tests/screenshots/ln3-watch-{list,detail}-{1440,390}.png
รัน: python3 run_tests_phase85.py"""
import copy, json, os
import ff_stub
ff_stub.FF_STUB = ff_stub.FF_STUB_BASE
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase13 as P13
import run_tests_phase24 as p24
import run_tests_phase29 as p29
import run_tests_phase35 as P35

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
txt = P35.txt


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


def launch(pw, w, h):
    browser, context, page, ce, pe, dl = p29.launch(pw, w, h, P35.doc26(), wl=P35.WL)
    p24.set_ff(page, P35.FF_OPEN()); P35.seed(page)
    page.evaluate("()=>{ window.__MOCK_UID='testuid'; }")
    return browser, page, ce, pe, dl


def go(page, view="wl"):
    js(page, "(v)=>{ switchTab('watch'); wlSetView(v); }", view); page.wait_for_timeout(500)


def rows(page):
    return js(page, """()=>[...document.querySelectorAll('.wlR')].map(r=>({sym: r.dataset.sym, t: r.innerText.replace(/\\s+/g,' ').trim(), al: (r.querySelector('[data-ln3-al]')||{dataset:{}}).dataset.ln3Al || null, h: Math.round(r.getBoundingClientRect().height)}))""")


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    b, page, ce, pe, dl = launch(pw, w, h)
    try:
        # ถือ AVGO ในบัญชีหลัก
        js(page, "([t])=>{ const B = getBook('main'); B.trades = t; saveBook('main'); render(); }", [[P13.T("h1", "core", "open", sym="AVGO", entry=300, sl=270, qty=100)]]); page.wait_for_timeout(400)
        dc = copy.deepcopy(P35.dump(page)["users/testuid/watchlist/CALM"]["thesis"]); dc["catalysts"] = [c for c in dc["catalysts"] if c["date"] >= "2026-10-01"]   # ตัด Catalyst ที่ผ่านแล้ว (ไม่ให้ติด 'ควร update')
        P35.put_thesis(page, "CALM", dc)
        go(page)
        R = rows(page); by = {x["sym"]: x for x in R}
        # ── 1 ลิสต์
        check(f"{tag} 1 ลิสต์แถวเดียวต่อหุ้น: AVGO · CALM · NOCARD (3 แถว) ไม่มีบล็อกซ้อนใต้แถว", [x["sym"] for x in R if x["sym"] in ("AVGO", "CALM", "NOCARD")] and len(R) == 3, [x["sym"] for x in R])
        check(f"{tag} 1 AVGO: Tier A · ป้ายเตือน '🟠 ทบทวน' (tripwire review) · มีจุดถืออยู่ + จุด Thesis", "A" in by["AVGO"]["t"] and by["AVGO"]["al"] == "review" and cnt(page, '.wlR[data-sym="AVGO"] .wlDotH') == 1 and cnt(page, '.wlR[data-sym="AVGO"] .wlDotR.ok') == 1, by["AVGO"])
        check(f"{tag} 1 CALM (ไม่มีเตือน) → 📅 Catalyst ใกล้สุด 1 ตัว (งานประชุมนักลงทุน 20 พ.ย.) · NOCARD → 'รอสร้าง Thesis'", by["CALM"]["al"] is None and "📅" in by["CALM"]["t"] and "20 พ.ย." in by["CALM"]["t"] and "รอสร้าง Thesis" in by["NOCARD"]["t"], [by["CALM"]["t"], by["NOCARD"]["t"]])
        order = [x["sym"] for x in R]
        check(f"{tag} 1 เรียงด่วนก่อน: AVGO (ทบทวน) → NOCARD (ไม่มี Thesis) → CALM (ปกติ)", order == ["AVGO", "CALM", "NOCARD"], order)   # TD4a: เรียง ★ → มีข้อมูล → ลำดับเดิม (CALM มี Thesis ขึ้นก่อน NOCARD)
        # Tripwire พัง → ขึ้นบนสุด + ⛔
        d = copy.deepcopy(dc); d["tripwires"][0]["level"] = "broken"
        P35.put_thesis(page, "CALM", d); go(page)
        R2 = rows(page)
        check(f"{tag} 1 Tripwire พัง → '⛔ Tripwire' สีแดง · ขึ้นแถวบนสุด", R2[0]["sym"] == "CALM" and R2[0]["al"] == "broken" and "⛔ Tripwire" in R2[0]["t"], R2[0])
        d["tripwires"][0]["level"] = "ok"; d["tripwires"][1]["level"] = "ok"; d["asOf"] = "2026-01-01"; d["date"] = "2026-01-01"; d["catalysts"] = [{"event": "งบ Q1", "date": "2026-02-01", "date_status": "confirmed", "thesis": 1}]
        P35.put_thesis(page, "CALM", d); go(page)
        st = [x for x in rows(page) if x["sym"] == "CALM"][0]
        check(f"{tag} 1 Thesis เก่า/Catalyst ผ่านแล้ว → 'ควร update'", st["al"] == "stale", st)
        # หัว
        hd = js(page, """()=>{ const h = document.querySelector('[data-ln3-wl2]'); const t = document.querySelector('.wlListHead'); return {pills: [...document.querySelectorAll('.wlHead .rsDeepBtn')].map(x=>x.innerText.replace(/\\s+/g,' ').trim()), ports: [...h.querySelectorAll('.wlPills .rsDeepBtn')].map(x=>x.innerText.trim()), add: !!h.querySelector('[data-ln3-add]'), menu: !!h.querySelector('[data-ln3-listmenu]'), flt: !!h.querySelector('[data-flt-btn]'), oldAdd: [...t.querySelectorAll('button')].filter(b=>/เพิ่มหุ้น$|^📥 Import$/.test(b.innerText.trim())).map(b=>b.innerText.trim()), right: (()=>{ const r = h.querySelector('.ln3-wlr').getBoundingClientRect(), p = h.getBoundingClientRect(); return Math.round(p.right - r.right); })()}; }""")
        check(f"{tag} 1 หัวลิสต์: Watchlist n | Ideas n | Cand. n · ตลาด All | US | TH · Filter · ＋ · ⋯ (มุมขวา)", len(hd["pills"]) == 3 and hd["pills"][0].startswith("Ideas") and hd["pills"][2].startswith("Watchlist") and hd["ports"] == ["All", "US", "TH"] and hd["add"] and hd["menu"] and hd["flt"] and hd["right"] <= 8, hd)
        check(f"{tag} 1 ไม่มีปุ่ม '＋ เพิ่มหุ้น' / 'Import' เป็นตัวหนังสือในลิสต์ (รวมเป็น ＋ และ ⋯)", hd["oldAdd"] == [], hd["oldAdd"])
        page.locator("[data-ln3-listmenu]").click(); page.wait_for_timeout(300)
        mn = txt(page, ".ltMenu") or ""
        check(f"{tag} 1 ⋯ ในลิสต์: '📥 Import' อยู่ในเมนู", "Import" in mn, mn)
        page.keyboard.press("Escape"); js(page, "()=>{ wlMenu=''; renderWatchlist(); }"); page.wait_for_timeout(200)
        page.locator("[data-ln3-add]").click(); page.wait_for_timeout(400)
        check(f"{tag} 1 ＋ (TD4b: Add on candidate) เปิดแผงเพิ่มเป็น Candidate (ไม่ใช่ฟอร์มเพิ่มเข้า Watchlist)", js(page, "()=>document.querySelectorAll('[data-wl-addc]').length") == 1 and js(page, "()=>[...document.querySelectorAll('.overlay.show')].length") == 0)
        js(page, "()=>{ document.querySelectorAll('.overlay.show').forEach(o=>o.classList.remove('show')); }")
        shot(page, f"ln3-watch-list-{sfx}.png", ".wlList")
        # ── 2 รายละเอียด
        js(page, "()=>{ wlOpen('AVGO','sum'); }"); page.wait_for_timeout(500)
        dh = js(page, """()=>{ const h = document.querySelector('[data-ln3-dh]'); if(!h) return null; return {t: h.innerText.replace(/\\s+/g,' ').trim(), btns: [...h.querySelectorAll('.wlActs button')].map(b=>b.innerText.trim()), menu: !!h.querySelector('[data-lt-menu]'), tabs: [...h.querySelectorAll('[data-lt-tab]')].map(b=>b.dataset.ltTab), meta: (h.querySelector('[data-ln3-meta]')||{}).innerText, alert: h.querySelectorAll('[data-wl-alert]').length, nxc: h.querySelectorAll('[data-lt-nxc]').length, rev: h.querySelectorAll('[data-rev-btn]').length, vis: [...h.querySelectorAll('button,a')].filter(b=>b.offsetParent && /แก้ไข|ลบ|Import/.test(b.innerText) && !b.closest('.ltMenu')).map(b=>b.innerText.trim())}; }""")
        check(f"{tag} 2 หัวรายละเอียด: ปุ่มหลักปุ่มเดียว 'เปิดแผน Core →' · ⋯ อยู่มุมขวา · ไม่มีปุ่ม แก้ไข/ลบ/Import เรียงแถว", dh and dh["btns"] == ["เปิดแผน Core →"] and dh["menu"] and dh["vis"] == [], dh)
        check(f"{tag} 2 มี 6 แท็บเดิม (สรุป · มุมมอง/กราฟ · ธุรกิจ · ทำไม · ติดตาม · ออก)", dh["tabs"] == ["sum", "view", "biz", "why", "trk", "exit"], dh["tabs"])
        check(f"{tag} 2 บรรทัดข้อมูลเดียว: Industry · Phase · Thesis (โหมด · วันที่) · สถานะ · ถือ: บัญชี (n ไม้)", dh["meta"] and "Semis" in dh["meta"] and "Thesis lite · 28 ก.ย." in dh["meta"] and "ถือ:" in dh["meta"] and "1 ไม้" in dh["meta"], dh["meta"])
        check(f"{tag} 2 เตือน Tripwire ในหัว (1 แถบ) · ไม่ซ้ำในแท็บสรุป · 📅 ใกล้สุด · ลิงก์รายได้แยกส่วน", dh["alert"] == 1 and cnt(page, ".wlOv [data-wl-alert]") == 0 and dh["nxc"] == 1 and dh["rev"] == 1, dh)
        shot(page, f"ln3-watch-detail-{sfx}.png", ".wlDPanel")   # LN3fix — ถ่ายก่อนกดเปิดแผน Core (ภาพไม่ถูกฟอร์มบัง)
        page.locator("[data-lt-menu]").click(); page.wait_for_timeout(300)
        items = js(page, "()=>[...document.querySelectorAll('.ltMenu [role=menuitem]')].map(b=>b.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 2 เมนู ⋯: ✎ แก้ไข · 📥 Import · Export JSON · ทบทวน (ประวัติ) · ✕ ลบ", len(items) == 5 and items[0].startswith("✎ แก้ไข") and "Import" in items[1] and items[2] == "Export JSON" and items[3].startswith("ทบทวน") and items[4].startswith("✕ ลบ"), items)
        js(page, "()=>{ wlMenu=''; renderWatchlist(); }")
        page.locator("[data-c-open-plan]").click(); page.wait_for_timeout(600)
        check(f"{tag} 2 'เปิดแผน Core →' พาไปแท็บแผน (Core)", js(page, "()=>activeTab") == "plan")
        js(page, "()=>{ coreSheetClose(); }")   # LN3fix — ปิดฟอร์มแผน Core ที่เปิดจาก 'เปิดแผน Core →' (ไม่ให้บังหน้ารายละเอียด)
        go(page); js(page, "()=>{ wlOpen('AVGO','sum'); }"); page.wait_for_timeout(300)
        # แท็บเดิมมีเนื้อหาครบ
        okt = {}
        for k in ("sum", "view", "biz", "why", "trk", "exit"):
            js(page, "(k)=>wlSetSub(k)", k); page.wait_for_timeout(250)
            okt[k] = len((txt(page, ".wlDBody") or "")) > 20
        check(f"{tag} 2 ทั้ง 6 แท็บมีเนื้อหา", all(okt.values()), okt)
        js(page, "()=>wlSetSub('trk')"); page.wait_for_timeout(250)
        check(f"{tag} 2 แท็บ ติดตาม: Catalysts + โน้ตของฉัน (＋ โน้ต) ยังอยู่", cnt(page, "[data-wl-sec=cat]") == 1 and cnt(page, "[data-wl-sec=blk]") == 1 and cnt(page, "[data-wl-addnote]") == 2)
        js(page, "()=>wlSetSub('exit')"); page.wait_for_timeout(250)
        check(f"{tag} 2 แท็บ ออกเมื่อ: Tripwire + ปุ่ม 'ชนแล้ว' (กดเอง) ยังอยู่", cnt(page, "[data-lt-tw]") >= 1 and cnt(page, "[data-lt-hit]") >= 1)
        # ── 3 Candidate
        go(page, "cand")
        js(page, "()=>wlOpen('CAND1')"); page.wait_for_timeout(500)
        cd = js(page, """()=>{ const h = document.querySelector('[data-ln3-dh]'); return h ? {btns: [...h.querySelectorAll('.wlActs button')].map(b=>b.innerText.trim()), dis: [...h.querySelectorAll('.wlActs button')].map(b=>b.disabled), menu: !!h.querySelector('[data-lt-menu]')} : null; }""")
        check(f"{tag} 3 Candidate: ปุ่มหลัก '＋ เพิ่มเข้า Watchlist' · ⋯ เมนู · แถวลิสต์มี CAND", cd and cd["btns"] == ["＋ เพิ่มเข้า Watchlist"] and cd["menu"] and any("CAND" in x["t"] for x in rows(page)), cd)
        # ── 4 Ideas (แบบเดิม)
        go(page, "idea")
        check(f"{tag} 4 หน้า Ideas ใช้แบบเดิม (แท็บ Watchlist/Ideas/Cand. ยังสลับได้)", cnt(page, ".wlm") == 1 and cnt(page, "[data-wl-view]") == 3)
        # ── 5 จอใหญ่
        go(page)
        if w >= 1024:
            lay = js(page, "()=>{ const l = document.querySelector('.wlList').getBoundingClientRect(), d = document.querySelector('.wlDet').getBoundingClientRect(); return [Math.round(l.right), Math.round(d.left)]; }")
            check(f"{tag} 5 จอ ≥ 1024: ลิสต์ซ้าย / รายละเอียดขวา", lay[0] <= lay[1] + 2, lay)
        # ── 6 ล้น + console
        ov = js(page, """()=>{ const W = window.innerWidth, bad = []; document.querySelectorAll('#watchGroups *').forEach(e=>{ if(e.closest('.ltTable, table, .ltTabs')) return; const r = e.getBoundingClientRect(); if(r.width && r.right > W + 1) bad.push((e.className || e.tagName) + ':' + Math.round(r.right)); }); return bad.slice(0,5); }""")
        check(f"{tag} 6 {label} ไม่ล้นแนวนอน · ไม่มี console error", js(page, "()=>document.documentElement.scrollWidth - window.innerWidth") <= 0 and not ov and not ce and not pe, [ov, ce[:2], pe[:2]])
        # ── 7 legacy
        js(page, "()=>ln1SetMode('legacy')"); js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(500)
        lg = js(page, """()=>({add: [...document.querySelectorAll('.wlListHead button')].some(b=>/Add on candidate/.test(b.innerText)), ports: [...document.querySelectorAll('.wlHead .wlPills')].pop().innerText.replace(/\\s+/g,' '), ln3: document.querySelectorAll('[data-ln3-wl2],[data-ln3-dh],.ln3r').length})""")
        js(page, "()=>wlOpen('AVGO','sum')"); page.wait_for_timeout(300)
        acts = js(page, "()=>[...document.querySelectorAll('.wlActs button')].map(b=>b.innerText.trim())")
        check(f"{tag} 7 โหมดแบบเดิม: '＋ Add on candidate' + Core.US/Core.TH + ปุ่ม ✎ ✕ 📥 เรียงแถวตามเดิม · ไม่มี LN3", lg["add"] and "Core.US" in lg["ports"] and lg["ln3"] == 0 and "✎ แก้ไข" in acts and "✕ ลบ" in acts, [lg, acts])
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
