#!/usr/bin/env python3
"""ID3b — 📝 ตอบข้อที่ขาด · ปิด "หาไม่ได้" ในแอป · Import ผล update (Ideas › หลักฐาน) · เทส 49
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 (จันทร์ เวลาไทย) · fixture: idea_semis.json (+ เติมข้อ track/skip ในสำเนาของเทส)
ภาพ tests/screenshots/id3b-{gaps-table,answer-sheet,unanswerable}-{1440,390}.png
รัน: python3 run_tests_phase49.py"""
import copy, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase44 as P44
import run_tests_phase47 as P47

P40 = P47.P40
js, check, txt_of = P40.js, P40.check, P40.txt_of
results = P40.results
ENGINE = P40.ENGINE
SHOTS = P40.SHOTS
IID = "semis-ai-memory-2026"
LSK = "ideaGapDraft"


def idea(**mods):
    d = P44.semis()                                  # มีบริษัท KLAC study + relevance_src · หลักฐานขัดแย้ง · kill 3
    g = {x["id"]: x for x in d["gaps"]}
    d["gaps"] = [g[3], g[1], g[2], dict(g[3], id=4, q="ราคาหุ้นเทียบกับค่าเฉลี่ยย้อนหลัง 10 ปี", priority="skip", where="", why="ไม่คุ้มเวลา")]   # สลับลำดับ: ติดตามมาก่อน เพื่อเช็กการเรียง
    d["status"] = "need_evidence"; d.update(mods); return d


def launch(pw, w, h, user=None, **mods):
    return P47.launcher(pw, w, h, [(idea(**mods), user)] if user is not None else [idea(**mods)], wl=())   # นาฬิกา 2026-10-05 แบบ phase47


def go_evd(page):
    P44.go_ideas(page, IID); P44.tabk(page, "evd")


def rows(page):
    return js(page, """()=>[...document.querySelectorAll('[data-idea-gaps] [data-idea-gap]')].map(e=>({id:e.dataset.ideaGap, st:e.dataset.gapStatus, tick:!!e.querySelector('[data-idea-gap-tick]'), ans:!!e.querySelector('[data-idea-gap-ans]'), un:!!e.querySelector('[data-idea-gap-unans]'), reopen:!!e.querySelector('[data-idea-gap-reopen]'), inSkip:!!e.closest('[data-idea-gap-skip]'),
      txt:e.textContent.replace(/\\s+/g,' ').trim()}))""")


def drafts(page): return js(page, "()=>{ try{ return JSON.parse(localStorage.getItem('ideaGapDraft')||'{}'); }catch(e){ return null; } }")
def user_of(page): return (P44.idb(page, IID) or {}).get("user") or {}
def idea_of(page): return (P44.idb(page, IID) or {}).get("idea")
def overflow(page): return P44.overflow(page)
def over_modal(page): return js(page, "()=>{ const m=document.getElementById('ltModal'); return m.scrollWidth - m.clientWidth; }")
def ready(page): return js(page, "(id)=>ideaReady(ideaFind(id))", IID)
def shot_modal(page, name): P47.shot_modal(page, name)
def shot_el(page, name, sel):
    page.wait_for_timeout(400)
    try: page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e: print("shot fail", name, e)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    mob = w <= 430
    # ───── 1 · ตาราง ─────
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        go_evd(page)
        R = rows(page)
        main = [r for r in R if not r["inSkip"]]; skip = [r for r in R if r["inSkip"]]
        chk = lambda n, ok, d="": check(f"{tag} {n}", ok, d)
        chk("1 เรียง ต้องรู้ → ติดตาม (1, 2, 3) แม้ข้อมูลเรียง 3,1,2 · ข้ามอยู่ในพับ 'ข้าม (1)' (ข้อ 4) · ปิดไว้เป็นค่าเริ่ม", [r["id"] for r in main] == ["1", "2", "3"] and [r["id"] for r in skip] == ["4"] and "ข้าม (1)" in (txt_of(page, "[data-idea-gap-skip] > summary") or "") and js(page, "()=>document.querySelector('[data-idea-gap-skip]').open") is False, json.dumps([[r["id"] for r in main], [r["id"] for r in skip]]))
        chk("1 แถว open ทุกแถวมีติ๊ก + 📝 ตอบ + หาไม่ได้ (รวมข้อในพับ)", all(r["st"] == "open" and r["tick"] and r["ans"] and r["un"] for r in R) and len(R) == 4, json.dumps([[r["id"], r["tick"], r["ans"], r["un"]] for r in R]))
        chk("1 ปุ่ม '📝 ตอบที่เลือก (0)' กดไม่ได้ตอนยังไม่ติ๊ก", js(page, "()=>document.querySelector('[data-idea-gap-ansel]').disabled") is True and "(0)" in (txt_of(page, "[data-idea-gap-ansel]") or ""))
        if mob:
            hs = js(page, "()=>[...document.querySelectorAll('[data-idea-gap] button, [data-idea-gap-ansel]')].filter(b=>b.getBoundingClientRect().width>0).map(b=>Math.round(b.getBoundingClientRect().height))")
            chk("1 มือถือ: รายการซ้อน (.ltStk · ไม่ใช่ table) · ปุ่มสูง ≥ 36px", js(page, "()=>!document.querySelector('[data-idea-gaps] table') && !!document.querySelector('[data-idea-gaps] .ltStk')") and hs and min(hs) >= 36, json.dumps(hs))
        else:
            chk("1 เดสก์ท็อป: เป็นตาราง (หัว ข้อที่ขาด · ระดับ · สถานะ · คำตอบ)", js(page, "()=>!!document.querySelector('[data-idea-gaps] table')") and "ข้อที่ขาด" in (txt_of(page, "[data-idea-gaps] th:nth-child(2)") or ""))
        shot_el(page, f"id3b-gaps-table-{sfx}.png", ".wlDBody")
        chk("7 (1) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()

    # ───── 2 · 📝 ตอบ ─────
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        chk = lambda n, ok, d="": check(f"{tag} {n}", ok, d)
        go_evd(page)
        page.check('[data-idea-gap-tick="1"]'); page.check('[data-idea-gap-tick="2"]'); page.wait_for_timeout(100)
        chk("2 ติ๊ก 2 ข้อ → '📝 ตอบที่เลือก (2)' กดได้", "(2)" in (txt_of(page, "[data-idea-gap-ansel]") or "") and js(page, "()=>document.querySelector('[data-idea-gap-ansel]').disabled") is False)
        page.click("[data-idea-gap-ansel]"); page.wait_for_selector("[data-idea-gap-box]")
        boxes = js(page, "()=>[...document.querySelectorAll('[data-idea-gap-box]')].map(e=>({id:e.dataset.ideaGapBox, t:e.textContent.replace(/\\s+/g,' ').trim()}))")
        chk("2 sheet: 1 กล่องต่อข้อ '#1 {q}' + 'หาจาก: …' + ช่อง 'สิ่งที่หามา (ข้อความ / ลิงก์)' · บอกแนบภาพ/PDF ในแชท AI", [x["id"] for x in boxes] == ["1", "2"] and boxes[0]["t"].startswith("#1 กำลังผลิต HBM/DRAM") and "หาจาก: แผน capex" in boxes[0]["t"] and "สิ่งที่หามา (ข้อความ / ลิงก์)" in boxes[0]["t"] and "ภาพหน้าจอ / PDF → แนบในแชท AI พร้อมคำสั่งนี้" in (txt_of(page, "[data-idea-gap-hint]") or ""), json.dumps(boxes, ensure_ascii=False)[:400])
        chk("2 ทุกช่องว่าง → ปุ่ม 'คัดลอกคำสั่ง' กดไม่ได้ + มีเหตุผล", js(page, "()=>document.getElementById('ideaGapCopyBtn').disabled") is True and (txt_of(page, "[data-idea-gap-why]") or "") != "")
        page.fill('[data-idea-gap-ta="1"]', "Micron แจ้ง capex FY27 $20B (IR deck สไลด์ 12)"); page.wait_for_timeout(100)
        chk("2 พิมพ์ข้อ 1 → ปุ่มกดได้ · ร่างถูกเก็บใน localStorage (ต่อ ไอเดีย+ข้อ)", js(page, "()=>document.getElementById('ideaGapCopyBtn').disabled") is False and (drafts(page) or {}).get(f"{IID}|1") == "Micron แจ้ง capex FY27 $20B (IR deck สไลด์ 12)" and f"{IID}|2" not in (drafts(page) or {}), json.dumps(drafts(page), ensure_ascii=False))
        shot_modal(page, f"id3b-answer-sheet-{sfx}.png")
        page.click("#ideaGapCopyBtn"); page.wait_for_timeout(400)
        cmd = js(page, "()=>window.__ideaLastGap") or ""
        head, _, tail = cmd.partition("JSON เดิม (idea@1):\n")
        obj = None
        try: obj = json.loads(tail)
        except Exception: pass
        lines = head.split("\n")
        chk("2 คำสั่ง: บรรทัดแรก 'idea-scout update · ตอบข้อที่ขาด #1' (ไม่มี #2) · 'ไอเดีย: {name} ({id})' · '#1 {q}' + 'สิ่งที่ผู้ใช้หามา: …' · บอกแนบภาพ/PDF · ---", lines[0] == "idea-scout update · ตอบข้อที่ขาด #1" and lines[1] == f"ไอเดีย: {idea()['name']} ({IID})" and lines[2].startswith("#1 กำลังผลิต HBM/DRAM") and lines[3] == "สิ่งที่ผู้ใช้หามา: Micron แจ้ง capex FY27 $20B (IR deck สไลด์ 12)" and "#2" not in head and "(ภาพ / PDF แนบในแชทนี้ ถ้ามี)" in head and "\n---\n" in cmd, json.dumps(lines[:6], ensure_ascii=False))
        chk("2 JSON เดิมต่อท้าย parse ได้ · schema idea@1 · id ตรง", obj is not None and obj.get("schema") == "idea@1" and obj.get("id") == IID and len(obj.get("gaps", [])) == 4, (tail or "")[:120])
        chk("2 ข้อความยืนยัน 'คัดลอกแล้ว — วางให้ idea-scout แล้ว 📥 Import ผลกลับมา' · ร่างยังอยู่ (คัดลอกแล้วไม่ล้าง)", "คัดลอกแล้ว — วางให้ idea-scout แล้ว 📥 Import ผลกลับมา" in (txt_of(page, "[data-idea-gap-copy]") or "") and f"{IID}|1" in (drafts(page) or {}), txt_of(page, "[data-idea-gap-copy]"))
        page.fill('[data-idea-gap-ta="2"]', "x"); page.fill('[data-idea-gap-ta="1"]', ""); page.fill('[data-idea-gap-ta="2"]', "ข้อ 2 ด้วย"); page.wait_for_timeout(100)
        page.click("#ideaGapCopyBtn"); page.wait_for_timeout(300)
        cmd2 = js(page, "()=>window.__ideaLastGap") or ""
        chk("2 ข้อ 1 ว่าง + ข้อ 2 มีข้อความ → คำสั่งมีเฉพาะ #2 (ตัดข้อว่างออก)", cmd2.split("\n")[0] == "idea-scout update · ตอบข้อที่ขาด #2" and "#1 " not in cmd2.split("---")[0], cmd2.split("\n")[0])
        page.fill('[data-idea-gap-ta="1"]', "กลับมาพิมพ์ข้อ 1"); page.wait_for_timeout(100)
        page.click("#ideaGapCopyBtn"); page.wait_for_timeout(300)
        cmd3 = js(page, "()=>window.__ideaLastGap") or ""
        chk("2 ทั้งสองข้อมีข้อความ → 'ตอบข้อที่ขาด #1, #2'", cmd3.split("\n")[0] == "idea-scout update · ตอบข้อที่ขาด #1, #2", cmd3.split("\n")[0])
        js(page, "()=>ideaGapSheetClose()"); page.wait_for_timeout(200)
        chk("2 ปิด sheet → overlay ปิด", not js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')"))
        page.click("[data-idea-gap-ansel]"); page.wait_for_selector("[data-idea-gap-box]")
        v1 = js(page, "()=>[document.querySelector('[data-idea-gap-ta=\"1\"]').value, document.querySelector('[data-idea-gap-ta=\"2\"]').value]")
        chk("2 เปิด sheet ใหม่ → ข้อความที่พิมพ์ยังอยู่ (ข้อ 1 · ข้อ 2)", v1 == ["กลับมาพิมพ์ข้อ 1", "ข้อ 2 ด้วย"], json.dumps(v1, ensure_ascii=False))
        chk("7 (2) sheet ไม่ล้นแนวนอน · ไม่มี console error", over_modal(page) <= 1 and overflow(page) <= 0 and not ce and not pe, json.dumps([over_modal(page), overflow(page), ce, pe]))
        js(page, "()=>ideaGapSheetClose()")
        # ปุ่ม 📝 ตอบ รายแถว (ข้อ 3)
        page.click('[data-idea-gap-ans="3"]'); page.wait_for_selector("[data-idea-gap-box]")
        chk("2 ปุ่ม 📝 ตอบ รายแถว → sheet มีเฉพาะข้อนั้น (#3)", js(page, "()=>[...document.querySelectorAll('[data-idea-gap-box]')].map(e=>e.dataset.ideaGapBox)") == ["3"])
    finally: b.close()

    # ───── 3 · หาไม่ได้ ─────
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        chk = lambda n, ok, d="": check(f"{tag} {n}", ok, d)
        go_evd(page)
        before = copy.deepcopy(idea_of(page))
        page.click('[data-idea-gap-unans="1"]'); page.wait_for_selector("[data-idea-gap-reason]")
        sv = lambda: js(page, "()=>document.getElementById('ideaGapUnSave').disabled")
        chk("3 ไม่มีเหตุผล → บันทึกไม่ได้", sv() is True)
        page.fill("[data-idea-gap-reason]", "บริษัทไม่เปิดเผยแผนกำลังผลิต"); page.wait_for_timeout(100)
        chk("3 มีเหตุผลแต่ไม่มีใช้แทน + ไม่ติ๊ก → บันทึกไม่ได้ · มีข้อความบอก", sv() is True and (txt_of(page, "[data-idea-gap-unwhy]") or "") != "")
        js(page, "()=>ideaGapUnSave()"); page.wait_for_timeout(300)
        chk("3 บังคับเรียก ideaGapUnSave() ตรง ๆ → ไม่เขียน (user.gaps ว่าง)", not user_of(page).get("gaps"))
        shot_modal(page, f"id3b-unanswerable-{sfx}.png")
        page.fill("[data-idea-gap-proxy]", "ใช้แผน capex ของ SK hynix แทน"); page.wait_for_timeout(100)
        chk("3 เหตุผล + ใช้แทน → บันทึกได้", sv() is False)
        page.click("#ideaGapUnSave"); page.wait_for_timeout(500)
        g1 = (user_of(page).get("gaps") or {}).get("1")
        chk("3 user.gaps['1'] = {status unanswerable · reason · proxy · accept_risk false · at 2026-10-05}", g1 and g1["status"] == "unanswerable" and g1["reason"] == "บริษัทไม่เปิดเผยแผนกำลังผลิต" and g1["proxy"] == "ใช้แผน capex ของ SK hynix แทน" and g1["accept_risk"] is False and g1["at"] == "2026-10-05", json.dumps(g1, ensure_ascii=False))
        chk("3 idea ไม่ถูกแก้ (gaps ใน doc.idea เหมือนเดิมทุกค่า)", idea_of(page) == before, "")
        R = {r["id"]: r for r in rows(page)}
        chk("3 ตารางแสดงข้อ 1 = หาไม่ได้ + เหตุผล/ใช้แทน + ปุ่ม 'เปิดใหม่' (ไม่มีติ๊ก/ตอบ)", R["1"]["st"] == "unanswerable" and R["1"]["reopen"] and not R["1"]["tick"] and not R["1"]["ans"] and "หาไม่ได้: บริษัทไม่เปิดเผยแผนกำลังผลิต · ใช้แทน: ใช้แผน capex ของ SK hynix แทน" in R["1"]["txt"] and "ผู้ใช้" in R["1"]["txt"], json.dumps(R["1"], ensure_ascii=False)[:400])
        # ติ๊กยอมรับความเสี่ยง (ไม่มี proxy)
        page.click('[data-idea-gap-unans="2"]'); page.wait_for_selector("[data-idea-gap-reason]")
        page.fill("[data-idea-gap-reason]", "ไม่มีข้อมูลแยก Industry"); page.check("[data-idea-gap-accept]"); page.wait_for_timeout(100)
        chk("3 เหตุผล + ติ๊กยอมรับความเสี่ยง (ไม่มีใช้แทน) → บันทึกได้", sv() is False)
        page.click("#ideaGapUnSave"); page.wait_for_timeout(500)
        g2 = (user_of(page).get("gaps") or {}).get("2")
        chk("3 user.gaps['2'] accept_risk true · proxy ว่าง · ข้อความ 'ใช้แทน: ยอมรับความเสี่ยง'", g2 and g2["accept_risk"] is True and g2["proxy"] == "" and "ใช้แทน: ยอมรับความเสี่ยง" in {r["id"]: r for r in rows(page)}["2"]["txt"], json.dumps(g2, ensure_ascii=False))
        # เปิดใหม่ข้อ 2 → ยกเลิกก่อน แล้วยืนยัน
        page.click('[data-idea-gap-reopen="2"]'); page.wait_for_selector("[data-idea-gap-reopenmsg]")
        page.click("[data-idea-gap-reopencancel]"); page.wait_for_timeout(300)
        chk("3 เปิดใหม่ → ยกเลิก → ยังหาไม่ได้ (user.gaps['2'] อยู่)", "2" in (user_of(page).get("gaps") or {}))
        page.click('[data-idea-gap-reopen="2"]'); page.wait_for_selector("[data-idea-gap-reopenok]"); page.click("[data-idea-gap-reopenok]"); page.wait_for_timeout(500)
        R = {r["id"]: r for r in rows(page)}
        chk("3 เปิดใหม่ → ยืนยัน → ลบ user.gaps['2'] · ข้อ 2 กลับเป็น open · ข้อ 1 ยังปิดอยู่", "2" not in (user_of(page).get("gaps") or {}) and "1" in (user_of(page).get("gaps") or {}) and R["2"]["st"] == "open" and R["2"]["ans"], json.dumps([user_of(page).get("gaps"), R["2"]["st"]], ensure_ascii=False))
        # ข้อที่ idea ปิดแล้ว (AI) ไม่มีปุ่มเปิดใหม่ — ทำใน 6
        chk("7 (3) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()

    # ───── 4 · พร้อมส่งต่อ ─────
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        chk = lambda n, ok, d="": check(f"{tag} {n}", ok, d)
        go_evd(page)
        r0 = ready(page)
        chk("4 ก่อนปิด: เหลือเงื่อนไขเดียวที่ไม่ผ่าน = ข้อ 'ไม่มีข้อที่ขาดระดับ ต้องรู้ ที่ยังเปิดอยู่'", r0["ok"] is False and len(r0["missing"]) == 1 and "ต้องรู้" in r0["missing"][0], json.dumps(r0, ensure_ascii=False))
        for gid in ("1", "2"):
            page.click(f'[data-idea-gap-unans="{gid}"]'); page.wait_for_selector("[data-idea-gap-reason]")
            page.fill("[data-idea-gap-reason]", f"เหตุผลข้อ {gid}"); page.check("[data-idea-gap-accept]"); page.click("#ideaGapUnSave"); page.wait_for_timeout(400)
        chk("4 ปิดข้อ 1 + 2 (must ทั้งคู่ · ข้อ 3 ติดตามยังเปิด) → ideaReady ผ่านครบ", ready(page)["ok"] is True, json.dumps(ready(page), ensure_ascii=False))
        js(page, "(id)=>ideaSetStatus(id,'ready')", IID); page.wait_for_timeout(400)
        chk("4 ตั้ง 'พร้อมส่งต่อ' ได้ → user.status = ready", user_of(page).get("status") == "ready", json.dumps(user_of(page).get("status")))
        js(page, "(id)=>ideaSetStatus(id,'need_evidence')", IID); page.wait_for_timeout(300)
        page.click('[data-idea-gap-reopen="2"]'); page.wait_for_selector("[data-idea-gap-reopenok]"); page.click("[data-idea-gap-reopenok]"); page.wait_for_timeout(500)
        r1 = ready(page)
        js(page, "(id)=>ideaSetStatus(id,'ready')", IID); page.wait_for_timeout(300)
        chk("4 เปิดใหม่ข้อ 2 → ideaReady ไม่ผ่าน (มีเหตุผล 'ต้องรู้') · ตั้ง พร้อมส่งต่อ ไม่ได้ (เรียกตรงก็ไม่ผ่าน)", r1["ok"] is False and any("ต้องรู้" in m for m in r1["missing"]) and user_of(page).get("status") == "need_evidence", json.dumps([r1["missing"], user_of(page).get("status")], ensure_ascii=False))
        chk("7 (4) ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally: b.close()

    # ───── 5 · Export ─────
    b, c, page, ce, pe, dl = launch(pw, w, h)
    try:
        chk = lambda n, ok, d="": check(f"{tag} {n}", ok, d)
        go_evd(page)
        page.click('[data-idea-gap-unans="1"]'); page.wait_for_selector("[data-idea-gap-reason]")
        page.fill("[data-idea-gap-reason]", "บริษัทไม่เปิดเผย"); page.fill("[data-idea-gap-proxy]", "ใช้ SK hynix แทน"); page.click("#ideaGapUnSave"); page.wait_for_timeout(500)
        o = js(page, "(id)=>ideaExportObj(ideaList.find(x=>x.id===id))", IID)
        g = {x["id"]: x for x in o["gaps"]}
        chk("5 Export: gap 1 = unanswerable · answer ขึ้นต้น 'หาไม่ได้:' · answer_src 'ผู้ใช้' · answered_at 2026-10-05", g[1]["status"] == "unanswerable" and g[1]["answer"] == "หาไม่ได้: บริษัทไม่เปิดเผย · ใช้แทน: ใช้ SK hynix แทน" and g[1]["answer_src"] == "ผู้ใช้" and g[1]["answered_at"] == "2026-10-05", json.dumps(g[1], ensure_ascii=False))
        chk("5 Export: ข้อที่ไม่ได้ปิดเอง (2, 3, 4) ยัง open ว่างเหมือนเดิม", all(g[i]["status"] == "open" and g[i]["answer"] == "" for i in (2, 3, 4)), json.dumps([g[i]["status"] for i in (2, 3, 4)]))
        chk("5 doc.idea ใน Firestore ไม่ถูกแก้โดย Export", idea_of(page)["gaps"][1]["status"] == "open")
    finally: b.close()

    # ───── 6 · Import ผล update ─────
    ai = idea()
    user0 = {"gaps": {"1": {"status": "unanswerable", "reason": "เหตุผลเดิมของผู้ใช้", "proxy": "", "accept_risk": True, "at": "2026-10-04"}}, "status": "need_evidence"}
    new = copy.deepcopy(ai)
    new["mode"] = "update"
    gg = {x["id"]: x for x in new["gaps"]}
    gg[1].update(status="answered", answer="Micron คาดเพิ่ม capex FY27 $20B — จุดที่ราคาเริ่มลงเร็วสุดปลายปี 2027", answer_src="Micron IR deck FY26 Q4 สไลด์ 12", answered_at="2026-10-05")
    gg[2].update(status="unanswerable", answer="หาไม่ได้: ไม่มีข้อมูลแยกรายส่วนที่เชื่อถือได้ · ใช้แทน: ผลตอบแทน SOX รายเดือน", answer_src="ผู้ใช้", answered_at="2026-10-05")
    new["evidence"] = new["evidence"] + [{"point": "Micron คาดเพิ่ม capex FY27", "found": "ผู้ใช้ส่ง IR deck — capex FY27 $20B", "src": "ผู้ใช้ส่งมา · Micron IR deck", "date": "2026-10-05", "tag": "U", "dir": "support"}]
    new["log"] = list(new.get("log", [])) + [{"date": "2026-10-05", "new": "ตอบข้อที่ขาด #1 (capex FY27)", "changed": "", "decision": ""}]
    b, c, page, ce, pe, dl = launch(pw, w, h, user=user0)
    try:
        chk = lambda n, ok, d="": check(f"{tag} {n}", ok, d)
        go_evd(page)
        R0 = {r["id"]: r for r in rows(page)}
        chk("6 ก่อน Import: ข้อ 1 แสดง หาไม่ได้ (ผู้ใช้) จาก user.gaps", R0["1"]["st"] == "unanswerable" and R0["1"]["reopen"], json.dumps(R0["1"], ensure_ascii=False)[:200])
        page.evaluate("([k,v])=>localStorage.setItem(k, v)", [LSK, json.dumps({f"{IID}|1": "ร่างเก่าของข้อ 1", f"{IID}|3": "ร่างข้อ 3 ที่ยังเปิด"}, ensure_ascii=False)])
        err, prev = P44.import_text(page, json.dumps(new, ensure_ascii=False), save=False)
        chk("6 ตัวอย่างก่อนบันทึก: 'ข้อที่ขาดที่ปิด: #1 ตอบแล้ว · #2 หาไม่ได้' · 'ข้อที่ยังเปิด: 2 ข้อ' (ข้อ 3 + ข้อ 4)", err == "" and "ข้อที่ขาดที่ปิด: #1 ตอบแล้ว · #2 หาไม่ได้" in prev and "ข้อที่ยังเปิด: 2 ข้อ" in prev, json.dumps([err, prev], ensure_ascii=False)[:500])
        page.click("[data-idea-save]"); page.wait_for_timeout(600)
        d = P44.idb(page, IID)
        chk("6 บันทึกแล้ว: idea.gaps ตามผล AI · user.gaps['1'] เดิมยังอยู่ใน doc (ไม่ลบ)", {x["id"]: x["status"] for x in d["idea"]["gaps"]}[1] == "answered" and (d["user"].get("gaps") or {}).get("1", {}).get("reason") == "เหตุผลเดิมของผู้ใช้", json.dumps(d["user"], ensure_ascii=False)[:300])
        go_evd(page)
        R = {r["id"]: r for r in rows(page)}
        chk("6 ตารางใช้ผล AI: ข้อ 1 ตอบแล้ว + คำตอบ + 'แหล่ง: Micron IR deck…' + วันที่ · ไม่มีปุ่ม (ไม่ใช่ของผู้ใช้ → ไม่มีเปิดใหม่) · ไม่แสดงเหตุผลเดิมของผู้ใช้", R["1"]["st"] == "answered" and "Micron คาดเพิ่ม capex FY27" in R["1"]["txt"] and "แหล่ง: Micron IR deck FY26 Q4 สไลด์ 12" in R["1"]["txt"] and not R["1"]["reopen"] and not R["1"]["ans"] and "เหตุผลเดิมของผู้ใช้" not in R["1"]["txt"], json.dumps(R["1"], ensure_ascii=False)[:500])
        chk("6 ข้อ 2 = หาไม่ได้ (จาก AI) · แสดงเหตุผล + ใช้แทน · ไม่มีปุ่มเปิดใหม่", R["2"]["st"] == "unanswerable" and "ใช้แทน: ผลตอบแทน SOX รายเดือน" in R["2"]["txt"] and not R["2"]["reopen"], json.dumps(R["2"], ensure_ascii=False)[:300])
        dr = drafts(page) or {}
        chk("6 ร่าง localStorage: ข้อ 1 (ไม่ใช่ open แล้ว) ถูกล้าง · ข้อ 3 (ยัง open) ยังอยู่", f"{IID}|1" not in dr and dr.get(f"{IID}|3") == "ร่างข้อ 3 ที่ยังเปิด", json.dumps(dr, ensure_ascii=False))
        chk("6 ป้าย U ในตารางหลักฐานแสดง '(ผู้ใช้)' · มีคำอธิบายป้าย", page.locator("[data-tag-u]").count() == 1 and "(ผู้ใช้)" in (txt_of(page, "[data-tag-u]") or "") and page.locator("[data-idea-taglegend]").count() == 1, str(page.locator("[data-tag-u]").count()))
        snap = copy.deepcopy(P44.idb(page, IID))
        err2, prev2 = P44.import_text(page, json.dumps(new, ensure_ascii=False))
        after = P44.idb(page, IID)
        chk("6 Import ซ้ำ → idea / user / log ไม่เปลี่ยน", err2 == "" and after["idea"] == snap["idea"] and after["user"] == snap["user"] and after["idea_log"] == snap["idea_log"], json.dumps(err2))
        chk("7 (6) ไม่ล้นแนวนอน · ไม่มี console error", overflow(page) <= 0 and not ce and not pe, json.dumps([overflow(page), ce, pe]))
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 49 / ID3b) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
