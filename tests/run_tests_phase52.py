#!/usr/bin/env python3
"""WL4 — ปุ่ม 📊 รายได้แยกส่วน · เลิกอ่าน research / meta/push · เทส 52
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 ไทย
ภาพ tests/screenshots/wl4-{card-revenue-btn,menu-no-push}-{1440,390}.png
รัน: python3 run_tests_phase52.py"""
import json, os, re
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase38 as P38
import run_tests_phase39 as P39
import run_tests_phase44 as P44
import run_tests_phase50 as P50

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
results = []
js = P39.js
CLK = "2026-10-05T03:00:00Z"
INDEX_SRC = os.path.abspath(os.path.join(HERE, "..", "index.html"))


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:600] + "...") if (detail and len(detail) > 600) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    page.wait_for_timeout(400)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def research_doc(sym, score):
    return {"ticker": sym, "name": sym + " Research Name", "mode_a": {"score": score, "max": 15, "rank": 1, "one_liner": "ทดสอบ"}, "summary": "สรุปจาก research"}


def launcher(pw, w, h, wl=(("AVGO", "2026-09-20"), ("PTT.BK", "2026-09-20")), ideas=(), research=True):
    doc = P38.doc38(clean=True, log={})

    def ex(pg):
        for sym, thd in wl:
            d = P50.wl_doc(sym, thd)
            if sym.endswith(".BK"): d["market"] = "TH"
            pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "watchlist", sym], d])
        for it in ideas: P44.seed_idea(pg, it)
        if research:   # seed ไว้ — ต้องไม่ถูกอ่าน/ไม่มีผล
            for sym, sc in (("AVGO", 5), ("PTT.BK", 15), ("AAA", 14), ("ZZZ", 3)):
                pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["research", sym], research_doc(sym, sc)])
            pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["meta", "push"], {"last_push_at": "2026-10-05T01:00:00Z"}])
    r = P39.launch(pw, w, h, doc=doc, cards={}, iso=CLK, clean=True, extra=ex)
    r[2].wait_for_timeout(400)
    return r


def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    cands = [P50.cand("NVDA", 1), P50.cand("PTT.BK", 2, market="TH")]
    idea = P50.idea("i-sem", "ไอเดียทดสอบ", status="need_evidence", cands=cands, scope=("US", "TH"))
    browser, context, page, ce, pe, dialogs = launcher(pw, w, h, ideas=[idea])
    try:
        # ── 1 ปุ่ม 📊
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(500)
        def btn(sym):
            js(page, "(s)=>wlOpen(s)", sym); page.wait_for_timeout(350)
            b = page.locator("#watchGroups [data-rev-btn]")
            return {"n": b.count(), "href": b.first.get_attribute("href") if b.count() else None, "target": b.first.get_attribute("target") if b.count() else None,
                    "rel": b.first.get_attribute("rel") if b.count() else None, "title": b.first.get_attribute("title") if b.count() else None,
                    "text": b.first.text_content().strip() if b.count() else None, "cls": b.first.get_attribute("class") if b.count() else None}
        a = btn("AVGO")
        check(f"{tag} 1 AVGO (US) → href /symbols/AVGO/financials-revenue/ · _blank · rel noopener · ปุ่มรอง (ไม่ primary)", a["n"] == 1 and a["href"] == "https://www.tradingview.com/symbols/AVGO/financials-revenue/" and a["target"] == "_blank" and "noopener" in (a["rel"] or "") and "primary" not in (a["cls"] or ""), json.dumps(a, ensure_ascii=False))
        check(f"{tag} 1 ข้อความปุ่ม '📊 รายได้แยกส่วน' · title ตาม brief", a["text"] == "📊 รายได้แยกส่วน" and a["title"] == "ดูรายได้แยกส่วนบน TradingView — ใช้ดูคร่าว ๆ · ตัวเลขที่ใช้เป็นหลักฐานต้องมาจากเอกสารบริษัท", json.dumps(a, ensure_ascii=False))
        shot(page, f"wl4-card-revenue-btn-{label.replace('px','')}.png", "#watchGroups .wlDHead")
        p = btn("PTT.BK")
        check(f"{tag} 1 PTT.BK (TH) → href /symbols/SET-PTT/financials-revenue/ (ตัด .BK)", p["href"] == "https://www.tradingview.com/symbols/SET-PTT/financials-revenue/", json.dumps(p))
        u = js(page, "()=>[wlRevUrl('avgo'), wlRevUrl('BRK.B'), wlRevUrl('ptt.bk'), wlRevUrl('KBANK.BK','TH'), wlRevUrl('X Y','US')]")
        check(f"{tag} 1 SYM ตัวใหญ่ · encodeURIComponent · ใช้ market ที่ส่งมา/เดาจาก .BK", u == ["https://www.tradingview.com/symbols/AVGO/financials-revenue/", "https://www.tradingview.com/symbols/BRK.B/financials-revenue/", "https://www.tradingview.com/symbols/SET-PTT/financials-revenue/", "https://www.tradingview.com/symbols/SET-KBANK/financials-revenue/", "https://www.tradingview.com/symbols/X%20Y/financials-revenue/"], json.dumps(u))
        if w < 600:
            check(f"{tag} 1 390px การ์ดหุ้นไม่ล้นแนวนอน", overflow(page) <= 0, str(overflow(page)))
        # Candidates
        js(page, "()=>{ wlSetView('cand'); }"); page.wait_for_timeout(450)
        js(page, "()=>wlOpen('NVDA')"); page.wait_for_timeout(350)
        c = page.locator("#watchGroups [data-rev-btn]")
        check(f"{tag} 1 Candidates (NVDA US) มีปุ่ม 📊 → /symbols/NVDA/financials-revenue/", c.count() == 1 and c.first.get_attribute("href") == "https://www.tradingview.com/symbols/NVDA/financials-revenue/" and c.first.get_attribute("target") == "_blank", c.first.get_attribute("href") if c.count() else "none")
        js(page, "()=>wlOpen('PTT.BK')"); page.wait_for_timeout(350)
        c = page.locator("#watchGroups [data-rev-btn]")
        check(f"{tag} 1 Candidates (PTT.BK TH) → SET-PTT", c.count() == 1 and c.first.get_attribute("href") == "https://www.tradingview.com/symbols/SET-PTT/financials-revenue/", c.first.get_attribute("href") if c.count() else "none")
        if w < 600: check(f"{tag} 1 390px การ์ด Candidates ไม่ล้นแนวนอน", overflow(page) <= 0, str(overflow(page)))
        # ── 2 ไม่อ่าน research / meta/push
        js(page, "()=>{ window.__fsAccess = []; }")
        for t in ("watch", "flow", "today", "watch"):
            js(page, "(t)=>{ switchTab(t); }", t); page.wait_for_timeout(500)
        js(page, "()=>rsLoad(true)"); page.wait_for_timeout(400)
        acc = js(page, "()=>window.__fsAccess || []")
        bad = [x for x in acc if x == "research" or x.startswith("research/") or x == "meta/push" or x == "meta" or x.startswith("meta/")]
        check(f"{tag} 2 เปิด Watch / Flow / Today + rsLoad(true): ไม่มีการเรียก research / meta/push (mock นับ path)", not bad, json.dumps(bad))
        js(page, "()=>{ wlSetView('wl'); }"); page.wait_for_timeout(300)
        html = js(page, "()=>document.body.innerHTML")
        check(f"{tag} 2 ไม่มีชิป Screen (Screen x/15 · Screen —)", not re.search(r"Screen\s*(—|\d)", js(page, "()=>document.querySelector('#watchGroups').innerText")))
        js(page, "()=>{ wlSetView('cand'); }"); page.wait_for_timeout(300)
        js(page, "()=>wlOpen('NVDA')"); page.wait_for_timeout(300)
        check(f"{tag} 2 Candidates ไม่มีชิป Screen — ด้วย", "Screen" not in js(page, "()=>document.querySelector('#watchGroups').innerText"))
        check(f"{tag} 2 ไม่มี #pushBadge / #pushWhen ใน DOM", js(page, "()=>!document.getElementById('pushBadge') && !document.getElementById('pushWhen')"))
        js(page, "()=>{ switchTab('watch'); wlSetView('wl'); }"); page.wait_for_timeout(300)
        txt = js(page, "()=>document.querySelector('#watchGroups').innerText")
        check(f"{tag} 2 ไม่มีข้อความ 'โหลดรีเสิร์ช' / 'กำลังโหลดรีเสิร์ช' / 'ข้อมูลตัวอย่าง'", not re.search(r"โหลดรีเสิร์ช|ข้อมูลตัวอย่าง", txt), txt[:200])
        js(page, "()=>toggleMoreMenu()"); page.wait_for_timeout(300)
        mm = js(page, "()=>document.getElementById('moreMenu').innerText")
        check(f"{tag} 2 เมนู ⋯ ไม่มี 'push ล่าสุด'", "push ล่าสุด" not in mm and js(page, "()=>document.getElementById('moreMenu').classList.contains('show')"), mm[:200])
        shot(page, f"wl4-menu-no-push-{label.replace('px','')}.png")
        js(page, "()=>toggleMoreMenu()")
        check(f"{tag} 2 chip ซิงก์ที่หัว ยังแสดงสถานะ (ไม่ว่าง) และไม่พูดถึง push", js(page, "()=>{ const t=document.getElementById('brandSyncTime'); return !!t && t.textContent.trim().length>0; }") and "push" not in js(page, "()=>document.getElementById('brandSync').title"))
        # ── 3 ลำดับ: ความด่วนเท่ากัน → ตามชื่อ (ไม่สนคะแนน research)
        order = js(page, "()=>wlRowsView().rows.map(r=>r.sym)")
        check(f"{tag} 3 Watchlist ความด่วนเท่ากัน → เรียงตามชื่อ (AVGO ก่อน PTT.BK แม้ research ให้ PTT.BK 15 · AVGO 5)", order == ["AVGO", "PTT.BK"], json.dumps(order))
        d_null = js(page, "()=>wlRowsAll().wl.every(r=>r.d===null) && wlRowsAll().cand.every(r=>r.d===null)")
        check(f"{tag} 3 ทุกแถว r.d = null (ไม่ join research)", d_null)
        # ชื่อบริษัท fallback: ไม่ error เมื่อ r.d null
        js(page, "()=>{ wlOpen('AVGO'); }"); page.wait_for_timeout(300)
        check(f"{tag} 3 เปิดรายละเอียด/ Overview ได้เมื่อ r.d = null ไม่ error", js(page, "()=>document.querySelector('#watchGroups .wlDHead')!==null"))
        # ── 4 console
        check(f"{tag} 4 ไม่มี console error ทุกแท็บ", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally:
        browser.close()


def static_tests():
    src = open(INDEX_SRC, encoding="utf-8").read()
    check("[static] 5 ไม่มี collection('research') ใน index.html", "collection('research')" not in src and 'collection("research")' not in src)
    check("[static] 5 ไม่มี doc('push') ใน index.html", "doc('push')" not in src and 'doc("push")' not in src)
    check("[static] 5 ไม่มี RS_DEMO / RS_DEMO_ON / pushBadge / wlScoreChips", not any(k in src for k in ("RS_DEMO", "pushBadge", "wlScoreChips", "rsUpdatePushBadge")))


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    static_tests()
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 52 / WL4) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
