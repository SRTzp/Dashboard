#!/usr/bin/env python3
"""PL1 Step 5 — A6 Watchlist management: status tag · Next check · filters (Track/Reason/RS) · sort · Last-updated lines · Archive/Restore · Delete visibility · เทส 117
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase117.py"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase107 as T
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle, cnt = T.settle, T.cnt


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def put(page, t, **kw):
    doc = {"ticker": t, "market": "US", "port": "core", "note": "", "added_at": "2026-10-01T00:00:00Z"}
    doc.update(kw)
    js(page, "([t,d])=>wlCol().doc(t).set(d)", [t, doc])


def rows(page): return js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)")
def goto(page, view="wl"):
    js(page, "(v)=>{ coreSheetClose(); switchTab('watch'); wlSetView(v); renderWatchlist(); }", view); settle(page, 500)


def seed(page):
    MT = lambda w, x, u: {"why": w, "exit": x, "updated_at": u}
    put(page, "AAA", ladder_watch=False, reasons=["strong-rs"], rs_stars=3, my_thesis=MT("w", "x", "2026-10-10T00:00:00Z"), next_check_date="2026-11-20", next_check_note="Q3 earnings")
    put(page, "BBB", ladder_watch=True, reasons=["volume-spike", "strong-rs"], rs_stars=1, my_thesis=MT("w", "", "2026-10-25T00:00:00Z"), next_check_date="2026-11-05")
    put(page, "CCC", ladder_watch=False, reasons=["earnings-spike"], rs_stars=None, thesis={"date": "2026-09-01", "mode": "full", "summary": {"status": "ok"}}, thesis_imported_at="2026-10-20T00:00:00Z")
    put(page, "DDD", ladder_watch=True, reasons=[], rs_stars=0, thesis={"date": "2026-08-15", "mode": "full", "summary": {"status": "ok"}}, my_thesis=MT("w", "x", "2026-09-01T00:00:00Z"))
    put(page, "EEE", ladder_watch=False, archived=True, archived_reason="thesis broke", archived_at="2026-10-30T00:00:00Z", my_thesis=MT("w", "x", "2026-10-01T00:00:00Z"))
    put(page, "FFF")   # typo-ticker: ว่างทั้งหมด
    settle(page, 600)


def mgmt_tests(pw, w, h):
    tag = f"[{ENGINE}/mgmt/{w}]"
    cards = {"ccAAA": {"acct": "main", "ticker": "DDD", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": 95, "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z", "tier": "A"}}
    b, page, ce, pe = P111.core(pw, w, h, cards=cards)
    try:
        js(page, "()=>{ window.__READY_REAL = true; }")
        seed(page); goto(page)
        st = js(page, "()=>Object.fromEntries(wlItems.map(i=>[i.ticker, wlStatusKey(i)]))")
        check(f"{tag} A6: status อัตโนมัติ — AAA Ready ไม่มีแผน = awaiting · BBB ขาด ④ = drafting · DDD มีแผน = plan · EEE archived", st["AAA"] == "awaiting" and st["BBB"] == "drafting" and st["CCC"] == "drafting" and st["DDD"] == "plan" and st["EEE"] == "archived", st)
        lbl = js(page, "()=>({dots: document.querySelectorAll('.wlR[data-sym] [data-wl-status]').length, tags: document.querySelectorAll('.wlR[data-sym] [data-ln4w-tag]').length, n: document.querySelectorAll('.wlR[data-sym]').length})")
        check(f"{tag} A6 (LN4 §7): lean row — one tag per row, no status dots (status stays in wlStatusKey / detail)", lbl["dots"] == 0 and lbl["tags"] == lbl["n"] > 0, lbl)
        check(f"{tag} A6: ค่าเริ่ม — EEE (archived) ถูกซ่อน · ปุ่ม 'Archived (1)' · เรียงตาม RS ★★★→★→Unrated→0 ท้ายสุด? (RS มากสุดก่อน)", "EEE" not in rows(page) and (js(page, "()=>document.querySelector('[data-wl-arch-toggle]').textContent.trim()")) == "Archived (1)" and rows(page)[0] == "AAA", rows(page))
        nc = js(page, "()=>{ const d = document.createElement('div'); d.innerHTML = wlNextHtml(wlItemOf('AAA')); return d.textContent + ' ' + ((d.firstChild||{}).title||''); }")
        check(f"{tag} A6 (LN4 §7): Next check moved off the lean row — still built for the detail (date + short text)", "11-20" in nc and "Q3 earnings" in nc and js(page, "()=>document.querySelectorAll('.wlR[data-sym=AAA] [data-wl-nc]').length") == 0, nc)
        # sort modes
        js(page, "()=>wlSetSortMode('next')"); settle(page, 300)
        check(f"{tag} A6: เรียง Next check (วันใกล้สุดก่อน · ไม่มีวัน = ท้าย): BBB(11-05) → AAA(11-20) → ที่เหลือ", rows(page)[:2] == ["BBB", "AAA"], rows(page))
        js(page, "()=>wlSetSortMode('upd')"); settle(page, 300)
        check(f"{tag} A6: เรียง Last updated (ใหม่สุดก่อน): BBB(10-25) → CCC(AI import 10-20) → AAA(10-10) → DDD(09-01)", rows(page)[:4] == ["BBB", "CCC", "AAA", "DDD"], rows(page))
        js(page, "()=>wlSetSortMode('rs')"); settle(page, 300)
        check(f"{tag} A6: เรียง RS (ค่าเริ่ม) — ★★★ AAA → ★ BBB → 0 DDD → Unrated CCC?", rows(page)[:3] == ["AAA", "BBB", "DDD"], rows(page))
        # filters
        js(page, "()=>wlSetTrack('ladder')"); settle(page, 300)
        check(f"{tag} A6: กรอง Track = Compounder → BBB, DDD", sorted(rows(page)) == ["BBB", "DDD"], rows(page))
        js(page, "()=>{ wlSetTrack('ladder'); wlToggleReason('strong-rs'); }"); settle(page, 300)
        check(f"{tag} A6: กรอง Reason = Strong RS → AAA, BBB", sorted(rows(page)) == ["AAA", "BBB"], rows(page))
        js(page, "()=>{ wlToggleRs('3'); }"); settle(page, 300)
        check(f"{tag} A6: + RS ★★★ → AAA เท่านั้น", rows(page) == ["AAA"], rows(page))
        js(page, "()=>{ wlRsF.clear(); wlReasonF.clear(); wlToggleRs('u'); }"); settle(page, 300)
        check(f"{tag} A6: กรอง RS = Unrated (ไม่ใช่ 0) → CCC, FFF", sorted(rows(page)) == ["CCC", "FFF"], rows(page))
        js(page, "()=>{ wlRsF.clear(); wlReasonF.clear(); wlTrackF = 'all'; renderWatchlist(); }"); settle(page, 300)
        fl = js(page, "()=>{ fltOpen = true; renderWatchlist(); return [!!document.querySelector('[data-wl-ftrack]'), !!document.querySelector('[data-wl-freason]'), !!document.querySelector('[data-wl-frs]'), !!document.querySelector('[data-wl-sort]')]; }")
        check(f"{tag} A6: แผง Filter ▾ มีกลุ่ม Track · Reason · RS · Sort", fl == [True, True, True, True], fl)
        js(page, "()=>{ fltOpen = false; renderWatchlist(); }")
        # card: dates + next check editor
        js(page, "()=>{ wlOpen('CCC'); wlSetSub('view'); }"); settle(page, 500)   # PL2·3: editor + dates now live in the My Thesis tab
        d1 = js(page, "()=>(document.querySelector('[data-wl-dates]')||{}).innerText||''")
        check(f"{tag} A6: การ์ดแสดง 'My Thesis' และ 'AI Thesis' แยกกัน — CCC: My —, AI imported 2026-10-20", "My Thesis: —" in d1 and "AI Thesis: imported 2026-10-20" in d1, d1)
        js(page, "()=>{ wlOpen('DDD'); wlSetSub('view'); }"); settle(page, 500)
        d2 = js(page, "()=>(document.querySelector('[data-wl-dates]')||{}).innerText||''")
        check(f"{tag} A6: ข้อมูลเก่า (ไม่มี thesis_imported_at) → 'data as of 2026-08-15' (ไม่เขียนว่า updated) · My Thesis updated 2026-09-01", "AI Thesis: data as of 2026-08-15" in d2 and "My Thesis: updated 2026-09-01" in d2, d2)
        js(page, "()=>wlOpen('FFF')"); settle(page, 400)
        page.fill("[data-wl-nc-date]", "2026-12-01"); page.fill("[data-wl-nc-note]", "check guidance"); page.locator("[data-wl-mt-save]").click(); settle(page, 600)
        f = js(page, "()=>{ const x = wlItems.find(i=>i.ticker==='FFF'); return [x.next_check_date, x.next_check_note]; }")
        check(f"{tag} A6: ตั้ง Next check (วัน + ข้อความ) → เก็บถาวร", f == ["2026-12-01", "check guidance"], f)
        # delete visibility
        def menu(sym):
            js(page, "(s)=>{ wlOpen(s); wlMenu = s; renderWatchlist(); }", sym); settle(page, 400)
            return js(page, "()=>[...document.querySelectorAll('[data-lt-menuwrap] [role=menuitem]')].map(e=>e.innerText.trim())")
        mF, mA = menu("FFF"), menu("AAA")
        check(f"{tag} A6: Archive เป็นรายการแรก · Delete แสดงเฉพาะหุ้นว่าง (FFF) — AAA มี My Thesis → ไม่มี Delete", mF[0].startswith("🗄 Archive") and any("ลบ" in x for x in mF) and mA[0].startswith("🗄 Archive") and not any("ลบ" in x for x in mA), [mF, mA])
        js(page, "()=>{ wlMenu = ''; renderWatchlist(); }")
        # archive flow
        js(page, "()=>wlArchiveOpen('AAA')"); settle(page, 300)
        page.locator("[data-wla-save]").click(); settle(page, 200)
        check(f"{tag} A6: Archive ต้องมีเหตุผล — ว่าง = error inline ไม่บันทึก", cnt(page, "[data-wla-err]") == 1 and not js(page, "()=>wlItemOf('AAA').archived"), "")
        page.fill("[data-wla-reason]", "waiting for pullback"); page.locator("[data-wla-save]").click(); settle(page, 600)
        a = js(page, "()=>{ const x = wlItemOf('AAA'); return [x.archived, x.archived_reason, !!x.archived_at, x.my_thesis.why, x.reasons, x.next_check_note]; }")
        check(f"{tag} A6: Archive → archived + reason + เวลา · thesis/reasons/next check ยังอยู่ครบ", a == [True, "waiting for pullback", True, "w", ["strong-rs"], "Q3 earnings"], a)
        check(f"{tag} A6: AAA หายจากลิสต์ปกติ · 'Archived (2)' · Ready ถูกบล็อก", "AAA" not in rows(page) and js(page, "()=>document.querySelector('[data-wl-arch-toggle]').textContent.trim()") == "Archived (2)" and js(page, "()=>wlReady('AAA')") is False, rows(page))
        hw = js(page, "()=>tdHomeworkCandidates().map(x=>x.t)")
        check(f"{tag} A6: หุ้น archived ไม่เข้าคิว Deep dive ของ Today", "AAA" not in hw and "EEE" not in hw and "BBB" in hw, hw)
        js(page, "()=>wlSetArch(true)"); settle(page, 400)
        check(f"{tag} A6: กด 'Archived' → เห็นเฉพาะ archived (AAA, EEE)", sorted(rows(page)) == ["AAA", "EEE"], rows(page))
        js(page, "()=>wlOpen('AAA')"); settle(page, 400)
        ai = js(page, "()=>(document.querySelector('[data-wl-arch-info]')||{}).innerText||''")
        check(f"{tag} A6: การ์ด archived แสดงเหตุผล + ปุ่ม Restore", "waiting for pullback" in ai and cnt(page, "[data-wl-restore]") == 1, ai)
        page.locator("[data-wl-restore]").click(); settle(page, 600)
        r_ = js(page, "()=>{ const x = wlItemOf('AAA'); return [x.archived, x.archived_reason, wlReady('AAA')]; }")
        check(f"{tag} A6: Restore → archived=false · เหตุผลล้าง · thesis คงเดิม → Ready อีกครั้ง", r_ == [False, "", True], r_)
        js(page, "()=>wlSetArch(false)"); settle(page, 300)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def archive_warn_tests(pw, w, h):
    tag = f"[{ENGINE}/archwarn/{w}]"
    cards = {"ccW": {"acct": "main", "ticker": "PLN", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": 95, "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z", "tier": "A"}}
    b, page, ce, pe = P111.core(pw, w, h, cards=cards)
    try:
        put(page, "PLN", my_thesis={"why": "w", "exit": "x", "updated_at": "2026-10-01T00:00:00Z"}); put(page, "NOPLAN", my_thesis={"why": "w", "exit": "x", "updated_at": "2026-10-01T00:00:00Z"}); settle(page, 500)
        js(page, "()=>wlArchiveOpen('PLN')"); settle(page, 300)
        page.fill("[data-wla-reason]", "rotating out"); page.locator("[data-wla-save]").click(); settle(page, 400)
        w1 = js(page, "()=>({warn:(document.querySelector('[data-wla-warn]')||{}).innerText||'', btn:document.querySelector('[data-wla-save]').innerText, archived:wlItemOf('PLN').archived, card:coreCardsList.find(c=>c.ticker==='PLN').status})")
        check(f"{tag} A6: หุ้นมีแผนค้าง → ครั้งแรกขึ้นเตือน 'Has an open position/plan — archive anyway?' · ปุ่มเป็น 'Archive anyway' · ยังไม่ archive", "Has an open position/plan" in w1["warn"] and w1["btn"] == "Archive anyway" and w1["archived"] is False, w1)
        page.locator("[data-wla-save]").click(); settle(page, 600)
        w2 = js(page, "()=>({archived:wlItemOf('PLN').archived, reason:wlItemOf('PLN').archived_reason, card:coreCardsList.find(c=>c.ticker==='PLN').status, plan:coreCardsList.find(c=>c.ticker==='PLN').plan})")
        check(f"{tag} A6: แตะอีกครั้ง → archive สำเร็จ · แผน (PLN) ไม่ถูกแตะ (status plan · entry/stop เดิม)", w2["archived"] is True and w2["reason"] == "rotating out" and w2["card"] == "plan" and w2["plan"] == {"entry": 100, "stop": 90}, w2)
        js(page, "()=>wlArchiveOpen('NOPLAN')"); settle(page, 300)
        page.fill("[data-wla-reason]", "done"); page.locator("[data-wla-save]").click(); settle(page, 600)
        check(f"{tag} A6: หุ้นที่ไม่มีแผน/ไม้ → archive ครั้งเดียว ไม่มีคำเตือน", js(page, "()=>wlItemOf('NOPLAN').archived") is True, "")
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def cand_rows_tests(pw, w, h):
    tag = f"[{ENGINE}/candrows/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_today(page)
        rec = lambda sym, track, rs: {"manual": True, "sym": sym, "market": "US", "cand_at": "2026-10-20T03:00:00.000Z", "track": track, "reasons": rs}
        js(page, "(d)=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, d); })", {"CAA": rec("CAA", "winner", ["strong-rs", "volume-spike"]), "CBB": rec("CBB", "ladder", ["earnings-spike"]), "CCC": {"manual": True, "sym": "CCC", "market": "US", "cand_at": "2026-10-20T03:00:00.000Z"}}); settle(page, 400)
        goto(page, "cand")
        chips = js(page, "()=>Object.fromEntries([...document.querySelectorAll('.wlR[data-sym]')].map(r=>[r.dataset.sym, [...r.querySelectorAll('.wlTg'), ...r.querySelectorAll('[data-tv1-src]')].map(x=>x.innerText)]))")   # TV1: reason moved from chips to the 'reason · age' tag
        check(f"{tag} A6 (LN4 §7): Candidate row = ONE reason tag (CAA Strong RS +1 · CBB Earnings Spike) · old doc (CCC) amber 'set reason'", chips.get("CAA") == ["Strong RS +1"] and chips.get("CBB") == ["Earnings Spike"] and chips.get("CCC") == ["set reason"], chips)
        js(page, "()=>wlSetTrack('ladder')"); settle(page, 300)
        check(f"{tag} A6: กรอง Track ใน Candidates → Compounder = CBB", rows(page) == ["CBB"], rows(page))
        js(page, "()=>{ wlTrackF = 'all'; wlToggleReason('strong-rs'); }"); settle(page, 300)
        check(f"{tag} A6: กรอง Reason ใน Candidates = Strong RS → CAA", rows(page) == ["CAA"], rows(page))
        js(page, "()=>{ wlReasonF.clear(); renderWatchlist(); }")
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            mgmt_tests(pw, w, h); cand_rows_tests(pw, w, h); archive_warn_tests(pw, w, h)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
