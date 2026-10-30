#!/usr/bin/env python3
"""SN1 — ลำดับหน้า Today ที่ยืนยันแล้ว + Weekly Stock Summary (Watchlist + Candidates) · เทส 102
Chromium · FF_STUB_BASE = Lean · 300 / 390 / 1280 / 1440 · นาฬิกาปลอม พฤ. 8 ต.ค. 2026 · ข้อมูลทดสอบ = SAMPLE ล้วน
ภาพ tests/screenshots/sn1-{today-390,today-1440,sheet-390,sheet-expanded-390,panel-1440}.png
รัน: python3 run_tests_phase102.py"""
import copy, json, os
import pf2_retire as RT
import ln3fix_common as C
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase56 as P56
import run_tests_phase100 as P100

ENGINE = base.BROWSER_ENGINE
results = []
js = C.js
ED = "2026-10-04"   # ฉบับของสัปดาห์ 28 ก.ย.–4 ต.ค. (สัปดาห์ก่อน) · ฉบับปัจจุบันของ 8 ต.ค. = 5–11 ต.ค. ไม่จำเป็น — ใช้ period_end ภายใน 7 วัน
ED = "2026-10-05"
DIALOGS = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:900] + "...") if (detail and len(detail) > 900) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def settle(page, ms=450): page.wait_for_timeout(ms)


def launch(pw, w, h):
    b, ctx, page, ce, pe, dl = P56.launch(pw, w, h, P56.with_goals(), None, log={})
    page.on("dialog", lambda d: DIALOGS.append(d.message))
    # รายชื่อหุ้นตัวอย่าง (SAMPLE) — Candidates 2 (AAA · CCC) · Watchlist 5 (BBB · CCC · DDD · EEE · GGG · HHH) · CCC อยู่ทั้งสองกลุ่ม
    page.evaluate("""()=>{ window.wlRowsAll = ()=>({wl: ['BBB','CCC','DDD','EEE','GGG','HHH'].map(s=>({sym:s})), cand: ['AAA','CCC'].map(s=>({sym:s}))}); }""")
    return b, page, ce, pe


def stock_doc(edition=ED, start="2026-09-29", **over):
    d = {"schema": "stockNews/v1", "edition_id": edition, "period_start": start, "period_end": edition, "asof": edition + "T09:00:00+07:00",
         "sources": {"s1": {"name": "SAMPLE source", "url": "https://example.com/a", "published_at": "2026-10-02"}},
         "stocks": {
             "AAA": {"groups": ["candidate"], "coverage": "news", "status": "review", "headline_th": "SAMPLE AAA ปรับแนวโน้มกำไร", "happened_th": "SAMPLE ข้อเท็จจริง AAA", "why_th": "SAMPLE การตีความ AAA", "monitor_th": "SAMPLE ติดตาม AAA", "source_refs": ["s1"], "thesis_ref": False},
             "CCC": {"groups": ["candidate", "watchlist"], "coverage": "news", "status": "supports", "headline_th": "SAMPLE CCC ลูกค้ารายใหญ่ใหม่", "happened_th": "SAMPLE h", "why_th": "SAMPLE w", "monitor_th": "SAMPLE m", "source_refs": ["s1"], "thesis_ref": True},
             "BBB": {"groups": ["watchlist"], "coverage": "news", "status": "info", "headline_th": "SAMPLE BBB ประกาศเพิ่มทุน", "happened_th": "h", "why_th": "w", "monitor_th": "m", "source_refs": [], "thesis_ref": False},
             "DDD": {"groups": ["watchlist"], "coverage": "news", "status": "supports", "headline_th": "SAMPLE DDD ผลิตภัณฑ์ใหม่", "happened_th": "h", "why_th": "w", "monitor_th": "m", "source_refs": [], "thesis_ref": False},
             "EEE": {"groups": ["watchlist"], "coverage": "none"}, "GGG": {"groups": ["watchlist"], "coverage": "none"},
             "HHH": {"groups": ["watchlist"], "coverage": "incomplete"},
             "ZZZ": {"groups": ["watchlist"], "coverage": "news", "status": "info", "headline_th": "SAMPLE ZZZ ออกจากรายการแล้ว", "source_refs": []}}}
    d.update(over)
    return d


def seed(page, d):
    page.evaluate("([id,b])=>{ window.firebase.__mockDb.__seedDoc(['users','testuid','stockNews',id], b); stkStop(); stkStart(); }", [d["edition_id"], d])
    settle(page, 600)


def seed_wi(page):
    d = P100.sample(week="2026-10-05")
    for ev in d["events"].values():
        for k in ("scheduled_at",):
            if ev.get(k): ev[k] = ev[k].replace("2026-10-01", "2026-10-08").replace("2026-10-02", "2026-10-09")
        if ev.get("date_local"): ev["date_local"] = ev["date_local"].replace("2026-10-01", "2026-10-08").replace("2026-10-02", "2026-10-09")
    P100.seed(page, d)


def go_today(page): js(page, "()=>{ switchTab('today'); todayRefresh(true); }"); settle(page, 700)


ORDER = """()=>{
  const sels = [['head','[data-ln3-tdhead]'],['goal','[data-td-goaltop],[data-gl-goal]'],['news','[data-wi-today]'],['slots','[data-td-routine],[data-td-off]'],['sat','[data-ln3-satbox]'],['hw','[data-ln3-hw]'],['stk','[data-stk-card]'],['ok','.ln3-tdok']];
  const out = {}; sels.forEach(([k,s])=>{ const e = document.querySelector('#tabToday '+s.split(',').join(',#tabToday ')); if(e){ const r = e.getBoundingClientRect(); out[k] = {t: Math.round(r.top + scrollY), l: Math.round(r.left), b: Math.round(r.bottom + scrollY), w: Math.round(r.width), h: Math.round(r.height)}; } });
  const dom = [...document.querySelectorAll('#tabToday [data-ln3-tdhead],#tabToday [data-td-goaltop],#tabToday [data-gl-goal],#tabToday [data-wi-today],#tabToday [data-td-routine],#tabToday [data-td-off],#tabToday [data-ln3-satbox],#tabToday [data-ln3-hw],#tabToday [data-stk-card],#tabToday .ln3-tdok')].map(e=>e.matches('[data-ln3-tdhead]') ? 'head' : e.matches('[data-td-goaltop],[data-gl-goal]') ? 'goal' : e.matches('[data-wi-today]') ? 'news' : e.matches('[data-td-routine],[data-td-off]') ? 'slots' : e.matches('[data-ln3-satbox]') ? 'sat' : e.matches('[data-ln3-hw]') ? 'hw' : e.matches('[data-stk-card]') ? 'stk' : 'ok');
  const c1 = document.querySelector('[data-td-col="1"]'), c2 = document.querySelector('[data-td-col="2"]');
  const kind = e => e.matches('[data-wi-today]') ? 'news' : e.matches('[data-td-routine],[data-td-off]') ? 'slots' : e.matches('[data-ln3-satbox]') ? 'sat' : e.matches('[data-gl-goal]') ? 'goal' : e.matches('[data-ln3-hw]') ? 'hw' : e.matches('[data-stk-card]') ? 'stk' : e.matches('[data-ln3-recheck]') ? 'recheck' : e.matches('.ln3-tdok') ? 'ok' : e.matches('[data-ln3-tasks]') ? 'tasks' : '?';
  return {pos: out, dom, c1: c1 ? [...c1.children].map(kind) : null, c2: c2 ? [...c2.children].map(kind) : null, c1b: c1 ? Math.round(c1.getBoundingClientRect().bottom) : null, c2b: c2 ? Math.round(c2.getBoundingClientRect().bottom) : null,
          c1l: c1 ? Math.round(c1.getBoundingClientRect().left) : null, c2l: c2 ? Math.round(c2.getBoundingClientRect().left) : null, ow: document.documentElement.scrollWidth - innerWidth,
          line: (()=>{ const l = document.querySelector('[data-td-goalline]'); if(!l || !l.getClientRects().length) return null; const r = l.getBoundingClientRect(); return {h: Math.round(r.height), t: l.innerText.replace(/\\s+/g,' ').trim(), open: l.getAttribute('aria-expanded')}; })(),
          full: (()=>{ const f = document.querySelector('.tdGoalFull'); return f ? f.getClientRects().length > 0 : null; })()};
}"""


def order_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed_wi(page); seed(page, stock_doc())
        go_today(page)
        o = js(page, ORDER)
        mac = w >= 1000
        RT.retired_td3a(f"{tag} 1 ลำดับ Today เดิม (goal/news/slots/sat/hw/stk/ok · 2 คอลัมน์ Mac · เป้าหมายแบบบรรทัด/การ์ดเต็ม) — ดู TD3a_retired.md")
        pn = js(page, RT.PANELS_JS)
        check(f"{tag} 1 TD3a: 3 panels (Overview · Core Port · Satellite) ชิดบนเท่ากันบน Mac · ไม่ล้นแนวนอน", RT.panels_ok(pn), pn)
        if shots and label == "390px": C.shot(page, "sn1-today-390.png", full=True)
        if shots and label == "1440px": C.shot(page, "sn1-today-1440.png", full=True)
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def card_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        go_today(page)
        c = js(page, "()=>({s: (document.querySelector('[data-stk-card]')||{}).dataset, t: (document.querySelector('[data-stk-card]')||{innerText:''}).innerText.replace(/\\s+/g,' ').trim(), n: document.querySelectorAll('[data-stk-card]').length})")
        check(f"{tag} 2 ไม่มีฉบับ → 'สรุปสัปดาห์นี้ยังไม่พร้อม' + วาง JSON (ไม่บอกว่าไม่มีข่าว · ไม่มีแถบ New)", c["n"] == 1 and "สรุปสัปดาห์นี้ยังไม่พร้อม" in c["t"] and "วาง JSON" in c["t"] and "New" not in c["t"] and "ไม่มีข่าว" not in c["t"], c)
        seed(page, stock_doc())
        go_today(page)
        c = js(page, "()=>({k: document.querySelector('[data-stk-card]').dataset.stkCard, t: document.querySelector('[data-stk-card]').innerText.replace(/\\s+/g,' ').trim(), line: document.querySelector('[data-stk-line]').innerText})")
        check(f"{tag} 2 ฉบับใหม่ (ยังไม่อ่าน): ป้าย New · '29 ก.ย.–5 ต.ค. · 4 ตัวมีอัปเดต · 1 Candidate ควรทบทวน' (นับจากข้อมูลจริง) · อ่าน →", c["k"] == "new" and "New" in c["t"] and "29 ก.ย.–5 ต.ค." in c["line"] and "4 ตัวมีอัปเดต" in c["line"] and "1 Candidate ควรทบทวน" in c["line"] and "อ่าน →" in c["t"], c)
        # เปลี่ยนข้อมูล → ตัวเลขเปลี่ยนตาม (ไม่ hardcode)
        d2 = stock_doc(); d2["stocks"]["AAA"]["status"] = "supports"; d2["stocks"]["DDD"]["coverage"] = "none"; d2["stocks"]["DDD"]["status"] = None
        seed(page, d2); go_today(page)
        l2 = js(page, "()=>document.querySelector('[data-stk-line]').innerText")
        check(f"{tag} 2 ตัวเลขคำนวณจากข้อมูลจริง: เปลี่ยนข้อมูลแล้ว → '3 ตัวมีอัปเดต' และไม่มี Candidate ควรทบทวน", "3 ตัวมีอัปเดต" in l2 and "ควรทบทวน" not in l2, l2)
        seed(page, stock_doc()); go_today(page)
        # อ่านแล้ว
        page.locator("[data-stk-open]").click(); settle(page, 500)
        page.locator("[data-stk-read]").click(); settle(page, 600)
        saved = js(page, "()=>tdSettings().stockNewsRead")
        js(page, "()=>stkCloseView()"); go_today(page)
        c = js(page, "()=>({k: document.querySelector('[data-stk-card]').dataset.stkCard, new: !!document.querySelector('[data-stk-new]'), cls: document.querySelector('[data-stk-card]').className})")
        check(f"{tag} 2 อ่านแล้ว → เก็บ stockNewsRead[{ED}] ใน settings · ป้าย New หาย · การ์ดจางลง · ยังเปิดอ่านได้", saved == {ED: True} and c["k"] == "read" and not c["new"] and "read" in c["cls"] and js(page, "()=>!!document.querySelector('[data-stk-open]')"), [saved, c])
        # โหลดซ้ำ (render ใหม่ทั้งหน้า) ยังไม่ flag ซ้ำ
        js(page, "()=>{ stkStop(); stkStart(); render(); }"); settle(page, 700); go_today(page)
        check(f"{tag} 2 เปิดแดชบอร์ดใหม่/โหลดซ้ำ → ฉบับเดิมไม่ถูก flag ว่าใหม่", js(page, "()=>document.querySelector('[data-stk-card]').dataset.stkCard") == "read")
        # ฉบับใหม่กว่า → New อีก
        seed(page, stock_doc(edition="2026-10-12", start="2026-10-06")); go_today(page)
        c = js(page, "()=>({k: document.querySelector('[data-stk-card]').dataset.stkCard, ed: document.querySelector('[data-stk-card]').dataset.stkEdition})")
        check(f"{tag} 2 ฉบับใหม่ (12 ต.ค.) → New อีกครั้ง (อ่านเป็นรายฉบับ)", c == {"k": "new", "ed": "2026-10-12"}, c)
        # ฉบับเก่า: แสดงวันที่จริง ไม่เรียกว่าสัปดาห์นี้
        b2 = None
    finally: b.close()
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        seed(page, stock_doc(edition="2026-09-13", start="2026-09-07")); go_today(page)
        t = js(page, "()=>document.querySelector('[data-stk-card]').innerText.replace(/\\s+/g,' ').trim()")
        check(f"{tag} 2 ฉบับเก่า (จบ 13 ก.ย.): ยังเปิดอ่านได้ · แสดงวันที่จริง '7 ก.ย.–13 ก.ย.' + 'ฉบับเก่า · ยังไม่มีฉบับสัปดาห์นี้' (ไม่ relabel เป็นสัปดาห์นี้)", "7 ก.ย.–13 ก.ย." in t and "ฉบับเก่า" in t and "อ่าน →" in t, t)
        check(f"{tag} 2 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def sheet_tests(pw, w, h, label, shots=False):
    tag = f"[{ENGINE}/{label}]"
    b, page, ce, pe = launch(pw, w, h)
    try:
        seed(page, stock_doc()); go_today(page)
        page.locator("[data-stk-open]").click(); settle(page, 600)
        mac = w >= 1000
        kind = js(page, "()=>({panel: !!document.querySelector('.stk-panel'), sheet: !!document.querySelector('.stk-sheet'), r: (document.querySelector('.stk-panel')||document.querySelector('.stk-sheet .ui-sheet')).getBoundingClientRect().toJSON(), vw: innerWidth, vh: innerHeight})")
        if mac: check(f"{tag} 3 Mac: เปิดเป็นแผงด้านขวา (~440px) ไม่ใช่แผ่นเต็มจอ", kind["panel"] and not kind["sheet"] and 380 <= kind["r"]["width"] <= 460 and abs(kind["r"]["right"] - kind["vw"]) <= 1, kind)
        else: check(f"{tag} 3 iPhone: เปิดเป็นแผ่นเต็มกว้าง สูงเกือบเต็มจอ + ปุ่ม ✕ ปิด ติดบน", kind["sheet"] and not kind["panel"] and abs(kind["r"]["width"] - kind["vw"]) <= 1 and kind["r"]["height"] >= kind["vh"] * 0.6 and js(page, "()=>!!document.querySelector('[data-stk-close]')"), kind)
        s = js(page, """()=>({meta: document.querySelector('[data-stk-meta]').innerText, secs: [...document.querySelectorAll('[data-stk-sec]')].map(s=>[s.dataset.stkSec, s.querySelector('.stkSecH').innerText, [...s.querySelectorAll('[data-stk-row]')].map(r=>r.dataset.stkRow)]),
          folds: [...document.querySelectorAll('[data-stk-fold]')].map(f=>[f.dataset.stkFold, f.querySelector('summary').innerText, f.open]), all: [...document.querySelectorAll('[data-stk-row]')].map(r=>r.dataset.stkRow),
          pills: Object.fromEntries([...document.querySelectorAll('[data-stk-row]')].map(r=>[r.dataset.stkRow, (r.querySelector('[data-stk-pill]')||{innerText:null}).innerText])), tags: [...document.querySelector('[data-stk-row="CCC"]').querySelectorAll('.wiBdg')].map(e=>e.innerText),
          ow: document.documentElement.scrollWidth - innerWidth})""")
        check(f"{tag} 3 หัว: ช่วงข่าว + 'อัปเดต' (asof) · Candidates ก่อน Watchlist · ในกลุ่ม: ควรทบทวน → สนับสนุน → ข้อมูลเพิ่มเติม แล้ว A–Z", "29 ก.ย.–5 ต.ค." in s["meta"] and "อัปเดต" in s["meta"] and [x[0] for x in s["secs"]] == ["cand", "wl"] and s["secs"][0][2] == ["AAA", "CCC"] and s["secs"][1][2] == ["DDD", "BBB"], s["secs"])
        check(f"{tag} 3 หุ้นที่อยู่ทั้งสองกลุ่ม (CCC) แสดงครั้งเดียวใต้ Candidates ติดป้ายสองอัน · ป้ายสถานะ 3 แบบเท่านั้น", s["all"].count("CCC") == 1 and s["tags"] == ["Candidate", "Watchlist"] and set(v for v in s["pills"].values() if v) <= {"สนับสนุนมุมมอง", "ควรทบทวน", "ข้อมูลเพิ่มเติม"}, s)
        check(f"{tag} 3 พับท้าย: 'ไม่มีข่าวสำคัญ (2)' แยกจาก 'ข้อมูลไม่ครบ (1)' · 'ไม่อยู่ในรายการแล้ว (1)' · พับเป็นค่าเริ่มต้น", s["folds"] == [["none", "ไม่มีข่าวสำคัญ (2)", False], ["incomplete", "ข้อมูลไม่ครบ (1)", False], ["gone", "ไม่อยู่ในรายการแล้ว (1)", False]] and "ZZZ" not in s["all"], s["folds"])
        if shots and label == "390px": C.shot(page, "sn1-sheet-390.png", ".stk-sheet .ui-sheet")
        page.locator('[data-stk-toggle="AAA"]').click(); settle(page, 300)
        e = js(page, "()=>({t: document.querySelector('[data-stk-body=\"AAA\"]').innerText.replace(/\\s+/g,' '), src: document.querySelector('[data-stk-body=\"AAA\"] .stkSrc').open, ow: document.documentElement.scrollWidth - innerWidth})")
        check(f"{tag} 3 กางแถว → ข้อเท็จจริง / การตีความ / ติดตามอะไร แยกส่วน · 'ยังไม่มี Thesis ที่บันทึก — ไม่ได้ระบุว่าข่าวนี้เปลี่ยน Thesis' (thesis_ref=false) · แหล่งข่าวพับ · ดูหุ้นใน Watch →",
              all(k in e["t"] for k in ("ข้อเท็จจริง SAMPLE ข้อเท็จจริง AAA", "การตีความ SAMPLE การตีความ AAA", "ติดตามอะไร SAMPLE ติดตาม AAA", "แหล่งข่าว (1)", "ดูหุ้นใน Watch →", "ไม่ได้ระบุว่าข่าวนี้เปลี่ยน Thesis")) and e["src"] is False, e)
        page.locator('[data-stk-toggle="CCC"]').click(); settle(page, 300)
        ccc = js(page, "()=>document.querySelector('[data-stk-body=\"CCC\"]').innerText")
        check(f"{tag} 3 thesis_ref=true → ไม่มีข้อความปฏิเสธ Thesis", "ไม่ได้ระบุว่าข่าวนี้เปลี่ยน Thesis" not in ccc)
        page.locator('[data-stk-body="AAA"] .stkSrc summary').click(); settle(page, 200)
        if shots and label == "390px": C.shot(page, "sn1-sheet-expanded-390.png", ".stk-sheet .ui-sheet")
        if shots and label == "1440px": C.shot(page, "sn1-panel-1440.png", ".stk-panel")
        check(f"{tag} 3 ไม่ล้นแนวนอน", js(page, "()=>document.documentElement.scrollWidth - innerWidth") <= 0)
        js(page, "()=>{ window.__wo = []; const o = window.wlOpen; window.wlOpen = (...a)=>{ window.__wo.push(a[0]); return o(...a); }; }")
        page.locator('[data-stk-watch="AAA"]').click(); settle(page, 600)
        w2 = js(page, "()=>({tab: activeTab, sel: window.__wo[0], open: !!document.querySelector('.stk-sheet, .stk-panel')})")
        check(f"{tag} 3 'ดูหุ้นใน Watch →' → ไปแท็บ Watch เปิดหุ้นตัวนั้น (AAA) และปิดแผ่น", w2 == {"tab": "watch", "sel": "AAA", "open": False}, w2)
        check(f"{tag} 3 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def import_tests(pw):
    tag = f"[{ENGINE}/390px]"
    b, page, ce, pe = launch(pw, 390, 844)
    try:
        go_today(page)
        def paste(t):
            if not page.locator("#stkText").count(): page.locator("[data-stk-paste]").first.click(); settle(page, 300)
            js(page, "(t)=>{ const e = document.getElementById('stkText'); e.value = t; stkPaste.text = t; }", t if isinstance(t, str) else json.dumps(t, ensure_ascii=False))
            page.locator("[data-stk-check]").click(); settle(page, 300)
        bad = {"JSON พัง": "{x", "schema ผิด": {**stock_doc(), "schema": "x"}, "edition ≠ period_end": {**stock_doc(), "edition_id": "2026-10-01"}, "status ผิด": {**stock_doc(), "stocks": {"AAA": {"groups": ["candidate"], "coverage": "news", "status": "bullish", "headline_th": "x", "source_refs": []}}},
               "source_refs ขาด": {**stock_doc(), "stocks": {"AAA": {"groups": ["candidate"], "coverage": "news", "status": "info", "headline_th": "x", "source_refs": ["nope"]}}}, "news ไม่มีพาดหัว": {**stock_doc(), "stocks": {"AAA": {"groups": [], "coverage": "news", "status": "info", "source_refs": []}}}}
        for k, t in bad.items():
            paste(t)
            r = js(page, "()=>({e: (document.querySelector('[data-stk-errs]')||{}).innerText || null, save: !!document.querySelector('[data-stk-save]'), n: Object.keys(stkDocs).length})")
            check(f"{tag} 4 ผิด [{k}] → error สั้น ๆ · ไม่มีปุ่มบันทึก · ไม่เขียนอะไร", r["e"] and not r["save"] and r["n"] == 0, r)
        # permission-denied
        js(page, "()=>{ window.__oc2 = sat7dCol; sat7dCol = (n)=> n==='stockNews' ? {doc: ()=>({set: ()=>Promise.reject({code:'permission-denied'})})} : window.__oc2(n); }")
        evil = stock_doc(); evil["stocks"]["AAA"]["headline_th"] = "<img src=x onerror=window.__pwn=1>SAMPLE"
        paste(evil)
        page.locator("[data-stk-save]").click(); settle(page, 600)
        pd = js(page, "()=>({err: (document.querySelector('[data-stk-saveerr]')||{}).innerText || null, ta: (document.getElementById('stkText')||{}).value || '', n: Object.keys(stkDocs).length})")
        check(f"{tag} 4 permission-denied → ข้อความชัด (ต้องเพิ่ม Rules) · ข้อความที่วางยังอยู่ · ไม่เขียน", pd["err"] and "permission-denied" in pd["err"] and "Rules" in pd["err"] and "SAMPLE" in pd["ta"] and pd["n"] == 0, pd)
        js(page, "()=>{ sat7dCol = window.__oc2; }")
        page.locator("[data-stk-save]").click(); settle(page, 900)
        doc = page.evaluate("(i)=>window.firebase.__mockDb.__getDoc(['users','testuid','stockNews',i])", ED)
        check(f"{tag} 4 บันทึกสำเร็จ → เก็บที่ stockNews/{ED} · การ์ดอัปเดต (New)", doc and doc["schema"] == "stockNews/v1" and len(doc["stocks"]) == 8 and js(page, "()=>document.querySelector('[data-stk-card]').dataset.stkCard") == "new", doc and list(doc.keys()))
        go_today(page)
        page.locator("[data-stk-open]").click(); settle(page, 500)
        page.locator('[data-stk-toggle="AAA"]').click(); settle(page, 300)
        h = js(page, "()=>({img: document.querySelectorAll('#stkHost img, .stkHl img').length, pwn: window.__pwn || null, txt: document.querySelector('[data-stk-row=\"AAA\"] .stkHl').innerText})")
        check(f"{tag} 4 ข้อความจากไฟล์แสดงเป็นข้อความ ไม่ใช่ HTML (ไม่มี <img> ไม่รันสคริปต์)", h["img"] == 0 and h["pwn"] is None and "<img" in h["txt"], h)
        # manifest
        m = js(page, "()=>stkManifest()")
        check(f"{tag} 4 รายชื่อหุ้นสำหรับสกิล: ticker + groups (CCC อยู่ทั้งสองกลุ่ม ครั้งเดียว)", [x["ticker"] for x in m["stocks"]] == ["AAA", "CCC", "BBB", "DDD", "EEE", "GGG", "HHH"] and [x for x in m["stocks"] if x["ticker"] == "CCC"][0]["groups"] == ["candidate", "watchlist"], m)
        check(f"{tag} 4 ไม่มี console error", not ce and not pe, [ce[:2], pe[:2]])
    finally: b.close()


def main():
    with sync_playwright() as pw:
        order_tests(pw, 390, 844, "390px", shots=True)
        order_tests(pw, 300, 700, "300px")
        order_tests(pw, 1280, 800, "1280px")
        order_tests(pw, 1440, 900, "1440px", shots=True)
        card_tests(pw)
        sheet_tests(pw, 390, 844, "390px", shots=True)
        sheet_tests(pw, 300, 700, "300px")
        sheet_tests(pw, 1440, 900, "1440px", shots=True)
        import_tests(pw)
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)}/{len(results)} passed")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
