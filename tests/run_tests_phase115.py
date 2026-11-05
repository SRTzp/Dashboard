#!/usr/bin/env python3
"""PL1 Step 3 — A1: Add popup (หลาย ticker ต่อแถว · Track/Reasons บังคับ) + Settings › Candidate reasons + hint แผนเก่า · เทส 115
Chromium · 390 / 1440 · ข้อมูล SAMPLE ล้วน · รัน: python3 run_tests_phase115.py"""
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
settle, cnt = T.settle, T.cnt


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def meta(page): return js(page, "()=>tdSettings().candMeta || {}")
def log(page): return js(page, "()=>td4AddLog()")
def box(page): return js(page, "()=>document.querySelector('[data-td4-add]') ? document.querySelector('[data-td4-add]').value : null")
def pop(page): return js(page, """()=>({open:!!document.querySelector('[data-cp-sheet]'), rows:[...document.querySelectorAll('[data-cp-row]')].map(r=>({k:r.dataset.cpRow, err:(r.querySelector('[data-cp-err]')||{}).innerText||'', track:(r.querySelector('[data-cp-track][aria-pressed=true]')||{dataset:{}}).dataset.cpTrack||'', reasons:[...r.querySelectorAll('[data-cp-reason][aria-pressed=true]')].map(x=>x.dataset.cpReason)})), msg:(document.querySelector('[data-cp-msg]')||{}).innerText||''})""")


def today_add(page, text):
    page.fill("[data-td4-add]", text); js(page, "()=>td4AddIn(document.querySelector('[data-td4-add]').value)"); page.locator("[data-td4-add-go]").click(); settle(page, 400)


def reasons_tests(pw, w, h):
    tag = f"[{ENGINE}/reasons/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        js(page, "()=>{ crsSetRender(); }")
        names = js(page, "()=>[...document.querySelectorAll('[data-crs-name]')].map(e=>e.value)")
        check(f"{tag} Settings › Candidate reasons: ค่าเริ่ม 6 ข้อ", names == ["Strong RS", "Volume Spike", "Earnings Spike", "Break 52W High", "Legendary Copy", "Investing Copy"], names)
        js(page, "()=>{ document.getElementById('crsNew').value = 'Insider Buying'; crsAdd(); }"); settle(page, 300)
        l = js(page, "()=>crsList().map(r=>[r.id,r.label,r.active])")
        check(f"{tag} เพิ่ม 'Insider Buying' → id สร้างอัตโนมัติ (insider-buying-xxxx) · active", len(l) == 7 and l[6][1] == "Insider Buying" and l[6][0].startswith("insider-buying-") and l[6][2] is True and l[0][0] == "strong-rs", l)
        js(page, "()=>{ document.getElementById('crsNew').value = 'insider buying'; crsAdd(); }"); settle(page, 200)
        check(f"{tag} ชื่อซ้ำ (ไม่สนตัวพิมพ์) → ไม่เพิ่ม + ข้อความ", len(js(page, "()=>crsList()")) == 7 and "already exists" in (js(page, "()=>document.querySelector('[data-crs-msg]').innerText")), "")
        js(page, "()=>crsRename('strong-rs', 'Strong Relative Strength')"); settle(page, 200)
        check(f"{tag} เปลี่ยนชื่อ → label ใหม่ แต่ id 'strong-rs' เดิม", js(page, "()=>[crsList()[0].id, crsList()[0].label, crsLabel('strong-rs')]") == ["strong-rs", "Strong Relative Strength", "Strong Relative Strength"], "")
        # ระเบียนเก่าอ้าง id → ปิดใช้งานแล้วยังแสดงชื่อ
        js(page, "()=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, {OLDC:{manual:true, sym:'OLDC', market:'US', cand_at:'2026-10-01T00:00:00Z', track:'winner', reasons:['volume-spike']}}); })"); settle(page, 200)
        js(page, "()=>crsToggle('volume-spike', false)"); settle(page, 200)
        chk = js(page, "()=>({active:crsActive().map(r=>r.id).includes('volume-spike'), label:crsLabel('volume-spike'), stillThere:tdSettings().candMeta.OLDC.reasons})")
        check(f"{tag} ปิดใช้งาน 'Volume Spike' → ไม่อยู่ในตัวเลือกใหม่ · ไม่ลบ · ระเบียนเก่ายังอ้าง id เดิมและแสดงชื่อได้", chk == {"active": False, "label": "Volume Spike", "stillThere": ["volume-spike"]}, chk)
        for r in js(page, "()=>crsActive().map(r=>r.id).slice(1)"): js(page, "(i)=>crsToggle(i,false)", r)
        check(f"{tag} ปิดข้อสุดท้ายไม่ได้ (ต้องเหลือ active อย่างน้อย 1)", len(js(page, "()=>crsActive()")) == 1, "")
        check(f"{tag} ไม่ล้นแนวนอน · ไม่มี console error", not C.overflow(page) and not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def popup_tests(pw, w, h, where):
    tag = f"[{ENGINE}/popup-{where}/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    dialogs = []
    try:
        page.on("dialog", lambda d: (dialogs.append(d.message), d.dismiss()))
        if where == "today": T.go_today(page)
        else:
            js(page, "()=>{ switchTab('watch'); wlSetView('cand'); wlAddCToggle(); }"); settle(page, 500)
        inp = "[data-td4-add]" if where == "today" else "[data-wl-addc-t]"
        go = "[data-td4-add-go]" if where == "today" else "[data-wl-addc-go]"
        page.fill(inp, "AAA BBB CCC"); js(page, "()=>td4AddIn(arguments[0])") if False else None
        js(page, "(v)=>td4AddIn(v)", "AAA BBB CCC")
        page.locator(go).first.click(); settle(page, 500)
        p0 = pop(page)
        check(f"{tag} A1: กด Add → popup แสดงทุก ticker เป็นแถว (AAA · BBB · CCC) · ยังไม่บันทึกอะไร", p0["open"] and [r["k"] for r in p0["rows"]] == ["AAA", "BBB", "CCC"] and meta(page).get("AAA") is None and log(page) == [], [p0, log(page)])
        # Cancel
        page.locator("[data-cp-cancel]").click(); settle(page, 300)
        check(f"{tag} Cancel = ไม่บันทึกอะไร · ticker ที่พิมพ์ยังอยู่ในกล่อง (AAA BBB CCC) · โควตาไม่ขยับ", not pop(page)["open"] and meta(page).get("AAA") is None and log(page) == [] and "AAA BBB CCC" in (js(page, "()=>td4Draft")), [js(page, "()=>td4Draft"), log(page)])
        # Save โดยไม่เลือก Track → inline error ไม่ใช่ alert
        page.locator(go).first.click(); settle(page, 400)
        page.locator("[data-cp-save]").click(); settle(page, 300)
        p1 = pop(page)
        check(f"{tag} บันทึกโดยไม่เลือก Track → ทุกแถวขึ้น 'Pick a track' แบบ inline · ไม่มี alert · ไม่บันทึก", all(r["err"] == "Pick a track" for r in p1["rows"]) and not dialogs and meta(page).get("AAA") is None, [p1, dialogs])
        # Apply to all: Track อย่างเดียว → ต้องมี Reason
        page.locator('[data-cp-all-track="winner"]').click(); settle(page, 200)
        p2 = pop(page)
        check(f"{tag} 'Apply to all' Momentum แตะครั้งเดียว → ทุกแถวมี Track · เหลือ error 'Pick at least one reason'", all(r["track"] == "winner" and r["err"] == "Pick at least one reason" for r in p2["rows"]), p2)
        page.locator('[data-cp-all-reason="strong-rs"]').click(); settle(page, 200)
        # override แถว BBB → Compounder + เพิ่ม reason
        page.locator('[data-cp-row="BBB"] [data-cp-track="ladder"]').click(); settle(page, 150)
        page.locator('[data-cp-row="BBB"] [data-cp-reason="earnings-spike"]').click(); settle(page, 150)
        page.locator('[data-cp-row="CCC"] [data-cp-note]').fill("watch breakout"); page.locator('[data-cp-row="CCC"] [data-cp-link]').fill("https://example.com/c"); settle(page, 150)
        p3 = pop(page)
        check(f"{tag} Apply to all ตั้งทุกแถว → แถวเดียว override ได้ (BBB = Compounder + 2 เหตุผล)", [r["track"] for r in p3["rows"]] == ["winner", "ladder", "winner"] and p3["rows"][1]["reasons"] == ["strong-rs", "earnings-spike"] and all(not r["err"] for r in p3["rows"]), p3)
        wd = js(page, "()=>{ const s = document.querySelector('.cpSh'); return s ? [s.scrollWidth - s.clientWidth, document.documentElement.scrollWidth - innerWidth] : null; }")
        check(f"{tag} popup ไม่ล้นแนวนอน", wd and wd[0] <= 1 and wd[1] <= 0, wd)
        page.locator('[data-cp-row="CCC"] [data-cp-rm]').click(); settle(page, 200)
        check(f"{tag} Remove-row: ลบ CCC ออกจากรายการ", [r["k"] for r in pop(page)["rows"]] == ["AAA", "BBB"], "")
        page.locator("[data-cp-save]").click(); settle(page, 600)
        m = meta(page)
        check(f"{tag} Save → candMeta มี track/reasons/cand_at (AAA winner [strong-rs] · BBB ladder [strong-rs, earnings-spike]) · โควตา 2 · popup ปิด", not pop(page)["open"] and m["AAA"]["track"] == "winner" and m["AAA"]["reasons"] == ["strong-rs"] and m["BBB"]["track"] == "ladder" and m["BBB"]["reasons"] == ["strong-rs", "earnings-spike"] and m["AAA"]["manual"] is True and log(page) == ["AAA", "BBB"], [m.get("AAA"), m.get("BBB"), log(page)])
        check(f"{tag} กล่อง ticker ว่าง (CCC ถูก Remove จาก popup = ออกจากรายการ) · ไม่มี console error", js(page, "()=>td4Draft").strip() == "" and not ce and not pe, [js(page, "()=>td4Draft"), ce[:2], pe[:2]])
    finally: b.close()


def partial_quota_failure_tests(pw, w, h):
    tag = f"[{ENGINE}/partial/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_today(page)
        # แถวผิดรูปแบบ/ซ้ำ + ถูกต้อง → บันทึกเฉพาะแถวถูก
        js(page, "()=>glWrite(S=>{ S.candMeta = Object.assign({}, S.candMeta||{}, {DUPE:{manual:true, sym:'DUPE', market:'US', cand_at:'2026-10-01T00:00:00Z'}}); })"); settle(page, 300)
        js(page, "(v)=>td4AddIn(v)", "GOODA BAD$ DUPE GOODB"); js(page, "()=>td4AddCands()"); settle(page, 400)
        p = pop(page)
        errs = {r["k"]: r["err"] for r in p["rows"]}
        check(f"{tag} ตรวจก่อนบันทึก: รูปแบบผิด (BAD$) · ซ้ำ (DUPE) ขึ้น error ทันที · แถวถูกไม่มี error (ยังไม่เลือก Track)", errs.get("BAD$") == "not a valid US ticker" and errs.get("DUPE") == "already a Candidate" and errs.get("GOODA") == "" and errs.get("GOODB") == "", errs)
        js(page, "()=>{ candPopAllTrack('winner'); candPopAllReason('volume-spike'); }"); settle(page, 300)
        page.locator("[data-cp-save]").click(); settle(page, 600)
        m = meta(page); p = pop(page)
        msg = js(page, "()=>td3Msg.add")
        check(f"{tag} บันทึกบางส่วน: GOODA/GOODB บันทึก · BAD$/DUPE ไม่บันทึก · เหลือแต่แถวที่แก้ไม่ได้ → popup ปิด + ข้อความสรุปเหตุผล · โควตานับ 2", m.get("GODA", m.get("GOODA")) and m.get("GOODB") and "BAD$" not in m and not p["open"] and "BAD$: not a valid US ticker" in msg and "DUPE: already a Candidate" in msg and log(page) == ["GOODA", "GOODB"], [list(m), p, log(page), msg])
        check(f"{tag} กล่อง ticker เหลือเฉพาะตัวที่แก้ได้ (BAD$) · DUPE (มีอยู่แล้ว) ถูกตัดออกเหมือนเดิม", js(page, "()=>td4Draft").split() == ["BAD$"], js(page, "()=>td4Draft"))
        # โควตา: เหลือ 1 ห้อง → บันทึกได้ 1 แถวเท่านั้น (นับเฉพาะที่บันทึก)
        js(page, "()=>glWrite(S=>{ const al = Object.assign({}, S.candAddLog||{}); const d = thaiToday(); const have = td4AddLog(d); al[d] = have.concat(Array.from({length:Math.max(0, 9 - have.length)}, (_, i)=>'Q'+i)); S.candAddLog = al; })"); settle(page, 300)
        room = js(page, "()=>TD4_MAX - td4AddLog().length")
        js(page, "(v)=>td4AddIn(v)", "QA QB"); js(page, "()=>td4AddCands()"); settle(page, 400)
        js(page, "()=>{ candPopAllTrack('ladder'); candPopAllReason('strong-rs'); }"); settle(page, 300)
        p = pop(page)
        check(f"{tag} โควตาเหลือ {room} → แถวแรกผ่าน · แถวที่เกินขึ้น 'Daily limit 10 reached'", room == 1 and p["rows"][0]["err"] == "" and "Daily limit" in p["rows"][1]["err"], [room, p])
        page.locator("[data-cp-save]").click(); settle(page, 500)
        check(f"{tag} Save → บันทึกเฉพาะ QA · โควตาเต็ม 10 · QB ไม่ถูกนับ", meta(page).get("QA") and "QB" not in meta(page) and js(page, "()=>td4AddLog().length") == 10, [list(meta(page)), js(page, "()=>td4AddLog().length")])
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def failure_survival_tests(pw, w, h):
    tag = f"[{ENGINE}/survive/{w}]"
    b, page, ce, pe = T.launch(pw, w, h)
    try:
        T.go_today(page)
        js(page, "(v)=>td4AddIn(v)", "SURVA SURVB"); js(page, "()=>td4AddCands()"); settle(page, 400)
        js(page, "()=>{ candPopAllTrack('winner'); candPopAllReason('strong-rs'); candPopIn(0,'note','keep this'); }"); settle(page, 300)
        # จำลอง glWrite ล้มเหลว
        js(page, "()=>{ window.__glw = window.glWrite; window.glWrite = ()=>false; }")
        page.locator("[data-cp-save]").click(); settle(page, 400)
        p = pop(page)
        check(f"{tag} เขียนไม่สำเร็จ (glWrite=false) → ไม่ขึ้นสำเร็จ · popup ค้างพร้อมข้อความ · ไม่บันทึก · โควตาไม่ขยับ", p["open"] and "Could not save" in p["msg"] and meta(page).get("SURVA") is None and log(page) == [], [p, log(page)])
        check(f"{tag} ค่าที่กรอก (Track/เหตุผล/โน้ต) ยังอยู่หลังล้มเหลว · กล่อง ticker ยังอยู่", all(r["track"] == "winner" and r["reasons"] == ["strong-rs"] for r in p["rows"]) and js(page, "()=>candPop.rows[0].note") == "keep this" and js(page, "()=>td4Draft") == "SURVA SURVB", p)
        js(page, "()=>{ window.glWrite = window.__glw; }")
        page.locator("[data-cp-save]").click(); settle(page, 500)
        check(f"{tag} ลองใหม่ (เขียนได้) → บันทึกสำเร็จ 2 แถว · โน้ตถูกเก็บ", meta(page).get("SURVA", {}).get("note") == "keep this" and meta(page).get("SURVB") and log(page) == ["SURVA", "SURVB"], [meta(page).get("SURVA"), log(page)])
        # refresh: ค่าที่เลือกไว้ใน popup ที่ยังไม่บันทึกต้องรอด
        js(page, "(v)=>td4AddIn(v)", "KEEPA"); js(page, "()=>td4AddCands()"); settle(page, 400)
        js(page, "()=>{ candPopAllTrack('ladder'); candPopAllReason('earnings-spike'); candPopIn(0,'link','https://x.test/k'); }"); settle(page, 200)
        P44.reload_keep(page); T.go_today(page); settle(page, 300)
        js(page, "()=>td4AddCands()"); settle(page, 400)
        p = pop(page)
        check(f"{tag} รีเฟรชหน้าแล้วกด Add อีกครั้ง → Track/เหตุผล/ลิงก์ที่เลือกไว้กลับมา (draft รอด refresh)", p["open"] and p["rows"][0]["track"] == "ladder" and p["rows"][0]["reasons"] == ["earnings-spike"] and js(page, "()=>candPop.rows[0].link") == "https://x.test/k", p)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def legacy_hint_tests(pw, w, h):
    tag = f"[{ENGINE}/legacyhint/{w}]"
    b, page, ce, pe = P111.core(pw, w, h)
    try:
        card = {"acct": "main", "ticker": "LEG", "market": "US", "strategy": "W", "plan": {"entry": 100, "stop": 90}, "stop": 90, "stopHistory": [], "px": 100, "pxDate": "2026-10-29", "emaW": 95,
                "lots": [], "trade_id": None, "acc_trade_id": None, "status": "plan", "created_at": "2026-10-20T00:00:00Z", "tier": "A"}
        newc = dict(card, ticker="NEWC", cs={"eval": None, "date": "2026-10-20", "evalDate": "", "stars": None, "stars_src": "none", "baseRiskPct": 1, "riskAmt": 955, "equity": P111.TANK, "used": 0, "budget": P111.TANK * 0.01, "adj": {"ff": 1, "dd": 1}, "capKey": "A"})
        for i, c in (("ccLEG", card), ("ccNEWC", newc)):
            page.evaluate("([id,c])=>window.firebase.__mockDb.__seedDoc(['users','testuid','coreCards',id], c)", [i, c])
        js(page, "()=>{ coreStop(); coreStart(); }"); settle(page, 800); C.go_core(page); settle(page, 400)
        h_ = js(page, "()=>({leg:(document.querySelector('[data-core-card=\"ccLEG\"] [data-c-oldrisk]')||{}).innerText||'', neu:document.querySelectorAll('[data-core-card=\"ccNEWC\"] [data-c-oldrisk]').length})")
        check(f"{tag} แผนเก่า (ไม่มี cs · ยังไม่มีไม้) มีข้อความ 'Old risk rule — re-save as new plan to use Base 1%' · แผนใหม่ (มี cs) ไม่มี", h_["leg"] == "Old risk rule — re-save as new plan to use Base 1%" and h_["neu"] == 0, h_)
        check(f"{tag} ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        reasons_tests(pw, 390, 844)
        for w, h in ((390, 844), (1440, 900)):
            popup_tests(pw, w, h, "today"); popup_tests(pw, w, h, "watch")
        partial_quota_failure_tests(pw, 390, 844)
        failure_survival_tests(pw, 390, 844)
        legacy_hint_tests(pw, 390, 844)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
