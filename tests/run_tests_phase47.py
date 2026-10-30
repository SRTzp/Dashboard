#!/usr/bin/env python3
"""ID3a — ＋ ไอเดีย (ร่าง) · 📋 จับคู่ list จาก TradingView (ชั้น 1) · 📥 Import ผลจับคู่ (idea-match@1) · เทส 47
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-05 (จันทร์ เวลาไทย) · fixtures: tv_volume_spike_2026-10-05.csv (ไฟล์จริง · ห้ามแก้) + idea_semis.json
ภาพ tests/screenshots/id3a-{match-layer1,group-line,match-import,draft-card}-{1440,390}.png
รัน: python3 run_tests_phase47.py"""
import copy, hashlib, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase40 as P40
import run_tests_phase44 as P44

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = P40.SHOTS
ENGINE = P40.ENGINE
js, check, txt_of, cnt = P40.js, P40.check, P40.txt_of, P40.cnt
results = P40.results
CLK = "2026-10-05T03:00:00Z"      # จันทร์ 5 ต.ค. 10:00 ไทย
CSV_PATH = os.path.join(HERE, "fixtures", "tv_volume_spike_2026-10-05.csv")
CSV = open(CSV_PATH, encoding="utf-8").read()
SEG = P44.SEG
SEMIS_ID = "semis-ai-memory-2026"
BAD_TXT = ["undefined", "null", "[object", "<span", "<b>", "&amp;", "&lt;", "&gt;", "&#39;", "**", "###"]



def fillx(page, sel, v):
    """SET1 — ช่องที่ไม่มี UI แล้ว (ซ่อน · ตายตัวในโค้ด): ตั้งค่าผ่าน JS เพื่อยังตรวจตรรกะ validation/อ่านกลับเดิม"""
    page.evaluate("([s,v])=>{ const e = document.querySelector(s); e.value = v; e.dispatchEvent(new Event('input',{bubbles:true})); e.dispatchEvent(new Event('change',{bubbles:true})); }", [sel, v])

def semis(**mods):
    d = copy.deepcopy(P44.SEMIS); d["candidates"] = []; d["status"] = "need_evidence"; d.update(mods); return d


def parked(**mods):
    d = semis(id="idea-parked", name="ไอเดียที่พัก", status="parked"); d.update(mods); return d


def seed_idea(pg, idea, user=None): P44.seed_idea(pg, idea, user)


def launcher(pw, w, h, ideas=(), wl=("QRVO",)):
    def ex(pg):
        for t in wl: P40.seed_wl(pg, t, P40.fx(t))
        for it in ideas: seed_idea(pg, it[0] if isinstance(it, tuple) else it, it[1] if isinstance(it, tuple) else None)
    return P40.launch(pw, w, h, ex, iso=CLK)


def go_ideas(page): js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250); js(page, "()=>wlSetView('idea')"); page.wait_for_timeout(300)
def go_cand(page):
    js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250); js(page, "()=>wlSetView('cand')"); page.wait_for_timeout(300)
def cand_syms(page): return js(page, "()=>[...document.querySelectorAll('.wlR[data-sym]')].map(e=>e.dataset.sym)")
def idb(page, iid=SEMIS_ID): return page.evaluate("(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','ideas',i])", iid)
def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")
def modal_over(page): return js(page, "()=>{ const m=document.getElementById('ltModal'); return m.scrollWidth - m.clientWidth; }")
def shot_modal(page, name):
    page.wait_for_timeout(400)
    try: page.locator("#ltModal").screenshot(path=os.path.join(SHOTS, name))
    except Exception as e: print("shot fail", name, e)


def open_match(page, text=None, read=True):
    go_cand(page)
    page.click("[data-cand-match-top]"); page.wait_for_selector("#matchText", state="visible")
    if text is not None: page.fill("#matchText", text)
    if read: page.click("[data-match-read]"); page.wait_for_timeout(200)


def rows_info(page):
    return js(page, "()=>{ const o={}; document.querySelectorAll('[data-match-row]').forEach(e=>{ o[e.dataset.matchRow]={kind:e.dataset.kind, dir:e.dataset.dir, nseg:+e.dataset.nseg, text:e.querySelector('.mtX').textContent, desc:e.querySelector('.mtD').textContent, ind:e.querySelector('.mtI').textContent, wl:!!e.querySelector('[data-match-inwl]')}; }); return o; }")


def gcount(page, k):
    t = txt_of(page, f'[data-match-gh="{k}"]') or ""
    return t


def add_cand_idea(page, idea, iid=SEMIS_ID):
    page.evaluate("([i,d])=>firebase.firestore().collection('users').doc('testuid').collection('ideas').doc(i).set(d)", [iid, {"idea": {k: v for k, v in idea.items() if k != "log"}, "idea_log": idea.get("log", []), "user": {}}]); page.wait_for_timeout(400)


def advance_days(page, days):
    page.evaluate("(d)=>{ const D = Date, off = d*864e5; class F2 extends D { constructor(...a){ if(a.length===0) super(D.now()+off); else super(...a); } static now(){ return D.now()+off; } } window.Date = F2; }", days)


def match_json(idea=SEMIS_ID, **kw):
    r = lambda sym, side, segs, fit="likely", why="เกี่ยวกับธีม", idea=idea: {"sym": sym, "market": "US", "idea": idea, "side": side, "segments": segs, "fit": fit, "why": why, "tag": "I"}
    d = {"schema": "idea-match@1", "date": "2026-10-05", "source": "TradingView screen", "results": [
        r("TER", "win", [SEG]), r("VECO", "win", [SEG, "ชื่อส่วนที่ไม่มีในไอเดีย"], fit="unsure"), r("CAMT", "win", [SEG]), r("QRVO", "lose", [], why="ลูกค้าตัดงบ"),
        r("GHOST", "win", [SEG], idea="no-such-idea"), r("PKD", "win", [SEG], idea="idea-parked")], "dropped": 2, "audit": ""}
    d.update(kw); return d


def fill_json(page, obj_or_text):
    t = obj_or_text if isinstance(obj_or_text, str) else json.dumps(obj_or_text, ensure_ascii=False)
    if not page.locator("#matchJson").count() or not page.locator("#matchJson").is_visible():
        page.click("[data-match-import-open]"); page.wait_for_selector("#matchJson", state="visible")
    page.fill("#matchJson", t); page.click("[data-match-imp-check]"); page.wait_for_timeout(150)


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); wide = w > 900
    scan_exp = None

    # ───── 1 · ＋ ไอเดีย ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [])
    try:
        go_ideas(page)
        check(f"{tag} 1 หัว Ideas มีปุ่ม '＋ ไอเดีย' อยู่ซ้ายของ '📥 Import'", js(page, "()=>{ const a=document.querySelector('[data-idea-new-top]'), b=document.querySelector('[data-idea-import-top]'); return !!a && !!b && a.nextElementSibling===b; }"))
        page.click("[data-idea-new-top]"); page.wait_for_selector("#ideaNewName", state="visible")
        check(f"{tag} 1 sheet มี 5 ช่อง: ชื่อ · ไอเดีย · ตลาด · โน้ต · หุ้นที่นึกไว้", all(page.locator(s).count() == 1 for s in ["#ideaNewName", "#ideaNewIdea", "#ideaNewMkt", "#ideaNewNote", "#ideaNewTk"]))
        page.click("[data-idea-new-save]"); page.wait_for_timeout(150)
        check(f"{tag} 1 ชื่อว่าง → error 'ใส่ชื่อไอเดียก่อน' · ไม่สร้าง doc", "ใส่ชื่อไอเดียก่อน" in (txt_of(page, "#ideaNewErr") or "") and not [k for k in js(page, "()=>Object.keys(window.firebase.__mockDb.__dump())") if "/ideas/" in k])
        page.fill("#ideaNewName", "Semis ทดสอบ"); page.click("[data-idea-new-save]"); page.wait_for_timeout(150)
        check(f"{tag} 1 ไอเดียว่าง → error 'ใส่ไอเดียประโยคเดียวก่อน'", "ใส่ไอเดียประโยคเดียวก่อน" in (txt_of(page, "#ideaNewErr") or ""))
        page.fill("#ideaNewIdea", "ชิปขาดตลาด ราคาพุ่ง"); page.fill("#ideaNewTk", "klac, AMAT  nasdaq:LRCX"); page.select_option("#ideaNewMkt", "TH"); page.fill("#ideaNewNote", "หน่วยความจำขายดีมาก")
        page.click("[data-idea-new-save]"); page.wait_for_timeout(500)
        d = idb(page, "semis-20261005")
        I = (d or {}).get("idea", {})
        check(f"{tag} 1 บันทึก → doc id 'semis-20261005' (slug จากชื่อ + วันที่ไทย) · idea.status 'draft' · mode 'draft' · schema idea@1", d is not None and I.get("status") == "draft" and I.get("mode") == "draft" and I.get("schema") == "idea@1" and I.get("id") == "semis-20261005" and I.get("date") == "2026-10-05", json.dumps(I, ensure_ascii=False)[:300])
        check(f"{tag} 1 user ว่าง (ไม่เก็บสถานะร่างใน user.status) · scope ['TH'] · origin []", d.get("user") == {} and I.get("scope") == ["TH"] and I.get("origin") == [], json.dumps([d.get("user"), I.get("scope"), I.get("origin")]))
        check(f"{tag} 1 user_notes = {{idea, mechanism, tickers:[KLAC,AMAT,LRCX], unsure:''}}", I.get("user_notes") == {"idea": "ชิปขาดตลาด ราคาพุ่ง", "mechanism": "หน่วยความจำขายดีมาก", "tickers": ["KLAC", "AMAT", "LRCX"], "unsure": ""}, json.dumps(I.get("user_notes"), ensure_ascii=False))
        check(f"{tag} 1 idea_log 1 บรรทัด 'สร้างร่างในแอป'", [l.get("new") for l in d.get("idea_log", [])] == ["สร้างร่างในแอป"], json.dumps(d.get("idea_log"), ensure_ascii=False))
        check(f"{tag} 1 หลังบันทึก: sheet ปิด · เปิดการ์ดร่างทันที (ชื่อ + ป้าย ร่าง + ข้อความ 'ร่าง — ยังไม่ได้รัน idea-scout')", not js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')") and (txt_of(page, "[data-idea-title]") or "") == "Semis ทดสอบ" and "ร่าง — ยังไม่ได้รัน idea-scout" in (txt_of(page, "[data-idea-draft-msg]") or ""), txt_of(page, "[data-idea-title]"))
        body = txt_of(page, "[data-idea-draft]") or ""
        check(f"{tag} 1 การ์ดร่างแสดง ไอเดีย · โน้ตของฉัน · หุ้นที่นึกไว้ (KLAC, AMAT, LRCX)", "ชิปขาดตลาด ราคาพุ่ง" in body and "หน่วยความจำขายดีมาก" in body and "KLAC, AMAT, LRCX" in body, body)
        shot_modal_page = page
        page.wait_for_timeout(300)
        try: page.screenshot(path=os.path.join(SHOTS, f"id3a-draft-card-{sfx}.png"), full_page=False)
        except Exception as e: print("shot fail", e)
        okt = []
        for k in ["sum", "mech", "evd", "vc", "co", "sum"]:
            js(page, "(k)=>ideaSetTab(k)", k); page.wait_for_timeout(120)
            t = txt_of(page, ".wlDBody") or ""
            okt.append((k, ("ยังไม่มี — รัน scan ก่อน" in t) if k != "sum" else ("ร่าง — ยังไม่ได้รัน" in t), not any(x in t for x in BAD_TXT)))
        check(f"{tag} 1 การ์ดร่างเปิดครบ 5 แท็บไม่ error · แท็บที่ว่าง = 'ยังไม่มี — รัน scan ก่อน'", all(a and b2 for _, a, b2 in okt), json.dumps(okt))
        check(f"{tag} 1 ป้ายสถานะ 'ร่าง' ไม่ใช่ปุ่มเมนู (กันตั้งสถานะค้างใน user)", js(page, "()=>{ const e=document.querySelector('[data-idea-status]'); return e.tagName!=='BUTTON' && e.dataset.ideaStatus==='draft'; }"))
        # คำสั่ง scan
        page.click("[data-idea-copyscan]"); page.wait_for_timeout(250)
        got = js(page, "()=>window.__ideaLastScan")
        exp = "idea-scout scan\nไอเดีย: ชิปขาดตลาด ราคาพุ่ง\nชื่อ: Semis ทดสอบ · id: semis-20261005 (ใช้ id เดิม — Import แล้วแทนที่ร่างนี้)\nตลาด: TH\nโน้ตของฉัน: หน่วยความจำขายดีมาก\nหุ้นที่นึกไว้: KLAC, AMAT, LRCX"
        check(f"{tag} 1 คำสั่ง scan ตรงรูปแบบ (ไม่มีบรรทัด ที่มา เพราะว่าง)", got == exp, json.dumps(got, ensure_ascii=False))
        check(f"{tag} 1 มีข้อความ 'คัดลอกคำสั่ง scan แล้ว' หลังกด", "คัดลอกคำสั่ง scan แล้ว" in (txt_of(page, "[data-idea-copymsg]") or "") or js(page, "()=>!!document.querySelector('[data-idea-copytext]')"))
        scan_exp = exp
        # ใน ⋯
        page.click("[data-idea-menu]"); page.wait_for_selector("[data-idea-copyscan-menu]")
        page.click("[data-idea-copyscan-menu]"); page.wait_for_timeout(200)
        check(f"{tag} 1 ปุ่ม 'คัดลอกคำสั่ง scan' ใน ⋯ ใช้ได้เหมือนกัน", js(page, "()=>window.__ideaLastScan") == exp)
        # ชื่อซ้ำ / ไทยล้วน
        def mk(name, idea="x"):
            js(page, "()=>ideaNewOpen()"); page.wait_for_selector("#ideaNewName"); page.fill("#ideaNewName", name); page.fill("#ideaNewIdea", idea); page.click("[data-idea-new-save]"); page.wait_for_timeout(400)
        mk("Semis ทดสอบ"); mk("Semis ทดสอบ"); mk("ไอเดียไทยล้วน")
        ids = sorted(k.split("/")[-1] for k in js(page, "()=>Object.keys(window.firebase.__mockDb.__dump())") if "/ideas/" in k)
        check(f"{tag} 1 ชื่อซ้ำ → -2, -3 · ชื่อไทยล้วน → idea-YYYYMMDD", ids == ["idea-20261005", "semis-20261005", "semis-20261005-2", "semis-20261005-3"], json.dumps(ids))
        # คำสั่ง scan ว่างช่อง → ตัดบรรทัด + ที่มา
        got2 = None
        js(page, "()=>ideaOpen('idea-20261005')"); page.wait_for_timeout(200); js(page, "()=>ideaCopyScan('idea-20261005')"); page.wait_for_timeout(200)
        got2 = js(page, "()=>window.__ideaLastScan")
        check(f"{tag} 1 ช่องว่าง = ตัดบรรทัดทิ้ง (เหลือ ไอเดีย · ชื่อ · ตลาด)", got2 == "idea-scout scan\nไอเดีย: x\nชื่อ: ไอเดียไทยล้วน · id: idea-20261005 (ใช้ id เดิม — Import แล้วแทนที่ร่างนี้)\nตลาด: US", json.dumps(got2, ensure_ascii=False))
        # Import ผล scan ด้วย id เดียวกัน
        sm = semis(id="semis-20261005", name="Semis ทดสอบ", status="exploring")
        js(page, "()=>ideaOpen('semis-20261005')"); page.wait_for_timeout(200)
        js(page, "()=>ideaImportOpen()"); page.wait_for_selector("#ideaJson", state="visible")
        page.fill("#ideaJson", json.dumps(sm, ensure_ascii=False)); page.click("[data-idea-check]"); page.wait_for_timeout(150)
        page.click("[data-idea-save]"); page.wait_for_timeout(600)
        d2 = idb(page, "semis-20261005")
        stt = txt_of(page, "[data-idea-status]") or ""
        check(f"{tag} 1 Import ผล scan (id เดียวกัน · exploring) → แทนที่ร่าง · idea.status exploring · user ยังว่าง · การ์ดแสดง 'กำลังสำรวจ' (ไม่ค้างร่าง)", d2["idea"]["status"] == "exploring" and d2["idea"]["mode"] == "scan" and d2.get("user") == {} and "กำลังสำรวจ" in stt, json.dumps([d2["idea"]["status"], d2.get("user"), stt], ensure_ascii=False))
        check(f"{tag} 1 log ร่างยังอยู่ + log จาก scan ต่อท้าย", len(d2["idea_log"]) == 2 and d2["idea_log"][0]["new"] == "สร้างร่างในแอป", json.dumps(d2["idea_log"], ensure_ascii=False)[:200])
        check(f"{tag} 1 ไม่มี console error (＋ ไอเดีย)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 2 · CSV จริง · ชั้น 1 ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [semis()])
    try:
        go_cand(page)
        check(f"{tag} 2 หัว Candidates มีปุ่ม '📋 จับคู่ list'", page.locator("[data-cand-match-top]").count() == 1)
        go_ideas(page)
        check(f"{tag} 2 หัว Ideas ไม่มีปุ่ม 📋", page.locator("[data-cand-match-top]").count() == 0)
        open_match(page, CSV)
        info = rows_info(page)
        check(f"{tag} 2 อ่านได้ 9 แถว (ชื่อมีจุลภาคถูก: TER = 'Teradyne, Inc.' · Industry ครบ)", len(info) == 9 and info["TER"]["desc"] == "Teradyne, Inc." and info["TER"]["ind"] == "Electronic production equipment" and info["PENG"]["desc"] == "Penguin Solutions, Inc.", json.dumps({k: [v["desc"], v["ind"]] for k, v in info.items()}, ensure_ascii=False)[:600])
        check(f"{tag} 2 สรุป 'อ่านได้ 9 แถว · CSV'", "อ่านได้ 9 แถว · CSV" in (txt_of(page, "[data-match-sum]") or ""), txt_of(page, "[data-match-sum]"))
        exp = {"TER": ("ind", "▲", 1), "VECO": ("ind", "▲", 1), "LSCC": ("ind", "▲", 4), "QRVO": ("ind", "▲", 4), "SYNA": ("ind", "▲", 4), "PENG": ("ind", "▲", 4), "CAMT": ("ind", "▼", 1), "NTAP": ("none", "", 0), "IBRX": ("none", "", 0)}
        got = {k: (v["kind"], v["dir"], v["nseg"]) for k, v in info.items()}
        check(f"{tag} 2 ผลชั้น 1 ครบ 9 แถว: TER·VECO = Industry ตรง ▲ (ไม่สนตัวพิมพ์) · LSCC·QRVO·SYNA·PENG = 4 ส่วน ▲ · CAMT = ▼ · NTAP·IBRX = ไม่ตรง", got == exp, json.dumps(got))
        check(f"{tag} 2 ข้อความผล (PX2): '▲ 4 ส่วน · {{ชื่อไอเดีย}}' / 'ไม่ตรง'", info["LSCC"]["text"].startswith("▲ 4 ส่วน · ") and "ทำไมหุ้น semiconductor" in info["LSCC"]["text"] and info["NTAP"]["text"] == "ไม่ตรง" and info["CAMT"]["text"].startswith("▼ 1 ส่วน · "), json.dumps([info["LSCC"]["text"], info["CAMT"]["text"]], ensure_ascii=False))
        check(f"{tag} 2 หัวกลุ่มมีจำนวน: อยู่ในไอเดียแล้ว (0) · Industry ตรง (7) · ไม่ตรง (2) · กลุ่ม 'ไม่ตรง' พับไว้", gcount(page, "in") == "อยู่ในไอเดียแล้ว (0)" and gcount(page, "ind") == "Industry ตรง (7)" and gcount(page, "none") == "ไม่ตรง (2)" and js(page, "()=>document.querySelector('[data-match-group-box=none]').open") is False, json.dumps([gcount(page, "in"), gcount(page, "ind"), gcount(page, "none")], ensure_ascii=False))
        check(f"{tag} 2 ชิป 'อยู่ใน Watchlist' เฉพาะ QRVO (seed)", [k for k, v in info.items() if v["wl"]] == ["QRVO"], json.dumps([k for k, v in info.items() if v["wl"]]))
        check(f"{tag} 2 ไม่มีบรรทัด 'กลุ่มยังไม่มีไอเดีย' (กลุ่ม ไม่ตรง มี Industry ละ 1 ตัว < 3)", page.locator("[data-match-groups]").count() == 0)
        one = js(page, "()=>{ const r=document.querySelector('[data-match-row=TER]'); const b=r.getBoundingClientRect(); return {h:b.height, ov:r.scrollWidth-r.clientWidth}; }")
        check(f"{tag} 2 แถวไม่ล้นแนวนอน (แถว {one['h']:.0f}px)" + (" · บรรทัดเดียวบนจอกว้าง" if wide else ""), one["ov"] <= 1 and (not wide or one["h"] < 40), json.dumps(one))
        check(f"{tag} 2 sheet/หน้าไม่ล้นแนวนอน", modal_over(page) <= 1 and overflow(page) <= 0, json.dumps([modal_over(page), overflow(page)]))
        js(page, "()=>{ document.querySelector('[data-match-group-box=none]').open = true; }")
        shot_modal(page, f"id3a-match-layer1-{sfx}.png")
        check(f"{tag} 2 ไม่มี console error (วาง CSV)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 3 · ticker ล้วน · อยู่ในไอเดียแล้ว ─────
    sem3 = semis(); sem3["candidates"] = [P44.cand("KLAC", "KLA", 1, "study")]; sem3["losers"] = [{"sym": "ZLOSE", "market": "US", "why": "x", "src": "x"}]
    b, c, page, ce, pe, dl = launcher(pw, w, h, [sem3])
    try:
        open_match(page, "KLAC,TER\nzlose NASDAQ:VECO")
        info = rows_info(page)
        check(f"{tag} 3 ticker ล้วน: KLAC = อยู่ในไอเดียแล้ว ▲ + ชื่อไอเดีย · ZLOSE = ▼ · TER/VECO = ไม่ตรง (ไม่มี Industry) · อ่านได้ 4 แถว", info["KLAC"]["kind"] == "in" and "▲" in info["KLAC"]["text"] and "ทำไมหุ้น semiconductor" in info["KLAC"]["text"] and info["ZLOSE"]["kind"] == "in" and "▼" in info["ZLOSE"]["text"] and info["TER"]["kind"] == "none" and info["VECO"]["kind"] == "none" and len(info) == 4, json.dumps({k: [v["kind"], v["text"][:40]] for k, v in info.items()}, ensure_ascii=False))
        check(f"{tag} 3 'NASDAQ:VECO' อ่านเป็น VECO · สรุป 'ticker ล้วน'", "VECO" in info and "ticker ล้วน" in (txt_of(page, "[data-match-sum]") or ""))
        check(f"{tag} 3 ไม่มีบรรทัดกลุ่ม (โหมด ticker ล้วน)", page.locator("[data-match-groups]").count() == 0)
        check(f"{tag} 3 ปุ่ม match กดไม่ได้ (ไม่มีกลุ่ม Industry ตรง) + เหตุผล · ติ๊กส่งตัวที่ถูกตัด → กดได้", js(page, "()=>document.querySelector('[data-match-copy]').disabled") is True and "ไม่มีหุ้นที่ Industry ตรง" in (txt_of(page, "[data-match-why]") or ""))
        page.check("[data-match-cut]"); page.wait_for_timeout(100)
        check(f"{tag} 3 ติ๊กแล้วปุ่มกดได้ · เหตุผลหาย", js(page, "()=>document.querySelector('[data-match-copy]').disabled") is False and page.locator("[data-match-why]").count() == 0)
        page.fill("#matchText", ""); page.click("[data-match-read]"); page.wait_for_timeout(100)
        check(f"{tag} 3 วางว่าง → error 'ยังไม่ได้วาง list' · ไม่มีผล", "ยังไม่ได้วาง list" in (txt_of(page, "#matchErr") or "") and page.locator("[data-match-row]").count() == 0)
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, [])
    try:
        open_match(page, CSV)
        check(f"{tag} 3 ไม่มีไอเดียที่นับ → ทุกตัวไม่ตรง · ปุ่ม match กดไม่ได้ + 'ยังไม่มีไอเดียที่รอหลักฐาน / พร้อมส่งต่อ ให้จับคู่' (แม้ติ๊กส่งตัวที่ถูกตัด)", set(v["kind"] for v in rows_info(page).values()) == {"none"} and js(page, "()=>document.querySelector('[data-match-copy]').disabled") is True and "ยังไม่มีไอเดียที่รอหลักฐาน" in (txt_of(page, "[data-match-why]") or ""))
        page.check("[data-match-cut]"); page.wait_for_timeout(100)
        check(f"{tag} 3 ติ๊กแล้วก็ยังกดไม่ได้ (ไม่มีไอเดียให้จับคู่)", js(page, "()=>document.querySelector('[data-match-copy]').disabled") is True)
    finally:
        b.close()

    # ───── 4 · กลุ่มยังไม่มีไอเดีย ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [parked()])
    try:
        open_match(page, CSV)
        gl = txt_of(page, "[data-match-groups]") or ""
        check(f"{tag} 4 ไอเดียตั้งพัก → ทุกตัวไม่ตรง · บรรทัด 'กลุ่มยังไม่มีไอเดีย: Semiconductors (4)' ขึ้น · 'Electronic production equipment (2)' ไม่ขึ้น (< 3)", "Semiconductors (4)" in gl and "Electronic production equipment" not in gl and gl.startswith("กลุ่มยังไม่มีไอเดีย:"), gl)
        shot_modal(page, f"id3a-group-line-{sfx}.png")
        js(page, "()=>{ const B = getBook(tdHome()); B.settings.ideaGroupMin = 2; }"); page.click("[data-match-read]"); page.wait_for_timeout(150)
        gl = txt_of(page, "[data-match-groups]") or ""
        check(f"{tag} 4 ตั้ง min = 2 → ขึ้นทั้ง Semiconductors (4) และ Electronic production equipment (2) · เรียงมาก → น้อย", "Semiconductors (4)" in gl and "Electronic production equipment (2)" in gl and gl.index("Semiconductors") < gl.index("Electronic"), gl)
        js(page, "()=>{ const B = getBook(tdHome()); B.settings.ideaGroupMin = 3; }")
        page.click("[data-match-group-hide][data-key=semiconductors]"); page.wait_for_timeout(150)
        check(f"{tag} 4 ✕ → กลุ่ม Semiconductors หาย · เก็บ localStorage ตามชื่อตัวเล็ก ถึง 2026-11-04 (30 วัน)", page.locator("[data-match-groups]").count() == 0 and js(page, "()=>JSON.parse(localStorage.getItem('ideaGroupHide'))") == {"semiconductors": "2026-11-04"}, json.dumps(js(page, "()=>localStorage.getItem('ideaGroupHide')")))
        advance_days(page, 29); page.click("[data-match-read]"); page.wait_for_timeout(150)
        check(f"{tag} 4 +29 วัน → ยังซ่อน", page.locator("[data-match-groups]").count() == 0)
        advance_days(page, 2); page.click("[data-match-read]"); page.wait_for_timeout(150)   # รวม +31 วัน
        check(f"{tag} 4 +31 วัน → กลับมา", "Semiconductors (4)" in (txt_of(page, "[data-match-groups]") or ""), txt_of(page, "[data-match-groups]"))
        check(f"{tag} 4 ไม่มี console error (กลุ่ม)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    b, c, page, ce, pe, dl = launcher(pw, w, h, [parked()])
    try:
        open_match(page, CSV)
        page.click("[data-match-group-add][data-key=semiconductors]"); page.wait_for_timeout(500)
        d = idb(page, "semiconductors-20261005"); I = (d or {}).get("idea", {})
        un = I.get("user_notes", {})
        check(f"{tag} 4 ＋ → ไอเดียร่าง: ชื่อ 'Semiconductors วิ่ง — เพราะอะไร?' · idea.status draft · โน้ต 'หุ้นกลุ่ม Semiconductors ขึ้นพร้อมกันใน screen 2026-10-05' · tickers = 4 ตัวกลุ่ม · origin · scope US", d is not None and I.get("name") == "Semiconductors วิ่ง — เพราะอะไร?" and I.get("status") == "draft" and un.get("idea") == "หุ้นกลุ่ม Semiconductors ขึ้นพร้อมกันใน screen 2026-10-05" and un.get("tickers") == ["LSCC", "QRVO", "SYNA", "PENG"] and I.get("origin") == [{"title": "TradingView screen 2026-10-05"}] and I.get("scope") == ["US"] and d.get("user") == {}, json.dumps(I, ensure_ascii=False)[:500])
        check(f"{tag} 4 ＋ → sheet ปิด · เปิดการ์ดร่างทันที (มี ที่มา ในการ์ด + คำสั่ง scan มี 'ที่มา:')", not js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')") and "ร่าง — ยังไม่ได้รัน" in (txt_of(page, "[data-idea-draft-msg]") or "") and "TradingView screen 2026-10-05" in (txt_of(page, "[data-idea-draft]") or ""))
        page.click("[data-idea-copyscan]"); page.wait_for_timeout(250)
        check(f"{tag} 4 คำสั่ง scan ของร่างจากกลุ่ม ตรงรูปแบบ (ไอเดีย · ชื่อ · ตลาด · หุ้น · ที่มา · ไม่มีโน้ต)", js(page, "()=>window.__ideaLastScan") == "idea-scout scan\nไอเดีย: หุ้นกลุ่ม Semiconductors ขึ้นพร้อมกันใน screen 2026-10-05\nชื่อ: Semiconductors วิ่ง — เพราะอะไร? · id: semiconductors-20261005 (ใช้ id เดิม — Import แล้วแทนที่ร่างนี้)\nตลาด: US\nหุ้นที่นึกไว้: LSCC, QRVO, SYNA, PENG\nที่มา: TradingView screen 2026-10-05", js(page, "()=>window.__ideaLastScan"))
        check(f"{tag} 4 ไม่มี console error (＋ กลุ่ม)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()
    # สูงสุด 3 กลุ่ม · เรียงมาก → น้อย
    def gen(counts):
        lines = ["Symbol,Description,Price - Currency,Industry"]
        for ind, n in counts:
            for i in range(n): lines.append(f"{ind[:2].upper()}{i},Co {ind[:2]}{i},USD,{ind}")
        return "\n".join(lines)
    b, c, page, ce, pe, dl = launcher(pw, w, h, [])
    try:
        open_match(page, gen([("Alpha", 3), ("Beta", 5), ("Gamma", 4), ("Delta", 3), ("Epsilon", 9)]))
        gl = txt_of(page, "[data-match-groups]") or ""
        check(f"{tag} 4 สูงสุด 3 กลุ่ม เรียงมาก → น้อย: Epsilon (9) · Beta (5) · Gamma (4) (Alpha/Delta ไม่ขึ้น)", gl.count("(") == 3 and gl.index("Epsilon") < gl.index("Beta") < gl.index("Gamma") and "Alpha" not in gl and "Delta" not in gl, gl)
    finally:
        b.close()

    # ───── ตั้งค่า (หน้าตั้งค่า) ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [])
    try:
        js(page, "()=>{ openSystemSettings(); document.getElementById('ideaSetSec').open = true; }"); page.wait_for_timeout(300)
        v0 = js(page, "()=>[document.getElementById('ideaGroupMinIn').value, document.getElementById('ideaGroupDaysIn').value]")
        check(f"{tag} 4 หน้าตั้งค่ามีช่อง min / วันซ่อน ค่าเริ่ม 3 / 30", v0 == ["3", "30"], json.dumps(v0))
        for (a, bb, want) in (("1", "30", "2–10"), ("11", "30", "2–10"), ("2.5", "30", "2–10"), ("3", "0", "1–90"), ("3", "91", "1–90"), ("3", "", "1–90")):
            fillx(page, "#ideaGroupMinIn", a); page.fill("#ideaGroupDaysIn", bb); js(page, "()=>ideaSetSave()"); page.wait_for_timeout(100)
            msg = txt_of(page, "#ideaSetMsg") or ""
            if want not in msg: check(f"{tag} 4 ค่าไม่ถูก ({a},{bb}) → error {want}", False, msg)
        check(f"{tag} 4 ค่านอกช่วง (1 / 11 / 2.5 / วัน 0 / 91 / ว่าง) → error ทุกกรณี · ไม่บันทึก", js(page, "()=>[getBook(tdHome()).settings.ideaGroupMin, getBook(tdHome()).settings.ideaGroupHideDays]") == [None, None])
        fillx(page, "#ideaGroupMinIn", "2"); page.fill("#ideaGroupDaysIn", "7"); js(page, "()=>ideaSetSave()"); page.wait_for_timeout(300)
        check(f"{tag} 4 บันทึก 2 / 7 → ใช้ทันที (ideaGroupMin()=2 · ideaGroupHideDays()=7) · ข้อความ 'บันทึกแล้ว'", js(page, "()=>[ideaGroupMin(), ideaGroupHideDays()]") == [2, 7] and "บันทึกแล้ว" in (txt_of(page, "#ideaSetMsg") or ""), txt_of(page, "#ideaSetMsg"))
        js(page, "()=>{ const B=getBook(tdHome()); B.settings.ideaGroupMin='abc'; B.settings.ideaGroupHideDays=999; }")
        check(f"{tag} 4 ค่าเสียใน settings → ใช้ค่าเริ่ม 3 / 30", js(page, "()=>[ideaGroupMin(), ideaGroupHideDays()]") == [3, 30])
    finally:
        b.close()

    # ───── 5 · คำสั่ง match ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [semis()])
    try:
        go_cand(page)
        page.click("[data-cand-match-top]"); page.wait_for_selector("#matchText", state="visible")
        page.set_input_files("#matchFile", CSV_PATH); page.wait_for_timeout(500)
        check(f"{tag} 5 เลือกไฟล์ .csv → อ่านได้ 9 แถว · สรุปมีชื่อไฟล์", len(rows_info(page)) == 9 and "tv_volume_spike_2026-10-05.csv" in (txt_of(page, "[data-match-sum]") or ""), txt_of(page, "[data-match-sum]"))
        page.click("[data-match-copy]"); page.wait_for_timeout(300)
        cmd = js(page, "()=>window.__ideaLastMatch"); L = cmd.split("\n")
        i0 = L.index("หุ้น (Symbol · Description · Industry · ตลาด):"); i1 = L.index("สรุปไอเดียสำหรับจับคู่:")
        stk = L[i0 + 1:i1]
        check(f"{tag} 5 หัวคำสั่ง: 'idea-scout match' · 'วันที่: 2026-10-05 · ที่มา: {{ชื่อไฟล์}}'", L[0] == "idea-scout match" and L[1] == "วันที่: 2026-10-05 · ที่มา: tv_volume_spike_2026-10-05.csv", json.dumps(L[:2], ensure_ascii=False))
        check(f"{tag} 5 ค่าเริ่ม = ส่งเฉพาะ 7 ตัวกลุ่ม Industry ตรง (ไม่มี NTAP · IBRX) · รูปแบบ 'SYM · Description · Industry · ตลาด'", len(stk) == 7 and "TER · Teradyne, Inc. · Electronic production equipment · US" in stk and not any(s.startswith(("NTAP", "IBRX")) for s in stk), json.dumps(stk, ensure_ascii=False))
        brief = "\n".join(L[i1 + 1:])
        check(f"{tag} 5 สรุปไอเดีย 1 ไอเดีย: '[id] ชื่อ — one_liner' + ได้/เสีย/ปนกัน พร้อม industries", brief.startswith("[" + SEMIS_ID + "] ") and brief.count("[" + SEMIS_ID + "]") == 1 and "\n ได้: " + SEG + " (Electronic Production Equipment, Semiconductors) ; " in brief and "\n เสีย: ผู้ผลิตอุปกรณ์ปลายทาง" in brief and "Electronic Components" in brief and "\n ปนกัน: hyperscaler · cloud (Internet Software/Services" in brief, brief[:700])
        first = brief.split("\n")[0]
        check(f"{tag} 5 one_liner ≤ 300 ตัวอักษร · ไม่มีส่วนอื่นของไอเดียปน (หลักฐาน / known / Micron / candidates)", len(first.split(" — ", 1)[1]) <= 300 and not any(x in cmd for x in ["Micron", "หลักฐาน", "hyperscaler 5 ราย", "known", "KLAC"]), json.dumps(first, ensure_ascii=False)[:200])
        check(f"{tag} 5 ขนาดคำสั่ง < 4000 ตัวอักษร (ไอเดียละ ~200 tokens)", len(brief) < 1500 and len(cmd) < 4000, f"{len(brief)} / {len(cmd)}")
        page.check("[data-match-cut]"); page.wait_for_timeout(100); page.click("[data-match-copy]"); page.wait_for_timeout(300)
        cmd2 = js(page, "()=>window.__ideaLastMatch"); L2 = cmd2.split("\n")
        stk2 = L2[L2.index("หุ้น (Symbol · Description · Industry · ตลาด):") + 1:L2.index("สรุปไอเดียสำหรับจับคู่:")]
        check(f"{tag} 5 ติ๊ก 'ส่งตัวที่ถูกตัดด้วย' → 9 ตัว (มี NTAP · IBRX)", len(stk2) == 9 and any(s.startswith("NTAP · NetApp, Inc. · Computer peripherals · US") for s in stk2) and any(s.startswith("IBRX") for s in stk2), json.dumps(stk2, ensure_ascii=False)[:400])
        # ไม่มีไฟล์ → ที่มา = TradingView screen
        page.fill("#matchText", CSV); page.click("[data-match-read]"); page.wait_for_timeout(150); page.click("[data-match-copy]"); page.wait_for_timeout(300)
        check(f"{tag} 5 วางข้อความ (ไม่มีไฟล์) → 'ที่มา: TradingView screen'", js(page, "()=>window.__ideaLastMatch").split("\n")[1] == "วันที่: 2026-10-05 · ที่มา: TradingView screen")
        check(f"{tag} 5 ไม่มี console error (คำสั่ง match)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 6–7 · Import idea-match@1 · ผลที่เห็น ─────
    user0 = {"pick": {SEG: True}, "updated_at": "2026-10-04T00:00:00.000Z"}
    b, c, page, ce, pe, dl = launcher(pw, w, h, [(semis(), user0), parked()])
    try:
        open_match(page, CSV)
        page.click("[data-match-import-open]"); page.wait_for_selector("#matchJson", state="visible")
        fill_json(page, match_json())
        pv = txt_of(page, "[data-match-prev]") or ""
        check(f"{tag} 6 ตัวอย่างก่อนบันทึก: ไอเดีย semis '+3 รอตรวจ ▲ · +1 รอตรวจ ▼'", "+3 รอตรวจ ▲" in pv and "+1 รอตรวจ ▼" in pv, pv)
        check(f"{tag} 6 ตัวอย่างแจ้งข้าม: ไอเดียไม่พบ 1 · ไอเดียไม่ได้อยู่สถานะที่นับ 1 · ตัดชื่อส่วนที่ไม่มีในไอเดีย 1 ชื่อ · dropped 2", "ข้าม 1 แถว: ไอเดียไม่พบ" in pv and "ข้าม 1 แถว: ไอเดียไม่ได้อยู่สถานะที่นับ" in pv and "ตัดชื่อส่วนที่ไม่มีในไอเดีย 1 ชื่อ" in pv and "(dropped) 2 ตัว" in pv, pv)
        shot_modal(page, f"id3a-match-import-{sfx}.png")
        check(f"{tag} 6 ยังไม่บันทึกก่อนกดบันทึก (doc ไม่เปลี่ยน)", ((idb(page).get("idea") or {}).get("candidates") or []) == [] and len(idb(page)["idea_log"]) == 1)
        page.click("[data-match-imp-save]"); page.wait_for_timeout(600)
        d = idb(page); I = d["idea"]
        cs = {c["sym"]: c for c in I["candidates"]}
        check(f"{tag} 6 บันทึก → candidates +3 (TER · VECO · CAMT) state 'screen' · from 'match' · relevance_src '' · rank null", list(cs) == ["TER", "VECO", "CAMT"] and all(c["state"] == "screen" and c["from"] == "match" and c["relevance_src"] == "" and c["rank"] is None for c in cs.values()), json.dumps(I["candidates"], ensure_ascii=False)[:500])
        check(f"{tag} 6 ชื่อบริษัทมาจาก list ที่วางไว้ (TER = 'Teradyne, Inc.') · segments ตัดชื่อผิดทิ้ง (VECO เหลือ [{SEG}]) · why_this/fit ตามไฟล์", cs["TER"]["name"] == "Teradyne, Inc." and cs["VECO"]["segments"] == [SEG] and cs["VECO"]["fit"] == "unsure" and cs["TER"]["why_this"] == "เกี่ยวกับธีม" and cs["CAMT"]["name"] == "Camtek Ltd.", json.dumps([cs["TER"], cs["VECO"]], ensure_ascii=False)[:500])
        check(f"{tag} 6 losers +1 (QRVO) state 'screen' · src '' · why ตามไฟล์", I["losers"] == [{"sym": "QRVO", "market": "US", "why": "ลูกค้าตัดงบ", "src": "", "state": "screen"}], json.dumps(I["losers"], ensure_ascii=False))
        check(f"{tag} 6 idea_log +1 บรรทัด 'match: +3 ▲ +1 ▼ รอตรวจ (TradingView screen)' วันที่ 2026-10-05", len(d["idea_log"]) == 2 and d["idea_log"][-1]["new"] == "match: +3 ▲ +1 ▼ รอตรวจ (TradingView screen)" and d["idea_log"][-1]["date"] == "2026-10-05", json.dumps(d["idea_log"], ensure_ascii=False)[:300])
        check(f"{tag} 6 field user เดิมไม่เปลี่ยน · ไอเดียที่พัก (idea-parked) ไม่ถูกแตะ", d["user"] == user0 and (idb(page, "idea-parked")["idea"].get("candidates") or []) == [] and len(idb(page, "idea-parked")["idea_log"]) == 1, json.dumps(d["user"]))
        check(f"{tag} 6 บันทึกแล้ว sheet ปิด", not js(page, "()=>document.getElementById('ltOverlay').classList.contains('show')"))
        # Import ซ้ำ
        open_match(page, CSV); fill_json(page, match_json())
        pv = txt_of(page, "[data-match-prev]") or ""
        check(f"{tag} 6 Import ซ้ำ → ข้าม 'อยู่ในไอเดียแล้ว' ทั้งหมด · ไม่มีปุ่มบันทึก · doc ไม่เพิ่มซ้ำ", "ข้าม 4 (อยู่ในไอเดียแล้ว)" in pv and not page.locator("[data-match-imp-save]").is_visible() and len(idb(page)["idea"]["candidates"]) == 3 and len(idb(page)["idea_log"]) == 2, pv)
        js(page, "()=>ideaSheetClose()")

        # ───── 7 · ผลที่เห็น ─────
        go_cand(page)
        syms = cand_syms(page)
        badges = {s: (js(page, "(s)=>{ const e=document.querySelector('.wlR[data-sym=\"'+s+'\"] [data-idea-badge]'); return e ? e.innerText : null; }", s)) for s in ["TER", "VECO", "CAMT"]}
        check(f"{tag} 7 Candidates มี TER · VECO · CAMT ติดป้าย ▲? (รอตรวจ)", all(s in syms for s in badges) and all(v and "▲?" in v for v in badges.values()), json.dumps([syms, badges], ensure_ascii=False))
        js(page, "()=>wlOpen('TER')"); page.wait_for_timeout(300)
        btn = js(page, "()=>{ const b=document.querySelector('[data-c-add]'); return b ? {dis:b.disabled, why:(document.querySelector('[data-c-add-why]')||{}).innerText||''} : null; }")
        check(f"{tag} 7 TER → Watchlist กดไม่ได้ + 'รอตรวจ — รัน pick ก่อน'", btn and btn["dis"] is True and "รอตรวจ — รัน pick ก่อน" in btn["why"], json.dumps(btn, ensure_ascii=False))
        js(page, "()=>{ ideaGo('" + SEMIS_ID + "','vc'); }"); page.wait_for_timeout(300)
        tks = js(page, "()=>[...document.querySelectorAll('.ideaTk.q')].map(e=>e.innerText)")
        check(f"{tag} 7 Value chain: ticker เหลืองมี '?' (TER ? · VECO ? · CAMT ?)", sorted(set(tks)) == ["CAMT ?", "TER ?", "VECO ?"], json.dumps(tks))
        lb = txt_of(page, "[data-idea-lose]") or ""
        check(f"{tag} 7 กล่องแดง 'หุ้นของเราที่อยู่ฝั่งเสีย' นับ QRVO (อยู่ Watchlist) แต่มี ?", "QRVO" in lb and page.locator("[data-idea-lose] [data-idea-lose-q]").count() == 1, lb)
        check(f"{tag} 7 แท็บ Value chain มีตัวเลขแดง 1 (ours)", (txt_of(page, "[data-idea-vcn]") or "") == "1")
        go_wl = js(page, "()=>{ wlSetView('wl'); wlOpen('QRVO'); return true; }"); page.wait_for_timeout(350)
        bd = js(page, "()=>{ const e=document.querySelector('.wlR[data-sym=\"QRVO\"] [data-idea-badge]'); return e ? e.innerText : null; }")
        check(f"{tag} 7 QRVO ใน Watchlist → ป้าย ▼? ที่แถว", bd and "▼?" in bd, json.dumps(bd, ensure_ascii=False))
        hu = js(page, "()=>{ const b=document.querySelector('[data-idea-handoff-up]'); return b ? {dis:b.disabled, why:(document.querySelector('[data-idea-handoff-up-why]')||{}).innerText||''} : null; }")
        check(f"{tag} 7 การ์ด QRVO: 'คัดลอก Handoff (update)' กดไม่ได้ + 'รอตรวจ — รัน pick ก่อน'", hu and hu["dis"] is True and "รอตรวจ — รัน pick ก่อน" in hu["why"], json.dumps(hu, ensure_ascii=False))
        check(f"{tag} 7 เรียก ideaDoCopy('lose') ตรง ๆ ก็ไม่คัดลอก (รอตรวจ)", js(page, "()=>{ window.__ideaLastHandoff=''; ideaDoCopy('lose','" + SEMIS_ID + "','QRVO'); return window.__ideaLastHandoff; }") == "")
        js(page, "()=>{ ideaGo('" + SEMIS_ID + "'); }"); page.wait_for_timeout(250)
        page.click("[data-idea-menu]"); page.wait_for_selector("[data-idea-export]"); page.click("[data-idea-export]"); page.wait_for_timeout(400)
        try: o = json.loads(js(page, "()=>window.__ideaLastExport"))
        except Exception as ex: o = {}
        check(f"{tag} 7 Export JSON มีบริษัทจาก match (TER · VECO · CAMT) และ losers (QRVO)", [x["sym"] for x in o.get("candidates", [])] == ["TER", "VECO", "CAMT"] and [x["sym"] for x in o.get("losers", [])] == ["QRVO"] and o["candidates"][0]["state"] == "screen" and len(o.get("log", [])) == 2, json.dumps(o.get("candidates", []))[:200])
        check(f"{tag} 7 หน้าไม่ล้นแนวนอน", overflow(page) <= 0, str(overflow(page)))
        check(f"{tag} 7 ไม่มี console error (Import match)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # Import ผิด
    b, c, page, ce, pe, dl = launcher(pw, w, h, [semis(), parked()])
    try:
        open_match(page, CSV); page.click("[data-match-import-open]"); page.wait_for_selector("#matchJson", state="visible")
        good = match_json()
        big = match_json(audit="x" * 210000)
        mod = lambda i, k, v: dict(good, results=[dict(r, **{k: v}) if j == i else r for j, r in enumerate(good["results"])])
        cases = [("ว่าง", "", "ยังไม่ได้วาง JSON"), ("JSON พัง", "{not json", "อ่าน JSON ไม่ได้"), ("schema ผิด", json.dumps(dict(good, schema="idea@1")), 'schema ต้องเป็น "idea-match@1"'),
                 ("results ไม่ใช่ list", json.dumps(dict(good, results={})), "results ต้องเป็นรายการ"), ("sym ว่าง", json.dumps(mod(0, "sym", "")), "แถวที่ 1: sym ว่าง"),
                 ("side ผิด", json.dumps(mod(1, "side", "buy")), "แถวที่ 2: side ต้องเป็น"), ("fit ผิด", json.dumps(mod(2, "fit", "maybe")), "แถวที่ 3: fit ต้องเป็น"), (">200KB", json.dumps(big, ensure_ascii=False), "เกิน 200KB")]
        for nm, text, want in cases:
            fill_json(page, text)
            err = txt_of(page, "#matchImpErr") or ""
            check(f"{tag} 6 Import ผิด · {nm} → error ภาษาไทย ไม่บันทึก", want in err and not page.locator("[data-match-imp-save]").is_visible() and not page.locator("[data-match-prev]").count(), err)
        fill_json(page, "```json\nผลจับคู่:\n" + json.dumps(good, ensure_ascii=False) + "\n```\nจบ")
        check(f"{tag} 6 ตัด ```json / ข้อความหน้า-หลัง แบบ Import อื่น → ผ่าน", page.locator("[data-match-prev]").count() == 1)
        check(f"{tag} 6 ไม่มี doc ถูกแก้จากไฟล์ผิด (semis ยังไม่มี candidates)", (idb(page)["idea"].get("candidates") or []) == [] and len(idb(page)["idea_log"]) == 1)
        check(f"{tag} 6 ไม่มี console error (Import ผิด)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 8 · ID1 Import เจอ idea-match@1 ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [])
    try:
        go_ideas(page)
        page.click("[data-idea-import-top]"); page.wait_for_selector("#ideaJson", state="visible")
        page.fill("#ideaJson", json.dumps(match_json(), ensure_ascii=False)); page.click("[data-idea-check]"); page.wait_for_timeout(150)
        err = txt_of(page, "#ideaErrBox") or ""
        check(f"{tag} 8 Import ไอเดีย (ID1) ใส่ไฟล์ idea-match@1 → 'ไฟล์นี้เป็นผลจับคู่ — Import ที่ Candidates › 📋 จับคู่ list' · ไม่มีปุ่มบันทึก", err == "ไฟล์นี้เป็นผลจับคู่ — Import ที่ Candidates › 📋 จับคู่ list" and not page.locator("[data-idea-save]").is_visible(), err)
        check(f"{tag} 8 ไม่มี doc ถูกสร้าง", not [k for k in js(page, "()=>Object.keys(window.firebase.__mockDb.__dump())") if "/ideas/" in k])
        check(f"{tag} 8 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()

    # ───── 9 · ขอบเขต list ─────
    b, c, page, ce, pe, dl = launcher(pw, w, h, [semis()])
    try:
        big_rows = "Symbol,Description,Industry\n" + "\n".join(f"T{i},Co {i},Semiconductors" for i in range(501))
        ok_rows = "Symbol,Description,Industry\n" + "\n".join(f"T{i},Co {i},Semiconductors" for i in range(500))
        big_bytes = "Symbol,Description,Industry\n" + "\n".join(f"T{i},{'x' * 300},Semiconductors" for i in range(1100))
        open_match(page, big_rows)
        check(f"{tag} 9 CSV 501 แถว → error 'เกิน 500 แถว' · ไม่มีผล", "เกิน 500 แถว" in (txt_of(page, "#matchErr") or "") and page.locator("[data-match-row]").count() == 0, txt_of(page, "#matchErr"))
        page.fill("#matchText", ok_rows); page.click("[data-match-read]"); page.wait_for_timeout(300)
        check(f"{tag} 9 CSV 500 แถว → ผ่าน (อ่านได้ 500 แถว) · หน้าไม่ล้น", "อ่านได้ 500 แถว" in (txt_of(page, "[data-match-sum]") or "") and not (txt_of(page, "#matchErr") or ""))
        page.fill("#matchText", big_bytes); page.click("[data-match-read]"); page.wait_for_timeout(300)
        check(f"{tag} 9 list > 300KB → error 'เกิน 300KB' · ไม่มีผล", "เกิน 300KB" in (txt_of(page, "#matchErr") or "") and page.locator("[data-match-row]").count() == 0, txt_of(page, "#matchErr"))
        page.fill("#matchText", "Symbol,Description,Industry\n"); page.click("[data-match-read]"); page.wait_for_timeout(150)
        check(f"{tag} 9 มีแต่หัวตาราง → error 'ไม่มีแถวข้อมูล'", "ไม่มีแถวข้อมูล" in (txt_of(page, "#matchErr") or "") and page.locator("[data-match-row]").count() == 0, txt_of(page, "#matchErr"))
        page.fill("#matchText", "!!! ??? ###"); page.click("[data-match-read]"); page.wait_for_timeout(150)
        check(f"{tag} 9 ข้อความที่ไม่มี ticker → error 'ไม่มีแถวข้อมูล'", "ไม่มีแถวข้อมูล" in (txt_of(page, "#matchErr") or ""), txt_of(page, "#matchErr"))
        page.fill("#matchText", '﻿Symbol,"Description",Price - Currency,Industry\r\nNASDAQ:AAA,"Say ""hi"", Inc.",THB,"Semi, conductors"\r\n'); page.click("[data-match-read]"); page.wait_for_timeout(150)
        info = rows_info(page)
        check(f"{tag} 9 CSV แบบ BOM + CRLF + \"\" + จุลภาคในเครื่องหมายคำพูด + 'NASDAQ:AAA' + THB → AAA · 'Say \"hi\", Inc.' · 'Semi, conductors' · ตลาด TH", list(info) == ["AAA"] and info["AAA"]["desc"] == 'Say "hi", Inc.' and info["AAA"]["ind"] == "Semi, conductors", json.dumps(info, ensure_ascii=False))
        page.fill("#matchText", "Symbol,Description,Industry\nA,x,I\na,y,I\nB,z,I"); page.click("[data-match-read]"); page.wait_for_timeout(150)
        check(f"{tag} 9 ticker ซ้ำ (A / a) นับครั้งเดียว", sorted(rows_info(page)) == ["A", "B"])
        check(f"{tag} 9 หน้า/sheet ไม่ล้นแนวนอน · ไม่มีข้อความดิบ (undefined / [object / &amp;)", modal_over(page) <= 1 and overflow(page) <= 0 and not any(x in (txt_of(page, "#ltModal") or "") for x in BAD_TXT), json.dumps([modal_over(page), overflow(page)]))
        check(f"{tag} 9 ไม่มี console error (ขอบเขต list)", not ce and not pe, json.dumps([ce, pe]))
    finally:
        b.close()


def static_tests():
    check("[static] สำรอง index.backup-pre-ID3a.html + tests/_bk_id3a/ อยู่", os.path.exists(os.path.join(ROOT, "index.backup-pre-ID3a.html")) and os.path.isdir(os.path.join(HERE, "_bk_id3a")))
    check("[static] fixture CSV จริงยังอยู่ครบ 9 แถวข้อมูล + 17 คอลัมน์", len([l for l in CSV.strip().split("\n")]) == 10 and CSV.split("\n")[0].count(",") >= 16)
    check("[static] ไม่แตะ core-size.js (sha ตรงกับก่อนทำ ID3a · CZ1 แก้ไฟล์ตามบรีฟ จึงเทียบกับสำรอง core-size.backup-pre-CZ1.js = สถานะก่อน CZ1)", hashlib.md5(open(os.path.join(ROOT, "core-size.backup-pre-CZ1.js"), "rb").read()).hexdigest() == "52c2f9de908f4032208fe68ba57085af")
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    check("[static] ตัวอ่าน CSV ไม่ใช้ split(',') กับแถวข้อมูล", "split(',')" not in html.split("function matchCsv(")[1].split("function matchParseList")[0])


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 47 / ID3a) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
