#!/usr/bin/env python3
"""WL1 — Watchlist Overview ใหม่ (WL2: ปรับเป็นแท็บ สรุป/ติดตาม/ออกเมื่อ บน Thesis · Catalysts · Blockers · Tripwire · โน้ตของฉัน · เอา FQC ออก) + ช่องเช็ก Tier + ค่าตั้ง SR1 · เทส 35
mock Firestore · Chromium 1440 + 430 · นาฬิกาปลอม = 2026-10-01 (เวลาไทย)
seed: AVGO (Watchlist + research_card: catalysts 3 [estimated 2026-12-10 · confirmed 2026-11-20 · ผ่านแล้ว 2026-09-01] · severe_risks 5 · tripwires 2 [check + watching] · fqc + investment_clearance)
      CALM (tripwire ไม่มี check) · NOCARD (ไม่มี research_card) · CAND1 (candidate · ไม่อยู่ Watchlist)
ภาพเก็บที่ tests/screenshots/wl1-*.png
รัน: python3 run_tests_phase35.py [/path/to/index.html]"""
import json, copy, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase24 as p24
import run_tests_phase26 as p26
import run_tests_phase29 as p29

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else base.DEFAULT_INDEX
p24.INDEX = INDEX
p29.INDEX = INDEX
results = []
txt = p24.txt
doc26 = p26.doc26; FF_OPEN = p26.FF_OPEN
BASE = json.load(open(os.path.join(HERE, "..", "avgo-research-card-th.json"), encoding="utf-8"))
SRC = "https://www.sec.gov/Archives/edgar/data/1/x.htm"


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot_el(page, sel, name):
    try:
        page.wait_for_timeout(400)
        page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
    except Exception as e: print("shot fail", name, e)


import run_tests_phase38 as P38   # WL2: th()/wl_th() สร้าง Thesis (living-thesis@1)


def m(name, value, unit="%", period="TTM"): return {"name": name, "value": value, "unit": unit, "period": period, "source_url": SRC}


def card(tk, tws, chk=(True, True, True), cats=True):
    """WL2 — Thesis แทน research_card เดิม · tws = [(signal, level, now)] · chk = (fcf3y, capret, ocf) → thesis.tier_inputs"""
    c = P38.th(tk, [], [], date="2026-09-28"); c["asOf"] = "2026-09-28"
    c["catalysts"] = ([{"event": "งบ Q4 FY26", "date": "2026-12-10", "date_status": "estimated", "thesis": 1},
                       {"event": "งานประชุมนักลงทุน", "date": "2026-11-20", "date_status": "confirmed", "thesis": 1},
                       {"event": "ประกาศเก่าที่ผ่านแล้ว", "date": "2026-09-01", "date_status": "confirmed", "thesis": 1}] if cats else [])
    c["tripwires"] = [{"thesis": 1, "area": "demand", "signal": t[0], "now": t[2], "level": t[1]} for t in tws]
    c["tier_inputs"] = {"roic": {"v": 24.5, "tag": "C", "period": "FY25", "src": "ทดสอบ"}}
    for k, v in zip(("fcfPositive3y", "capitalReturn", "ocfPositive"), chk): c["tier_inputs"][k] = {"v": v, "tag": "F", "period": "FY25", "src": "ทดสอบ"}
    return c


TW_CHECK = [("ลูกค้า 5 รายใหญ่ > 55%", "review", "~55% (Q3)"), ("ชิป AI Q4 < 21.7B", "watch", "Q3 = 16.7B")]
TW_CALM = [("ลูกค้า 5 รายใหญ่ > 55%", "watch", "~50%"), ("ชิป AI Q4 < 21.7B", "watch", "Q3 = 16.7B")]
FQC = {"lane": "A", "score": 8, "eligible": True, "approx": False}
IC = {"status": "verified_legacy", "ok": True, "valid_until": "2027-01-01", "evaluated_at": "2026-09-01", "source": {"rule_set": "legacy_entry_v1", "gates_checked_at": "2026-09-01", "fqc_date": "2026-09-01"}}


def put_research(page, tk, d):
    page.evaluate("([k,d])=>window.firebase.__mockDb.__seedDoc(['research',k], d)", [tk, d])


def put_thesis(page, tk, th, **kw):
    """WL2 — แทน Thesis ของ watchlist/{tk} (update) — ไม่ผ่าน UI"""
    page.evaluate("([k,t])=>wlCol().doc(k).update({thesis:t})", [tk, th]); page.wait_for_timeout(300)


IDEA_CAND1 = json.loads('''{"idea": {"schema": "idea@1", "id": "cand-fixture", "name": "ไอเดียตัวอย่าง (ID2: ให้ CAND1 เป็น Candidates)", "date": "2026-10-01", "mode": "scan", "scope": ["US"], "status": "need_evidence", "idea": {}, "chain": {"segments": [{"name": "ส่วนทดสอบ", "effect": "win"}]},
 "candidates": [{"sym": "CAND1", "market": "US", "name": "Cand One", "segments": ["ส่วนทดสอบ"], "relevance_src": "10-K ตัวอย่าง", "rank": 1, "state": "study"}], "kill": [], "gaps": [], "evidence": []}, "idea_log": [], "user": {}}''')


def seed(page):
    put_research(page, "AVGO", {"ticker": "AVGO", "name": "Broadcom Inc.", "fqc": FQC, "investment_clearance": IC})
    put_research(page, "CALM", {"ticker": "CALM", "name": "Calm Co"})
    put_research(page, "NOCARD", {"ticker": "NOCARD", "name": "No Card Co"})
    put_research(page, "CAND1", {"ticker": "CAND1", "name": "Cand One", "mode_a": {"score": 9, "max": 15, "rank": 3, "one_liner": "ผู้สมัครตัวอย่าง"}})
    page.evaluate("(d)=>window.firebase.__mockDb.__seedDoc(['users','testuid','ideas','cand-fixture'], d)", IDEA_CAND1)   # ID2 — Candidates มาจากไอเดีย: ให้ CAND1 เป็นบริษัทในไอเดีย (เคสเดิมตรวจสิ่งเดิม)
    page.evaluate("() => rsLoad(true)"); page.wait_for_timeout(300)


def _wlx(tk, t, **kw):
    d = P38.wl_th(tk, t); d.pop("ticker", None); d.pop("market", None); d.pop("port", None); d.pop("note", None); d.pop("industry", None); d.pop("added_at", None); d.update(kw); return d


WL = {"AVGO": _wlx("AVGO", card("AVGO", TW_CHECK), industry="Semis", note="ถือยาว ดูงบ Q4 ก่อนเติม", tier="A", tier_lens="both", tier_set_at="2026-09-01", fqc=FQC),
      "CALM": _wlx("CALM", card("CALM", TW_CALM)), "NOCARD": {}}


def open_ov(page, tk, sub="sum"):
    page.evaluate("([t,s])=>{ switchTab('watch'); wlSetView('wl'); wlOpen(t); wlSetSub(s); }", [tk, sub]); page.wait_for_timeout(350)


def open_cand(page, tk):
    page.evaluate("(t)=>{ switchTab('watch'); wlSetView('cand'); wlOpen(t); }", tk); page.wait_for_timeout(350)


def ov(page): return txt(page, ".wlOv") or ""
def n(page, sel): return page.locator(sel).count()
def wl_doc(page, t): return p29.wl_doc(page, t)
def dump(page): return p29.dump(page)


def overflow(page):
    return page.evaluate("""()=>{ const W = window.innerWidth, bad = [];
      document.querySelectorAll('.wlOv, .wlOv *').forEach(e=>{ const r = e.getBoundingClientRect(); if(r.width && (r.right > W + 1 || r.left < -1)) bad.push((e.className||e.tagName) + ':' + Math.round(r.left) + '-' + Math.round(r.right)); });
      const b = document.querySelector('.wlOv'); if(b && b.scrollWidth > b.clientWidth + 1) bad.push('wlOv scroll'); return bad.slice(0, 6); }""")


def checks(pw, w, h, label):
    tag = f"[chromium/{label}]"
    browser, context, page, ce, pe, dialogs = p29.launch(pw, w, h, doc26(), wl=WL)
    try:
        p24.set_ff(page, FF_OPEN()); seed(page)
        # 1 ─ AVGO สรุป (WL2 · เดิม Overview)
        open_ov(page, "AVGO")
        t = ov(page); full = txt(page, "body") or ""
        chip = txt(page, "[data-lt-chip]") or ""
        check(f"{tag} 1 AVGO แท็บ สรุป: ไม่มีคำ FQC · ไม่มี 'เกณฑ์ลงทุนเดิม' ทั้งแผง", "FQC" not in (txt(page, ".wlDBody") or "") and "FQC" not in (txt(page, ".wlDPanel") or "") and "เกณฑ์ลงทุนเดิม" not in full, t[:200])
        check(f"{tag} 1 ไม่มีบรรทัด 'ต้องทำ' · ไม่มีป้าย Business ซ้าย (.wlKV) · ไม่มีชิป 'Research Card' (WL2 ลบ Research Card แล้ว)", "ต้องทำ" not in t and n(page, ".wlTodo") == 0 and n(page, ".wlOv .wlKV") == 0 and "Research Card" not in (txt(page, ".ltChips") or "") and "Research Card" not in full, t[:200])
        check(f"{tag} 1 ชิป 'Thesis lite · 28 ก.ย.' (WL2 · เดิม 'Research 2026-09-28 · 3 วัน') + Industry อยู่แถวชิป", chip == "Thesis lite · 28 ก.ย." and "Semis" in (txt(page, ".ltChips") or ""), chip)
        # 2 ─ แถบเตือน (WL2 · tripwire ระดับ review/broken)
        al = txt(page, "[data-wl-alert]") or ""
        check(f"{tag} 2 AVGO แถบเตือนขึ้น (tripwire review) · มีชื่อ tripwire · ข้อความตามแบบ WL2", n(page, "[data-wl-alert]") == 1 and 'ลูกค้า 5 รายใหญ่ > 55%' in al and al.startswith("🟠 Tripwire ถึงระดับทบทวน:") and "ดูแท็บ ออกเมื่อ" in al, al)
        shot_el(page, ".wlDBody", f"wl1-overview-alert-{w}.png")
        page.click("[data-wl-alert]"); page.wait_for_timeout(250)
        check(f"{tag} 2 กดแถบเตือน → wlSub === 'exit' (แท็บ ออกเมื่อ · เดิม 'rs')", page.evaluate("()=>wlSub") == "exit")
        open_ov(page, "CALM")
        check(f"{tag} 2 CALM ไม่มีแถบเตือน", n(page, "[data-wl-alert]") == 0)
        shot_el(page, ".wlDBody", f"wl1-overview-calm-{w}.png")
        d = copy.deepcopy(dump(page)["users/testuid/watchlist/AVGO"]["thesis"]); d["tripwires"][0]["level"] = "broken"
        put_thesis(page, "AVGO", d)
        open_ov(page, "AVGO")
        al2 = txt(page, "[data-wl-alert]") or ""
        red = page.evaluate("()=>{ const e=document.querySelector('[data-wl-alert]'); return e && e.classList.contains('red'); }")
        check(f"{tag} 2 tripwire broken → แถบแดง 'พัง' (เดิม confirmed 'ยืนยันแล้ว')", red and "พัง" in al2 and al2.startswith("⛔"), al2)
        d["tripwires"][0]["level"] = "review"; put_thesis(page, "AVGO", d)
        open_ov(page, "AVGO", "trk")
        # 3 ─ Catalysts (WL2 · แท็บ ติดตาม · วันที่ผ่านแล้วแสดงพร้อมป้าย 'ผ่านไปแล้ว')
        rows = page.evaluate("()=>[...document.querySelectorAll('[data-wl-sec=cat] li')].map(l=>({t:l.innerText.replace(/\\s+/g,' ').trim(), est:!!l.querySelector('.wlDt.est'), past:!!l.querySelector('.wlDt.past')}))")
        check(f"{tag} 3 Catalysts 3 รายการ (WL2 · วันที่ผ่านแล้วแสดงเป็น 'ผ่านไปแล้ว' ไม่ซ่อน) · เรียงตามวัน (1 ก.ย. → 20 พ.ย. → ~10 ธ.ค.)", len(rows) == 3 and rows[0]["t"].startswith("1 ก.ย.") and rows[0]["past"] and "ผ่านไปแล้ว" in rows[0]["t"] and rows[1]["t"].startswith("20 พ.ย.") and rows[2]["t"].startswith("~10 ธ.ค."), json.dumps(rows, ensure_ascii=False))
        check(f"{tag} 3 estimated = '~10 ธ.ค.' + คลาสเส้นประ · confirmed ไม่มี", rows[2]["est"] and not rows[1]["est"], json.dumps(rows, ensure_ascii=False))
        # 4 ─ Blockers (WL2 · severe_risks เลิกใช้ — เหลือเฉพาะโน้ตของฉัน)
        bl = page.evaluate("()=>[...document.querySelectorAll('[data-wl-sec=blk] li')].map(l=>l.innerText.trim())")
        check(f"{tag} 4 สิ่งที่ต้องระวัง: ไม่มีข้อจาก Research แล้ว (0 ข้อ · ไม่มี '+ อีก n ข้อ') — เหลือเฉพาะโน้ตของฉัน", len(bl) == 0 and n(page, "[data-wl-more]") == 0, json.dumps(bl, ensure_ascii=False))
        # 5 ─ Tripwire (WL2 · แท็บ ออกเมื่อ)
        page.evaluate("()=>wlSetSub('exit')"); page.wait_for_timeout(250)
        tw = page.evaluate("()=>[...document.querySelectorAll('[data-lt-tw]')].map(e=>({lv:e.dataset.ltTw, t:e.querySelector('.s').innerText.trim(), v:e.querySelector('.n').innerText.trim()}))")
        check(f"{tag} 5 Tripwire 2 แถว review/watch (review ก่อน) · 'ตอนนี้: {{now}}' ในบรรทัดรอง",
              len(tw) == 2 and tw[0]["lv"] == "review" and tw[1]["lv"] == "watch" and tw[0]["v"].startswith("ตอนนี้: ~55% (Q3)") and tw[1]["v"].startswith("ตอนนี้: Q3 = 16.7B"), json.dumps(tw, ensure_ascii=False))
        page.evaluate("()=>wlSetSub('sum')"); page.wait_for_timeout(250)
        ft = txt(page, ".wlFoot") or ""
        check(f"{tag} 5 ท้ายแท็บ สรุป: 'ข้อมูล ณ 28 ก.ย.' · Note · Industry", ft.startswith("ข้อมูล ณ 28 ก.ย.") and "Note: ถือยาว ดูงบ Q4 ก่อนเติม" in ft and "Semis" in ft, ft)
        check(f"{tag} 5 ลำดับส่วนในแท็บ สรุป: ชิป → แถบเตือน → กล่องตัดสินใจ → รายการสรุป → ท้ายการ์ด",
              page.evaluate("""()=>{ const o=['.ltChips','[data-wl-alert]','[data-lt-decide]','.ltSum','.wlFoot'].map(s=>document.querySelector(s));
                return o.every(Boolean) && o.every((e,i)=>i==0 || (o[i-1].compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING)); }"""))
        open_ov(page, "AVGO", "trk")
        # 6 ─ โน้ตของฉัน
        page.click('[data-wl-addnote="cat"]'); page.wait_for_timeout(150)
        check(f"{tag} 6 ＋ โน้ต (catalyst) → ฟอร์มเล็ก มีช่องข้อความ + ช่องวันที่ type=date + บันทึก/ยกเลิก", n(page, '[data-wl-noteform="cat"] #wlNoteText') == 1 and page.get_attribute("#wlNoteDate", "type") == "date" and "บันทึก" in (txt(page, "[data-wl-noteform]") or "") and "ยกเลิก" in (txt(page, "[data-wl-noteform]") or ""))
        shot_el(page, ".wlDBody", f"wl1-note-form-{w}.png")
        page.fill("#wlNoteDate", "2026-11-01"); page.fill("#wlNoteText", "ลูกค้า XPU รายใหม่ประกาศใช้"); page.press("#wlNoteText", "Enter"); page.wait_for_timeout(350)
        dn = (wl_doc(page, "AVGO") or {}).get("my_notes") or {}
        check(f"{tag} 6 Enter = บันทึก → doc my_notes.cat มี 1 (text + date 2026-11-01) · ฟอร์มปิด", len(dn.get("cat", [])) == 1 and dn["cat"][0]["text"] == "ลูกค้า XPU รายใหม่ประกาศใช้" and dn["cat"][0]["date"] == "2026-11-01" and n(page, "[data-wl-noteform]") == 0, json.dumps(dn, ensure_ascii=False))
        rows = page.evaluate("()=>[...document.querySelectorAll('[data-wl-sec=cat] li')].map(l=>({t:l.innerText.replace(/\\s+/g,' ').trim(), me:l.classList.contains('wlMe'), tag:!!l.querySelector('.wlMeTag')}))")
        col = page.evaluate("()=>{ const e=document.querySelector('.wlMe .wlLiT'); return e ? getComputedStyle(e).color : null; }")
        check(f"{tag} 6 แสดง 4 แถว (WL2 · รวมงานที่ผ่านแล้ว) · โน้ตเรียงก่อน 20 พ.ย. (1 พ.ย. ต่อจาก 1 ก.ย.) · ป้าย 'โน้ตของฉัน' · สีม่วง", len(rows) == 4 and rows[1]["me"] and rows[1]["tag"] and "1 พ.ย." in rows[1]["t"] and "โน้ตของฉัน" in rows[1]["t"] and col == "rgb(107, 79, 200)", json.dumps([rows, col], ensure_ascii=False))
        page.click('[data-wl-addnote="cat"]'); page.fill("#wlNoteText", "ไม่มีวัน"); page.click("[data-wl-noteform] button.primary"); page.wait_for_timeout(300)
        rows = page.evaluate("()=>[...document.querySelectorAll('[data-wl-sec=cat] li')].map(l=>l.innerText.replace(/\\s+/g,' ').trim())")
        check(f"{tag} 6 โน้ตไม่มีวัน = '—' อยู่ท้ายรายการ", len(rows) == 5 and rows[-1].startswith("—") and "ไม่มีวัน" in rows[-1], json.dumps(rows, ensure_ascii=False))
        page.click('[data-wl-addnote="cat"]'); page.fill("#wlNoteText", "   "); page.press("#wlNoteText", "Enter"); page.wait_for_timeout(250)
        check(f"{tag} 6 ข้อความว่าง + Enter = ปิดฟอร์ม ไม่บันทึก", n(page, "[data-wl-noteform]") == 0 and len((wl_doc(page, "AVGO")["my_notes"]["cat"])) == 2)
        page.click('[data-wl-addnote="blk"]'); page.wait_for_timeout(100)
        check(f"{tag} 6 ＋ โน้ต (blocker) → ไม่มีช่องวันที่", n(page, '[data-wl-noteform="blk"]') == 1 and n(page, "#wlNoteDate") == 0)
        page.fill("#wlNoteText", "ราคาไม่ควรหลุด 280"); page.press("#wlNoteText", "Enter"); page.wait_for_timeout(300)
        dn = wl_doc(page, "AVGO")["my_notes"]
        bl = page.evaluate("()=>[...document.querySelectorAll('[data-wl-sec=blk] li')].map(l=>({t:l.innerText.replace(/\\s+/g,' ').trim(), me:l.classList.contains('wlMe')}))")
        check(f"{tag} 6 doc my_notes.blk มี 1 · สิ่งที่ต้องระวัง = 1 โน้ต (ม่วง · WL2 ไม่มีข้อจากการ์ดแล้ว)", len(dn["blk"]) == 1 and len(bl) == 1 and bl[0]["me"] and n(page, "[data-wl-more]") == 0, json.dumps([dn, bl], ensure_ascii=False))
        shot_el(page, ".wlDBody", f"wl1-overview-notes-{w}.png")
        page.click('[data-wl-sec=blk] .wlMe .wlNoteX'); page.wait_for_timeout(250)
        page.click('[data-wl-sec=cat] .wlMe .wlNoteX'); page.wait_for_timeout(250)
        page.click('[data-wl-sec=cat] .wlMe .wlNoteX'); page.wait_for_timeout(300)
        dn = wl_doc(page, "AVGO")["my_notes"]
        check(f"{tag} 6 × ลบ → หายจาก doc และจอ (blk 0 · cat 0 · ไม่มีแถวโน้ต)", dn["blk"] == [] and dn["cat"] == [] and n(page, ".wlMe") == 0, json.dumps(dn, ensure_ascii=False))
        # 7 ─ Import Thesis ฉบับใหม่ (WL2 · เดิม นำเข้า Research Card ใหม่ rcMerge) → โน้ตไม่หาย
        page.click('[data-wl-addnote="blk"]'); page.fill("#wlNoteText", "โน้ตรอดการนำเข้า"); page.press("#wlNoteText", "Enter"); page.wait_for_timeout(300)
        inc = copy.deepcopy(dump(page)["users/testuid/watchlist/AVGO"]["thesis"]); inc["date"] = "2026-09-30"; inc["asOf"] = "2026-09-30"; inc["log"] = [{"date": "2026-09-30", "new": "ปรับข้อมูล", "changed": "-", "impact": "-", "decision": "watch"}]
        page.click('[data-lt-import][data-sym="AVGO"]'); page.wait_for_selector("#ltJson", state="visible"); page.fill("#ltJson", json.dumps(inc, ensure_ascii=False)); page.click("[data-lt-check]"); page.wait_for_timeout(150)
        page.click("[data-lt-save]"); page.wait_for_timeout(500)
        open_ov(page, "AVGO", "trk")
        check(f"{tag} 7 Import Thesis ใหม่ → วันที่ Thesis 2026-09-30 · โน้ตของฉันยังอยู่ทั้งใน doc และบนจอ", (wl_doc(page, "AVGO")["thesis"]["date"] == "2026-09-30") and "โน้ตรอดการนำเข้า" in ov(page) and (wl_doc(page, "AVGO")["my_notes"]["blk"] or [{}])[0].get("text") == "โน้ตรอดการนำเข้า")
        # 8 ─ NOCARD
        open_ov(page, "NOCARD")
        check(f"{tag} 8 NOCARD: การ์ด 'ยังไม่มี Thesis' (WL2 · เดิมชิปเหลือง 'รอสร้าง Research Card') · ไม่มี Catalysts/Tripwire (ว่าง) · ไม่มีแถบเตือน",
              "ยังไม่มี Thesis" in (txt(page, "[data-lt-empty]") or "") and n(page, "[data-lt-tw]") == 0 and n(page, "[data-wl-sec=cat] li") == 0 and n(page, "[data-wl-alert]") == 0 and n(page, "[data-lt-chip]") == 0)
        page.click('[data-wl-addnote="cat"]'); page.fill("#wlNoteText", "รอข่าว NOCARD"); page.press("#wlNoteText", "Enter"); page.wait_for_timeout(300)
        check(f"{tag} 8 NOCARD ยังเพิ่มโน้ตได้ (doc my_notes.cat 1)", len((wl_doc(page, "NOCARD") or {}).get("my_notes", {}).get("cat", [])) == 1 and "รอข่าว NOCARD" in ov(page))
        shot_el(page, ".wlDBody", f"wl1-nocard-{w}.png")
        # 9 ─ CAND1
        open_cand(page, "CAND1")
        check(f"{tag} 9 CAND1 (candidate): ไม่มีปุ่ม ＋ โน้ต · ไม่มีชิป Screen (WL4: เดิมมี 'Screen 9/15') · ไม่มีส่วนโน้ต", n(page, "[data-wl-addnote]") == 0 and "Screen" not in (txt(page, ".ltChips") or "") and n(page, "[data-wl-note]") == 0, txt(page, ".ltChips") or "")
        # 10 ─ ช่องเช็ก Tier (WL2 · เติมจาก Thesis แทนช่องเช็กในแท็บ Research): thesis.tier_inputs → ติ๊ก 3 ช่อง
        def fill_chk(tk):
            page.evaluate("()=>{ switchTab('plan'); }"); page.wait_for_timeout(150)
            page.evaluate("(a)=>coreNewOpen(a)", "main"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
            page.fill("#cnTicker", tk); page.wait_for_timeout(120); page.click("#tiFillTh"); page.wait_for_timeout(150)
            r = page.evaluate("()=>Object.fromEntries(['fcf3y','capret','ocf'].map(k=>[k,(()=>{ const on=[...document.querySelectorAll('[data-tk=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; })()]))")
            page.evaluate("()=>coreSheetClose()"); page.wait_for_timeout(100); return r
        v1 = fill_chk("AVGO")
        check(f"{tag} 10 เติมจาก Thesis AVGO: ช่องเช็ก Tier = FCF 3 ปี ✓ · ปันผล/ซื้อคืน ✓ · OCF ✓", v1 == {"fcf3y": True, "capret": True, "ocf": True}, json.dumps(v1))
        d = copy.deepcopy(dump(page)["users/testuid/watchlist/AVGO"]["thesis"]); d["tier_inputs"]["capitalReturn"]["v"] = False; d["tier_inputs"]["ocfPositive"]["v"] = None
        put_thesis(page, "AVGO", d)
        v2 = fill_chk("AVGO")
        check(f"{tag} 10 ค่า yes/no/? → FCF 3 ปี ✓ · ปันผล/ซื้อคืน ✗ · OCF ? (ยังไม่ตอบ) · thesis ใน doc ไม่ถูกแก้ด้วยการเติม", v2 == {"fcf3y": True, "capret": False, "ocf": None} and dump(page)["users/testuid/watchlist/AVGO"]["thesis"]["tier_inputs"]["capitalReturn"]["v"] is False, json.dumps(v2))
        # 11 ─ ค่าตั้ง SR1
        hint = page.evaluate("()=>{ const e=document.getElementById('satHeatHint'); return e ? e.textContent : null; }")
        if not hint:
            page.evaluate("()=>{ try{ openSystemSettings(); }catch(e){} try{ if(typeof renderSatRisk==='function') renderSatRisk(); }catch(e){} }"); page.wait_for_timeout(200)
            hint = page.evaluate("()=>{ const e=document.getElementById('satHeatHint'); return e ? e.textContent : null; }")
        src_ok = "ด้านล่างในกล่องนี้" in open(INDEX, encoding="utf-8").read()
        check(f"{tag} 11 #satHeatHint มีคำ 'ด้านล่างในกล่องนี้' (SET1) (ในหน้าจริงถ้าวาดแล้ว + ในโค้ด)", src_ok and (not hint or "ด้านล่างในกล่องนี้" in hint) and "ด้านบน" not in (hint or ""), hint or "(ยังไม่วาด)")
        page.evaluate("()=>{ const o=document.getElementById('sysOverlay'); if(o) o.classList.remove('show'); }")
        # 12 ─ FQC ออกหมด
        src = open(INDEX, encoding="utf-8").read()
        hits = [l for l in src.split("\n") if re.search(r"fqc", l, re.I)]
        check(f"{tag} 12 grep fqc/FQC ใน index.html = 0 (ยกเว้นคอมเมนต์ประวัติ 1 บรรทัด)", len(hits) == 1 and "WL1 — FQC เลิกใช้ 1 ต.ค. 2569" in hits[0], json.dumps(hits[:3], ensure_ascii=False))
        check(f"{tag} 12 ไม่มี wlEntryChip / 'เกณฑ์ลงทุนเดิม' ในโค้ด", "wlEntryChip" not in src and "เกณฑ์ลงทุนเดิม" not in src)
        body_all = ""
        for tk in ("AVGO", "CALM", "NOCARD"):
            open_ov(page, tk); body_all += (txt(page, "body") or "")
        page.evaluate("()=>wlSetView('cand')"); page.wait_for_timeout(200); body_all += (txt(page, "body") or "")
        check(f"{tag} 12 ไม่มีชิป 'เกณฑ์ลงทุนเดิม…' / 'FQC' ทุกหน้า (Overview ทุกตัว + รายการ Candidates)", "เกณฑ์ลงทุนเดิม" not in body_all and "FQC" not in body_all)
        open_ov(page, "AVGO")
        page.evaluate("()=>wlOpenEdit('AVGO')"); page.wait_for_timeout(200); page.fill("#wlAddNote", "แก้โน้ตหลังตัด FQC"); page.evaluate("()=>wlAddSave()"); page.wait_for_timeout(400)
        dd = dump(page)
        check(f"{tag} 12 แก้หุ้น+บันทึก doc → ฟิลด์ fqc ใน watchlist/AVGO และ research/AVGO ยังอยู่ (ไม่ลบ/ไม่เขียนทับ) · investment_clearance ยังอยู่",
              dd["users/testuid/watchlist/AVGO"].get("fqc") == FQC and dd["research/AVGO"].get("fqc") == FQC and dd["research/AVGO"].get("investment_clearance") == IC and dd["users/testuid/watchlist/AVGO"]["note"] == "แก้โน้ตหลังตัด FQC")
        put_research(page, "OLDF", {"fqc": FQC, "growth_gate": {"x": 1}}); put_research(page, "OLDG", {"name": "ไม่มี ticker", "fqc": FQC})
        ok_old = page.evaluate("() => rsLoad(true).then(()=>{ try{ switchTab('watch'); renderWatchlist(); return true; }catch(e){ return String(e); } })"); page.wait_for_timeout(300)
        check(f"{tag} 12 doc เก่าที่มีแค่ fqc (ไม่มี ticker/research_card) → หน้าไม่พัง", ok_old is True and n(page, "#mainWrap") == 1)
        # 13 ─ ไม่ล้น + console
        open_ov(page, "AVGO", "trk")
        page.click('[data-wl-addnote="cat"]'); page.fill("#wlNoteText", "โน้ตยาวมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมากมาก ที่ต้องตัดบรรทัดไม่ล้นจอ"); page.fill("#wlNoteDate", "2026-11-05")
        bad_form = overflow(page)
        page.press("#wlNoteText", "Enter"); page.wait_for_timeout(300)
        bad_rows = overflow(page)
        chips = page.evaluate("()=>[...document.querySelectorAll('.wlDt')].map(e=>{ const r=e.getBoundingClientRect(); return r.right <= window.innerWidth + 1; }).every(Boolean)")
        check(f"{tag} 13 Overview ไม่ล้นแนวนอน: ฟอร์มโน้ต · แถวโน้ต · ชิปวันที่ (เช็กราย element)", not bad_form and not bad_rows and chips and page.evaluate("()=>document.documentElement.scrollWidth <= window.innerWidth + 1"), json.dumps([bad_form, bad_rows, chips]))
        check(f"{tag} 13 ไม่มี console/page error", not ce and not pe, json.dumps([ce[:3], pe[:3]]))
        check(f"{tag} 13 ไม่มี alert/dialog ค้าง", not dialogs, json.dumps(dialogs))
    finally:
        context.close(); browser.close()


def main():
    with sync_playwright() as pw:
        checks(pw, 1440, 900, "1440px")
        checks(pw, 430, 932, "430px")
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 35 / WL1) ====")
    print(f"engine=chromium  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail or "")[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
