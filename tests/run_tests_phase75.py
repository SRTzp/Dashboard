#!/usr/bin/env python3
"""RR1 — หน้า Strategy (แท็บ แผน) วาดใหม่เฉพาะเมื่อข้อมูลเปลี่ยน · ภาพกราฟไม่โหลดใหม่ · ตัวที่เลือก/ช่องพิมพ์ไม่หาย · จองที่ภาพ · ?debug=render · เทส 75
mock Firestore (เขียนแล้วสะท้อน snapshot + __ping ทุก 300ms ระหว่างเทส) · Chromium 1440 + 390
ภาพ tests/screenshots/rr1-{stable,debug-badge}-{1440,390}.png
รัน: python3 run_tests_phase75.py"""
import json, os
from playwright.sync_api import sync_playwright
import run_tests_phase4 as base
import run_tests_phase37 as P37
import run_tests_phase59 as P59
import run_tests_phase11 as P11
import run_tests_phase51 as P51
import run_tests_phase69 as P69
import base64
PNG169 = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAKAAAABaCAIAAACwpMoFAAABQ0lEQVR4nO3OAQkAMQDEsEqZhEl4/6peRTkYhQgI5355GPNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVTMB1ExH0TFfBAV80FUzAdRMR9ExXwQFfNBVMwHUTEfRMV8EBXzQVQ/vnel0tIFHOkAAAAASUVORK5CYII=")   # ภาพ 160x90 (16:9 แบบภาพ TV จริง)

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "screenshots"); os.makedirs(SHOTS, exist_ok=True)
ENGINE = base.BROWSER_ENGINE
INDEX = P59.P39.INDEX
results = []
js = P37.js
wait, cnt, rect, txt, overflow = P59.wait, P59.cnt, P59.rect, P59.txt, P59.overflow
PICK = ["XAUUSD", "BTCUSD"]
CHART = {"url": P59.TV1, "at": "2026-10-09"}


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    detail = detail if isinstance(detail, str) else json.dumps(detail, ensure_ascii=False)
    d = (detail[:700] + "...") if (detail and len(detail) > 700) else detail
    print(("PASS" if ok else "FAIL") + " - " + name + (("  :: " + d) if (d and not ok) else ""))


def shot(page, name, sel=None):
    wait(page, 350)
    try:
        if sel and page.locator(sel).count(): page.locator(sel).first.screenshot(path=os.path.join(SHOTS, name))
        else: page.screenshot(path=os.path.join(SHOTS, name), full_page=False)
    except Exception as e: print("shot fail", name, e)


def launch(pw, w, h):
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, pick=PICK)
    return b, page, ce, pe, env


def seed(page, chart=CHART):
    js(page, "(c)=>{ satwWrite('XAUUSD', {bias:'Long', support:[3920,3860], resistance:[4080], invalidation:3840, chart:c}); satwWrite('BTCUSD', {bias:'Long', support:[60000], resistance:[70000], invalidation:58000}); }", chart)
    wait(page, 400)
    P37.go_sat(page); wait(page, 400)


def ping(page, meta=None): page.evaluate("(m)=>window.firebase.__mockDb.__ping(m)", meta)


def echo_burst(page, n=5, gap=300):
    """snapshot ที่ข้อมูลไม่เปลี่ยน: metadata-only 3 แบบสลับ + บังคับ refresh ของแอปที่มีจริง"""
    metas = [{"hasPendingWrites": True}, {"fromCache": True, "hasPendingWrites": True}, {}]
    for i in range(n):
        ping(page, metas[i % 3])
        js(page, "()=>{ try{ sat7dRefresh(); }catch(e){} try{ todayRefresh(); }catch(e){} }")
        page.wait_for_timeout(gap)


WATCH = """()=>{ const p = document.getElementById('satV3Panel'); window.__mut = 0; window.__draw = 0;
  if(window.__mo) window.__mo.disconnect();
  window.__mo = new MutationObserver(rs=>{ window.__mut += rs.length; }); window.__mo.observe(p, {childList:true, subtree:true, attributes:true, characterData:true});
  if(!p.__rcw){ p.__rcw = true; const f = p.replaceChildren.bind(p); p.replaceChildren = function(){ window.__draw++; return f.apply(null, arguments); }; }
  window.__img = document.querySelector('.ui-tile[data-key=XAUUSD] img'); return !!window.__img; }"""
SAME_IMG = "()=>{ const n = document.querySelector('.ui-tile[data-key=XAUUSD] img'); return !!n && n === window.__img && n.isConnected; }"
PLANS_TOP = "()=>{ const p = document.getElementById('satV3Panel'); const c = [...p.children].filter(x=>/Trade Plans/.test(x.innerText||'')).pop(); return c ? c.getBoundingClientRect().top + window.scrollY : null; }"


def tests(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"; sfx = label.replace("px", "")

    # 1 ขยับเมาส์บนการ์ด BTC 3 วิ + snapshot ซ้ำ → img เดิม · DOM ไม่ขยับ
    b, page, ce, pe, env = launch(pw, w, h)
    try:
        seed(page)
        check(f"{tag} 1 เตรียม: pick XAUUSD+BTC · XAUUSD มี <img> กราฟ", cnt(page, ".ui-tile[data-key=XAUUSD] .vwSat img") == 1 and cnt(page, ".ui-tile[data-key=BTCUSD]") == 1)
        check(f"{tag} 1 ตั้ง observer + เก็บ ref <img>", js(page, WATCH))
        box = page.locator(".ui-tile[data-key=BTCUSD]").first.bounding_box()
        for i in range(10):
            page.mouse.move(box["x"] + 20 + i * 6, box["y"] + 15 + (i % 3) * 10)
            echo_burst(page, 1, 300)
        check(f"{tag} 1 ขยับเมาส์ 3 วิ + snapshot ไม่เปลี่ยน 10 ครั้ง → MutationObserver ใน #satV3Panel = 0", js(page, "()=>window.__mut") == 0 and js(page, "()=>window.__draw") == 0, [js(page, "()=>window.__mut"), js(page, "()=>window.__draw")])
        check(f"{tag} 1 <img> XAUUSD เป็น node เดิม", js(page, SAME_IMG))
        check(f"{tag} 1 ขอภาพจากเครือข่ายครั้งเดียว", env.urls.count(P59.SNAP1) == 1, env.urls)
        shot(page, f"rr1-stable-{sfx}.png", "#satV3Panel")
        check(f"{tag} 1 {label} ไม่มี console error · ไม่ล้นแนวนอน", not P59.real_errs(ce) and not pe and overflow(page) <= 1, [ce, pe])
    finally: b.close()

    # 2 เลือกการ์ด BTC → snapshot ไม่เปลี่ยน → ยังเลือก · แถวแก้เปิด · Trade Plans ไม่ขยับ
    b, page, ce, pe, env = launch(pw, w, h)
    try:
        seed(page)
        page.locator(".ui-tile[data-key=BTCUSD]").first.click(); wait(page, 400)
        ok_open = js(page, "()=>satV3Sel") == "BTCUSD" and cnt(page, "#satV3Sum.hasEd") == 1
        top0 = js(page, PLANS_TOP)
        js(page, WATCH)
        echo_burst(page, 5)
        check(f"{tag} 2 เลือก BTC → แถวแก้ Strategy เปิด", ok_open)
        check(f"{tag} 2 snapshot ไม่เปลี่ยน 5 ครั้ง → ยังเลือก BTC · แถวแก้ยังเปิด", js(page, "()=>satV3Sel") == "BTCUSD" and cnt(page, "#satV3Sum.hasEd") == 1 and cnt(page, ".ui-tile.sel[data-key=BTCUSD], .ui-tile[data-key=BTCUSD].on, .ui-tile[data-key=BTCUSD][aria-pressed=true]") >= 0)
        top1 = js(page, PLANS_TOP)
        check(f"{tag} 2 ตำแหน่ง Trade Plans ไม่ขยับ (±1px)", top0 is not None and top1 is not None and abs(top0 - top1) <= 1, [top0, top1])
        check(f"{tag} 2 DOM ไม่เปลี่ยน (mutation 0) · img เดิม", js(page, "()=>window.__mut") == 0 and js(page, SAME_IMG))
    finally: b.close()

    # 3 พิมพ์ช่องวางลิงก์ค้าง → snapshot เข้า → focus + ค่ายังอยู่ (ทั้งแบบมีตัวกัน และเรียกวาดตรง)
    b, page, ce, pe, env = launch(pw, w, h)
    try:
        seed(page)
        page.locator(".ui-tile[data-key=BTCUSD] [data-vw-sat-add]").click(); wait(page)
        inp = page.locator("[data-vw-sat-in]"); inp.click(); inp.press_sequentially("https://www.tradingview.com/x/ab", delay=15)
        js(page, WATCH)
        echo_burst(page, 4)
        st = js(page, "()=>{ const i=document.querySelector('[data-vw-sat-in]'); return i ? {v:i.value, f:document.activeElement===i} : null; }")
        check(f"{tag} 3 พิมพ์ค้าง + snapshot เข้า → focus + ค่ายังอยู่", st and st["f"] and st["v"] == "https://www.tradingview.com/x/ab", st)
        # วาดใหม่จริง (ข้อมูลเปลี่ยน) ขณะพิมพ์ค้าง — ผ่านเส้นที่ไม่มีตัวกัน
        js(page, "()=>{ document.querySelector('[data-vw-sat-in]').setSelectionRange(5,9); }")
        js(page, "()=>{ const p = document.getElementById('satV3Panel'); p._rrHtml = null; satV3Render(); }")   # บังคับวาดใหม่จริงทั้งแผง
        st2 = js(page, "()=>{ const i=document.querySelector('[data-vw-sat-in]'); return i ? {v:i.value, f:document.activeElement===i, s:[i.selectionStart,i.selectionEnd]} : null; }")
        check(f"{tag} 3 วาดใหม่จริงขณะพิมพ์ค้าง → focus + ค่า + cursor คงเดิม", st2 and st2["f"] and st2["v"] == "https://www.tradingview.com/x/ab" and st2["s"] == [5, 9], st2)
    finally: b.close()

    # 4 ข้อมูลเปลี่ยนจริง (Bias BTC) → วาดใหม่ 1 ครั้ง · img เดิม · ตัวที่เลือกยังอยู่
    b, page, ce, pe, env = launch(pw, w, h)
    try:
        seed(page)
        page.locator(".ui-tile[data-key=BTCUSD]").first.click(); wait(page, 400)
        js(page, WATCH)
        js(page, "()=>satwWrite('BTCUSD', {support:[2999], updated_at:new Date().toISOString()})"); wait(page, 600)
        echo_burst(page, 3)
        check(f"{tag} 4 แนวรับ BTC เปลี่ยน (PF1: Bias ไม่แสดงบน tile แล้ว) → วาดใหม่ 1 ครั้ง (ไม่ใช่ 0 · ไม่ซ้ำ)", js(page, "()=>window.__draw") == 1 and js(page, "()=>window.__mut") > 0, js(page, "()=>[window.__draw, window.__mut]"))
        check(f"{tag} 4 ภาพ XAUUSD ยังเป็น node เดิม", js(page, SAME_IMG))
        check(f"{tag} 4 ตัวที่เลือกยังอยู่ (BTC · แถวแก้เปิด) · เห็นค่าใหม่", js(page, "()=>satV3Sel") == "BTCUSD" and cnt(page, "#satV3Sum.hasEd") == 1 and js(page, "()=>(satwWeek(wpWeekKey(),'BTCUSD')||{}).support[0]") == 2999)
        check(f"{tag} 4 force:true บังคับวาดใหม่ได้ (ข้อมูลเท่าเดิม)", js(page, "()=>{ window.__draw = 0; satV3Render({force:true}); return window.__draw; }") == 1)
        check(f"{tag} 4 force แล้ว ภาพ XAUUSD ยังเป็น node เดิม", js(page, SAME_IMG))
    finally: b.close()

    # 5 ภาพยังโหลดไม่เสร็จ → กล่องมีความสูง · โหลดเสร็จ Trade Plans ไม่ขยับ
    b, page, ce, pe, env = launch(pw, w, h)
    try:
        held = []
        def hold(route): held.append(route)
        import re
        page.route(re.compile(r"s3\.tradingview\.com"), hold)
        seed(page, {"url": P59.TV2, "at": "2026-10-09"})
        wait(page, 500)
        bh = js(page, "()=>{ const e=document.querySelector('.ui-tile[data-key=XAUUSD] .vwSat'); return e ? e.getBoundingClientRect().height : -1; }")
        check(f"{tag} 5 ภาพยังไม่โหลด (ถูกถือไว้) → กล่องภาพมีความสูงแล้ว", len(held) >= 1 and bh >= 40, [len(held), bh])
        top0 = js(page, PLANS_TOP); bh0 = bh
        for r in held: r.fulfill(status=200, content_type="image/png", body=PNG169)
        wait(page, 800)
        top1 = js(page, PLANS_TOP)
        bh1 = js(page, "()=>document.querySelector('.ui-tile[data-key=XAUUSD] .vwSat').getBoundingClientRect().height")
        check(f"{tag} 5 โหลดเสร็จ (ภาพ 16:9) → Trade Plans ไม่ขยับ (±1px) · กล่องภาพสูงเท่าเดิม", top0 is not None and abs(top0 - top1) <= 1 and abs(bh0 - bh1) <= 1, [top0, top1, bh0, bh1])
        js(page, WATCH); js(page, "()=>{ satV3Render({force:true}); }"); wait(page, 200)
        top2 = js(page, PLANS_TOP)
        check(f"{tag} 5 วาดใหม่หลังรู้สัดส่วนภาพแล้ว → ไม่ขยับ · img เดิม", abs(top1 - top2) <= 1 and js(page, SAME_IMG), [top1, top2])
    finally: b.close()

    # 6 ?debug=render → ป้ายนับ · ไม่มีพารามิเตอร์ → ไม่มีป้าย
    b, page, ce, pe, env = launch(pw, w, h)
    try:
        seed(page)
        check(f"{tag} 6 ไม่มีพารามิเตอร์ → ไม่มีป้าย · rrDbg ปิด", cnt(page, "#rrDbgBadge") == 0 and js(page, "()=>rrDbg.on") is False)
    finally: b.close()
    b, c, page, ce, pe, dl, env = P59.launch(pw, w, h, pick=PICK, index=INDEX + "?debug=render")
    try:
        seed(page)
        b1 = js(page, "()=>{ const e=document.getElementById('rrDbgBadge'); return e ? e.innerText : null; }")
        check(f"{tag} 6 ?debug=render → มีป้ายมุมจอ แสดงจำนวนครั้ง + สาเหตุล่าสุด", js(page, "()=>rrDbg.on") is True and b1 and "satV3Render" in b1 and "วาดจริง" in b1, b1)
        n0 = js(page, "()=>rrDbg.calls")
        js(page, "()=>{ satV3Render(); satV3Render(); }"); wait(page, 100)
        n1 = js(page, "()=>rrDbg.calls"); sk = js(page, "()=>rrDbg.skipped")
        check(f"{tag} 6 ป้ายนับขึ้น · ครั้งที่ HTML เหมือนเดิมนับเป็น 'ข้าม' · เก็บสาเหตุได้ 5 รายการ", n1 == n0 + 2 and sk >= 2 and len(js(page, "()=>rrDbg.causes")) >= 5, [n0, n1, sk])
        check(f"{tag} 6 สาเหตุเป็นชื่อตัวเรียก (ไม่ว่าง)", all(js(page, "()=>rrDbg.causes.slice(-5)")), js(page, "()=>rrDbg.causes.slice(-5)"))
        shot(page, f"rr1-debug-badge-{sfx}.png")
        check(f"{tag} 6 {label} ไม่มี console error", not P59.real_errs(ce) and not pe, [ce, pe])
    finally: b.close()


COUNT = """()=>{ const p = document.getElementById('satV3Panel'); window.__draw = 0;
  if(!p.__rcw2){ p.__rcw2 = true; const f = p.replaceChildren.bind(p); p.replaceChildren = function(){ window.__draw++; return f.apply(null, arguments); }; } }"""
PB = P69.PB


def macro_launch(pw, w, h):
    browser, page, ce, pe = P69.launch(pw, w, h, picks=["XAUUSD", "S50"])
    P11.wk(page, "XAUUSD", "Short", "down")
    idea = P51.idea_doc(asset="XAUUSD", bias="Short", entry=2410, sl=2420, tp=2395, zone=(2395, 2380), iid="iAg"); idea["macro_note"] = ""
    P51.fresh(page, idea); P11.seed_pb(page, [PB]); P11.wk(page, "XAUUSD", "Short", "down")
    js(page, "()=>satV3Render()"); page.wait_for_timeout(300)
    return browser, page, ce, pe


def tests_fix(pw, w, h, label):
    tag = f"[{ENGINE}/{label}]"

    # 7 โฟกัส [data-macro-note] + blur listener เรียก satV3Render({force:true}) → ไม่มี error · ข้อมูลล่าสุด · ไม่เกิน 2 รอบ
    b, page, ce, pe = macro_launch(pw, w, h)
    try:
        check(f"{tag} 7 เตรียม: มีช่อง [data-macro-note]", cnt(page, "[data-macro-note]") == 1)
        js(page, COUNT)
        js(page, """()=>{ const i = document.querySelector('[data-macro-note]'); i.focus(); window.__blurs = 0;
          i.addEventListener('blur', ()=>{ window.__blurs++; satV3Render({force:true}); }); sat7dIdea('iAg').macro_note = 'ล่าสุด'; }""")
        js(page, "()=>satV3Render({force:true})"); page.wait_for_timeout(300)
        check(f"{tag} 7 ไม่มี console error / pageerror (replaceChildren)", not ce and not pe, [ce, pe])
        check(f"{tag} 7 หน้าแสดงข้อมูลล่าสุด", js(page, "()=>document.querySelector('[data-macro-note]').value") == "ล่าสุด")
        d = js(page, "()=>window.__draw")
        check(f"{tag} 7 วาดไม่เกิน 2 รอบ (blur ถูกยิงจริง {js(page, '()=>window.__blurs')} ครั้ง)", 1 <= d <= 2, d)
        check(f"{tag} 7 ตัวกันซ้อนปล่อยแล้ว (rrBusy=false · ไม่มีงานค้าง)", js(page, "()=>rrBusy === false && rrPending === null"))
    finally: b.close()

    # 7b จำลองพฤติกรรม Linux headless: เบราว์เซอร์ยิง blur ตอน replaceChildren ถอดช่องที่โฟกัส (Mac ไม่ยิง) → handler เรียกวาดซ้อน
    b, page, ce, pe = macro_launch(pw, w, h)
    try:
        js(page, """()=>{ const p = document.getElementById('satV3Panel'); window.__draw = 0; window.__fired = 0;
          const f = p.replaceChildren.bind(p);
          p.replaceChildren = function(){ window.__draw++; const a = document.activeElement;
            if(a && p.contains(a) && !window.__fired){ window.__fired = 1; a.dispatchEvent(new FocusEvent('blur')); }
            return f.apply(null, arguments); };
          const i = document.querySelector('[data-macro-note]'); i.focus(); i.addEventListener('blur', ()=>satV3Render({force:true}));
          sat7dIdea('iAg').macro_note = 'ล่าสุด7b'; }""")
        js(page, "()=>satV3Render({force:true})"); page.wait_for_timeout(300)
        check(f"{tag} 7b blur ยิงระหว่างถอดช่อง + handler วาดซ้อน → ไม่มี error · ข้อมูลล่าสุด · ≤ 2 รอบ", not ce and not pe and js(page, "()=>document.querySelector('[data-macro-note]').value") == "ล่าสุด7b" and js(page, "()=>window.__draw") <= 2, [ce, pe, js(page, "()=>window.__draw")])
    finally: b.close()

    # 8 ลำดับเดียวกับ p69 เคส 6: กรอกเหตุผล → change → ไม่มี error · ค่าบันทึกครบ
    b, page, ce, pe = macro_launch(pw, w, h)
    try:
        inp = page.locator("[data-macro-note]").first
        inp.fill("x" * 100); inp.dispatch_event("change"); page.wait_for_timeout(350)
        ln = len(js(page, "()=>sat7dIdea('iAg').macro_note") or "")
        inp = page.locator("[data-macro-note]").first
        inp.fill("เข้าสวนเพราะแนวรับแข็ง"); inp.dispatch_event("change"); page.wait_for_timeout(350)
        check(f"{tag} 8 กรอกเหตุผล 2 รอบ (ตัดที่ 80 ตัว) → บันทึกครบ", ln == 80 and js(page, "()=>sat7dIdea('iAg').macro_note") == "เข้าสวนเพราะแนวรับแข็ง", ln)
        check(f"{tag} 8 ไม่มี console error / pageerror", not ce and not pe, [ce, pe])
        # ช่องที่โฟกัสอยู่แล้วกดออกจากช่อง (blur จริง) ระหว่างมีข้อมูลเปลี่ยน
        page.locator("[data-macro-note]").first.focus(); page.locator("[data-macro-note]").first.fill("ข้อความใหม่")
        page.mouse.click(5, 5); page.wait_for_timeout(350)
        check(f"{tag} 8 blur จริงหลังพิมพ์ → ไม่มี error · ค่าบันทึก", not ce and not pe and js(page, "()=>sat7dIdea('iAg').macro_note") == "ข้อความใหม่", [ce, pe])
    finally: b.close()

    # 9 render ซ้อน 3 ชั้น (เรียกจากใน handler) → จบภายใน 2 รอบ · ไม่ค้าง
    b, page, ce, pe = macro_launch(pw, w, h)
    try:
        js(page, COUNT)
        js(page, """()=>{ const i = document.querySelector('[data-macro-note]'); i.focus();
          i.addEventListener('blur', ()=>{ satV3Render({force:true}); satV3Render({force:true}); satV3Render({force:true}); });
          const f = rrSatDraw; let depth = 0; window.__calls = 0;
          rrSatDraw = function(o){ window.__calls++; if(depth++ < 1) satV3Render({force:true}); try{ return f(o); } finally { depth--; } }; }""")
        js(page, "()=>satV3Render({force:true})"); page.wait_for_timeout(300)
        d = js(page, "()=>window.__draw"); cl = js(page, "()=>window.__calls")
        check(f"{tag} 9 เรียกซ้อน 3 ชั้น → วาดเต็มไม่เกิน 2 รอบ ({d} ครั้ง · rrSatDraw {cl})", 1 <= d <= 2 and cl <= 2, [d, cl])
        check(f"{tag} 9 จบแล้วไม่ค้าง: rrBusy=false · เรียกใหม่วาดได้", js(page, "()=>rrBusy === false && rrPending === null") and js(page, "()=>{ window.__draw = 0; satV3Render({force:true}); return window.__draw; }") >= 1)
        check(f"{tag} 9 ไม่มี error", not ce and not pe, [ce, pe])
    finally: b.close()


def static_checks():
    src = open(INDEX, encoding="utf-8").read()
    check("S1 โค้ด: ตรวจ query ?debug=render และ localStorage.dbgRender (ใน try/catch)", "debug=render" in src and "dbgRender" in src)
    check("S2 โค้ด: satV3Render รับ {force:true}", "function satV3Render(opts)" in src and "opts && opts.force" in src)
    check("S4 RR1fix: มีตัวกันซ้อน rrBusy/rrPending + blur() ก่อน replaceChildren", "let rrBusy" in src and "ae.blur()" in src and os.path.exists(os.path.join(HERE, "..", "index.backup-pre-RR1fix.html")) and os.path.isdir(os.path.join(HERE, "_bk_rr1fix")))
    check("S3 สำรอง index.backup-pre-RR1.html + tests/_bk_rr1/ มีอยู่", os.path.exists(os.path.join(HERE, "..", "index.backup-pre-RR1.html")) and os.path.isdir(os.path.join(HERE, "_bk_rr1")))


def main():
    static_checks()
    with sync_playwright() as pw:
        for w, h, label in ((1440, 900, "1440px"), (390, 844, "390px")):
            print(f"\n=== {ENGINE} {label} ===")
            tests(pw, w, h, label)
            tests_fix(pw, w, h, label)
    p = sum(1 for r in results if r[1]); f = len(results) - p
    print(f"\nสรุป: PASS {p} / FAIL {f} (รวม {len(results)})")
    raise SystemExit(1 if f else 0)


if __name__ == "__main__": main()
