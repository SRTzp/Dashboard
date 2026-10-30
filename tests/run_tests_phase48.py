#!/usr/bin/env python3
"""PX2 — EMA ว่างเติมจาก auto · ปุ่มใช้ราคาอัตโนมัติ · พับ/ลบการ์ดที่ปิดแล้ว · ทิศ ▲▼ ผลจับคู่ list · เทส 48
mock Firestore (มี prices) · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 13:03 ไทย · timezone Asia/Bangkok
ภาพ tests/screenshots/px2-{ema-fill,use-auto,closed-group,match-dir}-{1440,390}.png
รัน: python3 run_tests_phase48.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase24 as p24
import run_tests_phase43 as P43
import run_tests_phase47 as P47

js, check, txt, overflow, shot = P43.js, None, P43.txt, P43.overflow, P43.shot
results = P43.results
ENGINE = P43.ENGINE
T = P43.T
px_doc = P43.px_doc


def chk(name, ok, detail=""): P43.check(name, ok, detail)


def view(page, cid="cw"):
    return js(page, """(id)=>{ const c = coreCardsList.find(x=>x.id===id); return c ? {px:c.px, pxDate:c.pxDate, emaW:c.emaW, src:c.pxSrc||null, emaSrc:c.emaSrc||null, sus:!!c._pxSuspect} : null; }""", cid)


def card_txt(page, cid="cw"):
    return js(page, "(id)=>{ const e=document.querySelector('[data-core-card=\"'+id+'\"]'); return e ? e.textContent.replace(/\\s+/g,' ').trim() : ''; }", cid)


def man_card(px=350, px_date="2026-10-02", ema=None, **kw):
    return P43.w_card(px=px, px_date=px_date, ema=ema, **kw)


def launch(pw, w, h, prices=None, cards=None, doc=None):
    return P43.launch(pw, w, h, prices, None, cards, doc)


def closed_card(cid, tid, ticker, by=None, status="closed", acct="main"):
    c = p24.open_card(cid, tid, ticker=ticker, acct=acct, qty=100, entry=100, sl=90, px=100, pxDate="2026-10-01", emaW=95)
    c["status"] = status
    if by: c["closedBy"] = by
    return c


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ───── 1 · EMA ว่าง + auto วันเดียวกัน ─────
    b, c, page, ce, pe, d = launch(pw, w, h, {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06)}, {"cw": man_card()})
    try:
        s = view(page)
        chk(f"{tag} 1 กรอกเอง 350 (2 ต.ค.) ไม่มี EMA + auto 355.14/367.06 วันเดียวกัน → px 350 · emaW 367.06 · pxSrc manual · emaSrc auto", s == {"px": 350, "pxDate": "2026-10-02", "emaW": 367.06, "src": "manual", "emaSrc": "auto", "sus": False}, json.dumps(s))
        js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(200)
        t = card_txt(page)
        chk(f"{tag} 1 หน้าการ์ดมี 'EMA10 อัตโนมัติ' + 367.06 · ไม่มี 'ยังไม่กรอก EMA10'", "EMA10 อัตโนมัติ" in t and "367.06" in t and "ยังไม่กรอก EMA10" not in t, t[:400])
        chk(f"{tag} 1 ช่อง EMA ที่แสดง = 367.06 · ราคา = 350", txt(page, '[data-core-card="cw"] [data-c-ema]') == "367.06" and txt(page, '[data-core-card="cw"] [data-c-px]') == "350", json.dumps([txt(page, '[data-core-card="cw"] [data-c-ema]'), txt(page, '[data-core-card="cw"] [data-c-px]')]))
        st = js(page, "()=>document.querySelector('[data-core-card=cw]').dataset.status")
        chk(f"{tag} 1 สถานะใช้ EMA ที่เติม: 350 < 367.06 → เหลือง (ปิดใต้ EMA10)", st == "yellow", st)
        # action อื่น (เลื่อน Stop) ต้องไม่เขียน emaW ลง coreCards
        js(page, "()=>coreStopOpen('cw')"); page.wait_for_selector("#csStop"); page.fill("#csStop", "85"); page.wait_for_timeout(150)
        js(page, "()=>coreStopSave()"); page.wait_for_timeout(500)
        dc = p24.cards_db(page).get("cw")
        chk(f"{tag} 1 coreCards: ไม่มี emaW ถูกเขียน (ยัง null) · px 350 · stop 85 · ไม่มี emaSrc", dc and dc.get("emaW") is None and dc["px"] == 350 and dc["stop"] == 85 and "emaSrc" not in dc and "_pxMan" not in dc, json.dumps({k: (dc or {}).get(k) for k in ("emaW", "px", "stop", "emaSrc")}))
        shot(page, f"px2-ema-fill-{sfx}.png", '[data-core-card="cw"]')
        chk(f"{tag} 7 (1) ไม่ล้นแนวนอน", overflow(page) <= 0, str(overflow(page)))
        chk(f"{tag} 7 (1) ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally: b.close()

    # ───── 2 · กรณีที่ไม่เติม ─────
    cases = [
        ("กรอกเองมี EMA 360 → ใช้ 360 ไม่ทับ", {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06)}, {"cw": man_card(ema=360)}, lambda s: s["emaW"] == 360 and s["emaSrc"] is None),
        ("auto วันเก่ากว่า (25 ก.ย.) → ไม่เติม", {"AAA": px_doc("AAA", 355.14, "2026-09-25", ema=367.06)}, {"cw": man_card()}, lambda s: s["emaW"] is None and s["src"] == "manual" and s["emaSrc"] is None),
        ("auto suspect → ไม่เติม", {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06, suspect=True)}, {"cw": man_card()}, lambda s: s["emaW"] is None and s["sus"] and s["emaSrc"] is None),
        ("การ์ด L → ไม่เติม", {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06)}, {"cw": man_card(strategy="L")}, lambda s: s["emaW"] is None and s["emaSrc"] is None),
    ]
    for name, prices, cards, ok in cases:
        b, c, page, ce, pe, d = launch(pw, w, h, prices, cards)
        try:
            s = view(page)
            chk(f"{tag} 2 {name}", s and ok(s), json.dumps(s))
            if "EMA 360" in name:
                js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(150)
                chk(f"{tag} 2 EMA 360 → หน้าการ์ดไม่มี 'EMA10 อัตโนมัติ'", "EMA10 อัตโนมัติ" not in card_txt(page), card_txt(page)[:300])
            if "วันเก่า" in name:
                js(page, "()=>coreAll('main',1)"); page.wait_for_timeout(150)
                chk(f"{tag} 2 auto เก่า → หน้าการ์ดยังเขียน 'ยังไม่กรอก EMA10'", "ยังไม่กรอก EMA10" in card_txt(page), card_txt(page)[:300])
        finally: b.close()

    # ───── 3 · ปุ่มใช้ราคาอัตโนมัติแทน ─────
    def has_btn(page):
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        r = page.locator("[data-c-useauto]").count() == 1
        js(page, "()=>coreSheetClose()"); return r
    good = {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06)}
    b, c, page, ce, pe, d = launch(pw, w, h, good, {"cw": man_card()})
    try:
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx")
        chk(f"{tag} 3 manual + auto ดี → มีปุ่ม 'ใช้ราคาอัตโนมัติแทน' ใต้บรรทัดราคาอัตโนมัติล่าสุด", page.locator("[data-c-useauto]").count() == 1 and "ใช้ราคาอัตโนมัติแทน" in (txt(page, "[data-c-useauto]") or "") and js(page, "()=>{ const l=document.querySelector('[data-px-autoline]'), b=document.querySelector('[data-c-useauto]'); return !!(l.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING); }"))
        shot(page, f"px2-use-auto-{sfx}.png", ".core-sheet")
        # ยกเลิก
        page.click("[data-c-useauto]"); page.wait_for_selector("[data-pxauto-msg]")
        msg = txt(page, "[data-pxauto-msg]") or ""
        chk(f"{tag} 3 ยืนยันในตัว sheet: 'ลบราคาที่กรอกเอง (350 · ศ. 2 ต.ค.) แล้วใช้ราคาอัตโนมัติ 355.14 · EMA10 367.06 (ศ. 2 ต.ค.)' + คำเตือน 1 บรรทัด",
              msg == "ลบราคาที่กรอกเอง (350 · ศ. 2 ต.ค.) แล้วใช้ราคาอัตโนมัติ 355.14 · EMA10 367.06 (ศ. 2 ต.ค.)" and "ถ้าราคาอัตโนมัติหยุดอัปเดต การ์ดนี้จะขาดราคาจนกว่าจะกรอกใหม่" in (txt(page, ".core-sheet") or ""), msg)
        shot(page, f"px2-use-auto-{sfx}.png", ".core-sheet")
        page.click("[data-pxauto-cancel]"); page.wait_for_timeout(300)
        dc = p24.cards_db(page).get("cw"); s = view(page)
        chk(f"{tag} 3 ยกเลิก → ไม่เปลี่ยน (coreCards px 350 · pxDate 2026-10-02 · การ์ดยัง manual)", dc["px"] == 350 and dc["pxDate"] == "2026-10-02" and s["src"] == "manual" and page.locator(".core-sheet").count() == 0, json.dumps([dc.get("px"), s]))
        # ตกลง
        js(page, "()=>corePxOpen('cw')"); page.wait_for_selector("#cpxPx"); page.click("[data-c-useauto]"); page.wait_for_selector("[data-pxauto-ok]")
        page.click("[data-pxauto-ok]"); page.wait_for_timeout(500)
        dc = p24.cards_db(page).get("cw"); s = view(page)
        chk(f"{tag} 3 ตกลง → coreCards px/pxDate/emaW = null · การ์ดแสดง 355.14 / 367.06 ป้ายอัตโนมัติ", dc["px"] is None and dc["pxDate"] is None and dc["emaW"] is None and s["px"] == 355.14 and s["emaW"] == 367.06 and s["src"] == "auto" and txt(page, '[data-core-card="cw"] [data-c-pxsrc]').startswith("อัตโนมัติ"), json.dumps([dc.get("px"), dc.get("pxDate"), dc.get("emaW"), s]))
        chk(f"{tag} 3 หลังใช้ auto แล้ว → sheet ไม่มีปุ่ม (ใช้ auto อยู่)", not has_btn(page))
        chk(f"{tag} 7 (3) ไม่ล้น · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()
    for name, prices, cards in (
        ("ไม่มี auto", None, {"cw": man_card()}),
        ("auto suspect", {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06, suspect=True)}, {"cw": man_card()}),
        ("การ์ดใช้ auto อยู่แล้ว", {"AAA": px_doc("AAA", 355.14, "2026-10-02", ema=367.06)}, {"cw": man_card(px=300, px_date="2026-09-26", ema=290)}),
    ):
        b, c, page, ce, pe, d = launch(pw, w, h, prices, cards)
        try:
            chk(f"{tag} 3 {name} → ไม่มีปุ่ม 'ใช้ราคาอัตโนมัติแทน'", not has_btn(page))
        finally: b.close()
    # ฟังก์ชันกันซ้ำ: เรียก corePxAutoGo ตรง ๆ กับการ์ดที่ไม่ manual → ไม่เขียน
    b, c, page, ce, pe, d = launch(pw, w, h, None, {"cw": man_card()})
    try:
        js(page, "()=>corePxAutoGo('cw')"); page.wait_for_timeout(300)
        dc = p24.cards_db(page).get("cw")
        chk(f"{tag} 3 ไม่มี auto + เรียก corePxAutoGo ตรง ๆ → ไม่ลบค่ากรอกเอง (px 350)", dc["px"] == 350 and dc["pxDate"] == "2026-10-02", json.dumps([dc["px"], dc["pxDate"]]))
    finally: b.close()

    # ───── 4 · การ์ดปิดแล้ว พับรวม + ลบ ─────
    doc = P43.base_doc()
    doc["books"]["main"]["trades"] = [T("tw", "core", "open", sym="AAA", entry=100, sl=80, qty=100, cur="USD", date="2026-09-10", openedAt="2026-09-10"),
        T("t1", "core", "closed", sym="BBB", entry=100, sl=90, qty=10, exit=110, exitPrice=110, exitDate="2026-09-20", unplanned=False),
        T("t2", "core", "closed", sym="CCC", entry=100, sl=90, qty=10, exit=95, exitPrice=95, exitDate="2026-09-22", unplanned=False)]
    cards = {"cw": P43.w_card(), "c1": closed_card("c1", "t1", "BBB", by=None), "c2": closed_card("c2", "t2", "CCC", by="delete"),
             "cp": p24.card("cp", "main", "PPP", plan={"entry": 50, "stop": 45}, stop=45)}
    b, c, page, ce, pe, d = launch(pw, w, h, None, cards, doc)
    try:
        grp = "[data-c-closedgroup]"
        chk(f"{tag} 4 การ์ดปิดแล้ว 2 ใบ → <details> เดียว 'ปิดแล้ว 2 ตัว' พับไว้ · ไม่มี .ccClosed นอกกลุ่ม", page.locator(grp).count() == 1 and txt(page, grp + " > summary") == "ปิดแล้ว 2 ตัว" and js(page, "()=>document.querySelector('[data-c-closedgroup]').open") is False and js(page, "()=>[...document.querySelectorAll('.ccClosed')].every(e=>e.closest('[data-c-closedgroup]'))"), txt(page, grp + " > summary"))
        page.click(grp + " > summary"); page.wait_for_timeout(200)
        rows = js(page, "()=>[...document.querySelectorAll('[data-c-closedgroup] [data-kind=closed]')].map(e=>({id:e.dataset.coreCard, t:e.textContent.replace(/\\s+/g,' ').trim(), btn:!!e.querySelector('[data-c-delclosed]'), vis:e.getBoundingClientRect().width>0}))")
        chk(f"{tag} 4 เปิดแล้วเห็น 2 แถว + ปุ่ม 'ลบการ์ด' · ข้อความ BBB 'ปิดตำแหน่ง' / CCC 'ลบไม้' + บรรทัดไม้", len(rows) == 2 and all(r["btn"] and r["vis"] for r in rows) and any("BBB" in r["t"] and "ปิดตำแหน่ง" in r["t"] and "ไม้ 1" in r["t"] for r in rows) and any("CCC" in r["t"] and "ลบไม้" in r["t"] for r in rows), json.dumps(rows, ensure_ascii=False)[:500])
        shot(page, f"px2-closed-group-{sfx}.png", "[data-core-acct=main]")
        # ผลข้อ 5 — ก่อนลบ
        snap = lambda: js(page, """()=>withAccount('main', ()=>{ const s=journalStats(); const f=o=>({n:o.n,wins:o.wins,wr:o.winRate,pnl:o.totalPnlTHB,off:o.nOffPlan,inc:o.nSetupInc,offP:o.offPnlTHB}); return {all:f(s.overall), core:f(s.core), setup:jSetupGroups(s.closed), offPlan:state.trades.filter(tradeOffPlan).map(t=>t.id)}; })""")
        before = snap()
        js(page, "()=>coreDelClosedAsk('c1')"); page.wait_for_selector("[data-delclosed-msg]")
        m = txt(page, "[data-delclosed-msg]") or ""
        chk(f"{tag} 4 sheet ยืนยัน: 'ลบการ์ด BBB ที่ปิดแล้ว — ไม้ใน Journal ยังอยู่ครบ สถิติไม่เปลี่ยน · ประวัติไม้/Stop ในการ์ดจะหาย'", m == "ลบการ์ด BBB ที่ปิดแล้ว — ไม้ใน Journal ยังอยู่ครบ สถิติไม่เปลี่ยน · ประวัติไม้/Stop ในการ์ดจะหาย", m)
        page.click("[data-delclosed-cancel]"); page.wait_for_timeout(200)
        chk(f"{tag} 4 ยกเลิก → doc c1 ยังอยู่", "c1" in p24.cards_db(page))
        js(page, "()=>coreDelClosedAsk('c1')"); page.wait_for_selector("[data-delclosed-ok]"); page.click("[data-delclosed-ok]"); page.wait_for_timeout(500)
        db = p24.cards_db(page)
        chk(f"{tag} 4 ลบ c1 → doc หาย · c2 ยังอยู่ · เหลือ 'ปิดแล้ว 1 ตัว'", "c1" not in db and "c2" in db and txt(page, grp + " > summary") == "ปิดแล้ว 1 ตัว", json.dumps([list(db), txt(page, grp + " > summary")]))
        after1 = snap()
        js(page, "()=>coreDelClosedAsk('c2')"); page.wait_for_selector("[data-delclosed-ok]"); page.click("[data-delclosed-ok]"); page.wait_for_timeout(500)
        db = p24.cards_db(page)
        chk(f"{tag} 4 ลบหมด → ส่วน 'ปิดแล้ว' หาย · การ์ด open/plan ยังอยู่", "c2" not in db and page.locator(grp).count() == 0 and "cw" in db and "cp" in db, json.dumps(list(db)))
        after2 = snap()
        chk(f"{tag} 5 สถิติก่อน/หลังลบการ์ดปิดแล้ว เท่ากันทุกค่า (wins · Win Rate · P&L · ไม้นอกแผน · setup stats · รายชื่อไม้นอกแผน)", before == after1 == after2 and before["core"]["n"] == 2, json.dumps([before, after2], ensure_ascii=False)[:600])
        nt = js(page, "()=>getBook('main').trades.map(t=>t.id)")
        chk(f"{tag} 5 ไม้ใน Journal ยังอยู่ครบ (t1 · t2 · tw)", all(x in nt for x in ("t1", "t2", "tw")), json.dumps(nt))
        # กันที่ฟังก์ชัน
        r = [js(page, "(id)=>coreDeleteClosed(id)", i) for i in ("cw", "cp")]
        js(page, "()=>{ coreDelClosedAsk('cw'); coreDelClosedAsk('cp'); }"); page.wait_for_timeout(300)
        db = p24.cards_db(page)
        chk(f"{tag} 4 coreDeleteClosed / coreDelClosedAsk กับการ์ด open/plan → ไม่ลบ · ไม่เปิด sheet", "cw" in db and "cp" in db and r == [False, False] and page.locator("[data-delclosed-msg]").count() == 0, json.dumps([list(db), r]))
        chk(f"{tag} 7 (4) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()

    # ───── 6 · จับคู่ list: ทิศ ▲▼ ─────
    b, c, page, ce, pe, dl = P47.launcher(pw, w, h, [P47.semis()])
    try:
        P47.open_match(page, P47.CSV)
        info = js(page, """()=>{ const o={}, W=document.querySelector('.mtR') ? null : null; document.querySelectorAll('[data-match-row]').forEach(e=>{ const x=e.querySelector('.mtX'), d=x.querySelector('[data-match-dir]'), r=e.getBoundingClientRect(), dr=d?d.getBoundingClientRect():null, xr=x.getBoundingClientRect();
          o[e.dataset.matchRow]={dir:d?d.textContent:null, color:d?getComputedStyle(d).color:null, inRow: dr ? (dr.left>=r.left-0.5 && dr.right<=r.right+0.5 && dr.width>0) : null, inX: dr ? (dr.right<=xr.right+0.5) : null, text:x.textContent, dd:e.dataset.dir, nseg:e.dataset.nseg, scroll:e.scrollWidth-e.clientWidth}; }); return o; }""")
        rgb = lambda s: [int(v) for v in s[s.index("(") + 1:-1].split(",")[:3]]
        cam, ter, lscc = info["CAMT"], info["TER"], info["LSCC"]
        chk(f"{tag} 6 CAMT: ▼ 1 ส่วน มองเห็นในกรอบแถว (ไม่ถูกตัด) · สีแดง", cam["dir"] == "▼ 1 ส่วน" and cam["inRow"] and cam["inX"] and (lambda c: c[0] > c[1] + 60 and c[0] > c[2] + 60)(rgb(cam["color"])), json.dumps(cam, ensure_ascii=False))
        chk(f"{tag} 6 TER: ▲ 1 ส่วน มองเห็น · สีเขียว · LSCC ▲ 4 ส่วน", ter["dir"] == "▲ 1 ส่วน" and ter["inRow"] and ter["inX"] and (lambda c: c[1] > c[0] + 40 and c[1] > c[2])(rgb(ter["color"])) and lscc["dir"] == "▲ 4 ส่วน" and lscc["inRow"], json.dumps([ter, lscc], ensure_ascii=False))
        chk(f"{tag} 6 data-dir / data-nseg เดิมคงไว้ · ทิศอยู่ก่อนชื่อไอเดีย", cam["dd"] == "▼" and cam["nseg"] == "1" and ter["dd"] == "▲" and lscc["nseg"] == "4" and cam["text"].startswith("▼ 1 ส่วน · "), json.dumps([cam["dd"], cam["nseg"], cam["text"]], ensure_ascii=False))
        # mixed + in-idea: seed ผ่าน matchLayer1 จริงด้วยไอเดียที่มี segment effect mixed
        mix = js(page, """()=>{ const r={sym:'ZZ',desc:'',industry:'x',kind:'ind',dir:'▲▼',nSeg:2,ideas:[{v:{name:'ไอเดียทดสอบ'}}],inWl:false}; const h=document.createElement('div'); h.innerHTML=matchRowHtml(r); const d=h.querySelector('[data-match-dir]'); document.body.appendChild(h); const col=getComputedStyle(d).color; h.remove(); return {t:d.textContent, col}; }""")
        mc = rgb(mix["col"])
        chk(f"{tag} 6 ▲▼ (mixed) → ข้อความ '▲▼ 2 ส่วน' สีเหลือง (แดง/เขียวสูงใกล้กัน · น้ำเงินต่ำ)", mix["t"] == "▲▼ 2 ส่วน" and mc[0] > 180 and mc[1] > 150 and mc[2] < 100, json.dumps(mix))
        chk(f"{tag} 6 แถวไม่ล้นกรอบ (scrollWidth - clientWidth ≤ 1 ทุกแถว)", all(v["scroll"] <= 1 for v in info.values()), json.dumps({k: v["scroll"] for k, v in info.items()}))
        P47.shot_modal(page, f"px2-match-dir-{sfx}.png")
        chk(f"{tag} 7 (6) ไม่ล้นแนวนอน · ไม่มี console error", P47.overflow(page) <= 0 and not ce and not pe, json.dumps([P47.overflow(page), ce, pe]))
    finally: b.close()


    # ───── 8–10 · PX2-fix: ลบการ์ดปิดแล้ว → ล้างธง unplanned ค้างของไม้ที่ผูก ─────
    def fix_doc(flag_t1=True):
        doc = P43.base_doc()
        doc["books"]["main"]["trades"] = [
            T("t1", "core", "closed", sym="BBB", entry=100, sl=90, qty=10, exit=110, exitPrice=110, exitDate="2026-09-20", unplanned=flag_t1),
            T("t2", "core", "closed", sym="CCC", entry=100, sl=90, qty=10, exit=95, exitPrice=95, exitDate="2026-09-22", unplanned=False)]
        return doc
    FLAG = "[data-delclosed-flag]"
    FLAG_TX = 'ไม้นี้ติดธง "นอกแผน" ค้างจากระบบเก่า — จะตั้งเป็น "ตามแผน" ให้ (ซื้อผ่านการ์ด)'
    snap2 = """()=>withAccount('main', ()=>{ const s=journalStats(); const f=o=>({n:o.n,wins:o.wins,wr:o.winRate,pnl:o.totalPnlTHB,off:o.nOffPlan,inc:o.nSetupInc,offP:o.offPnlTHB}); return {all:f(s.overall), core:f(s.core), setup:jSetupGroups(s.closed), offPlan:state.trades.filter(tradeOffPlan).map(t=>t.id)}; })"""
    # 8 · ไม้ติดธง
    cards = {"c1": closed_card("c1", "t1", "BBB"), "c2": closed_card("c2", "t2", "CCC", by="delete")}
    b, c, page, ce, pe, d = launch(pw, w, h, None, cards, fix_doc(True))
    try:
        js(page, "()=>coreAll('main',1)")
        before = js(page, snap2)
        t1b = js(page, "()=>JSON.parse(JSON.stringify(getBook('main').trades.find(t=>t.id==='t1')))")
        js(page, "()=>coreDelClosedAsk('c1')"); page.wait_for_selector("[data-delclosed-ok]")
        chk(f"{tag} 8 ไม้ผูกติด unplanned:true → sheet มีบรรทัดธงค้าง", txt(page, FLAG) == FLAG_TX, txt(page, FLAG) or "")
        page.click("[data-delclosed-ok]"); page.wait_for_timeout(500)
        t1a = js(page, "()=>JSON.parse(JSON.stringify(getBook('main').trades.find(t=>t.id==='t1')))")
        diff = [k for k in set(t1a) | set(t1b) if t1a.get(k) != t1b.get(k)]
        chk(f"{tag} 8 ลบ → ไม้ unplanned:false · field อื่นเท่าเดิมทุกตัว", t1b["unplanned"] is True and t1a["unplanned"] is False and diff == ["unplanned"], json.dumps(diff))
        chk(f"{tag} 8 การ์ด c1 หาย (c2 ยังอยู่)", "c1" not in p24.cards_db(page) and "c2" in p24.cards_db(page))
        after = js(page, snap2)
        chk(f"{tag} 8 ไม้นอกแผน / statsFor / สถิติ setup เท่าก่อนลบ", before == after and before["offPlan"] == [], json.dumps([before, after], ensure_ascii=False)[:400])
        chk(f"{tag} 8 ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()
    # 9 · ไม้ไม่มีธง / การ์ด "ลบไม้" (ไม่มีไม้)
    cards = {"c1": closed_card("c1", "t1", "BBB"), "c3": closed_card("c3", "tGone", "DDD", by="delete")}
    b, c, page, ce, pe, d = launch(pw, w, h, None, cards, fix_doc(False))
    try:
        js(page, "()=>coreAll('main',1)")
        js(page, """()=>{ window.__sb=0; const o=window.saveBook; window.saveBook=function(){ window.__sb++; return o.apply(this,arguments); }; }""")
        docb = js(page, "()=>JSON.stringify(getBook('main').trades)")
        js(page, "()=>coreDelClosedAsk('c1')"); page.wait_for_selector("[data-delclosed-ok]")
        chk(f"{tag} 9 ไม้ไม่มีธง → ไม่มีบรรทัดธงค้าง", page.locator(FLAG).count() == 0)
        page.click("[data-delclosed-ok]"); page.wait_for_timeout(500)
        chk(f"{tag} 9 ลบแล้วไม้ไม่ถูกเขียน (doc เท่าเดิม · saveBook 0 ครั้ง) · การ์ดหาย", js(page, "()=>JSON.stringify(getBook('main').trades)") == docb and js(page, "()=>window.__sb") == 0 and "c1" not in p24.cards_db(page))
        js(page, "()=>coreDelClosedAsk('c3')"); page.wait_for_selector("[data-delclosed-ok]")
        nf = page.locator(FLAG).count()
        page.click("[data-delclosed-ok]"); page.wait_for_timeout(500)
        chk(f"{tag} 9 การ์ด 'ลบไม้' (ไม่มีไม้) → ลบได้ · ไม่ error · ไม่เขียนไม้", nf == 0 and "c3" not in p24.cards_db(page) and js(page, "()=>window.__sb") == 0 and not ce and not pe and page.locator("[data-core-err]").count() == 0, json.dumps([ce, pe]))
    finally: b.close()
    # 10 · เขียนไม้ล้ม → ไม่ลบการ์ด + error บนจอ
    cards = {"c1": closed_card("c1", "t1", "BBB"), "c2": closed_card("c2", "t2", "CCC", by="delete")}
    b, c, page, ce, pe, d = launch(pw, w, h, None, cards, fix_doc(True))
    try:
        js(page, "()=>coreAll('main',1)")
        js(page, "()=>{ window.saveBook=function(){ throw new Error('write failed'); }; }")
        js(page, "()=>coreDelClosedAsk('c1')"); page.wait_for_selector("[data-delclosed-ok]"); page.click("[data-delclosed-ok]"); page.wait_for_timeout(500)
        err = txt(page, "[data-core-err]") or ""
        chk(f"{tag} 10 เขียนไม้ล้ม → การ์ดยังอยู่ · error บนจอ · ไม้ยัง unplanned:true (ไม่ค้างครึ่งทาง)", "c1" in p24.cards_db(page) and "write failed" in err and js(page, "()=>getBook('main').trades.find(t=>t.id==='t1').unplanned") is True, json.dumps([list(p24.cards_db(page)), err], ensure_ascii=False))
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 48 / PX2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
