#!/usr/bin/env python3
"""NUM2 — เก็บกวาดตัวเลขรอบ 2 (luckyWins/goodLosses ใช้เกณฑ์ BE · sheet อัปเดตราคาเมื่อการ์ดใช้ auto · ffBizDaysSince เวลาไทย) · เทส 46
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม (P37 = 2026-10-01 · P43 = 2026-10-05) · ภาพ tests/screenshots/num2-px-sheet-auto-{1440,390}.png
รัน: python3 run_tests_phase46.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase37 as P37
import run_tests_phase38 as P38
import run_tests_phase42 as P42
import run_tests_phase43 as P43

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = P43.SHOTS
ENGINE = P43.ENGINE
results = P43.results
check, js, txt = P43.check, P43.js, P43.txt
INDEX_HTML = os.path.join(HERE, "..", "index.html")


def lucky_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    b, c, page, ce, pe, dl = P37.launch(pw, w, h, P37.doc37(), cards={})
    try:
        tr = [P42.pnl_trade(1, 0.4, discScore=1), P42.pnl_trade(2, 1, discScore=1), P42.pnl_trade(3, -0.3, discScore=3), P42.pnl_trade(4, -1, discScore=3),
              dict(P37.T("p5", "core", "open", sym="S5", entry=100, sl=90, qty=1, cur="THB", date="2026-09-10", openedAt="2026-09-10"), discScore=1)]
        P37.put_trades(page, "main", tr)
        s = js(page, "()=>{ const o=journalStats().overall; return {lucky:o.luckyWins, good:o.goodLosses, n:o.n}; }")
        check(f"{tag} 1 ผสม: +0.4(1) +1(1) −0.3(3) −1(3) + ไม้เปิด(1) → luckyWins 1 (เฉพาะ +1) · goodLosses 2 (−0.3 BE + −1 loss) · ไม้เปิดไม่นับ", s == {"lucky": 1, "good": 2, "n": 4}, json.dumps(s))
        P37.put_trades(page, "main", [P42.pnl_trade(1, 0.4, discScore=1)])
        a = js(page, "()=>journalStats().overall.luckyWins")
        P37.put_trades(page, "main", [P42.pnl_trade(2, 1, discScore=1)])
        b2 = js(page, "()=>journalStats().overall.luckyWins")
        P37.put_trades(page, "main", [P42.pnl_trade(3, -0.3, discScore=3)])
        c3 = js(page, "()=>journalStats().overall.goodLosses")
        P37.put_trades(page, "main", [P42.pnl_trade(4, -1, discScore=3)])
        d4 = js(page, "()=>journalStats().overall.goodLosses")
        check(f"{tag} 1 +0.4 discScore 1 → luckyWins 0 ({a}) · +1 discScore 1 → 1 ({b2}) · −0.3 discScore 3 → goodLosses 1 ({c3}) · −1 discScore 3 → 1 ({d4})", [a, b2, c3, d4] == [0, 1, 1, 1], json.dumps([a, b2, c3, d4]))
        P37.put_trades(page, "main", [dict(P37.T("po", "core", "open", sym="SO", entry=100, sl=90, qty=1, cur="THB", date="2026-09-10", openedAt="2026-09-10"), discScore=1)])
        o = js(page, "()=>{ const s=journalStats().overall; return [s.luckyWins, s.goodLosses]; }")
        check(f"{tag} 1 ยังไม่ปิด (ไม่มี P&L · pnlOutcome null) → ไม่นับทั้งคู่", o == [0, 0] and js(page, "()=>pnlOutcome(state.trades.find(t=>t.id==='po'))") is None, json.dumps(o))
        P37.put_trades(page, "main", [P42.pnl_trade(1, 1, discScore=1), P42.pnl_trade(2, 2, discScore=0)])
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(400)
        dec = txt(page, '[data-jsum="decision"]') or ""
        check(f"{tag} 1 ข้อความ 'ชนะแบบไม่ตามแผน 2 ไม้ — อย่านับเป็นฝีมือ' ตรงตัวเลข", "ชนะแบบไม่ตามแผน 2 ไม้" in dec, dec)
        P37.put_trades(page, "main", [P42.pnl_trade(1, 0.4, discScore=1)])
        js(page, "()=>{ switchTab('journal'); setJFilter('all'); }"); page.wait_for_timeout(400)
        dec = txt(page, '[data-jsum="decision"]') or ""
        check(f"{tag} 1 ไม้ +0.4 (BE) discScore 1 → ไม่ขึ้น 'ชนะแบบไม่ตามแผน'", "ชนะแบบไม่ตามแผน" not in dec, dec)
        check(f"{tag} 5 ไม่มี console error (luckyWins)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()


def px_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    vals = lambda pg: js(pg, "()=>[document.getElementById('cpxPx').value, document.getElementById('cpxEma').value, document.getElementById('cpxDate').value]")
    b, c, page, ce, pe, dl = P43.launch(pw, w, h, {"AAA": P43.px_doc("AAA", 105, ema=110)})
    try:
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        check(f"{tag} 2 auto 105/110 (2 ต.ค.) ใหม่กว่ากรอก 100 (26 ก.ย.) → sheet: ช่อง 105 / 110 · วันที่ 2026-10-02", vals(page) == ["105", "110", "2026-10-02"], json.dumps(vals(page)))
        check(f"{tag} 2 มีบรรทัด 'ตอนนี้ใช้ราคาอัตโนมัติ — แก้ตัวเลขแล้วบันทึกเพื่อใช้ค่าที่กรอกเองแทน'", "ตอนนี้ใช้ราคาอัตโนมัติ — แก้ตัวเลขแล้วบันทึกเพื่อใช้ค่าที่กรอกเองแทน" in (txt(page, "[data-px-usingauto]") or ""))
        page.locator(".core-sheet").first.screenshot(path=os.path.join(SHOTS, f"num2-px-sheet-auto-{sfx}.png"))
        js(page, "()=>corePxSave()"); page.wait_for_timeout(500)
        s = P43.state(page); dc = P43.db_card(page)
        check(f"{tag} 2 กดบันทึกโดยไม่แก้ → การ์ดยัง 105 / 110 (วันที่ 2 ต.ค.)", s["px"] == 105 and s["emaW"] == 110 and s["pxDate"] == "2026-10-02" and dc["px"] == 105 and dc["emaW"] == 110, json.dumps([s, {k: dc.get(k) for k in ("px", "emaW", "pxDate")}]))
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx"); page.fill("#cpxPx", "106"); page.wait_for_timeout(100)
        js(page, "()=>corePxSave()"); page.wait_for_timeout(500)
        s = P43.state(page)
        check(f"{tag} 2 แก้เป็น 106 → การ์ด 106 (กรอกเองชนะ · src=manual)", s["px"] == 106 and s["src"] == "manual", json.dumps(s))
        check(f"{tag} 5 ไม่มี console error (sheet auto)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    # ไม่มี auto → ค่ากรอกเอง + ศุกร์ล่าสุด
    b, c, page, ce, pe, dl = P43.launch(pw, w, h)
    try:
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        check(f"{tag} 3 ไม่มี auto → ช่อง = ค่ากรอกเอง 100 / 95 · วันที่ = ศุกร์ล่าสุด 2026-10-02 · ไม่มีบรรทัดใช้ auto", vals(page) == ["100", "95", "2026-10-02"] and txt(page, "[data-px-usingauto]") is None, json.dumps(vals(page)))
    finally:
        b.close()
    b, c, page, ce, pe, dl = P43.launch(pw, w, h, {"AAA": P43.px_doc("AAA", 160, ema=110, suspect=True)})
    try:
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        check(f"{tag} 3 auto suspect → ช่อง = ค่ากรอกเอง 100 / 95 + ศุกร์ล่าสุด · มีบรรทัด 'ราคาอัตโนมัติล่าสุด…' ตามเดิม", vals(page) == ["100", "95", "2026-10-02"] and "ราคาอัตโนมัติล่าสุด" in (txt(page, "[data-px-autoline]") or ""), json.dumps(vals(page)))
    finally:
        b.close()
    b, c, page, ce, pe, dl = P43.launch(pw, w, h, {"AAA": P43.px_doc("AAA", 105, close_date="2026-09-20", ema=110)}, None, {"cw": P43.w_card(px=100, px_date="2026-09-26", ema=95)})
    try:
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        check(f"{tag} 3 auto เก่ากว่าที่กรอก (20 ก.ย. < 26 ก.ย.) → ช่อง = ค่ากรอกเอง 100 / 95 + ศุกร์ล่าสุด", vals(page) == ["100", "95", "2026-10-02"], json.dumps(vals(page)))
    finally:
        b.close()


def ff_tests(pw):
    tag = f"[{ENGINE}]"
    html = open(INDEX_HTML, encoding="utf-8").read()
    thai = "function thaiToday(){" + html.split("function thaiToday(){")[1].split("\n")[0]
    biz = "function ffBizDaysSince(iso){" + html.split("function ffBizDaysSince(iso){")[1].split("\nasync function ffLoadJson")[0]
    src = thai + "\n" + biz
    clock = P38.CLOCK_JS
    lk = {"headless": True}
    from run_tests_phase4 import CHROMIUM_PATH
    if CHROMIUM_PATH: lk["executable_path"] = CHROMIUM_PATH
    browser = pw.chromium.launch(**lk)
    try:
        def run(tz, iso, dates):
            ctx = browser.new_context(timezone_id=tz); ctx.add_init_script("(" + clock + ")(" + json.dumps(iso) + ")")
            pg = ctx.new_page(); pg.goto("about:blank")
            out = pg.evaluate("([src, dates])=>{ const f = new Function(src + '; return {t: thaiToday(), r: ' + JSON.stringify(dates) + '.map(d=>ffBizDaysSince(d))};'); return f(); }", [src, dates])
            ctx.close(); return out
        D = ["2026-10-05", "2026-10-02", "2026-10-01", "2026-09-28", "2026-09-26", "2026-10-04", "bad", ""]
        # จันทร์ 5 ต.ค. 05:00 ไทย = อาทิตย์ 4 ต.ค. 22:00 UTC = อาทิตย์ 18:00 นิวยอร์ก
        ny = run("America/New_York", "2026-10-04T22:00:00Z", D); bk = run("Asia/Bangkok", "2026-10-04T22:00:00Z", D)
        check(f"{tag} 4 จันทร์ 05:00 ไทย: เครื่อง New_York = เครื่อง Bangkok ทุกกรณี (วันนี้ไทย 2026-10-05)", ny == bk and bk["t"] == "2026-10-05", json.dumps([ny, bk]))
        exp = [0, 1, 2, 5, 6, 1, None, None]
        check(f"{tag} 4 ค่าถูก: 5 ต.ค.→0 · ศ. 2 ต.ค.→1 (ข้ามเสาร์-อาทิตย์) · พฤ. 1 ต.ค.→2 · จ. 28 ก.ย.→5 · ส. 26 ก.ย.→6 · อา. 4 ต.ค.→1 · ผิดรูป→null", bk["r"] == exp, json.dumps(bk["r"]))
        ut = run("UTC", "2026-10-04T22:00:00Z", D); tk = run("Pacific/Kiritimati", "2026-10-04T22:00:00Z", D)
        check(f"{tag} 4 UTC / Kiritimati (UTC+14) ที่เวลาเดียวกัน → ผลเท่ากัน", ut == bk and tk == bk, json.dumps([ut["r"], tk["r"]]))
        mid = run("America/New_York", "2026-10-02T09:00:00Z", D)   # ศุกร์ 16:00 ไทย = ศุกร์ 05:00 นิวยอร์ก
        mid2 = run("Asia/Bangkok", "2026-10-02T09:00:00Z", D)
        check(f"{tag} 4 กลางสัปดาห์ (ศุกร์ 16:00 ไทย) NY = Bangkok · ศ. 2 ต.ค. → 0", mid == mid2 and mid2["r"][1] == 0, json.dumps([mid, mid2]))
        sat = run("America/New_York", "2026-10-03T22:00:00Z", D); sat2 = run("Asia/Bangkok", "2026-10-03T22:00:00Z", D)   # อาทิตย์ 05:00 ไทย
        check(f"{tag} 4 อาทิตย์ 05:00 ไทย: NY = Bangkok · ศ. 2 ต.ค. → 0 (เสาร์-อาทิตย์ไม่นับ)", sat == sat2 and sat2["r"][1] == 0, json.dumps([sat, sat2]))
    finally:
        browser.close()


def static_tests():
    root = os.path.join(HERE, "..")
    check("[static] สำรอง index.backup-pre-NUM2.html + tests/_bk_num2/ อยู่", os.path.exists(os.path.join(root, "index.backup-pre-NUM2.html")) and os.path.isdir(os.path.join(HERE, "_bk_num2")))
    html = open(INDEX_HTML, encoding="utf-8").read()
    biz = html.split("function ffBizDaysSince(iso){")[1].split("\nasync function ffLoadJson")[0]
    check("[static] ffBizDaysSince ใช้ thaiToday() · ไม่มี new Date() เวลาเครื่อง / setHours / getDay", "thaiToday()" in biz and "new Date()" not in biz and "setHours" not in biz and "getDay()" not in biz, biz[:200])
    check("[static] luckyWins/goodLosses ใช้ pnlOutcome (ไม่เหลือ realizedPnlOf>0 / <=0 ในสองตัวนี้)", "list.filter(t=>realizedPnlOf(t)>0  && t.discScore" not in html and "realizedPnlOf(t)<=0 && t.discScore" not in html)


def main():
    static_tests()
    with sync_playwright() as pw:
        ff_tests(pw)
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            lucky_tests(pw, w, h, label)
            px_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 46 / NUM2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
