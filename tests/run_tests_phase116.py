#!/usr/bin/env python3
"""PL1 Step 4 — A2 Screening modal (Trend 40 EMA must-pass · lens/Exception) + A5 Ready rule (Watchlist + ① Why buy + ④ Wrong if) · เทส 116
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase116.py"""
import json
from playwright.sync_api import sync_playwright
import ln3fix_common as C   # ต้องมาก่อน
import run_tests_phase4 as base
import run_tests_phase44 as P44
import run_tests_phase107 as T
import run_tests_phase111 as P111

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
settle = T.settle


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def seed_cand(page, sym, track=None, **extra):
    rec = {"manual": True, "sym": sym, "market": "US", "cand_at": "2026-10-20T03:00:00.000Z", "reasons": ["strong-rs", "volume-spike"], "note": "from ideas", "link": "https://example.com/" + sym.lower()}
    if track: rec["track"] = track
    rec.update(extra)
    js(page, "([k,r])=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, {[k]: r}); })", [sym, rec]); settle(page, 250)


def sheet(page):
    return js(page, """()=>{ const q = s=>document.querySelector(s);
      return {open: !!q('[data-scr-sheet]'), trendLbl: [...document.querySelectorAll('.scrSh .csR label')].map(l=>l.innerText).find(t=>/40 EMA/.test(t)) || '', exrow: !!q('[data-scr-exrow]'), errs: [...document.querySelectorAll('[data-scr-err]')].map(e=>e.innerText), msg: (q('[data-scr-msg]')||{}).innerText||'',
        trk: (q('[data-scr-track-btn][aria-pressed=true]')||{dataset:{}}).dataset.scrTrackBtn||'', opts: [...document.querySelectorAll('[data-scr-in=trend] option')].map(o=>o.textContent)}; }""")


def fill(page, **kw):
    for k, v in kw.items():
        if k in ("fortress", "proven", "emerging", "trend"): page.select_option(f'[data-scr-in="{k}"]', v)
        elif k == "why": page.fill("[data-scr-why]", v)
        elif k == "concerns": page.fill("[data-scr-concerns]", v)
        elif k == "exception": page.fill("[data-scr-exception]", v)
        elif k == "track": page.locator(f'[data-scr-track-btn="{v}"]').click()
        settle(page, 120)


def wl(page, t): return js(page, "(t)=>{ const w = wlItems.find(x=>x.ticker===t); return w ? JSON.parse(JSON.stringify(w)) : null; }", t)


def screening_tests(pw, w, h):
    tag = f"[{ENGINE}/screen/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_today(page)
        seed_cand(page, "MOM", "winner"); seed_cand(page, "CMP", "ladder"); seed_cand(page, "LEG")
        js(page, "()=>scrOpen('MOM')"); settle(page, 300)
        s0 = sheet(page)
        check(f"{tag} A2: เปิด modal → Trend label ตาม Track (Momentum = Weekly 40 EMA) · ตัวเลือก Not Evaluated · Pass · Fail · Insufficient Data · N/A", s0["open"] and "Weekly 40 EMA" in s0["trendLbl"] and s0["opts"] == ["Not Evaluated", "Pass", "Fail", "Insufficient Data", "N/A"], s0)
        page.locator("[data-scr-x]").click(); settle(page, 150)
        js(page, "()=>scrOpen('CMP')"); settle(page, 300)
        check(f"{tag} A2: Compounder → 'Monthly 40 EMA'", "Monthly 40 EMA" in sheet(page)["trendLbl"], sheet(page))
        page.locator("[data-scr-x]").click(); settle(page, 150)
        # Trend Fail → ไม่เข้า
        js(page, "()=>scrOpen('MOM')"); settle(page, 300)
        fill(page, fortress="passed", trend="failed", why="strong business")
        page.locator("[data-scr-save]").click(); settle(page, 300)
        s1 = sheet(page)
        check(f"{tag} A2: Trend = Fail (แม้ lens ผ่าน + Why) → ไม่บันทึก · error 'must be Pass' · ยังเป็น Candidate", s1["open"] and any("must be Pass" in x for x in s1["errs"]) and wl(page, "MOM") is None, [s1, wl(page, "MOM")])
        for v in ("untested", "insufficient", "na"):
            fill(page, trend=v); page.locator("[data-scr-save]").click(); settle(page, 200)
            check(f"{tag} A2: Trend = {v} ไม่นับว่าผ่าน (เฉพาะ Pass เท่านั้น)", wl(page, "MOM") is None and sheet(page)["open"], v)
        # Trend pass + ไม่มี lens + ไม่มี exception
        fill(page, fortress="untested", trend="passed")
        s2 = sheet(page)
        check(f"{tag} A2: ไม่มี lens Pass → ช่อง Exception Reason โผล่ (ซ่อนเมื่อมี lens Pass)", s2["exrow"] is True, s2)
        page.locator("[data-scr-save]").click(); settle(page, 250)
        check(f"{tag} A2: Trend Pass + Why แต่ไม่มี lens และไม่มี Exception → ไม่บันทึก + error", wl(page, "MOM") is None and any("Exception Reason" in x for x in sheet(page)["errs"]), sheet(page))
        fill(page, exception="Turnaround; lens data thin")
        page.locator("[data-scr-save]").click(); settle(page, 600)
        m = wl(page, "MOM") or {}
        ob = m.get("onboarding") or {}
        check(f"{tag} A2: exception path → บันทึกเข้า Watchlist · onboarding มีเวลา (at) · trend40=passed (weekly) · exception เก็บ · ไม่มี lens Pass", m and ob.get("at") and ob.get("trend40") == "passed" and ob.get("trend_basis") == "weekly" and ob.get("exception") == "Turnaround; lens data thin" and ob.get("fortress") == "untested" and ob.get("why_watch") == "strong business", ob)
        check(f"{tag} A2: carry Track/Reasons/Note/Link/วันที่เพิ่ม จาก candMeta · promoted_by ว่าง (ไม่มี RS)", m.get("ladder_watch") is False and m.get("reasons") == ["strong-rs", "volume-spike"] and m.get("note") == "from ideas" and m.get("link") == "https://example.com/mom" and m.get("cand_added_at") == "2026-10-20T03:00:00.000Z" and not m.get("promoted_by"), m)
        check(f"{tag} บันทึกสำเร็จ → modal ปิด · MOM ไม่อยู่ใน Candidates แล้ว", not sheet(page)["open"] and js(page, "()=>td4IsCand('MOM')") is False, "")
        # Compounder: Proven ตัวเดียวพอ
        js(page, "()=>scrOpen('CMP')"); settle(page, 300)
        fill(page, proven="passed", trend="passed", why="compounder growth")
        page.locator("[data-scr-save]").click(); settle(page, 600)
        c = wl(page, "CMP") or {}
        check(f"{tag} A2: Compounder + Proven Growth ตัวเดียว + Trend Pass + Why → เข้าได้ (ไม่ต้อง Fortress) · ladder_watch · trend_basis monthly · ไม่มี exception", c.get("ladder_watch") is True and c.get("onboarding", {}).get("trend_basis") == "monthly" and c["onboarding"].get("proven") == "passed" and c["onboarding"].get("exception") == "", c.get("onboarding"))
        # Legacy candidate ไม่มี Track
        js(page, "()=>scrOpen('LEG')"); settle(page, 300)
        fill(page, proven="passed", trend="passed", why="legacy one")
        page.locator("[data-scr-save]").click(); settle(page, 250)
        s3 = sheet(page)
        check(f"{tag} A2: Candidate เก่าไม่มี Track → ถามใน modal (ไม่มีค่าเริ่ม) · 'Pick a track' inline · ไม่บันทึก", s3["trk"] == "" and "Pick a track" in s3["errs"] and wl(page, "LEG") is None, s3)
        fill(page, track="ladder")
        page.locator("[data-scr-save]").click(); settle(page, 600)
        check(f"{tag} A2: เลือก Track แล้วบันทึกได้ → LEG อยู่ Watchlist เป็น Compounder", (wl(page, "LEG") or {}).get("ladder_watch") is True, wl(page, "LEG"))
        # ไม่มีเงื่อนไข Fortress สำหรับ Compounder แล้ว
        ok = js(page, "()=>{ const t = 'MOM'; const r = wlTrackBlock(t, 'ladder'); return r; }")
        check(f"{tag} A2: ย้าย Track เป็น Compounder ไม่ต้อง Fortress ผ่านแล้ว (wlTrackBlock = ไม่บล็อก)", not ok, ok)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def failure_tests(pw, w, h):
    tag = f"[{ENGINE}/scrfail/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_today(page)
        seed_cand(page, "FAILA", "winner")
        js(page, "()=>scrOpen('FAILA')"); settle(page, 300)
        fill(page, proven="passed", trend="passed", why="keep me")
        js(page, "()=>{ window.__wlc = window.wlCol; window.wlCol = ()=>({doc:()=>({set:()=>Promise.reject({code:'permission-denied'}), update:()=>Promise.reject({code:'permission-denied'})})}); }")
        page.locator("[data-scr-save]").click(); settle(page, 400)
        s = sheet(page)
        check(f"{tag} เขียนไม่สำเร็จ → ไม่ขึ้นสำเร็จ · modal ค้างพร้อมข้อความ · ค่าที่กรอกยังอยู่ · ไม่เข้า Watchlist", s["open"] and "Could not save" in s["msg"] and js(page, "()=>scr.why") == "keep me" and js(page, "()=>scr.proven") == "passed", s)
        js(page, "()=>{ window.wlCol = window.__wlc; }")
        check(f"{tag} ยัง Candidate อยู่ (ไม่มีเอกสาร Watchlist)", wl(page, "FAILA") is None and js(page, "()=>td4IsCand('FAILA')") is True, "")
        page.locator("[data-scr-save]").click(); settle(page, 600)
        check(f"{tag} ลองใหม่ (เขียนได้) → เข้า Watchlist", wl(page, "FAILA") is not None, "")
        # draft รอด refresh
        seed_cand(page, "FAILB", "ladder")
        js(page, "()=>scrOpen('FAILB')"); settle(page, 300)
        fill(page, emerging="passed", trend="passed", why="draft text")
        P44.reload_keep(page); T.go_today(page); settle(page, 300)
        js(page, "()=>scrOpen('FAILB')"); settle(page, 300)
        check(f"{tag} รีเฟรชแล้วเปิด modal ใหม่ → ค่าที่กรอกไว้กลับมา (Emerging Pass · Trend Pass · Why)", js(page, "()=>[scr.emerging, scr.trend, scr.why]") == ["passed", "passed", "draft text"], js(page, "()=>[scr.emerging, scr.trend, scr.why]"))
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def ready_tests(pw, w, h):
    tag = f"[{ENGINE}/ready/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        js(page, "()=>{ window.__READY_REAL = true; }")
        real = js(page, "()=>[window.__READY_REAL === true, wlReady('NOT_ON_WATCHLIST')]")
        check(f"{tag} ยืนยัน: phase116 ใช้ wlReady ตัวจริง (ปิด stub ใน tests/ff_stub.py) — ticker ที่ไม่อยู่ใน Watchlist ได้ false", real == [True, False], real)
        col = lambda t, **kw: js(page, "([t,kw])=>wlCol().doc(t).set(Object.assign({ticker:t, market:'US', port:'core', note:'', added_at:'2026-10-01T00:00:00Z'}, kw))", [t, kw])
        col("RDY0"); col("RDY1", my_thesis={"why": "improving margins", "exit": ""}); col("RDY2", my_thesis={"why": "improving margins", "exit": "loses 200d MA"})
        col("RDY3", thesis={"sections": {"s2": {"md": "AI why"}, "s4": {"md": "AI exit"}}}); col("RDY4", archived=True, my_thesis={"why": "a", "exit": "b"}); settle(page, 500)
        def attempt(sym):
            P111.open_form(page, sym); P111.setpx(page, 100, 90)
            return P111.form(page)
        f0 = attempt("RDY0")
        check(f"{tag} A5: ใน Watchlist แต่ไม่มี ① และ ④ → บล็อก 'Not ready — fill ① Why buy and ④ Wrong if' · บันทึกไม่ได้", f0["save"] is True and "Not ready" in f0["err"] and "① Why buy" in f0["err"] and "④ Wrong if" in f0["err"], f0)
        n0 = len(P111.cards(page)); js(page, "()=>coreNewSave()"); settle(page, 400)
        check(f"{tag} A5: เรียก coreNewSave ตรง ๆ ก็ไม่สร้างการ์ด (กันทางลัด)", len(P111.cards(page)) == n0, "")
        f1 = attempt("RDY1")
        check(f"{tag} A5: มีแค่ ① → ยังบล็อก (ขาด ④)", f1["save"] is True and "④ Wrong if" in f1["err"] and "① Why buy" not in f1["err"], f1)
        f2 = attempt("RDY2")
        check(f"{tag} A5: มี ① และ ④ → ผ่าน (ไม่มี error Ready) · ไม้แรก 127 หุ้น · บันทึกได้", f2["save"] is False and "Not ready" not in f2["err"] and f2["qty"].replace(",", "") == "127", f2)
        js(page, "()=>coreNewSave()"); settle(page, 800)
        check(f"{tag} A5: บันทึกแผนสำเร็จเมื่อ Ready", "RDY2" in js(page, "()=>coreCardsList.map(c=>c.ticker)"), "")
        f3 = attempt("RDY3")
        check(f"{tag} A5: Thesis นำเข้าจาก AI (s2/s4) ไม่นับเป็น Ready → ยังบล็อก", f3["save"] is True and "Not ready" in f3["err"], f3)
        f4 = attempt("RDY4")
        check(f"{tag} A5: archived (แม้ ①④ ครบ) → บล็อก 'archived'", f4["save"] is True and "archived" in f4["err"], f4)
        f5 = attempt("NOTWL")
        check(f"{tag} A5: ไม่อยู่ใน Watchlist → บล็อก 'not on the Watchlist'", f5["save"] is True and "not on the Watchlist" in f5["err"], f5)
        # RS stars ไม่ผูกกับ Ready
        js(page, "()=>wlStarSet('RDY0','3')"); settle(page, 300)
        f6 = attempt("RDY0")
        check(f"{tag} A5: RS ★★★ ไม่ทำให้ Ready (ต้อง ①④ เท่านั้น)", f6["save"] is True and "Not ready" in f6["err"], f6)
        # editor บน Watchlist card
        js(page, "()=>{ coreSheetClose(); switchTab('watch'); wlSetView('wl'); renderWatchlist(); wlOpen('RDY1'); }"); settle(page, 600)
        js(page, "()=>wlMtEditOpen('RDY1')"); settle(page, 300)   # TX1 — การ์ดที่มีข้อความเซฟแล้วเปิดเป็น Read · กด Edit ก่อนถึงมีช่อง
        st = js(page, "()=>document.querySelectorAll('.wlMtH [data-wl-status]').length+'|'+document.querySelectorAll('[data-wl-ready]').length+'|'+wlReady('RDY1')")
        check(f"{tag} A5: การ์ด Watchlist มีช่อง My Thesis ① Why buy / ④ Wrong if · มีแท็กสถานะเดียว (ไม่มีป้าย Ready ซ้ำ) · wlReady = false เมื่อยังไม่ครบ", st == "1|0|false" and cnt(page, "[data-wl-mt-why]") == 1 and cnt(page, "[data-wl-mt-exit]") == 1, st)
        page.fill("[data-wl-mt-exit]", "guidance cut"); page.locator("[data-wl-mt-save]").click(); settle(page, 600)
        st2 = js(page, "()=>document.querySelectorAll('.wlMtH [data-wl-status]').length+'|'+document.querySelectorAll('[data-wl-ready]').length")
        check(f"{tag} A5: กรอก ④ แล้ว Save → my_thesis เก็บถาวร · แท็กสถานะเดียว · wlReady = true", st2 == "1|0" and js(page, "()=>wlReady('RDY1')") is True and (wl(page, "RDY1")["my_thesis"]["exit"] == "guidance cut"), [st2, wl(page, "RDY1")["my_thesis"]])
        ob = js(page, "()=>(document.querySelector('[data-wl-onb]')||{}).innerText||''")
        check(f"{tag} การ์ด Watchlist เก่า (ไม่มี onboarding) แสดง 'Onboarding Data … Unspecified'", "Onboarding Data" in ob and "Unspecified" in ob, ob)
        # การ์ด/ไม้ที่เปิดอยู่ไม่โดน
        js(page, "()=>{ coreNewOpen('main',{id:coreCardsList.find(c=>c.ticker==='RDY2').id, mode:'edit'}); }"); settle(page, 400)
        e_ = js(page, "()=>(document.getElementById('cnErr')||{}).innerText||''")
        check(f"{tag} A5: แก้การ์ดที่มีอยู่ไม่ติดกฎ Ready (mode edit)", "Not ready" not in e_, e_)
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


cnt = T.cnt


def main():
    with sync_playwright() as pw:
        for w, h in ((390, 844), (1440, 900)):
            screening_tests(pw, w, h)
        failure_tests(pw, 390, 844)
        for w, h in ((390, 844), (1440, 900)):
            ready_tests(pw, w, h)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
