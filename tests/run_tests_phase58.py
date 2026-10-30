#!/usr/bin/env python3
"""GL3 — การบ้าน research แบ่ง 5 part + ดึงหุ้นจาก Candidates · เทส 58
mock Firestore · Chromium 1440 + 390 · นาฬิกาปลอม 2026-10-08 (พฤ.)
ภาพ tests/screenshots/gl3-hw-{1440,390}.png · gl3-daily-390.png
รัน: python3 run_tests_phase58.py"""
import copy, json, os
from playwright.sync_api import sync_playwright
import run_tests_phase56 as G
import run_tests_phase44 as P44
import run_tests_phase39 as P39
import run_tests_phase38 as P38
import run_tests_phase4 as base

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = base.BROWSER_ENGINE
results = G.results
check, js, txt, count, wait, shot = G.check, G.js, G.txt, G.count, G.wait, G.shot
TODAY = G.TODAY
BACKUP = os.path.abspath(os.path.join(HERE, "..", "index.backup-pre-GL3.html"))
PARTS = ["biz", "why", "next", "exit", "tier"]


def wl_doc(t, **kw): return P38.wl_th(t, **kw)


def cand(sym, name, rank, state="wait"): return P44.cand(sym, name, rank, state, src="10-K ตัวอย่าง")


def idea(cands, iid="idea-gl3"):
    d = copy.deepcopy(P44.SEMIS); d["id"] = iid; d["name"] = "ธีมทดสอบ"; d["date"] = "2026-10-02"; d["status"] = "need_evidence"
    d["candidates"] = cands; d["losers"] = []; d["assets"] = []
    return d


def launch(pw, w, h, wl=("ABC", "DEF"), ideas=(), log=None, mut=None, index=None):
    def extra(page):
        for t in wl: P39.seed(page, ["users", "testuid", "watchlist", t], wl_doc(t))
        for it in ideas: P44.seed_idea(page, it)
    doc = P38.doc38(clean=True, log=log if log is not None else {})
    if mut: mut(doc)
    saved = P39.INDEX
    if index: P39.INDEX = index
    try: r = P39.launch(pw, w, h, doc=doc, clean=True, iso=G.CLK, extra=extra)
    finally: P39.INDEX = saved
    r[2].wait_for_timeout(500)
    return r


def hw_row(page): return js(page, "()=>{ const r=document.querySelector('.tdRow[data-kind=\"homework\"]'); return r ? {t:r.querySelector('.tdWhat>b').textContent, src:(r.querySelector('[data-hw-src]')||{}).textContent||null, cnt:(r.querySelector('[data-hw-cnt]')||{}).textContent||null, on:[...r.querySelectorAll('.tdHp.on')].map(e=>e.dataset.hwPart)} : null; }")
def hw_log(page): return (G.settings(page, "routineLog") or {}).get(TODAY, {}).get("hw")
def tick(page, p): page.locator(f'[data-hw-part="{p}"]').first.click(); wait(page, 350)
def chips(page): return js(page, "()=>[...document.querySelectorAll('[data-gl-chip]')].map(e=>e.innerText.replace(/\\s+/g,' ').trim())")


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", ""); narrow = w < 500
    # ── 1 ไม่มีข้อมูลใหม่ → เหมือนก่อน GL3
    b1, c1, p1, ce, pe, _ = launch(pw, w, h)
    try:
        G.go_today(p1); new = hw_row(p1); reason = txt(p1, "[data-hw-reason]")
    finally: b1.close()
    b2, c2, p2, ce2, pe2, _ = launch(pw, w, h, index=BACKUP)
    try:
        G.go_today(p2); old = js(p2, "()=>{ const r=document.querySelector('.tdRow[data-kind=\"homework\"]'); return r ? r.querySelector('.tdWhat>b').textContent : null; }"); oreason = txt(p2, "[data-hw-reason]")
    finally: b2.close()
    check(f"{tag} 1 ไม่มีข้อมูลใหม่ → เสนอตัวเดิมเหมือนก่อน GL3 (ABC · เหตุผลเดิม) + ป้าย W", new and old and new["t"] == old == "ABC" and reason == oreason and new["src"] == "W" and new["cnt"] == "0/5", json.dumps([new, old, reason, oreason], ensure_ascii=False))

    # ── 2-3 ติ๊ก part
    b, c, page, ce, pe, _ = launch(pw, w, h)
    try:
        G.go_today(page)
        names = js(page, "()=>[...document.querySelectorAll('.tdRow[data-kind=homework] [data-hw-part]')].map(e=>e.innerText.trim())")
        check(f"{tag} 2 ชิปติ๊ก 5 ตัว ธุรกิจ · ทำไม · ติดตาม · ออก · Tier แทนปุ่ม ✓ เดิม (VW1 ข้อ 0: Next → ติดตาม)", names == ["Tier", "ธุรกิจ", "ทำไม", "ติดตาม", "ออก"] and count(page, "[data-hw-done-btn]") == 0, json.dumps(names, ensure_ascii=False))
        for p in ("biz", "why", "next"): tick(page, p)
        lg = hw_log(page); row = hw_row(page)
        check(f"{tag} 2 ติ๊ก biz why next → parts 3 ตัว · done:false · ตัวนับ 3/5", lg == {"pick": "ABC", "done": False, "parts": ["biz", "why", "next"]} and row["cnt"] == "3/5" and row["on"] == ["biz", "why", "next"], json.dumps([lg, row]))
        check(f"{tag} 2 Daily ชิป 'การบ้าน 3/5'", "การบ้าน 3/5" in chips(page), json.dumps(chips(page), ensure_ascii=False))
        tick(page, "why")
        check(f"{tag} 2 กดซ้ำ = ยกเลิก (why ออก → 2/5)", hw_log(page)["parts"] == ["biz", "next"] and hw_row(page)["cnt"] == "2/5")
        tick(page, "why")
        # ครบ 5
        shot(page, f"gl3-hw-{sfx}.png", ".tdRow[data-kind=homework]")
        hh = js(page, "()=>{ const r=document.querySelector('.tdRow[data-kind=homework]'); const bs=[...r.querySelectorAll('.tdHp')].map(b=>b.getBoundingClientRect()); const cnt=r.querySelector('[data-hw-cnt]').getBoundingClientRect(); const nm=r.querySelector('.tdWhat>b'); return {minH:Math.min(...bs.map(b=>b.height)), tops:(()=>{ const cs=bs.concat([cnt]).map(b=>b.top+b.height/2); return Math.max(...cs)-Math.min(...cs) < 4 ? 1 : 2; })(), ovf: document.documentElement.scrollWidth - innerWidth, trunc:getComputedStyle(nm).textOverflow, clipped: bs.some(b=>b.right > r.getBoundingClientRect().right)}; }")
        check(f"{tag} 8 ชิปสูง ≥ 32px · ชิป 5 + ตัวนับอยู่บรรทัดเดียว · ไม่ล้นแนวนอน · ชื่อหุ้น … เมื่อยาว", hh["minH"] >= 32 and hh["tops"] == 1 and hh["ovf"] <= 0 and hh["trunc"] == "ellipsis" and not hh["clipped"], json.dumps(hh))
        tick(page, "exit")
        check(f"{tag} 3 ก่อนครบ (4/5) → done:false · แถวยังอยู่", hw_log(page)["done"] is False and hw_row(page) is not None)
        tick(page, "tier")
        lg = hw_log(page)
        line = txt(page, "[data-hw-doneline]")
        check(f"{tag} 3 ติ๊กครบ 5 → done:true · แถวการบ้านหายเป็นสถานะเสร็จ (บรรทัด 'การบ้านวันนี้: ABC ✓' + ชิป 5/5)", lg["done"] is True and sorted(lg["parts"]) == sorted(PARTS) and hw_row(page) is None and line and line.startswith("การบ้านวันนี้: ABC") and count(page, "[data-hw-doneline] .tdHp.on") == 5 and "5/5" in line, json.dumps([lg, line], ensure_ascii=False))
        check(f"{tag} 3 Daily ชิป 'การบ้าน 5/5'", "การบ้าน 5/5" in chips(page))
        js(page, "()=>{ switchTab('flow'); switchTab('today'); }"); wait(page, 300)
        page.locator('[data-hw-doneline] [data-hw-part="tier"]').click(); wait(page, 400)
        lg = hw_log(page)
        check(f"{tag} 3 กด tier ออก → done:false · แถวกลับมา 4/5", lg["done"] is False and "tier" not in lg["parts"] and hw_row(page)["cnt"] == "4/5" and count(page, "[data-hw-doneline]") == 0, json.dumps(lg))
        # ── 7 เปลี่ยนตัว → parts ว่าง
        page.locator("[data-hw-next]").click(); wait(page, 400)
        lg = hw_log(page); row = hw_row(page)
        check(f"{tag} 7 เปลี่ยนตัว (ABC→DEF) → parts ว่าง · done:false · 0/5", lg == {"pick": "DEF", "done": False, "parts": []} and row["t"] == "DEF" and row["cnt"] == "0/5", json.dumps([lg, row]))
        # เปิดการ์ด
        page.locator(".tdRow[data-kind=homework] .tdWhat").click(); wait(page, 500)
        st = js(page, "()=>({tab:activeTab, sel:wlSel, view:wlView})")
        check(f"{tag} 2 กดแถวยังเปิดการ์ด Watchlist ของหุ้นนั้น (ปุ่มเปิดการ์ดคงเดิม) · กดชิปไม่เปิดการ์ด", st == {"tab": "watch", "sel": "DEF", "view": "wl"}, json.dumps(st))
        check(f"{tag} 8 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()
    # กดชิปไม่เปิดการ์ด
    b, c, page, ce, pe, _ = launch(pw, w, h)
    try:
        G.go_today(page); tick(page, "biz")
        check(f"{tag} 2 กดชิป ไม่ทำให้เปลี่ยนแท็บ", js(page, "()=>activeTab") == "today")
    finally: b.close()

    # ── 4 log เก่าไม่มี parts
    def legacy(doc): doc["books"]["main"]["settings"]["routineLog"] = {"2026-10-07": {"slots": [], "satState": {}, "hw": {"pick": "ABC", "done": True}}, "2026-10-06": {"slots": [], "satState": {}, "hw": {"pick": "DEF", "done": False}}, TODAY: {"slots": [], "satState": {}, "hw": {"pick": "ABC", "done": True}}}
    b, c, page, ce, pe, _ = launch(pw, w, h, log={}, mut=legacy)
    try:
        G.go_today(page)
        c7 = js(page, "()=>glDayStat('2026-10-07', tdLast).c.hw"); c6 = js(page, "()=>glDayStat('2026-10-06', tdLast).c.hw")
        check(f"{tag} 4 log เก่า {{pick, done:true}} ไม่มี parts → วันนั้นนับ 5/5 · done:false → 0/5", c7 == {"n": 5, "N": 5} and c6 == {"n": 0, "N": 5}, json.dumps([c7, c6]))
        check(f"{tag} 4 วันนี้เป็น log เก่า done:true → Daily 'การบ้าน 5/5' · แสดงสถานะเสร็จ", "การบ้าน 5/5" in chips(page) and count(page, "[data-hw-doneline]") == 1)
        raw = G.settings(page, "routineLog")
        check(f"{tag} 4 อ่านอย่างเดียว ไม่ migrate (log เดิมไม่ถูกเขียนทับ)", raw["2026-10-07"]["hw"] == {"pick": "ABC", "done": True} and raw[TODAY]["hw"] == {"pick": "ABC", "done": True})
        # แก้ part ของ log เก่า → ถือว่า 5 ครบเดิม แล้วเอาออก 1
        tick(page, "biz")
        lg = hw_log(page)
        check(f"{tag} 4 log เก่า done:true แล้วเอา part ออก → parts 4 ตัว (ไม่มี biz) · done:false", lg["done"] is False and lg["parts"] == ["why", "next", "exit", "tier"], json.dumps(lg))
    finally: b.close()

    # ── 5 Daily ตัวอย่าง 7/11 · 64% (WA1fix: เดิม 7/12 · 58%)
    def sample(doc):
        s = doc["books"]["main"]["settings"]
        s["routine"] = {"slots": [{"id": "s1", "start": "09:00", "end": "09:30", "name": "ก", "link": "none"}, {"id": "s2", "start": "17:30", "end": "18:00", "name": "ข", "link": "none"}], "satDaily": ["XAUUSD", "BTC", "S50", "BRENT"]}
        s["dailyExtra"] = [{"id": "x1", "name": "งานอื่น"}]
        s["routineLog"] = {TODAY: {"slots": ["s1"], "satState": {"XAUUSD": "ok", "BTC": "no"}, "hw": {"pick": "ABC", "done": False, "parts": ["biz", "why", "next"]}, "extra": ["x1"]}}
    b, c, page, ce, pe, _ = launch(pw, w, h, log={}, mut=sample)
    try:
        G.go_today(page)
        head = txt(page, "[data-gl-dpct]")
        check(f"{tag} 5 Daily: ช่วงเวลา 1/2 · Sat 2/3 (ok 1 no 1) · การบ้าน 3/5 · งานอื่น 1/1 → '7/11 · 64%' [WA1fix: Sat 3 ตลาดที่เลือก]", head == "7/11 · 64%" and chips(page) == ["ช่วงเวลา 1/2", "เช็กแผน Sat 2/3", "การบ้าน 3/5", "งานอื่น 1/1"], json.dumps([head, chips(page)], ensure_ascii=False))
        shot(page, f"gl3-daily-{sfx}.png", "[data-gl-pd]") if narrow else None
    finally: b.close()

    # ── 6 Candidates
    skip_log = {"2026-10-06": {"slots": [], "satState": {}, "hw": {"pick": "ABC", "done": True, "parts": PARTS}}, "2026-10-07": {"slots": [], "satState": {}, "hw": {"pick": "DEF", "done": True, "parts": PARTS}}}
    ideas = [idea([cand("CAA", "Cand A", 1, "study"), cand("CBB", "Cand B", 2, "wait"), cand("DEF", "Dup in WL", 3, "wait")])]
    b, c, page, ce, pe, _ = launch(pw, w, h, ideas=ideas, log=skip_log)
    try:
        G.go_today(page)
        lst = js(page, "()=>tdHomeworkCandidates().map(x=>[x.t, x.src, x.skip])")
        check(f"{tag} 6 รายการ: Watchlist ก่อน (ABC · DEF ข้าม) ตามด้วย Candidates CAA CBB · DEF ใน Candidate ไม่ซ้ำ", lst == [["ABC", "W", True], ["DEF", "W", True], ["CAA", "C", False], ["CBB", "C", False]], json.dumps(lst))
        row = hw_row(page)
        check(f"{tag} 6 W ถูกข้ามหมด → เสนอ Candidate ตัวแรก CAA + ป้าย C", row and row["t"] == "CAA" and row["src"] == "C", json.dumps(row))
        page.locator("[data-hw-next]").click(); wait(page, 400)
        r2 = hw_row(page)
        page.locator("[data-hw-next]").click(); wait(page, 400)
        r3 = hw_row(page)
        check(f"{tag} 6 ปุ่มถัดไปวนไป CBB แล้ววนกลับ CAA", r2["t"] == "CBB" and r2["src"] == "C" and r3["t"] == "CAA", json.dumps([r2, r3]))
        page.locator(".tdRow[data-kind=homework] .tdWhat").click(); wait(page, 500)
        st = js(page, "()=>({tab:activeTab, sel:wlSel, view:wlView})")
        check(f"{tag} 6 กดแถว Candidate ที่ไม่อยู่ Watchlist → เปิดแท็บ Watch › Candidates ที่แถวนั้น", st == {"tab": "watch", "sel": "CAA", "view": "cand"}, json.dumps(st))
        check(f"{tag} 6 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()

    # ── 7 ไม่มี Watchlist และ Candidates
    b, c, page, ce, pe, _ = launch(pw, w, h, wl=())
    b_old = None
    try:
        G.go_today(page)
        check(f"{tag} 7 ไม่มี Watchlist และ Candidates → ไม่มีแถวการบ้าน · ไม่มีเส้นสรุปการบ้าน · Daily ไม่มีชิปการบ้าน", hw_row(page) is None and count(page, "[data-hw-doneline]") == 0 and not any(x.startswith("การบ้าน") for x in chips(page)), json.dumps(chips(page), ensure_ascii=False))
        check(f"{tag} 7 console ไม่มี error", not ce and not pe, json.dumps(ce[:3] + pe[:3], ensure_ascii=False))
    finally: b.close()


def main():
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
