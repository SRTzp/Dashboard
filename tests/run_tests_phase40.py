#!/usr/bin/env python3
"""WL2 — การ์ด Watchlist v2 (Living Thesis · living-thesis@1) + ลบ Research Card ทั้งระบบ · เทส 40
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม = 2026-10-02 13:03 ไทย (ศุกร์) · timezone Asia/Bangkok · fixture tests/fixtures/avgo_thesis.json
ภาพเก็บที่ tests/screenshots/wl2-*.png (sum · trk-open · exit-hit · import-diff · no-thesis · today · tier-fill × 1440/390)
รัน: python3 run_tests_phase40.py"""
import copy, json, os, re, sys
from playwright.sync_api import sync_playwright
import run_tests_phase38 as P
import run_tests_phase39 as P39

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = P.base.BROWSER_ENGINE
CLK = P39.CLK
FX = json.load(open(os.path.join(HERE, "fixtures", "avgo_thesis.json"), encoding="utf-8"))
results = []
js, dump = P.js, P.dump
BAD_TXT = ["undefined", "null", "[object", "<span", "<b>", "</", "&amp;", "&lt;", "&gt;", "&#39;", "**", "###"]


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...(truncated)") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name):
    page.wait_for_timeout(700)
    try: page.screenshot(path=os.path.join(SHOTS, name), full_page=True)
    except Exception as e: print("shot fail", name, e)


def fx(sym="AVGO", **mods):
    d = copy.deepcopy(FX); d["sym"] = sym
    for k, v in mods.items(): d[k] = v
    return d


def seed(page, path, d): page.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [path, d])


def wl_doc(th=None, log=None, hits=None, hist=None, **kw):
    d = {"ticker": kw.pop("ticker", "AVGO"), "market": "US", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"}
    if th is not None:
        t = {k: v for k, v in th.items() if k != "log"}
        d["thesis"] = t; d["thesis_log"] = log if log is not None else th.get("log", []); d["thesis_history"] = hist or []; d["thesis_hits"] = hits or {}
    d.update(kw); return d


def promoted(page, sym, mk="US"):
    """TD4a — Import สร้างเอกสาร Watchlist ใหม่ไม่ได้แล้ว: ตั้งต้นด้วยตัวที่ย้ายเข้า Watchlist มาก่อน (เอกสารเปล่า)"""
    seed_wl(page, sym, market=mk, added_at="2026-10-01T00:00:00.000Z"); page.evaluate("()=>{ wlStop(); wlStart(); }"); page.wait_for_timeout(600)


def seed_wl(page, sym, th=None, **kw): seed(page, ["users", "testuid", "watchlist", sym], wl_doc(th, ticker=sym, **kw))


def launch(pw, w, h, extra=None, iso=CLK, init_js=None):
    """P39.launch (clean) + extra(page) seed ก่อน login · init_js = สคริปต์ก่อนโหลดหน้า (เช่น ตั้ง localStorage)"""
    return P39.launch(pw, w, h, doc=P.doc38(clean=True, log={}), clean=True, iso=iso, extra=extra)


def wdb(page): return {k.split("/")[-1]: v for k, v in dump(page).items() if k.startswith("users/testuid/watchlist/")}


def go_watch(page, sym=None, sub=None):
    js(page, "()=>switchTab('watch')"); page.wait_for_timeout(250)
    if sym: js(page, "([s,b])=>wlOpen(s,b)", [sym, sub]); page.wait_for_timeout(250)


def body_txt(page): return js(page, "()=>{ const e = document.querySelector('.wlDBody'); return e ? e.innerText.replace(/\\s+/g,' ').trim() : ''; }")
def txt_of(page, sel): return js(page, "(s)=>{ const e = document.querySelector(s); return e ? e.innerText.replace(/\\s+/g,' ').trim() : null; }", sel)
def cnt(page, sel): return js(page, "(s)=>document.querySelectorAll(s).length", sel)
def sub_now(page): return js(page, "()=>wlSub")
def tab(page, k): page.click(f'[data-lt-tab="{k}"]'); page.wait_for_timeout(150)


def import_via_ui(page, text, top=True, bound_sym=None, save=True):
    """เปิด sheet Import (แถบบน หรือหัวการ์ด) · วาง · ตรวจ · (บันทึก) → คืน (err, preview)"""
    page.click('[data-lt-import-top]' if top else f'[data-lt-import][data-sym="{bound_sym}"]'); page.wait_for_selector("#ltJson", state="visible")
    page.fill("#ltJson", text); page.click("[data-lt-check]"); page.wait_for_timeout(120)
    err = txt_of(page, "#ltErr") or ""; prev = txt_of(page, "#ltPrev") or ""
    if save and not err and page.locator("[data-lt-save]").is_visible():
        page.click("[data-lt-save]"); page.wait_for_timeout(500)
    return err, prev


def fenced(d): return "นี่คือผลจาก living-thesis ครับ:\n```json\n" + json.dumps(d, ensure_ascii=False, indent=1) + "\n```\nจบ ขอบคุณ"


# ───────────────────────── 1–9 Import · การ์ด · tripwire ─────────────────────────
def main_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_watch(page)
        # 1 ─ Import AVGO (fence + ข้อความหน้าหลัง)
        check(f"{tag} 1 แถบบนหน้า Watch มีปุ่ม 📥 Import (ไม่ผูก ticker)", cnt(page, "[data-lt-import-top]") == 1)
        promoted(page, "AVGO")
        err, prev = import_via_ui(page, fenced(FX), top=True)
        d = wdb(page).get("AVGO") or {}
        check(f"{tag} 1 Import (วางมี ```json + ข้อความหน้า/หลัง) → ไม่มี error", err == "" and "ตรวจผ่าน" in prev, err + prev)
        check(f"{tag} 1 doc watchlist/AVGO มี thesis (ไม่มี log) · thesis_log 1 บรรทัด · thesis_hits ว่าง", "log" not in d.get("thesis", {"log": 1}) and d.get("thesis", {}).get("schema") == "living-thesis@1" and len(d.get("thesis_log", [])) == 1 and d.get("thesis_hits") == {} and d.get("thesis_history") == [], json.dumps(list(d.keys())))
        check(f"{tag} 1 doc ใหม่ port=core market=US", d.get("port") == "core" and d.get("market") == "US" and str(d.get("added_at", "")).startswith("2026-10-0"), json.dumps({k: d.get(k) for k in ("port", "market", "added_at")}))
        check(f"{tag} 1 หลัง Import เปิดการ์ด AVGO ทันที · 6 แท็บ (VW1)", js(page, "()=>wlSel") == "AVGO" and [e for e in js(page, "()=>[...document.querySelectorAll('[data-lt-tab]')].map(e=>e.dataset.ltTab)")] == ["sum", "view", "biz", "why", "trk", "exit"])
        bad_all = {}
        for k in ("sum", "biz", "why", "trk", "exit"):
            tab(page, k)
            t = body_txt(page)
            bad = [b for b in BAD_TXT if b in t and not (b == "</" and False)]
            bad_all[k] = bad
        # ข้อความจริงใน AVGO มี "<" เฉยๆ ได้ แต่ไม่มี tag หลุด
        check(f"{tag} 1 ทั้ง 5 แท็บ: ไม่มี HTML หลุด / undefined / null / [object / ** / ###", all(not v for v in bad_all.values()), json.dumps(bad_all))
        tab(page, "sum")
        shot(page, f"wl2-sum-{sfx}.png")

        # 6 ─ แท็บ สรุป
        order = js(page, """()=>{ const p = document.querySelector('.wlDBody .wlOv'); return [...p.children].map(e=>e.matches('[data-lt-decide]')?'decide':e.matches('[data-wl-alert]')?'alert':e.matches('.ltSum')?'sum':e.tagName.toLowerCase()); }""")
        check(f"{tag} 6 กล่องตัดสินใจอยู่บนสุด (ก่อนรายการ label→ค่า)", order[0] == "decide" and "sum" in order and order.index("sum") > 0, json.dumps(order))
        dec = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-lt-decide] [data-lt-k]')].map(e=>[e.dataset.ltK, e.innerText.replace(/\\s+/g,' ').trim()]))")
        check(f"{tag} 6 กล่อง 3 บรรทัด: ข้อสรุป ศึกษาต่อ · Thesis breaker · ถัดไป", list(dec) == ["call", "breaker", "next"] and dec["call"].startswith("ข้อสรุป ศึกษาต่อ") and dec["breaker"].startswith("Thesis breaker AI rev Q4") and dec["next"].startswith("ถัดไป งบ Q4 FY26"), json.dumps(dec, ensure_ascii=False))
        nx = txt_of(page, "[data-lt-nxc]") or ""
        check(f"{tag} 6 บรรทัด 📅 = ~10 ธ.ค. · อีก 69 วัน · +1", "~10 ธ.ค. · อีก 69 วัน" in nx and "+1" in nx, nx)
        labels = js(page, "()=>[...document.querySelectorAll('.ltSum dt')].map(e=>e.innerText.trim())")
        check(f"{tag} 6 รายการ label→ค่า เรียง ธุรกิจ · Thesis · ความเสี่ยง #1 · ราคา · Life cycle · Power (moat) · Capital allocation · Unknown", labels == ["ธุรกิจ", "Thesis", "ความเสี่ยง #1", "ราคา", "Life cycle", "Power (moat)", "Capital allocation", "Unknown"], json.dumps(labels, ensure_ascii=False))
        chips = txt_of(page, "[data-lt-chips]") or ""
        check(f"{tag} 6 หัวการ์ด: ชิป Thesis lite · 2 ต.ค. + ชิปสถานะ เฝ้าดู + tier_note · ไม่มี ⚠ ควร update", "Thesis lite · 2 ต.ค." in chips and "เฝ้าดู" in chips and cnt(page, "[data-lt-stale]") == 0 and "ROIC ~15.5%" in (txt_of(page, "[data-lt-tiernote]") or ""), chips)
        # โน้ต cat วันที่ 2026-10-05
        tab(page, "trk")
        js(page, "()=>wlNoteOpen('AVGO','cat')"); page.wait_for_selector("#wlNoteText")
        page.fill("#wlNoteDate", "2026-10-05"); page.fill("#wlNoteText", "ประชุมผู้ถือหุ้น"); js(page, "()=>wlNoteSave()"); page.wait_for_timeout(400)
        tab(page, "sum")
        nx = txt_of(page, "[data-lt-nxc]") or ""; soon = js(page, "()=>document.querySelector('[data-lt-nxc]').classList.contains('soon')")
        check(f"{tag} 6 เพิ่มโน้ต cat 5 ต.ค. → 📅 เป็นโน้ตนั้น อีก 3 วัน · สีเหลือง · +2", "5 ต.ค. · อีก 3 วัน" in nx and "ประชุมผู้ถือหุ้น" in nx and soon and "+2" in nx, nx)
        page.click("[data-lt-nxc]"); page.wait_for_timeout(200)
        check(f"{tag} 6 กดบรรทัด 📅 → แท็บ ติดตาม", sub_now(page) == "trk" and js(page, "()=>document.querySelector('[data-lt-tab=trk]').classList.contains('on')"))

        # 8 ─ แท็บ ติดตาม
        secs = js(page, """()=>[...document.querySelectorAll('.wlDBody [data-wl-sec],.wlDBody [data-lt-sec]')].map(e=>e.dataset.wlSec ? 'wl:'+e.dataset.wlSec : 'lt:'+e.dataset.ltSec)""")
        check(f"{tag} 8 ลำดับหัวข้อ: catalysts → ระวัง → KPI → must", secs == ["wl:cat", "wl:blk", "lt:kpi", "lt:must"], json.dumps(secs))
        n_must = js(page, "()=>{ const s = document.querySelector('[data-lt-sec=must]'); return s.querySelectorAll('tbody tr, tr').length ? [...s.querySelectorAll('tr')].length - 1 : s.querySelectorAll('.ltStk').length; }")
        if w > 480: n_must = js(page, "()=>[...document.querySelector('[data-lt-sec=must]').querySelectorAll('tr')].length - 1")
        else: n_must = js(page, "()=>document.querySelector('[data-lt-sec=must]').querySelectorAll('.ltStk').length")
        check(f"{tag} 8 gaps must 3 ตัว", n_must == 3, str(n_must))
        folds = js(page, "()=>Object.fromEntries([...document.querySelectorAll('[data-lt-fold]')].map(e=>[e.dataset.ltFold, e.querySelector('.ltCnt').innerText.trim()]))")
        check(f"{tag} 8 แถบพับ 3 แถบพร้อมจำนวน (3 ข้อ · 3.1–3.4 · 1 รายการ) + หลักฐาน 17 · 8", folds.get("gap2") == "3 ข้อ" and folds.get("s3") == "3.1–3.4" and folds.get("log") == "1 รายการ" and folds.get("evd") == "17 · 8", json.dumps(folds, ensure_ascii=False))
        hts = js(page, "()=>[...document.querySelectorAll('.ltFoldBar')].map(e=>Math.round(e.getBoundingClientRect().height))")
        check(f"{tag} 8 แถบพับสูง ≥ 44px · ค่าเริ่มต้นพับ (aria-expanded=false)", all(x >= 44 for x in hts) and js(page, "()=>[...document.querySelectorAll('.ltFoldBar')].every(e=>e.getAttribute('aria-expanded')==='false')"), json.dumps(hts))
        page.click('[data-lt-fold="gap2"] .ltFoldBar'); page.wait_for_timeout(150)
        a1 = js(page, "()=>document.querySelector('[data-lt-fold=gap2] .ltFoldBar').getAttribute('aria-expanded')")
        page.click('[data-lt-fold="gap2"] .ltFoldBar'); page.wait_for_timeout(150)
        a2 = js(page, "()=>document.querySelector('[data-lt-fold=gap2] .ltFoldBar').getAttribute('aria-expanded')")
        check(f"{tag} 8 กดแถบ = กาง (aria-expanded=true) · กดซ้ำ = พับ", a1 == "true" and a2 == "false", f"{a1}/{a2}")
        for k in ("gap2", "s3", "log"): page.click(f'[data-lt-fold="{k}"] .ltFoldBar'); page.wait_for_timeout(100)
        shot(page, f"wl2-trk-open-{sfx}.png")
        if w > 480:
            page.click('[data-lt-fold="evd"] .ltFoldBar'); page.wait_for_timeout(150)
            wide = js(page, "()=>[...document.querySelectorAll('.wlDBody .ltTw')].map(w=>{ const t = w.querySelector('table'), a = w.getBoundingClientRect(), b = t.getBoundingClientRect(); return b.right > a.right + 1 ? [Math.round(a.right), Math.round(b.right)] : null; }).filter(Boolean)")
            check(f"{tag} 8 ตาราง gaps/KPI/Milestones/Log/หลักฐาน บนจอใหญ่ตัดบรรทัดในกรอบ (ไม่กว้างเกิน wrapper — ทับกฎ td nowrap รวมของแอป)", not wide, json.dumps(wide))
            page.click('[data-lt-fold="evd"] .ltFoldBar'); page.wait_for_timeout(100)
        for k in ("gap2", "s3", "log"): page.click(f'[data-lt-fold="{k}"] .ltFoldBar'); page.wait_for_timeout(100)

        # 7 ─ renderer
        tab(page, "why")
        r2 = js(page, "()=>({ol: document.querySelectorAll('.ltMd ol li').length, tbl: document.querySelectorAll('.ltTw table').length, tg: document.querySelectorAll('.ltTg.F, .ltTg.C').length, wrap: getComputedStyle(document.querySelector('.ltTw')).overflowX})")
        check(f"{tag} 7 ทำไมซื้อ: `1.` เป็น <ol> 3 ข้อ · ตารางอยู่ใน wrapper overflow-x:auto · ป้าย [F]/[C] เป็น chip", r2["ol"] == 3 and r2["tbl"] >= 1 and r2["wrap"] == "auto" and r2["tg"] > 0, json.dumps(r2))
        tab(page, "biz")
        r1 = js(page, "()=>({tbl: document.querySelectorAll('.ltMd .ltTw table').length, emptyLi: [...document.querySelectorAll('.ltMd li')].filter(e=>!e.textContent.trim()).length, tgF: document.querySelectorAll('.ltTg.F').length, bq: document.querySelectorAll('.ltMd blockquote').length})")
        check(f"{tag} 7 ธุรกิจ: ตาราง 1.2 เป็น <table> ใน wrapper · quote · [F] chip · ไม่มี <li> ว่าง", r1["tbl"] >= 2 and r1["tgF"] > 0 and r1["emptyLi"] == 0 and r1["bq"] > 0, json.dumps(r1))
        md = js(page, "(s)=>ltMd(s)", "### หัว\n- \n- ข้อ **หนา** [F] [C] [M] [I] [A] [?]\n-\n* ดอก\n1. หนึ่ง\n2. สอง\n> คำพูด\n\n| a | b |\n|---|---|\n| 1 | 2 |\n\nย่อหน้า <img src=x onerror=alert(1)>")
        check(f"{tag} 7 ltMd(): bullet ว่างข้าม · bold · ป้ายทุกสี · quote · ตาราง (ข้ามแถว |---|) · escape HTML", md.count("<li>") == 4 and "<b>หนา</b>" in md and all(f'ltTg {c}"' in md for c in "FCMIAQ") and md.count("<tr>") == 2 and "&lt;img" in md and "<img" not in md and "<ol>" in md and "<blockquote>" in md, md)

        # 9 ─ แท็บ ออกเมื่อ + ชนแล้ว
        tab(page, "exit")
        lv = js(page, "()=>[...document.querySelectorAll('[data-lt-tw]')].filter(e=>e.offsetParent!==null).map(e=>e.dataset.ltTw)")
        okbar = js(page, "()=>{ const f = document.querySelector('[data-lt-fold=ok]'); return f ? f.querySelector('.ltFoldBar').innerText.replace(/\\s+/g,' ').trim() : null; }")
        check(f"{tag} 9 แสดง watch 3 ตัว · แถบ ✓ ปกติ (ok) 4 ข้อ", lv == ["watch"] * 3 and okbar and "ปกติ (ok)" in okbar and "4 ข้อ" in okbar, json.dumps([lv, okbar], ensure_ascii=False))
        check(f"{tag} 9 ยังไม่กด: เลขบนแท็บ ออกเมื่อ = ไม่มี · ไม่มีแถบแดงใน สรุป", cnt(page, "[data-lt-hotn]") == 0)
        first_sig = js(page, "()=>document.querySelector('[data-lt-tw] .s').innerText.trim()")
        page.click("[data-lt-hit]"); page.wait_for_timeout(500)
        d = wdb(page)["AVGO"]
        check(f"{tag} 9 กด 'ชนแล้ว' ข้อแรก → thesis_hits มี signal = วันนี้", d.get("thesis_hits") == {first_sig: "2026-10-02"}, json.dumps(d.get("thesis_hits"), ensure_ascii=False))
        lvl = txt_of(page, '[data-lt-tw="broken"] [data-lt-lv]') or ""
        check(f"{tag} 9 ป้าย 'broken · กดเอง' · เลขบนแท็บ = 1 · หัวการ์ด ⚠ ควร update", "broken · กดเอง" in lvl and txt_of(page, "[data-lt-hotn]") == "1" and cnt(page, "[data-lt-stale]") == 1, lvl)
        shot(page, f"wl2-exit-hit-{sfx}.png")
        tab(page, "sum")
        check(f"{tag} 9 แท็บ สรุป มีแถบแดง + แถบเหลือง 'ควรรัน living-thesis โหมด update … กด \"ชนแล้ว\" 1 ข้อ'", cnt(page, ".wlAlert.red[data-wl-alert]") == 1 and 'กด "ชนแล้ว" 1 ข้อ' in (txt_of(page, "[data-lt-stalebar]") or ""))
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(350)
        kinds = P.kinds(page, "r"); rt = P.rows_text(page, "r")
        check(f"{tag} 9 Today มีแถว 🔴 Tripwire ชนแล้ว AVGO → ทบทวนการถือ", any("AVGO Tripwire ชนแล้ว" in t and "ทบทวนการถือ" in t for t in rt), json.dumps(rt, ensure_ascii=False))
        if kinds:
            js(page, "()=>document.querySelector('.tdRow[data-kind=\"tw-confirmed\"]').click()"); page.wait_for_timeout(300)
            check(f"{tag} 9 กดแถว 🔴 → เปิดการ์ด AVGO แท็บ ออกเมื่อ", sub_now(page) == "exit" and js(page, "()=>wlSel") == "AVGO")
        go_watch(page, "AVGO", "exit")
        page.click("[data-lt-hit].on"); page.wait_for_timeout(400)
        d = wdb(page)["AVGO"]
        check(f"{tag} 9 กดยกเลิก → thesis_hits ว่าง · เลขบนแท็บ/⚠ หาย", d.get("thesis_hits") == {} and cnt(page, "[data-lt-hotn]") == 0 and cnt(page, "[data-lt-stale]") == 0)
        page.click("[data-lt-hit]"); page.wait_for_timeout(300)

        # 2 ─ Import ซ้ำ (log ใหม่ 1 + บรรทัดเดิม) · เซ็ตข้อมูลผู้ใช้ก่อน
        js(page, "()=>wlCol().doc('AVGO').update({tier:'A', tier_set_at:'2026-09-01', tier_lens:'both', tier_inputs:{roic:0.2, ndEbitda:1.1}, tier_reason:'x', note:'โน้ตเดิม', industry:'Semis', my_notes:wlNormNotes({cat:[{id:'n1',text:'ก',date:'2026-10-05'}], blk:[{id:'b1',text:'ข'}]})})"); page.wait_for_timeout(300)
        before = copy.deepcopy(wdb(page)["AVGO"])
        v2 = fx(); v2["date"] = "2026-12-11"; v2["summary"]["status"] = "deep"; v2["summary"]["thesis"][1] = "Software เปลี่ยนข้อความ"
        v2["tripwires"][0]["level"] = "review"; v2["catalysts"] = v2["catalysts"][:1]
        v2["log"] = FX["log"] + [{"date": "2026-12-11", "new": "งบ Q4 ออกแล้ว", "changed": "AI rev ตรง guide", "impact": "ไม่เปลี่ยน", "decision": "deep"}]
        # ยกเลิก = ไม่เขียน
        err, prev = import_via_ui(page, json.dumps(v2, ensure_ascii=False), top=False, bound_sym="AVGO", save=False)
        check(f"{tag} 2 diff แสดงก่อนยืนยัน: สถานะ เฝ้าดู → ศึกษาลึก · Thesis ข้อ 2 · tripwire ok → review · catalyst 2 → 1 · วันที่", err == "" and "เฝ้าดู → ศึกษาลึก" in prev and "เปลี่ยนข้อ 2" in prev and "ok → review" in prev and "2 → 1 รายการ" in prev and "2026-10-02 → 2026-12-11" in prev and "ล้างปุ่ม" in prev, prev)
        shot(page, f"wl2-import-diff-{sfx}.png")
        page.click("#ltOverlay .btns button:first-child"); page.wait_for_timeout(200)
        check(f"{tag} 2 ยกเลิก = DB ไม่เปลี่ยน", wdb(page)["AVGO"] == before)
        err, prev = import_via_ui(page, json.dumps(v2, ensure_ascii=False), top=False, bound_sym="AVGO", save=True)
        d = wdb(page)["AVGO"]
        check(f"{tag} 2 บันทึก: thesis_log = 2 (บรรทัดเดิมไม่ซ้ำ + ใหม่ 1) · thesis_history = 1 (ฉบับเดิม 2026-10-02) · thesis_hits ว่าง", len(d["thesis_log"]) == 2 and len(d["thesis_history"]) == 1 and d["thesis_history"][0]["date"] == "2026-10-02" and d["thesis_hits"] == {} and d["thesis"]["date"] == "2026-12-11", json.dumps([d["thesis_log"], d["thesis_history"], d["thesis_hits"]], ensure_ascii=False)[:600])
        keep = {k: d.get(k) for k in ("tier", "tier_set_at", "tier_lens", "tier_inputs", "tier_reason", "note", "industry", "my_notes", "added_at", "market", "port")}
        check(f"{tag} 2 ไม่แตะ tier* / note / industry / my_notes / added_at (tier_inputs ของ WT1 ไม่ถูกทับด้วย thesis.tier_inputs)", keep == {k: before.get(k) for k in keep} and d["tier_inputs"] == {"roic": 0.2, "ndEbitda": 1.1}, json.dumps(keep, ensure_ascii=False)[:400])

        # 15 ─ Export / ประวัติ
        js(page, "()=>{ window.__clip = null; Object.defineProperty(navigator,'clipboard',{value:{writeText:t=>{window.__clip=t; return Promise.resolve();}},configurable:true}); }")
        go_watch(page, "AVGO", "sum")
        page.click("[data-lt-menu]"); page.wait_for_timeout(150)
        hist_txt = txt_of(page, "[data-lt-history]") or ""
        check(f"{tag} 15 เมนู ⋯ มี Export JSON + ประวัติ (1) (หลังข้อ 2)", "ประวัติ (1)" in hist_txt and cnt(page, "[data-lt-export]") == 1, hist_txt)
        page.click("[data-lt-export]"); page.wait_for_timeout(300)
        clip = js(page, "()=>window.__clip")
        o = json.loads(clip) if clip else {}
        check(f"{tag} 15 Export → clipboard = JSON เต็ม schema ครบ · log = thesis_log (2 บรรทัด) · มีข้อความ 'คัดลอกแล้ว'", o.get("schema") == "living-thesis@1" and len(o.get("log", [])) == 2 and o.get("date") == "2026-12-11" and "คัดลอกแล้ว" in (txt_of(page, "[data-lt-menumsg]") or ""), (clip or "")[:200])
        page.click("[data-lt-history]"); page.wait_for_timeout(200)
        ht = txt_of(page, "#ltModal") or ""
        check(f"{tag} 15 ประวัติ: รายการ date + ข้อสรุป ของฉบับเดิม · อ่านอย่างเดียว", "2026-10-02" in ht and "ศึกษาต่อ" in ht and cnt(page, "#ltModal textarea") == 0, ht)
        page.click("#ltModal .btns button"); page.wait_for_timeout(150)

        # 16 ─ จำแท็บ · ลิงก์เก่า
        go_watch(page, "AVGO", "ov"); s_ov = sub_now(page)
        go_watch(page, "AVGO", "rs"); s_rs = sub_now(page)
        check(f"{tag} 16 ลิงก์เก่า wlOpen(T,'ov') / 'rs' → แท็บ สรุป", s_ov == "sum" and s_rs == "sum")
        tab(page, "exit")
        mem = js(page, "()=>JSON.parse(localStorage.getItem('wlSubMap')||'{}')")
        check(f"{tag} 16 จำแท็บต่อ ticker ใน localStorage (wlSubMap)", mem.get("AVGO") == "exit", json.dumps(mem))
        js(page, "()=>{ wlOpen('AVGO'); }"); page.wait_for_timeout(200)
        check(f"{tag} 16 เปิด AVGO ซ้ำโดยไม่ระบุแท็บ → กลับแท็บล่าสุด (ออกเมื่อ)", js(page, "()=>document.querySelector('[data-lt-tab=exit]').classList.contains('on')"))

        # 17 ─ เค้าโครงเฉพาะจอ
        if w <= 480:
            tab(page, "sum")
            vis = js(page, """()=>[...document.querySelectorAll('[data-lt-tab]')].map(b=>{ const r = b.getBoundingClientRect(); return [b.dataset.ltTab, Math.round(r.left), Math.round(r.right)]; })""")
            tabs_scroll = js(page, "()=>{ const t = document.querySelector('[data-lt-tabs]'); return t.scrollWidth > t.clientWidth + 1; }")
            ok_all = all(r >= 0 and l <= js(page, "()=>innerWidth") for _, l, r in vis) or tabs_scroll
            check(f"{tag} 17 390px: 6 แท็บมองเห็นครบ (VW1) หรือเลื่อนแนวนอนได้", ok_all and len(vis) == 6, json.dumps([vis, tabs_scroll]))
            for k in ("exit", "trk", "sum"):
                tab(page, k)
                inview = js(page, """()=>{ const b = document.querySelector('[data-lt-tab].on'), r = b.getBoundingClientRect(); return r.left >= -1 && r.right <= innerWidth + 1; }""")
                if not inview: break
            check(f"{tag} 17 แท็บที่เลือกอยู่ในจอเสมอ (เลื่อนให้เอง)", inview)
            tab(page, "trk")
            check(f"{tag} 17 gaps/kpi เป็นรายการซ้อน (.ltStk) ไม่ใช่ตาราง", cnt(page, '[data-lt-sec="must"] .ltStk') == 3 and cnt(page, '[data-lt-sec="must"] table') == 0 and cnt(page, '[data-lt-sec="kpi"] .ltStk') == 5 and cnt(page, '[data-lt-sec="kpi"] table') == 0)
        else:
            tab(page, "trk")
            check(f"{tag} 17 จอใหญ่: gaps/kpi เป็นตาราง", cnt(page, '[data-lt-sec="must"] table') == 1 and cnt(page, '[data-lt-sec="kpi"] table') == 1)
        tab(page, "exit"); page.click('[data-lt-fold="ok"] .ltFoldBar'); page.wait_for_timeout(150)
        ov = P.overflow_x(page, [".wlDBody", ".wlDPanel", ".ltFoldBar", ".ltTwr", ".ltDecide", ".ltTierNote", ".wlDHead"])
        check(f"{tag} 17 ไม่ล้นแนวนอน (หน้า + การ์ด)", not ov, json.dumps(ov))
        pts = js(page, """()=>{ const bad = []; ['.ltFoldBar','[data-lt-hit]'].forEach(s=>{ const e = document.querySelector(s); if(!e) return; e.scrollIntoView({block:'center'}); const r = e.getBoundingClientRect(), t = document.elementFromPoint(r.left + r.width/2, r.top + r.height/2); if(!(t===e || e.contains(t))) bad.push(s + ' → ' + (t && (t.className||t.tagName))); }); return bad; }""")
        check(f"{tag} 17 elementFromPoint ของแถบพับ/ปุ่มชนแล้ว = ตัวมันเอง", not pts, json.dumps(pts))
        check(f"{tag} 17 ไม่มี console error / pageerror", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────────────────────── 3–5 ผิด · XSS · ticker ใหม่ ─────────────────────────
def error_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=lambda p: seed_wl(p, "AVGO", fx()))
    try:
        go_watch(page, "AVGO", "sum")
        before = copy.deepcopy(wdb(page))
        big = fx(); big["sections"]["s1"]["md"] = "x" * (210 * 1024)
        no_s3 = fx(); del no_s3["sections"]["s3"]["md"]
        no_sum = fx(); no_sum["summary"] = "ข้อความ"
        cases = [("schema อื่น", json.dumps(dict(fx(), schema="living-thesis@2")), "schema"),
                 ("JSON พัง", '{"schema": "living-thesis@1", "sym": ', "อ่าน JSON ไม่ได้"),
                 ("sym ไม่ตรงการ์ด", json.dumps(fx("NVDA")), "JSON นี้เป็นของ NVDA ไม่ใช่ AVGO"),
                 ("เกิน 200KB", json.dumps(big), "200KB"),
                 ("ไม่มี s3.md", json.dumps(no_s3), "sections.s3.md"),
                 ("summary ไม่ใช่ object", json.dumps(no_sum), "summary"),
                 ("ไม่มี sym", json.dumps({k: v for k, v in fx().items() if k != "sym"}), "sym"),
                 ("ว่าง", "   ", "ยังไม่ได้วาง")]
        for nm, text, want in cases:
            err, prev = import_via_ui(page, text, top=False, bound_sym="AVGO", save=False)
            saved_vis = js(page, "()=>getComputedStyle(document.getElementById('ltSaveBtn')).display !== 'none'")
            check(f"{tag} 3 {nm} → error ไทย ({want}) · ไม่มีปุ่มบันทึก", want in err and not saved_vis and prev == "", err)
            page.click("#ltOverlay .btns button:first-child"); page.wait_for_timeout(100)
        check(f"{tag} 3 ทุกเคสผิด → DB ไม่เปลี่ยน", wdb(page) == before)
        # sym ใกล้เคียง PTT ↔ PTT.BK ใช้ wlSymKey
        page.evaluate("()=>wlCol().doc('PTT.BK').set({ticker:'PTT.BK', market:'TH', port:'core', note:'', industry:'', added_at:'2026-01-01T00:00:00.000Z'})"); page.wait_for_timeout(300)
        go_watch(page, "PTT.BK", "sum")
        err, prev = import_via_ui(page, json.dumps(fx("PTT")), top=False, bound_sym="PTT.BK", save=True)
        d = wdb(page).get("PTT.BK") or {}
        check(f"{tag} 3 bound PTT.BK รับ JSON sym=PTT (เทียบด้วย wlSymKey) → เขียนที่ doc PTT.BK · ไม่สร้าง doc PTT ซ้ำ", err == "" and d.get("thesis", {}).get("sym") == "PTT" and "PTT" not in wdb(page), err)
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def xss_new_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_watch(page)
        X = '<script>window.__xss=1</script>'; I = '<img src=x onerror="window.__xss=2">'
        d = fx("XSSX", name="<b>Name</b>")
        d["market"] = "TH"
        d["summary"]["biz"] = X + I; d["summary"]["tier_note"] = I; d["summary"]["call"]["why"] = I
        d["sections"]["s1"]["md"] = "### " + I + "\n- " + X + "\n| " + I + " | b |\n|---|---|\n| <iframe src=x></iframe> | 2 |"
        d["sections"]["s2"]["md"] = "1. " + I; d["evidence"][0]["claim"] = I; d["sources"][0]["title"] = I; d["sources"][0]["url"] = "javascript:alert(1)"
        d["gaps"][0]["q"] = I; d["kpi"][0]["name"] = I; d["tripwires"][0]["signal"] = I; d["catalysts"][0]["event"] = I; d["log"][0]["new"] = I
        promoted(page, d["sym"], "TH")
        err, prev = import_via_ui(page, json.dumps(d, ensure_ascii=False), top=True)
        x = fx  # noqa
        row = wdb(page).get("XSSX") or {}
        check(f"{tag} 5 ticker ใหม่ (ไม่อยู่ใน Watchlist) → สร้าง doc port=core · market=TH (จาก JSON)", err == "" and row.get("port") == "core" and row.get("market") == "TH", err + json.dumps({k: row.get(k) for k in ("port", "market")}))
        res = {}
        for k in ("sum", "biz", "why", "trk", "exit"):
            tab(page, k)
            if k in ("sum", "exit", "trk"):
                for f in page.locator(".ltFoldBar").all():
                    try: f.click(timeout=500)
                    except Exception: pass
            res[k] = js(page, "()=>({s: document.querySelectorAll('.wlDBody script, .wlDPanel script').length, i: document.querySelectorAll('.wlDBody img, .wlDPanel img, .wlDBody iframe').length, a: [...document.querySelectorAll('.wlDBody a')].map(e=>e.getAttribute('href')), t: document.querySelector('.wlDBody').innerText.includes('<')})")
        check(f"{tag} 4 <script>/<img onerror> ใน summary/md/evidence/kpi/gaps/tripwire/log → ไม่มี element ใหม่ (script/img/iframe = 0)", all(v["s"] == 0 and v["i"] == 0 for v in res.values()), json.dumps(res))
        check(f"{tag} 4 แสดงเป็นตัวอักษร (innerText มี '<') · ไม่รัน (window.__xss ไม่ถูกตั้ง)", js(page, "()=>window.__xss") is None and res["biz"]["t"], json.dumps(res["biz"]))
        check(f"{tag} 4 ลิงก์แหล่งที่มา javascript: ไม่เป็น <a href>", all(not any(str(h).lower().startswith("javascript") for h in v["a"]) for v in res.values()), json.dumps(res))
        check(f"{tag} 4 ชื่อใน header escape (<b>Name</b> เป็นข้อความ)", "<b>Name</b>" in (txt_of(page, ".wlDTop") or ""))
        check(f"{tag} 4 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


# ───────────────────────── 10 · 11 · 12 stale · Today · การบ้าน ─────────────────────────
def stale_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    def extra(p):
        seed_wl(p, "D101", fx("D101", date="2026-06-23"))                 # 101 วันก่อน
        seed_wl(p, "D99", fx("D99", date="2026-06-25"))                   # 99 วันก่อน
        seed_wl(p, "D100", fx("D100", date="2026-06-24"))                 # 100 วัน = ยังไม่เก่ากว่า
        y = fx("YEST"); y["catalysts"] = [{"date": "2026-10-01", "date_status": "confirmed", "event": "งบไตรมาส ผ่านไปแล้ว", "thesis": 1}]
        seed_wl(p, "YEST", y)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=extra)
    try:
        go_watch(page)
        why = lambda s: js(page, "(s)=>{ const it = wlItems.find(x=>x.ticker===s); return ltStaleWhy(it); }", s)
        w101, w99, w100, wy = why("D101"), why("D99"), why("D100"), why("YEST")
        check(f"{tag} 10 date 101 วันก่อน → ⚠ ควร update 'Thesis อายุ 101 วัน'", w101 == ["Thesis อายุ 101 วัน"], json.dumps(w101, ensure_ascii=False))
        check(f"{tag} 10 date 99 / 100 วันก่อน → ไม่มี", w99 == [] and w100 == [], json.dumps([w99, w100]))
        check(f"{tag} 10 catalyst วันที่เมื่อวาน → มี · เหตุผลมีวันที่ '1 ต.ค. ผ่านไปแล้ว'", len(wy) == 1 and "1 ต.ค. ผ่านไปแล้ว" in wy[0], json.dumps(wy, ensure_ascii=False))
        go_watch(page, "D101", "sum")
        t1 = (js(page, "()=>{ const e = document.querySelector('[data-lt-stale]'); return e ? e.title : null; }") or "")
        go_watch(page, "D99", "sum"); n99 = cnt(page, "[data-lt-stale]")
        go_watch(page, "YEST", "sum"); t3 = js(page, "()=>{ const e = document.querySelector('[data-lt-stale]'); return e ? e.title : null; }") or ""
        bar = txt_of(page, "[data-lt-stalebar]") or ""
        check(f"{tag} 10 หัวการ์ด: D101 มีชิป (title = เหตุผล) · D99 ไม่มี · YEST มีชิป + แถบเหลืองในแท็บ สรุป", "101" in t1 and n99 == 0 and "1 ต.ค." in t3 and "ควรรัน living-thesis โหมด update" in bar, json.dumps([t1, n99, t3, bar], ensure_ascii=False))
    finally:
        browser.close()


def today_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    def extra(p):
        r = fx("RVW"); r["tripwires"][0]["level"] = "review"; seed_wl(p, "RVW", r)
        seed_wl(p, "WTC", fx("WTC", catalysts=[]))                                            # watch 3 ตัว แต่ไม่มี catalyst → เงียบ
        c1 = fx("CAT3", catalysts=[{"date": "2026-10-04", "date_status": "estimated", "event": "งบไตรมาสของ CAT3", "thesis": 1}]); c1["tripwires"] = []
        seed_wl(p, "CAT3", c1)
        c2 = fx("CAT10", catalysts=[{"date": "2026-10-12", "date_status": "confirmed", "event": "งบไกลเกิน", "thesis": 1}]); c2["tripwires"] = []
        seed_wl(p, "CAT10", c2)
        n = fx("NOTE4", catalysts=[]); n["tripwires"] = []
        seed_wl(p, "NOTE4", n, my_notes={"cat": [{"id": "n1", "text": "ประชุมใหญ่", "date": "2026-10-06"}, {"id": "n2", "text": "ไกลเกิน", "date": "2026-10-20"}], "blk": []})
        seed_wl(p, "NOTH", None, my_notes={"cat": [{"id": "n3", "text": "โน้ตไม่มี thesis", "date": "2026-10-03"}], "blk": []})
        for i in range(5):
            cx = fx("EXT%d" % i, catalysts=[{"date": "2026-10-0%d" % (3 + i % 3), "date_status": "confirmed", "event": "ext %d" % i, "thesis": 1}]); cx["tripwires"] = []
            seed_wl(p, "EXT%d" % i, cx)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=extra)
    try:
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(400)
        allrows = js(page, "()=>[...document.querySelectorAll('.tdRow')].map(e=>({k:e.dataset.kind, t:e.textContent.replace(/\\s+/g,' ').trim()}))")
        tw = [r for r in allrows if r["k"] == "tw-review"]
        check(f"{tag} 11 tripwire level review → แถว 🟡 'RVW Tripwire ถึงระดับทบทวน' · watch (WTC ฯลฯ) ไม่มีแถว", len(tw) == 1 and "RVW" in tw[0]["t"] and "ถึงระดับทบทวน" in tw[0]["t"] and not any(r["k"] in ("tw-review", "tw-confirmed") and "WTC" in r["t"] for r in allrows), json.dumps(tw, ensure_ascii=False))
        check(f"{tag} 11 ไม่มีแถว tw-check เดิม ('มีข่าวเข้าเงื่อนไข')", not any(r["k"] == "tw-check" or "มีข่าวเข้าเงื่อนไข" in r["t"] for r in allrows))
        cats = [r for r in allrows if r["k"] == "catalyst"]
        check(f"{tag} 11 catalyst thesis ภายใน 7 วัน + โน้ตมีวันที่ภายใน 7 วัน ขึ้นทั้งคู่ · สูงสุด 5 แถว", len(cats) == 5 and any("CAT3" in r["t"] for r in cats[:5]) , json.dumps([r["t"][:60] for r in cats], ensure_ascii=False))
        check(f"{tag} 11 catalyst +10 วัน ไม่ขึ้น", not any("CAT10" in r["t"] or "ไกลเกิน" in r["t"] for r in cats))
        shot(page, f"wl2-today-{sfx}.png")
        tw_go = js(page, "()=>document.querySelector('.tdRow[data-kind=\"tw-review\"]').dataset.args")
        js(page, "()=>document.querySelector('.tdRow[data-kind=\"tw-review\"]').click()"); page.wait_for_timeout(300)
        check(f"{tag} 11 กดแถว 🟡 tripwire → wlOpen(RVW,'exit')", js(page, "()=>wlSel") == "RVW" and sub_now(page) == "exit", tw_go)
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        # จำกัด catalyst แยกเคส: ลดแถว ext เพื่อเห็นโน้ต
        js(page, "()=>{ ['EXT0','EXT1','EXT2','EXT3','EXT4'].forEach(t=>wlCol().doc(t).delete()); }"); page.wait_for_timeout(500)
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        rows = js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=\"catalyst\"]')].map(e=>e.textContent.replace(/\\s+/g,' ').trim())")
        joined = " | ".join(rows)
        check(f"{tag} 11 โน้ตของฉันวันที่ 6 ต.ค. + ของ NOTH (ไม่มี thesis) ขึ้นพร้อม 'โน้ตของฉัน' · วันที่ 20 ต.ค. ไม่ขึ้น", "NOTE4 ประชุมใหญ่" in joined and "NOTH โน้ตไม่มี thesis" in joined and joined.count("โน้ตของฉัน") >= 2 and "ไกลเกิน" not in joined.replace("งบไกลเกิน", ""), joined)
        sub = js(page, "()=>document.querySelector('.tdRow[data-kind=\"catalyst\"]').textContent.replace(/\\s+/g,' ')")
        check(f"{tag} 11 บรรทัดรอง 'Watch · ติดตาม'", "Watch · ติดตาม" in sub, sub)
        js(page, "()=>document.querySelector('.tdRow[data-kind=\"catalyst\"]').click()"); page.wait_for_timeout(300)
        check(f"{tag} 11 กดแถว catalyst → wlOpen(T,'trk')", sub_now(page) == "trk")
        check(f"{tag} 11 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def hw_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    def extra(p):
        seed_wl(p, "NOTH", None)
        s = fx("STALE", date="2026-09-30"); sig = s["tripwires"][0]["signal"]
        seed_wl(p, "STALE", s, hits={sig: "2026-10-01"})
        seed_wl(p, "OLD", fx("OLD", date="2026-08-03"))
        seed_wl(p, "NEW", fx("NEW", date="2026-09-27"))
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=extra)
    try:
        js(page, "()=>switchTab('today')"); page.wait_for_timeout(300)
        c = js(page, "()=>tdHomeworkCandidates().map(x=>[x.t, x.reason])")
        check(f"{tag} 12 ลำดับการบ้าน NOTH → STALE → OLD → NEW", [x[0] for x in c] == ["NOTH", "STALE", "OLD", "NEW"], json.dumps(c, ensure_ascii=False))
        check(f"{tag} 12 เหตุผล 'ยังไม่มี Thesis' / 'ควร update: …' / 'Thesis เก่า 60 วัน' / 'Thesis เก่า 5 วัน'", c and c[0][1] == "ยังไม่มี Thesis" and c[1][1].startswith("ควร update: ") and 'ชนแล้ว' in c[1][1] and c[2][1] == "Thesis เก่า 60 วัน" and c[3][1] == "Thesis เก่า 5 วัน", json.dumps(c, ensure_ascii=False))
        hw = js(page, "()=>{ const r = document.querySelector('.tdRow[data-kind=\"homework\"]'); return r ? r.textContent.replace(/\\s+/g,' ').trim() : null; }")
        check(f"{tag} 12 แถวการบ้านใน Today = NOTH · ยังไม่มี Thesis", hw and "NOTH" in hw and "ยังไม่มี Thesis" in hw, str(hw))
    finally:
        browser.close()


# ───────────────────────── 13 Tier · 14 ไม่มี thesis ─────────────────────────
def tier_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    def extra(p):
        seed_wl(p, "AVGO", fx())
        seed_wl(p, "BARE", None)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=extra)
    try:
        js(page, "()=>switchTab('plan')"); page.wait_for_timeout(200)
        def new_form(t):
            if cnt(page, '.core-sheet [data-core-sheet="new"]'): js(page, "()=>{ if(typeof coreNewClose==='function') coreNewClose(); }")
            page.evaluate("(a)=>coreNewOpen(a)", "main"); page.wait_for_selector('.core-sheet [data-core-sheet="new"]')
            page.fill("#cnTicker", t); page.wait_for_timeout(120)
        vis = lambda s: page.locator(s).count() > 0 and page.locator(s).first.is_visible()
        new_form("BARE")
        check(f"{tag} 13 ticker ที่ไม่มี thesis → ไม่มีปุ่ม 'เติมจาก Thesis'", not vis("#tiFillTh"))
        new_form("AVGO")
        check(f"{tag} 13 AVGO มี thesis.tier_inputs → ปุ่ม 'เติมจาก Thesis' (ไม่มี 'เติมจาก Research')", vis("#tiFillTh") and "เติมจาก Thesis" in page.inner_text("#tiFillTh") and "เติมจาก Research" not in page.inner_text(".core-sheet"))
        page.fill("#tiRoic", "9.5")      # กรอกไว้ก่อน → ห้ามทับ
        snap0 = js(page, "()=>JSON.stringify({g5:[...document.querySelectorAll('[data-g5] button.on')].map(b=>b.parentElement.dataset.g5+b.dataset.v), pick:[...document.querySelectorAll('.ccSegTier button.on')].map(b=>b.dataset.pick), reason:(document.getElementById('cnReason')||{}).value})")
        page.click("#tiFillTh"); page.wait_for_timeout(200)
        got = {k: page.input_value(k) for k in ("#tiRoic", "#tiNd", "#tiFcf", "#tiRev", "#tiCagr", "#tiOpm", "#tiOpmPrev")}
        tk = js(page, "()=>Object.fromEntries(['fcf3y','capret','ocf','netcash'].map(k=>[k, (()=>{ const on=[...document.querySelectorAll('[data-tk=\"'+k+'\"] button.on')].map(b=>b.dataset.v); return on.length ? on[0]==='1' : null; })()]))")
        check(f"{tag} 13 เติมเฉพาะช่องว่าง: ROIC ที่กรอกไว้ (9.5) ไม่ถูกทับ · ND 1.4 · FCF 148 · รายได้โต 48.7 · CAGR 24.4 · Op 39.9/26.1", got == {"#tiRoic": "9.5", "#tiNd": "1.4", "#tiFcf": "148", "#tiRev": "48.7", "#tiCagr": "24.4", "#tiOpm": "39.9", "#tiOpmPrev": "26.1"}, json.dumps(got))
        check(f"{tag} 13 ช่องติ๊ก: FCF 3 ปี=ใช่ · ปันผล=ใช่ · OCF=ใช่ · เงินสดสุทธิ=ไม่ใช่", tk == {"fcf3y": True, "capret": True, "ocf": True, "netcash": False}, json.dumps(tk))
        msg = page.inner_text("#tiFillMsg")
        check(f"{tag} 13 ข้อความ: เติม 10 ช่อง · ข้าม 1 ช่องที่กรอกแล้ว · จาก Thesis 2 ต.ค. (ข้อมูล ณ 1 ต.ค.)", msg.strip() == "เติม 10 ช่อง · ข้าม 1 ช่องที่กรอกแล้ว · จาก Thesis 2 ต.ค. (ข้อมูล ณ 1 ต.ค.)", msg)
        title = page.get_attribute("#tiNd", "title") or ""
        check(f"{tag} 13 ช่องที่เติม title = '{{tag}} · {{period}} · {{src}}'", title.startswith("C · FY25 · ") and "หนี้รวม" in title, title)
        snap1 = js(page, "()=>JSON.stringify({g5:[...document.querySelectorAll('[data-g5] button.on')].map(b=>b.parentElement.dataset.g5+b.dataset.v), pick:[...document.querySelectorAll('.ccSegTier button.on')].map(b=>b.dataset.pick), reason:(document.getElementById('cnReason')||{}).value})")
        check(f"{tag} 13 ไม่แตะ Gate 5 / ปุ่ม Tier / เหตุผล (ก่อน/หลังกดเติมเหมือนเดิม: Gate 5 ว่าง)", json.loads(snap1)["g5"] == [] and snap1 == snap0, snap0 + " → " + snap1)
        shot_el = page.locator("[data-c-tierblock]").first
        try: shot_el.screenshot(path=os.path.join(SHOTS, f"wl2-tier-fill-{sfx}.png"))
        except Exception as e: print("shot fail", e)
        # ครั้งที่ 2: ไม่มีช่องว่าง → ข้อความ
        page.click("#tiFillTh"); page.wait_for_timeout(150)
        msg2 = page.inner_text("#tiFillMsg").strip()
        check(f"{tag} 13 กดซ้ำ (ไม่มีช่องว่าง) → 'ไม่มีช่องว่างให้เติม'", msg2 == "ไม่มีช่องว่างให้เติม", msg2)
        # เติมครบ 11 ช่อง ในฟอร์มใหม่
        new_form("AVGO"); page.click("#tiFillTh"); page.wait_for_timeout(200)
        check(f"{tag} 13 ฟอร์มว่าง → เติม 11 ช่อง (ROIC 15.5 · ND 1.4 · FCF 148 …) · netCash = ไม่ใช่", page.input_value("#tiRoic") == "15.5" and page.inner_text("#tiFillMsg").startswith("เติม 11 ช่อง · ข้าม 0 ช่อง"), page.inner_text("#tiFillMsg"))
        check(f"{tag} 13 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def nothesis_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    def extra(p):
        seed_wl(p, "BARE", None, my_notes={"cat": [{"id": "n1", "text": "รอข่าว", "date": None}], "blk": []})
        seed(p, ["research", "CAND1"], {"ticker": "CAND1", "name": "Cand One", "summary": "หุ้นตัวอย่าง"})
        seed(p, ["users", "testuid", "ideas", "cand-fixture"], json.loads('''{"idea": {"schema": "idea@1", "id": "cand-fixture", "name": "ไอเดียตัวอย่าง (ID2: ให้ CAND1 เป็น Candidates)", "date": "2026-10-01", "mode": "scan", "scope": ["US"], "status": "need_evidence", "idea": {}, "chain": {"segments": [{"name": "ส่วนทดสอบ", "effect": "win"}]},
 "candidates": [{"sym": "CAND1", "market": "US", "name": "Cand One", "segments": ["ส่วนทดสอบ"], "relevance_src": "10-K ตัวอย่าง", "rank": 1, "state": "study"}], "kill": [], "gaps": [], "evidence": []}, "idea_log": [], "user": {}}'''))   # ID2 — ให้ CAND1 เป็นบริษัทในไอเดีย
        seed_wl(p, "AVGO", fx())
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=extra)
    try:
        js(page, "()=>rsLoad(true)"); page.wait_for_timeout(500)
        go_watch(page, "BARE", "sum")
        t = txt_of(page, "[data-lt-empty]") or ""
        check(f"{tag} 14 ไม่มี thesis → การ์ด 'ยังไม่มี Thesis — รัน living-thesis แล้ว 📥 Import' + ปุ่ม Import", "ยังไม่มี Thesis — รัน living-thesis แล้ว 📥 Import" in t and cnt(page, "[data-lt-import]") == 1 and cnt(page, "[data-lt-tabs]") == 0, t)
        check(f"{tag} 14 โน้ตของฉันยังใช้ได้ (＋ โน้ต) แม้ยังไม่มี Thesis", cnt(page, '[data-wl-addnote="cat"]') == 1 and "รอข่าว" in body_txt(page))
        shot(page, f"wl2-no-thesis-{sfx}.png")
        dot = js(page, "()=>[...document.querySelectorAll('.wlR')].map(e=>[e.dataset.sym, e.querySelector('.wlDotR').className, e.querySelector('.wlDotR').title])")
        st = txt_of(page, ".wlStat") or ""
        check(f"{tag} 14 รายชื่อ: จุดสถานะ มี Thesis / รอสร้าง Thesis · สถานะบน '1 ตัวรอสร้าง Thesis'", ["AVGO", "wlDotR ok", "มี Thesis"] in dot and ["BARE", "wlDotR wait", "รอสร้าง Thesis"] in dot and "1 ตัวรอสร้าง Thesis" in st, json.dumps([dot, st], ensure_ascii=False))
        js(page, "()=>wlSetView('cand')"); page.wait_for_timeout(200); js(page, "()=>wlOpen('CAND1')"); page.wait_for_timeout(250)
        t2 = txt_of(page, "[data-lt-empty]") or ""
        btns = js(page, "()=>[...document.querySelectorAll('.wlActs button')].map(e=>e.innerText.trim())")
        check(f"{tag} 14 Candidates กดเข้า = การ์ด 'ยังไม่มี Thesis' + ปุ่ม ＋ เพิ่มเข้า Watchlist + 📥 Import", "ยังไม่มี Thesis" in t2 and any("เพิ่มเข้า Watchlist" in b for b in btns) and any("Import" in b for b in btns), json.dumps([t2, btns], ensure_ascii=False))
        # Import จาก Candidates → ต้องเป็นของ ticker นั้น
        err, prev = import_via_ui(page, json.dumps(fx("AVGO")), top=False, bound_sym="CAND1", save=False)
        check(f"{tag} 14 Import จากการ์ด CAND1 แต่ JSON เป็น AVGO → error JSON นี้เป็นของ AVGO ไม่ใช่ CAND1", "JSON นี้เป็นของ AVGO ไม่ใช่ CAND1" in err, err)
        check(f"{tag} 14 ไม่มี console error", not ce and not pe, json.dumps([ce[:2], pe[:2]]))
    finally:
        browser.close()


def mem_tests(pw, w, h, label):
    """16 — จำแท็บต่อ ticker หลังรีโหลด (localStorage ตั้งไว้ก่อนโหลดหน้า)"""
    tag = f"[{ENGINE}/{label}]"
    def extra(p):
        seed_wl(p, "AVGO", fx()); seed_wl(p, "NVDA", fx("NVDA"))
        p.evaluate("()=>{ localStorage.setItem('wlSubMap', JSON.stringify({AVGO:'trk', NVDA:'exit'})); localStorage.setItem('wlSelLast','AVGO'); }")
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, extra=extra)
    try:
        go_watch(page)
        on = js(page, "()=>{ const b = document.querySelector('[data-lt-tab].on'); return b ? b.dataset.ltTab : null; }")
        check(f"{tag} 16 โหลดใหม่: AVGO เปิดที่แท็บ ติดตาม (จากที่จำไว้)", js(page, "()=>wlSel") == "AVGO" and on == "trk", str(on))
        js(page, "()=>wlOpen('NVDA')"); page.wait_for_timeout(200)
        on2 = js(page, "()=>document.querySelector('[data-lt-tab].on').dataset.ltTab")
        check(f"{tag} 16 เปิด NVDA → แท็บของ NVDA เอง (ออกเมื่อ)", on2 == "exit", on2)
    finally:
        browser.close()


# ───────────────────────── 18 grep · ไฟล์ ─────────────────────────
def static_tests():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    n = len(re.findall(r"research_card|research-card|rcTierMetrics|เติมจาก Research", html))
    check("[static] 18 grep index.html: research_card / research-card / rcTierMetrics / เติมจาก Research = 0 บรรทัดข้อความ", n == 0, str(n))
    lines = sum(1 for ln in html.split("\n") if re.search(r"research_card|research-card|rcTierMetrics|เติมจาก Research", ln))
    check("[static] 18 grep -c (นับบรรทัด) = 0", lines == 0, str(lines))
    left = [f for f in os.listdir(ROOT) if f.startswith("research-card") or f == "inline-research-card.py"]
    moved = os.listdir(os.path.join(ROOT, "_to_delete", "research-card")) if os.path.isdir(os.path.join(ROOT, "_to_delete", "research-card")) else []
    check("[static] 18 ไฟล์ research-card* / inline-research-card.py ไม่อยู่ที่ root", not left, json.dumps(left))
    check("[static] 18 ไฟล์ทั้งหมดอยู่ใน _to_delete/research-card/ (ไม่ลบ)", {"research-card.js", "research-card-test.js", "inline-research-card.py"} <= set(moved), json.dumps(sorted(moved)))
    check("[static] ไม่มี <script> inline ของ research-card เหลือ · มี ltMd / ltParse / living-thesis@1", "RESEARCH CARD INLINE" not in html and "function ltMd(" in html and "living-thesis@1" in html)


def main():
    static_tests()
    with sync_playwright() as pw:
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            main_tests(pw, w, h, label)
            error_tests(pw, w, h, label)
            xss_new_tests(pw, w, h, label)
            stale_tests(pw, w, h, label)
            today_tests(pw, w, h, label)
            hw_tests(pw, w, h, label)
            tier_tests(pw, w, h, label)
            nothesis_tests(pw, w, h, label)
            mem_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 40 / WL2) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
