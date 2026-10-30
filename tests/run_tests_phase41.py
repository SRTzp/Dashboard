#!/usr/bin/env python3
"""WL3 — การ์ด Thesis อ่านง่ายขึ้น: คำศัพท์ [[ ]] · ชื่อหัวข้อสรุป · ปุ่ม ← → เปลี่ยนแท็บ · เทส 41
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-03 · fixture tests/fixtures/avgo_thesis_v3.json (+ avgo_thesis.json = thesis เก่า)
ภาพ tests/screenshots/wl3-{sum,term-pop,glossary-open,old-thesis}-{1440,390}.png
รัน: python3 run_tests_phase41.py"""
import copy, json, os, sys
from playwright.sync_api import sync_playwright
import run_tests_phase40 as P40

P, P39 = P40.P, P40.P39
HERE = P40.HERE
ENGINE = P40.ENGINE
CLK = P39.CLK_SAT          # 2026-10-03 13:03 ไทย
V3 = json.load(open(os.path.join(HERE, "fixtures", "avgo_thesis_v3.json"), encoding="utf-8"))
OLD = P40.FX
results = P40.results
check, shot, seed_wl, wdb, go_watch, body_txt, txt_of, cnt, tab, js = (P40.check, P40.shot, P40.seed_wl, P40.wdb, P40.go_watch, P40.body_txt, P40.txt_of, P40.cnt, P40.tab, P40.js)
SUBS = ["sum", "biz", "why", "trk", "exit"]


def launch(pw, w, h, extra=None):
    return P40.launch(pw, w, h, extra=extra, iso=CLK)


def key(page, k):
    page.keyboard.press(k); page.wait_for_timeout(120)


def overflow(page): return js(page, "()=>document.documentElement.scrollWidth - window.innerWidth")


def v3(**mods):
    d = copy.deepcopy(V3)
    for k, v in mods.items(): d[k] = v
    return d


def main_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")
    # ───── 1 · Import v3 ─────
    browser, context, page, ce, pe, dialogs = launch(pw, w, h)
    try:
        go_watch(page)
        P40.promoted(page, "AVGO")
        err, prev = P40.import_via_ui(page, json.dumps(V3, ensure_ascii=False), top=True)
        d = wdb(page).get("AVGO") or {}
        terms = (d.get("thesis") or {}).get("terms")
        check(f"{tag} 1 Import v3 ผ่าน · thesis.terms = 4 รายการ (ตัดซ้ำ xpu)", err == "" and isinstance(terms, list) and len(terms) == 4 and [t["k"] for t in terms] == ["XPU", "VMware", "substrate", "gross margin"], json.dumps([err, terms], ensure_ascii=False))
        check(f"{tag} 1 การ์ด AVGO เปิดปกติ 6 แท็บ (VW1 เพิ่ม มุมมอง)", js(page, "()=>wlSel") == "AVGO" and cnt(page, "[data-lt-tab]") == 6)
        bad = {}
        for k in SUBS:
            tab(page, k); t = body_txt(page)
            bad[k] = [x for x in ("[[", "]]", "undefined", "[object") if x in t]
        check(f"{tag} 1 ไม่มี [[ ]] / undefined บนจอทุกแท็บ", all(not v for v in bad.values()), json.dumps(bad))
        check(f"{tag} 1 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()

    # ───── 2–6 · คำศัพท์ · กล่อง · แถบพับ · หัวข้อ ─────
    def ex(pg): seed_wl(pg, "AVGO", v3())
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, ex)
    try:
        go_watch(page, "AVGO", "sum")
        # 6 · ชื่อหัวข้อ
        labels = js(page, "()=>[...document.querySelectorAll('.ltSum dt')].map(e=>e.innerText.trim())")
        check(f"{tag} 6 ป้าย Power (moat) · Capital allocation", "Power (moat)" in labels and "Capital allocation" in labels, json.dumps(labels, ensure_ascii=False))
        dk = js(page, "()=>[...document.querySelectorAll('[data-lt-decide] .dk')].map(e=>e.innerText.trim())")
        check(f"{tag} 6 กล่องตัดสินใจ: ข้อสรุป · Thesis breaker · ถัดไป", dk == ["ข้อสรุป", "Thesis breaker", "ถัดไป"], json.dumps(dk, ensure_ascii=False))
        t = body_txt(page)
        check(f"{tag} 6 ไม่มีคำ ออกถ้า / เครื่องยนต์ ในแท็บสรุป", "ออกถ้า" not in t and "เครื่องยนต์" not in t)
        ov = js(page, """()=>{ const bad=[]; document.querySelectorAll('[data-lt-decide] .dr').forEach(r=>{ const k=r.querySelector('.dk').getBoundingClientRect(), v=r.children[1].getBoundingClientRect(); if(k.right>v.left+0.5 && k.bottom>v.top+0.5 && k.top<v.bottom-0.5) bad.push(r.dataset.ltK); if(r.querySelector('.dk').scrollWidth>r.querySelector('.dk').clientWidth+1) bad.push(r.dataset.ltK+':clip'); }); return bad; }""")
        check(f"{tag} 6 ป้ายไม่ซ้อนข้อความ/ไม่ตัดคำ", ov == [], json.dumps(ov))
        shot(page, f"wl3-sum-{sfx}.png")

        # 2 · .ltTerm
        n_xpu = js(page, "()=>[...document.querySelectorAll('.ltTerm')].filter(e=>e.dataset.term==='XPU').length")
        ttl = js(page, "()=>{ const e=[...document.querySelectorAll('.ltTerm')].find(x=>x.dataset.term==='XPU'); return e && e.getAttribute('title'); }")
        check(f"{tag} 2 [[XPU]] ในสรุป = .ltTerm + title ความหมาย", n_xpu >= 1 and ttl and "custom accelerator" in ttl, str(ttl))
        tab(page, "biz")
        info = js(page, """()=>{ const g=n=>[...document.querySelectorAll('.wlDBody .ltTerm')].filter(e=>e.dataset.term===n); return {xpu:g('XPU').length, sub:g('substrate').length, gm:g('gross margin').length, tag:g('XPU')[0] && g('XPU')[0].tagName, noterm:g('NOTERM').length}; }""")
        check(f"{tag} 2 ธุรกิจ: XPU · substrate · gross margin เป็น .ltTerm (ปุ่ม)", info["xpu"] == 1 and info["sub"] == 1 and info["tag"] == "BUTTON", json.dumps(info))
        nt = js(page, "()=>({btn: document.querySelectorAll('.wlDBody .ltTerm[data-term=\"NOTERM\"]').length, txt: document.querySelector('.wlDBody').innerText.includes('NOTERM ไม่มีคำอธิบาย')})")
        check(f"{tag} 2 [[NOTERM]] = ข้อความเฉย ๆ ไม่ใช่ .ltTerm", nt["btn"] == 0 and nt["txt"], json.dumps(nt))
        style = js(page, "()=>{ const e=document.querySelector('.wlDBody .ltTerm'); const c=getComputedStyle(e); const p=getComputedStyle(e.parentElement); return {deco:c.textDecorationLine+' '+c.textDecorationStyle, bg:c.backgroundColor, bw:c.borderTopWidth, fs:c.fontSize===p.fontSize}; }")
        check(f"{tag} 2 หน้าตา: เส้นใต้ประ · ไม่มีกรอบ/พื้น · ขนาดเท่าข้อความรอบ", "underline" in style["deco"] and "dotted" in style["deco"] and style["bw"] == "0px" and style["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and style["fs"], json.dumps(style))

        # 3 · กล่องความหมาย
        def pop_count(): return cnt(page, "#ltTermPop")
        page.click('.wlDBody .ltTerm[data-term="XPU"]'); page.wait_for_timeout(150)
        pt = txt_of(page, "#ltTermPop") or ""
        check(f"{tag} 3 กดคำ → กล่อง 1 กล่อง มีคำ + ความหมาย", pop_count() == 1 and "XPU" in pt and "custom accelerator" in pt, pt)
        shot(page, f"wl3-term-pop-{sfx}.png")
        box = js(page, "()=>{ const r=document.getElementById('ltTermPop').getBoundingClientRect(); return {l:r.left,r:r.right,t:r.top,b:r.bottom,vw:document.documentElement.clientWidth,vh:innerHeight}; }")
        check(f"{tag} 3 กล่องอยู่ในจอ (0–{w}px)", box["l"] >= 0 and box["r"] <= box["vw"] and box["t"] >= 0 and box["b"] <= box["vh"], json.dumps(box))
        top_ok = js(page, """()=>{ const e=document.querySelector('.wlDBody .ltTerm[data-term="XPU"]'); const r=e.getBoundingClientRect(); const el=document.elementFromPoint(r.left+r.width/2, r.top+r.height/2); return el===e || e.contains(el); }""")
        check(f"{tag} 3 elementFromPoint ของคำ = ปุ่มคำ (ไม่ถูกบัง)", top_ok)
        page.click('.wlDBody .ltTerm[data-term="XPU"]'); page.wait_for_timeout(100)
        check(f"{tag} 3 กดคำเดิมซ้ำ → ปิด", pop_count() == 0)
        page.click('.wlDBody .ltTerm[data-term="XPU"]'); page.wait_for_timeout(100)
        page.click('.wlDHead .wlDT'); page.wait_for_timeout(100)
        check(f"{tag} 3 กดที่อื่น → ปิด", pop_count() == 0)
        page.click('.wlDBody .ltTerm[data-term="XPU"]'); page.wait_for_timeout(100); key(page, "Escape")
        check(f"{tag} 3 Esc → ปิด", pop_count() == 0)
        js(page, "()=>document.querySelector('.wlDBody .ltTerm[data-term=\"substrate\"]').scrollIntoView({block:'center'})"); page.wait_for_timeout(250)
        page.click('.wlDBody .ltTerm[data-term="XPU"]'); page.wait_for_timeout(100)
        page.click('.wlDBody .ltTerm[data-term="substrate"]'); page.wait_for_timeout(100)
        pt = txt_of(page, "#ltTermPop") or ""
        check(f"{tag} 3 กดคำอื่น → ยังกล่องเดียว (ของคำใหม่)", pop_count() == 1 and "substrate" in pt and "XPU" not in pt, json.dumps([pop_count(), pt], ensure_ascii=False))
        page.wait_for_timeout(350)
        js(page, "()=>{ const b=document.querySelector('.wlDBody'); b.scrollTop += 40; window.scrollBy(0,40); window.dispatchEvent(new Event('scroll')); }")
        page.mouse.wheel(0, 80); page.wait_for_timeout(250)
        check(f"{tag} 3 เลื่อนหน้า → ปิด", pop_count() == 0)
        page.focus('.wlDBody .ltTerm[data-term="XPU"]'); key(page, "Enter")
        check(f"{tag} 3 Enter บนคำ → เปิดกล่อง", pop_count() == 1)
        key(page, "Escape")

        # 5 · แถบพับ คำศัพท์
        pos = {}
        for k in SUBS:
            tab(page, k)
            pos[k] = js(page, """()=>{ const f=[...document.querySelectorAll('.wlDBody [data-lt-fold]')]; const gl=f.findIndex(e=>e.dataset.ltFold==='gl'), ev=f.findIndex(e=>e.dataset.ltFold==='evd'); const bar=document.querySelector('[data-lt-fold="gl"] .ltFoldBar'); return {gl, ev, text: bar && bar.innerText.replace(/\\s+/g,' ').trim(), open: !!document.querySelector('[data-lt-fold="gl"].open')}; }""")
        check(f"{tag} 5 'คำศัพท์ · 5 คำ' อยู่ท้ายทุกแท็บ · ค่าเริ่มต้นพับ", all(v["text"] and v["text"].startswith("คำศัพท์ · 5 คำ") and not v["open"] for v in pos.values()), json.dumps(pos, ensure_ascii=False))
        check(f"{tag} 5 อยู่เหนือแถบหลักฐาน (แท็บที่มีหลักฐาน)", all(v["ev"] < 0 or v["gl"] < v["ev"] for v in pos.values()) and any(v["ev"] >= 0 for v in pos.values()), json.dumps(pos))
        tab(page, "biz"); page.click('[data-lt-fold="gl"] .ltFoldBar'); page.wait_for_timeout(150)
        rows = js(page, "()=>[...document.querySelectorAll('[data-lt-fold=\"gl\"] li')].map(e=>({t:e.dataset.ltGl, x:e.innerText.replace(/\\s+/g,' ').trim()}))")
        terms = sorted([t["k"] for t in V3["terms"] if t["k"] != "xpu"], key=lambda s: s.lower())
        got = [r["x"].split(" — ")[0] for r in rows if r["t"] == "term"]
        creds = [r["x"].split(" — ")[0] for r in rows if r["t"] == "cred"]
        check(f"{tag} 5 กางแล้ว 4 คำเรียง A→Z + ป้าย Mgmt เท่านั้น", got == terms and creds == ["Mgmt"], json.dumps([got, creds, rows], ensure_ascii=False))
        check(f"{tag} 5 แถวแสดง 'คำ — ความหมาย'", any("XPU — ชิป AI" in r["x"] for r in rows), json.dumps(rows, ensure_ascii=False))
        cr = js(page, """()=>{ const e=document.querySelector('.wlDBody .ltCr'); if(!e) return null; const p=getComputedStyle(e.parentElement).color, c=getComputedStyle(e).color; return {txt:e.innerText, same:p===c, btn:e.tagName}; }""")
        check(f"{tag} 5 คำ Mgmt ในเนื้อหาเป็นสีเทา (ไม่ใช่ปุ่ม)", cr and cr["txt"] == "Mgmt" and not cr["same"] and cr["btn"] == "SPAN", json.dumps(cr))
        shot(page, f"wl3-glossary-open-{sfx}.png")
        check(f"{tag} 2–6 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()

    # ───── 5 · thesis เก่า ─────
    def exo(pg): seed_wl(pg, "AVGO", copy.deepcopy(OLD))
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, exo)
    try:
        go_watch(page, "AVGO", "biz")
        check(f"{tag} 5 thesis เก่า: ไม่มีแถบ คำศัพท์", all(cnt(page, '[data-lt-fold="gl"]') == 0 for _ in [0]) and all((tab(page, k), cnt(page, '[data-lt-fold="gl"]'))[1] == 0 for k in SUBS))
        tab(page, "biz")
        old = js(page, "()=>({chip: document.querySelectorAll('.wlDBody .ltTg').length, term: document.querySelectorAll('.ltTerm').length, cr: document.querySelectorAll('.ltCr').length})")
        check(f"{tag} 5 ป้าย [F][M] ใน thesis เก่ายังเป็น chip · ไม่มี .ltTerm/.ltCr", old["chip"] > 0 and old["term"] == 0 and old["cr"] == 0, json.dumps(old))
        tab(page, "sum")
        lbl = js(page, "()=>[...document.querySelectorAll('.ltSum dt')].map(e=>e.innerText.trim())")
        check(f"{tag} 6 thesis เก่าก็ใช้ป้ายใหม่ (Power (moat) · Capital allocation)", "Power (moat)" in lbl and "Capital allocation" in lbl, json.dumps(lbl, ensure_ascii=False))
        shot(page, f"wl3-old-thesis-{sfx}.png")
        check(f"{tag} 5 thesis เก่า: ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()

    # ───── 4 · XSS ─────
    x = v3()
    x["terms"] = x["terms"] + [{"k": "x", "th": "<img src=x onerror=alert(1)>"}]
    x["sections"]["s2"]["md"] = "ทดสอบ [[x]] และ [[<b>x</b>]] จบ"
    def exx(pg): seed_wl(pg, "AVGO", x)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, exx)
    try:
        go_watch(page, "AVGO", "why")
        txt = body_txt(page)
        check(f"{tag} 4 [[<b>x</b>]] แสดงเป็นตัวอักษร · ไม่มี element ใหม่", "<b>x</b>" in txt and cnt(page, ".wlDBody .ltMd b") == 0 and cnt(page, ".wlDBody img") == 0, txt[:200])
        page.click('.wlDBody .ltTerm[data-term="x"]'); page.wait_for_timeout(150)
        pt = txt_of(page, "#ltTermPop") or ""
        check(f"{tag} 4 terms[].th = <img…> → แสดงเป็นตัวอักษรในกล่อง · ไม่มี <img> · ไม่มี alert", "<img src=x onerror=alert(1)>" in pt and cnt(page, "#ltTermPop img") == 0 and cnt(page, ".wlDBody img") == 0 and not dialogs, json.dumps([pt, dialogs]))
        key(page, "Escape")
        page.click('[data-lt-fold="gl"] .ltFoldBar'); page.wait_for_timeout(120)
        check(f"{tag} 4 แถบคำศัพท์: ไม่มี <img> หลุด", cnt(page, "[data-lt-fold=\"gl\"] img") == 0 and "<img src=x" in (txt_of(page, '[data-lt-fold="gl"]') or ""))
        check(f"{tag} 4 ไม่มี console error", not pe, json.dumps([ce, pe]))
    finally:
        browser.close()

    # ───── 12 · คำที่มี & หรือ ' (WL3fix) ─────
    y = v3()
    y["terms"] = y["terms"] + [{"k": "R&D", "th": "ค่าวิจัยและพัฒนา"}, {"k": "S&P 500", "th": "ดัชนีหุ้นใหญ่สหรัฐ 500 ตัว"}, {"k": "Moody's", "th": "บริษัทจัดอันดับเครดิต"}]
    y["sections"]["s2"]["md"] = "ทดสอบ [[R&D]] และ [[s&p 500]] และ [[Moody's]] จบ"
    def exy(pg): seed_wl(pg, "AVGO", y)
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, exy)
    try:
        go_watch(page, "AVGO", "why")
        info = js(page, """()=>{ const o={}; [...document.querySelectorAll('.wlDBody .ltTerm')].forEach(e=>{ o[e.dataset.term]={title:e.getAttribute('title'), txt:e.textContent, tag:e.tagName}; }); return o; }""")
        want = {"R&D": "ค่าวิจัยและพัฒนา", "s&p 500": "ดัชนีหุ้นใหญ่สหรัฐ 500 ตัว", "Moody's": "บริษัทจัดอันดับเครดิต"}
        check(f"{tag} 12 [[R&D]] [[s&p 500]] [[Moody's]] = .ltTerm ปุ่ม + title ความหมาย", all(k in info and info[k]["title"] == v and info[k]["tag"] == "BUTTON" and "&amp;" not in info[k]["txt"] for k, v in want.items()), json.dumps(info, ensure_ascii=False))
        page.click('.wlDBody .ltTerm[data-term="R&D"]'); page.wait_for_timeout(150)
        pt = txt_of(page, "#ltTermPop") or ""
        check(f"{tag} 12 กด [[R&D]] → กล่องแสดง R&D · ไม่มี &amp; บนจอ", "R&D" in pt and "ค่าวิจัยและพัฒนา" in pt and "&amp;" not in pt, pt)
        check(f"{tag} 12 ไม่มี console error", not pe and not dialogs, json.dumps([ce, pe, dialogs]))
    finally:
        browser.close()


def terms_parse_tests(pw):
    """ltParse: terms ไม่ใช่ array / รายการเสีย / เกินขีด"""
    browser, context, page, ce, pe, dialogs = launch(pw, 1440, 900)
    try:
        def parse(**mods): return js(page, "(t)=>{ const r = ltParse(t, ''); return r.err ? {err:r.err} : r.th.terms; }", json.dumps(v3(**mods), ensure_ascii=False))
        check("[parse] ไม่มี terms = []", parse(terms=None) == [] or js(page, "(t)=>ltParse(t,'').th.terms", json.dumps({k: v for k, v in V3.items() if k != "terms"}, ensure_ascii=False)) == [])
        check("[parse] terms ไม่ใช่ array = []", parse(terms="abc") == [] and parse(terms={"k": "a"}) == [])
        bad = [{"k": "", "th": "a"}, {"k": "ok", "th": 5}, {"k": "k" * 41, "th": "a"}, {"k": "good", "th": "a" * 201}, "str", None, {"k": "fine", "th": "a" * 200}, {"k": "Fine", "th": "dup"}]
        r = parse(terms=bad)
        check("[parse] เก็บเฉพาะ k ไม่ว่าง ≤40 / th ≤200 · ตัดซ้ำ (ไม่สนตัวพิมพ์)", r == [{"k": "fine", "th": "a" * 200}], json.dumps(r, ensure_ascii=False)[:200])
        r = parse(terms=[{"k": f"t{i}", "th": "x"} for i in range(80)])
        check("[parse] ≤ 50 รายการ", isinstance(r, list) and len(r) == 50)
    finally:
        browser.close()


def key_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    def ex(pg):
        seed_wl(pg, "AVGO", v3())
        pg.evaluate("([p,d])=>window.firebase.__mockDb.__seedDoc(p, d)", [["users", "testuid", "watchlist", "NVDA"], {"ticker": "NVDA", "market": "US", "port": "core", "note": "", "industry": "", "added_at": "2026-01-01T00:00:00.000Z"}])
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, ex)
    try:
        go_watch(page, "AVGO", "sum")
        page.evaluate("()=>document.activeElement && document.activeElement.blur()")
        # 7 · ← →
        seq = []
        for _ in range(4): key(page, "ArrowRight"); seq.append(js(page, "()=>wlSub"))
        check(f"{tag} 7 → ×4 = มุมมอง → ธุรกิจ → ทำไมซื้อ → ติดตาม (VW1)", seq == ["view", "biz", "why", "trk"], json.dumps(seq))
        key(page, "ArrowRight")
        check(f"{tag} 7 → อีก = ยังออกเมื่อ (ไม่วน)", js(page, "()=>wlSub") == "exit")
        mem = js(page, "()=>ltSubMem('AVGO')")
        js(page, "()=>{ wlSub=''; renderWatchlist(); }")
        check(f"{tag} 7 จำแท็บต่อ ticker (เหมือนรีโหลด) = ออกเมื่อ", mem == "exit" and js(page, "()=>document.querySelector('.ltTab.on').dataset.ltTab") == "exit")
        seq = []
        for _ in range(4): key(page, "ArrowLeft"); seq.append(js(page, "()=>wlSub"))
        check(f"{tag} 7 ← ×4 = ติดตาม → ทำไมซื้อ → ธุรกิจ → มุมมอง (VW1)", seq == ["trk", "why", "biz", "view"], json.dumps(seq))
        key(page, "ArrowLeft")
        check(f"{tag} 7 ← อีก = ยังสรุป", js(page, "()=>wlSub") == "sum")
        key(page, "ArrowRight")
        on_vis = js(page, """()=>{ const on=document.querySelector('.ltTab.on'), tb=document.querySelector('[data-lt-tabs]'); const a=on.getBoundingClientRect(), b=tb.getBoundingClientRect(); return a.left>=b.left-1 && a.right<=b.right+1; }""")
        check(f"{tag} 7 แท็บที่เลือกใหม่อยู่ในแถบ/จอ", on_vis)

        # 8 · ไม่ทำงาน
        tab(page, "trk")
        js(page, "()=>wlNoteOpen('AVGO','blk')"); page.wait_for_timeout(100)
        page.focus("#wlNoteText"); key(page, "ArrowRight")
        check(f"{tag} 8 โฟกัสช่องพิมพ์ (โน้ต) → ไม่เปลี่ยนแท็บ", js(page, "()=>wlSub") == "trk")
        js(page, "()=>wlNoteClose()"); page.evaluate("()=>document.activeElement && document.activeElement.blur()")
        page.keyboard.press("Shift+ArrowRight"); page.wait_for_timeout(100)
        check(f"{tag} 8 Shift+→ → ไม่เปลี่ยนแท็บ", js(page, "()=>wlSub") == "trk")
        for m in ("Control", "Alt", "Meta"):
            page.keyboard.press(f"{m}+ArrowRight"); page.wait_for_timeout(60)
        check(f"{tag} 8 Ctrl/Alt/Cmd+→ → ไม่เปลี่ยนแท็บ", js(page, "()=>wlSub") == "trk")
        page.click("[data-lt-import]"); page.wait_for_selector("#ltJson", state="visible")
        page.evaluate("()=>document.activeElement && document.activeElement.blur()"); key(page, "ArrowRight")
        check(f"{tag} 8 sheet Import เปิด → ไม่เปลี่ยนแท็บ", js(page, "()=>wlSub") == "trk")
        page.fill("#ltJson", "abc"); key(page, "ArrowLeft")
        check(f"{tag} 8 พิมพ์ใน Import textarea → ไม่เปลี่ยนแท็บ", js(page, "()=>wlSub") == "trk")
        page.keyboard.press("Escape"); js(page, "()=>{ document.querySelectorAll('.overlay.show').forEach(e=>e.classList.remove('show')); ltImp=null; }")
        page.evaluate("()=>document.activeElement && document.activeElement.blur()")
        page.click('.wlDBody .ltTerm, [data-lt-tab="biz"]') if False else None
        tab(page, "biz"); page.click('.wlDBody .ltTerm[data-term="XPU"]'); page.wait_for_timeout(100); key(page, "ArrowRight")
        check(f"{tag} 8 กล่องคำศัพท์เปิดอยู่ → ไม่เปลี่ยนแท็บ (ปิดก่อน)", js(page, "()=>wlSub") == "biz" and cnt(page, "#ltTermPop") == 1)
        key(page, "Escape"); key(page, "ArrowRight")
        check(f"{tag} 8 ปิดกล่องแล้ว → เปลี่ยนแท็บได้", js(page, "()=>wlSub") == "why")
        js(page, "()=>ltMenuToggle('AVGO')"); page.wait_for_timeout(100)
        key(page, "ArrowRight")
        check(f"{tag} 8 เมนู ⋯ เปิด → ไม่เปลี่ยนแท็บ", js(page, "()=>wlSub") == "why")
        js(page, "()=>{ wlMenu=''; renderWatchlist(); }")
        # การ์ดไม่มี thesis
        js(page, "()=>wlOpen('NVDA')"); page.wait_for_timeout(200)
        before = js(page, "()=>[wlSel, wlSub]"); key(page, "ArrowRight"); key(page, "ArrowLeft")
        check(f"{tag} 8 การ์ดไม่มี thesis → ไม่เปลี่ยน/ไม่ error", js(page, "()=>[wlSel, wlSub]") == before and not pe, json.dumps([before, pe]))
        # แท็บ Today / แผน
        for t in ("today", "plan"):
            js(page, f"()=>switchTab('{t}')"); page.wait_for_timeout(200)
            key(page, "ArrowRight"); key(page, "ArrowLeft")
            check(f"{tag} 8 แท็บ {t}: ← → ไม่ทำอะไร · ไม่มี error", js(page, "()=>activeTab") == t and not pe, json.dumps(pe))
        js(page, "()=>switchTab('watch')"); page.wait_for_timeout(200)

        # 9 · ↑ ↓ (จอใหญ่)
        if w >= 1024:
            js(page, "()=>wlOpen('AVGO','sum')"); page.wait_for_timeout(150)
            page.evaluate("()=>document.activeElement && document.activeElement.blur()")
            a = js(page, "()=>wlSel"); key(page, "ArrowDown"); b = js(page, "()=>wlSel")
            first, second = ("ArrowUp", "ArrowDown") if b == a else ("ArrowDown", "ArrowUp")
            if b == a: key(page, "ArrowUp"); b = js(page, "()=>wlSel")
            key(page, second if b != a else first); c = js(page, "()=>wlSel")
            check(f"{tag} 9 ↑ ↓ ยังเลื่อนหุ้นเหมือนเดิม (ไปแล้วกลับ)", a == "AVGO" and b != a and c == a, json.dumps([a, b, c]))
        # 10 · หน้าคีย์ลัด
        key(page, "?") if False else js(page, "()=>openKbHelp()")
        kb = txt_of(page, "#kbHelpOverlay") or ""
        check(f"{tag} 10 หน้าคีย์ลัดมีบรรทัด ← → เปลี่ยนแท็บการ์ด", "← →" in kb and "เปลี่ยนแท็บการ์ด" in kb, kb[:300])
        check(f"{tag} 7–10 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


def layout_tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"
    def ex(pg): seed_wl(pg, "AVGO", v3())
    browser, context, page, ce, pe, dialogs = launch(pw, w, h, ex)
    try:
        go_watch(page, "AVGO", "sum")
        ov = {}
        for k in SUBS:
            tab(page, k); ov[k] = overflow(page)
            if page.locator('[data-lt-fold="gl"] .ltFoldBar').count(): page.click('[data-lt-fold="gl"] .ltFoldBar'); page.wait_for_timeout(100); ov[k + "+gl"] = overflow(page)
        check(f"{tag} 11 ไม่ล้นแนวนอนทุกแท็บ (รวมกางคำศัพท์)", all(v <= 0 for v in ov.values()), json.dumps(ov))
        check(f"{tag} 11 ไม่มี console error", not ce and not pe, json.dumps([ce, pe]))
    finally:
        browser.close()


def static_tests():
    html = open(os.path.join(HERE, "..", "index.html"), encoding="utf-8").read()
    check("[static] มี ltTerm / ltGlossFold / LT_CRED และคีย์ลัด ← →", all(x in html for x in ("class=\"ltTerm\"", "function ltGlossFold(", "const LT_CRED", "['← →'")))
    check("[static] สำรอง index.backup-pre-WL3.html + tests/_bk_wl3/ อยู่", os.path.exists(os.path.join(HERE, "..", "index.backup-pre-WL3.html")) and os.path.isdir(os.path.join(HERE, "_bk_wl3")))


def main():
    static_tests()
    with sync_playwright() as pw:
        terms_parse_tests(pw)
        for (w, h, label) in ((1440, 900, "1440px"), (390, 844, "390px")):
            main_tests(pw, w, h, label)
            key_tests(pw, w, h, label)
            layout_tests(pw, w, h, label)
    n_pass = sum(1 for _, ok, _ in results if ok); n_fail = len(results) - n_pass
    print("\n==== SUMMARY (Phase 41 / WL3) ====")
    print(f"engine={ENGINE}  PASS: {n_pass}  FAIL: {n_fail}  TOTAL: {len(results)}")
    if n_fail:
        print("\nFAILURES:")
        for name, ok, detail in results:
            if not ok: print(" -", name, "::", (detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False))[:300])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
