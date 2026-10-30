#!/usr/bin/env python3
"""ID1 — แท็บ Ideas (อ่านอย่างเดียว + Import) · users/{uid}/ideas · เทส 44
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-03 13:03 ไทย (P41.CLK) · fixture tests/fixtures/idea_semis.json (scan จริง · ไม่มีบริษัท → เทสต่อบริษัท KLAC/AMAT/LRCX/NORS เข้าไปเอง)
ภาพ tests/screenshots/id1-{list,summary,valuechain,companies,import-diff}-{1440,390}.png
รัน: python3 run_tests_phase44.py"""
import copy, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase40 as P40
import run_tests_phase41 as P41

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = P40.SHOTS
ENGINE = P40.ENGINE
js, check, shot, txt_of, cnt = P40.js, P40.check, P40.shot, P40.txt_of, P40.cnt
results = P40.results
CLK = P41.CLK
SEMIS = json.load(open(os.path.join(HERE, "fixtures", "idea_semis.json"), encoding="utf-8"))
SEG = "อุปกรณ์ผลิตชิป"
BAD_TXT = ["undefined", "null", "[object", "<span", "<b>", "&amp;", "&lt;", "&gt;", "&#39;", "**", "###", "[["]


def cand(sym, name, rank, state="wait", src="Applied Materials 10-K FY25 — รายได้ส่วนใหญ่มาจากเครื่องผลิตชิป", seg=SEG, **kw):
    c = {"sym": sym, "market": "US", "name": name, "from": "ai", "segments": [seg], "product": "เครื่องผลิตชิป", "mechanism": "ออเดอร์ตามแผนลงทุนของโรงงาน", "exposure": "ส่วนใหญ่ของรายได้",
         "relevance_src": src, "why_this": "เกี่ยวกับธีมตรง", "fail_even_if_right": "ถูกจำกัดการส่งออก", "questions": ["สัดส่วนรายได้จากหน่วยความจำ"], "rank": rank, "state": state, "state_why": ""}
    c.update(kw); return c


def semis(**mods):
    d = copy.deepcopy(SEMIS)
    d["candidates"] = [cand("KLAC", "KLA", 1, "study"), cand("AMAT", "Applied Materials", 2, "wait"), cand("LRCX", "Lam Research", 3, "wait"), cand("NORS", "No Source Co", 4, "wait", src="")]
    d.update(mods); return d


def ready_idea(**mods):
    d = semis(id="ready-idea", name="ไอเดียที่ผ่านครบ 4 ข้อ", date="2026-10-02")
    d["gaps"] = [dict(g, status="answered", answer="ตอบแล้ว") if g.get("priority") == "must" else g for g in d["gaps"]]
    d.update(mods); return d


def third(**mods):
    d = semis(id="third-idea", name="ไอเดียที่สาม", date="2026-09-20", status="exploring")
    d["kill"] = [dict(k, level="ok") for k in d["kill"]]
    d.update(mods); return d


def seed_idea(page, idea, user=None, log=None):
    doc = {"idea": {k: v for k, v in idea.items() if k != "log"}, "idea_log": log if log is not None else idea.get("log", []), "user": user or {}}
    page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "ideas", idea["id"]], doc])


def launcher(pw, w, h, ideas=(), deny=False):
    def ex(pg):
        if deny: pg.evaluate("()=>window.firebase.__mockDb.__denyPath(['users','testuid','ideas'])")
        for it in ideas: seed_idea(pg, it[0] if isinstance(it, tuple) else it, it[1] if isinstance(it, tuple) else None)
    return P40.launch(pw, w, h, ex, iso=CLK)


def go_ideas(page, sel=None):
    js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250)
    js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(250)
    if sel: js(page, "(s)=>ideaOpen(s)", sel); page.wait_for_timeout(250)


def idb(page, iid="semis-ai-memory-2026"):
    return page.evaluate("(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas',i])", iid)


def view(page): return js(page, "()=>wlView")
def tabk(page, k):
    page.click(f'[data-idea-tab="{k}"]'); page.wait_for_timeout(150)


def body_txt(page): return js(page, "()=>{ const e = document.querySelector('.wlDBody'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : ''; }")
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


def import_text(page, text, save=True):
    js(page, "()=>{ if(wlMobOpen && wlNarrow()) wlBack(); }"); page.wait_for_timeout(150)   # มือถือ: ปุ่ม Import อยู่ที่หัวรายการ
    page.click("[data-idea-import-top]"); page.wait_for_selector("#ideaJson", state="visible")
    page.fill("#ideaJson", text); page.click("[data-idea-check]"); page.wait_for_timeout(150)
    err = txt_of(page, "#ideaErrBox") or ""; prev = txt_of(page, "#ideaPrev") or ""
    if save and not err and page.locator("[data-idea-save]").is_visible():
        page.click("[data-idea-save]"); page.wait_for_timeout(500)
    return err, prev


def reload_keep(page):
    page.wait_for_timeout(600)
    dump = page.evaluate("() => window.firebase.__mockDb.__dump()")
    page.reload(wait_until="load"); page.wait_for_timeout(150)
    page.evaluate("""(dump)=>{ window.__MOCK_UID='testuid'; Object.keys(dump).forEach(k=>window.firebase.__mockDb.__seedDoc(k.split('/'), dump[k])); }""", dump)
    page.fill("#authEmail", "test@example.com"); page.fill("#authPass", "password123"); page.click("#authSubmit")
    page.wait_for_selector("#mainWrap", state="visible", timeout=8000); page.wait_for_timeout(900)


def press(page, k):
    page.keyboard.press(k); page.wait_for_timeout(150)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); wide = w > 900

    # ───── 1 · Import + 5 แท็บ + Value chain ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h)
    try:
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250)
        pills = js(page, "()=>[...document.querySelectorAll('.wlPills [data-wl-view]')].map(e=>e.dataset.wlView)")
        check(f"{tag} 2 pills ลำดับ Ideas · Candidates · Watchlist (TD4a เดิม: Watchlist · Ideas · Candidates)", pills == ["idea", "cand", "wl"], json.dumps(pills))
        js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(250)
        check(f"{tag} 4 ว่าง → 'ยังไม่มีไอเดีย — รัน skill idea-scout แล้ว 📥 Import'", "ยังไม่มีไอเดีย — รัน skill idea-scout แล้ว 📥 Import" in (txt_of(page, "[data-idea-empty]") or ""))
        err, prev = import_text(page, "ข้อความนำ\n```json\n" + json.dumps(semis(), ensure_ascii=False, indent=1) + "\n```\nจบ")
        check(f"{tag} 1 Import (มี ```json + ข้อความหน้า/หลัง) → ไม่มี error · diff มี 'สร้างไอเดียใหม่'", err == "" and "สร้างไอเดียใหม่" in prev, err + prev)
        d = idb(page) or {}
        check(f"{tag} 1 doc ideas/{{id}}: idea (ไม่มี log) · idea_log 1 บรรทัด · user ว่าง", d and "log" not in d["idea"] and len(d["idea_log"]) == 1 and d["user"] == {} and d["idea"]["schema"] == "idea@1", json.dumps(list((d or {}).keys())))
        rows = js(page, "()=>[...document.querySelectorAll('[data-idea]')].map(e=>({id:e.dataset.idea, st:e.querySelector('[data-idea-st]').innerText, dot:e.querySelector('[data-idea-dot]').dataset.ideaDot}))")
        check(f"{tag} 1 รายการมี 1 แถว สถานะ 'รอหลักฐาน' · จุดเหลือง (มีบริษัทศึกษา)", len(rows) == 1 and rows[0]["st"] == "รอหลักฐาน" and rows[0]["dot"] == "y", json.dumps(rows, ensure_ascii=False))
        shot(page, f"id1-list-{sfx}.png")
        check(f"{tag} 1 หลัง Import เปิดการ์ดทันที · 5 แท็บ", js(page, "()=>ideaSel") == "semis-ai-memory-2026" and cnt(page, "[data-idea-tab]") == 5 and [e for e in js(page, "()=>[...document.querySelectorAll('[data-idea-tab]')].map(e=>e.innerText.replace(/[0-9]/g,'').trim())")] == ["สรุป", "กลไก", "หลักฐาน", "Value chain", "บริษัท"])
        if not wide: js(page, "()=>{ wlMobOpen = true; renderWatchlist(); }"); page.wait_for_timeout(200)
        bad = {}
        for k in ("sum", "mech", "evd", "vc", "co"):
            tabk(page, k); t = body_txt(page); bad[k] = [x for x in BAD_TXT if x in t]
        check(f"{tag} 1 ทั้ง 5 แท็บ: ไม่มี HTML หลุด / undefined / null / [[ ]]", all(not v for v in bad.values()), json.dumps(bad))
        tabk(page, "sum")
        shot(page, f"id1-summary-{sfx}.png")
        t = body_txt(page)
        check(f"{tag} 1 แท็บสรุป: ประโยคเดียว · พักเมื่อ · ลำดับศึกษา · ข้อสรุป · เงื่อนไข 4 ข้อ", "เมื่อ hyperscaler" in t and "พักเมื่อ" in t and "ลำดับศึกษา KLAC" in t and "ข้อสรุป" in t and cnt(page, "[data-idea-gate] div") == 4, t[:300])
        hot = txt_of(page, "[data-idea-hotn]")
        nkill = len([k for k in SEMIS["kill"] if k.get("level") != "ok"])
        check(f"{tag} 1 ตัวเลขส้มบนแท็บหลักฐาน = จำนวน kill ที่ไม่ใช่ ok ({nkill})", (hot is None and nkill == 0) or hot == str(nkill), str(hot))
        tabk(page, "vc")
        vc = js(page, "()=>{ const s=[...document.querySelectorAll('[data-idea-seg]')].find(x=>x.innerText.includes('อุปกรณ์ผลิตชิป')); return s ? [...s.querySelectorAll('[data-idea-tk]')].map(e=>e.dataset.ideaTk) : null; }")
        check(f"{tag} 1 Value chain: กล่อง 'อุปกรณ์ผลิตชิป' มี KLAC/AMAT/LRCX", vc is not None and all(x in vc for x in ("KLAC", "AMAT", "LRCX")), json.dumps(vc))
        shot(page, f"id1-valuechain-{sfx}.png")
        tabk(page, "co")
        js(page, "()=>ideaCoToggle('KLAC')"); page.wait_for_timeout(150)
        check(f"{tag} 1 แท็บบริษัท: เรียงตาม rank · แตะเปิดรายละเอียด (ธุรกิจที่เกี่ยว · ทำไมตัวนี้ …)", js(page, "()=>[...document.querySelectorAll('[data-idea-co]')].map(e=>e.dataset.ideaCo)") == ["KLAC", "AMAT", "LRCX", "NORS"] and "ธุรกิจที่เกี่ยว" in (txt_of(page, "[data-idea-co-detail]") or ""))
        shot(page, f"id1-companies-{sfx}.png")
        check(f"{tag} 12 ไม่มี console error (Import + แท็บ)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 2–3 · คีย์บอร์ด ─────
    s1, s2, s3 = semis(), ready_idea(), third()
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [s1, s2, s3])
    try:
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250)
        seq = []
        for _ in range(3): press(page, "Tab"); seq.append(view(page))
        check(f"{tag} 2 Tab ×3 จาก Watchlist → Ideas → Candidates → Watchlist", seq == ["idea", "cand", "wl"], json.dumps(seq))
        seq = []
        for _ in range(3): press(page, "Shift+Tab"); seq.append(view(page))
        check(f"{tag} 2 Shift+Tab ย้อน: Candidates → Ideas → Watchlist", seq == ["cand", "idea", "wl"], json.dumps(seq))
        js(page, "()=>{ const i=document.createElement('input'); i.id='kbProbe'; document.body.appendChild(i); i.focus(); }")
        press(page, "Tab")
        check(f"{tag} 2 focus ในช่องพิมพ์ → Tab ไม่เปลี่ยนหน้า", view(page) == "wl", view(page))
        js(page, "()=>{ document.getElementById('kbProbe').remove(); document.activeElement.blur(); }")
        js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(200)
        js(page, "()=>ideaImportOpen()"); page.wait_for_selector("#ideaJson"); page.evaluate("()=>document.activeElement.blur()")
        press(page, "Tab")
        check(f"{tag} 2 มี sheet (Import) เปิด → Tab ไม่เปลี่ยนหน้า", view(page) == "idea", view(page))
        js(page, "()=>ideaSheetClose()")
        js(page, "()=>{ document.activeElement.blur(); coreSheet && coreSheet('x', '<h3>x</h3>'); }"); page.wait_for_timeout(100)
        press(page, "Tab")
        check(f"{tag} 2 มี core sheet เปิด → Tab ไม่เปลี่ยนหน้า", view(page) == "idea", view(page))
        js(page, "()=>coreSheetClose()")
        if wide:
            js(page, "()=>{ wlSetView('idea'); }"); page.wait_for_timeout(200)
            order = js(page, "()=>ideaRowsView().map(v=>v.id)")
            check(f"{tag} 3 เรียง แดง → เหลือง → วันที่ใหม่สุด (ready-idea 2 ต.ค. ก่อน semis? แดง/เหลืองก่อนเทา)", order[-1] == "third-idea" and set(order[:2]) == {"semis-ai-memory-2026", "ready-idea"}, json.dumps(order))
            js(page, "(i)=>ideaOpen(i)", order[0]); page.wait_for_timeout(200)
            press(page, "ArrowDown"); a = js(page, "()=>ideaSel"); press(page, "ArrowDown"); b2 = js(page, "()=>ideaSel"); press(page, "ArrowDown"); c3 = js(page, "()=>ideaSel")
            check(f"{tag} 3 ↓ เลือกไอเดียถัดไป · หยุดที่ท้ายรายการ", [a, b2] == order[1:3] and c3 == order[2], json.dumps([a, b2, c3]))
            press(page, "ArrowUp"); check(f"{tag} 3 ↑ ย้อนขึ้น", js(page, "()=>ideaSel") == order[1])
            js(page, "(i)=>{ ideaSel=i; ideaSubSave(i,'sum'); renderWatchlist(); }", order[0]); page.wait_for_timeout(150)
            ts = []
            for _ in range(6): press(page, "ArrowRight"); ts.append(js(page, "()=>ideaSubMem(ideaSel)"))
            check(f"{tag} 3 → เปลี่ยนแท็บ สรุป→กลไก→หลักฐาน→Value chain→บริษัท · หยุดที่ขอบ", ts == ["mech", "evd", "vc", "co", "co", "co"], json.dumps(ts))
            ts = []
            for _ in range(6): press(page, "ArrowLeft"); ts.append(js(page, "()=>ideaSubMem(ideaSel)"))
            check(f"{tag} 3 ← ย้อนแท็บ · หยุดที่ขอบซ้าย", ts == ["vc", "evd", "mech", "sum", "sum", "sum"], json.dumps(ts))
        fl = []
        for _ in range(5): press(page, "BracketRight"); fl.append(js(page, "()=>ideaFilter"))
        check(f"{tag} 3 ] วนตัวกรอง ทั้งหมด → รอหลักฐาน → พร้อมส่งต่อ → พัก → ทั้งหมด", fl == ["need_evidence", "ready", "parked", "all", "need_evidence"], json.dumps(fl))
        press(page, "BracketLeft"); check(f"{tag} 3 [ ย้อนตัวกรอง", js(page, "()=>ideaFilter") == "all")
        press(page, "KeyC"); v1 = view(page); press(page, "KeyV"); v2 = view(page)
        check(f"{tag} 3 C / V ยังทำงาน (Watchlist / Candidates)", v1 == "wl" and v2 == "cand", json.dumps([v1, v2]))
        check(f"{tag} 3 หน้า ? (ปุ่มลัด) มี Tab และ [ ] ของ Ideas", (lambda t: "Tab / Shift+Tab" in t and "[ ] ใน Ideas" in t)((js(page, "()=>{ openKbHelp(); const t=document.getElementById('kbHelpOverlay').innerText; document.getElementById('kbHelpOverlay').classList.remove('show'); return t; }"))))
        check(f"{tag} 12 ไม่มี console error (คีย์บอร์ด)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 4 · pick / rank / state คงอยู่ · Import ซ้ำ ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis()])
    try:
        go_ideas(page, "semis-ai-memory-2026")
        if not wide: pass
        tabk(page, "vc")
        page.check('[data-idea-pick="0"]'); page.wait_for_timeout(300)
        tabk(page, "co")
        js(page, "()=>ideaCoToggle('LRCX')"); page.wait_for_timeout(150)
        page.select_option('[data-idea-co-state="LRCX"]', "study"); page.wait_for_timeout(300)
        js(page, "()=>ideaCoMove('semis-ai-memory-2026','LRCX',-1)"); page.wait_for_timeout(300)
        u = (idb(page) or {}).get("user", {})
        check(f"{tag} 4 user: pick[อุปกรณ์ผลิตชิป]=true · cand.LRCX.state=study · rank สลับกับ AMAT", u.get("pick", {}).get(SEG) is True and u.get("cand", {}).get("LRCX", {}).get("state") == "study" and u["cand"]["LRCX"]["rank"] == 2 and u["cand"]["AMAT"]["rank"] == 3, json.dumps(u, ensure_ascii=False))
        reload_keep(page)
        go_ideas(page, "semis-ai-memory-2026")
        v = js(page, "()=>{ const x=ideaFind('semis-ai-memory-2026'); return {pick:x.segs.find(s=>s.name==='อุปกรณ์ผลิตชิป').pick, lr:x.cands.find(c=>c.sym==='LRCX'), order:x.cands.map(c=>c.sym)}; }")
        check(f"{tag} 4 reload → ค่ายังอยู่ (pick · LRCX ศึกษา · ลำดับ KLAC, LRCX, AMAT, NORS)", v["pick"] is True and v["lr"]["state"] == "study" and v["order"][:3] == ["KLAC", "LRCX", "AMAT"], json.dumps(v, ensure_ascii=False))
        tabk(page, "vc")
        check(f"{tag} 4 reload → checkbox ที่ติ๊กยังติ๊กอยู่", js(page, "()=>document.querySelector('[data-idea-pick=\"0\"]').checked"))
        before = idb(page)
        again = semis(); again["log"] = SEMIS["log"] + [{"date": "2026-10-05", "new": "อัปเดตรอบสอง", "changed": "-", "decision": "more_evidence"}]
        err, prev = import_text(page, json.dumps(again, ensure_ascii=False))
        shot(page, f"id1-import-diff-{sfx}.png") if False else None
        after = idb(page)
        check(f"{tag} 4 Import ไฟล์เดิมซ้ำ (log ใหม่ 1) → user ไม่ถูกแตะ · log 2 บรรทัด ไม่ซ้ำ", err == "" and after["user"] == before["user"] and len(after["idea_log"]) == 2, json.dumps([err, len(after["idea_log"])]))
        err2, _ = import_text(page, json.dumps(again, ensure_ascii=False))
        check(f"{tag} 4 Import ซ้ำอีกรอบ (log เดิม) → log ยัง 2 บรรทัด (ไม่ซ้ำ)", err2 == "" and len(idb(page)["idea_log"]) == 2)
        check(f"{tag} 12 ไม่มี console error (pick/rank)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # diff screenshot (Import ไอเดียที่มีอยู่แล้ว · เปลี่ยน mode/kill/gaps)
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis()])
    try:
        go_ideas(page, "semis-ai-memory-2026")
        nw = semis(mode="update"); nw["kill"] = [dict(k, level="watch") if i == 0 else k for i, k in enumerate(nw["kill"])]
        nw["gaps"] = [dict(g, status="answered", answer="x") if g["id"] == 1 else g for g in nw["gaps"]]
        err, prev = import_text(page, json.dumps(nw, ensure_ascii=False), save=False)
        check(f"{tag} 4 diff ไอเดียเดิม: mode เดิม→ใหม่ · บริษัท · kill ที่ level เปลี่ยน · ข้อที่ขาดที่ปิด · user ไม่ถูกแตะ", "scan → update" in prev and "จำนวนบริษัท" in prev and "ok → watch" in prev and "ข้อที่ขาดที่ปิด: #1 ตอบแล้ว" in prev and "ไม่ถูกแตะ" in prev, prev)
        shot(page, f"id1-import-diff-{sfx}.png")
    finally:
        b.close()

    # ───── 5–6 · พร้อมส่งต่อ · relevance_src ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis(), ready_idea()])
    try:
        go_ideas(page, "semis-ai-memory-2026")
        page.click("[data-idea-status]"); page.wait_for_selector("[data-idea-stmenu]")
        dis = js(page, "()=>document.querySelector('[data-idea-setst=ready]').disabled")
        why = txt_of(page, "[data-idea-setst=ready]") or ""
        check(f"{tag} 5 fixture semis (gap must เปิด) → 'พร้อมส่งต่อ' กดไม่ได้ + แสดงเหตุผลที่ขาด", dis is True and "ต้องรู้" in why, why)
        js(page, "()=>ideaSetStatus('semis-ai-memory-2026','ready')"); page.wait_for_timeout(300)
        check(f"{tag} 5 เรียกตรงก็ไม่ผ่าน (สถานะไม่เปลี่ยน)", (idb(page) or {}).get("user", {}).get("status") is None)
        js(page, "()=>ideaOpen('ready-idea')"); page.wait_for_timeout(250)
        page.click("[data-idea-status]"); page.wait_for_selector("[data-idea-stmenu]")
        check(f"{tag} 5 fixture ที่ผ่าน 4 ข้อ → กดได้", js(page, "()=>document.querySelector('[data-idea-setst=ready]').disabled") is False)
        page.click("[data-idea-setst=ready]"); page.wait_for_timeout(300)
        check(f"{tag} 5 ตั้ง 'พร้อมส่งต่อ' แล้ว → user.status=ready · ป้ายในแถว", (idb(page, "ready-idea") or {}).get("user", {}).get("status") == "ready" and "พร้อมส่งต่อ" in (txt_of(page, '[data-idea="ready-idea"] [data-idea-st]') or ""))
        # 6
        js(page, "()=>ideaSetStatus('ready-idea','exploring')"); js(page, "()=>ideaOpen('semis-ai-memory-2026')"); page.wait_for_timeout(250)
        tabk(page, "co"); js(page, "()=>ideaCoToggle('NORS')"); page.wait_for_timeout(150)
        opt_dis = js(page, "()=>document.querySelector('[data-idea-co-state=NORS] option[value=study]').disabled")
        js(page, "()=>ideaCoState('semis-ai-memory-2026','NORS','study')"); page.wait_for_timeout(300)
        st = (idb(page) or {}).get("user", {}).get("cand", {}).get("NORS")
        check(f"{tag} 6 บริษัทไม่มี relevance_src → ตัวเลือก 'ศึกษา' disabled · เรียกตรงก็ตั้งไม่ได้ · มีข้อความเหตุผล", opt_dis is True and st is None and "ตั้งเป็น \"ศึกษา\" ไม่ได้" in (txt_of(page, "[data-idea-co-detail]") or ""), json.dumps([opt_dis, st]))
        js(page, "()=>ideaCoState('semis-ai-memory-2026','NORS','park')"); page.wait_for_timeout(300)
        check(f"{tag} 6 ตั้ง 'พัก' ได้ตามปกติ", (idb(page) or {}).get("user", {}).get("cand", {}).get("NORS", {}).get("state") == "park")
        check(f"{tag} 12 ไม่มี console error (สถานะ)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 7 · Export ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [(semis(), {"status": "need_evidence", "pick": {SEG: True}, "cand": {"LRCX": {"rank": 1, "state": "study"}}})])
    try:
        go_ideas(page, "semis-ai-memory-2026")
        page.click("[data-idea-menu]"); page.wait_for_selector("[data-idea-export]")
        with page.expect_download() as dl:
            page.click("[data-idea-export]")
        fn = dl.value.suggested_filename
        page.wait_for_timeout(300)
        o = json.loads(js(page, "()=>window.__ideaLastExport"))
        seg = [s for s in o["chain"]["segments"] if s["name"] == SEG][0]
        lr = [c for c in o["candidates"] if c["sym"] == "LRCX"][0]
        check(f"{tag} 7 Export → parse ได้ · มี log · pick:true ตามที่ติ๊ก · rank/state ตามที่แก้", len(o["log"]) == 1 and seg["pick"] is True and lr["rank"] == 1 and lr["state"] == "study" and o["status"] == "need_evidence", json.dumps({"log": len(o["log"]), "pick": seg["pick"], "lr": [lr["rank"], lr["state"]]}))
        check(f"{tag} 7 ดาวน์โหลดไฟล์ {{id}}_idea_YYYYMMDD.json · ข้อความ 'คัดลอกแล้ว — แนบให้ idea-scout pick/update'", fn == "semis-ai-memory-2026_idea_20261003.json" and "คัดลอกแล้ว — แนบให้ idea-scout pick/update" in (txt_of(page, "[data-idea-msg]") or ""), fn + " | " + str(txt_of(page, "[data-idea-msg]")))
        check(f"{tag} 7 Export ไม่แก้ doc ใน Firestore (idea เดิมไม่มีธง pick)", all(not s.get("pick") for s in idb(page)["idea"]["chain"]["segments"]))
        check(f"{tag} 12 ไม่มี console error (Export)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 8 · Import ผิด ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h)
    try:
        go_ideas(page)
        good = semis()
        big = semis(); big["audit"] = "x" * 210000
        cases = [("schema ผิด", json.dumps(dict(good, schema="living-thesis@1")), 'schema ต้องเป็น "idea@1"'),
                 ("idea-match@1", json.dumps({"schema": "idea-match@1", "results": []}), "ไฟล์นี้เป็นผลจับคู่ — Import ที่ Candidates › 📋 จับคู่ list"),   # ID3a: ข้อความใหม่
                 (">200KB", json.dumps(big, ensure_ascii=False), "เกิน 200KB"),
                 ("ไม่มี id", json.dumps({k: v for k, v in good.items() if k != "id"}), "ไม่มี id"),
                 ("id มีตัวพิมพ์ใหญ่", json.dumps(dict(good, id="Bad_ID")), "id ต้องเป็น"),
                 ("ไม่มี name", json.dumps(dict(good, name="")), "ไม่มี name"),
                 ("ไม่มี chain.segments", json.dumps(dict(good, chain={})), "chain.segments"),
                 ("idea ไม่ใช่ object", json.dumps(dict(good, idea="x")), "idea ต้องเป็น object"),
                 ("JSON พัง", "{not json", "อ่าน JSON ไม่ได้"), ("ว่าง", "", "ยังไม่ได้วาง")]
        for nm, text, want in cases:
            page.click("[data-idea-import-top]"); page.wait_for_selector("#ideaJson", state="visible")
            page.fill("#ideaJson", text); page.click("[data-idea-check]"); page.wait_for_timeout(100)
            err = txt_of(page, "#ideaErrBox") or ""; sv = page.locator("[data-idea-save]").is_visible()
            check(f"{tag} 8 {nm} → error ภาษาไทย ไม่บันทึก", want in err and not sv, err)
            js(page, "()=>ideaSheetClose()")
        check(f"{tag} 8 ไม่มี doc ถูกสร้างจากไฟล์ผิด", not [k for k in js(page, "()=>Object.keys(window.firebase.__mockDb.__dump())") if "/ideas/" in k])
        check(f"{tag} 12 ไม่มี console error (Import ผิด)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 9 · ลบ ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis()])
    try:
        go_ideas(page, "semis-ai-memory-2026")
        page.click("[data-idea-menu]"); page.wait_for_selector("[data-idea-del]")
        check(f"{tag} 9 สถานะ 'รอหลักฐาน' → ลบ disabled + 'ตั้งเป็น พัก ก่อน'", js(page, "()=>document.querySelector('[data-idea-del]').disabled") is True and "ตั้งเป็น พัก ก่อน" in (txt_of(page, "[data-idea-del]") or ""))
        js(page, "()=>ideaDelOpen('semis-ai-memory-2026')"); page.wait_for_timeout(200)
        check(f"{tag} 9 เรียกลบตรง ๆ ตอนสถานะรอหลักฐาน → ไม่เปิดหน้าต่างยืนยัน · doc ยังอยู่", not js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')") and idb(page) is not None)
        js(page, "()=>ideaDelDo('semis-ai-memory-2026')"); page.wait_for_timeout(300)
        check(f"{tag} 9 เรียก ideaDelDo ตรง ๆ ตอนสถานะรอหลักฐาน → ไม่ลบ", idb(page) is not None)
        js(page, "()=>ideaSetStatus('semis-ai-memory-2026','parked')"); page.wait_for_timeout(300)
        js(page, "()=>{ ideaFilter='parked'; renderWatchlist(); ideaOpen('semis-ai-memory-2026'); }"); page.wait_for_timeout(250)
        page.click("[data-idea-menu]"); page.click("[data-idea-del]"); page.wait_for_selector("[data-idea-delok]")
        check(f"{tag} 9 สถานะพัก → ลบได้ · หน้าต่างยืนยันบอกชื่อไฟล์สำรอง", "semis-ai-memory-2026_idea_backup_20261003.json" in (txt_of(page, "[data-idea-delmsg]") or ""))
        with page.expect_download() as dl:
            page.click("[data-idea-delok]")
        page.wait_for_timeout(500)
        check(f"{tag} 9 ลบแล้ว: ดาวน์โหลด {{id}}_idea_backup_YYYYMMDD.json · doc หาย", dl.value.suggested_filename == "semis-ai-memory-2026_idea_backup_20261003.json" and idb(page) is None, dl.value.suggested_filename)
        check(f"{tag} 12 ไม่มี console error (ลบ)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 10 · XSS ─────
    X = "<script>window.__xss=1</script><img src=x onerror=window.__xss=2>"
    xi = semis(name="ไอเดีย " + X, **{"idea": dict(SEMIS["idea"], one_liner=[X, X, X, X], change=X)})
    xi["evidence"] = [dict(e, point=X) for e in xi["evidence"]]
    xi["candidates"][0]["name"] = X
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [xi])
    try:
        go_ideas(page, "semis-ai-memory-2026")
        t1 = body_txt(page)
        for k in ("evd", "co", "vc", "mech"):
            tabk(page, k)
        row = txt_of(page, "[data-idea-rows]") or ""
        n_script = js(page, "()=>document.querySelectorAll('#watchGroups script, #watchGroups img[src=x]').length")
        check(f"{tag} 10 <script> / <img onerror> ในข้อความ JSON → แสดงเป็นตัวอักษร · ไม่มี element · ไม่รันโค้ด", n_script == 0 and js(page, "()=>window.__xss") is None and "<script>" in t1 and "<script>" in row, json.dumps([n_script, t1[:120]]))
        check(f"{tag} 12 ไม่มี console error / dialog (XSS)", not ce and not pe and not dialogs, json.dumps([ce, pe, dialogs]))
    finally:
        b.close()

    # ───── 11 · 390px ─────
    if not wide:
        b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis()])
        try:
            js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250); js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(250)
            check(f"{tag} 11 มือถือ: เริ่มที่รายการ (ยังไม่เปิดการ์ด) · ไม่ล้นแนวนอน", not js(page, "()=>wlMobOpen") and overflow(page) <= 0, str(overflow(page)))
            page.click('[data-idea="semis-ai-memory-2026"]'); page.wait_for_timeout(300)
            check(f"{tag} 11 แตะแถว → เปิดการ์ด (มีปุ่ม ‹ Ideas)", js(page, "()=>wlMobOpen") and "‹ Ideas" in (txt_of(page, ".wlBackBtn") or ""))
            tabs = js(page, "()=>{ const t=document.querySelector('[data-idea-tabs]'); return {sw:t.scrollWidth, cw:t.clientWidth, ox:getComputedStyle(t).overflowX}; }")
            check(f"{tag} 11 แท็บเลื่อนแนวนอนได้ (overflow-x auto/scroll · กว้างเกินจอ)", tabs["ox"] in ("auto", "scroll") and tabs["sw"] > tabs["cw"], json.dumps(tabs))
            tabk(page, "vc")
            vc = js(page, "()=>{ const v=document.querySelector('[data-idea-vc]'); return {sw:v.scrollWidth, cw:v.clientWidth, ox:getComputedStyle(v).overflowX}; }")
            check(f"{tag} 11 Value chain เลื่อนในกล่อง (scrollWidth > clientWidth · overflow-x auto) · หน้าไม่ล้น", vc["ox"] in ("auto", "scroll") and vc["sw"] > vc["cw"] and overflow(page) <= 0, json.dumps([vc, overflow(page)]))
            page.keyboard.press("Escape"); page.wait_for_timeout(300)
            check(f"{tag} 11 Esc → กลับรายการ", not js(page, "()=>wlMobOpen") and js(page, "()=>{ const m=document.querySelector('.ideaM'); const d=m.querySelector('.wlDet'), l=m.querySelector('.wlList'); return !m.classList.contains('open') && getComputedStyle(d).display==='none' && getComputedStyle(l).display!=='none'; }"))
            check(f"{tag} 11 ไม่ล้นแนวนอนหลังกลับ", overflow(page) <= 0, str(overflow(page)))
            check(f"{tag} 12 ไม่มี console error (390)", not ce and not pe, json.dumps([ce, pe]))
        finally:
            b.close()

    # ───── 10 (ID1-fix) · ช่องวาง JSON ของ Import ไอเดีย ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis()])
    try:
        go_ideas(page)
        js(page, "()=>{ if(wlMobOpen && wlNarrow()) wlBack(); }"); page.wait_for_timeout(150)
        page.click("[data-idea-import-top]"); page.wait_for_selector("#ideaJson", state="visible")
        m = js(page, """()=>{ const t=document.getElementById('ideaJson'), m=document.getElementById('ltModal'), cs=getComputedStyle(m), inner=m.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
            return {w:t.getBoundingClientRect().width, inner, fs:parseFloat(getComputedStyle(t).fontSize), ff:getComputedStyle(t).fontFamily}; }""")
        page.locator("#ltModal").screenshot(path=os.path.join(SHOTS, f"id1fix-import-{sfx}.png"))
        js(page, "()=>ideaSheetClose()")
        js(page, "()=>ltImportOpen()"); page.wait_for_selector("#ltJson", state="visible")
        wt = js(page, "()=>document.getElementById('ltJson').getBoundingClientRect().width")
        js(page, "()=>ltSheetClose()")
        check(f"{tag} 10 Import ไอเดีย: #ideaJson กว้าง ≥ 90% ของเนื้อหา #ltModal ({m['w']:.0f}/{m['inner']:.0f})", m["w"] >= 0.9 * m["inner"], json.dumps(m))
        check(f"{tag} 10 #ideaJson font-size ≥ 16px (iPhone ไม่ซูม)", m["fs"] >= 16, json.dumps(m))
        check(f"{tag} 10 ความกว้างเท่า #ltJson ของ Import Thesis (±2px · {m['w']:.1f} vs {wt:.1f})", abs(m["w"] - wt) <= 2, json.dumps([m["w"], wt]))
    finally:
        b.close()

    # ───── prices/ideas อ่านไม่ได้ ─────
    b, c, page, ce, pe, dialogs = launcher(pw, w, h, [semis()], deny=True)
    try:
        go_ideas(page)
        t = txt_of(page, ".wlStat") or ""
        check(f"{tag} 1 อ่าน ideas ไม่ได้ (rules) → ข้อความ 'ตรวจ Firestore Rules ของ users/{{uid}}/ideas' · แอปไม่พัง", "ตรวจ Firestore Rules ของ users/{uid}/ideas" in t, t)
    finally:
        b.close()


def static_tests():
    root = os.path.join(HERE, "..")
    _h = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    check("[static] 11 มีกฎ @media (hover:none) ซ่อน .ideaFil .kbdhint", any("hover:none" in ln and ".kbdhint" in ln and "display:none" in ln for ln in _h.splitlines()))
    check("[static] สำรอง index.backup-pre-ID1.html + tests/_bk_id1/ + fixtures/idea_semis.json อยู่", os.path.exists(os.path.join(root, "index.backup-pre-ID1.html")) and os.path.isdir(os.path.join(HERE, "_bk_id1")) and os.path.exists(os.path.join(HERE, "fixtures", "idea_semis.json")))
    html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    check("[static] ไม่มีการอ่าน/เขียน field user ผ่าน innerHTML ดิบ · ข้อความผ่าน ltInl/escHtml (ไม่มี innerHTML = v.I.…)", "innerHTML = v.I" not in html and "ideaTxt = s => ltInl(" in html)
    check("[static] state หน้าจอ (ideaSel/ideaTab/ideaFilter) ไม่ถูกเขียนลง Firestore (ไม่อยู่ใน patch ของ ideaUserPatch)", "ideaUserPatch(id, {ideaSel" not in html and "ideaFilter:" not in html.split("function ideaUserPatch")[1].split("function ideaSetStatus")[0])


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 44 / ID1) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
